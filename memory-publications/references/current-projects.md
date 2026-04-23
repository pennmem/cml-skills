# Current Projects Reference

Last updated: March 17, 2026

This file provides project-specific context for each active manuscript. Stable
information (theoretical framing, author lists, file locations) persists across
sessions. The **Status** block at the top of each entry is the part that needs
regular updating.

---

## Journal Abbreviations

| Abbreviation | Full Name |
|---|---|
| JEP:LMC | Journal of Experimental Psychology: Learning, Memory, and Cognition |
| PR | Psychological Review |
| QJE | Quarterly Journal of Economics |
| MC | Memory & Cognition |
| JN | Journal of Neuroscience |
| NatComm | Nature Communications |
| CABN | Cognitive, Affective and Behavioral Neuroscience |
| TiCS | Trends in Cognitive Sciences |
| PNAS | Proceedings of the National Academy of Sciences |

---

## Priority Summary

| # | Short Name | Lead Author(s) | Target Journal | Status |
|---|---|---|---|---|
| 1 | DeHaan/Sileo | DeHaan, Sileo, Kahana | MC or JEP:LMC | Active — reanalyses + rewrite |
| 2 | Observational stim predictions | DeHaan, Halpern, Kahana | PNAS | Active — manuscript in progress |
| 3 | KahaFalk22 | Falkenburg, Broitman, Kahana | Intelligence | Active — full draft exists |
| 4 | Neural decoding of anticipation | J. Kahana, Lega, M.J. Kahana | JN | Active — full draft exists |
| 5 | SpectralTag | Broitman, Kahana et al. | TiCS | Active — review article |
| 6 | Memory & Forecasting | Wachter, Kahana et al. | TBD | On hold — manuscript complete |
| 7 | Phonological Similarity | Herrema, Kahana | JEP:LMC | Invited R2 |
| 8 | Herrema-Murdock Study | Herrema, Kahana | JEP:LMC | Invited revision |
| 9 | Intracranial Courier | Bruce, Tantry, Kahana | JN / CABN | Active — full draft exists |
| 10 | Spatial memory model | Herweg, Kahana | PR | Early stage |
| 11 | Multisite closed-loop stim | DeHaan, Chang, Ezzyat, Lega, Gross, Sperling, Aronson, Papanastasou, Kahana | JN | Active — results in progress |
| 12 | Open-loop stim (retrieval) | DeHaan, Sakon, Lega, Gross, Sperling, Kahana | JN | Early stage |

---

## Confirmed File Map (Box)

All projects live in `RESEARCH/KahanaOverleafLaTeX/` (folder ID: 371190112346).

| # | Folder Name | Folder ID | Current .tex | .tex File ID |
|---|---|---|---|---|
| 2 | observational_stim_predictions | 371192440442 | `main.tex` | 2165611787636 |
| 3 | KahaFalk22 | 371191180668 | `main.tex` | 2165607611557 |
| 4 | NeuralDecodingOfAnticipation | 371192516909 | `main.tex` | 2165611149337 |
| 5 | SpectralTag | 371191506589 | `main.tex` | 2165612644187 |
| 7 | Phonological Similarity and Recall Dynamics | 371191759108 | `revision2_JEPLMC.tex` | 2165611495072 |
| 8 | Herrema-MurdockStudy | 371191075070 | `KahaHerrMurdock.tex` | 2165615755104 |
| 9 | Intracranial Courier | 371191192144 | `main.tex` | 2165599230015 |
| 10 | A retrieved context model of human spatial memory | 371190232205 | `main.tex` (in subfolder HerwKahaSpatialModel) | 2165598879844 |
| 11 | Multisite closed-loop brain stimulation | 371191351037 | `main.tex` | 2165610851392 |
| 12 | RepFR2 - Brain stimulation during retrieval | 371190289951 | `main.tex` | 2165617731885 |

**Note on multiple .tex files:** Several projects contain archived versions
(`main_original_submission.tex`, `revision_JEPLMC.tex`, `Adams_version.tex`,
`jneurosci.tex`, etc.). The file listed above is confirmed as current.

---

## Project 1: DeHaan/Sileo/Kahana

### Status
- **Phase:** Reanalysis + rewrite. Riley DeHaan leads reanalyses on raw PEERS4
  data; writing follows the approved outline below.
