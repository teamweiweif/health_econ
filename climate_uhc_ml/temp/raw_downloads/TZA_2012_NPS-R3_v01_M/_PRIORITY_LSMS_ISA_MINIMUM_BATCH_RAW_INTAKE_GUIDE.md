# Minimum Batch Raw Intake Guide

IDNO: `TZA_2012_NPS-R3_v01_M`

Country-wave: Tanzania 2012-2013

Threshold rank: 9

Role: minimum_10_wave_core

Official World Bank microdata URL: https://microdata.worldbank.org/catalog/2252/get-microdata

Target folder: `temp/raw_downloads/TZA_2012_NPS-R3_v01_M/`

## Current Receipt Status

- Expected full official files: 80
- Matched full official files: 0
- Missing full official files: 80
- Expected core files: 33
- Matched core files: 0
- Missing core files: 33
- Official receipt status: `blocked_no_original_package`

## Core Files To Confirm

| requirement | file_rank | file_id | expected_file_name | top_variable_names | official_core_file_match_status |
|---|---|---|---|---|---|
| climate_geography | 1 | F24 | COM_SEC_A1A2.NSDstat | cm_lon_g;cm_lon_m;cm_lon_s;y3_cluster | missing_expected_core_file |
| climate_geography | 2 | F3 | AG_SEC_2A.NSDstat | ag2a_06_3;ag2a_06_4 | missing_expected_core_file |
| climate_geography | 3 | F23 | AG_SEC_A.NSDstat | ag_a04_1;ag_a04_2 | missing_expected_core_file |
| climate_geography | 4 | F34 | HH_SEC_A.NSDstat | hh_a04_1;hh_a04_2 | missing_expected_core_file |
| climate_geography | 5 | F76 | LF_SEC_A.NSDstat | lf_a04_1;lf_a04_2 | missing_expected_core_file |
| consumption_or_income | 1 | F47 | HH_SEC_K.NSDstat | hh_k01;hh_k02;hh_k03;itemcode;occ;y3_hhid | missing_expected_core_file |
| consumption_or_income | 2 | F48 | HH_SEC_L.NSDstat | hh_l01;hh_l02;hh_l03;itemcode;occ;y3_hhid | missing_expected_core_file |
| health_need_and_access | 1 | F37 | HH_SEC_D.NSDstat | hh_d12_1;hh_d12_2;hh_d02;hh_d13;hh_d23 | missing_expected_core_file |
| health_need_and_access | 2 | F32 | ConsumptionNPS3.NSDstat | health;healthR | missing_expected_core_file |
| health_need_and_access | 3 | F75 | LF_SEC_13B.NSDstat | costcode;costname | missing_expected_core_file |
| health_need_and_access | 4 | F40 | HH_SEC_G.NSDstat | hh_g03_5 | missing_expected_core_file |
| health_need_and_access | 5 | F20 | AG_SEC_11.NSDstat | ag11_05 | missing_expected_core_file |
| health_need_and_access | 6 | F25 | COM_SEC_CB.NSDstat | cm_b02 | missing_expected_core_file |
| household_person_keys | 1 | F35 | HH_SEC_B.NSDstat | y2_hhid;y3_hhid | missing_expected_core_file |
| household_person_keys | 2 | F2 | AG_SEC_01.NSDstat | y3_hhid | missing_expected_core_file |
| household_person_keys | 3 | F3 | AG_SEC_2A.NSDstat | y3_hhid | missing_expected_core_file |
| household_person_keys | 4 | F4 | AG_SEC_2B.NSDstat | y3_hhid | missing_expected_core_file |
| household_person_keys | 5 | F60 | LF_NETWORK.NSDstat | y3_hhid | missing_expected_core_file |
| household_person_keys | 6 | F61 | LF_SEC_01.NSDstat | y3_hhid | missing_expected_core_file |
| household_person_keys | 7 | F15 | AG_SEC_08.NSDstat | y3_hhid | missing_expected_core_file |
| household_person_keys | 8 | F20 | AG_SEC_11.NSDstat | y3_hhid | missing_expected_core_file |
| oop_health_expenditure | 1 | F37 | HH_SEC_D.NSDstat | hh_d05_1;hh_d05_2;hh_d07;hh_d08;hh_d09;hh_d13;hh_d15;hh_d20;hh_d01;hh_d02;hh_d03_1;hh_d03_2 | missing_expected_core_file |
| survey_timing | 1 | F34 | HH_SEC_A.NSDstat | hh_a18;hh_a18_1;hh_a18_2;hh_a18_3 | missing_expected_core_file |
| survey_timing | 2 | F24 | COM_SEC_A1A2.NSDstat | cm_a07;cm_a07_1;cm_a07_2;cm_a07_3 | missing_expected_core_file |
| survey_timing | 3 | F23 | AG_SEC_A.NSDstat | ag_a13;ag_a12_1 | missing_expected_core_file |
| survey_timing | 4 | F76 | LF_SEC_A.NSDstat | lf_a13 | missing_expected_core_file |
| survey_timing | 5 | F21 | AG_SEC_12A.NSDstat | ag12a_07 | missing_expected_core_file |
| weights_and_design | 1 | F34 | HH_SEC_A.NSDstat | y3_weight;strataid;hh_a04_1;hh_a04_2 | missing_expected_core_file |
| weights_and_design | 2 | F23 | AG_SEC_A.NSDstat | ag_a04_1;ag_a04_2 | missing_expected_core_file |
| weights_and_design | 3 | F76 | LF_SEC_A.NSDstat | lf_a04_1;lf_a04_2 | missing_expected_core_file |

## Intake Steps

1. Use the official World Bank link above after login, terms, or Data Access Agreement acceptance.
2. Download the complete official package and documentation. Keep original archive names where possible.
3. Place the unchanged package or extracted original files under the target folder.
4. Rerun the post-download commands below.
5. Review raw-value, outcome, timing, geography, and climate-linkage gates before any promotion.

```bash
python script/17_audit_raw_downloads.py; python script/144_build_priority_lsms_isa_raw_package_intake_packet.py; python script/145_build_priority_lsms_isa_archive_member_preflight.py; python script/150_build_priority_lsms_isa_raw_package_receipt_checklist.py; python script/152_build_priority_lsms_isa_credentialed_raw_acquisition_workbench.py; python script/153_validate_priority_lsms_isa_official_file_receipt.py; python script/154_build_priority_lsms_isa_threshold_download_sequence.py; python script/155_build_priority_lsms_isa_minimum_batch_raw_intake_guide.py; python script/149_build_priority_lsms_isa_raw_value_verification_workbook.py; python script/132_build_priority_analysis_dataset_synthesis_blueprint.py; python script/148_build_priority_lsms_isa_country_wave_promotion_packets.py; python script/151_refresh_refocused_promoted_country_wave_registry.py; python script/127_enforce_promoted_data_gate.py; python script/36_build_direct_read_audit_bundle.py; python script/14_validate_workspace.py
```

## Stop Rule

Do not write this country-wave into data/ or run ML until complete official file receipt, raw-value verification, outcome construction, survey timing/geography, and accepted CHIRPS or ERA5 climate linkage all pass.
