# Twenty-Fourth Round Decision: Public Charge / Immigrant Chilling Effect

## Decision

Status: **NO CLEAN GO FOR MAIN PAPER; KEEP AS DATA-UNLOCKED BACKUP ONLY**.

This round successfully removed the earlier data limitation: the compact SIPP parquet did not
include citizenship/nativity variables, but `ECITIZEN`, `EBORNUS`, and `ENATCIT` were extracted from
the raw Census SIPP zips and merged back to the person-month panel.

However, the first causal screen does **not** support a clean public-charge chilling-effect paper in
the current SIPP setup. The expected Medicaid/SNAP/public-benefit decline among low-income
noncitizens during 2019-2020 is not visible in a stable way. There is some directionally consistent
uninsurance/private-coverage movement, but not enough to carry a top-field causal paper.

## Why The Idea Was Worth Testing

The policy relevance is real.

External source checks:

- Federal Register history says DHS began applying the 2019 Public Charge Final Rule on February
  24, 2020, and stopped applying it after the March 9, 2021 judgment/vacatur path.
- USCIS says it stopped applying the Public Charge Final Rule to pending applications and petitions
  on March 9, 2021.
- KFF's 2022 public charge explainer states that the Biden Administration returned to the 1999
  field-guidance approach in March 2021 and that the 2022 final rule went into effect on December
  23, 2022.
- KFF's 2025/2026 public-charge coverage notes the issue is again active: immigrant adults report
  avoiding food, housing, or health-care assistance because of immigration-related worries.

So the policy question is current and important:

> Did public-charge policy changes cause low-income noncitizen adults to avoid Medicaid, SNAP, and
> other benefits, increasing uninsurance?

The SIPP attraction is also real: national person-month panel data can jointly observe citizenship,
coverage, SNAP/TANF/SSI, public/private insurance, Marketplace proxies, income, and state.

## What Was Added

Script:

- `sipp/script/11_idea_scan/31_public_charge_immigrant_chilling_test.py`

Main report:

- `sipp/report/63_public_charge_immigrant_chilling_test.md`

Supplemental extracted data:

- `sipp/temp/scratch/immigration_status_2018_2024.parquet`

Result tables:

- `sipp/result/idea_scan/public_charge_status_value_counts.csv`
- `sipp/result/idea_scan/public_charge_cell_means.csv`
- `sipp/result/idea_scan/public_charge_person_support.csv`
- `sipp/result/idea_scan/public_charge_model_support.csv`
- `sipp/result/idea_scan/public_charge_ddd_estimates.csv`

The extractor read all seven local raw SIPP primary CSV zips:

- 2018: 763,186 rows.
- 2019: 593,604 rows.
- 2020: 622,339 rows.
- 2021: 670,678 rows.
- 2022: 487,736 rows.
- 2023: 476,744 rows.
- 2024: 437,168 rows.

Total supplemental rows: 4,051,455.

## Variable Support

Citizenship/nativity rows after extraction:

- `ECITIZEN = 1`: 3,830,076 rows.
- `ECITIZEN = 2`: 221,379 rows.
- `EBORNUS = 1`: 3,443,557 rows.
- `EBORNUS = 2`: 607,898 rows.
- `ENATCIT` missing: 221,379 rows, consistent with noncitizen status.

Model support was not thin:

- Main monthly-FPL 250% cutoff sample: 1,543,116 person-months, 79,568 persons, 52 states.
- Noncitizen person-months: 150,321.
- Low-income noncitizen person-months: 93,408.
- Low-income noncitizen persons: 5,770.

So this is not a sample-size no-go.

## Design Tested

Unit: person-month.

Main DDD:

```text
noncitizen x low_income x chill_2019_2020
```

Reversal term:

```text
noncitizen x low_income x reversal_2021_2023
```

Pre period:

- 2017-2018.

Chilling/final-rule period:

- 2019-2020.

Reversal/post-rule period:

- 2021-2023.

Controls and fixed effects:

- State fixed effects.
- Calendar year-month fixed effects.
- FPL quadratic.
- Age quadratic.
- Sex, Black, Hispanic, disability.

Inference:

- State-clustered and person-clustered standard errors.

Outcomes:

- Medicaid.
- SNAP monthly participation.
- Public coverage.
- Uninsured.
- Any coverage.
- Private coverage.
- Direct purchase / Marketplace proxies.
- TANF and SSI.

## Main Result

For the main monthly-FPL 250% cutoff:

Chilling-period DDD:

- Medicaid: -0.8 pp, state-clustered t = -0.28.
- SNAP monthly: +1.1 pp, state-clustered t = 1.10.
- Public coverage: -0.2 pp, state-clustered t = -0.08.
- Uninsured: +2.3 pp, state-clustered t = 0.89.
- Any coverage: -2.3 pp, state-clustered t = -0.89.
- Private coverage: -2.8 pp, state-clustered t = -1.09.

For the tighter monthly-FPL 150% cutoff:

- Medicaid: +1.7 pp, state-clustered t = 0.80.
- SNAP monthly: +2.5 pp, state-clustered t = 1.56.
- Public coverage: +2.3 pp, state-clustered t = 1.10.
- Uninsured: +4.4 pp, state-clustered t = 1.28.
- Private coverage: -7.0 pp, state-clustered t = -1.99.

For annual-FPL 250% robustness:

- Medicaid: -1.0 pp, state-clustered t = -0.31.
- SNAP monthly: +1.0 pp, state-clustered t = 1.04.
- Public coverage: -0.5 pp, state-clustered t = -0.18.
- Uninsured: +4.7 pp, state-clustered t = 1.69.
- Private coverage: -5.3 pp, state-clustered t = -2.05.

## Interpretation

The uninsurance/private-coverage pattern is directionally interesting, especially in the annual-FPL
and 150% monthly-FPL versions. But the key mechanism fails:

- Medicaid does not fall robustly.
- SNAP does not fall; it is positive in the chilling period.
- Public coverage is not consistently negative.
- The strongest statistically visible movement is private coverage/uninsurance, not benefit
  avoidance.

That is not enough for a clean public-charge paper.

The main threat is also large: the 2019-2020 public-charge period overlaps the COVID shock and the
beginning of PHE administrative changes. This does not make the design impossible, but it means a
top-field design would need a much sharper source of variation than the current national
noncitizen-low-income DDD.

## Recommended Treatment Of This Idea

Do not use this as the current main project.

Keep it as a backup only if we can add sharper exposure:

1. Extract `TIMSTAT` despite the heavier raw-column position, to distinguish lawful permanent
   residents, temporary visa holders, and other initial immigration statuses if codes are usable.
2. Test Hispanic noncitizen and foreign-born household subgroups as mechanism checks, not as the
   main identifying design.
3. Add state-level immigrant policy climate or enforcement intensity if a credible external policy
   file is available.
4. Focus on uninsurance/private coverage only if Medicaid/SNAP mechanisms remain null, and be clear
   that it is not a direct benefit-avoidance result.
5. Avoid treating 2020 Medicaid as a clean public-charge outcome because of COVID and PHE overlap.

## Updated Ranking

1. **ARPA 400% FPL cliff removal** remains the most novel lead, but mechanism evidence is mixed.
2. **Late Medicaid expansion around 100-138% FPL** has the strongest new empirical signal, but a
   harder literature-gap problem.
3. **Public charge / immigrant chilling effect** is now data-unlocked but not empirically clean.

## Bottom Line

This was worth doing because it converted a variable-availability unknown into a tested empirical
fact. But based on the current first-pass DDD, public charge should not displace ARPA 400% FPL or
late Medicaid expansion as a lead SIPP paper.
