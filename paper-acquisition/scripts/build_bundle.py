#!/usr/bin/env python3
"""Build a standardized paper bundle from a source repo directory.

Usage:
    python build_bundle.py <source_repo> <output_bundle_dir> \\
        [--source-kind prepared_local|unprepared_local|github|user_upload] \\
        [--github-url URL] \\
        [--override-draft PATH]

The output directory will contain:
    manifest.json
    abstract.txt
    claude_md.md (if present in source)
    drafts/selected.tex (or .pdf)
    drafts/alternate_*
    figures/
    references.bib (if found)
    source/ -> symlink to original

See references/bundle_format.md for the full format spec.
"""

import argparse
import datetime as dt
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

# Make sibling scripts importable without installing
SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from parse_claude_md import parse_claude_md  # noqa: E402
from extract_abstract import extract_from_tex, extract_from_pdf  # noqa: E402
from extract_figures import find_figures, copy_figures, is_likely_paper_figure  # noqa: E402


DRAFT_EXCLUSION_PATTERNS = [
    "supplement", "supplementary", "_si.tex", "si_", "SI_",
    "response", "reviewer", "rebuttal",
    "cover_letter", "coverletter",
    "readme", "slides", "presentation", "talk",
]

# Directory name parts that indicate a file is NOT a draft (figures, images, etc.)
DRAFT_DIR_EXCLUSIONS = {"fig", "figs", "figure", "figures", "image", "images",
                        "plot", "plots", ".git", "__pycache__"}

TEX_FILE_GLOB = "*.tex"
PDF_FILE_GLOB = "*.pdf"
BIB_CANDIDATES = ["references.bib", "refs.bib", "bib.bib", "main.bib", "paper.bib"]


def is_excluded(path: Path, repo: Path | None = None) -> bool:
    name = path.name.lower()
    if any(p in name for p in DRAFT_EXCLUSION_PATTERNS):
        return True
    if repo is not None:
        try:
            rel = path.relative_to(repo)
            if any(part.lower() in DRAFT_DIR_EXCLUSIONS for part in rel.parts[:-1]):
                return True
        except ValueError:
            pass
    return False


def list_candidate_drafts(repo: Path, ext: str) -> list[Path]:
    return sorted(
        (p for p in repo.rglob(f"*{ext}") if p.is_file() and not is_excluded(p, repo)),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )


def select_draft(repo: Path, claude_fields: dict | None, override: Path | None):
    """Return (selected_path, reason, alternates)."""
    if override:
        if not override.exists():
            raise FileNotFoundError(f"--override-draft {override} does not exist")
        return override, "user_override", []

    # 1. CLAUDE.md hint
    if claude_fields:
        hint = claude_fields.get("main_document")
        if hint:
            candidate = repo / hint
            if candidate.exists():
                alts = list_candidate_drafts(repo, ".tex") + list_candidate_drafts(repo, ".pdf")
                alts = [a for a in alts if a != candidate]
                return candidate, "claude_md_hint", alts

    # 2. Most recent .tex
    tex_files = list_candidate_drafts(repo, ".tex")
    if tex_files:
        return tex_files[0], "most_recent_mtime", tex_files[1:]

    # 3. PDF fallback
    pdf_files = list_candidate_drafts(repo, ".pdf")
    if pdf_files:
        return pdf_files[0], "pdf_fallback", pdf_files[1:]

    return None, None, []


def find_bib(repo: Path) -> Path | None:
    for name in BIB_CANDIDATES:
        for match in repo.rglob(name):
            return match
    # Fallback: any .bib file
    for match in repo.rglob("*.bib"):
        return match
    return None


