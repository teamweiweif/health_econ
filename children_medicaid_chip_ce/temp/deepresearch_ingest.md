# Deep Research Ingest

## Local Search Result

The current workspace did not contain a prior project on the exact 2024 children Medicaid/CHIP 12-month CE mandate before this run.

The parent directory did contain related unwinding/churn materials under `..\US Insurance Project` and `..\InsuranceStudy\projects\insurance_churn_unwinding`. Those materials are adjacent, not same-topic outputs.

## Lessons Extracted

- Treat the 2023 Medicaid unwinding period as the central timing threat.
- Validate timing and mechanism coherence before moving to causal ML or broad heterogeneity.
- Do not call aggregate state-month enrollment volatility true churn; it is an aggregate coverage-instability proxy.
- Renewal/procedural outcomes are useful mechanisms, but if not child-specific they should not be treated as primary child-specific causal outcomes.
- A child-vs-adult triple difference is more defensible than a simple state DID because it absorbs state-month shocks, but adults are not a perfect untreated group.

## How This Shaped The Plan

- The main design is a state-group-month child-vs-adult DDD.
- 2023-04 through 2023-12 is explicitly flagged as an unwinding transition window.
- Mechanism and ACS validation panels are attempted but downgraded where public data are not child-specific or have only one post year.
