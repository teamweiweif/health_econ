# ARPA 100-150% FPL Non-Expansion State Screen

## Purpose

This screen evaluates the backup idea that ARPA's zero-premium / near-zero-premium Marketplace environment improved coverage among adults at 100-150% FPL in non-expansion states.

Policy hook: CMS states that many consumers with incomes from 100% to 150% FPL would have $0 premium plans after ARPA tax credits. The current 2026 enhanced-PTC expiration debate makes this margin policy-relevant again.

## Policy Sources

- CMS ARPA Marketplace fact sheet: https://www.cms.gov/newsroom/fact-sheets/american-rescue-plan-and-marketplace
- KFF ARPA subsidy explainer: https://www.kff.org/affordable-care-act/how-the-american-rescue-plan-act-affects-subsidies-for-marketplace-shoppers-and-people-who-are-uninsured/
- KFF 2026 enhanced premium tax credit calculator/update context: https://www.kff.org/interactive/calculator-aca-enhanced-premium-tax-credit/
- Bipartisan Policy Center enhanced PTC brief: https://bipartisanpolicy.org/issue-brief/enhanced-premium-tax-credits-who-benefits-how-much-and-what-happens-next/
- Urban Institute enhanced PTC beneficiary brief: https://www.urban.org/research/publication/who-benefits-enhanced-premium-tax-credits-marketplace

## Data and Sample

- SIPP person-month panel, reference years 2017-2023.
- Adults age 26-64, non-Medicare.
- Monthly family FPL 100-200% for DDD support and models.
- Medicaid expansion status merged from `data/policy/medicaid_expansion_state_month.csv`.
- Outcomes use the same coverage/source definitions as the ARPA400 source-decomposition scripts.

## Support and Raw Means

| nonexpansion | post | income_band | person_months | persons | states | uninsured | market_or_subsidy | direct_purchase | marketplace_flag | medicaid |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0 | 0 | 100_150 | 41326 | 5393 | 37 | 0.2069 | 0.2617 | 0.2568 | 0.2267 | 0.4484 |
| 0 | 1 | 100_150 | 20931 | 2988 | 41 | 0.1799 | 0.3120 | 0.3094 | 0.2765 | 0.5081 |
| 0 | 0 | 150_200 | 48399 | 6259 | 37 | 0.1965 | 0.2309 | 0.2245 | 0.1972 | 0.3194 |
| 0 | 1 | 150_200 | 23619 | 3489 | 41 | 0.1730 | 0.2658 | 0.2618 | 0.2359 | 0.3771 |
| 1 | 0 | 100_150 | 30457 | 3816 | 19 | 0.3985 | 0.1625 | 0.1596 | 0.1354 | 0.2039 |
| 1 | 1 | 100_150 | 12137 | 1666 | 14 | 0.3343 | 0.2140 | 0.2097 | 0.1679 | 0.2479 |
| 1 | 0 | 150_200 | 33801 | 4359 | 19 | 0.3257 | 0.1542 | 0.1505 | 0.1158 | 0.1232 |
| 1 | 1 | 150_200 | 13924 | 1987 | 14 | 0.2833 | 0.1817 | 0.1793 | 0.1422 | 0.1621 |

## Screen Estimates

Key terms:

- DDD: `low_100_150 x post2021 x nonexpansion` among 100-200% FPL adults.
- Non-expansion local 150% model: `below150 x post2021` within a local window around 150% FPL.
- Expansion local 150% model: same local threshold model, used as a placebo/contrast.

| model | outcome | term | coef | se_person_cluster | t_person_cluster | se_state_cluster | t_state_cluster | n_person_months | n_state_clusters |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ddd_nonexp_low100150_vs_150200_all_states | uninsured | low_post_nonexp | -0.0085 | 0.0273 | -0.3103 | 0.0294 | -0.2881 | 224594 | 51 |
| nonexp_local150_bw0.50 | uninsured | below_post | 0.0600 | 0.0436 | 1.3765 | 0.0527 | 1.1383 | 90195 | 19 |
| nonexp_local150_bw0.25 | uninsured | below_post | 0.0637 | 0.0517 | 1.2336 | 0.0783 | 0.8142 | 44378 | 19 |
| expansion_local150_placebo_bw0.50 | uninsured | below_post | 0.0156 | 0.0262 | 0.5943 | 0.0229 | 0.6801 | 134129 | 41 |
| ddd_nonexp_low100150_vs_150200_all_states | market_or_subsidy | low_post_nonexp | 0.0099 | 0.0264 | 0.3731 | 0.0320 | 0.3077 | 224594 | 51 |
| nonexp_local150_bw0.50 | market_or_subsidy | below_post | -0.0148 | 0.0376 | -0.3930 | 0.0266 | -0.5563 | 90195 | 19 |
| nonexp_local150_bw0.25 | market_or_subsidy | below_post | -0.0191 | 0.0446 | -0.4285 | 0.0457 | -0.4180 | 44378 | 19 |
| expansion_local150_placebo_bw0.50 | market_or_subsidy | below_post | -0.0066 | 0.0314 | -0.2085 | 0.0286 | -0.2287 | 134129 | 41 |
| ddd_nonexp_low100150_vs_150200_all_states | direct_purchase | low_post_nonexp | 0.0081 | 0.0263 | 0.3066 | 0.0327 | 0.2469 | 224594 | 51 |
| nonexp_local150_bw0.50 | direct_purchase | below_post | -0.0111 | 0.0375 | -0.2952 | 0.0271 | -0.4087 | 90195 | 19 |
| nonexp_local150_bw0.25 | direct_purchase | below_post | -0.0197 | 0.0444 | -0.4427 | 0.0455 | -0.4324 | 44378 | 19 |
| expansion_local150_placebo_bw0.50 | direct_purchase | below_post | -0.0070 | 0.0314 | -0.2233 | 0.0280 | -0.2503 | 134129 | 41 |
| ddd_nonexp_low100150_vs_150200_all_states | medicaid | low_post_nonexp | -0.0102 | 0.0273 | -0.3747 | 0.0340 | -0.3014 | 224594 | 51 |
| nonexp_local150_bw0.50 | medicaid | below_post | 0.0331 | 0.0350 | 0.9458 | 0.0487 | 0.6806 | 90195 | 19 |
| nonexp_local150_bw0.25 | medicaid | below_post | 0.0409 | 0.0424 | 0.9649 | 0.0445 | 0.9187 | 44378 | 19 |
| expansion_local150_placebo_bw0.50 | medicaid | below_post | -0.0031 | 0.0360 | -0.0867 | 0.0439 | -0.0712 | 134129 | 41 |

## Interpretation

This backup idea is policy-relevant, but the screen is designed to be stricter than raw pre/post means. A strong backup would need:

- lower uninsured or higher any coverage in the non-expansion 100-150% group;
- positive `market_or_subsidy` or direct-purchase movement;
- a pattern stronger than the expansion-state local placebo;
- enough state clusters and cell support.

The decision memo records whether the idea is a backup conditional go or should be downgraded.

## Artifacts

- `sipp/script/11_idea_scan/44_arpa_100150_nonexpansion_screen.py`
- `sipp/result/idea_scan/arpa100150_nonexpansion_support.csv`
- `sipp/result/idea_scan/arpa100150_nonexpansion_estimates.csv`