- **What's done:** Section-by-section outline approved. Reframing from Sileo
  thesis to output-encoding / "thoughts become memories" framing agreed upon.
  No revised draft yet.
- **Next steps:** DeHaan conducts PEERS4 reanalyses (SPC, lag-CRP, PLIs with
  conditional probabilities, possibly semantic clustering). Then writing.
- **Blocking issues:** Waiting on DeHaan to begin/complete reanalyses.

### What the Paper Is About

Transforms a Sileo undergraduate thesis into a short empirical paper
(~4,000-6,000 words). Uses the PEERS4 dataset: 97 subjects across 24 sessions
of delayed free recall. Sessions 1-23 use the same word pool. Session 24
introduces lists that mix "old" words (studied and recalled across all prior
sessions) with "new" words (never seen in the experiment).

### Theoretical Framework

Framed around the "thoughts become memories" principle (Rafla et al.). Each act
of recall deposits a new memory trace via output encoding. Over 23 sessions,
these traces accumulate for old words, producing a dissociation: enhanced recall
and organization for old words, but elevated prior-list intrusions. Retrieval
reshapes long-term memory structure.

### Approved Outline

**Introduction (~4 paragraphs):** Free recall signatures -> Rafla and output
encoding across days -> the gap -> present study.

**Methods:** PEERS4 paradigm, session 24 design, 97 subjects (one excluded for
bug). Mixed-effects models matching Rafla et al.

**Results:** SPC, lag-CRP, PLIs (conditional probabilities per Zaromb et al.
2006 / Healey & Kahana 2014), possibly semantic clustering (Google News 300d
Word2Vec), possibly PFR.

**Discussion (~4 paragraphs):** Summary -> Rafla/output encoding -> limitations
-> future modeling directions. No TCM/CMR speculation.

### Conventions
- No computational modeling
- PLI analyses: conditional probabilities, not raw counts
- Benchmark against Rafla et al. for methods and style
- ~4,000-6,000 words

### Key Files
- Rafla et al.: `RaflEtal24.pdf` in project knowledge
- PEERS4 overview: `KahaEtal24.pdf` in project knowledge
- Original Sileo thesis: Box folder `SileoKaha18` (ID: 371191379045)

---

## Project 2: Observational Stimulation Predictions

### Status
- **Phase:** Active -- manuscript in PNAS format, introduction and results
  partially written, discussion incomplete.
- **Target journal:** PNAS

### What the Paper Is About

**Title:** "The subsequent memory effect largely reflects experimental structure
rather than endogenous mnemonic variability"

**Authors:** Riley D. DeHaan, David J. Halpern, Michael J. Kahana

Tests whether the SME primarily reflects internal brain state fluctuations or
behavioral effects of experimental stimuli (serial position, item identity).
377 intracranial EEG patients, delayed free recall. After adjusting for stimulus
features, neural activity still predicts recall but explains only an additional
1.4% of variance. Decomposes regional SMEs and finds widespread attenuation.

### Key Methods
- Random-effects behavioral models of recall (item, SP, list, subject, interactions)
- Ridge-penalized logistic regression classifiers for neural decoding
- Leave-one-session-out cross-validation
- Incremental prediction analysis: behavioral model vs. neural + behavioral
- Univariate SME across ROIs and frequencies with/without residualization

### LaTeX System
- PNAS format: `pnas-new` document class, two-column
- Bibliography: `\bibliography{local_bibliography,memlab}`

### Box Location
- Folder: `observational_stim_predictions` (ID: 371192440442)
- Current file: `main.tex` (ID: 2165611787636)

---

## Project 3: KahaFalk22 (Spectral SMEs and Memory Ability)

### Status
- **Phase:** Active -- full draft exists, appears near submission-ready.
- **Target journal:** Intelligence

### What the Paper Is About

**Title:** "Spectral Correlates of Encoding Distinguish Good from Poor Learners"

**Authors:** Ben Falkenburg, Adam Broitman, Michael J. Kahana

Tests whether spectral SMEs (TAG pattern) reflect stable individual differences
in mnemonic ability. >1.6 million encoding events from two PEERS datasets (~250
subjects). Key finding: better learners show attenuated SMEs, particularly under
demanding encoding conditions. Challenges the assumption that larger SMEs
reflect more effective encoding.

