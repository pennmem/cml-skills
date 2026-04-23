---
name: poster-from-papers
description: Use this skill whenever a user in the Computational Memory Lab (CML) wants to turn one or more CML papers into a conference poster — beamerposter LaTeX as the primary output, with a single-slide PowerPoint version as parallel output when requested. Triggers include "make a poster from this paper", "build a poster for SfN on my PTSD paper", "CNS poster from CohenKahana2019", "I need a 48x36 poster", or any request to convert CML paper content into a poster. The skill assumes papers are already staged as bundles by the `paper-acquisition` skill; it does not search for or download papers itself. Do NOT use this for slide decks (use `beamer-from-papers` instead), for generic posters unrelated to CML papers, or for non-scientific poster styles (marketing, events).
---

# poster-from-papers

Turn one or more CML paper bundles into a single-page conference poster, with beamerposter LaTeX as the primary output and an optional parallel single-slide PowerPoint version. Built for scientific poster sessions (SfN, CNS, Psychonomics, CogSci) where a viewer might stop for 30 seconds to 3 minutes and the poster has to carry the core argument without a speaker.

## Relationship to other skills

**Upstream (required input).** This skill consumes paper bundles produced by `paper-acquisition`. Always run `paper-acquisition` first if bundles don't already exist. If the user asks for a poster without having run acquisition, do that step transparently — don't make them run two separate commands for what they asked as one thing.

**Sibling (similar architecture).** This skill mirrors `beamer-from-papers` in methodology: bundle → deep read → plan → emit LaTeX → compile → present. The *content strategy is different* though — a poster is much more aggressive compression than a 25-slide talk. See `references/content_selection.md`.

**Lateral (optional enrichment).** If the `memory-publications` skill is installed, consult these files to improve output quality:

```bash
for d in ./skills/memory-publications /mnt/skills/user/memory-publications \
         ~/.claude/skills/memory-publications ../memory-publications; do
  [ -f "$d/SKILL.md" ] && MEMPUB_DIR="$d" && break
done
```

| memory-publications file | Used by this skill for |
|---|---|
| `references/domain-knowledge.md` | Correct terminology in poster blocks (CMR ≠ TCM; TAG bands; "temporal context reinstatement" not "memory processes") |
| `references/writing-style.md` | Voice for section blurbs — posters use a terser register than slides, but still Kahana-ish |
| `references/research-index.json` | Topic-thread-aware layout (a brain-stim poster needs stim parameters; an EEG poster needs frequency bands) |
| `references/current-projects.md` | When the paper is one of the user's active manuscripts, pull target venue / lead authors / status |

When `memory-publications` is absent, use the fallbacks documented in this skill's reference files. The skill works standalone.

## High-level workflow

