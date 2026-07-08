#!/usr/bin/env python3
"""decipher_approach — extract, per question, the code that produced each answer.

Given a notebook (student or solution) and optionally its answer manifest, this
segments the notebook by ``## Question N`` / ``# Question X.Y`` anchors and emits,
for each sub-question, the prompt text and the concatenated code the author wrote
to answer it (grader cells excluded).

The ``grading-assignments`` skill runs this on **both** the student and the solution
notebook, then reads the two extractions side-by-side to write the natural-language
"what differed between the approaches" that feeds ``build_report_notebook.py``.

Usage
-----
    python decipher_approach.py --notebook Solution_Module_04.ipynb \
        [--manifest grader/manifests/Module_04.json] [--out approach_src_04.json]

Output JSON::

    { "notebook": "...", "module": 4,
      "questions": { "3.3": {"prompt": "...", "code": "...", "answer_keys": [...]} } }
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import nbformat

Q_CODE_RE = re.compile(r"^\s*#\s*Q(?:uestion|roblem)?\s*([0-9]+[a-z]?(?:\.[0-9]+)?)",
                       re.IGNORECASE)
Q_HEAD_RE = re.compile(r"^\s*#{1,6}\s*(?:Question|Problem)\s+([0-9]+)", re.IGNORECASE)
Q_MD_SUB_RE = re.compile(r"^\s*(?:Question|Problem)\s+([0-9]+[a-z]?(?:\.[0-9]+)?)",
                         re.IGNORECASE)


def _norm_q(tok):
    return str(tok).strip().lower()


def _section_of(q):
    m = re.match(r"\s*([0-9]+)", str(q))
    return int(m.group(1)) if m else None


def _first_line(src):
    for line in src.splitlines():
        if line.strip():
            return line
    return ""


def extract(nb_path, spec=None):
    nb = nbformat.read(str(nb_path), as_version=4)
    keys_by_q = {}
    if spec:
        for a in spec.get("answers", []):
            keys_by_q.setdefault(str(a["question"]), []).append(a["key"])

    questions = {}
    cur_section = None
    cur_sub = None

    def _q(q):
        return questions.setdefault(
            q, {"prompt": "", "code": "", "answer_keys": keys_by_q.get(q, [])})

    for c in nb.cells:
        if c.get("metadata", {}).get("grader") in ("save", "instructions"):
            continue
        src = c.source
        if c.cell_type == "markdown":
            hm = Q_HEAD_RE.match(_first_line(src))
            if hm:
                cur_section = int(hm.group(1))
                cur_sub = None
                # attach this prompt to every sub-question of the section
                clean = re.sub(r"<!-- grader-note -->.*?<!-- /grader-note -->", "",
                               src, flags=re.S).strip()
                for q in list(keys_by_q):
                    if _section_of(q) == cur_section:
                        _q(q)["prompt"] = clean
                continue
            sm = Q_MD_SUB_RE.match(_first_line(src))
            if sm:
                cur_sub = _norm_q(sm.group(1))
        elif c.cell_type == "code":
            m = Q_CODE_RE.match(_first_line(src))
            if m:
                cur_sub = _norm_q(m.group(1))
            if cur_sub is not None:
                entry = _q(cur_sub)
                entry["code"] = (entry["code"] + "\n\n" + src).strip() if entry["code"] else src

    # if we have a spec, keep only its questions (drop stray anchors)
    if spec:
        questions = {q: v for q, v in questions.items() if q in keys_by_q}
    return {
        "notebook": Path(nb_path).name,
        "module": spec["module"] if spec else None,
        "questions": questions,
    }


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--notebook", required=True)
    ap.add_argument("--manifest", default=None)
    ap.add_argument("--out", default=None)
    args = ap.parse_args(argv)
    spec = json.loads(Path(args.manifest).read_text()) if args.manifest else None
    result = extract(args.notebook, spec)
    text = json.dumps(result, indent=2)
    if args.out:
        Path(args.out).write_text(text)
        print(f"wrote {args.out} ({len(result['questions'])} questions)")
    else:
        print(text)


if __name__ == "__main__":
    main()
