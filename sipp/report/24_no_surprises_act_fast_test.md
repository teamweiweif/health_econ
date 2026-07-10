# No Surprises Act Fast Test

## Question

Can SIPP support a non-child, non-unwinding adult health-insurance paper on the No Surprises Act
and financial protection from medical bills?

Design idea: after the federal No Surprises Act took effect in 2022, privately insured adults in
states without comprehensive pre-existing balance-billing protections should receive a larger new
consumer-protection shock than privately insured adults in states that already had comprehensive
protections.

## Source Checks

- CMS, State Surprise Billing Laws and the No Surprises Act: https://www.cms.gov/files/document/nsa-state-laws.pdf
- KFF, No Surprises Act Implementation: What to Expect in 2022: https://www.kff.org/affordable-care-act/no-surprises-act-implementation-what-to-expect-in-2022/
- Commonwealth Fund, State Balance-Billing Protections as of April 16, 2020: https://www.commonwealthfund.org/sites/default/files/2021-03/Hoadley_state_balance_billing_protections_table_02052021.pdf

## Policy Coding

Comprehensive pre-NSA state protections use the Commonwealth Fund table's "Comprehensive
Approach (18 states)" as of April 16, 2020. The treatment is:

`no comprehensive pre-NSA state protection x reference_year >= 2022`.

The estimation window is 2020-2023 to avoid pretending that earlier state-law adoption timing is
fully coded.

## Data and Samples

- Source parquet: `data/analysis_ready/sipp_2018_2024_person_month_panel.parquet`.
- Unit: person-year collapsed from monthly SIPP rows.
- Main sample: privately insured adults age 26-64 with any doctor or hospital use.
- Stronger exposure sample: privately insured adults age 26-64 with any hospital nights.
- Placebo sample: public-covered adult care users.
- Outcomes: log medical OOP, any OOP, OOP above 1000, OOP above 2000, OOP amount, doctor use, hospital use.

Support:

- Private care users: 45,491 person-years, 31,226 persons, 52 states.
- Private hospital users: 3,696 person-years, 3,378 persons, 52 states.
- Public-care placebo: 14,122 person-years, 10,253 persons, 52 states.
- Main-sample post new-protection person-years: 8,220.

## Static Estimates

Main term: `nsa_new_protection`, with state and year fixed effects.

Private care users:

- `log_oop`: +0.0199, se 0.0708, t 0.28.
- `oop_any`: +0.0054, se 0.0099, t 0.54.
- `oop_gt_1000`: -0.0027, se 0.0101, t -0.27.
- `oop_gt_2000`: +0.0003, se 0.0087, t 0.04.
- `oop_amount`: -21.5657, se 63.8242, t -0.34.
- `doctor_any`: +0.0002, se 0.0019, t 0.12.
- `hospital_any`: +0.0019, se 0.0063, t 0.30.

Private hospital users:

- `log_oop`: -0.1441, se 0.2716, t -0.53.
- `oop_any`: -0.0152, se 0.0359, t -0.42.
- `oop_gt_1000`: -0.0578, se 0.0381, t -1.52.
- `oop_gt_2000`: -0.0125, se 0.0349, t -0.36.
- `oop_amount`: -239.5061, se 311.6445, t -0.77.
- `doctor_any`: +0.0073, se 0.0223, t 0.32.
- `hospital_any`: -0.0000, se 0.0000, t -9.66.

Public-care placebo:

- `log_oop`: -0.0788, se 0.1257, t -0.63.
- `oop_any`: -0.0151, se 0.0203, t -0.75.
- `oop_gt_1000`: -0.0190, se 0.0127, t -1.49.
- `oop_gt_2000`: -0.0000, se 0.0101, t -0.00.
- `oop_amount`: +34.3542, se 82.8993, t 0.41.
- `doctor_any`: +0.0035, se 0.0047, t 0.75.
- `hospital_any`: -0.0102, se 0.0157, t -0.65.

## Verdict

`NO-CLEAN-GO`

Interpretation:

- A credible GO would require lower OOP in newly protected states after 2022, especially among
  privately insured hospital users, with no comparable placebo pattern among public-covered users.
- This screen cannot observe out-of-network bills, emergency department use, self-funded plan
  status, or whether a given bill was actually subject to the No Surprises Act.
- Therefore a statistically clean SIPP signal must be unusually strong before this can be treated as
  a main-paper idea.

## Artifacts

- `script/11_idea_scan/11_no_surprises_act_fast_test.py`
- `result/idea_scan/no_surprises_act_person_year_panel.parquet`
- `result/idea_scan/no_surprises_act_support.csv`
- `result/idea_scan/no_surprises_act_estimates.csv`
- `result/idea_scan/no_surprises_act_event.csv`
