# Worked examples: before and after critique

Two one-off generators that produced Beamer decks for three CML papers
(CohenKahana2019, AGGA16memvar, Heal15agingcmr). Read them **side-by-side**
to see how the skill's rules translate into LaTeX.

**These are not reusable tools.** They hardcode paper lists, figure-filename
mappings, and per-slide LaTeX strings. Don't run them on new papers; write a
fresh generator per talk, or use the `plan_deck.py` + `compile_beamer.py`
pipeline that works from a slide-plan data structure.

## The two files

| File | What it does | Compliance |
|---|---|---|
| `build_decks_v1_original.py` | Initial auto-generated output for 8 decks (3 papers + synthesis, each built twice from local and GitHub sources). | Pre-critique. Demonstrates the failure modes the skill now prohibits. |
| `build_decks_v2_refined.py` | Rebuild of 3 single-paper decks after a written critique. | Applies the skill rules encoded in SKILL.md §11-12, `visual_design.md`, `beamer_generation.md`. |

## What the v1 → v2 diff illustrates

Each rule in the skill maps to a concrete edit you can see in the diff:

| Skill rule | v1 failure | v2 fix |
|---|---|---|
| SKILL.md §11.1 — no em-dashes | `disorders of affect regulation, but their hallmark symptoms are \emph{memorial}: rumination, mood-congruent recall, intrusive recollection` | split into two sentences; bulleted sub-list for the three symptoms |
| SKILL.md §11.2 — no inline comma-lists | `Usual explanations: uncontrolled exogenous factors word frequency, concreteness, emotional valence, fatigue, time of day, sleep` | sub-bullets grouped by category |
| SKILL.md §11.3 — no filler intensifiers | `fluctuates strikingly from day to day` | `changes from list to list and session to session, even under near-constant conditions` |
| SKILL.md §11.4 — no pipeline metadata on title | `\institute{... \\ {\small Data source: Prepared local mirror}}` | `\institute{Computational Memory Lab \\ University of Pennsylvania}` |
| SKILL.md §12 — Conclusions + Next Steps | Neither deck had a Conclusions frame; implications were merged into Discussion | Two separate frames before Acknowledgments |
| `visual_design.md` figure rules | `\includegraphics[width=0.65\textwidth]` without centering or height bound; figure sometimes overflows | `\centering` + `width=0.80\textwidth, height=0.65\textheight, keepaspectratio` |
| `visual_design.md` max 2 figures/slide | Some slides had 3-panel includes | Split into solo slides or same-type side-by-side |
| `visual_design.md` summary bullets on figure slides | Many figure frames had no bullets | 2-3 bullets stating what the figure shows and the takeaway |

## How to use this as a future skill reference

When editing the skill, test your changes by picking one rule from the list
above, find the v1 violation in `build_decks_v1_original.py`, and confirm
that the corresponding fix in `build_decks_v2_refined.py` matches what your
updated skill reference would prescribe. If it doesn't match, the reference
is out of sync with the working examples.

## Re-running

Both scripts assume they live next to the CML paper mirrors:

- `/home1/zrentala/github_migration/work/papers/` (local prepared mirror)
- `/tmp/pennmem-clones/` (GitHub shallow clones, for v1 only)

And write output to `/home1/zrentala/beamer-workshop/{local,github,refined}/`.

If paths change, update the `ROOT`, `LOCAL_PAPERS`, `GITHUB_PAPERS` constants
at the top of each file.
