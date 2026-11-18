"""peers_analysis.py -- the standard free-recall measures for PEERS events, and the figure style.

Convention: compute each measure within a subject, pooling that subject's lists, then average the subjects with
equal weight. Every function here returns one row per subject (and per level of `by`); summarize() takes the
mean across subjects with its standard error and 95% confidence interval.

    import peers, peers_analysis as pa
    ev = peers.load_events(1)
    ev = ev[(ev.age_group == 'young') & ev.session_complete]
    pa.summarize(pa.spc(ev), 'prob', by='serialpos')
    pa.summarize(pa.lag_crp(ev, by='list_type'), 'prob', by=['list_type', 'lag'])
    pa.standard_figure(ev, title='PEERS Experiment 1').savefig('exp1.pdf')

`by` names columns that are constant within a list (list_type, distractor, pre_distractor, session, group ...).
lag_crp() and temporal_factor() call pybeh (pip install git+https://github.com/pennmem/pybeh). The rest needs
only pandas and numpy. Do not use pybeh.irt until pennmem/pybeh pull request 7 is merged; irt_family() below
takes the differences itself.
"""
import numpy as np
import pandas as pd

import peers

KEYS = ['subject', 'session', 'list']
INK, INK2, GRID = '#0b0b0b', '#52514e', '#e1e0d9'
BLUE, ORANGE, AQUA = '#2a78d6', '#eb6834', '#1baf7a'        # condition colors, in this fixed order; at most three
MARKERS = ['o', 'D', 's']


def _by(by):
    return [by] if isinstance(by, str) else list(by or [])


def _words(ev):
    return ev[ev.type == 'WORD']


def _recalls(ev):
    return ev[ev.type == 'REC_WORD']


def _lists(ev, by=()):
    return _words(ev).drop_duplicates(KEYS)[KEYS + _by(by)]


def _pybeh(name):
    try:
        import importlib
        return getattr(importlib.import_module(f'pybeh.{name}'), name)
    except ImportError:
        try:
            import pybeh_pd
            return getattr(pybeh_pd, name)
        except ImportError:
            raise ImportError('needs pybeh: pip install git+https://github.com/pennmem/pybeh') from None


# ------------------------------------------------------------------------------------------- measures by subject
def recall_probability(ev, by=()):
    """Proportion of studied words recalled: subject, *by, p_recall, n_lists."""
    by = _by(by)
    out = _words(ev).groupby(['subject'] + by, observed=True).recalled.mean().rename('p_recall').reset_index()
    n = _lists(ev, by).groupby(['subject'] + by, observed=True).size().rename('n_lists').reset_index()
    return out.merge(n, on=['subject'] + by)


def spc(ev, by=()):
    """Serial position curve: subject, *by, serialpos, prob."""
    by = _by(by)
    return (_words(ev).groupby(['subject'] + by + ['serialpos'], observed=True).recalled.mean()
            .rename('prob').reset_index())


def pfr(ev, by=(), output=1):
    """Probability of first recall by serial position: subject, *by, serialpos, prob.

    The denominator is every list of the subject, so lists that begin with an intrusion or have no response
    count against every position (as in pybeh.pfr). output=2 gives the second response, and so on.
    """
    by = _by(by)
    lists = _lists(ev, by)
    r = _recalls(ev)
    first = r[(r.outpos == output) & (r.intrusion == 0) & (r.repeat == 0)][KEYS + ['serialpos']].merge(lists, on=KEYS)
    num = first.groupby(['subject'] + by + ['serialpos'], observed=True).size().rename('k')
    den = lists.groupby(['subject'] + by, observed=True).size().rename('n').reset_index()
    pos = pd.DataFrame({'serialpos': np.arange(1, int(_words(ev).serialpos.max()) + 1)})
    grid = den.merge(pos, how='cross').merge(num.reset_index(), on=['subject'] + by + ['serialpos'], how='left')
    grid['prob'] = grid.k.fillna(0) / grid.n
    return grid[['subject'] + by + ['serialpos', 'prob']]


def _matrix_measure(ev, by, fn):
    by = _by(by)
    groups = [((), ev)] if not by else ev[ev.type != 'FFR_REC_WORD'].groupby(by, observed=True)
    out = []
    for level, x in groups:
        m = peers.to_pybeh(x)
        t = fn(m)
        level = level if isinstance(level, tuple) else (level,)
        for c, v in zip(by, level):
            t[c] = v
        out.append(t)
    return pd.concat(out, ignore_index=True)


