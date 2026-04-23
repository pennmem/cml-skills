#!/usr/bin/env python3
"""
Refined build of three CML decks applying the beamer-from-papers skill's
critique rules:

  * Title slide: title/authors/affiliation/date only (no data-source line).
  * No em-dashes anywhere.
  * No inline comma-lists in sentences; use bullets or numbered-inline lists.
  * Max 2 figures per slide; same-type grouping only; always centered;
    width + height + keepaspectratio to prevent overflow; 2-3 summary bullets
    on every figure slide.
  * Conclusions + Next Steps frames at the end of every deck (before acks).
  * Madrid theme kept (metropolis not assumed-installed on rhino2).

Emits both a talk PDF and a notes-only PDF per deck.
"""

import shutil
import subprocess
from pathlib import Path

ROOT = Path("/home1/zrentala/beamer-workshop")
LOCAL_PAPERS = Path("/home1/zrentala/github_migration/work/papers")
REFINED_DIR = ROOT / "refined"

# --------------------------------------------------------------------------
# Shared preamble and helpers
# --------------------------------------------------------------------------

PREAMBLE = r"""\documentclass[aspectratio=169,11pt]{beamer}
\usetheme{Madrid}
\usecolortheme{default}
\definecolor{cmlblue}{RGB}{28, 53, 115}
\setbeamercolor{structure}{fg=cmlblue}
\setbeamercolor{palette primary}{bg=cmlblue, fg=white}
\setbeamercolor{palette secondary}{bg=cmlblue!80, fg=white}
\setbeamercolor{palette tertiary}{bg=cmlblue!60, fg=white}
\usepackage[T1]{fontenc}
\usepackage[utf8]{inputenc}
\usepackage{amsmath, amssymb}
\usepackage{graphicx}
\usepackage{setspace}
\usepackage{hyperref}
\hypersetup{colorlinks=true, linkcolor=cmlblue, urlcolor=cmlblue, citecolor=cmlblue!70}
\setstretch{0.97}
\setbeameroption{hide notes}
"""

def title_block(title, short_title, author, subtitle):
    sub = f"\\subtitle{{{subtitle}}}" if subtitle else ""
    return rf"""{PREAMBLE}
\title[{short_title}]{{{title}}}
{sub}
\author[CML]{{{author}}}
\institute[Penn CML]{{Computational Memory Lab \\ University of Pennsylvania}}
\date{{\today}}

\begin{{document}}

\begin{{frame}}[plain]\titlepage\end{{frame}}

\begin{{frame}}{{Outline}}\tableofcontents\end{{frame}}
"""

DOC_END = r"\end{document}"

# Standard figure sizing macros applied consistently.
SOLO_FIG_OPTS = r"width=0.80\textwidth, height=0.65\textheight, keepaspectratio"
DUAL_FIG_OPTS = r"width=\linewidth, height=0.58\textheight, keepaspectratio"


# --------------------------------------------------------------------------
# Deck 1 — Aggarwal & Kahana (2016) memory variability
# --------------------------------------------------------------------------

AG_FIGS = {
    "dotplot":  "dotplotVarActual.pdf",
    "betadist": "BetaDist.pdf",
    "rsqhist":  "hist_rsq.pdf",
    "as_pred":  "predictSummaryAS.pdf",
    "ws_pred":  "predictSummaryWS.pdf",
    "rewet":    "rewet.pdf",
}


