# Priority Download Execution Packet

Dataset: `UGA_2014_SAGE-EL_v01_M` - Uganda 2014

Download order: 10

Official get-microdata URL: https://microdata.worldbank.org/catalog/2654/get-microdata

Target folder: `temp/raw_downloads/UGA_2014_SAGE-EL_v01_M/`

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
| 1 | sage_labourintermed | demographics;geography;health_need_access;shocks;survey_design | sage_labourintermed;sage_labourintermed.*;sage_labourintermed.dta;sage_labourintermed.sav;sage_labourintermed.por;sag... | blocked_no_raw_or_archive_file |
| 2 | int_operational | demographics;geography;health_expenditure;health_need_access;shocks;survey_design | int_operational;int_operational.*;int_operational.dta;int_operational.sav;int_operational.por;int_operational.sas7bda... | blocked_no_raw_or_archive_file |
| 3 | int_demographics_mem | demographics;geography;health_expenditure;health_need_access;survey_design | int_demographics_mem;int_demographics_mem.*;int_demographics_mem.dta;int_demographics_mem.sav;int_demographics_mem.po... | blocked_no_raw_or_archive_file |
| 4 | int_migration | demographics;geography;health_need_access;shocks;survey_design | int_migration;int_migration.*;int_migration.dta;int_migration.sav;int_migration.por;int_migration.sas7bdat;int_migrat... | blocked_no_raw_or_archive_file |
| 5 | int_welfare_hh | demographics;geography;health_expenditure;health_need_access;shocks;survey_design | int_welfare_hh;int_welfare_hh.*;int_welfare_hh.dta;int_welfare_hh.sav;int_welfare_hh.por;int_welfare_hh.sas7bdat;int_... | blocked_no_raw_or_archive_file |
| 6 | int_consexp | consumption;demographics;geography;health_expenditure;health_need_access;survey_design | int_consexp;int_consexp.*;int_consexp.dta;int_consexp.sav;int_consexp.por;int_consexp.sas7bdat;int_consexp.xpt;int_co... | blocked_no_raw_or_archive_file |
| 7 | int_cohesion | demographics;geography;health_need_access;shocks;survey_design | int_cohesion;int_cohesion.*;int_cohesion.dta;int_cohesion.sav;int_cohesion.por;int_cohesion.sas7bdat;int_cohesion.xpt... | blocked_no_raw_or_archive_file |
| 8 | int_access_educ18plus | demographics;geography;health_expenditure;health_need_access;shocks;survey_design | int_access_educ18plus;int_access_educ18plus.*;int_access_educ18plus.dta;int_access_educ18plus.sav;int_access_educ18pl... | blocked_no_raw_or_archive_file |
| 9 | int_access_fin | demographics;geography;health_expenditure;health_need_access;shocks;survey_design | int_access_fin;int_access_fin.*;int_access_fin.dta;int_access_fin.sav;int_access_fin.por;int_access_fin.sas7bdat;int_... | blocked_no_raw_or_archive_file |
| 10 | int_access_health | demographics;geography;health_expenditure;health_need_access;survey_design | int_access_health;int_access_health.*;int_access_health.dta;int_access_health.sav;int_access_health.por;int_access_he... | blocked_no_raw_or_archive_file |
| 11 | int_access_school | demographics;geography;health_expenditure;health_need_access;shocks;survey_design | int_access_school;int_access_school.*;int_access_school.dta;int_access_school.sav;int_access_school.por;int_access_sc... | blocked_no_raw_or_archive_file |
| 12 | int_community | demographics;geography;health_need_access;shocks | int_community;int_community.*;int_community.dta;int_community.sav;int_community.por;int_community.sas7bdat;int_commun... | blocked_no_raw_or_archive_file |

## First-Pass Variables To Inspect

