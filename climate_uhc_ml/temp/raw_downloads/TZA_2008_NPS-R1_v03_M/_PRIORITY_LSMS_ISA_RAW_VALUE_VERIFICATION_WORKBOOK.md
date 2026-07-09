# Priority LSMS-ISA Raw Value Verification Workbook

Dataset: `TZA_2008_NPS-R1_v03_M` - Tanzania 2008-2009

Official get-microdata URL: https://microdata.worldbank.org/catalog/76/get-microdata

Target folder: `temp/raw_downloads/TZA_2008_NPS-R1_v03_M/`

Current status: blocked until the complete original raw package and
documentation are present and readable.

## Requirement Checklist

| requirement | requirement_role | candidate_variable_rows | candidate_file_rows | current_verification_status |
|---|---|---|---|---|
| household_person_keys | merge_key_gate | 12 | 11 | blocked_no_original_package |
| weights_and_design | survey_design_gate | 12 | 7 | blocked_no_original_package |
| consumption_or_income | financial_denominator_gate | 12 | 3 | blocked_no_original_package |
| oop_health_expenditure | financial_outcome_gate | 12 | 2 | blocked_no_original_package |
| health_need_and_access | access_outcome_gate | 12 | 2 | blocked_no_original_package |
| survey_timing | climate_timing_gate | 12 | 5 | blocked_no_original_package |
| climate_geography | climate_geography_gate | 12 | 9 | blocked_no_original_package |
| missing_codes_units_recall_skip_patterns | documentation_semantics_gate | 0 | 0 | blocked_no_original_package |

## File Review Preview

| requirement | file_name | candidate_variable_rows | top_variable_names | current_file_verification_status |
|---|---|---|---|---|
| climate_geography | HH.Geovariables_Y1 | 3 | ea_id;lat_modified;lon_modified | blocked_no_original_package |
| climate_geography | SEC_A_T_English_Labels | 2 | clusterid;ea | blocked_no_original_package |
| climate_geography | SEC_A_T_Swahili_Labels | 1 | ea | blocked_no_original_package |
| climate_geography | SECTA1A2_Swahili_Labels | 1 | ea_id | blocked_no_original_package |
| climate_geography | SECTCB_Swahili_Labels | 1 | ea_id | blocked_no_original_package |
| climate_geography | SECTCEFG | 1 | ea_id | blocked_no_original_package |
| climate_geography | SECTCH | 1 | ea_id | blocked_no_original_package |
| climate_geography | SECTCI | 1 | ea_id | blocked_no_original_package |
| consumption_or_income | TZY1.HH.Consumption | 4 | hhexpenses;hhexpensesR;expm;expmR | blocked_no_original_package |
| consumption_or_income | SEC_L_Swahili_Labels | 4 | hhid;slcode;slq1;slq2 | blocked_no_original_package |
| consumption_or_income | SEC_M_Swahili_Labels | 4 | hhid;smcode;smq1;smq2 | blocked_no_original_package |
| health_need_and_access | SEC_B_C_D_E1_F_G1_U_English_Labels | 11 | sdq22;sdq4;sdq43_1;sdq43_2;sdq43_3;sdq55_1;sdq55_2;sdq55_3;sdq6;sdq8;sdq9 | blocked_no_original_package |

## Workbook Files

- `temp/priority_lsms_isa_raw_value_requirement_workbook.csv`
- `temp/priority_lsms_isa_raw_value_variable_workbook.csv`
- `temp/priority_lsms_isa_raw_value_file_workbook.csv`

## Stop Rule

Do not mark this wave as value-verified or analysis-ready until the workbook
evidence fields are filled from original raw files and all required gates pass.
