# Family Glitch and STLDI Fast Test

## Question

Can current SIPP support a new adult, non-child, non-unwinding health-insurance paper using either:

1. the 2023 ACA family-glitch fix; or
2. state regulatory heterogeneity around the 2018 federal short-term limited-duration insurance
   expansion?

## Source Checks

- Federal Register final rule, Affordability of Employer Coverage for Family Members of Employees: https://www.federalregister.gov/documents/2022/10/13/2022-22184/affordability-of-employer-coverage-for-family-members-of-employees
- CMS family glitch technical assistance PDF: https://www.cms.gov/marketplace/technical-assistance-resources/afford-employer-coverage-fixing-family-glitch.pdf
- Commonwealth Fund short-term plan state regulation issue brief: https://www.commonwealthfund.org/publications/issue-briefs/2019/may/states-step-up-protect-markets-consumers-short-term-plans
- Federal Register 2018 short-term limited-duration insurance final rule: https://www.federalregister.gov/documents/2018/08/03/2018-16568/short-term-limited-duration-insurance
- KFF short-term plan availability summary: https://www.kff.org/patient-consumer-protections/examining-short-term-limited-duration-health-plans-on-the-eve-of-aca-marketplace-open-enrollment/

## Data Construction

- Source parquet: `data/analysis_ready/sipp_2018_2024_person_month_panel.parquet`.
- Unit: person-year collapsed from monthly rows.
- Family exposure is proxied from SIPP household/family structure, not from employer premium
  contributions.
- STLDI protective states are coded from Commonwealth/KFF summaries as states with bans or
  very restrictive/no-availability regimes.

## Family Glitch Fix

Design:

- Sample: adults age 26-64, 138-600% FPL, 2019-2023.
- Exposure: family-exposed adult in a multi-person family with spouse link or children.
- Treatment: `family_exposed x 2023`.
- Fixed effects: state-year and state-family.
- Family-year FE are intentionally not included because the treatment is a national 2023 family
  exposure shock and would be collinear with family-year indicators.

Support:

- Person-years: 57,935.
- Persons: 38,834.
- Family-exposed person-years: 38,908.
- Active treated person-years in 2023: 6,129.

Estimates:

- `direct_market`: +0.0159, se 0.0095, t 1.67.
- `exchange_subsidy`: +0.0214, se 0.0089, t 2.41.
- `uninsured`: +0.0142, se 0.0094, t 1.51.
- `any_coverage`: -0.0142, se 0.0094, t -1.51.
- `private`: +0.0025, se 0.0121, t 0.21.
- `oop_any`: -0.0060, se 0.0137, t -0.44.
- `doctor_any`: +0.0192, se 0.0129, t 1.49.

Same-person 2022 to 2023 first-difference check:

All observed persons:

- `direct_market`: +0.0279, se 0.0190, t 1.46; n=3,761.
- `exchange_subsidy`: +0.0228, se 0.0177, t 1.28; n=3,761.
- `uninsured`: -0.0031, se 0.0141, t -0.22; n=3,761.
- `any_coverage`: +0.0031, se 0.0141, t 0.22; n=3,761.
- `private`: +0.0138, se 0.0170, t 0.81; n=3,761.

Baseline employer-like private sample:

- `direct_market`: +0.0018, se 0.0156, t 0.12; n=2,445.
- `exchange_subsidy`: +0.0004, se 0.0133, t 0.03; n=2,445.
- `uninsured`: -0.0155, se 0.0111, t -1.40; n=2,445.
- `any_coverage`: +0.0155, se 0.0111, t 1.40; n=2,445.
- `private`: +0.0477, se 0.0156, t 3.05; n=2,445.

Key limitation:

- The compact SIPP parquet does not observe employer offer, family premium contribution, employee-only
  premium contribution, or whether family employer coverage is unaffordable. The treatment is a
  family-exposure proxy, not actual family-glitch eligibility.

## Short-Term Limited-Duration Insurance

Design:

- Sample: adults age 26-64, 200-800% FPL, 2017-2021.
- Target group: healthy adults age 26-44 with 300-800% FPL.
- Treatment: permissive STLDI state x target group x post-2019.
- Fixed effects: state-year, state-target, target-year.

Support:

- Person-years: 72,394.
- Persons: 45,675.
- Permissive-state target person-years: 10,333.
- Active treated person-years: 5,824.

Estimates:

- `direct_market`: -0.0053, se 0.0120, t -0.44.
- `exchange_subsidy`: -0.0094, se 0.0103, t -0.92.
- `uninsured`: +0.0074, se 0.0114, t 0.65.
- `any_coverage`: -0.0074, se 0.0114, t -0.65.
- `private`: +0.0073, se 0.0140, t 0.52.
- `oop_any`: -0.0281, se 0.0198, t -1.42.

Key limitation:

- SIPP does not separately identify STLDI enrollment. Survey respondents may report STLDI as private
  direct-purchase coverage, as other private coverage, or not distinguish it from ACA-compliant nongroup
  coverage. Thus this is an indirect market-segmentation test.

## Verdict

`FAMILY-GLITCH-DIRECTIONAL-SIGNAL`

A clean GO would require:

- Family glitch: a clear 2023 jump in direct-market or exchange/subsidized coverage among
  family-exposed adults, without offsetting uninsured increases and without earlier event movement.
- STLDI: a clear post-2019 shift away from exchange/subsidized ACA coverage, or into direct/off-
  marketplace private coverage, among healthy young higher-income adults in permissive states.

## Artifacts

- `script/11_idea_scan/13_family_glitch_stldi_fast_test.py`
- `result/idea_scan/family_glitch_stldi_person_year_panel.parquet`
- `result/idea_scan/family_glitch_stldi_support.csv`
- `result/idea_scan/family_glitch_stldi_estimates.csv`
- `result/idea_scan/family_glitch_stldi_event.csv`
- `result/idea_scan/family_glitch_transition_estimates.csv`
