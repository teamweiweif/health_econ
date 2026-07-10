# Current SIPP Idea Portfolio Ranking

## Status

`ARPA400 REMAINS LEAD; ARPA100-150 IS BACKUP ONLY`

This portfolio update reflects the current non-unwinding, non-child SIPP idea search.

## Rank 1: ARPA 400% FPL Subsidy-Cliff Removal

Verdict:

`CONDITIONAL GO / CURRENT LEAD`

Question:

**Did ARPA's removal of the ACA Marketplace 400% FPL subsidy cliff reduce uninsurance near the threshold?**

Why it remains the lead:

- Real federal threshold.
- Current policy relevance from 2026 enhanced-PTC expiration.
- Stronger quasi-experimental flavor: local difference-in-discontinuities around 400% FPL.
- Large support: 215,972 person-months, 23,888 persons, 52 state clusters.
- Main uninsured coefficient: -0.0277.
- Main uninsured result is negative in 5/5 bandwidth checks.
- Pre-ARPA fake-policy checks at 400% are near zero.
- Mechanism evidence is strongest among lagged non-employer adults: `market_or_subsidy` +0.0739.

Why it is still conditional:

- Full-sample employer-related source also rises.
- Annual-FPL mechanism is weak.
- Placebo thresholds are not empty.
- Premium/age gradient does not validate a clean premium-cliff mechanism.

Best framing:

> A coverage-affordability paper using ARPA's removal of the ACA 400% FPL subsidy cliff as a national local-threshold shock, with mechanism evidence concentrated among adults not coming from employer-related coverage.

Key artifacts:

- `sipp/report/90_arpa_400fpl_specification_lock_and_identification_memo.md`
- `sipp/report/92_arpa_400fpl_paper_section_draft.md`
- `sipp/result/idea_scan/arpa400_manuscript_package/README.md`

## Rank 2: ARPA 100-150% FPL Zero-Premium Margin in Non-Expansion States

Verdict:

`BACKUP ONLY / WEAK CONDITIONAL`

Question:

**Did ARPA's zero-premium / near-zero-premium Marketplace environment improve coverage among 100-150% FPL adults in non-expansion states?**

Why it is policy-relevant:

- CMS states many 100-150% FPL consumers would have $0 premium plans after ARPA.
- The 2026 enhanced-PTC expiration debate directly revisits loss of zero-premium or near-zero-premium Marketplace coverage.
- Non-expansion states have high uninsurance and a salient Marketplace eligibility channel for low-income adults.

Why it is weaker empirically:

- Raw non-expansion 100-150 pattern is favorable:
  - uninsured: 39.8% to 33.4%;
  - market/subsidy: 16.3% to 21.4%.
- But stricter models are weak:
  - DDD uninsured: -0.0085, state t -0.29;
  - DDD market/subsidy: +0.0099, state t +0.31;
  - non-expansion local 150 uninsured: +0.0600, state t +1.14;
  - non-expansion local 150 market/subsidy: -0.0148, state t -0.56.
- The 150% threshold design does not show the expected coverage gain or direct-market uptake.
- Expansion-state and 150-200% controls are contaminated by Medicaid eligibility and broader ARPA subsidy changes.

Best framing if retained:

> A descriptive/backup policy screen showing that non-expansion 100-150% FPL adults improved in raw coverage after ARPA, but not enough quasi-experimental support for a main paper.

Key artifacts:

- `sipp/report/97_arpa_100150_nonexpansion_screen.md`
- `sipp/report/98_fortyfirst_round_arpa_100150_nonexpansion_decision.md`
- `sipp/result/idea_scan/arpa100150_nonexpansion_estimates.csv`
- `sipp/result/idea_scan/arpa100150_nonexpansion_support.csv`

## Rank 3: Premium-Exposure Heterogeneity for ARPA400

Verdict:

`APPENDIX DIAGNOSTIC / NOT A PROMOTION`

This is not a separate paper idea. It is a mechanism diagnostic for Rank 1.

Findings:

- Continuous premium burden supports uninsured reduction somewhat: -0.0146, state t -2.08.
- Binary high-premium states do not support the mechanism.
- Older-adult gradients do not support a headline.
- High-premium older-adult quadruple interaction moves against clean coverage gain.

Use:

- Include as a mechanism-risk appendix.
- Do not use to claim a clean premium-cliff Marketplace channel.

Key artifact:

- `sipp/report/96_fortieth_round_arpa400_premium_exposure_extension_status.md`

## Dropped / Not Prioritized

### 2023 ACA family-glitch fix

Status:

`NO-GO AS MAIN SIPP IDEA`

Reason:

- The policy is real and important, but current SIPP lacks the statutory exposure variables: employer offer, employee-only premium contribution, family premium contribution, and exact family-member affordability status.
- Broad family-exposure models show some direct-market/exchange movement, but also an uninsured increase.
- The premium-burden refinement is closer to the true mechanism but too thin and not mechanism-clean:
  - actual 2022->2023 high-burden at-risk pairs at the 9.12% cutoff: 74;
  - direct-market transition +0.0203, person t 0.56;
  - exchange/subsidy proxy -0.0114, person t -0.47;
  - uninsured -0.0432, person t -2.90;
  - employer-related private +0.0603, person t 1.74.

Use:

- Keep as a documented future-data idea, not a main paper.

Key artifact:

- `sipp/report/100_family_glitch_current_no_go_decision.md`

### Arkansas work requirements

Status:

`NO-GO FOR SIPP`

Reason:

- Policy relevance is strong, but treated SIPP cell is too small.
- Prior screen found about 979 person-months in the key Arkansas work-requirement period cell and only about 109 Medicaid months.

### 138% FPL Medicaid-Marketplace cliff after ARPA

Status:

`NOT PRIORITIZED`

Reason:

- Concept is good, but first SIPP screen near the 138% boundary did not show a clean post-ARPA narrowing pattern.

## Current Recommendation

Proceed with Rank 1 only as the main paper candidate.

Use Rank 2 as a short backup note or policy-motivation robustness paragraph, not as a second main manuscript.

Do not return to unwinding or child continuous eligibility in this goal thread.
