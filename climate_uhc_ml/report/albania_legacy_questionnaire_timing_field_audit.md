# Albania Legacy Questionnaire Timing Field Audit

Status: questionnaire/raw-gap audit only. This report reads ALB_2002, ALB_2005, and ALB_2008 legacy `.xls` questionnaire control or panel-information sheets and documents timing/control field evidence. It also checks the raw SPSS variable catalog for matching household interview timing values. It does not write `data/`, does not construct climate exposures, and does not promote any legacy Albania wave to climate linkage.

## Summary

| Metric | Value | Interpretation |
|---|---:|---|
| albania_legacy_questionnaire_timing_workbooks_scanned | 5 | Legacy ALB_2002/2005/2008 questionnaire workbooks opened for timing/control content review. |
| albania_legacy_questionnaire_timing_sheets_scanned | 6 | Target control or panel-information sheets scanned. |
| albania_legacy_questionnaire_timing_target_sheets_missing | 0 | Expected target sheets not found in opened workbooks. |
| albania_legacy_questionnaire_timing_sheet_read_errors | 0 | Target sheets that could not be read. |
| albania_legacy_questionnaire_timing_field_rows | 83 | Questionnaire cells documenting date, begin/end, visit, status, contact, or remarks fields. |
| albania_legacy_questionnaire_timing_visit_rows | 18 | Questionnaire cells documenting VISIT_1/VISIT_2/VISIT_3 control rows. |
| albania_legacy_questionnaire_timing_second_visit_instruction_rows | 5 | Questionnaire cells documenting second-visit instructions. |
| albania_legacy_questionnaire_timing_date_begin_end_status_rows | 41 | Questionnaire cells documenting date, begin/end, status, or status-code fields. |
| albania_legacy_questionnaire_timing_raw_gap_rows | 58 | ALB_2002/2005/2008 raw SPSS catalog rows with timing-like terms or verified ALB_2002 timing fields. |
| albania_legacy_questionnaire_timing_raw_verified_variable_rows | 7 | ALB_2002 raw catalog variables classified as verified interview timing fields. |
| albania_legacy_questionnaire_timing_raw_control_candidate_rows | 0 | Raw SPSS rows with interview/fieldwork/survey timing wording requiring review. |
| alb2002_legacy_questionnaire_timing_raw_verified_interview_timing_rows | 3599 | ALB_2002 household rows with raw interview date from the existing household-core audit. |
| alb2005_legacy_questionnaire_timing_raw_verified_interview_timing_rows | 0 | ALB_2005 verified raw household interview timing rows from the exhaustive timing/geography audit. |
| alb2008_legacy_questionnaire_timing_raw_verified_interview_timing_rows | 0 | ALB_2008 verified raw household interview timing rows from the exhaustive timing/geography audit. |
| albania_legacy_questionnaire_timing_raw_verified_interview_timing_waves | 1 | Legacy Albania waves with verified raw household interview timing rows. |
| albania_legacy_questionnaire_timing_raw_verified_interview_timing_rows | 3599 | Total verified raw household interview timing rows already observed across ALB_2002/2005/2008. |
| albania_legacy_questionnaire_timing_climate_linkage_ready_rows | 0 | Rows ready for climate-linkage input promotion after this questionnaire timing audit. |
| albania_legacy_questionnaire_timing_current_decision | blocked_legacy_questionnaire_form_design_not_sufficient_for_climate_linkage | Current fail-closed decision for legacy questionnaire timing/control evidence. |

## Questionnaire Timing Field Evidence

