#!/usr/bin/env python3
"""build_report_notebook — render a per-question grade report as a Jupyter notebook.

Consumes the JSON written by ``compare_answers.py`` (numeric stats) and, optionally,
an *approach-diff* JSON produced by the ``grading-assignments`` skill (a natural-
language "what differed between the two approaches" per question).  Emits a
``grade_report_Module_<NN>.ipynb`` that lists, for each question, a pass/fail badge,
a metrics table, optional truth-vs-student figure thumbnails, and an approach
section whose depth is controlled by ``--verbosity``.

Verbosity (how much the *student* is shown)::

    none | 0        stats only, no approach text
    little | 1      one-sentence hint, failed questions only
    some | 2        differences + tip, failed questions only   (default)
    all | 3         full approach comparison for every question

Numeric values also accepted: 0->none, and >3 is read as a 0-100 percentage
(1-33 little, 34-66 some, 67-100 all).

Usage
-----
    python build_report_notebook.py --stats path/to/_grade_report.json \
        [--approach path/to/approach_Module_04.json] \
        [--verbosity some] [--out grade_report_Module_04.ipynb]

``--stats`` accepts one or more report JSON files (one notebook is written per module).
"""

from __future__ import annotations

import argparse
import base64
import json
import re
from pathlib import Path

import nbformat
from nbformat.v4 import new_code_cell, new_markdown_cell, new_notebook

BADGE = {
    "pass": "✅ **PASS**",
    "fail": "❌ **FAIL**",
    "missing_student": "⚠️ **not submitted**",
    "missing_truth": "⚠️ **no truth answer**",
    "error": "⚠️ **error**",
}

_LEVELS = {"none": 0, "little": 1, "some": 2, "all": 3}
_METRIC_LABELS = [
    ("allclose", "np.allclose"),
    ("frac_within_tol", "fraction within tol"),
    ("rmse", "RMSE"),
    ("mean_abs_diff", "mean |Δ|"),
    ("max_abs_diff", "max |Δ|"),
    ("std_diff", "std(Δ)"),
    ("rel_l2_error", "relative L2 error"),
    ("pearson_r", "Pearson r"),
    ("truth_mean", "truth mean"),
    ("student_mean", "student mean"),
]


def parse_verbosity(v):
    """Return an int level 0..3 from a name, level int, or 0-100 percentage."""
    if v is None:
        return 2
    s = str(v).strip().lower()
    if s in _LEVELS:
        return _LEVELS[s]
    try:
        n = int(float(s))
    except ValueError:
        return 2
    if n <= 3:
        return max(0, n)
    if n <= 33:
        return 1
    if n <= 66:
        return 2
    return 3


def _fmt(x):
    if isinstance(x, bool):
        return "✅" if x else "❌"
    if isinstance(x, float):
        if x != x:  # NaN
            return "nan"
        return f"{x:.4g}"
    return str(x)


def _metrics_table(metrics):
    if not metrics:
        return "_no metrics_"
    rows = ["| metric | value |", "|---|---|"]
    for kind_key in ("kind",):
        if metrics.get(kind_key):
            rows.append(f"| kind | {metrics[kind_key]} |")
    if "shape_match" in metrics:
        rows.append(f"| shape match | {_fmt(metrics['shape_match'])} "
                    f"(truth {metrics.get('truth_shape')}, "
                    f"student {metrics.get('student_shape')}) |")
    if "columns_match" in metrics:
        rows.append(f"| columns match | {_fmt(metrics['columns_match'])} |")
        rows.append(f"| compared columns | {metrics.get('compared_columns')} |")
    for mkey, label in _METRIC_LABELS:
        if mkey in metrics and metrics[mkey] is not None:
            rows.append(f"| {label} | {_fmt(metrics[mkey])} |")
    if metrics.get("note"):
        rows.append(f"| note | {metrics['note']} |")
    return "\n".join(rows)


def _img_html(png_path, label):
    try:
        data = base64.b64encode(Path(png_path).read_bytes()).decode()
        return (f'<figure style="display:inline-block;margin:4px;text-align:center">'
                f'<img src="data:image/png;base64,{data}" style="max-width:320px"/>'
                f'<figcaption>{label}</figcaption></figure>')
    except Exception:
        return ""


def _figures_block(key, module, student_root, truth_root):
    """Return an HTML block with truth/student thumbnails if PNG snapshots exist."""
    if not (student_root and truth_root):
        return None
    md = f"Module_{module:02d}"
    tp = Path(truth_root) / md / f"{key}.png"
    sp = Path(student_root) / md / f"{key}.png"
    imgs = []
    if tp.exists():
        imgs.append(_img_html(tp, "truth"))
    if sp.exists():
        imgs.append(_img_html(sp, "student"))
    imgs = [i for i in imgs if i]
    return "<div>" + "".join(imgs) + "</div>" if imgs else None


def _qsort_key(key, rec):
    """Natural-sort tolerant of letter sub-parts: 1a < 1b < 2 < 3.3."""
    q = rec.get("question") or ""
    parts = []
    for p in str(q).split("."):
        m = re.match(r"\s*([0-9]*)([a-z]*)", p.strip().lower())
        parts.append((int(m.group(1)) if m.group(1) else 0, m.group(2)))
    return (parts, key)


