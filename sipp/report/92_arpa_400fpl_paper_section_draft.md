# Paper Section Draft: ARPA 400% FPL Subsidy-Cliff Removal

## Working Title

**Did Removing the ACA Subsidy Cliff Reduce Uninsurance? SIPP Evidence from ARPA's 400% FPL Threshold Change**

## One-Paragraph Abstract Draft

The Affordable Care Act originally limited Marketplace premium tax credit eligibility to households with incomes at or below 400 percent of the federal poverty level, creating a subsidy cliff for households just above the threshold. The American Rescue Plan Act temporarily removed this cliff by capping benchmark-plan premium contributions as a share of income, and the expiration of enhanced premium tax credits has made the cliff a central policy issue again. This paper uses 2017-2023 SIPP person-month data and a local difference-in-discontinuities design around 400 percent FPL to test whether the cliff removal reduced uninsurance among nonelderly adults near the threshold. In the locked primary sample of adults age 26-64 with monthly family income between 350 and 450 percent FPL, uninsurance above the threshold falls by 2.8 percentage points after ARPA relative to below-threshold adults. Coverage-source decompositions show that the full-sample mechanism is mixed, but direct-market/subsidy proxies rise by 7.4 percentage points among adults not coming from employer-related coverage. The evidence supports a conditional-go coverage-affordability paper, with important limitations from monthly-versus-annual income measurement, nonempty placebo thresholds, and employer-source mixing.

## Introduction Skeleton

### Paragraph 1: Policy problem

The ACA Marketplace subsidy schedule has long contained a sharp affordability problem at 400 percent FPL. Under the original premium tax credit rules, households above the cutoff generally lost eligibility for federal premium subsidies even when unsubsidized premiums represented a large share of income. ARPA temporarily removed this cliff by extending premium tax credit eligibility above 400 percent FPL when benchmark premiums exceeded the specified income contribution cap. The expiration of enhanced premium tax credits at the end of 2025 has made the 400 percent cliff a current policy issue again, with policy organizations warning of premium increases and enrollment losses concentrated among above-400 percent FPL households, older adults, and high-premium areas.

### Paragraph 2: Empirical gap

Existing evidence establishes the policy stakes but leaves an empirical gap. Official CMS and IRS sources document the policy rule. KFF, Urban, RWJF, and BPC quantify affordability exposure and projected enrollment or coverage consequences. Recent Marketplace administrative research estimates demand and simulates subsidy targeting. Earlier academic work shows that ACA subsidy thresholds can affect insurance coverage and financial outcomes. Less is known about whether ARPA's actual removal of the 400 percent FPL cliff reduced uninsurance in national person-month survey data using a local pre/post threshold design.

### Paragraph 3: Design

This paper uses the SIPP's monthly coverage data to estimate a difference-in-discontinuities design around 400 percent FPL. The analysis compares adults just above and just below the threshold before and after ARPA, allowing for local linear income gradients, threshold-side interactions, state fixed effects, reference-month fixed effects, reference-year fixed effects, and demographic controls. The primary sample is adults age 26-64, excluding Medicare-covered months, with monthly family FPL between 350 and 450 percent in reference years 2017-2023.

### Paragraph 4: Main results

The primary estimate suggests that ARPA's removal of the 400 percent cliff is associated with a 2.8 percentage point reduction in uninsurance above the threshold relative to below-threshold adults. The estimate is stable in sign across bandwidth specifications and is not reproduced by pre-ARPA fake-policy tests at 400 percent FPL. However, full-sample source decomposition does not support a pure Marketplace-enrollment story: employer-related private coverage also rises in the broad sample.

### Paragraph 5: Mechanism and limits

Mechanism evidence is clearest among adults not coming from employer-related coverage. In lagged non-employer months, direct-market/subsidy proxy coverage rises by 7.4 percentage points, while employer-related source coverage does not rise. This pattern is consistent with an affordability response on the direct-market margin. The paper remains a conditional-go design because annual-FPL mechanism evidence is weaker, nearby placebo thresholds are not empty, and older-adult heterogeneity does not yet align cleanly with premium-exposure priors.

## Literature and Gap Paragraph

