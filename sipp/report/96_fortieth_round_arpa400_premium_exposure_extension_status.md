# Fortieth Round Decision: ARPA400 Premium-Exposure Extension Status

## Verdict

`PREMIUM-EXPOSURE EXTENSION ALREADY TESTED; DO NOT USE AS UPGRADE CLAIM`

The natural next extension for the ARPA 400% FPL paper is premium-exposure heterogeneity: the removed cliff should matter more where unsubsidized benchmark premiums are high, especially for older adults. Existing project outputs show that this extension has already been partially tested.

Relevant artifacts:

- `sipp/report/58_arpa_400fpl_premium_gradient_test.md`
- `sipp/report/59_twentysecond_round_arpa_400fpl_premium_gradient_decision.md`
- `sipp/result/idea_scan/arpa400_premium_gradient_estimates.csv`
- `sipp/result/idea_scan/arpa400_premium_gradient_support.csv`
- `sipp/script/11_idea_scan/28_arpa_400fpl_premium_gradient_test.py`

## Tested Design

The prior premium-gradient test used:

- adult person-months;
- ages 26-64;
- non-Medicare;
- 350-450% monthly FPL;
- 2018-2023;
- states covered by CMS Exchange PUF premium files;
- state, year, and month fixed effects;
- state-clustered standard errors.

The key terms were:

- `above400 x post x high-premium state`;
- `above400 x post x continuous excess age-60 premium burden`;
- `above400 x post x age 50-64`;
- `above400 x post x high-premium state x age 50-64`.

## Findings

Binary high-premium interaction:

- `uninsured`: -0.0014, state-clustered t = -0.07.
- `market_or_subsidy`: -0.0178, state-clustered t = -0.68.

This does not support a clean high-premium mechanism.

Continuous premium-burden interaction:

- `uninsured`: -0.0146, state-clustered t = -2.08.
- `any_coverage`: +0.0146, state-clustered t = 2.08.
- `private`: +0.0187, state-clustered t = 1.92.

This is the one supportive coverage-gradient signal, but the direct-market channel is not clean:

- `market_or_subsidy`: -0.0073, state-clustered t = -0.67.
- `direct_purchase`: -0.0072, state-clustered t = -0.65.

Older-age interaction:

- `uninsured`: -0.0142, state-clustered t = -0.65.
- `market_or_subsidy`: -0.0116, state-clustered t = -0.68.

This does not support an older-adult headline.

High-premium older-adult quadruple:

- `uninsured`: +0.0740, state-clustered t = 1.81.
- `any_coverage`: -0.0740, state-clustered t = -1.81.
- `market_or_subsidy`: +0.0177, state-clustered t = 0.54.

This moves against the cleanest premium-cliff mechanism.

## Interpretation

The premium-exposure evidence should not be used to upgrade the paper to a clean Marketplace premium-cliff mechanism.

It should be used as:

1. a diagnostic showing why the mechanism claim must stay narrow;
2. an appendix robustness section;
3. motivation for a future improved premium-linkage pass if cleaner rating-area premium data can be linked.

The locked paper should continue to state:

> The strongest evidence is a local uninsured reduction near 400% FPL, with direct-market/subsidy mechanism evidence concentrated among lagged non-employer adults. However, high-premium and older-adult gradients do not cleanly validate a premium-exposure mechanism.

## Decision For Manuscript Package

Do not add premium-gradient estimates to the headline table.

Do add a short mechanism-risk paragraph:

- high-premium binary interactions are not supportive;
- continuous premium burden gives a supportive uninsured gradient but not a direct-market gradient;
- older adults do not drive the result;
- high-premium older adults move in the wrong direction on uninsurance.

## Next If More Empirical Work Is Run

Only rerun premium-exposure work if a cleaner exposure variable is built, such as:

- rating-area-level second-lowest-cost silver premium by age;
- state-year and age-specific benchmark premium divided by income at 400% FPL;
- pre-ARPA premium burden averaged over 2019-2020;
- linkage that preserves both FFM and state-based Marketplace states.

This should be labeled as a new pre-specified extension, not a search for significance.
