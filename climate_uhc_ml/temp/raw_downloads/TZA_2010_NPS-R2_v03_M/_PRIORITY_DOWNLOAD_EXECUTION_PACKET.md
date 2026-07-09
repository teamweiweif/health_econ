# Priority Download Execution Packet

Dataset: `TZA_2010_NPS-R2_v03_M` - Tanzania 2010-2011

Download order: 8

Official get-microdata URL: https://microdata.worldbank.org/catalog/1050/get-microdata

Target folder: `temp/raw_downloads/TZA_2010_NPS-R2_v03_M/`

Current status: `ready_for_manual_credentialed_download_no_raw_receipt`

Raw receipt: `not_received_no_original_raw_package`

## Manual Download Scope

Download the complete unchanged official raw package plus all documentation
through the permitted World Bank account, terms, or Data Access Agreement
workflow. Do not assemble an incomplete analysis package from only the listed
core files.

## Minimum Acceptance Rule

Complete official package must be present; at least 12 priority core files/modules must be found directly or inside the official archive; all 8 promotion requirements and 39 selected first-pass variables must remain raw-backed before any data/ write.

## Core Files To Confirm

| core_file_rank | metadata_file_name | candidate_categories | expected_local_name_patterns | file_acceptance_status |
|---|---|---|---|---|
| 1 | AG_SEC2A | geography;shocks | AG_SEC2A;AG_SEC2A.*;AG_SEC2A.dta;AG_SEC2A.sav;AG_SEC2A.por;AG_SEC2A.sas7bdat;AG_SEC2A.xpt;AG_SEC2A.csv;*AG_SEC2A* | blocked_no_raw_or_archive_file |
| 2 | AG_SEC3A | consumption;health_need_access;shocks | AG_SEC3A;AG_SEC3A.*;AG_SEC3A.dta;AG_SEC3A.sav;AG_SEC3A.por;AG_SEC3A.sas7bdat;AG_SEC3A.xpt;AG_SEC3A.csv;*AG_SEC3A* | blocked_no_raw_or_archive_file |
| 3 | AG_SEC3B | consumption;health_need_access;shocks | AG_SEC3B;AG_SEC3B.*;AG_SEC3B.dta;AG_SEC3B.sav;AG_SEC3B.por;AG_SEC3B.sas7bdat;AG_SEC3B.xpt;AG_SEC3B.csv;*AG_SEC3B* | blocked_no_raw_or_archive_file |
| 4 | COMSEC_CD | geography;shocks;survey_design | COMSEC_CD;COMSEC_CD.*;COMSEC_CD.dta;COMSEC_CD.sav;COMSEC_CD.por;COMSEC_CD.sas7bdat;COMSEC_CD.xpt;COMSEC_CD.csv;*COMSE... | blocked_no_raw_or_archive_file |
| 5 | COMSEC_CE | demographics;geography;shocks;survey_design | COMSEC_CE;COMSEC_CE.*;COMSEC_CE.dta;COMSEC_CE.sav;COMSEC_CE.por;COMSEC_CE.sas7bdat;COMSEC_CE.xpt;COMSEC_CE.csv;*COMSE... | blocked_no_raw_or_archive_file |
| 6 | COMSEC_CI | demographics;geography;shocks;survey_design | COMSEC_CI;COMSEC_CI.*;COMSEC_CI.dta;COMSEC_CI.sav;COMSEC_CI.por;COMSEC_CI.sas7bdat;COMSEC_CI.xpt;COMSEC_CI.csv;*COMSE... | blocked_no_raw_or_archive_file |
| 7 | COMSEC_CJ | geography;survey_design | COMSEC_CJ;COMSEC_CJ.*;COMSEC_CJ.dta;COMSEC_CJ.sav;COMSEC_CJ.por;COMSEC_CJ.sas7bdat;COMSEC_CJ.xpt;COMSEC_CJ.csv;*COMSE... | blocked_no_raw_or_archive_file |
| 8 | HH_SEC_B | demographics;geography;survey_design | HH_SEC_B;HH_SEC_B.*;HH_SEC_B.dta;HH_SEC_B.sav;HH_SEC_B.por;HH_SEC_B.sas7bdat;HH_SEC_B.xpt;HH_SEC_B.csv;*HH_SEC_B* | blocked_no_raw_or_archive_file |
| 9 | HH_SEC_D | demographics;health_expenditure;health_need_access;survey_design | HH_SEC_D;HH_SEC_D.*;HH_SEC_D.dta;HH_SEC_D.sav;HH_SEC_D.por;HH_SEC_D.sas7bdat;HH_SEC_D.xpt;HH_SEC_D.csv;*HH_SEC_D* | blocked_no_raw_or_archive_file |
| 10 | TZY1.HH.Consumption | consumption;demographics;geography;health_need_access;survey_design | TZY1.HH.Consumption;TZY1.HH.*;*TZY1.HH* | blocked_no_raw_or_archive_file |
| 11 | TZY2.HH.Consumption | consumption;demographics;geography;health_need_access;survey_design | TZY2.HH.Consumption;TZY2.HH.*;*TZY2.HH* | blocked_no_raw_or_archive_file |
| 12 | HH.Geovariables_Y2 | geography;health_need_access;shocks;survey_design | HH.Geovariables_Y2;HH.*;*HH* | blocked_no_raw_or_archive_file |

## First-Pass Variables To Inspect

