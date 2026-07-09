# Priority LSMS-ISA Variable Evidence

Dataset: MWI_2010_IHS-III_v01_M - Malawi 2010-2011

Status: official public metadata candidate variables only.

## Requirement Coverage

| Requirement | Candidate variables | Strong candidates | Candidate files | Status |
|---|---:|---:|---:|---|
| household_person_keys | 12 | 12 | 12 | official_metadata_strong_candidates_present_raw_review_required |
| weights_and_design | 12 | 12 | 11 | official_metadata_strong_candidates_present_raw_review_required |
| consumption_or_income | 12 | 12 | 3 | official_metadata_strong_candidates_present_raw_review_required |
| oop_health_expenditure | 5 | 4 | 1 | official_metadata_strong_candidates_present_raw_review_required |
| health_need_and_access | 12 | 11 | 2 | official_metadata_strong_candidates_present_raw_review_required |
| survey_timing | 12 | 12 | 6 | official_metadata_strong_candidates_present_raw_review_required |
| climate_geography | 12 | 12 | 10 | official_metadata_strong_candidates_present_raw_review_required |
| missing_codes_units_recall_skip_patterns | 0 | 0 | 0 | documentation_and_raw_review_required_no_variable_shortlist |

## File Shortlist

| Requirement | File | Candidate variables | Top variable names |
|---|---|---:|---|
| climate_geography | HouseholdGeovariables.NSDstat | 3 | ea_id;lat_modified;lon_modified |
| climate_geography | PlotGeovariables.NSDstat | 1 | ea_id |
| climate_geography | HH_MOD_A_FILT.NSDstat | 1 | ea_id |
| climate_geography | HH_MOD_H.NSDstat | 1 | ea_id |
| climate_geography | HH_MOD_I1.NSDstat | 1 | ea_id |
| climate_geography | HH_MOD_I2.NSDstat | 1 | ea_id |
| climate_geography | HH_MOD_J.NSDstat | 1 | ea_id |
| climate_geography | HH_MOD_K.NSDstat | 1 | ea_id |
| consumption_or_income | Round 1 (2010) Consumption Aggregate.NSDstat | 7 | rexp_cat01;rexp_cat011;epoor;pcrexpagg;poor;rexp_cat012;rexp_cat02 |
| consumption_or_income | ihs3fc2M_consumption.NSDstat | 4 | exp_cat01;exp_cat011;rexp_cat01;rexp_cat011 |
| consumption_or_income | HH_MOD_T.NSDstat | 1 | hh_t01 |
| health_need_and_access | COM_CD.NSDstat | 6 | com_cd60a;com_cd60b;com_cd53;com_cd54;com_cd51a;com_cd51b |
| health_need_and_access | HH_MOD_D.NSDstat | 6 | hh_d04;hh_d05a;hh_d05a_os;hh_d05b;hh_d05b_os;hh_d34a |
| household_person_keys | HouseholdGeovariables.NSDstat | 1 | case_id |
| household_person_keys | HH_MOD_A_FILT.NSDstat | 1 | case_id |
| household_person_keys | HH_MOD_H.NSDstat | 1 | case_id |
| household_person_keys | HH_MOD_I1.NSDstat | 1 | case_id |
| household_person_keys | HH_MOD_I2.NSDstat | 1 | case_id |
| household_person_keys | HH_MOD_J.NSDstat | 1 | case_id |
| household_person_keys | HH_MOD_K.NSDstat | 1 | case_id |
| household_person_keys | HH_MOD_L.NSDstat | 1 | case_id |
| oop_health_expenditure | HH_MOD_D.NSDstat | 5 | hh_d11;hh_d15;hh_d16;hh_d21;hh_d14 |
| survey_timing | HH_MOD_A_FILT.NSDstat | 4 | hh_a23_1;hh_a23_2;hh_a23b_1;hh_a23b_2 |
| survey_timing | AG_MOD_B.NSDstat | 2 | ag_b05a;ag_b05b |
| survey_timing | AG_MOD_G.NSDstat | 2 | ag_g12a;ag_g12b |
| survey_timing | AG_MOD_M.NSDstat | 2 | ag_m12a;ag_m12b |
| survey_timing | COM_CA.NSDstat | 1 | com_ca07 |
| survey_timing | Round 1 (2010) Consumption Aggregate.NSDstat | 1 | intmonth |
| weights_and_design | Round 1 (2010) Consumption Aggregate.NSDstat | 2 | hhweight;strata |
| weights_and_design | HouseholdGeovariables.NSDstat | 1 | ea_id |

Guardrail: these candidates are not raw value verification. Do not promote
this wave until the original raw package confirms values, labels, units,
recall periods, missing codes, skip patterns, merge keys, survey design,
timing/geography, and accepted climate linkage.
