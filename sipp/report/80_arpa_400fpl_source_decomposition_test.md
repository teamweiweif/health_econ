# ARPA 400% FPL Source-Decomposition Test

## Question

Does the ARPA 400% FPL subsidy-cliff removal signal survive after separating employer-related private coverage from direct-purchase / Marketplace paths using raw SIPP private coverage source fields?

## Current Policy Hook

- CMS ARPA Marketplace fact sheet: https://www.cms.gov/newsroom/fact-sheets/american-rescue-plan-and-marketplace
- KFF 2026 Marketplace enrollment/premium update: https://www.kff.org/affordable-care-act/what-we-know-so-far-about-2026-aca-marketplace-enrollment-premiums-and-deductibles/
- KFF older-adult enhanced PTC expiration analysis: https://www.kff.org/affordable-care-act/how-will-the-loss-of-enhanced-premium-tax-credits-affect-older-adults/
- Urban Institute 2026 enhanced PTC expiration brief: https://www.urban.org/research/publication/48-million-people-will-lose-coverage-2026-if-enhanced-premium-tax-credits

CMS describes the ARPA change as replacing the pre-ARPA rule where households above 400% FPL were not eligible for premium tax credits with a benchmark-premium contribution cap of 8.5% of income. KFF's 2026 work makes this current again: after enhanced credits expired at the end of 2025, people just above 400% FPL accounted for a disproportionately large share of Marketplace enrollment losses, and older adults above 400% FPL faced especially large premium increases.

## Data Construction

- Base panel: `data/analysis_ready/sipp_2018_2024_person_month_panel.parquet`.
- RPRITYPE1 supplement: `temp/scratch/rpritype1_2018_2024.parquet`.
- Raw source supplement: `temp/scratch/cobra_source_job_vars_2018_2024.parquet`.
- Raw source fields: `EPR1MTH`, `EPR2MTH`, `EHEMPLY1`, `EHEMPLY2`, `EHICOST1`, `EHICOST2`.
- Employer-related source = current employer, former employer, or union source.
- Direct source = source line coded as bought directly.

## Support

- Main age 26-64 350-450% FPL support: 216,480 person-months; max cell persons 10,642.
- Pre-period nongroup/uninsured at-risk support: 25,361 person-months; max cell persons 1,739.

| sample | post | above400 | person_months | persons | states | uninsured | source_employer_related | source_bought_direct | market_or_subsidy |
|---|---|---|---|---|---|---|---|---|---|
| main_age26_64 | 0 | 0 | 75702 | 10642 | 51 | 0.1103 | 0.6580 | 0.0601 | 0.0990 |
| main_age26_64 | 0 | 1 | 68885 | 9932 | 51 | 0.0943 | 0.6816 | 0.0610 | 0.0914 |
| main_age26_64 | 1 | 0 | 38532 | 6207 | 51 | 0.1089 | 0.6351 | 0.0720 | 0.1235 |
| main_age26_64 | 1 | 1 | 33361 | 5596 | 51 | 0.0839 | 0.6897 | 0.0577 | 0.1069 |
| older_age50_64 | 0 | 0 | 29544 | 4113 | 51 | 0.0980 | 0.6556 | 0.0800 | 0.1189 |
| older_age50_64 | 0 | 1 | 26968 | 3884 | 51 | 0.0795 | 0.6777 | 0.0786 | 0.1088 |
| older_age50_64 | 1 | 0 | 13965 | 2307 | 51 | 0.0825 | 0.6265 | 0.1033 | 0.1614 |
| older_age50_64 | 1 | 1 | 13399 | 2186 | 50 | 0.0622 | 0.6961 | 0.0777 | 0.1208 |
| pre_nongroup_uninsured_baseline | 0 | 0 | 13669 | 1739 | 51 | 0.5164 | 0.0000 | 0.2636 | 0.4327 |
| pre_nongroup_uninsured_baseline | 0 | 1 | 10654 | 1494 | 51 | 0.5008 | 0.0000 | 0.2994 | 0.4490 |
| pre_nongroup_uninsured_baseline | 1 | 0 | 578 | 85 | 28 | 0.3739 | 0.3416 | 0.2099 | 0.2702 |
| pre_nongroup_uninsured_baseline | 1 | 1 | 460 | 77 | 27 | 0.4328 | 0.3044 | 0.1352 | 0.2052 |
| pre_current_employer_baseline | 0 | 0 | 46819 | 5432 | 48 | 0.0193 | 0.9590 | 0.0158 | 0.0260 |
| pre_current_employer_baseline | 0 | 1 | 44840 | 5398 | 49 | 0.0220 | 0.9523 | 0.0199 | 0.0282 |
| pre_current_employer_baseline | 1 | 0 | 2668 | 374 | 37 | 0.0215 | 0.9413 | 0.0252 | 0.0380 |
| pre_current_employer_baseline | 1 | 1 | 2576 | 365 | 37 | 0.0084 | 0.9583 | 0.0225 | 0.0322 |

