# Tenth-Round SNAP Emergency Allotment Decision

## Question

Can the current public SIPP parquet support an adult paper on SNAP Emergency Allotment termination,
food insecurity, and health/coverage spillovers?

## Why This Was Worth Testing

This is more data-aligned than several insurance-side candidates because:

- the policy shock is large and well documented;
- 17 states ended SNAP Emergency Allotments before the national March 2023 end;
- SIPP directly observes food-security outcomes, not only indirect health proxies;
- SIPP also observes monthly SNAP participation, coverage, medical utilization, out-of-pocket
  spending, employment, and income;
- the topic is still current because SNAP benefit cuts and restrictions remain active federal and
  state policy debates.

This is not a Medicaid unwinding or child continuous-eligibility project. It is an adult nutrition
assistance and health-economics design.

## Policy Source Checks

- USDA SNAP Emergency Allotments are Ending:
  https://www.usda.gov/about-usda/news/blog/snap-emergency-allotments-are-ending
- CBPP, Temporary Pandemic SNAP Benefits Will End in Remaining 35 States in March 2023:
  https://www.cbpp.org/research/food-assistance/temporary-pandemic-snap-benefits-will-end-in-remaining-35-states-in-march
- Federal Reserve FEDS 2023-046:
  https://www.federalreserve.gov/econres/feds/files/2023046pap.pdf
- USDA FNS SNAP benefit amount infographic:
  https://fns-prod.azureedge.us/sites/default/files/resource-files/snap-sunset-ea.pdf

Primary early-ending states and annual active coding:

- 2021 active: Idaho, North Dakota, Arkansas, Nebraska, Florida, South Dakota, Montana, Missouri.
- 2022 active: Mississippi, Tennessee, Iowa, Wyoming, Arizona, Kentucky, Indiana, Georgia, Alaska.

South Carolina is excluded from the primary design because it ended in January 2023, after the
federal decision to terminate EA nationwide.

## Design

Source:

- `data/analysis_ready/sipp_2018_2024_person_month_panel.parquet`

Unit:

- person-year collapsed from monthly SIPP rows.

Primary sample:

- adults age 18-64;
- FPL <= 300%;
- at least six observed months;
- consecutive prior-year SIPP record available;
- reference years 2018-2022.

Primary target:

- prior-year SNAP recipient, using lagged `RSNAP_YRYN`.

Treatment:

- early-EA-ending state x active year x prior-year SNAP target.

Fixed effects:

- state-year;
- state-target;
- target-year.

Main outcomes:

- `food_insecure`: `RFOODS >= 2`;
- `very_low_food`: `RFOODS == 3`;
- `food_score`: `RFOODR`, count of affirmative food-security responses;
- secondary SNAP, health care, coverage, and labor outcomes.

## Measurement Note

`RFOODS` and `RFOODR` are constant within person-year in the current parquet. This is not a
month-level event study even though SNAP receipt itself is monthly.

That does not kill the design, but it means the cleanest SIPP version is an annual state-year design.

## Support

Primary lagged-SNAP sample, 2018-2022:

- 27,708 person-years.
- 18,831 persons.
- 5,764 target person-years.
- 1,545 early-ending-state target person-years.
- 318 active treated person-years.

Lagged-SNAP sample including 2023:

- 31,809 person-years.
- 6,649 target person-years.
- 551 active treated person-years.

Current-year SNAP sensitivity, 2018-2022:

- 56,227 person-years.
- 11,261 target person-years.
- 663 active treated person-years.

Support is the main limitation. The current-year SNAP sensitivity has more power, but current SNAP
status is potentially endogenous to the policy shock.

## Main Results

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
- `uninsured`: +0.0233, se 0.0249, t 0.93.

Current-year SNAP sensitivity, 2018-2022:

- `food_insecure`: +0.1263, se 0.0305, t 4.13.
- `very_low_food`: +0.0814, se 0.0264, t 3.09.
- `food_score`: +0.5131, se 0.1450, t 3.54.
- `uninsured`: +0.0223, se 0.0233, t 0.96.

