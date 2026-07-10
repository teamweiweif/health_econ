# Student Loan Repayment Resumption SIPP Screen

## Question

Can SIPP support a publishable adult-policy causal design around the resumption of federal student loan payments in October 2023, using prior student-loan debt holders as the exposed group and measuring coverage, care use, medical spending, and hardship outcomes?

## Source Checks

- GAO student loan repayment status blog: https://www.gao.gov/blog/when-student-loan-payment-pause-ended-did-borrowers-pay
- NCUA Letter to Credit Unions on resumption of federal student loan payments: https://ncua.gov/regulation-supervision/letters-credit-unions-other-guidance/resumption-federal-student-loan-payments
- U.S. Department of Education 2025 repayment/collections release: https://www.ed.gov/about/news/press-release/us-department-of-education-begin-federal-student-loan-collections-other-actions-help-borrowers-get-back-repayment

Policy timing used here: the pandemic-era federal student loan payment pause ended before the 2023 repayment restart; interest resumed in September 2023 and payments restarted in October 2023. Federal agencies also described an October 2023-September 2024 on-ramp, which weakens immediate delinquency consequences and makes a large short-run SIPP signal less likely.

## Construction

- Base panel: `data/analysis_ready/sipp_2018_2024_person_month_panel.parquet`.
- Raw financial supplement: `temp/scratch/student_loan_financial_vars_2018_2024.parquet`.
- Exposure: prior-year student/education debt from `EDEBT_ED`, `TDEBT_ED`, `TOEDDEBTVAL`, and joint education-debt fields.
- Main monthly design: adult non-Medicare person-months age 25-64, years 2019-2023, excluding September; key coefficient is prior student debt x October-December x 2023.
- Annual-pair design: changes from baseline year to following year, with the 2022->2023 pair as the treated restart pair.
- Outcomes: insurance coverage, direct-market/exchange proxies, annual health care use/spending proxies, rent/mortgage hardship, food insecurity, medical debt, credit-card debt, and bank assets.

Measurement caveat: SIPP observes student/education debt, not federal-loan repayment obligation, servicer status, monthly payment due, SAVE/IDR enrollment, delinquency, default, or the exact restart month for each borrower. This is a major identification limitation.

## Support

- 2023 October-December monthly exposed support: 2,859 person-months; 974 persons.
- 2022->2023 annual-pair exposed support: 940 persons.

| panel | exposure | year | oct_dec | exposed | rows | persons | states | weighted_uninsured | weighted_direct_market | weighted_oop_any |
|---|---|---|---|---|---|---|---|---|---|---|
| monthly | student_debt_prev | 2022 | 0 | 0 | 56185 | 7404 | 48 | 0.1186 | 0.1562 | 0.5769 |
| monthly | student_debt_prev | 2022 | 0 | 1 | 9455 | 1255 | 44 | 0.0660 | 0.1273 | 0.7017 |
| monthly | student_debt_prev | 2022 | 1 | 0 | 20741 | 7033 | 48 | 0.1173 | 0.1578 | 0.5819 |
| monthly | student_debt_prev | 2022 | 1 | 1 | 3540 | 1205 | 44 | 0.0663 | 0.1282 | 0.7151 |
| monthly | student_debt_prev | 2023 | 0 | 0 | 48640 | 6401 | 44 | 0.1144 | 0.1689 | 0.5993 |
| monthly | student_debt_prev | 2023 | 0 | 1 | 7666 | 1024 | 44 | 0.0586 | 0.1401 | 0.7297 |
| monthly | student_debt_prev | 2023 | 1 | 0 | 18011 | 6121 | 44 | 0.1133 | 0.1694 | 0.6037 |
| monthly | student_debt_prev | 2023 | 1 | 1 | 2859 | 974 | 43 | 0.0570 | 0.1304 | 0.7411 |

## Raw Cells

