#!/usr/bin/env python3
"""Build a slide plan from paper bundles + parameters, then emit Beamer .tex.

Usage:
    python plan_deck.py <bundle1> [<bundle2> ...] \\
        --output-dir <dir> \\
        --title "Talk Title" \\
        --author "Speaker Name" \\
        [--subtitle "..."] \\
        [--audience expert|grad|lecture] \\
        [--target-slides 25] \\
        [--structure one-per-paper|integrated] \\
        [--notes/--no-notes] \\
        [--plan-only]

This is the bridge: bundle(s) -> slide plan (JSON) -> Beamer .tex.

Without --plan-only it writes both <output-dir>/plan.json and
<output-dir>/deck.tex (plus copies figures and bib into place). With
--plan-only it writes just plan.json so a caller can inspect/edit the
plan before LaTeX emission.

NOTE: This is a SCAFFOLD. The deep-reading and content-generation steps
(selecting which figures to include, writing bullets, generating speaker
notes) are stubs that emit placeholder text. Fill those in per the
`reading_strategy.md` and `speaker_notes.md` guidance. The structural
plumbing (bundle loading, figure copying, bib merging, Beamer emission)
works end-to-end.
"""

import argparse
import json
import re
import shutil
import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
TEMPLATE_PATH = SCRIPT_DIR.parent / "assets" / "cml_beamer_template.tex"


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

def plan_single_paper(bundle: dict, target_slides: int, include_notes: bool) -> dict:
    """Construct a slide plan for a single-paper talk.

    This is the scaffold: slides of each kind are emitted with placeholder
    content. Real content generation is the responsibility of the caller,
    which should feed the bundle's draft, figures, and bib to a deep-reading
    pass (see reading_strategy.md) and fill in the placeholders.
    """
    title = bundle.get("title") or bundle["paper_slug"]
    year = bundle.get("year")
    authors = bundle.get("authors") or []

    # Budget slides across sections based on target
    budget = _slide_budget(target_slides)

    slides: list[dict] = []

    slides.append({"kind": "title", "content": None})
    slides.append({"kind": "outline", "content": None})

    # Motivation
    slides.append({"kind": "section_header", "title": "Motivation"})
    for i in range(budget["motivation"]):
        slides.append({
            "kind": "content",
            "section": "Motivation",
            "title": f"[TODO motivation slide {i+1}]",
            "bullets": ["[TODO bullet 1]", "[TODO bullet 2]"],
            "figure": None,
            "notes": "[TODO speaker note]" if include_notes else None,
        })

    # Background
    slides.append({"kind": "section_header", "title": "Background"})
    for i in range(budget["background"]):
        slides.append({
            "kind": "content",
            "section": "Background",
            "title": f"[TODO background {i+1}]",
            "bullets": ["[TODO]"],
            "figure": None,
            "notes": "[TODO speaker note]" if include_notes else None,
        })

    # Methods
    slides.append({"kind": "section_header", "title": "Methods"})
    for i in range(budget["methods"]):
        slides.append({
            "kind": "content",
            "section": "Methods",
            "title": f"[TODO methods {i+1}]",
            "bullets": ["[TODO design / participants / analyses]"],
            "figure": None,
            "notes": "[TODO]" if include_notes else None,
        })

    # Results — one figure per slide from the bundle
    slides.append({"kind": "section_header", "title": "Results"})
    fig_files = bundle.get("figures", {}).get("files", [])
    results_slide_count = min(budget["results"], len(fig_files)) if fig_files else budget["results"]
    for i, fig in enumerate(fig_files[:results_slide_count]):
        slides.append({
            "kind": "figure",
            "section": "Results",
            "title": f"[TODO — figure {i+1}]",
            "figure": f"figures/{fig}",
            "caption": "[TODO short caption]",
            "notes": "[TODO walk the figure]" if include_notes else None,
        })
    # Top up with content slides if we didn't have enough figures
    for i in range(results_slide_count, budget["results"]):
        slides.append({
            "kind": "content",
            "section": "Results",
            "title": f"[TODO result {i+1}]",
            "bullets": ["[TODO]"],
            "figure": None,
            "notes": "[TODO]" if include_notes else None,
        })

    # Discussion
    slides.append({"kind": "section_header", "title": "Discussion"})
    for i in range(budget["discussion"]):
        slides.append({
            "kind": "content",
            "section": "Discussion",
            "title": f"[TODO implication {i+1}]",
            "bullets": ["[TODO]"],
            "figure": None,
            "notes": "[TODO]" if include_notes else None,
        })

    slides.append({
        "kind": "content",
        "section": "Acknowledgments",
        "title": "Acknowledgments",
        "bullets": ["[TODO collaborators + funding]"],
        "figure": None,
        "notes": None,
    })
    slides.append({"kind": "references"})

    plan = {
        "title": title,
        "subtitle": None,
        "authors": authors,
        "year": year,
        "slides": slides,
        "bundles": [bundle],
    }
    return plan


