# Twenty-Second Round Decision: ARPA 400% FPL Premium/Age Mechanism Check

## Decision

The ARPA 400% FPL idea remains the strongest SIPP lead, but this round weakens the strongest
mechanism claim.

Current status: **CONDITIONAL GO, downgraded from a clean subsidy-cliff/premium-cliff paper to a
policy-relevant near-threshold private-coverage response paper.**

The preferred framing should not be:

> ARPA removed the 400% FPL cliff, causing high-premium older Marketplace-eligible adults to take up
> Marketplace coverage.

The defensible framing is narrower:

> Around the former 400% FPL subsidy cliff, ARPA is associated with a coverage gain above the
> threshold, but the response is not cleanly isolated to Marketplace take-up or to the groups where
> gross-premium exposure should mechanically matter most.

## What This Round Tested

Script: `sipp/script/11_idea_scan/28_arpa_400fpl_premium_gradient_test.py`

Report: `sipp/report/58_arpa_400fpl_premium_gradient_test.md`

The test used the augmented SIPP panel with `RPRITYPE1` employer coverage and merged the existing CMS
Exchange PUF state-year premium policy file.

Sample:

- Person-months.
- Ages 26-64.
- Non-Medicare.
- 350-450% monthly FPL.
- 2018-2023.
- States covered by the CMS Exchange PUF premium file.

Key mechanism checks:

1. `above400 x post x high-premium state`.
2. `above400 x post x continuous excess age-60 premium burden`.
3. `above400 x post x age 50-64`.
4. `above400 x post x high-premium state x age 50-64`.

All models use year, month, and state fixed effects with state-clustered standard errors.

## Main Findings

### 1. Binary high-premium state gradient does not support the mechanism

For the high-premium-state interaction:

- `uninsured`: -0.0014, state-clustered t = -0.07.
- `direct_purchase`: -0.0159, state-clustered t = -0.60.
- `marketplace_flag`: -0.0070, state-clustered t = -0.35.
- `market_or_subsidy`: -0.0178, state-clustered t = -0.68.

This is not what a clean premium-cliff mechanism predicts. If the removal of the 400% cliff were
driving the result primarily through high gross premiums, high-premium states should show stronger
positive Marketplace or direct-purchase responses above 400% FPL after ARPA.

### 2. Continuous premium burden gives one supportive coverage signal

For the continuous pre-2021 age-60 excess-burden interaction:

- `uninsured`: -0.0146, state-clustered t = -2.08.
- `any_coverage`: +0.0146, state-clustered t = 2.08.
- `private`: +0.0187, state-clustered t = 1.92.

This is the one mechanism-supportive result from this round. It suggests that higher pre-ARPA
premium exposure may be associated with larger coverage gains above 400% FPL after ARPA.

But the channel is not clean:

- `direct_purchase`: -0.0072, state-clustered t = -0.65.
- `marketplace_flag`: -0.0070, state-clustered t = -0.65.
- `market_or_subsidy`: -0.0073, state-clustered t = -0.67.

The coverage gain does not show up as stronger observed Marketplace/direct-purchase take-up.

### 3. Older adults do not show the expected stronger Marketplace response

For the age 50-64 interaction:

- `uninsured`: -0.0142, state-clustered t = -0.65.
- `direct_purchase`: -0.0108, state-clustered t = -0.64.
- `marketplace_flag`: -0.0096, state-clustered t = -0.48.
- `private`: +0.0281, state-clustered t = 0.94.

The direction for uninsured is favorable but weak. The Marketplace/direct-purchase channel is not
positive.

### 4. High-premium older adults move in the wrong direction on coverage

For the quadruple interaction:

- `uninsured`: +0.0740, state-clustered t = 1.81.
- `any_coverage`: -0.0740, state-clustered t = -1.81.
- `employer_private`: -0.0874, state-clustered t = -1.64.
- `marketplace_flag`: -0.0312, state-clustered t = -0.72.

This is the most important negative diagnostic. The group that should be most mechanically exposed
to the removed cliff does not show a clean coverage gain in this specification.

## Interpretation

This does not kill the ARPA 400% FPL idea, because earlier tests still show a robust negative
near-threshold uninsured response:

- Main monthly-FPL 350-450% model: uninsured about -2.6 percentage points.
- Age 21-64 model: uninsured about -3.1 percentage points.
- Post-April-2021 model: uninsured about -3.0 percentage points.
- Pre-non-employer subgroup: direct-purchase / market-or-subsidy signals are large and positive,
  though less precise.

But this round makes the clean top-field mechanism claim harder. The current evidence is more
consistent with a broader private-coverage and reporting/composition response near 400% FPL than
with a sharply identified Marketplace premium-cliff channel.

## Recommendation

Keep this as the first lead, but only as **conditional go**.

The next version should be framed as a feasibility note or early paper design with explicit
diagnostics:

1. Main outcome: `uninsured` / `any_coverage`.
2. Secondary outcomes: `direct_purchase`, `marketplace_flag`, `market_or_subsidy`, `employer_private`.
3. Mechanism diagnostics required in the main text, not hidden in appendix.
4. Avoid claiming that the observed coverage gain is cleanly mediated by Marketplace enrollment.
5. The most promising refinement is a **pre-non-employer / non-ESI-at-baseline subgroup**, because
   it is closer to the actually exposed population than broad high-premium or older-age splits.

## Go / No-Go

**Conditional GO for further refinement.**

Do not stop the project, but do not present it as a clean discontinuity paper yet. The next pass
should test whether the signal survives in a sample plausibly exposed to Marketplace subsidies:
people without employer-related private coverage before ARPA, with stable near-threshold income, and
excluding obvious Medicare/disability channels.
