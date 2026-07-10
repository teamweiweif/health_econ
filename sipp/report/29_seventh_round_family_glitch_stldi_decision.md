# Seventh-Round Family Glitch / STLDI Decision

## Question

Can the current public SIPP parquet support another adult, non-child, non-unwinding health-insurance
paper with direct causal identification and a current policy gap?

This round tested two policies:

1. The 2023 ACA family-glitch fix.
2. State regulatory heterogeneity around the 2018 federal short-term limited-duration insurance
   expansion.

## Source Checks

- Federal Register final rule on family-member affordability:
  https://www.federalregister.gov/documents/2022/10/13/2022-22184/affordability-of-employer-coverage-for-family-members-of-employees
- CMS family glitch technical assistance PDF:
  https://www.cms.gov/marketplace/technical-assistance-resources/afford-employer-coverage-fixing-family-glitch.pdf
- Commonwealth Fund STLDI state regulation issue brief:
  https://www.commonwealthfund.org/publications/issue-briefs/2019/may/states-step-up-protect-markets-consumers-short-term-plans
- Federal Register 2018 STLDI final rule:
  https://www.federalregister.gov/documents/2018/08/03/2018-16568/short-term-limited-duration-insurance
- KFF STLDI availability summary:
  https://www.kff.org/patient-consumer-protections/examining-short-term-limited-duration-health-plans-on-the-eve-of-aca-marketplace-open-enrollment/

## 1. ACA Family Glitch Fix

### Why It Is Interesting

This is the best new candidate found since the PTC premium-intensity work.

The policy question is real and current: before 2023, family members could be blocked from
Marketplace PTCs if employee-only employer coverage was affordable, even if family coverage was
unaffordable. The 2022 final rule changed affordability for family members starting in 2023.

SIPP is potentially useful because it observes monthly coverage path:

- direct-purchase / Marketplace coverage;
- exchange/subsidized private coverage;
- private coverage;
- uninsured;
- medical OOP and doctor visits.

### Design Tested

Sample:

- Adults age 26-64.
- Family income 138-600% FPL.
- Years 2019-2023.
- At least six observed months per person-year.

Exposure:

- `family_exposed`: adult in a multi-person family with spouse link or children.

Treatment:

- `family_exposed x 2023`.

Fixed effects:

- state-year;
- state-family-exposure.

Family-year fixed effects are intentionally excluded because the treatment is a national 2023
family-exposure shock and would be collinear with family-year indicators.

### Support

- 57,935 person-years.
- 38,834 persons.
- 38,908 family-exposed person-years.
- 6,129 active treated person-years in 2023.

### Static Estimates

Main term: `family_exposed x 2023`.

- `direct_market`: +0.0159, se 0.0095.
- `exchange_subsidy`: +0.0214, se 0.0089.
- `uninsured`: +0.0142, se 0.0094.
- `any_coverage`: -0.0142, se 0.0094.
- `private`: +0.0025, se 0.0121.
- `oop_any`: -0.0060, se 0.0137.
- `doctor_any`: +0.0192, se 0.0129.

### Event Check

Relative to 2022:

`direct_market`:

- 2019: +0.0020, se 0.0108.
- 2020: +0.0001, se 0.0108.
- 2021: +0.0104, se 0.0118.
- 2023: +0.0190, se 0.0124.

`exchange_subsidy`:

- 2019: +0.0037, se 0.0098.
- 2020: +0.0044, se 0.0099.
- 2021: +0.0082, se 0.0109.
- 2023: +0.0254, se 0.0115.

`uninsured`:

- 2019: -0.0056, se 0.0112.
- 2020: -0.0036, se 0.0110.
- 2021: +0.0005, se 0.0117.
- 2023: +0.0120, se 0.0121.

### Same-Person 2022 to 2023 Check

All observed in both 2022 and 2023:

- `direct_market`: +0.0279, se 0.0190.
- `exchange_subsidy`: +0.0228, se 0.0177.
- `uninsured`: -0.0031, se 0.0141.
- `any_coverage`: +0.0031, se 0.0141.
- `private`: +0.0138, se 0.0170.
- n = 3,761 persons.

Baseline employer-like private sample:

- Defined as private coverage in 2022, not direct-market, not exchange/subsidized.
- This is the closest observable proxy to families potentially blocked by employer-family
  affordability, but it is still not actual family-glitch eligibility.

