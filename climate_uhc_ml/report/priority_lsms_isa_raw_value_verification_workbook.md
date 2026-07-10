# Priority LSMS-ISA Raw Value Verification Workbook

Status: fail-closed raw-value verification workbook for the 19-wave refocused
LSMS/ISA promotion queue. It translates official metadata candidates into
requirement, variable, and file review rows that must be filled from original
raw files before any country-wave can be promoted.

This workbook does not verify raw values by itself.

## Summary

| Metric | Value | Interpretation |
|---|---:|---|
| priority_lsms_raw_value_workbook_dataset_rows | 19 | Refocused LSMS/ISA datasets covered by the raw-value verification workbook. |
| priority_lsms_raw_value_workbook_requirement_rows | 152 | Requirement-level raw-value verification rows. |
| priority_lsms_raw_value_workbook_variable_rows | 1531 | Candidate variable-level raw-value verification rows. |
| priority_lsms_raw_value_workbook_file_rows | 629 | Candidate file-level raw-value verification rows. |
| priority_lsms_raw_value_workbook_handoff_readmes_written | 19 | Per-wave raw-folder workbook handoffs written. |
| priority_lsms_raw_value_workbook_ready_for_manual_review_rows | 7 | Requirement rows ready for manual raw value review through full archive preflight or received raw schema evidence. |
| priority_lsms_raw_value_workbook_blocked_requirement_rows | 145 | Requirement rows still blocked before raw value review. |
| priority_lsms_raw_value_workbook_raw_value_verified_rows | 0 | Workbook rows are unverified until reviewer evidence fields are filled and accepted. |
| priority_lsms_raw_value_workbook_data_write_status | blocked_no_promoted_rows | No country-wave may write to data/ from an unfilled verification workbook. |
| modeling_gate_status | blocked | Models remain blocked until promoted registry thresholds and accepted climate linkage pass. |
| priority_lsms_raw_value_workbook_queue_role_core_replacement_primary | 2 | Dataset count by refocused queue role. |
| priority_lsms_raw_value_workbook_queue_role_core_selected_lsms_isa_aligned | 8 | Dataset count by refocused queue role. |
| priority_lsms_raw_value_workbook_queue_role_replacement_backup_wave | 6 | Dataset count by refocused queue role. |
| priority_lsms_raw_value_workbook_queue_role_sixth_country_backup_candidate | 3 | Dataset count by refocused queue role. |
| priority_lsms_raw_value_workbook_requirement_status_blocked_archive_or_direct_file_preflight_not_ready | 1 | Requirement workbook status count. |
| priority_lsms_raw_value_workbook_requirement_status_blocked_no_original_package | 144 | Requirement workbook status count. |
| priority_lsms_raw_value_workbook_requirement_status_ready_for_manual_raw_value_review_value_profile_available | 7 | Requirement workbook status count. |
| priority_lsms_raw_value_workbook_variable_status_blocked_no_original_package | 1447 | Variable workbook status count. |
| priority_lsms_raw_value_workbook_variable_status_ready_for_manual_raw_value_review_value_profile_available | 84 | Variable workbook status count. |
| priority_lsms_raw_value_workbook_file_status_blocked_no_original_package | 592 | File workbook status count. |
| priority_lsms_raw_value_workbook_file_status_ready_for_manual_raw_value_review_value_profile_available | 37 | File workbook status count. |

## Requirement Workbook Preview

