# PTC 400% FPL Premium-Intensity Test

## Verdict

`PREMIUM-INTENSITY-SIGNAL-PRESENT-BUT-CHECK-DIRECTION`

This test adds the missing policy-intensity layer to the leading ACA affordability idea using CMS
Exchange Public Use Files. It is still a state-level approximation because the uploaded SIPP parquet
does not contain county or rating area.

## Data Built

- CMS Exchange PUF years: 2018-2023.
- Files used: Rate-PUF and Plan Attributes PUF.
- Plan filter: individual-market, non-dental, silver plans.
- Premium proxy: unweighted state average of rating-area second-lowest silver premiums for ages
  40 and 60.
- Treatment intensity: pre-2021 age-60 gross benchmark burden at 400% FPL above the 8.5% ARPA cap.

PUF state coverage is incomplete by construction because CMS Exchange PUFs generally exclude states
whose State-Based Exchanges do not rely on the federal platform.

## Support Cells

| post | above400 | high premium | persons | market events | uninsured events | states |
|---:|---:|---:|---:|---:|---:|---:|
| 0 | 0 | 0 | 3422 | 3147 | 5224 | 19 |
| 0 | 0 | 1 | 2794 | 3012 | 4627 | 20 |
| 0 | 1 | 0 | 2776 | 1746 | 2962 | 19 |
| 0 | 1 | 1 | 2119 | 1508 | 2654 | 20 |
| 1 | 0 | 0 | 1918 | 2315 | 3520 | 17 |
| 1 | 0 | 1 | 1824 | 2727 | 3120 | 19 |
| 1 | 1 | 0 | 1594 | 1155 | 1625 | 17 |
| 1 | 1 | 1 | 1426 | 1260 | 1779 | 19 |

## Triple-Difference Screen

Sample: adults 26-64, annual family income 300-500% FPL, PUF-covered states, SIPP reference years
2018-2023. Coefficient is `post2021 x above400 x high_pre_premium_burden`.

| outcome | coef_post_x_above400_x_highpremium | se_hc1 | t_stat | persons | states | min_cell_persons |
|---|---|---|---|---|---|---|
| any_coverage | -0.0210 | 0.0060 | -3.5255 | 15533 | 39 | 1426 |
| direct_purchase | 0.0129 | 0.0056 | 2.2991 | 15533 | 39 | 1426 |
| market_or_subsidy | 0.0128 | 0.0050 | 2.5640 | 15533 | 39 | 1426 |
| oop_any | -0.0231 | 0.0093 | -2.4773 | 15533 | 39 | 1426 |
| uninsured | 0.0210 | 0.0060 | 3.5255 | 15533 | 39 | 1426 |

## Interpretation

- This is the first version that directly tests the premium-intensity idea rather than only the
  400% FPL cliff.
- If the high-premium interaction does not recover a coherent market/subsidy or uninsured pattern,
  then the PTC project remains conditional rather than clean.
- A paper-quality version still needs county/rating-area matching or benchmark premium data mapped
  to geography finer than state.

## Source Checks

- CMS Exchange PUF page:
  https://www.cms.gov/marketplace/resources/data/public-use-files
- CMS notes that Rate-PUF reports rates by age, tobacco, and geographic location, and Plan-PUF
  identifies plan attributes including metal level.

## Outputs

- `result/idea_scan/ptc_premium_policy_state_year.csv`
- `result/idea_scan/ptc_premium_state_support.csv`
- `result/idea_scan/ptc_premium_intensity_support.csv`
- `result/idea_scan/ptc_premium_intensity_estimates.csv`
