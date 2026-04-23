---
name: memory-publications
description: >
  Assists with academic publications in human memory and cognitive neuroscience. Covers drafting
  manuscript sections, responding to reviewer comments, journal formatting (JEP:General, JEP:LMC,
  APA 7th), literature review, citation management via memlab.bib, LaTeX/latexdiff workflows,
  and Python figure generation. Encodes deep domain knowledge: retrieved context models (CMR, TCM),
  intracranial EEG, hippocampal oscillations, brain stimulation, and computational modeling.
  Accesses research artifacts on Box (KahanaPubs PDFs, Overleaf LaTeX projects, referee reports)
  and GitHub (pennmem). Matches the user's writing style via an extracted style profile.

  Use this skill whenever the user mentions: writing a paper, manuscript, journal submission,
  reviewer response, resubmission, LaTeX, BibTeX, latexdiff, APA formatting, figure captions,
  or anything related to academic publishing in memory/cognitive neuroscience — even casually
  like "help me with my paper" or "respond to Reviewer 2." Also trigger for .tex/.bib uploads.
---

# Memory Publications Skill

This skill helps produce high-quality academic manuscripts in human memory and cognitive neuroscience, with deep domain expertise and journal-specific formatting knowledge.

## Quick Reference

Before starting any task, identify which workflow applies:

| Task | Go to |
|------|-------|
| Identify which project is being discussed | `references/current-projects.md` |
| Draft a manuscript section | §1 Drafting |
| Respond to reviewer comments | §2 Reviewer Responses |
| Format / reformat for a journal | §3 Journal Formatting |
| Generate or refine figures | §4 Figures |
| latexdiff or track-changes | §5 LaTeX Workflows |
| Literature review or citations | §6 Citations & Literature |

**Before starting work on any manuscript, check `references/current-projects.md`** to identify the project, its current status, target journal, confirmed .tex file on Box, author list, and any project-specific conventions (e.g., which citation system it uses, what register to write in, what analyses are planned). This file contains the priority-ordered list of all active projects with Box folder IDs, file IDs, and detailed entries for each.

For domain-specific terminology, theoretical frameworks, and statistical conventions, read `references/domain-knowledge.md`.

For journal-specific formatting rules (especially JEP), read `references/journal-formats.md`.

---

## Research Artifact Locations

All research materials are accessible through two main channels. **Always check these locations first** before asking the user to upload files.

### Box (primary access point for documents)

Use the Box tools to search and retrieve files from these locations:

