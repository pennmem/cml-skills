# beamerposter patterns

LaTeX patterns specific to beamerposter that differ from standard beamer. Read in conjunction with `beamer-from-papers/references/beamer_generation.md` for the shared patterns (color theme, figure inclusion, bib handling).

## Document class + package

beamerposter extends beamer; the document class is still `beamer`:

```latex
\documentclass[final]{beamer}
\usepackage[orientation=landscape,size=custom,width=121.9,height=91.4,scale=1.2]{beamerposter}
```

The `final` class option disables beamer's overlay/animation machinery. You don't need `\pause`, `\only`, etc. on a poster — they just compile to static output anyway, but `final` makes the intent explicit.

## Single-frame structure

A beamerposter has exactly one frame. Everything goes inside it:

```latex
\begin{document}
\begin{frame}[t]{}  % [t] aligns to top; empty {} = no frame title
  \begin{columns}[T]
    % column definitions
  \end{columns}
\end{frame}
\end{document}
```

No `\section{}`, no `\tableofcontents`, no title slide — a poster IS the title slide plus content.

## Title header

The title area is **not** produced by `\titlepage`. Instead, build it as content at the top of the frame, before `\begin{columns}`:

```latex
\begin{frame}[t]{}
  % Title header as a full-width block
  \begin{center}
    \vspace{-1em}
    {\Huge\bfseries\color{cmlblue} Title of the Poster Goes Here} \\[0.5em]
    {\LARGE First Author$^1$, Second Author$^1$, Third Author$^2$} \\[0.3em]
    {\large $^1$University of Pennsylvania \quad $^2$Other Institution} \\
  \end{center}
  \vspace{1em}

  \begin{columns}[T]
    % ...
```

Or, if you want the navy-blue banner look matching the Beamer title slide, wrap it in a colored box:

```latex
\begin{tcolorbox}[colback=cmlblue,colframe=cmlblue,arc=0pt,boxsep=10pt]
  \begin{center}
    {\Huge\bfseries\color{white} Title Here} \\[0.5em]
    {\LARGE\color{white} Authors} \\[0.3em]
    {\large\color{white} Affiliations}
  \end{center}
\end{tcolorbox}
```

(Requires `\usepackage{tcolorbox}`.)

## Columns

beamerposter uses beamer's standard columns with the `[T]` top-alignment flag so columns don't shift when blocks have different heights:

```latex
\begin{columns}[T]
  \begin{column}{0.32\textwidth}
    % Blocks for column 1
  \end{column}
  \begin{column}{0.32\textwidth}
    % Blocks for column 2
  \end{column}
  \begin{column}{0.32\textwidth}
    % Blocks for column 3
  \end{column}
\end{columns}
```

Use `0.32\textwidth` rather than `0.33\textwidth` for 3 columns — this leaves 4% of the width as inter-column gutter, which is about right.

For 2 columns, use `0.48\textwidth`. For 4 columns, `0.23\textwidth`.

## Blocks

Each content area is a `block`:

```latex
\begin{block}{Motivation}
  Block content goes here. Can include paragraphs, lists, figures,
  equations — anything beamer can do.

  \begin{itemize}
    \item Bullet point one
    \item Bullet point two
  \end{itemize}
\end{block}
\vspace{0.5em}  % gap before next block
```

Block title styling is inherited from the beamer color theme. The CML navy palette makes block titles render as white-on-navy strips.

### Figure inside a block

```latex
\begin{block}{Key result: contiguity effect}
  \begin{center}
    \includegraphics[width=0.95\textwidth]{figures/fig2.pdf}
  \end{center}
  \vspace{0.3em}
  {\small Panel A shows lag-CRP curves for 129 participants across three
  list-length conditions. Forward transitions (lag $+1$) occur twice as
  often as backward (lag $-1$), consistent across list lengths.}
\end{block}
```

Use `width=0.95\textwidth` (not `\textwidth`) to leave a small margin so the figure doesn't crash against the block's border.

