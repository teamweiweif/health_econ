# Design Tournament Plan

## Reframing

The old global exposure DID is demoted because the prior identification audit found failed pre-trends and a significant placebo timing test. The new estimand is not a broad national transparency effect. It is whether algorithmic public labels and rating thresholds changed staffing reliability, staffing mix, and score-targeted behavior.

## Pre-Specified Designs

| Design | Estimand | Identification logic | Main failure mode |
|---|---|---|---|
| A. Staffing-star threshold RD | Local effect of being just above a staffing-score threshold | Homes near a CMS staffing-star cutoff have similar scores but different public labels | Score proxy fails; manipulation; pre-outcome jumps |
| B. RD-DID / difference-in-discontinuities | Change in cutoff discontinuity after July 2022 | Difference out pre-existing local discontinuities | Pre-period discontinuities move similarly at placebo cutoffs |
| C. Formula-induced overall-star shock | Effect of losing old four-star staffing overall bonus | July rule mechanically removes a label bonus for some homes | Formula reconstruction weak; exclusion restriction fragile |
| D. Facility-internal metric salience DDD | Post-July shift toward score-targeted weekend total staffing | Facility-month shocks absorbed by within-facility metric/day contrasts | Broad labor-market recovery moves all metrics similarly |
| E. Shadow price | Whether homes close to score rewards improve more | Marginal rating return varies discontinuously with baseline score distance | High-shadow facilities were already trending differently |
| F. Bunching/gaming | Post-July clustering above true cutoffs | Algorithmic score management predicts bunching at true, not placebo, cutoffs | Proxy score too noisy; bunching present before July |
| G. 2018 validation event | Whether PBJ detects zero-RN gaming after earlier policy | External validation against OIG-described mechanism | Current local PBJ source starts in 2019, so 2017-2018 may be unavailable |
| H. Matched/synthetic fallback | Secondary comparison only | Match on pre trajectories if threshold designs fail | Recreates old weak DID if pretrends remain poor |

## Outcome Priority

Primary outcomes are staffing reliability and lower-tail risk: RN<8h days, weekend RN<8h days, zero-RN days, zero-total-nurse days, weekend p10/p25 HPRD, worst weekend total nurse HPRD, worst weekend RN HPRD, low-staffing weekend shares, weekend total nurse HPRD, and census.

Mechanism and gaming outcomes are score-targeted HPRD, weekend share of total nursing hours, weekday-weekend gaps, contract share, and formula/rating recovery.

Downstream deficiencies and ratings are descriptive only unless timing and diagnostics support causal interpretation.

## Timing Rules

- January 2022 is a transparency shock.
- July 27, 2022 is the main rating / algorithmic-label shock.
- Monthly daily-staffing post starts in August 2022.
- Quarterly clean post starts in 2022Q4; 2022Q3 is transition.
- Turnover outcomes are treated as delayed because the guide uses six-quarter windows.
- Preferred pre windows avoid 2021Q4 where possible because the project instructions flag ransomware/incomplete-reporting risk.

## Go / No-Go Rules

Strong Go requires verified official algorithm sources, a valid running variable or formula shock, no serious pre-outcome discontinuity, local covariate balance, no invalid density manipulation, weak placebo-cutoff performance, robust bandwidths, July-aligned timing, and concentration in policy-targeted outcomes.

Conditional Go is used for compelling but imperfect local/mechanism evidence.

No-Go is required if emulator validation fails, pre-outcome discontinuities are large, placebo cutoffs look similar, effects appear before July 2022, or effects are broad in a way consistent with labor-market recovery.
