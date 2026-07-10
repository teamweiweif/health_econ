# Final Research Memo

## 1. Executive Verdict

NO GO.

The adult-boundary topic has been implemented as a full reproducible audit. The publishable claim depends on the support and robustness summarized in `report/08_go_no_go_decision.md`, `report/06_main_results_memo.md`, and `result/tables/sensitivity_summary.csv`.

## 2. Adult-Boundary Topic

The project tests temporary family-income crossings above 138% FPL (`TFINCPOV = 1.38`) among near-boundary adults in expansion states. The design is not assumed causal; it is audited through event support, regime contrasts, hazard models, descriptive event profiles, and robustness checks.

## 3. Sample And Years

SIPP file years 2018-2024 are mapped to reference years 2017-2023. The primary sample is adults age 19-64, not Medicare-covered, not SSI/disability flagged for the primary MAGI sample, in expansion-state months, and near 100-175% FPL.

## 4. Coverage Construction

Medicaid uses `EMDMTH` as primary and `RPUBTYPE2` as sensitivity. Uninsured uses `RHLTHMTH == 2`; private uses `RPRIMTH`; direct-purchase/exchange uses `RPRITYPE2`, `RMARKTPLACE`, and exchange/subsidy variables.

## 5. Temporary Eligibility Shocks

Primary exposure is a cross-up from `TFINCPOV <= 1.38` to `> 1.38` that returns below threshold within one month. Two- and three-month return windows, sustained crossings, alternative thresholds, and alternative bandwidths are reported.

## 6. Main Descriptive Facts

See:

- `result/tables/sample_counts_by_year_regime.csv`
- `result/tables/temporary_crossing_counts_by_year_regime.csv`
- `result/tables/coverage_transition_matrix_by_year.csv`
- `result/figures/transition_path_decomposition.png`

## 7. Causal Estimates

Main transparent hazard estimates are in `result/tables/main_hazard_results.csv`. Event-study profiles are descriptive and stored in `result/tables/event_study_results.csv`.

## 8. Robustness And Failed Specifications

Robustness and placebo-threshold variants are stored in `result/tables/sensitivity_summary.csv`. Specifications with insufficient support are retained with `status=insufficient_support`.

## 9. Causal ML

Not run.

Causal ML is not used as a headline unless conventional identification and support pass. This run writes the audit and avoids decorative ML.

## 10. Backup Recommendation

If the adult-boundary result is `NO-GO`, the recommended backup is pre-2024 child continuous eligibility, with state-year policy verification before modeling. Early unwinding administrative burden is only an exploratory backup unless state-month burden metrics can be validated against individual transition timing.

## 11. Next Steps For Paper Writing

- Use `report/06_main_results_memo.md` and `report/08_go_no_go_decision.md` as the decision core.
- If conditional/go, write the paper as a mechanism-oriented SIPP coverage-transition paper with strong caveats.
- If no-go, preserve this as a transparent failed adult-boundary audit and pivot to backup 1.
