# Priority LSMS/ISA Minimum-Batch Promotion Unlock Board

This report condenses the current 10-package manual-download batch into one
promotion-unlock row per country-wave. It does not download, copy, or promote
raw data. It only joins existing packet, public-documentation, target-folder,
download-acceptance, route-probe, and registry evidence.

The board is intentionally fail-closed: a row becomes ready only after local
official raw package files are present and expected core files match. Until
then, `data/` writes and all modeling remain blocked.

## Summary

| metric | value | interpretation |
| --- | --- | --- |
| minimum_batch_unlock_board_rows | 10 | Manual-download country-waves in the current minimum batch. |
| minimum_batch_unlock_public_documentation_complete_rows | 10 | Rows with complete public catalog/DDI/variables/get-microdata documentation receipt. |
| minimum_batch_unlock_validation_ready_rows | 0 | Rows with enough local files to begin receipt validation. |
| minimum_batch_unlock_blocked_no_local_or_incoming_files | 10 | Rows still lacking placed official raw package files or incoming route matches. |
| minimum_batch_unlock_target_file_rows | 0 | Non-generated files currently found in target folders by the manual progress tracker. |
| minimum_batch_unlock_target_total_bytes | 0 | Total bytes currently found in target folders by the manual progress tracker. |
| minimum_batch_unlock_missing_expected_file_rows | 838 | Expected official files still absent according to the download acceptance matrix. |
| minimum_batch_unlock_missing_core_requirement_rows | 70 | Requirement-level core file checks still blocked by missing official files. |
| minimum_batch_unlock_public_route_raw_payload_candidate_rows | 0 | Raw payload candidates found by public route probing. |
| minimum_batch_unlock_public_route_access_gate_rows | 80 | Route probes that hit login, registration, terms, or data-dictionary gates. |
| current_promoted_analysis_ready_rows | 1 | Country-waves already promoted in the registry. |
| projected_country_wave_rows_if_all_minimum_batch_promoted | 11 | Promoted country-wave count if every minimum-batch package passes all gates. |
| projected_country_rows_if_all_minimum_batch_promoted | 6 | Country count if the promoted row plus every minimum-batch package passes all gates. |
| minimum_batch_unlock_needed_for_modeling_threshold | 10 | All current minimum-batch packages are still needed to reach both 6-country and 10-wave thresholds. |
| data_write_gate_status | blocked_no_data_write | This board writes only result/report artifacts and does not promote datasets. |
| modeling_gate_status | blocked | No predictive, reduced-form, causal ML, or policy learning is opened. |

## Unlock Board

| download_rank | country | wave | idno | unlock_status | public_documentation_receipt_status | target_file_count | expected_core_file_rows | expected_core_file_name_matches |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Ethiopia | 2021-2022 | ETH_2021_ESPS-W5_v02_M | blocked_no_local_or_incoming_files | complete_core_public_documentation_receipt | 0 | 36 | 0 |
| 2 | Ethiopia | 2018-2019 | ETH_2018_ESS_v04_M | blocked_no_local_or_incoming_files | complete_core_public_documentation_receipt | 0 | 35 | 0 |
| 3 | Nigeria | 2012-2013 | NGA_2012_GHSP-W2_v02_M | blocked_no_local_or_incoming_files | complete_core_public_documentation_receipt | 0 | 26 | 0 |
| 4 | Nigeria | 2015-2016 | NGA_2015_GHSP-W3_v02_M | blocked_no_local_or_incoming_files | complete_core_public_documentation_receipt | 0 | 26 | 0 |
| 5 | Nigeria | 2010-2011 | NGA_2010_GHSP-W1_v03_M | blocked_no_local_or_incoming_files | complete_core_public_documentation_receipt | 0 | 27 | 0 |
| 6 | Tanzania | 2008-2009 | TZA_2008_NPS-R1_v03_M | blocked_no_local_or_incoming_files | complete_core_public_documentation_receipt | 0 | 35 | 0 |
| 7 | Tanzania | 2010-2011 | TZA_2010_NPS-R2_v03_M | blocked_no_local_or_incoming_files | complete_core_public_documentation_receipt | 0 | 38 | 0 |
| 8 | Tanzania | 2012-2013 | TZA_2012_NPS-R3_v01_M | blocked_no_local_or_incoming_files | complete_core_public_documentation_receipt | 0 | 33 | 0 |
| 9 | Uganda | 2019-2020 | UGA_2019_UNPS_v03_M | blocked_no_local_or_incoming_files | complete_core_public_documentation_receipt | 0 | 39 | 0 |
| 10 | Nepal | 2010-2011 | NPL_2010_LSS-III_v01_M | blocked_no_local_or_incoming_files | complete_core_public_documentation_receipt | 0 | 28 | 0 |

## Use

For each blocked row, open the official get-microdata URL, download the complete
unchanged official raw package and documentation, place all files under the
listed local target folder, then run the post-download validation commands in
`result/priority_lsms_isa_minimum_batch_promotion_unlock_board.csv`.
