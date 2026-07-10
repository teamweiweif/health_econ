# SIPP Adult Idea Search Evidence Map

## Status

`ONE LEAD, ONE WEAK BACKUP, MANY DOCUMENTED NO-GO / DIAGNOSTIC IDEAS`

This memo consolidates the non-unwinding, non-child SIPP idea search. It is meant to prevent repeated rescue attempts on ideas that already failed support, mechanism, or identification checks.

## Evaluation Standard

Each idea was judged on five dimensions:

1. Current policy relevance.
2. Literature gap / publication angle.
3. Clean identifying variation.
4. SIPP observability of treatment, exposure, and outcomes.
5. Empirical support and mechanism direction.

The current goal is not a descriptive SIPP report. The goal is a directly workable adult policy paper with a credible causal design and a real current policy gap.

## Final Ranking

### Rank 1. ARPA 400% FPL Subsidy-Cliff Removal

Verdict:

`CURRENT LEAD / CONDITIONAL GO`

Question:

**Did ARPA's removal of the ACA Marketplace 400% FPL subsidy cliff reduce uninsurance near the threshold?**

Why it leads:

- Federal threshold is real and national.
- Current 2026 enhanced-PTC expiration debate makes the subsidy cliff live again.
- Design has a strong quasi-experimental shape: local difference-in-discontinuities around 400% FPL.
- SIPP observes monthly uninsurance, any coverage, direct purchase, Marketplace/subsidy proxies, and employer-related source coverage.
- Main support is large: 215,972 person-months, 23,888 persons, 52 state clusters.
- Main uninsured estimate: -0.0277, person SE 0.0141, state SE 0.0151.
- Main uninsured effect is negative in all five bandwidth checks.
- Pre-ARPA fake-policy tests at 400% FPL are near zero.
- Lagged non-employer mechanism sample has `market_or_subsidy` +0.0739, person t 2.25, state t 2.11.

Why still conditional:

- Full-sample employer-related source also rises.
- Annual-FPL mechanism evidence is weak.
- Nearby placebo thresholds are not empty.
- Premium/age gradients do not validate a clean premium-cliff mechanism.

Use:

- Main paper candidate.
- Frame as coverage-affordability, not pure Marketplace enrollment.

Key artifacts:

- `sipp/report/90_arpa_400fpl_specification_lock_and_identification_memo.md`
- `sipp/report/92_arpa_400fpl_paper_section_draft.md`
- `sipp/result/idea_scan/arpa400_manuscript_package/README.md`

### Rank 2. Late Medicaid Expansion Threshold Design

Verdict:

`EMPIRICAL GO / PUBLICATION-GAP CONDITIONAL BACKUP`

Question:

**In late-expanding states, did expansion move 100-138% FPL adults from uninsurance or Marketplace/direct-purchase paths into Medicaid?**

Strength:

- Strong first-stage and coverage signal.
- Narrow 100-250% monthly-FPL design, treated eligibility band 100-138% FPL.
- Medicaid +8.9 pp, state t 3.04.
- Uninsured -7.4 pp, state t -4.80.
- Annual-FPL robustness directionally consistent.

Why not lead:

- Generic Medicaid expansion literature is large.
- Uninsured placebo/pretrend is mixed: fake pre-period uninsured -5.4 pp, state t -1.77.
- Needs a narrower SIPP-specific contribution around monthly coverage paths and late adopters.

Use:

- Best empirical backup if ARPA400 becomes too fragile.

Key artifact:

- `sipp/report/62_twentythird_round_late_medicaid_expansion_decision.md`

### Rank 3. Medicare Age-65 Threshold / Older-Adult Marketplace Bridge

Verdict:

`EMPIRICALLY CLEAN / CONDITIONAL BACKUP ONLY`

Question:

**Did the ARPA-era Marketplace environment change the pre-65 side of the Medicare age-65 transition?**

Strength:

- Clean age threshold.
- Large sample: 644,849 person-months ages 60-70.
- Medicare jumps by about 50.8 pp at age 65.
- Uninsurance falls by about 4.7 pp.
- Direct purchase and Marketplace flags fall sharply at 65.

Why not lead:

- Standard Medicare-at-65 RD is not novel.
- ARPA-era discontinuity change is mostly compositional, not a strong uninsured effect.

Use:

- Methodological benchmark or backup, not first lead.

Key artifact:

- `sipp/report/68_twentysixth_round_medicare_age65_decision.md`

### Rank 4. ARPA UI Marketplace Subsidy

Verdict:

