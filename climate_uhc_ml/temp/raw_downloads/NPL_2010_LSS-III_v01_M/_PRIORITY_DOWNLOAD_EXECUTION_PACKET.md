# Priority Download Execution Packet

Dataset: `NPL_2010_LSS-III_v01_M` - Nepal 2010-2011

Download order: 13

Official get-microdata URL: https://microdata.worldbank.org/catalog/1000/get-microdata

Target folder: `temp/raw_downloads/NPL_2010_LSS-III_v01_M/`

Current status: `ready_for_manual_credentialed_download_no_raw_receipt`

Raw receipt: `not_received_no_original_raw_package`

## Manual Download Scope

Download the complete unchanged official raw package plus all documentation
through the permitted World Bank account, terms, or Data Access Agreement
workflow. Do not assemble an incomplete analysis package from only the listed
core files.

## Minimum Acceptance Rule

Complete official package must be present; at least 12 priority core files/modules must be found directly or inside the official archive; all 8 promotion requirements and 35 selected first-pass variables must remain raw-backed before any data/ write.

## Core Files To Confirm

| core_file_rank | metadata_file_name | candidate_categories | expected_local_name_patterns | file_acceptance_status |
|---|---|---|---|---|
| 1 | anthro | demographics;survey_design | anthro;anthro.*;anthro.dta;anthro.sav;anthro.por;anthro.sas7bdat;anthro.xpt;anthro.csv;*anthro* | blocked_no_raw_or_archive_file |
| 2 | FINAL_PREF | consumption;demographics;geography;shocks;survey_design | FINAL_PREF;FINAL_PREF.*;FINAL_PREF.dta;FINAL_PREF.sav;FINAL_PREF.por;FINAL_PREF.sas7bdat;FINAL_PREF.xpt;FINAL_PREF.cs... | blocked_no_raw_or_archive_file |
| 3 | S01 | demographics;geography;survey_design | S01;S01.*;S01.dta;S01.sav;S01.por;S01.sas7bdat;S01.xpt;S01.csv;*S01* | blocked_no_raw_or_archive_file |
| 4 | S04 | geography;survey_design | S04;S04.*;S04.dta;S04.sav;S04.por;S04.sas7bdat;S04.xpt;S04.csv;*S04* | blocked_no_raw_or_archive_file |
| 5 | S08 | health_expenditure;health_need_access;survey_design | S08;S08.*;S08.dta;S08.sav;S08.por;S08.sas7bdat;S08.xpt;S08.csv;*S08* | blocked_no_raw_or_archive_file |
| 6 | S13A1 | geography;shocks;survey_design | S13A1;S13A1.*;S13A1.dta;S13A1.sav;S13A1.por;S13A1.sas7bdat;S13A1.xpt;S13A1.csv;*S13A1* | blocked_no_raw_or_archive_file |
| 7 | S16 | demographics;geography;survey_design | S16;S16.*;S16.dta;S16.sav;S16.por;S16.sas7bdat;S16.xpt;S16.csv;*S16* | blocked_no_raw_or_archive_file |
| 8 | S19 | consumption;demographics;health_need_access;shocks;survey_design | S19;S19.*;S19.dta;S19.sav;S19.por;S19.sas7bdat;S19.xpt;S19.csv;*S19* | blocked_no_raw_or_archive_file |
| 9 | S20 | demographics;survey_design | S20;S20.*;S20.dta;S20.sav;S20.por;S20.sas7bdat;S20.xpt;S20.csv;*S20* | blocked_no_raw_or_archive_file |
| 10 | S21 | demographics;geography;survey_design | S21;S21.*;S21.dta;S21.sav;S21.por;S21.sas7bdat;S21.xpt;S21.csv;*S21* | blocked_no_raw_or_archive_file |
| 11 | sample | demographics;geography;survey_design | sample;sample.*;sample.dta;sample.sav;sample.por;sample.sas7bdat;sample.xpt;sample.csv;*sample* | blocked_no_raw_or_archive_file |
| 12 | S00 | demographics;geography;health_need_access;shocks;survey_design | S00;S00.*;S00.dta;S00.sav;S00.por;S00.sas7bdat;S00.xpt;S00.csv;*S00* | blocked_no_raw_or_archive_file |

## First-Pass Variables To Inspect

