# Priority LSMS-ISA Credentialed Raw Acquisition Workbench

Status: 19-wave credentialed acquisition workbench for the refocused LSMS/ISA
promotion queue. It translates public official metadata into the manual login
download package, full-file manifest, core-file confirmation checklist, and
post-download validation commands.

This workbench does not bypass account, registration, terms, or request gates
and does not treat metadata as raw data.

## Summary

| Metric | Value | Interpretation |
|---|---:|---|
| priority_lsms_credentialed_workbench_dataset_rows | 19 | Refocused LSMS/ISA datasets covered by credentialed acquisition workbench. |
| priority_lsms_credentialed_workbench_full_file_rows | 1597 | Official DDI file-description rows carried into full-file download review. |
| priority_lsms_credentialed_workbench_core_file_rows | 629 | Requirement/file rows to confirm after official raw download. |
| priority_lsms_credentialed_workbench_access_gate_rows | 19 | Datasets whose get-microdata page shows account, registration, terms, or request language. |
| priority_lsms_credentialed_workbench_package_received_rows | 1 | Datasets with at least one original non-generated package or documentation file already present. |
| priority_lsms_credentialed_workbench_targets_missing_before_download | 592 | Core requirement/file rows still missing before credentialed download. |
| priority_lsms_credentialed_workbench_handoff_readmes_written | 19 | Per-wave credentialed acquisition workbench handoffs written. |
| priority_lsms_credentialed_workbench_data_write_status | blocked_no_promoted_rows | Credentialed acquisition workbench does not permit data/ writes. |
| modeling_gate_status | blocked | Models remain blocked until raw-backed promotion thresholds and accepted climate linkage pass. |
| priority_lsms_credentialed_workbench_queue_role_core_replacement_primary | 2 | Dataset count by refocused queue role. |
| priority_lsms_credentialed_workbench_queue_role_core_selected_lsms_isa_aligned | 8 | Dataset count by refocused queue role. |
| priority_lsms_credentialed_workbench_queue_role_replacement_backup_wave | 6 | Dataset count by refocused queue role. |
| priority_lsms_credentialed_workbench_queue_role_sixth_country_backup_candidate | 3 | Dataset count by refocused queue role. |
| priority_lsms_credentialed_workbench_status_ready_for_credentialed_manual_download | 19 | Credentialed acquisition status count. |

## Dataset Workbench Preview

