# PEERS behavioral data: where it is and what is in it

Contents: 1. Public release. 2. What the loader returns. 3. Raw columns. 4. Traps. 5. Public files versus
published samples. 6. The lab's internal copies.

Source tags used in the reference files: **[P]** Kahana, Lohnas, Healey, et al. (2024), *JEP:LMC*, 50(9),
1421-1443, doi 10.1037/xlm0001319. **[M]** the lab's internal methods files for each experiment.
**[W]** the lab wiki, https://memory.psych.upenn.edu/PEERS. **[D]** checked in the public files (most of these
checks are in `scripts/selftest.py`).

## 1. Public release

OpenNeuro **ds004395**, version 2.0.0, CC0. GitHub mirror: https://github.com/OpenNeuroDatasets/ds004395
(commit `798377a4d`). BIDS layout. 364 subjects, `sub-LTP063` to `sub-LTP440`.

| Experiment | Task label | Sessions (file numbers, 0-based) | Subjects | Session files |
|---|---|---|---|---|
| 1 | `ltpFR` | 0-6 | 237 | 1,582 |
| 2 | `ltpFR` | 7-13 (LTP063-LTP209), 7-15 (LTP210 and later) | 166 | 1,249 |
| 3 | `ltpFR` | 14-19 (LTP063-LTP209), 16-19 (LTP210 and later) | 156 | 802 |
| 4 | `ltpFR2` | 0-23 | 127 | 2,469 |
| 5 | `VFFR` | 0-9 | 57 | 462 |

Files: `sub-LTP###/ses-N/beh/sub-LTP###_ses-N_task-<label>_beh.tsv`, one per session, with a `.json` data
dictionary. `participants.tsv` gives age, sex and handedness. The EEG (about 8.7 TB) and the word-pool files under
`stimuli/` are in git-annex and are not fetched. The `eeg/*_events.tsv` files repeat the behavioral rows with
EEG sample numbers and add no behavioral field.

`scripts/fetch_peers.sh [DEST]` makes a sparse, blob-less clone holding only the 6,564 behavioral files (under a
minute, about 1 GB). The screening session that preceded enrollment is not in the release, and neither are the
psychometric sessions [D].

Subjects overlap: 41 did Experiments 1-3 and Experiment 4, 16 did Experiments 4 and 5, 4 did all [D]. A
subject's age is one number for all of their sessions.

## 2. What the loader returns

`peers.load_events(n)` gives one row per studied word and per recalled word, with the fields the public files
lack. Run `help(peers)` and `print(peers.CONDITION_COLUMNS)` for the full list. The essentials:

- `type`: `WORD`, `REC_WORD`, `FFR_REC_WORD`.
- `list` and `serialpos`: list number within the session and position within the list, both from 1.
- `recalled` (WORD rows): 1 if recalled after its own list.
- `intrusion` (recall rows): 0 correct; k > 0 prior-list intrusion from k lists back in the session; -1 extra-list.
- `repeat` (recall rows): 0 for the first report of a word in a recall period, 1 for the second, and so on.
- `rectime`: ms from the start of the recall period. `outpos`: output position, counting every response.
- `session_complete`, `age_group`, and the condition columns of each experiment.

The lab's own events store the source-list position of a prior-list intrusion in `serialpos`. The loader leaves
`serialpos` empty for every intrusion and puts that position in `source_serialpos`. Checked against the lab's
events for LTP093 (five sessions, in `pennmem/pybeh_pd/tests/data`): every row matches, 4,249 of 4,249, apart
from that convention [D].

Other tables: `load_recognition()` (Experiments 1-3), `load_math(2 or 4)`, `session_table()`, `participants()`.
`to_pybeh(events)` gives pybeh's matrices.

## 3. Raw columns

`ltpFR`: `mstime, trial_type, stim_file, subject, experiment, session, trial, task, item_name, item_num,
recog_resp, recog_conf, resp, answer, test_x, test_y, test_z, color_r, color_g, color_b, case, font`.
`ltpFR2`: `mstime, trial_type, stim_file, subject, experiment, session, trial, item_name, item_num, list, answer,
test_x, test_y, test_z`. `VFFR`: `mstime, trial_type, stim_file, subject, experiment, session, trial, item_name,
item_num, too_fast`.

- `trial` is the list number (the recognition block on recognition rows; the trial 0-575 in `VFFR`).
- `item_num` is the word's number in the 1,638-word pool; -1 marks a word outside the pool.
- `task`: -1 none, 0 size, 1 animacy. `resp`: the judgment, 0 small or nonliving, 1 big or living.
- `recog_resp`: 1 old, 0 new. `recog_conf`: 1 (very low) to 5 (complete).
- `answer` is the subject's typed sum; `test_x + test_y + test_z` is the correct one.

