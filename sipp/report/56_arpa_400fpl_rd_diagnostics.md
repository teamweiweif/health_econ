# ARPA 400% FPL RD Diagnostics

## Purpose

This diagnostic pass tests whether the leading ARPA 400% FPL result looks like a clean subsidy-cliff
effect or a broader near-threshold private-coverage shift. It uses the augmented panel with
`RPRITYPE1` employer-related private coverage extracted from raw Census SIPP zips.

## Outputs

- `result/idea_scan/arpa400_rd_bins.csv`
- `result/idea_scan/arpa400_yearly_discontinuities.csv`
- `result/idea_scan/arpa400_age_gradient_estimates.csv`
- `result/idea_scan/arpa400_pre_nonemployer_estimates.csv`
- `result/idea_scan/arpa400_diagnostics_support.csv`

Generated plot files:

- `result\idea_scan\arpa400_rd_bins_uninsured.png`
- `result\idea_scan\arpa400_rd_bins_employer_private.png`
- `result\idea_scan\arpa400_rd_bins_direct_purchase.png`
- `result\idea_scan\arpa400_rd_bins_marketplace_flag.png`

## Support

| sample | person_months | persons | states |
|---|---|---|---|
| main_age26_64_bw050 | 217610 | 23755 | 52 |
| pre_nonemployer_baseline | 43681 | 3987 | 52 |

## Year-Specific 400% FPL Discontinuities

These are within-year local linear discontinuities at 400% monthly FPL. They are not the final
diff-in-disc coefficient; they show whether jumps are already present before ARPA.

Pre-ARPA years 2017-2020:

| reference_year | outcome | coef_above | se_person_cluster | t_person_cluster | persons |
|---|---|---|---|---|---|
| 2017 | uninsured | 0.0107 | 0.0161 | 0.6646 | 5783 |
| 2017 | employer_private | -0.0283 | 0.0214 | -1.3235 | 5783 |
| 2017 | direct_purchase | 0.0187 | 0.0164 | 1.1389 | 5783 |
| 2017 | marketplace_flag | 0.0204 | 0.0132 | 1.5402 | 5783 |
| 2018 | uninsured | 0.0256 | 0.0159 | 1.6148 | 4531 |
| 2018 | employer_private | -0.0310 | 0.0220 | -1.4131 | 4531 |
| 2018 | direct_purchase | -0.0181 | 0.0162 | -1.1188 | 4531 |
| 2018 | marketplace_flag | -0.0334 | 0.0134 | -2.4832 | 4531 |
| 2019 | uninsured | -0.0106 | 0.0214 | -0.4934 | 4722 |
| 2019 | employer_private | 0.0212 | 0.0247 | 0.8598 | 4722 |
| 2019 | direct_purchase | 0.0004 | 0.0155 | 0.0236 | 4722 |
| 2019 | marketplace_flag | 0.0091 | 0.0137 | 0.6643 | 4722 |
| 2020 | uninsured | 0.0242 | 0.0180 | 1.3461 | 5414 |
| 2020 | employer_private | -0.0235 | 0.0237 | -0.9911 | 5414 |
| 2020 | direct_purchase | 0.0027 | 0.0161 | 0.1671 | 5414 |
| 2020 | marketplace_flag | 0.0017 | 0.0141 | 0.1221 | 5414 |

Post-ARPA years 2021-2023:

| reference_year | outcome | coef_above | se_person_cluster | t_person_cluster | persons |
|---|---|---|---|---|---|
| 2021 | uninsured | -0.0143 | 0.0123 | -1.1669 | 3897 |
| 2021 | employer_private | 0.0074 | 0.0185 | 0.4027 | 3897 |
| 2021 | direct_purchase | -0.0029 | 0.0140 | -0.2097 | 3897 |
| 2021 | marketplace_flag | -0.0096 | 0.0128 | -0.7519 | 3897 |
| 2022 | uninsured | -0.0064 | 0.0181 | -0.3513 | 3765 |
| 2022 | employer_private | 0.0451 | 0.0232 | 1.9446 | 3765 |
| 2022 | direct_purchase | 0.0482 | 0.0173 | 2.7921 | 3765 |
| 2022 | marketplace_flag | 0.0422 | 0.0154 | 2.7338 | 3765 |
| 2023 | uninsured | -0.0135 | 0.0196 | -0.6879 | 3278 |
| 2023 | employer_private | -0.0033 | 0.0270 | -0.1229 | 3278 |
| 2023 | direct_purchase | 0.0179 | 0.0202 | 0.8875 | 3278 |
| 2023 | marketplace_flag | 0.0143 | 0.0191 | 0.7492 | 3278 |

## Age-Gradient Diff-in-Discontinuities

| model | outcome | coef | se_person_cluster | t_person_cluster | persons |
|---|---|---|---|---|---|
| age_26_39 | uninsured | -0.0439 | 0.0249 | -1.7623 | 9234 |
| age_26_39 | employer_private | 0.0426 | 0.0306 | 1.3927 | 9234 |
| age_26_39 | direct_purchase | 0.0191 | 0.0196 | 0.9705 | 9234 |
| age_26_39 | marketplace_flag | 0.0169 | 0.0175 | 0.9653 | 9234 |
| age_26_39 | market_or_subsidy | 0.0190 | 0.0197 | 0.9679 | 9234 |
| age_40_49 | uninsured | -0.0077 | 0.0252 | -0.3075 | 5812 |
| age_40_49 | employer_private | 0.0181 | 0.0360 | 0.5038 | 5812 |
| age_40_49 | direct_purchase | 0.0572 | 0.0272 | 2.0998 | 5812 |
| age_40_49 | marketplace_flag | 0.0551 | 0.0253 | 2.1775 | 5812 |
| age_40_49 | market_or_subsidy | 0.0592 | 0.0273 | 2.1659 | 5812 |
| age_50_64 | uninsured | -0.0070 | 0.0199 | -0.3496 | 9220 |
| age_50_64 | employer_private | 0.0154 | 0.0285 | 0.5389 | 9220 |
| age_50_64 | direct_purchase | 0.0014 | 0.0236 | 0.0606 | 9220 |
| age_50_64 | marketplace_flag | -0.0050 | 0.0204 | -0.2432 | 9220 |
| age_50_64 | market_or_subsidy | -0.0012 | 0.0237 | -0.0519 | 9220 |

## Pre-Period Non-Employer Baseline Sample

This restricts to people with at least three pre-2021 near-threshold months and no employer coverage
in those pre-period months. It is a selected robustness sample, not the primary design.

| model | outcome | coef | se_person_cluster | t_person_cluster | persons |
|---|---|---|---|---|---|
| pre_nonemployer_baseline | uninsured | -0.0445 | 0.0571 | -0.7798 | 3987 |
| pre_nonemployer_baseline | employer_private | -0.0415 | 0.0545 | -0.7610 | 3987 |
| pre_nonemployer_baseline | direct_purchase | 0.1150 | 0.0727 | 1.5823 | 3987 |
| pre_nonemployer_baseline | marketplace_flag | 0.0888 | 0.0699 | 1.2700 | 3987 |
| pre_nonemployer_baseline | market_or_subsidy | 0.1176 | 0.0727 | 1.6172 | 3987 |

## Initial Interpretation

The yearly discontinuity and age-gradient checks are the decisive evidence for whether the 400% FPL
lead remains a clean cliff-removal paper. If employer coverage jumps are visible before ARPA or are
as large as Marketplace/direct-purchase jumps in the wrong age groups, the safer framing is a broader
ARPA-era private-coverage threshold response rather than a pure Marketplace cliff mechanism.
