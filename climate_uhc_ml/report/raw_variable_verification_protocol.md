# Raw Variable Verification Protocol

Status: planning artifact only. No country-wave is harmonization-ready until raw files are present, raw schemas are inspected, and raw values, labels, units, recall periods, merge keys, missing codes, and lineage pass verification.

## Counts

| Metric | Value | Interpretation |
|---|---:|---|
| protocol_rows | 2571 | Candidate raw variables requiring verification. |
| scaffold_rows | 1204 | Harmonized-variable scaffold rows; not a usable recipe. |
| priority_dataset_count | 28 | Quality-prioritized datasets included. |
| concept_count | 13 | Raw-ingestion concepts represented. |
| raw_file_inventory_rows | 209 | Raw tabular file inventory rows currently available. |
| raw_variable_catalog_rows | 5410 | Raw variable catalog rows currently available. |
| scaffold_ready_for_recipe_rows | 0 | No scaffold row is recipe-ready until raw value audits pass. |
| verification_status_raw_not_inspected | 2571 | Protocol verification status count. |
| raw_file_status_raw_files_not_present | 2571 | Protocol raw-file status count. |
| metadata_confidence_high | 2335 | Protocol metadata-confidence count. |
| metadata_confidence_metadata_candidate_from_concept_checklist | 49 | Protocol metadata-confidence count. |
| metadata_confidence_moderate | 187 | Protocol metadata-confidence count. |

## Verification Status

| Verification status | Count |
|---|---:|
| raw_not_inspected | 2571 |

## Raw File Status

| Raw file status | Count |
|---|---:|
| raw_files_not_present | 2571 |

## Metadata Confidence

| Metadata confidence | Count |
|---|---:|
| high | 2335 |
| moderate | 187 |
| metadata_candidate_from_concept_checklist | 49 |

## Concept Coverage

| Concept | Count |
|---|---:|
| demographics | 448 |
| shocks_or_livelihood | 439 |
| climate_geography | 322 |
| care_or_barrier | 275 |
| health_need | 230 |
| oop_health_expenditure | 199 |
| psu_cluster | 154 |
| survey_weight | 141 |
| survey_timing | 102 |
| total_consumption_or_income | 102 |
| household_id | 65 |
| strata | 59 |
| insurance | 35 |

## Required Raw Checks

| Concept | Raw verification checks |
|---|---|
| care_or_barrier | care-seeking denominator; barrier categories; cost/distance/supply coding; skip pattern; multiple responses |
| climate_geography | admin level or GPS availability; coordinate displacement/suppression; merge key; rural/admin consistency; climate linkage precision |
| demographics | age/sex/education/household roster logic; household head definition; derived age-structure feasibility |
| health_need | need denominator definition; skip pattern; individual vs household level; recall period; missing and no-need coding |
| household_id | nonmissing rate; uniqueness at stated level; stable across modules; household/person merge behavior |
| insurance | insurance/coverage definition; individual vs household level; current coverage timing; public/private coding |
| oop_health_expenditure | numeric type; OOP scope; reimbursement/insurance exclusion; recall period; item vs aggregate; missing and zero coding |
| psu_cluster | cluster/EA identifier; sampling level; variance cluster suitability; merge consistency |
| shocks_or_livelihood | shock/livelihood/coping meaning; pre/post treatment timing; agriculture exposure; food insecurity and coping coding |
| strata | strata identifier; survey-design documentation; missing/empty strata; merge consistency |
| survey_timing | parseable interview date/month/year; fieldwork calendar consistency; missing timing; usable lag windows |
| survey_weight | numeric positive weights; household vs person applicability; extreme weights; survey design documentation |
| total_consumption_or_income | numeric type; local currency unit; recall/reference period; aggregate source; negative/zero values; household level |

## Outputs

- `temp/raw_variable_verification_protocol.csv`: candidate raw variables and concept-specific checks.
- `temp/harmonization_recipe_scaffold.csv`: scaffold rows for expected harmonized variables. This is not `temp/harmonization_recipe.csv` and must not be used as an analysis recipe without raw verification.
- `result/raw_variable_verification_summary.csv`: machine-readable counts.

## Next Actions After Manual Downloads

1. Place raw files or archives under the dataset folders in `temp/raw_downloads/`.
2. Run `python script/17_audit_raw_downloads.py` and `python script/03_inspect_raw_schemas.py`.
3. Re-run this protocol script and inspect rows with `raw_variable_seen_value_audit_pending`.
4. Only after raw checks pass, create `temp/harmonization_recipe.csv` from verified rows, not from metadata-only candidates.
