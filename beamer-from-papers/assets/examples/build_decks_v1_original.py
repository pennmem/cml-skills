#!/usr/bin/env python3
"""
Generate 4 Beamer decks (CohenKahana2019, AGGA16memvar, Heal15agingcmr, synthesis)
twice: once with figures pulled from local prepared-paper mirrors
and once with figures pulled from GitHub clones of pennmem/paper-*.

Compiles each deck to PDF (+ notes PDF). Does not persist bundles.
"""

import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path("/home1/zrentala/beamer-workshop")
LOCAL_PAPERS = Path("/home1/zrentala/github_migration/work/papers")
GITHUB_PAPERS = Path("/tmp/pennmem-clones")

SOURCES = {
    "local": {
        "label": "Prepared local mirror",
        "ck": LOCAL_PAPERS / "CohenKahana2019",
        "ag": LOCAL_PAPERS / "AGGA16memvar",
        "he": LOCAL_PAPERS / "Heal15agingcmr",
    },
    "github": {
        "label": "pennmem GitHub org",
        "ck": GITHUB_PAPERS / "paper-CohenKahana2019",
        "ag": GITHUB_PAPERS / "paper-AGGA16memvar",
        "he": GITHUB_PAPERS / "paper-Heal15agingcmr",
    },
}

# ------------------------------------------------------------------
# Preamble and common utilities
# ------------------------------------------------------------------

PREAMBLE = r"""\documentclass[aspectratio=169]{beamer}
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
\usepackage{hyperref}
\hypersetup{colorlinks=true, linkcolor=cmlblue, urlcolor=cmlblue, citecolor=cmlblue!70}
\setbeameroption{hide notes}
"""

def title_block(title, short_title, author, subtitle, source_label):
    subtitle_line = f"\\subtitle{{{subtitle}}}" if subtitle else ""
    return rf"""{PREAMBLE}
\title[{short_title}]{{{title}}}
{subtitle_line}
\author[CML]{{{author}}}
\institute[Penn CML]{{Computational Memory Lab \\ University of Pennsylvania \\ {{\small Data source: {source_label}}}}}
\date{{\today}}

\begin{{document}}

\begin{{frame}}[plain]\titlepage\end{{frame}}

\begin{{frame}}{{Outline}}\tableofcontents\end{{frame}}
"""

def doc_end():
    return r"\end{document}"


# ------------------------------------------------------------------
# Deck 1 — Cohen & Kahana (2019)
# ------------------------------------------------------------------

CK_FIGS = {
    "model":       "Fig1_model_schematic.pdf",
    "fits":        "Fig2_FitComparisons.pdf",
    "clustering":  "Fig3_EValClustering.pdf",
    "sameval":     "Fig4A_SameVal_Error.pdf",
    "oppval":      "Fig4B_OppVal_Error.pdf",
    "statedep":    "Fig5.pdf",
    "stressfreq":  "Fig6_StressorFrequency_emotplot_indiv.pdf",
    "stressfreq2": "Fig7.pdf",
    "repstress":   "Fig8.pdf",
    "intrusion":   "Fig9_intrusion_histogram.pdf",
    "intrusive":   "Fig10_composite_IntrusiveRecollection.pdf",
    "vividness":   "Fig11A_Vividness.pdf",
    "nowness":     "Fig11B_Nowness.pdf",
    "imaginal":    "Fig12_emot_imaginalexp_indiv29.pdf",
    "mood_iexp":   "Fig13_mood_ImaginalExposure.pdf",
}


