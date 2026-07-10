# Specification Lock and Identification Memo: ARPA 400% FPL Subsidy-Cliff Removal

## Status

`PRE-ANALYSIS-STYLE LOCK FOR NEXT PAPER PACKAGE`

This memo locks the current leading SIPP idea for the next paper-style stage:

**Did ARPA's removal of the ACA Marketplace 400% FPL subsidy cliff reduce uninsurance near the threshold? A SIPP person-month difference-in-discontinuities design, 2017-2023.**

No additional model tuning should be run before this locked package is reproduced. New analyses are allowed only if they are labeled as pre-specified extensions or later diagnostics.

## Research Question

Primary question:

> Did removing the ACA Marketplace 400% FPL premium tax credit cliff reduce uninsurance among nonelderly adults near 400% FPL?

Secondary mechanism question:

> Is the coverage response concentrated among adults not coming from employer-related coverage, where Marketplace/direct-purchase take-up is the plausible margin?

## Current Contribution

The contribution is not that enhanced premium tax credits are unstudied. The contribution is narrower:

**A national SIPP person-month, local 400% FPL pre/post threshold design for ARPA's cliff removal, with uninsured and coverage-source outcomes.**

This complements:

- official CMS/IRS policy documentation;
- KFF, Urban, RWJF, and BPC enhanced-PTC expiration analysis;
- Marketplace administrative demand and simulation studies;
- earlier ACA subsidy-threshold papers.

## Locked Data Inputs

Primary panel:

- `data/analysis_ready/sipp_2018_2024_person_month_panel.parquet`

Supplemental private-source extracts:

- `temp/scratch/rpritype1_2018_2024.parquet`
- `temp/scratch/cobra_source_job_vars_2018_2024.parquet`

Primary scripts already used:

- `sipp/script/11_idea_scan/40_arpa_400fpl_source_decomposition_test.py`
- `sipp/script/11_idea_scan/41_arpa_400fpl_robustness_pack.py`
- `sipp/script/11_idea_scan/42_arpa_400fpl_paper_tables_figures.py`

Locked result references:

- `sipp/result/idea_scan/arpa400_source_decomposition_estimates.csv`
- `sipp/result/idea_scan/arpa400_source_decomposition_support.csv`
- `sipp/result/idea_scan/arpa400_source_decomposition_cell_means.csv`
- `sipp/result/idea_scan/arpa400_robustness_estimates.csv`
- `sipp/result/idea_scan/arpa400_robustness_summary.csv`
- `sipp/result/idea_scan/arpa400_paper_design_table.csv`
- `sipp/result/idea_scan/arpa400_paper_binned_means.csv`

Locked figure references:

- `sipp/result/idea_scan/arpa400_paper_bins_main.png`
- `sipp/result/idea_scan/arpa400_paper_bins_lag_nonemployer.png`
- `sipp/result/idea_scan/arpa400_paper_bins_lag_current_employer.png`
- `sipp/result/idea_scan/arpa400_bandwidth_robustness_coefficients.png`

## Locked Sample

Primary sample:

- Age 26-64.
- Non-Medicare.
- Reference years 2017-2023.
- Valid state identifier.
- Positive person-month weight.
- Monthly family FPL between 3.5 and 4.5.
- Unit: person-month.

Primary support:

- 215,972 person-months.
- 23,888 persons.
- 52 state clusters.

The age 26 lower bound avoids ACA dependent-coverage contamination. The upper bound avoids Medicare-age coverage transitions.

## Locked Running Variable and Threshold

Primary running variable:

- `monthly_fpl = bounded_numeric(TFINCPOV, 0, 20)`.

Threshold:

- `400% FPL`, coded as `monthly_fpl > 4.0`.

Running variable in model:

- `running = monthly_fpl - 4.0`.

Primary bandwidth:

- 3.5-4.5 FPL, equivalent to bandwidth 0.50 around 4.0.

Primary kernel:

- triangular kernel: `1 - abs(running) / bandwidth`, clipped at zero.

## Annual-Income Issue

The statutory premium tax credit cliff is annual-income based. The primary SIPP design uses monthly `TFINCPOV` because:

- SIPP's monthly coverage outcomes align naturally to person-month analysis;
- the monthly FPL variable gives stronger support and more local variation;
- the idea-screen signal is strongest and most coherent in monthly person-month data.

