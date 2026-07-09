# Priority LSMS-ISA Credentialed Raw Acquisition Workbench

Dataset: `TZA_2010_NPS-R2_v03_M` - Tanzania 2010-2011

Official get-microdata URL: https://microdata.worldbank.org/catalog/1050/get-microdata

Target folder: `temp/raw_downloads/TZA_2010_NPS-R2_v03_M/`

Current receipt status: `blocked_no_original_package`

## Manual Download Action

Open official_get_microdata_url, log in or register if required, accept official terms/Data Access Agreement, download the complete unchanged raw package plus all documentation, and place all files in local_target_folder.

Scope: Download the complete unchanged official World Bank package for this IDNO, including all raw microdata files, archives, documentation, questionnaires, codebooks, DDI/XML, and geography/timing supplements exposed after login.

## Core Files To Confirm After Download

| requirement | file_rank | file_name | candidate_variable_rows | top_variable_names |
|---|---|---|---|---|
| climate_geography | 1 | HH_SEC_A | 6 | clusterid;district;ea;hh_a18_year;region;ward |
| climate_geography | 2 | TZY2.EA.Offsets | 2 | clusterid;rum |
| climate_geography | 3 | Plot.Geovariables_Y2 | 1 | ea_id |
| climate_geography | 4 | TZY1.HH.Consumption | 1 | urban |
| climate_geography | 5 | TZY2.HH.Consumption | 1 | urban |
| climate_geography | 6 | HH.Geovariables_Y2 | 1 | ea_id |
| consumption_or_income | 1 | TZY1.HH.Consumption | 4 | hhexpenses;hhexpensesR;expm;expmR |
| consumption_or_income | 2 | TZY2.HH.Consumption | 4 | hhexpenses;hhexpensesR;expm;expmR |
| consumption_or_income | 3 | HH_SEC_L | 4 | hh_l01_2;hh_l02;itemcode;y2_hhid |
| health_need_and_access | 1 | HH_SEC_D | 5 | hh_d12_1;hh_d12_2;hh_d02;hh_d13;hh_d38 |
| health_need_and_access | 2 | FS_H2 | 2 | costid;costitem |
| health_need_and_access | 3 | TZY1.HH.Consumption | 2 | health;healthR |
| health_need_and_access | 4 | FS_N2 | 1 | costid |
| health_need_and_access | 5 | HH_SEC_G | 1 | hh_g03_5 |
| health_need_and_access | 6 | TZY2.HH.Consumption | 1 | health |
| household_person_keys | 1 | HH_SEC_B | 2 | hhid_2008;y2_hhid |
| household_person_keys | 2 | AG_SEC10B | 1 | y2_hhid |
| household_person_keys | 3 | AG_SEC7A | 1 | y2_hhid |
| household_person_keys | 4 | AG_SEC7B | 1 | y2_hhid |
| household_person_keys | 5 | TZY2.HH.Consumption | 1 | hhid_2008 |

## Official File Manifest Preview

| file_id | file_name | file_description | case_quantity | variable_quantity | priority_core_target |
|---|---|---|---|---|---|
| F95 | AG_SEC01 | This file contains data from Module 1 of the Agriculture questionnaire - name, age and sex of household members. | 15666 | 5 | 0 |
| F96 | AG_FILTERS | This file contains filter questions from the Agriculture questionnaire. | 3924 | 9 | 0 |
| F97 | AG_NETWORK | This file contains information on the network roster card on the last page of the Agriculture questionnaire. | 8884 | 4 | 0 |
| F98 | AG_SEC2A | This file contains data related to section 2A of the Agriculture questionnaire - list of all plots cultivated or owne... | 6038 | 8 | 0 |
| F99 | AG_SEC2B | This file contains data related to section 2B of the Agriculture questionnaire - list of all plots cultivated or owne... | 38 | 8 | 0 |
| F100 | AG_SEC3A | This file contains data related to section 3A of the Agriculture questionnaire - detailed plot information (agricultu... | 6038 | 166 | 0 |
| F101 | AG_SEC3B | This file contains data related to section 3B of the Agriculture questionnaire - detailed plot information (agricultu... | 6076 | 160 | 0 |
| F102 | AG_SEC4A | This file contains data related to section 4A of the Agriculture questionnaire - crops planted and harvested, seeds u... | 8206 | 29 | 0 |
| F103 | AG_SEC4B | This file contains data related to section 4B of the Agriculture questionnaire - crops planted and harvested, seeds u... | 6742 | 29 | 0 |
| F104 | AG_SEC5A | This file contains dta related to section 5A of the Agriculture questionnaire - quantity and value of crops sold, pos... | 4621 | 41 | 0 |
| F105 | AG_SEC5B | This file contains dta related to section 5B of the Agriculture questionnaire - quantity and value of crops sold, pos... | 1336 | 41 | 0 |
| F106 | AG_SEC6A | This file contains data related to section 6A of the Agriculture questionnaire - age of plants, agricultural practice... | 4796 | 16 | 0 |
| F107 | AG_SEC6B | This file contains data related to section 6B of the Agriculture questionnaire - age of plants, agricultural practice... | 3990 | 16 | 0 |
| F108 | AG_SEC7A | This file contains data related to section 7A of the Agriculture questionnaire - quantity and value of crop sole, pos... | 4110 | 17 | 1 |
| F109 | AG_SEC7B | This file contains data related to section 7B of the Agriculture questionnaire - quantity and value of crop sole, pos... | 2983 | 18 | 1 |
| F110 | AG_SEC8A | This file contains data related to section 8A of the Agriculture questionnaire - outgrowers or contract farming agree... | 28 | 15 | 0 |
| F111 | AG_SEC8B | This file contains data related to section 8B of the Agriculture questionnaire - outgrowers or contract farming agree... | 2 | 15 | 0 |
| F112 | AG_SEC8C | This file contains data related to section 8C of the Agriculture questionnaire - outgrowers or contract farming agree... | 4 | 15 | 0 |
| F113 | AG_SEC09 | This file contains data related to section 9 of the Agriculture questionnaire - agricultural products that were proce... | 4713 | 16 | 0 |
| F114 | AG_SEC10A | This file contains data related to section 10A of the Agriculture questionnaire - livestock owned by the household du... | 30944 | 56 | 0 |

## After Placing Files

Run:

`python script/17_audit_raw_downloads.py; python script/144_build_priority_lsms_isa_raw_package_intake_packet.py; python script/145_build_priority_lsms_isa_archive_member_preflight.py; python script/149_build_priority_lsms_isa_raw_value_verification_workbook.py; python script/150_build_priority_lsms_isa_raw_package_receipt_checklist.py; python script/152_build_priority_lsms_isa_credentialed_raw_acquisition_workbench.py; python script/132_build_priority_analysis_dataset_synthesis_blueprint.py; python script/148_build_priority_lsms_isa_country_wave_promotion_packets.py; python script/151_refresh_refocused_promoted_country_wave_registry.py; python script/127_enforce_promoted_data_gate.py; python script/36_build_direct_read_audit_bundle.py; python script/14_validate_workspace.py`

## Stop Rule

Do not mark receipt, raw-value verification, climate linkage, or analysis
readiness as passed until the complete official package is present and the raw
value workbook evidence fields are filled from original files.