def deck_cohen_kahana(source_label):
    head = title_block(
        title="A Memory-Based Theory of Emotional Disorders",
        short_title="CMR3 \\& Emotional Disorders",
        author="Cohen \\& Kahana (2019) \\\\ \\emph{Psychological Review}",
        subtitle="Nine simulations of affective dysregulation in retrieved-context memory",
        source_label=source_label,
    )

    body = r"""
\section{Motivation}

\begin{frame}{A memory problem hiding inside a clinical problem}
  \begin{itemize}
    \item Depression and PTSD are often framed as disorders of affect regulation, but
          their hallmark symptoms are \emph{memorial}: rumination, mood-congruent
          recall, intrusive recollection.
    \item If the same retrieval mechanisms that explain healthy free recall also
          govern how emotional material is remembered, clinical symptoms fall out of
          the dynamics of a single cognitive system.
    \item \textbf{Thesis:} A retrieved-context account of episodic memory, extended
          with an emotional-valence feature of context, produces the full
          phenomenology of depression and PTSD without new machinery.
  \end{itemize}
  \note{Sell the ambition of the paper. Emphasize that the authors are replacing
        a menagerie of disorder-specific constructs with one cognitive architecture.}
\end{frame}

\begin{frame}{Empirical phenomena the theory must explain}
  \begin{columns}
    \column{0.55\textwidth}
      \begin{itemize}
        \item Emotional clustering effect (same-valence transitions)
        \item Mood-congruent recall
        \item Emotional state--dependent recall
        \item Rumination / repetitive negative recall after stressors
        \item Intrusive recollection in PTSD
        \item Therapy-induced attenuation (behavioral activation, exposure)
        \item Vividness and ``nowness'' of traumatic memories
      \end{itemize}
    \column{0.45\textwidth}
      \begin{itemize}
        \item 1 experiment (emotional clustering)
        \item 9 simulations spanning affective phenomena from healthy populations
              to patient-level behavior
      \end{itemize}
  \end{columns}
  \note{Signal the scale. Nine simulations is unusual; the paper's force comes
        from the coverage, not any single fit.}
\end{frame}

\section{Model: CMR3}

\begin{frame}{CMR3: adding emotional valence to context}
  \begin{columns}
    \column{0.55\textwidth}
      \includegraphics[width=\textwidth]{figures/""" + CK_FIGS["model"] + r"""}
    \column{0.45\textwidth}
      \begin{itemize}
        \item Builds on CMR2 (Lohnas et al., 2015)
        \item Context layer augmented with an \emph{emotional} sub-region whose
              features code valence (positive / negative / neutral)
        \item Items associate with and retrieve emotional context via the same
              $M^{FC}$, $M^{CF}$ machinery that carries temporal and source context
        \item Pre-experimental emotional associations scale with each word's
              normed valence
      \end{itemize}
  \end{columns}
  \note{Point at the emotional sub-region. Emphasize that nothing in the retrieval
        rule changes; only the feature space grows.}
\end{frame}

\begin{frame}{Fits to the Exp.\ 1 emotional clustering effect}
  \includegraphics[width=0.85\textwidth]{figures/""" + CK_FIGS["fits"] + r"""}
  \note{Transition probabilities between same-valence pairs. CMR3 captures the
        effect with fewer free parameters than competing accounts; eCMR does too
        but only after adding an arousal mechanism that the data do not require.}
\end{frame}

\section{Sim.\ 1--3: Affective clustering and state-dependence}

\begin{frame}{Emotional clustering by valence}
  \includegraphics[width=0.75\textwidth]{figures/""" + CK_FIGS["clustering"] + r"""}
  \note{Same-valence transitions (positive-to-positive, negative-to-negative)
        exceed opposite-valence transitions. Falls out of shared emotional
        context without a valence-specific clustering mechanism.}
\end{frame}

\begin{frame}{Same- vs opposite-valence errors}
  \begin{columns}
    \column{0.5\textwidth}
      \includegraphics[width=\textwidth]{figures/""" + CK_FIGS["sameval"] + r"""}
    \column{0.5\textwidth}
      \includegraphics[width=\textwidth]{figures/""" + CK_FIGS["oppval"] + r"""}
  \end{columns}
  \note{Symmetry of the clustering effect under same- vs opposite-valence errors.
        A strong test: the model has no free knob to swap these distributions
        independently.}
\end{frame}

\begin{frame}{Mood-congruent and state-dependent recall}
  \includegraphics[width=0.65\textwidth]{figures/""" + CK_FIGS["statedep"] + r"""}
  \note{When encoding and retrieval share a mood state, recall is enhanced.
        Dissociating mood at encoding vs test produces the well-known asymmetric
        costs.}
\end{frame}

\section{Sim.\ 4--5: Depression}

\begin{frame}{Frequent stressors: model analogue of depression}
  \begin{columns}
    \column{0.55\textwidth}
      \includegraphics[width=\textwidth]{figures/""" + CK_FIGS["stressfreq"] + r"""}
    \column{0.45\textwidth}
      \begin{itemize}
        \item Repeated negative events bias emotional context toward negative
              valence
        \item Negative contextual bias persistently cues further negative
              retrievals
        \item Produces sustained low-mood drift without an explicit mood-regulation
              module
      \end{itemize}
  \end{columns}
  \note{The stressor simulations are where the clinical claims live. Make clear
        that ``depression'' here is the model's persistent negative context, not
        a separate construct.}
\end{frame}

\begin{frame}{Cumulative effects and behavioral activation}
  \begin{columns}
    \column{0.5\textwidth}
      \includegraphics[width=\textwidth]{figures/""" + CK_FIGS["stressfreq2"] + r"""}
    \column{0.5\textwidth}
      \includegraphics[width=\textwidth]{figures/""" + CK_FIGS["repstress"] + r"""}
  \end{columns}
  \note{Left: stressor frequency sculpts the mood distribution. Right: repeated
        stressors extend the emotional bias. Behavioral-activation therapy is
        implemented as scheduled positive events, which shift emotional context
        back toward neutrality.}
\end{frame}

\section{Sim.\ 6--9: PTSD and exposure therapies}

\begin{frame}{Intrusive recollection as misclassified context}
  \begin{columns}
    \column{0.6\textwidth}
      \includegraphics[width=\textwidth]{figures/""" + CK_FIGS["intrusion"] + r"""}
    \column{0.4\textwidth}
      \begin{itemize}
        \item Trauma memories acquire unusually strong emotional-context
              associations
        \item Weak cues from everyday context partially overlap with the trauma
              context and exceed retrieval threshold
        \item Intrusions are not failures of inhibition --- they are successful
              retrievals under a biased cue
      \end{itemize}
  \end{columns}
  \note{Reframe intrusions: they are the model's normal retrieval rule operating
        on an unusually sticky context. This is the conceptual move of the PTSD
        simulations.}
\end{frame}

\begin{frame}{Intrusive recollection: composite dynamics}
  \includegraphics[width=0.78\textwidth]{figures/""" + CK_FIGS["intrusive"] + r"""}
  \note{Intrusion frequency, latency distribution, and sensitivity to cue
        similarity reproduced under a single parameter setting. Figure shows the
        aggregate match across these measures.}
\end{frame}

\begin{frame}{Vividness and ``nowness''}
  \begin{columns}
    \column{0.5\textwidth}
      \includegraphics[width=\textwidth]{figures/""" + CK_FIGS["vividness"] + r"""}
    \column{0.5\textwidth}
      \includegraphics[width=\textwidth]{figures/""" + CK_FIGS["nowness"] + r"""}
  \end{columns}
  \note{Vividness and the subjective sense of ``nowness'' scale with the
        similarity between retrieved and current context; for trauma memories
        that similarity is abnormally high.}
\end{frame}

\begin{frame}{Imaginal exposure and emotion regulation}
  \begin{columns}
    \column{0.5\textwidth}
      \includegraphics[width=\textwidth]{figures/""" + CK_FIGS["imaginal"] + r"""}
    \column{0.5\textwidth}
      \includegraphics[width=\textwidth]{figures/""" + CK_FIGS["mood_iexp"] + r"""}
  \end{columns}
  \note{Imaginal exposure and reappraisal both act by updating the emotional
        context associated with the trauma item, weakening the cue--retrieval
        loop that produces intrusions. Prolonged exposure is simulated similarly.}
\end{frame}

\section{Discussion}

\begin{frame}{What the coverage buys}
  \begin{itemize}
    \item A single architecture produces nine affective phenomena with one set of
          parameters, without disorder-specific modules.
    \item Symptoms that look qualitatively different (rumination, intrusions,
          mood-congruence) all reduce to the same retrieval dynamics on a
          valence-biased context.
    \item Therapy mechanisms have a computational home: they are context-update
          operations, not mood repairs.
  \end{itemize}
  \note{End on the unifying claim. Audience question they'll ask: what breaks
        this account? Preview: arousal effects, individual differences in
        attentional bias, neural implementation.}
\end{frame}

\begin{frame}{Open directions}
  \begin{itemize}
    \item Link CMR3 parameters to neural variables (e.g., amygdala--hippocampal
          coupling, vmPFC regulation)
    \item Use the model to predict individual treatment response from behavioral
          tasks
    \item Extend to arousal and anxiety disorders (panic, GAD, social anxiety)
    \item Relate endogenous-state fluctuations (cf.\ Aggarwal \& Kahana, 2016) to
          the emotional-context drift rate
  \end{itemize}
  \note{Foreshadow the synthesis talk: the same context mechanism that explains
        emotional disorders also features in variability and aging talks.}
\end{frame}

\begin{frame}{Acknowledgments}
  \begin{itemize}
    \item Rivka Cohen (lead author; all simulation code)
    \item Lynn Lohnas, Sean Polyn, Per Sederberg (CMR lineage)
    \item Christoph Weidemann (methodological contributions)
    \item Computational Memory Lab, University of Pennsylvania
    \item Funding: NIH / NSF (see original publication)
  \end{itemize}
\end{frame}
"""
    return head + body + doc_end()


