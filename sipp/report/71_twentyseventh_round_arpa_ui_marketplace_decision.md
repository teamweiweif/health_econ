# Twenty-Seventh Round Decision: ARPA UI Marketplace Subsidy

## Decision

Status: **CONDITIONAL BACKUP / ARPA EXTENSION, NOT FIRST-LEAD**.

This is a better SIPP idea than the IRA insulin-cap screen because the data directly observe both
the policy exposure proxy and the intended coverage margins:

- unemployment compensation receipt;
- monthly uninsured status;
- direct-purchase private coverage;
- Marketplace / exchange flags;
- subsidized private coverage flags.

But it is still weaker than the 400% FPL cliff design. The key reason is identification: UI receipt
in 2021 is deeply entangled with the pandemic labor market, UI program changes, job loss, and
coverage substitution. The policy signal is visible, but not clean enough to become the lead paper.

## Policy Question

Did ARPA's special 2021 Marketplace subsidy rule for people receiving unemployment compensation
increase Marketplace/direct-purchase coverage or reduce uninsurance among UI recipients?

The policy hook is real:

- CMS states that taxpayers receiving unemployment compensation during any week beginning in 2021
  may be eligible for premium tax credits for 2021 Marketplace coverage.
- KFF explains that for UI recipients, household income above 133% FPL was disregarded for
  Marketplace premium and cost-sharing subsidy purposes in 2021, making zero-premium benchmark
  silver coverage possible.

This is a narrower and more individual-level ARPA affordability shock than the 400% FPL cliff.

## New Artifacts

Script:

- `sipp/script/11_idea_scan/35_arpa_ui_marketplace_subsidy_test.py`

Report:

- `sipp/report/70_arpa_ui_marketplace_subsidy_test.md`

Outputs:

- `sipp/result/idea_scan/arpa_ui_marketplace_estimates.csv`
- `sipp/result/idea_scan/arpa_ui_marketplace_support.csv`
- `sipp/result/idea_scan/arpa_ui_marketplace_raw_cells.csv`

## Data Support

Main sample:

- adults ages 26-64;
- non-Medicare;
- FPL <= 1000%;
- SIPP reference years 2018-2023.

2021 UI-recipient support:

- 10,446 person-months;
- 931 persons with any UI receipt in the year;
- 4,773 person-months with UI receipt in that month.

Support is usable for a screen, but much smaller than the 400% FPL cliff or late Medicaid expansion
designs.

## Raw Pattern

Among UI-year recipients:

- 2019:
  - uninsured: 22.6%;
  - direct purchase: 14.3%;
  - Marketplace flag: 12.1%;
  - subsidized private: 3.5%.
- 2021:
  - uninsured: 17.4%;
  - direct purchase: 27.2%;
  - Marketplace flag: 24.9%;
  - subsidized private: 8.0%.
- 2022:
  - uninsured: 15.4%;
  - direct purchase: 25.3%;
  - Marketplace flag: 22.0%;
  - subsidized private: 4.3%.

The 2021 jump in Marketplace/direct-purchase coverage is large and policy-consistent. The problem is
that 2022 remains high, so the pattern is not uniquely a short-lived 2021 UI rule.

## Model Results

Main DDD key:

- `ui_year x 2021`

All years:

- uninsured: -0.36 pp, person-clustered t = -0.27;
- direct purchase: +3.08 pp, person-clustered t = 1.84;
- Marketplace flag: +2.33 pp, person-clustered t = 1.45;
- subsidized private: +1.44 pp, person-clustered t = 1.29;
- market/subsidy composite: +2.89 pp, person-clustered t = 1.72.

Excluding 2020:

- uninsured: -2.32 pp, person-clustered t = -1.41;
- direct purchase: +3.94 pp, person-clustered t = 2.06;
- Marketplace flag: +3.11 pp, person-clustered t = 1.70;
- market/subsidy composite: +3.81 pp, person-clustered t = 1.99.

Timing model, 2019/2021/2022 with April-September subsidy window:

- uninsured: -1.41 pp, person-clustered t = -1.98;
- direct purchase: -0.70 pp, person-clustered t = -1.45;
- Marketplace flag: -0.21 pp, person-clustered t = -0.52;
- market/subsidy composite: -0.68 pp, person-clustered t = -1.41.

Timing model, 2019/2021/2022 with July-December implementation window:

- uninsured: -0.58 pp, person-clustered t = -0.47;
- direct purchase: +0.67 pp, person-clustered t = 0.74;
- Marketplace flag: +1.58 pp, person-clustered t = 1.79;
- market/subsidy composite: +0.77 pp, person-clustered t = 0.85.

## Interpretation

The signal is real enough to preserve:

- direct-purchase / Marketplace coverage is higher for 2021 UI recipients;
- excluding 2020 strengthens the Marketplace/direct-purchase estimates;
- the estimates are in the expected direction for ARPA affordability.

But the screen does not yet clear the causal bar:

- the uninsured effect is weaker than the Marketplace/direct-purchase effect;
- within-year timing is mixed, especially for April-September;
- UI receipt in 2021 is not quasi-random;
- SIPP observes UI receipt and coverage, not actual APTC determination or plan selection;
- the special UI subsidy was temporary and embedded in broader ARPA enhanced PTCs, Marketplace SEP,
  pandemic labor-market disruption, and Medicaid continuous coverage.

## Recommendation

Keep as a **conditional ARPA extension**, not a standalone lead.

Best use:

1. If the ARPA 400% FPL paper continues, add this as an additional individual-level ARPA
   affordability margin.
2. Re-estimate around first UI receipt/event month, separating pre-UI, UI-month, and post-UI
   coverage transitions.
3. Focus on direct-purchase / Marketplace uptake, not uninsured as the only primary outcome.
4. Test heterogeneity for people without Medicaid, without current private coverage, and above 138%
   FPL.
5. Do not present this as clean top-field causal evidence unless stronger event-time diagnostics
   solve the 2021 labor-market confounding problem.

## Updated Ranking

1. ARPA 400% FPL cliff removal: still most novel and closest to a threshold-based top-field design.
2. Late Medicaid expansion 100-138% FPL: strongest empirical signal, but literature gap is harder.
3. ARPA UI Marketplace subsidy: plausible new ARPA extension with visible Marketplace signal, but
   causal identification is weaker.
4. Medicare age-65 / older-adult Marketplace bridge: very clean threshold, weaker novelty.
5. IRA Medicare insulin cap: policy-hot, but SIPP no-go because measurement is too indirect.
6. Public charge / immigrant chilling effect: data-unlocked, but DDD signal not clean.
7. Georgia Pathways / work requirement: policy-hot, but SIPP support is too thin.
