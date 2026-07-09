# ALB_2005 Consumption Aggregate Metadata Crosswalk Audit

Status: fail-closed metadata/local-raw crosswalk. This audit compares public metadata aggregate/component variables for ALB_2005 `poverty` with the variables actually exposed by local `poverty.sav`. It does not write `data/`, does not construct CHE/SDG outcomes, and does not promote any row to harmonization, outcome construction, SDG 3.8.2, or climate linkage.

## Bottom Line

- Public metadata lists old-lek aggregate/component variables including `food`, `edu`, `durcons`, `nfoodc`, `nfood05`, `totutil`, `totutil05`, `totcons`, and `totcons05`.
- Local `poverty.sav` exposes `totcons`, `rcons`, and per-capita components, but the checked public-metadata formula components and `totcons05` are absent from this local extract.
- `totcons` is positive locally, but the local file cannot independently reconstruct or variant-check the documented formula from public metadata.
- Local per-capita fields (`rcons`, `rfood`, `rnfood`, `rutility`, `reduexp`, `rdurable`) are useful diagnostics only; they are not a documented household-total denominator recipe.
- SDG 3.8.2, recipe-ready, outcome-ready, and climate-linkage-ready rows from this audit: 0.
- Current decision: `blocked_alb2005_consumption_aggregate_metadata_crosswalk_not_ready`.

## Summary

| Metric | Value | Interpretation |
|---|---:|---|
| alb2005_consumption_aggregate_crosswalk_rows | 16 | Rows in the ALB_2005 consumption aggregate metadata crosswalk audit. |
| alb2005_consumption_aggregate_crosswalk_metadata_rows | 9 | Public metadata aggregate/component variables checked against local poverty.sav. |
| alb2005_consumption_aggregate_crosswalk_metadata_old_lek_rows | 8 | Checked public metadata aggregate/component labels mentioning old lek. |
| alb2005_consumption_aggregate_crosswalk_local_poverty_columns | 16 | Columns exposed by local ALB_2005 poverty.sav. |
| alb2005_consumption_aggregate_crosswalk_metadata_variables_present_in_local_raw_rows | 1 | Checked public metadata aggregate/component variables present in local poverty.sav. |
| alb2005_consumption_aggregate_crosswalk_metadata_variables_absent_from_local_raw_rows | 8 | Checked public metadata aggregate/component variables absent from local poverty.sav. |
| alb2005_consumption_aggregate_crosswalk_local_per_capita_component_rows | 6 | Local per-capita component variables available for diagnostics only. |
| alb2005_consumption_aggregate_crosswalk_totcons_positive_rows | 3638 | Positive local `totcons` rows in poverty.sav. |
| alb2005_consumption_aggregate_crosswalk_totcons05_local_rows | 0 | Local `totcons05` rows available in poverty.sav; should remain zero in current extract. |
| alb2005_consumption_aggregate_crosswalk_component_formula_reconstructable_rows | 0 | Rows indicating whether required public-metadata formula components are all present locally; should remain zero. |
| alb2005_consumption_aggregate_crosswalk_sdg382_ready_rows | 0 | Rows promoted to SDG 3.8.2 denominator readiness by this audit; intentionally zero. |
| alb2005_consumption_aggregate_crosswalk_recipe_ready_rows | 0 | Rows promoted to a harmonization recipe by this audit; intentionally zero. |
| alb2005_consumption_aggregate_crosswalk_outcome_ready_rows | 0 | Rows promoted to outcome construction by this audit; intentionally zero. |
| alb2005_consumption_aggregate_crosswalk_climate_linkage_ready_rows | 0 | Rows promoted to climate linkage by this audit; intentionally zero. |
| alb2005_consumption_aggregate_crosswalk_current_decision | blocked_alb2005_consumption_aggregate_metadata_crosswalk_not_ready | Current fail-closed decision for ALB_2005 aggregate metadata/local raw crosswalk evidence. |

## Crosswalk Rows

| audit_family | source_variable | metadata_presence | local_raw_presence | local_raw_label | nonmissing_rows | positive_rows | readiness_status |
|---|---|---|---|---|---|---|---|
| metadata_aggregate_crosswalk | food | 1 | 0 |  | 0 | 0 | public_metadata_variable_absent_from_local_raw_extract |
| metadata_aggregate_crosswalk | edu | 1 | 0 |  | 0 | 0 | public_metadata_variable_absent_from_local_raw_extract |
| metadata_aggregate_crosswalk | durcons | 1 | 0 |  | 0 | 0 | public_metadata_variable_absent_from_local_raw_extract |
| metadata_aggregate_crosswalk | nfoodc | 1 | 0 |  | 0 | 0 | public_metadata_variable_absent_from_local_raw_extract |
| metadata_aggregate_crosswalk | nfood05 | 1 | 0 |  | 0 | 0 | public_metadata_variable_absent_from_local_raw_extract |
| metadata_aggregate_crosswalk | totutil | 1 | 0 |  | 0 | 0 | public_metadata_variable_absent_from_local_raw_extract |
| metadata_aggregate_crosswalk | totutil05 | 1 | 0 |  | 0 | 0 | public_metadata_variable_absent_from_local_raw_extract |
| metadata_aggregate_crosswalk | totcons | 1 | 1 | Household total consumption | 3638 | 3638 | local_totcons_available_but_formula_components_absent |
| metadata_aggregate_crosswalk | totcons05 | 1 | 0 |  | 0 | 0 | public_metadata_variable_absent_from_local_raw_extract |
| local_per_capita_aggregate | rcons | 1 | 1 | Per capita consumption | 3638 | 3638 | local_per_capita_component_seen_not_household_denominator |
| local_per_capita_aggregate | rfood | 0 | 1 | Per capita food | 3638 | 3638 | local_per_capita_component_seen_not_household_denominator |
| local_per_capita_aggregate | rnfood | 0 | 1 | Per capita non food | 3638 | 3634 | local_per_capita_component_seen_not_household_denominator |
| local_per_capita_aggregate | rutility | 0 | 1 | Per capita utility | 3638 | 3638 | local_per_capita_component_seen_not_household_denominator |
| local_per_capita_aggregate | reduexp | 0 | 1 | Per capita education expenditure | 3638 | 2164 | local_per_capita_component_seen_not_household_denominator |
| local_per_capita_aggregate | rdurable | 0 | 1 | Per capita durable | 3638 | 3559 | local_per_capita_component_seen_not_household_denominator |
| upstream_blocker_crosscheck | current_decision | 1 | 1 |  | 0 | 0 | upstream_unit_period_audit_remains_fail_closed |

## Interpretation

- The old-lek metadata evidence supports manual review but is not enough to build financial-protection outcomes.
- The aggregate formula cannot be locally reconstructed from the current `poverty.sav` extract because key public-metadata components are missing locally.
- The `totcons05` variant is public-metadata-visible but not locally available, so denominator variant choice remains unresolved.
- SDG 3.8.2 remains blocked because the discretionary-budget denominator still needs verified total-consumption scope/period, poverty-line treatment, PPP/CPI alignment, and OOP numerator annualization.
- Climate-linked analysis remains independently blocked by missing verified household interview timing and climate-ready geography.

## Machine-Readable Outputs

- `temp/alb2005_consumption_aggregate_metadata_crosswalk_audit.csv`
- `result/alb2005_consumption_aggregate_metadata_crosswalk_summary.csv`
