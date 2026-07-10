# PTC 400% FPL Fast RD-DID Test

## Verdict

`SUPPORT-YES-BUT-SIGNAL-CONFLICTS-WITH-UPTAKE-STORY`

The support is large enough to justify a serious follow-up design, but the first-pass
local RD-DID signal conflicts with a simple positive marketplace-uptake story. This should be
treated as **conditional next-test worthy**, not paper-ready.

## Main 400% FPL Screen

Specification: adults 26-64, annual family income-to-poverty within 50 percentage points
of the cutoff, pre 2017-2020 vs post 2021-2023. Coefficient is the change in the above-cutoff
discontinuity after 2021 from a local linear weighted model.

| outcome | coef_post_x_above | se_hc1 | t_stat | persons | min_cell_persons | min_cell_events |
|---|---|---|---|---|---|---|
| any_coverage | 0.0088 | 0.0063 | 1.3985 | 15602 | 2766 | 32779 |
| direct_purchase | -0.0324 | 0.0063 | -5.1499 | 15602 | 2766 | 3992 |
| market_or_subsidy | -0.0312 | 0.0058 | -5.3527 | 15602 | 2766 | 3138 |
| uninsured | -0.0088 | 0.0063 | -1.3985 | 15602 | 2766 | 3233 |

## Age-Intensity Check

Premium subsidies should matter more for older adults because age-rated premiums are higher.
This quick check estimates the same market/subsidy outcome separately for ages 50-64 and 26-49.

| age_group | coef_post_x_above | se_hc1 | t_stat | persons | min_cell_persons | min_cell_events |
|---|---|---|---|---|---|---|
| age_26_49 | -0.0325 | 0.0074 | -4.3844 | 9384 | 1669 | 1730 |
| older_50_64 | -0.0273 | 0.0092 | -2.9625 | 6347 | 1110 | 1408 |

## Placebo Cutoffs

Outcome: market/subsidy coverage. Bandwidth: 50 percentage points.

| cutoff | coef_post_x_above | se_hc1 | t_stat | persons | min_cell_persons |
|---|---|---|---|---|---|
| 3.0000 | 0.0280 | 0.0066 | 4.2624 | 17633 | 3269 |
| 3.5000 | 0.0420 | 0.0063 | 6.6678 | 16892 | 3145 |
| 4.5000 | -0.0044 | 0.0056 | -0.7841 | 14011 | 2469 |
| 5.0000 | 0.0280 | 0.0055 | 5.0746 | 12321 | 2211 |

## Interpretation

- SIPP support around 400% FPL is not the problem; cell sizes are adequate.
- The current-market/subsidy signal is negative in the broad local screen, so the next stage
  must diagnose whether this is real substitution, below-400 treatment spillover, measurement
  limits in exchange/subsidy flags, or a poor control-side construction.
- A publishable version needs a sharper treatment-intensity measure: age-rated premium exposure,
  county/state benchmark premiums, or state-by-age pre-ARP premium burden.
- Without that treatment-intensity layer, the design is causally attractive but empirically
  underidentified because both sides of 400% FPL received affordability changes after ARPA.

## Outputs

- `result/idea_scan/ptc_400fpl_rddid_fast_estimates.csv`
- `result/idea_scan/ptc_400fpl_density_bins.csv`
