# PEERS Experiment 4 (task `ltpFR2`): delayed free recall

Source tags ([P] paper, [M] lab methods files, [W] wiki, [D] checked in the public files) are defined in
`data.md`.

## Design

- 24 sessions, each with 24 lists of 24 words: 576 words a session [P][D].
- Every list is followed by 24 s of arithmetic (A + B + C = ?) and then 75 s of spoken recall [P]. There is no
  encoding task, no final free recall and no recognition test.
- **Pre-list distractor.** Twelve of the 24 lists in every complete session are also preceded by 24 s of
  arithmetic [D]. The paper says the first list was excluded from this manipulation [P]; in the public files
  list 1 is preceded by arithmetic in 48% of sessions [D]. Loader column: `pre_distractor`.
- Trial sequence [M]: a 10-s countdown that the subject may pause, the pre-list arithmetic if any, a 1,500-ms
  fixation, then the words. Each word stays for 1,600 ms with 800-1,200 ms between words, so onsets are 2.6 s
  apart [D]. A row of asterisks (500 ms) marks the start of recall.
- A break of about five minutes follows every eighth list [P].
- **Words.** A 576-word subset of the 1,638-word pool of Experiments 1-3, the same for every subject. Sessions
  0-22 present all 576, reordered each session [P][D]. Sixteen of each list's 24 words are pairs chosen by
  word-association-space similarity and eight are unconstrained [M].
- **Session 23** (the 24th) mixes the old words with 288 new ones, also the same for every subject: eight lists
  have 8 old words, eight have 12 and eight have 16 [M][D]. Loader column: `novel`. Leave session 23 out of
  anything that pools sessions, as Kahana, Aggarwal and Phan (2018) did (23 sessions, 552 lists).

## What the public files hold

- 127 subjects and 2,469 sessions; 83 subjects have 24 complete sessions and 84 have sessions 0-22 complete.
  The paper reports 98 completers [P]. Ages 17-30 where given; 35 subjects have no age [D].
- 41 of the subjects had already done Experiments 1-3 [D]. Healey, Long and Kahana (2019) compared such
  practiced subjects with naive ones.
- Recall probability is .48 on average (SD .19 across subjects) and does not depend on the pre-list distractor
  (.479 without, .480 with) [D]. Subjects make 12.5 responses per list [D].
- `peers.load_math(4)` gives every arithmetic problem, labeled `pre_list` or `post_list`, with accuracy 95.5% [D].

## Analyses done on these data

- Variability across lists and sessions: Kahana, Aggarwal and Phan (2018), 79 subjects, 23 sessions (552
  lists). Recall on the previous list strongly predicts recall on the current one.
- Contiguity in recall order and in inter-response times for 24-word delayed recall: Healey, Long and Kahana
  (2019, Figure 1).
- Word and list predictors of recall: Aka, Phan and Kahana (2021), 98 subjects, 23 sessions.
- For an analysis of subjects who saw the same words throughout, take those with sessions 0-22 present (86
  subjects) or complete (84) [D].
