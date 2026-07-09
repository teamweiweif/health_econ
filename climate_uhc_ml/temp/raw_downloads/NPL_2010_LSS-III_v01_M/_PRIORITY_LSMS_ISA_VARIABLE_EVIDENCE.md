# Priority LSMS-ISA Variable Evidence

Dataset: NPL_2010_LSS-III_v01_M - Nepal 2010-2011

Status: official public metadata candidate variables only.

## Requirement Coverage

| Requirement | Candidate variables | Strong candidates | Candidate files | Status |
|---|---:|---:|---:|---|
| household_person_keys | 12 | 5 | 4 | official_metadata_strong_candidates_present_raw_review_required |
| weights_and_design | 12 | 12 | 12 | official_metadata_strong_candidates_present_raw_review_required |
| consumption_or_income | 12 | 12 | 3 | official_metadata_strong_candidates_present_raw_review_required |
| oop_health_expenditure | 6 | 6 | 1 | official_metadata_strong_candidates_present_raw_review_required |
| health_need_and_access | 12 | 5 | 4 | official_metadata_strong_candidates_present_raw_review_required |
| survey_timing | 12 | 12 | 3 | official_metadata_strong_candidates_present_raw_review_required |
| climate_geography | 12 | 1 | 5 | official_metadata_strong_candidates_present_raw_review_required |
| missing_codes_units_recall_skip_patterns | 0 | 0 | 0 | documentation_and_raw_review_required_no_variable_shortlist |

## File Shortlist

| Requirement | File | Candidate variables | Top variable names |
|---|---|---:|---|
| climate_geography | S00 | 4 | v00_zone;v00_headn;v00_team;v00_ward |
| climate_geography | FINAL_PREF | 4 | district;district_name;Eastern;HEAD___ |
| climate_geography | S04 | 2 | v04_03b;v04_11b |
| climate_geography | S01 | 1 | v01_05b |
| climate_geography | S21 | 1 | v21_ward |
| consumption_or_income | FINAL_PREF | 8 | sh_nonfood_30;sh_nonfood_7;nonfood_30;nonfood_7;nonfood_pc_30;nonfood_pc_7;nonfood_pc_7_tadj;nfood |
| consumption_or_income | S06B | 2 | v06b_idc;v06b_itm |
| consumption_or_income | S06A | 2 | v06a_idc;v06a_itm |
| health_need_and_access | S08 | 6 | v08_12;v08_17b;v08_14;v08_16;v08_17a;v08_17c |
| health_need_and_access | S19 | 2 | v19_09;v19_05 |
| health_need_and_access | S09B | 2 | v09_18;v09_24 |
| health_need_and_access | S03 | 2 | v03_03a;v03_03b |
| household_person_keys | S01 | 8 | v01_10;REC_TYPE;v01_01;v01_02;v01_03;v01_04;v01_05a;v01_05b |
| household_person_keys | S21x | 2 | v21_10;v21_11 |
| household_person_keys | S10B | 1 | v10_02 |
| household_person_keys | S12 | 1 | v12_01 |
| oop_health_expenditure | S08 | 6 | v08_17a;v08_07a;v08_07b;v08_17b;v08_18;v08_17c |
| survey_timing | S00 | 7 | v00_int1_m;v00_int1_y;v00_int2_m;v00_int2_y;v00_int3_m;v00_int3_y;v00_sup_m |
| survey_timing | sys | 4 | hsys_c1date;hsys_u1date;hsys_c2date;hsys_u2date |
| survey_timing | FINAL_PREF | 1 | Date |
| weights_and_design | anthro | 1 | weight |
| weights_and_design | S06B | 1 | xhpsu |
| weights_and_design | S06C | 1 | xhpsu |
| weights_and_design | S06D | 1 | xhpsu |
| weights_and_design | S09D | 1 | xhpsu |
| weights_and_design | S15D | 1 | xhpsu |
| weights_and_design | S01 | 1 | xhpsu |
| weights_and_design | S21 | 1 | xhpsu |

Guardrail: these candidates are not raw value verification. Do not promote
this wave until the original raw package confirms values, labels, units,
recall periods, missing codes, skip patterns, merge keys, survey design,
timing/geography, and accepted climate linkage.
