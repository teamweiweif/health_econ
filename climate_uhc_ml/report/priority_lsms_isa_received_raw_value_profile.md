# Priority LSMS-ISA Received Raw Value Profile

Status: metadata-only value-distribution and key/design/geography prefill for
received raw archives. No raw microdata are persisted and no dataset is
promoted by this audit.

## Summary

| metric | value | interpretation |
|---|---:|---|
| priority_lsms_received_raw_value_profile_dataset_rows | 3 | Datasets with received raw value-profile evidence. |
| priority_lsms_received_raw_value_profile_variable_rows | 218 | Candidate requirement variable rows with value-profile evidence. |
| priority_lsms_received_raw_value_profile_nonmissing_variable_rows | 217 | Candidate variables with at least one nonmissing raw value. |
| priority_lsms_received_raw_value_profile_value_label_rows | 52 | Candidate variables with raw value-label metadata. |
| priority_lsms_received_raw_key_design_geography_profile_rows | 217 | Utility key, design, and geography variables profiled from received raw files. |
| priority_lsms_received_raw_value_requirement_profile_rows | 21 | Requirement-level value-profile summary rows. |
| priority_lsms_received_raw_value_profile_requirements_with_profiles | 21 | Requirements with value-profile evidence available for manual review. |
| priority_lsms_received_raw_value_profile_raw_value_verified_rows | 0 | No rows are value-verified until reviewer acceptance fields and documentation checks pass. |
| priority_lsms_received_raw_value_profile_data_write_status | blocked_value_profile_only | Value-profile evidence does not write promoted analysis data. |
| modeling_gate_status | blocked | Models remain blocked until promoted registry thresholds and climate linkage pass. |
| priority_lsms_received_raw_value_profile_status_value_profile_available_needs_documentation_review | 72 | Candidate variable value-profile status count. |
| priority_lsms_received_raw_value_profile_status_value_profile_available_needs_semantics_review | 145 | Candidate variable value-profile status count. |
| priority_lsms_received_raw_value_profile_status_value_profile_no_nonmissing_values | 1 | Candidate variable value-profile status count. |
| priority_lsms_received_raw_value_requirement_status_value_profile_available_not_value_verified | 21 | Requirement value-profile status count. |
| priority_lsms_received_raw_key_design_geography_role_admin_geography_region | 6 | Utility key/design/geography variable role count. |
| priority_lsms_received_raw_key_design_geography_role_cluster_or_enumeration_area | 111 | Utility key/design/geography variable role count. |
| priority_lsms_received_raw_key_design_geography_role_household_key_component | 97 | Utility key/design/geography variable role count. |
| priority_lsms_received_raw_key_design_geography_role_survey_design_strata | 3 | Utility key/design/geography variable role count. |
| priority_lsms_received_raw_value_profile_handoff_readmes_written | 3 | Per-dataset received raw value-profile handoffs written. |

## Requirement-Level Profile

