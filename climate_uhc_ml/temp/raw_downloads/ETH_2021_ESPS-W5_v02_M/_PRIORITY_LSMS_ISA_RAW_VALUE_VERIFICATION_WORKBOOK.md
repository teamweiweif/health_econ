# Priority LSMS-ISA Raw Value Verification Workbook

Dataset: `ETH_2021_ESPS-W5_v02_M` - Ethiopia 2021-2022

Official get-microdata URL: https://microdata.worldbank.org/catalog/6161/get-microdata

Target folder: `temp/raw_downloads/ETH_2021_ESPS-W5_v02_M/`

Current status: blocked until the complete original raw package and
documentation are present and readable.

## Requirement Checklist

| requirement | requirement_role | candidate_variable_rows | candidate_file_rows | current_verification_status |
|---|---|---|---|---|
| household_person_keys | merge_key_gate | 12 | 11 | blocked_no_original_package |
| weights_and_design | survey_design_gate | 12 | 11 | blocked_no_original_package |
| consumption_or_income | financial_denominator_gate | 12 | 1 | blocked_no_original_package |
| oop_health_expenditure | financial_outcome_gate | 12 | 2 | blocked_no_original_package |
| health_need_and_access | access_outcome_gate | 12 | 3 | blocked_no_original_package |
| survey_timing | climate_timing_gate | 12 | 10 | blocked_no_original_package |
| climate_geography | climate_geography_gate | 12 | 6 | blocked_no_original_package |
| missing_codes_units_recall_skip_patterns | documentation_semantics_gate | 0 | 0 | blocked_no_original_package |

## File Review Preview

| requirement | file_name | candidate_variable_rows | top_variable_names | current_file_verification_status |
|---|---|---|---|---|
| climate_geography | sect_cover_hh_w5.dta | 2 | saq19__Latitude;saq19__Longitude | blocked_no_original_package |
| climate_geography | sect10a_com_w5.dta | 2 | cs10q05__Latitude;cs10q05__Longitude | blocked_no_original_package |
| climate_geography | sect_cover_pp_w5.dta | 2 | saq19__Latitude;saq19__Longitude | blocked_no_original_package |
| climate_geography | sect_cover_ph_w5.dta | 2 | saq19__Latitude;saq19__Longitude | blocked_no_original_package |
| climate_geography | sect_cover_ls_w5.dta | 2 | saq19__Latitude;saq19__Longitude | blocked_no_original_package |
| climate_geography | sect3_pp_w5.dta | 2 | s3q09__Latitude;s3q09__Longitude | blocked_no_original_package |
| consumption_or_income | cons_agg_w5.dta | 12 | nonfood_cons2;nom_nonfoodcons_aeq;nonfood_cons_ann;food_cons2;food_cons_ann;nom_foodcons_aeq;fafh_cons_ann;spat_totco... | blocked_no_original_package |
| health_need_and_access | sect3_hh_w5.dta | 6 | s3q14;s3q15;s3q05;s3q17;s3q13;s3q18 | blocked_no_original_package |
| health_need_and_access | sect04_com_w5.dta | 4 | cs4q37;cs4q34;cs4q35;cs4q28 | blocked_no_original_package |
| health_need_and_access | sect3_pp_w5.dta | 2 | s3q15_1;s3q15_2 | blocked_no_original_package |
| household_person_keys | sect1_hh_w5.dta | 2 | individual_id;household_id | blocked_no_original_package |
| household_person_keys | sect12b1_hh_w5.dta | 1 | household_id | blocked_no_original_package |

## Workbook Files

- `temp/priority_lsms_isa_raw_value_requirement_workbook.csv`
- `temp/priority_lsms_isa_raw_value_variable_workbook.csv`
- `temp/priority_lsms_isa_raw_value_file_workbook.csv`

## Stop Rule

Do not mark this wave as value-verified or analysis-ready until the workbook
evidence fields are filled from original raw files and all required gates pass.
