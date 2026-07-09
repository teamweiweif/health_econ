# Priority LSMS-ISA Raw Value Verification Workbook

Dataset: `NGA_2010_GHSP-W1_v03_M` - Nigeria 2010-2011

Official get-microdata URL: https://microdata.worldbank.org/catalog/1002/get-microdata

Target folder: `temp/raw_downloads/NGA_2010_GHSP-W1_v03_M/`

Current status: blocked until the complete original raw package and
documentation are present and readable.

## Requirement Checklist

| requirement | requirement_role | candidate_variable_rows | candidate_file_rows | current_verification_status |
|---|---|---|---|---|
| household_person_keys | merge_key_gate | 12 | 12 | blocked_no_original_package |
| weights_and_design | survey_design_gate | 12 | 8 | blocked_no_original_package |
| consumption_or_income | financial_denominator_gate | 12 | 2 | blocked_no_original_package |
| oop_health_expenditure | financial_outcome_gate | 5 | 1 | blocked_no_original_package |
| health_need_and_access | access_outcome_gate | 12 | 3 | blocked_no_original_package |
| survey_timing | climate_timing_gate | 12 | 2 | blocked_no_original_package |
| climate_geography | climate_geography_gate | 12 | 3 | blocked_no_original_package |
| missing_codes_units_recall_skip_patterns | documentation_semantics_gate | 0 | 0 | blocked_no_original_package |

## File Review Preview

| requirement | file_name | candidate_variable_rows | top_variable_names | current_file_verification_status |
|---|---|---|---|---|
| climate_geography | NGA_HouseholdGeovariables_Y1 | 10 | lat_dd_mod;lon_dd_mod;ea;eviarea_avg;grn_avg;h2010_eviarea;h2010_grn;h2010_sen;lga;sen_avg | blocked_no_original_package |
| climate_geography | cons_agg_wave1_visit1 | 1 | ea | blocked_no_original_package |
| climate_geography | cons_agg_wave1_visit2 | 1 | ea | blocked_no_original_package |
| consumption_or_income | cons_agg_wave1_visit1 | 7 | totcons;nfdfoth;fdfishpr;fdothpr;fdrestby;fdalcpr;fdbeanpr | blocked_no_original_package |
| consumption_or_income | cons_agg_wave1_visit2 | 5 | totcons;nfdfoth;fdfishpr;fdothpr;fdrestby | blocked_no_original_package |
| health_need_and_access | sect4a_harvestw1 | 10 | s4aq15;s4aq16;s4aq17;s4aq1;s4aq3;s4aq6a;s4aq6b;s4aq6c;s4aq20;s4aq20b | blocked_no_original_package |
| health_need_and_access | sect4b_harvestw1 | 1 | s4bq3 | blocked_no_original_package |
| health_need_and_access | sect3a_harvestw1 | 1 | s3aq17 | blocked_no_original_package |
| household_person_keys | secta7_harvestw1 | 1 | hhid | blocked_no_original_package |
| household_person_keys | secta8_harvestw1 | 1 | hhid | blocked_no_original_package |
| household_person_keys | secta9a1_harvestw1 | 1 | hhid | blocked_no_original_package |
| household_person_keys | secta9a2_harvestw1 | 1 | hhid | blocked_no_original_package |

## Workbook Files

- `temp/priority_lsms_isa_raw_value_requirement_workbook.csv`
- `temp/priority_lsms_isa_raw_value_variable_workbook.csv`
- `temp/priority_lsms_isa_raw_value_file_workbook.csv`

## Stop Rule

Do not mark this wave as value-verified or analysis-ready until the workbook
evidence fields are filled from original raw files and all required gates pass.
