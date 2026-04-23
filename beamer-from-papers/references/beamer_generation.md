# Beamer generation

How to turn a slide plan (see `presentation_structure.md`) into a working
`.tex` file that compiles with `assets/cml_beamer_template.tex`.

**Read this file together with `visual_design.md`**, which covers TikZ
patterns and recurring visual motifs. Use TikZ for data figures whenever
possible; use `\includegraphics` only for photos, schematics, and multi-panel
publication figures that can't be simplified without distorting the story.

## Workflow

1. Start from a copy of `assets/cml_beamer_template.tex`.
2. Fill in the metadata placeholders (`<<TITLE>>`, `<<AUTHOR>>`, etc.).
3. Strip the placeholder sections (everything between `% Sections begin here.`
   and `% --- Acknowledgments ---`).
4. Walk the slide plan and emit one LaTeX block per slide.
5. Write the final `.tex` alongside `references.bib` and a `figures/`
   subdirectory populated from the paper bundle(s).
6. Run `scripts/compile_beamer.py --render-preview N` to compile and
   render-verify changed slides.

## The three rules that govern every slide

1. **Visuals on the slide, content in `\note{}`.** Full sentences on slides
   mean you're using the wrong container — move the sentence to the note
   and leave a short phrase.
2. **Cut 30% more than instinct.** First-pass slides are always too dense.
3. **Render-verify after each batch.** `pdflatex` doesn't catch overflow
   clipping.

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

### Section header
With `metropolis` + `\metroset{sectionpage=none}` (the default), `\section{}`
just updates the progress bar without injecting a divider slide. If you want
an explicit divider for a long talk:

```latex
\section{Methods}
\begin{frame}[plain]
  \begin{center}
    {\Huge \color{cmlblue} Methods}
  \end{center}
\end{frame}
```

On Madrid, `\section{}` auto-renders a divider slide; suppress with
`\begin{frame}[noframenumbering,plain]{}\end{frame}` or leave enabled.

### Content slide — short bullets, long note

```latex
\begin{frame}{Why this matters}
  \begin{itemize}
    \item Phenomenon everyone recognizes
    \item Specific gap in existing accounts
    \item What this talk adds
  \end{itemize}
  \note{
    Full paragraph. See references/speaker_notes.md for length and voice.
  }
\end{frame}
```

Bullets are short phrases, not sentences. If a bullet needs a subclause, it's
two bullets or it belongs in the note.

### Figure-dominant slide (with summary bullets)

Every figure slide needs 2–3 summary bullets. Never ship a figure-only frame.

```latex
\begin{frame}{Serial position effects}
  \centering
  \includegraphics[width=0.82\textwidth, height=0.62\textheight,
                   keepaspectratio]{figures/fig2_spc.pdf}
  \vspace{2pt}
  \begin{itemize}
    \setlength\itemsep{2pt}
    \item U-shape: strong recency, weaker primacy
    \item Recency attenuates under filled delay; primacy does not
  \end{itemize}
  \note{Full paragraph. See references/speaker_notes.md.}
\end{frame}
```

The `width` + `height` + `keepaspectratio` combination guarantees the figure
never clips off the bottom of the frame. **Prefer TikZ for data figures**
(see `visual_design.md`); only use `\includegraphics` for photographs,
schematics, or publication figures that are already clean.

### Two-column (text + figure)

```latex
\begin{frame}{Headline result \novelbadge}
  \begin{columns}[T]
    \column{0.6\textwidth}
      \centering
      \includegraphics[width=\linewidth, height=0.72\textheight,
                       keepaspectratio]{figures/fig_main.pdf}
    \column{0.4\textwidth}
      \setstretch{0.95}
      \begin{itemize}
        \item What the figure shows
        \item Why it's surprising
      \end{itemize}
  \end{columns}
  \note{Talk to the figure, not the bullets. The bullets are there for the
        audience's eyes while you narrate. Full narrative in this note.}
\end{frame}
```

### Two figures, side-by-side (same type only)

