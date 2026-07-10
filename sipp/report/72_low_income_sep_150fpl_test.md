# Low-Income 150% FPL Marketplace SEP Fast Test

## Question

Did the 2022 low-income monthly Marketplace Special Enrollment Period for people at or below 150% FPL increase off-season Marketplace/direct-purchase coverage among adults just below the 150% FPL threshold?

## Source Checks

- CMS 150% FPL SEP online functionality bulletin: https://content.govdelivery.com/accounts/USCMSHIM/bulletins/30fd85c
- KFF Marketplace enrollment-period FAQ on 150% FPL SEP: https://www.kff.org/faqs/faqs-health-insurance-marketplace-and-the-aca/marketplace-enrollment-periods/i-hear-there-is-a-new-special-enrollment-opportunity-in-2022-for-people-with-very-low-income-how-does-that-work/
- CMS 2027 proposed rule fact sheet discussing removal of the 150% FPL SEP after PY2026: https://www.cms.gov/newsroom/fact-sheets/hhs-notice-benefit-payment-parameters-2027-proposed-rule
- Federal Register 2027 payment parameters discussion of the 150% FPL SEP: https://www.federalregister.gov/documents/2026/05/20/2026-10050/patient-protection-and-affordable-care-act-hhs-notice-of-benefit-and-payment-parameters-for-2027-and

Policy logic: CMS made a low-income SEP available for consumers at or below 150% FPL, with HealthCare.gov online functionality live in March 2022. The issue is current again because CMS and the 2026-2027 rulemaking discuss removal/continued prohibition of this SEP after enhanced subsidy changes.

## Design

Unit: person-month.

Main sample:

- adults ages 26-64;
- non-Medicare;
- monthly FPL 138-200%;
- target group 138-150% FPL;
- comparison group 150-200% FPL;
- off-season months March-October only;
- pre years 2018-2019 and post years 2022-2023;
- 2020 and 2021 excluded because they contain pandemic disruption, COVID SEP, and broad ARPA rollout;
- states with overlapping SBM platform transitions excluded: KY, ME, NJ, NM, PA.

Treatment contrast:

- HealthCare.gov states versus stable full State-Based Marketplace states.
- This is intentionally conservative because some SBMs may have adopted similar low-income SEP policies, which would attenuate the contrast.

Key coefficient:

- `HealthCare.gov state x 138-150% FPL target x post-2022`.

Fixed effects and controls:

- state fixed effects;
- year-month fixed effects;
- age, FPL, sex, race/ethnicity, disability, Medicaid.

## Support

- Main sample: 47,048 person-months; 8,208 persons; 47 states.
- HealthCare.gov target-post cell: 2,361 person-months; 600 persons.
- Stable SBM target-post cell: 1,085 person-months; 286 persons.
- No-Medicaid sensitivity sample: 34,128 person-months; 6,086 persons.
- Broad 100-150% no-Medicaid sensitivity sample: 49,823 person-months; 8,104 persons.

## Results

Main sample, state-clustered:

- Uninsured: -0.0278 (state_fips t=-0.82).
- Direct purchase: 0.0221 (state_fips t=0.38).
- Marketplace flag: 0.0154 (state_fips t=0.31).
- Subsidized private: 0.0509 (state_fips t=1.14).
- Market/subsidy composite: 0.0174 (state_fips t=0.29).
- Medicaid: 0.0000 (state_fips t=2.16).

No-Medicaid sensitivity, state-clustered:

- Uninsured: -0.0197 (state_fips t=-0.36).
- Direct purchase: 0.0904 (state_fips t=1.50).
- Marketplace flag: 0.0947 (state_fips t=1.93).
- Market/subsidy composite: 0.0904 (state_fips t=1.50).

Broad 100-150% FPL no-Medicaid sensitivity, state-clustered:

- Uninsured: 0.0363 (state_fips t=0.52).
- Direct purchase: 0.0328 (state_fips t=0.59).
- Marketplace flag: -0.0085 (state_fips t=-0.21).
- Market/subsidy composite: 0.0328 (state_fips t=0.59).

## Decision

`150% FPL LOW-INCOME MARKETPLACE SEP: PLAUSIBLE POLICY GAP, BUT SIPP SCREEN IS NO-GO / APPENDIX ONLY`.

Why:

1. The policy question is current and real: the 150% FPL SEP was created as a low-income access tool and is now being removed/restricted in current rulemaking.
2. The design is cleaner than generic ARPA low-income comparisons because it isolates off-season months and the 150% FPL threshold.
3. But the usable threshold window is narrow, and Medicaid eligibility around 138% FPL creates contamination.
4. The HealthCare.gov-versus-SBM treatment contrast is imperfect because state-based exchanges may have parallel policies or different outreach.
5. The screen must show a large, clean direct-purchase/Marketplace effect to justify further work. The first-pass estimates do not clear that bar.

## Artifacts

- `script/11_idea_scan/36_low_income_sep_150fpl_test.py`
- `report/72_low_income_sep_150fpl_test.md`
- `result/idea_scan/low_income_sep_150fpl_estimates.csv`
- `result/idea_scan/low_income_sep_150fpl_support.csv`
- `result/idea_scan/low_income_sep_150fpl_raw_cells.csv`
