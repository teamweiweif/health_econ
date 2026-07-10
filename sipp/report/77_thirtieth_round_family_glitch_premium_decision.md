# Thirtieth Round Decision: Family Glitch Premium-Burden Refinement

## Question

Can the 2023 ACA family-glitch fix become a stronger SIPP idea if the sample is restricted to
family-exposed adults who had employer-related private coverage, paid comprehensive health-insurance
premiums, and had high baseline premium burden?

This was worth testing because the earlier family-glitch screen had a broad `family_exposed x 2023`
proxy. It produced a directional exchange/subsidy signal, but the exposure was too wide. The new
test asks whether the signal concentrates where the policy mechanism should be strongest.

## Source Check

- Federal Register final rule:
  https://www.federalregister.gov/documents/2022/10/13/2022-22184/affordability-of-employer-coverage-for-family-members-of-employees
- CMS family-glitch technical assistance:
  https://www.cms.gov/marketplace/technical-assistance-resources/afford-employer-coverage-fixing-family-glitch.pdf

The policy rule is real and relevant: beginning with 2023 coverage, affordability for family members
is based on the employee share of family coverage, not only self-only employee coverage.

## What Was Added

New script:

- `script/11_idea_scan/38_family_glitch_premium_burden_test.py`

New extracted raw variables:

- `THIPAYC`: comprehensive health-insurance premium payments.
- `EWHIPAYC`: who in the household the respondent paid premiums for.
- reused `EHEMPLY1/2` from the raw private-source supplement to identify employer-related coverage.

New outputs:

- `report/76_family_glitch_premium_burden_test.md`
- `result/idea_scan/family_glitch_premium_person_year_panel.parquet`
- `result/idea_scan/family_glitch_premium_transition_pairs.parquet`
- `result/idea_scan/family_glitch_premium_support.csv`
- `result/idea_scan/family_glitch_premium_raw_cells.csv`
- `result/idea_scan/family_glitch_premium_estimates.csv`

## Design

Unit:

- person transition pair: baseline year to following year.

Transition years:

- placebo transitions: 2019->2020, 2020->2021, 2021->2022.
- policy transition: 2022->2023.

Main baseline sample:

- adults age 26-64;
- 138-600% FPL;
- family-exposed;
- employer-related private coverage in baseline year;
- no baseline direct-market / exchange coverage;
- positive comprehensive premium payment;
- observed in both baseline and following year.

Treatment contrast:

- high baseline premium burden x 2022->2023.

Primary high-burden cutoff:

- `THIPAYC / (12 x THTOTINC) > 9.12%`.

Sensitivity cutoff:

- premium burden > 5%.

## Support

The support check is the first major problem.

At the statutory-style 9.12% cutoff:

- 2022->2023 actual high-burden pairs: 74.
- actual high-burden persons: 74.

At the looser 5% cutoff:

- 2022->2023 actual high-burden pairs: 265.
- actual high-burden persons: 265.

The 9.12% group is too thin for a standalone top-field paper.

## Results

Main at-risk sample, high burden > 9.12%:

- Direct-market coverage: +0.0203, person-clustered t = 0.56.
- Exchange/subsidy proxy: -0.0114, t = -0.47.
- Uninsured: -0.0432, t = -2.90.
- Any coverage: +0.0432, t = 2.90.
- Private coverage: +0.0577, t = 3.31.
- Employer-related private coverage: +0.0603, t = 1.74.
- Current-employer private coverage: +0.1089, t = 2.34.

Main at-risk sample, high burden > 5%:

- Direct-market coverage: +0.0093, t = 0.56.
- Exchange/subsidy proxy: -0.0011, t = -0.08.
- Uninsured: -0.0243, t = -2.18.
- Private coverage: +0.0396, t = 3.13.
- Employer-related private coverage: +0.0260, t = 1.29.

## Interpretation

This refinement does not produce the family-glitch mechanism.

What the policy mechanism predicts:

- high family-premium-burden employer-coverage households should show a stronger 2023 shift into
  Marketplace / exchange / subsidized nongroup coverage.

What SIPP shows:

- direct-market movement is small and imprecise;
- exchange/subsidy does not rise;
- uninsured falls, but the offset is mainly private and current-employer coverage, not Marketplace;
- the clean statutory-style high-burden group has only 74 people in the policy transition.

This is a useful diagnostic because it shows the earlier broad family-glitch signal does not survive
when the sample is pushed toward the actual mechanism.

## Decision

`FAMILY GLITCH PREMIUM-BURDEN REFINEMENT: NO-GO AS MAIN SIPP PAPER`

The family-glitch topic should be downgraded from "conditional lead" to "not currently workable with
public SIPP alone."

It can still be mentioned as a discarded diagnostic:

- policy is excellent;
- SIPP has some premium-burden information;
- but SIPP lacks the key statutory eligibility variables, and the refined mechanism check fails to
show Marketplace uptake.

## Ranking Implication

This makes the current ordering cleaner:

1. **ARPA 400% FPL enhanced PTC / private-coverage response** remains the best current SIPP lead.
2. **Late Medicaid expansion 100-138% FPL bridge** remains the strongest Medicaid/uninsurance
   backup.
3. **ARPA UI / broader ARPA Marketplace affordability variants** remain useful extensions.
4. **Family glitch fix** is downgraded: policy gap strong, but SIPP mechanism support fails after
   premium-burden refinement.
5. **ARPA COBRA subsidy** remains no-go standalone.

## Next Move

Do not spend more time trying to rescue family glitch with public SIPP unless a new extract can
directly observe:

- employer offer;
- employee-only premium;
- family premium;
- employee versus family-member policyholder status;
- actual Marketplace PTC eligibility.

The strongest practical path remains a sharpened ARPA 400% FPL design with an explicitly narrow
non-employer or individual-market-at-risk sample.
