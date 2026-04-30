#!/usr/bin/env python3
"""Build a CSV + PDF inventory of every paper in a CML papers directory.

Usage:
    python generate_report.py                              # defaults
    python generate_report.py --papers-dir /path/to/papers --out /path/to/report
    python generate_report.py --skip-online                # skip DOI lookup
    python generate_report.py --limit 5                    # only first 5 papers

For each paper directory, extracts:
  - Repo name (directory basename; GitHub slug is paper-<basename>)
  - Paper name (from \\title{} in selected .tex, else CLAUDE.md heading)
  - Authors (from \\author{} in .tex, else "**Authors:**" line in CLAUDE.md)
  - Final-draft relative path (CLAUDE.md Main document, else the .tex whose
    last git commit is most recent, excluding supplement/response/cover/
    rebuttal/referee filenames)
  - Draft date (last git-commit timestamp for the chosen file; fs mtime
    fallback — mtime alone is useless after the rhino → GitHub migration
    normalized every file's mtime to the checkout date)
  - Publication URL (via search_online.py --> CrossRef/arXiv, cached)
  - Experimental / conversion / analysis code locations (subdir patterns +
    CLAUDE.md analysis_scripts field)
  - Data locations (subdir patterns + CLAUDE.md data_files field)

Writes:
  <out>/paper_report.csv         (all columns, one row per paper)
  <out>/paper_report.pdf         (summary table, if pdflatex succeeds)
  <out>/paper_report.tex         (source for the PDF)
  <out>/paper_report.log.json    (per-paper warnings)
"""

import argparse
import csv
import json
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))
from parse_claude_md import parse_claude_md  # noqa: E402
import search_online  # noqa: E402
import scrape_wiki  # noqa: E402


DEFAULT_PAPERS_DIR = Path("/home1/zrentala/github_migration/work/papers")
DEFAULT_OUT = Path("/home1/zrentala/github_migration/work/papers/_report")
DEFAULT_OVERLEAF_JSON = Path("/home1/zrentala/FigureLibraryBuild/folder_candidates.json")
DEFAULT_CV_MD = Path("/home1/zrentala/FigureLibraryBuild/cv_papers.md")
CV_SCAN_DIR = Path("/home1/zrentala/FigureLibraryBuild")
GITHUB_REPO_PREFIX = "https://github.com/computational-memory-lab/paper-"

# Subdirectory-name patterns for each code/data category.
EXP_PATTERNS = [
    r"^experiments?$", r"^exp$", r"^task$", r"^pyepl.*$",
    r"^eeg_task.*$", r"^stim.*$", r".*_task$",
]
CONV_PATTERNS = [
    r"^conversion$", r"^convert$", r"^preproc.*$",
    r"^import$", r"^bids.*$", r"^conversion_code$",
]
ANALYSIS_PATTERNS = [
    r"^analysis$", r"^analyses$", r"^scripts$", r"^code$",
    r"^notebooks$", r"^core_model$", r"^sim[0-9_].*$",
]
DATA_PATTERNS = [
    r"^data$", r"^behavioral$", r"^behav.*$", r"^params$",
]

# Filenames to exclude from "final draft" candidates.
DRAFT_EXCLUDE = re.compile(
    r"(supplement|response|cover.?letter|rebuttal|referee|reviewer|reply|sup_?mat)",
    re.IGNORECASE,
)


# Filename-keyword priority for draft selection. Lower = higher priority.
# Ties within the same tier fall back to git-commit time (newest first).
DRAFT_PRIORITY_KEYWORDS = [
    ("accepted", 0),
    ("resubmit", 1),   # matches 'resubmitted', 'resubmitted_r1', etc.
    ("final", 2),
    # 'main' is a weaker signal — only triggers if the stem is exactly 'main'
]


def draft_priority_rank(path: Path) -> int:
    """Return a priority rank for a draft file. Lower = preferred."""
    low = path.name.lower()
    for kw, rank in DRAFT_PRIORITY_KEYWORDS:
        if kw in low:
            return rank
    stem = path.stem.lower()
    if stem == "main":
        return 3
    return 4


def match_any(name: str, patterns: list[str]) -> bool:
    low = name.lower()
    return any(re.fullmatch(p, low) for p in patterns)


def git_last_commit_time(repo: Path, rel_path: str) -> float | None:
    """Return the UNIX time of the last git commit that modified rel_path.

    Falls back to None if:
      - the repo is not a git working tree
      - the file has no recorded history (untracked, staged-only, etc.)
      - git isn't available

    The migration process reset every file's filesystem mtime when repos were
    rehydrated, so fs mtime is useless for judging draft age; git history is
    the authoritative signal.
    """
    try:
        result = subprocess.run(
            ["git", "-C", str(repo), "log", "-1", "--format=%ct",
             "--follow", "--", rel_path],
            capture_output=True, text=True, timeout=10,
        )
    except (subprocess.SubprocessError, OSError):
        return None
    if result.returncode != 0:
        return None
    out = result.stdout.strip()
    if not out:
        return None
    try:
        return float(out.splitlines()[0])
    except (ValueError, IndexError):
        return None


def _sort_key_for_draft(repo: Path, path: Path) -> float:
    """Primary sort key: git last-commit time; fallback: fs mtime."""
    rel = str(path.relative_to(repo))
    t = git_last_commit_time(repo, rel)
    if t is not None:
        return t
    try:
        return path.stat().st_mtime
    except OSError:
        return 0.0


def find_subdirs(repo_path: Path, patterns: list[str]) -> list[str]:
    """Return repo-relative paths of direct subdirectories matching any pattern."""
    out = []
    for child in sorted(repo_path.iterdir()):
        if child.is_dir() and not child.name.startswith(".") and match_any(child.name, patterns):
            out.append(child.name + "/")
    return out


def pick_final_draft(repo_path: Path, claude_main_doc: str | None) -> tuple[str | None, float | None, str]:
    """Return (relative_path, timestamp, reason) for the chosen draft.

    Timestamp is the UNIX time of the last git commit that touched the chosen
    file, or (if git has no record) the filesystem mtime as a last resort.
    Returns (None, None, reason) when no candidate exists.
    """
    if claude_main_doc:
        candidate = repo_path / claude_main_doc
        if candidate.exists():
            t = git_last_commit_time(repo_path, claude_main_doc)
            if t is None:
                t = candidate.stat().st_mtime
            return claude_main_doc, t, "from CLAUDE.md Main document"
        # CLAUDE.md pointed to a file that doesn't exist; fall through.

    tex_files = [
        p for p in repo_path.rglob("*.tex")
        if p.is_file() and not DRAFT_EXCLUDE.search(p.name)
        and ".git" not in p.parts
    ]
    if tex_files:
        # Rank first by filename-keyword priority ('accepted' > 'resubmit' >
        # 'final' > 'main' > other), then by git-commit time as tiebreaker.
        scored = [(draft_priority_rank(p), _sort_key_for_draft(repo_path, p), p)
                  for p in tex_files]
        scored.sort(key=lambda t: (t[0], -t[1]))
        rank, ts, chosen = scored[0]
        why = ("keyword-priority " + chosen.name if rank < 4
               else "most-recent .tex by git commit")
        return str(chosen.relative_to(repo_path)), ts, why

    pdf_files = [
        p for p in repo_path.rglob("*.pdf")
        if p.is_file() and not DRAFT_EXCLUDE.search(p.name)
        and ".git" not in p.parts
    ]
    if pdf_files:
        scored = [(draft_priority_rank(p), _sort_key_for_draft(repo_path, p), p)
                  for p in pdf_files]
        scored.sort(key=lambda t: (t[0], -t[1]))
        rank, ts, chosen = scored[0]
        why = ("keyword-priority " + chosen.name if rank < 4
               else "most-recent .pdf (no .tex found)")
        return str(chosen.relative_to(repo_path)), ts, why

    return None, None, "no .tex or .pdf found"


