# Twenty-First-Round ARPA 400% FPL Diagnostic Decision

## Question

After adding employer coverage and RD diagnostics, is the ARPA 400% FPL idea still a credible
top-candidate causal design?

## Diagnostics Added

This round extends the prior ARPA 400% FPL work with:

- binned RD means around 400% monthly FPL;
- plot files for uninsured, employer-related private coverage, direct purchase, and Marketplace;
- year-specific local discontinuities at 400% FPL;
- age-gradient difference-in-discontinuities;
- a selected pre-period non-employer baseline robustness sample.

New outputs:

- `result/idea_scan/arpa400_rd_bins.csv`
- `result/idea_scan/arpa400_rd_bins_uninsured.png`
- `result/idea_scan/arpa400_rd_bins_employer_private.png`
- `result/idea_scan/arpa400_rd_bins_direct_purchase.png`
- `result/idea_scan/arpa400_rd_bins_marketplace_flag.png`
- `result/idea_scan/arpa400_yearly_discontinuities.csv`
- `result/idea_scan/arpa400_age_gradient_estimates.csv`
- `result/idea_scan/arpa400_pre_nonemployer_estimates.csv`
- `result/idea_scan/arpa400_diagnostics_support.csv`

## Visual RD Read

The binned plots do not show a clean, sharp 400% FPL cliff in the simple visual sense:

- uninsured declines smoothly with income both before and after ARPA;
- the post-ARPA uninsured curve is lower in parts of the near-threshold region, but not only at the
  cutoff;
- direct-purchase coverage is often higher post-ARPA, but the change is broad rather than a
  point-discontinuity only at 400% FPL;
- employer coverage is a strong smooth income gradient, not a clean post-ARPA jump only at the
  cutoff.

This does not kill the idea, but it changes the paper framing. The empirical object is not yet a
visually obvious RD-style cliff.

## Year-Specific Discontinuities

Within-year local discontinuities at 400% monthly FPL show mixed pre-period behavior:

Pre-ARPA:

- `uninsured`: +0.0107 in 2017, +0.0256 in 2018, -0.0106 in 2019, +0.0242 in 2020.
- `employer_private`: -0.0283 in 2017, -0.0310 in 2018, +0.0212 in 2019, -0.0235 in 2020.
- `direct_purchase`: +0.0187 in 2017, -0.0181 in 2018, +0.0004 in 2019, +0.0027 in 2020.
- `marketplace_flag`: +0.0204 in 2017, -0.0334 in 2018, +0.0091 in 2019, +0.0017 in 2020.

Post-ARPA:

- `uninsured`: -0.0143 in 2021, -0.0064 in 2022, -0.0135 in 2023.
- `employer_private`: +0.0074 in 2021, +0.0451 in 2022, -0.0033 in 2023.
- `direct_purchase`: -0.0029 in 2021, +0.0482 in 2022, +0.0179 in 2023.
- `marketplace_flag`: -0.0096 in 2021, +0.0422 in 2022, +0.0143 in 2023.

The strongest Marketplace/direct-purchase discontinuity is in 2022, not uniformly across 2021-2023.
This is consistent with ARPA implementation/enrollment dynamics, but it is not a clean one-time
threshold jump.

## Age Gradient

If the story were mainly gross premium relief above 400% FPL, the cleanest signal should plausibly
be strongest for older adults. The diagnostics do not show that:

- Ages 26-39:
  - `uninsured`: -0.0439, person-clustered t -1.76.
  - `employer_private`: +0.0426, t 1.39.
  - `market_or_subsidy`: +0.0190, t 0.97.
- Ages 40-49:
  - `uninsured`: -0.0077, t -0.31.
  - `direct_purchase`: +0.0572, t 2.10.
  - `marketplace_flag`: +0.0551, t 2.18.
  - `market_or_subsidy`: +0.0592, t 2.17.
- Ages 50-64:
  - `uninsured`: -0.0070, t -0.35.
  - `direct_purchase`: +0.0014, t 0.06.
  - `marketplace_flag`: -0.0050, t -0.24.
  - `market_or_subsidy`: -0.0012, t -0.05.

This weakens a clean "older/high-premium households above the cliff responded most" story.

## Pre-Period Non-Employer Baseline Robustness

I restricted to people with at least three pre-2021 near-threshold months and no pre-period employer
coverage. This is selected, so it cannot be the primary design, but it is a useful mechanism check.

Results:

- `uninsured`: -0.0445, person-clustered se 0.0571, t -0.78.
- `employer_private`: -0.0415, person-clustered se 0.0545, t -0.76.
- `direct_purchase`: +0.1150, person-clustered se 0.0727, t 1.58.
- `marketplace_flag`: +0.0888, person-clustered se 0.0699, t 1.27.
- `market_or_subsidy`: +0.1176, person-clustered se 0.0727, t 1.62.

This is directionally the cleanest mechanism check: among people without pre-period employer
coverage, Marketplace/direct-purchase responses are large and employer coverage does not explain the
effect. But the sample is much smaller: 43,681 person-months and 3,987 persons.

## Decision

`ARPA 400% FPL: KEEP AS FIRST LEAD, BUT REFRAME`

The strongest version is no longer:

> "ARPA's removal of the 400% FPL cliff sharply increased Marketplace enrollment above the cliff."

The better current framing is:

> "ARPA's enhanced PTC regime changed private coverage and uninsurance near the 400% FPL threshold,
> with strongest evidence for lower uninsurance and a mixed employer-vs-Marketplace mechanism."

This is still the best current candidate because:

- the main uninsured estimate is still large and policy-current;
- support is large;
- the non-employer baseline robustness moves in the right mechanism direction;
- the question is highly relevant after the 2025 expiration of enhanced PTCs.

But it is not ready for a paper outline until the next diagnostics pass answers:

- whether the 2022 Marketplace discontinuity is real or an artifact;
- why ages 50-64 do not show the strongest response;
- whether a credible non-employer or individual-market-at-risk baseline sample can be constructed;
- whether state/age premium intensity recovers the expected older-adult gradient.

## Updated Ranking

1. **ARPA enhanced PTC near 400% FPL / private coverage response**: best lead, but mechanism
   unresolved; no longer a clean pure-cliff story.
2. **SNAP Emergency Allotment termination**: best non-ACA/food-security lead.
3. **ACA enhanced PTC premium-intensity portfolio**: should now be folded into the ARPA 400% project
   as a mechanism/heterogeneity layer.
4. **ACA family glitch fix**: conceptually strong but current compact data lacks actual employer
   offer/premium eligibility.
5. **ACA state reinsurance waivers**: support good, first-stage weak.
6. **ARPA 100-150% FPL non-expansion Marketplace**: raw uptake direction, no clean uninsured DDD.

## New Artifacts

- `script/11_idea_scan/27_arpa_400fpl_rd_diagnostics.py`
- `report/56_arpa_400fpl_rd_diagnostics.md`
- `result/idea_scan/arpa400_rd_bins.csv`
- `result/idea_scan/arpa400_rd_bins_uninsured.png`
- `result/idea_scan/arpa400_rd_bins_employer_private.png`
- `result/idea_scan/arpa400_rd_bins_direct_purchase.png`
- `result/idea_scan/arpa400_rd_bins_marketplace_flag.png`
- `result/idea_scan/arpa400_yearly_discontinuities.csv`
- `result/idea_scan/arpa400_age_gradient_estimates.csv`
- `result/idea_scan/arpa400_pre_nonemployer_estimates.csv`
- `result/idea_scan/arpa400_diagnostics_support.csv`
