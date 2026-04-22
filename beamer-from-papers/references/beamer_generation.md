# Beamer generation

How to turn a slide plan (see `presentation_structure.md`) into a working `.tex` file that compiles with `assets/cml_beamer_template.tex`.

## Workflow

1. Start from a copy of `assets/cml_beamer_template.tex`.
2. Fill in the metadata placeholders (`<<TITLE>>`, `<<AUTHOR>>`, etc.).
3. Strip the placeholder sections (everything between `% Sections begin here.` and `% --- Acknowledgments ---`).
4. Walk the slide plan and emit one LaTeX block per slide.
5. Write the final `.tex` alongside `references.bib` and a `figures/` subdirectory populated from the paper bundle(s).
6. Run `scripts/compile_beamer.py`.

## Per-slide LaTeX patterns

### Title slide
```latex
\begin{frame}[plain]
  \titlepage
\end{frame}
```

### Outline
```latex
\begin{frame}{Outline}
  \tableofcontents
\end{frame}
```

### Section header (auto-generated divider on Madrid)
```latex
\section{Motivation}
```
No `\begin{frame}` needed — Madrid auto-renders a section divider frame when a section is declared outside any frame. If a more visible divider is wanted:
```latex
\section{Motivation}
\begin{frame}[plain]
  \begin{center}
    {\Huge \color{cmlblue} Motivation}
  \end{center}
\end{frame}
```

### Content with bullets
```latex
\begin{frame}{Why this matters}
  \begin{itemize}
    \item First point
    \item Second point with a \cite{kahana1996} inline citation
    \item Third point
  \end{itemize}
  \note{Set the stakes. 45 seconds.}
\end{frame}
```

### Figure-dominant slide
```latex
\begin{frame}{Serial position effects}
  \centering
  \includegraphics[width=0.85\textwidth]{figures/fig2_spc.pdf}
  \note{Classic U-shape. Walk primacy then recency.}
\end{frame}
```

### Two-column (text + figure side-by-side)
```latex
\begin{frame}{Headline result}
  \begin{columns}
    \column{0.6\textwidth}
      \includegraphics[width=\textwidth]{figures/fig_main.pdf}
    \column{0.4\textwidth}
      \begin{itemize}
        \item What the figure shows
        \item Why it matters
      \end{itemize}
  \end{columns}
  \note{Don't talk to the bullets — talk to the figure.}
\end{frame}
```

### Equation slide
```latex
\begin{frame}{Retrieved Context Theory}
  Context evolves with each item:
  \begin{equation}
    \mathbf{c}_i = \rho_i \mathbf{c}_{i-1} + \beta_{enc} M^{FC} \mathbf{f}_i
  \end{equation}
  And context is updated by retrieved items at recall:
  \begin{equation}
    \mathbf{f}^{IN}_r = M^{CF} \mathbf{c}_r
  \end{equation}
  \note{Walk through each symbol. Emphasize the bidirectional associations.}
\end{frame}
```

### References (with `allowframebreaks` for overflow)
```latex
\begin{frame}[allowframebreaks]{References}
  \bibliographystyle{apalike}
  \bibliography{references}
\end{frame}
```

## Figure path conventions

Copy figure files from each bundle's `figures/` directory into a local `figures/` subdirectory alongside the `.tex`. Use relative paths:
```latex
\includegraphics[width=0.8\textwidth]{figures/fig1.pdf}
```

Don't use absolute paths — the talk .tex should be self-contained and portable.

## Handling name collisions across papers

When pulling figures from multiple bundles into one deck, prefix each figure with the paper slug to avoid collisions:

```
figures/
├── cohenkahana2019_fig1.pdf
├── cohenkahana2019_fig2.pdf
├── healeykahana2016_fig1.pdf
└── healeykahana2016_fig2.pdf
```

Update `\includegraphics` paths accordingly.

## Citation keys

When extracting `\cite{}` commands from the source paper, the cite keys reference the paper's original `.bib`. When building the deck, dedupe keys across all source bibs and write a unified `references.bib` in the deck directory.

If two source bibs use the same key for different entries, the deck builder should rename one with a suffix (`kahana1996b`) and update the citation in the corresponding paper's text.

## LaTeX escaping

Text pulled from paper sources may contain LaTeX-unsafe characters. Escape these in generated content (not in content the user supplies verbatim):

| Char | Replacement |
|---|---|
| `&` | `\&` |
| `%` | `\%` |
| `$` | `\$` |
| `#` | `\#` |
| `_` | `\_` |
| `{` / `}` | `\{` / `\}` |
| `~` | `\textasciitilde{}` |
| `^` | `\textasciicircum{}` |
| `\` | `\textbackslash{}` |

Be careful: if the source material is already LaTeX (e.g., a sentence lifted directly from `drafts/selected.tex`), don't re-escape.

## Section + frametitle style

Each section only needs one `\section{}` declaration — subsequent frames in that section inherit the section in the header dots. Don't redeclare.

Keep frame titles short (under 40 chars). Madrid truncates longer titles awkwardly.

## Common pitfalls

- **`\includegraphics` with a PDF that contains transparency**: pdflatex handles this fine; other engines may not. If a figure doesn't render, convert the PDF to PNG first.
- **Over-filled frames**: if content overflows, either split across two frames (`\begin{frame}[allowframebreaks]`), reduce content, or use `\scriptsize`/`\small`.
- **Unicode in figure captions**: LaTeX + inputenc utf8 handles Latin-1 range. For Greek/math, use LaTeX commands instead: `\alpha`, `\beta`, etc.
- **References not resolving**: the `\cite{key}` must match a `@article{key, ...}` entry in `references.bib`. Missing entries produce `[?]` in the output. `compile_beamer.py` surfaces these warnings.
