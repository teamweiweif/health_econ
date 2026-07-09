# Priority LSMS-ISA Variable Evidence

Dataset: NGA_2012_GHSP-W2_v02_M - Nigeria 2012-2013

Status: official public metadata candidate variables only.

## Requirement Coverage

| Requirement | Candidate variables | Strong candidates | Candidate files | Status |
|---|---:|---:|---:|---|
| household_person_keys | 12 | 12 | 12 | official_metadata_strong_candidates_present_raw_review_required |
| weights_and_design | 12 | 12 | 4 | official_metadata_strong_candidates_present_raw_review_required |
| consumption_or_income | 12 | 12 | 4 | official_metadata_strong_candidates_present_raw_review_required |
| oop_health_expenditure | 6 | 6 | 1 | official_metadata_strong_candidates_present_raw_review_required |
| health_need_and_access | 12 | 9 | 3 | official_metadata_strong_candidates_present_raw_review_required |
| survey_timing | 12 | 12 | 1 | official_metadata_strong_candidates_present_raw_review_required |
| climate_geography | 12 | 4 | 5 | official_metadata_strong_candidates_present_raw_review_required |
| missing_codes_units_recall_skip_patterns | 0 | 0 | 0 | documentation_and_raw_review_required_no_variable_shortlist |

## File Shortlist

| Requirement | File | Candidate variables | Top variable names |
|---|---|---:|---|
| climate_geography | HHTrack | 4 | ea;lga;state;zone |
| climate_geography | secta_harvestw2 | 4 | ea;lga;state;zone |
| climate_geography | NGA_HouseholdGeovars_Y2 | 2 | LAT_DD_MOD;LON_DD_MOD |
| climate_geography | cons_agg_wave2_visit1 | 1 | ea |
| climate_geography | cons_agg_wave2_visit2 | 1 | ea |
| consumption_or_income | cons_agg_wave2_visit1 | 5 | totcons;nfdfoth;fdfishpr;fdothpr;fdrestby |
| consumption_or_income | cons_agg_wave2_visit2 | 5 | totcons;nfdfoth;fdfishpr;fdothpr;fdrestby |
| consumption_or_income | sect8e_plantingw2 | 1 | s8q10 |
| consumption_or_income | sect8a_plantingw2 | 1 | ea |
| health_need_and_access | sect4a_harvestw2 | 9 | s4aq15;s4aq16;s4aq17;s4aq1;s4aq3;s4aq20;s4aq6a;s4aq6b;s4aq6c |
| health_need_and_access | secta7_harvestw2 | 2 | cost_cd;cost_desc |
| health_need_and_access | sect4b_harvestw2 | 1 | s4bq3 |
| household_person_keys | sect1_plantingw2 | 1 | hhid |
| household_person_keys | sect1_harvestw2 | 1 | hhid |
| household_person_keys | secta10_harvestw2 | 1 | hhid |
| household_person_keys | sect11a_plantingw2 | 1 | hhid |
| household_person_keys | sect11a1_plantingw2 | 1 | hhid |
| household_person_keys | sect12_plantingw2 | 1 | hhid |
| household_person_keys | HHTrack | 1 | hhid |
| household_person_keys | secta_harvestw2 | 1 | hhid |
| oop_health_expenditure | sect4a_harvestw2 | 6 | s4aq20;s4aq20b;s4aq13;s4aq35a;s4aq35b;s4aq35c |
| survey_timing | secta_harvestw2 | 12 | saq14ah;saq14am;saq14bh;saq14bm;saq18ah;saq18am;saq18bh;saq18bm;saq22ah;saq22am;saq22bh;saq22bm |
| weights_and_design | HHTrack | 7 | wt_combined;wt_w1v1;wt_w1v2;wt_w2v1;wt_w2v2;wt_wave1;wt_wave2 |
| weights_and_design | cons_agg_wave2_visit1 | 2 | ea;hhweight |
| weights_and_design | cons_agg_wave2_visit2 | 2 | ea;hhweight |
| weights_and_design | secta_harvestw2 | 1 | wt_combined |

Guardrail: these candidates are not raw value verification. Do not promote
this wave until the original raw package confirms values, labels, units,
recall periods, missing codes, skip patterns, merge keys, survey design,
timing/geography, and accepted climate linkage.
