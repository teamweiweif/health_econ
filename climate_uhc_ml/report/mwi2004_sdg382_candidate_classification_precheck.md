# Malawi 2004 SDG 3.8.2 Candidate Classification Precheck

Dataset: `MWI_2004_IHS-II_v01_M` - Malawi 2004-2005

This artifact stress-tests the candidate SDG 3.8.2 SPL bridge against Malawi
2004 raw financial inputs. It writes aggregate diagnostics only. It does not
write household-level candidate classifications to `data/`, does not update the
promotion registry, and does not open modeling gates.

Two denominator variants are shown because the external PPP/CPI bridge and the
final denominator floor rule are not accepted:

- `positive_discretionary_budget_only`: classify only rows with positive total
  consumption minus the candidate SPL.
- `floor_denominator_to_total_consumption_if_nonpositive`: sensitivity variant
  that uses total consumption where candidate discretionary budget is
  nonpositive.

## Summary

| metric | value | interpretation |
| --- | --- | --- |
| country_wave | MWI_2004_IHS-II_v01_M | Country-wave covered by the candidate SDG 3.8.2 classification precheck. |
| candidate_spl_daily_raw_2004_mwk | 87.5590037117 | Candidate SPL from the external parameter source ledger; not final. |
| household_rows | 11280 | Household rows in the internal SDG 3.8.2 frame. |
| weighted_population | 12328479.8922 | Population-weighted denominator before final SDG 3.8.2 acceptance. |
| positive_oop_household_rows | 7765 | Households with positive OOP health spending. |
| nonpositive_discretionary_budget_rows | 9073 | Rows where total consumption minus candidate SPL is nonpositive. |
| positive_discretionary_classified_rows | 2207 | Rows classified under the strict positive-discretionary-budget diagnostic variant. |
| positive_discretionary_candidate_sdg382_rows | 119 | Candidate catastrophic rows under the strict diagnostic variant. |
| positive_discretionary_candidate_sdg382_weighted_rate | 0.00902823398559 | Population-weighted candidate rate under the strict diagnostic variant. |
| floor_variant_candidate_sdg382_rows | 122 | Candidate catastrophic rows under the denominator-floor sensitivity variant. |
| floor_variant_candidate_sdg382_weighted_rate | 0.00929136456778 | Population-weighted candidate rate under the denominator-floor sensitivity variant. |
| external_ppp_source_verified | 1 | Whether PPP source candidate is captured in the external ledger. |
| external_cpi_source_verified | 1 | Whether CPI source candidates are captured in the external ledger. |
| external_parameter_bridge_accepted | 0 | Whether the external PPP/CPI/base-period bridge is accepted. |
| candidate_classification_written_to_data | 0 | No household-level candidate classification was written to data/. |
| sdg382_ready | 0 | The candidate classification precheck does not open the SDG 3.8.2 gate. |
| data_write_gate_status | closed | This precheck writes aggregate result/report artifacts only. |
| modeling_gate_status | blocked | No predictive, reduced-form, causal ML, or policy learning is opened. |

## Candidate Variants

| denominator_policy_variant | classification_status | nonpositive_discretionary_budget_rows | classified_household_rows | candidate_sdg382_household_rows | candidate_sdg382_weighted_rate | decision |
| --- | --- | --- | --- | --- | --- | --- |
| positive_discretionary_budget_only | classify_only_positive_candidate_discretionary_budget | 9073 | 2207 | 119 | 0.00902823398559 | diagnostic_only_do_not_promote |
| floor_denominator_to_total_consumption_if_nonpositive | sensitivity_variant_not_final | 9073 | 11280 | 122 | 0.00929136456778 | diagnostic_only_do_not_promote |

## Gate Decision

This precheck narrows the remaining SDG 3.8.2 work to denominator policy:
candidate PPP/CPI/SPL values are available, but the CPI/base-period bridge and
denominator floor rule are still unaccepted. Therefore `sdg382_ready` remains
`0`, `data_write_gate_status` remains `closed`, and `modeling_gate_status`
remains `blocked`.
