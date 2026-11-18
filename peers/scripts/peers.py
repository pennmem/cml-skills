"""peers.py -- load the public behavioral data of the Penn Electrophysiology of Encoding and Retrieval Study.

Source data: OpenNeuro ds004395, version 2.0.0 (fetch with fetch_peers.sh). No EEG is read.

The public event files keep only a few columns of the lab's internal events (word, item number, list, time,
encoding task, recognition response, distractor problems). Serial positions, recalled flags, intrusion codes,
response times and the distractor condition of each list are NOT in the files. This module derives them, in the
conventions of the lab's own event structures, so that the output works with pybeh and pybeh_pd.

    import peers
    ev  = peers.load_events(4)                # PEERS Experiment 4: one row per presented or recalled word
    rec = peers.load_recognition()            # Experiments 1-3: one row per recognition probe
    m   = peers.to_pybeh(ev[ev.subject == 'LTP331'])   # matrices for pybeh (recalls, times, intrusions, ...)

Experiments and files (session numbers are the 0-based numbers in the file names):
    Experiment 1   task-ltpFR   sessions 0-6                       immediate free recall, 16 lists x 16 words
    Experiment 2   task-ltpFR   sessions 7-13 (LTP063-LTP209)      distractor manipulation, 12 lists x 16 words
                                sessions 7-15 (LTP210 and later)   (session 7 is a practice session of 14 lists)
    Experiment 3   task-ltpFR   sessions 14-19 (LTP063-LTP209)     externalized recall (session 14 introduces it)
                                sessions 16-19 (LTP210 and later)  standard immediate free recall
    Experiment 4   task-ltpFR2  sessions 0-23                      delayed free recall, 24 lists x 24 words
    Experiment 5   task-VFFR    sessions 0-9                       read-aloud trials; 10-min recall at start of 5-9

Columns of load_events() (one row per event):
    subject, experiment, task, session, list, type, item_name, item_num, serialpos, outpos, rectime, intrusion,
    repeat, recalled, mstime, plus condition columns (print(peers.CONDITION_COLUMNS)).
    type       'WORD' (study), 'REC_WORD' (recall of the list just studied), 'FFR_REC_WORD' (final free recall in
               Experiments 1-3; the 10-minute recall of the whole pool in Experiment 5).
    serialpos  WORD: position in the list (1..list length). REC_WORD: position of the recalled word in the list
               just studied; NaN for an intrusion.
    intrusion  recalls only: 0 = word from the current list; k > 0 = prior-list intrusion from k lists back in the
               same session; -1 = extra-list intrusion (any other word, including words seen in earlier sessions).
    repeat     recalls only: 0 for the first report of a word in this recall period, 1 for its second report, ...
    rectime    recalls only: ms from the start of the recall period (Experiment 5 read-aloud trials: ms from word
               offset to speech onset).
    recalled   WORD rows only: 1 if the word was recalled in the recall period of its own list.
"""
import glob
import os
import re
import subprocess

import numpy as np
import pandas as pd

__all__ = ['find_root', 'participants', 'load_events', 'load_recognition', 'load_math', 'session_table',
           'to_pybeh', 'EXPERIMENT_TASK', 'LATE_COHORT_FIRST_ID', 'CONDITION_COLUMNS']

EXPERIMENT_TASK = {1: 'ltpFR', 2: 'ltpFR', 3: 'ltpFR', 4: 'ltpFR2', 5: 'VFFR'}
LATE_COHORT_FIRST_ID = 210      # LTP210 and later: nine sessions of Experiment 2, then standard recall in Exp. 3
YOUNG_MAX_AGE, OLD_MIN_AGE = 35, 60             # the study enrolled ages 17-30 and 60+; nobody falls between
CACHE_VERSION = 4

CONDITION_COLUMNS = """
Condition columns of load_events():
    list_length       number of words studied in the list
    session_complete  True if the session has every list (and, for Experiment 5, all 576 trials)
    age, age_group    from participants.tsv; age_group is 'young', 'older' or 'unknown' (age missing)
  Experiments 1-3
    list_type         'no_task', 'size', 'animacy' or 'shift' (both judgments within the list)
    enc_task          per word: 'none', 'size' or 'animacy'
    judgment          per word: the subject's key press (0 small/nonliving, 1 big/living; NaN if none)
    distractor        seconds of arithmetic before every word (0, 8 or 16); always 0 outside Experiment 2
    final_distractor  seconds of arithmetic between the last word and recall (0, 8 or 16); 0 outside Experiment 2
    group             Experiment 3 only: 'EFR' (externalized recall) or 'IFR' (standard recall)
    has_ffr           True if the session ended with final free recall
    has_recog         True if the session has a recognition test
    math_logged       True if the file has arithmetic rows (one Experiment 2 session lacks them)
    source_list, source_serialpos   for a prior-list intrusion and for final free recall: where the word was studied
  Experiment 4
    pre_distractor    True if 24 s of arithmetic preceded the list (every list has 24 s after it)
    novel             session 23 only: True for a word that is not one of the 576 words of sessions 0-22
    source_list, source_serialpos   for a prior-list intrusion: where the word was studied
  Experiment 5
    trial             0-575 within the session for read-aloud trials (list = block 1-24, serialpos = 1-24)
    too_fast          1 if the subject spoke within 1 s of word offset on that trial
    has_ffr           True if the session began with the 10-minute recall
"""