| download_priority_order | idno | country | wave | official_full_file_rows | core_file_checklist_rows | current_receipt_status | credentialed_acquisition_status |
|---|---|---|---|---|---|---|---|
| 1 | ETH_2021_ESPS-W5_v02_M | Ethiopia | 2021-2022 | 68 | 36 | blocked_no_original_package | ready_for_credentialed_manual_download |
| 2 | ETH_2018_ESS_v04_M | Ethiopia | 2018-2019 | 68 | 35 | blocked_no_original_package | ready_for_credentialed_manual_download |
| 3 | MWI_2004_IHS-II_v01_M | Malawi | 2004-2005 | 52 | 37 | ready_for_raw_value_review | ready_for_credentialed_manual_download |
| 4 | NGA_2012_GHSP-W2_v02_M | Nigeria | 2012-2013 | 103 | 26 | blocked_no_original_package | ready_for_credentialed_manual_download |
| 5 | NGA_2015_GHSP-W3_v02_M | Nigeria | 2015-2016 | 104 | 26 | blocked_no_original_package | ready_for_credentialed_manual_download |
| 6 | NGA_2010_GHSP-W1_v03_M | Nigeria | 2010-2011 | 99 | 27 | blocked_no_original_package | ready_for_credentialed_manual_download |
| 7 | TZA_2008_NPS-R1_v03_M | Tanzania | 2008-2009 | 61 | 35 | blocked_no_original_package | ready_for_credentialed_manual_download |
| 8 | TZA_2010_NPS-R2_v03_M | Tanzania | 2010-2011 | 95 | 38 | blocked_no_original_package | ready_for_credentialed_manual_download |
| 9 | TZA_2012_NPS-R3_v01_M | Tanzania | 2012-2013 | 80 | 33 | blocked_no_original_package | ready_for_credentialed_manual_download |
| 10 | UGA_2019_UNPS_v03_M | Uganda | 2019-2020 | 109 | 39 | blocked_no_original_package | ready_for_credentialed_manual_download |
| 11 | JAM_1997_SLC_v01_M | Jamaica | 1997 | 68 | 32 | blocked_no_original_package | ready_for_credentialed_manual_download |
| 12 | KGZ_1993_KMPS_v01_M | Kyrgyz Republic | 1993 | 15 | 31 | blocked_no_original_package | ready_for_credentialed_manual_download |
| 13 | NPL_2010_LSS-III_v01_M | Nepal | 2010-2011 | 51 | 28 | blocked_no_original_package | ready_for_credentialed_manual_download |
| 14 | MWI_2019_IHS-V_v06_M | Malawi | 2019-2020 | 108 | 35 | blocked_no_original_package | ready_for_credentialed_manual_download |
| 15 | MWI_2016_IHS-IV_v04_M | Malawi | 2016-2017 | 99 | 35 | blocked_no_original_package | ready_for_credentialed_manual_download |
| 16 | MWI_2010_IHS-III_v01_M | Malawi | 2010-2011 | 85 | 36 | blocked_no_original_package | ready_for_credentialed_manual_download |
| 17 | UGA_2011_UNPS_v02_M | Uganda | 2011-2012 | 103 | 32 | blocked_no_original_package | ready_for_credentialed_manual_download |
| 18 | UGA_2018_UNPS_v02_M | Uganda | 2018-2019 | 109 | 34 | blocked_no_original_package | ready_for_credentialed_manual_download |
| 19 | UGA_2015_UNPS_v02_M | Uganda | 2015-2016 | 120 | 34 | blocked_no_original_package | ready_for_credentialed_manual_download |

## Core File Checklist Preview

