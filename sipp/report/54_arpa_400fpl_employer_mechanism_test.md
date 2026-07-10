# ARPA 400% FPL Employer-Coverage Mechanism Test

## Purpose

This is a supplemental validation of the leading ARPA 400% FPL cliff design. The prior compact
analysis-ready parquet did not include `RPRITYPE1`, the monthly employer-related private coverage
recode. This script extracts `RPRITYPE1` directly from the local raw Census SIPP zips and merges it
back onto the person-month panel by `file_year`, `SSUID`, `PNUM`, and `MONTHCODE`.

## Source and Merge Check

- Raw zips: `temp/raw_downloads/census_sipp/YYYY/primary/puYYYY_csv.zip`.
- Supplemental extract: `temp/scratch/rpritype1_2018_2024.parquet`.
- Merge key: `file_year + SSUID + PNUM + MONTHCODE`.
- Main sample missing `RPRITYPE1` rows after merge: 26,281.

## Main Support

- Main model: age 26-64, non-Medicare, 350-450% monthly FPL.
- Person-months: 217,610.
- Persons: 23,755.
- States: 52.

## Raw Cell Means

| post | above | person_months | persons | uninsured | employer_private | direct_purchase | marketplace_flag | market_or_subsidy | private |
|---|---|---|---|---|---|---|---|---|---|
| 0.0000 | 0.0000 | 75922.0000 | 10628.0000 | 0.1129 | 0.6706 | 0.0983 | 0.0688 | 0.0992 | 0.8296 |
| 0.0000 | 1.0000 | 69184.0000 | 9892.0000 | 0.0957 | 0.6946 | 0.0902 | 0.0640 | 0.0909 | 0.8607 |
| 1.0000 | 0.0000 | 38834.0000 | 6173.0000 | 0.1102 | 0.6480 | 0.1216 | 0.1000 | 0.1228 | 0.8102 |
| 1.0000 | 1.0000 | 33670.0000 | 5562.0000 | 0.0861 | 0.7052 | 0.1055 | 0.0816 | 0.1058 | 0.8470 |

## Main Estimates

Monthly FPL, age 26-64, post = 2021-2023:

- `uninsured`: -0.0263, HC1 se 0.0072, t -3.67; person-cluster se 0.0143, t -1.84.
- `any_coverage`: +0.0263, HC1 se 0.0072, t 3.67; person-cluster se 0.0143, t 1.84.
- `employer_private`: +0.0311, HC1 se 0.0092, t 3.37; person-cluster se 0.0187, t 1.67.
- `direct_purchase`: +0.0222, HC1 se 0.0068, t 3.27; person-cluster se 0.0137, t 1.63.
- `marketplace_flag`: +0.0197, HC1 se 0.0061, t 3.22; person-cluster se 0.0123, t 1.61.
- `market_or_subsidy`: +0.0218, HC1 se 0.0068, t 3.20; person-cluster se 0.0137, t 1.59.
- `private`: +0.0237, HC1 se 0.0086, t 2.77; person-cluster se 0.0171, t 1.39.
- `public`: +0.0081, HC1 se 0.0064, t 1.27; person-cluster se 0.0132, t 0.62.
- `medicaid`: +0.0033, HC1 se 0.0058, t 0.57; person-cluster se 0.0117, t 0.28.

Monthly FPL, age 21-64 sensitivity:

- `uninsured`: -0.0313, HC1 se 0.0068, t -4.60; person-cluster se 0.0137, t -2.28.
- `any_coverage`: +0.0313, HC1 se 0.0068, t 4.60; person-cluster se 0.0137, t 2.28.
- `employer_private`: +0.0325, HC1 se 0.0088, t 3.68; person-cluster se 0.0179, t 1.81.
- `direct_purchase`: +0.0218, HC1 se 0.0067, t 3.27; person-cluster se 0.0132, t 1.66.
- `marketplace_flag`: +0.0174, HC1 se 0.0060, t 2.87; person-cluster se 0.0119, t 1.46.
- `market_or_subsidy`: +0.0225, HC1 se 0.0067, t 3.36; person-cluster se 0.0132, t 1.70.

Monthly FPL, age 26-64, post = April 2021 onward:

- `uninsured`: -0.0296, HC1 se 0.0074, t -4.03; person-cluster se 0.0147, t -2.01.
- `any_coverage`: +0.0296, HC1 se 0.0074, t 4.03; person-cluster se 0.0147, t 2.01.
- `employer_private`: +0.0338, HC1 se 0.0095, t 3.56; person-cluster se 0.0193, t 1.75.
- `direct_purchase`: +0.0258, HC1 se 0.0070, t 3.69; person-cluster se 0.0141, t 1.83.
- `marketplace_flag`: +0.0270, HC1 se 0.0063, t 4.26; person-cluster se 0.0127, t 2.12.
- `market_or_subsidy`: +0.0253, HC1 se 0.0070, t 3.61; person-cluster se 0.0142, t 1.79.

Annual FPL sensitivity:

- `uninsured`: -0.0301, HC1 se 0.0070, t -4.33; person-cluster se 0.0226, t -1.33.
- `any_coverage`: +0.0301, HC1 se 0.0070, t 4.33; person-cluster se 0.0226, t 1.33.
- `employer_private`: +0.0479, HC1 se 0.0092, t 5.21; person-cluster se 0.0309, t 1.55.
- `direct_purchase`: -0.0243, HC1 se 0.0067, t -3.62; person-cluster se 0.0230, t -1.06.
- `marketplace_flag`: -0.0192, HC1 se 0.0061, t -3.16; person-cluster se 0.0208, t -0.92.
- `market_or_subsidy`: -0.0240, HC1 se 0.0067, t -3.58; person-cluster se 0.0230, t -1.05.

## Interpretation

The employer coverage variable materially improves the mechanism audit. A clean ARPA cliff story
should show that the uninsured decline is not simply employer coverage substitution. The key check
is therefore whether `employer_private` moves little relative to direct purchase / Marketplace
proxies in the same difference-in-discontinuities design.

## Artifacts

- `script/11_idea_scan/26_arpa_400fpl_employer_mechanism_test.py`
- `temp/scratch/rpritype1_2018_2024.parquet`
- `result/idea_scan/arpa400_employer_mechanism_estimates.csv`
- `result/idea_scan/arpa400_employer_mechanism_cell_means.csv`
- `result/idea_scan/arpa400_employer_mechanism_support.csv`
