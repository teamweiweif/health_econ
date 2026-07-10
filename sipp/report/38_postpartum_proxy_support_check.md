# Postpartum Medicaid Extension Proxy Support Check

## Question

Can current compact SIPP support an adult maternal-coverage paper on 12-month postpartum Medicaid
extensions?

## Source Checks

- KFF Medicaid Postpartum Coverage Extension Tracker: https://www.kff.org/medicaid/medicaid-postpartum-coverage-extension-tracker/
- CMS SHO 21-007 on postpartum extension state plan option: https://www.medicaid.gov/federal-policy-guidance/downloads/sho21007.pdf
- CMS press release on postpartum coverage expansion: https://www.cms.gov/newsroom/press-releases/biden-harris-administration-announces-expansion-medicaid-postpartum-coverage-oklahoma-30-states-d-c
- ASPE Medicaid Postpartum Coverage Issue Brief: https://aspe.hhs.gov/sites/default/files/documents/a315d594ab2e6dfbb8ef3c2bfccfcc8f/Postpartum-Coverage-Issue-Brief.pdf

The policy is substantively important: federal law historically required pregnancy-related Medicaid
coverage only through 60 days postpartum; ARPA created a state plan option for 12-month postpartum
coverage effective April 1, 2022, and the option was later made permanent.

## Compact-Parquet Feasibility

The compact 96-column parquet does not include the direct pregnancy/birth/leave variables needed for
a clean postpartum sample. Metadata confirms that variables such as `EBIRTHRSN3`, `EBIRTHRSN5`,
`TPREBIRTHINT`, and `TPSTBIRTHINT` exist in the broader SIPP metadata but are not in the compact
parquet.

This check therefore uses only a proxy:

- female;
- age 18-44;
- in a family-month with an infant age 0;
- low-income defined as FPL <= 300% for the main upper-bound support count.

This is an adult maternal-coverage proxy, not a child continuous-eligibility design.

## Support Upper Bound

- All proxy person-years, 2017-2023: 1,822.
- All proxy persons: 1,746.
- Low-income proxy person-years, 2017-2023: 1,108.
- Low-income proxy persons: 1,067.
- Low-income proxy person-years in 2022: 111.
- Low-income proxy person-years in 2023: 104.
- Low-income proxy person-years in 2022-2023 combined: 215.
- States with any low-income 2022-2023 proxy support: 39.
- Maximum support in any single state-year: 20.

This is an upper-bound support check. Actual treated support after exact state adoption timing,
Medicaid-enrollment targeting, and postpartum-month restrictions would be smaller.

## Decision

`NO-GO-SUPPORT`

The policy is important and adult-focused, but the current compact SIPP parquet is not adequate for
this paper:

- direct birth/pregnancy variables are not present in the compact parquet;
- the infant-in-family proxy is too coarse;
- low-income proxy support in the relevant 2022-2023 window is only
  215 person-years;
- the largest single state-year has only 20 person-years;
- PHE continuous enrollment overlaps the early policy implementation period and would further mute
  coverage changes.

This should not be pursued from the current uploaded compact parquet. It could be revisited only
with a richer SIPP extract that includes pregnancy/birth variables and enough years after 2023.

## Artifacts

- `script/11_idea_scan/18_postpartum_proxy_support_check.py`
- `result/idea_scan/postpartum_proxy_person_year_panel.parquet`
- `result/idea_scan/postpartum_proxy_upper_bound.csv`
- `result/idea_scan/postpartum_proxy_year_support.csv`
- `result/idea_scan/postpartum_proxy_state_support.csv`
