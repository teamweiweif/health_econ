# Priority LSMS-ISA Credentialed Raw Acquisition Workbench

Dataset: `MWI_2004_IHS-II_v01_M` - Malawi 2004-2005

Official get-microdata URL: https://microdata.worldbank.org/catalog/2307/get-microdata

Target folder: `temp/raw_downloads/MWI_2004_IHS-II_v01_M/`

Current receipt status: `blocked_no_original_package`

## Manual Download Action

Open official_get_microdata_url, log in or register if required, accept official terms/Data Access Agreement, download the complete unchanged raw package plus all documentation, and place all files in local_target_folder.

Scope: Download the complete unchanged official World Bank package for this IDNO, including all raw microdata files, archives, documentation, questionnaires, codebooks, DDI/XML, and geography/timing supplements exposed after login.

## Core Files To Confirm After Download

| requirement | file_rank | file_name | candidate_variable_rows | top_variable_names |
|---|---|---|---|---|
| climate_geography | 1 | sec_a.NSDstat | 1 | type |
| climate_geography | 2 | sec_f.NSDstat | 1 | type |
| climate_geography | 3 | sec_g.NSDstat | 1 | type |
| climate_geography | 4 | sec_h.NSDstat | 1 | type |
| climate_geography | 5 | sec_i.NSDstat | 1 | type |
| climate_geography | 6 | sec_j1.NSDstat | 1 | type |
| climate_geography | 7 | sec_j2.NSDstat | 1 | type |
| climate_geography | 8 | sec_k.NSDstat | 1 | type |
| consumption_or_income | 1 | sec_j1.NSDstat | 10 | add;case_id;dist;ea;hhid;hhsize;hhwght;j01a;j02a;j03a |
| consumption_or_income | 2 | sec_i.NSDstat | 1 | i03both |
| consumption_or_income | 3 | sec_aa.NSDstat | 1 | aa01 |
| health_need_and_access | 1 | sec_d.NSDstat | 7 | d05a;d05aoth;d05b;d05both;d27a;d27b;d04 |
| health_need_and_access | 2 | mod_d.NSDstat | 5 | cd51b;cd_51a;cd47;cd57a;cd_50 |
| household_person_keys | 1 | sec_b.NSDstat | 1 | hhid |
| household_person_keys | 2 | sec_a.NSDstat | 1 | hhid |
| household_person_keys | 3 | sec_f.NSDstat | 1 | hhid |
| household_person_keys | 4 | sec_g.NSDstat | 1 | hhid |
| household_person_keys | 5 | sec_h.NSDstat | 1 | hhid |
| household_person_keys | 6 | sec_i.NSDstat | 1 | hhid |
| household_person_keys | 7 | sec_j1.NSDstat | 1 | hhid |

## Official File Manifest Preview

| file_id | file_name | file_description | case_quantity | variable_quantity | priority_core_target |
|---|---|---|---|---|---|
| F1 | sec_a.NSDstat | Household characteristics, income and expenditure questionnaire, Module A-1: household identification | 11280 | 38 | 1 |
| F2 | sec_aa.NSDstat | Household characteristics, income and expenditure questionnaire, Module AA: Subjective assessment of well-being | 11280 | 35 | 1 |
| F3 | sec_ab.NSDstat | Household characteristics, income and expenditure questionnaire, Module AB: Recent shocks to household welfare | 203044 | 28 | 0 |
| F4 | sec_ac.NSDstat | Household characteristics, income and expenditure questionnaire, Module AC: Deaths in household | 1731 | 35 | 0 |
| F5 | sec_ad.NSDstat | Household characteristics, income and expenditure questionnaire, Module AD: Child anthropometry | 52644 | 32 | 0 |
| F6 | sec_b.NSDstat | Household characteristics, income and expenditure questionnaire, Module B: household roster | 52707 | 53 | 1 |
| F7 | sec_c.NSDstat | Household characteristics, income and expenditure questionnaire, Module C: Education | 52707 | 62 | 1 |
| F8 | sec_d.NSDstat | Household characteristics, income and expenditure questionnaire, Module D: Health | 51292 | 70 | 1 |
| F9 | sec_e.NSDstat | Household characteristics, income and expenditure questionnaire, Module E: Time use & labour | 52702 | 52 | 0 |
| F10 | sec_f.NSDstat | Household characteristics, income and expenditure questionnaire, Module F: Security & safety | 52679 | 50 | 1 |
| F11 | sec_g.NSDstat | Household characteristics, income and expenditure questionnaire, Module G: Housing | 11280 | 73 | 1 |
| F12 | sec_h.NSDstat | Household characteristics, income and expenditure questionnaire, Module H: Consumption of selected food over past thr... | 67680 | 22 | 1 |
| F13 | sec_i.NSDstat | Household characteristics, income and expenditure questionnaire, Module I: Consumption of food over past one week | 1297199 | 31 | 1 |
| F14 | sec_j1.NSDstat | Household characteristics, income and expenditure questionnaire, Module J: Non-food expenditures - past one week & on... | 67676 | 18 | 1 |
| F15 | sec_j2.NSDstat | Household characteristics, income and expenditure questionnaire, Module J: Non-food expenditures - past one week & on... | 203040 | 18 | 1 |
| F16 | sec_k.NSDstat | Household characteristics, income and expenditure questionnaire, Module K: Non-food expenditures - Past three months | 439920 | 18 | 1 |
| F17 | sec_l.NSDstat | Household characteristics, income and expenditure questionnaire, Module L: Non-food expenditures - Past twelve months | 191760 | 19 | 0 |
| F18 | sec_m1.NSDstat | Household characteristics, income and expenditure questionnaire, Module M: Durable goods | 214319 | 22 | 0 |
| F19 | sec_m2.NSDstat | Household characteristics, income and expenditure questionnaire, Module M: Durable goods | 191760 | 20 | 0 |
| F20 | sec_n.NSDstat | Household characteristics, income and expenditure questionnaire, Module N: Agriculture - general | 11280 | 46 | 0 |

## After Placing Files

Run:

`python script/17_audit_raw_downloads.py; python script/144_build_priority_lsms_isa_raw_package_intake_packet.py; python script/145_build_priority_lsms_isa_archive_member_preflight.py; python script/149_build_priority_lsms_isa_raw_value_verification_workbook.py; python script/150_build_priority_lsms_isa_raw_package_receipt_checklist.py; python script/152_build_priority_lsms_isa_credentialed_raw_acquisition_workbench.py; python script/153_validate_priority_lsms_isa_official_file_receipt.py; python script/154_build_priority_lsms_isa_threshold_download_sequence.py; python script/132_build_priority_analysis_dataset_synthesis_blueprint.py; python script/148_build_priority_lsms_isa_country_wave_promotion_packets.py; python script/151_refresh_refocused_promoted_country_wave_registry.py; python script/127_enforce_promoted_data_gate.py; python script/36_build_direct_read_audit_bundle.py; python script/14_validate_workspace.py`

## Stop Rule

Do not mark receipt, raw-value verification, climate linkage, or analysis
readiness as passed until the complete official package is present and the raw
value workbook evidence fields are filled from original files.
