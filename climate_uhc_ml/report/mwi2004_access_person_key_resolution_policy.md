# Malawi 2004 Access Person-Key Resolution Policy

Dataset: `MWI_2004_IHS-II_v01_M` - Malawi 2004-2005

This artifact resolves the health-module person-key and skip-exception policy
for one narrow access construct: acute need (`d04==Yes`) and cost-barrier
forgone care (`d07a==2` or `d07b==2`) among roster-matched `sec_d` person rows.

It exports only aggregate evidence. Raw person IDs are not written.

## Summary

| metric | value | interpretation |
| --- | --- | --- |
| country_wave | MWI_2004_IHS-II_v01_M | Country-wave covered by this access/person-key resolution policy. |
| access_resolution_status | access_person_keys_and_cost_barrier_forgone_care_verified_with_documented_exclusions | Final access/person-key resolution decision for the stated cost-barrier forgone-care scope. |
| person_key_policy_final_verified_for_access | 1 | Whether person-key exceptions are accepted for the stated access outcome scope. |
| health_access_final_verified | 1 | Whether acute need and cost-barrier forgone care are raw-value verified under the documented exclusion policy. |
| access_forgone_care_inputs_ready | 1 | Whether Malawi 2004 can be counted as access/forgone-care ready for the stated cost-barrier outcome. |
| analytic_roster_matched_health_rows | 51286 | sec_d rows matched to the individual roster. |
| health_person_unmatched_to_roster | 6 | Health-module person keys excluded from the access universe; raw IDs not exported. |
| roster_person_unmatched_to_health | 2 | Roster person keys with no health-module observation; no access outcome is imputed. |
| nonroster_d04_yes_rows | 0 | Nonroster health rows with acute illness/injury need. |
| nonroster_no_money_rows | 0 | Nonroster health rows with no-money access action. |
| acute_need_denominator_rows | 14143 | Roster-matched d04==Yes rows. |
| cost_barrier_forgone_care_rows | 631 | Roster-matched acute-need rows with any no-money no-action label, counted once. |
| all_health_cost_barrier_rows | 631 | All sec_d d04==Yes rows with no-money label; used to show exclusions do not change the no-money count. |
| d07a_d07b_skip_exception_rows | 6 | Nonmissing d07a/d07b values outside d04==Yes under the roster-matched universe. |
| d07a_d07b_skip_exception_no_money_rows | 0 | Skip-exception rows carrying the no-money value; must be zero for accepted exclusion. |
| d07a_skip_exception_labels | 5=Sought treatment at gvt health fac.; 6=Sought treatment at church/mission facility; 9=Went to local grocery for medicine | Aggregate value-label evidence for excluded d07a skip exceptions. |
| formal_care_core_rows | 5130 | Government/private facility care rows among acute-need universe. |
| formal_care_extended_rows | 5593 | Government/private/church/mission care rows among acute-need universe. |
| label_manual_review_rows | 88 | Health/access label rows still requiring review outside the promoted cost-barrier rule. |
| data_write_gate_status | closed | This policy verifies an input requirement but does not write promoted data. |

## Policy Components

| policy_component | aggregate_count | accepted_rule | final_verification_decision | remaining_caveat |
| --- | --- | --- | --- | --- |
| analytic_access_person_universe | 51286 | Use only sec_d person rows whose case_id+memid appears in ihs2_individ.dta. | raw_value_verified_for_access_person_universe_with_documented_exclusions | Six nonroster health rows and two roster-only rows are excluded from person-level access outcomes; raw IDs are not exported. |
| nonroster_health_rows | 6 | Exclude nonroster health rows from person-level access outcomes and report them as documented exclusions. | documented_exclusion_accepted_for_access_scope | This does not prove full roster-module reconciliation for every possible health construct. |
| roster_only_rows | 2 | Do not impute health need or access outcomes for roster persons absent from sec_d. | documented_exclusion_accepted_for_access_scope | This is a no-imputation rule, not evidence of no illness or no forgone care. |
| acute_need_denominator | 14143 | Define acute health need as d04==1 among roster-matched sec_d rows. | raw_value_verified_for_acute_need_denominator | Chronic need and hospitalization are context/mechanism only unless separately promoted. |
| cost_barrier_forgone_care | 631 | Among roster-matched d04==1 rows, count a person once if d07a==2 or d07b==2. | raw_value_verified_for_cost_barrier_forgone_care | This verifies cost-barrier forgone care, not distance/supply access barriers. |
| d07a_d07b_skip_exceptions | 6 | Do not repair d07a/d07b values outside d04==1; exclude them from the acute-need denominator and report the leakage. | documented_exclusion_accepted_for_access_scope | Excluded leakage rows are not used to repair access outcomes; their presence remains a survey-quality caveat. |
| provider_grouping_context | 5130 | Use government/private facilities as core formal care; add church/mission as an extended sensitivity. | context_grouping_documented_not_required_for_cost_barrier_gate | Provider grouping is context/sensitivity here and does not change the cost-barrier forgone-care numerator. |

## Gate Decision

Status: `access_person_keys_and_cost_barrier_forgone_care_verified_with_documented_exclusions`.

This verifies the Malawi 2004 access/forgone-care input for the stated
cost-barrier outcome only. It does not verify SDG 3.8.2, distance or supply
barrier outcomes, a CHIRPS/ERA5 climate route, or promoted data synthesis.
Therefore the data-write gate remains closed.
