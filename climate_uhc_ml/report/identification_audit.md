# Identification Audit

Status: reduced-form estimates exist, but causal interpretation still depends on placebo/robustness checks.

## Current Evidence

The project now has broad catalog screening, public metadata/schema inventories, candidate variable maps, a current fail-closed design scorecard, and public external raw schema evidence where direct archives were available. Verified harmonized outcomes, verified climate exposure variables, event rates, and placebo tests remain unavailable unless the counts below say otherwise.

## Design Scorecard State

| Go/no-go state | Count |
|---|---:|
| no-go for estimation; go for manual raw access/schema inspection | 35 |
| no-go for estimation; go for source/boundary/baseline/outcome-resolution work | 1 |
| no-go for main multi-country paper under current evidence | 1 |
| go for internal audit screen only; no-go for publishable descriptive estimates | 1 |

Current design scorecard audit:

| Metric | Value |
|---|---:|
| Scorecard rows | 38 |
| Current-state rows | 3 |
| Audit rows | 4 |
| No-go threshold rows | 8 |
| Failed/not-estimable thresholds | 8 |
| Data-write-ready rows | 0 |
| Decision | fail_closed_design_scorecard_currently_no_go_for_estimation_or_policy_learning |

| Current design scorecard audit status | Count |
|---|---:|
| complete | 1 |
| complete_candidate_not_promoted | 1 |
| complete_fail_closed | 1 |
| blocked | 1 |

| Current design threshold status | Count |
|---|---:|
| failed | 2 |
| not_estimable | 2 |
| failed_for_causal_claims | 1 |
| candidate_only_not_final | 1 |
| rejected_until_reduced_form_passes | 1 |
| not_yet_descriptive_paper_ready | 1 |

## Reduced-Form Gate

| Reduced-form model status | Count |
|---|---:|
| complete_limited_diagnostic | 1 |
| complete_limited_reduced_form_diagnostic_not_promoted | 1 |

Reduced-form estimate rows: 88

## Placebo Readiness

| Placebo-readiness status | Count |
|---|---:|
| ready | 2 |
| not_ready | 1 |

## Required Before Causal Language

- construct financial-protection/access outcomes from raw microdata;
- link verified geography and survey timing to pre-interview climate exposure;
- test seasonality and geography controls;
- run future-climate lead placebo checks;
- run alternative lag/source robustness;
- cluster or survey-design robustness;
- country leave-one-out diagnostics.
