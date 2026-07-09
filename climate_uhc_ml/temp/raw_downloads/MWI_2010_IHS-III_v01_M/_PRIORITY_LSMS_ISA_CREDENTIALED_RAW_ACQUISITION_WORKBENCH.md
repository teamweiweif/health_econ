# Priority LSMS-ISA Credentialed Raw Acquisition Workbench

Dataset: `MWI_2010_IHS-III_v01_M` - Malawi 2010-2011

Official get-microdata URL: https://microdata.worldbank.org/catalog/1003/get-microdata

Target folder: `temp/raw_downloads/MWI_2010_IHS-III_v01_M/`

Current receipt status: `blocked_no_original_package`

## Manual Download Action

Open official_get_microdata_url, log in or register if required, accept official terms/Data Access Agreement, download the complete unchanged raw package plus all documentation, and place all files in local_target_folder.

Scope: Download the complete unchanged official World Bank package for this IDNO, including all raw microdata files, archives, documentation, questionnaires, codebooks, DDI/XML, and geography/timing supplements exposed after login.

## Core Files To Confirm After Download

| requirement | file_rank | file_name | candidate_variable_rows | top_variable_names |
|---|---|---|---|---|
| climate_geography | 1 | HouseholdGeovariables.NSDstat | 3 | ea_id;lat_modified;lon_modified |
| climate_geography | 2 | PlotGeovariables.NSDstat | 1 | ea_id |
| climate_geography | 3 | HH_MOD_A_FILT.NSDstat | 1 | ea_id |
| climate_geography | 4 | HH_MOD_H.NSDstat | 1 | ea_id |
| climate_geography | 5 | HH_MOD_I1.NSDstat | 1 | ea_id |
| climate_geography | 6 | HH_MOD_I2.NSDstat | 1 | ea_id |
| climate_geography | 7 | HH_MOD_J.NSDstat | 1 | ea_id |
| climate_geography | 8 | HH_MOD_K.NSDstat | 1 | ea_id |
| consumption_or_income | 1 | Round 1 (2010) Consumption Aggregate.NSDstat | 7 | rexp_cat01;rexp_cat011;epoor;pcrexpagg;poor;rexp_cat012;rexp_cat02 |
| consumption_or_income | 2 | ihs3fc2M_consumption.NSDstat | 4 | exp_cat01;exp_cat011;rexp_cat01;rexp_cat011 |
| consumption_or_income | 3 | HH_MOD_T.NSDstat | 1 | hh_t01 |
| health_need_and_access | 1 | COM_CD.NSDstat | 6 | com_cd60a;com_cd60b;com_cd53;com_cd54;com_cd51a;com_cd51b |
| health_need_and_access | 2 | HH_MOD_D.NSDstat | 6 | hh_d04;hh_d05a;hh_d05a_os;hh_d05b;hh_d05b_os;hh_d34a |
| household_person_keys | 1 | HouseholdGeovariables.NSDstat | 1 | case_id |
| household_person_keys | 2 | HH_MOD_A_FILT.NSDstat | 1 | case_id |
| household_person_keys | 3 | HH_MOD_H.NSDstat | 1 | case_id |
| household_person_keys | 4 | HH_MOD_I1.NSDstat | 1 | case_id |
| household_person_keys | 5 | HH_MOD_I2.NSDstat | 1 | case_id |
| household_person_keys | 6 | HH_MOD_J.NSDstat | 1 | case_id |
| household_person_keys | 7 | HH_MOD_K.NSDstat | 1 | case_id |

## Official File Manifest Preview

| file_id | file_name | file_description | case_quantity | variable_quantity | priority_core_target |
|---|---|---|---|---|---|
| F1 | HH_MOD_A_FILT.NSDstat |  | 12271 | 57 | 1 |
| F2 | HH_MOD_B.NSDstat |  | 56409 | 40 | 0 |
| F3 | HH_MOD_C.NSDstat |  | 56218 | 42 | 0 |
| F4 | HH_MOD_D.NSDstat |  | 56218 | 68 | 1 |
| F5 | HH_MOD_E.NSDstat |  | 56218 | 82 | 0 |
| F6 | HH_MOD_F.NSDstat |  | 12271 | 68 | 0 |
| F7 | HH_MOD_G1.NSDstat |  | 1521604 | 19 | 0 |
| F8 | HH_MOD_G2.NSDstat |  | 122710 | 6 | 0 |
| F9 | HH_MOD_G3.NSDstat |  | 23263 | 8 | 0 |
| F10 | HH_MOD_H.NSDstat |  | 12271 | 43 | 1 |
| F11 | HH_MOD_I1.NSDstat |  | 110439 | 6 | 1 |
| F12 | HH_MOD_I2.NSDstat |  | 245420 | 6 | 1 |
| F13 | HH_MOD_J.NSDstat |  | 478569 | 6 | 1 |
| F14 | HH_MOD_K.NSDstat |  | 245420 | 7 | 1 |
| F15 | HH_MOD_L.NSDstat |  | 392672 | 10 | 1 |
| F16 | HH_MOD_M.NSDstat |  | 276396 | 22 | 0 |
| F17 | HH_MOD_N1.NSDstat |  | 12271 | 13 | 0 |
| F18 | HH_MOD_N2.NSDstat |  | 12509 | 112 | 0 |
| F19 | HH_MOD_O.NSDstat |  | 19577 | 27 | 0 |
| F20 | HH_MOD_P.NSDstat |  | 184066 | 12 | 0 |

## After Placing Files

Run:

`python script/17_audit_raw_downloads.py; python script/144_build_priority_lsms_isa_raw_package_intake_packet.py; python script/145_build_priority_lsms_isa_archive_member_preflight.py; python script/149_build_priority_lsms_isa_raw_value_verification_workbook.py; python script/150_build_priority_lsms_isa_raw_package_receipt_checklist.py; python script/152_build_priority_lsms_isa_credentialed_raw_acquisition_workbench.py; python script/153_validate_priority_lsms_isa_official_file_receipt.py; python script/132_build_priority_analysis_dataset_synthesis_blueprint.py; python script/148_build_priority_lsms_isa_country_wave_promotion_packets.py; python script/151_refresh_refocused_promoted_country_wave_registry.py; python script/127_enforce_promoted_data_gate.py; python script/36_build_direct_read_audit_bundle.py; python script/14_validate_workspace.py`

## Stop Rule

Do not mark receipt, raw-value verification, climate linkage, or analysis
readiness as passed until the complete official package is present and the raw
value workbook evidence fields are filled from original files.
