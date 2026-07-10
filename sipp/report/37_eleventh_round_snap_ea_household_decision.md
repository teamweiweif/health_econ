# Eleventh-Round SNAP EA Household Decision

## Question

Does the SNAP Emergency Allotment idea survive a stricter household-year construction?

## Why This Follow-Up Was Necessary

The tenth-round person-year screen found the best new conditional lead so far:

- lagged-SNAP target: `food_insecure` +6.6pp, se 4.2pp;
- current-year SNAP sensitivity: large and significant, but endogenous.

However, `RFOODS` and `RFOODR` are household food-security measures repeated across persons in this
compact parquet. A credible SIPP paper cannot rely only on person-year repeated household outcomes.

The household-level follow-up therefore tests whether the signal survives after collapsing to
household-year.

## Policy Source Checks

Same source base as the tenth-round SNAP EA screen:

- USDA SNAP Emergency Allotments are Ending:
  https://www.usda.gov/about-usda/news/blog/snap-emergency-allotments-are-ending
- CBPP, Temporary Pandemic SNAP Benefits Will End in Remaining 35 States in March 2023:
  https://www.cbpp.org/research/food-assistance/temporary-pandemic-snap-benefits-will-end-in-remaining-35-states-in-march
- Federal Reserve FEDS 2023-046:
  https://www.federalreserve.gov/econres/feds/files/2023046pap.pdf
- USDA FNS SNAP benefit amount infographic:
  https://fns-prod.azureedge.us/sites/default/files/resource-files/snap-sunset-ea.pdf

## Design

Source:

- `data/analysis_ready/sipp_2018_2024_person_month_panel.parquet`

Unit:

- household-year, using `SSUID + SHHADID + RFAMNUM + reference_year`.

Primary sample:

- low-income households with at least one adult age 18-64;
- FPL <= 300%;
- at least one adult observed in the consecutive prior year;
- reference years 2018-2022;
- South Carolina excluded because its January 2023 end is too close to the national termination.

Primary target:

- any current adult in the household was observed in the prior year and received SNAP in that prior
  year.

Treatment:

- early-EA-ending state x active year x lagged-SNAP household target.

Fixed effects:

- state-year;
- state-target;
- target-year.

Main outcomes:

- `food_insecure`: `RFOODS >= 2`;
- `very_low_food`: `RFOODS == 3`;
- `food_score`: `RFOODR`, count of affirmative food-security responses.

## Support

Primary household lagged-SNAP sample, 2018-2022:

- 19,492 household-years.
- 19,449 households.
- 5,054 target household-years.
- 1,402 early-ending-state target household-years.
- 303 active treated household-years.

Current-year SNAP household sensitivity, 2018-2022:

- 40,328 household-years.
- 10,219 target household-years.
- 636 active treated household-years.

## Main Results

Primary household lagged-SNAP DDD, 2018-2022:

- `food_insecure`: +0.0763, se 0.0443, t 1.72.
- State-clustered `food_insecure`: +0.0763, se 0.0473, t 1.61.
- `very_low_food`: +0.0258, se 0.0367, t 0.70.
- `food_score`: +0.1611, se 0.2059, t 0.78.
- `snap_any`: -0.0266, se 0.0349, t -0.76.
- `doctor_any`: -0.0078, se 0.0336, t -0.23.
- `oop_any`: +0.0191, se 0.0353, t 0.54.
- `uninsured`: -0.0233, se 0.0250, t -0.93.

Household lagged-SNAP robustness including 2023 federal cliff:

- `food_insecure`: +0.0427, se 0.0365, t 1.17.
- `very_low_food`: +0.0185, se 0.0292, t 0.63.
- `food_score`: +0.0648, se 0.1669, t 0.39.

Household current-year SNAP sensitivity:

- `food_insecure`: +0.1072, se 0.0317, t 3.38.
- State-clustered `food_insecure`: +0.1072, se 0.0306, t 3.50.
- `very_low_food`: +0.0549, se 0.0271, t 2.03.
- `food_score`: +0.3854, se 0.1496, t 2.58.

## Interpretation

This is materially stronger than most previous candidate ideas:

- the outcome is directly observed;
- household-level de-duplication does not erase the effect;
- the main sign is exactly as expected;
- state-clustered standard errors do not collapse the signal;
- current-year SNAP sensitivity gives a large, internally consistent first-pass pattern.

But it still falls short of a clean top-economics GO:

- the defensible lagged-SNAP active treated cell is only 303 household-years;
- `very_low_food` and `food_score` are positive but imprecise;
- including 2023 attenuates the lagged-SNAP estimate;
- event estimates remain suggestive rather than clean;
- current-year SNAP targeting is not valid as a headline exposure because SNAP receipt can itself
  respond to policy and hardship.

## Decision

`SNAP EA TERMINATION: BEST CURRENT CONDITIONAL LEAD, NOT YET CLEAN GO`

This should be ranked above the insurance-side conditional leads for the current compact parquet,
because SIPP directly measures the main outcome and the signal survives a household-level correction.

It should not yet be called a publishable causal design. The next serious step would be a second-stage
SNAP-specific build, not more generic idea scanning:

- reconstruct household-level SNAP exposure from monthly receipt before EA termination;
- use richer raw SIPP food-security and hardship variables if available;
- implement a modern staggered DID/event-study estimator;
- run a stricter pretrend and cohort support audit;
- compare SIPP results to Household Pulse evidence as an external benchmark;
- position the contribution around annual SIPP food-security and health/coverage spillovers, not
  simply the existence of a food-insecurity effect.

## Updated Ranking

1. **SNAP Emergency Allotment termination**: best current conditional lead; household-level
   `food_insecure` rises about 7.6pp for lagged-SNAP households in early-ending states, but support
   is thin and secondary food outcomes are imprecise.
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

- `script/11_idea_scan/17_snap_ea_household_test.py`
- `report/36_snap_ea_household_test.md`
- `result/idea_scan/snap_ea_household_year_panel.parquet`
- `result/idea_scan/snap_ea_household_support.csv`
- `result/idea_scan/snap_ea_household_state_year_support.csv`
- `result/idea_scan/snap_ea_household_estimates.csv`
- `result/idea_scan/snap_ea_household_estimates_state_cluster.csv`
- `result/idea_scan/snap_ea_household_event.csv`
- `result/idea_scan/snap_ea_household_leave_one.csv`