def deck_aggarwal():
    head = title_block(
        title="Accounting for Variability in Human Memory",
        short_title="Memory Variability",
        author="Aggarwal \\& Kahana (2016)",
        subtitle="What exogenous factors explain, and what they leave over",
    )
    body = r"""
\section{The variability puzzle}

\begin{frame}{Memory varies across minutes, lists, and days}
  \begin{itemize}
    \setlength\itemsep{3pt}
    \item A single person's recall performance changes from list to list and session to session, even under near-constant conditions.
    \item Field consensus: most short-term variation reflects uncontrolled exogenous variables.
    \item Candidate exogenous variables:
      \begin{itemize}
        \item word frequency, concreteness, emotional valence
        \item practice, fatigue, alertness, time of day, sleep
      \end{itemize}
    \item If we equate these, how much within-subject variability remains?
  \end{itemize}
  \note{
    Open with the phenomenology: anyone running multi-session memory
    experiments has seen subjects swing 20 percentage points in recall
    from one day to the next. The field's implicit assumption has been
    that uncontrolled environmental variables carry most of this
    variance. Aggarwal and Kahana test that assumption directly: a
    tightly controlled 24-session design with every plausible exogenous
    predictor in a regression model. The question is whether the model
    accounts for most of the variance, which would support the
    environment account, or whether a large residual remains, which
    would support an endogenous-state account. The answer is the latter
    and is the paper's main contribution.
  }
\end{frame}

\begin{frame}{Why the answer matters}
  \begin{itemize}
    \setlength\itemsep{3pt}
    \item Practical: if external factors dominate, memory interventions should target environment and scheduling.
    \item Theoretical: if a large residual remains, models of memory must account for endogenous fluctuations in core encoding and retrieval mechanisms.
    \item Either way, the residual structure is diagnostic of where the machinery fluctuates.
  \end{itemize}
  \note{
    Set up the two horns of the dilemma before showing results.
    Audiences tend to have a prior about whether memory variability
    is mostly environmental or mostly internal; the paper moves the
    needle toward internal. Frame that as a theoretical commitment
    with consequences for how retrieved-context models are
    parameterized, not just a methodological finding.
  }
\end{frame}

\section{Design}

\begin{frame}{A 24-session PEERS delayed free recall experiment}
  \begin{itemize}
    \setlength\itemsep{3pt}
    \item 50 younger adults, ages 17 to 30, right-handed native English speakers.
    \item 24 sessions per subject across multiple days.
    \item Per session: 24 lists of 24 words, each list followed by a 24-second distractor-filled delay and a free-recall test.
    \item 576 trials per subject, nearly 29{,}000 list-level observations total.
    \item Sessions 1 to 23 reshuffle a fixed 576-word pool; Session 24 introduces new words to probe prior-list intrusions.
  \end{itemize}
  \note{
    The scale is the design's principal asset. Nearly 29,000 list-level
    observations give the within-subject regressions enormous power
    to detect small effects. Twenty-three sessions on the same word
    pool eliminates item-novelty confounds; Session 24 swaps in new
    words so prior-list intrusions are measurable. Every subject
    received the full 24 sessions.
  }
\end{frame}

\begin{frame}{Environment controlled, exogenous variables regressed}
  \begin{columns}[T]
    \column{0.5\textwidth}
      \textbf{Controlled by protocol}
      \begin{itemize}
        \item Soundproof room, constant light and temperature
        \item No phones or devices
        \item Standardized instructions and encoding task
        \item Distractor-filled delay suppresses rehearsal
      \end{itemize}
    \column{0.5\textwidth}
      \textbf{Regression predictors}
      \begin{itemize}
        \item Across-session: session number, sleep, alertness, start time, day of week
        \item Within-session: list number, block number, word frequency, valence, concreteness, prior-list recall
      \end{itemize}
  \end{columns}
  \note{
    The within-session predictor list is exhaustive of what plausibly
    varies list-to-list once the environment is fixed. Every
    short-term factor a reviewer would ask about is in the model.
    If the model's R-squared is low, the residual cannot be blamed
    on an omitted variable from the short list of obvious
    candidates. That sets up the punchline.
  }
\end{frame}

\section{How variable is performance}

\begin{frame}{Performance varies across sessions and across lists}
  \centering
  \includegraphics[""" + SOLO_FIG_OPTS + r"""]{figures/""" + AG_FIGS["dotplot"] + r"""}
  \begin{itemize}
    \setlength\itemsep{2pt}
    \item Panel A: 24 session-level recall proportions per subject; spread remains large after many sessions.
    \item Panel B: rank-ordered list-level spread within a session, averaged across sessions.
  \end{itemize}
  \note{
    Walk Panel A first. Each row is one subject; horizontal spread
    is how variable that subject was across the 24 sessions. Many
    subjects show 20 to 30 percentage-point swings, and the grey
    line marks each subject's median. Then Panel B: within a single
    session, the difference between a subject's best list and worst
    list is typically 0.40 to 0.60 recall probability. That is the
    within-session variability we want to explain.
  }
\end{frame}

\begin{frame}{Block-level recall trajectory}
  \centering
  \includegraphics[""" + SOLO_FIG_OPTS + r"""]{figures/""" + AG_FIGS["rewet"] + r"""}
  \begin{itemize}
    \setlength\itemsep{2pt}
    \item General downward drift within a session, consistent with fatigue or practice decrement.
    \item Eight-list block structure produces small resets at block boundaries.
  \end{itemize}
  \note{
    Performance trends downward across the 24-list session but with
    small spikes at each 8-list block boundary where subjects had
    the option of a short break. Effect is small and captured by
    the block-number predictor in the regression. The spikes are
    not the story; the broad downward drift is.
  }
\end{frame}

\section{What the exogenous predictors buy}

\begin{frame}{Regression coefficients}
  \centering
  \includegraphics[""" + SOLO_FIG_OPTS + r"""]{figures/""" + AG_FIGS["betadist"] + r"""}
  \begin{itemize}
    \setlength\itemsep{2pt}
    \item Across-session: only day of week reaches significance (negative beta, earlier in week = better recall).
    \item Within-session: only list number, block number, and list-average word frequency survive.
  \end{itemize}
  \note{
    Distributions of per-subject beta coefficients for each predictor.
    Black dots are significant at p less than 0.05. The story: sleep,
    alertness, start time, emotional valence, and concreteness are
    all null. Day of week is small but reliable and probably reflects
    weekly habits rather than memory per se. List number and block
    number capture the fatigue drift. Word frequency is the only
    item-level predictor.
  }
\end{frame}

\begin{frame}{How much variance the models capture}
  \centering
  \includegraphics[""" + SOLO_FIG_OPTS + r"""]{figures/""" + AG_FIGS["rsqhist"] + r"""}
  \begin{itemize}
    \setlength\itemsep{2pt}
    \item Across-session mean R-squared about 0.39.
    \item Within-session mean R-squared about 0.10.
    \item List-level performance is essentially unexplained by these predictors.
  \end{itemize}
  \note{
    R-squared histograms across the 50 per-subject regression models.
    Across-session: the predictors account for roughly 40 percent of
    the variance, which is substantial. Within-session: they account
    for roughly 10 percent. The latter number is the paper's load-
    bearing result. Even with every plausible list-level predictor
    in the model, 90 percent of within-session variability remains
    unaccounted for.
  }
\end{frame}

\section{What the residual looks like}

\begin{frame}{Session-level residual variability}
  \centering
  \includegraphics[""" + SOLO_FIG_OPTS + r"""]{figures/""" + AG_FIGS["as_pred"] + r"""}
  \begin{itemize}
    \setlength\itemsep{2pt}
    \item Panel A: raw across-session recall range per subject.
    \item Panel B: same range after regressing out predictors; visible but modest reduction.
  \end{itemize}
  \note{
    Before and after the regression model is applied. If the model
    captured the true sources of session-to-session variability, the
    dots in Panel B would collapse tightly around zero. They shrink
    a little (mean range 0.31 to 0.25) but the structure persists.
    Across-session variability is partially tamed by exogenous
    predictors, consistent with the 0.39 R-squared.
  }
\end{frame}

\begin{frame}{List-level residual variability}
  \centering
  \includegraphics[""" + SOLO_FIG_OPTS + r"""]{figures/""" + AG_FIGS["ws_pred"] + r"""}
  \begin{itemize}
    \setlength\itemsep{2pt}
    \item Pre vs.\ post residual ranges are nearly identical (0.557 then 0.543).
    \item Prediction model does not meaningfully reduce list-level spread.
  \end{itemize}
  \note{
    List-level residuals. The model barely moves the distribution.
    Mean list range pre: 0.557. Post: 0.543. The variability that
    looked tractable in principle is, in practice, untouched by the
    predictors. This is the visual form of the 0.10 R-squared.
  }
\end{frame}

\begin{frame}{Residuals are structured, not noise}
  \begin{itemize}
    \setlength\itemsep{3pt}
    \item Lag-1 autocorrelation of list-level residuals is significantly positive (mean beta 0.192, p less than 0.05).
    \item Good lists beget good lists; bad lists beget bad lists.
    \item Unexplained variability is a slowly-drifting endogenous process, not memoryless noise.
  \end{itemize}
  \note{
    The residual is not random. After regressing out predictors, a
    list's residual is reliably predicted by the residual of the
    immediately previous list. This is direct evidence for an
    endogenous state that drifts more slowly than a single list.
    Theoretically it points toward CMR parameters that fluctuate
    across trials, not just across subjects: attention-related
    primacy scaling, retrieval drift rate, accumulator noise,
    post-retrieval threshold.
  }
\end{frame}

\section{Conclusions}

\begin{frame}{Conclusions}
  \begin{itemize}
    \setlength\itemsep{3pt}
    \item Exogenous factors explain only about 10 percent of within-session memory variability.
    \item Across-session variability is better explained (R-squared about 0.39) but still leaves most spread in place.
    \item Residual variability is autocorrelated and therefore reflects a structured endogenous state.
    \item Models of recall need parameters that drift between lists, not just between individuals.
  \end{itemize}
  \note{
    Punchline: in one of the most controlled free-recall datasets
    ever collected, environmental explanations fail to account for
    the bulk of the fluctuation. The residual is structured, which
    means theory should take endogenous state seriously as a source
    of memory behavior.
  }
\end{frame}

\begin{frame}{Next steps}
  \begin{itemize}
    \setlength\itemsep{3pt}
    \item Search for neural correlates of the endogenous state using the PEERS EEG data.
    \item Fit trial-level CMR parameters; ask which parameters carry the residual autocorrelation.
    \item Relate the endogenous state to physiological signals (pupil, spectral tilt).
    \item Exploit the lag-1 autocorrelation to forecast list-level performance from the previous list.
  \end{itemize}
  \note{
    The paper functions as a problem statement for the lab's
    electrophysiology program. The residuals are real and
    structured; the follow-up work is to localize them in neural
    signals and in model parameters.
  }
\end{frame}

\begin{frame}{Acknowledgments}
  \begin{itemize}
    \item 50 PEERS participants
    \item Computational Memory Lab, Penn Psychology
    \item NIH grant MH55687 and NSF grant 1058886
  \end{itemize}
\end{frame}
"""
    return head + body + DOC_END


