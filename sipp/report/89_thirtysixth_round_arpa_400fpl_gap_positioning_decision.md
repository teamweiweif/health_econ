# Thirty-Sixth Round Decision: ARPA 400% FPL Gap Positioning

## Verdict

`GAP POSITIONING: CONDITIONAL GO STRENGTHENED`

The source and literature-gap review strengthens the ARPA 400% FPL idea as the current lead SIPP project.

The policy problem is real, current, and externally validated:

- CMS and IRS confirm the policy threshold and ARPA's temporary removal of the above-400% FPL premium tax credit cliff.
- KFF, Urban, RWJF, and BPC show that the 2026 return of the cliff is a live affordability and coverage issue.
- Recent administrative and simulation work studies enhanced premium tax credit expiration and subsidy targeting.

The remaining opening is specific:

**National SIPP person-month evidence on whether the 2021 removal of the 400% FPL cliff reduced uninsurance near the threshold, with coverage-source decomposition.**

## Decision

Proceed with this idea as a **conditional go** for the next writing/design stage.

Do not run additional model variants until the next package locks:

1. exact primary sample;
2. primary monthly-FPL design;
3. annual-FPL robustness role;
4. main uninsured outcome;
5. secondary any-coverage outcome;
6. source-decomposition mechanism outcomes;
7. lagged non-employer mechanism sample;
8. placebo-threshold and fake-policy checks;
9. no-go triggers.

## Defensible Contribution

Use this contribution statement:

> We provide national person-month evidence on whether ARPA's removal of the ACA 400% FPL subsidy cliff reduced uninsurance near the threshold, complementing policy simulations and Marketplace administrative-demand studies of enhanced premium tax credits.

Use this identification statement:

> The design compares local coverage discontinuities above versus below 400% FPL before and after ARPA, using SIPP monthly coverage data from 2017-2023.

Use this mechanism statement:

> The strongest mechanism evidence is concentrated among adults not coming from employer-related coverage, where direct-purchase/Marketplace subsidy proxies rise after the cliff removal.

## Boundary Conditions

The novelty claim must be narrow:

- not "first enhanced PTC paper";
- not "first ACA Marketplace subsidy threshold paper";
- not "first study of 400% FPL";
- not "final evidence on 2026 expiration";
- not "pure Marketplace enrollment effect";
- not "clean RDD."

The correct novelty claim is:

**ARPA-specific, national SIPP, person-month, local 400% FPL pre/post threshold design, with uninsured and coverage-source outcomes.**

## Evidence Carried Forward

Primary result from the consolidated memo:

- Sample: age 26-64, non-Medicare, 350-450% monthly FPL, 2017-2023.
- N: 215,972 person-months; 23,888 persons; 52 state clusters.
- Main outcome: uninsured.
- Main coefficient: above400 x post2021 = -0.0277.
- Person-cluster SE: 0.0141.
- State-cluster SE: 0.0151.

Mechanism result:

- Lagged non-employer sample N: 71,638 person-months.
- Market/subsidy proxy coefficient: +0.0739.
- Person-cluster SE: 0.0328.
- State-cluster SE: 0.0350.
- Direct-purchase coefficient: +0.0735.

Robustness carried forward:

- Main uninsured effect is negative across all tested bandwidths.
- Lagged non-employer market/subsidy effect is positive across all tested bandwidths.
- Pre-ARPA fake-policy test at 400% FPL is near zero.

Concerns carried forward:

- Annual-FPL mechanism is weak.
- Nearby placebo thresholds are not empty.
- Full-sample employer-related source also rises.
- Older-adult gradient is not supportive despite policy priors.

## Next Required Artifact

The next work unit should be:

**Paper-style empirical specification lock and identification memo**

It should include:

- final variable definitions;
- statutory annual-income issue and monthly-FPL rationale;
- model equation;
- table-shell list;
- figure-shell list;
- placebo and robustness sequence;
- exact claims allowed and disallowed;
- no-go triggers.

After that, a draft introduction/literature section can be written using `88_arpa_400fpl_source_literature_gap_memo.md` as the source base.
