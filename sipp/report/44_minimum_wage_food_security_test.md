# Minimum Wage Food-Security Spillover Test

## Question

Can current SIPP support an adult paper on state minimum-wage increases, food insecurity, and
safety-net or medical-financial spillovers?

## Source Check

- U.S. Department of Labor historical state minimum wage table:
  https://www.dol.gov/agencies/whd/state/minimum-wage/history
- U.S. Department of Labor current state minimum wage table:
  https://www.dol.gov/agencies/whd/minimum-wage/state

The policy file is reconstructed from the DOL historical state minimum wage table. Effective wage is
the maximum of the listed state wage and the federal floor. For ranges or firm-size variants, this
fast screen uses the highest listed statewide value, so it is a screening policy file rather than a
final statutory treatment panel.

## Design

- Unit: household-year, reference years 2018-2023.
- Primary target: household with at least one adult low-wage worker, defined as age 19-64, at least
  six observed months, employed in at least half of months, annual earnings $1-$35,000, and FPL <=
  300%.
- Secondary target: household with at least one low-education adult.
- Treatment intensity: state minimum-wage increase from prior year x target household.
- Fixed effects: state-year, state-target, target-year.
- Standard errors: clustered by state.

This is stronger than the earlier monthly insurance spillover screen because `RFOODS` and `RFOODR`
are household-year food-security outcomes.

## Support

Primary low-wage household target:

- Household-years: 98,500.
- Households: 95,960.
- Target household-years: 21,260.
- Target household-years with any minimum-wage increase: 8,739.
- Target household-years with at least $0.50 increase: 6,582.

## Main Estimates

Low-wage household, continuous increase intensity:

- `food_insecure`: -0.0011, state-clustered se 0.0093, t -0.12.
- `very_low_food`: +0.0042, state-clustered se 0.0076, t 0.55.
- `food_score`: +0.0276, state-clustered se 0.0525, t 0.53.
- `snap_any`: +0.0085, state-clustered se 0.0089, t 0.95.
- `uninsured`: -0.0046, state-clustered se 0.0064, t -0.72.
- `oop_any`: +0.0048, state-clustered se 0.0097, t 0.49.
- `log_earnings`: -0.0521, state-clustered se 0.0795, t -0.66.

Low-wage household, >= $0.50 increase:

- `food_insecure`: +0.0089, state-clustered se 0.0094, t 0.95.
- `very_low_food`: +0.0121, state-clustered se 0.0092, t 1.32.
- `food_score`: +0.0679, state-clustered se 0.0524, t 1.30.
- `snap_any`: +0.0071, state-clustered se 0.0107, t 0.66.
- `uninsured`: -0.0126, state-clustered se 0.0089, t -1.41.
- `oop_any`: -0.0022, state-clustered se 0.0122, t -0.18.
- `log_earnings`: -0.0831, state-clustered se 0.0862, t -0.96.

Low-education household, continuous increase intensity:

- `food_insecure`: +0.0066, state-clustered se 0.0081, t 0.81.
- `very_low_food`: +0.0070, state-clustered se 0.0057, t 1.22.
- `food_score`: +0.0373, state-clustered se 0.0350, t 1.06.
- `snap_any`: -0.0053, state-clustered se 0.0056, t -0.95.
- `uninsured`: -0.0067, state-clustered se 0.0067, t -1.00.
- `oop_any`: -0.0022, state-clustered se 0.0104, t -0.22.
- `log_earnings`: -0.0483, state-clustered se 0.0500, t -0.97.

## Verdict

`DIRECTIONAL-BUT-ID-WEAK`

A clean GO would require a robust reduction in food insecurity or SNAP reliance among plausibly
exposed households, stable signs across target definitions, and a sharper exposure measure than the
current compact parquet provides. The current parquet lacks occupation, industry, hourly wage, and
baseline statutory coverage/exemption details.

## Artifacts

- `script/11_idea_scan/21_minimum_wage_food_security_test.py`
- `result/idea_scan/minimum_wage_food_policy.csv`
- `result/idea_scan/minimum_wage_food_household_year_panel.parquet`
- `result/idea_scan/minimum_wage_food_support.csv`
- `result/idea_scan/minimum_wage_food_year_support.csv`
- `result/idea_scan/minimum_wage_food_estimates.csv`