# --------------------------------------------------------------------------
# Deck 2 — Cohen & Kahana (2019) memory-based theory of emotional disorders
# --------------------------------------------------------------------------

CK_FIGS = {
    "model":      "Fig1_model_schematic.pdf",
    "fits":       "Fig2_FitComparisons.pdf",
    "clustering": "Fig3_EValClustering.pdf",
    "sameval":    "Fig4A_SameVal_Error.pdf",
    "oppval":     "Fig4B_OppVal_Error.pdf",
    "statedep":   "Fig5.pdf",
    "stressfreq": "Fig6_StressorFrequency_emotplot_indiv.pdf",
    "stressfreq2":"Fig7.pdf",
    "repstress":  "Fig8.pdf",
    "intrusion":  "Fig9_intrusion_histogram.pdf",
    "intrusive":  "Fig10_composite_IntrusiveRecollection.pdf",
    "vividness":  "Fig11A_Vividness.pdf",
    "nowness":    "Fig11B_Nowness.pdf",
    "imaginal":   "Fig12_emot_imaginalexp_indiv29.pdf",
    "mood_iexp":  "Fig13_mood_ImaginalExposure.pdf",
}


def deck_cohen_kahana():
    head = title_block(
        title="A Memory-Based Theory of Emotional Disorders",
        short_title="CMR3 \\& Emotional Disorders",
        author="Cohen \\& Kahana (2019)",
        subtitle="Nine simulations of affective dysregulation in retrieved-context memory",
    )
    body = r"""
\section{Motivation}

\begin{frame}{A memory problem inside a clinical problem}
  \begin{itemize}
    \setlength\itemsep{3pt}
    \item Depression and PTSD are commonly framed as disorders of affect.
    \item But their hallmark symptoms are memorial:
      \begin{itemize}
        \item rumination
        \item mood-congruent recall
        \item intrusive recollection
      \end{itemize}
    \item If the same retrieval mechanisms that explain healthy free recall also govern emotional material, clinical symptoms reduce to retrieval dynamics.
  \end{itemize}
  \note{
    Sell the ambition. The authors are replacing a menagerie of
    disorder-specific constructs with a single cognitive architecture.
    The claim is not metaphorical: they commit to explicit parameters
    and simulate each phenomenon end-to-end. Emphasize that the
    framing is unusual in clinical theory, which typically treats
    memory symptoms as downstream of mood or inhibition deficits.
  }
\end{frame}

\begin{frame}{Phenomena the theory must explain}
  \begin{itemize}
    \setlength\itemsep{3pt}
    \item Emotional clustering effect in free recall.
    \item Mood-congruent and state-dependent recall.
    \item Rumination following repeated stressors.
    \item Intrusive recollection in PTSD.
    \item Vividness and sense of ``nowness'' of traumatic memories.
    \item Therapy-induced attenuation (behavioral activation, prolonged exposure, imaginal exposure, emotion regulation).
  \end{itemize}
  \note{
    Signal the scope. Nine simulations span from healthy-population
    emotional clustering to patient-level behavior and to the
    computational action of specific psychotherapies. The force of
    the paper is coverage rather than any single fit.
  }
\end{frame}

\section{Model: CMR3}

\begin{frame}{CMR3: adding an emotional-valence sub-region to context}
  \centering
  \includegraphics[""" + SOLO_FIG_OPTS + r"""]{figures/""" + CK_FIGS["model"] + r"""}
  \begin{itemize}
    \setlength\itemsep{2pt}
    \item Context layer augmented with a valence sub-region (positive, negative, neutral).
    \item Items associate with and retrieve emotional context through the same $M^{FC}$ and $M^{CF}$ matrices that carry temporal context.
  \end{itemize}
  \note{
    Point to the emotional sub-region in the schematic. The critical
    design claim is minimalist: the retrieval rule does not change.
    Only the feature space grows. Pre-experimental emotional
    associations scale with each word's normed valence (from the Warriner
    norms). This is the smallest architectural change compatible with
    modeling emotional content.
  }
\end{frame}

\begin{frame}{Fits to the emotional clustering effect (Exp.\ 1)}
  \centering
  \includegraphics[""" + SOLO_FIG_OPTS + r"""]{figures/""" + CK_FIGS["fits"] + r"""}
  \begin{itemize}
    \setlength\itemsep{2pt}
    \item Transition probabilities between same-valence pairs, reproduced with fewer parameters than eCMR.
    \item Fit does not require an arousal mechanism.
  \end{itemize}
  \note{
    Walk the comparison. CMR3 matches the transition probabilities
    between same-valence word pairs across recall positions. eCMR can
    also fit these data but requires an additional arousal mechanism
    that CMR3 does not. The point is parsimony: adding one feature
    dimension to context is enough to explain emotional clustering,
    without a separate arousal module.
  }
\end{frame}

\section{Clustering, mood, and state-dependence}

\begin{frame}{Emotional clustering by valence}
  \centering
  \includegraphics[""" + SOLO_FIG_OPTS + r"""]{figures/""" + CK_FIGS["clustering"] + r"""}
  \begin{itemize}
    \setlength\itemsep{2pt}
    \item Same-valence transitions (positive to positive, negative to negative) exceed opposite-valence transitions.
    \item Falls out of a shared emotional-context retrieval cue.
  \end{itemize}
  \note{
    This is the direct clustering result. During recall, having just
    produced a negative word biases retrieval toward the next
    negative word because emotional context drifts slowly during
    recall and the cue remains negatively tinted. The effect is
    symmetric across positive and negative valence, which rules out
    simple attention-to-negative-items accounts.
  }
\end{frame}

\begin{frame}{Same-valence vs.\ opposite-valence error distributions}
  \begin{columns}[T]
    \column{0.48\textwidth}
      \centering
      \includegraphics[""" + DUAL_FIG_OPTS + r"""]{figures/""" + CK_FIGS["sameval"] + r"""}\\
      {\footnotesize Same-valence errors}
    \column{0.48\textwidth}
      \centering
      \includegraphics[""" + DUAL_FIG_OPTS + r"""]{figures/""" + CK_FIGS["oppval"] + r"""}\\
      {\footnotesize Opposite-valence errors}
  \end{columns}
  \vspace{4pt}
  \begin{itemize}
    \setlength\itemsep{2pt}
    \item Symmetric error patterns across same vs.\ opposite valence.
    \item Model has no free parameter to shape the two distributions independently.
  \end{itemize}
  \note{
    Strong test of the account: the model has no degree of freedom
    that moves same-valence and opposite-valence error distributions
    independently, yet the patterns match. Same-type grouping (both
    panels are error-rate distributions) justifies the side-by-side.
  }
\end{frame}

\begin{frame}{Mood-congruent and state-dependent recall}
  \centering
  \includegraphics[""" + SOLO_FIG_OPTS + r"""]{figures/""" + CK_FIGS["statedep"] + r"""}
  \begin{itemize}
    \setlength\itemsep{2pt}
    \item Recall is enhanced when encoding and retrieval share a mood state.
    \item Asymmetric cost when mood at encoding differs from mood at test.
  \end{itemize}
  \note{
    Classic mood-congruent and state-dependent effects fall out
    naturally. When emotional context at test matches the emotional
    context at encoding, the cue similarity is high and retrieval
    succeeds. The asymmetric dissociation (larger deficit when
    negative encoding is tested in a positive state than vice versa)
    also replicates.
  }
\end{frame}

\section{Depression simulations (Sims 4-5)}

\begin{frame}{Frequent stressors: a model analogue of depression}
  \centering
  \includegraphics[""" + SOLO_FIG_OPTS + r"""]{figures/""" + CK_FIGS["stressfreq"] + r"""}
  \begin{itemize}
    \setlength\itemsep{2pt}
    \item Repeated negative events bias emotional context toward negative valence.
    \item Negative context persistently cues further negative retrievals, producing sustained low mood.
  \end{itemize}
  \note{
    Depression is not a separate module. It emerges as an equilibrium
    of the same retrieval dynamics: stressors bias context toward
    negative valence, and the negative context acts as a retrieval
    cue for past negative experiences, reinforcing itself. No mood-
    regulation module is required.
  }
\end{frame}

\begin{frame}{Stressor frequency and repetition effects}
  \begin{columns}[T]
    \column{0.48\textwidth}
      \centering
      \includegraphics[""" + DUAL_FIG_OPTS + r"""]{figures/""" + CK_FIGS["stressfreq2"] + r"""}\\
      {\footnotesize Stressor frequency}
    \column{0.48\textwidth}
      \centering
      \includegraphics[""" + DUAL_FIG_OPTS + r"""]{figures/""" + CK_FIGS["repstress"] + r"""}\\
      {\footnotesize Repeated stressors}
  \end{columns}
  \vspace{4pt}
  \begin{itemize}
    \setlength\itemsep{2pt}
    \item Stressor frequency sculpts the mood distribution.
    \item Repeated stressors extend the emotional-context bias over time.
  \end{itemize}
  \note{
    Two matched plots of emotional-context drift under different
    stressor schedules. Behavioral activation therapy is simulated as
    a scheduled positive-event schedule, which shifts the context
    distribution back toward neutrality and breaks the self-cueing
    loop. The model gives a computational account of why scheduling
    positive activities works even when subjective mood is initially
    unaffected.
  }
\end{frame}

\section{PTSD simulations (Sims 6-9)}

\begin{frame}{Intrusive recollection as a successful retrieval on biased cues}
  \centering
  \includegraphics[""" + SOLO_FIG_OPTS + r"""]{figures/""" + CK_FIGS["intrusion"] + r"""}
  \begin{itemize}
    \setlength\itemsep{2pt}
    \item Trauma memories acquire abnormally strong emotional-context associations.
    \item Everyday cues exceed retrieval threshold; intrusions are successful retrievals under a biased cue, not inhibition failures.
  \end{itemize}
  \note{
    Reframe intrusions. In classic clinical accounts, intrusions
    reflect a failure to suppress unwanted memories. In CMR3 they
    reflect normal retrieval operating on a context that has become
    overly sticky for the trauma memory. The distinction matters for
    treatment: the intervention should retrain the context binding,
    not strengthen a suppression mechanism.
  }
\end{frame}

\begin{frame}{Intrusive recollection: composite dynamics}
  \centering
  \includegraphics[""" + SOLO_FIG_OPTS + r"""]{figures/""" + CK_FIGS["intrusive"] + r"""}
  \begin{itemize}
    \setlength\itemsep{2pt}
    \item Intrusion frequency, latency distribution, and cue-similarity sensitivity reproduced with one parameter set.
    \item Matches aggregate clinical measures without disorder-specific tuning.
  \end{itemize}
  \note{
    The composite figure aggregates several PTSD measures against
    model predictions. Speak to each measure briefly. The point is
    joint fit, not any single curve: the same parameter vector that
    yields realistic intrusion frequency also yields realistic
    latency distribution and cue-similarity sensitivity.
  }
\end{frame}

\begin{frame}{Vividness and ``nowness'' of traumatic memories}
  \begin{columns}[T]
    \column{0.48\textwidth}
      \centering
      \includegraphics[""" + DUAL_FIG_OPTS + r"""]{figures/""" + CK_FIGS["vividness"] + r"""}\\
      {\footnotesize Vividness}
    \column{0.48\textwidth}
      \centering
      \includegraphics[""" + DUAL_FIG_OPTS + r"""]{figures/""" + CK_FIGS["nowness"] + r"""}\\
      {\footnotesize Nowness}
  \end{columns}
  \vspace{4pt}
  \begin{itemize}
    \setlength\itemsep{2pt}
    \item Vividness and ``nowness'' scale with similarity of retrieved context to current context.
    \item For trauma memories this similarity is abnormally high.
  \end{itemize}
  \note{
    Both are density plots over context-similarity values, so they
    belong side-by-side. Subjective vividness and the feeling that
    the event is happening now are not separate phenomena in the
    model; both are monotone functions of retrieved-to-current
    context similarity. The clinical literature has treated them as
    related symptoms without a common mechanism.
  }
\end{frame}

\begin{frame}{Imaginal exposure: emotional trajectory}
  \centering
  \includegraphics[""" + SOLO_FIG_OPTS + r"""]{figures/""" + CK_FIGS["imaginal"] + r"""}
  \begin{itemize}
    \setlength\itemsep{2pt}
    \item Repeated retrieval under a safe context rebinds the trauma item's emotional context.
    \item Attenuates the self-cueing loop that produces intrusions.
  \end{itemize}
  \note{
    Imaginal exposure asks the patient to retrieve the trauma
    memory under safe, controlled conditions. In the model this is
    re-encoding the trauma item with a different emotional context,
    which competes with the original trauma context during future
    retrieval. The intrusion rate drops over sessions.
  }
\end{frame}

\begin{frame}{Mood dynamics during imaginal exposure}
  \centering
  \includegraphics[""" + SOLO_FIG_OPTS + r"""]{figures/""" + CK_FIGS["mood_iexp"] + r"""}
  \begin{itemize}
    \setlength\itemsep{2pt}
    \item Mood deteriorates within an exposure session and recovers across sessions.
    \item Cross-session trajectory matches published PE therapy trajectories.
  \end{itemize}
  \note{
    Characteristic within-session worsening followed by between-
    session recovery is reproduced without any additional
    mood-regulation module. The within-session pattern reflects
    activation of negative context during retrieval; the between-
    session pattern reflects accumulated re-binding of the trauma
    item to safer contexts.
  }
\end{frame}

\section{Conclusions}

\begin{frame}{Conclusions}
  \begin{itemize}
    \setlength\itemsep{3pt}
    \item One retrieval architecture produces nine affective phenomena with a single parameter set.
    \item Symptoms that look qualitatively different reduce to retrieval dynamics on a valence-biased context.
    \item Therapies gain a computational description as context-update operations.
    \item The clinical memory literature is unified with the healthy-memory literature under a common formalism.
  \end{itemize}
  \note{
    End on the unifying claim. The paper's contribution is not any
    single simulation but the demonstration that a broad clinical
    phenomenology is internally generated by an unchanged retrieval
    model once the feature space carries valence.
  }
\end{frame}

\begin{frame}{Next steps}
  \begin{itemize}
    \setlength\itemsep{3pt}
    \item Link CMR3 parameters to neural variables (amygdala-hippocampal coupling, vmPFC regulation).
    \item Use the model to predict individual treatment response from short behavioral tasks.
    \item Extend to anxiety disorders (panic, generalized anxiety, social anxiety).
    \item Connect trial-level endogenous fluctuations (cf.\ Aggarwal \& Kahana, 2016) to the emotional context drift rate.
  \end{itemize}
  \note{
    Foreshadow extensions. The neural mapping is the largest open
    question; a behavioral predictor of treatment response would
    have the biggest clinical impact.
  }
\end{frame}

\begin{frame}{Acknowledgments}
  \begin{itemize}
    \item Rivka Cohen, lead author and simulation developer.
    \item Lynn Lohnas, Sean Polyn, Per Sederberg (CMR lineage).
    \item Christoph Weidemann (methodological contributions).
    \item Computational Memory Lab, University of Pennsylvania.
    \item Funding: see original publication.
  \end{itemize}
\end{frame}
"""
    return head + body + DOC_END


