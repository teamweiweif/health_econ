# Country-Wave Promotion Packet: Ethiopia 2021-2022

Dataset: `Socio-Economic Panel Survey 2021-2022`

IDNO: `ETH_2021_ESPS-W5_v02_M`

Official URL: https://microdata.worldbank.org/catalog/6161/get-microdata

Local target folder: `temp/raw_downloads/ETH_2021_ESPS-W5_v02_M/`

Current registry status: `not_promoted`

## Gate Summary

| Gate | Status | Evidence | Required action |
|---|---|---|---|
| complete_original_raw_package | fail | intake_status=instructions_or_documentation_only; tabular=0; archives=0; docs=1 | Place complete original raw archive/tabular package and documentation in the local target folder. |
| raw_value_unit_recall_missing_verification | fail | raw_not_inspected=107 | Inspect raw labels/values, merge keys, units, recall periods, skip patterns, and missing codes. |
| financial_protection_che10_che25 | fail | climate_geography:raw_not_inspected; household_id:raw_not_inspected; oop_health_expenditure:raw_not_inspected; survey_timing:raw_not_inspected; survey_weight:raw_not_inspected; total_consumption_or_income:raw_not_inspected | Verify total consumption/income, OOP health expenditure, weights, timing, geography, and merge keys. |
| access_forgone_care | fail | care_or_barrier:raw_not_inspected; health_need:raw_not_inspected | Verify illness/need denominator, care seeking, and cost/distance/supply barrier semantics. |
| climate_linkage | fail | survey_timing:raw_not_inspected; climate_geography:raw_not_inspected | Verify survey month/date, usable admin/GPS/cluster geography, and accepted CHIRPS/ERA5 extraction route. |
| double_failure | fail | financial_ready=0; access_ready=0 | Pass both financial-protection and access/forgone-care value verification gates. |

## Expected Files or Modules

- `sect8_3_ls_w5.dta`: not_present; concepts=admin1_or_admin2;agriculture_livelihood;care_sought;hhid;household_weight_or_person_weight;oop_health_expenditure;psu_or_cluster_id;rural;shock_module_variable;strata
- `sect11_ph_w5.dta`: not_present; concepts=admin1_or_admin2;agriculture_livelihood;hhid;household_weight_or_person_weight;psu_or_cluster_id;reason_not_sought_distance;rural
- `sect3_pp_w5.dta`: not_present; concepts=admin1_or_admin2;agriculture_livelihood;coping_borrowed;hhid;household_weight_or_person_weight;latitude_or_longitude;psu_or_cluster_id;reason_not_sought_distance;rural
- `sect06_com_w5.dta`: not_present; concepts=admin1_or_admin2;agriculture_livelihood;coping_borrowed;psu_or_cluster_id;reason_not_sought_distance;rural;shock_module_variable
- `sect04_com_w5.dta`: not_present; concepts=admin1_or_admin2;asset_index_or_asset_variable;care_sought;psu_or_cluster_id;reason_not_sought_distance;rural;sex;shock_module_variable
- `sect4_pp_w5.dta`: not_present; concepts=admin1_or_admin2;agriculture_livelihood;hhid;household_weight_or_person_weight;psu_or_cluster_id;rural;shock_module_variable
- `sect9_ph_w5.dta`: not_present; concepts=admin1_or_admin2;agriculture_livelihood;hhid;household_weight_or_person_weight;psu_or_cluster_id;rural;shock_module_variable
- `sect8_2_ls_w5.dta`: not_present; concepts=admin1_or_admin2;agriculture_livelihood;hhid;household_weight_or_person_weight;psu_or_cluster_id;reason_not_sought_distance;rural;total_consumption_or_income
- `sect3_hh_w5.dta`: not_present; concepts=admin1_or_admin2;age;care_not_sought_reason;care_sought;health_insurance;hhid;household_weight_or_person_weight;illness_or_injury_need;oop_health_expenditure;pid;psu_or_cluster_id;reason_not_sought_distance;rural
- `sect7_pp_w5.dta`: not_present; concepts=admin1_or_admin2;agriculture_livelihood;care_not_sought_reason;coping_borrowed;education;household_weight_or_person_weight;psu_or_cluster_id
- `sect11_com_w5.dta`: not_present; concepts=admin1_or_admin2;agriculture_livelihood;education;psu_or_cluster_id;rural
- `eth_householdgeovariables_y5.dta`: not_present; concepts=admin1_or_admin2;agriculture_livelihood;hhid;latitude_or_longitude;psu_or_cluster_id;reason_not_sought_distance;rural;shock_module_variable

## Raw Variable Verification Queue

- `sect04_com_w5.dta` / `cs4q28`: care_or_barrier; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `sect04_com_w5.dta` / `cs4q30`: care_or_barrier; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `sect04_com_w5.dta` / `cs4q37`: care_or_barrier; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `sect3_hh_w5.dta` / `s3q10a`: care_or_barrier; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `sect3_hh_w5.dta` / `s3q10b`: care_or_barrier; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `sect3_hh_w5.dta` / `s3q11`: care_or_barrier; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `sect3_hh_w5.dta` / `s3q12a`: care_or_barrier; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `sect3_hh_w5.dta` / `s3q12b`: care_or_barrier; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `sect3_hh_w5.dta` / `s3q13`: care_or_barrier; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `sect3_hh_w5.dta;sect3_pp_w5.dta` / `s3q16`: care_or_barrier; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `sect3_hh_w5.dta;sect3_pp_w5.dta` / `s3q17`: care_or_barrier; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `sect3_hh_w5.dta;sect3_pp_w5.dta` / `s3q18`: care_or_barrier; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `sect8_3_ls_w5.dta` / `ls_s8_3q23`: care_or_barrier; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `sect8_3_ls_w5.dta` / `ls_s8_3q24`: care_or_barrier; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `cons_agg_w5.dta;sect01a_com_w5.dta;sect01b_com_w5.dta;sect02_com_w5.dta;sect03_com_w5.dta;sect04_com_w5.dta;sect05_com_w5.dta;sect06_com_w5.dta;sect07_com_w5.dta;sect08_com_w5.dta;sect09_com_w5.dta;sect10_ph_w5.dta;sect10a_com_w5.dta;sect10a_hh_w5.dta;sect11_com_w5.dta;sect11_hh_w5.dta;sect11_ph_w5.dta;sect12_com_w5.dta;sect12a_hh_w5.dta;sect12b1_hh_w5.dta` / `saq01`: climate_geography; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `eth_householdgeovariables_y5.dta;eth_plotgeovariables_y5.dta` / `cropshare`: climate_geography; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization

## Promotion Rule

Do not write this country-wave into `data/` until the raw package is complete,
merge keys and survey design are verified, financial-protection and access
variables pass value/unit/recall/missing-code checks, and a CHIRPS or ERA5
climate-linkage route is accepted.
