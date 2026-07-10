# Arkansas Medicaid Work-Requirement Fast Test

## Question

Can the 2018 Arkansas Medicaid work and reporting requirement support a new adult SIPP paper on
coverage loss, employment, and medical-financial spillovers?

## Source Checks

- KFF Medicaid work requirements resources: https://www.kff.org/medicaid/medicaid-work-requirements-tracker-resources/
- KFF 5 key facts about Medicaid work requirements: https://www.kff.org/medicaid/5-key-facts-about-medicaid-work-requirements/
- NEJM results from the first year in Arkansas: https://www.nejm.org/doi/full/10.1056/NEJMsr1901772
- Health Affairs two-year impacts: https://www.healthaffairs.org/doi/abs/10.1377/hlthaff.2020.00538

Key policy facts:

- Arkansas implemented Medicaid work and reporting requirements beginning June 2018.
- The initial implementation targeted adults ages 30-49; requirements for ages 19-29 were planned
  for January 2019.
- KFF summarizes the requirements as being in effect from June 2018 through March 2019 and reports
  more than 18,000 coverage losses.
- NEJM and Health Affairs studies found coverage losses without employment gains, so the SIPP
  contribution would need to be a credible replication plus added outcomes.

## Design

- Unit: person-month, reference months 2017-2019.
- Geography: Arkansas plus regional comparison states: Alabama, Arkansas, Kentucky, Louisiana, Mississippi, Missouri, Oklahoma, Tennessee, Texas.
- Primary target: ages 30-49, low-income, nondisabled adults.
- Treatment: Arkansas x target age x active requirement months.
- Main active window: June-December 2018.
- Sensitivity active window: June 2018-March 2019.
- Fixed effects: state-month, state-target, target-month.
- Standard errors: clustered by state, with only nine regional state clusters.

## Support

FPL <= 100%, 2017-2019:

- Person-months: 26,395.
- Persons: 2,707.
- Arkansas target person-months: 547.
- Active Arkansas target person-months: 88.
- Active Arkansas target persons: 17.

FPL <= 138%, 2017-2019:

- Person-months: 37,000.
- Persons: 3,478.
- Arkansas target person-months: 821.
- Active Arkansas target person-months: 148.
- Active Arkansas target persons: 24.

Baseline Medicaid sample, FPL <= 138%, 2018:

- Person-months: 2,924.
- Persons: 295.
- Arkansas target person-months: 97.
- Active Arkansas target person-months: 58.
- Active Arkansas target persons: 10.

## Main Estimates

FPL <= 100%, June-December 2018:

- `medicaid`: -0.1668, state-clustered se 0.0310, t -5.38.
- `public`: -0.1866, state-clustered se 0.0297, t -6.28.
- `uninsured`: +0.0993, state-clustered se 0.0315, t 3.15.
- `any_coverage`: -0.0993, state-clustered se 0.0315, t -3.15.
- `private`: +0.0219, state-clustered se 0.0169, t 1.30.
- `employed_any_week`: +0.2035, state-clustered se 0.0366, t 5.55.
- `weeks_with_job`: +0.8242, state-clustered se 0.1641, t 5.02.
- `earn_pos`: +0.2378, state-clustered se 0.0300, t 7.93.
- `log_earnings`: +1.0800, state-clustered se 0.2125, t 5.08.

FPL <= 138%, June-December 2018:

- `medicaid`: -0.0842, state-clustered se 0.0341, t -2.47.
- `public`: -0.0947, state-clustered se 0.0274, t -3.46.
- `uninsured`: +0.1034, state-clustered se 0.0222, t 4.66.
- `any_coverage`: -0.1034, state-clustered se 0.0222, t -4.66.
- `private`: -0.0405, state-clustered se 0.0258, t -1.57.
- `employed_any_week`: +0.1251, state-clustered se 0.0338, t 3.70.
- `weeks_with_job`: +0.5586, state-clustered se 0.1422, t 3.93.
- `earn_pos`: +0.1312, state-clustered se 0.0352, t 3.72.
- `log_earnings`: -0.2118, state-clustered se 0.1804, t -1.17.

Baseline Medicaid sample, June-December 2018:

- `medicaid`: -0.0304, state-clustered se 0.0180, t -1.69.
- `public`: -0.0304, state-clustered se 0.0180, t -1.69.
- `uninsured`: +0.0304, state-clustered se 0.0180, t 1.69.
- `any_coverage`: -0.0304, state-clustered se 0.0180, t -1.69.
- `private`: -0.0343, state-clustered se 0.0276, t -1.24.
- `employed_any_week`: -0.0139, state-clustered se 0.0421, t -0.33.
- `weeks_with_job`: -0.1514, state-clustered se 0.1772, t -0.85.
- `earn_pos`: +0.0022, state-clustered se 0.0441, t 0.05.
- `log_earnings`: +0.0515, state-clustered se 0.3187, t 0.16.

## Verdict

`REPLICATION-SIGNAL-BUT-TREATED-CELL-TOO-THIN`

This is a high-current-policy question, but a clean SIPP GO requires three things at once: a visible
Medicaid/public coverage loss, a corresponding uninsured increase, and no offsetting employment gain
large enough to change the interpretation. The design also has a serious limitation: it is a
single-state short-duration policy with only nine regional state clusters in this screen.

## Artifacts

- `script/11_idea_scan/23_arkansas_medicaid_work_requirement_test.py`
- `result/idea_scan/arkansas_workreq_person_month_panel.parquet`
- `result/idea_scan/arkansas_workreq_support.csv`
- `result/idea_scan/arkansas_workreq_estimates.csv`
