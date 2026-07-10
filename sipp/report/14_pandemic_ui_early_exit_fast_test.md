# Pandemic UI Early Termination Fast Test

## Verdict

`DIRECT-TIMING-BUT-LOW-POWER`

This is the clearest newly screened design for **direct policy timing** from the current parquet.
It is adult-focused, non-child, and non-unwinding. The drawback is that the primary SIPP UC-recipient
sample is small and the labor-supply effect is already studied using CPS, bank, and administrative
data. A SIPP paper would need to be about the insurance/safety-net/medical-financial spillovers of
UI withdrawal, not simply employment.

## Policy Design

In 2021, 26 states ended at least the federal $300 FPUC supplement before the national September
expiration. This screen compares early-exit states with states retaining benefits through the
federal expiration.

- Sample: prime-age adults 25-54 in reference year 2021.
- Primary at-risk group: people receiving unemployment compensation in January-May 2021.
- Pre period: February-May 2021.
- Transition month excluded: June 2021.
- Post period: July-August 2021.
- Model: weighted individual-month DiD with state and month fixed effects.

## Support

| sample | persons | early persons | control persons | UC months | analysis rows |
|---|---:|---:|---:|---:|---:|
| at_risk_uc | 624 | 183 | 446 | 3698 | 3701 |
| at_risk_layofflooking | 678 | 279 | 416 | 1179 | 4052 |
| at_risk_nonemployment | 3511 | 1646 | 1925 | 2011 | 21012 |
| at_risk_broad | 3811 | 1728 | 2143 | 3744 | 22777 |

## Primary At-Risk UC Results

Coefficient is `early-exit state x post period`.

| outcome | coef_early_x_post | se_hc1 | t_stat | persons | early_persons | control_persons | min_cell_persons |
|---|---|---|---|---|---|---|---|
| earnings_positive | 0.0214 | 0.0421 | 0.5098 | 624 | 183 | 446 | 178 |
| employed_any_week | 0.0388 | 0.0416 | 0.9330 | 624 | 183 | 446 | 178 |
| medicaid | 0.0117 | 0.0347 | 0.3373 | 624 | 183 | 446 | 178 |
| oop_any | 0.0017 | 0.0399 | 0.0425 | 624 | 183 | 446 | 178 |
| snap | -0.0192 | 0.0338 | -0.5674 | 624 | 183 | 446 | 178 |
| uc_any | -0.0565 | 0.0406 | -1.3908 | 624 | 183 | 446 | 178 |
| uninsured | -0.0332 | 0.0349 | -0.9508 | 624 | 183 | 446 | 178 |

## Interpretation

- This design has a clearer policy shock than the PTC-only screen, but weaker SIPP power.
- The SIPP novelty is not measuring employment alone. The contribution would be whether UI withdrawal
  caused substitution into SNAP/Medicaid, loss of private coverage, uninsured spells, or medical
  financial pressure.
- If the safety-net/insurance outcomes are null or unstable after full checks, this should be a no-go
  because the main employment question is already crowded.

## Next Checks

1. Re-estimate with person fixed effects for the at-risk panel.
2. Separate states ending all pandemic programs from states ending only FPUC.
3. Add event-study leads/lags from February-August 2021.
4. Test placebo early-exit assignment in 2019 and 2020 SIPP reference years if comparable monthly
   UC variables support it.
5. Keep outcomes focused on SIPP's comparative advantage: insurance, SNAP/TANF/SSI, medical OOP,
   and doctor use.

## Source Checks

- U.S. Department of Labor UIPL 14-21 Change 1 confirms no PUA/FPUC/PEUC/MEUC payments after
  September 6, 2021 under federal law:
  https://www.dol.gov/node/162738
- St. Louis Fed summarizes that 26 states stopped FPUC in June-July 2021:
  https://www.stlouisfed.org/on-the-economy/2022/apr/end-emergency-pandemic-unemployment-benefits-2021
- NBER WP 29575 / related paper documents the existing labor-supply literature and the crowded
  main employment question:
  https://www.nber.org/papers/w29575
- AEA Papers and Proceedings bank-data study reports UI receipt and employment effects after early
  withdrawal, underscoring why SIPP should target spillovers:
  https://www.aeaweb.org/articles?id=10.1257/pandp.20221009

## Outputs

- `result/idea_scan/pandemic_ui_early_exit_estimates.csv`
- `result/idea_scan/pandemic_ui_early_exit_support.csv`
