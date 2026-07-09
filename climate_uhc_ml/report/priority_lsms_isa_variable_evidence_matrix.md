# Priority LSMS-ISA Variable Evidence Matrix

Status: official public metadata variable shortlist for the refocused LSMS/ISA
queue. This is a pre-review layer for raw package checking. It does not verify
raw values, units, recall periods, missing codes, skip patterns, merge keys,
survey design, timing/geography, or climate linkage.

## Summary

| Metric | Value | Interpretation |
|---|---:|---|
| priority_lsms_variable_evidence_dataset_rows | 19 | Refocused LSMS/ISA datasets covered by official variable evidence. |
| priority_lsms_variable_evidence_requirement_rows | 152 | Requirement-by-wave coverage rows. |
| priority_lsms_variable_evidence_candidate_variable_rows | 1531 | Top official public metadata candidate variables shortlisted for raw review. |
| priority_lsms_variable_evidence_file_shortlist_rows | 629 | Official DDI files shortlisted by concept for raw package checking. |
| priority_lsms_variable_evidence_strong_requirement_rows | 128 | Non-documentation requirement rows with at least one strong metadata candidate. |
| priority_lsms_variable_evidence_documentation_only_requirement_rows | 19 | Rows where missing codes, units, recall, and skips require documentation/raw review rather than variable shortlisting. |
| priority_lsms_variable_evidence_no_candidate_requirement_rows | 0 | Rows where public metadata found no variable candidate. |
| priority_lsms_variable_evidence_handoff_readmes_written | 19 | Per-wave variable-evidence handoff files written. |
| priority_lsms_variable_evidence_raw_value_verified_rows | 0 | Official metadata shortlists do not verify raw values. |
| priority_lsms_variable_evidence_data_write_status | blocked_no_promoted_rows | No country-wave may write to data/ from metadata variable evidence alone. |
| modeling_gate_status | blocked | Models remain blocked until raw-backed promotion thresholds and accepted climate linkage pass. |
| priority_lsms_variable_evidence_coverage_status_documentation_and_raw_review_required_no_variable_shortlist | 19 | Requirement coverage status count. |
| priority_lsms_variable_evidence_coverage_status_official_metadata_strong_candidates_present_raw_review_required | 128 | Requirement coverage status count. |
| priority_lsms_variable_evidence_coverage_status_official_metadata_weak_candidates_present_raw_review_required | 5 | Requirement coverage status count. |
| priority_lsms_variable_evidence_queue_role_core_replacement_primary | 2 | Dataset count by refocused queue role. |
| priority_lsms_variable_evidence_queue_role_core_selected_lsms_isa_aligned | 8 | Dataset count by refocused queue role. |
| priority_lsms_variable_evidence_queue_role_replacement_backup_wave | 6 | Dataset count by refocused queue role. |
| priority_lsms_variable_evidence_queue_role_sixth_country_backup_candidate | 3 | Dataset count by refocused queue role. |

## Requirement Coverage

