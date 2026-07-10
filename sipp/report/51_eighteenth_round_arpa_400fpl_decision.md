# Eighteenth-Round ARPA 400% FPL Cliff Decision

## Question

Did ARPA's temporary removal of the ACA Marketplace 400% FPL subsidy cliff reduce uninsurance among
near-threshold adults?

## Why This Is Now the Leading Candidate

This is the strongest new idea tested so far because it combines:

- a live 2026 policy question: the enhanced premium tax credits expired after 2025 and the 400% FPL
  cliff has returned;
- a federal threshold rule documented by CMS and IRS;
- a plausible top-field design: difference-in-discontinuities around 400% FPL before and after ARPA;
- large SIPP support around the threshold;
- a direct monthly outcome: uninsured / any coverage.

Unlike the single-state designs, this is not a small-cell problem. Unlike minimum wage or tax-credit
ideas, SIPP directly observes the main outcome.

## Source Checks

- CMS American Rescue Plan and the Marketplace:
  https://www.cms.gov/newsroom/fact-sheets/american-rescue-plan-and-marketplace
- IRS Premium Tax Credit eligibility:
  https://www.irs.gov/affordable-care-act/individuals-and-families/eligibility-for-the-premium-tax-credit
- KFF 2026 Marketplace enrollment / premiums / deductibles:
  https://www.kff.org/affordable-care-act/what-we-know-so-far-about-2026-aca-marketplace-enrollment-premiums-and-deductibles/
- KFF enhanced PTC expiration premium-payment analysis:
  https://www.kff.org/affordable-care-act/aca-marketplace-premium-payments-would-more-than-double-on-average-next-year-if-enhanced-premium-tax-credits-expire/

CMS states that before ARPA, households above 400% FPL were not eligible for Marketplace premium tax
credits. CMS also states that ARPA capped benchmark-plan premium contributions at 8.5% of household
income, addressing the above-400% FPL subsidy cliff. IRS confirms that ARPA temporarily eliminated
the rule barring PTC eligibility above 400% FPL for 2021 and 2022. KFF's 2026 analyses show why the
question is current again: the enhanced credits expired after 2025, above-400% FPL consumers again
face the cliff, and this group accounts for a large share of early Marketplace enrollment losses.

## Design Tested

Source:

- `data/analysis_ready/sipp_2018_2024_person_month_panel.parquet`

Unit:

- person-month, SIPP 2017-2023.

Primary running variable:

- `TFINCPOV`, family monthly income-to-poverty ratio.

Sensitivity running variable:

- `TFCYINCPOV`, family calendar-year income-to-poverty ratio.

Primary sample:

- age 26-64;
- non-Medicare months;
- 350-450% FPL.

Model:

- local linear difference-in-discontinuities;
- triangular kernel weights;
- year fixed effects;
- month fixed effects;
- state fixed effects;
- basic demographics;
- HC1 and person-clustered standard errors.

Treatment contrast:

- above 400% FPL x post-2021.

## Support

Main age 26-64, monthly FPL sample:

- 217,610 person-months.
- 23,755 persons.
- 52 states including DC.
- Minimum cell support: 5,562 persons.

Age 21-64 broader support sample:

- 241,512 person-months.
- 26,825 persons.

This is sufficient support for serious follow-up.

## Main Results

Primary age 26-64, monthly FPL, post = 2021-2023:

- `uninsured`: -0.0263, HC1 se 0.0072, t -3.67; person-clustered se 0.0143, t -1.84.
- `any_coverage`: +0.0263, HC1 se 0.0072, t 3.67; person-clustered se 0.0143, t 1.84.
- `direct_purchase`: +0.0222, HC1 se 0.0068, t 3.27; person-clustered se 0.0137, t 1.63.
- `marketplace_flag`: +0.0197, HC1 se 0.0061, t 3.22; person-clustered se 0.0123, t 1.61.
- `market_or_subsidy`: +0.0218, HC1 se 0.0068, t 3.20; person-clustered se 0.0137, t 1.59.
- `private`: +0.0237, HC1 se 0.0086, t 2.77; person-clustered se 0.0171, t 1.39.
- `public`: +0.0081, HC1 se 0.0064, t 1.27; person-clustered se 0.0132, t 0.62.
- `medicaid`: +0.0033, HC1 se 0.0058, t 0.57; person-clustered se 0.0117, t 0.28.

Broader age 21-64 monthly-FPL sample:

- `uninsured`: -0.0313, person-clustered se 0.0137, t -2.28.
- `direct_purchase`: +0.0218, person-clustered se 0.0132, t 1.66.
- `market_or_subsidy`: +0.0225, person-clustered se 0.0132, t 1.70.

Post-April-2021 timing:

- `uninsured`: -0.0296, person-clustered se 0.0147, t -2.01.
- `marketplace_flag`: +0.0270, person-clustered se 0.0127, t 2.12.