# ------------------------------------------------------------------
# Deck 2 — Aggarwal & Kahana (2016) memvar
# ------------------------------------------------------------------

AG_FIGS = {
    "dotplot":   "dotplotVarActual.pdf",
    "betadist":  "BetaDist.pdf",
    "rsqhist":   "hist_rsq.pdf",
    "as_pred":   "predictSummaryAS.pdf",
    "ws_pred":   "predictSummaryWS.pdf",
    "rewet":     "rewet.pdf",
}


def deck_aggarwal(source_label):
    head = title_block(
        title="Accounting for Variability in Human Memory Using Exogenous Factors",
        short_title="Memory Variability",
        author="Aggarwal \\& Kahana (2016)",
        subtitle="A 24-session PEERS study of what exogenous variables can and cannot explain",
        source_label=source_label,
    )

    body = r"""
\section{The variability puzzle}

\begin{frame}{Memory is variable even under near-constant conditions}
  \begin{itemize}
    \item It is long established that a single person's recall performance
          fluctuates strikingly from hour to hour, list to list, session to
          session.
    \item Usual explanations: uncontrolled exogenous factors --- word frequency,
          concreteness, emotional valence, fatigue, time of day, sleep.
    \item \textbf{Question:} if we equate or statistically control all of these,
          how much short-term variability remains?
  \end{itemize}
  \note{Frame as a methodological--theoretical test: the field has tacitly
        assumed exogenous factors explain most fluctuation. This paper puts that
        assumption on the line.}
\end{frame}

\begin{frame}{Two stakes for the answer}
  \begin{itemize}
    \item \emph{Practical:} If exogenous factors dominate, memory interventions
          should target environment and scheduling.
    \item \emph{Theoretical:} If a large residual remains, then models of memory
          must account for endogenous-state fluctuations in core encoding and
          retrieval mechanisms --- variability is a feature of the system, not
          noise from outside.
  \end{itemize}
  \note{End of motivation. Next section: the experiment.}
\end{frame}

\section{Design}

\begin{frame}{A 24-session PEERS delayed free recall experiment}
  \begin{itemize}
    \item $N = 50$ younger adults (ages 17--30), right-handed, native English
          speakers
    \item 24 sessions per subject across multiple days
    \item Each session: 24 lists of 24 words with a 24-second distractor-filled
          delay before free recall
    \item $24 \times 24 = 576$ trials per subject
    \item Subjects 1--23: same 576-word pool reshuffled; Session 24: new words
          introduced to probe prior-list intrusions
  \end{itemize}
  \note{The scale is the design's main asset. 28{,}800 list-level observations
        across 50 subjects give the regressions power.}
\end{frame}

\begin{frame}{Controlled environment, candidate exogenous variables}
  \begin{columns}
    \column{0.5\textwidth}
      \textbf{Controlled by the protocol}
      \begin{itemize}
        \item Soundproof room, constant light and temperature
        \item No phones / devices
        \item Standardized instructions and encoding task
        \item Distractor-filled delay (reduces rehearsal)
      \end{itemize}
    \column{0.5\textwidth}
      \textbf{Candidate predictors}
      \begin{itemize}
        \item Across-session: session number, sleep the prior night,
              self-rated alertness, start time, day of week
        \item Within-session: list number, block number, list-average word
              frequency, valence, concreteness, prior-list recall
      \end{itemize}
  \end{columns}
  \note{Emphasize that the within-session predictor list is exhaustive of what
        plausibly varies list-to-list once environment is fixed.}
\end{frame}

\section{The variability itself}

\begin{frame}{Performance varies day-to-day and list-to-list}
  \includegraphics[width=0.72\textwidth]{figures/""" + AG_FIGS["dotplot"] + r"""}
  \note{Panel A: subject-level variation across the 24 sessions. Panel B:
        rank-ordered list variability within a session, averaged across
        sessions. Both reveal substantial spread even after 20+ sessions of
        practice.}
\end{frame}

\begin{frame}{Block-level trajectory}
  \includegraphics[width=0.6\textwidth]{figures/""" + AG_FIGS["rewet"] + r"""}
  \note{Average recall probability by list, across subjects. A general downward
        drift within a session with spikes at the start of each 8-list block
        (older-adult breaks in the full PEERS protocol landed here).}
\end{frame}

\section{What do exogenous variables buy us?}

\begin{frame}{Regression coefficients: few significant}
  \includegraphics[width=0.72\textwidth]{figures/""" + AG_FIGS["betadist"] + r"""}
  \note{Distribution of $\beta$ coefficients across subjects for each predictor.
        Across-session: only day-of-week reaches significance. Within-session:
        only list number, block number, and list-average word frequency.
        Sleep, alertness, start time, valence, concreteness all non-significant.}
\end{frame}

\begin{frame}{How much variance do the models capture?}
  \includegraphics[width=0.72\textwidth]{figures/""" + AG_FIGS["rsqhist"] + r"""}
  \note{Across-session $R^2 \approx 0.39$; within-session $R^2 \approx 0.10$.
        Within-session performance is almost entirely unexplained by the
        exogenous predictors.}
\end{frame}

\begin{frame}{Residual variability, session level}
  \includegraphics[width=0.78\textwidth]{figures/""" + AG_FIGS["as_pred"] + r"""}
  \note{Panel A: actual session-level recall range. Panel B: same range after
        regressing out the predictors. Reduction is visible but small.}
\end{frame}

\begin{frame}{Residual variability, list level}
  \includegraphics[width=0.78\textwidth]{figures/""" + AG_FIGS["ws_pred"] + r"""}
  \note{List-level picture is starker --- the prediction model barely shrinks
        the within-subject spread. Mean list range pre: 0.557; post: 0.543.
        Essentially untouched.}
\end{frame}

\begin{frame}{Autocorrelation in the residuals}
  \begin{itemize}
    \item Lag-1 autocorrelation of list-level residuals is significantly positive
          ($\bar\beta = 0.192$, $p < 0.05$).
    \item Unexplained variability is \emph{not} memoryless noise --- good lists
          beget good lists.
    \item Suggests a slowly-drifting endogenous process modulating encoding /
          retrieval efficacy.
  \end{itemize}
  \note{This is the paper's cleanest positive finding: the residuals have
        structure. An endogenous-state account predicts exactly that.}
\end{frame}

\section{Discussion}

\begin{frame}{What this rules out, and what it implies}
  \begin{itemize}
    \item Exogenous-factor accounts of short-term memory variability are
          insufficient --- list-to-list fluctuation is largely untouched by the
          obvious controllable variables.
    \item A meaningful fraction of memory performance reflects endogenous state
          dynamics of the memory system itself.
    \item Models of recall need parameters that drift between sessions and
          between lists, not just between individuals.
  \end{itemize}
  \note{Segue naturally to Healey \& Kahana --- which of CMR's parameters could
        plausibly drift? $\beta_{enc}$, $\phi_s$, retrieval noise $\eta$, and
        post-retrieval threshold $c_{thresh}$ are prime candidates.}
\end{frame}

\begin{frame}{Future directions}
  \begin{itemize}
    \item Search for neural correlates of the endogenous state (EEG from PEERS)
    \item Relate trial-level CMR parameters to physiological arousal, pupil,
          and scalp spectral markers
    \item Exploit the lag-1 autocorrelation to predict list-level performance
          from immediately preceding trials
  \end{itemize}
  \note{This paper is really a problem statement the lab's later
        electrophysiology studies try to answer.}
\end{frame}

\begin{frame}{Acknowledgments}
  \begin{itemize}
    \item 50 PEERS participants
    \item Computational Memory Lab; Penn Psychology
    \item Funded by NIH grant MH55687 and NSF grant 1058886
  \end{itemize}
\end{frame}
"""
    return head + body + doc_end()


