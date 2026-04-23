# Deep reading strategy

The user asked for "deepest possible reading" of each paper. This document describes how to get real comprehension — not a skim — before generating any slides.

## Consulting `memory-publications/references/domain-knowledge.md` when installed

If the `memory-publications` skill is installed (see the integration section of this skill's SKILL.md), read its `references/domain-knowledge.md` **once at the start of the deep-reading pass** and keep it as reference material while reading papers and writing slides. It gives you:

- Correct model provenance: CMR (Polyn, Norman, Kahana 2009) vs. TCM (Howard & Kahana 2002) vs. CMR2 (Lohnas et al. 2015) vs. eCMR (Talmi et al. 2019) vs. CMR-IA (Jin et al.) vs. sCMR (Herweg & Kahana). Don't conflate these on slides.
- Canonical terminology: "contiguity effect" (not "contiguity bias"), "lag-CRP", "semantic clustering", "PLI / ELI / ILI", "spectral tilt", "TAG" (T+A-G+), "SME" vs. "SCE", "delta-classifier" post-stim minus pre-stim.
- Parameter names that should appear on equation slides without drift: β_enc, β_rec, γ_FC, γ_CF, φ_s, φ_d, s, κ, λ, η.
- Statistical reporting conventions: mixed-effects models with random intercepts + slopes, cluster-based permutation (Maris & Oostenveld 2007), bootstrap CIs, Yule's Q.
- Framework-specific details (TAG, closed-loop stim, SME decomposition) that may be invoked without explanation in the paper's methods section — you'll need them to interpret figures.

When a paper uses a term the domain-knowledge file defines differently, trust the paper's usage (it's the authority on its own contents) but note the divergence in a warning on the slide plan so the speaker can decide how to resolve it.

**When `memory-publications` is absent**, you proceed without this scaffolding. Be extra conservative: if a term's meaning is uncertain, quote the paper's own phrasing verbatim on the slide rather than paraphrasing, and flag the uncertainty in the slide's note.

## Don't assume authors remember their own papers

When the user asks a factual question about their own manuscript ("is Sim 2b
about rearranged pairs or intact pairs?", "what was N for Experiment 3?",
"did we report Cohen's $d$ or $\eta^2$?"), take it at face value. Look up
the answer in the bundle's `drafts/selected.tex` or the PDF and respond with
specifics, including section/figure references.

This is a feature of working with busy researchers on past work — not a gap
in their competence. They genuinely don't remember every methodological
detail of a paper they drafted years ago, and that's why they're asking.
The skill's job is to retrieve quickly and cite the source.

## Fact-checking as a separate pass

Fact-checking (statistics, dates, exact citation years, figure-to-text
consistency) is its own pass that runs **after slide content is approved by
the user** — not during drafting. Rationale: any slide the user decides to
cut is a wasted fact-check.

The fact-checking pass produces a single report (not in-deck edits), listing
each discrepancy between the slide and the source, with line numbers. The
user resolves the report; only then does the skill apply edits.

## Order of operations per paper

1. **Read the manifest** (`manifest.json`) — title, authors, year, figure count
2. **Read the abstract** (`abstract.txt`) — the paper's own framing
3. **Read the full draft** (`drafts/selected.tex` or `.pdf`) — in order, not skimming
4. **Study every figure** — load each image from `figures/` and describe what it shows
5. **Parse citations in context** — note which references are used to justify which claims
6. **Identify the paper's sections** — map to the standard structure (intro, methods, results, discussion) even if the .tex uses different section names

## Reading the draft

For `.tex` sources, strip comments (`%...`) and preamble (`\documentclass`, `\usepackage`, etc.) before reading. The content between `\begin{document}` and `\end{document}` is what matters.

Sections to pay special attention to:

