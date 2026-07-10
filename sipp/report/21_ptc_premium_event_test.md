# PTC Premium-Intensity Dynamic Check

## Verdict

`NO-DYNAMIC-SUPPORT`

This checks whether the above-400 x high-premium signal is concentrated after ARPA rather than
being a pre-existing difference. The omitted reference year is 2020.

## Dynamic Coefficients

| outcome | year | coef_above400_highpremium_vs_2020 | se_hc1 | t_stat |
|---|---|---|---|---|
| any_coverage | 2018 | 0.0027 | 0.0055 | 0.4879 |
| any_coverage | 2019 | 0.0206 | 0.0056 | 3.6564 |
| any_coverage | 2021 | 0.0172 | 0.0062 | 2.7594 |
| any_coverage | 2022 | 0.0132 | 0.0066 | 2.0028 |
| any_coverage | 2023 | 0.0165 | 0.0063 | 2.6174 |
| direct_purchase | 2018 | 0.0020 | 0.0047 | 0.4262 |
| direct_purchase | 2019 | 0.0158 | 0.0047 | 3.3464 |
| direct_purchase | 2021 | -0.0183 | 0.0049 | -3.7178 |
| direct_purchase | 2022 | 0.0232 | 0.0060 | 3.8887 |
| direct_purchase | 2023 | 0.0071 | 0.0065 | 1.1004 |
| market_or_subsidy | 2018 | -0.0066 | 0.0040 | -1.6699 |
| market_or_subsidy | 2019 | 0.0061 | 0.0040 | 1.5231 |
| market_or_subsidy | 2021 | -0.0202 | 0.0042 | -4.8166 |
| market_or_subsidy | 2022 | -0.0025 | 0.0050 | -0.5024 |
| market_or_subsidy | 2023 | -0.0063 | 0.0059 | -1.0619 |
| oop_any | 2018 | 0.0133 | 0.0086 | 1.5501 |
| oop_any | 2019 | 0.0347 | 0.0084 | 4.1439 |
| oop_any | 2021 | 0.0123 | 0.0098 | 1.2568 |
| oop_any | 2022 | 0.0555 | 0.0097 | 5.7445 |
| oop_any | 2023 | 0.0740 | 0.0102 | 7.2804 |
| uninsured | 2018 | -0.0027 | 0.0055 | -0.4879 |
| uninsured | 2019 | -0.0206 | 0.0056 | -3.6564 |
| uninsured | 2021 | -0.0172 | 0.0062 | -2.7594 |
| uninsured | 2022 | -0.0132 | 0.0066 | -2.0028 |
| uninsured | 2023 | -0.0165 | 0.0063 | -2.6174 |

## Interpretation

- A clean PTC story would show weak pre-2021 lead coefficients and coherent post-2021 changes:
  more marketplace/subsidized coverage and less uninsured or more any coverage.
- If market/subsidy rises but uninsured also rises, the idea remains promising but not clean.
- These are still screening standard errors, not final clustered inference.

## Outputs

- `result/idea_scan/ptc_premium_event_estimates.csv`
- `result/idea_scan/ptc_premium_event_support.csv`
