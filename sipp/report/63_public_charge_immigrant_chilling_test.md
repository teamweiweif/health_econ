# Public Charge Immigrant Chilling Effect Quick Screen

## Purpose

This test revisits a previously deferred adult idea: whether the Trump-era public charge rule
chilled Medicaid, SNAP, and coverage among low-income noncitizen adults. The compact SIPP parquet
did not include citizenship/nativity variables, so this script extracts `ECITIZEN`, `EBORNUS`, and
`ENATCIT` from the local raw SIPP CSV zips and merges them back to the person-month panel.

## Policy Timing Used

- Pre period: reference years 2017-2018.
- Chilling / final-rule period: reference years 2019-2020.
- Reversal / post-rule period: reference years 2021-2023.

The exact rule implementation was February 24, 2020, and DHS stopped applying the 2019 rule on
March 9, 2021. The broader chilling period starts earlier because the final rule was published in
2019 and the policy debate/reaction began before implementation.

## Supplemental Extraction

- Source raw zips: `temp/raw_downloads/census_sipp/YYYY/primary/puYYYY_csv.zip`.
- Extracted variables: `SSUID`, `PNUM`, `MONTHCODE`, `ECITIZEN`, `ACITIZEN`, `EBORNUS`, `ABORNUS`,
  `ENATCIT`, `ANATCIT`.
- Cached extract: `temp/scratch/immigration_status_2018_2024.parquet`.
- Merge key: `file_year + SSUID + PNUM + MONTHCODE`.

## Citizenship Variable Counts

| variable | value | rows |
|---|---|---|
| ECITIZEN | 1 | 3830076 |
| ECITIZEN | 2 | 221379 |
| EBORNUS | 1 | 3443557 |
| EBORNUS | 2 | 607898 |
| ENATCIT | 1 | 253185 |
| ENATCIT | 2 | 4464 |
| ENATCIT | 3 | 4819 |
| ENATCIT | 4 | 3443557 |
| ENATCIT | 5 | 124051 |
| ENATCIT | <NA> | 221379 |

## Model Support

| spec | person_months | persons | states | noncitizen_person_months | low_noncitizen_person_months | low_noncitizen_persons |
|---|---|---|---|---|---|---|
| monthly_low250 | 1543116 | 79568 | 52 | 150321 | 93408 | 5770 |
| monthly_low150 | 1543116 | 79568 | 52 | 150321 | 56043 | 4184 |
| annual_low250 | 1523390 | 74655 | 52 | 149555 | 92403 | 5032 |

## Raw Cell Means

Monthly FPL low-income cutoff at 250% FPL.

| period | noncitizen | low250 | person_months | persons | medicaid | snap_month | uninsured | public | private |
|---|---|---|---|---|---|---|---|---|---|
| chill_2019_2020 | 0 | 0 | 247352 | 21286 | 0.0830 | 0.0210 | 0.1047 | 0.0990 | 0.8274 |
| chill_2019_2020 | 0 | 1 | 198057 | 17080 | 0.3173 | 0.1731 | 0.2315 | 0.3306 | 0.4855 |
| chill_2019_2020 | 1 | 0 | 16150 | 1469 | 0.1088 | 0.0108 | 0.2527 | 0.1095 | 0.6577 |
| chill_2019_2020 | 1 | 1 | 26774 | 2042 | 0.2683 | 0.1022 | 0.4577 | 0.2713 | 0.2890 |
| pre_2017_2018 | 0 | 0 | 261370 | 21600 | 0.0732 | 0.0183 | 0.0997 | 0.0878 | 0.8418 |
| pre_2017_2018 | 0 | 1 | 229668 | 18551 | 0.3043 | 0.1833 | 0.2368 | 0.3185 | 0.4858 |
| pre_2017_2018 | 1 | 0 | 20224 | 1805 | 0.1050 | 0.0176 | 0.2483 | 0.1065 | 0.6761 |
| pre_2017_2018 | 1 | 1 | 36985 | 2770 | 0.2643 | 0.1058 | 0.4400 | 0.2646 | 0.3273 |
| reversal_2021_2023 | 0 | 0 | 256743 | 19813 | 0.1132 | 0.0287 | 0.0944 | 0.1268 | 0.8174 |
| reversal_2021_2023 | 0 | 1 | 199605 | 15576 | 0.3611 | 0.1795 | 0.2011 | 0.3726 | 0.4851 |
| reversal_2021_2023 | 1 | 0 | 20539 | 1705 | 0.1456 | 0.0200 | 0.2853 | 0.1458 | 0.5945 |
| reversal_2021_2023 | 1 | 1 | 29649 | 2076 | 0.2999 | 0.0783 | 0.4463 | 0.3032 | 0.2843 |

## DDD Design

Main term:

- `noncitizen x low_income x chill_2019_2020`

Reversal term:

- `noncitizen x low_income x reversal_2021_2023`

Controls and fixed effects:

