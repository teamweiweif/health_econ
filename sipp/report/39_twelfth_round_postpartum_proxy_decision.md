# Twelfth-Round Postpartum Proxy Decision

## Question

Should 12-month postpartum Medicaid extensions be pursued with the current compact SIPP parquet?

## Why This Was Worth Checking

This is an adult maternal-coverage policy, not a child continuous-eligibility project. It is
substantively important because postpartum Medicaid eligibility historically ended after 60 days for
many pregnancy-related eligibility pathways, and ARPA created a 12-month state plan option effective
April 1, 2022.

It also fits the user's preference for current, policy-relevant, authority-backed topics. The
question is whether the uploaded compact parquet can actually support the design.

## Source Checks

- KFF Medicaid Postpartum Coverage Extension Tracker:
  https://www.kff.org/medicaid/medicaid-postpartum-coverage-extension-tracker/
- CMS SHO 21-007:
  https://www.medicaid.gov/federal-policy-guidance/downloads/sho21007.pdf
- CMS press release on postpartum coverage expansion:
  https://www.cms.gov/newsroom/press-releases/biden-harris-administration-announces-expansion-medicaid-postpartum-coverage-oklahoma-30-states-d-c
- ASPE Medicaid Postpartum Coverage Issue Brief:
  https://aspe.hhs.gov/sites/default/files/documents/a315d594ab2e6dfbb8ef3c2bfccfcc8f/Postpartum-Coverage-Issue-Brief.pdf

KFF states that ARPA gave states a new option to extend Medicaid postpartum coverage to 12 months
via SPA, effective April 1, 2022, and that the option was later made permanent. CMS SHO 21-007
confirms states could only elect the SPA option with an effective date on or after April 1, 2022.

## Compact-Parquet Constraint

The current 96-column parquet does not include the direct pregnancy, birth, postpartum, or leave
variables needed for a clean maternal sample.

Metadata shows relevant variables exist in broader SIPP metadata, including:

- `EBIRTHRSN3`: paid maternity or paternity leave after child was born;
- `EBIRTHRSN5`: paid sick leave after child was born;
- `TPREBIRTHINT`: weeks not working leading up to birth;
- `TPSTBIRTHINT`: time not working after birth;
- `TYEAR_FB`: year of first birth.

But those variables are not present in the compact parquet. Therefore the only feasible uploaded-file
proxy is:

- female;
- age 18-44;
- in a family-month with an infant age 0;
- low-income using FPL <= 300%.

## Support Result

The upper-bound support check found:

- all proxy person-years, 2017-2023: 1,822;
- low-income proxy person-years, 2017-2023: 1,108;
- low-income proxy person-years in 2022: 111;
- low-income proxy person-years in 2023: 104;
- low-income proxy person-years in 2022-2023 combined: 215;
- maximum support in any single state-year: 20.

This is before applying exact state adoption timing, Medicaid enrollment targeting, postpartum-month
restrictions, or any credible comparison design. Actual treated support would be smaller.

## Decision

`POSTPARTUM MEDICAID EXTENSION: NO-GO FROM CURRENT COMPACT PARQUET`

The failure reason is support and measurement, not policy relevance.

This should not be pursued with the uploaded compact parquet because:

- direct birth/pregnancy variables are absent;
- the infant-in-family proxy is too coarse;
- the 2022-2023 target universe is tiny;
- the largest single state-year has only 20 proxy person-years;
- PHE continuous enrollment overlaps the early implementation period and would mute observed
  Medicaid coverage loss/gain;
- any regression would be more likely to manufacture false precision than identify a credible
  causal effect.

This can be revisited only with a richer SIPP extract and more post-2023 data.

## Updated Ranking

1. **SNAP Emergency Allotment termination**: best current conditional lead; household-level
   `food_insecure` rises about 7.6pp for lagged-SNAP households in early-ending states, but support
   is thin and secondary food outcomes are imprecise.
2. **ACA enhanced PTC / 400% FPL with premium intensity**: best insurance-policy gap, but dynamic
   checks failed.
3. **ACA family glitch fix**: best insurance-side conditional lead; current compact parquet lacks
   actual employer offer/premium eligibility variables.
4. **Maryland young-adult Marketplace subsidy**: clean design, but treatment cell is too small.
5. **New Jersey Health Plan Savings**: plausible, but bundled with ARPA, SBE transition, and state
   mandate.
6. **Adult Medicaid dental benefits**: strong policy/outcome fit, but treated support is too small
   and estimates are wrong-signed.
7. **State paid sick leave mandates**: policy variation exists, but no direct leave first stage and
   no coherent reduced-form pattern.
8. **State individual mandates**: weak Marketplace signal.
9. **Postpartum Medicaid extension**: important adult maternal-coverage policy, but compact SIPP has
   no direct birth/pregnancy variables and only 215 low-income proxy person-years in 2022-2023.
10. **Pandemic UI early termination**: clean timing, too small for insurance spillovers.
11. **No Surprises Act**: excellent policy, SIPP measurement too indirect.
12. **STLDI expansion/state regulation**: no coherent SIPP signal.
13. **State-Based Marketplace transitions**: wrong-signed dynamics.

## New Artifacts

- `script/11_idea_scan/18_postpartum_proxy_support_check.py`
- `report/38_postpartum_proxy_support_check.md`
- `result/idea_scan/postpartum_proxy_person_year_panel.parquet`
- `result/idea_scan/postpartum_proxy_upper_bound.csv`
- `result/idea_scan/postpartum_proxy_year_support.csv`
- `result/idea_scan/postpartum_proxy_state_support.csv`
