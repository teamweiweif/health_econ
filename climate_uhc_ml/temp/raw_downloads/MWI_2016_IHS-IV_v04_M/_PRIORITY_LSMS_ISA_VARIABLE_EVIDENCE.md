# Priority LSMS-ISA Variable Evidence

Dataset: MWI_2016_IHS-IV_v04_M - Malawi 2016-2017

Status: official public metadata candidate variables only.

## Requirement Coverage

| Requirement | Candidate variables | Strong candidates | Candidate files | Status |
|---|---:|---:|---:|---|
| household_person_keys | 12 | 12 | 12 | official_metadata_strong_candidates_present_raw_review_required |
| weights_and_design | 12 | 12 | 12 | official_metadata_strong_candidates_present_raw_review_required |
| consumption_or_income | 12 | 12 | 5 | official_metadata_strong_candidates_present_raw_review_required |
| oop_health_expenditure | 10 | 10 | 1 | official_metadata_strong_candidates_present_raw_review_required |
| health_need_and_access | 12 | 8 | 3 | official_metadata_strong_candidates_present_raw_review_required |
| survey_timing | 12 | 12 | 3 | official_metadata_strong_candidates_present_raw_review_required |
| climate_geography | 12 | 12 | 7 | official_metadata_strong_candidates_present_raw_review_required |
| missing_codes_units_recall_skip_patterns | 0 | 0 | 0 | documentation_and_raw_review_required_no_variable_shortlist |

## File Shortlist

| Requirement | File | Candidate variables | Top variable names |
|---|---|---:|---|
| climate_geography | IHS4 Consumption Aggregate | 2 | ea_id;area |
| climate_geography | AG_MOD_J | 2 | ag_j06e;ag_j06e_oth |
| climate_geography | AG_MOD_B1 | 2 | ag_b105e;ag_b105e_oth |
| climate_geography | AG_MOD_I1 | 2 | ag_i106c;ag_i106c_oth |
| climate_geography | AG_MOD_O1 | 2 | ag_o105e;ag_o105e_oth |
| climate_geography | HH_MOD_A_FILT | 1 | ea_id |
| climate_geography | AG_MOD_C | 1 | ag_c05e |
| consumption_or_income | HH_MOD_I1 | 5 | case_id;hh_i01;hh_i02;hh_i03;HHID |
| consumption_or_income | HH_MOD_I2 | 3 | case_id;hh_i04;hh_i05 |
| consumption_or_income | HH_MOD_G1 | 2 | hh_g00_2;hh_g00_1 |
| consumption_or_income | HH_MOD_K1 | 1 | hh_k03 |
| consumption_or_income | HH_MOD_K2 | 1 | hh_k03 |
| health_need_and_access | HH_MOD_D | 7 | hh_d04;hh_d05_oth;hh_d34a;hh_d34b;hh_d11;hh_d13;hh_d14 |
| health_need_and_access | COM_CD | 4 | com_cd60a;com_cd53;com_cd54;com_cd51a |
| health_need_and_access | AG_MOD_D | 1 | ag_d25_2a |
| household_person_keys | HH_MOD_B | 1 | case_id |
| household_person_keys | AG_MOD_J | 1 | case_id |
| household_person_keys | AG_MOD_B1 | 1 | case_id |
| household_person_keys | AG_MOD_C | 1 | case_id |
| household_person_keys | AG_MOD_I1 | 1 | case_id |
| household_person_keys | AG_MOD_O1 | 1 | case_id |
| household_person_keys | AG_MOD_O2 | 1 | case_id |
| household_person_keys | HH_METADATA | 1 | case_id |
| oop_health_expenditure | HH_MOD_D | 10 | hh_d11;hh_d12;hh_d12_1;hh_d15;hh_d16;hh_d10;hh_d14;hh_d19;hh_d20;hh_d21 |
| survey_timing | HH_METADATA | 10 | moduleB_start_date;moduleF_start_date;moduleJ_start_date;moduleK_start_date;moduleL_start_date;moduleM_start_date;moduleN_start_date;moduleO_start_date;moduleP_start_date;moduleQ_start_date |
| survey_timing | COM_CA | 1 | InterviewDate |
| survey_timing | HH_MOD_A_FILT | 1 | interviewDate |
| weights_and_design | HH_MOD_A_FILT | 1 | ea_id |
| weights_and_design | IHS4 Consumption Aggregate | 1 | ea_id |
| weights_and_design | com_ch | 1 | ea_id |

Guardrail: these candidates are not raw value verification. Do not promote
this wave until the original raw package confirms values, labels, units,
recall periods, missing codes, skip patterns, merge keys, survey design,
timing/geography, and accepted climate linkage.
