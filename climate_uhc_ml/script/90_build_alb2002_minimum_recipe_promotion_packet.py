from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

from common import REPORT_DIR, RESULT_DIR, TEMP_DIR, append_log, ensure_dirs, write_csv


IDNO = "ALB_2002_LSMS_v01_M"
COUNTRY = "Albania"
SURVEY_NAME = "Living Standards Measurement Survey 2002"
WAVE = "2002"

CORE_SUMMARY_PATH = RESULT_DIR / "alb2002_household_core_candidate_summary.csv"
PROVISIONAL_OUTCOME_SUMMARY_PATH = RESULT_DIR / "alb2002_provisional_outcome_feasibility_summary.csv"
OUTCOME_SEMANTICS_SUMMARY_PATH = RESULT_DIR / "alb2002_outcome_semantics_raw_value_summary.csv"
HEALTH_QUESTIONNAIRE_SUMMARY_PATH = RESULT_DIR / "alb2002_health_questionnaire_semantics_summary.csv"
OOP_POLICY_SUMMARY_PATH = RESULT_DIR / "alb2002_oop_aggregation_policy_summary.csv"
PERIOD_ALIGNED_CHE_SUMMARY_PATH = RESULT_DIR / "alb2002_period_aligned_che_policy_summary.csv"
UHC_COMPOSITE_SUMMARY_PATH = RESULT_DIR / "alb2002_uhc_composite_candidate_summary.csv"
WEIGHT_DESIGN_SUMMARY_PATH = RESULT_DIR / "alb2002_weight_design_evidence_summary.csv"
SAMPLE_DESIGN_SUMMARY_PATH = RESULT_DIR / "alb2002_sample_design_documentation_summary.csv"
SKIP_MISSING_SUMMARY_PATH = RESULT_DIR / "alb2002_skip_missing_semantics_summary.csv"
OOP_SKIP_VALUE_SUMMARY_PATH = RESULT_DIR / "alb2002_oop_skip_value_decision_summary.csv"
ACCESS_NEED_SUMMARY_PATH = RESULT_DIR / "alb2002_access_need_denominator_policy_summary.csv"
ACCESS_CANDIDATE_SUMMARY_PATH = RESULT_DIR / "alb2002_access_candidate_outcome_summary.csv"
CONSUMPTION_SDG_SUMMARY_PATH = RESULT_DIR / "alb2002_consumption_sdg_denominator_policy_summary.csv"
CONSUMPTION_AGGREGATE_SUMMARY_PATH = RESULT_DIR / "alb2002_consumption_aggregate_metadata_crosswalk_summary.csv"
DISTRICT_CROSSWALK_SUMMARY_PATH = RESULT_DIR / "alb2002_district_climate_crosswalk_summary.csv"
CLIMATE_SHOCK_SUMMARY_PATH = RESULT_DIR / "alb2002_climate_shock_candidate_summary.csv"
CLIMATE_OUTCOME_LINKED_SUMMARY_PATH = RESULT_DIR / "alb2002_climate_outcome_linked_candidate_summary.csv"
BOUNDARY_MANUAL_SUMMARY_PATH = RESULT_DIR / "alb2002_boundary_manual_verification_packet_summary.csv"
BOUNDARY_FOLLOWUP_SUMMARY_PATH = RESULT_DIR / "alb2002_boundary_manual_source_followup_summary.csv"
GADM_SUMMARY_PATH = RESULT_DIR / "alb2002_gadm_boundary_lead_summary.csv"

ACTION_QUEUE_PATH = TEMP_DIR / "alb2002_minimum_recipe_promotion_action_queue.csv"
GATE_CHECKLIST_PATH = TEMP_DIR / "alb2002_minimum_recipe_promotion_gate_checklist.csv"
SUMMARY_PATH = RESULT_DIR / "alb2002_minimum_recipe_promotion_summary.csv"
REPORT_PATH = REPORT_DIR / "alb2002_minimum_recipe_promotion_packet.md"

DECISION = "blocked_alb2002_minimum_recipe_not_ready_for_promotion"

ACTION_COLUMNS = [
    "action_rank",
    "gate_id",
    "blocker_domain",
    "current_evidence",
    "blocking_status",
    "required_resolution",
    "acceptance_evidence",
    "post_resolution_commands",
]
GATE_COLUMNS = [
    "gate_id",
    "gate_label",
    "required_for",
    "current_status",
    "current_evidence",
    "minimum_evidence_to_pass",
    "promotion_effect_if_passed",
    "fail_closed_stop_rule",
]
SUMMARY_COLUMNS = ["metric", "value", "interpretation"]