- state fixed effects;
- calendar year-month fixed effects;
- FPL quadratic;
- age quadratic;
- sex, Black, Hispanic, disability.

The model is a difference-in-difference-in-differences comparing low-income noncitizens to
low-income citizens and higher-income noncitizens/citizens over time.

## Main Monthly-FPL 250% Cutoff Estimates

Chilling-period DDD term:

- `medicaid`: -0.0076, state-cluster se 0.0269, t -0.28; person-cluster se 0.0173, t -0.44.
- `snap_month`: +0.0106, state-cluster se 0.0097, t 1.10; person-cluster se 0.0100, t 1.07.
- `public`: -0.0020, state-cluster se 0.0249, t -0.08; person-cluster se 0.0173, t -0.11.
- `uninsured`: +0.0230, state-cluster se 0.0259, t 0.89; person-cluster se 0.0207, t 1.11.
- `any_coverage`: -0.0230, state-cluster se 0.0259, t -0.89; person-cluster se 0.0207, t -1.11.
- `private`: -0.0284, state-cluster se 0.0261, t -1.09; person-cluster se 0.0216, t -1.31.
- `direct_purchase`: +0.0035, state-cluster se 0.0261, t 0.13; person-cluster se 0.0182, t 0.19.
- `marketplace_flag`: +0.0235, state-cluster se 0.0216, t 1.09; person-cluster se 0.0155, t 1.52.
- `market_or_subsidy`: -0.0007, state-cluster se 0.0255, t -0.03; person-cluster se 0.0183, t -0.04.
- `tanf_month`: -0.0004, state-cluster se 0.0011, t -0.38; person-cluster se 0.0016, t -0.26.
- `ssi_month`: -0.0025, state-cluster se 0.0030, t -0.83; person-cluster se 0.0039, t -0.65.

Reversal-period DDD term:

- `medicaid`: -0.0199, state-cluster se 0.0198, t -1.00; person-cluster se 0.0192, t -1.03.
- `snap_month`: -0.0158, state-cluster se 0.0108, t -1.45; person-cluster se 0.0115, t -1.38.
- `public`: -0.0134, state-cluster se 0.0188, t -0.71; person-cluster se 0.0193, t -0.70.
- `uninsured`: -0.0054, state-cluster se 0.0261, t -0.21; person-cluster se 0.0230, t -0.23.
- `any_coverage`: +0.0054, state-cluster se 0.0261, t 0.21; person-cluster se 0.0230, t 0.23.
- `private`: +0.0184, state-cluster se 0.0259, t 0.71; person-cluster se 0.0236, t 0.78.
- `direct_purchase`: +0.0120, state-cluster se 0.0257, t 0.47; person-cluster se 0.0195, t 0.61.
- `marketplace_flag`: +0.0138, state-cluster se 0.0283, t 0.49; person-cluster se 0.0175, t 0.79.
- `market_or_subsidy`: +0.0057, state-cluster se 0.0262, t 0.22; person-cluster se 0.0196, t 0.29.
- `tanf_month`: +0.0000, state-cluster se 0.0022, t 0.02; person-cluster se 0.0019, t 0.02.
- `ssi_month`: +0.0013, state-cluster se 0.0044, t 0.29; person-cluster se 0.0042, t 0.30.

## Low-Income 150% FPL Sensitivity

Chilling-period DDD term:

- `medicaid`: +0.0167, state-cluster se 0.0208, t 0.80; person-cluster se 0.0194, t 0.86.
- `snap_month`: +0.0247, state-cluster se 0.0159, t 1.56; person-cluster se 0.0141, t 1.75.
- `public`: +0.0228, state-cluster se 0.0207, t 1.10; person-cluster se 0.0193, t 1.18.
- `uninsured`: +0.0440, state-cluster se 0.0345, t 1.28; person-cluster se 0.0226, t 1.94.
- `any_coverage`: -0.0440, state-cluster se 0.0345, t -1.28; person-cluster se 0.0226, t -1.94.
- `private`: -0.0699, state-cluster se 0.0351, t -1.99; person-cluster se 0.0221, t -3.16.
- `direct_purchase`: -0.0078, state-cluster se 0.0219, t -0.36; person-cluster se 0.0193, t -0.41.
- `marketplace_flag`: -0.0004, state-cluster se 0.0176, t -0.02; person-cluster se 0.0160, t -0.02.
- `market_or_subsidy`: -0.0085, state-cluster se 0.0220, t -0.39; person-cluster se 0.0194, t -0.44.
- `tanf_month`: +0.0025, state-cluster se 0.0022, t 1.13; person-cluster se 0.0023, t 1.06.
- `ssi_month`: -0.0026, state-cluster se 0.0037, t -0.69; person-cluster se 0.0053, t -0.48.

Reversal-period DDD term:

