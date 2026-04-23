# Journal Formatting Reference

Detailed formatting requirements for target journals. Consult when preparing a submission or reformatting between journals.

## Table of Contents
1. JEP: General
2. JEP: Learning, Memory, and Cognition
3. Other Journals (brief notes)

---

## 1. Journal of Experimental Psychology: General (JEP:General)

**Publisher**: American Psychological Association (APA)
**Style**: APA 7th Edition (strict)
**Submission format**: Manuscript format (double-spaced, 12pt, Times New Roman or equivalent serif)

### LaTeX Setup

```latex
\documentclass[man,12pt]{apa7}
\usepackage[american]{babel}
\usepackage{csquotes}
\usepackage[style=apa,backend=biber]{biblatex}
\usepackage{graphicx}
\usepackage{amsmath}
\usepackage{booktabs}

\addbibresource{references.bib}

% Author note (required)
\authornote{
  \addORCIDlink{First Author}{0000-0000-0000-0000}

  Correspondence concerning this article should be addressed to
  First Author, Department of Psychology, University of Pennsylvania,
  3401 Walnut Street, Philadelphia, PA 19104.
  E-mail: author@psych.upenn.edu
}
```

### Structure Requirements

1. **Title page**: Title, author names, affiliations, author note, ORCID links
2. **Abstract**: Maximum 250 words. No citations in abstract. End with 3-5 keywords.
3. **Body**: Introduction (unlabeled — do NOT write "Introduction" as a heading), Method, Results, Discussion
4. **References**: APA 7th edition format via biblatex-apa
5. **Footnotes**: Numbered sequentially, used sparingly
6. **Tables**: Each on separate page after references, numbered Table 1, Table 2, etc. Use `booktabs` for clean horizontal rules (no vertical lines).
7. **Figures**: Each on separate page after tables. Figure caption below the figure. Number Figure 1, Figure 2, etc.
8. **Appendices**: After figures, labeled Appendix A, B, etc.

### Specific Formatting Rules

**Headings hierarchy:**
- Level 1: Centered, Bold (e.g., "Method")
- Level 2: Left-Aligned, Bold (e.g., "Participants")
- Level 3: Left-Aligned, Bold Italic, ending with period, text continues on same line
- Level 4: Indented, Bold, ending with period, text continues
- Level 5: Indented, Bold Italic, ending with period, text continues

**Citations:**
- Parenthetical: (Kahana, 2012) or (Kahana & Lohnas, 2020)
- Narrative: Kahana (2012) showed that...
- Two authors: Always cite both names
- Three or more: Use "et al." from first citation — e.g., (Polyn et al., 2009)
- Multiple citations in parentheses: Alphabetical order, separated by semicolons — (Howard & Kahana, 2002; Polyn et al., 2009; Raaijmakers & Shiffrin, 1981)
- "and" in running text, "&" in parenthetical citations

**Statistics:**
- Italicize: *F*, *t*, *p*, *d*, *M*, *SD*, *N*, *n*, *r*, *R*², *η*², *β*, *χ*²
- Do NOT italicize: Greek letters used as names of tests or models (e.g., alpha level, not *α* unless referring to the statistic)
- Report exact *p* values to three decimal places: *p* = .032 (not *p* < .05)
- Exception: *p* < .001 (don't report extremely small exact values)
- Zero before decimal for statistics that can exceed 1 (e.g., *t*(34) = 0.82); no zero for those bounded by ±1 (e.g., *p* = .041, *r* = .55)

**Numbers:**
- Spell out one through nine in running text
- Use numerals for 10 and above, measurements, ages, statistical values, time/dates, percentages
- Spell out numbers that begin a sentence

**Tables:**
- Title in italics above the table
- Use `\toprule`, `\midrule`, `\bottomrule` from booktabs
- General notes, specific notes, and probability notes below table
- Column headings centered; stub column left-aligned

### Word / Page Limits

JEP:General does not impose a strict word limit but typical research articles are 8,000-12,000 words. Substantially longer papers should be justified. Brief Reports are ~3,000 words.

### Transparency and Openness

APA journals now require:
- Data availability statement
- Preregistration disclosure (whether study was preregistered, and if so, where)
- Materials availability
- Code availability

Include these in the author note or as a separate section before references.

---

## 2. Journal of Experimental Psychology: Learning, Memory, and Cognition (JEP:LMC)

**Same APA 7th edition formatting as JEP:General.** The differences are editorial scope, not formatting:

- JEP:LMC focuses more narrowly on learning and memory (the core experimental phenomena)
- JEP:General publishes broader, often higher-impact or cross-cutting work
- The formatting, style, and submission requirements are identical

**Typical article length**: 6,000-10,000 words for regular articles.

### What JEP:LMC Reviewers Specifically Care About

Based on field conventions:
- Rigorous behavioral methodology with appropriate controls
- Clear connection to existing theoretical frameworks (especially computational models when applicable)
- Adequate sample sizes — the field has moved toward N > 30 for behavioral studies, N > 50 for individual-differences work
- Replication or converging evidence across experiments (multi-experiment papers are common)
- Clean statistical reporting following APA standards exactly

---

## 3. Other Journals (Brief Notes)

These are not primary targets but may come up. Formatting details can be added if needed.

### Psychological Review
- APA format (same as JEP)
- Theory-heavy — expects formal models or substantial theoretical contribution
- Longer papers typical (10,000-15,000 words)
- Figures often contain model diagrams, simulation results

### Brain Stimulation
- Elsevier journal — uses Elsevier article classes or standard LaTeX
- NOT APA style — uses numbered references (Vancouver-style), not author-date
- Structured abstract: Background, Objective, Methods, Results, Conclusions
- Short communications and full articles
- Very specific about stimulation parameter reporting (see domain-knowledge.md §3)
- Impact factor-conscious community; concise writing valued

```latex
% Brain Stimulation LaTeX setup
\documentclass[12pt]{elsarticle}
\usepackage{natbib}
\bibliographystyle{elsarticle-num}
% Numbered references: \cite{kahana2012} produces [1]
```

### Hippocampus / Journal of Neuroscience
- Wiley (Hippocampus) / Society for Neuroscience (J Neuro)
- Not APA style — both use author-date but with journal-specific tweaks
- J Neuroscience has strict length limits: Regular articles ~6,000 words, Brief Communications ~3,000 words
- Both require detailed methods for neural recording and analysis

### PNAS
- National Academy format — very specific two-column layout
- 6-page limit for direct submissions (longer for contributed/communicated)
- Significance statement required (120 words, accessible to broad audience)
- SI Appendix for detailed methods and supplementary results

### Nature / Science Family
- Extremely concise main text (Nature: ~3,000 words, ~4 figures)
- Extended Data and Supplementary Information carry the methodological detail
- Methods section at end of paper (Nature) or in Supplementary Materials (Science)
- Very different style from APA — no APA formatting conventions apply
- Numbered references

---

## Format Conversion Checklist

When reformatting a paper between journals, check these items:

- [ ] Document class / template changed
- [ ] Reference style switched (author-date ↔ numbered)
- [ ] Abstract restructured if needed (structured vs. unstructured)
- [ ] Heading levels adjusted to journal conventions
- [ ] Figure/table placement adjusted (end of manuscript vs. inline)
- [ ] Word count within journal limits
- [ ] Author note / correspondence / conflict of interest statement updated
- [ ] Transparency / data availability statement included
- [ ] Statistical notation matches journal style
- [ ] Keywords added/removed as required
- [ ] Supplementary materials formatted per journal guidelines
