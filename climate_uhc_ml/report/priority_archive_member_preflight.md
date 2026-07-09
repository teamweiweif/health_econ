# Priority Archive Member Preflight

Status: fail-closed archive/direct-file completeness preflight for the priority
10-wave batch and sixth-country backups. This does not inspect raw values and
does not promote any country-wave into `data/`.

## Summary

| Metric | Value | Interpretation |
|---|---:|---|
| priority_archive_preflight_dataset_rows | 13 | Priority and backup waves checked for direct/archive raw coverage. |
| priority_archive_preflight_file_target_rows | 156 | Priority file targets checked against direct files and archive members. |
| priority_archive_files_found | 0 | Archive files found in priority target folders. |
| priority_archive_member_rows | 0 | Raw-like members listed inside priority archives. |
| priority_targets_covered_by_direct_file | 0 | Priority file targets covered by a direct raw file. |
| priority_targets_covered_by_archive_member | 0 | Priority file targets covered by a listed archive member. |
| priority_targets_missing_direct_or_archive_member | 156 | Priority file targets still missing after direct/archive preflight. |
| priority_archives_with_unsupported_listing | 0 | Archive files whose members could not be listed by available tools. |
| priority_datasets_all_targets_covered | 0 | Datasets with all priority targets covered but still requiring raw value verification. |
| priority_datasets_blocked_no_raw_or_archive | 13 | Datasets with no raw tabular or archive file in the priority folder. |
| modeling_gate_status | blocked | Models remain blocked until promoted registry thresholds and accepted climate linkage pass. |

## Coverage Status

| Coverage status | File targets |
|---|---:|
| `blocked_no_raw_or_archive_file` | 156 |

## Completeness Preview

