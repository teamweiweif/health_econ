# Country-Wave Promotion Packet: Tanzania 2008-2009

Dataset: `National Panel Survey 2008-2009, Wave 1`

IDNO: `TZA_2008_NPS-R1_v03_M`

Official URL: https://microdata.worldbank.org/catalog/76/get-microdata

Local target folder: `temp/raw_downloads/TZA_2008_NPS-R1_v03_M/`

Current registry status: `not_promoted`

## Gate Summary

| Gate | Status | Evidence | Required action |
|---|---|---|---|
| complete_original_raw_package | fail | intake_status=instructions_or_documentation_only; tabular=0; archives=0; docs=1 | Place complete original raw archive/tabular package and documentation in the local target folder. |
| raw_value_unit_recall_missing_verification | fail | raw_not_inspected=105 | Inspect raw labels/values, merge keys, units, recall periods, skip patterns, and missing codes. |
| financial_protection_che10_che25 | fail | climate_geography:raw_not_inspected; household_id:raw_not_inspected; oop_health_expenditure:raw_not_inspected; survey_timing:raw_not_inspected; survey_weight:raw_not_inspected; total_consumption_or_income:raw_not_inspected | Verify total consumption/income, OOP health expenditure, weights, timing, geography, and merge keys. |
| access_forgone_care | fail | care_or_barrier:raw_not_inspected; health_need:raw_not_inspected | Verify illness/need denominator, care seeking, and cost/distance/supply barrier semantics. |
| climate_linkage | fail | survey_timing:raw_not_inspected; climate_geography:raw_not_inspected | Verify survey month/date, usable admin/GPS/cluster geography, and accepted CHIRPS/ERA5 extraction route. |
| double_failure | fail | financial_ready=0; access_ready=0 | Pass both financial-protection and access/forgone-care value verification gates. |

## Expected Files or Modules

- `SEC_3A_English_Labels`: not_present; concepts=agriculture_livelihood;care_not_sought_reason;coping_borrowed;hhid;reason_not_sought_distance;shock_module_variable;total_consumption_or_income
- `SEC_3B_English_Labels`: not_present; concepts=agriculture_livelihood;care_not_sought_reason;coping_borrowed;hhid;reason_not_sought_distance;shock_module_variable;total_consumption_or_income
- `SEC_B_C_D_E1_F_G1_U_English_Labels`: not_present; concepts=admin1_or_admin2;age;agriculture_livelihood;asset_index_or_asset_variable;care_sought;education;hhid;household_weight_or_person_weight;illness_or_injury_need;oop_health_expenditure;reason_not_sought_distance;sex
- `HH.Geovariables_Y1`: not_present; concepts=admin1_or_admin2;agriculture_livelihood;hhid;latitude_or_longitude;psu_or_cluster_id;reason_not_sought_distance;shock_module_variable
- `SEC_4A_English_Labels`: not_present; concepts=agriculture_livelihood;hhid;shock_module_variable
- `SEC_A_T_English_Labels`: not_present; concepts=admin1_or_admin2;agriculture_livelihood;hhid;household_weight_or_person_weight;psu_or_cluster_id;rural;shock_module_variable;strata
- `SEC_H1_J_K2_O2_P1_Q1_S1_English_Labels`: not_present; concepts=admin1_or_admin2;age;asset_index_or_asset_variable;coping_borrowed;hhid;shock_module_variable
- `TZY1.HH.Consumption`: not_present; concepts=admin1_or_admin2;education;hhid;household_size;household_weight_or_person_weight;interview_date_or_survey_month;psu_or_cluster_id;reason_not_sought_distance;rural;strata;total_consumption_or_income
- `SEC_S2_English_Labels`: not_present; concepts=age;asset_index_or_asset_variable;hhid;illness_or_injury_need;sex
- `SECTCEFG`: not_present; concepts=admin1_or_admin2;agriculture_livelihood;psu_or_cluster_id;shock_module_variable
- `SEC_P2_English_Labels`: not_present; concepts=coping_borrowed;hhid
- `SECTCH`: not_present; concepts=admin1_or_admin2;agriculture_livelihood;asset_index_or_asset_variable;education;psu_or_cluster_id;sex

## Raw Variable Verification Queue

- `SEC_B_C_D_E1_F_G1_U_English_Labels` / `scq14_trans`: care_or_barrier; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `SEC_B_C_D_E1_F_G1_U_English_Labels` / `sdq3_1`: care_or_barrier; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `SEC_B_C_D_E1_F_G1_U_English_Labels` / `sdq3_2`: care_or_barrier; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `SEC_B_C_D_E1_F_G1_U_English_Labels` / `sdq42`: care_or_barrier; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `SEC_B_C_D_E1_F_G1_U_English_Labels` / `sdq43_1`: care_or_barrier; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `SEC_B_C_D_E1_F_G1_U_English_Labels` / `sdq43_2`: care_or_barrier; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `SEC_B_C_D_E1_F_G1_U_English_Labels` / `sdq43_3`: care_or_barrier; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `SEC_B_C_D_E1_F_G1_U_English_Labels` / `sdq54`: care_or_barrier; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `SEC_B_C_D_E1_F_G1_U_English_Labels` / `sdq55_1`: care_or_barrier; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `SEC_B_C_D_E1_F_G1_U_English_Labels` / `sdq55_2`: care_or_barrier; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `SEC_B_C_D_E1_F_G1_U_English_Labels` / `sdq55_3`: care_or_barrier; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `HH.Geovariables_Y1` / `lat_modified`: climate_geography; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `HH.Geovariables_Y1` / `lon_modified`: climate_geography; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `SECTA1A2_English_Labels;SECTA1A2_Swahili_Labels;SECTCB;SECTCB_Swahili_Labels;SECTCC;SECTCD;SECTCEFG;SECTCH;SECTCI;SECTCJ_S;SEC_A_T_English_Labels;SEC_A_T_Swahili_Labels;nps_weights_oct2010` / `district`: climate_geography; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `SECTA1A2_English_Labels;SECTA1A2_Swahili_Labels;SECTCB;SECTCB_Swahili_Labels;SECTCC;SECTCD;SECTCEFG;SECTCH;SECTCI;SECTCJ_S;SEC_A_T_English_Labels;SEC_A_T_Swahili_Labels;TZY1.HH.Consumption;nps_weights_oct2010` / `region`: climate_geography; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `SECTA1A2_English_Labels;SECTA1A2_Swahili_Labels;SECTCB;SECTCB_Swahili_Labels;SECTCC;SECTCD;SECTCEFG;SECTCH;SECTCI;SECTCJ_S;SEC_A_T_English_Labels;SEC_A_T_Swahili_Labels;nps_weights_oct2010` / `ward`: climate_geography; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization

## Promotion Rule

Do not write this country-wave into `data/` until the raw package is complete,
merge keys and survey design are verified, financial-protection and access
variables pass value/unit/recall/missing-code checks, and a CHIRPS or ERA5
climate-linkage route is accepted.
