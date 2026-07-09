# Country-Wave Promotion Packet: Tanzania 2010-2011

Dataset: `National Panel Survey 2010-2011, Wave 2`

IDNO: `TZA_2010_NPS-R2_v03_M`

Official URL: https://microdata.worldbank.org/catalog/1050/get-microdata

Local target folder: `temp/raw_downloads/TZA_2010_NPS-R2_v03_M/`

Current registry status: `not_promoted`

## Gate Summary

| Gate | Status | Evidence | Required action |
|---|---|---|---|
| complete_original_raw_package | fail | intake_status=instructions_or_documentation_only; tabular=0; archives=0; docs=1 | Place complete original raw archive/tabular package and documentation in the local target folder. |
| raw_value_unit_recall_missing_verification | fail | raw_not_inspected=91 | Inspect raw labels/values, merge keys, units, recall periods, skip patterns, and missing codes. |
| financial_protection_che10_che25 | fail | climate_geography:raw_not_inspected; household_id:raw_not_inspected; oop_health_expenditure:raw_not_inspected; survey_timing:raw_not_inspected; survey_weight:raw_not_inspected; total_consumption_or_income:raw_not_inspected | Verify total consumption/income, OOP health expenditure, weights, timing, geography, and merge keys. |
| access_forgone_care | fail | care_or_barrier:raw_not_inspected; health_need:raw_not_inspected | Verify illness/need denominator, care seeking, and cost/distance/supply barrier semantics. |
| climate_linkage | fail | survey_timing:raw_not_inspected; climate_geography:raw_not_inspected | Verify survey month/date, usable admin/GPS/cluster geography, and accepted CHIRPS/ERA5 extraction route. |
| double_failure | fail | financial_ready=0; access_ready=0 | Pass both financial-protection and access/forgone-care value verification gates. |

## Expected Files or Modules

- `AG_SEC3A`: not_present; concepts=agriculture_livelihood;care_not_sought_reason;coping_borrowed;reason_not_sought_distance;shock_module_variable;total_consumption_or_income
- `AG_SEC3B`: not_present; concepts=agriculture_livelihood;care_not_sought_reason;coping_borrowed;reason_not_sought_distance;shock_module_variable;total_consumption_or_income
- `HH.Geovariables_Y2`: not_present; concepts=admin1_or_admin2;agriculture_livelihood;latitude_or_longitude;psu_or_cluster_id;reason_not_sought_distance;shock_module_variable
- `TZY1.HH.Consumption`: not_present; concepts=admin1_or_admin2;education;hhid;household_size;household_weight_or_person_weight;interview_date_or_survey_month;psu_or_cluster_id;reason_not_sought_distance;rural;strata;total_consumption_or_income
- `HH_SEC_D`: not_present; concepts=age;care_sought;education;illness_or_injury_need;oop_health_expenditure;pid
- `TZY2.HH.Consumption`: not_present; concepts=admin1_or_admin2;education;hhid;household_size;household_weight_or_person_weight;interview_date_or_survey_month;reason_not_sought_distance;rural;strata;total_consumption_or_income
- `COMSEC_CD`: not_present; concepts=admin1_or_admin2;agriculture_livelihood;psu_or_cluster_id
- `COMSEC_CE`: not_present; concepts=admin1_or_admin2;agriculture_livelihood;psu_or_cluster_id;sex;shock_module_variable
- `COMSEC_CI`: not_present; concepts=admin1_or_admin2;agriculture_livelihood;asset_index_or_asset_variable;education;psu_or_cluster_id;sex;shock_module_variable
- `HH_SEC_B`: not_present; concepts=admin1_or_admin2;age;hhid;household_head_marker;pid;sex
- `COMSEC_CJ`: not_present; concepts=admin1_or_admin2;household_weight_or_person_weight;psu_or_cluster_id
- `AG_SEC2A`: not_present; concepts=agriculture_livelihood;latitude_or_longitude;shock_module_variable

## Raw Variable Verification Queue

- `HH_SEC_D` / `hh_d04_1`: care_or_barrier; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `HH_SEC_D` / `hh_d04_2`: care_or_barrier; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `HH_SEC_D` / `hh_d48`: care_or_barrier; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `HH_SEC_D` / `hh_d49_1`: care_or_barrier; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `HH_SEC_D` / `hh_d49_2`: care_or_barrier; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `HH_SEC_D` / `hh_d49_3`: care_or_barrier; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `AG_SEC2A` / `ag2a_09`: climate_geography; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `AG_SEC2A` / `ag2a_10`: climate_geography; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `AG_SEC2B` / `ag2b_20`: climate_geography; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `AG_SEC2B` / `ag2b_21`: climate_geography; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `COMSEC_CA;COMSEC_CB;COMSEC_CD;COMSEC_CE;COMSEC_CF;COMSEC_CG;COMSEC_CH;COMSEC_CI;COMSEC_CJ;comsec_cc` / `id_01`: climate_geography; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `COMSEC_CD` / `cm_d04b`: climate_geography; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `COMSEC_CD` / `cm_d05bm`: climate_geography; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `COMSEC_CD` / `cm_d05by`: climate_geography; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `COMSEC_CD` / `cm_d06b`: climate_geography; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `COMSEC_CD` / `cm_d07b`: climate_geography; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization

## Promotion Rule

Do not write this country-wave into `data/` until the raw package is complete,
merge keys and survey design are verified, financial-protection and access
variables pass value/unit/recall/missing-code checks, and a CHIRPS or ERA5
climate-linkage route is accepted.
