# Late Medicaid Expansion Threshold Test

## Purpose

This screen tests whether late ACA Medicaid expansion adoptions can support a publishable adult
SIPP design. The policy question remains live because KFF reports that, as of May 2026, 41 states
including DC have adopted expansion while 10 have not. The empirical problem is that the broad
Medicaid-expansion literature is already large, so a SIPP project needs a stronger contribution than
the usual "expansion increased Medicaid coverage" result.

## Design

- Unit: person-month.
- Sample states: late expansion states plus never-expansion states.
- Main adults: age 19-64, non-Medicare.
- Main income design: 0-250% monthly FPL, with `eligible <=138% FPL`.
- Narrow design: 100-250% monthly FPL, with `eligible = 100-138% FPL`.
- Treatment: state-month Medicaid expansion active after each late-adopter implementation month.
- Main term: `expansion_active x eligible`.
- Fixed effects: state and calendar year-month.
- Controls: FPL quadratic, age quadratic, sex, Black, Hispanic, disability.
- Inference: state-clustered and person-clustered standard errors.

Late expansion dates coded here:

- Maine and Virginia: 2019-01.
- Idaho and Utah: 2020-01.
- Nebraska: 2020-10.
- Oklahoma: 2021-07.
- Missouri: 2021-10.
- South Dakota: 2023-07.
- North Carolina: 2023-12.

## Support by Specification

| spec | person_months | persons | states | treated_active_person_months | eligible_person_months | active_eligible_person_months | active_eligible_persons |
|---|---|---|---|---|---|---|---|
| broad_000_250_monthly_fpl | 312436 | 20838 | 19 | 24790 | 164485 | 12244 | 1355 |
| near_100_250_monthly_fpl | 191926 | 16175 | 19 | 15788 | 43975 | 3242 | 583 |
| broad_000_250_annual_fpl | 302453 | 17236 | 19 | 23802 | 152605 | 11071 | 931 |
| near_100_250_annual_fpl | 195199 | 12187 | 19 | 15952 | 45351 | 3221 | 307 |
| near_100_200_monthly_fpl_no_disabled_ssi | 96035 | 10014 | 19 | 7422 | 32743 | 2410 | 438 |

## 100-138% FPL Treated-State Support

| state_name | implementation | period | person_months | persons | medicaid | uninsured | direct_purchase | market_or_subsidy |
|---|---|---|---|---|---|---|---|---|
| Idaho | 2020-01 | pre | 448 | 71 | 0.1726 | 0.2441 | 0.2466 | 0.2466 |
| Idaho | 2020-01 | post | 373 | 64 | 0.3236 | 0.2243 | 0.2097 | 0.2097 |
| Maine | 2019-01 | pre | 111 | 12 | 0.1896 | 0.1616 | 0.0477 | 0.0477 |
| Maine | 2019-01 | post | 108 | 17 | 0.3259 | 0.0000 | 0.3791 | 0.3791 |
| Missouri | 2021-10 | pre | 936 | 160 | 0.1860 | 0.2870 | 0.2628 | 0.2666 |
| Missouri | 2021-10 | post | 344 | 68 | 0.3560 | 0.1946 | 0.3762 | 0.3762 |
| Nebraska | 2020-10 | pre | 366 | 68 | 0.2970 | 0.1308 | 0.1040 | 0.1040 |
| Nebraska | 2020-10 | post | 151 | 38 | 0.2853 | 0.2807 | 0.1817 | 0.1817 |
| North Carolina | 2023-12 | pre | 3332 | 460 | 0.2237 | 0.3275 | 0.1965 | 0.1971 |
| North Carolina | 2023-12 | post | 24 | 24 | 0.2872 | 0.1984 | 0.4265 | 0.4265 |
| Oklahoma | 2021-07 | pre | 1210 | 186 | 0.2459 | 0.3763 | 0.2362 | 0.2362 |
| Oklahoma | 2021-07 | post | 639 | 105 | 0.4120 | 0.3014 | 0.1446 | 0.1446 |
| South Dakota | 2023-07 | pre | 161 | 29 | 0.1444 | 0.3156 | 0.0749 | 0.0749 |
| South Dakota | 2023-07 | post | 6 | 2 | 0.0000 | 1.0000 | 0.0000 | 0.0000 |
| Utah | 2020-01 | pre | 359 | 62 | 0.1408 | 0.4318 | 0.1828 | 0.2366 |
| Utah | 2020-01 | post | 448 | 81 | 0.2142 | 0.1846 | 0.2196 | 0.2196 |
| Virginia | 2019-01 | pre | 848 | 125 | 0.2846 | 0.3123 | 0.1199 | 0.1199 |
| Virginia | 2019-01 | post | 1149 | 184 | 0.4750 | 0.2118 | 0.1724 | 0.1724 |

