# Family Glitch Premium-Burden Refinement Test

## Question

Can the 2023 ACA family-glitch fix be tested more credibly in SIPP by focusing on family-exposed adults who had employer-related private coverage, paid comprehensive health-insurance premiums, and had high baseline premium burden before the 2023 rule change?

## Source Checks

- Federal Register final rule: https://www.federalregister.gov/documents/2022/10/13/2022-22184/affordability-of-employer-coverage-for-family-members-of-employees
- CMS technical assistance PDF: https://www.cms.gov/marketplace/technical-assistance-resources/afford-employer-coverage-fixing-family-glitch.pdf

The final rule changed affordability testing for family members so that family-member PTC eligibility depends on the employee share of the cost of covering the employee and family members, not self-only employee coverage. CMS technical assistance describes the case where self-only coverage can remain affordable for the employee while family coverage is unaffordable for family members.

## Construction

- Base panel: `data/analysis_ready/sipp_2018_2024_person_month_panel.parquet`.
- Raw private-source supplement: `temp/scratch/cobra_source_job_vars_2018_2024.parquet`.
- New raw premium supplement: `temp/scratch/family_glitch_premium_vars_2018_2024.parquet`.
- Baseline at-risk sample: adults 26-64, 138-600% FPL, family-exposed, employer-related private coverage, no direct-market/exchange coverage, positive comprehensive premium payment.
- High burden: baseline `THIPAYC / (12 x THTOTINC) > 9.12%`.
- Design: transition DDD using baseline years 2019-2022; key term is `high premium burden x 2022->2023 transition`.

Measurement caveat: `THIPAYC` is household premium payment, not the exact employee share for self-only versus family coverage. This is a mechanism-focused refinement, not direct statutory eligibility.

## Support

- Actual 2022->2023 high-burden at-risk pairs at 9.12% cutoff: 74 pairs, 74 persons.

| sample | high_col | actual_2022_2023 | high | pairs | persons | states | mean_premium_burden |
|---|---|---|---|---|---|---|---|
| baseline_family_employer_premium_atrisk | premium_gt_0912 | 0 | 0 | 3684 | 3182 | 44 | 0.0280 |
| baseline_family_employer_premium_atrisk | premium_gt_0912 | 0 | 1 | 373 | 355 | 38 | 0.1445 |
| baseline_family_employer_premium_atrisk | premium_gt_0912 | 1 | 0 | 1079 | 1079 | 42 | 0.0266 |
| baseline_family_employer_premium_atrisk | premium_gt_0912 | 1 | 1 | 74 | 74 | 30 | 0.1427 |
| baseline_family_employer_premium_atrisk | premium_gt_05 | 0 | 0 | 2957 | 2608 | 44 | 0.0189 |
| baseline_family_employer_premium_atrisk | premium_gt_05 | 0 | 1 | 1100 | 1001 | 42 | 0.0921 |
| baseline_family_employer_premium_atrisk | premium_gt_05 | 1 | 0 | 888 | 888 | 40 | 0.0181 |
| baseline_family_employer_premium_atrisk | premium_gt_05 | 1 | 1 | 265 | 265 | 38 | 0.0854 |
| paid_for_family_or_others | premium_gt_0912 | 0 | 0 | 2056 | 1810 | 44 | 0.0325 |
| paid_for_family_or_others | premium_gt_0912 | 0 | 1 | 269 | 258 | 36 | 0.1462 |
| paid_for_family_or_others | premium_gt_0912 | 1 | 0 | 573 | 573 | 41 | 0.0317 |
| paid_for_family_or_others | premium_gt_0912 | 1 | 1 | 56 | 56 | 25 | 0.1535 |
| paid_for_family_or_others | premium_gt_05 | 0 | 0 | 1526 | 1375 | 43 | 0.0211 |
| paid_for_family_or_others | premium_gt_05 | 0 | 1 | 799 | 729 | 41 | 0.0925 |
| paid_for_family_or_others | premium_gt_05 | 1 | 0 | 435 | 435 | 39 | 0.0209 |
| paid_for_family_or_others | premium_gt_05 | 1 | 1 | 194 | 194 | 36 | 0.0873 |
| premium_gt_0912_only | premium_gt_0912 | 0 | 0 | 0 | 0 | 0 | nan |
| premium_gt_0912_only | premium_gt_0912 | 0 | 1 | 373 | 355 | 38 | 0.1445 |
| premium_gt_0912_only | premium_gt_0912 | 1 | 0 | 0 | 0 | 0 | nan |
| premium_gt_0912_only | premium_gt_0912 | 1 | 1 | 74 | 74 | 30 | 0.1427 |
| premium_gt_0912_only | premium_gt_05 | 0 | 0 | 0 | 0 | 0 | nan |
| premium_gt_0912_only | premium_gt_05 | 0 | 1 | 373 | 355 | 38 | 0.1445 |
| premium_gt_0912_only | premium_gt_05 | 1 | 0 | 0 | 0 | 0 | nan |
| premium_gt_0912_only | premium_gt_05 | 1 | 1 | 74 | 74 | 30 | 0.1427 |