Results:

- `direct_market`: +0.0018, se 0.0156.
- `exchange_subsidy`: +0.0004, se 0.0133.
- `uninsured`: -0.0155, se 0.0111.
- `any_coverage`: +0.0155, se 0.0111.
- `private`: +0.0477, se 0.0156.
- n = 2,445 persons.

### Decision

`FAMILY GLITCH: BEST NEW CONDITIONAL LEAD, NOT CLEAN GO`

Why it is worth remembering:

- The event pattern is better than most prior candidates.
- Exchange/subsidized coverage rises in 2023 among family-exposed adults.
- Pre-2023 event coefficients are much smaller.
- The policy is current, authority-backed, and has a plausible SIPP-specific contribution.

Why it is not a clean GO:

- The uploaded SIPP parquet does not observe employer offer, employee-only premium, family premium,
  employer contribution, or actual family-glitch eligibility.
- The family-exposure proxy is broad and includes many people never at risk of the glitch.
- The static estimate also shows a positive uninsured coefficient, which is not the clean coverage
  expansion story.
- The closest baseline employer-like private sample does not show a Marketplace/subsidy transition.

Practical interpretation:

- This is not ready as a top-field causal paper from the current 96-column parquet.
- It is the strongest candidate to revisit if a richer SIPP extract can add employer coverage source,
  offer, premium contribution, or more detailed private coverage type.

## 2. Short-Term Limited-Duration Insurance

### Design Tested

Sample:

- Adults age 26-64.
- Family income 200-800% FPL.
- Years 2017-2021.

Target group:

- Healthy adults age 26-44 with family income 300-800% FPL.

Treatment:

- permissive STLDI state x target group x post-2019.

Fixed effects:

- state-year;
- state-target;
- target-year.

### Support

- 72,394 person-years.
- 45,675 persons.
- 10,333 permissive-state target person-years.
- 5,824 active treated person-years.

### Estimates

- `direct_market`: -0.0053, se 0.0120.
- `exchange_subsidy`: -0.0094, se 0.0103.
- `uninsured`: +0.0074, se 0.0114.
- `any_coverage`: -0.0074, se 0.0114.
- `private`: +0.0073, se 0.0140.
- `oop_any`: -0.0281, se 0.0198.

Event pattern:

- No clear post-2019 movement in direct-market, exchange/subsidy, or uninsured outcomes.

### Decision

`STLDI: NO-GO FROM CURRENT SIPP`

The policy question is valid, but SIPP does not identify STLDI enrollment. The indirect outcomes do
not show a coherent market-segmentation signal. This should not be pursued.

## Updated Ranking After Seventh Round

1. **ACA enhanced PTC / 400% FPL with premium intensity**: best policy gap, but state-level premium
   intensity failed dynamic checks.
2. **ACA family glitch fix**: best new conditional lead; directional 2023 exchange/subsidy signal,
   but actual eligibility is unobserved.
3. **Maryland young-adult subsidy**: clean conceptual age-income design, but public SIPP treatment
   support is too thin.
4. **New Jersey Health Plan Savings**: directionally plausible, but bundled with SBE transition,
   ARPA, and state mandate.
5. **State individual mandates**: weak Marketplace signal, not robust enough.
6. **Pandemic UI early termination**: clean timing, too small for health-insurance spillovers.
7. **No Surprises Act**: excellent policy, SIPP measurement too indirect.
8. **STLDI federal expansion/state regulation**: no coherent SIPP signal.
9. **State-Based Marketplace transitions**: wrong-signed dynamic pattern.

## Current Verdict

`NO CLEAN IMMEDIATE GO FROM CURRENT 96-COLUMN PUBLIC SIPP PARQUET`

The family-glitch idea is the only new result that deserves a conditional follow-up note. But it
does not satisfy the user's requested standard yet because the compact parquet lacks the core
eligibility variables.

## New Artifacts

- `script/11_idea_scan/13_family_glitch_stldi_fast_test.py`
- `report/28_family_glitch_stldi_fast_test.md`
- `result/idea_scan/family_glitch_stldi_person_year_panel.parquet`
- `result/idea_scan/family_glitch_stldi_support.csv`
- `result/idea_scan/family_glitch_stldi_estimates.csv`
- `result/idea_scan/family_glitch_stldi_event.csv`
- `result/idea_scan/family_glitch_transition_estimates.csv`