This paper connects three literatures. First, it contributes to work on ACA Marketplace subsidies and coverage by studying a federal threshold change that directly altered premium tax credit eligibility above 400 percent FPL. Prior subsidy-threshold research demonstrates that ACA subsidy eligibility can affect coverage and financial outcomes, but the ARPA removal of the 400 percent cliff creates a distinct pre/post threshold shock. Second, it complements policy simulation and monitoring work on enhanced premium tax credits. KFF, Urban, RWJF, and BPC document who is exposed to the return of the cliff and model likely affordability and coverage effects, but those analyses are not national SIPP person-month quasi-experimental estimates. Third, it complements Marketplace administrative demand studies by shifting the outcome from Marketplace selection alone to insurance coverage and uninsurance in national survey microdata. The contribution is therefore not a broad claim of first evidence on enhanced PTCs, but a narrow national microdata test of whether removing the 400 percent cliff translated into lower uninsurance near the threshold.

## Empirical Design Draft

### Data

The analysis uses the SIPP 2018-2024 public-use files, corresponding to reference years 2017-2023. The unit of analysis is the adult person-month. The primary analysis panel is `data/analysis_ready/sipp_2018_2024_person_month_panel.parquet`, supplemented with private-source extracts for `RPRITYPE1` and employer-related source variables. The primary sample includes adults age 26-64, excludes Medicare-covered months, requires valid state and positive person-month weight, and restricts monthly family income to 350-450 percent FPL.

### Treatment threshold

The policy threshold is 400 percent FPL. The primary running variable is monthly family FPL, constructed from `TFINCPOV` and centered at 4.0. The primary treatment contrast is the interaction between being above 400 percent FPL and the post-ARPA period, coded as reference year 2021 or later. A robustness check uses April 2021 as the implementation month.

### Model

The locked specification is:

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

The running function is local linear and observations receive a triangular kernel weight within the 350-450 percent FPL bandwidth. Covariates include age, sex, race/ethnicity, and disability controls. Standard errors are reported clustered at the person and state levels.

### Outcomes

The primary outcome is monthly uninsurance, defined from `RHLTHMTH`. The secondary coverage counterpart is any coverage. Mechanism outcomes distinguish direct-purchase/Marketplace/subsidy proxies from employer-related source coverage. The primary mechanism composite is `market_or_subsidy`; the primary mechanism threat variable is `source_employer_related`.

## Results Narrative Draft

### Main estimate

In the primary sample of 215,972 person-months and 23,888 adults, the coefficient on `above400 x post_year2021` for uninsurance is -0.0277. The person-clustered standard error is 0.0141 and the state-clustered standard error is 0.0151. The corresponding any-coverage estimate is +0.0277. This implies a local 2.8 percentage point reduction in uninsurance above 400 percent FPL after ARPA relative to below-threshold adults.

### Source decomposition

The full-sample direct-market mechanism is positive but not definitive. The `market_or_subsidy` coefficient is +0.0202 and the direct-purchase coefficient is +0.0208, but neither is precise under the preferred clustered inference. Employer-related source coverage also rises by +0.0301. Therefore, the full sample supports a coverage-affordability result but not a clean Marketplace-channel result.

### Mechanism sample

The mechanism is stronger among lagged non-employer person-months. In this sample of 71,638 person-months, `market_or_subsidy` rises by +0.0739 with a person-clustered standard error of 0.0328 and state-clustered standard error of 0.0350. Direct purchase rises by +0.0735. Employer-related source coverage falls slightly rather than rising. This is the strongest evidence that the policy operated through a direct-market affordability margin for adults who were plausibly exposed to non-employer coverage choices.

### Contrast sample

Among lagged current-employer months, uninsurance is essentially unchanged, with a coefficient of -0.0011. This contrast is consistent with the interpretation that the uninsured response is not primarily driven by adults already attached to current-employer coverage.

## Robustness Narrative Draft

