# Twenty-Fifth Round Decision: Georgia Pathways / Medicaid Work Requirement

## Decision

Status: **NO-GO FOR MAIN SIPP CAUSAL PAPER; useful as a policy-relevance sidebar only.**

Georgia Pathways is an excellent current policy question, but the current SIPP support and timing do
not justify a top-field causal paper.

The key finding is not that Pathways increased Medicaid coverage. In the SIPP screen, Georgia's
target group shows no detectable Medicaid gain after launch. In several specifications the estimated
effect is negative, with uninsurance rising in annual-FPL and local-bandwidth specifications.

That result is consistent with external policy reports saying Pathways enrolled far fewer adults
than expected, but SIPP is not the right primary dataset for a rigorous evaluation because:

1. only one treated state;
2. only six observed post-launch months in current public SIPP;
3. very small Georgia post-launch target cells;
4. overlap with the 2023 Medicaid administrative environment;
5. inability to observe actual Pathways application, verification, or enrollment status.

## Why This Was Worth Testing

Georgia Pathways is the only active state-level experience conditioning Medicaid eligibility at
application on a work / qualifying activity requirement. That makes it directly relevant to the
2026-2027 national Medicaid work-requirement debate.

External source checks:

- Georgia Pathways official eligibility pages say the program covers adults age 19-64 with income up
  to 100% FPL who complete at least 80 hours of qualifying activities per month.
- KFF says Georgia is the only state with experience conditioning Medicaid eligibility at application
  on meeting work requirements.
- KFF also reports that after 18 months, Georgia enrolled only about 7,000 people, far below its own
  projected 25,000 adults in the first year and 64,000 over five years.
- KFF Health News reports that Pathways launched in July 2023 and had just over 8,000 enrollees by
  the end of June after more than 100,000 applications.

So the policy question is very live. The problem is the SIPP design.

## Script And Outputs

Script:

- `sipp/script/11_idea_scan/32_georgia_pathways_work_requirement_test.py`

Report:

- `sipp/report/65_georgia_pathways_work_requirement_test.md`

Outputs:

- `sipp/result/idea_scan/georgia_pathways_estimates.csv`
- `sipp/result/idea_scan/georgia_pathways_support.csv`
- `sipp/result/idea_scan/georgia_pathways_cell_means.csv`
- `sipp/result/idea_scan/georgia_pathways_state_support.csv`

## Design Tested

Unit:

- person-month.

Years:

- 2022-2023 only.

Treated state:

- Georgia.

Control states:

- never-expansion comparison states without full ACA expansion during the period.

Main sample:

- adults age 19-64;
- non-Medicare;
- 0-200% monthly FPL.

Target group:

- <=100% FPL.

Comparison income group:

- 100-200% FPL.

Main term:

```text
Georgia x post-July-2023 x <=100% FPL
```

Fixed effects and controls:

- state fixed effects;
- calendar year-month fixed effects;
- FPL quadratic;
- age quadratic;
- sex, Black, Hispanic, disability;
- work-activity proxy.

Inference:

- state-clustered and person-clustered standard errors.

## Support

Main monthly-FPL support:

- Full estimation sample: 36,376 person-months, 3,267 persons, 10 states.
- Georgia target <=100% FPL: 2,149 person-months, 231 persons.
- Georgia post-launch target: 494 person-months, 92 persons.
- Georgia post-launch target Medicaid months: 129.
- Georgia post-launch target uninsured months: 191.
- Georgia post-launch target work-activity-proxy months: 155.

Work-activity proxy sample:

- Georgia post-launch target: 155 person-months, 35 persons.
- Medicaid months: 38.
- Uninsured months: 52.

Local 50-150% FPL sample:

- Georgia post-launch target: 177 person-months, 38 persons.
- Medicaid months: 66.
- Uninsured months: 83.

These cells are too small for a convincing single-state causal design.

## Raw Pattern

In Georgia target adults <=100% monthly FPL:

- Medicaid: 28.1% pre -> 23.9% post.
- Uninsured: 43.2% pre -> 41.7% post.
- Any coverage: 56.8% pre -> 58.3% post.
- Private coverage: 32.7% pre -> 34.4% post.
- SNAP monthly: 28.9% pre -> 15.0% post.

This does not look like a meaningful Medicaid expansion in SIPP.

## Main Estimates

Monthly FPL 0-200%, post July 2023:

- Medicaid: -4.6 pp, state-clustered t = -1.49; person-clustered t = -0.67.
- Uninsured: -3.3 pp, state-clustered t = -0.82; person-clustered t = -0.41.
- Any coverage: +3.3 pp, state-clustered t = 0.82; person-clustered t = 0.41.
- Public coverage: -3.3 pp, state-clustered t = -0.83; person-clustered t = -0.49.
- SNAP monthly: -10.4 pp, state-clustered t = -7.50; person-clustered t = -1.79.

Post-September sensitivity:

- Medicaid: -4.6 pp, state-clustered t = -1.68.
- Uninsured: -6.8 pp, state-clustered t = -1.59.
- Any coverage: +6.8 pp, state-clustered t = 1.59.
- SNAP monthly: -9.1 pp, state-clustered t = -6.04.

Work-activity proxy sample:

- Medicaid: -4.6 pp, state-clustered t = -1.40.
- Uninsured: +4.5 pp, state-clustered t = 1.20.
- Any coverage: -4.5 pp, state-clustered t = -1.20.

Annual-FPL sensitivity:

- Medicaid: -8.1 pp, state-clustered t = -3.35; person-clustered t = -1.13.
- Uninsured: +7.6 pp, state-clustered t = 3.09; person-clustered t = 0.94.
- Any coverage: -7.6 pp, state-clustered t = -3.09.
- Public coverage: -7.8 pp, state-clustered t = -3.10.

Local 50-150% FPL sensitivity:

- Medicaid: -14.4 pp, state-clustered t = -3.08; person-clustered t = -1.22.
- Uninsured: +21.0 pp, state-clustered t = 3.10; person-clustered t = 1.61.
- Any coverage: -21.0 pp, state-clustered t = -3.10.
- Public coverage: -12.8 pp, state-clustered t = -2.54.

## Interpretation

This is not a positive coverage-expansion result.

The strongest interpretation is:

> In SIPP, Georgia Pathways does not produce a detectable Medicaid coverage gain among adults who
> should be income-eligible. Some specifications are consistent with coverage loss or failure to
> enroll, but the design is too weak to make a causal claim.

This matches the policy narrative that administrative complexity limited enrollment, but it is not a
standalone causal paper.

The SNAP decline is large, but it should not be over-interpreted. It may reflect broader Georgia
administrative conditions, state benefit-processing issues, or sample composition. It is not a clean
Pathways mechanism.

## Go / No-Go

**No-go as a main SIPP causal paper.**

Possible uses:

1. Short policy sidebar in a broader Medicaid work-requirement review.
2. Descriptive SIPP check showing no population-level Medicaid increase among Georgia low-income
   adults in the first six observed post-launch months.
3. Motivation for using administrative data rather than SIPP to evaluate Pathways.

Do not rank this above ARPA 400% FPL or late Medicaid expansion.

## Updated Ranking

1. ARPA 400% FPL cliff removal: still most novel, conditional due to mechanism diagnostics.
2. Late Medicaid expansion 100-138% FPL: strongest empirical signal, but literature gap is harder.
3. Public charge / immigrant chilling effect: data-unlocked, but first DDD not clean.
4. Georgia Pathways / work requirement: policy-hot but SIPP no-go for main causal design.
