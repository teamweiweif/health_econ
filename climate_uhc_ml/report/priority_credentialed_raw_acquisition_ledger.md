# Priority Credentialed Raw Acquisition Ledger

Status: credentialed-download execution layer for the priority dataset-promotion
batch. This does not bypass World Bank login, registration, terms, or Data
Access Agreement gates. It turns the official metadata and download dossier
into a per-wave raw-package acquisition checklist.

## Summary

| Metric | Value | Interpretation |
|---|---:|---|
| priority_credentialed_acquisition_dataset_rows | 13 | Priority and backup datasets with credentialed raw-acquisition instructions. |
| priority_credentialed_acquisition_priority_batch_rows | 10 | Immediate priority waves in the credentialed acquisition ledger. |
| priority_credentialed_acquisition_backup_rows | 3 | Backup sixth-country waves in the credentialed acquisition ledger. |
| priority_credentialed_acquisition_full_file_rows | 965 | Official metadata file rows carried into the download review manifest. |
| priority_credentialed_acquisition_core_file_rows | 156 | Priority core file/module rows to confirm after official download. |
| priority_credentialed_acquisition_public_documentation_ready_rows | 13 | Datasets with complete public documentation receipt before raw acquisition. |
| priority_credentialed_acquisition_official_metadata_ready_rows | 13 | Datasets with official DDI/XML metadata evidence before raw acquisition. |
| priority_credentialed_acquisition_original_package_receipt_rows | 0 | Datasets with any original raw/package files already received. |
| priority_credentialed_acquisition_targets_missing_before_download | 156 | Priority target files still missing before credentialed download. |
| priority_credentialed_acquisition_handoff_readmes_written | 13 | Per-wave credentialed raw acquisition handoff README files written. |
| modeling_gate_status | blocked | Credentialed acquisition instructions do not satisfy raw value verification or climate-linkage promotion gates. |
| priority_credentialed_acquisition_status_ready_for_credentialed_manual_download | 13 | Credentialed acquisition status count. |

## Dataset Ledger

| acquisition_batch_rank | idno | official_full_file_rows | priority_core_file_rows | public_documentation_status | official_metadata_evidence_status | raw_receipt_status | credentialed_acquisition_status | local_target_folder |
|---|---|---|---|---|---|---|---|---|
| 1 | ETH_2021_ESPS-W5_v02_M | 68 | 12 | complete_full_public_documentation_receipt | complete_official_metadata_evidence_extract | not_received_no_original_raw_package | ready_for_credentialed_manual_download | temp/raw_downloads/ETH_2021_ESPS-W5_v02_M/ |
| 2 | ETH_2018_ESS_v04_M | 68 | 12 | complete_full_public_documentation_receipt | complete_official_metadata_evidence_extract | not_received_no_original_raw_package | ready_for_credentialed_manual_download | temp/raw_downloads/ETH_2018_ESS_v04_M/ |
| 3 | MWI_2007-2009_MTM_v01_M | 118 | 12 | complete_core_public_documentation_receipt_optional_pdf_unlisted_or_missing | partial_official_metadata_evidence_extract | not_received_no_original_raw_package | ready_for_credentialed_manual_download | temp/raw_downloads/MWI_2007-2009_MTM_v01_M/ |
| 4 | NGA_2012_GHSP-W2_v02_M | 103 | 12 | complete_full_public_documentation_receipt | partial_official_metadata_evidence_extract | not_received_no_original_raw_package | ready_for_credentialed_manual_download | temp/raw_downloads/NGA_2012_GHSP-W2_v02_M/ |
| 5 | NGA_2015_GHSP-W3_v02_M | 104 | 12 | complete_full_public_documentation_receipt | partial_official_metadata_evidence_extract | not_received_no_original_raw_package | ready_for_credentialed_manual_download | temp/raw_downloads/NGA_2015_GHSP-W3_v02_M/ |
| 6 | NGA_2010_GHSP-W1_v03_M | 99 | 12 | complete_full_public_documentation_receipt | partial_official_metadata_evidence_extract | not_received_no_original_raw_package | ready_for_credentialed_manual_download | temp/raw_downloads/NGA_2010_GHSP-W1_v03_M/ |
| 7 | TZA_2008_NPS-R1_v03_M | 61 | 12 | complete_full_public_documentation_receipt | partial_official_metadata_evidence_extract | not_received_no_original_raw_package | ready_for_credentialed_manual_download | temp/raw_downloads/TZA_2008_NPS-R1_v03_M/ |
| 8 | TZA_2010_NPS-R2_v03_M | 95 | 12 | complete_full_public_documentation_receipt | partial_official_metadata_evidence_extract | not_received_no_original_raw_package | ready_for_credentialed_manual_download | temp/raw_downloads/TZA_2010_NPS-R2_v03_M/ |
| 9 | TZA_2012_NPS-R3_v01_M | 80 | 12 | complete_full_public_documentation_receipt | complete_official_metadata_evidence_extract | not_received_no_original_raw_package | ready_for_credentialed_manual_download | temp/raw_downloads/TZA_2012_NPS-R3_v01_M/ |
| 10 | UGA_2014_SAGE-EL_v01_M | 35 | 12 | complete_full_public_documentation_receipt | partial_official_metadata_evidence_extract | not_received_no_original_raw_package | ready_for_credentialed_manual_download | temp/raw_downloads/UGA_2014_SAGE-EL_v01_M/ |
| 11 | JAM_1997_SLC_v01_M | 68 | 12 | complete_full_public_documentation_receipt | partial_official_metadata_evidence_extract | not_received_no_original_raw_package | ready_for_credentialed_manual_download | temp/raw_downloads/JAM_1997_SLC_v01_M/ |
| 12 | KGZ_1993_KMPS_v01_M | 15 | 12 | complete_core_public_documentation_receipt_optional_pdf_unlisted_or_missing | partial_official_metadata_evidence_extract | not_received_no_original_raw_package | ready_for_credentialed_manual_download | temp/raw_downloads/KGZ_1993_KMPS_v01_M/ |
| 13 | NPL_2010_LSS-III_v01_M | 51 | 12 | complete_full_public_documentation_receipt | partial_official_metadata_evidence_extract | not_received_no_original_raw_package | ready_for_credentialed_manual_download | temp/raw_downloads/NPL_2010_LSS-III_v01_M/ |

