# ALB_2002 Consumption Aggregate Metadata Crosswalk Audit

Status: fail-closed local-raw and metadata crosswalk for the ALB_2002 consumption denominator. This audit does not write `data/`, does not construct CHE or SDG outcomes, and does not promote any row to harmonization, outcome construction, SDG 3.8.2, or climate linkage.

## Bottom Line

- Local `Poverty_2002.sav` exposes `totcons`, `rcons`, `rfood`, `rnfood`, and `rutil` for 3,599 households.
- `total_consumption` in the ALB_2002 household-core candidate is an exact copy of raw `totcons` for all matched households.
- Local SPSS labels and the current master metadata catalog do not define the `totcons` unit, reference period, price basis, inclusion scope, or construction formula.
- A separate public IHSN source audit now documents the construction source: the PDF, metadata JSON, and 19 Stata do-files map local `totcons` to public metadata `totcons3`, labelled with durables and without rent and health.
- The questionnaire workbook supplies source-item spending language, including New Lek and recall-period wording, but not the constructed poverty aggregate recipe.
- SDG 3.8.2, recipe-ready, outcome-ready, and climate-linkage-ready rows from this audit: 0.
- Current decision: `documented_alb2002_consumption_aggregate_but_not_outcome_sdg_climate_ready`.

## Summary

| Metric | Value | Interpretation |
|---|---:|---|
| alb2002_consumption_aggregate_crosswalk_rows | 11 | Rows in the ALB_2002 consumption aggregate metadata/local evidence audit. |
| alb2002_consumption_aggregate_crosswalk_local_poverty_rows | 3599 | Rows exposed by local ALB_2002 Poverty_2002.sav. |
| alb2002_consumption_aggregate_crosswalk_local_poverty_columns | 14 | Columns exposed by local ALB_2002 Poverty_2002.sav. |
| alb2002_consumption_aggregate_crosswalk_metadata_catalog_rows | 0 | Local master metadata rows for ALB_2002; currently expected to be zero. |
| alb2002_consumption_aggregate_crosswalk_raw_totcons_positive_rows | 3599 | Positive raw `totcons` rows observed locally. |
| alb2002_consumption_aggregate_crosswalk_candidate_totcons_match_rows | 3599 | Candidate `total_consumption` rows exactly matching raw `totcons` by household id. |
| alb2002_consumption_aggregate_crosswalk_scale_ratio_within_10pct_rows | 2618 | Rows where `totcons / household_size / rcons` is within 10 percent of 1; diagnostic only. |
| alb2002_consumption_aggregate_crosswalk_questionnaire_new_lek_hits | 8 | Binary questionnaire string hits for New Lek wording; source-item evidence only. |
| alb2002_consumption_aggregate_crosswalk_questionnaire_aggregate_formula_hits | 0 | Binary questionnaire string hits for aggregate/formula terms; not accepted documentation. |
| alb2002_consumption_aggregate_crosswalk_construction_source_rows | 9 | Rows in the upstream public consumption-construction source audit. |
| alb2002_consumption_aggregate_crosswalk_construction_do_file_rows | 19 | Extracted public Stata do-files documenting the ALB_2002 consumption aggregate. |
| alb2002_consumption_aggregate_crosswalk_metadata_unit_period_ready_rows | 8 | Public source-audit rows documenting the denominator variant and unit/period context. |
| alb2002_consumption_aggregate_crosswalk_official_documentation_ready_rows | 9 | Rows with accepted public aggregate-construction documentation. |
| alb2002_consumption_aggregate_crosswalk_released_variable_mapping_ready_rows | 3 | Rows supporting the mapping from local `totcons` to public metadata `totcons3`. |
| alb2002_consumption_aggregate_crosswalk_denominator_variant_ready_rows | 8 | Rows documenting the final total-budget denominator variant. |
| alb2002_consumption_aggregate_crosswalk_recipe_ready_rows | 0 | Rows promoted to harmonization recipe readiness by this audit; intentionally zero. |
| alb2002_consumption_aggregate_crosswalk_outcome_ready_rows | 0 | Rows promoted to outcome construction by this audit; intentionally zero. |
| alb2002_consumption_aggregate_crosswalk_sdg382_ready_rows | 0 | Rows promoted to SDG 3.8.2 denominator readiness by this audit; intentionally zero. |
| alb2002_consumption_aggregate_crosswalk_climate_linkage_ready_rows | 0 | Rows promoted to climate linkage by this audit; intentionally zero. |
| alb2002_consumption_aggregate_crosswalk_current_decision | documented_alb2002_consumption_aggregate_but_not_outcome_sdg_climate_ready | Current fail-closed decision for ALB_2002 consumption aggregate metadata/local evidence. |

## Crosswalk Rows

| audit_family | source_variable | metadata_presence | local_raw_presence | candidate_presence | nonmissing_rows | positive_rows | readiness_status |
|---|---|---|---|---|---|---|---|
| raw_aggregate_metadata_crosswalk | totcons | 0 | 1 | 1 | 3599 | 3599 | local_totcons_documented_as_public_totcons3_total_budget_candidate |
| raw_aggregate_metadata_crosswalk | rcons | 0 | 1 | 0 | 3599 | 3599 | local_component_seen_not_household_denominator |
| raw_aggregate_metadata_crosswalk | rfood | 0 | 1 | 0 | 3599 | 3599 | local_component_seen_not_household_denominator |
| raw_aggregate_metadata_crosswalk | rnfood | 0 | 1 | 0 | 3599 | 3599 | local_component_seen_not_household_denominator |
| raw_aggregate_metadata_crosswalk | rutil | 0 | 1 | 0 | 3599 | 3598 | local_component_seen_not_household_denominator |
| candidate_lineage_crosscheck | totcons;total_consumption | 0 | 1 | 1 | 3599 | 3599 | candidate_copy_verified_but_denominator_semantics_blocked |
| scale_plausibility_diagnostic | totcons;household_size;rcons | 0 | 1 | 1 | 3599 | 2618 | scale_check_supports_review_not_promotion |
| questionnaire_source_scan | binary_string_scan | 0 | 1 | 0 | 1 | 0 | questionnaire_item_evidence_seen_aggregate_formula_absent |
| metadata_inventory_gap | ALB_2002_LSMS_v01_M | 0 | 0 | 0 | 0 | 0 | metadata_inventory_gap_blocks_denominator_acceptance |
| public_construction_source_evidence | totcons3;rpcons3;totcons.do;poverty.do | 1 | 1 | 1 | 3 | 8 | official_construction_source_documents_total_budget_denominator |
| upstream_sdg_policy_crosscheck | current_decision | 0 | 1 | 0 | 0 | 0 | upstream_denominator_policy_remains_fail_closed |

## Interpretation

- The raw aggregate is now documented as the public `totcons3` total-budget variant, but denominator provenance is not the same as outcome acceptance.
- Because the local metadata inventory lacks ALB_2002 aggregate rows, this workspace relies on the downloaded IHSN PDF, JSON, and Stata code source audit rather than the master metadata catalog.
- The scale diagnostic involving `totcons`, household size, and `rcons` supports manual review but must not be treated as an inferred formula.
- SDG 3.8.2 remains blocked because discretionary-budget construction still needs accepted total-consumption scope/period, SPL, PPP/CPI alignment, OOP numerator alignment, and benchmark validation.
- CHE10/CHE25 remain stress tests only until the denominator and OOP numerator pass together.

## Machine-Readable Outputs

- `temp/alb2002_consumption_aggregate_metadata_crosswalk_audit.csv`
- `result/alb2002_consumption_aggregate_metadata_crosswalk_summary.csv`
