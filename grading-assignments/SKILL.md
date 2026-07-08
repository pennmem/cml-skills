---
name: grading-assignments
description: Auto-grade COGS 4290 / PSYC 4290 ("Big Data, Memory, and the Human Brain") student assignments against the DataSolutions-BIDS reference answers, and explain how the student's approach differed from the solution. Use this skill whenever the user wants to grade, autograde, score, check, or give feedback on a student's notebook for this course, compare a student's saved answers to the truth/solution answers, build a grade report, or run the answer comparison — e.g. "grade this student's Module 4", "how close is this submission to the solution?", "autograde assignment 7", "compare the student's approach to ours for the SPC question", "make a feedback notebook for these students". Triggers also include mentions of the COGS4290_DataMemoryBrains repos, DataSolutions-BIDS, the `answers/Module_NN/` folders, `save_answer`, `compare_answers.py`, grade reports, or answer manifests. Do NOT use this for grading code outside this course, for nbgrader-style autograders in other classes, or for running the analyses themselves (that's the student's/instructor's job) — this skill compares already-saved answer arrays and deciphers approaches.
---

# grading-assignments

Automated grader for the COGS 4290 course (student repo
`COGS4290_DataMemoryBrains-BIDS`, solutions `DataSolutions-BIDS`). It compares the
data arrays a student plotted/computed per question against the reference answers,
then writes a per-question **report notebook** that lists the numeric closeness and,
at a grader-chosen verbosity, explains how the two *approaches* differed.

## How the pieces fit

```
 solution notebook ──run──> answers/Module_NN/ (TRUTH) ─┐
                                                         ├─ compare_answers.py ─> _grade_report.json
 student notebook  ──run──> answers/Module_NN/ (STUDENT)─┘                              │
                                                                                        ▼
 both notebooks ──> decipher_approach.py ──> (model writes) approach_Module_NN.json ──> build_report_notebook.py
                                                                                        │
                                                                                        ▼
                                                                        grade_report_Module_NN.ipynb
```

Everything is keyed on a per-module **answer manifest**
(`DataSolutions-BIDS/grader/manifests/Module_<NN>.json`) — the single source of truth
binding each answer `key` (e.g. `Q3.3_ave_spc`) to its question, type, tolerance, and
the solution's variable. See `references/manifest_schema.md`.

## Prerequisites (check first)
1. **Truth answers exist.** `DataSolutions-BIDS/answers/Module_<NN>/manifest.json` must
   be present — i.e. the instructor ran the solution notebook's grader cells. If not,
   grading returns `missing_truth` for everything; tell the user to run the solution
   (needs `/data/LTP_BIDS`, and the EEG/ML modules need Dask + possibly the RAM_maint
   account). Behavioral modules (01/04/06) run as a normal user.
2. **Student answers exist.** The student ran their notebook's grader cells to produce
   their `answers/Module_<NN>/`. If they didn't, keys show `missing_student`.
3. **Env.** Use the course conda env
   `/usr/global/ubuntu/miniforge3/25.3.1/envs/workshop_311_rhino2b/bin/python`
   (has numpy/pandas/nbformat). The comparison itself needs no course data.

## Workflow

Follow `references/workflow.md`. In brief:

1. **Compare** — run `scripts/compare_answers.py --modules <N...> --student <repo>`
   (truth defaults to `DataSolutions-BIDS`). Read the resulting
   `_grade_report.json` per module.
2. **Ask the grader the verbosity** if they didn't say — `none | little | some | all`
   (see `references/verbosity.md`). Default `some`.
3. **If verbosity > none**, run `scripts/decipher_approach.py` on the student and the
   solution notebook for each module, then **you (the model) write** an
   `approach_Module_<NN>.json` comparing the two approaches per question, guided by the
   stats (look where `rmse` is high / `pearson_r` is low). Respect the verbosity ceiling
   when writing (paraphrase, don't paste reference code at low levels).
4. **Build** — `scripts/build_report_notebook.py --stats … [--approach …] --verbosity …`
   → `grade_report_Module_<NN>.ipynb`.
5. **Report back** — pass/fail per module, failed questions one-liners, notebook paths,
   and flag any `missing_truth` / manifest `review_notes`.

## Preparing notebooks (instructor setup, occasional)

`scripts/prep_assignments.py` injects the grader cells (driven by the manifests). It's
idempotent — safe to re-run after editing a manifest.

- Student repo: `python scripts/prep_assignments.py --mode student --repo <student_repo> --all`
  → top instructions cell + a pre-filled `save_answer(...)` cell after each question +
  a "save for grading" note on each prompt.
- Solution repo: `python scripts/prep_assignments.py --mode solution --repo DataSolutions-BIDS --all`
  → save cells referencing the solution's real variables; run the notebooks to populate
  truth.

The same scripts are vendored into `DataSolutions-BIDS/grader/` (and `answer_io.py` +
`prep_assignments.py` into the student repo) so they run without this skill; this skill's
`scripts/` are the canonical copies.

## Scripts
- `scripts/compare_answers.py` — numeric comparison → `_grade_report.json` + `grade_summary.csv`
- `scripts/decipher_approach.py` — extract per-question code from a notebook for approach analysis
- `scripts/build_report_notebook.py` — render stats + approach diff into a report `.ipynb`
- `scripts/prep_assignments.py` — inject grader cells / prompt notes into notebooks
- `scripts/answer_io.py` — save/load answers (imported by the notebooks; canonical copy)

## References
- `references/manifest_schema.md` — the answer-manifest format + authoring rules
- `references/metrics.md` — what each closeness metric means + tolerance guidance
- `references/verbosity.md` — the none/little/some/all knob + approach-diff JSON format
- `references/workflow.md` — the full step-by-step grading loop

Each script has `--help`. Read the script before modifying it.
