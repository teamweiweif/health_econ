# Priority LSMS-ISA Raw Value Verification Workbook

Dataset: `NPL_2010_LSS-III_v01_M` - Nepal 2010-2011

Official get-microdata URL: https://microdata.worldbank.org/catalog/1000/get-microdata

Target folder: `temp/raw_downloads/NPL_2010_LSS-III_v01_M/`

Current status: blocked until the complete original raw package and
documentation are present and readable.

## Requirement Checklist

| requirement | requirement_role | candidate_variable_rows | candidate_file_rows | current_verification_status |
|---|---|---|---|---|
| household_person_keys | merge_key_gate | 12 | 4 | blocked_no_original_package |
| weights_and_design | survey_design_gate | 12 | 12 | blocked_no_original_package |
| consumption_or_income | financial_denominator_gate | 12 | 3 | blocked_no_original_package |
| oop_health_expenditure | financial_outcome_gate | 6 | 1 | blocked_no_original_package |
| health_need_and_access | access_outcome_gate | 12 | 4 | blocked_no_original_package |
| survey_timing | climate_timing_gate | 12 | 3 | blocked_no_original_package |
| climate_geography | climate_geography_gate | 12 | 5 | blocked_no_original_package |
| missing_codes_units_recall_skip_patterns | documentation_semantics_gate | 0 | 0 | blocked_no_original_package |

## File Review Preview

| requirement | file_name | candidate_variable_rows | top_variable_names | current_file_verification_status |
|---|---|---|---|---|
| climate_geography | S00 | 4 | v00_zone;v00_headn;v00_team;v00_ward | blocked_no_original_package |
| climate_geography | FINAL_PREF | 4 | district;district_name;Eastern;HEAD___ | blocked_no_original_package |
| climate_geography | S04 | 2 | v04_03b;v04_11b | blocked_no_original_package |
| climate_geography | S01 | 1 | v01_05b | blocked_no_original_package |
| climate_geography | S21 | 1 | v21_ward | blocked_no_original_package |
| consumption_or_income | FINAL_PREF | 8 | sh_nonfood_30;sh_nonfood_7;nonfood_30;nonfood_7;nonfood_pc_30;nonfood_pc_7;nonfood_pc_7_tadj;nfood | blocked_no_original_package |
| consumption_or_income | S06B | 2 | v06b_idc;v06b_itm | blocked_no_original_package |
| consumption_or_income | S06A | 2 | v06a_idc;v06a_itm | blocked_no_original_package |
| health_need_and_access | S08 | 6 | v08_12;v08_17b;v08_14;v08_16;v08_17a;v08_17c | blocked_no_original_package |
| health_need_and_access | S19 | 2 | v19_09;v19_05 | blocked_no_original_package |
| health_need_and_access | S09B | 2 | v09_18;v09_24 | blocked_no_original_package |
| health_need_and_access | S03 | 2 | v03_03a;v03_03b | blocked_no_original_package |

## Workbook Files

- `temp/priority_lsms_isa_raw_value_requirement_workbook.csv`
- `temp/priority_lsms_isa_raw_value_variable_workbook.csv`
- `temp/priority_lsms_isa_raw_value_file_workbook.csv`

## Stop Rule

Do not mark this wave as value-verified or analysis-ready until the workbook
evidence fields are filled from original raw files and all required gates pass.
