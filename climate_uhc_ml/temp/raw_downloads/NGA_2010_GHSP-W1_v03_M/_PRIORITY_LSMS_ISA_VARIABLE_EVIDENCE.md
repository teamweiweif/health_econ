# Priority LSMS-ISA Variable Evidence

Dataset: NGA_2010_GHSP-W1_v03_M - Nigeria 2010-2011

Status: official public metadata candidate variables only.

## Requirement Coverage

| Requirement | Candidate variables | Strong candidates | Candidate files | Status |
|---|---:|---:|---:|---|
| household_person_keys | 12 | 12 | 12 | official_metadata_strong_candidates_present_raw_review_required |
| weights_and_design | 12 | 4 | 8 | official_metadata_strong_candidates_present_raw_review_required |
| consumption_or_income | 12 | 12 | 2 | official_metadata_strong_candidates_present_raw_review_required |
| oop_health_expenditure | 5 | 5 | 1 | official_metadata_strong_candidates_present_raw_review_required |
| health_need_and_access | 12 | 8 | 3 | official_metadata_strong_candidates_present_raw_review_required |
| survey_timing | 12 | 12 | 2 | official_metadata_strong_candidates_present_raw_review_required |
| climate_geography | 12 | 12 | 3 | official_metadata_strong_candidates_present_raw_review_required |
| missing_codes_units_recall_skip_patterns | 0 | 0 | 0 | documentation_and_raw_review_required_no_variable_shortlist |

## File Shortlist

| Requirement | File | Candidate variables | Top variable names |
|---|---|---:|---|
| climate_geography | NGA_HouseholdGeovariables_Y1 | 10 | lat_dd_mod;lon_dd_mod;ea;eviarea_avg;grn_avg;h2010_eviarea;h2010_grn;h2010_sen;lga;sen_avg |
| climate_geography | cons_agg_wave1_visit1 | 1 | ea |
| climate_geography | cons_agg_wave1_visit2 | 1 | ea |
| consumption_or_income | cons_agg_wave1_visit1 | 7 | totcons;nfdfoth;fdfishpr;fdothpr;fdrestby;fdalcpr;fdbeanpr |
| consumption_or_income | cons_agg_wave1_visit2 | 5 | totcons;nfdfoth;fdfishpr;fdothpr;fdrestby |
| health_need_and_access | sect4a_harvestw1 | 10 | s4aq15;s4aq16;s4aq17;s4aq1;s4aq3;s4aq6a;s4aq6b;s4aq6c;s4aq20;s4aq20b |
| health_need_and_access | sect4b_harvestw1 | 1 | s4bq3 |
| health_need_and_access | sect3a_harvestw1 | 1 | s3aq17 |
| household_person_keys | secta7_harvestw1 | 1 | hhid |
| household_person_keys | secta8_harvestw1 | 1 | hhid |
| household_person_keys | secta9a1_harvestw1 | 1 | hhid |
| household_person_keys | secta9a2_harvestw1 | 1 | hhid |
| household_person_keys | secta9b1_harvestw1 | 1 | hhid |
| household_person_keys | secta9b2_harvestw1 | 1 | hhid |
| household_person_keys | secta10_harvestw1 | 1 | hhid |
| household_person_keys | secta41_harvestw1 | 1 | hhid |
| oop_health_expenditure | sect4a_harvestw1 | 5 | s4aq20;s4aq20b;s4aq19;s4aq13;s4aq17 |
| survey_timing | secta_harvestw1 | 11 | saq14ah;saq14am;saq14bh;saq14bm;saq18ah;saq18am;saq18bh;saq18bm;saq22ah;saq22am;saq22bh |
| survey_timing | sectc_plantingw1 | 1 | interview_date |
| weights_and_design | cons_agg_wave1_visit1 | 2 | ea;hhweight |
| weights_and_design | cons_agg_wave1_visit2 | 2 | ea;hhweight |
| weights_and_design | NGA_HouseholdGeovariables_Y1 | 3 | ea;eviarea_avg;h2010_eviarea |
| weights_and_design | secta7_harvestw1 | 1 | ea |
| weights_and_design | secta8_harvestw1 | 1 | ea |
| weights_and_design | secta9a1_harvestw1 | 1 | ea |
| weights_and_design | secta9a2_harvestw1 | 1 | ea |
| weights_and_design | secta9b1_harvestw1 | 1 | ea |

Guardrail: these candidates are not raw value verification. Do not promote
this wave until the original raw package confirms values, labels, units,
recall periods, missing codes, skip patterns, merge keys, survey design,
timing/geography, and accepted climate linkage.
