# Minimum Batch Raw Intake Guide

IDNO: `NPL_2010_LSS-III_v01_M`

Country-wave: Nepal 2010-2011

Threshold rank: 11

Role: minimum_6th_country_financial_protection_candidate

Official World Bank microdata URL: https://microdata.worldbank.org/catalog/1000/get-microdata

Target folder: `temp/raw_downloads/NPL_2010_LSS-III_v01_M/`

## Current Receipt Status

- Expected full official files: 51
- Matched full official files: 0
- Missing full official files: 51
- Expected core files: 28
- Matched core files: 0
- Missing core files: 28
- Official receipt status: `blocked_no_original_package`

## Core Files To Confirm

| requirement | file_rank | file_id | expected_file_name | top_variable_names | official_core_file_match_status |
|---|---|---|---|---|---|
| climate_geography | 1 | F52 | S00 | v00_zone;v00_headn;v00_team;v00_ward | missing_expected_core_file |
| climate_geography | 2 | F2 | FINAL_PREF | district;district_name;Eastern;HEAD___ | missing_expected_core_file |
| climate_geography | 3 | F7 | S04 | v04_03b;v04_11b | missing_expected_core_file |
| climate_geography | 4 | F4 | S01 | v01_05b | missing_expected_core_file |
| climate_geography | 5 | F48 | S21 | v21_ward | missing_expected_core_file |
| consumption_or_income | 1 | F2 | FINAL_PREF | sh_nonfood_30;sh_nonfood_7;nonfood_30;nonfood_7;nonfood_pc_30;nonfood_pc_7;nonfood_pc_7_tadj;nfood | missing_expected_core_file |
| consumption_or_income | 2 | F10 | S06B | v06b_idc;v06b_itm | missing_expected_core_file |
| consumption_or_income | 3 | F9 | S06A | v06a_idc;v06a_itm | missing_expected_core_file |
| health_need_and_access | 1 | F14 | S08 | v08_12;v08_17b;v08_14;v08_16;v08_17a;v08_17c | missing_expected_core_file |
| health_need_and_access | 2 | F46 | S19 | v19_09;v19_05 | missing_expected_core_file |
| health_need_and_access | 3 | F16 | S09B | v09_18;v09_24 | missing_expected_core_file |
| health_need_and_access | 4 | F6 | S03 | v03_03a;v03_03b | missing_expected_core_file |
| household_person_keys | 1 | F4 | S01 | v01_10;REC_TYPE;v01_01;v01_02;v01_03;v01_04;v01_05a;v01_05b | missing_expected_core_file |
| household_person_keys | 2 | F49 | S21x | v21_10;v21_11 | missing_expected_core_file |
| household_person_keys | 3 | F20 | S10B | v10_02 | missing_expected_core_file |
| household_person_keys | 4 | F22 | S12 | v12_01 | missing_expected_core_file |
| oop_health_expenditure | 1 | F14 | S08 | v08_17a;v08_07a;v08_07b;v08_17b;v08_18;v08_17c | missing_expected_core_file |
| survey_timing | 1 | F52 | S00 | v00_int1_m;v00_int1_y;v00_int2_m;v00_int2_y;v00_int3_m;v00_int3_y;v00_sup_m | missing_expected_core_file |
| survey_timing | 2 | F51 | sys | hsys_c1date;hsys_u1date;hsys_c2date;hsys_u2date | missing_expected_core_file |
| survey_timing | 3 | F2 | FINAL_PREF | Date | missing_expected_core_file |
| weights_and_design | 1 | F1 | anthro | weight | missing_expected_core_file |
| weights_and_design | 2 | F10 | S06B | xhpsu | missing_expected_core_file |
| weights_and_design | 3 | F11 | S06C | xhpsu | missing_expected_core_file |
| weights_and_design | 4 | F12 | S06D | xhpsu | missing_expected_core_file |
| weights_and_design | 5 | F18 | S09D | xhpsu | missing_expected_core_file |
| weights_and_design | 6 | F39 | S15D | xhpsu | missing_expected_core_file |
| weights_and_design | 7 | F4 | S01 | xhpsu | missing_expected_core_file |
| weights_and_design | 8 | F48 | S21 | xhpsu | missing_expected_core_file |

## Intake Steps

1. Use the official World Bank link above after login, terms, or Data Access Agreement acceptance.
2. Download the complete official package and documentation. Keep original archive names where possible.
3. Place the unchanged package or extracted original files under the target folder.
4. Rerun the post-download commands below.
5. Review raw-value, outcome, timing, geography, and climate-linkage gates before any promotion.

```bash
python script/17_audit_raw_downloads.py; python script/144_build_priority_lsms_isa_raw_package_intake_packet.py; python script/145_build_priority_lsms_isa_archive_member_preflight.py; python script/150_build_priority_lsms_isa_raw_package_receipt_checklist.py; python script/152_build_priority_lsms_isa_credentialed_raw_acquisition_workbench.py; python script/153_validate_priority_lsms_isa_official_file_receipt.py; python script/154_build_priority_lsms_isa_threshold_download_sequence.py; python script/155_build_priority_lsms_isa_minimum_batch_raw_intake_guide.py; python script/156_probe_priority_lsms_isa_minimum_batch_endpoint_refresh.py; python script/149_build_priority_lsms_isa_raw_value_verification_workbook.py; python script/132_build_priority_analysis_dataset_synthesis_blueprint.py; python script/148_build_priority_lsms_isa_country_wave_promotion_packets.py; python script/151_refresh_refocused_promoted_country_wave_registry.py; python script/127_enforce_promoted_data_gate.py; python script/36_build_direct_read_audit_bundle.py; python script/14_validate_workspace.py
```

## Stop Rule

Do not write this country-wave into data/ or run ML until complete official file receipt, raw-value verification, outcome construction, survey timing/geography, and accepted CHIRPS or ERA5 climate linkage all pass.