### Key Methods
- PEERS Exp 1 (immediate FR, 16 items, 151 subjects) and Exp 2 (delayed FR,
  24 items, 98 subjects)
- Tiling procedure (Li et al. 2024) to control serial position confounds
- Linear mixed-effects models separating within- and between-subject variance
- Session-level (state) and subject-level (trait) SME-recall correlations

### LaTeX System
- `apa6` document class with `apacite`

### Box Location
- Folder: `KahaFalk22` (ID: 371191180668)
- Current file: `main.tex` (ID: 2165607611557)

---

## Project 4: Neural Decoding of Anticipation

### Status
- **Phase:** Active -- full draft exists, Discussion needs expansion. Reviewer
  comments from Malach re: occipital gamma analysis noted in file.
- **Target journal:** JN

### What the Paper Is About

**Title:** "Neural Decoding of Anticipation"

**Authors:** Joseph M. Kahana, Bradley Lega, Michael J. Kahana

396 intracranial patients watching 10-second countdown videos before a memory
task. Theta power increases, gamma decreases, alpha spikes at countdown ticks.
Penalized regression reliably predicts time within the interval. Predictions
better for earlier intervals but exceed chance after excluding initial 2 seconds.

### Key Methods
- Morlet wavelet decomposition (30 log-spaced frequencies, 3-280 Hz)
- Regional analysis: frontal, temporal, hippocampal, parietal/occipital
- L1 (lasso) and L2 (ridge) regression, session-level cross-validation
- Sliding 5-second windows

### LaTeX System
- `apa7` document class with `apacite`

### Box Location
- Folder: `NeuralDecodingOfAnticipation` (ID: 371192516909)
- Current file: `main.tex` (ID: 2165611149337)

---

## Project 5: SpectralTag (TAG Review)

### Status
- **Phase:** Active -- review article for TiCS. `main.tex` is the current
  version; `TiCS_pre_submission.tex` and `Adams_version.tex` are earlier drafts.
- **Target journal:** TiCS

### What the Paper Is About

Review article arguing that the spectral TAG (T+A-G+) constitutes a composite
marker of mnemonic success. Synthesizes evidence on TAG's neurocognitive
processes, evaluates whether it reflects memory-specific mechanisms vs.
task-general attention/engagement, and examines sensitivity to age, cognitive
abilities, and task demands. Authors: Broitman, Kahana, et al.

### LaTeX System
- `apa6` document class with `apacite` and `natbib`
- Uses `memlab_v2.bib`

### Box Location
- Folder: `SpectralTag` (ID: 371191506589)
- Current file: `main.tex` (ID: 2165612644187)

---

## Project 6: Memory & Forecasting (Wachter & Kahana)

### Status
- **Phase:** On hold. Sections 1-3 revised. Experiment designs finalized.
  Sections 4-5 methods text needs revision.
- **Next steps (when resumed):** Revise Sections 4-5; compile .bib files;
  finalize Experiment 1 prediction figure.

### What the Paper Is About

Connects retrieved-context models (TCM/CMR) to economic forecasting. Forecasters'
overweighting of recent information arises from temporal context drift -- the
same mechanism producing the contiguity effect. Recency is emergent, not
parametric.

### Two Experiments
1. **Experiment 1 (Temporal drift):** Manipulates distractor duration. Ratio
   rule prediction. Between-subjects: forced encoding vs. passive; distractor
   type. Within-subject: variable duration [2, 12]s. rho in {0.6, 0.9}.
2. **Experiment 2 (Source reinstatement):** Alternating distractor-task trains.
   rho in {0.6, 0.7}. Forced encoding only. 60 trials. Template: Polyn et al.
   (2009).

### Conventions
- `natbib` with manual `\begin{thebibliography}` -- NOT biblatex
- Three `pdflatex` passes; check `grep -c "undefined" main.log` = 0
- Cross-disciplinary register: econ audience, explain memory concepts
- `\textcolor{olive}{...}` for tracked changes
- TikZ figures

### Key Files (project knowledge)
- `main.tex`, `exp2_final_design.md`, `power_final_exp2.py`, `fpr_by_rho.py`

