# ARPA Low-Income Non-Expansion Marketplace Test

## Question

Did ARPA's zero- or near-zero-premium Marketplace environment improve coverage among 100-150% FPL
adults in stable non-expansion states?

## Source Checks

- CMS American Rescue Plan and the Marketplace: https://www.cms.gov/newsroom/fact-sheets/american-rescue-plan-and-marketplace
- KFF Medicaid expansion status: https://www.kff.org/medicaid/status-of-state-medicaid-expansion-decisions/
- KFF enhanced PTC expiration premium-payment analysis: https://www.kff.org/affordable-care-act/aca-marketplace-premium-payments-would-more-than-double-on-average-next-year-if-enhanced-premium-tax-credits-expire/

Policy facts used here:

- CMS states that many households at 100-150% FPL would have $0 premium plans after ARPA.
- KFF tracks Medicaid expansion status and identifies the states that have not adopted expansion.
- KFF's 2026 enhanced-PTC expiration analysis again highlights low-income non-expansion-state
  Marketplace affordability as a live policy issue.

## Design

- Unit: person-month, SIPP 2017-2023.
- Main sample: age 26-64, non-Medicare, nondisabled adults, 100-200% FPL.
- Treated income band: 100-150% FPL.
- Comparison income band: 150-200% FPL.
- Treated geography: stable non-expansion states.
- Excluded states with expansion timing changes or partial expansion complications: Missouri,
  Oklahoma, South Dakota, North Carolina.
- Treatment: stable non-expansion x 100-150% FPL x post-2021.
- Fixed effects: state-year, state-target, target-year, calendar month.
- Standard errors: clustered by state.

## Support

Age 26-64 main sample:

- Pre-2021 stable non-expansion target person-months: 17,970.
- Pre-2021 stable non-expansion target persons: 2,307.
- Post-2021 stable non-expansion target person-months: 8,021.
- Post-2021 stable non-expansion target persons: 1,117.

Raw support and means:

| nonexpansion | target_100_150 | post2021 | person_months | persons | uninsured | direct_purchase | marketplace_flag | market_or_subsidy |
|---|---|---|---|---|---|---|---|---|
| 0 | 0 | 0 | 41611 | 5455 | 0.2145 | 0.2130 | 0.1857 | 0.2181 |
| 0 | 0 | 1 | 17269 | 2620 | 0.1864 | 0.2554 | 0.2259 | 0.2589 |
| 0 | 1 | 0 | 34637 | 4594 | 0.2316 | 0.2481 | 0.2144 | 0.2534 |
| 0 | 1 | 1 | 15017 | 2189 | 0.1916 | 0.3119 | 0.2765 | 0.3123 |
| 1 | 0 | 0 | 20552 | 2664 | 0.3438 | 0.1528 | 0.1169 | 0.1552 |
| 1 | 0 | 1 | 10117 | 1431 | 0.3009 | 0.1637 | 0.1291 | 0.1637 |
| 1 | 1 | 0 | 17970 | 2307 | 0.4287 | 0.1478 | 0.1218 | 0.1488 |
| 1 | 1 | 1 | 8021 | 1117 | 0.3769 | 0.1887 | 0.1565 | 0.1903 |
| active_term | active_term | active_term | 8021 | 1117 | 0.3769 | 0.1887 | 0.1565 | 0.1903 |

## Main Estimates

Age 26-64, post = 2021-2023:

- `uninsured`: +0.0175, state-clustered se 0.0320, t 0.55.
- `any_coverage`: -0.0175, state-clustered se 0.0320, t -0.55.
- `direct_purchase`: +0.0167, state-clustered se 0.0425, t 0.39.
- `marketplace_flag`: +0.0115, state-clustered se 0.0415, t 0.28.
- `market_or_subsidy`: +0.0221, state-clustered se 0.0414, t 0.53.
- `private`: -0.0002, state-clustered se 0.0525, t -0.00.
- `public`: -0.0094, state-clustered se 0.0340, t -0.28.
- `medicaid`: -0.0118, state-clustered se 0.0362, t -0.33.
- `oop_any`: -0.0080, state-clustered se 0.0332, t -0.24.
- `doctor_any`: -0.0026, state-clustered se 0.0368, t -0.07.

Age 21-64 sensitivity:

- `uninsured`: +0.0002, state-clustered se 0.0329, t 0.00.
- `any_coverage`: -0.0002, state-clustered se 0.0329, t -0.00.
- `direct_purchase`: +0.0267, state-clustered se 0.0361, t 0.74.
- `marketplace_flag`: +0.0156, state-clustered se 0.0355, t 0.44.
- `market_or_subsidy`: +0.0309, state-clustered se 0.0362, t 0.85.

Age 26-64, post = April 2021 onward:

- `uninsured`: +0.0123, state-clustered se 0.0276, t 0.44.
- `any_coverage`: -0.0123, state-clustered se 0.0276, t -0.44.
- `direct_purchase`: +0.0121, state-clustered se 0.0348, t 0.35.
- `marketplace_flag`: +0.0133, state-clustered se 0.0342, t 0.39.
- `market_or_subsidy`: +0.0159, state-clustered se 0.0343, t 0.46.

## Verdict

`DIRECTIONAL-MARKETPLACE-UPTAKE-BUT-WEAK-COVERAGE`

This is a useful backup idea only if the triple-difference recovers both Marketplace/direct-purchase
uptake and lower uninsured rates. If the market proxy rises without a clear uninsured decline, the
paper is weaker than the 400% FPL cliff design.

## Artifacts

- `script/11_idea_scan/25_arpa_low_income_nonexpansion_test.py`
- `result/idea_scan/arpa_low_income_nonexpansion_estimates.csv`
- `result/idea_scan/arpa_low_income_nonexpansion_support.csv`