## Priority Core File Checklist Preview

| acquisition_batch_rank | idno | core_file_rank | metadata_file_name | candidate_categories | candidate_harmonized_variables | current_receipt_status |
|---|---|---|---|---|---|---|
| 1 | ETH_2021_ESPS-W5_v02_M | 1 | sect3_hh_w5.dta | demographics;geography;health_expenditure;health_need_access;survey_design | admin1_or_admin2;age;care_not_sought_reason;care_sought;health_insurance;hhid;household_weight_or_person_weight;illne... | not_received_no_original_raw_package |
| 1 | ETH_2021_ESPS-W5_v02_M | 2 | sect04_com_w5.dta | demographics;geography;health_need_access;shocks;survey_design | admin1_or_admin2;asset_index_or_asset_variable;care_sought;psu_or_cluster_id;reason_not_sought_distance;rural;sex;sho... | not_received_no_original_raw_package |
| 1 | ETH_2021_ESPS-W5_v02_M | 3 | sect06_com_w5.dta | geography;health_need_access;shocks;survey_design | admin1_or_admin2;agriculture_livelihood;coping_borrowed;psu_or_cluster_id;reason_not_sought_distance;rural;shock_modu... | not_received_no_original_raw_package |
| 1 | ETH_2021_ESPS-W5_v02_M | 4 | sect11_com_w5.dta | demographics;geography;shocks;survey_design | admin1_or_admin2;agriculture_livelihood;education;psu_or_cluster_id;rural | not_received_no_original_raw_package |
| 1 | ETH_2021_ESPS-W5_v02_M | 5 | sect3_pp_w5.dta | geography;health_need_access;shocks;survey_design | admin1_or_admin2;agriculture_livelihood;coping_borrowed;hhid;household_weight_or_person_weight;latitude_or_longitude;... | not_received_no_original_raw_package |
| 1 | ETH_2021_ESPS-W5_v02_M | 6 | sect4_pp_w5.dta | geography;shocks;survey_design | admin1_or_admin2;agriculture_livelihood;hhid;household_weight_or_person_weight;psu_or_cluster_id;rural;shock_module_v... | not_received_no_original_raw_package |
| 1 | ETH_2021_ESPS-W5_v02_M | 7 | sect7_pp_w5.dta | demographics;geography;health_need_access;shocks;survey_design | admin1_or_admin2;agriculture_livelihood;care_not_sought_reason;coping_borrowed;education;household_weight_or_person_w... | not_received_no_original_raw_package |
| 1 | ETH_2021_ESPS-W5_v02_M | 8 | sect9_ph_w5.dta | geography;shocks;survey_design | admin1_or_admin2;agriculture_livelihood;hhid;household_weight_or_person_weight;psu_or_cluster_id;rural;shock_module_v... | not_received_no_original_raw_package |
| 1 | ETH_2021_ESPS-W5_v02_M | 9 | sect11_ph_w5.dta | geography;health_need_access;shocks;survey_design | admin1_or_admin2;agriculture_livelihood;hhid;household_weight_or_person_weight;psu_or_cluster_id;reason_not_sought_di... | not_received_no_original_raw_package |
| 1 | ETH_2021_ESPS-W5_v02_M | 10 | sect8_2_ls_w5.dta | consumption;geography;health_need_access;shocks;survey_design | admin1_or_admin2;agriculture_livelihood;hhid;household_weight_or_person_weight;psu_or_cluster_id;reason_not_sought_di... | not_received_no_original_raw_package |
| 1 | ETH_2021_ESPS-W5_v02_M | 11 | sect8_3_ls_w5.dta | geography;health_expenditure;health_need_access;shocks;survey_design | admin1_or_admin2;agriculture_livelihood;care_sought;hhid;household_weight_or_person_weight;oop_health_expenditure;psu... | not_received_no_original_raw_package |
| 1 | ETH_2021_ESPS-W5_v02_M | 12 | eth_householdgeovariables_y5.dta | geography;health_need_access;shocks;survey_design | admin1_or_admin2;agriculture_livelihood;hhid;latitude_or_longitude;psu_or_cluster_id;reason_not_sought_distance;rural... | not_received_no_original_raw_package |
| 2 | ETH_2018_ESS_v04_M | 1 | sect3_hh_w4.dta | demographics;geography;health_expenditure;health_need_access;survey_design | admin1_or_admin2;age;care_not_sought_reason;care_sought;health_insurance;hhid;household_weight_or_person_weight;illne... | not_received_no_original_raw_package |
| 2 | ETH_2018_ESS_v04_M | 2 | sect5b2_hh_w4.dta | demographics;geography;survey_design | admin1_or_admin2;age;asset_index_or_asset_variable;hhid;household_weight_or_person_weight;pid;psu_or_cluster_id;rural... | not_received_no_original_raw_package |
| 2 | ETH_2018_ESS_v04_M | 3 | sect10c_hh_w4.dta | demographics;geography;shocks;survey_design | admin1_or_admin2;agriculture_livelihood;asset_index_or_asset_variable;hhid;household_weight_or_person_weight;pid;psu_... | not_received_no_original_raw_package |
| 2 | ETH_2018_ESS_v04_M | 4 | sect8_2_ls_w4.dta | consumption;geography;health_need_access;shocks;survey_design | admin1_or_admin2;agriculture_livelihood;hhid;household_weight_or_person_weight;psu_or_cluster_id;reason_not_sought_di... | not_received_no_original_raw_package |
| 2 | ETH_2018_ESS_v04_M | 5 | sect8_3_ls_w4.dta | geography;health_expenditure;health_need_access;shocks;survey_design | admin1_or_admin2;agriculture_livelihood;care_sought;hhid;household_weight_or_person_weight;oop_health_expenditure;psu... | not_received_no_original_raw_package |
| 2 | ETH_2018_ESS_v04_M | 6 | sect8_4_ls_w4.dta | geography;shocks;survey_design | admin1_or_admin2;agriculture_livelihood;hhid;household_weight_or_person_weight;psu_or_cluster_id;rural | not_received_no_original_raw_package |
| 2 | ETH_2018_ESS_v04_M | 7 | sect9_ph_w4.dta | geography;shocks;survey_design | admin1_or_admin2;agriculture_livelihood;hhid;household_weight_or_person_weight;psu_or_cluster_id;rural | not_received_no_original_raw_package |
| 2 | ETH_2018_ESS_v04_M | 8 | sect11_ph_w4.dta | geography;health_need_access;shocks;survey_design | admin1_or_admin2;agriculture_livelihood;hhid;household_weight_or_person_weight;psu_or_cluster_id;reason_not_sought_di... | not_received_no_original_raw_package |
| 2 | ETH_2018_ESS_v04_M | 9 | sect3_pp_w4.dta | geography;shocks;survey_design | admin1_or_admin2;agriculture_livelihood;coping_borrowed;hhid;household_weight_or_person_weight;latitude_or_longitude;... | not_received_no_original_raw_package |
| 2 | ETH_2018_ESS_v04_M | 10 | sect4_pp_w4.dta | geography;shocks;survey_design | admin1_or_admin2;agriculture_livelihood;hhid;household_weight_or_person_weight;psu_or_cluster_id;rural | not_received_no_original_raw_package |
| 2 | ETH_2018_ESS_v04_M | 11 | sect04_com_w4.dta | demographics;geography;health_need_access;shocks;survey_design | admin1_or_admin2;asset_index_or_asset_variable;care_sought;psu_or_cluster_id;reason_not_sought_distance;rural;sex;sho... | not_received_no_original_raw_package |
| 2 | ETH_2018_ESS_v04_M | 12 | sect06_com_w4.dta | geography;health_need_access;shocks;survey_design | admin1_or_admin2;agriculture_livelihood;coping_borrowed;psu_or_cluster_id;reason_not_sought_distance;rural;shock_modu... | not_received_no_original_raw_package |
| 3 | MWI_2007-2009_MTM_v01_M | 1 | hh2_cmty | demographics;geography;health_need_access;shocks | admin1_or_admin2;age;agriculture_livelihood;asset_index_or_asset_variable;care_sought;coping_borrowed;education;healt... | not_received_no_original_raw_package |
| 3 | MWI_2007-2009_MTM_v01_M | 2 | hh2p2_s10 | demographics;geography;health_need_access;shocks;survey_design | admin1_or_admin2;age;agriculture_livelihood;asset_index_or_asset_variable;coping_borrowed;hhid;illness_or_injury_need... | not_received_no_original_raw_package |
| 3 | MWI_2007-2009_MTM_v01_M | 3 | hh2p2_s12 | demographics;geography;shocks;survey_design | admin1_or_admin2;age;agriculture_livelihood;asset_index_or_asset_variable;education;hhid;pid;psu_or_cluster_id;sex | not_received_no_original_raw_package |
| 3 | MWI_2007-2009_MTM_v01_M | 4 | hh2p3_s15 | demographics;geography;survey_design | admin1_or_admin2;age;education;hhid;pid;psu_or_cluster_id;sex | not_received_no_original_raw_package |
| 3 | MWI_2007-2009_MTM_v01_M | 5 | hh2p3_s17 | demographics;health_expenditure;health_need_access;shocks;survey_design | age;asset_index_or_asset_variable;hhid;illness_or_injury_need;oop_health_expenditure;pid;shock_module_variable | not_received_no_original_raw_package |
| 3 | MWI_2007-2009_MTM_v01_M | 6 | hh3p3_s15 | demographics;geography;health_need_access;shocks;survey_design | admin1_or_admin2;age;agriculture_livelihood;coping_borrowed;education;hhid;pid;psu_or_cluster_id;reason_not_sought_di... | not_received_no_original_raw_package |

## Guardrail

Download the complete unchanged official package when the official interface
permits it. The 12-file core checklist is for post-download verification, not a
license to assemble an incomplete analysis package from selected modules.

Do not write any country-wave into `data/` until original raw/package receipt,
priority module coverage, raw value checks, merge-key checks, outcome checks,
and accepted CHIRPS/ERA5 climate linkage all pass.

## Machine-Readable Outputs

- `temp/priority_credentialed_raw_acquisition_ledger.csv`
- `temp/priority_credentialed_raw_full_file_manifest.csv`
- `temp/priority_credentialed_raw_core_file_checklist.csv`
- `result/priority_credentialed_raw_acquisition_summary.csv`
