#!/usr/bin/env python3
"""compare_answers — numerically compare a student's saved answers against truth.

Reads per-module answer **spec manifests** (``grader/manifests/Module_<NN>.json``)
to know which answer keys exist and what tolerance each wants, then loads the
matching values from the student's and the truth's ``answers/Module_<NN>/``
directories (written by ``answer_io.save_answer``) and computes a battery of
closeness metrics per key.

For every key it reports a binary ``np.allclose`` pass/fail plus magnitude and
relational metrics (mean/max abs diff, RMSE, std of diff, relative L2 error,
Pearson r, fraction of elements within tolerance).  Results are written into the
**student's** answers folder as ``Module_<NN>/_grade_report.json`` and a combined
``grade_summary.csv``.

Usage
-----
    python compare_answers.py --modules 4 6 15 \
        --student /path/to/student_repo \
        [--truth /path/to/DataSolutions-BIDS/answers] \
        [--manifests /path/to/grader/manifests]

``--student`` / ``--truth`` may point at a repo root (an ``answers/`` child is
found automatically) or directly at an ``answers`` directory.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

import numpy as np

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))
import answer_io  # noqa: E402  (sibling module)

try:
    import pandas as pd
except Exception:  # pragma: no cover
    pd = None

DEFAULT_RTOL = 1e-3
DEFAULT_ATOL = 1e-6


# --------------------------------------------------------------------------- #
# metric core
# --------------------------------------------------------------------------- #
def _array_metrics(truth, student, rtol, atol):
    """Elementwise metrics for two same-shape numeric arrays (NaN-aware)."""
    t = np.asarray(truth, dtype=float)
    s = np.asarray(student, dtype=float)
    out = {
        "truth_shape": list(t.shape),
        "student_shape": list(s.shape),
        "shape_match": t.shape == s.shape,
    }
    if t.shape != s.shape:
        # last-ditch: compare a raveled common prefix so the grader still sees signal
        n = min(t.size, s.size)
        if n:
            tf, sf = t.ravel()[:n], s.ravel()[:n]
            out["note"] = "shape mismatch; metrics computed on raveled common prefix"
            t, s = tf, sf
        else:
            out["allclose"] = False
            return out

    mask = ~(np.isnan(t) | np.isnan(s))
    n_valid = int(mask.sum())
    out["n"] = int(t.size)
    out["n_valid"] = n_valid
    out["n_nan_mismatch"] = int((np.isnan(t) ^ np.isnan(s)).sum())
    if n_valid == 0:
        out["allclose"] = bool(np.array_equal(np.isnan(t), np.isnan(s)))
        return out

    tv, sv = t[mask], s[mask]
    diff = sv - tv
    absd = np.abs(diff)
    within = np.abs(diff) <= (atol + rtol * np.abs(tv))
    denom = np.linalg.norm(tv)

    out.update(
        {
            "allclose": bool(np.all(within)) and out["shape_match"] and out["n_nan_mismatch"] == 0,
            "frac_within_tol": float(within.mean()),
            "mean_abs_diff": float(absd.mean()),
            "max_abs_diff": float(absd.max()),
            "rmse": float(np.sqrt(np.mean(diff ** 2))),
            "std_diff": float(diff.std()),
            "rel_l2_error": float(np.linalg.norm(diff) / denom) if denom > 0 else None,
            "truth_mean": float(tv.mean()),
            "student_mean": float(sv.mean()),
            "truth_std": float(tv.std()),
            "student_std": float(sv.std()),
        }
    )
    if n_valid > 1 and tv.std() > 0 and sv.std() > 0:
        out["pearson_r"] = float(np.corrcoef(tv, sv)[0, 1])
    else:
        out["pearson_r"] = None
    return out


def _df_to_frame(x):
    return x if (pd is not None and isinstance(x, pd.DataFrame)) else None


def compare_values(truth, student, opts=None):
    """Compare two answer values and return a metrics dict with an ``allclose`` flag.

    Handles ndarrays, pandas DataFrame/Series, scalars, dicts, and string labels.
    ``opts`` may carry ``rtol``, ``atol``, and (for DataFrames) ``on`` = list of
    columns to compare.
    """
    opts = opts or {}
    rtol = float(opts.get("rtol", DEFAULT_RTOL))
    atol = float(opts.get("atol", DEFAULT_ATOL))

    # ---- pandas DataFrame ------------------------------------------------- #
    dft, dfs = _df_to_frame(truth), _df_to_frame(student)
    if dft is not None and dfs is not None:
        cols_t, cols_s = list(dft.columns), list(dfs.columns)
        on = opts.get("on") or [c for c in cols_t if c in cols_s]
        num = [c for c in on if c in dft.columns and c in dfs.columns
               and np.issubdtype(dft[c].dtype, np.number)
               and np.issubdtype(dfs[c].dtype, np.number)]
        res = {
            "kind": "dataframe",
            "columns_match": set(cols_t) == set(cols_s),
            "truth_columns": [str(c) for c in cols_t],
            "student_columns": [str(c) for c in cols_s],
            "compared_columns": [str(c) for c in num],
            "row_count_match": len(dft) == len(dfs),
        }
        if not num:
            res["allclose"] = False
            res["note"] = "no shared numeric columns to compare"
            return res
        m = _array_metrics(dft[num].to_numpy(), dfs[num].to_numpy(), rtol, atol)
        res.update(m)
        res["allclose"] = bool(m.get("allclose")) and res["row_count_match"]
        return res

    # ---- pandas Series ---------------------------------------------------- #
    if pd is not None and isinstance(truth, pd.Series) and isinstance(student, pd.Series):
        m = _array_metrics(truth.to_numpy(), student.to_numpy(), rtol, atol)
        m["kind"] = "series"
        return m

    # ---- dict (recurse) --------------------------------------------------- #
    if isinstance(truth, dict) and isinstance(student, dict):
        shared = [k for k in truth if k in student]
        sub = {str(k): compare_values(truth[k], student[k], opts) for k in shared}
        return {
            "kind": "dict",
            "keys_match": set(truth) == set(student),
            "shared_keys": [str(k) for k in shared],
            "allclose": bool(shared) and all(v.get("allclose") for v in sub.values()),
            "per_key": sub,
        }

    # ---- strings / label lists -------------------------------------------- #
    def _is_labels(x):
        return isinstance(x, str) or (
            isinstance(x, (list, tuple)) and all(isinstance(e, str) for e in x)
        )

    if _is_labels(truth) and _is_labels(student):
        if isinstance(truth, str):
            return {"kind": "string", "allclose": truth == student,
                    "truth": truth, "student": student}
        st, ss = set(truth), set(student)
        inter = st & ss
        return {
            "kind": "labels",
            "allclose": st == ss,
            "n_truth": len(st), "n_student": len(ss),
            "n_overlap": len(inter),
            "jaccard": len(inter) / len(st | ss) if (st | ss) else 1.0,
            "missing": sorted(st - ss), "extra": sorted(ss - st),
        }

    # ---- scalars / numeric arrays (default) ------------------------------- #
    try:
        m = _array_metrics(np.asarray(truth), np.asarray(student), rtol, atol)
        m["kind"] = "scalar" if np.ndim(truth) == 0 else "array"
        return m
    except Exception as exc:
        return {"kind": "unknown", "allclose": False, "error": str(exc)}


# --------------------------------------------------------------------------- #
# orchestration
# --------------------------------------------------------------------------- #
def _answers_root(path):
    """Accept a repo root or an answers dir; return the answers dir Path."""
    p = Path(path)
    if (p / "answers").is_dir():
        return p / "answers"
    return p


def _load_manifest_spec(manifests_dir, module):
    p = Path(manifests_dir) / f"Module_{int(module):02d}.json"
    if not p.exists():
        return None
    return json.loads(p.read_text())


def grade_module(module, student_root, truth_root, manifests_dir):
    """Grade one module; return the report dict and write it into the student dir."""
    spec = _load_manifest_spec(manifests_dir, module)
    report = {"module": int(module), "keys": {}}
    if spec is None:
        report["error"] = f"no spec manifest for module {module} in {manifests_dir}"
        return report
    report["title"] = spec.get("title")
    report["assignment"] = spec.get("assignment")

    for a in spec.get("answers", []):
        key = a["key"]
        opts = a.get("compare", {})
        rec = {"question": a.get("question"), "role": a.get("role"),
               "desc": a.get("student_hint") or a.get("desc")}
        try:
            truth_val = answer_io.load_answer(key, module, answers_root=truth_root)
        except Exception:
            rec["status"] = "missing_truth"
            report["keys"][key] = rec
            continue
        try:
            stud_val = answer_io.load_answer(key, module, answers_root=student_root)
        except Exception:
            rec["status"] = "missing_student"
            report["keys"][key] = rec
            continue
        try:
            metrics = compare_values(truth_val, stud_val, opts)
            rec["metrics"] = metrics
            rec["status"] = "pass" if metrics.get("allclose") else "fail"
        except Exception as exc:
            rec["status"] = "error"
            rec["error"] = str(exc)
        report["keys"][key] = rec

    statuses = [r["status"] for r in report["keys"].values()]
    report["summary"] = {
        "n_keys": len(statuses),
        "n_pass": statuses.count("pass"),
        "n_fail": statuses.count("fail"),
        "n_missing_student": statuses.count("missing_student"),
        "n_missing_truth": statuses.count("missing_truth"),
        "n_error": statuses.count("error"),
    }

    out_dir = answer_io.module_dir(module, student_root)
    (out_dir / "_grade_report.json").write_text(json.dumps(report, indent=2))
    return report


def _write_summary_csv(reports, student_root):
    path = Path(student_root) / "grade_summary.csv"
    fields = ["module", "key", "question", "status", "allclose",
              "frac_within_tol", "rmse", "mean_abs_diff", "max_abs_diff",
              "rel_l2_error", "pearson_r"]
    with open(path, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        for rep in reports:
            for key, rec in rep.get("keys", {}).items():
                m = rec.get("metrics", {})
                w.writerow({
                    "module": rep["module"], "key": key,
                    "question": rec.get("question"), "status": rec.get("status"),
                    "allclose": m.get("allclose"),
                    "frac_within_tol": m.get("frac_within_tol"),
                    "rmse": m.get("rmse"), "mean_abs_diff": m.get("mean_abs_diff"),
                    "max_abs_diff": m.get("max_abs_diff"),
                    "rel_l2_error": m.get("rel_l2_error"),
                    "pearson_r": m.get("pearson_r"),
                })
    return path


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--modules", "-m", nargs="+", type=int, required=True,
                    help="module numbers to grade, e.g. --modules 4 6 15")
    ap.add_argument("--student", required=True,
                    help="student repo root or answers/ dir")
    ap.add_argument("--truth", default=None,
                    help="truth repo root or answers/ dir "
                         "(default: DataSolutions-BIDS/answers next to the manifests)")
    ap.add_argument("--manifests", default=None,
                    help="dir of Module_<NN>.json spec manifests "
                         "(default: <truth repo>/grader/manifests)")
    args = ap.parse_args(argv)

    student_root = _answers_root(args.student)

    if args.truth:
        truth_repo = Path(args.truth)
    else:
        truth_repo = Path("/home1/zrentala/DataSolutions-BIDS")
    truth_root = _answers_root(truth_repo)

    if args.manifests:
        manifests_dir = Path(args.manifests)
    else:
        # look next to the truth repo, else next to this script's course copy
        cand = (truth_repo if (truth_repo / "grader").is_dir() else truth_repo.parent)
        manifests_dir = cand / "grader" / "manifests"
        if not manifests_dir.is_dir():
            manifests_dir = Path("/home1/zrentala/DataSolutions-BIDS/grader/manifests")

    reports = []
    for mod in args.modules:
        rep = grade_module(mod, student_root, truth_root, manifests_dir)
        reports.append(rep)
        s = rep.get("summary", {})
        if "error" in rep:
            print(f"Module {mod:02d}: {rep['error']}")
        else:
            print(f"Module {mod:02d} ({rep.get('title','')}): "
                  f"{s.get('n_pass',0)}/{s.get('n_keys',0)} pass, "
                  f"{s.get('n_fail',0)} fail, "
                  f"{s.get('n_missing_student',0)} missing")
    csv_path = _write_summary_csv(reports, student_root)
    print(f"\nWrote per-module _grade_report.json and {csv_path}")
    return reports


if __name__ == "__main__":
    main()