`CONDITIONAL ARPA EXTENSION / NOT FIRST LEAD`

Question:

**Did ARPA's special 2021 Marketplace subsidy rule for unemployment-compensation recipients increase Marketplace/direct-purchase coverage or reduce uninsurance?**

Strength:

- SIPP observes UI receipt and coverage outcomes.
- UI-year recipients show a large raw 2021 direct-purchase / Marketplace jump.
- Excluding 2020, direct purchase +3.94 pp, person t 2.06; market/subsidy +3.81 pp, person t 1.99.

Why not lead:

- UI receipt in 2021 is heavily confounded by pandemic labor-market shocks and UI program changes.
- Within-year timing tests are mixed.
- The effect is not as clean as the 400% FPL threshold.

Use:

- Possible ARPA appendix/extension.

Key artifact:

- `sipp/report/71_twentyseventh_round_arpa_ui_marketplace_decision.md`

### Rank 5. ARPA 100-150% FPL Zero-Premium Margin in Non-Expansion States

Verdict:

`BACKUP ONLY / WEAK CONDITIONAL`

Question:

**Did ARPA's zero-premium Marketplace environment improve coverage among 100-150% FPL adults in non-expansion states?**

Strength:

- Policy-relevant, especially after enhanced-PTC expiration.
- Raw non-expansion 100-150 pattern is favorable:
  - uninsured: 39.8% to 33.4%;
  - market/subsidy: 16.3% to 21.4%.

Why weak:

- DDD uninsured: -0.0085, state t -0.29.
- DDD market/subsidy: +0.0099, state t +0.31.
- Non-expansion local 150 uninsured: +0.0600, state t +1.14.
- Non-expansion local 150 market/subsidy: -0.0148, state t -0.56.

Use:

- Background/descriptive backup only.

Key artifact:

- `sipp/report/98_fortyfirst_round_arpa_100150_nonexpansion_decision.md`

### Rank 6. Low-Income 150% FPL Marketplace SEP

Verdict:

`POLICY-RELEVANT BUT FRAGILE / APPENDIX ONLY`

Question:

**Did the 2022 150% FPL low-income Marketplace SEP increase off-season Marketplace coverage?**

Strength:

- Current policy debate around enrollment frictions and SEP rules.
- Narrow no-Medicaid sample has Marketplace flag +9.47 pp, state t 1.93.

Why not lead:

- Main sample effect is weak.
- Broad 100-150% no-Medicaid sensitivity does not replicate.
- HealthCare.gov versus SBM treatment contrast is imperfect.
- SIPP does not observe SEP use.

Key artifact:

- `sipp/report/73_twentyeighth_round_low_income_sep_decision.md`

## Mechanism Diagnostic, Not Separate Lead

### ARPA400 Premium-Exposure Heterogeneity

Verdict:

`APPENDIX DIAGNOSTIC / NOT A PROMOTION`

Use:

- Mechanism-risk evidence for ARPA400.

Findings:

- Continuous premium burden gives one supportive uninsured gradient: -0.0146, state t -2.08.
- Binary high-premium state interactions do not support a clean mechanism.
- Older-adult gradients do not support a headline.
- High-premium older-adult interaction moves against clean coverage gain.

Key artifact:

- `sipp/report/96_fortieth_round_arpa400_premium_exposure_extension_status.md`

## No-Go / Dropped Insurance Ideas

### 2023 ACA Family-Glitch Fix

Verdict:

`NO-GO AS MAIN SIPP IDEA`

Reason:

- Policy is real, but current SIPP lacks employer offer, employee-only premium, family premium contribution, and exact family-member affordability status.
- Broad family exposure shows some exchange/subsidy movement but also uninsured increase.
- Premium-burden refinement is closest to the mechanism but too thin: 74 actual 2022->2023 high-burden at-risk pairs at 9.12% cutoff.
- Direct-market transition +0.0203, person t 0.56; exchange/subsidy -0.0114, person t -0.47.

Key artifact:

- `sipp/report/100_family_glitch_current_no_go_decision.md`

### Arkansas Medicaid Work Requirements

Verdict:

`NO-GO FOR CURRENT SIPP MAIN PAPER`

Reason:

- Policy relevance is strong.
- Treated SIPP cell is too small.
- Key Arkansas work-requirement period has about 979 person-months and only about 109 Medicaid months.

Key artifact:

- `sipp/report/49_seventeenth_round_arkansas_work_requirement_decision.md`

### Georgia Pathways / Medicaid Work Requirement

Verdict:

