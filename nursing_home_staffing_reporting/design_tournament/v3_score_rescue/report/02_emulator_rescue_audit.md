# Emulator Rescue Audit V3

## Core Rescue

- Official 0-380 staffing score was not found.
- Explicit adjusted weekend total nurse HPRD was not found in the July 2022 ProviderInfo file.
- July 2022 adjusted weekend total nurse HPRD was reconstructed from official July ProviderInfo components as `reported_weekend_total_nurse_hprd * adjusted_total_nurse_hprd / reported_total_nurse_hprd`.
- This is supported by the July guide statement that the all-days case-mix value is used for case-mix-adjusted total nurse staffing on weekends.
- In October 2022 and January 2023, where CMS publishes explicit adjusted weekend total HPRD, the same identity reproduces the official field almost exactly.

## Validation

| snapshot_date | n_facilities | n_with_official_staffing_star | n_with_score_or_proxy | n_valid_match_test | star_match_rate | exact_score_source | adjusted_weekend_hprd_source | proxy_used | passes_95pct_threshold | notes | n | sample_definition |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2022-01-27 | 14940 | 14671 | 14534 | 14366 | 0.553668 | not found | missing;reconstructed_from_official_ratio;reported_weekend_proxy | True | False | pre-July snapshot used old staffing methodology | 14366 | facilities with official staffing star and reconstructed/official score |
| 2022-04-27 | 14910 | 14438 | 14352 | 14117 | 0.547 | not found | missing;reconstructed_from_official_ratio;reported_weekend_proxy | True | False | pre-July snapshot used old staffing methodology | 14117 | facilities with official staffing star and reconstructed/official score |
| 2022-07-27 | 14888 | 14584 | 14370 | 14201 | 0.963453 | not found | missing;reconstructed_from_official_ratio;reported_weekend_proxy | True | True | July 2022 guide six-component score validation | 14201 | facilities with official staffing star and reconstructed/official score |
| 2022-10-27 | 14858 | 14592 | 14285 | 14124 | 0.967219 | not found | explicit_official_field;missing;reported_weekend_proxy | True | True | July 2022 guide six-component score validation | 14124 | facilities with official staffing star and reconstructed/official score |
| 2023-01-02 | 14819 | 14529 | 14355 | 14203 | 0.966486 | not found | explicit_official_field;missing;reported_weekend_proxy | True | True | July 2022 guide six-component score validation | 14203 | facilities with official staffing star and reconstructed/official score |

## V2 Versus V3

| snapshot_date | v3_star_match_rate | v2_star_match_rate | v3_minus_v2 | n |
| --- | --- | --- | --- | --- |
| 2022-01-27 | 0.553668 | 0.548726 | 0.00494222 | 5 |
| 2022-04-27 | 0.547 | 0.5419 | 0.00510023 | 5 |
| 2022-07-27 | 0.963453 | 0.89888 | 0.0645729 | 5 |
| 2022-10-27 | 0.967219 | 0.967219 | 0 | 5 |
| 2023-01-02 | 0.966486 | 0.966486 | -1.11022e-16 | 5 |

## Decision

July 2022 match rate is 0.963; RD/RD-DID status: **candidate primary evidence**.
Pre-July snapshots are retained as old-methodology comparisons and are not used to validate the July 2022 six-component score.
