# Third-Round Direct-ID Decision Memo

## Question

Can the current 96-column SIPP parquet support a new adult, non-child, non-unwinding paper with
direct causal identification, current policy relevance, and enough innovation for a high-level
economics journal?

## Short Answer

Not yet. The current file supports several credible feasibility screens, but no clean immediate
`GO` without either richer SIPP variables or one targeted external policy/intensity merge.

## Updated Ranking

### 1. ACA Enhanced PTC / 400% FPL Cliff

Status: `BEST POLICY GAP; CONDITIONAL GO ONLY WITH PREMIUM INTENSITY`.

This remains the best substantive health-insurance idea. The policy problem is current because the
enhanced PTC cliff returned in 2026, and SIPP can observe uninsured spells, off-Marketplace
coverage, medical OOP, utilization, and labor outcomes.

Why not clean yet:

- Simple RD-DID around 400% FPL gives a negative market/subsidy signal.
- Both below-400 and above-400 groups were affected by ARPA affordability changes.
- Needs external premium burden or benchmark-premium treatment intensity.

### 2. Pandemic UI Early Termination

Status: `CLEANEST DIRECT TIMING; LOW POWER`.

The new person-FE event study strengthens this backup. Among 2021 prime-age UC recipients:

- Persons: 624.
- Early-exit state persons: 183.
- UC receipt post mean event coefficient: -0.1068.
- Employment post mean event coefficient: +0.0630.
- Earnings-positive post mean event coefficient: +0.0564.
- SNAP post mean event coefficient: -0.0154.
- Medicaid post mean event coefficient: -0.0073.
- Uninsured has pre-lead concerns.

Interpretation:

- Mechanism is coherent: UC receipt falls and employment rises after early termination.
- But SIPP sample is too small for a top-field main paper unless insurance/safety-net spillovers
  become much stronger under a full specification.
- The employment effect itself is already covered by CPS/bank-data literature.

### 3. Childless EITC ARPA 2021 Expansion

Status: `CONCEPTUALLY STRONG; CURRENT PARQUET SUPPORT THIN`.

This is a good adult tax-policy idea. ARPA temporarily expanded the childless EITC in 2021,
including younger workers who were previously excluded from the age-25 childless EITC threshold.

Fast support:

- Age 24 vs 25 childless low-income workers: 1,622 persons, but only 142 treated age-24 persons
  in 2021.
- Wider age 19-24 vs 25-29 screen: 7,433 persons and 937 treated young-adult persons in 2021.

Fast signals:

- Age 19-24 screen: log earnings +0.1345, t = 1.98.
- Medicaid any -0.0455, t = -1.64.
- Age 24 vs 25 screen is too thin.

Why not clean:

- No actual EITC receipt or refund in the uploaded parquet.
- No filing status.
- No exact tax-unit construction.
- No school-enrollment variable, which matters because under-24 students have special rules.

Verdict:

Promising only if a richer SIPP extract includes tax-program variables, school enrollment, or better
tax-unit construction. With the current 96 columns, do not make it the main paper.

### 4. Minimum Wage Spillovers

Status: `LARGE SUPPORT; IDENTIFICATION TOO BROAD`.

The screen has large samples and strong naive signals, but the current parquet lacks occupation,
industry, and clean pre-policy hourly wages. High-school-or-less exposure is too broad for a
top-field design.

Verdict:

Use as a backup if richer work-exposure variables can be added. Do not headline it from the current
file.

## Current Best Next Move

If the goal is a real paper rather than just a feasible exercise, the best next step is **not**
another broad SIPP-only screen. It is one of these two targeted upgrades:

1. Add external premium-intensity data and retest the PTC / 400% FPL cliff design.
2. Add richer SIPP variables for tax-unit/school-enrollment or occupation/industry exposure, then
   retest childless EITC or minimum-wage spillovers.

Without one of those upgrades, the best honest conclusion is:

`NO CLEAN IMMEDIATE GO FROM CURRENT 96-COLUMN PARQUET`.

## New Artifacts This Round

- `script/11_idea_scan/06_pandemic_ui_person_fe_event_test.py`
- `script/11_idea_scan/07_childless_eitc_fast_test.py`
- `report/17_pandemic_ui_person_fe_event_test.md`
- `report/18_childless_eitc_fast_test.md`
- `result/idea_scan/pandemic_ui_person_fe_event_estimates.csv`
- `result/idea_scan/pandemic_ui_person_fe_event_summary.csv`
- `result/idea_scan/childless_eitc_fast_estimates.csv`
- `result/idea_scan/childless_eitc_support.csv`
- `result/idea_scan/childless_eitc_person_year_panel.csv`

## Source Checks

- IRS EITC eligibility:
  https://www.irs.gov/credits-deductions/individuals/earned-income-tax-credit/who-qualifies-for-the-earned-income-tax-credit-eitc
- Tax Policy Center ARPA childless EITC expansion:
  https://taxpolicycenter.org/publications/how-american-rescue-plans-temporary-eitc-expansion-impacted-workers-without-children
- CRS ARPA 2021 summary:
  https://www.everycrsreport.com/reports/R46680.html
- NBER childless EITC young-adult paper:
  https://www.nber.org/system/files/working_papers/w32571/w32571.pdf
