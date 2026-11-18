# Analyzing PEERS recall data: conventions and tools

Contents: 1. Rules. 2. Which function for which measure. 3. Status of the lab toolboxes. 4. Recipes.

## 1. Rules

These follow the lab's published analyses. Depart from one only for a stated reason.

1. **Subjects are the unit.** Compute each measure within a subject, pooling that subject's lists, then average
   subjects with equal weight. Report N. Never pool lists across subjects.
2. **Say which subjects and sessions.** Give the experiment, the sessions (and whether the practice sessions 0
   and 7 are in), the list types, the age group, and whether partial sessions were dropped
   (`session_complete`). Check counts against `selftest.py`, Part 2, before quoting a published N.
3. **A subject enters a cell only with enough lists.** With equal weighting, one list from a subject who has no
   other list in a cell can move the mean. `irt_family` requires five lists per subject per partition.
4. **Inter-response times are a family of curves.** Partition lists by the number of words recalled and plot
   one curve per partition against output position (Murdock & Okada, 1970). Do not pool across the number
   recalled: each curve rises steeply toward its last response, and pooling mixes early and final intervals.
5. **Lag-CRP.** Lags -5 to +5. Leave out transitions to or from a repetition or an intrusion, and condition each
   transition on the words not yet recalled (Kahana, 1996). Healey, Long and Kahana (2019) also left out the
   first two output positions (`skip_first=2`); say which you did. For one number per subject use the temporal
   factor (Polyn, Norman & Kahana, 2009), where chance is .5.
6. **Intrusions.** A prior-list intrusion is a word from an earlier list of the same session; every other
   wrong word is an extra-list intrusion. Report counts per list. For list recency, use only lists late enough
   that every lag was possible (Zaromb et al., 2006; the first ten lists are dropped in Kahana, 2020, Figure 5).
7. **Recall termination.** Miller, Weidemann and Kahana (2012): recall has stopped when the time from the last
   response to the end of the period exceeds every inter-response time on the trial and exceeds 12 s. Report
   the probability of stopping after each kind of response by output position.
8. **Recognition.** Weidemann and Kahana (2016): drop trials with an invalid rating or a response time outside
   300-3,000 ms; build the ROC within each session from the confidence ratings (or from response times), then
   average within subject.
9. **Goodness of fit.** Do not report R². Report the root-mean-squared deviation in the units of the data, with
   the standard errors of the data beside it.
10. **Uncertainty.** Show 95% confidence intervals and say in the caption what the bars are. For a contrast
    among conditions that every subject contributes to, use within-subject intervals (Loftus & Masson, 1994),
    as Healey, Long and Kahana (2019) and Katerman et al. (2022) did. With a test, give the statistic, its
    degrees of freedom, an effect size and the descriptive statistics.
11. **Keep the pipeline deterministic.** Scripts in a git repository, the data commit pinned by
    `fetch_peers.sh`, numbers written to a results file that the text and the figures both read.

## 2. Which function for which measure

`pa` is `peers_analysis`; each returns one row per subject. `pa.summarize(table, value, by)` gives the mean
across subjects with SEM and 95% interval.

| Measure | Function |
|---|---|
| Recall probability | `pa.recall_probability(ev, by=...)` |
| Serial position curve | `pa.spc(ev)` (identical to `pybeh.spc`) |
| Probability of first recall | `pa.pfr(ev)` (identical to `pybeh.pfr`); `output=2` for the second response |
| Lag-CRP | `pa.lag_crp(ev, max_lag=5, skip_first=0)` (calls `pybeh.crp`) |
| Temporal factor | `pa.temporal_factor(ev)` (calls `pybeh.temp_fact`) |
| Intrusions and repetitions per list | `pa.intrusions(ev)` |
| Prior-list intrusions by list lag | `pa.pli_by_lag(ev, max_lag=5)` |
| Inter-response times | `pa.irt_family(ev, min_lists=5)` |
| Lag-conditional response latency | `pybeh.crl.crl` on `peers.to_pybeh(ev)` |
| Hit and false-alarm rates | `pa.recognition_rates(peers.load_recognition())` |
| Within-subject intervals | `pybeh_pd.loftus_masson_analytic(table, 'subject', condition, value)` |
| Semantic clustering | `pybeh_pd.pd_sem_crp`, `pd_dist_fact`; needs a similarity matrix for the pool, which you must supply |

