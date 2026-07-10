# Twenty-Ninth Round Decision: ARPA COBRA Premium Subsidy

## Why This Was Tested

The external GPT note correctly keeps the ARPA 400% FPL cliff as the current best SIPP idea. Local
follow-up has already pushed that topic beyond the first screen: `RPRITYPE1` employer coverage was
recovered from raw SIPP, RD plots and age/premium-gradient checks were run, and the result now has a
more cautious label:

> strong uninsurance signal near 400% FPL, but not a clean Marketplace-only mechanism.

Given that, this round tested a different adult ARPA insurance provision that might explain part of
the broader 2021 private-coverage environment:

> Did ARPA's April-September 2021 100% COBRA premium subsidy help involuntarily separated workers
> retain former-employer coverage and avoid becoming uninsured?

This is policy-relevant and adult-only. The design is not as elegant as the 400% FPL cliff because
SIPP does not directly label COBRA, but SIPP does contain former-employer private coverage and job
separation reasons.

## Source Verification

- DOL COBRA premium assistance FAQ:
  https://www.dol.gov/sites/dolgov/files/EBSA/about-ebsa/our-activities/resource-center/faqs/cobra-premium-assistance.pdf
- KFF ARPA private coverage affordability summary:
  https://www.kff.org/affordable-care-act/how-the-american-rescue-plan-will-improve-affordability-of-private-health-coverage/

The verified policy rule is clean: premium assistance covered April 1, 2021 through September 30,
2021; eligibility required COBRA continuation eligibility due to reduction in hours or involuntary
termination, not voluntary quitting.

## Data Construction

New script:

- `script/11_idea_scan/37_arpa_cobra_subsidy_test.py`

New raw supplement:

- `temp/scratch/cobra_source_job_vars_2018_2024.parquet`

Main outputs:

- `report/74_arpa_cobra_subsidy_test.md`
- `result/idea_scan/arpa_cobra_event_panel.parquet`
- `result/idea_scan/arpa_cobra_support.csv`
- `result/idea_scan/arpa_cobra_raw_cells.csv`
- `result/idea_scan/arpa_cobra_estimates.csv`

Key SIPP variables recovered from raw files:

- `EHEMPLY1`, `EHEMPLY2`: source of private plan, including former employer.
- `EHICOST1`, `EHICOST2`: whether employer/union pays all, part, or none of premium.
- `EJB*_EMONTH`, `EJB*_RSEND`, `EJB*_JBORSE`: job end month, stop-work reason, job type.

COBRA proxy:

- active private plan line with `EHEMPLY1/2 == 2`, meaning former-employer source.

Stronger premium proxy:

- former-employer private coverage with `EHICOST1/2 == 1`, meaning employer/union pays all premium.

Treated event proxy:

- adult age 26-64, non-Medicare, involuntary separation (`RSEND` 1-6) in April-September 2021.

Main at-risk sample:

- had current-employer private coverage in the prior month.

## Support

April-September, excluding 2020:

- All adult separation events: 6,322 events, 5,630 persons.
- Treated involuntary events in subsidy window: 296 events, 283 persons.
- Main at-risk sample with lagged current-employer coverage: 151 treated events, 147 persons.
- Excluding seasonal completions from involuntary reasons leaves only 96 treated at-risk events.

This is usable for a fast screen, but small for a top-field standalone causal paper.

## Main Estimates

Main at-risk sample, April-September, excluding 2020. Event-level weighted OLS with year, month, and
state fixed effects; key coefficient is `involuntary separation x April-September 2021`.

- Former-employer private coverage, months 0-3: -0.0169, person-clustered t = -2.41.
- Premium all paid, months 0-3: -0.0078, person-clustered t = -1.83.
- Employer-related private coverage, months 0-3: -0.0030, person-clustered t = -0.10.
- Uninsured, months 0-3: -0.0144, person-clustered t = -0.64.
- Direct purchase, months 0-3: +0.0540, person-clustered t = 1.69.
- Market/subsidy proxy, months 0-3: +0.0518, person-clustered t = 1.62.

Broad April-September sample:

- Former-employer private coverage: -0.0072, t = -0.50.
- Premium all paid: +0.0025, t = 0.37.
- Uninsured: -0.0074, t = -0.46.
- Direct purchase: +0.0082, t = 0.28.

## Interpretation

This does not look like a COBRA retention first stage in SIPP.

The at-risk treated cell is not zero, but the directly relevant proxy, former-employer coverage, does
not rise. The stronger premium proxy also does not rise. There is a suggestive increase in
direct-purchase / Marketplace coverage among the at-risk group, which is interesting, but that is
not the intended COBRA mechanism and is only borderline in a small event sample.

The result may reflect displaced workers moving into Marketplace coverage under the broader ARPA
affordability regime, not COBRA subsidy take-up.

## Decision

`ARPA COBRA SUBSIDY: NO-GO AS A MAIN SIPP PAPER`

Keep it only as a possible mechanism appendix to the broader ARPA private-coverage project:

- It helps rule out a clean COBRA-first explanation for the ARPA 400% FPL/private-coverage results.
- It gives one additional sign that ARPA may have shifted job separators toward direct-purchase /
  Marketplace coverage.
- It should not replace the 400% FPL cliff lead.

## Updated Ranking

1. **ARPA enhanced PTC near 400% FPL / private-coverage response**: still the top conditional GO.
   The uninsurance signal is strongest, but the paper must be framed cautiously because Marketplace
   and employer mechanisms are not cleanly separable yet.
2. **Late Medicaid expansion 100-138% FPL bridge**: strongest pure Medicaid/uninsurance signal after
   the ARPA lead, but literature gap is less clean.
3. **ARPA UI Marketplace subsidy / ARPA low-income Marketplace variants**: useful as extensions of
   the broader ARPA affordability environment, not yet main-paper clean.
4. **Medicare age-65 bridge / threshold design**: clean threshold but weaker novelty.
5. **150% FPL low-income Marketplace SEP**: current policy gap but fragile in SIPP.
6. **ARPA COBRA premium subsidy**: policy clean, but SIPP first stage is wrong-signed or null for
   former-employer coverage; no-go as standalone.
7. **Arkansas work requirements**: policy hot but treated cell too thin.
8. **138% Medicaid-Marketplace cliff after ARPA**: conceptually good, but first-pass SIPP pattern
   was not compelling.

## Next Best Move

The next refinement should return to the lead ARPA 400% FPL project, but with the narrow exposed
sample suggested by the diagnostics:

- no employer-related private coverage in a pre-ARPA baseline window;
- stable near-threshold income around 350-450% FPL;
- age 40-64 and possibly age-premium-burden interactions;
- outcomes ordered as uninsured / any coverage first, direct-purchase / Marketplace second,
  employer coverage as a competing mechanism.

That is the highest-probability path to a defensible SIPP paper from the current evidence.
