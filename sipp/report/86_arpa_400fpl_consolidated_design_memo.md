# Consolidated Design Memo: ARPA 400% FPL Subsidy-Cliff Removal

## Verdict

`CONDITIONAL GO AS CURRENT LEAD SIPP IDEA`

The strongest current SIPP paper idea is:

**Did removing the ACA Marketplace 400% FPL subsidy cliff reduce uninsurance near the threshold? Evidence from a SIPP person-month difference-in-discontinuities design, 2017-2023.**

This should be framed as a **coverage-affordability paper**, not as a pure Marketplace-enrollment paper. The main outcome is uninsured / any coverage. Marketplace or direct-purchase uptake is a mechanism check, strongest among people not coming from employer coverage.

## Policy Hook

The policy is current and well-defined.

- CMS states that ARPA temporarily increased Marketplace premium tax credits so that households would pay no more than 8.5% of household income toward the benchmark plan.
- IRS eligibility guidance describes the baseline 400% FPL premium tax credit income cap outside the enhanced-credit years.
- KFF's 2026 Marketplace work reports that the expiration of enhanced premium tax credits has renewed enrollment and affordability pressure, especially around middle-income Marketplace enrollees.

Core policy contrast:

- Pre-ARPA: households above 400% FPL generally faced the ACA subsidy cliff.
- ARPA / enhanced-credit period: the cliff was removed; the benchmark premium contribution was capped.
- Current relevance: the 2026 expiration returned the cliff as a live policy problem.

## Data

Primary local data:

- `data/analysis_ready/sipp_2018_2024_person_month_panel.parquet`
- Reference years: 2017-2023.
- Unit: adult person-month.
- Main population: age 26-64, non-Medicare, valid state and monthly FPL.

Raw source supplements:

- `temp/scratch/rpritype1_2018_2024.parquet`
- `temp/scratch/cobra_source_job_vars_2018_2024.parquet`

Private-source fields used:

- `RPRITYPE1`
- `RPRITYPE2`
- `RMARKTPLACE`
- `EPRIEXCH1`, `EPRIEXCH2`
- `EPRISUBS1`, `EPRISUBS2`
- `EMDEXCH`, `EMDSUBS`
- `EPR1MTH`, `EPR2MTH`
- `EHEMPLY1`, `EHEMPLY2`

## Primary Sample

Primary analysis sample:

- Age 26-64.
- Non-Medicare.
- Monthly family FPL in 350-450% FPL.
- Reference years 2017-2023.
- Person-month weight positive.
- Running variable: monthly `TFINCPOV - 4.0`.

Primary support:

- 215,972 person-months.
- 23,888 persons.
- 52 state clusters.

## Primary Estimand

The estimand is a local difference-in-discontinuities:

```text
Y_ist = beta * 1[FPL_it > 400%] * 1[post-ARPA_t]
      + threshold side
      + post
      + local linear running variable terms
      + running x side
      + running x post
      + running x side x post
      + age, sex, race/ethnicity, disability
      + state FE
      + calendar month FE
      + year FE
      + error_ist
```

Primary bandwidth:

- 350-450% monthly FPL.
- Triangular kernel.

Primary post period:

- 2021-2023.

Primary outcome:

- `uninsured`.

Co-primary descriptive counterpart:

- `any_coverage`.

## Main Results

Primary source-decomposition result, monthly FPL 350-450%:

| Outcome | Coef | Person SE | Person t | State SE | State t | N |
|---|---:|---:|---:|---:|---:|---:|
| uninsured | -0.0277 | 0.0141 | -1.96 | 0.0151 | -1.83 | 215,972 |
| any coverage | +0.0277 | 0.0141 | +1.96 | 0.0151 | +1.83 | 215,972 |
| market/subsidy proxy | +0.0202 | 0.0137 | +1.47 | 0.0147 | +1.37 | 215,972 |
| direct purchase | +0.0208 | 0.0137 | +1.52 | 0.0145 | +1.43 | 215,972 |
| employer-related source | +0.0301 | 0.0190 | +1.59 | 0.0244 | +1.24 | 215,972 |

Interpretation:

- The main coverage result is a roughly 2.8 percentage point reduction in uninsurance above 400% FPL after ARPA.
- Full-sample Marketplace/direct-purchase uptake is positive but not strong enough to be the headline.
- Employer-related source also rises in the full sample, so the broad mechanism is mixed.

## Mechanism Sample

The cleanest mechanism sample is **lagged non-employer person-months**:

- Previous month had no employer-related source.
- This focuses on people whose next-month response is not naturally employer-origin coverage.

Mechanism estimates:

| Outcome | Coef | Person SE | Person t | State SE | State t | N |
|---|---:|---:|---:|---:|---:|---:|
| uninsured | -0.0457 | 0.0331 | -1.38 | 0.0425 | -1.08 | 71,638 |
| market/subsidy proxy | +0.0739 | 0.0328 | +2.25 | 0.0350 | +2.11 | 71,638 |
| direct purchase | +0.0735 | 0.0328 | +2.24 | 0.0334 | +2.20 | 71,638 |
| employer-related source | -0.0100 | 0.0058 | -1.72 | 0.0066 | -1.52 | 71,638 |

