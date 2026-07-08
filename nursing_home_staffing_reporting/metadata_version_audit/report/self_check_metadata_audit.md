# Self-Check Metadata Audit

Result: PASS

- Passed checks: 33
- Failed checks: 0

| Check | Status | Requirement | Detail |
|---|---:|---|---|
| exists_time_period_policy_variable_map.csv | PASS | all required CSV tables exist | D:\GlobalHealthPolicy Dropbox\Fan Bowei\health_econ\nursing_home_staffing_reporting\metadata_version_audit\result\tables\time_period_policy_variable_map.csv |
| columns_time_period_policy_variable_map.csv | PASS | all required columns are present |  |
| source_evidence_time_period_policy_variable_map.csv | PASS | every row has source evidence | empty_rows=0 |
| exists_raw_pbj_daily_codebook_by_period.csv | PASS | all required CSV tables exist | D:\GlobalHealthPolicy Dropbox\Fan Bowei\health_econ\nursing_home_staffing_reporting\metadata_version_audit\result\tables\raw_pbj_daily_codebook_by_period.csv |
| columns_raw_pbj_daily_codebook_by_period.csv | PASS | all required columns are present |  |
| source_evidence_raw_pbj_daily_codebook_by_period.csv | PASS | every row has source evidence | empty_rows=0 |
| exists_pbj_employee_detail_codebook_by_period.csv | PASS | all required CSV tables exist | D:\GlobalHealthPolicy Dropbox\Fan Bowei\health_econ\nursing_home_staffing_reporting\metadata_version_audit\result\tables\pbj_employee_detail_codebook_by_period.csv |
| columns_pbj_employee_detail_codebook_by_period.csv | PASS | all required columns are present |  |
| source_evidence_pbj_employee_detail_codebook_by_period.csv | PASS | every row has source evidence | empty_rows=0 |
| exists_provider_catalog_codebook_by_snapshot.csv | PASS | all required CSV tables exist | D:\GlobalHealthPolicy Dropbox\Fan Bowei\health_econ\nursing_home_staffing_reporting\metadata_version_audit\result\tables\provider_catalog_codebook_by_snapshot.csv |
| columns_provider_catalog_codebook_by_snapshot.csv | PASS | all required columns are present |  |
| source_evidence_provider_catalog_codebook_by_snapshot.csv | PASS | every row has source evidence | empty_rows=0 |
| exists_six_measure_rating_component_crosswalk.csv | PASS | all required CSV tables exist | D:\GlobalHealthPolicy Dropbox\Fan Bowei\health_econ\nursing_home_staffing_reporting\metadata_version_audit\result\tables\six_measure_rating_component_crosswalk.csv |
| columns_six_measure_rating_component_crosswalk.csv | PASS | all required columns are present |  |
| source_evidence_six_measure_rating_component_crosswalk.csv | PASS | every row has source evidence | empty_rows=0 |
| exists_constructed_variables_codebook.csv | PASS | all required CSV tables exist | D:\GlobalHealthPolicy Dropbox\Fan Bowei\health_econ\nursing_home_staffing_reporting\metadata_version_audit\result\tables\constructed_variables_codebook.csv |
| columns_constructed_variables_codebook.csv | PASS | all required columns are present |  |
| source_evidence_constructed_variables_codebook.csv | PASS | every row has source evidence | empty_rows=0 |
| exists_running_variable_audit.csv | PASS | all required CSV tables exist | D:\GlobalHealthPolicy Dropbox\Fan Bowei\health_econ\nursing_home_staffing_reporting\metadata_version_audit\result\tables\running_variable_audit.csv |
| columns_running_variable_audit.csv | PASS | all required columns are present |  |
| source_evidence_running_variable_audit.csv | PASS | every row has source evidence | empty_rows=0 |
| exists_outcome_family_codebook.csv | PASS | all required CSV tables exist | D:\GlobalHealthPolicy Dropbox\Fan Bowei\health_econ\nursing_home_staffing_reporting\metadata_version_audit\result\tables\outcome_family_codebook.csv |
| columns_outcome_family_codebook.csv | PASS | all required columns are present |  |
| source_evidence_outcome_family_codebook.csv | PASS | every row has source evidence | empty_rows=0 |
| constructed_not_raw_official | PASS | no constructed variable is listed as a raw official field | bad_rows=0 |
| jan2022_not_first_pbj_daily_existence | PASS | January 2022 is not described as first existence of PBJ daily staffing data | 2022_01_07_to_2022_01_25 2022-01-07 to 2022-01-25 qso announcement period; providers are informed that weekend staffing, turnover, and employee-level data will be public and later rating-relevant. announcement and antici |
| jan_to_july_not_clean_pre | PASS | January-July 2022 is not described as clean untreated pre-period | 2022_01_26_to_2022_07_26 2022-01-26 to 2022-07-26 transparency and employee-level data-release transition period before formal july staffing rating algorithm change. weekend staffing and turnover are public on care compa |
| july_adjusted_weekend_not_falsely_direct | PASS | July 2022 adjusted weekend total nurse HPRD is not falsely described as directly available if absent | july_field=absent; reported field available: total number of nurse staff hours per resident per day on the weekend; direct=reconstructed for july 2022; direct official field in october 2022 and january 2023 |
| official_0_380_not_direct_observed | PASS | official 0-380 score is not falsely described as directly observed | official_facility_level_staffing_score_0_380 official field searched, not found no direct field found in providerinfo headers, data dictionaries, or score-field scan.  155, 205, 255, 320 five-star technical users' guide  |
| final_report_exists | PASS | final report exists | D:\GlobalHealthPolicy Dropbox\Fan Bowei\health_econ\nursing_home_staffing_reporting\metadata_version_audit\report\final_time_versioned_codebook.md |
| report_separates_variable_types | PASS | final report clearly separates raw variables, official measures, reconstructed variables, and outcomes | variable-type terms checked |
| report_jan2022_not_first_data | PASS | final report states January 2022 is not first existence of PBJ daily data | phrase checked |
| report_jan_july_transition | PASS | final report states January-July 2022 is transition, not clean pre-period | phrase checked |
