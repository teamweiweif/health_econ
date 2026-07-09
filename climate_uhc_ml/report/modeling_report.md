# Modeling Report

Status: some model outputs exist, but interpretation is still gated by validation and identification audits.

## Current Model Gate

The current design scorecard has 38 rows, including 3 current fail-closed rows. Decision: `fail_closed_design_scorecard_currently_no_go_for_estimation_or_policy_learning`. Data-write-ready rows: 0. Estimation remains gated unless audited analytical data, event rates, climate linkage, validation splits, and placebo-ready identifying variation exist.

| Current design audit status | Count |
|---|---:|
| complete | 1 |
| complete_candidate_not_promoted | 1 |
| complete_fail_closed | 1 |
| blocked | 1 |

| Current design no-go decision | Count |
|---|---:|
| no-go_main_multi_country_financial_protection | 1 |
| no-go_double_failure_primary | 1 |
| no-go_point_or_strong_causal_claims | 1 |
| no-go_final_event_rate_claims | 1 |
| no-go_transportable_targeting_claim | 1 |
| no-go_causal_claims | 1 |
| no-go_policy_learning_claim | 1 |
| go_audit_only_no_go_descriptive_manuscript | 1 |

The modeling/identification readiness plan has 476 dataset-outcome rows. Ready rows: predictive ML 0, reduced-form 0, causal ML 0, policy learning 0. These are readiness counts only.

## Readiness Plan

Predictive gate:

| Predictive readiness status | Count |
|---|---:|
| metadata_plan_only_raw_unverified | 369 |
| blocked_metadata_incomplete | 90 |
| blocked_until_constructed_outcome_and_climate_linked_data | 17 |

Reduced-form gate:

| Reduced-form readiness status | Count |
|---|---:|
| metadata_plan_only_raw_unverified | 369 |
| blocked_metadata_incomplete | 90 |
| blocked_until_constructed_outcome_and_climate_linked_data | 17 |

Causal ML gate:

| Causal ML readiness status | Count |
|---|---:|
| rejected_until_reduced_form_identification_passes | 476 |

Policy-learning gate:

| Policy-learning readiness status | Count |
|---|---:|
| rejected_until_validated_prediction_or_causal_effect_exists | 476 |

Validation-plan status:

| Model validation plan status | Count |
|---|---:|
| blocked_until_constructed_target_and_climate_linked_dataset | 85 |

Falsification/placebo-plan status:

| Falsification plan status | Count |
|---|---:|
| blocked_until_primary_estimate_and_required_inputs | 12 |

Policy-rule plan status:

| Policy rule plan status | Count |
|---|---:|
| rejected_until_reduced_form_identification_and_validation_pass | 40 |

## Scorecard Summary

| Outcome-validity metadata score | Count |
|---|---:|
| 5 | 33 |
| 2 | 3 |
| 3 | 1 |
| 1 | 1 |

## Predictive ML

| Predictive ML status | Count |
|---|---:|
| complete_limited_diagnostic | 1 |
| complete_limited_predictive_diagnostic_not_promoted | 1 |

Validated metric rows: 30

## Reduced-Form Models

| Reduced-form status | Count |
|---|---:|
| complete_limited_diagnostic | 1 |
| complete_limited_reduced_form_diagnostic_not_promoted | 1 |

Estimate rows: 88

## Causal ML and Policy Learning

| Causal ML/policy status | Count |
|---|---:|
| rejected_placebo_not_ready | 1 |

CATE rows: 0

Policy simulation rows: 0

## Robustness

| Robustness audit status | Count |
|---|---:|
| complete_limited_diagnostic | 1 |

| Robustness result status | Count |
|---|---:|
| planned_not_attempted | 14 |
| attempted_limited_threshold_comparison | 1 |
| attempted_limited_window_lag_comparison | 1 |
| attempted_limited_bh_correction | 1 |
| attempted_future_climate_placebo_not_available | 1 |

## Rejected for Now

- Predictive ML has been estimated only as a limited ALB_2002 CHE diagnostic with 30 grouped-admin2 validation metric rows. It is not deployable or transportable, and promoted multi-country predictive ML remains blocked.
- Reduced-form causal interpretation is rejected until climate-linked outcome data, geography/timing controls, and placebo tests exist.
- Causal ML/policy learning is rejected until the reduced-form identification gate passes.
