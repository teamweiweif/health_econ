# First-Batch Raw Value And Key Audit

Status: raw-value summary layer only. This audit reads observed values and key candidates for first-batch datasets whose raw files are already present. It does not promote a harmonization recipe or create analysis-ready data.

## Summary

| Metric | Value | Interpretation |
|---|---:|---|
| raw_ready_first_batch_dataset_rows | 1 | First-batch datasets with raw files and variables present for value/key audit. |
| raw_ready_first_batch_idnos | ALB_2005_LSMS_v01_M | IDNOs entering the raw value/key audit. |
| first_batch_value_candidate_rows | 513 | Candidate raw variable rows gathered from the harmonization scaffold and first-batch variable template. |
| first_batch_value_audit_rows | 535 | Resolved or blocked long-form value-audit rows. |
| first_batch_value_rows_variable_present | 182 | Value-audit rows whose candidate raw variable was found in the raw schema catalog. |
| first_batch_value_rows_read_ok | 176 | Value-audit rows whose raw values were read successfully. |
| first_batch_value_rows_nonmissing | 176 | Value-audit rows with at least one nonmissing observed raw value. |
| first_batch_false_survey_weight_birth_measure_rows | 6 | Survey-weight candidates rejected because the raw variable is a birth-weight measure. |
| first_batch_auto_harmonization_value_audit_rows | 431 | Fail-closed auto value-audit rows provided to the harmonization gate. |
| first_batch_key_audit_rows | 56 | File-level key/design/geography/timing cardinality audit rows. |
| first_batch_key_rows_read_ok | 56 | Key-audit rows whose raw files were read successfully. |
| first_batch_recipe_promoted_rows | 0 | This audit never promotes a harmonization recipe; manual unit/recall/missing-code/key review is still required. |
| value_audit_status_raw_value_summary_available_manual_interpretation_required | 176 | First-batch raw value-audit status count. |
| value_audit_status_raw_variable_not_found | 353 | First-batch raw value-audit status count. |
| value_audit_status_raw_variable_rejected_false_survey_weight_birth_measure | 6 | First-batch raw value-audit status count. |
| key_audit_status_key_repeats_at_file_row_level_manual_merge_level_review_required | 35 | First-batch raw key-audit status count. |
| key_audit_status_key_summary_available_manual_design_level_review_required | 11 | First-batch raw key-audit status count. |
| key_audit_status_key_unique_at_file_row_level_manual_cross_file_review_required | 10 | First-batch raw key-audit status count. |
| value_read_status_not_attempted | 353 | First-batch raw value read-status count. |
| value_read_status_not_attempted_rejected_false_positive | 6 | First-batch raw value read-status count. |
| value_read_status_read_ok | 176 | First-batch raw value read-status count. |

## Value Audit Status

| Value-audit status | Count |
|---|---:|
| raw_variable_not_found | 353 |
| raw_value_summary_available_manual_interpretation_required | 176 |
| raw_variable_rejected_false_survey_weight_birth_measure | 6 |

## Value Read Status

| Value read status | Count |
|---|---:|
| not_attempted | 353 |
| read_ok | 176 |
| not_attempted_rejected_false_positive | 6 |

## Key Audit Status

| Key-audit status | Count |
|---|---:|
| key_repeats_at_file_row_level_manual_merge_level_review_required | 35 |
| key_summary_available_manual_design_level_review_required | 11 |
| key_unique_at_file_row_level_manual_cross_file_review_required | 10 |

## Value Examples

