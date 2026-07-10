# Medicare Age-65 Threshold / ARPA Older-Adult Coverage Screen

## Purpose

This screen tests a non-state-policy adult design: the Medicare eligibility threshold at age 65.
The policy question is current because older adults ages 50-64 are highly exposed to Marketplace
premium affordability, enhanced premium tax credit expiration, and periodic proposals to lower the
Medicare eligibility age to 60. The identification appeal is the age-65 statutory threshold.

The innovation would need to be narrower than a standard Medicare-at-65 RD, because that literature
already exists. The possible SIPP contribution is monthly coverage-path substitution in the recent
ACA/ARPA Marketplace era:

- uninsured -> Medicare at age 65;
- direct-purchase / Marketplace -> Medicare at age 65;
- whether the age-65 discontinuity changed after ARPA improved pre-65 Marketplace affordability.

## Data And Design

- Unit: person-month.
- Running variable: `TAGE_EHC`, monthly age during the reference year; falls back to `TAGE` if
  needed.
- Main window: ages 60-70.
- Narrow window: ages 62-68.
- Threshold: age >=65.
- Pooled RD term: `above65`.
- RD-DID term: `above65 x post_2021_2023`.
- Fixed effects: calendar year-month.
- Controls: FPL, sex, Black, Hispanic, disability.
- Inference: person-clustered standard errors.

## Support

| spec | person_months | persons | age_min | age_max | below65_person_months | above65_person_months | below65_persons | above65_persons |
|---|---|---|---|---|---|---|---|---|
| age60_70_pooled | 644849 | 29792 | 60.0000 | 70.0000 | 303254 | 341595 | 17016 | 18044 |
| age62_68_pooled | 414962 | 21068 | 62.0000 | 68.0000 | 182945 | 232017 | 12374 | 13920 |
| age60_70_rd_did_arpa | 644849 | 29792 | 60.0000 | 70.0000 | 303254 | 341595 | 17016 | 18044 |
| age62_68_rd_did_arpa | 414962 | 21068 | 62.0000 | 68.0000 | 182945 | 232017 | 12374 | 13920 |

## Age-Bin Means

| age | person_months | persons | medicare | uninsured | direct_purchase | marketplace_flag | private | oop_gt_1000 | doctor_visit_any |
|---|---|---|---|---|---|---|---|---|---|
| 60.0000 | 59601.0000 | 7401.0000 | 0.1247 | 0.0785 | 0.1582 | 0.1149 | 0.7470 | 0.2638 | 0.8284 |
| 61.0000 | 60708.0000 | 7432.0000 | 0.1291 | 0.0752 | 0.1721 | 0.1249 | 0.7523 | 0.2644 | 0.8338 |
| 62.0000 | 61268.0000 | 7493.0000 | 0.1434 | 0.0755 | 0.1880 | 0.1354 | 0.7411 | 0.2606 | 0.8430 |
| 63.0000 | 60615.0000 | 7504.0000 | 0.1684 | 0.0710 | 0.1954 | 0.1398 | 0.7266 | 0.2563 | 0.8518 |
| 64.0000 | 61062.0000 | 7476.0000 | 0.3157 | 0.0735 | 0.1949 | 0.1208 | 0.6997 | 0.2510 | 0.8572 |
| 65.0000 | 60098.0000 | 7400.0000 | 0.7545 | 0.0290 | 0.1585 | 0.0737 | 0.6352 | 0.2329 | 0.8658 |
| 66.0000 | 58674.0000 | 7150.0000 | 0.8753 | 0.0159 | 0.1548 | 0.0556 | 0.6164 | 0.2328 | 0.8738 |
| 67.0000 | 57317.0000 | 6973.0000 | 0.9074 | 0.0119 | 0.1684 | 0.0531 | 0.6133 | 0.2341 | 0.8850 |
| 68.0000 | 55928.0000 | 6920.0000 | 0.9230 | 0.0103 | 0.1836 | 0.0572 | 0.6171 | 0.2372 | 0.8895 |
| 69.0000 | 55619.0000 | 6815.0000 | 0.9289 | 0.0136 | 0.1862 | 0.0517 | 0.6220 | 0.2417 | 0.8925 |
| 70.0000 | 53959.0000 | 6610.0000 | 0.9400 | 0.0107 | 0.2043 | 0.0549 | 0.6170 | 0.2394 | 0.9040 |

## Pre/Post Cells

