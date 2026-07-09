# Priority Raw Verification Workbook: NGA_2012_GHSP-W2_v02_M

This workbook is the post-download verification gate for `Nigeria`
`2012-2013`. It does not verify the dataset by itself; all blank
`fill_*` columns in the machine-readable templates must be completed from raw
files, labels, values, units, recall periods, missing codes, skip patterns, and
merge-key checks.

Current dataset gate: `blocked_raw_files_absent`

Next action: Download/place complete original raw package and documentation into the target folder.

Accepted CHIRPS/ERA5 route: `not_accepted_raw_timing_geography_unverified`

## Requirement Checklist

| requirement_id | current_requirement_gate | mapped_concepts | minimum_evidence |
|---|---|---|---|
| household_person_merge_keys | blocked_raw_package_required | household_id;demographics | Household/person IDs and module-level keys match across raw files; key cardinality and duplicates are documented. |
| weights_and_survey_design | blocked_raw_package_required | survey_weight;psu_cluster;strata | Household/person weights, PSU/cluster, strata, and any design notes are verified from raw values and documentation. |
| consumption_or_income_aggregate | blocked_raw_package_required | total_consumption_or_income | Survey-team consumption/income aggregate or documented reconstruction variables are verified with units and period. |
| oop_health_expenditure | blocked_raw_package_required | oop_health_expenditure | OOP health spending variables are verified with payer scope, units, recall period, zero/missing semantics, and aggreg... |
| illness_need_care_access | blocked_raw_package_required | health_need;care_or_barrier;insurance | Illness/need denominator, care-seeking, forgone care, barrier categories, and insurance variables are verified. |
| survey_timing | blocked_raw_package_required | survey_timing | Interview date/month/year or fieldwork timing is verified and can support pre-interview lag windows. |
| geography_climate_linkage | blocked_raw_package_required | climate_geography | GPS, cluster, EA, or admin geography is verified with geolocation quality, displacement/suppression, and boundary/cro... |
| missing_skip_units_recall | blocked_raw_package_required | household_id;survey_weight;total_consumption_or_income;oop_health_expenditure;health_need;care_or_barrier;survey_timi... | Missing codes, skip patterns, units, recall periods, valid ranges, and outlier handling are documented for all critic... |

## Machine-Readable Templates

- `temp/priority_promotion_verification_checklist.csv`
- `temp/priority_concept_verification_template.csv`
- `temp/priority_variable_verification_template.csv`
- `result/priority_dataset_verification_gate.csv`

## Guardrail

Do not write this wave into `data/` until every requirement row, critical
concept row, and selected variable row has raw-backed evidence and the climate
linkage route is accepted.
