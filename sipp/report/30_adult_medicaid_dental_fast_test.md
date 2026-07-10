# Adult Medicaid Dental Benefit Fast Test

## Question

Can current SIPP support an adult, non-child, non-unwinding paper on Medicaid adult dental benefit
expansions and dental care access?

## Source Checks

- Medicaid.gov Dental Care page: https://www.medicaid.gov/medicaid/benefits/dental-care
- Virginia DMAS adult dental benefit press release, July 1 2021: https://www.dmas.virginia.gov/media/3612/07-01-21-press-release-more-than-750000-medicaid-members-receive-adult-dental-benefit.pdf
- MaineCare covered benefits: https://www.maine.gov/dhhs/oms/mainecare-options/covered-services-benefits
- TennCare dental services: https://www.tn.gov/tenncare/members-applicants/dental-services.html
- New Hampshire Medicaid adult dental coverage: https://www.dhhs.nh.gov/nhsmiles

Policy coding:

- Virginia: comprehensive Medicaid adult dental benefit began July 1, 2021; first full-year active
  coding is 2022.
- Maine: MaineCare adult dental coverage began July 1, 2022; first full-year active coding is 2023.
- Tennessee: adult TennCare dental benefits began in 2023.
- New Hampshire: adult Medicaid dental benefit began April 1, 2023.

Michigan 2023 dental redesign is not coded as a clean new benefit in this screen because the official
source describes delivery/redesign rather than a clearly new adult benefit.

## Data Construction

- Source parquet: `data/analysis_ready/sipp_2018_2024_person_month_panel.parquet`.
- Unit: person-year collapsed from monthly rows.
- Sample: adults age 21-64, family income 0-250% FPL, at least six observed months.
- Primary target: Medicaid adult, measured by monthly Medicaid indicators in at least half of
  observed months.
- Secondary target: public-covered adult.
- Treatment: adult dental expansion state x active full-year x target adult.
- Fixed effects: state-year, state-target, target-year.

## Support

Medicaid-target sample:

- Person-years: 50,091.
- Persons: 34,440.
- Target Medicaid adult person-years: 17,689.
- Expansion-state target person-years: 853.
- Active treated person-years: 165.

Public-target sample:

- Person-years: 50,091.
- Persons: 34,440.
- Target public adult person-years: 20,884.
- Expansion-state target person-years: 1,055.
- Active treated person-years: 190.

## Main Estimates

Medicaid target:

- `dental_visits`: -0.2698, se 0.2163, t -1.25.
- `dental_any`: -0.0548, se 0.0660, t -0.83.
- `doctor_any`: -0.0026, se 0.0559, t -0.05.
- `hospital_any`: -0.0734, se 0.0401, t -1.83.
- `oop_any`: -0.0006, se 0.0634, t -0.01.
- `sick_days`: -3.5662, se 6.8074, t -0.52.

Public target:

- `dental_visits`: -0.3191, se 0.2069, t -1.54.
- `dental_any`: -0.0300, se 0.0635, t -0.47.
- `doctor_any`: -0.0155, se 0.0560, t -0.28.
- `hospital_any`: -0.0605, se 0.0391, t -1.55.
- `oop_any`: -0.0058, se 0.0616, t -0.09.
- `sick_days`: +2.0702, se 6.6855, t 0.31.

## Virginia Event Check

Virginia is the only treated state with enough post-policy support before the last observed year.
The event check estimates Virginia Medicaid-target differential coefficients by year, omitting 2020.

See `result/idea_scan/adult_medicaid_dental_event.csv`.

## Verdict

`NO-CLEAN-GO`

A clean GO would require:

- a positive effect on `dental_visits` and `dental_any`;
- no similar movement in placebo outcomes such as doctor visits;
- an event pattern concentrated after benefit implementation;
- enough treated-state support that the result is not a single-small-state artifact.

## Artifacts

- `script/11_idea_scan/14_adult_medicaid_dental_fast_test.py`
- `result/idea_scan/adult_medicaid_dental_person_year_panel.parquet`
- `result/idea_scan/adult_medicaid_dental_support.csv`
- `result/idea_scan/adult_medicaid_dental_expansion_state_support.csv`
- `result/idea_scan/adult_medicaid_dental_estimates.csv`
- `result/idea_scan/adult_medicaid_dental_event.csv`
- `result/idea_scan/adult_medicaid_dental_leave_one.csv`
