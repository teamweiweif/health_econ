# Thirty-Second Round Decision: ARPA 400% FPL Source Decomposition

## Verdict

`LEAD REMAINS CONDITIONAL GO`

The source-decomposition screen supports keeping ARPA 400% FPL as the lead, but it changes the framing.

The main full-sample estimate shows a 2.8 percentage-point uninsured decline above 400% FPL after ARPA, but employer-related private coverage also rises. That means the paper should not claim a pure Marketplace enrollment channel from the full sample alone.

The stronger mechanism evidence comes from lagged non-employer months: market/subsidy coverage rises by 7.4 percentage points, while uninsured falls by 4.6 percentage points and employer-related source does not rise. This is the cleanest SIPP mechanism check currently available.

## Main Estimates

- Uninsured: -0.0277 (person-cluster se 0.0141, t -1.96; state-cluster se 0.0151, t -1.83; N=215,972).
- Source employer-related: +0.0301 (person-cluster se 0.0190, t 1.59; state-cluster se 0.0244, t 1.24; N=215,972).
- Source bought direct: +0.0073 (person-cluster se 0.0108, t 0.67; state-cluster se 0.0107, t 0.68; N=215,972).
- Direct-purchase / RMARKTPLACE: +0.0208 (person-cluster se 0.0137, t 1.52; state-cluster se 0.0145, t 1.43; N=215,972).
- Marketplace flag: +0.0165 (person-cluster se 0.0123, t 1.34; state-cluster se 0.0107, t 1.54; N=215,972).
- Market/subsidy composite: +0.0202 (person-cluster se 0.0137, t 1.47; state-cluster se 0.0147, t 1.37; N=215,972).
- Lagged non-employer uninsured: -0.0457 (person-cluster se 0.0331, t -1.38; state-cluster se 0.0425, t -1.08; N=71,638).
- Lagged non-employer market/subsidy: +0.0739 (person-cluster se 0.0328, t 2.25; state-cluster se 0.0350, t 2.11; N=71,638).
- Lagged current-employer source employer-related: -0.0007 (person-cluster se 0.0029, t -0.24; state-cluster se 0.0026, t -0.26; N=126,551).

## Ranking Implication

1. ARPA 400% FPL cliff removal remains the strongest SIPP lead.
2. The paper should be written as a difference-in-discontinuities coverage-affordability design around the removal of the 400% FPL subsidy cliff.
3. Marketplace/direct-purchase uptake should be treated as an observed mechanism check, not the necessary primary outcome.
4. The strongest next technical improvement is a full regression-discontinuity/event-study robustness pack: bandwidths, donut around 400%, annual-vs-monthly FPL, age/premium-risk gradients, and pre-ARPA yearly placebo discontinuities.

## Caution

The older-adult gradient is not supportive in this screen. Since older adults should be most exposed to high unsubsidized benchmark premiums, that is a real weakness for a simple premium-burden story. The next robustness pass must test whether the response is concentrated by state-level premium burden rather than age alone, and whether the 50-64 null is stable across bandwidths and annual-FPL definitions.
