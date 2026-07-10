# ARPA 400% FPL Premium/Age Gradient Test

## Purpose

This test asks whether the ARPA near-400% FPL response is stronger where the subsidy-cliff mechanism
should be strongest: high gross benchmark-premium states and older adults. It uses the augmented
SIPP panel with `RPRITYPE1` employer coverage and the existing CMS Exchange PUF state-year premium
policy file.

## Design

- Unit: person-month.
- Sample: age 26-64, non-Medicare, 350-450% monthly FPL, 2018-2023.
- Geography: states covered by CMS Exchange PUF premium files.
- Premium exposure: pre-2021 state age-60 SLCSP burden above 8.5% of 400% FPL income.
- Main term: above 400% FPL x post-2021 x high pre-premium-burden state.
- Additional tests: continuous premium burden, older age, and high-premium x older-age quadruple.
- FE: year, month, and state.
- SE: state-clustered.

## Support

| post | above400 | highpremium | person_months | persons | states | uninsured | employer_private | direct_purchase | marketplace_flag |
|---|---|---|---|---|---|---|---|---|---|
| 0.0000 | 0.0000 | 0.0000 | 21349.0000 | 3208.0000 | 19.0000 | 0.1168 | 0.6810 | 0.0789 | 0.0515 |
| 0.0000 | 0.0000 | 1.0000 | 17945.0000 | 2595.0000 | 20.0000 | 0.1053 | 0.6289 | 0.0864 | 0.0567 |
| 0.0000 | 1.0000 | 0.0000 | 19340.0000 | 2936.0000 | 19.0000 | 0.0955 | 0.6993 | 0.0612 | 0.0431 |
| 0.0000 | 1.0000 | 1.0000 | 15355.0000 | 2344.0000 | 20.0000 | 0.1062 | 0.6337 | 0.0829 | 0.0541 |
| 1.0000 | 0.0000 | 0.0000 | 14676.0000 | 2322.0000 | 19.0000 | 0.1114 | 0.6868 | 0.0840 | 0.0633 |
| 1.0000 | 0.0000 | 1.0000 | 12023.0000 | 1909.0000 | 20.0000 | 0.1135 | 0.5674 | 0.1243 | 0.0962 |
| 1.0000 | 1.0000 | 0.0000 | 12703.0000 | 2077.0000 | 19.0000 | 0.0787 | 0.7338 | 0.0842 | 0.0591 |
| 1.0000 | 1.0000 | 1.0000 | 10111.0000 | 1700.0000 | 20.0000 | 0.0989 | 0.6278 | 0.1001 | 0.0754 |

## Estimates

Binary high-premium gradient:

- `uninsured`: -0.0014, state-clustered se 0.0208, t -0.07.
- `any_coverage`: +0.0014, state-clustered se 0.0208, t 0.07.
- `employer_private`: +0.0105, state-clustered se 0.0431, t 0.24.
- `direct_purchase`: -0.0159, state-clustered se 0.0265, t -0.60.
- `marketplace_flag`: -0.0070, state-clustered se 0.0202, t -0.35.
- `market_or_subsidy`: -0.0178, state-clustered se 0.0263, t -0.68.
- `private`: +0.0142, state-clustered se 0.0295, t 0.48.

Continuous excess-premium gradient:

- `uninsured`: -0.0146, state-clustered se 0.0070, t -2.08.
- `any_coverage`: +0.0146, state-clustered se 0.0070, t 2.08.
- `employer_private`: +0.0168, state-clustered se 0.0129, t 1.30.
- `direct_purchase`: -0.0072, state-clustered se 0.0111, t -0.65.
- `marketplace_flag`: -0.0070, state-clustered se 0.0108, t -0.65.
- `market_or_subsidy`: -0.0073, state-clustered se 0.0110, t -0.67.
- `private`: +0.0187, state-clustered se 0.0098, t 1.92.

Older-age gradient:

- `uninsured`: -0.0142, state-clustered se 0.0219, t -0.65.
- `any_coverage`: +0.0142, state-clustered se 0.0219, t 0.65.
- `employer_private`: +0.0146, state-clustered se 0.0287, t 0.51.
- `direct_purchase`: -0.0108, state-clustered se 0.0170, t -0.64.
- `marketplace_flag`: -0.0096, state-clustered se 0.0202, t -0.48.
- `market_or_subsidy`: -0.0116, state-clustered se 0.0170, t -0.68.
- `private`: +0.0281, state-clustered se 0.0299, t 0.94.

High-premium x older-age quadruple interaction:

- `uninsured`: +0.0740, state-clustered se 0.0409, t 1.81.
- `any_coverage`: -0.0740, state-clustered se 0.0409, t -1.81.
- `employer_private`: -0.0874, state-clustered se 0.0532, t -1.64.
- `direct_purchase`: +0.0243, state-clustered se 0.0324, t 0.75.
- `marketplace_flag`: -0.0312, state-clustered se 0.0431, t -0.72.
- `market_or_subsidy`: +0.0177, state-clustered se 0.0327, t 0.54.
- `private`: -0.0882, state-clustered se 0.0571, t -1.55.

## Interpretation

A clean subsidy-cliff mechanism would predict lower uninsured and stronger Marketplace/direct
purchase gains in high-premium states and among older adults. If the high-premium interaction raises
Marketplace proxies but also raises uninsured, or if older adults do not respond, the current lead
should remain a policy-relevant private-coverage threshold response rather than a clean premium
cliff paper.

## Artifacts

- `script/11_idea_scan/28_arpa_400fpl_premium_gradient_test.py`
- `result/idea_scan/arpa400_premium_gradient_estimates.csv`
- `result/idea_scan/arpa400_premium_gradient_support.csv`
