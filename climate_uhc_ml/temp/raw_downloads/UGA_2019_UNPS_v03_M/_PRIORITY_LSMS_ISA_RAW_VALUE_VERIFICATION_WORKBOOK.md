# Priority LSMS-ISA Raw Value Verification Workbook

Dataset: `UGA_2019_UNPS_v03_M` - Uganda 2019-2020

Official get-microdata URL: https://microdata.worldbank.org/catalog/3902/get-microdata

Target folder: `temp/raw_downloads/UGA_2019_UNPS_v03_M/`

Current status: blocked until the complete original raw package and
documentation are present and readable.

## Requirement Checklist

| requirement | requirement_role | candidate_variable_rows | candidate_file_rows | current_verification_status |
|---|---|---|---|---|
| household_person_keys | merge_key_gate | 12 | 12 | blocked_no_original_package |
| weights_and_design | survey_design_gate | 12 | 12 | blocked_no_original_package |
| consumption_or_income | financial_denominator_gate | 12 | 2 | blocked_no_original_package |
| oop_health_expenditure | financial_outcome_gate | 12 | 3 | blocked_no_original_package |
| health_need_and_access | access_outcome_gate | 12 | 4 | blocked_no_original_package |
| survey_timing | climate_timing_gate | 12 | 6 | blocked_no_original_package |
| climate_geography | climate_geography_gate | 12 | 10 | blocked_no_original_package |
| missing_codes_units_recall_skip_patterns | documentation_semantics_gate | 0 | 0 | blocked_no_original_package |

## File Review Preview

| requirement | file_name | candidate_variable_rows | top_variable_names | current_file_verification_status |
|---|---|---|---|---|
| climate_geography | pov2019_20.NSDstat | 3 | regurb;urban;district | blocked_no_original_package |
| climate_geography | GSEC1.NSDstat | 1 | urban | blocked_no_original_package |
| climate_geography | CSEC1A.NSDstat | 1 | Final_EA_code | blocked_no_original_package |
| climate_geography | CSEC2.NSDstat | 1 | Final_EA_code | blocked_no_original_package |
| climate_geography | CSEC2A.NSDstat | 1 | Final_EA_code | blocked_no_original_package |
| climate_geography | CSEC2B.NSDstat | 1 | Final_EA_code | blocked_no_original_package |
| climate_geography | CSEC2C.NSDstat | 1 | Final_EA_code | blocked_no_original_package |
| climate_geography | CSEC2C_0.NSDstat | 1 | Final_EA_code | blocked_no_original_package |
| consumption_or_income | GSEC15B.NSDstat | 9 | CEB03;CEB04;CEB07;CEB10;CEB11;CEB14a;CEB15;CEB16;coicop_2 | blocked_no_original_package |
| consumption_or_income | pov2019_20.NSDstat | 3 | cpexp30;nrrexp30;hpline | blocked_no_original_package |
| health_need_and_access | CSEC2B.NSDstat | 6 | s2bq13__1;s2bq09;s2bq10;s2bq13__2;s2bq13__3;s2bq13__4 | blocked_no_original_package |
| health_need_and_access | CSEC4B.NSDstat | 4 | s4bq23;s4bq26;s4bq27;s4bq28 | blocked_no_original_package |

## Workbook Files

- `temp/priority_lsms_isa_raw_value_requirement_workbook.csv`
- `temp/priority_lsms_isa_raw_value_variable_workbook.csv`
- `temp/priority_lsms_isa_raw_value_file_workbook.csv`

## Stop Rule

Do not mark this wave as value-verified or analysis-ready until the workbook
evidence fields are filled from original raw files and all required gates pass.
