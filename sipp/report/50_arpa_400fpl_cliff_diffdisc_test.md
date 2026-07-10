# ARPA 400% FPL Subsidy-Cliff Difference-in-Discontinuities Test

## Question

Did ARPA's temporary removal of the ACA Marketplace 400% FPL subsidy cliff reduce uninsurance among
near-threshold adults?

## Source Checks

- CMS American Rescue Plan and the Marketplace: https://www.cms.gov/newsroom/fact-sheets/american-rescue-plan-and-marketplace
- IRS Premium Tax Credit eligibility: https://www.irs.gov/affordable-care-act/individuals-and-families/eligibility-for-the-premium-tax-credit
- KFF 2026 Marketplace enrollment/premiums/deductibles: https://www.kff.org/affordable-care-act/what-we-know-so-far-about-2026-aca-marketplace-enrollment-premiums-and-deductibles/
- KFF enhanced PTC expiration premium-payment analysis: https://www.kff.org/affordable-care-act/aca-marketplace-premium-payments-would-more-than-double-on-average-next-year-if-enhanced-premium-tax-credits-expire/

Policy facts used here:

- CMS states that before ARPA, households above 400% FPL were not eligible for Marketplace premium
  tax credits.
- CMS states that ARPA made premium tax credits available above 400% FPL when benchmark premiums
  exceeded 8.5% of household income.
- IRS confirms that ARPA temporarily eliminated the rule barring PTC eligibility above 400% FPL for
  tax years 2021 and 2022.
- KFF's 2026 analyses make the question current again: enhanced PTCs expired after 2025, the
  subsidy cliff returned, and above-400% FPL consumers account for a large share of early Marketplace
  enrollment losses.

## Design

- Unit: person-month, SIPP 2017-2023.
- Main running variable: `TFINCPOV`, family monthly income-to-poverty ratio.
- Sensitivity running variable: `TFCYINCPOV`, family calendar-year income-to-poverty ratio.
- Main sample: age 26-64, non-Medicare months, 350-450% FPL.
- User-matched support sample: age 21-64, non-Medicare months, 350-450% FPL.
- Treatment contrast: above 400% FPL x post-2021.
- Model: local linear difference-in-discontinuities with triangular kernel weights, year FE, month
  FE, state FE, and basic demographics.
- Standard errors: HC1 and person-clustered SEs.

## Support

Main age 26-64 monthly-FPL sample:

- Person-months: 217,610.
- Persons: 23,755.
- States: 52.
- Minimum cell persons: 5,562.

Age 21-64 monthly-FPL sample, matching the broader screen:

- Person-months: 241,512.
- Persons: 26,825.
- States: 52.

## Raw Cell Means

Main age 26-64 monthly-FPL sample:

| post | above | person_months | persons | uninsured | direct_purchase | marketplace_flag | market_or_subsidy |
|---|---|---|---|---|---|---|---|
| 0.0000 | 0.0000 | 75922.0000 | 10628.0000 | 0.1129 | 0.0983 | 0.0688 | 0.0992 |
| 0.0000 | 1.0000 | 69184.0000 | 9892.0000 | 0.0957 | 0.0902 | 0.0640 | 0.0909 |
| 1.0000 | 0.0000 | 38834.0000 | 6173.0000 | 0.1102 | 0.1216 | 0.1000 | 0.1228 |
| 1.0000 | 1.0000 | 33670.0000 | 5562.0000 | 0.0861 | 0.1055 | 0.0816 | 0.1058 |

## Main Estimates

Main age 26-64, monthly FPL, post = 2021-2023:

- `uninsured`: -0.0263, HC1 se 0.0072, t -3.67; person-cluster se 0.0143, t -1.84.
- `any_coverage`: +0.0263, HC1 se 0.0072, t 3.67; person-cluster se 0.0143, t 1.84.
- `direct_purchase`: +0.0222, HC1 se 0.0068, t 3.27; person-cluster se 0.0137, t 1.63.
- `marketplace_flag`: +0.0197, HC1 se 0.0061, t 3.22; person-cluster se 0.0123, t 1.61.
- `market_or_subsidy`: +0.0218, HC1 se 0.0068, t 3.20; person-cluster se 0.0137, t 1.59.
- `private`: +0.0237, HC1 se 0.0086, t 2.77; person-cluster se 0.0171, t 1.39.
- `public`: +0.0081, HC1 se 0.0064, t 1.27; person-cluster se 0.0132, t 0.62.
- `medicaid`: +0.0033, HC1 se 0.0058, t 0.57; person-cluster se 0.0117, t 0.28.

Age 21-64, monthly FPL, post = 2021-2023:

- `uninsured`: -0.0313, HC1 se 0.0068, t -4.60; person-cluster se 0.0137, t -2.28.
- `any_coverage`: +0.0313, HC1 se 0.0068, t 4.60; person-cluster se 0.0137, t 2.28.
- `direct_purchase`: +0.0218, HC1 se 0.0067, t 3.27; person-cluster se 0.0132, t 1.66.
- `marketplace_flag`: +0.0174, HC1 se 0.0060, t 2.87; person-cluster se 0.0119, t 1.46.
- `market_or_subsidy`: +0.0225, HC1 se 0.0067, t 3.36; person-cluster se 0.0132, t 1.70.

Age 26-64, monthly FPL, post = April 2021 onward:

- `uninsured`: -0.0296, HC1 se 0.0074, t -4.03; person-cluster se 0.0147, t -2.01.
- `any_coverage`: +0.0296, HC1 se 0.0074, t 4.03; person-cluster se 0.0147, t 2.01.
- `direct_purchase`: +0.0258, HC1 se 0.0070, t 3.69; person-cluster se 0.0141, t 1.83.
- `marketplace_flag`: +0.0270, HC1 se 0.0063, t 4.26; person-cluster se 0.0127, t 2.12.
- `market_or_subsidy`: +0.0253, HC1 se 0.0070, t 3.61; person-cluster se 0.0142, t 1.79.

