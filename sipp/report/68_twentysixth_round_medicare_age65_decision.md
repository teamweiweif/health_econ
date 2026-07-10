# Twenty-Sixth Round Decision: Medicare Age-65 Threshold / Older-Adult Marketplace Bridge

## Decision

Status: **EMPIRICALLY CLEAN BUT NOT FIRST-LEAD; CONDITIONAL BACKUP ONLY**.

The age-65 Medicare threshold is the cleanest statistical design tested in this round. The first
stage is enormous, outcomes move in expected directions, and SIPP has enough support for precise
age-window estimation.

The problem is novelty. A standard "Medicare eligibility at age 65 reduces uninsurance" paper is
not new. The only plausible contribution is narrower:

> In the recent ACA/ARPA Marketplace era, did enhanced Marketplace subsidies change the pre-65 side
> of the Medicare age-65 transition, especially direct-purchase / Marketplace reliance among adults
> ages 60-64?

That framing is current and policy-relevant, but it is a backup, not a replacement for the ARPA
400% FPL lead or the late-Medicaid-expansion backup.

## Why This Is Policy-Relevant

External source checks:

- KFF discusses proposals to lower Medicare eligibility to 60 and notes that a policy lowering the
  eligibility age could shift millions of people with employer or nongroup coverage into Medicare.
- KFF's 2026 older-adult Marketplace analysis says adults ages 50-64 are disproportionately affected
  by the expiration of enhanced premium tax credits because Marketplace premiums rise with age.
- CBO estimated that lowering Medicare eligibility to age 60 would increase federal deficits by
  $155 billion over 2026-2031 and materially change sources of insurance coverage.
- The 2026 Medicare handbook says Marketplace enrollees should sign up for Medicare when first
  eligible and that once eligible for premium-free Part A, they no longer qualify for Marketplace
  help paying premiums or other medical costs.

So the policy bridge is real: older pre-Medicare adults face expensive Marketplace/non-group
coverage, and Medicare eligibility creates a hard institutional transition at age 65.

## Script And Outputs

Script:

- `sipp/script/11_idea_scan/33_medicare_age65_threshold_test.py`

Report:

- `sipp/report/67_medicare_age65_threshold_test.md`

Outputs:

- `sipp/result/idea_scan/medicare_age65_estimates.csv`
- `sipp/result/idea_scan/medicare_age65_support.csv`
- `sipp/result/idea_scan/medicare_age65_age_bins.csv`
- `sipp/result/idea_scan/medicare_age65_prepost_cells.csv`
- `sipp/result/idea_scan/medicare_age65_fpl_prepost_support.csv`

## Design Tested

Unit:

- person-month.

Running variable:

- `TAGE_EHC`, monthly age during the reference year.

Threshold:

- `age >= 65`.

Windows:

- ages 60-70;
- ages 62-68.

Models:

1. Pooled age-65 local-linear RD.
2. RD-DID using `age >= 65 x post_2021_2023` to ask whether the age-65 discontinuity changed after
   ARPA-enhanced Marketplace subsidies.

Controls and fixed effects:

- calendar year-month fixed effects;
- FPL;
- sex, Black, Hispanic, disability.

Inference:

- person-clustered standard errors.

## Support

Age 60-70:

- 644,849 person-months.
- 29,792 persons.
- 303,254 person-months below 65.
- 341,595 person-months at/above 65.

Age 62-68:

- 414,962 person-months.
- 21,068 persons.
- 182,945 person-months below 65.
- 232,017 person-months at/above 65.

This is not a support problem.

## Pooled RD Result

Age 60-70:

- Medicare: +50.8 pp, person-clustered t = 68.0.
- Uninsured: -4.7 pp, person-clustered t = -11.5.
- Any coverage: +4.7 pp, person-clustered t = 11.5.
- Public coverage: +43.3 pp, person-clustered t = 53.3.
- Private coverage: -8.2 pp, person-clustered t = -10.0.
- Direct purchase: -5.7 pp, person-clustered t = -7.6.
- Marketplace flag: -6.7 pp, person-clustered t = -11.1.
- OOP > $1,000: -2.2 pp, person-clustered t = -2.9.

