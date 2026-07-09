# Modeling and Identification Plan

Status: modeling, identification, robustness, and policy-learning designs are planned but not estimated. These rows are gate checks only and do not claim predictive performance, causal effects, CATEs, or policy value.

## Predictive ML Gate

| Predictive ML gate status | Count |
|---|---:|
| metadata_plan_only_raw_unverified | 369 |
| blocked_metadata_incomplete | 90 |
| blocked_until_constructed_outcome_and_climate_linked_data | 17 |

## Reduced-Form Gate

| Reduced-form gate status | Count |
|---|---:|
| metadata_plan_only_raw_unverified | 369 |
| blocked_metadata_incomplete | 90 |
| blocked_until_constructed_outcome_and_climate_linked_data | 17 |

## Causal ML Gate

| Causal ML gate status | Count |
|---|---:|
| rejected_until_reduced_form_identification_passes | 476 |

## Validation Plan Status

| Validation plan status | Count |
|---|---:|
| blocked_until_constructed_target_and_climate_linked_dataset | 85 |

## Falsification and Placebo Plan Status

| Falsification plan status | Count |
|---|---:|
| blocked_until_primary_estimate_and_required_inputs | 12 |

## Policy-Learning Plan Status

| Policy rule status | Count |
|---|---:|
| rejected_until_reduced_form_identification_and_validation_pass | 40 |

## Summary Metrics

| Metric | Value | Interpretation |
|---|---:|---|
| modeling_identification_plan_rows | 476 | Dataset-outcome modeling readiness rows. |
| modeling_validation_plan_rows | 85 | Outcome-by-validation-design predictive ML planning rows. |
| falsification_placebo_plan_rows | 12 | Required placebo, robustness, and falsification checks to run after estimation exists. |
| policy_learning_plan_rows | 40 | Targeting-rule by budget planning rows. |
| predictive_ready_rows | 0 | Rows ready for predictive model validation. |
| reduced_form_ready_rows | 0 | Rows ready for reduced-form estimation. |
| causal_ml_ready_rows | 0 | Rows where causal ML may be specified after reduced-form and placebo gates. |
| policy_learning_ready_rows | 0 | Rows where policy learning may be evaluated. |
| predictive_gate_count_blocked_metadata_incomplete | 90 | Modeling/identification planning status count. |
| predictive_gate_count_blocked_until_constructed_outcome_and_climate_linked_data | 17 | Modeling/identification planning status count. |
| predictive_gate_count_metadata_plan_only_raw_unverified | 369 | Modeling/identification planning status count. |
| reduced_form_gate_count_blocked_metadata_incomplete | 90 | Modeling/identification planning status count. |
| reduced_form_gate_count_blocked_until_constructed_outcome_and_climate_linked_data | 17 | Modeling/identification planning status count. |
| reduced_form_gate_count_metadata_plan_only_raw_unverified | 369 | Modeling/identification planning status count. |
| causal_ml_gate_count_rejected_until_reduced_form_identification_passes | 476 | Modeling/identification planning status count. |
| validation_plan_status_count_blocked_until_constructed_target_and_climate_linked_dataset | 85 | Modeling/identification planning status count. |
| falsification_plan_status_count_blocked_until_primary_estimate_and_required_inputs | 12 | Modeling/identification planning status count. |
| policy_rule_status_count_rejected_until_reduced_form_identification_and_validation_pass | 40 | Modeling/identification planning status count. |

## Guardrails

- Predictive ML requires constructed outcomes, climate-linked data, and non-random validation splits before any performance claim.
- Reduced-form climate estimates require verified geography, timing, exposure variation, controls, and placebo checks before causal language.
- Causal ML and policy learning are rejected until the reduced-form identification gate passes; they cannot compensate for weak identification.
- Policy simulations require sensitivity over assumed support benefit sizes and must report false exclusion and transportability diagnostics.

## Machine-Readable Outputs

- `temp/modeling_identification_plan.csv`
- `result/modeling_validation_plan.csv`
- `result/falsification_placebo_plan.csv`
- `result/policy_learning_plan.csv`
- `result/modeling_identification_plan_summary.csv`
