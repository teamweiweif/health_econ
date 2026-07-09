# Priority Analysis Dataset Synthesis Blueprint

Dataset: NPL_2010_LSS-III_v01_M - Nepal 2010-2011

Join plan status: blocked_required_schema_columns_not_verified

Current synthesis evidence:

- Required schema columns: 25
- Synthesis-ready columns: 0
- Blocked columns: 22
- Base household key: blocked_raw_package_absent
- Financial inputs: blocked
- Access inputs: blocked
- Climate route: blocked_raw_timing_geography_not_verified_sources_ready

Blocked column examples:

- household_id: blocked_raw_package_absent (complete original raw package absent)
- survey_weight: blocked_raw_package_absent (complete original raw package absent)
- psu_cluster: blocked_raw_package_absent (complete original raw package absent)
- survey_year: blocked_raw_package_absent (complete original raw package absent)
- survey_month: blocked_raw_package_absent (complete original raw package absent)
- cluster_id: blocked_raw_package_absent (complete original raw package absent)
- geolocation_quality: blocked_raw_package_absent (complete original raw package absent)
- total_consumption: blocked_raw_package_absent (complete original raw package absent)
- oop_health_expenditure: blocked_raw_package_absent (complete original raw package absent)
- che10: blocked_raw_package_absent (complete original raw package absent)
- che25: blocked_raw_package_absent (complete original raw package absent)
- sdg382_indicator: blocked_raw_package_absent (complete original raw package absent)
- illness_or_injury_need: blocked_raw_package_absent (complete original raw package absent)
- care_sought: blocked_raw_package_absent (complete original raw package absent)
- forgone_care_access_failure: blocked_raw_package_absent (complete original raw package absent)
- double_failure_indicator: blocked_raw_package_absent (complete original raw package absent)
- climate_source: blocked_raw_package_absent (complete original raw package absent)
- climate_window_start: blocked_raw_package_absent (complete original raw package absent)
- climate_window_end: blocked_raw_package_absent (complete original raw package absent)
- chirps_precip_anomaly: blocked_raw_package_absent (complete original raw package absent)
- era5_heat_anomaly: blocked_raw_package_absent (complete original raw package absent)
- climate_shock_indicator: blocked_raw_package_absent (complete original raw package absent)

Next action: Complete raw package receipt and manual verification for blocked required schema columns before writing any promoted household-climate dataset.

Stop rule: do not write this wave into `data/` until all required schema columns are source-verified, outcome-ready, and climate-linkage-ready.
