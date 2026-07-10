# Priority LSMS/ISA Browser Download Starter

This starter is a local browser/manual-download bridge for the 10 remaining
minimum-batch World Bank Microdata packages. It does not download files by
itself, does not include credentials, and does not write promoted data.

It generates a local helper script:

- `temp/priority_lsms_isa_browser_download_starter.ps1`

Use the first canary before scaling the workflow:

```powershell
powershell -ExecutionPolicy Bypass -File temp/priority_lsms_isa_browser_download_starter.ps1 -Idno ETH_2021_ESPS-W5_v02_M
```

After a package is downloaded or manually placed in the target folder, run the
per-IDNO probe/execute and post-download validation commands listed below.

## Summary

| metric | value | interpretation |
| --- | --- | --- |
| browser_download_starter_rows | 10 | Minimum-batch rows covered by the browser download starter. |
| browser_download_starter_ready_rows | 10 | Rows with both official URL and local target folder commands. |
| browser_download_starter_priority_country_rows | 9 | Rows from Ethiopia, Nigeria, Malawi, Tanzania, or Uganda. |
| browser_download_starter_sixth_country_rows | 1 | Rows included to meet the sixth-country threshold. |
| browser_download_starter_expected_core_file_rows | 323 | Core raw-file rows expected after the packages are placed. |
| browser_download_starter_target_file_count | 0 | Existing target-folder files before browser/manual download. |
| browser_download_starter_first_canary_idno | ETH_2021_ESPS-W5_v02_M | First wave to try before scaling the browser/manual download workflow. |
| post_download_validation_scope | selected_idno_triggers_batch_rebuild | The per-IDNO runner command gates execution on one packet, while downstream validation scripts rebuild canonical batc... |
| browser_download_starter_local_ps1_path | temp/priority_lsms_isa_browser_download_starter.ps1 | Local helper script generated under temp; not intended for Git commit. |
| data_write_gate_status | blocked_no_data_write | This starter writes only command artifacts and a temp helper script, not promoted data. |
| modeling_gate_status | blocked | No predictive, reduced-form, causal ML, or policy learning is opened. |

## Starter Rows

| canary_sequence_rank | canary_role | country | wave | idno | starter_status | local_target_folder | python_probe_command |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | first_canary | Ethiopia | 2021-2022 | ETH_2021_ESPS-W5_v02_M | ready_for_browser_terms_acceptance | temp/raw_downloads/ETH_2021_ESPS-W5_v02_M/ | python script/180_build_priority_lsms_isa_credentialed_download_handoff.py --idno ETH_2021_ESPS-W5_v02_M --probe |
| 2 | follow_after_first_canary_passes | Ethiopia | 2018-2019 | ETH_2018_ESS_v04_M | ready_for_browser_terms_acceptance | temp/raw_downloads/ETH_2018_ESS_v04_M/ | python script/180_build_priority_lsms_isa_credentialed_download_handoff.py --idno ETH_2018_ESS_v04_M --probe |
| 3 | follow_after_first_canary_passes | Nigeria | 2012-2013 | NGA_2012_GHSP-W2_v02_M | ready_for_browser_terms_acceptance | temp/raw_downloads/NGA_2012_GHSP-W2_v02_M/ | python script/180_build_priority_lsms_isa_credentialed_download_handoff.py --idno NGA_2012_GHSP-W2_v02_M --probe |
| 4 | follow_after_first_canary_passes | Nigeria | 2015-2016 | NGA_2015_GHSP-W3_v02_M | ready_for_browser_terms_acceptance | temp/raw_downloads/NGA_2015_GHSP-W3_v02_M/ | python script/180_build_priority_lsms_isa_credentialed_download_handoff.py --idno NGA_2015_GHSP-W3_v02_M --probe |
| 5 | follow_after_first_canary_passes | Nigeria | 2010-2011 | NGA_2010_GHSP-W1_v03_M | ready_for_browser_terms_acceptance | temp/raw_downloads/NGA_2010_GHSP-W1_v03_M/ | python script/180_build_priority_lsms_isa_credentialed_download_handoff.py --idno NGA_2010_GHSP-W1_v03_M --probe |
| 6 | follow_after_first_canary_passes | Tanzania | 2008-2009 | TZA_2008_NPS-R1_v03_M | ready_for_browser_terms_acceptance | temp/raw_downloads/TZA_2008_NPS-R1_v03_M/ | python script/180_build_priority_lsms_isa_credentialed_download_handoff.py --idno TZA_2008_NPS-R1_v03_M --probe |
| 7 | follow_after_first_canary_passes | Tanzania | 2010-2011 | TZA_2010_NPS-R2_v03_M | ready_for_browser_terms_acceptance | temp/raw_downloads/TZA_2010_NPS-R2_v03_M/ | python script/180_build_priority_lsms_isa_credentialed_download_handoff.py --idno TZA_2010_NPS-R2_v03_M --probe |
| 8 | follow_after_first_canary_passes | Tanzania | 2012-2013 | TZA_2012_NPS-R3_v01_M | ready_for_browser_terms_acceptance | temp/raw_downloads/TZA_2012_NPS-R3_v01_M/ | python script/180_build_priority_lsms_isa_credentialed_download_handoff.py --idno TZA_2012_NPS-R3_v01_M --probe |
| 9 | follow_after_first_canary_passes | Uganda | 2019-2020 | UGA_2019_UNPS_v03_M | ready_for_browser_terms_acceptance | temp/raw_downloads/UGA_2019_UNPS_v03_M/ | python script/180_build_priority_lsms_isa_credentialed_download_handoff.py --idno UGA_2019_UNPS_v03_M --probe |
| 10 | follow_after_first_canary_passes | Nepal | 2010-2011 | NPL_2010_LSS-III_v01_M | ready_for_browser_terms_acceptance | temp/raw_downloads/NPL_2010_LSS-III_v01_M/ | python script/180_build_priority_lsms_isa_credentialed_download_handoff.py --idno NPL_2010_LSS-III_v01_M --probe |

