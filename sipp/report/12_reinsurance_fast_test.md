# State Reinsurance Fast DDD Test

## Verdict

`SUPPORT-YES-SIGNAL-WEAK`

This design has genuine state-policy variation and targets the adult individual market, but the
current fast cell-level DDD is not yet a clean top-field design. It remains a backup or a possible
component of a broader ACA affordability paper.

## Design Tested

Sample: adults 26-64, annual family income 150-600% FPL, reference years 2017-2023.

Treatment intensity: state reinsurance active x income above 400% FPL. The idea is that
reinsurance lowers gross individual-market premiums and should matter more for people above
the PTC eligibility cliff or otherwise weakly subsidized.

Model: weighted state-month-income-group cell regression with state, year, and month fixed effects.
Coefficient shown is `active x above400`.

| outcome | coef_active_x_above400 | se_hc1 | t_stat | treated_cells | treated_event_count |
|---|---|---|---|---|---|
| any_coverage | -0.0273 | 0.0025 | -11.1372 | 768 | 42450 |
| direct_purchase | -0.0112 | 0.0028 | -3.9467 | 768 | 3566 |
| doctor_any | -0.0247 | 0.0035 | -7.0890 | 768 | 34689 |
| market_or_subsidy | -0.0077 | 0.0026 | -2.9928 | 768 | 2634 |
| oop_any | -0.0004 | 0.0041 | -0.1035 | 768 | 31233 |
| private | -0.0282 | 0.0031 | -9.0876 | 768 | 40121 |
| uninsured | 0.0273 | 0.0025 | 11.1372 | 768 | 2560 |

## Largest Treated-State Support Cells

- CO 2020: persons=722, above400 persons=317, direct-purchase events=2093, market/subsidy events=1692.
- PA 2021: persons=918, above400 persons=381, direct-purchase events=1314, market/subsidy events=877.
- MD 2019: persons=484, above400 persons=264, direct-purchase events=1290, market/subsidy events=1011.
- WI 2019: persons=687, above400 persons=308, direct-purchase events=1158, market/subsidy events=829.
- OR 2018: persons=442, above400 persons=178, direct-purchase events=1080, market/subsidy events=877.
- NJ 2019: persons=458, above400 persons=180, direct-purchase events=1011, market/subsidy events=785.

## Interpretation

- Support is adequate for descriptive and secondary analysis.
- The design is less sharp than the 400% FPL PTC cliff because reinsurance treatment intensity
  depends on state premium reductions, insurer pricing, and pass-through funding.
- A stronger version would merge official state-year premium impacts or county benchmark premiums
  and use continuous treatment intensity rather than a binary adoption indicator.

## Outputs

- `result/idea_scan/reinsurance_ddd_fast_estimates.csv`
- `result/idea_scan/reinsurance_support_by_state.csv`
