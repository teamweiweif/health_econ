# Ninth-Round Paid Sick Leave Decision

## Question

Can the current public SIPP parquet support an adult, non-child, non-unwinding paper on state
paid sick leave mandates?

## Why This Was Worth Testing

This was a legitimate adult policy candidate because:

- paid sick leave remains a current labor and public-health policy issue;
- several states newly implemented statewide laws during the SIPP 2017-2023 reference window;
- the policy applies to working-age adults rather than children or unwinding;
- SIPP observes employment, earnings, health care visits, insurance, out-of-pocket spending, and
  `TDAYSICK`;
- a plausible target group exists among low-education or low-income workers, who are more likely to
  be marginally affected by mandates.

## Policy Source Checks

- NCSL paid sick leave summary:
  https://www.ncsl.org/labor-and-employment/paid-sick-leave
- Washington L&I paid sick leave page:
  https://www.lni.wa.gov/workers-rights/leave/paid-sick-leave/
- New York Paid Sick Leave official page:
  https://www.ny.gov/programs/new-york-paid-sick-leave
- Colorado Healthy Families and Workplaces Act:
  https://cdle.colorado.gov/sites/cdle/files/colorado_healthy_families_and_workplaces_act_revised_aug_7_2023.pdf
- Maryland Healthy Working Families Act FAQ:
  https://labor.maryland.gov/paidleave/paidleavefaqs.shtml
- New Mexico paid sick leave notice:
  https://www.dws.state.nm.us/Researchers/Publications/Economic-News/law-for-paid-sick-leave-goes-into-effect-july-2022-employers-are-encouraged-to-attend-nmdws-information-webinar

Primary clean coding used:

- Maryland: 2018.
- Washington: 2018.
- New Jersey: 2019, because the law became effective late in 2018.
- Rhode Island: 2019, because the law became effective July 2018.
- Colorado: 2021.
- New York: 2021.
- New Mexico: 2023, because the law became effective July 2022.

Broad sensitivity adds Michigan, Nevada, and Maine, but these are less clean because Michigan is
more limited and Nevada/Maine are broader earned paid-leave policies rather than classic paid sick
leave.

## Design

Source:

- `data/analysis_ready/sipp_2018_2024_person_month_panel.parquet`

Unit:

- person-year collapsed from monthly SIPP rows.

Primary sample:

- employed adults age 18-64;
- at least six observed months;
- valid education and FPL;
- reference years 2017-2023.

Primary target:

- high-school-or-less workers, `EEDUC <= 39`.

Treatment:

- clean paid sick leave adopter state x active year x target worker.

Fixed effects:

- state-year;
- state-target;
- target-year.

Main outcomes:

- `sick_days`;
- `sick_any`;
- `doctor_any`;
- `doctor_visits`;
- `uninsured`;
- `log_earnings`.

## Critical Measurement Caveat

The compact SIPP parquet does not observe paid sick leave access, accrual, availability, employer
coverage, or actual paid sick leave use.

`TDAYSICK` is not sick leave. It is the number of days illness or injury kept the person in bed more
than half the day. This means the design has no direct first stage. The test can only look for
reduced-form changes in health, care utilization, coverage, and earnings.

That is a serious limitation for a top-field causal paper.

## Support

Primary low-education worker sample:

- 123,078 person-years.
- 70,330 persons.
- 43,776 target worker person-years.
- 5,218 clean-adopter target person-years.
- 2,770 clean active treated person-years.

Low-income worker sample:

- 123,078 person-years.
- 36,063 target worker person-years.
- 2,163 clean active treated person-years.

All-adult worker-target sample:

- 174,509 person-years.
- 123,078 target worker person-years.
- 9,590 clean active treated person-years.

Support is not the main failure. The treatment cells are large enough for a quick screen.

## Main Results

Primary low-education worker DDD:

- `sick_days`: +0.6849, se 0.6808.
- `sick_any`: -0.0177, se 0.0220.
- `doctor_any`: -0.0143, se 0.0206.
- `doctor_visits`: -0.0279, se 0.3975.
- `uninsured`: +0.0088, se 0.0159.
- `log_earnings`: +0.0124, se 0.0818.

