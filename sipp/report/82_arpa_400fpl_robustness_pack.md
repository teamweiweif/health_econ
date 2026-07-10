# ARPA 400% FPL Robustness Pack

## Purpose

This pass stress-tests the leading ARPA 400% FPL difference-in-discontinuities idea after the source-decomposition screen. It asks whether the uninsured decline and lagged non-employer market/subsidy mechanism survive bandwidth, donut, FPL-definition, post-period, placebo-threshold, and pre-ARPA fake-policy checks.

## Main Bandwidth Stability

| model | outcome | bandwidth | coef | t_person_cluster | t_state_cluster | n_person_months | min_cell_persons |
|---|---|---|---|---|---|---|---|
| main_bandwidth | uninsured | 0.2500 | -0.0255 | -1.5017 | -1.0062 | 109427 | 3793 |
| main_bandwidth | market_or_subsidy | 0.2500 | 0.0124 | 0.8579 | 0.8528 | 109427 | 3793 |
| main_bandwidth | source_employer_related | 0.2500 | 0.0360 | 1.6550 | 1.2185 | 109427 | 3793 |
| lag_nonemployer_bandwidth | uninsured | 0.2500 | -0.0485 | -1.2239 | -0.7197 | 35500 | 1424 |
| lag_nonemployer_bandwidth | market_or_subsidy | 0.2500 | 0.0869 | 2.4200 | 2.0719 | 35500 | 1424 |
| lag_nonemployer_bandwidth | source_employer_related | 0.2500 | -0.0096 | -1.2781 | -1.1078 | 35500 | 1424 |
| main_bandwidth | uninsured | 0.3500 | -0.0283 | -1.8278 | -1.3054 | 152297 | 4555 |
| main_bandwidth | market_or_subsidy | 0.3500 | 0.0185 | 1.3212 | 1.2842 | 152297 | 4555 |
| main_bandwidth | source_employer_related | 0.3500 | 0.0321 | 1.5853 | 1.2176 | 152297 | 4555 |
| lag_nonemployer_bandwidth | uninsured | 0.3500 | -0.0478 | -1.3267 | -0.7978 | 49955 | 1719 |
| lag_nonemployer_bandwidth | market_or_subsidy | 0.3500 | 0.0822 | 2.4103 | 2.0051 | 49955 | 1719 |
| lag_nonemployer_bandwidth | source_employer_related | 0.3500 | -0.0112 | -1.6661 | -1.4198 | 49955 | 1719 |
| main_bandwidth | uninsured | 0.5000 | -0.0277 | -1.9607 | -1.8335 | 215972 | 5596 |
| main_bandwidth | market_or_subsidy | 0.5000 | 0.0202 | 1.4708 | 1.3730 | 215972 | 5596 |
| main_bandwidth | source_employer_related | 0.5000 | 0.0301 | 1.5864 | 1.2355 | 215972 | 5596 |
| lag_nonemployer_bandwidth | uninsured | 0.5000 | -0.0457 | -1.3800 | -1.0760 | 71638 | 2101 |
| lag_nonemployer_bandwidth | market_or_subsidy | 0.5000 | 0.0739 | 2.2515 | 2.1100 | 71638 | 2101 |
| lag_nonemployer_bandwidth | source_employer_related | 0.5000 | -0.0100 | -1.7169 | -1.5191 | 71638 | 2101 |
| main_bandwidth | uninsured | 0.7500 | -0.0260 | -1.8759 | -2.1388 | 216480 | 5596 |
| main_bandwidth | market_or_subsidy | 0.7500 | 0.0187 | 1.3498 | 1.2309 | 216480 | 5596 |
| main_bandwidth | source_employer_related | 0.7500 | 0.0307 | 1.6320 | 1.3334 | 216480 | 5596 |
| lag_nonemployer_bandwidth | uninsured | 0.7500 | -0.0382 | -1.1682 | -1.0901 | 71794 | 2101 |
| lag_nonemployer_bandwidth | market_or_subsidy | 0.7500 | 0.0682 | 2.0693 | 2.0402 | 71794 | 2101 |
| lag_nonemployer_bandwidth | source_employer_related | 0.7500 | -0.0085 | -1.5491 | -1.3743 | 71794 | 2101 |
| main_bandwidth | uninsured | 1.0000 | -0.0255 | -1.8328 | -2.2168 | 216480 | 5596 |
| main_bandwidth | market_or_subsidy | 1.0000 | 0.0183 | 1.3100 | 1.1904 | 216480 | 5596 |
| main_bandwidth | source_employer_related | 1.0000 | 0.0308 | 1.6247 | 1.3451 | 216480 | 5596 |
| lag_nonemployer_bandwidth | uninsured | 1.0000 | -0.0361 | -1.0982 | -1.0802 | 71794 | 2101 |
| lag_nonemployer_bandwidth | market_or_subsidy | 1.0000 | 0.0667 | 2.0051 | 2.0088 | 71794 | 2101 |
| lag_nonemployer_bandwidth | source_employer_related | 1.0000 | -0.0082 | -1.4962 | -1.3319 | 71794 | 2101 |

