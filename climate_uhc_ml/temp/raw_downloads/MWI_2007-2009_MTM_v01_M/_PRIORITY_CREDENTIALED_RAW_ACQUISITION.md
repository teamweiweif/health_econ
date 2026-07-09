# Priority Credentialed Raw Acquisition Handoff

Dataset: MWI_2007-2009_MTM_v01_M - Malawi 2007-2009

Official get-microdata URL: https://microdata.worldbank.org/catalog/3462/get-microdata

Target folder: `temp/raw_downloads/MWI_2007-2009_MTM_v01_M/`

Current status: ready_for_credentialed_manual_download

Required scope: download the complete unchanged official raw package and all
documentation available after the official login/register/terms workflow. Do
not download only the priority core files if the interface offers a full
package/archive.

Priority core files to confirm after download:

| core_file_rank | metadata_file_name | candidate_categories | candidate_harmonized_variables |
|---|---|---|---|
| 1 | hh2_cmty | demographics;geography;health_need_access;shocks | admin1_or_admin2;age;agriculture_livelihood;asset_index_or_asset_variable;care_sought;coping_borrowed;education;healt... |
| 2 | hh2p2_s10 | demographics;geography;health_need_access;shocks;survey_design | admin1_or_admin2;age;agriculture_livelihood;asset_index_or_asset_variable;coping_borrowed;hhid;illness_or_injury_need... |
| 3 | hh2p2_s12 | demographics;geography;shocks;survey_design | admin1_or_admin2;age;agriculture_livelihood;asset_index_or_asset_variable;education;hhid;pid;psu_or_cluster_id;sex |
| 4 | hh2p3_s15 | demographics;geography;survey_design | admin1_or_admin2;age;education;hhid;pid;psu_or_cluster_id;sex |
| 5 | hh2p3_s17 | demographics;health_expenditure;health_need_access;shocks;survey_design | age;asset_index_or_asset_variable;hhid;illness_or_injury_need;oop_health_expenditure;pid;shock_module_variable |
| 6 | hh3p3_s15 | demographics;geography;health_need_access;shocks;survey_design | admin1_or_admin2;age;agriculture_livelihood;coping_borrowed;education;hhid;pid;psu_or_cluster_id;reason_not_sought_di... |
| 7 | p2_s9 | demographics;geography;survey_design | admin1_or_admin2;age;education;hhid;pid;psu_or_cluster_id;sex |
| 8 | p2_s10 | demographics;health_expenditure;health_need_access;shocks;survey_design | age;agriculture_livelihood;asset_index_or_asset_variable;coping_borrowed;education;hhid;illness_or_injury_need;oop_he... |
| 9 | p2_s11 | demographics;health_expenditure;health_need_access;shocks;survey_design | age;asset_index_or_asset_variable;hhid;illness_or_injury_need;oop_health_expenditure;pid;psu_or_cluster_id;sex;shock_... |
| 10 | p2_s13 | demographics;geography;health_need_access;survey_design | admin1_or_admin2;age;asset_index_or_asset_variable;education;hhid;pid;psu_or_cluster_id;reason_not_sought_cost;sex |
| 11 | p2_s14a | demographics;health_need_access;survey_design | age;education;hhid;pid;psu_or_cluster_id;reason_not_sought_cost;reason_not_sought_distance;sex |
| 12 | pi_s5a | demographics;health_need_access;survey_design | care_not_sought_reason;education;hhid;pid;reason_not_sought_cost;reason_not_sought_distance;sex |

After placing files here, rerun:

`python script/17_audit_raw_downloads.py; python script/128_build_priority_archive_member_preflight.py; python script/130_build_priority_raw_package_receipt_ledger.py; python script/03_inspect_raw_schemas.py; python script/29_build_raw_variable_verification_protocol.py; python script/33_build_harmonization_recipe_gate.py; python script/125_build_priority_climate_linkage_preflight.py; python script/126_build_priority_raw_verification_workbook.py; python script/129_build_priority_manual_verification_decision_gate.py; python script/127_enforce_promoted_data_gate.py; python script/36_build_direct_read_audit_bundle.py; python script/14_validate_workspace.py`
