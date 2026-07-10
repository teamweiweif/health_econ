# ARPA Unemployment-Compensation Marketplace Subsidy Fast Test

## Question

Did ARPA's special 2021 Marketplace subsidy rule for people receiving unemployment compensation increase Marketplace/direct-purchase coverage or reduce uninsurance among UI recipients?

## Source Checks

- CMS American Rescue Plan and the Marketplace: https://www.cms.gov/newsroom/fact-sheets/american-rescue-plan-and-marketplace
- KFF ARPA affordability analysis for Marketplace shoppers and the uninsured: https://www.kff.org/affordable-care-act/how-the-american-rescue-plan-act-affects-subsidies-for-marketplace-shoppers-and-people-who-are-uninsured/
- KFF ARPA private-coverage affordability analysis: https://www.kff.org/affordable-care-act/how-the-american-rescue-plan-will-improve-affordability-of-private-health-coverage/
- CMS assister webinar on unemployment compensation and APTC: https://www.cms.gov/marketplace/assister-webinars/uc-aptc-arp-webinar.pdf

Policy logic: CMS states that taxpayers receiving unemployment compensation during any week beginning in 2021 may be eligible for premium tax credits for 2021 Marketplace coverage. KFF explains that for UI recipients, household income above 133% FPL was disregarded for Marketplace premium and cost-sharing subsidy purposes in 2021, making zero-premium benchmark silver coverage possible.

## Design

Unit: person-month.

Main sample: adults ages 26-64, non-Medicare, FPL <= 1000%, SIPP reference years 2018-2023.

Exposure:

- `ui_year`: any regular, supplemental, or other unemployment compensation receipt in the reference year.
- Main DDD key: `ui_year x 2021`.
- Timing sensitivity: `ui_year x 2021 x subsidy-window month`, using April-September and July-December windows.

Outcomes:

- uninsured;
- direct-purchase private coverage;
- Marketplace flag;
- subsidized private flag;
- direct-purchase / Marketplace / subsidy composite.

Controls and fixed effects:

- age, FPL, sex, race/ethnicity, disability, employment and earnings indicators, Medicaid;
- state fixed effects, calendar month/year fixed effects for the year-2021 model;
- state and year-month fixed effects for timing models.

## Support

- Full screen support table: `result/idea_scan/arpa_ui_marketplace_support.csv`.
- 2021 UI-recipient support: 10,446 person-months, 931 persons with any UI in the year; 4,773 UI-receipt person-months.

## Results

Main `ui_year x 2021` model, all years:

- Uninsured: -0.0036 (person-cluster t=-0.27).
- Direct purchase: 0.0308 (person-cluster t=1.84).
- Marketplace flag: 0.0233 (person-cluster t=1.45).
- Subsidized private: 0.0144 (person-cluster t=1.29).
- Market/subsidy composite: 0.0289 (person-cluster t=1.72).

Main `ui_year x 2021` model excluding 2020:

- Uninsured: -0.0232 (person-cluster t=-1.41).
- Direct purchase: 0.0394 (person-cluster t=2.06).
- Marketplace flag: 0.0311 (person-cluster t=1.70).
- Market/subsidy composite: 0.0381 (person-cluster t=1.99).

Timing model, 2019/2021/2022 with April-September window:

- Uninsured: -0.0141 (person-cluster t=-1.98).
- Direct purchase: -0.0070 (person-cluster t=-1.45).
- Marketplace flag: -0.0021 (person-cluster t=-0.52).
- Market/subsidy composite: -0.0068 (person-cluster t=-1.41).

Timing model, 2019/2021/2022 with July-December window:

- Uninsured: -0.0058 (person-cluster t=-0.47).
- Direct purchase: 0.0067 (person-cluster t=0.74).
- Marketplace flag: 0.0158 (person-cluster t=1.79).
- Market/subsidy composite: 0.0077 (person-cluster t=0.85).

## Interpretation

This is a credible new SIPP idea only if the UI-recipient group shows a clear 2021-specific Marketplace/direct-purchase increase and a corresponding uninsured decline. Otherwise, the individual-level eligibility rule is too entangled with pandemic labor-market shocks to serve as a lead causal design.

## Artifacts

- `script/11_idea_scan/35_arpa_ui_marketplace_subsidy_test.py`
- `report/70_arpa_ui_marketplace_subsidy_test.md`
- `result/idea_scan/arpa_ui_marketplace_estimates.csv`
- `result/idea_scan/arpa_ui_marketplace_support.csv`
- `result/idea_scan/arpa_ui_marketplace_raw_cells.csv`