def parse_tex_metadata(tex_text: str) -> dict:
    """Extract title, authors, year from a .tex file. Best-effort."""
    meta: dict = {"title": None, "authors": None, "year": None}

    m = re.search(r"\\title\{((?:[^{}]|\{[^{}]*\})+)\}", tex_text, re.DOTALL)
    if m:
        meta["title"] = _clean(m.group(1))

    m = re.search(r"\\author\{((?:[^{}]|\{[^{}]*\})+)\}", tex_text, re.DOTALL)
    if m:
        # Split on \and FIRST, before LaTeX cleanup strips it out
        raw_blocks = re.split(r"\\and\b", m.group(1))
        authors = [_clean(b) for b in raw_blocks]
        # Also handle comma-separated authors within a single \author{} block
        flat: list[str] = []
        for a in authors:
            # Only split on commas if it doesn't look like "LastName, FirstName" style
            if a.count(",") > 1 or (a.count(",") == 1 and len(a.split(",")[1].strip().split()) > 2):
                flat.extend(s.strip() for s in a.split(",") if s.strip())
            else:
                flat.append(a)
        meta["authors"] = [a for a in flat if a]

    m = re.search(r"\\year\{(\d{4})\}", tex_text)
    if m:
        meta["year"] = int(m.group(1))
    else:
        m = re.search(r"\\date\{[^}]*?(\d{4})[^}]*\}", tex_text)
        if m:
            meta["year"] = int(m.group(1))

    return meta


