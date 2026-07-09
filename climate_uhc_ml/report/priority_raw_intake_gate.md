# Priority Raw Intake Gate

Status: priority acquisition handoff and fail-closed raw-intake gate. This
report does not promote country-waves into `data/`; it makes the manual raw
package placement and post-download verification requirements explicit for the
10-wave priority batch and sixth-country backups.

## Summary

| Metric | Value | Interpretation |
|---|---:|---|
| priority_raw_intake_gate_rows | 13 | Priority acquisition and backup waves with raw-intake gates. |
| priority_raw_intake_priority_10_rows | 10 | Immediate priority wave rows covered by the raw-intake gate. |
| priority_raw_intake_priority_10_countries | 5 | Priority countries covered by the raw-intake gate. |
| priority_raw_intake_backup_rows | 3 | Sixth-country backup rows covered by the raw-intake gate. |
| priority_raw_file_target_rows | 156 | Priority file/module targets with current present/missing gate status. |
| priority_raw_file_targets_missing_rows | 156 | Priority file targets still absent from raw-download folders. |
| priority_raw_gate_blocked_manual_rows | 13 | Waves still blocked by missing complete original raw package. |
| priority_raw_gate_schema_ready_rows | 0 | Waves ready for raw value/key/unit audit after current intake check. |
| priority_raw_handoff_readmes_written | 13 | Per-target handoff README files written under temp/raw_downloads. |
| modeling_gate_status | blocked | Models remain blocked until promoted registry thresholds and climate linkage gates pass. |

## Gate Status

| Current gate status | Waves |
|---|---:|
| `blocked_manual_raw_package_required` | 13 |

## Wave-Level Intake Gate

| acquisition_batch_rank | batch_role | country | wave | idno | current_gate_status | priority_expected_files_not_present | required_concepts_unverified | handoff_readme |
|---|---|---|---|---|---|---|---|---|
| 1 | priority_10_wave_batch | Ethiopia | 2021-2022 | ETH_2021_ESPS-W5_v02_M | blocked_manual_raw_package_required | 12 | 13 | temp/raw_downloads/ETH_2021_ESPS-W5_v02_M/_PRIORITY_RAW_INTAKE_HANDOFF.md |
| 2 | priority_10_wave_batch | Ethiopia | 2018-2019 | ETH_2018_ESS_v04_M | blocked_manual_raw_package_required | 12 | 13 | temp/raw_downloads/ETH_2018_ESS_v04_M/_PRIORITY_RAW_INTAKE_HANDOFF.md |
| 3 | priority_10_wave_batch | Malawi | 2007-2009 | MWI_2007-2009_MTM_v01_M | blocked_manual_raw_package_required | 12 | 13 | temp/raw_downloads/MWI_2007-2009_MTM_v01_M/_PRIORITY_RAW_INTAKE_HANDOFF.md |
| 4 | priority_10_wave_batch | Nigeria | 2012-2013 | NGA_2012_GHSP-W2_v02_M | blocked_manual_raw_package_required | 12 | 13 | temp/raw_downloads/NGA_2012_GHSP-W2_v02_M/_PRIORITY_RAW_INTAKE_HANDOFF.md |
| 5 | priority_10_wave_batch | Nigeria | 2015-2016 | NGA_2015_GHSP-W3_v02_M | blocked_manual_raw_package_required | 12 | 13 | temp/raw_downloads/NGA_2015_GHSP-W3_v02_M/_PRIORITY_RAW_INTAKE_HANDOFF.md |
| 6 | priority_10_wave_batch | Nigeria | 2010-2011 | NGA_2010_GHSP-W1_v03_M | blocked_manual_raw_package_required | 12 | 13 | temp/raw_downloads/NGA_2010_GHSP-W1_v03_M/_PRIORITY_RAW_INTAKE_HANDOFF.md |
| 7 | priority_10_wave_batch | Tanzania | 2008-2009 | TZA_2008_NPS-R1_v03_M | blocked_manual_raw_package_required | 12 | 13 | temp/raw_downloads/TZA_2008_NPS-R1_v03_M/_PRIORITY_RAW_INTAKE_HANDOFF.md |
| 8 | priority_10_wave_batch | Tanzania | 2010-2011 | TZA_2010_NPS-R2_v03_M | blocked_manual_raw_package_required | 12 | 13 | temp/raw_downloads/TZA_2010_NPS-R2_v03_M/_PRIORITY_RAW_INTAKE_HANDOFF.md |
| 9 | priority_10_wave_batch | Tanzania | 2012-2013 | TZA_2012_NPS-R3_v01_M | blocked_manual_raw_package_required | 12 | 13 | temp/raw_downloads/TZA_2012_NPS-R3_v01_M/_PRIORITY_RAW_INTAKE_HANDOFF.md |
| 10 | priority_10_wave_batch | Uganda | 2014 | UGA_2014_SAGE-EL_v01_M | blocked_manual_raw_package_required | 12 | 13 | temp/raw_downloads/UGA_2014_SAGE-EL_v01_M/_PRIORITY_RAW_INTAKE_HANDOFF.md |
| 11 | sixth_country_backup_candidate | Jamaica | 1997 | JAM_1997_SLC_v01_M | blocked_manual_raw_package_required | 12 | 13 | temp/raw_downloads/JAM_1997_SLC_v01_M/_PRIORITY_RAW_INTAKE_HANDOFF.md |
| 12 | sixth_country_backup_candidate | Kyrgyz Republic | 1993 | KGZ_1993_KMPS_v01_M | blocked_manual_raw_package_required | 12 | 13 | temp/raw_downloads/KGZ_1993_KMPS_v01_M/_PRIORITY_RAW_INTAKE_HANDOFF.md |
| 13 | sixth_country_backup_candidate | Nepal | 2010-2011 | NPL_2010_LSS-III_v01_M | blocked_manual_raw_package_required | 12 | 13 | temp/raw_downloads/NPL_2010_LSS-III_v01_M/_PRIORITY_RAW_INTAKE_HANDOFF.md |

