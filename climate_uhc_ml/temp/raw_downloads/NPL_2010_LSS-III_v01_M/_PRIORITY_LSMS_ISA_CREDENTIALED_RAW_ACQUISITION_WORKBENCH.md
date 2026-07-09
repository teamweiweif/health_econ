# Priority LSMS-ISA Credentialed Raw Acquisition Workbench

Dataset: `NPL_2010_LSS-III_v01_M` - Nepal 2010-2011

Official get-microdata URL: https://microdata.worldbank.org/catalog/1000/get-microdata

Target folder: `temp/raw_downloads/NPL_2010_LSS-III_v01_M/`

Current receipt status: `blocked_no_original_package`

## Manual Download Action

Open official_get_microdata_url, log in or register if required, accept official terms/Data Access Agreement, download the complete unchanged raw package plus all documentation, and place all files in local_target_folder.

Scope: Download the complete unchanged official World Bank package for this IDNO, including all raw microdata files, archives, documentation, questionnaires, codebooks, DDI/XML, and geography/timing supplements exposed after login.

## Core Files To Confirm After Download

| requirement | file_rank | file_name | candidate_variable_rows | top_variable_names |
|---|---|---|---|---|
| climate_geography | 1 | S00 | 4 | v00_zone;v00_headn;v00_team;v00_ward |
| climate_geography | 2 | FINAL_PREF | 4 | district;district_name;Eastern;HEAD___ |
| climate_geography | 3 | S04 | 2 | v04_03b;v04_11b |
| climate_geography | 4 | S01 | 1 | v01_05b |
| climate_geography | 5 | S21 | 1 | v21_ward |
| consumption_or_income | 1 | FINAL_PREF | 8 | sh_nonfood_30;sh_nonfood_7;nonfood_30;nonfood_7;nonfood_pc_30;nonfood_pc_7;nonfood_pc_7_tadj;nfood |
| consumption_or_income | 2 | S06B | 2 | v06b_idc;v06b_itm |
| consumption_or_income | 3 | S06A | 2 | v06a_idc;v06a_itm |
| health_need_and_access | 1 | S08 | 6 | v08_12;v08_17b;v08_14;v08_16;v08_17a;v08_17c |
| health_need_and_access | 2 | S19 | 2 | v19_09;v19_05 |
| health_need_and_access | 3 | S09B | 2 | v09_18;v09_24 |
| health_need_and_access | 4 | S03 | 2 | v03_03a;v03_03b |
| household_person_keys | 1 | S01 | 8 | v01_10;REC_TYPE;v01_01;v01_02;v01_03;v01_04;v01_05a;v01_05b |
| household_person_keys | 2 | S21x | 2 | v21_10;v21_11 |
| household_person_keys | 3 | S10B | 1 | v10_02 |
| household_person_keys | 4 | S12 | 1 | v12_01 |
| oop_health_expenditure | 1 | S08 | 6 | v08_17a;v08_07a;v08_07b;v08_17b;v08_18;v08_17c |
| survey_timing | 1 | S00 | 7 | v00_int1_m;v00_int1_y;v00_int2_m;v00_int2_y;v00_int3_m;v00_int3_y;v00_sup_m |
| survey_timing | 2 | sys | 4 | hsys_c1date;hsys_u1date;hsys_c2date;hsys_u2date |
| survey_timing | 3 | FINAL_PREF | 1 | Date |

## Official File Manifest Preview

| file_id | file_name | file_description | case_quantity | variable_quantity | priority_core_target |
|---|---|---|---|---|---|
| F1 | anthro |  | 3450 | 19 | 1 |
| F2 | FINAL_PREF |  | 5988 | 266 | 1 |
| F4 | S01 | This file contains household-member information from Section 1 - Household Roster of the questionnaire. It contains t... | 34815 | 23 | 1 |
| F5 | S02 | This file contains household-level information from Section 2 - Housing of the questionnaire. It contains the followi... | 7180 | 64 | 0 |
| F6 | S03 | This file contains household-level information from Section 3 - Access to Facilities of the questionnaire. It contain... | 172320 | 14 | 1 |
| F7 | S04 | This file contains household-level information from Section 3 - Migration of the questionnaire. It contains the follo... | 34815 | 28 | 1 |
| F8 | S05 | This file contains household-level information from Section 5 - Food Expenses and Home Production of the questionnair... | 531320 | 21 | 0 |
| F9 | S06A | This file contains household-level information from Section 6 - Non-food Expenditures and Inventory of Durable Goods,... | 186680 | 9 | 1 |
| F10 | S06B | This file contains household-level information from Section 6 - Non-food Expenditures and Inventory of Durable Goods,... | 265660 | 8 | 1 |
| F11 | S06C | This file contains household-level information from Section 6 - Non-food Expenditures and Inventory of Durable Goods,... | 122060 | 12 | 1 |
| F12 | S06D | This file contains household-level information from Section 6 - Non-food Expenditures and Inventory of Durable Goods,... | 100520 | 9 | 1 |
| F13 | S07 | The file contains data for questions in SECTION 7. EDUCATION of NLSS III Questionnaire. | 34815 | 50 | 0 |
| F14 | S08 | The file contains data for Section 8. Health of the NLSS III (2010/11) questionnaire. | 34815 | 64 | 1 |
| F15 | S09A | The file contains data for Part A. Maternity History of Section 9. Marriage and Maternity History of the NLSS III (20... | 18860 | 20 | 0 |
| F16 | S09B | The file contains data for Part B. Pre- and Post-Natal Care of Section 9. Marriage and Maternity History of the NLSS ... | 1875 | 20 | 1 |
| F17 | S09C | The file contains data for Part C. Family Planning of Section 9. Marriage and Maternity History | 34807 | 18 | 0 |
| F18 | S09D | The file contains data for Part D. Household Decisions of Section 9. Marriage and Maternity History of the NLSS III (... | 99135 | 9 | 1 |
| F19 | S10A | The file contains data for Part A. Time Use of Section 10. Jobs and Time Use of the NLSS III (2010/11) questionnaire. | 34815 | 20 | 0 |
| F20 | S10B | The file contains data for Part B. Jobs during the past 12 Months of Section 10. Jobs and Time Use of the NLSS III (2... | 39665 | 32 | 1 |
| F21 | S11 | The file contains data for Section 11. Unemployment/ Under-employment of the NLSS III (2010/11) questionnaire. | 34815 | 13 | 0 |

## After Placing Files

Run:

`python script/17_audit_raw_downloads.py; python script/144_build_priority_lsms_isa_raw_package_intake_packet.py; python script/145_build_priority_lsms_isa_archive_member_preflight.py; python script/149_build_priority_lsms_isa_raw_value_verification_workbook.py; python script/150_build_priority_lsms_isa_raw_package_receipt_checklist.py; python script/152_build_priority_lsms_isa_credentialed_raw_acquisition_workbench.py; python script/153_validate_priority_lsms_isa_official_file_receipt.py; python script/154_build_priority_lsms_isa_threshold_download_sequence.py; python script/132_build_priority_analysis_dataset_synthesis_blueprint.py; python script/148_build_priority_lsms_isa_country_wave_promotion_packets.py; python script/151_refresh_refocused_promoted_country_wave_registry.py; python script/127_enforce_promoted_data_gate.py; python script/36_build_direct_read_audit_bundle.py; python script/14_validate_workspace.py`

## Stop Rule

Do not mark receipt, raw-value verification, climate linkage, or analysis
readiness as passed until the complete official package is present and the raw
value workbook evidence fields are filled from original files.
