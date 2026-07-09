# ALB_2002 Access Candidate Outcome Audit

Status: temp-only household-level access candidate outcome audit. This builds household access, need, barrier, and composite candidates from raw ALB_2002 Health A/B variables. It does not write `data/`, does not construct final access outcomes, and does not promote any row to harmonization, SDG 3.8.2, or climate linkage.

## Summary

| Metric | Value | Interpretation |
|---|---:|---|
| alb2002_access_candidate_household_rows | 3599 | Temp-only ALB_2002 household access candidate rows. |
| alb2002_access_candidate_lineage_rows | 8 | Lineage rows for access candidate fields. |
| alb2002_access_candidate_audit_rows | 13 | Outcome audit rows for access candidate fields. |
| alb2002_access_candidate_q01_need_rows | 3247 | Households not coded as no-one-needed-care by m5b_q01. |
| alb2002_access_candidate_person_need_rows | 2202 | Households with Health A person-level need proxy. |
| alb2002_access_candidate_q01_cost_difficulty_rows | 1623 | Households reporting difficult/very difficult health-care payment situation. |
| alb2002_access_candidate_delayed_help_rows | 144 | Households with delayed or not-sought help candidate. |
| alb2002_access_candidate_referral_not_gone_rows | 161 | Households with hospital referral not gone candidate. |
| alb2002_access_candidate_refused_service_rows | 68 | Households with health-service refusal candidate. |
| alb2002_access_candidate_medicine_discount_any_barrier_rows | 493 | Households with medicine-discount entitlement barrier candidate. |
| alb2002_access_candidate_composite_cost_rows | 1661 | Composite cost-barrier candidate rows. |
| alb2002_access_candidate_composite_cost_rate | 0.461517 | Composite cost-barrier unweighted candidate rate. |
| alb2002_access_candidate_composite_cost_weighted_rate | 0.476346 | Composite cost-barrier weighted candidate rate. |
| alb2002_access_candidate_composite_distance_rows | 34 | Composite distance-barrier candidate rows. |
| alb2002_access_candidate_composite_supply_admin_rows | 405 | Composite supply/admin-barrier candidate rows. |
| alb2002_access_candidate_composite_nonuse_rows | 318 | Composite delayed/refused/nonuse candidate rows. |
| alb2002_access_candidate_composite_any_rows | 1861 | Composite any-access-barrier candidate rows. |
| alb2002_access_candidate_composite_any_rate | 0.517088 | Composite any-access-barrier unweighted candidate rate. |
| alb2002_access_candidate_composite_any_weighted_rate | 0.528953 | Composite any-access-barrier weighted candidate rate. |
| alb2002_access_candidate_policy_rows_observed | 24 | Upstream access/need policy audit rows consumed. |
| alb2002_access_candidate_low_event_rate_rows | 2 | Candidate access outcomes with event rate below 3 percent. |
| alb2002_access_candidate_outcome_promotion_ready_rows | 0 | Rows ready for final access-outcome promotion; intentionally zero. |
| alb2002_access_candidate_recipe_ready_rows | 0 | Rows ready for harmonized recipe promotion; intentionally zero. |
| alb2002_access_candidate_sdg382_ready_rows | 0 | Rows ready for SDG 3.8.2 construction; intentionally zero. |
| alb2002_access_candidate_climate_linkage_ready_rows | 0 | Rows ready for climate linkage; should remain zero until geography is verified. |
| alb2002_access_candidate_current_decision | blocked_alb2002_access_candidate_not_promoted_due_denominator_skip_climate_gates | Current fail-closed access candidate outcome decision. |

## Outcome Audit

