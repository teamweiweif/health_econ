# Priority LSMS/ISA Post-Download Receipt Handoff

Status: direct-read post-download handoff for the 10 locked World Bank LSMS/ISA
packages.

This artifact starts where the manual download launchpad stops. It tells the
reviewer what receipt and requirement gates must pass after a complete official
raw package is placed in the target folder. It does not download, copy, delete,
extract, write `data/`, or promote country-waves.

## Summary

| metric | value | interpretation |
| --- | --- | --- |
| post_download_receipt_handoff_rows | 10 | Post-download receipt handoff rows for locked download-required waves. |
| post_download_receipt_country_rows | 5 | Countries covered by the post-download handoff. |
| post_download_receipt_priority_country_rows | 9 | Rows from priority countries. |
| post_download_receipt_sixth_country_rows | 1 | Rows supplying the sixth country. |
| post_download_receipt_expected_file_rows | 838 | Expected official file rows across handoff targets. |
| post_download_receipt_missing_expected_file_rows | 838 | Expected official file rows currently missing. |
| post_download_receipt_requirement_gate_rows | 70 | Requirement-level gates exported for direct review. |
| post_download_receipt_blocked_requirement_rows | 70 | Requirement gates blocked by missing core files. |
| post_download_receipt_ready_requirement_rows | 0 | Requirement gates whose core files are present. |
| post_download_receipt_expected_core_file_rows | 323 | Requirement-linked core file rows in the handoff. |
| post_download_receipt_missing_core_file_rows | 323 | Requirement-linked core file rows currently missing. |
| post_download_receipt_target_file_rows | 0 | Files currently present under exact target folders. |
| post_download_receipt_incoming_file_rows | 0 | Files currently staged under temp/raw_downloads/_incoming. |
| post_download_receipt_blocked_no_target_files_rows | 10 | Handoff rows still blocked because target folders contain no files. |
| data_write_gate_status | blocked_no_data_write | The handoff does not write promoted data. |
| modeling_gate_status | blocked | No predictive, reduced-form, causal ML, or policy learning is opened. |

## Handoff Rows

| download_rank | country | wave | idno | post_download_receipt_status | expected_file_rows | missing_expected_file_rows | requirement_gate_rows | blocked_requirement_rows |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Ethiopia | 2021-2022 | ETH_2021_ESPS-W5_v02_M | blocked_no_target_files | 68 | 68 | 7 | 7 |
| 2 | Ethiopia | 2018-2019 | ETH_2018_ESS_v04_M | blocked_no_target_files | 68 | 68 | 7 | 7 |
| 3 | Nigeria | 2012-2013 | NGA_2012_GHSP-W2_v02_M | blocked_no_target_files | 103 | 103 | 7 | 7 |
| 4 | Nigeria | 2015-2016 | NGA_2015_GHSP-W3_v02_M | blocked_no_target_files | 104 | 104 | 7 | 7 |
| 5 | Nigeria | 2010-2011 | NGA_2010_GHSP-W1_v03_M | blocked_no_target_files | 99 | 99 | 7 | 7 |
| 6 | Tanzania | 2008-2009 | TZA_2008_NPS-R1_v03_M | blocked_no_target_files | 61 | 61 | 7 | 7 |
| 7 | Tanzania | 2010-2011 | TZA_2010_NPS-R2_v03_M | blocked_no_target_files | 95 | 95 | 7 | 7 |
| 8 | Tanzania | 2012-2013 | TZA_2012_NPS-R3_v01_M | blocked_no_target_files | 80 | 80 | 7 | 7 |
| 9 | Uganda | 2019-2020 | UGA_2019_UNPS_v03_M | blocked_no_target_files | 109 | 109 | 7 | 7 |
| 10 | Nepal | 2010-2011 | NPL_2010_LSS-III_v01_M | blocked_no_target_files | 51 | 51 | 7 | 7 |

## Requirement Gate Preview

