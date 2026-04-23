---
name: beamer-from-papers
description: >
  Build polished Beamer slide decks from CML paper bundles, following a visual-first,
  minimal-text philosophy. Draws figures and LaTeX source from `paper-acquisition`
  bundles, prefers TikZ recreations over `\includegraphics` for data figures, and
  compiles to PDF (with optional PowerPoint and notes-only PDF parallel outputs).

  Use this skill whenever a CML user mentions: slides, presentation, talk, Beamer,
  slide deck, lecture, seminar, keynote, colloquium, conference talk, invited talk,
  or asks to "make a presentation / build slides / a talk" about their own papers
  — even casually ("I have a talk coming up", "can you make me some slides from
  CohenKahana2019", "put together a presentation comparing our retrieved-context
  papers"). Also trigger when the user uploads a `.tex` with `\documentclass{beamer}`
  or references an existing deck for revision. The skill assumes papers are already
  staged as bundles by the `paper-acquisition` skill; if not, run that first
  transparently. Do NOT use this for general-purpose presentations unrelated to CML
  papers.
---

# beamer-from-papers

Build polished Beamer slide decks from CML paper bundles. The cardinal rule: **the
speaker provides the words. The slides provide the visuals.** Everything below
serves that principle.

## Relationship to other skills

**Upstream (required input).** This skill is the consumer of paper bundles produced
by `paper-acquisition`. Always run `paper-acquisition` first if bundles don't
already exist. If the user asks for a presentation without having run acquisition,
do that step transparently and report it — don't make them run two separate
commands when they asked for one thing.

**Lateral (optional enrichment).** If the `memory-publications` skill is installed,
consult three of its reference files to improve output quality. The skill works
without them — the fallback is generic academic voice and figure-caption-based
content — but the difference in output quality is substantial.

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
| `references/writing-style.md` | Speaker notes + slide bullet voice | `references/speaker_notes.md` tells you how to adapt it |
| `references/research-index.json` | Topic-aware deck structure | `references/presentation_structure.md` uses it to pick section patterns |

`memory-publications/references/current-projects.md` is primarily a
paper-acquisition concern (it maps short names to Box folders), but when one of
the user's active manuscripts is the subject of the talk, reading the project's
entry gives you target-journal context, lead-author list, and status that can
seed the title slide and acknowledgments.

**Do not duplicate** memory-publications content into this skill's references.
If it isn't installed, use the fallbacks described in the downstream reference
files.

For **manuscript-level work** (drafting papers, reviewer responses) use
`memory-publications` directly instead of this skill.

---

## Core design principles

Apply these preemptively, not after correction. They emerged from iterated
feedback across many presentations.

### 1. Cardinal rule — visuals on slides, content in notes
If you find yourself writing a paragraph on a slide, move it to `\note{}`. If you
find yourself writing prose that duplicates what an equation or diagram already
shows, delete the prose.

### 2. Aggressive text minimization
Users routinely ask for further text reduction across 2–4 rounds per slide. When
drafting, cut **30% more than your first instinct**:
- Equations + prose explanation → drop the prose (equations speak to experts).
- Diagram + caption explaining the diagram → drop the caption.
- Column text blocks: `\setstretch{0.95}` and `\vspace{4pt}` between paragraphs.
- Footer captions: one line. Two-line footers almost always clip.

### 3. TikZ-first for data figures
Prefer TikZ recreations over `\includegraphics` of publication figures for data
(bar graphs, scatterplots, line plots). Publication figures have multiple panels
sized for a static paper but overwhelming for a 30-second slide read. See
`references/visual_design.md` for TikZ patterns. Use `\includegraphics` only for:
complex multi-panel figures where simplification would distort the story,
photographs, schematics, and screenshots.

### 4. Recurring visual motifs
For talks with multiple parallel mechanisms, design one reusable visual and
toggle its emphasis across slides. Example: a memory-state diagram macro with
Items and Context boxes and two arrows ($M^{FC}$, $M^{CF}$) toggled `active`
(bold, colored) or `inactive` (thin, gray). Audience builds recognition;
architectural parallels become visible without prose. See
`references/visual_design.md`.

### 5. Summary-table-then-deep-dive
For papers with many simulations or experiments, avoid the "simulation parade"
(one figure slide per result). Instead: one summary table listing all results
with short phenomena + source + key mechanism, then 2–3 deep-dive slides on the
architecturally important ones. Matches how a presenter actually allocates time
(breadth-fast, depth-slow).

### 6. Mark novelty explicitly
When a talk involves both inherited and novel mechanisms, make the distinction
visible: a `\novelbadge` on slide titles for novel content, red text in summary
tables for mechanisms that depend on the new architecture, plain black for
pre-existing ones.

### 7. Test artifacts for risky redesigns
For risky changes (new table structure, new mechanism slide, reorganized
section), build a standalone `test_foo.tex` next to the deck that renders just
the new slides. Iterate on that isolated design, then drop the approved version
into the main deck. Faster than iterating in-deck with full-compile overhead.

### 8. Render-and-verify after every compile
`pdflatex` succeeds silently even when text overflows the slide boundary.
Clipping is the most common layout failure mode. After each batch of edits,
render changed slides to PNG and inspect:

```bash
pdflatex -interaction=nonstopmode deck.tex
pdftoppm -png -f N -l N -r 180 deck.pdf preview
```

`scripts/compile_beamer.py --render-preview N` wraps both steps. Fix clipping by
tightening `\arraystretch`, reducing `\vspace`, or cutting text.

### 9. Speaker notes carry the real content
Speaker notes should contain **what the presenter will actually say** — full
explanations with math, transitions, anticipated audience questions. Test: can
the speaker deliver a coherent 1–2 minute block using only the notes as
reference? If the notes are just terse reminders, they're too short.

### 10. Don't assume authors remember their own papers
When the user asks a factual question about their own manuscript ("is Sim 2b
about rearranged pairs or intact pairs?"), take it at face value. Look up the
answer in the source `.tex` or PDF and remind them with specifics. This is a
feature of working with busy researchers on past work, not a gap.

### 11. Prose hygiene (applies to every slide and every bullet)
Critiqued output across real CML decks shows four recurring issues. Apply
these preemptively:

1. **No em-dashes.** Not on slides, not in notes. Use a colon, a period, or
   parentheses instead. `—` and `---` are banned; `--` in LaTeX math is fine.
2. **No inline lists inside a sentence.** A sentence like *"Usual
   explanations: word frequency, concreteness, emotional valence, fatigue,
   time of day, sleep"* must be rewritten as:
   - A sub-bullet per item (when items are sentences or phrases), or
   - A single-line numbered inline list (when items are short words):
     *"1. word frequency 2. concreteness 3. emotional valence 4. fatigue
     5. time of day 6. sleep"*.
3. **No filler intensifiers.** Cut "fluctuates strikingly", "remarkably",
   "importantly", "interestingly", "it is worth noting that", "robust"
   (as filler). These are signals of weak content, not strong content.
4. **Slides never expose pipeline metadata.** Do not print the data source,
   build date, repo path, or any other internal metadata on the title slide.
   The title slide shows the talk title, authors, affiliation, and date.
   Nothing else.

### 12. Every deck ends with Conclusions and Next Steps
Two distinct frames (not one combined frame):

- **Conclusions** — 3–5 bullets restating the talk's claims in their final
  form. One sentence per bullet. No new material.
- **Next steps** — 2–4 bullets on what the lab does next, open questions,
  or the natural follow-up experiments.

Acknowledgments and References come after these two slides, not before.

---

## High-level workflow

1. **Session start protocol** — confirm inputs and elicit parameters (below).
2. **Deep reading** — text of each draft, figures with vision, `.bib` for
   citations. See `references/reading_strategy.md`.
3. **Propose outline, get approval** — numbered section outline with slide
   counts. Don't draft slides until the user approves.
4. **Draft in batches of 3–6 slides**, compile after each batch, render-verify
   for clipping. See `references/visual_design.md`.
5. **Polish pass** — tighten text (cut 30% more), insert `\novelbadge`s, flip
   section dividers off unless requested.
6. **Fact-checking pass** (separate, only after content is approved) —
   statistics, dates, citations against source papers. Collect discrepancies
   into a single report.
7. **Compile final PDF + notes-only PDF**, optional PPTX.
8. **Session-end manifest** — deliverables, pending items, Box file IDs, what
   to bring to the next session.

---

## Session start protocol

When the user invokes the skill without specifying details, ask the following in
a single turn (don't ping-pong). If the initial message already specified any,
skip those questions. If they say "just use defaults," use all defaults and
move on.

```
Building a presentation from <N> paper(s). Quick parameters:

1. Audience: [memory-scientists | neuroscientists | behavioral-economists |
              grad-students | mixed-audience | general-lay | lecture]
   Default: memory-scientists

2. Duration: [15-min / ~12 slides | 30-min / ~25 slides |
              50-min / ~35 slides | custom]
   Default: 50-min

3. Structure (multi-paper only): [one-section-per-paper | integrated-by-theme]
   Default: one-section-per-paper + comparison section at the end

4. Theme: [metropolis | Madrid | Cambridge]
   Default: metropolis  (clean, minimal; matches current CML talks)

5. Include speaker notes? (yes/no) — Default: yes
   Notes are the real content; budget 1–2 minutes of material per slide.

6. Output formats: [pdf-only | pdf+tex | pdf+tex+notes-pdf | pdf+tex+pptx]
   Default: pdf+tex+notes-pdf
```

For **any memory-related talk**, if `memory-publications` is installed, read its
`references/domain-knowledge.md` once before drafting — it locks down CMR-family
model provenance and terminology that will otherwise drift on slides.

Also check for an existing `.tex` file in the workspace and ask if continuing
from a prior session.

---

## Outline-approval checkpoint

Before generating any slide content, propose a numbered section outline with
per-section slide counts. Compile a title-slide-only PDF at this point so the
user sees the theme and metadata. Example:

```
Proposed outline (~35 slides):
  1. Title + outline (2)
  2. Motivation — why this matters (3)
  3. Retrieved-context background (4)
  4. Model: CMR3 (5)
  5. Results — summary table + three deep-dives (8)
  6. Clinical applications (5)
  7. Discussion + future directions (4)
  8. Acknowledgments + references (4)
Shall I draft, or revise the outline first?
```

---

## Deep reading

The user asked for "deepest possible reading." For each paper:

1. **Full text**: read `drafts/selected.tex` start to finish. If only a PDF
   exists, extract text via `pdftotext`.
2. **Figures with vision**: for each file in `figures/`, load it as an image
   and describe what it shows — not just the caption.
3. **Citations**: parse the `.bib` for entries that appear in the draft (via
   `\cite{}` keys). Build a working bibliography for the talk.

For multi-paper presentations, additionally identify shared methods / datasets,
shared theoretical framework, and points of agreement / disagreement.

See `references/reading_strategy.md` for the full procedure, including the
"don't assume authors remember" heuristic and the fact-checking pass.

---

## Planning the deck

Default outlines by scenario live in `references/presentation_structure.md`.
Quick summary:

- **Single paper, expert audience** — 30–50 slides for a 50-min talk, ≤20 for a
  15-min slot. Includes a summary-table slide before deep-dives when there are
  many simulations or experiments.
- **Multiple papers** — either one section per paper (safer) or integrated by
  theme (more ambitious). Always include a comparison/synthesis section.
- **Lecture / teaching mode** — different beast; equations, derivations, more
  bullets, longer. Mirrors `BigData_ML_Lecture` style.

See `references/presentation_structure.md` for full tables, plus the
**audience tailoring** section for what to bridge to for behavioral economists,
neuroscientists, and general audiences.

---

## Generating the Beamer source

Use `assets/cml_beamer_template.tex`. Defaults:
- `\documentclass[aspectratio=169,11pt]{beamer}`
- `\usetheme{metropolis}` with `\metroset{sectionpage=none}` (suppress dividers)
- Madrid + CML navy blue available as a one-line swap for users who want the
  older CML house style.

The template exposes the standard metadata plus a `\novelbadge` macro and a
`\memorydiagram` motif template. See `references/beamer_generation.md` for
per-slide patterns (visual-first, summary tables, equation slides, novelty
marking).

Figures get copied from each bundle's `figures/` directory into a local
`figures/` alongside the `.tex`. Use relative paths in `\includegraphics`. For
data figures that would need simplification, **recreate in TikZ instead**.

Citations use `\cite{}` against a `references.bib` built from the union of all
papers' bibs (deduped by cite key).

---

## Speaker notes

Speaker notes carry the real content — 1–2 minutes of material the presenter
will deliver, not 100-character reminders. Use Beamer's `\note{}`:

```latex
\begin{frame}{Serial Position Effects}
  \includegraphics[width=0.9\textwidth]{figures/fig2_spc.pdf}
  \note{
    Classic U-shape with strong recency (last 3 items ~80\%) and weaker
    primacy (first 2 items ~40\%). The primacy gradient reflects stronger
    encoding of early list items, either because of more frequent rehearsal
    (Rundus 1971) or more efficient attention during initial presentation
    (Sederberg et al.\ 2006). DFR attenuates recency but preserves primacy —
    that's the setup for the next slide, where I'll contrast immediate and
    delayed free recall. Audience Q to expect: why doesn't primacy also
    attenuate with a filled delay? Short answer: it depends on which model;
    in CMR, primacy is encoding-side and unaffected by delay, whereas recency
    is retrieval-side and attenuates as end-of-list context drifts away.
  }
\end{frame}
```

Compile twice: once with `\setbeameroption{hide notes}` for the talk-facing
PDF, once with `\setbeameroption{show only notes}` for a notes-only printable
version. Ship both. `compile_beamer.py --notes-only` handles the second pass.

See `references/speaker_notes.md` for tone, voice, and register guidance.

---

## Compiling

Primary: `pdflatex -interaction=nonstopmode` → `bibtex` → `pdflatex` →
`pdflatex`. Three pdflatex passes handle TOC + citations + cross-refs.

Use `scripts/compile_beamer.py`:
- Wraps all passes, filters the log, surfaces actionable errors only.
- `--render-preview N` or `--render-preview N-M` renders the named slides to PNG
  with `pdftoppm` at 180 DPI for visual clipping inspection.
- `--notes-only` flips `\setbeameroption` and produces a notes-only PDF.
- `--skip-bib` skips the bibtex pass.

**Always render-verify after a batch of slide edits.** If LaTeX isn't
installed, the script surfaces a clear error pointing to
`references/latex_setup.md`.

---

## PPTX output

**Native generation** via `python-pptx` — **not** a Beamer→PPTX conversion
(those look terrible). Build the same slide plan with the same figures / text /
notes, but emit `.pptx` directly.

See `references/pptx_generation.md` and `scripts/generate_pptx.py` if present.

---

## Fact-checking (separate pass)

Only after the user has approved slide content:
- Verify statistics, dates, citations against source papers in the bundle.
- Collect discrepancies into a single report for the user.
- Do not spend time verifying slides the user may still cut.

The verification report is a plain-text doc next to the deck; don't edit the
deck directly without user confirmation.

---

## Reporting results (session-end manifest)

When done, tell the user:

- **Current files**: compiled PDF, `.tex` source, notes-only PDF, optional
  `.pptx`.
- **Slide count and rough timing estimate** (60s expert / 90s grad /
  120s lecture).
- **Pending items**: figure placeholders still needing insertion (with source
  paths), unverified quotes or statistics, slides needing speaker notes, any
  decisions deferred to the user.
- **Compilation warnings**: missing figures, unresolved citations, clipped
  slides flagged by render-verify.
- **Files needed for next session** — what to bring.

Keep the prose short. The user can open the artifacts themselves. End with a
one-line prompt inviting revision.

---

## Reference files

- `references/reading_strategy.md` — deep reading with vision + fact-checking
- `references/presentation_structure.md` — default outlines + audience tailoring
- `references/beamer_generation.md` — LaTeX generation patterns
- `references/visual_design.md` — TikZ-first data figures + recurring motifs +
  test-artifact workflow
- `references/speaker_notes.md` — tone, length, register
- `references/pptx_generation.md` — python-pptx parallel output (if present)
- `references/latex_setup.md` — troubleshooting missing LaTeX / beamer class /
  fonts

## Assets

- `assets/cml_beamer_template.tex` — starter template (metropolis default, CML
  macros, Madrid fallback)
- `assets/example_single_paper_deck.tex` — reference for single-paper structure
- `assets/examples/` — paired before/after generators showing how the rules
  translate into LaTeX. `build_decks_v1_original.py` is pre-critique output;
  `build_decks_v2_refined.py` applies §11-12 + visual_design.md rules. Read
  the README there and use these as regression fixtures when editing the
  skill.

## Scripts

- `scripts/compile_beamer.py` — compile passes + error filtering +
  render-and-verify preview
- `scripts/plan_deck.py` — builds the slide-plan data structure from bundles +
  parameters
- `scripts/generate_pptx.py` — native PPTX emitter parallel to Beamer (if
  present)
