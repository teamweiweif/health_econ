# Priority LSMS/ISA Local Stray Raw Package Locator

Status: non-destructive local locator for the current 10 minimum-batch manual-download packets.

This locator searches the local project/workspace tree for files that appear to
match the expected LSMS/ISA raw files or archive packages but are not already
handled by the normal target-folder receipt gate. It reads only file names,
sizes, and archive member listings. It does not copy, move, delete, extract,
harmonize, write `data/`, or run models.

## Summary

| metric | value | interpretation |
| --- | --- | --- |
| priority_lsms_local_stray_raw_locator_dataset_rows | 10 | Current manual-download minimum-batch rows covered by the locator route plan. |
| priority_lsms_local_stray_raw_locator_scanned_file_rows | 4881 | Filesystem file rows seen under the bounded search roots before suffix filtering. |
| priority_lsms_local_stray_raw_locator_considered_file_rows | 1353 | Candidate suffix files considered for raw/documentation/package matching. |
| priority_lsms_local_stray_raw_locator_candidate_file_rows | 0 | Local candidate files matching expected core/full names, archive members, or strong IDNO/catalog archive-na... |
| priority_lsms_local_stray_raw_locator_matched_idno_rows | 0 | Manual-download packet rows with at least one candidate local file outside the normal receipt gate. |
| priority_lsms_local_stray_raw_locator_route_plan_rows | 10 | One route-plan row per current minimum-batch manual packet. |
| priority_lsms_local_stray_raw_locator_outside_target_candidate_rows | 0 | Candidate files outside the correct target folder and outside _incoming. |
| priority_lsms_local_stray_raw_locator_incoming_candidate_rows | 0 | Candidate files already staged under temp/raw_downloads/_incoming. |
| priority_lsms_local_stray_raw_locator_already_target_candidate_rows | 0 | Candidate files already inside the expected target folder. |
| priority_lsms_local_stray_raw_locator_direct_expected_match_rows | 0 | Candidates whose filename directly matches an expected file name. |
| priority_lsms_local_stray_raw_locator_archive_member_match_rows | 0 | Candidates whose readable archive member list matches expected file names. |
| priority_lsms_local_stray_raw_locator_core_expected_match_rows | 0 | Candidates matching at least one priority core expected file. |
| priority_lsms_local_stray_raw_locator_weak_archive_name_rows | 0 | Archive-name-only matches using IDNO or catalog tokens; these require extra manual scrutiny. |
| priority_lsms_local_stray_raw_locator_unreadable_directory_rows | 22 | Skipped directory rows from explicit skip rules or inaccessible walk locations. |
| priority_lsms_local_stray_raw_locator_unreadable_archive_rows | 0 | Candidate archive files whose members could not be listed. |
| priority_lsms_local_stray_raw_locator_data_write_status | blocked_no_data_write | The locator does not copy, extract, harmonize, or write promoted data. |
| priority_lsms_local_stray_raw_locator_raw_promotion_status | blocked_no_local_stray_raw_package_found | Raw packages remain unaccepted until the normal receipt, schema, value, semantics, timing/geography, and cl... |
| modeling_gate_status | blocked | No predictive, reduced-form, causal ML, or policy learning until registry thresholds pass. |

## Route Plan

| download_rank | idno | target_receipt_smoke_status | stray_candidate_rows | outside_target_candidate_rows | incoming_candidate_rows | already_target_candidate_rows | route_status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | ETH_2021_ESPS-W5_v02_M | blocked_no_candidate_raw_or_documentation_files | 0 | 0 | 0 | 0 | no_local_stray_raw_package_found |
| 2 | ETH_2018_ESS_v04_M | blocked_no_candidate_raw_or_documentation_files | 0 | 0 | 0 | 0 | no_local_stray_raw_package_found |
| 3 | NGA_2012_GHSP-W2_v02_M | blocked_no_candidate_raw_or_documentation_files | 0 | 0 | 0 | 0 | no_local_stray_raw_package_found |
| 4 | NGA_2015_GHSP-W3_v02_M | blocked_no_candidate_raw_or_documentation_files | 0 | 0 | 0 | 0 | no_local_stray_raw_package_found |
| 5 | NGA_2010_GHSP-W1_v03_M | blocked_no_candidate_raw_or_documentation_files | 0 | 0 | 0 | 0 | no_local_stray_raw_package_found |
| 6 | TZA_2008_NPS-R1_v03_M | blocked_no_candidate_raw_or_documentation_files | 0 | 0 | 0 | 0 | no_local_stray_raw_package_found |
| 7 | TZA_2010_NPS-R2_v03_M | blocked_no_candidate_raw_or_documentation_files | 0 | 0 | 0 | 0 | no_local_stray_raw_package_found |
| 8 | TZA_2012_NPS-R3_v01_M | blocked_no_candidate_raw_or_documentation_files | 0 | 0 | 0 | 0 | no_local_stray_raw_package_found |
| 9 | UGA_2019_UNPS_v03_M | blocked_no_candidate_raw_or_documentation_files | 0 | 0 | 0 | 0 | no_local_stray_raw_package_found |
| 10 | NPL_2010_LSS-III_v01_M | blocked_no_candidate_raw_or_documentation_files | 0 | 0 | 0 | 0 | no_local_stray_raw_package_found |

## Candidate Files

_No rows._

## Stop Rule

Any candidate found here is only a pointer for manual review. A country-wave
remains blocked until the complete official raw package is placed in the target
folder and passes receipt, schema, raw-value, semantics, timing/geography, and
climate-linkage validation.
