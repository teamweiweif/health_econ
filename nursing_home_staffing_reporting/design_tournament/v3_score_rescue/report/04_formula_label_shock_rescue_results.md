# Formula Label Shock Rescue Results V3

Formula-induced-loss homes: 1547. Treatment remains mechanical: `old_formula_overall > new_formula_overall` under verified January 2022 and July 2022 rules.

## First Stage

| outcome | group | n | sample_definition | treated_n | control_n | diff | se | p |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| predicted_formula_loss_size | formula_induced_overall_star_loss | 14689 | July facilities, treated if old overall formula exceeds July 2022 formula | 1547 | 13142 | 1 | 0 |  |
| actual_overall_change_apr_to_jul | formula_induced_overall_star_loss | 14653 | July facilities, treated if old overall formula exceeds July 2022 formula | 1544 | 13109 | -0.481481 | 0.0208224 | 0 |
| actual_staffing_change_apr_to_jul | formula_induced_overall_star_loss | 14369 | July facilities, treated if old overall formula exceeds July 2022 formula | 1526 | 12843 | 0.555582 | 0.0241425 | 0 |
| actual_health_change_apr_to_jul | formula_induced_overall_star_loss | 14653 | July facilities, treated if old overall formula exceeds July 2022 formula | 1544 | 13109 | -0.0363039 | 0.0129957 | 0.00522025 |
| actual_qm_change_apr_to_jul | formula_induced_overall_star_loss | 14593 | July facilities, treated if old overall formula exceeds July 2022 formula | 1544 | 13049 | -0.00964673 | 0.0179902 | 0.591815 |

## Balance

Maximum absolute IPTW standardized difference: 0.058.
| covariate | n | treated_mean | control_mean | std_diff | method | sample_definition |
| --- | --- | --- | --- | --- | --- | --- |
| overall_rating_apr2022 | 14666 | 3.23964 | 3.07796 | 0.114599 | raw | raw treated-control balance |
| overall_rating_apr2022 | 14358 | 3.03979 | 3.12109 | -0.0576187 | iptw | propensity-score IPTW balance |
| staffing_rating_apr2022 | 14409 | 3.7097 | 2.70636 | 0.799879 | raw | raw treated-control balance |
| staffing_rating_apr2022 | 14358 | 3.1942 | 3.25694 | -0.0501084 | iptw | propensity-score IPTW balance |
| health_inspection_rating_apr2022 | 14666 | 2.38083 | 2.84667 | -0.366539 | raw | raw treated-control balance |
| health_inspection_rating_apr2022 | 14358 | 2.52152 | 2.58304 | -0.04846 | iptw | propensity-score IPTW balance |
| qm_rating_apr2022 | 14623 | 3.73316 | 3.67528 | 0.0474803 | raw | raw treated-control balance |
| qm_rating_apr2022 | 14358 | 3.70456 | 3.7054 | -0.000691816 | iptw | propensity-score IPTW balance |
| certified_beds | 14888 | 106.913 | 107.067 | -0.00259674 | raw | raw treated-control balance |
| certified_beds | 14358 | 104.798 | 106.586 | -0.0301466 | iptw | propensity-score IPTW balance |
| avg_residents_per_day | 14821 | 75.3482 | 77.4126 | -0.044244 | raw | raw treated-control balance |
| avg_residents_per_day | 14358 | 74.1693 | 75.5336 | -0.0292884 | iptw | propensity-score IPTW balance |

## Pretrends

| outcome | sample | n | treated_time_slope_diff | se | p | sample_definition |
| --- | --- | --- | --- | --- | --- | --- |
| avg_daily_census | raw | 155038 | -0.318566 | 0.125772 | 0.0113141 | 2019Q1-2021Q3 pretrend regression |
| avg_daily_census | matched | 28561 | -0.308412 | 0.178701 | 0.0843842 | 2019Q1-2021Q3 pretrend regression |
| weekend_rn_lt8_day_share | raw | 155038 | -0.00128824 | 0.00033105 | 9.97183e-05 | 2019Q1-2021Q3 pretrend regression |
| weekend_rn_lt8_day_share | matched | 28561 | 6.54907e-05 | 0.000358839 | 0.855186 | 2019Q1-2021Q3 pretrend regression |
| zero_rn_day_share | raw | 155038 | -0.000510355 | 0.000120985 | 2.4624e-05 | 2019Q1-2021Q3 pretrend regression |
| zero_rn_day_share | matched | 28561 | -0.000126957 | 0.000138751 | 0.360199 | 2019Q1-2021Q3 pretrend regression |
| weekend_p10_total_hprd | raw | 155038 | 0.0101893 | 0.00213352 | 1.7912e-06 | 2019Q1-2021Q3 pretrend regression |
| weekend_p10_total_hprd | matched | 28561 | 0.00389813 | 0.00266152 | 0.143034 | 2019Q1-2021Q3 pretrend regression |

## Matched/Weighted Estimates