## Broad Monthly-FPL DDD Estimates

Spec: 0-250% monthly FPL, eligible <=138%.

- `medicaid`: +0.0753, state-cluster se 0.0277, t 2.72; person-cluster se 0.0227, t 3.31.
- `uninsured`: -0.0650, state-cluster se 0.0196, t -3.32; person-cluster se 0.0196, t -3.31.
- `any_coverage`: +0.0650, state-cluster se 0.0196, t 3.32; person-cluster se 0.0196, t 3.31.
- `public`: +0.0635, state-cluster se 0.0267, t 2.37; person-cluster se 0.0229, t 2.77.
- `private`: -0.0024, state-cluster se 0.0228, t -0.10; person-cluster se 0.0236, t -0.10.
- `direct_purchase`: +0.0131, state-cluster se 0.0222, t 0.59; person-cluster se 0.0208, t 0.63.
- `marketplace_flag`: +0.0169, state-cluster se 0.0162, t 1.04; person-cluster se 0.0190, t 0.89.
- `market_or_subsidy`: +0.0089, state-cluster se 0.0203, t 0.44; person-cluster se 0.0207, t 0.43.
- `snap_month`: +0.0162, state-cluster se 0.0226, t 0.72; person-cluster se 0.0184, t 0.88.

## Narrow Monthly-FPL DDD Estimates

Spec: 100-250% monthly FPL, eligible 100-138%.

- `medicaid`: +0.0891, state-cluster se 0.0294, t 3.04; person-cluster se 0.0330, t 2.70.
- `uninsured`: -0.0735, state-cluster se 0.0153, t -4.80; person-cluster se 0.0253, t -2.91.
- `any_coverage`: +0.0735, state-cluster se 0.0153, t 4.80; person-cluster se 0.0253, t 2.91.
- `public`: +0.0752, state-cluster se 0.0287, t 2.62; person-cluster se 0.0327, t 2.30.
- `private`: -0.0166, state-cluster se 0.0375, t -0.44; person-cluster se 0.0324, t -0.51.
- `direct_purchase`: +0.0326, state-cluster se 0.0368, t 0.89; person-cluster se 0.0292, t 1.12.
- `marketplace_flag`: +0.0262, state-cluster se 0.0320, t 0.82; person-cluster se 0.0267, t 0.98.
- `market_or_subsidy`: +0.0275, state-cluster se 0.0331, t 0.83; person-cluster se 0.0287, t 0.96.
- `snap_month`: +0.0650, state-cluster se 0.0241, t 2.69; person-cluster se 0.0281, t 2.31.

## Annual-FPL Robustness

Broad annual-FPL spec:

