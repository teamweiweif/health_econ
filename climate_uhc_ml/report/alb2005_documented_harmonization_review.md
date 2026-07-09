# ALB_2005 Documented Harmonization Review

Status: documentation-backed review only. This audit uses inspected ALB_2005 raw SPSS metadata and observed values to identify plausible future harmonization candidates and explicit false positives. It does not create or promote a harmonization recipe.

## Summary

| Metric | Value | Interpretation |
|---|---:|---|
| alb2005_documented_evidence_rows | 44 | Rows in the ALB_2005 documented harmonization review. |
| alb2005_rows_with_observed_value_summaries | 41 | Rows where raw values were summarized from inspected SPSS files. |
| alb2005_documentation_supported_rows | 39 | Rows with documentation/schema support but still requiring manual review. |
| alb2005_future_recipe_candidate_rows | 36 | Rows that may enter a future recipe only after manual key/unit/recall/skip review. |
| alb2005_false_positive_rows | 2 | Rows explicitly rejected as false-positive harmonization candidates. |
| alb2005_timing_or_geography_blocker_rows | 3 | Rows blocking climate linkage because timing or geography evidence is insufficient. |
| alb2005_oop_candidate_rows | 16 | Candidate OOP payment variables requiring aggregation/recall review. |
| alb2005_questionnaire_xls_reader_available | 1 | Whether a trusted legacy XLS reader is available for questionnaire extraction. |
| alb2005_recipe_ready_rows | 0 | This review does not promote any harmonization recipe rows. |
| alb2005_current_decision | not_ready_for_verified_recipe | ALB_2005 remains blocked pending timing/geography, OOP aggregation, units, skip patterns, and merge-key review. |

## Documentation Support Status

| Status | Count |
|---|---:|
| documentation_supported_aggregation_recall_review_required | 16 |
| documentation_supported_key_review_required | 6 |
| documentation_supported_need_definition_review_required | 4 |
| documentation_supported_shock_module_review_required | 3 |
| documentation_supported_referral_nonuse_review_required | 2 |
| documentation_supported_value_label_review_required | 2 |
| documentation_supported_not_direct_household_total | 2 |
| blocked_false_positive | 2 |
| documentation_supported_design_review_required | 2 |
| documentation_supported_unit_period_review_required | 1 |
| documentation_reader_available | 1 |
| documentation_supported_weak_geography_coverage_review_required | 1 |
| blocked_no_gps_coordinates | 1 |
| blocked_missing_timing | 1 |

## Recipe Decision

| Decision | Count |
|---|---:|
| candidate_for_future_recipe_after_aggregation_recall_skip_review | 16 |
| candidate_for_future_recipe_after_skip_pattern_denominator_review | 6 |
| candidate_for_future_recipe_after_manual_key_review | 6 |
| candidate_for_future_mechanism_or_covariate_review | 3 |
| candidate_for_future_recipe_after_value_label_and_denominator_review | 2 |
| not_recipe_ready_per_capita_or_component_review_required | 2 |
| blocked_false_positive | 2 |
| candidate_for_future_recipe_after_survey_design_review | 2 |
| candidate_for_future_recipe_after_unit_period_review | 1 |
| not_recipe_ready_questionnaire_extraction_pending | 1 |
| not_recipe_ready_missing_geography_coverage_review | 1 |
| not_recipe_ready_no_gps | 1 |
| not_recipe_ready_missing_timing | 1 |

## Candidate Rows Requiring Manual Review