The current-year SNAP result is strong and exactly in the expected direction, but it cannot be the
headline without dealing with endogenous SNAP receipt/retention.

## Event and Leave-One Checks

Event estimates for the lagged-SNAP design show the expected positive movement in `food_insecure`
at relative year 0 and year 1, but they are imprecise.

There is a pre-period concern:

- relative year -3 has negative coefficients for `very_low_food` and `food_score`;
- relative year -2 is closer to zero or positive.

Leave-one-state checks for `food_insecure` are mostly positive and fairly stable, usually around
+3.4pp to +8.6pp. Dropping Florida weakens the estimate most. Dropping Tennessee or Iowa makes the
estimate larger and close to conventionally meaningful, but this is not enough to call it clean.

## Decision

`SNAP EA TERMINATION: CONDITIONAL LEAD, NOT CLEAN GO`

This is the best new direction found after the paid-sick-leave no-go because:

- SIPP directly measures the primary outcome;
- policy timing is real and externally documented;
- signs are mostly in the expected direction;
- current-year SNAP sensitivity is strong.

But it is not yet a top-field causal GO from the current compact parquet because:

- the defensible lagged-SNAP treated cell has only 318 active treated person-years;
- the main lagged-SNAP coefficient is suggestive but imprecise;
- `very_low_food` and `food_score` do not confirm the primary `food_insecure` estimate;
- food outcomes are annual, not monthly;
- existing Household Pulse work already studies this policy, so the SIPP contribution must be
  stronger than a simple replication.

## What Would Make It Worth Continuing

This direction becomes worth a serious second-stage build only if one of the following is feasible:

- recover richer SIPP food-security and hardship variables from the raw files;
- use household-level construction rather than person-level repeated food-security records;
- build a stronger lagged exposure definition using pre-policy SNAP receipt over multiple months or
  multiple prior years;
- combine SIPP's food-security outcomes with medical utilization, out-of-pocket spending, and
  insurance spillovers as the distinctive contribution;
- run a modern staggered DID estimator with cohort-specific effects and a documented pretrend audit.

## Updated Ranking

1. **SNAP Emergency Allotment termination**: best new conditional lead; outcome is directly measured,
   but lagged-SNAP support is thin and current-SNAP estimates are endogenous.
2. **ACA enhanced PTC / 400% FPL with premium intensity**: best insurance-policy gap, but dynamic
   checks failed.
3. **ACA family glitch fix**: best insurance-side conditional lead; current compact parquet lacks
   actual employer offer/premium eligibility variables.
4. **Maryland young-adult Marketplace subsidy**: clean design, but treatment cell is too small.
5. **New Jersey Health Plan Savings**: plausible, but bundled with ARPA, SBE transition, and state
   mandate.
6. **Adult Medicaid dental benefits**: strong policy/outcome fit, but treated support is too small
   and estimates are wrong-signed.
7. **State paid sick leave mandates**: policy variation exists, but no direct leave first stage and
   no coherent reduced-form pattern.
8. **State individual mandates**: weak Marketplace signal.
9. **Pandemic UI early termination**: clean timing, too small for insurance spillovers.
10. **No Surprises Act**: excellent policy, SIPP measurement too indirect.
11. **STLDI expansion/state regulation**: no coherent SIPP signal.
12. **State-Based Marketplace transitions**: wrong-signed dynamics.

## New Artifacts

- `script/11_idea_scan/16_snap_ea_fast_test.py`
- `report/34_snap_emergency_allotment_fast_test.md`
- `result/idea_scan/snap_ea_person_year_panel.parquet`
- `result/idea_scan/snap_ea_support.csv`
- `result/idea_scan/snap_ea_state_year_support.csv`
- `result/idea_scan/snap_ea_event_support.csv`
- `result/idea_scan/snap_ea_estimates.csv`
- `result/idea_scan/snap_ea_event.csv`
- `result/idea_scan/snap_ea_leave_one.csv`