The `{\small ...}` after the figure gives a caption in smaller type. Don't use `\caption{}` — that's for `figure` environments, which beamerposter treats oddly.

### Block with two side-by-side figures

```latex
\begin{block}{Results}
  \begin{columns}[T]
    \begin{column}{0.48\columnwidth}
      \includegraphics[width=\textwidth]{figures/fig3a.pdf}
    \end{column}
    \begin{column}{0.48\columnwidth}
      \includegraphics[width=\textwidth]{figures/fig3b.pdf}
    \end{column}
  \end{columns}
\end{block}
```

Note `\columnwidth` inside a nested column, not `\textwidth`.

## References in compact footer

Don't use `\bibliography` on a poster — it produces full-format references that eat space. Hand-format them in compact numbered style inside a block.

**Important**: Don't use `\\` to separate numbered references. A line like `[1] Author (2002)... \\` followed by `[2] Author (2009)...` causes LaTeX to parse `\\` followed by `[2]` as `\\[2]` — a line break of length `2` with no unit, which fires a fatal-looking "Illegal unit of measure" warning (though the PDF still compiles). Use `\par` instead, and prefix the bracket with an empty `{}` group for belt-and-suspenders:

```latex
\begin{block}{References}
  {\scriptsize
    \textbf{References:}\par
    {}[1] Howard, M.W. \& Kahana, M.J. (2002). \textit{J Math Psych}, 46, 269--299.\par
    {}[2] Polyn, S.M. et al. (2009). \textit{Psych Rev}, 116, 129--156.\par
    {}[3] Lohnas, L.J. et al. (2015). \textit{Psych Rev}, 122, 337--363.\par
    {}[4] Cohen, N. \& Kahana, M.J. (2019). \textit{Psych Rev}, 129, 742--776.
  }
\end{block}
```

In the poster body, cite as superscripts: `memory is driven by context\cite{howard2002}` → rendered as "memory is driven by context$^1$". To get superscript citation numbers with natbib:

```latex
\usepackage[numbers,super,sort&compress]{natbib}
```

## Acknowledgments

Same block style, terse:

```latex
\begin{block}{Acknowledgments}
  {\small
    This work was supported by NIH grant MH-055687 and NSF BCS-1354938.
    We thank the Penn Computational Memory Lab for helpful discussion.
    Correspondence: \texttt{author@psych.upenn.edu}
  }
\end{block}
```

## QR code

If the user wants a QR code linking to the paper:

```latex
\usepackage{qrcode}

% In the references block:
\begin{minipage}{0.3\textwidth}
  \qrcode[height=3cm]{https://doi.org/10.1037/rev0000348}
\end{minipage}
\begin{minipage}{0.65\textwidth}
  {\small Scan for full paper DOI}
\end{minipage}
```

## Common pitfalls

**Text overflow**: if a block's content exceeds its height, it silently gets cut off (beamer doesn't show overflow warnings the way pdflatex does for regular frames). Compile, look at the PDF, trim content until everything fits. The planner should budget text aggressively.

**Figure that's too small**: figures from papers are often sized for a journal column (~3.5 inches wide). On a poster they need to be bigger. Use `width=\textwidth` inside the block; if that's still too small, the figure itself needs to be regenerated from the original source at higher resolution.

**Figures with white text on transparent background**: these become invisible on the cmlblue title bar if placed there. Check figures in a preview before committing. If a figure has transparency issues, convert to a flat PNG first.

**Too many columns for the size**: 4 columns on a 36×48 portrait is too many — each column ends up ~22cm wide, which can't fit readable text at 22pt. Stick to the recommendations in `poster_design.md`.

**Pixelated figures at print size**: a 300dpi print of a 48×36 poster is 14400×10800 pixels. A figure that's 800×600 in the paper will be stretched and pixelated on the poster. For the "money" figure, ask the paper's first author for a higher-res version or regenerate from the plotting code.