| country | wave | idno | requirement | candidate_variable_rows | profiled_variable_rows | variables_with_nonmissing_values | detected_recall_periods | detected_units_or_scales | value_profile_requirement_status |
|---|---|---|---|---|---|---|---|---|---|
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
| weights_and_design | cons_agg_wave3_visit1.dta | ea | Enumeration area | 4590 | 400 | 0 | 7586 |  |  | value_profile_available_needs_semantics_review |
| weights_and_design | cons_agg_wave3_visit1.dta | hhweight | Household cross sect weight | 4590 | 442 | 612.196 | 37188.3 |  | survey_weight | value_profile_available_needs_semantics_review |
| consumption_or_income | cons_agg_wave3_visit1.dta | totcons | Total consumption per capita | 4590 | 4590 | 8127.42 | 7.44175e+06 |  | local_currency_amount_needs_unit_confirmation | value_profile_available_needs_semantics_review |
| consumption_or_income | cons_agg_wave3_visit1.dta | nfdfoth | Expenditures on frequent non-food not mentioned elsewhere | 4590 | 438 | 0 | 2.02981e+06 |  | local_currency_amount_needs_unit_confirmation | value_profile_available_needs_semantics_review |
| consumption_or_income | cons_agg_wave3_visit1.dta | fdfishpr | Fish and seafood auto-consumption | 4590 | 420 | 0 | 275210 |  | local_currency_amount_needs_unit_confirmation | value_profile_available_needs_semantics_review |
| consumption_or_income | cons_agg_wave3_visit1.dta | fdothpr | Food items not mentioned above auto-consumption | 4590 | 1258 | 0 | 357473 |  | local_currency_amount_needs_unit_confirmation | value_profile_available_needs_semantics_review |
| consumption_or_income | cons_agg_wave3_visit1.dta | fdrestby | Food consumed in restaurants & canteens purchased | 4590 | 2717 | 0 | 3.06949e+06 |  |  | value_profile_available_needs_documentation_review |
| climate_geography | cons_agg_wave3_visit1.dta | ea | Enumeration area | 4590 | 400 | 0 | 7586 |  |  | value_profile_available_needs_semantics_review |
| weights_and_design | cons_agg_wave3_visit2.dta | ea | Enumeration area | 4579 | 402 | 0 | 7586 |  |  | value_profile_available_needs_semantics_review |
| weights_and_design | cons_agg_wave3_visit2.dta | hhweight | Household cross sect weight | 4579 | 444 | 612.196 | 37188.3 |  | survey_weight | value_profile_available_needs_semantics_review |
| consumption_or_income | cons_agg_wave3_visit2.dta | totcons | Total consumption per capita | 4579 | 4579 | 7774.37 | 2.75009e+06 |  | local_currency_amount_needs_unit_confirmation | value_profile_available_needs_semantics_review |
| consumption_or_income | cons_agg_wave3_visit2.dta | nfdfoth | Expenditures on frequent non-food not mentioned elsewhere | 4579 | 1561 | 0 | 512167 |  | local_currency_amount_needs_unit_confirmation | value_profile_available_needs_semantics_review |
| consumption_or_income | cons_agg_wave3_visit2.dta | fdfishpr | Fish and seafood auto-consumption | 4579 | 439 | 0 | 829071 |  | local_currency_amount_needs_unit_confirmation | value_profile_available_needs_semantics_review |
| consumption_or_income | cons_agg_wave3_visit2.dta | fdothpr | Food items not mentioned above auto-consumption | 4579 | 1338 | 0 | 212140 |  | local_currency_amount_needs_unit_confirmation | value_profile_available_needs_semantics_review |
| consumption_or_income | cons_agg_wave3_visit2.dta | fdrestby | Food consumed in restaurants & canteens purchased | 4579 | 2585 | 0 | 799115 |  |  | value_profile_available_needs_documentation_review |
| climate_geography | cons_agg_wave3_visit2.dta | ea | Enumeration area | 4579 | 402 | 0 | 7586 |  |  | value_profile_available_needs_semantics_review |
| household_person_keys | HHTrack.dta | hhid | HOUSEHOLD IDENTIFICATION | 5000 | 5000 | 10001 | 370040 |  |  | value_profile_available_needs_documentation_review |
| weights_and_design | HHTrack.dta | wt_combined | Combined Wave 1 & Wave 2 household weight (hhs interviewed in both W1 & W2 | 4671 | 472 | 680.218 | 37188.3 |  | survey_weight | value_profile_available_needs_semantics_review |
| weights_and_design | HHTrack.dta | wt_w1_w2_w3 | Combined Wave 1, 2, & 3 household weight (hhs interviewed in W1, W2, & W3) | 4407 | 460 | 680.218 | 37188.3 |  | survey_weight | value_profile_available_needs_semantics_review |
| weights_and_design | HHTrack.dta | wt_w1_w3 | Combined Wave 1 & Wave 3 household weight (hhs interviewed in both W1 & W3) | 4533 | 464 | 612.196 | 37188.3 |  | survey_weight | value_profile_available_needs_semantics_review |
| weights_and_design | HHTrack.dta | wt_w1v1 | Wave 1 Visit 1 (PP) household weight | 4997 | 462 | 612.196 | 33469.5 |  | survey_weight | value_profile_available_needs_semantics_review |
| weights_and_design | HHTrack.dta | wt_w1v2 | Wave 1 Visit 2 (PH) household weight | 4917 | 469 | 612.196 | 33469.5 |  | survey_weight | value_profile_available_needs_semantics_review |
| weights_and_design | HHTrack.dta | wt_w2_w3 | Combined Wave 2 & Wave 3 household weight (hhs interviewed in both W2 & W3) | 4448 | 459 | 680.218 | 37188.3 |  | survey_weight | value_profile_available_needs_semantics_review |
| climate_geography | NGA_HouseholdGeovars_Y3.dta | LAT_DD_MOD | EA Latitude (offset) | 4613 | 669 | 4.31579 | 13.7142 |  |  | value_profile_available_needs_documentation_review |
| climate_geography | NGA_HouseholdGeovars_Y3.dta | LON_DD_MOD | EA Longitude (offset) | 4613 | 669 | 2.87948 | 13.6307 |  |  | value_profile_available_needs_documentation_review |
| household_person_keys | sect10b_harvestw3.dta | hhid | HOUSEHOLD IDENTIFICATION | 531280 | 4580 | 10001 | 370040 |  |  | value_profile_available_needs_documentation_review |
| household_person_keys | sect11a1_plantingw3.dta | hhid | HOUSEHOLD IDENTIFICATION | 5824 | 2869 | 10009 | 370040 |  |  | value_profile_available_needs_documentation_review |
| household_person_keys | sect11a_plantingw3.dta | hhid | HOUSEHOLD IDENTIFICATION | 4611 | 4611 | 10001 | 370040 |  |  | value_profile_available_needs_documentation_review |
| household_person_keys | sect12_plantingw3.dta | hhid | HOUSEHOLD IDENTIFICATION | 4793 | 2428 | 10009 | 370040 |  |  | value_profile_available_needs_documentation_review |
| household_person_keys | sect1_harvestw3.dta | hhid | HOUSEHOLD IDENTIFICATION | 32827 | 4582 | 10001 | 370040 |  |  | value_profile_available_needs_documentation_review |
| climate_geography | sect1_harvestw3.dta | s1q31a | WHICH STATE AND LGA DID [NAME] MOVE TO? (LGA NAME) | 32827 | 952 | 0 | 99 |  |  | value_profile_available_needs_semantics_review |
| climate_geography | sect1_harvestw3.dta | s1q31b | WHICH STATE AND LGA DID [NAME] MOVE TO? (LGA CODE) | 4891 | 586 | 3 | 3706 |  |  | value_profile_available_needs_semantics_review |
| climate_geography | sect1_harvestw3.dta | s1q31c | WHICH STATE AND LGA DID [NAME] MOVE TO? (STATE NAME) | 32827 | 107 | 12 | 12 |  |  | value_profile_available_needs_documentation_review |
| climate_geography | sect1_harvestw3.dta | s1q31d | WHICH STATE AND LGA DID [NAME] MOVE TO? (STATE CODE) | 4928 | 38 | 0 | 37 |  |  | value_profile_available_needs_semantics_review |
| household_person_keys | sect1_plantingw3.dta | hhid | HOUSEHOLD IDENTIFICATION | 32139 | 4611 | 10001 | 370040 |  |  | value_profile_available_needs_documentation_review |
| health_need_and_access | sect3_plantingw3.dta | s3q9b | MAIN REASON FOR NOT LOOKING FOR A JOB IN THE PAST 7 DAYS?(OTHER SPECIFY) | 26735 | 87 | 10 | 10 |  |  | value_profile_available_needs_documentation_review |
| oop_health_expenditure | sect4a_harvestw3.dta | s4aq20 | WHO PAID FOR MOST OF [NAME]'S HEALTH EXPENSES? | 9541 | 10 | 1 | 11 |  | local_currency_amount_needs_unit_confirmation | value_profile_available_needs_semantics_review |
| oop_health_expenditure | sect4a_harvestw3.dta | s4aq20b | WHO PAID FOR MOST OF [NAME]'S HEALTH EXPENSES? (OTHER SPECIFY) | 26176 | 11 |  |  |  | local_currency_amount_needs_unit_confirmation | value_profile_available_needs_semantics_review |
| oop_health_expenditure | sect4a_harvestw3.dta | s4aq13 | DID [NAME] SPEND ANY MONEY ON DRUGS/MEDICINE OVER THE COUNTER? | 26176 | 2 | 1 | 2 |  | local_currency_amount_needs_unit_confirmation | value_profile_available_needs_semantics_review |
| oop_health_expenditure | sect4a_harvestw3.dta | s4aq35a | DOES THIS DIFFICULTY REDUCE THE AMOUNT OF WORK [NAME] CAN DO AT HOME? | 552 | 4 | 1 | 4 |  |  | value_profile_available_needs_semantics_review |
| oop_health_expenditure | sect4a_harvestw3.dta | s4aq35b | DOES THIS DIFFICULTY REDUCE THE AMOUNT OF WORK [NAME] CAN DO AT SCHOOL? | 416 | 4 | 1 | 4 |  |  | value_profile_available_needs_semantics_review |
| oop_health_expenditure | sect4a_harvestw3.dta | s4aq35c | DOES THIS DIFFICULTY REDUCE THE AMOUNT OF WORK [NAME] CAN DO AT WORK? | 469 | 4 | 1 | 4 |  |  | value_profile_available_needs_semantics_review |
| health_need_and_access | sect4a_harvestw3.dta | s4aq15 | DURING LAST 12 MONTHS, WAS [NAME] ADMITTED TO A HOSPITAL/HEALTH FACILITY? | 26176 | 2 | 1 | 2 |  | month | value_profile_available_needs_semantics_review |
| health_need_and_access | sect4a_harvestw3.dta | s4aq16 | HOW MANY NIGHTS DID [NAME] STAY IN HOSPITAL/HEALTH FACILITY? | 614 | 31 | 0 | 180 |  |  | value_profile_available_needs_semantics_review |
| health_need_and_access | sect4a_harvestw3.dta | s4aq17 | HOW MUCH DID [NAME] PAY FOR STAYING IN A HOSPITAL/HEALTH FACILITY? (NAIRA) | 613 | 132 | 0 | 832000 |  |  | value_profile_available_needs_semantics_review |
| health_need_and_access | sect4a_harvestw3.dta | s4aq1 | DURING PAST 4 WEEKS HAS [NAME] CONSULTED A HEALTH PRACTIONER? | 26176 | 2 | 1 | 2 | past_4_weeks |  | value_profile_available_needs_semantics_review |
| health_need_and_access | sect4a_harvestw3.dta | s4aq6a | WHOM DID [NAME] CONSULT FOR THIS ILLNESS/INJURY?(1ST) | 3754 | 13 | 1 | 13 |  |  | value_profile_available_needs_semantics_review |
| health_need_and_access | sect4a_harvestw3.dta | s4aq6a_os | WHOM DID [NAME] CONSULT FOR THIS ILLNESS/INJURY?(1ST)(OTHER SPECIFY) | 26176 | 12 |  |  |  |  | value_profile_available_needs_documentation_review |
| health_need_and_access | sect4a_harvestw3.dta | s4aq6b | WHOM DID [NAME] CONSULT FOR THIS ILLNESS/INJURY?(2ND) | 276 | 11 | 1 | 13 |  |  | value_profile_available_needs_semantics_review |
| health_need_and_access | sect4a_harvestw3.dta | s4aq6b_os | WHOM DID [NAME] CONSULT FOR THIS ILLNESS/INJURY?(2ND)(OTHER SPECIFY) | 26176 | 2 |  |  |  |  | value_profile_available_needs_documentation_review |
| health_need_and_access | sect4a_harvestw3.dta | s4aq3 | DURING THE PAST 4 WEEKS HAS [NAME] SUFFERED FROM AN ILLNESS/INJURY? | 26176 | 2 | 1 | 2 | past_4_weeks |  | value_profile_available_needs_semantics_review |
| health_need_and_access | sect4a_harvestw3.dta | s4aq3b | WHAT TYPE OF ILLNESS/INJURY DID [NAME] SUFFER FROM? | 3757 | 12 | 1 | 12 |  |  | value_profile_available_needs_semantics_review |
| health_need_and_access | sect4a_harvestw3.dta | s4aq3b_os | WHAT TYPE OF ILLNESS/INJURY DID [NAME] SUFFER FROM?(OTHER SPECIFY) | 26176 | 235 | 1 | 1 |  |  | value_profile_available_needs_documentation_review |
| household_person_keys | sect7a_plantingw3.dta | hhid | HOUSEHOLD IDENTIFICATION | 41318 | 4591 | 10001 | 370040 |  |  | value_profile_available_needs_documentation_review |
| household_person_keys | sect7b_plantingw3.dta | hhid | HOUSEHOLD IDENTIFICATION | 532555 | 4591 | 10001 | 370040 |  |  | value_profile_available_needs_documentation_review |
| consumption_or_income | sect8a_plantingw3.dta | ea | EA CODE | 18363 | 400 | 0 | 7586 |  |  | value_profile_available_needs_semantics_review |
| consumption_or_income | sect8a_plantingw3.dta | hhid | HOUSEHOLD IDENTIFICATION | 18363 | 4591 | 10001 | 370040 |  |  | value_profile_available_needs_documentation_review |
| household_person_keys | secta10_harvestw3.dta | hhid | HOUSEHOLD IDENTIFICATION | 5178 | 2450 | 10009 | 370040 |  |  | value_profile_available_needs_documentation_review |
| household_person_keys | secta_harvestw3.dta | hhid | HOUSEHOLD IDENTIFICATION | 4592 | 4592 | 10001 | 370040 |  |  | value_profile_available_needs_documentation_review |
| survey_timing | secta_harvestw3.dta | saq14ah | START TIME OF FIRST INTERVIEW - HOUR | 4589 | 19 | 1 | 20 |  |  | value_profile_available_needs_semantics_review |

## Selected Key / Design / Geography Profiles

| actual_member_name | variable_name | variable_role | nonmissing_count | distinct_nonmissing_count | numeric_min | numeric_max | profile_status |
|---|---|---|---|---|---|---|---|
| aux1.dta | ea | cluster_or_enumeration_area | 4590 | 400 | 0 | 7586 | geography_variable_present_needs_linkage_review |
| aux1.dta | hhid | household_key_component | 4590 | 4590 | 10001 | 370040 | unique_key_at_file_level |
| aux2.dta | ea | cluster_or_enumeration_area | 4579 | 402 | 0 | 7586 | geography_variable_present_needs_linkage_review |
| aux2.dta | hhid | household_key_component | 4579 | 4579 | 10001 | 370040 | unique_key_at_file_level |
| aux3.dta | hhid | household_key_component | 4591 | 4591 | 10001 | 370040 | unique_key_at_file_level |
| aux4.dta | hhid | household_key_component | 4582 | 4582 | 10001 | 370040 | unique_key_at_file_level |
| aux_round1.dta | ea | cluster_or_enumeration_area | 9169 | 402 | 0 | 7586 | geography_variable_present_needs_linkage_review |
| aux_round1.dta | hhid | household_key_component | 9169 | 4610 | 10001 | 370040 | repeated_key_requires_secondary_line_key |
| aux_round2.dta | ea | cluster_or_enumeration_area | 9169 | 402 | 0 | 7586 | geography_variable_present_needs_linkage_review |
| aux_round2.dta | hhid | household_key_component | 9169 | 4610 | 10001 | 370040 | repeated_key_requires_secondary_line_key |
| aux_round5.dta | ea | cluster_or_enumeration_area | 9169 | 402 | 0 | 7586 | geography_variable_present_needs_linkage_review |
| aux_round5.dta | hhid | household_key_component | 9169 | 4610 | 10001 | 370040 | repeated_key_requires_secondary_line_key |
| aux_year1.dta | ea | cluster_or_enumeration_area | 4579 | 402 | 0 | 7586 | geography_variable_present_needs_linkage_review |
| aux_year1.dta | hhid | household_key_component | 4610 | 4610 | 10001 | 370040 | unique_key_at_file_level |
| aux_year2.dta | ea | cluster_or_enumeration_area | 4579 | 402 | 0 | 7586 | geography_variable_present_needs_linkage_review |
| aux_year2.dta | hhid | household_key_component | 4610 | 4610 | 10001 | 370040 | unique_key_at_file_level |
| aux_year3.dta | ea | cluster_or_enumeration_area | 4611 | 402 | 0 | 7586 | geography_variable_present_needs_linkage_review |
| aux_year3.dta | hhid | household_key_component | 4611 | 4611 | 10001 | 370040 | unique_key_at_file_level |
| aux_year4.dta | ea | cluster_or_enumeration_area | 4611 | 402 | 0 | 7586 | geography_variable_present_needs_linkage_review |
| aux_year4.dta | hhid | household_key_component | 4613 | 4613 | 10001 | 370040 | unique_key_at_file_level |
| cons_agg_wave3_visit1.dta | ea | cluster_or_enumeration_area | 4590 | 400 | 0 | 7586 | geography_variable_present_needs_linkage_review |
| cons_agg_wave3_visit1.dta | hhid | household_key_component | 4590 | 4590 | 10001 | 370040 | unique_key_at_file_level |
| cons_agg_wave3_visit2.dta | ea | cluster_or_enumeration_area | 4579 | 402 | 0 | 7586 | geography_variable_present_needs_linkage_review |
| cons_agg_wave3_visit2.dta | hhid | household_key_component | 4579 | 4579 | 10001 | 370040 | unique_key_at_file_level |
| HHTrack.dta | ea | cluster_or_enumeration_area | 5000 | 411 | 4 | 7586 | geography_variable_present_needs_linkage_review |
| HHTrack.dta | hhid | household_key_component | 5000 | 5000 | 10001 | 370040 | unique_key_at_file_level |
| NGA_HouseholdGeovars_Y3.dta | ea | cluster_or_enumeration_area | 4612 | 402 | 0 | 7586 | geography_variable_present_needs_linkage_review |
| NGA_HouseholdGeovars_Y3.dta | hhid | household_key_component | 4613 | 4613 | 10001 | 370040 | unique_key_at_file_level |
| NGA_PlotGeovariables_Y3.dta | ea | cluster_or_enumeration_area | 5951 | 333 | 0 | 5180 | geography_variable_present_needs_linkage_review |
| NGA_PlotGeovariables_Y3.dta | hhid | household_key_component | 5951 | 2891 | 10009 | 370040 | repeated_key_requires_secondary_line_key |
| PTrack.dta | hhid | household_key_component | 34898 | 4998 | 10001 | 370040 | repeated_key_requires_secondary_line_key |
| sect10a_harvestw3.dta | ea | cluster_or_enumeration_area | 41238 | 402 | 0 | 7586 | geography_variable_present_needs_linkage_review |
| sect10a_harvestw3.dta | hhid | household_key_component | 41238 | 4582 | 10001 | 370040 | repeated_key_requires_secondary_line_key |
| sect10b_harvestw3.dta | ea | cluster_or_enumeration_area | 531280 | 402 | 0 | 7586 | geography_variable_present_needs_linkage_review |
| sect10b_harvestw3.dta | hhid | household_key_component | 531280 | 4580 | 10001 | 370040 | repeated_key_requires_secondary_line_key |
| sect10c_harvestw3.dta | ea | cluster_or_enumeration_area | 50402 | 402 | 0 | 7586 | geography_variable_present_needs_linkage_review |
| sect10c_harvestw3.dta | hhid | household_key_component | 50402 | 4582 | 10001 | 370040 | repeated_key_requires_secondary_line_key |
| sect10ca_harvestw3.dta | ea | cluster_or_enumeration_area | 4582 | 402 | 0 | 7586 | geography_variable_present_needs_linkage_review |
| sect10ca_harvestw3.dta | hhid | household_key_component | 4582 | 4582 | 10001 | 370040 | unique_key_at_file_level |
| sect10cb_harvestw3.dta | ea | cluster_or_enumeration_area | 6968 | 366 | 0 | 7586 | geography_variable_present_needs_linkage_review |
| sect10cb_harvestw3.dta | hhid | household_key_component | 6968 | 1742 | 10001 | 370039 | repeated_key_requires_secondary_line_key |
| sect11_plantingw3.dta | ea | cluster_or_enumeration_area | 4611 | 402 | 0 | 7586 | geography_variable_present_needs_linkage_review |
| sect11_plantingw3.dta | hhid | household_key_component | 4611 | 4611 | 10001 | 370040 | unique_key_at_file_level |
| sect11a1_plantingw3.dta | ea | cluster_or_enumeration_area | 5824 | 332 | 0 | 5180 | geography_variable_present_needs_linkage_review |
| sect11a1_plantingw3.dta | hhid | household_key_component | 5824 | 2869 | 10009 | 370040 | repeated_key_requires_secondary_line_key |
| sect11a_harvestw3.dta | ea | cluster_or_enumeration_area | 18328 | 402 | 0 | 7586 | geography_variable_present_needs_linkage_review |
| sect11a_harvestw3.dta | hhid | household_key_component | 18328 | 4582 | 10001 | 370040 | repeated_key_requires_secondary_line_key |
| sect11a_plantingw3.dta | ea | cluster_or_enumeration_area | 4591 | 400 | 0 | 7586 | geography_variable_present_needs_linkage_review |
| sect11a_plantingw3.dta | hhid | household_key_component | 4611 | 4611 | 10001 | 370040 | unique_key_at_file_level |
| sect11b1_plantingw3.dta | ea | cluster_or_enumeration_area | 5824 | 332 | 0 | 5180 | geography_variable_present_needs_linkage_review |
| sect11b1_plantingw3.dta | hhid | household_key_component | 5824 | 2869 | 10009 | 370040 | repeated_key_requires_secondary_line_key |
| sect11b_harvestw3.dta | ea | cluster_or_enumeration_area | 137460 | 402 | 0 | 7586 | geography_variable_present_needs_linkage_review |
| sect11b_harvestw3.dta | hhid | household_key_component | 137460 | 4582 | 10001 | 370040 | repeated_key_requires_secondary_line_key |
| sect11c1_plantingw3.dta | ea | cluster_or_enumeration_area | 5824 | 332 | 0 | 5180 | geography_variable_present_needs_linkage_review |
| sect11c1_plantingw3.dta | hhid | household_key_component | 5824 | 2869 | 10009 | 370040 | repeated_key_requires_secondary_line_key |
| sect11c_harvestw3.dta | ea | cluster_or_enumeration_area | 187862 | 402 | 0 | 7586 | geography_variable_present_needs_linkage_review |
| sect11c_harvestw3.dta | hhid | household_key_component | 187862 | 4582 | 10001 | 370040 | repeated_key_requires_secondary_line_key |
| sect11d_harvestw3.dta | ea | cluster_or_enumeration_area | 77894 | 402 | 0 | 7586 | geography_variable_present_needs_linkage_review |
| sect11d_harvestw3.dta | hhid | household_key_component | 77894 | 4582 | 10001 | 370040 | repeated_key_requires_secondary_line_key |
| sect11e_harvestw3.dta | ea | cluster_or_enumeration_area | 9164 | 402 | 0 | 7586 | geography_variable_present_needs_linkage_review |
| sect11e_harvestw3.dta | hhid | household_key_component | 9164 | 4582 | 10001 | 370040 | repeated_key_requires_secondary_line_key |
| sect11e_plantingw3.dta | ea | cluster_or_enumeration_area | 11840 | 330 | 0 | 5180 | geography_variable_present_needs_linkage_review |
| sect11e_plantingw3.dta | hhid | household_key_component | 11840 | 2845 | 10009 | 370040 | repeated_key_requires_secondary_line_key |
| sect11f_plantingw3.dta | ea | cluster_or_enumeration_area | 11830 | 330 | 0 | 5180 | geography_variable_present_needs_linkage_review |
| sect11f_plantingw3.dta | hhid | household_key_component | 11830 | 2844 | 10009 | 370040 | repeated_key_requires_secondary_line_key |
| sect11i_plantingw3.dta | ea | cluster_or_enumeration_area | 69275 | 349 | 0 | 5180 | geography_variable_present_needs_linkage_review |
| sect11i_plantingw3.dta | hhid | household_key_component | 69275 | 3012 | 10009 | 370040 | repeated_key_requires_secondary_line_key |
| sect11j_plantingw3.dta | ea | cluster_or_enumeration_area | 27197 | 350 | 0 | 5180 | geography_variable_present_needs_linkage_review |
| sect11j_plantingw3.dta | hhid | household_key_component | 27197 | 3022 | 10009 | 370040 | repeated_key_requires_secondary_line_key |
| sect11k_plantingw3.dta | ea | cluster_or_enumeration_area | 24159 | 349 | 0 | 5180 | geography_variable_present_needs_linkage_review |
| sect11k_plantingw3.dta | hhid | household_key_component | 24159 | 3020 | 10009 | 370040 | repeated_key_requires_secondary_line_key |
| sect11l1_plantingw3.dta | ea | cluster_or_enumeration_area | 36239 | 349 | 0 | 5180 | geography_variable_present_needs_linkage_review |
| sect11l1_plantingw3.dta | hhid | household_key_component | 36239 | 3020 | 10009 | 370040 | repeated_key_requires_secondary_line_key |
| sect11l2_plantingw3.dta | ea | cluster_or_enumeration_area | 42279 | 349 | 0 | 5180 | geography_variable_present_needs_linkage_review |
| sect11l2_plantingw3.dta | hhid | household_key_component | 42279 | 3020 | 10009 | 370040 | repeated_key_requires_secondary_line_key |
| sect12_harvestw3.dta | ea | cluster_or_enumeration_area | 4582 | 402 | 0 | 7586 | geography_variable_present_needs_linkage_review |
| sect12_harvestw3.dta | hhid | household_key_component | 4582 | 4582 | 10001 | 370040 | unique_key_at_file_level |
| sect12_plantingw3.dta | ea | cluster_or_enumeration_area | 4793 | 343 | 0 | 5180 | geography_variable_present_needs_linkage_review |
| sect12_plantingw3.dta | hhid | household_key_component | 4793 | 2428 | 10009 | 370040 | repeated_key_requires_secondary_line_key |
| sect13_harvestw3.dta | ea | cluster_or_enumeration_area | 4582 | 402 | 0 | 7586 | geography_variable_present_needs_linkage_review |

## Interpretation

The audit advances received raw packages from schema presence to value-profile
review evidence. It is still not raw-value verification. Promotion remains
blocked until reviewer acceptance, documentation cross-checks, harmonized
outcome construction, and climate linkage pass.
