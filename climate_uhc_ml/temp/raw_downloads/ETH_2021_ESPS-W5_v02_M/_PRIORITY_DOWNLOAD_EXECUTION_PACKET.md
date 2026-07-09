# Priority Download Execution Packet

Dataset: `ETH_2021_ESPS-W5_v02_M` - Ethiopia 2021-2022

Download order: 1

Official get-microdata URL: https://microdata.worldbank.org/catalog/6161/get-microdata

Target folder: `temp/raw_downloads/ETH_2021_ESPS-W5_v02_M/`

Current status: `ready_for_manual_credentialed_download_no_raw_receipt`

Raw receipt: `not_received_no_original_raw_package`

## Manual Download Scope

Download the complete unchanged official raw package plus all documentation
through the permitted World Bank account, terms, or Data Access Agreement
workflow. Do not assemble an incomplete analysis package from only the listed
core files.

## Minimum Acceptance Rule

Complete official package must be present; at least 12 priority core files/modules must be found directly or inside the official archive; all 8 promotion requirements and 37 selected first-pass variables must remain raw-backed before any data/ write.

## Core Files To Confirm

| core_file_rank | metadata_file_name | candidate_categories | expected_local_name_patterns | file_acceptance_status |
|---|---|---|---|---|
| 1 | sect3_hh_w5.dta | demographics;geography;health_expenditure;health_need_access;survey_design | sect3_hh_w5.dta;sect3_hh_w5.*;*sect3_hh_w5* | blocked_no_raw_or_archive_file |
| 2 | sect04_com_w5.dta | demographics;geography;health_need_access;shocks;survey_design | sect04_com_w5.dta;sect04_com_w5.*;*sect04_com_w5* | blocked_no_raw_or_archive_file |
| 3 | sect06_com_w5.dta | geography;health_need_access;shocks;survey_design | sect06_com_w5.dta;sect06_com_w5.*;*sect06_com_w5* | blocked_no_raw_or_archive_file |
| 4 | sect11_com_w5.dta | demographics;geography;shocks;survey_design | sect11_com_w5.dta;sect11_com_w5.*;*sect11_com_w5* | blocked_no_raw_or_archive_file |
| 5 | sect3_pp_w5.dta | geography;health_need_access;shocks;survey_design | sect3_pp_w5.dta;sect3_pp_w5.*;*sect3_pp_w5* | blocked_no_raw_or_archive_file |
| 6 | sect4_pp_w5.dta | geography;shocks;survey_design | sect4_pp_w5.dta;sect4_pp_w5.*;*sect4_pp_w5* | blocked_no_raw_or_archive_file |
| 7 | sect7_pp_w5.dta | demographics;geography;health_need_access;shocks;survey_design | sect7_pp_w5.dta;sect7_pp_w5.*;*sect7_pp_w5* | blocked_no_raw_or_archive_file |
| 8 | sect9_ph_w5.dta | geography;shocks;survey_design | sect9_ph_w5.dta;sect9_ph_w5.*;*sect9_ph_w5* | blocked_no_raw_or_archive_file |
| 9 | sect11_ph_w5.dta | geography;health_need_access;shocks;survey_design | sect11_ph_w5.dta;sect11_ph_w5.*;*sect11_ph_w5* | blocked_no_raw_or_archive_file |
| 10 | sect8_2_ls_w5.dta | consumption;geography;health_need_access;shocks;survey_design | sect8_2_ls_w5.dta;sect8_2_ls_w5.*;*sect8_2_ls_w5* | blocked_no_raw_or_archive_file |
| 11 | sect8_3_ls_w5.dta | geography;health_expenditure;health_need_access;shocks;survey_design | sect8_3_ls_w5.dta;sect8_3_ls_w5.*;*sect8_3_ls_w5* | blocked_no_raw_or_archive_file |
| 12 | eth_householdgeovariables_y5.dta | geography;health_need_access;shocks;survey_design | eth_householdgeovariables_y5.dta;eth_householdgeovariables_y5.*;*eth_householdgeovariables_y5* | blocked_no_raw_or_archive_file |

## First-Pass Variables To Inspect

