---
name: beamer-from-papers
description: Use this skill whenever a user in the Computational Memory Lab (CML) wants to turn one or more CML papers into a scientific presentation — Beamer LaTeX as the primary output, with PowerPoint (.pptx) and PDF as parallel outputs when requested. Triggers include "make a talk from these papers", "build a Beamer deck on my PTSD paper", "slides from CohenKahana2019", "put together a presentation comparing our retrieved-context papers", or any request to convert CML paper content into a slide deck. The skill assumes papers are already staged as bundles by the `paper-acquisition` skill; it does not search for or download papers itself. Do NOT use this for general-purpose presentations unrelated to CML papers, or for purely text-to-slides conversions that don't involve a paper bundle.
---

# beamer-from-papers

Turn one or more CML paper bundles into a scientific Beamer presentation, with optional PowerPoint and PDF parallel outputs. Built for talks to an expert audience (grad students, faculty, conference attendees) — not teaching lectures, unless the user asks.

## Relationship to other skills

**Upstream (required input).** This skill is the consumer of paper bundles produced by `paper-acquisition`. Always run `paper-acquisition` first if bundles don't already exist. If the user asks for a presentation without having run acquisition, do that step transparently and report it — don't make them run two separate commands when they asked for one thing.

**Lateral (optional enrichment).** If the `memory-publications` skill is installed, consult three of its reference files to improve output quality. The skill works without them — the fallback is generic academic voice and figure-caption-based content — but the difference in output quality is substantial.

```bash
# Check for memory-publications once at skill startup
for d in ./skills/memory-publications /mnt/skills/user/memory-publications \
         ~/.claude/skills/memory-publications ../memory-publications; do
  [ -f "$d/SKILL.md" ] && MEMPUB_DIR="$d" && break
done
```

When `$MEMPUB_DIR` is set, integrate these three files at specific workflow steps:

| memory-publications file | Used by | Where |
|---|---|---|
| `references/domain-knowledge.md` | Deep reading + slide drafting | `references/reading_strategy.md` tells you when to consult it |
| `references/writing-style.md` | Speaker notes + slide bullet voice | `references/speaker_notes.md` tells you how to adapt it to the notes register |
| `references/research-index.json` | Topic-aware deck structure | `references/presentation_structure.md` uses it to pick section patterns |

`memory-publications/references/current-projects.md` is primarily a paper-acquisition concern (it maps short names to Box folders), but when one of the user's active manuscripts is the subject of the talk, reading the project's entry gives you target-journal context, lead-author list, and status that can seed the title slide and acknowledgments.

**Do not duplicate** memory-publications content into this skill's references. If it isn't installed, use the fallbacks described in the downstream reference files.


## High-level workflow

1. **Confirm inputs** — one or more paper bundles (paths to `<bundle>/manifest.json`).
2. **Elicit presentation parameters** — audience, duration/slide count, structure preference. Use sensible defaults.
3. **Read the papers deeply** — text of each draft, figures (with vision), `.bib` for citations.
4. **Plan the deck** — section structure, slide-by-slide outline.
5. **Generate the Beamer source** — `.tex` file using the CML template.
6. **Compile to PDF** (and optionally PPTX).
7. **Present results** — PDF, `.tex` source, and a brief summary.

See `references/workflow_details.md` for expanded guidance on each step.

## Eliciting parameters

