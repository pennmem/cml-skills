#!/usr/bin/env python3
"""Emit a native PowerPoint poster from a poster plan (single slide, poster-sized).

Usage:
    python generate_pptx_poster.py <plan.json> [--output poster.pptx]

Produces a single-slide .pptx sized to the poster dimensions specified
in the plan. Mirrors the Beamer output's structure: navy-blue title bar,
columns of blocks with title headers, figures embedded, references block
in compact type.

This is native emission via python-pptx — NOT a PDF-to-PPTX conversion.
Font sizes are scaled for the poster dimensions (title 72pt, block
headings 36pt, body 22pt for a 48x36 poster).
"""

import argparse
import json
import sys
from pathlib import Path

try:
    from pptx import Presentation
    from pptx.util import Inches, Pt, Emu
    from pptx.dml.color import RGBColor
    from pptx.enum.shapes import MSO_SHAPE
    from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
except ImportError:
    print(
        "ERROR: python-pptx not installed.\n"
        "Install with: pip install python-pptx --break-system-packages",
        file=sys.stderr,
    )
    sys.exit(1)


def _rasterize_pdf(pdf_path: Path, dpi: int = 200) -> Path | None:
    """Convert a single-page PDF figure to PNG so python-pptx can embed it.

    python-pptx uses PIL under the hood, which doesn't open PDFs. Returns
    the path to a generated PNG sibling, or None if rasterization fails.
    Uses pdftoppm if available; falls back to pdf2image if installed.
    """
    import shutil, subprocess
    png_path = pdf_path.with_suffix(".png")
    if png_path.exists() and png_path.stat().st_mtime > pdf_path.stat().st_mtime:
        return png_path  # cached
    if shutil.which("pdftoppm"):
        try:
            # pdftoppm writes to <root>-1.png for single-page PDFs
            root = pdf_path.with_suffix("")
            subprocess.run(
                ["pdftoppm", "-r", str(dpi), "-png", "-f", "1", "-l", "1",
                 str(pdf_path), str(root)],
                check=True, capture_output=True, timeout=60,
            )
            generated = pdf_path.parent / f"{pdf_path.stem}-1.png"
            if generated.exists():
                generated.rename(png_path)
                return png_path
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
            pass
    try:
        from pdf2image import convert_from_path
        images = convert_from_path(str(pdf_path), dpi=dpi, first_page=1, last_page=1)
        if images:
            images[0].save(str(png_path), "PNG")
            return png_path
    except Exception:
        pass
    return None


# CML navy blue matching the Beamer template: RGB(28, 53, 115)
CML_BLUE = RGBColor(0x1C, 0x35, 0x73)
CML_BLUE_LIGHT = RGBColor(0xE5, 0xE9, 0xF2)  # cmlblue!5 approximation
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
BLACK = RGBColor(0x00, 0x00, 0x00)


# Dimensions and font sizes per size preset
# All measurements in inches; font sizes in points
SIZE_PRESETS = {
    "48x36-landscape": {
        "width": 48.0, "height": 36.0,
        "title_font": 72, "author_font": 36, "affil_font": 22,
        "block_title_font": 32, "body_font": 22, "ref_font": 14,
        "title_height": 4.5,  # inches
    },
    "36x48-portrait": {
        "width": 36.0, "height": 48.0,
        "title_font": 60, "author_font": 32, "affil_font": 20,
        "block_title_font": 28, "body_font": 20, "ref_font": 13,
        "title_height": 4.0,
    },
    "A0-portrait": {
        "width": 33.1, "height": 46.8,
        "title_font": 58, "author_font": 30, "affil_font": 20,
        "block_title_font": 28, "body_font": 20, "ref_font": 13,
        "title_height": 3.8,
    },
    "A0-landscape": {
        "width": 46.8, "height": 33.1,
        "title_font": 68, "author_font": 34, "affil_font": 22,
        "block_title_font": 30, "body_font": 22, "ref_font": 14,
        "title_height": 4.2,
    },
    "42x42": {
        "width": 42.0, "height": 42.0,
        "title_font": 64, "author_font": 32, "affil_font": 20,
        "block_title_font": 30, "body_font": 22, "ref_font": 14,
        "title_height": 4.0,
    },
}


def _set_text(frame, text: str, font_size: int, color=BLACK,
              bold: bool = False, anchor=MSO_ANCHOR.TOP, align=PP_ALIGN.LEFT) -> None:
    """Populate a text frame with uniformly styled text."""
    frame.text = text
    frame.vertical_anchor = anchor
    frame.word_wrap = True
    for para in frame.paragraphs:
        para.alignment = align
        for run in para.runs:
            run.font.size = Pt(font_size)
            run.font.color.rgb = color
            run.font.bold = bold
            run.font.name = "Helvetica"


def _add_rect(slide, left: float, top: float, width: float, height: float,
              fill_color=CML_BLUE, line_color=None):
    """Add a filled rectangle to the slide. All dimensions in inches."""
    shape = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE,
        Inches(left), Inches(top), Inches(width), Inches(height),
    )
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill_color
    if line_color is None:
        shape.line.fill.background()
    else:
        shape.line.color.rgb = line_color
    shape.text_frame.word_wrap = True
    return shape


