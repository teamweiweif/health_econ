# ALB_2002 Harmonized Household Core Promotion

Status: scoped limited promotion. This writes `data/harmonized_household.csv` for ALB_2002 household-core inspection only. It does not promote final outcomes, SDG 3.8.2, climate exposure, climate-linked data, weighted inference, descriptive diagnostics, predictive ML, reduced-form estimation, causal ML, or policy learning.

## Summary

| metric | value | interpretation |
|---|---|---|
| alb2002_harmonized_household_core_promotion_audit_rows | 8 | Rows in the scoped harmonized-core promotion audit. |
| alb2002_harmonized_household_core_source_candidate_rows | 3599 | Rows in temp/alb2002_analysis_candidate_dataset.csv. |
| alb2002_harmonized_household_core_rows | 3599 | Rows written to data/harmonized_household.csv under limited scope. |
| alb2002_harmonized_household_core_columns | 68 | Columns in the limited harmonized household core. |
| alb2002_harmonized_household_core_identity_rows | 3599 | Rows with nonmissing household ID. |
| alb2002_harmonized_household_core_timing_rows | 3599 | Rows with interview month and date. |
| alb2002_harmonized_household_core_weight_rows | 3599 | Rows with nonmissing household weight. |
| alb2002_harmonized_household_core_admin2_rows | 3599 | Rows with candidate admin2 name. |
| alb2002_harmonized_household_core_coordinate_rows | 0 | Rows with both latitude and longitude; should remain zero. |
| alb2002_harmonized_household_core_candidate_consumption_rows | 3599 | Rows carrying candidate total-budget input. |
| alb2002_harmonized_household_core_candidate_oop_rows | 3599 | Rows carrying candidate OOP input. |
| alb2002_harmonized_household_core_candidate_need_rows | 3599 | Rows carrying candidate health-need input. |
| alb2002_harmonized_household_core_limited_data_write_ready_rows | 3599 | Rows allowed in data/ only as a limited harmonized household core. |
| alb2002_harmonized_household_core_final_outcome_ready_rows | 0 | Rows ready for final outcome construction; intentionally zero. |
| alb2002_harmonized_household_core_climate_linkage_ready_rows | 0 | Rows ready for climate linkage; intentionally zero. |
| alb2002_harmonized_household_core_analysis_ready_rows | 0 | Rows ready for final empirical analysis; intentionally zero. |
| alb2002_harmonized_household_core_current_decision | limited_harmonized_household_core_promoted_outcome_climate_still_blocked | Current scoped promotion decision. |
| alb2002_harmonized_household_core_data_use_limit | harmonized_household_core_only_not_for_final_outcome_or_climate_analysis | Guardrail embedded in every output row. |

## Gate Audit

| gate_id | status | rows_passing | rows_blocked | next_action |
|---|---|---|---|---|
| source_candidate | complete | 3599 | 0 | Use only with the explicit data-use limit until final gates pass. |
| identity_timing_design | complete_limited_core | 3599 | 0 | Resolve weight-use semantics before weighted inference. |
| demographic_covariates | complete_limited_core | 3599 | 0 | Extend only after raw variable value/label checks are accepted. |
| candidate_financial_inputs | candidate_input_not_final_outcome | 3599 | 3599 | Accept numerator inclusion, recall policy, denominator benchmark, and SDG 3.8.2 rules before outcome construction. |
| candidate_access_inputs | candidate_input_not_final_outcome | 3599 | 3599 | Accept access denominator, skip semantics, and low-event handling before final outcome construction. |
| geography_for_climate | blocked_for_climate_linkage | 0 | 3599 | Obtain/verify official GPS, PSU crosswalk, or historical district boundaries before climate linkage. |
| final_outcomes | blocked_final_outcome_promotion | 0 | 3599 | Resolve OOP/access/SDG rules and rerun outcome construction only after candidate status is removed. |
| climate_linked_dataset | blocked_climate_linkage_promotion | 0 | 3599 | Promote climate exposure only after geography, timing, source, and baseline gates pass. |

## Guardrails

- Every row carries `harmonized_scope=alb2002_household_core_limited_no_final_outcome_no_climate`.
- Every row carries `outcome_status=candidate_inputs_not_final_outcomes` and `data_use_limit=harmonized_household_core_only_not_for_final_outcome_or_climate_analysis`.
- Candidate OOP, consumption, access, and composite fields are retained for audit but are not final outcomes.
- Climate linkage remains blocked because the output has no coordinates and no promoted historical admin boundary/crosswalk.
- `data/household_outcomes.csv`, `data/climate_exposures_nasa_power.csv`, and `data/climate_linked_household.csv` are not written by this promotion.

## Machine-Readable Outputs

- `data/harmonized_household.csv`
- `temp/harmonization_audit.csv`
- `temp/harmonized_lineage.csv`
- `temp/alb2002_harmonized_household_core_promotion_audit.csv`
- `result/alb2002_harmonized_household_core_promotion_summary.csv`