| download_priority_order | idno | requirement | requirement_role | candidate_variable_rows | candidate_file_rows | current_verification_status |
|---|---|---|---|---|---|---|
| 1 | ETH_2021_ESPS-W5_v02_M | household_person_keys | merge_key_gate | 12 | 11 | blocked_no_original_package |
| 1 | ETH_2021_ESPS-W5_v02_M | weights_and_design | survey_design_gate | 12 | 11 | blocked_no_original_package |
| 1 | ETH_2021_ESPS-W5_v02_M | consumption_or_income | financial_denominator_gate | 12 | 1 | blocked_no_original_package |
| 1 | ETH_2021_ESPS-W5_v02_M | oop_health_expenditure | financial_outcome_gate | 12 | 2 | blocked_no_original_package |
| 1 | ETH_2021_ESPS-W5_v02_M | health_need_and_access | access_outcome_gate | 12 | 3 | blocked_no_original_package |
| 1 | ETH_2021_ESPS-W5_v02_M | survey_timing | climate_timing_gate | 12 | 10 | blocked_no_original_package |
| 1 | ETH_2021_ESPS-W5_v02_M | climate_geography | climate_geography_gate | 12 | 6 | blocked_no_original_package |
| 1 | ETH_2021_ESPS-W5_v02_M | missing_codes_units_recall_skip_patterns | documentation_semantics_gate | 0 | 0 | blocked_no_original_package |
| 2 | ETH_2018_ESS_v04_M | household_person_keys | merge_key_gate | 12 | 10 | blocked_no_original_package |
| 2 | ETH_2018_ESS_v04_M | weights_and_design | survey_design_gate | 12 | 12 | blocked_no_original_package |
| 2 | ETH_2018_ESS_v04_M | consumption_or_income | financial_denominator_gate | 12 | 2 | blocked_no_original_package |
| 2 | ETH_2018_ESS_v04_M | oop_health_expenditure | financial_outcome_gate | 12 | 2 | blocked_no_original_package |
| 2 | ETH_2018_ESS_v04_M | health_need_and_access | access_outcome_gate | 12 | 2 | blocked_no_original_package |
| 2 | ETH_2018_ESS_v04_M | survey_timing | climate_timing_gate | 12 | 7 | blocked_no_original_package |
| 2 | ETH_2018_ESS_v04_M | climate_geography | climate_geography_gate | 12 | 6 | blocked_no_original_package |
| 2 | ETH_2018_ESS_v04_M | missing_codes_units_recall_skip_patterns | documentation_semantics_gate | 0 | 0 | blocked_no_original_package |
| 3 | MWI_2004_IHS-II_v01_M | household_person_keys | merge_key_gate | 12 | 12 | ready_for_manual_raw_value_review_value_profile_available |
| 3 | MWI_2004_IHS-II_v01_M | weights_and_design | survey_design_gate | 12 | 12 | ready_for_manual_raw_value_review_value_profile_available |
| 3 | MWI_2004_IHS-II_v01_M | consumption_or_income | financial_denominator_gate | 12 | 3 | ready_for_manual_raw_value_review_value_profile_available |
| 3 | MWI_2004_IHS-II_v01_M | oop_health_expenditure | financial_outcome_gate | 12 | 1 | ready_for_manual_raw_value_review_value_profile_available |
| 3 | MWI_2004_IHS-II_v01_M | health_need_and_access | access_outcome_gate | 12 | 2 | ready_for_manual_raw_value_review_value_profile_available |
| 3 | MWI_2004_IHS-II_v01_M | survey_timing | climate_timing_gate | 12 | 7 | ready_for_manual_raw_value_review_value_profile_available |
| 3 | MWI_2004_IHS-II_v01_M | climate_geography | climate_geography_gate | 12 | 12 | ready_for_manual_raw_value_review_value_profile_available |
| 3 | MWI_2004_IHS-II_v01_M | missing_codes_units_recall_skip_patterns | documentation_semantics_gate | 0 | 0 | blocked_archive_or_direct_file_preflight_not_ready |
| 4 | NGA_2012_GHSP-W2_v02_M | household_person_keys | merge_key_gate | 12 | 12 | blocked_no_original_package |
| 4 | NGA_2012_GHSP-W2_v02_M | weights_and_design | survey_design_gate | 12 | 4 | blocked_no_original_package |
| 4 | NGA_2012_GHSP-W2_v02_M | consumption_or_income | financial_denominator_gate | 12 | 4 | blocked_no_original_package |
| 4 | NGA_2012_GHSP-W2_v02_M | oop_health_expenditure | financial_outcome_gate | 6 | 1 | blocked_no_original_package |
| 4 | NGA_2012_GHSP-W2_v02_M | health_need_and_access | access_outcome_gate | 12 | 3 | blocked_no_original_package |
| 4 | NGA_2012_GHSP-W2_v02_M | survey_timing | climate_timing_gate | 12 | 1 | blocked_no_original_package |
| 4 | NGA_2012_GHSP-W2_v02_M | climate_geography | climate_geography_gate | 12 | 5 | blocked_no_original_package |
| 4 | NGA_2012_GHSP-W2_v02_M | missing_codes_units_recall_skip_patterns | documentation_semantics_gate | 0 | 0 | blocked_no_original_package |
| 5 | NGA_2015_GHSP-W3_v02_M | household_person_keys | merge_key_gate | 12 | 12 | blocked_no_original_package |
| 5 | NGA_2015_GHSP-W3_v02_M | weights_and_design | survey_design_gate | 12 | 5 | blocked_no_original_package |
| 5 | NGA_2015_GHSP-W3_v02_M | consumption_or_income | financial_denominator_gate | 12 | 3 | blocked_no_original_package |
| 5 | NGA_2015_GHSP-W3_v02_M | oop_health_expenditure | financial_outcome_gate | 6 | 1 | blocked_no_original_package |
| 5 | NGA_2015_GHSP-W3_v02_M | health_need_and_access | access_outcome_gate | 12 | 2 | blocked_no_original_package |
| 5 | NGA_2015_GHSP-W3_v02_M | survey_timing | climate_timing_gate | 12 | 1 | blocked_no_original_package |
| 5 | NGA_2015_GHSP-W3_v02_M | climate_geography | climate_geography_gate | 12 | 6 | blocked_no_original_package |
| 5 | NGA_2015_GHSP-W3_v02_M | missing_codes_units_recall_skip_patterns | documentation_semantics_gate | 0 | 0 | blocked_no_original_package |
| 6 | NGA_2010_GHSP-W1_v03_M | household_person_keys | merge_key_gate | 12 | 12 | blocked_no_original_package |
| 6 | NGA_2010_GHSP-W1_v03_M | weights_and_design | survey_design_gate | 12 | 8 | blocked_no_original_package |
| 6 | NGA_2010_GHSP-W1_v03_M | consumption_or_income | financial_denominator_gate | 12 | 2 | blocked_no_original_package |
| 6 | NGA_2010_GHSP-W1_v03_M | oop_health_expenditure | financial_outcome_gate | 5 | 1 | blocked_no_original_package |
| 6 | NGA_2010_GHSP-W1_v03_M | health_need_and_access | access_outcome_gate | 12 | 3 | blocked_no_original_package |
| 6 | NGA_2010_GHSP-W1_v03_M | survey_timing | climate_timing_gate | 12 | 2 | blocked_no_original_package |
| 6 | NGA_2010_GHSP-W1_v03_M | climate_geography | climate_geography_gate | 12 | 3 | blocked_no_original_package |
| 6 | NGA_2010_GHSP-W1_v03_M | missing_codes_units_recall_skip_patterns | documentation_semantics_gate | 0 | 0 | blocked_no_original_package |
| 7 | TZA_2008_NPS-R1_v03_M | household_person_keys | merge_key_gate | 12 | 11 | blocked_no_original_package |
| 7 | TZA_2008_NPS-R1_v03_M | weights_and_design | survey_design_gate | 12 | 7 | blocked_no_original_package |
| 7 | TZA_2008_NPS-R1_v03_M | consumption_or_income | financial_denominator_gate | 12 | 3 | blocked_no_original_package |
| 7 | TZA_2008_NPS-R1_v03_M | oop_health_expenditure | financial_outcome_gate | 12 | 2 | blocked_no_original_package |
| 7 | TZA_2008_NPS-R1_v03_M | health_need_and_access | access_outcome_gate | 12 | 2 | blocked_no_original_package |
| 7 | TZA_2008_NPS-R1_v03_M | survey_timing | climate_timing_gate | 12 | 5 | blocked_no_original_package |
| 7 | TZA_2008_NPS-R1_v03_M | climate_geography | climate_geography_gate | 12 | 9 | blocked_no_original_package |
| 7 | TZA_2008_NPS-R1_v03_M | missing_codes_units_recall_skip_patterns | documentation_semantics_gate | 0 | 0 | blocked_no_original_package |
| 8 | TZA_2010_NPS-R2_v03_M | household_person_keys | merge_key_gate | 12 | 11 | blocked_no_original_package |
| 8 | TZA_2010_NPS-R2_v03_M | weights_and_design | survey_design_gate | 12 | 11 | blocked_no_original_package |
| 8 | TZA_2010_NPS-R2_v03_M | consumption_or_income | financial_denominator_gate | 12 | 3 | blocked_no_original_package |
| 8 | TZA_2010_NPS-R2_v03_M | oop_health_expenditure | financial_outcome_gate | 8 | 1 | blocked_no_original_package |
| 8 | TZA_2010_NPS-R2_v03_M | health_need_and_access | access_outcome_gate | 12 | 6 | blocked_no_original_package |
| 8 | TZA_2010_NPS-R2_v03_M | survey_timing | climate_timing_gate | 12 | 6 | blocked_no_original_package |
| 8 | TZA_2010_NPS-R2_v03_M | climate_geography | climate_geography_gate | 12 | 6 | blocked_no_original_package |
| 8 | TZA_2010_NPS-R2_v03_M | missing_codes_units_recall_skip_patterns | documentation_semantics_gate | 0 | 0 | blocked_no_original_package |
| 9 | TZA_2012_NPS-R3_v01_M | household_person_keys | merge_key_gate | 12 | 11 | blocked_no_original_package |
| 9 | TZA_2012_NPS-R3_v01_M | weights_and_design | survey_design_gate | 12 | 6 | blocked_no_original_package |
| 9 | TZA_2012_NPS-R3_v01_M | consumption_or_income | financial_denominator_gate | 12 | 2 | blocked_no_original_package |
| 9 | TZA_2012_NPS-R3_v01_M | oop_health_expenditure | financial_outcome_gate | 12 | 1 | blocked_no_original_package |
| 9 | TZA_2012_NPS-R3_v01_M | health_need_and_access | access_outcome_gate | 12 | 6 | blocked_no_original_package |
| 9 | TZA_2012_NPS-R3_v01_M | survey_timing | climate_timing_gate | 12 | 5 | blocked_no_original_package |
| 9 | TZA_2012_NPS-R3_v01_M | climate_geography | climate_geography_gate | 12 | 5 | blocked_no_original_package |
| 9 | TZA_2012_NPS-R3_v01_M | missing_codes_units_recall_skip_patterns | documentation_semantics_gate | 0 | 0 | blocked_no_original_package |
| 10 | UGA_2019_UNPS_v03_M | household_person_keys | merge_key_gate | 12 | 12 | blocked_no_original_package |
| 10 | UGA_2019_UNPS_v03_M | weights_and_design | survey_design_gate | 12 | 12 | blocked_no_original_package |
| 10 | UGA_2019_UNPS_v03_M | consumption_or_income | financial_denominator_gate | 12 | 2 | blocked_no_original_package |
| 10 | UGA_2019_UNPS_v03_M | oop_health_expenditure | financial_outcome_gate | 12 | 3 | blocked_no_original_package |
| 10 | UGA_2019_UNPS_v03_M | health_need_and_access | access_outcome_gate | 12 | 4 | blocked_no_original_package |
| 10 | UGA_2019_UNPS_v03_M | survey_timing | climate_timing_gate | 12 | 6 | blocked_no_original_package |
| 10 | UGA_2019_UNPS_v03_M | climate_geography | climate_geography_gate | 12 | 10 | blocked_no_original_package |
| 10 | UGA_2019_UNPS_v03_M | missing_codes_units_recall_skip_patterns | documentation_semantics_gate | 0 | 0 | blocked_no_original_package |

