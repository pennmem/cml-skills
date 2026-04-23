#!/usr/bin/env python3
"""Build a poster plan from a paper bundle + parameters, then emit beamerposter .tex.

Usage:
    python plan_poster.py <bundle> \\
        --output-dir <dir> \\
        --title "Poster title" \\
        --author "Name 1" --author "Name 2" \\
        [--affiliation "Penn"] \\
        [--size 48x36-landscape|36x48-portrait|A0-portrait|A0-landscape|custom] \\
        [--columns 3] \\
        [--plan-only]

This is the bridge: bundle -> poster plan (JSON) -> beamerposter .tex.

Without --plan-only it writes both <output-dir>/plan.json and
<output-dir>/poster.tex (plus copies figures and bib into place). With
--plan-only it writes just plan.json so a caller can inspect/edit the
plan before LaTeX emission.

NOTE: This is a SCAFFOLD. Deep reading and content generation (selecting
WHICH 3-5 figures, writing motivation/methods/conclusions text) are stubs
that emit [TODO ...] placeholders. Fill those in per the reading_strategy.md,
content_selection.md, and figure_selection.md guidance. The structural
plumbing (bundle loading, figure copying, bib inclusion, layout emission)
works end-to-end.
"""

import argparse
import json
import re
import shutil
import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
TEMPLATE_PATH = SCRIPT_DIR.parent / "assets" / "cml_poster_template.tex"


# ---------------------------------------------------------------------------
# Size presets
# ---------------------------------------------------------------------------

SIZE_PRESETS = {
    "48x36-landscape": {
        "beamerposter_opts": "orientation=landscape,size=custom,width=121.9,height=91.4",
        "default_columns": 3,
    },
    "36x48-portrait": {
        "beamerposter_opts": "orientation=portrait,size=custom,width=91.4,height=121.9",
        "default_columns": 2,
    },
    "A0-portrait": {
        "beamerposter_opts": "orientation=portrait,size=a0",
        "default_columns": 2,
    },
    "A0-landscape": {
        "beamerposter_opts": "orientation=landscape,size=a0",
        "default_columns": 3,
    },
    "42x42": {
        "beamerposter_opts": "orientation=portrait,size=custom,width=106.7,height=106.7",
        "default_columns": 3,
    },
}


# ---------------------------------------------------------------------------
# Bundle loading
# ---------------------------------------------------------------------------

def load_bundle(bundle_path: Path) -> dict:
    """Load a paper bundle's manifest and core contents."""
    manifest_path = bundle_path / "manifest.json"
    if not manifest_path.exists():
        raise FileNotFoundError(f"No manifest.json in {bundle_path}")
    manifest = json.loads(manifest_path.read_text())
    abstract_path = bundle_path / "abstract.txt"
    manifest["_bundle_path"] = str(bundle_path.resolve())
    manifest["_abstract_text"] = abstract_path.read_text() if abstract_path.exists() else ""
    return manifest


# ---------------------------------------------------------------------------
# Plan construction
# ---------------------------------------------------------------------------

