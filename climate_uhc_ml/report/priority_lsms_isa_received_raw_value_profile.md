# Priority LSMS-ISA Received Raw Value Profile

Status: metadata-only value-distribution and key/design/geography prefill for
received raw archives. No raw microdata are persisted and no dataset is
promoted by this audit.

## Summary

| metric | value | interpretation |
|---|---:|---|
| priority_lsms_received_raw_value_profile_dataset_rows | 1 | Datasets with received raw value-profile evidence. |
| priority_lsms_received_raw_value_profile_variable_rows | 84 | Candidate requirement variable rows with value-profile evidence. |
| priority_lsms_received_raw_value_profile_nonmissing_variable_rows | 84 | Candidate variables with at least one nonmissing raw value. |
| priority_lsms_received_raw_value_profile_value_label_rows | 31 | Candidate variables with raw value-label metadata. |
| priority_lsms_received_raw_key_design_geography_profile_rows | 459 | Utility key, design, and geography variables profiled from received raw files. |
| priority_lsms_received_raw_value_requirement_profile_rows | 7 | Requirement-level value-profile summary rows. |
| priority_lsms_received_raw_value_profile_requirements_with_profiles | 7 | Requirements with value-profile evidence available for manual review. |
| priority_lsms_received_raw_value_profile_raw_value_verified_rows | 0 | No rows are value-verified until reviewer acceptance fields and documentation checks pass. |
| priority_lsms_received_raw_value_profile_data_write_status | blocked_value_profile_only | Value-profile evidence does not write promoted analysis data. |
| modeling_gate_status | blocked | Models remain blocked until promoted registry thresholds and climate linkage pass. |
| priority_lsms_received_raw_value_profile_status_value_profile_available_needs_documentation_review | 33 | Candidate variable value-profile status count. |
| priority_lsms_received_raw_value_profile_status_value_profile_available_needs_semantics_review | 51 | Candidate variable value-profile status count. |
| priority_lsms_received_raw_value_requirement_status_value_profile_available_not_value_verified | 7 | Requirement value-profile status count. |
| priority_lsms_received_raw_key_design_geography_role_admin_geography_ag_development_district | 38 | Utility key/design/geography variable role count. |
| priority_lsms_received_raw_key_design_geography_role_admin_geography_district | 51 | Utility key/design/geography variable role count. |
| priority_lsms_received_raw_key_design_geography_role_admin_geography_region | 39 | Utility key/design/geography variable role count. |
| priority_lsms_received_raw_key_design_geography_role_admin_geography_traditional_authority | 51 | Utility key/design/geography variable role count. |
| priority_lsms_received_raw_key_design_geography_role_cluster_or_enumeration_area | 51 | Utility key/design/geography variable role count. |
| priority_lsms_received_raw_key_design_geography_role_household_head_member_id | 1 | Utility key/design/geography variable role count. |
| priority_lsms_received_raw_key_design_geography_role_household_key | 41 | Utility key/design/geography variable role count. |
| priority_lsms_received_raw_key_design_geography_role_household_key_component | 35 | Utility key/design/geography variable role count. |
| priority_lsms_received_raw_key_design_geography_role_survey_design_household_weight | 40 | Utility key/design/geography variable role count. |
| priority_lsms_received_raw_key_design_geography_role_survey_design_psu | 35 | Utility key/design/geography variable role count. |
| priority_lsms_received_raw_key_design_geography_role_survey_design_strata | 39 | Utility key/design/geography variable role count. |
| priority_lsms_received_raw_key_design_geography_role_urban_rural_ea_type | 38 | Utility key/design/geography variable role count. |
| priority_lsms_received_raw_value_profile_handoff_readmes_written | 1 | Per-dataset received raw value-profile handoffs written. |

## Requirement-Level Profile