```latex
\begin{frame}{Same vs.\ opposite valence errors}
  \begin{columns}[T]
    \column{0.48\textwidth}
      \centering
      \includegraphics[width=\linewidth, height=0.62\textheight,
                       keepaspectratio]{figures/same_valence.pdf}\\
      {\footnotesize Same-valence errors}
    \column{0.48\textwidth}
      \centering
      \includegraphics[width=\linewidth, height=0.62\textheight,
                       keepaspectratio]{figures/opp_valence.pdf}\\
      {\footnotesize Opposite-valence errors}
  \end{columns}
  \vspace{4pt}
  \begin{itemize}
    \setlength\itemsep{2pt}
    \item Same-valence transitions dominate across recall positions
    \item Effect magnitude predicted by emotional-context binding
  \end{itemize}
\end{frame}
```

If the two figures would differ in type (bar chart + line plot, schematic +
data plot, brain rendering + regression), put them on separate slides.

### Summary table + deep-dive pattern

For papers with many simulations or experiments, emit one summary table slide
before the result slides — then only 2–3 deep-dive slides on the
architecturally important results. Avoids the "simulation parade."

```latex
\begin{frame}{Results summary}
  \small
  \renewcommand{\arraystretch}{1.15}
  \begin{tabular}{lll}
    \textbf{Phenomenon}     & \textbf{Source}   & \textbf{Mechanism} \\
    \hline
    Emotional clustering    & Exp.~1, Sim.~1    & Pre-existing eCMR       \\
    Mood-congruent recall   & Sim.~2            & {\color{novelred}New: emo.\ ctx} \\
    Intrusive recollection  & Sim.~6            & {\color{novelred}New: emo.\ ctx} \\
    Vividness + ``nowness'' & Sim.~8            & Inherited               \\
    \ldots                  & \ldots            & \ldots                  \\
  \end{tabular}
  \note{Orient the audience before the deep dives. Red entries depend on the
        novel architecture; black entries are inherited from eCMR / CMR2.
        Flag that I'll deep-dive on Sim.~2 and Sim.~6 but only touch the
        others briefly.}
\end{frame}
```

Red-coloring for novel mechanisms should match what you use in slide titles
with `\novelbadge`. Consistency compounds across the talk.

### Novelty marking on a slide title

```latex
\begin{frame}{Intrusive recollection \novelbadge}
  \includegraphics[width=0.72\textwidth]{figures/fig_intrusion.pdf}
  \note{This is one of the two deep-dive slides on novel mechanisms.
        The `[NEW]` badge in the title primes the audience to focus
        on what depends on the new architecture.}
\end{frame}
```

### Equation slide — equations speak, prose doesn't

For an expert audience, the equation should carry the meaning. Don't
sandwich it in explanatory prose. The note carries the verbal walkthrough.

```latex
\begin{frame}{Retrieved-context dynamics}
  Context evolves with each item:
  \[ \mathbf{c}_i = \rho_i \mathbf{c}_{i-1} + \beta_{enc} M^{FC} \mathbf{f}_i \]
  Retrieved items update context in the same form:
  \[ \mathbf{f}^{IN}_r = M^{CF} \mathbf{c}_r \]
  \note{Walk through each symbol --- $\mathbf{c}$, $M^{FC}$, $M^{CF}$,
        $\beta_{enc}$. Emphasize the bidirectional associations and the
        fact that encoding and retrieval use the same equations. See
        domain-knowledge.md for canonical parameter names.}
\end{frame}
```

### References (with `allowframebreaks` for overflow)

```latex
\begin{frame}[allowframebreaks]{References}
  \bibliographystyle{apalike}
  \bibliography{references}
\end{frame}
```

## Text minimization rules

Apply these preemptively, not after correction.

- If a slide has an equation and an explanation of the equation, delete the
  explanation.
- If a slide has a diagram and a caption describing the diagram, delete the
  caption.
- If a bullet is a full sentence with a period, compress it to a phrase.
- In column text blocks, use `\setstretch{0.95}` and `\vspace{4pt}` between
  paragraphs rather than the default leading.
- Footer captions: one line. Two-line footers almost always clip.
- Default to `11pt`; do not reach for `\small` or `\scriptsize` to fit more
  words. Cut the words instead.

### Prose hygiene

