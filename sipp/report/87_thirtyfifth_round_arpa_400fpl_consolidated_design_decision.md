# Thirty-Fifth Round Decision: ARPA 400% FPL Consolidated Design

## Verdict

`ARPA 400% FPL IS THE CURRENT LEAD IDEA; CONDITIONAL GO`

The idea has now passed the current idea-screen threshold:

- current policy relevance is strong;
- the treatment threshold is real and national;
- sample support is large;
- main uninsured effect is stable across bandwidths;
- lagged non-employer mechanism supports a direct-market affordability channel;
- pre-ARPA fake-policy tests do not reproduce the result.

It is still conditional because:

- annual-FPL mechanism is weak;
- nearby placebo thresholds are not empty;
- employer-related coverage rises in the broad sample;
- older-adult gradient is not supportive.

## Locked Design for Next Stage

Primary design:

- sample: age 26-64, non-Medicare, 350-450% monthly FPL;
- unit: person-month;
- treatment contrast: above 400% FPL x post-2021;
- model: local linear difference-in-discontinuities with state, year, and month FE;
- primary outcome: uninsured;
- primary inference: person-cluster and state-cluster standard errors.

Secondary mechanism design:

- sample: lagged non-employer person-months;
- outcomes: market/subsidy proxy, direct purchase, employer-related source;
- purpose: mechanism, not main causal estimand.

## Current Main Claim

The defensible claim is:

`ARPA's removal of the 400% FPL subsidy cliff is associated with a local reduction in uninsurance near the threshold in SIPP. The most credible mechanism evidence appears among adults not coming from employer-related coverage, where direct-market / subsidy proxies rise substantially.`

## Not Yet Defensible

Do not yet claim:

- clean Marketplace enrollment gains in the full sample;
- older adults drive the response;
- annual-FPL and monthly-FPL designs are fully consistent;
- placebo thresholds are empty;
- this is a final causal paper without a fuller identification writeup.

## Next Step

Write the empirical-design section and source/literature-gap memo before running more model variants.
