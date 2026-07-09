# ALB_2002 Skip and Missing-Code Semantics Audit

Status: fail-closed raw skip/missing evidence. This audit reads ALB_2002 raw SPSS health files and checks whether downstream OOP payment and access-reason fields are observed only when their questionnaire trigger fields indicate they should be asked. It does not write `data/`, does not construct final outcomes, and does not promote any harmonization, SDG 3.8.2, outcome, or climate-linkage row.

## Bottom Line

- The ALB_2002 payment skip paths have zero positive downstream payment values when visit, drug, hospital-stay, or dentist trigger variables are negative.
- The nonmissing skipped downstream payment values are zero-only, so they feed the separate OOP skip-value decision audit rather than final outcome promotion.
- Conditional access and health-financing reason fields remain denominator-sensitive and still require manual policy review.
- These checks do not settle OOP inclusion scope, gift treatment, recall-period comparability, SDG 3.8.2 denominator construction, household aggregation, or climate-ready geography.
- Recipe-ready, outcome-ready, SDG 3.8.2-ready, and climate-linkage-ready rows from this audit: 0.
- Current decision: `blocked_alb2002_skip_missing_semantics_seen_but_recipe_not_ready`.

## Summary

| Metric | Value | Interpretation |
|---|---:|---|
| alb2002_skip_missing_semantics_rows | 12 | Rows in the ALB_2002 skip/missing semantics audit. |
| alb2002_skip_missing_payment_block_rows | 7 | Person-level visit/payment skip blocks audited. |
| alb2002_skip_missing_access_condition_rows | 5 | Household access/financing conditional skip blocks audited. |
| alb2002_skip_missing_payment_nonmissing_when_not_triggered_rows | 11 | Payment downstream rows nonmissing when the trigger is negative. |
| alb2002_skip_missing_payment_positive_when_not_triggered_rows | 0 | Payment downstream rows positive when the trigger is negative. |
| alb2002_skip_missing_payment_nonmissing_cells_when_not_triggered | 11 | Payment downstream cells nonmissing when the trigger is negative. |
| alb2002_skip_missing_payment_zero_cells_when_not_triggered | 11 | Payment downstream cells equal to zero when the trigger is negative. |
| alb2002_skip_missing_payment_positive_cells_when_not_triggered | 0 | Payment downstream cells positive when the trigger is negative. |
| alb2002_skip_missing_payment_zero_only_block_rows | 2 | Payment skip blocks where nonmissing skipped values are zero-only. |
| alb2002_skip_missing_payment_no_skipped_value_block_rows | 5 | Payment skip blocks with no downstream values when triggers are negative. |
| alb2002_skip_missing_payment_all_missing_when_triggered_rows | 0 | Triggered payment rows where every downstream payment variable is missing. |
| alb2002_skip_missing_payment_zero_or_missing_when_triggered_rows | 274 | Triggered payment rows with no positive downstream payment; may be true zero care/spending and needs policy review. |
| alb2002_skip_missing_condition_nonmissing_when_not_triggered_rows | 0 | Conditional access/financing downstream rows nonmissing when the trigger condition is false. |
| alb2002_skip_missing_condition_missing_when_triggered_rows | 0 | Conditional access/financing downstream rows missing when the trigger condition is true. |
| alb2002_skip_missing_questionnaire_payment_nonmissing_skip_review_observed | 11 | Nonmissing skipped-payment rows observed in the questionnaire audit. |
| alb2002_skip_missing_questionnaire_payment_positive_skip_leaks_observed | 0 | Positive skipped-payment rows observed in the questionnaire audit. |
| alb2002_skip_missing_oop_policy_rows_observed | 11 | OOP aggregation policy stress-test rows observed upstream. |
| alb2002_skip_missing_minimum_recipe_harmonized_ready_observed | 0 | Harmonized-ready rows observed upstream. |
| alb2002_skip_missing_climate_ready_rows_observed | 0 | Climate-linkage-ready rows observed upstream. |
| alb2002_skip_missing_recipe_ready_rows | 0 | Rows promoted to harmonization recipe by this audit; intentionally zero. |
| alb2002_skip_missing_outcome_ready_rows | 0 | Rows promoted to final outcome construction by this audit; intentionally zero. |
| alb2002_skip_missing_sdg382_ready_rows | 0 | Rows promoted to SDG 3.8.2 construction by this audit; intentionally zero. |
| alb2002_skip_missing_climate_linkage_ready_rows | 0 | Rows promoted to climate linkage by this audit; intentionally zero. |
| alb2002_skip_missing_current_decision | blocked_alb2002_skip_missing_semantics_seen_but_recipe_not_ready | Current fail-closed decision for ALB_2002 skip/missing semantics. |