| requirement_id | concept | candidate_files | candidate_raw_variable | metadata_confidence | first_pass_review_status |
|---|---|---|---|---|---|
| household_person_merge_keys | household_id |  |  | metadata_candidate_from_concept_checklist | blocked_raw_package_not_received |
| household_person_merge_keys | demographics | FINAL_PREF | depratio3 | high | blocked_raw_package_not_received |
| household_person_merge_keys | demographics | FINAL_PREF | educatn | high | blocked_raw_package_not_received |
| weights_and_survey_design | survey_weight | S20 | v20_07 | high | blocked_raw_package_not_received |
| weights_and_survey_design | survey_weight | anthro | underwt | high | blocked_raw_package_not_received |
| weights_and_survey_design | psu_cluster | FINAL_PREF;anthro;sample;sys | xhpsu | high | blocked_raw_package_not_received |
| weights_and_survey_design | psu_cluster | S00 | v00_dist | high | blocked_raw_package_not_received |
| weights_and_survey_design | strata | FINAL_PREF;sample | stratum | high | blocked_raw_package_not_received |
| weights_and_survey_design | strata | FINAL_PREF;S00;S01;S02;S03;S04;S05;S06A;S06B;S06C;S06D;S07;S08;S09A;S09B;S09C;S09D;S10A;S10B;S11 | xstra | high | blocked_raw_package_not_received |
| consumption_or_income_aggregate | total_consumption_or_income | FINAL_PREF | sh_consdur_30 | high | blocked_raw_package_not_received |
| consumption_or_income_aggregate | total_consumption_or_income | FINAL_PREF | sh_consdur_7 | high | blocked_raw_package_not_received |
| oop_health_expenditure | oop_health_expenditure | S08 | v08_17a | high | blocked_raw_package_not_received |
| oop_health_expenditure | oop_health_expenditure | S08 | v08_17b | high | blocked_raw_package_not_received |
| illness_need_care_access | health_need | S08 | v08_04 | high | blocked_raw_package_not_received |
| illness_need_care_access | health_need | S08 | v08_05 | high | blocked_raw_package_not_received |
| illness_need_care_access | care_or_barrier | S08 | v08_14 | high | blocked_raw_package_not_received |
| illness_need_care_access | care_or_barrier | S08 | v08_15 | high | blocked_raw_package_not_received |
| illness_need_care_access | insurance |  |  | metadata_candidate_from_concept_checklist | blocked_raw_package_not_received |
| survey_timing | survey_timing | FINAL_PREF | Date | high | blocked_raw_package_not_received |
| geography_climate_linkage | climate_geography | FINAL_PREF;sample | district | high | blocked_raw_package_not_received |
| geography_climate_linkage | climate_geography | FINAL_PREF;sample | region | high | blocked_raw_package_not_received |
| missing_skip_units_recall | household_id |  |  | metadata_candidate_from_concept_checklist | blocked_raw_package_not_received |
| missing_skip_units_recall | survey_weight | S20 | v20_07 | high | blocked_raw_package_not_received |
| missing_skip_units_recall | survey_weight | anthro | underwt | high | blocked_raw_package_not_received |
| missing_skip_units_recall | total_consumption_or_income | FINAL_PREF | sh_consdur_30 | high | blocked_raw_package_not_received |
| missing_skip_units_recall | total_consumption_or_income | FINAL_PREF | sh_consdur_7 | high | blocked_raw_package_not_received |
| missing_skip_units_recall | oop_health_expenditure | S08 | v08_17a | high | blocked_raw_package_not_received |
| missing_skip_units_recall | oop_health_expenditure | S08 | v08_17b | high | blocked_raw_package_not_received |
| missing_skip_units_recall | health_need | S08 | v08_04 | high | blocked_raw_package_not_received |
| missing_skip_units_recall | health_need | S08 | v08_05 | high | blocked_raw_package_not_received |
| missing_skip_units_recall | care_or_barrier | S08 | v08_14 | high | blocked_raw_package_not_received |
| missing_skip_units_recall | care_or_barrier | S08 | v08_15 | high | blocked_raw_package_not_received |
| missing_skip_units_recall | survey_timing | FINAL_PREF | Date | high | blocked_raw_package_not_received |
| missing_skip_units_recall | climate_geography | FINAL_PREF;sample | district | high | blocked_raw_package_not_received |
| missing_skip_units_recall | climate_geography | FINAL_PREF;sample | region | high | blocked_raw_package_not_received |

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
