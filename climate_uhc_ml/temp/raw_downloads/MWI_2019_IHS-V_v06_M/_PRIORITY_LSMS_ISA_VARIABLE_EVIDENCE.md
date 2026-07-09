# Priority LSMS-ISA Variable Evidence

Dataset: MWI_2019_IHS-V_v06_M - Malawi 2019-2020

Status: official public metadata candidate variables only.

## Requirement Coverage

| Requirement | Candidate variables | Strong candidates | Candidate files | Status |
|---|---:|---:|---:|---|
| household_person_keys | 12 | 12 | 12 | official_metadata_strong_candidates_present_raw_review_required |
| weights_and_design | 12 | 12 | 11 | official_metadata_strong_candidates_present_raw_review_required |
| consumption_or_income | 12 | 12 | 6 | official_metadata_strong_candidates_present_raw_review_required |
| oop_health_expenditure | 12 | 12 | 1 | official_metadata_strong_candidates_present_raw_review_required |
| health_need_and_access | 12 | 12 | 2 | official_metadata_strong_candidates_present_raw_review_required |
| survey_timing | 12 | 12 | 3 | official_metadata_strong_candidates_present_raw_review_required |
| climate_geography | 12 | 12 | 7 | official_metadata_strong_candidates_present_raw_review_required |
| missing_codes_units_recall_skip_patterns | 0 | 0 | 0 | documentation_and_raw_review_required_no_variable_shortlist |

## File Shortlist

| Requirement | File | Candidate variables | Top variable names |
|---|---|---:|---|
| climate_geography | householdgeovariables_ihs5.dta | 3 | ea_id;ea_lat_mod;ea_lon_mod |
| climate_geography | ihs5_consumption_aggregate.dta | 2 | area;ea_id |
| climate_geography | ag_mod_j.dta | 2 | ag_j06e;ag_j06e_oth |
| climate_geography | ag_mod_o2.dta | 2 | ag_o05e;ag_o05e_oth |
| climate_geography | hh_mod_a_filt.dta | 1 | ea_id |
| climate_geography | ag_mod_c.dta | 1 | ag_c05e_oth |
| climate_geography | HH_MOD_F1.dta | 1 | hh_f102e |
| consumption_or_income | HH_MOD_I1.dta | 5 | case_id;hh_i01;hh_i02;hh_i03;HHID |
| consumption_or_income | HH_MOD_G1.dta | 2 | hh_g00_2;hh_g00_1 |
| consumption_or_income | HH_MOD_I2.dta | 2 | case_id;hh_i04 |
| consumption_or_income | HH_MOD_K1.dta | 1 | hh_k03 |
| consumption_or_income | HH_MOD_K2.dta | 1 | hh_k03 |
| consumption_or_income | HH_MOD_T.dta | 1 | hh_t01 |
| health_need_and_access | HH_MOD_D.dta | 8 | hh_d34a;hh_d34b;hh_d04;hh_d05_oth;hh_d11;hh_d13;hh_d14;hh_d05a |
| health_need_and_access | com_cd.dta | 4 | com_cd60a;com_cd53;com_cd54;com_cd51a |
| household_person_keys | HH_MOD_B.dta | 1 | case_id |
| household_person_keys | ag_mod_c.dta | 1 | case_id |
| household_person_keys | ag_mod_j.dta | 1 | case_id |
| household_person_keys | ag_mod_o2.dta | 1 | case_id |
| household_person_keys | HH_MOD_F1.dta | 1 | case_id |
| household_person_keys | HH_MOD_N2.dta | 1 | HHID |
| household_person_keys | HH_MOD_X.dta | 1 | HHID |
| household_person_keys | HH_MOD_D.dta | 1 | PID |
| oop_health_expenditure | HH_MOD_D.dta | 12 | hh_d11;hh_d12;hh_d12_1;hh_d15;hh_d16;hh_d10;hh_d13;hh_d14;hh_d19;hh_d20;hh_d21;hh_d31 |
| survey_timing | HH_MOD_META.dta | 10 | module_f_1_start_date;moduleB_start_date;moduleF_start_date;moduleJ_start_date;moduleK_start_date;moduleL_start_date;moduleM_startdate;moduleN_start_date;moduleO_start_date;moduleP_start_date |
| survey_timing | hh_mod_a_filt.dta | 1 | interviewDate |
| survey_timing | com_ca.dta | 1 | InterviewDate |
| weights_and_design | hh_mod_a_filt.dta | 2 | ea_id;hh_wgt |
| weights_and_design | householdgeovariables_ihs5.dta | 1 | ea_id |
| weights_and_design | ihs5_consumption_aggregate.dta | 1 | ea_id |

Guardrail: these candidates are not raw value verification. Do not promote
this wave until the original raw package confirms values, labels, units,
recall periods, missing codes, skip patterns, merge keys, survey design,
timing/geography, and accepted climate linkage.
