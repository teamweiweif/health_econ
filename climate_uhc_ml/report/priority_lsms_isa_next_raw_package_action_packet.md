# Priority LSMS/ISA Next Raw Package Action Packet

Status: exact acquisition queue for moving beyond the first promoted Malawi
2004 household-climate dataset.

The current registry has one promoted country-wave. The remaining minimum
batch needs complete official raw packages before raw-value, outcome, timing,
geography, and climate-linkage verification can start.

This packet does not bypass World Bank account, registration, terms, or
request gates. It translates the existing minimum viable acquisition plan into
the next file-level acquisition actions.

## Summary

| metric | value | interpretation |
| --- | --- | --- |
| next_raw_package_action_rows | 18 | Country-waves requiring raw package acquisition or backup acquisition action. |
| minimum_batch_remaining_action_rows | 10 | Unpromoted minimum-batch waves still needing complete official raw packages. |
| backup_after_minimum_action_rows | 8 | Backup waves queued after the minimum batch. |
| core_file_action_rows | 592 | Requirement-file rows to verify after raw packages are placed. |
| unique_core_files_remaining_minimum_batch | 213 | Sum of per-wave unique core files in the remaining minimum batch. |
| current_promoted_analysis_ready_rows | 1 | Current promoted registry rows before additional raw acquisition. |
| current_promoted_country_rows | 1 | Current promoted countries before additional raw acquisition. |
| countries_if_minimum_batch_passes | 6 | Countries covered if current promoted rows plus remaining minimum batch all pass verification. |
| country_waves_if_minimum_batch_passes | 11 | Country-waves covered if current promoted rows plus remaining minimum batch all pass verification. |
| official_raw_download_candidate_rows | 0 | Current endpoint-refresh raw download candidates; zero means login/terms workflow remains required. |
| credentialed_download_required_rows | 11 | Minimum-batch waves whose current get-microdata page requires credentialed access. |
| data_write_gate_status | blocked_raw_package_acquisition_required | This packet only controls raw acquisition; it does not permit promoted data writes. |
| modeling_gate_status | blocked | No predictive, reduced-form, causal ML, or policy learning until registry thresholds pass. |
| wave_handoff_readmes_written | 18 | Per-wave next raw package handoff files written under target folders. |

## Action Queue

| action_rank | acquisition_tier | country | wave | idno | full_official_file_rows | unique_core_files_required | missing_core_file_rows |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | minimum_batch_remaining | Ethiopia | 2021-2022 | ETH_2021_ESPS-W5_v02_M | 68 | 25 | 36 |
| 2 | minimum_batch_remaining | Ethiopia | 2018-2019 | ETH_2018_ESS_v04_M | 68 | 23 | 35 |
| 3 | minimum_batch_remaining | Nigeria | 2012-2013 | NGA_2012_GHSP-W2_v02_M | 103 | 16 | 26 |
| 4 | minimum_batch_remaining | Nigeria | 2015-2016 | NGA_2015_GHSP-W3_v02_M | 104 | 18 | 26 |
| 5 | minimum_batch_remaining | Nigeria | 2010-2011 | NGA_2010_GHSP-W1_v03_M | 99 | 16 | 27 |
| 6 | minimum_batch_remaining | Tanzania | 2008-2009 | TZA_2008_NPS-R1_v03_M | 61 | 22 | 35 |
| 7 | minimum_batch_remaining | Tanzania | 2010-2011 | TZA_2010_NPS-R2_v03_M | 95 | 23 | 38 |
| 8 | minimum_batch_remaining | Tanzania | 2012-2013 | TZA_2012_NPS-R3_v01_M | 80 | 23 | 33 |
| 9 | minimum_batch_remaining | Uganda | 2019-2020 | UGA_2019_UNPS_v03_M | 109 | 27 | 39 |
| 10 | minimum_batch_remaining | Nepal | 2010-2011 | NPL_2010_LSS-III_v01_M | 51 | 20 | 28 |
| 11 | backup_after_minimum_batch | Jamaica | 1997 | JAM_1997_SLC_v01_M | 68 | 21 | 32 |
| 12 | backup_after_minimum_batch | Kyrgyz Republic | 1993 | KGZ_1993_KMPS_v01_M | 15 | 13 | 31 |
| 13 | backup_after_minimum_batch | Malawi | 2019-2020 | MWI_2019_IHS-V_v06_M | 108 | 23 | 35 |
| 14 | backup_after_minimum_batch | Malawi | 2016-2017 | MWI_2016_IHS-IV_v04_M | 99 | 23 | 35 |
| 15 | backup_after_minimum_batch | Malawi | 2010-2011 | MWI_2010_IHS-III_v01_M | 85 | 18 | 36 |
| 16 | backup_after_minimum_batch | Uganda | 2011-2012 | UGA_2011_UNPS_v02_M | 103 | 26 | 32 |
| 17 | backup_after_minimum_batch | Uganda | 2018-2019 | UGA_2018_UNPS_v02_M | 109 | 26 | 34 |
| 18 | backup_after_minimum_batch | Uganda | 2015-2016 | UGA_2015_UNPS_v02_M | 120 | 23 | 34 |

