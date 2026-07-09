# Data Dictionary

## state_policy_month.parquet
Rows: 5049. Columns: 28.
- `state`: object
- `state_abbr`: object
- `state_fips`: object
- `pre2024_medicaid_child_12mo_ce`: int64
- `pre2024_chip_child_12mo_ce`: float64
- `pre2024_any_child_12mo_ce`: int64
- `newly_treated_medicaid_child_ce`: int64
- `newly_treated_chip_child_ce`: int64
- `newly_treated_any_child_ce`: int64
- `partial_pre2024_ce`: int64
- `separate_chip_program`: int64
- `medicaid_expansion_chip`: object
- `chip_premium_policy_pre2024`: object
- `premium_nonpayment_discontinuation_exposure`: object
- `chip_waiting_period_pre2024`: object
- `chip_lockout_pre2024`: object
- `medicaid_expansion_status`: object
- `unwinding_start_month`: object
- `unwinding_completion_month`: object
- `ex_parte_rate_baseline_if_available`: object
- `baseline_procedural_disenrollment_rate_if_available`: object
- `state_policy_notes`: object
- `source_url_or_source_name`: object
- `confidence_level`: object
- `kff_medicaid_child_ce_status`: object
- `kff_chip_child_ce_status`: object
- `month`: object
- `child_ce_mandate_post_2024`: int64

## enrollment_state_group_month.parquet
Rows: 10098. Columns: 21.
- `state_name`: object
- `state_abbr`: object
- `state_fips`: object
- `month`: object
- `reporting_period`: int64
- `preliminary_or_updated`: object
- `final_report`: object
- `medicaid_expansion_status`: object
- `total_enrollment`: float64
- `total_medicaid_enrollment`: float64
- `total_chip_enrollment`: float64
- `enrollment`: float64
- `group`: object
- `child_group`: int64
- `log_enrollment`: float64
- `enrollment_lag`: float64
- `month_to_month_change`: float64
- `month_to_month_pct_change`: float64
- `net_enrollment_loss_rate`: float64
- `aggregate_instability_proxy`: float64
- `child_adult_enrollment_ratio`: float64

## renewal_state_month.parquet
Rows: 1887. Columns: 24.
- `state_name`: object
- `state_abbr`: object
- `state_fips`: object
- `month`: object
- `reporting_period`: int64
- `original_or_updated`: object
- `renewals_initiated`: float64
- `renewals_due`: float64
- `renewed_total`: float64
- `ex_parte_renewed`: float64
- `form_renewed`: float64
- `disenrolled_total`: float64
- `ineligible_terminations`: float64
- `procedural_terminations`: float64
- `pending_renewals`: float64
- `renewal_completion_rate`: float64
- `ex_parte_renewal_rate_due`: float64
- `ex_parte_renewal_rate_renewed`: float64
- `form_renewal_rate_due`: float64
- `termination_rate_due`: float64
- `procedural_termination_rate_due`: float64
- `procedural_termination_share`: float64
- `ineligibility_termination_share`: float64
- `pending_renewal_share`: float64

## acs_state_age_year.parquet
Rows: 510. Columns: 19.
- `year`: int64
- `state`: object
- `state_abbr`: object
- `state_fips`: object
- `age_group`: object
- `child_group`: int64
- `population_thousands`: float64
- `any_insurance_thousands`: float64
- `any_insurance_percent`: float64
- `private_insurance_thousands`: float64
- `private_insurance_percent`: float64
- `public_insurance_thousands`: float64
- `public_insurance_percent`: float64
- `medicaid_thousands`: float64
- `medicaid_percent`: float64
- `uninsured_thousands`: float64
- `uninsured_percent`: float64
- `source_file`: object
- `post2024`: int64

