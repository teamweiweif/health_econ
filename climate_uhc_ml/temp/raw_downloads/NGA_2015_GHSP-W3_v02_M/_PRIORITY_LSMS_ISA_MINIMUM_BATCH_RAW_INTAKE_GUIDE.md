# Minimum Batch Raw Intake Guide

IDNO: `NGA_2015_GHSP-W3_v02_M`

Country-wave: Nigeria 2015-2016

Threshold rank: 5

Role: minimum_10_wave_core

Official World Bank microdata URL: https://microdata.worldbank.org/catalog/2734/get-microdata

Target folder: `temp/raw_downloads/NGA_2015_GHSP-W3_v02_M/`

## Current Receipt Status

- Expected full official files: 104
- Matched full official files: 0
- Missing full official files: 104
- Expected core files: 26
- Matched core files: 0
- Missing core files: 26
- Official receipt status: `blocked_no_original_package`

## Core Files To Confirm

| requirement | file_rank | file_id | expected_file_name | top_variable_names | official_core_file_match_status |
|---|---|---|---|---|---|
| climate_geography | 1 | F40 | sect1_harvestw3 | s1q31a;s1q31b;s1q31c;s1q31d | missing_expected_core_file |
| climate_geography | 2 | F97 | NGA_HouseholdGeovars_Y3 | LAT_DD_MOD;LON_DD_MOD | missing_expected_core_file |
| climate_geography | 3 | F104 | sectc1_harvestw3 | ea;lga | missing_expected_core_file |
| climate_geography | 4 | F109 | sectc2_harvestw3 | ea;lga | missing_expected_core_file |
| climate_geography | 5 | F113 | cons_agg_wave3_visit1 | ea | missing_expected_core_file |
| climate_geography | 6 | F114 | cons_agg_wave3_visit2 | ea | missing_expected_core_file |
| consumption_or_income | 1 | F113 | cons_agg_wave3_visit1 | totcons;nfdfoth;fdfishpr;fdothpr;fdrestby | missing_expected_core_file |
| consumption_or_income | 2 | F114 | cons_agg_wave3_visit2 | totcons;nfdfoth;fdfishpr;fdothpr;fdrestby | missing_expected_core_file |
| consumption_or_income | 3 | F12 | sect8a_plantingw3 | ea;hhid | missing_expected_core_file |
| health_need_and_access | 1 | F43 | sect4a_harvestw3 | s4aq15;s4aq16;s4aq17;s4aq1;s4aq6a;s4aq6a_os;s4aq6b;s4aq6b_os;s4aq3;s4aq3b;s4aq3b_os | missing_expected_core_file |
| health_need_and_access | 2 | F3 | sect3_plantingw3 | s3q9b | missing_expected_core_file |
| household_person_keys | 1 | F19 | sect11a_plantingw3 | hhid | missing_expected_core_file |
| household_person_keys | 2 | F2 | sect1_plantingw3 | hhid | missing_expected_core_file |
| household_person_keys | 3 | F20 | sect11a1_plantingw3 | hhid | missing_expected_core_file |
| household_person_keys | 4 | F30 | sect12_plantingw3 | hhid | missing_expected_core_file |
| household_person_keys | 5 | F40 | sect1_harvestw3 | hhid | missing_expected_core_file |
| household_person_keys | 6 | F81 | secta10_harvestw3 | hhid | missing_expected_core_file |
| household_person_keys | 7 | F10 | sect7a_plantingw3 | hhid | missing_expected_core_file |
| household_person_keys | 8 | F107 | sect7b_plantingw3 | hhid | missing_expected_core_file |
| oop_health_expenditure | 1 | F43 | sect4a_harvestw3 | s4aq20;s4aq20b;s4aq13;s4aq35a;s4aq35b;s4aq35c | missing_expected_core_file |
| survey_timing | 1 | F115 | secta_harvestw3 | saq14ah;saq14am;saq14bh;saq14bm;saq17ah;saq17am;saq17bh;saq17bm;saq20ah;saq20am;saq20bh;saq20bm | missing_expected_core_file |
| weights_and_design | 1 | F110 | HHTrack | wt_combined;wt_w1_w2_w3;wt_w1_w3;wt_w1v1;wt_w1v2;wt_w2_w3 | missing_expected_core_file |
| weights_and_design | 2 | F113 | cons_agg_wave3_visit1 | ea;hhweight | missing_expected_core_file |
| weights_and_design | 3 | F114 | cons_agg_wave3_visit2 | ea;hhweight | missing_expected_core_file |
| weights_and_design | 4 | F104 | sectc1_harvestw3 | ea | missing_expected_core_file |
| weights_and_design | 5 | F109 | sectc2_harvestw3 | ea | missing_expected_core_file |

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