def plan_multi_paper(bundles: list[dict], target_slides: int, include_notes: bool,
                     structure: str) -> dict:
    """Construct a slide plan for multi-paper talks."""
    titles = " / ".join(b.get("title") or b["paper_slug"] for b in bundles)
    slides: list[dict] = [
        {"kind": "title", "content": None},
        {"kind": "outline", "content": None},
        {"kind": "section_header", "title": "Motivation"},
        {"kind": "content", "section": "Motivation",
         "title": "[TODO unifying motivation]",
         "bullets": ["[TODO the shared research thread]"],
         "figure": None,
         "notes": "[TODO]" if include_notes else None},
    ]

    if structure == "one-per-paper":
        per_paper_budget = max(4, (target_slides - 6) // len(bundles))
        for b in bundles:
            sec_name = b.get("title") or b["paper_slug"]
            slides.append({"kind": "section_header", "title": _shorten(sec_name, 30)})
            slides.extend(_paper_mini_section(b, per_paper_budget, include_notes))
        slides.append({"kind": "section_header", "title": "Comparison"})
        slides.append({
            "kind": "content", "section": "Comparison",
            "title": "[TODO what they agree on]",
            "bullets": ["[TODO]"],
            "figure": None,
            "notes": "[TODO]" if include_notes else None,
        })
    else:  # integrated
        slides.append({"kind": "section_header", "title": "Themes"})
        slides.append({
            "kind": "content", "section": "Themes",
            "title": "[TODO theme 1]",
            "bullets": ["[TODO evidence pulled from multiple papers]"],
            "figure": None,
            "notes": "[TODO]" if include_notes else None,
        })

    slides.append({
        "kind": "content",
        "section": "Acknowledgments",
        "title": "Acknowledgments",
        "bullets": ["[TODO]"],
        "figure": None,
        "notes": None,
    })
    slides.append({"kind": "references"})

    return {
        "title": titles,
        "subtitle": None,
        "authors": _merge_authors(bundles),
        "year": None,
        "slides": slides,
        "bundles": bundles,
    }


def _paper_mini_section(bundle: dict, budget: int, include_notes: bool) -> list[dict]:
    """Small section per paper in multi-paper mode."""
    sec = _shorten(bundle.get("title") or bundle["paper_slug"], 30)
    out: list[dict] = [
        {"kind": "content", "section": sec,
         "title": "[TODO setup / question]",
         "bullets": ["[TODO]"],
         "figure": None,
         "notes": "[TODO]" if include_notes else None},
    ]
    fig_files = bundle.get("figures", {}).get("files", [])
    for fig in fig_files[: max(1, budget - 2)]:
        out.append({
            "kind": "figure", "section": sec,
            "title": "[TODO figure caption]",
            "figure": f"figures/{bundle['paper_slug']}_{fig}",
            "caption": "[TODO]",
            "notes": "[TODO]" if include_notes else None,
        })
    return out


def _slide_budget(target: int) -> dict:
    """Proportional budget for a single-paper talk targeting N slides."""
    # Reserve: title(1) + outline(1) + section headers(5) + acks(1) + refs(1) = 9
    content_budget = max(6, target - 9)
    # Allocate proportionally
    return {
        "motivation": max(1, content_budget * 2 // 15),
        "background": max(1, content_budget * 2 // 15),
        "methods": max(1, content_budget * 3 // 15),
        "results": max(3, content_budget * 6 // 15),
        "discussion": max(1, content_budget * 2 // 15),
    }


def _shorten(s: str, max_chars: int) -> str:
    s = s.strip()
    if len(s) <= max_chars:
        return s
    return s[: max_chars - 1] + "…"


def _merge_authors(bundles: list[dict]) -> list[str]:
    seen: set[str] = set()
    merged: list[str] = []
    for b in bundles:
        for a in (b.get("authors") or []):
            if a not in seen:
                seen.add(a)
                merged.append(a)
    return merged


# ---------------------------------------------------------------------------
# Asset assembly (figures + bib)
# ---------------------------------------------------------------------------

def assemble_assets(plan: dict, output_dir: Path) -> None:
    """Copy figures + merge bib files into the output directory."""
    fig_out = output_dir / "figures"
    fig_out.mkdir(parents=True, exist_ok=True)

    merged_bib: list[str] = []
    seen_keys: set[str] = set()

    for bundle in plan["bundles"]:
        bundle_path = Path(bundle["_bundle_path"])
        bundle_figs = bundle_path / "figures"
        if bundle_figs.is_dir():
            # In multi-paper mode we prefix figure filenames with the slug
            multi = len(plan["bundles"]) > 1
            for f in bundle_figs.iterdir():
                if not f.is_file():
                    continue
                dest_name = f"{bundle['paper_slug']}_{f.name}" if multi else f.name
                shutil.copy2(f, fig_out / dest_name)
        bib_path = bundle_path / "references.bib"
        if bib_path.exists():
            entries = _split_bib_entries(bib_path.read_text(errors="replace"))
            for key, entry_text in entries:
                if key not in seen_keys:
                    seen_keys.add(key)
                    merged_bib.append(entry_text)

    (output_dir / "references.bib").write_text("\n\n".join(merged_bib) + "\n")


def _split_bib_entries(bib_text: str) -> list[tuple[str, str]]:
    """Naive bibtex splitter. Returns [(citekey, full_entry_text), ...]."""
    entries: list[tuple[str, str]] = []
    # Match @type{key, ... } handling nested braces with a depth counter
    i = 0
    while i < len(bib_text):
        if bib_text[i] != "@":
            i += 1
            continue
        start = i
        # Find opening brace
        brace_start = bib_text.find("{", i)
        if brace_start == -1:
            break
        # Extract key (up to comma)
        comma = bib_text.find(",", brace_start)
        if comma == -1:
            break
        key = bib_text[brace_start + 1:comma].strip()
        # Walk braces to find matching close
        depth = 1
        j = brace_start + 1
        while j < len(bib_text) and depth > 0:
            if bib_text[j] == "{":
                depth += 1
            elif bib_text[j] == "}":
                depth -= 1
            j += 1
        if depth != 0:
            # Malformed; bail
            break
        entries.append((key, bib_text[start:j]))
        i = j
    return entries


# ---------------------------------------------------------------------------
# Beamer emission
# ---------------------------------------------------------------------------

def emit_beamer(plan: dict, output_dir: Path) -> Path:
    """Write deck.tex from plan into output_dir. Returns the .tex path."""
    template = TEMPLATE_PATH.read_text()

    short_title = _shorten(plan["title"], 30)
    authors_short = _format_authors(plan["authors"], short=True)
    authors_long = _format_authors(plan["authors"], short=False)

    subs = {
        "<<TITLE>>": _latex_escape(plan["title"]),
        "<<SUBTITLE>>": _latex_escape(plan.get("subtitle") or ""),
        "<<AUTHOR>>": _latex_escape(authors_long or "[TODO author]"),
        "<<DATE>>": r"\today",
        "<<SHORT_TITLE>>": _latex_escape(short_title),
    }
    for k, v in subs.items():
        template = template.replace(k, v)
    # Patch the \author[]{} short form (post-substitution the short and long
    # forms are identical; we want [short]{long})
    template = template.replace(
        f"\\author[{_latex_escape(authors_long or '[TODO author]')}]",
        f"\\author[{_latex_escape(authors_short or 'TODO')}]",
    )

    # Replace the ENTIRE document body (between \begin{document} and
    # \end{document}) with our generated slides. The template ships with
    # placeholder frames (title, outline, sample sections, acks, refs) —
    # those are illustrative only and get thrown out here.
    doc_start = template.find(r"\begin{document}")
    doc_end = template.find(r"\end{document}")
    if doc_start == -1 or doc_end == -1:
        raise RuntimeError(
            "Template missing \\begin{document} or \\end{document} markers"
        )
    doc_start += len(r"\begin{document}")

    generated_body = (
        "\n\n"
        "% ============================================================================\n"
        "% Slides below generated by scripts/plan_deck.py\n"
        "% ============================================================================\n\n"
        + _render_slides(plan["slides"])
        + "\n"
    )
    template = template[:doc_start] + generated_body + template[doc_end:]

    tex_path = output_dir / "deck.tex"
    tex_path.write_text(template)
    return tex_path


def _render_slides(slides: list[dict]) -> str:
    parts: list[str] = []
    for s in slides:
        k = s["kind"]
        if k == "title":
            parts.append(_tex_title_slide())
        elif k == "outline":
            parts.append(_tex_outline())
        elif k == "section_header":
            parts.append(f"\\section{{{_latex_escape(s['title'])}}}\n")
        elif k == "content":
            parts.append(_tex_content(s))
        elif k == "figure":
            parts.append(_tex_figure(s))
        elif k == "references":
            parts.append(_tex_references())
        else:
            parts.append(f"% unsupported slide kind: {k}\n")
    return "\n".join(parts)


def _tex_title_slide() -> str:
    return "\\begin{frame}[plain]\n  \\titlepage\n\\end{frame}\n"


def _tex_outline() -> str:
    return "\\begin{frame}{Outline}\n  \\tableofcontents\n\\end{frame}\n"


def _tex_content(s: dict) -> str:
    bullets = s.get("bullets") or []
    # Brace-wrap each bullet's body. Without this, a bullet starting with `[`
    # (e.g. "[TODO]") is parsed by LaTeX as the optional label argument to
    # \item, eating part of the content. The braces start a new group so the
    # `[` can't be misread.
    bullet_tex = "\n".join(f"    \\item {{{_latex_escape(b)}}}" for b in bullets)
    note = s.get("notes")
    note_tex = f"  \\note{{{_latex_escape(note)}}}\n" if note else ""
    return (
        f"\\begin{{frame}}{{{_latex_escape(s['title'])}}}\n"
        f"  \\begin{{itemize}}\n{bullet_tex}\n  \\end{{itemize}}\n"
        f"{note_tex}"
        f"\\end{{frame}}\n"
    )


def _tex_figure(s: dict) -> str:
    fig = s.get("figure")
    caption = s.get("caption") or ""
    note = s.get("notes")
    note_tex = f"  \\note{{{_latex_escape(note)}}}\n" if note else ""
    cap_tex = f"\\\\[0.5em]\\footnotesize {_latex_escape(caption)}" if caption else ""
    return (
        f"\\begin{{frame}}{{{_latex_escape(s['title'])}}}\n"
        f"  \\centering\n"
        f"  \\includegraphics[width=0.85\\textwidth,height=0.75\\textheight,keepaspectratio]{{{fig}}}\n"
        f"  {cap_tex}\n"
        f"{note_tex}"
        f"\\end{{frame}}\n"
    )


def _tex_references() -> str:
    return (
        "\\begin{frame}[allowframebreaks]{References}\n"
        "  \\bibliographystyle{apalike}\n"
        "  \\bibliography{references}\n"
        "\\end{frame}\n"
    )


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
    # Do backslash first so later replacements don't get double-escaped
    for a, b in replacements:
        s = s.replace(a, b)
    return s


def _format_authors(authors: list[str], short: bool = False) -> str:
    if not authors:
        return ""
    if short:
        # Short form: first-author + "et al." if >1
        if len(authors) == 1:
            return authors[0]
        return f"{authors[0]} et al."
    return ", ".join(authors)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("bundles", type=Path, nargs="+",
                    help="Paths to paper bundle directories")
    ap.add_argument("--output-dir", type=Path, required=True)
    ap.add_argument("--title", help="Override deck title")
    ap.add_argument("--subtitle", default=None)
    ap.add_argument("--author", action="append",
                    help="Override author list; pass multiple times for multiple authors")
    ap.add_argument("--audience", choices=["expert", "grad", "lecture"], default="expert")
    ap.add_argument("--target-slides", type=int, default=25)
    ap.add_argument("--structure", choices=["one-per-paper", "integrated"],
                    default="one-per-paper")
    ap.add_argument("--notes", dest="notes", action="store_true", default=True)
    ap.add_argument("--no-notes", dest="notes", action="store_false")
    ap.add_argument("--plan-only", action="store_true",
                    help="Write just plan.json, don't emit .tex")
    args = ap.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)

    bundles = [load_bundle(b) for b in args.bundles]

    if len(bundles) == 1:
        plan = plan_single_paper(bundles[0], args.target_slides, args.notes)
    else:
        plan = plan_multi_paper(bundles, args.target_slides, args.notes, args.structure)

    if args.title:
        plan["title"] = args.title
    if args.subtitle:
        plan["subtitle"] = args.subtitle
    if args.author:
        plan["authors"] = args.author

    # Write plan.json first (serializable view of the plan)
    plan_for_json = {k: v for k, v in plan.items() if k != "bundles"}
    plan_for_json["bundle_paths"] = [b["_bundle_path"] for b in plan["bundles"]]
    (args.output_dir / "plan.json").write_text(json.dumps(plan_for_json, indent=2))

    if args.plan_only:
        print(f"Plan: {args.output_dir / 'plan.json'}")
        return 0

    assemble_assets(plan, args.output_dir)
    tex_path = emit_beamer(plan, args.output_dir)
    print(f"Deck: {tex_path}")
    print(f"Plan: {args.output_dir / 'plan.json'}")
    print(f"Next: python compile_beamer.py {tex_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
