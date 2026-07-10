# Priority LSMS-ISA Received Raw Value Profile

Status: metadata-only value-distribution and key/design/geography prefill for
received raw archives. No raw microdata are persisted and no dataset is
promoted by this audit.

## Summary

| metric | value | interpretation |
|---|---:|---|
| priority_lsms_received_raw_value_profile_dataset_rows | 5 | Datasets with received raw value-profile evidence. |
| priority_lsms_received_raw_value_profile_variable_rows | 434 | Candidate requirement variable rows with value-profile evidence. |
| priority_lsms_received_raw_value_profile_nonmissing_variable_rows | 433 | Candidate variables with at least one nonmissing raw value. |
| priority_lsms_received_raw_value_profile_value_label_rows | 100 | Candidate variables with raw value-label metadata. |
| priority_lsms_received_raw_key_design_geography_profile_rows | 554 | Utility key, design, and geography variables profiled from received raw files. |
| priority_lsms_received_raw_value_requirement_profile_rows | 35 | Requirement-level value-profile summary rows. |
| priority_lsms_received_raw_value_profile_requirements_with_profiles | 35 | Requirements with value-profile evidence available for manual review. |
| priority_lsms_received_raw_value_profile_raw_value_verified_rows | 0 | No rows are value-verified until reviewer acceptance fields and documentation checks pass. |
| priority_lsms_received_raw_value_profile_data_write_status | blocked_value_profile_only | Value-profile evidence does not write promoted analysis data. |
| modeling_gate_status | blocked | Models remain blocked until promoted registry thresholds and climate linkage pass. |
| priority_lsms_received_raw_value_profile_status_value_profile_available_needs_documentation_review | 186 | Candidate variable value-profile status count. |
| priority_lsms_received_raw_value_profile_status_value_profile_available_needs_semantics_review | 247 | Candidate variable value-profile status count. |
| priority_lsms_received_raw_value_profile_status_value_profile_no_nonmissing_values | 1 | Candidate variable value-profile status count. |
| priority_lsms_received_raw_value_requirement_status_value_profile_available_not_value_verified | 35 | Requirement value-profile status count. |
| priority_lsms_received_raw_key_design_geography_role_admin_geography_region | 10 | Utility key/design/geography variable role count. |
| priority_lsms_received_raw_key_design_geography_role_admin_geography_traditional_authority | 2 | Utility key/design/geography variable role count. |
| priority_lsms_received_raw_key_design_geography_role_cluster_or_enumeration_area | 111 | Utility key/design/geography variable role count. |
| priority_lsms_received_raw_key_design_geography_role_household_key | 172 | Utility key/design/geography variable role count. |
| priority_lsms_received_raw_key_design_geography_role_household_key_component | 255 | Utility key/design/geography variable role count. |
| priority_lsms_received_raw_key_design_geography_role_survey_design_strata | 4 | Utility key/design/geography variable role count. |
| priority_lsms_received_raw_value_profile_handoff_readmes_written | 5 | Per-dataset received raw value-profile handoffs written. |

## Requirement-Level Profile

