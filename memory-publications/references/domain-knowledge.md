# Domain Knowledge: Human Memory & Cognitive Neuroscience

This reference covers the theoretical frameworks, terminology, and methodological conventions used in the field. Consult when drafting or reviewing manuscripts to ensure precision. **Content is drawn from the user's own publications and active manuscripts — always verify specific claims against the source text before drafting.**

## Table of Contents
1. Core Theoretical Frameworks
2. Key Behavioral Phenomena
3. Neural Mechanisms & Methods
4. Spectral TAG Framework
5. Closed-Loop Brain Stimulation
6. Statistical & Modeling Conventions
7. Terminology Guide

---

## 1. Core Theoretical Frameworks

### Retrieved Context Models

The retrieved context framework is the dominant computational theory of episodic memory in the free recall tradition. The central idea: as items are encoded, they become associated with a gradually evolving temporal context representation. At retrieval, recalling an item reinstates its associated context, which then cues the next recall.

**Key models in this family:**

- **TCM (Temporal Context Model)** — Howard & Kahana (2002). Introduced the idea that temporal context drifts during encoding and is reinstated during retrieval. Context evolves via: the currently active item retrieves its previous contextual states via M^FC, which serves as input to the context evolution equation. Explains the contiguity effect and temporal clustering.

- **CMR (Context Maintenance and Retrieval)** — Polyn, Norman, & Kahana (2009). Extended TCM with source context features (e.g., encoding task), a competitive retrieval mechanism (Luce choice rule over activations), and pre-experimental semantic associations. Accounts for temporal, semantic, and source clustering simultaneously.

- **CMR2** — Lohnas, Polyn, & Kahana (2015). Added mechanisms for prior-list intrusions and inter-list context carryover. Key for understanding errors and interference across lists.

- **eCMR (Emotional CMR)** — Talmi et al. (2019). Extends CMR to handle emotional arousal effects on memory, including emotional clustering and enhanced recall of emotional items.

- **CMR-IA (CMR for Items and Associations)** — Jin, Halpern, Wachter, & Kahana (submitted to Psych Review). Extends retrieved-context theory to item recognition, associative recognition, and cued recall. Key innovations:
  - **Gestalt associative representation**: Paired associates are encoded by summing their feature vectors (F_i = F_{i_1} + F_{i_2}) and associating the composite with a single context state. This produces associative symmetry naturally.
  - **Item recognition via context similarity**: A test probe retrieves its encoding context via M^FC; if the similarity between this retrieved context and the current context exceeds a threshold (c^item_thresh), the model responds "old."
  - **Associative recognition**: The first item in a test pair reinstates its context, updating the current context; the model then compares this updated context with the context retrieved by the second item. This extra reinstatement step is why associative information is forgotten more slowly than item information (Hockley, 1992).
  - **Cued recall**: The cue item reinstates its context, which then cues retrieval of items via M^CF, as in free recall.
  - **Attention to rare items**: Parameter ψ boosts encoding of low-frequency words in M^FC, accounting for the word-frequency mirror effect.
  - **Variable recognition thresholds**: c^item_thresh adjusts dynamically based on exponentially weighted average of previous context similarities.
  - **Output encoding**: Recognized items and recalled items update M^FC and M^CF during test. Essential for explaining correlations between successive memory tests (Tulving-Wiseman relation).
  - Eight simulations covering: continuous recognition (recency × similarity), contiguity in item/associative recognition, differential forgetting, word frequency effects, serial position in cued recall, associative symmetry, PLIs/ILIs in cued recall, and similarity effects.

- **sCMR (Spatial CMR)** — Herweg & Kahana (in preparation, targeting Psych Review). Extends CMR to human spatial memory. Key innovations:
  - **Joint item-location feature vectors**: f = f^item ⊕ f^location, with corresponding context subregions c = c^item ⊕ c^location.
  - **Distinct drift rates**: β_enc^item and β_enc^location govern how quickly item and spatial context evolve.
  - **Four-quadrant associative matrices**: M^FC and M^CF each have item-item, item-location, location-item, location-location quadrants with independent learning rates.
  - **Pre-experimental spatial knowledge**: Location-location quadrants initialized as identity matrices (no prior spatial knowledge); item-item quadrants incorporate semantic similarity via word2vec.
  - **Target phenomena**: Spatial clustering in free recall (Miller et al., 2013), spatial learning curves, shortcuts, boundary effects, pointing accuracy, temporal-spatial clustering interplay.

**Core parameters in CMR-family models:**
- β_enc (encoding drift rate), β_rec (retrieval drift rate), β_cue (cue drift rate, CMR-IA), β_distract (distractor drift rate)
- γ_FC, γ_CF (learning rates for item-to-context and context-to-item associations)
- s (semantic scaling): weight of pre-experimental semantic associations
- φ_s, φ_d (primacy scaling parameters)
- κ, λ, η (accumulator parameters): decay, lateral inhibition, noise
- c^item_thresh, c^assoc_thresh (CMR-IA recognition thresholds)
- ψ_s, ψ_c (CMR-IA attention parameters)