Annual robustness:

- `annual_fpl = bounded_numeric(TFCYINCPOV, 0, 20)`.
- Annual-FPL estimates are robustness and measurement-check evidence, not the primary design.

Interpretation constraint:

- If annual-FPL and monthly-FPL evidence remain materially inconsistent, the paper must describe the estimate as a monthly-income local coverage response near the statutory cliff, not as a clean tax-eligibility estimate.

## Locked Treatment Timing

Primary post indicator:

- `post_year2021 = 1[reference_year >= 2021]`.

Alternative timing robustness:

- `post_apr2021 = 1[reference_year * 100 + reference_month >= 202104]`.

Primary reason:

- ARPA implementation and Marketplace subsidy availability began in 2021; the year-level post is the main screen and avoids over-interpreting exact monthly take-up timing.

Robustness reason:

- The April 2021 version tests whether the signal is sensitive to the more exact implementation month.

## Locked Outcomes

Primary outcome:

- `uninsured = 1[RHLTHMTH == 2]`.

Secondary descriptive counterpart:

- `any_coverage = 1 - uninsured`.

Mechanism outcomes:

- `direct_purchase`.
- `marketplace_flag`.
- `subsidized_private`.
- `market_or_subsidy`.
- `source_employer_related`.
- `source_current_employer`.
- `source_former_employer`.
- `rpritype1_employer`.

Primary mechanism composite:

- `market_or_subsidy`, combining direct-market, Marketplace, exchange, and subsidy indicators as constructed in the source-decomposition script.

Primary mechanism contrast:

- `source_employer_related`, using `RPRITYPE1` plus source/job-related private coverage fields.

Interpretation rule:

- `uninsured` is the headline outcome.
- `market_or_subsidy` and `direct_purchase` are mechanism outcomes.
- `source_employer_related` is a mechanism threat and decomposition outcome.

## Locked Model

The primary estimand is the coefficient on:

```text
above400 x post_year2021
```

The locked local difference-in-discontinuities model is:

```text
Y_ist = beta * above400_it * post_t
      + alpha1 * above400_it
      + alpha2 * post_t
      + f(running_it)
      + above400_it * f(running_it)
      + post_t * f(running_it)
      + above400_it * post_t * f(running_it)
      + X_it
      + state_s FE
      + reference_month_m FE
      + reference_year_y FE
      + error_ist
```

where:

- `above400_it = 1[monthly_fpl_it > 4.0]`;
- `post_t = post_year2021` in the primary model;
- `f(running_it)` is local linear;
- `X_it` includes age, sex, race/ethnicity, and disability controls as currently implemented;
- observations are weighted by person-month weight and triangular local kernel.

Inference to report:

- person-cluster standard errors;
- state-cluster standard errors;
- HC1 as secondary diagnostic only.

Primary decision should rely on person and state cluster inference, not HC1.

## Locked Primary Estimate

Primary source-decomposition table, monthly FPL 350-450%:

| Outcome | Coef | Person SE | Person t | State SE | State t | N |
|---|---:|---:|---:|---:|---:|---:|
| uninsured | -0.0277 | 0.0141 | -1.96 | 0.0151 | -1.83 | 215,972 |
| any coverage | +0.0277 | 0.0141 | +1.96 | 0.0151 | +1.83 | 215,972 |
| market/subsidy proxy | +0.0202 | 0.0137 | +1.47 | 0.0147 | +1.37 | 215,972 |
| direct purchase | +0.0208 | 0.0137 | +1.52 | 0.0145 | +1.43 | 215,972 |
| employer-related source | +0.0301 | 0.0190 | +1.59 | 0.0244 | +1.24 | 215,972 |

Allowed interpretation:

- Uninsurance falls by about 2.8 percentage points above 400% FPL after ARPA in the local monthly-FPL design.
- Full-sample source movement is mixed, so the paper cannot claim a pure Marketplace channel in the full sample.

## Locked Mechanism Sample

Primary mechanism sample:

- `lag_nonemployer_months`: prior month had no employer-related source.

Support:

- 71,638 person-months.

Locked mechanism estimates:

