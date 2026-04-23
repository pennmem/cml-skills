# Visual design

TikZ-first patterns for data figures, recurring visual motifs, and the
test-artifact workflow for risky redesigns.

The cardinal rule from SKILL.md in practice: every slide should have a
visual element (figure, diagram, or equation), and the visual should do the
explanatory work the prose would otherwise do.

## Figure rules (non-negotiable)

Critiques of earlier auto-generated decks surfaced a consistent set of
failures. Apply these rules on every figure slide:

1. **Maximum 2 figures (or sub-figures) per slide.** If the paper's Figure 4
   has panels A and B you can keep both side-by-side. If it has A, B, C, D,
   split across multiple slides.
2. **Same-type grouping.** Two figures on one slide must be the same kind of
   plot (two bar charts, two line plots, two brain renderings). Do not mix
   a bar chart with a schematic on one slide just because they're from the
   same figure number in the paper.
3. **Always centered.** `\centering` at the top of the frame, or wrap the
   `\includegraphics` in `\begin{center}...\end{center}`.
4. **Large and dominant.** A solo figure should occupy 0.75–0.88 of the
   text width. Two side-by-side figures should each use 0.46–0.48 of the
   text width. Do not emit figures under 0.6\\textwidth when they are the
   point of the slide.
5. **Bound the height** to prevent bottom clipping. Use
   `keepaspectratio` with both a width and a height:
   `\includegraphics[width=0.82\textwidth, height=0.72\textheight, keepaspectratio]{...}`.
6. **Render-verify every figure slide.** `pdflatex` does not catch
   overflow; `pdftoppm` previews do.
7. **Every figure slide has 2–3 summary bullets** placed above, below, or
   to the side: what the figure shows (axes/comparison) and the takeaway.
   Never emit a figure-only slide with no textual orientation.
8. **Be discerning.** Not every figure in the paper deserves a slide. Ask
   what story links the figures you include; if a figure doesn't advance
   the narrative, demote it to the appendix (`\appendix`) or cut it.

## When to use TikZ vs. `\includegraphics`

**Use TikZ for:**
- Bar plots, line plots, scatterplots of data the paper reports.
- Schematic diagrams of models (CMR feature/context layers, pathway diagrams).
- Small multiples that need consistent styling across slides.
- Anything you'd want to tweak incrementally while iterating on a slide.

**Use `\includegraphics` for:**
- Complex multi-panel publication figures where simplification would distort
  the story (e.g., an electrode-coverage brain rendering).
- Photographs and microscopy.
- Screenshots of tasks, software, clinical interfaces.
- Figures that must exactly match the paper's camera-ready version.

The TikZ advantage on data figures is iteration speed: colors, legends,
labels, and axis ranges change in-place without re-running an analysis.
Publication figures are sized for print density; on a slide they're usually
too busy, and TikZ recreations let you show only the panels that matter for
the talk.

## pgfplots patterns

`pgfplots` is loaded by the template. Preferred defaults:

```latex
\begin{tikzpicture}
  \begin{axis}[
    width=7.5cm, height=5cm,
    title={Serial position},
    xlabel={Position}, ylabel={P(recall)},
    xmin=0, xmax=15, ymin=0, ymax=1,
    xtick={1,5,10,15},
    legend pos=south east,
    legend style={draw=none, font=\footnotesize},
    every axis plot/.append style={thick},
  ]
    \addplot[color=cmlblue, mark=*, mark size=2pt]
      coordinates {(1,0.62)(2,0.55)(3,0.50)(4,0.47)(5,0.45)
                   (6,0.44)(7,0.45)(8,0.47)(9,0.52)(10,0.62)
                   (11,0.70)(12,0.78)(13,0.83)(14,0.86)(15,0.80)};
    \addlegendentry{Data}
    \addplot[color=novelred, mark=o, mark size=2pt, dashed]
      coordinates {(1,0.60)(2,0.53)(3,0.49)(4,0.46)(5,0.44)
                   (6,0.44)(7,0.46)(8,0.49)(9,0.54)(10,0.63)
                   (11,0.71)(12,0.78)(13,0.82)(14,0.84)(15,0.79)};
    \addlegendentry{Model}
  \end{axis}
\end{tikzpicture}
```

