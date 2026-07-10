# Priority LSMS-ISA Download Acceptance Matrix

Status: receipt checklist for the 10 remaining minimum-batch official raw packages.

This matrix converts the official file manifest and requirement-linked core files into a file-by-file acceptance checklist. It does not download, copy, extract, write promoted `data/`, or run models.

## Summary

- Packet datasets: 10
- Expected official files: 838
- Requirement-level rows: 70
- Requirement-linked core file rows: 323
- Missing expected files: 838
- Ready requirement rows: 0
- Public route raw payload candidates: 0
- Data-write gate: blocked_no_data_write
- Modeling gate: blocked

## Dataset Acceptance Status

| download_rank | country | wave | idno | expected_files | missing_files | core_requirements | blocked_requirements |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Ethiopia | 2021-2022 | ETH_2021_ESPS-W5_v02_M | 68 | 68 | 7 | 7 |
| 2 | Ethiopia | 2018-2019 | ETH_2018_ESS_v04_M | 68 | 68 | 7 | 7 |
| 3 | Nigeria | 2012-2013 | NGA_2012_GHSP-W2_v02_M | 103 | 103 | 7 | 7 |
| 4 | Nigeria | 2015-2016 | NGA_2015_GHSP-W3_v02_M | 104 | 104 | 7 | 7 |
| 5 | Nigeria | 2010-2011 | NGA_2010_GHSP-W1_v03_M | 99 | 99 | 7 | 7 |
| 6 | Tanzania | 2008-2009 | TZA_2008_NPS-R1_v03_M | 61 | 61 | 7 | 7 |
| 7 | Tanzania | 2010-2011 | TZA_2010_NPS-R2_v03_M | 95 | 95 | 7 | 7 |
| 8 | Tanzania | 2012-2013 | TZA_2012_NPS-R3_v01_M | 80 | 80 | 7 | 7 |
| 9 | Uganda | 2019-2020 | UGA_2019_UNPS_v03_M | 109 | 109 | 7 | 7 |
| 10 | Nepal | 2010-2011 | NPL_2010_LSS-III_v01_M | 51 | 51 | 7 | 7 |

## Requirement Preview

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
| ... | ... | ... | ... | ... | ... |

## File Preview

