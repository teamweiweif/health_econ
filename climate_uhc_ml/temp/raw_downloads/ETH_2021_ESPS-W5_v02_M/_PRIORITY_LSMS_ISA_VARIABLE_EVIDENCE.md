# Priority LSMS-ISA Variable Evidence

Dataset: ETH_2021_ESPS-W5_v02_M - Ethiopia 2021-2022

Status: official public metadata candidate variables only.

## Requirement Coverage

| Requirement | Candidate variables | Strong candidates | Candidate files | Status |
|---|---:|---:|---:|---|
| household_person_keys | 12 | 12 | 11 | official_metadata_strong_candidates_present_raw_review_required |
| weights_and_design | 12 | 12 | 11 | official_metadata_strong_candidates_present_raw_review_required |
| consumption_or_income | 12 | 12 | 1 | official_metadata_strong_candidates_present_raw_review_required |
| oop_health_expenditure | 12 | 12 | 2 | official_metadata_strong_candidates_present_raw_review_required |
| health_need_and_access | 12 | 9 | 3 | official_metadata_strong_candidates_present_raw_review_required |
| survey_timing | 12 | 8 | 10 | official_metadata_strong_candidates_present_raw_review_required |
| climate_geography | 12 | 12 | 6 | official_metadata_strong_candidates_present_raw_review_required |
| missing_codes_units_recall_skip_patterns | 0 | 0 | 0 | documentation_and_raw_review_required_no_variable_shortlist |

## File Shortlist

| Requirement | File | Candidate variables | Top variable names |
|---|---|---:|---|
| climate_geography | sect_cover_hh_w5.dta | 2 | saq19__Latitude;saq19__Longitude |
| climate_geography | sect10a_com_w5.dta | 2 | cs10q05__Latitude;cs10q05__Longitude |
| climate_geography | sect_cover_pp_w5.dta | 2 | saq19__Latitude;saq19__Longitude |
| climate_geography | sect_cover_ph_w5.dta | 2 | saq19__Latitude;saq19__Longitude |
| climate_geography | sect_cover_ls_w5.dta | 2 | saq19__Latitude;saq19__Longitude |
| climate_geography | sect3_pp_w5.dta | 2 | s3q09__Latitude;s3q09__Longitude |
| consumption_or_income | cons_agg_w5.dta | 12 | nonfood_cons2;nom_nonfoodcons_aeq;nonfood_cons_ann;food_cons2;food_cons_ann;nom_foodcons_aeq;fafh_cons_ann;spat_totcons_aeq;educ_cons_ann;nom_educcons_aeq;nom_totcons_aeq;total_cons_ann |
| health_need_and_access | sect3_hh_w5.dta | 6 | s3q14;s3q15;s3q05;s3q17;s3q13;s3q18 |
| health_need_and_access | sect04_com_w5.dta | 4 | cs4q37;cs4q34;cs4q35;cs4q28 |
| health_need_and_access | sect3_pp_w5.dta | 2 | s3q15_1;s3q15_2 |
| household_person_keys | sect1_hh_w5.dta | 2 | individual_id;household_id |
| household_person_keys | sect12b1_hh_w5.dta | 1 | household_id |
| household_person_keys | sect1_pp_w5.dta | 1 | household_id |
| household_person_keys | sect1_ph_w5.dta | 1 | household_id |
| household_person_keys | sect2_pp_w5.dta | 1 | household_id |
| household_person_keys | sect3_pp_w5.dta | 1 | household_id |
| household_person_keys | sect4_pp_w5.dta | 1 | household_id |
| household_person_keys | sect6c_hh_w5.dta | 1 | individual_id |
| oop_health_expenditure | sect8_3_ls_w5.dta | 10 | ls_s8_3q04;ls_s8_3q22;ls_s8_3q24;ls_s8_3q03;ls_s8_3q05;ls_s8_3q06;ls_s8_3q10a;ls_s8_3q10b;ls_s8_3q11;ls_s8_3q12_1 |
| oop_health_expenditure | sect3_hh_w5.dta | 2 | s3q17;s3q18 |
| survey_timing | sect_cover_pp_w5.dta | 1 | InterviewDate |
| survey_timing | sect_cover_ph_w5.dta | 1 | InterviewDate |
| survey_timing | sect_cover_ls_w5.dta | 1 | InterviewDate |
| survey_timing | sect12b1_hh_w5.dta | 2 | s12bq08a;s12bq08b |
| survey_timing | sect7b_hh_w5.dta | 2 | item_cd_12months;s7q04 |
| survey_timing | eth_householdgeovariables_y5.dta | 1 | wetQ_avgstart |
| survey_timing | sect_cover_hh_w5.dta | 1 | saq19__Timestamp |
| survey_timing | eth_plotgeovariables_y5.dta | 1 | wetQ_avgstart |
| weights_and_design | sect_cover_hh_w5.dta | 2 | pw_w5;ea_id |
| weights_and_design | sect6b2_hh_w5.dta | 1 | pw_w5 |

Guardrail: these candidates are not raw value verification. Do not promote
this wave until the original raw package confirms values, labels, units,
recall periods, missing codes, skip patterns, merge keys, survey design,
timing/geography, and accepted climate linkage.