| idno | source_workbook | sheet_name | row_number | column_number | cell_text | evidence_role | promotion_status |
|---|---|---|---|---|---|---|---|
| ALB_2002_LSMS_v01_M | LSMS02_Questionnaire.xls | CONTROL SHEET | 2 | 2 | DATE | date_field_or_format | form_design_only_not_raw_household_value |
| ALB_2002_LSMS_v01_M | LSMS02_Questionnaire.xls | CONTROL SHEET | 2 | 3 | BEGIN | begin_end_time_field | form_design_only_not_raw_household_value |
| ALB_2002_LSMS_v01_M | LSMS02_Questionnaire.xls | CONTROL SHEET | 2 | 4 | END | begin_end_time_field | form_design_only_not_raw_household_value |
| ALB_2002_LSMS_v01_M | LSMS02_Questionnaire.xls | CONTROL SHEET | 2 | 5 | STATUS | completion_status_field_or_code | form_design_only_not_raw_household_value |
| ALB_2002_LSMS_v01_M | LSMS02_Questionnaire.xls | CONTROL SHEET | 2 | 6 | REMARKS | remarks_field | form_design_only_not_raw_household_value |
| ALB_2002_LSMS_v01_M | LSMS02_Questionnaire.xls | CONTROL SHEET | 2 | 11 | Status codes | status_code_label | form_design_only_not_raw_household_value |
| ALB_2002_LSMS_v01_M | LSMS02_Questionnaire.xls | CONTROL SHEET | 3 | 1 | VISIT_1 | visit_control_row | form_design_only_not_raw_household_value |
| ALB_2002_LSMS_v01_M | LSMS02_Questionnaire.xls | CONTROL SHEET | 3 | 11 | 1. Complete | completion_status_field_or_code | form_design_only_not_raw_household_value |
| ALB_2002_LSMS_v01_M | LSMS02_Questionnaire.xls | CONTROL SHEET | 4 | 1 | VISIT_2 | visit_control_row | form_design_only_not_raw_household_value |
| ALB_2002_LSMS_v01_M | LSMS02_Questionnaire.xls | CONTROL SHEET | 4 | 11 | 2. Incomplete, must return | completion_status_field_or_code | form_design_only_not_raw_household_value |
| ALB_2002_LSMS_v01_M | LSMS02_Questionnaire.xls | CONTROL SHEET | 5 | 1 | VISIT_3 | visit_control_row | form_design_only_not_raw_household_value |
| ALB_2002_LSMS_v01_M | LSMS02_Questionnaire.xls | SECTION 2 & PANEL INFORMATION | 3 | 2 | Enumerators: Please fill this page during the second visit to the household: | second_visit_instruction | form_design_only_not_raw_household_value |
| ALB_2002_LSMS_v01_M | LSMS02_Questionnaire.xls | SECTION 2 & PANEL INFORMATION | 10 | 2 | would like to contact you again in the coming year.. | fieldwork_contact_instruction | form_design_only_not_raw_household_value |
| ALB_2002_LSMS_v01_M | LSMS02_Questionnaire.xls | SECTION 2 & PANEL INFORMATION | 13 | 2 | This information will help us contact you in the future: | fieldwork_contact_instruction | form_design_only_not_raw_household_value |
| ALB_2002_LSMS_v01_M | LSMS02_Questionnaire.xls | SECTION 2 & PANEL INFORMATION | 18 | 2 | And would it also be possible to have an alternative address or telephone number to contact you in case of ... | fieldwork_contact_instruction | form_design_only_not_raw_household_value |
| ALB_2002_LSMS_v01_M | LSMS02_Questionnaire.xls | SECTION 2 & PANEL INFORMATION | 32 | 3 | DATE | date_field_or_format | form_design_only_not_raw_household_value |
| ALB_2002_LSMS_v01_M | LSMS02_Questionnaire.xls | SECTION 2 & PANEL INFORMATION | 32 | 4 | BEGIN | begin_end_time_field | form_design_only_not_raw_household_value |
| ALB_2002_LSMS_v01_M | LSMS02_Questionnaire.xls | SECTION 2 & PANEL INFORMATION | 32 | 6 | STATUS | completion_status_field_or_code | form_design_only_not_raw_household_value |
| ALB_2002_LSMS_v01_M | LSMS02_Questionnaire.xls | SECTION 2 & PANEL INFORMATION | 32 | 7 | REMARKS | remarks_field | form_design_only_not_raw_household_value |
| ALB_2002_LSMS_v01_M | LSMS02_Questionnaire.xls | SECTION 2 & PANEL INFORMATION | 32 | 12 | Status codes | status_code_label | form_design_only_not_raw_household_value |
| ALB_2002_LSMS_v01_M | LSMS02_Questionnaire.xls | SECTION 2 & PANEL INFORMATION | 33 | 2 | VISIT_1 | visit_control_row | form_design_only_not_raw_household_value |
| ALB_2002_LSMS_v01_M | LSMS02_Questionnaire.xls | SECTION 2 & PANEL INFORMATION | 34 | 2 | VISIT_2 | visit_control_row | form_design_only_not_raw_household_value |
| ALB_2002_LSMS_v01_M | LSMS02_Questionnaire.xls | SECTION 2 & PANEL INFORMATION | 34 | 12 | 1. Complete | completion_status_field_or_code | form_design_only_not_raw_household_value |
| ALB_2002_LSMS_v01_M | LSMS02_Questionnaire.xls | SECTION 2 & PANEL INFORMATION | 35 | 2 | VISIT_3 | visit_control_row | form_design_only_not_raw_household_value |
| ALB_2002_LSMS_v01_M | LSMS02_Questionnaire.xls | SECTION 2 & PANEL INFORMATION | 35 | 12 | 2. Incomplete, must return | completion_status_field_or_code | form_design_only_not_raw_household_value |
| ALB_2005_LSMS_v01_M | LSMS05_questionnaire_part1.xls | CONTROL SHEET | 2 | 2 | DATE | date_field_or_format | form_design_only_not_raw_household_value |
| ALB_2005_LSMS_v01_M | LSMS05_questionnaire_part1.xls | CONTROL SHEET | 2 | 3 | BEGIN | begin_end_time_field | form_design_only_not_raw_household_value |
| ALB_2005_LSMS_v01_M | LSMS05_questionnaire_part1.xls | CONTROL SHEET | 2 | 4 | END | begin_end_time_field | form_design_only_not_raw_household_value |
| ALB_2005_LSMS_v01_M | LSMS05_questionnaire_part1.xls | CONTROL SHEET | 2 | 5 | STATUS | completion_status_field_or_code | form_design_only_not_raw_household_value |
| ALB_2005_LSMS_v01_M | LSMS05_questionnaire_part1.xls | CONTROL SHEET | 2 | 6 | REMARKS | remarks_field | form_design_only_not_raw_household_value |
| ALB_2005_LSMS_v01_M | LSMS05_questionnaire_part1.xls | CONTROL SHEET | 2 | 11 | Status codes | status_code_label | form_design_only_not_raw_household_value |
| ALB_2005_LSMS_v01_M | LSMS05_questionnaire_part1.xls | CONTROL SHEET | 3 | 1 | VISIT_1 | visit_control_row | form_design_only_not_raw_household_value |
| ALB_2005_LSMS_v01_M | LSMS05_questionnaire_part1.xls | CONTROL SHEET | 3 | 11 | 1. Complete | completion_status_field_or_code | form_design_only_not_raw_household_value |
| ALB_2005_LSMS_v01_M | LSMS05_questionnaire_part1.xls | CONTROL SHEET | 4 | 1 | VISIT_2 | visit_control_row | form_design_only_not_raw_household_value |
| ALB_2005_LSMS_v01_M | LSMS05_questionnaire_part1.xls | CONTROL SHEET | 4 | 11 | 2. Incomplete, must return | completion_status_field_or_code | form_design_only_not_raw_household_value |
| ALB_2005_LSMS_v01_M | LSMS05_questionnaire_part1.xls | CONTROL SHEET | 5 | 1 | VISIT_3 | visit_control_row | form_design_only_not_raw_household_value |
| ALB_2005_LSMS_v01_M | LSMS05_Questionnaire_part2.xls | SECTION 2 & PANEL INFORMATION | 3 | 2 | Enumerator: Please fill this page during your second visit to the household: | second_visit_instruction | form_design_only_not_raw_household_value |
| ALB_2005_LSMS_v01_M | LSMS05_Questionnaire_part2.xls | SECTION 2 & PANEL INFORMATION | 6 | 2 | We have to keep in contact with these households. Since the household may move from this dwelling, | fieldwork_contact_instruction | form_design_only_not_raw_household_value |
| ALB_2005_LSMS_v01_M | LSMS05_Questionnaire_part2.xls | SECTION 2 & PANEL INFORMATION | 7 | 2 | please ask them for contact infromation during your second visit. | second_visit_instruction | form_design_only_not_raw_household_value |
| ALB_2005_LSMS_v01_M | LSMS05_Questionnaire_part2.xls | SECTION 2 & PANEL INFORMATION | 13 | 2 | For this reason we may wish to contact you again in the coming year.. | fieldwork_contact_instruction | form_design_only_not_raw_household_value |
| ALB_2005_LSMS_v01_M | LSMS05_Questionnaire_part2.xls | SECTION 2 & PANEL INFORMATION | 16 | 2 | Some information will help us contact you in the future: | fieldwork_contact_instruction | form_design_only_not_raw_household_value |
| ALB_2005_LSMS_v01_M | LSMS05_Questionnaire_part2.xls | SECTION 2 & PANEL INFORMATION | 21 | 2 | And would it also be possible to have an alternative address or telephone of a relative number to contact y... | fieldwork_contact_instruction | form_design_only_not_raw_household_value |
| ALB_2005_LSMS_v01_M | LSMS05_Questionnaire_part2.xls | SECTION 2 & PANEL INFORMATION | 25 | 2 | Information on another household that we could contact in case of move | fieldwork_contact_instruction | form_design_only_not_raw_household_value |
| ALB_2005_LSMS_v01_M | LSMS05_Questionnaire_part2.xls | SECTION 2 & PANEL INFORMATION | 35 | 3 | DATE | date_field_or_format | form_design_only_not_raw_household_value |
| ALB_2005_LSMS_v01_M | LSMS05_Questionnaire_part2.xls | SECTION 2 & PANEL INFORMATION | 35 | 4 | BEGIN | begin_end_time_field | form_design_only_not_raw_household_value |
| ALB_2005_LSMS_v01_M | LSMS05_Questionnaire_part2.xls | SECTION 2 & PANEL INFORMATION | 35 | 5 | END | begin_end_time_field | form_design_only_not_raw_household_value |
| ALB_2005_LSMS_v01_M | LSMS05_Questionnaire_part2.xls | SECTION 2 & PANEL INFORMATION | 35 | 6 | STATUS | completion_status_field_or_code | form_design_only_not_raw_household_value |
| ALB_2005_LSMS_v01_M | LSMS05_Questionnaire_part2.xls | SECTION 2 & PANEL INFORMATION | 35 | 7 | REMARKS | remarks_field | form_design_only_not_raw_household_value |
| ALB_2005_LSMS_v01_M | LSMS05_Questionnaire_part2.xls | SECTION 2 & PANEL INFORMATION | 35 | 12 | Status codes | status_code_label | form_design_only_not_raw_household_value |
| ALB_2005_LSMS_v01_M | LSMS05_Questionnaire_part2.xls | SECTION 2 & PANEL INFORMATION | 36 | 2 | VISIT_1 | visit_control_row | form_design_only_not_raw_household_value |
| ALB_2005_LSMS_v01_M | LSMS05_Questionnaire_part2.xls | SECTION 2 & PANEL INFORMATION | 37 | 2 | VISIT_2 | visit_control_row | form_design_only_not_raw_household_value |
| ALB_2005_LSMS_v01_M | LSMS05_Questionnaire_part2.xls | SECTION 2 & PANEL INFORMATION | 37 | 12 | 1. Complete | completion_status_field_or_code | form_design_only_not_raw_household_value |
| ALB_2005_LSMS_v01_M | LSMS05_Questionnaire_part2.xls | SECTION 2 & PANEL INFORMATION | 38 | 2 | VISIT_3 | visit_control_row | form_design_only_not_raw_household_value |
| ALB_2005_LSMS_v01_M | LSMS05_Questionnaire_part2.xls | SECTION 2 & PANEL INFORMATION | 38 | 12 | 2. Incomplete, must return | completion_status_field_or_code | form_design_only_not_raw_household_value |
| ALB_2008_LSMS_v01_M | FINAL LSMS08 PART 1 ENGLISH.xls | CONTROL SHEET | 2 | 2 | DATE | date_field_or_format | form_design_only_not_raw_household_value |
| ALB_2008_LSMS_v01_M | FINAL LSMS08 PART 1 ENGLISH.xls | CONTROL SHEET | 2 | 3 | BEGIN | begin_end_time_field | form_design_only_not_raw_household_value |
| ALB_2008_LSMS_v01_M | FINAL LSMS08 PART 1 ENGLISH.xls | CONTROL SHEET | 2 | 4 | END | begin_end_time_field | form_design_only_not_raw_household_value |
| ALB_2008_LSMS_v01_M | FINAL LSMS08 PART 1 ENGLISH.xls | CONTROL SHEET | 2 | 5 | STATUS | completion_status_field_or_code | form_design_only_not_raw_household_value |
| ALB_2008_LSMS_v01_M | FINAL LSMS08 PART 1 ENGLISH.xls | CONTROL SHEET | 2 | 6 | REMARKS | remarks_field | form_design_only_not_raw_household_value |
| ALB_2008_LSMS_v01_M | FINAL LSMS08 PART 1 ENGLISH.xls | CONTROL SHEET | 2 | 11 | Status codes | status_code_label | form_design_only_not_raw_household_value |
| ALB_2008_LSMS_v01_M | FINAL LSMS08 PART 1 ENGLISH.xls | CONTROL SHEET | 3 | 1 | VISIT_1 | visit_control_row | form_design_only_not_raw_household_value |
| ALB_2008_LSMS_v01_M | FINAL LSMS08 PART 1 ENGLISH.xls | CONTROL SHEET | 3 | 11 | 1. Complete | completion_status_field_or_code | form_design_only_not_raw_household_value |
| ALB_2008_LSMS_v01_M | FINAL LSMS08 PART 1 ENGLISH.xls | CONTROL SHEET | 4 | 1 | VISIT_2 | visit_control_row | form_design_only_not_raw_household_value |
| ALB_2008_LSMS_v01_M | FINAL LSMS08 PART 1 ENGLISH.xls | CONTROL SHEET | 4 | 11 | 2. Incomplete, must return | completion_status_field_or_code | form_design_only_not_raw_household_value |
| ALB_2008_LSMS_v01_M | FINAL LSMS08 PART 1 ENGLISH.xls | CONTROL SHEET | 5 | 1 | VISIT_3 | visit_control_row | form_design_only_not_raw_household_value |
| ALB_2008_LSMS_v01_M | FINAL LSMS08 PART 2 ENGLISH1.xls | SECTION 2 & PANEL INFORMATION | 3 | 2 | Enumerator: Please fill this page during your second visit to the household: | second_visit_instruction | form_design_only_not_raw_household_value |
| ALB_2008_LSMS_v01_M | FINAL LSMS08 PART 2 ENGLISH1.xls | SECTION 2 & PANEL INFORMATION | 6 | 2 | We have to keep in contact with these households. Since the household may move from this dwelling, | fieldwork_contact_instruction | form_design_only_not_raw_household_value |
| ALB_2008_LSMS_v01_M | FINAL LSMS08 PART 2 ENGLISH1.xls | SECTION 2 & PANEL INFORMATION | 7 | 2 | please ask them for contact infromation during your second visit. | second_visit_instruction | form_design_only_not_raw_household_value |
| ALB_2008_LSMS_v01_M | FINAL LSMS08 PART 2 ENGLISH1.xls | SECTION 2 & PANEL INFORMATION | 13 | 2 | For this reason we may wish to contact you again in the coming year.. | fieldwork_contact_instruction | form_design_only_not_raw_household_value |
| ALB_2008_LSMS_v01_M | FINAL LSMS08 PART 2 ENGLISH1.xls | SECTION 2 & PANEL INFORMATION | 16 | 2 | Some information will help us contact you in the future: | fieldwork_contact_instruction | form_design_only_not_raw_household_value |
| ALB_2008_LSMS_v01_M | FINAL LSMS08 PART 2 ENGLISH1.xls | SECTION 2 & PANEL INFORMATION | 21 | 2 | And would it also be possible to have an alternative address or telephone of a relative number to contact y... | fieldwork_contact_instruction | form_design_only_not_raw_household_value |
| ALB_2008_LSMS_v01_M | FINAL LSMS08 PART 2 ENGLISH1.xls | SECTION 2 & PANEL INFORMATION | 25 | 2 | Information on another household that we could contact in case of move | fieldwork_contact_instruction | form_design_only_not_raw_household_value |
| ALB_2008_LSMS_v01_M | FINAL LSMS08 PART 2 ENGLISH1.xls | SECTION 2 & PANEL INFORMATION | 35 | 3 | DATE | date_field_or_format | form_design_only_not_raw_household_value |
| ALB_2008_LSMS_v01_M | FINAL LSMS08 PART 2 ENGLISH1.xls | SECTION 2 & PANEL INFORMATION | 35 | 4 | BEGIN | begin_end_time_field | form_design_only_not_raw_household_value |
| ALB_2008_LSMS_v01_M | FINAL LSMS08 PART 2 ENGLISH1.xls | SECTION 2 & PANEL INFORMATION | 35 | 5 | END | begin_end_time_field | form_design_only_not_raw_household_value |
| ALB_2008_LSMS_v01_M | FINAL LSMS08 PART 2 ENGLISH1.xls | SECTION 2 & PANEL INFORMATION | 35 | 6 | STATUS | completion_status_field_or_code | form_design_only_not_raw_household_value |
| ALB_2008_LSMS_v01_M | FINAL LSMS08 PART 2 ENGLISH1.xls | SECTION 2 & PANEL INFORMATION | 35 | 7 | REMARKS | remarks_field | form_design_only_not_raw_household_value |
| ALB_2008_LSMS_v01_M | FINAL LSMS08 PART 2 ENGLISH1.xls | SECTION 2 & PANEL INFORMATION | 35 | 12 | Status codes | status_code_label | form_design_only_not_raw_household_value |
| ALB_2008_LSMS_v01_M | FINAL LSMS08 PART 2 ENGLISH1.xls | SECTION 2 & PANEL INFORMATION | 36 | 2 | VISIT_1 | visit_control_row | form_design_only_not_raw_household_value |
| ALB_2008_LSMS_v01_M | FINAL LSMS08 PART 2 ENGLISH1.xls | SECTION 2 & PANEL INFORMATION | 37 | 2 | VISIT_2 | visit_control_row | form_design_only_not_raw_household_value |
| ALB_2008_LSMS_v01_M | FINAL LSMS08 PART 2 ENGLISH1.xls | SECTION 2 & PANEL INFORMATION | 37 | 12 | 1. Complete | completion_status_field_or_code | form_design_only_not_raw_household_value |
| ALB_2008_LSMS_v01_M | FINAL LSMS08 PART 2 ENGLISH1.xls | SECTION 2 & PANEL INFORMATION | 38 | 2 | VISIT_3 | visit_control_row | form_design_only_not_raw_household_value |
| ALB_2008_LSMS_v01_M | FINAL LSMS08 PART 2 ENGLISH1.xls | SECTION 2 & PANEL INFORMATION | 38 | 12 | 2. Incomplete, must return | completion_status_field_or_code | form_design_only_not_raw_household_value |

