#!/usr/bin/env python3
"""Compare two files (or URLs) and decide whether they're the same paper.

Used standalone for ad-hoc dedup checks, and as a library by
stage_final_drafts.py to verify candidate PDFs before trusting them as the
canonical version.

Usage:
    compare_papers.py FILE_OR_URL_A FILE_OR_URL_B
    compare_papers.py a.pdf b.pdf --mode abstract
    compare_papers.py paper.pdf paper.md --threshold 0.7 --json

Inputs accepted:
    - Local paths: .pdf / .md / .tex / .txt
    - http(s):// URLs (downloaded with caching)

Pipeline:
    1. Extract plain text via the format-appropriate backend
       (pymupdf4llm for PDF, strip-LaTeX for TeX, read-as-is for MD/TXT).
    2. Locate the abstract (regex between Abstract and the next section
       header). Fall back to the first 1500 chars after the title.
    3. Tokenize + drop stopwords.
    4. Score:  combined = 0.55 * abstract_ratio + 0.45 * body_jaccard
       - abstract_ratio: difflib.SequenceMatcher.ratio() over abstract text
       - body_jaccard:  |A_tok n B_tok| / |A_tok u B_tok|
    5. Verdict: same (>=0.75), likely_same (0.55-0.75), different (<0.55).

Exit codes: 0 = same / likely_same, 1 = different, 2 = hard error.
"""

import argparse
import contextlib
import hashlib
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request
from difflib import SequenceMatcher
from pathlib import Path

# Single-thread BLAS / OMP so onnxruntime (transitive dep of pymupdf_layout)
# doesn't try to pin affinity onto cores outside the cgroup.
os.environ.setdefault("ORT_LOGGING_LEVEL", "4")
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")


@contextlib.contextmanager
def _silence_fd_stderr():
    """Redirect FD 2 to /dev/null. onnxruntime writes from C-land before
    Python's sys.stderr layer ever sees the message — plain redirect_stderr()
    is not enough."""
    devnull_fd = os.open(os.devnull, os.O_WRONLY)
    saved = os.dup(2)
    try:
        os.dup2(devnull_fd, 2)
        yield
    finally:
        os.dup2(saved, 2)
        os.close(devnull_fd)
        os.close(saved)

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))
from search_online import _STOPWORDS, USER_AGENT  # noqa: E402

CACHE_DIR = Path.home() / ".cache" / "cml-paper-acquisition" / "compare_downloads"
DEFAULT_CACHE_TTL = 30 * 24 * 3600  # 30 days

# Verdict cutoffs (combined score). default --threshold == "likely_same" floor.
VERDICT_SAME = 0.75
VERDICT_LIKELY = 0.55

_ABSTRACT_BLOCK_RE = re.compile(
    # Match "Abstract" header (case-insensitive, optional numbering / colon /
    # newlines around it), then capture until the next section marker. Allow
    # anything up to: Introduction, Keywords, "1." / "1 " section header, or
    # "## ..." in markdown.
    r"(?:^|\n)\s*(?:#+\s*)?\b[Aa]bstract\b\s*[:.\-]?\s*\n+"
    r"(?P<body>.+?)"
    r"(?=\n\s*(?:#+\s*)?(?:[Ii]ntroduction|[Kk]eywords|"
    r"\d+\.?\s+[A-Z]|[Bb]ackground|[Mm]ethods?|"
    r"[Ii]ndex\s+[Tt]erms)\b)",
    re.DOTALL,
)

_REFS_CUT_RE = re.compile(
    r"\n\s*(?:#+\s*)?(?:References|REFERENCES|Bibliography)\b.*$",
    re.DOTALL,
)


def _cache_path(url: str) -> Path:
    h = hashlib.sha1(url.encode("utf-8")).hexdigest()
    suffix = ".pdf" if url.lower().endswith(".pdf") else ".bin"
    return CACHE_DIR / (h + suffix)


def _download(url: str, cache_ttl: int = DEFAULT_CACHE_TTL) -> Path:
    """Download URL to disk cache; return local path. Cached by sha1(url)."""
    target = _cache_path(url)
    if target.exists() and (time.time() - target.stat().st_mtime) < cache_ttl:
        return target
    target.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=60) as resp:
        if resp.status != 200:
            raise RuntimeError(f"HTTP {resp.status} on {url}")
        tmp = target.with_suffix(target.suffix + ".tmp")
        with tmp.open("wb") as f:
            while True:
                chunk = resp.read(65536)
                if not chunk:
                    break
                f.write(chunk)
        tmp.replace(target)
    return target


def _resolve_input(path_or_url: str) -> Path:
    """Return a local Path for either a filesystem path or a URL."""
    if path_or_url.startswith(("http://", "https://")):
        return _download(path_or_url)
    p = Path(path_or_url).expanduser().resolve()
    if not p.exists():
        raise FileNotFoundError(p)
    return p


def _strip_latex(s: str) -> str:
    """Best-effort LaTeX → plain text. Keeps body text and sections."""
    s = re.sub(r"(?<!\\)%.*", "", s)               # comments
    s = re.sub(r"\\(?:title|author)\s*\{[^{}]*\}", " ", s)
    s = re.sub(r"\\begin\{[^}]+\}", " ", s)
    s = re.sub(r"\\end\{[^}]+\}", " ", s)
    s = re.sub(r"\$[^$]*\$", " ", s)               # inline math
    s = re.sub(r"\\[a-zA-Z]+\s*\{([^{}]*)\}", r"\1", s)
    s = re.sub(r"\\[a-zA-Z]+\*?", " ", s)          # lone macros
    s = s.replace("{", "").replace("}", "")
    s = re.sub(r"\s+", " ", s)
    return s.strip()