_KEEP = {
    'ltpFR': ['WORD', 'REC_WORD', 'REC_START', 'FFR_REC_WORD', 'RECOG_TARGET', 'RECOG_LURE', 'RECOG_RESP',
              'RECOG_CONF', 'START', 'PROB', 'STOP'],
    'ltpFR2': ['WORD', 'REC_WORD', 'REC_START', 'DISTRACTOR', 'START', 'PROB', 'STOP'],
    'VFFR': ['WORD', 'WORD_OFF', 'REC_WORD', 'FFR_START', 'FFR_STOP', 'FFR_REC_WORD'],
}
_NUMERIC = ['trial', 'task', 'item_num', 'recog_resp', 'recog_conf', 'resp', 'answer', 'test_x', 'test_y',
            'test_z', 'list', 'too_fast']
_COLUMNS = ['mstime', 'trial_type', 'item_name'] + _NUMERIC


# ------------------------------------------------------------------------------------------------ locating data
def find_root(root=None):
    """Return the path of the ds004395 folder. Order: argument, $PEERS_DATA, ./peers-data, ~/peers-data, '.'."""
    for c in (root, os.environ.get('PEERS_DATA'), 'peers-data', os.path.expanduser('~/peers-data'), '.'):
        if not c:
            continue
        for p in (c, os.path.join(c, 'ds004395')):
            if os.path.isfile(os.path.join(p, 'participants.tsv')) and glob.glob(os.path.join(p, 'sub-LTP*')):
                return os.path.abspath(p)
    raise FileNotFoundError('PEERS data not found. Run fetch_peers.sh, then pass root= or set PEERS_DATA.')


def _commit(root):
    try:
        return subprocess.run(['git', '-C', root, 'rev-parse', '--short=9', 'HEAD'], capture_output=True,
                              text=True, check=True).stdout.strip()
    except Exception:
        return 'unknown'


def participants(root=None):
    """participants.tsv as subject, num, age, sex, hand, age_group ('young', 'older', 'unknown')."""
    root = find_root(root)
    p = pd.read_csv(os.path.join(root, 'participants.tsv'), sep='\t', encoding='utf-8-sig')
    p['subject'] = p.participant_id.str[4:]
    p['num'] = p.subject.str[3:].astype(int)
    p['age'] = pd.to_numeric(p.age, errors='coerce')
    p['age_group'] = np.where(p.age >= OLD_MIN_AGE, 'older', np.where(p.age <= YOUNG_MAX_AGE, 'young', 'unknown'))
    return p[['subject', 'num', 'age', 'sex', 'hand', 'age_group']]


def _files(root, task):
    out = []
    for f in glob.glob(os.path.join(root, 'sub-*', 'ses-*', 'beh', f'*_task-{task}_beh.tsv')):
        m = re.search(r'sub-(LTP\d+)_ses-(\d+)_task-', os.path.basename(f))
        out.append((m.group(1), int(m.group(2)), f))
    return sorted(out, key=lambda x: (x[0], x[1]))


# ---------------------------------------------------------------------------------------- one pass over the files
def _read_all(task, root, verbose):
    """Every kept row of every session file of a task, in file order, with numeric columns converted."""
    files = _files(root, task)
    keep = set(_KEEP[task])
    frames = []
    for i, (sub, ses, f) in enumerate(files):
        d = pd.read_csv(f, sep='\t', dtype=str, keep_default_na=False, usecols=lambda c: c in _COLUMNS)
        d = d[d.trial_type.isin(keep)]
        out = {'sid': np.full(len(d), i, dtype=np.int32), 'ms': pd.to_numeric(d.mstime, errors='coerce').values,
               'tt': d.trial_type.values, 'item_name': d.item_name.values}
        for c in _NUMERIC:
            out[c] = pd.to_numeric(d[c], errors='coerce').values if c in d.columns else np.full(len(d), np.nan)
        frames.append(pd.DataFrame(out))
        if verbose and (i + 1) % 1000 == 0:
            print(f'  {task}: {i + 1} of {len(files)} session files read', flush=True)
    raw = pd.concat(frames, ignore_index=True).rename(columns={'trial': 'tr', 'list': 'lcount'})
    raw['tt'] = raw.tt.astype('category')
    sess = pd.DataFrame({'sid': np.arange(len(files)), 'subject': [f[0] for f in files],
                         'session': [f[1] for f in files]})
    return raw, sess


