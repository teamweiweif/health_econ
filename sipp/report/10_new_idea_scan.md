# New SIPP Idea Scan: Adult, Non-Unwinding Designs

## Bottom Line

The best next SIPP idea is **ACA enhanced premium tax credits and the 400% FPL subsidy cliff**.

Fast verdict: `GO-TO-NEXT-TEST`.

The design is currently policy-relevant because enhanced premium tax credits removed the old
400% FPL cliff in 2021 and the cliff returned in 2026. SIPP 2018-2024 covers reference
years 2017-2023, so it can test the 2021 cliff-removal side now. It cannot test the 2026
return until newer SIPP data arrive.

## Why This Is The Leading Candidate

- It is adult-focused and avoids unwinding and child continuous eligibility.
- It has a sharp policy threshold: 400% FPL.
- The current parquet contains the needed monthly variables: income-to-poverty, insurance,
  direct purchase, marketplace/exchange/subsidy flags, age, state, employment, and medical
  utilization/spending.
- The SIPP contribution is not just Marketplace enrollment. It can observe people outside
  Marketplace administrative data: uninsured, direct-purchase, Medicaid/private transitions,
  employment, income volatility, and utilization.

## Fast Empirical Screen

Primary screen sample: adults 26-64, annual family income 300-500% FPL, reference years 2017-2023.

- Rows: 454,440
- Persons: 27,496
- Key support: above400 persons=13990; above400 market/subsidy events=14319; above400 uninsured events=17393
- Weighted DD screen, market/subsidy outcome: -0.0305
- Weighted DD screen, uninsured outcome: -0.0056

This is not a final estimate. It is only enough to justify a proper next-stage
difference-in-discontinuities/RD-DID design with donut windows, bandwidth checks,
income-density diagnostics, and placebo thresholds.

## Main Testable Research Idea

**Question.** Did eliminating the ACA 400% FPL subsidy cliff change coverage and coverage
stability for middle-income adults who were just above the old eligibility cutoff?

**Design.** Difference-in-discontinuities around 400% FPL:

- running variable: `TFCYINCPOV`, where `4.0` equals 400% FPL;
- treated side: just above 400% FPL;
- comparison side: just below 400% FPL;
- pre period: 2017-2020;
- post period: 2021-2023;
- outcomes: direct-purchase/marketplace coverage, subsidized/exchange coverage,
  uninsured status, coverage loss, Medicaid/private transitions, utilization, and
  out-of-pocket medical spending;
- high-intensity heterogeneity: ages 50-64, because premiums and subsidy value are
  mechanically larger for older adults.

**Publication angle.** Existing public debate and many policy reports focus on Marketplace
enrollment and premiums. SIPP can ask whether a cliff-removal policy changes total insurance
coverage, off-Marketplace substitution, uninsured spells, and income-management behavior around
the cutoff.

## Candidate Ranking

| Rank | Candidate | Fast verdict | Fit with current parquet |
|---:|---|---|---|
| 1 | `aca_ptc_400_fpl_cliff` | GO-TO-NEXT-TEST | strong |
| 2 | `late_medicaid_expansion` | CONDITIONAL-BUT-LITERATURE-SATURATED | strong |
| 3 | `arkansas_medicaid_work_requirements` | FAST-NOGO-FOR-MAIN-PAPER | strong |
| 4 | `state_reinsurance_individual_market` | BACKUP-ONLY | moderate |
| 5 | `family_glitch_fix` | NOT-TESTABLE-WITH-CURRENT-PARQUET | weak |
| 6 | `public_charge_immigrant_chilling` | NOT-TESTABLE-WITH-CURRENT-PARQUET | weak |
| 7 | `adult_postpartum_medicaid_extension` | DEFER | weak |


## Other Candidate Screens

### Arkansas Medicaid Work Requirements

Fast verdict: `FAST-NOGO-FOR-MAIN-PAPER`.

The policy is very current because national work requirements are back on the policy agenda,
but the historical SIPP event is too narrow. The target cell, Arkansas adults age 30-49 at
or below 138% FPL during the 2018-2019 implementation window, has:

- Rows: 279
- Persons: 43

This is useful for a robustness/sidebar exercise, not a top-economics main design.

### Late Medicaid Expansions

Fast verdict: `CONDITIONAL-BUT-LITERATURE-SATURATED`.

This is empirically feasible but not sufficiently novel unless paired with a sharper SIPP-only
mechanism such as income volatility, within-year coverage transitions, or labor-supply lock-in.

