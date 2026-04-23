# Default presentation structures

Target slide counts below assume ~90 seconds per slide for an expert audience
(memory scientists, neuroscientists) — that is the recent CML norm, not the
older "60 seconds per slide" rule. Use 120s for grad students, 150s for a
teaching lecture. Scale the slide counts to fit the talk slot, not the other
way around.

| Talk length | Target slide count |
|---|---|
| 15 min | ≤ 12 |
| 30 min | ≤ 22 |
| 50 min | 30–40 |
| 60 min | 35–50 |
| 90-min lecture | 55–70 |

30–50 for a 50-minute talk is the sweet spot for expert audiences with a
figure-heavy, visual-first style.

## Topic-aware structure selection (when `memory-publications` is installed)

Before picking a template, classify the paper(s) into one of the five research
threads defined in `memory-publications/references/research-index.json`:

1. `memory_theory_and_models` — behavioral/theoretical papers
2. `behavioral_economics_memory_decisions` — memory × decisions; mixed
   audience register
3. `eeg_oscillations` — intracranial or scalp EEG methods-heavy
4. `brain_stimulation` — closed-loop / open-loop stim; translational slant
5. `single_unit_recordings` — unit data; neurophysiology-heavy

The thread changes what "methods" means and therefore what slides are
load-bearing:

| Thread | Needs extra slides for | Can often cut |
|---|---|---|
| memory_theory_and_models | Model equations + schematic; fit procedure; parameter interpretation | Heavy methods detail |
| behavioral_economics_memory_decisions | Task paradigm diagram; cross-domain translation (econ ↔ psych); both-domain definitions | Long literature review |
| eeg_oscillations | Electrode coverage figure; frequency bands definition; referencing / preprocessing; IRASA if used | Behavioral design detail |
| brain_stimulation | Stim parameters (amplitude / freq / pulse width / duration / location); target selection; safety / artifact handling; classifier design if closed-loop | Pure behavioral controls |
| single_unit_recordings | Unit isolation criteria; anatomical localization; spike-sorting QC | Population-level decoding |

When `memory-publications` is absent, skip this step and use the generic
template.

## Single paper, expert audience (50-min talk, 30–40 slides)

Default for most requests. Maps one paper to ~35 slides covering the full
arc from motivation to implications.

| Section | Slides | Content |
|---|---|---|
| Title | 1 | Title, authors, institute, date |
| Outline | 1 | `\tableofcontents` |
| Motivation | 2–3 | Why this question matters; why existing answers are insufficient |
| Background | 2–3 | Prior work the audience should have in mind before the new result |
| Research question | 1 | Crisp statement of what the paper asks |
| Methods | 4–6 | Design, stimuli, participants, key analyses; one figure per subtlety |
| Results summary table | 1 | **Required for papers with >4 experiments/simulations.** Overview + novelty marking |
| Results deep-dives | 6–10 | 2–3 figures per core finding; `\novelbadge` novel mechanisms |
| Discussion | 3–4 | What this changes; how it connects to theory |
| Limitations | 1 | Honest constraints |
| **Conclusions** | 1 | **Required.** 3–5 bullets, one sentence each, restating the talk's claims in their final form. No new material. |
| **Next steps** | 1 | **Required.** 2–4 bullets on open questions, follow-up experiments, or the natural next paper. |
| Acknowledgments | 1 | Collaborators + funding |
| References | 1–2 | `[allowframebreaks]` handles overflow |

The **summary-table-then-deep-dive** pattern is the single biggest structural
improvement you can make to results sections. For a 13-figure paper like
CohenKahana2019, don't emit 13 results slides; emit 1 summary table + 3–4
deep-dives on the architecturally important findings. Demote the rest to
backup slides (use `\appendix` so they don't appear in the outline).

## Multiple papers, integrated theme

When the user says "our papers on X" and the papers share a framework,
interleave them by theme rather than isolating each.

| Section | Slides | Content |
|---|---|---|
| Title + outline | 2 | Introduce the unifying thread |
| Unifying motivation | 2–3 | The shared research program |
| Theme 1: phenomenon A | 4–6 | Evidence pulled from multiple papers |
| Theme 2: model / mechanism | 4–6 | " |
| Theme 3: implications / extensions | 4–6 | " |
| Synthesis | 3–5 | What the papers collectively claim; remaining puzzles |
| Acknowledgments + references | 2–3 | |

## Multiple papers, one-section-per-paper

Safer default when papers are less thematically unified or the user wants
parity across them.

| Section | Slides per paper |
|---|---|
| Title + outline | 2 |
| Paper 1: setup + key results | 6–8 |
| Paper 2: setup + key results | 6–8 |
| ... | |
| Comparison / synthesis | 3–5 |
| Acknowledgments + references | 2–3 |

## Lecture / teaching mode

Mimic the style of `BigData_ML_Lecture.pdf` (the CML lecture reference).

Characteristics:

- Explicit section divider slides (`\metroset{sectionpage=progressbar}` or
  inject an explicit `[plain]` divider frame per section)
- Equation-dense: numbered equations, derivations walked through explicitly
- More bullet-heavy than expert talks; each bullet is a single concept
- Heavier use of external figures (textbook covers, pedagogical diagrams)
- Links displayed inline verbatim for reference material
- Speaker notes shorter — the content on the slide IS the teaching material

Target length is longer (45–90 min = 30–60 slides) because the audience needs
time to work through each step.

## Audience tailoring

The audience radically changes which bridging material is needed.

### Memory scientists (default)
**Know:** free recall, recognition, cued recall; serial position, contiguity;
CMR / TCM formally; PEERS dataset; iEEG terminology.

**Don't know:** economic applications of memory; clinical translation
specifics.

**Tailoring:**
- Go deep on formal details, model parameters, simulation results
- Emphasize methodological innovations (multi-session designs, PEERS)
- Less need to define paradigms — focus on what's new
- Use `\novelbadge` to cut through the inherited-vs-new distinction
  quickly

### Neuroscientists
**Know:** EEG, intracranial recording, fMRI methodology, neural oscillations,
hippocampal function.

**Don't know:** may be less familiar with computational memory models (CMR,
TCM).

