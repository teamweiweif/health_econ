# Priority LSMS-ISA Raw Value Verification Workbook

Dataset: `NGA_2015_GHSP-W3_v02_M` - Nigeria 2015-2016

Official get-microdata URL: https://microdata.worldbank.org/catalog/2734/get-microdata

Target folder: `temp/raw_downloads/NGA_2015_GHSP-W3_v02_M/`

Current status: blocked until the complete original raw package and
documentation are present and readable.

## Requirement Checklist

| requirement | requirement_role | candidate_variable_rows | candidate_file_rows | current_verification_status |
|---|---|---|---|---|
| household_person_keys | merge_key_gate | 12 | 12 | blocked_no_original_package |
| weights_and_design | survey_design_gate | 12 | 5 | blocked_no_original_package |
| consumption_or_income | financial_denominator_gate | 12 | 3 | blocked_no_original_package |
| oop_health_expenditure | financial_outcome_gate | 6 | 1 | blocked_no_original_package |
| health_need_and_access | access_outcome_gate | 12 | 2 | blocked_no_original_package |
| survey_timing | climate_timing_gate | 12 | 1 | blocked_no_original_package |
| climate_geography | climate_geography_gate | 12 | 6 | blocked_no_original_package |
| missing_codes_units_recall_skip_patterns | documentation_semantics_gate | 0 | 0 | blocked_no_original_package |

## File Review Preview

| requirement | file_name | candidate_variable_rows | top_variable_names | current_file_verification_status |
|---|---|---|---|---|
| climate_geography | sect1_harvestw3 | 4 | s1q31a;s1q31b;s1q31c;s1q31d | blocked_no_original_package |
| climate_geography | NGA_HouseholdGeovars_Y3 | 2 | LAT_DD_MOD;LON_DD_MOD | blocked_no_original_package |
| climate_geography | sectc1_harvestw3 | 2 | ea;lga | blocked_no_original_package |
| climate_geography | sectc2_harvestw3 | 2 | ea;lga | blocked_no_original_package |
| climate_geography | cons_agg_wave3_visit1 | 1 | ea | blocked_no_original_package |
| climate_geography | cons_agg_wave3_visit2 | 1 | ea | blocked_no_original_package |
| consumption_or_income | cons_agg_wave3_visit1 | 5 | totcons;nfdfoth;fdfishpr;fdothpr;fdrestby | blocked_no_original_package |
| consumption_or_income | cons_agg_wave3_visit2 | 5 | totcons;nfdfoth;fdfishpr;fdothpr;fdrestby | blocked_no_original_package |
| consumption_or_income | sect8a_plantingw3 | 2 | ea;hhid | blocked_no_original_package |
| health_need_and_access | sect4a_harvestw3 | 11 | s4aq15;s4aq16;s4aq17;s4aq1;s4aq6a;s4aq6a_os;s4aq6b;s4aq6b_os;s4aq3;s4aq3b;s4aq3b_os | blocked_no_original_package |
| health_need_and_access | sect3_plantingw3 | 1 | s3q9b | blocked_no_original_package |
| household_person_keys | sect11a_plantingw3 | 1 | hhid | blocked_no_original_package |

## Workbook Files

- `temp/priority_lsms_isa_raw_value_requirement_workbook.csv`
- `temp/priority_lsms_isa_raw_value_variable_workbook.csv`
- `temp/priority_lsms_isa_raw_value_file_workbook.csv`

## Stop Rule

Do not mark this wave as value-verified or analysis-ready until the workbook
evidence fields are filled from original raw files and all required gates pass.
