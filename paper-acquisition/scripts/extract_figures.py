#!/usr/bin/env python3
"""Copy all figure files from a paper repo into a flat figures/ dir.

Usage:
    python extract_figures.py <source_repo_dir> <output_figures_dir>

Walks the repo, finds files with figure-like extensions (.pdf, .png, .jpg,
.eps, .svg) inside directories that look like they hold figures (Figs/,
figures/, fig/, images/), plus any top-level figure files.

Copies them to the output directory, preserving just the basename.
Duplicates are renamed with a numeric suffix.
"""

import argparse
import shutil
import sys
from pathlib import Path


FIGURE_EXTS = {".pdf", ".png", ".jpg", ".jpeg", ".eps", ".svg", ".gif", ".tiff", ".tif"}

# Directories likely to contain paper figures (case-insensitive)
FIGURE_DIR_PATTERNS = {"fig", "figs", "figure", "figures", "image", "images", "plot", "plots"}

# Directories to ALWAYS skip (not paper figures)
SKIP_DIRS = {
    ".git", "__pycache__", "node_modules", ".ipynb_checkpoints",
    "venv", ".venv", "env", ".env",
}


def is_in_figure_dir(path: Path, repo_root: Path) -> bool:
    """Check if path is inside a directory matching figure conventions."""
    rel = path.relative_to(repo_root)
    for part in rel.parts[:-1]:
        if part.lower() in FIGURE_DIR_PATTERNS:
            return True
    return False


def is_skippable(path: Path, repo_root: Path) -> bool:
    rel = path.relative_to(repo_root)
    return any(part in SKIP_DIRS for part in rel.parts)


def find_figures(repo_root: Path) -> list[Path]:
    """Return candidate figure files in the repo."""
    candidates: list[Path] = []
    for p in repo_root.rglob("*"):
        if not p.is_file():
            continue
        if p.suffix.lower() not in FIGURE_EXTS:
            continue
        if is_skippable(p, repo_root):
            continue
        # Include if in a figure-like directory, OR at the top level
        rel = p.relative_to(repo_root)
        if len(rel.parts) == 1 or is_in_figure_dir(p, repo_root):
            candidates.append(p)
    return sorted(candidates)


def is_likely_paper_figure(path: Path) -> bool:
    """Filter out figures that are almost certainly not paper figures.

    PDFs at the top level are often the *compiled paper itself*, not a
    figure. Same for .pdf files whose name matches the repo name.
    """
    name_lower = path.name.lower()
    # Drop things that look like compiled paper PDFs
    if path.suffix.lower() == ".pdf" and any(
        s in name_lower
        for s in ("manuscript", "submission", "paper.pdf", "supplement", "final")
    ):
        return False
    return True


def copy_figures(figures: list[Path], output_dir: Path) -> list[str]:
    """Copy figures to output_dir; return list of final filenames."""
    output_dir.mkdir(parents=True, exist_ok=True)
    final_names: list[str] = []
    for fig in figures:
        target = output_dir / fig.name
        # Handle collisions
        suffix_num = 1
        while target.exists():
            stem, ext = fig.stem, fig.suffix
            target = output_dir / f"{stem}_{suffix_num}{ext}"
            suffix_num += 1
        shutil.copy2(fig, target)
        final_names.append(target.name)
    return sorted(final_names)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("source", type=Path, help="Source repo directory")
    ap.add_argument("output", type=Path, help="Output figures directory")
    ap.add_argument(
        "--keep-all",
        action="store_true",
        help="Don't filter out likely non-figure PDFs (manuscripts, supplements)",
    )
    args = ap.parse_args()

    if not args.source.is_dir():
        print(f"ERROR: {args.source} is not a directory", file=sys.stderr)
        return 1

    figs = find_figures(args.source)
    if not args.keep_all:
        figs = [f for f in figs if is_likely_paper_figure(f)]

    names = copy_figures(figs, args.output)
    print(f"Copied {len(names)} figures to {args.output}")
    for n in names:
        print(f"  {n}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
