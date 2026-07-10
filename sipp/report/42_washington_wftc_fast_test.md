# Washington Working Families Tax Credit Fast Test

## Question

Can current SIPP support an adult low-wage-worker paper on Washington's Working Families Tax Credit
launch?

## Source Checks

- Washington Working Families Tax Credit official site: https://workingfamiliescredit.wa.gov/
- Washington Working Families Tax Credit eligibility page: https://workingfamiliescredit.wa.gov/eligibility
- Washington Department of Revenue WFTC application window release: https://dor.wa.gov/about/news-releases/2026/working-families-tax-credit-application-window-opens-feb-1
- NCSL Earned Income Tax Credit Overview: https://www.ncsl.org/human-services/earned-income-tax-credit-overview

The official Washington WFTC site describes the credit as a tax credit for Washington workers. The
eligibility page states that eligible individuals must have lived in Washington for at least 183 days,
be at least 25 and under 65 or have a qualifying child, file a federal tax return, and be eligible for
the federal EITC or ITIN-equivalent eligibility. Washington Department of Revenue states the program
launched in 2023.

## Design

- Unit: person-year, 2018-2023.
- Geography: Washington vs regional controls: California, Colorado, Idaho, Montana, Oregon.
- Primary target: age 25-64, FPL <= 300%, annual earnings $1-$40,000, employed in at least half of
  observed months.
- Treatment: Washington x 2023 x target worker.
- Fixed effects: state-year, state-target, target-year.
- Outcomes: food security, SNAP, coverage, medical OOP, labor-market outcomes.

This is a feasibility screen. The compact parquet does not observe tax filing, federal EITC
eligibility, ITIN/SSN eligibility, actual WFTC application, or refund receipt.

## Support

Primary low-wage worker target:

- Person-years: 60,842.
- Persons: 32,337.
- Target person-years: 4,850.
- Washington 2023 target person-years: 50.
- Washington 2023 target persons: 50.

## Main Estimates

Low-wage worker target:

- `food_insecure`: -0.0147, se 0.0602, t -0.24.
- `very_low_food`: -0.0201, se 0.0377, t -0.53.
- `food_score`: -0.1062, se 0.2636, t -0.40.
- `snap_any`: -0.0548, se 0.0445, t -1.23.
- `uninsured`: +0.0374, se 0.0749, t 0.50.
- `oop_any`: +0.1447, se 0.0857, t 1.69.
- `log_earnings`: +0.3559, se 0.3141, t 1.13.

Broad worker sensitivity:

- `food_insecure`: +0.0150, se 0.0474, t 0.32.
- `very_low_food`: -0.0204, se 0.0254, t -0.80.
- `food_score`: -0.0168, se 0.1923, t -0.09.
- `snap_any`: -0.0512, se 0.0268, t -1.91.
- `uninsured`: +0.0429, se 0.0513, t 0.84.
- `oop_any`: +0.0450, se 0.0616, t 0.73.
- `log_earnings`: +0.3074, se 0.2482, t 1.24.

## Verdict

`NO-GO-SUPPORT`

A clean GO would require a much larger Washington 2023 target cell, credible tax-unit construction,
and a coherent improvement in food security or financial outcomes among likely eligible workers.

## Artifacts

- `script/11_idea_scan/20_washington_wftc_fast_test.py`
- `result/idea_scan/washington_wftc_person_year_panel.parquet`
- `result/idea_scan/washington_wftc_support.csv`
- `result/idea_scan/washington_wftc_estimates.csv`
