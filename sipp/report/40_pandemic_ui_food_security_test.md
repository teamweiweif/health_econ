# Pandemic UI Early Termination Food-Security Test

## Question

Does the 2021 early termination of federal pandemic unemployment benefits show a SIPP food-security
or safety-net spillover signal?

## Source Checks

- U.S. Department of Labor UIPL 14-21 Change 1: https://www.dol.gov/node/162738
- St. Louis Fed, The End of Emergency Pandemic Unemployment Benefits in 2021: https://www.stlouisfed.org/on-the-economy/2022/apr/end-emergency-pandemic-unemployment-benefits-2021
- St. Louis Fed, Ending Pandemic Unemployment Benefits Linked to Job Growth: https://www.stlouisfed.org/on-the-economy/2022/aug/ending-pandemic-unemployment-benefits-linked-job-growth
- NBER WP 29575, Early Withdrawal of Pandemic Unemployment Insurance: https://www.nber.org/papers/w29575

The policy shock is already verified in the earlier UI screen: 26 states stopped at least FPUC before
the September 2021 federal expiration. This follow-up asks whether SIPP's direct food-security
outcomes make the design more useful than the previous insurance-only screen.

## Design

- Unit: person-year, reference years 2020 and 2021.
- Sample: prime-age adults 25-54 with FPL <= 400%.
- Primary target: received unemployment compensation in January-May 2021.
- Treatment: early-exit state x target x 2021.
- Fixed effects: state-year, state-target, target-year.
- Standard errors: clustered by state.

Important measurement note: `RFOODS` and `RFOODR` are annual household food-security measures
repeated on person records. This is a quick screen, not a final household-level estimator.

## Support

Balanced UI-recipient target sample:

- Person-years: 4,516.
- Persons: 2,218.
- Target persons: 127.
- Early-exit target persons in 2021: 45.
- Control target persons in 2021: 85.

Balanced broad-risk target sample:

- Person-years: 4,516.
- Persons: 2,218.
- Target persons: 859.
- Early-exit target persons in 2021: 387.

## Main Estimates

Balanced UI-recipient target:

- `food_insecure`: -0.0684, state-clustered se 0.0686, t -1.00.
- `very_low_food`: +0.0679, state-clustered se 0.0505, t 1.34.
- `food_score`: -0.0150, state-clustered se 0.2794, t -0.05.
- `snap_any`: +0.1086, state-clustered se 0.0988, t 1.10.
- `ui_any`: +0.0443, state-clustered se 0.1045, t 0.42.
- `employed_share`: +0.0738, state-clustered se 0.0997, t 0.74.
- `uninsured`: -0.0745, state-clustered se 0.0470, t -1.59.
- `oop_any`: +0.1836, state-clustered se 0.1177, t 1.56.

Balanced broad-risk target:

- `food_insecure`: -0.0728, state-clustered se 0.0341, t -2.13.
- `very_low_food`: -0.0077, state-clustered se 0.0271, t -0.29.
- `food_score`: -0.2154, state-clustered se 0.1250, t -1.72.
- `snap_any`: +0.0718, state-clustered se 0.0311, t 2.31.
- `ui_any`: -0.0665, state-clustered se 0.0448, t -1.48.
- `employed_share`: -0.0036, state-clustered se 0.0296, t -0.12.
- `uninsured`: -0.0115, state-clustered se 0.0296, t -0.39.
- `oop_any`: +0.1221, state-clustered se 0.0608, t 2.01.

Unbalanced UI-recipient sensitivity:

- `food_insecure`: -0.0198, state-clustered se 0.0607, t -0.33.
- `very_low_food`: +0.0772, state-clustered se 0.0493, t 1.56.
- `food_score`: +0.2077, state-clustered se 0.2551, t 0.81.
- `snap_any`: +0.0274, state-clustered se 0.0709, t 0.39.
- `ui_any`: +0.0746, state-clustered se 0.1057, t 0.71.
- `employed_share`: +0.0834, state-clustered se 0.0729, t 1.14.
- `uninsured`: +0.0023, state-clustered se 0.0605, t 0.04.
- `oop_any`: +0.1669, state-clustered se 0.0895, t 1.87.

## Verdict

`NO-CLEAN-GO`

A clean GO would require a negative first-stage effect on UI receipt, a coherent increase in food
insecurity or SNAP substitution, and enough target support that the estimate is not just a small-cell
artifact.

## Artifacts

- `script/11_idea_scan/19_pandemic_ui_food_security_test.py`
- `result/idea_scan/pandemic_ui_food_person_year_panel.parquet`
- `result/idea_scan/pandemic_ui_food_support.csv`
- `result/idea_scan/pandemic_ui_food_estimates.csv`