_TITLE_RE = re.compile(r"\\title\s*(?:\[[^\]]*\])?\s*\{", re.DOTALL)
_AUTHOR_RE = re.compile(r"\\author\s*(?:\[[^\]]*\])?\s*\{", re.DOTALL)


def _extract_braced(text: str, start_match: re.Match) -> str | None:
    """Return the balanced-brace body after a matched \\cmd{ opener."""
    i = start_match.end()
    depth = 1
    buf = []
    while i < len(text) and depth > 0:
        ch = text[i]
        if ch == "{":
            depth += 1
            buf.append(ch)
        elif ch == "}":
            depth -= 1
            if depth == 0:
                break
            buf.append(ch)
        else:
            buf.append(ch)
        i += 1
    if depth != 0:
        return None
    return "".join(buf)


_AFFIL_CUT_RE = re.compile(
    r"(?i)(?:"
    r"\$\^|"                                 # LaTeX superscript markers
    r"\\affil|\\address|\\email|\\thanks|"
    r"department\s+of\b|"
    r"university\s+of\b|"
    r"\buniversity\b|"
    r"\bcollege\b|"
    r"\binstitute\b|"
    r"\bcorrespondence\b|"
    r"\bemail:|\bcontact:|"
    r"\bdepartment\b|"
    r"@[a-z]"                                # email-looking address
    r")"
)


def _clean_latex(s: str, trim_affiliations: bool = False) -> str:
    """Strip common LaTeX markup for plain-text display.

    When `trim_affiliations` is true, cut the string at the first affiliation-
    like token — useful for author fields where authors are followed by
    university / email lines.
    """
    if not s:
        return s
    # Comments
    s = re.sub(r"(?<!\\)%.*", "", s)
    # \\ line breaks and \and separators become commas
    s = re.sub(r"\\\\", ",", s)
    s = re.sub(r"\\and\b", ",", s)
    # Drop whole braced groups for known metadata commands
    for cmd in ("thanks", "footnote", "affil", "email", "institute",
                "address", "orcid", "corref"):
        s = re.sub(rf"\\{cmd}\s*\{{[^{{}}]*\}}", "", s)
    # Strip \command{arg} keeping arg (single-level)
    s = re.sub(r"\\[a-zA-Z]+\s*\{([^{}]*)\}", r"\1", s)
    # Lone backslash commands (\LaTeX, \&, \., \ , etc.)
    s = re.sub(r"\\([^a-zA-Z])", r"\1", s)
    s = re.sub(r"\\[a-zA-Z]+\s*", " ", s)
    # Strip superscript / math markers and lingering braces
    s = re.sub(r"\$[^$]*\$", "", s)
    s = s.replace("{", "").replace("}", "")
    s = re.sub(r"\s+", " ", s).strip()

    if trim_affiliations:
        m = _AFFIL_CUT_RE.search(s)
        if m:
            s = s[: m.start()].rstrip(" ,;:")
        # Drop trailing numeric/punct superscript remnants on each name
        s = re.sub(r",\s*,", ",", s)
        s = s.strip(" ,;*")

    s = s.strip(" ,;*")
    return s


def extract_title_authors_from_tex(tex_path: Path) -> tuple[str | None, str | None]:
    try:
        text = tex_path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None, None

    title = None
    m = _TITLE_RE.search(text)
    if m:
        body = _extract_braced(text, m)
        if body is not None:
            title = _clean_latex(body)

    authors = None
    m = _AUTHOR_RE.search(text)
    if m:
        body = _extract_braced(text, m)
        if body is not None:
            authors = _clean_latex(body, trim_affiliations=True)

    return (title or None), (authors or None)


_CLAUDE_AUTHOR_RE = re.compile(r"\*\*Authors?:\*\*\s*(.+)", re.IGNORECASE)


def _parse_author_prefixes(repo_name: str) -> tuple[list[str], int | None]:
    """Parse repo names like 'BroiHealKaha16' into surname prefixes + year.

    Examples:
      'BroiHealKaha16' -> (['broi', 'heal', 'kaha'], 2016)
      'CohenKahana2019' -> (['cohen', 'kahana'], 2019)
      'AGGA16memvar'    -> (['agga'], 2016)
      'AkaKaha17'       -> (['aka', 'kaha'], 2017)
    """
    year = None
    m = re.search(r"(\d{2,4})", repo_name)
    if m:
        y = int(m.group(1))
        if len(m.group(1)) == 2:
            year = 2000 + y if y < 50 else 1900 + y
        else:
            year = y
        repo_clean = repo_name[: m.start()]
    else:
        repo_clean = repo_name
    repo_clean = repo_clean.split("_")[0]
    chunks = re.findall(r"[A-Z][a-z]+|[A-Z]{2,}", repo_clean)
    return [c.lower() for c in chunks], year


def _norm_title_tokens(s: str) -> set[str]:
    if not s:
        return set()
    s = re.sub(r"[^a-z0-9\s]", " ", s.lower())
    return {w for w in s.split() if len(w) > 2}


def load_cv_md(path: Path) -> list[dict]:
    """Parse the lab CV (flat \\item list) into structured entries.

    Reuses scan_cv.py's extract_* helpers. Returns a list of dicts with
    keys: key, year, title, first_author, last_author, all_authors, raw.
    """
    if not path.exists():
        return []
    if str(CV_SCAN_DIR) not in sys.path:
        sys.path.insert(0, str(CV_SCAN_DIR))
    from scan_cv import extract_year, extract_authors, extract_title, make_key

    text = path.read_text(encoding="utf-8", errors="replace")
    # Drop comment-only lines before splitting on \item
    clean_text = "\n".join(
        ln for ln in text.splitlines() if not ln.lstrip().startswith("%")
    )
    parts = re.split(r"\\item\s+", clean_text)
    out = []
    for part in parts[1:]:
        content = " ".join(
            ln for ln in part.split("\n") if not ln.lstrip().startswith("%")
        ).strip()
        if not content:
            continue
        year = extract_year(content)
        try:
            authors, first, last = extract_authors(content, year)
        except Exception:
            continue
        title = extract_title(content, year)
        if not authors or not title:
            continue
        status = "working" if year is None else "published"
        key = make_key(authors, year, status)
        out.append({
            "key": key,
            "year": year,
            "status": status,
            "title": title,
            "first_author": first,
            "last_author": last,
            "all_authors": [a["surname"] for a in authors],
            "author_count": len(authors),
        })
    return out


