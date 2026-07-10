# Priority LSMS-ISA Minimum-Batch Raw Value Queue

Status: executable raw-value review queue for the 10 remaining minimum-batch downloads.

This queue narrows the full 19-wave workbook to the 10 manual-download packets. It does not verify raw values, promote country-waves, write `data/`, or run models.

## Summary

- Datasets: 10
- Requirement rows: 80
- Variable rows: 811
- File rows: 323
- Blocked requirement rows: 80
- Ready requirement rows: 0
- Local target readmes: 10
- Data-write gate: blocked_no_data_write
- Modeling gate: blocked

## Requirement Queue Preview

| download_rank | idno | requirement_review_order | requirement | candidate_variable_rows | candidate_file_rows | minimum_batch_review_status |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | ETH_2021_ESPS-W5_v02_M | 1 | household_person_keys | 12 | 11 | blocked_until_official_raw_package_received |
| 1 | ETH_2021_ESPS-W5_v02_M | 2 | weights_and_design | 12 | 11 | blocked_until_official_raw_package_received |
| 1 | ETH_2021_ESPS-W5_v02_M | 3 | consumption_or_income | 12 | 1 | blocked_until_official_raw_package_received |
| 1 | ETH_2021_ESPS-W5_v02_M | 4 | oop_health_expenditure | 12 | 2 | blocked_until_official_raw_package_received |
| 1 | ETH_2021_ESPS-W5_v02_M | 5 | health_need_and_access | 12 | 3 | blocked_until_official_raw_package_received |
| 1 | ETH_2021_ESPS-W5_v02_M | 6 | survey_timing | 12 | 10 | blocked_until_official_raw_package_received |
| 1 | ETH_2021_ESPS-W5_v02_M | 7 | climate_geography | 12 | 6 | blocked_until_official_raw_package_received |
| 1 | ETH_2021_ESPS-W5_v02_M | 8 | missing_codes_units_recall_skip_patterns | 0 | 0 | blocked_until_official_raw_package_received |
| 2 | ETH_2018_ESS_v04_M | 1 | household_person_keys | 12 | 10 | blocked_until_official_raw_package_received |
| 2 | ETH_2018_ESS_v04_M | 2 | weights_and_design | 12 | 12 | blocked_until_official_raw_package_received |
| 2 | ETH_2018_ESS_v04_M | 3 | consumption_or_income | 12 | 2 | blocked_until_official_raw_package_received |
| 2 | ETH_2018_ESS_v04_M | 4 | oop_health_expenditure | 12 | 2 | blocked_until_official_raw_package_received |
| 2 | ETH_2018_ESS_v04_M | 5 | health_need_and_access | 12 | 2 | blocked_until_official_raw_package_received |
| 2 | ETH_2018_ESS_v04_M | 6 | survey_timing | 12 | 7 | blocked_until_official_raw_package_received |
| 2 | ETH_2018_ESS_v04_M | 7 | climate_geography | 12 | 6 | blocked_until_official_raw_package_received |
| 2 | ETH_2018_ESS_v04_M | 8 | missing_codes_units_recall_skip_patterns | 0 | 0 | blocked_until_official_raw_package_received |
| 3 | NGA_2012_GHSP-W2_v02_M | 1 | household_person_keys | 12 | 12 | blocked_until_official_raw_package_received |
| 3 | NGA_2012_GHSP-W2_v02_M | 2 | weights_and_design | 12 | 4 | blocked_until_official_raw_package_received |
| 3 | NGA_2012_GHSP-W2_v02_M | 3 | consumption_or_income | 12 | 4 | blocked_until_official_raw_package_received |
| 3 | NGA_2012_GHSP-W2_v02_M | 4 | oop_health_expenditure | 6 | 1 | blocked_until_official_raw_package_received |
| 3 | NGA_2012_GHSP-W2_v02_M | 5 | health_need_and_access | 12 | 3 | blocked_until_official_raw_package_received |
| 3 | NGA_2012_GHSP-W2_v02_M | 6 | survey_timing | 12 | 1 | blocked_until_official_raw_package_received |
| 3 | NGA_2012_GHSP-W2_v02_M | 7 | climate_geography | 12 | 5 | blocked_until_official_raw_package_received |
| 3 | NGA_2012_GHSP-W2_v02_M | 8 | missing_codes_units_recall_skip_patterns | 0 | 0 | blocked_until_official_raw_package_received |
| 4 | NGA_2015_GHSP-W3_v02_M | 1 | household_person_keys | 12 | 12 | blocked_until_official_raw_package_received |
| 4 | NGA_2015_GHSP-W3_v02_M | 2 | weights_and_design | 12 | 5 | blocked_until_official_raw_package_received |
| 4 | NGA_2015_GHSP-W3_v02_M | 3 | consumption_or_income | 12 | 3 | blocked_until_official_raw_package_received |
| 4 | NGA_2015_GHSP-W3_v02_M | 4 | oop_health_expenditure | 6 | 1 | blocked_until_official_raw_package_received |
| 4 | NGA_2015_GHSP-W3_v02_M | 5 | health_need_and_access | 12 | 2 | blocked_until_official_raw_package_received |
| 4 | NGA_2015_GHSP-W3_v02_M | 6 | survey_timing | 12 | 1 | blocked_until_official_raw_package_received |
| 4 | NGA_2015_GHSP-W3_v02_M | 7 | climate_geography | 12 | 6 | blocked_until_official_raw_package_received |
| 4 | NGA_2015_GHSP-W3_v02_M | 8 | missing_codes_units_recall_skip_patterns | 0 | 0 | blocked_until_official_raw_package_received |
| 5 | NGA_2010_GHSP-W1_v03_M | 1 | household_person_keys | 12 | 12 | blocked_until_official_raw_package_received |
| 5 | NGA_2010_GHSP-W1_v03_M | 2 | weights_and_design | 12 | 8 | blocked_until_official_raw_package_received |
| 5 | NGA_2010_GHSP-W1_v03_M | 3 | consumption_or_income | 12 | 2 | blocked_until_official_raw_package_received |
| ... | ... | ... | ... | ... | ... | ... |