When the user invokes the skill without specifying details, ask in a single turn (don't ping-pong):

```
Building a presentation from <N> paper(s). Quick parameters:

1. Audience: [expert-researchers | grad-students | mixed-audience | lecture]
   Default: expert-researchers

2. Target length: [15-min / ~12 slides | 30-min / ~25 slides | 45-min / ~40 slides | custom]
   Default: 30-min

3. Structure (multi-paper only): [one-section-per-paper | integrated-by-theme]
   Default: one-section-per-paper + a comparison section at the end

4. Include speaker notes? (yes/no) — Default: yes

5. Output formats: [pdf-only | pdf+tex | pdf+tex+pptx]
   Default: pdf+tex
```

If the user's initial message already specified any of these, skip those questions. If they say "just use defaults," use all defaults and move on.

## Deep reading

The user asked for "deepest possible reading." For each paper:

1. **Full text**: read `drafts/selected.tex` start to finish. If only a PDF exists, extract text via pdftotext.
2. **Figures with vision**: for each file in `figures/`, load it as an image and describe what it shows — not just the caption. This is the difference between "Figure 2: serial position curve" and "Figure 2 shows a U-shaped curve with strong recency (last 4 items ~80% recall) and weaker primacy (first 2 items ~40%), on lists of length 15-40."
3. **Citations**: parse the `.bib` for entries that appear in the draft (via `\cite{}` keys). Build a working bibliography for the talk.

For multi-paper presentations, additionally identify:
- **Shared methods / datasets** (PEERS? ltpFR? Kahana lab word pool?)
- **Shared theoretical framework** (CMR variants? SAM? dual-store?)
- **Points of agreement and disagreement** across the papers

See `references/reading_strategy.md`.

## Planning the deck

Default structures by scenario:

### Single paper, expert audience (~25 slides)

1. Title slide (1)
2. Outline (1)
3. Motivation / background (2-3)
4. Research question / hypothesis (1)
5. Methods (3-5) — experimental design, stimuli, participants, analyses
6. Results (8-10) — one figure per major finding, with interpretation
7. Discussion / implications (2-3)
8. Limitations / future directions (1)
9. Acknowledgments (1)
10. References (1-2)

### Multiple papers, expert audience

1. Title (1), Outline (1), Unifying motivation (2-3)
2. Section per paper: brief setup + key results (6-8 slides each)
3. Comparison / synthesis section: what they agree on, where they diverge, implications (3-5)
4. Acknowledgments + References

### Lecture / teaching mode

Favor equations, derivations, worked examples. More bullet-heavy. Mirrors the style of `BigData_ML_Lecture` (the CML lecture reference shipped with this skill).

See `references/presentation_structure.md` for more variants.

## Generating the Beamer source

Use `assets/cml_beamer_template.tex` as the starting point. It matches the visual style of CML's existing Beamer lectures: Madrid theme, navy blue, lab name in the footer, section dots in the header.

The template exposes these variables at the top:

```latex
\title{...}
\subtitle{...}  % optional
\author{...}
\institute{Computational Memory Lab \\ University of Pennsylvania}
\date{\today}
```

For multi-paper talks, use `\section{}` divisions per paper (or per theme if integrated structure).

Figures get copied from each bundle's `figures/` directory into a local `figures/` alongside the `.tex` at generation time. Use relative paths in `\includegraphics`.

Inline citations use `\cite{}` against a `references.bib` built from the union of all papers' bibs (deduped by cite key).

See `references/beamer_generation.md` for detailed patterns.

## Speaker notes

Every content slide should have a speaker note of roughly 100-300 characters — enough to remind the speaker of the narrative beat without being a script. Use Beamer's `\note{}`:

```latex
\begin{frame}{Serial Position Effects}
  \includegraphics[width=\textwidth]{figures/fig2_spc.pdf}
  \note{Classic U-shape. Start with primacy and recency as the two
        phenomena, mention that DFR attenuates recency (setup for
        next slide), keep it to 45 seconds.}
\end{frame}
```

Compile twice: once with `\setbeameroption{hide notes}` for the talk-facing PDF, once with `\setbeameroption{show only notes}` for a notes-only printable version. Ship both.

See `references/speaker_notes.md` for tone and length guidance (looked at 16 real CML speaker-note examples from AES 2017 to calibrate).

## Compiling

Primary: `pdflatex -interaction=nonstopmode` → `biber` (or `bibtex`) → `pdflatex` → `pdflatex`. Three pdflatex passes handle TOC + citations + cross-refs.

Use `scripts/compile_beamer.py` — it wraps the passes, captures errors, and surfaces the actionable ones to the user (undefined references, missing figures, etc.) rather than the full 500-line log.

If LaTeX isn't installed, the script surfaces a clear error pointing to `references/latex_setup.md`.

## PPTX output

**Native generation** via `python-pptx` — **not** a Beamer→PPTX conversion (those look terrible). Build the same slide plan with the same figures/text/notes, but emit `.pptx` directly. This means two parallel code paths that share the slide plan data structure.

See `references/pptx_generation.md` and `scripts/generate_pptx.py`.

## Reporting results

When done, tell the user:

- Paths to: the compiled PDF, the `.tex` source, the `.pptx` if requested, the notes-only PDF
- Slide count and rough timing estimate
- Any warnings from compilation (missing figures, unresolved citations)
- One-line "what would you like to change?" prompt inviting revision

Keep it short. The user can open the artifacts themselves.

## Reference files

- `references/workflow_details.md` — step-by-step operator notes
- `references/reading_strategy.md` — how to read papers deeply with vision
- `references/presentation_structure.md` — default outlines per scenario
- `references/beamer_generation.md` — LaTeX generation patterns
- `references/speaker_notes.md` — tone, length, and examples from real CML talks
- `references/pptx_generation.md` — python-pptx patterns that match the Beamer output
- `references/latex_setup.md` — troubleshooting missing LaTeX / beamer class / fonts

## Assets

- `assets/cml_beamer_template.tex` — the starter template (Madrid theme, CML footer)
- `assets/example_single_paper_deck.tex` — reference for single-paper structure
- `assets/example_multi_paper_deck.tex` — reference for comparison structure

## Scripts

- `scripts/compile_beamer.py` — runs the pdflatex passes + error filtering
- `scripts/generate_pptx.py` — native PPTX emitter parallel to Beamer
- `scripts/plan_deck.py` — builds the slide plan data structure from bundles + parameters