def _clean(s: str) -> str:
    s = re.sub(r"\\[a-zA-Z]+\*?\{([^{}]*)\}", r"\1", s)
    s = re.sub(r"\\[a-zA-Z]+\*?", "", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def slugify(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")


def iso_now() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def iso_mtime(path: Path) -> str:
    return dt.datetime.fromtimestamp(
        path.stat().st_mtime, tz=dt.timezone.utc
    ).strftime("%Y-%m-%dT%H:%M:%SZ")


def build_bundle(
    source: Path,
    output: Path,
    source_kind: str,
    github_url: str | None,
    override_draft: Path | None,
) -> dict:
    """Build the bundle and return the manifest dict."""
    warnings: list[str] = []
    source = source.resolve()
    output.mkdir(parents=True, exist_ok=True)
    (output / "drafts").mkdir(exist_ok=True)

    # --- CLAUDE.md ---
    claude_md_path = source / "CLAUDE.md"
    claude_fields = None
    if claude_md_path.exists():
        shutil.copy2(claude_md_path, output / "claude_md.md")
        claude_fields = parse_claude_md(claude_md_path.read_text(errors="replace"))
        warnings.extend(
            f"CLAUDE.md: {w}" for w in claude_fields.get("parse_warnings", [])
        )
    else:
        if source_kind == "prepared_local" or source_kind == "github":
            warnings.append(f"Expected CLAUDE.md not found for {source_kind} source")

    # --- Draft selection ---
    selected, reason, alternates = select_draft(source, claude_fields, override_draft)
    if selected is None:
        warnings.append("No draft (.tex or .pdf) found in source repo")
        selected_info = None
    else:
        ext = selected.suffix
        selected_target = output / "drafts" / f"selected{ext}"
        shutil.copy2(selected, selected_target)
        selected_info = {
            "path": str(selected_target.relative_to(output)),
            "original_name": selected.name,
            "selection_reason": reason,
            "mtime_iso": iso_mtime(selected),
        }

    # --- Alternates ---
    alternate_info = []
    for i, alt in enumerate(alternates[:10]):  # cap at 10
        target = output / "drafts" / f"alternate_{i}_{alt.name}"
        try:
            shutil.copy2(alt, target)
            alternate_info.append({
                "path": str(target.relative_to(output)),
                "original_name": alt.name,
            })
        except OSError as e:
            warnings.append(f"Couldn't copy alternate draft {alt.name}: {e}")

    # --- Abstract ---
    abstract = None
    if selected and selected.suffix == ".tex":
        try:
            abstract = extract_from_tex(selected.read_text(errors="replace"))
        except Exception as e:
            warnings.append(f"Abstract extraction from .tex failed: {e}")
    elif selected and selected.suffix == ".pdf":
        try:
            abstract = extract_from_pdf(selected)
        except Exception as e:
            warnings.append(f"Abstract extraction from .pdf failed: {e}")

    if abstract:
        (output / "abstract.txt").write_text(abstract)
    else:
        (output / "abstract.txt").write_text("")
        warnings.append("Abstract could not be extracted")

    # --- Figures ---
    fig_dir = output / "figures"
    fig_dir.mkdir(exist_ok=True)
    raw_figs = find_figures(source)
    paper_figs = [f for f in raw_figs if is_likely_paper_figure(f)]
    fig_names = copy_figures(paper_figs, fig_dir)

    # --- Bibliography ---
    bib_src = find_bib(source)
    bib_info = None
    if bib_src:
        shutil.copy2(bib_src, output / "references.bib")
        bib_info = "references.bib"

    # --- Source link ---
    source_link = output / "source"
    if source_link.exists() or source_link.is_symlink():
        source_link.unlink()
    try:
        source_link.symlink_to(source)
    except OSError:
        # Fallback: record the path instead of symlinking (some filesystems refuse)
        warnings.append(f"Couldn't symlink source; left at {source}")

    # --- Metadata from .tex ---
    meta = {"title": None, "authors": None, "year": None}
    if selected and selected.suffix == ".tex":
        try:
            tex_text = selected.read_text(errors="replace")
            meta.update(parse_tex_metadata(tex_text))
        except Exception as e:
            warnings.append(f"Tex metadata extraction failed: {e}")

    # Fall back to repo name for title
    paper_slug = slugify(source.name)
    if not meta["title"]:
        meta["title"] = source.name
        warnings.append("Title not found in .tex; using repo directory name")

    manifest = {
        "schema_version": "1.0",
        "paper_slug": paper_slug,
        "title": meta["title"],
        "authors": meta["authors"],
        "year": meta["year"],
        "venue": None,
        "source": {
            "kind": source_kind,
            "path": str(source),
            "github_url": github_url,
            "mtime_iso": iso_mtime(source),
        },
        "selected_draft": selected_info,
        "alternate_drafts": alternate_info,
        "figures": {"count": len(fig_names), "files": fig_names},
        "bib_path": bib_info,
        "claude_md_present": claude_fields is not None,
        "claude_md_fields": {
            k: v for k, v in (claude_fields or {}).items()
            if k not in ("directory_structure", "extra", "parse_warnings")
        } if claude_fields else None,
        "warnings": warnings,
        "built_at": iso_now(),
    }

    (output / "manifest.json").write_text(json.dumps(manifest, indent=2))
    return manifest


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("source", type=Path, help="Source repo directory")
    ap.add_argument("output", type=Path, help="Output bundle directory")
    ap.add_argument(
        "--source-kind",
        choices=["prepared_local", "unprepared_local", "github", "user_upload"],
        default="prepared_local",
    )
    ap.add_argument("--github-url", default=None)
    ap.add_argument("--override-draft", type=Path, default=None)
    args = ap.parse_args()

    if not args.source.is_dir():
        print(f"ERROR: {args.source} is not a directory", file=sys.stderr)
        return 1

    manifest = build_bundle(
        args.source,
        args.output,
        args.source_kind,
        args.github_url,
        args.override_draft,
    )

    # Short summary to stdout
    print(f"Built bundle at {args.output}")
    print(f"  Title:   {manifest['title']}")
    print(f"  Year:    {manifest['year']}")
    print(f"  Draft:   {manifest['selected_draft']['original_name'] if manifest['selected_draft'] else '(none)'}")
    print(f"  Reason:  {manifest['selected_draft']['selection_reason'] if manifest['selected_draft'] else 'n/a'}")
    print(f"  Figures: {manifest['figures']['count']}")
    if manifest["warnings"]:
        print(f"  Warnings ({len(manifest['warnings'])}):")
        for w in manifest["warnings"]:
            print(f"    - {w}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