| requirement_id | concept | candidate_files | candidate_raw_variable | metadata_confidence | first_pass_review_status |
|---|---|---|---|---|---|
| household_person_merge_keys | household_id | AG_SEC10B;AG_SEC7A;AG_SEC7B | y2_hhid | high | blocked_raw_package_not_received |
| household_person_merge_keys | household_id | FS_J1;FS_J3;HH_SEC_H1;TZY1.HH.Consumption | hhid | high | blocked_raw_package_not_received |
| household_person_merge_keys | demographics | AG_SEC01 | ag1a_02 | high | blocked_raw_package_not_received |
| household_person_merge_keys | demographics | AG_SEC01 | ag1a_03 | high | blocked_raw_package_not_received |
| weights_and_survey_design | survey_weight | COMSEC_CJ | cm_j01b | high | blocked_raw_package_not_received |
| weights_and_survey_design | survey_weight | COMSEC_CJ | cm_j02b | high | blocked_raw_package_not_received |
| weights_and_survey_design | psu_cluster | COMSEC_CA;COMSEC_CB;COMSEC_CD;COMSEC_CE;COMSEC_CF;COMSEC_CG;COMSEC_CH;COMSEC_CI;COMSEC_CJ;comsec_cc | id_04 | high | blocked_raw_package_not_received |
| weights_and_survey_design | psu_cluster | COMSEC_CI | cm_i15d | high | blocked_raw_package_not_received |
| weights_and_survey_design | strata | HH_SEC_A | strataid | high | blocked_raw_package_not_received |
| weights_and_survey_design | strata | TZY1.HH.Consumption;TZY2.HH.Consumption | strata | high | blocked_raw_package_not_received |
| consumption_or_income_aggregate | total_consumption_or_income | AG_SEC3A | ag3a_04 | high | blocked_raw_package_not_received |
| consumption_or_income_aggregate | total_consumption_or_income | AG_SEC3B | ag3b_04 | high | blocked_raw_package_not_received |
| oop_health_expenditure | oop_health_expenditure | HH_SEC_D | hh_d13 | high | blocked_raw_package_not_received |
| oop_health_expenditure | oop_health_expenditure | HH_SEC_D | hh_d15 | high | blocked_raw_package_not_received |
| illness_need_care_access | health_need | HH_SEC_D | hh_d12_1 | high | blocked_raw_package_not_received |
| illness_need_care_access | health_need | HH_SEC_D | hh_d12_2 | high | blocked_raw_package_not_received |
| illness_need_care_access | care_or_barrier | HH_SEC_D | hh_d04_1 | high | blocked_raw_package_not_received |
| illness_need_care_access | care_or_barrier | HH_SEC_D | hh_d04_2 | high | blocked_raw_package_not_received |
| illness_need_care_access | insurance |  |  | metadata_candidate_from_concept_checklist | blocked_raw_package_not_received |
| survey_timing | survey_timing | TZY1.HH.Consumption;TZY2.HH.Consumption | intmonth | high | blocked_raw_package_not_received |
| survey_timing | survey_timing | TZY1.HH.Consumption;TZY2.HH.Consumption | quarter | high | blocked_raw_package_not_received |
| geography_climate_linkage | climate_geography | AG_SEC2A | ag2a_09 | high | blocked_raw_package_not_received |
| geography_climate_linkage | climate_geography | AG_SEC2A | ag2a_10 | high | blocked_raw_package_not_received |
| missing_skip_units_recall | household_id | AG_SEC10B;AG_SEC7A;AG_SEC7B | y2_hhid | high | blocked_raw_package_not_received |
| missing_skip_units_recall | household_id | FS_J1;FS_J3;HH_SEC_H1;TZY1.HH.Consumption | hhid | high | blocked_raw_package_not_received |
| missing_skip_units_recall | survey_weight | COMSEC_CJ | cm_j01b | high | blocked_raw_package_not_received |
| missing_skip_units_recall | survey_weight | COMSEC_CJ | cm_j02b | high | blocked_raw_package_not_received |
| missing_skip_units_recall | total_consumption_or_income | AG_SEC3A | ag3a_04 | high | blocked_raw_package_not_received |
| missing_skip_units_recall | total_consumption_or_income | AG_SEC3B | ag3b_04 | high | blocked_raw_package_not_received |
| missing_skip_units_recall | oop_health_expenditure | HH_SEC_D | hh_d13 | high | blocked_raw_package_not_received |
| missing_skip_units_recall | oop_health_expenditure | HH_SEC_D | hh_d15 | high | blocked_raw_package_not_received |
| missing_skip_units_recall | health_need | HH_SEC_D | hh_d12_1 | high | blocked_raw_package_not_received |
| missing_skip_units_recall | health_need | HH_SEC_D | hh_d12_2 | high | blocked_raw_package_not_received |
| missing_skip_units_recall | care_or_barrier | HH_SEC_D | hh_d04_1 | high | blocked_raw_package_not_received |
| missing_skip_units_recall | care_or_barrier | HH_SEC_D | hh_d04_2 | high | blocked_raw_package_not_received |
| missing_skip_units_recall | survey_timing | TZY1.HH.Consumption;TZY2.HH.Consumption | intmonth | high | blocked_raw_package_not_received |
| missing_skip_units_recall | survey_timing | TZY1.HH.Consumption;TZY2.HH.Consumption | quarter | high | blocked_raw_package_not_received |
| missing_skip_units_recall | climate_geography | AG_SEC2A | ag2a_09 | high | blocked_raw_package_not_received |
| missing_skip_units_recall | climate_geography | AG_SEC2A | ag2a_10 | high | blocked_raw_package_not_received |

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
