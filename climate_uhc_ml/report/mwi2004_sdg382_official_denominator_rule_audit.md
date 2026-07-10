# Malawi 2004 SDG 3.8.2 Official Denominator Rule Audit

Dataset: `MWI_2004_IHS-II_v01_M` - Malawi 2004-2005

This artifact resolves one narrow SDG 3.8.2 blocker: the official denominator
rule for households whose discretionary budget is nonpositive. The UNSD
metadata says that when household consumption or income is below the societal
poverty line, discretionary budget is negative, so any positive OOP health
expenditure exceeds a nonpositive 40 percent discretionary-budget threshold.

Official source: https://unstats.un.org/sdgs/metadata/files/Metadata-03-08-02.pdf

This does **not** promote Malawi 2004 SDG 3.8.2. The Malawi local-currency SPL
still depends on a candidate PPP/CPI/base-period bridge, so the classification
below is an aggregate stress test only. No household-level SDG 3.8.2 field is
written to `data/`, and modeling remains blocked.

## Summary

| metric | value | interpretation |
| --- | --- | --- |
| country_wave | MWI_2004_IHS-II_v01_M | Country-wave covered by the official denominator rule audit. |
| official_metadata_last_update | 2026-03-27 | Date printed in the current UNSD SDG 3.8.2 metadata file. |
| official_metadata_url | https://unstats.un.org/sdgs/metadata/files/Metadata-03-08-02.pdf | Primary source used for the denominator rule. |
| official_negative_discretionary_rule_verified | 1 | Official metadata verifies that any positive OOP exceeds a nonpositive 40 percent discretionary-budget threshold. |
| official_denominator_rule_accepted | 1 | The denominator rule is accepted as official; parameter conversion remains separate. |
| candidate_spl_daily_raw_2004_mwk | 87.5590037117 | Candidate local-currency SPL inherited from the external parameter ledger. |
| household_rows | 11280 | Household rows in the internal Malawi SDG 3.8.2 frame. |
| weighted_population | 12328479.8922 | Population-weighted denominator for the aggregate stress test. |
| positive_oop_household_rows | 7765 | Households with positive OOP health expenditure. |
| nonpositive_discretionary_budget_rows | 9073 | Rows where total consumption minus the candidate SPL is nonpositive. |
| positive_oop_nonpositive_discretionary_rows | 6318 | Rows classified by the official nonpositive-discretionary rule under the candidate SPL. |
| positive_oop_nonpositive_discretionary_weighted_population | 7798985.95653 | Weighted population classified through the nonpositive-discretionary rule. |
| positive_discretionary_candidate_sdg382_rows | 119 | Candidate catastrophic rows among households with positive discretionary budget. |
| positive_discretionary_candidate_sdg382_weighted_population | 111304.401154 | Weighted population classified among positive-discretionary rows. |
| official_rule_candidate_sdg382_rows | 6437 | Aggregate candidate classification using the official denominator rule plus candidate SPL. |
| official_rule_candidate_sdg382_weighted_population | 7910290.35768 | Weighted population for the official-rule candidate classification. |
| official_rule_candidate_sdg382_weighted_rate | 0.641627388522 | Population-weighted candidate SDG 3.8.2 rate; not final. |
| external_parameter_bridge_accepted | 0 | Whether the PPP/CPI/base-period bridge is accepted for final SDG 3.8.2. |
| candidate_classification_written_to_data | 0 | No household-level candidate SDG 3.8.2 classification was written to data/. |
| sdg382_ready | 0 | The SDG 3.8.2 gate stays closed until the local-currency SPL bridge is accepted. |
| data_write_gate_status | closed | This audit writes only aggregate result/report artifacts. |
| modeling_gate_status | blocked | No predictive, reduced-form, causal ML, or policy learning is opened. |

## Audit Components

| component | status | value | decision | remaining_blocker |
| --- | --- | --- | --- | --- |
| official_negative_or_nonpositive_discretionary_rule | source_verified | accept_any_positive_oop_when_discretionary_budget_is_nonpositive | official_denominator_rule_accepted | None for this denominator rule. |
| candidate_spl_bridge_status | blocked | 87.5590037117 | candidate_spl_not_final | Accept the PPP concept and CPI/base-period bridge before final SDG 3.8.2 classification. |
| nonpositive_discretionary_bucket | computed_from_candidate_spl | 9073 | candidate_diagnostic_only | Bucket size depends on the candidate local-currency SPL bridge. |
| positive_discretionary_bucket | computed_from_candidate_spl | 2207 | candidate_diagnostic_only | Positive-discretionary classification is still tied to the candidate SPL bridge. |
| official_rule_candidate_classification | aggregate_stress_test | 6437 | do_not_write_household_classification | Classification remains candidate because the local-currency SPL bridge is not accepted. |
| gate_decision | fail_closed | sdg382_ready=0 | keep_data_write_closed_and_modeling_blocked | Resolve the CPI/base-period and PPP/SPL bridge before promoting SDG 3.8.2. |

## Gate Decision

`official_denominator_rule_accepted=1`, but
`external_parameter_bridge_accepted=0`, `candidate_classification_written_to_data=0`,
`sdg382_ready=0`, `data_write_gate_status=closed`, and
`modeling_gate_status=blocked`.