def read_csv_dicts(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def metric_value(rows: list[dict[str, str]], metric: str, default: str = "0") -> str:
    return next((row.get("value", default) for row in rows if row.get("metric") == metric), default)


def int_value(value: Any) -> int:
    try:
        return int(float(str(value).strip()))
    except (TypeError, ValueError):
        return 0


def action_row(rank: int, gate_id: str, blocker_domain: str, current_evidence: str, blocking_status: str, required_resolution: str, acceptance_evidence: str) -> dict[str, str]:
    return {
        "action_rank": str(rank),
        "gate_id": gate_id,
        "blocker_domain": blocker_domain,
        "current_evidence": current_evidence,
        "blocking_status": blocking_status,
        "required_resolution": required_resolution,
        "acceptance_evidence": acceptance_evidence,
        "post_resolution_commands": "python script/54_audit_alb2002_household_core_merge.py; python script/55_audit_alb2002_provisional_outcome_feasibility.py; python script/60_audit_alb2002_outcome_semantics_raw_values.py; python script/89_audit_alb2002_health_questionnaire_semantics.py; python script/91_audit_alb2002_oop_aggregation_policy.py; python script/92_audit_alb2002_skip_missing_semantics.py; python script/97_audit_alb2002_oop_skip_value_decision.py; python script/93_audit_alb2002_access_need_denominator_policy.py; python script/105_build_alb2002_access_candidate_outcomes.py; python script/94_audit_alb2002_consumption_sdg_denominator_policy.py; python script/96_audit_alb2002_consumption_construction_sources.py; python script/95_audit_alb2002_consumption_aggregate_metadata_crosswalk.py; python script/99_audit_alb2002_period_aligned_che_policy.py; python script/100_audit_alb2002_weight_design_evidence.py; python script/104_audit_alb2002_sample_design_documentation.py; python script/90_build_alb2002_minimum_recipe_promotion_packet.py; python script/101_build_alb2002_che_candidate_outcomes.py; python script/106_build_alb2002_uhc_composite_candidate_outcomes.py; python script/102_build_alb2002_analysis_candidate_dataset.py; python script/103_build_alb2002_climate_centroid_exposure_candidates.py; python script/107_build_alb2002_climate_shock_candidate_audit.py; python script/108_build_alb2002_climate_outcome_linked_candidate_audit.py; python script/109_build_alb2002_linked_candidate_descriptive_diagnostics.py; python script/90_build_alb2002_minimum_recipe_promotion_packet.py; python script/98_audit_analysis_dataset_promotion_barriers.py; python script/110_build_current_design_scorecard.py; python script/111_audit_alb2002_promotion_gate_delta.py; python script/112_build_alb2002_boundary_blocker_resolution_matrix.py; python script/113_build_alb2002_outcome_blocker_resolution_matrix.py; python script/57_audit_alb2012_raw_core_feasibility.py; python script/58_audit_alb2012_provisional_outcome_feasibility.py; python script/63_audit_alb2012_outcome_semantics_raw_values.py; python script/59_audit_alb2012_timing_geography_exhaustive.py; python script/65_audit_alb2012_questionnaire_timing_fields.py; python script/114_build_alb2012_timing_geography_blocker_resolution_matrix.py; python script/13_write_reports.py; python script/14_validate_workspace.py",
    }


def gate_row(gate_id: str, label: str, required_for: str, status: str, evidence: str, minimum: str, effect: str, stop_rule: str) -> dict[str, str]:
    return {
        "gate_id": gate_id,
        "gate_label": label,
        "required_for": required_for,
        "current_status": status,
        "current_evidence": evidence,
        "minimum_evidence_to_pass": minimum,
        "promotion_effect_if_passed": effect,
        "fail_closed_stop_rule": stop_rule,
    }


def summary_row(metric: str, value: Any, interpretation: str) -> dict[str, str]:
    return {"metric": metric, "value": str(value), "interpretation": interpretation}


def build_packet() -> tuple[list[dict[str, str]], list[dict[str, str]], list[dict[str, str]]]:
    core = read_csv_dicts(CORE_SUMMARY_PATH)
    provisional = read_csv_dicts(PROVISIONAL_OUTCOME_SUMMARY_PATH)
    semantics = read_csv_dicts(OUTCOME_SEMANTICS_SUMMARY_PATH)
    questionnaire = read_csv_dicts(HEALTH_QUESTIONNAIRE_SUMMARY_PATH)
    oop_policy = read_csv_dicts(OOP_POLICY_SUMMARY_PATH)
    period_aligned_che = read_csv_dicts(PERIOD_ALIGNED_CHE_SUMMARY_PATH)
    uhc_composite = read_csv_dicts(UHC_COMPOSITE_SUMMARY_PATH)
    weight_design = read_csv_dicts(WEIGHT_DESIGN_SUMMARY_PATH)
    sample_design = read_csv_dicts(SAMPLE_DESIGN_SUMMARY_PATH)
    skip_missing = read_csv_dicts(SKIP_MISSING_SUMMARY_PATH)
    oop_skip_value = read_csv_dicts(OOP_SKIP_VALUE_SUMMARY_PATH)
    access_need = read_csv_dicts(ACCESS_NEED_SUMMARY_PATH)
    access_candidate = read_csv_dicts(ACCESS_CANDIDATE_SUMMARY_PATH)
    consumption_sdg = read_csv_dicts(CONSUMPTION_SDG_SUMMARY_PATH)
    consumption_aggregate = read_csv_dicts(CONSUMPTION_AGGREGATE_SUMMARY_PATH)
    crosswalk = read_csv_dicts(DISTRICT_CROSSWALK_SUMMARY_PATH)
    climate_shock = read_csv_dicts(CLIMATE_SHOCK_SUMMARY_PATH)
    climate_outcome_linked = read_csv_dicts(CLIMATE_OUTCOME_LINKED_SUMMARY_PATH)
    boundary_manual = read_csv_dicts(BOUNDARY_MANUAL_SUMMARY_PATH)
    boundary_followup = read_csv_dicts(BOUNDARY_FOLLOWUP_SUMMARY_PATH)
    gadm = read_csv_dicts(GADM_SUMMARY_PATH)

    candidate_rows = metric_value(core, "alb2002_household_core_candidate_rows")
    total_consumption_rows = metric_value(core, "alb2002_households_with_total_consumption")
    weight_rows = metric_value(core, "alb2002_households_with_household_weight")
    oop_4w_positive = metric_value(core, "alb2002_households_with_oop_4w_positive")
    oop_12m_positive = metric_value(core, "alb2002_households_with_oop_12m_positive")
    district_code_rows = metric_value(core, "alb2002_households_with_district_code")
    survey_month_rows = metric_value(core, "alb2002_households_with_survey_month")
    interview_date_rows = metric_value(core, "alb2002_households_with_interview_date")
    core_recipe_ready = metric_value(core, "alb2002_household_core_recipe_ready_rows")
    core_decision = metric_value(core, "alb2002_household_core_current_decision", "missing")
    weight_design_audit_rows = metric_value(weight_design, "alb2002_weight_design_evidence_audit_rows")
    weight_design_source_flags = metric_value(weight_design, "alb2002_weight_design_source_page_flag_rows")
    weight_design_raw_rows = metric_value(weight_design, "alb2002_weight_design_raw_weight_file_rows")
    weight_design_positive_rows = metric_value(weight_design, "alb2002_weight_design_positive_weight_rows")
    weight_design_key_match_rows = metric_value(weight_design, "alb2002_weight_design_candidate_key_match_rows")
    weight_design_distinct_psu = metric_value(weight_design, "alb2002_weight_design_distinct_psu_rows")
    weight_design_distinct_stratum = metric_value(weight_design, "alb2002_weight_design_distinct_stratum_rows")
    weight_design_inference_ready = metric_value(weight_design, "alb2002_weight_design_weighted_inference_ready_rows")
    weight_design_harmonized_ready = metric_value(weight_design, "alb2002_weight_design_harmonized_promotion_ready_rows")
    weight_design_decision = metric_value(weight_design, "alb2002_weight_design_current_decision", "missing")
    sample_design_doc_ready = metric_value(sample_design, "alb2002_sample_design_documentation_ready_rows")
    sample_design_pdf_pages = metric_value(sample_design, "alb2002_sample_design_pdf_pages")
    sample_design_official_design = metric_value(sample_design, "alb2002_sample_design_official_450_psu_8_hh_rows")
    sample_design_official_final = metric_value(sample_design, "alb2002_sample_design_official_3599_final_rows")
    sample_design_raw_concordance = metric_value(sample_design, "alb2002_sample_design_raw_design_concordance_rows")
    sample_design_weighted_inference_ready = metric_value(sample_design, "alb2002_sample_design_weighted_inference_ready_rows")
    sample_design_decision = metric_value(sample_design, "alb2002_sample_design_current_decision", "missing")

    provisional_outcome_ready = metric_value(provisional, "alb2002_provisional_outcome_ready_rows")
    outcome_ready = metric_value(semantics, "alb2002_outcome_semantics_outcome_ready_rows")
    sdg_ready = metric_value(semantics, "alb2002_outcome_semantics_sdg382_ready_rows")
    oop_candidate_rows = metric_value(semantics, "alb2002_outcome_semantics_financial_oop_candidate_rows")
    access_candidate_rows = metric_value(semantics, "alb2002_outcome_semantics_access_candidate_rows")
    conditional_reason_rows = metric_value(semantics, "alb2002_outcome_semantics_conditional_reason_rows")

    questionnaire_rows = metric_value(questionnaire, "alb2002_health_questionnaire_semantics_rows")
    questionnaire_oop_rows = metric_value(questionnaire, "alb2002_health_questionnaire_oop_item_rows")
    questionnaire_gift_rows = metric_value(questionnaire, "alb2002_health_questionnaire_gift_item_rows")
    questionnaire_new_lek_rows = metric_value(questionnaire, "alb2002_health_questionnaire_new_lek_unit_rows")
    questionnaire_four_week_rows = metric_value(questionnaire, "alb2002_health_questionnaire_four_week_oop_rows")
    questionnaire_twelve_month_rows = metric_value(questionnaire, "alb2002_health_questionnaire_twelve_month_oop_rows")
    questionnaire_access_rows = metric_value(questionnaire, "alb2002_health_questionnaire_access_rows")
    questionnaire_payment_positive_skip = metric_value(questionnaire, "alb2002_health_questionnaire_payment_positive_when_not_triggered_rows")
    questionnaire_payment_nonmissing_skip = metric_value(questionnaire, "alb2002_health_questionnaire_payment_nonmissing_when_not_triggered_rows")
    questionnaire_recipe_ready = metric_value(questionnaire, "alb2002_health_questionnaire_recipe_ready_rows")
    questionnaire_outcome_ready = metric_value(questionnaire, "alb2002_health_questionnaire_outcome_ready_rows")
    questionnaire_climate_ready = metric_value(questionnaire, "alb2002_health_questionnaire_climate_linkage_ready_rows")
    oop_policy_rows = metric_value(oop_policy, "alb2002_oop_aggregation_policy_rows")
    oop_policy_core_4w_match = metric_value(oop_policy, "alb2002_oop_aggregation_policy_core_4w_match_rows")
    oop_policy_core_12m_match = metric_value(oop_policy, "alb2002_oop_aggregation_policy_core_12m_match_rows")
    oop_policy_max_che10 = metric_value(oop_policy, "alb2002_oop_aggregation_policy_max_che10_rate")
    oop_policy_max_che25 = metric_value(oop_policy, "alb2002_oop_aggregation_policy_max_che25_rate")
    oop_policy_outcome_ready = metric_value(oop_policy, "alb2002_oop_aggregation_policy_outcome_ready_rows")
    oop_policy_recipe_ready = metric_value(oop_policy, "alb2002_oop_aggregation_policy_recipe_ready_rows")
    oop_policy_sdg_ready = metric_value(oop_policy, "alb2002_oop_aggregation_policy_sdg382_ready_rows")
    period_aligned_che_policy_rows = metric_value(period_aligned_che, "alb2002_period_aligned_che_policy_rows")
    period_aligned_che_denominator_rows = metric_value(period_aligned_che, "alb2002_period_aligned_che_denominator_rows")
    period_aligned_che_denominator_documented = metric_value(period_aligned_che, "alb2002_period_aligned_che_denominator_documented_rows")
    period_aligned_che_zero_skip_ready = metric_value(period_aligned_che, "alb2002_period_aligned_che_zero_skip_ready_rows")
    period_aligned_che_period_ready = metric_value(period_aligned_che, "alb2002_period_aligned_che_period_alignment_ready_rows")
    period_aligned_che_combined_che10 = metric_value(period_aligned_che, "alb2002_period_aligned_che_combined_che10_rate", "")
    period_aligned_che_combined_che25 = metric_value(period_aligned_che, "alb2002_period_aligned_che_combined_che25_rate", "")
    period_aligned_che_outcome_ready = metric_value(period_aligned_che, "alb2002_period_aligned_che_outcome_ready_rows")
    period_aligned_che_recipe_ready = metric_value(period_aligned_che, "alb2002_period_aligned_che_recipe_ready_rows")
    period_aligned_che_sdg_ready = metric_value(period_aligned_che, "alb2002_period_aligned_che_sdg382_ready_rows")
    period_aligned_che_climate_ready = metric_value(period_aligned_che, "alb2002_period_aligned_che_climate_linkage_ready_rows")
    period_aligned_che_decision = metric_value(period_aligned_che, "alb2002_period_aligned_che_current_decision", "missing")
    uhc_composite_rows = metric_value(uhc_composite, "alb2002_uhc_composite_candidate_household_rows")
    uhc_composite_che10_or_access = metric_value(uhc_composite, "alb2002_uhc_composite_candidate_che10_or_access_rows")
    uhc_composite_che25_or_access = metric_value(uhc_composite, "alb2002_uhc_composite_candidate_che25_or_access_rows")
    uhc_composite_both_che10 = metric_value(uhc_composite, "alb2002_uhc_composite_candidate_both_che10_access_rows")
    uhc_composite_coping = metric_value(uhc_composite, "alb2002_uhc_composite_candidate_coping_rows")
    uhc_composite_outcome_ready = metric_value(uhc_composite, "alb2002_uhc_composite_candidate_outcome_promotion_ready_rows")
    uhc_composite_recipe_ready = metric_value(uhc_composite, "alb2002_uhc_composite_candidate_recipe_ready_rows")
    uhc_composite_climate_ready = metric_value(uhc_composite, "alb2002_uhc_composite_candidate_climate_linkage_ready_rows")
    skip_missing_rows = metric_value(skip_missing, "alb2002_skip_missing_semantics_rows")
    skip_payment_nonmissing_rows = metric_value(skip_missing, "alb2002_skip_missing_payment_nonmissing_when_not_triggered_rows")
    skip_payment_positive_rows = metric_value(skip_missing, "alb2002_skip_missing_payment_positive_when_not_triggered_rows")
    skip_payment_zero_cells = metric_value(skip_missing, "alb2002_skip_missing_payment_zero_cells_when_not_triggered")
    skip_payment_positive_cells = metric_value(skip_missing, "alb2002_skip_missing_payment_positive_cells_when_not_triggered")
    skip_payment_zero_only_blocks = metric_value(skip_missing, "alb2002_skip_missing_payment_zero_only_block_rows")
    skip_outcome_ready = metric_value(skip_missing, "alb2002_skip_missing_outcome_ready_rows")
    oop_skip_value_rows = metric_value(oop_skip_value, "alb2002_oop_skip_value_decision_rows")
    oop_skip_value_zero_ready = metric_value(oop_skip_value, "alb2002_oop_skip_value_zero_skip_policy_ready_rows")
    oop_skip_value_positive_rows = metric_value(oop_skip_value, "alb2002_oop_skip_value_payment_positive_skipped_rows")
    oop_skip_value_positive_cells = metric_value(oop_skip_value, "alb2002_oop_skip_value_payment_positive_skipped_cells")
    oop_skip_value_recall_ready = metric_value(oop_skip_value, "alb2002_oop_skip_value_oop_recall_scope_ready_rows")
    oop_skip_value_inclusion_ready = metric_value(oop_skip_value, "alb2002_oop_skip_value_oop_inclusion_scope_ready_rows")
    oop_skip_value_decision = metric_value(oop_skip_value, "alb2002_oop_skip_value_current_decision", "missing")
    access_need_policy_rows = metric_value(access_need, "alb2002_access_need_denominator_policy_rows")
    access_need_q01_need_rows = metric_value(access_need, "alb2002_access_need_q01_need_rows")
    access_need_person_need_rows = metric_value(access_need, "alb2002_access_need_person_need_household_rows")
    access_need_delayed_rows = metric_value(access_need, "alb2002_access_need_delayed_help_rows")
    access_need_referral_rows = metric_value(access_need, "alb2002_access_need_referral_not_gone_rows")
    access_need_refused_rows = metric_value(access_need, "alb2002_access_need_refused_service_rows")
    access_need_composite_any_rows = metric_value(access_need, "alb2002_access_need_composite_any_access_barrier_rows")
    access_need_low_event_rows = metric_value(access_need, "alb2002_access_need_low_event_rate_rows")
    access_need_outcome_ready = metric_value(access_need, "alb2002_access_need_outcome_ready_rows")
    access_need_recipe_ready = metric_value(access_need, "alb2002_access_need_recipe_ready_rows")
    access_candidate_household_rows = metric_value(access_candidate, "alb2002_access_candidate_household_rows")
    access_candidate_any_rows = metric_value(access_candidate, "alb2002_access_candidate_composite_any_rows")
    access_candidate_cost_rows = metric_value(access_candidate, "alb2002_access_candidate_composite_cost_rows")
    access_candidate_low_event_rows = metric_value(access_candidate, "alb2002_access_candidate_low_event_rate_rows")
    access_candidate_outcome_ready = metric_value(access_candidate, "alb2002_access_candidate_outcome_promotion_ready_rows")
    access_candidate_recipe_ready = metric_value(access_candidate, "alb2002_access_candidate_recipe_ready_rows")
    access_candidate_climate_ready = metric_value(access_candidate, "alb2002_access_candidate_climate_linkage_ready_rows")
    consumption_sdg_policy_rows = metric_value(consumption_sdg, "alb2002_consumption_sdg_denominator_policy_rows")
    consumption_sdg_positive_total_rows = metric_value(consumption_sdg, "alb2002_consumption_sdg_positive_total_consumption_rows")
    consumption_sdg_spl_ready = metric_value(consumption_sdg, "alb2002_consumption_sdg_spl_ready_rows")
    consumption_sdg_ppp_cpi_ready = metric_value(consumption_sdg, "alb2002_consumption_sdg_ppp_cpi_ready_rows")
    consumption_sdg_discretionary_ready = metric_value(consumption_sdg, "alb2002_consumption_sdg_discretionary_budget_ready_rows")
    consumption_sdg_che_ready = metric_value(consumption_sdg, "alb2002_consumption_sdg_che_denominator_ready_rows")
    consumption_sdg_recipe_ready = metric_value(consumption_sdg, "alb2002_consumption_sdg_recipe_ready_rows")
    consumption_sdg_outcome_ready = metric_value(consumption_sdg, "alb2002_consumption_sdg_outcome_ready_rows")
    consumption_sdg_sdg_ready = metric_value(consumption_sdg, "alb2002_consumption_sdg_sdg382_ready_rows")
    consumption_sdg_climate_ready = metric_value(consumption_sdg, "alb2002_consumption_sdg_climate_linkage_ready_rows")
    consumption_sdg_decision = metric_value(consumption_sdg, "alb2002_consumption_sdg_current_decision", "missing")
    consumption_aggregate_rows = metric_value(consumption_aggregate, "alb2002_consumption_aggregate_crosswalk_rows")
    consumption_aggregate_metadata_rows = metric_value(consumption_aggregate, "alb2002_consumption_aggregate_crosswalk_metadata_catalog_rows")
    consumption_aggregate_raw_totcons_positive = metric_value(consumption_aggregate, "alb2002_consumption_aggregate_crosswalk_raw_totcons_positive_rows")
    consumption_aggregate_candidate_match = metric_value(consumption_aggregate, "alb2002_consumption_aggregate_crosswalk_candidate_totcons_match_rows")
    consumption_aggregate_documentation_ready = metric_value(consumption_aggregate, "alb2002_consumption_aggregate_crosswalk_official_documentation_ready_rows")
    consumption_aggregate_recipe_ready = metric_value(consumption_aggregate, "alb2002_consumption_aggregate_crosswalk_recipe_ready_rows")
    consumption_aggregate_outcome_ready = metric_value(consumption_aggregate, "alb2002_consumption_aggregate_crosswalk_outcome_ready_rows")
    consumption_aggregate_sdg_ready = metric_value(consumption_aggregate, "alb2002_consumption_aggregate_crosswalk_sdg382_ready_rows")
    consumption_aggregate_climate_ready = metric_value(consumption_aggregate, "alb2002_consumption_aggregate_crosswalk_climate_linkage_ready_rows")
    consumption_aggregate_decision = metric_value(consumption_aggregate, "alb2002_consumption_aggregate_crosswalk_current_decision", "missing")

    district_groups = metric_value(crosswalk, "alb2002_district_crosswalk_district_rows")
    crosswalk_climate_ready = metric_value(crosswalk, "alb2002_climate_linkage_ready_rows")
    manual_blocked_gates = metric_value(boundary_manual, "alb2002_boundary_manual_verification_blocked_gates")
    manual_climate_ready = metric_value(boundary_manual, "alb2002_boundary_manual_verification_climate_linkage_ready_rows")
    followup_conclusive_blockers = metric_value(boundary_followup, "alb2002_boundary_manual_source_followup_conclusive_blocker_rows")
    followup_district_ready = metric_value(boundary_followup, "alb2002_boundary_manual_source_followup_district_level_ready_rows")
    followup_climate_ready = metric_value(boundary_followup, "alb2002_boundary_manual_source_followup_climate_linkage_ready_rows")
    gadm_complete_name_coverage = metric_value(gadm, "alb2002_gadm36_complete_name_coverage_rows")
    gadm_duplicate_keys = metric_value(gadm, "alb2002_gadm36_duplicate_boundary_key_count")
    gadm_historical_ready = metric_value(gadm, "alb2002_gadm_boundary_lead_historical_2002_ready_rows")
    gadm_climate_ready = metric_value(gadm, "alb2002_gadm_boundary_lead_climate_linkage_ready_rows")
    shock_rows = metric_value(climate_shock, "alb2002_climate_shock_candidate_exposure_rows")
    shock_reference_groups = metric_value(climate_shock, "alb2002_climate_shock_candidate_reference_group_rows")
    shock_precip_z = metric_value(climate_shock, "alb2002_climate_shock_candidate_precip_z_nonmissing_rows")
    shock_temp_z = metric_value(climate_shock, "alb2002_climate_shock_candidate_temp_z_nonmissing_rows")
    shock_combined = metric_value(climate_shock, "alb2002_climate_shock_candidate_combined_stress_rows")
    shock_climate_ready = metric_value(climate_shock, "alb2002_climate_shock_candidate_climate_linkage_ready_rows")
    shock_data_write = metric_value(climate_shock, "alb2002_climate_shock_candidate_data_write_ready_rows")
    linked_rows = metric_value(climate_outcome_linked, "alb2002_climate_outcome_linked_candidate_rows")
    linked_households = metric_value(climate_outcome_linked, "alb2002_climate_outcome_linked_candidate_household_rows")
    linked_windows = metric_value(climate_outcome_linked, "alb2002_climate_outcome_linked_candidate_window_rows")
    linked_precip_z = metric_value(climate_outcome_linked, "alb2002_climate_outcome_linked_candidate_precip_z_rows")
    linked_temp_z = metric_value(climate_outcome_linked, "alb2002_climate_outcome_linked_candidate_temp_z_rows")
    linked_combined = metric_value(climate_outcome_linked, "alb2002_climate_outcome_linked_candidate_combined_stress_rows")
    linked_climate_ready = metric_value(climate_outcome_linked, "alb2002_climate_outcome_linked_candidate_climate_linkage_ready_rows")
    linked_data_write = metric_value(climate_outcome_linked, "alb2002_climate_outcome_linked_candidate_data_write_ready_rows")

    actions = [
        action_row(
            1,
            "official_geography_artifacts",
            "climate_geography",
            f"district groups={district_groups}; district code rows={district_code_rows}; manual blocked gates={manual_blocked_gates}; follow-up conclusive blockers={followup_conclusive_blockers}",
            "blocked_no_verified_2002_boundary_or_gps_artifact",
            "Obtain or verify official ALB_2002 geography/GPS/EA-map files, district/commune codebooks, or a 2001/2002 district boundary source with usable join keys.",
            "Machine-readable evidence proves boundary vintage, level, codes/names, license, and join coverage for the ALB_2002 household district field.",
        ),
        action_row(
            2,
            "historical_boundary_crosswalk",
            "climate_geography",
            f"GADM complete name coverage={gadm_complete_name_coverage}; GADM duplicate keys={gadm_duplicate_keys}; GADM historical-ready={gadm_historical_ready}; district-level source-ready={followup_district_ready}",
            "blocked_name_coverage_without_historical_provenance",
            "Resolve duplicate/ambiguous boundary keys and verify the source as a 2001/2002 district layer or document a lossless historical crosswalk.",
            "Every observed district code/name maps to exactly one accepted boundary feature, with provenance and boundary-year evidence.",
        ),
        action_row(
            3,
            "oop_aggregation",
            "financial_protection_outcome",
            f"positive unreviewed OOP rows: 4w={oop_4w_positive}, 12m={oop_12m_positive}; questionnaire OOP rows={questionnaire_oop_rows}; four-week rows={questionnaire_four_week_rows}; twelve-month rows={questionnaire_twelve_month_rows}; policy stress rows={oop_policy_rows}; period-aligned policies={period_aligned_che_policy_rows}; period-ready rows={period_aligned_che_period_ready}; monthly-equivalent combined CHE10/CHE25={period_aligned_che_combined_che10}/{period_aligned_che_combined_che25}; core matches: 4w={oop_policy_core_4w_match}, 12m={oop_policy_core_12m_match}; skipped-payment rows={skip_payment_nonmissing_rows}; zero skipped cells={skip_payment_zero_cells}; positive skipped rows/cells={skip_payment_positive_rows}/{skip_payment_positive_cells}; zero-only skip blocks={skip_payment_zero_only_blocks}; skip-value decision rows={oop_skip_value_rows}; zero-skip ready rows={oop_skip_value_zero_ready}; skip-value decision={oop_skip_value_decision}",
            "blocked_mixed_recall_gift_scope_period_alignment_and_aggregation_review",
            "Use the no-positive-leakage skipped-payment decision and monthly-equivalent CHE stress tests, then choose and document OOP recall period, item scope, gift/payment inclusion, annualization policy, and person-to-household aggregation.",
            "A single OOP recipe has raw-variable lineage, questionnaire support, skip-path evidence, unit/recall decisions, period-aligned event-rate checks, and promotion review.",
        ),
        action_row(
            4,
            "consumption_sdg_denominator",
            "financial_protection_denominator",
            f"total consumption rows={total_consumption_rows}; positive total consumption rows={consumption_sdg_positive_total_rows}; aggregate crosswalk rows={consumption_aggregate_rows}; raw totcons positive={consumption_aggregate_raw_totcons_positive}; candidate totcons matches={consumption_aggregate_candidate_match}; metadata catalog rows={consumption_aggregate_metadata_rows}; official aggregate-documentation-ready={consumption_aggregate_documentation_ready}; denominator policy rows={consumption_sdg_policy_rows}; CHE denominator-ready={consumption_sdg_che_ready}; SPL-ready={consumption_sdg_spl_ready}; PPP/CPI-ready={consumption_sdg_ppp_cpi_ready}; discretionary-budget-ready={consumption_sdg_discretionary_ready}; SDG 3.8.2-ready semantics rows={sdg_ready}; aggregate decision={consumption_aggregate_decision}; denominator decision={consumption_sdg_decision}",
            "blocked_sdg_discretionary_budget_inputs_not_ready",
            "Use the documented total-budget denominator, then add SPL, PPP/CPI, and discretionary-budget handling before SDG 3.8.2 construction.",
            "Denominator audit accepts the documented consumption variable, OOP numerator alignment, and all SDG 3.8.2 discretionary-budget inputs.",
        ),
        action_row(
            5,
            "access_need_denominator",
            "access_outcome",
            f"raw access candidates={access_candidate_rows}; questionnaire access rows={questionnaire_access_rows}; conditional reason rows={conditional_reason_rows}; denominator policy rows={access_need_policy_rows}; q01 need rows={access_need_q01_need_rows}; person need rows={access_need_person_need_rows}; delayed={access_need_delayed_rows}; referral nonuse={access_need_referral_rows}; refused={access_need_refused_rows}; policy composite any barrier={access_need_composite_any_rows}; access candidate households={access_candidate_household_rows}; access candidate any barrier={access_candidate_any_rows}; access candidate cost barrier={access_candidate_cost_rows}; low-event policies={access_need_low_event_rows}; candidate low-event rows={access_candidate_low_event_rows}; access outcome-ready={access_need_outcome_ready}; access candidate outcome-ready={access_candidate_outcome_ready}",
            "blocked_need_access_denominator_and_barrier_scope",
            "Verify illness/need denominator, care-seeking/referral denominator, reason-not-sought coding, and cost/distance/supply barrier value labels.",
            "Access outcome formulas have eligible-denominator rules, raw value labels, skip-path evidence, and missing-code handling.",
        ),
        action_row(
            6,
            "keys_weights_merge",
            "household_merge_and_survey_design",
            f"candidate rows={candidate_rows}; household weight rows={weight_rows}; sample-design documentation-ready rows={sample_design_doc_ready}; sample-design raw concordance rows={sample_design_raw_concordance}; survey month rows={survey_month_rows}; interview date rows={interview_date_rows}; core recipe-ready rows={core_recipe_ready}",
            "blocked_recipe_promotion_review_not_complete",
            "Promote household frame, key uniqueness, survey weight, timing, denominator, OOP, and access/need decisions only after all required gates pass.",
            "A reviewed recipe permits writing a harmonized household dataset only after outcome and climate gates remain clearly separated.",
        ),
    ]

    gates = [
        gate_row(
            "household_frame",
            "Household frame and merge keys are accepted",
            "harmonized_household_dataset",
            "candidate_not_ready",
            f"temp candidate rows={candidate_rows}; core decision={core_decision}; recipe-ready rows={core_recipe_ready}",
            "Complete household frame, key uniqueness/cardinality, module coverage, and raw lineage are verified.",
            "Allows a non-climate household candidate to be considered if value/outcome gates also pass.",
            "Do not write `data/harmonized_household.csv` while recipe-ready rows remain zero.",
        ),
        gate_row(
            "survey_weight",
            "Household survey weight is verified",
            "weighted_descriptive_and_modeling",
            "candidate_not_ready",
            f"household weight rows={weight_rows}; candidate rows={candidate_rows}; weight-design audit rows={weight_design_audit_rows}; raw positive weights={weight_design_positive_rows}; key-match rows={weight_design_key_match_rows}; distinct PSU={weight_design_distinct_psu}; distinct strata={weight_design_distinct_stratum}; official source flags={weight_design_source_flags}; sample-design documentation-ready rows={sample_design_doc_ready}; sample-design raw concordance rows={sample_design_raw_concordance}; weighted-inference ready rows={weight_design_inference_ready}; sample-design weighted-inference ready rows={sample_design_weighted_inference_ready}; decision={weight_design_decision}; sample-design decision={sample_design_decision}",
            "Official household weight target population, normalization, and survey-design variance use are verified and preserved in lineage.",
            "Permits weighted descriptive diagnostics after outcomes exist.",
            "Do not report weighted prevalence until final outcomes and weight semantics pass together.",
        ),
        gate_row(
            "interview_timing",
            "Interview timing is verified for exposure windows",
            "climate_linkage",
            "candidate_not_ready",
            f"survey month rows={survey_month_rows}; interview date rows={interview_date_rows}",
            "Interview month/date values are accepted for the analysis rows, with exposure-window implications documented.",
            "Allows exposure-window construction only after geography also passes.",
            "Do not construct lagged climate exposures while the geography gate is blocked.",
        ),
        gate_row(
            "consumption_denominator",
            "Total consumption and SDG denominator are accepted",
            "CHE10_CHE25_and_SDG_denominator",
            "blocked",
            f"total consumption rows={total_consumption_rows}; positive total consumption rows={consumption_sdg_positive_total_rows}; raw totcons positive rows={consumption_aggregate_raw_totcons_positive}; candidate totcons match rows={consumption_aggregate_candidate_match}; metadata catalog rows={consumption_aggregate_metadata_rows}; official aggregate-documentation-ready rows={consumption_aggregate_documentation_ready}; denominator policy rows={consumption_sdg_policy_rows}; CHE denominator-ready rows={consumption_sdg_che_ready}; discretionary-budget-ready rows={consumption_sdg_discretionary_ready}; SDG 3.8.2-ready rows={max(int_value(consumption_sdg_sdg_ready), int_value(consumption_aggregate_sdg_ready))}",
            "Documented total-budget denominator is accepted with OOP alignment, missing rules, SPL/PPP/CPI, and SDG discretionary-budget inputs.",
            "Permits CHE10/CHE25 denominator construction and, after poverty-line/PPP/CPI work, SDG 3.8.2 construction.",
            "Do not construct official financial-protection outcomes until denominator semantics pass.",
        ),
        gate_row(
            "oop_aggregation",
            "OOP health expenditure aggregation is accepted",
            "CHE10_CHE25_and_OOP_outcomes",
            "blocked",
            f"raw OOP candidates={oop_candidate_rows}; questionnaire OOP rows={questionnaire_oop_rows}; NEW LEKS rows={questionnaire_new_lek_rows}; gift rows={questionnaire_gift_rows}; policy stress rows={oop_policy_rows}; max CHE10={oop_policy_max_che10}; max CHE25={oop_policy_max_che25}; period-aligned policies={period_aligned_che_policy_rows}; denominator rows={period_aligned_che_denominator_rows}; documented denominator rows={period_aligned_che_denominator_documented}; period-ready rows={period_aligned_che_period_ready}; monthly-equivalent combined CHE10/CHE25={period_aligned_che_combined_che10}/{period_aligned_che_combined_che25}; positive skipped-payment rows/cells={skip_payment_positive_rows}/{skip_payment_positive_cells}; zero-only skipped cells={skip_payment_zero_cells}; skip audit rows={skip_missing_rows}; policy outcome-ready={oop_policy_outcome_ready}; period-aligned outcome-ready={period_aligned_che_outcome_ready}; skip outcome-ready={skip_outcome_ready}",
            "OOP item scope, recall period, period alignment, annualization, gift/payment inclusion, residual missing rules, and household aggregation are verified.",
            "Permits financial-hardship outcome construction after denominator gate passes.",
            "Do not treat unreviewed mixed-recall OOP sums as final outcomes.",
        ),
        gate_row(
            "health_need_access",
            "Need/care/access denominator is accepted",
            "forgone_care_and_double_failure_outcomes",
            "blocked",
            f"raw access candidates={access_candidate_rows}; questionnaire access rows={questionnaire_access_rows}; denominator policy rows={access_need_policy_rows}; q01 need rows={access_need_q01_need_rows}; person need rows={access_need_person_need_rows}; delayed={access_need_delayed_rows}; referral nonuse={access_need_referral_rows}; refused={access_need_refused_rows}; policy composite any barrier={access_need_composite_any_rows}; access candidate households={access_candidate_household_rows}; access candidate any barrier={access_candidate_any_rows}; access candidate cost barrier={access_candidate_cost_rows}; outcome-ready rows={access_need_outcome_ready}; access candidate outcome-ready rows={access_candidate_outcome_ready}",
            "Illness/need, care-seeking, and barrier value labels and skip paths are verified.",
            "Permits access outcomes and UHC double-failure construction.",
            "Do not construct access or double-failure outcomes from unresolved skip-path variables.",
        ),
        gate_row(
            "climate_geography",
            "Climate geography is verified",
            "climate_linkage",
            "blocked",
            f"district groups={district_groups}; crosswalk climate-ready={crosswalk_climate_ready}; GADM climate-ready={gadm_climate_ready}; manual climate-ready={manual_climate_ready}; follow-up climate-ready={followup_climate_ready}",
            "GPS/cluster coordinates or a verified 2001/2002 district boundary/crosswalk are available for the household geography.",
            "Allows admin or point climate extraction with documented measurement error after timing gate passes.",
            "Do not call ALB_2002 climate-linked while only current or unprovenance boundary leads exist.",
        ),
        gate_row(
            "outcome_promotion",
            "Main outcomes may be constructed",
            "household_outcomes",
            "blocked",
            f"provisional outcome-ready rows={provisional_outcome_ready}; raw semantics outcome-ready rows={outcome_ready}; questionnaire outcome-ready rows={questionnaire_outcome_ready}; consumption denominator outcome-ready rows={consumption_sdg_outcome_ready}; period-aligned CHE outcome-ready rows={period_aligned_che_outcome_ready}; access outcome-ready rows={access_need_outcome_ready}; access candidate outcome-ready rows={access_candidate_outcome_ready}; composite candidate rows={uhc_composite_rows}; CHE10-or-access rows={uhc_composite_che10_or_access}; CHE25-or-access rows={uhc_composite_che25_or_access}; composite outcome-ready rows={uhc_composite_outcome_ready}; SDG 3.8.2-ready rows={max(int_value(sdg_ready), int_value(period_aligned_che_sdg_ready))}",
            "Key, weight, consumption, OOP, and access/need gates pass, with event-rate and missingness audits.",
            "Allows writing `data/household_outcomes.csv` for accepted outcome families.",
            "Do not write final outcome data while any required outcome component gate is blocked.",
        ),
        gate_row(
            "harmonized_dataset_promotion",
            "ALB_2002 may be promoted to a harmonized household dataset",
            "data/harmonized_household.csv",
            "blocked",
            f"core recipe-ready rows={core_recipe_ready}; questionnaire recipe-ready rows={questionnaire_recipe_ready}; OOP policy recipe-ready rows={oop_policy_recipe_ready}; period-aligned CHE recipe-ready rows={period_aligned_che_recipe_ready}; consumption denominator recipe-ready rows={consumption_sdg_recipe_ready}; aggregate crosswalk recipe-ready rows={consumption_aggregate_recipe_ready}; access recipe-ready rows={access_need_recipe_ready}; access candidate recipe-ready rows={access_candidate_recipe_ready}; composite recipe-ready rows={uhc_composite_recipe_ready}; outcome-ready rows={outcome_ready}",
            "Required household frame, key, weight, denominator, OOP, and minimum outcome variables all pass value/key/unit review.",
            "Allows a single-country harmonized household dataset to be written, still without climate linkage if geography remains blocked.",
            "Keep ALB_2002 in temp-only candidate state until all required minimum recipe gates pass.",
        ),
        gate_row(
            "climate_dataset_promotion",
            "ALB_2002 may be promoted to climate-linked analysis data",
            "data/climate_linked_household.csv",
            "blocked",
            f"questionnaire climate-ready={questionnaire_climate_ready}; consumption denominator climate-ready={consumption_sdg_climate_ready}; period-aligned CHE climate-ready={period_aligned_che_climate_ready}; access candidate climate-ready={access_candidate_climate_ready}; composite climate-ready={uhc_composite_climate_ready}; aggregate crosswalk climate-ready={consumption_aggregate_climate_ready}; crosswalk climate-ready={crosswalk_climate_ready}; GADM climate-ready={gadm_climate_ready}; shock diagnostic rows={shock_rows}; shock reference groups={shock_reference_groups}; shock combined-stress rows={shock_combined}; linked household-window rows={linked_rows}; linked households={linked_households}; linked windows={linked_windows}; linked combined-stress rows={linked_combined}; shock climate-ready={shock_climate_ready}; linked climate-ready={linked_climate_ready}; shock data-write-ready={shock_data_write}; linked data-write-ready={linked_data_write}; outcome-ready rows={outcome_ready}",
            "Harmonized dataset, accepted outcomes, verified timing, and verified climate geography all pass.",
            "Allows climate exposure extraction and merge for ALB_2002.",
            "Do not create climate-linked data until timing, geography, outcomes, and harmonization are all accepted.",
        ),
    ]

    summary = [
        summary_row("alb2002_minimum_recipe_promotion_action_rows", len(actions), "Action rows needed before ALB_2002 can become a minimum harmonized household dataset."),
        summary_row("alb2002_minimum_recipe_promotion_gate_rows", len(gates), "Pass/fail promotion gates for ALB_2002 harmonization, outcome, and climate linkage."),
        summary_row("alb2002_minimum_recipe_promotion_blocked_gates", sum(1 for row in gates if row["current_status"] == "blocked"), "Promotion gates still blocked."),
        summary_row("alb2002_minimum_recipe_promotion_candidate_gates", sum(1 for row in gates if row["current_status"] == "candidate_not_ready"), "Gates with candidate evidence that still needs acceptance review."),
        summary_row("alb2002_minimum_recipe_promotion_weight_design_audit_rows", int_value(weight_design_audit_rows), "ALB_2002 weight/design evidence audit rows observed upstream."),
        summary_row("alb2002_minimum_recipe_promotion_weight_design_source_flag_rows", int_value(weight_design_source_flags), "Official source-context flags detected by the ALB_2002 weight/design audit."),
        summary_row("alb2002_minimum_recipe_promotion_weight_design_positive_weight_rows", int_value(weight_design_positive_rows), "ALB_2002 positive household-weight rows observed in the readable weight file."),
        summary_row("alb2002_minimum_recipe_promotion_weight_design_key_match_rows", int_value(weight_design_key_match_rows), "ALB_2002 readable weight-file keys matching the temp household core."),
        summary_row("alb2002_minimum_recipe_promotion_weight_design_distinct_psu_rows", int_value(weight_design_distinct_psu), "ALB_2002 distinct PSU values observed in the readable weight file."),
        summary_row("alb2002_minimum_recipe_promotion_weight_design_distinct_stratum_rows", int_value(weight_design_distinct_stratum), "ALB_2002 distinct strata observed in the readable weight file."),
        summary_row("alb2002_minimum_recipe_promotion_weight_design_weighted_inference_ready_rows", int_value(weight_design_inference_ready), "ALB_2002 rows ready for promoted weighted inference; intentionally zero."),
        summary_row("alb2002_minimum_recipe_promotion_weight_design_harmonized_ready_rows", int_value(weight_design_harmonized_ready), "ALB_2002 rows ready for harmonized promotion after weight/design audit; intentionally zero."),
        summary_row("alb2002_minimum_recipe_promotion_weight_design_decision", weight_design_decision, "Current ALB_2002 weight/design fail-closed decision observed by the minimum recipe packet."),
        summary_row("alb2002_minimum_recipe_promotion_sample_design_pdf_pages", int_value(sample_design_pdf_pages), "Pages extracted from the ALB_2002 Basic Information PDF sample-design source."),
        summary_row("alb2002_minimum_recipe_promotion_sample_design_official_design_rows", int_value(sample_design_official_design), "Official 450 PSU by 8 household sample-design evidence observed upstream."),
        summary_row("alb2002_minimum_recipe_promotion_sample_design_official_final_rows", int_value(sample_design_official_final), "Official 3,599 final household sample-size evidence observed upstream."),
        summary_row("alb2002_minimum_recipe_promotion_sample_design_raw_concordance_rows", int_value(sample_design_raw_concordance), "Raw weight and candidate counts concordant with the official sample-design evidence."),
        summary_row("alb2002_minimum_recipe_promotion_sample_design_documentation_ready_rows", int_value(sample_design_doc_ready), "ALB_2002 sample-design documentation evidence ready; not a data-promotion gate pass."),
        summary_row("alb2002_minimum_recipe_promotion_sample_design_weighted_inference_ready_rows", int_value(sample_design_weighted_inference_ready), "ALB_2002 rows ready for promoted weighted inference after sample-design audit; intentionally zero."),
        summary_row("alb2002_minimum_recipe_promotion_sample_design_decision", sample_design_decision, "Current ALB_2002 sample-design documentation decision observed by the minimum recipe packet."),
        summary_row("alb2002_minimum_recipe_promotion_oop_policy_rows", int_value(oop_policy_rows), "ALB_2002 OOP aggregation policy stress-test rows observed upstream."),
        summary_row("alb2002_minimum_recipe_promotion_oop_policy_outcome_ready_rows", int_value(oop_policy_outcome_ready), "ALB_2002 OOP policy rows ready for outcome promotion; intentionally zero."),
        summary_row("alb2002_minimum_recipe_promotion_oop_policy_sdg382_ready_rows", int_value(oop_policy_sdg_ready), "ALB_2002 OOP policy rows ready for SDG 3.8.2 promotion; intentionally zero."),
        summary_row("alb2002_minimum_recipe_promotion_period_aligned_che_policy_rows", int_value(period_aligned_che_policy_rows), "ALB_2002 period-aligned CHE stress-test policy rows observed upstream."),
        summary_row("alb2002_minimum_recipe_promotion_period_aligned_che_denominator_rows", int_value(period_aligned_che_denominator_rows), "ALB_2002 rows with a positive monthly total-budget denominator in the period-aligned CHE audit."),
        summary_row("alb2002_minimum_recipe_promotion_period_aligned_che_period_ready_rows", int_value(period_aligned_che_period_ready), "ALB_2002 period-aligned CHE policies with denominator, zero-skip, and period-alignment checks passing for stress testing."),
        summary_row("alb2002_minimum_recipe_promotion_period_aligned_che_combined_che10_rate", period_aligned_che_combined_che10, "Combined monthly-equivalent CHE10 stress-test rate; not a final outcome."),
        summary_row("alb2002_minimum_recipe_promotion_period_aligned_che_combined_che25_rate", period_aligned_che_combined_che25, "Combined monthly-equivalent CHE25 stress-test rate; not a final outcome."),
        summary_row("alb2002_minimum_recipe_promotion_period_aligned_che_outcome_ready_rows", int_value(period_aligned_che_outcome_ready), "ALB_2002 period-aligned CHE rows ready for outcome promotion; intentionally zero."),
        summary_row("alb2002_minimum_recipe_promotion_period_aligned_che_recipe_ready_rows", int_value(period_aligned_che_recipe_ready), "ALB_2002 period-aligned CHE rows ready for recipe promotion; intentionally zero."),
        summary_row("alb2002_minimum_recipe_promotion_period_aligned_che_sdg382_ready_rows", int_value(period_aligned_che_sdg_ready), "ALB_2002 period-aligned CHE rows ready for SDG 3.8.2 promotion; intentionally zero."),
        summary_row("alb2002_minimum_recipe_promotion_period_aligned_che_climate_ready_rows", int_value(period_aligned_che_climate_ready), "ALB_2002 period-aligned CHE rows ready for climate linkage; intentionally zero."),
        summary_row("alb2002_minimum_recipe_promotion_period_aligned_che_decision", period_aligned_che_decision, "Current ALB_2002 period-aligned CHE fail-closed decision observed by the minimum recipe packet."),
        summary_row("alb2002_minimum_recipe_promotion_skip_missing_rows", int_value(skip_missing_rows), "ALB_2002 skip/missing semantics audit rows observed upstream."),
        summary_row("alb2002_minimum_recipe_promotion_skip_positive_rows", int_value(skip_payment_positive_rows), "ALB_2002 positive skipped-payment rows observed upstream; should remain zero."),
        summary_row("alb2002_minimum_recipe_promotion_skip_zero_cells", int_value(skip_payment_zero_cells), "ALB_2002 zero-only skipped-payment cells observed upstream."),
        summary_row("alb2002_minimum_recipe_promotion_skip_outcome_ready_rows", int_value(skip_outcome_ready), "ALB_2002 skip/missing rows ready for outcome promotion; intentionally zero."),
        summary_row("alb2002_minimum_recipe_promotion_oop_skip_value_decision_rows", int_value(oop_skip_value_rows), "ALB_2002 OOP skip-value decision audit rows observed upstream."),
        summary_row("alb2002_minimum_recipe_promotion_oop_skip_value_zero_ready_rows", int_value(oop_skip_value_zero_ready), "ALB_2002 skip-value rows supporting the no-positive-leakage skipped-payment decision."),
        summary_row("alb2002_minimum_recipe_promotion_oop_skip_value_positive_rows", int_value(oop_skip_value_positive_rows), "ALB_2002 positive skipped-payment rows after the skip-value decision; should remain zero."),
        summary_row("alb2002_minimum_recipe_promotion_oop_skip_value_positive_cells", int_value(oop_skip_value_positive_cells), "ALB_2002 positive skipped-payment cells after the skip-value decision; should remain zero."),
        summary_row("alb2002_minimum_recipe_promotion_oop_skip_value_recall_ready_rows", int_value(oop_skip_value_recall_ready), "ALB_2002 OOP recall-scope rows accepted by the skip-value audit; intentionally zero."),
        summary_row("alb2002_minimum_recipe_promotion_oop_skip_value_inclusion_ready_rows", int_value(oop_skip_value_inclusion_ready), "ALB_2002 OOP inclusion-scope rows accepted by the skip-value audit; intentionally zero."),
        summary_row("alb2002_minimum_recipe_promotion_oop_skip_value_decision", oop_skip_value_decision, "Current ALB_2002 OOP skip-value decision observed by the minimum recipe packet."),
        summary_row("alb2002_minimum_recipe_promotion_access_need_policy_rows", int_value(access_need_policy_rows), "ALB_2002 access/need denominator policy rows observed upstream."),
        summary_row("alb2002_minimum_recipe_promotion_access_need_q01_need_rows", int_value(access_need_q01_need_rows), "ALB_2002 q01 need-denominator rows observed upstream."),
        summary_row("alb2002_minimum_recipe_promotion_access_need_any_barrier_rows", int_value(access_need_composite_any_rows), "ALB_2002 composite any-access-barrier candidate rows observed upstream."),
        summary_row("alb2002_minimum_recipe_promotion_access_need_outcome_ready_rows", int_value(access_need_outcome_ready), "ALB_2002 access/need rows ready for outcome promotion; intentionally zero."),
        summary_row("alb2002_minimum_recipe_promotion_access_candidate_household_rows", int_value(access_candidate_household_rows), "ALB_2002 temp-only household access candidate rows observed upstream."),
        summary_row("alb2002_minimum_recipe_promotion_access_candidate_any_barrier_rows", int_value(access_candidate_any_rows), "ALB_2002 temp-only composite any-access-barrier candidate rows observed upstream."),
        summary_row("alb2002_minimum_recipe_promotion_access_candidate_cost_barrier_rows", int_value(access_candidate_cost_rows), "ALB_2002 temp-only composite cost-barrier candidate rows observed upstream."),
        summary_row("alb2002_minimum_recipe_promotion_access_candidate_outcome_ready_rows", int_value(access_candidate_outcome_ready), "ALB_2002 household access candidate rows ready for final outcome promotion; intentionally zero."),
        summary_row("alb2002_minimum_recipe_promotion_uhc_composite_rows", int_value(uhc_composite_rows), "ALB_2002 temp-only composite UHC candidate rows observed upstream."),
        summary_row("alb2002_minimum_recipe_promotion_uhc_composite_che10_or_access_rows", int_value(uhc_composite_che10_or_access), "ALB_2002 temp-only CHE10-or-access candidate rows observed upstream."),
        summary_row("alb2002_minimum_recipe_promotion_uhc_composite_che25_or_access_rows", int_value(uhc_composite_che25_or_access), "ALB_2002 temp-only CHE25-or-access candidate rows observed upstream."),
        summary_row("alb2002_minimum_recipe_promotion_uhc_composite_both_che10_access_rows", int_value(uhc_composite_both_che10), "ALB_2002 temp-only both CHE10 and access-barrier candidate rows observed upstream."),
        summary_row("alb2002_minimum_recipe_promotion_uhc_composite_coping_rows", int_value(uhc_composite_coping), "ALB_2002 temp-only health-cost coping candidate rows observed upstream."),
        summary_row("alb2002_minimum_recipe_promotion_uhc_composite_outcome_ready_rows", int_value(uhc_composite_outcome_ready), "ALB_2002 composite UHC candidate rows ready for final outcome promotion; intentionally zero."),
        summary_row("alb2002_minimum_recipe_promotion_consumption_sdg_policy_rows", int_value(consumption_sdg_policy_rows), "ALB_2002 consumption/SDG denominator policy rows observed upstream."),
        summary_row("alb2002_minimum_recipe_promotion_consumption_sdg_positive_total_rows", int_value(consumption_sdg_positive_total_rows), "ALB_2002 positive total-consumption denominator rows observed upstream."),
        summary_row("alb2002_minimum_recipe_promotion_consumption_aggregate_crosswalk_rows", int_value(consumption_aggregate_rows), "ALB_2002 consumption aggregate metadata/local evidence crosswalk rows observed upstream."),
        summary_row("alb2002_minimum_recipe_promotion_consumption_aggregate_metadata_rows", int_value(consumption_aggregate_metadata_rows), "ALB_2002 local master metadata catalog rows for the aggregate audit."),
        summary_row("alb2002_minimum_recipe_promotion_consumption_aggregate_totcons_match_rows", int_value(consumption_aggregate_candidate_match), "ALB_2002 candidate total-consumption rows exactly matching raw `totcons`."),
        summary_row("alb2002_minimum_recipe_promotion_consumption_aggregate_documentation_ready_rows", int_value(consumption_aggregate_documentation_ready), "ALB_2002 rows with accepted public aggregate documentation."),
        summary_row("alb2002_minimum_recipe_promotion_consumption_aggregate_recipe_ready_rows", int_value(consumption_aggregate_recipe_ready), "ALB_2002 aggregate crosswalk rows ready for recipe promotion; intentionally zero."),
        summary_row("alb2002_minimum_recipe_promotion_consumption_aggregate_outcome_ready_rows", int_value(consumption_aggregate_outcome_ready), "ALB_2002 aggregate crosswalk rows ready for outcome promotion; intentionally zero."),
        summary_row("alb2002_minimum_recipe_promotion_consumption_aggregate_sdg382_ready_rows", int_value(consumption_aggregate_sdg_ready), "ALB_2002 aggregate crosswalk rows ready for SDG 3.8.2 promotion; intentionally zero."),
        summary_row("alb2002_minimum_recipe_promotion_consumption_sdg_spl_ready_rows", int_value(consumption_sdg_spl_ready), "ALB_2002 consumption/SDG rows with SPL inputs accepted; intentionally zero."),
        summary_row("alb2002_minimum_recipe_promotion_consumption_sdg_ppp_cpi_ready_rows", int_value(consumption_sdg_ppp_cpi_ready), "ALB_2002 consumption/SDG rows with PPP/CPI inputs accepted; intentionally zero."),
        summary_row("alb2002_minimum_recipe_promotion_consumption_sdg_discretionary_ready_rows", int_value(consumption_sdg_discretionary_ready), "ALB_2002 rows with household discretionary budget accepted; intentionally zero."),
        summary_row("alb2002_minimum_recipe_promotion_consumption_sdg_che_ready_rows", int_value(consumption_sdg_che_ready), "ALB_2002 rows with CHE denominator accepted; intentionally zero."),
        summary_row("alb2002_minimum_recipe_promotion_consumption_sdg_outcome_ready_rows", int_value(consumption_sdg_outcome_ready), "ALB_2002 consumption/SDG rows ready for outcome promotion; intentionally zero."),
        summary_row("alb2002_minimum_recipe_promotion_consumption_sdg_sdg382_ready_rows", int_value(consumption_sdg_sdg_ready), "ALB_2002 consumption/SDG rows ready for SDG 3.8.2 promotion; intentionally zero."),
        summary_row("alb2002_minimum_recipe_promotion_harmonized_ready_rows", 0, "Rows ready for harmonized dataset promotion after this packet; intentionally zero."),
        summary_row("alb2002_minimum_recipe_promotion_outcome_ready_rows", int_value(outcome_ready), "Existing ALB_2002 outcome-ready rows observed from raw semantics audits."),
        summary_row("alb2002_minimum_recipe_promotion_sdg382_ready_rows", int_value(sdg_ready), "Existing ALB_2002 SDG 3.8.2-ready rows observed from raw semantics audits."),
        summary_row("alb2002_minimum_recipe_promotion_climate_shock_rows", int_value(shock_rows), "ALB_2002 temp-only climate shock diagnostic rows observed upstream."),
        summary_row("alb2002_minimum_recipe_promotion_climate_shock_reference_groups", int_value(shock_reference_groups), "ALB_2002 survey-month/window diagnostic climate shock reference groups."),
        summary_row("alb2002_minimum_recipe_promotion_climate_shock_precip_z_rows", int_value(shock_precip_z), "ALB_2002 diagnostic rainfall z-score rows observed upstream."),
        summary_row("alb2002_minimum_recipe_promotion_climate_shock_temp_z_rows", int_value(shock_temp_z), "ALB_2002 diagnostic temperature z-score rows observed upstream."),
        summary_row("alb2002_minimum_recipe_promotion_climate_shock_combined_stress_rows", int_value(shock_combined), "ALB_2002 diagnostic combined climate-stress rows; not accepted treatment variables."),
        summary_row("alb2002_minimum_recipe_promotion_climate_shock_climate_ready_rows", int_value(shock_climate_ready), "ALB_2002 shock diagnostic rows ready for climate linkage; intentionally zero."),
        summary_row("alb2002_minimum_recipe_promotion_climate_shock_data_write_ready_rows", int_value(shock_data_write), "ALB_2002 shock diagnostic rows allowed for data/ write; intentionally zero."),
        summary_row("alb2002_minimum_recipe_promotion_climate_outcome_linked_rows", int_value(linked_rows), "ALB_2002 temp-only household-window climate/outcome linked candidate rows observed upstream."),
        summary_row("alb2002_minimum_recipe_promotion_climate_outcome_linked_households", int_value(linked_households), "ALB_2002 households represented in the linked diagnostic candidate."),
        summary_row("alb2002_minimum_recipe_promotion_climate_outcome_linked_windows", int_value(linked_windows), "Diagnostic exposure windows per household in the linked candidate."),
        summary_row("alb2002_minimum_recipe_promotion_climate_outcome_linked_precip_z_rows", int_value(linked_precip_z), "ALB_2002 linked diagnostic rainfall z-score rows."),
        summary_row("alb2002_minimum_recipe_promotion_climate_outcome_linked_temp_z_rows", int_value(linked_temp_z), "ALB_2002 linked diagnostic temperature z-score rows."),
        summary_row("alb2002_minimum_recipe_promotion_climate_outcome_linked_combined_stress_rows", int_value(linked_combined), "ALB_2002 linked diagnostic combined climate-stress rows; not accepted treatment variables."),
        summary_row("alb2002_minimum_recipe_promotion_climate_outcome_linked_climate_ready_rows", int_value(linked_climate_ready), "ALB_2002 linked rows ready for promoted climate linkage; intentionally zero."),
        summary_row("alb2002_minimum_recipe_promotion_climate_outcome_linked_data_write_ready_rows", int_value(linked_data_write), "ALB_2002 linked rows allowed for data/ write; intentionally zero."),
        summary_row("alb2002_minimum_recipe_promotion_climate_linkage_ready_rows", max(int_value(crosswalk_climate_ready), int_value(gadm_climate_ready), int_value(manual_climate_ready), int_value(followup_climate_ready)), "Existing ALB_2002 climate-linkage-ready rows observed from geography audits."),
        summary_row("alb2002_minimum_recipe_promotion_current_decision", DECISION, "Current fail-closed ALB_2002 minimum recipe promotion decision."),
    ]
    return actions, gates, summary


def markdown_rows(rows: list[dict[str, str]], columns: list[str]) -> str:
    lines = ["| " + " | ".join(columns) + " |", "|" + "|".join("---" for _ in columns) + "|"]
    for row in rows:
        values = []
        for column in columns:
            value = (row.get(column, "") or "").replace("|", "/")
            if len(value) > 115:
                value = value[:112] + "..."
            values.append(value)
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines)