## Skip/Missing Evidence Rows

| audit_family | subdomain | trigger_variable | trigger_positive_rows | trigger_negative_rows | downstream_any_nonmissing_when_not_triggered_rows | downstream_positive_cells_when_not_triggered | downstream_zero_cells_when_not_triggered | dependent_missing_when_triggered_rows | skip_missing_evidence_status |
|---|---|---|---|---|---|---|---|---|---|
| person_payment_visit_skip | public_ambulatory_4w | m5a_q12 | 2120 | 13439 | 8 | 0 | 8 | 0 | raw_skip_path_nonmissing_values_when_not_triggered_are_zero_only |
| person_payment_visit_skip | private_doctor_4w | m5a_q22 | 219 | 15340 | 0 | 0 | 0 | 0 | raw_skip_path_consistent_no_downstream_values_when_not_triggered |
| person_payment_visit_skip | nurse_paramedic_midwife_4w | m5a_q30 | 375 | 15184 | 0 | 0 | 0 | 0 | raw_skip_path_consistent_no_downstream_values_when_not_triggered |
| person_payment_visit_skip | popular_doctor_4w | m5a_q38 | 53 | 15506 | 0 | 0 | 0 | 0 | raw_skip_path_consistent_no_downstream_values_when_not_triggered |
| person_payment_visit_skip | own_drugs_4w | m5a_q46 | 2445 | 13114 | 0 | 0 | 0 | 0 | raw_skip_path_consistent_no_downstream_values_when_not_triggered |
| person_payment_visit_skip | hospital_stay_12m | m5a_q48 | 707 | 14852 | 3 | 0 | 3 | 0 | raw_skip_path_nonmissing_values_when_not_triggered_are_zero_only |
| person_payment_visit_skip | dentist_12m | m5a_q59 | 3352 | 12207 | 0 | 0 | 0 | 0 | raw_skip_path_consistent_no_downstream_values_when_not_triggered |
| household_access_condition_skip | raise_money_for_health_care_methods | m5b_q01 | 1623 | 1976 | 0 | 0 | 0 | 0 | raw_conditional_skip_path_consistent |
| household_access_condition_skip | delayed_or_no_help_reason | m5b_q03 | 144 | 3103 | 0 | 0 | 0 | 0 | raw_conditional_skip_path_consistent |
| household_access_condition_skip | hospital_referral_not_gone_reason | m5b_q05 | 161 | 3086 | 0 | 0 | 0 | 0 | raw_conditional_skip_path_consistent |
| household_access_condition_skip | refused_health_services_reason | m5b_q07 | 68 | 3531 | 0 | 0 | 0 | 0 | raw_conditional_skip_path_consistent |
| household_access_condition_skip | medicine_discount_access_reason | m5b_q09 | 2044 | 1555 | 0 | 0 | 0 | 0 | raw_conditional_skip_path_consistent |

## Interpretation

- Zero-only skipped payment values can be coded as structural zeros only after the recipe explicitly defines zero/missing semantics for skipped fields.
- Triggered rows with no positive downstream payment may reflect no spending, free care, or unresolved missing-code behavior; they are not outcome-ready by themselves.
- Access-reason variables can support forgone-care barriers only after the trigger denominator is fixed for illness, delayed care, referral, refusal, medicine entitlement, and no-care-needed responses.

## Machine-Readable Outputs

- `temp/alb2002_skip_missing_semantics_audit.csv`
- `result/alb2002_skip_missing_semantics_summary.csv`
