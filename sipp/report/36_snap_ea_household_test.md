# SNAP Emergency Allotment Household-Level Test

## Question

Does the SNAP Emergency Allotment signal survive when food-security outcomes are treated as
household-year outcomes rather than repeated person-year outcomes?

## Why This Test Was Needed

`RFOODS` and `RFOODR` are identical within every household-year in the compact parquet. The previous
person-year screen was useful, but it may overweight multi-adult households. This test collapses to
household-year before estimating the early-EA-ending design.

## Design

- Unit: household-year, identified by `SSUID + SHHADID + RFAMNUM + reference_year`.
- Sample: low-income households with at least one adult age 18-64 and FPL <= 300%.
- Primary target: any current adult in the household was observed in the prior year and received
  SNAP in that prior year.
- Treatment: early-EA-ending state x active year x lagged-SNAP household target.
- Main period: reference years 2018-2022, excluding South Carolina.
- Fixed effects: state-year, state-target, target-year.

## Support

Primary household lagged-SNAP sample, 2018-2022:

- Household-years: 19,492.
- Households: 19,449.
- Target household-years: 5,054.
- Early-ending-state target household-years: 1,402.
- Active treated household-years: 303.

Current-year SNAP sensitivity, 2018-2022:

- Household-years: 40,328.
- Target household-years: 10,219.
- Active treated household-years: 636.

## Main Estimates

Primary household lagged-SNAP DDD, 2018-2022:

- `food_insecure`: +0.0763, se 0.0443, t 1.72.
- `very_low_food`: +0.0258, se 0.0367, t 0.70.
- `food_score`: +0.1611, se 0.2059, t 0.78.
- `snap_any`: -0.0266, se 0.0349, t -0.76.
- `doctor_any`: -0.0078, se 0.0336, t -0.23.
- `oop_any`: +0.0191, se 0.0353, t 0.54.
- `uninsured`: -0.0233, se 0.0250, t -0.93.

State-clustered check for the primary `food_insecure` estimate:

- `food_insecure`: +0.0763, state-clustered se 0.0473, t 1.61.

Household lagged-SNAP robustness including 2023 federal cliff:

- `food_insecure`: +0.0427, se 0.0365, t 1.17.
- `very_low_food`: +0.0185, se 0.0292, t 0.63.
- `food_score`: +0.0648, se 0.1669, t 0.39.
- `snap_any`: -0.0250, se 0.0288, t -0.87.
- `doctor_any`: -0.0185, se 0.0283, t -0.65.
- `oop_any`: +0.0188, se 0.0297, t 0.63.
- `uninsured`: -0.0029, se 0.0213, t -0.13.

Household current-year SNAP sensitivity, 2018-2022:

- `food_insecure`: +0.1072, se 0.0317, t 3.38.
- `very_low_food`: +0.0549, se 0.0271, t 2.03.
- `food_score`: +0.3854, se 0.1496, t 2.58.
- `snap_any`: +0.0000, se 0.0000, t 25.05.
- `doctor_any`: +0.0074, se 0.0243, t 0.30.
- `oop_any`: +0.0004, se 0.0252, t 0.02.
- `uninsured`: +0.0071, se 0.0203, t 0.35.

## Verdict

`CONDITIONAL-HOUSEHOLD-LEVEL-LEAD`

The household-level test is stricter than the person-year screen. A genuine upgrade would require the
lagged-SNAP household estimates to remain positive on `food_insecure` and `food_score`, with no
large pre-period contradiction in the event file.

## Artifacts

- `script/11_idea_scan/17_snap_ea_household_test.py`
- `result/idea_scan/snap_ea_household_year_panel.parquet`
- `result/idea_scan/snap_ea_household_support.csv`
- `result/idea_scan/snap_ea_household_state_year_support.csv`
- `result/idea_scan/snap_ea_household_estimates.csv`
- `result/idea_scan/snap_ea_household_estimates_state_cluster.csv`
- `result/idea_scan/snap_ea_household_event.csv`
- `result/idea_scan/snap_ea_household_leave_one.csv`
