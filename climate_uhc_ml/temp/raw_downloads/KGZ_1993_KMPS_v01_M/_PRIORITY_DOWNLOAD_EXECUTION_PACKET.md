# Priority Download Execution Packet

Dataset: `KGZ_1993_KMPS_v01_M` - Kyrgyz Republic 1993

Download order: 12

Official get-microdata URL: https://microdata.worldbank.org/catalog/280/get-microdata

Target folder: `temp/raw_downloads/KGZ_1993_KMPS_v01_M/`

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
| 1 | CONADULT | demographics;survey_design | CONADULT;CONADULT.*;CONADULT.dta;CONADULT.sav;CONADULT.por;CONADULT.sas7bdat;CONADULT.xpt;CONADULT.csv;*CONADULT* | blocked_no_raw_or_archive_file |
| 2 | CORE | geography;survey_design | CORE;CORE.*;CORE.dta;CORE.sav;CORE.por;CORE.sas7bdat;CORE.xpt;CORE.csv;*CORE* | blocked_no_raw_or_archive_file |
| 3 | INCEXP | consumption;demographics;geography;health_need_access;shocks;survey_design | INCEXP;INCEXP.*;INCEXP.dta;INCEXP.sav;INCEXP.por;INCEXP.sas7bdat;INCEXP.xpt;INCEXP.csv;*INCEXP* | blocked_no_raw_or_archive_file |
| 4 | KADULT | consumption;demographics;geography;health_expenditure;health_need_access;shocks;survey_design | KADULT;KADULT.*;KADULT.dta;KADULT.sav;KADULT.por;KADULT.sas7bdat;KADULT.xpt;KADULT.csv;*KADULT* | blocked_no_raw_or_archive_file |
| 5 | KCHILD | demographics;health_expenditure;health_need_access;shocks;survey_design | KCHILD;KCHILD.*;KCHILD.dta;KCHILD.sav;KCHILD.por;KCHILD.sas7bdat;KCHILD.xpt;KCHILD.csv;*KCHILD* | blocked_no_raw_or_archive_file |
| 6 | KCOMM | demographics;geography;health_need_access;shocks | KCOMM;KCOMM.*;KCOMM.dta;KCOMM.sav;KCOMM.por;KCOMM.sas7bdat;KCOMM.xpt;KCOMM.csv;*KCOMM* | blocked_no_raw_or_archive_file |
| 7 | KHHLD | demographics;geography;health_expenditure;health_need_access;shocks;survey_design | KHHLD;KHHLD.*;KHHLD.dta;KHHLD.sav;KHHLD.por;KHHLD.sas7bdat;KHHLD.xpt;KHHLD.csv;*KHHLD* | blocked_no_raw_or_archive_file |
| 8 | KINDIV | demographics;survey_design | KINDIV;KINDIV.*;KINDIV.dta;KINDIV.sav;KINDIV.por;KINDIV.sas7bdat;KINDIV.xpt;KINDIV.csv;*KINDIV* | blocked_no_raw_or_archive_file |
| 9 | KINDIVH | demographics;survey_design | KINDIVH;KINDIVH.*;KINDIVH.dta;KINDIVH.sav;KINDIVH.por;KINDIVH.sas7bdat;KINDIVH.xpt;KINDIVH.csv;*KINDIVH* | blocked_no_raw_or_archive_file |
| 10 | KPRICE2 | geography;shocks | KPRICE2;KPRICE2.*;KPRICE2.dta;KPRICE2.sav;KPRICE2.por;KPRICE2.sas7bdat;KPRICE2.xpt;KPRICE2.csv;*KPRICE2* | blocked_no_raw_or_archive_file |
| 11 | KPRICE3 | geography;shocks | KPRICE3;KPRICE3.*;KPRICE3.dta;KPRICE3.sav;KPRICE3.por;KPRICE3.sas7bdat;KPRICE3.xpt;KPRICE3.csv;*KPRICE3* | blocked_no_raw_or_archive_file |
| 12 | KYGPOV | geography;survey_design | KYGPOV;KYGPOV.*;KYGPOV.dta;KYGPOV.sav;KYGPOV.por;KYGPOV.sas7bdat;KYGPOV.xpt;KYGPOV.csv;*KYGPOV* | blocked_no_raw_or_archive_file |

## First-Pass Variables To Inspect