Every function takes `by=`, a column or list of columns constant within a list (`list_type`, `distractor`,
`final_distractor`, `pre_distractor`, `session`, `group`).

## 3. Status of the lab toolboxes

Install with `pip install git+https://github.com/pennmem/pybeh git+https://github.com/pennmem/pybeh_pd` (add
`--break-system-packages` where pip asks for it).

- **pybeh** (matrix functions; no test suite). Checked against hand-worked examples in November 2026: `spc`,
  `pfr`, `pnr`, `crp`, `crl`, `temp_fact`, `pli`, `xli`, `reps` and `mask_maker.make_clean_recalls_mask2d` are
  correct. Feed them `peers.to_pybeh(ev)`.
- **`pybeh.irt` is wrong on master.** For a trial with as many recalls as the matrix has columns, or one fewer,
  it returns a recall time where the last interval belongs, and it overwrites its input. With one matrix per
  session it corrupts 19% of Experiment 1 lists and 12% of Experiment 4 lists. Pull request 7 on
  `pennmem/pybeh` fixes it and adds tests. `selftest.py` reports whether the installed copy has the fix.
- **`pybeh.p_stop_op`** raises an error when the time arguments are NumPy arrays (pass lists), and with the
  default mask it treats the last correct recall as the stop even if an intrusion followed.
- **pybeh_pd** (pandas wrappers with tests). `pd_crp` and `pd_temp_fact` accept the loader's events directly with
  `itemno_column='item_num'` and give the same numbers as pybeh. They take one subject at a time. Under pandas 3,
  `groupby('subject').apply(pb.pd_crp, ...)` fails; loop instead:
  `pd.concat({s: pb.pd_crp(d, itemno_column='item_num') for s, d in ev.groupby('subject', observed=True)})`.

## 4. Recipes

```python
import peers, peers_analysis as pa

# Experiment 1, younger adults, lists without an encoding task, complete sessions
ev = peers.load_events(1)
ev = ev[(ev.age_group == 'young') & ev.session_complete & (ev.list_type == 'no_task')]
pa.summarize(pa.spc(ev), 'prob', by='serialpos')
pa.summarize(pa.lag_crp(ev, skip_first=2), 'prob', by='lag')

# Experiment 2: recall by distractor condition
ev = peers.load_events(2, complete_sessions_only=True)
pa.summarize(pa.recall_probability(ev, by=['distractor', 'final_distractor']), 'p_recall',
             by=['distractor', 'final_distractor'])

# Experiment 3: intrusions in the two groups (sessions 15-19 and 16-19)
ev = peers.load_events(3)
ev = ev[((ev.group == 'EFR') & (ev.session >= 15)) | (ev.group == 'IFR')]
pa.summarize(pa.intrusions(ev, by='group'), 'pli', by='group')

# Experiment 4: timing, subjects with the 23 standard sessions
ev = peers.load_events(4)
ev = ev[ev.session <= 22]
n = ev.groupby('subject', observed=True).session.nunique()
ev = ev[ev.subject.isin(n[n == 23].index)]
f = pa.irt_family(ev)
pa.summarize(f[f.n_recalled == 10], 'irt', by='outpos')

# Experiment 5: words recalled in each ten-minute test
ev = peers.load_events(5)
r = ev[(ev.type == 'FFR_REC_WORD') & (ev.intrusion == 0) & (ev.repeat == 0)]
r.groupby(['subject', 'session'], observed=True).size().groupby('session').mean()
```