| Outcome | Coef | Person SE | Person t | State SE | State t | N |
|---|---:|---:|---:|---:|---:|---:|
| uninsured | -0.0457 | 0.0331 | -1.38 | 0.0425 | -1.08 | 71,638 |
| market/subsidy proxy | +0.0739 | 0.0328 | +2.25 | 0.0350 | +2.11 | 71,638 |
| direct purchase | +0.0735 | 0.0328 | +2.24 | 0.0334 | +2.20 | 71,638 |
| employer-related source | -0.0100 | 0.0058 | -1.72 | 0.0066 | -1.52 | 71,638 |

Allowed interpretation:

- The cleanest mechanism evidence is a direct-market/subsidy response among adults not coming from employer-related coverage.
- The uninsured estimate in this subgroup is directionally large but imprecise.

Not allowed:

- Do not use this subgroup as the headline causal estimand.
- Do not claim all above-400 adults moved into Marketplace coverage.

## Locked Mechanism Contrast

Contrast sample:

- `lag_current_employer_months`: prior month had current employer-related source.

Locked contrast:

- uninsured coefficient: -0.0011, near zero;
- market/subsidy coefficient: +0.0136;
- employer-related source coefficient: -0.0007.

Interpretation:

- Uninsurance barely moves among adults coming from current-employer coverage.
- This supports the lagged non-employer mechanism emphasis.
- It does not prove perfect source isolation because small direct-market movement still appears in employer-origin months.

## Locked Robustness Sequence

Report robustness in this order:

1. Bandwidths around 400% FPL:
   - 0.25, 0.35, 0.50, 0.75, 1.00.
   - Main uninsured must be shown for every bandwidth.
   - Lagged non-employer `market_or_subsidy` must be shown for every bandwidth.

2. Donut exclusions:
   - 0.025, 0.05, 0.10, 0.15 inside bandwidth 0.50.
   - Use to show whether the signal is only threshold-adjacent.

3. Annual-FPL robustness:
   - Use `TFCYINCPOV`-based `annual_fpl`.
   - Treat as measurement robustness and statutory-alignment check.

4. Post timing:
   - Compare `post_year2021` with `post_apr2021`.

5. Placebo thresholds:
   - Report placebo thresholds from the robustness pack.
   - Do not bury the 3.5 FPL uninsured placebo.

6. Pre-ARPA fake policy:
   - Report fake post tests within pre-ARPA years.
   - The current 400% fake-policy estimates are near zero.

7. Mechanism contrast:
   - Lagged non-employer versus lagged current-employer.

## Locked Robustness Facts

Current robustness facts:

- Main uninsured bandwidth specs: median -0.0260; range -0.0283 to -0.0255; negative in 5/5.
- Lagged non-employer market/subsidy bandwidth specs: median +0.0739; range +0.0667 to +0.0869; positive in 5/5 and significant under person and state clustering in 5/5.
- Main uninsured donut specs remain negative, but precision weakens.
- Lagged non-employer market/subsidy stays positive in donut specs, but loses precision for larger donuts.
- Annual-FPL uninsured is negative; annual-FPL market/subsidy does not survive.
- Pre-ARPA fake-policy tests at 400% FPL are near zero.
- Placebo thresholds are not empty, especially the 3.5 FPL uninsured placebo and 3.0 FPL market/subsidy placebo.

## Locked Table Shells

Table 1: Sample support and weighted cell means.

- Source: `arpa400_source_decomposition_support.csv`.
- Rows: main sample, older, younger, lagged non-employer, lagged current-employer.
- Columns: pre/post, below/above 400, person-months, persons, states, uninsured, employer-related source, direct purchase, market/subsidy.

Table 2: Primary local difference-in-discontinuities estimates.

- Source: `arpa400_paper_design_table.csv`.
- Rows: uninsured, any coverage, market/subsidy, direct purchase, employer-related source.
- Columns: coefficient, person-cluster SE/t, state-cluster SE/t, N.

Table 3: Mechanism decomposition.

- Source: `arpa400_source_decomposition_estimates.csv`.
- Panels: main sample, lagged non-employer, lagged current-employer.
- Outcomes: uninsured, market/subsidy, direct purchase, employer-related source.

Table 4: Robustness summary.

- Source: `arpa400_robustness_summary.csv`.
- Rows: main bandwidth, lagged non-employer bandwidth, donuts, annual FPL, post-April 2021, placebo thresholds, pre-ARPA fake policy.
- Columns: number of specs, median coefficient, range, sign share, significant specs under person/state clustering.

Table 5: Identification threats and falsification.