def match_local_repo_to_cv(cv: dict, paper_dirs: list[Path]) -> tuple[Path | None, float]:
    """Find the local repo (directory) that best matches a CV entry.

    Score = author-prefix overlap + year proximity + folder-name token overlap.
    Requires first-author match (lead signal) plus at least one secondary signal.
    """
    first = (cv.get("first_author") or "").lower()
    last = (cv.get("last_author") or "").lower()
    cv_year = cv.get("year")
    cv_tokens = _norm_title_tokens(cv.get("title", ""))

    best = None
    best_score = 0.0
    for repo in paper_dirs:
        prefixes, repo_year = _parse_author_prefixes(repo.name)
        if not prefixes:
            continue

        # First author must match — without it the pairing is speculative.
        first_hit = bool(first) and any(
            first.startswith(p) or p.startswith(first[:4]) for p in prefixes
        )
        if not first_hit:
            continue

        # Hard cutoff: same-author papers more than 5 years apart are almost
        # always different works (different submissions/projects that happen to
        # share authors), so don't match them.
        if cv_year and repo_year and abs(cv_year - repo_year) > 5:
            continue

        score = 1.0
        if last and any(last.startswith(p) or p.startswith(last[:4]) for p in prefixes):
            score += 0.7
        # Continuous year proximity so closer years always beat farther ones.
        # diff=0 → +1.0, diff=3 → +0.5, diff=5 → +0.17, diff>5 skipped above.
        if cv_year and repo_year:
            diff = abs(cv_year - repo_year)
            score += max(0.0, (6 - diff) / 6)

        # Folder-name token overlap against CV title (helps disambiguate between
        # multiple same-author papers from the same era — e.g., CoheKaha17_MemMood
        # vs CohenKahana2019).
        repo_tokens = _norm_title_tokens(repo.name)
        if cv_tokens and repo_tokens:
            overlap = len(cv_tokens & repo_tokens) / len(cv_tokens)
            score += overlap * 1.5

        if score > best_score:
            best = repo
            best_score = score

    # Require first-author + at least one secondary signal.
    return (best, best_score) if best_score >= 1.2 else (None, best_score)


def match_overleaf_to_cv(cv: dict, overleaf_index: list[dict]) -> dict | None:
    """Find the Overleaf folder that best matches a CV entry.

    Prefers strong title-token overlap + author agreement between CV and the
    folder's top candidate.
    """
    if not overleaf_index:
        return None

    cv_title_tokens = _norm_title_tokens(cv.get("title", ""))
    cv_surnames = [s.lower() for s in (cv.get("all_authors") or []) if s]
    first = (cv.get("first_author") or "").lower()
    cv_year = cv.get("year")

    best = None
    best_score = 0.0
    for folder_rec in overleaf_index:
        candidates = folder_rec.get("candidates") or []
        if not candidates:
            continue
        cand = candidates[0]
        cand_title_tokens = _norm_title_tokens(cand.get("title", ""))
        cand_authors = [
            a.lower() for a in cand.get("authors", [])
            if a and len(re.sub(r"[^a-zA-Z]", "", a)) >= 3
        ]

        # Title overlap (primary signal).
        title_score = 0.0
        if cv_title_tokens and cand_title_tokens:
            inter = len(cv_title_tokens & cand_title_tokens)
            # F1-ish measure: fraction of CV tokens present
            title_score = inter / max(1, len(cv_title_tokens))

        # Author agreement.
        author_matched = 0
        for surname in cv_surnames:
            if any(
                a.startswith(surname) or surname.startswith(a[:4])
                for a in cand_authors if len(a) >= 4
            ):
                author_matched += 1
        author_score = 0.0
        if cv_surnames and author_matched:
            author_score = min(1.0, author_matched / len(cv_surnames))

        # First-author bonus.
        first_hit = bool(first) and any(
            a.startswith(first) or first.startswith(a[:4])
            for a in cand_authors if len(a) >= 4
        )

        # Folder-name token overlap.
        folder_tokens = _norm_title_tokens(folder_rec["folder_name"])
        folder_score = 0.0
        if cv_title_tokens and folder_tokens:
            folder_score = (
                len(cv_title_tokens & folder_tokens) / max(1, len(cv_title_tokens))
            )

        # Year proximity via candidate mtime (approximation).
        mtime = cand.get("mtime")
        year_score = 0.0
        if mtime and cv_year:
            try:
                cand_year = int(time.strftime("%Y", time.gmtime(float(mtime))))
                diff = abs(cv_year - cand_year)
                if diff <= 1:
                    year_score = 0.3
                elif diff <= 3:
                    year_score = 0.15
            except Exception:
                pass

        score = (0.6 * title_score + 0.3 * author_score
                 + 0.2 * folder_score + year_score
                 + (0.1 if first_hit else 0.0))
        if score > best_score:
            best_score = score
            best = {
                "folder": folder_rec["folder_name"],
                "title": cand.get("title"),
                "authors": cand.get("authors", []),
                "path": cand.get("path"),
                "abs_path": cand.get("abs_path"),
                "mtime": mtime,
                "match_score": round(score, 3),
            }

    if best and best_score >= 0.45:
        return best
    return None


def match_wiki_to_cv(cv: dict, wiki_index: list[dict]) -> dict | None:
    """Find the wiki publication entry that best matches a CV entry.

    Strategy mirrors match_overleaf_to_cv: title-token overlap (primary) +
    surname agreement (secondary) + year proximity. Plus a fast path: many
    wiki keys share the CV key's first-author + year suffix, so try direct
    key-prefix match first.
    """
    if not wiki_index:
        return None

    cv_year = cv.get("year")
    cv_title_tokens = _norm_title_tokens(cv.get("title", ""))
    cv_surnames = [s.lower() for s in (cv.get("all_authors") or []) if s]
    first = (cv.get("first_author") or "").lower()
    cv_key = (cv.get("key") or "").lower()

    best = None
    best_score = 0.0
    for entry in wiki_index:
        # Year hard filter (skip entries >2 years apart from CV).
        wiki_year_int = None
        try:
            wiki_year_int = int(entry.get("year") or 0) or None
        except (ValueError, TypeError):
            wiki_year_int = None  # "Submitted", "In Press"
        if cv_year and wiki_year_int and abs(cv_year - wiki_year_int) > 2:
            continue

        # Title overlap: prefer parsed title; fall back to raw_text tokens
        # (a few "Submitted" entries don't have parseable titles).
        wiki_title = entry.get("title") or ""
        wiki_tokens = _norm_title_tokens(wiki_title)
        if not wiki_tokens:
            wiki_tokens = _norm_title_tokens(entry.get("raw_text") or "")
        title_score = 0.0
        if cv_title_tokens and wiki_tokens:
            title_score = len(cv_title_tokens & wiki_tokens) / max(1, len(cv_title_tokens))

        # Author surname agreement.
        wiki_surnames = [a.lower() for a in (entry.get("authors") or [])]
        author_match = 0
        for s in cv_surnames:
            if any(
                a.startswith(s) or (len(a) >= 4 and s.startswith(a[:4]))
                for a in wiki_surnames if len(a) >= 3
            ):
                author_match += 1
        author_score = (author_match / max(1, len(cv_surnames))) if cv_surnames else 0.0
        first_hit = bool(first) and any(
            a.startswith(first) or (len(a) >= 4 and first.startswith(a[:4]))
            for a in wiki_surnames if len(a) >= 3
        )

        # Direct key-prefix bonus: CV key 'CoheKaha22' vs wiki key 'CohenKahana22'
        # often share the first 4 + year-suffix.
        key_bonus = 0.0
        wiki_key = (entry.get("key") or "").lower()
        if cv_key and wiki_key:
            # Compare alpha prefixes (drop trailing year digits)
            cv_alpha = re.sub(r"\d+", "", cv_key)
            wiki_alpha = re.sub(r"\d+", "", wiki_key)
            if cv_alpha and wiki_alpha and (
                cv_alpha.startswith(wiki_alpha[:6])
                or wiki_alpha.startswith(cv_alpha[:6])
            ):
                # Same authors signal — also check year matches
                cv_y_match = re.search(r"\d+", cv_key)
                wiki_y_match = re.search(r"\d+", wiki_key)
                if (cv_y_match and wiki_y_match
                        and cv_y_match.group() == wiki_y_match.group()):
                    key_bonus = 0.4
                else:
                    key_bonus = 0.15

        # Year proximity bonus (within hard cutoff).
        year_score = 0.0
        if cv_year and wiki_year_int:
            diff = abs(cv_year - wiki_year_int)
            if diff == 0:
                year_score = 0.15
            elif diff == 1:
                year_score = 0.07

        score = (0.55 * title_score + 0.30 * author_score
                 + (0.10 if first_hit else 0.0)
                 + year_score + key_bonus)
        if score > best_score:
            best_score = score
            best = entry

    if best and best_score >= 0.45:
        return {**best, "match_score": round(best_score, 3)}
    return None


