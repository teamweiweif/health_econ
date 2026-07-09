# Priority Credentialed Raw Acquisition Handoff

Dataset: NGA_2010_GHSP-W1_v03_M - Nigeria 2010-2011

Official get-microdata URL: https://microdata.worldbank.org/catalog/1002/get-microdata

Target folder: `temp/raw_downloads/NGA_2010_GHSP-W1_v03_M/`

Current status: ready_for_credentialed_manual_download

Required scope: download the complete unchanged official raw package and all
documentation available after the official login/register/terms workflow. Do
not download only the priority core files if the interface offers a full
package/archive.

Priority core files to confirm after download:

| core_file_rank | metadata_file_name | candidate_categories | candidate_harmonized_variables |
|---|---|---|---|
| 1 | NGA_HouseholdGeovariables_Y1 | geography;health_need_access;shocks;survey_design | admin1_or_admin2;agriculture_livelihood;hhid;latitude_or_longitude;psu_or_cluster_id;reason_not_sought_distance;shock... |
| 2 | secta1_harvestw1 | geography;shocks;survey_design | admin1_or_admin2;agriculture_livelihood;hhid;latitude_or_longitude;psu_or_cluster_id |
| 3 | secta2_harvestw1 | geography;shocks;survey_design | admin1_or_admin2;agriculture_livelihood;hhid;psu_or_cluster_id |
| 4 | secta3_harvestw1 | geography;health_need_access;shocks;survey_design | admin1_or_admin2;agriculture_livelihood;care_not_sought_reason;hhid;psu_or_cluster_id |
| 5 | sect1_harvestw1 | demographics;geography;health_need_access;survey_design | admin1_or_admin2;age;education;hhid;psu_or_cluster_id;reason_not_sought_distance;sex |
| 6 | sect4a_harvestw1 | demographics;geography;health_expenditure;health_need_access;survey_design | admin1_or_admin2;care_sought;education;hhid;household_weight_or_person_weight;illness_or_injury_need;oop_health_expen... |
| 7 | sect8_harvestw1 | demographics;geography;survey_design | admin1_or_admin2;asset_index_or_asset_variable;hhid;psu_or_cluster_id |
| 8 | sect11b_plantingw1 | geography;shocks;survey_design | admin1_or_admin2;agriculture_livelihood;hhid;pid;psu_or_cluster_id |
| 9 | sect11c_plantingw1 | geography;shocks;survey_design | admin1_or_admin2;agriculture_livelihood;hhid;psu_or_cluster_id |
| 10 | sect11d_plantingw1 | geography;health_need_access;shocks;survey_design | admin1_or_admin2;agriculture_livelihood;coping_borrowed;hhid;psu_or_cluster_id;reason_not_sought_distance |
| 11 | sect11e_plantingw1 | geography;health_need_access;shocks;survey_design | admin1_or_admin2;agriculture_livelihood;coping_borrowed;hhid;psu_or_cluster_id;reason_not_sought_distance |
| 12 | sect11h_plantingw1 | geography;health_need_access;shocks;survey_design | admin1_or_admin2;agriculture_livelihood;coping_borrowed;hhid;psu_or_cluster_id;reason_not_sought_distance |

After placing files here, rerun:

`python script/17_audit_raw_downloads.py; python script/128_build_priority_archive_member_preflight.py; python script/130_build_priority_raw_package_receipt_ledger.py; python script/03_inspect_raw_schemas.py; python script/29_build_raw_variable_verification_protocol.py; python script/33_build_harmonization_recipe_gate.py; python script/125_build_priority_climate_linkage_preflight.py; python script/126_build_priority_raw_verification_workbook.py; python script/140_build_priority_first_pass_variable_review_queue.py; python script/141_build_priority_download_execution_packet.py; python script/129_build_priority_manual_verification_decision_gate.py; python script/127_enforce_promoted_data_gate.py; python script/36_build_direct_read_audit_bundle.py; python script/14_validate_workspace.py`
