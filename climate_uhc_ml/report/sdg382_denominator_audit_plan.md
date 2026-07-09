# SDG 3.8.2 Denominator Audit Plan

Status: denominator construction is blocked. This report is a fail-closed checklist for constructing `household_discretionary_budget`; it does not create SDG 3.8.2 outcomes.

## Official Rule Basis

The local UNSD metadata snapshot defines SDG 3.8.2 as positive OOP health expenditure exceeding 40 percent of household discretionary budget. It defines discretionary budget as total household consumption expenditure or income minus the societal poverty line. The SPL is in 2017 PPP daily per-capita terms and uses the greater of the international poverty line or the relative societal line.

## Counts

| Metric | Value | Interpretation |
|---|---:|---|
| requirement_rows | 207 | Country-wave denominator component requirement rows. |
| country_wave_rows | 23 | Priority bundle country-waves assessed. |
| source_matrix_rows | 18 | Reference/source role rows. |
| ready_for_sdg382_construction_rows | 0 | Rows ready for household denominator value audit. |
| blocked_country_wave_rows | 23 | Rows still blocked by raw or exact external denominator inputs. |
| component_gate_metadata_missing | 20 | Denominator component gate count. |
| component_gate_metadata_ready_raw_unverified | 187 | Denominator component gate count. |
| source_status_indicator_metadata_available | 8 | Source-matrix probe status count. |
| source_status_local_snapshot_present | 2 | Source-matrix probe status count. |
| source_status_not_probed | 2 | Source-matrix probe status count. |
| source_status_reachable_snapshot_saved | 4 | Source-matrix probe status count. |
| source_status_records_available | 2 | Source-matrix probe status count. |

## Component Gates

| Component gate status | Count |
|---|---:|
| metadata_ready_raw_unverified | 187 |
| metadata_missing | 20 |

## Country-Wave Readiness

| Readiness status | Count |
|---|---:|
| blocked_until_raw_and_external_denominator_audit | 23 |

| bundle_rank | country | wave | idno | component_rows | blocked_component_rows | readiness_status |
|---|---|---|---|---|---|---|
| 1 | Albania | 2005 | ALB_2005_LSMS_v01_M | 9 | 9 | blocked_until_raw_and_external_denominator_audit |
| 2 | Ethiopia | 2021-2022 | ETH_2021_ESPS-W5_v02_M | 9 | 9 | blocked_until_raw_and_external_denominator_audit |
| 3 | Ethiopia | 2018-2019 | ETH_2018_ESS_v04_M | 9 | 9 | blocked_until_raw_and_external_denominator_audit |
| 4 | Jamaica | 1997 | JAM_1997_SLC_v01_M | 9 | 9 | blocked_until_raw_and_external_denominator_audit |
| 5 | Kyrgyz Republic | 1993 | KGZ_1993_KMPS_v01_M | 9 | 9 | blocked_until_raw_and_external_denominator_audit |
| 6 | Malawi | 2007-2009 | MWI_2007-2009_MTM_v01_M | 9 | 9 | blocked_until_raw_and_external_denominator_audit |
| 7 | Malawi | 2004-2005 | MWI_2004_IHS-II_v01_M | 9 | 9 | blocked_until_raw_and_external_denominator_audit |
| 8 | Nepal | 2010-2011 | NPL_2010_LSS-III_v01_M | 9 | 9 | blocked_until_raw_and_external_denominator_audit |
| 9 | Nigeria | 2012-2013 | NGA_2012_GHSP-W2_v02_M | 9 | 9 | blocked_until_raw_and_external_denominator_audit |
| 10 | Nigeria | 2015-2016 | NGA_2015_GHSP-W3_v02_M | 9 | 9 | blocked_until_raw_and_external_denominator_audit |
| 11 | Nigeria | 2010-2011 | NGA_2010_GHSP-W1_v03_M | 9 | 9 | blocked_until_raw_and_external_denominator_audit |
| 12 | Tanzania | 2008-2009 | TZA_2008_NPS-R1_v03_M | 9 | 9 | blocked_until_raw_and_external_denominator_audit |
| 13 | Tanzania | 2010-2011 | TZA_2010_NPS-R2_v03_M | 9 | 9 | blocked_until_raw_and_external_denominator_audit |
| 14 | Tanzania | 2012-2013 | TZA_2012_NPS-R3_v01_M | 9 | 9 | blocked_until_raw_and_external_denominator_audit |
| 15 | Uganda | 2014 | UGA_2014_SAGE-EL_v01_M | 9 | 9 | blocked_until_raw_and_external_denominator_audit |

## Source Matrix Status

| Source status | Count |
|---|---:|
| indicator_metadata_available | 8 |
| reachable_snapshot_saved | 4 |
| not_probed | 2 |
| local_snapshot_present | 2 |
| records_available | 2 |

## Guardrails

- Do not construct `sdg382_discretionary_40` from CHE10/CHE25 denominators.
- Do not infer SPL from a poverty-headcount indicator alone.
- Do not use WDI PPP/CPI context as the exact SDG denominator without verifying 2017 PPP/PIP compatibility.
- Do not interpret country-wave SDG 3.8.2 unless raw OOP, welfare, household size, survey period, weights, SPL, PPP/CPI, and benchmark checks pass.

## Outputs

- `temp/sdg382_denominator_requirements.csv`
- `result/sdg382_denominator_source_matrix.csv`
- `result/sdg382_denominator_country_wave_readiness.csv`
- `result/sdg382_denominator_summary.csv`
