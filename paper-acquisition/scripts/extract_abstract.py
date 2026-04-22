#!/usr/bin/env python3
r"""Extract the abstract from a paper's .tex source or .pdf.

Usage:
    python extract_abstract.py <path/to/paper.tex>
    python extract_abstract.py <path/to/paper.pdf>

Returns the abstract as plain text on stdout. Exits 0 on success, 1 if
no abstract could be found, 2 on hard error (file unreadable, etc.).

For .tex: looks for \begin{abstract}...\end{abstract}.
For .pdf: extracts page 1 text, finds the word "Abstract", takes the
next paragraph until a blank line or a section heading.
"""

import argparse
import re
import sys
from pathlib import Path


def extract_from_tex(text: str) -> str | None:
    """Find \\begin{abstract}...\\end{abstract}."""
    m = re.search(
        r"\\begin\{abstract\}(.*?)\\end\{abstract\}",
        text,
        re.DOTALL | re.IGNORECASE,
    )
    if m:
        return _clean_latex(m.group(1))

    # Some templates use \abstract{...} instead
    m = re.search(r"\\abstract\{((?:[^{}]|\{[^{}]*\})*)\}", text, re.DOTALL)
    if m:
        return _clean_latex(m.group(1))

    # APA template style: \keywords after abstract, look for stuff between maketitle and keywords
    m = re.search(
        r"\\maketitle\s*(.*?)(?:\\keywords|\\section)",
        text,
        re.DOTALL | re.IGNORECASE,
    )
    if m:
        candidate = _clean_latex(m.group(1))
        if 100 < len(candidate) < 3000:  # plausible abstract length
            return candidate

    return None


def _clean_latex(s: str) -> str:
    """Strip common LaTeX commands from extracted text. Imperfect but OK."""
    # Remove comments
    s = re.sub(r"(?<!\\)%.*$", "", s, flags=re.MULTILINE)
    # Remove simple commands like \emph{x} -> x, \textbf{x} -> x
    for _ in range(3):  # a few passes for nested
        s = re.sub(r"\\[a-zA-Z]+\*?\{([^{}]*)\}", r"\1", s)
    # Remove bare commands with no args
    s = re.sub(r"\\[a-zA-Z]+\*?", "", s)
    # Collapse whitespace
    s = re.sub(r"\s+", " ", s).strip()
    return s


def extract_from_pdf(path: Path) -> str | None:
    """Use pdftotext or pypdf to get page 1, then find the abstract block."""
    try:
        import subprocess
        result = subprocess.run(
            ["pdftotext", "-f", "1", "-l", "1", str(path), "-"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode == 0 and result.stdout.strip():
            page1 = result.stdout
        else:
            raise RuntimeError("pdftotext failed")
    except (FileNotFoundError, RuntimeError):
        # Fallback to pypdf
        try:
            from pypdf import PdfReader
            reader = PdfReader(str(path))
            if len(reader.pages) == 0:
                return None
            page1 = reader.pages[0].extract_text() or ""
        except Exception:
            return None

    return _find_abstract_in_text(page1)


def _find_abstract_in_text(text: str) -> str | None:
    """Given page text, find 'Abstract' heading and take the following paragraph."""
    # Try matching 'Abstract' as a standalone heading
    m = re.search(
        r"\bAbstract\b\s*[:\n]\s*(.+?)(?=\n\s*\n|\n\s*(?:Keywords|Introduction|1\s*\.|1\s+Introduction))",
        text,
        re.DOTALL | re.IGNORECASE,
    )
    if m:
        candidate = re.sub(r"\s+", " ", m.group(1)).strip()
        if 50 < len(candidate) < 5000:
            return candidate

    # Fallback: look for any block starting with "Abstract" and up to 2000 chars
    m = re.search(r"\bAbstract\b[:\s]+(.{100,2000}?)(?=\n\s*\n)", text, re.DOTALL)
    if m:
        return re.sub(r"\s+", " ", m.group(1)).strip()

    return None


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("path", type=Path)
    args = ap.parse_args()

    if not args.path.exists():
        print(f"ERROR: {args.path} does not exist", file=sys.stderr)
        return 2

    ext = args.path.suffix.lower()
    try:
        if ext == ".tex":
            text = args.path.read_text(encoding="utf-8", errors="replace")
            abstract = extract_from_tex(text)
        elif ext == ".pdf":
            abstract = extract_from_pdf(args.path)
        else:
            print(f"ERROR: unsupported file type: {ext}", file=sys.stderr)
            return 2
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 2

    if abstract is None:
        print("No abstract found.", file=sys.stderr)
        return 1

    print(abstract)
    return 0


if __name__ == "__main__":
    sys.exit(main())
