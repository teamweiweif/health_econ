# New SIPP Adult ACA Idea Recommendation

## Executive Recommendation

Do not pivot to unwinding or child continuous eligibility.

The only direction from the current uploaded parquet that clears the first support screen is an
adult ACA affordability design centered on the **400% FPL premium tax credit cliff**. It is not
paper-ready from SIPP alone yet. The correct next paper-level version should add an external
premium-intensity layer, then retest:

**How do ACA affordability policies change insurance coverage, uninsured spells, and financial
exposure for middle-income adults near the subsidy cliff?**

Primary design:

- Use the 2021 ARPA removal of the 400% FPL premium tax credit cliff.
- Running variable: annual family income-to-poverty, `TFCYINCPOV`, with 4.0 equal to 400% FPL.
- RD-DID: just above vs just below 400% FPL, pre 2017-2020 vs post 2021-2023.
- Treatment-intensity upgrade: merge state/county-age benchmark premium burden or predicted
  premium burden, because the policy shock is much larger for older adults and high-premium
  states.
- SIPP contribution: observe people outside Marketplace admin data, including uninsured spells,
  non-Marketplace private coverage, direct purchase, utilization, out-of-pocket spending, and
  employment.

Fast verdict:

`CONDITIONAL-GO-ONLY-WITH-PREMIUM-INTENSITY`

## Why This Is Still The Best Candidate

The current policy gap is real. IRS confirms ARPA temporarily eliminated the 400% FPL PTC cap for
2021-2022. CMS describes the ARP/IRA tax credits as newly reaching people over 400% FPL, especially
older adults with high premiums. KFF's May 2026 evidence shows the expiration of enhanced credits
hit people just above the subsidy cliff especially hard.

The SIPP support is also real:

- PTC 300-500% FPL initial screen: 454,440 person-month rows and 27,496 persons.
- Above-400 group: 13,990 persons.
- Above-400 market/subsidy events: 14,319.
- Above-400 uninsured events: 17,393.
- Local 400% FPL bandwidth 0.50 screen: 231,984 rows and 15,602 persons.

## Why It Is Not Yet A Clean Go

The simple RD-DID does not show a clean positive Marketplace uptake story. Around 400% FPL with
a 50 percentage point bandwidth:

- `market_or_subsidy`: -0.0312, HC1 se 0.0058.
- `direct_purchase`: -0.0324, HC1 se 0.0063.
- `uninsured`: -0.0088, HC1 se 0.0063.
- `any_coverage`: +0.0088, HC1 se 0.0063.

Interpretation: support is adequate, but the simple threshold contrast is not enough. Both sides
of 400% FPL received affordability changes after ARPA, and SIPP marketplace/subsidy flags may not
track Marketplace administrative enrollment cleanly. The next test must use premium burden as
treatment intensity.

## Candidate Ranking After Fast Tests

1. `aca_ptc_400_fpl_cliff`
   - Status: `CONDITIONAL-GO-ONLY-WITH-PREMIUM-INTENSITY`.
   - Best research gap and best current policy relevance.
   - Not paper-ready without external premium data.

2. `state_reinsurance_individual_market`
   - Status: `BACKUP / COMPONENT ONLY`.
   - Good state policy variation, but binary adoption DDD gives the wrong sign:
     direct purchase -0.0112, market/subsidy -0.0077, uninsured +0.0273.
   - Could become useful if merged with official premium-reduction/pass-through intensity, but
     not as a standalone SIPP paper.

3. `late_medicaid_expansion`
   - Status: `FEASIBLE BUT LITERATURE-SATURATED`.
   - Support exists for VA/NE/OK/MO, but SD and NC are too late in the SIPP window.
   - Needs a sharper SIPP-only mechanism to be publishable.

4. `arkansas_medicaid_work_requirements`
   - Status: `FAST NOGO FOR MAIN PAPER`.
   - Target Arkansas age 30-49 low-income implementation window has only 43 persons.

5. `family_glitch_fix`
   - Status: `NOT TESTABLE FROM CURRENT PARQUET`.
   - Needs employer offer/family premium treatment variable.

6. `public_charge_immigrant_chilling`
   - Status: `NOT TESTABLE FROM CURRENT PARQUET`.
   - Metadata contains citizenship/nativity variables, but the 96-column uploaded parquet does
     not include them; national timing is also COVID-confounded.

7. `adult_postpartum_medicaid_extension`
   - Status: `DEFER`.
   - Requires pregnancy/birth variables not in current parquet and drifts toward maternal/child
     coverage.

## Concrete Next Test

Build `ptc_400fpl_cliff_v2` only if premium-intensity data can be added. Minimum external data:

- county/state-age benchmark silver premiums or premium burden by age/income/state;
- state Marketplace type and state supplemental subsidy indicators;
- state reinsurance premium-impact estimates as controls or secondary treatment intensity.

Required pass/fail checks:

- RD-DID around 400% FPL with bandwidths 390-410, 375-425, 350-450, and 300-500% FPL.
- Placebo cutoffs at 300%, 350%, 450%, and 500% FPL.
- Income-density/bunching around 400% FPL pre vs post.
- Age-intensity heterogeneity for 50-64 vs 26-49.
- Premium-intensity heterogeneity: high vs low expected benchmark premium burden.
- Outcome families: any coverage, uninsured, direct purchase/Marketplace, private, utilization,
  out-of-pocket spending, and employment.

Stop rule: if premium-intensity heterogeneity does not recover a coherent sign pattern and
placebo cutoffs remain large, mark this as a transparent no-go and do not compensate with causal ML.

## Files Created

- `script/11_idea_scan/01_fast_sipp_idea_screen.py`
- `script/11_idea_scan/02_ptc_400fpl_fast_test.py`
- `script/11_idea_scan/03_reinsurance_fast_test.py`
- `report/10_new_idea_scan.md`
- `report/11_ptc_400fpl_fast_test.md`
- `report/12_reinsurance_fast_test.md`
- `result/idea_scan/idea_screen_candidate_summary.csv`
- `result/idea_scan/ptc_400fpl_rddid_fast_estimates.csv`
- `result/idea_scan/reinsurance_ddd_fast_estimates.csv`

## Source Checks

- CMS, ARP/IRA tax credits and >400% FPL affordability:
  https://www.cms.gov/newsroom/blog/inflation-reduction-act-tax-credits-improve-coverage-affordability-middle-income-americans
- IRS, ARPA eliminated the >400% FPL PTC rule for 2021-2022:
  https://www.irs.gov/affordable-care-act/individuals-and-families/eligibility-for-the-premium-tax-credit
- KFF, 2026 enhanced PTC expiration and subsidy cliff evidence:
  https://www.kff.org/affordable-care-act/what-we-know-so-far-about-2026-aca-marketplace-enrollment-premiums-and-deductibles/
- KFF, Medicaid expansion implementation dates:
  https://www.kff.org/affordable-care-act/state-indicator/state-activity-around-expanding-medicaid-under-the-affordable-care-act/
- KFF, Medicaid work requirements implementation tracker:
  https://www.kff.org/medicaid/medicaid-work-requirements-tracker-overview/
- CMS, Section 1332 State Innovation Waivers:
  https://www.cms.gov/marketplace/states/section-1332-state-innovation-waivers