Lagged-source diagnostic support:

| sample | post | above400 | person_months | persons | states | uninsured | source_employer_related | source_bought_direct | market_or_subsidy |
|---|---|---|---|---|---|---|---|---|---|
| lag_nonemployer_months | 0 | 0 | 25733 | 4295 | 51 | 0.3139 | 0.0160 | 0.1659 | 0.2652 |
| lag_nonemployer_months | 0 | 1 | 21487 | 3670 | 51 | 0.2881 | 0.0146 | 0.1824 | 0.2645 |
| lag_nonemployer_months | 1 | 0 | 14168 | 2669 | 50 | 0.2872 | 0.0177 | 0.1884 | 0.3073 |
| lag_nonemployer_months | 1 | 1 | 10406 | 2101 | 50 | 0.2619 | 0.0217 | 0.1656 | 0.2957 |
| lag_nongroup_uninsured_months | 0 | 0 | 14915 | 2798 | 51 | 0.5273 | 0.0237 | 0.2795 | 0.4452 |
| lag_nongroup_uninsured_months | 0 | 1 | 11988 | 2333 | 50 | 0.5075 | 0.0228 | 0.3224 | 0.4662 |
| lag_nongroup_uninsured_months | 1 | 0 | 8748 | 1786 | 50 | 0.4687 | 0.0273 | 0.3082 | 0.5019 |
| lag_nongroup_uninsured_months | 1 | 1 | 5987 | 1330 | 50 | 0.4530 | 0.0343 | 0.2883 | 0.5122 |
| lag_current_employer_months | 0 | 0 | 43499 | 6271 | 47 | 0.0030 | 0.9944 | 0.0044 | 0.0113 |
| lag_current_employer_months | 0 | 1 | 41303 | 6170 | 48 | 0.0028 | 0.9948 | 0.0045 | 0.0101 |
| lag_current_employer_months | 1 | 0 | 21671 | 3504 | 46 | 0.0036 | 0.9931 | 0.0047 | 0.0168 |
| lag_current_employer_months | 1 | 1 | 20392 | 3434 | 46 | 0.0019 | 0.9942 | 0.0092 | 0.0222 |

## RPRITYPE1 vs Raw Source Agreement

| reference_year | person_months | persons | rpritype1_employer | source_employer_related | source_current_employer | source_former_employer | source_bought_direct | agreement_rpritype1_source_employer |
|---|---|---|---|---|---|---|---|---|
| 2017.0000 | 42987.0000 | 5801.0000 | 0.6800 | 0.6658 | 0.6242 | 0.0274 | 0.0645 | 0.9858 |
| 2018.0000 | 32755.0000 | 4572.0000 | 0.7065 | 0.6853 | 0.6464 | 0.0319 | 0.0590 | 0.9788 |
| 2019.0000 | 33628.0000 | 4770.0000 | 0.6675 | 0.6550 | 0.6115 | 0.0296 | 0.0621 | 0.9875 |
| 2020.0000 | 35217.0000 | 5449.0000 | 0.6832 | 0.6708 | 0.6303 | 0.0308 | 0.0564 | 0.9876 |
| 2021.0000 | 24930.0000 | 3919.0000 | 0.6697 | 0.6543 | 0.6171 | 0.0294 | 0.0686 | 0.9846 |
| 2022.0000 | 24459.0000 | 3797.0000 | 0.6779 | 0.6661 | 0.6314 | 0.0251 | 0.0560 | 0.9882 |
| 2023.0000 | 22504.0000 | 3302.0000 | 0.6750 | 0.6606 | 0.6326 | 0.0193 | 0.0716 | 0.9856 |

