# Twenty-Third Round Decision: Late ACA Medicaid Expansions

## Decision

This is the strongest **new** adult SIPP signal found in this round.

Status: **CONDITIONAL GO / EMPIRICAL GO, PUBLICATION-GAP CONDITIONAL**.

The estimates are much cleaner than many prior adult-policy screens: Medicaid rises and uninsured
falls around the 138% FPL eligibility boundary in late-expansion states. But the topic cannot be
sold as a generic Medicaid-expansion paper because that literature is already large. The only
credible publication angle is a narrower SIPP contribution:

> Late Medicaid expansions and the 100-138% FPL coverage-gap bridge: monthly evidence on whether
> low-income adults moved from uninsurance or Marketplace/direct-purchase paths into Medicaid in
> late-adopting states.

## Why This Is Policy-Relevant Now

Current external source checks:

- KFF's May 21, 2026 tracker reports that 41 states including DC have adopted ACA Medicaid
  expansion and 10 states have not. KFF describes ACA expansion as covering nearly all adults up to
  138% FPL.
- KFF's 2026 Medicaid watch notes that the 2025 reconciliation law and related policy changes put
  Medicaid expansion adults directly in the policy spotlight, including work requirements,
  more frequent redeterminations, and eligibility changes.
- KFF's 2025 Medicaid expansion brief says South Dakota and North Carolina were the most recent
  adopters in 2023, and also emphasizes that the existing evidence base already links expansion to
  lower uninsurance and better access.

That last point is the central tradeoff: the policy question is live, but the literature gap is much
smaller than in the ARPA 400% FPL cliff idea.

## Scripts and Outputs

Main test:

- `sipp/script/11_idea_scan/29_late_medicaid_expansion_threshold_test.py`
- `sipp/report/60_late_medicaid_expansion_threshold_test.md`
- `sipp/result/idea_scan/late_medicaid_expansion_threshold_estimates.csv`
- `sipp/result/idea_scan/late_medicaid_expansion_threshold_support.csv`
- `sipp/result/idea_scan/late_medicaid_expansion_state_support.csv`
- `sipp/result/idea_scan/late_medicaid_expansion_cell_support.csv`

Robustness:

- `sipp/script/11_idea_scan/30_late_medicaid_expansion_robustness.py`
- `sipp/report/61_late_medicaid_expansion_robustness.md`
- `sipp/result/idea_scan/late_medicaid_expansion_robustness.csv`
- `sipp/result/idea_scan/late_medicaid_expansion_robustness_pivot.csv`

Both scripts compile.

## Design Tested

Unit: person-month.

Sample:

- Adults age 19-64.
- Non-Medicare.
- Late expansion states plus never-expansion states.
- Main FPL window: 0-250% monthly FPL.
- Narrow FPL window: 100-250% monthly FPL, with the treated eligibility band defined as 100-138%
  FPL.

Treatment:

- `expansion_active`: state-month is after late Medicaid expansion implementation.
- Main interaction: `expansion_active x eligible`.

Fixed effects and controls:

- State fixed effects.
- Calendar year-month fixed effects.
- FPL quadratic.
- Age quadratic.
- Sex, Black, Hispanic, disability.

Inference:

- State-clustered and person-clustered standard errors.

Late expansion dates coded:

- Maine and Virginia: January 2019.
- Idaho and Utah: January 2020.
- Nebraska: October 2020.
- Oklahoma: July 2021.
- Missouri: October 2021.
- South Dakota: July 2023.
- North Carolina: December 2023.

## Main Empirical Result

The strongest specification is the narrow monthly-FPL threshold design:

Sample: 100-250% monthly FPL, treated eligibility band 100-138% FPL.

- Person-months: 191,926.
- Persons: 16,175.
- States: 19.
- Active eligible person-months: 3,242.
- Active eligible persons: 583.

Main DDD estimates:

- Medicaid: +8.9 percentage points, state-clustered t = 3.04.
- Uninsured: -7.4 percentage points, state-clustered t = -4.80.
- Any coverage: +7.4 percentage points, state-clustered t = 4.80.
- Public coverage: +7.5 percentage points, state-clustered t = 2.62.
- Private coverage: -1.7 percentage points, not significant.
- Direct purchase / Marketplace proxies: positive but not significant with state clustering.
- SNAP monthly participation: +6.5 percentage points, state-clustered t = 2.69.