## Variable Workbook Preview

| download_priority_order | idno | requirement | candidate_rank | file_name | variable_name | variable_label | current_verification_status |
|---|---|---|---|---|---|---|---|
| 1 | ETH_2021_ESPS-W5_v02_M | household_person_keys | 1 | sect1_hh_w5.dta | individual_id | Household member ID | blocked_no_original_package |
| 1 | ETH_2021_ESPS-W5_v02_M | household_person_keys | 2 | sect1_hh_w5.dta | household_id | Unique Household Indentifier | blocked_no_original_package |
| 1 | ETH_2021_ESPS-W5_v02_M | household_person_keys | 3 | sect12b1_hh_w5.dta | household_id | Unique Household Indentifier | blocked_no_original_package |
| 1 | ETH_2021_ESPS-W5_v02_M | household_person_keys | 4 | sect1_pp_w5.dta | household_id | Unique Household Indentifier | blocked_no_original_package |
| 1 | ETH_2021_ESPS-W5_v02_M | household_person_keys | 5 | sect1_ph_w5.dta | household_id | Unique Household Indentifier | blocked_no_original_package |
| 1 | ETH_2021_ESPS-W5_v02_M | household_person_keys | 6 | sect2_pp_w5.dta | household_id | Unique Household Indentifier | blocked_no_original_package |
| 1 | ETH_2021_ESPS-W5_v02_M | household_person_keys | 7 | sect3_pp_w5.dta | household_id | Unique Household Indentifier | blocked_no_original_package |
| 1 | ETH_2021_ESPS-W5_v02_M | household_person_keys | 8 | sect4_pp_w5.dta | household_id | Unique Household Indentifier | blocked_no_original_package |
| 1 | ETH_2021_ESPS-W5_v02_M | household_person_keys | 9 | sect6c_hh_w5.dta | individual_id | Household member ID | blocked_no_original_package |
| 1 | ETH_2021_ESPS-W5_v02_M | household_person_keys | 10 | sect2_hh_w5.dta | individual_id | Household member ID | blocked_no_original_package |
| 1 | ETH_2021_ESPS-W5_v02_M | household_person_keys | 11 | sect3_hh_w5.dta | individual_id | Household member ID | blocked_no_original_package |
| 1 | ETH_2021_ESPS-W5_v02_M | household_person_keys | 12 | sect3b_hh_w5.dta | individual_id | Household member ID | blocked_no_original_package |
| 1 | ETH_2021_ESPS-W5_v02_M | weights_and_design | 1 | sect_cover_hh_w5.dta | pw_w5 | household sample weight | blocked_no_original_package |
| 1 | ETH_2021_ESPS-W5_v02_M | weights_and_design | 2 | sect_cover_hh_w5.dta | ea_id | Unique Enumeration Area Indentifier | blocked_no_original_package |
| 1 | ETH_2021_ESPS-W5_v02_M | weights_and_design | 3 | sect6b2_hh_w5.dta | pw_w5 | household sample weight | blocked_no_original_package |
| 1 | ETH_2021_ESPS-W5_v02_M | weights_and_design | 4 | sect6b3_hh_w5.dta | pw_w5 | household sample weight | blocked_no_original_package |
| 1 | ETH_2021_ESPS-W5_v02_M | weights_and_design | 5 | sect6b4_hh_w5.dta | pw_w5 | household sample weight | blocked_no_original_package |
| 1 | ETH_2021_ESPS-W5_v02_M | weights_and_design | 6 | sect6c_hh_w5.dta | pw_w5 | household sample weight | blocked_no_original_package |
| 1 | ETH_2021_ESPS-W5_v02_M | weights_and_design | 7 | sect7a_hh_w5.dta | pw_w5 | household sample weight | blocked_no_original_package |
| 1 | ETH_2021_ESPS-W5_v02_M | weights_and_design | 8 | sect7b_hh_w5.dta | pw_w5 | household sample weight | blocked_no_original_package |
| 1 | ETH_2021_ESPS-W5_v02_M | weights_and_design | 9 | sect8_hh_w5.dta | pw_w5 | household sample weight | blocked_no_original_package |
| 1 | ETH_2021_ESPS-W5_v02_M | weights_and_design | 10 | sect9_hh_w5.dta | pw_w5 | household sample weight | blocked_no_original_package |
| 1 | ETH_2021_ESPS-W5_v02_M | weights_and_design | 11 | sect10a_hh_w5.dta | pw_w5 | household sample weight | blocked_no_original_package |
| 1 | ETH_2021_ESPS-W5_v02_M | weights_and_design | 12 | sect11_hh_w5.dta | pw_w5 | household sample weight | blocked_no_original_package |
| 1 | ETH_2021_ESPS-W5_v02_M | consumption_or_income | 1 | cons_agg_w5.dta | nonfood_cons2 | Non-food consumption | blocked_no_original_package |
| 1 | ETH_2021_ESPS-W5_v02_M | consumption_or_income | 2 | cons_agg_w5.dta | nom_nonfoodcons_aeq | Nominal annual expenditure on nonfood per adult equivalent | blocked_no_original_package |
| 1 | ETH_2021_ESPS-W5_v02_M | consumption_or_income | 3 | cons_agg_w5.dta | nonfood_cons_ann | annual expenditure on nonfood items (selected items) | blocked_no_original_package |
| 1 | ETH_2021_ESPS-W5_v02_M | consumption_or_income | 4 | cons_agg_w5.dta | food_cons2 | Food consumption | blocked_no_original_package |
| 1 | ETH_2021_ESPS-W5_v02_M | consumption_or_income | 5 | cons_agg_w5.dta | food_cons_ann | annual value of food consumption (selected items) | blocked_no_original_package |
| 1 | ETH_2021_ESPS-W5_v02_M | consumption_or_income | 6 | cons_agg_w5.dta | nom_foodcons_aeq | Nominal annual expenditure on food per adult equivalent | blocked_no_original_package |
| 1 | ETH_2021_ESPS-W5_v02_M | consumption_or_income | 7 | cons_agg_w5.dta | fafh_cons_ann | annual expenditure on food away from home | blocked_no_original_package |
| 1 | ETH_2021_ESPS-W5_v02_M | consumption_or_income | 8 | cons_agg_w5.dta | spat_totcons_aeq | Annual consumption per AEQ, spatially adjusted (food prices only) | blocked_no_original_package |
| 1 | ETH_2021_ESPS-W5_v02_M | consumption_or_income | 9 | cons_agg_w5.dta | educ_cons_ann | annual expenditure on education (including assistance) | blocked_no_original_package |
| 1 | ETH_2021_ESPS-W5_v02_M | consumption_or_income | 10 | cons_agg_w5.dta | nom_educcons_aeq | Nominal annual expenditure on education per adult equivalent | blocked_no_original_package |
| 1 | ETH_2021_ESPS-W5_v02_M | consumption_or_income | 11 | cons_agg_w5.dta | nom_totcons_aeq | Nominal annual consumption per adult equivalent | blocked_no_original_package |
| 1 | ETH_2021_ESPS-W5_v02_M | consumption_or_income | 12 | cons_agg_w5.dta | total_cons_ann | Total annual consumption | blocked_no_original_package |
| 1 | ETH_2021_ESPS-W5_v02_M | oop_health_expenditure | 1 | sect8_3_ls_w5.dta | ls_s8_3q04 | 4.Total amount spent for breeding [LIVESTOCK TYPE] in the past 12 months | blocked_no_original_package |
| 1 | ETH_2021_ESPS-W5_v02_M | oop_health_expenditure | 2 | sect8_3_ls_w5.dta | ls_s8_3q22 | 22.Total amount spent on vaccines, anthelmingics and etc for [LIVESTOCK TYPE] | blocked_no_original_package |
| 1 | ETH_2021_ESPS-W5_v02_M | oop_health_expenditure | 3 | sect8_3_ls_w5.dta | ls_s8_3q24 | 24.Total amount spent on curative treatments for [LIVESTOCK TYPE] | blocked_no_original_package |
| 1 | ETH_2021_ESPS-W5_v02_M | oop_health_expenditure | 4 | sect3_hh_w5.dta | s3q17 | 17. How many nights did [NAME] spend in any health facility in last 12 months? | blocked_no_original_package |
| 1 | ETH_2021_ESPS-W5_v02_M | oop_health_expenditure | 5 | sect3_hh_w5.dta | s3q18 | 18. What were the total cost of [NAME]'s health consultations in last 12 months? | blocked_no_original_package |
| 1 | ETH_2021_ESPS-W5_v02_M | oop_health_expenditure | 6 | sect8_3_ls_w5.dta | ls_s8_3q03 | 3.Any cost incurred related to breeding [LIVESTOCK TYPE]? | blocked_no_original_package |
| 1 | ETH_2021_ESPS-W5_v02_M | oop_health_expenditure | 7 | sect8_3_ls_w5.dta | ls_s8_3q05 | 5.Has this holder paid anyone outside HH to help look after [LIVESTOCK TYPE]? | blocked_no_original_package |
| 1 | ETH_2021_ESPS-W5_v02_M | oop_health_expenditure | 8 | sect8_3_ls_w5.dta | ls_s8_3q06 | 6.Total wages paid for those looking after [LIVESTOCK TYPE] | blocked_no_original_package |
| 1 | ETH_2021_ESPS-W5_v02_M | oop_health_expenditure | 9 | sect8_3_ls_w5.dta | ls_s8_3q10a | 10a.During dry season, has water been paid for [LIVESTOCK TYPE]? | blocked_no_original_package |
| 1 | ETH_2021_ESPS-W5_v02_M | oop_health_expenditure | 10 | sect8_3_ls_w5.dta | ls_s8_3q10b | 10b.During rainy season, has water been paid for [LIVESTOCK TYPE]? | blocked_no_original_package |
| 1 | ETH_2021_ESPS-W5_v02_M | oop_health_expenditure | 11 | sect8_3_ls_w5.dta | ls_s8_3q11 | 11.How much has been paid for the water for [LIVESTOCK TYPE]? | blocked_no_original_package |
| 1 | ETH_2021_ESPS-W5_v02_M | oop_health_expenditure | 12 | sect8_3_ls_w5.dta | ls_s8_3q12_1 | 12.This holder's major feeding practices for [LIVESTOCK TYPE]: FEED 1 | blocked_no_original_package |
| 1 | ETH_2021_ESPS-W5_v02_M | health_need_and_access | 1 | sect04_com_w5.dta | cs4q37 | 37. Distance to the nearest hospital/health facility with a medical doctor | blocked_no_original_package |
| 1 | ETH_2021_ESPS-W5_v02_M | health_need_and_access | 2 | sect3_hh_w5.dta | s3q14 | 14. [NAME] consulted a healthcare provider in the last 12 months | blocked_no_original_package |
| 1 | ETH_2021_ESPS-W5_v02_M | health_need_and_access | 3 | sect3_hh_w5.dta | s3q15 | 15. Number of times [NAME] consulted a healthcare provider in the last 12 months | blocked_no_original_package |
| 1 | ETH_2021_ESPS-W5_v02_M | health_need_and_access | 4 | sect3_hh_w5.dta | s3q05 | 5. During the last 4 weeks, did [NAME] suffer from any illness or injury? | blocked_no_original_package |
| 1 | ETH_2021_ESPS-W5_v02_M | health_need_and_access | 5 | sect3_hh_w5.dta | s3q17 | 17. How many nights did [NAME] spend in any health facility in last 12 months? | blocked_no_original_package |
| 1 | ETH_2021_ESPS-W5_v02_M | health_need_and_access | 6 | sect04_com_w5.dta | cs4q34 | 34. Is there a hospital/health center/clinic in this community? | blocked_no_original_package |
| 1 | ETH_2021_ESPS-W5_v02_M | health_need_and_access | 7 | sect04_com_w5.dta | cs4q35 | 35. Does the community hospital/health center have a doctor or health officer? | blocked_no_original_package |
| 1 | ETH_2021_ESPS-W5_v02_M | health_need_and_access | 8 | sect3_hh_w5.dta | s3q13 | 13. Main reason for [NAME] not consulting a healthcare provider | blocked_no_original_package |
| 1 | ETH_2021_ESPS-W5_v02_M | health_need_and_access | 9 | sect3_hh_w5.dta | s3q18 | 18. What were the total cost of [NAME]'s health consultations in last 12 months? | blocked_no_original_package |
| 1 | ETH_2021_ESPS-W5_v02_M | health_need_and_access | 10 | sect3_pp_w5.dta | s3q15_1 | 15. Who are other HH members consulted on [FIELD]?: HH ID 1 | blocked_no_original_package |
| 1 | ETH_2021_ESPS-W5_v02_M | health_need_and_access | 11 | sect3_pp_w5.dta | s3q15_2 | 15. Who are other HH members consulted on [FIELD]?: HH ID 2 | blocked_no_original_package |
| 1 | ETH_2021_ESPS-W5_v02_M | health_need_and_access | 12 | sect04_com_w5.dta | cs4q28 | 28. Distance to the nearest place where one can purchase common medicines | blocked_no_original_package |
| 1 | ETH_2021_ESPS-W5_v02_M | survey_timing | 1 | sect_cover_pp_w5.dta | InterviewDate | 20. Date of Interview | blocked_no_original_package |
| 1 | ETH_2021_ESPS-W5_v02_M | survey_timing | 2 | sect_cover_ph_w5.dta | InterviewDate | 20. Date of Interview | blocked_no_original_package |
| 1 | ETH_2021_ESPS-W5_v02_M | survey_timing | 3 | sect_cover_ls_w5.dta | InterviewDate | 20. Date of Interview | blocked_no_original_package |
| 1 | ETH_2021_ESPS-W5_v02_M | survey_timing | 4 | sect12b1_hh_w5.dta | s12bq08a | 8. When did [NFE] start operating? (MONTH) | blocked_no_original_package |
| 1 | ETH_2021_ESPS-W5_v02_M | survey_timing | 5 | sect12b1_hh_w5.dta | s12bq08b | 8. When did [NFE] start operating? (YEAR) | blocked_no_original_package |
| 1 | ETH_2021_ESPS-W5_v02_M | survey_timing | 6 | eth_householdgeovariables_y5.dta | wetQ_avgstart | Avg start of wettest quarter in dekads 1-36, where first dekad of year =1 | blocked_no_original_package |
| 1 | ETH_2021_ESPS-W5_v02_M | survey_timing | 7 | sect_cover_hh_w5.dta | saq19__Timestamp | GPS coordinates of the dwelling: Timestamp | blocked_no_original_package |
| 1 | ETH_2021_ESPS-W5_v02_M | survey_timing | 8 | eth_plotgeovariables_y5.dta | wetQ_avgstart | Avg start of wettest quarter in dekads 1-36, where first dekad of year =1 | blocked_no_original_package |
| 1 | ETH_2021_ESPS-W5_v02_M | survey_timing | 9 | sect7b_hh_w5.dta | item_cd_12months | Item Code (12 MONTHS) | blocked_no_original_package |
| 1 | ETH_2021_ESPS-W5_v02_M | survey_timing | 10 | sect7b_hh_w5.dta | s7q04 | 4. In total, how much did your household spend on [ITEM] in the past 12 months? | blocked_no_original_package |
| 1 | ETH_2021_ESPS-W5_v02_M | survey_timing | 11 | sect10a_hh_w5.dta | s10aq35 | 35. On average, how much does the household spend on electricty each month? | blocked_no_original_package |
| 1 | ETH_2021_ESPS-W5_v02_M | survey_timing | 12 | sect12e_hh_w5.dta | s12eq03_1 | 3. Did loss of crop production happended last time due to the [event]? | blocked_no_original_package |
| 1 | ETH_2021_ESPS-W5_v02_M | climate_geography | 1 | sect_cover_hh_w5.dta | saq19__Latitude | GPS coordinates of the dwelling: Latitude | blocked_no_original_package |
| 1 | ETH_2021_ESPS-W5_v02_M | climate_geography | 2 | sect_cover_hh_w5.dta | saq19__Longitude | GPS coordinates of the dwelling: Longitude | blocked_no_original_package |
| 1 | ETH_2021_ESPS-W5_v02_M | climate_geography | 3 | sect10a_com_w5.dta | cs10q05__Latitude | 5. GPS COORDINATES OF THE MARKET:LATITUDE | blocked_no_original_package |
| 1 | ETH_2021_ESPS-W5_v02_M | climate_geography | 4 | sect10a_com_w5.dta | cs10q05__Longitude | 5. GPS COORDINATES OF THE MARKET: LONGITUDE | blocked_no_original_package |
| 1 | ETH_2021_ESPS-W5_v02_M | climate_geography | 5 | sect_cover_pp_w5.dta | saq19__Latitude | GPS coordinates of the dwelling: Latitude | blocked_no_original_package |
| 1 | ETH_2021_ESPS-W5_v02_M | climate_geography | 6 | sect_cover_pp_w5.dta | saq19__Longitude | GPS coordinates of the dwelling: Longitude | blocked_no_original_package |
| 1 | ETH_2021_ESPS-W5_v02_M | climate_geography | 7 | sect_cover_ph_w5.dta | saq19__Latitude | GPS coordinates of the dwelling: Latitude | blocked_no_original_package |
| 1 | ETH_2021_ESPS-W5_v02_M | climate_geography | 8 | sect_cover_ph_w5.dta | saq19__Longitude | GPS coordinates of the dwelling: Longitude | blocked_no_original_package |