- `\title{}`, `\author{}`, `\date{}` — confirm against manifest
- `\begin{abstract}...\end{abstract}` — if manifest's abstract seems thin, re-extract
- Each `\section{}` and `\subsection{}` — these define the paper's argumentative arc
- `\begin{figure}...\end{figure}` blocks — each has a `\caption{}` that belongs with the figure file
- `\cite{}` / `\citep{}` / `\citet{}` commands — note which claims reference which work

For PDF-only sources, use `pdftotext` to extract the full text. Accept that figure captions may be interleaved awkwardly; cross-reference with figures/ directory names when possible.

## Studying figures

This is where a skill that does *real* reading differs from one that does template filling.

For each figure file in `figures/`:

1. **Load the file as an image** (via vision input, not just filename)
2. **Describe what the figure actually shows**: axes, variables plotted, trends, comparisons, number of panels, error bars, etc. Don't just regurgitate the caption.
3. **Record the figure's caption** from the `.tex` source (find the matching `\includegraphics{}` and grab the surrounding `\caption{}`)
4. **Note the figure's role in the paper**: is it a design diagram, a result, a model fit, a schematic?

Example: for `Fig2_FitComparisons.pdf` in CohenKahana2019:

- Vision output: "Four-panel figure. Each panel shows a line plot with recall probability (y-axis) vs. serial position (x-axis). Three lines per panel: filled black circles for data, open circles for model A, open triangles for model B. Error bars visible. Model A tracks data more closely than Model B across all four panels."
- Caption from tex: `\caption{CMR3 fits to four benchmark recall phenomena...}`
- Role in paper: results / model validation

Vision output + caption + role = enough context to write a useful slide about this figure.

## Parsing citations

Citations anchor the paper's argument. For each `\cite{key}` in the draft, you should be able to say:

- What claim it supports
- Whether the cited work is foundational, contrasting, or extending

The skill doesn't need to read the cited papers themselves — it just needs to know which references are load-bearing for the paper's argument. These are the citations that should appear in the talk's slides (not every citation — just the important ones).

Rough heuristic: citations that appear in the abstract, introduction, or discussion are usually load-bearing. Citations buried in methods sections (especially for software tools or statistical procedures) usually aren't.

## For multi-paper decks

After reading each paper individually, do a cross-paper synthesis pass:

1. **Shared methods / datasets**: do the papers use PEERS? ltpFR? A common word pool? Same analysis pipeline? Note this — it's worth a slide in the methods section.
2. **Shared framework**: common theoretical model (CMR? SAM? dual-store?), common computational approach (model fitting, neural decoding, etc.)
3. **Points of agreement**: findings replicated across multiple papers — strongest evidence in a talk
4. **Points of divergence**: cases where papers differ — honest to acknowledge; interesting to explore
5. **Temporal arc**: if papers span years, note the evolution of the research program

Record these findings in a working document before drafting slides. The synthesis section of the deck depends on them.

## When to stop reading

Reading is time-bounded. For an expert-audience talk of ~25 slides, budget roughly:

- 5-10 minutes on the draft text (first pass)
- 2-3 minutes per figure with vision
- 2-3 minutes on the bib / citation map
- 5 minutes on synthesis (multi-paper only)

If a paper has 30 figures, you don't need to study all of them deeply. Prioritize figures the draft's discussion section references as key results.

## Output of the reading stage

Before touching any slide code, produce a structured summary per paper:

```
{
  "paper_slug": "cohenkahana2019",
  "one_line_summary": "Extension of CMR to emotional memory...",
  "key_claims": ["claim 1", "claim 2", "claim 3"],
  "methods_summary": "Two-part approach: (a) ... (b) ...",
  "figure_roles": {
    "Fig1_model_schematic.pdf": {"role": "schematic", "shows": "..."},
    "Fig2_FitComparisons.pdf": {"role": "results", "shows": "..."},
    ...
  },
  "load_bearing_citations": ["howard2002", "polyn2009", ...],
  "candidate_slide_material": ["..."]
}
```

Feed this summary into `plan_deck.py`. The slide plan is built from structured summaries, not from raw paper text.
