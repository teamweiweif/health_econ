# Priority LSMS/ISA Web GPT Download Control Manifest

Status: direct-read acquisition control manifest for the 10 download-required
LSMS/ISA waves in the locked dataset-promotion scope.

This report consolidates the official get-microdata URLs, credentialed
`/download` URLs, local target folders, command packets, incoming-file status,
and expected core-file checks into files under `result/` so a Web GPT reviewer
does not need to infer the download plan from scattered `temp/` artifacts.

It does not download raw files, export credentials, write `data/`, or promote
country-waves. The current stop rule remains: browser/manual World Bank terms
acceptance or session material is required before package receipt validation can
start.

## Summary

| metric | value | interpretation |
| --- | --- | --- |
| webgpt_download_control_rows | 10 | Download-required waves in the Web GPT control manifest. |
| webgpt_download_control_country_rows | 5 | Countries covered by the download-required control manifest. |
| webgpt_download_control_priority_country_rows | 9 | Rows from Ethiopia, Nigeria, Malawi, Tanzania, or Uganda. |
| webgpt_download_control_sixth_country_rows | 1 | Rows supplying the sixth country in the locked scope. |
| webgpt_download_control_expected_full_file_rows | 838 | Expected official file rows across the 10 download-required waves. |
| webgpt_download_control_expected_core_file_rows | 323 | Expected core-file requirement rows exported for direct review. |
| webgpt_download_control_target_file_rows | 0 | Current files in exact target folders. |
| webgpt_download_control_incoming_file_rows | 0 | Current files staged under temp/raw_downloads/_incoming. |
| webgpt_download_control_browser_manual_rows | 10 | Rows still requiring browser/manual terms acceptance or session material. |
| webgpt_download_control_data_write_status | blocked_no_data_write | The download control manifest does not write promoted data. |
| modeling_gate_status | blocked | No predictive, reduced-form, causal ML, or policy learning is opened. |
| webgpt_download_control_status_browser_manual_terms_acceptance_required | 10 | Web GPT download control status count. |

## Download Control

| download_rank | country | wave | idno | catalog_id | webgpt_download_status | expected_core_file_rows | target_file_count | incoming_file_rows |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Ethiopia | 2021-2022 | ETH_2021_ESPS-W5_v02_M | 6161 | browser_manual_terms_acceptance_required | 36 | 0 | 0 |
| 2 | Ethiopia | 2018-2019 | ETH_2018_ESS_v04_M | 3823 | browser_manual_terms_acceptance_required | 35 | 0 | 0 |
| 3 | Nigeria | 2012-2013 | NGA_2012_GHSP-W2_v02_M | 1952 | browser_manual_terms_acceptance_required | 26 | 0 | 0 |
| 4 | Nigeria | 2015-2016 | NGA_2015_GHSP-W3_v02_M | 2734 | browser_manual_terms_acceptance_required | 26 | 0 | 0 |
| 5 | Nigeria | 2010-2011 | NGA_2010_GHSP-W1_v03_M | 1002 | browser_manual_terms_acceptance_required | 27 | 0 | 0 |
| 6 | Tanzania | 2008-2009 | TZA_2008_NPS-R1_v03_M | 76 | browser_manual_terms_acceptance_required | 35 | 0 | 0 |
| 7 | Tanzania | 2010-2011 | TZA_2010_NPS-R2_v03_M | 1050 | browser_manual_terms_acceptance_required | 38 | 0 | 0 |
| 8 | Tanzania | 2012-2013 | TZA_2012_NPS-R3_v01_M | 2252 | browser_manual_terms_acceptance_required | 33 | 0 | 0 |
| 9 | Uganda | 2019-2020 | UGA_2019_UNPS_v03_M | 3902 | browser_manual_terms_acceptance_required | 39 | 0 | 0 |
| 10 | Nepal | 2010-2011 | NPL_2010_LSS-III_v01_M | 1000 | browser_manual_terms_acceptance_required | 28 | 0 | 0 |

## Core File Preview

