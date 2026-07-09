# Priority Download Execution Packet

Dataset: `JAM_1997_SLC_v01_M` - Jamaica 1997

Download order: 11

Official get-microdata URL: https://microdata.worldbank.org/catalog/2368/get-microdata

Target folder: `temp/raw_downloads/JAM_1997_SLC_v01_M/`

Current status: `ready_for_manual_credentialed_download_no_raw_receipt`

Raw receipt: `not_received_no_original_raw_package`

## Manual Download Scope

Download the complete unchanged official raw package plus all documentation
through the permitted World Bank account, terms, or Data Access Agreement
workflow. Do not assemble an incomplete analysis package from only the listed
core files.

## Minimum Acceptance Rule

Complete official package must be present; at least 12 priority core files/modules must be found directly or inside the official archive; all 8 promotion requirements and 31 selected first-pass variables must remain raw-backed before any data/ write.

## Core Files To Confirm

| core_file_rank | metadata_file_name | candidate_categories | expected_local_name_patterns | file_acceptance_status |
|---|---|---|---|---|
| 1 | REC001 | demographics;geography;survey_design | REC001;REC001.*;REC001.dta;REC001.sav;REC001.por;REC001.sas7bdat;REC001.xpt;REC001.csv;*REC001* | blocked_no_raw_or_archive_file |
| 2 | REC003 | health_expenditure;health_need_access | REC003;REC003.*;REC003.dta;REC003.sav;REC003.por;REC003.sas7bdat;REC003.xpt;REC003.csv;*REC003* | blocked_no_raw_or_archive_file |
| 3 | REC006 | geography;health_need_access | REC006;REC006.*;REC006.dta;REC006.sav;REC006.por;REC006.sas7bdat;REC006.xpt;REC006.csv;*REC006* | blocked_no_raw_or_archive_file |
| 4 | REC007 | demographics;survey_design | REC007;REC007.*;REC007.dta;REC007.sav;REC007.por;REC007.sas7bdat;REC007.xpt;REC007.csv;*REC007* | blocked_no_raw_or_archive_file |
| 5 | REC025 | consumption | REC025;REC025.*;REC025.dta;REC025.sav;REC025.por;REC025.sas7bdat;REC025.xpt;REC025.csv;*REC025* | blocked_no_raw_or_archive_file |
| 6 | ANNUAL | consumption;demographics;geography;survey_design | ANNUAL;ANNUAL.*;ANNUAL.dta;ANNUAL.sav;ANNUAL.por;ANNUAL.sas7bdat;ANNUAL.xpt;ANNUAL.csv;*ANNUAL* | blocked_no_raw_or_archive_file |
| 7 | EDTOTALS | consumption;demographics;geography;survey_design | EDTOTALS;EDTOTALS.*;EDTOTALS.dta;EDTOTALS.sav;EDTOTALS.por;EDTOTALS.sas7bdat;EDTOTALS.xpt;EDTOTALS.csv;*EDTOTALS* | blocked_no_raw_or_archive_file |
| 8 | EXP97 | consumption;geography;survey_design | EXP97;EXP97.*;EXP97.dta;EXP97.sav;EXP97.por;EXP97.sas7bdat;EXP97.xpt;EXP97.csv;*EXP97* | blocked_no_raw_or_archive_file |
| 9 | HEADS | demographics;geography;survey_design | HEADS;HEADS.*;HEADS.dta;HEADS.sav;HEADS.por;HEADS.sas7bdat;HEADS.xpt;HEADS.csv;*HEADS* | blocked_no_raw_or_archive_file |
| 10 | HHSIZE | demographics;geography | HHSIZE;HHSIZE.*;HHSIZE.dta;HHSIZE.sav;HHSIZE.por;HHSIZE.sas7bdat;HHSIZE.xpt;HHSIZE.csv;*HHSIZE* | blocked_no_raw_or_archive_file |
| 11 | LABORF | demographics;geography;health_need_access;shocks;survey_design | LABORF;LABORF.*;LABORF.dta;LABORF.sav;LABORF.por;LABORF.sas7bdat;LABORF.xpt;LABORF.csv;*LABORF* | blocked_no_raw_or_archive_file |
| 12 | NUTR97 | demographics;survey_design | NUTR97;NUTR97.*;NUTR97.dta;NUTR97.sav;NUTR97.por;NUTR97.sas7bdat;NUTR97.xpt;NUTR97.csv;*NUTR97* | blocked_no_raw_or_archive_file |

## First-Pass Variables To Inspect