| evidence_domain | harmonized_variable | source_file | raw_variable | raw_label | nonmissing_count | distinct_count | recipe_decision |
|---|---|---|---|---|---|---|---|
| care_access | care_not_sought | Modul_9B_healthb_cl.sav | m9b_q05 | Times HH Member has been referred to hospital but not gone | 3463 | 5 | candidate_for_future_recipe_after_skip_pattern_denominator_review |
| care_access | care_not_sought | Modul_9B_healthb_cl.sav | m9b_q06 | Reason for not going to Hospital | 182 | 7 | candidate_for_future_recipe_after_skip_pattern_denominator_review |
| care_access | reason_not_sought_cost | Modul_9B_healthb_cl.sav | m9b_q06 | Reason for not going to Hospital | 182 | 7 | candidate_for_future_recipe_after_value_label_and_denominator_review |
| care_access | reason_not_sought_distance | Modul_9B_healthb_cl.sav | m9b_q06 | Reason for not going to Hospital | 182 | 7 | candidate_for_future_recipe_after_value_label_and_denominator_review |
| consumption | total_consumption | poverty.sav | totcons | Household total consumption | 3638 | 3638 | candidate_for_future_recipe_after_unit_period_review |
| health_need | illness_or_injury_need | Modul_9A_healtha_cl.sav | m9a_q01 | Suffers from chronic illness or disabilility | 16430 | 2 | candidate_for_future_recipe_after_skip_pattern_denominator_review |
| health_need | illness_or_injury_need | Modul_9A_healtha_cl.sav | m9a_q03 | Illness diagnosed by a profesional | 2497 | 2 | candidate_for_future_recipe_after_skip_pattern_denominator_review |
| health_need | illness_or_injury_need | Modul_9A_healtha_cl.sav | m9a_q04 | Name of illness/disease | 2474 | 12 | candidate_for_future_recipe_after_skip_pattern_denominator_review |
| health_need | illness_or_injury_need | Modul_9A_healtha_cl.sav | m9a_q07 | Has had sudden illness in past 4 weeks | 16430 | 2 | candidate_for_future_recipe_after_skip_pattern_denominator_review |
| identity | hhid | Modul_11_check_form_food_cl.sav | hh | Household ID | 3840 | 12 | candidate_for_future_recipe_after_manual_key_review |
| identity | hhid | Modul_11_check_form_food_cl.sav | hhid | household identifier | 3840 | 3840 | candidate_for_future_recipe_after_manual_key_review |
| identity | hhid | Modul_11_check_form_food_cl.sav | psu | PSU | 3840 | 480 | candidate_for_future_recipe_after_manual_key_review |
| identity | hhid | filters_cl.sav | HHID | household identifier | 3840 | 3840 | candidate_for_future_recipe_after_manual_key_review |
| identity | hhid | filters_cl.sav | M0_Q00 | PSU | 3840 | 480 | candidate_for_future_recipe_after_manual_key_review |
| identity | hhid | filters_cl.sav | M0_Q01 | Household ID | 3840 | 12 | candidate_for_future_recipe_after_manual_key_review |
| oop_health_expenditure | oop_health_expenditure | Modul_9A_healtha_cl.sav | m9a_q20 | Amount paid for medicines | 1482 | 121 | candidate_for_future_recipe_after_aggregation_recall_skip_review |
| oop_health_expenditure | oop_health_expenditure | Modul_9A_healtha_cl.sav | m9a_q22 | Amount paid for lab work | 1591 | 33 | candidate_for_future_recipe_after_aggregation_recall_skip_review |
| oop_health_expenditure | oop_health_expenditure | Modul_9A_healtha_cl.sav | m9a_q32 | Amount paid for medicines | 561 | 87 | candidate_for_future_recipe_after_aggregation_recall_skip_review |
| oop_health_expenditure | oop_health_expenditure | Modul_9A_healtha_cl.sav | m9a_q34 | Amount paid for laboratory work | 653 | 32 | candidate_for_future_recipe_after_aggregation_recall_skip_review |
| oop_health_expenditure | oop_health_expenditure | Modul_9A_healtha_cl.sav | m9a_q41 | Amount paid for medicines | 205 | 46 | candidate_for_future_recipe_after_aggregation_recall_skip_review |
| oop_health_expenditure | oop_health_expenditure | Modul_9A_healtha_cl.sav | m9a_q42 | Amount paid for lab work | 205 | 24 | candidate_for_future_recipe_after_aggregation_recall_skip_review |
| oop_health_expenditure | oop_health_expenditure | Modul_9A_healtha_cl.sav | m9a_q49 | Amount paid for medicines | 210 | 26 | candidate_for_future_recipe_after_aggregation_recall_skip_review |

## Explicit False Positives

| harmonized_variable | source_file | raw_variable | raw_label | recipe_decision | blocking_reason |
|---|---|---|---|---|---|
| household_weight_or_person_weight | Modul_10_fertility_cl.sav | m10_q13a | Weight at birth - Kgs | blocked_false_positive | birth-weight variables are child health/fertility measures and are not survey design weights |
| household_weight_or_person_weight | Modul_10_fertility_cl.sav | m10_q13b | Weight at birth - Grms | blocked_false_positive | birth-weight variables are child health/fertility measures and are not survey design weights |

## Timing And Geography Blockers

| evidence_domain | harmonized_variable | source_file | raw_variable | nonmissing_count | distinct_count | recipe_decision | blocking_reason |
|---|---|---|---|---|---|---|---|
| geography | admin1_or_admin2 | filters.sav | P11_Q5B | 329 | 28 | not_recipe_ready_missing_geography_coverage_review | district code exists in filters.sav but coverage and merge path to all households require review; no GPS is present |
| geography | latitude_longitude |  |  |  |  | not_recipe_ready_no_gps | no household or cluster latitude/longitude variable has been found in inspected ALB_2005 raw files |
| survey_timing | survey_month_or_interview_date |  |  |  |  | not_recipe_ready_missing_timing | no raw interview month/date variable has been verified for ALB_2005 |

## Interpretation

- `weight_retro` and `totcons` are credible documented candidates for future review, not recipe-ready variables.
- The `m9a_*` payment variables are documented OOP candidates, but aggregation, recall period, care context, skip patterns, and missing-code semantics are unresolved.
- `m9b_q06` supports cost and distance/access-barrier review only after its referral/nonuse denominator is verified.
- `P11_Q5B` is a district-code candidate, but it is not GPS and its coverage/merge path must be verified before climate linkage.
- No interview month/date variable is currently verified for ALB_2005, so climate exposure timing remains blocked.
- `m10_q13a` and `m10_q13b` are birth-weight variables and must not be used as household/person survey weights.

## Machine-Readable Outputs

- `temp/alb2005_documented_variable_evidence.csv`
- `result/alb2005_documented_harmonization_summary.csv`
