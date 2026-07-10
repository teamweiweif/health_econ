# State Marketplace Subsidy Fast Test

## Question

Can current SIPP support a new adult, non-child, non-unwinding paper on state-funded Marketplace
subsidies?

This tests two policy shocks:

1. Maryland's 2022 young-adult Marketplace subsidy.
2. New Jersey Health Plan Savings, effective for 2021 coverage.

## Source Checks

- Maryland Health Benefit Exchange young adult subsidy report: https://www.marylandhbe.com/wp-content/uploads/2024/12/Report-on-the-Young-Adult-Subsidy-Program.pdf
- SHVS State Marketplace Subsidies report: https://shvs.org/wp-content/uploads/2026/03/SHVS_State-Marketplace-Subsidies-to-Support-Health-Insurance-Affordability_Final.pdf
- GetCoveredNJ Health Plan Savings: https://www.nj.gov/getcoverednj/financialhelp/premiums/
- Maryland Health Connection 2026 enrollment bulletin: https://content.govdelivery.com/accounts/MDHC/bulletins/405d2db

Key policy facts from the source checks:

- Maryland has offered a young-adult subsidy since 2022; current summaries describe eligibility for
  young adults with income up to 400% FPL.
- SHVS describes young adults as disproportionately uninsured and potentially important for the
  Marketplace risk pool.
- New Jersey Health Plan Savings started lowering premiums for coverage beginning January 1,
  2021 and applies up to 600% FPL.

## Data Construction

- Source parquet: `data/analysis_ready/sipp_2018_2024_person_month_panel.parquet`.
- Unit: person-year collapsed from monthly SIPP observations.
- Outcomes: annual share of months in direct-purchase/Marketplace coverage,
  exchange/subsidized private coverage, uninsured, any coverage, private coverage, OOP any, doctor
  visit any.
- Models: weighted LPM screens with saturated DDD fixed effects.

## Maryland Young Adult Subsidy

Broad sample:

- Ages 18-44.
- Family income 138-400% FPL.
- Treated group: Maryland ages 18-34 in 2022+.
- Comparison: ages 35-44 and the same age groups in other states.
- Fixed effects: state-year, state-young, and young-year.

Support:

- Person-years: 26,620.
- Persons: 19,584.
- Maryland target person-years: 287.
- Active treated Maryland target person-years: 97.

Estimates:

- `direct_market`: +0.0847, se 0.1215, t 0.70.
- `exchange_subsidy`: +0.0829, se 0.1190, t 0.70.
- `uninsured`: +0.1407, se 0.0700, t 2.01.
- `any_coverage`: -0.1407, se 0.0700, t -2.01.
- `private`: -0.0464, se 0.1289, t -0.36.
- `oop_any`: +0.1391, se 0.1230, t 1.13.
- `doctor_any`: +0.1138, se 0.1199, t 0.95.

Cleaner adult sample:

- Ages 26-44, to avoid dependent-coverage confounding for ages under 26.
- Treated group: Maryland ages 26-34 in 2022+.

Support:

- Person-years: 18,732.
- Persons: 13,716.
- Maryland target person-years: 164.
- Active treated Maryland target person-years: 57.

Estimates:

- `direct_market`: +0.1025, se 0.1347, t 0.76.
- `exchange_subsidy`: +0.1092, se 0.1327, t 0.82.
- `uninsured`: +0.1178, se 0.0686, t 1.72.
- `any_coverage`: -0.1178, se 0.0686, t -1.72.
- `private`: -0.0116, se 0.1354, t -0.09.
- `oop_any`: +0.2197, se 0.1371, t 1.60.
- `doctor_any`: +0.1107, se 0.1273, t 0.87.

## New Jersey Health Plan Savings

Sample:

- Ages 26-64.
- Family income 138-1000% FPL.
- Treated group: New Jersey residents at 138-600% FPL in 2021+.
- Comparison: 600-1000% FPL and the same income bands in other states.
- Fixed effects: state-year, state-eligible-income, eligible-income-year.

Support:

- Person-years: 76,892.
- Persons: 48,471.
- New Jersey eligible person-years: 978.
- Active treated New Jersey eligible person-years: 526.

Estimates:

- `direct_market`: +0.0490, se 0.0355, t 1.38.
- `exchange_subsidy`: +0.0332, se 0.0302, t 1.10.
- `uninsured`: -0.0105, se 0.0287, t -0.36.
- `any_coverage`: +0.0105, se 0.0287, t 0.36.
- `private`: +0.0108, se 0.0391, t 0.28.
- `oop_any`: +0.1691, se 0.0581, t 2.91.
- `doctor_any`: +0.0783, se 0.0505, t 1.55.

## Verdict

`DIRECTIONAL-SIGNAL-BUT-NOT-CLEAN`

Interpretation:

- Maryland is the cleaner design because eligibility varies sharply by age and income, but SIPP has
  very little Maryland support in the eligible age-income cell.
- New Jersey has more support, but the 2021 policy is bundled with New Jersey's Marketplace
  transition and the ARPA federal subsidy expansion. The income-band DDD helps but does not make
  it a top-field design by itself.
- A clean GO would require large, consistent increases in direct-market or exchange/subsidized
  coverage with no offsetting increase in uninsured and no pre-trend in the event checks.

## Artifacts

- `script/11_idea_scan/12_state_marketplace_subsidy_fast_test.py`
- `result/idea_scan/state_marketplace_subsidy_person_year_panel.parquet`
- `result/idea_scan/state_marketplace_subsidy_support.csv`
- `result/idea_scan/state_marketplace_subsidy_estimates.csv`
- `result/idea_scan/state_marketplace_subsidy_event.csv`
