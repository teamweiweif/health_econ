# Fifth-Round Adult SIPP Policy Idea Decision

## Question

After the PTC premium-intensity upgrade failed to become a clean go, can the current 96-column
SIPP parquet support another adult, non-child, non-unwinding idea with direct causal identification
and current policy relevance?

## New Ideas Tested

This round tested three adult policy ideas using the uploaded main parquet as the source:

1. State individual mandate penalties after the federal individual mandate penalty was set to zero.
2. State transitions from HealthCare.gov to full State-Based Marketplaces.
3. The No Surprises Act as a financial-protection shock for privately insured adults in states without
   comprehensive pre-existing balance-billing protections.

## 1. State Individual Mandates

Policy source:

- New Jersey Treasury Health Insurance Mandate.
- California Franchise Tax Board Health Care Mandate.
- Rhode Island Division of Taxation Health Insurance Mandate.

Design:

- Treated states: New Jersey from 2019, California and Rhode Island from 2020.
- Excluded: Massachusetts legacy mandate, Vermont no-penalty mandate, DC because the compact
  SIPP support is too small and policy coding is less useful for this screen.
- Sample: adults age 26-64, 138-600% FPL, at least six observed months.
- Outcomes: uninsured, any coverage, direct-purchase/Marketplace, exchange/subsidized private,
  private coverage, OOP, doctor use.
- Model: person-year weighted LPM with state and year FE.
- Mechanism check: `mandate_active x healthy`.

Support:

- 89,724 person-years.
- 53,773 persons.
- 48 states.
- 13,760 treated-state person-years.
- 7,368 active mandate person-years.

Main static estimates:

- `uninsured`: -0.0067, se 0.0078.
- `any_coverage`: +0.0067, se 0.0078.
- `direct_market`: +0.0138, se 0.0097.
- `exchange_subsidy`: +0.0106, se 0.0089.

Mechanism problem:

- `mandate_active x healthy` is not supportive:
  - `uninsured`: +0.0124, se 0.0087.
  - `direct_market`: -0.0088, se 0.0109.

Dynamic check:

- No pre-lead problem at event time -2.
- Direct-market and exchange/subsidy signals appear only later:
  - `direct_market` event +2: +0.0229, se 0.0138.
  - `direct_market` event +3: +0.0303, se 0.0143.
  - `exchange_subsidy` event +2: +0.0266, se 0.0128.
  - `exchange_subsidy` event +3: +0.0312, se 0.0134.
- Uninsured/any coverage do not show a clean event pattern.

Leave-one-treated-state check:

- Excluding California flips `direct_market` negative (-0.0123).
- Excluding New Jersey or Rhode Island leaves direct-market positive, which implies the signal is
  not stable across treated-state definitions and is likely California-sensitive.

Decision:

`WEAK MECHANISM SIGNAL; NOT CLEAN GO`

This is the best new idea from this round, but not yet a main-paper design. The policy gap is real:
state mandates remain a live ACA market-stabilization tool after federal repeal. The SIPP novelty is
monthly individual coverage-path measurement. But the current screen is not strong enough:
coverage effects are small and insignificant, healthy-person selection is the wrong sign, and the
marketplace signal is not robust to excluding California.

## 2. State-Based Marketplace Transitions

Policy source:

- CMS Health Insurance Exchanges 2025 Open Enrollment Report footnote: New Jersey and
  Pennsylvania transitioned to SBEs for 2021 coverage; Kentucky, Maine, and New Mexico for 2022
  coverage.
- KFF State Health Insurance Marketplace Types.

Design:

- Treated states: NJ, PA, KY, ME, NM.
- Risk set excludes states that were already state-based marketplaces before the transition window.
- Sample: adults age 26-64, 138-600% FPL.
- Mechanism check: `sbm_active x subsidy_income`.

Support:

- 64,228 person-years.
- 38,502 persons.
- 38 states.
- 7,316 transition-state person-years.
- 2,034 active SBM person-years.

Main static estimates:

- `uninsured`: +0.0313, se 0.0118.
- `any_coverage`: -0.0313, se 0.0118.
- `direct_market`: -0.0249, se 0.0123.
- `exchange_subsidy`: -0.0169, se 0.0106.

Subsidy-income interaction:

- `uninsured`: -0.0425, se 0.0147.
- `any_coverage`: +0.0425, se 0.0147.
- `direct_market`: +0.0217, se 0.0164.
- `exchange_subsidy`: +0.0164, se 0.0148.

Dynamic check:

- Event +2 goes in the wrong direction:
  - `uninsured`: +0.0472, se 0.0186.
  - `direct_market`: -0.0453, se 0.0177.
  - `exchange_subsidy`: -0.0352, se 0.0160.

Decision:

`NO CLEAN GO`

The interaction suggests lower-income subsidy-eligible adults may move differently, but the main
policy signal is wrong-signed and the dynamic pattern does not support a clean SBM uptake story.
This should not be pursued as a SIPP-only paper.

## 3. No Surprises Act