- Source: `arpa400_robustness_estimates.csv`.
- Rows: placebo thresholds, pre-ARPA fake policies, annual-FPL models, current-employer contrast.
- Purpose: show whether the 400% pattern is distinctive.

## Locked Figure Shells

Figure 1: Binned uninsured and source means around 400% FPL, main sample.

- File: `arpa400_paper_bins_main.png`.

Figure 2: Binned mechanism plot, lagged non-employer sample.

- File: `arpa400_paper_bins_lag_nonemployer.png`.

Figure 3: Binned mechanism contrast, lagged current-employer sample.

- File: `arpa400_paper_bins_lag_current_employer.png`.

Figure 4: Bandwidth robustness coefficient plot.

- File: `arpa400_bandwidth_robustness_coefficients.png`.

Rule:

- Figures are descriptive support, not standalone identification proof.
- Regression tables must carry the claim.

## Identification Assumptions

Required assumptions for the primary interpretation:

1. In the absence of ARPA cliff removal, local coverage discontinuities around 400% FPL would not have shifted discontinuously at 2021 in a way that specifically mimics the above-400 treatment.

2. The below-400 local group is a useful local comparison for above-400 adults after conditioning on local FPL slopes, FE, and covariates.

3. Other 2021 shocks do not create the same local above-versus-below 400% FPL pattern.

4. Monthly SIPP FPL is a useful proxy for local eligibility-margin exposure, even though statutory PTC eligibility is annual.

5. Coverage-source variables distinguish direct-market/subsidy response from employer-related private coverage well enough for mechanism analysis.

## Main Identification Threats

1. Monthly versus annual income.
   - The strongest result uses monthly FPL.
   - Annual-FPL mechanism evidence is weak.

2. Broader ARPA-era income gradients.
   - Placebo thresholds are not empty.
   - The paper must show placebo thresholds prominently.

3. Employer-source mixing.
   - Employer-related source rises in the full sample.
   - The full sample cannot support a pure Marketplace mechanism claim.

4. Older-adult gradient.
   - Policy priors suggest older adults should be more exposed to premium costs.
   - Current SIPP older-adult gradient is not supportive enough for a headline.

5. Premium geography.
   - The policy effect should plausibly be stronger in high-premium areas.
   - A later pre-specified extension should test high-premium state or rating-area proxies if cleanly linkable.

## Allowed Claims

Allowed:

- ARPA's removal of the 400% FPL subsidy cliff is associated with lower uninsurance above the threshold in a local SIPP monthly-FPL design.
- The main estimate is around a 2.8 percentage point uninsured decline.
- Mechanism evidence is strongest among adults not coming from employer-related coverage, where direct-market/subsidy proxies rise by about 7.4 percentage points.
- The paper complements simulation and Marketplace administrative-demand work by studying actual coverage outcomes in national SIPP microdata.
- The evidence is a conditional go, not final proof.

## Disallowed Claims

Disallowed:

- ARPA clearly increased Marketplace enrollment for all above-400 adults.
- This is a clean RDD.
- This is the first paper on ACA subsidy thresholds.
- This estimates the 2026 expiration effect.
- Older adults drive the result.
- The annual-income statutory mechanism is fully validated.
- Placebo thresholds are empty.
- Employer-related coverage is irrelevant.

## No-Go and Downgrade Rules

Downgrade or abandon the idea as a main paper if paper-ready replication shows any of the following:

1. Main uninsured estimate changes sign or shrinks below 1 percentage point in the locked 3.5-4.5 monthly-FPL bandwidth.

2. Placebo thresholds produce uninsured estimates as large and systematic as the 400% estimate.

3. Pre-ARPA fake-policy estimates at 400% FPL become similar in size to the ARPA estimate.

4. Lagged non-employer `market_or_subsidy` becomes non-positive across bandwidths.

5. Employer-related source changes can explain most of the full-sample uninsured decline.

6. Annual-FPL and monthly-FPL results cannot be reconciled even as a measurement distinction.

7. Figure diagnostics show extreme bin instability or sample holes around the threshold.

## Next Work Unit

Next artifact:

**Draft paper introduction and empirical design section**

Inputs:

- `88_arpa_400fpl_source_literature_gap_memo.md`
- this specification lock
- `arpa400_paper_design_table.csv`
- the four locked figures

Do not add new estimates to the introduction. Use only the locked estimates above.