def lag_crp(ev, max_lag=5, skip_first=0, by=()):
    """Lag-CRP (Kahana, 1996), computed by pybeh.crp: subject, *by, lag, prob.

    Transitions to or from a repetition or an intrusion are left out, and each transition is conditioned on the
    words not yet recalled. skip_first=2 leaves out the first two output positions, as Healey, Long and Kahana
    (2019) did.
    """
    crp = _pybeh('crp')

    def fn(m):
        c = np.asarray(crp(m['recalls'], m['subjects'], m['list_length'], lag_num=max_lag, skip_first_n=skip_first))
        lags = np.arange(-max_lag, max_lag + 1)
        subs = np.unique(m['subjects'])
        return pd.DataFrame({'subject': np.repeat(subs, len(lags)), 'lag': np.tile(lags, len(subs)),
                             'prob': c.ravel()})
    out = _matrix_measure(ev, by, fn)
    return out[['subject'] + _by(by) + ['lag', 'prob']]


def temporal_factor(ev, skip_first=0, by=()):
    """Temporal clustering factor (Polyn, Norman & Kahana, 2009), by pybeh.temp_fact: subject, *by,
    temporal_factor. Chance is 0.5."""
    tf = _pybeh('temp_fact')

    def fn(m):
        v = np.asarray(tf(m['recalls'], m['subjects'], m['list_length'], skip_first_n=skip_first))
        return pd.DataFrame({'subject': np.unique(m['subjects']), 'temporal_factor': v})
    out = _matrix_measure(ev, by, fn)
    return out[['subject'] + _by(by) + ['temporal_factor']]


def intrusions(ev, by=()):
    """Mean counts per list: subject, *by, correct, pli, eli, repetitions, responses, n_lists.

    pli = prior-list intrusions (a word from an earlier list of the session), eli = extra-list intrusions,
    repetitions = second and later reports of a word from the current list.
    """
    by = _by(by)
    L = _lists(ev, by).merge(_words(ev).groupby(KEYS, observed=True).recalled.sum().rename('correct').reset_index(),
                             on=KEYS)
    r = _recalls(ev)
    for name, mask in (('pli', r.intrusion > 0), ('eli', r.intrusion == -1),
                       ('repetitions', (r.intrusion == 0) & (r.repeat > 0)), ('responses', r.outpos > 0)):
        c = r[mask].groupby(KEYS, observed=True).size().rename(name).reset_index()
        L = L.merge(c, on=KEYS, how='left')
        L[name] = L[name].fillna(0)
    g = L.groupby(['subject'] + by, observed=True)
    out = g[['correct', 'pli', 'eli', 'repetitions', 'responses']].mean()
    out['n_lists'] = g.size()
    return out.reset_index()


def pli_by_lag(ev, max_lag=5, by=()):
    """Prior-list intrusions by how many lists back the word was studied: subject, *by, list_lag, prop.

    Only lists after the first max_lag of a session are used, so that every lag was possible. prop is the share
    of the subject's prior-list intrusions on those lists that came from list_lag lists back; the shares need
    not sum to 1 because some come from further back. Subjects with no such intrusion are absent.
    """
    by = _by(by)
    r = _recalls(ev)
    r = r[(r.intrusion > 0) & (r.list > max_lag)]
    tot = r.groupby(['subject'] + by, observed=True).size().rename('n').reset_index()
    k = (r[r.intrusion <= max_lag].groupby(['subject'] + by + ['intrusion'], observed=True).size().rename('k')
         .reset_index().rename(columns={'intrusion': 'list_lag'}))
    grid = tot.merge(pd.DataFrame({'list_lag': np.arange(1, max_lag + 1)}), how='cross')
    grid = grid.merge(k, on=['subject'] + by + ['list_lag'], how='left')
    grid['prop'] = grid.k.fillna(0) / grid.n
    return grid[['subject'] + by + ['list_lag', 'prop']]