# ------------------------------------------------------------------
# Deck 3 — Healey & Kahana (2016) four-component aging
# ------------------------------------------------------------------

HE_FIGS = {
    "quantex":     "f1.pdf",    # quant example
    "summary":     "f2.pdf",    # RDF summary
    "cmr":         "f3.pdf",    # CMR schematic
    "encoding":    "f4.pdf",
    "retrieval":   "f5.pdf",
    "adh":         "f6.pdf",
    "idh":         "f7.pdf",
    "csh":         "f8.pdf",
    "combo":       "f11.pdf",
    "fourcomp":    "f14.pdf",
    "primacy":     "f15.pdf",
    "paramdiffs":  "f16.pdf",
    "recognition": "f21.pdf",
    "fa_corr":     "f22.pdf",
}


def deck_healey(source_label):
    head = title_block(
        title="A Four-Component Model of Age-Related Memory Change",
        short_title="Four-Component Aging Model",
        author="Healey \\& Kahana (2016) \\\\ \\emph{Psychological Review}",
        subtitle="Fitting CMR2 to older adults tells us which four mechanisms decline --- and which do not",
        source_label=source_label,
    )

    body = r"""
\section{The aging puzzle}

\begin{frame}{A complex pattern of spared and impaired memory with age}
  \begin{itemize}
    \item Older adults show a \emph{gradient} of impairment: free recall $>$
          cued recall $>$ recognition.
    \item Within free recall, some measures are stable (PFR, recency, PLI
          recency) and others are impaired (overall SPC, lag-CRP, intrusion
          rates).
    \item Existing theories explain isolated effects; none account for the
          pattern with a single parameter set.
  \end{itemize}
  \note{Set up the theory-comparison game. The key move is that the pattern
        is multivariate: a theory can be right about any one measure and still
        fail the package.}
\end{frame}

\begin{frame}{Why a single parameter must explain the whole pattern}
  \includegraphics[width=0.65\textwidth]{figures/""" + HE_FIGS["quantex"] + r"""}
  \note{If reduced ``resources'' are parameter $d$, both recall and recognition
        are functions of $d$. Only when those functions intersect the observed
        values at the same $d$ does the theory survive. Qualitative fits are
        cheap; quantitative simultaneous fits are not.}
\end{frame}

\section{Benchmark effects}

\begin{frame}{Five benchmark measures from Kahana et al.\ (2002)}
  \includegraphics[width=0.82\textwidth]{figures/""" + HE_FIGS["summary"] + r"""}
  \note{SPC, PFR, lag-CRP, PLI+ELI rates, PLI recency. Black = older, grey =
        younger. Older adults match on recency initiation; diverge on contiguity
        and intrusion rates; lower SPC overall.}
\end{frame}

\section{Retrieved context background}

\begin{frame}{CMR2 in one figure}
  \includegraphics[width=0.55\textwidth]{figures/""" + HE_FIGS["cmr"] + r"""}
  \note{Feature layer $\leftrightarrow$ context layer, connected by $M^{FC}$ and
        $M^{CF}$. Continuous across lists, so it can produce PLIs naturally.
        Context drifts via $\beta_{enc}$, $\beta_{rec}$; primacy from $\phi_s,
        \phi_d$; post-retrieval threshold screens intrusions.}
\end{frame}

\begin{frame}{CMR2 encoding and retrieval}
  \begin{columns}
    \column{0.5\textwidth}
      \includegraphics[width=\textwidth]{figures/""" + HE_FIGS["encoding"] + r"""}
    \column{0.5\textwidth}
      \includegraphics[width=\textwidth]{figures/""" + HE_FIGS["retrieval"] + r"""}
  \end{columns}
  \note{Left: Hebbian learning between active feature and context nodes.
        Right: context-based cueing, accumulator competition, editing against
        the current state of context.}
\end{frame}

\section{Candidate theories, as lesions}

\begin{frame}{Three theories, each implemented as a CMR2 lesion}
  \begin{columns}
    \column{0.5\textwidth}
      \begin{itemize}
        \item \textbf{ADH} (Naveh-Benjamin, 2000): associative deficit
              $\to$ reduce $\gamma_{FC}$, $\gamma_{CF}$
        \item \textbf{IDH} (Hasher \& Zacks, 1988): inhibitory deficit
              $\to$ raise lateral-inhibition parameter, slow context drift
        \item \textbf{CSH} (Salthouse, 1996): cognitive slowing
              $\to$ increase accumulator time step
      \end{itemize}
    \column{0.5\textwidth}
      \begin{itemize}
        \item Start from CMR2 fit to younger data.
        \item Lesion the corresponding mechanism until one benchmark matches
              older adults.
        \item Ask: does the remainder of the pattern also match?
      \end{itemize}
  \end{columns}
  \note{The game is explicit: tune one knob to match one effect, check the
        other effects under that same knob setting. This is the quantitative
        simultaneity test.}
\end{frame}

\begin{frame}{ADH lesion}
  \includegraphics[width=0.78\textwidth]{figures/""" + HE_FIGS["adh"] + r"""}
  \note{ADH captures associative-task deficits but under-predicts contiguity
        deficit and over-predicts overall SPC impairment.}
\end{frame}

\begin{frame}{IDH lesion}
  \includegraphics[width=0.78\textwidth]{figures/""" + HE_FIGS["idh"] + r"""}
  \note{IDH does well on intrusions and PLIs but fails on lag-CRP asymmetry
        and produces too-steep primacy.}
\end{frame}

\begin{frame}{CSH lesion}
  \includegraphics[width=0.78\textwidth]{figures/""" + HE_FIGS["csh"] + r"""}
  \note{CSH produces global accuracy drops but doesn't differentiate SPC
        from contiguity or intrusion effects.}
\end{frame}

\begin{frame}{Even a combination fails}
  \includegraphics[width=0.78\textwidth]{figures/""" + HE_FIGS["combo"] + r"""}
  \note{Combining ADH+IDH+CSH lesions leaves residual misfits for the PLI
        recency and lag-CRP asymmetry. The conclusion: the pattern requires
        impairments that none of these theories isolate.}
\end{frame}

\section{Deriving the four-component theory}

\begin{frame}{Fit the full model to each participant; compare distributions}
  \begin{itemize}
    \item Allow all parameters to vary; fit CMR2 to each older and younger
          participant individually using a genetic algorithm.
    \item Ask which parameters show reliable older-vs-younger differences.
    \item Keep only those; lock the rest to healthy values.
  \end{itemize}
  \note{Methodological pivot: instead of predicting which knob to turn, let
        the data reveal which knobs differ. The cost is exploration; the
        reward is an empirically derived theory.}
\end{frame}

\begin{frame}{Parameter differences with age}
  \includegraphics[width=0.75\textwidth]{figures/""" + HE_FIGS["paramdiffs"] + r"""}
  \note{Four parameters reliably differ: $\phi_s$ (primacy / sustained
        encoding attention), $\beta_{rec}$ (context retrieval drift),
        $c_{thresh}$ (post-retrieval monitoring), and $\eta$ (retrieval noise).}
\end{frame}

\begin{frame}{The four components}
  \begin{enumerate}
    \item \textbf{Sustained attention across encoding} --- $\phi_s$ and primacy
          gradient
    \item \textbf{Contextual retrieval} --- $\beta_{rec}$: older adults retrieve
          context more sluggishly, attenuating lag-CRP contiguity
    \item \textbf{Post-retrieval monitoring} --- $c_{thresh}$: lower threshold
          admits more PLIs / ELIs
    \item \textbf{Retrieval noise} --- higher $\eta$ lowers overall accuracy
          without changing recency
  \end{enumerate}
  \note{These four mechanisms are neither arbitrarily chosen nor purely
        statistical --- they correspond to identifiable cognitive constructs
        and map cleanly onto existing constructs (attention, binding,
        monitoring, signal-to-noise).}
\end{frame}

\begin{frame}{Four-component simultaneous fit to all benchmarks}
  \includegraphics[width=0.82\textwidth]{figures/""" + HE_FIGS["fourcomp"] + r"""}
  \note{A single parameter vector now captures SPC, PFR, lag-CRP, intrusion
        rates, and PLI recency simultaneously. Compare to single-theory panels
        where at least one curve was always wrong.}
\end{frame}

\section{Cross-task prediction: recognition}

\begin{frame}{Extending CMR2 to item recognition}
  \begin{itemize}
    \item Recognition uses the \emph{same} post-retrieval monitoring mechanism:
          context retrieved by the probe is compared to current context; if
          similarity exceeds $c_{thresh}$, respond ``old.''
    \item No new parameters are fit; the four-component aging differences
          carry over.
  \end{itemize}
  \note{This is the paper's out-of-sample test. If the four-component theory
        is a real description of age-related memory change, a model locked to
        those parameters should also predict recognition accuracy deficits.}
\end{frame}

\begin{frame}{Model predicts age differences in hits and false alarms}
  \includegraphics[width=0.72\textwidth]{figures/""" + HE_FIGS["recognition"] + r"""}
  \note{Older adults: modest hit-rate drop, larger false-alarm rise, smaller
        overall accuracy deficit than free recall. Model matches without
        re-fitting.}
\end{frame}

\begin{frame}{Individual-difference prediction}
  \includegraphics[width=0.65\textwidth]{figures/""" + HE_FIGS["fa_corr"] + r"""}
  \note{Participants with higher free-recall intrusion rates also produce more
        recognition false alarms --- a cross-task correlation that falls out of
        sharing $c_{thresh}$ across the two tasks. A direct prediction of the
        four-component theory.}
\end{frame}

\section{Discussion}

\begin{frame}{What this changes}
  \begin{itemize}
    \item Aging theories should be evaluated against multivariate, cross-task
          benchmarks, not single effects.
    \item The ``resources'' construct breaks apart: at least four distinct
          mechanisms change with age, each with its own signature.
    \item Interventions can in principle target each separately --- sustained
          attention, context binding, monitoring, or retrieval signal-to-noise.
  \end{itemize}
  \note{Interventions are speculative here; the paper's contribution is to
        localize the impairment.}
\end{frame}

\begin{frame}{Open questions}
  \begin{itemize}
    \item Neural correlates of each of the four mechanisms (hippocampus, PFC,
          frontal-parietal)
    \item Trial-level fluctuations in the same four parameters --- do they
          explain the variability residuals of Aggarwal \& Kahana (2016)?
    \item Extensions to emotional material (cf.\ Cohen \& Kahana, 2019): does
          older adults' positivity effect reflect different $c_{thresh}$
          tuned on emotional valence?
  \end{itemize}
  \note{These are the three threads that make the synthesis talk interesting.}
\end{frame}

\begin{frame}{Acknowledgments}
  \begin{itemize}
    \item K.\ Healey (lead author)
    \item Kahana Lab, PEERS older-adult sample
    \item Funding: NIH MH55687, NSF 1058886
  \end{itemize}
\end{frame}
"""
    return head + body + doc_end()