## main_ddd_panel.parquet
Rows: 10098. Columns: 55.
- `state_name`: object
- `state_abbr`: object
- `state_fips`: object
- `month`: object
- `reporting_period`: int64
- `preliminary_or_updated`: object
- `final_report`: object
- `medicaid_expansion_status`: object
- `total_enrollment`: float64
- `total_medicaid_enrollment`: float64
- `total_chip_enrollment`: float64
- `enrollment`: float64
- `group`: object
- `child_group`: int64
- `log_enrollment`: float64
- `enrollment_lag`: float64
- `month_to_month_change`: float64
- `month_to_month_pct_change`: float64
- `net_enrollment_loss_rate`: float64
- `aggregate_instability_proxy`: float64
- `child_adult_enrollment_ratio`: float64
- `pre2024_medicaid_child_12mo_ce`: int64
- `pre2024_chip_child_12mo_ce`: float64
- `pre2024_any_child_12mo_ce`: int64
- `newly_treated_medicaid_child_ce`: int64
- `newly_treated_chip_child_ce`: int64
- `newly_treated_any_child_ce`: int64
- `partial_pre2024_ce`: int64
- `separate_chip_program`: int64
- `medicaid_expansion_chip`: object
- `chip_premium_policy_pre2024`: object
- `premium_nonpayment_discontinuation_exposure`: object
- `chip_waiting_period_pre2024`: object
- `chip_lockout_pre2024`: object
- `medicaid_expansion_status_policy`: object
- `unwinding_start_month`: object
- `unwinding_completion_month`: object
- `ex_parte_rate_baseline_if_available`: object
- `baseline_procedural_disenrollment_rate_if_available`: object
- `state_policy_notes`: object
- `source_url_or_source_name`: object
- `confidence_level`: object
- `kff_medicaid_child_ce_status`: object
- `kff_chip_child_ce_status`: object
- `child_ce_mandate_post_2024`: int64
- `post2024`: int64
- `event_month`: int64
- `ddd_any_newly_treated`: int64
- `ddd_medicaid_newly_treated`: int64
- `ddd_partial_or_new`: int64
- `renewals_due`: float64
- `ex_parte_renewal_rate_due`: float64
- `procedural_termination_rate_due`: float64
- `procedural_termination_share`: float64
- `pending_renewal_share`: float64

## mechanism_panel.parquet
Rows: 1887. Columns: 29.
- `state_name`: object
- `state_abbr`: object
- `state_fips`: object
- `month`: object
- `reporting_period`: int64
- `original_or_updated`: object
- `renewals_initiated`: float64
- `renewals_due`: float64
- `renewed_total`: float64
- `ex_parte_renewed`: float64
- `form_renewed`: float64
- `disenrolled_total`: float64
- `ineligible_terminations`: float64
- `procedural_terminations`: float64
- `pending_renewals`: float64
- `renewal_completion_rate`: float64
- `ex_parte_renewal_rate_due`: float64
- `ex_parte_renewal_rate_renewed`: float64
- `form_renewal_rate_due`: float64
- `termination_rate_due`: float64
- `procedural_termination_rate_due`: float64
- `procedural_termination_share`: float64
- `ineligibility_termination_share`: float64
- `pending_renewal_share`: float64
- `newly_treated_any_child_ce`: int64
- `partial_pre2024_ce`: int64
- `separate_chip_program`: int64
- `post2024`: int64
- `did_any_newly_treated`: int64

## validation_panel.parquet
Rows: 510. Columns: 23.
- `year`: int64
- `state`: object
- `state_abbr`: object
- `state_fips`: object
- `age_group`: object
- `child_group`: int64
- `population_thousands`: float64
- `any_insurance_thousands`: float64
- `any_insurance_percent`: float64
- `private_insurance_thousands`: float64
- `private_insurance_percent`: float64
- `public_insurance_thousands`: float64
- `public_insurance_percent`: float64
- `medicaid_thousands`: float64
- `medicaid_percent`: float64
- `uninsured_thousands`: float64
- `uninsured_percent`: float64
- `source_file`: object
- `post2024`: int64
- `newly_treated_any_child_ce`: int64
- `partial_pre2024_ce`: int64
- `separate_chip_program`: int64
- `ddd_any_newly_treated`: int64

Constructed outcome caveat: aggregate enrollment volatility is an aggregate coverage-instability proxy, not individual-level churn.