def _lists(raw):
    """WORD and REC_WORD rows of numbered lists with serialpos, outpos, rectime, repeat, intrusion, recalled."""
    W = raw[(raw.tt == 'WORD') & (raw.tr >= 1)].copy()
    W['list'] = W.tr.astype(int)
    W['item_num'] = W.item_num.fillna(-1).astype(int)
    W = W.sort_values(['sid', 'list', 'ms'], kind='stable').reset_index(drop=True)
    W['serialpos'] = W.groupby(['sid', 'list']).cumcount() + 1
    W['list_length'] = W.groupby(['sid', 'list']).serialpos.transform('max')

    R = raw[(raw.tt == 'REC_WORD') & (raw.tr >= 1)].copy()
    R['list'] = R.tr.astype(int)
    R['item_num'] = R.item_num.fillna(-1).astype(int)
    R = R.sort_values(['sid', 'list', 'ms'], kind='stable').reset_index(drop=True)
    rs = raw[(raw.tt == 'REC_START') & (raw.tr >= 1)]
    rs = rs.assign(list=rs.tr.astype(int)).groupby(['sid', 'list']).ms.min().rename('rec_start').reset_index()
    R = R.merge(rs, on=['sid', 'list'], how='left')
    R['rectime'] = R.ms - R.rec_start
    R['outpos'] = R.groupby(['sid', 'list']).cumcount() + 1
    R['repeat'] = R.groupby(['sid', 'list', 'item_name']).cumcount()
    cur = W.drop_duplicates(['sid', 'list', 'item_num'])[['sid', 'list', 'item_num', 'serialpos']]
    R = R.merge(cur, on=['sid', 'list', 'item_num'], how='left')
    R.loc[R.item_num < 0, 'serialpos'] = np.nan
    first = (W.drop_duplicates(['sid', 'item_num'])[['sid', 'item_num', 'list', 'serialpos']]
             .rename(columns={'list': 'source_list', 'serialpos': 'source_serialpos'}))
    R = R.merge(first, on=['sid', 'item_num'], how='left')
    lag = R.list - R.source_list
    R['intrusion'] = np.where(R.serialpos.notna(), 0, np.where((lag > 0) & (R.item_num >= 0), lag, -1)).astype(int)
    R.loc[R.intrusion <= 0, ['source_list', 'source_serialpos']] = np.nan
    R = R.merge(W.drop_duplicates(['sid', 'list'])[['sid', 'list', 'list_length']], on=['sid', 'list'], how='left')
    got = R.loc[R.intrusion == 0, ['sid', 'list', 'item_num']].drop_duplicates().assign(recalled=1)
    W = W.merge(got, on=['sid', 'list', 'item_num'], how='left')
    W['recalled'] = W.recalled.fillna(0).astype(int)
    W['type'] = 'WORD'
    R['type'] = 'REC_WORD'
    return W, R, rs, first


def _finish(frames, sess, task, extra, root):
    ev = pd.concat(frames, ignore_index=True, sort=False)
    ev = ev.merge(sess, on='sid', how='left')
    ev['task'] = task
    ev['mstime'] = ev.ms
    P = participants(root).set_index('subject')
    ev['age'] = ev.subject.map(P.age).astype(float)
    ev['age_group'] = ev.subject.map(P.age_group).fillna('unknown')
    # order: session by session; within a session list by list (words, then recalls), final free recall last
    # (first in Experiment 5, where the 10-minute recall opens the session)
    ev['_o'] = ev.type.map({'WORD': 0, 'REC_WORD': 1, 'FFR_REC_WORD': 2})
    ffr = ev.type == 'FFR_REC_WORD'
    if task == 'VFFR':
        ev['_l'] = np.where(ffr, -1, ev.get('trial', ev.list))
    else:
        ev['_l'] = np.where(ffr, np.inf, ev.list)
    ev = ev.sort_values(['sid', '_l', '_o', 'ms'], kind='stable')
    cols = ['subject', 'experiment', 'task', 'session', 'list', 'type', 'item_name', 'item_num', 'serialpos',
            'outpos', 'rectime', 'intrusion', 'repeat', 'recalled', 'mstime', 'list_length', 'session_complete']
    ev = ev[[c for c in cols + extra + ['age', 'age_group'] if c in ev.columns]].reset_index(drop=True)
    for c in ('subject', 'type', 'task', 'item_name', 'list_type', 'enc_task', 'group', 'age_group'):
        if c in ev.columns:
            ev[c] = ev[c].astype('category')
    return ev