Annual-FPL robustness is directionally consistent:

- Medicaid: +11.1 percentage points, state-clustered t = 3.51.
- Uninsured: -7.1 percentage points, state-clustered t = -2.44.
- Any coverage: +7.1 percentage points, state-clustered t = 2.44.

Non-disability / non-SSI narrow robustness is also directionally supportive:

- Medicaid: +6.0 percentage points, state-clustered t = 3.08.
- Uninsured: -7.3 percentage points, state-clustered t = -2.60.
- Any coverage: +7.3 percentage points, state-clustered t = 2.60.

## Robustness Findings

Leave-one-state checks preserve the basic result:

- Dropping Oklahoma: Medicaid +7.5 pp, uninsured -7.6 pp.
- Dropping Missouri: Medicaid +10.8 pp, uninsured -7.8 pp.
- Dropping Virginia: Medicaid +6.3 pp, uninsured -7.1 pp.
- Dropping 2023 adopters: Medicaid +8.9 pp, uninsured -7.6 pp.
- Dropping 2021 PHE adopters: Medicaid +9.4 pp, uninsured -8.2 pp.

The weakest group check is dropping all 2019/2020 adopters:

- Medicaid +8.1 pp, state-clustered t = 1.51.
- Uninsured -4.2 pp, state-clustered t = -2.43.

This says the design is not one-state driven, but sample support becomes thin when early adopters
are removed.

## Main Problem

The fake 12-month pre-period placebo is mixed:

- Medicaid placebo: +1.3 pp, state-clustered t = 0.22.
- Uninsured placebo: -5.4 pp, state-clustered t = -1.77.

This is important. It means the Medicaid take-up result passes a useful placebo check, but the
uninsured decline may partly reflect treated-state pre-trends or composition differences among
low-income adults before implementation.

The second problem is innovation. KFF itself points to a large literature linking Medicaid expansion
to lower uninsurance, access gains, affordability gains, and broader benefits. A standard expansion
DID would not be enough.

## How To Frame If Continued

Do not frame as:

> Did Medicaid expansion reduce uninsurance?

That is too saturated.

Frame as:

> In late-adopting states, how did expansion change monthly coverage paths around the 100-138% FPL
> bridge between Medicaid eligibility and subsidized Marketplace coverage?

The SIPP-specific contribution must be:

1. Monthly coverage path decomposition.
2. 100-138% FPL threshold targeting rather than all low-income adults.
3. Late-adopter states during 2019-2023, including ballot-initiative and delayed-implementation
   states.
4. Direct comparison of Medicaid uptake, uninsurance, direct purchase / Marketplace coverage, and
   SNAP co-participation.
5. Explicit placebo/pretrend evidence rather than a generic expansion result.

## Recommendation

Keep this as a **second lead / backup to ARPA 400% FPL**.

It is empirically stronger than most previous new adult ideas, but less innovative than the ARPA
cliff idea. If the ARPA paper remains too mechanism-fragile, this late-expansion idea is now the
best backup because it has:

- clear adult policy treatment;
- strong sample support;
- strong Medicaid take-up signal;
- consistent uninsured decline;
- real current policy salience in 2026.

Before promoting it to first lead, run:

1. A stacked DID / Callaway-Sant'Anna style event-study variant.
2. Event-time plots for Medicaid and uninsured in 100-138% FPL adults.
3. Placebo thresholds, especially 150-200% and 200-250% FPL.
4. State-specific event plots for Virginia, Oklahoma, Missouri, Utah, Idaho, Nebraska.
5. A transition decomposition: uninsured to Medicaid, direct-purchase/Marketplace to Medicaid,
   private to Medicaid, and no-coverage changes.

## Current Ranking

1. ARPA 400% FPL cliff removal: more novel, still conditional because mechanism diagnostics are
   mixed.
2. Late Medicaid expansion threshold design: stronger first-stage and coverage signal, but
   literature gap is much harder.
3. Public charge / immigrant chilling effect: highly topical and potentially novel, but requires
   heavy raw-variable extraction for citizenship/nativity before quick-screening.
