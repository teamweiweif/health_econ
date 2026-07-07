# RD Threshold Results

July 2022 proxy score/star match rate: 0.899.

Because the match rate is below the pre-specified 95% threshold, all RD estimates using `staffing_score_proxy_round` are proxy-running-variable diagnostics unless later improved.

## Main 320-Cutoff RD, Bandwidth 20

| outcome | cutoff | bandwidth | donut | n | coef | se | p | mean_below | mean_above | design |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| post_weekend_rn_lt8_day_share | 320 | 20 | 0 | 1452 | -0.00426935 | 0.00876876 | 0.626416 | 0.0326815 | 0.030797 | RD |
| post_zero_rn_day_share | 320 | 20 | 0 | 1452 | 0.0011814 | 0.00486549 | 0.808186 | 0.00624831 | 0.00951824 | RD |
| post_weekend_p10_total_hprd | 320 | 20 | 0 | 1452 | 0.0102591 | 0.0686204 | 0.881176 | 3.45375 | 3.66647 | RD |
| post_avg_daily_census | 320 | 20 | 0 | 1452 | 2.03179 | 4.4412 | 0.647389 | 71.1465 | 65.6265 | RD |
| post_weekend_share_total_hours | 320 | 20 | 0 | 1452 | 0.000113267 | 0.00147793 | 0.938921 | 0.2523 | 0.253217 | RD |
| post_contract_share_total_hours | 320 | 20 | 0 | 1452 | 0.00268516 | 0.0135135 | 0.842524 | 0.0867251 | 0.0789221 | RD |

## Density Checks

| cutoff | bandwidth | below_n | above_n | binomial_density_p |
| --- | --- | --- | --- | --- |
| 155 | 10 | 544 | 777 | 1.56032e-10 |
| 155 | 10 | 544 | 777 | 1.56032e-10 |
| 155 | 10 | 544 | 777 | 1.56032e-10 |
| 155 | 10 | 544 | 777 | 1.56032e-10 |
| 155 | 10 | 544 | 777 | 1.56032e-10 |
| 205 | 10 | 659 | 906 | 4.63541e-10 |
| 205 | 10 | 659 | 906 | 4.63541e-10 |
| 205 | 10 | 659 | 906 | 4.63541e-10 |
| 205 | 10 | 659 | 906 | 4.63541e-10 |
| 205 | 10 | 659 | 906 | 4.63541e-10 |
| 255 | 10 | 551 | 731 | 5.52418e-07 |
| 255 | 10 | 551 | 731 | 5.52418e-07 |
| 255 | 10 | 551 | 731 | 5.52418e-07 |
| 255 | 10 | 551 | 731 | 5.52418e-07 |
| 255 | 10 | 551 | 731 | 5.52418e-07 |
| 320 | 10 | 360 | 424 | 0.0243872 |
| 320 | 10 | 360 | 424 | 0.0243872 |
| 320 | 10 | 360 | 424 | 0.0243872 |
| 320 | 10 | 360 | 424 | 0.0243872 |
| 320 | 10 | 360 | 424 | 0.0243872 |

## Decision

No STRONG GO from RD unless the emulator is improved or an official score field is located. Current RD can still inform whether local patterns are worth deeper reconstruction.
