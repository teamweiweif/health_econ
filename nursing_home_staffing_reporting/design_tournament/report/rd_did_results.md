# RD-DID Results

RD-DID estimates use facility-level post-minus-pre changes, where clean post is 2022Q4-2023Q4 and pre is 2021Q1-2021Q3.

These are downgraded if the score emulator remains below 95% match.

## 320 Cutoff, Bandwidth 20

| outcome | cutoff | bandwidth | donut | n | coef | se | p | mean_below | mean_above | design |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| delta_weekend_rn_lt8_day_share | 320 | 20 | 0 | 1441 | 0.0343637 | 0.0129862 | 0.00822949 | -0.00411139 | 0.00862945 | RD_DID |
| delta_zero_rn_day_share | 320 | 20 | 0 | 1441 | 0.0113096 | 0.00555876 | 0.0420797 | -0.00017483 | 0.00527718 | RD_DID |
| delta_weekend_p10_total_hprd | 320 | 20 | 0 | 1441 | -0.122481 | 0.0605979 | 0.0434427 | -0.128445 | -0.21606 | RD_DID |
| delta_avg_daily_census | 320 | 20 | 0 | 1441 | 0.595687 | 1.24278 | 0.631786 | 3.7474 | 2.68063 | RD_DID |
