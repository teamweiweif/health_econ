# IRA Medicare Insulin Cap SIPP Fast Test

## Question

Can SIPP support a quasi-experimental paper on the 2023 Inflation Reduction Act $35 Medicare insulin cap, using Medicare beneficiaries with diabetes or daily prescription-drug use as the exposed group?

## Source Checks

- CMS IRA implementation fact sheet: https://www.cms.gov/newsroom/fact-sheets/anniversary-inflation-reduction-act-update-cms-implementation
- KFF Medicare Part D IRA changes: https://www.kff.org/medicare/changes-to-medicare-part-d-in-2024-and-2025-under-the-inflation-reduction-act-and-how-enrollees-will-benefit/
- KFF $35 insulin cap explainer: https://www.kff.org/medicare/the-facts-about-the-35-insulin-copay-cap-in-medicare/
- Johns Hopkins summary of 2026 JAMA claims study: https://publichealth.jhu.edu/2026/medicare-patients-out-of-pocket-costs-for-insulin-decrease-under-mandated-caps

Key policy timing: the Part D insulin cap began January 1, 2023; the Part B insulin cap began July 1, 2023. Current public SIPP reaches reference year 2023 through the 2024 SIPP file, so this is a one-post-year screen.

## Data Construction

- Main panel: `data/analysis_ready/sipp_2018_2024_person_month_panel.parquet`.
- Added raw health-need variables from 2021-2024 SIPP raw zip files, corresponding to reference years 2020-2023.
- Added scratch file: `temp/scratch/ira_insulin_health_need_2020_2023.parquet`.
- Diabetes proxy: any `RCONDBRIDGE1-3 == 10`.
- Broader drug-need proxy: daily prescription medication, `EDALYDRG == 1`.
- Outcomes: broad non-premium medical OOP (`TMDPAY`), high-OOP indicators, medical debt (`EDEBT_MED`), utilization checks.

Important limitation: SIPP does not identify insulin use or prescription-drug-specific OOP spending in this compact analysis. The screen therefore tests diluted proxies, not the literal insulin transaction margin.

## Support

- Age 50-90, FPL <= 1000% sample: 67,985 person-years; 42,685 persons.
- Post-2023 Medicare + diabetes-proxy cell: 419 person-years; 419 persons.
- Post-2023 Medicare + daily-prescription cell: 6,661 person-years; 6,659 persons.

## DDD Screen

Specification: weighted OLS on person-year data, age 50-90, years 2020-2023. Key coefficient is `Medicare x high-need x 2023`, with all lower-order interactions, year fixed effects, age/age-squared, FPL, sex, race/ethnicity, and disability controls. Standard errors are person-clustered.

Diabetes-proxy high need:

- OOP amount: -356.0986 (person-cluster t=-1.24).
- log OOP: -0.5131 (person-cluster t=-1.21).
- OOP > $1,000: -0.0585 (person-cluster t=-1.18).
- Medical debt: 0.0028 (person-cluster t=0.05).
- Doctor any: 0.0104 (person-cluster t=0.28).

Daily-prescription high need:

- OOP amount: 207.6508 (person-cluster t=1.75).
- log OOP: 0.2111 (person-cluster t=1.39).
- OOP > $1,000: 0.0102 (person-cluster t=0.56).
- Medical debt: -0.0117 (person-cluster t=-0.97).
- Doctor any: 0.0069 (person-cluster t=0.38).

## Decision

`IRA MEDICARE INSULIN CAP: POLICY-HOT BUT SIPP-NO-GO AS A MAIN CAUSAL PAPER`.

Why:

1. The policy is excellent and current, but the SIPP measurement is too indirect: no insulin-user flag, no Part D plan detail, and no prescription-drug-specific OOP outcome.
2. Only one post-policy SIPP reference year is currently available.
3. A 2026 JAMA claims-based study already analyzes insulin OOP directly with nearly 3.8 million insulin users, so the strongest contribution has moved to claims data rather than SIPP.
4. SIPP can still be useful as a descriptive supplement for household financial spillovers, but not as the lead causal design.

## Artifacts

- `script/11_idea_scan/34_ira_insulin_medicare_fast_test.py`
- `report/69_ira_insulin_medicare_fast_test.md`
- `result/idea_scan/ira_insulin_medicare_estimates.csv`
- `result/idea_scan/ira_insulin_medicare_support.csv`
- `result/idea_scan/ira_insulin_medicare_raw_cells.csv`