The main uninsured result is stable across bandwidths: all five tested bandwidth specifications are negative, with a median coefficient of -0.0260 and a range from -0.0283 to -0.0255. Lagged non-employer `market_or_subsidy` is also stable across bandwidths, with a median coefficient of +0.0739 and a range from +0.0667 to +0.0869. Donut specifications preserve the sign of the main uninsured effect but weaken precision, suggesting the signal is meaningfully local to the threshold. Pre-ARPA fake-policy tests at 400 percent FPL are near zero. However, placebo thresholds are not empty, and annual-FPL mechanism estimates do not reproduce the monthly-FPL direct-market pattern. These checks support conditional-go language rather than a final unconditional causal claim.

## Identification Threats Paragraph

The central identifying concern is that other ARPA-era changes could have shifted coverage gradients around income thresholds in ways unrelated to the 400 percent cliff. The design addresses this by focusing on a real federal policy cutoff, using local income controls, reporting pre-ARPA fake-policy tests, and showing placebo thresholds. Still, placebo results are not empty, so the paper must present them as a serious threat. A second concern is income measurement: premium tax credit eligibility is based on annual income, while the strongest SIPP design uses monthly family FPL. Annual-FPL estimates preserve the uninsured sign but not the direct-market mechanism, so the interpretation should be framed as a monthly-income local response near the statutory cliff. A third concern is source mixing: employer-related private coverage rises in the full sample, making it inappropriate to claim a pure Marketplace channel. The lagged non-employer mechanism sample helps but does not fully eliminate this concern.

## Table Captions

Table 1. Sample Support and Cell Means Around 400 Percent FPL.

This table reports weighted coverage means and sample support by period and threshold side for the main sample and mechanism subsamples.

Table 2. Local Difference-in-Discontinuities Estimates Around 400 Percent FPL.

This table reports coefficients on `above400 x post_year2021` for uninsured, any coverage, direct-market/subsidy proxies, and employer-related source coverage in the locked 350-450 percent FPL bandwidth.

Table 3. Coverage-Source Decomposition and Mechanism Samples.

This table compares the full sample, lagged non-employer months, and lagged current-employer months to assess whether the coverage response is consistent with a direct-market affordability mechanism.

Table 4. Robustness Across Bandwidths, Donuts, FPL Measures, and Timing.

This table summarizes whether the main uninsured and mechanism estimates are stable across pre-specified sensitivity checks.

Table 5. Placebo and Falsification Tests.

This table reports placebo thresholds and pre-ARPA fake-policy tests used to assess whether the observed 400 percent pattern is distinctive.

## Figure Captions

Figure 1. Coverage Outcomes Around 400 Percent FPL, Main Sample.

This figure plots binned weighted means for uninsured and coverage-source outcomes around the 400 percent FPL threshold, separately by pre/post ARPA period.

Figure 2. Coverage Outcomes Around 400 Percent FPL, Lagged Non-Employer Sample.

This figure repeats the binned means for adults not coming from employer-related coverage in the prior month.

Figure 3. Coverage Outcomes Around 400 Percent FPL, Lagged Current-Employer Sample.

This figure provides a mechanism contrast for adults coming from current-employer coverage in the prior month.

Figure 4. Bandwidth Robustness of Primary and Mechanism Estimates.

This figure plots the `above400 x post_year2021` coefficient across bandwidths for the main uninsured outcome and the lagged non-employer market/subsidy mechanism.

## Claim Discipline

Use:

- "associated with a local reduction in uninsurance";
- "consistent with a direct-market affordability mechanism among lagged non-employer adults";
- "conditional-go evidence";
- "national SIPP person-month evidence."

Avoid:

- "clean RDD";
- "proves Marketplace enrollment rose for all";
- "estimates 2026 expiration";
- "older adults drive the effect";
- "annual-income eligibility is directly observed";
- "placebo tests are clean."

## Immediate Drafting Need

Before turning this into a manuscript introduction, add formal citations and full bibliographic entries for:

- CMS ARPA Marketplace fact sheet;
- IRS premium tax credit eligibility guidance;
- KFF 2026 Marketplace update;
- KFF older middle-income subsidy cliff quick insight;
- Urban enhanced PTC coverage-loss projections;
- RWJF Marketplace Pulse over-400 FPL analysis;
- Bipartisan Policy Center enhanced PTC brief;
- Drake, Meiselbach, and Polsky 2025;
- Gallagher, Gopalan, and Grinstein-Weiss 2019.