| requirement_id | concept | candidate_files | candidate_raw_variable | metadata_confidence | first_pass_review_status |
|---|---|---|---|---|---|
| household_person_merge_keys | household_id | eth_householdgeovariables_y5.dta;eth_plotgeovariables_y5.dta | household_id | high | blocked_raw_package_not_received |
| household_person_merge_keys | household_id | sect10_ph_w5.dta;sect10a_hh_w5.dta;sect11_hh_w5.dta;sect11_ph_w5.dta;sect12a_hh_w5.dta;sect12b1_hh_w5.dta;sect12b2_hh... | saq08 | high | blocked_raw_package_not_received |
| household_person_merge_keys | demographics | cons_agg_w5.dta | educ_cons_ann | high | blocked_raw_package_not_received |
| household_person_merge_keys | demographics | cons_agg_w5.dta | hh_size | high | blocked_raw_package_not_received |
| weights_and_survey_design | survey_weight | cons_agg_w5.dta;sect10_ph_w5.dta;sect10a_hh_w5.dta;sect11_hh_w5.dta;sect11_ph_w5.dta;sect12a_hh_w5.dta;sect12b1_hh_w5... | pw_w5 | high | blocked_raw_package_not_received |
| weights_and_survey_design | survey_weight | sect10b_com_w5.dta | cs10bq04 | high | blocked_raw_package_not_received |
| weights_and_survey_design | psu_cluster | cons_agg_w5.dta;sect01a_com_w5.dta;sect01b_com_w5.dta;sect02_com_w5.dta;sect03_com_w5.dta;sect04_com_w5.dta;sect05_co... | ea_id | high | blocked_raw_package_not_received |
| weights_and_survey_design | psu_cluster | eth_householdgeovariables_y5.dta;eth_plotgeovariables_y5.dta | pct_urban_cluster | high | blocked_raw_package_not_received |
| weights_and_survey_design | strata | sect8_3_ls_w5.dta | ls_s8_3q01 | high | blocked_raw_package_not_received |
| weights_and_survey_design | strata | sect8_3_ls_w5.dta | ls_s8_3q02 | high | blocked_raw_package_not_received |
| consumption_or_income_aggregate | total_consumption_or_income | sect8_2_ls_w5.dta | ls_s8_2q14 | high | blocked_raw_package_not_received |
| consumption_or_income_aggregate | total_consumption_or_income | sect8_2_ls_w5.dta | ls_s8_2q18 | high | blocked_raw_package_not_received |
| oop_health_expenditure | oop_health_expenditure | sect3_hh_w5.dta;sect3_pp_w5.dta | s3q18 | high | blocked_raw_package_not_received |
| oop_health_expenditure | oop_health_expenditure | sect8_3_ls_w5.dta | ls_s8_3q04 | moderate | blocked_raw_package_not_received |
| illness_need_care_access | health_need | sect3_hh_w5.dta | s3q05 | high | blocked_raw_package_not_received |
| illness_need_care_access | health_need | sect3_hh_w5.dta | s3q06_1 | high | blocked_raw_package_not_received |
| illness_need_care_access | care_or_barrier | sect04_com_w5.dta | cs4q28 | high | blocked_raw_package_not_received |
| illness_need_care_access | care_or_barrier | sect04_com_w5.dta | cs4q30 | high | blocked_raw_package_not_received |
| illness_need_care_access | insurance | sect3_hh_w5.dta | s3q19 | high | blocked_raw_package_not_received |
| survey_timing | survey_timing | sect_cover_ls_w5.dta;sect_cover_ph_w5.dta;sect_cover_pp_w5.dta | InterviewDate | high | blocked_raw_package_not_received |
| geography_climate_linkage | climate_geography | cons_agg_w5.dta;sect01a_com_w5.dta;sect01b_com_w5.dta;sect02_com_w5.dta;sect03_com_w5.dta;sect04_com_w5.dta;sect05_co... | saq01 | high | blocked_raw_package_not_received |
| geography_climate_linkage | climate_geography | eth_householdgeovariables_y5.dta;eth_plotgeovariables_y5.dta | cropshare | high | blocked_raw_package_not_received |
| missing_skip_units_recall | household_id | eth_householdgeovariables_y5.dta;eth_plotgeovariables_y5.dta | household_id | high | blocked_raw_package_not_received |
| missing_skip_units_recall | household_id | sect10_ph_w5.dta;sect10a_hh_w5.dta;sect11_hh_w5.dta;sect11_ph_w5.dta;sect12a_hh_w5.dta;sect12b1_hh_w5.dta;sect12b2_hh... | saq08 | high | blocked_raw_package_not_received |
| missing_skip_units_recall | survey_weight | cons_agg_w5.dta;sect10_ph_w5.dta;sect10a_hh_w5.dta;sect11_hh_w5.dta;sect11_ph_w5.dta;sect12a_hh_w5.dta;sect12b1_hh_w5... | pw_w5 | high | blocked_raw_package_not_received |
| missing_skip_units_recall | survey_weight | sect10b_com_w5.dta | cs10bq04 | high | blocked_raw_package_not_received |
| missing_skip_units_recall | total_consumption_or_income | sect8_2_ls_w5.dta | ls_s8_2q14 | high | blocked_raw_package_not_received |
| missing_skip_units_recall | total_consumption_or_income | sect8_2_ls_w5.dta | ls_s8_2q18 | high | blocked_raw_package_not_received |
| missing_skip_units_recall | oop_health_expenditure | sect3_hh_w5.dta;sect3_pp_w5.dta | s3q18 | high | blocked_raw_package_not_received |
| missing_skip_units_recall | oop_health_expenditure | sect8_3_ls_w5.dta | ls_s8_3q04 | moderate | blocked_raw_package_not_received |
| missing_skip_units_recall | health_need | sect3_hh_w5.dta | s3q05 | high | blocked_raw_package_not_received |
| missing_skip_units_recall | health_need | sect3_hh_w5.dta | s3q06_1 | high | blocked_raw_package_not_received |
| missing_skip_units_recall | care_or_barrier | sect04_com_w5.dta | cs4q28 | high | blocked_raw_package_not_received |
| missing_skip_units_recall | care_or_barrier | sect04_com_w5.dta | cs4q30 | high | blocked_raw_package_not_received |
| missing_skip_units_recall | survey_timing | sect_cover_ls_w5.dta;sect_cover_ph_w5.dta;sect_cover_pp_w5.dta | InterviewDate | high | blocked_raw_package_not_received |
| missing_skip_units_recall | climate_geography | cons_agg_w5.dta;sect01a_com_w5.dta;sect01b_com_w5.dta;sect02_com_w5.dta;sect03_com_w5.dta;sect04_com_w5.dta;sect05_co... | saq01 | high | blocked_raw_package_not_received |
| missing_skip_units_recall | climate_geography | eth_householdgeovariables_y5.dta;eth_plotgeovariables_y5.dta | cropshare | high | blocked_raw_package_not_received |

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
