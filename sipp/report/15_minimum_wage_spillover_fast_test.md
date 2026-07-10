# Minimum Wage Spillover Fast Test

## Verdict

`LARGE-SUPPORT-NAIVE-SPILLOVER-SIGNAL-BUT-ID-WEAK`

This is feasible with the current SIPP parquet and official DOL policy data, but it is not yet a
top-field idea by itself. The minimum-wage employment/wage literature is crowded, and the uploaded
parquet lacks occupation, industry, and clean pre-policy hourly wages. The only possible SIPP
contribution is a safety-net and insurance spillover paper: do wage floors reduce Medicaid/SNAP
receipt, change uninsured risk, or alter medical financial exposure among exposed adults?

## Policy/Data Construction

- Source: U.S. Department of Labor historical state minimum wage table.
- Effective wage: max(state listed wage, federal floor); for ranges this fast screen uses the
  highest listed statewide value.
- Treatment intensity: annual state minimum-wage increase from the previous January.
- Exposure group: adults 19-64 with high school or less.
- Comparison group: adults with some college or more.
- Model: weighted individual-month DDD screen with state and year fixed effects. This is a screen,
  not a final clustered event-study design.
- Coefficient: `minimum wage increase x high-school-or-less`.

## Policy Support By Year

| year | states any increase | states >= $0.50 | mean positive increase |
|---:|---:|---:|---:|
| 2018 | 21 | 12 | 0.58 |
| 2019 | 26 | 17 | 0.97 |
| 2020 | 9 | 8 | 0.75 |
| 2021 | 25 | 15 | 0.68 |
| 2022 | 26 | 22 | 0.80 |
| 2023 | 28 | 26 | 0.92 |

## SIPP Support

| group | persons | treated persons | SNAP events | Medicaid events | uninsured events |
|---|---:|---:|---:|---:|---:|
| adult_hs_or_less | 34582 | 16611 | 93972 | 175994 | 142110 |
| adult_some_college_plus | 55547 | 30288 | 53406 | 122475 | 99546 |

## Adult 19-64 Fast DDD Results

| outcome | coef_low_educ_x_mw_increase | se_hc1 | t_stat | persons | treated_low_educ_persons | treated_low_educ_mean_w |
|---|---|---|---|---|---|---|
| direct_purchase | -0.0022 | 0.0010 | -2.2635 | 87582 | 16611 | 0.0666 |
| doctor_any | -0.0091 | 0.0016 | -5.8586 | 87582 | 16611 | 0.6704 |
| earnings_positive | 0.0088 | 0.0016 | 5.5590 | 87582 | 16611 | 0.6288 |
| employed_any_week | 0.0075 | 0.0015 | 4.8771 | 87582 | 16611 | 0.6571 |
| medicaid | 0.0224 | 0.0014 | 16.4825 | 87582 | 16611 | 0.3018 |
| oop_any | -0.0306 | 0.0017 | -18.2634 | 87582 | 16611 | 0.4295 |
| private | -0.0029 | 0.0016 | -1.8431 | 87582 | 16611 | 0.5317 |
| snap | -0.0137 | 0.0010 | -13.7760 | 87582 | 16611 | 0.1350 |
| ssi | -0.0101 | 0.0007 | -15.4795 | 87582 | 16611 | 0.0536 |
| tanf | 0.0015 | 0.0002 | 8.5166 | 87582 | 16611 | 0.0045 |
| uninsured | -0.0153 | 0.0012 | -12.2920 | 87582 | 16611 | 0.1791 |

## Interpretation

- Sample support is large.
- The identifying variation is real but broad; the standard errors here are screening standard
  errors, not final clustered inference. A publishable design would need a sharper exposure
  measure, ideally occupation/industry or pre-policy hourly wage. The uploaded parquet lacks those.
- If treated as a SIPP safety-net-spillover paper, this is a secondary candidate. It is weaker than
  the UI early-exit timing design and less directly tied to insurance than the PTC cliff.

## Next Checks

1. Add occupation/industry or baseline hourly-wage exposure if available in a richer SIPP extract.
2. Use event studies around states with large increases only.
3. Check SNAP/Medicaid crowd-out and uninsured effects with placebo high-education groups.
4. Do not headline ordinary wage/employment effects unless the contribution is explicitly tied to
   safety-net and insurance spillovers.

## Source Check

- U.S. Department of Labor historical state minimum wage table:
  https://www.dol.gov/agencies/whd/state/minimum-wage/history
- DOL current state minimum wage table:
  https://www.dol.gov/agencies/whd/minimum-wage/state

## Outputs

- `result/idea_scan/minimum_wage_policy_dol_history.csv`
- `result/idea_scan/minimum_wage_spillover_estimates.csv`
- `result/idea_scan/minimum_wage_spillover_year_support.csv`
- `result/idea_scan/minimum_wage_spillover_sample_support.csv`
