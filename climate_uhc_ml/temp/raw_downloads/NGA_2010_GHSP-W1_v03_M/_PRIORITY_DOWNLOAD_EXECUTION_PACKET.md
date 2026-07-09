# Priority Download Execution Packet

Dataset: `NGA_2010_GHSP-W1_v03_M` - Nigeria 2010-2011

Download order: 6

Official get-microdata URL: https://microdata.worldbank.org/catalog/1002/get-microdata

Target folder: `temp/raw_downloads/NGA_2010_GHSP-W1_v03_M/`

Current status: `ready_for_manual_credentialed_download_no_raw_receipt`

Raw receipt: `not_received_no_original_raw_package`

## Manual Download Scope

Download the complete unchanged official raw package plus all documentation
through the permitted World Bank account, terms, or Data Access Agreement
workflow. Do not assemble an incomplete analysis package from only the listed
core files.

## Minimum Acceptance Rule

Complete official package must be present; at least 12 priority core files/modules must be found directly or inside the official archive; all 8 promotion requirements and 33 selected first-pass variables must remain raw-backed before any data/ write.

## Core Files To Confirm

| core_file_rank | metadata_file_name | candidate_categories | expected_local_name_patterns | file_acceptance_status |
|---|---|---|---|---|
| 1 | NGA_HouseholdGeovariables_Y1 | geography;health_need_access;shocks;survey_design | NGA_HouseholdGeovariables_Y1;NGA_HouseholdGeovariables_Y1.*;NGA_HouseholdGeovariables_Y1.dta;NGA_HouseholdGeovariable... | blocked_no_raw_or_archive_file |
| 2 | secta1_harvestw1 | geography;shocks;survey_design | secta1_harvestw1;secta1_harvestw1.*;secta1_harvestw1.dta;secta1_harvestw1.sav;secta1_harvestw1.por;secta1_harvestw1.s... | blocked_no_raw_or_archive_file |
| 3 | secta2_harvestw1 | geography;shocks;survey_design | secta2_harvestw1;secta2_harvestw1.*;secta2_harvestw1.dta;secta2_harvestw1.sav;secta2_harvestw1.por;secta2_harvestw1.s... | blocked_no_raw_or_archive_file |
| 4 | secta3_harvestw1 | geography;health_need_access;shocks;survey_design | secta3_harvestw1;secta3_harvestw1.*;secta3_harvestw1.dta;secta3_harvestw1.sav;secta3_harvestw1.por;secta3_harvestw1.s... | blocked_no_raw_or_archive_file |
| 5 | sect1_harvestw1 | demographics;geography;health_need_access;survey_design | sect1_harvestw1;sect1_harvestw1.*;sect1_harvestw1.dta;sect1_harvestw1.sav;sect1_harvestw1.por;sect1_harvestw1.sas7bda... | blocked_no_raw_or_archive_file |
| 6 | sect4a_harvestw1 | demographics;geography;health_expenditure;health_need_access;survey_design | sect4a_harvestw1;sect4a_harvestw1.*;sect4a_harvestw1.dta;sect4a_harvestw1.sav;sect4a_harvestw1.por;sect4a_harvestw1.s... | blocked_no_raw_or_archive_file |
| 7 | sect8_harvestw1 | demographics;geography;survey_design | sect8_harvestw1;sect8_harvestw1.*;sect8_harvestw1.dta;sect8_harvestw1.sav;sect8_harvestw1.por;sect8_harvestw1.sas7bda... | blocked_no_raw_or_archive_file |
| 8 | sect11b_plantingw1 | geography;shocks;survey_design | sect11b_plantingw1;sect11b_plantingw1.*;sect11b_plantingw1.dta;sect11b_plantingw1.sav;sect11b_plantingw1.por;sect11b_... | blocked_no_raw_or_archive_file |
| 9 | sect11c_plantingw1 | geography;shocks;survey_design | sect11c_plantingw1;sect11c_plantingw1.*;sect11c_plantingw1.dta;sect11c_plantingw1.sav;sect11c_plantingw1.por;sect11c_... | blocked_no_raw_or_archive_file |
| 10 | sect11d_plantingw1 | geography;health_need_access;shocks;survey_design | sect11d_plantingw1;sect11d_plantingw1.*;sect11d_plantingw1.dta;sect11d_plantingw1.sav;sect11d_plantingw1.por;sect11d_... | blocked_no_raw_or_archive_file |
| 11 | sect11e_plantingw1 | geography;health_need_access;shocks;survey_design | sect11e_plantingw1;sect11e_plantingw1.*;sect11e_plantingw1.dta;sect11e_plantingw1.sav;sect11e_plantingw1.por;sect11e_... | blocked_no_raw_or_archive_file |
| 12 | sect11h_plantingw1 | geography;health_need_access;shocks;survey_design | sect11h_plantingw1;sect11h_plantingw1.*;sect11h_plantingw1.dta;sect11h_plantingw1.sav;sect11h_plantingw1.por;sect11h_... | blocked_no_raw_or_archive_file |

## First-Pass Variables To Inspect

