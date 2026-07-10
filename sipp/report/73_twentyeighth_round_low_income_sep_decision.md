# Twenty-Eighth Round Decision: 150% FPL Low-Income Marketplace SEP

## Decision

Status: **POLICY-RELEVANT BUT NOT A CLEAN SIPP GO; APPENDIX/BACKUP ONLY**.

This is a legitimate new idea and should be preserved in the idea inventory, but it should not
replace the ARPA 400% FPL cliff lead or the late Medicaid expansion backup.

The screen found one interesting signal:

- among non-Medicaid adults in the narrow 138-150% FPL target window, HealthCare.gov states had a
  post-2022 Marketplace-flag increase of about +9.5 pp relative to stable SBM states and 150-200%
  FPL controls.

But the signal does not survive a broader policy-consistent sensitivity using 100-150% FPL
non-Medicaid adults. That broader test has much better support and shows no clean Marketplace
increase. The result is therefore too fragile for a main causal paper.

## Policy Question

Did the 2022 low-income monthly Marketplace Special Enrollment Period for people at or below 150%
FPL increase off-season Marketplace/direct-purchase coverage among low-income adults?

The question is current and real:

- CMS announced HealthCare.gov online functionality for the 150% FPL SEP in March 2022.
- KFF explains the SEP as a year-round enrollment opportunity for low-income Marketplace-eligible
  people.
- CMS 2026-2027 rulemaking again discusses removing or continuing to prohibit the 150% FPL SEP
  after enhanced subsidy changes.

This is attractive because the current 2026 policy debate is not only about subsidy generosity; it
is also about enrollment frictions, broker behavior, adverse selection, and whether low-income
consumers should have a year-round enrollment pathway.

## New Artifacts

Script:

- `sipp/script/11_idea_scan/36_low_income_sep_150fpl_test.py`

Report:

- `sipp/report/72_low_income_sep_150fpl_test.md`

Outputs:

- `sipp/result/idea_scan/low_income_sep_150fpl_estimates.csv`
- `sipp/result/idea_scan/low_income_sep_150fpl_support.csv`
- `sipp/result/idea_scan/low_income_sep_150fpl_raw_cells.csv`

## Design Tested

Unit:

- person-month.

Main sample:

- adults ages 26-64;
- non-Medicare;
- monthly FPL 138-200%;
- target group 138-150% FPL;
- comparison group 150-200% FPL;
- off-season months March-October only;
- pre years 2018-2019 and post years 2022-2023;
- 2020 and 2021 excluded because they contain pandemic disruption, COVID SEP, and broad ARPA
  rollout;
- overlapping SBM transition states excluded: Kentucky, Maine, New Jersey, New Mexico,
  Pennsylvania.

Treatment contrast:

- HealthCare.gov states versus stable full State-Based Marketplace states.

Key coefficient:

- `HealthCare.gov state x 138-150% FPL target x post-2022`.

Inference:

- state-clustered and person-clustered standard errors saved;
- memo emphasizes state-clustered inference because the policy contrast is state/platform-level.

## Support

Main narrow threshold sample:

- 47,048 person-months;
- 8,208 persons;
- 47 states.

Target-post support:

- HealthCare.gov target-post cell: 2,361 person-months, 600 persons.
- stable SBM target-post cell: 1,085 person-months, 286 persons.

No-Medicaid sensitivity:

- 34,128 person-months;
- 6,086 persons.

Broad 100-150% FPL no-Medicaid sensitivity:

- 49,823 person-months;
- 8,104 persons;
- HealthCare.gov target-post cell: 6,299 person-months, 1,199 persons;
- stable SBM target-post cell: 1,900 person-months, 422 persons.

Support is adequate for screening. The issue is not a tiny sample; it is robustness and design
purity.

## Main Results

Main 138-150% FPL target sample:

- uninsured: -2.78 pp, state-clustered t = -0.82;
- direct purchase: +2.21 pp, state-clustered t = 0.38;
- Marketplace flag: +1.54 pp, state-clustered t = 0.31;
- subsidized private: +5.09 pp, state-clustered t = 1.14;
- market/subsidy composite: +1.74 pp, state-clustered t = 0.29.

No-Medicaid narrow target sensitivity:

- uninsured: -1.97 pp, state-clustered t = -0.36;
- direct purchase: +9.04 pp, state-clustered t = 1.50;
- Marketplace flag: +9.47 pp, state-clustered t = 1.93;
- market/subsidy composite: +9.04 pp, state-clustered t = 1.50.

Broad 100-150% FPL no-Medicaid sensitivity:

- uninsured: +3.63 pp, state-clustered t = 0.52;
- direct purchase: +3.28 pp, state-clustered t = 0.59;
- Marketplace flag: -0.85 pp, state-clustered t = -0.21;
- market/subsidy composite: +3.28 pp, state-clustered t = 0.59.

## Interpretation

There is a plausible mechanism signal in the narrow no-Medicaid sample, but it is too fragile:

- the main sample does not show a clear Marketplace/direct-purchase effect;
- the broad no-Medicaid sensitivity does not replicate the Marketplace increase;
- the 138-150% FPL window is small and hard to cleanly separate from Medicaid eligibility near
  138% FPL;
- HealthCare.gov versus SBM is an imperfect treatment contrast because SBMs may have parallel
  low-income SEP policies, different outreach, and different broker/enrollment dynamics;
- SIPP observes coverage status but not whether a person used the 150% FPL SEP.

The right interpretation is not "policy did nothing." It is:

> SIPP can see some low-income Marketplace movement around this policy, but the current
> state-platform DDD is not clean enough for a lead causal paper.

## Recommendation

Do not lead with this design.

Keep it as:

1. an appendix/extension in a broader ARPA Marketplace affordability paper;
2. a policy-background contrast for the 400% FPL cliff project;
3. a possible future design if state-level SEP adoption/implementation dates by SBM can be coded
   precisely and paired with stronger external Marketplace administrative enrollment data.

If revisited, the next test should not simply rerun the same DDD. It should:

- hand-code which SBMs adopted equivalent 150% FPL SEP rules and when;
- focus on off-season entry among people with no private coverage in the previous month;
- use event-time around March 2022 for HealthCare.gov states;
- separate Marketplace uptake from Medicaid/Public coverage transitions;
- treat the broad 100-150% FPL no-Medicaid null as a real warning.

## Updated Ranking

1. ARPA 400% FPL cliff removal: still the best novelty/design combination.
2. Late Medicaid expansion 100-138% FPL: strongest empirical signal, literature gap harder.
3. ARPA UI Marketplace subsidy: visible Marketplace/direct-purchase signal but weaker
   identification.
4. Medicare age-65 / older-adult Marketplace bridge: clean threshold, weaker novelty.
5. 150% FPL low-income Marketplace SEP: current policy gap, but fragile SIPP evidence.
6. IRA Medicare insulin cap: policy-hot, but SIPP measurement is too indirect.
7. Public charge / immigrant chilling effect: data-unlocked, but DDD signal not clean.
8. Georgia Pathways / work requirement: policy-hot, but SIPP support is too thin.
