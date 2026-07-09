# Priority LSMS-ISA Raw Value Verification Workbook

Dataset: `ETH_2018_ESS_v04_M` - Ethiopia 2018-2019

Official get-microdata URL: https://microdata.worldbank.org/catalog/3823/get-microdata

Target folder: `temp/raw_downloads/ETH_2018_ESS_v04_M/`

Current status: blocked until the complete original raw package and
documentation are present and readable.

## Requirement Checklist

| requirement | requirement_role | candidate_variable_rows | candidate_file_rows | current_verification_status |
|---|---|---|---|---|
| household_person_keys | merge_key_gate | 12 | 10 | blocked_no_original_package |
| weights_and_design | survey_design_gate | 12 | 12 | blocked_no_original_package |
| consumption_or_income | financial_denominator_gate | 12 | 2 | blocked_no_original_package |
| oop_health_expenditure | financial_outcome_gate | 12 | 2 | blocked_no_original_package |
| health_need_and_access | access_outcome_gate | 12 | 2 | blocked_no_original_package |
| survey_timing | climate_timing_gate | 12 | 7 | blocked_no_original_package |
| climate_geography | climate_geography_gate | 12 | 6 | blocked_no_original_package |
| missing_codes_units_recall_skip_patterns | documentation_semantics_gate | 0 | 0 | blocked_no_original_package |

## File Review Preview

| requirement | file_name | candidate_variable_rows | top_variable_names | current_file_verification_status |
|---|---|---|---|---|
| climate_geography | sect_cover_ph_w4.dta | 3 | saq19__Latitude;saq19__Longitude;ea_id | blocked_no_original_package |
| climate_geography | sect_cover_pp_w4.dta | 2 | saq19__Latitude;saq19__Longitude | blocked_no_original_package |
| climate_geography | sect_cover_ls_w4.dta | 2 | saq19__Latitude;saq19__Longitude | blocked_no_original_package |
| climate_geography | sect3_pp_w4.dta | 2 | s3q09__Latitude;s3q09__Longitude | blocked_no_original_package |
| climate_geography | sect10a_com_w4.dta | 2 | cs10q05__Latitude;cs10q05__Longitude | blocked_no_original_package |
| climate_geography | sect_cover_hh_w4.dta | 1 | ea_id | blocked_no_original_package |
| consumption_or_income | sect7a_hh_w4.dta | 9 | ea_id;household_id;item_cd_30day;pw_w4;s7q01;s7q02;saq01;saq02;saq03 | blocked_no_original_package |
| consumption_or_income | cons_agg_w4.dta | 3 | nom_nonfoodcons_aeq;nonfood_cons_ann;food_cons_ann | blocked_no_original_package |
| health_need_and_access | sect3_hh_w4.dta | 11 | s3q14;s3q15;s3q05;s3q17;s3q13;s3q18;s3q06_1;s3q06_2;s3q06_os;s3q09a;s3q09b | blocked_no_original_package |
| health_need_and_access | sect04_com_w4.dta | 1 | cs4q37 | blocked_no_original_package |
| household_person_keys | sect1_hh_w4.dta | 2 | individual_id;household_id | blocked_no_original_package |
| household_person_keys | sect11b1_hh_w4.dta | 2 | individual_id;household_id | blocked_no_original_package |

## Workbook Files

- `temp/priority_lsms_isa_raw_value_requirement_workbook.csv`
- `temp/priority_lsms_isa_raw_value_variable_workbook.csv`
- `temp/priority_lsms_isa_raw_value_file_workbook.csv`

## Stop Rule

Do not mark this wave as value-verified or analysis-ready until the workbook
evidence fields are filled from original raw files and all required gates pass.
