# Malawi 2004 SDG 3.8.2 SPL Bridge Verification Gate

Dataset: `MWI_2004_IHS-II_v01_M` - Malawi 2004-2005

This verifier narrows the Malawi 2004 SDG 3.8.2 blocker. The current UNSD
metadata formula and the World Bank WDI source values for 2017 private
consumption PPP, 2004 CPI, and 2017 CPI are revalidated. The candidate SPL is
also reproducible.

The gate remains closed because the raw survey `price_index` context identifies
the real-currency base as national February/March 2004, while the candidate
bridge uses annual CPI 2004. Without a documented base-period reconciliation or
an official accepted Malawi SDG 3.8.2 production source, the local-currency SPL
cannot be accepted for a promoted household-level SDG 3.8.2 field.

## Summary

| metric | value | interpretation |
| --- | --- | --- |
| country_wave | MWI_2004_IHS-II_v01_M | Country-wave covered by the SPL bridge verification gate. |
| official_metadata_last_update | 2026-03-27 | Official UNSD SDG 3.8.2 metadata version checked for the formula. |
| world_bank_api_revalidation_date | 2026-07-10 | Date the PPP/CPI source values were rechecked against the official World Bank API. |
| wdi_ppp_private_consumption_2017_api_match | 1 | Ledger private-consumption PPP value matches the official World Bank API value. |
| wdi_cpi_2004_api_match | 1 | Ledger 2004 CPI value matches the official World Bank API value. |
| wdi_cpi_2017_api_match | 1 | Ledger 2017 CPI value matches the official World Bank API value. |
| source_parameters_revalidated | 1 | All three external source values match the official API values used by the ledger. |
| candidate_cpi_ratio_recomputed | 1 | The annual CPI 2017/2004 ratio is reproducible from source values. |
| candidate_local_currency_spl_recomputed | 1 | The candidate local-currency SPL is reproducible from PPP, CPI ratio, and SPL formula. |
| candidate_spl_2017_ppp | 2.15 | Candidate SPL in 2017 PPP international dollars per person per day. |
| candidate_spl_daily_raw_2004_mwk | 87.5590037117 | Candidate local-currency SPL in survey raw real 2004 MWK per person per day. |
| survey_povline_daily_raw_2004_mwk | 44.2877 | Survey national poverty-line context; not the official SDG SPL by itself. |
| candidate_spl_to_survey_povline_ratio | 1.97705014511 | Diagnostic ratio between candidate SDG SPL and survey poverty-line context. |
| survey_price_index_base_status | national_february_march_2004_base | Base-period evidence from the raw price_index label. |
| annual_cpi_bridge_base_period_accepted | 0 | Whether annual CPI is accepted as a final bridge to the survey real-currency base. |
| nonpositive_discretionary_budget_rows | 9073 | Rows with nonpositive discretionary budget under the candidate SPL. |
| official_rule_candidate_sdg382_rows | 6437 | Aggregate candidate SDG 3.8.2 rows under the official nonpositive rule and candidate SPL. |
| external_parameter_bridge_accepted | 0 | The PPP/CPI source values are verified, but the survey-base bridge is not accepted. |
| local_currency_spl_accepted | 0 | The local-currency SPL remains candidate. |
| sdg382_ready | 0 | Malawi 2004 SDG 3.8.2 remains blocked. |
| registry_sdg382_status | blocked_spl_base_period_bridge_not_accepted_ppp_cpi_values_revalidated | More precise registry blocker after this verifier. |
| data_write_gate_status | closed | No household-level SDG 3.8.2 data are written. |
| modeling_gate_status | blocked | No predictive, reduced-form, causal ML, or policy learning is opened. |

## Gate Components

| component | status | value | decision | remaining_blocker |
| --- | --- | --- | --- | --- |
| official_sdg382_formula | verified_current_metadata | SPL=max(2.15, 1.15 + 0.50 * median excluding OOP), 2017 PPP per capita daily | official_formula_verified |  |
| world_bank_ppp_private_consumption_2017 | source_value_revalidated | 249.104888916 | use_as_candidate_ppp_concept | PPP concept still remains tied to the bridge policy; source value itself is verified. |
| world_bank_cpi_annual_values | source_values_revalidated | cpi_2004=55.6247640619; cpi_2017=340.242124548 | annual_cpi_values_verified | Annual CPI values are verified, but annual CPI does not by itself verify the survey real-currency base. |
| candidate_cpi_ratio | formula_recomputed | 6.11673829608 | candidate_ratio_reproducible | Reproducible ratio is still only a candidate because the survey deflator base is February/March 2004. |
| candidate_spl_2017_ppp | ipl_binds_relative_formula | 2.15 | candidate_spl_2017_ppp_reproducible | 2017 PPP SPL is reproducible, but local-currency conversion remains candidate. |
| candidate_spl_local_currency | formula_recomputed_candidate_not_accepted | 87.5590037117 | candidate_local_currency_spl_not_accepted | The local-currency SPL depends on the annual CPI bridge; do not promote SDG 3.8.2 yet. |
| survey_real_currency_base | base_period_mismatch_blocks_bridge | 86.1-128.6 | annual_cpi_bridge_not_accepted | The raw survey price index is explicitly based at national February/March 2004; annual CPI 2004 is too coarse to acce... |
| candidate_classification_scale | aggregate_stress_test_only | official_rule_candidate_rows=6437 | do_not_write_household_sdg382 | Candidate classification is sensitive to the unaccepted local-currency SPL bridge. |
| final_bridge_gate | fail_closed | sdg382_ready=0 | block_sdg382_until_survey_base_period_bridge_is_documented | Need a documented conversion from the survey's February/March 2004 real MWK base to 2017 PPP terms, or an official ac... |

## Decision

`source_parameters_revalidated=1`, but
`annual_cpi_bridge_base_period_accepted=0`, `local_currency_spl_accepted=0`,
`sdg382_ready=0`, `data_write_gate_status=closed`, and
`modeling_gate_status=blocked`.
