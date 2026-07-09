# Outcome Denominator Plan

Status: outcome construction is planned but not executed. This report separates metadata-supported outcome readiness from raw-verified outcome construction.

## Outcome Gate Counts

| Outcome gate status | Count |
|---|---:|
| metadata_ready_raw_unverified | 369 |
| metadata_incomplete_for_outcome | 90 |
| ready_for_harmonized_outcome_construction | 17 |

## Outcome Families

| Outcome family | Count |
|---|---:|
| financial_protection | 196 |
| access | 140 |
| composite | 112 |
| mechanism_or_composite | 28 |

## External Input Status

| External input status | Count |
|---|---:|
| source_probe_ready | 252 |
| not_required | 224 |

## Summary Metrics

| Metric | Value | Interpretation |
|---|---:|---|
| outcome_plan_rows | 476 | Dataset-outcome readiness rows across quality-screened country-waves. |
| outcome_specification_rows | 17 | Unique outcome formula/specification rows. |
| metadata_ready_raw_unverified_outcome_rows | 369 | Outcome rows with metadata support but no raw verification. |
| ready_for_harmonized_outcome_construction_rows | 17 | Outcome rows with raw-verified required concepts and source-probed external inputs. |
| external_source_probe_ready_rows | 252 | Rows whose external validation/denominator source category has been probed. |
| gate_count_metadata_incomplete_for_outcome | 90 | Outcome construction gate status count. |
| gate_count_metadata_ready_raw_unverified | 369 | Outcome construction gate status count. |
| gate_count_ready_for_harmonized_outcome_construction | 17 | Outcome construction gate status count. |
| family_count_access | 140 | Outcome family row count. |
| family_count_composite | 112 | Outcome family row count. |
| family_count_financial_protection | 196 | Outcome family row count. |
| family_count_mechanism_or_composite | 28 | Outcome family row count. |

## Guardrail

CHE10/CHE25 and access outcomes can be prioritized once raw OOP, budget, need/access, weights, and recall periods are verified. SDG 3.8.2, capacity-to-pay, and impoverishment outcomes require additional denominator choices such as societal poverty line, PPP, CPI/price adjustment, or capacity-to-pay method. None of these outcomes should be interpreted until `data/household_outcomes.*` exists and `result/outcome_audit.csv` reports constructed rows with event-rate and missingness checks.

## Machine-Readable Outputs

- `temp/outcome_denominator_plan.csv`
- `result/outcome_specification_plan.csv`
- `result/outcome_denominator_plan_summary.csv`
