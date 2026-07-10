# SNAP Emergency Allotment Fast Test

## Question

Can current SIPP support an adult paper on SNAP Emergency Allotment termination, food
insecurity, and health/coverage spillovers?

## Source Checks

- USDA, SNAP Emergency Allotments are Ending: https://www.usda.gov/about-usda/news/blog/snap-emergency-allotments-are-ending
- CBPP, Temporary Pandemic SNAP Benefits Will End in Remaining 35 States in March 2023: https://www.cbpp.org/research/food-assistance/temporary-pandemic-snap-benefits-will-end-in-remaining-35-states-in-march
- Federal Reserve FEDS 2023-046, Termination of SNAP Emergency Allotments, Food Sufficiency, and Economic Hardships: https://www.federalreserve.gov/econres/feds/files/2023046pap.pdf
- USDA FNS, Recent changes to SNAP benefit amounts infographic: https://fns-prod.azureedge.us/sites/default/files/resource-files/snap-sunset-ea.pdf

Policy coding:

- SNAP Emergency Allotments began during 2020.
- The primary design uses the 17 states that ended EA before the 2023 nationwide termination.
- South Carolina is excluded from the primary design because it ended in January 2023, after the
  federal decision to terminate EA nationwide.
- Main analysis period is reference years 2018-2022, so the 2023 nationwide cliff is not used as
  identifying variation.

## Data Construction

- Source parquet: `data/analysis_ready/sipp_2018_2024_person_month_panel.parquet`.
- Unit: person-year collapsed from monthly rows.
- Primary sample: low-income adults age 18-64, FPL <= 300%, valid consecutive prior-year record.
- Primary target: prior-year SNAP recipient, using lagged `RSNAP_YRYN`.
- Treatment: early-EA-ending state x active year x prior-year SNAP target.
- Fixed effects: state-year, state-target, target-year.

Outcomes:

- `food_insecure`: `RFOODS >= 2`.
- `very_low_food`: `RFOODS == 3`.
- `food_score`: `RFOODR`, count of affirmative food-security responses.
- program, utilization, coverage, and labor-market secondary outcomes.

Important measurement note: `RFOODS` and `RFOODR` are constant within person-year in this extract.
This is an annual SIPP screen, not a month-level event study.

## Support

Primary lagged-SNAP sample, 2018-2022:

- Person-years: 27,708.
- Persons: 18,831.
- Target person-years: 5,764.
- Early-ending-state target person-years: 1,545.
- Active treated person-years: 318.

Current-year SNAP sensitivity, 2018-2022:

- Person-years: 56,227.
- Target person-years: 11,261.
- Active treated person-years: 663.

## Main Estimates

Primary lagged-SNAP DDD, 2018-2022:

- `food_insecure`: +0.0662, se 0.0420, t 1.58.
- `very_low_food`: +0.0097, se 0.0351, t 0.28.
- `food_score`: +0.1036, se 0.1956, t 0.53.
- `snap_any`: -0.0090, se 0.0352, t -0.26.
- `doctor_any`: +0.0465, se 0.0377, t 1.23.
- `oop_any`: +0.0272, se 0.0426, t 0.64.
- `uninsured`: -0.0059, se 0.0285, t -0.21.

Lagged-SNAP robustness including 2023 federal cliff:

- `food_insecure`: +0.0387, se 0.0339, t 1.14.
- `very_low_food`: +0.0053, se 0.0275, t 0.19.
- `food_score`: +0.0345, se 0.1556, t 0.22.
- `snap_any`: -0.0191, se 0.0287, t -0.67.
- `doctor_any`: +0.0193, se 0.0317, t 0.61.
- `oop_any`: +0.0217, se 0.0359, t 0.60.
- `uninsured`: +0.0233, se 0.0249, t 0.93.

Current-year SNAP sensitivity, 2018-2022:

- `food_insecure`: +0.1263, se 0.0305, t 4.13.
- `very_low_food`: +0.0814, se 0.0264, t 3.09.
- `food_score`: +0.5131, se 0.1450, t 3.54.
- `snap_any`: +0.0000, se 0.0000, t 11.76.
- `doctor_any`: +0.0235, se 0.0278, t 0.85.
- `oop_any`: -0.0095, se 0.0307, t -0.31.
- `uninsured`: +0.0223, se 0.0233, t 0.96.

## Event and Robustness Checks

Event estimates for early-ending states, omitting relative year -1, are saved in
`result/idea_scan/snap_ea_event.csv`.

Leave-one-early-ending-state estimates are saved in
`result/idea_scan/snap_ea_leave_one.csv`.

## Verdict

`DIRECTIONAL-BUT-WEAK`

A clean GO would require:

- positive effects on `food_insecure`, `very_low_food`, and `food_score`;
- weak or no pre-policy differential movement;
- robustness to current-year SNAP and 2023-inclusive variants;
- and enough treated lagged-SNAP person-years to support state-timing heterogeneity.

This direction is more data-aligned than several insurance-side candidates because SIPP directly
observes food-security outcomes and monthly SNAP participation.

## Artifacts

- `script/11_idea_scan/16_snap_ea_fast_test.py`
- `result/idea_scan/snap_ea_person_year_panel.parquet`
- `result/idea_scan/snap_ea_support.csv`
- `result/idea_scan/snap_ea_state_year_support.csv`
- `result/idea_scan/snap_ea_event_support.csv`
- `result/idea_scan/snap_ea_estimates.csv`
- `result/idea_scan/snap_ea_event.csv`
- `result/idea_scan/snap_ea_leave_one.csv`
