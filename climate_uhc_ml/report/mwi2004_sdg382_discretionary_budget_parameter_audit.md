# Malawi 2004 SDG 3.8.2 Discretionary-Budget Parameter Audit

Dataset: `MWI_2004_IHS-II_v01_M` - Malawi 2004-2005

This artifact updates the Malawi 2004 SDG 3.8.2 gate to the current official
metadata definition: positive household OOP health expenditure exceeding 40% of
household discretionary budget. The discretionary budget is total household
consumption or income minus the societal poverty line (SPL).

It does not construct the final SDG 3.8.2 indicator, does not write `data/`,
and does not open modeling gates. It separates raw internal readiness from the
still-missing external PPP/CPI/SPL parameter lock.

Official metadata source: `https://unstats.un.org/sdgs/metadata/files/Metadata-03-08-02.pdf`; last update:
`2026-03-27`.

## Summary

| metric | value | interpretation |
| --- | --- | --- |
| country_wave | MWI_2004_IHS-II_v01_M | Country-wave covered by the SDG 3.8.2 parameter audit. |
| official_metadata_url | https://unstats.un.org/sdgs/metadata/files/Metadata-03-08-02.pdf | Official UNSD SDG metadata PDF used for current indicator definition. |
| official_metadata_last_update | 2026-03-27 | Last update date recorded in the official SDG 3.8.2 metadata. |
| official_sdg382_series | SH_OOP_XPD_EARNNET40 | Official SDG 3.8.2 series code in the current metadata. |
| official_threshold_discretionary_budget | 0.40 | OOP health expenditure threshold over household discretionary budget. |
| household_rows_with_internal_sdg382_inputs | 11280 | Rows with case_id, positive weight, positive household size, positive total consumption, and nonmissing OOP. |
| positive_oop_household_rows | 7765 | Households with positive OOP health expenditure; official numerator requires positive OOP. |
| weighted_population_internal_universe | 1.23285e+07 | Population-weighted denominator before final SDG 3.8.2 parameterization. |
| weighted_median_daily_total_consumption_pc_raw | 42.6362 | Diagnostic raw-currency daily per-capita median total consumption. |
| weighted_median_daily_consumption_excluding_oop_pc_raw | 41.9651 | Diagnostic raw-currency median needed for the relative SPL formula after PPP/CPI conversion. |
| survey_povline_rows | 11280 | Rows with survey poverty-line context; not the final official 2026 SPL by itself. |
| price_index_rows | 11280 | Rows with survey spatial/temporal price index context. |
| raw_internal_sdg382_inputs_complete | 1 | OOP, total consumption, household size, and population weights are present for the internal SDG 3.8.2 frame. |
| external_ppp_cpi_parameters_verified | 0 | Official 2017 PPP and CPI/deflator bridge have not been frozen in project artifacts. |
| spl_local_currency_verified | 0 | Societal poverty line in Malawi survey local currency is not yet accepted. |
| sdg382_ready | 0 | SDG 3.8.2 remains blocked by external parameter and SPL verification. |
| data_write_gate_status | closed | This audit writes no promoted data and does not alter the existing promoted Malawi dataset. |
| modeling_gate_status | blocked | No predictive, reduced-form, causal ML, or policy learning is opened by this parameter audit. |

## Audit Rows

| component | status | aggregate_evidence | decision | remaining_blocker |
| --- | --- | --- | --- | --- |
| official_indicator_definition | source_checked_current_2026_metadata | last_update=2026-03-27; series=SH_OOP_XPD_EARNNET40; threshold=0.40; denominator=household_discretionary_budget | use_current_40pct_discretionary_budget_definition_for_sdg382_gate |  |
| oop_health_expenditure | raw_internal_input_complete | label=Health(real) Annual HH exp; nonmissing_rows=11280; positive_oop_rows=7765; positive_oop_percent=68.8387 | oop_health_input_ready_for_parameterized_sdg382_test | Need final 2017 PPP/CPI/SPL parameterization before SDG 3.8.2 indicator can be accepted. |
| total_consumption_or_income | raw_internal_input_complete | label=Total Annual HH exp; positive_total_consumption_rows=11280; weighted_median_daily_total_pc_raw=42.6362 | consumption_welfare_input_ready_for_parameterized_sdg382_test | Confirm real-currency base and 2017 PPP/CPI conversion before final SPL local-currency mapping. |
| household_size_population_weight | raw_internal_input_complete | hhsize_label=HH Size (based on hh members b08, see IHS2_individ.dta); hhwght_label=IHS2 HH weight; analytic_household... | person_weighting_input_ready_for_aggregate_sdg382_rate_after_parameter_lock | No person-level SDG 3.8.2 rate should be published until the denominator parameter policy is accepted. |
| consumption_excluding_oop_for_spl_median | raw_internal_derivation_complete | weighted_median_daily_consumption_excluding_oop_pc_raw=41.9651; nonpositive_excluding_oop_rows=0 | median_component_ready_but_currency_conversion_missing | Need verified conversion from survey real local currency to 2017 PPP international dollars before SPL can be final. |
| survey_poverty_line_context | diagnostic_context_not_official_spl | label=Poverty Line MK pp pa; nonmissing_rows=11280; weighted_median_daily_povline_pc_raw=44.2877; daily_range_raw=44.... | use_as_context_only_not_sdg382_spl | Official 2026 SDG 3.8.2 SPL is max(2017 IPL, relative SPL formula), not the survey national poverty line by itself. |
| survey_price_index_context | diagnostic_context_not_complete_cpi_bridge | label=Spatial and temporal deflator with base national February/March 2004; nonmissing_rows=11280; observed_range=86.... | use_as_context_only_until_cpi_ppp_bridge_is_documented | Need locked conversion from February/March 2004 real local currency to 2017 PPP terms. |
| external_2017_ppp_parameter | blocked_external_parameter_not_verified | not_stored_in_project_artifacts | sdg382_not_ready | Fetch, source, and freeze the official 2017 PPP conversion factor appropriate for household consumption/income. |
| external_cpi_or_deflator_bridge | blocked_external_parameter_not_verified | not_stored_in_project_artifacts | sdg382_not_ready | Fetch, source, and freeze the CPI/deflator bridge consistent with rexpagg/rexp_cat06 real currency base. |
| official_spl_local_currency | blocked_until_ppp_cpi_policy_locked | median_excluding_oop_raw_available=41.9651; ppp_verified=0; cpi_bridge_verified=0 | sdg382_not_ready | Cannot compute final SPL in Malawi survey local currency until PPP and CPI/deflator parameters are verified. |
| sdg382_indicator_final | blocked_external_parameters | raw_internal_inputs_complete=1; external_ppp_cpi_parameters_verified=0; spl_verified=0 | keep_sdg382_ready_0 | Do not mark SDG 3.8.2 ready until current 2026 metadata parameters are frozen and the final population-weighted 40% d... |

## Gate Decision

Malawi 2004 has the internal raw ingredients needed to parameterize SDG 3.8.2:
OOP health expenditure, total consumption, household size, and population
weights. It remains fail-closed because the official 2017 PPP conversion, the
CPI/deflator bridge from the survey real-currency base to 2017, and the final
SPL local-currency parameter are not yet verified in project artifacts.
