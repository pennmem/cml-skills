# Grading workflow (detail)

The full loop the skill runs when asked to grade one or more student submissions.

## Inputs the skill needs
- **Student answers**: the student's repo root or its `answers/` dir (they run their
  notebook's grader cells to produce `answers/Module_<NN>/`).
- **Truth**: `DataSolutions-BIDS` (default) — the instructor must have run the solution
  notebooks so `DataSolutions-BIDS/answers/Module_<NN>/` exists.
- **Modules**: which module numbers to grade.
- **Verbosity**: none | little | some | all (default some).
- Optionally the two notebooks themselves, for approach analysis.

## Steps

### 1. Numeric comparison
```bash
python scripts/compare_answers.py --modules 4 6 --student <student_repo> \
    --truth /home1/zrentala/DataSolutions-BIDS \
    --manifests /home1/zrentala/DataSolutions-BIDS/grader/manifests
```
Writes `<student>/answers/Module_<NN>/_grade_report.json` + `grade_summary.csv`.
Read those to see per-key `status` + metrics.

### 2. Decipher each approach (only needed for verbosity > none)
For every module, extract the per-question code from **both** notebooks:
```bash
python scripts/decipher_approach.py --notebook <student>/Module_04_*.ipynb \
    --manifest <manifests>/Module_04.json --out /tmp/appr_student_04.json
python scripts/decipher_approach.py --notebook DataSolutions-BIDS/Solution_Module_04.ipynb \
    --manifest <manifests>/Module_04.json --out /tmp/appr_truth_04.json
```
Each file maps `question -> {prompt, code, answer_keys}`.

### 3. Compare approaches (this is the model's job)
Read the two extractions side by side. For each answer `key`, and **guided by the stats**
from step 1 (a failing `rmse`/`pearson_r` tells you where to look), write the approach-diff
entry described in `verbosity.md`: `truth_approach`, `student_approach`, `differences`,
`tip`, `one_liner`. Only cover what the code actually shows. Save one
`approach_Module_<NN>.json` per module.

Tips:
- Passing keys → approaches are equivalent; keep `tip` empty/positive.
- High `pearson_r`, non-trivial `rmse` → "same shape, scale/offset differs" (look for
  normalization, averaging order, unit conversion).
- `missing_student` → the student didn't save it; the "difference" is that it wasn't
  produced — say so, don't invent a method.
- Respect the verbosity ceiling when writing: at `little`/`some`, paraphrase; never paste
  reference code.

### 4. Build the report notebook
```bash
python scripts/build_report_notebook.py \
    --stats <student>/answers/Module_04/_grade_report.json \
    --approach /tmp/approach_Module_04.json \
    --verbosity some \
    --student-root <student>/answers --truth-root DataSolutions-BIDS/answers \
    --out <student>/grade_report_Module_04.ipynb
```
`--student-root`/`--truth-root` let the report embed the saved figure thumbnails
(`<key>.png`) side by side when they exist.

### 5. Report back to the grader
Tell them: pass/fail counts per module, which questions failed and why (one line each),
where the report notebook(s) landed, and flag any `missing_truth` (solution not yet run)
or manifest `review_notes` that need attention.

## Scaling to many students
Loop step 1 over each student dir, then steps 2–4 per student. The numeric stats are cheap;
the approach analysis (step 3) is the model-time cost — for large classes, run it only at
the verbosity the grader chose (at `none` you can skip steps 2–3 entirely).
