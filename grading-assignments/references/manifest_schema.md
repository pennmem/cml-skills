# Answer manifest schema

One JSON manifest per module lives in `DataSolutions-BIDS/grader/manifests/Module_<NN>.json`
(a copy ships in the student repo). It is the **single source of truth** that binds a
stable answer key to its question, expected type/shape, the solution's real variable,
and a student-facing hint. Every grader component reads it:

- `answer_io.save_answer` writes answers under the manifest's `key`s.
- `prep_assignments.py` inserts grader cells + prompt notes from the manifest.
- `compare_answers.py` loads the `key`s and applies each `compare` tolerance.
- `decipher_approach.py` maps question code back to `key`s.

`<NN>` is the **student** module number (e.g. the Machine-Learning assignment is
`Module_16.json` even though its solution notebook is `Solution_Module_17.ipynb`).

## Top-level fields

| field | required | notes |
|---|---|---|
| `module` | yes | student module number (int) |
| `assignment` | no | assignment number shown in reports |
| `title` | no | assignment title |
| `student_notebook` | yes | filename in the student repo |
| `solution_notebook` | yes | filename in `DataSolutions-BIDS` |
| `review_notes` | no | array of strings flagging drift / bindings a human should verify |
| `answers` | yes | array of answer entries (below) |

## Answer entry fields

| field | required | notes |
|---|---|---|
| `key` | yes | stable id, format `Q<N.M>_<short_snake_name>` (e.g. `Q3.3_ave_spc`) |
| `question` | yes | sub-question as a string `"N.M"` — must match a `# Question N.M` code cell / `## Question N` section |
| `role` | yes | `"plot"` (an array/df that gets plotted) or `"value"` (a reported number/label) |
| `type` | yes | `scalar` \| `array` \| `dataframe` \| `series` \| `labels` \| `json` |
| `columns` | df only | list of column names |
| `shape_hint` | no | e.g. `"(24, 2)"` — shown to students |
| `solution_var` | one of these | exact variable in the solution holding the answer **at that sub-question's cell** |
| `solution_expr` | one of these | a python expression, used when the answer isn't a single variable (e.g. `spcs_by_cond[16000]`) |
| `student_hint` | yes | concise prose describing what to save (no need to repeat type/columns) |
| `skip_solution` | no | `true` → don't emit a solution grader cell (solution doesn't produce this yet) |
| `needs_solution_update` | no | `true` → flags a drift the instructor must reconcile |
| `compare` | no | tolerances (below); omit for `labels`/`json` (compared by set/exact) |

### `compare` options
- `rtol`, `atol` — passed to the `np.allclose`-style check (defaults `rtol=1e-3`, `atol=1e-6`).
  Use `atol=0, rtol=0` for exact-integer answers (counts).
- `on` — (dataframe) list of numeric columns to compare (e.g. `["recalled"]`); defaults to all shared numeric columns.

## Authoring rules

1. Create one entry for **every quantity that gets plotted** (`plt.plot/hist/errorbar/
   imshow/semilogx`, `sns.*`, `ax.plot`, `topoplot`, …) and every **numeric/label answer
   reported** for a sub-question. Skip purely written (`YOUR ANSWER HERE`) answers.
2. `solution_var` must name the variable **as it exists right after that sub-question's
   `# Question N.M` cell**. Variable reuse across sub-parts is fine — grader cells are
   placed per sub-question, so each captures the value at its own point.
3. If the answer is computed inline (never bound to a variable), either add a one-line
   binding in the solution and use `solution_var`, or use `solution_expr`. Note any
   binding you add in `review_notes`.
4. If a sub-question's answer variable is only finalized in a **later untagged cell**
   (no `# Question N.M` comment), the grader cell falls back to the end of the
   `## Question N` section — note it in `review_notes`.
5. **Drift:** when the current student prompt asks for something the solution no longer
   produces, mark the entry `skip_solution: true, needs_solution_update: true` and add a
   `review_notes` line. Prefer the *student prompt* as canonical.

See `Module_04.json` for a complete worked example.
