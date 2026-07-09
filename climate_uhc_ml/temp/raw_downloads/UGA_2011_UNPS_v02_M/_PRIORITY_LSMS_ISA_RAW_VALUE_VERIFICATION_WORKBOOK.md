# Priority LSMS-ISA Raw Value Verification Workbook

Dataset: `UGA_2011_UNPS_v02_M` - Uganda 2011-2012

Official get-microdata URL: https://microdata.worldbank.org/catalog/2059/get-microdata

Target folder: `temp/raw_downloads/UGA_2011_UNPS_v02_M/`

Current status: blocked until the complete original raw package and
documentation are present and readable.

## Requirement Checklist

| requirement | requirement_role | candidate_variable_rows | candidate_file_rows | current_verification_status |
|---|---|---|---|---|
| household_person_keys | merge_key_gate | 12 | 11 | blocked_no_original_package |
| weights_and_design | survey_design_gate | 12 | 4 | blocked_no_original_package |
| consumption_or_income | financial_denominator_gate | 12 | 4 | blocked_no_original_package |
| oop_health_expenditure | financial_outcome_gate | 5 | 3 | blocked_no_original_package |
| health_need_and_access | access_outcome_gate | 12 | 9 | blocked_no_original_package |
| survey_timing | climate_timing_gate | 12 | 4 | blocked_no_original_package |
| climate_geography | climate_geography_gate | 12 | 1 | blocked_no_original_package |
| missing_codes_units_recall_skip_patterns | documentation_semantics_gate | 0 | 0 | blocked_no_original_package |

## File Review Preview

| requirement | file_name | candidate_variable_rows | top_variable_names | current_file_verification_status |
|---|---|---|---|---|
| climate_geography | CSEC1.NSDstat | 12 | GPS_Manual_Health;cgpsdlg2;cgpsdlg3;cgpsdlg4;cgpsdlg5;cgpsdlt2;cgpsdlt3;cgpsdlt4;cgpsdlt5;cgpsmlg2_min;cgpsmlg2_sec;c... | blocked_no_original_package |
| consumption_or_income | GSEC15B.NSDstat | 8 | h15bq14;h15bq15;h15bq2d;h15bq3a;h15bq3b;h15bq4;h15bq5;itmcd | blocked_no_original_package |
| consumption_or_income | UNPS 2011-12 Consumption Aggregate.NSDstat | 2 | welfare;cpexp30 | blocked_no_original_package |
| consumption_or_income | GSEC15BB.NSDstat | 1 | h15bq14 | blocked_no_original_package |
| consumption_or_income | GSEC15C.NSDstat | 1 | h15cq2 | blocked_no_original_package |
| health_need_and_access | CSEC4l.NSDstat | 2 | c4lq102;c4lq102_other | blocked_no_original_package |
| health_need_and_access | CSEC2b.NSDstat | 2 | c2bq10;c2bq9 | blocked_no_original_package |
| health_need_and_access | CSEC4c.NSDstat | 2 | c4cq46;c4cq48 | blocked_no_original_package |
| health_need_and_access | CSEC4n.NSDstat | 1 | End_sup_health | blocked_no_original_package |
| health_need_and_access | CSEC4ab.NSDstat | 1 | c4bq23 | blocked_no_original_package |
| health_need_and_access | CSEC4d.NSDstat | 1 | End_Diseases | blocked_no_original_package |
| health_need_and_access | CSEC4e.NSDstat | 1 | c4e61 | blocked_no_original_package |

## Workbook Files

- `temp/priority_lsms_isa_raw_value_requirement_workbook.csv`
- `temp/priority_lsms_isa_raw_value_variable_workbook.csv`
- `temp/priority_lsms_isa_raw_value_file_workbook.csv`

## Stop Rule

Do not mark this wave as value-verified or analysis-ready until the workbook
evidence fields are filled from original raw files and all required gates pass.
