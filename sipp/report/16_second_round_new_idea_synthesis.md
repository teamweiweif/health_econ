# Second-Round SIPP Idea Synthesis

## Bottom Line

After expanding beyond the ACA affordability screen, the current 96-column SIPP parquet still does
not produce a clean top-field `GO` from SIPP alone. It does produce three conditional paths:

1. **Best current policy gap:** ACA enhanced PTC / 400% FPL subsidy cliff.
2. **Cleanest policy timing:** 2021 pandemic UI early termination.
3. **Largest sample support:** state minimum wage increases and safety-net/insurance spillovers.

The decision is not to enter unwinding or child projects. Those remain out of scope.

## Updated Ranking

### 1. ACA Enhanced PTC / 400% FPL Cliff

Status: `CONDITIONAL-GO-ONLY-WITH-PREMIUM-INTENSITY`.

This is still the most policy-relevant and publication-relevant idea. The 2026 return of the
subsidy cliff is current, and SIPP can observe uninsured spells, off-Marketplace coverage,
medical out-of-pocket spending, and labor outcomes outside Marketplace administrative data.

Fast support:

- 300-500% FPL adult sample: 454,440 person-month rows and 27,496 persons.
- Above-400 group: 13,990 persons.
- Above-400 market/subsidy events: 14,319.
- Above-400 uninsured events: 17,393.

Problem:

- Simple RD-DID around 400% FPL gives a negative market/subsidy coefficient.
- Both below-400 and above-400 groups received ARPA affordability changes.
- A paper-quality design needs external premium-intensity data.

Verdict:

Use this only if we merge premium burden or benchmark premium data. Without that, it is not clean.

### 2. Pandemic UI Early Termination

Status: `DIRECT-TIMING-BUT-LOW-POWER`.

This is the cleanest state-month policy timing from the current parquet. In 2021, many states
ended federal pandemic unemployment benefits before the national September expiration. SIPP has
monthly unemployment compensation, employment, earnings, SNAP, Medicaid, insurance, and medical
financial outcomes.

Fast support:

- Primary UC at-risk sample: 624 persons.
- Early-exit states: 183 persons.
- Control states: 446 persons.
- UC months among the at-risk sample: 3,698.

Primary UC at-risk DiD signs:

- UC receipt: -0.0565.
- Employed any week: +0.0388.
- Earnings positive: +0.0214.
- SNAP: -0.0192.
- Medicaid: +0.0117.
- Uninsured: -0.0332.

Problem:

- Primary sample is small for SIPP.
- Employment/labor-supply effects are already studied with CPS, bank, and administrative data.
- SIPP novelty must be safety-net and insurance spillovers, not employment.

Verdict:

This is the best "direct causal timing" backup, but it is not yet top-field because power and
novelty are limited. It deserves one person-FE/event-study pass before final no-go.

### 3. Minimum Wage Spillovers

Status: `LARGE-SUPPORT-NAIVE-SPILLOVER-SIGNAL-BUT-ID-WEAK`.

This has the largest sample and strong naive spillover patterns. DOL official minimum-wage history
is usable, and SIPP has earnings, employment, SNAP, Medicaid, uninsured status, medical OOP, and
doctor use.

Fast support:

- Adults with high school or less: 34,582 persons.
- Treated low-education adults in state-years with minimum-wage increases: 16,611 persons.
- Low-education SNAP events: 93,972.
- Low-education Medicaid events: 175,994.
- Low-education uninsured events: 142,110.

Naive DDD signs for minimum-wage increase x high-school-or-less:

- Earnings positive: +0.0088.
- Employed any week: +0.0075.
- SNAP: -0.0137.
- SSI: -0.0101.
- Medicaid: +0.0224.
- Uninsured: -0.0153.
- OOP any: -0.0306.

Problem:

- The uploaded parquet lacks occupation, industry, and clean pre-policy hourly wage.
- High-school-or-less is too broad for a top-field exposure design.
- Individual-month screening standard errors are not final clustered inference.
- Minimum-wage literature is crowded.

Verdict:

Large-sample secondary candidate only. It becomes much stronger if a richer SIPP extract includes
occupation/industry or a pre-policy low-wage exposure measure.

### 4. Medicare Age 65 / ACA Age 26 Thresholds

Status: `NOT RECOMMENDED`.

These are clean textbook thresholds and have large support, but they do not meet the requested
innovation and current-gap standard.

Support:

- Age 60-70 cells each have roughly 4,500-5,000 persons by integer `TAGE`.
- Age 24-28 cells each have roughly 3,600-3,800 persons.

Problem:

- Age is only integer years in the uploaded parquet, not exact age in months.
- Medicare age 65 and ACA dependent coverage age 26 are old, heavily studied designs.
- They are useful as validation exercises, not as a new high-potential paper.

## Current Best Answer

There is no clean, immediate, top-economics `GO` from the uploaded 96-column parquet alone.

The most defensible next move is:

1. Keep **PTC 400% FPL** as the lead idea only if external premium-intensity data can be added.
2. Run one more **UI early termination** person-FE/event-study pass because its timing is clean.
3. Treat **minimum wage spillovers** as a large-sample backup that needs a richer SIPP extract for
   credible exposure.

## Artifacts

- `report/10_new_idea_scan.md`
- `report/11_ptc_400fpl_fast_test.md`
- `report/12_reinsurance_fast_test.md`
- `report/13_new_sipp_idea_recommendation.md`
- `report/14_pandemic_ui_early_exit_fast_test.md`
- `report/15_minimum_wage_spillover_fast_test.md`
- `result/idea_scan/idea_screen_candidate_summary.csv`
- `result/idea_scan/ptc_400fpl_rddid_fast_estimates.csv`
- `result/idea_scan/reinsurance_ddd_fast_estimates.csv`
- `result/idea_scan/pandemic_ui_early_exit_estimates.csv`
- `result/idea_scan/minimum_wage_spillover_estimates.csv`

## Source Checks Added In This Round

- U.S. Department of Labor, federal pandemic UI expiration guidance:
  https://www.dol.gov/node/162738
- St. Louis Fed, early state termination of FPUC in June-July 2021:
  https://www.stlouisfed.org/on-the-economy/2022/apr/end-emergency-pandemic-unemployment-benefits-2021
- NBER pandemic UI early termination working paper:
  https://www.nber.org/papers/w29575
- AEA Papers and Proceedings bank-data study on early UI withdrawal:
  https://www.aeaweb.org/articles?id=10.1257/pandp.20221009
- U.S. Department of Labor historical state minimum wage table:
  https://www.dol.gov/agencies/whd/state/minimum-wage/history
- CBO minimum wage report:
  https://www.cbo.gov/publication/55410
