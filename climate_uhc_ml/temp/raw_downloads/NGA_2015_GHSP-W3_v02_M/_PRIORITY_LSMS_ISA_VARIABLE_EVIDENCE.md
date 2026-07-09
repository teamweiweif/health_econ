# Priority LSMS-ISA Variable Evidence

Dataset: NGA_2015_GHSP-W3_v02_M - Nigeria 2015-2016

Status: official public metadata candidate variables only.

## Requirement Coverage

| Requirement | Candidate variables | Strong candidates | Candidate files | Status |
|---|---:|---:|---:|---|
| household_person_keys | 12 | 12 | 12 | official_metadata_strong_candidates_present_raw_review_required |
| weights_and_design | 12 | 12 | 5 | official_metadata_strong_candidates_present_raw_review_required |
| consumption_or_income | 12 | 12 | 3 | official_metadata_strong_candidates_present_raw_review_required |
| oop_health_expenditure | 6 | 6 | 1 | official_metadata_strong_candidates_present_raw_review_required |
| health_need_and_access | 12 | 8 | 2 | official_metadata_strong_candidates_present_raw_review_required |
| survey_timing | 12 | 12 | 1 | official_metadata_strong_candidates_present_raw_review_required |
| climate_geography | 12 | 12 | 6 | official_metadata_strong_candidates_present_raw_review_required |
| missing_codes_units_recall_skip_patterns | 0 | 0 | 0 | documentation_and_raw_review_required_no_variable_shortlist |

## File Shortlist

| Requirement | File | Candidate variables | Top variable names |
|---|---|---:|---|
| climate_geography | sect1_harvestw3 | 4 | s1q31a;s1q31b;s1q31c;s1q31d |
| climate_geography | NGA_HouseholdGeovars_Y3 | 2 | LAT_DD_MOD;LON_DD_MOD |
| climate_geography | sectc1_harvestw3 | 2 | ea;lga |
| climate_geography | sectc2_harvestw3 | 2 | ea;lga |
| climate_geography | cons_agg_wave3_visit1 | 1 | ea |
| climate_geography | cons_agg_wave3_visit2 | 1 | ea |
| consumption_or_income | cons_agg_wave3_visit1 | 5 | totcons;nfdfoth;fdfishpr;fdothpr;fdrestby |
| consumption_or_income | cons_agg_wave3_visit2 | 5 | totcons;nfdfoth;fdfishpr;fdothpr;fdrestby |
| consumption_or_income | sect8a_plantingw3 | 2 | ea;hhid |
| health_need_and_access | sect4a_harvestw3 | 11 | s4aq15;s4aq16;s4aq17;s4aq1;s4aq6a;s4aq6a_os;s4aq6b;s4aq6b_os;s4aq3;s4aq3b;s4aq3b_os |
| health_need_and_access | sect3_plantingw3 | 1 | s3q9b |
| household_person_keys | sect11a_plantingw3 | 1 | hhid |
| household_person_keys | sect1_plantingw3 | 1 | hhid |
| household_person_keys | sect11a1_plantingw3 | 1 | hhid |
| household_person_keys | sect12_plantingw3 | 1 | hhid |
| household_person_keys | sect1_harvestw3 | 1 | hhid |
| household_person_keys | secta10_harvestw3 | 1 | hhid |
| household_person_keys | sect7a_plantingw3 | 1 | hhid |
| household_person_keys | sect7b_plantingw3 | 1 | hhid |
| oop_health_expenditure | sect4a_harvestw3 | 6 | s4aq20;s4aq20b;s4aq13;s4aq35a;s4aq35b;s4aq35c |
| survey_timing | secta_harvestw3 | 12 | saq14ah;saq14am;saq14bh;saq14bm;saq17ah;saq17am;saq17bh;saq17bm;saq20ah;saq20am;saq20bh;saq20bm |
| weights_and_design | HHTrack | 6 | wt_combined;wt_w1_w2_w3;wt_w1_w3;wt_w1v1;wt_w1v2;wt_w2_w3 |
| weights_and_design | cons_agg_wave3_visit1 | 2 | ea;hhweight |
| weights_and_design | cons_agg_wave3_visit2 | 2 | ea;hhweight |
| weights_and_design | sectc1_harvestw3 | 1 | ea |
| weights_and_design | sectc2_harvestw3 | 1 | ea |

Guardrail: these candidates are not raw value verification. Do not promote
this wave until the original raw package confirms values, labels, units,
recall periods, missing codes, skip patterns, merge keys, survey design,
timing/geography, and accepted climate linkage.
