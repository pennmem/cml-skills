# Figure selection

A talk can show 10 figures in its results section. A poster shows 3–5. This file is how you pick which ones.

## The selection question

For every figure in the paper, ask: **if the viewer sees only this figure and no other, do they understand what the paper claims?**

Figures that pass: keep. Figures that only make sense in the context of other figures: cut or combine.

## Priority ladder

Walk the paper's figures in this order and select:

### 1. The "money figure"

Every empirical paper has one. It's the figure the discussion section leads with — often Figure 2 or Figure 3, occasionally Figure 4 (rarely Figure 1, which is usually a schematic). The discussion paragraph that begins "Our key result..." or "Figure X shows..." points at it.

The money figure **must** be on the poster. It's non-negotiable. If the money figure has sub-panels, all relevant panels come too (or crop to the panel that most directly shows the main effect).

### 2. A methods / design schematic

If the paper's methods are non-obvious (novel task, unusual analysis pipeline, complex closed-loop setup), include a schematic figure. This lets a viewer understand what the participants *did* before trying to parse results. Candidates:

- Task diagrams (trial timing, stimulus presentation)
- Electrode coverage (iEEG / ECoG papers)
- Model architecture diagrams (for computational modeling papers)
- Closed-loop control diagrams (for stimulation papers)

If the methods are standard (free recall with a word list, standard EEG cap), skip the schematic — spend the real estate on results.

### 3. One or two supporting result figures

Pick figures that show effects **complementary** to the money figure, not ones that show the *same* effect via a different analysis. For example, if the money figure is a lag-CRP, don't also include a semantic-CRP showing the same clustering story; include a serial position curve that shows a different aspect.

Good complement: different DV on the same data (e.g., PFR if money figure is lag-CRP).
Good complement: same effect at a different scale (e.g., individual-subject plot if money figure is group-level).
Bad complement: the same effect with different tick marks or binning.

### 4. A model-fit or comparison figure (if applicable)

For modeling papers, a figure showing the model's predictions overlaid on data is almost always worth a slot. This is where "the model accounts for the effect" becomes visible. Examples:

- CMR fits to serial position curves (data as points, model as lines)
- Model-versus-data plots across multiple conditions
- Parameter recovery figures if novel fitting procedures are introduced

### 5. NEVER pick these for a poster

- Control analyses that rule out alternative explanations — the viewer won't know to ask
- Replication figures that show the main effect again in a different dataset — one is enough
- Individual-subject panels showing the effect is robust — unless robustness IS the story
- Supplementary-material figures
- Tables (posters are bad for tables; convert to a bar chart or cut)
- Fit-quality diagnostics (residual plots, Q-Q plots)
- Equation "figures" (put equations in the text block, not as images)

## Multi-panel figures

Papers commonly use 4-panel figures where 2 panels are the effect and 2 panels are controls. For the poster, **crop to the effect panels**. A 2-panel figure is easier to read at poster scale than a 4-panel figure where two panels don't carry weight.

To crop: if the original is a PDF, use `pdfcrop` or open in Illustrator. If it's PNG, use any image editor. Save as a separate file in the deck's `figures/` directory with a name like `fig2_cropped.pdf`.

If the authors used a 6-panel figure to fit journal space limits (common in Nature-family journals), consider **splitting it back out** into 2-3 separate poster figures if each panel carries its own story.

## Figure resolution

Journal figures are often rasterized at 300dpi for print, which is fine. But some journals strip resolution for web-PDF. Check by viewing the paper's figures at 200% zoom — if they're sharp, the PDF version is fine; if fuzzy, ask the lead author for the source file.

For a 48×36 poster printed at 300dpi, figures need to be at minimum:

| Figure size on poster | Required min pixels |
|---|---|
| 10 × 8 inches | 3000 × 2400 |
| 8 × 6 inches | 2400 × 1800 |
| 6 × 4 inches | 1800 × 1200 |

Below these, figures will look pixelated at print scale even if they look fine on screen.

## When there isn't a good figure

Occasionally a paper's key claim is supported by statistics rather than a figure (e.g., "we found a three-way interaction, F(2,56) = 8.4, p < .001"). This doesn't carry a poster. Two options:

1. **Ask the lead author for a custom figure.** A bar chart showing the interaction is almost always makeable from the data and carries the poster much better than an F-statistic in prose.
2. **Make a custom figure from the paper's data.** If the data are public (OSF, GitHub), generate a summary figure that shows the effect. Credit it as "post-hoc visualization from the published data."

Don't leave the claim un-illustrated. A poster is a visual medium.

## When `memory-publications` is installed

Consult `memory-publications/references/domain-knowledge.md` to understand what figures are canonical in each subfield. For example:

- Free recall papers → SPC, PFR, lag-CRP, semantic-CRP
- Oscillation papers → time-frequency decomposition, SME plots, topography maps
- Stimulation papers → stim location on brain surface, delta-classifier histograms, effect size by brain region

If the paper has one of each canonical figure, those are strong poster candidates because viewers from the field can parse them fast.

When absent, the guidance in this file stands — the principles are general.
