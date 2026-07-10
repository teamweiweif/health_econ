# Seventeenth-Round Arkansas Medicaid Work-Requirement Decision

## Question

Can Arkansas's 2018 Medicaid work and reporting requirement support a new adult SIPP paper on
coverage loss, employment, and medical-financial spillovers?

## Why This Was Worth Testing

This is a high-relevance adult policy question:

- Arkansas was the first state to implement Medicaid work and reporting requirements with coverage
  consequences;
- the policy began in June 2018 and was stopped in March 2019;
- the initial group was age 30-49;
- current 2026 policy debates have made Medicaid work requirements newly salient;
- existing studies report coverage losses without employment gains, which creates a natural
  replication-plus-outcomes question for SIPP.

## Source Checks

- KFF Medicaid work requirements resources:
  https://www.kff.org/medicaid/medicaid-work-requirements-tracker-resources/
- KFF 5 key facts about Medicaid work requirements:
  https://www.kff.org/medicaid/5-key-facts-about-medicaid-work-requirements/
- NEJM results from the first year in Arkansas:
  https://www.nejm.org/doi/full/10.1056/NEJMsr1901772
- Health Affairs two-year impacts:
  https://www.healthaffairs.org/doi/abs/10.1377/hlthaff.2020.00538

The source facts are strong. The policy question is real. The limiting factor is SIPP support.

## Design Tested

Source:

- `data/analysis_ready/sipp_2018_2024_person_month_panel.parquet`

Unit:

- person-month, reference months 2017-2019.

Geography:

- Arkansas plus regional comparison states: Alabama, Kentucky, Louisiana, Mississippi, Missouri,
  Oklahoma, Tennessee, Texas.

Treatment:

- Arkansas x age 30-49 x active requirement months.

Main active window:

- June-December 2018.

Sensitivity active window:

- June 2018-March 2019.

Fixed effects:

- state-month;
- state-target;
- target-month.

Standard errors:

- clustered by state, but only nine regional state clusters.

## Support

FPL <= 100%, 2017-2019:

- 26,395 person-months.
- 2,707 persons.
- 547 Arkansas target person-months.
- 88 active Arkansas target person-months.
- 17 active Arkansas target persons.

FPL <= 138%, 2017-2019:

- 37,000 person-months.
- 3,478 persons.
- 821 Arkansas target person-months.
- 148 active Arkansas target person-months.
- 24 active Arkansas target persons.

Baseline Medicaid sample, FPL <= 138%, 2018:

- 2,924 person-months.
- 295 persons.
- 97 Arkansas target person-months.
- 58 active Arkansas target person-months.
- 10 active Arkansas target persons.

The cleanest causal target, baseline Medicaid enrollees actually at risk of losing Medicaid, has only
10 treated people.

## Main Results

FPL <= 100%, June-December 2018:

- `medicaid`: -0.1668, state-clustered se 0.0310.
- `public`: -0.1866, state-clustered se 0.0297.
- `uninsured`: +0.0993, state-clustered se 0.0315.
- `employed_any_week`: +0.2035, state-clustered se 0.0366.
- `earn_pos`: +0.2378, state-clustered se 0.0300.

FPL <= 138%, June-December 2018:

- `medicaid`: -0.0842, state-clustered se 0.0341.
- `public`: -0.0947, state-clustered se 0.0274.
- `uninsured`: +0.1034, state-clustered se 0.0222.
- `employed_any_week`: +0.1251, state-clustered se 0.0338.
- `earn_pos`: +0.1312, state-clustered se 0.0352.

Baseline Medicaid sample, June-December 2018:

- `medicaid`: -0.0304, state-clustered se 0.0180.
- `public`: -0.0304, state-clustered se 0.0180.
- `uninsured`: +0.0304, state-clustered se 0.0180.
- `employed_any_week`: -0.0139, state-clustered se 0.0421.
- `earn_pos`: +0.0022, state-clustered se 0.0441.

## Interpretation

The direction is interesting but not usable as a main SIPP paper:

- broad low-income samples show Medicaid/public coverage declines and uninsured increases;
- the clean baseline-Medicaid sample also points toward coverage loss without employment gain;
- however, the clean treated cell has only 10 active Arkansas target persons;
- broad samples show positive employment/earnings effects, which conflict with the known Arkansas
  literature and are likely compositional or target-definition artifacts;
- state-clustered inference with nine regional clusters is not reliable for a top-field claim;
- a single-state, short-duration policy needs stronger treated support than this compact SIPP file
  provides.

## Decision

`ARKANSAS MEDICAID WORK REQUIREMENT: NO-GO FOR CURRENT SIPP MAIN PAPER`

This can be cited internally as a directional replication screen, but it should not be developed as
the main project from this extract. The policy is hot; the SIPP support is not.

## Ranking Implication

Arkansas should sit below the stronger ACA and SNAP candidates. It is more policy-current than many
older ideas, but the treated-cell problem is decisive.

## Artifacts

- `script/11_idea_scan/23_arkansas_medicaid_work_requirement_test.py`
- `report/48_arkansas_medicaid_work_requirement_test.md`
- `result/idea_scan/arkansas_workreq_person_month_panel.parquet`
- `result/idea_scan/arkansas_workreq_support.csv`
- `result/idea_scan/arkansas_workreq_estimates.csv`