### Key Files (Box, needed when resumed)
- `memlab.bib`, `memlab_additions.bib`, `econ.bib`
- `fig_ratio_rule_final.pdf`, `generate_ratio_rule_final.py`

---

## Project 7: Phonological Similarity and Recall Dynamics

### Status
- **Phase:** Invited R2 at JEP:LMC. Full revised manuscript exists.
- **Target journal:** JEP:LMC

### What the Paper Is About

**Title:** "Phonological Similarity and Recall Dynamics"

**Authors:** Haydn G. Herrema, Michael J. Kahana

Demonstrates that phonological similarity (alliteration and rhyme) organizes
free recall dynamics. PEERS Experiment 4 (127 subjects, 23 sessions, delayed
FR). Participants cluster recalls by shared first phoneme or last two phonemes.
Phonological clustering predicts recall. Phonological features induce PLIs and
ELIs. Phonological similarity interacts with temporal contiguity and semantic
relatedness to accelerate IRTs.

### Key Methods
- Binary phonological similarity (alliteration/rhyme) + continuous Jaccard index
- Novel phonological clustering score (PCS)
- Linear mixed-effects models for recall probability and IRT
- Controls: temporal lag, semantic similarity, output position, n correct recalls

### LaTeX System
- `apa7` with `apacite`

### Box Location
- Folder: `Phonological Similarity and Recall Dynamics` (ID: 371191759108)
- Current file: `revision2_JEPLMC.tex` (ID: 2165611495072)

---

## Project 8: Herrema-Murdock Study

### Status
- **Phase:** Invited revision at JEP:LMC. Full manuscript exists.
- **Target journal:** JEP:LMC

### What the Paper Is About

**Title:** "Recall initiation predicts intrusions in free recall"

**Authors:** Haydn Herrema, Michael J. Kahana

Replication of Murdock (1962) online (MTurk, 456 subjects, up to 5 sessions).
Six conditions varying list length (10-40) and presentation rate (1 or 2 s).
Unexpectedly symmetric SPCs explained by U-shaped PFR. Subjects partitioned
into primacy-initiators, recency-initiators, no-strategy. Key finding: strategy
does not affect total recall but profoundly affects dynamics -- primacy group
shows stronger temporal contiguity, higher intrusions, flat IRTs; recency group
shows stronger semantic clustering. Temporal and semantic organization
negatively correlate within the recency group.

### Key Methods
- Online typed auditory free recall (jsPsych/PsiTurk)
- 6 between-subject conditions: 10-2, 15-2, 20-1, 20-2, 30-1, 40-1
- Strategy classification: >2/3 primacy or recency initiation
- Lag-CRP, temporal/semantic clustering scores, IRT analysis

### LaTeX System
- `apa7` with `apacite`

### Box Location
- Folder: `Herrema-MurdockStudy` (ID: 371191075070)
- Current file: `KahaHerrMurdock.tex` (ID: 2165615755104)

---

## Project 9: Intracranial Courier

### Status
- **Phase:** Active -- full draft with behavioral and neural results.
- **Target journal:** JN or CABN

### What the Paper Is About

**Title:** "Neural and behavioral correlates of spatiotemporal memory
organization and recall"

**Authors:** Colin R. Bruce, Deepti K. Tantry, Michael J. Kahana

104 intracranial EEG patients in Courier virtual-town task. Subjects deliver
items to businesses and later recall items and locations. Shows spatial and
temporal clustering, spatial learning curves (pointing accuracy improves), and
spectral TAG during encoding/retrieval. SME survives serial position correction.

### Key Methods
- Courier task: 13 deliveries per day, then free recall (90 s)
- Temporal and spatial clustering (Euclidean distance)
- Pointing accuracy as spatial learning index
- Morlet wavelets, 3-128 Hz, 6 ROIs (CgC, MTL, LTC, OcL, PaL, PFC)

### LaTeX System
- `apa6` with `apacite`

### Box Location
- Folder: `Intracranial Courier` (ID: 371191192144)
- Current file: `main.tex` (ID: 2165599230015)

---

## Project 10: A Retrieved-Context Model of Human Spatial Memory

### Status
- **Phase:** Early stage. Model equations written, simulations planned, abstract
  is a stub. Extensive notes on benchmark phenomena but no results yet.
- **Target journal:** PR

### What the Paper Is About

**Title:** "A retrieved context model of human spatial memory"