def plan_single_paper(bundle: dict, size: str, columns: int) -> dict:
    """Build a poster plan from one paper bundle.

    This is the scaffold: blocks are emitted with placeholder content. The
    content-generation pass (reading the paper, selecting the 3-5 figures,
    writing motivation/methods/interpretations/conclusions) is a separate
    step driven by the reading_strategy.md + content_selection.md guidance.
    """
    title = bundle.get("title") or bundle["paper_slug"]
    year = bundle.get("year")
    authors = bundle.get("authors") or []
    fig_files = bundle.get("figures", {}).get("files", [])

    # Figure budget: 3-5 for a single-paper poster. Scaffold takes first N.
    # The real figure-selection logic is the deep-reading pass.
    fig_budget = min(5, max(3, len(fig_files)))
    selected_figs = fig_files[:fig_budget]

    # Distribute blocks across columns. For 3-column landscape:
    #   col 1: motivation + question + methods
    #   col 2: first 2 result figures
    #   col 3: remaining result figures + conclusions + references
    blocks: list[dict] = []

    # Column 1: setup
    blocks.append({
        "kind": "motivation", "column": 1, "title": "Motivation",
        "text": "[TODO — 40-80 words. Lead with the phenomenon or puzzle, not the literature.]",
    })
    blocks.append({
        "kind": "question", "column": 1, "title": "Question",
        "text": "[TODO — one-sentence research question, visually emphasized.]",
    })
    blocks.append({
        "kind": "methods", "column": 1, "title": "Methods",
        "text": "[TODO — 50-100 words. Task, N, key DV. Prefer a schematic to prose.]",
        "figure": None,
    })

    # Columns 2 and 3: results
    if columns >= 3:
        # 3-column layout: split figures between col 2 and col 3
        split = max(1, len(selected_figs) // 2)
        col2_figs = selected_figs[:split]
        col3_figs = selected_figs[split:]
    else:
        # 2-column layout: all results in col 2
        col2_figs = selected_figs
        col3_figs = []

    for i, fig in enumerate(col2_figs):
        blocks.append({
            "kind": "result", "column": 2,
            "title": f"[TODO — takeaway-style heading for {fig}]",
            "figure": f"figures/{fig}",
            "caption": "[TODO — 30-80 words. What to notice and what it means.]",
        })
    for i, fig in enumerate(col3_figs):
        blocks.append({
            "kind": "result", "column": 3,
            "title": f"[TODO — takeaway-style heading for {fig}]",
            "figure": f"figures/{fig}",
            "caption": "[TODO — 30-80 words. What to notice and what it means.]",
        })

    # Final column closer
    close_col = columns  # last column
    blocks.append({
        "kind": "conclusions", "column": close_col, "title": "Conclusions",
        "bullets": [
            "[TODO — complete-sentence claim 1.]",
            "[TODO — complete-sentence claim 2.]",
            "[TODO — complete-sentence claim 3.]",
        ],
    })
    blocks.append({
        "kind": "references", "column": close_col,
        "title": "References & Acknowledgments",
        "refs": [
            "[TODO — reference 1]",
            "[TODO — reference 2]",
        ],
        "acknowledgments": "[TODO — grant numbers, collaborators, contact.]",
    })

    return {
        "title": title,
        "authors": authors,
        "year": year,
        "size": size,
        "columns": columns,
        "blocks": blocks,
        "bundles": [bundle],
    }


# ---------------------------------------------------------------------------
# Asset assembly (figures + bib)
# ---------------------------------------------------------------------------

def assemble_assets(plan: dict, output_dir: Path) -> None:
    """Copy figures + (optionally) bib from the bundle into the output directory."""
    fig_out = output_dir / "figures"
    fig_out.mkdir(parents=True, exist_ok=True)

    for bundle in plan["bundles"]:
        bundle_path = Path(bundle["_bundle_path"])
        bundle_figs = bundle_path / "figures"
        if bundle_figs.is_dir():
            for f in bundle_figs.iterdir():
                if f.is_file():
                    shutil.copy2(f, fig_out / f.name)
        # Copy bib if present — the poster template doesn't use \bibliography
        # by default (posters use hand-formatted refs), but we stage it for
        # users who want to switch the template to natbib-superscripts.
        bib_path = bundle_path / "references.bib"
        if bib_path.exists():
            shutil.copy2(bib_path, output_dir / "references.bib")


# ---------------------------------------------------------------------------
# Beamerposter emission
# ---------------------------------------------------------------------------

def emit_poster(plan: dict, output_dir: Path) -> Path:
    """Write poster.tex from plan into output_dir. Returns the .tex path."""
    template = TEMPLATE_PATH.read_text()

    # Fill metadata
    authors_formatted = _format_authors_with_affiliations(plan["authors"])
    affiliations_formatted = r"$^1$University of Pennsylvania"  # default; user can edit

    subs = {
        "<<TITLE>>": _latex_escape(plan["title"]),
        "<<AUTHORS>>": authors_formatted,
        "<<AFFILIATIONS>>": affiliations_formatted,
        "<<VENUE>>": "",
    }
    for k, v in subs.items():
        template = template.replace(k, v)

    # Swap the beamerposter size options to match the plan
    size_opts = SIZE_PRESETS[plan["size"]]["beamerposter_opts"]
    template = re.sub(
        r"\\usepackage\[[^\]]*\]\{beamerposter\}",
        f"\\\\usepackage[{size_opts},scale=1.35]{{beamerposter}}",
        template,
    )

    # Adjust column width fractions based on columns count
    col_width = {2: "0.48", 3: "0.32", 4: "0.23"}[plan["columns"]]
    template = re.sub(
        r"\\begin\{column\}\{0\.32\\textwidth\}",
        f"\\\\begin{{column}}{{{col_width}\\\\textwidth}}",
        template,
    )

    # Replace everything between \begin{columns} and \end{columns} with our blocks
    generated_body = _render_blocks(plan["blocks"], plan["columns"], col_width)

    # Find the columns region in the template and swap in our content
    # Use [T] marker to find the opening, \end{columns} to close
    columns_open = r"\begin{columns}[T]"
    columns_close = r"\end{columns}"
    open_idx = template.find(columns_open)
    close_idx = template.find(columns_close, open_idx)
    if open_idx == -1 or close_idx == -1:
        raise RuntimeError("Template missing columns markers")
    close_idx += len(columns_close)

    template = (
        template[:open_idx]
        + columns_open + "\n\n"
        + "% Generated by scripts/plan_poster.py from the poster plan.\n\n"
        + generated_body
        + "\n" + columns_close
        + template[close_idx:]
    )

    tex_path = output_dir / "poster.tex"
    tex_path.write_text(template)
    return tex_path


def _render_blocks(blocks: list[dict], n_columns: int, col_width: str) -> str:
    """Render all blocks, grouped by column."""
    by_col: dict[int, list[dict]] = {i: [] for i in range(1, n_columns + 1)}
    for b in blocks:
        col = b.get("column", 1)
        # Clamp to valid range — if someone set column=3 in a 2-col layout, push to col 2
        col = min(col, n_columns)
        by_col[col].append(b)

    parts: list[str] = []
    for col_num in range(1, n_columns + 1):
        parts.append(f"\\begin{{column}}{{{col_width}\\textwidth}}\n")
        for b in by_col[col_num]:
            parts.append(_render_one_block(b))
            parts.append("\n")
        parts.append("\\end{column}\n")
    return "\n".join(parts)


def _render_one_block(b: dict) -> str:
    kind = b["kind"]
    title = _latex_escape(b.get("title", ""))

    if kind == "motivation" or kind == "methods":
        text = _latex_escape(b.get("text", ""))
        fig_part = ""
        if b.get("figure"):
            fig_part = (
                f"\n  \\begin{{center}}\n"
                f"    \\includegraphics[width=0.95\\textwidth]{{{b['figure']}}}\n"
                f"  \\end{{center}}"
            )
        return (
            f"\\begin{{block}}{{{title}}}\n"
            f"  {text}{fig_part}\n"
            f"\\end{{block}}\n"
        )

    if kind == "question":
        text = _latex_escape(b.get("text", ""))
        return (
            f"\\begin{{block}}{{{title}}}\n"
            f"  \\begin{{center}}\n"
            f"    \\bfseries {text}\n"
            f"  \\end{{center}}\n"
            f"\\end{{block}}\n"
        )

    if kind == "result":
        fig = b.get("figure", "")
        caption = _latex_escape(b.get("caption", ""))
        fig_line = (
            f"    \\includegraphics[width=0.95\\textwidth]{{{fig}}}"
            if fig else "    [TODO --- figure placeholder]"
        )
        return (
            f"\\begin{{block}}{{{title}}}\n"
            f"  \\begin{{center}}\n"
            f"{fig_line}\n"
            f"  \\end{{center}}\n"
            f"  \\vspace{{0.3em}}\n"
            f"  {{\\small {caption}}}\n"
            f"\\end{{block}}\n"
        )

    if kind == "conclusions":
        bullets = b.get("bullets", [])
        # Brace-wrap each bullet to prevent LaTeX misparsing leading [
        bullet_tex = "\n".join(
            f"    \\item {{{_latex_escape(bull)}}}" for bull in bullets
        )
        return (
            f"\\begin{{block}}{{{title}}}\n"
            f"  \\begin{{itemize}}\n{bullet_tex}\n  \\end{{itemize}}\n"
            f"\\end{{block}}\n"
        )

    if kind == "references":
        refs = b.get("refs", [])
        ack = _latex_escape(b.get("acknowledgments", ""))
        # Use \par + {}[N] guard to avoid the \\[N] parsing bug
        ref_lines = "\n".join(
            f"    {{}}[{i+1}] {_latex_escape(r)}\\par"
            for i, r in enumerate(refs)
        )
        return (
            f"\\begin{{block}}{{{title}}}\n"
            f"  {{\\scriptsize\n"
            f"    \\textbf{{References:}}\\par\n"
            f"{ref_lines}\n"
            f"    \\vspace{{0.5em}}\n"
            f"    \\textbf{{Acknowledgments:}} {ack}\n"
            f"  }}\n"
            f"\\end{{block}}\n"
        )

    return f"% unsupported block kind: {kind}\n"


def _format_authors_with_affiliations(authors: list[str]) -> str:
    """Format like 'A. Smith$^1$, B. Jones$^1$' — all at affiliation 1 by default."""
    if not authors:
        return "[TODO author]"
    parts = [f"{_latex_escape(a)}$^1$" for a in authors]
    return ", ".join(parts)


def _latex_escape(s: str) -> str:
    if s is None:
        return ""
    replacements = [
        ("\\", r"\textbackslash{}"),
        ("&", r"\&"),
        ("%", r"\%"),
        ("$", r"\$"),
        ("#", r"\#"),
        ("_", r"\_"),
        ("{", r"\{"),
        ("}", r"\}"),
        ("~", r"\textasciitilde{}"),
        ("^", r"\textasciicircum{}"),
    ]
    for a, b in replacements:
        s = s.replace(a, b)
    return s


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("bundle", type=Path, help="Path to paper bundle directory")
    ap.add_argument("--output-dir", type=Path, required=True)
    ap.add_argument("--title", help="Override poster title")
    ap.add_argument("--author", action="append", dest="authors",
                    help="Override author list; pass multiple times")
    ap.add_argument("--affiliation", action="append", dest="affiliations",
                    help="Affiliation(s); currently only used via --plan-only override")
    ap.add_argument("--size", choices=list(SIZE_PRESETS.keys()),
                    default="48x36-landscape")
    ap.add_argument("--columns", type=int, default=None,
                    help="Override default column count for the chosen size")
    ap.add_argument("--plan-only", action="store_true")
    args = ap.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)

    bundle = load_bundle(args.bundle)

    columns = args.columns if args.columns is not None else SIZE_PRESETS[args.size]["default_columns"]

    plan = plan_single_paper(bundle, args.size, columns)

    if args.title:
        plan["title"] = args.title
    if args.authors:
        plan["authors"] = args.authors

    # Write plan.json (strip the non-serializable bundle reference)
    plan_for_json = {k: v for k, v in plan.items() if k != "bundles"}
    plan_for_json["bundle_paths"] = [b["_bundle_path"] for b in plan["bundles"]]
    (args.output_dir / "plan.json").write_text(json.dumps(plan_for_json, indent=2))

    if args.plan_only:
        print(f"Plan: {args.output_dir / 'plan.json'}")
        return 0

    assemble_assets(plan, args.output_dir)
    tex_path = emit_poster(plan, args.output_dir)
    print(f"Poster: {tex_path}")
    print(f"Plan:   {args.output_dir / 'plan.json'}")
    print(f"Next:   python compile_poster.py {tex_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
