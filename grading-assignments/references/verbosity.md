# Verbosity — how much the student is told

The grader chooses how much of the *approach analysis* (the "what differed between
your method and the reference" text) appears in the student's report notebook. The
numeric stats table always appears; verbosity only gates the prose/tips.

| level | int | 0-100 | what the student sees beyond the stats table |
|---|---|---|---|
| **none** | 0 | 0 | Nothing. Stats tables only. |
| **little** | 1 | 1–33 | A one-sentence hint, **failed questions only**. |
| **some** | 2 | 34–66 | "What differed" + a tip, **failed questions only**. (default) |
| **all** | 3 | 67–100 | Full approach comparison (reference approach, your approach, what differed, tip) for **every** question. |

Accepted by `build_report_notebook.py --verbosity`: the names (`none|little|some|all`),
a level int (`0..3`), or a 0-100 percentage (bucketed as above). Default: `some`.

## Approach-diff JSON (what the skill produces to feed the report)
The skill writes one file per module, e.g. `approach_Module_04.json`:

```json
{
  "module": 4,
  "questions": {
    "Q3.3_ave_spc": {
      "question": "3.3",
      "truth_approach": "grouped events by subject, computed each subject's SPC, then averaged the curves",
      "student_approach": "averaged the recalled flag over all rows pooled across subjects",
      "differences": "you pooled rows instead of averaging per-subject curves, which weights high-session subjects more",
      "tip": "compute one SPC per subject first, then average those",
      "one_liner": "average per-subject curves, not pooled rows"
    }
  }
}
```

Field usage by level: `little` uses `one_liner` (falls back to `tip`/`differences`);
`some` uses `differences` + `tip`; `all` uses all four fields. Keys match the manifest
answer `key`s so the report can line them up with the stats.

## Guidance for writing the diff text
- Base it only on the two extracted code blocks (`decipher_approach.py`) — describe what
  each actually did, not what you assume.
- When `allclose` is True, the approaches are numerically equivalent; still note stylistic
  differences at `all`, but keep `tip` empty/positive.
- When `pearson_r` is high but `rmse` is non-trivial, say "same shape, offset/scale differs"
  and point at the likely cause (normalization, averaging order, tolerance).
- Keep `one_liner` truly one line — it's the only thing shown at `little`.
- Never reveal full reference code at `little`/`some`; paraphrase the method.
