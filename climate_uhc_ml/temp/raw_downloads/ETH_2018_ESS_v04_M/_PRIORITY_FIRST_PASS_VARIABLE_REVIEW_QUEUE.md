# Priority First-Pass Variable Review Queue

Dataset: `ETH_2018_ESS_v04_M` - Ethiopia 2018-2019

Campaign phase: phase_1_double_failure_10_wave_base

Threshold role: required_for_10_country_wave_double_failure_threshold

Current raw receipt: not_received_no_original_raw_package

This is a compact first-pass queue for post-download raw-value review. It does
not verify raw values, does not promote any dataset, and does not write to
`data/`.

## Selected Variables

| requirement_id | concept | candidate_files | candidate_raw_variable | metadata_confidence | first_pass_review_status |
|---|---|---|---|---|---|
| household_person_merge_keys | household_id | ETH_HouseholdGeovariables_Y4.dta;ETH_PlotGeovariables_Y4.dta | household_id | high | blocked_raw_package_not_received |
| household_person_merge_keys | household_id | sect10_ph_w4.dta;sect10a_hh_w4.dta;sect10b_hh_w4.dta;sect10c_hh_w4.dta;sect10d1_hh_w4.dta;sect10d2_hh_w4.dta;sect11_h... | saq08 | high | blocked_raw_package_not_received |
| household_person_merge_keys | demographics | cons_agg_w4.dta | educ_cons_ann | high | blocked_raw_package_not_received |
| household_person_merge_keys | demographics | cons_agg_w4.dta | hh_size | high | blocked_raw_package_not_received |
| weights_and_survey_design | survey_weight | cons_agg_w4.dta;sect10_ph_w4.dta;sect10a_hh_w4.dta;sect10b_hh_w4.dta;sect10c_hh_w4.dta;sect10d1_hh_w4.dta;sect10d2_hh... | pw_w4 | high | blocked_raw_package_not_received |
| weights_and_survey_design | survey_weight | sect10b_com_w4.dta | cs10bq04 | high | blocked_raw_package_not_received |
| weights_and_survey_design | psu_cluster | ETH_HouseholdGeovariables_Y4.dta;cons_agg_w4.dta;sect01a_com_w4.dta;sect01b_com_w4.dta;sect02_com_w4.dta;sect03_com_w... | ea_id | high | blocked_raw_package_not_received |
| weights_and_survey_design | psu_cluster | sect01a_com_w4.dta;sect01b_com_w4.dta;sect02_com_w4.dta;sect03_com_w4.dta;sect04_com_w4.dta;sect05_com_w4.dta;sect06_... | saq07 | high | blocked_raw_package_not_received |
| weights_and_survey_design | strata | sect8_3_ls_w4.dta | ls_s8_3q01 | high | blocked_raw_package_not_received |
| weights_and_survey_design | strata | sect8_3_ls_w4.dta | ls_s8_3q02 | high | blocked_raw_package_not_received |
| consumption_or_income_aggregate | total_consumption_or_income | sect8_2_ls_w4.dta | ls_s8_2q14 | high | blocked_raw_package_not_received |
| consumption_or_income_aggregate | total_consumption_or_income | sect8_2_ls_w4.dta | ls_s8_2q18 | high | blocked_raw_package_not_received |
| oop_health_expenditure | oop_health_expenditure | sect3_hh_w4.dta;sect3_pp_w4.dta | s3q18 | high | blocked_raw_package_not_received |
| oop_health_expenditure | oop_health_expenditure | sect8_3_ls_w4.dta | ls_s8_3q04 | moderate | blocked_raw_package_not_received |
| illness_need_care_access | health_need | sect3_hh_w4.dta | s3q05 | high | blocked_raw_package_not_received |
| illness_need_care_access | health_need | sect3_hh_w4.dta | s3q06_1 | high | blocked_raw_package_not_received |
| illness_need_care_access | care_or_barrier | sect04_com_w4.dta | cs4q28 | high | blocked_raw_package_not_received |
| illness_need_care_access | care_or_barrier | sect04_com_w4.dta | cs4q30 | high | blocked_raw_package_not_received |
| illness_need_care_access | insurance | sect3_hh_w4.dta | s3q19 | high | blocked_raw_package_not_received |
| survey_timing | survey_timing | sect_cover_hh_w4.dta | InterviewStart | high | blocked_raw_package_not_received |
| survey_timing | survey_timing | sect_cover_ls_w4.dta;sect_cover_ph_w4.dta;sect_cover_pp_w4.dta | InterviewDate | high | blocked_raw_package_not_received |
| geography_climate_linkage | climate_geography | ETH_HouseholdGeovariables_Y4.dta | dist_admhq | high | blocked_raw_package_not_received |
| geography_climate_linkage | climate_geography | ETH_HouseholdGeovariables_Y4.dta | lat_mod | high | blocked_raw_package_not_received |
| missing_skip_units_recall | household_id | ETH_HouseholdGeovariables_Y4.dta;ETH_PlotGeovariables_Y4.dta | household_id | high | blocked_raw_package_not_received |
| missing_skip_units_recall | household_id | sect10_ph_w4.dta;sect10a_hh_w4.dta;sect10b_hh_w4.dta;sect10c_hh_w4.dta;sect10d1_hh_w4.dta;sect10d2_hh_w4.dta;sect11_h... | saq08 | high | blocked_raw_package_not_received |
| missing_skip_units_recall | survey_weight | cons_agg_w4.dta;sect10_ph_w4.dta;sect10a_hh_w4.dta;sect10b_hh_w4.dta;sect10c_hh_w4.dta;sect10d1_hh_w4.dta;sect10d2_hh... | pw_w4 | high | blocked_raw_package_not_received |
| missing_skip_units_recall | survey_weight | sect10b_com_w4.dta | cs10bq04 | high | blocked_raw_package_not_received |
| missing_skip_units_recall | total_consumption_or_income | sect8_2_ls_w4.dta | ls_s8_2q14 | high | blocked_raw_package_not_received |
| missing_skip_units_recall | total_consumption_or_income | sect8_2_ls_w4.dta | ls_s8_2q18 | high | blocked_raw_package_not_received |
| missing_skip_units_recall | oop_health_expenditure | sect3_hh_w4.dta;sect3_pp_w4.dta | s3q18 | high | blocked_raw_package_not_received |
| missing_skip_units_recall | oop_health_expenditure | sect8_3_ls_w4.dta | ls_s8_3q04 | moderate | blocked_raw_package_not_received |
| missing_skip_units_recall | health_need | sect3_hh_w4.dta | s3q05 | high | blocked_raw_package_not_received |
| missing_skip_units_recall | health_need | sect3_hh_w4.dta | s3q06_1 | high | blocked_raw_package_not_received |
| missing_skip_units_recall | care_or_barrier | sect04_com_w4.dta | cs4q28 | high | blocked_raw_package_not_received |
| missing_skip_units_recall | care_or_barrier | sect04_com_w4.dta | cs4q30 | high | blocked_raw_package_not_received |
| missing_skip_units_recall | survey_timing | sect_cover_hh_w4.dta | InterviewStart | high | blocked_raw_package_not_received |
| missing_skip_units_recall | survey_timing | sect_cover_ls_w4.dta;sect_cover_ph_w4.dta;sect_cover_pp_w4.dta | InterviewDate | high | blocked_raw_package_not_received |
| missing_skip_units_recall | climate_geography | ETH_HouseholdGeovariables_Y4.dta | dist_admhq | high | blocked_raw_package_not_received |
| missing_skip_units_recall | climate_geography | ETH_HouseholdGeovariables_Y4.dta | lat_mod | high | blocked_raw_package_not_received |

## Post-Download Rule

Use the queue only after the complete original raw package and documentation
are present. For each selected variable, inspect labels, raw values, missing and
skip codes, units, recall periods, merge level, and denominator semantics.
Then fill:

- `temp/priority_promotion_verification_checklist.csv`
- `temp/priority_concept_verification_template.csv`
- `temp/priority_variable_verification_template.csv`

Do not promote this wave until the manual verification decision gate, synthesis
blueprint, country-wave packet, promoted-data gate, and accepted CHIRPS/ERA5
linkage all pass.
