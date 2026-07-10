# Priority LSMS-ISA Focused Raw Value Decision Packet

Status: fail-closed documentation crosswalk for received raw LSMS/ISA packages.
This packet does not mark any country-wave as value-verified and does not write
to `data/`. It narrows the next reviewer task by pairing raw value profiles with
local package PDF documentation.

## Summary

| Metric | Value | Interpretation |
|---|---:|---|
| priority_lsms_focused_raw_value_decision_dataset_rows | 2 | Received raw datasets with focused decision rows. |
| priority_lsms_focused_raw_value_documentation_file_rows | 4 | Local PDF documentation files parsed for received raw datasets. |
| priority_lsms_focused_raw_value_documentation_extracted_rows | 4 | PDF documentation files with extracted text. |
| priority_lsms_focused_raw_value_variable_decision_rows | 366 | Variable-level focused raw value decision rows. |
| priority_lsms_focused_raw_value_requirement_decision_rows | 14 | Requirement-level focused raw value decision rows. |
| priority_lsms_focused_raw_value_requirement_raw_value_verified_rows | 0 | No requirement is value-verified by this fail-closed documentation crosswalk. |
| priority_lsms_focused_raw_value_data_write_status | blocked_decision_packet_only | Focused raw value decisions do not write promoted data. |
| modeling_gate_status | blocked | Models remain blocked until promoted registry thresholds and climate linkage pass. |
| priority_lsms_focused_raw_value_documentation_status_extracted | 4 | PDF extraction status count. |
| priority_lsms_focused_raw_value_documentation_match_documented_by_variable_code | 115 | Variable documentation match status count. |
| priority_lsms_focused_raw_value_documentation_match_label_terms_found_needs_manual_confirmation | 107 | Variable documentation match status count. |
| priority_lsms_focused_raw_value_documentation_match_not_found_in_local_pdf_text | 114 | Variable documentation match status count. |
| priority_lsms_focused_raw_value_documentation_match_weak_label_term_found_needs_manual_confirmation | 30 | Variable documentation match status count. |
| priority_lsms_focused_raw_value_requirement_mechanical_mechanical_raw_profile_available_documentation_crosscheck_missing | 1 | Requirement mechanical decision status count. |
| priority_lsms_focused_raw_value_requirement_mechanical_mechanical_raw_profile_plus_documentation_hits_needs_reviewer_acceptance | 13 | Requirement mechanical decision status count. |

## Documentation Parsed

| idno | documentation_file_name | page_count | extracted_character_count | extraction_status |
|---|---|---|---|---|
| NGA_2015_GHSP-W3_v02_M | PH_W3_Household_Quest.pdf | 70 | 106085 | extracted |
| NGA_2015_GHSP-W3_v02_M | PP_W3_Household_Quest.pdf | 47 | 75687 | extracted |
| TZA_2012_NPS-R3_v01_M | NPS_Household_Qx_Y3_Final_English.pdf | 52 | 89586 | extracted |
| TZA_2012_NPS-R3_v01_M | NPS_Wave_3 _Final _Report.pdf | 120 | 245665 | extracted |

## Requirement Decisions

| idno | requirement | mechanical_pass_rows | documentation_code_match_rows | documentation_label_match_rows | mechanical_raw_check_decision | final_verification_decision |
|---|---|---|---|---|---|---|
| NGA_2015_GHSP-W3_v02_M | household_person_keys | 104 | 104 | 0 | mechanical_raw_profile_plus_documentation_hits_needs_reviewer_acceptance | blocked_manual_acceptance_required |
| NGA_2015_GHSP-W3_v02_M | weights_and_design | 12 | 0 | 12 | mechanical_raw_profile_plus_documentation_hits_needs_reviewer_acceptance | blocked_manual_acceptance_required |
| NGA_2015_GHSP-W3_v02_M | consumption_or_income | 12 | 1 | 10 | mechanical_raw_profile_plus_documentation_hits_needs_reviewer_acceptance | blocked_manual_acceptance_required |
| NGA_2015_GHSP-W3_v02_M | oop_health_expenditure | 6 | 0 | 6 | mechanical_raw_profile_plus_documentation_hits_needs_reviewer_acceptance | blocked_manual_acceptance_required |
| NGA_2015_GHSP-W3_v02_M | health_need_and_access | 12 | 0 | 12 | mechanical_raw_profile_plus_documentation_hits_needs_reviewer_acceptance | blocked_manual_acceptance_required |
| NGA_2015_GHSP-W3_v02_M | survey_timing | 12 | 0 | 12 | mechanical_raw_profile_plus_documentation_hits_needs_reviewer_acceptance | blocked_manual_acceptance_required |
| NGA_2015_GHSP-W3_v02_M | climate_geography | 122 | 2 | 21 | mechanical_raw_profile_plus_documentation_hits_needs_reviewer_acceptance | blocked_manual_acceptance_required |
| TZA_2012_NPS-R3_v01_M | household_person_keys | 12 | 0 | 0 | mechanical_raw_profile_available_documentation_crosscheck_missing | blocked_manual_acceptance_required |
| TZA_2012_NPS-R3_v01_M | weights_and_design | 12 | 0 | 12 | mechanical_raw_profile_plus_documentation_hits_needs_reviewer_acceptance | blocked_manual_acceptance_required |
| TZA_2012_NPS-R3_v01_M | consumption_or_income | 11 | 4 | 6 | mechanical_raw_profile_plus_documentation_hits_needs_reviewer_acceptance | blocked_manual_acceptance_required |
| TZA_2012_NPS-R3_v01_M | oop_health_expenditure | 12 | 0 | 12 | mechanical_raw_profile_plus_documentation_hits_needs_reviewer_acceptance | blocked_manual_acceptance_required |
| TZA_2012_NPS-R3_v01_M | health_need_and_access | 12 | 2 | 10 | mechanical_raw_profile_plus_documentation_hits_needs_reviewer_acceptance | blocked_manual_acceptance_required |
| TZA_2012_NPS-R3_v01_M | survey_timing | 12 | 0 | 12 | mechanical_raw_profile_plus_documentation_hits_needs_reviewer_acceptance | blocked_manual_acceptance_required |
| TZA_2012_NPS-R3_v01_M | climate_geography | 14 | 2 | 12 | mechanical_raw_profile_plus_documentation_hits_needs_reviewer_acceptance | blocked_manual_acceptance_required |

