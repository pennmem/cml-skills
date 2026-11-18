# PEERS Experiments 1, 2 and 3 (task `ltpFR`)

One cohort did all three in order, 20 sessions in all, so a subject's Experiment 2 and 3 data come from someone
already practiced at the task. Source tags ([P] paper, [M] lab methods files, [W] wiki, [D] checked in the
public files) are defined in `data.md`.

## Subjects and sessions

- Younger adults did Experiments 1-3 (enrollment was 17-30 [M]; 18-30 in the public files [D]). Older adults
  (60 and over) did Experiment 1 only [P][M][D]. Enrollment followed a screening session, which is not in the
  public files [P][D].
- Two cohorts differ after Experiment 1 [W][D]. The loader assigns the experiment from the session number and the
  subject number:

| File session | LTP063-LTP209 | LTP210 and later |
|---|---|---|
| 0-6 | Experiment 1 | Experiment 1 |
| 7-13 | Experiment 2 | Experiment 2 |
| 14-15 | Experiment 3, externalized recall | Experiment 2 |
| 16-19 | Experiment 3, externalized recall | Experiment 3, standard recall |

- Session 0 is the practice session of Experiment 1 and session 7 the practice session of Experiment 2. Some
  papers leave them out ("one practice plus six sessions"); say which you did.
- Each session: lists with immediate recall, then final free recall in about half of the sessions, then a
  recognition test [P][D].

## What every list has in common

- 16 words shown one at a time for 3,000 ms, with 800-1,200 ms between words. After the last word, a 1,200-1,400
  ms delay, a tone and a row of asterisks, then 75 s of spoken recall [P][M]. Word onsets are 4.0 s apart [D].
- Words come from a pool of 1,638, chosen to be clear in meaning and easy to judge for size and animacy [P].
  A session never repeats a word; later sessions reuse words from earlier ones [D].
- Lists were built from word-association-space similarity: four bins (cos θ above 0.7, 0.4-0.7, 0.14-0.4, below
  0.14), two pairs from each bin, one pair in adjacent positions and one separated by at least two items [M].
  Semantic clustering analyses need those similarity values, which are not in the public files.
- **Encoding task** [P]. No-task lists: study for a later test. Task lists: every word is judged for size ("Will
  this item fit into a shoebox?") or animacy ("Does this word refer to something living or not living?").
  Task-shift lists: the judgment alternates every two to six words. Color, font and case cued the judgment.
  Loader columns: `list_type` (`no_task`, `size`, `animacy`, `shift`), `enc_task` per word, `judgment`.
- Responses were spoken and scored offline with Penn TotalRecall [P].

## Experiment 1 (sessions 0-6): immediate free recall

- 16 lists per session. Session 0: lists 1-4 no task, 5-8 one judgment, 9-12 the other, 13-16 task-shift, and
  final free recall always [M][D]. Sessions 1-6: 4 no-task, 3 size, 3 animacy and 6 task-shift lists, the first
  two lists always task-shift [M][D].
- In the public files: 237 subjects (172 younger, 40 older, 25 of unknown age), 1,582 sessions [D].
- Recall probability, all subjects, by list type: no task .64, size .56, animacy .56, task-shift .55 [D].

## Experiment 2: distractor manipulation

- Arithmetic of the form A + B + C = ?, single digits, typed answer [P]. Each list has one of five conditions,
  written as seconds of arithmetic before every word and seconds after the last word: **0-0** (immediate),
  **0-8** and **0-16** (delayed), **8-8** and **16-16** (continual distractor) [P].
  Loader columns: `distractor` and `final_distractor` (0, 8 or 16).
- Session 7: 14 lists, 7 size and 7 animacy, two lists each of 0-0, 0-16 and 16-16 and four each of 0-8 and 8-8;
  lists 1-4 are two 0-8 and two 8-8; final free recall always [M][D].
- Later sessions: 12 lists, 3 size, 3 animacy and 6 task-shift, two lists each of 0-0, 0-16 and 16-16 and three
  each of 0-8 and 8-8; lists 1-2 are one 0-8 and one 8-8 [P][D]. No list is without an encoding task [P][D].
- Word onsets are 4, 12 and 20 s apart with 0, 8 and 16 s of arithmetic [D].
- `peers.load_math(2)` gives every problem with its list, the word it preceded, the answer and whether it was
  correct (93.5% overall) [D].

## Experiment 3: externalized recall

- Same lists as Experiment 1 sessions 1-6 (4 no-task, 3 size, 3 animacy, 6 task-shift) [D].
- **Externalized group** (`group == 'EFR'`, LTP063-LTP209): subjects said every word that came to mind and
  pressed the spacebar after one they knew to be wrong or repeated [P]. Session 14 introduced the instruction
  after its third list, and five sessions followed [M]. Use sessions 15-19: with them the public files
  reproduce Lohnas et al. (2015, Table 5). 92 subjects finished; 96 began [D]. The spacebar marks are not in
  the public files.
- **Standard group** (`group == 'IFR'`, LTP210 and later): ordinary instructions, sessions 16-19. 60 subjects [D].
- Per list, sessions 15-19, the externalized group made 10.60 correct recalls, 0.69 prior-list intrusions, 1.39
  extra-list intrusions and 0.87 repetitions; the standard group made 10.66 correct recalls and 0.075 prior-list
  intrusions [D]. Lohnas et al. (2015, Table 5) report 10.6, 0.68, 1.4 and 0.89, and 10.6 and 0.08.

## Final free recall and recognition

- Final free recall: five minutes to recall words from any list of the session, after a 5-s delay [M]. Rows of
  type `FFR_REC_WORD`, with `source_list` and `source_serialpos`. `has_ffr` marks the sessions.
- Recognition: 320 probes after a 16-list session (240 or 280 after 12 or 14 lists). Targets are words from the
  session and make up 80, 75, 62.5 or 50% of the probes, varying by session [M][D]. The subject says "pess" (old)
  or "po" (new), then rates confidence from 1 to 5, 5 the most confident, and receives feedback [M].
- `peers.load_recognition()`: one row per probe with `target`, `response`, `confidence`, `rt`, and for targets the
  study list and position, the encoding task and whether the word was recalled after its list.
- Weidemann and Kahana (2016) dropped trials with an invalid rating or a response time under 300 ms or over
  3,000 ms, and sessions lacking both responses to both probe types.

## Papers cited here

Miller, Weidemann and Kahana (2012, recall termination; the first 80 subjects of Experiment 1); Lohnas, Polyn
and Kahana (2015, Experiment 3); Weidemann and Kahana (2016, recognition); Healey, Long and Kahana (2019,
contiguity); Kahana et al. (2024, the overview). The wiki lists every paper that used these data [W].
