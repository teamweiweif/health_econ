# Mechanism Analysis Protocol

Status: planned and fail-closed. No mechanism claim is currently supported because raw mechanism variables, harmonized outcomes, climate linkage, and main-effect identification gates have not passed.

## Purpose

This protocol maps the Phase 11 mechanism pathways to required raw concepts and protects the main causal design from post-treatment controls. Mechanism variables may be modeled as separate outcomes or mediators only after raw values, timing, denominators, and lineage are audited.

## Counts

| Metric | Value | Interpretation |
|---|---:|---|
| requirement_rows | 1449 | Country-wave pathway concept requirement rows. |
| pathway_protocol_rows | 7 | Mechanism pathway protocol rows. |
| readiness_rows | 161 | Country-wave by mechanism pathway readiness rows. |
| country_wave_rows | 23 | Country-waves assessed. |
| mechanism_pathway_count | 7 | Mechanism pathways assessed. |
| ready_pathway_rows | 0 | Country-wave pathway rows ready for mechanism analysis design. |
| blocked_pathway_rows | 161 | Country-wave pathway rows blocked by raw evidence or upstream gates. |
| raw_variable_catalog_rows | 5410 | Inspected raw variable catalog rows. |
| requirement_gate_metadata_incomplete | 212 | Mechanism requirement gate status count. |
| requirement_gate_metadata_ready_raw_unverified | 1174 | Mechanism requirement gate status count. |
| requirement_gate_raw_concept_verified | 63 | Mechanism requirement gate status count. |
| readiness_status_blocked_until_required_raw_mechanism_concepts_verified | 154 | Mechanism readiness status count. |
| readiness_status_blocked_until_verified_harmonization_recipe | 7 | Mechanism readiness status count. |
| pathway_rows_coping_response_to_health_or_climate | 23 | Country-wave readiness row count by pathway. |
| pathway_rows_food_insecurity | 23 | Country-wave readiness row count by pathway. |
| pathway_rows_forgone_care_after_need | 23 | Country-wave readiness row count by pathway. |
| pathway_rows_health_need_illness | 23 | Country-wave readiness row count by pathway. |
| pathway_rows_income_consumption_decline | 23 | Country-wave readiness row count by pathway. |
| pathway_rows_oop_share_conditional_on_seeking | 23 | Country-wave readiness row count by pathway. |
| pathway_rows_uhc_double_failure_composite | 23 | Country-wave readiness row count by pathway. |

## Requirement Gates

| Requirement gate status | Count |
|---|---:|
| metadata_ready_raw_unverified | 1174 |
| metadata_incomplete | 212 |
| raw_concept_verified | 63 |

## Readiness

| Readiness status | Count |
|---|---:|
| blocked_until_required_raw_mechanism_concepts_verified | 154 |
| blocked_until_verified_harmonization_recipe | 7 |

## Pathway Coverage

| Mechanism pathway | Count |
|---|---:|
| coping_response_to_health_or_climate | 23 |
| food_insecurity | 23 |
| forgone_care_after_need | 23 |
| health_need_illness | 23 |
| income_consumption_decline | 23 |
| oop_share_conditional_on_seeking | 23 |
| uhc_double_failure_composite | 23 |

| bundle_rank | country | wave | idno | mechanism_pathway | blocked_required_rows | readiness_status |
|---|---|---|---|---|---|---|
| 1 | Albania | 2005 | ALB_2005_LSMS_v01_M | coping_response_to_health_or_climate | 0 | blocked_until_verified_harmonization_recipe |
| 1 | Albania | 2005 | ALB_2005_LSMS_v01_M | food_insecurity | 0 | blocked_until_verified_harmonization_recipe |
| 1 | Albania | 2005 | ALB_2005_LSMS_v01_M | forgone_care_after_need | 0 | blocked_until_verified_harmonization_recipe |
| 1 | Albania | 2005 | ALB_2005_LSMS_v01_M | health_need_illness | 0 | blocked_until_verified_harmonization_recipe |
| 1 | Albania | 2005 | ALB_2005_LSMS_v01_M | income_consumption_decline | 0 | blocked_until_verified_harmonization_recipe |
| 1 | Albania | 2005 | ALB_2005_LSMS_v01_M | oop_share_conditional_on_seeking | 0 | blocked_until_verified_harmonization_recipe |
| 1 | Albania | 2005 | ALB_2005_LSMS_v01_M | uhc_double_failure_composite | 0 | blocked_until_verified_harmonization_recipe |
| 2 | Ethiopia | 2021-2022 | ETH_2021_ESPS-W5_v02_M | coping_response_to_health_or_climate | 4 | blocked_until_required_raw_mechanism_concepts_verified |
| 2 | Ethiopia | 2021-2022 | ETH_2021_ESPS-W5_v02_M | food_insecurity | 4 | blocked_until_required_raw_mechanism_concepts_verified |
| 2 | Ethiopia | 2021-2022 | ETH_2021_ESPS-W5_v02_M | forgone_care_after_need | 5 | blocked_until_required_raw_mechanism_concepts_verified |
| 2 | Ethiopia | 2021-2022 | ETH_2021_ESPS-W5_v02_M | health_need_illness | 4 | blocked_until_required_raw_mechanism_concepts_verified |
| 2 | Ethiopia | 2021-2022 | ETH_2021_ESPS-W5_v02_M | income_consumption_decline | 4 | blocked_until_required_raw_mechanism_concepts_verified |
| 2 | Ethiopia | 2021-2022 | ETH_2021_ESPS-W5_v02_M | oop_share_conditional_on_seeking | 5 | blocked_until_required_raw_mechanism_concepts_verified |
| 2 | Ethiopia | 2021-2022 | ETH_2021_ESPS-W5_v02_M | uhc_double_failure_composite | 7 | blocked_until_required_raw_mechanism_concepts_verified |
| 3 | Ethiopia | 2018-2019 | ETH_2018_ESS_v04_M | coping_response_to_health_or_climate | 4 | blocked_until_required_raw_mechanism_concepts_verified |
| 3 | Ethiopia | 2018-2019 | ETH_2018_ESS_v04_M | food_insecurity | 4 | blocked_until_required_raw_mechanism_concepts_verified |
| 3 | Ethiopia | 2018-2019 | ETH_2018_ESS_v04_M | forgone_care_after_need | 5 | blocked_until_required_raw_mechanism_concepts_verified |
| 3 | Ethiopia | 2018-2019 | ETH_2018_ESS_v04_M | health_need_illness | 4 | blocked_until_required_raw_mechanism_concepts_verified |
| 3 | Ethiopia | 2018-2019 | ETH_2018_ESS_v04_M | income_consumption_decline | 4 | blocked_until_required_raw_mechanism_concepts_verified |
| 3 | Ethiopia | 2018-2019 | ETH_2018_ESS_v04_M | oop_share_conditional_on_seeking | 5 | blocked_until_required_raw_mechanism_concepts_verified |

## Guardrails

- Do not include post-shock income, food insecurity, health need, care-seeking, OOP spending, or coping variables as controls in the main climate-effect model.
- Do not force a mechanism where raw questionnaire wording, recall period, denominator, and value coding do not support it.
- Do not pool mechanism estimates across country-waves unless construct definitions and recall windows are comparable.
- If only the main outcome is supported, report mechanisms as unavailable rather than speculative.

## Outputs

- `temp/mechanism_variable_requirements.csv`
- `result/mechanism_pathway_protocol.csv`
- `result/mechanism_readiness_matrix.csv`
- `result/mechanism_analysis_protocol_summary.csv`
