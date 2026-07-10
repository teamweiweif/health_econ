# Eighth-Round Adult Medicaid Dental Decision

## Question

Can the current public SIPP parquet support an adult, non-child, non-unwinding paper on Medicaid
adult dental benefit expansions?

## Why This Was Worth Testing

This is one of the cleanest remaining adult policy ideas because:

- the policy is adult-specific and not tied to Medicaid unwinding or children;
- Medicaid adult dental benefits are optional and vary by state;
- oral health access is a live policy issue as states expand or consider cutting adult dental
  benefits;
- SIPP directly observes dental visits (`TVISDENT`), unlike many prior candidates where the core
  mechanism was only indirectly observed.

## Policy Source Checks

- Medicaid.gov Dental Care:
  https://www.medicaid.gov/medicaid/benefits/dental-care
- Virginia DMAS adult dental benefit press release:
  https://www.dmas.virginia.gov/media/3612/07-01-21-press-release-more-than-750000-medicaid-members-receive-adult-dental-benefit.pdf
- MaineCare covered services:
  https://www.maine.gov/dhhs/oms/mainecare-options/covered-services-benefits
- TennCare dental services:
  https://www.tn.gov/tenncare/members-applicants/dental-services.html
- New Hampshire Medicaid adult dental coverage:
  https://www.dhhs.nh.gov/nhsmiles

Policy coding used:

- Virginia: comprehensive adult Medicaid dental benefit began July 1, 2021; first full-year active
  coding is 2022.
- Maine: adult MaineCare dental coverage began July 1, 2022; first full-year active coding is 2023.
- Tennessee: adult TennCare dental benefits began in 2023.
- New Hampshire: adult Medicaid dental benefit began April 1, 2023.

Michigan 2023 dental redesign was not coded as a clean new benefit because the official source
describes delivery/redesign and reimbursement changes, not a clearly new adult dental benefit.

## Design

Source:

- `data/analysis_ready/sipp_2018_2024_person_month_panel.parquet`

Unit:

- person-year collapsed from monthly SIPP rows.

Sample:

- adults age 21-64;
- family income 0-250% FPL;
- at least six observed months;
- reference years 2018-2023.

Target groups:

1. Medicaid adult: Medicaid in at least half of observed months.
2. Public-covered adult: any public coverage in at least half of observed months.

Treatment:

- adult dental expansion state x active full-year x target adult.

Fixed effects:

- state-year;
- state-target;
- target-year.

Outcomes:

- `dental_visits`;
- `dental_any`;
- `doctor_any` as a utilization placebo;
- `hospital_any`;
- `oop_any`;
- `sick_days`.

## Support

Medicaid-target sample:

- 50,091 person-years.
- 34,440 persons.
- 17,689 target Medicaid adult person-years.
- 853 expansion-state target person-years.
- 165 active treated person-years.

Public-target sample:

- 50,091 person-years.
- 34,440 persons.
- 20,884 target public adult person-years.
- 1,055 expansion-state target person-years.
- 190 active treated person-years.

State-specific Medicaid target support:

- Virginia has usable but still thin support: 317 Medicaid target person-years in 2018-2023, with
  50 in 2022 and 45 in 2023.
- Tennessee has 358 person-years but only 42 in 2023, its first treated year.
- Maine and New Hampshire are too small for independent inference.

## Main Estimates

Medicaid target:

- `dental_visits`: -0.2698, se 0.2163.
- `dental_any`: -0.0548, se 0.0660.
- `doctor_any`: -0.0026, se 0.0559.
- `hospital_any`: -0.0734, se 0.0401.
- `oop_any`: -0.0006, se 0.0634.
- `sick_days`: -3.5662, se 6.8074.

Public target:

- `dental_visits`: -0.3191, se 0.2069.
- `dental_any`: -0.0300, se 0.0635.
- `doctor_any`: -0.0155, se 0.0560.
- `hospital_any`: -0.0605, se 0.0391.
- `oop_any`: -0.0058, se 0.0616.
- `sick_days`: +2.0702, se 6.6855.

Leave-one-treated-state checks remain negative or near zero for the dental outcomes. Excluding
Virginia, Maine, Tennessee, or New Hampshire does not reveal a positive pooled effect.

## Virginia Event Check

Virginia is the only state with pre/post support before the final observed year.

Virginia Medicaid-target differential coefficients, omitting 2020:

`dental_visits`:

- 2018: +0.2909, se 0.3599.
- 2019: +0.5094, se 0.3374.
- 2021: -0.0491, se 0.4074.
- 2022: -0.5349, se 0.4043.
- 2023: +0.2914, se 0.3984.

`dental_any`:

- 2018: +0.0048, se 0.1244.
- 2019: +0.1306, se 0.1226.
- 2021: +0.0793, se 0.1302.
- 2022: -0.1714, se 0.1324.
- 2023: +0.0870, se 0.1396.

There is no coherent post-policy jump. The 2022 first full year is negative, and 2023 is imprecise.

## Decision

`ADULT MEDICAID DENTAL: NO-GO FROM CURRENT PUBLIC SIPP`

The idea is substantively strong and the outcome is well matched to SIPP, but the empirical screen
fails:

- active treated support is only 165 Medicaid-target person-years;
- main dental outcomes are negative, not positive;
- Virginia event estimates do not show a post-benefit access increase;
- leave-one checks do not uncover a stable positive signal.

This should not be pursued as a main paper with the current public SIPP extract.

## Updated Ranking

1. **ACA enhanced PTC / 400% FPL with premium intensity**: best policy gap, but state-level premium
   intensity failed dynamic checks.
2. **ACA family glitch fix**: best current conditional lead; exchange/subsidy rises in 2023 among
   family-exposed adults, but actual eligibility is unobserved.
3. **Maryland young-adult Marketplace subsidy**: clean conceptual design, but public SIPP treatment
   cell is too small.
4. **New Jersey Health Plan Savings**: directionally plausible, but bundled with ARPA, SBE
   transition, and state mandate.
5. **Adult Medicaid dental benefits**: policy/outcome fit is excellent, but treated support is too
   small and estimates are wrong-signed.
6. **State individual mandates**: weak Marketplace signal, not robust enough.
7. **Pandemic UI early termination**: clean timing, too small for insurance spillovers.
8. **No Surprises Act**: excellent policy, SIPP measurement too indirect.
9. **STLDI expansion/state regulation**: no coherent SIPP signal.
10. **State-Based Marketplace transitions**: wrong-signed dynamics.

## Current Verdict

`NO CLEAN IMMEDIATE GO FROM CURRENT 96-COLUMN PUBLIC SIPP PARQUET`

The adult dental test was important because it used an outcome SIPP actually measures well. Its
failure strengthens the broader conclusion: the current compact public SIPP file is useful for rapid
screening, but the viable top-field adult policy paper likely needs either richer SIPP variables or a
policy with much larger treated support.

## New Artifacts

- `script/11_idea_scan/14_adult_medicaid_dental_fast_test.py`
- `report/30_adult_medicaid_dental_fast_test.md`
- `result/idea_scan/adult_medicaid_dental_person_year_panel.parquet`
- `result/idea_scan/adult_medicaid_dental_support.csv`
- `result/idea_scan/adult_medicaid_dental_expansion_state_support.csv`
- `result/idea_scan/adult_medicaid_dental_estimates.csv`
- `result/idea_scan/adult_medicaid_dental_event.csv`
- `result/idea_scan/adult_medicaid_dental_leave_one.csv`