## File Workbook Preview

| download_priority_order | idno | requirement | file_rank | file_name | candidate_variable_rows | current_file_verification_status |
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
| 3 | MWI_2004_IHS-II_v01_M | climate_geography | 1 | sec_a.NSDstat | 1 | ready_for_manual_raw_value_review_value_profile_available |
| 3 | MWI_2004_IHS-II_v01_M | climate_geography | 2 | sec_f.NSDstat | 1 | ready_for_manual_raw_value_review_value_profile_available |
| 3 | MWI_2004_IHS-II_v01_M | climate_geography | 3 | sec_g.NSDstat | 1 | ready_for_manual_raw_value_review_value_profile_available |
| 3 | MWI_2004_IHS-II_v01_M | climate_geography | 4 | sec_h.NSDstat | 1 | ready_for_manual_raw_value_review_value_profile_available |
| 3 | MWI_2004_IHS-II_v01_M | climate_geography | 5 | sec_i.NSDstat | 1 | ready_for_manual_raw_value_review_value_profile_available |
| 3 | MWI_2004_IHS-II_v01_M | climate_geography | 6 | sec_j1.NSDstat | 1 | ready_for_manual_raw_value_review_value_profile_available |
| 3 | MWI_2004_IHS-II_v01_M | climate_geography | 7 | sec_j2.NSDstat | 1 | ready_for_manual_raw_value_review_value_profile_available |
| 3 | MWI_2004_IHS-II_v01_M | climate_geography | 8 | sec_k.NSDstat | 1 | ready_for_manual_raw_value_review_value_profile_available |
| 3 | MWI_2004_IHS-II_v01_M | consumption_or_income | 1 | sec_j1.NSDstat | 10 | ready_for_manual_raw_value_review_value_profile_available |

## Machine-Readable Outputs

- `temp/priority_lsms_isa_raw_value_requirement_workbook.csv`
- `temp/priority_lsms_isa_raw_value_variable_workbook.csv`
- `temp/priority_lsms_isa_raw_value_file_workbook.csv`
- `result/priority_lsms_isa_raw_value_verification_workbook_summary.csv`

## Guardrails

- Empty fill fields mean the requirement is not value-verified.
- Metadata candidates must be checked against original raw files and questionnaires.
- Financial-protection readiness requires verified consumption/income, OOP health expenditure, weights, design, and denominator semantics.
- Access readiness requires verified illness/need, care-seeking, forgone-care, and barrier skip patterns.
- Climate readiness requires verified timing and geography plus an accepted CHIRPS or ERA5 route.
