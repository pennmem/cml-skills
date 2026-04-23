# Content selection

This is where posters differ most from slide decks. A 25-slide talk walks the audience through your argument. A poster has to deliver the argument without you standing next to it — a viewer stops for 30 seconds to 3 minutes and either decides to read more or moves on.

The right mental model is **"a newspaper front page", not "a condensed paper"**. You're selling a story, not summarizing literature.

## Target word count

For a 48×36 landscape poster, total body text including all block content should run **300–600 words**. For 36×48 portrait, 250–500 words. If you're over these numbers, you haven't cut enough. Viewers will skim section headings and figures, read captions, and dip into body text only when something catches them.

## The six blocks

Every poster has exactly six content blocks. Do not invent more.

### 1. Motivation / problem (40–80 words)

Answer: **why should I, the viewer, care?** Lead with the phenomenon or puzzle, not with a literature review. One good rhetorical move: open with a concrete observation the viewer has experienced themselves, then state why it's scientifically unresolved.

*Bad (too much lit review):*
> Retrieved context models (Howard & Kahana, 2002; Polyn et al., 2009) propose that...

*Better (leads with the phenomenon):*
> When we recall a list of words, what we just retrieved shapes what comes next. This contiguity effect is one of the most reliable findings in memory research — but its theoretical basis remains contested.

### 2. Question / hypothesis (single sentence, optional standalone block)

If the paper has a crisp one-sentence research question, put it in its own box with visual emphasis. If it doesn't, fold it into the motivation block.

*Example:*
> **Does context reinstatement during retrieval drive the forward asymmetry in lag-CRP curves?**

### 3. Methods (50–100 words + one schematic figure)

For behavioral papers: task structure, participant N, key DVs. For neural papers: recording modality, N subjects, electrode coverage, analysis approach. Prefer a design schematic figure with callouts to a prose description. If the schematic is self-explanatory, text can shrink to 1–2 sentences naming the task and the sample.

Cut from methods:
- Stimulus frequency/concreteness norms (unless they're the story)
- Participant demographics beyond N and a one-line summary
- Every analysis the paper ran — only the ones that produced the poster's figures
- IRB statement (goes in acknowledgments if anywhere)

### 4. Results (3–5 blocks, each: one figure + 30–80 words)

**This is most of the poster.** Pick 3–5 figures that carry the argument. See `figure_selection.md` for how to pick. For each figure:

- A block heading that states the takeaway, not the method ("Strong forward bias in lag-CRPs" not "Lag-CRP analysis")
- The figure itself, large enough to read at 4-6 feet
- A short caption (30–80 words) that tells the viewer what to notice and what it means — don't just repeat the caption from the paper

*Bad block heading:* "Conditional response probability as a function of lag"
*Good block heading:* "Forward transitions 2× more likely than backward"

### 5. Conclusions (3–5 bullets, each a complete sentence)

Not "takeaways" or "implications" — **conclusions**. Each bullet should be a complete declarative sentence that states something the paper has shown. Avoid hedging unless genuinely warranted.

*Example:*
- Context reinstatement produces asymmetric contiguity effects at all lags tested.
- CMR with bidirectional associations accounts for the asymmetry quantitatively.
- The asymmetry is preserved in continual-distractor recall, arguing against short-term buffer explanations.

Do **not** include:
- Future directions (belongs in the talk, not the poster — at conferences they clutter)
- Limitations (ditto; discuss them in person if asked)
- A restatement of the question
- Vague claims ("This work advances our understanding of memory")

### 6. References + acknowledgments (compact footer)

A single block at the bottom or in the last column:

- **References**: 4–8 citations, cited inline in the poster by superscript number. Full references in a compact footer. If the paper has 80 citations in its `.bib`, the poster gets 6.
- **Acknowledgments**: 1–2 sentences. Funding sources (NIH grant numbers), key collaborators not in authorship. If the poster is from a DARPA-funded or NIH-funded project, include the grant number — reviewers check.
- **Contact**: email + optional QR code linking to the full paper, preprint, or lab page.

## What to cut (checklist)

Go through the paper and cut aggressively:

- [ ] All literature review beyond 1–2 sentences in motivation
- [ ] All methodological details not load-bearing for the results shown
- [ ] All control analyses and replication checks (flag on request, don't display)
- [ ] All supplementary / robustness figures
- [ ] Sub-panel figures where only one panel carries the story — show just that panel
- [ ] Discussion paragraphs that don't become conclusion bullets
- [ ] Caveats and limitations (discuss in person)
- [ ] Future directions
- [ ] Restatements of the same finding in different terms

## When the paper has multiple findings

If the paper makes 3 or more distinct claims, you have two options:

1. **Pick the most important one and build the whole poster around it.** Mention the others in a single conclusion bullet. This produces a tighter, more memorable poster.
2. **Build the poster around the integration.** Works when the claims are tightly coupled — e.g., "three different tasks all show the same pattern." One results block per task, shared conclusion block.

Don't try to give equal weight to 3+ independent claims on a single page. It doesn't fit and the viewer walks away unable to state what you found.

## Multi-paper posters

Multi-paper posters are unusual in CML (conferences generally prefer one paper per poster), but they happen — e.g., a thesis-defense poster covering multiple chapters. Use one results column per paper, shared motivation and conclusions. Target ≤ 3 papers; beyond that, the poster can't hold them.

## When `memory-publications` is installed

Cross-check your selected content against `memory-publications/references/writing-style.md`:

- Motivation blocks should follow Kahana's "lead with phenomenon, not lit review" pattern (see §1 of that file)
- Conclusion bullets should use his direct-assertion register, not hedged academic prose (see §5)
- Avoid the vocabulary listed in §8 as "words to avoid" — "interestingly", "importantly", "it is worth noting that", "novel", "robust" as a filler intensifier

When absent, the guidance in this file stands on its own — it was calibrated against Kahana's published abstracts and the AES 2017 talk.
