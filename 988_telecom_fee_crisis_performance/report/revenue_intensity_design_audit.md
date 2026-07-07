# Revenue-Intensity Design Audit

## Design Tested

The rescue layer tested observed annual FCC fee revenue per capita, a 12-month lag of observed revenue per capita, statutory fee amount per line, and event time around first positive annual revenue. Revenue is observed only annually through calendar year 2024, so it cannot identify monthly staffing/disbursement timing.

## Model Results

| design_family | treatment_definition | outcome | term | estimate | std_error_cluster | p_value | nobs | n_clusters |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| revenue_intensity | observed annual revenue per capita, same year | in_state_answer_rate_rescue | fee_revenue_per_capita_observed_2021_2024 | -0.56 pp | 0.59 pp | 0.349 | 2936 | 51 |
| revenue_intensity | observed annual revenue per capita, same year | flowout_to_national_backup_rate | fee_revenue_per_capita_observed_2021_2024 | 0.56 pp | 0.51 pp | 0.278 | 2936 | 51 |
| revenue_intensity | observed annual revenue per capita, same year | abandoned_in_state_rate | fee_revenue_per_capita_observed_2021_2024 | -0.01 pp | 0.11 pp | 0.956 | 2936 | 51 |
| revenue_intensity | observed annual revenue per capita, same year | average_speed_to_answer_seconds | fee_revenue_per_capita_observed_2021_2024 | -0.8785 | 0.3538 | 0.016 | 2936 | 51 |
| revenue_intensity | observed annual revenue per capita, 12-month lag | in_state_answer_rate_rescue | lag12_revenue_per_capita | 0.42 pp | 0.27 pp | 0.131 | 2936 | 51 |
| revenue_intensity | observed annual revenue per capita, 12-month lag | flowout_to_national_backup_rate | lag12_revenue_per_capita | -0.17 pp | 0.24 pp | 0.473 | 2936 | 51 |
| revenue_intensity | observed annual revenue per capita, 12-month lag | abandoned_in_state_rate | lag12_revenue_per_capita | -0.19 pp | 0.28 pp | 0.491 | 2936 | 51 |
| revenue_intensity | observed annual revenue per capita, 12-month lag | average_speed_to_answer_seconds | lag12_revenue_per_capita | 0.1467 | 0.6110 | 0.811 | 2936 | 51 |
| revenue_intensity | statutory fee amount per line | in_state_answer_rate_rescue | fee_amount_per_line_dollars | 0.81 pp | 5.66 pp | 0.887 | 2925 | 51 |
| revenue_intensity | statutory fee amount per line | flowout_to_national_backup_rate | fee_amount_per_line_dollars | -0.25 pp | 6.31 pp | 0.968 | 2925 | 51 |
| revenue_intensity | statutory fee amount per line | abandoned_in_state_rate | fee_amount_per_line_dollars | -0.13 pp | 2.19 pp | 0.953 | 2925 | 51 |
| revenue_intensity | statutory fee amount per line | average_speed_to_answer_seconds | fee_amount_per_line_dollars | -0.6563 | 8.4517 | 0.938 | 2925 | 51 |
| revenue_intensity | event time by first positive annual revenue year | in_state_answer_rate_rescue | first_revenue_positive_start | 2.62 pp | NA |  | 2936 | 51 |
| revenue_intensity | event time by first positive annual revenue year | flowout_to_national_backup_rate | first_revenue_positive_start | -1.36 pp | NA |  | 2936 | 51 |
| revenue_intensity | event time by first positive annual revenue year | abandoned_in_state_rate | first_revenue_positive_start | -1.14 pp | NA |  | 2936 | 51 |
| revenue_intensity | event time by first positive annual revenue year | average_speed_to_answer_seconds | first_revenue_positive_start | -1.3980 | NA |  | 2936 | 51 |

## IV Exploration

Candidate instruments were rejected:

- Pre-existing 911 fee infrastructure x post-988 authorization: nearly universal and strongly tied to state emergency-service administrative capacity.
- Pre-period telecom subscriber/access-line base x statutory fee rate: subscriber-base data are not in the current public panel, and fee-rate setting is itself policy-selected.
- Pre-existing access-line base x adoption framework: likely violates exclusion through broader state telecom, emergency-service, and fiscal capacity channels.

## Decision

Weak as a causal design. Revenue intensity is substantively useful mechanism evidence, but actual revenue is a post-adoption policy outcome and is observed too coarsely. A skeptical referee would treat the dose-response models as descriptive unless a credible external funding shock or valid instrument is found.
