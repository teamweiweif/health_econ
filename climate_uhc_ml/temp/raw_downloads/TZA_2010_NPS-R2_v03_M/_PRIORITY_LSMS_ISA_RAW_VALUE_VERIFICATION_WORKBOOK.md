# Priority LSMS-ISA Raw Value Verification Workbook

Dataset: `TZA_2010_NPS-R2_v03_M` - Tanzania 2010-2011

Official get-microdata URL: https://microdata.worldbank.org/catalog/1050/get-microdata

Target folder: `temp/raw_downloads/TZA_2010_NPS-R2_v03_M/`

Current status: blocked until the complete original raw package and
documentation are present and readable.

## Requirement Checklist

| requirement | requirement_role | candidate_variable_rows | candidate_file_rows | current_verification_status |
|---|---|---|---|---|
| household_person_keys | merge_key_gate | 12 | 11 | blocked_no_original_package |
| weights_and_design | survey_design_gate | 12 | 11 | blocked_no_original_package |
| consumption_or_income | financial_denominator_gate | 12 | 3 | blocked_no_original_package |
| oop_health_expenditure | financial_outcome_gate | 8 | 1 | blocked_no_original_package |
| health_need_and_access | access_outcome_gate | 12 | 6 | blocked_no_original_package |
| survey_timing | climate_timing_gate | 12 | 6 | blocked_no_original_package |
| climate_geography | climate_geography_gate | 12 | 6 | blocked_no_original_package |
| missing_codes_units_recall_skip_patterns | documentation_semantics_gate | 0 | 0 | blocked_no_original_package |

## File Review Preview

| requirement | file_name | candidate_variable_rows | top_variable_names | current_file_verification_status |
|---|---|---|---|---|
| climate_geography | HH_SEC_A | 6 | clusterid;district;ea;hh_a18_year;region;ward | blocked_no_original_package |
| climate_geography | TZY2.EA.Offsets | 2 | clusterid;rum | blocked_no_original_package |
| climate_geography | Plot.Geovariables_Y2 | 1 | ea_id | blocked_no_original_package |
| climate_geography | TZY1.HH.Consumption | 1 | urban | blocked_no_original_package |
| climate_geography | TZY2.HH.Consumption | 1 | urban | blocked_no_original_package |
| climate_geography | HH.Geovariables_Y2 | 1 | ea_id | blocked_no_original_package |
| consumption_or_income | TZY1.HH.Consumption | 4 | hhexpenses;hhexpensesR;expm;expmR | blocked_no_original_package |
| consumption_or_income | TZY2.HH.Consumption | 4 | hhexpenses;hhexpensesR;expm;expmR | blocked_no_original_package |
| consumption_or_income | HH_SEC_L | 4 | hh_l01_2;hh_l02;itemcode;y2_hhid | blocked_no_original_package |
| health_need_and_access | HH_SEC_D | 5 | hh_d12_1;hh_d12_2;hh_d02;hh_d13;hh_d38 | blocked_no_original_package |
| health_need_and_access | FS_H2 | 2 | costid;costitem | blocked_no_original_package |
| health_need_and_access | TZY1.HH.Consumption | 2 | health;healthR | blocked_no_original_package |

## Workbook Files

- `temp/priority_lsms_isa_raw_value_requirement_workbook.csv`
- `temp/priority_lsms_isa_raw_value_variable_workbook.csv`
- `temp/priority_lsms_isa_raw_value_file_workbook.csv`

## Stop Rule

Do not mark this wave as value-verified or analysis-ready until the workbook
evidence fields are filled from original raw files and all required gates pass.
