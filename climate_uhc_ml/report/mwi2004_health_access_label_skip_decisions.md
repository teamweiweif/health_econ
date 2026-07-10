# Malawi 2004 Health Access Label And Skip Decisions

Dataset: `MWI_2004_IHS-II_v01_M` - Malawi 2004-2005

This artifact maps health/access value labels from `sec_d.dta` into candidate
construct roles for illness/need, care-seeking, forgone care, hospitalization,
coping, chronic illness, and maternal-care context. It exports only labels,
counts, and aggregate skip metrics. It does not export raw person identifiers,
does not write to `data/`, and does not mark the wave as value-verified.

## Summary

| metric | value | interpretation |
| --- | --- | --- |
| country_wave | MWI_2004_IHS-II_v01_M | Country-wave covered by this health/access label-skip decision artifact. |
| label_decision_rows | 127 | Variable-value rows with value labels and proposed construct mappings. |
| mapping_ready_rows | 39 | Variable-value rows with an explicit mapping ready for policy review. |
| manual_review_rows | 88 | Variable-value rows still requiring manual review. |
| financial_barrier_no_money_rows | 660 | d07a/d07b rows mapped to no-money no-action candidate access failure. |
| formal_facility_care_rows | 5516 | d07a/d07b rows mapped to formal facility care. |
| informal_or_self_care_rows | 6655 | d07a/d07b rows mapped to informal/self-care actions. |
| total_skip_leakage_rows | 6 | Aggregate skip leakage across d07a/d07b/d17/d20 checks. |
| health_access_label_skip_decision | label_skip_mapping_has_skip_or_manual_review_blockers | Decision for the health/access label-skip mapping layer; still not final raw-value verification. |
| data_write_gate_status | closed | This artifact cannot write data or open modeling gates. |

## Skip Metrics

| metric | value | status | interpretation |
| --- | --- | --- | --- |
| sec_d_rows | 51292 | pass | Rows read from the health module. |
| d04_illness_injury_yes_rows | 14143 | pass | Recent illness/injury need denominator candidate. |
| d07a_nonmissing_when_d04_yes | 14105 | pass | Problem 1 action rows among recent illness/injury respondents. |
| d07b_nonmissing_when_d04_yes | 1574 | review | Problem 2 action rows among recent illness/injury respondents. |
| d07a_skip_leakage_when_d04_not_yes | 6 | blocker | Problem 1 action nonmissing outside d04==Yes. |
| d07b_skip_leakage_when_d04_not_yes | 0 | pass | Problem 2 action nonmissing outside d04==Yes. |
| care_action_no_money_rows | 660 | review | d07a/d07b rows whose value labels indicate did nothing/no money. |
| care_action_did_nothing_rows | 2012 | review | d07a/d07b rows whose value labels indicate did nothing for any reason. |
| care_action_formal_facility_rows | 5516 | review | d07a/d07b rows mapped to formal health facility care. |
| care_action_informal_or_self_care_rows | 6655 | review | d07a/d07b rows mapped to medicine purchase, traditional care, or self/informal care. |
| d15_hospitalization_yes_rows | 2051 | pass | Hospitalization need/severity candidate. |
| d17_skip_leakage_when_d15_not_yes | 0 | pass | Borrow/sell assets for hospitalization nonmissing outside d15==Yes. |
| d18_traditional_healer_overnight_yes_rows | 421 | review | Traditional healer overnight-stay candidate. |
| d20_skip_leakage_when_d18_not_yes | 0 | pass | Borrow/sell assets for traditional healer nonmissing outside d18==Yes. |
| d26_chronic_illness_yes_rows | 4918 | pass | Chronic illness need denominator candidate. |
| total_skip_leakage_rows | 6 | blocker | Aggregate skip leakage across d07a/d07b/d17/d20 checks. |

## Label Decisions