| country | wave | idno | requirement | candidate_variable_rows | profiled_variable_rows | variables_with_nonmissing_values | detected_recall_periods | detected_units_or_scales | value_profile_requirement_status |
|---|---|---|---|---|---|---|---|---|---|
| Malawi | 2004-2005 | MWI_2004_IHS-II_v01_M | climate_geography | 12 | 12 | 12 |  |  | value_profile_available_not_value_verified |
| Malawi | 2004-2005 | MWI_2004_IHS-II_v01_M | consumption_or_income | 12 | 12 | 12 | past_month; past_week | local_currency_amount_needs_unit_confirmation; month; local_currency_amount_needs_unit_confirmati... | value_profile_available_not_value_verified |
| Malawi | 2004-2005 | MWI_2004_IHS-II_v01_M | health_need_and_access | 12 | 12 | 12 | past_2_weeks | distance_measure_needs_unit_confirmation; unit_variable | value_profile_available_not_value_verified |
| Malawi | 2004-2005 | MWI_2004_IHS-II_v01_M | household_person_keys | 12 | 12 | 12 |  |  | value_profile_available_not_value_verified |
| Malawi | 2004-2005 | MWI_2004_IHS-II_v01_M | oop_health_expenditure | 12 | 12 | 12 | past_2_weeks; past_4_weeks | local_currency_amount_needs_unit_confirmation | value_profile_available_not_value_verified |
| Malawi | 2004-2005 | MWI_2004_IHS-II_v01_M | survey_timing | 12 | 12 | 12 | calendar_year; interview_date; interview_month | month; month; year; unit_variable; month; year; year | value_profile_available_not_value_verified |
| Malawi | 2004-2005 | MWI_2004_IHS-II_v01_M | weights_and_design | 12 | 12 | 12 |  |  | value_profile_available_not_value_verified |

## Selected Candidate Value Profiles

