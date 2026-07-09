# Priority LSMS-ISA Raw Value Verification Workbook

Dataset: `TZA_2012_NPS-R3_v01_M` - Tanzania 2012-2013

Official get-microdata URL: https://microdata.worldbank.org/catalog/2252/get-microdata

Target folder: `temp/raw_downloads/TZA_2012_NPS-R3_v01_M/`

Current status: blocked until the complete original raw package and
documentation are present and readable.

## Requirement Checklist

| requirement | requirement_role | candidate_variable_rows | candidate_file_rows | current_verification_status |
|---|---|---|---|---|
| household_person_keys | merge_key_gate | 12 | 11 | blocked_no_original_package |
| weights_and_design | survey_design_gate | 12 | 6 | blocked_no_original_package |
| consumption_or_income | financial_denominator_gate | 12 | 2 | blocked_no_original_package |
| oop_health_expenditure | financial_outcome_gate | 12 | 1 | blocked_no_original_package |
| health_need_and_access | access_outcome_gate | 12 | 6 | blocked_no_original_package |
| survey_timing | climate_timing_gate | 12 | 5 | blocked_no_original_package |
| climate_geography | climate_geography_gate | 12 | 5 | blocked_no_original_package |
| missing_codes_units_recall_skip_patterns | documentation_semantics_gate | 0 | 0 | blocked_no_original_package |

## File Review Preview

| requirement | file_name | candidate_variable_rows | top_variable_names | current_file_verification_status |
|---|---|---|---|---|
| climate_geography | COM_SEC_A1A2.NSDstat | 4 | cm_lon_g;cm_lon_m;cm_lon_s;y3_cluster | blocked_no_original_package |
| climate_geography | AG_SEC_2A.NSDstat | 2 | ag2a_06_3;ag2a_06_4 | blocked_no_original_package |
| climate_geography | AG_SEC_A.NSDstat | 2 | ag_a04_1;ag_a04_2 | blocked_no_original_package |
| climate_geography | HH_SEC_A.NSDstat | 2 | hh_a04_1;hh_a04_2 | blocked_no_original_package |
| climate_geography | LF_SEC_A.NSDstat | 2 | lf_a04_1;lf_a04_2 | blocked_no_original_package |
| consumption_or_income | HH_SEC_K.NSDstat | 6 | hh_k01;hh_k02;hh_k03;itemcode;occ;y3_hhid | blocked_no_original_package |
| consumption_or_income | HH_SEC_L.NSDstat | 6 | hh_l01;hh_l02;hh_l03;itemcode;occ;y3_hhid | blocked_no_original_package |
| health_need_and_access | HH_SEC_D.NSDstat | 5 | hh_d12_1;hh_d12_2;hh_d02;hh_d13;hh_d23 | blocked_no_original_package |
| health_need_and_access | ConsumptionNPS3.NSDstat | 2 | health;healthR | blocked_no_original_package |
| health_need_and_access | LF_SEC_13B.NSDstat | 2 | costcode;costname | blocked_no_original_package |
| health_need_and_access | HH_SEC_G.NSDstat | 1 | hh_g03_5 | blocked_no_original_package |
| health_need_and_access | AG_SEC_11.NSDstat | 1 | ag11_05 | blocked_no_original_package |

## Workbook Files

- `temp/priority_lsms_isa_raw_value_requirement_workbook.csv`
- `temp/priority_lsms_isa_raw_value_variable_workbook.csv`
- `temp/priority_lsms_isa_raw_value_file_workbook.csv`

## Stop Rule

Do not mark this wave as value-verified or analysis-ready until the workbook
evidence fields are filled from original raw files and all required gates pass.