| variable_name | raw_value | value_label | raw_count | construct_mapping | proposed_indicator_use | acceptance_status |
| --- | --- | --- | --- | --- | --- | --- |
| d04 | 2 | No | 36739 | acute_illness_or_injury_need_no | candidate_negative_or_no_event_signal | mapping_ready_policy_pending |
| d04 | 1 | Yes | 14143 | acute_illness_or_injury_need_yes | candidate_denominator_or_event_signal | mapping_ready_policy_pending |
| d04 | Sysmiss | Sysmiss | 410 | acute_illness_or_injury_need_system_missing | missing_or_skip_review | requires_manual_review |
| d07a | Sysmiss | Sysmiss | 37181 | care_seeking_action_problem_1_system_missing | missing_or_skip_review | requires_manual_review |
| d07a | 9 | Went to local grocery for medicine | 5291 | informal_or_self_care_candidate | candidate_care_action_not_formal_facility | mapping_ready_policy_pending |
| d07a | 5 | Sought treatment at gvt health fac. | 4298 | formal_care_sought_candidate | candidate_care_sought_signal | mapping_ready_policy_pending |
| d07a | 1 | Did nothing, not serious | 1260 | no_care_no_serious_need_or_other_no_action_candidate | not_financial_access_failure_by_default | mapping_ready_policy_pending |
| d07a | 7 | Sought treatment atpvt health facility | 791 | formal_care_sought_candidate | candidate_care_sought_signal | mapping_ready_policy_pending |
| d07a | 2 | Did nothing, no money | 610 | forgone_care_financial_barrier_candidate | candidate_access_failure_numerator | mapping_ready_double_count_policy_pending |
| d07a | 10 | Sought treatment with trad. healer | 479 | informal_or_self_care_candidate | candidate_care_action_not_formal_facility | mapping_ready_policy_pending |
| d07a | 6 | Sought treatment at church/mission facility | 461 | care_seeking_action_problem_1_review | context_or_review_only | requires_manual_review |
| d07a | 4 | Personally known remedies | 393 | care_seeking_action_problem_1_review | context_or_review_only | requires_manual_review |
| d07a | 3 | Used medicine had in stock | 365 | informal_or_self_care_candidate | candidate_care_action_not_formal_facility | mapping_ready_policy_pending |
| d07a | 8 | Went to local pharmacy | 55 | care_seeking_action_problem_1_review | context_or_review_only | requires_manual_review |
| d07a | 11 | Sought treatment with faith healer | 54 | informal_or_self_care_candidate | candidate_care_action_not_formal_facility | mapping_ready_policy_pending |
| d07a | 12 | Other | 43 | care_seeking_action_problem_1_review | context_or_review_only | requires_manual_review |
| d07a | 13 | help from relatives/neighbours | 11 | care_seeking_action_problem_1_review | context_or_review_only | requires_manual_review |
| d07b | Sysmiss | Sysmiss | 49718 | care_seeking_action_problem_2_system_missing | missing_or_skip_review | requires_manual_review |
| d07b | 99 | No other action taken | 443 | no_second_action_candidate | secondary_action_absence | mapping_ready_policy_pending |
| d07b | 9 | Went to local grocery for medicine | 385 | informal_or_self_care_candidate | candidate_care_action_not_formal_facility | mapping_ready_policy_pending |
| d07b | 5 | Sought treatment at gvt health fac. | 354 | formal_care_sought_candidate | candidate_care_sought_signal | mapping_ready_policy_pending |
| d07b | 1 | Did nothing, not serious | 92 | no_care_no_serious_need_or_other_no_action_candidate | not_financial_access_failure_by_default | mapping_ready_policy_pending |
| d07b | 7 | Sought treatment atpvt health facility | 73 | formal_care_sought_candidate | candidate_care_sought_signal | mapping_ready_policy_pending |
| d07b | 2 | Did nothing, no money | 50 | forgone_care_financial_barrier_candidate | candidate_access_failure_numerator | mapping_ready_double_count_policy_pending |
| d07b | 6 | Sought treatment at church/mission facility | 45 | care_seeking_action_problem_2_review | context_or_review_only | requires_manual_review |
| d07b | 10 | Sought treatment with trad. healer | 41 | informal_or_self_care_candidate | candidate_care_action_not_formal_facility | mapping_ready_policy_pending |
| d07b | 4 | Personally known remedies | 38 | care_seeking_action_problem_2_review | context_or_review_only | requires_manual_review |
| d07b | 3 | Used medicine had in stock | 36 | informal_or_self_care_candidate | candidate_care_action_not_formal_facility | mapping_ready_policy_pending |
| d07b | 12 | Other | 7 | care_seeking_action_problem_2_review | context_or_review_only | requires_manual_review |
| d07b | 8 | Went to local pharmacy | 5 | care_seeking_action_problem_2_review | context_or_review_only | requires_manual_review |
| d07b | 11 | Sought treatment with faith healer | 4 | informal_or_self_care_candidate | candidate_care_action_not_formal_facility | mapping_ready_policy_pending |
| d07b | 13 | help from relatives/neighbours | 1 | care_seeking_action_problem_2_review | context_or_review_only | requires_manual_review |
| d08 | Sysmiss | Sysmiss | 37180 | activity_limitation_from_recent_need_system_missing | missing_or_skip_review | requires_manual_review |
| d08 | 1 | Yes | 7838 | activity_limitation_from_recent_need_review | context_or_review_only | requires_manual_review |
| d08 | 2 | No | 6274 | activity_limitation_from_recent_need_review | context_or_review_only | requires_manual_review |
| d10 | Sysmiss | Sysmiss | 43506 | other_household_member_activity_limitation_system_missing | missing_or_skip_review | requires_manual_review |
| d10 | 2 | No | 4406 | other_household_member_activity_limitation_review | context_or_review_only | requires_manual_review |
| d10 | 1 | Yes | 3380 | other_household_member_activity_limitation_review | context_or_review_only | requires_manual_review |
| d15 | 2 | No | 48835 | hospitalization_need_last_12_months_no | candidate_negative_or_no_event_signal | mapping_ready_policy_pending |
| d15 | 1 | Yes | 2051 | hospitalization_need_last_12_months_yes | candidate_denominator_or_event_signal | mapping_ready_policy_pending |
| d15 | Sysmiss | Sysmiss | 406 | hospitalization_need_last_12_months_system_missing | missing_or_skip_review | requires_manual_review |
| d17 | Sysmiss | Sysmiss | 49365 | hospitalization_financing_coping_system_missing | missing_or_skip_review | requires_manual_review |
| d17 | 2 | No | 1469 | borrow_sell_assets_for_health_cost_no | candidate_no_coping_signal | mapping_ready_policy_pending |
| d17 | 1 | Yes | 458 | borrow_sell_assets_for_health_cost_yes | candidate_financial_coping_signal | mapping_ready_policy_pending |
| d18 | 2 | No | 50488 | traditional_healer_overnight_stay_no | candidate_negative_or_no_event_signal | mapping_ready_policy_pending |
| d18 | 1 | Yes | 421 | traditional_healer_overnight_stay_yes | candidate_denominator_or_event_signal | mapping_ready_policy_pending |
| d18 | Sysmiss | Sysmiss | 383 | traditional_healer_overnight_stay_system_missing | missing_or_skip_review | requires_manual_review |
| d20 | Sysmiss | Sysmiss | 50877 | traditional_healer_financing_coping_system_missing | missing_or_skip_review | requires_manual_review |
| d20 | 2 | No | 230 | borrow_sell_assets_for_health_cost_no | candidate_no_coping_signal | mapping_ready_policy_pending |
| d20 | 1 | Yes | 185 | borrow_sell_assets_for_health_cost_yes | candidate_financial_coping_signal | mapping_ready_policy_pending |
| d21 | 3 | about the same | 17904 | self_rated_health_change_review | context_or_review_only | requires_manual_review |
| d21 | 1 | much better | 17782 | self_rated_health_change_review | context_or_review_only | requires_manual_review |
| d21 | 2 | somewhat better | 9469 | self_rated_health_change_review | context_or_review_only | requires_manual_review |
| d21 | 4 | somewhat worse | 3659 | self_rated_health_change_review | context_or_review_only | requires_manual_review |
| d21 | 6 | child less than 1 year old | 1533 | self_rated_health_change_review | context_or_review_only | requires_manual_review |
| d21 | Sysmiss | Sysmiss | 583 | self_rated_health_change_system_missing | missing_or_skip_review | requires_manual_review |
| d21 | 5 | much worse | 362 | self_rated_health_change_review | context_or_review_only | requires_manual_review |
| d26 | 2 | No | 45961 | chronic_illness_need_no | candidate_negative_or_no_event_signal | mapping_ready_policy_pending |
| d26 | 1 | Yes | 4918 | chronic_illness_need_yes | candidate_denominator_or_event_signal | mapping_ready_policy_pending |
| d26 | Sysmiss | Sysmiss | 413 | chronic_illness_need_system_missing | missing_or_skip_review | requires_manual_review |
| ... | ... | ... | ... | ... | ... | ... |

## Gate Decision

The label/skip layer is ready for policy review, but final health/access
verification remains blocked until person-join exceptions, double-counting of
`d07a`/`d07b`, formal-vs-informal care grouping, maternal module inclusion, and
missing/unit/recall rules are accepted.