### Dual-Store / Buffer Models

- **SAM (Search of Associative Memory)** — Raaijmakers & Shiffrin (1981). Historically important but largely superseded by retrieved context models for free recall.

### Complementary Learning Systems (CLS)

- McClelland, McNaughton, & O'Reilly (1995). Hippocampus supports rapid, pattern-separated encoding; neocortex supports slow, overlapping statistical learning.

---

## 2. Key Behavioral Phenomena

### Free Recall

- **Serial Position Effect**: U-shaped recall probability — primacy and recency. Delayed free recall attenuates recency.
- **Contiguity Effect**: Transitions to nearby serial positions. Measured by lag-CRP. Peak at lag +1 with forward asymmetry. Forward transitions ~2× more likely than backward.
- **Temporal Clustering Score**: 0 to 1, chance = 0.5.
- **Semantic Clustering**: Transitions between semantically related items (word2vec, LSA).
- **Phonological Clustering** (Project 7): Clustering by shared phonemes. Novel PCS measure. Interacts with temporal contiguity and semantic relatedness.
- **Spatial Clustering** (sCMR): Items from nearby locations recalled together (Miller et al., 2013).
- **Prior-List Intrusions (PLIs)**: Probability decreases with list recency. CMR2 models this. Project 1 uses conditional probabilities per Zaromb et al. (2006) / Healey & Kahana (2014).
- **Extra-List Intrusions (ELIs)**: Recalls of never-presented items.
- **Probability of First Recall (PFR)**: Strong recency in immediate FR. Project 8: U-shaped PFR produces symmetric SPCs.
- **Output Encoding**: Each recall deposits a new trace. Central to Project 1 — "thoughts become memories" (Rafla et al.).

### Recognition Memory

- d', A_z, ROC curves, Remember/Know paradigm
- **Word frequency mirror effect**: Higher hit rate AND lower false alarm rate for rare words (Lohnas & Kahana, 2013)
- **Differential forgetting**: Items forgotten faster than associations (Hockley, 1992)

### Paired Associates / Cued Recall

- **Associative symmetry**: Forward = backward cued recall (Kahana, 2002). Constrains models.
- **Successive testing**: Yule's Q measures dependency between successive tests (Kahana, 2000).
- **ILIs in cued recall**: Show contiguity and similarity effects (Davis et al., 2008).

---

## 3. Neural Mechanisms & Methods

### Intracranial EEG (iEEG / ECoG)

**Recording context**: Epilepsy patients. Electrodes placed clinically. Coverage varies.

**Electrode types**: Depth (sEEG) for hippocampus/deep structures; Subdural grids/strips (ECoG) for cortical surface.

**Signal processing:**
- Bipolar re-referencing standard
- Frequency bands: Delta (1-3), theta (3-8), alpha (8-12), beta (12-30), gamma (30-100+). Always specify boundaries.
- Morlet wavelets or multitaper decomposition
- HFA (70-200 Hz): Proxy for local firing
- IRASA: Separates narrowband oscillations from broadband (1/f) activity. Critical for isolating true theta.

**Key findings:**
- Theta increases during successful encoding (Sederberg et al., 2003)
- Spectral tilt: increased HFA, decreased LFA for successful encoding (Burke et al., 2013)
- Theta-gamma coupling (Lega et al., 2016)
- Traveling theta waves along hippocampal long axis (Zhang & Bhatt et al., 2024)

### Scalp EEG

Used in PEERS studies (Projects 3, 5). Same oscillatory phenomena, more volume conduction. Tiling procedure (Li et al., 2024) controls serial position confounds.

---

## 4. Spectral TAG Framework

**Central to Project 5 (SpectralTag review, TiCS) and Project 3 (KahaFalk22, Intelligence).**

### Definition

TAG = T+A-G+: increased low Theta (~3 Hz), decreased Alpha (~10 Hz), increased Gamma (>40 Hz) accompanying successful episodic memory encoding and retrieval. Term introduced by Katerman et al. (2021).

### TAG During Retrieval

- Gamma increases in bilateral hippocampus and cortex preceding successful recall (Sederberg et al., 2007)
- Widespread alpha decreases (Burke et al., 2014/2015)
- Low-theta (2-4 Hz) increases, especially after IRASA broadband removal (Rudoler et al.)
- Mid-theta can be occluded by strong alpha decreases
- Scalp replication: Katerman et al. (2022) — TAG predicts recall after >18-hour delays

### TAG During Encoding (SME)

