# Childless EITC ARPA 2021 Fast Test

## Verdict

`SUPPORT-THIN`

This is a genuinely adult, non-child, non-unwinding policy idea. The 2021 American Rescue Plan
temporarily expanded the childless EITC, including younger workers who were previously excluded.
The identification hook is age eligibility, especially the old age-25 threshold.

## Why It Is Interesting

- It is a tax-and-transfer policy with current relevance: the 2021 expansion expired, and proposals
  to expand the childless EITC remain active.
- It targets adults without qualifying children, matching the requested non-child direction.
- SIPP can observe employment, earnings, insurance, Medicaid/SNAP, and medical financial outcomes.

## Main Limitation

The uploaded parquet does **not** include actual EITC receipt, tax refunds, filing status, school
enrollment, or qualifying-child tax-unit construction. Childless status is approximated as living
in a family-month with no child under 19. The test below is therefore a reduced-form feasibility
screen, not a final tax-unit design.

## Support

| design | persons | persons 2021 | treated 2021 persons | median earnings | SNAP events | Medicaid events | uninsured events |
|---|---:|---:|---:|---:|---:|---:|---:|
| age24_vs_age25 | 1622 | 273 | 142 | 15634 | 110 | 313 | 422 |
| age19_24_vs_age25_29 | 7433 | 1407 | 937 | 13600 | 571 | 1748 | 2277 |

## Primary Age-24 vs Age-25 Screen

Sample: childless low-income workers ages 24-25, 2018-2023. Treatment is age 24 in tax year 2021.
Age 24 is newly eligible in 2021 relative to the old childless EITC age-25 cutoff; age 25 is already
eligible but also affected by the larger 2021 credit, so this is conservative and imperfect.

| outcome | coef_treated_2021 | se_hc1 | t_stat | persons | treated_2021_persons |
|---|---|---|---|---|---|
| employed_all_year | 0.0597 | 0.0744 | 0.8025 | 1622 | 142 |
| employed_any_year | 0.0000 | 0.0000 | 0.5727 | 1622 | 142 |
| log_earnings_plus1 | 0.1041 | 0.1510 | 0.6897 | 1622 | 142 |
| medicaid_any | -0.0856 | 0.0493 | -1.7351 | 1622 | 142 |
| oop_any | -0.0739 | 0.0726 | -1.0192 | 1622 | 142 |
| private_any | 0.0373 | 0.0666 | 0.5600 | 1622 | 142 |
| snap_any | 0.0075 | 0.0400 | 0.1871 | 1622 | 142 |
| uninsured_any | -0.0058 | 0.0648 | -0.0894 | 1622 | 142 |

## Interpretation

- This is more innovative than age-26 or age-65 insurance thresholds.
- The policy shock is real and the sample is not tiny.
- It is not yet a clean top-field design because the current parquet lacks actual tax-unit and
  student-status variables.
- A stronger version needs richer SIPP variables or an IRS/SIPP-linked tax measure. Without that,
  this remains a promising concept rather than an immediate paper.

## Source Checks

- IRS EITC eligibility page:
  https://www.irs.gov/credits-deductions/individuals/earned-income-tax-credit/who-qualifies-for-the-earned-income-tax-credit-eitc
- Tax Policy Center summary of the ARPA childless EITC expansion:
  https://taxpolicycenter.org/publications/how-american-rescue-plans-temporary-eitc-expansion-impacted-workers-without-children
- CRS summary of ARPA 2021, including childless EITC age changes:
  https://www.everycrsreport.com/reports/R46680.html
- NBER working paper on expanded EITC for childless young adults:
  https://www.nber.org/system/files/working_papers/w32571/w32571.pdf

## Outputs

- `result/idea_scan/childless_eitc_person_year_panel.csv`
- `result/idea_scan/childless_eitc_fast_estimates.csv`
- `result/idea_scan/childless_eitc_support.csv`
