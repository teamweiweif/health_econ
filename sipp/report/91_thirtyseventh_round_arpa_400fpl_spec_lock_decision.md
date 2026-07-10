# Thirty-Seventh Round Decision: ARPA 400% FPL Specification Lock

## Verdict

`SPECIFICATION LOCK COMPLETE; CONDITIONAL GO CARRIED FORWARD`

The ARPA 400% FPL lead has now moved from idea screen to a locked paper-style design package.

The locked design is:

- national SIPP person-months;
- reference years 2017-2023;
- adults age 26-64;
- non-Medicare;
- monthly FPL 3.5-4.5;
- local linear difference-in-discontinuities around 400% FPL;
- primary treatment: `above400 x post_year2021`;
- primary outcome: uninsured;
- mechanism outcome: `market_or_subsidy`;
- mechanism sample: lagged non-employer months;
- inference: person and state cluster standard errors.

## Current Decision

Proceed to paper-writing stage only under conditional-go language.

Do not run additional tuning before writing:

- introduction;
- source/literature section;
- empirical design section;
- main results table shell;
- identification-threat section.

## Locked Headline

Use this as the headline empirical statement:

> In SIPP person-month data for adults age 26-64 near 400% FPL, the ARPA period is associated with a roughly 2.8 percentage point local reduction in uninsurance above the former subsidy cliff, relative to below-threshold adults.

Use this as the mechanism statement:

> Direct-market/subsidy proxy coverage rises most clearly among adults not coming from employer-related coverage, but full-sample source changes are mixed.

## Current Evidence

Main sample:

- 215,972 person-months.
- 23,888 persons.
- 52 state clusters.
- Uninsured coefficient: -0.0277.
- Person SE: 0.0141.
- State SE: 0.0151.

Mechanism sample:

- Lagged non-employer person-months: 71,638.
- Market/subsidy coefficient: +0.0739.
- Person SE: 0.0328.
- State SE: 0.0350.

Robustness:

- Main uninsured effect is negative in 5/5 bandwidth specifications.
- Lagged non-employer market/subsidy effect is positive and significant under person and state clustering in 5/5 bandwidth specifications.
- Donut specifications weaken precision but do not reverse the main uninsured signal.
- Pre-ARPA fake-policy tests at 400% are near zero.

Threats:

- Annual-FPL market/subsidy mechanism is weak.
- Placebo thresholds are not empty.
- Employer-related source rises in the full sample.
- Older-adult heterogeneity is not supportive enough for a headline.

## Paper-Framing Decision

Frame as:

`A coverage-affordability paper using the ARPA 400% FPL cliff removal as a local federal threshold shock.`

Do not frame as:

- a pure Marketplace enrollment paper;
- a clean RDD;
- a causal-ML paper;
- an unwinding paper;
- a child coverage paper;
- a 2026 expiration-effect paper.

## Next Required Step

Write a draft paper section package:

1. one-page introduction skeleton;
2. literature/gap paragraph using the source memo;
3. empirical design subsection using the specification lock;
4. table and figure captions for the locked artifacts;
5. identification threats paragraph.

No further exploration should precede that writing package unless a replication error is found in the locked outputs.
