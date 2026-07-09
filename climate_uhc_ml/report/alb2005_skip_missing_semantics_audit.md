# ALB_2005 Skip and Missing-Code Semantics Audit

Status: fail-closed raw skip/missing evidence. This audit reads ALB_2005 raw SPSS health files and checks whether downstream OOP payment and access-reason fields are observed only when their questionnaire trigger fields indicate they should be asked. It does not write `data/`, does not construct final outcomes, and does not promote any harmonization, outcome, or climate-linkage row.

## Bottom Line

- Person-level visit/payment skip paths are internally consistent in the raw values audited here: downstream payment variables are not observed when visit/drug/hospital/dentist trigger variables are negative.
- Household access reason variables are internally consistent with their count/yes-no trigger variables in the audited rows.
- Health-financing multi-response methods are observed only when paying for health care is very difficult or difficult.
- These checks reduce one blocker, but they do not verify final OOP inclusion policy, old-lek unit conversion, recall-period comparability, total-consumption period, survey design, fieldwork timing, climate-ready geography, or SDG 3.8.2 discretionary-budget inputs.
- Recipe-ready, outcome-ready, and climate-linkage-ready rows from this audit: 0.
- Current decision: `blocked_alb2005_skip_missing_semantics_seen_but_recipe_not_ready`.

## Summary

| Metric | Value | Interpretation |
|---|---:|---|
| alb2005_skip_missing_semantics_rows | 13 | Rows in the ALB_2005 skip/missing semantics audit. |
| alb2005_skip_missing_payment_block_rows | 8 | Person-level visit/payment skip blocks audited. |
| alb2005_skip_missing_access_condition_rows | 4 | Household access reason conditional skip blocks audited. |
| alb2005_skip_missing_financing_multiselect_rows | 1 | Household health-financing method skip blocks audited. |
| alb2005_skip_missing_payment_nonmissing_when_not_triggered_rows | 0 | Payment downstream rows nonmissing when the visit/drug/stay trigger is negative. |
| alb2005_skip_missing_payment_positive_when_not_triggered_rows | 0 | Payment downstream rows positive when the visit/drug/stay trigger is negative. |
| alb2005_skip_missing_payment_all_missing_when_triggered_rows | 0 | Triggered payment rows where every downstream payment variable is missing. |
| alb2005_skip_missing_payment_zero_or_missing_when_triggered_rows | 326 | Triggered payment rows with no positive downstream payment; these are not outcome-ready without zero/missing-code review. |
| alb2005_skip_missing_condition_nonmissing_when_not_triggered_rows | 0 | Conditional reason rows nonmissing when the trigger condition is false. |
| alb2005_skip_missing_condition_missing_when_triggered_rows | 0 | Conditional reason rows missing when the trigger condition is true. |
| alb2005_skip_missing_financing_nonmissing_when_not_triggered_rows | 0 | Health-financing method rows nonmissing when q01 is not difficult/very difficult. |
| alb2005_skip_missing_financing_missing_when_triggered_rows | 0 | Health-financing method rows all missing when q01 is difficult/very difficult. |
| alb2005_skip_missing_questionnaire_oop_rows_observed | 36 | Questionnaire-backed OOP rows observed upstream. |
| alb2005_skip_missing_oop_policy_rows_observed | 11 | OOP aggregation policy stress-test rows observed upstream. |
| alb2005_skip_missing_required_value_key_recipe_ready_observed | 0 | Recipe-ready rows observed upstream. |
| alb2005_skip_missing_timing_verified_rows_observed | 0 | Verified interview-timing rows observed upstream. |
| alb2005_skip_missing_climate_ready_rows_observed | 0 | Climate-linkage-ready rows observed upstream. |
| alb2005_skip_missing_recipe_ready_rows | 0 | Rows promoted to harmonization recipe by this audit; intentionally zero. |
| alb2005_skip_missing_outcome_ready_rows | 0 | Rows promoted to final outcome construction by this audit; intentionally zero. |
| alb2005_skip_missing_climate_linkage_ready_rows | 0 | Rows promoted to climate linkage by this audit; intentionally zero. |
| alb2005_skip_missing_current_decision | blocked_alb2005_skip_missing_semantics_seen_but_recipe_not_ready | Current fail-closed decision for ALB_2005 skip/missing semantics. |

## Skip/Missing Evidence Rows

| audit_family | subdomain | trigger_variable | trigger_positive_rows | trigger_negative_rows | downstream_any_nonmissing_when_not_triggered_rows | dependent_missing_when_triggered_rows | skip_missing_evidence_status |
|---|---|---|---|---|---|---|---|
| person_payment_visit_skip | public_ambulatory_4w | m9a_q12 | 1591 | 14839 | 0 | 0 | raw_skip_path_consistent_no_downstream_values_when_not_triggered |
| person_payment_visit_skip | hospital_outpatient_4w | m9a_q24 | 653 | 15777 | 0 | 0 | raw_skip_path_consistent_no_downstream_values_when_not_triggered |
| person_payment_visit_skip | private_doctor_4w | m9a_q36 | 205 | 16225 | 0 | 0 | raw_skip_path_consistent_no_downstream_values_when_not_triggered |
| person_payment_visit_skip | nurse_paramedic_midwife_4w | m9a_q44 | 210 | 16220 | 0 | 0 | raw_skip_path_consistent_no_downstream_values_when_not_triggered |
| person_payment_visit_skip | popular_doctor_4w | m9a_q52 | 56 | 16374 | 0 | 0 | raw_skip_path_consistent_no_downstream_values_when_not_triggered |
| person_payment_visit_skip | own_drugs_4w | m9a_q60 | 2630 | 13800 | 0 | 0 | raw_skip_path_consistent_no_downstream_values_when_not_triggered |
| person_payment_visit_skip | hospital_stay_12m | m9a_q62 | 710 | 15720 | 0 | 0 | raw_skip_path_consistent_no_downstream_values_when_not_triggered |
| person_payment_visit_skip | dentist_12m | m9a_q74 | 3425 | 13005 | 0 | 0 | raw_skip_path_consistent_no_downstream_values_when_not_triggered |
| household_access_reason_skip | delayed_or_no_help_reason | m9b_q03 | 268 | 3195 | 0 | 0 | raw_conditional_reason_skip_path_consistent |
| household_access_reason_skip | hospital_referral_not_gone_reason | m9b_q05 | 182 | 3281 | 0 | 0 | raw_conditional_reason_skip_path_consistent |
| household_access_reason_skip | refused_health_services_reason | m9b_q07 | 143 | 3697 | 0 | 0 | raw_conditional_reason_skip_path_consistent |
| household_access_reason_skip | medicine_discount_access_reason | m9b_q09 | 2224 | 1616 | 0 | 0 | raw_conditional_reason_skip_path_consistent |
| household_financing_multiselect_skip | raise_money_for_health_care_methods | m9b_q01 | 1289 | 2551 | 0 | 0 | raw_conditional_reason_skip_path_consistent |

## Interpretation

- A zero skip-leak count supports the internal questionnaire-to-raw skip path for the audited variables, but it is not enough to choose an OOP aggregation rule or construct CHE/SDG outcomes.
- Triggered rows with no positive payment can be real zero spending or no-cost care, but they still require explicit missing-code and zero-code review before final financial-protection outcomes.
- Conditional reason variables can support access-barrier outcomes only after the denominator is specified and health need/care-seeking scope is verified.

## Machine-Readable Outputs

- `temp/alb2005_skip_missing_semantics_audit.csv`
- `result/alb2005_skip_missing_semantics_summary.csv`
