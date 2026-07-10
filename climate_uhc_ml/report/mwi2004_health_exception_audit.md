# Malawi 2004 Health Exception Audit

Dataset: `MWI_2004_IHS-II_v01_M` - Malawi 2004-2005

This audit checks whether the health-module person-key exception and the
health/access skip exception are the same aggregate issue. It exports no
`case_id`, `memid`, or row-level raw identifiers.

## Summary

| metric | value | interpretation |
| --- | --- | --- |
| country_wave | MWI_2004_IHS-II_v01_M | Country-wave covered by this health exception audit. |
| health_module_rows | 51292 | Rows in sec_d.dta read for aggregate exception audit. |
| health_person_unmatched_to_roster | 6 | Health-module person keys absent from roster; raw IDs are not exported. |
| roster_person_unmatched_to_health | 2 | Roster person keys absent from health module; raw IDs are not exported. |
| d07a_skip_leakage_rows | 6 | d07a nonmissing rows where d04 is not Yes. |
| d07a_skip_leakage_overlap_with_unmatched_health_rows | 0 | d07a leakage rows that are also absent from the roster. |
| d07a_skip_leakage_explained_by_nonroster_rows | 0 | Whether all d07a leakage is exactly concentrated in nonroster health rows. |
| other_skip_leakage_rows | 0 | Combined d07b, d17, and d20 leakage rows. |
| exception_policy_status | policy_pending_exception_unresolved | Exception status; still not final verification. |
| data_write_gate_status | closed | This exception audit cannot write promoted data. |

## Exception Checks

| exception_domain | exception_check | exception_count | overlap_count | decision_status | promotion_effect | remaining_blocker |
| --- | --- | --- | --- | --- | --- | --- |
| person_key_join | health_module_person_keys_absent_from_roster | 6 | 0 | exception_requires_review | can_support_exclusion_policy_but_not_final_verification | Need documented policy for excluding or reconciling health rows absent from the individual roster. |
| person_key_join | roster_person_keys_absent_from_health_module | 2 | 0 | minor_roster_health_absence_review | does_not_block_financial_outcomes_but_blocks_full_double_failure_acceptance | Need policy for roster persons with no health module row before person-level access denominator finalization. |
| skip_consistency | d07a_nonmissing_when_d04_not_yes | 6 | 0 | skip_leakage_requires_review | can_support_d07a_skip_leakage_resolution_if_nonroster_rows_are_excluded | d07a skip leakage cannot be treated as resolved until the nonroster-row policy is accepted. |
| skip_consistency | d07b_nonmissing_when_d04_not_yes | 0 | 0 | pass_no_exception_detected | supports_health_access_skip_rule |  |
| skip_consistency | d17_nonmissing_when_d15_not_yes | 0 | 0 | pass_no_exception_detected | supports_financial_coping_skip_rule |  |
| skip_consistency | d20_nonmissing_when_d18_not_yes | 0 | 0 | pass_no_exception_detected | supports_financial_coping_skip_rule |  |

## Gate Decision

The health-module person-key exception and the `d07a` skip-leakage
exception are separate aggregate issues. The `d07a` leakage is not explained by
nonroster health rows, so both the person-key exception and skip-rule exception
remain active blockers. Final verification remains blocked until both are
resolved or documented under an accepted construction rule.
