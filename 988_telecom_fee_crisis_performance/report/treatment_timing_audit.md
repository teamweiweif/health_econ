# Treatment Timing Audit

## State-by-State Fee Timing

| state | state_name | bill_number | bill_enactment_date | statutory_effective_date | fee_collection_start_date | first_observed_fee_revenue_date | revenue_timing_precision | first_operational_use_date | fund_scope | fee_amount_and_base | preexisting_911_fee_infrastructure | confidence_rating | audit_note |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| VA | Virginia | SB1302 | 2021-03-18 | 2021-07-01 | 2021-07-01 | 2021-07-01 | annual FCC revenue observed; month inferred from collection/effective timing, not directly observed | 2021-10-01 | 988 call center fund | $0.12 postpaid wireless; $0.08 prepaid wireless | 1.0 | high | Enactment and collection are source-supported; operational use remains a 3-month analytic lag. |
| WA | Washington | HB1477 | 2021-05-13 | 2021-07-25 | 2021-10-01 | 2021-10-01 | annual FCC revenue observed; month inferred from collection/effective timing, not directly observed | 2022-01-01 | behavioral health crisis response and suicide prevention line | $0.24 per line initially; $0.40 from 2023 in coded schedule | 1.0 | high | Collection start is high-confidence; operational date is analytic lag. |
| CO | Colorado | SB21-154 | 2021-07-06 | 2021-07-06 | 2022-01-01 | 2022-01-01 | annual FCC revenue observed; month inferred from collection/effective timing, not directly observed | 2022-04-01 | 988 crisis hotline enterprise and crisis care coordination | annual enterprise-set line/prepaid fee, maximum $0.30; coded as 18/27/14/7 cents by year | 1.0 | medium_high | Collection start is high-confidence; exact enactment date should be rechecked before manuscript submission. |
| CA | California | AB988 | 2022-09-29 | 2023-01-01 | 2023-01-01 | 2023-01-01 | annual FCC revenue observed; month inferred from collection/effective timing, not directly observed | 2023-04-01 | 988 state suicide and behavioral health crisis services fund | $0.08 per access line for 2023-2025; $0.05 in 2026 in coded schedule | 1.0 | high | Effective and collection date are direct tax-administration dates. |
| NV | Nevada | Temporary regulation T004-23A | 2023-01-20 | 2023-06-01 | 2023-06-01 | 2023-06-01 | annual FCC revenue observed; month inferred from collection/effective timing, not directly observed | 2023-09-01 | 988 surcharge for crisis response program | $0.35 per telecommunications access line | 1.0 | medium_high | Regulatory path differs from ordinary legislative enactment. |
| DE | Delaware | HS1 for HB160 | 2023-08-03 | 2024-01-01 | 2024-01-01 | 2024-01-01 | annual FCC revenue observed; month inferred from collection/effective timing, not directly observed | 2024-04-01 | behavioral health crisis intervention services surcharge | $0.60 monthly and prepaid surcharge | 1.0 | medium_high | Effective and collection dates align with FCC/state coding. |
| MN | Minnesota | SF2588/HF1566 provisions | 2023-05-24 | 2024-01-01 | 2024-01-01 | 2024-01-01 | annual FCC revenue observed; month inferred from collection/effective timing, not directly observed | 2024-04-01 | statewide 988 suicide prevention crisis system and related costs | $0.12 per consumer access line; prepaid timing differs | 1.0 | medium_high | Postpaid fee began 2024; prepaid implementation changed later. |
| OR | Oregon | HB2757 | 2023-07-27 | 2024-01-01 | 2024-01-01 | 2024-01-01 | annual FCC revenue observed; month inferred from collection/effective timing, not directly observed | 2024-04-01 | 988 coordinated crisis services and mobile crisis when resources allow | $0.40 per line/VoIP service and prepaid transaction | 1.0 | high | Tax applies to subscriber bills and retail transactions on or after January 1, 2024. |
| MD | Maryland | SB974/HB933 | 2024-05-16 | 2024-10-01 | 2024-10-01 | 2024-10-01 | annual FCC revenue observed; month inferred from collection/effective timing, not directly observed | 2025-01-01 | 9-8-8 Trust Fund fees for behavioral health crisis response services | $0.25 per 988-accessible service; prepaid later | 1.0 | high | Governor approval and effective date are source-supported. |
| VT | Vermont | H.657 / Act 145 | 2024-06-03 | 2025-07-01 | 2025-07-01 |  | not observed in current FCC annual revenue window | 2025-10-01 | Vermont 988 Suicide and Crisis Lifeline | VUSF per-line contribution allocation; amount not coded from FCC report | 1.0 | medium_high | No 2024 fee revenue observed in FCC report. |
| NM | New Mexico | SB535 | 2025-04-08 | 2025-07-01 | 2025-07-01 |  | not observed in current FCC annual revenue window | 2025-10-01 | 988 lifeline fund supported by telecom relay surcharge increase | relay surcharge increased from 0.33% to 1.66%; 80% of increase to 988 lifeline fund | 1.0 | medium_high | Outside FCC revenue window and post-2025 monitor status in original data. |
| IL | Illinois | HB2755 / SB2120 related language | 2025-06-01 | 2025-06-01 | 2025-07-01 |  | not observed in current FCC annual revenue window | 2025-10-01 | Statewide 9-8-8 Trust Fund and intrastate telecommunications tax surcharge | 1.65 percentage-point intrastate telecommunications tax increase designated for 988 | 1.0 | low_medium | FCC notes 2025 legislation after the 2024 reporting period; revenue not yet observed. |
| VI | U.S. Virgin Islands | authority reported to FCC |  |  |  |  | not observed in current FCC annual revenue window |  | authority reported but no collection through 2024 | not collected by 2024 |  | medium | Not part of state/DC causal sample and no observed collection. |

