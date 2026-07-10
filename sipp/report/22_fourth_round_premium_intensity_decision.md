# Fourth-Round PTC Premium-Intensity Decision

## Question

Can the leading ACA enhanced PTC / 400% FPL idea become a clean go by adding official CMS premium
intensity data?

## Data Added

I built a state-year premium-intensity file from official CMS Exchange Public Use Files:

- CMS Exchange PUF years: 2018-2023.
- Files: Rate-PUF and Plan Attributes PUF.
- Plan filter: individual-market, non-dental, silver plans.
- Premium proxy: unweighted state average of rating-area second-lowest silver premiums for ages
  40 and 60.
- Intensity: pre-2021 age-60 gross benchmark premium burden at 400% FPL above the 8.5% ARPA cap.

The resulting file is:

- `result/idea_scan/ptc_premium_policy_state_year.csv`

Important limitation:

- This is state-level, not county/rating-area matched, because the uploaded SIPP parquet only has
  state. CMS Exchange PUFs also generally exclude state-based exchanges that do not rely on the
  federal platform.

## Static Triple-D Screen

Sample: adults 26-64, annual family income 300-500% FPL, PUF-covered states, SIPP reference years
2018-2023.

Coefficient: `post2021 x above400 x high_pre_premium_burden`.

Main static estimates:

- `market_or_subsidy`: +0.0128, se 0.0050.
- `direct_purchase`: +0.0129, se 0.0056.
- `subsidized_private`: +0.0103, se 0.0035.
- `uninsured`: +0.0210, se 0.0060.
- `any_coverage`: -0.0210, se 0.0060.
- `oop_any`: -0.0231, se 0.0093.

Support is adequate:

- 15,533 persons.
- 39 PUF-covered states.
- Minimum support cell: 1,426 persons.

## Dynamic Check

The dynamic check estimates `above400 x highpremium` by year, with 2020 omitted.

This weakens the PTC idea.

For `market_or_subsidy`:

- 2018: -0.0066.
- 2019: +0.0061.
- 2021: -0.0202.
- 2022: -0.0025.
- 2023: -0.0063.

For `uninsured`:

- 2018: -0.0027.
- 2019: -0.0206.
- 2021: -0.0172.
- 2022: -0.0132.
- 2023: -0.0165.

For `any_coverage`:

- 2018: +0.0027.
- 2019: +0.0206.
- 2021: +0.0172.
- 2022: +0.0132.
- 2023: +0.0165.

## Decision

`PTC PREMIUM-INTENSITY: NOT CLEAN GO FROM CURRENT STATE-LEVEL MERGE`

The premium-intensity merge improves the conceptual design, but it does not produce a coherent
clean result:

- Static triple-D suggests more market/subsidy coverage in high-premium above-400 cells.
- But the dynamic model does not show a clear post-ARPA positive market/subsidy shift.
- Coverage/uninsured patterns move in ways that are not cleanly aligned with the simple marketplace
  uptake story.
- The state-level premium proxy is too coarse for final identification.

## What Would Be Needed To Rescue It

The PTC idea remains the best policy question, but it needs one of the following:

1. SIPP geography finer than state, so rating-area or county benchmark premiums can be merged.
2. External county/rating-area premium exposure mapped to the SIPP geography if available in the
   restricted-use file.
3. A design centered on 2026 return of the subsidy cliff once SIPP data cover 2026, because that
   would test a cleaner policy reversal.

Without those, this should stay conditional and should not be the main paper.

## Artifacts

- `script/11_idea_scan/08_ptc_premium_intensity_test.py`
- `script/11_idea_scan/09_ptc_premium_event_test.py`
- `report/20_ptc_premium_intensity_test.md`
- `report/21_ptc_premium_event_test.md`
- `result/idea_scan/ptc_premium_policy_state_year.csv`
- `result/idea_scan/ptc_premium_intensity_estimates.csv`
- `result/idea_scan/ptc_premium_intensity_support.csv`
- `result/idea_scan/ptc_premium_event_estimates.csv`
- `result/idea_scan/ptc_premium_event_support.csv`

## Source

- CMS Exchange Public Use Files:
  https://www.cms.gov/marketplace/resources/data/public-use-files
