# Priority Download Execution Packet

Dataset: `MWI_2007-2009_MTM_v01_M` - Malawi 2007-2009

Download order: 3

Official get-microdata URL: https://microdata.worldbank.org/catalog/3462/get-microdata

Target folder: `temp/raw_downloads/MWI_2007-2009_MTM_v01_M/`

Current status: `ready_for_manual_credentialed_download_no_raw_receipt`

Raw receipt: `not_received_no_original_raw_package`

## Manual Download Scope

Download the complete unchanged official raw package plus all documentation
through the permitted World Bank account, terms, or Data Access Agreement
workflow. Do not assemble an incomplete analysis package from only the listed
core files.

## Minimum Acceptance Rule

Complete official package must be present; at least 12 priority core files/modules must be found directly or inside the official archive; all 8 promotion requirements and 38 selected first-pass variables must remain raw-backed before any data/ write.

## Core Files To Confirm

| core_file_rank | metadata_file_name | candidate_categories | expected_local_name_patterns | file_acceptance_status |
|---|---|---|---|---|
| 1 | hh2_cmty | demographics;geography;health_need_access;shocks | hh2_cmty;hh2_cmty.*;hh2_cmty.dta;hh2_cmty.sav;hh2_cmty.por;hh2_cmty.sas7bdat;hh2_cmty.xpt;hh2_cmty.csv;*hh2_cmty* | blocked_no_raw_or_archive_file |
| 2 | hh2p2_s10 | demographics;geography;health_need_access;shocks;survey_design | hh2p2_s10;hh2p2_s10.*;hh2p2_s10.dta;hh2p2_s10.sav;hh2p2_s10.por;hh2p2_s10.sas7bdat;hh2p2_s10.xpt;hh2p2_s10.csv;*hh2p2... | blocked_no_raw_or_archive_file |
| 3 | hh2p2_s12 | demographics;geography;shocks;survey_design | hh2p2_s12;hh2p2_s12.*;hh2p2_s12.dta;hh2p2_s12.sav;hh2p2_s12.por;hh2p2_s12.sas7bdat;hh2p2_s12.xpt;hh2p2_s12.csv;*hh2p2... | blocked_no_raw_or_archive_file |
| 4 | hh2p3_s15 | demographics;geography;survey_design | hh2p3_s15;hh2p3_s15.*;hh2p3_s15.dta;hh2p3_s15.sav;hh2p3_s15.por;hh2p3_s15.sas7bdat;hh2p3_s15.xpt;hh2p3_s15.csv;*hh2p3... | blocked_no_raw_or_archive_file |
| 5 | hh2p3_s17 | demographics;health_expenditure;health_need_access;shocks;survey_design | hh2p3_s17;hh2p3_s17.*;hh2p3_s17.dta;hh2p3_s17.sav;hh2p3_s17.por;hh2p3_s17.sas7bdat;hh2p3_s17.xpt;hh2p3_s17.csv;*hh2p3... | blocked_no_raw_or_archive_file |
| 6 | hh3p3_s15 | demographics;geography;health_need_access;shocks;survey_design | hh3p3_s15;hh3p3_s15.*;hh3p3_s15.dta;hh3p3_s15.sav;hh3p3_s15.por;hh3p3_s15.sas7bdat;hh3p3_s15.xpt;hh3p3_s15.csv;*hh3p3... | blocked_no_raw_or_archive_file |
| 7 | p2_s9 | demographics;geography;survey_design | p2_s9;p2_s9.*;p2_s9.dta;p2_s9.sav;p2_s9.por;p2_s9.sas7bdat;p2_s9.xpt;p2_s9.csv;*p2_s9* | blocked_no_raw_or_archive_file |
| 8 | p2_s10 | demographics;health_expenditure;health_need_access;shocks;survey_design | p2_s10;p2_s10.*;p2_s10.dta;p2_s10.sav;p2_s10.por;p2_s10.sas7bdat;p2_s10.xpt;p2_s10.csv;*p2_s10* | blocked_no_raw_or_archive_file |
| 9 | p2_s11 | demographics;health_expenditure;health_need_access;shocks;survey_design | p2_s11;p2_s11.*;p2_s11.dta;p2_s11.sav;p2_s11.por;p2_s11.sas7bdat;p2_s11.xpt;p2_s11.csv;*p2_s11* | blocked_no_raw_or_archive_file |
| 10 | p2_s13 | demographics;geography;health_need_access;survey_design | p2_s13;p2_s13.*;p2_s13.dta;p2_s13.sav;p2_s13.por;p2_s13.sas7bdat;p2_s13.xpt;p2_s13.csv;*p2_s13* | blocked_no_raw_or_archive_file |
| 11 | p2_s14a | demographics;health_need_access;survey_design | p2_s14a;p2_s14a.*;p2_s14a.dta;p2_s14a.sav;p2_s14a.por;p2_s14a.sas7bdat;p2_s14a.xpt;p2_s14a.csv;*p2_s14a* | blocked_no_raw_or_archive_file |
| 12 | pi_s5a | demographics;health_need_access;survey_design | pi_s5a;pi_s5a.*;pi_s5a.dta;pi_s5a.sav;pi_s5a.por;pi_s5a.sas7bdat;pi_s5a.xpt;pi_s5a.csv;*pi_s5a* | blocked_no_raw_or_archive_file |

## First-Pass Variables To Inspect

