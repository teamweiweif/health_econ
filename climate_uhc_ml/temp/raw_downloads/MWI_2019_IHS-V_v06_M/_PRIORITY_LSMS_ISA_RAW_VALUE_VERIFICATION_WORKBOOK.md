# Priority LSMS-ISA Raw Value Verification Workbook

Dataset: `MWI_2019_IHS-V_v06_M` - Malawi 2019-2020

Official get-microdata URL: https://microdata.worldbank.org/catalog/3818/get-microdata

Target folder: `temp/raw_downloads/MWI_2019_IHS-V_v06_M/`

Current status: blocked until the complete original raw package and
documentation are present and readable.

## Requirement Checklist

| requirement | requirement_role | candidate_variable_rows | candidate_file_rows | current_verification_status |
|---|---|---|---|---|
| household_person_keys | merge_key_gate | 12 | 12 | blocked_no_original_package |
| weights_and_design | survey_design_gate | 12 | 11 | blocked_no_original_package |
| consumption_or_income | financial_denominator_gate | 12 | 6 | blocked_no_original_package |
| oop_health_expenditure | financial_outcome_gate | 12 | 1 | blocked_no_original_package |
| health_need_and_access | access_outcome_gate | 12 | 2 | blocked_no_original_package |
| survey_timing | climate_timing_gate | 12 | 3 | blocked_no_original_package |
| climate_geography | climate_geography_gate | 12 | 7 | blocked_no_original_package |
| missing_codes_units_recall_skip_patterns | documentation_semantics_gate | 0 | 0 | blocked_no_original_package |

## File Review Preview

| requirement | file_name | candidate_variable_rows | top_variable_names | current_file_verification_status |
|---|---|---|---|---|
| climate_geography | householdgeovariables_ihs5.dta | 3 | ea_id;ea_lat_mod;ea_lon_mod | blocked_no_original_package |
| climate_geography | ihs5_consumption_aggregate.dta | 2 | area;ea_id | blocked_no_original_package |
| climate_geography | ag_mod_j.dta | 2 | ag_j06e;ag_j06e_oth | blocked_no_original_package |
| climate_geography | ag_mod_o2.dta | 2 | ag_o05e;ag_o05e_oth | blocked_no_original_package |
| climate_geography | hh_mod_a_filt.dta | 1 | ea_id | blocked_no_original_package |
| climate_geography | ag_mod_c.dta | 1 | ag_c05e_oth | blocked_no_original_package |
| climate_geography | HH_MOD_F1.dta | 1 | hh_f102e | blocked_no_original_package |
| consumption_or_income | HH_MOD_I1.dta | 5 | case_id;hh_i01;hh_i02;hh_i03;HHID | blocked_no_original_package |
| consumption_or_income | HH_MOD_G1.dta | 2 | hh_g00_2;hh_g00_1 | blocked_no_original_package |
| consumption_or_income | HH_MOD_I2.dta | 2 | case_id;hh_i04 | blocked_no_original_package |
| consumption_or_income | HH_MOD_K1.dta | 1 | hh_k03 | blocked_no_original_package |
| consumption_or_income | HH_MOD_K2.dta | 1 | hh_k03 | blocked_no_original_package |

## Workbook Files

- `temp/priority_lsms_isa_raw_value_requirement_workbook.csv`
- `temp/priority_lsms_isa_raw_value_variable_workbook.csv`
- `temp/priority_lsms_isa_raw_value_file_workbook.csv`

## Stop Rule

Do not mark this wave as value-verified or analysis-ready until the workbook
evidence fields are filled from original raw files and all required gates pass.