def get_github_remote(repo: Path) -> str | None:
    """Return the origin URL for a git repo, or None if unset/not a git tree."""
    try:
        result = subprocess.run(
            ["git", "-C", str(repo), "remote", "get-url", "origin"],
            capture_output=True, text=True, timeout=5,
        )
    except (subprocess.SubprocessError, OSError):
        return None
    if result.returncode != 0:
        return None
    url = result.stdout.strip()
    return url or None


def load_overleaf_index(path: Path) -> list[dict]:
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text())
    except Exception as e:
        print(f"WARN: failed to read {path}: {e}", file=sys.stderr)
        return []
    return data.get("scanned_folders", []) or []


def match_overleaf(repo_name: str, extracted_title: str | None,
                   overleaf_index: list[dict]) -> dict | None:
    """Find the best Overleaf folder candidate for a local repo.

    Combines three signals:
      - Author-prefix match: surname prefixes parsed from the repo name
        (e.g., 'Broi', 'Heal', 'Kaha') matched against Overleaf authors
      - Folder-name containment: repo name appears in folder name or vice versa
      - Title-token overlap: extracted local title vs. Overleaf candidate title

    Returns a dict with {folder, title, authors, path, abs_path, mtime,
    match_score} or None if no folder scores above the threshold.
    """
    if not overleaf_index:
        return None

    prefixes, _year = _parse_author_prefixes(repo_name)
    repo_tokens = _norm_title_tokens(repo_name)
    local_tokens = _norm_title_tokens(extracted_title or "")

    best = None
    best_score = 0.0
    for folder_rec in overleaf_index:
        candidates = folder_rec.get("candidates") or []
        if not candidates:
            continue
        cand = candidates[0]
        # Filter out initial-only "authors" (the Overleaf scan splits "Aka, A"
        # into ["Aka", "A"] — the one-character tokens aren't surnames).
        cand_authors = [
            a.lower() for a in cand.get("authors", [])
            if a and len(re.sub(r"[^a-zA-Z]", "", a)) >= 3
        ]
        cand_title_tokens = _norm_title_tokens(cand.get("title", ""))

        # Author-prefix coverage. A single prefix hit is weak evidence
        # (many authors share a starting letter); two+ hits is strong.
        author_score = 0.0
        if prefixes and cand_authors:
            matched = sum(
                1 for p in prefixes
                if any(
                    a.startswith(p) or (len(a) >= 4 and p.startswith(a[:4]))
                    for a in cand_authors
                )
            )
            if matched >= 2:
                author_score = min(1.0, matched / max(1, len(prefixes)))
            elif matched == 1:
                author_score = 0.3

        # Folder-name containment
        name_score = 0.0
        folder_lower = folder_rec["folder_name"].lower()
        repo_lower = repo_name.lower()
        if repo_lower in folder_lower or folder_lower in repo_lower:
            name_score = 1.0
        else:
            folder_tokens = _norm_title_tokens(folder_rec["folder_name"])
            if repo_tokens and folder_tokens:
                overlap = len(repo_tokens & folder_tokens) / max(1, len(repo_tokens))
                name_score = overlap

        # Title-token overlap (if local title is real, not just the repo name)
        title_score = 0.0
        if local_tokens and cand_title_tokens and local_tokens != repo_tokens:
            overlap = len(local_tokens & cand_title_tokens) / max(1, len(local_tokens))
            title_score = overlap

        score = 0.5 * author_score + 0.3 * name_score + 0.5 * title_score
        if score > best_score:
            best_score = score
            best = {
                "folder": folder_rec["folder_name"],
                "title": cand.get("title"),
                "authors": cand.get("authors", []),
                "path": cand.get("path"),
                "abs_path": cand.get("abs_path"),
                "mtime": cand.get("mtime"),
                "match_score": round(score, 3),
            }

    if best and best_score >= 0.5:
        return best
    return None


def extract_authors_from_claude_md(text: str) -> str | None:
    m = _CLAUDE_AUTHOR_RE.search(text)
    if not m:
        return None
    return _clean_latex(m.group(1).strip(), trim_affiliations=True)


def extract_code_and_data(repo: Path, claude_parsed: dict) -> dict:
    exp = find_subdirs(repo, EXP_PATTERNS)
    conv = find_subdirs(repo, CONV_PATTERNS)
    analysis = find_subdirs(repo, ANALYSIS_PATTERNS)
    data = find_subdirs(repo, DATA_PATTERNS)

    # Merge with CLAUDE.md fields (which list specific files, not directories).
    # Collapse to unique top-level directories to avoid bloating the report.
    for f in claude_parsed.get("analysis_scripts", []):
        top = f.split("/", 1)[0] + "/" if "/" in f else f
        if top and top not in analysis:
            analysis.append(top)
    for f in claude_parsed.get("data_files", []):
        top = f.split("/", 1)[0] + "/" if "/" in f else f
        if top and top not in data:
            data.append(top)

    return {
        "experimental_code": exp,
        "conversion_code": conv,
        "analysis_code": analysis,
        "data_locations": data,
    }