| requirement_id | concept | candidate_files | candidate_raw_variable | metadata_confidence | first_pass_review_status |
|---|---|---|---|---|---|
| household_person_merge_keys | household_id | hh2p1_cs;hh2p1_s1;hh2p1_s2;hh2p1_s3;hh2p1_s4;hh2p1_s5;hh2p1_s6;hh2p1_s7;hh2p1_s8;hh2p2_cs;hh2p2_s10;hh2p2_s11;hh2p2_s... | hhid | high | blocked_raw_package_not_received |
| household_person_merge_keys | household_id | p1_cs;p1_s1;p1_s2;p1_s3;p1_s4;p1_s5;p1_s6;p1_s7;p1_s8;p2_cs;p2_s10;p2_s11;p2_s12;p2_s13;p2_s14;p2_s14a;p2_s15;p2_s9;p... | ea | high | blocked_raw_package_not_received |
| household_person_merge_keys | demographics | hh2_cmty;hh3_cmty | caq14 | high | blocked_raw_package_not_received |
| household_person_merge_keys | demographics | hh2_cmty;hh3_cmty | caq16_l | high | blocked_raw_package_not_received |
| weights_and_survey_design | survey_weight | hh2_mortality;pi_mortality | mq18 | high | blocked_raw_package_not_received |
| weights_and_survey_design | survey_weight | hh2_mortality;pi_mortality | mq19 | high | blocked_raw_package_not_received |
| weights_and_survey_design | psu_cluster | hh2_mkts_location;mkts_location | q7_1 | high | blocked_raw_package_not_received |
| weights_and_survey_design | psu_cluster | hh2_mkts_location;mkts_location | q7_10 | high | blocked_raw_package_not_received |
| weights_and_survey_design | strata |  |  | metadata_candidate_from_concept_checklist | blocked_raw_package_not_received |
| consumption_or_income_aggregate | total_consumption_or_income | hh2p1_s4;p1_s4 | s4q03 | high | blocked_raw_package_not_received |
| consumption_or_income_aggregate | total_consumption_or_income | hh2p1_s4;p1_s4 | s4q03u | high | blocked_raw_package_not_received |
| oop_health_expenditure | oop_health_expenditure | hh2p2_s9 | s9q22b | high | blocked_raw_package_not_received |
| oop_health_expenditure | oop_health_expenditure | hh2p3_s16 | s16q35b | high | blocked_raw_package_not_received |
| illness_need_care_access | health_need | hh2_mortality;pi_mortality | mq04 | high | blocked_raw_package_not_received |
| illness_need_care_access | health_need | hh2_mortality;pi_mortality | mq06_1 | high | blocked_raw_package_not_received |
| illness_need_care_access | care_or_barrier | hh2_cmty | ccq42_n | high | blocked_raw_package_not_received |
| illness_need_care_access | care_or_barrier | hh2_cmty | ccq42_u | high | blocked_raw_package_not_received |
| illness_need_care_access | insurance |  |  | metadata_candidate_from_concept_checklist | blocked_raw_package_not_received |
| survey_timing | survey_timing | hh2_mortality | mq25c | high | blocked_raw_package_not_received |
| survey_timing | survey_timing | hh2_tf | tfq6_c1 | high | blocked_raw_package_not_received |
| geography_climate_linkage | climate_geography | hh2_mkts_hlthfac | cq5e1 | high | blocked_raw_package_not_received |
| geography_climate_linkage | climate_geography | hh2_mkts_hlthfac | cq5e2 | high | blocked_raw_package_not_received |
| missing_skip_units_recall | household_id | hh2p1_cs;hh2p1_s1;hh2p1_s2;hh2p1_s3;hh2p1_s4;hh2p1_s5;hh2p1_s6;hh2p1_s7;hh2p1_s8;hh2p2_cs;hh2p2_s10;hh2p2_s11;hh2p2_s... | hhid | high | blocked_raw_package_not_received |
| missing_skip_units_recall | household_id | p1_cs;p1_s1;p1_s2;p1_s3;p1_s4;p1_s5;p1_s6;p1_s7;p1_s8;p2_cs;p2_s10;p2_s11;p2_s12;p2_s13;p2_s14;p2_s14a;p2_s15;p2_s9;p... | ea | high | blocked_raw_package_not_received |
| missing_skip_units_recall | survey_weight | hh2_mortality;pi_mortality | mq18 | high | blocked_raw_package_not_received |
| missing_skip_units_recall | survey_weight | hh2_mortality;pi_mortality | mq19 | high | blocked_raw_package_not_received |
| missing_skip_units_recall | total_consumption_or_income | hh2p1_s4;p1_s4 | s4q03 | high | blocked_raw_package_not_received |
| missing_skip_units_recall | total_consumption_or_income | hh2p1_s4;p1_s4 | s4q03u | high | blocked_raw_package_not_received |
| missing_skip_units_recall | oop_health_expenditure | hh2p2_s9 | s9q22b | high | blocked_raw_package_not_received |
| missing_skip_units_recall | oop_health_expenditure | hh2p3_s16 | s16q35b | high | blocked_raw_package_not_received |
| missing_skip_units_recall | health_need | hh2_mortality;pi_mortality | mq04 | high | blocked_raw_package_not_received |
| missing_skip_units_recall | health_need | hh2_mortality;pi_mortality | mq06_1 | high | blocked_raw_package_not_received |
| missing_skip_units_recall | care_or_barrier | hh2_cmty | ccq42_n | high | blocked_raw_package_not_received |
| missing_skip_units_recall | care_or_barrier | hh2_cmty | ccq42_u | high | blocked_raw_package_not_received |
| missing_skip_units_recall | survey_timing | hh2_mortality | mq25c | high | blocked_raw_package_not_received |
| missing_skip_units_recall | survey_timing | hh2_tf | tfq6_c1 | high | blocked_raw_package_not_received |
| missing_skip_units_recall | climate_geography | hh2_mkts_hlthfac | cq5e1 | high | blocked_raw_package_not_received |
| missing_skip_units_recall | climate_geography | hh2_mkts_hlthfac | cq5e2 | high | blocked_raw_package_not_received |

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