def write_report(actions: list[dict[str, str]], gates: list[dict[str, str]], summary: list[dict[str, str]]) -> None:
    summary_table = "\n".join(f"| {row['metric']} | {row['value']} | {row['interpretation']} |" for row in summary)
    REPORT_PATH.write_text(
        f"""# ALB_2002 Minimum Recipe Promotion Packet

Status: fail-closed promotion packet. ALB_2002 is the current top-ranked Albania first-analysis lead, but this packet does not promote any dataset to `data/`. It records what must pass before the temp household-core candidate can become a harmonized household dataset, outcome dataset, or climate-linked dataset.

## Summary

| Metric | Value | Interpretation |
|---|---:|---|
{summary_table}

## Action Queue

{markdown_rows(actions, ['action_rank', 'gate_id', 'blocker_domain', 'blocking_status', 'required_resolution'])}

## Promotion Gates

{markdown_rows(gates, ['gate_id', 'required_for', 'current_status', 'current_evidence', 'minimum_evidence_to_pass'])}

## Interpretation

- ALB_2002 has the strongest local candidate evidence because household timing, district codes, weights, consumption, and OOP/access signals are visible in raw audits.
- The minimum harmonized dataset is still blocked by weight/design inference semantics, OOP aggregation policy, gift/payment scope, mixed recall periods, SDG denominator handling, access-denominator policy acceptance, and recipe promotion review. The skipped-payment positive-leakage check is documented separately as zero-only, and the period-aligned CHE audit supplies monthly-equivalent stress-test rates for downstream temp-only CHE candidate outcomes without promoting final outcomes.
- Climate linkage is separately blocked by the absence of a verified 2001/2002 district boundary, official GPS/EA-map artifact, or accepted historical crosswalk. GADM 3.6 is a useful lead with complete name coverage, but it has duplicate SHKODER rows and no verified 2002 provenance in this workspace. The household-window climate/outcome linked candidate is mechanical diagnostic evidence only and remains outside `data/`.
- This packet preserves the line between a promising temp candidate and promoted analytical data.

## Machine-Readable Outputs

- `temp/alb2002_minimum_recipe_promotion_action_queue.csv`
- `temp/alb2002_minimum_recipe_promotion_gate_checklist.csv`
- `result/alb2002_minimum_recipe_promotion_summary.csv`
""",
        encoding="utf-8",
    )


def main() -> None:
    ensure_dirs()
    actions, gates, summary = build_packet()
    write_csv(ACTION_QUEUE_PATH, actions, ACTION_COLUMNS)
    write_csv(GATE_CHECKLIST_PATH, gates, GATE_COLUMNS)
    write_csv(SUMMARY_PATH, summary, SUMMARY_COLUMNS)
    write_report(actions, gates, summary)
    append_log(TEMP_DIR / "audit_log.md", f"Built ALB_2002 minimum recipe promotion packet actions={len(actions)} gates={len(gates)} decision={DECISION}.")
    print(f"ALB_2002 minimum recipe promotion packet actions={len(actions)} gates={len(gates)} decision={DECISION}.")


if __name__ == "__main__":
    main()
