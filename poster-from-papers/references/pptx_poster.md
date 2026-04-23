# PPTX poster generation

The PPTX output path is a **parallel emitter**, not a converter. It reads the same `plan.json` that produces the Beamer `.tex` and writes a single-slide `.pptx` sized to the poster dimensions. No PDF-to-PPTX conversion is done — that approach produces ugly results.

## What the output looks like

A `.pptx` file with:

- One slide, sized to the poster dimensions (48×36, 36×48, A0, etc.)
- Title banner at the top (navy-blue rectangle, white title/authors/affiliation text)
- Columns of blocks, each with a colored header bar and light-background body
- Embedded figures in result blocks
- Conclusions as bulleted text
- References in compact type in the closing block

Visually matches the Beamer output so the two are interchangeable deliverables.

## Running it

```bash
python scripts/generate_pptx_poster.py <output-dir>/plan.json
```

Writes `<output-dir>/poster.pptx` alongside the plan. If you pass `--output <path>`, writes there instead.

## Figures: PDF → PNG rasterization

PowerPoint embeds raster images (PNG, JPG, TIFF, GIF). It cannot open PDF figures — python-pptx uses PIL, which doesn't read PDF. The script handles this by **automatically rasterizing any PDF figures to PNG** before embedding:

1. When the plan references `figures/fig1.pdf`, the script checks if `figures/fig1.png` already exists as a fresher sibling.
2. If not, it runs `pdftoppm -r 200 -png` to generate a 200dpi PNG.
3. If `pdftoppm` isn't installed, it falls back to `pdf2image` (a Python package wrapping poppler).
4. The PNG is cached next to the original PDF and reused on subsequent runs.

200dpi is appropriate for an embedded poster figure printed at ~8×6 inches. Higher DPI is possible via editing the script but bloats the `.pptx` file.

**Troubleshooting**:
- `pdftoppm` not found → `sudo apt-get install poppler-utils` (Linux) or `brew install poppler` (macOS). It's tiny and worth installing.
- Figures appear blank in PowerPoint → check that the source PDF actually has content (some PDFs are 1-pixel or empty). Test with `pdftoppm -r 72 -png figure.pdf test` and open `test-1.png`.

## Font sizes

Defined per poster-size preset in the script:

| Size | Title | Authors | Block heading | Body | References |
|---|---|---|---|---|---|
| 48×36 landscape | 72pt | 36pt | 32pt | 22pt | 14pt |
| 36×48 portrait | 60pt | 32pt | 28pt | 20pt | 13pt |
| A0 portrait | 58pt | 30pt | 28pt | 20pt | 13pt |
| A0 landscape | 68pt | 34pt | 30pt | 22pt | 14pt |

These are tuned to be readable at 4–6 feet when printed at the target dimensions. If you need different sizes, edit `SIZE_PRESETS` in `generate_pptx_poster.py`.

## Font family

The PPTX emitter uses **Helvetica** as the font family (same convention as the Beamer template's `\usepackage{helvet}`). If Helvetica isn't installed on the system that opens the `.pptx`, PowerPoint will substitute Arial or another sans-serif — same visual family, so this is rarely a problem.

## When to use PPTX vs Beamer

**Prefer Beamer when**:
- The paper has many equations (beamer renders LaTeX math natively; PPTX needs rasterized equation images)
- Figures are PDF-native and high-res
- You want the output to look like a CML Beamer deck
- You'll print directly from PDF

**Prefer PPTX when**:
- Collaborators need to edit the poster in PowerPoint
- The conference asks for a PPTX submission
- You'll share drafts with non-LaTeX users for feedback
- The poster will be animated or embedded in a digital display

You can always generate both from the same plan — they share the same data structure.

## Text-box sizing: a known limitation

python-pptx doesn't auto-size text boxes to fit content. The script estimates each block's height based on its content type (see `_estimate_body_height`), then scales if total column height exceeds the available space. If content is much longer than typical, a block can overflow off the bottom of its column — the PPTX won't catch this, and PowerPoint just cuts the text off at the text box edge.

**Mitigation**: after generating the `.pptx`, open it in PowerPoint and eyeball each block. Drag text-box edges as needed. Save. Done.

The Beamer output has the same issue (overfull hbox), but LaTeX at least warns about it. PPTX is silent. Treat the PPTX output as a first draft that needs a visual review pass.

## When `memory-publications` is installed

No direct integration with the PPTX emitter itself — but the upstream content that fills the plan (via the reading pass from `reading_strategy.md`) benefits the same way it does for Beamer. Voice, terminology, and content selection all flow through the plan.

The one PPTX-specific tweak: if the memory-publications writing style would produce paragraph-length motivation or conclusion bullets, those can overflow PPTX text boxes more easily than Beamer blocks. Keep motivation at ≤80 words and bullets at ≤20 words each when targeting PPTX.