Policy source:

- CMS State Surprise Billing Laws and the No Surprises Act.
- KFF No Surprises Act implementation brief.
- Commonwealth Fund state balance-billing protections table, as of April 16, 2020.

Design:

- Treatment: states without comprehensive pre-NSA balance-billing protections x 2022+.
- Control: states with comprehensive pre-NSA protections.
- Window: 2020-2023 only, to avoid pretending older state-law adoption dates were fully coded.
- Main sample: privately insured adults age 26-64 with doctor or hospital use.
- Stronger exposure sample: privately insured hospital users.
- Placebo: public-covered care users.

Support:

- Private care users: 45,491 person-years, 31,226 persons.
- Private hospital users: 3,696 person-years, 3,378 persons.
- Public-care placebo: 14,122 person-years, 10,253 persons.
- Main-sample post new-protection person-years: 8,220.

Main estimates:

Private care users:

- `log_oop`: +0.0199, se 0.0708.
- `oop_gt_1000`: -0.0027, se 0.0101.
- `oop_amount`: -21.57, se 63.82.

Private hospital users:

- `log_oop`: -0.1441, se 0.2716.
- `oop_gt_1000`: -0.0578, se 0.0381.
- `oop_amount`: -239.51, se 311.64.

Placebo issue:

- Public-covered care users also show a negative `oop_gt_1000` coefficient (-0.0190, se 0.0127),
  so the private-hospital signal is not cleanly separable from broader state-year movement.

Measurement problem:

- SIPP observes broad medical OOP, not out-of-network surprise bills.
- It does not identify emergency-department use, self-funded plans, provider network status, or
  whether a bill was subject to the No Surprises Act.

Decision:

`NO CLEAN GO`

The policy question is excellent, but the uploaded SIPP file is too blunt for this causal design.

## Updated Ranking After This Round

1. **ACA enhanced PTC / 400% FPL with premium intensity** remains the best policy question, but
   current state-level premium matching failed the dynamic check. Status: `conditional only`.
2. **State individual mandates** are the best new adult idea from this round. Status:
   `weak signal, not clean GO`.
3. **Pandemic UI early termination** remains the cleanest direct timing design from earlier rounds,
   but the SIPP insurance sample is too small for a top-field main paper.
4. **No Surprises Act** has a strong policy gap but SIPP measurement is too indirect.
5. **State-Based Marketplace transitions** fail the direction/dynamics screen.
6. **Childless EITC and minimum wage** remain dependent on richer variables not present in the
   uploaded 96-column parquet.

## Current Honest Verdict

`NO NEW CLEAN IMMEDIATE GO FROM THE CURRENT 96-COLUMN PARQUET`

The new searches and tests did not overturn the prior conclusion. The current file is excellent for
fast feasibility screening, but every high-policy-relevance adult design has one of the following
binding problems:

- policy variation is too coarse at state-year level;
- SIPP state-only geography prevents clean premium or local-market exposure;
- the compact parquet omits key variables such as citizenship/nativity, filing/tax-unit details,
  school enrollment, occupation/industry, county/rating area, emergency department use, and plan
  network status;
- the event is real but treated SIPP support is too thin.

## Next Best Search Direction

The next idea search should not keep retesting generic ACA uptake with the same state-year design.
The best remaining route is to find an adult policy where:

1. treatment varies at state-year or state-month level;
2. the treatment directly maps to variables already in the compact SIPP file;
3. the outcome is not a rare path-specific event;
4. the expected first-stage mechanism is visible in SIPP.

If no such policy is found, the practical next move is not another model. It is to rebuild a richer
SIPP extract with one targeted variable family:

- citizenship/nativity for public-charge chilling effects;
- tax filing/school enrollment for childless EITC;
- occupation/industry/hourly wage for minimum-wage insurance spillovers;
- county/rating area for ACA premium subsidy exposure;
- emergency/plan/network/bill variables if available for No Surprises Act style financial protection.

## New Artifacts

- `script/11_idea_scan/10_aca_market_governance_fast_test.py`
- `script/11_idea_scan/11_no_surprises_act_fast_test.py`
- `report/23_aca_market_governance_fast_test.md`
- `report/24_no_surprises_act_fast_test.md`
- `result/idea_scan/aca_market_governance_policy_state_year.csv`
- `result/idea_scan/aca_market_governance_person_year_panel.parquet`
- `result/idea_scan/aca_market_governance_mandate_estimates.csv`
- `result/idea_scan/aca_market_governance_mandate_event.csv`
- `result/idea_scan/aca_market_governance_sbm_estimates.csv`
- `result/idea_scan/aca_market_governance_sbm_event.csv`
- `result/idea_scan/aca_market_governance_leave_one.csv`
- `result/idea_scan/no_surprises_act_person_year_panel.parquet`
- `result/idea_scan/no_surprises_act_support.csv`
- `result/idea_scan/no_surprises_act_estimates.csv`
- `result/idea_scan/no_surprises_act_event.csv`
