# Priority LSMS-ISA Variable Evidence

Dataset: TZA_2012_NPS-R3_v01_M - Tanzania 2012-2013

Status: official public metadata candidate variables only.

## Requirement Coverage

| Requirement | Candidate variables | Strong candidates | Candidate files | Status |
|---|---:|---:|---:|---|
| household_person_keys | 12 | 12 | 11 | official_metadata_strong_candidates_present_raw_review_required |
| weights_and_design | 12 | 12 | 6 | official_metadata_strong_candidates_present_raw_review_required |
| consumption_or_income | 12 | 12 | 2 | official_metadata_strong_candidates_present_raw_review_required |
| oop_health_expenditure | 12 | 12 | 1 | official_metadata_strong_candidates_present_raw_review_required |
| health_need_and_access | 12 | 2 | 6 | official_metadata_strong_candidates_present_raw_review_required |
| survey_timing | 12 | 12 | 5 | official_metadata_strong_candidates_present_raw_review_required |
| climate_geography | 12 | 12 | 5 | official_metadata_strong_candidates_present_raw_review_required |
| missing_codes_units_recall_skip_patterns | 0 | 0 | 0 | documentation_and_raw_review_required_no_variable_shortlist |

## File Shortlist

| Requirement | File | Candidate variables | Top variable names |
|---|---|---:|---|
| climate_geography | COM_SEC_A1A2.NSDstat | 4 | cm_lon_g;cm_lon_m;cm_lon_s;y3_cluster |
| climate_geography | AG_SEC_2A.NSDstat | 2 | ag2a_06_3;ag2a_06_4 |
| climate_geography | AG_SEC_A.NSDstat | 2 | ag_a04_1;ag_a04_2 |
| climate_geography | HH_SEC_A.NSDstat | 2 | hh_a04_1;hh_a04_2 |
| climate_geography | LF_SEC_A.NSDstat | 2 | lf_a04_1;lf_a04_2 |
| consumption_or_income | HH_SEC_K.NSDstat | 6 | hh_k01;hh_k02;hh_k03;itemcode;occ;y3_hhid |
| consumption_or_income | HH_SEC_L.NSDstat | 6 | hh_l01;hh_l02;hh_l03;itemcode;occ;y3_hhid |
| health_need_and_access | HH_SEC_D.NSDstat | 5 | hh_d12_1;hh_d12_2;hh_d02;hh_d13;hh_d23 |
| health_need_and_access | ConsumptionNPS3.NSDstat | 2 | health;healthR |
| health_need_and_access | LF_SEC_13B.NSDstat | 2 | costcode;costname |
| health_need_and_access | HH_SEC_G.NSDstat | 1 | hh_g03_5 |
| health_need_and_access | AG_SEC_11.NSDstat | 1 | ag11_05 |
| health_need_and_access | COM_SEC_CB.NSDstat | 1 | cm_b02 |
| household_person_keys | HH_SEC_B.NSDstat | 2 | y2_hhid;y3_hhid |
| household_person_keys | AG_SEC_01.NSDstat | 1 | y3_hhid |
| household_person_keys | AG_SEC_2A.NSDstat | 1 | y3_hhid |
| household_person_keys | AG_SEC_2B.NSDstat | 1 | y3_hhid |
| household_person_keys | LF_NETWORK.NSDstat | 1 | y3_hhid |
| household_person_keys | LF_SEC_01.NSDstat | 1 | y3_hhid |
| household_person_keys | AG_SEC_08.NSDstat | 1 | y3_hhid |
| household_person_keys | AG_SEC_11.NSDstat | 1 | y3_hhid |
| oop_health_expenditure | HH_SEC_D.NSDstat | 12 | hh_d05_1;hh_d05_2;hh_d07;hh_d08;hh_d09;hh_d13;hh_d15;hh_d20;hh_d01;hh_d02;hh_d03_1;hh_d03_2 |
| survey_timing | HH_SEC_A.NSDstat | 4 | hh_a18;hh_a18_1;hh_a18_2;hh_a18_3 |
| survey_timing | COM_SEC_A1A2.NSDstat | 4 | cm_a07;cm_a07_1;cm_a07_2;cm_a07_3 |
| survey_timing | AG_SEC_A.NSDstat | 2 | ag_a13;ag_a12_1 |
| survey_timing | LF_SEC_A.NSDstat | 1 | lf_a13 |
| survey_timing | AG_SEC_12A.NSDstat | 1 | ag12a_07 |
| weights_and_design | HH_SEC_A.NSDstat | 4 | y3_weight;strataid;hh_a04_1;hh_a04_2 |
| weights_and_design | AG_SEC_A.NSDstat | 2 | ag_a04_1;ag_a04_2 |
| weights_and_design | LF_SEC_A.NSDstat | 2 | lf_a04_1;lf_a04_2 |

Guardrail: these candidates are not raw value verification. Do not promote
this wave until the original raw package confirms values, labels, units,
recall periods, missing codes, skip patterns, merge keys, survey design,
timing/geography, and accepted climate linkage.
