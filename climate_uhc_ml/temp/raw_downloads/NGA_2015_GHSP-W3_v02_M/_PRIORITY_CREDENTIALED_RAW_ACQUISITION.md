# Priority Credentialed Raw Acquisition Handoff

Dataset: NGA_2015_GHSP-W3_v02_M - Nigeria 2015-2016

Official get-microdata URL: https://microdata.worldbank.org/catalog/2734/get-microdata

Target folder: `temp/raw_downloads/NGA_2015_GHSP-W3_v02_M/`

Current status: ready_for_credentialed_manual_download

Required scope: download the complete unchanged official raw package and all
documentation available after the official login/register/terms workflow. Do
not download only the priority core files if the interface offers a full
package/archive.

Priority core files to confirm after download:

| core_file_rank | metadata_file_name | candidate_categories | candidate_harmonized_variables |
|---|---|---|---|
| 1 | sect11_plantingw3 | demographics;geography;survey_design | admin1_or_admin2;asset_index_or_asset_variable;hhid;psu_or_cluster_id |
| 2 | sect11b1_plantingw3 | geography;shocks;survey_design | admin1_or_admin2;agriculture_livelihood;hhid;psu_or_cluster_id |
| 3 | sect11e_plantingw3 | geography;health_need_access;shocks;survey_design | admin1_or_admin2;agriculture_livelihood;coping_borrowed;hhid;psu_or_cluster_id;reason_not_sought_distance |
| 4 | sect11f_plantingw3 | geography;shocks;survey_design | admin1_or_admin2;agriculture_livelihood;hhid;psu_or_cluster_id |
| 5 | sect1_harvestw3 | demographics;geography;health_need_access;survey_design | admin1_or_admin2;age;education;hhid;pid;psu_or_cluster_id;reason_not_sought_distance;sex |
| 6 | sect4a_harvestw3 | demographics;geography;health_expenditure;health_need_access;survey_design | admin1_or_admin2;care_sought;education;hhid;household_weight_or_person_weight;illness_or_injury_need;oop_health_expen... |
| 7 | secta1_harvestw3 | geography;shocks;survey_design | admin1_or_admin2;agriculture_livelihood;hhid;latitude_or_longitude;psu_or_cluster_id |
| 8 | secta2_harvestw3 | geography;shocks;survey_design | admin1_or_admin2;agriculture_livelihood;hhid;psu_or_cluster_id |
| 9 | secta3i_harvestw3 | geography;health_need_access;shocks;survey_design | admin1_or_admin2;agriculture_livelihood;care_not_sought_reason;hhid;psu_or_cluster_id |
| 10 | secta3ii_harvestw3 | demographics;geography;shocks;survey_design | admin1_or_admin2;agriculture_livelihood;asset_index_or_asset_variable;hhid;psu_or_cluster_id |
| 11 | secta11d_harvestw3 | geography;health_need_access;shocks;survey_design | admin1_or_admin2;agriculture_livelihood;coping_borrowed;hhid;psu_or_cluster_id;reason_not_sought_distance |
| 12 | NGA_HouseholdGeovars_Y3 | geography;health_need_access;shocks;survey_design | admin1_or_admin2;agriculture_livelihood;hhid;latitude_or_longitude;psu_or_cluster_id;reason_not_sought_distance;shock... |

After placing files here, rerun:

`python script/17_audit_raw_downloads.py; python script/128_build_priority_archive_member_preflight.py; python script/130_build_priority_raw_package_receipt_ledger.py; python script/03_inspect_raw_schemas.py; python script/29_build_raw_variable_verification_protocol.py; python script/33_build_harmonization_recipe_gate.py; python script/125_build_priority_climate_linkage_preflight.py; python script/126_build_priority_raw_verification_workbook.py; python script/129_build_priority_manual_verification_decision_gate.py; python script/127_enforce_promoted_data_gate.py; python script/36_build_direct_read_audit_bundle.py; python script/14_validate_workspace.py`