## File Queue Preview

| download_rank | idno | requirement | file_rank | file_name | acceptance_gate_status | minimum_batch_review_status |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | ETH_2021_ESPS-W5_v02_M | household_person_keys | 1 | sect1_hh_w5.dta | missing_required_official_file | blocked_until_official_raw_package_received |
| 1 | ETH_2021_ESPS-W5_v02_M | household_person_keys | 2 | sect12b1_hh_w5.dta | missing_required_official_file | blocked_until_official_raw_package_received |
| 1 | ETH_2021_ESPS-W5_v02_M | household_person_keys | 3 | sect1_pp_w5.dta | missing_required_official_file | blocked_until_official_raw_package_received |
| 1 | ETH_2021_ESPS-W5_v02_M | household_person_keys | 4 | sect1_ph_w5.dta | missing_required_official_file | blocked_until_official_raw_package_received |
| 1 | ETH_2021_ESPS-W5_v02_M | household_person_keys | 5 | sect2_pp_w5.dta | missing_required_official_file | blocked_until_official_raw_package_received |
| 1 | ETH_2021_ESPS-W5_v02_M | household_person_keys | 6 | sect3_pp_w5.dta | missing_required_official_file | blocked_until_official_raw_package_received |
| 1 | ETH_2021_ESPS-W5_v02_M | household_person_keys | 7 | sect4_pp_w5.dta | missing_required_official_file | blocked_until_official_raw_package_received |
| 1 | ETH_2021_ESPS-W5_v02_M | household_person_keys | 8 | sect6c_hh_w5.dta | missing_required_official_file | blocked_until_official_raw_package_received |
| 1 | ETH_2021_ESPS-W5_v02_M | weights_and_design | 1 | sect_cover_hh_w5.dta | missing_required_official_file | blocked_until_official_raw_package_received |
| 1 | ETH_2021_ESPS-W5_v02_M | weights_and_design | 2 | sect6b2_hh_w5.dta | missing_required_official_file | blocked_until_official_raw_package_received |
| 1 | ETH_2021_ESPS-W5_v02_M | weights_and_design | 3 | sect6b3_hh_w5.dta | missing_required_official_file | blocked_until_official_raw_package_received |
| 1 | ETH_2021_ESPS-W5_v02_M | weights_and_design | 4 | sect6b4_hh_w5.dta | missing_required_official_file | blocked_until_official_raw_package_received |
| 1 | ETH_2021_ESPS-W5_v02_M | weights_and_design | 5 | sect6c_hh_w5.dta | missing_required_official_file | blocked_until_official_raw_package_received |
| 1 | ETH_2021_ESPS-W5_v02_M | weights_and_design | 6 | sect7a_hh_w5.dta | missing_required_official_file | blocked_until_official_raw_package_received |
| 1 | ETH_2021_ESPS-W5_v02_M | weights_and_design | 7 | sect7b_hh_w5.dta | missing_required_official_file | blocked_until_official_raw_package_received |
| 1 | ETH_2021_ESPS-W5_v02_M | weights_and_design | 8 | sect8_hh_w5.dta | missing_required_official_file | blocked_until_official_raw_package_received |
| 1 | ETH_2021_ESPS-W5_v02_M | consumption_or_income | 1 | cons_agg_w5.dta | missing_required_official_file | blocked_until_official_raw_package_received |
| 1 | ETH_2021_ESPS-W5_v02_M | oop_health_expenditure | 1 | sect8_3_ls_w5.dta | missing_required_official_file | blocked_until_official_raw_package_received |
| 1 | ETH_2021_ESPS-W5_v02_M | oop_health_expenditure | 2 | sect3_hh_w5.dta | missing_required_official_file | blocked_until_official_raw_package_received |
| 1 | ETH_2021_ESPS-W5_v02_M | health_need_and_access | 1 | sect3_hh_w5.dta | missing_required_official_file | blocked_until_official_raw_package_received |
| 1 | ETH_2021_ESPS-W5_v02_M | health_need_and_access | 2 | sect04_com_w5.dta | missing_required_official_file | blocked_until_official_raw_package_received |
| 1 | ETH_2021_ESPS-W5_v02_M | health_need_and_access | 3 | sect3_pp_w5.dta | missing_required_official_file | blocked_until_official_raw_package_received |
| 1 | ETH_2021_ESPS-W5_v02_M | survey_timing | 1 | sect_cover_pp_w5.dta | missing_required_official_file | blocked_until_official_raw_package_received |
| 1 | ETH_2021_ESPS-W5_v02_M | survey_timing | 2 | sect_cover_ph_w5.dta | missing_required_official_file | blocked_until_official_raw_package_received |
| 1 | ETH_2021_ESPS-W5_v02_M | survey_timing | 3 | sect_cover_ls_w5.dta | missing_required_official_file | blocked_until_official_raw_package_received |
| 1 | ETH_2021_ESPS-W5_v02_M | survey_timing | 4 | sect12b1_hh_w5.dta | missing_required_official_file | blocked_until_official_raw_package_received |
| 1 | ETH_2021_ESPS-W5_v02_M | survey_timing | 5 | sect7b_hh_w5.dta | missing_required_official_file | blocked_until_official_raw_package_received |
| 1 | ETH_2021_ESPS-W5_v02_M | survey_timing | 6 | eth_householdgeovariables_y5.dta | missing_required_official_file | blocked_until_official_raw_package_received |
| 1 | ETH_2021_ESPS-W5_v02_M | survey_timing | 7 | sect_cover_hh_w5.dta | missing_required_official_file | blocked_until_official_raw_package_received |
| 1 | ETH_2021_ESPS-W5_v02_M | survey_timing | 8 | eth_plotgeovariables_y5.dta | missing_required_official_file | blocked_until_official_raw_package_received |
| 1 | ETH_2021_ESPS-W5_v02_M | climate_geography | 1 | sect_cover_hh_w5.dta | missing_required_official_file | blocked_until_official_raw_package_received |
| 1 | ETH_2021_ESPS-W5_v02_M | climate_geography | 2 | sect10a_com_w5.dta | missing_required_official_file | blocked_until_official_raw_package_received |
| 1 | ETH_2021_ESPS-W5_v02_M | climate_geography | 3 | sect_cover_pp_w5.dta | missing_required_official_file | blocked_until_official_raw_package_received |
| 1 | ETH_2021_ESPS-W5_v02_M | climate_geography | 4 | sect_cover_ph_w5.dta | missing_required_official_file | blocked_until_official_raw_package_received |
| 1 | ETH_2021_ESPS-W5_v02_M | climate_geography | 5 | sect_cover_ls_w5.dta | missing_required_official_file | blocked_until_official_raw_package_received |
| ... | ... | ... | ... | ... | ... | ... |

