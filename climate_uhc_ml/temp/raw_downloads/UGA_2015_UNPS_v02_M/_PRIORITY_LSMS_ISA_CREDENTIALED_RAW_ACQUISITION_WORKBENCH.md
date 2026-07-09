# Priority LSMS-ISA Credentialed Raw Acquisition Workbench

Dataset: `UGA_2015_UNPS_v02_M` - Uganda 2015-2016

Official get-microdata URL: https://microdata.worldbank.org/catalog/3460/get-microdata

Target folder: `temp/raw_downloads/UGA_2015_UNPS_v02_M/`

Current receipt status: `blocked_no_original_package`

## Manual Download Action

Open official_get_microdata_url, log in or register if required, accept official terms/Data Access Agreement, download the complete unchanged raw package plus all documentation, and place all files in local_target_folder.

Scope: Download the complete unchanged official World Bank package for this IDNO, including all raw microdata files, archives, documentation, questionnaires, codebooks, DDI/XML, and geography/timing supplements exposed after login.

## Core Files To Confirm After Download

| requirement | file_rank | file_name | candidate_variable_rows | top_variable_names |
|---|---|---|---|---|
| climate_geography | 1 | AGSEC2B | 3 | GPS_Manual;GPS_Not_Captured;Visit_GPS_Parcel |
| climate_geography | 2 | gsec1 | 4 | urban;ea;sregion;h1aq5 |
| climate_geography | 3 | AGSEC1 | 3 | urban;sregion;h1aq5 |
| climate_geography | 4 | pov2015_16 | 2 | regurb;urban |
| consumption_or_income | 1 | pov2015_16 | 10 | cpexp30;nrrexp30;hpline;ctpline;spline;district;equiv;hh;hsize;plinen |
| consumption_or_income | 2 | AGSEC1 | 1 | interview |
| consumption_or_income | 3 | gsec1 | 1 | interview |
| health_need_and_access | 1 | gsec5 | 4 | h5q4;h5q5;h5q8;h5q9 |
| health_need_and_access | 2 | CSEC4B_1 | 3 | C4BQ23;C4BQ19;C4BQ20 |
| health_need_and_access | 3 | CSEC2B_1 | 2 | C2BQ10;C2BQ9 |
| health_need_and_access | 4 | CSEC4A_1 | 2 | C4AQ8;C4Q7 |
| health_need_and_access | 5 | CSEC4M | 1 | End_sup_health |
| household_person_keys | 1 | unps_geovars_2015_16 | 1 | HHID |
| household_person_keys | 2 | gsec2 | 1 | pid |
| household_person_keys | 3 | gsec3 | 1 | pid |
| household_person_keys | 4 | gsec4 | 1 | pid |
| household_person_keys | 5 | gsec5 | 1 | pid |
| household_person_keys | 6 | gsec6_1 | 1 | pid |
| household_person_keys | 7 | gsec6_3 | 1 | pid |
| household_person_keys | 8 | gsec8 | 1 | pid |

## Official File Manifest Preview

| file_id | file_name | file_description | case_quantity | variable_quantity | priority_core_target |
|---|---|---|---|---|---|
| F1 | AGSEC1 | Agriculture round - AGSection 1 data | 2694 | 37 | 1 |
| F2 | AGSEC10 | Agriculture round - AGSection 10 data | 61865 | 14 | 0 |
| F3 | AGSEC11 | Agriculture round - AGSection 11 data | 26900 | 10 | 0 |
| F4 | AGSEC2A | Agriculture round - AGSection 2A data | 4200 | 38 | 0 |
| F5 | AGSEC2AB_1 | Agriculture round - AGSection 2AB_1 data | 2694 | 2 | 0 |
| F6 | AGSEC2B | Agriculture round - AGSection 2B data | 1381 | 35 | 1 |
| F7 | AGSEC3A | Agriculture round - AGSection 3A data | 7787 | 50 | 0 |
| F8 | AGSEC3A_1 | Agriculture round - AGSection 3A_1 data | 2694 | 2 | 0 |
| F9 | AGSEC3B | Agriculture round - AGSection 3B data | 6792 | 52 | 0 |
| F10 | AGSEC3B_1 | Agriculture round - AGSection 3B_1 data | 2694 | 2 | 0 |
| F11 | AGSEC4A | Agriculture round - AGSection 4A data | 10823 | 26 | 0 |
| F12 | AGSEC4A_1 | Agriculture round - AGSection 4A_1 data | 2694 | 2 | 0 |
| F13 | AGSEC4B | Agriculture round - AGSection 4B data | 9691 | 23 | 0 |
| F14 | AGSEC4B_1 | Agriculture round - AGSection 4B_1 data | 2694 | 2 | 0 |
| F15 | AGSEC5A | Agriculture round - AGSection 5A data | 10678 | 46 | 0 |
| F16 | AGSEC5B | Agriculture round - AGSection 5B data | 8971 | 46 | 0 |
| F17 | AGSEC6A | Agriculture round - AGSection 6A data | 32280 | 28 | 0 |
| F18 | AGSEC6A_1 | Agriculture round - AGSection 6A_1 data | 2694 | 5 | 0 |
| F19 | AGSEC6B | Agriculture round - AGSection 6B data | 26900 | 28 | 0 |
| F20 | AGSEC6B_1 | Agriculture round - AGSection 6B_1 data | 2694 | 5 | 0 |

## After Placing Files

Run:

`python script/17_audit_raw_downloads.py; python script/144_build_priority_lsms_isa_raw_package_intake_packet.py; python script/145_build_priority_lsms_isa_archive_member_preflight.py; python script/149_build_priority_lsms_isa_raw_value_verification_workbook.py; python script/150_build_priority_lsms_isa_raw_package_receipt_checklist.py; python script/152_build_priority_lsms_isa_credentialed_raw_acquisition_workbench.py; python script/132_build_priority_analysis_dataset_synthesis_blueprint.py; python script/148_build_priority_lsms_isa_country_wave_promotion_packets.py; python script/151_refresh_refocused_promoted_country_wave_registry.py; python script/127_enforce_promoted_data_gate.py; python script/36_build_direct_read_audit_bundle.py; python script/14_validate_workspace.py`

## Stop Rule

Do not mark receipt, raw-value verification, climate linkage, or analysis
readiness as passed until the complete official package is present and the raw
value workbook evidence fields are filled from original files.