def process_paper(repo: Path, warnings: list[str], online_lookup: bool,
                  overleaf_index: list[dict] | None = None) -> dict:
    row = {
        "repo_name": f"paper-{repo.name}",
        "paper_name": "",
        "authors": "",
        "final_draft_path": "",
        "publication_url": "",
        "experimental_code": "",
        "conversion_code": "",
        "analysis_code": "",
        "data_locations": "",
        "draft_date": "",
    }

    claude_md = repo / "CLAUDE.md"
    claude_parsed = {"main_document": None, "analysis_scripts": [], "data_files": [], "repo_name": None}
    claude_text = ""
    if claude_md.exists():
        try:
            claude_text = claude_md.read_text(encoding="utf-8", errors="replace")
            claude_parsed = parse_claude_md(claude_text)
        except Exception as e:
            warnings.append(f"{repo.name}: CLAUDE.md parse error: {e}")
    else:
        warnings.append(f"{repo.name}: no CLAUDE.md")

    # Final-draft selection.
    draft_rel, draft_date, draft_reason = pick_final_draft(
        repo, claude_parsed.get("main_document")
    )
    if draft_rel:
        row["final_draft_path"] = draft_rel
        row["draft_date"] = time.strftime("%Y-%m-%d", time.gmtime(draft_date)) if draft_date else ""
    else:
        warnings.append(f"{repo.name}: {draft_reason}")

    # Title + authors from the chosen tex, with fallbacks.
    title = authors = None
    if draft_rel and draft_rel.endswith(".tex"):
        title, authors = extract_title_authors_from_tex(repo / draft_rel)

    if not title and claude_parsed.get("repo_name"):
        title = claude_parsed["repo_name"]
    if not authors and claude_text:
        authors = extract_authors_from_claude_md(claude_text)

    # Overleaf enrichment: fill missing title/authors and surface an Overleaf
    # draft when the local repo has no manuscript of its own.
    overleaf_match = None
    if overleaf_index:
        overleaf_match = match_overleaf(repo.name, title, overleaf_index)

    if overleaf_match:
        overleaf_title = overleaf_match.get("title") or None
        # Prefer Overleaf title when local title is missing or is just the repo
        # name fallback (CLAUDE.md heading == repo folder name).
        if overleaf_title and (
            not title
            or title == repo.name
            or title == f"paper-{repo.name}"
        ):
            title = overleaf_title
        if not authors and overleaf_match.get("authors"):
            clean = [
                a for a in overleaf_match["authors"]
                if a and len(re.sub(r"[^a-zA-Z]", "", a)) >= 3
            ]
            authors = ", ".join(clean) if clean else None
        if not draft_rel:
            # Local repo had no .tex or .pdf — surface the Overleaf draft.
            row["final_draft_path"] = (
                f"(overleaf) {overleaf_match['folder']}/{overleaf_match['path']}"
            )
            mtime = overleaf_match.get("mtime")
            if mtime:
                try:
                    row["draft_date"] = time.strftime(
                        "%Y-%m-%d", time.gmtime(float(mtime))
                    )
                except Exception:
                    pass

    row["paper_name"] = title or ""
    row["authors"] = authors or ""
    if not title:
        warnings.append(f"{repo.name}: no title found")
    if not authors:
        warnings.append(f"{repo.name}: no authors found")

    # Code + data locations.
    code_data = extract_code_and_data(repo, claude_parsed)
    row["experimental_code"] = "; ".join(code_data["experimental_code"]) or "N/A"
    row["conversion_code"] = "; ".join(code_data["conversion_code"]) or "N/A"
    row["analysis_code"] = "; ".join(code_data["analysis_code"]) or "N/A"
    row["data_locations"] = "; ".join(code_data["data_locations"]) or "N/A"

    # Online lookup (cached).
    if online_lookup and title and authors:
        try:
            result, cache_hit = search_online.lookup(title, authors)
            if result and result.get("url"):
                row["publication_url"] = result["url"]
            else:
                warnings.append(f"{repo.name}: online lookup found no confident match")
            if not cache_hit:
                # Be polite to the API when the cache is cold.
                time.sleep(0.3)
        except Exception as e:
            warnings.append(f"{repo.name}: online lookup error: {e}")

    return row


CV_FIELDNAMES = [
    # Identification
    "cv_key", "year", "status",
    "paper_title", "authors",
    # Source identifiers
    "repo_name", "overleaf_folder", "wiki_key",
    # Chosen draft
    "final_draft_path", "draft_source", "draft_date",
    # 1-hot per source: title / authors / draft / code / data / url
    "title_in_github", "title_in_overleaf", "title_in_wiki",
    "authors_in_github", "authors_in_overleaf", "authors_in_wiki",
    "draft_in_github", "draft_in_overleaf", "draft_in_wiki",
    "code_in_github", "code_in_wiki",
    "data_in_github", "data_in_wiki",
    "url_in_github", "url_in_wiki",
    # Detail columns
    "publication_url",
    "github_remote_url",
    "experimental_code", "conversion_code",
    "analysis_code", "data_locations",
    "wiki_pdf_url", "wiki_code_url", "wiki_data_url",
    "wiki_supplemental_url", "wiki_poster_url", "wiki_eeg_access_url",
]


def _yn(b: bool) -> str:
    return "Y" if b else ""