Annual-FPL sensitivity:

- `uninsured`: -0.0301, person-clustered se 0.0226, t -1.33.
- `direct_purchase`: -0.0243, person-clustered se 0.0230, t -1.06.
- `market_or_subsidy`: -0.0240, person-clustered se 0.0230, t -1.05.

## Interpretation

This is a real signal, but not paper-ready:

- the uninsured result is robust in sign across monthly-FPL, broader age window, post-April timing,
  and annual-FPL sensitivity;
- the main monthly-FPL model also shows positive direct-purchase / Marketplace proxy effects, which
  improves on the older screen;
- person-clustered inference is borderline in the primary age 26-64 model and stronger in the
  age 21-64 and post-April versions;
- annual-FPL sensitivity keeps the uninsured reduction but flips the Marketplace proxy negative;
- the 350% FPL placebo also shows a negative uninsured effect, suggesting the estimate may partly
  reflect broader ARPA subsidy-schedule changes below 400% FPL rather than only the cliff removal;
- the compact parquet lacks `RPRITYPE1`, so employer-sponsored private coverage substitution cannot
  be cleanly separated yet.

## Decision

`ARPA 400% FPL CLIFF: CURRENT BEST CONDITIONAL GO`

This should move above SNAP Emergency Allotment as the top current candidate, but it needs a formal
second-stage validation package before being treated as a clean paper.

The immediate next work should be:

- add `RPRITYPE1` employer-related private coverage back into the analysis-ready panel;
- produce year-specific/binned RD plots around 400% FPL for uninsured and direct purchase;
- test pre-ARPA discontinuity stability by year;
- test age-premium-gradient heterogeneity, especially ages 50-64;
- separate the 400% cliff effect from the broader ARPA below-400% generosity effect;
- rerun with premium-intensity or state-age gross benchmark burden.

## Updated Ranking

1. **ARPA 400% FPL subsidy-cliff removal**: current best conditional GO. Strong support and a
   policy-current diff-in-discontinuities design; uninsured falls about 2.6-3.1pp in main monthly-FPL
   screens, but mechanism and placebo checks need work.
2. **SNAP Emergency Allotment termination**: best food-security lead; household-level
   `food_insecure` rises about 7.6pp for lagged-SNAP households in early-ending states, but support
   is thin and secondary food outcomes are imprecise.
3. **ACA enhanced PTC / premium-intensity portfolio**: related to the new lead; useful as the
   premium-intensity extension, but earlier dynamic checks were not clean.
4. **ACA family glitch fix**: good insurance-side policy gap, but compact parquet lacks actual
   employer offer/premium eligibility variables.
5. **ACA state reinsurance waivers**: multi-state timing and good support, but SIPP first stage is
   only weakly directional and uninsured does not improve.
6. **ARPA zero-premium Marketplace in non-expansion states, 100-150% FPL**: promising backup from
   external quick screen; not yet fully tested in this pipeline.
7. **Maryland young-adult Marketplace subsidy**: clean design, but treatment cell is too small.
8. **New Jersey Health Plan Savings**: plausible, but bundled with ARPA, SBE transition, and state
   mandate.
9. **Adult Medicaid dental benefits**: strong policy/outcome fit, but treated support is too small
   and estimates are wrong-signed.
10. **State paid sick leave mandates**: policy variation exists, but no direct leave first stage and
    no coherent reduced-form pattern.
11. **State individual mandates**: weak Marketplace signal.
12. **Postpartum Medicaid extension**: important adult maternal-coverage policy, but compact SIPP
    has no direct birth/pregnancy variables and tiny support.
13. **Arkansas Medicaid work requirements**: policy-hot and directional replication signal, but
    current SIPP treated cell is too thin for a main paper.
14. **Minimum-wage food-security spillovers**: support is large, but the main food-security signal is
    null or wrong-signed and exposure is too crude for this crowded literature.
15. **Washington Working Families Tax Credit**: policy is strong, but 2023 treated support and tax
    eligibility measurement are too weak.
16. **Pandemic UI early termination**: clean timing, but no-go even with food-security outcomes.
17. **No Surprises Act**: excellent policy, SIPP measurement too indirect.
18. **STLDI expansion/state regulation**: no coherent SIPP signal.
19. **State-Based Marketplace transitions**: wrong-signed dynamics.

## New Artifacts

- `script/11_idea_scan/24_arpa_400fpl_cliff_diffdisc_test.py`
- `report/50_arpa_400fpl_cliff_diffdisc_test.md`
- `result/idea_scan/arpa400_diffdisc_estimates.csv`
- `result/idea_scan/arpa400_diffdisc_support.csv`
- `result/idea_scan/arpa400_diffdisc_cell_means.csv`
