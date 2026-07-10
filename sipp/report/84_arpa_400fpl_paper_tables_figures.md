# ARPA 400% FPL Paper Tables and Figures

## Purpose

This file converts the idea-screen estimates into paper-facing artifacts: a compact design table, binned RD-style plots, and a bandwidth coefficient plot.

## Paper Design Table

Coefficient format is coefficient with person-cluster standard error in parentheses. Stars use person-cluster t-statistics.

| panel | outcome | coef_fmt | t_person | t_state | n_person_months |
|---|---|---|---|---|---|
| Primary source-decomposition, monthly FPL 350-450% | uninsured | -0.0277** (0.0141) | -1.9607 | -1.8335 | 215972 |
| Primary source-decomposition, monthly FPL 350-450% | any_coverage | +0.0277** (0.0141) | 1.9607 | 1.8335 | 215972 |
| Primary source-decomposition, monthly FPL 350-450% | market_or_subsidy | +0.0202 (0.0137) | 1.4708 | 1.3730 | 215972 |
| Primary source-decomposition, monthly FPL 350-450% | direct_purchase | +0.0208 (0.0137) | 1.5210 | 1.4326 | 215972 |
| Primary source-decomposition, monthly FPL 350-450% | source_employer_related | +0.0301 (0.0190) | 1.5864 | 1.2355 | 215972 |
| Mechanism sample: lagged non-employer | uninsured | -0.0457 (0.0331) | -1.3800 | -1.0760 | 71638 |
| Mechanism sample: lagged non-employer | market_or_subsidy | +0.0739** (0.0328) | 2.2515 | 2.1100 | 71638 |
| Mechanism sample: lagged non-employer | direct_purchase | +0.0735** (0.0328) | 2.2427 | 2.1985 | 71638 |
| Mechanism sample: lagged non-employer | source_employer_related | -0.0100* (0.0058) | -1.7169 | -1.5191 | 71638 |
| Placebo/substitution sample: lagged current employer | uninsured | -0.0011 (0.0021) | -0.5229 | -0.5593 | 126551 |
| Placebo/substitution sample: lagged current employer | market_or_subsidy | +0.0136** (0.0064) | 2.1239 | 1.7396 | 126551 |
| Placebo/substitution sample: lagged current employer | direct_purchase | +0.0138** (0.0064) | 2.1656 | 1.7752 | 126551 |
| Placebo/substitution sample: lagged current employer | source_employer_related | -0.0007 (0.0029) | -0.2360 | -0.2619 | 126551 |
| Robustness: main donut 0.05 | uninsured | -0.0246 (0.0188) | -1.3094 | -1.5116 | 194353 |
| Robustness: main donut 0.05 | market_or_subsidy | +0.0299 (0.0199) | 1.5079 | 1.3170 | 194353 |
| Robustness: annual FPL bw 0.50 | uninsured | -0.0424* (0.0224) | -1.8964 | -1.3149 | 165940 |
| Robustness: annual FPL bw 0.50 | market_or_subsidy | -0.0129 (0.0234) | -0.5510 | -0.4844 | 165940 |
| Placebo threshold 3.5 FPL | uninsured | -0.0255* (0.0150) | -1.7040 | -1.7371 | 234957 |
| Placebo threshold 3.5 FPL | market_or_subsidy | +0.0181 (0.0141) | 1.2808 | 1.3157 | 234957 |
| Pre-ARPA fake policy 2020 | uninsured | +0.0128 (0.0214) | 0.5998 | 0.4513 | 144245 |
| Pre-ARPA fake policy 2020 | market_or_subsidy | +0.0011 (0.0186) | 0.0616 | 0.0714 | 144245 |

## Generated Figures

- `result\idea_scan\arpa400_paper_bins_main.png`
- `result\idea_scan\arpa400_paper_bins_lag_nonemployer.png`
- `result\idea_scan\arpa400_paper_bins_lag_current_employer.png`
- `result\idea_scan\arpa400_bandwidth_robustness_coefficients.png`

## Read for Writing

- Main uninsured is the headline outcome.
- Lagged non-employer market/subsidy is the cleanest mechanism figure and should be shown before any broad Marketplace claim.
- Lagged current-employer patterns should be used as a mechanism contrast, not as proof of treatment irrelevance.
- Placebo and annual-FPL rows must stay in the table because they define the conditional nature of the go decision.

## Artifacts

- `script/11_idea_scan/42_arpa_400fpl_paper_tables_figures.py`
- `report/84_arpa_400fpl_paper_tables_figures.md`
- `report/85_thirtyfourth_round_arpa_400fpl_paper_readiness.md`
- `result/idea_scan/arpa400_paper_design_table.csv`
- `result/idea_scan/arpa400_paper_binned_means.csv`
