#!/usr/bin/env python3
"""Compile a beamerposter .tex file to PDF with error filtering.

Usage:
    python compile_poster.py <path/to/poster.tex> [--compress]

Runs pdflatex twice (no TOC so two passes suffices), capturing logs and
surfacing only actionable errors (undefined references, missing figures,
package errors) instead of the full LaTeX log.

--compress runs Ghostscript with /prepress settings afterwards to reduce
PDF size while preserving print quality. Recommended for posters over 30MB.

Known benign warnings this script filters out:
  - "No file X.nav" / "No file X.aux" on first run
  - Font shape substitution warnings (beamer fallbacks at extreme sizes)
"""

import argparse
import re
import subprocess
import sys
import shutil
from pathlib import Path


REQUIRED_TOOLS = ["pdflatex"]


def check_tools() -> list[str]:
    return [t for t in REQUIRED_TOOLS if not shutil.which(t)]


BENIGN_WARNINGS = [
    r"No file .*\.nav\.",
    r"No file .*\.aux\.",
    r"No file .*\.toc\.",
    r"Font shape .* in size .* not available",
    r"^\(Font\) +size .* substituted",
    r"Overfull \\hbox",  # common in posters, usually visible and user-fixable
    r"Underfull \\hbox",
    r"Underfull \\vbox",
]
BENIGN_PATTERN = re.compile("|".join(BENIGN_WARNINGS))


def extract_errors(log_text: str) -> list[str]:
    """Pull out the actionable errors from a LaTeX log, skipping benign ones."""
    errors: list[str] = []
    lines = log_text.splitlines()
    for i, line in enumerate(lines):
        if BENIGN_PATTERN.search(line):
            continue
        if line.startswith("!"):
            # Collect 1-3 lines of context after the bang
            block = [line]
            for off in range(1, 4):
                if i + off < len(lines) and lines[i + off].strip():
                    block.append(lines[i + off])
                else:
                    break
            errors.append("\n".join(block))
        elif "LaTeX Warning: File" in line and "not found" in line:
            errors.append(line.strip())
        elif "LaTeX Warning: Citation" in line or "LaTeX Warning: Reference" in line:
            errors.append(line.strip())
    return errors


def run_pass(cmd: list[str], cwd: Path, label: str) -> tuple[int, str]:
    try:
        result = subprocess.run(
            cmd, cwd=cwd, capture_output=True, text=True, timeout=180
        )
        return result.returncode, result.stdout + result.stderr
    except subprocess.TimeoutExpired:
        return 124, f"{label}: timed out after 180s"
    except FileNotFoundError as e:
        return 127, f"{label}: {e}"


def compile_poster(tex_path: Path, compress: bool) -> int:
    cwd = tex_path.parent
    stem = tex_path.stem

    # Pass 1
    rc1, log1 = run_pass(
        ["pdflatex", "-interaction=nonstopmode", tex_path.name],
        cwd, "pdflatex pass 1"
    )

    # Optional bibtex — only if the .aux file references a .bib
    aux = cwd / f"{stem}.aux"
    if aux.exists():
        aux_text = aux.read_text(errors="replace")
        if "\\citation" in aux_text or "\\bibdata" in aux_text:
            rc_bib, log_bib = run_pass(["bibtex", stem], cwd, "bibtex")
            if rc_bib != 0:
                print(f"WARN: bibtex rc={rc_bib}", file=sys.stderr)

    # Pass 2 (resolves cross-refs and citation numbers)
    rc2, log2 = run_pass(
        ["pdflatex", "-interaction=nonstopmode", tex_path.name],
        cwd, "pdflatex pass 2"
    )

    pdf_path = cwd / f"{stem}.pdf"
    if not pdf_path.exists():
        print("ERROR: no PDF produced.", file=sys.stderr)
        for e in extract_errors(log2)[:5]:
            print(f"  {e}", file=sys.stderr)
        return 1

    # Surface actionable warnings
    errs = extract_errors(log2)
    if errs:
        print(f"Compiled {pdf_path} with {len(errs)} warning(s):", file=sys.stderr)
        for w in errs[:10]:
            print(f"  {w}", file=sys.stderr)
        if len(errs) > 10:
            print(f"  ... and {len(errs) - 10} more", file=sys.stderr)

    # Optional compression
    if compress:
        compressed = cwd / f"{stem}_compressed.pdf"
        if shutil.which("gs"):
            rc_gs = subprocess.run(
                [
                    "gs", "-dNOPAUSE", "-dBATCH", "-sDEVICE=pdfwrite",
                    "-dPDFSETTINGS=/prepress",
                    f"-sOutputFile={compressed}", str(pdf_path),
                ],
                capture_output=True, text=True, timeout=120,
            ).returncode
            if rc_gs == 0 and compressed.exists():
                orig_size = pdf_path.stat().st_size
                new_size = compressed.stat().st_size
                print(f"Compressed: {orig_size//1024}KB -> {new_size//1024}KB ({compressed})", file=sys.stderr)
                print(str(compressed))
                return 0
            else:
                print("WARN: ghostscript compression failed", file=sys.stderr)
        else:
            print("WARN: ghostscript (gs) not available; skipping compression", file=sys.stderr)

    print(str(pdf_path))
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("tex_path", type=Path)
    ap.add_argument("--compress", action="store_true",
                    help="Run Ghostscript /prepress compression after compile")
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

    return compile_poster(args.tex_path, args.compress)


if __name__ == "__main__":
    sys.exit(main())
