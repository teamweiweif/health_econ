# Sixth-Round State Marketplace Subsidy Decision

## Question

Can the current 96-column SIPP parquet support a new adult, non-child, non-unwinding paper on
state-funded Marketplace subsidies?

## Ideas Tested

This round tested two state subsidy policies that map directly to variables in the compact SIPP file:

1. Maryland's 2022 young-adult Marketplace subsidy.
2. New Jersey Health Plan Savings, effective for 2021 coverage.

These are better-targeted than another generic ACA uptake screen because eligibility is tied to
observed SIPP variables:

- Maryland: state x age x income x post-2022.
- New Jersey: state x income eligibility x post-2021.

## Policy Source Checks

- Maryland Health Benefit Exchange young adult subsidy report:
  https://www.marylandhbe.com/wp-content/uploads/2024/12/Report-on-the-Young-Adult-Subsidy-Program.pdf
- SHVS State Marketplace Subsidies report:
  https://shvs.org/wp-content/uploads/2026/03/SHVS_State-Marketplace-Subsidies-to-Support-Health-Insurance-Affordability_Final.pdf
- GetCoveredNJ Health Plan Savings:
  https://www.nj.gov/getcoverednj/financialhelp/premiums/
- Maryland Health Connection 2026 enrollment bulletin:
  https://content.govdelivery.com/accounts/MDHC/bulletins/405d2db

Relevant facts:

- SHVS describes state subsidies as a tool to address affordability gaps, expand coverage, improve
  the risk pool, and target groups difficult to reach.
- SHVS identifies Maryland's young-adult subsidy as effective beginning in 2022 and targeted to
  young adults with income up to 400% FPL.
- Maryland Health Connection reports that Maryland created the young-adult subsidy in 2022 to
  encourage young-adult enrollment.
- GetCoveredNJ states that NJ Health Plan Savings began lowering premiums for coverage starting
  January 1, 2021 and applies up to 600% FPL.

## Data and Design

Source:

- `data/analysis_ready/sipp_2018_2024_person_month_panel.parquet`

Constructed file:

- `result/idea_scan/state_marketplace_subsidy_person_year_panel.parquet`

Outcomes:

- `direct_market`
- `exchange_subsidy`
- `uninsured`
- `any_coverage`
- `private`
- `oop_any`
- `doctor_any`

Model family:

- Weighted person-year LPM.
- Saturated DDD fixed effects.

## Maryland Young Adult Subsidy

Broad design:

- Ages 18-44.
- Family income 138-400% FPL.
- Treated group: Maryland ages 18-34 in 2022+.
- Comparison: ages 35-44 and the same age groups in other states.
- Fixed effects: state-year, state-young, young-year.

Support:

- 26,620 person-years.
- 19,584 persons.
- Maryland target person-years: 287.
- Active treated Maryland target person-years: 97.

Main estimates:

- `direct_market`: +0.0847, se 0.1215.
- `exchange_subsidy`: +0.0829, se 0.1190.
- `uninsured`: +0.1407, se 0.0700.
- `any_coverage`: -0.1407, se 0.0700.

Cleaner adult-only design:

- Ages 26-44.
- Family income 138-400% FPL.
- Treated group: Maryland ages 26-34 in 2022+.
- This avoids the under-26 dependent-coverage confound.

Support:

- 18,732 person-years.
- 13,716 persons.
- Maryland target person-years: 164.
- Active treated Maryland target person-years: 57.

Main estimates:

- `direct_market`: +0.1025, se 0.1347.
- `exchange_subsidy`: +0.1092, se 0.1327.
- `uninsured`: +0.1178, se 0.0686.
- `any_coverage`: -0.1178, se 0.0686.

Dynamic check:

- Clean adult direct-market coefficient:
  - 2019: +0.1239, se 0.1912.
  - 2020: +0.1437, se 0.1823.
  - 2022: +0.3075, se 0.2046.
  - 2023: +0.0854, se 0.2329.
- Clean adult exchange/subsidy coefficient:
  - 2019: +0.2121, se 0.1818.
  - 2020: +0.1082, se 0.1801.
  - 2022: +0.3606, se 0.2012.
  - 2023: +0.0762, se 0.2335.