def _add_textbox(slide, left: float, top: float, width: float, height: float):
    """Add a transparent-background text box."""
    return slide.shapes.add_textbox(
        Inches(left), Inches(top), Inches(width), Inches(height),
    )


def render_title_bar(slide, plan: dict, preset: dict) -> float:
    """Draw the top title banner. Returns y-offset where content starts (inches)."""
    width = preset["width"]
    title_h = preset["title_height"]

    # Navy blue banner
    _add_rect(slide, 0.5, 0.5, width - 1.0, title_h, fill_color=CML_BLUE)

    # Title text
    title_box = _add_textbox(slide, 0.5, 0.7, width - 1.0, 2.0)
    _set_text(
        title_box.text_frame, plan["title"],
        font_size=preset["title_font"], color=WHITE, bold=True,
        anchor=MSO_ANCHOR.MIDDLE, align=PP_ALIGN.CENTER,
    )

    # Authors
    authors_text = ", ".join(plan["authors"]) if plan["authors"] else ""
    author_box = _add_textbox(slide, 0.5, 2.8, width - 1.0, 0.8)
    _set_text(
        author_box.text_frame, authors_text,
        font_size=preset["author_font"], color=WHITE,
        align=PP_ALIGN.CENTER,
    )

    # Affiliation (hardcoded Penn for now; could be templated later)
    affil_box = _add_textbox(slide, 0.5, 3.6, width - 1.0, 0.7)
    _set_text(
        affil_box.text_frame,
        "University of Pennsylvania \u2014 Computational Memory Lab",
        font_size=preset["affil_font"], color=WHITE,
        align=PP_ALIGN.CENTER,
    )

    return title_h + 1.0  # content starts below the banner + gap


def render_block(slide, block: dict, left: float, top: float,
                 width: float, max_height: float, preset: dict) -> float:
    """Draw a single content block. Returns the height it consumed."""
    # Header bar
    header_h = 0.9 if preset["width"] > 40 else 0.7
    _add_rect(slide, left, top, width, header_h, fill_color=CML_BLUE)
    header_box = _add_textbox(slide, left + 0.15, top + 0.1, width - 0.3, header_h - 0.2)
    _set_text(
        header_box.text_frame, block.get("title", ""),
        font_size=preset["block_title_font"], color=WHITE, bold=True,
    )

    # Body area — light background
    body_top = top + header_h
    body_h = _estimate_body_height(block, preset, width)
    # Constrain to available max
    body_h = min(body_h, max_height - header_h)
    _add_rect(slide, left, body_top, width, body_h, fill_color=CML_BLUE_LIGHT)

    content_pad = 0.25
    content_left = left + content_pad
    content_top = body_top + content_pad
    content_width = width - 2 * content_pad
    content_height = body_h - 2 * content_pad

    kind = block["kind"]
    if kind in ("motivation", "methods"):
        tb = _add_textbox(slide, content_left, content_top, content_width, content_height)
        _set_text(tb.text_frame, block.get("text", ""), preset["body_font"])
    elif kind == "question":
        tb = _add_textbox(slide, content_left, content_top, content_width, content_height)
        _set_text(
            tb.text_frame, block.get("text", ""),
            preset["body_font"], bold=True, align=PP_ALIGN.CENTER,
        )
    elif kind == "result":
        fig = block.get("figure")
        # Allocate most of the block to the figure, leave room for caption
        fig_h = content_height - 1.4
        fig_path = None
        if fig:
            # Resolve figure path — try as given, then relative to CWD
            candidate = Path(fig)
            if not candidate.exists():
                candidate = Path.cwd() / fig
            if candidate.exists():
                # python-pptx can't embed PDFs via PIL. Rasterize to PNG first.
                if candidate.suffix.lower() == ".pdf":
                    rasterized = _rasterize_pdf(candidate)
                    fig_path = rasterized if rasterized else None
                else:
                    fig_path = candidate
        if fig_path:
            try:
                slide.shapes.add_picture(
                    str(fig_path),
                    Inches(content_left + 0.1),
                    Inches(content_top),
                    width=Inches(content_width - 0.2),
                    height=Inches(fig_h),
                )
            except Exception as e:
                ph = _add_textbox(slide, content_left, content_top, content_width, fig_h)
                _set_text(ph.text_frame, f"[figure: {fig}]\n({e})", preset["body_font"])
        else:
            ph = _add_textbox(slide, content_left, content_top, content_width, fig_h)
            _set_text(ph.text_frame, f"[figure placeholder: {fig or 'none'}]",
                      preset["body_font"], align=PP_ALIGN.CENTER)
        # Caption below figure
        cap = _add_textbox(
            slide, content_left, content_top + fig_h + 0.2,
            content_width, 1.1,
        )
        _set_text(cap.text_frame, block.get("caption", ""), preset["body_font"] - 4)
    elif kind == "conclusions":
        bullets = block.get("bullets", [])
        tb = _add_textbox(slide, content_left, content_top, content_width, content_height)
        tf = tb.text_frame
        tf.word_wrap = True
        for i, bullet in enumerate(bullets):
            p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
            p.text = "\u2022 " + bullet
            p.alignment = PP_ALIGN.LEFT
            for run in p.runs:
                run.font.size = Pt(preset["body_font"])
                run.font.color.rgb = BLACK
                run.font.name = "Helvetica"
    elif kind == "references":
        tb = _add_textbox(slide, content_left, content_top, content_width, content_height)
        tf = tb.text_frame
        tf.word_wrap = True
        # References sub-heading
        p = tf.paragraphs[0]
        p.text = "References:"
        for run in p.runs:
            run.font.size = Pt(preset["ref_font"])
            run.font.bold = True
            run.font.color.rgb = BLACK
            run.font.name = "Helvetica"
        for i, r in enumerate(block.get("refs", []), start=1):
            p = tf.add_paragraph()
            p.text = f"[{i}] {r}"
            for run in p.runs:
                run.font.size = Pt(preset["ref_font"])
                run.font.color.rgb = BLACK
                run.font.name = "Helvetica"
        # Blank line then acknowledgments
        p = tf.add_paragraph()
        p.text = ""
        p = tf.add_paragraph()
        p.text = "Acknowledgments:"
        for run in p.runs:
            run.font.size = Pt(preset["ref_font"])
            run.font.bold = True
            run.font.color.rgb = BLACK
            run.font.name = "Helvetica"
        p = tf.add_paragraph()
        p.text = block.get("acknowledgments", "")
        for run in p.runs:
            run.font.size = Pt(preset["ref_font"])
            run.font.color.rgb = BLACK
            run.font.name = "Helvetica"

    return header_h + body_h


