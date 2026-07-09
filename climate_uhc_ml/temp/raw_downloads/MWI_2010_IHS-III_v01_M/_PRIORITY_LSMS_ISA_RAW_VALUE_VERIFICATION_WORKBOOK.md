# Priority LSMS-ISA Raw Value Verification Workbook

Dataset: `MWI_2010_IHS-III_v01_M` - Malawi 2010-2011

Official get-microdata URL: https://microdata.worldbank.org/catalog/1003/get-microdata

Target folder: `temp/raw_downloads/MWI_2010_IHS-III_v01_M/`

Current status: blocked until the complete original raw package and
documentation are present and readable.

## Requirement Checklist

| requirement | requirement_role | candidate_variable_rows | candidate_file_rows | current_verification_status |
|---|---|---|---|---|
| household_person_keys | merge_key_gate | 12 | 12 | blocked_no_original_package |
| weights_and_design | survey_design_gate | 12 | 11 | blocked_no_original_package |
| consumption_or_income | financial_denominator_gate | 12 | 3 | blocked_no_original_package |
| oop_health_expenditure | financial_outcome_gate | 5 | 1 | blocked_no_original_package |
| health_need_and_access | access_outcome_gate | 12 | 2 | blocked_no_original_package |
| survey_timing | climate_timing_gate | 12 | 6 | blocked_no_original_package |
| climate_geography | climate_geography_gate | 12 | 10 | blocked_no_original_package |
| missing_codes_units_recall_skip_patterns | documentation_semantics_gate | 0 | 0 | blocked_no_original_package |

## File Review Preview

| requirement | file_name | candidate_variable_rows | top_variable_names | current_file_verification_status |
|---|---|---|---|---|
| climate_geography | HouseholdGeovariables.NSDstat | 3 | ea_id;lat_modified;lon_modified | blocked_no_original_package |
| climate_geography | PlotGeovariables.NSDstat | 1 | ea_id | blocked_no_original_package |
| climate_geography | HH_MOD_A_FILT.NSDstat | 1 | ea_id | blocked_no_original_package |
| climate_geography | HH_MOD_H.NSDstat | 1 | ea_id | blocked_no_original_package |
| climate_geography | HH_MOD_I1.NSDstat | 1 | ea_id | blocked_no_original_package |
| climate_geography | HH_MOD_I2.NSDstat | 1 | ea_id | blocked_no_original_package |
| climate_geography | HH_MOD_J.NSDstat | 1 | ea_id | blocked_no_original_package |
| climate_geography | HH_MOD_K.NSDstat | 1 | ea_id | blocked_no_original_package |
| consumption_or_income | Round 1 (2010) Consumption Aggregate.NSDstat | 7 | rexp_cat01;rexp_cat011;epoor;pcrexpagg;poor;rexp_cat012;rexp_cat02 | blocked_no_original_package |
| consumption_or_income | ihs3fc2M_consumption.NSDstat | 4 | exp_cat01;exp_cat011;rexp_cat01;rexp_cat011 | blocked_no_original_package |
| consumption_or_income | HH_MOD_T.NSDstat | 1 | hh_t01 | blocked_no_original_package |
| health_need_and_access | COM_CD.NSDstat | 6 | com_cd60a;com_cd60b;com_cd53;com_cd54;com_cd51a;com_cd51b | blocked_no_original_package |

## Workbook Files

- `temp/priority_lsms_isa_raw_value_requirement_workbook.csv`
- `temp/priority_lsms_isa_raw_value_variable_workbook.csv`
- `temp/priority_lsms_isa_raw_value_file_workbook.csv`

## Stop Rule

Do not mark this wave as value-verified or analysis-ready until the workbook
evidence fields are filled from original raw files and all required gates pass.