1. **Confirm inputs** — one or more paper bundles.
2. **Elicit poster parameters** — size, orientation, column count, venue. Use sensible defaults.
3. **Read the paper(s) deeply** — same strategy as beamer-from-papers (see `references/reading_strategy.md` in that skill for the full approach, or this skill's local summary below).
4. **Select content aggressively** — for a poster, most of the paper gets cut. See `references/content_selection.md`.
5. **Plan the layout** — sections, column assignment, figure placement.
6. **Emit the beamerposter source** — using `assets/cml_poster_template.tex`.
7. **Compile** to PDF.
8. **Present** — PDF, `.tex`, and a brief summary.

## Eliciting poster parameters

Ask in a single turn if the user didn't specify:

```
Building a poster from <N> paper(s). Quick parameters:

1. Size: [48x36-landscape | 36x48-portrait | A0-portrait | A0-landscape | custom]
   Default: 48x36-landscape (standard US conference poster)

2. Columns: [2 | 3 | 4]
   Default: 3 (standard for 48x36 landscape)

3. Venue / audience: [SfN | CNS | Psychonomics | CogSci | department | custom]
   Default: generic — influences acknowledgment language and whether you
   lean methods-heavy (SfN) or theory-heavy (CogSci)

4. Output formats: [pdf-only | pdf+tex | pdf+tex+pptx]
   Default: pdf+tex
```

If the user already specified any of these, skip those questions. "Just use defaults" → go.

## Deep reading

Same deep-reading strategy as `beamer-from-papers`:

1. Read `drafts/selected.tex` (or the PDF) end to end.
2. Load every figure from `figures/` with vision — describe what each actually shows, not just the caption.
3. Parse citations to identify the load-bearing prior work.

For posters specifically, pay extra attention to:

- The paper's **abstract** — it's already compressed to near-poster length; mine it.
- The paper's **discussion section** — the first 1-2 paragraphs usually state the headline claims, which become the poster's conclusions block.
- The "money" figure — the one the discussion leads with. That's your anchor figure.

If the user has `memory-publications` installed, also consult `memory-publications/references/domain-knowledge.md` once at the start so terminology stays precise.

See `references/reading_strategy.md` (the one in this skill's folder — it's a short pointer; the main reading strategy lives in beamer-from-papers and mostly still applies).

## Content selection: the poster-specific part

**This is where posters differ most from slide decks.** A 25-slide talk can show every major figure and walk the audience through them; a poster can't. A viewer at a conference will stop for 30s–3min. You have to fit the whole argument into:

- A title bar with authors and affiliations
- A **motivation / question block** (3-5 sentences)
- A **methods block** (2-3 sentences + one schematic figure, or just a schematic figure with callouts)
- **3-5 results blocks** — each one is a single figure with a 1-2 sentence interpretation
- A **conclusions block** (3-5 bullets, each a complete sentence)
- A **references + acknowledgments footer**

That's it. Everything else goes. See `references/content_selection.md` for the heuristics on what to cut and what to keep.

## Planning the layout

Standard 48×36 landscape, 3 columns:

```
┌────────────────────────────────────────────────────────────┐
│  [ TITLE BAR: Title, Authors, Affiliations, Lab Logo ]      │
├──────────────────┬───────────────────┬─────────────────────┤
│  MOTIVATION      │  RESULT 1 (figure) │  RESULT 3 (figure)  │
│                  │                   │                     │
│  QUESTION        │                   │                     │
│                  │                   │                     │
│  METHODS         │  RESULT 2 (figure) │  CONCLUSIONS        │
│  (+ schematic)   │                   │                     │
│                  │                   │  REFERENCES         │
│                  │                   │  ACKNOWLEDGMENTS    │
└──────────────────┴───────────────────┴─────────────────────┘
```

For 36×48 portrait, the same sections in a different arrangement (more vertical, 2 columns typically). For A0 and custom sizes, the planner adjusts.

Column assignment rule: left column sets up the work; middle column shows it; right column wraps up. Tweak as content demands — sometimes results are so figure-heavy they need two columns.

See `references/poster_design.md` for dimensions, fonts, color conventions, and readability rules.

## Emitting the beamerposter source

Use `assets/cml_poster_template.tex` as the starting point. It uses the same CML navy-blue palette as the Beamer template. Key structural elements:

```latex
\begin{frame}{}
  \begin{columns}[T]
    \begin{column}{0.32\textwidth}
      \begin{block}{Motivation}
        ... motivation text ...
      \end{block}
      \begin{block}{Methods}
        ... methods text ... \\
        \includegraphics[width=\textwidth]{figures/design.pdf}
      \end{block}
    \end{column}
    \begin{column}{0.32\textwidth}
      ... results blocks ...
    \end{column}
    \begin{column}{0.32\textwidth}
      ... conclusions + references ...
    \end{column}
  \end{columns}
\end{frame}
```

See `references/beamerposter_patterns.md` for detailed LaTeX patterns.

## Figures

Copy figures from each bundle's `figures/` directory into a local `figures/` alongside the `.tex`. Same convention as beamer-from-papers.

Poster figures should be large enough to be readable at 4-6 feet. If a paper's figure is multi-panel with tiny subpanels, consider cropping it to a single panel rather than shrinking the whole thing below legibility.

## Compiling

`pdflatex` twice (no bibtex typically — references on a poster are hand-formatted in a compact style). Use `scripts/compile_poster.py`. If bibtex *is* needed (e.g., user wants full-format references), the script handles that too.

Poster PDFs are LARGE (a 48×36 poster at 300dpi can be 50MB+). The compile script runs with `-dPDFSETTINGS=/prepress` to keep the file reasonable while preserving figure quality.

## PPTX output

Native PPTX via `python-pptx` — a single gigantic slide sized to the poster dimensions. Font sizes scaled up accordingly (title ~72pt, block headings ~44pt, body ~32pt for 48×36).

See `references/pptx_poster.md` and `scripts/generate_pptx_poster.py`.

## Reporting

Tell the user:

- Path to the compiled PDF
- Path to the `.tex` source
- Path to the `.pptx` if requested
- Poster dimensions and rough print cost estimate if you know it ($40-60 for 48×36 at a typical university print shop)
- Any compile warnings (missing figures, block overflow)
- One-line "what would you like to change?" prompt

## Reference files

- `references/reading_strategy.md` — short pointer; main strategy lives in beamer-from-papers
- `references/content_selection.md` — what to keep, what to cut (this is the skill's heart)
- `references/poster_design.md` — dimensions, fonts, colors, readability conventions
- `references/beamerposter_patterns.md` — LaTeX patterns specific to beamerposter
- `references/figure_selection.md` — picking the 3-5 figures that carry the poster
- `references/pptx_poster.md` — python-pptx patterns for poster-sized slides
- `references/latex_setup.md` — troubleshooting missing beamerposter / fonts

## Assets

- `assets/cml_poster_template.tex` — the starter template (CML navy blue)
- `assets/example_poster.tex` — reference for how a rendered single-paper poster looks

## Scripts

- `scripts/compile_poster.py` — wraps pdflatex passes + error filtering (mostly shared with beamer-from-papers but adapted for single-page)
- `scripts/plan_poster.py` — builds the poster plan from bundles + parameters
- `scripts/generate_pptx_poster.py` — native PPTX poster emitter (single slide sized to poster)
