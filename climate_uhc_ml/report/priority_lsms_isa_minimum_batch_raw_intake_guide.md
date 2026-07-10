# Priority LSMS-ISA Minimum Batch Raw Intake Guide

Status: actionable intake guide for the 11 country-waves in the minimum
threshold batch. This is a post-download handoff, not a raw-data download and
not an analysis dataset.

It narrows the current acquisition burden to the smallest set that could
reach the pre-modeling thresholds if every row later passes raw receipt,
raw-value, outcome, timing, geography, and climate-linkage gates.

## Summary

| Metric | Value | Interpretation |
|---|---:|---|
| priority_lsms_minimum_batch_country_wave_rows | 11 | Minimum batch country-waves requiring complete official raw package intake. |
| priority_lsms_minimum_batch_country_rows | 6 | Countries represented in the minimum threshold batch. |
| priority_lsms_minimum_batch_expected_full_file_rows | 890 | Official DDI file rows expected across the minimum batch. |
| priority_lsms_minimum_batch_matched_full_file_rows | 0 | Expected full official files currently matched locally. |
| priority_lsms_minimum_batch_missing_full_file_rows | 890 | Expected full official files still missing locally. |
| priority_lsms_minimum_batch_expected_core_file_rows | 360 | Core requirement-linked official files expected across the minimum batch. |
| priority_lsms_minimum_batch_matched_core_file_rows | 0 | Core requirement-linked official files currently matched locally. |
| priority_lsms_minimum_batch_missing_core_file_rows | 360 | Core requirement-linked official files still missing locally. |
| priority_lsms_minimum_batch_expected_manifest_rows | 890 | Rows written to the minimum-batch expected full-file manifest. |
| priority_lsms_minimum_batch_core_manifest_rows | 360 | Rows written to the minimum-batch core-file manifest. |
| priority_lsms_minimum_batch_handoff_readmes_written | 11 | Per-wave raw intake guides written under temp/raw_downloads. |
| priority_lsms_minimum_batch_data_write_status | blocked_no_value_verified_raw_packages | The minimum-batch intake guide never writes promoted data. |
| modeling_gate_status | blocked | Models remain blocked until 6 countries, 10 country-waves, and accepted CHIRPS/ERA5 linkage are value-verified. |
| priority_lsms_minimum_batch_receipt_status_blocked_no_original_package | 11 | Minimum batch rows by current official file receipt status. |

## Minimum Batch Intake Rows

| threshold_sequence_rank | threshold_download_role | country | wave | idno | expected_full_file_rows | missing_full_file_rows | expected_core_file_rows | missing_core_file_rows | official_file_receipt_status |
|---|---|---|---|---|---|---|---|---|---|
| 1 | minimum_10_wave_core | Ethiopia | 2021-2022 | ETH_2021_ESPS-W5_v02_M | 68 | 68 | 36 | 36 | blocked_no_original_package |
| 2 | minimum_10_wave_core | Ethiopia | 2018-2019 | ETH_2018_ESS_v04_M | 68 | 68 | 35 | 35 | blocked_no_original_package |
| 3 | minimum_10_wave_core | Malawi | 2004-2005 | MWI_2004_IHS-II_v01_M | 52 | 52 | 37 | 37 | blocked_no_original_package |
| 4 | minimum_10_wave_core | Nigeria | 2012-2013 | NGA_2012_GHSP-W2_v02_M | 103 | 103 | 26 | 26 | blocked_no_original_package |
| 5 | minimum_10_wave_core | Nigeria | 2015-2016 | NGA_2015_GHSP-W3_v02_M | 104 | 104 | 26 | 26 | blocked_no_original_package |
| 6 | minimum_10_wave_core | Nigeria | 2010-2011 | NGA_2010_GHSP-W1_v03_M | 99 | 99 | 27 | 27 | blocked_no_original_package |
| 7 | minimum_10_wave_core | Tanzania | 2008-2009 | TZA_2008_NPS-R1_v03_M | 61 | 61 | 35 | 35 | blocked_no_original_package |
| 8 | minimum_10_wave_core | Tanzania | 2010-2011 | TZA_2010_NPS-R2_v03_M | 95 | 95 | 38 | 38 | blocked_no_original_package |
| 9 | minimum_10_wave_core | Tanzania | 2012-2013 | TZA_2012_NPS-R3_v01_M | 80 | 80 | 33 | 33 | blocked_no_original_package |
| 10 | minimum_10_wave_core | Uganda | 2019-2020 | UGA_2019_UNPS_v03_M | 109 | 109 | 39 | 39 | blocked_no_original_package |
| 11 | minimum_6th_country_financial_protection_candidate | Nepal | 2010-2011 | NPL_2010_LSS-III_v01_M | 51 | 51 | 28 | 28 | blocked_no_original_package |

## Core File Manifest Preview

