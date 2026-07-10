# ACA State Reinsurance Fast Test

## Question

Can state ACA Section 1332 reinsurance programs support an adult SIPP paper on Marketplace
affordability and coverage?

## Source Checks

- KFF Section 1332 waiver tracker: https://www.kff.org/affordable-care-act/tracking-section-1332-state-innovation-waivers/
- CMS CCIIO 2024 Section 1332 data brief: https://www.cms.gov/files/document/cciio-data-brief-042024-508-final.pdf

Key policy facts used here:

- KFF describes Section 1332 waivers as ACA innovation waivers and notes that most approved waivers
  have been used for state reinsurance programs.
- The CMS CCIIO data brief reports state first years of operation and actual SLCSP premium reductions
  under state reinsurance waivers.
- CMS reports that state reinsurance programs reduced statewide average SLCSP premiums by 3.75% to
  41.17% from 2018 through 2023 relative to no-waiver premiums.

## Design

- Unit: person-year collapsed from monthly SIPP observations.
- Sample: adults age 26-64 with family income 138-1000% FPL and at least six observed months.
- Primary exposed group: 400-1000% FPL adults, who are more exposed to gross premium reductions,
  especially before ARPA removed the hard 400% FPL subsidy cliff.
- Comparison group: 138-400% FPL adults in the same state-years.
- Treatment intensity: high-income target x CMS actual SLCSP premium reduction, scaled per 10
  percentage points.
- Alternative treatment: high-income target x any active reinsurance program.
- Fixed effects: state-year, state-target, target-year.
- Standard errors: clustered by state.
- Alaska is excluded because CMS notes its state reinsurance program began operating in 2017 before
  the approved 1332 waiver period.

## Support

All years, 2017-2023:

- Person-years: 116,877.
- Persons: 66,365.
- States: 51.
- High-income target person-years: 58,372.
- Active reinsurance high-income person-years: 7,719.
- Active reinsurance states: 16.

Pre-ARPA years, 2017-2020:

- Person-years: 77,622.
- Persons: 46,029.
- States: 51.
- High-income target person-years: 38,300.
- Active reinsurance high-income person-years: 2,945.
- Active reinsurance states: 11.

## Main Estimates

Pre-ARPA 2017-2020, premium-reduction intensity per 10 percentage points:

- `direct_market`: +0.0055, state-clustered se 0.0059, t 0.93.
- `exchange_subsidy`: +0.0071, state-clustered se 0.0061, t 1.15.
- `uninsured`: -0.0017, state-clustered se 0.0052, t -0.33.
- `any_coverage`: +0.0017, state-clustered se 0.0052, t 0.33.
- `private`: -0.0062, state-clustered se 0.0069, t -0.90.
- `oop_any`: +0.0133, state-clustered se 0.0154, t 0.86.
- `doctor_any`: +0.0027, state-clustered se 0.0104, t 0.25.

Pre-ARPA 2017-2020, active reinsurance indicator:

- `direct_market`: +0.0169, state-clustered se 0.0105, t 1.61.
- `exchange_subsidy`: +0.0150, state-clustered se 0.0127, t 1.18.
- `uninsured`: +0.0044, state-clustered se 0.0133, t 0.33.
- `any_coverage`: -0.0044, state-clustered se 0.0133, t -0.33.
- `private`: -0.0215, state-clustered se 0.0152, t -1.42.
- `oop_any`: +0.0272, state-clustered se 0.0333, t 0.82.
- `doctor_any`: +0.0087, state-clustered se 0.0311, t 0.28.

All years 2017-2023, premium-reduction intensity per 10 percentage points:

- `direct_market`: +0.0031, state-clustered se 0.0052, t 0.61.
- `exchange_subsidy`: +0.0057, state-clustered se 0.0066, t 0.87.
- `uninsured`: +0.0109, state-clustered se 0.0067, t 1.63.
- `any_coverage`: -0.0109, state-clustered se 0.0067, t -1.63.
- `private`: -0.0175, state-clustered se 0.0081, t -2.17.
- `oop_any`: +0.0077, state-clustered se 0.0100, t 0.77.
- `doctor_any`: -0.0134, state-clustered se 0.0112, t -1.20.

## Verdict

`DIRECTIONAL-BUT-NOT-CLEAN`

A clean GO requires a clear positive first stage on direct-market or exchange/subsidized coverage
among the high-income exposed group, preferably with lower uninsured months. If the direct-market
signal is not coherent in the pre-ARPA screen, this should not displace the stronger SNAP EA lead.

## Artifacts

- `script/11_idea_scan/22_aca_reinsurance_fast_test.py`
- `result/idea_scan/aca_reinsurance_policy.csv`
- `result/idea_scan/aca_reinsurance_person_year_panel.parquet`
- `result/idea_scan/aca_reinsurance_support.csv`
- `result/idea_scan/aca_reinsurance_year_support.csv`
- `result/idea_scan/aca_reinsurance_estimates.csv`
