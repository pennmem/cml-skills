# Speaker notes

The tone and length of speaker notes should match what a scientist would actually write for themselves before giving a talk — not a script, not a summary, but a reminder of the narrative beat and the specific points to hit.

This reference uses 16 real speaker notes from CML's `AES_2017.pptx` as calibration data.

## Observed patterns in real CML talks

**Length**: Most substantive notes run 100-400 characters. The longest goes to ~1200 characters on methodology-heavy slides. Short notes (under 50 chars) are rare — when they appear, they're bullet-point reminders rather than prose.

**Tone**: First-person, conversational, as if writing to yourself. "Each patient first performs several record-only sessions, with which we trained a classifier..." not "The authors report that..."

**Structure**: Typically opens with the point of the slide ("Ok so the first thing I want to show..."), walks through the figure or data, and sometimes flags the transition to the next slide.

**Animation cues**: `[CLICK]` appears inline in notes when the slide has animations. Use this convention — the skill should detect `\only`, `\uncover`, or similar Beamer overlays and insert `[CLICK]` cues into notes at the right points.

**Transition phrasing**: "Next I'll show...", "This sets up the next slide where...", "That brings us to..." — these appear on most transition slides.

**Self-references**: Notes sometimes reference the paper being presented: "Figure 2 of the Ezzyat 2017 Current Biology paper shows..." Keep this. Audiences often ask "which paper is that from?" and having the reference in the notes helps the speaker answer quickly.

## Tone examples by slide type

### Results slide with a figure
> Each patient first performs several record-only sessions, with which we trained a classifier to discriminate recalled and not recalled words. During the closed loop stimulation sessions, raw voltage was streamed through the model in real time. [CLICK] The classifier output determined when stimulation was delivered.

### Motivation slide
> Nearly all translational human memory research targets biomarkers of diseased memory. But a common observation in our daily lives is that memory is highly variable within an individual. Even patient populations with memory disorders show meaningful good and bad moments.

### Methods detail
> 100-200 electrodes implanted in variety of brain regions. Patients monitored for ~2 weeks. Identify biomarkers of good memory performance.

### Transition / setup
> In these experiments, stimulation came on randomly with respect to brain state. Given the profound intraindividual variability in performance one would expect that stimulation is sometimes arriving during good states and sometimes during poor states. This sets up the question for the next slide: what happens if we only stimulate during low states?

## Generation guidance for the skill

When generating speaker notes for a slide, feed the LLM the following context:

1. **The slide's content**: title, bullets, figure path, caption
2. **Its position in the arc**: is this a setup slide, a results slide, a synthesis? What section?
3. **The paper's claim that this slide supports**: pull from `manifest.json` + the extracted section of the draft
4. **The previous and next slides**: so transition phrasing makes sense
5. **Figure vision output** (if a figure is present): the actual description of what the figure shows, not just its caption

Prompt the LLM to write in the CML voice described above — first person, 100-300 chars, includes specifics, flags animations if present.

## Length calibration

| Slide kind | Target note length |
|---|---|
| Title | 0 — skip |
| Outline | 0 — skip or very short orientation note |
| Section header | 50-150 chars — one sentence framing the section |
| Content (bullets only) | 100-250 chars |
| Content (figure) | 200-500 chars — walk through what the figure shows |
| Methods detail | 200-400 chars |
| Results headline | 300-600 chars |
| Discussion / synthesis | 200-400 chars |
| References | 0 — skip |

Don't pad. A 80-char note that says the right thing beats a 300-char note that wanders.

## Beamer note rendering

Use `\note{...}` after the frame content:

```latex
\begin{frame}{Serial position effects}
  \includegraphics[width=0.9\textwidth]{figures/fig2.pdf}
  \note{Classic U-shape with strong recency (last 3 items ~80\%)
        and weaker primacy (first 2 items ~40\%). Mention that DFR
        attenuates recency as setup for next slide on distractors.
        [CLICK] after showing the DFR comparison.}
\end{frame}
```

Escape `%` as `\%` and `&` as `\&` in notes — they're LaTeX too.

At the document level, the notes behavior is controlled by `\setbeameroption`:

- `\setbeameroption{hide notes}` — default; notes compiled but not visible
- `\setbeameroption{show only notes}` — produces a notes-only handout
- `\setbeameroption{show notes on second screen=right}` — dual-screen presenter mode

The skill's `compile_beamer.py --notes-only` flag handles the second case.