# ----------------------------------------------------------------------------------- Experiments 1-3 (task-ltpFR)
def _gap_class(seconds, lo, hi):
    return np.where(seconds < lo, 0, np.where(seconds < hi, 8, 16))


def _scan_ltpfr(root, verbose):
    raw, sess = _read_all('ltpFR', root, verbose)
    num = sess.subject.str[3:].astype(int)
    last_exp2 = np.where(num < LATE_COHORT_FIRST_ID, 13, 15)
    sess['experiment'] = np.where(sess.session <= 6, 1, np.where(sess.session <= last_exp2, 2, 3))
    sess['group'] = np.where(sess.experiment == 3, np.where(num >= LATE_COHORT_FIRST_ID, 'IFR', 'EFR'), None)
    W, R, rs, first = _lists(raw)
    task_map = {-1: 'none', 0: 'size', 1: 'animacy'}
    W['enc_task'] = W.task.map(task_map).fillna('none')
    R['enc_task'] = R.task.map(task_map)
    W['judgment'] = W.resp.where(W.resp.isin([0, 1]))
    g = W.assign(a=W.enc_task == 'none', b=W.enc_task == 'size', c=W.enc_task == 'animacy').groupby(['sid', 'list'])
    L = g[['a', 'b', 'c']].any()
    L['list_type'] = np.select([L.a & ~L.b & ~L.c, L.b & ~L.a & ~L.c, L.c & ~L.a & ~L.b],
                               ['no_task', 'size', 'animacy'], 'shift')
    # Distractor condition of each list, from timing alone (the arithmetic rows are missing from one session).
    # Word onset to word onset is about 4, 12 or 20 s with 0, 8 or 16 s of arithmetic before each word; last word
    # onset to the start of recall is about 6, 13 or 21 s with 0, 8 or 16 s of arithmetic after the list.
    gap = W.groupby(['sid', 'list']).ms.diff()
    L['gap'] = gap.groupby([W.sid, W.list]).median() / 1000
    L['last'] = W.groupby(['sid', 'list']).ms.max()
    L = L.reset_index().merge(rs, on=['sid', 'list'], how='left')
    L['distractor'] = np.where(L.gap.notna(), _gap_class(L.gap, 8, 16), 0)
    fin = (L.rec_start - L['last']) / 1000
    L['final_distractor'] = np.where(fin.notna(), _gap_class(fin, 10, 18), 0)
    cond = L[['sid', 'list', 'list_type', 'distractor', 'final_distractor']]
    W = W.merge(cond, on=['sid', 'list'], how='left')
    R = R.merge(cond, on=['sid', 'list'], how='left')
    # final free recall: FFR_REC_WORD rows, timed from the REC_START that carries no list number
    F = raw[raw.tt == 'FFR_REC_WORD'].copy().sort_values(['sid', 'ms'], kind='stable').reset_index(drop=True)
    F['item_num'] = F.item_num.fillna(-1).astype(int)
    cand = raw[(raw.tt == 'REC_START') & raw.tr.isna()][['sid', 'ms']]
    cand = cand[cand.ms > cand.sid.map(W.groupby('sid').ms.max())]
    firstF = F.groupby('sid').ms.min()
    t0 = cand[cand.ms <= cand.sid.map(firstF)].groupby('sid').ms.max()
    F['rectime'] = F.ms - F.sid.map(t0)
    F['outpos'] = F.groupby('sid').cumcount() + 1
    F['repeat'] = F.groupby(['sid', 'item_name']).cumcount()
    F = F.merge(first, on=['sid', 'item_num'], how='left')
    F.loc[F.item_num < 0, ['source_list', 'source_serialpos']] = np.nan
    F['intrusion'] = np.where(F.source_list.notna(), 0, -1)
    F['enc_task'] = F.task.map(task_map)
    F['type'] = 'FFR_REC_WORD'
    F['list'] = np.nan
    # session facts
    n = W.groupby('sid').list.nunique()
    sess['n_lists'] = sess.sid.map(n).fillna(0).astype(int)
    expected = np.where(sess.experiment != 2, 16, np.where(sess.session == 7, 14, 12))
    all16 = W.groupby('sid').list_length.agg(lambda s: (s == 16).all())
    sess['session_complete'] = (sess.n_lists == expected) & sess.sid.map(all16).fillna(False).astype(bool)
    sess['has_ffr'] = sess.sid.isin(set(F.sid) | set(cand.sid))
    sess['has_recog'] = sess.sid.isin(set(raw.sid[raw.tt == 'RECOG_TARGET']))
    sess['math_logged'] = sess.sid.isin(set(raw.sid[raw.tt == 'PROB']))
    extra = ['list_type', 'enc_task', 'judgment', 'distractor', 'final_distractor', 'group', 'has_ffr', 'has_recog',
             'math_logged', 'source_list', 'source_serialpos']
    ev = _finish([W, R, F], sess, 'ltpFR', extra, root)
    return {'events': ev, 'recog': _recognition(raw, sess, ev), 'math': _math(raw, sess, W, rs, 2),
            'sessions': sess}