| idno | concept | harmonized_variable | candidate_raw_variable | resolved_file_name | nonmissing_count | distinct_count | min_value | max_value | top_values | value_audit_status |
|---|---|---|---|---|---|---|---|---|---|---|
| ALB_2005_LSMS_v01_M | care_or_barrier | care_not_sought | m13a_q13b |  |  |  |  |  |  | raw_variable_not_found |
| ALB_2005_LSMS_v01_M | care_or_barrier | care_not_sought | m9b_q05 | Modul_9B_healthb_cl.sav | 3463 | 5 | 1 | 5 | 1.0:3281;2.0:137;3.0:32;5.0:8;4.0:5 | raw_value_summary_available_manual_interpretation_required |
| ALB_2005_LSMS_v01_M | care_or_barrier | care_not_sought | m9b_q06 | Modul_9B_healthb_cl.sav | 182 | 7 | 1 | 7 | 2.0:88;1.0:56;6.0:15;5.0:7;3.0:7;7.0:5;4.0:4 | raw_value_summary_available_manual_interpretation_required |
| ALB_2005_LSMS_v01_M | care_or_barrier | care_not_sought_reason | m9b_q05 | Modul_9B_healthb_cl.sav | 3463 | 5 | 1 | 5 | 1.0:3281;2.0:137;3.0:32;5.0:8;4.0:5 | raw_value_summary_available_manual_interpretation_required |
| ALB_2005_LSMS_v01_M | care_or_barrier | care_not_sought_reason | m9b_q06 | Modul_9B_healthb_cl.sav | 182 | 7 | 1 | 7 | 2.0:88;1.0:56;6.0:15;5.0:7;3.0:7;7.0:5;4.0:4 | raw_value_summary_available_manual_interpretation_required |
| ALB_2005_LSMS_v01_M | care_or_barrier | care_sought | m13a_q13b |  |  |  |  |  |  | raw_variable_not_found |
| ALB_2005_LSMS_v01_M | care_or_barrier | care_sought | m9b_q05 | Modul_9B_healthb_cl.sav | 3463 | 5 | 1 | 5 | 1.0:3281;2.0:137;3.0:32;5.0:8;4.0:5 | raw_value_summary_available_manual_interpretation_required |
| ALB_2005_LSMS_v01_M | care_or_barrier | care_sought | m9b_q06 | Modul_9B_healthb_cl.sav | 182 | 7 | 1 | 7 | 2.0:88;1.0:56;6.0:15;5.0:7;3.0:7;7.0:5;4.0:4 | raw_value_summary_available_manual_interpretation_required |
| ALB_2005_LSMS_v01_M | care_or_barrier | health_facility_distance | m13a_q13b |  |  |  |  |  |  | raw_variable_not_found |
| ALB_2005_LSMS_v01_M | care_or_barrier | health_facility_distance | m9b_q05 | Modul_9B_healthb_cl.sav | 3463 | 5 | 1 | 5 | 1.0:3281;2.0:137;3.0:32;5.0:8;4.0:5 | raw_value_summary_available_manual_interpretation_required |
| ALB_2005_LSMS_v01_M | care_or_barrier | health_facility_distance | m9b_q06 | Modul_9B_healthb_cl.sav | 182 | 7 | 1 | 7 | 2.0:88;1.0:56;6.0:15;5.0:7;3.0:7;7.0:5;4.0:4 | raw_value_summary_available_manual_interpretation_required |
| ALB_2005_LSMS_v01_M | care_or_barrier | reason_not_sought_cost | m13a_q13b |  |  |  |  |  |  | raw_variable_not_found |
| ALB_2005_LSMS_v01_M | care_or_barrier | reason_not_sought_cost | m9b_q05 | Modul_9B_healthb_cl.sav | 3463 | 5 | 1 | 5 | 1.0:3281;2.0:137;3.0:32;5.0:8;4.0:5 | raw_value_summary_available_manual_interpretation_required |
| ALB_2005_LSMS_v01_M | care_or_barrier | reason_not_sought_cost | m9b_q06 | Modul_9B_healthb_cl.sav | 182 | 7 | 1 | 7 | 2.0:88;1.0:56;6.0:15;5.0:7;3.0:7;7.0:5;4.0:4 | raw_value_summary_available_manual_interpretation_required |
| ALB_2005_LSMS_v01_M | care_or_barrier | reason_not_sought_distance | m13a_q13b |  |  |  |  |  |  | raw_variable_not_found |
| ALB_2005_LSMS_v01_M | care_or_barrier | reason_not_sought_distance | m13a_q13b |  |  |  |  |  |  | raw_variable_not_found |
| ALB_2005_LSMS_v01_M | care_or_barrier | reason_not_sought_distance | m9b_q05 | Modul_9B_healthb_cl.sav | 3463 | 5 | 1 | 5 | 1.0:3281;2.0:137;3.0:32;5.0:8;4.0:5 | raw_value_summary_available_manual_interpretation_required |
| ALB_2005_LSMS_v01_M | care_or_barrier | reason_not_sought_distance | m9b_q06 | Modul_9B_healthb_cl.sav | 182 | 7 | 1 | 7 | 2.0:88;1.0:56;6.0:15;5.0:7;3.0:7;7.0:5;4.0:4 | raw_value_summary_available_manual_interpretation_required |
| ALB_2005_LSMS_v01_M | care_or_barrier | reason_not_sought_supply | m13a_q13b |  |  |  |  |  |  | raw_variable_not_found |
| ALB_2005_LSMS_v01_M | care_or_barrier | reason_not_sought_supply | m9b_q05 | Modul_9B_healthb_cl.sav | 3463 | 5 | 1 | 5 | 1.0:3281;2.0:137;3.0:32;5.0:8;4.0:5 | raw_value_summary_available_manual_interpretation_required |

## Key Examples

