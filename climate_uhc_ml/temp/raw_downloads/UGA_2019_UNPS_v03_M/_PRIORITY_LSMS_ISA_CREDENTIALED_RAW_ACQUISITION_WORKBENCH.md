# Priority LSMS-ISA Credentialed Raw Acquisition Workbench

Dataset: `UGA_2019_UNPS_v03_M` - Uganda 2019-2020

Official get-microdata URL: https://microdata.worldbank.org/catalog/3902/get-microdata

Target folder: `temp/raw_downloads/UGA_2019_UNPS_v03_M/`

Current receipt status: `blocked_no_original_package`

## Manual Download Action

Open official_get_microdata_url, log in or register if required, accept official terms/Data Access Agreement, download the complete unchanged raw package plus all documentation, and place all files in local_target_folder.

Scope: Download the complete unchanged official World Bank package for this IDNO, including all raw microdata files, archives, documentation, questionnaires, codebooks, DDI/XML, and geography/timing supplements exposed after login.

## Core Files To Confirm After Download

| requirement | file_rank | file_name | candidate_variable_rows | top_variable_names |
|---|---|---|---|---|
| climate_geography | 1 | pov2019_20.NSDstat | 3 | regurb;urban;district |
| climate_geography | 2 | GSEC1.NSDstat | 1 | urban |
| climate_geography | 3 | CSEC1A.NSDstat | 1 | Final_EA_code |
| climate_geography | 4 | CSEC2.NSDstat | 1 | Final_EA_code |
| climate_geography | 5 | CSEC2A.NSDstat | 1 | Final_EA_code |
| climate_geography | 6 | CSEC2B.NSDstat | 1 | Final_EA_code |
| climate_geography | 7 | CSEC2C.NSDstat | 1 | Final_EA_code |
| climate_geography | 8 | CSEC2C_0.NSDstat | 1 | Final_EA_code |
| consumption_or_income | 1 | GSEC15B.NSDstat | 9 | CEB03;CEB04;CEB07;CEB10;CEB11;CEB14a;CEB15;CEB16;coicop_2 |
| consumption_or_income | 2 | pov2019_20.NSDstat | 3 | cpexp30;nrrexp30;hpline |
| health_need_and_access | 1 | CSEC2B.NSDstat | 6 | s2bq13__1;s2bq09;s2bq10;s2bq13__2;s2bq13__3;s2bq13__4 |
| health_need_and_access | 2 | CSEC4B.NSDstat | 4 | s4bq23;s4bq26;s4bq27;s4bq28 |
| health_need_and_access | 3 | CSEC4L.NSDstat | 1 | Health_Water_id |
| health_need_and_access | 4 | GSEC6_1.NSDstat | 1 | s6q15b |
| household_person_keys | 1 | GSEC2.NSDstat | 1 | hhid |
| household_person_keys | 2 | GSEC15C.NSDstat | 1 | hhid |
| household_person_keys | 3 | GSEC15D.NSDstat | 1 | hhid |
| household_person_keys | 4 | GSEC17_1.NSDstat | 1 | hhid |
| household_person_keys | 5 | GSEC19.NSDstat | 1 | hhid |
| household_person_keys | 6 | GSEC1.NSDstat | 1 | hhid |

## Official File Manifest Preview

| file_id | file_name | file_description | case_quantity | variable_quantity | priority_core_target |
|---|---|---|---|---|---|
| F1 | AGSEC1.NSDstat | Household Identification Particulars Household level | 2586 | 12 | 0 |
| F2 | AGSEC2A.NSDstat | Current Land Holdings - 1st/2nd Visit Parcel level | 4087 | 46 | 0 |
| F3 | AGSEC2B.NSDstat | Land That the Household Has Access Through Use Rights - 1st/2nd Visit Parcel level | 1278 | 24 | 0 |
| F4 | AGSEC3A.NSDstat | Agriculture and Labour Inputs – 1st Visit Parcel-Plot level | 5884 | 41 | 0 |
| F5 | AGSEC3A_1.NSDstat | Agriculture and Labour Inputs – 1st Visit Parcel-Plot level | 28566 | 7 | 0 |
| F6 | AGSEC3B.NSDstat | Agriculture and Labour Inputs – 2nd Visit Parcel-Plot level | 6378 | 42 | 0 |
| F7 | AGSEC3B_1.NSDstat | Agriculture and Labour Inputs – 2nd Visit Parcel-Plot level | 31147 | 8 | 0 |
| F8 | AGSEC4A.NSDstat | Crops Grown and Types of Seeds Used – 1st Visit Parcel-Plot-Crop level | 8429 | 20 | 0 |
| F9 | AGSEC4B.NSDstat | Crops Grown and Types of Seed Used – 2nd Visit Parcel-Plot-Crop level | 9356 | 20 | 0 |
| F10 | AGSEC5A.NSDstat | Quantification of Production – 1st Visit Parcel-Plot-Crop level | 8429 | 150 | 1 |
| F11 | AGSEC5B.NSDstat | Quantification of Production – 2nd Visit Parcel-Plot-Crop level | 9356 | 78 | 0 |
| F12 | AGSEC6A.NSDstat | Livestock Ownership – Cattle and Pack Animals Livestock Type | 1851 | 27 | 0 |
| F13 | AGSEC6B.NSDstat | Livestock Ownership – Small Animals Livestock Type | 2535 | 27 | 0 |
| F14 | AGSEC6C.NSDstat | Livestock Ownership – Poultry and Others Livestock Type | 1447 | 27 | 0 |
| F15 | AGSEC7.NSDstat | Livestock Inputs Livestock Input Type | 3871 | 40 | 0 |
| F16 | AGSEC8A.NSDstat | Livestock Production Livestock Product (Meat) | 3871 | 9 | 0 |
| F17 | AGSEC8B.NSDstat |  | 2110 | 14 | 0 |
| F18 | AGSEC8C.NSDstat | Livestock Production Livestock Product (Eggs) | 1279 | 9 | 0 |
| F19 | AGSEC9A.NSDstat | Extension Services Extension Source | 234 | 19 | 1 |
| F20 | AGSEC9B.NSDstat | Extension Services (NAADS) Household level | 2584 | 14 | 0 |

## After Placing Files

Run:

`python script/17_audit_raw_downloads.py; python script/144_build_priority_lsms_isa_raw_package_intake_packet.py; python script/145_build_priority_lsms_isa_archive_member_preflight.py; python script/149_build_priority_lsms_isa_raw_value_verification_workbook.py; python script/150_build_priority_lsms_isa_raw_package_receipt_checklist.py; python script/152_build_priority_lsms_isa_credentialed_raw_acquisition_workbench.py; python script/132_build_priority_analysis_dataset_synthesis_blueprint.py; python script/148_build_priority_lsms_isa_country_wave_promotion_packets.py; python script/151_refresh_refocused_promoted_country_wave_registry.py; python script/127_enforce_promoted_data_gate.py; python script/36_build_direct_read_audit_bundle.py; python script/14_validate_workspace.py`

## Stop Rule

Do not mark receipt, raw-value verification, climate linkage, or analysis
readiness as passed until the complete official package is present and the raw
value workbook evidence fields are filled from original files.