| country | wave | idno | requirement | candidate_variable_rows | profiled_variable_rows | variables_with_nonmissing_values | detected_recall_periods | detected_units_or_scales | value_profile_requirement_status |
|---|---|---|---|---|---|---|---|---|---|
| Malawi | 2010-2011 | MWI_2010_IHS-III_v01_M | climate_geography | 20 | 20 | 20 |  |  | value_profile_available_not_value_verified |
| Malawi | 2010-2011 | MWI_2010_IHS-III_v01_M | consumption_or_income | 13 | 13 | 13 | past_month | local_currency_amount_needs_unit_confirmation; local_currency_amount_needs_unit_confirmation; month | value_profile_available_not_value_verified |
| Malawi | 2010-2011 | MWI_2010_IHS-III_v01_M | health_need_and_access | 24 | 24 | 24 | past_2_weeks | distance_measure_needs_unit_confirmation; distance_measure_needs_unit_confirmation; unit_variable | value_profile_available_not_value_verified |
| Malawi | 2010-2011 | MWI_2010_IHS-III_v01_M | household_person_keys | 23 | 23 | 23 |  |  | value_profile_available_not_value_verified |
| Malawi | 2010-2011 | MWI_2010_IHS-III_v01_M | oop_health_expenditure | 10 | 10 | 10 | past_4_weeks | local_currency_amount_needs_unit_confirmation | value_profile_available_not_value_verified |
| Malawi | 2010-2011 | MWI_2010_IHS-III_v01_M | survey_timing | 23 | 23 | 23 | interview_date; interview_month | month | value_profile_available_not_value_verified |
| Malawi | 2010-2011 | MWI_2010_IHS-III_v01_M | weights_and_design | 21 | 21 | 21 |  | survey_weight | value_profile_available_not_value_verified |
| Malawi | 2016-2017 | MWI_2016_IHS-IV_v04_M | climate_geography | 12 | 12 | 12 |  |  | value_profile_available_not_value_verified |
| Malawi | 2016-2017 | MWI_2016_IHS-IV_v04_M | consumption_or_income | 12 | 12 | 12 |  | local_currency_amount_needs_unit_confirmation | value_profile_available_not_value_verified |
| Malawi | 2016-2017 | MWI_2016_IHS-IV_v04_M | health_need_and_access | 12 | 12 | 12 | past_2_weeks | distance_measure_needs_unit_confirmation; local_currency_amount_needs_unit_confirmation; local_cu... | value_profile_available_not_value_verified |
| Malawi | 2016-2017 | MWI_2016_IHS-IV_v04_M | household_person_keys | 12 | 12 | 12 |  |  | value_profile_available_not_value_verified |
| Malawi | 2016-2017 | MWI_2016_IHS-IV_v04_M | oop_health_expenditure | 10 | 10 | 10 | past_4_weeks | local_currency_amount_needs_unit_confirmation; local_currency_amount_needs_unit_confirmation; month | value_profile_available_not_value_verified |
| Malawi | 2016-2017 | MWI_2016_IHS-IV_v04_M | survey_timing | 12 | 12 | 12 | interview_date |  | value_profile_available_not_value_verified |
| Malawi | 2016-2017 | MWI_2016_IHS-IV_v04_M | weights_and_design | 12 | 12 | 12 |  |  | value_profile_available_not_value_verified |
| Nigeria | 2015-2016 | NGA_2015_GHSP-W3_v02_M | climate_geography | 12 | 12 | 12 |  |  | value_profile_available_not_value_verified |
| Nigeria | 2015-2016 | NGA_2015_GHSP-W3_v02_M | consumption_or_income | 12 | 12 | 12 |  | local_currency_amount_needs_unit_confirmation | value_profile_available_not_value_verified |
| Nigeria | 2015-2016 | NGA_2015_GHSP-W3_v02_M | health_need_and_access | 12 | 12 | 12 | past_4_weeks | month | value_profile_available_not_value_verified |
| Nigeria | 2015-2016 | NGA_2015_GHSP-W3_v02_M | household_person_keys | 12 | 12 | 12 |  |  | value_profile_available_not_value_verified |
| Nigeria | 2015-2016 | NGA_2015_GHSP-W3_v02_M | oop_health_expenditure | 6 | 6 | 6 |  | local_currency_amount_needs_unit_confirmation | value_profile_available_not_value_verified |
| Nigeria | 2015-2016 | NGA_2015_GHSP-W3_v02_M | survey_timing | 12 | 12 | 12 |  |  | value_profile_available_not_value_verified |
| Nigeria | 2015-2016 | NGA_2015_GHSP-W3_v02_M | weights_and_design | 12 | 12 | 12 |  | survey_weight | value_profile_available_not_value_verified |
| Tanzania | 2010-2011 | TZA_2010_NPS-R2_v03_M | climate_geography | 6 | 6 | 6 |  | unit_variable; year | value_profile_available_not_value_verified |
| Tanzania | 2010-2011 | TZA_2010_NPS-R2_v03_M | consumption_or_income | 4 | 4 | 4 |  | year | value_profile_available_not_value_verified |
| Tanzania | 2010-2011 | TZA_2010_NPS-R2_v03_M | health_need_and_access | 9 | 9 | 9 |  | local_currency_amount_needs_unit_confirmation | value_profile_available_not_value_verified |
| Tanzania | 2010-2011 | TZA_2010_NPS-R2_v03_M | household_person_keys | 11 | 11 | 11 |  | year | value_profile_available_not_value_verified |
| Tanzania | 2010-2011 | TZA_2010_NPS-R2_v03_M | oop_health_expenditure | 8 | 8 | 8 |  | local_currency_amount_needs_unit_confirmation | value_profile_available_not_value_verified |
| Tanzania | 2010-2011 | TZA_2010_NPS-R2_v03_M | survey_timing | 10 | 10 | 10 | past_12_months | local_currency_amount_needs_unit_confirmation; local_currency_amount_needs_unit_confirmation; mon... | value_profile_available_not_value_verified |
| Tanzania | 2010-2011 | TZA_2010_NPS-R2_v03_M | weights_and_design | 8 | 8 | 8 |  | survey_weight | value_profile_available_not_value_verified |
| Tanzania | 2012-2013 | TZA_2012_NPS-R3_v01_M | climate_geography | 12 | 12 | 12 |  |  | value_profile_available_not_value_verified |
| Tanzania | 2012-2013 | TZA_2012_NPS-R3_v01_M | consumption_or_income | 12 | 12 | 11 | past_12_months | local_currency_amount_needs_unit_confirmation; month | value_profile_available_not_value_verified |
| Tanzania | 2012-2013 | TZA_2012_NPS-R3_v01_M | health_need_and_access | 12 | 12 | 12 |  | local_currency_amount_needs_unit_confirmation | value_profile_available_not_value_verified |
| Tanzania | 2012-2013 | TZA_2012_NPS-R3_v01_M | household_person_keys | 12 | 12 | 12 |  |  | value_profile_available_not_value_verified |
| Tanzania | 2012-2013 | TZA_2012_NPS-R3_v01_M | oop_health_expenditure | 12 | 12 | 12 | past_4_weeks | local_currency_amount_needs_unit_confirmation; year | value_profile_available_not_value_verified |
| Tanzania | 2012-2013 | TZA_2012_NPS-R3_v01_M | survey_timing | 12 | 12 | 12 | past_12_months | month | value_profile_available_not_value_verified |
| Tanzania | 2012-2013 | TZA_2012_NPS-R3_v01_M | weights_and_design | 12 | 12 | 12 |  | survey_weight | value_profile_available_not_value_verified |

