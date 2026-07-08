# Identification Audit

## Preferred Design

The preferred design is implemented as a state-month child-vs-adult/non-child enrollment-gap difference-in-differences, equivalent to the two-group DDD comparison after differencing children against adults/non-children within each state-month:

`log(child enrollment) - log(adult/non-child enrollment proxy)` on `NewlyTreatedState x Post2024`, with state and month fixed effects.

The estimand is the incremental association of the federal 2024 children CE mandate in states without any pre-2024 child CE, relative to the adult/non-child comparison group and relative to already or partly compliant states. The adult/non-child comparison is constructed as total Medicaid/CHIP enrollment minus child Medicaid/CHIP enrollment so that the comparison group is consistently available from 2018 forward.

## Treatment Coding

Pre-2024 child CE status is transcribed from KFF/Georgetown Table 5 for January 2023 and preserved in `temp/policy_seed_child_ce_jan2023.csv`. The federal post period begins January 2024, verified against CMS SHO 23-004, CMS FAQ 10/27/2023, and the CMS continuous eligibility page.

## Main Threats

- The Medicaid unwinding transition in 2023 is the central confounder.
- Adult Medicaid enrollment is not a perfect untreated group.
- Already-compliant states are prior-treated comparison states, not never-treated controls.
- Renewal mechanism outcomes are state-level, not child-specific.
- Public state-month enrollment does not observe true individual churn.

## Diagnostics Status

Main DDD estimate: -0.0553 (SE 0.0548, n=4367).

Event-study coefficients estimated: 35 pre-period and 27 post-period coefficients.

The final go/no-go judgment is in `temp/go_no_go.md` and `report/final_report.md`.
