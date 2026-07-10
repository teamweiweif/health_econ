# Family Glitch Current Decision

## Verdict

`NO-GO AS MAIN SIPP IDEA; RETAIN ONLY AS DIAGNOSTIC / FUTURE DATA TOPIC`

The 2023 ACA family-glitch fix is a real and policy-relevant federal rule change, but the current SIPP evidence does not support it as a main paper idea.

## Policy Hook

The policy is real:

- Federal Register final rule: https://www.federalregister.gov/documents/2022/10/13/2022-22184/affordability-of-employer-coverage-for-family-members-of-employees
- CMS family glitch technical assistance: https://www.cms.gov/marketplace/technical-assistance-resources/afford-employer-coverage-fixing-family-glitch.pdf
- KFF family glitch explainer: https://www.kff.org/affordable-care-act/issue-brief/fixing-the-family-glitch-and-what-it-means-for-family-coverage/

Policy logic:

- Before 2023, family members could be blocked from Marketplace premium tax credits if the employee's self-only employer coverage was affordable, even when family coverage was unaffordable.
- The final rule changed the affordability test for family members so that family-member eligibility considers the cost of covering the employee and family members.
- This is conceptually attractive for SIPP because it is a federal timing shock with direct-market / exchange / uninsured outcomes.

## Local Evidence Reviewed

Existing artifacts:

- `sipp/report/28_family_glitch_stldi_fast_test.md`
- `sipp/report/76_family_glitch_premium_burden_test.md`
- `sipp/result/idea_scan/family_glitch_stldi_estimates.csv`
- `sipp/result/idea_scan/family_glitch_transition_estimates.csv`
- `sipp/result/idea_scan/family_glitch_premium_estimates.csv`
- `sipp/result/idea_scan/family_glitch_premium_support.csv`

## First-Pass Family Exposure Test

The first-pass person-year screen used:

- adults age 26-64;
- 138-600% FPL;
- 2019-2023;
- family-exposed adults in multi-person families with spouse links or children;
- treatment: `family_exposed x 2023`.

Support:

- 57,935 person-years;
- 38,834 persons;
- 6,129 active treated person-years in 2023.

Main estimates:

- `direct_market`: +0.0159, t 1.67.
- `exchange_subsidy`: +0.0214, t 2.41.
- `uninsured`: +0.0142, t 1.51.
- `any_coverage`: -0.0142, t -1.51.

Interpretation:

- There is a directional direct-market/exchange signal.
- But uninsurance also rises, and exposure is a broad family-structure proxy rather than statutory family-glitch eligibility.
- This is not clean enough for a main causal paper.

## Premium-Burden Refinement

The refinement tried to get closer to actual statutory exposure:

- adults age 26-64;
- 138-600% FPL;
- family-exposed;
- employer-related private coverage at baseline;
- no direct-market/exchange coverage at baseline;
- positive comprehensive premium payment;
- high premium burden threshold based on household premium payment divided by income.

Critical support problem:

- Actual 2022->2023 high-burden at-risk pairs at the 9.12% cutoff: **74 pairs, 74 persons**.

Main at-risk sample, high burden > 9.12%:

- Direct-market coverage: +0.0203, person-cluster t 0.56.
- Exchange/subsidy proxy: -0.0114, person-cluster t -0.47.
- Uninsured: -0.0432, person-cluster t -2.90.
- Private coverage: +0.0577, person-cluster t 3.31.
- Employer-related private: +0.0603, person-cluster t 1.74.

Sensitivity high burden > 5%:

- Direct-market coverage: +0.0093, person-cluster t 0.56.
- Exchange/subsidy proxy: -0.0011, person-cluster t -0.08.
- Uninsured: -0.0243, person-cluster t -2.18.
- Private coverage: +0.0396, person-cluster t 3.13.

Interpretation:

- The closest at-risk design does not show the required direct-market or exchange/subsidy transition.
- The coverage gain appears more like broad/private/employer-related movement.
- The sample most aligned with the statutory mechanism is too small.

## Measurement Blocker

Current SIPP does not cleanly observe:

- employer offer to the family member;
- employee-only premium contribution;
- family premium contribution for offered ESI;
- whether the family offer is unaffordable under the statutory rule;
- whether Marketplace subsidy eligibility changed specifically because of the family-glitch fix.

SIPP has useful proxies:

- family structure;
- employer-related source coverage;
- direct-market and exchange/subsidy proxies;
- household premium payments.

But these are not enough for a clean top-field causal design.

## Decision

Do not promote family glitch as a main SIPP idea.

Use it only as:

1. a discarded-but-documented diagnostic;
2. a future-data idea if better employer offer and family premium contribution variables become available;
3. a short note in the idea portfolio showing that the policy was considered and failed on data support/mechanism.

## Updated Ranking Impact

Current main idea remains:

1. ARPA 400% FPL subsidy-cliff removal: `CONDITIONAL GO / CURRENT LEAD`.

Family glitch should rank below:

- ARPA100-150 non-expansion zero-premium margin, because that idea at least has substantial low-income policy group support even though it is weak as a quasi-experiment.

Recommended label:

`Family glitch: NO-GO with current SIPP; future data topic.`