def irt_family(ev, min_lists=5, by=()):
    """Inter-response times as a family of curves, one per number of words recalled (Murdock & Okada, 1970):
    subject, *by, n_recalled, outpos, irt (seconds), n_lists.

    Lists are partitioned on the number of correct recalls (first reports of words from the list). The value
    at outpos k is the time from the (k-1)th to the kth correct recall, kept only when no repetition or
    intrusion came between them. A subject enters a partition only with at least min_lists lists in it,
    because with equal weighting one slow list from a subject with no other list in the partition can move a
    point. Do not pool these times across n_recalled: the curves differ, and each rises steeply at its end.
    """
    by = _by(by)
    r = _recalls(ev).sort_values(KEYS + ['outpos'], kind='stable')
    c = r[(r.intrusion == 0) & (r.repeat == 0)].copy()
    g = c.groupby(KEYS, observed=True)
    c['k'] = g.cumcount() + 1
    c['n_recalled'] = g.k.transform('max')
    c['irt'] = np.where(c.outpos - g.outpos.shift() == 1, (c.rectime - g.rectime.shift()) / 1000, np.nan)
    c = c[c.k >= 2]
    bad = c[c.irt <= 0][KEYS].drop_duplicates().assign(bad=True)       # two responses with the same time stamp
    c = c.merge(bad, on=KEYS, how='left')
    c = c[c.bad.isna()]
    part = ['subject'] + by + ['n_recalled']
    nl = c.drop_duplicates(KEYS).groupby(part, observed=True).size().rename('n_lists').reset_index()
    out = c.groupby(part + ['k'], observed=True).irt.mean().rename('irt').reset_index().merge(nl, on=part)
    out = out[out.n_lists >= min_lists].rename(columns={'k': 'outpos'})
    return out[part + ['outpos', 'irt', 'n_lists']].reset_index(drop=True)


def recognition_rates(rec, by=()):
    """Hit and false-alarm rates of the end-of-session recognition test (Experiments 1-3): subject, *by,
    hit_rate, fa_rate, n_targets, n_lures. `by` may use session-level columns of the recognition table
    (experiment, session). Probes without a response are left out.
    """
    by = _by(by)
    v = rec[rec.response.isin([0, 1])]
    g = v.groupby(['subject'] + by + ['target'], observed=True).response
    t = g.mean().unstack('target').rename(columns={1: 'hit_rate', 0: 'fa_rate'})
    n = g.size().unstack('target').rename(columns={1: 'n_targets', 0: 'n_lures'})
    return t.join(n).reset_index()[['subject'] + by + ['hit_rate', 'fa_rate', 'n_targets', 'n_lures']]


# -------------------------------------------------------------------------------------------------- across subjects
def summarize(table, value, by=()):
    """Mean across subjects of a per-subject table: *by, mean, sem, ci_lo, ci_hi, n.

    The interval is the 95% t interval across subjects. For a contrast between conditions that every subject
    contributes to, use a within-subject interval instead (pybeh_pd.loftus_masson_analytic or
    pybeh_pd.cousineau), as the lab's papers do.
    """
    from scipy import stats
    by = _by(by)
    t = table.dropna(subset=[value])
    g = t.groupby(by, observed=True)[value] if by else t.assign(_all=0).groupby('_all')[value]
    out = g.agg(mean='mean', sd=lambda s: s.std(ddof=1), n='size').reset_index()
    out['sem'] = out['sd'] / np.sqrt(out['n'])
    h = out['sem'] * stats.t.ppf(0.975, np.maximum(out['n'] - 1, 1))
    out['ci_lo'], out['ci_hi'] = out['mean'] - h, out['mean'] + h
    return out[by + ['mean', 'sem', 'ci_lo', 'ci_hi', 'n']]


# ------------------------------------------------------------------------------------------------------------ figures
def set_style():
    """Matplotlib settings for the lab's figures: Arial-metric sans serif, no top or right spine, vector text."""
    import matplotlib as mpl
    from matplotlib import font_manager
    have = {f.name for f in font_manager.fontManager.ttflist}
    family = next((f for f in ('Arial', 'Liberation Sans', 'Helvetica') if f in have), 'DejaVu Sans')
    mpl.rcParams.update({
        'font.family': family, 'font.size': 8.5, 'axes.labelsize': 9, 'axes.titlesize': 9,
        'xtick.labelsize': 8, 'ytick.labelsize': 8, 'legend.fontsize': 8, 'legend.frameon': False,
        'axes.spines.top': False, 'axes.spines.right': False, 'axes.edgecolor': INK2, 'axes.linewidth': 0.6,
        'axes.labelcolor': INK, 'xtick.color': INK2, 'ytick.color': INK2, 'xtick.major.width': 0.6,
        'ytick.major.width': 0.6, 'lines.linewidth': 1.6, 'pdf.fonttype': 42, 'ps.fonttype': 42,
        'savefig.dpi': 300, 'figure.dpi': 150})
    return family


