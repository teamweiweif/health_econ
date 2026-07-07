# Rating Algorithm Emulation Audit

## Source Version

- Primary algorithm source: CMS archived `Five Star Users' Guide July 2022.pdf` from the official previous-versions ZIP.
- Comparison versions extracted: January 2022, October 2022, January 2023.

## Emulation Method

- Applied July 2022 Table A2 cutpoints to Provider Data Catalog component fields.
- Used adjusted total nurse HPRD, adjusted RN HPRD, weekend total nurse HPRD, total nurse turnover, RN turnover, and administrator departures.
- Rescaled available points to 380 when turnover components are missing, matching the guide's rescaling rule.
- July 2022 ProviderInfo lacks adjusted weekend total nurse HPRD, so reported weekend total nurse HPRD is used as a proxy.

## Validation

| snapshot | n_facilities | n_with_official_staffing_star | n_with_proxy_score | n_valid_match_test | star_match_rate | uses_reported_weekend_proxy |
| --- | --- | --- | --- | --- | --- | --- |
| 2022-01-27 | 14940 | 14671 | 14534 | 14366 | 0.548726 | True |
| 2022-04-27 | 14910 | 14438 | 14352 | 14117 | 0.5419 | True |
| 2022-07-27 | 14888 | 14584 | 14370 | 14201 | 0.89888 | True |
| 2022-10-27 | 14858 | 14592 | 14232 | 14124 | 0.967219 | False |
| 2023-01-02 | 14819 | 14529 | 14307 | 14203 | 0.966486 | False |

## Primary-Use Decision

The July 2022 proxy score does not reach the 95% match threshold. RD/RD-DID estimates are reported as proxy-running-variable evidence, not strong primary causal evidence.
