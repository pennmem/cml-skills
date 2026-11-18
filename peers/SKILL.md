---
name: peers
description: Load, check and analyze the behavioral data of the Penn Electrophysiology of Encoding and Retrieval Study (PEERS Experiments 1-5; lab task names ltpFR, ltpFR2, VFFR; OpenNeuro ds004395), with each experiment's methods, the file formats, pybeh, and Michael Kahana's conventions for analysis and figures. Use whenever PEERS, ltpFR, ltpFR2, VFFR or a numbered PEERS experiment comes up, or a free-recall analysis (serial position, lag-CRP, intrusions, inter-response times, recognition) is wanted on those data.
---

# PEERS behavioral data

PEERS is five multi-session free-recall experiments run in the Kahana lab from 2010 to 2020. This skill covers
the behavioral data only. It gives the methods of each experiment, a loader that turns the public files into
events in the lab's conventions, the standard analyses, and the figure style. It does not handle the EEG.

## 1. Get the skill's files

The loader, the analysis code and the reference files live in the `peers/` directory of `pennmem/cml-skills`.
If `scripts/` and `references/` sit beside this file, use them. Otherwise:

```bash
SK=~/cml-skills
[ -d $SK/.git ] || git clone --depth 1 https://github.com/pennmem/cml-skills $SK
# until the pull request that adds this skill is merged, its files are on the branch peers-skill
[ -d $SK/peers ] || { git -C $SK fetch --depth 1 origin peers-skill && git -C $SK checkout -q FETCH_HEAD; }
export PEERS_SKILL=$SK/peers PEERS_DATA=~/peers-data
bash $PEERS_SKILL/scripts/fetch_peers.sh $PEERS_DATA       # behavioral files only: under a minute, about 1 GB
PKGS="git+https://github.com/pennmem/pybeh git+https://github.com/pennmem/pybeh_pd"
pip install -q $PKGS 2>/dev/null || pip install -q --break-system-packages $PKGS
python $PEERS_SKILL/scripts/selftest.py --quick            # must end with ALL STRUCTURE CHECKS PASSED
```

In Python, `sys.path.insert(0, f'{PEERS_SKILL}/scripts')`, then `import peers, peers_analysis as pa`. The first
`load_events` call for a task reads its files (under a minute) and caches the result beside the data.

If the self-test fails, stop: the dataset or the code has changed, and numbers from the loader cannot be
trusted until you know which. On rhino, prefer the lab's internal events (`references/data.md`, section 6) and
use the loader as a cross-check.

## 2. Which experiment

Read the reference file for the experiment in question before analyzing it. Session numbers below are the
0-based numbers in the file names; the paper counts from 1.

| Experiment | Lab name | Sessions | Design in one line | Read |
|---|---|---|---|---|
| 1 | ltpFR | 0-6 | Immediate free recall, 16 lists of 16 words; no-task, size, animacy and task-shift lists; younger and older adults | `references/experiments-1-3.md` |
| 2 | ltpFR | 7-13, or 7-15 for LTP210 and later | Arithmetic distractors of 0, 8 or 16 s between words and before recall; 12 lists | `references/experiments-1-3.md` |
| 3 | ltpFR | 14-19 (externalized recall), or 16-19 (standard recall) for LTP210 and later | As Experiment 1; one group says every word that comes to mind | `references/experiments-1-3.md` |
| 4 | ltpFR2 | 0-23 | Delayed free recall, 24 lists of 24 words, the same 576 words every session | `references/experiment-4.md` |
| 5 | VFFR | 0-9 | Read each of the 576 words aloud; from session 5, ten minutes of recall at the start | `references/experiment-5.md` |

Experiments 1-3 are one cohort of 20 sessions. All have end-of-session recognition and, in half the sessions,
final free recall. If a request names no experiment, ask which, or say which you chose and why.

Other references: `references/data.md` (files, columns, traps, how the public files differ from published
samples), `references/analysis.md` (rules, functions, recipes), `references/figures.md`.

## 3. Loading

```python
ev = peers.load_events(4)            # one row per studied word (WORD) and per recalled word (REC_WORD)
ev = ev[ev.session_complete]         # every subject and session is returned; select deliberately
rec = peers.load_recognition()       # Experiments 1-3, one row per probe
m = peers.to_pybeh(ev)               # recalls, times, intrusions ... as pybeh matrices
print(peers.CONDITION_COLUMNS)       # the condition columns of each experiment
```

The public files lack serial positions, recalled flags, intrusion codes and recall times. The loader derives
them: `serialpos`, `recalled`, `intrusion` (0 correct, k > 0 prior-list from k lists back, -1 extra-list),
`repeat`, `rectime` (ms), `outpos`. Conditions: `list_type`, `enc_task`, `distractor`, `final_distractor`,
`group`, `pre_distractor`, `novel`, `age_group`. `peers.session_table()` lists every session with its flags.

## 4. Analysis rules

Full version with sources in `references/analysis.md`. The ones that are most often broken:

1. Compute within subject, then average subjects with equal weight. Report N, sessions and list types.
2. Inter-response times: one curve per number of words recalled (`pa.irt_family`). Never pool across the
   number recalled.
3. Lag-CRP over lags -5 to 5, excluding transitions to or from repetitions and intrusions (`pa.lag_crp`).
4. No R². Give RMSD in the units of the data, beside the standard errors.
5. 95% confidence intervals; within-subject intervals for within-subject contrasts.
6. Quote a published N only after checking it against the public files (`selftest.py`, Part 2). They differ:
   for example the paper reports 98 completers of Experiment 4 and the public files hold 83.
7. `pybeh.irt` is wrong on master until pull request 7 of `pennmem/pybeh` is merged. The other pybeh functions
   listed in `references/analysis.md` were checked by hand.

`pa.spc`, `pa.pfr`, `pa.lag_crp`, `pa.temporal_factor`, `pa.intrusions`, `pa.pli_by_lag`, `pa.irt_family` and
`pa.recognition_rates` each return one row per subject and take `by=` for conditions.
`pa.summarize(table, value, by)` averages across subjects.

## 5. Figures

`pa.set_style()`, `pa.plot_curve`, `pa.plot_lag_crp`, and `pa.standard_figure(ev, title)` for the four-panel
summary. Arial or Liberation Sans, vector PDF, black filled symbols with error bars for data, at most three
condition colors. Details in `references/figures.md`. Render the figure and look at it before sending it.

## 6. Traps

- The practice sessions (0, and 7 for Experiment 2) are in the data. Say whether you kept them.
- Experiment 3's externalized group: use sessions 15-19. The spacebar rejections are not in the public files.
- Experiment 4: leave session 23 out of pooled analyses (half its words are new). List 1 is preceded by a
  distractor in about half the sessions, although the paper says it never was.
- Experiment 5 has no study lists; serial-position and lag analyses do not apply to its read-aloud trials.
- Older adults are in Experiment 1 only. Age is missing for 35 subjects (`age_group == 'unknown'`); all of them
  took part in Experiment 4, which enrolled young adults.
- Words recur across sessions, so an extra-list intrusion may be a word from an earlier session.

## 7. Reporting

Lead with the result. Give N, the sessions and lists used, and the definition of any measure that has more
than one in the literature. Mark each number as computed from the public files or quoted from a paper. Prose
that will go out under Michael Kahana's name goes through the `kahana-voice` skill, and manuscript work through
`memory-publications`.
