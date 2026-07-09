# ALB_2012 Questionnaire Timing Field Audit

Status: questionnaire/raw-gap audit only. This report reads the ALB_2012 English questionnaire workbooks and documents control-sheet timing fields. It also checks the raw SPSS variable catalog for matching household interview timing values. It does not write `data/`, does not construct climate exposures, and does not promote ALB_2012 to climate linkage.

## Summary

| Metric | Value | Interpretation |
|---|---:|---|
| alb2012_questionnaire_timing_workbooks_scanned | 2 | ALB_2012 questionnaire workbooks scanned for control-sheet timing fields. |
| alb2012_questionnaire_timing_field_rows | 29 | Questionnaire cells documenting date, begin/end, visit, status, or remarks fields. |
| alb2012_questionnaire_timing_visit_rows | 6 | Questionnaire cells documenting VISIT_1/VISIT_2/VISIT_3 control rows. |
| alb2012_questionnaire_timing_date_begin_end_status_rows | 19 | Questionnaire cells documenting date, begin/end, status, or status-code fields. |
| alb2012_questionnaire_timing_raw_gap_rows | 12 | ALB_2012 raw SPSS catalog rows with timing-like terms but not verified interview timing. |
| alb2012_questionnaire_timing_raw_control_candidate_rows | 0 | Raw SPSS rows with interview/fieldwork/survey timing wording requiring review. |
| alb2012_questionnaire_timing_raw_verified_interview_timing_rows | 0 | Verified household interview month/date values in raw SPSS modules. |
| alb2012_questionnaire_timing_previous_exhaustive_verified_interview_rows | 0 | Verified interview timing rows reported by the exhaustive raw timing/geography audit. |
| alb2012_questionnaire_timing_previous_exhaustive_climate_ready_rows | 0 | Climate-linkage-ready rows reported by the exhaustive raw timing/geography audit. |
| alb2012_questionnaire_timing_climate_linkage_ready_rows | 0 | Rows ready for climate-linkage input promotion after this questionnaire timing audit. |
| alb2012_questionnaire_timing_current_decision | blocked_questionnaire_timing_fields_not_in_raw_household_values | Current fail-closed decision for ALB_2012 questionnaire timing evidence. |

## Questionnaire Timing Field Evidence