def _estimate_body_height(block: dict, preset: dict, width: float) -> float:
    """Rough estimate of how much height a block's body should get, in inches."""
    kind = block["kind"]
    if kind == "result":
        return 10.5  # big — figures are the main event
    if kind == "conclusions":
        n = len(block.get("bullets", []))
        return max(3.0, 0.8 * n + 0.8)
    if kind == "references":
        n = len(block.get("refs", []))
        return max(4.0, 0.5 * n + 2.5)
    if kind == "question":
        return 2.2
    if kind == "motivation":
        return 4.5
    if kind == "methods":
        return 4.0
    return 3.0


def generate_pptx_poster(plan_path: Path, output_path: Path) -> int:
    plan = json.loads(plan_path.read_text())
    size = plan.get("size", "48x36-landscape")
    if size not in SIZE_PRESETS:
        print(f"ERROR: unknown poster size {size}", file=sys.stderr)
        return 1
    preset = SIZE_PRESETS[size]

    prs = Presentation()
    prs.slide_width = Inches(preset["width"])
    prs.slide_height = Inches(preset["height"])
    slide_layout = prs.slide_layouts[6]  # blank
    slide = prs.slides.add_slide(slide_layout)

    # Title bar
    content_top = render_title_bar(slide, plan, preset)

    # Columns
    n_cols = plan.get("columns", 3)
    gutter = 0.8  # inches between columns
    usable_width = preset["width"] - 1.0  # 0.5 margin each side
    col_width = (usable_width - gutter * (n_cols - 1)) / n_cols

    # Group blocks by column
    by_col: dict[int, list[dict]] = {i: [] for i in range(1, n_cols + 1)}
    for b in plan["blocks"]:
        col = min(b.get("column", 1), n_cols)
        by_col[col].append(b)

    bottom_margin = 0.8  # don't render below this many inches from slide bottom
    max_block_height = preset["height"] - content_top - bottom_margin

    for col_num in range(1, n_cols + 1):
        left = 0.5 + (col_num - 1) * (col_width + gutter)
        current_top = content_top
        remaining = max_block_height
        blocks_in_col = by_col[col_num]
        # Distribute height budgets proportionally to estimates
        est = [_estimate_body_height(b, preset, col_width) + 0.9 for b in blocks_in_col]
        total_est = sum(est) if est else 1.0
        scale = min(1.0, remaining / total_est)
        for b, e in zip(blocks_in_col, est):
            block_h = e * scale
            consumed = render_block(
                slide, b, left, current_top, col_width, block_h, preset,
            )
            current_top += consumed + 0.3
            remaining = max(0, preset["height"] - bottom_margin - current_top)
            if remaining < 1.5:
                break  # don't start a block we can't finish

    prs.save(str(output_path))
    print(str(output_path))
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("plan_path", type=Path)
    ap.add_argument("--output", type=Path, default=None,
                    help="Output .pptx path (default: alongside plan.json)")
    args = ap.parse_args()

    if not args.plan_path.exists():
        print(f"ERROR: {args.plan_path} not found", file=sys.stderr)
        return 1

    output_path = args.output or args.plan_path.parent / "poster.pptx"
    return generate_pptx_poster(args.plan_path, output_path)


if __name__ == "__main__":
    sys.exit(main())
