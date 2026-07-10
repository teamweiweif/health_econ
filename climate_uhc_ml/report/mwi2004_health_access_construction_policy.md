# Malawi 2004 Health Access Construction Policy

Dataset: `MWI_2004_IHS-II_v01_M` - Malawi 2004-2005

This artifact proposes a candidate construction policy for acute illness,
care-seeking, no-money forgone care, provider grouping, and health-cost coping
using `sec_d.dta`. It exports only aggregate counts and rules. It does not
write person-level data and does not final-verify the health/access gate.

## Summary

| metric | value | interpretation |
| --- | --- | --- |
| country_wave | MWI_2004_IHS-II_v01_M | Country-wave covered by this health/access construction policy. |
| analytic_roster_matched_health_rows | 51286 | Candidate analytic person rows in sec_d matched to individual roster. |
| acute_need_denominator_rows | 14143 | Roster-matched d04==Yes rows. |
| financial_barrier_forgone_care_rows | 631 | Candidate no-money forgone-care rows counted once per person row. |
| formal_care_core_rows | 5130 | Candidate government/private facility care rows. |
| formal_care_extended_rows | 5593 | Candidate formal care rows adding church/mission facility. |
| informal_or_self_care_rows | 6282 | Candidate informal/self-care context rows. |
| d07a_d07b_skip_exception_rows | 6 | d07a/d07b nonmissing rows outside d04==Yes under roster-matched candidate universe. |
| no_second_action_only_rows | 443 | Rows with d07b indicating no other action taken among acute-need rows. |
| hospitalization_need_rows | 2051 | Roster-matched d15==Yes rows. |
| hospitalization_coping_rows | 458 | Roster-matched d15==Yes and d17==Yes rows. |
| traditional_healer_need_rows | 421 | Roster-matched d18==Yes rows. |
| traditional_healer_coping_rows | 185 | Roster-matched d18==Yes and d20==Yes rows. |
| chronic_need_context_rows | 4918 | Roster-matched d26==Yes rows. |
| construction_policy_status | candidate_policy_ready_active_skip_and_provider_blockers | Policy is explicit enough for review but not final verification. |
| final_health_access_verified | 0 | Health/access construct is not final verified. |
| data_write_gate_status | closed | No promoted data may be written from this policy artifact. |

## Candidate Policy Components

| policy_component | candidate_rule | aggregate_count | acceptance_status | remaining_blocker |
| --- | --- | --- | --- | --- |
| analytic_person_universe | Keep health rows with case_id+memid present in ihs2_individ.dta; do not export raw IDs. | 51286 | candidate_policy_ready_exception_documentation_pending | Need formal exception policy for 6 nonroster health rows and 2 roster-only health absences. |
| acute_need_denominator | Recent illness/injury need equals d04==Yes among roster-matched health rows. | 14143 | candidate_policy_ready_skip_exception_pending | Need accepted rule for 6 d07a skip-leakage rows outside d04==Yes. |
| financial_barrier_forgone_care | Financial access failure candidate equals any d07a/d07b value labeled Did nothing, no money among acute-need rows. | 631 | candidate_policy_ready_double_count_policy_pending | Need final double-count and missing-action policy before access outcome promotion. |
| nonfinancial_no_action_context | Nonfinancial no-action context equals any d07a/d07b value labeled Did nothing, not serious among acute-need rows. | 1325 | candidate_context_policy_ready | Need final decision whether this remains context only or becomes nonfinancial access barrier. |
| formal_care_core | Core formal care equals government or private health facility in d07a/d07b among acute-need rows. | 5130 | candidate_policy_ready_provider_grouping_pending | Need accepted provider grouping for church/mission facility, pharmacy, and traditional healer. |
| formal_care_extended_sensitivity | Extended formal care adds church/mission facility to government/private facilities. | 5593 | candidate_sensitivity_policy_ready | Need final provider grouping decision. |
| informal_or_self_care_context | Informal/self-care context includes medicine in stock, grocery medicine, traditional healer, and faith healer among acute-need rows. | 6282 | candidate_context_policy_ready | Need final formal/informal grouping decision. |
| hospitalization_coping_context | Hospitalization cost-coping context equals d15==Yes and d17==Yes. | 458 | candidate_context_policy_ready | Need final decision whether coping is context, mechanism, or severity outcome. |
| traditional_healer_coping_context | Traditional-healer cost-coping context equals d18==Yes and d20==Yes. | 185 | candidate_context_policy_ready | Need final decision whether traditional-healer care is access, informal care, or context only. |
| chronic_need_context | Chronic need context equals d26==Yes among roster-matched health rows. | 4918 | candidate_context_policy_ready | Need final decision whether chronic need enters double-failure denominator. |
| documented_skip_exceptions | Document skip exceptions without repairing raw values: d07a leakage outside d04==Yes remains excluded and flagged. | 6 | blocking_exception_policy_required | Need accepted skip-leakage exclusion/repair rule before health/access final verification. |

## Gate Decision

The construction policy is explicit enough for review, but not final. Active
blockers remain: the 6 `d07a` skip-exception rows outside `d04==Yes`, provider
grouping for church/mission/pharmacy/traditional care, double-count treatment
across `d07a` and `d07b`, and the roster/health person-key exceptions.
