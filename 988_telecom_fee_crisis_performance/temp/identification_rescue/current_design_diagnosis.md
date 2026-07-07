# Current Design Diagnosis

## Reproduction

The official pipeline was reproduced in an external temporary copy of the project to avoid overwriting existing outputs. The regenerated panel summary, cohort ATT table, final report, and go/no-go report were byte-identical to the preserved originals. FE-model CSV hashes differed only because of machine-precision float string differences; displayed coefficients match.

## Current Identification

The current fee-adoption design remains policy-selected. Fee states differ in administrative capacity, mental-health policy commitment, fiscal choices, and baseline crisis-system conditions. Modern staggered-DID-style comparisons improve on a naive TWFE headline, but they do not make fee adoption exogenous.

The rescue-layer corrected answer-rate version of the original three-month operational lag produces an answer-rate ATT of 6.77 pp. This is still suggestive rather than decisive because the design does not solve policy selection.

## Data Coverage

| metric | value |
| --- | --- |
| raw_jurisdictions | 56 |
| state_dc_jurisdictions | 51 |
| primary_sample_rows | 2936 |
| primary_sample_states | 51 |
| observed_source_months | 58 |
| calendar_window | 2021-07-01 to 2026-05-01 |
| missing_calendar_months | 2025-02 |
| post2025_monitor_rows_excluded_from_primary | 22 |
| post2025_monitor_states_excluded_from_primary | IL;NM |

## PDF Extraction Audit

The 30-row validation sample was rechecked against the original PDF row text. Counts and time fields are parsed correctly in the sampled rows. The main issue is denominator choice for answer rate: some 2022 launch-transition PDFs include a received-contact denominator that differs from routed contacts, and the official reported answer rate aligns with answered/received contacts. The original pipeline used answered/routed contacts.

Rows in sampled validation classified as current-pipeline denominator errors: 3 of 30.

Months with any current answer-rate denominator difference above 1 percentage point:

| year_month | states | max_current_routed_abs_diff | max_received_abs_diff | rows_with_current_diff_gt_1pp |
| --- | --- | --- | --- | --- |
| 2022-07 | 56 | 0.08750293358366579 | 0.004896965763426908 | 52 |
| 2022-08 | 56 | 0.11555030703826163 | 0.004931506849314982 | 52 |
| 2022-09 | 56 | 0.08465346534653473 | 0.004943820224719175 | 51 |

## Bottom Line

The project is reproducible and mostly internally consistent, but the original answer-rate series should be corrected in any rescue analysis. This correction is not enough to rescue causal identification by itself.