### Data + model with offset error bars

When both data and model points fall at the same nominal x, offset the model
by a small amount (e.g., +0.12) so error bars remain visible:

```latex
\addplot[only marks, mark=o, mark size=2pt, thick,
         error bars/.cd, y dir=both, y explicit]
  coordinates {
    (0.88, 0.57) +- (0, 0.06)
    (1.88, 0.71) +- (0, 0.05)
    (2.88, 0.83) +- (0, 0.04)
  };
\addplot[only marks, mark=*, mark size=2pt]
  coordinates {(1.12, 0.56) (2.12, 0.71) (3.12, 0.82)};
```

### Bar chart with groups

```latex
\begin{axis}[ybar, bar width=8pt,
             enlarge x limits=0.15,
             symbolic x coords={Young, Old},
             nodes near coords,
             ymin=0, ymax=1,
             ylabel={Hit rate}, legend pos=north east,
             legend style={draw=none, font=\footnotesize}]
  \addplot[fill=cmlblue!80]  coordinates {(Young,0.89) (Old,0.72)};
  \addplot[fill=novelred!80] coordinates {(Young,0.84) (Old,0.69)};
  \legend{Data, Model}
\end{axis}
```

## Color palette

Set once in the preamble and reuse. The template defines `cmlblue` and
`novelred`. Add category colors as needed:

```latex
\definecolor{cmlblue}{RGB}{28, 53, 115}      % primary accent
\definecolor{novelred}{RGB}{176, 0, 32}      % novel mechanism
\definecolor{cmlgreen}{RGB}{0, 110, 63}      % supporting data
\definecolor{cmlgray}{RGB}{120, 120, 120}    % baseline / control
```

Use color consistently across the talk: one color per category, not one
color per slide. Audiences build recognition.

## Recurring visual motifs

For talks with multiple parallel mechanisms, design one reusable figure and
toggle its emphasis across slides. The template ships one example:

```latex
% Feature-to-context pathway emphasized
\memorydiagram{active}{inactive}

% Context-to-feature pathway emphasized
\memorydiagram{inactive}{active}

% Full retrieval loop engaged
\memorydiagram{active}{active}
```

The macro draws Items and Context boxes with $M^{FC}$ and $M^{CF}$ arrows,
bolding the active pathway and graying the inactive one. Build a habit of
re-using it on every slide that discusses encoding or retrieval — the
audience builds recognition, architectural parallels become visible without
prose, and edits propagate from one macro definition.

### Designing your own motif

1. Identify the mechanism or object that appears repeatedly in the talk.
2. Draw it in TikZ once, parameterize the variable elements, give the macro
   a short name.
3. Use it consistently — every slide that discusses the mechanism uses the
   same visual.

Example skeleton:

```latex
\newcommand{\stimdiagram}[1]{%
  \begin{tikzpicture}
    % #1 in {random, closed-loop, sham} toggles emphasis
    \node (brain) {\includegraphics[width=2cm]{figures/brain.pdf}};
    \node[right=of brain] (sig) {Classifier};
    \draw[->, thick] (brain) -- (sig);
    \ifnum\pdfstrcmp{#1}{closed-loop}=0
      \draw[->, thick, cmlblue] (sig) |- (brain);
    \fi
  \end{tikzpicture}%
}
```

## Text minimization in practice

The rules from SKILL.md, applied:

- **Before** (too much text):
  ```latex
  \begin{frame}{Serial position effects}
    \begin{itemize}
      \item The serial position curve shows a U-shape with strong recency
            and weaker primacy
      \item Recency is attenuated by a filled delay, but primacy is not
      \item This asymmetry is explained by retrieved context theory
    \end{itemize}
  \end{frame}
  ```
- **After** (visual-first):
  ```latex
  \begin{frame}{Serial position effects}
    \centering
    \includegraphics[width=0.85\textwidth]{figures/fig2_spc.pdf}
    \note{The serial position curve shows a U-shape with strong recency
          and weaker primacy. Recency is attenuated by a filled delay,
          but primacy is not. This asymmetry is explained by retrieved
          context theory --- recency is a retrieval-side effect that
          drifts away with time, whereas primacy is encoding-side and
          preserved.}
  \end{frame}
  ```