Age 26-64, annual FPL sensitivity:

- `uninsured`: -0.0301, HC1 se 0.0070, t -4.33; person-cluster se 0.0226, t -1.33.
- `any_coverage`: +0.0301, HC1 se 0.0070, t 4.33; person-cluster se 0.0226, t 1.33.
- `direct_purchase`: -0.0243, HC1 se 0.0067, t -3.62; person-cluster se 0.0230, t -1.06.
- `marketplace_flag`: -0.0192, HC1 se 0.0061, t -3.16; person-cluster se 0.0208, t -0.92.
- `market_or_subsidy`: -0.0240, HC1 se 0.0067, t -3.58; person-cluster se 0.0230, t -1.05.

## Bandwidth Sensitivity

| model | outcome | coef_above_x_post | se_person_cluster | t_person_cluster | n_persons | min_cell_persons |
|---|---|---|---|---|---|---|
| monthly_fpl_age26_64_postyear_bw050 | uninsured | -0.0263 | 0.0143 | -1.8394 | 23755 | 5562 |
| monthly_fpl_age26_64_postyear_bw050 | direct_purchase | 0.0222 | 0.0137 | 1.6252 | 23755 | 5562 |
| monthly_fpl_age26_64_postyear_bw050 | market_or_subsidy | 0.0218 | 0.0137 | 1.5911 | 23755 | 5562 |
| monthly_fpl_age26_64_postyear_bw025 | uninsured | -0.0244 | 0.0170 | -1.4323 | 15833 | 3775 |
| monthly_fpl_age26_64_postyear_bw025 | direct_purchase | 0.0140 | 0.0144 | 0.9769 | 15833 | 3775 |
| monthly_fpl_age26_64_postyear_bw025 | market_or_subsidy | 0.0157 | 0.0144 | 1.0869 | 15833 | 3775 |
| monthly_fpl_age26_64_postyear_bw075 | uninsured | -0.0189 | 0.0129 | -1.4688 | 30062 | 7084 |
| monthly_fpl_age26_64_postyear_bw075 | direct_purchase | 0.0147 | 0.0127 | 1.1593 | 30062 | 7084 |
| monthly_fpl_age26_64_postyear_bw075 | market_or_subsidy | 0.0136 | 0.0127 | 1.0721 | 30062 | 7084 |

## Placebo Cutoffs

| model | outcome | coef_above_x_post | se_person_cluster | t_person_cluster | n_persons | min_cell_persons |
|---|---|---|---|---|---|---|
| placebo_cutoff_3.0_monthly_fpl_age26_64 | uninsured | 0.0079 | 0.0153 | 0.5154 | 25871 | 6216 |
| placebo_cutoff_3.0_monthly_fpl_age26_64 | direct_purchase | -0.0507 | 0.0161 | -3.1442 | 25871 | 6216 |
| placebo_cutoff_3.0_monthly_fpl_age26_64 | market_or_subsidy | -0.0500 | 0.0162 | -3.0905 | 25871 | 6216 |
| placebo_cutoff_3.5_monthly_fpl_age26_64 | uninsured | -0.0284 | 0.0149 | -1.8971 | 25274 | 6155 |
| placebo_cutoff_3.5_monthly_fpl_age26_64 | direct_purchase | 0.0139 | 0.0142 | 0.9820 | 25274 | 6155 |
| placebo_cutoff_3.5_monthly_fpl_age26_64 | market_or_subsidy | 0.0131 | 0.0142 | 0.9205 | 25274 | 6155 |
| placebo_cutoff_4.5_monthly_fpl_age26_64 | uninsured | 0.0020 | 0.0132 | 0.1519 | 22052 | 5353 |
| placebo_cutoff_4.5_monthly_fpl_age26_64 | direct_purchase | -0.0016 | 0.0142 | -0.1107 | 22052 | 5353 |
| placebo_cutoff_4.5_monthly_fpl_age26_64 | market_or_subsidy | -0.0031 | 0.0142 | -0.2174 | 22052 | 5353 |
| placebo_cutoff_5.0_monthly_fpl_age26_64 | uninsured | 0.0048 | 0.0123 | 0.3864 | 20301 | 4887 |
| placebo_cutoff_5.0_monthly_fpl_age26_64 | direct_purchase | 0.0058 | 0.0131 | 0.4420 | 20301 | 4887 |
| placebo_cutoff_5.0_monthly_fpl_age26_64 | market_or_subsidy | 0.0059 | 0.0131 | 0.4476 | 20301 | 4887 |

## Verdict

`CONDITIONAL-GO-UNINSURANCE-SIGNAL`

Interpretation:

- The go/no-go hinge is the uninsured estimate, because SIPP's Marketplace/direct-purchase
  measurement is known to be incomplete and the compact parquet lacks `RPRITYPE1` employer-related
  private coverage.
- A clean GO requires the uninsured reduction to survive age window, post-April-2021 timing, annual
  FPL sensitivity, bandwidth checks, and placebo-cutoff checks.
- If the uninsured effect survives but Marketplace proxies remain weak, the paper should be framed
  around coverage/uninsurance and then use direct-purchase/Marketplace proxies as secondary
  mechanism evidence, not as the sole first stage.

## Artifacts

- `script/11_idea_scan/24_arpa_400fpl_cliff_diffdisc_test.py`
- `result/idea_scan/arpa400_diffdisc_estimates.csv`
- `result/idea_scan/arpa400_diffdisc_support.csv`
- `result/idea_scan/arpa400_diffdisc_cell_means.csv`