## Variable Queue Preview

| download_rank | idno | requirement | candidate_rank | file_name | variable_name | minimum_batch_review_status |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | ETH_2021_ESPS-W5_v02_M | household_person_keys | 1 | sect1_hh_w5.dta | individual_id | blocked_until_official_raw_package_received |
| 1 | ETH_2021_ESPS-W5_v02_M | household_person_keys | 2 | sect1_hh_w5.dta | household_id | blocked_until_official_raw_package_received |
| 1 | ETH_2021_ESPS-W5_v02_M | household_person_keys | 3 | sect12b1_hh_w5.dta | household_id | blocked_until_official_raw_package_received |
| 1 | ETH_2021_ESPS-W5_v02_M | household_person_keys | 4 | sect1_pp_w5.dta | household_id | blocked_until_official_raw_package_received |
| 1 | ETH_2021_ESPS-W5_v02_M | household_person_keys | 5 | sect1_ph_w5.dta | household_id | blocked_until_official_raw_package_received |
| 1 | ETH_2021_ESPS-W5_v02_M | household_person_keys | 6 | sect2_pp_w5.dta | household_id | blocked_until_official_raw_package_received |
| 1 | ETH_2021_ESPS-W5_v02_M | household_person_keys | 7 | sect3_pp_w5.dta | household_id | blocked_until_official_raw_package_received |
| 1 | ETH_2021_ESPS-W5_v02_M | household_person_keys | 8 | sect4_pp_w5.dta | household_id | blocked_until_official_raw_package_received |
| 1 | ETH_2021_ESPS-W5_v02_M | household_person_keys | 9 | sect6c_hh_w5.dta | individual_id | blocked_until_official_raw_package_received |
| 1 | ETH_2021_ESPS-W5_v02_M | household_person_keys | 10 | sect2_hh_w5.dta | individual_id | blocked_until_official_raw_package_received |
| 1 | ETH_2021_ESPS-W5_v02_M | household_person_keys | 11 | sect3_hh_w5.dta | individual_id | blocked_until_official_raw_package_received |
| 1 | ETH_2021_ESPS-W5_v02_M | household_person_keys | 12 | sect3b_hh_w5.dta | individual_id | blocked_until_official_raw_package_received |
| 1 | ETH_2021_ESPS-W5_v02_M | weights_and_design | 1 | sect_cover_hh_w5.dta | pw_w5 | blocked_until_official_raw_package_received |
| 1 | ETH_2021_ESPS-W5_v02_M | weights_and_design | 2 | sect_cover_hh_w5.dta | ea_id | blocked_until_official_raw_package_received |
| 1 | ETH_2021_ESPS-W5_v02_M | weights_and_design | 3 | sect6b2_hh_w5.dta | pw_w5 | blocked_until_official_raw_package_received |
| 1 | ETH_2021_ESPS-W5_v02_M | weights_and_design | 4 | sect6b3_hh_w5.dta | pw_w5 | blocked_until_official_raw_package_received |
| 1 | ETH_2021_ESPS-W5_v02_M | weights_and_design | 5 | sect6b4_hh_w5.dta | pw_w5 | blocked_until_official_raw_package_received |
| 1 | ETH_2021_ESPS-W5_v02_M | weights_and_design | 6 | sect6c_hh_w5.dta | pw_w5 | blocked_until_official_raw_package_received |
| 1 | ETH_2021_ESPS-W5_v02_M | weights_and_design | 7 | sect7a_hh_w5.dta | pw_w5 | blocked_until_official_raw_package_received |
| 1 | ETH_2021_ESPS-W5_v02_M | weights_and_design | 8 | sect7b_hh_w5.dta | pw_w5 | blocked_until_official_raw_package_received |
| 1 | ETH_2021_ESPS-W5_v02_M | weights_and_design | 9 | sect8_hh_w5.dta | pw_w5 | blocked_until_official_raw_package_received |
| 1 | ETH_2021_ESPS-W5_v02_M | weights_and_design | 10 | sect9_hh_w5.dta | pw_w5 | blocked_until_official_raw_package_received |
| 1 | ETH_2021_ESPS-W5_v02_M | weights_and_design | 11 | sect10a_hh_w5.dta | pw_w5 | blocked_until_official_raw_package_received |
| 1 | ETH_2021_ESPS-W5_v02_M | weights_and_design | 12 | sect11_hh_w5.dta | pw_w5 | blocked_until_official_raw_package_received |
| 1 | ETH_2021_ESPS-W5_v02_M | consumption_or_income | 1 | cons_agg_w5.dta | nonfood_cons2 | blocked_until_official_raw_package_received |
| 1 | ETH_2021_ESPS-W5_v02_M | consumption_or_income | 2 | cons_agg_w5.dta | nom_nonfoodcons_aeq | blocked_until_official_raw_package_received |
| 1 | ETH_2021_ESPS-W5_v02_M | consumption_or_income | 3 | cons_agg_w5.dta | nonfood_cons_ann | blocked_until_official_raw_package_received |
| 1 | ETH_2021_ESPS-W5_v02_M | consumption_or_income | 4 | cons_agg_w5.dta | food_cons2 | blocked_until_official_raw_package_received |
| 1 | ETH_2021_ESPS-W5_v02_M | consumption_or_income | 5 | cons_agg_w5.dta | food_cons_ann | blocked_until_official_raw_package_received |
| 1 | ETH_2021_ESPS-W5_v02_M | consumption_or_income | 6 | cons_agg_w5.dta | nom_foodcons_aeq | blocked_until_official_raw_package_received |
| 1 | ETH_2021_ESPS-W5_v02_M | consumption_or_income | 7 | cons_agg_w5.dta | fafh_cons_ann | blocked_until_official_raw_package_received |
| 1 | ETH_2021_ESPS-W5_v02_M | consumption_or_income | 8 | cons_agg_w5.dta | spat_totcons_aeq | blocked_until_official_raw_package_received |
| 1 | ETH_2021_ESPS-W5_v02_M | consumption_or_income | 9 | cons_agg_w5.dta | educ_cons_ann | blocked_until_official_raw_package_received |
| 1 | ETH_2021_ESPS-W5_v02_M | consumption_or_income | 10 | cons_agg_w5.dta | nom_educcons_aeq | blocked_until_official_raw_package_received |
| 1 | ETH_2021_ESPS-W5_v02_M | consumption_or_income | 11 | cons_agg_w5.dta | nom_totcons_aeq | blocked_until_official_raw_package_received |
| ... | ... | ... | ... | ... | ... | ... |
