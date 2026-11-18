"""selftest.py -- check the PEERS loader against the structure of the public files and against published numbers.

    python selftest.py [DATA_ROOT]         (about two minutes after the first load; --quick skips the slow part)

Part 1 checks facts that must hold for the loader to be right (counts of files, lists and conditions; agreement
with pybeh). A failure there means the data or the code has changed: stop and find out which. Part 2 sets numbers
from the public files beside numbers published from the lab's internal files. Those need not agree exactly,
because the published samples differ (see references/data.md), so Part 2 only reports.
"""
import sys
import warnings

import numpy as np
import pandas as pd

import peers
import peers_analysis as pa

warnings.simplefilter('ignore')
PINNED = '798377a4d'
fails = []


def check(name, got, expected):
    ok = got == expected
    print(f"  {'ok  ' if ok else 'FAIL'}  {name}: {got}" + ('' if ok else f'   (expected {expected})'))
    if not ok:
        fails.append(name)


def report(name, public, published, source):
    print(f'  {name}\n      public files: {public}\n      published:    {published}   [{source}]')


def main(root=None, quick=False):
    root = peers.find_root(root)
    commit = peers._commit(root)
    print(f'PEERS self-test. Data: {root} (commit {commit})')
    if commit != PINNED:
        print(f'NOTE: the expected counts below were recorded at commit {PINNED}; read CHANGES in the dataset.')
    S = peers.session_table(root)
    P = peers.participants(root)
    ag = P.set_index('subject').age_group
    ev = {e: peers.load_events(e, root, verbose=False) for e in (1, 2, 3, 4, 5)}

    print('\nPart 1. Structure of the public files')
    check('subjects in participants.tsv', len(P), 364)
    check('session files (ltpFR, ltpFR2, VFFR)', S.groupby('task').size().reindex(['ltpFR', 'ltpFR2', 'VFFR']).tolist(),
          [3633, 2469, 462])
    check('subjects per experiment', S.groupby('experiment').subject.nunique().tolist(), [237, 166, 156, 127, 57])
    check('sessions per experiment', S.groupby('experiment').size().tolist(), [1582, 1249, 802, 2469, 462])
    check('incomplete sessions per experiment', (~S.session_complete).groupby(S.experiment).sum().tolist(),
          [2, 0, 0, 4, 1])
    check('Experiment 1 age groups (young, older, unknown)',
          [int((ag[S[S.experiment == 1].subject.unique()] == g).sum()) for g in ('young', 'older', 'unknown')],
          [172, 40, 25])
    g3 = S[S.experiment == 3].drop_duplicates('subject').group.value_counts()
    check('Experiment 3 groups that started (EFR, IFR)', [int(g3['EFR']), int(g3['IFR'])], [96, 60])
    s19 = S[(S.experiment == 3) & (S.session == 19)].group.value_counts()
    check('Experiment 3 groups that finished session 19 (EFR, IFR)', [int(s19['EFR']), int(s19['IFR'])], [92, 60])
    L2 = ev[2][ev[2].type == 'WORD'].drop_duplicates(pa.KEYS)
    cells = L2.groupby(['distractor', 'final_distractor']).size()
    check('Experiment 2 lists by condition 0-0, 0-8, 0-16, 8-8, 16-16',
          [int(cells.get(k, 0)) for k in ((0, 0), (0, 8), (0, 16), (8, 8), (16, 16))], [2498, 3911, 2498, 3911, 2498])
    check('Experiment 2 lists in any other condition', int(len(L2) - sum(cells.get(k, 0) for k in
          ((0, 0), (0, 8), (0, 16), (8, 8), (16, 16)))), 0)
    for e in (1, 3):
        L = ev[e][ev[e].type == 'WORD'].drop_duplicates(pa.KEYS)
        check(f'Experiment {e} lists with any distractor', int(((L.distractor > 0) | (L.final_distractor > 0)).sum()), 0)
    L4 = ev[4][(ev[4].type == 'WORD') & ev[4].session_complete].drop_duplicates(pa.KEYS)
    check('Experiment 4: lists with a pre-list distractor in each complete session',
          sorted(L4.groupby(['subject', 'session'], observed=True).pre_distractor.sum().unique().tolist()), [12])
    w4 = ev[4][(ev[4].type == 'WORD') & ev[4].session_complete & (ev[4].session < 23)]
    sets = w4.groupby('subject', observed=True).item_num.agg(frozenset)
    check('Experiment 4: distinct 576-word sets across subjects (sessions 0-22)', [sets.nunique(), len(next(iter(sets)))],
          [1, 576])
    n23 = ev[4][(ev[4].type == 'WORD') & (ev[4].session == 23)].groupby('subject', observed=True).novel.sum()
    check('Experiment 4, session 23: new words per subject', sorted(n23.unique().tolist()), [288])
    w5 = ev[5][(ev[5].type == 'WORD') & ev[5].session_complete]
    check('Experiment 5 uses the Experiment 4 word set',
          set(w5.item_name.astype(str).unique()) == set(w4.item_name.astype(str).unique()), True)
    check('Experiment 5 sessions with the 10-minute recall, by session number',
          S[(S.experiment == 5) & (S.has_ffr == True)].groupby('session').size().to_dict(),  # noqa: E712
          {5: 43, 6: 42, 7: 41, 8: 40, 9: 37})
    r = pd.concat([ev[e][ev[e].type == 'REC_WORD'] for e in (1, 2, 3, 4)])
    check('list recalls with a missing time or serial-position code', int(r.rectime.isna().sum() +
          ((r.intrusion == 0) & r.serialpos.isna()).sum() + ((r.intrusion != 0) & r.serialpos.notna()).sum()), 0)
    check('list recalls later than 75.1 s', int((r.rectime > 75100).sum()), 1)
    rec = peers.load_recognition(root, verbose=False)
    check('recognition: share of targets per session (four values)',
          sorted(rec.groupby(['subject', 'session']).target.mean().round(3).value_counts().index[:4].tolist()),
          [0.5, 0.625, 0.75, 0.8])
    check('recognition: lures that were studied in the session', int(rec[rec.target == 0].study_list.notna().sum()), 0)

    print('\n        agreement with pybeh (Experiment 1, complete sessions)')
    x = ev[1][ev[1].session_complete]
    try:
        from pybeh.spc import spc as pb_spc
        from pybeh.pfr import pfr as pb_pfr
        from pybeh.irt import irt as pb_irt
        m = peers.to_pybeh(x)
        subs = np.unique(m['subjects'])
        a = pa.spc(x).pivot(index='subject', columns='serialpos', values='prob').reindex(subs).values
        check('largest difference from pybeh.spc', float(np.abs(a - np.array(pb_spc(m['recalls'], m['subjects'], 16))).max()), 0.0)
        a = pa.pfr(x).pivot(index='subject', columns='serialpos', values='prob').reindex(subs).values
        check('largest difference from pybeh.pfr', float(np.abs(a - np.array(pb_pfr(m['recalls'], m['subjects'], 16))).max()), 0.0)
        fixed = np.array(pb_irt([[1000, 3000, 7000, 15000]]), dtype=float).tolist() == [[2000.0, 4000.0, 8000.0, 0.0]]
        print('  ' + ('ok    the installed pybeh.irt has the fix (pull request 7)' if fixed else
                      'NOTE  the installed pybeh.irt still returns recall times for the longest trials; use '
                      'peers_analysis.irt_family'))
    except ImportError:
        print('  NOTE  pybeh is not installed (pip install git+https://github.com/pennmem/pybeh); skipped')
    f = pa.irt_family(ev[1], min_lists=5)
    part = f[f.n_recalled == 9]
    check('inter-response times, Experiment 1, lists with 9 recalled: lists and subjects',
          [int(part.drop_duplicates('subject').n_lists.sum()), part.subject.nunique()], [2806, 198])
    check('   mean time before recalls 2 and 9 (s)',
          pa.summarize(part, 'irt', 'outpos').set_index('outpos')['mean'].round(3).loc[[2, 9]].tolist(), [1.226, 9.735])

    print('\nPart 2. Public files beside published numbers')
    any1 = ag[S[S.experiment == 1].subject.unique()].value_counts()
    c1 = S[(S.experiment == 1) & S.session_complete].groupby('subject').session.nunique()
    done1 = ag[c1[c1 == 7].index].value_counts()
    report('Experiment 1, subjects', f"{any1.get('young', 0)} young, {any1.get('older', 0)} older, "
           f"{any1.get('unknown', 0)} of unknown age; with seven complete sessions "
           f"{done1.get('young', 0)}, {done1.get('older', 0)}, {done1.get('unknown', 0)}",
           '172 younger adults; 39 older adults (38 in Healey et al., 2019)', 'Kahana et al., 2024, Table 1 and Appendix')
    s2 = S[S.experiment == 2]
    need = np.where(s2.subject.str[3:].astype(int) < peers.LATE_COHORT_FIRST_ID, 7, 9)
    n2 = s2.assign(need=need).groupby('subject').agg(n=('session', 'nunique'), need=('need', 'first'))
    report('Experiment 2, subjects', f'{len(n2)} with a session; {int((n2.n == n2.need).sum())} with all 7 or 9 sessions',
           '157', 'Kahana et al., 2024, Table 1')
    c4 = S[(S.experiment == 4) & S.session_complete].groupby('subject').session.nunique()
    c4b = S[(S.experiment == 4) & S.session_complete & (S.session < 23)].groupby('subject').session.nunique()
    report('Experiment 4, subjects', f'{S[S.experiment == 4].subject.nunique()} with a session; {int((c4 == 24).sum())} with 24 '
           f'complete sessions; {int((c4b == 23).sum())} with sessions 0-22 complete', '98 completed 24 sessions',
           'Kahana et al., 2024')
    report('Experiment 5, subjects', f'{S[S.experiment == 5].subject.nunique()}; '
           f'{S[(S.experiment == 5) & (S.has_ffr == True)].subject.nunique()} reached a recall session', '57',  # noqa: E712
           'Kahana et al., 2024; Katerman et al., 2022')

    e3 = ev[3][ev[3].session_complete]
    for grp, ses, pub in (('EFR', range(15, 20), 'correct 10.6, prior-list 0.68 (SEM 0.08), extra-list 1.4, repetitions 0.89; n = 92'),
                          ('IFR', range(16, 20), 'correct 10.6, prior-list 0.08 (SEM 0.01); n = 51')):
        x = e3[(e3.group == grp) & e3.session.isin(list(ses))]
        k = x.groupby('subject', observed=True).session.nunique()
        t = pa.intrusions(x[x.subject.isin(k[k == len(ses)].index)])
        s = {c: pa.summarize(t, c).iloc[0] for c in ('correct', 'pli', 'eli', 'repetitions')}
        report(f'Experiment 3, {grp} group, per list', f"correct {s['correct']['mean']:.2f}, prior-list {s['pli']['mean']:.3f} "
               f"(SEM {s['pli']['sem']:.3f}), extra-list {s['eli']['mean']:.2f}, repetitions {s['repetitions']['mean']:.2f}; "
               f"n = {int(s['correct']['n'])}", pub, 'Lohnas et al., 2015, Table 5')

    v = ev[5]
    acc = v[v.type == 'WORD'].groupby('subject', observed=True).recalled.mean().mean()
    ff = v[v.type == 'FFR_REC_WORD']
    g = ff.groupby(['subject', 'session'], observed=True)
    words = g.apply(lambda d: (d.intrusion == 0).sum()).groupby('session').mean()
    uniq = g.apply(lambda d: ((d.intrusion == 0) & (d.repeat == 0)).sum()).groupby('session').mean()
    share = ff.groupby('session').apply(lambda d: (d.intrusion == -1).mean())
    report('Experiment 5', f'read-aloud accuracy {100 * acc:.1f}%; words recalled in the first and last recall sessions '
           f'{words.loc[5]:.0f} and {words.loc[9]:.0f} ({uniq.loc[5]:.0f} and {uniq.loc[9]:.0f} without repetitions); '
           f'intrusions {100 * share.loc[5]:.0f}% and {100 * share.loc[9]:.0f}% of responses',
           'accuracy above 96%; 29 and 103 words; intrusions 37% and 23%', 'Katerman et al., 2022')

    R = rec[rec.subject.map(ag) == 'young']
    ok = R[R.confidence.between(1, 5) & R.rt.between(300, 3000) & R.response.isin([0, 1])]
    kind = np.select([(ok.target == 1) & (ok.response == 1), (ok.target == 0) & (ok.response == 1),
                      (ok.target == 0) & (ok.response == 0)], ['hit', 'false alarm', 'correct rejection'], 'miss')
    rt = ok.assign(kind=kind).groupby('kind').rt.mean()
    prev = R[R.target == 1].groupby('subject').recalled.mean()
    report('Recognition (young adults)', f"{R.subject.nunique()} subjects, {R.groupby(['subject', 'session']).ngroups} sessions; "
           f"mean response time: hits {rt['hit']:.0f}, false alarms {rt['false alarm']:.0f}, correct rejections "
           f"{rt['correct rejection']:.0f}, misses {rt['miss']:.0f} ms; {100 * prev.mean():.0f}% of targets recalled earlier",
           '171 subjects, 3120 sessions; 773, 943, 967, 1065 ms; 61%', 'Weidemann & Kahana, 2016')

    if not quick:
        allev = pd.concat([ev[e] for e in (1, 2, 3)], ignore_index=True)
        allev = allev[allev.session_complete & (allev.age_group == 'young')]
        k = allev.groupby('subject', observed=True).session.nunique()
        allev = allev[allev.subject.isin(k[k >= 7].index)]
        t = pa.temporal_factor(allev).merge(pa.recall_probability(allev), on='subject')
        report('Contiguity and recall across young adults, Experiments 1-3',
               f'r({len(t) - 2}) = {np.corrcoef(t.temporal_factor, t.p_recall)[0, 1]:.2f} between the temporal factor and '
               f'recall probability', 'r(170) = .51', 'Healey, Long & Kahana, 2019')

    print('\n' + ('ALL STRUCTURE CHECKS PASSED' if not fails else f'{len(fails)} STRUCTURE CHECK(S) FAILED: ' + '; '.join(fails)))
    return 1 if fails else 0


if __name__ == '__main__':
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    sys.exit(main(args[0] if args else None, quick='--quick' in sys.argv))