def _recognition(raw, sess, ev):
    P = raw[raw.tt.isin(['RECOG_TARGET', 'RECOG_LURE', 'RECOG_RESP', 'RECOG_CONF'])].copy()
    probe = P.tt.isin(['RECOG_TARGET', 'RECOG_LURE'])
    P['probe'] = probe.groupby(P.sid).cumsum()
    resp = P[P.tt == 'RECOG_RESP'].groupby(['sid', 'probe']).ms.min().rename('resp_ms')
    conf = P[P.tt == 'RECOG_CONF'].groupby(['sid', 'probe']).ms.min().rename('conf_ms')
    P = P[probe].merge(resp.reset_index(), on=['sid', 'probe'], how='left')
    P = P.merge(conf.reset_index(), on=['sid', 'probe'], how='left')
    P['rt'] = P.resp_ms - P.ms
    P['conf_rt'] = P.conf_ms - P.ms
    P['target'] = (P.tt == 'RECOG_TARGET').astype(int)
    P['item_num'] = P.item_num.fillna(-1).astype(int)
    P = P.merge(sess[['sid', 'subject', 'session', 'experiment']], on='sid', how='left')
    P = P.rename(columns={'recog_resp': 'response', 'recog_conf': 'confidence', 'tr': 'block'})
    study = ev[ev.type == 'WORD'][['subject', 'session', 'item_num', 'list', 'serialpos', 'recalled', 'enc_task',
                                   'list_type', 'distractor', 'final_distractor']]
    study = study.drop_duplicates(['subject', 'session', 'item_num']).rename(
        columns={'list': 'study_list', 'serialpos': 'study_serialpos'})
    study['subject'] = study.subject.astype(str)
    P = P.merge(study, on=['subject', 'session', 'item_num'], how='left')
    cols = ['subject', 'experiment', 'session', 'probe', 'block', 'item_name', 'item_num', 'target', 'response',
            'confidence', 'rt', 'conf_rt', 'study_list', 'study_serialpos', 'recalled', 'enc_task', 'list_type',
            'distractor', 'final_distractor']
    return P[cols].reset_index(drop=True)