# ------------------------------------------------------------------
# Deck 4 — Synthesis
# ------------------------------------------------------------------

def deck_synthesis(source_label):
    head = title_block(
        title="Endogenous Dynamics of Retrieved Context",
        short_title="Synthesis",
        author="Aggarwal, Cohen, Healey, \\& Kahana",
        subtitle="How three retrieved-context studies carve the same machine at different joints",
        source_label=source_label,
    )

    body = r"""
\section{A common machine}

\begin{frame}{One framework, three windows}
  \begin{itemize}
    \item All three papers work in the retrieved-context framework (CMR / CMR2 /
          CMR3).
    \item Each asks a different question about the \emph{parameters} of that
          machine:
      \begin{itemize}
        \item \textbf{Aggarwal \& Kahana (2016):} do the parameters fluctuate
              endogenously from one list to the next?
        \item \textbf{Healey \& Kahana (2016):} do they differ systematically
              between older and younger adults?
        \item \textbf{Cohen \& Kahana (2019):} can clinical syndromes be
              described as chronic biases in the emotional sub-region of
              context?
      \end{itemize}
  \end{itemize}
  \note{Set the frame: same architecture, different axes of variation.}
\end{frame}

\begin{frame}{The retrieved-context architecture in one slide}
  \begin{itemize}
    \item Items and context are two coupled layers; item$\to$context and
          context$\to$item associations live in $M^{FC}$ and $M^{CF}$.
    \item Encoding: a primacy-weighted Hebbian update links active features to
          slowly drifting context.
    \item Retrieval: current context cues a noisy accumulator competition;
          winning items are screened against context similarity.
    \item Knobs: $\beta_{enc}$, $\beta_{rec}$, $\phi_s$, $\phi_d$, $\gamma_{FC}$,
          $\gamma_{CF}$, $c_{thresh}$, accumulator noise $\eta$.
  \end{itemize}
  \note{Audience orientation before comparisons. Keep this tight; they have
        seen it in the individual-paper talks.}
\end{frame}

\section{Aggarwal: the variability residual}

\begin{frame}{What exogenous factors do not explain}
  \begin{itemize}
    \item 50 subjects, 576 trials each, nine plausible exogenous predictors.
    \item Within-session $R^2 \approx 0.10$ --- about 90\% of list-level
          variability remains.
    \item Lag-1 autocorrelation of residuals is significantly positive:
          unexplained variance is a slowly-drifting endogenous process.
  \end{itemize}
  \note{Take-away: the missing variance is structured. It looks like something.}
\end{frame}

\begin{frame}{Endogenous state in the architecture}
  \begin{itemize}
    \item Where could the drift live? Any CMR parameter that plausibly varies
          trial-to-trial:
      \begin{itemize}
        \item $\beta_{enc}$ --- context drift rate during study
        \item $\phi_s$ --- primacy gradient / attention
        \item accumulator noise $\eta$ --- signal-to-noise during retrieval
        \item $c_{thresh}$ --- readiness to commit a recall
      \end{itemize}
    \item Aggarwal \& Kahana offer a statistical lower bound; the architecture
          tells us where to look next.
  \end{itemize}
  \note{This is the hinge into Healey: those same parameters are exactly the
        four mechanisms that differ with age.}
\end{frame}

\section{Healey: the four-component signature}

\begin{frame}{Four parameters differ with age}
  \begin{enumerate}
    \item \textbf{Sustained attention} --- primacy scaling $\phi_s$
    \item \textbf{Contextual retrieval} --- $\beta_{rec}$
    \item \textbf{Post-retrieval monitoring} --- $c_{thresh}$
    \item \textbf{Retrieval noise} --- accumulator $\eta$
  \end{enumerate}
  \begin{itemize}
    \item Simultaneous fit to SPC, PFR, lag-CRP, intrusions, PLI recency.
    \item Extends to recognition: same $c_{thresh}$ predicts false-alarm
          elevation without re-fitting.
  \end{itemize}
  \note{Mirror the Aggarwal list explicitly: three of Healey's four
        age-differentiated parameters ($\phi_s$, $\eta$, $c_{thresh}$) are on
        that list.}
\end{frame}

\begin{frame}{A convergence, not a coincidence}
  \begin{itemize}
    \item Aggarwal identifies a structured residual in within-subject trial
          fluctuation.
    \item Healey identifies a structured between-subject difference in the same
          architecture.
    \item \emph{The same small set of parameters is implicated at both
          time-scales.}
    \item Prediction: the short-term endogenous drift measured in Aggarwal
          could be read out as trial-by-trial values of $\phi_s$, $\beta_{rec}$,
          $c_{thresh}$, and $\eta$.
  \end{itemize}
  \note{This is the synthesis talk's first payoff. The variability literature
        and the aging literature have been carving the same joints without
        knowing it.}
\end{frame}

\section{Cohen: biasing the emotional sub-region}

\begin{frame}{Depression and PTSD as chronic context bias}
  \begin{itemize}
    \item CMR3 augments context with an emotional valence sub-region.
    \item Depression $\approx$ persistent negative bias in emotional context
          $\to$ negative retrievals self-cue further negative retrievals.
    \item PTSD $\approx$ abnormally strong trauma--context association
          $\to$ everyday cues exceed $c_{thresh}$ for the trauma memory.
  \end{itemize}
  \note{Note the reuse of $c_{thresh}$: the same threshold that governs
        intrusion rejection in Healey governs intrusive recollection in Cohen.}
\end{frame}

\begin{frame}{Therapies as context-update operations}
  \begin{itemize}
    \item Behavioral activation: schedule positive events $\to$ updates the
          emotional context distribution.
    \item Prolonged / imaginal exposure: retrieves trauma item under a safe
          context $\to$ rebinds the emotional sub-region.
    \item Emotion regulation (reappraisal): alters context at encoding of new
          episodes $\to$ reshapes future cueing.
  \end{itemize}
  \note{Computational translations of three distinct therapeutic modalities.
        A unifying claim: therapies work by overwriting context bindings, not
        by extinguishing memories.}
\end{frame}

\section{What the three papers do together}

\begin{frame}{Shared mechanisms, different questions}
  \begin{columns}
    \column{0.6\textwidth}
      \begin{itemize}
        \item Aggarwal: \textit{Do parameters drift within a subject across lists?}
              --- Yes, and exogenous factors don't explain it.
        \item Healey: \textit{Do parameters differ between populations?}
              --- Yes, four specific ones, and they predict cross-task effects.
        \item Cohen: \textit{Do chronic biases in one sub-region generate
              clinical phenotypes?} --- Yes, nine phenomena from one setting.
      \end{itemize}
    \column{0.4\textwidth}
      \begin{itemize}
        \item Different time-scales: trials, lifetimes, chronic conditions
        \item Same architecture
        \item Same handful of knobs
      \end{itemize}
  \end{columns}
  \note{Make explicit that the lab's research program is orthogonalizing the
        CMR parameter space across these three axes.}
\end{frame}

\begin{frame}{A concrete prediction the synthesis generates}
  \begin{itemize}
    \item Measure Aggarwal-style trial-level residuals in older adults.
    \item Expect: the residuals load disproportionately on the same four
          parameters Healey identified.
    \item In PTSD: expect the residuals to have \emph{emotional} structure ---
          cluster by the valence of the cued items (per CMR3).
    \item Each of these is a test the framework has not yet been put through.
  \end{itemize}
  \note{End on a forward-looking experiment --- the synthesis earns its keep
        only if it sharpens future work.}
\end{frame}

\begin{frame}{Take-homes}
  \begin{itemize}
    \item The retrieved-context framework is not just a model of free recall;
          it is a parameterization of inter-subject, intra-subject, and clinical
          differences in episodic memory.
    \item A handful of parameters --- sustained attention, context drift,
          monitoring threshold, retrieval noise, emotional context binding ---
          carry the explanatory load across all three studies.
    \item Variability, aging, and clinical syndromes are best thought of as
          three cross-sections of the same parameter manifold.
  \end{itemize}
\end{frame}

\begin{frame}{Acknowledgments}
  \begin{itemize}
    \item Eash Aggarwal, Rivka Cohen, Karl Healey, Lynn Lohnas, Sean Polyn,
          Per Sederberg, the CMR lineage, and PEERS participants.
    \item Funding: NIH MH55687, NSF 1058886 (and grants to the individual
          papers).
    \item Computational Memory Lab, University of Pennsylvania.
  \end{itemize}
\end{frame}
"""
    return head + body + doc_end()