| source_workbook | sheet_name | row_number | column_number | cell_text | evidence_role | promotion_status |
|---|---|---|---|---|---|---|
| LSMS_12  PART 1 Eng.xlsx | CONTROL SHEET | 2 | 2 | DATE | date_field_or_format | not_raw_household_value_not_ready_for_climate_linkage |
| LSMS_12  PART 1 Eng.xlsx | CONTROL SHEET | 2 | 3 | BEGIN | begin_end_time_field | not_raw_household_value_not_ready_for_climate_linkage |
| LSMS_12  PART 1 Eng.xlsx | CONTROL SHEET | 2 | 4 | END | begin_end_time_field | not_raw_household_value_not_ready_for_climate_linkage |
| LSMS_12  PART 1 Eng.xlsx | CONTROL SHEET | 2 | 5 | STATUS | completion_status_field_or_code | not_raw_household_value_not_ready_for_climate_linkage |
| LSMS_12  PART 1 Eng.xlsx | CONTROL SHEET | 2 | 6 | REMARKS | remarks_field | not_raw_household_value_not_ready_for_climate_linkage |
| LSMS_12  PART 1 Eng.xlsx | CONTROL SHEET | 2 | 10 | Status codes | status_code_label | not_raw_household_value_not_ready_for_climate_linkage |
| LSMS_12  PART 1 Eng.xlsx | CONTROL SHEET | 3 | 2 | Day/MM/YY | date_field_or_format | not_raw_household_value_not_ready_for_climate_linkage |
| LSMS_12  PART 1 Eng.xlsx | CONTROL SHEET | 4 | 1 | VISIT_1 | visit_control_row | not_raw_household_value_not_ready_for_climate_linkage |
| LSMS_12  PART 1 Eng.xlsx | CONTROL SHEET | 4 | 10 | 1. Complete | completion_status_field_or_code | not_raw_household_value_not_ready_for_climate_linkage |
| LSMS_12  PART 1 Eng.xlsx | CONTROL SHEET | 5 | 1 | VISIT_2 | visit_control_row | not_raw_household_value_not_ready_for_climate_linkage |
| LSMS_12  PART 1 Eng.xlsx | CONTROL SHEET | 5 | 10 | 2. Incomplete, must return | completion_status_field_or_code | not_raw_household_value_not_ready_for_climate_linkage |
| LSMS_12  PART 1 Eng.xlsx | CONTROL SHEET | 6 | 1 | VISIT_3 | visit_control_row | not_raw_household_value_not_ready_for_climate_linkage |
| LSMS_12  PART 1 Eng.xlsx | CONTROL SHEET | 6 | 10 | 3. Not contacted | completion_status_field_or_code | not_raw_household_value_not_ready_for_climate_linkage |
| LSMS_12  PART 1 Eng.xlsx | CONTROL SHEET | 7 | 10 | 4. Refused | completion_status_field_or_code | not_raw_household_value_not_ready_for_climate_linkage |
| LSMS_12  PART 2 Eng.xlsx | SECTION 2 & PANEL INFORMATION | 3 | 2 | Enumerator: Please fill this page during your second visit to the household: | second_visit_instruction | not_raw_household_value_not_ready_for_climate_linkage |
| LSMS_12  PART 2 Eng.xlsx | SECTION 2 & PANEL INFORMATION | 7 | 2 | please ask them for contact infromation during your second visit. | second_visit_instruction | not_raw_household_value_not_ready_for_climate_linkage |
| LSMS_12  PART 2 Eng.xlsx | SECTION 2 & PANEL INFORMATION | 33 | 12 | Status codes | status_code_label | not_raw_household_value_not_ready_for_climate_linkage |
| LSMS_12  PART 2 Eng.xlsx | SECTION 2 & PANEL INFORMATION | 35 | 3 | DATE | date_field_or_format | not_raw_household_value_not_ready_for_climate_linkage |
| LSMS_12  PART 2 Eng.xlsx | SECTION 2 & PANEL INFORMATION | 35 | 4 | BEGIN | begin_end_time_field | not_raw_household_value_not_ready_for_climate_linkage |
| LSMS_12  PART 2 Eng.xlsx | SECTION 2 & PANEL INFORMATION | 35 | 5 | END | begin_end_time_field | not_raw_household_value_not_ready_for_climate_linkage |
| LSMS_12  PART 2 Eng.xlsx | SECTION 2 & PANEL INFORMATION | 35 | 6 | STATUS | completion_status_field_or_code | not_raw_household_value_not_ready_for_climate_linkage |
| LSMS_12  PART 2 Eng.xlsx | SECTION 2 & PANEL INFORMATION | 35 | 7 | REMARKS | remarks_field | not_raw_household_value_not_ready_for_climate_linkage |
| LSMS_12  PART 2 Eng.xlsx | SECTION 2 & PANEL INFORMATION | 35 | 12 | 1. Complete | completion_status_field_or_code | not_raw_household_value_not_ready_for_climate_linkage |
| LSMS_12  PART 2 Eng.xlsx | SECTION 2 & PANEL INFORMATION | 36 | 2 | VISIT_1 | visit_control_row | not_raw_household_value_not_ready_for_climate_linkage |
| LSMS_12  PART 2 Eng.xlsx | SECTION 2 & PANEL INFORMATION | 36 | 12 | 2. Incomplete, must return | completion_status_field_or_code | not_raw_household_value_not_ready_for_climate_linkage |
| LSMS_12  PART 2 Eng.xlsx | SECTION 2 & PANEL INFORMATION | 37 | 2 | VISIT_2 | visit_control_row | not_raw_household_value_not_ready_for_climate_linkage |
| LSMS_12  PART 2 Eng.xlsx | SECTION 2 & PANEL INFORMATION | 37 | 12 | 3. Not contacted | completion_status_field_or_code | not_raw_household_value_not_ready_for_climate_linkage |
| LSMS_12  PART 2 Eng.xlsx | SECTION 2 & PANEL INFORMATION | 38 | 2 | VISIT_3 | visit_control_row | not_raw_household_value_not_ready_for_climate_linkage |
| LSMS_12  PART 2 Eng.xlsx | SECTION 2 & PANEL INFORMATION | 38 | 12 | 4. Refused | completion_status_field_or_code | not_raw_household_value_not_ready_for_climate_linkage |

## Questionnaire Evidence Roles

| evidence_role | Rows |
|---|---:|
| begin_end_time_field | 4 |
| completion_status_field_or_code | 10 |
| date_field_or_format | 3 |
| remarks_field | 2 |
| second_visit_instruction | 2 |
| status_code_label | 2 |
| visit_control_row | 6 |

## Raw SPSS Timing Gap Evidence

