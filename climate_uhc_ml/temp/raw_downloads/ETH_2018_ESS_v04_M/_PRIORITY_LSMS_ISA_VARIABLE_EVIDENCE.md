# Priority LSMS-ISA Variable Evidence

Dataset: ETH_2018_ESS_v04_M - Ethiopia 2018-2019

Status: official public metadata candidate variables only.

## Requirement Coverage

| Requirement | Candidate variables | Strong candidates | Candidate files | Status |
|---|---:|---:|---:|---|
| household_person_keys | 12 | 12 | 10 | official_metadata_strong_candidates_present_raw_review_required |
| weights_and_design | 12 | 12 | 12 | official_metadata_strong_candidates_present_raw_review_required |
| consumption_or_income | 12 | 12 | 2 | official_metadata_strong_candidates_present_raw_review_required |
| oop_health_expenditure | 12 | 12 | 2 | official_metadata_strong_candidates_present_raw_review_required |
| health_need_and_access | 12 | 12 | 2 | official_metadata_strong_candidates_present_raw_review_required |
| survey_timing | 12 | 9 | 7 | official_metadata_strong_candidates_present_raw_review_required |
| climate_geography | 12 | 12 | 6 | official_metadata_strong_candidates_present_raw_review_required |
| missing_codes_units_recall_skip_patterns | 0 | 0 | 0 | documentation_and_raw_review_required_no_variable_shortlist |

## File Shortlist

| Requirement | File | Candidate variables | Top variable names |
|---|---|---:|---|
| climate_geography | sect_cover_ph_w4.dta | 3 | saq19__Latitude;saq19__Longitude;ea_id |
| climate_geography | sect_cover_pp_w4.dta | 2 | saq19__Latitude;saq19__Longitude |
| climate_geography | sect_cover_ls_w4.dta | 2 | saq19__Latitude;saq19__Longitude |
| climate_geography | sect3_pp_w4.dta | 2 | s3q09__Latitude;s3q09__Longitude |
| climate_geography | sect10a_com_w4.dta | 2 | cs10q05__Latitude;cs10q05__Longitude |
| climate_geography | sect_cover_hh_w4.dta | 1 | ea_id |
| consumption_or_income | sect7a_hh_w4.dta | 9 | ea_id;household_id;item_cd_30day;pw_w4;s7q01;s7q02;saq01;saq02;saq03 |
| consumption_or_income | cons_agg_w4.dta | 3 | nom_nonfoodcons_aeq;nonfood_cons_ann;food_cons_ann |
| health_need_and_access | sect3_hh_w4.dta | 11 | s3q14;s3q15;s3q05;s3q17;s3q13;s3q18;s3q06_1;s3q06_2;s3q06_os;s3q09a;s3q09b |
| health_need_and_access | sect04_com_w4.dta | 1 | cs4q37 |
| household_person_keys | sect1_hh_w4.dta | 2 | individual_id;household_id |
| household_person_keys | sect11b1_hh_w4.dta | 2 | individual_id;household_id |
| household_person_keys | sect10d1_hh_w4.dta | 1 | household_id |
| household_person_keys | sect1_ph_w4.dta | 1 | household_id |
| household_person_keys | sect1_pp_w4.dta | 1 | household_id |
| household_person_keys | sect10b_hh_w4.dta | 1 | household_id |
| household_person_keys | sect2_pp_w4.dta | 1 | household_id |
| household_person_keys | sect3_pp_w4.dta | 1 | household_id |
| oop_health_expenditure | sect8_3_ls_w4.dta | 10 | ls_s8_3q04;ls_s8_3q22;ls_s8_3q24;ls_s8_3q03;ls_s8_3q05;ls_s8_3q06;ls_s8_3q10a;ls_s8_3q10b;ls_s8_3q11;ls_s8_3q12_1 |
| oop_health_expenditure | sect3_hh_w4.dta | 2 | s3q17;s3q18 |
| survey_timing | sect_cover_ph_w4.dta | 2 | InterviewDate;saq19__Timestamp |
| survey_timing | sect_cover_pp_w4.dta | 2 | InterviewDate;saq19__Timestamp |
| survey_timing | sect_cover_ls_w4.dta | 2 | InterviewDate;saq19__Timestamp |
| survey_timing | sect12b1_hh_w4.dta | 2 | s12bq08a;s12bq08b |
| survey_timing | ETH_HouseholdGeovariables_Y4.dta | 2 | wetQ_avgstart;h2018_wetQstart |
| survey_timing | sect_cover_hh_w4.dta | 1 | InterviewStart |
| survey_timing | sect15b_hh_w4.dta | 1 | s15q06b |
| weights_and_design | sect_cover_hh_w4.dta | 1 | ea_id |
| weights_and_design | sect_cover_ph_w4.dta | 1 | ea_id |
| weights_and_design | sect_cover_pp_w4.dta | 1 | ea_id |

Guardrail: these candidates are not raw value verification. Do not promote
this wave until the original raw package confirms values, labels, units,
recall periods, missing codes, skip patterns, merge keys, survey design,
timing/geography, and accepted climate linkage.