| download_rank | idno | file_id | expected_file_name | priority_core_target | core_requirements | acceptance_gate_status |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | ETH_2021_ESPS-W5_v02_M | F1 | sect_cover_hh_w5.dta | 1 | climate_geography;survey_timing;weights_and_design | missing_required_official_file |
| 1 | ETH_2021_ESPS-W5_v02_M | F10 | sect6b2_hh_w5.dta | 1 | weights_and_design | missing_required_official_file |
| 1 | ETH_2021_ESPS-W5_v02_M | F11 | sect6b3_hh_w5.dta | 1 | weights_and_design | missing_required_official_file |
| 1 | ETH_2021_ESPS-W5_v02_M | F12 | sect6b4_hh_w5.dta | 1 | weights_and_design | missing_required_official_file |
| 1 | ETH_2021_ESPS-W5_v02_M | F13 | sect6c_hh_w5.dta | 1 | household_person_keys;weights_and_design | missing_required_official_file |
| 1 | ETH_2021_ESPS-W5_v02_M | F14 | sect7a_hh_w5.dta | 1 | weights_and_design | missing_required_official_file |
| 1 | ETH_2021_ESPS-W5_v02_M | F15 | sect7b_hh_w5.dta | 1 | survey_timing;weights_and_design | missing_required_official_file |
| 1 | ETH_2021_ESPS-W5_v02_M | F16 | sect8_hh_w5.dta | 1 | weights_and_design | missing_required_official_file |
| 1 | ETH_2021_ESPS-W5_v02_M | F17 | sect9_hh_w5.dta | 0 |  | missing_required_official_file |
| 1 | ETH_2021_ESPS-W5_v02_M | F18 | sect10a_hh_w5.dta | 0 |  | missing_required_official_file |
| 1 | ETH_2021_ESPS-W5_v02_M | F19 | sect11_hh_w5.dta | 0 |  | missing_required_official_file |
| 1 | ETH_2021_ESPS-W5_v02_M | F2 | sect1_hh_w5.dta | 1 | household_person_keys | missing_required_official_file |
| 1 | ETH_2021_ESPS-W5_v02_M | F20 | sect12a_hh_w5.dta | 0 |  | missing_required_official_file |
| 1 | ETH_2021_ESPS-W5_v02_M | F21 | sect12b1_hh_w5.dta | 1 | household_person_keys;survey_timing | missing_required_official_file |
| 1 | ETH_2021_ESPS-W5_v02_M | F22 | sect12b2_hh_w5.dta | 0 |  | missing_required_official_file |
| 1 | ETH_2021_ESPS-W5_v02_M | F23 | sect12c_hh_w5.dta | 0 |  | missing_required_official_file |
| 1 | ETH_2021_ESPS-W5_v02_M | F24 | sect12c_q1_hh_w5.dta | 0 |  | missing_required_official_file |
| 1 | ETH_2021_ESPS-W5_v02_M | F25 | sect12d_hh_w5.dta | 0 |  | missing_required_official_file |
| 1 | ETH_2021_ESPS-W5_v02_M | F26 | sect12e_hh_w5.dta | 0 |  | missing_required_official_file |
| 1 | ETH_2021_ESPS-W5_v02_M | F27 | sect12f_hh_w5.dta | 0 |  | missing_required_official_file |
| 1 | ETH_2021_ESPS-W5_v02_M | F28 | sect13_hh_w5.dta | 0 |  | missing_required_official_file |
| 1 | ETH_2021_ESPS-W5_v02_M | F29 | sect14_hh_w5.dta | 0 |  | missing_required_official_file |
| 1 | ETH_2021_ESPS-W5_v02_M | F3 | sect2_hh_w5.dta | 0 |  | missing_required_official_file |
| 1 | ETH_2021_ESPS-W5_v02_M | F30 | sect15a_hh_w5.dta | 0 |  | missing_required_official_file |
| 1 | ETH_2021_ESPS-W5_v02_M | F31 | sect15b_hh_w5.dta | 0 |  | missing_required_official_file |
| 1 | ETH_2021_ESPS-W5_v02_M | F32 | sect01a_com_w5.dta | 0 |  | missing_required_official_file |
| 1 | ETH_2021_ESPS-W5_v02_M | F33 | sect01b_com_w5.dta | 0 |  | missing_required_official_file |
| 1 | ETH_2021_ESPS-W5_v02_M | F34 | sect02_com_w5.dta | 0 |  | missing_required_official_file |
| 1 | ETH_2021_ESPS-W5_v02_M | F35 | sect03_com_w5.dta | 0 |  | missing_required_official_file |
| 1 | ETH_2021_ESPS-W5_v02_M | F36 | sect04_com_w5.dta | 1 | health_need_and_access | missing_required_official_file |
| 1 | ETH_2021_ESPS-W5_v02_M | F37 | sect05_com_w5.dta | 0 |  | missing_required_official_file |
| 1 | ETH_2021_ESPS-W5_v02_M | F38 | sect06_com_w5.dta | 0 |  | missing_required_official_file |
| 1 | ETH_2021_ESPS-W5_v02_M | F39 | sect07_com_w5.dta | 0 |  | missing_required_official_file |
| 1 | ETH_2021_ESPS-W5_v02_M | F4 | sect3_hh_w5.dta | 1 | health_need_and_access;oop_health_expenditure | missing_required_official_file |
| 1 | ETH_2021_ESPS-W5_v02_M | F40 | sect08_com_w5.dta | 0 |  | missing_required_official_file |
| 1 | ETH_2021_ESPS-W5_v02_M | F41 | sect09_com_w5.dta | 0 |  | missing_required_official_file |
| 1 | ETH_2021_ESPS-W5_v02_M | F42 | sect10a_com_w5.dta | 1 | climate_geography | missing_required_official_file |
| 1 | ETH_2021_ESPS-W5_v02_M | F43 | sect10b_com_w5.dta | 0 |  | missing_required_official_file |
| 1 | ETH_2021_ESPS-W5_v02_M | F44 | sect11_com_w5.dta | 0 |  | missing_required_official_file |
| 1 | ETH_2021_ESPS-W5_v02_M | F45 | sect12_com_w5.dta | 0 |  | missing_required_official_file |
| 1 | ETH_2021_ESPS-W5_v02_M | F46 | sect_cover_pp_w5.dta | 1 | climate_geography;survey_timing | missing_required_official_file |
| 1 | ETH_2021_ESPS-W5_v02_M | F47 | sect1_pp_w5.dta | 1 | household_person_keys | missing_required_official_file |
| 1 | ETH_2021_ESPS-W5_v02_M | F48 | sect2_pp_w5.dta | 1 | household_person_keys | missing_required_official_file |
| 1 | ETH_2021_ESPS-W5_v02_M | F49 | sect3_pp_w5.dta | 1 | climate_geography;health_need_and_access;household_person_keys | missing_required_official_file |
| 1 | ETH_2021_ESPS-W5_v02_M | F5 | sect3b_hh_w5.dta | 0 |  | missing_required_official_file |
| 1 | ETH_2021_ESPS-W5_v02_M | F50 | sect4_pp_w5.dta | 1 | household_person_keys | missing_required_official_file |
| 1 | ETH_2021_ESPS-W5_v02_M | F51 | sect5_pp_w5.dta | 0 |  | missing_required_official_file |
| 1 | ETH_2021_ESPS-W5_v02_M | F52 | sect7_pp_w5.dta | 0 |  | missing_required_official_file |
| 1 | ETH_2021_ESPS-W5_v02_M | F53 | sect9a_pp_w5.dta | 0 |  | missing_required_official_file |
| 1 | ETH_2021_ESPS-W5_v02_M | F54 | sect_cover_ph_w5.dta | 1 | climate_geography;survey_timing | missing_required_official_file |
| 1 | ETH_2021_ESPS-W5_v02_M | F55 | sect1_ph_w5.dta | 1 | household_person_keys | missing_required_official_file |
| 1 | ETH_2021_ESPS-W5_v02_M | F56 | sect9_ph_w5.dta | 0 |  | missing_required_official_file |
| 1 | ETH_2021_ESPS-W5_v02_M | F57 | sect10_ph_w5.dta | 0 |  | missing_required_official_file |
| 1 | ETH_2021_ESPS-W5_v02_M | F58 | sect11_ph_w5.dta | 0 |  | missing_required_official_file |
| 1 | ETH_2021_ESPS-W5_v02_M | F59 | sect_cover_ls_w5.dta | 1 | climate_geography;survey_timing | missing_required_official_file |
| 1 | ETH_2021_ESPS-W5_v02_M | F6 | sect4_hh_w5.dta | 0 |  | missing_required_official_file |
| 1 | ETH_2021_ESPS-W5_v02_M | F60 | sect8_1_ls_w5.dta | 0 |  | missing_required_official_file |
| 1 | ETH_2021_ESPS-W5_v02_M | F61 | sect8_2_ls_w5.dta | 0 |  | missing_required_official_file |
| 1 | ETH_2021_ESPS-W5_v02_M | F62 | sect8_3_ls_w5.dta | 1 | oop_health_expenditure | missing_required_official_file |
| 1 | ETH_2021_ESPS-W5_v02_M | F63 | sect8_4_ls_w5.dta | 0 |  | missing_required_official_file |
| ... | ... | ... | ... | ... | ... | ... |

## Use

After a complete official package is placed in the packet target folder, rerun the raw-download audit, archive preflight, official file receipt validator, and this script. A wave must have all required files and requirement rows present before raw value, units, recall, missing-code, skip-pattern, merge-key, and design checks can promote it.
