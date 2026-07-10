# Sixteenth-Round ACA Reinsurance Decision

## Question

Can state ACA Section 1332 reinsurance waivers support an adult SIPP paper on Marketplace coverage,
insurance affordability, and medical-financial outcomes?

## Why This Was Worth Testing

This is one of the better insurance-side candidates in principle:

- it is adult, non-child, and non-unwinding;
- it has multi-state policy timing inside the SIPP window;
- CMS reports actual state-year premium reductions under the waivers;
- SIPP directly observes monthly insurance coverage, direct purchase / Marketplace indicators,
  exchange/subsidy indicators, doctor visits, and medical out-of-pocket spending;
- the natural exposed group is adults above 400% FPL, especially before ARPA removed the hard
  subsidy cliff.

The potential gap is a household survey angle on coverage and financial spillovers, rather than only
premium or administrative enrollment effects. That gap is real, but it requires a clear first stage
in SIPP Marketplace coverage.

## Source Checks

- KFF Section 1332 waiver tracker:
  https://www.kff.org/affordable-care-act/tracking-section-1332-state-innovation-waivers/
- CMS CCIIO 2024 Section 1332 data brief:
  https://www.cms.gov/files/document/cciio-data-brief-042024-508-final.pdf

KFF describes Section 1332 waivers as ACA state innovation waivers and notes that most approved
waivers have been used for state reinsurance programs. CMS reports state first years of operation
and actual SLCSP premium reductions from 2018 through 2023. The fast screen uses those CMS
state-year premium reductions.

## Design

Source:

- `data/analysis_ready/sipp_2018_2024_person_month_panel.parquet`

Unit:

- person-year, collapsed from monthly SIPP observations.

Sample:

- age 26-64;
- family income 138-1000% FPL;
- at least six observed months;
- Alaska excluded because CMS notes Alaska's reinsurance program began operating in 2017 before the
  approved 1332 waiver period.

Primary exposed group:

- 400-1000% FPL adults.

Comparison group:

- 138-400% FPL adults in the same state-years.

Treatment:

- high-income target x actual CMS SLCSP premium reduction, scaled per 10 percentage points;
- sensitivity: high-income target x active reinsurance indicator.

Fixed effects:

- state-year;
- state-target;
- target-year.

Standard errors:

- clustered by state.

## Support

All years, 2017-2023:

- 116,877 person-years.
- 66,365 persons.
- 51 states.
- 58,372 high-income target person-years.
- 7,719 active reinsurance high-income person-years.
- 16 active reinsurance states.

Pre-ARPA years, 2017-2020:

- 77,622 person-years.
- 46,029 persons.
- 51 states.
- 38,300 high-income target person-years.
- 2,945 active reinsurance high-income person-years.
- 11 active reinsurance states.

Support is good enough for a real screen. This is not a small-cell failure.

## Main Results

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

## Interpretation

This is not a clean GO:

- the pre-ARPA direct-market first stage is positive but small and not robust to the continuous
  premium-reduction intensity;
- uninsured does not fall in the active-policy specification;
- all-year estimates become less credible because ARPA changed the meaning of the 400% FPL exposure
  group and the uninsured estimate turns positive;
- private coverage moves negative in the all-year model;
- SIPP cannot observe premiums, plan choices, silver loading, gross-vs-net premium exposure, or
  whether a person was actually shopping in the individual market.

The policy variation and support are better than several earlier single-state Marketplace subsidy
ideas, but the result is still too weak for a top-field causal paper.

## Decision

`ACA REINSURANCE: DIRECTIONAL INSURANCE SIGNAL, BUT NO CLEAN GO`

This should remain on the insurance-side shortlist, but below the ACA enhanced PTC and family-glitch
ideas. It can be useful background if the project pivots to a broader ACA affordability portfolio,
but it should not displace the SNAP Emergency Allotment lead.

## Updated Ranking

1. **SNAP Emergency Allotment termination**: best current conditional lead; household-level
   `food_insecure` rises about 7.6pp for lagged-SNAP households in early-ending states, but support
   is thin and secondary food outcomes are imprecise.
2. **ACA enhanced PTC / 400% FPL with premium intensity**: best insurance-policy gap, but dynamic
   checks failed.
3. **ACA family glitch fix**: best insurance-side conditional lead; current compact parquet lacks
   actual employer offer/premium eligibility variables.
4. **ACA state reinsurance waivers**: multi-state timing and good support, but SIPP first stage is
   only weakly directional and uninsured does not improve.
5. **Maryland young-adult Marketplace subsidy**: clean design, but treatment cell is too small.
6. **New Jersey Health Plan Savings**: plausible, but bundled with ARPA, SBE transition, and state
   mandate.
7. **Adult Medicaid dental benefits**: strong policy/outcome fit, but treated support is too small
   and estimates are wrong-signed.
8. **State paid sick leave mandates**: policy variation exists, but no direct leave first stage and
   no coherent reduced-form pattern.
9. **State individual mandates**: weak Marketplace signal.
10. **Postpartum Medicaid extension**: important adult maternal-coverage policy, but compact SIPP has
    no direct birth/pregnancy variables and tiny support.
11. **Minimum-wage food-security spillovers**: support is large, but the main food-security signal is
    null or wrong-signed and exposure is too crude for this crowded literature.
12. **Washington Working Families Tax Credit**: policy is strong, but 2023 treated support and tax
    eligibility measurement are too weak.
13. **Pandemic UI early termination**: clean timing, but no-go even with food-security outcomes.
14. **No Surprises Act**: excellent policy, SIPP measurement too indirect.
15. **STLDI expansion/state regulation**: no coherent SIPP signal.
16. **State-Based Marketplace transitions**: wrong-signed dynamics.

## New Artifacts

- `script/11_idea_scan/22_aca_reinsurance_fast_test.py`
- `report/46_aca_reinsurance_fast_test.md`
- `result/idea_scan/aca_reinsurance_policy.csv`
- `result/idea_scan/aca_reinsurance_person_year_panel.parquet`
- `result/idea_scan/aca_reinsurance_support.csv`
- `result/idea_scan/aca_reinsurance_year_support.csv`
- `result/idea_scan/aca_reinsurance_estimates.csv`
