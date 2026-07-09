# Priority First-Pass Variable Review Queue

Status: compact review queue for the 13-wave priority/backup campaign. It
selects a minimum first-pass set of metadata candidate variables for each
country-wave promotion requirement. It is not raw-value verification and does
not promote any dataset.

## Summary

| Metric | Value | Interpretation |
|---|---:|---|
| priority_first_pass_dataset_rows | 13 | Priority and backup country-waves covered by the first-pass review queue. |
| priority_first_pass_requirement_rows | 104 | Country-wave requirement coverage rows in the first-pass queue. |
| priority_first_pass_selected_variable_rows | 465 | Selected metadata candidate variables for first-pass post-download review. |
| priority_first_pass_distinct_countries | 8 | Distinct countries covered by the first-pass queue. |
| priority_first_pass_priority_10_wave_rows | 10 | Phase-1 priority waves covered. |
| priority_first_pass_backup_wave_rows | 3 | Sixth-country backup waves covered. |
| priority_first_pass_missing_requirement_coverage_rows | 0 | Requirement rows lacking at least one selected variable candidate for a mapped concept. |
| priority_first_pass_raw_package_received_rows | 0 | Covered datasets with complete or target-covered original raw package receipt. |
| priority_first_pass_ready_after_download_rows | 0 | Selected variable rows ready for immediate first-pass raw value review. |
| priority_first_pass_handoff_readmes_written | 13 | Per-wave first-pass queue handoff README files written. |
| modeling_gate_status | blocked | Models remain blocked until promoted registry thresholds and accepted climate linkage pass. |
| first_pass_review_status_blocked_raw_package_not_received | 465 | Selected variable first-pass status count. |
| first_pass_requirement_status_blocked_raw_package_not_received | 104 | Requirement first-pass status count. |

## Selected Variable Status

| First-pass status | Count |
|---|---:|
| `blocked_raw_package_not_received` | 465 |

## Requirement Status

| Requirement first-pass status | Count |
|---|---:|
| `blocked_raw_package_not_received` | 104 |

## Concept Mix

| Concept | Count |
|---|---:|
| `survey_weight` | 52 |
| `oop_health_expenditure` | 52 |
| `health_need` | 52 |
| `care_or_barrier` | 52 |
| `climate_geography` | 52 |
| `total_consumption_or_income` | 42 |
| `survey_timing` | 40 |
| `household_id` | 38 |
| `demographics` | 26 |
| `psu_cluster` | 23 |
| `strata` | 19 |
| `insurance` | 17 |

## Coverage Preview

