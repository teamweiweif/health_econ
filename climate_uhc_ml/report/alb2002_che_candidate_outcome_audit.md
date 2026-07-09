# ALB_2002 CHE Candidate Outcome Audit

Status: temp-only household-level CHE candidate outcome audit. This builds household CHE10/CHE25 candidates from the period-aligned combined no-gifts-with-transport OOP numerator and documented monthly total-budget denominator candidate. It does not write `data/`, does not declare SDG 3.8.2 ready, and does not construct climate-linked outcomes.

## Summary

| Metric | Value | Interpretation |
|---|---:|---|
| alb2002_che_candidate_household_rows | 3599 | Temp-only ALB_2002 household CHE candidate rows. |
| alb2002_che_candidate_denominator_rows | 3599 | Rows with positive monthly total-budget candidate denominator. |
| alb2002_che_candidate_missing_rows | 0 | Rows missing the candidate denominator. |
| alb2002_che_candidate_positive_oop_rows | 3038 | Rows with positive period-aligned combined OOP candidate. |
| alb2002_che_candidate_positive_oop_weighted_rate | 0.852605 | Weighted positive-OOP rate using current weight evidence. |
| alb2002_che_candidate_che10_rows | 824 | Rows with candidate CHE10 under the period-aligned combined OOP policy. |
| alb2002_che_candidate_che10_rate | 0.228952 | Unweighted candidate CHE10 rate. |
| alb2002_che_candidate_che10_weighted_rate | 0.23666 | Weighted candidate CHE10 rate. |
| alb2002_che_candidate_che25_rows | 290 | Rows with candidate CHE25 under the period-aligned combined OOP policy. |
| alb2002_che_candidate_che25_rate | 0.0805779 | Unweighted candidate CHE25 rate. |
| alb2002_che_candidate_che25_weighted_rate | 0.0859036 | Weighted candidate CHE25 rate. |
| alb2002_che_candidate_period_policy_rows | 3 | Period-aligned policy rows consumed upstream. |
| alb2002_che_candidate_weight_positive_rows | 3599 | Positive household-weight rows consumed upstream. |
| alb2002_che_candidate_weighted_inference_ready_rows | 0 | Rows ready for promoted weighted inference; should remain zero. |
| alb2002_che_candidate_minimum_recipe_harmonized_ready_rows | 0 | Rows ready for harmonized data promotion upstream; should remain zero. |
| alb2002_che_candidate_minimum_recipe_outcome_ready_rows | 0 | Rows ready for outcome promotion upstream; should remain zero. |
| alb2002_che_candidate_climate_linkage_ready_rows | 0 | Rows ready for climate linkage; should remain zero until geography is verified. |
| alb2002_che_candidate_outcome_promotion_ready_rows | 0 | Rows ready for final household outcome promotion; intentionally zero. |
| alb2002_che_candidate_current_decision | blocked_alb2002_che_candidate_not_promoted_due_recipe_sdg_climate_gates | Current fail-closed CHE candidate outcome decision. |

## Outcome Audit

| outcome_id | denominator_rows | event_rows | event_rate | weighted_event_rate | ready_for_outcome | promotion_status |
|---|---|---|---|---|---|---|
| positive_oop_candidate | 3599 | 3038 | 0.844123 | 0.852605 | 0 | temp_only_candidate_outcomes_not_promoted |
| oop_share_total_budget_candidate | 3599 |  |  |  | 0 | temp_only_candidate_outcomes_not_promoted |
| che10_total_budget_candidate | 3599 | 824 | 0.228952 | 0.23666 | 0 | temp_only_candidate_outcomes_not_promoted |
| che25_total_budget_candidate | 3599 | 290 | 0.0805779 | 0.0859036 | 0 | temp_only_candidate_outcomes_not_promoted |

## Lineage

| derived_field | source_fields | formula_or_rule | status | blocking_reason |
|---|---|---|---|---|
| oop_4w_monthly_equivalent | oop_4w_sum_unreviewed | oop_4w_sum_unreviewed * 13 / 12 | candidate_not_promoted | Four-week OOP scope is documented as a stress-test numerator, not a promoted final numerator. |
| oop_12m_monthly_equivalent | oop_12m_sum_unreviewed | oop_12m_sum_unreviewed / 12 | candidate_not_promoted | Twelve-month hospital/dentist OOP scope is documented as a stress-test numerator, not a promoted final numerator. |
| oop_combined_monthly_equivalent | oop_4w_sum_unreviewed;oop_12m_sum_unreviewed | (oop_4w_sum_unreviewed * 13 / 12) + (oop_12m_sum_unreviewed / 12) | candidate_not_promoted | Combined mixed-recall OOP requires final numerator-scope and benchmark review before outcome promotion. |
| oop_share_total_budget_candidate | oop_combined_monthly_equivalent;total_consumption | oop_combined_monthly_equivalent / total_consumption | candidate_not_promoted | Total consumption is documented as a monthly total-budget candidate, but final outcome promotion still requires recipe and benchmark review. |
| che10_total_budget_candidate | oop_share_total_budget_candidate | oop_share_total_budget_candidate > 0.10 | candidate_not_promoted | CHE10 candidate is computed for audit only and not written to data/. |
| che25_total_budget_candidate | oop_share_total_budget_candidate | oop_share_total_budget_candidate > 0.25 | candidate_not_promoted | CHE25 candidate is computed for audit only and not written to data/. |

## Interpretation

- Candidate CHE10 and CHE25 are now available at household level in `temp/alb2002_che_candidate_household_outcomes.csv`.
- The candidate rates are audit evidence only: outcome-promotion-ready rows remain zero.
- SDG 3.8.2 remains blocked because SPL, PPP/CPI, and discretionary-budget inputs are not accepted.
- Climate-linked outcome construction remains blocked because ALB_2002 geography is district-admin only and the available boundary lead is not verified as a 2001/2002 source.

## Machine-Readable Outputs

- `temp/alb2002_che_candidate_household_outcomes.csv`
- `temp/alb2002_che_candidate_outcome_lineage.csv`
- `result/alb2002_che_candidate_outcome_audit.csv`
- `result/alb2002_che_candidate_outcome_summary.csv`
