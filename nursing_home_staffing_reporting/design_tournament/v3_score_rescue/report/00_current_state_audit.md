# V3 Current State Audit

## What Was Already Solved

- CMS official sources verify January 2022 as the transparency event: weekend staffing and turnover were added to Care Compare, and employee-level PBJ staffing data were scheduled for release on January 26, 2022.
- CMS official sources verify July 27, 2022 as the algorithmic staffing-label event: weekend total nurse HPRD, total nurse turnover, RN turnover, and administrator departures were added to the staffing-domain methodology.
- The July 2022 Technical Users' Guide was snapshotted and used to implement the six-component staffing score: adjusted total nurse HPRD, adjusted RN HPRD, adjusted weekend total nurse HPRD, total nurse turnover, RN turnover, and administrator departures.
- The old overall-star formula change was verified: January 2022 allowed a four- or five-star staffing bonus when staffing exceeded health inspection, while July 2022 allowed an overall-star bonus only for five-star staffing.
- PBJ daily data were converted into policy-relevant lower-tail reliability outcomes including RN<8h days, zero-RN days, weekend low-HPRD measures, weekend share of nursing hours, contract share, and average daily census.
- V2 self-test passed 31/31 checks and correctly preserved the downgrade that RD/RD-DID cannot be strong causal evidence while the July running variable remains below validation threshold.

## What Failed

- The public Provider Data Catalog snapshots used in V2 contained staffing stars and component measures, but not the official facility-level 0-380 staffing score.
- The July 2022 emulator used reported weekend total nurse HPRD as a proxy because the July ProviderInfo archive did not expose adjusted weekend total nurse HPRD.
- The July 2022 emulator matched official staffing stars at 0.899, below the pre-specified 0.950 threshold for primary RD/RD-DID use.
- RD density diagnostics around the proxy score showed nontrivial imbalance near true thresholds; at the 320 cutoff with bandwidth 10, the below/above counts were 360/424 with binomial p=0.024.
- The metric-salience DDD was implemented only as a facility-level post-minus-pre proxy rather than a true facility-day or facility-week by metric panel.
- The 2018 validation event was not recovered in V2 because the local PBJ source inventory started in 2019.

## What Is Still Unknown

- Whether an official CMS archive, API metadata endpoint, hidden ZIP member, data dictionary, or Provider Preview-related file contains the official 0-380 staffing score, staffing points, or a usable equivalent.
- Whether adjusted weekend total nurse HPRD exists in an official July 2022 facility-snapshot file outside the parsed ProviderInfo CSV.
- Whether the July 2022 emulator can be improved above the 0.950 match threshold without proxy substitution.
- Whether formula-induced overall-star loss can be isolated from underlying quality using matched, weighted, or local comparison designs.
- Whether a true facility-day or facility-week metric-salience panel shows targeted weekend total nurse staffing, broad labor-market recovery, or reallocation across staffing dimensions.
- Whether official 2017-2018 PBJ daily files can be recovered and used to validate the OIG zero-RN to low-positive-RN reporting pattern.

## Prior Estimates Not Strong Causal Evidence

- The old global composite exposure DID remains demoted because earlier audits found failed pre-trends and placebo timing concerns.
- V2 RD and RD-DID estimates are exploratory only because the July 2022 proxy running variable failed the 95% validation threshold.
- V2 shadow-price and bunching diagnostics inherit the proxy-score limitation and should not be interpreted causally.
- V2 formula-induced label-shock estimates are conditional mechanism evidence only; the first stage is strong, but exclusion is fragile without matching, balance, and pretrend diagnostics.
- V2 metric-salience estimates are supporting mechanism diagnostics only because the panel was too aggregated.
- None of the V2 staffing, rating, or census results proves resident clinical quality improvement.

## Files And Tables Reused

- `report/final_breakthrough_report.md`
- `report/design_tournament_scorecard.md`
- `report/rating_algorithm_emulation_audit.md`
- `report/rd_threshold_results.md`
- `report/formula_label_shock_results.md`
- `report/metric_salience_ddd_results.md`
- `report/official_policy_algorithm_audit.md`
- `report/outcome_reconstruction_audit.md`
- `report/identification_audit_v2.md`
- `temp/rejected_designs_v2.md`
- `temp/self_test_v2.md`
- `result/tables/rating_emulator_validation.csv`
- `result/tables/rd_threshold_estimates.csv`
- `result/tables/rd_density_checks.csv`
- `result/tables/rd_did_estimates.csv`
- `result/tables/formula_label_first_stage.csv`
- `result/tables/formula_label_shock_estimates.csv`
- `result/tables/metric_salience_ddd_estimates.csv`
- `result/tables/reliability_outcome_coverage.csv`
- `result/tables/self_test_checks.csv`

## What V3 Will Try To Fix

- Run an official-source field hunt across CMS Technical Users' Guide archives, Data.CMS.gov metadata/API endpoints, Provider Data Catalog archived ZIPs, ZIP members, headers, data dictionaries, and schema metadata for January 2022, April 2022, July 2022, October 2022, and January 2023.
- Replace the proxy running variable if an official 0-380 score, official points field, adjusted weekend total nurse HPRD, or complete official component set is found.
- Rebuild and validate the July 2022 score emulator using the July 2022 guide and compare V3 validation against V2.
- Re-run RD/RD-DID only if the running variable is official or the emulator reaches the 0.950 validation threshold without severe systematic mismatch.
- Strengthen formula-induced overall-star label shock with matched or weighted controls, balance diagnostics, pretrends, event timing, and heterogeneity checks.
- Build a true facility-day or facility-week metric-salience DDD panel when data access and size permit; otherwise document the exact infeasibility.
- Search official PBJ archives for 2017-2018 daily files to attempt the OIG validation event.
- Produce a self-checking final decision report that assigns strong-go, conditional-go, or no-go status to each design without returning to the old composite exposure DID.
