# Priority LSMS-ISA Raw Value Verification Workbook

Dataset: `JAM_1997_SLC_v01_M` - Jamaica 1997

Official get-microdata URL: https://microdata.worldbank.org/catalog/2368/get-microdata

Target folder: `temp/raw_downloads/JAM_1997_SLC_v01_M/`

Current status: blocked until the complete original raw package and
documentation are present and readable.

## Requirement Checklist

| requirement | requirement_role | candidate_variable_rows | candidate_file_rows | current_verification_status |
|---|---|---|---|---|
| household_person_keys | merge_key_gate | 12 | 2 | blocked_no_original_package |
| weights_and_design | survey_design_gate | 12 | 10 | blocked_no_original_package |
| consumption_or_income | financial_denominator_gate | 12 | 5 | blocked_no_original_package |
| oop_health_expenditure | financial_outcome_gate | 11 | 2 | blocked_no_original_package |
| health_need_and_access | access_outcome_gate | 12 | 3 | blocked_no_original_package |
| survey_timing | climate_timing_gate | 12 | 5 | blocked_no_original_package |
| climate_geography | climate_geography_gate | 12 | 7 | blocked_no_original_package |
| missing_codes_units_recall_skip_patterns | documentation_semantics_gate | 0 | 0 | blocked_no_original_package |

## File Review Preview

| requirement | file_name | candidate_variable_rows | top_variable_names | current_file_verification_status |
|---|---|---|---|---|
| climate_geography | REC001.NSDstat | 4 | area;district;parish;region | blocked_no_original_package |
| climate_geography | HEADS.NSDstat | 2 | district;parish | blocked_no_original_package |
| climate_geography | HHSIZE.NSDstat | 2 | district;parish | blocked_no_original_package |
| climate_geography | EXP97.NSDstat | 1 | Cluster | blocked_no_original_package |
| climate_geography | REC034.NSDstat | 1 | xearn | blocked_no_original_package |
| climate_geography | REC041.NSDstat | 1 | year | blocked_no_original_package |
| climate_geography | ANNUAL.NSDstat | 1 | district | blocked_no_original_package |
| consumption_or_income | TOTGIFTS.NSDstat | 4 | t_gfood;serial;tcgift;totgift | blocked_no_original_package |
| consumption_or_income | FOOD.NSDstat | 3 | consgift;giftfood;hpfood | blocked_no_original_package |
| consumption_or_income | MEALS.NSDstat | 3 | consgift;giftfood;hpfood | blocked_no_original_package |
| consumption_or_income | ANNUAL.NSDstat | 1 | non_food | blocked_no_original_package |
| consumption_or_income | TOTFOOD.NSDstat | 1 | t_food | blocked_no_original_package |

## Workbook Files

- `temp/priority_lsms_isa_raw_value_requirement_workbook.csv`
- `temp/priority_lsms_isa_raw_value_variable_workbook.csv`
- `temp/priority_lsms_isa_raw_value_file_workbook.csv`

## Stop Rule

Do not mark this wave as value-verified or analysis-ready until the workbook
evidence fields are filled from original raw files and all required gates pass.
