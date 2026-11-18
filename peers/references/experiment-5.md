# PEERS Experiment 5 (task `VFFR`): reading aloud, then recall after days

The lab also calls this experiment VFFR, ltpFR2.5 or ltpFR2b [W]. The lab's methods files use the name "PEERS
Experiment 5" for a different study, ltpFR3 (auditory and visual lists of 12 or 24 words) [M]. That study is not
in the PEERS release; the published Experiment 5 is the one described here [P]. Source tags are defined in
`data.md`.

## Design

- Ten sessions. The words are the 576 of Experiment 4, reordered each session [P][D].
- **Read-aloud trials** (every session): 10 practice trials, then 576 trials in 24 blocks of 24, each block
  preceded by a countdown [P]. A word appears for 1,200-1,800 ms after a 1,000-1,600 ms blank. The subject waits
  at least 1 s after it disappears and then says it aloud; speaking sooner brings a "Too fast" message.
  Two-minute breaks follow blocks 8 and 16 [W; Katerman et al., 2022].
- **Recall after a long delay** (sessions 5-9 in the files): the session opens with ten minutes of free recall
  of the words from the earlier sessions, under externalized-recall instructions (say every word that comes to
  mind). The first of these tests is a surprise [P]. At least 16 hours separate sessions (Katerman et al., 2022).
- The purpose was to compare the EEG before a word recalled from days ago with the EEG before the same word
  read a second ago, with the same vocal response in both [P].

## What the loader returns

- `WORD` rows: one per read-aloud trial. `trial` 0-575, `list` (block) 1-24, `serialpos` 1-24, `too_fast`,
  and `recalled` = 1 if the subject said the word shown.
- `REC_WORD` rows: the spoken response on a trial. `rectime` is ms from the word's offset to speech onset.
- `FFR_REC_WORD` rows: the ten-minute recall. `rectime` is ms from its start, `intrusion` is 0 for one of the
  576 words and -1 otherwise, and `repeat` counts repetitions within the test.
- `has_ffr`, `session_complete` (576 trials).

## What the public files hold

- 57 subjects, 462 sessions; 30 subjects have all ten sessions and 45 reach a recall session (43, 42, 41, 40
  and 37 subjects in sessions 5 to 9) [D]. Ages 18-29 where given.
- Read-aloud accuracy is 98.2%. Speech begins 1.49 s after word offset on average (median 1.38 s), and 9.8% of
  trials were too fast [D].
- Words recalled in the ten minutes rise from 26 in the first test to 104 in the fifth (25 and 100 without
  repetitions); intrusions fall from 40% to 25% of responses [D]. Katerman et al. (2022), who excluded subjects
  with fewer than seven sessions or accuracy below 70%, report 29 and 103 words and 37% and 23%.
- Sixteen subjects had done Experiment 4, so some knew the words before the first session [D].

## Notes for analysis

- There are no study lists in the usual sense. Serial position, lag-CRP and prior-list intrusions do not apply
  to the read-aloud trials, and `peers.to_pybeh` is not meant for this experiment.
- A response outside the 576 is not necessarily a new word: the ten practice words of each session have
  `item_num` -1 and count as intrusions here.
- Inter-response times in the ten-minute recall rise steeply toward the last response, as in list recall
  (Katerman et al., 2022, Figure 1E).