# --------------------------------------------------------------------------
# Deck 3 — Healey & Kahana (2016) four-component aging
# --------------------------------------------------------------------------

HE_FIGS = {
    "quantex":     "f1.pdf",
    "summary":     "f2.pdf",
    "cmr":         "f3.pdf",
    "adh":         "f6.pdf",
    "idh":         "f7.pdf",
    "csh":         "f8.pdf",
    "combo":       "f11.pdf",
    "fourcomp":    "f14.pdf",
    "paramdiffs":  "f16.pdf",
    "recognition": "f21.pdf",
    "fa_corr":     "f22.pdf",
}


def deck_healey():
    head = title_block(
        title="A Four-Component Model of Age-Related Memory Change",
        short_title="Four-Component Aging Model",
        author="Healey \\& Kahana (2016)",
        subtitle="Fitting CMR2 to older adults reveals which four mechanisms decline and which do not",
    )
    body = r"""
\section{The aging puzzle}

\begin{frame}{Spared and impaired memory with age}
  \begin{itemize}
    \setlength\itemsep{3pt}
    \item Age-related deficits follow a gradient:
      \begin{itemize}
        \item free recall, large and robust
        \item cued recall, moderate
        \item recognition, modest
      \end{itemize}
    \item Within free recall, some measures are stable (probability of first recall, recency) and others are impaired (serial position curve, lag-CRP, intrusion rates).
    \item Existing theories fit isolated effects; none captures the full pattern with a single parameter set.
  \end{itemize}
  \note{
    Set up the theory-comparison game. The pattern is multivariate:
    a theory can be right about any one measure and still fail the
    package. That is the paper's methodological complaint against
    existing qualitative theories. A useful theory of cognitive
    aging must predict which effects are spared and which are
    impaired simultaneously.
  }
\end{frame}

\begin{frame}{A single parameter must explain the whole pattern}
  \centering
  \includegraphics[""" + SOLO_FIG_OPTS + r"""]{figures/""" + HE_FIGS["quantex"] + r"""}
  \begin{itemize}
    \setlength\itemsep{2pt}
    \item If ``reduced resources'' means a parameter $d$, both recall and recognition are functions of $d$.
    \item The theory passes only if a single $d$ hits both observed values simultaneously.
  \end{itemize}
  \note{
    Figure makes the methodological point concrete. Two hypothetical
    functions relate the impairment parameter $d$ to recall and
    recognition accuracy. Panel A: a single value of $d$ hits both
    curves. Panel B: no single value does. Qualitative predictions
    cannot distinguish A from B; quantitative simultaneous fits
    can.
  }
\end{frame}

\section{Benchmarks}

\begin{frame}{Five benchmark measures from Kahana et al.\ (2002)}
  \centering
  \includegraphics[""" + SOLO_FIG_OPTS + r"""]{figures/""" + HE_FIGS["summary"] + r"""}
  \begin{itemize}
    \setlength\itemsep{2pt}
    \item Older adults match younger adults on PFR and PLI recency.
    \item Older adults diverge on serial position, lag-CRP contiguity, and intrusion rates.
  \end{itemize}
  \note{
    Five-panel summary. Panel A: serial position curves, older below
    younger but same shape. Panel B: PFR curves are essentially
    identical; both groups initiate recall with the final item.
    Panel C: lag-CRP shows older adults make fewer close-neighbor
    transitions, a contiguity deficit. Panel D: older adults produce
    more PLIs and ELIs. Panel E: PLI recency is preserved in both
    groups. These five effects are the benchmark.
  }
\end{frame}

\section{Retrieved-context framework}

\begin{frame}{CMR2 in one figure}
  \centering
  \includegraphics[""" + SOLO_FIG_OPTS + r"""]{figures/""" + HE_FIGS["cmr"] + r"""}
  \begin{itemize}
    \setlength\itemsep{2pt}
    \item Feature layer and context layer connected by $M^{FC}$ and $M^{CF}$.
    \item Continuous across lists; produces prior-list intrusions without auxiliary machinery.
  \end{itemize}
  \note{
    CMR2 is the retrieved-context model used as the healthy baseline.
    Context drifts via beta-enc and beta-rec. Primacy arises from
    the attention parameters phi-s and phi-d. Post-retrieval
    monitoring compares retrieved context to current context
    against a threshold c-thresh. The aging theories below will
    implicate subsets of these parameters.
  }
\end{frame}

\section{Candidate theories as CMR2 lesions}

\begin{frame}{Three theories, each implemented as a lesion}
  \begin{itemize}
    \setlength\itemsep{3pt}
    \item Associative Deficit Hypothesis (Naveh-Benjamin, 2000): reduce $\gamma_{FC}$, $\gamma_{CF}$.
    \item Inhibitory Deficit Hypothesis (Hasher \& Zacks, 1988): raise lateral inhibition, slow context drift.
    \item Cognitive Slowing Hypothesis (Salthouse, 1996): increase accumulator iteration time.
    \item Strategy: fit CMR2 to younger adults; lesion; ask whether the lesioned model simulates older adults.
  \end{itemize}
  \note{
    The three leading qualitative theories get mapped onto concrete
    model parameters. Each lesion is tuned so that the lesioned
    model matches older adults on one effect, then the remaining
    effects are checked under that same parameter setting. This is
    the quantitative simultaneity test.
  }
\end{frame}

\begin{frame}{ADH lesion: associative deficit}
  \centering
  \includegraphics[""" + SOLO_FIG_OPTS + r"""]{figures/""" + HE_FIGS["adh"] + r"""}
  \begin{itemize}
    \setlength\itemsep{2pt}
    \item Captures associative-task deficits.
    \item Under-predicts the contiguity deficit; over-predicts the overall SPC drop.
  \end{itemize}
  \note{
    Row shows the ADH fit across the five benchmark panels. It does
    well on the effects most directly tied to binding but fails to
    match lag-CRP asymmetry and produces too large a global SPC
    deficit. Net: insufficient.
  }
\end{frame}

\begin{frame}{IDH lesion: inhibitory deficit}
  \centering
  \includegraphics[""" + SOLO_FIG_OPTS + r"""]{figures/""" + HE_FIGS["idh"] + r"""}
  \begin{itemize}
    \setlength\itemsep{2pt}
    \item Matches intrusion rates and PLI recency.
    \item Fails lag-CRP asymmetry; produces too steep a primacy gradient.
  \end{itemize}
  \note{
    The IDH lesion does well on what it is designed for
    (interference control and intrusions) but misses the contiguity
    and primacy shape. Again insufficient as a complete account.
  }
\end{frame}

\begin{frame}{CSH lesion: cognitive slowing}
  \centering
  \includegraphics[""" + SOLO_FIG_OPTS + r"""]{figures/""" + HE_FIGS["csh"] + r"""}
  \begin{itemize}
    \setlength\itemsep{2pt}
    \item Produces global accuracy drops.
    \item Does not differentiate SPC from contiguity or intrusion effects.
  \end{itemize}
  \note{
    CSH lowers overall accuracy but does not produce the selective
    pattern of spared versus impaired effects. The impairment is
    too uniform across measures.
  }
\end{frame}

\begin{frame}{Even a combination of the three theories fails}
  \centering
  \includegraphics[""" + SOLO_FIG_OPTS + r"""]{figures/""" + HE_FIGS["combo"] + r"""}
  \begin{itemize}
    \setlength\itemsep{2pt}
    \item Residual misfits remain on PLI recency and lag-CRP asymmetry.
    \item The benchmark pattern requires impairments none of these three theories isolates.
  \end{itemize}
  \note{
    Combining ADH, IDH, and CSH lesions does not yield the pattern
    either. The residual misfits are systematic: the combination
    still cannot simultaneously reproduce PLI recency and lag-CRP
    asymmetry. This motivates the data-driven approach on the next
    slide.
  }
\end{frame}

\section{The four-component theory}

\begin{frame}{Fit CMR2 per participant; compare parameter distributions}
  \begin{itemize}
    \setlength\itemsep{3pt}
    \item Let all parameters vary; fit CMR2 to each younger and older participant individually with a genetic algorithm.
    \item Ask which parameters show reliable age-group differences.
    \item Lock the rest; name the surviving parameters as the aging signature.
  \end{itemize}
  \note{
    Methodological pivot. Rather than hypothesizing which parameter
    differs, let the data reveal which ones do. The cost is
    exploration; the reward is an empirically grounded set of
    age-differentiated parameters that carries joint constraints.
  }
\end{frame}

\begin{frame}{Parameter differences with age}
  \centering
  \includegraphics[""" + SOLO_FIG_OPTS + r"""]{figures/""" + HE_FIGS["paramdiffs"] + r"""}
  \begin{itemize}
    \setlength\itemsep{2pt}
    \item Four parameters differ reliably: $\phi_s$, $\beta_{rec}$, $c_{thresh}$, accumulator noise $\eta$.
    \item The remaining parameters are statistically indistinguishable between groups.
  \end{itemize}
  \note{
    Point to each of the four distributions. $\phi_s$ controls
    primacy scaling and tracks sustained encoding attention.
    $\beta_{rec}$ is the context-retrieval drift rate. $c_{thresh}$
    is the post-retrieval monitoring threshold. Accumulator noise
    $\eta$ controls retrieval signal-to-noise. All other parameters
    overlap between older and younger groups.
  }
\end{frame}

\begin{frame}{The four components}
  \begin{enumerate}
    \setlength\itemsep{4pt}
    \item Sustained attention across encoding ($\phi_s$, primacy gradient).
    \item Contextual retrieval ($\beta_{rec}$).
    \item Post-retrieval monitoring ($c_{thresh}$).
    \item Retrieval noise ($\eta$).
  \end{enumerate}
  \note{
    Name each component. These are neither arbitrary nor purely
    statistical. Each has a construct analogue: attention, temporal
    binding, source monitoring, signal-to-noise. The theory thus
    refines rather than replaces the qualitative literature.
  }
\end{frame}

\begin{frame}{Simultaneous fit to all benchmarks}
  \centering
  \includegraphics[""" + SOLO_FIG_OPTS + r"""]{figures/""" + HE_FIGS["fourcomp"] + r"""}
  \begin{itemize}
    \setlength\itemsep{2pt}
    \item One parameter vector now captures SPC, PFR, lag-CRP, intrusions, and PLI recency together.
    \item Contrast with prior panels where at least one curve always missed.
  \end{itemize}
  \note{
    The four-component model matches all five benchmark panels
    under a single parameter setting. This is the simultaneity
    test the single-theory lesions failed. Direct visual comparison
    with the ADH, IDH, CSH panels is the point.
  }
\end{frame}

\section{Cross-task prediction: recognition}

\begin{frame}{Recognition via context comparison, no new parameters}
  \begin{itemize}
    \setlength\itemsep{3pt}
    \item Probe item retrieves its encoding context through $M^{FC}$.
    \item Respond ``old'' if similarity between retrieved and current context exceeds $c_{thresh}$.
    \item Four-component aging differences carry over without re-fitting.
  \end{itemize}
  \note{
    Recognition is modeled with the same post-retrieval monitoring
    mechanism used to screen intrusions in free recall. No new
    parameters are fit; the four-component age differences transfer
    directly. This is an out-of-sample test of the theory.
  }
\end{frame}

\begin{frame}{Predicted age differences in hit and false-alarm rates}
  \centering
  \includegraphics[""" + SOLO_FIG_OPTS + r"""]{figures/""" + HE_FIGS["recognition"] + r"""}
  \begin{itemize}
    \setlength\itemsep{2pt}
    \item Modest hit-rate drop, larger false-alarm rise in older adults.
    \item Predicted accuracy deficit smaller than free-recall deficit, matching the empirical gradient.
  \end{itemize}
  \note{
    Hit rates drop modestly in older adults; false alarms rise more
    substantially; overall recognition accuracy deficit is smaller
    than the free-recall deficit. All three qualitative patterns
    are produced by the free-recall-fit parameters without any
    re-fitting.
  }
\end{frame}

\begin{frame}{Individual-difference prediction}
  \centering
  \includegraphics[""" + SOLO_FIG_OPTS + r"""]{figures/""" + HE_FIGS["fa_corr"] + r"""}
  \begin{itemize}
    \setlength\itemsep{2pt}
    \item Free-recall intrusion rate correlates with recognition false-alarm rate across subjects.
    \item Direct consequence of sharing $c_{thresh}$ across tasks.
  \end{itemize}
  \note{
    The correlation is a model-derived prediction. Individuals with
    lower post-retrieval thresholds produce more intrusions in free
    recall AND more false alarms in recognition; hence the cross-
    task positive correlation. The data support it.
  }
\end{frame}

\section{Conclusions}

\begin{frame}{Conclusions}
  \begin{itemize}
    \setlength\itemsep{3pt}
    \item Age differences in free recall require impairments in four CMR2 mechanisms, not one.
    \item The ``resources'' construct breaks apart into sustained attention, contextual retrieval, post-retrieval monitoring, and retrieval noise.
    \item A single parameter vector explains both free recall and recognition, including individual-difference correlations.
    \item Aging theories should be evaluated against multivariate cross-task benchmarks, not isolated effects.
  \end{itemize}
  \note{
    Final claims in order. The methodological lesson (multivariate
    evaluation) is as important as the substantive theory; the
    authors push the field to adopt stricter testing standards.
  }
\end{frame}

\begin{frame}{Next steps}
  \begin{itemize}
    \setlength\itemsep{3pt}
    \item Map each of the four components onto distinct neural correlates (hippocampus, PFC, frontoparietal network).
    \item Ask whether trial-level fluctuations in the same parameters explain the residuals in Aggarwal \& Kahana (2016).
    \item Extend to emotional material (cf.\ Cohen \& Kahana, 2019): do older adults' positivity effects reflect altered $c_{thresh}$ on emotional valence?
    \item Develop interventions that target each component individually.
  \end{itemize}
  \note{
    The neural mapping is the most immediate follow-up. The other
    three threads connect the aging work to the lab's other
    programs (variability, emotional memory, translation to
    interventions).
  }
\end{frame}

\begin{frame}{Acknowledgments}
  \begin{itemize}
    \item K.\ Healey, lead author.
    \item Kahana Lab, PEERS older-adult sample.
    \item NIH MH55687, NSF 1058886.
  \end{itemize}
\end{frame}
"""
    return head + body + DOC_END