# ------------------------------------------------------------------
# Figure discovery + conversion utilities
# ------------------------------------------------------------------

def convert_eps_to_pdf(eps_path: Path, out_dir: Path) -> Path:
    """Use epstopdf when available; fall back to ImageMagick or ghostscript."""
    out = out_dir / (eps_path.stem + ".pdf")
    if out.exists():
        return out
    for cmd in [
        ["epstopdf", str(eps_path), "--outfile=" + str(out)],
        ["gs", "-dNOPAUSE", "-dBATCH", "-dEPSCrop", "-sDEVICE=pdfwrite",
         f"-sOutputFile={out}", str(eps_path)],
    ]:
        try:
            subprocess.run(cmd, check=True, capture_output=True)
            return out
        except (subprocess.CalledProcessError, FileNotFoundError):
            continue
    raise RuntimeError(f"could not convert {eps_path}")


def copy_ck_figures(root: Path, dest: Path) -> None:
    """Copy Cohen/Kahana 2019 figures."""
    src = root / "Figs"
    for fig in CK_FIGS.values():
        shutil.copy(src / fig, dest / fig)


def copy_ag_figures(root: Path, dest: Path) -> None:
    src = root / "Figures"
    for fig in AG_FIGS.values():
        shutil.copy(src / fig, dest / fig)