| download_rank | idno | requirement | expected_file_name | file_description | top_variable_names |
| --- | --- | --- | --- | --- | --- |
| 1 | ETH_2021_ESPS-W5_v02_M | climate_geography | sect_cover_hh_w5.dta | Household Data - Cover page | saq19__Latitude;saq19__Longitude |
| 1 | ETH_2021_ESPS-W5_v02_M | consumption_or_income | cons_agg_w5.dta | Household Data - Consumption aggregate | nonfood_cons2;nom_nonfoodcons_aeq;nonfood_cons_ann;food_cons2;food_cons_ann;nom_foodcons_aeq;fafh_cons_ann;... |
| 1 | ETH_2021_ESPS-W5_v02_M | health_need_and_access | sect3_hh_w5.dta | Household Data - Health | s3q14;s3q15;s3q05;s3q17;s3q13;s3q18 |
| 1 | ETH_2021_ESPS-W5_v02_M | household_person_keys | sect1_hh_w5.dta | Household Data - Roster | individual_id;household_id |
| 1 | ETH_2021_ESPS-W5_v02_M | oop_health_expenditure | sect8_3_ls_w5.dta | Livestock - Livestock breeding, health, shelter, water, and feed | ls_s8_3q04;ls_s8_3q22;ls_s8_3q24;ls_s8_3q03;ls_s8_3q05;ls_s8_3q06;ls_s8_3q10a;ls_s8_3q10b;ls_s8_3q11;ls_s8_... |
| 1 | ETH_2021_ESPS-W5_v02_M | survey_timing | sect_cover_pp_w5.dta | Post-planting - Cover page | InterviewDate |
| 1 | ETH_2021_ESPS-W5_v02_M | weights_and_design | sect_cover_hh_w5.dta | Household Data - Cover page | pw_w5;ea_id |
| 1 | ETH_2021_ESPS-W5_v02_M | climate_geography | sect10a_com_w5.dta | Community - Market prices: market location | cs10q05__Latitude;cs10q05__Longitude |
| 1 | ETH_2021_ESPS-W5_v02_M | health_need_and_access | sect04_com_w5.dta | Community - Access to basic services and infrastructure | cs4q37;cs4q34;cs4q35;cs4q28 |
| 1 | ETH_2021_ESPS-W5_v02_M | household_person_keys | sect12b1_hh_w5.dta | Household Data - Nonfarm enterprises roster | household_id |
| 1 | ETH_2021_ESPS-W5_v02_M | oop_health_expenditure | sect3_hh_w5.dta | Household Data - Health | s3q17;s3q18 |
| 1 | ETH_2021_ESPS-W5_v02_M | survey_timing | sect_cover_ph_w5.dta | Post-harvest - Cover page | InterviewDate |
| 1 | ETH_2021_ESPS-W5_v02_M | weights_and_design | sect6b2_hh_w5.dta | Household Data - Food shared by non-household members (Filter Question) | pw_w5 |
| 1 | ETH_2021_ESPS-W5_v02_M | climate_geography | sect_cover_pp_w5.dta | Post-planting - Cover page | saq19__Latitude;saq19__Longitude |
| 1 | ETH_2021_ESPS-W5_v02_M | health_need_and_access | sect3_pp_w5.dta | Post-planting - Field roster | s3q15_1;s3q15_2 |
| 1 | ETH_2021_ESPS-W5_v02_M | household_person_keys | sect1_pp_w5.dta | Post-planting - Household roster | household_id |
| 1 | ETH_2021_ESPS-W5_v02_M | survey_timing | sect_cover_ls_w5.dta | Livestock - Cover page | InterviewDate |
| 1 | ETH_2021_ESPS-W5_v02_M | weights_and_design | sect6b3_hh_w5.dta | Household Data - Food shared by non-household members | pw_w5 |
| 1 | ETH_2021_ESPS-W5_v02_M | climate_geography | sect_cover_ph_w5.dta | Post-harvest - Cover page | saq19__Latitude;saq19__Longitude |
| 1 | ETH_2021_ESPS-W5_v02_M | household_person_keys | sect1_ph_w5.dta | Post-harvest - Household roster | household_id |
| 1 | ETH_2021_ESPS-W5_v02_M | survey_timing | sect12b1_hh_w5.dta | Household Data - Nonfarm enterprises roster | s12bq08a;s12bq08b |
| 1 | ETH_2021_ESPS-W5_v02_M | weights_and_design | sect6b4_hh_w5.dta | Household Data - Food consumed outside home | pw_w5 |
| 1 | ETH_2021_ESPS-W5_v02_M | climate_geography | sect_cover_ls_w5.dta | Livestock - Cover page | saq19__Latitude;saq19__Longitude |
| 1 | ETH_2021_ESPS-W5_v02_M | household_person_keys | sect2_pp_w5.dta | Post-planting - Parcel roster | household_id |
| 1 | ETH_2021_ESPS-W5_v02_M | survey_timing | sect7b_hh_w5.dta | Household Data - Nonfood expenditure, 12 months | item_cd_12months;s7q04 |
| 1 | ETH_2021_ESPS-W5_v02_M | weights_and_design | sect6c_hh_w5.dta | Household Data - Dietary quality | pw_w5 |
| 1 | ETH_2021_ESPS-W5_v02_M | climate_geography | sect3_pp_w5.dta | Post-planting - Field roster | s3q09__Latitude;s3q09__Longitude |
| 1 | ETH_2021_ESPS-W5_v02_M | household_person_keys | sect3_pp_w5.dta | Post-planting - Field roster | household_id |
| 1 | ETH_2021_ESPS-W5_v02_M | survey_timing | eth_householdgeovariables_y5.dta | Household geo-variables | wetQ_avgstart |
| 1 | ETH_2021_ESPS-W5_v02_M | weights_and_design | sect7a_hh_w5.dta | Household Data - Nonfood expenditure, one month | pw_w5 |
| 1 | ETH_2021_ESPS-W5_v02_M | household_person_keys | sect4_pp_w5.dta | Post-planting - Crop field roster | household_id |
| 1 | ETH_2021_ESPS-W5_v02_M | survey_timing | sect_cover_hh_w5.dta | Household Data - Cover page | saq19__Timestamp |
| 1 | ETH_2021_ESPS-W5_v02_M | weights_and_design | sect7b_hh_w5.dta | Household Data - Nonfood expenditure, 12 months | pw_w5 |
| 1 | ETH_2021_ESPS-W5_v02_M | household_person_keys | sect6c_hh_w5.dta | Household Data - Dietary quality | individual_id |
| 1 | ETH_2021_ESPS-W5_v02_M | survey_timing | eth_plotgeovariables_y5.dta | Plot geo-variables | wetQ_avgstart |
| 1 | ETH_2021_ESPS-W5_v02_M | weights_and_design | sect8_hh_w5.dta | Household Data - Food insecurity experience scale | pw_w5 |
| 2 | ETH_2018_ESS_v04_M | climate_geography | sect_cover_ph_w4.dta | Holder location identification; household size, agriculture holding type: farming, livestock, or both, fiel... | saq19__Latitude;saq19__Longitude;ea_id |
| 2 | ETH_2018_ESS_v04_M | consumption_or_income | sect7a_hh_w4.dta | Nonfood expenditure - Household monthly expenditures on nonfood items. | ea_id;household_id;item_cd_30day;pw_w4;s7q01;s7q02;saq01;saq02;saq03 |
| 2 | ETH_2018_ESS_v04_M | health_need_and_access | sect3_hh_w4.dta | Health - Health problems, types of injury/illness, medical assistance/consultation, health insurance, disab... | s3q14;s3q15;s3q05;s3q17;s3q13;s3q18;s3q06_1;s3q06_2;s3q06_os;s3q09a;s3q09b |
| 2 | ETH_2018_ESS_v04_M | household_person_keys | sect1_hh_w4.dta | Roster - List of individuals living in the household and basic demographics; for members younger than 18, p... | individual_id;household_id |
| ... | ... | ... | ... | ... | ... |

## Use Rule

Use `result/priority_lsms_isa_webgpt_download_control_manifest.csv` as the
one-table acquisition control board, and
`result/priority_lsms_isa_webgpt_expected_core_file_manifest.csv` as the
post-download core-file checklist. A country-wave can only move toward
promotion after complete official package receipt and all value, timing,
geography, climate-linkage, and promotion-packet gates pass.