| model | exposure | resume_2023 | oct_dec | exposed | rows | persons | uninsured | direct_market | oop_any | doctor_any |
|---|---|---|---|---|---|---|---|---|---|---|
| monthly_octdec_ddd | student_debt_prev | 0 | 0.0000 | 0 | 217778 | 20096 | 0.1278 | 0.1482 | 0.5736 | 0.7155 |
| monthly_octdec_ddd | student_debt_prev | 0 | 0.0000 | 1 | 39621 | 4091 | 0.0788 | 0.1079 | 0.6813 | 0.7468 |
| monthly_octdec_ddd | student_debt_prev | 0 | 1.0000 | 0 | 80007 | 19041 | 0.1274 | 0.1490 | 0.5792 | 0.7237 |
| monthly_octdec_ddd | student_debt_prev | 0 | 1.0000 | 1 | 14762 | 3906 | 0.0756 | 0.1094 | 0.6928 | 0.7582 |
| monthly_octdec_ddd | student_debt_prev | 1 | 0.0000 | 0 | 48640 | 6401 | 0.1144 | 0.1689 | 0.5993 | 0.7389 |
| monthly_octdec_ddd | student_debt_prev | 1 | 0.0000 | 1 | 7666 | 1024 | 0.0586 | 0.1401 | 0.7297 | 0.8131 |
| monthly_octdec_ddd | student_debt_prev | 1 | 1.0000 | 0 | 18011 | 6121 | 0.1133 | 0.1694 | 0.6037 | 0.7473 |
| monthly_octdec_ddd | student_debt_prev | 1 | 1.0000 | 1 | 2859 | 974 | 0.0570 | 0.1304 | 0.7411 | 0.8257 |

## Monthly DDD Estimates

Main exposure: prior-year student debt. Coefficients are on `student_debt_prev x Oct-Dec x 2023`.

- Uninsured: +0.0025 (person-cluster se 0.0081, t 0.31; treated post persons 974).
- Any coverage: -0.0025 (person-cluster se 0.0081, t -0.31; treated post persons 974).
- Direct-market coverage: -0.0080 (person-cluster se 0.0078, t -1.02; treated post persons 974).
- Exchange/subsidy proxy: -0.0042 (person-cluster se 0.0075, t -0.56; treated post persons 974).
- OOP-any proxy: +0.0009 (person-cluster se 0.0053, t 0.18; treated post persons 974).
- Doctor-any proxy: +0.0005 (person-cluster se 0.0049, t 0.09; treated post persons 974).

High-debt sensitivity, prior student debt > $25,000:

- Uninsured: +0.0078 (person-cluster se 0.0103, t 0.76; treated post persons 391).
- OOP-any proxy: +0.0021 (person-cluster se 0.0085, t 0.24; treated post persons 391).
- Doctor-any proxy: +0.0069 (person-cluster se 0.0079, t 0.87; treated post persons 391).

## Annual-Pair Estimates

Main exposure: baseline student debt. Coefficients are on `student_debt_base x 2022->2023`.

- Food insecurity change: +0.0102 (person-cluster se 0.0214, t 0.47; treated post persons 940).
- Rent/mortgage hardship change: -0.0153 (person-cluster se 0.0131, t -1.17; treated post persons 940).
- Medical debt change: +0.0237 (person-cluster se 0.0174, t 1.36; treated post persons 940).
- Credit-card debt change: +0.0016 (person-cluster se 0.0218, t 0.07; treated post persons 940).
- Uninsured change: -0.0056 (person-cluster se 0.0127, t -0.44; treated post persons 940).
- Direct-market change: +0.0033 (person-cluster se 0.0151, t 0.22; treated post persons 940).

## Decision

`STUDENT LOAN REPAYMENT RESUMPTION: NO-GO AS MAIN SIPP HEALTH-INSURANCE PAPER`.

The event is nationally important and the exposed sample is large enough, but SIPP lacks the decisive exposure and outcome variables for a top-field causal paper. The policy shock is federal, timing is concentrated in only three observable post-restart months, the on-ramp intentionally muted immediate adverse credit consequences, and public SIPP cannot separate federal loans from private education debt or observe actual payment-due changes.

This can be a discarded diagnostic or a short descriptive appendix about household financial strain among debt holders, but it should not displace the ARPA 400% FPL subsidy-cliff design.

## Artifacts

- `script/11_idea_scan/39_student_loan_repayment_resumption_test.py`
- `report/78_student_loan_repayment_resumption_test.md`
- `report/79_thirtyfirst_round_student_loan_repayment_decision.md`
- `result/idea_scan/student_loan_repayment_monthly_panel.parquet`
- `result/idea_scan/student_loan_repayment_annual_pairs.parquet`
- `result/idea_scan/student_loan_repayment_estimates.csv`
- `result/idea_scan/student_loan_repayment_support.csv`
- `result/idea_scan/student_loan_repayment_raw_cells.csv`
- `result/idea_scan/student_loan_repayment_annual_support.csv`
