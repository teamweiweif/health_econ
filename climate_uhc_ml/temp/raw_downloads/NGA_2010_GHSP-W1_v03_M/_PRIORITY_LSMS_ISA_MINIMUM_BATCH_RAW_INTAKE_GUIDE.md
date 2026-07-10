# Minimum Batch Raw Intake Guide

IDNO: `NGA_2010_GHSP-W1_v03_M`

Country-wave: Nigeria 2010-2011

Threshold rank: 6

Role: minimum_10_wave_core

Official World Bank microdata URL: https://microdata.worldbank.org/catalog/1002/get-microdata

Target folder: `temp/raw_downloads/NGA_2010_GHSP-W1_v03_M/`

## Current Receipt Status

- Expected full official files: 99
- Matched full official files: 0
- Missing full official files: 99
- Expected core files: 27
- Matched core files: 0
- Missing core files: 27
- Official receipt status: `blocked_no_original_package`

## Core Files To Confirm

| requirement | file_rank | file_id | expected_file_name | top_variable_names | official_core_file_match_status |
|---|---|---|---|---|---|
| climate_geography | 1 | F2 | NGA_HouseholdGeovariables_Y1 | lat_dd_mod;lon_dd_mod;ea;eviarea_avg;grn_avg;h2010_eviarea;h2010_grn;h2010_sen;lga;sen_avg | missing_expected_core_file |
| climate_geography | 2 | F98 | cons_agg_wave1_visit1 | ea | missing_expected_core_file |
| climate_geography | 3 | F99 | cons_agg_wave1_visit2 | ea | missing_expected_core_file |
| consumption_or_income | 1 | F98 | cons_agg_wave1_visit1 | totcons;nfdfoth;fdfishpr;fdothpr;fdrestby;fdalcpr;fdbeanpr | missing_expected_core_file |
| consumption_or_income | 2 | F99 | cons_agg_wave1_visit2 | totcons;nfdfoth;fdfishpr;fdothpr;fdrestby | missing_expected_core_file |
| health_need_and_access | 1 | F34 | sect4a_harvestw1 | s4aq15;s4aq16;s4aq17;s4aq1;s4aq3;s4aq6a;s4aq6b;s4aq6c;s4aq20;s4aq20b | missing_expected_core_file |
| health_need_and_access | 2 | F35 | sect4b_harvestw1 | s4bq3 | missing_expected_core_file |
| health_need_and_access | 3 | F32 | sect3a_harvestw1 | s3aq17 | missing_expected_core_file |
| household_person_keys | 1 | F10 | secta7_harvestw1 | hhid | missing_expected_core_file |
| household_person_keys | 2 | F11 | secta8_harvestw1 | hhid | missing_expected_core_file |
| household_person_keys | 3 | F12 | secta9a1_harvestw1 | hhid | missing_expected_core_file |
| household_person_keys | 4 | F13 | secta9a2_harvestw1 | hhid | missing_expected_core_file |
| household_person_keys | 5 | F14 | secta9b1_harvestw1 | hhid | missing_expected_core_file |
| household_person_keys | 6 | F15 | secta9b2_harvestw1 | hhid | missing_expected_core_file |
| household_person_keys | 7 | F16 | secta10_harvestw1 | hhid | missing_expected_core_file |
| household_person_keys | 8 | F17 | secta41_harvestw1 | hhid | missing_expected_core_file |
| oop_health_expenditure | 1 | F34 | sect4a_harvestw1 | s4aq20;s4aq20b;s4aq19;s4aq13;s4aq17 | missing_expected_core_file |
| survey_timing | 1 | F57 | secta_harvestw1 | saq14ah;saq14am;saq14bh;saq14bm;saq18ah;saq18am;saq18bh;saq18bm;saq22ah;saq22am;saq22bh | missing_expected_core_file |
| survey_timing | 2 | F73 | sectc_plantingw1 | interview_date | missing_expected_core_file |
| weights_and_design | 1 | F98 | cons_agg_wave1_visit1 | ea;hhweight | missing_expected_core_file |
| weights_and_design | 2 | F99 | cons_agg_wave1_visit2 | ea;hhweight | missing_expected_core_file |
| weights_and_design | 3 | F2 | NGA_HouseholdGeovariables_Y1 | ea;eviarea_avg;h2010_eviarea | missing_expected_core_file |
| weights_and_design | 4 | F10 | secta7_harvestw1 | ea | missing_expected_core_file |
| weights_and_design | 5 | F11 | secta8_harvestw1 | ea | missing_expected_core_file |
| weights_and_design | 6 | F12 | secta9a1_harvestw1 | ea | missing_expected_core_file |
| weights_and_design | 7 | F13 | secta9a2_harvestw1 | ea | missing_expected_core_file |
| weights_and_design | 8 | F14 | secta9b1_harvestw1 | ea | missing_expected_core_file |

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