| acquisition_batch_rank | idno | requirement_id | selected_variable_rows | missing_concepts | first_pass_requirement_status |
|---|---|---|---|---|---|
| 1 | ETH_2021_ESPS-W5_v02_M | household_person_merge_keys | 4 |  | blocked_raw_package_not_received |
| 1 | ETH_2021_ESPS-W5_v02_M | weights_and_survey_design | 6 |  | blocked_raw_package_not_received |
| 1 | ETH_2021_ESPS-W5_v02_M | consumption_or_income_aggregate | 2 |  | blocked_raw_package_not_received |
| 1 | ETH_2021_ESPS-W5_v02_M | oop_health_expenditure | 2 |  | blocked_raw_package_not_received |
| 1 | ETH_2021_ESPS-W5_v02_M | illness_need_care_access | 5 |  | blocked_raw_package_not_received |
| 1 | ETH_2021_ESPS-W5_v02_M | survey_timing | 1 |  | blocked_raw_package_not_received |
| 1 | ETH_2021_ESPS-W5_v02_M | geography_climate_linkage | 2 |  | blocked_raw_package_not_received |
| 1 | ETH_2021_ESPS-W5_v02_M | missing_skip_units_recall | 15 |  | blocked_raw_package_not_received |
| 2 | ETH_2018_ESS_v04_M | household_person_merge_keys | 4 |  | blocked_raw_package_not_received |
| 2 | ETH_2018_ESS_v04_M | weights_and_survey_design | 6 |  | blocked_raw_package_not_received |
| 2 | ETH_2018_ESS_v04_M | consumption_or_income_aggregate | 2 |  | blocked_raw_package_not_received |
| 2 | ETH_2018_ESS_v04_M | oop_health_expenditure | 2 |  | blocked_raw_package_not_received |
| 2 | ETH_2018_ESS_v04_M | illness_need_care_access | 5 |  | blocked_raw_package_not_received |
| 2 | ETH_2018_ESS_v04_M | survey_timing | 2 |  | blocked_raw_package_not_received |
| 2 | ETH_2018_ESS_v04_M | geography_climate_linkage | 2 |  | blocked_raw_package_not_received |
| 2 | ETH_2018_ESS_v04_M | missing_skip_units_recall | 16 |  | blocked_raw_package_not_received |
| 3 | MWI_2007-2009_MTM_v01_M | household_person_merge_keys | 4 |  | blocked_raw_package_not_received |
| 3 | MWI_2007-2009_MTM_v01_M | weights_and_survey_design | 5 |  | blocked_raw_package_not_received |
| 3 | MWI_2007-2009_MTM_v01_M | consumption_or_income_aggregate | 2 |  | blocked_raw_package_not_received |
| 3 | MWI_2007-2009_MTM_v01_M | oop_health_expenditure | 2 |  | blocked_raw_package_not_received |
| 3 | MWI_2007-2009_MTM_v01_M | illness_need_care_access | 5 |  | blocked_raw_package_not_received |
| 3 | MWI_2007-2009_MTM_v01_M | survey_timing | 2 |  | blocked_raw_package_not_received |
| 3 | MWI_2007-2009_MTM_v01_M | geography_climate_linkage | 2 |  | blocked_raw_package_not_received |
| 3 | MWI_2007-2009_MTM_v01_M | missing_skip_units_recall | 16 |  | blocked_raw_package_not_received |
| 4 | NGA_2012_GHSP-W2_v02_M | household_person_merge_keys | 3 |  | blocked_raw_package_not_received |
| 4 | NGA_2012_GHSP-W2_v02_M | weights_and_survey_design | 5 |  | blocked_raw_package_not_received |
| 4 | NGA_2012_GHSP-W2_v02_M | consumption_or_income_aggregate | 1 |  | blocked_raw_package_not_received |
| 4 | NGA_2012_GHSP-W2_v02_M | oop_health_expenditure | 2 |  | blocked_raw_package_not_received |
| 4 | NGA_2012_GHSP-W2_v02_M | illness_need_care_access | 6 |  | blocked_raw_package_not_received |
| 4 | NGA_2012_GHSP-W2_v02_M | survey_timing | 1 |  | blocked_raw_package_not_received |

## Selected Variable Preview