## Donut Robustness

| model | outcome | donut | coef | t_person_cluster | t_state_cluster | n_person_months | min_cell_persons |
|---|---|---|---|---|---|---|---|
| main_donut_bw050 | uninsured | 0.0250 | -0.0330 | -2.0615 | -2.2184 | 205349 | 5438 |
| main_donut_bw050 | market_or_subsidy | 0.0250 | 0.0314 | 1.8604 | 1.7071 | 205349 | 5438 |
| lag_nonemployer_donut_bw050 | uninsured | 0.0250 | -0.0598 | -1.5820 | -1.3741 | 68286 | 2035 |
| lag_nonemployer_donut_bw050 | market_or_subsidy | 0.0250 | 0.0844 | 2.1424 | 2.1106 | 68286 | 2035 |
| main_donut_bw050 | uninsured | 0.0500 | -0.0246 | -1.3094 | -1.5116 | 194353 | 5255 |
| main_donut_bw050 | market_or_subsidy | 0.0500 | 0.0299 | 1.5079 | 1.3170 | 194353 | 5255 |
| lag_nonemployer_donut_bw050 | uninsured | 0.0500 | -0.0351 | -0.8059 | -0.7766 | 64866 | 1964 |
| lag_nonemployer_donut_bw050 | market_or_subsidy | 0.0500 | 0.0406 | 0.8575 | 0.8412 | 64866 | 1964 |
| main_donut_bw050 | uninsured | 0.1000 | -0.0296 | -1.2001 | -1.3836 | 171769 | 4864 |
| main_donut_bw050 | market_or_subsidy | 0.1000 | 0.0256 | 0.9924 | 0.7924 | 171769 | 4864 |
| lag_nonemployer_donut_bw050 | uninsured | 0.1000 | -0.0317 | -0.5517 | -0.5650 | 57560 | 1788 |
| lag_nonemployer_donut_bw050 | market_or_subsidy | 0.1000 | 0.0676 | 1.1055 | 1.0313 | 57560 | 1788 |
| main_donut_bw050 | uninsured | 0.1500 | -0.0197 | -0.6277 | -0.5506 | 150524 | 4445 |
| main_donut_bw050 | market_or_subsidy | 0.1500 | 0.0052 | 0.1611 | 0.1192 | 150524 | 4445 |
| lag_nonemployer_donut_bw050 | uninsured | 0.1500 | -0.0259 | -0.3381 | -0.2802 | 50503 | 1612 |
| lag_nonemployer_donut_bw050 | market_or_subsidy | 0.1500 | 0.0090 | 0.1204 | 0.1055 | 50503 | 1612 |

## Placebo Checks

