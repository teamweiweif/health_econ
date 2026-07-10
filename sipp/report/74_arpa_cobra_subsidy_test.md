# ARPA COBRA Premium Subsidy SIPP Fast Test

## Question

Did the temporary ARPA 100% COBRA premium subsidy in April-September 2021 help adults who involuntarily left jobs retain employer-related or former-employer private coverage and avoid uninsurance?

## Source Checks

- DOL COBRA premium assistance FAQ: https://www.dol.gov/sites/dolgov/files/EBSA/about-ebsa/our-activities/resource-center/faqs/cobra-premium-assistance.pdf
- KFF ARPA private coverage affordability summary: https://www.kff.org/affordable-care-act/how-the-american-rescue-plan-will-improve-affordability-of-private-health-coverage/

DOL states that ARP COBRA premium assistance applied to coverage periods from April 1, 2021 through September 30, 2021 and to people eligible for COBRA due to reduction in hours or involuntary termination. KFF describes the same six-month subsidy window and notes that voluntary quits were not eligible.

## SIPP Construction

- Base panel: `data/analysis_ready/sipp_2018_2024_person_month_panel.parquet`.
- Raw supplement: `temp/scratch/cobra_source_job_vars_2018_2024.parquet`.
- COBRA proxy: private-plan source line coded as `Former Employer` (`EHEMPLY1/2 == 2`) while the plan line is active.
- Stronger premium proxy: former-employer private coverage where `EHICOST1/2 == 1`, meaning employer/union pays all of the policy premium.
- Separation event: any job spell whose `EJB*_EMONTH` equals the reference month and has a stop-work reason in `EJB*_RSEND`.
- Treated event proxy: involuntary separation (`RSEND` 1-6) in April-September 2021.
- Control events: voluntary separations and involuntary separations in the same calendar months of other non-2020 years.
- Main at-risk sample: adults 26-64 with current-employer private coverage in the prior month.

Important measurement caveat: SIPP does not directly label COBRA. The closest monthly proxy is former-employer private coverage, plus the premium-payment source question.

## Support

- April-September non-2020 separation events, all adults 26-64: 296 treated involuntary events in the subsidy window.
- Main at-risk April-September sample with lagged current-employer private coverage: 151 treated involuntary events and 147 treated persons.

| sample | inv_col | events | persons | treated_events | treated_persons | control_invol_events | control_voluntary_events | treated_lag_current_employer_events |
|---|---|---|---|---|---|---|---|---|
| aprsep_exclude2020_all | involuntary | 6322 | 5630 | 296 | 283 | 1765 | 4261 | 151 |
| aprsep_exclude2020_all | involuntary_noseason | 6322 | 5630 | 196 | 191 | 1192 | 4934 | 96 |
| aprsep_exclude2020_lag_current_employer | involuntary | 3462 | 3176 | 151 | 147 | 933 | 2378 | 151 |
| aprsep_exclude2020_lag_current_employer | involuntary_noseason | 3462 | 3176 | 96 | 93 | 626 | 2740 | 96 |
| allmonths_exclude2020_all | involuntary | 11916 | 9501 | 296 | 283 | 3803 | 7817 | 151 |
| allmonths_exclude2020_all | involuntary_noseason | 11916 | 9501 | 196 | 191 | 2592 | 9128 | 96 |
| allmonths_exclude2020_lag_current_employer | involuntary | 6273 | 5348 | 151 | 147 | 1906 | 4216 | 151 |
| allmonths_exclude2020_lag_current_employer | involuntary_noseason | 6273 | 5348 | 96 | 93 | 1315 | 4862 | 96 |

## Raw Event Means

April-September non-2020 sample. Outcomes average months 0-3 after separation.

| subsidy_window | involuntary | events | persons | lag_current_employer_events | former_employer_private_m0_3 | former_premium_all_paid_m0_3 | employer_related_private_m0_3 | uninsured_m0_3 | direct_purchase_m0_3 | market_or_subsidy_m0_3 | any_coverage_m0_3 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0.0000 | 0.0000 | 3433.0000 | 3222.0000 | 1918.0000 | 0.0419 | 0.0131 | 0.5982 | 0.1647 | 0.1414 | 0.1423 | 0.8353 |
| 0.0000 | 1.0000 | 1765.0000 | 1660.0000 | 933.0000 | 0.0427 | 0.0102 | 0.5672 | 0.1883 | 0.1505 | 0.1516 | 0.8117 |
| 1.0000 | 0.0000 | 828.0000 | 798.0000 | 460.0000 | 0.0507 | 0.0088 | 0.6170 | 0.1614 | 0.1551 | 0.1571 | 0.8386 |
| 1.0000 | 1.0000 | 296.0000 | 283.0000 | 151.0000 | 0.0396 | 0.0067 | 0.5395 | 0.1809 | 0.1868 | 0.1868 | 0.8191 |

## Event-DDD Screen

Weighted event-level OLS. Key coefficient is `involuntary separation x April-September 2021 subsidy window`; models include year, month, and state fixed effects plus age, FPL, sex, race/ethnicity, disability, and lagged coverage controls. Standard errors are clustered by person.

Main at-risk sample, April-September, excluding 2020:

- Former-employer private coverage, months 0-3: -0.0169 (person-cluster se 0.0070, t -2.41; treated events 151, persons 147).
- Premium all paid, months 0-3: -0.0078 (person-cluster se 0.0043, t -1.83; treated events 151, persons 147).
- Employer-related private coverage, months 0-3: -0.0030 (person-cluster se 0.0297, t -0.10; treated events 151, persons 147).
- Uninsured, months 0-3: -0.0144 (person-cluster se 0.0226, t -0.64; treated events 151, persons 147).
- Direct purchase, months 0-3: +0.0540 (person-cluster se 0.0320, t 1.69; treated events 151, persons 147).
- Market/subsidy proxy, months 0-3: +0.0518 (person-cluster se 0.0320, t 1.62; treated events 151, persons 147).

Broad April-September sample, excluding 2020:

- Former-employer private coverage, months 0-3: -0.0072 (person-cluster se 0.0143, t -0.50; treated events 296, persons 283).
- Premium all paid, months 0-3: +0.0025 (person-cluster se 0.0067, t 0.37; treated events 296, persons 283).
- Uninsured, months 0-3: -0.0074 (person-cluster se 0.0161, t -0.46; treated events 296, persons 283).
- Direct purchase, months 0-3: +0.0082 (person-cluster se 0.0290, t 0.28; treated events 296, persons 283).

## Decision

`ARPA COBRA SUBSIDY: NO-GO for a main SIPP paper`.

Why this ranking:

- The policy is clean and official, but the empirical estimand is not as clean as the 400% FPL cliff because COBRA is only proxied, not directly observed.
- The main at-risk treated cell is the binding support check; if it is small, this cannot sustain a top-field standalone paper.
- A credible positive result would need former-employer coverage or all-premium-paid coverage to rise after involuntary separations in the subsidy window, with uninsured falling or at least not rising.
- Even if directional, this is more likely a mechanism extension to the ARPA private-coverage portfolio than a replacement for the 400% FPL lead.

## Artifacts

- `script/11_idea_scan/37_arpa_cobra_subsidy_test.py`
- `report/74_arpa_cobra_subsidy_test.md`
- `result/idea_scan/arpa_cobra_event_panel.parquet`
- `result/idea_scan/arpa_cobra_support.csv`
- `result/idea_scan/arpa_cobra_raw_cells.csv`
- `result/idea_scan/arpa_cobra_estimates.csv`