| requirement | actual_member_name | variable_name | raw_variable_label | nonmissing_count | distinct_nonmissing_count | numeric_min | numeric_max | detected_recall_period | detected_unit_or_scale | value_profile_status |
|---|---|---|---|---|---|---|---|---|---|---|
| survey_timing | ihs2_household.dta | idate | Interview Date | 11280 | 386 | 16138 | 16526 | interview_date |  | value_profile_available_needs_semantics_review |
| survey_timing | ihs2_individ.dta | age_months | Age in months (if <5 years) | 8904 | 60 | 0 | 59 |  | month; year | value_profile_available_needs_semantics_review |
| health_need_and_access | mod_d.dta | cd51b | What is the distance to the nearest health facility where th | 529 | 4 | 0 | 3 |  | distance_measure_needs_unit_confirmation | value_profile_available_needs_semantics_review |
| health_need_and_access | mod_d.dta | cd_51a | What is the distance to the nearest health facility where th | 559 | 85 | 0 | 500 |  | distance_measure_needs_unit_confirmation | value_profile_available_needs_semantics_review |
| health_need_and_access | mod_d.dta | cd47 | CD47. Is there a health clinic (Chipatala)in this community | 563 | 2 | 1 | 2 |  | unit_variable | value_profile_available_needs_semantics_review |
| health_need_and_access | mod_d.dta | cd57a | Medical care & medicine? | 206 | 3 | 0 | 2 |  |  | value_profile_available_needs_semantics_review |
| health_need_and_access | mod_d.dta | cd_50 | At this health clinic, is Fansidar | 563 | 3 | 1 | 3 |  |  | value_profile_available_needs_semantics_review |
| household_person_keys | sec_a.dta | hhid | Household ID | 11280 | 578 | 1 | 999 |  |  | value_profile_available_needs_semantics_review |
| weights_and_design | sec_a.dta | psu | Enumeration Area/PSU (564 total) | 11280 | 564 | 1.0101e+07 | 3.12021e+07 |  |  | value_profile_available_needs_documentation_review |
| survey_timing | sec_a.dta | a14b | Month of interview | 11280 | 12 | 1 | 12 | interview_month | month | value_profile_available_needs_semantics_review |
| climate_geography | sec_a.dta | type | EA Type: Major Urban,Boma/Large center, Small Urban,Rural,Gazetted | 11280 | 5 | 1 | 5 |  |  | value_profile_available_needs_documentation_review |
| weights_and_design | sec_aa.dta | psu | Enumeration Area/PSU (564 total) | 11280 | 564 | 1.0101e+07 | 3.12021e+07 |  |  | value_profile_available_needs_documentation_review |
| consumption_or_income | sec_aa.dta | aa01 | Description of household's food consumption, over past month | 11274 | 3 | 1 | 3 | past_month | local_currency_amount_needs_unit_confirmation; month | value_profile_available_needs_semantics_review |
| climate_geography | sec_aa.dta | type | EA Type: Major Urban,Boma/Large center, Small Urban,Rural,Gazetted | 11280 | 5 | 1 | 5 |  |  | value_profile_available_needs_documentation_review |
| household_person_keys | sec_b.dta | hhid | Household ID | 52707 | 578 | 1 | 999 |  |  | value_profile_available_needs_semantics_review |
| survey_timing | sec_c.dta | c14 | In which calendar year did you begin school for 1st time? | 32605 | 89 | 5 | 2005 | calendar_year | year | value_profile_available_needs_semantics_review |
| survey_timing | sec_c.dta | c16 | Did you attend school in the last completed academic year? | 32750 | 2 | 1 | 2 |  | year | value_profile_available_needs_semantics_review |
| oop_health_expenditure | sec_d.dta | d13 | How much did you spend in the past 4 wks for medicine? | 50844 | 83 | 0 | 3500 | past_4_weeks | local_currency_amount_needs_unit_confirmation | value_profile_available_needs_semantics_review |
| oop_health_expenditure | sec_d.dta | d12 | How much in total did you spend in the past 4 weeks for all | 50854 | 220 | 0 | 12000 | past_4_weeks | local_currency_amount_needs_unit_confirmation | value_profile_available_needs_semantics_review |
| oop_health_expenditure | sec_d.dta | d14 | How much did you spend in the past 4 wks for nonprescription | 50572 | 171 | 0 | 14000 | past_4_weeks | local_currency_amount_needs_unit_confirmation | value_profile_available_needs_semantics_review |
| oop_health_expenditure | sec_d.dta | d16 | Total cost of your hospitalization or overnight stay | 2036 | 234 | 0 | 47000 |  | local_currency_amount_needs_unit_confirmation | value_profile_available_needs_semantics_review |
| oop_health_expenditure | sec_d.dta | d19 | What was the total cost of stay at the traditional healer? | 418 | 85 | 0 | 10000 |  | local_currency_amount_needs_unit_confirmation | value_profile_available_needs_semantics_review |
| oop_health_expenditure | sec_d.dta | add | Ag Development District | 51292 | 8 | 1 | 8 |  |  | value_profile_available_needs_documentation_review |
| oop_health_expenditure | sec_d.dta | case_id |  | 51292 | 11280 | 1.0101e+10 | 3.12021e+10 |  |  | value_profile_available_needs_documentation_review |
| oop_health_expenditure | sec_d.dta | d02 | IS THE INFORMATION SELF REPORTED OR PROVIDED BY ANOTHER | 51103 | 3 | 1 | 3 |  |  | value_profile_available_needs_semantics_review |
| oop_health_expenditure | sec_d.dta | d03 | Who is reporting the information for the individual | 20325 | 17 | 0 | 18 |  |  | value_profile_available_needs_semantics_review |
| oop_health_expenditure | sec_d.dta | d04 | During the past 2 weeks have you suffered an illness/injury | 50882 | 2 | 1 | 2 | past_2_weeks |  | value_profile_available_needs_semantics_review |
| oop_health_expenditure | sec_d.dta | d05a | What was the illness or injury: Problem 1 | 14129 | 37 | 1 | 99 |  |  | value_profile_available_needs_semantics_review |
| oop_health_expenditure | sec_d.dta | d05aoth | D05A - Other response, illness or injury | 51292 | 190 | 0 | 3 |  |  | value_profile_available_needs_documentation_review |
| health_need_and_access | sec_d.dta | d05a | What was the illness or injury: Problem 1 | 14129 | 37 | 1 | 99 |  |  | value_profile_available_needs_semantics_review |
| health_need_and_access | sec_d.dta | d05aoth | D05A - Other response, illness or injury | 51292 | 190 | 0 | 3 |  |  | value_profile_available_needs_documentation_review |
| health_need_and_access | sec_d.dta | d05b | What was the illness or injury: Problem 2 | 14295 | 32 | 1 | 99 |  |  | value_profile_available_needs_semantics_review |
| health_need_and_access | sec_d.dta | d05both | D05B - Other response, illness or injury | 51292 | 42 |  |  |  |  | value_profile_available_needs_documentation_review |
| health_need_and_access | sec_d.dta | d27a | What illness do you suffer from: illness 1 | 4854 | 27 | 1 | 99 |  |  | value_profile_available_needs_semantics_review |
| health_need_and_access | sec_d.dta | d27b | What illness do you suffer from: illness 2 | 5093 | 20 | 1 | 99 |  |  | value_profile_available_needs_semantics_review |
| health_need_and_access | sec_d.dta | d04 | During the past 2 weeks have you suffered an illness/injury | 50882 | 2 | 1 | 2 | past_2_weeks |  | value_profile_available_needs_semantics_review |
| household_person_keys | sec_f.dta | hhid | Household ID | 52679 | 578 | 1 | 999 |  |  | value_profile_available_needs_semantics_review |
| weights_and_design | sec_f.dta | psu | Enumeration Area/PSU (564 total) | 52679 | 564 | 1.0101e+07 | 3.12021e+07 |  |  | value_profile_available_needs_documentation_review |
| climate_geography | sec_f.dta | type | EA Type: Major Urban,Boma/Large center, Small Urban,Rural,Gazetted | 52679 | 5 | 1 | 5 |  |  | value_profile_available_needs_documentation_review |
| household_person_keys | sec_g.dta | hhid | Household ID | 11280 | 578 | 1 | 999 |  |  | value_profile_available_needs_semantics_review |
| weights_and_design | sec_g.dta | psu | Enumeration Area/PSU (564 total) | 11280 | 564 | 1.0101e+07 | 3.12021e+07 |  |  | value_profile_available_needs_documentation_review |
| climate_geography | sec_g.dta | type | EA Type: Major Urban,Boma/Large center, Small Urban,Rural,Gazetted | 11280 | 5 | 1 | 5 |  |  | value_profile_available_needs_documentation_review |
| household_person_keys | sec_h.dta | hhid | Household ID | 67680 | 578 | 1 | 999 |  |  | value_profile_available_needs_semantics_review |
| weights_and_design | sec_h.dta | psu | Enumeration Area/PSU (564 total) | 67680 | 564 | 1.0101e+07 | 3.12021e+07 |  |  | value_profile_available_needs_documentation_review |
| climate_geography | sec_h.dta | type | EA Type: Major Urban,Boma/Large center, Small Urban,Rural,Gazetted | 67680 | 5 | 1 | 5 |  |  | value_profile_available_needs_documentation_review |
| household_person_keys | sec_i.dta | hhid | Household ID | 1297199 | 578 | 1 | 999 |  |  | value_profile_available_needs_semantics_review |
| weights_and_design | sec_i.dta | psu | Enumeration Area/PSU (564 total) | 1297199 | 564 | 1.0101e+07 | 3.12021e+07 |  |  | value_profile_available_needs_documentation_review |
| consumption_or_income | sec_i.dta | i03both | I03B - Other response, UNIT of total consumption | 1297199 | 1007 | 0 | 812 |  | local_currency_amount_needs_unit_confirmation; unit_variable | value_profile_available_needs_semantics_review |
| climate_geography | sec_i.dta | type | EA Type: Major Urban,Boma/Large center, Small Urban,Rural,Gazetted | 1297199 | 5 | 1 | 5 |  |  | value_profile_available_needs_documentation_review |
| household_person_keys | sec_j1.dta | hhid | Household ID | 67676 | 578 | 1 | 999 |  |  | value_profile_available_needs_semantics_review |
| weights_and_design | sec_j1.dta | psu | Enumeration Area/PSU (564 total) | 67676 | 564 | 1.0101e+07 | 3.12021e+07 |  |  | value_profile_available_needs_documentation_review |
| consumption_or_income | sec_j1.dta | add | Ag Development District | 67676 | 8 | 1 | 8 |  |  | value_profile_available_needs_documentation_review |
| consumption_or_income | sec_j1.dta | case_id |  | 67676 | 11280 | 1.0101e+10 | 3.12021e+10 |  |  | value_profile_available_needs_documentation_review |
| consumption_or_income | sec_j1.dta | dist | DISTRICT | 67676 | 26 | 101 | 312 |  |  | value_profile_available_needs_documentation_review |
| consumption_or_income | sec_j1.dta | ea | Enumeration Area | 67676 | 110 | 1 | 901 |  |  | value_profile_available_needs_semantics_review |
| consumption_or_income | sec_j1.dta | hhid | Household ID | 67676 | 578 | 1 | 999 |  |  | value_profile_available_needs_semantics_review |
| consumption_or_income | sec_j1.dta | hhsize | HH Size (based on hh members b08, see IHS2_individ.dta) | 67676 | 19 | 1 | 27 |  |  | value_profile_available_needs_documentation_review |
| consumption_or_income | sec_j1.dta | hhwght | IHS2 HH weight | 67676 | 30 | 90.5 | 358.7 |  | survey_weight | value_profile_available_needs_semantics_review |
| consumption_or_income | sec_j1.dta | j01a | Over the past one week did you purchase (item)? | 67676 | 2 | 1 | 2 | past_week |  | value_profile_available_needs_semantics_review |
| consumption_or_income | sec_j1.dta | j02a | ITEM CODE | 67676 | 6 | 101 | 106 |  |  | value_profile_available_needs_semantics_review |