## Main Diff-in-Discontinuities

Coefficient: above 400% FPL x post-2021, local linear with triangular kernel in the 350-450% FPL window; year, month, and state fixed effects; controls for age, sex, race/ethnicity, disability.

- Uninsured: -0.0277 (person-cluster se 0.0141, t -1.96; state-cluster se 0.0151, t -1.83; N=215,972).
- Any coverage: +0.0277 (person-cluster se 0.0141, t 1.96; state-cluster se 0.0151, t 1.83; N=215,972).
- Private: +0.0265 (person-cluster se 0.0170, t 1.56; state-cluster se 0.0202, t 1.31; N=215,972).
- RPRITYPE1 employer: +0.0342 (person-cluster se 0.0186, t 1.84; state-cluster se 0.0232, t 1.47; N=215,972).
- Raw source employer-related: +0.0301 (person-cluster se 0.0190, t 1.59; state-cluster se 0.0244, t 1.24; N=215,972).
- Raw source current employer: +0.0129 (person-cluster se 0.0198, t 0.65; state-cluster se 0.0235, t 0.55; N=215,972).
- Raw source former employer: +0.0147 (person-cluster se 0.0069, t 2.13; state-cluster se 0.0079, t 1.86; N=215,972).
- Raw source bought direct: +0.0073 (person-cluster se 0.0108, t 0.67; state-cluster se 0.0107, t 0.68; N=215,972).
- Direct-purchase / RMARKTPLACE: +0.0208 (person-cluster se 0.0137, t 1.52; state-cluster se 0.0145, t 1.43; N=215,972).
- Marketplace flag: +0.0165 (person-cluster se 0.0123, t 1.34; state-cluster se 0.0107, t 1.54; N=215,972).
- Market/subsidy composite: +0.0202 (person-cluster se 0.0137, t 1.47; state-cluster se 0.0147, t 1.37; N=215,972).

## Mechanism Subsamples

Older adults 50-64:

- Uninsured: -0.0080 (person-cluster se 0.0202, t -0.39; state-cluster se 0.0191, t -0.42; N=83,704).
- Source employer-related: +0.0267 (person-cluster se 0.0293, t 0.91; state-cluster se 0.0356, t 0.75; N=83,704).
- Source bought direct: +0.0113 (person-cluster se 0.0206, t 0.55; state-cluster se 0.0232, t 0.49; N=83,704).
- Market/subsidy composite: -0.0033 (person-cluster se 0.0240, t -0.14; state-cluster se 0.0279, t -0.12; N=83,704).

Pre-period nongroup/uninsured baseline:

- Uninsured: -0.0374 (person-cluster se 0.1111, t -0.34; state-cluster se 0.0839, t -0.45; N=25,303).
- Source employer-related: -0.0118 (person-cluster se 0.1129, t -0.10; state-cluster se 0.1127, t -0.10; N=25,303).
- Source bought direct: +0.0370 (person-cluster se 0.0792, t 0.47; state-cluster se 0.0771, t 0.48; N=25,303).
- Market/subsidy composite: +0.0553 (person-cluster se 0.0888, t 0.62; state-cluster se 0.0853, t 0.65; N=25,303).

Pre-period current-employer baseline placebo/substitution sample:

- Uninsured: -0.0115 (person-cluster se 0.0104, t -1.11; state-cluster se 0.0122, t -0.94; N=96,688).
- Source employer-related: +0.0367 (person-cluster se 0.0170, t 2.16; state-cluster se 0.0233, t 1.58; N=96,688).
- Source bought direct: -0.0050 (person-cluster se 0.0094, t -0.54; state-cluster se 0.0104, t -0.48; N=96,688).
- Market/subsidy composite: -0.0092 (person-cluster se 0.0234, t -0.39; state-cluster se 0.0254, t -0.36; N=96,688).

