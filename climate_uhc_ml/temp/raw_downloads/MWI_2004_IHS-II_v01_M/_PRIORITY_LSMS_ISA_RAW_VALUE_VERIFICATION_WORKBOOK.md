# Priority LSMS-ISA Raw Value Verification Workbook

Dataset: `MWI_2004_IHS-II_v01_M` - Malawi 2004-2005

Official get-microdata URL: https://microdata.worldbank.org/catalog/2307/get-microdata

Target folder: `temp/raw_downloads/MWI_2004_IHS-II_v01_M/`

Current status: blocked until the complete original raw package and
documentation are present and readable.

## Requirement Checklist

| requirement | requirement_role | candidate_variable_rows | candidate_file_rows | current_verification_status |
|---|---|---|---|---|
| household_person_keys | merge_key_gate | 12 | 12 | ready_for_manual_raw_value_review_value_profile_available |
| weights_and_design | survey_design_gate | 12 | 12 | ready_for_manual_raw_value_review_value_profile_available |
| consumption_or_income | financial_denominator_gate | 12 | 3 | ready_for_manual_raw_value_review_value_profile_available |
| oop_health_expenditure | financial_outcome_gate | 12 | 1 | ready_for_manual_raw_value_review_value_profile_available |
| health_need_and_access | access_outcome_gate | 12 | 2 | ready_for_manual_raw_value_review_value_profile_available |
| survey_timing | climate_timing_gate | 12 | 7 | ready_for_manual_raw_value_review_value_profile_available |
| climate_geography | climate_geography_gate | 12 | 12 | ready_for_manual_raw_value_review_value_profile_available |
| missing_codes_units_recall_skip_patterns | documentation_semantics_gate | 0 | 0 | ready_for_manual_raw_value_review_semantics_review_available |

## File Review Preview

| requirement | file_name | candidate_variable_rows | top_variable_names | current_file_verification_status |
|---|---|---|---|---|
| climate_geography | sec_a.NSDstat | 1 | type | ready_for_manual_raw_value_review_value_profile_available |
| climate_geography | sec_f.NSDstat | 1 | type | ready_for_manual_raw_value_review_value_profile_available |
| climate_geography | sec_g.NSDstat | 1 | type | ready_for_manual_raw_value_review_value_profile_available |
| climate_geography | sec_h.NSDstat | 1 | type | ready_for_manual_raw_value_review_value_profile_available |
| climate_geography | sec_i.NSDstat | 1 | type | ready_for_manual_raw_value_review_value_profile_available |
| climate_geography | sec_j1.NSDstat | 1 | type | ready_for_manual_raw_value_review_value_profile_available |
| climate_geography | sec_j2.NSDstat | 1 | type | ready_for_manual_raw_value_review_value_profile_available |
| climate_geography | sec_k.NSDstat | 1 | type | ready_for_manual_raw_value_review_value_profile_available |
| consumption_or_income | sec_j1.NSDstat | 10 | add;case_id;dist;ea;hhid;hhsize;hhwght;j01a;j02a;j03a | ready_for_manual_raw_value_review_value_profile_available |
| consumption_or_income | sec_i.NSDstat | 1 | i03both | ready_for_manual_raw_value_review_value_profile_available |
| consumption_or_income | sec_aa.NSDstat | 1 | aa01 | ready_for_manual_raw_value_review_value_profile_available |
| health_need_and_access | sec_d.NSDstat | 7 | d05a;d05aoth;d05b;d05both;d27a;d27b;d04 | ready_for_manual_raw_value_review_value_profile_available |

## Workbook Files

- `temp/priority_lsms_isa_raw_value_requirement_workbook.csv`
- `temp/priority_lsms_isa_raw_value_variable_workbook.csv`
- `temp/priority_lsms_isa_raw_value_file_workbook.csv`

## Stop Rule

Do not mark this wave as value-verified or analysis-ready until the workbook
evidence fields are filled from original raw files and all required gates pass.
