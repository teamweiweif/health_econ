# Minimum Batch Raw Intake Guide

IDNO: `UGA_2019_UNPS_v03_M`

Country-wave: Uganda 2019-2020

Threshold rank: 10

Role: minimum_10_wave_core

Official World Bank microdata URL: https://microdata.worldbank.org/catalog/3902/get-microdata

Target folder: `temp/raw_downloads/UGA_2019_UNPS_v03_M/`

## Current Receipt Status

- Expected full official files: 109
- Matched full official files: 0
- Missing full official files: 109
- Expected core files: 39
- Matched core files: 0
- Missing core files: 39
- Official receipt status: `blocked_no_original_package`

## Core Files To Confirm

| requirement | file_rank | file_id | expected_file_name | top_variable_names | official_core_file_match_status |
|---|---|---|---|---|---|
| climate_geography | 1 | F114 | pov2019_20.NSDstat | regurb;urban;district | missing_expected_core_file |
| climate_geography | 2 | F76 | GSEC1.NSDstat | urban | missing_expected_core_file |
| climate_geography | 3 | F23 | CSEC1A.NSDstat | Final_EA_code | missing_expected_core_file |
| climate_geography | 4 | F24 | CSEC2.NSDstat | Final_EA_code | missing_expected_core_file |
| climate_geography | 5 | F25 | CSEC2A.NSDstat | Final_EA_code | missing_expected_core_file |
| climate_geography | 6 | F26 | CSEC2B.NSDstat | Final_EA_code | missing_expected_core_file |
| climate_geography | 7 | F27 | CSEC2C.NSDstat | Final_EA_code | missing_expected_core_file |
| climate_geography | 8 | F28 | CSEC2C_0.NSDstat | Final_EA_code | missing_expected_core_file |
| consumption_or_income | 1 | F98 | GSEC15B.NSDstat | CEB03;CEB04;CEB07;CEB10;CEB11;CEB14a;CEB15;CEB16;coicop_2 | missing_expected_core_file |
| consumption_or_income | 2 | F114 | pov2019_20.NSDstat | cpexp30;nrrexp30;hpline | missing_expected_core_file |
| health_need_and_access | 1 | F26 | CSEC2B.NSDstat | s2bq13__1;s2bq09;s2bq10;s2bq13__2;s2bq13__3;s2bq13__4 | missing_expected_core_file |
| health_need_and_access | 2 | F47 | CSEC4B.NSDstat | s4bq23;s4bq26;s4bq27;s4bq28 | missing_expected_core_file |
| health_need_and_access | 3 | F57 | CSEC4L.NSDstat | Health_Water_id | missing_expected_core_file |
| health_need_and_access | 4 | F82 | GSEC6_1.NSDstat | s6q15b | missing_expected_core_file |
| household_person_keys | 1 | F77 | GSEC2.NSDstat | hhid | missing_expected_core_file |
| household_person_keys | 2 | F100 | GSEC15C.NSDstat | hhid | missing_expected_core_file |
| household_person_keys | 3 | F101 | GSEC15D.NSDstat | hhid | missing_expected_core_file |
| household_person_keys | 4 | F104 | GSEC17_1.NSDstat | hhid | missing_expected_core_file |
| household_person_keys | 5 | F105 | GSEC19.NSDstat | hhid | missing_expected_core_file |
| household_person_keys | 6 | F76 | GSEC1.NSDstat | hhid | missing_expected_core_file |
| household_person_keys | 7 | F87 | GSEC7_1.NSDstat | hhid | missing_expected_core_file |
| household_person_keys | 8 | F88 | GSEC7_2.NSDstat | hhid | missing_expected_core_file |
| oop_health_expenditure | 1 | F81 | GSEC5.NSDstat | h5q12a;h5q12b;h5q12f;h5q12f_1;h5q12g;h5q12c;h5q12d;h5q12e | missing_expected_core_file |
| oop_health_expenditure | 2 | F82 | GSEC6_1.NSDstat | h6q12h;s6q07_1;s6q07_3i | missing_expected_core_file |
| oop_health_expenditure | 3 | F84 | GSEC6_3.NSDstat | t31 | missing_expected_core_file |
| survey_timing | 1 | F95 | GSEC12_2.NSDstat | h12q04;h12q12;h12q13 | missing_expected_core_file |
| survey_timing | 2 | F76 | GSEC1.NSDstat | month;year | missing_expected_core_file |
| survey_timing | 3 | F10 | AGSEC5A.NSDstat | s5aq06f_1;s5aq06f_11;s5aq06f_1_1 | missing_expected_core_file |
| survey_timing | 4 | F77 | GSEC2.NSDstat | h2q9b;h2q9c | missing_expected_core_file |
| survey_timing | 5 | F91 | GSEC9.NSDstat | dwellingVisit | missing_expected_core_file |

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
