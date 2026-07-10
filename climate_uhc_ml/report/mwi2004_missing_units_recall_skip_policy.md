# Malawi 2004 Missing, Units, Recall, and Skip Policy

Dataset: `MWI_2004_IHS-II_v01_M` - Malawi 2004-2005

This artifact accepts missing-code, unit, recall-period, and skip-pattern rules
for the current Malawi 2004 verified constructs: CHE10/CHE25 financial
protection and acute cost-barrier forgone care. It does not accept SDG 3.8.2,
distance/supply access outcomes, CHIRPS/ERA5 linkage, or promoted data writes.

## Summary

| metric | value | interpretation |
| --- | --- | --- |
| country_wave | MWI_2004_IHS-II_v01_M | Country-wave covered by this missing/units/recall/skip policy. |
| missing_units_recall_skip_policy_status | raw_missing_units_recall_skip_policy_verified_for_accepted_constructs | Final policy status for accepted Malawi 2004 constructs. |
| missing_units_recall_skip_policy_final_verified | 1 | Whether missing-code, unit, recall, and skip rules are accepted for the current CHE10/CHE25 and cost-barrier access scope. |
| financial_units_verified | 1 | Whether financial units/recall are accepted for CHE10/CHE25. |
| access_units_recall_skip_verified | 1 | Whether access recall, value labels, and skip policy are accepted for cost-barrier forgone care. |
| timing_units_verified | 1 | Whether interview timing units are accepted for climate-window route review. |
| geography_units_verified | 1 | Whether admin/EA geography units are accepted for route review. |
| sdg382_ready | 0 | SDG 3.8.2 remains blocked even when CHE10/CHE25 units are accepted. |
| accepted_chirps_era5_route | 0 | Climate route remains blocked. |
| data_write_gate_status | closed | This policy verifies raw-value semantics only; it does not write promoted data. |

## Policy Components

| policy_component | variables | accepted_policy | verification_status | remaining_caveat |
| --- | --- | --- | --- | --- |
| financial_units_and_recall | rexpagg; rexp_cat06; rexp_cat061; rexp_cat062; rexp_cat063 | Use annual real household expenditure variables from ihs2_pov.dta/ihs2_exp.dta for CHE10/CHE25; do not mix them with person-level health-module recall amounts. | raw_value_verified_for_accepted_scope | SDG 3.8.2 remains blocked because discretionary-budget poverty-line/PPP/CPI policy is not accepted. |
| financial_missing_policy | rexpagg; rexp_cat06 | Require positive total expenditure and nonmissing health OOP aggregate for CHE10/CHE25; retain zero OOP as valid zero spending. | raw_value_verified_for_accepted_scope | Financial inputs are verified for CHE10/CHE25 only. |
| acute_need_recall_and_values | d04 | Use d04==1 as illness/injury need during the past 2 weeks and d04==2 as no acute need; missing d04 is not imputed. | raw_value_verified_for_accepted_scope |  |
| access_action_values | d07a; d07b | Use code 2, labelled Did nothing/no money, as cost-barrier forgone care; count once when either d07a or d07b equals 2. | raw_value_verified_for_accepted_scope | Other access barriers are not promoted by this policy. |
| d07b_99_policy | d07b | Treat d07b==99 as no second action taken; do not count it as care or forgone care. | raw_value_verified_for_accepted_scope |  |
| access_skip_policy | d04; d07a; d07b | Exclude documented d07a/d07b values outside d04==1 from the acute-need access denominator; do not repair or reclassify them. | raw_value_verified_for_accepted_scope | This is an accepted exclusion for cost-barrier forgone care, not a general survey-cleaning repair. |
| health_context_recall | d15; d17; d18; d20; d26 | Use hospitalization/traditional-healer and coping variables as context/mechanism only; do not include them in the acute cost-barrier denominator. | raw_value_verified_for_accepted_scope | Separate outcome promotion is required before using coping or chronic need as primary outcomes. |
| timing_units | idate | Use converted household interview month/date only for climate-window anchoring; do not use generated fieldwork assumptions where raw idate exists. | raw_value_verified_for_accepted_scope | Climate exposure extraction remains blocked until CHIRPS/ERA5 route acceptance. |
| geography_units | dist; ta; ea; V51; access; access2 | Treat district/TA/EA as administrative or enumeration geography, not household coordinates. | raw_value_verified_for_accepted_scope | A boundary/crosswalk and CHIRPS/ERA5 aggregation route is still required. |

## Gate Decision

Status: `raw_missing_units_recall_skip_policy_verified_for_accepted_constructs`. The remaining Malawi 2004 promotion blockers after
this policy are climate-route acceptance, promoted-dataset synthesis, SDG 3.8.2
policy, and the data-write gate.