| outcome_id | outcome_family | denominator_rows | event_rows | event_rate | weighted_event_rate | low_event_rate_flag | ready_for_outcome |
|---|---|---|---|---|---|---|---|
| person_need_proxy_candidate | need_denominator | 3599 | 2202 | 0.611837 | 0.63232 | 0 | 0 |
| q01_family_healthcare_need_candidate | need_denominator | 3599 | 3247 | 0.902195 | 0.908742 | 0 | 0 |
| q01_cost_difficulty_candidate | cost_barrier | 3247 | 1623 | 0.499846 | 0.51424 | 0 | 0 |
| money_raising_any_candidate | coping_barrier | 1623 | 1476 | 0.909427 | 0.93036 | 0 | 0 |
| delayed_help_any_candidate | forgone_or_delayed_care | 3247 | 144 | 0.0443486 | 0.0389328 | 0 | 0 |
| hospital_referral_not_gone_candidate | forgone_or_delayed_care | 3247 | 161 | 0.0495842 | 0.0445007 | 0 | 0 |
| refused_health_services_candidate | forgone_or_delayed_care | 3599 | 68 | 0.0188941 | 0.0176393 | 1 | 0 |
| medicine_discount_any_barrier_candidate | medicine_access_barrier | 2044 | 493 | 0.241194 | 0.226843 | 0 | 0 |
| composite_cost_barrier_candidate | cost_barrier | 3599 | 1661 | 0.461517 | 0.476346 | 0 | 0 |
| composite_distance_barrier_candidate | distance_barrier | 3599 | 34 | 0.00944707 | 0.00951398 | 1 | 0 |
| composite_supply_admin_barrier_candidate | supply_or_admin_barrier | 3599 | 405 | 0.112531 | 0.102979 | 0 | 0 |
| composite_delayed_refused_nonuse_candidate | forgone_or_delayed_care | 3599 | 318 | 0.0883579 | 0.080829 | 0 | 0 |
| composite_any_access_barrier_candidate | access_failure_composite | 3599 | 1861 | 0.517088 | 0.528953 | 0 | 0 |

## Lineage

| derived_field | source_fields | formula_or_rule | status | blocking_reason |
|---|---|---|---|---|
| person_need_proxy_candidate | m5a_q01;m5a_q07 | Any person chronic/disability or sudden-illness proxy aggregated to household. | candidate_not_promoted | Person-to-household need proxy is candidate-only. |
| q01_family_healthcare_need_candidate | m5b_q01 | m5b_q01 in 1,2,3; code 4 treated as no-one-needed-health-care. | candidate_not_promoted | Broad household need denominator requires final acceptance. |
| q01_cost_difficulty_candidate | m5b_q01 | m5b_q01 in 1,2 among q01 need-coded households. | candidate_not_promoted | Broad affordability is not the same as forgone care. |
| delayed_help_any_candidate | m5b_q03 | m5b_q03 greater than none. | candidate_not_promoted | Delayed-care count coding and denominator require final review. |
| hospital_referral_not_gone_candidate | m5b_q05 | m5b_q05 greater than none. | candidate_not_promoted | Referral nonuse has a narrower trigger than broad need. |
| refused_health_services_candidate | m5b_q07 | m5b_q07 yes. | candidate_not_promoted | Ever-refusal scope and period require final review. |
| medicine_discount_*_candidate | m5b_q09;m5b_q10 | Medicine discount barriers among entitled households. | candidate_not_promoted | Entitlement-specific barrier should not be pooled without a scope decision. |
| composite_*_candidate | m5b_q01;m5b_q03;m5b_q04;m5b_q05;m5b_q06;m5b_q07;m5b_q08;m5b_q10 | Union of cost, distance, supply/admin, delayed-care, referral nonuse, refusal, and medicine barriers. | candidate_not_promoted | Composite mixes denominators and is a screening diagnostic only. |

## Interpretation

- Candidate access outcomes are now available at household level in `temp/alb2002_access_candidate_household_outcomes.csv`.
- `m5b_q01` is the broadest need-denominator candidate, while delay, referral, refusal, and medicine-discount fields have narrower trigger-specific denominators.
- Composite access candidates are screening diagnostics only because they mix broad affordability, delayed care, referral nonuse, refusal, medicine entitlement, and conditional reason scopes.
- Outcome-promotion-ready, recipe-ready, SDG 3.8.2-ready, and climate-linkage-ready rows remain zero.

## Machine-Readable Outputs

- `temp/alb2002_access_candidate_household_outcomes.csv`
- `temp/alb2002_access_candidate_outcome_lineage.csv`
- `result/alb2002_access_candidate_outcome_audit.csv`
- `result/alb2002_access_candidate_outcome_summary.csv`