- VA 2019-01: persons=331, pre=176, post=210, Medicaid weighted mean 0.355->0.523.
- NE 2020-10: persons=98, pre=79, post=68, Medicaid weighted mean 0.411->0.564.
- OK 2021-07: persons=268, pre=188, post=163, Medicaid weighted mean 0.313->0.358.
- MO 2021-10: persons=215, pre=154, post=133, Medicaid weighted mean 0.316->0.382.
- SD 2023-07: persons=16, pre=15, post=4, Medicaid weighted mean 0.047->0.000.
- NC 2023-12: persons=192, pre=190, post=91, Medicaid weighted mean 0.388->0.399.

### State Reinsurance

Fast verdict: `BACKUP-ONLY`.

The policy is plausible but less sharp in SIPP because treatment intensity is state-premium
specific and individual-market cells are small. Largest treated-state support cells:

- CO 2020: persons=839, direct-purchase events=2015, market/subsidy events=1589.
- PA 2021: persons=1080, direct-purchase events=1312, market/subsidy events=890.
- MD 2019: persons=567, direct-purchase events=1194, market/subsidy events=944.
- WI 2019: persons=779, direct-purchase events=1155, market/subsidy events=848.
- GA 2022: persons=774, direct-purchase events=1066, market/subsidy events=759.

## Not Testable From The Uploaded Parquet Alone

- `family_glitch_fix`: needs employer offer/family premium and dependent-level eligibility.
- `public_charge_immigrant_chilling`: metadata has citizenship/nativity variables, but the current
  96-column parquet does not include them.
- `adult_postpartum_medicaid_extension`: metadata has pregnancy/birth variables, but the current
  parquet does not include them and the topic drifts toward maternal/child coverage.

## Next Stage

Build a dedicated `ptc_400fpl_cliff` pipeline:

1. Add polynomial/local-linear RD-DID estimates around 400% FPL, using `TFCYINCPOV`
   as the primary tax-year income proxy and `TFINCPOV` as a monthly-income sensitivity.
2. Run density and bunching diagnostics around 400% FPL before and after 2021.
3. Use bandwidths 300-500, 350-450, 375-425, and 390-410% FPL.
4. Use placebo thresholds at 300%, 350%, 450%, and 500% FPL.
5. Estimate age-intensity heterogeneity for 50-64 vs 26-49.
6. Separate outcomes into coverage, market/subsidy, uninsured spells, utilization, and OOP spending.
7. Do not use causal ML unless the RD-DID and placebo diagnostics pass.

## Source Checks Used For This Scan

- CMS: ARP expanded premium tax credits to marketplace consumers whose sticker
  premiums exceeded 8.5% of income and newly reached households above 400% FPL:
  https://www.cms.gov/newsroom/blog/inflation-reduction-act-tax-credits-improve-coverage-affordability-middle-income-americans
- IRS: ARPA temporarily eliminated the rule denying PTC when household income
  exceeded 400% FPL for 2021-2022:
  https://www.irs.gov/affordable-care-act/individuals-and-families/eligibility-for-the-premium-tax-credit
- KFF: enhanced PTCs expired at the end of 2025 and early 2026 enrollment drops
  were concentrated above the 400% FPL subsidy cliff:
  https://www.kff.org/affordable-care-act/what-we-know-so-far-about-2026-aca-marketplace-enrollment-premiums-and-deductibles/
- KFF: current Medicaid expansion implementation dates:
  https://www.kff.org/affordable-care-act/state-indicator/state-activity-around-expanding-medicaid-under-the-affordable-care-act/
- KFF: 2025 federal law work requirements begin January 1, 2027 for ACA expansion
  adults and certain 1115 waiver enrollees:
  https://www.kff.org/medicaid/medicaid-work-requirements-tracker-overview/
- KFF: Arkansas 2018 work/reporting requirements applied first to ages 30-49:
  https://www.kff.org/medicaid/state-data-for-medicaid-work-requirements-in-arkansas/
- CMS: Section 1332 state innovation waivers are the official policy route for
  state reinsurance programs:
  https://www.cms.gov/marketplace/states/section-1332-state-innovation-waivers

## Output Tables

- `result/idea_scan/idea_screen_candidate_summary.csv`
- `result/idea_scan/idea_screen_variable_availability.csv`
- `result/idea_scan/idea_screen_ptc_dd.csv`
- `result/idea_scan/idea_screen_ptc_bins.csv`
- `result/idea_scan/idea_screen_work_requirements.csv`
- `result/idea_scan/idea_screen_late_expansion.csv`
- `result/idea_scan/idea_screen_reinsurance.csv`