| acquisition_batch_rank | idno | requirement_id | concept | candidate_files | candidate_raw_variable | metadata_confidence | first_pass_review_status |
|---|---|---|---|---|---|---|---|
| 1 | ETH_2021_ESPS-W5_v02_M | household_person_merge_keys | household_id | eth_householdgeovariables_y5.dta;eth_plotgeovariables_y5.dta | household_id | high | blocked_raw_package_not_received |
| 1 | ETH_2021_ESPS-W5_v02_M | household_person_merge_keys | household_id | sect10_ph_w5.dta;sect10a_hh_w5.dta;sect11_hh_w5.dta;sect11_ph_w5.dta;sect12a_hh_w5.dta;sect12b1_hh_w5.dta;sect12b2_hh... | saq08 | high | blocked_raw_package_not_received |
| 1 | ETH_2021_ESPS-W5_v02_M | household_person_merge_keys | demographics | cons_agg_w5.dta | educ_cons_ann | high | blocked_raw_package_not_received |
| 1 | ETH_2021_ESPS-W5_v02_M | household_person_merge_keys | demographics | cons_agg_w5.dta | hh_size | high | blocked_raw_package_not_received |
| 1 | ETH_2021_ESPS-W5_v02_M | weights_and_survey_design | survey_weight | cons_agg_w5.dta;sect10_ph_w5.dta;sect10a_hh_w5.dta;sect11_hh_w5.dta;sect11_ph_w5.dta;sect12a_hh_w5.dta;sect12b1_hh_w5... | pw_w5 | high | blocked_raw_package_not_received |
| 1 | ETH_2021_ESPS-W5_v02_M | weights_and_survey_design | survey_weight | sect10b_com_w5.dta | cs10bq04 | high | blocked_raw_package_not_received |
| 1 | ETH_2021_ESPS-W5_v02_M | weights_and_survey_design | psu_cluster | cons_agg_w5.dta;sect01a_com_w5.dta;sect01b_com_w5.dta;sect02_com_w5.dta;sect03_com_w5.dta;sect04_com_w5.dta;sect05_co... | ea_id | high | blocked_raw_package_not_received |
| 1 | ETH_2021_ESPS-W5_v02_M | weights_and_survey_design | psu_cluster | eth_householdgeovariables_y5.dta;eth_plotgeovariables_y5.dta | pct_urban_cluster | high | blocked_raw_package_not_received |
| 1 | ETH_2021_ESPS-W5_v02_M | weights_and_survey_design | strata | sect8_3_ls_w5.dta | ls_s8_3q01 | high | blocked_raw_package_not_received |
| 1 | ETH_2021_ESPS-W5_v02_M | weights_and_survey_design | strata | sect8_3_ls_w5.dta | ls_s8_3q02 | high | blocked_raw_package_not_received |
| 1 | ETH_2021_ESPS-W5_v02_M | consumption_or_income_aggregate | total_consumption_or_income | sect8_2_ls_w5.dta | ls_s8_2q14 | high | blocked_raw_package_not_received |
| 1 | ETH_2021_ESPS-W5_v02_M | consumption_or_income_aggregate | total_consumption_or_income | sect8_2_ls_w5.dta | ls_s8_2q18 | high | blocked_raw_package_not_received |
| 1 | ETH_2021_ESPS-W5_v02_M | oop_health_expenditure | oop_health_expenditure | sect3_hh_w5.dta;sect3_pp_w5.dta | s3q18 | high | blocked_raw_package_not_received |
| 1 | ETH_2021_ESPS-W5_v02_M | oop_health_expenditure | oop_health_expenditure | sect8_3_ls_w5.dta | ls_s8_3q04 | moderate | blocked_raw_package_not_received |
| 1 | ETH_2021_ESPS-W5_v02_M | illness_need_care_access | health_need | sect3_hh_w5.dta | s3q05 | high | blocked_raw_package_not_received |
| 1 | ETH_2021_ESPS-W5_v02_M | illness_need_care_access | health_need | sect3_hh_w5.dta | s3q06_1 | high | blocked_raw_package_not_received |
| 1 | ETH_2021_ESPS-W5_v02_M | illness_need_care_access | care_or_barrier | sect04_com_w5.dta | cs4q28 | high | blocked_raw_package_not_received |
| 1 | ETH_2021_ESPS-W5_v02_M | illness_need_care_access | care_or_barrier | sect04_com_w5.dta | cs4q30 | high | blocked_raw_package_not_received |
| 1 | ETH_2021_ESPS-W5_v02_M | illness_need_care_access | insurance | sect3_hh_w5.dta | s3q19 | high | blocked_raw_package_not_received |
| 1 | ETH_2021_ESPS-W5_v02_M | survey_timing | survey_timing | sect_cover_ls_w5.dta;sect_cover_ph_w5.dta;sect_cover_pp_w5.dta | InterviewDate | high | blocked_raw_package_not_received |
| 1 | ETH_2021_ESPS-W5_v02_M | geography_climate_linkage | climate_geography | cons_agg_w5.dta;sect01a_com_w5.dta;sect01b_com_w5.dta;sect02_com_w5.dta;sect03_com_w5.dta;sect04_com_w5.dta;sect05_co... | saq01 | high | blocked_raw_package_not_received |
| 1 | ETH_2021_ESPS-W5_v02_M | geography_climate_linkage | climate_geography | eth_householdgeovariables_y5.dta;eth_plotgeovariables_y5.dta | cropshare | high | blocked_raw_package_not_received |
| 1 | ETH_2021_ESPS-W5_v02_M | missing_skip_units_recall | household_id | eth_householdgeovariables_y5.dta;eth_plotgeovariables_y5.dta | household_id | high | blocked_raw_package_not_received |
| 1 | ETH_2021_ESPS-W5_v02_M | missing_skip_units_recall | household_id | sect10_ph_w5.dta;sect10a_hh_w5.dta;sect11_hh_w5.dta;sect11_ph_w5.dta;sect12a_hh_w5.dta;sect12b1_hh_w5.dta;sect12b2_hh... | saq08 | high | blocked_raw_package_not_received |
| 1 | ETH_2021_ESPS-W5_v02_M | missing_skip_units_recall | survey_weight | cons_agg_w5.dta;sect10_ph_w5.dta;sect10a_hh_w5.dta;sect11_hh_w5.dta;sect11_ph_w5.dta;sect12a_hh_w5.dta;sect12b1_hh_w5... | pw_w5 | high | blocked_raw_package_not_received |
| 1 | ETH_2021_ESPS-W5_v02_M | missing_skip_units_recall | survey_weight | sect10b_com_w5.dta | cs10bq04 | high | blocked_raw_package_not_received |
| 1 | ETH_2021_ESPS-W5_v02_M | missing_skip_units_recall | total_consumption_or_income | sect8_2_ls_w5.dta | ls_s8_2q14 | high | blocked_raw_package_not_received |
| 1 | ETH_2021_ESPS-W5_v02_M | missing_skip_units_recall | total_consumption_or_income | sect8_2_ls_w5.dta | ls_s8_2q18 | high | blocked_raw_package_not_received |
| 1 | ETH_2021_ESPS-W5_v02_M | missing_skip_units_recall | oop_health_expenditure | sect3_hh_w5.dta;sect3_pp_w5.dta | s3q18 | high | blocked_raw_package_not_received |
| 1 | ETH_2021_ESPS-W5_v02_M | missing_skip_units_recall | oop_health_expenditure | sect8_3_ls_w5.dta | ls_s8_3q04 | moderate | blocked_raw_package_not_received |
| 1 | ETH_2021_ESPS-W5_v02_M | missing_skip_units_recall | health_need | sect3_hh_w5.dta | s3q05 | high | blocked_raw_package_not_received |
| 1 | ETH_2021_ESPS-W5_v02_M | missing_skip_units_recall | health_need | sect3_hh_w5.dta | s3q06_1 | high | blocked_raw_package_not_received |
| 1 | ETH_2021_ESPS-W5_v02_M | missing_skip_units_recall | care_or_barrier | sect04_com_w5.dta | cs4q28 | high | blocked_raw_package_not_received |
| 1 | ETH_2021_ESPS-W5_v02_M | missing_skip_units_recall | care_or_barrier | sect04_com_w5.dta | cs4q30 | high | blocked_raw_package_not_received |
| 1 | ETH_2021_ESPS-W5_v02_M | missing_skip_units_recall | survey_timing | sect_cover_ls_w5.dta;sect_cover_ph_w5.dta;sect_cover_pp_w5.dta | InterviewDate | high | blocked_raw_package_not_received |
| 1 | ETH_2021_ESPS-W5_v02_M | missing_skip_units_recall | climate_geography | cons_agg_w5.dta;sect01a_com_w5.dta;sect01b_com_w5.dta;sect02_com_w5.dta;sect03_com_w5.dta;sect04_com_w5.dta;sect05_co... | saq01 | high | blocked_raw_package_not_received |
| 1 | ETH_2021_ESPS-W5_v02_M | missing_skip_units_recall | climate_geography | eth_householdgeovariables_y5.dta;eth_plotgeovariables_y5.dta | cropshare | high | blocked_raw_package_not_received |
| 2 | ETH_2018_ESS_v04_M | household_person_merge_keys | household_id | ETH_HouseholdGeovariables_Y4.dta;ETH_PlotGeovariables_Y4.dta | household_id | high | blocked_raw_package_not_received |
| 2 | ETH_2018_ESS_v04_M | household_person_merge_keys | household_id | sect10_ph_w4.dta;sect10a_hh_w4.dta;sect10b_hh_w4.dta;sect10c_hh_w4.dta;sect10d1_hh_w4.dta;sect10d2_hh_w4.dta;sect11_h... | saq08 | high | blocked_raw_package_not_received |
| 2 | ETH_2018_ESS_v04_M | household_person_merge_keys | demographics | cons_agg_w4.dta | educ_cons_ann | high | blocked_raw_package_not_received |

## Use

1. Download the complete original raw package and documentation into each
   target folder.
2. Use this queue to inspect the first-pass variables for labels, raw values,
   missing and skip codes, units, recall periods, merge level, and denominator
   semantics.
3. Fill the existing requirement, concept, and variable verification templates.
4. Rerun `python script/129_build_priority_manual_verification_decision_gate.py`,
   `python script/132_build_priority_analysis_dataset_synthesis_blueprint.py`,
   `python script/134_build_priority_country_wave_promotion_packets.py`, and
   `python script/127_enforce_promoted_data_gate.py`.

## Machine-Readable Outputs

- `temp/priority_first_pass_variable_review_queue.csv`
- `temp/priority_first_pass_requirement_coverage.csv`
- `result/priority_first_pass_variable_review_summary.csv`