def copy_he_figures(root: Path, dest: Path) -> None:
    """Healey's figures ship as EPS; convert to PDF for pdflatex."""
    src = root / "PsychRevSubmission" / "accepted_version" / "latex_to_submit" / "figures"
    for key, pdf_name in HE_FIGS.items():
        eps = src / pdf_name.replace(".pdf", ".eps")
        if not eps.exists():
            raise FileNotFoundError(eps)
        out = convert_eps_to_pdf(eps, dest)
        if out.name != pdf_name:
            shutil.move(out, dest / pdf_name)


# ------------------------------------------------------------------
# Driver
# ------------------------------------------------------------------

def write_and_compile(deck_dir: Path, tex_source: str, tex_name: str = "deck.tex"):
    deck_dir.mkdir(parents=True, exist_ok=True)
    tex_path = deck_dir / tex_name
    tex_path.write_text(tex_source)

    # Compile twice for TOC + cross-refs; don't fail the whole build on non-fatal errors.
    log = []
    for _ in range(2):
        res = subprocess.run(
            ["pdflatex", "-interaction=nonstopmode", "-halt-on-error", tex_name],
            cwd=deck_dir, capture_output=True, text=True,
        )
        log.append(res.stdout[-2000:] + "\n" + res.stderr[-500:])
        if res.returncode != 0:
            # one more retry with relaxed mode for known non-fatal errors
            res = subprocess.run(
                ["pdflatex", "-interaction=nonstopmode", tex_name],
                cwd=deck_dir, capture_output=True, text=True,
            )
            log.append(res.stdout[-2000:])
            if res.returncode != 0 and not (deck_dir / tex_name.replace(".tex", ".pdf")).exists():
                (deck_dir / "compile.log").write_text("\n".join(log))
                return False, res.stdout + res.stderr
    (deck_dir / "compile.log").write_text("\n".join(log))
    return True, "ok"