| outcome | group | n | sample_definition | treated_n | control_n | diff | se | p | method |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| delta_avg_daily_census | formula_induced_overall_star_loss | 14521 | post 2022Q4-2023Q4 minus pre 2021Q1-2021Q3 outcome changes | 1525 | 12996 | -1.04245 | 0.331994 | 0.001693 | raw |
| delta_avg_daily_census | formula_induced_overall_star_loss | 14135 | post 2022Q4-2023Q4 minus pre 2021Q1-2021Q3 outcome changes | 1505 | 12630 | 0.217286 |  |  | iptw |
| delta_avg_daily_census | matched_treat | 2667 | post 2022Q4-2023Q4 minus pre 2021Q1-2021Q3 outcome changes | 1525 | 1142 | -0.128654 | 0.479124 | 0.788321 | nearest_neighbor_state_fallback |
| delta_weekend_rn_lt8_day_share | formula_induced_overall_star_loss | 14521 | post 2022Q4-2023Q4 minus pre 2021Q1-2021Q3 outcome changes | 1525 | 12996 | 0.008479 | 0.00242669 | 0.000477156 | raw |
| delta_weekend_rn_lt8_day_share | formula_induced_overall_star_loss | 14135 | post 2022Q4-2023Q4 minus pre 2021Q1-2021Q3 outcome changes | 1505 | 12630 | -0.00258973 |  |  | iptw |
| delta_weekend_rn_lt8_day_share | matched_treat | 2667 | post 2022Q4-2023Q4 minus pre 2021Q1-2021Q3 outcome changes | 1525 | 1142 | -0.000495657 | 0.00384187 | 0.897356 | nearest_neighbor_state_fallback |
| delta_zero_rn_day_share | formula_induced_overall_star_loss | 14521 | post 2022Q4-2023Q4 minus pre 2021Q1-2021Q3 outcome changes | 1525 | 12996 | 0.00104368 | 0.000970283 | 0.282105 | raw |
| delta_zero_rn_day_share | formula_induced_overall_star_loss | 14135 | post 2022Q4-2023Q4 minus pre 2021Q1-2021Q3 outcome changes | 1505 | 12630 | -0.00111218 |  |  | iptw |
| delta_zero_rn_day_share | matched_treat | 2667 | post 2022Q4-2023Q4 minus pre 2021Q1-2021Q3 outcome changes | 1525 | 1142 | 0.000177184 | 0.001626 | 0.913235 | nearest_neighbor_state_fallback |
| delta_weekend_p10_total_hprd | formula_induced_overall_star_loss | 14521 | post 2022Q4-2023Q4 minus pre 2021Q1-2021Q3 outcome changes | 1525 | 12996 | -0.0806107 | 0.0131258 | 8.39336e-10 | raw |
| delta_weekend_p10_total_hprd | formula_induced_overall_star_loss | 14135 | post 2022Q4-2023Q4 minus pre 2021Q1-2021Q3 outcome changes | 1505 | 12630 | -0.0301361 |  |  | iptw |
| delta_weekend_p10_total_hprd | matched_treat | 2667 | post 2022Q4-2023Q4 minus pre 2021Q1-2021Q3 outcome changes | 1525 | 1142 | -0.0275236 | 0.0194264 | 0.156654 | nearest_neighbor_state_fallback |
| delta_weekend_share_total_hours | formula_induced_overall_star_loss | 14521 | post 2022Q4-2023Q4 minus pre 2021Q1-2021Q3 outcome changes | 1525 | 12996 | -0.000787107 | 0.000327897 | 0.0163865 | raw |
| delta_weekend_share_total_hours | formula_induced_overall_star_loss | 14135 | post 2022Q4-2023Q4 minus pre 2021Q1-2021Q3 outcome changes | 1505 | 12630 | -0.00151469 |  |  | iptw |
| delta_weekend_share_total_hours | matched_treat | 2667 | post 2022Q4-2023Q4 minus pre 2021Q1-2021Q3 outcome changes | 1525 | 1142 | -0.00065312 | 0.000494607 | 0.186787 | nearest_neighbor_state_fallback |
| delta_contract_share_total_hours | formula_induced_overall_star_loss | 14521 | post 2022Q4-2023Q4 minus pre 2021Q1-2021Q3 outcome changes | 1525 | 12996 | 0.0141614 | 0.00282299 | 5.32536e-07 | raw |
| delta_contract_share_total_hours | formula_induced_overall_star_loss | 14135 | post 2022Q4-2023Q4 minus pre 2021Q1-2021Q3 outcome changes | 1505 | 12630 | 0.00918084 |  |  | iptw |
| delta_contract_share_total_hours | matched_treat | 2667 | post 2022Q4-2023Q4 minus pre 2021Q1-2021Q3 outcome changes | 1525 | 1142 | 0.0110086 | 0.00414311 | 0.00792876 | nearest_neighbor_state_fallback |

Decision: **conditional only; no strong causal claim**. Interpret any adverse label-loss response as market/operational response to an adverse public label, not pure resident quality improvement.
