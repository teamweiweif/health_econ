# Priority LSMS-ISA Raw Value Verification Workbook

Dataset: `UGA_2018_UNPS_v02_M` - Uganda 2018-2019

Official get-microdata URL: https://microdata.worldbank.org/catalog/3795/get-microdata

Target folder: `temp/raw_downloads/UGA_2018_UNPS_v02_M/`

Current status: blocked until the complete original raw package and
documentation are present and readable.

## Requirement Checklist

| requirement | requirement_role | candidate_variable_rows | candidate_file_rows | current_verification_status |
|---|---|---|---|---|
| household_person_keys | merge_key_gate | 12 | 11 | blocked_no_original_package |
| weights_and_design | survey_design_gate | 12 | 7 | blocked_no_original_package |
| consumption_or_income | financial_denominator_gate | 12 | 4 | blocked_no_original_package |
| oop_health_expenditure | financial_outcome_gate | 2 | 1 | blocked_no_original_package |
| health_need_and_access | access_outcome_gate | 12 | 6 | blocked_no_original_package |
| survey_timing | climate_timing_gate | 12 | 4 | blocked_no_original_package |
| climate_geography | climate_geography_gate | 12 | 4 | blocked_no_original_package |
| missing_codes_units_recall_skip_patterns | documentation_semantics_gate | 0 | 0 | blocked_no_original_package |

## File Review Preview

| requirement | file_name | candidate_variable_rows | top_variable_names | current_file_verification_status |
|---|---|---|---|---|
| climate_geography | pov2018_19 | 4 | qurban;regurb;urban;district | blocked_no_original_package |
| climate_geography | GSEC1 | 4 | urban;district_code;s1aq07;regurb | blocked_no_original_package |
| climate_geography | WSEC1A | 2 | urban;regurb | blocked_no_original_package |
| climate_geography | AGSEC1 | 2 | region;urban | blocked_no_original_package |
| consumption_or_income | pov2018_19 | 7 | cpexp30;fcpexp30;nrrexp30;fnrfxp30;hpline;ctpline;spline | blocked_no_original_package |
| consumption_or_income | GSEC15B | 3 | CEB03;CEB04;CEB07 | blocked_no_original_package |
| consumption_or_income | GSEC15E | 1 | CEE02_1 | blocked_no_original_package |
| consumption_or_income | GSEC7_2 | 1 | IncomeSource | blocked_no_original_package |
| health_need_and_access | CSEC4B | 4 | s4bq23;s4bq26;s4bq27;s4bq28 | blocked_no_original_package |
| health_need_and_access | CSEC2B | 2 | s2bq09;s2bq10 | blocked_no_original_package |
| health_need_and_access | CSEC4C | 2 | healthservice_id;s4cq46 | blocked_no_original_package |
| health_need_and_access | CSEC4D | 2 | s4eq61;s4eq61_v2 | blocked_no_original_package |

## Workbook Files

- `temp/priority_lsms_isa_raw_value_requirement_workbook.csv`
- `temp/priority_lsms_isa_raw_value_variable_workbook.csv`
- `temp/priority_lsms_isa_raw_value_file_workbook.csv`

## Stop Rule

Do not mark this wave as value-verified or analysis-ready until the workbook
evidence fields are filled from original raw files and all required gates pass.
