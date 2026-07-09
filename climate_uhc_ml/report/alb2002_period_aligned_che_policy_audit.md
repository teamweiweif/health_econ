# ALB_2002 Period-Aligned CHE Policy Audit

Status: fail-closed period-aligned CHE stress test. This audit compares monthly-equivalent OOP numerator candidates with the documented monthly total-budget denominator candidate (`totcons`) but does not promote household outcomes.

## Summary

| Metric | Value | Interpretation |
|---|---:|---|
| alb2002_period_aligned_che_policy_rows | 3 | Period-aligned ALB_2002 CHE stress-test policies. |
| alb2002_period_aligned_che_household_rows | 3599 | Household rows evaluated by the period-aligned CHE audit. |
| alb2002_period_aligned_che_denominator_rows | 3599 | Rows with positive documented total-budget denominator candidate. |
| alb2002_period_aligned_che_denominator_documented_rows | 3 | Rows where the monthly total-budget denominator evidence is documented for this policy row. |
| alb2002_period_aligned_che_zero_skip_ready_rows | 4 | Existing narrow zero-skipped-payment decision rows carried into this audit. |
| alb2002_period_aligned_che_period_alignment_ready_rows | 3 | Policy rows with denominator period and no-positive-leakage skip evidence ready for stress testing. |
| alb2002_period_aligned_che_combined_che10_rows | 824 | CHE10 rows under the combined monthly-equivalent no-gifts-with-transport policy. |
| alb2002_period_aligned_che_combined_che10_rate | 0.228952 | Unweighted CHE10 rate under the combined monthly-equivalent no-gifts-with-transport policy. |
| alb2002_period_aligned_che_combined_che10_weighted_rate | 0.23666 | Weighted CHE10 rate under the combined monthly-equivalent no-gifts-with-transport policy. |
| alb2002_period_aligned_che_combined_che25_rows | 290 | CHE25 rows under the combined monthly-equivalent no-gifts-with-transport policy. |
| alb2002_period_aligned_che_combined_che25_rate | 0.0805779 | Unweighted CHE25 rate under the combined monthly-equivalent no-gifts-with-transport policy. |
| alb2002_period_aligned_che_combined_che25_weighted_rate | 0.0859036 | Weighted CHE25 rate under the combined monthly-equivalent no-gifts-with-transport policy. |
| alb2002_period_aligned_che_outcome_ready_rows | 0 | Rows promoted to final household outcomes by this audit; intentionally zero. |
| alb2002_period_aligned_che_recipe_ready_rows | 0 | Rows promoted to harmonized recipe status by this audit; intentionally zero. |
| alb2002_period_aligned_che_sdg382_ready_rows | 0 | Rows promoted to SDG 3.8.2 status by this audit; intentionally zero. |
| alb2002_period_aligned_che_climate_linkage_ready_rows | 0 | Rows ready for climate linkage by this audit; intentionally zero. |
| alb2002_period_aligned_che_current_decision | blocked_alb2002_period_aligned_che_policy_not_outcome_ready | Current fail-closed decision for ALB_2002 period-aligned CHE policy. |

## Policy Rows

| policy_name | numerator_period_alignment | positive_oop_rows | che10_rows | che10_rate | che10_weighted_rate | che25_rows | che25_rate | che25_weighted_rate | period_alignment_ready | ready_for_outcome |
|---|---|---|---|---|---|---|---|---|---|---|
| period_aligned_4w_no_gifts_transport_monthly_equivalent | four_week_oop_scaled_by_13_over_12_to_monthly_equivalent | 2541 | 680 | 0.188941 | 0.199549 | 225 | 0.0625174 | 0.0661003 | 1 | 0 |
| period_aligned_12m_hospital_dentist_monthly_equivalent | twelve_month_hospital_dentist_oop_scaled_by_1_over_12 | 2102 | 121 | 0.0336205 | 0.0338611 | 32 | 0.00889136 | 0.00897615 | 1 | 0 |
| period_aligned_combined_no_gifts_transport_monthly_equivalent | four_week_oop_scaled_by_13_over_12_plus_twelve_month_hospital_dentist_scaled_by_1_over_12 | 3038 | 824 | 0.228952 | 0.23666 | 290 | 0.0805779 | 0.0859036 | 1 | 0 |

## Interpretation

- The denominator audit documents local `totcons` as the public `totcons3` monthly total-budget candidate.
- The OOP aggregation audit verifies that the existing four-week and twelve-month core OOP sums match the no-gifts-with-transport reconstruction for all household rows.
- This audit corrects the period comparison for stress testing: four-week OOP is scaled by `13/12`, and twelve-month hospital/dentist OOP is scaled by `1/12`.
- These remain stress tests. The audit writes no `data/` files and promotes zero recipe, outcome, SDG 3.8.2, or climate-linkage rows.

## Machine-Readable Outputs

- `temp/alb2002_period_aligned_che_policy_audit.csv`
- `result/alb2002_period_aligned_che_policy_summary.csv`