**Tailoring:**
- Lead with neural findings and work backward to behavioral constraints
- Emphasize T+A-G+ and its generalization across paradigms
- Courier paradigm bridges behavioral and neural approaches
- Closed-loop brain–computer interfaces as applications
- Brief CMR equations — cite Howard & Kahana 2002, Polyn et al.\ 2009
  but don't derive on the slide

### Behavioral economists
**Know:** prospect theory, AR(1) processes, rational expectations. Some
familiarity with CML work through Wachter & Kahana (2024, QJE), Charles (2024,
RFS).

**Don't know:** memory paradigms, retrieved-context theory formally, EEG
methodology.

**Tailoring:**
- Bridge list paradigms to financial markets, forecasting, belief formation
- Steady-state measurement critical; excess volatility (Shiller 1981) as
  an analog
- Portfolio allocation as metaphor for scientific resource allocation
- Cite papers they know: Shiller (1981), Samuelson (1969), Kahneman &
  Tversky

### Grad students
**Know:** general memory experimentation, basic CMR, the paper in question
at an introductory level.

**Don't know:** parameter-level details of the model; methodological
subtleties of older published work.

**Tailoring:**
- Slower pace on methods (4–6 methods slides, not 3)
- More careful terminology definition on first use
- One full worked example somewhere (CMR applied to a 4-item list is a
  classic)
- Speaker notes can assume they'll ask questions mid-talk

### Mixed audience (invited colloquium)
**Know:** varies widely; treat as lowest-common-denominator experts.

**Tailoring:**
- Lead with an accessible motivation (Ebbinghaus, Courier, autobiographical
  memory)
- Defer deep model equations to backup slides
- Spend more time on figures than on derivations
- Include one "here's how we do this experiment" methods slide for
  non-memory specialists

### General lay audience
**Know:** everyday experience with memory, general awareness of its
imperfection.

**Don't know:** essentially all technical content.

**Tailoring:**
- Start from everyday experiences; show how the lab captures them
- Use analogies freely; minimize jargon
- Focus on surprising findings and practical implications
- Courier paradigm is very accessible — everyone understands delivering
  packages

### Lecture / teaching
See the Lecture section above; audience assumes they'll work through
derivations with you.

## Slide plan data structure

`scripts/plan_deck.py` produces a deck plan as a JSON document before writing
any LaTeX. This lets the same plan feed both Beamer and PPTX generators.
Shape:

```json
{
  "title": "Memory Search: A Primer",
  "subtitle": "Retrieved Context Theory",
  "authors": ["Michael J. Kahana"],
  "date": "2024-10-15",
  "audience": "memory-scientists",
  "theme": "metropolis",
  "slides": [
    {"kind": "title", "content": null},
    {"kind": "outline", "content": null},
    {"kind": "section_header", "title": "Motivation"},
    {
      "kind": "content",
      "section": "Motivation",
      "title": "Why memory search matters",
      "bullets": ["Point 1", "Point 2"],
      "figure": null,
      "novelty": false,
      "notes": "Full 1--2 minute opening..."
    },
    {
      "kind": "figure",
      "section": "Results",
      "title": "Serial position effects",
      "figure": "figures/fig2_spc.pdf",
      "caption": "",
      "novelty": false,
      "notes": "Walk U-shape with specific numbers..."
    },
    {
      "kind": "summary_table",
      "section": "Results",
      "title": "Results summary",
      "rows": [
        ["Effect A", "Exp.~1", "pre-existing"],
        ["Effect B", "Sim.~2", "new"]
      ],
      "notes": "Orient before deep dives..."
    },
    {"kind": "references"}
  ],
  "bibliography_entries": ["kahana1996", "howard2002", "..."]
}
```

Supported `kind` values: `title`, `outline`, `section_header`, `content`,
`figure`, `columns`, `equation`, `summary_table`, `references`,
`acknowledgments`.

Keep the plan as a data structure, not mid-generation LaTeX. LaTeX is emitted
from the plan in one step by `beamer_generation.md`'s templates. Each slide
entry can have a `novelty: true` flag that tells the emitter to append
`\novelbadge` to the frame title.