- **Reference PDFs & Publications**: `RESEARCH/References-Publications/` (folder ID: 68429854028) — Topical subfolders (Alzheimer's, TBI, Memory and enhancement, DBS Safety, etc.) plus the user's own publications.
- **Master Bibliography**: `RESEARCH/References-Publications/memlab.bib` (file ID: 2165624865421) — The canonical BibTeX database with entries for every article the user has read and cited. Use this as the authoritative source for citations rather than generating BibTeX entries from memory. Note: copies of memlab.bib also exist inside each Overleaf project, but this is the master version.
- **Kahana Lab Publications**: `RESEARCH/References-Publications/KahanaPubs/` (folder ID: 353580318851) — 346 PDFs of published work. Naming convention: `AuthorEtalYY.pdf` (e.g., `BurkEtal13.pdf` = Burke et al., 2013; `PolyEtal09.pdf` = Polyn et al., 2009). Search here when you need the full text of one of the user's own papers.
- **Referee Reports**: `RESEARCH/KahanaRefereeReports/` (folder ID: 352048088561) — Past referee reports.
- **SNS Manuscript**: `RESEARCH/SNS manuscript/` (folder ID: 253376092507) — Brain Stimulation paper files.
- **LaTeX Source Projects**: `RESEARCH/KahanaOverleafLaTeX/` (folder ID: 371190112346) — Full Overleaf project trees including .tex sources, .bib files, figures, and submission history. Folders are named by paper title (e.g., "A memory-based theory of emotional disorders"), with subfolders for each submission round (Submission1, Submission2, etc.). When the user asks to work on a manuscript's LaTeX source, search here first. The shared bibliography file is `memlab.bib`. **For active projects, consult `references/current-projects.md` first — it maps each project to its confirmed Box folder ID, .tex file ID, and current filename, avoiding ambiguity when multiple .tex files exist in a folder.**
- **Writing Style Exemplars**: `RESEARCH/KahanaWritingStyle/` (folder ID: 371189482842) — 14 LaTeX files that define the user's writing voice. Includes 9 chapters of *Foundations of Human Memory* (chap1-9.tex, FHM2.tex), plus KahaAR2019.tex, LawsOfMemory.tex, LiEtalNatureCommunications.tex, and PeersManuscript.tex. Consult `references/writing-style.md` for the extracted style profile; when drafting any prose, follow those patterns.

When the user mentions a paper they're working on, search `RESEARCH/KahanaPubs/` first. When they reference a cited paper, search `RESEARCH/Reference-Publications/`.

### GitHub (data and analysis code)

- **Organization**: `github.com/pennmem` — Data processing pipelines, analysis scripts, and computational modeling code.
- Public repos can be accessed directly via `web_fetch`. For private repos, check whether a copy exists in Box, or ask the user to paste the relevant code.

### Topic Index

Consult `references/research-index.json` to determine which topic a query falls under before searching. The index maps 206 Overleaf projects and KahanaPubs PDFs into 5 research threads:

1. **Memory Theory & Models** — Retrieved context models (TCM, CMR, sCMR, CMR-IA), empirical free recall phenomena, serial recall, recognition
2. **Behavioral Economics, Memory & Decisions** — Wachter collaborations on portfolio choice/forecasting, Ramayya/Zaghloul reward and RPE intracranial work
3. **EEG & Oscillations** — Theta, alpha, beta, gamma during memory tasks, both intracranial and scalp EEG (NOT single-unit recordings)
4. **Brain Stimulation** — Open/closed-loop stimulation, DARPA RAM, Nia Therapeutics, TBI
5. **Single-Unit Recordings** — Time cells, MTL neuron phase locking, shared neural assemblies, and other single-neuron studies

### Access Strategy

**Key papers quick-reference (Box file IDs for frequently needed sources):**

| Citation key | Box filename | Box file ID | Topic |
|---|---|---|---|
| WachterKahana2024 | WachKaha24.pdf | 2061095713219 | Retrieved-context theory of financial decisions (QJE) |
| PolynNormanKahana2009 | PolyEtal09.pdf | 2061097974698 | CMR model (Psych Review) |
| LohnasPolynKahana2015 | LohnEtal15.pdf | 2061090935012 | CMR2 / interlist effects (Psych Review) |
| KahanaParonWachter2025 | ParoEtal24.pdf | 2061096373979 | Associative learning & representativeness |
| KahaEtal24 (PEERS) | KahaEtal24.pdf | varies — search | PEERS overview (JEP:LMC) |
| HowardKahana2002 | HowKaha02.pdf | search | TCM (J Math Psych) |
| JinEtal24 (CMR-IA) | JinEtal24.pdf | 2061091062488 | CMR-IA model |

Use `get_file_content` with the file ID to read these papers directly. When writing about model mechanisms, equations, or predictions, **always fetch and verify against the source before drafting.**

1. User mentions a topic → Check the topic index to narrow search to relevant projects and PDFs
2. User says "open my CMR paper" → Topic index says memory_theory_and_models → Search the listed Overleaf projects or KahanaPubs PDFs for that topic
3. User says "check what Burke et al. 2013 said about spectral tilt" → Search `RESEARCH/References-Publications/KahanaPubs/` for `BurkEtal13.pdf`, or if it's not a Kahana lab paper, search the topical subfolders in `References-Publications/`
4. User says "look at the analysis script for the theta project" → Try `github.com/pennmem` first; fall back to asking the user
5. User uploads a file directly → Use that; it's the freshest version

---

## §1 Drafting Manuscript Sections

**Before drafting any prose, read `references/writing-style.md`** for the extracted writing style profile. All drafted text should match the voice, sentence architecture, and rhetorical patterns described there.

**Before writing any paragraph that makes claims about the predictions, mechanisms, or equations of a computational model (CMR, TCM, CMR-IA, etc.), fetch the relevant paper from Box and verify the claims against the source text.** Do not rely on general knowledge for model equations, parameter interpretations, or quantitative predictions — these are precisely the details most susceptible to hallucination. Use the key papers table in the Access Strategy section below, or search `RESEARCH/References-Publications/KahanaPubs/` by filename. The same principle applies to claims about specific experimental results: if you are stating what a study found, read the paper first.

### General Principles

Academic writing in memory science is precise but not sterile. The best papers in this field (Kahana, Polyn, Howard, Lohnas, etc.) combine formal rigor with clear narrative flow. Key qualities:

- **Lead with the scientific question**, not the history of the field. The introduction should make the reader care about the problem before surveying what's known.
- **Be specific about mechanisms.** Don't write "memory processes" when you mean "temporal context reinstatement" or "hippocampal theta-gamma coupling." The field values precision.
- **Connect computational models to data.** If the paper involves modeling (e.g., CMR, TCM), the writing should make clear what the model predicts, how the prediction was tested, and what the data showed — not just "the model fit the data well."
- **Statistical reporting follows APA 7th edition** (see §3 for details).

### Section-by-Section Guidance

**Introduction**
1. Open with a concrete phenomenon or question (1-2 paragraphs)
2. Review the relevant literature, organized by theoretical thread — not chronologically
3. Identify the gap or tension that motivates the current work
4. State the current study's approach and key hypotheses
5. If the study uses computational modeling, briefly introduce the model framework and what it adds

**Methods**
- **Participants**: N, demographics, inclusion/exclusion criteria, IRB approval statement. For intracranial EEG studies, specify epilepsy monitoring context, electrode coverage, and how seizure onset zones were handled.
- **Materials/Stimuli**: Word pools (e.g., noun pool size, frequency norms used), encoding tasks, list structure (list length, number of lists, IPI, ISI)
- **Procedure**: Enough detail to replicate. Timing parameters matter in memory experiments — report them precisely.
- **Electrophysiological recording** (if applicable): Sampling rate, reference scheme, re-referencing approach (e.g., bipolar), artifact rejection criteria, frequency bands analyzed (theta: 3-8 Hz, gamma: 30-100 Hz, or whatever bands were used)
- **Computational modeling** (if applicable): Model equations or point to the original paper. Specify free parameters, fitting procedure (MLE, Bayesian, grid search), and goodness-of-fit metric.
- **Statistical analysis**: Describe the analytic approach. For mixed-effects models, specify fixed and random effects. For permutation tests, specify N permutations.

**Results**
- Report results in the order of the hypotheses/questions from the introduction
- For behavioral data: accuracy, response times, serial position curves, conditional response probability curves, lag-CRP curves — whatever is relevant
- For neural data: describe effects with both statistical tests and effect sizes
- For modeling: report fits, parameter estimates, and key model comparisons
- Use precise statistical language: F(df1, df2) = X.XX, p = .XXX, η² = .XX (or other appropriate effect size)

**Discussion**
1. Summarize the key findings (1 paragraph — don't repeat the results section)
2. Interpret in terms of the theoretical framework
3. Compare with prior work — where do findings converge/diverge?
4. Acknowledge limitations honestly
5. Future directions — be specific, not vague "future work should explore..."
6. Concluding paragraph that ties back to the opening question

### Writing Style Notes

- Use past tense for methods and results ("Participants studied..."), present tense for established facts ("The retrieved context framework assumes...")
- Avoid hedging language when the data are clear. If p < .001 and the effect size is large, say "X reliably increased Y" not "X appeared to somewhat increase Y"
- Define abbreviations on first use (CRP, SPC, IRI, CMR, TCM, ECoG, etc.)
- When referring to specific models, use their established abbreviations: CMR (Context Maintenance and Retrieval), TCM (Temporal Context Model), SAM (Search of Associative Memory), eCMR (emotional CMR)

---

## §2 Reviewer Responses

Reviewer response documents are a specific genre with their own conventions. The goal is to be thorough, respectful, and efficient — reviewers are busy.

### Format

Use a structured LaTeX document (or can be plain text if requested):

```latex
\documentclass[12pt]{article}
\usepackage[margin=1in]{geometry}
\usepackage{xcolor}

% Blue for our responses, black for reviewer comments
\newcommand{\response}[1]{\textcolor{blue}{#1}}
\newcommand{\reviewer}[1]{\textit{#1}}

\begin{document}
\title{Response to Reviewers}
\maketitle

\section*{Editor}
\reviewer{Editor's comment here.}

\response{Our response here.}

\section*{Reviewer 1}
\subsection*{Major Comments}

\reviewer{1. Reviewer's first major comment...}

\response{We thank the reviewer for this observation. [Response]...}

% Continue for each comment
\end{document}
```

### Tone and Strategy

- **Thank the reviewer** for substantive points (briefly — don't grovel)
- **Quote each comment** in full, then respond point by point
- **When you've made a change**, say exactly what changed and where: "We have revised the third paragraph of the Discussion (p. 18, lines 4-12) to address this point."
- **When you disagree**, do so respectfully with evidence: "We appreciate this suggestion. However, [specific reason with citation or data]..."
- **Never be dismissive.** Even minor comments deserve a clear response.
- **Cross-reference** between reviewer comments when they raise related issues
- **Include page/line numbers** for every revision made in the manuscript

### Common Reviewer Concerns in Memory Papers

- Sample size justification → Power analysis or reference to comparable studies in the field
- Multiple comparisons → Describe correction method (Bonferroni, FDR, cluster-based permutation)
- Model overfitting → Report cross-validation, BIC/AIC comparisons, or held-out data fits
- Generalizability across paradigms → Acknowledge limitation or cite converging evidence
- Effect of seizure focus on neural results (iEEG) → Describe controls (exclusion of SOZ electrodes, comparison across hemispheres)

---

## §3 Journal Formatting

Read `references/journal-formats.md` for detailed formatting rules per journal.

### APA 7th Edition (JEP: General, JEP: LMC)

These are the core formatting requirements:

**Document structure in LaTeX:**
```latex
\documentclass[man,12pt]{apa7}  % Use the apa7 document class
\usepackage[american]{babel}
\usepackage{csquotes}
\usepackage[style=apa,backend=biber]{biblatex}
\addbibresource{references.bib}

\title{Your Title Here}
\shorttitle{SHORT TITLE}
\author{Author One\textsuperscript{1} and Author Two\textsuperscript{2}}
\affiliation{
  \textsuperscript{1}Department of Psychology, University of Pennsylvania \\
  \textsuperscript{2}Second Affiliation
}
\abstract{Your abstract here (max 250 words for JEP).}
\keywords{keyword one, keyword two, keyword three}

\begin{document}
\maketitle
% Body sections are NOT numbered in APA style
\section{Introduction}  % Note: APA doesn't label this "Introduction" — just start writing
```

**Note:** The above is a generic APA template. Many of the user's active manuscripts use `apacite` (with `\citeA{}`, `\citeNP{}`) rather than `biblatex`. Always check `references/current-projects.md` for the specific LaTeX system each project uses before editing citations.

**Key APA rules to internalize:**
- Section headings: Level 1 (centered, bold), Level 2 (left-aligned, bold), Level 3 (left-aligned, bold italic, indented)
- In-text citations: (Kahana, 2012) or Kahana (2012); two authors use "&" in parenthetical but "and" in running text; 3+ authors use "et al." from first citation
- Statistics: Italicize test statistics and p — *F*(2, 45) = 3.21, *p* = .032, *η*² = .12
- Numbers: Spell out below 10 unless it's a measurement, age, statistical value, or in a series with numbers ≥10
- Tables and figures: Each on its own page after references (in manuscript format), numbered sequentially, with descriptive titles and notes
- References: DOI as `https://doi.org/10.xxxx` format

**Statistical reporting checklist:**
- [ ] Exact *p* values (not *p* < .05, unless *p* < .001)
- [ ] Effect sizes for all inferential tests
- [ ] Confidence intervals where appropriate
- [ ] Degrees of freedom for all test statistics
- [ ] Descriptive statistics (M, SD) before or alongside inferential tests

---

## §4 Figures

Figures in memory papers often include serial position curves, lag-CRP curves, temporal clustering scores, spectrograms, electrode placement maps, and model fit comparisons.

### Python Figure Generation

When generating figures with matplotlib/seaborn, follow these principles:

```python
import matplotlib.pyplot as plt
import matplotlib as mpl
import seaborn as sns
import numpy as np

# Publication-quality defaults
def set_pub_style():
    """Set matplotlib defaults for publication figures."""
    mpl.rcParams.update({
        'font.family': 'sans-serif',
        'font.sans-serif': ['Arial', 'Helvetica'],
        'font.size': 10,
        'axes.titlesize': 12,
        'axes.labelsize': 11,
        'xtick.labelsize': 9,
        'ytick.labelsize': 9,
        'legend.fontsize': 9,
        'figure.dpi': 300,
        'savefig.dpi': 300,
        'savefig.bbox': 'tight',
        'axes.spines.top': False,
        'axes.spines.right': False,
        'lines.linewidth': 1.5,
        'lines.markersize': 5,
    })

set_pub_style()
```

**Standard figure sizes** (APA single column ~3.3in, double column ~6.9in):
- Single panel: `figsize=(3.3, 2.5)` or `(3.3, 3.3)` for square
- Two panels side by side: `figsize=(6.9, 2.5)`
- Multi-panel: use `plt.subplots()` with `constrained_layout=True`

**Common memory science figures:**

1. **Serial Position Curve**: x = serial position, y = recall probability. Include error bars (SEM). Often shown with a solid line for data, dashed for model predictions.

2. **Lag-CRP (Conditional Response Probability by Lag)**: x = lag (transition distance), y = CRP. Typically shown for lags -5 to +5. The asymmetry (forward > backward) and the contiguity effect (peak near lag ±1) are the key features to highlight.

3. **Probability of First Recall (PFR)**: x = serial position, y = probability of first recall. Shows strong recency in immediate free recall.

4. **Spectrograms / Power plots**: Use consistent colormaps (e.g., `viridis` or `RdBu_r` for contrast maps). Always include a colorbar with units (e.g., "log power", "t-statistic").

5. **Electrode placement**: If showing electrode locations on a brain, use standard MNI coordinates or a cortical surface rendering.

**Figure captions** should be self-contained: a reader should understand the figure without reading the main text. Include what the figure shows, what each panel/line represents, what error bars mean, and the N if it differs from the full sample.

### Exporting

- Save as PDF or EPS for vector graphics: `plt.savefig('fig1.pdf')`
- For raster elements (e.g., spectrograms), use 300 DPI minimum
- Ensure all text in figures is legible at the printed size

---

## §5 LaTeX Workflows

### latexdiff for Revisions

When preparing a revised manuscript, use `latexdiff` to generate a marked-up PDF showing changes:

```bash
# Basic usage: compare old and new versions
latexdiff original.tex revised.tex > diff.tex
pdflatex diff.tex
biber diff      # if using biblatex
pdflatex diff.tex
pdflatex diff.tex  # run twice for references

# For multi-file projects, flatten first:
latexpand original.tex > original_flat.tex
latexpand revised.tex > revised_flat.tex
latexdiff original_flat.tex revised_flat.tex > diff.tex
```

**Common latexdiff issues and fixes:**
- If latexdiff chokes on complex math or custom macros, use `--math-markup=0` to disable math diffing
- For `apa7` class conflicts, add `%DIF PREAMBLE` exclusions as needed
- If tables break, use `--type=UNDERLINE` instead of the default `CFONT`
- Always visually inspect the diff PDF — latexdiff sometimes misplaces change markers around figures or tables

### Project Structure

A clean LaTeX project for a memory paper typically looks like:

```
manuscript/
├── main.tex            # Master document
├── references.bib      # BibTeX database
├── sections/
│   ├── introduction.tex
│   ├── methods.tex
│   ├── results.tex
│   └── discussion.tex
├── figures/
│   ├── fig1_spc.pdf
│   ├── fig2_lagcrp.pdf
│   └── fig3_model.pdf
├── tables/
│   └── table1.tex
└── supplementary/
    └── supplement.tex
```

Use `\input{sections/introduction}` in main.tex to keep things modular.

---

## §6 Citations & Literature

### BibTeX Management

The user's manuscripts use several different citation systems depending on the project. **Always check `references/current-projects.md` for the specific system before editing citations.** The three systems in active use are:

1. **`apacite`** (most common in active projects): Used with `apa6` or `apa7` document classes. Citations use `\citeA{}` (narrative), `\citeNP{}` (parenthetical without parens), `\cite{}` (parenthetical). Compile with `pdflatex` + `bibtex`.

2. **`natbib` + manual `\begin{thebibliography}`**: Used in some working papers (e.g., Memory & Forecasting). Citations use `\citet{}`, `\citep{}`, `\citeauthor{}`. Three `pdflatex` passes for full reference resolution. New references must be placed alphabetically by hand.

3. **`biblatex` + `biber`**: Used in some Overleaf projects for APA-formatted submissions. Citations use `\autocite{}`, `\textcite{}`, etc.

**Do not mix citation systems within a project.** If uncertain, read the preamble of the project's .tex file.

**BibTeX entry conventions for the field:**

```bibtex
@article{kahana2012,
  author    = {Kahana, Michael J.},
  title     = {Foundations of human memory},
  year      = {2012},
  journal   = {Oxford University Press},
  doi       = {10.1093/acprof:oso/9780199764822.001.0001}
}

@article{polyn2009,
  author    = {Polyn, Sean M. and Norman, Kenneth A. and Kahana, Michael J.},
  title     = {A context maintenance and retrieval model of organizational
               processes in free recall},
  year      = {2009},
  journal   = {Psychological Review},
  volume    = {116},
  number    = {1},
  pages     = {129--156},
  doi       = {10.1037/a0014420}
}
```

- Always include DOIs
- Use full first names (APA style prefers initials, but full names in .bib entries let biblatex abbreviate correctly)
- Keep journal names unabbreviated in the .bib file — let the style handle abbreviation

### Literature Review Assistance

When helping with literature review:

1. Start from the theoretical framework. For a paper using retrieved context models, the core citation chain typically includes: Raaijmakers & Shiffrin (1981), Howard & Kahana (2002), Polyn et al. (2009), Lohnas et al. (2015), and recent extensions.

2. Identify the specific behavioral phenomena being addressed — contiguity effects, temporal clustering, forward asymmetry, semantic clustering, prior-list intrusions, etc. — and cite the key empirical papers for each.

3. For neural work, situate within the oscillation literature: Sederberg et al. (2003) for theta during encoding, Burke et al. (2013) for spectral tilt, Solomon et al. (2019) for theta/gamma interactions, etc.

4. Be careful about citation currency. If the user provides a .bib file, work from that. If constructing citations from domain knowledge, flag any citation where you're uncertain about the year or specific details — bibliographic precision matters enormously.

**Important**: Always tell the user when you're generating citations from memory versus working from a provided .bib file. Hallucinated citations are a serious problem — when in doubt, note the uncertainty and suggest the user verify.

---

## General Workflow

When the user asks for help with a publication task:

1. **Identify the project** by checking `references/current-projects.md`. This tells you the target journal, confirmed .tex file, author list, LaTeX system, and project-specific conventions. If the user mentions a project by short name, nickname, lead author, or topic, match it to the priority list there.
2. **Gather source materials — project knowledge first, then Box.** The user's standard workflow is to discuss papers within a Claude Project that contains the relevant PDFs as project knowledge. These files are already in context and require no fetching — they are the preferred source. For any materials not available in the project knowledge, fall back to Box. The priority order is:
   1. **Project knowledge** (PDFs and other files uploaded to the current Claude Project) — check these first. They are immediately available, require no tool calls, and represent the user's curated set of relevant papers for this manuscript.
   2. **Box** — for papers not in the project knowledge, use the file IDs and folder paths in `current-projects.md` or search `RESEARCH/References-Publications/KahanaPubs/` (346 PDFs, named `AuthorEtalYY.pdf`) and the topical subfolders in `RESEARCH/References-Publications/`.
   3. **GitHub** (`github.com/pennmem`) — for analysis code and data processing scripts.
   4. **User upload** — ask the user to provide a file only as a last resort, if it cannot be found in project knowledge or Box.
3. **Confirm inputs before drafting.** Before writing anything, present the user with a brief summary of the inputs you have assembled and confirm readiness. This checkpoint lets the user catch missing files, wrong versions, or access problems before any drafting time is spent. The summary should include:
   - **Project identified:** name, target journal, and current status from `current-projects.md`
   - **From project knowledge:** list papers available in the current project's uploaded files, with a one-line note on what you will use each for
   - **Fetched from Box:** list any additional files retrieved from Box by name and file ID, noting whether each was readable
   - **Not available:** list any files you expected to need but could not find in project knowledge or Box, along with what you tried
   - **Skill reference files consulted:** which of `writing-style.md`, `domain-knowledge.md`, `journal-formats.md`, `current-projects.md` you read
   - **Key assumptions:** any decisions you are making in the absence of explicit instruction (e.g., "Assuming APA 7th for JEP:LMC target")
   Wait for the user to confirm or redirect before proceeding to step 4.
4. **Verify claims against source text.** Before writing about any computational model's mechanisms, equations, or predictions, or about any specific experimental result, read the relevant sections of the fetched papers. Do not draft from general knowledge — this is the single most important rule for avoiding hallucination.
5. **Read the relevant reference file** if needed (domain knowledge, journal formats, writing style)
6. **Ask clarifying questions** if the task is ambiguous — but be efficient about it. If you can make reasonable assumptions (e.g., APA format for a JEP paper), do so and note the assumption.
7. **Draft in markdown** by default. Use plain-text citation style — e.g., `Rafla et al. (2024)` or `(Kahana, 1996)` — and focus on prose and argument structure without worrying about LaTeX commands, citation keys, or special-character escaping. Convert to LaTeX with project-specific formatting (apacite/natbib/biblatex, correct citation keys from memlab.bib) once the content is approved. If the user is working directly in a `.tex` file or explicitly requests LaTeX, produce LaTeX from the start.
8. **For figures**, generate complete Python scripts that produce publication-ready output
9. **Flag uncertainties** — especially around citations, specific formatting requirements that may have changed, or claims about the literature that you're not fully confident in

---

## §7 Revision Workflow

When working through a manuscript revision (as opposed to drafting from scratch), follow these practices:

### Iterative, Section-by-Section Review

The user prefers to work through revisions one section at a time, reviewing and providing feedback before moving to the next section. Do not revise the entire manuscript in one pass unless explicitly asked. At the start of a revision session:

1. **Check `references/current-projects.md`** to identify the project's current status, what's been done, what remains, and any project-specific conventions
2. Read the full manuscript to understand the current state
3. Propose a section-by-section plan and ask which section to start with
4. For each section, ask clarifying questions before drafting
5. Present the revised section and summarize the key changes
6. Wait for approval or further instructions before proceeding

### Change Tracking

- Use `\textcolor{olive}{...}` to highlight new or substantially revised text, unless the user asks otherwise
- When the user approves changes, strip the olive coloring in the next pass
- For comparing versions, use `diff` with process substitution or `latexdiff`

### Handoff Documents

When a session is ending, prepare a handoff document summarizing: (a) what was completed, (b) the current state of each section, (c) what remains to be done, and (d) any open decisions. This allows the next conversation to start efficiently.

### Cross-Disciplinary Register

When drafting for an economics audience (e.g., QJE, JFE), adjust the register: assume familiarity with financial concepts (AR processes, rational expectations, asset pricing) but explain memory science concepts. When drafting for a psychology audience (e.g., JEP, Psych Review), do the reverse. For papers that bridge both fields, define terms from both domains on first use.

### LaTeX System Note

The user's manuscripts use three different citation systems depending on the project. **Always check `references/current-projects.md` for the specific system before editing.** The three systems are:

- **`apacite`** (most common): Used with `apa6`/`apa7`. `\citeA{}`, `\citeNP{}`, `\cite{}`. Compile with `pdflatex` + `bibtex`.
- **`natbib` + manual `\begin{thebibliography}`**: Used in some working papers. `\citet{}`, `\citep{}`. Three `pdflatex` passes. Manual alphabetical placement of new references.
- **`biblatex` + `biber`**: Used in some Overleaf projects. `\autocite{}`, `\textcite{}`.

Do not mix systems within a project. When in doubt, read the preamble of the .tex file.