- Full TAG at individual electrodes (Sederberg et al., 2003)
- Alpha decreases + gamma increases replicated in large samples (Burke et al., 2014)
- Theta increases elusive unless: (a) focusing on lowest frequencies (Lin et al., 2017) or (b) using IRASA (Rudoler et al.)
- **Subsequent clustering effect (SCE)**: Encoding gamma/HFA greater for items later recalled in temporally clustered manner — suggests gamma indexes item-context binding (Long & Kahana, 2014, 2016)

### Individual Differences (Project 3)

- Better learners show attenuated SMEs, especially under demanding conditions
- Challenges assumption that larger SMEs = more effective encoding
- Session-level (state) vs. subject-level (trait) SME-recall correlations
- >1.6 million encoding events, ~250 subjects, two PEERS datasets

### TAG and Sharp-Wave Ripples

- Encoding: SWRs support associative links, not individual item recall (Sakon et al., 2023; Vaz et al., 2019)
- Retrieval: Ripples increase before successful recall (Sakon & Kahana, 2022)
- Ripples (70-200 Hz) overlap with gamma range but coordinate broader network reactivation

---

## 5. Closed-Loop Brain Stimulation

**Central to Projects 2, 11, 12, and Nia Therapeutics (SNS).**

### Open-Loop vs. Closed-Loop

- **Open-loop (Project 12)**: Stimulation regardless of brain state. During retrieval period.
- **Closed-loop**: Classifier-triggered stimulation at optimal moments. State-dependent effects: stimulating during poor encoding improves memory; during good states, can impair (Ezzyat et al., 2017, 2018).

### Multisite Stimulation (Project 11)

Design: Lists assigned to single-target A, single-target B, multi-target A+B, or sham.

Three predictions: (1) Additive — independent effects across subnetworks; (2) Sub-additive — overlapping mechanisms; (3) Interfering — one target conflicts with the other.

Electrode categories: (1) both left temporal, (2) left temporal + left prefrontal, (3) left temporal + contralateral.

Key analyses: Delta-classifier (post-stim minus pre-stim), univariate SME at MTL, linear mixed-effects models at item level.

### SME Decomposition (Project 2)

377 iEEG patients. Behavioral models of recall: serial position, item identity, list, subject, interactions. Subject-item interactions explain substantial variance. Neural classifiers add only ~1.4% additional variance after behavioral controls. Univariate SMEs attenuated but remain significant after residualization.

### Stimulation Parameters (Standard)

- 0.5 mA, 200 Hz, 500 ms typical
- Post-stim artifact window: first 300 ms excluded
- Always report: amplitude, frequency, pulse width, duration, location, monopolar/bipolar

---

## 6. Statistical & Modeling Conventions

### Behavioral Analysis

- Mixed-effects models (lme4 / statsmodels). Random intercepts and slopes by subject.
- Permutation tests (1000-10000) for neural data
- Cluster-based permutation (Maris & Oostenveld, 2007) for time-frequency
- Bootstrap CIs for behavioral summary statistics
- Satterthwaite-approximated ANOVA for LMMs

### Model Fitting

- MLE for CMR-family models
- Particle swarm optimization (CMR-IA)
- Genetic algorithm (sCMR): 10000 initial sets, 20 generations of 1000, mutation 10%
- Cross-validation: fit on half lists, test on other half
- Model comparison: BIC/AIC (nested); held-out log-likelihood (non-nested)
- Chi-squared loss: sum of squared deviations / variance per data point

### Effect Sizes

- Cohen's d, η²/partial η², fixed effect estimates with 95% CIs
- Yule's Q for 2×2 contingency tables in successive testing (-1 to +1)

---

## 7. Terminology Guide

| Term | Meaning | ≠ Confused with |
|------|---------|------------------|
| Encoding | Forming a memory trace | Learning (broader) |
| Retrieval | Accessing a stored memory | Recall (a type of retrieval) |
| Recall | Overt production of a studied item | Recognition (judgment of prior occurrence) |
| Temporal context | Gradually evolving mental state items associate with | Temporal order (sequence memory) |
| Contiguity | Tendency to recall nearby items | Similarity (semantic relatedness) |
| TAG | Spectral pattern T+A-G+ marking memory success | Spectral tilt (related but distinct) |
| Spectral tilt | Broadband shift: increased HFA, decreased LFA | TAG (includes narrowband theta) |
| SME | Subsequent memory effect | SCE (subsequent clustering effect) |
| SCE | Subsequent clustering effect | SME (item-level) |
| Gestalt representation | Conjunctive pair encoding as single composite | Sequential/directional encoding |
| Output encoding | Trace formation during recall/recognition | Study-phase encoding |
| Delta-classifier | Post-stim minus pre-stim classifier output | Raw classifier output |

**Abbreviations (define on first use):**
CRP, SPC, PFR, PCS, IRT/IRI, CMR, CMR-IA, sCMR, TCM, TAG, SME, SCE, iEEG, ECoG, sEEG, HFA, LFA, SOZ, DES, SWR, IRASA, TBI, PLI, ELI, ILI