| download_priority_order | idno | requirement | candidate_variable_rows | strong_candidate_variable_rows | candidate_file_rows | coverage_status |
|---|---|---|---|---|---|---|
| 1 | ETH_2021_ESPS-W5_v02_M | household_person_keys | 12 | 12 | 11 | official_metadata_strong_candidates_present_raw_review_required |
| 1 | ETH_2021_ESPS-W5_v02_M | weights_and_design | 12 | 12 | 11 | official_metadata_strong_candidates_present_raw_review_required |
| 1 | ETH_2021_ESPS-W5_v02_M | consumption_or_income | 12 | 12 | 1 | official_metadata_strong_candidates_present_raw_review_required |
| 1 | ETH_2021_ESPS-W5_v02_M | oop_health_expenditure | 12 | 12 | 2 | official_metadata_strong_candidates_present_raw_review_required |
| 1 | ETH_2021_ESPS-W5_v02_M | health_need_and_access | 12 | 9 | 3 | official_metadata_strong_candidates_present_raw_review_required |
| 1 | ETH_2021_ESPS-W5_v02_M | survey_timing | 12 | 8 | 10 | official_metadata_strong_candidates_present_raw_review_required |
| 1 | ETH_2021_ESPS-W5_v02_M | climate_geography | 12 | 12 | 6 | official_metadata_strong_candidates_present_raw_review_required |
| 1 | ETH_2021_ESPS-W5_v02_M | missing_codes_units_recall_skip_patterns | 0 | 0 | 0 | documentation_and_raw_review_required_no_variable_shortlist |
| 2 | ETH_2018_ESS_v04_M | household_person_keys | 12 | 12 | 10 | official_metadata_strong_candidates_present_raw_review_required |
| 2 | ETH_2018_ESS_v04_M | weights_and_design | 12 | 12 | 12 | official_metadata_strong_candidates_present_raw_review_required |
| 2 | ETH_2018_ESS_v04_M | consumption_or_income | 12 | 12 | 2 | official_metadata_strong_candidates_present_raw_review_required |
| 2 | ETH_2018_ESS_v04_M | oop_health_expenditure | 12 | 12 | 2 | official_metadata_strong_candidates_present_raw_review_required |
| 2 | ETH_2018_ESS_v04_M | health_need_and_access | 12 | 12 | 2 | official_metadata_strong_candidates_present_raw_review_required |
| 2 | ETH_2018_ESS_v04_M | survey_timing | 12 | 9 | 7 | official_metadata_strong_candidates_present_raw_review_required |
| 2 | ETH_2018_ESS_v04_M | climate_geography | 12 | 12 | 6 | official_metadata_strong_candidates_present_raw_review_required |
| 2 | ETH_2018_ESS_v04_M | missing_codes_units_recall_skip_patterns | 0 | 0 | 0 | documentation_and_raw_review_required_no_variable_shortlist |
| 3 | MWI_2004_IHS-II_v01_M | household_person_keys | 12 | 12 | 12 | official_metadata_strong_candidates_present_raw_review_required |
| 3 | MWI_2004_IHS-II_v01_M | weights_and_design | 12 | 12 | 12 | official_metadata_strong_candidates_present_raw_review_required |
| 3 | MWI_2004_IHS-II_v01_M | consumption_or_income | 12 | 12 | 3 | official_metadata_strong_candidates_present_raw_review_required |
| 3 | MWI_2004_IHS-II_v01_M | oop_health_expenditure | 12 | 5 | 1 | official_metadata_strong_candidates_present_raw_review_required |
| 3 | MWI_2004_IHS-II_v01_M | health_need_and_access | 12 | 8 | 2 | official_metadata_strong_candidates_present_raw_review_required |
| 3 | MWI_2004_IHS-II_v01_M | survey_timing | 12 | 4 | 7 | official_metadata_strong_candidates_present_raw_review_required |
| 3 | MWI_2004_IHS-II_v01_M | climate_geography | 12 | 12 | 12 | official_metadata_strong_candidates_present_raw_review_required |
| 3 | MWI_2004_IHS-II_v01_M | missing_codes_units_recall_skip_patterns | 0 | 0 | 0 | documentation_and_raw_review_required_no_variable_shortlist |
| 4 | NGA_2012_GHSP-W2_v02_M | household_person_keys | 12 | 12 | 12 | official_metadata_strong_candidates_present_raw_review_required |
| 4 | NGA_2012_GHSP-W2_v02_M | weights_and_design | 12 | 12 | 4 | official_metadata_strong_candidates_present_raw_review_required |
| 4 | NGA_2012_GHSP-W2_v02_M | consumption_or_income | 12 | 12 | 4 | official_metadata_strong_candidates_present_raw_review_required |
| 4 | NGA_2012_GHSP-W2_v02_M | oop_health_expenditure | 6 | 6 | 1 | official_metadata_strong_candidates_present_raw_review_required |
| 4 | NGA_2012_GHSP-W2_v02_M | health_need_and_access | 12 | 9 | 3 | official_metadata_strong_candidates_present_raw_review_required |
| 4 | NGA_2012_GHSP-W2_v02_M | survey_timing | 12 | 12 | 1 | official_metadata_strong_candidates_present_raw_review_required |
| 4 | NGA_2012_GHSP-W2_v02_M | climate_geography | 12 | 4 | 5 | official_metadata_strong_candidates_present_raw_review_required |
| 4 | NGA_2012_GHSP-W2_v02_M | missing_codes_units_recall_skip_patterns | 0 | 0 | 0 | documentation_and_raw_review_required_no_variable_shortlist |
| 5 | NGA_2015_GHSP-W3_v02_M | household_person_keys | 12 | 12 | 12 | official_metadata_strong_candidates_present_raw_review_required |
| 5 | NGA_2015_GHSP-W3_v02_M | weights_and_design | 12 | 12 | 5 | official_metadata_strong_candidates_present_raw_review_required |
| 5 | NGA_2015_GHSP-W3_v02_M | consumption_or_income | 12 | 12 | 3 | official_metadata_strong_candidates_present_raw_review_required |
| 5 | NGA_2015_GHSP-W3_v02_M | oop_health_expenditure | 6 | 6 | 1 | official_metadata_strong_candidates_present_raw_review_required |
| 5 | NGA_2015_GHSP-W3_v02_M | health_need_and_access | 12 | 8 | 2 | official_metadata_strong_candidates_present_raw_review_required |
| 5 | NGA_2015_GHSP-W3_v02_M | survey_timing | 12 | 12 | 1 | official_metadata_strong_candidates_present_raw_review_required |
| 5 | NGA_2015_GHSP-W3_v02_M | climate_geography | 12 | 12 | 6 | official_metadata_strong_candidates_present_raw_review_required |
| 5 | NGA_2015_GHSP-W3_v02_M | missing_codes_units_recall_skip_patterns | 0 | 0 | 0 | documentation_and_raw_review_required_no_variable_shortlist |
| 6 | NGA_2010_GHSP-W1_v03_M | household_person_keys | 12 | 12 | 12 | official_metadata_strong_candidates_present_raw_review_required |
| 6 | NGA_2010_GHSP-W1_v03_M | weights_and_design | 12 | 4 | 8 | official_metadata_strong_candidates_present_raw_review_required |
| 6 | NGA_2010_GHSP-W1_v03_M | consumption_or_income | 12 | 12 | 2 | official_metadata_strong_candidates_present_raw_review_required |
| 6 | NGA_2010_GHSP-W1_v03_M | oop_health_expenditure | 5 | 5 | 1 | official_metadata_strong_candidates_present_raw_review_required |
| 6 | NGA_2010_GHSP-W1_v03_M | health_need_and_access | 12 | 8 | 3 | official_metadata_strong_candidates_present_raw_review_required |
| 6 | NGA_2010_GHSP-W1_v03_M | survey_timing | 12 | 12 | 2 | official_metadata_strong_candidates_present_raw_review_required |
| 6 | NGA_2010_GHSP-W1_v03_M | climate_geography | 12 | 12 | 3 | official_metadata_strong_candidates_present_raw_review_required |
| 6 | NGA_2010_GHSP-W1_v03_M | missing_codes_units_recall_skip_patterns | 0 | 0 | 0 | documentation_and_raw_review_required_no_variable_shortlist |
| 7 | TZA_2008_NPS-R1_v03_M | household_person_keys | 12 | 12 | 11 | official_metadata_strong_candidates_present_raw_review_required |
| 7 | TZA_2008_NPS-R1_v03_M | weights_and_design | 12 | 12 | 7 | official_metadata_strong_candidates_present_raw_review_required |
| 7 | TZA_2008_NPS-R1_v03_M | consumption_or_income | 12 | 12 | 3 | official_metadata_strong_candidates_present_raw_review_required |
| 7 | TZA_2008_NPS-R1_v03_M | oop_health_expenditure | 12 | 12 | 2 | official_metadata_strong_candidates_present_raw_review_required |
| 7 | TZA_2008_NPS-R1_v03_M | health_need_and_access | 12 | 0 | 2 | official_metadata_weak_candidates_present_raw_review_required |
| 7 | TZA_2008_NPS-R1_v03_M | survey_timing | 12 | 3 | 5 | official_metadata_strong_candidates_present_raw_review_required |
| 7 | TZA_2008_NPS-R1_v03_M | climate_geography | 12 | 12 | 9 | official_metadata_strong_candidates_present_raw_review_required |
| 7 | TZA_2008_NPS-R1_v03_M | missing_codes_units_recall_skip_patterns | 0 | 0 | 0 | documentation_and_raw_review_required_no_variable_shortlist |
| 8 | TZA_2010_NPS-R2_v03_M | household_person_keys | 12 | 12 | 11 | official_metadata_strong_candidates_present_raw_review_required |
| 8 | TZA_2010_NPS-R2_v03_M | weights_and_design | 12 | 12 | 11 | official_metadata_strong_candidates_present_raw_review_required |
| 8 | TZA_2010_NPS-R2_v03_M | consumption_or_income | 12 | 12 | 3 | official_metadata_strong_candidates_present_raw_review_required |
| 8 | TZA_2010_NPS-R2_v03_M | oop_health_expenditure | 8 | 8 | 1 | official_metadata_strong_candidates_present_raw_review_required |

