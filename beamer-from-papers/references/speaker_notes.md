# Speaker notes

Speaker notes are the actual content the presenter will deliver. They are not
terse reminders or tweet-length cues — they are 1–2 minutes of material per
slide, written so the presenter can glance at them and keep talking without
breaking flow.

**Test of adequate length:** can the speaker deliver a coherent 1–2 minute
block using only the note as reference? If the note is under ~300 characters
for a content slide, the answer is almost certainly no — expand it.

## What belongs in a speaker note

- Full narrative explanation of the slide's content — what it shows, why it
  matters, where it came from.
- Transitions to the next slide ("That brings us to...", "This sets up...").
- Key statistics the speaker will say aloud (effect sizes, sample sizes, CIs,
  p-values) with the values written out, not paraphrased.
- References the speaker might mention ("Howard \& Kahana, 2002, introduced
  this formalism"), inline so they can be read off quickly.
- Anticipated audience questions and short responses.
- Animation cues (`[CLICK]`) at the points where the slide advances overlays.

## What does NOT belong in a speaker note

- One-word reminders ("walk the figure") — too terse; useless under
  presentation pressure.
- A duplicate of what's already visible on the slide.
- Self-commentary about the slide design ("this slide is a bit busy") — cut
  those before shipping.

## Adapting `memory-publications/references/writing-style.md` when installed

If the `memory-publications` skill is installed, its `writing-style.md` extracts
Michael Kahana's writing voice across two registers: journal articles (Annual
Review, Nature Communications, JEP:LMC, Psych Review) and the textbook
*Foundations of Human Memory*. Speaker notes are a **third register** that
borrows from both without matching either. Specifically:

**Borrow from the textbook register**:
- "Consider..." as an invitation to engage
- Concrete running examples ("the classic word list house, shoe, tree, car...")
- Pedagogical signposting ("[CLICK] after showing the DFR comparison")
- Honest acknowledgment of what's not known

**Borrow from the journal-article register**:
- Precise terminology — use the domain's actual terms, never soften them to
  "memory processes"
- The "X, however, Y" pivot for contrasts
- Active "we" voice for work by the author's group
- Citations to load-bearing prior work inline ("Howard \& Kahana, 2002")

**Don't borrow from either**:
- Long embedded clauses with many commas (readable in print, not at-a-glance)
- Historical vignettes and classical quotations (textbook opener device; too
  slow for a note)
- Meta-scientific reflection (wrong scale for a slide)

**Words to reach for** (per writing-style.md §8): "accounts for", "gives rise
to", "by contrast", "benchmark", "embodies", "in the same manner that".
**Words to avoid**: "interestingly", "importantly", "robust" (as filler), "it
is worth noting that", excessive "novel".

When `memory-publications` is absent, fall back to the tone observed in the
AES 2017 notes (§"Observed patterns" below). Don't invent a voice — stay close
to what the real examples show.

## Observed patterns in real CML talks

Based on 16 real speaker notes from CML's `AES_2017.pptx`.

**Length**: substantive CML notes routinely run 300–800 characters.
Methodology-heavy slides can reach 1200+. Short notes (<100 chars) appear
only on section-header slides or pure visual slides where the speaker is
gesturing at a figure rather than reading.

**Tone**: First-person, conversational, as if writing to yourself. "Each
patient first performs several record-only sessions, with which we trained a
classifier..." not "The authors report that..."