def _math(raw, sess, W, rs, experiment):
    """Arithmetic problems with the list, phase and (Experiment 2) serial position they precede."""
    M = raw[raw.tt.isin(['START', 'PROB', 'STOP'])].copy()
    M['block'] = (M.tt == 'START').groupby(M.sid).cumsum()
    M['next_ms'] = M.groupby('sid').ms.shift(-1)
    start = M[M.tt == 'START'][['sid', 'block', 'ms', 'lcount']].rename(columns={'ms': 'start_ms'})
    stop = M[M.tt == 'STOP'].groupby(['sid', 'block']).ms.max().rename('stop_ms').reset_index()
    start = start.merge(stop, on=['sid', 'block'], how='left')
    # what follows each block: the next word (arithmetic before a word or a list) or the start of recall
    nxt = pd.concat([W[['sid', 'ms', 'list', 'serialpos']].assign(what='word'),
                     rs.rename(columns={'rec_start': 'ms'}).assign(serialpos=np.nan, what='recall')])
    nxt = nxt.sort_values('ms', kind='stable')
    start = pd.merge_asof(start.sort_values('start_ms'), nxt, left_on='start_ms', right_on='ms', by='sid',
                          direction='forward')
    # A real block ends 1-4 s before the word or the recall period it precedes. The warm-up block that opens
    # each session (about 20 s in Experiment 2, 11 s in Experiment 4) is followed by a longer pause.
    gap = (start.ms - start.stop_ms) / 1000
    start['practice'] = ~(gap <= 5)
    if experiment == 2:
        start['phase'] = np.where(start.what == 'word', 'before_word', 'end_of_list')
    else:
        start['phase'] = np.where(start.what == 'word', 'pre_list', 'post_list')
        start['serialpos'] = np.nan
    start.loc[start.practice, 'phase'] = None
    start.loc[start.practice, ['list', 'serialpos']] = np.nan
    start['seconds'] = (start.stop_ms - start.start_ms) / 1000
    P = M[M.tt == 'PROB'].merge(start[['sid', 'block', 'list', 'serialpos', 'phase', 'practice', 'seconds']],
                                on=['sid', 'block'], how='left')
    P['correct'] = (P.answer == P.test_x + P.test_y + P.test_z).astype(int)
    P['duration'] = P.next_ms - P.ms
    P = P.merge(sess[['sid', 'subject', 'session']], on='sid', how='left')
    cols = ['subject', 'session', 'block', 'list', 'phase', 'serialpos', 'practice', 'seconds', 'test_x', 'test_y',
            'test_z', 'answer', 'correct', 'duration', 'ms']
    return P[cols].rename(columns={'ms': 'mstime', 'seconds': 'block_seconds'}).reset_index(drop=True)


# -------------------------------------------------------------------------------------- Experiment 4 (task-ltpFR2)
def _scan_ltpfr2(root, verbose):
    raw, sess = _read_all('ltpFR2', root, verbose)
    sess['experiment'] = 4
    W, R, rs, first = _lists(raw)
    D = raw[(raw.tt == 'DISTRACTOR') & (raw.tr >= 1)]
    D = D.assign(list=D.tr.astype(int)).merge(W.groupby(['sid', 'list']).ms.min().rename('first_word').reset_index(),
                                              on=['sid', 'list'], how='inner')
    pre = D[D.ms < D.first_word][['sid', 'list']].drop_duplicates().assign(pre_distractor=True)
    W = W.merge(pre, on=['sid', 'list'], how='left')
    R = R.merge(pre, on=['sid', 'list'], how='left')
    for x in (W, R):
        x['pre_distractor'] = x.pre_distractor.fillna(False).astype(bool)
    n = W.groupby('sid').list.nunique()
    all24 = W.groupby('sid').list_length.agg(lambda s: (s == 24).all())
    sess['n_lists'] = sess.sid.map(n).fillna(0).astype(int)
    sess['session_complete'] = (sess.n_lists == 24) & sess.sid.map(all24).fillna(False).astype(bool)
    ok = sess.sid[sess.session_complete & (sess.session < 23)]
    pool = set(W.item_num[W.sid.isin(set(ok))].unique())
    ses23 = set(sess.sid[sess.session == 23])
    for x in (W, R):
        x['novel'] = x.sid.isin(ses23) & ~x.item_num.isin(pool) & (x.item_num >= 0)
    ev = _finish([W, R], sess, 'ltpFR2', ['pre_distractor', 'novel', 'source_list', 'source_serialpos'], root)
    return {'events': ev, 'math': _math(raw, sess, W, rs, 4), 'sessions': sess}


