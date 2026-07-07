# RD/RD-DID Rescue Results V3

July 2022 V3 emulator match rate: 0.963. RD/RD-DID was rerun because the running variable passed the 0.950 validation threshold.

## Main 320-Cutoff RD, Bandwidth 20

| outcome | cutoff | bandwidth | donut | n | coef | se | p | mean_below | mean_above | design | sample_definition |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| post_weekend_rn_lt8_day_share | 320 | 20 | 0 | 1476 | -0.01205 | 0.00843735 | 0.153453 | 0.0330447 | 0.0321218 | RD | July 2022 facilities with valid V3 score and post-quarter outcome |
| post_weekend_rn_lt8_days | 320 | 20 | 0 | 1476 | -0.311494 | 0.22275 | 0.162204 | 0.87266 | 0.850069 | RD | July 2022 facilities with valid V3 score and post-quarter outcome |
| post_zero_rn_day_share | 320 | 20 | 0 | 1476 | -0.00303729 | 0.00333275 | 0.362262 | 0.00716513 | 0.00949158 | RD | July 2022 facilities with valid V3 score and post-quarter outcome |
| post_zero_rn_days | 320 | 20 | 0 | 1476 | -0.273984 | 0.304423 | 0.368262 | 0.654813 | 0.868429 | RD | July 2022 facilities with valid V3 score and post-quarter outcome |
| post_weekend_p10_total_hprd | 320 | 20 | 0 | 1476 | 0.0802324 | 0.0676 | 0.23547 | 3.42739 | 3.62025 | RD | July 2022 facilities with valid V3 score and post-quarter outcome |
| post_weekend_p25_total_hprd | 320 | 20 | 0 | 1476 | 0.0682505 | 0.0709975 | 0.336555 | 3.60796 | 3.81703 | RD | July 2022 facilities with valid V3 score and post-quarter outcome |
| post_worst_weekend_total_hprd | 320 | 20 | 0 | 1476 | 0.125719 | 0.0663375 | 0.058269 | 3.14028 | 3.3164 | RD | July 2022 facilities with valid V3 score and post-quarter outcome |
| post_worst_weekend_rn_hprd | 320 | 20 | 0 | 1476 | 0.0864475 | 0.0276024 | 0.00177108 | 0.310955 | 0.41182 | RD | July 2022 facilities with valid V3 score and post-quarter outcome |
| post_weekend_share_total_hours | 320 | 20 | 0 | 1476 | 0.00142118 | 0.00141039 | 0.313788 | 0.252514 | 0.252807 | RD | July 2022 facilities with valid V3 score and post-quarter outcome |
| post_contract_share_total_hours | 320 | 20 | 0 | 1476 | 0.00267478 | 0.0123218 | 0.828179 | 0.088267 | 0.0796396 | RD | July 2022 facilities with valid V3 score and post-quarter outcome |
| post_avg_daily_census | 320 | 20 | 0 | 1476 | 6.14161 | 4.31856 | 0.155197 | 71.0995 | 65.6825 | RD | July 2022 facilities with valid V3 score and post-quarter outcome |
| post_occupancy | 320 | 20 | 0 | 1476 | 0.0207174 | 0.0201154 | 0.303214 | 0.759651 | 0.768962 | RD | July 2022 facilities with valid V3 score and post-quarter outcome |

## Main 320-Cutoff RD-DID, Bandwidth 20

| outcome | cutoff | bandwidth | donut | n | coef | se | p | mean_below | mean_above | design | sample_definition |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| delta_weekend_rn_lt8_day_share | 320 | 20 | 0 | 1465 | 0.0217505 | 0.0129699 | 0.0937573 | -0.00185522 | 0.00751964 | RD_DID | post-minus-pre facility outcomes around V3 reconstructed staffing score cutoff |
| delta_weekend_rn_lt8_days | 320 | 20 | 0 | 1465 | 0.567226 | 0.338651 | 0.094157 | -0.0350854 | 0.210489 | RD_DID | post-minus-pre facility outcomes around V3 reconstructed staffing score cutoff |
| delta_zero_rn_day_share | 320 | 20 | 0 | 1465 | 0.00196076 | 0.00452345 | 0.66474 | 0.00199607 | 0.00499254 | RD_DID | post-minus-pre facility outcomes around V3 reconstructed staffing score cutoff |
| delta_zero_rn_days | 320 | 20 | 0 | 1465 | 0.182872 | 0.412502 | 0.657597 | 0.183356 | 0.459152 | RD_DID | post-minus-pre facility outcomes around V3 reconstructed staffing score cutoff |
| delta_weekend_p10_total_hprd | 320 | 20 | 0 | 1465 | -0.0858632 | 0.0615123 | 0.162965 | -0.130661 | -0.220931 | RD_DID | post-minus-pre facility outcomes around V3 reconstructed staffing score cutoff |
| delta_weekend_p25_total_hprd | 320 | 20 | 0 | 1465 | -0.0713873 | 0.0624944 | 0.253517 | -0.138259 | -0.221818 | RD_DID | post-minus-pre facility outcomes around V3 reconstructed staffing score cutoff |
| delta_worst_weekend_total_hprd | 320 | 20 | 0 | 1465 | -0.0591199 | 0.0652895 | 0.365348 | -0.150345 | -0.217047 | RD_DID | post-minus-pre facility outcomes around V3 reconstructed staffing score cutoff |
| delta_worst_weekend_rn_hprd | 320 | 20 | 0 | 1465 | -0.0363699 | 0.0209957 | 0.0834396 | -0.0444563 | -0.0538384 | RD_DID | post-minus-pre facility outcomes around V3 reconstructed staffing score cutoff |
| delta_weekend_share_total_hours | 320 | 20 | 0 | 1465 | -0.00177279 | 0.0015011 | 0.237797 | 0.00498001 | 0.00393749 | RD_DID | post-minus-pre facility outcomes around V3 reconstructed staffing score cutoff |
| delta_contract_share_total_hours | 320 | 20 | 0 | 1465 | 0.00548435 | 0.00981475 | 0.576393 | 0.0432047 | 0.0412664 | RD_DID | post-minus-pre facility outcomes around V3 reconstructed staffing score cutoff |
| delta_avg_daily_census | 320 | 20 | 0 | 1465 | 0.467164 | 1.2501 | 0.708681 | 3.74896 | 2.65132 | RD_DID | post-minus-pre facility outcomes around V3 reconstructed staffing score cutoff |
| delta_occupancy | 320 | 20 | 0 | 1465 | -0.00172293 | 0.0141469 | 0.903083 | 0.0400961 | 0.0346453 | RD_DID | post-minus-pre facility outcomes around V3 reconstructed staffing score cutoff |

## Diagnostics

- 320 cutoff density p-value at bandwidth 10: 0.001737.
- Balance checks with p<0.05: 2.
- Pre-outcome checks with p<0.05: 28.

Decision: **exploratory/conditional because density, balance, or pre-outcome diagnostics remain imperfect**.
