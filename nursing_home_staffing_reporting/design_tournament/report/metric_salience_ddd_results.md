# Metric Salience DDD Results

This implementation uses a facility-level post-minus-pre contrast in `(weekend total - weekday total) - (weekend RN - weekday RN)`. It is a conservative proxy for the full facility-day-staff-category DDD because the existing data are already aggregated to facility-month.

| estimand | n | mean_delta | se | outcome | group | treated_n | control_n | diff | p |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| overall_post_pre_change_in_targeted_minus_rn_weekend_gap | 14836 | 0.0158392 | 0.00306618 |  |  |  |  |  |  |
| high_shadow_price_heterogeneity | 14573 |  | 0.00622439 | delta_targeted_minus_rn_gap | high_shadow_price | 2098 | 12475 | -0.00501129 | 0.420772 |

Interpretation should focus on mechanism direction, not standalone causality.