| model | outcome | threshold | post_col | pre_only | coef | t_person_cluster | t_state_cluster | n_person_months |
|---|---|---|---|---|---|---|---|---|
| placebo_thresholds | uninsured | 3.0000 | post_year2021 | 0 | -0.0017 | -0.1116 | -0.1122 | 247214 |
| placebo_thresholds | market_or_subsidy | 3.0000 | post_year2021 | 0 | -0.0471 | -2.9094 | -2.2616 | 247214 |
| placebo_thresholds | uninsured | 3.5000 | post_year2021 | 0 | -0.0255 | -1.7040 | -1.7371 | 234957 |
| placebo_thresholds | market_or_subsidy | 3.5000 | post_year2021 | 0 | 0.0181 | 1.2808 | 1.3157 | 234957 |
| placebo_thresholds | uninsured | 4.5000 | post_year2021 | 0 | 0.0025 | 0.1866 | 0.1978 | 193558 |
| placebo_thresholds | market_or_subsidy | 4.5000 | post_year2021 | 0 | -0.0103 | -0.7305 | -0.5757 | 193558 |
| placebo_thresholds | uninsured | 5.0000 | post_year2021 | 0 | 0.0058 | 0.4738 | 0.4717 | 173160 |
| placebo_thresholds | market_or_subsidy | 5.0000 | post_year2021 | 0 | 0.0069 | 0.5327 | 0.5410 | 173160 |
| pre_arpa_fake_policy | uninsured | 4.0000 | fake_post_2019 | 1 | -0.0138 | -0.7522 | -0.5439 | 144245 |
| pre_arpa_fake_policy | market_or_subsidy | 4.0000 | fake_post_2019 | 1 | 0.0002 | 0.0124 | 0.0131 | 144245 |
| pre_arpa_fake_policy | uninsured | 4.0000 | fake_post_2020 | 1 | 0.0128 | 0.5998 | 0.4513 | 144245 |
| pre_arpa_fake_policy | market_or_subsidy | 4.0000 | fake_post_2020 | 1 | 0.0011 | 0.0616 | 0.0714 | 144245 |

## Summary

| model | outcome | specs | median_coef | min_coef | max_coef | share_negative | share_positive | person_sig_specs | state_sig_specs | min_cell_persons_min |
|---|---|---|---|---|---|---|---|---|---|---|
| lag_nonemployer_bandwidth | market_or_subsidy | 5 | 0.0739 | 0.0667 | 0.0869 | 0.0000 | 1.0000 | 5 | 5 | 1424 |
| lag_nonemployer_bandwidth | source_employer_related | 5 | -0.0096 | -0.0112 | -0.0082 | 1.0000 | 0.0000 | 0 | 0 | 1424 |
| lag_nonemployer_bandwidth | uninsured | 5 | -0.0457 | -0.0485 | -0.0361 | 1.0000 | 0.0000 | 0 | 0 | 1424 |
| lag_nonemployer_donut_bw050 | market_or_subsidy | 4 | 0.0541 | 0.0090 | 0.0844 | 0.0000 | 1.0000 | 1 | 1 | 1612 |
| lag_nonemployer_donut_bw050 | source_employer_related | 4 | -0.0112 | -0.0183 | -0.0032 | 1.0000 | 0.0000 | 0 | 1 | 1612 |
| lag_nonemployer_donut_bw050 | uninsured | 4 | -0.0334 | -0.0598 | -0.0259 | 1.0000 | 0.0000 | 0 | 0 | 1612 |
| main_annual_fpl | direct_purchase | 3 | -0.0129 | -0.0189 | -0.0020 | 1.0000 | 0.0000 | 0 | 0 | 1291 |
| main_annual_fpl | market_or_subsidy | 3 | -0.0129 | -0.0196 | -0.0015 | 1.0000 | 0.0000 | 0 | 0 | 1291 |
| main_annual_fpl | source_employer_related | 3 | 0.0243 | -0.0053 | 0.0275 | 0.3333 | 0.6667 | 0 | 0 | 1291 |
| main_annual_fpl | uninsured | 3 | -0.0349 | -0.0424 | -0.0204 | 1.0000 | 0.0000 | 0 | 0 | 1291 |
| main_bandwidth | direct_purchase | 5 | 0.0198 | 0.0109 | 0.0208 | 0.0000 | 1.0000 | 0 | 0 | 3793 |
| main_bandwidth | market_or_subsidy | 5 | 0.0185 | 0.0124 | 0.0202 | 0.0000 | 1.0000 | 0 | 0 | 3793 |
| main_bandwidth | source_employer_related | 5 | 0.0308 | 0.0301 | 0.0360 | 0.0000 | 1.0000 | 0 | 0 | 3793 |
| main_bandwidth | uninsured | 5 | -0.0260 | -0.0283 | -0.0255 | 1.0000 | 0.0000 | 1 | 2 | 3793 |
| main_donut_bw050 | direct_purchase | 4 | 0.0308 | 0.0117 | 0.0323 | 0.0000 | 1.0000 | 0 | 0 | 4445 |
| main_donut_bw050 | market_or_subsidy | 4 | 0.0278 | 0.0052 | 0.0314 | 0.0000 | 1.0000 | 0 | 0 | 4445 |
| main_donut_bw050 | source_employer_related | 4 | 0.0270 | 0.0103 | 0.0298 | 0.0000 | 1.0000 | 0 | 0 | 4445 |
| main_donut_bw050 | uninsured | 4 | -0.0271 | -0.0330 | -0.0197 | 1.0000 | 0.0000 | 1 | 1 | 4445 |
| placebo_thresholds | market_or_subsidy | 4 | -0.0017 | -0.0471 | 0.0181 | 0.5000 | 0.5000 | 1 | 1 | 4913 |
| placebo_thresholds | uninsured | 4 | 0.0004 | -0.0255 | 0.0058 | 0.5000 | 0.5000 | 0 | 0 | 4913 |
| pre_arpa_fake_policy | market_or_subsidy | 2 | 0.0007 | 0.0002 | 0.0011 | 0.0000 | 1.0000 | 0 | 0 | 3147 |
| pre_arpa_fake_policy | source_employer_related | 2 | 0.0162 | 0.0004 | 0.0320 | 0.0000 | 1.0000 | 0 | 0 | 3147 |
| pre_arpa_fake_policy | uninsured | 2 | -0.0005 | -0.0138 | 0.0128 | 0.5000 | 0.5000 | 0 | 0 | 3147 |