def process_cv_paper(cv: dict, paper_dirs: list[Path],
                     overleaf_index: list[dict],
                     wiki_index: list[dict],
                     warnings: list[str],
                     online_lookup: bool) -> dict:
    """Build one report row for a CV paper entry.

    Strategy:
      1. Match the CV entry to a github paper repo (if any) via author-prefix
         + year + title overlap.
      2. Match to an Overleaf folder (if any) via title + author tokens.
      3. Match to a wiki publication entry (if any) via title + authors + key.
      4. Pull draft metadata from github + overleaf, then pick the best draft:
         - Overleaf wins when its file date is newer than the github git-commit
           date (post-migration drafts often live on Overleaf only).
         - Github wins when it's newer, or when Overleaf had no match.
      5. Code/data come from the github repo OR the wiki (.code.tgz / .data.tgz).
         Overleaf isn't a code/data host.
      6. Online URL lookup uses CV's authoritative title + authors.
    """
    row = {k: "" for k in CV_FIELDNAMES}
    row["cv_key"] = cv.get("key") or ""
    row["year"] = str(cv.get("year") or "")
    row["status"] = cv.get("status") or ""
    row["paper_title"] = cv.get("title") or ""
    row["authors"] = ", ".join(cv.get("all_authors") or [])

    # --- Github repo match ----------------------------------------------
    github_repo, _gh_score = match_local_repo_to_cv(cv, paper_dirs)
    github_draft_rel = None
    github_draft_ts = None
    github_title_found = False
    github_authors_found = False
    github_code_found = False
    github_data_found = False
    github_remote_url = None

    if github_repo is not None:
        row["repo_name"] = f"paper-{github_repo.name}"

        claude_parsed = {"main_document": None, "analysis_scripts": [], "data_files": []}
        claude_md = github_repo / "CLAUDE.md"
        if claude_md.exists():
            try:
                claude_parsed = parse_claude_md(
                    claude_md.read_text(encoding="utf-8", errors="replace")
                )
            except Exception:
                pass

        github_draft_rel, github_draft_ts, _why = pick_final_draft(
            github_repo, claude_parsed.get("main_document")
        )
        if github_draft_rel and github_draft_rel.endswith(".tex"):
            t, a = extract_title_authors_from_tex(github_repo / github_draft_rel)
            github_title_found = bool(t)
            github_authors_found = bool(a)

        code_data = extract_code_and_data(github_repo, claude_parsed)
        row["experimental_code"] = "; ".join(code_data["experimental_code"]) or "N/A"
        row["conversion_code"] = "; ".join(code_data["conversion_code"]) or "N/A"
        row["analysis_code"] = "; ".join(code_data["analysis_code"]) or "N/A"
        row["data_locations"] = "; ".join(code_data["data_locations"]) or "N/A"
        github_code_found = any(
            row[f] != "N/A" for f in
            ("experimental_code", "conversion_code", "analysis_code")
        )
        github_data_found = row["data_locations"] != "N/A"

        # Try to read the actual remote URL; fall back to the canonical
        # pattern (paper- prefix + basename) so the column has a value when
        # the repo exists but has no remote configured yet.
        remote = get_github_remote(github_repo)
        github_remote_url = remote or f"{GITHUB_REPO_PREFIX}{github_repo.name}"
        row["github_remote_url"] = github_remote_url
    else:
        warnings.append(f"{cv.get('key')}: no github repo match")
        row["experimental_code"] = "N/A"
        row["conversion_code"] = "N/A"
        row["analysis_code"] = "N/A"
        row["data_locations"] = "N/A"

    # --- Overleaf match -------------------------------------------------
    overleaf_match = match_overleaf_to_cv(cv, overleaf_index)
    overleaf_ts = None
    overleaf_title_found = False
    overleaf_authors_found = False
    if overleaf_match:
        row["overleaf_folder"] = overleaf_match["folder"]
        overleaf_title_found = bool(overleaf_match.get("title"))
        overleaf_authors_found = bool([
            a for a in (overleaf_match.get("authors") or [])
            if a and len(re.sub(r"[^a-zA-Z]", "", a)) >= 3
        ])
        try:
            overleaf_ts = float(overleaf_match["mtime"]) if overleaf_match.get("mtime") else None
        except (TypeError, ValueError):
            overleaf_ts = None

    # --- Wiki match -----------------------------------------------------
    wiki_match = match_wiki_to_cv(cv, wiki_index)
    wiki_title_found = False
    wiki_authors_found = False
    wiki_code_found = False
    wiki_data_found = False
    if wiki_match:
        row["wiki_key"] = wiki_match.get("key") or ""
        wiki_title_found = bool(wiki_match.get("title"))
        wiki_authors_found = bool(wiki_match.get("authors"))
        # Code = .code.tgz OR a Supplemental.* link (per user spec)
        wiki_code_found = bool(
            wiki_match.get("code_url") or wiki_match.get("supplemental_url")
        )
        # Data = .data.tgz OR an Ephys-access request link
        wiki_data_found = bool(
            wiki_match.get("data_url") or wiki_match.get("eeg_access_url")
        )
        row["wiki_pdf_url"] = wiki_match.get("pdf_url") or ""
        row["wiki_code_url"] = wiki_match.get("code_url") or ""
        row["wiki_data_url"] = wiki_match.get("data_url") or ""
        row["wiki_supplemental_url"] = wiki_match.get("supplemental_url") or ""
        row["wiki_poster_url"] = wiki_match.get("poster_url") or ""
        row["wiki_eeg_access_url"] = wiki_match.get("eeg_access_url") or ""

    # --- Pick the best draft across github + overleaf ------------------
    # Prefer whichever source has the newer timestamp; wiki is always a
    # final-draft snapshot, but it's the published PDF — already represented
    # by wiki_pdf_url, so we don't compete with it here.
    if github_draft_rel and overleaf_match:
        if (overleaf_ts or 0) > (github_draft_ts or 0):
            row["final_draft_path"] = (
                f"(overleaf) {overleaf_match['folder']}/{overleaf_match['path']}"
            )
            row["draft_source"] = "overleaf"
            chosen_ts = overleaf_ts
        else:
            row["final_draft_path"] = github_draft_rel
            row["draft_source"] = "github"
            chosen_ts = github_draft_ts
    elif github_draft_rel:
        row["final_draft_path"] = github_draft_rel
        row["draft_source"] = "github"
        chosen_ts = github_draft_ts
    elif overleaf_match:
        row["final_draft_path"] = (
            f"(overleaf) {overleaf_match['folder']}/{overleaf_match['path']}"
        )
        row["draft_source"] = "overleaf"
        chosen_ts = overleaf_ts
    elif wiki_match and wiki_match.get("pdf_url"):
        # No editable source — show the published wiki PDF as the final draft.
        row["final_draft_path"] = f"(wiki) {wiki_match['pdf_url']}"
        row["draft_source"] = "wiki"
        chosen_ts = None
    else:
        chosen_ts = None
        warnings.append(f"{cv.get('key')}: no draft found (github / overleaf / wiki)")

    if chosen_ts:
        try:
            row["draft_date"] = time.strftime("%Y-%m-%d", time.gmtime(float(chosen_ts)))
        except Exception:
            pass

    # --- One-hot source flag columns -----------------------------------
    row["title_in_github"] = _yn(github_title_found)
    row["title_in_overleaf"] = _yn(overleaf_title_found)
    row["title_in_wiki"] = _yn(wiki_title_found)
    row["authors_in_github"] = _yn(github_authors_found)
    row["authors_in_overleaf"] = _yn(overleaf_authors_found)
    row["authors_in_wiki"] = _yn(wiki_authors_found)
    row["draft_in_github"] = _yn(bool(github_draft_rel))
    row["draft_in_overleaf"] = _yn(bool(overleaf_match))
    row["draft_in_wiki"] = _yn(bool(wiki_match and wiki_match.get("pdf_url")))
    row["code_in_github"] = _yn(github_code_found)
    row["code_in_wiki"] = _yn(wiki_code_found)
    row["data_in_github"] = _yn(github_data_found)
    row["data_in_wiki"] = _yn(wiki_data_found)
    row["url_in_github"] = _yn(bool(github_remote_url))
    # Wiki URL: the wiki page anchor for this entry — present whenever a wiki
    # match was found. publication_url (CrossRef DOI) lives in its own column.
    row["url_in_wiki"] = _yn(bool(wiki_match))

    # --- Online URL lookup ---------------------------------------------
    if online_lookup and cv.get("title"):
        try:
            authors_str = ", ".join(cv.get("all_authors") or [])
            result, _cache_hit = search_online.lookup(
                cv["title"], authors_str, cv.get("year")
            )
            if result and result.get("url"):
                row["publication_url"] = result["url"]
            else:
                warnings.append(f"{cv.get('key')}: online lookup miss")
            if not _cache_hit:
                time.sleep(0.3)
        except Exception as e:
            warnings.append(f"{cv.get('key')}: online lookup error: {e}")

    return row


LATEX_ESCAPES = {
    "\\": r"\textbackslash{}",
    "&": r"\&",
    "%": r"\%",
    "$": r"\$",
    "#": r"\#",
    "_": r"\_",
    "{": r"\{",
    "}": r"\}",
    "~": r"\textasciitilde{}",
    "^": r"\textasciicircum{}",
    "<": r"\textless{}",
    ">": r"\textgreater{}",
}


def latex_escape(s: str) -> str:
    if not s:
        return ""
    # Backslash must be replaced first, otherwise the replacements injected by
    # other substitutions (which contain backslashes) get mangled.
    out = []
    for ch in s:
        out.append(LATEX_ESCAPES.get(ch, ch))
    return "".join(out)


def truncate(s: str, n: int) -> str:
    if s is None:
        return ""
    s = s.strip()
    return s if len(s) <= n else s[: n - 1] + "…"


def _trait_list_cell(traits: list[tuple[str, bool]]) -> str:
    """Render a per-source PDF cell as a comma-list of trait names found.

    `traits` is an ordered [(label, present), ...] list. Order encodes the
    user's preference: Code, Data first, then Title, Authors, Final Draft, URL.
    Returns "--" (escaped) when nothing is present.
    """
    found = [latex_escape(label) for label, ok in traits if ok]
    if not found:
        return r"\textcolor{black!40}{--}"
    return ", ".join(found)