| download_rank | idno | requirement | core_file_rows | core_missing_file_rows | requirement_acceptance_status |
| --- | --- | --- | --- | --- | --- |
| 1 | ETH_2021_ESPS-W5_v02_M | climate_geography | 6 | 6 | blocked_missing_core_files |
| 1 | ETH_2021_ESPS-W5_v02_M | consumption_or_income | 1 | 1 | blocked_missing_core_files |
| 1 | ETH_2021_ESPS-W5_v02_M | health_need_and_access | 3 | 3 | blocked_missing_core_files |
| 1 | ETH_2021_ESPS-W5_v02_M | household_person_keys | 8 | 8 | blocked_missing_core_files |
| 1 | ETH_2021_ESPS-W5_v02_M | oop_health_expenditure | 2 | 2 | blocked_missing_core_files |
| 1 | ETH_2021_ESPS-W5_v02_M | survey_timing | 8 | 8 | blocked_missing_core_files |
| 1 | ETH_2021_ESPS-W5_v02_M | weights_and_design | 8 | 8 | blocked_missing_core_files |
| 2 | ETH_2018_ESS_v04_M | climate_geography | 6 | 6 | blocked_missing_core_files |
| 2 | ETH_2018_ESS_v04_M | consumption_or_income | 2 | 2 | blocked_missing_core_files |
| 2 | ETH_2018_ESS_v04_M | health_need_and_access | 2 | 2 | blocked_missing_core_files |
| 2 | ETH_2018_ESS_v04_M | household_person_keys | 8 | 8 | blocked_missing_core_files |
| 2 | ETH_2018_ESS_v04_M | oop_health_expenditure | 2 | 2 | blocked_missing_core_files |
| 2 | ETH_2018_ESS_v04_M | survey_timing | 7 | 7 | blocked_missing_core_files |
| 2 | ETH_2018_ESS_v04_M | weights_and_design | 8 | 8 | blocked_missing_core_files |
| 3 | NGA_2012_GHSP-W2_v02_M | climate_geography | 5 | 5 | blocked_missing_core_files |
| 3 | NGA_2012_GHSP-W2_v02_M | consumption_or_income | 4 | 4 | blocked_missing_core_files |
| 3 | NGA_2012_GHSP-W2_v02_M | health_need_and_access | 3 | 3 | blocked_missing_core_files |
| 3 | NGA_2012_GHSP-W2_v02_M | household_person_keys | 8 | 8 | blocked_missing_core_files |
| 3 | NGA_2012_GHSP-W2_v02_M | oop_health_expenditure | 1 | 1 | blocked_missing_core_files |
| 3 | NGA_2012_GHSP-W2_v02_M | survey_timing | 1 | 1 | blocked_missing_core_files |
| 3 | NGA_2012_GHSP-W2_v02_M | weights_and_design | 4 | 4 | blocked_missing_core_files |
| 4 | NGA_2015_GHSP-W3_v02_M | climate_geography | 6 | 6 | blocked_missing_core_files |
| 4 | NGA_2015_GHSP-W3_v02_M | consumption_or_income | 3 | 3 | blocked_missing_core_files |
| 4 | NGA_2015_GHSP-W3_v02_M | health_need_and_access | 2 | 2 | blocked_missing_core_files |
| 4 | NGA_2015_GHSP-W3_v02_M | household_person_keys | 8 | 8 | blocked_missing_core_files |
| 4 | NGA_2015_GHSP-W3_v02_M | oop_health_expenditure | 1 | 1 | blocked_missing_core_files |
| 4 | NGA_2015_GHSP-W3_v02_M | survey_timing | 1 | 1 | blocked_missing_core_files |
| 4 | NGA_2015_GHSP-W3_v02_M | weights_and_design | 5 | 5 | blocked_missing_core_files |
| 5 | NGA_2010_GHSP-W1_v03_M | climate_geography | 3 | 3 | blocked_missing_core_files |
| 5 | NGA_2010_GHSP-W1_v03_M | consumption_or_income | 2 | 2 | blocked_missing_core_files |
| 5 | NGA_2010_GHSP-W1_v03_M | health_need_and_access | 3 | 3 | blocked_missing_core_files |
| 5 | NGA_2010_GHSP-W1_v03_M | household_person_keys | 8 | 8 | blocked_missing_core_files |
| 5 | NGA_2010_GHSP-W1_v03_M | oop_health_expenditure | 1 | 1 | blocked_missing_core_files |
| 5 | NGA_2010_GHSP-W1_v03_M | survey_timing | 2 | 2 | blocked_missing_core_files |
| 5 | NGA_2010_GHSP-W1_v03_M | weights_and_design | 8 | 8 | blocked_missing_core_files |
| 6 | TZA_2008_NPS-R1_v03_M | climate_geography | 8 | 8 | blocked_missing_core_files |
| 6 | TZA_2008_NPS-R1_v03_M | consumption_or_income | 3 | 3 | blocked_missing_core_files |
| 6 | TZA_2008_NPS-R1_v03_M | health_need_and_access | 2 | 2 | blocked_missing_core_files |
| 6 | TZA_2008_NPS-R1_v03_M | household_person_keys | 8 | 8 | blocked_missing_core_files |
| 6 | TZA_2008_NPS-R1_v03_M | oop_health_expenditure | 2 | 2 | blocked_missing_core_files |
| 6 | TZA_2008_NPS-R1_v03_M | survey_timing | 5 | 5 | blocked_missing_core_files |
| 6 | TZA_2008_NPS-R1_v03_M | weights_and_design | 7 | 7 | blocked_missing_core_files |
| 7 | TZA_2010_NPS-R2_v03_M | climate_geography | 6 | 6 | blocked_missing_core_files |
| 7 | TZA_2010_NPS-R2_v03_M | consumption_or_income | 3 | 3 | blocked_missing_core_files |
| 7 | TZA_2010_NPS-R2_v03_M | health_need_and_access | 6 | 6 | blocked_missing_core_files |
| 7 | TZA_2010_NPS-R2_v03_M | household_person_keys | 8 | 8 | blocked_missing_core_files |
| 7 | TZA_2010_NPS-R2_v03_M | oop_health_expenditure | 1 | 1 | blocked_missing_core_files |
| 7 | TZA_2010_NPS-R2_v03_M | survey_timing | 6 | 6 | blocked_missing_core_files |
| 7 | TZA_2010_NPS-R2_v03_M | weights_and_design | 8 | 8 | blocked_missing_core_files |
| 8 | TZA_2012_NPS-R3_v01_M | climate_geography | 5 | 5 | blocked_missing_core_files |
| ... | ... | ... | ... | ... | ... |

## Stop Rule

Receipt handoff completion is not promotion. A country-wave can only enter
`data/` after the official package receipt, raw schema, raw value, semantics,
timing/geography, climate-linkage, and country-wave promotion-packet gates all
pass.