| period | age_side | person_months | persons | medicare | uninsured | any_coverage | private | direct_purchase | market_or_subsidy | oop_gt_1000 | doctor_visit_any |
|---|---|---|---|---|---|---|---|---|---|---|---|
| post_2021_2023 | 60_64 | 106012 | 6728 | 0.1717 | 0.0680 | 0.9320 | 0.7338 | 0.1963 | 0.1990 | 0.2611 | 0.8413 |
| post_2021_2023 | 65_70 | 129053 | 7813 | 0.8784 | 0.0155 | 0.9845 | 0.5966 | 0.1747 | 0.1777 | 0.2370 | 0.8818 |
| pre_2017_2020 | 60_64 | 197242 | 11706 | 0.1784 | 0.0800 | 0.9200 | 0.7335 | 0.1702 | 0.1737 | 0.2579 | 0.8438 |
| pre_2017_2020 | 65_70 | 212542 | 11830 | 0.8909 | 0.0155 | 0.9845 | 0.6394 | 0.1752 | 0.1790 | 0.2355 | 0.8865 |

## Pre-65 Older Adult ARPA Descriptives

| sample | person_months | persons | pre_60_64_uninsured | post_60_64_uninsured | pre_60_64_market_or_subsidy | post_60_64_market_or_subsidy |
|---|---|---|---|---|---|---|
| low_income_le250 | 220039 | 13935 | 0.1337 | 0.1150 | 0.2652 | 0.3051 |
| middle_income_250_600 | 251502 | 16931 | 0.0681 | 0.0613 | 0.1485 | 0.1730 |
| all_age60_70 | 644849 | 29792 | 0.0800 | 0.0680 | 0.1737 | 0.1990 |

## Pooled Age-65 RD Estimates

Age 60-70:

- `medicare`: +0.5084, HC1 se 0.0023, t 217.10; person-cluster se 0.0075, t 68.00.
- `uninsured`: -0.0470, HC1 se 0.0013, t -36.30; person-cluster se 0.0041, t -11.51.
- `any_coverage`: +0.0470, HC1 se 0.0013, t 36.30; person-cluster se 0.0041, t 11.51.
- `public`: +0.4327, HC1 se 0.0025, t 176.17; person-cluster se 0.0081, t 53.32.
- `private`: -0.0816, HC1 se 0.0025, t -32.39; person-cluster se 0.0081, t -10.02.
- `direct_purchase`: -0.0570, HC1 se 0.0023, t -25.11; person-cluster se 0.0075, t -7.60.
- `marketplace_flag`: -0.0675, HC1 se 0.0018, t -36.72; person-cluster se 0.0061, t -11.09.
- `market_or_subsidy`: -0.0570, HC1 se 0.0023, t -24.91; person-cluster se 0.0075, t -7.56.
- `medicaid`: -0.0095, HC1 se 0.0020, t -4.77; person-cluster se 0.0064, t -1.49.
- `oop_gt_0`: -0.0019, HC1 se 0.0027, t -0.68; person-cluster se 0.0086, t -0.22.
- `oop_gt_1000`: -0.0225, HC1 se 0.0025, t -8.95; person-cluster se 0.0078, t -2.88.
- `doctor_visit_any`: -0.0002, HC1 se 0.0020, t -0.11; person-cluster se 0.0062, t -0.04.
- `dentist_visit_any`: -0.0070, HC1 se 0.0026, t -2.66; person-cluster se 0.0083, t -0.84.
- `hospital_night_any`: -0.0007, HC1 se 0.0019, t -0.35; person-cluster se 0.0058, t -0.11.

Age 62-68:

- `medicare`: +0.4053, HC1 se 0.0034, t 120.93; person-cluster se 0.0089, t 45.34.
- `uninsured`: -0.0449, HC1 se 0.0019, t -24.23; person-cluster se 0.0049, t -9.11.
- `any_coverage`: +0.0449, HC1 se 0.0019, t 24.23; person-cluster se 0.0049, t 9.11.
- `public`: +0.3431, HC1 se 0.0035, t 98.14; person-cluster se 0.0095, t 36.29.
- `private`: -0.0597, HC1 se 0.0034, t -17.46; person-cluster se 0.0090, t -6.62.
- `direct_purchase`: -0.0455, HC1 se 0.0031, t -14.49; person-cluster se 0.0084, t -5.39.
- `marketplace_flag`: -0.0477, HC1 se 0.0026, t -18.48; person-cluster se 0.0069, t -6.95.
- `market_or_subsidy`: -0.0457, HC1 se 0.0032, t -14.44; person-cluster se 0.0085, t -5.39.
- `medicaid`: -0.0064, HC1 se 0.0027, t -2.35; person-cluster se 0.0069, t -0.93.
- `oop_gt_0`: -0.0010, HC1 se 0.0037, t -0.28; person-cluster se 0.0102, t -0.10.
- `oop_gt_1000`: -0.0193, HC1 se 0.0034, t -5.64; person-cluster se 0.0091, t -2.12.
- `doctor_visit_any`: -0.0004, HC1 se 0.0028, t -0.16; person-cluster se 0.0072, t -0.06.
- `dentist_visit_any`: -0.0103, HC1 se 0.0036, t -2.87; person-cluster se 0.0094, t -1.10.
- `hospital_night_any`: -0.0034, HC1 se 0.0026, t -1.32; person-cluster se 0.0069, t -0.49.