Lagged non-employer source months:

- Uninsured: -0.0457 (person-cluster se 0.0331, t -1.38; state-cluster se 0.0425, t -1.08; N=71,638).
- Source employer-related: -0.0100 (person-cluster se 0.0058, t -1.72; state-cluster se 0.0066, t -1.52; N=71,638).
- Source bought direct: +0.0362 (person-cluster se 0.0273, t 1.33; state-cluster se 0.0255, t 1.42; N=71,638).
- Market/subsidy composite: +0.0739 (person-cluster se 0.0328, t 2.25; state-cluster se 0.0350, t 2.11; N=71,638).

Lagged nongroup/uninsured source months:

- Uninsured: -0.0619 (person-cluster se 0.0490, t -1.26; state-cluster se 0.0580, t -1.07; N=41,543).
- Source employer-related: -0.0255 (person-cluster se 0.0096, t -2.67; state-cluster se 0.0106, t -2.42; N=41,543).
- Source bought direct: +0.0395 (person-cluster se 0.0443, t 0.89; state-cluster se 0.0451, t 0.88; N=41,543).
- Market/subsidy composite: +0.1006 (person-cluster se 0.0494, t 2.04; state-cluster se 0.0599, t 1.68; N=41,543).

Lagged current-employer source months:

- Uninsured: -0.0011 (person-cluster se 0.0021, t -0.52; state-cluster se 0.0019, t -0.56; N=126,551).
- Source employer-related: -0.0007 (person-cluster se 0.0029, t -0.24; state-cluster se 0.0026, t -0.26; N=126,551).
- Source bought direct: +0.0056 (person-cluster se 0.0034, t 1.67; state-cluster se 0.0040, t 1.41; N=126,551).
- Market/subsidy composite: +0.0136 (person-cluster se 0.0064, t 2.12; state-cluster se 0.0078, t 1.74; N=126,551).

## Decision

`ARPA 400% FPL: STILL THE LEAD, BUT POSITION AS COVERAGE-LOSS / AFFORDABILITY RESPONSE FIRST; MARKETPLACE MECHANISM SECONDARY UNLESS FURTHER REFINED.`

This screen directly addresses the key worry raised after the first pass: whether the uninsured decline above 400% FPL is actually employer coverage substitution. The answer is mixed but still useful.

What survives:

- Main uninsured falls by about 2.8 percentage points.
- Lagged non-employer months show a large market/subsidy response of about 7.4 percentage points and a 4.6 percentage point uninsured decline.
- Lagged nongroup/uninsured months show an even larger market/subsidy response of about 10.1 percentage points.
- Lagged current-employer months show essentially no uninsured response.

What weakens the pure version:

- Main-sample employer-related coverage also rises, especially former-employer coverage.
- Older adults 50-64 do not show the expected strong response.
- Marketplace/direct-purchase uptake is clear in lagged non-employer mechanism samples but only moderate in the full sample.

Therefore, the viable paper is not "Marketplace enrollment jumped cleanly everywhere above 400% FPL." The viable paper is a difference-in-discontinuities coverage-affordability paper: removing the 400% cliff reduced uninsurance near the threshold, with the strongest direct-market mechanism among people who were not coming from employer coverage.

## Artifacts

- `script/11_idea_scan/40_arpa_400fpl_source_decomposition_test.py`
- `report/80_arpa_400fpl_source_decomposition_test.md`
- `report/81_thirtysecond_round_arpa_400fpl_source_decomposition_decision.md`
- `result/idea_scan/arpa400_source_decomposition_estimates.csv`
- `result/idea_scan/arpa400_source_decomposition_support.csv`
- `result/idea_scan/arpa400_source_decomposition_agreement.csv`
- `result/idea_scan/arpa400_source_decomposition_cell_means.csv`