# ---------------------------------------------------------------------------------------- Experiment 5 (task-VFFR)
def _scan_vffr(root, verbose):
    raw, sess = _read_all('VFFR', root, verbose)
    sess['experiment'] = 5
    W = raw[raw.tt == 'WORD'].copy().sort_values(['sid', 'tr'], kind='stable').reset_index(drop=True)
    W['trial'] = W.tr.astype(int)
    W['list'] = W.trial // 24 + 1
    W['serialpos'] = W.trial % 24 + 1
    W['item_num'] = W.item_num.fillna(-1).astype(int)
    W['list_length'] = 24
    off = raw[raw.tt == 'WORD_OFF'].groupby(['sid', 'tr']).ms.min().rename('off').reset_index()
    R = raw[raw.tt == 'REC_WORD'].copy().sort_values(['sid', 'ms'], kind='stable').reset_index(drop=True)
    R = R.merge(off, on=['sid', 'tr'], how='left')
    R = R.merge(W[['sid', 'tr', 'item_name']].rename(columns={'item_name': 'shown'}), on=['sid', 'tr'], how='left')
    R['trial'] = R.tr.astype(int)
    R['list'] = R.trial // 24 + 1
    R['serialpos'] = R.trial % 24 + 1
    R['item_num'] = R.item_num.fillna(-1).astype(int)
    R['rectime'] = R.ms - R.off
    R['outpos'] = R.groupby(['sid', 'trial']).cumcount() + 1
    R['repeat'] = R.groupby(['sid', 'trial', 'item_name']).cumcount()
    R['intrusion'] = np.where(R.item_name == R.shown, 0, -1)      # 0 = the subject said the word shown
    R['list_length'] = 24
    said = R.loc[R.intrusion == 0, ['sid', 'trial']].drop_duplicates().assign(recalled=1)
    W = W.merge(said, on=['sid', 'trial'], how='left')
    W['recalled'] = W.recalled.fillna(0).astype(int)              # 1 = read aloud correctly on its trial
    W['type'] = 'WORD'
    R['type'] = 'REC_WORD'
    F = raw[raw.tt == 'FFR_REC_WORD'].copy().sort_values(['sid', 'ms'], kind='stable').reset_index(drop=True)
    F['item_num'] = F.item_num.fillna(-1).astype(int)
    F['rectime'] = F.ms - F.sid.map(raw[raw.tt == 'FFR_START'].groupby('sid').ms.min())
    F['outpos'] = F.groupby('sid').cumcount() + 1
    F['repeat'] = F.groupby(['sid', 'item_name']).cumcount()
    # A word counts as correct if it is one of the session's 576 words. Match on the word, not its number.
    pool = W[['sid', 'item_name']].drop_duplicates().assign(inpool=True)
    F = F.merge(pool, on=['sid', 'item_name'], how='left')
    F['intrusion'] = np.where(F.inpool.fillna(False).astype(bool), 0, -1)
    F['type'] = 'FFR_REC_WORD'
    for x in (R, F):
        x['too_fast'] = np.nan
    F['trial'] = np.nan
    F['list'] = np.nan
    sess['n_words'] = sess.sid.map(W.groupby('sid').size()).fillna(0).astype(int)
    sess['n_lists'] = sess.sid.map(W.groupby('sid').list.nunique()).fillna(0).astype(int)
    sess['session_complete'] = sess.n_words == 576
    sess['has_ffr'] = sess.sid.isin(set(raw.sid[raw.tt.isin(['FFR_START', 'FFR_REC_WORD'])]))
    ev = _finish([F, W, R], sess, 'VFFR', ['trial', 'too_fast', 'has_ffr'], root)
    return {'events': ev, 'sessions': sess}


_SCAN = {'ltpFR': _scan_ltpfr, 'ltpFR2': _scan_ltpfr2, 'VFFR': _scan_vffr}


def _load_task(task, root=None, cache=True, verbose=True):
    root = find_root(root)
    cdir = os.path.join(os.path.dirname(root), 'peers-cache')
    cfile = os.path.join(cdir, f'{task}_{_commit(root)}_v{CACHE_VERSION}.pkl')
    if cache and os.path.exists(cfile):
        return pd.read_pickle(cfile)
    if verbose:
        print(f'peers: reading the {task} session files (once; cached afterwards) ...', flush=True)
    out = _SCAN[task](root, verbose)
    if cache:
        os.makedirs(cdir, exist_ok=True)
        pd.to_pickle(out, cfile)
    return out


# ----------------------------------------------------------------------------------------------------- public API
def load_events(experiment, root=None, subjects=None, complete_sessions_only=False, cache=True, verbose=True):
    """Events of one PEERS experiment (1-5) as a tidy DataFrame; see the module docstring for the columns.

    Every subject and session in the public files is returned, including the older adults of Experiment 1,
    subjects who did not finish, and partial sessions. Select with age_group, session_complete and the counts in
    session_table(). The first call per task reads the files (about a minute) and writes a cache beside the data
    folder; later calls read the cache.
    """
    if experiment not in EXPERIMENT_TASK:
        raise ValueError('experiment must be 1, 2, 3, 4 or 5')
    ev = _load_task(EXPERIMENT_TASK[experiment], root, cache=cache, verbose=verbose)['events']
    ev = ev[ev.experiment == experiment]
    if subjects is not None:
        ev = ev[ev.subject.isin(list(subjects))]
    if complete_sessions_only:
        ev = ev[ev.session_complete]
    ev = ev.dropna(axis=1, how='all').reset_index(drop=True)
    for c in ev.select_dtypes('category').columns:
        ev[c] = ev[c].cat.remove_unused_categories()
    return ev