def build_one(source_key: str, paper_key: str):
    src = SOURCES[source_key]
    label = src["label"]
    deck_root = ROOT / source_key / paper_key
    fig_dir = deck_root / "figures"
    fig_dir.mkdir(parents=True, exist_ok=True)

    if paper_key == "CohenKahana2019":
        copy_ck_figures(src["ck"], fig_dir)
        tex = deck_cohen_kahana(label)
    elif paper_key == "AGGA16memvar":
        copy_ag_figures(src["ag"], fig_dir)
        tex = deck_aggarwal(label)
    elif paper_key == "Heal15agingcmr":
        copy_he_figures(src["he"], fig_dir)
        tex = deck_healey(label)
    elif paper_key == "synthesis":
        copy_ck_figures(src["ck"], fig_dir)
        copy_ag_figures(src["ag"], fig_dir)
        copy_he_figures(src["he"], fig_dir)
        tex = deck_synthesis(label)
    else:
        raise ValueError(paper_key)

    ok, log = write_and_compile(deck_root, tex)
    status = "OK" if ok else "FAIL"
    print(f"[{status}] {source_key}/{paper_key}")
    if not ok:
        print(log[-1500:])
    return ok


def main():
    papers = ["CohenKahana2019", "AGGA16memvar", "Heal15agingcmr", "synthesis"]
    results = []
    for source_key in ["local", "github"]:
        for paper in papers:
            results.append((source_key, paper, build_one(source_key, paper)))
    print()
    print("Summary:")
    for s, p, ok in results:
        tag = "OK" if ok else "FAIL"
        print(f"  [{tag}] {s:7s} / {p}")


if __name__ == "__main__":
    main()
