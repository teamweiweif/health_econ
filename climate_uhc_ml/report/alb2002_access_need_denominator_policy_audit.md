# ALB_2002 Access and Need Denominator Policy Audit

Status: fail-closed denominator-policy audit. This report reads ALB_2002 raw Health A and Health B files and compares candidate need, forgone-care, cost, distance, supply/admin, medicine-access, coping, and composite access-denominator policies. It does not write `data/`, does not construct final access outcomes, and does not promote any row to harmonization, SDG 3.8.2, outcome construction, or climate linkage.

## Bottom Line

- ALB_2002 has usable raw access and need signals, including no-one-needed-care coding, delayed/not-sought care, referral nonuse, service refusal, medicine-discount barriers, and person-level illness proxies.
- The denominator options differ materially: broad family health-care need, delayed-care triggers, referral triggers, refusal triggers, medicine entitlement, and person-level illness proxies are not interchangeable.
- Cost, distance, and supply/admin barriers can be stress-tested, but final access outcomes require an explicit denominator and trigger policy.
- Recipe-ready, outcome-ready, SDG 3.8.2-ready, and climate-linkage-ready rows from this audit: 0.
- Current decision: `blocked_alb2002_access_need_denominator_policy_not_outcome_ready`.

## Summary

| Metric | Value | Interpretation |
|---|---:|---|
| alb2002_access_need_denominator_policy_rows | 24 | Rows in the ALB_2002 access/need denominator policy audit. |
| alb2002_access_need_household_rows | 3599 | Base household rows included in the access/need audit. |
| alb2002_access_need_person_need_household_rows | 2202 | Households with any Health A chronic/disability or sudden-illness need proxy. |
| alb2002_access_need_q01_need_rows | 3247 | Households not coded as no-one-needed-health-care in m5b_q01. |
| alb2002_access_need_q01_cost_difficulty_rows | 1623 | Households reporting very difficult or difficult payment situation among q01 need-coded households. |
| alb2002_access_need_delayed_help_rows | 144 | Households with delayed/not-sought help count above none. |
| alb2002_access_need_referral_not_gone_rows | 161 | Households with hospital referral not gone count above none. |
| alb2002_access_need_refused_service_rows | 68 | Households with any health-service refusal. |
| alb2002_access_need_medicine_discount_any_barrier_rows | 493 | Households entitled to medicine discount but not always able to exercise it. |
| alb2002_access_need_composite_cost_barrier_rows | 1661 | Composite cost-barrier candidate event rows. |
| alb2002_access_need_composite_distance_barrier_rows | 34 | Composite distance-barrier candidate event rows. |
| alb2002_access_need_composite_supply_admin_barrier_rows | 405 | Composite supply/admin-barrier candidate event rows. |
| alb2002_access_need_composite_any_access_barrier_rows | 1861 | Composite any-access-barrier candidate event rows. |
| alb2002_access_need_composite_any_access_barrier_denominator_rows | 3599 | Composite any-access-barrier candidate denominator rows. |
| alb2002_access_need_low_event_rate_rows | 3 | Candidate policies with unweighted event rate below 3 percent. |
| alb2002_access_need_questionnaire_access_rows_observed | 8 | Access rows observed upstream in the questionnaire audit. |
| alb2002_access_need_skip_missing_rows_observed | 12 | Skip/missing audit rows observed upstream. |
| alb2002_access_need_minimum_recipe_outcome_ready_observed | 0 | Outcome-ready rows observed upstream in the minimum recipe packet. |
| alb2002_access_need_climate_ready_rows_observed | 0 | Climate-linkage-ready rows observed upstream. |
| alb2002_access_need_recipe_ready_rows | 0 | Rows promoted to harmonization recipe by this audit; intentionally zero. |
| alb2002_access_need_outcome_ready_rows | 0 | Rows promoted to final outcome construction by this audit; intentionally zero. |
| alb2002_access_need_sdg382_ready_rows | 0 | Rows promoted to SDG 3.8.2 construction by this audit; intentionally zero. |
| alb2002_access_need_climate_linkage_ready_rows | 0 | Rows promoted to climate linkage by this audit; intentionally zero. |
| alb2002_access_need_current_decision | blocked_alb2002_access_need_denominator_policy_not_outcome_ready | Current fail-closed decision for ALB_2002 access/need denominator policies. |

## Candidate Denominator Policies

