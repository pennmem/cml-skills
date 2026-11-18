# Figures for PEERS recall data

`peers_analysis.set_style()` applies the settings below, `plot_curve` and `plot_lag_crp` draw in this style, and
`standard_figure(ev)` makes the four-panel summary (serial position, first recall, lag-CRP, inter-response
times). Look at every figure before delivering it.

## Settings

- Matplotlib. Font Arial; Liberation Sans has the same metrics and is what a Linux session usually has (check
  with `fc-list`). Text 8-9 pt at final size.
- Sizes: one column 3.3 in wide, two columns 6.9 in (APA journals); 7.5 x 2.95 in for a full-width strip in a
  grant or talk. Save vector PDF with `pdf.fonttype` 42 so the text stays editable; 300 dpi for anything raster.
- No top or right spine. Thin axes in dark gray. No grid unless values must be read off it.
- Panel letters in bold capitals at the top left. No titles inside panels that repeat the axis label.

## Marks

- Observed data: black, thin line, filled circles ringed in white, error bars on every point.
- A model beside data: a colored line without markers (orange), or broken lines with open symbols as in Kahana
  (2020, Figure 8). Data are always the filled symbols.
- Conditions: at most three colors, in this fixed order: blue `#2a78d6`, orange `#eb6834`, aqua `#1baf7a`, each
  with its own marker (circle, diamond, square). The set passes checks for color-vision deficiencies. Beyond
  three conditions use separate panels. For younger and older adults use blue and orange, in that order.
- Legend without a frame whenever there are two or more series. Text is always black or dark gray, never the
  color of a series. Never two y-axes.

## The standard plots

| Plot | x | y | Notes |
|---|---|---|---|
| Serial position curve | Serial position, ticks at 1 and every fourth | Recall probability, 0 to 1 | |
| Probability of first recall | Serial position | Probability of first recall, from 0 | |
| Lag-CRP | Lag, -5 to 5, ticks at odd lags | Conditional response probability, from 0 | break the line at lag 0 |
| Inter-response times | Output position | Inter-response time (s), log scale | one curve per number recalled, labeled |
| Intrusions | Type or list lag | Number per list, or proportion | |

## Error bars and captions

- 95% confidence intervals unless there is a reason for SEM. Within-subject intervals (Loftus & Masson, 1994)
  when the comparison is within subject.
- The caption stands alone: what is plotted, what each line and panel is, what the error bars are, the number of
  subjects, and which sessions and lists went in.
- State goodness of fit as RMSD in the units of the y-axis, not as R².
