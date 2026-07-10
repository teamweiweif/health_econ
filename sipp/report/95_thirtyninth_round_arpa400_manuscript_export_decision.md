# Thirty-Ninth Round Decision: ARPA400 Manuscript Export Package

## Verdict

`MANUSCRIPT/WEB-GPT EXPORT PACKAGE COMPLETE; CONDITIONAL GO MAINTAINED`

The locked ARPA 400% FPL design now has a small manuscript-ready export package:

- `sipp/result/idea_scan/arpa400_manuscript_package/`

This package is generated from existing locked result CSVs only. It does not rerun models and does not add tuning.

## New Script

Export script:

- `sipp/script/11_idea_scan/43_arpa_400fpl_export_manuscript_package.py`

Purpose:

- convert locked result CSVs into compact Markdown and CSV tables;
- create a figure manifest;
- create a package README for Web GPT or manuscript drafting.

## Exported Files

Package contents:

- `README.md`
- `table1_support_cell_means.csv`
- `table1_support_cell_means.md`
- `table2_primary_estimates.csv`
- `table2_primary_estimates.md`
- `table3_mechanism_decomposition.csv`
- `table3_mechanism_decomposition.md`
- `table4_robustness_summary.csv`
- `table4_robustness_summary.md`
- `table5_placebo_falsification.csv`
- `table5_placebo_falsification.md`
- `figure_manifest.csv`
- `figure_manifest.md`

## What The Package Shows

Main table:

- uninsured coefficient: -0.0277;
- person SE: 0.0141;
- state SE: 0.0151;
- N: 215,972.

Mechanism table:

- lagged non-employer `market_or_subsidy`: +0.0739;
- person SE: 0.0328;
- state SE: 0.0350;
- N: 71,638.

Robustness table:

- main uninsured is negative in 5/5 bandwidth checks;
- lagged non-employer market/subsidy is positive in 5/5 bandwidth checks;
- annual-FPL mechanism is weak;
- placebo thresholds are not empty;
- pre-ARPA fake-policy tests near 400% FPL are near zero.

Figure manifest:

- all four locked figure files exist.

## Use

For Web GPT critique, upload:

1. `sipp/result/idea_scan/arpa400_manuscript_package/README.md`
2. `sipp/result/idea_scan/arpa400_manuscript_package/table2_primary_estimates.md`
3. `sipp/result/idea_scan/arpa400_manuscript_package/table3_mechanism_decomposition.md`
4. `sipp/result/idea_scan/arpa400_manuscript_package/table4_robustness_summary.md`
5. `sipp/result/idea_scan/arpa400_manuscript_package/table5_placebo_falsification.md`
6. `sipp/report/92_arpa_400fpl_paper_section_draft.md`
7. `sipp/report/90_arpa_400fpl_specification_lock_and_identification_memo.md`

Optional:

- add the four PNG files listed in `figure_manifest.md`.

## Decision

Keep ARPA400 as the current lead idea.

The next improvement should not be more generic tuning. The next pre-specified empirical extension should be:

**premium-exposure heterogeneity**, ideally using clean state/rating-area benchmark premium measures if linkable.

Purpose:

- test whether the effect is larger where the dollar value of eliminating the 400% cliff should be larger;
- address the current weak older-adult gradient;
- strengthen mechanism credibility without changing the primary estimand.

Do this only as an explicitly labeled extension, not as a replacement for the locked design.