- `medicaid`: +0.0003, state-cluster se 0.0205, t 0.02; person-cluster se 0.0227, t 0.02.
- `snap_month`: -0.0080, state-cluster se 0.0177, t -0.45; person-cluster se 0.0160, t -0.50.
- `public`: +0.0053, state-cluster se 0.0213, t 0.25; person-cluster se 0.0228, t 0.23.
- `uninsured`: +0.0019, state-cluster se 0.0305, t 0.06; person-cluster se 0.0250, t 0.08.
- `any_coverage`: -0.0019, state-cluster se 0.0305, t -0.06; person-cluster se 0.0250, t -0.08.
- `private`: -0.0053, state-cluster se 0.0378, t -0.14; person-cluster se 0.0239, t -0.22.
- `direct_purchase`: +0.0308, state-cluster se 0.0237, t 1.30; person-cluster se 0.0217, t 1.42.
- `marketplace_flag`: +0.0253, state-cluster se 0.0308, t 0.82; person-cluster se 0.0196, t 1.29.
- `market_or_subsidy`: +0.0277, state-cluster se 0.0243, t 1.14; person-cluster se 0.0219, t 1.27.
- `tanf_month`: +0.0025, state-cluster se 0.0039, t 0.63; person-cluster se 0.0027, t 0.93.
- `ssi_month`: +0.0029, state-cluster se 0.0048, t 0.60; person-cluster se 0.0058, t 0.49.

## Annual-FPL 250% Cutoff Sensitivity

Chilling-period DDD term:

- `medicaid`: -0.0100, state-cluster se 0.0327, t -0.31; person-cluster se 0.0190, t -0.53.
- `snap_month`: +0.0098, state-cluster se 0.0094, t 1.04; person-cluster se 0.0104, t 0.94.
- `public`: -0.0054, state-cluster se 0.0307, t -0.18; person-cluster se 0.0191, t -0.29.
- `uninsured`: +0.0470, state-cluster se 0.0279, t 1.69; person-cluster se 0.0226, t 2.08.
- `any_coverage`: -0.0470, state-cluster se 0.0279, t -1.69; person-cluster se 0.0226, t -2.08.
- `private`: -0.0528, state-cluster se 0.0258, t -2.05; person-cluster se 0.0237, t -2.23.
- `direct_purchase`: -0.0005, state-cluster se 0.0284, t -0.02; person-cluster se 0.0198, t -0.02.
- `marketplace_flag`: +0.0169, state-cluster se 0.0245, t 0.69; person-cluster se 0.0174, t 0.97.
- `market_or_subsidy`: -0.0047, state-cluster se 0.0279, t -0.17; person-cluster se 0.0199, t -0.24.
- `tanf_month`: -0.0005, state-cluster se 0.0012, t -0.45; person-cluster se 0.0017, t -0.32.
- `ssi_month`: -0.0044, state-cluster se 0.0029, t -1.54; person-cluster se 0.0041, t -1.08.

Reversal-period DDD term:

- `medicaid`: -0.0137, state-cluster se 0.0178, t -0.77; person-cluster se 0.0207, t -0.66.
- `snap_month`: -0.0199, state-cluster se 0.0128, t -1.55; person-cluster se 0.0122, t -1.63.
- `public`: -0.0069, state-cluster se 0.0174, t -0.40; person-cluster se 0.0208, t -0.33.
- `uninsured`: -0.0101, state-cluster se 0.0301, t -0.34; person-cluster se 0.0250, t -0.40.
- `any_coverage`: +0.0101, state-cluster se 0.0301, t 0.34; person-cluster se 0.0250, t 0.40.
- `private`: +0.0189, state-cluster se 0.0267, t 0.71; person-cluster se 0.0255, t 0.74.
- `direct_purchase`: +0.0241, state-cluster se 0.0282, t 0.86; person-cluster se 0.0211, t 1.14.
- `marketplace_flag`: +0.0236, state-cluster se 0.0314, t 0.75; person-cluster se 0.0191, t 1.24.
- `market_or_subsidy`: +0.0186, state-cluster se 0.0289, t 0.65; person-cluster se 0.0213, t 0.87.
- `tanf_month`: -0.0007, state-cluster se 0.0023, t -0.32; person-cluster se 0.0020, t -0.37.
- `ssi_month`: +0.0006, state-cluster se 0.0042, t 0.15; person-cluster se 0.0045, t 0.14.

## Initial Interpretation

A clean public-charge chilling story predicts negative effects on Medicaid/SNAP/public coverage and
positive effects on uninsurance for low-income noncitizens during 2019-2020, with possible rebound
after 2021. If the signs are mixed, or if Medicaid moves differently from SNAP, the design should
be treated as exploratory because the rule period overlaps the COVID-19 shock and the PHE.

## Artifacts

- `script/11_idea_scan/31_public_charge_immigrant_chilling_test.py`
- `temp/scratch/immigration_status_2018_2024.parquet`
- `result/idea_scan/public_charge_status_value_counts.csv`
- `result/idea_scan/public_charge_cell_means.csv`
- `result/idea_scan/public_charge_person_support.csv`
- `result/idea_scan/public_charge_model_support.csv`
- `result/idea_scan/public_charge_ddd_estimates.csv`
