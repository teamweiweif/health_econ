# Priority LSMS-ISA Credentialed Raw Acquisition Workbench

Dataset: `UGA_2018_UNPS_v02_M` - Uganda 2018-2019

Official get-microdata URL: https://microdata.worldbank.org/catalog/3795/get-microdata

Target folder: `temp/raw_downloads/UGA_2018_UNPS_v02_M/`

Current receipt status: `blocked_no_original_package`

## Manual Download Action

Open official_get_microdata_url, log in or register if required, accept official terms/Data Access Agreement, download the complete unchanged raw package plus all documentation, and place all files in local_target_folder.

Scope: Download the complete unchanged official World Bank package for this IDNO, including all raw microdata files, archives, documentation, questionnaires, codebooks, DDI/XML, and geography/timing supplements exposed after login.

## Core Files To Confirm After Download

| requirement | file_rank | file_name | candidate_variable_rows | top_variable_names |
|---|---|---|---|---|
| climate_geography | 1 | pov2018_19 | 4 | qurban;regurb;urban;district |
| climate_geography | 2 | GSEC1 | 4 | urban;district_code;s1aq07;regurb |
| climate_geography | 3 | WSEC1A | 2 | urban;regurb |
| climate_geography | 4 | AGSEC1 | 2 | region;urban |
| consumption_or_income | 1 | pov2018_19 | 7 | cpexp30;fcpexp30;nrrexp30;fnrfxp30;hpline;ctpline;spline |
| consumption_or_income | 2 | GSEC15B | 3 | CEB03;CEB04;CEB07 |
| consumption_or_income | 3 | GSEC15E | 1 | CEE02_1 |
| consumption_or_income | 4 | GSEC7_2 | 1 | IncomeSource |
| health_need_and_access | 1 | CSEC4B | 4 | s4bq23;s4bq26;s4bq27;s4bq28 |
| health_need_and_access | 2 | CSEC2B | 2 | s2bq09;s2bq10 |
| health_need_and_access | 3 | CSEC4C | 2 | healthservice_id;s4cq46 |
| health_need_and_access | 4 | CSEC4D | 2 | s4eq61;s4eq61_v2 |
| health_need_and_access | 5 | CSEC4L | 1 | health_water_id |
| health_need_and_access | 6 | CSEC4F | 1 | s4fq65 |
| household_person_keys | 1 | GSEC2 | 2 | hhid;t0_hhid |
| household_person_keys | 2 | GSEC1 | 1 | hhid |
| household_person_keys | 3 | GSEC2B | 1 | hhid |
| household_person_keys | 4 | GSEC4 | 1 | hhid |
| household_person_keys | 5 | GSEC5 | 1 | hhid |
| household_person_keys | 6 | GSEC6_1 | 1 | hhid |

## Official File Manifest Preview

| file_id | file_name | file_description | case_quantity | variable_quantity | priority_core_target |
|---|---|---|---|---|---|
| F1 | AGSEC1 | Agriculture Questionnaire Section 1: Household identification particulars | 3242 | 15 | 1 |
| F2 | AGSEC2A | Agriculture Questionnaire Section 2A: Current land holdings - second/first visit | 4368 | 47 | 0 |
| F3 | AGSEC2B | Agriculture Questionnaire Section 2B: Land that the household has access through use rights | 1443 | 26 | 0 |
| F4 | AGSEC3A | Agriculture Questionnaire Section 3A: Agricultural and labor inputs - first visit | 6073 | 37 | 0 |
| F5 | AGSEC3B | Agriculture Questionnaire Section 3B: Agricultural and labor inputs - second visit | 6134 | 33 | 0 |
| F6 | AGSEC4A | Agriculture Questionnaire Section 4A: Crops grown and types of seeds used - first visit | 8776 | 21 | 0 |
| F7 | AGSEC4B | Agriculture Questionnaire Section 4B: Crops grown and types of seeds used - second visit (cont.) | 7063 | 21 | 0 |
| F8 | AGSEC5A | Agriculture Questionnaire Section 5A: Quantification of production - first visit | 7153 | 33 | 0 |
| F9 | AGSEC5B | Agriculture Questionnaire Section 5B: Quantification of production - second visit | 7041 | 84 | 0 |
| F10 | AGSEC6A | Agriculture Questionnaire Section 6A: Cattle and pack animals | 1615 | 30 | 0 |
| F11 | AGSEC6B | Agriculture Questionnaire Section 6B: Small animals | 2355 | 30 | 0 |
| F12 | AGSEC6C | Agriculture Questionnaire Section 6C: Poultry & others | 1424 | 30 | 0 |
| F13 | AGSEC8A | Agriculture Questionnaire Section 8A: Livestock production - meat | 5854 | 10 | 0 |
| F14 | AGSEC8B | Agriculture Questionnaire Section 8B: Livestock production - milk | 3058 | 15 | 0 |
| F15 | AGSEC8C | Agriculture Questionnaire Section 8C: Livestock production - eggs | 1793 | 10 | 0 |
| F16 | AGSEC9A | Agriculture Questionnaire Section 9: Extension services | 298 | 21 | 0 |
| F17 | AGSEC9B | Agriculture Questionnaire Section 9: Extension services (cont) | 3212 | 15 | 0 |
| F18 | AGSEC10 | Agriculture Questionnaire Section 10: Farm implements and machinery | 8297 | 11 | 0 |
| F19 | AGSEC11 | Agriculture Questionnaire Section 11: Animal power | 7662 | 15 | 0 |
| F20 | CSEC1A | Community/Facility Questionnaire Section 1A: Identification particulars | 305 | 12 | 1 |

## After Placing Files

Run:

`python script/17_audit_raw_downloads.py; python script/144_build_priority_lsms_isa_raw_package_intake_packet.py; python script/145_build_priority_lsms_isa_archive_member_preflight.py; python script/149_build_priority_lsms_isa_raw_value_verification_workbook.py; python script/150_build_priority_lsms_isa_raw_package_receipt_checklist.py; python script/152_build_priority_lsms_isa_credentialed_raw_acquisition_workbench.py; python script/153_validate_priority_lsms_isa_official_file_receipt.py; python script/132_build_priority_analysis_dataset_synthesis_blueprint.py; python script/148_build_priority_lsms_isa_country_wave_promotion_packets.py; python script/151_refresh_refocused_promoted_country_wave_registry.py; python script/127_enforce_promoted_data_gate.py; python script/36_build_direct_read_audit_bundle.py; python script/14_validate_workspace.py`

## Stop Rule

Do not mark receipt, raw-value verification, climate linkage, or analysis
readiness as passed until the complete official package is present and the raw
value workbook evidence fields are filled from original files.