| download_priority_order | idno | requirement | file_rank | file_name | candidate_variable_rows | current_receipt_status |
|---|---|---|---|---|---|---|
| 1 | ETH_2021_ESPS-W5_v02_M | climate_geography | 1 | sect_cover_hh_w5.dta | 2 | blocked_no_original_package |
| 1 | ETH_2021_ESPS-W5_v02_M | climate_geography | 2 | sect10a_com_w5.dta | 2 | blocked_no_original_package |
| 1 | ETH_2021_ESPS-W5_v02_M | climate_geography | 3 | sect_cover_pp_w5.dta | 2 | blocked_no_original_package |
| 1 | ETH_2021_ESPS-W5_v02_M | climate_geography | 4 | sect_cover_ph_w5.dta | 2 | blocked_no_original_package |
| 1 | ETH_2021_ESPS-W5_v02_M | climate_geography | 5 | sect_cover_ls_w5.dta | 2 | blocked_no_original_package |
| 1 | ETH_2021_ESPS-W5_v02_M | climate_geography | 6 | sect3_pp_w5.dta | 2 | blocked_no_original_package |
| 1 | ETH_2021_ESPS-W5_v02_M | consumption_or_income | 1 | cons_agg_w5.dta | 12 | blocked_no_original_package |
| 1 | ETH_2021_ESPS-W5_v02_M | health_need_and_access | 1 | sect3_hh_w5.dta | 6 | blocked_no_original_package |
| 1 | ETH_2021_ESPS-W5_v02_M | health_need_and_access | 2 | sect04_com_w5.dta | 4 | blocked_no_original_package |
| 1 | ETH_2021_ESPS-W5_v02_M | health_need_and_access | 3 | sect3_pp_w5.dta | 2 | blocked_no_original_package |
| 1 | ETH_2021_ESPS-W5_v02_M | household_person_keys | 1 | sect1_hh_w5.dta | 2 | blocked_no_original_package |
| 1 | ETH_2021_ESPS-W5_v02_M | household_person_keys | 2 | sect12b1_hh_w5.dta | 1 | blocked_no_original_package |
| 1 | ETH_2021_ESPS-W5_v02_M | household_person_keys | 3 | sect1_pp_w5.dta | 1 | blocked_no_original_package |
| 1 | ETH_2021_ESPS-W5_v02_M | household_person_keys | 4 | sect1_ph_w5.dta | 1 | blocked_no_original_package |
| 1 | ETH_2021_ESPS-W5_v02_M | household_person_keys | 5 | sect2_pp_w5.dta | 1 | blocked_no_original_package |
| 1 | ETH_2021_ESPS-W5_v02_M | household_person_keys | 6 | sect3_pp_w5.dta | 1 | blocked_no_original_package |
| 1 | ETH_2021_ESPS-W5_v02_M | household_person_keys | 7 | sect4_pp_w5.dta | 1 | blocked_no_original_package |
| 1 | ETH_2021_ESPS-W5_v02_M | household_person_keys | 8 | sect6c_hh_w5.dta | 1 | blocked_no_original_package |
| 1 | ETH_2021_ESPS-W5_v02_M | oop_health_expenditure | 1 | sect8_3_ls_w5.dta | 10 | blocked_no_original_package |
| 1 | ETH_2021_ESPS-W5_v02_M | oop_health_expenditure | 2 | sect3_hh_w5.dta | 2 | blocked_no_original_package |
| 1 | ETH_2021_ESPS-W5_v02_M | survey_timing | 1 | sect_cover_pp_w5.dta | 1 | blocked_no_original_package |
| 1 | ETH_2021_ESPS-W5_v02_M | survey_timing | 2 | sect_cover_ph_w5.dta | 1 | blocked_no_original_package |
| 1 | ETH_2021_ESPS-W5_v02_M | survey_timing | 3 | sect_cover_ls_w5.dta | 1 | blocked_no_original_package |
| 1 | ETH_2021_ESPS-W5_v02_M | survey_timing | 4 | sect12b1_hh_w5.dta | 2 | blocked_no_original_package |
| 1 | ETH_2021_ESPS-W5_v02_M | survey_timing | 5 | sect7b_hh_w5.dta | 2 | blocked_no_original_package |
| 1 | ETH_2021_ESPS-W5_v02_M | survey_timing | 6 | eth_householdgeovariables_y5.dta | 1 | blocked_no_original_package |
| 1 | ETH_2021_ESPS-W5_v02_M | survey_timing | 7 | sect_cover_hh_w5.dta | 1 | blocked_no_original_package |
| 1 | ETH_2021_ESPS-W5_v02_M | survey_timing | 8 | eth_plotgeovariables_y5.dta | 1 | blocked_no_original_package |
| 1 | ETH_2021_ESPS-W5_v02_M | weights_and_design | 1 | sect_cover_hh_w5.dta | 2 | blocked_no_original_package |
| 1 | ETH_2021_ESPS-W5_v02_M | weights_and_design | 2 | sect6b2_hh_w5.dta | 1 | blocked_no_original_package |
| 1 | ETH_2021_ESPS-W5_v02_M | weights_and_design | 3 | sect6b3_hh_w5.dta | 1 | blocked_no_original_package |
| 1 | ETH_2021_ESPS-W5_v02_M | weights_and_design | 4 | sect6b4_hh_w5.dta | 1 | blocked_no_original_package |
| 1 | ETH_2021_ESPS-W5_v02_M | weights_and_design | 5 | sect6c_hh_w5.dta | 1 | blocked_no_original_package |
| 1 | ETH_2021_ESPS-W5_v02_M | weights_and_design | 6 | sect7a_hh_w5.dta | 1 | blocked_no_original_package |
| 1 | ETH_2021_ESPS-W5_v02_M | weights_and_design | 7 | sect7b_hh_w5.dta | 1 | blocked_no_original_package |
| 1 | ETH_2021_ESPS-W5_v02_M | weights_and_design | 8 | sect8_hh_w5.dta | 1 | blocked_no_original_package |
| 2 | ETH_2018_ESS_v04_M | climate_geography | 1 | sect_cover_ph_w4.dta | 3 | blocked_no_original_package |
| 2 | ETH_2018_ESS_v04_M | climate_geography | 2 | sect_cover_pp_w4.dta | 2 | blocked_no_original_package |
| 2 | ETH_2018_ESS_v04_M | climate_geography | 3 | sect_cover_ls_w4.dta | 2 | blocked_no_original_package |
| 2 | ETH_2018_ESS_v04_M | climate_geography | 4 | sect3_pp_w4.dta | 2 | blocked_no_original_package |
| 2 | ETH_2018_ESS_v04_M | climate_geography | 5 | sect10a_com_w4.dta | 2 | blocked_no_original_package |
| 2 | ETH_2018_ESS_v04_M | climate_geography | 6 | sect_cover_hh_w4.dta | 1 | blocked_no_original_package |
| 2 | ETH_2018_ESS_v04_M | consumption_or_income | 1 | sect7a_hh_w4.dta | 9 | blocked_no_original_package |
| 2 | ETH_2018_ESS_v04_M | consumption_or_income | 2 | cons_agg_w4.dta | 3 | blocked_no_original_package |
| 2 | ETH_2018_ESS_v04_M | health_need_and_access | 1 | sect3_hh_w4.dta | 11 | blocked_no_original_package |
| 2 | ETH_2018_ESS_v04_M | health_need_and_access | 2 | sect04_com_w4.dta | 1 | blocked_no_original_package |
| 2 | ETH_2018_ESS_v04_M | household_person_keys | 1 | sect1_hh_w4.dta | 2 | blocked_no_original_package |
| 2 | ETH_2018_ESS_v04_M | household_person_keys | 2 | sect11b1_hh_w4.dta | 2 | blocked_no_original_package |
| 2 | ETH_2018_ESS_v04_M | household_person_keys | 3 | sect10d1_hh_w4.dta | 1 | blocked_no_original_package |
| 2 | ETH_2018_ESS_v04_M | household_person_keys | 4 | sect1_ph_w4.dta | 1 | blocked_no_original_package |
| 2 | ETH_2018_ESS_v04_M | household_person_keys | 5 | sect1_pp_w4.dta | 1 | blocked_no_original_package |
| 2 | ETH_2018_ESS_v04_M | household_person_keys | 6 | sect10b_hh_w4.dta | 1 | blocked_no_original_package |
| 2 | ETH_2018_ESS_v04_M | household_person_keys | 7 | sect2_pp_w4.dta | 1 | blocked_no_original_package |
| 2 | ETH_2018_ESS_v04_M | household_person_keys | 8 | sect3_pp_w4.dta | 1 | blocked_no_original_package |
| 2 | ETH_2018_ESS_v04_M | oop_health_expenditure | 1 | sect8_3_ls_w4.dta | 10 | blocked_no_original_package |
| 2 | ETH_2018_ESS_v04_M | oop_health_expenditure | 2 | sect3_hh_w4.dta | 2 | blocked_no_original_package |
| 2 | ETH_2018_ESS_v04_M | survey_timing | 1 | sect_cover_ph_w4.dta | 2 | blocked_no_original_package |
| 2 | ETH_2018_ESS_v04_M | survey_timing | 2 | sect_cover_pp_w4.dta | 2 | blocked_no_original_package |
| 2 | ETH_2018_ESS_v04_M | survey_timing | 3 | sect_cover_ls_w4.dta | 2 | blocked_no_original_package |
| 2 | ETH_2018_ESS_v04_M | survey_timing | 4 | sect12b1_hh_w4.dta | 2 | blocked_no_original_package |
| 2 | ETH_2018_ESS_v04_M | survey_timing | 5 | ETH_HouseholdGeovariables_Y4.dta | 2 | blocked_no_original_package |
| 2 | ETH_2018_ESS_v04_M | survey_timing | 6 | sect_cover_hh_w4.dta | 1 | blocked_no_original_package |
| 2 | ETH_2018_ESS_v04_M | survey_timing | 7 | sect15b_hh_w4.dta | 1 | blocked_no_original_package |
| 2 | ETH_2018_ESS_v04_M | weights_and_design | 1 | sect_cover_hh_w4.dta | 1 | blocked_no_original_package |
| 2 | ETH_2018_ESS_v04_M | weights_and_design | 2 | sect_cover_ph_w4.dta | 1 | blocked_no_original_package |
| 2 | ETH_2018_ESS_v04_M | weights_and_design | 3 | sect_cover_pp_w4.dta | 1 | blocked_no_original_package |
| 2 | ETH_2018_ESS_v04_M | weights_and_design | 4 | sect6b2_hh_w4.dta | 1 | blocked_no_original_package |
| 2 | ETH_2018_ESS_v04_M | weights_and_design | 5 | sect7a_hh_w4.dta | 1 | blocked_no_original_package |
| 2 | ETH_2018_ESS_v04_M | weights_and_design | 6 | sect9_hh_w4.dta | 1 | blocked_no_original_package |
| 2 | ETH_2018_ESS_v04_M | weights_and_design | 7 | sect1_hh_w4.dta | 1 | blocked_no_original_package |
| 2 | ETH_2018_ESS_v04_M | weights_and_design | 8 | sect10d1_hh_w4.dta | 1 | blocked_no_original_package |
| 3 | MWI_2004_IHS-II_v01_M | climate_geography | 1 | sec_a.NSDstat | 1 | ready_for_raw_value_review |
| 3 | MWI_2004_IHS-II_v01_M | climate_geography | 2 | sec_f.NSDstat | 1 | ready_for_raw_value_review |
| 3 | MWI_2004_IHS-II_v01_M | climate_geography | 3 | sec_g.NSDstat | 1 | ready_for_raw_value_review |
| 3 | MWI_2004_IHS-II_v01_M | climate_geography | 4 | sec_h.NSDstat | 1 | ready_for_raw_value_review |
| 3 | MWI_2004_IHS-II_v01_M | climate_geography | 5 | sec_i.NSDstat | 1 | ready_for_raw_value_review |
| 3 | MWI_2004_IHS-II_v01_M | climate_geography | 6 | sec_j1.NSDstat | 1 | ready_for_raw_value_review |
| 3 | MWI_2004_IHS-II_v01_M | climate_geography | 7 | sec_j2.NSDstat | 1 | ready_for_raw_value_review |
| 3 | MWI_2004_IHS-II_v01_M | climate_geography | 8 | sec_k.NSDstat | 1 | ready_for_raw_value_review |
| 3 | MWI_2004_IHS-II_v01_M | consumption_or_income | 1 | sec_j1.NSDstat | 10 | ready_for_raw_value_review |