def build_latex_cv(rows: list[dict], out_dir: Path, cv_md_path: Path) -> Path:
    """Emit paper_report.tex — Key/Yr/Title/Authors + 3 source columns
    (GitHub, Overleaf, Wiki). Each source cell lists which of {Code, Data,
    Title, Authors, Final Draft, URL} were found for that paper at that
    source.
    """
    lines = [
        r"\documentclass[9pt]{extarticle}",
        r"\usepackage[landscape,margin=0.4in]{geometry}",
        r"\usepackage{longtable}",
        r"\usepackage{array}",
        r"\usepackage[T1]{fontenc}",
        r"\usepackage[utf8]{inputenc}",
        r"\usepackage{hyperref}",
        r"\hypersetup{colorlinks=true,urlcolor=blue}",
        r"\usepackage{xcolor}",
        r"\renewcommand{\arraystretch}{1.15}",
        r"\begin{document}",
        r"\begin{center}",
        r"{\Large\textbf{CML Papers Inventory (CV-driven)}}\\[4pt]",
        f"{len(rows)} papers from \\texttt{{{latex_escape(str(cv_md_path))}}}" + r"\\",
        r"Generated " + time.strftime("%Y-%m-%d") + r"\\",
        r"\vspace{4pt}",
        r"\textit{Each source column lists what we can find: "
        r"\textbf{Code}, \textbf{Data}, \textbf{Title}, \textbf{Authors}, "
        r"\textbf{Final Draft}, \textbf{URL}. "
        r"Full one-hot columns in \texttt{paper\_report.csv}.}",
        r"\end{center}",
        r"\vspace{6pt}",
        r"\scriptsize",
        r"\setlength{\tabcolsep}{4pt}",
        # key | yr | title | authors | github | overleaf | wiki
        r"\begin{longtable}{|p{0.07\textwidth}|c|p{0.18\textwidth}|p{0.13\textwidth}|p{0.16\textwidth}|p{0.14\textwidth}|p{0.16\textwidth}|}",
        r"\hline",
        r"\textbf{Key} & \textbf{Yr} & \textbf{Title} & \textbf{Authors} "
        r"& \textbf{GitHub} & \textbf{Overleaf} & \textbf{Wiki} \\",
        r"\hline",
        r"\endfirsthead",
        r"\hline",
        r"\textbf{Key} & \textbf{Yr} & \textbf{Title} & \textbf{Authors} "
        r"& \textbf{GitHub} & \textbf{Overleaf} & \textbf{Wiki} \\",
        r"\hline",
        r"\endhead",
        r"\hline",
        r"\endfoot",
    ]

    def y(field: str, row: dict) -> bool:
        return row.get(field) == "Y"

    for row in rows:
        # Title cell (links to publication_url if found).
        pub_url = row.get("publication_url") or ""
        title = truncate(row.get("paper_title") or "", 90)
        title_cell = (
            r"\href{" + pub_url.replace("%", r"\%") + r"}{" + latex_escape(title) + r"}"
            if pub_url else latex_escape(title)
        )

        # Per-source trait list. User-specified order: Code, Data first; then
        # Title, Authors, Final Draft, URL.
        github_traits = [
            ("Code", y("code_in_github", row)),
            ("Data", y("data_in_github", row)),
            ("Title", y("title_in_github", row)),
            ("Authors", y("authors_in_github", row)),
            ("Final Draft", y("draft_in_github", row)),
            ("URL", y("url_in_github", row)),
        ]
        overleaf_traits = [
            # Overleaf doesn't host code/data/URL — only show what it actually has.
            ("Title", y("title_in_overleaf", row)),
            ("Authors", y("authors_in_overleaf", row)),
            ("Final Draft", y("draft_in_overleaf", row)),
        ]
        wiki_traits = [
            ("Code", y("code_in_wiki", row)),
            ("Data", y("data_in_wiki", row)),
            ("Title", y("title_in_wiki", row)),
            ("Authors", y("authors_in_wiki", row)),
            ("Final Draft", y("draft_in_wiki", row)),
            ("URL", y("url_in_wiki", row)),
        ]

        lines.append(
            "{key} & {yr} & {title} & {authors} & {gh} & {ov} & {wk} \\\\".format(
                key=latex_escape(truncate(row["cv_key"], 16)),
                yr=latex_escape(row["year"] or row["status"][:4]),
                title=title_cell,
                authors=latex_escape(truncate(row["authors"], 70)),
                gh=_trait_list_cell(github_traits),
                ov=_trait_list_cell(overleaf_traits),
                wk=_trait_list_cell(wiki_traits),
            )
        )
        lines.append(r"\hline")

    lines.append(r"\end{longtable}")
    lines.append(r"\end{document}")
    tex_path = out_dir / "paper_report.tex"
    tex_path.write_text("\n".join(lines), encoding="utf-8")
    return tex_path


def build_latex(rows: list[dict], out_dir: Path, papers_dir: Path) -> Path:
    """Emit paper_report.tex — summary table (landscape longtable)."""
    lines = [
        r"\documentclass[10pt]{article}",
        r"\usepackage[landscape,margin=0.5in]{geometry}",
        r"\usepackage{longtable}",
        r"\usepackage{array}",
        r"\usepackage[T1]{fontenc}",
        r"\usepackage[utf8]{inputenc}",
        r"\usepackage{hyperref}",
        r"\hypersetup{colorlinks=true,urlcolor=blue}",
        r"\usepackage{xcolor}",
        r"\renewcommand{\arraystretch}{1.15}",
        r"\newcommand{\checkmk}{\textcolor{green!55!black}{\textbf{Y}}}",
        r"\newcommand{\crossmk}{\textcolor{red!70!black}{--}}",
        r"\begin{document}",
        r"\begin{center}",
        r"{\Large\textbf{CML Papers Inventory}}\\[4pt]",
        f"{len(rows)} papers scanned from \\texttt{{{latex_escape(str(papers_dir))}}}"
        + r"\\",
        r"Generated " + time.strftime("%Y-%m-%d") + r"\\",
        r"\vspace{4pt}",
        r"\textit{Full columns (exp / conv / analysis code, data locations, URLs) are in "
        r"\texttt{paper\_report.csv} in this directory.}",
        r"\end{center}",
        r"\vspace{6pt}",
        r"\footnotesize",
        r"\setlength{\tabcolsep}{4pt}",
        r"\begin{longtable}{|p{0.18\textwidth}|p{0.27\textwidth}|p{0.16\textwidth}|p{0.17\textwidth}|c|c|c|c|c|}",
        r"\hline",
        r"\textbf{Repo} & \textbf{Paper name} & \textbf{Authors} & \textbf{Draft (rel.)}"
        r" & \textbf{Draft date} & \textbf{Exp} & \textbf{Conv} & \textbf{Anal} & \textbf{Data} \\",
        r"\hline",
        r"\endfirsthead",
        r"\hline",
        r"\textbf{Repo} & \textbf{Paper name} & \textbf{Authors} & \textbf{Draft (rel.)}"
        r" & \textbf{Draft date} & \textbf{Exp} & \textbf{Conv} & \textbf{Anal} & \textbf{Data} \\",
        r"\hline",
        r"\endhead",
        r"\hline",
        r"\endfoot",
    ]

    def flag(v: str) -> str:
        return r"\checkmk" if v and v != "N/A" else r"\crossmk"

    for row in rows:
        url = row.get("publication_url") or ""
        paper_name = truncate(row["paper_name"] or "(no title)", 80)
        if url:
            paper_cell = (
                r"\href{" + url.replace("%", r"\%") + r"}{"
                + latex_escape(paper_name) + r"}"
            )
        else:
            paper_cell = latex_escape(paper_name)

        lines.append(
            "{repo} & {paper} & {authors} & {draft} & {dt} & {e} & {c} & {a} & {d} \\\\".format(
                repo=latex_escape(truncate(row["repo_name"], 45)),
                paper=paper_cell,
                authors=latex_escape(truncate(row["authors"] or "", 55)),
                draft=latex_escape(truncate(row["final_draft_path"] or "--", 55)),
                dt=latex_escape(row.get("draft_date") or "--"),
                e=flag(row["experimental_code"]),
                c=flag(row["conversion_code"]),
                a=flag(row["analysis_code"]),
                d=flag(row["data_locations"]),
            )
        )
        lines.append(r"\hline")

    lines.append(r"\end{longtable}")
    lines.append(r"\end{document}")
    tex_path = out_dir / "paper_report.tex"
    tex_path.write_text("\n".join(lines), encoding="utf-8")
    return tex_path


