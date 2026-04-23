# Poster design

Physical and visual constraints that beamer-from-papers doesn't face.

## Standard sizes

| Name | Dimensions (inches) | Dimensions (cm) | When to use |
|---|---|---|---|
| `48x36-landscape` | 48 × 36 | 121.9 × 91.4 | US conference default (SfN, CNS, Psychonomics) |
| `36x48-portrait` | 36 × 48 | 91.4 × 121.9 | Portrait variant when booth space is narrow |
| `A0-portrait` | 33.1 × 46.8 | 84.1 × 118.9 | European conferences (CogSci, ESCOP) |
| `A0-landscape` | 46.8 × 33.1 | 118.9 × 84.1 | European landscape variant |
| `42x42` | 42 × 42 | 106.7 × 106.7 | Square, less common; some labs prefer |
| `custom` | user-specified | — | When the venue has unusual requirements |

**Always verify with the conference.** SfN recently allowed 48×36 or 42×60; CNS tends to enforce 36×48 portrait strictly. Posting the wrong size means reprinting.

## Beamerposter invocation

For 48×36 landscape:
```latex
\usepackage[orientation=landscape,size=custom,width=121.9,height=91.4,scale=1.2]{beamerposter}
```

For 36×48 portrait:
```latex
\usepackage[orientation=portrait,size=custom,width=91.4,height=121.9,scale=1.2]{beamerposter}
```

For A0 portrait:
```latex
\usepackage[orientation=portrait,size=a0,scale=1.2]{beamerposter}
```

The `scale` parameter adjusts relative font sizes. `scale=1.2` is a good starting point for 48×36; increase to 1.3–1.4 for A0 which is larger.

## Font sizing

At the `scale=1.2` default for a 48×36 poster, beamerposter's relative sizes work out to approximately:

| Element | Font size | Visible at |
|---|---|---|
| Title | ~72pt | 15+ feet |
| Authors / affiliations | ~32pt | 8 feet |
| Block headings | ~36pt | 10 feet |
| Body text | ~22pt | 4–5 feet |
| Figure captions | ~18pt | 3 feet |
| References | ~14pt | 2 feet (viewers will approach) |

**Readability test**: print a page of the poster at 25% size (so 48×36 → 12×9 inches). If body text is readable at arm's length on the 12×9, it's readable at 4–5 feet on the full size. If not, bump up the scale.

Avoid dropping body text below ~20pt at standard scale. It just won't be read.

## Color scheme

Use the CML navy blue from beamer-from-papers:
```latex
\definecolor{cmlblue}{RGB}{28, 53, 115}
```

Typical application to a poster:

- **Title bar**: cmlblue background, white text
- **Block title bars**: cmlblue background, white text (smaller than title bar)
- **Block body**: white background, dark text (not pure black — slightly softer for long reading)
- **Figures**: whatever color the paper's original figures use (don't recolor to match theme)
- **Conclusion bullets**: cmlblue bullet markers on white background

The `Madrid` beamer theme's palette cascades work for posters too if you set the `structure` and `palette primary/secondary/tertiary` colors (see the template).

## Whitespace and block spacing

Posters are read in snatches. Generous whitespace between blocks helps viewers find their place when their eye jumps around. Rough rule:

- 1.5–2 cm gap between columns
- 1 cm gap between blocks within a column
- 0.5 cm inside each block between heading and content

Beamerposter's default block spacing is a bit tight for this purpose. Override with `\setlength{\parskip}{0.5em}` inside blocks.

## Readability conventions

- **Serif body text** (Latin Modern, Times) — easier to read in long blocks than sans-serif.
- **Sans-serif headings** (Helvetica, Arial, or Latin Modern Sans) — higher contrast at large sizes.
- **Left-align body text**, don't justify. Justified text on posters produces uneven word spacing that's hard to read at distance.
- **Line length 40–60 characters** per line. Column widths should be chosen to hit this.
- **Avoid full-width multi-line text** — if a block spans two columns, that's too wide to read comfortably.

## Column count and assignment

| Poster size | Recommended columns |
|---|---|
| 48×36 landscape | 3 |
| 36×48 portrait | 2 |
| 42×42 | 3 |
| A0 portrait | 2 or 3 (3 is tighter) |
| A0 landscape | 3 or 4 |

For 3-column 48×36 landscape, the standard assignment:

- Column 1 (left): Motivation + Methods
- Column 2 (middle): Results (first 2 figures)
- Column 3 (right): Results (last 1–2 figures) + Conclusions + References

For 2-column portrait:

- Column 1 (left): Motivation + Methods + first results block
- Column 2 (right): Remaining results + Conclusions + References

These are starting points — adjust based on figure sizes and block weights.

## Title bar

Full-width strip across the top. Contains:

- **Title** — large, centered, often 2 lines
- **Authors** — smaller, below title, full names or First-Initial Last format. Superscript numbers link to affiliations.
- **Affiliations** — smallest, below authors. "1University of Pennsylvania, 2MIT"
- **Lab logo** — often bottom-left or bottom-right of the title bar. The CML has a Penn shield + lab wordmark; if the user has it on hand, they should drop the file next to the .tex and reference it.

Total title bar height: ~12–15% of total poster height. Don't let it balloon beyond that or it steals from content.

## QR codes

Increasingly common. Place in the references/acknowledgments footer, link to:

- Preprint DOI
- Full paper DOI (after publication)
- GitHub repo for code/data
- Lab page

Generate via `qrcode` package in LaTeX, or produce a PNG externally and `\includegraphics` it in.

## Print and file size

Conference print shops accept PDF at 300dpi for the final output. beamerposter's default should produce this without intervention.

**File size**: posters with many embedded high-res figures can reach 50–100 MB. Acceptable but slow to upload. The compile script uses Ghostscript's `/prepress` setting to trim file size without quality loss:

```bash
gs -dNOPAUSE -dBATCH -sDEVICE=pdfwrite -dPDFSETTINGS=/prepress \
   -sOutputFile=poster_compressed.pdf poster.pdf
```

Run this after the main compile if the output is over 25 MB. Typical compression: 50–80%.
