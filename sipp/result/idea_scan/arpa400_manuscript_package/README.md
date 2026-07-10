# ARPA 400% FPL Manuscript Package

Status: CONDITIONAL GO.

This directory contains manuscript-ready filtered tables and figure manifests for the locked SIPP ARPA 400% FPL design. These outputs are derived from existing result CSVs only; this export script does not rerun models.

## Files

- `table1_support_cell_means.csv` / `.md`: support and weighted cell means by period and threshold side.
- `table2_primary_estimates.csv` / `.md`: locked primary local difference-in-discontinuities estimates.
- `table3_mechanism_decomposition.csv` / `.md`: full sample, lagged non-employer, and lagged current-employer mechanism comparison.
- `table4_robustness_summary.csv` / `.md`: bandwidth, donut, annual-FPL, timing, placebo, and fake-policy summaries.
- `table5_placebo_falsification.csv` / `.md`: row-level falsification and measurement-check estimates.
- `figure_manifest.csv` / `.md`: paths and intended uses for the four locked figures.

## Main Claim Discipline

Allowed: ARPA's removal of the 400% FPL subsidy cliff is associated with a local uninsured reduction near the threshold in SIPP monthly data.

Allowed: direct-market/subsidy mechanism evidence is strongest among lagged non-employer adults.

Not allowed: clean RDD, pure Marketplace enrollment effect, 2026 expiration effect, or older-adult headline effect.

## Minimum Web GPT Upload

Upload this README plus:

- `table2_primary_estimates.md`
- `table3_mechanism_decomposition.md`
- `table4_robustness_summary.md`
- `table5_placebo_falsification.md`
- `sipp/report/92_arpa_400fpl_paper_section_draft.md`
- `sipp/report/90_arpa_400fpl_specification_lock_and_identification_memo.md`