The information didn't disappear; it moved to the container (notes) designed
to hold full sentences.

### Tightening a cluttered column slide

```latex
\begin{columns}
  \column{0.5\textwidth}
    \setstretch{0.95}   % tighten leading
    \begin{itemize}
      \setlength\itemsep{3pt}  % tighten item spacing
      \item Phrase
      \item Phrase
    \end{itemize}
  \column{0.5\textwidth}
    \centering
    \includegraphics[width=\textwidth]{figures/x.pdf}
\end{columns}
```

Single-line footer caption under the figure:

```latex
\column{0.5\textwidth}
  \centering
  \includegraphics[width=\textwidth]{figures/x.pdf}
  {\scriptsize \color{cmlgray} Data from Kahana et al., 2002}
```

## Novelty marking

Use `\novelbadge` in frame titles for new content:

```latex
\begin{frame}{Intrusive recollection \novelbadge}
  ...
\end{frame}
```

In summary tables, color rows that depend on novel architecture:

```latex
\begin{tabular}{lll}
  Phenomenon        & Source  & Mechanism \\
  \hline
  Emotional cluster & Exp.~1  & Inherited                        \\
  Mood-congruent    & Sim.~2  & {\color{novelred}\textbf{NEW}}   \\
  Intrusions        & Sim.~6  & {\color{novelred}\textbf{NEW}}   \\
\end{tabular}
```

Novelty marking compounds: if one slide uses `\novelbadge` and another uses
red text in a summary table, audiences learn that the red-novel pairing is
load-bearing and parse subsequent slides faster.

## The test-artifact workflow

For risky redesigns (new table structure, new mechanism slide, reorganized
section), build a standalone `test_foo.tex` alongside the deck that renders
just the new slides. Iterate with the user on the isolated design, then drop
the approved version into the main deck.

### Setup

```bash
cd /path/to/deck/
cp cml_beamer_template.tex test_summary_table.tex
# Strip everything except the preamble and the new frame(s)
```

A test artifact typically looks like:

```latex
\documentclass[aspectratio=169,11pt]{beamer}
\usetheme{metropolis}
\metroset{sectionpage=none,progressbar=frametitle}
\definecolor{cmlblue}{RGB}{28, 53, 115}
\definecolor{novelred}{RGB}{176, 0, 32}
\setbeamercolor{alerted text}{fg=novelred}
\newcommand{\novelbadge}{\hfill{\color{novelred}\scriptsize\textbf{[NEW]}}}

\begin{document}
\begin{frame}{Results summary}
  % the candidate new slide
\end{frame}
\end{document}
```

Compile and render-verify:

```bash
python3 scripts/compile_beamer.py test_summary_table.tex --render-preview 1
```

Open the PNG, show the user, iterate. Only once approved do you promote the
frame body into the main deck.

### Why this is faster than iterating in-deck

- Full deck compile takes 10–30s with figures; a single-frame test compiles
  in ~2s.
- No risk of breaking the main deck while experimenting.
- Easier to share with the user as a single PNG preview.
- Encourages smaller, reviewable units of change.

## Render-and-verify protocol

After every batch of slide edits:

```bash
python3 scripts/compile_beamer.py deck.tex --render-preview 3-8
```

Inspect the PNGs in `preview/`. Look for:

- Text overflowing the frame boundary (clipping).
- Figures overlapping text or each other.
- Accidentally tiny figures (usually a `width` that was dropped).
- Accidentally large figures (usually a `width=\textwidth` on a two-column
  slide where `\textwidth` is the column width, not the frame width).
- Color clashes between `cmlblue` and theme defaults.

Common fixes:

| Symptom | Fix |
|---|---|
| Text clipping at bottom | `\setstretch{0.95}`, reduce `\vspace`, or cut text |
| Bullets overflow | Split into two slides, or use `\scriptsize` (last resort) |
| Table wider than frame | `\small`, reduce `\tabcolsep`, or rotate columns |
| Figure too big in column | Use `width=0.9\linewidth`, not `\textwidth` |
| `metropolis` missing | Swap to Madrid (template preamble comments explain) |

Do not ship a deck without at least one render-verify pass over the final
slide set.
