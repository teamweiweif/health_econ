# Metric Salience DDD Rescue Results V3

This pass builds a true facility-week by metric panel from PBJ daily nurse staffing files, excluding 2021Q4 because CMS/OIG documentation flags incomplete PBJ reporting for many homes.

## DDD Estimates

| estimand | n | mean_delta | se | sample_definition | outcome | group | treated_n | control_n | diff | p |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| post_minus_pre_targeted_weekend_total_minus_weekend_rn_gap | 14679 | 0.0189122 | 0.00247244 | facility-week by metric panel, post Aug 2022 versus pre 2021Q1-2022Q2 excluding 2021Q4 |  |  |  |  |  |  |
| formula_loss_heterogeneity | 14677 |  | 0.00567134 | two-group post-minus-pre comparison | delta_score_targeted_minus_rn_gap | formula_induced_overall_star_loss | 1540 | 13137 | -0.00828902 | 0.143882 |
| high_rating_incentive_heterogeneity | 14677 |  | 0.00478718 | two-group post-minus-pre comparison | delta_score_targeted_minus_rn_gap | high_shadow_price | 2015 | 12662 | 0.00328552 | 0.492525 |

## Placebo and Reallocation

| placebo | n | mean_delta | sample_definition |
| --- | --- | --- | --- |
| weekday_total_vs_weekday_rn | 14679 | 0.0625592 | non-targeted placebo metric contrast in facility-week panel |

| outcome | n | mean_delta | sample_definition |
| --- | --- | --- | --- |
| total_weekly_nursing_hours | 14682 | 107.264 | weekly total nursing hours reallocation diagnostic |
| weekend_total_nurse_hprd | 14679 | -0.0498287 | score-targeted weekend total nurse HPRD diagnostic |
| weekday_total_nurse_hprd | 14679 | -0.0890943 | weekday offset diagnostic |

Interpretation: **broad labor-market or mixed movement**. This is mechanism evidence and should be read with the RD/formula diagnostics.