## Raw Transition Means

Main at-risk sample. Outcomes are post-year minus baseline-year coverage shares.

| high_col | actual_2022_2023 | high | pairs | persons | d_direct_market | d_exchange_subsidy | d_uninsured | d_private | d_employer_related_private |
|---|---|---|---|---|---|---|---|---|---|
| premium_gt_0912 | 0 | 0 | 3684 | 3182 | 0.0476 | 0.0328 | 0.0176 | -0.0307 | -0.0696 |
| premium_gt_0912 | 0 | 1 | 373 | 355 | 0.0694 | 0.0434 | 0.0418 | -0.0652 | -0.1272 |
| premium_gt_0912 | 1 | 0 | 1079 | 1079 | 0.0429 | 0.0343 | 0.0270 | -0.0342 | -0.0694 |
| premium_gt_0912 | 1 | 1 | 74 | 74 | 0.0732 | 0.0210 | 0.0068 | -0.0068 | -0.0578 |
| premium_gt_05 | 0 | 0 | 2957 | 2608 | 0.0506 | 0.0352 | 0.0182 | -0.0308 | -0.0729 |
| premium_gt_05 | 0 | 1 | 1100 | 1001 | 0.0469 | 0.0297 | 0.0242 | -0.0420 | -0.0801 |
| premium_gt_05 | 1 | 0 | 888 | 888 | 0.0447 | 0.0367 | 0.0308 | -0.0402 | -0.0750 |
| premium_gt_05 | 1 | 1 | 265 | 265 | 0.0442 | 0.0228 | 0.0089 | -0.0066 | -0.0474 |

## Transition-DDD Estimates

Main at-risk sample, high burden > 9.12%:

- Direct-market coverage: +0.0203 (person-cluster se 0.0359, t 0.56; actual high-burden pairs 74).
- Exchange/subsidy proxy: -0.0114 (person-cluster se 0.0245, t -0.47; actual high-burden pairs 74).
- Uninsured: -0.0432 (person-cluster se 0.0149, t -2.90; actual high-burden pairs 74).
- Any coverage: +0.0432 (person-cluster se 0.0149, t 2.90; actual high-burden pairs 74).
- Private coverage: +0.0577 (person-cluster se 0.0175, t 3.31; actual high-burden pairs 74).
- Employer-related private: +0.0603 (person-cluster se 0.0346, t 1.74; actual high-burden pairs 74).

Main at-risk sample, high burden > 5% sensitivity:

- Direct-market coverage: +0.0093 (person-cluster se 0.0166, t 0.56; actual high-burden pairs 265).
- Exchange/subsidy proxy: -0.0011 (person-cluster se 0.0134, t -0.08; actual high-burden pairs 265).
- Uninsured: -0.0243 (person-cluster se 0.0111, t -2.18; actual high-burden pairs 265).
- Private coverage: +0.0396 (person-cluster se 0.0126, t 3.13; actual high-burden pairs 265).

## Decision

`FAMILY GLITCH PREMIUM-BURDEN REFINEMENT: NO-GO`.

A clean paper needs a positive direct-market / exchange transition concentrated in high-premium-burden family-employer baseline households in 2022->2023, with no similar placebo transition in earlier pairs and no rise in uninsurance. This screen is the closest current SIPP can get without actual employer offer and family premium eligibility fields.

## Artifacts

- `script/11_idea_scan/38_family_glitch_premium_burden_test.py`
- `report/76_family_glitch_premium_burden_test.md`
- `result/idea_scan/family_glitch_premium_person_year_panel.parquet`
- `result/idea_scan/family_glitch_premium_transition_pairs.parquet`
- `result/idea_scan/family_glitch_premium_support.csv`
- `result/idea_scan/family_glitch_premium_raw_cells.csv`
- `result/idea_scan/family_glitch_premium_estimates.csv`