def compile_pdf(tex_path: Path) -> bool:
    if not shutil.which("pdflatex"):
        print("WARN: pdflatex not found; skipping PDF build", file=sys.stderr)
        return False
    cwd = tex_path.parent
    for run in (1, 2):
        result = subprocess.run(
            ["pdflatex", "-interaction=nonstopmode", "-halt-on-error", tex_path.name],
            cwd=cwd, capture_output=True, text=True, timeout=300,
        )
        if result.returncode != 0:
            print(f"WARN: pdflatex pass {run} failed", file=sys.stderr)
            tail = "\n".join(result.stdout.splitlines()[-30:])
            print(tail, file=sys.stderr)
            return False
    return (cwd / (tex_path.stem + ".pdf")).exists()


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--papers-dir", type=Path, default=DEFAULT_PAPERS_DIR)
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT)
    ap.add_argument("--skip-online", action="store_true",
                    help="Skip DOI lookup (leave publication_url blank)")
    ap.add_argument("--limit", type=int, default=None,
                    help="Process only the first N papers (alphabetical)")
    ap.add_argument("--overleaf-json", type=Path, default=DEFAULT_OVERLEAF_JSON,
                    help="folder_candidates.json from the Overleaf scan (optional)")
    ap.add_argument("--cv-md", type=Path, default=DEFAULT_CV_MD,
                    help="Path to cv_papers.md. When it exists, the report is "
                         "driven by CV entries (one row per CV paper); "
                         "otherwise the report iterates all local paper dirs.")
    ap.add_argument("--skip-wiki", action="store_true",
                    help="Skip wiki scrape (leave all wiki_* columns blank)")
    ap.add_argument("--wiki-cache-ttl", type=int,
                    default=scrape_wiki.DEFAULT_CACHE_TTL,
                    help="Cache TTL (seconds) for the wiki scrape")
    args = ap.parse_args()

    if not args.papers_dir.exists():
        print(f"ERROR: {args.papers_dir} does not exist", file=sys.stderr)
        return 2

    args.out.mkdir(parents=True, exist_ok=True)

    paper_dirs = sorted(
        p for p in args.papers_dir.iterdir()
        if p.is_dir() and not p.name.startswith(".") and not p.name.startswith("_")
    )
    if args.limit:
        paper_dirs = paper_dirs[: args.limit]

    overleaf_index = load_overleaf_index(args.overleaf_json) if args.overleaf_json else []
    if overleaf_index:
        print(
            f"Loaded {len(overleaf_index)} Overleaf folders from {args.overleaf_json}",
            file=sys.stderr,
        )
    elif args.overleaf_json and args.overleaf_json != DEFAULT_OVERLEAF_JSON:
        print(f"WARN: no Overleaf data at {args.overleaf_json}", file=sys.stderr)

    wiki_index: list[dict] = []
    if not args.skip_wiki:
        try:
            wiki_index = scrape_wiki.get_entries(cache_ttl=args.wiki_cache_ttl)
            print(
                f"Loaded {len(wiki_index)} wiki publications from "
                f"{scrape_wiki.WIKI_URL}",
                file=sys.stderr,
            )
        except Exception as e:
            print(f"WARN: wiki scrape failed: {e}", file=sys.stderr)

    # --- CV-driven mode: one row per CV paper --------------------------
    cv_entries = load_cv_md(args.cv_md) if args.cv_md else []
    if cv_entries:
        print(
            f"Loaded {len(cv_entries)} CV entries from {args.cv_md}",
            file=sys.stderr,
        )
        if args.limit:
            cv_entries = cv_entries[: args.limit]

        rows: list[dict] = []
        warnings: list[str] = []
        for i, cv in enumerate(cv_entries, 1):
            if i == 1 or i % 25 == 0 or i == len(cv_entries):
                print(f"  [{i}/{len(cv_entries)}] {cv.get('key')}", file=sys.stderr)
            try:
                row = process_cv_paper(
                    cv, paper_dirs, overleaf_index, wiki_index, warnings,
                    online_lookup=not args.skip_online,
                )
                rows.append(row)
            except Exception as e:
                warnings.append(f"{cv.get('key')}: fatal error: {e}")

        csv_path = args.out / "paper_report.csv"
        with csv_path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=CV_FIELDNAMES)
            writer.writeheader()
            writer.writerows(rows)
        print(f"Wrote {csv_path} ({len(rows)} rows)", file=sys.stderr)

        tex_path = build_latex_cv(rows, args.out, args.cv_md)
        print(f"Wrote {tex_path}", file=sys.stderr)
        if compile_pdf(tex_path):
            print(f"Wrote {tex_path.with_suffix('.pdf')}", file=sys.stderr)
        else:
            print("PDF build failed; CSV still available.", file=sys.stderr)

        log_path = args.out / "paper_report.log.json"
        log_path.write_text(json.dumps({
            "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "mode": "cv-driven",
            "cv_md": str(args.cv_md),
            "papers_dir": str(args.papers_dir),
            "paper_count": len(rows),
            "warnings": warnings,
        }, indent=2))
        print(f"Wrote {log_path} ({len(warnings)} warnings)", file=sys.stderr)
        return 0

    # --- Repo-driven mode (original behavior) --------------------------
    print(f"Scanning {len(paper_dirs)} papers from {args.papers_dir}", file=sys.stderr)

    rows: list[dict] = []
    warnings: list[str] = []
    for i, repo in enumerate(paper_dirs, 1):
        if i == 1 or i % 25 == 0 or i == len(paper_dirs):
            print(f"  [{i}/{len(paper_dirs)}] {repo.name}", file=sys.stderr)
        try:
            row = process_paper(
                repo, warnings,
                online_lookup=not args.skip_online,
                overleaf_index=overleaf_index,
            )
            rows.append(row)
        except Exception as e:
            warnings.append(f"{repo.name}: fatal error: {e}")
            rows.append({
                "repo_name": f"paper-{repo.name}",
                "paper_name": "(error)",
                "authors": "",
                "final_draft_path": "",
                "publication_url": "",
                "experimental_code": "ERROR",
                "conversion_code": "ERROR",
                "analysis_code": "ERROR",
                "data_locations": "ERROR",
                "draft_date": "",
            })

    # CSV
    csv_path = args.out / "paper_report.csv"
    fieldnames = [
        "repo_name", "paper_name", "authors",
        "final_draft_path", "publication_url",
        "experimental_code", "conversion_code",
        "analysis_code", "data_locations",
        "draft_date",
    ]
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {csv_path} ({len(rows)} rows)", file=sys.stderr)

    # LaTeX + PDF
    tex_path = build_latex(rows, args.out, args.papers_dir)
    print(f"Wrote {tex_path}", file=sys.stderr)
    if compile_pdf(tex_path):
        print(f"Wrote {tex_path.with_suffix('.pdf')}", file=sys.stderr)
    else:
        print("PDF build failed; CSV still available.", file=sys.stderr)

    # Log
    log_path = args.out / "paper_report.log.json"
    log_path.write_text(json.dumps({
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "papers_dir": str(args.papers_dir),
        "paper_count": len(rows),
        "warnings": warnings,
    }, indent=2))
    print(f"Wrote {log_path} ({len(warnings)} warnings)", file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