- `medicaid`: +0.1032, state-cluster se 0.0372, t 2.78; person-cluster se 0.0260, t 3.97.
- `uninsured`: -0.0666, state-cluster se 0.0228, t -2.92; person-cluster se 0.0221, t -3.01.
- `any_coverage`: +0.0666, state-cluster se 0.0228, t 2.92; person-cluster se 0.0221, t 3.01.
- `public`: +0.0888, state-cluster se 0.0385, t 2.31; person-cluster se 0.0263, t 3.38.
- `private`: -0.0270, state-cluster se 0.0274, t -0.99; person-cluster se 0.0266, t -1.02.
- `direct_purchase`: +0.0164, state-cluster se 0.0159, t 1.03; person-cluster se 0.0231, t 0.71.
- `marketplace_flag`: +0.0241, state-cluster se 0.0122, t 1.98; person-cluster se 0.0211, t 1.14.
- `market_or_subsidy`: +0.0162, state-cluster se 0.0152, t 1.07; person-cluster se 0.0231, t 0.70.
- `snap_month`: +0.0395, state-cluster se 0.0271, t 1.46; person-cluster se 0.0211, t 1.87.

Narrow annual-FPL spec:

- `medicaid`: +0.1113, state-cluster se 0.0317, t 3.51; person-cluster se 0.0395, t 2.82.
- `uninsured`: -0.0714, state-cluster se 0.0293, t -2.44; person-cluster se 0.0299, t -2.39.
- `any_coverage`: +0.0714, state-cluster se 0.0293, t 2.44; person-cluster se 0.0299, t 2.39.
- `public`: +0.0992, state-cluster se 0.0339, t 2.93; person-cluster se 0.0392, t 2.53.
- `private`: -0.0506, state-cluster se 0.0416, t -1.22; person-cluster se 0.0376, t -1.35.
- `direct_purchase`: -0.0061, state-cluster se 0.0198, t -0.31; person-cluster se 0.0309, t -0.20.
- `marketplace_flag`: -0.0148, state-cluster se 0.0237, t -0.62; person-cluster se 0.0269, t -0.55.
- `market_or_subsidy`: -0.0074, state-cluster se 0.0188, t -0.39; person-cluster se 0.0308, t -0.24.
- `snap_month`: +0.0698, state-cluster se 0.0212, t 3.29; person-cluster se 0.0334, t 2.09.

## Non-Disability / Non-SSI Narrow Robustness

Spec: 100-200% monthly FPL, excluding disability and SSI.

- `medicaid`: +0.0600, state-cluster se 0.0195, t 3.08; person-cluster se 0.0389, t 1.55.
- `uninsured`: -0.0727, state-cluster se 0.0279, t -2.60; person-cluster se 0.0338, t -2.15.
- `any_coverage`: +0.0727, state-cluster se 0.0279, t 2.60; person-cluster se 0.0338, t 2.15.
- `public`: +0.0529, state-cluster se 0.0182, t 2.90; person-cluster se 0.0389, t 1.36.
- `private`: -0.0034, state-cluster se 0.0361, t -0.09; person-cluster se 0.0410, t -0.08.
- `direct_purchase`: +0.0507, state-cluster se 0.0317, t 1.60; person-cluster se 0.0381, t 1.33.
- `marketplace_flag`: +0.0405, state-cluster se 0.0284, t 1.42; person-cluster se 0.0352, t 1.15.
- `market_or_subsidy`: +0.0453, state-cluster se 0.0284, t 1.59; person-cluster se 0.0377, t 1.20.
- `snap_month`: +0.0199, state-cluster se 0.0180, t 1.11; person-cluster se 0.0291, t 0.68.

## Initial Interpretation

A strong SIPP paper would need Medicaid increases and uninsured declines concentrated below 138%
FPL, with limited placebo movement above the threshold and enough treated-state support after
implementation. If the result is only "Medicaid rises" but uninsured does not fall, or if estimates
are unstable across monthly and annual FPL, the idea is empirically feasible but not novel enough
relative to the existing Medicaid-expansion literature.

## Artifacts

- `script/11_idea_scan/29_late_medicaid_expansion_threshold_test.py`
- `result/idea_scan/late_medicaid_expansion_threshold_estimates.csv`
- `result/idea_scan/late_medicaid_expansion_threshold_support.csv`
- `result/idea_scan/late_medicaid_expansion_state_support.csv`
- `result/idea_scan/late_medicaid_expansion_cell_support.csv`