## Selected Key / Design / Geography Profiles

| actual_member_name | variable_name | variable_role | nonmissing_count | distinct_nonmissing_count | numeric_min | numeric_max | profile_status |
|---|---|---|---|---|---|---|---|
| Filters.dta | add | admin_geography_ag_development_district | 11252 | 8 | 1 | 8 | geography_variable_present_needs_linkage_review |
| Filters.dta | case_id | household_key | 11252 | 11252 | 1.0101e+10 | 3.12021e+10 | unique_key_at_file_level |
| Filters.dta | dist | admin_geography_district | 11252 | 26 | 101 | 312 | geography_variable_present_needs_linkage_review |
| Filters.dta | ea | cluster_or_enumeration_area | 11252 | 110 | 1 | 901 | geography_variable_present_needs_linkage_review |
| Filters.dta | hhid | household_key_component | 11252 | 578 | 1 | 999 | repeated_key_requires_secondary_line_key |
| Filters.dta | hhwght | survey_design_household_weight | 11252 | 30 | 90.5 | 358.7 | weight_positive_candidate |
| Filters.dta | psu | survey_design_psu | 11252 | 563 | 1.0101e+07 | 3.12021e+07 | survey_design_variable_present |
| Filters.dta | region | admin_geography_region | 11252 | 3 | 1 | 3 | geography_variable_present_needs_linkage_review |
| Filters.dta | strata | survey_design_strata | 11252 | 30 | 101 | 404 | survey_design_variable_present |
| Filters.dta | ta | admin_geography_traditional_authority | 11252 | 48 | 1 | 87 | geography_variable_present_needs_linkage_review |
| Filters.dta | type | urban_rural_ea_type | 11252 | 5 | 1 | 5 | geography_variable_present_needs_linkage_review |
| ihs2_ag.dta | case_id | household_key | 11280 | 11280 | 1.0101e+10 | 3.12021e+10 | unique_key_at_file_level |
| ihs2_ag.dta | hhwght | survey_design_household_weight | 11280 | 29 | 79 | 358.7 | weight_positive_candidate |
| ihs2_anthro.dta | case_id | household_key | 6808 | 5153 | 1.0101e+10 | 3.12021e+10 | repeated_key_requires_secondary_line_key |
| ihs2_anthro.dta | dist | admin_geography_district | 6808 | 26 | 101 | 312 | geography_variable_present_needs_linkage_review |
| ihs2_anthro.dta | ea | cluster_or_enumeration_area | 6808 | 110 | 1 | 901 | geography_variable_present_needs_linkage_review |
| ihs2_anthro.dta | hhwght | survey_design_household_weight | 6808 | 30 | 90.5 | 358.7 | weight_positive_candidate |
| ihs2_anthro.dta | region | admin_geography_region | 6808 | 3 | 1 | 3 | geography_variable_present_needs_linkage_review |
| ihs2_anthro.dta | ta | admin_geography_traditional_authority | 6808 | 48 | 1 | 87 | geography_variable_present_needs_linkage_review |
| ihs2_ea_data.dta | dist | admin_geography_district | 564 | 26 | 101 | 312 | geography_variable_present_needs_linkage_review |
| ihs2_ea_data.dta | ea | cluster_or_enumeration_area | 564 | 110 | 1 | 901 | geography_variable_present_needs_linkage_review |
| ihs2_ea_data.dta | ta | admin_geography_traditional_authority | 564 | 48 | 1 | 87 | geography_variable_present_needs_linkage_review |
| ihs2_exp.dta | add | admin_geography_ag_development_district | 11280 | 8 | 1 | 8 | geography_variable_present_needs_linkage_review |
| ihs2_exp.dta | case_id | household_key | 11280 | 11280 | 1.0101e+10 | 3.12021e+10 | unique_key_at_file_level |
| ihs2_exp.dta | dist | admin_geography_district | 11280 | 26 | 101 | 312 | geography_variable_present_needs_linkage_review |
| ihs2_exp.dta | ea | cluster_or_enumeration_area | 11280 | 110 | 1 | 901 | geography_variable_present_needs_linkage_review |
| ihs2_exp.dta | hhwght | survey_design_household_weight | 11280 | 30 | 90.5 | 358.7 | weight_positive_candidate |
| ihs2_exp.dta | region | admin_geography_region | 11280 | 3 | 1 | 3 | geography_variable_present_needs_linkage_review |
| ihs2_exp.dta | strata | survey_design_strata | 11280 | 30 | 101 | 404 | survey_design_variable_present |
| ihs2_exp.dta | ta | admin_geography_traditional_authority | 11280 | 48 | 1 | 87 | geography_variable_present_needs_linkage_review |
| ihs2_exp.dta | type | urban_rural_ea_type | 11280 | 5 | 1 | 5 | geography_variable_present_needs_linkage_review |
| ihs2_household.dta | add | admin_geography_ag_development_district | 11280 | 8 | 1 | 8 | geography_variable_present_needs_linkage_review |
| ihs2_household.dta | case_id | household_key | 11280 | 11280 | 1.0101e+10 | 3.12021e+10 | unique_key_at_file_level |
| ihs2_household.dta | dist | admin_geography_district | 11280 | 26 | 101 | 312 | geography_variable_present_needs_linkage_review |
| ihs2_household.dta | ea | cluster_or_enumeration_area | 11280 | 110 | 1 | 901 | geography_variable_present_needs_linkage_review |
| ihs2_household.dta | hhmemid | household_head_member_id | 11280 | 1 | 1 | 1 | utility_variable_present |
| ihs2_household.dta | hhwght | survey_design_household_weight | 11280 | 30 | 90.5 | 358.7 | weight_positive_candidate |
| ihs2_household.dta | region | admin_geography_region | 11280 | 3 | 1 | 3 | geography_variable_present_needs_linkage_review |
| ihs2_household.dta | strata | survey_design_strata | 11280 | 30 | 101 | 404 | survey_design_variable_present |
| ihs2_household.dta | ta | admin_geography_traditional_authority | 11280 | 48 | 1 | 87 | geography_variable_present_needs_linkage_review |
| ihs2_household.dta | type | urban_rural_ea_type | 11280 | 5 | 1 | 5 | geography_variable_present_needs_linkage_review |
| ihs2_individ.dta | case_id | household_key | 51288 | 11280 | 1.0101e+10 | 3.12021e+10 | repeated_key_requires_secondary_line_key |
| ihs2_individ.dta | dist | admin_geography_district | 51288 | 26 | 101 | 312 | geography_variable_present_needs_linkage_review |
| ihs2_individ.dta | ea | cluster_or_enumeration_area | 51288 | 110 | 1 | 901 | geography_variable_present_needs_linkage_review |
| ihs2_individ.dta | strata | survey_design_strata | 51288 | 30 | 101 | 404 | survey_design_variable_present |
| ihs2_individ.dta | ta | admin_geography_traditional_authority | 51288 | 48 | 1 | 87 | geography_variable_present_needs_linkage_review |
| ihs2_pov.dta | add | admin_geography_ag_development_district | 11280 | 8 | 1 | 8 | geography_variable_present_needs_linkage_review |
| ihs2_pov.dta | case_id | household_key | 11280 | 11280 | 1.0101e+10 | 3.12021e+10 | unique_key_at_file_level |
| ihs2_pov.dta | dist | admin_geography_district | 11280 | 26 | 101 | 312 | geography_variable_present_needs_linkage_review |
| ihs2_pov.dta | ea | cluster_or_enumeration_area | 11280 | 110 | 1 | 901 | geography_variable_present_needs_linkage_review |
| ihs2_pov.dta | hhwght | survey_design_household_weight | 11280 | 30 | 90.5 | 358.7 | weight_positive_candidate |
| ihs2_pov.dta | region | admin_geography_region | 11280 | 3 | 1 | 3 | geography_variable_present_needs_linkage_review |
| ihs2_pov.dta | strata | survey_design_strata | 11280 | 30 | 101 | 404 | survey_design_variable_present |
| ihs2_pov.dta | ta | admin_geography_traditional_authority | 11280 | 48 | 1 | 87 | geography_variable_present_needs_linkage_review |
| ihs2_pov.dta | type | urban_rural_ea_type | 11280 | 5 | 1 | 5 | geography_variable_present_needs_linkage_review |
| mod_a.dta | dist | admin_geography_district | 564 | 26 | 101 | 312 | geography_variable_present_needs_linkage_review |
| mod_a.dta | ea | cluster_or_enumeration_area | 564 | 110 | 1 | 901 | geography_variable_present_needs_linkage_review |
| mod_a.dta | ta | admin_geography_traditional_authority | 564 | 48 | 1 | 87 | geography_variable_present_needs_linkage_review |
| mod_b.dta | dist | admin_geography_district | 4427 | 26 | 101 | 312 | geography_variable_present_needs_linkage_review |
| mod_b.dta | ea | cluster_or_enumeration_area | 4427 | 110 | 1 | 901 | geography_variable_present_needs_linkage_review |
| mod_b.dta | ta | admin_geography_traditional_authority | 4427 | 48 | 1 | 87 | geography_variable_present_needs_linkage_review |
| mod_c.dta | dist | admin_geography_district | 564 | 26 | 101 | 312 | geography_variable_present_needs_linkage_review |
| mod_c.dta | ea | cluster_or_enumeration_area | 564 | 110 | 1 | 901 | geography_variable_present_needs_linkage_review |
| mod_c.dta | ta | admin_geography_traditional_authority | 564 | 48 | 1 | 87 | geography_variable_present_needs_linkage_review |
| mod_d.dta | dist | admin_geography_district | 564 | 26 | 101 | 312 | geography_variable_present_needs_linkage_review |
| mod_d.dta | ea | cluster_or_enumeration_area | 564 | 110 | 1 | 901 | geography_variable_present_needs_linkage_review |
| mod_d.dta | ta | admin_geography_traditional_authority | 564 | 48 | 1 | 87 | geography_variable_present_needs_linkage_review |
| mod_e.dta | dist | admin_geography_district | 564 | 26 | 101 | 312 | geography_variable_present_needs_linkage_review |
| mod_e.dta | ea | cluster_or_enumeration_area | 564 | 110 | 1 | 901 | geography_variable_present_needs_linkage_review |
| mod_e.dta | ta | admin_geography_traditional_authority | 564 | 48 | 1 | 87 | geography_variable_present_needs_linkage_review |
| mod_f.dta | dist | admin_geography_district | 564 | 26 | 101 | 312 | geography_variable_present_needs_linkage_review |
| mod_f.dta | ea | cluster_or_enumeration_area | 564 | 110 | 1 | 901 | geography_variable_present_needs_linkage_review |
| mod_f.dta | ta | admin_geography_traditional_authority | 564 | 48 | 1 | 87 | geography_variable_present_needs_linkage_review |
| mod_g.dta | dist | admin_geography_district | 564 | 26 | 101 | 312 | geography_variable_present_needs_linkage_review |
| mod_g.dta | ea | cluster_or_enumeration_area | 564 | 110 | 1 | 901 | geography_variable_present_needs_linkage_review |
| mod_g.dta | ta | admin_geography_traditional_authority | 564 | 48 | 1 | 87 | geography_variable_present_needs_linkage_review |
| mod_g50better.dta | dist | admin_geography_district | 986 | 26 | 101 | 312 | geography_variable_present_needs_linkage_review |
| mod_g50better.dta | ea | cluster_or_enumeration_area | 986 | 104 | 1 | 901 | geography_variable_present_needs_linkage_review |
| mod_g50better.dta | ta | admin_geography_traditional_authority | 986 | 46 | 1 | 87 | geography_variable_present_needs_linkage_review |
| mod_g50worse.dta | dist | admin_geography_district | 2058 | 26 | 101 | 312 | geography_variable_present_needs_linkage_review |

## Interpretation

The audit advances received raw packages from schema presence to value-profile
review evidence. It is still not raw-value verification. Promotion remains
blocked until reviewer acceptance, documentation cross-checks, harmonized
outcome construction, and climate linkage pass.