## RD-DID: Did The Age-65 Discontinuity Change After ARPA?

Age 60-70:

- `medicare`: -0.0125, HC1 se 0.0048, t -2.57; person-cluster se 0.0151, t -0.82.
- `uninsured`: +0.0051, HC1 se 0.0026, t 1.93; person-cluster se 0.0084, t 0.61.
- `any_coverage`: -0.0051, HC1 se 0.0026, t -1.93; person-cluster se 0.0084, t -0.61.
- `public`: -0.0229, HC1 se 0.0051, t -4.51; person-cluster se 0.0164, t -1.40.
- `private`: -0.0356, HC1 se 0.0052, t -6.85; person-cluster se 0.0166, t -2.14.
- `direct_purchase`: -0.0342, HC1 se 0.0047, t -7.25; person-cluster se 0.0156, t -2.19.
- `marketplace_flag`: -0.0186, HC1 se 0.0038, t -4.84; person-cluster se 0.0129, t -1.44.
- `market_or_subsidy`: -0.0337, HC1 se 0.0047, t -7.10; person-cluster se 0.0157, t -2.15.
- `medicaid`: +0.0089, HC1 se 0.0042, t 2.15; person-cluster se 0.0135, t 0.66.
- `oop_gt_0`: -0.0082, HC1 se 0.0056, t -1.46; person-cluster se 0.0178, t -0.46.
- `oop_gt_1000`: +0.0150, HC1 se 0.0052, t 2.90; person-cluster se 0.0161, t 0.93.
- `doctor_visit_any`: +0.0089, HC1 se 0.0042, t 2.13; person-cluster se 0.0131, t 0.68.
- `dentist_visit_any`: -0.0021, HC1 se 0.0054, t -0.39; person-cluster se 0.0173, t -0.12.
- `hospital_night_any`: -0.0052, HC1 se 0.0039, t -1.35; person-cluster se 0.0120, t -0.43.

Age 62-68:

- `medicare`: -0.0168, HC1 se 0.0069, t -2.43; person-cluster se 0.0185, t -0.91.
- `uninsured`: +0.0163, HC1 se 0.0038, t 4.30; person-cluster se 0.0103, t 1.58.
- `any_coverage`: -0.0163, HC1 se 0.0038, t -4.30; person-cluster se 0.0103, t -1.58.
- `public`: -0.0324, HC1 se 0.0072, t -4.50; person-cluster se 0.0196, t -1.66.
- `private`: -0.0281, HC1 se 0.0070, t -4.00; person-cluster se 0.0190, t -1.48.
- `direct_purchase`: -0.0330, HC1 se 0.0065, t -5.08; person-cluster se 0.0180, t -1.83.
- `marketplace_flag`: -0.0139, HC1 se 0.0054, t -2.58; person-cluster se 0.0149, t -0.93.
- `market_or_subsidy`: -0.0298, HC1 se 0.0065, t -4.55; person-cluster se 0.0181, t -1.65.
- `medicaid`: +0.0085, HC1 se 0.0057, t 1.50; person-cluster se 0.0151, t 0.56.
- `oop_gt_0`: +0.0114, HC1 se 0.0077, t 1.49; person-cluster se 0.0213, t 0.54.
- `oop_gt_1000`: +0.0153, HC1 se 0.0070, t 2.17; person-cluster se 0.0191, t 0.80.
- `doctor_visit_any`: -0.0023, HC1 se 0.0057, t -0.40; person-cluster se 0.0154, t -0.15.
- `dentist_visit_any`: -0.0040, HC1 se 0.0074, t -0.54; person-cluster se 0.0201, t -0.20.
- `hospital_night_any`: -0.0256, HC1 se 0.0052, t -4.87; person-cluster se 0.0143, t -1.79.

## Initial Interpretation

A viable new paper would need more than the canonical Medicare first stage. It would need evidence
that recent Marketplace policy changed the pre-65 side of the threshold or the size/composition of
the age-65 coverage transition. If the only finding is that Medicare rises sharply at age 65 and
uninsurance falls, the design is empirically clean but not novel enough.

## Artifacts

- `script/11_idea_scan/33_medicare_age65_threshold_test.py`
- `result/idea_scan/medicare_age65_estimates.csv`
- `result/idea_scan/medicare_age65_support.csv`
- `result/idea_scan/medicare_age65_age_bins.csv`
- `result/idea_scan/medicare_age65_prepost_cells.csv`
- `result/idea_scan/medicare_age65_fpl_prepost_support.csv`