def extract_body_text(path_or_url: str) -> str:
    """Return plain text for a local file or URL.

    Routes:
      *.pdf            -> pymupdf4llm.to_markdown -> strip refs
      *.tex            -> _strip_latex
      *.md / *.txt     -> read as-is
      other            -> read as-is
    """
    p = _resolve_input(path_or_url)
    suf = p.suffix.lower()
    if suf == ".pdf":
        # Lazy import — pymupdf4llm is heavy and the rest of this module
        # works without it for non-PDF inputs. Silence FD-level stderr so
        # onnxruntime warnings don't leak into JSON/text output.
        with _silence_fd_stderr():
            import pymupdf4llm
            text = pymupdf4llm.to_markdown(str(p))
    elif suf == ".tex":
        text = _strip_latex(p.read_text(encoding="utf-8", errors="replace"))
    else:
        text = p.read_text(encoding="utf-8", errors="replace")
    # Drop everything from "References" onward — bibs inflate the Jaccard.
    text = _REFS_CUT_RE.sub("", text)
    return text


def extract_abstract(text: str) -> str | None:
    """Return the abstract text from a body string, or None."""
    if not text:
        return None
    m = _ABSTRACT_BLOCK_RE.search(text)
    if m:
        body = m.group("body").strip()
        # Cap to reasonable abstract length so noisy preprints don't pollute.
        return body[:3500].strip()
    # Fallback: first 1500 chars after the first non-trivial heading.
    head = text[:300]
    rest = text[len(head):]
    return (rest[:1500] or text[:1500]).strip() or None


def _tokens(s: str) -> set[str]:
    s = re.sub(r"[^a-z0-9\s]", " ", s.lower())
    return {w for w in s.split() if w not in _STOPWORDS and len(w) > 2}


def _abstract_score(a: str | None, b: str | None) -> float:
    if not a or not b:
        return 0.0
    # Normalize whitespace for SequenceMatcher; it's character-level so
    # tabs/extra spaces inflate noise.
    return SequenceMatcher(
        None,
        re.sub(r"\s+", " ", a).strip(),
        re.sub(r"\s+", " ", b).strip(),
    ).ratio()


def _body_score(a: str, b: str) -> float:
    ta, tb = _tokens(a), _tokens(b)
    if not ta or not tb:
        return 0.0
    return len(ta & tb) / len(ta | tb)


def _verdict(score: float) -> str:
    if score >= VERDICT_SAME:
        return "same"
    if score >= VERDICT_LIKELY:
        return "likely_same"
    return "different"


def compare(file_a: str, file_b: str, mode: str = "both") -> dict:
    """Return a dict with abstract_score, body_score, combined, verdict."""
    body_a = extract_body_text(file_a)
    body_b = extract_body_text(file_b)
    abs_a = extract_abstract(body_a) if mode in ("abstract", "both") else None
    abs_b = extract_abstract(body_b) if mode in ("abstract", "both") else None

    abstract_score = _abstract_score(abs_a, abs_b) if mode != "body" else 0.0
    body_jaccard = _body_score(body_a, body_b) if mode != "abstract" else 0.0

    if mode == "abstract":
        combined = abstract_score
    elif mode == "body":
        combined = body_jaccard
    else:
        combined = 0.55 * abstract_score + 0.45 * body_jaccard

    return {
        "file_a": str(file_a),
        "file_b": str(file_b),
        "mode": mode,
        "abstract_score": round(abstract_score, 4),
        "body_score": round(body_jaccard, 4),
        "combined": round(combined, 4),
        "verdict": _verdict(combined),
        "abstract_a_len": len(abs_a) if abs_a else 0,
        "abstract_b_len": len(abs_b) if abs_b else 0,
        "body_a_tokens": len(_tokens(body_a)),
        "body_b_tokens": len(_tokens(body_b)),
    }


def is_same_paper(file_a: str, file_b: str,
                  threshold: float = 0.6, mode: str = "both") -> bool:
    """Convenience predicate. Returns True iff combined >= threshold."""
    return compare(file_a, file_b, mode=mode)["combined"] >= threshold


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("file_a")
    ap.add_argument("file_b")
    ap.add_argument("--mode", choices=("body", "abstract", "both"),
                    default="both")
    ap.add_argument("--threshold", type=float, default=0.6,
                    help="Cutoff for the predicate / exit code "
                         "(default 0.6 ≈ likely_same)")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    try:
        result = compare(args.file_a, args.file_b, mode=args.mode)
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 2

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"a:        {result['file_a']}")
        print(f"b:        {result['file_b']}")
        print(f"mode:     {result['mode']}")
        print(f"abstract: {result['abstract_score']:.4f} "
              f"(lens {result['abstract_a_len']} / {result['abstract_b_len']})")
        print(f"body:     {result['body_score']:.4f} "
              f"(toks {result['body_a_tokens']} / {result['body_b_tokens']})")
        print(f"combined: {result['combined']:.4f}")
        print(f"verdict:  {result['verdict']}")

    return 0 if result["combined"] >= args.threshold else 1


if __name__ == "__main__":
    sys.exit(main())