## Selected Candidate Value Profiles

| requirement | actual_member_name | variable_name | raw_variable_label | nonmissing_count | distinct_nonmissing_count | numeric_min | numeric_max | detected_recall_period | detected_unit_or_scale | value_profile_status |
|---|---|---|---|---|---|---|---|---|---|---|
| survey_timing | ag_mod_b.dta | ag_b05a | What were the months when the harvest started and ended? (START MONTH) | 5083 | 12 | 1 | 12 |  | month | value_profile_available_needs_semantics_review |
| survey_timing | ag_mod_b.dta | ag_b05b | What were the months when the harvest started and ended? (END MONTH) | 5075 | 12 | 1 | 12 |  | month | value_profile_available_needs_semantics_review |
| survey_timing | ag_mod_b.dta | ag_b05a | What were the months when the harvest started and ended? (START MONTH) | 5083 | 12 | 1 | 12 |  | month | value_profile_available_needs_semantics_review |
| survey_timing | ag_mod_b.dta | ag_b05b | What were the months when the harvest started and ended? (END MONTH) | 5075 | 12 | 1 | 12 |  | month | value_profile_available_needs_semantics_review |
| survey_timing | ag_mod_g.dta | ag_g12a | What were the months when the harvest started and ended? (START) | 6999 | 10 | 1 | 12 |  | month | value_profile_available_needs_semantics_review |
| survey_timing | ag_mod_g.dta | ag_g12b | What were the months when the harvest started and ended? (END) | 6999 | 10 | 1 | 10 |  | month | value_profile_available_needs_semantics_review |
| survey_timing | ag_mod_g.dta | ag_g12a | What were the months when the harvest started and ended? (START) | 6999 | 10 | 1 | 12 |  | month | value_profile_available_needs_semantics_review |
| survey_timing | ag_mod_g.dta | ag_g12b | What were the months when the harvest started and ended? (END) | 6999 | 10 | 1 | 10 |  | month | value_profile_available_needs_semantics_review |
| survey_timing | ag_mod_m.dta | ag_m12a | What were the months when the harvest started and ended? (START) | 249 | 12 | 1 | 12 |  | month | value_profile_available_needs_semantics_review |
| survey_timing | ag_mod_m.dta | ag_m12b | What were the months when the harvest started and ended? (END) | 248 | 11 | 1 | 12 |  | month | value_profile_available_needs_semantics_review |
| survey_timing | ag_mod_m.dta | ag_m12a | What were the months when the harvest started and ended? (START) | 249 | 12 | 1 | 12 |  | month | value_profile_available_needs_semantics_review |
| survey_timing | ag_mod_m.dta | ag_m12b | What were the months when the harvest started and ended? (END) | 248 | 11 | 1 | 12 |  | month | value_profile_available_needs_semantics_review |
| survey_timing | com_ca.dta | com_ca07 | Interview Date [MDY] | 204 | 136 | 18344 | 18786 | interview_date |  | value_profile_available_needs_semantics_review |
| survey_timing | com_ca.dta | com_ca07 | Interview Date [MDY] | 204 | 136 | 18344 | 18786 | interview_date |  | value_profile_available_needs_semantics_review |
| health_need_and_access | com_cd.dta | com_cd60a | Distance to nearest health facility with medical doctor/clinical officer?(NUM) | 204 | 55 | 0 | 600 |  | distance_measure_needs_unit_confirmation | value_profile_available_needs_semantics_review |
| health_need_and_access | com_cd.dta | com_cd60b | Distance to nearest health facility with medical doctor/clinical officer?(UNIT) | 202 | 4 | 0 | 3 |  | distance_measure_needs_unit_confirmation; unit_variable | value_profile_available_needs_semantics_review |
| health_need_and_access | com_cd.dta | com_cd53 | Is this health facility… | 86 | 3 | 1 | 3 |  |  | value_profile_available_needs_semantics_review |
| health_need_and_access | com_cd.dta | com_cd54 | Is this health facility electrified? | 86 | 2 | 1 | 2 |  |  | value_profile_available_needs_semantics_review |
| health_need_and_access | com_cd.dta | com_cd51a | Distance to nearest place where there is a health clinic(Chipatala)?(NUMBER) | 138 | 26 | 1 | 600 |  | distance_measure_needs_unit_confirmation | value_profile_available_needs_semantics_review |
| health_need_and_access | com_cd.dta | com_cd51b | Distance to nearest place where there is a health clinic(Chipatala)?(UNIT) | 138 | 3 | 1 | 3 |  | distance_measure_needs_unit_confirmation; unit_variable | value_profile_available_needs_semantics_review |
| health_need_and_access | com_cd.dta | com_cd60a | Distance to nearest health facility with medical doctor/clinical officer?(NUM) | 204 | 55 | 0 | 600 |  | distance_measure_needs_unit_confirmation | value_profile_available_needs_semantics_review |
| health_need_and_access | com_cd.dta | com_cd60b | Distance to nearest health facility with medical doctor/clinical officer?(UNIT) | 202 | 4 | 0 | 3 |  | distance_measure_needs_unit_confirmation; unit_variable | value_profile_available_needs_semantics_review |
| health_need_and_access | com_cd.dta | com_cd53 | Is this health facility… | 86 | 3 | 1 | 3 |  |  | value_profile_available_needs_semantics_review |
| health_need_and_access | com_cd.dta | com_cd54 | Is this health facility electrified? | 86 | 2 | 1 | 2 |  |  | value_profile_available_needs_semantics_review |
| health_need_and_access | com_cd.dta | com_cd51a | Distance to nearest place where there is a health clinic(Chipatala)?(NUMBER) | 138 | 26 | 1 | 600 |  | distance_measure_needs_unit_confirmation | value_profile_available_needs_semantics_review |
| health_need_and_access | com_cd.dta | com_cd51b | Distance to nearest place where there is a health clinic(Chipatala)?(UNIT) | 138 | 3 | 1 | 3 |  | distance_measure_needs_unit_confirmation; unit_variable | value_profile_available_needs_semantics_review |
| household_person_keys | hh_mod_a_filt.dta | case_id | IHS3 Baseline case_id as in IHS3 Public Data | 3246 | 3246 | 1.0101e+11 | 3.15556e+11 |  |  | value_profile_available_needs_documentation_review |
| weights_and_design | hh_mod_a_filt.dta | ea_id | Baseline EA Identifier | 3246 | 204 | 1.0101e+07 | 3.15556e+07 |  |  | value_profile_available_needs_documentation_review |
| survey_timing | hh_mod_a_filt.dta | hh_a23_1 | Interview Date [MDY] (Visit 1) | 3246 | 123 | 18324 | 18515 | interview_date |  | value_profile_available_needs_semantics_review |
| survey_timing | hh_mod_a_filt.dta | hh_a23_2 | Interview Date [MDY] (Visit 2) | 3246 | 118 | 18344 | 18779 | interview_date |  | value_profile_available_needs_semantics_review |
| survey_timing | hh_mod_a_filt.dta | hh_a23b_1 | Month of Interview (Visit 1) | 3246 | 6 | 3 | 9 | interview_month | month | value_profile_available_needs_semantics_review |
| survey_timing | hh_mod_a_filt.dta | hh_a23b_2 | Month of Interview (Visit 2) | 3246 | 9 | 3 | 11 | interview_month | month | value_profile_available_needs_semantics_review |
| climate_geography | hh_mod_a_filt.dta | ea_id | Baseline EA Identifier | 3246 | 204 | 1.0101e+07 | 3.15556e+07 |  |  | value_profile_available_needs_documentation_review |
| household_person_keys | hh_mod_a_filt.dta | case_id | IHS3 Baseline case_id as in IHS3 Public Data | 3246 | 3246 | 1.0101e+11 | 3.15556e+11 |  |  | value_profile_available_needs_documentation_review |
| weights_and_design | hh_mod_a_filt.dta | ea_id | Baseline EA Identifier | 3246 | 204 | 1.0101e+07 | 3.15556e+07 |  |  | value_profile_available_needs_documentation_review |
| survey_timing | hh_mod_a_filt.dta | hh_a23_1 | Interview Date [MDY] (Visit 1) | 3246 | 123 | 18324 | 18515 | interview_date |  | value_profile_available_needs_semantics_review |
| survey_timing | hh_mod_a_filt.dta | hh_a23_2 | Interview Date [MDY] (Visit 2) | 3246 | 118 | 18344 | 18779 | interview_date |  | value_profile_available_needs_semantics_review |
| survey_timing | hh_mod_a_filt.dta | hh_a23b_1 | Month of Interview (Visit 1) | 3246 | 6 | 3 | 9 | interview_month | month | value_profile_available_needs_semantics_review |
| survey_timing | hh_mod_a_filt.dta | hh_a23b_2 | Month of Interview (Visit 2) | 3246 | 9 | 3 | 11 | interview_month | month | value_profile_available_needs_semantics_review |
| climate_geography | hh_mod_a_filt.dta | ea_id | Baseline EA Identifier | 3246 | 204 | 1.0101e+07 | 3.15556e+07 |  |  | value_profile_available_needs_documentation_review |
| oop_health_expenditure | hh_mod_d.dta | hh_d11 | How much in total did you spend in the past 4 weeks for medical care not related | 15353 | 35 | 0 | 10000 | past_4_weeks | local_currency_amount_needs_unit_confirmation | value_profile_available_needs_semantics_review |
| oop_health_expenditure | hh_mod_d.dta | hh_d15 | How much in to tal did you spend to travel to the medical facility for overnight | 619 | 51 | 0 | 10000 |  | local_currency_amount_needs_unit_confirmation | value_profile_available_needs_semantics_review |
| oop_health_expenditure | hh_mod_d.dta | hh_d16 | How much did you spend on food during overnight stay(s) at the medical facility | 619 | 63 | 0 | 70000 |  | local_currency_amount_needs_unit_confirmation | value_profile_available_needs_semantics_review |
| oop_health_expenditure | hh_mod_d.dta | hh_d21 | How much in total did you spend in the past 4 weeks for medical care not related | 49 | 17 | 0 | 5000 | past_4_weeks | local_currency_amount_needs_unit_confirmation | value_profile_available_needs_semantics_review |
| oop_health_expenditure | hh_mod_d.dta | hh_d14 | What was the total cost of your hospital-ization(s) or overnight stay(s) in a me | 619 | 93 | 0 | 35000 |  | local_currency_amount_needs_unit_confirmation | value_profile_available_needs_semantics_review |
| health_need_and_access | hh_mod_d.dta | hh_d04 | During the past 2 weeks have you suffered from an illness or injury? | 15339 | 2 | 1 | 2 | past_2_weeks |  | value_profile_available_needs_semantics_review |
| health_need_and_access | hh_mod_d.dta | hh_d05a | What was the illness or injury (Problem 1)? | 2984 | 31 | 0 | 30 |  |  | value_profile_available_needs_semantics_review |
| health_need_and_access | hh_mod_d.dta | hh_d05a_os | What was the illness or injury (Problem 1)? (Other Specify) | 15597 | 36 |  |  |  |  | value_profile_available_needs_documentation_review |
| health_need_and_access | hh_mod_d.dta | hh_d05b | What was the illness or injury (Problem 2)? | 347 | 25 | 0 | 30 |  |  | value_profile_available_needs_semantics_review |
| health_need_and_access | hh_mod_d.dta | hh_d05b_os | What was the illness or injury (Problem 2)? (Other Specify) | 15597 | 7 |  |  |  |  | value_profile_available_needs_documentation_review |
| health_need_and_access | hh_mod_d.dta | hh_d34a | What illness do you suffer from (illness 1)? | 785 | 15 | 1 | 15 |  |  | value_profile_available_needs_semantics_review |
| oop_health_expenditure | hh_mod_d.dta | hh_d11 | How much in total did you spend in the past 4 weeks for medical care not related | 15353 | 35 | 0 | 10000 | past_4_weeks | local_currency_amount_needs_unit_confirmation | value_profile_available_needs_semantics_review |
| oop_health_expenditure | hh_mod_d.dta | hh_d15 | How much in to tal did you spend to travel to the medical facility for overnight | 619 | 51 | 0 | 10000 |  | local_currency_amount_needs_unit_confirmation | value_profile_available_needs_semantics_review |
| oop_health_expenditure | hh_mod_d.dta | hh_d16 | How much did you spend on food during overnight stay(s) at the medical facility | 619 | 63 | 0 | 70000 |  | local_currency_amount_needs_unit_confirmation | value_profile_available_needs_semantics_review |
| oop_health_expenditure | hh_mod_d.dta | hh_d21 | How much in total did you spend in the past 4 weeks for medical care not related | 49 | 17 | 0 | 5000 | past_4_weeks | local_currency_amount_needs_unit_confirmation | value_profile_available_needs_semantics_review |
| oop_health_expenditure | hh_mod_d.dta | hh_d14 | What was the total cost of your hospital-ization(s) or overnight stay(s) in a me | 619 | 93 | 0 | 35000 |  | local_currency_amount_needs_unit_confirmation | value_profile_available_needs_semantics_review |
| health_need_and_access | hh_mod_d.dta | hh_d04 | During the past 2 weeks have you suffered from an illness or injury? | 15339 | 2 | 1 | 2 | past_2_weeks |  | value_profile_available_needs_semantics_review |
| health_need_and_access | hh_mod_d.dta | hh_d05a | What was the illness or injury (Problem 1)? | 2984 | 31 | 0 | 30 |  |  | value_profile_available_needs_semantics_review |
| health_need_and_access | hh_mod_d.dta | hh_d05a_os | What was the illness or injury (Problem 1)? (Other Specify) | 15597 | 36 |  |  |  |  | value_profile_available_needs_documentation_review |
| health_need_and_access | hh_mod_d.dta | hh_d05b | What was the illness or injury (Problem 2)? | 347 | 25 | 0 | 30 |  |  | value_profile_available_needs_semantics_review |

