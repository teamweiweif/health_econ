# Priority LSMS/ISA Package-Level Download Manifest

Status: package-level download and receipt manifest for the 10 locked
World Bank LSMS/ISA targets that still need official raw packages.

This is the practical download view. The expected-file matrix has 838 official
file rows and 323 core rows, but the acquisition action is to download each
complete official microdata package after accepting World Bank terms, then
place it unchanged in the target folder or under `_incoming` for routing.

The manifest does not download files, extract archives, write `data/`, or open
any modeling gate.

## Summary

| metric | value | interpretation |
| --- | --- | --- |
| package_level_download_manifest_rows | 10 | Package-level rows for locked download-required country-waves. |
| package_level_download_country_rows | 5 | Countries covered by the package-level manifest. |
| package_level_download_priority_country_rows | 9 | Package-level rows from the five priority countries. |
| package_level_download_sixth_country_rows | 1 | Package-level rows supplying the sixth-country buffer. |
| package_level_download_expected_full_file_rows | 838 | Expected official file rows after complete packages are placed or extracted. |
| package_level_download_expected_core_file_rows | 323 | Requirement-linked core file rows after complete packages are placed or extracted. |
| package_level_download_unique_core_file_manifest_rows | 213 | Unique expected core files represented in the package-level core manifest. |
| package_level_download_requirement_gate_rows | 70 | Requirement-level gates covered by package receipt. |
| package_level_download_blocked_requirement_gate_rows | 70 | Requirement gates blocked until complete package receipt. |
| package_level_download_target_file_rows | 0 | Files currently present under exact target folders. |
| package_level_download_incoming_file_rows | 0 | Files currently staged under temp/raw_downloads/_incoming. |
| package_level_download_blocked_no_local_package_rows | 10 | Package rows still lacking local package or incoming files. |
| package_level_download_first_canary_idno | ETH_2021_ESPS-W5_v02_M | First package to download and validate before scaling. |
| data_write_gate_status | blocked_no_data_write | The manifest does not write promoted data. |
| modeling_gate_status | blocked | No predictive, reduced-form, causal ML, or policy learning is opened. |

## Package Rows

| download_rank | country | wave | idno | package_receipt_status | target_file_count | incoming_file_rows | expected_full_file_rows | expected_core_file_rows | unique_core_file_rows | expected_requirement_gate_rows |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Ethiopia | 2021-2022 | ETH_2021_ESPS-W5_v02_M | blocked_no_local_package_or_incoming_files | 0 | 0 | 68 | 36 | 25 | 7 |
| 2 | Ethiopia | 2018-2019 | ETH_2018_ESS_v04_M | blocked_no_local_package_or_incoming_files | 0 | 0 | 68 | 35 | 23 | 7 |
| 3 | Nigeria | 2012-2013 | NGA_2012_GHSP-W2_v02_M | blocked_no_local_package_or_incoming_files | 0 | 0 | 103 | 26 | 16 | 7 |
| 4 | Nigeria | 2015-2016 | NGA_2015_GHSP-W3_v02_M | blocked_no_local_package_or_incoming_files | 0 | 0 | 104 | 26 | 18 | 7 |
| 5 | Nigeria | 2010-2011 | NGA_2010_GHSP-W1_v03_M | blocked_no_local_package_or_incoming_files | 0 | 0 | 99 | 27 | 16 | 7 |
| 6 | Tanzania | 2008-2009 | TZA_2008_NPS-R1_v03_M | blocked_no_local_package_or_incoming_files | 0 | 0 | 61 | 35 | 22 | 7 |
| 7 | Tanzania | 2010-2011 | TZA_2010_NPS-R2_v03_M | blocked_no_local_package_or_incoming_files | 0 | 0 | 95 | 38 | 23 | 7 |
| 8 | Tanzania | 2012-2013 | TZA_2012_NPS-R3_v01_M | blocked_no_local_package_or_incoming_files | 0 | 0 | 80 | 33 | 23 | 7 |
| 9 | Uganda | 2019-2020 | UGA_2019_UNPS_v03_M | blocked_no_local_package_or_incoming_files | 0 | 0 | 109 | 39 | 27 | 7 |
| 10 | Nepal | 2010-2011 | NPL_2010_LSS-III_v01_M | blocked_no_local_package_or_incoming_files | 0 | 0 | 51 | 28 | 20 | 7 |

## Core File Preview