Low-income worker DDD:

- `sick_days`: -1.6482, se 0.9943.
- `sick_any`: -0.0312, se 0.0237.
- `doctor_any`: +0.0212, se 0.0220.
- `doctor_visits`: -0.2726, se 0.4699.
- `uninsured`: +0.0172, se 0.0168.
- `log_earnings`: -0.0178, se 0.1138.

All-adult worker-target DDD:

- `sick_days`: -1.3416, se 1.5211.
- `doctor_any`: -0.0048, se 0.0170.
- `uninsured`: -0.0129, se 0.0122.
- `employed_share`: -0.0045, se 0.0041.

Broad paid-leave sensitivity among low-education workers:

- `sick_days`: +0.1365, se 0.6198.
- `sick_any`: -0.0151, se 0.0189.
- `doctor_any`: +0.0032, se 0.0176.
- `uninsured`: +0.0066, se 0.0135.
- `log_earnings`: -0.0708, se 0.0697.

## Event and Leave-One Checks

Event estimates do not show a coherent policy break.

For the primary low-education worker event specification, omitting relative year -1:

- `doctor_any` is already positive in pre-period relative years -3 and -2, then near zero at event
  year 0.
- `sick_days` has mixed pre-period and post-period movement.
- `uninsured` has no meaningful post-policy pattern.

Leave-one-clean-adopter checks do not reveal a stable hidden result. Dropping Maryland, Washington,
New Jersey, Rhode Island, Colorado, New York, or New Mexico keeps the main outcomes weak or
incoherent.

## Decision

`STATE PAID SICK LEAVE: NO-GO FROM CURRENT PUBLIC SIPP PARQUET`

The policy question is real, but the current SIPP extract is not the right data product for a main
paper:

- no direct paid-sick-leave first stage is observed;
- `TDAYSICK` is a health-severity measure, not leave use;
- the primary low-education worker estimates do not show improved doctor access or a coherent
  health/utilization pattern;
- low-income worker results are directionally mixed and not robust;
- event estimates do not provide a clean visual or statistical policy break;
- broad paid-leave coding attenuates rather than clarifies the result.

This should not be pursued as the main SIPP paper unless a richer SIPP extract can recover employer
benefit/leave-access variables.

## Updated Ranking

1. **ACA enhanced PTC / 400% FPL with premium intensity**: best policy gap, but dynamic checks failed.
2. **ACA family glitch fix**: best conditional lead; current compact parquet lacks actual employer
   offer/premium eligibility variables.
3. **Maryland young-adult Marketplace subsidy**: clean design, but public SIPP treatment cell is too
   small.
4. **New Jersey Health Plan Savings**: plausible, but bundled with ARPA, SBE transition, and state
   mandate.
5. **Adult Medicaid dental benefits**: strong policy/outcome fit, but treated support is too small
   and estimates are wrong-signed.
6. **State paid sick leave mandates**: policy variation and sample support exist, but SIPP lacks the
   first-stage leave measure and reduced-form outcomes do not move coherently.
7. **State individual mandates**: weak Marketplace signal.
8. **Pandemic UI early termination**: clean timing, too small for insurance spillovers.
9. **No Surprises Act**: excellent policy, SIPP measurement too indirect.
10. **STLDI expansion/state regulation**: no coherent SIPP signal.
11. **State-Based Marketplace transitions**: wrong-signed dynamics.

## New Artifacts

- `script/11_idea_scan/15_paid_sick_leave_fast_test.py`
- `report/32_paid_sick_leave_fast_test.md`
- `result/idea_scan/paid_sick_leave_person_year_panel.parquet`
- `result/idea_scan/paid_sick_leave_support.csv`
- `result/idea_scan/paid_sick_leave_state_year_support.csv`
- `result/idea_scan/paid_sick_leave_event_support.csv`
- `result/idea_scan/paid_sick_leave_estimates.csv`
- `result/idea_scan/paid_sick_leave_event.csv`
- `result/idea_scan/paid_sick_leave_leave_one.csv`