| acquisition_batch_rank | idno | file_rank | expected_file_name | coverage_status | verification_action |
|---|---|---|---|---|---|
| 1 | ETH_2021_ESPS-W5_v02_M | 1 | sect8_3_ls_w5.dta | blocked_no_raw_or_archive_file | Place complete original raw archive/tabular package in the target folder. |
| 1 | ETH_2021_ESPS-W5_v02_M | 2 | sect11_ph_w5.dta | blocked_no_raw_or_archive_file | Place complete original raw archive/tabular package in the target folder. |
| 1 | ETH_2021_ESPS-W5_v02_M | 3 | sect3_pp_w5.dta | blocked_no_raw_or_archive_file | Place complete original raw archive/tabular package in the target folder. |
| 1 | ETH_2021_ESPS-W5_v02_M | 4 | sect06_com_w5.dta | blocked_no_raw_or_archive_file | Place complete original raw archive/tabular package in the target folder. |
| 1 | ETH_2021_ESPS-W5_v02_M | 5 | sect04_com_w5.dta | blocked_no_raw_or_archive_file | Place complete original raw archive/tabular package in the target folder. |
| 1 | ETH_2021_ESPS-W5_v02_M | 6 | sect4_pp_w5.dta | blocked_no_raw_or_archive_file | Place complete original raw archive/tabular package in the target folder. |
| 1 | ETH_2021_ESPS-W5_v02_M | 7 | sect9_ph_w5.dta | blocked_no_raw_or_archive_file | Place complete original raw archive/tabular package in the target folder. |
| 1 | ETH_2021_ESPS-W5_v02_M | 8 | sect8_2_ls_w5.dta | blocked_no_raw_or_archive_file | Place complete original raw archive/tabular package in the target folder. |
| 1 | ETH_2021_ESPS-W5_v02_M | 9 | sect3_hh_w5.dta | blocked_no_raw_or_archive_file | Place complete original raw archive/tabular package in the target folder. |
| 1 | ETH_2021_ESPS-W5_v02_M | 10 | sect7_pp_w5.dta | blocked_no_raw_or_archive_file | Place complete original raw archive/tabular package in the target folder. |
| 1 | ETH_2021_ESPS-W5_v02_M | 11 | sect11_com_w5.dta | blocked_no_raw_or_archive_file | Place complete original raw archive/tabular package in the target folder. |
| 1 | ETH_2021_ESPS-W5_v02_M | 12 | eth_householdgeovariables_y5.dta | blocked_no_raw_or_archive_file | Place complete original raw archive/tabular package in the target folder. |
| 2 | ETH_2018_ESS_v04_M | 1 | sect8_3_ls_w4.dta | blocked_no_raw_or_archive_file | Place complete original raw archive/tabular package in the target folder. |
| 2 | ETH_2018_ESS_v04_M | 2 | sect10c_hh_w4.dta | blocked_no_raw_or_archive_file | Place complete original raw archive/tabular package in the target folder. |
| 2 | ETH_2018_ESS_v04_M | 3 | sect11_ph_w4.dta | blocked_no_raw_or_archive_file | Place complete original raw archive/tabular package in the target folder. |
| 2 | ETH_2018_ESS_v04_M | 4 | sect04_com_w4.dta | blocked_no_raw_or_archive_file | Place complete original raw archive/tabular package in the target folder. |
| 2 | ETH_2018_ESS_v04_M | 5 | sect06_com_w4.dta | blocked_no_raw_or_archive_file | Place complete original raw archive/tabular package in the target folder. |
| 2 | ETH_2018_ESS_v04_M | 6 | sect3_pp_w4.dta | blocked_no_raw_or_archive_file | Place complete original raw archive/tabular package in the target folder. |
| 2 | ETH_2018_ESS_v04_M | 7 | sect5b2_hh_w4.dta | blocked_no_raw_or_archive_file | Place complete original raw archive/tabular package in the target folder. |
| 2 | ETH_2018_ESS_v04_M | 8 | sect4_pp_w4.dta | blocked_no_raw_or_archive_file | Place complete original raw archive/tabular package in the target folder. |
| 2 | ETH_2018_ESS_v04_M | 9 | sect3_hh_w4.dta | blocked_no_raw_or_archive_file | Place complete original raw archive/tabular package in the target folder. |
| 2 | ETH_2018_ESS_v04_M | 10 | sect8_2_ls_w4.dta | blocked_no_raw_or_archive_file | Place complete original raw archive/tabular package in the target folder. |
| 2 | ETH_2018_ESS_v04_M | 11 | sect9_ph_w4.dta | blocked_no_raw_or_archive_file | Place complete original raw archive/tabular package in the target folder. |
| 2 | ETH_2018_ESS_v04_M | 12 | sect8_4_ls_w4.dta | blocked_no_raw_or_archive_file | Place complete original raw archive/tabular package in the target folder. |
| 3 | MWI_2007-2009_MTM_v01_M | 1 | hh2_cmty | blocked_no_raw_or_archive_file | Place complete original raw archive/tabular package in the target folder. |
| 3 | MWI_2007-2009_MTM_v01_M | 2 | pi_s5a | blocked_no_raw_or_archive_file | Place complete original raw archive/tabular package in the target folder. |
| 3 | MWI_2007-2009_MTM_v01_M | 3 | p2_s14a | blocked_no_raw_or_archive_file | Place complete original raw archive/tabular package in the target folder. |
| 3 | MWI_2007-2009_MTM_v01_M | 4 | p2_s13 | blocked_no_raw_or_archive_file | Place complete original raw archive/tabular package in the target folder. |
| 3 | MWI_2007-2009_MTM_v01_M | 5 | p2_s10 | blocked_no_raw_or_archive_file | Place complete original raw archive/tabular package in the target folder. |
| 3 | MWI_2007-2009_MTM_v01_M | 6 | p2_s11 | blocked_no_raw_or_archive_file | Place complete original raw archive/tabular package in the target folder. |
| 3 | MWI_2007-2009_MTM_v01_M | 7 | hh2p3_s17 | blocked_no_raw_or_archive_file | Place complete original raw archive/tabular package in the target folder. |
| 3 | MWI_2007-2009_MTM_v01_M | 8 | hh3p3_s15 | blocked_no_raw_or_archive_file | Place complete original raw archive/tabular package in the target folder. |
| 3 | MWI_2007-2009_MTM_v01_M | 9 | p2_s9 | blocked_no_raw_or_archive_file | Place complete original raw archive/tabular package in the target folder. |
| 3 | MWI_2007-2009_MTM_v01_M | 10 | hh2p2_s10 | blocked_no_raw_or_archive_file | Place complete original raw archive/tabular package in the target folder. |
| 3 | MWI_2007-2009_MTM_v01_M | 11 | hh2p2_s12 | blocked_no_raw_or_archive_file | Place complete original raw archive/tabular package in the target folder. |
| 3 | MWI_2007-2009_MTM_v01_M | 12 | hh2p3_s15 | blocked_no_raw_or_archive_file | Place complete original raw archive/tabular package in the target folder. |
| 4 | NGA_2012_GHSP-W2_v02_M | 1 | secta1_harvestw2 | blocked_no_raw_or_archive_file | Place complete original raw archive/tabular package in the target folder. |
| 4 | NGA_2012_GHSP-W2_v02_M | 2 | sect11b1_plantingw2 | blocked_no_raw_or_archive_file | Place complete original raw archive/tabular package in the target folder. |
| 4 | NGA_2012_GHSP-W2_v02_M | 3 | sect11h_plantingw2 | blocked_no_raw_or_archive_file | Place complete original raw archive/tabular package in the target folder. |
| 4 | NGA_2012_GHSP-W2_v02_M | 4 | sect4a_harvestw2 | blocked_no_raw_or_archive_file | Place complete original raw archive/tabular package in the target folder. |

## Archive Member Preview

No priority archive files were found.

## Rule

An archive-member match is only a placement/completeness signal. Promotion still
requires extraction or direct schema inspection plus raw value, label, unit,
recall-period, missing-code, merge-key, survey-design, timing, geography, and
CHIRPS/ERA5 linkage verification.

## Machine-Readable Outputs

- `temp/priority_archive_member_inventory.csv`
- `temp/priority_archive_completeness_matrix.csv`
- `result/priority_archive_member_preflight_summary.csv`