- **No em-dashes** (`---`, `—`). Use colons, periods, or parentheses.
- **No inline lists in sentences.** A comma-separated list inside a sentence
  must become either:
  - One sub-bullet per item (when items are short sentences or phrases):
    ```latex
    \begin{itemize}
      \item Usual explanations:
      \begin{itemize}
        \item word frequency
        \item concreteness
        \item emotional valence
        \item fatigue
        \item time of day
        \item sleep
      \end{itemize}
    \end{itemize}
    ```
  - Or a single-line numbered inline list (when items are short and the
    whole list fits in one line), using `enumerate` with `[label=\arabic*.,
    leftmargin=*]` or a manual numbering with `\textbf{1.}`:
    ```latex
    Usual explanations:
    \textbf{1.}~word frequency \textbf{2.}~concreteness
    \textbf{3.}~emotional valence \textbf{4.}~fatigue
    \textbf{5.}~time of day \textbf{6.}~sleep
    ```
- **No filler intensifiers**: "fluctuates strikingly", "remarkably",
  "importantly", "interestingly", "robust" (as filler). Cut them.
- **Title slide shows title/authors/affiliation/date only.** No data
  source, no repo path, no pipeline provenance, no build date. Metadata
  belongs in the compile log, not on the first slide.

## Recurring visual motifs

For talks with multiple parallel mechanisms, design one reusable figure and
toggle its emphasis across slides. The template's `\memorydiagram{a}{b}`
macro is one example: call it `{active}{inactive}` on an encoding slide and
`{inactive}{active}` on a retrieval slide to visually parallel the two
pathways. Audience builds recognition without prose. See `visual_design.md`
for the pattern in general.

## Figure path conventions

Copy figure files from each bundle's `figures/` directory into a local
`figures/` subdirectory alongside the `.tex`. Use relative paths:

```latex
\includegraphics[width=0.8\textwidth]{figures/fig1.pdf}
```

Don't use absolute paths — the talk .tex should be self-contained and
portable.

## Handling name collisions across papers

When pulling figures from multiple bundles into one deck, prefix each figure
with the paper slug to avoid collisions:

```
figures/
├── cohenkahana2019_fig1.pdf
├── cohenkahana2019_fig2.pdf
├── healeykahana2016_fig1.pdf
└── healeykahana2016_fig2.pdf
```

Update `\includegraphics` paths accordingly.

## EPS figures

If a source bundle ships `.eps` figures (older PsychRev submissions often
do), convert to PDF with `epstopdf` at generation time:

```bash
epstopdf src.eps --outfile=figures/src.pdf
```

Then reference the `.pdf` from `\includegraphics`. Don't ship both.

## Citation keys

When extracting `\cite{}` commands from the source paper, the cite keys
reference the paper's original `.bib`. When building the deck, dedupe keys
across all source bibs and write a unified `references.bib` in the deck
directory.

If two source bibs use the same key for different entries, the deck builder
should rename one with a suffix (`kahana1996b`) and update the citation in
the corresponding paper's text.

## LaTeX escaping

Text pulled from paper sources may contain LaTeX-unsafe characters. Escape
these in generated content (not in content the user supplies verbatim):

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

Be careful: if the source material is already LaTeX (e.g., a sentence lifted
directly from `drafts/selected.tex`), don't re-escape.

## Section + frametitle style

Each section only needs one `\section{}` declaration — subsequent frames in
that section inherit the section in the progress bar / header. Don't
redeclare.

Keep frame titles short (under 40 chars). `metropolis` wraps long titles
without truncation but the wrap looks ugly; `Madrid` truncates.

## Common pitfalls

- **Overflow clipping** — `pdflatex` succeeds silently. Always render-verify
  (`compile_beamer.py --render-preview`).
- **Transparency in included PDFs** — pdflatex handles this; other engines
  may not. If a figure fails to render, convert to PNG first.
- **Unicode in figure captions** — LaTeX + inputenc utf8 handles the Latin-1
  range. For Greek or math, use LaTeX commands: `\alpha`, `\beta`.
- **References not resolving** — the `\cite{key}` must match a `@article{key,
  ...}` entry in `references.bib`. Missing entries produce `[?]` in the
  output. `compile_beamer.py` surfaces these warnings.
- **`metropolis` not installed** — some TeX Live installations ship without
  it. Fall back to Madrid via the swap block in the template preamble.