## Questionnaire Evidence Roles

| evidence_role | Rows |
|---|---:|
| begin_end_time_field | 11 |
| completion_status_field_or_code | 18 |
| date_field_or_format | 6 |
| fieldwork_contact_instruction | 13 |
| remarks_field | 6 |
| second_visit_instruction | 5 |
| status_code_label | 6 |
| visit_control_row | 18 |

## Raw SPSS Timing Evidence And Gaps

| idno | source_path | variable_name | variable_label | raw_gap_role | promotion_status |
|---|---|---|---|---|---|
| ALB_2002_LSMS_v01_M | temp\raw_extracted\lsms2002en_4dbf0b087520\lsms2002en\Data_2002\Modul_0_identification.sav | m0_q08d | Day of Interview | raw_household_interview_timing_verified_alb2002 | raw_timing_observed_but_not_questionnaire_derived_and_climate_blocked |
| ALB_2002_LSMS_v01_M | temp\raw_extracted\lsms2002en_4dbf0b087520\lsms2002en\Data_2002\Modul_0_identification.sav | m0_q08m | Month of Interview | raw_household_interview_timing_verified_alb2002 | raw_timing_observed_but_not_questionnaire_derived_and_climate_blocked |
| ALB_2002_LSMS_v01_M | temp\raw_extracted\lsms2002en_4dbf0b087520\lsms2002en\Data_2002\Modul_0_identification.sav | m0_q08y | Year of Interview | raw_household_interview_timing_verified_alb2002 | raw_timing_observed_but_not_questionnaire_derived_and_climate_blocked |
| ALB_2002_LSMS_v01_M | temp\raw_extracted\lsms2002en_4dbf0b087520\lsms2002en\Data_2002\Modul_0_identification.sav | m0_q08d2 | Day of Interview | raw_household_interview_timing_verified_alb2002 | raw_timing_observed_but_not_questionnaire_derived_and_climate_blocked |
| ALB_2002_LSMS_v01_M | temp\raw_extracted\lsms2002en_4dbf0b087520\lsms2002en\Data_2002\Modul_0_identification.sav | m0_q08m2 | Month of Interview | raw_household_interview_timing_verified_alb2002 | raw_timing_observed_but_not_questionnaire_derived_and_climate_blocked |
| ALB_2002_LSMS_v01_M | temp\raw_extracted\lsms2002en_4dbf0b087520\lsms2002en\Data_2002\Modul_0_identification.sav | m0_q08y2 | Year of Interview | raw_household_interview_timing_verified_alb2002 | raw_timing_observed_but_not_questionnaire_derived_and_climate_blocked |
| ALB_2002_LSMS_v01_M | temp\raw_extracted\lsms2002en_4dbf0b087520\lsms2002en\Data_2002\Modul_0_identification.sav | m0_date | Date of last modification | raw_household_interview_timing_verified_alb2002 | raw_timing_observed_but_not_questionnaire_derived_and_climate_blocked |
| ALB_2002_LSMS_v01_M | temp\raw_extracted\lsms2002en_4dbf0b087520\lsms2002en\Data_2002\Modul_1_hhroster.sav | m1_q06 | What is John's Marital Status? | status_keyword_not_verified_interview_timing | raw_timing_not_verified_for_climate_windows |
| ALB_2002_LSMS_v01_M | temp\raw_extracted\lsms2002en_4dbf0b087520\lsms2002en\Data_2002\Modul_2_Migration.sav | m2_q04a | Date (month) moving here | timing_keyword_not_verified_interview_timing | raw_timing_not_verified_for_climate_windows |
| ALB_2002_LSMS_v01_M | temp\raw_extracted\lsms2002en_4dbf0b087520\lsms2002en\Data_2002\Modul_2_Migration.sav | m2_q04b | Date (Year) moving here | timing_keyword_not_verified_interview_timing | raw_timing_not_verified_for_climate_windows |
| ALB_2002_LSMS_v01_M | temp\raw_extracted\lsms2002en_4dbf0b087520\lsms2002en\Data_2002\Modul_5A_Health.sav | m5a_q68 | Status of license | status_keyword_not_verified_interview_timing | raw_timing_not_verified_for_climate_windows |
| ALB_2002_LSMS_v01_M | temp\raw_extracted\lsms2002en_4dbf0b087520\lsms2002en\Data_2002\Modul_9_subjpov_cl.sav | M09_Q09 | Economic status | status_keyword_not_verified_interview_timing | raw_timing_not_verified_for_climate_windows |
| ALB_2005_LSMS_v01_M | temp\raw_extracted\lsms2005en_1e7f1965c4a5\lsms2005en\Data_2005\filters.sav | P8_Q01 | extension visit | not_interview_timing_health_or_module_visit_context | raw_timing_not_verified_for_climate_windows |
| ALB_2005_LSMS_v01_M | temp\raw_extracted\lsms2005en_1e7f1965c4a5\lsms2005en\Data_2005\filters.sav | P8_Q03 | visit number | not_interview_timing_health_or_module_visit_context | raw_timing_not_verified_for_climate_windows |
| ALB_2005_LSMS_v01_M | temp\raw_extracted\lsms2005en_1e7f1965c4a5\lsms2005en\Data_2005\Modul_10_fertility_cl.sav | m10_q5d | Date of Birth - Day | not_interview_timing_birth_or_fertility_context | raw_timing_not_verified_for_climate_windows |
| ALB_2005_LSMS_v01_M | temp\raw_extracted\lsms2005en_1e7f1965c4a5\lsms2005en\Data_2005\Modul_10_fertility_cl.sav | m10_q5m | Date of Birth - Month | not_interview_timing_birth_or_fertility_context | raw_timing_not_verified_for_climate_windows |
| ALB_2005_LSMS_v01_M | temp\raw_extracted\lsms2005en_1e7f1965c4a5\lsms2005en\Data_2005\Modul_10_fertility_cl.sav | m10_q5y | Date of Birth - Year | not_interview_timing_birth_or_fertility_context | raw_timing_not_verified_for_climate_windows |
| ALB_2005_LSMS_v01_M | temp\raw_extracted\lsms2005en_1e7f1965c4a5\lsms2005en\Data_2005\Modul_10_fertility_cl.sav | m10_q09 | Period of 1st visit | not_interview_timing_health_or_module_visit_context | raw_timing_not_verified_for_climate_windows |
| ALB_2005_LSMS_v01_M | temp\raw_extracted\lsms2005en_1e7f1965c4a5\lsms2005en\Data_2005\Modul_16_social_capital_cl.sav | m16_q22b | Different economic status | status_keyword_not_verified_interview_timing | raw_timing_not_verified_for_climate_windows |
| ALB_2005_LSMS_v01_M | temp\raw_extracted\lsms2005en_1e7f1965c4a5\lsms2005en\Data_2005\Modul_16_social_capital_cl.sav | m16_q22c | Different social status | status_keyword_not_verified_interview_timing | raw_timing_not_verified_for_climate_windows |
| ALB_2005_LSMS_v01_M | temp\raw_extracted\lsms2005en_1e7f1965c4a5\lsms2005en\Data_2005\Modul_1A_household_rostera_cl.sav | m1a_q4d | Date of Birth - Day | not_interview_timing_birth_or_fertility_context | raw_timing_not_verified_for_climate_windows |
| ALB_2005_LSMS_v01_M | temp\raw_extracted\lsms2005en_1e7f1965c4a5\lsms2005en\Data_2005\Modul_1A_household_rostera_cl.sav | m1a_q4m | Date of Birth - Month | not_interview_timing_birth_or_fertility_context | raw_timing_not_verified_for_climate_windows |
| ALB_2005_LSMS_v01_M | temp\raw_extracted\lsms2005en_1e7f1965c4a5\lsms2005en\Data_2005\Modul_1A_household_rostera_cl.sav | m1a_q4y | Date of Birth - Year | not_interview_timing_birth_or_fertility_context | raw_timing_not_verified_for_climate_windows |
| ALB_2005_LSMS_v01_M | temp\raw_extracted\lsms2005en_1e7f1965c4a5\lsms2005en\Data_2005\Modul_1A_household_rostera_cl.sav | m1a_q06 | Marital Status | status_keyword_not_verified_interview_timing | raw_timing_not_verified_for_climate_windows |
| ALB_2005_LSMS_v01_M | temp\raw_extracted\lsms2005en_1e7f1965c4a5\lsms2005en\Data_2005\Modul_4A_laboura_cl.sav | m4a_q11 | begun status less than 12 months ago | status_keyword_not_verified_interview_timing | raw_timing_not_verified_for_climate_windows |
| ALB_2005_LSMS_v01_M | temp\raw_extracted\lsms2005en_1e7f1965c4a5\lsms2005en\Data_2005\Modul_4A_laboura_cl.sav | m4a_q16 | Begun status of not working less than 12 months ago | status_keyword_not_verified_interview_timing | raw_timing_not_verified_for_climate_windows |
| ALB_2005_LSMS_v01_M | temp\raw_extracted\lsms2005en_1e7f1965c4a5\lsms2005en\Data_2005\Modul_4C_labourc_cl.sav | m4c_q07 | Status at work | status_keyword_not_verified_interview_timing | raw_timing_not_verified_for_climate_windows |
| ALB_2005_LSMS_v01_M | temp\raw_extracted\lsms2005en_1e7f1965c4a5\lsms2005en\Data_2005\Modul_4C_labourc_cl.sav | m4c_q29 | Status at work | status_keyword_not_verified_interview_timing | raw_timing_not_verified_for_climate_windows |
| ALB_2005_LSMS_v01_M | temp\raw_extracted\lsms2005en_1e7f1965c4a5\lsms2005en\Data_2005\Modul_4D_labourd_cl.sav | m4d_q01 | Status Code | status_keyword_not_verified_interview_timing | raw_timing_not_verified_for_climate_windows |
| ALB_2005_LSMS_v01_M | temp\raw_extracted\lsms2005en_1e7f1965c4a5\lsms2005en\Data_2005\Modul_4D_labourd_cl.sav | m4d_q05 | Status at job | not_interview_timing_event_history_context | raw_timing_not_verified_for_climate_windows |
| ALB_2005_LSMS_v01_M | temp\raw_extracted\lsms2005en_1e7f1965c4a5\lsms2005en\Data_2005\Modul_6C_migrationc_cl.sav | m6c_q62 | Assistance for interview | not_interview_timing_event_history_context | raw_timing_not_verified_for_climate_windows |
| ALB_2005_LSMS_v01_M | temp\raw_extracted\lsms2005en_1e7f1965c4a5\lsms2005en\Data_2005\Modul_6C_migrationc_cl.sav | m6c_q77 | Activity status | status_keyword_not_verified_interview_timing | raw_timing_not_verified_for_climate_windows |
| ALB_2005_LSMS_v01_M | temp\raw_extracted\lsms2005en_1e7f1965c4a5\lsms2005en\Data_2005\Modul_7_subjective_poverty_cl.sav | m07_q09 | Economic status | status_keyword_not_verified_interview_timing | raw_timing_not_verified_for_climate_windows |
| ALB_2005_LSMS_v01_M | temp\raw_extracted\lsms2005en_1e7f1965c4a5\lsms2005en\Data_2005\Modul_7_subjective_poverty_cl.sav | m07_q010 | Economic status | status_keyword_not_verified_interview_timing | raw_timing_not_verified_for_climate_windows |
| ALB_2005_LSMS_v01_M | temp\raw_extracted\lsms2005en_1e7f1965c4a5\lsms2005en\Data_2005\Modul_9A_healtha_cl.sav | m9a_q83 | Status of license | status_keyword_not_verified_interview_timing | raw_timing_not_verified_for_climate_windows |
| ALB_2008_LSMS_v01_M | temp\raw_extracted\lsms_2008_eng_a54110ab32b9\LSMS 2008_eng\Data_2008\Modul_10_fertility.sav | m10_q5d | date of birth - day | not_interview_timing_birth_or_fertility_context | raw_timing_not_verified_for_climate_windows |
| ALB_2008_LSMS_v01_M | temp\raw_extracted\lsms_2008_eng_a54110ab32b9\LSMS 2008_eng\Data_2008\Modul_10_fertility.sav | m10_q5m | date of birth - month | not_interview_timing_birth_or_fertility_context | raw_timing_not_verified_for_climate_windows |
| ALB_2008_LSMS_v01_M | temp\raw_extracted\lsms_2008_eng_a54110ab32b9\LSMS 2008_eng\Data_2008\Modul_10_fertility.sav | m10_q5y | date of birth - year | not_interview_timing_birth_or_fertility_context | raw_timing_not_verified_for_climate_windows |
| ALB_2008_LSMS_v01_M | temp\raw_extracted\lsms_2008_eng_a54110ab32b9\LSMS 2008_eng\Data_2008\Modul_10_fertility.sav | m10_q09 | period of 1st visit | not_interview_timing_health_or_module_visit_context | raw_timing_not_verified_for_climate_windows |
| ALB_2008_LSMS_v01_M | temp\raw_extracted\lsms_2008_eng_a54110ab32b9\LSMS 2008_eng\Data_2008\Modul_16_social_capital.sav | m16_q22b | different economic status | status_keyword_not_verified_interview_timing | raw_timing_not_verified_for_climate_windows |
| ALB_2008_LSMS_v01_M | temp\raw_extracted\lsms_2008_eng_a54110ab32b9\LSMS 2008_eng\Data_2008\Modul_16_social_capital.sav | m16_q22c | different social status | status_keyword_not_verified_interview_timing | raw_timing_not_verified_for_climate_windows |
| ALB_2008_LSMS_v01_M | temp\raw_extracted\lsms_2008_eng_a54110ab32b9\LSMS 2008_eng\Data_2008\Modul_1A_household_roster.sav | m1a_q4d | date of birth - day | not_interview_timing_birth_or_fertility_context | raw_timing_not_verified_for_climate_windows |
| ALB_2008_LSMS_v01_M | temp\raw_extracted\lsms_2008_eng_a54110ab32b9\LSMS 2008_eng\Data_2008\Modul_1A_household_roster.sav | m1a_q4m | date of birth - month | not_interview_timing_birth_or_fertility_context | raw_timing_not_verified_for_climate_windows |
| ALB_2008_LSMS_v01_M | temp\raw_extracted\lsms_2008_eng_a54110ab32b9\LSMS 2008_eng\Data_2008\Modul_1A_household_roster.sav | m1a_q4y | date of birth - year | not_interview_timing_birth_or_fertility_context | raw_timing_not_verified_for_climate_windows |
| ALB_2008_LSMS_v01_M | temp\raw_extracted\lsms_2008_eng_a54110ab32b9\LSMS 2008_eng\Data_2008\Modul_1A_household_roster.sav | m1a_q06 | marital status | status_keyword_not_verified_interview_timing | raw_timing_not_verified_for_climate_windows |
| ALB_2008_LSMS_v01_M | temp\raw_extracted\lsms_2008_eng_a54110ab32b9\LSMS 2008_eng\Data_2008\Modul_2D_education.sav | end_m2d | end form m2d | not_interview_timing_module_end_marker | raw_timing_not_verified_for_climate_windows |
| ALB_2008_LSMS_v01_M | temp\raw_extracted\lsms_2008_eng_a54110ab32b9\LSMS 2008_eng\Data_2008\Modul_4A_labour.sav | m4a_q11 | begun status less than 12 months ago | status_keyword_not_verified_interview_timing | raw_timing_not_verified_for_climate_windows |
| ALB_2008_LSMS_v01_M | temp\raw_extracted\lsms_2008_eng_a54110ab32b9\LSMS 2008_eng\Data_2008\Modul_4A_labour.sav | m4a_q16 | begun status of not working less than 12 months ago | status_keyword_not_verified_interview_timing | raw_timing_not_verified_for_climate_windows |
| ALB_2008_LSMS_v01_M | temp\raw_extracted\lsms_2008_eng_a54110ab32b9\LSMS 2008_eng\Data_2008\Modul_4C_labour.sav | m4c_q07 | status at work | status_keyword_not_verified_interview_timing | raw_timing_not_verified_for_climate_windows |
| ALB_2008_LSMS_v01_M | temp\raw_extracted\lsms_2008_eng_a54110ab32b9\LSMS 2008_eng\Data_2008\Modul_4C_labour.sav | m4c_q29 | status at work | status_keyword_not_verified_interview_timing | raw_timing_not_verified_for_climate_windows |
| ALB_2008_LSMS_v01_M | temp\raw_extracted\lsms_2008_eng_a54110ab32b9\LSMS 2008_eng\Data_2008\Modul_4D_labour.sav | m4d_q01 | status code | status_keyword_not_verified_interview_timing | raw_timing_not_verified_for_climate_windows |
| ALB_2008_LSMS_v01_M | temp\raw_extracted\lsms_2008_eng_a54110ab32b9\LSMS 2008_eng\Data_2008\Modul_4D_labour.sav | m4d_q05 | status at job | not_interview_timing_event_history_context | raw_timing_not_verified_for_climate_windows |
| ALB_2008_LSMS_v01_M | temp\raw_extracted\lsms_2008_eng_a54110ab32b9\LSMS 2008_eng\Data_2008\Modul_6C_migration_c.sav | m6c_q70 | activity status | status_keyword_not_verified_interview_timing | raw_timing_not_verified_for_climate_windows |
| ALB_2008_LSMS_v01_M | temp\raw_extracted\lsms_2008_eng_a54110ab32b9\LSMS 2008_eng\Data_2008\Modul_7_subjective_poverty.sav | m07_q09 | economic status | status_keyword_not_verified_interview_timing | raw_timing_not_verified_for_climate_windows |
| ALB_2008_LSMS_v01_M | temp\raw_extracted\lsms_2008_eng_a54110ab32b9\LSMS 2008_eng\Data_2008\Modul_7_subjective_poverty.sav | m07_q090 | economic status | status_keyword_not_verified_interview_timing | raw_timing_not_verified_for_climate_windows |
| ALB_2008_LSMS_v01_M | temp\raw_extracted\lsms_2008_eng_a54110ab32b9\LSMS 2008_eng\Data_2008\Modul_9A_health.sav | m9a_q83 | status of license | status_keyword_not_verified_interview_timing | raw_timing_not_verified_for_climate_windows |
| ALB_2008_LSMS_v01_M | temp\raw_extracted\lsms_2008_eng_a54110ab32b9\LSMS 2008_eng\Data_2008\Modul_9B_health.sav | end_m9b | end form m9b | not_interview_timing_module_end_marker | raw_timing_not_verified_for_climate_windows |
| ALB_2008_LSMS_v01_M | temp\raw_extracted\lsms_2008_eng_a54110ab32b9\LSMS 2008_eng\Data_2008\Modul_9C_health.sav | end_m9c | end form m9c | not_interview_timing_module_end_marker | raw_timing_not_verified_for_climate_windows |