## No-Candidate Requirement Rows

No non-documentation requirement row lacked a public-metadata variable candidate.

## Candidate Variable Preview

| download_priority_order | idno | requirement | candidate_rank | variable_name | variable_label | file_name | match_score |
|---|---|---|---|---|---|---|---|
| 1 | ETH_2021_ESPS-W5_v02_M | household_person_keys | 1 | individual_id | Household member ID | sect1_hh_w5.dta | 37 |
| 1 | ETH_2021_ESPS-W5_v02_M | household_person_keys | 2 | household_id | Unique Household Indentifier | sect1_hh_w5.dta | 33 |
| 1 | ETH_2021_ESPS-W5_v02_M | household_person_keys | 3 | household_id | Unique Household Indentifier | sect12b1_hh_w5.dta | 33 |
| 1 | ETH_2021_ESPS-W5_v02_M | household_person_keys | 4 | household_id | Unique Household Indentifier | sect1_pp_w5.dta | 33 |
| 1 | ETH_2021_ESPS-W5_v02_M | household_person_keys | 5 | household_id | Unique Household Indentifier | sect1_ph_w5.dta | 33 |
| 1 | ETH_2021_ESPS-W5_v02_M | household_person_keys | 6 | household_id | Unique Household Indentifier | sect2_pp_w5.dta | 31 |
| 1 | ETH_2021_ESPS-W5_v02_M | household_person_keys | 7 | household_id | Unique Household Indentifier | sect3_pp_w5.dta | 31 |
| 1 | ETH_2021_ESPS-W5_v02_M | household_person_keys | 8 | household_id | Unique Household Indentifier | sect4_pp_w5.dta | 31 |
| 1 | ETH_2021_ESPS-W5_v02_M | household_person_keys | 9 | individual_id | Household member ID | sect6c_hh_w5.dta | 28 |
| 1 | ETH_2021_ESPS-W5_v02_M | household_person_keys | 10 | individual_id | Household member ID | sect2_hh_w5.dta | 28 |
| 1 | ETH_2021_ESPS-W5_v02_M | household_person_keys | 11 | individual_id | Household member ID | sect3_hh_w5.dta | 28 |
| 1 | ETH_2021_ESPS-W5_v02_M | household_person_keys | 12 | individual_id | Household member ID | sect3b_hh_w5.dta | 28 |
| 1 | ETH_2021_ESPS-W5_v02_M | weights_and_design | 1 | pw_w5 | household sample weight | sect_cover_hh_w5.dta | 33 |
| 1 | ETH_2021_ESPS-W5_v02_M | weights_and_design | 2 | ea_id | Unique Enumeration Area Indentifier | sect_cover_hh_w5.dta | 31 |
| 1 | ETH_2021_ESPS-W5_v02_M | weights_and_design | 3 | pw_w5 | household sample weight | sect6b2_hh_w5.dta | 31 |
| 1 | ETH_2021_ESPS-W5_v02_M | weights_and_design | 4 | pw_w5 | household sample weight | sect6b3_hh_w5.dta | 31 |
| 1 | ETH_2021_ESPS-W5_v02_M | weights_and_design | 5 | pw_w5 | household sample weight | sect6b4_hh_w5.dta | 31 |
| 1 | ETH_2021_ESPS-W5_v02_M | weights_and_design | 6 | pw_w5 | household sample weight | sect6c_hh_w5.dta | 31 |
| 1 | ETH_2021_ESPS-W5_v02_M | weights_and_design | 7 | pw_w5 | household sample weight | sect7a_hh_w5.dta | 31 |
| 1 | ETH_2021_ESPS-W5_v02_M | weights_and_design | 8 | pw_w5 | household sample weight | sect7b_hh_w5.dta | 31 |
| 1 | ETH_2021_ESPS-W5_v02_M | weights_and_design | 9 | pw_w5 | household sample weight | sect8_hh_w5.dta | 31 |
| 1 | ETH_2021_ESPS-W5_v02_M | weights_and_design | 10 | pw_w5 | household sample weight | sect9_hh_w5.dta | 31 |
| 1 | ETH_2021_ESPS-W5_v02_M | weights_and_design | 11 | pw_w5 | household sample weight | sect10a_hh_w5.dta | 31 |
| 1 | ETH_2021_ESPS-W5_v02_M | weights_and_design | 12 | pw_w5 | household sample weight | sect11_hh_w5.dta | 31 |
| 1 | ETH_2021_ESPS-W5_v02_M | consumption_or_income | 1 | nonfood_cons2 | Non-food consumption | cons_agg_w5.dta | 52 |
| 1 | ETH_2021_ESPS-W5_v02_M | consumption_or_income | 2 | nom_nonfoodcons_aeq | Nominal annual expenditure on nonfood per adult equivalent | cons_agg_w5.dta | 45 |
| 1 | ETH_2021_ESPS-W5_v02_M | consumption_or_income | 3 | nonfood_cons_ann | annual expenditure on nonfood items (selected items) | cons_agg_w5.dta | 45 |
| 1 | ETH_2021_ESPS-W5_v02_M | consumption_or_income | 4 | food_cons2 | Food consumption | cons_agg_w5.dta | 36 |
| 1 | ETH_2021_ESPS-W5_v02_M | consumption_or_income | 5 | food_cons_ann | annual value of food consumption (selected items) | cons_agg_w5.dta | 36 |
| 1 | ETH_2021_ESPS-W5_v02_M | consumption_or_income | 6 | nom_foodcons_aeq | Nominal annual expenditure on food per adult equivalent | cons_agg_w5.dta | 29 |
| 1 | ETH_2021_ESPS-W5_v02_M | consumption_or_income | 7 | fafh_cons_ann | annual expenditure on food away from home | cons_agg_w5.dta | 25 |
| 1 | ETH_2021_ESPS-W5_v02_M | consumption_or_income | 8 | spat_totcons_aeq | Annual consumption per AEQ, spatially adjusted (food prices only) | cons_agg_w5.dta | 25 |
| 1 | ETH_2021_ESPS-W5_v02_M | consumption_or_income | 9 | educ_cons_ann | annual expenditure on education (including assistance) | cons_agg_w5.dta | 21 |
| 1 | ETH_2021_ESPS-W5_v02_M | consumption_or_income | 10 | nom_educcons_aeq | Nominal annual expenditure on education per adult equivalent | cons_agg_w5.dta | 21 |
| 1 | ETH_2021_ESPS-W5_v02_M | consumption_or_income | 11 | nom_totcons_aeq | Nominal annual consumption per adult equivalent | cons_agg_w5.dta | 21 |
| 1 | ETH_2021_ESPS-W5_v02_M | consumption_or_income | 12 | total_cons_ann | Total annual consumption | cons_agg_w5.dta | 21 |
| 1 | ETH_2021_ESPS-W5_v02_M | oop_health_expenditure | 1 | ls_s8_3q04 | 4.Total amount spent for breeding [LIVESTOCK TYPE] in the past 12 months | sect8_3_ls_w5.dta | 16 |
| 1 | ETH_2021_ESPS-W5_v02_M | oop_health_expenditure | 2 | ls_s8_3q22 | 22.Total amount spent on vaccines, anthelmingics and etc for [LIVESTOCK TYPE] | sect8_3_ls_w5.dta | 16 |
| 1 | ETH_2021_ESPS-W5_v02_M | oop_health_expenditure | 3 | ls_s8_3q24 | 24.Total amount spent on curative treatments for [LIVESTOCK TYPE] | sect8_3_ls_w5.dta | 16 |
| 1 | ETH_2021_ESPS-W5_v02_M | oop_health_expenditure | 4 | s3q17 | 17. How many nights did [NAME] spend in any health facility in last 12 months? | sect3_hh_w5.dta | 12 |
| 1 | ETH_2021_ESPS-W5_v02_M | oop_health_expenditure | 5 | s3q18 | 18. What were the total cost of [NAME]'s health consultations in last 12 months? | sect3_hh_w5.dta | 12 |
| 1 | ETH_2021_ESPS-W5_v02_M | oop_health_expenditure | 6 | ls_s8_3q03 | 3.Any cost incurred related to breeding [LIVESTOCK TYPE]? | sect8_3_ls_w5.dta | 12 |
| 1 | ETH_2021_ESPS-W5_v02_M | oop_health_expenditure | 7 | ls_s8_3q05 | 5.Has this holder paid anyone outside HH to help look after [LIVESTOCK TYPE]? | sect8_3_ls_w5.dta | 12 |
| 1 | ETH_2021_ESPS-W5_v02_M | oop_health_expenditure | 8 | ls_s8_3q06 | 6.Total wages paid for those looking after [LIVESTOCK TYPE] | sect8_3_ls_w5.dta | 12 |
| 1 | ETH_2021_ESPS-W5_v02_M | oop_health_expenditure | 9 | ls_s8_3q10a | 10a.During dry season, has water been paid for [LIVESTOCK TYPE]? | sect8_3_ls_w5.dta | 12 |
| 1 | ETH_2021_ESPS-W5_v02_M | oop_health_expenditure | 10 | ls_s8_3q10b | 10b.During rainy season, has water been paid for [LIVESTOCK TYPE]? | sect8_3_ls_w5.dta | 12 |
| 1 | ETH_2021_ESPS-W5_v02_M | oop_health_expenditure | 11 | ls_s8_3q11 | 11.How much has been paid for the water for [LIVESTOCK TYPE]? | sect8_3_ls_w5.dta | 12 |
| 1 | ETH_2021_ESPS-W5_v02_M | oop_health_expenditure | 12 | ls_s8_3q12_1 | 12.This holder's major feeding practices for [LIVESTOCK TYPE]: FEED 1 | sect8_3_ls_w5.dta | 12 |
| 1 | ETH_2021_ESPS-W5_v02_M | health_need_and_access | 1 | cs4q37 | 37. Distance to the nearest hospital/health facility with a medical doctor | sect04_com_w5.dta | 29 |
| 1 | ETH_2021_ESPS-W5_v02_M | health_need_and_access | 2 | s3q14 | 14. [NAME] consulted a healthcare provider in the last 12 months | sect3_hh_w5.dta | 21 |
| 1 | ETH_2021_ESPS-W5_v02_M | health_need_and_access | 3 | s3q15 | 15. Number of times [NAME] consulted a healthcare provider in the last 12 months | sect3_hh_w5.dta | 21 |
| 1 | ETH_2021_ESPS-W5_v02_M | health_need_and_access | 4 | s3q05 | 5. During the last 4 weeks, did [NAME] suffer from any illness or injury? | sect3_hh_w5.dta | 17 |
| 1 | ETH_2021_ESPS-W5_v02_M | health_need_and_access | 5 | s3q17 | 17. How many nights did [NAME] spend in any health facility in last 12 months? | sect3_hh_w5.dta | 17 |
| 1 | ETH_2021_ESPS-W5_v02_M | health_need_and_access | 6 | cs4q34 | 34. Is there a hospital/health center/clinic in this community? | sect04_com_w5.dta | 14 |
| 1 | ETH_2021_ESPS-W5_v02_M | health_need_and_access | 7 | cs4q35 | 35. Does the community hospital/health center have a doctor or health officer? | sect04_com_w5.dta | 14 |
| 1 | ETH_2021_ESPS-W5_v02_M | health_need_and_access | 8 | s3q13 | 13. Main reason for [NAME] not consulting a healthcare provider | sect3_hh_w5.dta | 14 |
| 1 | ETH_2021_ESPS-W5_v02_M | health_need_and_access | 9 | s3q18 | 18. What were the total cost of [NAME]'s health consultations in last 12 months? | sect3_hh_w5.dta | 14 |
| 1 | ETH_2021_ESPS-W5_v02_M | health_need_and_access | 10 | s3q15_1 | 15. Who are other HH members consulted on [FIELD]?: HH ID 1 | sect3_pp_w5.dta | 11 |
| 1 | ETH_2021_ESPS-W5_v02_M | health_need_and_access | 11 | s3q15_2 | 15. Who are other HH members consulted on [FIELD]?: HH ID 2 | sect3_pp_w5.dta | 11 |
| 1 | ETH_2021_ESPS-W5_v02_M | health_need_and_access | 12 | cs4q28 | 28. Distance to the nearest place where one can purchase common medicines | sect04_com_w5.dta | 10 |
| 1 | ETH_2021_ESPS-W5_v02_M | survey_timing | 1 | InterviewDate | 20. Date of Interview | sect_cover_pp_w5.dta | 46 |
| 1 | ETH_2021_ESPS-W5_v02_M | survey_timing | 2 | InterviewDate | 20. Date of Interview | sect_cover_ph_w5.dta | 46 |
| 1 | ETH_2021_ESPS-W5_v02_M | survey_timing | 3 | InterviewDate | 20. Date of Interview | sect_cover_ls_w5.dta | 46 |
| 1 | ETH_2021_ESPS-W5_v02_M | survey_timing | 4 | s12bq08a | 8. When did [NFE] start operating? (MONTH) | sect12b1_hh_w5.dta | 14 |
| 1 | ETH_2021_ESPS-W5_v02_M | survey_timing | 5 | s12bq08b | 8. When did [NFE] start operating? (YEAR) | sect12b1_hh_w5.dta | 14 |
| 1 | ETH_2021_ESPS-W5_v02_M | survey_timing | 6 | wetQ_avgstart | Avg start of wettest quarter in dekads 1-36, where first dekad of year =1 | eth_householdgeovariables_y5.dta | 14 |
| 1 | ETH_2021_ESPS-W5_v02_M | survey_timing | 7 | saq19__Timestamp | GPS coordinates of the dwelling: Timestamp | sect_cover_hh_w5.dta | 12 |
| 1 | ETH_2021_ESPS-W5_v02_M | survey_timing | 8 | wetQ_avgstart | Avg start of wettest quarter in dekads 1-36, where first dekad of year =1 | eth_plotgeovariables_y5.dta | 12 |
| 1 | ETH_2021_ESPS-W5_v02_M | survey_timing | 9 | item_cd_12months | Item Code (12 MONTHS) | sect7b_hh_w5.dta | 10 |
| 1 | ETH_2021_ESPS-W5_v02_M | survey_timing | 10 | s7q04 | 4. In total, how much did your household spend on [ITEM] in the past 12 months? | sect7b_hh_w5.dta | 10 |
| 1 | ETH_2021_ESPS-W5_v02_M | survey_timing | 11 | s10aq35 | 35. On average, how much does the household spend on electricty each month? | sect10a_hh_w5.dta | 10 |
| 1 | ETH_2021_ESPS-W5_v02_M | survey_timing | 12 | s12eq03_1 | 3. Did loss of crop production happended last time due to the [event]? | sect12e_hh_w5.dta | 10 |
| 1 | ETH_2021_ESPS-W5_v02_M | climate_geography | 1 | saq19__Latitude | GPS coordinates of the dwelling: Latitude | sect_cover_hh_w5.dta | 44 |
| 1 | ETH_2021_ESPS-W5_v02_M | climate_geography | 2 | saq19__Longitude | GPS coordinates of the dwelling: Longitude | sect_cover_hh_w5.dta | 44 |
| 1 | ETH_2021_ESPS-W5_v02_M | climate_geography | 3 | cs10q05__Latitude | 5. GPS COORDINATES OF THE MARKET:LATITUDE | sect10a_com_w5.dta | 42 |
| 1 | ETH_2021_ESPS-W5_v02_M | climate_geography | 4 | cs10q05__Longitude | 5. GPS COORDINATES OF THE MARKET: LONGITUDE | sect10a_com_w5.dta | 42 |
| 1 | ETH_2021_ESPS-W5_v02_M | climate_geography | 5 | saq19__Latitude | GPS coordinates of the dwelling: Latitude | sect_cover_pp_w5.dta | 42 |
| 1 | ETH_2021_ESPS-W5_v02_M | climate_geography | 6 | saq19__Longitude | GPS coordinates of the dwelling: Longitude | sect_cover_pp_w5.dta | 42 |
| 1 | ETH_2021_ESPS-W5_v02_M | climate_geography | 7 | saq19__Latitude | GPS coordinates of the dwelling: Latitude | sect_cover_ph_w5.dta | 42 |
| 1 | ETH_2021_ESPS-W5_v02_M | climate_geography | 8 | saq19__Longitude | GPS coordinates of the dwelling: Longitude | sect_cover_ph_w5.dta | 42 |

