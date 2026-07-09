# Country-Wave Promotion Packet: Nigeria 2010-2011

Dataset: `General Household Survey, Panel 2010-2011, Wave 1`

IDNO: `NGA_2010_GHSP-W1_v03_M`

Official URL: https://microdata.worldbank.org/catalog/1002/get-microdata

Local target folder: `temp/raw_downloads/NGA_2010_GHSP-W1_v03_M/`

Current registry status: `not_promoted`

## Gate Summary

| Gate | Status | Evidence | Required action |
|---|---|---|---|
| complete_original_raw_package | fail | intake_status=instructions_or_documentation_only; tabular=0; archives=0; docs=1 | Place complete original raw archive/tabular package and documentation in the local target folder. |
| raw_value_unit_recall_missing_verification | fail | raw_not_inspected=67 | Inspect raw labels/values, merge keys, units, recall periods, skip patterns, and missing codes. |
| financial_protection_che10_che25 | fail | climate_geography:raw_not_inspected; household_id:raw_not_inspected; oop_health_expenditure:raw_not_inspected; survey_timing:raw_not_inspected; survey_weight:raw_not_inspected; total_consumption_or_income:raw_not_inspected | Verify total consumption/income, OOP health expenditure, weights, timing, geography, and merge keys. |
| access_forgone_care | fail | care_or_barrier:raw_not_inspected; health_need:raw_not_inspected | Verify illness/need denominator, care seeking, and cost/distance/supply barrier semantics. |
| climate_linkage | fail | survey_timing:raw_not_inspected; climate_geography:raw_not_inspected | Verify survey month/date, usable admin/GPS/cluster geography, and accepted CHIRPS/ERA5 extraction route. |
| double_failure | fail | financial_ready=0; access_ready=0 | Pass both financial-protection and access/forgone-care value verification gates. |

## Expected Files or Modules

- `secta1_harvestw1`: not_present; concepts=admin1_or_admin2;agriculture_livelihood;hhid;latitude_or_longitude;psu_or_cluster_id
- `sect11h_plantingw1`: not_present; concepts=admin1_or_admin2;agriculture_livelihood;coping_borrowed;hhid;psu_or_cluster_id;reason_not_sought_distance
- `sect11c_plantingw1`: not_present; concepts=admin1_or_admin2;agriculture_livelihood;hhid;psu_or_cluster_id
- `sect11b_plantingw1`: not_present; concepts=admin1_or_admin2;agriculture_livelihood;hhid;pid;psu_or_cluster_id
- `secta3_harvestw1`: not_present; concepts=admin1_or_admin2;agriculture_livelihood;care_not_sought_reason;hhid;psu_or_cluster_id
- `sect11e_plantingw1`: not_present; concepts=admin1_or_admin2;agriculture_livelihood;coping_borrowed;hhid;psu_or_cluster_id;reason_not_sought_distance
- `sect4a_harvestw1`: not_present; concepts=admin1_or_admin2;care_sought;education;hhid;household_weight_or_person_weight;illness_or_injury_need;oop_health_expenditure;psu_or_cluster_id;reason_not_sought_distance;sex
- `sect8_harvestw1`: not_present; concepts=admin1_or_admin2;asset_index_or_asset_variable;hhid;psu_or_cluster_id
- `secta2_harvestw1`: not_present; concepts=admin1_or_admin2;agriculture_livelihood;hhid;psu_or_cluster_id
- `sect11d_plantingw1`: not_present; concepts=admin1_or_admin2;agriculture_livelihood;coping_borrowed;hhid;psu_or_cluster_id;reason_not_sought_distance
- `NGA_HouseholdGeovariables_Y1`: not_present; concepts=admin1_or_admin2;agriculture_livelihood;hhid;latitude_or_longitude;psu_or_cluster_id;reason_not_sought_distance;shock_module_variable
- `sect1_harvestw1`: not_present; concepts=admin1_or_admin2;age;education;hhid;psu_or_cluster_id;reason_not_sought_distance;sex

## Raw Variable Verification Queue

- `sect4a_harvestw1` / `s4aq15`: care_or_barrier; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `sect4a_harvestw1` / `s4aq16`: care_or_barrier; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `sect4a_harvestw1` / `s4aq17`: care_or_barrier; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `sect4a_harvestw1` / `s4aq20`: care_or_barrier; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `sect4a_harvestw1` / `s4aq20b`: care_or_barrier; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `NGA_HouseholdGeovariables_Y1` / `lat_dd_mod`: climate_geography; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `NGA_HouseholdGeovariables_Y1` / `lon_dd_mod`: climate_geography; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `sect11a1_plantingw1` / `s11aq4d`: climate_geography; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `secta1_harvestw1` / `sa1q9d`: climate_geography; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `cons_agg_wave1_visit1;cons_agg_wave1_visit2` / `edtexp`: demographics; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `cons_agg_wave1_visit1;cons_agg_wave1_visit2` / `nfdinsur`: demographics; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `sect12_harvestw1` / `s12q1d`: demographics; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `sect12_harvestw1` / `s12q4a`: demographics; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `sect12_harvestw1` / `s12q4b`: demographics; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `sect15b_harvestw1` / `s15bq3`: demographics; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `sect15b_harvestw1` / `s15bq4`: demographics; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization

## Promotion Rule

Do not write this country-wave into `data/` until the raw package is complete,
merge keys and survey design are verified, financial-protection and access
variables pass value/unit/recall/missing-code checks, and a CHIRPS or ERA5
climate-linkage route is accepted.