def load_recognition(root=None, cache=True, verbose=True):
    """Experiments 1-3: one row per recognition probe.

    target (1 studied this session, 0 lure), response (1 "old", 0 "new"), confidence (1 very low - 5 complete),
    rt and conf_rt (ms from probe onset to the spoken response and to the confidence rating), block (the
    'trial' value on the probe row), and, for targets, where the word was studied (study_list, study_serialpos),
    whether it was recalled after its list, its encoding task and its list's conditions.
    """
    return _load_task('ltpFR', root, cache=cache, verbose=verbose)['recog'].copy()


def load_math(experiment, root=None, cache=True, verbose=True):
    """Arithmetic problems (A + B + C = ?) of Experiment 2 or 4: one row per problem.

    answer is the subject's response and correct compares it with the sum. duration is ms to the next problem
    or to the end of the block. block numbers the arithmetic periods of a session in order and block_seconds is
    the period's length. list and phase say what the period preceded: Experiment 2 'before_word' (with the
    word's serialpos) or 'end_of_list'; Experiment 4 'pre_list' or 'post_list'. practice marks a block that
    belongs to no list: the warm-up that opens each session (about 20 s in Experiment 2, 11 s in Experiment
    4) and, in a few interrupted sessions, blocks whose list rows are missing.
    """
    if experiment not in (2, 4):
        raise ValueError('arithmetic distractors occur in Experiments 2 and 4 only')
    m = _load_task(EXPERIMENT_TASK[experiment], root, cache=cache, verbose=verbose)['math'].copy()
    return m if experiment == 2 else m.drop(columns='serialpos')


def session_table(root=None, cache=True, verbose=True):
    """One row per session file: subject, task, experiment, session, n_lists, session_complete, and the
    experiment's flags (group, has_ffr, has_recog, math_logged), with age and age_group."""
    root = find_root(root)
    rows = []
    for task in ('ltpFR', 'ltpFR2', 'VFFR'):
        s = _load_task(task, root, cache=cache, verbose=verbose)['sessions'].drop(columns='sid').copy()
        s.insert(1, 'task', task)
        rows.append(s)
    t = pd.concat(rows, ignore_index=True, sort=False)
    P = participants(root).set_index('subject')
    t['age'] = t.subject.map(P.age)
    t['age_group'] = t.subject.map(P.age_group).fillna('unknown')
    return t


def to_pybeh(events):
    """Matrices in pybeh's conventions from the WORD and REC_WORD rows of load_events().

    Returns a dict: recalls (lists x outputs; serial position, -1 for any intrusion, 0 padding), times (ms from
    the start of recall, 0 padding), intrusions (k > 0 prior-list intrusion from k lists back, -1 extra-list,
    0 otherwise), rec_itemnos, pres_itemnos, and one entry per row of those matrices in subjects, sessions,
    lists; list_length is the length of the longest list. Repeats are kept: pybeh's functions mask them, and
    pybeh.mask_maker.make_clean_recalls_mask2d(recalls) marks the first correct recall of each word.
    """
    w = events[events.type == 'WORD'].sort_values(['subject', 'session', 'list', 'serialpos'], kind='stable')
    r = events[events.type == 'REC_WORD'].sort_values(['subject', 'session', 'list', 'outpos'], kind='stable')
    keys = w[['subject', 'session', 'list']].drop_duplicates().reset_index(drop=True)
    row = {k: i for i, k in enumerate(zip(keys.subject.astype(str), keys.session, keys.list))}
    n = len(keys)
    L = int(w.serialpos.max())
    nout = int(r.outpos.max()) if len(r) else 1
    pres = np.zeros((n, L), int)
    wi = np.array([row[k] for k in zip(w.subject.astype(str), w.session, w.list)])
    pres[wi, w.serialpos.values.astype(int) - 1] = w.item_num.values
    recalls = np.zeros((n, nout), int)
    times = np.zeros((n, nout))
    intr = np.zeros((n, nout), int)
    items = np.zeros((n, nout), int)
    if len(r):
        ri = np.array([row.get(k, -1) for k in zip(r.subject.astype(str), r.session, r.list)])
        ok = ri >= 0
        j = r.outpos.values.astype(int)[ok] - 1
        ri = ri[ok]
        sp = r.serialpos.values[ok].astype(float)
        recalls[ri, j] = np.where(np.isnan(sp), -1, sp).astype(int)
        times[ri, j] = r.rectime.values[ok]
        intr[ri, j] = r.intrusion.values[ok]
        items[ri, j] = r.item_num.values[ok]
    return dict(recalls=recalls, times=times, intrusions=intr, rec_itemnos=items, pres_itemnos=pres,
                subjects=keys.subject.astype(str).values, sessions=keys.session.values, lists=keys.list.values,
                list_length=L)