| requirement_id | concept | candidate_files | candidate_raw_variable | metadata_confidence | first_pass_review_status |
|---|---|---|---|---|---|
| household_person_merge_keys | household_id | CONADULT;CORE;KADIET;KADULT;KCHDIET;KCHILD;KHHLD;KINDIV;KINDIVH;KYGPOV | hid | high | blocked_raw_package_not_received |
| household_person_merge_keys | household_id | INCEXP | khid | high | blocked_raw_package_not_received |
| household_person_merge_keys | demographics | CONADULT;KINDIV | age | high | blocked_raw_package_not_received |
| household_person_merge_keys | demographics | CONADULT | edlevel | high | blocked_raw_package_not_received |
| weights_and_survey_design | survey_weight | KADULT;KCHILD | a1m1 | high | blocked_raw_package_not_received |
| weights_and_survey_design | survey_weight | KADULT;KCHILD | a1m37_2 | high | blocked_raw_package_not_received |
| weights_and_survey_design | psu_cluster |  |  | metadata_candidate_from_concept_checklist | blocked_raw_package_not_received |
| weights_and_survey_design | strata |  |  | metadata_candidate_from_concept_checklist | blocked_raw_package_not_received |
| consumption_or_income_aggregate | total_consumption_or_income | INCEXP | khomcx | moderate | blocked_raw_package_not_received |
| oop_health_expenditure | oop_health_expenditure | KADULT;KCHILD | a1l15 | high | blocked_raw_package_not_received |
| oop_health_expenditure | oop_health_expenditure | KADULT;KCHILD | a1l16 | high | blocked_raw_package_not_received |
| illness_need_care_access | health_need | KADULT;KCHILD | a1l24 | high | blocked_raw_package_not_received |
| illness_need_care_access | health_need | KHHLD | af14_4a | high | blocked_raw_package_not_received |
| illness_need_care_access | care_or_barrier | KADULT;KCHILD | a1l15 | high | blocked_raw_package_not_received |
| illness_need_care_access | care_or_barrier | KADULT;KCHILD | a1l16 | high | blocked_raw_package_not_received |
| illness_need_care_access | insurance |  |  | metadata_candidate_from_concept_checklist | blocked_raw_package_not_received |
| survey_timing | survey_timing | CORE | month | high | blocked_raw_package_not_received |
| survey_timing | survey_timing | KADULT;KCHILD | a1h7_2 | high | blocked_raw_package_not_received |
| geography_climate_linkage | climate_geography | CORE | region | high | blocked_raw_package_not_received |
| geography_climate_linkage | climate_geography | KCOMM | a1x3 | moderate | blocked_raw_package_not_received |
| missing_skip_units_recall | household_id | CONADULT;CORE;KADIET;KADULT;KCHDIET;KCHILD;KHHLD;KINDIV;KINDIVH;KYGPOV | hid | high | blocked_raw_package_not_received |
| missing_skip_units_recall | household_id | INCEXP | khid | high | blocked_raw_package_not_received |
| missing_skip_units_recall | survey_weight | KADULT;KCHILD | a1m1 | high | blocked_raw_package_not_received |
| missing_skip_units_recall | survey_weight | KADULT;KCHILD | a1m37_2 | high | blocked_raw_package_not_received |
| missing_skip_units_recall | total_consumption_or_income | INCEXP | khomcx | moderate | blocked_raw_package_not_received |
| missing_skip_units_recall | oop_health_expenditure | KADULT;KCHILD | a1l15 | high | blocked_raw_package_not_received |
| missing_skip_units_recall | oop_health_expenditure | KADULT;KCHILD | a1l16 | high | blocked_raw_package_not_received |
| missing_skip_units_recall | health_need | KADULT;KCHILD | a1l24 | high | blocked_raw_package_not_received |
| missing_skip_units_recall | health_need | KHHLD | af14_4a | high | blocked_raw_package_not_received |
| missing_skip_units_recall | care_or_barrier | KADULT;KCHILD | a1l15 | high | blocked_raw_package_not_received |
| missing_skip_units_recall | care_or_barrier | KADULT;KCHILD | a1l16 | high | blocked_raw_package_not_received |
| missing_skip_units_recall | survey_timing | CORE | month | high | blocked_raw_package_not_received |
| missing_skip_units_recall | survey_timing | KADULT;KCHILD | a1h7_2 | high | blocked_raw_package_not_received |
| missing_skip_units_recall | climate_geography | CORE | region | high | blocked_raw_package_not_received |
| missing_skip_units_recall | climate_geography | KCOMM | a1x3 | moderate | blocked_raw_package_not_received |

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