| requirement_id | concept | candidate_files | candidate_raw_variable | metadata_confidence | first_pass_review_status |
|---|---|---|---|---|---|
| household_person_merge_keys | household_id |  |  | metadata_candidate_from_concept_checklist | blocked_raw_package_not_received |
| household_person_merge_keys | demographics | ANNUAL;HHSIZE | hhsize1 | high | blocked_raw_package_not_received |
| household_person_merge_keys | demographics | ANNUAL;HHSIZE | hhsize2 | high | blocked_raw_package_not_received |
| weights_and_survey_design | survey_weight | ANNUAL;EDTOTALS;REC001 | edwght | high | blocked_raw_package_not_received |
| weights_and_survey_design | survey_weight | NUTR97 | waz | high | blocked_raw_package_not_received |
| weights_and_survey_design | psu_cluster | EXP97 | Cluster | high | blocked_raw_package_not_received |
| weights_and_survey_design | strata | REC033 | strat | high | blocked_raw_package_not_received |
| consumption_or_income_aggregate | total_consumption_or_income | ANNUAL | cons | moderate | blocked_raw_package_not_received |
| oop_health_expenditure | oop_health_expenditure | REC003 | a11 | moderate | blocked_raw_package_not_received |
| oop_health_expenditure | oop_health_expenditure | REC003 | a12 | moderate | blocked_raw_package_not_received |
| illness_need_care_access | health_need | REC002 | a01 | high | blocked_raw_package_not_received |
| illness_need_care_access | health_need | REC002 | a02 | high | blocked_raw_package_not_received |
| illness_need_care_access | care_or_barrier | REC003 | a09 | high | blocked_raw_package_not_received |
| illness_need_care_access | care_or_barrier | REC003 | a10 | high | blocked_raw_package_not_received |
| illness_need_care_access | insurance | REC003 | a21 | high | blocked_raw_package_not_received |
| survey_timing | survey_timing | REC001 | int_date | high | blocked_raw_package_not_received |
| geography_climate_linkage | climate_geography | ANNUAL;EDTOTALS;HEADS;HHSIZE;REC001 | district | high | blocked_raw_package_not_received |
| geography_climate_linkage | climate_geography | EDTOTALS;REC001 | region | high | blocked_raw_package_not_received |
| missing_skip_units_recall | household_id |  |  | metadata_candidate_from_concept_checklist | blocked_raw_package_not_received |
| missing_skip_units_recall | survey_weight | ANNUAL;EDTOTALS;REC001 | edwght | high | blocked_raw_package_not_received |
| missing_skip_units_recall | survey_weight | NUTR97 | waz | high | blocked_raw_package_not_received |
| missing_skip_units_recall | total_consumption_or_income | ANNUAL | cons | moderate | blocked_raw_package_not_received |
| missing_skip_units_recall | oop_health_expenditure | REC003 | a11 | moderate | blocked_raw_package_not_received |
| missing_skip_units_recall | oop_health_expenditure | REC003 | a12 | moderate | blocked_raw_package_not_received |
| missing_skip_units_recall | health_need | REC002 | a01 | high | blocked_raw_package_not_received |
| missing_skip_units_recall | health_need | REC002 | a02 | high | blocked_raw_package_not_received |
| missing_skip_units_recall | care_or_barrier | REC003 | a09 | high | blocked_raw_package_not_received |
| missing_skip_units_recall | care_or_barrier | REC003 | a10 | high | blocked_raw_package_not_received |
| missing_skip_units_recall | survey_timing | REC001 | int_date | high | blocked_raw_package_not_received |
| missing_skip_units_recall | climate_geography | ANNUAL;EDTOTALS;HEADS;HHSIZE;REC001 | district | high | blocked_raw_package_not_received |
| missing_skip_units_recall | climate_geography | EDTOTALS;REC001 | region | high | blocked_raw_package_not_received |

## Post-Download Commands

- `python script/17_audit_raw_downloads.py`
- `python script/128_build_priority_archive_member_preflight.py`
- `python script/130_build_priority_raw_package_receipt_ledger.py`
- `python script/03_inspect_raw_schemas.py`
- `python script/29_build_raw_variable_verification_protocol.py`
- `python script/33_build_harmonization_recipe_gate.py`
- `python script/125_build_priority_climate_linkage_preflight.py`
- `python script/126_build_priority_raw_verification_workbook.py`
- `python script/140_build_priority_first_pass_variable_review_queue.py`
- `python script/129_build_priority_manual_verification_decision_gate.py`
- `python script/132_build_priority_analysis_dataset_synthesis_blueprint.py`
- `python script/134_build_priority_country_wave_promotion_packets.py`
- `python script/127_enforce_promoted_data_gate.py`
- `python script/36_build_direct_read_audit_bundle.py`
- `python script/14_validate_workspace.py`

## Stop Rule

Do not write this country-wave into data/ until original package receipt, core-file coverage, raw schema inspection, manual value/unit/key review, outcome readiness, and accepted CHIRPS/ERA5 linkage all pass.
