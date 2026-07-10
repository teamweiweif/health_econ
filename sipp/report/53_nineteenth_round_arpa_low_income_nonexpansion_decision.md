# Nineteenth-Round ARPA Low-Income Non-Expansion Decision

## Question

Did ARPA's zero- or near-zero-premium Marketplace environment improve coverage among 100-150% FPL
adults in stable non-expansion states?

## Why This Was Worth Testing

This is the natural backup to the 400% FPL cliff idea:

- CMS states that many 100-150% FPL households could access $0 premium plans after ARPA;
- KFF's 2026 enhanced-PTC expiration analysis makes this policy margin current again;
- non-expansion states are the most policy-relevant setting because low-income adults do not have
  the same Medicaid expansion fallback;
- SIPP directly observes monthly uninsured status, direct purchase, Marketplace flags, Medicaid,
  public coverage, and private coverage.

The weakness is identification: there is no sharp national cliff like 400% FPL. The best quick
screen is a triple difference.

## Source Checks

- CMS American Rescue Plan and the Marketplace:
  https://www.cms.gov/newsroom/fact-sheets/american-rescue-plan-and-marketplace
- KFF Medicaid expansion status:
  https://www.kff.org/medicaid/status-of-state-medicaid-expansion-decisions/
- KFF enhanced PTC expiration premium-payment analysis:
  https://www.kff.org/affordable-care-act/aca-marketplace-premium-payments-would-more-than-double-on-average-next-year-if-enhanced-premium-tax-credits-expire/

## Design

Source:

- `data/analysis_ready/sipp_2018_2024_person_month_panel.parquet`

Unit:

- person-month, SIPP 2017-2023.

Sample:

- age 26-64;
- non-Medicare;
- nondisabled;
- 100-200% FPL.

Treatment group:

- stable non-expansion states x 100-150% FPL x post-2021.

Comparison groups:

- 150-200% FPL adults;
- expansion-state adults in the same income bands.

Excluded states:

- Missouri, Oklahoma, South Dakota, North Carolina, because expansion timing changes or partial
  expansion complications make them poor fast-screen controls.

Fixed effects:

- state-year;
- state-target;
- target-year;
- calendar month.

Standard errors:

- clustered by state.

## Support

Age 26-64 main sample:

- Pre-2021 stable non-expansion target: 17,970 person-months, 2,307 persons.
- Post-2021 stable non-expansion target: 8,021 person-months, 1,117 persons.

Support is acceptable for a screen, but much weaker than the 400% FPL design.

## Raw Pattern

In stable non-expansion states among 100-150% FPL adults:

- `uninsured`: 42.9% pre to 37.7% post.
- `direct_purchase`: 14.8% pre to 18.9% post.
- `marketplace_flag`: 12.2% pre to 15.6% post.
- `market_or_subsidy`: 14.9% pre to 19.0% post.

The raw pattern is directionally plausible.

## Triple-Difference Results

Age 26-64, post = 2021-2023:

- `uninsured`: +0.0175, state-clustered se 0.0320, t 0.55.
- `any_coverage`: -0.0175, state-clustered se 0.0320, t -0.55.
- `direct_purchase`: +0.0167, state-clustered se 0.0425, t 0.39.
- `marketplace_flag`: +0.0115, state-clustered se 0.0415, t 0.28.
- `market_or_subsidy`: +0.0221, state-clustered se 0.0414, t 0.53.
- `private`: -0.0002, state-clustered se 0.0525, t -0.00.
- `public`: -0.0094, state-clustered se 0.0340, t -0.28.
- `medicaid`: -0.0118, state-clustered se 0.0362, t -0.33.

Age 21-64 sensitivity:

- `uninsured`: +0.0002, state-clustered se 0.0329, t 0.00.
- `market_or_subsidy`: +0.0309, state-clustered se 0.0362, t 0.85.

Post-April-2021 timing:

- `uninsured`: +0.0123, state-clustered se 0.0276, t 0.44.
- `market_or_subsidy`: +0.0159, state-clustered se 0.0343, t 0.46.

## Interpretation

This is weaker than expected:

- raw means show plausible Marketplace/direct-purchase increases;
- the triple difference does not recover a reduction in uninsured status;
- state-clustered standard errors are large;
- the low-income target group is also affected by state Medicaid rules, churn, pandemic Medicaid
  continuous coverage, and baseline non-expansion state differences;
- the design does not have the clean threshold discontinuity of the 400% FPL cliff.

## Decision

`ARPA 100-150% FPL NON-EXPANSION: BACKUP ONLY, NO CLEAN GO`

This should not compete with the 400% FPL cliff paper. It can remain as a descriptive extension or
heterogeneity appendix if the broader ARPA affordability project develops, but it is not the main
causal design.

## Updated Ranking Implication

The ranking from the previous memo stands:

1. ARPA 400% FPL subsidy-cliff removal.
2. SNAP Emergency Allotment termination.
3. ACA enhanced PTC / premium-intensity portfolio.
4. ACA family glitch.
5. ACA state reinsurance.
6. ARPA 100-150% FPL non-expansion Marketplace affordability.

## New Artifacts

- `script/11_idea_scan/25_arpa_low_income_nonexpansion_test.py`
- `report/52_arpa_low_income_nonexpansion_test.md`
- `result/idea_scan/arpa_low_income_nonexpansion_estimates.csv`
- `result/idea_scan/arpa_low_income_nonexpansion_support.csv`