Interpretation:

- This is the best evidence that the ARPA 400% threshold response operates through an affordability/direct-market margin.
- It should be the secondary mechanism table, not the primary estimand.

## Mechanism Contrast

Lagged current-employer person-months:

| Outcome | Coef | Person SE | Person t | State SE | State t | N |
|---|---:|---:|---:|---:|---:|---:|
| uninsured | -0.0011 | 0.0021 | -0.52 | 0.0019 | -0.56 | 126,551 |
| market/subsidy proxy | +0.0136 | 0.0064 | +2.12 | 0.0078 | +1.74 | 126,551 |
| direct purchase | +0.0138 | 0.0064 | +2.17 | 0.0078 | +1.78 | 126,551 |
| employer-related source | -0.0007 | 0.0029 | -0.24 | 0.0026 | -0.26 | 126,551 |

Interpretation:

- Uninsurance barely moves among people coming from current-employer coverage.
- This contrast supports using lagged non-employer months as the mechanism sample.
- However, small direct-market movement exists even among lagged employer people, so the mechanism is not perfectly isolated.

## Robustness Evidence

Bandwidth stability:

- Main uninsured bandwidth specs: median -0.0260; range -0.0283 to -0.0255; negative in 5/5 specifications.
- Lagged non-employer market/subsidy bandwidth specs: median +0.0739; range +0.0667 to +0.0869; positive in 5/5 specifications and significant under both person and state clustering in 5/5.

Donut robustness:

- Main uninsured remains negative with donuts 0.025, 0.05, 0.10, 0.15.
- Precision weakens as threshold-adjacent observations are removed.
- Lagged non-employer market/subsidy stays positive but becomes imprecise for larger donuts.

Annual-FPL robustness:

- Annual-FPL uninsured remains negative.
- Annual-FPL market/subsidy mechanism does not survive.
- This is a real measurement risk because the statutory cliff is annual-income based while the strongest SIPP design uses monthly poverty ratios.

Placebo checks:

- Pre-ARPA fake-policy estimates at 400% FPL are near zero.
- Placebo thresholds are not empty:
  - 3.5 FPL uninsured is also negative.
  - 3.0 FPL market/subsidy is strongly negative.
- These do not reproduce the full 400% pattern, but they prevent an unconditional go.

## Required Figures

Already generated:

- `result/idea_scan/arpa400_paper_bins_main.png`
- `result/idea_scan/arpa400_paper_bins_lag_nonemployer.png`
- `result/idea_scan/arpa400_paper_bins_lag_current_employer.png`
- `result/idea_scan/arpa400_bandwidth_robustness_coefficients.png`

Use in paper draft:

- Main binned uninsured plot.
- Lagged non-employer mechanism plot.
- Bandwidth coefficient plot.

Do not use plots alone as evidence. The binned mechanism plots are noisy and must be paired with the regression table.

## Identification Threats

1. Monthly vs annual income:
   The SIPP monthly FPL variable gives the strongest design, but statutory premium tax credit eligibility is annual-income based.

2. Nearby income-gradient placebo:
   The 3.5 FPL placebo uninsured coefficient is not zero. The paper must show placebo thresholds transparently.

3. Employer-source mixing:
   Full-sample employer-related coverage rises. This is why the paper must not claim a pure Marketplace channel in the whole sample.

4. Older-adult null:
   The 50-64 gradient is not supportive even though older adults should face larger unsubsidized premiums.

5. State premium heterogeneity:
   The next pass must test whether response is stronger in high-premium states, not only by age.

## No-Go Triggers

Downgrade or abandon as a main paper if any of the following occurs in the paper-ready replication:

1. Main uninsured estimate changes sign or shrinks below 1 percentage point under the pre-specified primary bandwidth.
2. Main uninsured estimate is equally large at multiple placebo thresholds with no distinctive 400% pattern.
3. Pre-ARPA fake-policy tests at 400% FPL become similar in size to the ARPA estimate.
4. Lagged non-employer market/subsidy mechanism becomes non-positive across bandwidths.
5. Employer-source movements fully account for the uninsured decline in the primary design.
6. Annual-FPL and monthly-FPL discrepancies cannot be explained or bounded.

## Current Paper Positioning

Recommended positioning:

`Difference-in-discontinuities evidence that removing the ACA 400% FPL subsidy cliff reduced uninsurance near the threshold, with direct-market mechanism evidence concentrated among adults not coming from employer coverage.`

Avoid:

- "ARPA clearly increased Marketplace enrollment for all above-400% adults."
- "This is a clean RDD."
- "Older adults drive the response."

## Next Work Unit

The next work unit should be a paper-style empirical design package:

- one regression table with primary and mechanism specifications;
- one figure set with binned means and bandwidth robustness;
- one source-reading/literature-gap memo;
- one explicit identification-threat section;
- one pre-analysis-style specification lock.

No further tuning should be done until that package is written.