| threshold_sequence_rank | country | wave | idno | requirement | file_id | expected_file_name | official_core_file_match_status |
|---|---|---|---|---|---|---|---|
| 1 | Ethiopia | 2021-2022 | ETH_2021_ESPS-W5_v02_M | climate_geography | F1 | sect_cover_hh_w5.dta | missing_expected_core_file |
| 1 | Ethiopia | 2021-2022 | ETH_2021_ESPS-W5_v02_M | climate_geography | F42 | sect10a_com_w5.dta | missing_expected_core_file |
| 1 | Ethiopia | 2021-2022 | ETH_2021_ESPS-W5_v02_M | climate_geography | F46 | sect_cover_pp_w5.dta | missing_expected_core_file |
| 1 | Ethiopia | 2021-2022 | ETH_2021_ESPS-W5_v02_M | climate_geography | F54 | sect_cover_ph_w5.dta | missing_expected_core_file |
| 1 | Ethiopia | 2021-2022 | ETH_2021_ESPS-W5_v02_M | climate_geography | F59 | sect_cover_ls_w5.dta | missing_expected_core_file |
| 1 | Ethiopia | 2021-2022 | ETH_2021_ESPS-W5_v02_M | climate_geography | F49 | sect3_pp_w5.dta | missing_expected_core_file |
| 1 | Ethiopia | 2021-2022 | ETH_2021_ESPS-W5_v02_M | consumption_or_income | F66 | cons_agg_w5.dta | missing_expected_core_file |
| 1 | Ethiopia | 2021-2022 | ETH_2021_ESPS-W5_v02_M | health_need_and_access | F4 | sect3_hh_w5.dta | missing_expected_core_file |
| 1 | Ethiopia | 2021-2022 | ETH_2021_ESPS-W5_v02_M | health_need_and_access | F36 | sect04_com_w5.dta | missing_expected_core_file |
| 1 | Ethiopia | 2021-2022 | ETH_2021_ESPS-W5_v02_M | health_need_and_access | F49 | sect3_pp_w5.dta | missing_expected_core_file |
| 1 | Ethiopia | 2021-2022 | ETH_2021_ESPS-W5_v02_M | household_person_keys | F2 | sect1_hh_w5.dta | missing_expected_core_file |
| 1 | Ethiopia | 2021-2022 | ETH_2021_ESPS-W5_v02_M | household_person_keys | F21 | sect12b1_hh_w5.dta | missing_expected_core_file |
| 1 | Ethiopia | 2021-2022 | ETH_2021_ESPS-W5_v02_M | household_person_keys | F47 | sect1_pp_w5.dta | missing_expected_core_file |
| 1 | Ethiopia | 2021-2022 | ETH_2021_ESPS-W5_v02_M | household_person_keys | F55 | sect1_ph_w5.dta | missing_expected_core_file |
| 1 | Ethiopia | 2021-2022 | ETH_2021_ESPS-W5_v02_M | household_person_keys | F48 | sect2_pp_w5.dta | missing_expected_core_file |
| 1 | Ethiopia | 2021-2022 | ETH_2021_ESPS-W5_v02_M | household_person_keys | F49 | sect3_pp_w5.dta | missing_expected_core_file |
| 1 | Ethiopia | 2021-2022 | ETH_2021_ESPS-W5_v02_M | household_person_keys | F50 | sect4_pp_w5.dta | missing_expected_core_file |
| 1 | Ethiopia | 2021-2022 | ETH_2021_ESPS-W5_v02_M | household_person_keys | F13 | sect6c_hh_w5.dta | missing_expected_core_file |
| 1 | Ethiopia | 2021-2022 | ETH_2021_ESPS-W5_v02_M | oop_health_expenditure | F62 | sect8_3_ls_w5.dta | missing_expected_core_file |
| 1 | Ethiopia | 2021-2022 | ETH_2021_ESPS-W5_v02_M | oop_health_expenditure | F4 | sect3_hh_w5.dta | missing_expected_core_file |
| 1 | Ethiopia | 2021-2022 | ETH_2021_ESPS-W5_v02_M | survey_timing | F46 | sect_cover_pp_w5.dta | missing_expected_core_file |
| 1 | Ethiopia | 2021-2022 | ETH_2021_ESPS-W5_v02_M | survey_timing | F54 | sect_cover_ph_w5.dta | missing_expected_core_file |
| 1 | Ethiopia | 2021-2022 | ETH_2021_ESPS-W5_v02_M | survey_timing | F59 | sect_cover_ls_w5.dta | missing_expected_core_file |
| 1 | Ethiopia | 2021-2022 | ETH_2021_ESPS-W5_v02_M | survey_timing | F21 | sect12b1_hh_w5.dta | missing_expected_core_file |
| 1 | Ethiopia | 2021-2022 | ETH_2021_ESPS-W5_v02_M | survey_timing | F15 | sect7b_hh_w5.dta | missing_expected_core_file |
| 1 | Ethiopia | 2021-2022 | ETH_2021_ESPS-W5_v02_M | survey_timing | F64 | eth_householdgeovariables_y5.dta | missing_expected_core_file |
| 1 | Ethiopia | 2021-2022 | ETH_2021_ESPS-W5_v02_M | survey_timing | F1 | sect_cover_hh_w5.dta | missing_expected_core_file |
| 1 | Ethiopia | 2021-2022 | ETH_2021_ESPS-W5_v02_M | survey_timing | F65 | eth_plotgeovariables_y5.dta | missing_expected_core_file |
| 1 | Ethiopia | 2021-2022 | ETH_2021_ESPS-W5_v02_M | weights_and_design | F1 | sect_cover_hh_w5.dta | missing_expected_core_file |
| 1 | Ethiopia | 2021-2022 | ETH_2021_ESPS-W5_v02_M | weights_and_design | F10 | sect6b2_hh_w5.dta | missing_expected_core_file |

## Outputs

- `temp/priority_lsms_isa_minimum_batch_raw_intake_guide.csv`
- `temp/priority_lsms_isa_minimum_batch_expected_file_manifest.csv`
- `temp/priority_lsms_isa_minimum_batch_core_file_manifest.csv`
- `result/priority_lsms_isa_minimum_batch_raw_intake_guide_summary.csv`
- `temp/raw_downloads/<IDNO>/_PRIORITY_LSMS_ISA_MINIMUM_BATCH_RAW_INTAKE_GUIDE.md`

## Stop Rule

This guide is only an acquisition and intake control file. `data/` writes and
all predictive, reduced-form, causal ML, or policy-learning models remain
blocked until the promoted registry passes the 6-country, 10-wave, and accepted
CHIRPS/ERA5 linkage thresholds with value-verified raw files.