| requirement_id | concept | candidate_files | candidate_raw_variable | metadata_confidence | first_pass_review_status |
|---|---|---|---|---|---|
| household_person_merge_keys | household_id | SAGE_HHWEIGHTSV2;int_access_educ18plus;int_access_fin;int_access_health;int_access_health_hh;int_access_school;int_as... | hhid | high | blocked_raw_package_not_received |
| household_person_merge_keys | demographics | int_access_educ18plus | attended_school | high | blocked_raw_package_not_received |
| household_person_merge_keys | demographics | int_access_educ18plus | attended_school_female | high | blocked_raw_package_not_received |
| weights_and_survey_design | survey_weight | SAGE_HHWEIGHTSV2;int_access_educ18plus;int_access_fin;int_access_health;int_access_health_hh;int_access_school;int_as... | weightfinal2 | high | blocked_raw_package_not_received |
| weights_and_survey_design | survey_weight | int_consexp | hmult | high | blocked_raw_package_not_received |
| weights_and_survey_design | psu_cluster |  |  | metadata_candidate_from_concept_checklist | blocked_raw_package_not_received |
| weights_and_survey_design | strata |  |  | metadata_candidate_from_concept_checklist | blocked_raw_package_not_received |
| consumption_or_income_aggregate | total_consumption_or_income | int_consexp | cpexp30_pae | moderate | blocked_raw_package_not_received |
| consumption_or_income_aggregate | total_consumption_or_income | int_consexp | nrexp30 | moderate | blocked_raw_package_not_received |
| oop_health_expenditure | oop_health_expenditure | int_access_educ18plus;int_access_health;int_access_school;int_demographics_mem;int_welfare_memdata | hh3_q8 | high | blocked_raw_package_not_received |
| oop_health_expenditure | oop_health_expenditure | int_access_fin | credit_item_10 | high | blocked_raw_package_not_received |
| illness_need_care_access | health_need | int_access_educ18plus;int_access_health;int_access_school;int_demographics_mem;int_welfare_memdata | hh3_q1 | high | blocked_raw_package_not_received |
| illness_need_care_access | health_need | int_access_educ18plus;int_access_health;int_access_school;int_demographics_mem;int_welfare_memdata | hh3_q4 | high | blocked_raw_package_not_received |
| illness_need_care_access | care_or_barrier | int_access_educ18plus;int_access_fin;int_access_health;int_access_health_hh;int_access_school;int_asset_index;int_ben... | eligilitystatus | high | blocked_raw_package_not_received |
| illness_need_care_access | care_or_barrier | int_access_educ18plus;int_access_health;int_access_school;int_demographics_mem;int_welfare_memdata | hh3_q8 | high | blocked_raw_package_not_received |
| illness_need_care_access | insurance |  |  | metadata_candidate_from_concept_checklist | blocked_raw_package_not_received |
| survey_timing | survey_timing | int_access_fin;int_cohesion;int_welfare_hh;sage_labourintermed | doi | high | blocked_raw_package_not_received |
| survey_timing | survey_timing | int_access_fin;int_cohesion;int_welfare_hh;sage_labourintermed | intdate | high | blocked_raw_package_not_received |
| geography_climate_linkage | climate_geography | SAGE_HHWEIGHTSV2;int_access_educ18plus;int_access_fin;int_access_health;int_access_health_hh;int_access_school;int_as... | county | high | blocked_raw_package_not_received |
| geography_climate_linkage | climate_geography | SAGE_HHWEIGHTSV2;int_access_educ18plus;int_access_fin;int_access_health;int_access_health_hh;int_access_school;int_as... | district | high | blocked_raw_package_not_received |
| missing_skip_units_recall | household_id | SAGE_HHWEIGHTSV2;int_access_educ18plus;int_access_fin;int_access_health;int_access_health_hh;int_access_school;int_as... | hhid | high | blocked_raw_package_not_received |
| missing_skip_units_recall | survey_weight | SAGE_HHWEIGHTSV2;int_access_educ18plus;int_access_fin;int_access_health;int_access_health_hh;int_access_school;int_as... | weightfinal2 | high | blocked_raw_package_not_received |
| missing_skip_units_recall | survey_weight | int_consexp | hmult | high | blocked_raw_package_not_received |
| missing_skip_units_recall | total_consumption_or_income | int_consexp | cpexp30_pae | moderate | blocked_raw_package_not_received |
| missing_skip_units_recall | total_consumption_or_income | int_consexp | nrexp30 | moderate | blocked_raw_package_not_received |
| missing_skip_units_recall | oop_health_expenditure | int_access_educ18plus;int_access_health;int_access_school;int_demographics_mem;int_welfare_memdata | hh3_q8 | high | blocked_raw_package_not_received |
| missing_skip_units_recall | oop_health_expenditure | int_access_fin | credit_item_10 | high | blocked_raw_package_not_received |
| missing_skip_units_recall | health_need | int_access_educ18plus;int_access_health;int_access_school;int_demographics_mem;int_welfare_memdata | hh3_q1 | high | blocked_raw_package_not_received |
| missing_skip_units_recall | health_need | int_access_educ18plus;int_access_health;int_access_school;int_demographics_mem;int_welfare_memdata | hh3_q4 | high | blocked_raw_package_not_received |
| missing_skip_units_recall | care_or_barrier | int_access_educ18plus;int_access_fin;int_access_health;int_access_health_hh;int_access_school;int_asset_index;int_ben... | eligilitystatus | high | blocked_raw_package_not_received |
| missing_skip_units_recall | care_or_barrier | int_access_educ18plus;int_access_health;int_access_school;int_demographics_mem;int_welfare_memdata | hh3_q8 | high | blocked_raw_package_not_received |
| missing_skip_units_recall | survey_timing | int_access_fin;int_cohesion;int_welfare_hh;sage_labourintermed | doi | high | blocked_raw_package_not_received |
| missing_skip_units_recall | survey_timing | int_access_fin;int_cohesion;int_welfare_hh;sage_labourintermed | intdate | high | blocked_raw_package_not_received |
| missing_skip_units_recall | climate_geography | SAGE_HHWEIGHTSV2;int_access_educ18plus;int_access_fin;int_access_health;int_access_health_hh;int_access_school;int_as... | county | high | blocked_raw_package_not_received |
| missing_skip_units_recall | climate_geography | SAGE_HHWEIGHTSV2;int_access_educ18plus;int_access_fin;int_access_health;int_access_health_hh;int_access_school;int_as... | district | high | blocked_raw_package_not_received |

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
