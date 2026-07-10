# Minimum Batch Raw Intake Guide

IDNO: `TZA_2010_NPS-R2_v03_M`

Country-wave: Tanzania 2010-2011

Threshold rank: 8

Role: minimum_10_wave_core

Official World Bank microdata URL: https://microdata.worldbank.org/catalog/1050/get-microdata

Target folder: `temp/raw_downloads/TZA_2010_NPS-R2_v03_M/`

## Current Receipt Status

- Expected full official files: 95
- Matched full official files: 0
- Missing full official files: 95
- Expected core files: 38
- Matched core files: 0
- Missing core files: 38
- Official receipt status: `blocked_no_original_package`

## Core Files To Confirm

| requirement | file_rank | file_id | expected_file_name | top_variable_names | official_core_file_match_status |
|---|---|---|---|---|---|
| climate_geography | 1 | F157 | HH_SEC_A | clusterid;district;ea;hh_a18_year;region;ward | missing_expected_core_file |
| climate_geography | 2 | F130 | TZY2.EA.Offsets | clusterid;rum | missing_expected_core_file |
| climate_geography | 3 | F120 | Plot.Geovariables_Y2 | ea_id | missing_expected_core_file |
| climate_geography | 4 | F187 | TZY1.HH.Consumption | urban | missing_expected_core_file |
| climate_geography | 5 | F188 | TZY2.HH.Consumption | urban | missing_expected_core_file |
| climate_geography | 6 | F189 | HH.Geovariables_Y2 | ea_id | missing_expected_core_file |
| consumption_or_income | 1 | F187 | TZY1.HH.Consumption | hhexpenses;hhexpensesR;expm;expmR | missing_expected_core_file |
| consumption_or_income | 2 | F188 | TZY2.HH.Consumption | hhexpenses;hhexpensesR;expm;expmR | missing_expected_core_file |
| consumption_or_income | 3 | F176 | HH_SEC_L | hh_l01_2;hh_l02;itemcode;y2_hhid | missing_expected_core_file |
| health_need_and_access | 1 | F160 | HH_SEC_D | hh_d12_1;hh_d12_2;hh_d02;hh_d13;hh_d38 | missing_expected_core_file |
| health_need_and_access | 2 | F143 | FS_H2 | costid;costitem | missing_expected_core_file |
| health_need_and_access | 3 | F187 | TZY1.HH.Consumption | health;healthR | missing_expected_core_file |
| health_need_and_access | 4 | F155 | FS_N2 | costid | missing_expected_core_file |
| health_need_and_access | 5 | F165 | HH_SEC_G | hh_g03_5 | missing_expected_core_file |
| health_need_and_access | 6 | F188 | TZY2.HH.Consumption | health | missing_expected_core_file |
| household_person_keys | 1 | F158 | HH_SEC_B | hhid_2008;y2_hhid | missing_expected_core_file |
| household_person_keys | 2 | F115 | AG_SEC10B | y2_hhid | missing_expected_core_file |
| household_person_keys | 3 | F108 | AG_SEC7A | y2_hhid | missing_expected_core_file |
| household_person_keys | 4 | F109 | AG_SEC7B | y2_hhid | missing_expected_core_file |
| household_person_keys | 5 | F188 | TZY2.HH.Consumption | hhid_2008 | missing_expected_core_file |
| household_person_keys | 6 | F146 | FS_J1 | hhid_2008 | missing_expected_core_file |
| household_person_keys | 7 | F148 | FS_J3 | hhid_2008 | missing_expected_core_file |
| household_person_keys | 8 | F132 | FS_C1 | y2_hhid | missing_expected_core_file |
| oop_health_expenditure | 1 | F160 | HH_SEC_D | hh_d05_1;hh_d05_2;hh_d07;hh_d08;hh_d09;hh_d13;hh_d15;hh_d29_1 | missing_expected_core_file |
| survey_timing | 1 | F159 | HH_SEC_C | hh_c08;hh_c10;hh_c30 | missing_expected_core_file |
| survey_timing | 2 | F161 | HH_SEC_E1 | hh_e44;hh_e67;hh_e68 | missing_expected_core_file |
| survey_timing | 3 | F157 | HH_SEC_A | hh_a18_month;hh_a18_year | missing_expected_core_file |
| survey_timing | 4 | F160 | HH_SEC_D | hh_d05_1;hh_d05_2 | missing_expected_core_file |
| survey_timing | 5 | F187 | TZY1.HH.Consumption | intmonth | missing_expected_core_file |
| survey_timing | 6 | F188 | TZY2.HH.Consumption | intmonth | missing_expected_core_file |

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
