# Paid Sick Leave Fast Test

## Question

Can the current public SIPP parquet support an adult, non-child, non-unwinding paper on state
paid sick leave mandates and worker health/utilization?

## Source Checks

- NCSL paid sick leave summary: https://www.ncsl.org/labor-and-employment/paid-sick-leave
- Washington L&I paid sick leave page: https://www.lni.wa.gov/workers-rights/leave/paid-sick-leave/
- New York Paid Sick Leave official page: https://www.ny.gov/programs/new-york-paid-sick-leave
- Colorado Department of Labor paid sick leave topic page: https://cdle.colorado.gov/dlss/labor-laws-by-topic/wage-and-hour-laws-including-paid-sick-leave
- Maryland Healthy Working Families Act FAQ: https://labor.maryland.gov/paidleave/paidleavefaqs.shtml
- New Mexico Department of Workforce Solutions Healthy Workplaces Act notice: https://www.dws.state.nm.us/Researchers/Publications/Economic-News/law-for-paid-sick-leave-goes-into-effect-july-2022-employers-are-encouraged-to-attend-nmdws-information-webinar

Primary clean coding:

- Maryland: active in 2018.
- Washington: active in 2018.
- New Jersey: effective late 2018; first full-year active coding is 2019.
- Rhode Island: effective July 2018; first full-year active coding is 2019.
- Colorado: active in 2021 for larger employers and 2022 for all employers; coding starts in 2021.
- New York: accrual began September 2020 and use began January 2021; coding starts in 2021.
- New Mexico: effective July 2022; first full-year active coding is 2023.

Broad sensitivity adds Michigan, Nevada, and Maine, but these are less clean because Michigan's
law is more limited and Nevada/Maine are earned paid leave rather than classic paid sick leave.

## Data Construction

- Source parquet: `data/analysis_ready/sipp_2018_2024_person_month_panel.parquet`.
- Unit: person-year collapsed from monthly rows.
- Years: reference years 2017-2023.
- Primary sample: employed adults age 18-64 with at least six observed months and valid education/FPL.
- Primary target: high-school-or-less workers (`EEDUC <= 39`).
- Treatment: clean paid sick leave adopter x active year x target worker.
- Fixed effects: state-year, state-target, target-year.

Important measurement caveat: SIPP has `TDAYSICK`, days illness/injury kept the person in bed more
than half the day. It does not directly measure paid sick leave access, accrual, or leave use. This
screen can only test reduced-form health/utilization and labor-market patterns.

## Support

Primary low-education worker sample:

- Person-years: 123,078.
- Persons: 70,330.
- Target worker person-years: 43,776.
- Clean-adopter target person-years: 5,218.
- Clean active treated person-years: 2,770.

Low-income worker sample:

- Person-years: 123,078.
- Target worker person-years: 36,063.
- Clean active treated person-years: 2,163.

All-adult worker-target sample:

- Person-years: 174,509.
- Target worker person-years: 123,078.
- Clean active treated person-years: 9,590.

## Main Estimates

Primary low-education worker DDD:

- `sick_days`: +0.6849, se 0.6808, t 1.01.
- `sick_any`: -0.0177, se 0.0220, t -0.80.
- `doctor_any`: -0.0143, se 0.0206, t -0.69.
- `doctor_visits`: -0.0279, se 0.3975, t -0.07.
- `uninsured`: +0.0088, se 0.0159, t 0.55.
- `log_earnings`: +0.0124, se 0.0818, t 0.15.

Low-income worker DDD:

- `sick_days`: -1.6482, se 0.9943, t -1.66.
- `sick_any`: -0.0312, se 0.0237, t -1.32.
- `doctor_any`: +0.0212, se 0.0220, t 0.96.
- `doctor_visits`: -0.2726, se 0.4699, t -0.58.
- `uninsured`: +0.0172, se 0.0168, t 1.02.
- `log_earnings`: -0.0178, se 0.1138, t -0.16.

All-adult worker-target DDD:

- `sick_days`: -1.3416, se 1.5211, t -0.88.
- `sick_any`: -0.0070, se 0.0191, t -0.36.
- `doctor_any`: -0.0048, se 0.0170, t -0.28.
- `doctor_visits`: -0.2246, se 0.5219, t -0.43.
- `uninsured`: -0.0129, se 0.0122, t -1.05.
- `log_earnings`: -0.0969, se 0.1127, t -0.86.
- `employed_share`: -0.0045, se 0.0041, t -1.10.

Broad paid-leave sensitivity among low-education workers:

- `sick_days`: +0.1365, se 0.6198, t 0.22.
- `sick_any`: -0.0151, se 0.0189, t -0.80.
- `doctor_any`: +0.0032, se 0.0176, t 0.18.
- `doctor_visits`: -0.1699, se 0.3355, t -0.51.
- `uninsured`: +0.0066, se 0.0135, t 0.49.
- `log_earnings`: -0.0708, se 0.0697, t -1.02.

## Event and Robustness Checks

Event coefficients for clean adopter states, omitting relative year -1, are saved in
`result/idea_scan/paid_sick_leave_event.csv`.

Leave-one-clean-adopter-state estimates are saved in
`result/idea_scan/paid_sick_leave_leave_one.csv`.

## Verdict

`NO-CLEAN-GO`

A clean GO would require:

- a coherent access or health-utilization response among plausibly binding workers;
- no large negative earnings/employment signal;
- event estimates without meaningful pre-policy differential movement;
- robustness to leaving out major adopter states;
- and, ideally, a direct first-stage measure of sick-leave access or use.

The last condition is not met in the current 96-column parquet. Therefore this idea can only become
credible if the reduced-form pattern is unusually strong and clean.

## Artifacts

- `script/11_idea_scan/15_paid_sick_leave_fast_test.py`
- `result/idea_scan/paid_sick_leave_person_year_panel.parquet`
- `result/idea_scan/paid_sick_leave_support.csv`
- `result/idea_scan/paid_sick_leave_state_year_support.csv`
- `result/idea_scan/paid_sick_leave_event_support.csv`
- `result/idea_scan/paid_sick_leave_estimates.csv`
- `result/idea_scan/paid_sick_leave_event.csv`
- `result/idea_scan/paid_sick_leave_leave_one.csv`
