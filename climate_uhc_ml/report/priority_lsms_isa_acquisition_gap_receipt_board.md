# Priority LSMS/ISA Acquisition Gap Receipt Board

Status: single execution board for the remaining locked World Bank raw-package downloads.

This board reconciles the manual launchpad, package-level manifest, post-download receipt handoff, and promotion-threshold gap. It does not download files, move files, extract archives, write `data/`, or open any modeling gate.

## Summary

| metric | value | interpretation |
| --- | --- | --- |
| acquisition_gap_receipt_board_rows | 10 | Download-required package rows in the acquisition gap and receipt board. |
| acquisition_gap_receipt_country_rows | 5 | Countries covered by the remaining package-download board. |
| current_promoted_analysis_ready_rows | 1 | Currently promoted analysis-ready rows from the registry before these downloads. |
| current_financial_protection_ready_countries | 1 | Current countries with value-verified financial-protection readiness. |
| current_double_failure_ready_country_waves | 1 | Current value-verified double-failure-ready country-waves. |
| current_accepted_climate_linkage_rows | 1 | Current accepted CHIRPS/ERA5 climate-linkage rows. |
| target_financial_protection_ready_countries | 6 | Goal threshold before modeling can resume. |
| target_double_failure_ready_country_waves | 10 | Goal threshold before modeling can resume. |
| target_accepted_climate_linkage_rows | 1 | Minimum climate-linkage threshold; more rows still need country-wave linkage for final data. |
| remaining_financial_country_gap | 5 | Countries still needed before modeling can resume. |
| remaining_double_failure_wave_gap | 9 | Country-waves still needed before modeling can resume. |
| acquisition_gap_expected_full_file_rows | 838 | Expected official file rows across the remaining download packages. |
| acquisition_gap_missing_expected_file_rows | 838 | Expected official file rows currently missing. |
| acquisition_gap_expected_core_file_rows | 323 | Requirement-linked core file rows across the remaining download packages. |
| acquisition_gap_missing_core_file_rows | 323 | Requirement-linked core file rows currently missing. |
| acquisition_gap_requirement_gate_rows | 70 | Receipt-level requirement gates represented in the board. |
| acquisition_gap_blocked_requirement_rows | 70 | Requirement gates still blocked by missing local packages/core files. |
| acquisition_gap_target_file_rows | 0 | Files currently present under exact target folders. |
| acquisition_gap_incoming_file_rows | 0 | Files currently staged under temp/raw_downloads/_incoming. |
| acquisition_gap_missing_package_rows | 10 | Download-required package rows with no local package or incoming file. |
| acquisition_gap_local_or_incoming_package_rows | 0 | Rows with at least one local target or incoming candidate file. |
| acquisition_gap_first_canary_idno | ETH_2021_ESPS-W5_v02_M | First package to download and validate before scaling the batch. |
| data_write_gate_status | blocked_no_data_write | This board does not write promoted data. |
| modeling_gate_status | blocked | No predictive, reduced-form, causal ML, or policy learning is opened. |

## Threshold Gap

- Current promoted analysis-ready rows: 1.
- Current financial-protection-ready countries: 1 of 6.
- Current double-failure-ready country-waves: 1 of 10.
- Remaining financial country gap: 5.
- Remaining double-failure wave gap: 9.
- Remaining download-required packages in this board: 10.

## Download And Receipt Board

| download_rank | country | wave | idno | scope_role | first_canary_flag | target_file_count | incoming_file_rows | expected_full_file_rows | missing_expected_file_rows | expected_core_file_rows | missing_core_file_rows | receipt_status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Ethiopia | 2021-2022 | ETH_2021_ESPS-W5_v02_M | download_required_priority_country_wave | 1 | 0 | 0 | 68 | 68 | 36 | 36 | blocked_no_local_package_or_incoming_files |
| 2 | Ethiopia | 2018-2019 | ETH_2018_ESS_v04_M | download_required_priority_country_wave | 0 | 0 | 0 | 68 | 68 | 35 | 35 | blocked_no_local_package_or_incoming_files |
| 3 | Nigeria | 2012-2013 | NGA_2012_GHSP-W2_v02_M | download_required_priority_country_wave | 0 | 0 | 0 | 103 | 103 | 26 | 26 | blocked_no_local_package_or_incoming_files |
| 4 | Nigeria | 2015-2016 | NGA_2015_GHSP-W3_v02_M | download_required_priority_country_wave | 0 | 0 | 0 | 104 | 104 | 26 | 26 | blocked_no_local_package_or_incoming_files |
| 5 | Nigeria | 2010-2011 | NGA_2010_GHSP-W1_v03_M | download_required_priority_country_wave | 0 | 0 | 0 | 99 | 99 | 27 | 27 | blocked_no_local_package_or_incoming_files |
| 6 | Tanzania | 2008-2009 | TZA_2008_NPS-R1_v03_M | download_required_priority_country_wave | 0 | 0 | 0 | 61 | 61 | 35 | 35 | blocked_no_local_package_or_incoming_files |
| 7 | Tanzania | 2010-2011 | TZA_2010_NPS-R2_v03_M | download_required_priority_country_wave | 0 | 0 | 0 | 95 | 95 | 38 | 38 | blocked_no_local_package_or_incoming_files |
| 8 | Tanzania | 2012-2013 | TZA_2012_NPS-R3_v01_M | download_required_priority_country_wave | 0 | 0 | 0 | 80 | 80 | 33 | 33 | blocked_no_local_package_or_incoming_files |
| 9 | Uganda | 2019-2020 | UGA_2019_UNPS_v03_M | download_required_priority_country_wave | 0 | 0 | 0 | 109 | 109 | 39 | 39 | blocked_no_local_package_or_incoming_files |
| 10 | Nepal | 2010-2011 | NPL_2010_LSS-III_v01_M | download_required_sixth_country_candidate | 0 | 0 | 0 | 51 | 51 | 28 | 28 | blocked_no_local_package_or_incoming_files |

## Execution Rule

Download the first canary package first, place the complete unchanged official package under its target folder or under `_incoming`, then run the row-specific validation commands before scaling to the remaining packages.

## Stop Rule

A package receipt is not a promoted dataset. A country-wave can enter `data/` only after official package receipt, schema, raw value, semantics, timing/geography, climate-linkage, and promotion-packet gates all pass. Modeling stays blocked until the registry reaches 6 value-verified countries and 10 value-verified country-waves.
