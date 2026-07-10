# Thirteenth-Round Pandemic UI Food-Security Decision

## Question

Does the 2021 early termination of federal pandemic unemployment benefits become a stronger SIPP
idea when the outcome is food insecurity rather than insurance spillovers?

## Why This Was Worth Re-Testing

The earlier pandemic UI screen had one advantage and one major weakness:

- advantage: the policy timing was direct and externally documented;
- weakness: SIPP's insurance/safety-net spillover outcomes had low power and no clean signal.

Because the compact parquet also contains `RFOODS` and `RFOODR`, it was worth asking whether UI
benefit withdrawal can be reframed around household food insecurity and SNAP substitution.

This remains an adult, non-child, non-unwinding candidate.

## Source Checks

- U.S. Department of Labor UIPL 14-21 Change 1:
  https://www.dol.gov/node/162738
- St. Louis Fed, The End of Emergency Pandemic Unemployment Benefits in 2021:
  https://www.stlouisfed.org/on-the-economy/2022/apr/end-emergency-pandemic-unemployment-benefits-2021
- St. Louis Fed, Ending Pandemic Unemployment Benefits Linked to Job Growth:
  https://www.stlouisfed.org/on-the-economy/2022/aug/ending-pandemic-unemployment-benefits-linked-job-growth
- NBER WP 29575:
  https://www.nber.org/papers/w29575

The policy timing remains valid: 26 states ended at least the $300 FPUC supplement before the
September 2021 federal expiration.

## Design

Source:

- `data/analysis_ready/sipp_2018_2024_person_month_panel.parquet`

Unit:

- person-year, reference years 2020 and 2021.

Primary sample:

- prime-age adults 25-54;
- FPL <= 400%;
- observed in both 2020 and 2021 for the primary balanced design.

Primary target:

- received unemployment compensation in January-May 2021.

Treatment:

- early-exit state x target x 2021.

Fixed effects:

- state-year;
- state-target;
- target-year.

Standard errors:

- clustered by state.

Main outcomes:

- `food_insecure`;
- `very_low_food`;
- `food_score`;
- `snap_any`;
- `ui_any`;
- `employed_share`;
- `uninsured`;
- `oop_any`.

## Support

Balanced UI-recipient target sample:

- 4,516 person-years.
- 2,218 persons.
- 127 target persons.
- 45 early-exit target persons in 2021.
- 85 control target persons in 2021.

Balanced broad-risk target sample:

- 4,516 person-years.
- 2,218 persons.
- 859 target persons.
- 387 early-exit target persons in 2021.

Unbalanced UI-recipient target sample:

- 10,386 person-years.
- 7,943 persons.
- 462 target persons.
- 152 early-exit target persons in 2021.

## Main Results

Primary balanced UI-recipient target:

- `food_insecure`: -0.0684, state-clustered se 0.0686.
- `very_low_food`: +0.0679, state-clustered se 0.0505.
- `food_score`: -0.0150, state-clustered se 0.2794.
- `snap_any`: +0.1086, state-clustered se 0.0988.
- `ui_any`: +0.0443, state-clustered se 0.1045.
- `employed_share`: +0.0738, state-clustered se 0.0997.
- `uninsured`: -0.0745, state-clustered se 0.0470.
- `oop_any`: +0.1836, state-clustered se 0.1177.

Balanced broad-risk target:

- `food_insecure`: -0.0728, state-clustered se 0.0341.
- `very_low_food`: -0.0077, state-clustered se 0.0271.
- `food_score`: -0.2154, state-clustered se 0.1250.
- `snap_any`: +0.0718, state-clustered se 0.0311.
- `ui_any`: -0.0665, state-clustered se 0.0448.
- `oop_any`: +0.1221, state-clustered se 0.0608.

Unbalanced UI-recipient sensitivity:

- `food_insecure`: -0.0198, state-clustered se 0.0607.
- `very_low_food`: +0.0772, state-clustered se 0.0493.
- `food_score`: +0.2077, state-clustered se 0.2551.
- `snap_any`: +0.0274, state-clustered se 0.0709.
- `ui_any`: +0.0746, state-clustered se 0.1057.

## Interpretation

This does not produce a credible SIPP paper:

- the primary treated UI-recipient cell is only 45 people in early-exit states;
- the intended first stage is not clean in the annual DDD;
- food insecurity does not rise in the primary or broad-risk balanced specifications;
- the SNAP substitution result is strongest in the broad-risk sample, but that sample is less tied
  to actual UI receipt;
- `RFOODS` and `RFOODR` are annual household measures repeated on person records, so the person-year
  screen is already generous.

The result is not just underpowered. It points in the wrong direction for the headline food-security
outcome.

## Decision

`PANDEMIC UI EARLY TERMINATION: NO-GO EVEN WITH FOOD-SECURITY OUTCOMES`

This direction should remain below SNAP EA and below the better insurance-side conditional leads.
The early termination policy shock is real, but the current SIPP extract does not provide enough
direct target support or a coherent food-security mechanism.

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
9. **Postpartum Medicaid extension**: important adult maternal-coverage policy, but compact SIPP has
   no direct birth/pregnancy variables and tiny support.
10. **Pandemic UI early termination**: clean timing, but no-go even with food-security outcomes.
11. **No Surprises Act**: excellent policy, SIPP measurement too indirect.
12. **STLDI expansion/state regulation**: no coherent SIPP signal.
13. **State-Based Marketplace transitions**: wrong-signed dynamics.

## New Artifacts

- `script/11_idea_scan/19_pandemic_ui_food_security_test.py`
- `report/40_pandemic_ui_food_security_test.md`
- `result/idea_scan/pandemic_ui_food_person_year_panel.parquet`
- `result/idea_scan/pandemic_ui_food_support.csv`
- `result/idea_scan/pandemic_ui_food_estimates.csv`