## File-Level Targets

| acquisition_batch_rank | idno | file_rank | file_name | current_file_gate_status | download_priority_reason |
|---|---|---|---|---|---|
| 1 | ETH_2021_ESPS-W5_v02_M | 1 | sect8_3_ls_w5.dta | blocked_missing_raw_file | OOP spending; need/access; climate geography; weights/design/keys |
| 1 | ETH_2021_ESPS-W5_v02_M | 2 | sect11_ph_w5.dta | blocked_missing_raw_file | need/access; climate geography; weights/design/keys |
| 1 | ETH_2021_ESPS-W5_v02_M | 3 | sect3_pp_w5.dta | blocked_missing_raw_file | need/access; climate geography; weights/design/keys |
| 1 | ETH_2021_ESPS-W5_v02_M | 4 | sect06_com_w5.dta | blocked_missing_raw_file | need/access; climate geography; weights/design/keys |
| 1 | ETH_2021_ESPS-W5_v02_M | 5 | sect04_com_w5.dta | blocked_missing_raw_file | need/access; climate geography; weights/design/keys |
| 1 | ETH_2021_ESPS-W5_v02_M | 6 | sect4_pp_w5.dta | blocked_missing_raw_file | climate geography; weights/design/keys |
| 1 | ETH_2021_ESPS-W5_v02_M | 7 | sect9_ph_w5.dta | blocked_missing_raw_file | climate geography; weights/design/keys |
| 1 | ETH_2021_ESPS-W5_v02_M | 8 | sect8_2_ls_w5.dta | blocked_missing_raw_file | financial denominator; need/access; climate geography; weights/design/keys |
| 1 | ETH_2021_ESPS-W5_v02_M | 9 | sect3_hh_w5.dta | blocked_missing_raw_file | OOP spending; need/access; climate geography; weights/design/keys |
| 1 | ETH_2021_ESPS-W5_v02_M | 10 | sect7_pp_w5.dta | blocked_missing_raw_file | need/access; climate geography; weights/design/keys |
| 1 | ETH_2021_ESPS-W5_v02_M | 11 | sect11_com_w5.dta | blocked_missing_raw_file | climate geography; weights/design/keys |
| 1 | ETH_2021_ESPS-W5_v02_M | 12 | eth_householdgeovariables_y5.dta | blocked_missing_raw_file | need/access; climate geography; weights/design/keys |
| 2 | ETH_2018_ESS_v04_M | 1 | sect8_3_ls_w4.dta | blocked_missing_raw_file | OOP spending; need/access; climate geography; weights/design/keys |
| 2 | ETH_2018_ESS_v04_M | 2 | sect10c_hh_w4.dta | blocked_missing_raw_file | climate geography; weights/design/keys |
| 2 | ETH_2018_ESS_v04_M | 3 | sect11_ph_w4.dta | blocked_missing_raw_file | need/access; climate geography; weights/design/keys |
| 2 | ETH_2018_ESS_v04_M | 4 | sect04_com_w4.dta | blocked_missing_raw_file | need/access; climate geography; weights/design/keys |
| 2 | ETH_2018_ESS_v04_M | 5 | sect06_com_w4.dta | blocked_missing_raw_file | need/access; climate geography; weights/design/keys |
| 2 | ETH_2018_ESS_v04_M | 6 | sect3_pp_w4.dta | blocked_missing_raw_file | climate geography; weights/design/keys |
| 2 | ETH_2018_ESS_v04_M | 7 | sect5b2_hh_w4.dta | blocked_missing_raw_file | climate geography; weights/design/keys |
| 2 | ETH_2018_ESS_v04_M | 8 | sect4_pp_w4.dta | blocked_missing_raw_file | climate geography; weights/design/keys |
| 2 | ETH_2018_ESS_v04_M | 9 | sect3_hh_w4.dta | blocked_missing_raw_file | OOP spending; need/access; climate geography; weights/design/keys |
| 2 | ETH_2018_ESS_v04_M | 10 | sect8_2_ls_w4.dta | blocked_missing_raw_file | financial denominator; need/access; climate geography; weights/design/keys |
| 2 | ETH_2018_ESS_v04_M | 11 | sect9_ph_w4.dta | blocked_missing_raw_file | climate geography; weights/design/keys |
| 2 | ETH_2018_ESS_v04_M | 12 | sect8_4_ls_w4.dta | blocked_missing_raw_file | climate geography; weights/design/keys |
| 3 | MWI_2007-2009_MTM_v01_M | 1 | hh2_cmty | blocked_missing_raw_file | need/access; climate geography |
| 3 | MWI_2007-2009_MTM_v01_M | 2 | pi_s5a | blocked_missing_raw_file | need/access; weights/design/keys |
| 3 | MWI_2007-2009_MTM_v01_M | 3 | p2_s14a | blocked_missing_raw_file | need/access; weights/design/keys |
| 3 | MWI_2007-2009_MTM_v01_M | 4 | p2_s13 | blocked_missing_raw_file | need/access; climate geography; weights/design/keys |
| 3 | MWI_2007-2009_MTM_v01_M | 5 | p2_s10 | blocked_missing_raw_file | OOP spending; need/access; weights/design/keys |
| 3 | MWI_2007-2009_MTM_v01_M | 6 | p2_s11 | blocked_missing_raw_file | OOP spending; need/access; weights/design/keys |

## Machine-Readable Outputs

- `temp/priority_raw_intake_gate.csv`
- `temp/priority_raw_file_targets.csv`
- `result/priority_raw_intake_gate_summary.csv`
- per-wave `temp/raw_downloads/<IDNO>/_PRIORITY_RAW_INTAKE_HANDOFF.md`
