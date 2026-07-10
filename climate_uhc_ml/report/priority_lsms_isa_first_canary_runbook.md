# Priority LSMS/ISA First Canary Download Runbook

Status: one-wave execution runbook for the first manual-download canary. It
does not download, copy, extract, write promoted `data/`, or run models.

The canary is `ETH_2021_ESPS-W5_v02_M` (Ethiopia 2021-2022). Use it before
scaling the remaining minimum-batch downloads.

## Summary

| metric | value | interpretation |
| --- | --- | --- |
| first_canary_idno | ETH_2021_ESPS-W5_v02_M | IDNO selected as the first manual-download canary. |
| first_canary_country | Ethiopia | Country for the first canary. |
| first_canary_wave | 2021-2022 | Survey wave for the first canary. |
| first_canary_expected_official_file_rows | 68 | Official file rows expected from the complete package. |
| first_canary_expected_unique_core_file_rows | 25 | Unique official core files to check immediately after package placement. |
| first_canary_requirement_core_file_rows | 36 | Requirement-file linkage rows; one file can support multiple requirements. |
| first_canary_requirement_gate_rows | 7 | Promotion requirement rows covered by this canary. |
| first_canary_missing_unique_core_file_rows | 25 | Unique core files still missing locally. |
| first_canary_missing_requirement_core_file_rows | 36 | Requirement-file linkage rows still blocked by missing files. |
| first_canary_blocked_requirement_rows | 7 | Requirement rows still blocked by missing files. |
| first_canary_target_file_count | 0 | Candidate raw files currently present in the target folder. |
| first_canary_progress_status | blocked_no_local_or_incoming_files | Manual-download progress status for the canary. |
| data_write_gate_status | blocked_no_data_write | This runbook writes only result/report artifacts. |
| modeling_gate_status | blocked | No predictive, reduced-form, causal ML, or policy learning is opened. |

## Canary Commands

```powershell
New-Item -ItemType Directory -Force -Path 'temp/raw_downloads/ETH_2021_ESPS-W5_v02_M'
Start-Process 'https://microdata.worldbank.org/catalog/6161/get-microdata'
Invoke-Item 'temp/raw_downloads/ETH_2021_ESPS-W5_v02_M'
```

After accepting World Bank terms and placing the complete unchanged official
package under `temp/raw_downloads/ETH_2021_ESPS-W5_v02_M/`, run:

```bash
python script/177_build_priority_lsms_isa_manual_download_progress_tracker.py
python script/180_build_priority_lsms_isa_credentialed_download_handoff.py --idno ETH_2021_ESPS-W5_v02_M --probe
python script/180_build_priority_lsms_isa_credentialed_download_handoff.py --idno ETH_2021_ESPS-W5_v02_M --execute
python script/178_build_priority_lsms_isa_post_download_validation_runner.py --idno ETH_2021_ESPS-W5_v02_M
python script/178_build_priority_lsms_isa_post_download_validation_runner.py --idno ETH_2021_ESPS-W5_v02_M --execute
```

## Requirement Gates

| requirement | core_file_rows | core_matched_file_rows | core_missing_file_rows | requirement_acceptance_status |
| --- | --- | --- | --- | --- |
| climate_geography | 6 | 0 | 6 | blocked_missing_core_files |
| consumption_or_income | 1 | 0 | 1 | blocked_missing_core_files |
| health_need_and_access | 3 | 0 | 3 | blocked_missing_core_files |
| household_person_keys | 8 | 0 | 8 | blocked_missing_core_files |
| oop_health_expenditure | 2 | 0 | 2 | blocked_missing_core_files |
| survey_timing | 8 | 0 | 8 | blocked_missing_core_files |
| weights_and_design | 8 | 0 | 8 | blocked_missing_core_files |

## Core File Checklist

| file_id | expected_file_name | core_requirements | current_official_file_match_status | acceptance_gate_status |
| --- | --- | --- | --- | --- |
| F1 | sect_cover_hh_w5.dta | climate_geography;survey_timing;weights_and_design | missing_expected_official_file | missing_required_official_file |
| F2 | sect1_hh_w5.dta | household_person_keys | missing_expected_official_file | missing_required_official_file |
| F4 | sect3_hh_w5.dta | health_need_and_access;oop_health_expenditure | missing_expected_official_file | missing_required_official_file |
| F10 | sect6b2_hh_w5.dta | weights_and_design | missing_expected_official_file | missing_required_official_file |
| F11 | sect6b3_hh_w5.dta | weights_and_design | missing_expected_official_file | missing_required_official_file |
| F12 | sect6b4_hh_w5.dta | weights_and_design | missing_expected_official_file | missing_required_official_file |
| F13 | sect6c_hh_w5.dta | household_person_keys;weights_and_design | missing_expected_official_file | missing_required_official_file |
| F14 | sect7a_hh_w5.dta | weights_and_design | missing_expected_official_file | missing_required_official_file |
| F15 | sect7b_hh_w5.dta | survey_timing;weights_and_design | missing_expected_official_file | missing_required_official_file |
| F16 | sect8_hh_w5.dta | weights_and_design | missing_expected_official_file | missing_required_official_file |
| F21 | sect12b1_hh_w5.dta | household_person_keys;survey_timing | missing_expected_official_file | missing_required_official_file |
| F36 | sect04_com_w5.dta | health_need_and_access | missing_expected_official_file | missing_required_official_file |
| F42 | sect10a_com_w5.dta | climate_geography | missing_expected_official_file | missing_required_official_file |
| F46 | sect_cover_pp_w5.dta | climate_geography;survey_timing | missing_expected_official_file | missing_required_official_file |
| F47 | sect1_pp_w5.dta | household_person_keys | missing_expected_official_file | missing_required_official_file |
| F48 | sect2_pp_w5.dta | household_person_keys | missing_expected_official_file | missing_required_official_file |
| F49 | sect3_pp_w5.dta | climate_geography;health_need_and_access;household_person_keys | missing_expected_official_file | missing_required_official_file |
| F50 | sect4_pp_w5.dta | household_person_keys | missing_expected_official_file | missing_required_official_file |
| F54 | sect_cover_ph_w5.dta | climate_geography;survey_timing | missing_expected_official_file | missing_required_official_file |
| F55 | sect1_ph_w5.dta | household_person_keys | missing_expected_official_file | missing_required_official_file |
| F59 | sect_cover_ls_w5.dta | climate_geography;survey_timing | missing_expected_official_file | missing_required_official_file |
| F62 | sect8_3_ls_w5.dta | oop_health_expenditure | missing_expected_official_file | missing_required_official_file |
| F64 | eth_householdgeovariables_y5.dta | survey_timing | missing_expected_official_file | missing_required_official_file |
| F65 | eth_plotgeovariables_y5.dta | survey_timing | missing_expected_official_file | missing_required_official_file |
| F66 | cons_agg_w5.dta | consumption_or_income | missing_expected_official_file | missing_required_official_file |

## Outputs

- `result/priority_lsms_isa_first_canary_download_runbook.csv`
- `result/priority_lsms_isa_first_canary_core_file_checklist.csv`
- `result/priority_lsms_isa_first_canary_requirement_gate_checklist.csv`
- `result/priority_lsms_isa_first_canary_runbook_summary.csv`

## Stop Rule

Do not write a promoted dataset after the canary download alone. Promotion still
requires receipt, schema, value-profile, semantics, timing/geography, and
climate-linkage gates to pass.
