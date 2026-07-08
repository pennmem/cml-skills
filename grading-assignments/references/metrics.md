# Comparison metrics

`compare_answers.py` (`compare_values`) is type-aware. For each answer key present in
both the student's and the truth's `answers/Module_<NN>/`, it loads both values and
computes the metrics below. The **binary verdict** is `allclose` (an
`np.allclose`-style check with the key's `rtol`/`atol`); everything else is diagnostic.

## By type

| value type | how it's compared | key metrics |
|---|---|---|
| **ndarray / list of numbers** | elementwise after aligning shape (NaN-masked) | `allclose`, `frac_within_tol`, `rmse`, `mean_abs_diff`, `max_abs_diff`, `std_diff`, `rel_l2_error`, `pearson_r`, `truth/student mean/std`, `shape_match` |
| **scalar** | same as a 0-d array | `allclose`, `mean_abs_diff` (= |Δ|), `rmse` |
| **DataFrame** | on shared numeric columns (or `compare.on`) | `columns_match`, `row_count_match`, `compared_columns`, plus all array metrics on the stacked columns |
| **Series** | as an array | array metrics |
| **dict** | recurse per shared key | `keys_match`, `per_key` (nested results); `allclose` = all sub-keys close |
| **labels (str / list of str)** | set/exact | `allclose` (exact set match), `jaccard`, `n_overlap`, `missing`, `extra` |

## Metric definitions
- **allclose** — `all(|s - t| <= atol + rtol*|t|)` over valid (non-NaN) elements, requiring shape match and no NaN-pattern mismatch. This is the pass/fail flag.
- **frac_within_tol** — fraction of elements meeting the per-element tolerance (partial credit signal).
- **rmse** — `sqrt(mean((s - t)^2))`.
- **mean_abs_diff / max_abs_diff / std_diff** — L1 mean, L∞, and spread of the residual.
- **rel_l2_error** — `||s - t|| / ||t||` (scale-free error; good for power/z-score arrays).
- **pearson_r** — correlation of flattened arrays; distinguishes "right shape, wrong offset/scale" (high r, high rmse) from "wrong pattern" (low r).
- **jaccard** — for label sets, `|intersection| / |union|`.

## Status values (per key)
`pass` · `fail` · `missing_student` (student never saved it) · `missing_truth` (no ground
truth yet — the solution wasn't run) · `error` (incomparable types / load failure).

## Choosing tolerances (in the manifest `compare`)
- Exact integer counts → `{"atol": 0, "rtol": 0}`.
- Probabilities / SPCs → `{"rtol": 1e-3, "atol": 1e-6}`.
- Log-power, z-power, ML outputs (noisy, method-dependent) → `{"rtol": 1e-2, "atol": 1e-3}`.
- AUC scalars → `{"atol": 0.02}`.

`rmse` and `pearson_r` are the most useful for reports: a student who used a slightly
different but valid method usually shows **high `pearson_r`, small `rmse`** even when
`allclose` is False — worth surfacing as "close, minor numerical difference" rather than
"wrong".