def plot_curve(ax, x, mean, err=None, color=INK, marker='o', label=None, line=True, ms=4.2):
    """One observed curve: a thin line, markers ringed in white, and error bars (pass sem or a CI half-width)."""
    x, mean = np.asarray(x, float), np.asarray(mean, float)
    if err is not None:
        ax.errorbar(x, mean, yerr=np.asarray(err, float), fmt='none', ecolor=color, elinewidth=0.8, zorder=2)
    if line:
        ax.plot(x, mean, '-', color=color, lw=1.3, zorder=3)
    ax.plot(x, mean, marker, color=color, ms=ms, mec='white', mew=0.8, lw=0, zorder=4, label=label)


def plot_lag_crp(ax, summary, color=INK, marker='o', label=None):
    """Lag-CRP from summarize(lag_crp(ev), 'prob', by='lag'): the curve is broken at lag 0."""
    s = summary.sort_values('lag')
    for i, part in enumerate((s[s.lag < 0], s[s.lag > 0])):
        plot_curve(ax, part.lag, part['mean'], part.ci_hi - part['mean'], color=color, marker=marker,
                   label=label if i == 0 else None)
    L = int(s.lag.abs().max())
    ax.set_xticks([t for t in range(-L, L + 1) if t % 2])
    ax.set_xlabel('Lag')
    ax.set_ylabel('Conditional response probability')
    ax.set_ylim(bottom=0)


def standard_figure(ev, title=None, min_lists=5, partitions=4):
    """Four panels for one condition of list recall: serial position curve, probability of first recall,
    lag-CRP, and the family of inter-response-time curves. Error bars are 95% confidence intervals across
    subjects. Returns the figure (7.5 x 2.6 in); save as PDF.
    """
    import matplotlib.pyplot as plt
    set_style()
    fig, axs = plt.subplots(1, 4, figsize=(7.5, 2.6))
    fig.subplots_adjust(left=0.07, right=0.99, top=0.86, bottom=0.2, wspace=0.42)
    n = ev.subject.nunique()
    s = summarize(spc(ev), 'prob', 'serialpos')
    plot_curve(axs[0], s.serialpos, s['mean'], s.ci_hi - s['mean'])
    axs[0].set(xlabel='Serial position', ylabel='Recall probability', ylim=(0, 1))
    s = summarize(pfr(ev), 'prob', 'serialpos')
    plot_curve(axs[1], s.serialpos, s['mean'], s.ci_hi - s['mean'])
    axs[1].set(xlabel='Serial position', ylabel='Probability of first recall')
    axs[1].set_ylim(bottom=0)
    L = int(s.serialpos.max())
    for ax in axs[:2]:
        ax.set_xticks([1] + list(range(4, L + 1, 4)))
    plot_lag_crp(axs[2], summarize(lag_crp(ev), 'prob', 'lag'))
    f = irt_family(ev, min_lists=min_lists)
    counts = f.drop_duplicates(['subject', 'n_recalled']).groupby('n_recalled').n_lists.sum()
    lo = max(counts.index, key=lambda a: sum(counts.get(a + i, 0) for i in range(partitions)))
    for i, n_rec in enumerate(range(lo, lo + partitions)):       # the adjacent partitions that hold the most lists
        s = summarize(f[f.n_recalled == n_rec], 'irt', 'outpos')
        if s.empty:
            continue
        plot_curve(axs[3], s.outpos, s['mean'], s.ci_hi - s['mean'], ms=3.2)
        axs[3].annotate(str(n_rec), (s.outpos.iloc[-1], s.ci_hi.iloc[-1]), xytext=(0, 2 + 7 * (i % 2)),
                        textcoords='offset points', ha='center', va='bottom', fontsize=7.5, color=INK2)
    axs[3].set_yscale('log')
    axs[3].set_yticks([1, 2, 5, 10, 20])
    axs[3].set_yticklabels(['1', '2', '5', '10', '20'])
    axs[3].minorticks_off()
    axs[3].set(xlabel='Output position', ylabel='Inter-response time (s)')
    for ax, t in zip(axs, 'ABCD'):
        ax.set_title(t, loc='left', fontweight='bold')
    axs[3].text(0.03, 0.97, 'Labels give the number\nof words recalled', transform=axs[3].transAxes, va='top',
                fontsize=7.5, color=INK2)
    if title:
        fig.suptitle(f'{title} (N = {n})', x=0.07, ha='left', fontsize=9)
    return fig


if __name__ == '__main__':
    import sys
    exp = int(sys.argv[1]) if len(sys.argv) > 1 else 4
    out = sys.argv[2] if len(sys.argv) > 2 else f'peers{exp}_standard.pdf'
    e = peers.load_events(exp)
    e = e[e.session_complete]
    standard_figure(e, title=f'PEERS Experiment {exp}, every subject and complete session').savefig(out)
    print('wrote', out)