| source_path | variable_name | variable_label | raw_gap_role | promotion_status |
|---|---|---|---|---|
| temp\raw_extracted\lsms_2012_eng_7631729d2caf\LSMS 2012_eng\Data_LSMS 2012\Modul_10_Fertility.sav | M10_Q09 | Period of first prenatal visit | not_interview_timing_health_or_module_visit_context | raw_household_interview_timing_not_verified |
| temp\raw_extracted\lsms_2012_eng_7631729d2caf\LSMS 2012_eng\Data_LSMS 2012\Modul_1A_householdroster.sav | m1a_q04 | Date of Birth | not_interview_timing_birth_or_fertility_context | raw_household_interview_timing_not_verified |
| temp\raw_extracted\lsms_2012_eng_7631729d2caf\LSMS 2012_eng\Data_LSMS 2012\Modul_1A_householdroster.sav | m1a_q06 | Marital Status | status_keyword_not_verified_interview_timing | raw_household_interview_timing_not_verified |
| temp\raw_extracted\lsms_2012_eng_7631729d2caf\LSMS 2012_eng\Data_LSMS 2012\Modul_4A_labor.sav | M4A_Q11 | Status began 12 months ago | not_interview_timing_event_history_context | raw_household_interview_timing_not_verified |
| temp\raw_extracted\lsms_2012_eng_7631729d2caf\LSMS 2012_eng\Data_LSMS 2012\Modul_4A_labor.sav | M4A_Q16 | Status began 12 months ago | not_interview_timing_event_history_context | raw_household_interview_timing_not_verified |
| temp\raw_extracted\lsms_2012_eng_7631729d2caf\LSMS 2012_eng\Data_LSMS 2012\modul_9A_health.sav | M9A_Q14 | Visit public ambulatory last month | not_interview_timing_health_or_module_visit_context | raw_household_interview_timing_not_verified |
| temp\raw_extracted\lsms_2012_eng_7631729d2caf\LSMS 2012_eng\Data_LSMS 2012\modul_9A_health.sav | M9A_Q26 | Visit a hospital | not_interview_timing_health_or_module_visit_context | raw_household_interview_timing_not_verified |
| temp\raw_extracted\lsms_2012_eng_7631729d2caf\LSMS 2012_eng\Data_LSMS 2012\modul_9A_health.sav | M9A_Q38 | Visit private doctor | not_interview_timing_health_or_module_visit_context | raw_household_interview_timing_not_verified |
| temp\raw_extracted\lsms_2012_eng_7631729d2caf\LSMS 2012_eng\Data_LSMS 2012\modul_9A_health.sav | M9A_Q46 | Visit private nurse/paramedic | not_interview_timing_health_or_module_visit_context | raw_household_interview_timing_not_verified |
| temp\raw_extracted\lsms_2012_eng_7631729d2caf\LSMS 2012_eng\Data_LSMS 2012\modul_9A_health.sav | M9A_Q54 | Visit popular doctor/alternative medicine | not_interview_timing_health_or_module_visit_context | raw_household_interview_timing_not_verified |
| temp\raw_extracted\lsms_2012_eng_7631729d2caf\LSMS 2012_eng\Data_LSMS 2012\modul_9A_health.sav | M9A_Q77 | Visit dentist | not_interview_timing_health_or_module_visit_context | raw_household_interview_timing_not_verified |
| temp\raw_extracted\lsms_2012_eng_7631729d2caf\LSMS 2012_eng\Data_LSMS 2012\modul_9A_health.sav | M9A_Q86 | Status of license | status_keyword_not_verified_interview_timing | raw_household_interview_timing_not_verified |

## Raw Gap Roles

| raw_gap_role | Rows |
|---|---:|
| not_interview_timing_birth_or_fertility_context | 1 |
| not_interview_timing_event_history_context | 2 |
| not_interview_timing_health_or_module_visit_context | 7 |
| status_keyword_not_verified_interview_timing | 2 |

## Interpretation

- The questionnaire control sheets document `DATE`, `BEGIN`, `END`, `STATUS`, `REMARKS`, and repeated visit rows.
- These cells show that fieldwork timing and visit status were intended on the forms, but they are not household-level raw timing values.
- The raw SPSS module catalog still does not verify household interview month/date values.
- Birth dates, recall windows, health-service visit counts, migration/residence histories, and other event dates cannot define pre-interview climate exposure windows.
- ALB_2012 remains blocked for climate linkage until raw household timing values or official fieldwork-period metadata can be connected to household geography.

## Machine-Readable Outputs

- `temp/alb2012_questionnaire_timing_field_audit.csv`
- `temp/alb2012_questionnaire_timing_raw_gap_audit.csv`
- `result/alb2012_questionnaire_timing_field_summary.csv`