| policy_name | outcome_family | denominator_rows | event_rows | event_rate | weighted_event_rate | low_event_rate_flag | denominator_status | skip_path_status |
|---|---|---|---|---|---|---|---|---|
| person_any_chronic_or_sudden_need | need_denominator | 3599 | 2202 | 0.611837 | 0.63232 | 0 | person_level_need_proxy_household_aggregation_required | person_module_not_a_direct_forgone_care_denominator |
| q01_family_healthcare_need_denominator | need_denominator | 3599 | 3247 | 0.902195 | 0.908742 | 0 | household_need_denominator_candidate_no_one_needed_care_code_seen | questionnaire_skip_to_access_items_requires_policy_review |
| q01_cost_affordability_difficulty_among_need | cost_barrier | 3247 | 1623 | 0.499846 | 0.51424 | 0 | cost_affordability_denominator_candidate | broad_affordability_question_not_forgone_care_by_itself |
| money_raising_any_among_q01_difficult | coping_barrier | 1623 | 1476 | 0.909427 | 0.93036 | 0 | coping_denominator_candidate | multi_response_method_semantics_require_manual_review |
| delayed_help_any_among_q01_need | forgone_or_delayed_care | 3247 | 144 | 0.0443486 | 0.0389328 | 0 | delayed_care_denominator_candidate | count_coding_and_need_scope_require_manual_review |
| delay_reason_cost_conditional | cost_barrier | 144 | 64 | 0.444444 | 0.353882 | 0 | conditional_reason_denominator_candidate | conditional_reason_denominator_requires_trigger_policy |
| delay_reason_distance_conditional | distance_barrier | 144 | 13 | 0.0902778 | 0.114923 | 0 | conditional_reason_denominator_candidate | conditional_reason_denominator_requires_trigger_policy |
| hospital_referral_not_gone_any | forgone_or_delayed_care | 3247 | 161 | 0.0495842 | 0.0445007 | 0 | referral_nonuse_denominator_candidate | referral_need_scope_requires_manual_review |
| referral_reason_cost_conditional | cost_barrier | 161 | 102 | 0.63354 | 0.582364 | 0 | conditional_referral_reason_denominator_candidate | conditional_reason_denominator_requires_trigger_policy |
| referral_reason_distance_conditional | distance_barrier | 161 | 8 | 0.0496894 | 0.0738095 | 0 | conditional_referral_reason_denominator_candidate | conditional_reason_denominator_requires_trigger_policy |
| referral_reason_other_service_trust_conditional | supply_or_acceptability_barrier | 161 | 15 | 0.0931677 | 0.101491 | 0 | conditional_referral_reason_denominator_candidate | category_scope_requires_manual_supply_acceptability_policy |
| refused_health_services_any | forgone_or_delayed_care | 3599 | 68 | 0.0188941 | 0.0176393 | 1 | refusal_denominator_candidate | ever_refusal_scope_requires_period_policy |
| refused_reason_cost_conditional | cost_barrier | 68 | 46 | 0.676471 | 0.689873 | 0 | conditional_refusal_reason_denominator_candidate | conditional_reason_denominator_requires_trigger_policy |
| refused_reason_distance_conditional | distance_barrier | 68 | 15 | 0.220588 | 0.179077 | 0 | conditional_refusal_reason_denominator_candidate | conditional_reason_denominator_requires_trigger_policy |
| refused_reason_supply_admin_conditional | supply_or_admin_barrier | 68 | 6 | 0.0882353 | 0.112291 | 0 | conditional_refusal_reason_denominator_candidate | category_scope_requires_manual_supply_admin_policy |
| medicine_discount_entitlement | coverage_denominator | 3599 | 2044 | 0.567936 | 0.562732 | 0 | coverage_denominator_candidate_not_failure_outcome | entitlement_scope_not_a_direct_access_failure |
| medicine_discount_any_barrier | medicine_access_barrier | 2044 | 493 | 0.241194 | 0.226843 | 0 | medicine_access_denominator_candidate | discount_entitlement_and_need_scope_require_manual_review |
| medicine_discount_cost_barrier | cost_barrier | 2044 | 45 | 0.0220157 | 0.0194027 | 1 | medicine_cost_denominator_candidate | discount_entitlement_and_need_scope_require_manual_review |
| medicine_discount_supply_admin_barrier | supply_or_admin_barrier | 2044 | 390 | 0.190802 | 0.175403 | 0 | medicine_supply_admin_denominator_candidate | discount_entitlement_and_need_scope_require_manual_review |
| composite_cost_barrier_candidate | cost_barrier | 3599 | 1661 | 0.461517 | 0.476346 | 0 | composite_cost_denominator_candidate | composite_union_mixes_broad_affordability_and_conditional_reason_denominators |
| composite_distance_barrier_candidate | distance_barrier | 3599 | 34 | 0.00944707 | 0.00951398 | 1 | composite_distance_denominator_candidate | composite_union_mixes_conditional_reason_denominators |
| composite_supply_admin_barrier_candidate | supply_or_admin_barrier | 3599 | 405 | 0.112531 | 0.102979 | 0 | composite_supply_admin_denominator_candidate | composite_union_mixes_conditional_reason_denominators |
| composite_delayed_refused_nonuse_candidate | forgone_or_delayed_care | 3599 | 318 | 0.0883579 | 0.080829 | 0 | composite_nonuse_denominator_candidate | composite_union_mixes_delay_referral_and_ever_refusal_scopes |
| composite_any_access_barrier_candidate | access_failure_composite | 3599 | 1861 | 0.517088 | 0.528953 | 0 | composite_access_denominator_candidate | composite_union_too_broad_for_final_outcome_without_policy_review |

## Interpretation

- `m5b_q01` is the clearest broad household denominator candidate because it separates households where no one needed health care from households reporting the difficulty of paying for care.
- Conditional reason variables such as `m5b_q04`, `m5b_q06`, and `m5b_q08` must remain tied to their trigger variables; using them over all households would inflate denominators and understate event rates.
- Medicine-discount access is policy-relevant but conditional on entitlement and should not be treated as a general forgone-care denominator without a separate scope decision.
- The composite candidates are screening diagnostics only; they mix broad affordability, delayed care, referral, refusal, and medicine-entitlement scopes.
- Climate linkage remains separately blocked by the unresolved district-boundary/GPS evidence.

## Machine-Readable Outputs

- `temp/alb2002_access_need_denominator_policy_audit.csv`
- `result/alb2002_access_need_denominator_policy_summary.csv`
