# Country-Wave Promotion Packet: Albania 2005

Dataset: `Living Standards Measurement Survey 2005`

IDNO: `ALB_2005_LSMS_v01_M`

Official URL: https://microdata.worldbank.org/catalog/64/get-microdata

Local target folder: `temp/raw_downloads/ALB_2005_LSMS_v01_M/`

Current registry status: `not_promoted`

## Gate Summary

| Gate | Status | Evidence | Required action |
|---|---|---|---|
| complete_original_raw_package | pass | intake_status=ready_for_raw_schema_inspection; tabular=0; archives=1; docs=1 |  |
| raw_value_unit_recall_missing_verification | fail | raw_not_inspected=96 | Inspect raw labels/values, merge keys, units, recall periods, skip patterns, and missing codes. |
| financial_protection_che10_che25 | fail | climate_geography:raw_variables_inspected; household_id:raw_variables_inspected; oop_health_expenditure:raw_variables_inspected; survey_timing:raw_variables_inspected; survey_weight:raw_variables_inspected; total_consumption_or_income:raw_variables_inspected | Verify total consumption/income, OOP health expenditure, weights, timing, geography, and merge keys. |
| access_forgone_care | fail | care_or_barrier:raw_variables_inspected; health_need:raw_variables_inspected | Verify illness/need denominator, care seeking, and cost/distance/supply barrier semantics. |
| climate_linkage | fail | survey_timing:raw_variables_inspected; climate_geography:raw_variables_inspected | Verify survey month/date, usable admin/GPS/cluster geography, and accepted CHIRPS/ERA5 extraction route. |
| double_failure | fail | financial_ready=0; access_ready=0 | Pass both financial-protection and access/forgone-care value verification gates. |

## Expected Files or Modules

- `community_all`: archive_present_needs_schema_extraction; concepts=admin1_or_admin2;age;agriculture_livelihood;asset_index_or_asset_variable;care_not_sought_reason;coping_borrowed;education;interview_date_or_survey_month;pid;psu_or_cluster_id;reason_not_sought_distance;rural;sex
- `community_dups`: archive_present_needs_schema_extraction; concepts=admin1_or_admin2;age;agriculture_livelihood;asset_index_or_asset_variable;care_not_sought_reason;coping_borrowed;education;interview_date_or_survey_month;pid;psu_or_cluster_id;reason_not_sought_distance;rural;sex
- `agriculture_hhlevel`: archive_present_needs_schema_extraction; concepts=admin1_or_admin2;agriculture_livelihood;asset_index_or_asset_variable;coping_borrowed;hhid;household_weight_or_person_weight;psu_or_cluster_id;reason_not_sought_cost;reason_not_sought_distance;rural;strata
- `healthA_cl`: archive_present_needs_schema_extraction; concepts=age;hhid;illness_or_injury_need;oop_health_expenditure;psu_or_cluster_id;reason_not_sought_distance;shock_module_variable
- `dwellingA_cl`: archive_present_needs_schema_extraction; concepts=asset_index_or_asset_variable;hhid;psu_or_cluster_id;reason_not_sought_cost;reason_not_sought_distance;shock_module_variable
- `dwellingB_cl`: archive_present_needs_schema_extraction; concepts=asset_index_or_asset_variable;care_not_sought_reason;hhid;psu_or_cluster_id;reason_not_sought_distance;shock_module_variable
- `poverty`: archive_present_needs_schema_extraction; concepts=admin1_or_admin2;asset_index_or_asset_variable;education;food_consumption;hhid;household_size;household_weight_or_person_weight;nonfood_consumption;psu_or_cluster_id;rural;strata;total_consumption_or_income
- `educationB_cl`: archive_present_needs_schema_extraction; concepts=age;asset_index_or_asset_variable;care_not_sought_reason;education;hhid;psu_or_cluster_id;reason_not_sought_distance
- `fertility_cl`: archive_present_needs_schema_extraction; concepts=age;care_not_sought_reason;care_sought;hhid;household_weight_or_person_weight;pid;psu_or_cluster_id
- `household_rosterA_cl`: archive_present_needs_schema_extraction; concepts=age;education;hhid;psu_or_cluster_id;sex
- `migrationA_cl`: archive_present_needs_schema_extraction; concepts=admin1_or_admin2;hhid;psu_or_cluster_id
- `migrationC_cl`: archive_present_needs_schema_extraction; concepts=admin1_or_admin2;age;education;hhid;pid;psu_or_cluster_id;sex

## Raw Variable Verification Queue

- `dwellingA_cl` / `m13a_q13b`: care_or_barrier; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `healthB_cl` / `m9b_q05`: care_or_barrier; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `healthB_cl` / `m9b_q06`: care_or_barrier; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `agriculture_hhlevel` / `distcode`: climate_geography; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `community_all;community_dups` / `m001a`: climate_geography; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `filters` / `p11_q5b`: climate_geography; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `identification` / `p0_q5b`: climate_geography; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `identification_cl` / `m0_q1a`: climate_geography; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `migrationA_cl` / `m6a_q03`: climate_geography; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `migrationA_cl` / `m6a_q09`: climate_geography; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `migrationA_cl` / `m6a_q15`: climate_geography; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `migrationA_cl` / `m6a_q20`: climate_geography; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `migrationA_cl` / `m6a_q24`: climate_geography; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `migrationC_cl` / `m6c_q47`: climate_geography; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `part1_roster_a` / `p1a_q05`: climate_geography; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `part1_roster_b` / `p1b_q05`: climate_geography; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization

## Promotion Rule

Do not write this country-wave into `data/` until the raw package is complete,
merge keys and survey design are verified, financial-protection and access
variables pass value/unit/recall/missing-code checks, and a CHIRPS or ERA5
climate-linkage route is accepted.