## Selected Key / Design / Geography Profiles

| actual_member_name | variable_name | variable_role | nonmissing_count | distinct_nonmissing_count | numeric_min | numeric_max | profile_status |
|---|---|---|---|---|---|---|---|
| ag_mod_a_filt.dta | case_id | household_key | 2666 | 2666 | 1.0101e+11 | 3.15556e+11 | unique_key_at_file_level |
| ag_mod_a_filt.dta | hhid | household_key_component | 2666 | 2666 | 1 | 3261 | unique_key_at_file_level |
| ag_mod_b.dta | case_id | household_key | 5409 | 2666 | 1.0101e+11 | 3.15556e+11 | repeated_key_requires_secondary_line_key |
| ag_mod_b.dta | hhid | household_key_component | 5409 | 2666 | 1 | 3261 | repeated_key_requires_secondary_line_key |
| ag_mod_c.dta | case_id | household_key | 5513 | 2666 | 1.0101e+11 | 3.15556e+11 | repeated_key_requires_secondary_line_key |
| ag_mod_c.dta | hhid | household_key_component | 5513 | 2666 | 1 | 3261 | repeated_key_requires_secondary_line_key |
| ag_mod_d.dta | case_id | household_key | 5513 | 2666 | 1.0101e+11 | 3.15556e+11 | repeated_key_requires_secondary_line_key |
| ag_mod_d.dta | hhid | household_key_component | 5513 | 2666 | 1 | 3261 | repeated_key_requires_secondary_line_key |
| ag_mod_e.dta | case_id | household_key | 4104 | 2666 | 1.0101e+11 | 3.15556e+11 | repeated_key_requires_secondary_line_key |
| ag_mod_e.dta | hhid | household_key_component | 4104 | 2666 | 1 | 3261 | repeated_key_requires_secondary_line_key |
| ag_mod_f.dta | case_id | household_key | 6702 | 2666 | 1.0101e+11 | 3.15556e+11 | repeated_key_requires_secondary_line_key |
| ag_mod_f.dta | hhid | household_key_component | 6702 | 2666 | 1 | 3261 | repeated_key_requires_secondary_line_key |
| ag_mod_g.dta | case_id | household_key | 7378 | 2666 | 1.0101e+11 | 3.15556e+11 | repeated_key_requires_secondary_line_key |
| ag_mod_g.dta | hhid | household_key_component | 7378 | 2666 | 1 | 3261 | repeated_key_requires_secondary_line_key |
| ag_mod_h.dta | case_id | household_key | 6265 | 2666 | 1.0101e+11 | 3.15556e+11 | repeated_key_requires_secondary_line_key |
| ag_mod_h.dta | hhid | household_key_component | 6265 | 2666 | 1 | 3261 | repeated_key_requires_secondary_line_key |
| ag_mod_i.dta | case_id | household_key | 6325 | 2666 | 1.0101e+11 | 3.15556e+11 | repeated_key_requires_secondary_line_key |
| ag_mod_i.dta | hhid | household_key_component | 6325 | 2666 | 1 | 3261 | repeated_key_requires_secondary_line_key |
| ag_mod_j.dta | case_id | household_key | 2706 | 2666 | 1.0101e+11 | 3.15556e+11 | repeated_key_requires_secondary_line_key |
| ag_mod_j.dta | hhid | household_key_component | 2706 | 2666 | 1 | 3261 | repeated_key_requires_secondary_line_key |
| ag_mod_k.dta | case_id | household_key | 3700 | 2666 | 1.0101e+11 | 3.15556e+11 | repeated_key_requires_secondary_line_key |
| ag_mod_k.dta | hhid | household_key_component | 3700 | 2666 | 1 | 3261 | repeated_key_requires_secondary_line_key |
| ag_mod_l.dta | case_id | household_key | 2878 | 2666 | 1.0101e+11 | 3.15556e+11 | repeated_key_requires_secondary_line_key |
| ag_mod_l.dta | hhid | household_key_component | 2878 | 2666 | 1 | 3261 | repeated_key_requires_secondary_line_key |
| ag_mod_m.dta | case_id | household_key | 2815 | 2666 | 1.0101e+11 | 3.15556e+11 | repeated_key_requires_secondary_line_key |
| ag_mod_m.dta | hhid | household_key_component | 2815 | 2666 | 1 | 3261 | repeated_key_requires_secondary_line_key |
| ag_mod_n.dta | case_id | household_key | 2807 | 2666 | 1.0101e+11 | 3.15556e+11 | repeated_key_requires_secondary_line_key |
| ag_mod_n.dta | hhid | household_key_component | 2807 | 2666 | 1 | 3261 | repeated_key_requires_secondary_line_key |
| ag_mod_o.dta | case_id | household_key | 2806 | 2666 | 1.0101e+11 | 3.15556e+11 | repeated_key_requires_secondary_line_key |
| ag_mod_o.dta | hhid | household_key_component | 2806 | 2666 | 1 | 3261 | repeated_key_requires_secondary_line_key |
| ag_mod_p.dta | case_id | household_key | 3205 | 2666 | 1.0101e+11 | 3.15556e+11 | repeated_key_requires_secondary_line_key |
| ag_mod_p.dta | hhid | household_key_component | 3205 | 2666 | 1 | 3261 | repeated_key_requires_secondary_line_key |
| ag_mod_q.dta | case_id | household_key | 3145 | 2666 | 1.0101e+11 | 3.15556e+11 | repeated_key_requires_secondary_line_key |
| ag_mod_q.dta | hhid | household_key_component | 3145 | 2666 | 1 | 3261 | repeated_key_requires_secondary_line_key |
| ag_mod_r1.dta | case_id | household_key | 28404 | 2666 | 1.0101e+11 | 3.15556e+11 | repeated_key_requires_secondary_line_key |
| ag_mod_r1.dta | hhid | household_key_component | 28404 | 2666 | 1 | 3261 | repeated_key_requires_secondary_line_key |
| ag_mod_r2.dta | case_id | household_key | 2666 | 2666 | 1.0101e+11 | 3.15556e+11 | unique_key_at_file_level |
| ag_mod_r2.dta | hhid | household_key_component | 2666 | 2666 | 1 | 3261 | unique_key_at_file_level |
| ag_mod_s.dta | case_id | household_key | 13264 | 2666 | 1.0101e+11 | 3.15556e+11 | repeated_key_requires_secondary_line_key |
| ag_mod_s.dta | hhid | household_key_component | 13264 | 2666 | 1 | 3261 | repeated_key_requires_secondary_line_key |
| ag_mod_t1.dta | case_id | household_key | 37272 | 2666 | 1.0101e+11 | 3.15556e+11 | repeated_key_requires_secondary_line_key |
| ag_mod_t1.dta | hhid | household_key_component | 37272 | 2666 | 1 | 3261 | repeated_key_requires_secondary_line_key |
| ag_mod_t2.dta | case_id | household_key | 37272 | 2666 | 1.0101e+11 | 3.15556e+11 | repeated_key_requires_secondary_line_key |
| ag_mod_t2.dta | hhid | household_key_component | 37272 | 2666 | 1 | 3261 | repeated_key_requires_secondary_line_key |
| ag_network.dta | case_id | household_key | 10011 | 2666 | 1.0101e+11 | 3.15556e+11 | repeated_key_requires_secondary_line_key |
| ag_network.dta | hhid | household_key_component | 10011 | 2666 | 1 | 3261 | repeated_key_requires_secondary_line_key |
| aux1.dta | case_id | household_key | 12271 | 12271 | 1.0101e+11 | 3.15556e+11 | unique_key_at_file_level |
| aux2.dta | case_id | household_key | 12268 | 12268 | 1.0101e+11 | 3.15556e+11 | unique_key_at_file_level |
| aux3.dta | case_id | household_key | 12271 | 12271 | 1.0101e+11 | 3.15556e+11 | unique_key_at_file_level |
| aux4.dta | case_id | household_key | 12270 | 12270 | 1.0101e+11 | 3.15556e+11 | unique_key_at_file_level |
| aux5.dta | case_id | household_key | 655 | 655 | 1.01012e+11 | 3.15532e+11 | unique_key_at_file_level |
| fs_mod_b_filt.dta | case_id | household_key | 78 | 78 | 1.01034e+11 | 3.14424e+11 | unique_key_at_file_level |
| fs_mod_b_filt.dta | hhid | household_key_component | 78 | 78 | 70 | 2984 | unique_key_at_file_level |
| fs_mod_c.dta | case_id | household_key | 87 | 78 | 1.01034e+11 | 3.14424e+11 | repeated_key_requires_secondary_line_key |
| fs_mod_c.dta | hhid | household_key_component | 87 | 78 | 70 | 2984 | repeated_key_requires_secondary_line_key |
| fs_mod_d1.dta | case_id | household_key | 624 | 78 | 1.01034e+11 | 3.14424e+11 | repeated_key_requires_secondary_line_key |
| fs_mod_d1.dta | hhid | household_key_component | 624 | 78 | 70 | 2984 | repeated_key_requires_secondary_line_key |
| fs_mod_d2.dta | case_id | household_key | 390 | 78 | 1.01034e+11 | 3.14424e+11 | repeated_key_requires_secondary_line_key |
| fs_mod_d2.dta | hhid | household_key_component | 390 | 78 | 70 | 2984 | repeated_key_requires_secondary_line_key |
| fs_mod_d3.dta | case_id | household_key | 78 | 78 | 1.01034e+11 | 3.14424e+11 | unique_key_at_file_level |
| fs_mod_d3.dta | hhid | household_key_component | 78 | 78 | 70 | 2984 | unique_key_at_file_level |
| fs_mod_e1.dta | case_id | household_key | 104 | 78 | 1.01034e+11 | 3.14424e+11 | repeated_key_requires_secondary_line_key |
| fs_mod_e1.dta | hhid | household_key_component | 104 | 78 | 70 | 2984 | repeated_key_requires_secondary_line_key |
| fs_mod_e2.dta | case_id | household_key | 468 | 78 | 1.01034e+11 | 3.14424e+11 | repeated_key_requires_secondary_line_key |
| fs_mod_e2.dta | hhid | household_key_component | 468 | 78 | 70 | 2984 | repeated_key_requires_secondary_line_key |
| fs_mod_f1.dta | case_id | household_key | 125 | 78 | 1.01034e+11 | 3.14424e+11 | repeated_key_requires_secondary_line_key |
| fs_mod_f1.dta | hhid | household_key_component | 125 | 78 | 70 | 2984 | repeated_key_requires_secondary_line_key |
| fs_mod_f2.dta | case_id | household_key | 323 | 78 | 1.01034e+11 | 3.14424e+11 | repeated_key_requires_secondary_line_key |
| fs_mod_f2.dta | hhid | household_key_component | 323 | 78 | 70 | 2984 | repeated_key_requires_secondary_line_key |
| fs_mod_g.dta | case_id | household_key | 81 | 78 | 1.01034e+11 | 3.14424e+11 | repeated_key_requires_secondary_line_key |
| fs_mod_g.dta | hhid | household_key_component | 81 | 78 | 70 | 2984 | repeated_key_requires_secondary_line_key |
| fs_mod_h1.dta | case_id | household_key | 358 | 78 | 1.01034e+11 | 3.14424e+11 | repeated_key_requires_secondary_line_key |
| fs_mod_h1.dta | hhid | household_key_component | 358 | 78 | 70 | 2984 | repeated_key_requires_secondary_line_key |
| fs_mod_h2.dta | case_id | household_key | 238 | 78 | 1.01034e+11 | 3.14424e+11 | repeated_key_requires_secondary_line_key |
| fs_mod_h2.dta | hhid | household_key_component | 238 | 78 | 70 | 2984 | repeated_key_requires_secondary_line_key |
| fs_mod_h3.dta | case_id | household_key | 78 | 78 | 1.01034e+11 | 3.14424e+11 | unique_key_at_file_level |
| fs_mod_h3.dta | hhid | household_key_component | 78 | 78 | 70 | 2984 | unique_key_at_file_level |
| fs_mod_i1.dta | case_id | household_key | 81 | 78 | 1.01034e+11 | 3.14424e+11 | repeated_key_requires_secondary_line_key |
| fs_mod_i1.dta | hhid | household_key_component | 81 | 78 | 70 | 2984 | repeated_key_requires_secondary_line_key |
| fs_mod_i2.dta | case_id | household_key | 278 | 78 | 1.01034e+11 | 3.14424e+11 | repeated_key_requires_secondary_line_key |

## Interpretation

The audit advances received raw packages from schema presence to value-profile
review evidence. It is still not raw-value verification. Promotion remains
blocked until reviewer acceptance, documentation cross-checks, harmonized
outcome construction, and climate linkage pass.