## File Shortlist Preview

| download_priority_order | idno | requirement | file_rank | file_name | candidate_variable_rows | top_variable_names |
|---|---|---|---|---|---|---|
| 1 | ETH_2021_ESPS-W5_v02_M | climate_geography | 1 | sect_cover_hh_w5.dta | 2 | saq19__Latitude;saq19__Longitude |
| 1 | ETH_2021_ESPS-W5_v02_M | climate_geography | 2 | sect10a_com_w5.dta | 2 | cs10q05__Latitude;cs10q05__Longitude |
| 1 | ETH_2021_ESPS-W5_v02_M | climate_geography | 3 | sect_cover_pp_w5.dta | 2 | saq19__Latitude;saq19__Longitude |
| 1 | ETH_2021_ESPS-W5_v02_M | climate_geography | 4 | sect_cover_ph_w5.dta | 2 | saq19__Latitude;saq19__Longitude |
| 1 | ETH_2021_ESPS-W5_v02_M | climate_geography | 5 | sect_cover_ls_w5.dta | 2 | saq19__Latitude;saq19__Longitude |
| 1 | ETH_2021_ESPS-W5_v02_M | climate_geography | 6 | sect3_pp_w5.dta | 2 | s3q09__Latitude;s3q09__Longitude |
| 1 | ETH_2021_ESPS-W5_v02_M | consumption_or_income | 1 | cons_agg_w5.dta | 12 | nonfood_cons2;nom_nonfoodcons_aeq;nonfood_cons_ann;food_cons2;food_cons_ann;nom_foodcons_aeq;fafh_cons_ann;spat_totco... |
| 1 | ETH_2021_ESPS-W5_v02_M | health_need_and_access | 1 | sect3_hh_w5.dta | 6 | s3q14;s3q15;s3q05;s3q17;s3q13;s3q18 |
| 1 | ETH_2021_ESPS-W5_v02_M | health_need_and_access | 2 | sect04_com_w5.dta | 4 | cs4q37;cs4q34;cs4q35;cs4q28 |
| 1 | ETH_2021_ESPS-W5_v02_M | health_need_and_access | 3 | sect3_pp_w5.dta | 2 | s3q15_1;s3q15_2 |
| 1 | ETH_2021_ESPS-W5_v02_M | household_person_keys | 1 | sect1_hh_w5.dta | 2 | individual_id;household_id |
| 1 | ETH_2021_ESPS-W5_v02_M | household_person_keys | 2 | sect12b1_hh_w5.dta | 1 | household_id |
| 1 | ETH_2021_ESPS-W5_v02_M | household_person_keys | 3 | sect1_pp_w5.dta | 1 | household_id |
| 1 | ETH_2021_ESPS-W5_v02_M | household_person_keys | 4 | sect1_ph_w5.dta | 1 | household_id |
| 1 | ETH_2021_ESPS-W5_v02_M | household_person_keys | 5 | sect2_pp_w5.dta | 1 | household_id |
| 1 | ETH_2021_ESPS-W5_v02_M | household_person_keys | 6 | sect3_pp_w5.dta | 1 | household_id |
| 1 | ETH_2021_ESPS-W5_v02_M | household_person_keys | 7 | sect4_pp_w5.dta | 1 | household_id |
| 1 | ETH_2021_ESPS-W5_v02_M | household_person_keys | 8 | sect6c_hh_w5.dta | 1 | individual_id |
| 1 | ETH_2021_ESPS-W5_v02_M | oop_health_expenditure | 1 | sect8_3_ls_w5.dta | 10 | ls_s8_3q04;ls_s8_3q22;ls_s8_3q24;ls_s8_3q03;ls_s8_3q05;ls_s8_3q06;ls_s8_3q10a;ls_s8_3q10b;ls_s8_3q11;ls_s8_3q12_1 |
| 1 | ETH_2021_ESPS-W5_v02_M | oop_health_expenditure | 2 | sect3_hh_w5.dta | 2 | s3q17;s3q18 |
| 1 | ETH_2021_ESPS-W5_v02_M | survey_timing | 1 | sect_cover_pp_w5.dta | 1 | InterviewDate |
| 1 | ETH_2021_ESPS-W5_v02_M | survey_timing | 2 | sect_cover_ph_w5.dta | 1 | InterviewDate |
| 1 | ETH_2021_ESPS-W5_v02_M | survey_timing | 3 | sect_cover_ls_w5.dta | 1 | InterviewDate |
| 1 | ETH_2021_ESPS-W5_v02_M | survey_timing | 4 | sect12b1_hh_w5.dta | 2 | s12bq08a;s12bq08b |
| 1 | ETH_2021_ESPS-W5_v02_M | survey_timing | 5 | sect7b_hh_w5.dta | 2 | item_cd_12months;s7q04 |
| 1 | ETH_2021_ESPS-W5_v02_M | survey_timing | 6 | eth_householdgeovariables_y5.dta | 1 | wetQ_avgstart |
| 1 | ETH_2021_ESPS-W5_v02_M | survey_timing | 7 | sect_cover_hh_w5.dta | 1 | saq19__Timestamp |
| 1 | ETH_2021_ESPS-W5_v02_M | survey_timing | 8 | eth_plotgeovariables_y5.dta | 1 | wetQ_avgstart |
| 1 | ETH_2021_ESPS-W5_v02_M | weights_and_design | 1 | sect_cover_hh_w5.dta | 2 | pw_w5;ea_id |
| 1 | ETH_2021_ESPS-W5_v02_M | weights_and_design | 2 | sect6b2_hh_w5.dta | 1 | pw_w5 |
| 1 | ETH_2021_ESPS-W5_v02_M | weights_and_design | 3 | sect6b3_hh_w5.dta | 1 | pw_w5 |
| 1 | ETH_2021_ESPS-W5_v02_M | weights_and_design | 4 | sect6b4_hh_w5.dta | 1 | pw_w5 |
| 1 | ETH_2021_ESPS-W5_v02_M | weights_and_design | 5 | sect6c_hh_w5.dta | 1 | pw_w5 |
| 1 | ETH_2021_ESPS-W5_v02_M | weights_and_design | 6 | sect7a_hh_w5.dta | 1 | pw_w5 |
| 1 | ETH_2021_ESPS-W5_v02_M | weights_and_design | 7 | sect7b_hh_w5.dta | 1 | pw_w5 |
| 1 | ETH_2021_ESPS-W5_v02_M | weights_and_design | 8 | sect8_hh_w5.dta | 1 | pw_w5 |
| 2 | ETH_2018_ESS_v04_M | climate_geography | 1 | sect_cover_ph_w4.dta | 3 | saq19__Latitude;saq19__Longitude;ea_id |
| 2 | ETH_2018_ESS_v04_M | climate_geography | 2 | sect_cover_pp_w4.dta | 2 | saq19__Latitude;saq19__Longitude |
| 2 | ETH_2018_ESS_v04_M | climate_geography | 3 | sect_cover_ls_w4.dta | 2 | saq19__Latitude;saq19__Longitude |
| 2 | ETH_2018_ESS_v04_M | climate_geography | 4 | sect3_pp_w4.dta | 2 | s3q09__Latitude;s3q09__Longitude |
| 2 | ETH_2018_ESS_v04_M | climate_geography | 5 | sect10a_com_w4.dta | 2 | cs10q05__Latitude;cs10q05__Longitude |
| 2 | ETH_2018_ESS_v04_M | climate_geography | 6 | sect_cover_hh_w4.dta | 1 | ea_id |
| 2 | ETH_2018_ESS_v04_M | consumption_or_income | 1 | sect7a_hh_w4.dta | 9 | ea_id;household_id;item_cd_30day;pw_w4;s7q01;s7q02;saq01;saq02;saq03 |
| 2 | ETH_2018_ESS_v04_M | consumption_or_income | 2 | cons_agg_w4.dta | 3 | nom_nonfoodcons_aeq;nonfood_cons_ann;food_cons_ann |
| 2 | ETH_2018_ESS_v04_M | health_need_and_access | 1 | sect3_hh_w4.dta | 11 | s3q14;s3q15;s3q05;s3q17;s3q13;s3q18;s3q06_1;s3q06_2;s3q06_os;s3q09a;s3q09b |
| 2 | ETH_2018_ESS_v04_M | health_need_and_access | 2 | sect04_com_w4.dta | 1 | cs4q37 |
| 2 | ETH_2018_ESS_v04_M | household_person_keys | 1 | sect1_hh_w4.dta | 2 | individual_id;household_id |
| 2 | ETH_2018_ESS_v04_M | household_person_keys | 2 | sect11b1_hh_w4.dta | 2 | individual_id;household_id |
| 2 | ETH_2018_ESS_v04_M | household_person_keys | 3 | sect10d1_hh_w4.dta | 1 | household_id |
| 2 | ETH_2018_ESS_v04_M | household_person_keys | 4 | sect1_ph_w4.dta | 1 | household_id |
| 2 | ETH_2018_ESS_v04_M | household_person_keys | 5 | sect1_pp_w4.dta | 1 | household_id |
| 2 | ETH_2018_ESS_v04_M | household_person_keys | 6 | sect10b_hh_w4.dta | 1 | household_id |
| 2 | ETH_2018_ESS_v04_M | household_person_keys | 7 | sect2_pp_w4.dta | 1 | household_id |
| 2 | ETH_2018_ESS_v04_M | household_person_keys | 8 | sect3_pp_w4.dta | 1 | household_id |
| 2 | ETH_2018_ESS_v04_M | oop_health_expenditure | 1 | sect8_3_ls_w4.dta | 10 | ls_s8_3q04;ls_s8_3q22;ls_s8_3q24;ls_s8_3q03;ls_s8_3q05;ls_s8_3q06;ls_s8_3q10a;ls_s8_3q10b;ls_s8_3q11;ls_s8_3q12_1 |
| 2 | ETH_2018_ESS_v04_M | oop_health_expenditure | 2 | sect3_hh_w4.dta | 2 | s3q17;s3q18 |
| 2 | ETH_2018_ESS_v04_M | survey_timing | 1 | sect_cover_ph_w4.dta | 2 | InterviewDate;saq19__Timestamp |
| 2 | ETH_2018_ESS_v04_M | survey_timing | 2 | sect_cover_pp_w4.dta | 2 | InterviewDate;saq19__Timestamp |
| 2 | ETH_2018_ESS_v04_M | survey_timing | 3 | sect_cover_ls_w4.dta | 2 | InterviewDate;saq19__Timestamp |
| 2 | ETH_2018_ESS_v04_M | survey_timing | 4 | sect12b1_hh_w4.dta | 2 | s12bq08a;s12bq08b |

## Guardrails

- Candidate variables are metadata search hits, not accepted harmonized fields.
- OOP and care-access candidates must be checked in raw values and questionnaires.
- Missing codes, units, recall periods, and skip patterns remain documentation/raw review tasks.
- No country-wave can be promoted or written to `data/` from this evidence alone.

## Machine-Readable Outputs

- `temp/priority_lsms_isa_variable_evidence_matrix.csv`
- `temp/priority_lsms_isa_requirement_variable_coverage.csv`
- `temp/priority_lsms_isa_concept_file_shortlist.csv`
- `result/priority_lsms_isa_variable_evidence_summary.csv`
