# Twentieth-Round ARPA 400% FPL Employer-Coverage Validation

## Question

Does adding `RPRITYPE1` employer-related private coverage clarify whether the ARPA 400% FPL
uninsured reduction is really a Marketplace subsidy-cliff mechanism?

## Why This Validation Was Necessary

The earlier ARPA 400% FPL cliff screen became the leading conditional idea because:

- uninsured fell by about 2.6-3.1pp above 400% FPL after ARPA in the monthly-FPL local
  difference-in-discontinuities screens;
- direct-purchase / Marketplace proxies also moved positively in the main monthly-FPL screen;
- support around the threshold was large.

But the compact analysis-ready parquet did not include `RPRITYPE1`, the monthly employer-related
private coverage recode. Without that variable, a rise in employer coverage could be mistakenly
interpreted as Marketplace uptake.

## New Data Step

I extracted `RPRITYPE1` directly from the local raw Census SIPP zips:

- source zips: `temp/raw_downloads/census_sipp/YYYY/primary/puYYYY_csv.zip`;
- years: SIPP file years 2018-2024, corresponding to reference years 2017-2023;
- merge key: `file_year + SSUID + PNUM + MONTHCODE`;
- supplemental file: `temp/scratch/rpritype1_2018_2024.parquet`.

The variable is present in all raw zip headers and in the local metadata registry:

- `RPRITYPE1`: monthly non-military employer-related private coverage.
- `RPRITYPE2`: monthly direct-purchase private coverage.

## Merge / Missingness Check

Main ARPA 400% sample:

- age 26-64;
- non-Medicare;
- 350-450% monthly FPL;
- 217,610 person-months;
- 23,755 persons;
- 52 states including DC.

Rows with missing `RPRITYPE1` after merge:

- 26,281 person-months in the main sample.

Missingness by reference year:

- 2017: 5,304 missing out of 43,199 rows.
- 2018: 4,106 missing out of 32,738 rows.
- 2019: 4,451 missing out of 33,718 rows.
- 2020: 4,464 missing out of 35,451 rows.
- 2021: 2,464 missing out of 25,140 rows.
- 2022: 3,132 missing out of 24,630 rows.
- 2023: 2,360 missing out of 22,734 rows.

This is not a failed merge concentrated in one year. It looks like ordinary universe / blank-response
missingness that needs to be documented in the final data build.

## Main Results With Employer Coverage

Monthly FPL, age 26-64, post = 2021-2023:

- `uninsured`: -0.0263, person-clustered se 0.0143, t -1.84.
- `any_coverage`: +0.0263, person-clustered se 0.0143, t 1.84.
- `employer_private`: +0.0311, person-clustered se 0.0187, t 1.67.
- `direct_purchase`: +0.0222, person-clustered se 0.0137, t 1.63.
- `marketplace_flag`: +0.0197, person-clustered se 0.0123, t 1.61.
- `market_or_subsidy`: +0.0218, person-clustered se 0.0137, t 1.59.
- `private`: +0.0237, person-clustered se 0.0171, t 1.39.
- `public`: +0.0081, person-clustered se 0.0132, t 0.62.
- `medicaid`: +0.0033, person-clustered se 0.0117, t 0.28.

Age 21-64 sensitivity:

- `uninsured`: -0.0313, person-clustered se 0.0137, t -2.28.
- `employer_private`: +0.0325, person-clustered se 0.0179, t 1.81.
- `market_or_subsidy`: +0.0225, person-clustered se 0.0132, t 1.70.

Post-April-2021 timing:

- `uninsured`: -0.0296, person-clustered se 0.0147, t -2.01.
- `employer_private`: +0.0338, person-clustered se 0.0193, t 1.75.
- `marketplace_flag`: +0.0270, person-clustered se 0.0127, t 2.12.

Annual-FPL sensitivity:

- `uninsured`: -0.0301, person-clustered se 0.0226, t -1.33.
- `employer_private`: +0.0479, person-clustered se 0.0309, t 1.55.
- `direct_purchase`: -0.0243, person-clustered se 0.0230, t -1.06.
- `market_or_subsidy`: -0.0240, person-clustered se 0.0230, t -1.05.

## Interpretation

This materially changes the mechanism story:

- the uninsured reduction remains in the same range as before;
- direct-purchase / Marketplace proxies still move positively in the main monthly-FPL model;
- however, employer-related private coverage also rises by about 3.1pp in the same design;
- in the annual-FPL sensitivity, employer coverage rises while direct-purchase / Marketplace proxies
  move negative.

That means the current evidence cannot be sold as a clean Marketplace subsidy-cliff first stage.
The result may reflect a broader post-2021 near-threshold private-coverage shift, labor-market /
income-composition changes around the running variable, or incomplete separation of employer and
Marketplace coverage in SIPP.

## Decision Update

`ARPA 400% FPL CLIFF: STILL CURRENT BEST LEAD, BUT MECHANISM NOT CLEAN`

The idea remains first in the queue because the uninsured outcome is large, policy-current, and
well-supported. But the next-stage standard is higher:

- do not claim a clean Marketplace enrollment mechanism yet;
- headline the result only as an uninsured / any-coverage threshold response;
- treat Marketplace/direct-purchase evidence as suggestive;
- explicitly report employer coverage as a competing mechanism;
- require binned plots and pre-period discontinuity checks before any paper outline.

## Immediate Next Checks

1. Build binned RD plots for `uninsured`, `employer_private`, `direct_purchase`, and
   `marketplace_flag` separately by year or pre/post period.
2. Test whether the employer-coverage discontinuity already exists in pre-ARPA years.
3. Estimate age-gradient heterogeneity, especially ages 50-64, where premium subsidies should matter
   more than employer coverage transitions.
4. Run a non-employer baseline subsample if a defensible baseline definition can be constructed.
5. Decide whether the final paper is a narrower cliff-removal paper or a broader ARPA private
   coverage near-threshold paper.

## Ranking Implication

The top ranking does not change, but the confidence label changes:

1. **ARPA 400% FPL subsidy-cliff / private-coverage threshold response**: best lead, mechanism
   unresolved.
2. **SNAP Emergency Allotment termination**: best food-security lead.
3. **ACA enhanced PTC / premium-intensity portfolio**: useful as a mechanism extension.
4. **ACA family glitch fix**: conceptually good, variable-limited.
5. **ACA state reinsurance waivers**: support good, first stage weak.

## New Artifacts

- `script/11_idea_scan/26_arpa_400fpl_employer_mechanism_test.py`
- `report/54_arpa_400fpl_employer_mechanism_test.md`
- `temp/scratch/rpritype1_2018_2024.parquet`
- `result/idea_scan/arpa400_employer_mechanism_estimates.csv`
- `result/idea_scan/arpa400_employer_mechanism_cell_means.csv`
- `result/idea_scan/arpa400_employer_mechanism_support.csv`