**Structure**: typically opens with the point of the slide ("Ok so the first
thing I want to show..."), walks through the figure or data with specifics,
and ends with a transition to the next slide.

**Animation cues**: `[CLICK]` appears inline in notes when the slide has
animations. The skill should detect `\only`, `\uncover`, or similar Beamer
overlays and insert `[CLICK]` cues at the right points.

**Transition phrasing**: "Next I'll show...", "This sets up the next slide
where...", "That brings us to..." — appears on most transition slides.

**Self-references**: notes sometimes reference the paper being presented:
"Figure 2 of the Ezzyat 2017 Current Biology paper shows..." Keep this.
Audiences often ask "which paper is that from?" and having the reference in
the notes helps the speaker answer quickly.

## Tone examples by slide type

### Results slide with a figure
> Each patient first performs several record-only sessions, with which we
> trained a classifier to discriminate recalled and not recalled words.
> During the closed loop stimulation sessions, raw voltage was streamed
> through the model in real time. [CLICK] The classifier output determined
> when stimulation was delivered. We see here a 15\% boost in recall when
> stimulation arrives during low-performance states — a bigger effect than
> any open-loop comparison, and the first evidence that state-matched
> stimulation can exceed the best open-loop dose. Audience question to
> anticipate: does the effect hold for individual patients or only the
> group? Answer: 9 of 11 patients show the effect individually; the two
> that don't have the lowest baseline recall variability.

### Motivation slide
> Nearly all translational human memory research targets biomarkers of
> diseased memory — Alzheimer's, MCI, epilepsy-related impairment. But a
> common observation in our daily lives is that memory is highly variable
> within an individual: even patient populations with memory disorders show
> meaningful good and bad moments. That intraindividual variability is what
> we'll focus on today. If we can identify the neural signature of a
> good moment, stimulation can in principle be timed to coincide with bad
> moments — a within-subject intervention rather than a group-level one.

### Methods detail
> 100–200 electrodes implanted in a variety of brain regions, per patient.
> Patients monitored over ~2 weeks as part of their standard
> presurgical work-up. Our goal: identify biomarkers of good memory
> performance. We use a penalized logistic regression over spectral power
> in eight frequency bands at each electrode, fit on the record-only
> sessions, then validate on held-out stimulation sessions. The classifier
> output is a probability of recall; we threshold it to decide when
> stimulation fires.

### Transition / setup
> In these experiments, stimulation came on randomly with respect to brain
> state. Given the profound intraindividual variability in performance one
> would expect that stimulation is sometimes arriving during good states
> and sometimes during poor states — and the random-trigger data bears
> this out. This sets up the next slide's question: what happens if we
> only stimulate during low states?

## Generation guidance for the skill

When generating speaker notes for a slide, feed the LLM the following context:

1. **The slide's content**: title, bullets, figure path, caption
2. **Its position in the arc**: is this a setup slide, a results slide, a
   synthesis? What section?
3. **The paper's claim that this slide supports**: pull from `manifest.json` +
   the extracted section of the draft
4. **The previous and next slides**: so transition phrasing makes sense
5. **Figure vision output** (if a figure is present): the actual description
   of what the figure shows, not just its caption

Prompt the LLM to write in the CML voice described above — first person, full
1–2 minute content, includes specific numbers, inline citations to load-bearing
prior work, `[CLICK]` cues for animated overlays, and a transition phrase at
the end.

## Length calibration

| Slide kind | Target note length |
|---|---|
| Title | 0 — skip |
| Outline | 0 — skip or very short orientation |
| Section header | 100–300 chars — one paragraph framing the section |
| Content (bullets only) | 400–700 chars |
| Content (figure) | 600–1000 chars — walk through what the figure shows with specifics |
| Methods detail | 500–900 chars |
| Results headline | 700–1200 chars |
| Summary table | 400–700 chars — orient the audience, preview deep dives |
| Discussion / synthesis | 500–900 chars |
| References | 0 — skip |

These targets are **lower bounds for content slides**. A short note that says
the right thing beats padding, but a 100-char note on a results slide is
almost always insufficient under presentation pressure.

## Beamer note rendering

Use `\note{...}` after the frame content:

```latex
\begin{frame}{Serial position effects}
  \includegraphics[width=0.9\textwidth]{figures/fig2.pdf}
  \note{
    Classic U-shape with strong recency (last 3 items ~80\%) and weaker
    primacy (first 2 items ~40\%). The primacy gradient reflects stronger
    encoding of early list items, either from more frequent rehearsal
    (Rundus 1971) or more efficient initial attention (Sederberg et al.\
    2006). DFR attenuates recency but preserves primacy --- that's the
    setup for the next slide, where I'll contrast immediate and delayed
    free recall. Audience Q to anticipate: why doesn't primacy also
    attenuate with a filled delay? Short answer: in CMR, primacy is
    encoding-side and unaffected by delay, whereas recency is
    retrieval-side and attenuates as end-of-list context drifts away.
    [CLICK] here to bring in the DFR curve.
  }
\end{frame}
```

Escape `%` as `\%` and `&` as `\&` in notes — they're LaTeX too.

At the document level, the notes behavior is controlled by `\setbeameroption`:

- `\setbeameroption{hide notes}` — default; notes compiled but not visible
- `\setbeameroption{show only notes}` — produces a notes-only handout
- `\setbeameroption{show notes on second screen=right}` — dual-screen presenter
  mode

The skill's `compile_beamer.py --notes-only` flag handles the second case and
ships both PDFs alongside the deck.
