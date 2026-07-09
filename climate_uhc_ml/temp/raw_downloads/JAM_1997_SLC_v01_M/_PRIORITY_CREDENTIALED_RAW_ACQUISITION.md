# Priority Credentialed Raw Acquisition Handoff

Dataset: JAM_1997_SLC_v01_M - Jamaica 1997

Official get-microdata URL: https://microdata.worldbank.org/catalog/2368/get-microdata

Target folder: `temp/raw_downloads/JAM_1997_SLC_v01_M/`

Current status: ready_for_credentialed_manual_download

Required scope: download the complete unchanged official raw package and all
documentation available after the official login/register/terms workflow. Do
not download only the priority core files if the interface offers a full
package/archive.

Priority core files to confirm after download:

| core_file_rank | metadata_file_name | candidate_categories | candidate_harmonized_variables |
|---|---|---|---|
| 1 | REC001 | demographics;geography;survey_design | admin1_or_admin2;asset_index_or_asset_variable;household_weight_or_person_weight;interview_date_or_survey_month |
| 2 | REC003 | health_expenditure;health_need_access | care_sought;health_insurance;illness_or_injury_need;oop_health_expenditure |
| 3 | REC006 | geography;health_need_access | admin1_or_admin2;reason_not_sought_distance |
| 4 | REC007 | demographics;survey_design | age;household_weight_or_person_weight |
| 5 | REC025 | consumption | nonfood_consumption |
| 6 | ANNUAL | consumption;demographics;geography;survey_design | admin1_or_admin2;asset_index_or_asset_variable;food_consumption;household_size;household_weight_or_person_weight;nonf... |
| 7 | EDTOTALS | consumption;demographics;geography;survey_design | admin1_or_admin2;asset_index_or_asset_variable;food_consumption;household_weight_or_person_weight;nonfood_consumption... |
| 8 | EXP97 | consumption;geography;survey_design | admin1_or_admin2;food_consumption;psu_or_cluster_id |
| 9 | HEADS | demographics;geography;survey_design | admin1_or_admin2;age;household_head_marker;pid;sex |
| 10 | HHSIZE | demographics;geography | admin1_or_admin2;age;asset_index_or_asset_variable;household_size;sex |
| 11 | LABORF | demographics;geography;health_need_access;shocks;survey_design | admin1_or_admin2;age;asset_index_or_asset_variable;care_not_sought_reason;education;pid;sex;shock_module_variable |
| 12 | NUTR97 | demographics;survey_design | age;household_weight_or_person_weight;sex |

After placing files here, rerun:

`python script/17_audit_raw_downloads.py; python script/128_build_priority_archive_member_preflight.py; python script/130_build_priority_raw_package_receipt_ledger.py; python script/03_inspect_raw_schemas.py; python script/29_build_raw_variable_verification_protocol.py; python script/33_build_harmonization_recipe_gate.py; python script/125_build_priority_climate_linkage_preflight.py; python script/126_build_priority_raw_verification_workbook.py; python script/129_build_priority_manual_verification_decision_gate.py; python script/127_enforce_promoted_data_gate.py; python script/36_build_direct_read_audit_bundle.py; python script/14_validate_workspace.py`