| requirement_id | concept | candidate_files | candidate_raw_variable | metadata_confidence | first_pass_review_status |
|---|---|---|---|---|---|
| household_person_merge_keys | household_id | NGA_HouseholdGeovariables_Y1;NGA_PlotGeovariables_Y1;cons_agg_wave1_visit1;cons_agg_wave1_visit2;sect10_plantingw1;se... | hhid | high | blocked_raw_package_not_received |
| household_person_merge_keys | demographics | cons_agg_wave1_visit1;cons_agg_wave1_visit2 | edtexp | high | blocked_raw_package_not_received |
| household_person_merge_keys | demographics | cons_agg_wave1_visit1;cons_agg_wave1_visit2 | nfdinsur | high | blocked_raw_package_not_received |
| weights_and_survey_design | survey_weight | cons_agg_wave1_visit1;cons_agg_wave1_visit2 | hhweight | high | blocked_raw_package_not_received |
| weights_and_survey_design | survey_weight | sect4a_harvestw1 | s4aq52 | high | blocked_raw_package_not_received |
| weights_and_survey_design | psu_cluster | NGA_HouseholdGeovariables_Y1;NGA_PlotGeovariables_Y1;cons_agg_wave1_visit1;cons_agg_wave1_visit2;sect10_plantingw1;se... | ea | high | blocked_raw_package_not_received |
| weights_and_survey_design | psu_cluster | NGA_HouseholdGeovariables_Y1 | lat_dd_mod | high | blocked_raw_package_not_received |
| weights_and_survey_design | strata |  |  | metadata_candidate_from_concept_checklist | blocked_raw_package_not_received |
| consumption_or_income_aggregate | total_consumption_or_income | cons_agg_wave1_visit1;cons_agg_wave1_visit2 | totcons | high | blocked_raw_package_not_received |
| oop_health_expenditure | oop_health_expenditure | sect4a_harvestw1 | s4aq20 | high | blocked_raw_package_not_received |
| oop_health_expenditure | oop_health_expenditure | sect4a_harvestw1 | s4aq20b | high | blocked_raw_package_not_received |
| illness_need_care_access | health_need | sect4a_harvestw1 | s4aq3 | high | blocked_raw_package_not_received |
| illness_need_care_access | health_need | sect4a_harvestw1 | s4aq6a | high | blocked_raw_package_not_received |
| illness_need_care_access | care_or_barrier | sect4a_harvestw1 | s4aq15 | high | blocked_raw_package_not_received |
| illness_need_care_access | care_or_barrier | sect4a_harvestw1 | s4aq16 | high | blocked_raw_package_not_received |
| illness_need_care_access | insurance | sect3_plantingw1 | s3q36 | high | blocked_raw_package_not_received |
| illness_need_care_access | insurance | sect3a_harvestw1 | s3aq35 | high | blocked_raw_package_not_received |
| survey_timing | survey_timing | sectc_plantingw1 | interview_date | high | blocked_raw_package_not_received |
| geography_climate_linkage | climate_geography | NGA_HouseholdGeovariables_Y1 | lat_dd_mod | high | blocked_raw_package_not_received |
| geography_climate_linkage | climate_geography | NGA_HouseholdGeovariables_Y1 | lon_dd_mod | high | blocked_raw_package_not_received |
| missing_skip_units_recall | household_id | NGA_HouseholdGeovariables_Y1;NGA_PlotGeovariables_Y1;cons_agg_wave1_visit1;cons_agg_wave1_visit2;sect10_plantingw1;se... | hhid | high | blocked_raw_package_not_received |
| missing_skip_units_recall | survey_weight | cons_agg_wave1_visit1;cons_agg_wave1_visit2 | hhweight | high | blocked_raw_package_not_received |
| missing_skip_units_recall | survey_weight | sect4a_harvestw1 | s4aq52 | high | blocked_raw_package_not_received |
| missing_skip_units_recall | total_consumption_or_income | cons_agg_wave1_visit1;cons_agg_wave1_visit2 | totcons | high | blocked_raw_package_not_received |
| missing_skip_units_recall | oop_health_expenditure | sect4a_harvestw1 | s4aq20 | high | blocked_raw_package_not_received |
| missing_skip_units_recall | oop_health_expenditure | sect4a_harvestw1 | s4aq20b | high | blocked_raw_package_not_received |
| missing_skip_units_recall | health_need | sect4a_harvestw1 | s4aq3 | high | blocked_raw_package_not_received |
| missing_skip_units_recall | health_need | sect4a_harvestw1 | s4aq6a | high | blocked_raw_package_not_received |
| missing_skip_units_recall | care_or_barrier | sect4a_harvestw1 | s4aq15 | high | blocked_raw_package_not_received |
| missing_skip_units_recall | care_or_barrier | sect4a_harvestw1 | s4aq16 | high | blocked_raw_package_not_received |
| missing_skip_units_recall | survey_timing | sectc_plantingw1 | interview_date | high | blocked_raw_package_not_received |
| missing_skip_units_recall | climate_geography | NGA_HouseholdGeovariables_Y1 | lat_dd_mod | high | blocked_raw_package_not_received |
| missing_skip_units_recall | climate_geography | NGA_HouseholdGeovariables_Y1 | lon_dd_mod | high | blocked_raw_package_not_received |

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