## Per-Wave Validation Runner

| canary_sequence_rank | idno | post_download_runner_dry_run_command | post_download_runner_execute_command | post_download_validation_scope |
| --- | --- | --- | --- | --- |
| 1 | ETH_2021_ESPS-W5_v02_M | python script/178_build_priority_lsms_isa_post_download_validation_runner.py --idno ETH_2021_ESPS-W5_v02_M | python script/178_build_priority_lsms_isa_post_download_validation_runner.py --idno ETH_2021_ESPS-W5_v02_M --execute | selected_idno_triggers_batch_rebuild |
| 2 | ETH_2018_ESS_v04_M | python script/178_build_priority_lsms_isa_post_download_validation_runner.py --idno ETH_2018_ESS_v04_M | python script/178_build_priority_lsms_isa_post_download_validation_runner.py --idno ETH_2018_ESS_v04_M --execute | selected_idno_triggers_batch_rebuild |
| 3 | NGA_2012_GHSP-W2_v02_M | python script/178_build_priority_lsms_isa_post_download_validation_runner.py --idno NGA_2012_GHSP-W2_v02_M | python script/178_build_priority_lsms_isa_post_download_validation_runner.py --idno NGA_2012_GHSP-W2_v02_M --execute | selected_idno_triggers_batch_rebuild |
| 4 | NGA_2015_GHSP-W3_v02_M | python script/178_build_priority_lsms_isa_post_download_validation_runner.py --idno NGA_2015_GHSP-W3_v02_M | python script/178_build_priority_lsms_isa_post_download_validation_runner.py --idno NGA_2015_GHSP-W3_v02_M --execute | selected_idno_triggers_batch_rebuild |
| 5 | NGA_2010_GHSP-W1_v03_M | python script/178_build_priority_lsms_isa_post_download_validation_runner.py --idno NGA_2010_GHSP-W1_v03_M | python script/178_build_priority_lsms_isa_post_download_validation_runner.py --idno NGA_2010_GHSP-W1_v03_M --execute | selected_idno_triggers_batch_rebuild |
| 6 | TZA_2008_NPS-R1_v03_M | python script/178_build_priority_lsms_isa_post_download_validation_runner.py --idno TZA_2008_NPS-R1_v03_M | python script/178_build_priority_lsms_isa_post_download_validation_runner.py --idno TZA_2008_NPS-R1_v03_M --execute | selected_idno_triggers_batch_rebuild |
| 7 | TZA_2010_NPS-R2_v03_M | python script/178_build_priority_lsms_isa_post_download_validation_runner.py --idno TZA_2010_NPS-R2_v03_M | python script/178_build_priority_lsms_isa_post_download_validation_runner.py --idno TZA_2010_NPS-R2_v03_M --execute | selected_idno_triggers_batch_rebuild |
| 8 | TZA_2012_NPS-R3_v01_M | python script/178_build_priority_lsms_isa_post_download_validation_runner.py --idno TZA_2012_NPS-R3_v01_M | python script/178_build_priority_lsms_isa_post_download_validation_runner.py --idno TZA_2012_NPS-R3_v01_M --execute | selected_idno_triggers_batch_rebuild |
| 9 | UGA_2019_UNPS_v03_M | python script/178_build_priority_lsms_isa_post_download_validation_runner.py --idno UGA_2019_UNPS_v03_M | python script/178_build_priority_lsms_isa_post_download_validation_runner.py --idno UGA_2019_UNPS_v03_M --execute | selected_idno_triggers_batch_rebuild |
| 10 | NPL_2010_LSS-III_v01_M | python script/178_build_priority_lsms_isa_post_download_validation_runner.py --idno NPL_2010_LSS-III_v01_M | python script/178_build_priority_lsms_isa_post_download_validation_runner.py --idno NPL_2010_LSS-III_v01_M --execute | selected_idno_triggers_batch_rebuild |

The `--idno` runner commands are canary gates. Once the selected packet has
official raw files, the downstream validation scripts rebuild the canonical
batch receipt, schema, value-profile, and semantics outputs.

## Stop Rule

This starter only helps place official raw packages. Promotion remains blocked
until receipt, schema, value-profile, semantics, timing/geography, and
climate-linkage gates pass for a country-wave.