Decision:

`CONCEPTUALLY CLEAN; EMPIRICALLY TOO THIN`

This is a real, interesting, policy-backed idea. The age-eligibility design is much cleaner than the
generic ACA state-year screens. But the public SIPP support is too small in Maryland. In the clean
adult cell there are only 57 active treated person-years, and the standard errors are extremely large.
The point estimates are positive for Marketplace/subsidized coverage, but uninsured also rises and
the event estimates are noisy.

This should not be a main paper with the current public SIPP file.

## New Jersey Health Plan Savings

Design:

- Ages 26-64.
- Family income 138-1000% FPL.
- Treated group: New Jersey residents at 138-600% FPL in 2021+.
- Comparison: 600-1000% FPL and the same income bands in other states.
- Fixed effects: state-year, state-eligible-income, eligible-income-year.

Support:

- 76,892 person-years.
- 48,471 persons.
- New Jersey eligible person-years: 978.
- Active treated New Jersey eligible person-years: 526.

Main estimates:

- `direct_market`: +0.0490, se 0.0355.
- `exchange_subsidy`: +0.0332, se 0.0302.
- `uninsured`: -0.0105, se 0.0287.
- `any_coverage`: +0.0105, se 0.0287.
- `oop_any`: +0.1691, se 0.0581.

Dynamic check:

- `direct_market`:
  - 2019: +0.0063, se 0.0520.
  - 2021: +0.0700, se 0.0474.
  - 2022: +0.0573, se 0.0573.
  - 2023: +0.0303, se 0.0483.
- `exchange_subsidy`:
  - 2019: +0.0283, se 0.0422.
  - 2021: +0.0559, se 0.0434.
  - 2022: +0.0551, se 0.0518.
  - 2023: +0.0286, se 0.0419.
- `uninsured`:
  - 2019: +0.0324, se 0.0435.
  - 2021: -0.0645, se 0.0469.
  - 2022: +0.0080, se 0.0423.
  - 2023: +0.0612, se 0.0449.

Decision:

`DIRECTIONAL SIGNAL; NOT CLEAN TOP-FIELD DESIGN`

New Jersey has more support than Maryland and the Marketplace/subsidy signs are in the expected
direction. But it is bundled with multiple simultaneous shocks:

- New Jersey moved to GetCoveredNJ / SBE for 2021 coverage.
- ARPA enhanced federal subsidies started in 2021.
- New Jersey already had a state individual mandate from 2019.

The income-band DDD helps but cannot fully isolate NJHPS. This can be a robustness or descriptive
case study, not a standalone top economics causal paper.

## Updated Ranking

1. **PTC / 400% FPL with premium intensity**: best policy gap, but current state-level premium
   matching failed the dynamic check.
2. **Maryland young-adult subsidy**: cleanest new conceptual design, but public SIPP support is
   far too thin.
3. **New Jersey Health Plan Savings**: directionally plausible, but bundled with SBE transition,
   ARPA, and state mandate.
4. **State individual mandates**: weak marketplace signal but no clean coverage or healthy-risk-pool
   mechanism.
5. **Pandemic UI early termination**: clean timing but too small for insurance/safety-net spillovers.
6. **No Surprises Act**: excellent policy but SIPP measurement is too indirect.
7. **State-Based Marketplace transitions**: fails direction/dynamics.

## Current Verdict

`NO CLEAN IMMEDIATE GO FROM CURRENT 96-COLUMN PUBLIC SIPP PARQUET`

This round did find one idea worth remembering: Maryland young-adult subsidies. The reason to keep
it is conceptual, not empirical. It would become viable only with a larger dataset or pooled
Marketplace administrative data, because the treatment cell in public SIPP is too small.

## New Artifacts

- `script/11_idea_scan/12_state_marketplace_subsidy_fast_test.py`
- `report/26_state_marketplace_subsidy_fast_test.md`
- `result/idea_scan/state_marketplace_subsidy_person_year_panel.parquet`
- `result/idea_scan/state_marketplace_subsidy_support.csv`
- `result/idea_scan/state_marketplace_subsidy_estimates.csv`
- `result/idea_scan/state_marketplace_subsidy_event.csv`
