# Fourteenth-Round Washington WFTC Decision

## Question

Can Washington's 2023 Working Families Tax Credit launch support an adult low-wage-worker SIPP paper?

## Why This Was Worth Testing

This is an adult, non-child, non-unwinding candidate. It is also current and policy relevant:

- it is a state refundable credit targeted to low- and moderate-income workers;
- it launched recently enough to be inside the 2018-2023 SIPP reference window;
- current policy debates still include state EITC/working-family credits and tax refunds for
  low-income workers;
- the compact parquet contains earnings, employment, FPL, food security, SNAP, coverage, doctor
  visits, and medical out-of-pocket outcomes.

The main question is whether the uploaded compact parquet can identify likely eligible workers and
has enough Washington 2023 support.

## Source Checks

- Washington Working Families Tax Credit official site:
  https://workingfamiliescredit.wa.gov/
- Washington Working Families Tax Credit eligibility page:
  https://workingfamiliescredit.wa.gov/eligibility
- Washington Department of Revenue WFTC application window release:
  https://dor.wa.gov/about/news-releases/2026/working-families-tax-credit-application-window-opens-feb-1
- NCSL Earned Income Tax Credit Overview:
  https://www.ncsl.org/human-services/earned-income-tax-credit-overview

Official Washington sources describe the WFTC as a tax credit for Washington workers. Eligibility
requires Washington residence, being at least 25 and under 65 or having a qualifying child, filing a
federal tax return, and federal EITC or ITIN-equivalent eligibility. Washington Department of Revenue
states the program launched in 2023.

## Design

Source:

- `data/analysis_ready/sipp_2018_2024_person_month_panel.parquet`

Unit:

- person-year, 2018-2023.

Geography:

- Washington vs regional controls: California, Colorado, Idaho, Montana, Oregon.

Primary target:

- age 25-64;
- FPL <= 300%;
- annual earnings $1-$40,000;
- employed in at least half of observed months.

Treatment:

- Washington x 2023 x target worker.

Fixed effects:

- state-year;
- state-target;
- target-year.

Main outcomes:

- food insecurity;
- food security score;
- SNAP;
- uninsured;
- medical out-of-pocket spending;
- earnings.

## Compact-Parquet Limitation

The compact parquet does not observe:

- federal tax filing;
- federal EITC eligibility;
- WFTC application;
- WFTC receipt;
- refund timing;
- exact tax-unit structure;
- ITIN/SSN eligibility.

This is therefore a reduced-form proxy screen, not a final tax-credit design.

## Support

Primary low-wage worker target:

- 60,842 person-years.
- 32,337 persons.
- 4,850 target person-years.
- 50 Washington 2023 target person-years.
- 50 Washington 2023 target persons.

Broad worker sensitivity:

- 8,088 target person-years.
- 101 Washington 2023 target person-years.

The relevant treated cell is too small for a single-state launch design.

## Main Results

Primary low-wage worker target:

- `food_insecure`: -0.0147, se 0.0602.
- `very_low_food`: -0.0201, se 0.0377.
- `food_score`: -0.1062, se 0.2636.
- `snap_any`: -0.0548, se 0.0445.
- `uninsured`: +0.0374, se 0.0749.
- `oop_any`: +0.1447, se 0.0857.
- `log_earnings`: +0.3559, se 0.3141.

Broad worker sensitivity:

- `food_insecure`: +0.0150, se 0.0474.
- `food_score`: -0.0168, se 0.1923.
- `snap_any`: -0.0512, se 0.0268.
- `uninsured`: +0.0429, se 0.0513.
- `oop_any`: +0.0450, se 0.0616.
- `log_earnings`: +0.3074, se 0.2482.

There is no coherent food-security or medical-financial improvement signal.

## Decision

`WASHINGTON WFTC: NO-GO FROM CURRENT COMPACT SIPP`

This is a good policy idea in principle, but not a viable immediate SIPP paper from the uploaded
parquet:

- the single treated state-year has only 50 primary target person-years;
- even broadening the target gives only 101 treated person-years;
- tax filing, EITC eligibility, and WFTC receipt are unobserved;
- the estimated food-security effects are near zero or mixed;
- a single-state 2023 design has little room for pretrend/event-study validation.

This direction should not displace the SNAP EA lead.

## Updated Ranking

1. **SNAP Emergency Allotment termination**: best current conditional lead; household-level
   `food_insecure` rises about 7.6pp for lagged-SNAP households in early-ending states, but support
   is thin and secondary food outcomes are imprecise.
2. **ACA enhanced PTC / 400% FPL with premium intensity**: best insurance-policy gap, but dynamic
   checks failed.
3. **ACA family glitch fix**: best insurance-side conditional lead; current compact parquet lacks
   actual employer offer/premium eligibility variables.
4. **Maryland young-adult Marketplace subsidy**: clean design, but treatment cell is too small.
5. **New Jersey Health Plan Savings**: plausible, but bundled with ARPA, SBE transition, and state
   mandate.
6. **Adult Medicaid dental benefits**: strong policy/outcome fit, but treated support is too small
   and estimates are wrong-signed.
7. **State paid sick leave mandates**: policy variation exists, but no direct leave first stage and
   no coherent reduced-form pattern.
8. **State individual mandates**: weak Marketplace signal.
9. **Postpartum Medicaid extension**: important adult maternal-coverage policy, but compact SIPP has
   no direct birth/pregnancy variables and tiny support.
10. **Washington Working Families Tax Credit**: policy is strong, but 2023 treated support and tax
    eligibility measurement are too weak.
11. **Pandemic UI early termination**: clean timing, but no-go even with food-security outcomes.
12. **No Surprises Act**: excellent policy, SIPP measurement too indirect.
13. **STLDI expansion/state regulation**: no coherent SIPP signal.
14. **State-Based Marketplace transitions**: wrong-signed dynamics.

## New Artifacts

- `script/11_idea_scan/20_washington_wftc_fast_test.py`
- `report/42_washington_wftc_fast_test.md`
- `result/idea_scan/washington_wftc_person_year_panel.parquet`
- `result/idea_scan/washington_wftc_support.csv`
- `result/idea_scan/washington_wftc_estimates.csv`