Age 62-68:

- Medicare: +40.5 pp, person-clustered t = 45.3.
- Uninsured: -4.5 pp, person-clustered t = -9.1.
- Direct purchase: -4.5 pp, person-clustered t = -5.4.
- Marketplace flag: -4.8 pp, person-clustered t = -6.9.
- OOP > $1,000: -1.9 pp, person-clustered t = -2.1.

This is a very strong first-stage / coverage-path screen.

## ARPA-Era Discontinuity Change

The RD-DID result is more mixed but has one interesting mechanism:

Age 60-70, `age>=65 x post_2021_2023`:

- Medicare: -1.2 pp, person-clustered t = -0.82.
- Uninsured: +0.5 pp, person-clustered t = 0.61.
- Direct purchase: -3.4 pp, person-clustered t = -2.19.
- Marketplace flag: -1.9 pp, person-clustered t = -1.44.
- Market/subsidy: -3.4 pp, person-clustered t = -2.15.
- Private coverage: -3.6 pp, person-clustered t = -2.14.

Age 62-68:

- Uninsured: +1.6 pp, person-clustered t = 1.58.
- Direct purchase: -3.3 pp, person-clustered t = -1.83.
- Market/subsidy: -3.0 pp, person-clustered t = -1.65.

Interpretation:

- The age-65 direct-purchase / market-subsidy drop becomes larger after 2021.
- That is consistent with older pre-Medicare adults becoming more reliant on Marketplace/non-group
  coverage after ARPA, so the transition into Medicare at age 65 substitutes away from more
  Marketplace coverage.
- The uninsured discontinuity does not clearly shrink; the coverage effect is mostly compositional.

## Descriptive ARPA Pattern For Ages 60-64

Among ages 60-64:

- Uninsured fell from 8.0% pre-2021 to 6.8% post-2021.
- Market/subsidy coverage rose from 17.4% to 19.9%.

Among low-income ages 60-64:

- Uninsured fell from 13.4% to 11.5%.
- Market/subsidy coverage rose from 26.5% to 30.5%.

This is consistent with ARPA improving the pre-65 coverage environment, but not enough to create a
new headline unless mechanism checks are expanded.

## Main Limitation

The identification is strong, but the paper idea is not automatically novel.

The canonical Medicare-at-65 RD has been studied extensively. A paper based only on the pooled RD
would be a replication-style result:

> Medicare jumps at 65, uninsurance falls, direct purchase/Marketplace coverage falls, and high OOP
> spending falls.

That is useful but not a top-field gap.

The potential gap is the interaction with the modern Marketplace subsidy environment:

> ARPA made ages 60-64 more reliant on subsidized Marketplace coverage, changing the composition of
> the age-65 transition into Medicare.

That is more interesting, but this first pass does not yet show a strong enough uninsured or
affordability outcome to become a first lead.

## Recommendation

Keep this as a **conditional backup / robustness benchmark**, not a first lead.

If continued, the next pass should:

1. Focus only on ages 60-64 vs 65-67 and current Marketplace exposure.
2. Add income heterogeneity: low-income, 250-400% FPL, >400% FPL.
3. Add pre-65 direct-purchase / Marketplace baseline subgroups.
4. Test whether ARPA changed the 64-to-65 transition specifically, not all 60-70 ages.
5. Add event-time around first observed age 65 if `TAGE_EHC` increments within person correctly.
6. Treat OOP/utilization as secondary; coverage path is the main contribution.

## Updated Ranking

1. ARPA 400% FPL cliff removal: still most novel, but mechanism diagnostics are mixed.
2. Late Medicaid expansion 100-138% FPL: strongest new empirical signal, but literature gap is hard.
3. Medicare age-65 / older-adult Marketplace bridge: cleanest threshold design, but only conditional
   novelty.
4. Public charge / immigrant chilling effect: data-unlocked, but DDD not clean.
5. Georgia Pathways / work requirement: policy-hot but SIPP no-go for main causal design.