## Core File Preview

| action_rank | idno | requirement | file_rank | file_name | current_receipt_status |
| --- | --- | --- | --- | --- | --- |
| 1 | ETH_2021_ESPS-W5_v02_M | climate_geography | 1 | sect_cover_hh_w5.dta | blocked_no_original_package |
| 1 | ETH_2021_ESPS-W5_v02_M | climate_geography | 2 | sect10a_com_w5.dta | blocked_no_original_package |
| 1 | ETH_2021_ESPS-W5_v02_M | climate_geography | 3 | sect_cover_pp_w5.dta | blocked_no_original_package |
| 1 | ETH_2021_ESPS-W5_v02_M | climate_geography | 4 | sect_cover_ph_w5.dta | blocked_no_original_package |
| 1 | ETH_2021_ESPS-W5_v02_M | climate_geography | 5 | sect_cover_ls_w5.dta | blocked_no_original_package |
| 1 | ETH_2021_ESPS-W5_v02_M | climate_geography | 6 | sect3_pp_w5.dta | blocked_no_original_package |
| 1 | ETH_2021_ESPS-W5_v02_M | consumption_or_income | 1 | cons_agg_w5.dta | blocked_no_original_package |
| 1 | ETH_2021_ESPS-W5_v02_M | health_need_and_access | 1 | sect3_hh_w5.dta | blocked_no_original_package |
| 1 | ETH_2021_ESPS-W5_v02_M | health_need_and_access | 2 | sect04_com_w5.dta | blocked_no_original_package |
| 1 | ETH_2021_ESPS-W5_v02_M | health_need_and_access | 3 | sect3_pp_w5.dta | blocked_no_original_package |
| 1 | ETH_2021_ESPS-W5_v02_M | household_person_keys | 1 | sect1_hh_w5.dta | blocked_no_original_package |
| 1 | ETH_2021_ESPS-W5_v02_M | household_person_keys | 2 | sect12b1_hh_w5.dta | blocked_no_original_package |
| 1 | ETH_2021_ESPS-W5_v02_M | household_person_keys | 3 | sect1_pp_w5.dta | blocked_no_original_package |
| 1 | ETH_2021_ESPS-W5_v02_M | household_person_keys | 4 | sect1_ph_w5.dta | blocked_no_original_package |
| 1 | ETH_2021_ESPS-W5_v02_M | household_person_keys | 5 | sect2_pp_w5.dta | blocked_no_original_package |
| 1 | ETH_2021_ESPS-W5_v02_M | household_person_keys | 6 | sect3_pp_w5.dta | blocked_no_original_package |
| 1 | ETH_2021_ESPS-W5_v02_M | household_person_keys | 7 | sect4_pp_w5.dta | blocked_no_original_package |
| 1 | ETH_2021_ESPS-W5_v02_M | household_person_keys | 8 | sect6c_hh_w5.dta | blocked_no_original_package |
| 1 | ETH_2021_ESPS-W5_v02_M | oop_health_expenditure | 1 | sect8_3_ls_w5.dta | blocked_no_original_package |
| 1 | ETH_2021_ESPS-W5_v02_M | oop_health_expenditure | 2 | sect3_hh_w5.dta | blocked_no_original_package |
| 1 | ETH_2021_ESPS-W5_v02_M | survey_timing | 1 | sect_cover_pp_w5.dta | blocked_no_original_package |
| 1 | ETH_2021_ESPS-W5_v02_M | survey_timing | 2 | sect_cover_ph_w5.dta | blocked_no_original_package |
| 1 | ETH_2021_ESPS-W5_v02_M | survey_timing | 3 | sect_cover_ls_w5.dta | blocked_no_original_package |
| 1 | ETH_2021_ESPS-W5_v02_M | survey_timing | 4 | sect12b1_hh_w5.dta | blocked_no_original_package |
| 1 | ETH_2021_ESPS-W5_v02_M | survey_timing | 5 | sect7b_hh_w5.dta | blocked_no_original_package |
| 1 | ETH_2021_ESPS-W5_v02_M | survey_timing | 6 | eth_householdgeovariables_y5.dta | blocked_no_original_package |
| 1 | ETH_2021_ESPS-W5_v02_M | survey_timing | 7 | sect_cover_hh_w5.dta | blocked_no_original_package |
| 1 | ETH_2021_ESPS-W5_v02_M | survey_timing | 8 | eth_plotgeovariables_y5.dta | blocked_no_original_package |
| 1 | ETH_2021_ESPS-W5_v02_M | weights_and_design | 1 | sect_cover_hh_w5.dta | blocked_no_original_package |
| 1 | ETH_2021_ESPS-W5_v02_M | weights_and_design | 2 | sect6b2_hh_w5.dta | blocked_no_original_package |
| 1 | ETH_2021_ESPS-W5_v02_M | weights_and_design | 3 | sect6b3_hh_w5.dta | blocked_no_original_package |
| 1 | ETH_2021_ESPS-W5_v02_M | weights_and_design | 4 | sect6b4_hh_w5.dta | blocked_no_original_package |
| 1 | ETH_2021_ESPS-W5_v02_M | weights_and_design | 5 | sect6c_hh_w5.dta | blocked_no_original_package |
| 1 | ETH_2021_ESPS-W5_v02_M | weights_and_design | 6 | sect7a_hh_w5.dta | blocked_no_original_package |
| 1 | ETH_2021_ESPS-W5_v02_M | weights_and_design | 7 | sect7b_hh_w5.dta | blocked_no_original_package |
| 1 | ETH_2021_ESPS-W5_v02_M | weights_and_design | 8 | sect8_hh_w5.dta | blocked_no_original_package |
| 2 | ETH_2018_ESS_v04_M | climate_geography | 1 | sect_cover_ph_w4.dta | blocked_no_original_package |
| 2 | ETH_2018_ESS_v04_M | climate_geography | 2 | sect_cover_pp_w4.dta | blocked_no_original_package |
| 2 | ETH_2018_ESS_v04_M | climate_geography | 3 | sect_cover_ls_w4.dta | blocked_no_original_package |
| 2 | ETH_2018_ESS_v04_M | climate_geography | 4 | sect3_pp_w4.dta | blocked_no_original_package |
| 2 | ETH_2018_ESS_v04_M | climate_geography | 5 | sect10a_com_w4.dta | blocked_no_original_package |
| 2 | ETH_2018_ESS_v04_M | climate_geography | 6 | sect_cover_hh_w4.dta | blocked_no_original_package |
| 2 | ETH_2018_ESS_v04_M | consumption_or_income | 1 | sect7a_hh_w4.dta | blocked_no_original_package |
| 2 | ETH_2018_ESS_v04_M | consumption_or_income | 2 | cons_agg_w4.dta | blocked_no_original_package |
| 2 | ETH_2018_ESS_v04_M | health_need_and_access | 1 | sect3_hh_w4.dta | blocked_no_original_package |
| 2 | ETH_2018_ESS_v04_M | health_need_and_access | 2 | sect04_com_w4.dta | blocked_no_original_package |
| 2 | ETH_2018_ESS_v04_M | household_person_keys | 1 | sect1_hh_w4.dta | blocked_no_original_package |
| 2 | ETH_2018_ESS_v04_M | household_person_keys | 2 | sect11b1_hh_w4.dta | blocked_no_original_package |
| 2 | ETH_2018_ESS_v04_M | household_person_keys | 3 | sect10d1_hh_w4.dta | blocked_no_original_package |
| 2 | ETH_2018_ESS_v04_M | household_person_keys | 4 | sect1_ph_w4.dta | blocked_no_original_package |
| ... | ... | ... | ... | ... | ... |

## Rule

After files are placed, rerun the receipt, official-file validation, schema,
value-profile, and semantics-review commands listed in the action queue. Do
not write additional country-waves to `data/` until every required gate passes.
