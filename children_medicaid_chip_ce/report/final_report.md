# Final Report

## Executive Summary

This project built a reproducible public-data workspace for the January 1, 2024 children Medicaid/CHIP 12-month continuous eligibility mandate. The main empirical product is a state-month child-vs-adult/non-child DDD-style enrollment-gap panel using CMS enrollment data through the latest staged June 2026 release, plus state-level renewal mechanism data and ACS health-insurance table validation.

Main DDD estimate for log enrollment: -0.0553 (SE 0.0548, n=4367).

Renewal mechanism procedural-rate estimate: 0.0102 (SE 0.0235, n=1781).

ACS child-vs-adult uninsured validation estimate: -0.3692 (SE 0.3705, n=510).

## Policy Background

Section 5112 of the Consolidated Appropriations Act, 2023 required all states to provide 12 months of continuous eligibility for children under age 19 in Medicaid and CHIP beginning January 1, 2024. Before that date, KFF/Georgetown Table 5 shows substantial state variation: some states already provided CE in Medicaid and CHIP, some only in one program, some only for younger ages, and some did not provide child CE.

## Exposure Definition

The primary exposure is `newly_treated_any_child_ce`: states with no pre-2024 child CE in either Medicaid or CHIP. Secondary designs use Medicaid-only and partial-or-new exposure definitions.

## Data Sources And Coverage

Core sources are CMS/Data.Medicaid.gov enrollment data, CMS eligibility processing renewal data, KFF/Georgetown policy survey Table 5, CMS SHO 23-004, CMS FAQ guidance, and Census ACS HI-05 public tables. Source inventory is in `temp/source_inventory.csv`.

## Outcomes

Primary administrative outcomes are child enrollment, adult/non-child proxy enrollment, the log child-adult/non-child enrollment gap, month-to-month net loss, and aggregate coverage-instability proxies. Mechanism outcomes include ex parte renewal rate, procedural termination rate/share, and pending renewal share. ACS validation outcomes include public/Medicaid coverage and uninsured percentages for children under 19 and adults 19-64.

## Identification

The preferred DDD-style gap design is stronger than a simple state DID because children are differenced against an adult/non-child comparison group before comparing newly treated states with already or partly compliant states. This is still not perfect: the comparison group is affected by Medicaid policy and unwinding, and already-compliant states are prior-treated comparison states.

## Diagnostics And Robustness

Dynamic event-study coefficients were estimated and plotted in `result/child_adult_gap_event_study.png`. Leave-one-state-out estimates ranged from -0.0700 to -0.0247. Window robustness outputs are in `result/robustness_summary.csv`.

## Mechanism Evidence

Renewal outcomes were attempted, but they are state-level and generally not child-specific. They should be interpreted as mechanism-consistent context or moderators, not child-specific causal outcomes.

## Survey Validation

ACS validation was attempted using Census published HI-05 tables. The reproducible XLSX parser uses 2019 and 2021-2024; 2020 is omitted by Census 1-year release limitations, and the 2018 HI-05 source is a legacy XLS file recorded in the source inventory but not parsed without an XLS reader. Census API access returned a key requirement in this environment, so validation uses official public table files rather than live API microdata/PUMS.

## Rejected Designs

Rejected or downgraded designs are documented in `temp/rejected_designs.md`. The main downgrades are: no individual-level true churn in public aggregate enrollment, renewal outcomes not child-specific, and ACS only having one current post-policy year in the staged tables.

## Final Go/No-Go Judgment

This workspace is empirically usable as a reproducible feasibility and first-results platform. It should not yet be treated as a finished publishable causal paper unless event-study pretrends, mechanism coherence, and influence diagnostics are judged acceptable after reviewing the generated plots and tables. If those diagnostics are weak, the appropriate paper is a transparent weak-design or wait-for-better-data report, not a significance search.

## Next Empirical Steps

1. Add a stronger state-specific source for CHIP premiums, lockouts, waiting periods, and unwinding completion timing.
2. Use a Census API key or direct PUMS download if microdata heterogeneity is required.
3. Add wild cluster bootstrap or randomization inference for state-cluster uncertainty.
4. Audit event-study pretrends visually before advancing to manuscript claims.