# --------------------------------------------------------------------------
# Figure copy helpers
# --------------------------------------------------------------------------

def copy_ck(paper_root: Path, dest: Path):
    src = paper_root / "Figs"
    for fig in CK_FIGS.values():
        shutil.copy(src / fig, dest / fig)


def copy_ag(paper_root: Path, dest: Path):
    src = paper_root / "Figures"
    for fig in AG_FIGS.values():
        shutil.copy(src / fig, dest / fig)


def copy_he(paper_root: Path, dest: Path):
    src = paper_root / "PsychRevSubmission" / "accepted_version" / "latex_to_submit" / "figures"
    for pdf_name in HE_FIGS.values():
        eps = src / pdf_name.replace(".pdf", ".eps")
        out_pdf = dest / pdf_name
        if out_pdf.exists():
            continue
        subprocess.run(
            ["epstopdf", str(eps), "--outfile=" + str(out_pdf)],
            check=True, capture_output=True,
        )


# --------------------------------------------------------------------------
# Compile + notes PDF
# --------------------------------------------------------------------------

def compile_both(deck_dir: Path, tex_source: str) -> None:
    """Write deck.tex + deck_notes.tex, compile both."""
    (deck_dir / "deck.tex").write_text(tex_source)
    notes_src = tex_source.replace(
        r"\setbeameroption{hide notes}",
        r"\setbeameroption{show only notes}",
    )
    (deck_dir / "deck_notes.tex").write_text(notes_src)

    for tex_name in ("deck.tex", "deck_notes.tex"):
        for _ in range(2):
            subprocess.run(
                ["pdflatex", "-interaction=nonstopmode", "-halt-on-error", tex_name],
                cwd=deck_dir, capture_output=True, text=True,
            )


