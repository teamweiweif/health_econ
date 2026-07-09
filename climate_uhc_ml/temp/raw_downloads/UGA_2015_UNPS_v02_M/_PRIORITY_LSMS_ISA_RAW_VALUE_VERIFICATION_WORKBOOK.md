# Priority LSMS-ISA Raw Value Verification Workbook

Dataset: `UGA_2015_UNPS_v02_M` - Uganda 2015-2016

Official get-microdata URL: https://microdata.worldbank.org/catalog/3460/get-microdata

Target folder: `temp/raw_downloads/UGA_2015_UNPS_v02_M/`

Current status: blocked until the complete original raw package and
documentation are present and readable.

## Requirement Checklist

| requirement | requirement_role | candidate_variable_rows | candidate_file_rows | current_verification_status |
|---|---|---|---|---|
| household_person_keys | merge_key_gate | 12 | 12 | blocked_no_original_package |
| weights_and_design | survey_design_gate | 12 | 4 | blocked_no_original_package |
| consumption_or_income | financial_denominator_gate | 12 | 3 | blocked_no_original_package |
| oop_health_expenditure | financial_outcome_gate | 3 | 2 | blocked_no_original_package |
| health_need_and_access | access_outcome_gate | 12 | 5 | blocked_no_original_package |
| survey_timing | climate_timing_gate | 12 | 9 | blocked_no_original_package |
| climate_geography | climate_geography_gate | 12 | 4 | blocked_no_original_package |
| missing_codes_units_recall_skip_patterns | documentation_semantics_gate | 0 | 0 | blocked_no_original_package |

## File Review Preview

| requirement | file_name | candidate_variable_rows | top_variable_names | current_file_verification_status |
|---|---|---|---|---|
| climate_geography | AGSEC2B | 3 | GPS_Manual;GPS_Not_Captured;Visit_GPS_Parcel | blocked_no_original_package |
| climate_geography | gsec1 | 4 | urban;ea;sregion;h1aq5 | blocked_no_original_package |
| climate_geography | AGSEC1 | 3 | urban;sregion;h1aq5 | blocked_no_original_package |
| climate_geography | pov2015_16 | 2 | regurb;urban | blocked_no_original_package |
| consumption_or_income | pov2015_16 | 10 | cpexp30;nrrexp30;hpline;ctpline;spline;district;equiv;hh;hsize;plinen | blocked_no_original_package |
| consumption_or_income | AGSEC1 | 1 | interview | blocked_no_original_package |
| consumption_or_income | gsec1 | 1 | interview | blocked_no_original_package |
| health_need_and_access | gsec5 | 4 | h5q4;h5q5;h5q8;h5q9 | blocked_no_original_package |
| health_need_and_access | CSEC4B_1 | 3 | C4BQ23;C4BQ19;C4BQ20 | blocked_no_original_package |
| health_need_and_access | CSEC2B_1 | 2 | C2BQ10;C2BQ9 | blocked_no_original_package |
| health_need_and_access | CSEC4A_1 | 2 | C4AQ8;C4Q7 | blocked_no_original_package |
| health_need_and_access | CSEC4M | 1 | End_sup_health | blocked_no_original_package |

## Workbook Files

- `temp/priority_lsms_isa_raw_value_requirement_workbook.csv`
- `temp/priority_lsms_isa_raw_value_variable_workbook.csv`
- `temp/priority_lsms_isa_raw_value_file_workbook.csv`

## Stop Rule

Do not mark this wave as value-verified or analysis-ready until the workbook
evidence fields are filled from original raw files and all required gates pass.