**Authors:** Nora A. Herweg, Michael J. Kahana

Develops spatial-CMR (sCMR). Items and locations jointly represented in feature
vectors; context has item and location subregions with distinct drift rates.
Associative matrices have four quadrants (item-item, item-location, location-
item, location-location). Aims to account for spatial clustering, spatial
learning, cued recall of locations, and other spatial memory benchmarks.

### LaTeX System
- `apa` (older) with `apacite`; uses `memlab.bib` and `mendeley.bib`

### Box Location
- Folder: `A retrieved context model of human spatial memory` (ID: 371190232205)
- Subfolder: `HerwKahaSpatialModel` (ID: 371190596651)
- Current file: `main.tex` (ID: 2165598879844)

---

## Project 11: Multisite Closed-Loop Brain Stimulation

### Status
- **Phase:** Active -- methods written, results partially filled, data
  collection ongoing. Discussion empty.
- **Target journal:** JN

### What the Paper Is About

**Title:** "Multisite closed-loop brain stimulation"

**Authors:** Riley DeHaan, Woohyeuk Chang, Youssef Ezzyat, Bradley C. Lega,
Robert E. Gross, Michael R. Sperling, Joshua P. Aronson, Alexander
Papanastasou, Michael J. Kahana

Compares single-target vs. multi-target closed-loop stimulation during verbal
episodic memory. Classifiers trigger stimulation during encoding when poor memory
states detected. Lists assigned to single A, single B, multi A+B, or sham.
Tests additive vs. sub-additive vs. interfering effects.

### Key Methods
- Intracranial patients, delayed free recall
- Classifier-triggered stimulation (0.5 mA, 200 Hz)
- Three electrode-pair categories: both left temporal; left temporal + left
  prefrontal; left temporal + contralateral
- Delta-classifier analysis (post minus pre stimulation)

### LaTeX System
- `article` class with `jneurosci.sty`; `\bibliography{memlab}`

### Box Location
- Folder: `Multisite closed-loop brain stimulation` (ID: 371191351037)
- Current file: `main.tex` (ID: 2165610851392)

---

## Project 12: Open-Loop Stimulation During Retrieval

### Status
- **Phase:** Early stage. Title and author list set, structure exists, abstract
  empty, no results written.
- **Target journal:** JN

### What the Paper Is About

**Title:** "Brain stimulation during retrieval enhances memory performance"

**Authors:** Riley DeHaan, John Sakon, Bradley C. Lega, Robert E. Gross,
Michael R. Sperling, Michael J. Kahana

Open-loop (non-classifier-triggered) brain stimulation during retrieval in free
recall. Early stage -- structure exists but content is minimal.

### LaTeX System
- `article` class with `natbib` (cerebralcortex bibstyle currently)
- Bibliography: `\bibliography{memlab_local,memlab}`

### Box Location
- Folder: `RepFR2 - Brain stimulation during retrieval` (ID: 371190289951)
- Current file: `main.tex` (ID: 2165617731885)

---

## Submitted / Completed Manuscripts

### Jin et al. -- CMR-IA (Submitted to PR)

**Citation:** Jin, B. J., Halpern, D. J., Wachter, J. A., & Kahana, M. J.
*A theory of memory for items and associations.* Submitted to Psychological
Review.

Presents CMR-IA, a retrieved-context model for item and associative memory.
Eight simulations covering item recognition, associative recognition, and cued
recall. Two new experiments on successive tests. Key contributions: Gestalt
representation for paired associates, attention to rare items, variable
recognition thresholds, output encoding.

**LaTeX:** `apa7` with `apacite`. Custom math macros.
**Key file:** `JinEtalPsychReview.tex` in project knowledge.

---

## Next Steps for Skill Refinement (Deferred to Future Session)

1. **Psychological Review formatting and simulation-section guidance** -- PR
   coverage in `journal-formats.md` is thin. Need detailed PR expectations and
   guidance on writing simulation sections.

2. **Expand domain knowledge** -- `domain-knowledge.md` should cover CMR-IA
   and retrieved-context models applied to forecasting/finance.

3. **Align skill with actual working practices** -- Several SKILL.md sections
   default to `biblatex + biber` but most active manuscripts use `natbib` or
   `apacite`. Update sections 3 and 6.
