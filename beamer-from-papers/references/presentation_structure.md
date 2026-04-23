# Default presentation structures

Target slide counts assume ~60 seconds per slide for an expert audience, ~90 seconds for grad students, ~2 minutes for a teaching lecture. Adjust accordingly.

## Topic-aware structure selection (when `memory-publications` is installed)

Before picking a template, classify the paper(s) into one of the five research threads defined in `memory-publications/references/research-index.json`:

1. `memory_theory_and_models` — behavioral/theoretical papers
2. `behavioral_economics_memory_decisions` — memory × decisions; mixed audience register
3. `eeg_oscillations` — intracranial or scalp EEG methods-heavy
4. `brain_stimulation` — closed-loop / open-loop stim; translational slant
5. `single_unit_recordings` — unit data; neurophysiology-heavy

The thread changes what "methods" means and therefore what slides are load-bearing:

| Thread | Needs extra slides for | Can often cut |
|---|---|---|
| memory_theory_and_models | Model equations + schematic; fit procedure; parameter interpretation | Heavy methods detail |
| behavioral_economics_memory_decisions | Task paradigm diagram; cross-domain translation (econ ↔ psych); both-domain definitions | Long literature review |
| eeg_oscillations | Electrode coverage figure; frequency bands definition; referencing / preprocessing; IRASA if used | Behavioral design detail |
| brain_stimulation | Stim parameters (amplitude / freq / pulse width / duration / location); target selection; safety / artifact handling; classifier design if closed-loop | Pure behavioral controls |
| single_unit_recordings | Unit isolation criteria; anatomical localization; spike-sorting QC | Population-level decoding |

So before picking the single-paper template below, read the paper's thread and adjust: a 25-slide brain-stimulation talk might devote 5 slides to the methods section where a 25-slide behavioral talk needs only 3.

When `memory-publications` is absent, skip this step and use the generic template. The output is still usable — just less tuned.

## Single paper, expert audience

Default for most requests. Maps one paper to ~25 slides covering the full arc from motivation to implications.

| Section | Slides | Content |
|---|---|---|
| Title | 1 | Title, authors, institute, date |
| Outline | 1 | `\tableofcontents` |
| Motivation | 2 | Why this question matters; why existing answers are insufficient |
| Background | 1-2 | Prior work the audience should have in mind before the new result |
| Research question | 1 | Crisp statement of what the paper asks |
| Methods | 3-5 | Design, stimuli, participants, key analyses; one figure per methodological subtlety |
| Results | 8-10 | One figure per major finding with interpretation alongside |
| Discussion | 2-3 | What this changes; how it connects to theory |
| Limitations / future | 1 | Honest constraints + where this goes next |
| Acknowledgments | 1 | Collaborators + funding |
| References | 1-2 | `[allowframebreaks]` handles overflow |

The **results** section is where slide density matters most. Default = one figure per panel of interest. For a 13-figure paper like CohenKahana2019, this means 13 results slides; if that blows the target length, prioritize figures that drive the paper's headline claim and demote others to backup slides.

## Multiple papers, integrated theme

When the user says "our papers on X" and the papers share a framework, interleave them by theme rather than isolating each.

| Section | Slides | Content |
|---|---|---|
| Title + outline | 2 | Introduce the unifying thread |
| Unifying motivation | 2-3 | The shared research program |
| Theme 1: phenomenon A | 4-6 | Evidence pulled from multiple papers |
| Theme 2: model / mechanism | 4-6 | " |
| Theme 3: implications / extensions | 4-6 | " |
| Synthesis | 2-3 | What the papers collectively claim; remaining puzzles |
| Acknowledgments + references | 2-3 | |

This works well when the user wants a talk, not a report.

## Multiple papers, one-section-per-paper

Safer default when papers are less thematically unified or the user wants parity across them.

| Section | Slides per paper | |
|---|---|---|
| Title + outline | 2 | |
| Paper 1: setup + key results | 6-8 | |
| Paper 2: setup + key results | 6-8 | |
| ... | | |
| Comparison / synthesis | 3-5 | Agreement, divergence, implications |
| Acknowledgments + references | 2-3 | |

## Lecture / teaching mode

Mimic the style of `BigData_ML_Lecture.pdf` (the CML lecture reference).

Characteristics:

- Single-word section divider slides before each section (`\section{Regularization}` → auto-generates a dividing slide)
- Equation-dense: numbered equations, derivations walked through explicitly
- Bullet-heavy: `\begin{itemize}` with `▶` markers (Madrid's default); each bullet is a single concept
- Heavier use of external figures (textbook covers, pedagogical diagrams from cited sources)
- Links displayed inline verbatim for reference material: `https://d2l.ai/`
- Minimal speaker notes — the content on the slide IS the teaching material

Target length is longer (45-90 min = 30-60 slides) because the audience needs time to work through each step.

## Slide plan data structure

`scripts/plan_deck.py` produces a deck plan as a JSON document before writing any LaTeX. This lets the same plan feed both Beamer and PPTX generators. Shape:

```json
{
  "title": "Memory Search: A Primer",
  "subtitle": "Retrieved Context Theory",
  "authors": ["Michael J. Kahana"],
  "date": "2024-10-15",
  "slides": [
    {
      "kind": "title",
      "content": null
    },
    {
      "kind": "outline",
      "content": null
    },
    {
      "kind": "section_header",
      "title": "Motivation"
    },
    {
      "kind": "content",
      "section": "Motivation",
      "title": "Why memory search matters",
      "bullets": ["Point 1", "Point 2"],
      "figure": null,
      "notes": "Open with the question..."
    },
    {
      "kind": "figure",
      "section": "Results",
      "title": "Serial position effects",
      "figure": "figures/fig2_spc.pdf",
      "caption": "Short caption for the slide",
      "notes": "Classic U-shape; walk through primacy then recency."
    },
    {
      "kind": "references"
    }
  ],
  "bibliography_entries": ["kahana1996", "howard2002", ...]
}
```

Supported `kind` values: `title`, `outline`, `section_header`, `content`, `figure`, `columns` (text + figure side-by-side), `equation`, `references`, `acknowledgments`.

Keep the plan as a data structure, not as mid-generation LaTeX. LaTeX is emitted from the plan in one step by `beamer_generation.md`'s templates.