## Interpretation

- Main-sample uninsured is directionally stable: all five bandwidth specifications are negative, with a tight range around -2.5 to -2.8 percentage points. Donut specifications also remain negative, although precision weakens as threshold-adjacent observations are removed.
- Lagged non-employer market/subsidy is the key mechanism. It is positive in all five bandwidth specifications and significant under both person and state clustering, but it weakens in larger donut exclusions. The mechanism appears concentrated near the threshold.
- Annual-FPL specifications preserve the uninsured decline but do not preserve the direct-market mechanism. This is a real measurement warning: the paper should be explicit that the strongest design uses monthly SIPP poverty ratios around a statutory annual-income cliff.
- Placebo checks are not perfect. The 3.5 FPL placebo uninsured coefficient is also negative, and the 3.0 FPL placebo market/subsidy coefficient is strongly negative. However, placebo results are not systematic across thresholds, and pre-ARPA fake-policy tests at 400% FPL are near zero. This supports a conditional-go interpretation, not a clean unconditional go.

## Decision Read

The robustness pack strengthens the lead but does not make it bulletproof. The signal is not a one-bandwidth accident, and the lagged non-employer mechanism is the strongest evidence so far. The remaining identification threat is that ARPA-era coverage changes may have broader income-gradient components around nearby FPL points, so the paper must report placebo thresholds prominently.

## Key Estimates

- Main uninsured, bw 0.50: -0.0277 (person t -1.96; state t -1.83; N=215,972).
- Main uninsured, donut 0.05: -0.0246 (person t -1.31; state t -1.51; N=194,353).
- Lagged non-employer market/subsidy, bw 0.50: +0.0739 (person t 2.25; state t 2.11; N=71,638).
- Lagged non-employer market/subsidy, donut 0.05: +0.0406 (person t 0.86; state t 0.84; N=64,866).
- Pre-ARPA fake 2020 uninsured: +0.0128 (person t 0.60; state t 0.45; N=144,245).

## Artifacts

- `script/11_idea_scan/41_arpa_400fpl_robustness_pack.py`
- `report/82_arpa_400fpl_robustness_pack.md`
- `report/83_thirtythird_round_arpa_400fpl_robustness_decision.md`
- `result/idea_scan/arpa400_robustness_estimates.csv`
- `result/idea_scan/arpa400_robustness_summary.csv`