Row types. `ltpFR`: `SESS_START, WORD, REC_START, REC_WORD, REC_WORD_VV, FFR_REC_WORD, FFR_REC_WORD_VV,
RECOG_TARGET, RECOG_LURE, RECOG_RESP, RECOG_CONF, RECOG_RESP_VV, START, PROB, STOP, SLOW_MSG, KEY_MSG,
REST_REWET, SESS_END`. `ltpFR2`: `SESS_START, START, PROB, STOP, DISTRACTOR, WORD, REC_START, REC_WORD,
REC_WORD_VV, REST_REWET, SESS_END`. `VFFR`: `SESS_START, FFR_START, FFR_REC_WORD, FFR_REC_WORD_VV, FFR_STOP,
PRACTICE_WORD, PRACTICE_WORD_OFF, PRACTICE_REC_START, PRACTICE_REC_WORD, PRACTICE_REC_WORD_VV,
PRACTICE_REC_STOP, COUNTDOWN, WORD, WORD_OFF, REC_START, REC_WORD, REC_WORD_VV, REC_STOP, BREAK_START,
BREAK_STOP, SESS_END`. `_VV` rows are vocalizations that are not words; the loader drops them.

## 4. Traps

1. **Session numbers.** File names count from 0; the paper and wiki count from 1. The `session` column inside a
   file is wrong in `LTP067` ses-13 and empty in `LTP158` ses-3. The loader uses the file name.
2. **`list` in the raw `ltpFR2` files is not the list number.** It counts distractor periods. `trial` is the list.
3. **No serial position, recalled flag, intrusion code or recall time in the public files.** The loader derives
   them. Do not expect the lab's event fields when reading a raw file.
4. **Externalized recall: the spacebar marks are missing.** The public files do not say which Experiment 3
   responses the subject rejected, so rejection analyses (Lohnas et al., 2015) need the lab's internal events.
5. **Words repeat across sessions.** In Experiments 1-3 a session uses 256 of the 1,638 words (192 or 224 in
   Experiment 2) and words recur from the third session on. In Experiments 4 and 5 every session uses the same
   576 words. The intrusion code -1 therefore includes words studied in earlier sessions.
6. **`item_num` is -1 for the ten practice words of each Experiment 5 session.** Decide whether a recalled word
   belongs to the 576 by matching the word, as the loader does.
7. **Arithmetic rows are incomplete.** One Experiment 2 session (`LTP244` ses-11) has none, and 178 lists in 49
   Experiment 4 sessions have none. The loader takes the Experiment 2 condition of each list from timing and the
   Experiment 4 pre-list flag from the `DISTRACTOR` rows, both of which are complete.
8. **Each session of Experiments 2 and 4 opens with a warm-up arithmetic block** (about 20 s and 11 s). It
   belongs to no list; `load_math` marks it `practice`.
9. **Seven sessions are incomplete:** `LTP158` ses-3 and `LTP255` ses-0 (`ltpFR`); `LTP298` ses-9 and ses-10,
   `LTP325` ses-14, `LTP331` ses-5 (`ltpFR2`); `LTP411` ses-4 (`VFFR`). Filter on `session_complete`.
10. **Age is missing for 35 subjects**, labeled `age_group == 'unknown'`. All 35 took part in Experiment 4,
    which enrolled young adults only; 25 of them also did Experiments 1-3 and 8 did Experiment 5. Decide whether
    to count them as young and say so. The older adults (40 subjects, ages 60-86) did Experiment 1 only.
11. **Stray values.** One recall is stamped 86.6 s into a 75-s period (`LTP354` ses-7, list 3). In Experiment 4,
    685 recalls fall in the first 200 ms. Sixteen confidence ratings are 0, 6 or 7; 8,051 probes have no rating
    and 2,467 no response.
12. **`pybeh.irt` on master returns recall times in place of the last inter-response time** for the trials with
    the most recalls. The fix is pull request 7 on `pennmem/pybeh`. Use `peers_analysis.irt_family`.

## 5. Public files versus published samples

Published counts come from the lab's internal files at the time of each paper. The public release differs
(`scripts/selftest.py` prints the current comparison):

| | Published | Public files |
|---|---|---|
| Experiment 1, younger adults | 172 [P] | 172 with a session, 152 with seven complete sessions; plus 25 of unknown age, all with seven |
| Older adults | 39 [P]; 38 in Healey et al. (2019) | 40 with a session; 34 with seven complete sessions |
| Experiment 2 | 157 [P] | 166 with a session; 152 with all 7 or 9 sessions |
| Experiment 3 | 60 standard, 92 externalized [P] | 60 and 92 finished; 96 began the externalized condition |
| Experiment 4 | 98 completed 24 sessions [P] | 127 with a session; 83 with 24 complete sessions |
| Experiment 5 | 57 [P] | 57; 45 reached a recall session |

Where a published analysis can be repeated on the public files it comes out close: Lohnas et al. (2015), Table 5,
externalized-recall group (correct recalls, intrusions and repetitions per list) within 0.02; Katerman et al.
(2022) recall counts within three words; Weidemann and Kahana (2016) response times within 45 ms; Healey, Long
and Kahana (2019), r = .50 against .51.

## 6. The lab's internal copies

Not reachable from a cloud session, and not checked from one. From the wiki [W]: on rhino the events are under
`/protocols/ltp/subjects/<subject>/experiments/<ltpFR|ltpFR2|VFFR>/`, read with `cmlreaders`
(`cmlreaders.get_data_index('ltp')`, then `CMLReader(subject, experiment, session).load('events')`), and the EEG
is under `/data/eeg/scalp/ltp/<experiment>/`. Those events carry the lab's own `serialpos`, `recalled`,
`intrusion` and `rectime` fields. Whether they keep the externalized-recall key presses has not been checked.
Prefer the internal events when working on rhino, and use this loader's output as a cross-check. The wiki names
a Box file that lists the 98 Experiment 4 completers.