## Variable Documentation Hits

| idno | requirement | variable_name | raw_variable_label | documentation_match_status | documentation_file_name |
|---|---|---|---|---|---|
| NGA_2015_GHSP-W3_v02_M | climate_geography | lga | Local Government Area (LGA) | documented_by_variable_code | PH_W3_Household_Quest.pdf |
| NGA_2015_GHSP-W3_v02_M | climate_geography | lga | Local Government Area (LGA) | documented_by_variable_code | PH_W3_Household_Quest.pdf |
| NGA_2015_GHSP-W3_v02_M | consumption_or_income | hhid | HOUSEHOLD IDENTIFICATION | documented_by_variable_code | PH_W3_Household_Quest.pdf |
| NGA_2015_GHSP-W3_v02_M | household_person_keys | hhid | HOUSEHOLD IDENTIFICATION | documented_by_variable_code | PH_W3_Household_Quest.pdf |
| NGA_2015_GHSP-W3_v02_M | household_person_keys | hhid | HOUSEHOLD IDENTIFICATION | documented_by_variable_code | PH_W3_Household_Quest.pdf |
| NGA_2015_GHSP-W3_v02_M | household_person_keys | hhid | HOUSEHOLD IDENTIFICATION | documented_by_variable_code | PH_W3_Household_Quest.pdf |
| NGA_2015_GHSP-W3_v02_M | household_person_keys | hhid | HOUSEHOLD IDENTIFICATION | documented_by_variable_code | PH_W3_Household_Quest.pdf |
| NGA_2015_GHSP-W3_v02_M | household_person_keys | hhid | HOUSEHOLD IDENTIFICATION | documented_by_variable_code | PH_W3_Household_Quest.pdf |
| NGA_2015_GHSP-W3_v02_M | household_person_keys | hhid | HOUSEHOLD IDENTIFICATION | documented_by_variable_code | PH_W3_Household_Quest.pdf |
| NGA_2015_GHSP-W3_v02_M | household_person_keys | hhid | HOUSEHOLD IDENTIFICATION | documented_by_variable_code | PH_W3_Household_Quest.pdf |
| NGA_2015_GHSP-W3_v02_M | household_person_keys | hhid | HOUSEHOLD IDENTIFICATION | documented_by_variable_code | PH_W3_Household_Quest.pdf |
| NGA_2015_GHSP-W3_v02_M | household_person_keys | hhid | HOUSEHOLD IDENTIFICATION | documented_by_variable_code | PH_W3_Household_Quest.pdf |
| NGA_2015_GHSP-W3_v02_M | household_person_keys | hhid | HOUSEHOLD IDENTIFICATION | documented_by_variable_code | PH_W3_Household_Quest.pdf |
| NGA_2015_GHSP-W3_v02_M | household_person_keys | hhid | HOUSEHOLD IDENTIFICATION | documented_by_variable_code | PH_W3_Household_Quest.pdf |
| NGA_2015_GHSP-W3_v02_M | household_person_keys | hhid | HOUSEHOLD IDENTIFICATION | documented_by_variable_code | PH_W3_Household_Quest.pdf |
| NGA_2015_GHSP-W3_v02_M | household_person_keys | hhid | HOUSEHOLD IDENTIFICATION | documented_by_variable_code | PH_W3_Household_Quest.pdf |
| NGA_2015_GHSP-W3_v02_M | household_person_keys | hhid | HOUSEHOLD IDENTIFICATION | documented_by_variable_code | PH_W3_Household_Quest.pdf |
| NGA_2015_GHSP-W3_v02_M | household_person_keys | hhid | HOUSEHOLD IDENTIFICATION | documented_by_variable_code | PH_W3_Household_Quest.pdf |
| NGA_2015_GHSP-W3_v02_M | household_person_keys | hhid | HOUSEHOLD IDENTIFICATION | documented_by_variable_code | PH_W3_Household_Quest.pdf |
| NGA_2015_GHSP-W3_v02_M | household_person_keys | hhid | HOUSEHOLD IDENTIFICATION | documented_by_variable_code | PH_W3_Household_Quest.pdf |

## Promotion Rule

Rows in `result/priority_lsms_isa_requirement_acceptance_decisions.csv` remain
`blocked_manual_acceptance_required`. A future reviewer or script may only turn
an item into `raw_value_verified` after checking raw files, value labels, units,
recall periods, missing codes, skip patterns, merge level, and the outcome or
climate-linkage role against official documentation.
