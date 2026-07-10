# README for Web GPT Review: ARPA 400% FPL SIPP Idea

## Purpose

Use this file to brief Web GPT or another high-reasoning model on the current leading SIPP idea without uploading the full parquet panel.

The project is currently:

`CONDITIONAL GO`

Working idea:

**Did ARPA's removal of the ACA Marketplace 400% FPL subsidy cliff reduce uninsurance near the threshold? A SIPP person-month difference-in-discontinuities design, 2017-2023.**

## Do Not Upload First

Do not start by uploading the full parquet data.

The current question is not raw data cleaning. It is:

- whether the idea is publishable;
- whether the identification is credible;
- whether the literature gap is correctly stated;
- whether the main estimates and robustness support a conditional go;
- how to frame the paper without overclaiming.

The small reports and CSV outputs below are enough for that review.

## Minimum Upload Set

Upload these first:

1. `sipp/report/92_arpa_400fpl_paper_section_draft.md`
2. `sipp/report/90_arpa_400fpl_specification_lock_and_identification_memo.md`
3. `sipp/report/88_arpa_400fpl_source_literature_gap_memo.md`
4. `sipp/result/idea_scan/arpa400_paper_design_table.csv`
5. `sipp/result/idea_scan/arpa400_robustness_summary.csv`

This is the smallest useful package for:

- paper framing;
- identification review;
- gap review;
- main estimate review;
- robustness review.

## Optional Stronger Upload Set

If Web GPT can accept more files, also upload:

6. `sipp/result/idea_scan/arpa400_source_decomposition_estimates.csv`
7. `sipp/result/idea_scan/arpa400_source_decomposition_support.csv`
8. `sipp/result/idea_scan/arpa400_source_decomposition_cell_means.csv`
9. `sipp/result/idea_scan/arpa400_robustness_estimates.csv`
10. `sipp/result/idea_scan/arpa400_paper_binned_means.csv`

These allow deeper review of:

- mechanism decomposition;
- sample support;
- placebo thresholds;
- annual-FPL robustness;
- exact sensitivity rows.

## Optional Figures

Upload these if visual review is useful:

1. `sipp/result/idea_scan/arpa400_paper_bins_main.png`
2. `sipp/result/idea_scan/arpa400_paper_bins_lag_nonemployer.png`
3. `sipp/result/idea_scan/arpa400_paper_bins_lag_current_employer.png`
4. `sipp/result/idea_scan/arpa400_bandwidth_robustness_coefficients.png`

The figures are supporting evidence only. The regression tables carry the main claim.

## Current Locked Design

Primary sample:

- adults age 26-64;
- non-Medicare;
- reference years 2017-2023;
- monthly FPL 3.5-4.5;
- national SIPP person-months;
- N = 215,972 person-months;
- persons = 23,888;
- state clusters = 52.

Primary model:

- local linear difference-in-discontinuities;
- treatment coefficient: `above400 x post_year2021`;
- running variable: `monthly_fpl - 4.0`;
- threshold: 400% FPL;
- fixed effects: state, reference month, reference year;
- controls: age, sex, race/ethnicity, disability;
- inference: person-cluster and state-cluster standard errors.

Primary outcome:

- `uninsured`.

Mechanism outcomes:

- `market_or_subsidy`;
- `direct_purchase`;
- `source_employer_related`.

Mechanism sample:

- lagged non-employer person-months.

## Current Main Estimates

Primary estimate:

- uninsured coefficient: -0.0277;
- person SE: 0.0141;
- state SE: 0.0151;
- N: 215,972.

Mechanism estimate in lagged non-employer sample:

- `market_or_subsidy` coefficient: +0.0739;
- person SE: 0.0328;
- state SE: 0.0350;
- N: 71,638.

Interpretation:

- main outcome: local uninsured reduction near 400% FPL;
- mechanism: direct-market/subsidy response is clearest among adults not coming from employer coverage;
- full sample does not support a pure Marketplace-channel claim.

## Current Robustness

Strong:

- main uninsured estimate is negative in 5/5 bandwidth specifications;
- lagged non-employer `market_or_subsidy` estimate is positive in 5/5 bandwidth specifications;
- pre-ARPA fake-policy tests at 400% FPL are near zero.

Weak or conditional:

- annual-FPL mechanism evidence is weak;
- placebo thresholds are not empty;
- employer-related source coverage rises in the full sample;
- older-adult heterogeneity is not strong enough for a headline.

## Ask Web GPT These Questions

Use this prompt:

```text
You are reviewing a SIPP-based health economics paper idea.

Read the uploaded ARPA 400% FPL files. The working question is whether ARPA's removal of the ACA Marketplace 400% FPL subsidy cliff reduced uninsurance near the threshold, using a national SIPP person-month difference-in-discontinuities design for 2017-2023.

Please evaluate:

1. Is the literature gap stated narrowly and defensibly?
2. Is the difference-in-discontinuities design credible enough for a health economics paper?
3. What are the most serious identification threats?
4. Are the placebo-threshold and annual-FPL concerns fatal, or manageable with transparent framing?
5. Is the mechanism evidence from lagged non-employer months persuasive?
6. What exact claims should the paper make and avoid?
7. What additional robustness check would most improve credibility without p-hacking?
8. How should the introduction and contribution paragraph be rewritten for a top-field health economics audience?

Do not treat this as a clean RDD. Do not claim the paper estimates the 2026 expiration effect. Focus on whether this is a conditional-go empirical paper and how to strengthen it honestly.
```

## One-File Fallback

If Web GPT can accept only one file, upload:

- `sipp/report/92_arpa_400fpl_paper_section_draft.md`

If it can accept two files, upload:

- `sipp/report/92_arpa_400fpl_paper_section_draft.md`
- `sipp/result/idea_scan/arpa400_paper_design_table.csv`

If it can accept five files, use the minimum upload set above.

## Do Not Ask Web GPT To Do This Yet

Do not ask it to:

- rerun models;
- inspect the full parquet;
- design a new topic from scratch;
- claim an unconditional go;
- write a final manuscript conclusion;
- ignore the annual-FPL and placebo concerns.

The best use of Web GPT now is critique and framing, not data processing.