def build(paper_key: str):
    paper_root = {
        "CohenKahana2019": LOCAL_PAPERS / "CohenKahana2019",
        "AGGA16memvar":    LOCAL_PAPERS / "AGGA16memvar",
        "Heal15agingcmr":  LOCAL_PAPERS / "Heal15agingcmr",
    }[paper_key]

    deck_dir = REFINED_DIR / paper_key
    fig_dir = deck_dir / "figures"
    fig_dir.mkdir(parents=True, exist_ok=True)

    if paper_key == "CohenKahana2019":
        copy_ck(paper_root, fig_dir)
        tex = deck_cohen_kahana()
    elif paper_key == "AGGA16memvar":
        copy_ag(paper_root, fig_dir)
        tex = deck_aggarwal()
    elif paper_key == "Heal15agingcmr":
        copy_he(paper_root, fig_dir)
        tex = deck_healey()
    else:
        raise ValueError(paper_key)

    compile_both(deck_dir, tex)

    pdf = deck_dir / "deck.pdf"
    notes = deck_dir / "deck_notes.pdf"
    ok = pdf.exists() and notes.exists()
    status = "OK" if ok else "FAIL"
    print(f"[{status}] {paper_key}  talk={pdf.exists()} notes={notes.exists()}")


def main():
    REFINED_DIR.mkdir(parents=True, exist_ok=True)
    for paper in ["CohenKahana2019", "AGGA16memvar", "Heal15agingcmr"]:
        build(paper)


if __name__ == "__main__":
    main()
