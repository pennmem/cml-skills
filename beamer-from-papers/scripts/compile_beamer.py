#!/usr/bin/env python3
"""Compile a Beamer .tex file to PDF with error filtering.

Usage:
    python compile_beamer.py <path/to/deck.tex> [--skip-bib] [--notes-only]

Runs pdflatex → bibtex → pdflatex → pdflatex, capturing logs and surfacing
only the actionable error lines (undefined references, missing figures,
package errors) instead of the full 2000-line LaTeX log.

Outputs the PDF next to the .tex. If --notes-only, toggles the Beamer notes
option and produces a second PDF with only the speaker notes.
"""

import argparse
import re
import subprocess
import sys
import shutil
from pathlib import Path


REQUIRED_TOOLS = ["pdflatex"]
OPTIONAL_TOOLS = ["bibtex", "biber"]


def check_tools() -> list[str]:
    """Return a list of missing required tools, empty if all present."""
    missing = [t for t in REQUIRED_TOOLS if not shutil.which(t)]
    return missing


def extract_errors(log_text: str) -> list[str]:
    """Pull out the actionable errors from a LaTeX log."""
    errors: list[str] = []
    lines = log_text.splitlines()
    for i, line in enumerate(lines):
        # Actual LaTeX errors begin with "!"
        if line.startswith("!"):
            # Take the ! line and the next line or two for context
            block = [line]
            for off in range(1, 4):
                if i + off < len(lines) and lines[i + off].strip():
                    block.append(lines[i + off])
                else:
                    break
            errors.append("\n".join(block))
        # Missing figures
        elif "LaTeX Warning: File" in line and "not found" in line:
            errors.append(line.strip())
        # Undefined citations / references (only warn, don't fail)
        elif "LaTeX Warning: Citation" in line or "LaTeX Warning: Reference" in line:
            errors.append(line.strip())
    return errors


def run_pass(cmd: list[str], cwd: Path, label: str) -> tuple[int, str]:
    """Run a single compile pass, return (returncode, combined_log)."""
    try:
        result = subprocess.run(
            cmd, cwd=cwd, capture_output=True, text=True, timeout=120
        )
        return result.returncode, result.stdout + result.stderr
    except subprocess.TimeoutExpired:
        return 124, f"{label}: timed out after 120s"
    except FileNotFoundError as e:
        return 127, f"{label}: {e}"


def compile_deck(tex_path: Path, skip_bib: bool, notes_only: bool) -> int:
    cwd = tex_path.parent
    stem = tex_path.stem

    if notes_only:
        # Rewrite a copy of the tex with the notes option flipped
        src = tex_path.read_text()
        src = re.sub(
            r"\\setbeameroption\{hide notes\}",
            r"\\setbeameroption{show only notes}",
            src,
        )
        notes_path = cwd / f"{stem}_notes.tex"
        notes_path.write_text(src)
        tex_path = notes_path
        stem = notes_path.stem

    # Pass 1
    rc, log1 = run_pass(
        ["pdflatex", "-interaction=nonstopmode", tex_path.name],
        cwd, "pdflatex pass 1"
    )
    if rc not in (0, 1):  # 1 = warnings only
        print(f"ERROR: pdflatex pass 1 failed (rc={rc})", file=sys.stderr)
        for e in extract_errors(log1)[:5]:
            print(f"  {e}", file=sys.stderr)
        return rc

    # Bibtex
    if not skip_bib and (cwd / f"{stem}.aux").exists():
        aux_text = (cwd / f"{stem}.aux").read_text(errors="replace")
        if "\\citation" in aux_text or "\\bibdata" in aux_text:
            rc_bib, log_bib = run_pass(["bibtex", stem], cwd, "bibtex")
            if rc_bib != 0:
                # bibtex often exits non-zero on minor warnings; don't abort
                print(f"WARN: bibtex rc={rc_bib}", file=sys.stderr)

    # Pass 2 and 3 (resolves citations, then TOC / cross-refs)
    for n in (2, 3):
        rc, log = run_pass(
            ["pdflatex", "-interaction=nonstopmode", tex_path.name],
            cwd, f"pdflatex pass {n}"
        )

    pdf_path = cwd / f"{stem}.pdf"
    if not pdf_path.exists():
        print(f"ERROR: no PDF produced at {pdf_path}", file=sys.stderr)
        for e in extract_errors(log)[:5]:
            print(f"  {e}", file=sys.stderr)
        return 1

    # Report warnings but don't fail on them
    warnings = extract_errors(log)
    if warnings:
        print(f"Compiled {pdf_path} with {len(warnings)} warnings:", file=sys.stderr)
        for w in warnings[:10]:
            print(f"  {w}", file=sys.stderr)
        if len(warnings) > 10:
            print(f"  ... and {len(warnings) - 10} more", file=sys.stderr)

    print(str(pdf_path))
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("tex_path", type=Path)
    ap.add_argument("--skip-bib", action="store_true")
    ap.add_argument("--notes-only", action="store_true",
                    help="Produce a notes-only PDF alongside the talk PDF")
    args = ap.parse_args()

    if not args.tex_path.exists():
        print(f"ERROR: {args.tex_path} not found", file=sys.stderr)
        return 1

    missing = check_tools()
    if missing:
        print(
            f"ERROR: missing LaTeX tools: {', '.join(missing)}\n"
            f"See references/latex_setup.md for installation help.",
            file=sys.stderr,
        )
        return 127

    return compile_deck(args.tex_path, args.skip_bib, args.notes_only)


if __name__ == "__main__":
    sys.exit(main())
