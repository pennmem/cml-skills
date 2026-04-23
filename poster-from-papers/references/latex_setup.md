# LaTeX setup for posters

Beyond the base `pdflatex` + `bibtex` requirements (covered in `beamer-from-papers/references/latex_setup.md`), posters need:

## Required packages

- `beamerposter` — the package itself. Included in `texlive-pictures` on Debian/Ubuntu.
- `beamer` — baseline (included via `texlive-latex-extra`).
- `tcolorbox` — optional; used if the template's title header uses the colored-box banner style.
- `qrcode` — optional; used if the poster includes a QR code linking to the paper.

All of these are in standard TeX Live installations. `texlive-full` is overkill but guarantees everything is present.

## Verify beamerposter is available

```bash
kpsewhich beamerposter.sty
```

Should return a path. If it returns nothing:

```bash
# Debian / Ubuntu
sudo apt-get install texlive-pictures
# macOS (MacTeX ships it already)
# Windows — use MiKTeX's package manager to install beamerposter
```

## Compile command differences from beamer

The compile flow is simpler than a regular beamer deck because:

- No table of contents (no extra pass needed for TOC resolution)
- Usually no bibtex (poster references are hand-formatted; see `beamerposter_patterns.md`)

Typical compile:

```bash
pdflatex -interaction=nonstopmode poster.tex
pdflatex -interaction=nonstopmode poster.tex  # second pass for cross-refs
```

`scripts/compile_poster.py` handles this and adds bibtex passes only when the `.aux` file shows a `\bibdata` entry.

## Common errors specific to posters

### `Overfull \hbox ... too wide` warnings

These are usually safe on a poster — they indicate a block's content extended beyond its column. But check the output PDF: if the overflow is visible (text cut off at the column edge), trim content.

### `beamerposter does not know size 'foo'`

The `size=` parameter must be either a named preset (`a0`, `a1`, `a2`) or `size=custom,width=...,height=...`. Typo in the size → fall back to custom with explicit dimensions.

### Figure renders tiny despite `width=\textwidth`

beamerposter's `\textwidth` inside a column is the column's width, not the poster's full width. So `width=\textwidth` inside a column 32% of the poster wide will be only 32% of the poster wide. This is correct behavior — but it means a figure that's huge on a slide will be modest on a poster. If the figure needs to span columns, pull it out of the column structure and make it a full-width block:

```latex
% Full-width figure spanning all columns
\end{columns}  % close the column structure
\begin{center}
  \includegraphics[width=0.9\textwidth]{figures/big_figure.pdf}
\end{center}
\begin{columns}[T]  % reopen
  % ... subsequent blocks ...
\end{columns}
```

### Compile is slow (> 30 seconds)

A complex poster with many embedded high-res PDF figures can take 30–60 seconds per pass. This is normal — pdflatex has to parse and embed every figure. If it's much slower than that, check for:

- PDF figures with transparency (re-save as flat)
- Very large raster images (reduce to 300dpi before embedding)
- `\usepackage{pgf}` / tikz rendering many drawn elements (precompile to external PDFs)

### Ghostscript compression

After compile, if the PDF exceeds 25–30 MB, compress with:

```bash
gs -dNOPAUSE -dBATCH -sDEVICE=pdfwrite -dPDFSETTINGS=/prepress \
   -sOutputFile=poster_compressed.pdf poster.pdf
```

`/prepress` preserves print quality; `/printer` is smaller but lower quality; `/ebook` is much smaller but NOT suitable for print.

The compile script applies `/prepress` automatically when the output exceeds 30 MB.
