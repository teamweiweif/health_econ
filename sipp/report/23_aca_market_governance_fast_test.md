# ACA Market Governance Fast Test

## Question

Can current SIPP 2017-2023 reference-year data support a new adult, non-child, non-unwinding
paper around ACA market-governance policies?

This screen tests two policy shocks:

1. State individual mandate penalties after the federal penalty was set to zero.
2. State transitions from HealthCare.gov to full State-Based Marketplaces.

## Source Checks

Individual mandate policy coding:

- New Jersey Treasury Health Insurance Mandate: https://nj.gov/treasury/njhealthinsurancemandate/
- California Franchise Tax Board Health Care Mandate: https://www.ftb.ca.gov/file/personal/filing-situations/healthcare/estimator/
- Rhode Island Division of Taxation Health Insurance Mandate: https://tax.ri.gov/guidance/health-insurance-mandate

State-Based Marketplace transition coding:

- CMS Health Insurance Exchanges 2025 Open Enrollment Report, footnote on state SBE transitions: https://www.cms.gov/files/document/health-insurance-exchanges-2025-open-enrollment-report.pdf
- KFF State Health Insurance Marketplace Types: https://www.kff.org/affordable-care-act/state-indicator/state-health-insurance-marketplace-types/

## Data Construction

- Source parquet: `data/analysis_ready/sipp_2018_2024_person_month_panel.parquet`.
- Collapsed to person-year from monthly observations.
- Sample: adults age 26-64 with family income 138-600% FPL and at least six observed months.
- Main outcomes: annual share of months uninsured, covered, direct-purchase/Marketplace, exchange/subsidized private, private, OOP any, and doctor visit any.
- Models: weighted linear probability screens with state and year fixed effects.
- Mandate heterogeneity: `mandate_active x healthy`, where healthy is excellent/very good health.
- SBM heterogeneity: `sbm_active x subsidy_income`, where subsidy-income is 138-400% FPL.

## Support

Mandate sample:

- Person-years: 89,724.
- Persons: 53,773.
- States: 48.
- Treated-state person-years: 13,760.
- Active mandate person-years: 7,368.

SBM transition sample:

- Person-years: 64,228.
- Persons: 38,502.
- States: 38.
- Transition-state person-years: 7,316.
- Active SBM person-years: 2,034.

## Static Estimates: State Individual Mandates

Main term: `mandate_active`, state/year FE, adults 26-64 and 138-600% FPL.

- `uninsured`: -0.0067, se 0.0078, t -0.86.
- `any_coverage`: +0.0067, se 0.0078, t 0.86.
- `direct_market`: +0.0138, se 0.0097, t 1.42.
- `exchange_subsidy`: +0.0106, se 0.0089, t 1.19.
- `private`: +0.0032, se 0.0112, t 0.29.
- `oop_any`: +0.0080, se 0.0126, t 0.64.
- `doctor_any`: -0.0239, se 0.0114, t -2.11.

Healthy-selection term: `mandate_active_x_healthy`.

- `uninsured`: +0.0124, se 0.0087, t 1.42.
- `any_coverage`: -0.0124, se 0.0087, t -1.42.
- `direct_market`: -0.0088, se 0.0109, t -0.80.
- `exchange_subsidy`: +0.0064, se 0.0102, t 0.63.
- `private`: -0.0009, se 0.0123, t -0.07.
- `oop_any`: +0.0342, se 0.0140, t 2.44.
- `doctor_any`: -0.0107, se 0.0131, t -0.82.

Verdict: `WEAK-MECHANISM-SIGNAL-NOT-CLEAN-GO`.

## Static Estimates: State-Based Marketplace Transitions

Main term: `sbm_active`, state/year FE, adults 26-64 and 138-600% FPL in the transition-risk state set.

- `uninsured`: +0.0313, se 0.0118, t 2.64.
- `any_coverage`: -0.0313, se 0.0118, t -2.64.
- `direct_market`: -0.0249, se 0.0123, t -2.03.
- `exchange_subsidy`: -0.0169, se 0.0106, t -1.59.
- `private`: +0.0020, se 0.0152, t 0.13.
- `oop_any`: +0.0984, se 0.0203, t 4.85.
- `doctor_any`: -0.0137, se 0.0198, t -0.69.

Subsidy-income term: `sbm_active_x_subsidy_income`.

- `uninsured`: -0.0425, se 0.0147, t -2.90.
- `any_coverage`: +0.0425, se 0.0147, t 2.90.
- `direct_market`: +0.0217, se 0.0164, t 1.32.
- `exchange_subsidy`: +0.0164, se 0.0148, t 1.10.
- `private`: -0.0039, se 0.0201, t -0.20.
- `oop_any`: -0.0682, se 0.0247, t -2.76.
- `doctor_any`: +0.0205, se 0.0236, t 0.87.

Verdict: `NO-CLEAN-COVERAGE-SIGNAL`.

## Interpretation

This is a fast screen, not a final paper design. A clean GO would require:

- signs aligned with the policy mechanism;
- enough treated support;
- no large pre-event deviations in the event coefficients;
- robustness to excluding states with overlapping ACA policies such as reinsurance and state subsidies.

## Artifacts

- `script/11_idea_scan/10_aca_market_governance_fast_test.py`
- `result/idea_scan/aca_market_governance_policy_state_year.csv`
- `result/idea_scan/aca_market_governance_person_year_panel.parquet`
- `result/idea_scan/aca_market_governance_support.csv`
- `result/idea_scan/aca_market_governance_mandate_estimates.csv`
- `result/idea_scan/aca_market_governance_mandate_event.csv`
- `result/idea_scan/aca_market_governance_sbm_estimates.csv`
- `result/idea_scan/aca_market_governance_sbm_event.csv`
- `result/idea_scan/aca_market_governance_leave_one.csv`