## Revised Treatment Definitions

The rescue layer rebuilt active-treatment variables for enactment, collection start, operational lags of 0, 1, 3, 6, and 12 months, first positive annual revenue, fee amount per line, revenue per capita, revenue per routed contact, restricted 988-only funding, and broader crisis-system funding.

## Answer-Rate Sensitivity: Not-Yet-Treated ATT

| treatment_definition | overall_att | pre_mean_abs_att | att_cells | treated_cohorts |
| --- | --- | --- | --- | --- |
| enactment date | 0.90 pp | 10.31 pp | 1 | 1 |
| collection start | 2.31 pp | 4.06 pp | 180 | 7 |
| collection plus 0 months | 2.31 pp | 4.06 pp | 180 | 7 |
| collection plus 1 month | 3.50 pp | 4.10 pp | 208 | 8 |
| collection plus 3 months | 6.77 pp | 5.61 pp | 202 | 8 |
| collection plus 6 months | 3.33 pp | 4.14 pp | 193 | 8 |
| collection plus 12 months | 0.66 pp | 5.63 pp | 166 | 7 |
| first positive annual revenue | 2.62 pp | 3.84 pp | 169 | 6 |

## Answer-Rate Sensitivity: TWFE Diagnostics

| treatment_definition | term | estimate | std_error_cluster | p_value | nobs | n_clusters |
| --- | --- | --- | --- | --- | --- | --- |
| enactment date | enacted_active | -1.57 pp | 2.37 pp | 0.512 | 2936 | 51 |
| collection start | collection_start_audit_active | -0.95 pp | 2.20 pp | 0.668 | 2936 | 51 |
| collection plus 0 months | operational_lag_0m_active | -0.95 pp | 2.20 pp | 0.668 | 2936 | 51 |
| collection plus 1 month | operational_lag_1m_active | -0.50 pp | 2.10 pp | 0.815 | 2936 | 51 |
| collection plus 3 months | operational_lag_3m_active | 0.69 pp | 2.03 pp | 0.738 | 2936 | 51 |
| collection plus 6 months | operational_lag_6m_active | 1.70 pp | 2.19 pp | 0.443 | 2936 | 51 |
| collection plus 12 months | operational_lag_12m_active | 2.11 pp | 2.26 pp | 0.356 | 2936 | 51 |
| first positive annual revenue | revenue_positive_active | -0.23 pp | 2.32 pp | 0.920 | 2936 | 51 |
| fee amount per line | fee_amount_per_line_dollars | 0.95 pp | 5.65 pp | 0.867 | 2936 | 51 |
| annual fee revenue per capita | fee_revenue_per_capita | -0.56 pp | 0.59 pp | 0.349 | 2936 | 51 |
| annual fee revenue per routed contact | fee_revenue_per_routed_contact | -0.00 pp | 0.00 pp | 0.734 | 2936 | 51 |
| restricted 988-only funding active | restricted_988_only_active | -5.24 pp | 1.57 pp | 0.002 | 2936 | 51 |
| broader crisis-system funding active | broader_crisis_system_active | 0.45 pp | 2.53 pp | 0.860 | 2936 | 51 |

## Interpretation

The sign and size of the corrected answer-rate ATT vary across timing definitions. Collection/enactment definitions and revenue-based definitions are not externally assigned; changing the date convention does not remove policy selection. The three-month lag remains a reasonable operational convention, not a credible source of quasi-random variation.