## Full Official File Manifest Preview

| download_priority_order | idno | file_id | file_name | file_description | priority_core_target |
|---|---|---|---|---|---|
| 1 | ETH_2021_ESPS-W5_v02_M | F1 | sect_cover_hh_w5.dta | Household Data - Cover page | 1 |
| 1 | ETH_2021_ESPS-W5_v02_M | F2 | sect1_hh_w5.dta | Household Data - Roster | 1 |
| 1 | ETH_2021_ESPS-W5_v02_M | F3 | sect2_hh_w5.dta | Household Data - Education | 0 |
| 1 | ETH_2021_ESPS-W5_v02_M | F4 | sect3_hh_w5.dta | Household Data - Health | 1 |
| 1 | ETH_2021_ESPS-W5_v02_M | F5 | sect3b_hh_w5.dta | Household Data - COVID-19 | 0 |
| 1 | ETH_2021_ESPS-W5_v02_M | F6 | sect4_hh_w5.dta | Household Data - Labor and time use | 0 |
| 1 | ETH_2021_ESPS-W5_v02_M | F7 | sect5a_hh_w5.dta | Banking and financial inclusion | 0 |
| 1 | ETH_2021_ESPS-W5_v02_M | F8 | sect5b_hh_w5.dta | Digital financial services | 0 |
| 1 | ETH_2021_ESPS-W5_v02_M | F9 | sect6a_hh_w5.dta | Household Data - Food consumption last 7 days | 0 |
| 1 | ETH_2021_ESPS-W5_v02_M | F10 | sect6b2_hh_w5.dta | Household Data - Food shared by non-household members (Filter Question) | 1 |
| 1 | ETH_2021_ESPS-W5_v02_M | F11 | sect6b3_hh_w5.dta | Household Data - Food shared by non-household members | 1 |
| 1 | ETH_2021_ESPS-W5_v02_M | F12 | sect6b4_hh_w5.dta | Household Data - Food consumed outside home | 1 |
| 1 | ETH_2021_ESPS-W5_v02_M | F13 | sect6c_hh_w5.dta | Household Data - Dietary quality | 1 |
| 1 | ETH_2021_ESPS-W5_v02_M | F14 | sect7a_hh_w5.dta | Household Data - Nonfood expenditure, one month | 1 |
| 1 | ETH_2021_ESPS-W5_v02_M | F15 | sect7b_hh_w5.dta | Household Data - Nonfood expenditure, 12 months | 1 |
| 1 | ETH_2021_ESPS-W5_v02_M | F16 | sect8_hh_w5.dta | Household Data - Food insecurity experience scale | 1 |
| 1 | ETH_2021_ESPS-W5_v02_M | F17 | sect9_hh_w5.dta | Household Data - Shocks | 0 |
| 1 | ETH_2021_ESPS-W5_v02_M | F18 | sect10a_hh_w5.dta | Household Data - Housing | 0 |
| 1 | ETH_2021_ESPS-W5_v02_M | F19 | sect11_hh_w5.dta | Household Data - Assets | 0 |
| 1 | ETH_2021_ESPS-W5_v02_M | F20 | sect12a_hh_w5.dta | Household Data - Nonfarm enterprises participation filter question | 0 |
| 1 | ETH_2021_ESPS-W5_v02_M | F21 | sect12b1_hh_w5.dta | Household Data - Nonfarm enterprises roster | 1 |
| 1 | ETH_2021_ESPS-W5_v02_M | F22 | sect12b2_hh_w5.dta | Household Data - Nonfarm enterprises start-up barriers | 0 |
| 1 | ETH_2021_ESPS-W5_v02_M | F23 | sect12c_hh_w5.dta | Household Data - Agriculture for All Urban EAs and rural EAs that are not part of the agriculture survey | 0 |
| 1 | ETH_2021_ESPS-W5_v02_M | F24 | sect12c_q1_hh_w5.dta | Household Data - Agriculture for All Urban EAs and rural EAs that are not part of agriculture survey: filter question | 0 |
| 1 | ETH_2021_ESPS-W5_v02_M | F25 | sect12d_hh_w5.dta | Household Data - Livestock for All Urban EAs and rural EAs that are not part of the agriculture survey | 0 |
| 1 | ETH_2021_ESPS-W5_v02_M | F26 | sect12e_hh_w5.dta | Household Data - Perception of climate risk | 0 |
| 1 | ETH_2021_ESPS-W5_v02_M | F27 | sect12f_hh_w5.dta | Household Data - Perception of climate risk: source of information | 0 |
| 1 | ETH_2021_ESPS-W5_v02_M | F28 | sect13_hh_w5.dta | Household Data - Other income | 0 |
| 1 | ETH_2021_ESPS-W5_v02_M | F29 | sect14_hh_w5.dta | Household Data - Assistance | 0 |
| 1 | ETH_2021_ESPS-W5_v02_M | F30 | sect15a_hh_w5.dta | Credit access filter and constraints | 0 |
| 1 | ETH_2021_ESPS-W5_v02_M | F31 | sect15b_hh_w5.dta | Credit details data | 0 |
| 1 | ETH_2021_ESPS-W5_v02_M | F32 | sect01a_com_w5.dta | Community - Cover/ identification | 0 |
| 1 | ETH_2021_ESPS-W5_v02_M | F33 | sect01b_com_w5.dta | Community - Cover/ community overview/ observation | 0 |
| 1 | ETH_2021_ESPS-W5_v02_M | F34 | sect02_com_w5.dta | Community - Roster of informants | 0 |
| 1 | ETH_2021_ESPS-W5_v02_M | F35 | sect03_com_w5.dta | Community - Community basic information/ demographics | 0 |
| 1 | ETH_2021_ESPS-W5_v02_M | F36 | sect04_com_w5.dta | Community - Access to basic services and infrastructure | 1 |
| 1 | ETH_2021_ESPS-W5_v02_M | F37 | sect05_com_w5.dta | Community - Economic activities and employment | 0 |
| 1 | ETH_2021_ESPS-W5_v02_M | F38 | sect06_com_w5.dta | Community - Agriculture | 0 |
| 1 | ETH_2021_ESPS-W5_v02_M | F39 | sect07_com_w5.dta | Community - Changes and events | 0 |
| 1 | ETH_2021_ESPS-W5_v02_M | F40 | sect08_com_w5.dta | Community - Community needs | 0 |
| 1 | ETH_2021_ESPS-W5_v02_M | F41 | sect09_com_w5.dta | Community - Productive safety net program | 0 |
| 1 | ETH_2021_ESPS-W5_v02_M | F42 | sect10a_com_w5.dta | Community - Market prices: market location | 1 |
| 1 | ETH_2021_ESPS-W5_v02_M | F43 | sect10b_com_w5.dta | Community - Prices in market | 0 |
| 1 | ETH_2021_ESPS-W5_v02_M | F44 | sect11_com_w5.dta | Community - Agriculture mechanization | 0 |
| 1 | ETH_2021_ESPS-W5_v02_M | F45 | sect12_com_w5.dta | Community - Virtual/video extension services | 0 |
| 1 | ETH_2021_ESPS-W5_v02_M | F46 | sect_cover_pp_w5.dta | Post-planting - Cover page | 1 |
| 1 | ETH_2021_ESPS-W5_v02_M | F47 | sect1_pp_w5.dta | Post-planting - Household roster | 1 |
| 1 | ETH_2021_ESPS-W5_v02_M | F48 | sect2_pp_w5.dta | Post-planting - Parcel roster | 1 |
| 1 | ETH_2021_ESPS-W5_v02_M | F49 | sect3_pp_w5.dta | Post-planting - Field roster | 1 |
| 1 | ETH_2021_ESPS-W5_v02_M | F50 | sect4_pp_w5.dta | Post-planting - Crop field roster | 1 |
| 1 | ETH_2021_ESPS-W5_v02_M | F51 | sect5_pp_w5.dta | Post-planting - Seed acquisition | 0 |
| 1 | ETH_2021_ESPS-W5_v02_M | F52 | sect7_pp_w5.dta | Post-planting - Holder questions | 0 |
| 1 | ETH_2021_ESPS-W5_v02_M | F53 | sect9a_pp_w5.dta | Post-planting - Crop cut by field (for specified fields and crops only) | 0 |
| 1 | ETH_2021_ESPS-W5_v02_M | F54 | sect_cover_ph_w5.dta | Post-harvest - Cover page | 1 |
| 1 | ETH_2021_ESPS-W5_v02_M | F55 | sect1_ph_w5.dta | Post-harvest - Household roster | 1 |
| 1 | ETH_2021_ESPS-W5_v02_M | F56 | sect9_ph_w5.dta | Post-harvest - Harvest by field | 0 |
| 1 | ETH_2021_ESPS-W5_v02_M | F57 | sect10_ph_w5.dta | Post-harvest - Harvest labor | 0 |
| 1 | ETH_2021_ESPS-W5_v02_M | F58 | sect11_ph_w5.dta | Post-harvest - Crop utilization | 0 |
| 1 | ETH_2021_ESPS-W5_v02_M | F59 | sect_cover_ls_w5.dta | Livestock - Cover page | 1 |
| 1 | ETH_2021_ESPS-W5_v02_M | F60 | sect8_1_ls_w5.dta | Livestock - Livestock inventory and ownership | 0 |
| 1 | ETH_2021_ESPS-W5_v02_M | F61 | sect8_2_ls_w5.dta | Livestock - Livestock change | 0 |
| 1 | ETH_2021_ESPS-W5_v02_M | F62 | sect8_3_ls_w5.dta | Livestock - Livestock breeding, health, shelter, water, and feed | 1 |
| 1 | ETH_2021_ESPS-W5_v02_M | F63 | sect8_4_ls_w5.dta | Livestock - Milk and egg production, animal power, and dung | 0 |
| 1 | ETH_2021_ESPS-W5_v02_M | F64 | eth_householdgeovariables_y5.dta | Household geo-variables | 1 |
| 1 | ETH_2021_ESPS-W5_v02_M | F65 | eth_plotgeovariables_y5.dta | Plot geo-variables | 1 |
| 1 | ETH_2021_ESPS-W5_v02_M | F66 | cons_agg_w5.dta | Household Data - Consumption aggregate | 1 |
| 1 | ETH_2021_ESPS-W5_v02_M | F67 | crop_cf_wave5.dta | Crop unit of measurement conversion factor data | 0 |
| 1 | ETH_2021_ESPS-W5_v02_M | F68 | food_cf_wave5.dta | Food item unit of measurement conversion factor data | 0 |
| 2 | ETH_2018_ESS_v04_M | F1 | sect_cover_hh_w4.dta | Household identification; location; household size, and field staff identification | 1 |
| 2 | ETH_2018_ESS_v04_M | F2 | sect1_hh_w4.dta | Roster - List of individuals living in the household and basic demographics; for members younger than 18, parental ed... | 1 |
| 2 | ETH_2018_ESS_v04_M | F3 | sect2_hh_w4.dta | Education - Educational attainment, enrollment, attendance, school characteristics, and expenditures for the 2018‒19 ... | 0 |
| 2 | ETH_2018_ESS_v04_M | F4 | sect3_hh_w4.dta | Health - Health problems, types of injury/illness, medical assistance/consultation, health insurance, disabilities, v... | 1 |
| 2 | ETH_2018_ESS_v04_M | F5 | sect4_hh_w4.dta | Labor and time use - Time use, labor market participation in the last 7 days and the last 12 months, unpaid apprentic... | 0 |
| 2 | ETH_2018_ESS_v04_M | F6 | sect5a_hh_w4.dta | Banking and financial inclusion - Saving, financial literacy, insurance, and financial practices. | 0 |
| 2 | ETH_2018_ESS_v04_M | F7 | sect5b1_hh_w4.dta | Financial assets - Individual disaggregated financial asset module: Ownership of financial asset accounts (exclusivel... | 0 |
| 2 | ETH_2018_ESS_v04_M | F8 | sect5b2_hh_w4.dta | Financial assets - Individual disaggregated financial asset module: Value of financial assets owned privately or join... | 0 |
| 2 | ETH_2018_ESS_v04_M | F9 | sect6a_hh_w4.dta | Food consumption, last 7 days - Household food consumption (quantity and value) in the last 7 days and source of food... | 0 |
| 2 | ETH_2018_ESS_v04_M | F10 | sect6b1_hh_w4.dta | Food aggregate, last 7 days - Summary on consumption of food in the last 7 days. Dietary diversification. | 0 |
| 2 | ETH_2018_ESS_v04_M | F11 | sect6b2_hh_w4.dta | Meals shared with non-household members, last 7 days - Meal sharing with non-household members (number of persons and... | 1 |
| 2 | ETH_2018_ESS_v04_M | F12 | sect6b3_hh_w4.dta | Food consumed away from home, last 7 days - Total number of days and total number of meals shared with people (groupe... | 0 |

## Machine-Readable Outputs

- `temp/priority_lsms_isa_credentialed_raw_acquisition_workbench.csv`
- `temp/priority_lsms_isa_credentialed_raw_full_file_manifest.csv`
- `temp/priority_lsms_isa_credentialed_raw_core_file_checklist.csv`
- `result/priority_lsms_isa_credentialed_raw_acquisition_workbench_summary.csv`

## Guardrails

- Complete official package receipt is required before raw-value verification.
- Generated markdown handoffs and public DDI metadata do not count as raw packages.
- No row may be promoted into `data/` until registry and climate-linkage gates pass.