| download_rank | idno | expected_file_name | core_requirements | package_receipt_status |
| --- | --- | --- | --- | --- |
| 1 | ETH_2021_ESPS-W5_v02_M | sect_cover_hh_w5.dta | climate_geography;survey_timing;weights_and_design | blocked_no_local_package_or_incoming_files |
| 1 | ETH_2021_ESPS-W5_v02_M | sect6b2_hh_w5.dta | weights_and_design | blocked_no_local_package_or_incoming_files |
| 1 | ETH_2021_ESPS-W5_v02_M | sect6b3_hh_w5.dta | weights_and_design | blocked_no_local_package_or_incoming_files |
| 1 | ETH_2021_ESPS-W5_v02_M | sect6b4_hh_w5.dta | weights_and_design | blocked_no_local_package_or_incoming_files |
| 1 | ETH_2021_ESPS-W5_v02_M | sect6c_hh_w5.dta | household_person_keys;weights_and_design | blocked_no_local_package_or_incoming_files |
| 1 | ETH_2021_ESPS-W5_v02_M | sect7a_hh_w5.dta | weights_and_design | blocked_no_local_package_or_incoming_files |
| 1 | ETH_2021_ESPS-W5_v02_M | sect7b_hh_w5.dta | survey_timing;weights_and_design | blocked_no_local_package_or_incoming_files |
| 1 | ETH_2021_ESPS-W5_v02_M | sect8_hh_w5.dta | weights_and_design | blocked_no_local_package_or_incoming_files |
| 1 | ETH_2021_ESPS-W5_v02_M | sect1_hh_w5.dta | household_person_keys | blocked_no_local_package_or_incoming_files |
| 1 | ETH_2021_ESPS-W5_v02_M | sect12b1_hh_w5.dta | household_person_keys;survey_timing | blocked_no_local_package_or_incoming_files |
| 1 | ETH_2021_ESPS-W5_v02_M | sect04_com_w5.dta | health_need_and_access | blocked_no_local_package_or_incoming_files |
| 1 | ETH_2021_ESPS-W5_v02_M | sect3_hh_w5.dta | health_need_and_access;oop_health_expenditure | blocked_no_local_package_or_incoming_files |
| 1 | ETH_2021_ESPS-W5_v02_M | sect10a_com_w5.dta | climate_geography | blocked_no_local_package_or_incoming_files |
| 1 | ETH_2021_ESPS-W5_v02_M | sect_cover_pp_w5.dta | climate_geography;survey_timing | blocked_no_local_package_or_incoming_files |
| 1 | ETH_2021_ESPS-W5_v02_M | sect1_pp_w5.dta | household_person_keys | blocked_no_local_package_or_incoming_files |
| 1 | ETH_2021_ESPS-W5_v02_M | sect2_pp_w5.dta | household_person_keys | blocked_no_local_package_or_incoming_files |
| 1 | ETH_2021_ESPS-W5_v02_M | sect3_pp_w5.dta | climate_geography;health_need_and_access;household_person_keys | blocked_no_local_package_or_incoming_files |
| 1 | ETH_2021_ESPS-W5_v02_M | sect4_pp_w5.dta | household_person_keys | blocked_no_local_package_or_incoming_files |
| 1 | ETH_2021_ESPS-W5_v02_M | sect_cover_ph_w5.dta | climate_geography;survey_timing | blocked_no_local_package_or_incoming_files |
| 1 | ETH_2021_ESPS-W5_v02_M | sect1_ph_w5.dta | household_person_keys | blocked_no_local_package_or_incoming_files |
| 1 | ETH_2021_ESPS-W5_v02_M | sect_cover_ls_w5.dta | climate_geography;survey_timing | blocked_no_local_package_or_incoming_files |
| 1 | ETH_2021_ESPS-W5_v02_M | sect8_3_ls_w5.dta | oop_health_expenditure | blocked_no_local_package_or_incoming_files |
| 1 | ETH_2021_ESPS-W5_v02_M | eth_householdgeovariables_y5.dta | survey_timing | blocked_no_local_package_or_incoming_files |
| 1 | ETH_2021_ESPS-W5_v02_M | eth_plotgeovariables_y5.dta | survey_timing | blocked_no_local_package_or_incoming_files |
| 1 | ETH_2021_ESPS-W5_v02_M | cons_agg_w5.dta | consumption_or_income | blocked_no_local_package_or_incoming_files |
| 2 | ETH_2018_ESS_v04_M | sect_cover_hh_w4.dta | climate_geography;survey_timing;weights_and_design | blocked_no_local_package_or_incoming_files |
| 2 | ETH_2018_ESS_v04_M | sect6b2_hh_w4.dta | weights_and_design | blocked_no_local_package_or_incoming_files |
| 2 | ETH_2018_ESS_v04_M | sect7a_hh_w4.dta | consumption_or_income;weights_and_design | blocked_no_local_package_or_incoming_files |
| 2 | ETH_2018_ESS_v04_M | sect9_hh_w4.dta | weights_and_design | blocked_no_local_package_or_incoming_files |
| 2 | ETH_2018_ESS_v04_M | sect1_hh_w4.dta | household_person_keys;weights_and_design | blocked_no_local_package_or_incoming_files |
| 2 | ETH_2018_ESS_v04_M | sect10b_hh_w4.dta | household_person_keys | blocked_no_local_package_or_incoming_files |
| 2 | ETH_2018_ESS_v04_M | sect10d1_hh_w4.dta | household_person_keys;weights_and_design | blocked_no_local_package_or_incoming_files |
| 2 | ETH_2018_ESS_v04_M | sect11b1_hh_w4.dta | household_person_keys | blocked_no_local_package_or_incoming_files |
| 2 | ETH_2018_ESS_v04_M | sect12b1_hh_w4.dta | survey_timing | blocked_no_local_package_or_incoming_files |
| 2 | ETH_2018_ESS_v04_M | sect15b_hh_w4.dta | survey_timing | blocked_no_local_package_or_incoming_files |
| 2 | ETH_2018_ESS_v04_M | sect_cover_ls_w4.dta | climate_geography;survey_timing | blocked_no_local_package_or_incoming_files |
| 2 | ETH_2018_ESS_v04_M | sect8_3_ls_w4.dta | oop_health_expenditure | blocked_no_local_package_or_incoming_files |
| 2 | ETH_2018_ESS_v04_M | sect_cover_ph_w4.dta | climate_geography;survey_timing;weights_and_design | blocked_no_local_package_or_incoming_files |
| 2 | ETH_2018_ESS_v04_M | sect3_hh_w4.dta | health_need_and_access;oop_health_expenditure | blocked_no_local_package_or_incoming_files |
| 2 | ETH_2018_ESS_v04_M | sect1_ph_w4.dta | household_person_keys | blocked_no_local_package_or_incoming_files |
| 2 | ETH_2018_ESS_v04_M | sect_cover_pp_w4.dta | climate_geography;survey_timing;weights_and_design | blocked_no_local_package_or_incoming_files |
| 2 | ETH_2018_ESS_v04_M | sect1_pp_w4.dta | household_person_keys | blocked_no_local_package_or_incoming_files |
| 2 | ETH_2018_ESS_v04_M | sect2_pp_w4.dta | household_person_keys | blocked_no_local_package_or_incoming_files |
| 2 | ETH_2018_ESS_v04_M | sect3_pp_w4.dta | climate_geography;household_person_keys | blocked_no_local_package_or_incoming_files |
| 2 | ETH_2018_ESS_v04_M | sect04_com_w4.dta | health_need_and_access | blocked_no_local_package_or_incoming_files |
| 2 | ETH_2018_ESS_v04_M | cons_agg_w4.dta | consumption_or_income | blocked_no_local_package_or_incoming_files |
| 2 | ETH_2018_ESS_v04_M | ETH_HouseholdGeovariables_Y4.dta | survey_timing | blocked_no_local_package_or_incoming_files |
| 2 | ETH_2018_ESS_v04_M | sect10a_com_w4.dta | climate_geography | blocked_no_local_package_or_incoming_files |
| 3 | NGA_2012_GHSP-W2_v02_M | secta7_harvestw2 | health_need_and_access | blocked_no_local_package_or_incoming_files |
| 3 | NGA_2012_GHSP-W2_v02_M | secta10_harvestw2 | household_person_keys | blocked_no_local_package_or_incoming_files |
| ... | ... | ... | ... | ... |

## Receipt Rule

Download the complete unchanged official package for each row. If the browser
download name is not known in advance, keep the original downloaded archive name
and place it in the target folder listed in the manifest. After local placement,
run the receipt validation chain before any extraction-derived promotion,
value-review, climate-linkage, or data-write step.
