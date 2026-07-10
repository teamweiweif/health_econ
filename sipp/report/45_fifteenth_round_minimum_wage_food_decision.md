# Fifteenth-Round Minimum Wage Food-Security Decision

## Question

Can state minimum-wage increases support an adult SIPP paper on food insecurity, SNAP use, and
medical-financial spillovers among low-wage households?

## Why This Was Worth Testing

This was an adult, non-child, non-unwinding candidate with unusually good raw support:

- many states changed minimum wages during the 2018-2023 SIPP reference window;
- the compact parquet contains annual household food-security outcomes (`RFOODS`, `RFOODR`);
- the same file also contains monthly employment, earnings, SNAP, insurance, utilization, and
  out-of-pocket measures;
- current debates about wage floors, safety-net reliance, and household hardship remain active.

The key question was not whether the policy is important. It was whether this compact SIPP extract
adds a publishable, causally credible adult hardship angle beyond a crowded minimum-wage literature.

## Source Checks

- U.S. Department of Labor historical state minimum wage table:
  https://www.dol.gov/agencies/whd/state/minimum-wage/history
- U.S. Department of Labor current state minimum wage table:
  https://www.dol.gov/agencies/whd/minimum-wage/state

The screening policy file reconstructs state-year minimum wages from the DOL historical table and
uses the federal floor where relevant. For states with ranges, firm-size tiers, or local exceptions,
the fast screen uses the highest listed statewide value. That is adequate for a go/no-go screen but
not precise enough for a final statutory treatment panel.

## Design

Source:

- `data/analysis_ready/sipp_2018_2024_person_month_panel.parquet`

Unit:

- household-year, reference years 2018-2023.

Primary target:

- household with at least one adult low-wage worker;
- adult age 19-64;
- at least six observed months;
- employed in at least half of observed months;
- annual earnings between $1 and $35,000;
- family FPL <= 300%.

Secondary target:

- household with at least one low-education adult.

Treatment:

- annual state minimum-wage increase x target household;
- alternative binary treatment for increases of at least $0.50.

Fixed effects:

- state-year;
- state-target;
- target-year.

Standard errors:

- clustered by state.

## Support

Primary low-wage household target:

- 98,500 household-years.
- 95,960 households.
- 51 states.
- 21,260 target household-years.
- 8,739 target household-years with any minimum-wage increase.
- 6,582 target household-years with at least a $0.50 increase.

Secondary low-education household target:

- 31,257 target household-years.
- 12,579 target household-years with any minimum-wage increase.
- 9,584 target household-years with at least a $0.50 increase.

Policy variation is also broad: depending on year, 9 to 28 states have an increase, and 8 to 26
states have an increase of at least $0.50.

## Main Results

Low-wage household, continuous increase intensity:

- `food_insecure`: -0.0011, state-clustered se 0.0093, t -0.12.
- `very_low_food`: +0.0042, state-clustered se 0.0076, t 0.55.
- `food_score`: +0.0276, state-clustered se 0.0525, t 0.53.
- `snap_any`: +0.0085, state-clustered se 0.0089, t 0.95.
- `uninsured`: -0.0046, state-clustered se 0.0064, t -0.72.
- `oop_any`: +0.0048, state-clustered se 0.0097, t 0.49.
- `worker_share`: -0.0099, state-clustered se 0.0063, t -1.55.
- `log_earnings`: -0.0521, state-clustered se 0.0795, t -0.66.

Low-wage household, >= $0.50 increase:

- `food_insecure`: +0.0089, state-clustered se 0.0094, t 0.95.
- `very_low_food`: +0.0121, state-clustered se 0.0092, t 1.32.
- `food_score`: +0.0679, state-clustered se 0.0524, t 1.30.
- `snap_any`: +0.0071, state-clustered se 0.0107, t 0.66.
- `uninsured`: -0.0126, state-clustered se 0.0089, t -1.41.
- `oop_any`: -0.0022, state-clustered se 0.0122, t -0.18.
- `worker_share`: -0.0164, state-clustered se 0.0076, t -2.15.
- `log_earnings`: -0.0831, state-clustered se 0.0862, t -0.96.

Low-education household, continuous increase intensity:

- `food_insecure`: +0.0066, state-clustered se 0.0081, t 0.81.
- `very_low_food`: +0.0070, state-clustered se 0.0057, t 1.22.
- `food_score`: +0.0373, state-clustered se 0.0350, t 1.06.
- `snap_any`: -0.0053, state-clustered se 0.0056, t -0.95.
- `uninsured`: -0.0067, state-clustered se 0.0067, t -1.00.
- `oop_any`: -0.0022, state-clustered se 0.0104, t -0.22.
- `worker_share`: -0.0039, state-clustered se 0.0055, t -0.70.
- `log_earnings`: -0.0483, state-clustered se 0.0500, t -0.97.

## Interpretation

This fails the publishable-SIPP threshold despite excellent support:

- the primary food-insecurity estimate is essentially zero;
- the stronger binary increase and low-education specifications move food insecurity and very low
  food security in the wrong direction;
- there is no clear earnings or employment first-stage mechanism in the compact parquet;
- the small insurance and doctor-visit signals are secondary and do not rescue the food-security
  framing;
- exposure is too crude because the compact parquet lacks occupation, industry, hourly wage, firm
  coverage, tip status, local wage ordinances, and statutory exemption details;
- the existing minimum-wage literature is crowded, so a SIPP paper would need a strong distinctive
  hardship result rather than a null/mixed reduced-form screen.

## Decision

`MINIMUM WAGE FOOD-SECURITY SPILLOVER: LARGE SUPPORT, BUT NO CLEAN GO`

This should not become the next main paper. It is useful as evidence that the compact parquet can
support broad household-year hardship designs, but the actual signal is not strong enough and not
coherent enough to displace the SNAP Emergency Allotment lead.

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
10. **Minimum-wage food-security spillovers**: support is large, but the main food-security signal is
    null or wrong-signed and exposure is too crude for this crowded literature.
11. **Washington Working Families Tax Credit**: policy is strong, but 2023 treated support and tax
    eligibility measurement are too weak.
12. **Pandemic UI early termination**: clean timing, but no-go even with food-security outcomes.
13. **No Surprises Act**: excellent policy, SIPP measurement too indirect.
14. **STLDI expansion/state regulation**: no coherent SIPP signal.
15. **State-Based Marketplace transitions**: wrong-signed dynamics.

## New Artifacts

- `script/11_idea_scan/21_minimum_wage_food_security_test.py`
- `report/44_minimum_wage_food_security_test.md`
- `result/idea_scan/minimum_wage_food_policy.csv`
- `result/idea_scan/minimum_wage_food_household_year_panel.parquet`
- `result/idea_scan/minimum_wage_food_support.csv`
- `result/idea_scan/minimum_wage_food_year_support.csv`
- `result/idea_scan/minimum_wage_food_estimates.csv`
