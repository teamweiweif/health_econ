# Priority LSMS-ISA Raw Value Verification Workbook

Dataset: `KGZ_1993_KMPS_v01_M` - Kyrgyz Republic 1993

Official get-microdata URL: https://microdata.worldbank.org/catalog/280/get-microdata

Target folder: `temp/raw_downloads/KGZ_1993_KMPS_v01_M/`

Current status: blocked until the complete original raw package and
documentation are present and readable.

## Requirement Checklist

| requirement | requirement_role | candidate_variable_rows | candidate_file_rows | current_verification_status |
|---|---|---|---|---|
| household_person_keys | merge_key_gate | 12 | 7 | blocked_no_original_package |
| weights_and_design | survey_design_gate | 12 | 2 | blocked_no_original_package |
| consumption_or_income | financial_denominator_gate | 12 | 3 | blocked_no_original_package |
| oop_health_expenditure | financial_outcome_gate | 12 | 4 | blocked_no_original_package |
| health_need_and_access | access_outcome_gate | 12 | 4 | blocked_no_original_package |
| survey_timing | climate_timing_gate | 12 | 6 | blocked_no_original_package |
| climate_geography | climate_geography_gate | 12 | 5 | blocked_no_original_package |
| missing_codes_units_recall_skip_patterns | documentation_semantics_gate | 0 | 0 | blocked_no_original_package |

## File Review Preview

| requirement | file_name | candidate_variable_rows | top_variable_names | current_file_verification_status |
|---|---|---|---|---|
| climate_geography | KPRICE2 | 5 | aye1_12a;aye1_12b;aye1_12c;aye1_12d;aye1_12e | blocked_no_original_package |
| climate_geography | KHHLD | 4 | ae2_1a;ae2_1b;ae3_1a;ae3_1b | blocked_no_original_package |
| climate_geography | KPRICE3 | 1 | ayeaid | blocked_no_original_package |
| climate_geography | CORE | 1 | region | blocked_no_original_package |
| climate_geography | CONADULT | 1 | hhead | blocked_no_original_package |
| consumption_or_income | INCEXP | 9 | khomcx;khomcy;kfoodx;khousex;kotherx;kothery;kothousx;kselfemy;ktothhy | blocked_no_original_package |
| consumption_or_income | KHHLD | 2 | ad141_1d;ad141_2d | blocked_no_original_package |
| consumption_or_income | KADULT | 1 | a1o16 | blocked_no_original_package |
| health_need_and_access | KYGPOV | 8 | hcsblne;lcsblne;poor3e;poor4e;rhcsblne;rlcsblne;rpoor3e;rpoor4e | blocked_no_original_package |
| health_need_and_access | KADULT | 2 | a1l16;a1j98 | blocked_no_original_package |
| health_need_and_access | INCEXP | 1 | khealthx | blocked_no_original_package |
| health_need_and_access | KCHILD | 1 | a1l16 | blocked_no_original_package |

## Workbook Files

- `temp/priority_lsms_isa_raw_value_requirement_workbook.csv`
- `temp/priority_lsms_isa_raw_value_variable_workbook.csv`
- `temp/priority_lsms_isa_raw_value_file_workbook.csv`

## Stop Rule

Do not mark this wave as value-verified or analysis-ready until the workbook
evidence fields are filled from original raw files and all required gates pass.
