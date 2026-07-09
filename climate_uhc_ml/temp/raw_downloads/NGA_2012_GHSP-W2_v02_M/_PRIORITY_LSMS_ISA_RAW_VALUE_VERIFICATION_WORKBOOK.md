# Priority LSMS-ISA Raw Value Verification Workbook

Dataset: `NGA_2012_GHSP-W2_v02_M` - Nigeria 2012-2013

Official get-microdata URL: https://microdata.worldbank.org/catalog/1952/get-microdata

Target folder: `temp/raw_downloads/NGA_2012_GHSP-W2_v02_M/`

Current status: blocked until the complete original raw package and
documentation are present and readable.

## Requirement Checklist

| requirement | requirement_role | candidate_variable_rows | candidate_file_rows | current_verification_status |
|---|---|---|---|---|
| household_person_keys | merge_key_gate | 12 | 12 | blocked_no_original_package |
| weights_and_design | survey_design_gate | 12 | 4 | blocked_no_original_package |
| consumption_or_income | financial_denominator_gate | 12 | 4 | blocked_no_original_package |
| oop_health_expenditure | financial_outcome_gate | 6 | 1 | blocked_no_original_package |
| health_need_and_access | access_outcome_gate | 12 | 3 | blocked_no_original_package |
| survey_timing | climate_timing_gate | 12 | 1 | blocked_no_original_package |
| climate_geography | climate_geography_gate | 12 | 5 | blocked_no_original_package |
| missing_codes_units_recall_skip_patterns | documentation_semantics_gate | 0 | 0 | blocked_no_original_package |

## File Review Preview

| requirement | file_name | candidate_variable_rows | top_variable_names | current_file_verification_status |
|---|---|---|---|---|
| climate_geography | HHTrack | 4 | ea;lga;state;zone | blocked_no_original_package |
| climate_geography | secta_harvestw2 | 4 | ea;lga;state;zone | blocked_no_original_package |
| climate_geography | NGA_HouseholdGeovars_Y2 | 2 | LAT_DD_MOD;LON_DD_MOD | blocked_no_original_package |
| climate_geography | cons_agg_wave2_visit1 | 1 | ea | blocked_no_original_package |
| climate_geography | cons_agg_wave2_visit2 | 1 | ea | blocked_no_original_package |
| consumption_or_income | cons_agg_wave2_visit1 | 5 | totcons;nfdfoth;fdfishpr;fdothpr;fdrestby | blocked_no_original_package |
| consumption_or_income | cons_agg_wave2_visit2 | 5 | totcons;nfdfoth;fdfishpr;fdothpr;fdrestby | blocked_no_original_package |
| consumption_or_income | sect8e_plantingw2 | 1 | s8q10 | blocked_no_original_package |
| consumption_or_income | sect8a_plantingw2 | 1 | ea | blocked_no_original_package |
| health_need_and_access | sect4a_harvestw2 | 9 | s4aq15;s4aq16;s4aq17;s4aq1;s4aq3;s4aq20;s4aq6a;s4aq6b;s4aq6c | blocked_no_original_package |
| health_need_and_access | secta7_harvestw2 | 2 | cost_cd;cost_desc | blocked_no_original_package |
| health_need_and_access | sect4b_harvestw2 | 1 | s4bq3 | blocked_no_original_package |

## Workbook Files

- `temp/priority_lsms_isa_raw_value_requirement_workbook.csv`
- `temp/priority_lsms_isa_raw_value_variable_workbook.csv`
- `temp/priority_lsms_isa_raw_value_file_workbook.csv`

## Stop Rule

Do not mark this wave as value-verified or analysis-ready until the workbook
evidence fields are filled from original raw files and all required gates pass.