## Raw Gap Roles

| raw_gap_role | Rows |
|---|---:|
| not_interview_timing_birth_or_fertility_context | 12 |
| not_interview_timing_event_history_context | 3 |
| not_interview_timing_health_or_module_visit_context | 4 |
| not_interview_timing_module_end_marker | 3 |
| raw_household_interview_timing_verified_alb2002 | 7 |
| status_keyword_not_verified_interview_timing | 27 |
| timing_keyword_not_verified_interview_timing | 2 |

## Interpretation

- The legacy questionnaire control sheets document `DATE`, `BEGIN`, `END`, `STATUS`, status codes, remarks/contact context, and repeated visit rows.
- These cells show that fieldwork timing and visit status were intended on the forms, but they are form-design evidence, not household-level raw timing values.
- ALB_2002 already has raw household interview timing values in the existing household-core audit; this was not discovered from the questionnaire and does not solve the remaining boundary, no-GPS/admin aggregation, outcome-semantics, unit, recall, and comparability gates.
- ALB_2005 and ALB_2008 still do not have verified raw household interview timing rows in the current exhaustive timing/geography audits.
- Climate-linkage-ready rows remain zero for all legacy Albania waves after this audit.

## Machine-Readable Outputs

- `temp/albania_legacy_questionnaire_timing_field_audit.csv`
- `temp/albania_legacy_questionnaire_timing_raw_gap_audit.csv`
- `result/albania_legacy_questionnaire_timing_field_summary.csv`