| idno | lineage_role | resolved_file_name | key_variables | row_count | complete_key_rows | distinct_key_count | duplicate_key_rows | key_audit_status |
|---|---|---|---|---|---|---|---|---|
| ALB_2005_LSMS_v01_M | household_id | Modul_10_fertility_cl.sav | hh;hhid | 573 | 573 | 520 | 53 | key_repeats_at_file_row_level_manual_merge_level_review_required |
| ALB_2005_LSMS_v01_M | person_id | Modul_10_fertility_cl.sav | m10_q00 | 573 | 573 | 3 | 570 | key_repeats_at_file_row_level_manual_merge_level_review_required |
| ALB_2005_LSMS_v01_M | psu_cluster | Modul_10_fertility_cl.sav | psu | 573 | 573 | 308 | 265 | key_summary_available_manual_design_level_review_required |
| ALB_2005_LSMS_v01_M | household_id | Modul_11_check_form_food_cl.sav | hhid | 3840 | 3840 | 3840 | 0 | key_unique_at_file_row_level_manual_cross_file_review_required |
| ALB_2005_LSMS_v01_M | household_id | Modul_12A_non_food_expendituresa_cl.sav | hhid | 57600 | 57600 | 3840 | 53760 | key_repeats_at_file_row_level_manual_merge_level_review_required |
| ALB_2005_LSMS_v01_M | household_id | Modul_12B_non_food_expendituresb_cl.sav | hhid | 69120 | 69120 | 3840 | 65280 | key_repeats_at_file_row_level_manual_merge_level_review_required |
| ALB_2005_LSMS_v01_M | household_id | Modul_12C_non_food_expendituresc_cl.sav | hhid | 69120 | 69120 | 3840 | 65280 | key_repeats_at_file_row_level_manual_merge_level_review_required |
| ALB_2005_LSMS_v01_M | household_id | Modul_13A_dwellinga_cl.sav | hhid | 3840 | 3840 | 3840 | 0 | key_unique_at_file_row_level_manual_cross_file_review_required |
| ALB_2005_LSMS_v01_M | household_id | Modul_13B_dwellingb_cl.sav | M0_Q01;HHID | 3840 | 3840 | 3840 | 0 | key_unique_at_file_row_level_manual_cross_file_review_required |
| ALB_2005_LSMS_v01_M | psu_cluster | Modul_13B_dwellingb_cl.sav | M0_Q00 | 3840 | 3840 | 480 | 3360 | key_summary_available_manual_design_level_review_required |
| ALB_2005_LSMS_v01_M | household_id | Modul_13C_dwellingc1_cl.sav | HHID;M0_Q01 | 96000 | 96000 | 3840 | 92160 | key_repeats_at_file_row_level_manual_merge_level_review_required |
| ALB_2005_LSMS_v01_M | psu_cluster | Modul_13C_dwellingc1_cl.sav | M0_Q00 | 96000 | 96000 | 480 | 95520 | key_summary_available_manual_design_level_review_required |
| ALB_2005_LSMS_v01_M | household_id | Modul_13C_dwellingc2_cl.sav | hhid | 23913 | 23913 | 3816 | 20097 | key_repeats_at_file_row_level_manual_merge_level_review_required |
| ALB_2005_LSMS_v01_M | household_id | Modul_13C_dwellingc3_cl.sav | hhid | 30720 | 30720 | 3840 | 26880 | key_repeats_at_file_row_level_manual_merge_level_review_required |
| ALB_2005_LSMS_v01_M | household_id | Modul_14_social_assistance_cl.sav | hhid | 57600 | 57600 | 3840 | 53760 | key_repeats_at_file_row_level_manual_merge_level_review_required |
| ALB_2005_LSMS_v01_M | household_id | Modul_15_other_income_cl.sav | hhid | 57600 | 57600 | 3840 | 53760 | key_repeats_at_file_row_level_manual_merge_level_review_required |
| ALB_2005_LSMS_v01_M | household_id | Modul_16_social_capital_cl.sav | hhid | 3840 | 3840 | 3840 | 0 | key_unique_at_file_row_level_manual_cross_file_review_required |
| ALB_2005_LSMS_v01_M | household_id | Modul_17_id_agric_household_animals_cl.sav | hhid | 15230 | 15230 | 1523 | 13707 | key_repeats_at_file_row_level_manual_merge_level_review_required |
| ALB_2005_LSMS_v01_M | person_id | Modul_17_id_agric_household_animals_cl.sav | m17b_q8a | 15230 | 15230 | 10 | 15220 | key_repeats_at_file_row_level_manual_merge_level_review_required |
| ALB_2005_LSMS_v01_M | household_id | Modul_17_id_agric_household_cl.sav | hhid | 4631 | 4631 | 1821 | 2810 | key_repeats_at_file_row_level_manual_merge_level_review_required |

## Guardrails

- `raw_value_summary_available_manual_interpretation_required` means the raw values were read, not that the variable is harmonized.
- `key_*_manual_*_review_required` means cardinality was summarized, not that merge keys or survey design variables are verified.
- The generated auto value-audit sidecar sets `ready_for_recipe=0` for every row.
- Do not construct `data/harmonized_household.csv`, outcomes, climate linkage, models, causal estimates, or policy-learning outputs from this audit alone.

## Machine-Readable Outputs

- `temp/first_batch_raw_value_key_audit.csv`
- `temp/first_batch_raw_merge_key_audit.csv`
- `temp/first_batch_harmonization_value_audit_auto.csv`
- `result/first_batch_raw_value_key_summary.csv`