def _approach_section(level, status, adiff):
    """Return the markdown approach text for one question at the given level."""
    if level == 0 or not adiff:
        return None
    failed = status != "pass"
    if level == 1:
        if not failed:
            return None
        line = adiff.get("one_liner") or adiff.get("tip") or adiff.get("differences")
        return f"**Hint:** {line}" if line else None
    if level == 2:
        if not failed:
            return None
        parts = []
        if adiff.get("differences"):
            parts.append(f"**What differed:** {adiff['differences']}")
        if adiff.get("tip"):
            parts.append(f"**Tip:** {adiff['tip']}")
        return "\n\n".join(parts) if parts else None
    # level 3 — everything, every question
    parts = ["#### Approach comparison"]
    if adiff.get("truth_approach"):
        parts.append(f"**Reference approach:** {adiff['truth_approach']}")
    if adiff.get("student_approach"):
        parts.append(f"**Your approach:** {adiff['student_approach']}")
    if adiff.get("differences"):
        parts.append(f"**What differed:** {adiff['differences']}")
    if adiff.get("tip"):
        parts.append(f"**Tip:** {adiff['tip']}")
    return "\n\n".join(parts)


def build_notebook(report, approach=None, verbosity="some",
                   student_root=None, truth_root=None):
    """Return an nbformat notebook object for a single module *report* dict."""
    level = parse_verbosity(verbosity)
    approach = approach or {}
    aq = approach.get("questions", {})
    module = report["module"]
    cells = []

    s = report.get("summary", {})
    title = report.get("title", "")
    cells.append(new_markdown_cell(
        f"# Grade report — Module {module:02d}"
        + (f": {title}" if title else "")
        + "\n\n"
        + (f"**Assignment {report['assignment']}** &nbsp;·&nbsp; "
           if report.get("assignment") is not None else "")
        + f"Passed **{s.get('n_pass', 0)} / {s.get('n_keys', 0)}** checks "
        + f"&nbsp;·&nbsp; {s.get('n_fail', 0)} fail "
        + f"&nbsp;·&nbsp; {s.get('n_missing_student', 0)} not submitted"
        + f"\n\n_Detail level: **{['none','little','some','all'][level]}**_"
    ))

    for key, rec in sorted(report.get("keys", {}).items(),
                           key=lambda kv: _qsort_key(kv[0], kv[1])):
        status = rec.get("status", "error")
        q = rec.get("question", "?")
        desc = rec.get("desc") or ""
        header = f"## Question {q} — {BADGE.get(status, status)}"
        body = [f"**{key}**" + (f" — {desc}" if desc else "")]
        if rec.get("status") in ("missing_student", "missing_truth"):
            body.append(f"_{status.replace('_', ' ')}_")
        else:
            body.append(_metrics_table(rec.get("metrics", {})))
        cells.append(new_markdown_cell(header + "\n\n" + "\n\n".join(body)))

        figs = _figures_block(key, module, student_root, truth_root)
        if figs:
            cells.append(new_markdown_cell(figs))

        approach_md = _approach_section(level, status, aq.get(key))
        if approach_md:
            cells.append(new_markdown_cell(approach_md))
        elif level >= 2 and status != "pass" and not aq.get(key):
            cells.append(new_markdown_cell(
                "_Run the `grading-assignments` skill to populate an approach "
                "comparison for this question._"))

    nb = new_notebook(cells=cells)
    nb.metadata["grade_report"] = {"module": module, "verbosity": level}
    return nb


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--stats", nargs="+", required=True,
                    help="one or more _grade_report.json files")
    ap.add_argument("--approach", default=None,
                    help="optional approach-diff JSON (or a dir of them)")
    ap.add_argument("--verbosity", default="some",
                    help="none|little|some|all, a level 0-3, or a 0-100 percentage")
    ap.add_argument("--out", default=None,
                    help="output .ipynb (default: grade_report_Module_<NN>.ipynb "
                         "next to each stats file)")
    ap.add_argument("--student-root", default=None,
                    help="student answers dir, to embed figure thumbnails")
    ap.add_argument("--truth-root", default=None,
                    help="truth answers dir, to embed figure thumbnails")
    args = ap.parse_args(argv)

    approach_arg = Path(args.approach) if args.approach else None
    written = []
    for stats_path in args.stats:
        report = json.loads(Path(stats_path).read_text())
        module = report["module"]

        approach = None
        if approach_arg:
            p = approach_arg
            if p.is_dir():
                p = p / f"approach_Module_{module:02d}.json"
            if p.exists():
                approach = json.loads(p.read_text())

        nb = build_notebook(report, approach, args.verbosity,
                            args.student_root, args.truth_root)
        out = (Path(args.out) if args.out
               else Path(stats_path).parent / f"grade_report_Module_{module:02d}.ipynb")
        nbformat.write(nb, str(out))
        written.append(str(out))
        print(f"Module {module:02d}: wrote {out}")
    return written


if __name__ == "__main__":
    main()
