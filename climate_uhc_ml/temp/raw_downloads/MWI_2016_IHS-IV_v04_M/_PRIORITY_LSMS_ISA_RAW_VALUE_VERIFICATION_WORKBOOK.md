# Priority LSMS-ISA Raw Value Verification Workbook

Dataset: `MWI_2016_IHS-IV_v04_M` - Malawi 2016-2017

Official get-microdata URL: https://microdata.worldbank.org/catalog/2936/get-microdata

Target folder: `temp/raw_downloads/MWI_2016_IHS-IV_v04_M/`

Current status: blocked until the complete original raw package and
documentation are present and readable.

## Requirement Checklist

| requirement | requirement_role | candidate_variable_rows | candidate_file_rows | current_verification_status |
|---|---|---|---|---|
| household_person_keys | merge_key_gate | 12 | 12 | blocked_no_original_package |
| weights_and_design | survey_design_gate | 12 | 12 | blocked_no_original_package |
| consumption_or_income | financial_denominator_gate | 12 | 5 | blocked_no_original_package |
| oop_health_expenditure | financial_outcome_gate | 10 | 1 | blocked_no_original_package |
| health_need_and_access | access_outcome_gate | 12 | 3 | blocked_no_original_package |
| survey_timing | climate_timing_gate | 12 | 3 | blocked_no_original_package |
| climate_geography | climate_geography_gate | 12 | 7 | blocked_no_original_package |
| missing_codes_units_recall_skip_patterns | documentation_semantics_gate | 0 | 0 | blocked_no_original_package |

## File Review Preview

| requirement | file_name | candidate_variable_rows | top_variable_names | current_file_verification_status |
|---|---|---|---|---|
| climate_geography | IHS4 Consumption Aggregate | 2 | ea_id;area | blocked_no_original_package |
| climate_geography | AG_MOD_J | 2 | ag_j06e;ag_j06e_oth | blocked_no_original_package |
| climate_geography | AG_MOD_B1 | 2 | ag_b105e;ag_b105e_oth | blocked_no_original_package |
| climate_geography | AG_MOD_I1 | 2 | ag_i106c;ag_i106c_oth | blocked_no_original_package |
| climate_geography | AG_MOD_O1 | 2 | ag_o105e;ag_o105e_oth | blocked_no_original_package |
| climate_geography | HH_MOD_A_FILT | 1 | ea_id | blocked_no_original_package |
| climate_geography | AG_MOD_C | 1 | ag_c05e | blocked_no_original_package |
| consumption_or_income | HH_MOD_I1 | 5 | case_id;hh_i01;hh_i02;hh_i03;HHID | blocked_no_original_package |
| consumption_or_income | HH_MOD_I2 | 3 | case_id;hh_i04;hh_i05 | blocked_no_original_package |
| consumption_or_income | HH_MOD_G1 | 2 | hh_g00_2;hh_g00_1 | blocked_no_original_package |
| consumption_or_income | HH_MOD_K1 | 1 | hh_k03 | blocked_no_original_package |
| consumption_or_income | HH_MOD_K2 | 1 | hh_k03 | blocked_no_original_package |

## Workbook Files

- `temp/priority_lsms_isa_raw_value_requirement_workbook.csv`
- `temp/priority_lsms_isa_raw_value_variable_workbook.csv`
- `temp/priority_lsms_isa_raw_value_file_workbook.csv`

## Stop Rule

Do not mark this wave as value-verified or analysis-ready until the workbook
evidence fields are filled from original raw files and all required gates pass.