`NO-GO FOR MAIN SIPP CAUSAL PAPER`

Reason:

- Policy-hot but too little SIPP support for a main causal design.
- Best use is policy-relevance sidebar.

Key artifact:

- `sipp/report/66_twentyfifth_round_georgia_pathways_decision.md`

### ARPA COBRA Premium Subsidy

Verdict:

`NO-GO AS MAIN SIPP PAPER`

Reason:

- SIPP can observe former-employer/private source proxies but not clean COBRA eligibility and take-up.
- Too thin and too indirect as standalone.

Key artifact:

- `sipp/report/75_twentyninth_round_arpa_cobra_decision.md`

### STLDI State Regulation

Verdict:

`NO-GO FROM CURRENT SIPP`

Reason:

- SIPP does not separately identify short-term limited-duration insurance.
- Any effect would be mixed into direct-purchase or other private coverage.

Key artifact:

- `sipp/report/29_seventh_round_family_glitch_stldi_decision.md`

### ACA Reinsurance

Verdict:

`DIRECTIONAL INSURANCE SIGNAL, BUT NO CLEAN GO`

Reason:

- State policy variation is plausible, but effects are not clean enough in SIPP.
- Requires better premium-reduction/pass-through intensity to be useful.

Key artifact:

- `sipp/report/47_sixteenth_round_aca_reinsurance_decision.md`

### State Marketplace Subsidies

Verdict:

`NO CLEAN IMMEDIATE GO`

Reason:

- Potentially relevant state policy variation.
- Current public SIPP design lacks clean timing/intensity and sufficient mechanism clarity.

Key artifact:

- `sipp/report/27_sixth_round_state_subsidy_decision.md`

### Public Charge / Immigrant Chilling Effect

Verdict:

`TOPICAL BUT NOT CLEAN FROM CURRENT PACKAGE`

Reason:

- Policy question is important and potentially novel.
- Requires raw-variable extraction for citizenship/nativity and stronger DDD design.
- Existing DDD signal was not clean enough.

Key artifact:

- `sipp/report/64_twentyfourth_round_public_charge_decision.md`

### IRA Medicare Insulin Cap

Verdict:

`NO-GO / MEASUREMENT TOO INDIRECT`

Reason:

- Policy-hot, but SIPP does not observe insulin use or Part D plan exposure cleanly enough for a causal coverage paper.

Key artifact:

- `sipp/report/69_ira_insulin_medicare_fast_test.md`

### Student Loan Repayment Resumption

Verdict:

`NO-GO AS MAIN SIPP HEALTH-INSURANCE PAPER`

Reason:

- True repayment exposure is not cleanly observed.
- Health-insurance causal interpretation is too indirect.

Key artifact:

- `sipp/report/79_thirtyfirst_round_student_loan_repayment_decision.md`

## Non-Insurance / Out-Of-Scope Adult Screens

These were tested during broad SIPP exploration but are not current health-insurance paper leads:

- SNAP Emergency Allotment termination: conditional lead in food-security direction, but outside the current insurance-paper target.
- Minimum wage food-security spillover: large support, no clean go.
- Washington Working Families Tax Credit: no-go.
- Paid sick leave: no-go from compact SIPP.
- Pandemic UI food-security / early termination: no-go.

These should not displace the ARPA400 insurance lead in this goal thread.

## Current Recommendation

Proceed with:

1. **ARPA400 as the only main manuscript candidate.**
2. **Late Medicaid expansion as the empirical backup if ARPA400 fails.**
3. **Medicare age-65 as a clean-design benchmark, not a first lead.**
4. **ARPA100-150 and low-income SEP only as policy-background or appendix screens.**

Do not spend more time trying to rescue family glitch, Arkansas, Georgia Pathways, COBRA, STLDI, or student-loan repayment with current SIPP.

## Web GPT Upload Recommendation

For external critique, upload:

- `sipp/report/101_sipp_adult_idea_search_evidence_map.md`
- `sipp/report/99_current_sipp_idea_portfolio_ranking.md`
- `sipp/report/92_arpa_400fpl_paper_section_draft.md`
- `sipp/report/90_arpa_400fpl_specification_lock_and_identification_memo.md`
- `sipp/result/idea_scan/arpa400_manuscript_package/README.md`
- `sipp/result/idea_scan/sipp_adult_idea_evidence_map.csv`

Ask the external reviewer to challenge the ranking and decide whether ARPA400 should proceed to manuscript drafting or whether late Medicaid expansion is a more defensible backup.
