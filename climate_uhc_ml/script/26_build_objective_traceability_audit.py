from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path
from typing import Any, Callable

from common import DATA_DIR, REPORT_DIR, RESULT_DIR, SCRIPT_DIR, TEMP_DIR, append_log, ensure_dirs, write_csv


TRACE_PATH = RESULT_DIR / "objective_requirement_traceability.csv"
GUARDRAIL_PATH = RESULT_DIR / "objective_guardrail_audit.csv"
SUMMARY_PATH = RESULT_DIR / "objective_traceability_summary.csv"
REPORT_PATH = REPORT_DIR / "objective_traceability_audit.md"

TRACE_COLUMNS = [
    "requirement_id",
    "objective_section",
    "requirement",
    "status",
    "evidence",
    "evidence_artifacts",
    "gap",
]

GUARDRAIL_COLUMNS = [
    "guardrail_id",
    "guardrail",
    "status",
    "evidence",
    "evidence_artifacts",
    "gap",
]

SUMMARY_COLUMNS = ["metric", "value", "interpretation"]

RAW_EXTENSIONS = {".dta", ".sav", ".por", ".sas7bdat", ".xpt", ".zip", ".tar", ".gz", ".tgz", ".rar", ".7z"}
MESSY_REPORT_EXTENSIONS = {".csv", ".log", ".tmp", ".json"}
VARIABLE_MAP_FILES = [
    TEMP_DIR / "variable_map_consumption.csv",
    TEMP_DIR / "variable_map_health_expenditure.csv",
    TEMP_DIR / "variable_map_health_need_access.csv",
    TEMP_DIR / "variable_map_geography.csv",
    TEMP_DIR / "variable_map_survey_design.csv",
    TEMP_DIR / "variable_map_demographics.csv",
    TEMP_DIR / "variable_map_shocks.csv",
]


def read_csv_dicts(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def row_count(path: Path) -> int:
    return len(read_csv_dicts(path))


def safe_int(value: Any, default: int = 0) -> int:
    try:
        return int(float(str(value).strip()))
    except (TypeError, ValueError):
        return default


def file_ok(path: Path) -> bool:
    return path.exists() and path.is_file() and path.stat().st_size > 0


def text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def exists_any(paths: list[Path]) -> bool:
    return any(file_ok(path) for path in paths)


def has_limited_harmonized_core_marker(path: Path) -> bool:
    rows = read_csv_dicts(path)
    if not rows:
        return False
    return any(
        row.get("harmonized_scope") == "alb2002_household_core_limited_no_final_outcome_no_climate"
        and row.get("data_use_limit") == "harmonized_household_core_only_not_for_final_outcome_or_climate_analysis"
        and row.get("outcome_status") == "candidate_inputs_not_final_outcomes"
        for row in rows
    )


def has_limited_climate_exposure_marker(path: Path) -> bool:
    rows = read_csv_dicts(path)
    if not rows:
        return False
    return any(
        row.get("climate_exposure_scope") == "alb2002_admin2_centroid_nasa_power_fallback_no_historical_baseline"
        and row.get("data_use_limit") == "climate_exposure_admin2_centroid_only_not_for_final_climate_linkage"
        and row.get("final_analysis_ready") == "0"
        for row in rows
    )


def has_limited_household_outcome_marker(path: Path) -> bool:
    rows = read_csv_dicts(path)
    if not rows:
        return False
    return any(
        row.get("outcome_scope") == "alb2002_financial_protection_che10_che25_limited_no_sdg382_no_access"
        and row.get("data_use_limit") == "outcome_che10_che25_only_not_for_final_sdg382_access_or_climate_analysis"
        and row.get("final_analysis_ready") == "0"
        for row in rows
    )


def has_limited_climate_linked_marker(path: Path) -> bool:
    rows = read_csv_dicts(path)
    if not rows:
        return False
    return any(
        row.get("climate_linked_scope") == "alb2002_limited_che_admin2_centroid_nasa_power_window_linkage_not_final"
        and row.get("data_use_limit") == "climate_linked_che_diagnostic_only_not_for_promoted_descriptive_ml_causal_or_policy_analysis"
        and row.get("final_analysis_ready") == "0"
        for row in rows
    )


def count_glob_rows(pattern: str) -> int:
    return sum(row_count(path) for path in TEMP_DIR.glob(pattern))


def count_status(path: Path, field: str, value: str) -> int:
    return sum(1 for row in read_csv_dicts(path) if row.get(field) == value)


def count_status_prefix(path: Path, field: str, prefixes: tuple[str, ...]) -> int:
    return sum(1 for row in read_csv_dicts(path) if row.get(field, "").startswith(prefixes))


def artifact_list(paths: list[Path]) -> str:
    root = TEMP_DIR.parent
    out = []
    for path in paths:
        try:
            out.append(str(path.relative_to(root)).replace("\\", "/"))
        except ValueError:
            out.append(str(path))
    return ";".join(out)


def status_done(condition: bool) -> str:
    return "satisfied" if condition else "incomplete"


def blocked_if_raw(condition: bool) -> str:
    return "satisfied" if condition else "blocked_raw_microdata"


def current_counts() -> dict[str, int]:
    completion = read_csv_dicts(RESULT_DIR / "completion_criteria_audit.csv")
    workspace_validation = read_csv_dicts(RESULT_DIR / "workspace_validation_audit.csv")
    raw_manifest = read_csv_dicts(TEMP_DIR / "raw_download_file_manifest.csv")
    raw_targets = read_csv_dicts(TEMP_DIR / "raw_download_target_audit.csv")
    sample_gate = read_csv_dicts(RESULT_DIR / "sample_selection_gate_audit.csv")
    sample_gate_summary = read_csv_dicts(RESULT_DIR / "sample_selection_gate_summary.csv")
    modeling_plan = read_csv_dicts(TEMP_DIR / "modeling_identification_plan.csv")
    public_external_downloads = read_csv_dicts(TEMP_DIR / "public_external_raw_candidate_downloads.csv")
    first_batch_access_probe = read_csv_dicts(TEMP_DIR / "first_batch_official_raw_access_probe.csv")
    first_batch_public_docs = read_csv_dicts(TEMP_DIR / "first_batch_public_documentation_audit.csv")
    first_batch_file_source = read_csv_dicts(TEMP_DIR / "first_batch_file_source_traceability.csv")
    first_batch_merge_key_plan = read_csv_dicts(TEMP_DIR / "first_batch_merge_key_lineage_plan.csv")
    first_batch_merge_key_candidates = read_csv_dicts(TEMP_DIR / "first_batch_merge_key_candidate_variables.csv")
    first_batch_value_key_audit = read_csv_dicts(TEMP_DIR / "first_batch_raw_value_key_audit.csv")
    first_batch_raw_key_audit = read_csv_dicts(TEMP_DIR / "first_batch_raw_merge_key_audit.csv")
    first_batch_auto_value_audit = read_csv_dicts(TEMP_DIR / "first_batch_harmonization_value_audit_auto.csv")
    alb2002_core_summary = read_csv_dicts(RESULT_DIR / "alb2002_household_core_candidate_summary.csv")
    alb2002_outcome_summary = read_csv_dicts(RESULT_DIR / "alb2002_provisional_outcome_feasibility_summary.csv")
    alb2002_semantics_summary = read_csv_dicts(RESULT_DIR / "alb2002_outcome_semantics_raw_value_summary.csv")
    alb2002_health_questionnaire_summary = read_csv_dicts(RESULT_DIR / "alb2002_health_questionnaire_semantics_summary.csv")
    alb2002_oop_policy_summary = read_csv_dicts(RESULT_DIR / "alb2002_oop_aggregation_policy_summary.csv")
    alb2002_skip_missing_summary = read_csv_dicts(RESULT_DIR / "alb2002_skip_missing_semantics_summary.csv")
    alb2002_oop_skip_value_summary = read_csv_dicts(RESULT_DIR / "alb2002_oop_skip_value_decision_summary.csv")
    alb2002_access_need_summary = read_csv_dicts(RESULT_DIR / "alb2002_access_need_denominator_policy_summary.csv")
    alb2002_consumption_sdg_summary = read_csv_dicts(RESULT_DIR / "alb2002_consumption_sdg_denominator_policy_summary.csv")
    alb2002_consumption_construction_summary = read_csv_dicts(RESULT_DIR / "alb2002_consumption_construction_source_summary.csv")
    alb2002_consumption_aggregate_summary = read_csv_dicts(RESULT_DIR / "alb2002_consumption_aggregate_metadata_crosswalk_summary.csv")
    alb2002_period_aligned_che_summary = read_csv_dicts(RESULT_DIR / "alb2002_period_aligned_che_policy_summary.csv")
    alb2002_che_candidate_summary = read_csv_dicts(RESULT_DIR / "alb2002_che_candidate_outcome_summary.csv")
    alb2002_access_candidate_summary = read_csv_dicts(RESULT_DIR / "alb2002_access_candidate_outcome_summary.csv")
    alb2002_uhc_composite_summary = read_csv_dicts(RESULT_DIR / "alb2002_uhc_composite_candidate_summary.csv")
    alb2002_analysis_candidate_summary = read_csv_dicts(RESULT_DIR / "alb2002_analysis_candidate_readiness_summary.csv")
    alb2002_climate_centroid_summary = read_csv_dicts(RESULT_DIR / "alb2002_climate_centroid_exposure_summary.csv")
    alb2002_climate_shock_summary = read_csv_dicts(RESULT_DIR / "alb2002_climate_shock_candidate_summary.csv")
    alb2002_climate_outcome_linked_summary = read_csv_dicts(RESULT_DIR / "alb2002_climate_outcome_linked_candidate_summary.csv")
    alb2002_linked_candidate_descriptive_summary = read_csv_dicts(RESULT_DIR / "alb2002_linked_candidate_descriptive_summary.csv")
    alb2002_weight_design_summary = read_csv_dicts(RESULT_DIR / "alb2002_weight_design_evidence_summary.csv")
    alb2002_sample_design_summary = read_csv_dicts(RESULT_DIR / "alb2002_sample_design_documentation_summary.csv")
    alb2002_minimum_recipe_summary = read_csv_dicts(RESULT_DIR / "alb2002_minimum_recipe_promotion_summary.csv")
    analysis_promotion_summary = read_csv_dicts(RESULT_DIR / "analysis_dataset_promotion_barrier_summary.csv")
    alb2002_harmonized_core_summary = read_csv_dicts(RESULT_DIR / "alb2002_harmonized_household_core_promotion_summary.csv")
    alb2002_limited_financial_summary = read_csv_dicts(RESULT_DIR / "alb2002_limited_financial_outcome_promotion_summary.csv")
    alb2002_limited_climate_summary = read_csv_dicts(RESULT_DIR / "alb2002_limited_climate_exposure_promotion_summary.csv")
    alb2002_limited_linked_summary = read_csv_dicts(RESULT_DIR / "alb2002_limited_climate_linked_promotion_summary.csv")
    design_scorecard_current_summary = read_csv_dicts(RESULT_DIR / "design_scorecard_current_summary.csv")
    alb2002_promotion_gate_delta_summary = read_csv_dicts(RESULT_DIR / "alb2002_promotion_gate_delta_summary.csv")
    alb2002_boundary_blocker_summary = read_csv_dicts(RESULT_DIR / "alb2002_boundary_blocker_resolution_summary.csv")
    alb2002_outcome_blocker_summary = read_csv_dicts(RESULT_DIR / "alb2002_outcome_blocker_resolution_summary.csv")
    alb2012_blocker_summary = read_csv_dicts(RESULT_DIR / "alb2012_timing_geography_blocker_resolution_summary.csv")
    alb2002_crosswalk_summary = read_csv_dicts(RESULT_DIR / "alb2002_district_climate_crosswalk_summary.csv")
    alb2002_boundary_name_summary = read_csv_dicts(RESULT_DIR / "alb2002_boundary_name_match_summary.csv")
    alb2002_boundary_source_summary = read_csv_dicts(RESULT_DIR / "alb2002_boundary_source_alternative_summary.csv")
    alb2002_boundary_resource_summary = read_csv_dicts(RESULT_DIR / "alb2002_boundary_source_resource_search_summary.csv")
    alb2002_boundary_geometry_summary = read_csv_dicts(RESULT_DIR / "alb2002_boundary_geometry_provenance_summary.csv")
    alb2002_boundary_manual_summary = read_csv_dicts(RESULT_DIR / "alb2002_boundary_manual_verification_packet_summary.csv")
    alb2002_boundary_followup_summary = read_csv_dicts(RESULT_DIR / "alb2002_boundary_manual_source_followup_summary.csv")
    alb2002_gadm_summary = read_csv_dicts(RESULT_DIR / "alb2002_gadm_boundary_lead_summary.csv")
    alb2002_local_geo_summary = read_csv_dicts(RESULT_DIR / "alb2002_local_geography_artifact_summary.csv")
    alb2012_summary = read_csv_dicts(RESULT_DIR / "alb2012_raw_core_feasibility_summary.csv")
    alb2012_outcome_summary = read_csv_dicts(RESULT_DIR / "alb2012_provisional_outcome_feasibility_summary.csv")
    alb2012_semantics_summary = read_csv_dicts(RESULT_DIR / "alb2012_outcome_semantics_raw_value_summary.csv")
    alb2012_timing_geo_summary = read_csv_dicts(RESULT_DIR / "alb2012_timing_geography_exhaustive_summary.csv")
    alb2012_questionnaire_timing_summary = read_csv_dicts(RESULT_DIR / "alb2012_questionnaire_timing_field_summary.csv")
    albania_legacy_questionnaire_summary = read_csv_dicts(RESULT_DIR / "albania_legacy_questionnaire_readability_summary.csv")
    albania_legacy_questionnaire_timing_summary = read_csv_dicts(RESULT_DIR / "albania_legacy_questionnaire_timing_field_summary.csv")
    alb2005_summary = read_csv_dicts(RESULT_DIR / "alb2005_documented_harmonization_summary.csv")
    alb2005_core_summary = read_csv_dicts(RESULT_DIR / "alb2005_household_core_candidate_summary.csv")
    alb2005_outcome_summary = read_csv_dicts(RESULT_DIR / "alb2005_provisional_outcome_feasibility_summary.csv")
    alb2005_semantics_summary = read_csv_dicts(RESULT_DIR / "alb2005_outcome_semantics_raw_value_summary.csv")
    alb2005_timing_geo_summary = read_csv_dicts(RESULT_DIR / "alb2005_timing_geography_exhaustive_summary.csv")
    alb2005_timing_geo_source_summary = read_csv_dicts(RESULT_DIR / "alb2005_timing_geography_source_search_summary.csv")
    alb2005_value_decision_summary = read_csv_dicts(RESULT_DIR / "alb2005_harmonization_value_decision_summary.csv")
    alb2005_required_value_key_summary = read_csv_dicts(RESULT_DIR / "alb2005_required_value_key_summary.csv")
    alb2005_health_questionnaire_summary = read_csv_dicts(RESULT_DIR / "alb2005_health_questionnaire_semantics_summary.csv")
    alb2005_oop_policy_summary = read_csv_dicts(RESULT_DIR / "alb2005_oop_aggregation_policy_summary.csv")
    alb2005_skip_missing_summary = read_csv_dicts(RESULT_DIR / "alb2005_skip_missing_semantics_summary.csv")
    alb2005_unit_period_summary = read_csv_dicts(RESULT_DIR / "alb2005_consumption_oop_unit_period_summary.csv")
    alb2005_aggregate_crosswalk_summary = read_csv_dicts(RESULT_DIR / "alb2005_consumption_aggregate_metadata_crosswalk_summary.csv")
    alb2005_component_source_summary = read_csv_dicts(RESULT_DIR / "alb2005_consumption_component_source_search_summary.csv")
    alb2005_minimum_recipe_summary = read_csv_dicts(RESULT_DIR / "alb2005_minimum_recipe_promotion_summary.csv")
    alb2005_public_fieldwork_geo_summary = read_csv_dicts(RESULT_DIR / "alb2005_public_fieldwork_geo_metadata_summary.csv")
    alb2005_diary_timing_summary = read_csv_dicts(RESULT_DIR / "alb2005_diary_timing_candidate_summary.csv")
    alb2005_extracted_module_summary = read_csv_dicts(RESULT_DIR / "alb2005_extracted_module_coverage_summary.csv")
    alb2005_fallback_blocker_summary = read_csv_dicts(RESULT_DIR / "alb2005_fallback_blocker_resolution_summary.csv")
    albania_first_analysis_summary = read_csv_dicts(RESULT_DIR / "albania_first_analysis_promotion_summary.csv")
    albania_wave_summary = read_csv_dicts(RESULT_DIR / "albania_existing_raw_wave_audit_summary.csv")
    alb2008_core_summary = read_csv_dicts(RESULT_DIR / "alb2008_household_core_candidate_summary.csv")
    alb2008_outcome_summary = read_csv_dicts(RESULT_DIR / "alb2008_provisional_outcome_feasibility_summary.csv")
    alb2008_semantics_summary = read_csv_dicts(RESULT_DIR / "alb2008_outcome_semantics_raw_value_summary.csv")
    alb2008_timing_geo_summary = read_csv_dicts(RESULT_DIR / "alb2008_timing_geography_exhaustive_summary.csv")
    alb2008_fallback_blocker_summary = read_csv_dicts(RESULT_DIR / "alb2008_fallback_blocker_resolution_summary.csv")
    objective_trace = read_csv_dicts(TRACE_PATH)
    objective_guardrails = read_csv_dicts(GUARDRAIL_PATH)
    counts = {
        "source_inventory": row_count(TEMP_DIR / "source_inventory.csv"),
        "country_wave_screening": row_count(TEMP_DIR / "country_wave_screening.csv"),
        "manual_download_manifest": row_count(TEMP_DIR / "manual_download_manifest.csv"),
        "manual_download_priority": row_count(TEMP_DIR / "manual_download_priority.csv"),
        "manual_file_checklist": row_count(TEMP_DIR / "manual_download_file_checklist.csv"),
        "manual_access_action_queue": row_count(TEMP_DIR / "manual_access_action_queue.csv"),
        "worldbank_docs": row_count(TEMP_DIR / "worldbank_public_documentation_audit.csv"),
        "worldbank_docs_saved": count_status(TEMP_DIR / "worldbank_public_documentation_audit.csv", "status", "saved"),
        "raw_download_manifest": len(raw_manifest),
        "raw_download_intake": row_count(TEMP_DIR / "raw_download_intake_manifest.csv"),
        "raw_download_expected": row_count(TEMP_DIR / "raw_download_expected_files.csv"),
        "raw_download_intake_summary": row_count(RESULT_DIR / "raw_download_intake_summary.csv"),
        "raw_download_intake_ready": count_status(TEMP_DIR / "raw_download_intake_manifest.csv", "intake_status", "ready_for_raw_schema_inspection"),
        "raw_download_expected_not_present": count_status(TEMP_DIR / "raw_download_expected_files.csv", "expected_file_status", "not_present"),
        "public_external_downloads": len(public_external_downloads),
        "public_external_download_summary": row_count(RESULT_DIR / "public_external_raw_candidate_download_summary.csv"),
        "public_external_downloaded": sum(1 for row in public_external_downloads if row.get("download_status") in {"downloaded", "already_exists"}),
        "public_external_datasets": len({row.get("idno", "") for row in public_external_downloads if row.get("download_status") in {"downloaded", "already_exists"} and row.get("idno", "")}),
        "raw_like_files": sum(1 for row in raw_manifest if row.get("file_role") in {"archive", "raw_tabular_or_spreadsheet"}),
        "raw_like_targets": sum(1 for row in raw_targets if row.get("status") == "raw_or_archive_files_present"),
        "raw_files": row_count(TEMP_DIR / "raw_schema_inventory" / "raw_file_inventory.csv"),
        "raw_variables": row_count(TEMP_DIR / "raw_schema_inventory" / "raw_variable_catalog.csv"),
        "schema_studies": row_count(TEMP_DIR / "raw_schema_inventory" / "schema_study_inventory.csv"),
        "schema_files": row_count(TEMP_DIR / "raw_schema_inventory" / "schema_file_inventory.csv"),
        "metadata_variables": row_count(TEMP_DIR / "raw_schema_inventory" / "metadata_variable_catalog.csv"),
        "variable_maps": sum(row_count(path) for path in VARIABLE_MAP_FILES),
        "variable_confidence": row_count(TEMP_DIR / "variable_map_confidence_audit.csv"),
        "metadata_quality_priority": row_count(TEMP_DIR / "metadata_quality_download_priority.csv"),
        "raw_ingestion_plan": row_count(TEMP_DIR / "raw_ingestion_plan.csv"),
        "raw_ingestion_verified_concepts": count_status(TEMP_DIR / "raw_ingestion_concept_checklist.csv", "raw_verification_status", "raw_variables_inspected"),
        "raw_variable_verification_protocol": row_count(TEMP_DIR / "raw_variable_verification_protocol.csv"),
        "harmonization_scaffold": row_count(TEMP_DIR / "harmonization_recipe_scaffold.csv"),
        "raw_variable_verification_summary": row_count(RESULT_DIR / "raw_variable_verification_summary.csv"),
        "raw_variable_protocol_value_pending": count_status(TEMP_DIR / "raw_variable_verification_protocol.csv", "verification_status", "raw_variable_seen_value_audit_pending"),
        "raw_variable_protocol_not_inspected": count_status(TEMP_DIR / "raw_variable_verification_protocol.csv", "verification_status", "raw_not_inspected"),
        "harmonization_recipe_gate": row_count(TEMP_DIR / "harmonization_recipe_gate.csv"),
        "harmonization_value_audit_template": row_count(TEMP_DIR / "harmonization_value_audit_template.csv"),
        "harmonization_verified_candidates": row_count(TEMP_DIR / "harmonization_recipe_verified_candidates.csv"),
        "harmonization_readiness": row_count(RESULT_DIR / "harmonization_readiness_matrix.csv"),
        "harmonization_recipe_gate_summary": row_count(RESULT_DIR / "harmonization_recipe_gate_summary.csv"),
        "harmonization_ready_country_waves": count_status(RESULT_DIR / "harmonization_readiness_matrix.csv", "readiness_status", "ready_for_verified_recipe_assembly"),
        "analysis_dataset_promotion_barrier_audit": row_count(TEMP_DIR / "analysis_dataset_promotion_barrier_audit.csv"),
        "analysis_dataset_promotion_barrier_summary": len(analysis_promotion_summary),
        "analysis_dataset_promotion_audit_rows": safe_int(next((row.get("value", "0") for row in analysis_promotion_summary if row.get("metric") == "analysis_dataset_promotion_audit_rows"), "0")),
        "analysis_dataset_promotion_blocked_rows": safe_int(next((row.get("value", "0") for row in analysis_promotion_summary if row.get("metric") == "analysis_dataset_promotion_blocked_rows"), "0")),
        "analysis_dataset_promotion_promoted_rows": safe_int(next((row.get("value", "0") for row in analysis_promotion_summary if row.get("metric") == "analysis_dataset_promotion_promoted_rows"), "0")),
        "analysis_dataset_promotion_data_file_count": safe_int(next((row.get("value", "0") for row in analysis_promotion_summary if row.get("metric") == "analysis_dataset_promotion_data_file_count"), "0")),
        "analysis_dataset_promotion_verified_recipe_candidates": safe_int(next((row.get("value", "0") for row in analysis_promotion_summary if row.get("metric") == "analysis_dataset_promotion_verified_recipe_candidates"), "0")),
        "analysis_dataset_promotion_ready_country_waves": safe_int(next((row.get("value", "0") for row in analysis_promotion_summary if row.get("metric") == "analysis_dataset_promotion_ready_country_waves"), "0")),
        "analysis_dataset_promotion_alb2002_temp_core_rows": safe_int(next((row.get("value", "0") for row in analysis_promotion_summary if row.get("metric") == "analysis_dataset_promotion_alb2002_temp_core_rows"), "0")),
        "analysis_dataset_promotion_alb2002_weight_positive_rows": safe_int(next((row.get("value", "0") for row in analysis_promotion_summary if row.get("metric") == "analysis_dataset_promotion_alb2002_weight_positive_rows"), "0")),
        "analysis_dataset_promotion_alb2002_weight_key_match_rows": safe_int(next((row.get("value", "0") for row in analysis_promotion_summary if row.get("metric") == "analysis_dataset_promotion_alb2002_weight_key_match_rows"), "0")),
        "analysis_dataset_promotion_alb2002_weighted_inference_ready_rows": safe_int(next((row.get("value", "0") for row in analysis_promotion_summary if row.get("metric") == "analysis_dataset_promotion_alb2002_weighted_inference_ready_rows"), "0")),
        "analysis_dataset_promotion_alb2002_harmonized_ready_rows": safe_int(next((row.get("value", "0") for row in analysis_promotion_summary if row.get("metric") == "analysis_dataset_promotion_alb2002_harmonized_ready_rows"), "0")),
        "analysis_dataset_promotion_alb2002_outcome_ready_rows": safe_int(next((row.get("value", "0") for row in analysis_promotion_summary if row.get("metric") == "analysis_dataset_promotion_alb2002_outcome_ready_rows"), "0")),
        "analysis_dataset_promotion_alb2002_climate_linkage_ready_rows": safe_int(next((row.get("value", "0") for row in analysis_promotion_summary if row.get("metric") == "analysis_dataset_promotion_alb2002_climate_linkage_ready_rows"), "0")),
        "analysis_dataset_promotion_limited_harmonized_core_rows": safe_int(next((row.get("value", "0") for row in analysis_promotion_summary if row.get("metric") == "analysis_dataset_promotion_limited_harmonized_core_rows"), "0")),
        "analysis_dataset_promotion_limited_harmonized_core_data_write_ready_rows": safe_int(next((row.get("value", "0") for row in analysis_promotion_summary if row.get("metric") == "analysis_dataset_promotion_limited_harmonized_core_data_write_ready_rows"), "0")),
        "analysis_dataset_promotion_limited_harmonized_core_final_outcome_ready_rows": safe_int(next((row.get("value", "0") for row in analysis_promotion_summary if row.get("metric") == "analysis_dataset_promotion_limited_harmonized_core_final_outcome_ready_rows"), "0")),
        "analysis_dataset_promotion_limited_harmonized_core_climate_linkage_ready_rows": safe_int(next((row.get("value", "0") for row in analysis_promotion_summary if row.get("metric") == "analysis_dataset_promotion_limited_harmonized_core_climate_linkage_ready_rows"), "0")),
        "analysis_dataset_promotion_limited_harmonized_core_analysis_ready_rows": safe_int(next((row.get("value", "0") for row in analysis_promotion_summary if row.get("metric") == "analysis_dataset_promotion_limited_harmonized_core_analysis_ready_rows"), "0")),
        "analysis_dataset_promotion_limited_financial_outcome_rows": safe_int(next((row.get("value", "0") for row in analysis_promotion_summary if row.get("metric") == "analysis_dataset_promotion_limited_financial_outcome_rows"), "0")),
        "analysis_dataset_promotion_limited_financial_outcome_data_write_ready_rows": safe_int(next((row.get("value", "0") for row in analysis_promotion_summary if row.get("metric") == "analysis_dataset_promotion_limited_financial_outcome_data_write_ready_rows"), "0")),
        "analysis_dataset_promotion_limited_financial_outcome_che10_rows": safe_int(next((row.get("value", "0") for row in analysis_promotion_summary if row.get("metric") == "analysis_dataset_promotion_limited_financial_outcome_che10_rows"), "0")),
        "analysis_dataset_promotion_limited_financial_outcome_che25_rows": safe_int(next((row.get("value", "0") for row in analysis_promotion_summary if row.get("metric") == "analysis_dataset_promotion_limited_financial_outcome_che25_rows"), "0")),
        "analysis_dataset_promotion_limited_financial_outcome_sdg382_ready_rows": safe_int(next((row.get("value", "0") for row in analysis_promotion_summary if row.get("metric") == "analysis_dataset_promotion_limited_financial_outcome_sdg382_ready_rows"), "0")),
        "analysis_dataset_promotion_limited_financial_outcome_access_ready_rows": safe_int(next((row.get("value", "0") for row in analysis_promotion_summary if row.get("metric") == "analysis_dataset_promotion_limited_financial_outcome_access_ready_rows"), "0")),
        "analysis_dataset_promotion_limited_financial_outcome_composite_ready_rows": safe_int(next((row.get("value", "0") for row in analysis_promotion_summary if row.get("metric") == "analysis_dataset_promotion_limited_financial_outcome_composite_ready_rows"), "0")),
        "analysis_dataset_promotion_limited_financial_outcome_climate_linkage_ready_rows": safe_int(next((row.get("value", "0") for row in analysis_promotion_summary if row.get("metric") == "analysis_dataset_promotion_limited_financial_outcome_climate_linkage_ready_rows"), "0")),
        "analysis_dataset_promotion_limited_financial_outcome_analysis_ready_rows": safe_int(next((row.get("value", "0") for row in analysis_promotion_summary if row.get("metric") == "analysis_dataset_promotion_limited_financial_outcome_analysis_ready_rows"), "0")),
        "analysis_dataset_promotion_limited_climate_exposure_rows": safe_int(next((row.get("value", "0") for row in analysis_promotion_summary if row.get("metric") == "analysis_dataset_promotion_limited_climate_exposure_rows"), "0")),
        "analysis_dataset_promotion_limited_climate_exposure_data_write_ready_rows": safe_int(next((row.get("value", "0") for row in analysis_promotion_summary if row.get("metric") == "analysis_dataset_promotion_limited_climate_exposure_data_write_ready_rows"), "0")),
        "analysis_dataset_promotion_limited_climate_exposure_climate_linkage_ready_rows": safe_int(next((row.get("value", "0") for row in analysis_promotion_summary if row.get("metric") == "analysis_dataset_promotion_limited_climate_exposure_climate_linkage_ready_rows"), "0")),
        "analysis_dataset_promotion_limited_climate_exposure_analysis_ready_rows": safe_int(next((row.get("value", "0") for row in analysis_promotion_summary if row.get("metric") == "analysis_dataset_promotion_limited_climate_exposure_analysis_ready_rows"), "0")),
        "analysis_dataset_promotion_limited_climate_linked_rows": safe_int(next((row.get("value", "0") for row in analysis_promotion_summary if row.get("metric") == "analysis_dataset_promotion_limited_climate_linked_rows"), "0")),
        "analysis_dataset_promotion_limited_climate_linked_data_write_ready_rows": safe_int(next((row.get("value", "0") for row in analysis_promotion_summary if row.get("metric") == "analysis_dataset_promotion_limited_climate_linked_data_write_ready_rows"), "0")),
        "analysis_dataset_promotion_limited_climate_linked_descriptive_ready_rows": safe_int(next((row.get("value", "0") for row in analysis_promotion_summary if row.get("metric") == "analysis_dataset_promotion_limited_climate_linked_descriptive_ready_rows"), "0")),
        "analysis_dataset_promotion_limited_climate_linked_predictive_ml_ready_rows": safe_int(next((row.get("value", "0") for row in analysis_promotion_summary if row.get("metric") == "analysis_dataset_promotion_limited_climate_linked_predictive_ml_ready_rows"), "0")),
        "analysis_dataset_promotion_limited_climate_linked_reduced_form_ready_rows": safe_int(next((row.get("value", "0") for row in analysis_promotion_summary if row.get("metric") == "analysis_dataset_promotion_limited_climate_linked_reduced_form_ready_rows"), "0")),
        "analysis_dataset_promotion_limited_climate_linked_robustness_ready_rows": safe_int(next((row.get("value", "0") for row in analysis_promotion_summary if row.get("metric") == "analysis_dataset_promotion_limited_climate_linked_robustness_ready_rows"), "0")),
        "analysis_dataset_promotion_limited_climate_linked_analysis_ready_rows": safe_int(next((row.get("value", "0") for row in analysis_promotion_summary if row.get("metric") == "analysis_dataset_promotion_limited_climate_linked_analysis_ready_rows"), "0")),
        "analysis_dataset_promotion_current_decision": next((row.get("value", "") for row in analysis_promotion_summary if row.get("metric") == "analysis_dataset_promotion_current_decision"), ""),
        "alb2002_harmonized_core_promotion_audit": row_count(TEMP_DIR / "alb2002_harmonized_household_core_promotion_audit.csv"),
        "alb2002_harmonized_core_promotion_summary": len(alb2002_harmonized_core_summary),
        "alb2002_harmonized_core_rows": safe_int(next((row.get("value", "0") for row in alb2002_harmonized_core_summary if row.get("metric") == "alb2002_harmonized_household_core_rows"), "0")),
        "limited_harmonized_core_marker": 1 if has_limited_harmonized_core_marker(DATA_DIR / "harmonized_household.csv") else 0,
        "alb2002_limited_financial_outcome_promotion_audit": row_count(TEMP_DIR / "alb2002_limited_financial_outcome_promotion_audit.csv"),
        "alb2002_limited_financial_outcome_promotion_summary": len(alb2002_limited_financial_summary),
        "alb2002_limited_financial_outcome_rows": safe_int(next((row.get("value", "0") for row in alb2002_limited_financial_summary if row.get("metric") == "alb2002_limited_financial_outcome_rows"), "0")),
        "alb2002_limited_climate_exposure_promotion_audit": row_count(TEMP_DIR / "alb2002_limited_climate_exposure_promotion_audit.csv"),
        "alb2002_limited_climate_exposure_promotion_summary": len(alb2002_limited_climate_summary),
        "alb2002_limited_climate_exposure_rows": safe_int(next((row.get("value", "0") for row in alb2002_limited_climate_summary if row.get("metric") == "alb2002_limited_climate_exposure_rows"), "0")),
        "limited_climate_exposure_marker": 1 if has_limited_climate_exposure_marker(DATA_DIR / "climate_exposures_nasa_power.csv") else 0,
        "alb2002_limited_climate_linked_rows": safe_int(next((row.get("value", "0") for row in alb2002_limited_linked_summary if row.get("metric") == "alb2002_limited_climate_linked_rows"), "0")),
        "alb2002_limited_climate_linked_descriptive_ready_rows": safe_int(next((row.get("value", "0") for row in alb2002_limited_linked_summary if row.get("metric") == "alb2002_limited_climate_linked_descriptive_ready_rows"), "0")),
        "alb2002_limited_climate_linked_predictive_ml_ready_rows": safe_int(next((row.get("value", "0") for row in alb2002_limited_linked_summary if row.get("metric") == "alb2002_limited_climate_linked_predictive_ml_ready_rows"), "0")),
        "alb2002_limited_climate_linked_reduced_form_ready_rows": safe_int(next((row.get("value", "0") for row in alb2002_limited_linked_summary if row.get("metric") == "alb2002_limited_climate_linked_reduced_form_ready_rows"), "0")),
        "alb2002_limited_climate_linked_robustness_ready_rows": safe_int(next((row.get("value", "0") for row in alb2002_limited_linked_summary if row.get("metric") == "alb2002_limited_climate_linked_robustness_ready_rows"), "0")),
        "alb2002_limited_climate_linked_final_analysis_ready_rows": safe_int(next((row.get("value", "0") for row in alb2002_limited_linked_summary if row.get("metric") == "alb2002_limited_climate_linked_final_analysis_ready_rows"), "0")),
        "limited_climate_linked_marker": 1 if has_limited_climate_linked_marker(DATA_DIR / "climate_linked_household.csv") else 0,
        "minimum_viable_acquisition_targets": row_count(RESULT_DIR / "minimum_viable_acquisition_targets.csv"),
        "minimum_viable_download_bundles": row_count(TEMP_DIR / "minimum_viable_download_bundles.csv"),
        "minimum_viable_acquisition_summary": row_count(RESULT_DIR / "minimum_viable_acquisition_summary.csv"),
        "minimum_viable_financial_probe": count_status(RESULT_DIR / "minimum_viable_acquisition_targets.csv", "acquisition_set", "financial_6_country_probe"),
        "minimum_viable_double_probe": count_status(RESULT_DIR / "minimum_viable_acquisition_targets.csv", "acquisition_set", "double_failure_10_wave_probe"),
        "harmonized_household": row_count(DATA_DIR / "harmonized_household.csv"),
        "harmonization_audit": row_count(TEMP_DIR / "harmonization_audit.csv"),
        "household_outcomes": row_count(DATA_DIR / "household_outcomes.csv"),
        "limited_household_outcome_marker": 1 if has_limited_household_outcome_marker(DATA_DIR / "household_outcomes.csv") else 0,
        "outcome_audit": row_count(RESULT_DIR / "outcome_audit.csv"),
        "outcome_audit_constructed": count_status(RESULT_DIR / "outcome_audit.csv", "status", "constructed"),
        "outcome_plan": row_count(TEMP_DIR / "outcome_denominator_plan.csv"),
        "outcome_ready": count_status(TEMP_DIR / "outcome_denominator_plan.csv", "outcome_gate_status", "ready_for_harmonized_outcome_construction"),
        "sdg382_denominator_requirements": row_count(TEMP_DIR / "sdg382_denominator_requirements.csv"),
        "sdg382_denominator_source_matrix": row_count(RESULT_DIR / "sdg382_denominator_source_matrix.csv"),
        "sdg382_denominator_readiness": row_count(RESULT_DIR / "sdg382_denominator_country_wave_readiness.csv"),
        "sdg382_denominator_summary": row_count(RESULT_DIR / "sdg382_denominator_summary.csv"),
        "sdg382_denominator_ready": count_status(RESULT_DIR / "sdg382_denominator_country_wave_readiness.csv", "readiness_status", "ready_for_household_denominator_value_audit"),
        "sdg382_denominator_blocked": sum(1 for row in read_csv_dicts(RESULT_DIR / "sdg382_denominator_country_wave_readiness.csv") if row.get("readiness_status") != "ready_for_household_denominator_value_audit"),
        "climate_source_probe": row_count(TEMP_DIR / "climate_source_probe.csv"),
        "climate_source_probe_ok": sum(
            1
            for row in read_csv_dicts(TEMP_DIR / "climate_source_probe.csv")
            if row.get("status") in {"reachable_snapshot_saved", "pass_api_parameters_present"}
        ),
        "climate_exposure_plan": row_count(TEMP_DIR / "climate_exposure_plan.csv"),
        "climate_exposure_specs": row_count(RESULT_DIR / "climate_exposure_specification.csv"),
        "climate_linkage_requirements": row_count(TEMP_DIR / "climate_linkage_requirements.csv"),
        "climate_source_method_matrix": row_count(RESULT_DIR / "climate_source_method_matrix.csv"),
        "climate_validation_protocol": row_count(RESULT_DIR / "climate_exposure_validation_protocol.csv"),
        "climate_linkage_readiness": row_count(RESULT_DIR / "climate_linkage_readiness.csv"),
        "climate_validation_summary": row_count(RESULT_DIR / "climate_validation_protocol_summary.csv"),
        "climate_linkage_ready_value": count_status(RESULT_DIR / "climate_linkage_readiness.csv", "readiness_status", "ready_for_climate_linkage_value_audit"),
        "climate_linkage_blocked_value": sum(1 for row in read_csv_dicts(RESULT_DIR / "climate_linkage_readiness.csv") if row.get("readiness_status") != "ready_for_climate_linkage_value_audit"),
        "climate_exposures": row_count(DATA_DIR / "climate_exposures_nasa_power.csv"),
        "climate_audit": row_count(TEMP_DIR / "climate_extraction_audit.csv"),
        "climate_linked": row_count(DATA_DIR / "climate_linked_household.csv"),
        "climate_merge_audit": row_count(TEMP_DIR / "climate_merge_audit.csv"),
        "descriptive_prevalence": row_count(RESULT_DIR / "descriptive_weighted_prevalence.csv"),
        "descriptive_missingness": row_count(RESULT_DIR / "descriptive_missingness.csv"),
        "sample_flow": row_count(RESULT_DIR / "sample_inclusion_flow.csv"),
        "sample_gate": len(sample_gate),
        "sample_gate_raw_final": sum(1 for row in sample_gate if row.get("eligible_for_final_sample") == "1"),
        "sample_gate_failed_rules": sum(1 for row in sample_gate_summary if row.get("status") == "fail"),
        "alb2002_district_climate_crosswalk_template": row_count(TEMP_DIR / "alb2002_district_climate_crosswalk_template.csv"),
        "alb2002_district_boundary_source_probe": row_count(TEMP_DIR / "alb2002_district_boundary_source_probe.csv"),
        "alb2002_district_climate_crosswalk_summary": len(alb2002_crosswalk_summary),
        "alb2002_district_crosswalk_district_rows": safe_int(next((row.get("value", "0") for row in alb2002_crosswalk_summary if row.get("metric") == "alb2002_district_crosswalk_district_rows"), "0")),
        "alb2002_district_crosswalk_source_reachable_rows": safe_int(next((row.get("value", "0") for row in alb2002_crosswalk_summary if row.get("metric") == "alb2002_district_crosswalk_boundary_source_reachable_rows"), "0")),
        "alb2002_climate_linkage_ready_rows": safe_int(next((row.get("value", "0") for row in alb2002_crosswalk_summary if row.get("metric") == "alb2002_climate_linkage_ready_rows"), "0")),
        "alb2002_boundary_name_match_audit": row_count(TEMP_DIR / "alb2002_boundary_name_match_audit.csv"),
        "alb2002_boundary_geojson_inventory": row_count(TEMP_DIR / "alb2002_boundary_geojson_inventory.csv"),
        "alb2002_boundary_name_match_summary": len(alb2002_boundary_name_summary),
        "alb2002_boundary_name_match_exact_rows": safe_int(next((row.get("value", "0") for row in alb2002_boundary_name_summary if row.get("metric") == "alb2002_boundary_name_match_exact_rows"), "0")),
        "alb2002_boundary_name_match_euro_repaired_rows": safe_int(next((row.get("value", "0") for row in alb2002_boundary_name_summary if row.get("metric") == "alb2002_boundary_name_match_euro_repaired_rows"), "0")),
        "alb2002_boundary_name_match_unmatched_survey_rows": safe_int(next((row.get("value", "0") for row in alb2002_boundary_name_summary if row.get("metric") == "alb2002_boundary_name_match_unmatched_survey_rows"), "0")),
        "alb2002_boundary_name_match_duplicate_boundary_name_keys": safe_int(next((row.get("value", "0") for row in alb2002_boundary_name_summary if row.get("metric") == "alb2002_boundary_name_match_duplicate_boundary_name_keys"), "0")),
        "alb2002_boundary_name_match_historical_year_ready_rows": safe_int(next((row.get("value", "0") for row in alb2002_boundary_name_summary if row.get("metric") == "alb2002_boundary_name_match_historical_year_ready_rows"), "0")),
        "alb2002_boundary_name_match_climate_linkage_ready_rows": safe_int(next((row.get("value", "0") for row in alb2002_boundary_name_summary if row.get("metric") == "alb2002_boundary_name_match_climate_linkage_ready_rows"), "0")),
        "alb2002_boundary_source_alternative_audit": row_count(TEMP_DIR / "alb2002_boundary_source_alternative_audit.csv"),
        "alb2002_boundary_source_alternative_summary": len(alb2002_boundary_source_summary),
        "alb2002_boundary_source_alternative_rows": safe_int(next((row.get("value", "0") for row in alb2002_boundary_source_summary if row.get("metric") == "alb2002_boundary_source_alternative_rows"), "0")),
        "alb2002_boundary_source_alternative_reachable_rows": safe_int(next((row.get("value", "0") for row in alb2002_boundary_source_summary if row.get("metric") == "alb2002_boundary_source_alternative_reachable_rows"), "0")),
        "alb2002_boundary_source_alternative_historical_2002_boundary_ready_rows": safe_int(next((row.get("value", "0") for row in alb2002_boundary_source_summary if row.get("metric") == "alb2002_boundary_source_alternative_historical_2002_boundary_ready_rows"), "0")),
        "alb2002_boundary_source_alternative_climate_linkage_ready_rows": safe_int(next((row.get("value", "0") for row in alb2002_boundary_source_summary if row.get("metric") == "alb2002_boundary_source_alternative_climate_linkage_ready_rows"), "0")),
        "alb2002_boundary_resource_search_audit": row_count(TEMP_DIR / "alb2002_boundary_source_resource_search_audit.csv"),
        "alb2002_boundary_resource_search_summary": len(alb2002_boundary_resource_summary),
        "alb2002_boundary_resource_search_candidate_rows": safe_int(next((row.get("value", "0") for row in alb2002_boundary_resource_summary if row.get("metric") == "alb2002_boundary_resource_search_candidate_rows"), "0")),
        "alb2002_boundary_resource_search_complete_name_coverage_rows": safe_int(next((row.get("value", "0") for row in alb2002_boundary_resource_summary if row.get("metric") == "alb2002_boundary_resource_search_complete_name_coverage_rows"), "0")),
        "alb2002_boundary_resource_search_exact_unit_count_rows": safe_int(next((row.get("value", "0") for row in alb2002_boundary_resource_summary if row.get("metric") == "alb2002_boundary_resource_search_exact_unit_count_rows"), "0")),
        "alb2002_boundary_resource_search_2002_historical_ready_rows": safe_int(next((row.get("value", "0") for row in alb2002_boundary_resource_summary if row.get("metric") == "alb2002_boundary_resource_search_2002_historical_ready_rows"), "0")),
        "alb2002_boundary_resource_search_climate_linkage_ready_rows": safe_int(next((row.get("value", "0") for row in alb2002_boundary_resource_summary if row.get("metric") == "alb2002_boundary_resource_search_climate_linkage_ready_rows"), "0")),
        "alb2002_boundary_resource_search_best_candidate_exact_matches": safe_int(next((row.get("value", "0") for row in alb2002_boundary_resource_summary if row.get("metric") == "alb2002_boundary_resource_search_best_candidate_exact_matches"), "0")),
        "alb2002_boundary_resource_search_best_candidate_repaired_matches": safe_int(next((row.get("value", "0") for row in alb2002_boundary_resource_summary if row.get("metric") == "alb2002_boundary_resource_search_best_candidate_repaired_matches"), "0")),
        "alb2002_boundary_resource_search_best_candidate_alias_matches": safe_int(next((row.get("value", "0") for row in alb2002_boundary_resource_summary if row.get("metric") == "alb2002_boundary_resource_search_best_candidate_alias_matches"), "0")),
        "alb2002_boundary_geometry_provenance_audit": row_count(TEMP_DIR / "alb2002_boundary_geometry_provenance_audit.csv"),
        "alb2002_boundary_metadata_provenance_probe": row_count(TEMP_DIR / "alb2002_boundary_metadata_provenance_probe.csv"),
        "alb2002_boundary_geometry_provenance_summary": len(alb2002_boundary_geometry_summary),
        "alb2002_boundary_geometry_feature_rows": safe_int(next((row.get("value", "0") for row in alb2002_boundary_geometry_summary if row.get("metric") == "alb2002_boundary_geometry_feature_rows"), "0")),
        "alb2002_boundary_geometry_coordinate_structure_ok_rows": safe_int(next((row.get("value", "0") for row in alb2002_boundary_geometry_summary if row.get("metric") == "alb2002_boundary_geometry_coordinate_structure_ok_rows"), "0")),
        "alb2002_boundary_geometry_survey_key_matched_rows": safe_int(next((row.get("value", "0") for row in alb2002_boundary_geometry_summary if row.get("metric") == "alb2002_boundary_geometry_survey_key_matched_rows"), "0")),
        "alb2002_boundary_geometry_metadata_boundary_year": safe_int(next((row.get("value", "0") for row in alb2002_boundary_geometry_summary if row.get("metric") == "alb2002_boundary_geometry_metadata_boundary_year"), "0")),
        "alb2002_boundary_geometry_boundary_year_matches_2002_rows": safe_int(next((row.get("value", "0") for row in alb2002_boundary_geometry_summary if row.get("metric") == "alb2002_boundary_geometry_boundary_year_matches_2002_rows"), "0")),
        "alb2002_boundary_geometry_topology_validated_rows": safe_int(next((row.get("value", "0") for row in alb2002_boundary_geometry_summary if row.get("metric") == "alb2002_boundary_geometry_topology_validated_rows"), "0")),
        "alb2002_boundary_geometry_historical_2002_boundary_ready_rows": safe_int(next((row.get("value", "0") for row in alb2002_boundary_geometry_summary if row.get("metric") == "alb2002_boundary_geometry_historical_2002_boundary_ready_rows"), "0")),
        "alb2002_boundary_geometry_climate_linkage_ready_rows": safe_int(next((row.get("value", "0") for row in alb2002_boundary_geometry_summary if row.get("metric") == "alb2002_boundary_geometry_climate_linkage_ready_rows"), "0")),
        "alb2002_boundary_manual_verification_action_rows": row_count(TEMP_DIR / "alb2002_boundary_manual_verification_action_queue.csv"),
        "alb2002_boundary_manual_verification_gate_rows": row_count(TEMP_DIR / "alb2002_boundary_promotion_gate_checklist.csv"),
        "alb2002_boundary_manual_verification_summary_rows": len(alb2002_boundary_manual_summary),
        "alb2002_boundary_manual_verification_candidate_evidence_gates": safe_int(next((row.get("value", "0") for row in alb2002_boundary_manual_summary if row.get("metric") == "alb2002_boundary_manual_verification_candidate_evidence_gates"), "0")),
        "alb2002_boundary_manual_verification_blocked_gates": safe_int(next((row.get("value", "0") for row in alb2002_boundary_manual_summary if row.get("metric") == "alb2002_boundary_manual_verification_blocked_gates"), "0")),
        "alb2002_boundary_manual_verification_high_priority_actions": safe_int(next((row.get("value", "0") for row in alb2002_boundary_manual_summary if row.get("metric") == "alb2002_boundary_manual_verification_high_priority_actions"), "0")),
        "alb2002_boundary_manual_verification_pre2011_digital_map_absence_rows": safe_int(next((row.get("value", "0") for row in alb2002_boundary_manual_summary if row.get("metric") == "alb2002_boundary_manual_verification_pre2011_digital_map_absence_rows"), "0")),
        "alb2002_boundary_manual_verification_climate_linkage_ready_rows": safe_int(next((row.get("value", "0") for row in alb2002_boundary_manual_summary if row.get("metric") == "alb2002_boundary_manual_verification_climate_linkage_ready_rows"), "0")),
        "alb2002_boundary_manual_source_followup_audit": row_count(TEMP_DIR / "alb2002_boundary_manual_source_followup_audit.csv"),
        "alb2002_boundary_manual_source_followup_summary_rows": len(alb2002_boundary_followup_summary),
        "alb2002_boundary_manual_source_followup_rows": safe_int(next((row.get("value", "0") for row in alb2002_boundary_followup_summary if row.get("metric") == "alb2002_boundary_manual_source_followup_rows"), "0")),
        "alb2002_boundary_manual_source_followup_conclusive_blocker_rows": safe_int(next((row.get("value", "0") for row in alb2002_boundary_followup_summary if row.get("metric") == "alb2002_boundary_manual_source_followup_conclusive_blocker_rows"), "0")),
        "alb2002_boundary_manual_source_followup_district_level_ready_rows": safe_int(next((row.get("value", "0") for row in alb2002_boundary_followup_summary if row.get("metric") == "alb2002_boundary_manual_source_followup_district_level_ready_rows"), "0")),
        "alb2002_boundary_manual_source_followup_climate_linkage_ready_rows": safe_int(next((row.get("value", "0") for row in alb2002_boundary_followup_summary if row.get("metric") == "alb2002_boundary_manual_source_followup_climate_linkage_ready_rows"), "0")),
        "alb2002_boundary_manual_source_followup_unece_pre2011_map_status": next((row.get("value", "") for row in alb2002_boundary_followup_summary if row.get("metric") == "alb2002_boundary_manual_source_followup_unece_pre2011_map_status"), ""),
        "alb2002_gadm_boundary_lead_audit": row_count(TEMP_DIR / "alb2002_gadm_boundary_lead_audit.csv"),
        "alb2002_gadm_boundary_name_match_audit": row_count(TEMP_DIR / "alb2002_gadm_boundary_name_match_audit.csv"),
        "alb2002_gadm_boundary_lead_summary_rows": len(alb2002_gadm_summary),
        "alb2002_gadm_boundary_lead_candidate_rows": safe_int(next((row.get("value", "0") for row in alb2002_gadm_summary if row.get("metric") == "alb2002_gadm_boundary_lead_candidate_rows"), "0")),
        "alb2002_gadm36_adm2_row_count": safe_int(next((row.get("value", "0") for row in alb2002_gadm_summary if row.get("metric") == "alb2002_gadm36_adm2_row_count"), "0")),
        "alb2002_gadm36_distinct_normalized_key_count": safe_int(next((row.get("value", "0") for row in alb2002_gadm_summary if row.get("metric") == "alb2002_gadm36_distinct_normalized_key_count"), "0")),
        "alb2002_gadm36_engtype_district_rows": safe_int(next((row.get("value", "0") for row in alb2002_gadm_summary if row.get("metric") == "alb2002_gadm36_engtype_district_rows"), "0")),
        "alb2002_gadm36_complete_name_coverage_rows": safe_int(next((row.get("value", "0") for row in alb2002_gadm_summary if row.get("metric") == "alb2002_gadm36_complete_name_coverage_rows"), "0")),
        "alb2002_gadm36_duplicate_boundary_key_count": safe_int(next((row.get("value", "0") for row in alb2002_gadm_summary if row.get("metric") == "alb2002_gadm36_duplicate_boundary_key_count"), "0")),
        "alb2002_gadm_boundary_lead_historical_2002_ready_rows": safe_int(next((row.get("value", "0") for row in alb2002_gadm_summary if row.get("metric") == "alb2002_gadm_boundary_lead_historical_2002_ready_rows"), "0")),
        "alb2002_gadm_boundary_lead_climate_linkage_ready_rows": safe_int(next((row.get("value", "0") for row in alb2002_gadm_summary if row.get("metric") == "alb2002_gadm_boundary_lead_climate_linkage_ready_rows"), "0")),
        "alb2002_gadm_boundary_lead_current_decision": next((row.get("value", "") for row in alb2002_gadm_summary if row.get("metric") == "alb2002_gadm_boundary_lead_current_decision"), ""),
        "alb2002_local_geo_artifact_audit": row_count(TEMP_DIR / "alb2002_local_geography_artifact_audit.csv"),
        "alb2002_local_geo_artifact_summary": len(alb2002_local_geo_summary),
        "alb2002_local_geo_artifact_files_scanned": safe_int(next((row.get("value", "0") for row in alb2002_local_geo_summary if row.get("metric") == "alb2002_local_geo_artifact_files_scanned"), "0")),
        "alb2002_local_geo_artifact_coordinate_raw_variable_rows": safe_int(next((row.get("value", "0") for row in alb2002_local_geo_summary if row.get("metric") == "alb2002_local_geo_artifact_coordinate_raw_variable_rows"), "0")),
        "alb2002_local_geo_artifact_questionnaire_coordinate_field_rows": safe_int(next((row.get("value", "0") for row in alb2002_local_geo_summary if row.get("metric") == "alb2002_local_geo_artifact_questionnaire_coordinate_field_rows"), "0")),
        "alb2002_local_geo_artifact_admin_variable_rows": safe_int(next((row.get("value", "0") for row in alb2002_local_geo_summary if row.get("metric") == "alb2002_local_geo_artifact_admin_variable_rows"), "0")),
        "alb2002_local_geo_artifact_local_coordinate_ready_rows": safe_int(next((row.get("value", "0") for row in alb2002_local_geo_summary if row.get("metric") == "alb2002_local_geo_artifact_local_coordinate_ready_rows"), "0")),
        "alb2002_local_geo_artifact_local_boundary_ready_rows": safe_int(next((row.get("value", "0") for row in alb2002_local_geo_summary if row.get("metric") == "alb2002_local_geo_artifact_local_boundary_ready_rows"), "0")),
        "alb2002_local_geo_artifact_climate_linkage_ready_rows": safe_int(next((row.get("value", "0") for row in alb2002_local_geo_summary if row.get("metric") == "alb2002_local_geo_artifact_climate_linkage_ready_rows"), "0")),
        "alb2012_household_core_candidate": row_count(TEMP_DIR / "alb2012_household_core_candidate.csv"),
        "alb2012_raw_core_feasibility_audit": row_count(TEMP_DIR / "alb2012_raw_core_feasibility_audit.csv"),
        "alb2012_raw_core_lineage": row_count(TEMP_DIR / "alb2012_raw_core_lineage.csv"),
        "alb2012_raw_core_feasibility_summary": len(alb2012_summary),
        "alb2012_household_core_recipe_ready_rows": safe_int(next((row.get("value", "0") for row in alb2012_summary if row.get("metric") == "alb2012_household_core_recipe_ready_rows"), "0")),
        "alb2012_climate_linkage_ready_rows": safe_int(next((row.get("value", "0") for row in alb2012_summary if row.get("metric") == "alb2012_climate_linkage_ready_rows"), "0")),
        "alb2012_timing_signal_rows": safe_int(next((row.get("value", "0") for row in alb2012_summary if row.get("metric") == "alb2012_timing_signal_rows"), "0")),
        "alb2012_households_with_oop_4w_positive": safe_int(next((row.get("value", "0") for row in alb2012_summary if row.get("metric") == "alb2012_households_with_oop_4w_positive"), "0")),
        "alb2012_provisional_outcome_feasibility_audit": row_count(TEMP_DIR / "alb2012_provisional_outcome_feasibility_audit.csv"),
        "alb2012_provisional_outcome_feasibility_summary": len(alb2012_outcome_summary),
        "alb2012_provisional_outcome_ready_rows": safe_int(next((row.get("value", "0") for row in alb2012_outcome_summary if row.get("metric") == "alb2012_provisional_outcome_ready_rows"), "0")),
        "alb2012_provisional_climate_linkage_ready_rows": safe_int(next((row.get("value", "0") for row in alb2012_outcome_summary if row.get("metric") == "alb2012_provisional_climate_linkage_ready_rows"), "0")),
        "alb2012_outcome_semantics_raw_value_audit": row_count(TEMP_DIR / "alb2012_outcome_semantics_raw_value_audit.csv"),
        "alb2012_outcome_semantics_raw_value_summary": len(alb2012_semantics_summary),
        "alb2012_outcome_semantics_outcome_ready_rows": safe_int(next((row.get("value", "0") for row in alb2012_semantics_summary if row.get("metric") == "alb2012_outcome_semantics_outcome_ready_rows"), "0")),
        "alb2012_outcome_semantics_sdg382_ready_rows": safe_int(next((row.get("value", "0") for row in alb2012_semantics_summary if row.get("metric") == "alb2012_outcome_semantics_sdg382_ready_rows"), "0")),
        "alb2012_outcome_semantics_climate_linkage_ready_rows": safe_int(next((row.get("value", "0") for row in alb2012_semantics_summary if row.get("metric") == "alb2012_outcome_semantics_climate_linkage_ready_rows"), "0")),
        "alb2012_outcome_semantics_financial_oop_candidate_rows": safe_int(next((row.get("value", "0") for row in alb2012_semantics_summary if row.get("metric") == "alb2012_outcome_semantics_financial_oop_candidate_rows"), "0")),
        "alb2012_outcome_semantics_gift_candidate_rows": safe_int(next((row.get("value", "0") for row in alb2012_semantics_summary if row.get("metric") == "alb2012_outcome_semantics_gift_candidate_rows"), "0")),
        "alb2012_outcome_semantics_access_candidate_rows": safe_int(next((row.get("value", "0") for row in alb2012_semantics_summary if row.get("metric") == "alb2012_outcome_semantics_access_candidate_rows"), "0")),
        "alb2012_outcome_semantics_service_quality_proxy_rows": safe_int(next((row.get("value", "0") for row in alb2012_semantics_summary if row.get("metric") == "alb2012_outcome_semantics_service_quality_proxy_rows"), "0")),
        "alb2012_outcome_semantics_conditional_reason_rows": safe_int(next((row.get("value", "0") for row in alb2012_semantics_summary if row.get("metric") == "alb2012_outcome_semantics_conditional_reason_rows"), "0")),
        "alb2012_timing_geography_exhaustive_audit": row_count(TEMP_DIR / "alb2012_timing_geography_exhaustive_audit.csv"),
        "alb2012_timing_geography_exhaustive_summary": len(alb2012_timing_geo_summary),
        "alb2012_interview_timing_verified_rows": safe_int(next((row.get("value", "0") for row in alb2012_timing_geo_summary if row.get("metric") == "alb2012_interview_timing_verified_rows"), "0")),
        "alb2012_coordinate_candidate_rows": safe_int(next((row.get("value", "0") for row in alb2012_timing_geo_summary if row.get("metric") == "alb2012_coordinate_candidate_rows"), "0")),
        "alb2012_timing_geography_climate_linkage_ready_rows": safe_int(next((row.get("value", "0") for row in alb2012_timing_geo_summary if row.get("metric") == "alb2012_climate_linkage_ready_rows"), "0")),
        "alb2012_questionnaire_timing_field_audit": row_count(TEMP_DIR / "alb2012_questionnaire_timing_field_audit.csv"),
        "alb2012_questionnaire_timing_raw_gap_audit": row_count(TEMP_DIR / "alb2012_questionnaire_timing_raw_gap_audit.csv"),
        "alb2012_questionnaire_timing_field_summary": len(alb2012_questionnaire_timing_summary),
        "alb2012_questionnaire_timing_field_rows": safe_int(next((row.get("value", "0") for row in alb2012_questionnaire_timing_summary if row.get("metric") == "alb2012_questionnaire_timing_field_rows"), "0")),
        "alb2012_questionnaire_timing_raw_gap_rows": safe_int(next((row.get("value", "0") for row in alb2012_questionnaire_timing_summary if row.get("metric") == "alb2012_questionnaire_timing_raw_gap_rows"), "0")),
        "alb2012_questionnaire_timing_raw_control_candidate_rows": safe_int(next((row.get("value", "0") for row in alb2012_questionnaire_timing_summary if row.get("metric") == "alb2012_questionnaire_timing_raw_control_candidate_rows"), "0")),
        "alb2012_questionnaire_timing_raw_verified_interview_timing_rows": safe_int(next((row.get("value", "0") for row in alb2012_questionnaire_timing_summary if row.get("metric") == "alb2012_questionnaire_timing_raw_verified_interview_timing_rows"), "0")),
        "alb2012_questionnaire_timing_climate_linkage_ready_rows": safe_int(next((row.get("value", "0") for row in alb2012_questionnaire_timing_summary if row.get("metric") == "alb2012_questionnaire_timing_climate_linkage_ready_rows"), "0")),
        "albania_legacy_questionnaire_readability_audit": row_count(TEMP_DIR / "albania_legacy_questionnaire_readability_audit.csv"),
        "albania_legacy_questionnaire_readability_summary": len(albania_legacy_questionnaire_summary),
        "albania_legacy_questionnaire_present_files": safe_int(next((row.get("value", "0") for row in albania_legacy_questionnaire_summary if row.get("metric") == "albania_legacy_questionnaire_present_files"), "0")),
        "albania_legacy_questionnaire_read_ok_files": safe_int(next((row.get("value", "0") for row in albania_legacy_questionnaire_summary if row.get("metric") == "albania_legacy_questionnaire_read_ok_files"), "0")),
        "albania_legacy_questionnaire_missing_reader_blocked_files": safe_int(next((row.get("value", "0") for row in albania_legacy_questionnaire_summary if row.get("metric") == "albania_legacy_questionnaire_missing_reader_blocked_files"), "0")),
        "albania_legacy_questionnaire_timing_content_audit_ready_rows": safe_int(next((row.get("value", "0") for row in albania_legacy_questionnaire_summary if row.get("metric") == "albania_legacy_questionnaire_timing_content_audit_ready_rows"), "0")),
        "albania_legacy_questionnaire_climate_linkage_ready_rows": safe_int(next((row.get("value", "0") for row in albania_legacy_questionnaire_summary if row.get("metric") == "albania_legacy_questionnaire_climate_linkage_ready_rows"), "0")),
        "albania_legacy_questionnaire_timing_field_audit": row_count(TEMP_DIR / "albania_legacy_questionnaire_timing_field_audit.csv"),
        "albania_legacy_questionnaire_timing_raw_gap_audit": row_count(TEMP_DIR / "albania_legacy_questionnaire_timing_raw_gap_audit.csv"),
        "albania_legacy_questionnaire_timing_field_summary": len(albania_legacy_questionnaire_timing_summary),
        "albania_legacy_questionnaire_timing_field_rows": safe_int(next((row.get("value", "0") for row in albania_legacy_questionnaire_timing_summary if row.get("metric") == "albania_legacy_questionnaire_timing_field_rows"), "0")),
        "albania_legacy_questionnaire_timing_raw_gap_rows": safe_int(next((row.get("value", "0") for row in albania_legacy_questionnaire_timing_summary if row.get("metric") == "albania_legacy_questionnaire_timing_raw_gap_rows"), "0")),
        "albania_legacy_questionnaire_timing_raw_verified_interview_timing_rows": safe_int(next((row.get("value", "0") for row in albania_legacy_questionnaire_timing_summary if row.get("metric") == "albania_legacy_questionnaire_timing_raw_verified_interview_timing_rows"), "0")),
        "albania_legacy_questionnaire_timing_climate_linkage_ready_rows": safe_int(next((row.get("value", "0") for row in albania_legacy_questionnaire_timing_summary if row.get("metric") == "albania_legacy_questionnaire_timing_climate_linkage_ready_rows"), "0")),
        "predictive_metrics": row_count(RESULT_DIR / "predictive_ml_metrics.csv"),
        "predictive_audit": row_count(RESULT_DIR / "predictive_ml_audit.csv"),
        "reduced_form_estimates": row_count(RESULT_DIR / "reduced_form_estimates.csv"),
        "causal_model_audit": row_count(RESULT_DIR / "causal_model_audit.csv"),
        "placebo_readiness": row_count(RESULT_DIR / "placebo_readiness_audit.csv"),
        "causal_ml_policy_audit": row_count(RESULT_DIR / "causal_ml_policy_audit.csv"),
        "causal_ml_rejected": count_status_prefix(RESULT_DIR / "causal_ml_policy_audit.csv", "status", ("rejected_",)),
        "robustness_results": row_count(RESULT_DIR / "robustness_results.csv"),
        "robustness_attempted": count_status_prefix(RESULT_DIR / "robustness_results.csv", "status", ("complete", "attempted")),
        "modeling_plan": len(modeling_plan),
        "modeling_predictive_ready": sum(1 for row in modeling_plan if row.get("predictive_ml_gate_status") == "ready_for_nonrandom_validation_design"),
        "modeling_reduced_ready": sum(1 for row in modeling_plan if row.get("reduced_form_gate_status") == "ready_for_reduced_form_estimation_design"),
        "modeling_causal_ml_ready": sum(1 for row in modeling_plan if row.get("causal_ml_policy_gate_status") == "ready_for_causal_ml_specification"),
        "modeling_policy_ready": sum(1 for row in modeling_plan if row.get("policy_learning_gate_status") == "ready_for_policy_learning_sensitivity_design"),
        "modeling_validation_plan": row_count(RESULT_DIR / "modeling_validation_plan.csv"),
        "falsification_plan": row_count(RESULT_DIR / "falsification_placebo_plan.csv"),
        "policy_learning_plan": row_count(RESULT_DIR / "policy_learning_plan.csv"),
        "mechanism_requirements": row_count(TEMP_DIR / "mechanism_variable_requirements.csv"),
        "mechanism_pathway_protocol": row_count(RESULT_DIR / "mechanism_pathway_protocol.csv"),
        "mechanism_readiness": row_count(RESULT_DIR / "mechanism_readiness_matrix.csv"),
        "mechanism_summary": row_count(RESULT_DIR / "mechanism_analysis_protocol_summary.csv"),
        "mechanism_ready": count_status(RESULT_DIR / "mechanism_readiness_matrix.csv", "readiness_status", "ready_for_mechanism_analysis_design"),
        "mechanism_blocked": sum(1 for row in read_csv_dicts(RESULT_DIR / "mechanism_readiness_matrix.csv") if row.get("readiness_status") != "ready_for_mechanism_analysis_design"),
        "empirical_dashboard": row_count(RESULT_DIR / "empirical_readiness_dashboard.csv"),
        "empirical_no_go": row_count(RESULT_DIR / "empirical_no_go_threshold_status.csv"),
        "empirical_dashboard_summary": row_count(RESULT_DIR / "empirical_readiness_dashboard_summary.csv"),
        "empirical_no_go_pass": count_status(RESULT_DIR / "empirical_no_go_threshold_status.csv", "status", "pass"),
        "empirical_no_go_blocked": sum(1 for row in read_csv_dicts(RESULT_DIR / "empirical_no_go_threshold_status.csv") if row.get("status") != "pass"),
        "first_batch_raw_acquisition_checklist": row_count(TEMP_DIR / "first_batch_raw_acquisition_checklist.csv"),
        "first_batch_raw_file_targets": row_count(TEMP_DIR / "first_batch_raw_file_targets.csv"),
        "first_batch_raw_acquisition_summary": row_count(RESULT_DIR / "first_batch_raw_acquisition_summary.csv"),
        "first_batch_raw_tabular_files": sum(safe_int(row.get("raw_tabular_file_count"), 0) for row in read_csv_dicts(TEMP_DIR / "first_batch_raw_acquisition_checklist.csv")),
        "first_batch_archive_files": sum(safe_int(row.get("archive_file_count"), 0) for row in read_csv_dicts(TEMP_DIR / "first_batch_raw_acquisition_checklist.csv")),
        "first_batch_official_raw_access_probe": len(first_batch_access_probe),
        "first_batch_official_raw_access_summary": row_count(RESULT_DIR / "first_batch_official_raw_access_summary.csv"),
        "first_batch_access_gate_detected": sum(1 for row in first_batch_access_probe if row.get("access_gate_detected") == "1"),
        "first_batch_possible_direct_raw_routes": sum(1 for row in first_batch_access_probe if row.get("direct_raw_route_status") == "possible_direct_raw_links_unverified"),
        "first_batch_manual_action_required": sum(1 for row in first_batch_access_probe if row.get("manual_action_status") != "direct_link_review_required"),
        "first_batch_manual_download_handoff": row_count(TEMP_DIR / "first_batch_manual_download_handoff.csv"),
        "first_batch_manual_download_file_queue": row_count(TEMP_DIR / "first_batch_manual_download_file_queue.csv"),
        "first_batch_manual_download_handoff_summary": row_count(RESULT_DIR / "first_batch_manual_download_handoff_summary.csv"),
        "first_batch_handoff_manual_required": count_status(TEMP_DIR / "first_batch_manual_download_handoff.csv", "handoff_status", "manual_account_terms_download_required"),
        "first_batch_handoff_raw_ready": count_status(TEMP_DIR / "first_batch_manual_download_handoff.csv", "handoff_status", "ready_for_raw_schema_and_value_audit"),
        "first_batch_public_documentation_audit": len(first_batch_public_docs),
        "first_batch_public_documentation_summary": row_count(RESULT_DIR / "first_batch_public_documentation_summary.csv"),
        "first_batch_public_documentation_saved": sum(1 for row in first_batch_public_docs if row.get("coverage_status") == "saved" or row.get("coverage_status", "").startswith("saved_existing_")),
        "first_batch_public_documentation_failed": sum(1 for row in first_batch_public_docs if row.get("coverage_status", "").startswith("failed")),
        "first_batch_public_documentation_complete_datasets": count_status(RESULT_DIR / "first_batch_public_documentation_summary.csv", "metric", "first_batch_documentation_complete_dataset_rows"),
        "first_batch_file_source_traceability": len(first_batch_file_source),
        "first_batch_file_source_traceability_summary": row_count(RESULT_DIR / "first_batch_file_source_traceability_summary.csv"),
        "first_batch_file_source_supported": sum(1 for row in first_batch_file_source if row.get("source_trace_status") == "metadata_file_and_examples_supported"),
        "first_batch_file_source_unsupported": sum(1 for row in first_batch_file_source if row.get("source_trace_status", "").startswith("unsupported_")),
        "first_batch_merge_key_lineage_plan": len(first_batch_merge_key_plan),
        "first_batch_merge_key_candidates": len(first_batch_merge_key_candidates),
        "first_batch_merge_key_lineage_summary": row_count(RESULT_DIR / "first_batch_merge_key_lineage_summary.csv"),
        "first_batch_merge_key_planned": sum(1 for row in first_batch_merge_key_plan if row.get("merge_key_lineage_status") == "metadata_key_lineage_planned_raw_unverified"),
        "first_batch_merge_key_raw_ready": sum(1 for row in first_batch_merge_key_plan if row.get("raw_gate_status") != "blocked_raw_microdata"),
        "first_batch_raw_value_key_audit": len(first_batch_value_key_audit),
        "first_batch_raw_value_key_read_ok": sum(1 for row in first_batch_value_key_audit if row.get("read_status") == "read_ok"),
        "first_batch_raw_merge_key_audit": len(first_batch_raw_key_audit),
        "first_batch_raw_merge_key_read_ok": sum(1 for row in first_batch_raw_key_audit if row.get("read_status") == "read_ok"),
        "first_batch_harmonization_value_audit_auto": len(first_batch_auto_value_audit),
        "first_batch_harmonization_value_audit_auto_ready": sum(1 for row in first_batch_auto_value_audit if row.get("ready_for_recipe") == "1"),
        "first_batch_raw_value_key_summary": row_count(RESULT_DIR / "first_batch_raw_value_key_summary.csv"),
        "alb2002_household_core_candidate": row_count(TEMP_DIR / "alb2002_household_core_candidate.csv"),
        "alb2002_household_core_merge_audit": row_count(TEMP_DIR / "alb2002_household_core_merge_audit.csv"),
        "alb2002_household_core_lineage": row_count(TEMP_DIR / "alb2002_household_core_lineage.csv"),
        "alb2002_household_core_candidate_summary": len(alb2002_core_summary),
        "alb2002_household_core_recipe_ready_rows": safe_int(next((row.get("value", "0") for row in alb2002_core_summary if row.get("metric") == "alb2002_household_core_recipe_ready_rows"), "0")),
        "alb2002_provisional_outcome_feasibility_audit": row_count(TEMP_DIR / "alb2002_provisional_outcome_feasibility_audit.csv"),
        "alb2002_provisional_outcome_feasibility_summary": len(alb2002_outcome_summary),
        "alb2002_provisional_outcome_ready_rows": safe_int(next((row.get("value", "0") for row in alb2002_outcome_summary if row.get("metric") == "alb2002_provisional_outcome_ready_rows"), "0")),
        "alb2002_outcome_semantics_raw_value_audit": row_count(TEMP_DIR / "alb2002_outcome_semantics_raw_value_audit.csv"),
        "alb2002_outcome_semantics_raw_value_summary": len(alb2002_semantics_summary),
        "alb2002_outcome_semantics_outcome_ready_rows": safe_int(next((row.get("value", "0") for row in alb2002_semantics_summary if row.get("metric") == "alb2002_outcome_semantics_outcome_ready_rows"), "0")),
        "alb2002_outcome_semantics_sdg382_ready_rows": safe_int(next((row.get("value", "0") for row in alb2002_semantics_summary if row.get("metric") == "alb2002_outcome_semantics_sdg382_ready_rows"), "0")),
        "alb2002_outcome_semantics_financial_oop_candidate_rows": safe_int(next((row.get("value", "0") for row in alb2002_semantics_summary if row.get("metric") == "alb2002_outcome_semantics_financial_oop_candidate_rows"), "0")),
        "alb2002_outcome_semantics_access_candidate_rows": safe_int(next((row.get("value", "0") for row in alb2002_semantics_summary if row.get("metric") == "alb2002_outcome_semantics_access_candidate_rows"), "0")),
        "alb2002_outcome_semantics_conditional_reason_rows": safe_int(next((row.get("value", "0") for row in alb2002_semantics_summary if row.get("metric") == "alb2002_outcome_semantics_conditional_reason_rows"), "0")),
        "alb2002_health_questionnaire_semantics_audit": row_count(TEMP_DIR / "alb2002_health_questionnaire_semantics_audit.csv"),
        "alb2002_health_questionnaire_semantics_summary": len(alb2002_health_questionnaire_summary),
        "alb2002_health_questionnaire_semantics_rows": safe_int(next((row.get("value", "0") for row in alb2002_health_questionnaire_summary if row.get("metric") == "alb2002_health_questionnaire_semantics_rows"), "0")),
        "alb2002_health_questionnaire_oop_item_rows": safe_int(next((row.get("value", "0") for row in alb2002_health_questionnaire_summary if row.get("metric") == "alb2002_health_questionnaire_oop_item_rows"), "0")),
        "alb2002_health_questionnaire_gift_item_rows": safe_int(next((row.get("value", "0") for row in alb2002_health_questionnaire_summary if row.get("metric") == "alb2002_health_questionnaire_gift_item_rows"), "0")),
        "alb2002_health_questionnaire_new_lek_unit_rows": safe_int(next((row.get("value", "0") for row in alb2002_health_questionnaire_summary if row.get("metric") == "alb2002_health_questionnaire_new_lek_unit_rows"), "0")),
        "alb2002_health_questionnaire_four_week_oop_rows": safe_int(next((row.get("value", "0") for row in alb2002_health_questionnaire_summary if row.get("metric") == "alb2002_health_questionnaire_four_week_oop_rows"), "0")),
        "alb2002_health_questionnaire_twelve_month_oop_rows": safe_int(next((row.get("value", "0") for row in alb2002_health_questionnaire_summary if row.get("metric") == "alb2002_health_questionnaire_twelve_month_oop_rows"), "0")),
        "alb2002_health_questionnaire_payment_positive_when_not_triggered_rows": safe_int(next((row.get("value", "0") for row in alb2002_health_questionnaire_summary if row.get("metric") == "alb2002_health_questionnaire_payment_positive_when_not_triggered_rows"), "0")),
        "alb2002_health_questionnaire_outcome_ready_rows": safe_int(next((row.get("value", "0") for row in alb2002_health_questionnaire_summary if row.get("metric") == "alb2002_health_questionnaire_outcome_ready_rows"), "0")),
        "alb2002_health_questionnaire_sdg382_ready_rows": safe_int(next((row.get("value", "0") for row in alb2002_health_questionnaire_summary if row.get("metric") == "alb2002_health_questionnaire_sdg382_ready_rows"), "0")),
        "alb2002_health_questionnaire_climate_linkage_ready_rows": safe_int(next((row.get("value", "0") for row in alb2002_health_questionnaire_summary if row.get("metric") == "alb2002_health_questionnaire_climate_linkage_ready_rows"), "0")),
        "alb2002_health_questionnaire_current_decision": next((row.get("value", "") for row in alb2002_health_questionnaire_summary if row.get("metric") == "alb2002_health_questionnaire_current_decision"), ""),
        "alb2002_oop_aggregation_policy_audit": row_count(TEMP_DIR / "alb2002_oop_aggregation_policy_audit.csv"),
        "alb2002_oop_aggregation_policy_summary": len(alb2002_oop_policy_summary),
        "alb2002_oop_aggregation_policy_rows": safe_int(next((row.get("value", "0") for row in alb2002_oop_policy_summary if row.get("metric") == "alb2002_oop_aggregation_policy_rows"), "0")),
        "alb2002_oop_aggregation_policy_core_4w_match_rows": safe_int(next((row.get("value", "0") for row in alb2002_oop_policy_summary if row.get("metric") == "alb2002_oop_aggregation_policy_core_4w_match_rows"), "0")),
        "alb2002_oop_aggregation_policy_core_12m_match_rows": safe_int(next((row.get("value", "0") for row in alb2002_oop_policy_summary if row.get("metric") == "alb2002_oop_aggregation_policy_core_12m_match_rows"), "0")),
        "alb2002_oop_aggregation_policy_outcome_ready_rows": safe_int(next((row.get("value", "0") for row in alb2002_oop_policy_summary if row.get("metric") == "alb2002_oop_aggregation_policy_outcome_ready_rows"), "0")),
        "alb2002_oop_aggregation_policy_recipe_ready_rows": safe_int(next((row.get("value", "0") for row in alb2002_oop_policy_summary if row.get("metric") == "alb2002_oop_aggregation_policy_recipe_ready_rows"), "0")),
        "alb2002_oop_aggregation_policy_sdg382_ready_rows": safe_int(next((row.get("value", "0") for row in alb2002_oop_policy_summary if row.get("metric") == "alb2002_oop_aggregation_policy_sdg382_ready_rows"), "0")),
        "alb2002_oop_aggregation_policy_climate_linkage_ready_rows": safe_int(next((row.get("value", "0") for row in alb2002_oop_policy_summary if row.get("metric") == "alb2002_oop_aggregation_policy_climate_linkage_ready_rows"), "0")),
        "alb2002_oop_aggregation_policy_current_decision": next((row.get("value", "") for row in alb2002_oop_policy_summary if row.get("metric") == "alb2002_oop_aggregation_policy_current_decision"), ""),
        "alb2002_skip_missing_semantics_audit": row_count(TEMP_DIR / "alb2002_skip_missing_semantics_audit.csv"),
        "alb2002_skip_missing_semantics_summary": len(alb2002_skip_missing_summary),
        "alb2002_skip_missing_semantics_rows": safe_int(next((row.get("value", "0") for row in alb2002_skip_missing_summary if row.get("metric") == "alb2002_skip_missing_semantics_rows"), "0")),
        "alb2002_skip_missing_payment_block_rows": safe_int(next((row.get("value", "0") for row in alb2002_skip_missing_summary if row.get("metric") == "alb2002_skip_missing_payment_block_rows"), "0")),
        "alb2002_skip_missing_access_condition_rows": safe_int(next((row.get("value", "0") for row in alb2002_skip_missing_summary if row.get("metric") == "alb2002_skip_missing_access_condition_rows"), "0")),
        "alb2002_skip_missing_payment_positive_when_not_triggered_rows": safe_int(next((row.get("value", "0") for row in alb2002_skip_missing_summary if row.get("metric") == "alb2002_skip_missing_payment_positive_when_not_triggered_rows"), "0")),
        "alb2002_skip_missing_payment_zero_cells_when_not_triggered": safe_int(next((row.get("value", "0") for row in alb2002_skip_missing_summary if row.get("metric") == "alb2002_skip_missing_payment_zero_cells_when_not_triggered"), "0")),
        "alb2002_skip_missing_payment_positive_cells_when_not_triggered": safe_int(next((row.get("value", "0") for row in alb2002_skip_missing_summary if row.get("metric") == "alb2002_skip_missing_payment_positive_cells_when_not_triggered"), "0")),
        "alb2002_skip_missing_outcome_ready_rows": safe_int(next((row.get("value", "0") for row in alb2002_skip_missing_summary if row.get("metric") == "alb2002_skip_missing_outcome_ready_rows"), "0")),
        "alb2002_skip_missing_recipe_ready_rows": safe_int(next((row.get("value", "0") for row in alb2002_skip_missing_summary if row.get("metric") == "alb2002_skip_missing_recipe_ready_rows"), "0")),
        "alb2002_skip_missing_sdg382_ready_rows": safe_int(next((row.get("value", "0") for row in alb2002_skip_missing_summary if row.get("metric") == "alb2002_skip_missing_sdg382_ready_rows"), "0")),
        "alb2002_skip_missing_climate_linkage_ready_rows": safe_int(next((row.get("value", "0") for row in alb2002_skip_missing_summary if row.get("metric") == "alb2002_skip_missing_climate_linkage_ready_rows"), "0")),
        "alb2002_skip_missing_current_decision": next((row.get("value", "") for row in alb2002_skip_missing_summary if row.get("metric") == "alb2002_skip_missing_current_decision"), ""),
        "alb2002_oop_skip_value_decision_audit": row_count(TEMP_DIR / "alb2002_oop_skip_value_decision_audit.csv"),
        "alb2002_oop_skip_value_decision_summary": len(alb2002_oop_skip_value_summary),
        "alb2002_oop_skip_value_decision_rows": safe_int(next((row.get("value", "0") for row in alb2002_oop_skip_value_summary if row.get("metric") == "alb2002_oop_skip_value_decision_rows"), "0")),
        "alb2002_oop_skip_value_payment_block_rows": safe_int(next((row.get("value", "0") for row in alb2002_oop_skip_value_summary if row.get("metric") == "alb2002_oop_skip_value_payment_block_rows"), "0")),
        "alb2002_oop_skip_value_access_condition_block_rows": safe_int(next((row.get("value", "0") for row in alb2002_oop_skip_value_summary if row.get("metric") == "alb2002_oop_skip_value_access_condition_block_rows"), "0")),
        "alb2002_oop_skip_value_payment_nonmissing_skipped_rows": safe_int(next((row.get("value", "0") for row in alb2002_oop_skip_value_summary if row.get("metric") == "alb2002_oop_skip_value_payment_nonmissing_skipped_rows"), "0")),
        "alb2002_oop_skip_value_payment_nonmissing_skipped_cells": safe_int(next((row.get("value", "0") for row in alb2002_oop_skip_value_summary if row.get("metric") == "alb2002_oop_skip_value_payment_nonmissing_skipped_cells"), "0")),
        "alb2002_oop_skip_value_payment_zero_skipped_cells": safe_int(next((row.get("value", "0") for row in alb2002_oop_skip_value_summary if row.get("metric") == "alb2002_oop_skip_value_payment_zero_skipped_cells"), "0")),
        "alb2002_oop_skip_value_payment_positive_skipped_rows": safe_int(next((row.get("value", "0") for row in alb2002_oop_skip_value_summary if row.get("metric") == "alb2002_oop_skip_value_payment_positive_skipped_rows"), "0")),
        "alb2002_oop_skip_value_payment_positive_skipped_cells": safe_int(next((row.get("value", "0") for row in alb2002_oop_skip_value_summary if row.get("metric") == "alb2002_oop_skip_value_payment_positive_skipped_cells"), "0")),
        "alb2002_oop_skip_value_zero_skip_policy_ready_rows": safe_int(next((row.get("value", "0") for row in alb2002_oop_skip_value_summary if row.get("metric") == "alb2002_oop_skip_value_zero_skip_policy_ready_rows"), "0")),
        "alb2002_oop_skip_value_oop_recall_scope_ready_rows": safe_int(next((row.get("value", "0") for row in alb2002_oop_skip_value_summary if row.get("metric") == "alb2002_oop_skip_value_oop_recall_scope_ready_rows"), "0")),
        "alb2002_oop_skip_value_oop_inclusion_scope_ready_rows": safe_int(next((row.get("value", "0") for row in alb2002_oop_skip_value_summary if row.get("metric") == "alb2002_oop_skip_value_oop_inclusion_scope_ready_rows"), "0")),
        "alb2002_oop_skip_value_recipe_ready_rows": safe_int(next((row.get("value", "0") for row in alb2002_oop_skip_value_summary if row.get("metric") == "alb2002_oop_skip_value_recipe_ready_rows"), "0")),
        "alb2002_oop_skip_value_outcome_ready_rows": safe_int(next((row.get("value", "0") for row in alb2002_oop_skip_value_summary if row.get("metric") == "alb2002_oop_skip_value_outcome_ready_rows"), "0")),
        "alb2002_oop_skip_value_sdg382_ready_rows": safe_int(next((row.get("value", "0") for row in alb2002_oop_skip_value_summary if row.get("metric") == "alb2002_oop_skip_value_sdg382_ready_rows"), "0")),
        "alb2002_oop_skip_value_climate_linkage_ready_rows": safe_int(next((row.get("value", "0") for row in alb2002_oop_skip_value_summary if row.get("metric") == "alb2002_oop_skip_value_climate_linkage_ready_rows"), "0")),
        "alb2002_oop_skip_value_current_decision": next((row.get("value", "") for row in alb2002_oop_skip_value_summary if row.get("metric") == "alb2002_oop_skip_value_current_decision"), ""),
        "alb2002_access_need_denominator_policy_audit": row_count(TEMP_DIR / "alb2002_access_need_denominator_policy_audit.csv"),
        "alb2002_access_need_denominator_policy_summary": len(alb2002_access_need_summary),
        "alb2002_access_need_denominator_policy_rows": safe_int(next((row.get("value", "0") for row in alb2002_access_need_summary if row.get("metric") == "alb2002_access_need_denominator_policy_rows"), "0")),
        "alb2002_access_need_household_rows": safe_int(next((row.get("value", "0") for row in alb2002_access_need_summary if row.get("metric") == "alb2002_access_need_household_rows"), "0")),
        "alb2002_access_need_person_need_household_rows": safe_int(next((row.get("value", "0") for row in alb2002_access_need_summary if row.get("metric") == "alb2002_access_need_person_need_household_rows"), "0")),
        "alb2002_access_need_q01_need_rows": safe_int(next((row.get("value", "0") for row in alb2002_access_need_summary if row.get("metric") == "alb2002_access_need_q01_need_rows"), "0")),
        "alb2002_access_need_delayed_help_rows": safe_int(next((row.get("value", "0") for row in alb2002_access_need_summary if row.get("metric") == "alb2002_access_need_delayed_help_rows"), "0")),
        "alb2002_access_need_referral_not_gone_rows": safe_int(next((row.get("value", "0") for row in alb2002_access_need_summary if row.get("metric") == "alb2002_access_need_referral_not_gone_rows"), "0")),
        "alb2002_access_need_refused_service_rows": safe_int(next((row.get("value", "0") for row in alb2002_access_need_summary if row.get("metric") == "alb2002_access_need_refused_service_rows"), "0")),
        "alb2002_access_need_composite_any_access_barrier_rows": safe_int(next((row.get("value", "0") for row in alb2002_access_need_summary if row.get("metric") == "alb2002_access_need_composite_any_access_barrier_rows"), "0")),
        "alb2002_access_need_low_event_rate_rows": safe_int(next((row.get("value", "0") for row in alb2002_access_need_summary if row.get("metric") == "alb2002_access_need_low_event_rate_rows"), "0")),
        "alb2002_access_need_outcome_ready_rows": safe_int(next((row.get("value", "0") for row in alb2002_access_need_summary if row.get("metric") == "alb2002_access_need_outcome_ready_rows"), "0")),
        "alb2002_access_need_recipe_ready_rows": safe_int(next((row.get("value", "0") for row in alb2002_access_need_summary if row.get("metric") == "alb2002_access_need_recipe_ready_rows"), "0")),
        "alb2002_access_need_sdg382_ready_rows": safe_int(next((row.get("value", "0") for row in alb2002_access_need_summary if row.get("metric") == "alb2002_access_need_sdg382_ready_rows"), "0")),
        "alb2002_access_need_climate_linkage_ready_rows": safe_int(next((row.get("value", "0") for row in alb2002_access_need_summary if row.get("metric") == "alb2002_access_need_climate_linkage_ready_rows"), "0")),
        "alb2002_access_need_current_decision": next((row.get("value", "") for row in alb2002_access_need_summary if row.get("metric") == "alb2002_access_need_current_decision"), ""),
        "alb2002_consumption_sdg_denominator_policy_audit": row_count(TEMP_DIR / "alb2002_consumption_sdg_denominator_policy_audit.csv"),
        "alb2002_consumption_sdg_denominator_policy_summary": len(alb2002_consumption_sdg_summary),
        "alb2002_consumption_sdg_denominator_policy_rows": safe_int(next((row.get("value", "0") for row in alb2002_consumption_sdg_summary if row.get("metric") == "alb2002_consumption_sdg_denominator_policy_rows"), "0")),
        "alb2002_consumption_sdg_household_rows": safe_int(next((row.get("value", "0") for row in alb2002_consumption_sdg_summary if row.get("metric") == "alb2002_consumption_sdg_household_rows"), "0")),
        "alb2002_consumption_sdg_positive_total_consumption_rows": safe_int(next((row.get("value", "0") for row in alb2002_consumption_sdg_summary if row.get("metric") == "alb2002_consumption_sdg_positive_total_consumption_rows"), "0")),
        "alb2002_consumption_sdg_positive_household_weight_rows": safe_int(next((row.get("value", "0") for row in alb2002_consumption_sdg_summary if row.get("metric") == "alb2002_consumption_sdg_positive_household_weight_rows"), "0")),
        "alb2002_consumption_sdg_positive_household_size_rows": safe_int(next((row.get("value", "0") for row in alb2002_consumption_sdg_summary if row.get("metric") == "alb2002_consumption_sdg_positive_household_size_rows"), "0")),
        "alb2002_consumption_sdg_spl_ready_rows": safe_int(next((row.get("value", "0") for row in alb2002_consumption_sdg_summary if row.get("metric") == "alb2002_consumption_sdg_spl_ready_rows"), "0")),
        "alb2002_consumption_sdg_ppp_cpi_ready_rows": safe_int(next((row.get("value", "0") for row in alb2002_consumption_sdg_summary if row.get("metric") == "alb2002_consumption_sdg_ppp_cpi_ready_rows"), "0")),
        "alb2002_consumption_sdg_discretionary_budget_ready_rows": safe_int(next((row.get("value", "0") for row in alb2002_consumption_sdg_summary if row.get("metric") == "alb2002_consumption_sdg_discretionary_budget_ready_rows"), "0")),
        "alb2002_consumption_sdg_che_denominator_ready_rows": safe_int(next((row.get("value", "0") for row in alb2002_consumption_sdg_summary if row.get("metric") == "alb2002_consumption_sdg_che_denominator_ready_rows"), "0")),
        "alb2002_consumption_sdg_recipe_ready_rows": safe_int(next((row.get("value", "0") for row in alb2002_consumption_sdg_summary if row.get("metric") == "alb2002_consumption_sdg_recipe_ready_rows"), "0")),
        "alb2002_consumption_sdg_outcome_ready_rows": safe_int(next((row.get("value", "0") for row in alb2002_consumption_sdg_summary if row.get("metric") == "alb2002_consumption_sdg_outcome_ready_rows"), "0")),
        "alb2002_consumption_sdg_sdg382_ready_rows": safe_int(next((row.get("value", "0") for row in alb2002_consumption_sdg_summary if row.get("metric") == "alb2002_consumption_sdg_sdg382_ready_rows"), "0")),
        "alb2002_consumption_sdg_climate_linkage_ready_rows": safe_int(next((row.get("value", "0") for row in alb2002_consumption_sdg_summary if row.get("metric") == "alb2002_consumption_sdg_climate_linkage_ready_rows"), "0")),
        "alb2002_consumption_sdg_current_decision": next((row.get("value", "") for row in alb2002_consumption_sdg_summary if row.get("metric") == "alb2002_consumption_sdg_current_decision"), ""),
        "alb2002_consumption_construction_source_audit": row_count(TEMP_DIR / "alb2002_consumption_construction_source_audit.csv"),
        "alb2002_consumption_construction_source_summary": len(alb2002_consumption_construction_summary),
        "alb2002_consumption_construction_source_audit_rows": safe_int(next((row.get("value", "0") for row in alb2002_consumption_construction_summary if row.get("metric") == "alb2002_consumption_construction_source_audit_rows"), "0")),
        "alb2002_consumption_construction_public_pdf_present": safe_int(next((row.get("value", "0") for row in alb2002_consumption_construction_summary if row.get("metric") == "alb2002_consumption_construction_public_pdf_present"), "0")),
        "alb2002_consumption_construction_program_zip_present": safe_int(next((row.get("value", "0") for row in alb2002_consumption_construction_summary if row.get("metric") == "alb2002_consumption_construction_program_zip_present"), "0")),
        "alb2002_consumption_construction_do_file_rows": safe_int(next((row.get("value", "0") for row in alb2002_consumption_construction_summary if row.get("metric") == "alb2002_consumption_construction_do_file_rows"), "0")),
        "alb2002_consumption_construction_totcons_do_present": safe_int(next((row.get("value", "0") for row in alb2002_consumption_construction_summary if row.get("metric") == "alb2002_consumption_construction_totcons_do_present"), "0")),
        "alb2002_consumption_construction_poverty_do_present": safe_int(next((row.get("value", "0") for row in alb2002_consumption_construction_summary if row.get("metric") == "alb2002_consumption_construction_poverty_do_present"), "0")),
        "alb2002_consumption_construction_metadata_json_present": safe_int(next((row.get("value", "0") for row in alb2002_consumption_construction_summary if row.get("metric") == "alb2002_consumption_construction_metadata_json_present"), "0")),
        "alb2002_consumption_construction_documentation_ready_rows": safe_int(next((row.get("value", "0") for row in alb2002_consumption_construction_summary if row.get("metric") == "alb2002_consumption_construction_documentation_ready_rows"), "0")),
        "alb2002_consumption_construction_released_variable_mapping_ready_rows": safe_int(next((row.get("value", "0") for row in alb2002_consumption_construction_summary if row.get("metric") == "alb2002_consumption_construction_released_variable_mapping_ready_rows"), "0")),
        "alb2002_consumption_construction_denominator_variant_ready_rows": safe_int(next((row.get("value", "0") for row in alb2002_consumption_construction_summary if row.get("metric") == "alb2002_consumption_construction_denominator_variant_ready_rows"), "0")),
        "alb2002_consumption_construction_recipe_ready_rows": safe_int(next((row.get("value", "0") for row in alb2002_consumption_construction_summary if row.get("metric") == "alb2002_consumption_construction_recipe_ready_rows"), "0")),
        "alb2002_consumption_construction_outcome_ready_rows": safe_int(next((row.get("value", "0") for row in alb2002_consumption_construction_summary if row.get("metric") == "alb2002_consumption_construction_outcome_ready_rows"), "0")),
        "alb2002_consumption_construction_sdg382_ready_rows": safe_int(next((row.get("value", "0") for row in alb2002_consumption_construction_summary if row.get("metric") == "alb2002_consumption_construction_sdg382_ready_rows"), "0")),
        "alb2002_consumption_construction_climate_linkage_ready_rows": safe_int(next((row.get("value", "0") for row in alb2002_consumption_construction_summary if row.get("metric") == "alb2002_consumption_construction_climate_linkage_ready_rows"), "0")),
        "alb2002_consumption_construction_current_decision": next((row.get("value", "") for row in alb2002_consumption_construction_summary if row.get("metric") == "alb2002_consumption_construction_current_decision"), ""),
        "alb2002_consumption_aggregate_crosswalk_audit": row_count(TEMP_DIR / "alb2002_consumption_aggregate_metadata_crosswalk_audit.csv"),
        "alb2002_consumption_aggregate_crosswalk_summary": len(alb2002_consumption_aggregate_summary),
        "alb2002_consumption_aggregate_crosswalk_rows": safe_int(next((row.get("value", "0") for row in alb2002_consumption_aggregate_summary if row.get("metric") == "alb2002_consumption_aggregate_crosswalk_rows"), "0")),
        "alb2002_consumption_aggregate_crosswalk_local_poverty_rows": safe_int(next((row.get("value", "0") for row in alb2002_consumption_aggregate_summary if row.get("metric") == "alb2002_consumption_aggregate_crosswalk_local_poverty_rows"), "0")),
        "alb2002_consumption_aggregate_crosswalk_metadata_catalog_rows": safe_int(next((row.get("value", "0") for row in alb2002_consumption_aggregate_summary if row.get("metric") == "alb2002_consumption_aggregate_crosswalk_metadata_catalog_rows"), "0")),
        "alb2002_consumption_aggregate_crosswalk_raw_totcons_positive_rows": safe_int(next((row.get("value", "0") for row in alb2002_consumption_aggregate_summary if row.get("metric") == "alb2002_consumption_aggregate_crosswalk_raw_totcons_positive_rows"), "0")),
        "alb2002_consumption_aggregate_crosswalk_candidate_totcons_match_rows": safe_int(next((row.get("value", "0") for row in alb2002_consumption_aggregate_summary if row.get("metric") == "alb2002_consumption_aggregate_crosswalk_candidate_totcons_match_rows"), "0")),
        "alb2002_consumption_aggregate_crosswalk_questionnaire_aggregate_formula_hits": safe_int(next((row.get("value", "0") for row in alb2002_consumption_aggregate_summary if row.get("metric") == "alb2002_consumption_aggregate_crosswalk_questionnaire_aggregate_formula_hits"), "0")),
        "alb2002_consumption_aggregate_crosswalk_construction_source_rows": safe_int(next((row.get("value", "0") for row in alb2002_consumption_aggregate_summary if row.get("metric") == "alb2002_consumption_aggregate_crosswalk_construction_source_rows"), "0")),
        "alb2002_consumption_aggregate_crosswalk_construction_do_file_rows": safe_int(next((row.get("value", "0") for row in alb2002_consumption_aggregate_summary if row.get("metric") == "alb2002_consumption_aggregate_crosswalk_construction_do_file_rows"), "0")),
        "alb2002_consumption_aggregate_crosswalk_metadata_unit_period_ready_rows": safe_int(next((row.get("value", "0") for row in alb2002_consumption_aggregate_summary if row.get("metric") == "alb2002_consumption_aggregate_crosswalk_metadata_unit_period_ready_rows"), "0")),
        "alb2002_consumption_aggregate_crosswalk_official_documentation_ready_rows": safe_int(next((row.get("value", "0") for row in alb2002_consumption_aggregate_summary if row.get("metric") == "alb2002_consumption_aggregate_crosswalk_official_documentation_ready_rows"), "0")),
        "alb2002_consumption_aggregate_crosswalk_released_variable_mapping_ready_rows": safe_int(next((row.get("value", "0") for row in alb2002_consumption_aggregate_summary if row.get("metric") == "alb2002_consumption_aggregate_crosswalk_released_variable_mapping_ready_rows"), "0")),
        "alb2002_consumption_aggregate_crosswalk_denominator_variant_ready_rows": safe_int(next((row.get("value", "0") for row in alb2002_consumption_aggregate_summary if row.get("metric") == "alb2002_consumption_aggregate_crosswalk_denominator_variant_ready_rows"), "0")),
        "alb2002_consumption_aggregate_crosswalk_recipe_ready_rows": safe_int(next((row.get("value", "0") for row in alb2002_consumption_aggregate_summary if row.get("metric") == "alb2002_consumption_aggregate_crosswalk_recipe_ready_rows"), "0")),
        "alb2002_consumption_aggregate_crosswalk_outcome_ready_rows": safe_int(next((row.get("value", "0") for row in alb2002_consumption_aggregate_summary if row.get("metric") == "alb2002_consumption_aggregate_crosswalk_outcome_ready_rows"), "0")),
        "alb2002_consumption_aggregate_crosswalk_sdg382_ready_rows": safe_int(next((row.get("value", "0") for row in alb2002_consumption_aggregate_summary if row.get("metric") == "alb2002_consumption_aggregate_crosswalk_sdg382_ready_rows"), "0")),
        "alb2002_consumption_aggregate_crosswalk_climate_linkage_ready_rows": safe_int(next((row.get("value", "0") for row in alb2002_consumption_aggregate_summary if row.get("metric") == "alb2002_consumption_aggregate_crosswalk_climate_linkage_ready_rows"), "0")),
        "alb2002_consumption_aggregate_crosswalk_current_decision": next((row.get("value", "") for row in alb2002_consumption_aggregate_summary if row.get("metric") == "alb2002_consumption_aggregate_crosswalk_current_decision"), ""),
        "alb2002_period_aligned_che_audit": row_count(TEMP_DIR / "alb2002_period_aligned_che_policy_audit.csv"),
        "alb2002_period_aligned_che_summary": len(alb2002_period_aligned_che_summary),
        "alb2002_period_aligned_che_policy_rows": safe_int(next((row.get("value", "0") for row in alb2002_period_aligned_che_summary if row.get("metric") == "alb2002_period_aligned_che_policy_rows"), "0")),
        "alb2002_period_aligned_che_household_rows": safe_int(next((row.get("value", "0") for row in alb2002_period_aligned_che_summary if row.get("metric") == "alb2002_period_aligned_che_household_rows"), "0")),
        "alb2002_period_aligned_che_denominator_rows": safe_int(next((row.get("value", "0") for row in alb2002_period_aligned_che_summary if row.get("metric") == "alb2002_period_aligned_che_denominator_rows"), "0")),
        "alb2002_period_aligned_che_period_alignment_ready_rows": safe_int(next((row.get("value", "0") for row in alb2002_period_aligned_che_summary if row.get("metric") == "alb2002_period_aligned_che_period_alignment_ready_rows"), "0")),
        "alb2002_period_aligned_che_combined_che10_rate": next((row.get("value", "") for row in alb2002_period_aligned_che_summary if row.get("metric") == "alb2002_period_aligned_che_combined_che10_rate"), ""),
        "alb2002_period_aligned_che_combined_che25_rate": next((row.get("value", "") for row in alb2002_period_aligned_che_summary if row.get("metric") == "alb2002_period_aligned_che_combined_che25_rate"), ""),
        "alb2002_period_aligned_che_outcome_ready_rows": safe_int(next((row.get("value", "0") for row in alb2002_period_aligned_che_summary if row.get("metric") == "alb2002_period_aligned_che_outcome_ready_rows"), "0")),
        "alb2002_period_aligned_che_recipe_ready_rows": safe_int(next((row.get("value", "0") for row in alb2002_period_aligned_che_summary if row.get("metric") == "alb2002_period_aligned_che_recipe_ready_rows"), "0")),
        "alb2002_period_aligned_che_sdg382_ready_rows": safe_int(next((row.get("value", "0") for row in alb2002_period_aligned_che_summary if row.get("metric") == "alb2002_period_aligned_che_sdg382_ready_rows"), "0")),
        "alb2002_period_aligned_che_climate_linkage_ready_rows": safe_int(next((row.get("value", "0") for row in alb2002_period_aligned_che_summary if row.get("metric") == "alb2002_period_aligned_che_climate_linkage_ready_rows"), "0")),
        "alb2002_period_aligned_che_current_decision": next((row.get("value", "") for row in alb2002_period_aligned_che_summary if row.get("metric") == "alb2002_period_aligned_che_current_decision"), ""),
        "alb2002_che_candidate_household_outcomes": row_count(TEMP_DIR / "alb2002_che_candidate_household_outcomes.csv"),
        "alb2002_che_candidate_outcome_lineage": row_count(TEMP_DIR / "alb2002_che_candidate_outcome_lineage.csv"),
        "alb2002_che_candidate_outcome_audit": row_count(RESULT_DIR / "alb2002_che_candidate_outcome_audit.csv"),
        "alb2002_che_candidate_outcome_summary": len(alb2002_che_candidate_summary),
        "alb2002_che_candidate_household_rows": safe_int(next((row.get("value", "0") for row in alb2002_che_candidate_summary if row.get("metric") == "alb2002_che_candidate_household_rows"), "0")),
        "alb2002_che_candidate_denominator_rows": safe_int(next((row.get("value", "0") for row in alb2002_che_candidate_summary if row.get("metric") == "alb2002_che_candidate_denominator_rows"), "0")),
        "alb2002_che_candidate_che10_rows": safe_int(next((row.get("value", "0") for row in alb2002_che_candidate_summary if row.get("metric") == "alb2002_che_candidate_che10_rows"), "0")),
        "alb2002_che_candidate_che10_rate": next((row.get("value", "") for row in alb2002_che_candidate_summary if row.get("metric") == "alb2002_che_candidate_che10_rate"), ""),
        "alb2002_che_candidate_che25_rows": safe_int(next((row.get("value", "0") for row in alb2002_che_candidate_summary if row.get("metric") == "alb2002_che_candidate_che25_rows"), "0")),
        "alb2002_che_candidate_che25_rate": next((row.get("value", "") for row in alb2002_che_candidate_summary if row.get("metric") == "alb2002_che_candidate_che25_rate"), ""),
        "alb2002_che_candidate_outcome_promotion_ready_rows": safe_int(next((row.get("value", "0") for row in alb2002_che_candidate_summary if row.get("metric") == "alb2002_che_candidate_outcome_promotion_ready_rows"), "0")),
        "alb2002_che_candidate_climate_linkage_ready_rows": safe_int(next((row.get("value", "0") for row in alb2002_che_candidate_summary if row.get("metric") == "alb2002_che_candidate_climate_linkage_ready_rows"), "0")),
        "alb2002_che_candidate_current_decision": next((row.get("value", "") for row in alb2002_che_candidate_summary if row.get("metric") == "alb2002_che_candidate_current_decision"), ""),
        "alb2002_access_candidate_household_outcomes": row_count(TEMP_DIR / "alb2002_access_candidate_household_outcomes.csv"),
        "alb2002_access_candidate_outcome_lineage": row_count(TEMP_DIR / "alb2002_access_candidate_outcome_lineage.csv"),
        "alb2002_access_candidate_outcome_audit": row_count(RESULT_DIR / "alb2002_access_candidate_outcome_audit.csv"),
        "alb2002_access_candidate_outcome_summary": len(alb2002_access_candidate_summary),
        "alb2002_access_candidate_household_rows": safe_int(next((row.get("value", "0") for row in alb2002_access_candidate_summary if row.get("metric") == "alb2002_access_candidate_household_rows"), "0")),
        "alb2002_access_candidate_q01_need_rows": safe_int(next((row.get("value", "0") for row in alb2002_access_candidate_summary if row.get("metric") == "alb2002_access_candidate_q01_need_rows"), "0")),
        "alb2002_access_candidate_person_need_rows": safe_int(next((row.get("value", "0") for row in alb2002_access_candidate_summary if row.get("metric") == "alb2002_access_candidate_person_need_rows"), "0")),
        "alb2002_access_candidate_q01_cost_difficulty_rows": safe_int(next((row.get("value", "0") for row in alb2002_access_candidate_summary if row.get("metric") == "alb2002_access_candidate_q01_cost_difficulty_rows"), "0")),
        "alb2002_access_candidate_composite_cost_rows": safe_int(next((row.get("value", "0") for row in alb2002_access_candidate_summary if row.get("metric") == "alb2002_access_candidate_composite_cost_rows"), "0")),
        "alb2002_access_candidate_composite_any_rows": safe_int(next((row.get("value", "0") for row in alb2002_access_candidate_summary if row.get("metric") == "alb2002_access_candidate_composite_any_rows"), "0")),
        "alb2002_access_candidate_outcome_promotion_ready_rows": safe_int(next((row.get("value", "0") for row in alb2002_access_candidate_summary if row.get("metric") == "alb2002_access_candidate_outcome_promotion_ready_rows"), "0")),
        "alb2002_access_candidate_recipe_ready_rows": safe_int(next((row.get("value", "0") for row in alb2002_access_candidate_summary if row.get("metric") == "alb2002_access_candidate_recipe_ready_rows"), "0")),
        "alb2002_access_candidate_climate_linkage_ready_rows": safe_int(next((row.get("value", "0") for row in alb2002_access_candidate_summary if row.get("metric") == "alb2002_access_candidate_climate_linkage_ready_rows"), "0")),
        "alb2002_access_candidate_current_decision": next((row.get("value", "") for row in alb2002_access_candidate_summary if row.get("metric") == "alb2002_access_candidate_current_decision"), ""),
        "alb2002_uhc_composite_candidate_outcomes": row_count(TEMP_DIR / "alb2002_uhc_composite_candidate_outcomes.csv"),
        "alb2002_uhc_composite_candidate_lineage": row_count(TEMP_DIR / "alb2002_uhc_composite_candidate_lineage.csv"),
        "alb2002_uhc_composite_candidate_audit": row_count(RESULT_DIR / "alb2002_uhc_composite_candidate_audit.csv"),
        "alb2002_uhc_composite_candidate_summary": len(alb2002_uhc_composite_summary),
        "alb2002_uhc_composite_candidate_household_rows": safe_int(next((row.get("value", "0") for row in alb2002_uhc_composite_summary if row.get("metric") == "alb2002_uhc_composite_candidate_household_rows"), "0")),
        "alb2002_uhc_composite_candidate_che10_or_access_rows": safe_int(next((row.get("value", "0") for row in alb2002_uhc_composite_summary if row.get("metric") == "alb2002_uhc_composite_candidate_che10_or_access_rows"), "0")),
        "alb2002_uhc_composite_candidate_che25_or_access_rows": safe_int(next((row.get("value", "0") for row in alb2002_uhc_composite_summary if row.get("metric") == "alb2002_uhc_composite_candidate_che25_or_access_rows"), "0")),
        "alb2002_uhc_composite_candidate_both_che10_access_rows": safe_int(next((row.get("value", "0") for row in alb2002_uhc_composite_summary if row.get("metric") == "alb2002_uhc_composite_candidate_both_che10_access_rows"), "0")),
        "alb2002_uhc_composite_candidate_coping_rows": safe_int(next((row.get("value", "0") for row in alb2002_uhc_composite_summary if row.get("metric") == "alb2002_uhc_composite_candidate_coping_rows"), "0")),
        "alb2002_uhc_composite_candidate_outcome_promotion_ready_rows": safe_int(next((row.get("value", "0") for row in alb2002_uhc_composite_summary if row.get("metric") == "alb2002_uhc_composite_candidate_outcome_promotion_ready_rows"), "0")),
        "alb2002_uhc_composite_candidate_recipe_ready_rows": safe_int(next((row.get("value", "0") for row in alb2002_uhc_composite_summary if row.get("metric") == "alb2002_uhc_composite_candidate_recipe_ready_rows"), "0")),
        "alb2002_uhc_composite_candidate_climate_linkage_ready_rows": safe_int(next((row.get("value", "0") for row in alb2002_uhc_composite_summary if row.get("metric") == "alb2002_uhc_composite_candidate_climate_linkage_ready_rows"), "0")),
        "alb2002_uhc_composite_candidate_current_decision": next((row.get("value", "") for row in alb2002_uhc_composite_summary if row.get("metric") == "alb2002_uhc_composite_candidate_current_decision"), ""),
        "alb2002_analysis_candidate_dataset": row_count(TEMP_DIR / "alb2002_analysis_candidate_dataset.csv"),
        "alb2002_analysis_candidate_lineage": row_count(TEMP_DIR / "alb2002_analysis_candidate_lineage.csv"),
        "alb2002_analysis_candidate_readiness_audit": row_count(RESULT_DIR / "alb2002_analysis_candidate_readiness_audit.csv"),
        "alb2002_analysis_candidate_readiness_summary": len(alb2002_analysis_candidate_summary),
        "alb2002_analysis_candidate_rows": safe_int(next((row.get("value", "0") for row in alb2002_analysis_candidate_summary if row.get("metric") == "alb2002_analysis_candidate_rows"), "0")),
        "alb2002_analysis_candidate_columns": safe_int(next((row.get("value", "0") for row in alb2002_analysis_candidate_summary if row.get("metric") == "alb2002_analysis_candidate_columns"), "0")),
        "alb2002_analysis_candidate_complete_candidate_gates": safe_int(next((row.get("value", "0") for row in alb2002_analysis_candidate_summary if row.get("metric") == "alb2002_analysis_candidate_complete_candidate_gates"), "0")),
        "alb2002_analysis_candidate_missing_gates": safe_int(next((row.get("value", "0") for row in alb2002_analysis_candidate_summary if row.get("metric") == "alb2002_analysis_candidate_missing_gates"), "0")),
        "alb2002_analysis_candidate_blocked_promotion_gates": safe_int(next((row.get("value", "0") for row in alb2002_analysis_candidate_summary if row.get("metric") == "alb2002_analysis_candidate_blocked_promotion_gates"), "0")),
        "alb2002_analysis_candidate_harmonized_ready_rows": safe_int(next((row.get("value", "0") for row in alb2002_analysis_candidate_summary if row.get("metric") == "alb2002_analysis_candidate_harmonized_ready_rows"), "0")),
        "alb2002_analysis_candidate_outcome_promotion_ready_rows": safe_int(next((row.get("value", "0") for row in alb2002_analysis_candidate_summary if row.get("metric") == "alb2002_analysis_candidate_outcome_promotion_ready_rows"), "0")),
        "alb2002_analysis_candidate_climate_linkage_ready_rows": safe_int(next((row.get("value", "0") for row in alb2002_analysis_candidate_summary if row.get("metric") == "alb2002_analysis_candidate_climate_linkage_ready_rows"), "0")),
        "alb2002_analysis_candidate_data_write_ready_rows": safe_int(next((row.get("value", "0") for row in alb2002_analysis_candidate_summary if row.get("metric") == "alb2002_analysis_candidate_data_write_ready_rows"), "0")),
        "alb2002_analysis_candidate_current_decision": next((row.get("value", "") for row in alb2002_analysis_candidate_summary if row.get("metric") == "alb2002_analysis_candidate_current_decision"), ""),
        "alb2002_climate_centroid_exposure_input": row_count(TEMP_DIR / "alb2002_climate_centroid_exposure_input.csv"),
        "alb2002_climate_centroid_exposure_candidates": row_count(TEMP_DIR / "alb2002_climate_centroid_exposure_candidates.csv"),
        "alb2002_climate_centroid_nasa_api_manifest": row_count(TEMP_DIR / "alb2002_climate_centroid_nasa_power_api_manifest.csv"),
        "alb2002_climate_centroid_exposure_audit": row_count(RESULT_DIR / "alb2002_climate_centroid_exposure_audit.csv"),
        "alb2002_climate_centroid_exposure_summary": len(alb2002_climate_centroid_summary),
        "alb2002_climate_centroid_input_rows": safe_int(next((row.get("value", "0") for row in alb2002_climate_centroid_summary if row.get("metric") == "alb2002_climate_centroid_input_rows"), "0")),
        "alb2002_climate_centroid_distinct_district_rows": safe_int(next((row.get("value", "0") for row in alb2002_climate_centroid_summary if row.get("metric") == "alb2002_climate_centroid_distinct_district_rows"), "0")),
        "alb2002_climate_centroid_household_rows_covered": safe_int(next((row.get("value", "0") for row in alb2002_climate_centroid_summary if row.get("metric") == "alb2002_climate_centroid_household_rows_covered"), "0")),
        "alb2002_climate_centroid_exposure_rows": safe_int(next((row.get("value", "0") for row in alb2002_climate_centroid_summary if row.get("metric") == "alb2002_climate_centroid_exposure_rows"), "0")),
        "alb2002_climate_centroid_nasa_api_rows": safe_int(next((row.get("value", "0") for row in alb2002_climate_centroid_summary if row.get("metric") == "alb2002_climate_centroid_nasa_api_rows"), "0")),
        "alb2002_climate_centroid_nasa_failed_rows": safe_int(next((row.get("value", "0") for row in alb2002_climate_centroid_summary if row.get("metric") == "alb2002_climate_centroid_nasa_failed_rows"), "0")),
        "alb2002_climate_centroid_precip_nonmissing_rows": safe_int(next((row.get("value", "0") for row in alb2002_climate_centroid_summary if row.get("metric") == "alb2002_climate_centroid_precip_nonmissing_rows"), "0")),
        "alb2002_climate_centroid_temp_nonmissing_rows": safe_int(next((row.get("value", "0") for row in alb2002_climate_centroid_summary if row.get("metric") == "alb2002_climate_centroid_temp_nonmissing_rows"), "0")),
        "alb2002_climate_centroid_boundary_year": safe_int(next((row.get("value", "0") for row in alb2002_climate_centroid_summary if row.get("metric") == "alb2002_climate_centroid_boundary_year"), "0")),
        "alb2002_climate_centroid_climate_linkage_ready_rows": safe_int(next((row.get("value", "0") for row in alb2002_climate_centroid_summary if row.get("metric") == "alb2002_climate_centroid_climate_linkage_ready_rows"), "0")),
        "alb2002_climate_centroid_data_write_ready_rows": safe_int(next((row.get("value", "0") for row in alb2002_climate_centroid_summary if row.get("metric") == "alb2002_climate_centroid_data_write_ready_rows"), "0")),
        "alb2002_climate_centroid_current_decision": next((row.get("value", "") for row in alb2002_climate_centroid_summary if row.get("metric") == "alb2002_climate_centroid_current_decision"), ""),
        "alb2002_climate_shock_candidate_exposures": row_count(TEMP_DIR / "alb2002_climate_shock_candidate_exposures.csv"),
        "alb2002_climate_shock_candidate_lineage": row_count(TEMP_DIR / "alb2002_climate_shock_candidate_lineage.csv"),
        "alb2002_climate_shock_candidate_audit": row_count(RESULT_DIR / "alb2002_climate_shock_candidate_audit.csv"),
        "alb2002_climate_shock_candidate_summary": len(alb2002_climate_shock_summary),
        "alb2002_climate_shock_candidate_exposure_rows": safe_int(next((row.get("value", "0") for row in alb2002_climate_shock_summary if row.get("metric") == "alb2002_climate_shock_candidate_exposure_rows"), "0")),
        "alb2002_climate_shock_candidate_source_centroid_rows": safe_int(next((row.get("value", "0") for row in alb2002_climate_shock_summary if row.get("metric") == "alb2002_climate_shock_candidate_source_centroid_rows"), "0")),
        "alb2002_climate_shock_candidate_lineage_rows": safe_int(next((row.get("value", "0") for row in alb2002_climate_shock_summary if row.get("metric") == "alb2002_climate_shock_candidate_lineage_rows"), "0")),
        "alb2002_climate_shock_candidate_audit_rows": safe_int(next((row.get("value", "0") for row in alb2002_climate_shock_summary if row.get("metric") == "alb2002_climate_shock_candidate_audit_rows"), "0")),
        "alb2002_climate_shock_candidate_reference_group_rows": safe_int(next((row.get("value", "0") for row in alb2002_climate_shock_summary if row.get("metric") == "alb2002_climate_shock_candidate_reference_group_rows"), "0")),
        "alb2002_climate_shock_candidate_min_reference_group_size": safe_int(next((row.get("value", "0") for row in alb2002_climate_shock_summary if row.get("metric") == "alb2002_climate_shock_candidate_min_reference_group_size"), "0")),
        "alb2002_climate_shock_candidate_precip_z_nonmissing_rows": safe_int(next((row.get("value", "0") for row in alb2002_climate_shock_summary if row.get("metric") == "alb2002_climate_shock_candidate_precip_z_nonmissing_rows"), "0")),
        "alb2002_climate_shock_candidate_temp_z_nonmissing_rows": safe_int(next((row.get("value", "0") for row in alb2002_climate_shock_summary if row.get("metric") == "alb2002_climate_shock_candidate_temp_z_nonmissing_rows"), "0")),
        "alb2002_climate_shock_candidate_low_rain_rows": safe_int(next((row.get("value", "0") for row in alb2002_climate_shock_summary if row.get("metric") == "alb2002_climate_shock_candidate_low_rain_rows"), "0")),
        "alb2002_climate_shock_candidate_extreme_wet_rows": safe_int(next((row.get("value", "0") for row in alb2002_climate_shock_summary if row.get("metric") == "alb2002_climate_shock_candidate_extreme_wet_rows"), "0")),
        "alb2002_climate_shock_candidate_extreme_heat_rows": safe_int(next((row.get("value", "0") for row in alb2002_climate_shock_summary if row.get("metric") == "alb2002_climate_shock_candidate_extreme_heat_rows"), "0")),
        "alb2002_climate_shock_candidate_combined_stress_rows": safe_int(next((row.get("value", "0") for row in alb2002_climate_shock_summary if row.get("metric") == "alb2002_climate_shock_candidate_combined_stress_rows"), "0")),
        "alb2002_climate_shock_candidate_climate_linkage_ready_rows": safe_int(next((row.get("value", "0") for row in alb2002_climate_shock_summary if row.get("metric") == "alb2002_climate_shock_candidate_climate_linkage_ready_rows"), "0")),
        "alb2002_climate_shock_candidate_data_write_ready_rows": safe_int(next((row.get("value", "0") for row in alb2002_climate_shock_summary if row.get("metric") == "alb2002_climate_shock_candidate_data_write_ready_rows"), "0")),
        "alb2002_climate_shock_candidate_current_decision": next((row.get("value", "") for row in alb2002_climate_shock_summary if row.get("metric") == "alb2002_climate_shock_candidate_current_decision"), ""),
        "alb2002_climate_outcome_linked_candidate": row_count(TEMP_DIR / "alb2002_climate_outcome_linked_candidate.csv"),
        "alb2002_climate_outcome_linked_candidate_lineage": row_count(TEMP_DIR / "alb2002_climate_outcome_linked_candidate_lineage.csv"),
        "alb2002_climate_outcome_linked_candidate_audit": row_count(RESULT_DIR / "alb2002_climate_outcome_linked_candidate_audit.csv"),
        "alb2002_climate_outcome_linked_candidate_summary": len(alb2002_climate_outcome_linked_summary),
        "alb2002_climate_outcome_linked_candidate_rows": safe_int(next((row.get("value", "0") for row in alb2002_climate_outcome_linked_summary if row.get("metric") == "alb2002_climate_outcome_linked_candidate_rows"), "0")),
        "alb2002_climate_outcome_linked_candidate_household_rows": safe_int(next((row.get("value", "0") for row in alb2002_climate_outcome_linked_summary if row.get("metric") == "alb2002_climate_outcome_linked_candidate_household_rows"), "0")),
        "alb2002_climate_outcome_linked_candidate_window_rows": safe_int(next((row.get("value", "0") for row in alb2002_climate_outcome_linked_summary if row.get("metric") == "alb2002_climate_outcome_linked_candidate_window_rows"), "0")),
        "alb2002_climate_outcome_linked_candidate_district_month_cells": safe_int(next((row.get("value", "0") for row in alb2002_climate_outcome_linked_summary if row.get("metric") == "alb2002_climate_outcome_linked_candidate_district_month_cells"), "0")),
        "alb2002_climate_outcome_linked_candidate_lineage_rows": safe_int(next((row.get("value", "0") for row in alb2002_climate_outcome_linked_summary if row.get("metric") == "alb2002_climate_outcome_linked_candidate_lineage_rows"), "0")),
        "alb2002_climate_outcome_linked_candidate_audit_rows": safe_int(next((row.get("value", "0") for row in alb2002_climate_outcome_linked_summary if row.get("metric") == "alb2002_climate_outcome_linked_candidate_audit_rows"), "0")),
        "alb2002_climate_outcome_linked_candidate_source_analysis_rows": safe_int(next((row.get("value", "0") for row in alb2002_climate_outcome_linked_summary if row.get("metric") == "alb2002_climate_outcome_linked_candidate_source_analysis_rows"), "0")),
        "alb2002_climate_outcome_linked_candidate_source_uhc_rows": safe_int(next((row.get("value", "0") for row in alb2002_climate_outcome_linked_summary if row.get("metric") == "alb2002_climate_outcome_linked_candidate_source_uhc_rows"), "0")),
        "alb2002_climate_outcome_linked_candidate_source_shock_rows": safe_int(next((row.get("value", "0") for row in alb2002_climate_outcome_linked_summary if row.get("metric") == "alb2002_climate_outcome_linked_candidate_source_shock_rows"), "0")),
        "alb2002_climate_outcome_linked_candidate_expected_rows": safe_int(next((row.get("value", "0") for row in alb2002_climate_outcome_linked_summary if row.get("metric") == "alb2002_climate_outcome_linked_candidate_expected_rows"), "0")),
        "alb2002_climate_outcome_linked_candidate_unmatched_rows": safe_int(next((row.get("value", "0") for row in alb2002_climate_outcome_linked_summary if row.get("metric") == "alb2002_climate_outcome_linked_candidate_unmatched_rows"), "0")),
        "alb2002_climate_outcome_linked_candidate_precip_z_rows": safe_int(next((row.get("value", "0") for row in alb2002_climate_outcome_linked_summary if row.get("metric") == "alb2002_climate_outcome_linked_candidate_precip_z_rows"), "0")),
        "alb2002_climate_outcome_linked_candidate_temp_z_rows": safe_int(next((row.get("value", "0") for row in alb2002_climate_outcome_linked_summary if row.get("metric") == "alb2002_climate_outcome_linked_candidate_temp_z_rows"), "0")),
        "alb2002_climate_outcome_linked_candidate_combined_stress_rows": safe_int(next((row.get("value", "0") for row in alb2002_climate_outcome_linked_summary if row.get("metric") == "alb2002_climate_outcome_linked_candidate_combined_stress_rows"), "0")),
        "alb2002_climate_outcome_linked_candidate_che10_or_access_rows": safe_int(next((row.get("value", "0") for row in alb2002_climate_outcome_linked_summary if row.get("metric") == "alb2002_climate_outcome_linked_candidate_che10_or_access_rows"), "0")),
        "alb2002_climate_outcome_linked_candidate_che25_or_access_rows": safe_int(next((row.get("value", "0") for row in alb2002_climate_outcome_linked_summary if row.get("metric") == "alb2002_climate_outcome_linked_candidate_che25_or_access_rows"), "0")),
        "alb2002_climate_outcome_linked_candidate_both_che10_access_rows": safe_int(next((row.get("value", "0") for row in alb2002_climate_outcome_linked_summary if row.get("metric") == "alb2002_climate_outcome_linked_candidate_both_che10_access_rows"), "0")),
        "alb2002_climate_outcome_linked_candidate_coping_rows": safe_int(next((row.get("value", "0") for row in alb2002_climate_outcome_linked_summary if row.get("metric") == "alb2002_climate_outcome_linked_candidate_coping_rows"), "0")),
        "alb2002_climate_outcome_linked_candidate_climate_linkage_ready_rows": safe_int(next((row.get("value", "0") for row in alb2002_climate_outcome_linked_summary if row.get("metric") == "alb2002_climate_outcome_linked_candidate_climate_linkage_ready_rows"), "0")),
        "alb2002_climate_outcome_linked_candidate_outcome_promotion_ready_rows": safe_int(next((row.get("value", "0") for row in alb2002_climate_outcome_linked_summary if row.get("metric") == "alb2002_climate_outcome_linked_candidate_outcome_promotion_ready_rows"), "0")),
        "alb2002_climate_outcome_linked_candidate_harmonized_recipe_ready_rows": safe_int(next((row.get("value", "0") for row in alb2002_climate_outcome_linked_summary if row.get("metric") == "alb2002_climate_outcome_linked_candidate_harmonized_recipe_ready_rows"), "0")),
        "alb2002_climate_outcome_linked_candidate_data_write_ready_rows": safe_int(next((row.get("value", "0") for row in alb2002_climate_outcome_linked_summary if row.get("metric") == "alb2002_climate_outcome_linked_candidate_data_write_ready_rows"), "0")),
        "alb2002_climate_outcome_linked_candidate_current_decision": next((row.get("value", "") for row in alb2002_climate_outcome_linked_summary if row.get("metric") == "alb2002_climate_outcome_linked_candidate_current_decision"), ""),
        "alb2002_linked_candidate_descriptive_audit": row_count(RESULT_DIR / "alb2002_linked_candidate_descriptive_audit.csv"),
        "alb2002_linked_candidate_descriptive_cells": row_count(RESULT_DIR / "alb2002_linked_candidate_descriptive_cells.csv"),
        "alb2002_linked_candidate_descriptive_summary": len(alb2002_linked_candidate_descriptive_summary),
        "alb2002_linked_candidate_descriptive_input_rows": safe_int(next((row.get("value", "0") for row in alb2002_linked_candidate_descriptive_summary if row.get("metric") == "alb2002_linked_candidate_descriptive_input_rows"), "0")),
        "alb2002_linked_candidate_descriptive_household_rows": safe_int(next((row.get("value", "0") for row in alb2002_linked_candidate_descriptive_summary if row.get("metric") == "alb2002_linked_candidate_descriptive_household_rows"), "0")),
        "alb2002_linked_candidate_descriptive_window_rows": safe_int(next((row.get("value", "0") for row in alb2002_linked_candidate_descriptive_summary if row.get("metric") == "alb2002_linked_candidate_descriptive_window_rows"), "0")),
        "alb2002_linked_candidate_descriptive_audit_rows": safe_int(next((row.get("value", "0") for row in alb2002_linked_candidate_descriptive_summary if row.get("metric") == "alb2002_linked_candidate_descriptive_audit_rows"), "0")),
        "alb2002_linked_candidate_descriptive_cell_rows": safe_int(next((row.get("value", "0") for row in alb2002_linked_candidate_descriptive_summary if row.get("metric") == "alb2002_linked_candidate_descriptive_cell_rows"), "0")),
        "alb2002_linked_candidate_descriptive_household_outcome_cell_rows": safe_int(next((row.get("value", "0") for row in alb2002_linked_candidate_descriptive_summary if row.get("metric") == "alb2002_linked_candidate_descriptive_household_outcome_cell_rows"), "0")),
        "alb2002_linked_candidate_descriptive_subgroup_outcome_cell_rows": safe_int(next((row.get("value", "0") for row in alb2002_linked_candidate_descriptive_summary if row.get("metric") == "alb2002_linked_candidate_descriptive_subgroup_outcome_cell_rows"), "0")),
        "alb2002_linked_candidate_descriptive_climate_flag_cell_rows": safe_int(next((row.get("value", "0") for row in alb2002_linked_candidate_descriptive_summary if row.get("metric") == "alb2002_linked_candidate_descriptive_climate_flag_cell_rows"), "0")),
        "alb2002_linked_candidate_descriptive_outcome_by_climate_flag_cell_rows": safe_int(next((row.get("value", "0") for row in alb2002_linked_candidate_descriptive_summary if row.get("metric") == "alb2002_linked_candidate_descriptive_outcome_by_climate_flag_cell_rows"), "0")),
        "alb2002_linked_candidate_descriptive_che10_or_access_households": safe_int(next((row.get("value", "0") for row in alb2002_linked_candidate_descriptive_summary if row.get("metric") == "alb2002_linked_candidate_descriptive_che10_or_access_households"), "0")),
        "alb2002_linked_candidate_descriptive_che25_or_access_households": safe_int(next((row.get("value", "0") for row in alb2002_linked_candidate_descriptive_summary if row.get("metric") == "alb2002_linked_candidate_descriptive_che25_or_access_households"), "0")),
        "alb2002_linked_candidate_descriptive_both_che10_access_households": safe_int(next((row.get("value", "0") for row in alb2002_linked_candidate_descriptive_summary if row.get("metric") == "alb2002_linked_candidate_descriptive_both_che10_access_households"), "0")),
        "alb2002_linked_candidate_descriptive_coping_households": safe_int(next((row.get("value", "0") for row in alb2002_linked_candidate_descriptive_summary if row.get("metric") == "alb2002_linked_candidate_descriptive_coping_households"), "0")),
        "alb2002_linked_candidate_descriptive_combined_stress_rows": safe_int(next((row.get("value", "0") for row in alb2002_linked_candidate_descriptive_summary if row.get("metric") == "alb2002_linked_candidate_descriptive_combined_stress_rows"), "0")),
        "alb2002_linked_candidate_descriptive_climate_linkage_ready_rows": safe_int(next((row.get("value", "0") for row in alb2002_linked_candidate_descriptive_summary if row.get("metric") == "alb2002_linked_candidate_descriptive_climate_linkage_ready_rows"), "0")),
        "alb2002_linked_candidate_descriptive_outcome_promotion_ready_rows": safe_int(next((row.get("value", "0") for row in alb2002_linked_candidate_descriptive_summary if row.get("metric") == "alb2002_linked_candidate_descriptive_outcome_promotion_ready_rows"), "0")),
        "alb2002_linked_candidate_descriptive_harmonized_recipe_ready_rows": safe_int(next((row.get("value", "0") for row in alb2002_linked_candidate_descriptive_summary if row.get("metric") == "alb2002_linked_candidate_descriptive_harmonized_recipe_ready_rows"), "0")),
        "alb2002_linked_candidate_descriptive_data_write_ready_rows": safe_int(next((row.get("value", "0") for row in alb2002_linked_candidate_descriptive_summary if row.get("metric") == "alb2002_linked_candidate_descriptive_data_write_ready_rows"), "0")),
        "alb2002_linked_candidate_descriptive_current_decision": next((row.get("value", "") for row in alb2002_linked_candidate_descriptive_summary if row.get("metric") == "alb2002_linked_candidate_descriptive_current_decision"), ""),
        "alb2002_weight_design_evidence_audit": row_count(TEMP_DIR / "alb2002_weight_design_evidence_audit.csv"),
        "alb2002_weight_design_evidence_summary": len(alb2002_weight_design_summary),
        "alb2002_weight_design_source_page_flag_rows": safe_int(next((row.get("value", "0") for row in alb2002_weight_design_summary if row.get("metric") == "alb2002_weight_design_source_page_flag_rows"), "0")),
        "alb2002_weight_design_raw_weight_file_rows": safe_int(next((row.get("value", "0") for row in alb2002_weight_design_summary if row.get("metric") == "alb2002_weight_design_raw_weight_file_rows"), "0")),
        "alb2002_weight_design_positive_weight_rows": safe_int(next((row.get("value", "0") for row in alb2002_weight_design_summary if row.get("metric") == "alb2002_weight_design_positive_weight_rows"), "0")),
        "alb2002_weight_design_candidate_key_match_rows": safe_int(next((row.get("value", "0") for row in alb2002_weight_design_summary if row.get("metric") == "alb2002_weight_design_candidate_key_match_rows"), "0")),
        "alb2002_weight_design_distinct_psu_rows": safe_int(next((row.get("value", "0") for row in alb2002_weight_design_summary if row.get("metric") == "alb2002_weight_design_distinct_psu_rows"), "0")),
        "alb2002_weight_design_distinct_stratum_rows": safe_int(next((row.get("value", "0") for row in alb2002_weight_design_summary if row.get("metric") == "alb2002_weight_design_distinct_stratum_rows"), "0")),
        "alb2002_weight_design_weighted_inference_ready_rows": safe_int(next((row.get("value", "0") for row in alb2002_weight_design_summary if row.get("metric") == "alb2002_weight_design_weighted_inference_ready_rows"), "0")),
        "alb2002_weight_design_harmonized_promotion_ready_rows": safe_int(next((row.get("value", "0") for row in alb2002_weight_design_summary if row.get("metric") == "alb2002_weight_design_harmonized_promotion_ready_rows"), "0")),
        "alb2002_weight_design_current_decision": next((row.get("value", "") for row in alb2002_weight_design_summary if row.get("metric") == "alb2002_weight_design_current_decision"), ""),
        "alb2002_sample_design_documentation_audit": row_count(TEMP_DIR / "alb2002_sample_design_documentation_audit.csv"),
        "alb2002_sample_design_documentation_summary": len(alb2002_sample_design_summary),
        "alb2002_sample_design_pdf_available_rows": safe_int(next((row.get("value", "0") for row in alb2002_sample_design_summary if row.get("metric") == "alb2002_sample_design_pdf_available_rows"), "0")),
        "alb2002_sample_design_pdf_pages": safe_int(next((row.get("value", "0") for row in alb2002_sample_design_summary if row.get("metric") == "alb2002_sample_design_pdf_pages"), "0")),
        "alb2002_sample_design_official_450_psu_8_hh_rows": safe_int(next((row.get("value", "0") for row in alb2002_sample_design_summary if row.get("metric") == "alb2002_sample_design_official_450_psu_8_hh_rows"), "0")),
        "alb2002_sample_design_official_3599_final_rows": safe_int(next((row.get("value", "0") for row in alb2002_sample_design_summary if row.get("metric") == "alb2002_sample_design_official_3599_final_rows"), "0")),
        "alb2002_sample_design_raw_weight_rows": safe_int(next((row.get("value", "0") for row in alb2002_sample_design_summary if row.get("metric") == "alb2002_sample_design_raw_weight_rows"), "0")),
        "alb2002_sample_design_positive_weight_rows": safe_int(next((row.get("value", "0") for row in alb2002_sample_design_summary if row.get("metric") == "alb2002_sample_design_positive_weight_rows"), "0")),
        "alb2002_sample_design_distinct_psu_rows": safe_int(next((row.get("value", "0") for row in alb2002_sample_design_summary if row.get("metric") == "alb2002_sample_design_distinct_psu_rows"), "0")),
        "alb2002_sample_design_raw_design_concordance_rows": safe_int(next((row.get("value", "0") for row in alb2002_sample_design_summary if row.get("metric") == "alb2002_sample_design_raw_design_concordance_rows"), "0")),
        "alb2002_sample_design_documentation_ready_rows": safe_int(next((row.get("value", "0") for row in alb2002_sample_design_summary if row.get("metric") == "alb2002_sample_design_documentation_ready_rows"), "0")),
        "alb2002_sample_design_weighted_inference_ready_rows": safe_int(next((row.get("value", "0") for row in alb2002_sample_design_summary if row.get("metric") == "alb2002_sample_design_weighted_inference_ready_rows"), "0")),
        "alb2002_sample_design_harmonized_promotion_ready_rows": safe_int(next((row.get("value", "0") for row in alb2002_sample_design_summary if row.get("metric") == "alb2002_sample_design_harmonized_promotion_ready_rows"), "0")),
        "alb2002_sample_design_current_decision": next((row.get("value", "") for row in alb2002_sample_design_summary if row.get("metric") == "alb2002_sample_design_current_decision"), ""),
        "alb2002_minimum_recipe_promotion_action_rows": row_count(TEMP_DIR / "alb2002_minimum_recipe_promotion_action_queue.csv"),
        "alb2002_minimum_recipe_promotion_gate_rows": row_count(TEMP_DIR / "alb2002_minimum_recipe_promotion_gate_checklist.csv"),
        "alb2002_minimum_recipe_promotion_summary_rows": len(alb2002_minimum_recipe_summary),
        "alb2002_minimum_recipe_promotion_blocked_gates": safe_int(next((row.get("value", "0") for row in alb2002_minimum_recipe_summary if row.get("metric") == "alb2002_minimum_recipe_promotion_blocked_gates"), "0")),
        "alb2002_minimum_recipe_promotion_candidate_gates": safe_int(next((row.get("value", "0") for row in alb2002_minimum_recipe_summary if row.get("metric") == "alb2002_minimum_recipe_promotion_candidate_gates"), "0")),
        "alb2002_minimum_recipe_promotion_weight_positive_rows": safe_int(next((row.get("value", "0") for row in alb2002_minimum_recipe_summary if row.get("metric") == "alb2002_minimum_recipe_promotion_weight_design_positive_weight_rows"), "0")),
        "alb2002_minimum_recipe_promotion_weight_key_match_rows": safe_int(next((row.get("value", "0") for row in alb2002_minimum_recipe_summary if row.get("metric") == "alb2002_minimum_recipe_promotion_weight_design_key_match_rows"), "0")),
        "alb2002_minimum_recipe_promotion_weighted_inference_ready_rows": safe_int(next((row.get("value", "0") for row in alb2002_minimum_recipe_summary if row.get("metric") == "alb2002_minimum_recipe_promotion_weight_design_weighted_inference_ready_rows"), "0")),
        "alb2002_minimum_recipe_promotion_harmonized_ready_rows": safe_int(next((row.get("value", "0") for row in alb2002_minimum_recipe_summary if row.get("metric") == "alb2002_minimum_recipe_promotion_harmonized_ready_rows"), "0")),
        "alb2002_minimum_recipe_promotion_outcome_ready_rows": safe_int(next((row.get("value", "0") for row in alb2002_minimum_recipe_summary if row.get("metric") == "alb2002_minimum_recipe_promotion_outcome_ready_rows"), "0")),
        "alb2002_minimum_recipe_promotion_sdg382_ready_rows": safe_int(next((row.get("value", "0") for row in alb2002_minimum_recipe_summary if row.get("metric") == "alb2002_minimum_recipe_promotion_sdg382_ready_rows"), "0")),
        "alb2002_minimum_recipe_promotion_climate_linkage_ready_rows": safe_int(next((row.get("value", "0") for row in alb2002_minimum_recipe_summary if row.get("metric") == "alb2002_minimum_recipe_promotion_climate_linkage_ready_rows"), "0")),
        "alb2002_minimum_recipe_promotion_current_decision": next((row.get("value", "") for row in alb2002_minimum_recipe_summary if row.get("metric") == "alb2002_minimum_recipe_promotion_current_decision"), ""),
        "alb2005_documented_variable_evidence": row_count(TEMP_DIR / "alb2005_documented_variable_evidence.csv"),
        "alb2005_documented_harmonization_summary": len(alb2005_summary),
        "alb2005_recipe_ready_rows": safe_int(next((row.get("value", "0") for row in alb2005_summary if row.get("metric") == "alb2005_recipe_ready_rows"), "0")),
        "alb2005_household_core_candidate": row_count(TEMP_DIR / "alb2005_household_core_candidate.csv"),
        "alb2005_household_core_merge_audit": row_count(TEMP_DIR / "alb2005_household_core_merge_audit.csv"),
        "alb2005_household_core_lineage": row_count(TEMP_DIR / "alb2005_household_core_lineage.csv"),
        "alb2005_household_core_candidate_summary": len(alb2005_core_summary),
        "alb2005_household_core_recipe_ready_rows": safe_int(next((row.get("value", "0") for row in alb2005_core_summary if row.get("metric") == "alb2005_household_core_recipe_ready_rows"), "0")),
        "alb2005_provisional_outcome_feasibility_audit": row_count(TEMP_DIR / "alb2005_provisional_outcome_feasibility_audit.csv"),
        "alb2005_provisional_outcome_feasibility_summary": len(alb2005_outcome_summary),
        "alb2005_provisional_outcome_ready_rows": safe_int(next((row.get("value", "0") for row in alb2005_outcome_summary if row.get("metric") == "alb2005_provisional_outcome_ready_rows"), "0")),
        "alb2005_outcome_semantics_raw_value_audit": row_count(TEMP_DIR / "alb2005_outcome_semantics_raw_value_audit.csv"),
        "alb2005_outcome_semantics_raw_value_summary": len(alb2005_semantics_summary),
        "alb2005_outcome_semantics_outcome_ready_rows": safe_int(next((row.get("value", "0") for row in alb2005_semantics_summary if row.get("metric") == "alb2005_outcome_semantics_outcome_ready_rows"), "0")),
        "alb2005_outcome_semantics_sdg382_ready_rows": safe_int(next((row.get("value", "0") for row in alb2005_semantics_summary if row.get("metric") == "alb2005_outcome_semantics_sdg382_ready_rows"), "0")),
        "alb2005_outcome_semantics_climate_linkage_ready_rows": safe_int(next((row.get("value", "0") for row in alb2005_semantics_summary if row.get("metric") == "alb2005_outcome_semantics_climate_linkage_ready_rows"), "0")),
        "alb2005_outcome_semantics_financial_oop_candidate_rows": safe_int(next((row.get("value", "0") for row in alb2005_semantics_summary if row.get("metric") == "alb2005_outcome_semantics_financial_oop_candidate_rows"), "0")),
        "alb2005_outcome_semantics_gift_candidate_rows": safe_int(next((row.get("value", "0") for row in alb2005_semantics_summary if row.get("metric") == "alb2005_outcome_semantics_gift_candidate_rows"), "0")),
        "alb2005_outcome_semantics_access_candidate_rows": safe_int(next((row.get("value", "0") for row in alb2005_semantics_summary if row.get("metric") == "alb2005_outcome_semantics_access_candidate_rows"), "0")),
        "alb2005_outcome_semantics_conditional_reason_rows": safe_int(next((row.get("value", "0") for row in alb2005_semantics_summary if row.get("metric") == "alb2005_outcome_semantics_conditional_reason_rows"), "0")),
        "alb2005_timing_geography_exhaustive_audit": row_count(TEMP_DIR / "alb2005_timing_geography_exhaustive_audit.csv"),
        "alb2005_timing_geography_exhaustive_summary": len(alb2005_timing_geo_summary),
        "alb2005_climate_linkage_ready_rows": safe_int(next((row.get("value", "0") for row in alb2005_timing_geo_summary if row.get("metric") == "alb2005_climate_linkage_ready_rows"), "0")),
        "alb2005_timing_geography_source_search_audit": row_count(TEMP_DIR / "alb2005_timing_geography_source_search_audit.csv"),
        "alb2005_timing_geography_source_search_summary": len(alb2005_timing_geo_source_summary),
        "alb2005_timing_geography_source_search_rows": safe_int(next((row.get("value", "0") for row in alb2005_timing_geo_source_summary if row.get("metric") == "alb2005_timing_geography_source_search_rows"), "0")),
        "alb2005_timing_geography_source_search_target_concepts": safe_int(next((row.get("value", "0") for row in alb2005_timing_geo_source_summary if row.get("metric") == "alb2005_timing_geography_source_search_target_concepts"), "0")),
        "alb2005_timing_geography_source_search_local_files_scanned": safe_int(next((row.get("value", "0") for row in alb2005_timing_geo_source_summary if row.get("metric") == "alb2005_timing_geography_source_search_local_files_scanned"), "0")),
        "alb2005_timing_geography_source_search_local_variables_scanned": safe_int(next((row.get("value", "0") for row in alb2005_timing_geo_source_summary if row.get("metric") == "alb2005_timing_geography_source_search_local_variables_scanned"), "0")),
        "alb2005_timing_geography_source_search_questionnaire_workbooks_scanned": safe_int(next((row.get("value", "0") for row in alb2005_timing_geo_source_summary if row.get("metric") == "alb2005_timing_geography_source_search_questionnaire_workbooks_scanned"), "0")),
        "alb2005_timing_geography_source_search_raw_targets_with_hits": safe_int(next((row.get("value", "0") for row in alb2005_timing_geo_source_summary if row.get("metric") == "alb2005_timing_geography_source_search_raw_targets_with_hits"), "0")),
        "alb2005_timing_geography_source_search_questionnaire_targets_with_hits": safe_int(next((row.get("value", "0") for row in alb2005_timing_geo_source_summary if row.get("metric") == "alb2005_timing_geography_source_search_questionnaire_targets_with_hits"), "0")),
        "alb2005_timing_geography_source_search_legacy_questionnaire_timing_rows": safe_int(next((row.get("value", "0") for row in alb2005_timing_geo_source_summary if row.get("metric") == "alb2005_timing_geography_source_search_legacy_questionnaire_timing_rows"), "0")),
        "alb2005_timing_geography_source_search_verified_household_timing_rows": safe_int(next((row.get("value", "0") for row in alb2005_timing_geo_source_summary if row.get("metric") == "alb2005_timing_geography_source_search_verified_household_timing_rows"), "0")),
        "alb2005_timing_geography_source_search_coordinate_candidate_rows": safe_int(next((row.get("value", "0") for row in alb2005_timing_geo_source_summary if row.get("metric") == "alb2005_timing_geography_source_search_coordinate_candidate_rows"), "0")),
        "alb2005_timing_geography_source_search_partial_district_variable_rows": safe_int(next((row.get("value", "0") for row in alb2005_timing_geo_source_summary if row.get("metric") == "alb2005_timing_geography_source_search_partial_district_variable_rows"), "0")),
        "alb2005_timing_geography_source_search_partial_district_name_nonmissing_rows": safe_int(next((row.get("value", "0") for row in alb2005_timing_geo_source_summary if row.get("metric") == "alb2005_timing_geography_source_search_partial_district_name_nonmissing_rows"), "0")),
        "alb2005_timing_geography_source_search_partial_district_code_nonmissing_rows": safe_int(next((row.get("value", "0") for row in alb2005_timing_geo_source_summary if row.get("metric") == "alb2005_timing_geography_source_search_partial_district_code_nonmissing_rows"), "0")),
        "alb2005_timing_geography_source_search_required_value_key_timing_rows": safe_int(next((row.get("value", "0") for row in alb2005_timing_geo_source_summary if row.get("metric") == "alb2005_timing_geography_source_search_required_value_key_timing_rows"), "0")),
        "alb2005_timing_geography_source_search_required_value_key_coordinate_rows": safe_int(next((row.get("value", "0") for row in alb2005_timing_geo_source_summary if row.get("metric") == "alb2005_timing_geography_source_search_required_value_key_coordinate_rows"), "0")),
        "alb2005_timing_geography_source_search_geography_crosswalk_ready_rows": safe_int(next((row.get("value", "0") for row in alb2005_timing_geo_source_summary if row.get("metric") == "alb2005_timing_geography_source_search_geography_crosswalk_ready_rows"), "0")),
        "alb2005_timing_geography_source_search_interview_timing_ready_rows": safe_int(next((row.get("value", "0") for row in alb2005_timing_geo_source_summary if row.get("metric") == "alb2005_timing_geography_source_search_interview_timing_ready_rows"), "0")),
        "alb2005_timing_geography_source_search_climate_linkage_ready_rows": safe_int(next((row.get("value", "0") for row in alb2005_timing_geo_source_summary if row.get("metric") == "alb2005_timing_geography_source_search_climate_linkage_ready_rows"), "0")),
        "alb2005_timing_geography_source_search_current_decision": next((row.get("value", "") for row in alb2005_timing_geo_source_summary if row.get("metric") == "alb2005_timing_geography_source_search_current_decision"), ""),
        "alb2005_harmonization_value_decision_audit": row_count(TEMP_DIR / "alb2005_harmonization_value_decision_audit.csv"),
        "alb2005_harmonization_value_decision_summary": len(alb2005_value_decision_summary),
        "alb2005_harmonization_value_decision_recipe_ready_rows": safe_int(next((row.get("value", "0") for row in alb2005_value_decision_summary if row.get("metric") == "alb2005_harmonization_value_decision_recipe_ready_rows"), "0")),
        "alb2005_harmonization_value_decision_required_blocked_rows": safe_int(next((row.get("value", "0") for row in alb2005_value_decision_summary if row.get("metric") == "alb2005_harmonization_value_decision_required_blocked_rows"), "0")),
        "alb2005_required_value_key_audit": row_count(TEMP_DIR / "alb2005_required_value_key_audit.csv"),
        "alb2005_required_value_key_summary": len(alb2005_required_value_key_summary),
        "alb2005_required_value_key_recipe_ready_rows": safe_int(next((row.get("value", "0") for row in alb2005_required_value_key_summary if row.get("metric") == "alb2005_required_value_key_recipe_ready_rows"), "0")),
        "alb2005_required_value_key_not_promoted_rows": safe_int(next((row.get("value", "0") for row in alb2005_required_value_key_summary if row.get("metric") == "alb2005_required_value_key_not_promoted_rows"), "0")),
        "alb2005_required_value_key_total_consumption_nonmissing_rows": safe_int(next((row.get("value", "0") for row in alb2005_required_value_key_summary if row.get("metric") == "alb2005_required_value_key_total_consumption_nonmissing_rows"), "0")),
        "alb2005_required_value_key_oop_4w_household_positive_rows": safe_int(next((row.get("value", "0") for row in alb2005_required_value_key_summary if row.get("metric") == "alb2005_required_value_key_oop_4w_household_positive_rows"), "0")),
        "alb2005_required_value_key_oop_12m_household_positive_rows": safe_int(next((row.get("value", "0") for row in alb2005_required_value_key_summary if row.get("metric") == "alb2005_required_value_key_oop_12m_household_positive_rows"), "0")),
        "alb2005_required_value_key_district_code_nonmissing_rows": safe_int(next((row.get("value", "0") for row in alb2005_required_value_key_summary if row.get("metric") == "alb2005_required_value_key_district_code_nonmissing_rows"), "0")),
        "alb2005_required_value_key_interview_timing_verified_rows": safe_int(next((row.get("value", "0") for row in alb2005_required_value_key_summary if row.get("metric") == "alb2005_required_value_key_interview_timing_verified_rows"), "0")),
        "alb2005_required_value_key_coordinate_ready_rows": safe_int(next((row.get("value", "0") for row in alb2005_required_value_key_summary if row.get("metric") == "alb2005_required_value_key_coordinate_ready_rows"), "0")),
        "alb2005_required_value_key_climate_linkage_ready_rows": safe_int(next((row.get("value", "0") for row in alb2005_required_value_key_summary if row.get("metric") == "alb2005_required_value_key_climate_linkage_ready_rows"), "0")),
        "alb2005_health_questionnaire_semantics_audit": row_count(TEMP_DIR / "alb2005_health_questionnaire_semantics_audit.csv"),
        "alb2005_health_questionnaire_semantics_summary": len(alb2005_health_questionnaire_summary),
        "alb2005_health_questionnaire_oop_item_rows": safe_int(next((row.get("value", "0") for row in alb2005_health_questionnaire_summary if row.get("metric") == "alb2005_health_questionnaire_oop_item_rows"), "0")),
        "alb2005_health_questionnaire_old_lek_unit_rows": safe_int(next((row.get("value", "0") for row in alb2005_health_questionnaire_summary if row.get("metric") == "alb2005_health_questionnaire_old_lek_unit_rows"), "0")),
        "alb2005_health_questionnaire_access_rows": safe_int(next((row.get("value", "0") for row in alb2005_health_questionnaire_summary if row.get("metric") == "alb2005_health_questionnaire_access_rows"), "0")),
        "alb2005_health_questionnaire_cost_barrier_rows": safe_int(next((row.get("value", "0") for row in alb2005_health_questionnaire_summary if row.get("metric") == "alb2005_health_questionnaire_cost_barrier_rows"), "0")),
        "alb2005_health_questionnaire_recipe_ready_rows": safe_int(next((row.get("value", "0") for row in alb2005_health_questionnaire_summary if row.get("metric") == "alb2005_health_questionnaire_recipe_ready_rows"), "0")),
        "alb2005_health_questionnaire_outcome_ready_rows": safe_int(next((row.get("value", "0") for row in alb2005_health_questionnaire_summary if row.get("metric") == "alb2005_health_questionnaire_outcome_ready_rows"), "0")),
        "alb2005_health_questionnaire_climate_linkage_ready_rows": safe_int(next((row.get("value", "0") for row in alb2005_health_questionnaire_summary if row.get("metric") == "alb2005_health_questionnaire_climate_linkage_ready_rows"), "0")),
        "alb2005_oop_aggregation_policy_audit": row_count(TEMP_DIR / "alb2005_oop_aggregation_policy_audit.csv"),
        "alb2005_oop_aggregation_policy_summary": len(alb2005_oop_policy_summary),
        "alb2005_oop_aggregation_policy_rows": safe_int(next((row.get("value", "0") for row in alb2005_oop_policy_summary if row.get("metric") == "alb2005_oop_aggregation_policy_rows"), "0")),
        "alb2005_oop_aggregation_policy_household_rows": safe_int(next((row.get("value", "0") for row in alb2005_oop_policy_summary if row.get("metric") == "alb2005_oop_aggregation_policy_household_rows"), "0")),
        "alb2005_oop_aggregation_policy_total_consumption_rows": safe_int(next((row.get("value", "0") for row in alb2005_oop_policy_summary if row.get("metric") == "alb2005_oop_aggregation_policy_total_consumption_rows"), "0")),
        "alb2005_oop_aggregation_policy_questionnaire_oop_item_rows_observed": safe_int(next((row.get("value", "0") for row in alb2005_oop_policy_summary if row.get("metric") == "alb2005_oop_aggregation_policy_questionnaire_oop_item_rows_observed"), "0")),
        "alb2005_oop_aggregation_policy_questionnaire_old_lek_rows_observed": safe_int(next((row.get("value", "0") for row in alb2005_oop_policy_summary if row.get("metric") == "alb2005_oop_aggregation_policy_questionnaire_old_lek_rows_observed"), "0")),
        "alb2005_oop_aggregation_policy_outcome_ready_rows": safe_int(next((row.get("value", "0") for row in alb2005_oop_policy_summary if row.get("metric") == "alb2005_oop_aggregation_policy_outcome_ready_rows"), "0")),
        "alb2005_oop_aggregation_policy_recipe_ready_rows": safe_int(next((row.get("value", "0") for row in alb2005_oop_policy_summary if row.get("metric") == "alb2005_oop_aggregation_policy_recipe_ready_rows"), "0")),
        "alb2005_oop_aggregation_policy_climate_linkage_ready_rows": safe_int(next((row.get("value", "0") for row in alb2005_oop_policy_summary if row.get("metric") == "alb2005_oop_aggregation_policy_climate_linkage_ready_rows"), "0")),
        "alb2005_skip_missing_semantics_audit": row_count(TEMP_DIR / "alb2005_skip_missing_semantics_audit.csv"),
        "alb2005_skip_missing_semantics_summary": len(alb2005_skip_missing_summary),
        "alb2005_skip_missing_semantics_rows": safe_int(next((row.get("value", "0") for row in alb2005_skip_missing_summary if row.get("metric") == "alb2005_skip_missing_semantics_rows"), "0")),
        "alb2005_skip_missing_payment_nonmissing_when_not_triggered_rows": safe_int(next((row.get("value", "0") for row in alb2005_skip_missing_summary if row.get("metric") == "alb2005_skip_missing_payment_nonmissing_when_not_triggered_rows"), "0")),
        "alb2005_skip_missing_payment_positive_when_not_triggered_rows": safe_int(next((row.get("value", "0") for row in alb2005_skip_missing_summary if row.get("metric") == "alb2005_skip_missing_payment_positive_when_not_triggered_rows"), "0")),
        "alb2005_skip_missing_payment_zero_or_missing_when_triggered_rows": safe_int(next((row.get("value", "0") for row in alb2005_skip_missing_summary if row.get("metric") == "alb2005_skip_missing_payment_zero_or_missing_when_triggered_rows"), "0")),
        "alb2005_skip_missing_condition_nonmissing_when_not_triggered_rows": safe_int(next((row.get("value", "0") for row in alb2005_skip_missing_summary if row.get("metric") == "alb2005_skip_missing_condition_nonmissing_when_not_triggered_rows"), "0")),
        "alb2005_skip_missing_condition_missing_when_triggered_rows": safe_int(next((row.get("value", "0") for row in alb2005_skip_missing_summary if row.get("metric") == "alb2005_skip_missing_condition_missing_when_triggered_rows"), "0")),
        "alb2005_skip_missing_financing_nonmissing_when_not_triggered_rows": safe_int(next((row.get("value", "0") for row in alb2005_skip_missing_summary if row.get("metric") == "alb2005_skip_missing_financing_nonmissing_when_not_triggered_rows"), "0")),
        "alb2005_skip_missing_financing_missing_when_triggered_rows": safe_int(next((row.get("value", "0") for row in alb2005_skip_missing_summary if row.get("metric") == "alb2005_skip_missing_financing_missing_when_triggered_rows"), "0")),
        "alb2005_skip_missing_recipe_ready_rows": safe_int(next((row.get("value", "0") for row in alb2005_skip_missing_summary if row.get("metric") == "alb2005_skip_missing_recipe_ready_rows"), "0")),
        "alb2005_skip_missing_outcome_ready_rows": safe_int(next((row.get("value", "0") for row in alb2005_skip_missing_summary if row.get("metric") == "alb2005_skip_missing_outcome_ready_rows"), "0")),
        "alb2005_skip_missing_climate_linkage_ready_rows": safe_int(next((row.get("value", "0") for row in alb2005_skip_missing_summary if row.get("metric") == "alb2005_skip_missing_climate_linkage_ready_rows"), "0")),
        "alb2005_consumption_oop_unit_period_audit": row_count(TEMP_DIR / "alb2005_consumption_oop_unit_period_audit.csv"),
        "alb2005_consumption_oop_unit_period_summary": len(alb2005_unit_period_summary),
        "alb2005_consumption_oop_unit_period_rows": safe_int(next((row.get("value", "0") for row in alb2005_unit_period_summary if row.get("metric") == "alb2005_consumption_oop_unit_period_rows"), "0")),
        "alb2005_consumption_oop_unit_period_total_consumption_positive_rows": safe_int(next((row.get("value", "0") for row in alb2005_unit_period_summary if row.get("metric") == "alb2005_consumption_oop_unit_period_total_consumption_positive_rows"), "0")),
        "alb2005_consumption_oop_unit_period_rcons_positive_rows": safe_int(next((row.get("value", "0") for row in alb2005_unit_period_summary if row.get("metric") == "alb2005_consumption_oop_unit_period_rcons_positive_rows"), "0")),
        "alb2005_consumption_oop_unit_period_metadata_old_lek_rows": safe_int(next((row.get("value", "0") for row in alb2005_unit_period_summary if row.get("metric") == "alb2005_consumption_oop_unit_period_metadata_old_lek_rows_observed"), "0")),
        "alb2005_consumption_oop_unit_period_oop_old_lek_rows": safe_int(next((row.get("value", "0") for row in alb2005_unit_period_summary if row.get("metric") == "alb2005_consumption_oop_unit_period_oop_old_lek_questionnaire_rows_observed"), "0")),
        "alb2005_consumption_oop_unit_period_four_week_oop_rows": safe_int(next((row.get("value", "0") for row in alb2005_unit_period_summary if row.get("metric") == "alb2005_consumption_oop_unit_period_four_week_oop_rows_observed"), "0")),
        "alb2005_consumption_oop_unit_period_twelve_month_oop_rows": safe_int(next((row.get("value", "0") for row in alb2005_unit_period_summary if row.get("metric") == "alb2005_consumption_oop_unit_period_twelve_month_oop_rows_observed"), "0")),
        "alb2005_consumption_oop_unit_period_questionnaire_nonfood_old_lek_rows": safe_int(next((row.get("value", "0") for row in alb2005_unit_period_summary if row.get("metric") == "alb2005_consumption_oop_unit_period_questionnaire_nonfood_old_lek_rows_observed"), "0")),
        "alb2005_consumption_oop_unit_period_sdg382_ready_rows": safe_int(next((row.get("value", "0") for row in alb2005_unit_period_summary if row.get("metric") == "alb2005_consumption_oop_unit_period_sdg382_ready_rows"), "0")),
        "alb2005_consumption_oop_unit_period_recipe_ready_rows": safe_int(next((row.get("value", "0") for row in alb2005_unit_period_summary if row.get("metric") == "alb2005_consumption_oop_unit_period_recipe_ready_rows"), "0")),
        "alb2005_consumption_oop_unit_period_outcome_ready_rows": safe_int(next((row.get("value", "0") for row in alb2005_unit_period_summary if row.get("metric") == "alb2005_consumption_oop_unit_period_outcome_ready_rows"), "0")),
        "alb2005_consumption_oop_unit_period_climate_linkage_ready_rows": safe_int(next((row.get("value", "0") for row in alb2005_unit_period_summary if row.get("metric") == "alb2005_consumption_oop_unit_period_climate_linkage_ready_rows"), "0")),
        "alb2005_consumption_oop_unit_period_current_decision": next((row.get("value", "") for row in alb2005_unit_period_summary if row.get("metric") == "alb2005_consumption_oop_unit_period_current_decision"), ""),
        "alb2005_consumption_aggregate_crosswalk_audit": row_count(TEMP_DIR / "alb2005_consumption_aggregate_metadata_crosswalk_audit.csv"),
        "alb2005_consumption_aggregate_crosswalk_summary": len(alb2005_aggregate_crosswalk_summary),
        "alb2005_consumption_aggregate_crosswalk_rows": safe_int(next((row.get("value", "0") for row in alb2005_aggregate_crosswalk_summary if row.get("metric") == "alb2005_consumption_aggregate_crosswalk_rows"), "0")),
        "alb2005_consumption_aggregate_crosswalk_metadata_rows": safe_int(next((row.get("value", "0") for row in alb2005_aggregate_crosswalk_summary if row.get("metric") == "alb2005_consumption_aggregate_crosswalk_metadata_rows"), "0")),
        "alb2005_consumption_aggregate_crosswalk_metadata_old_lek_rows": safe_int(next((row.get("value", "0") for row in alb2005_aggregate_crosswalk_summary if row.get("metric") == "alb2005_consumption_aggregate_crosswalk_metadata_old_lek_rows"), "0")),
        "alb2005_consumption_aggregate_crosswalk_local_poverty_columns": safe_int(next((row.get("value", "0") for row in alb2005_aggregate_crosswalk_summary if row.get("metric") == "alb2005_consumption_aggregate_crosswalk_local_poverty_columns"), "0")),
        "alb2005_consumption_aggregate_crosswalk_metadata_present_local_rows": safe_int(next((row.get("value", "0") for row in alb2005_aggregate_crosswalk_summary if row.get("metric") == "alb2005_consumption_aggregate_crosswalk_metadata_variables_present_in_local_raw_rows"), "0")),
        "alb2005_consumption_aggregate_crosswalk_metadata_absent_local_rows": safe_int(next((row.get("value", "0") for row in alb2005_aggregate_crosswalk_summary if row.get("metric") == "alb2005_consumption_aggregate_crosswalk_metadata_variables_absent_from_local_raw_rows"), "0")),
        "alb2005_consumption_aggregate_crosswalk_local_per_capita_component_rows": safe_int(next((row.get("value", "0") for row in alb2005_aggregate_crosswalk_summary if row.get("metric") == "alb2005_consumption_aggregate_crosswalk_local_per_capita_component_rows"), "0")),
        "alb2005_consumption_aggregate_crosswalk_totcons_positive_rows": safe_int(next((row.get("value", "0") for row in alb2005_aggregate_crosswalk_summary if row.get("metric") == "alb2005_consumption_aggregate_crosswalk_totcons_positive_rows"), "0")),
        "alb2005_consumption_aggregate_crosswalk_totcons05_local_rows": safe_int(next((row.get("value", "0") for row in alb2005_aggregate_crosswalk_summary if row.get("metric") == "alb2005_consumption_aggregate_crosswalk_totcons05_local_rows"), "0")),
        "alb2005_consumption_aggregate_crosswalk_component_formula_reconstructable_rows": safe_int(next((row.get("value", "0") for row in alb2005_aggregate_crosswalk_summary if row.get("metric") == "alb2005_consumption_aggregate_crosswalk_component_formula_reconstructable_rows"), "0")),
        "alb2005_consumption_aggregate_crosswalk_sdg382_ready_rows": safe_int(next((row.get("value", "0") for row in alb2005_aggregate_crosswalk_summary if row.get("metric") == "alb2005_consumption_aggregate_crosswalk_sdg382_ready_rows"), "0")),
        "alb2005_consumption_aggregate_crosswalk_recipe_ready_rows": safe_int(next((row.get("value", "0") for row in alb2005_aggregate_crosswalk_summary if row.get("metric") == "alb2005_consumption_aggregate_crosswalk_recipe_ready_rows"), "0")),
        "alb2005_consumption_aggregate_crosswalk_outcome_ready_rows": safe_int(next((row.get("value", "0") for row in alb2005_aggregate_crosswalk_summary if row.get("metric") == "alb2005_consumption_aggregate_crosswalk_outcome_ready_rows"), "0")),
        "alb2005_consumption_aggregate_crosswalk_climate_linkage_ready_rows": safe_int(next((row.get("value", "0") for row in alb2005_aggregate_crosswalk_summary if row.get("metric") == "alb2005_consumption_aggregate_crosswalk_climate_linkage_ready_rows"), "0")),
        "alb2005_consumption_aggregate_crosswalk_current_decision": next((row.get("value", "") for row in alb2005_aggregate_crosswalk_summary if row.get("metric") == "alb2005_consumption_aggregate_crosswalk_current_decision"), ""),
        "alb2005_consumption_component_source_search_audit": row_count(TEMP_DIR / "alb2005_consumption_component_source_search_audit.csv"),
        "alb2005_consumption_component_source_search_summary": len(alb2005_component_source_summary),
        "alb2005_consumption_component_source_search_rows": safe_int(next((row.get("value", "0") for row in alb2005_component_source_summary if row.get("metric") == "alb2005_consumption_component_source_search_rows"), "0")),
        "alb2005_consumption_component_source_search_target_variables": safe_int(next((row.get("value", "0") for row in alb2005_component_source_summary if row.get("metric") == "alb2005_consumption_component_source_search_target_variables"), "0")),
        "alb2005_consumption_component_source_search_local_files_scanned": safe_int(next((row.get("value", "0") for row in alb2005_component_source_summary if row.get("metric") == "alb2005_consumption_component_source_search_local_files_scanned"), "0")),
        "alb2005_consumption_component_source_search_local_variables_scanned": safe_int(next((row.get("value", "0") for row in alb2005_component_source_summary if row.get("metric") == "alb2005_consumption_component_source_search_local_variables_scanned"), "0")),
        "alb2005_consumption_component_source_search_exact_target_variables_found": safe_int(next((row.get("value", "0") for row in alb2005_component_source_summary if row.get("metric") == "alb2005_consumption_component_source_search_exact_target_variables_found"), "0")),
        "alb2005_consumption_component_source_search_exact_target_variables_missing": safe_int(next((row.get("value", "0") for row in alb2005_component_source_summary if row.get("metric") == "alb2005_consumption_component_source_search_exact_target_variables_missing"), "0")),
        "alb2005_consumption_component_source_search_label_phrase_targets_found": safe_int(next((row.get("value", "0") for row in alb2005_component_source_summary if row.get("metric") == "alb2005_consumption_component_source_search_label_phrase_targets_found"), "0")),
        "alb2005_consumption_component_source_search_questionnaire_phrase_targets_found": safe_int(next((row.get("value", "0") for row in alb2005_component_source_summary if row.get("metric") == "alb2005_consumption_component_source_search_questionnaire_phrase_targets_found"), "0")),
        "alb2005_consumption_component_source_search_construction_code_files_found": safe_int(next((row.get("value", "0") for row in alb2005_component_source_summary if row.get("metric") == "alb2005_consumption_component_source_search_construction_code_files_found"), "0")),
        "alb2005_consumption_component_source_search_construction_code_targets_found": safe_int(next((row.get("value", "0") for row in alb2005_component_source_summary if row.get("metric") == "alb2005_consumption_component_source_search_construction_code_targets_found"), "0")),
        "alb2005_consumption_component_source_search_recipe_ready_rows": safe_int(next((row.get("value", "0") for row in alb2005_component_source_summary if row.get("metric") == "alb2005_consumption_component_source_search_recipe_ready_rows"), "0")),
        "alb2005_consumption_component_source_search_outcome_ready_rows": safe_int(next((row.get("value", "0") for row in alb2005_component_source_summary if row.get("metric") == "alb2005_consumption_component_source_search_outcome_ready_rows"), "0")),
        "alb2005_consumption_component_source_search_sdg382_ready_rows": safe_int(next((row.get("value", "0") for row in alb2005_component_source_summary if row.get("metric") == "alb2005_consumption_component_source_search_sdg382_ready_rows"), "0")),
        "alb2005_consumption_component_source_search_climate_linkage_ready_rows": safe_int(next((row.get("value", "0") for row in alb2005_component_source_summary if row.get("metric") == "alb2005_consumption_component_source_search_climate_linkage_ready_rows"), "0")),
        "alb2005_consumption_component_source_search_current_decision": next((row.get("value", "") for row in alb2005_component_source_summary if row.get("metric") == "alb2005_consumption_component_source_search_current_decision"), ""),
        "alb2005_minimum_recipe_promotion_action_rows": row_count(TEMP_DIR / "alb2005_minimum_recipe_promotion_action_queue.csv"),
        "alb2005_minimum_recipe_promotion_gate_rows": row_count(TEMP_DIR / "alb2005_minimum_recipe_promotion_gate_checklist.csv"),
        "alb2005_minimum_recipe_promotion_summary_rows": len(alb2005_minimum_recipe_summary),
        "alb2005_minimum_recipe_promotion_blocked_gates": safe_int(next((row.get("value", "0") for row in alb2005_minimum_recipe_summary if row.get("metric") == "alb2005_minimum_recipe_promotion_blocked_gates"), "0")),
        "alb2005_minimum_recipe_promotion_candidate_gates": safe_int(next((row.get("value", "0") for row in alb2005_minimum_recipe_summary if row.get("metric") == "alb2005_minimum_recipe_promotion_candidate_gates"), "0")),
        "alb2005_minimum_recipe_promotion_harmonized_ready_rows": safe_int(next((row.get("value", "0") for row in alb2005_minimum_recipe_summary if row.get("metric") == "alb2005_minimum_recipe_promotion_harmonized_ready_rows"), "0")),
        "alb2005_minimum_recipe_promotion_outcome_ready_rows": safe_int(next((row.get("value", "0") for row in alb2005_minimum_recipe_summary if row.get("metric") == "alb2005_minimum_recipe_promotion_outcome_ready_rows"), "0")),
        "alb2005_minimum_recipe_promotion_climate_linkage_ready_rows": safe_int(next((row.get("value", "0") for row in alb2005_minimum_recipe_summary if row.get("metric") == "alb2005_minimum_recipe_promotion_climate_linkage_ready_rows"), "0")),
        "alb2005_minimum_recipe_promotion_current_decision": next((row.get("value", "") for row in alb2005_minimum_recipe_summary if row.get("metric") == "alb2005_minimum_recipe_promotion_current_decision"), ""),
        "alb2005_public_fieldwork_geo_metadata_audit": row_count(TEMP_DIR / "alb2005_public_fieldwork_geo_metadata_audit.csv"),
        "alb2005_public_fieldwork_geo_metadata_summary": len(alb2005_public_fieldwork_geo_summary),
        "alb2005_public_fieldwork_geo_metadata_evidence_rows": safe_int(next((row.get("value", "0") for row in alb2005_public_fieldwork_geo_summary if row.get("metric") == "alb2005_public_fieldwork_geo_metadata_evidence_rows"), "0")),
        "alb2005_public_fieldwork_geo_metadata_verified_source_rows": safe_int(next((row.get("value", "0") for row in alb2005_public_fieldwork_geo_summary if row.get("metric") == "alb2005_public_fieldwork_geo_metadata_verified_source_rows"), "0")),
        "alb2005_public_fieldwork_geo_metadata_source_missing_rows": safe_int(next((row.get("value", "0") for row in alb2005_public_fieldwork_geo_summary if row.get("metric") == "alb2005_public_fieldwork_geo_metadata_source_missing_rows"), "0")),
        "alb2005_public_fieldwork_geo_metadata_fieldwork_period_evidence_rows": safe_int(next((row.get("value", "0") for row in alb2005_public_fieldwork_geo_summary if row.get("metric") == "alb2005_public_fieldwork_geo_metadata_fieldwork_period_evidence_rows"), "0")),
        "alb2005_public_fieldwork_geo_metadata_gps_claim_rows": safe_int(next((row.get("value", "0") for row in alb2005_public_fieldwork_geo_summary if row.get("metric") == "alb2005_public_fieldwork_geo_metadata_gps_claim_rows"), "0")),
        "alb2005_public_fieldwork_geo_metadata_sampling_geo_rows": safe_int(next((row.get("value", "0") for row in alb2005_public_fieldwork_geo_summary if row.get("metric") == "alb2005_public_fieldwork_geo_metadata_sampling_geo_rows"), "0")),
        "alb2005_public_fieldwork_geo_metadata_household_timing_verified_rows": safe_int(next((row.get("value", "0") for row in alb2005_public_fieldwork_geo_summary if row.get("metric") == "alb2005_public_fieldwork_geo_metadata_household_timing_verified_rows"), "0")),
        "alb2005_public_fieldwork_geo_metadata_raw_coordinate_value_rows": safe_int(next((row.get("value", "0") for row in alb2005_public_fieldwork_geo_summary if row.get("metric") == "alb2005_public_fieldwork_geo_metadata_raw_coordinate_value_rows"), "0")),
        "alb2005_public_fieldwork_geo_metadata_climate_linkage_ready_rows": safe_int(next((row.get("value", "0") for row in alb2005_public_fieldwork_geo_summary if row.get("metric") == "alb2005_public_fieldwork_geo_metadata_climate_linkage_ready_rows"), "0")),
        "alb2005_public_fieldwork_geo_metadata_current_decision": next((row.get("value", "") for row in alb2005_public_fieldwork_geo_summary if row.get("metric") == "alb2005_public_fieldwork_geo_metadata_current_decision"), ""),
        "alb2005_diary_timing_candidate_audit": row_count(TEMP_DIR / "alb2005_diary_timing_candidate_audit.csv"),
        "alb2005_diary_timing_candidate_summary": len(alb2005_diary_timing_summary),
        "alb2005_diary_timing_candidate_audit_rows": safe_int(next((row.get("value", "0") for row in alb2005_diary_timing_summary if row.get("metric") == "alb2005_diary_timing_candidate_audit_rows"), "0")),
        "alb2005_diary_timing_candidate_metadata_found_rows": safe_int(next((row.get("value", "0") for row in alb2005_diary_timing_summary if row.get("metric") == "alb2005_diary_timing_candidate_metadata_found_rows"), "0")),
        "alb2005_diary_timing_candidate_schema_file_rows": safe_int(next((row.get("value", "0") for row in alb2005_diary_timing_summary if row.get("metric") == "alb2005_diary_timing_candidate_schema_file_rows"), "0")),
        "alb2005_diary_timing_candidate_raw_bookmetadata_files_present": safe_int(next((row.get("value", "0") for row in alb2005_diary_timing_summary if row.get("metric") == "alb2005_diary_timing_candidate_raw_bookmetadata_files_present"), "0")),
        "alb2005_diary_timing_candidate_key_candidate_rows": safe_int(next((row.get("value", "0") for row in alb2005_diary_timing_summary if row.get("metric") == "alb2005_diary_timing_candidate_key_candidate_rows"), "0")),
        "alb2005_diary_timing_candidate_date_candidate_rows": safe_int(next((row.get("value", "0") for row in alb2005_diary_timing_summary if row.get("metric") == "alb2005_diary_timing_candidate_date_candidate_rows"), "0")),
        "alb2005_diary_timing_candidate_household_timing_promoted_rows": safe_int(next((row.get("value", "0") for row in alb2005_diary_timing_summary if row.get("metric") == "alb2005_diary_timing_candidate_household_timing_promoted_rows"), "0")),
        "alb2005_diary_timing_candidate_climate_linkage_ready_rows": safe_int(next((row.get("value", "0") for row in alb2005_diary_timing_summary if row.get("metric") == "alb2005_diary_timing_candidate_climate_linkage_ready_rows"), "0")),
        "alb2005_diary_timing_candidate_current_decision": next((row.get("value", "") for row in alb2005_diary_timing_summary if row.get("metric") == "alb2005_diary_timing_candidate_current_decision"), ""),
        "alb2005_extracted_module_coverage_audit": row_count(TEMP_DIR / "alb2005_extracted_module_coverage_audit.csv"),
        "alb2005_extracted_extra_files_audit": row_count(TEMP_DIR / "alb2005_extracted_extra_files_audit.csv"),
        "alb2005_archive_member_manifest": row_count(TEMP_DIR / "alb2005_archive_member_manifest.csv"),
        "alb2005_extracted_module_coverage_summary": len(alb2005_extracted_module_summary),
        "alb2005_extracted_module_coverage_ddi_module_rows": safe_int(next((row.get("value", "0") for row in alb2005_extracted_module_summary if row.get("metric") == "alb2005_extracted_module_coverage_ddi_module_rows"), "0")),
        "alb2005_archive_member_rows": safe_int(next((row.get("value", "0") for row in alb2005_extracted_module_summary if row.get("metric") == "alb2005_archive_member_rows"), "0")),
        "alb2005_archive_sav_member_rows": safe_int(next((row.get("value", "0") for row in alb2005_extracted_module_summary if row.get("metric") == "alb2005_archive_sav_member_rows"), "0")),
        "alb2005_archive_questionnaire_member_rows": safe_int(next((row.get("value", "0") for row in alb2005_extracted_module_summary if row.get("metric") == "alb2005_archive_questionnaire_member_rows"), "0")),
        "alb2005_archive_ddi_module_present_rows": safe_int(next((row.get("value", "0") for row in alb2005_extracted_module_summary if row.get("metric") == "alb2005_archive_ddi_module_present_rows"), "0")),
        "alb2005_archive_ddi_module_absent_rows": safe_int(next((row.get("value", "0") for row in alb2005_extracted_module_summary if row.get("metric") == "alb2005_archive_ddi_module_absent_rows"), "0")),
        "alb2005_archive_critical_module_absent_rows": safe_int(next((row.get("value", "0") for row in alb2005_extracted_module_summary if row.get("metric") == "alb2005_archive_critical_module_absent_rows"), "0")),
        "alb2005_archive_listing_status": next((row.get("value", "") for row in alb2005_extracted_module_summary if row.get("metric") == "alb2005_archive_listing_status"), ""),
        "alb2005_extracted_module_coverage_present_rows": safe_int(next((row.get("value", "0") for row in alb2005_extracted_module_summary if row.get("metric") == "alb2005_extracted_module_coverage_present_rows"), "0")),
        "alb2005_extracted_module_coverage_missing_rows": safe_int(next((row.get("value", "0") for row in alb2005_extracted_module_summary if row.get("metric") == "alb2005_extracted_module_coverage_missing_rows"), "0")),
        "alb2005_extracted_module_coverage_extracted_file_rows": safe_int(next((row.get("value", "0") for row in alb2005_extracted_module_summary if row.get("metric") == "alb2005_extracted_module_coverage_extracted_file_rows"), "0")),
        "alb2005_extracted_module_coverage_bookmetadata_missing_rows": safe_int(next((row.get("value", "0") for row in alb2005_extracted_module_summary if row.get("metric") == "alb2005_extracted_module_coverage_bookmetadata_missing_rows"), "0")),
        "alb2005_extracted_module_coverage_food_diary_missing_rows": safe_int(next((row.get("value", "0") for row in alb2005_extracted_module_summary if row.get("metric") == "alb2005_extracted_module_coverage_food_diary_missing_rows"), "0")),
        "alb2005_extracted_module_coverage_critical_missing_rows": safe_int(next((row.get("value", "0") for row in alb2005_extracted_module_summary if row.get("metric") == "alb2005_extracted_module_coverage_critical_missing_rows"), "0")),
        "alb2005_extracted_module_coverage_coordinate_metadata_variable_rows": safe_int(next((row.get("value", "0") for row in alb2005_extracted_module_summary if row.get("metric") == "alb2005_extracted_module_coverage_coordinate_metadata_variable_rows"), "0")),
        "alb2005_extracted_module_coverage_coordinate_extracted_file_rows": safe_int(next((row.get("value", "0") for row in alb2005_extracted_module_summary if row.get("metric") == "alb2005_extracted_module_coverage_coordinate_extracted_file_rows"), "0")),
        "alb2005_extracted_module_coverage_harmonized_ready_rows": safe_int(next((row.get("value", "0") for row in alb2005_extracted_module_summary if row.get("metric") == "alb2005_extracted_module_coverage_harmonized_ready_rows"), "0")),
        "alb2005_extracted_module_coverage_household_timing_ready_rows": safe_int(next((row.get("value", "0") for row in alb2005_extracted_module_summary if row.get("metric") == "alb2005_extracted_module_coverage_household_timing_ready_rows"), "0")),
        "alb2005_extracted_module_coverage_climate_linkage_ready_rows": safe_int(next((row.get("value", "0") for row in alb2005_extracted_module_summary if row.get("metric") == "alb2005_extracted_module_coverage_climate_linkage_ready_rows"), "0")),
        "alb2005_extracted_module_coverage_current_decision": next((row.get("value", "") for row in alb2005_extracted_module_summary if row.get("metric") == "alb2005_extracted_module_coverage_current_decision"), ""),
        "alb2005_fallback_blocker_resolution_matrix": row_count(TEMP_DIR / "alb2005_fallback_blocker_resolution_matrix.csv"),
        "alb2005_fallback_blocker_resolution_summary": len(alb2005_fallback_blocker_summary),
        "alb2005_fallback_blocker_resolution_rows": safe_int(next((row.get("value", "0") for row in alb2005_fallback_blocker_summary if row.get("metric") == "alb2005_fallback_blocker_resolution_rows"), "0")),
        "alb2005_fallback_blocker_raw_package_rows": safe_int(next((row.get("value", "0") for row in alb2005_fallback_blocker_summary if row.get("metric") == "alb2005_fallback_blocker_raw_package_rows"), "0")),
        "alb2005_fallback_blocker_timing_rows": safe_int(next((row.get("value", "0") for row in alb2005_fallback_blocker_summary if row.get("metric") == "alb2005_fallback_blocker_timing_rows"), "0")),
        "alb2005_fallback_blocker_geography_rows": safe_int(next((row.get("value", "0") for row in alb2005_fallback_blocker_summary if row.get("metric") == "alb2005_fallback_blocker_geography_rows"), "0")),
        "alb2005_fallback_blocker_outcome_rows": safe_int(next((row.get("value", "0") for row in alb2005_fallback_blocker_summary if row.get("metric") == "alb2005_fallback_blocker_outcome_rows"), "0")),
        "alb2005_fallback_blocker_promotion_gate_rows": safe_int(next((row.get("value", "0") for row in alb2005_fallback_blocker_summary if row.get("metric") == "alb2005_fallback_blocker_promotion_gate_rows"), "0")),
        "alb2005_fallback_blocker_hard_blocked_rows": safe_int(next((row.get("value", "0") for row in alb2005_fallback_blocker_summary if row.get("metric") == "alb2005_fallback_blocker_hard_blocked_rows"), "0")),
        "alb2005_fallback_blocker_harmonized_ready_rows": safe_int(next((row.get("value", "0") for row in alb2005_fallback_blocker_summary if row.get("metric") == "alb2005_fallback_blocker_harmonized_ready_rows"), "0")),
        "alb2005_fallback_blocker_outcome_ready_rows": safe_int(next((row.get("value", "0") for row in alb2005_fallback_blocker_summary if row.get("metric") == "alb2005_fallback_blocker_outcome_ready_rows"), "0")),
        "alb2005_fallback_blocker_interview_timing_ready_rows": safe_int(next((row.get("value", "0") for row in alb2005_fallback_blocker_summary if row.get("metric") == "alb2005_fallback_blocker_interview_timing_ready_rows"), "0")),
        "alb2005_fallback_blocker_geography_ready_rows": safe_int(next((row.get("value", "0") for row in alb2005_fallback_blocker_summary if row.get("metric") == "alb2005_fallback_blocker_geography_ready_rows"), "0")),
        "alb2005_fallback_blocker_climate_linkage_ready_rows": safe_int(next((row.get("value", "0") for row in alb2005_fallback_blocker_summary if row.get("metric") == "alb2005_fallback_blocker_climate_linkage_ready_rows"), "0")),
        "alb2005_fallback_blocker_data_write_ready_rows": safe_int(next((row.get("value", "0") for row in alb2005_fallback_blocker_summary if row.get("metric") == "alb2005_fallback_blocker_data_write_ready_rows"), "0")),
        "alb2005_fallback_blocker_current_decision": next((row.get("value", "") for row in alb2005_fallback_blocker_summary if row.get("metric") == "alb2005_fallback_blocker_current_decision"), ""),
        "albania_first_analysis_promotion_gate_checklist": row_count(TEMP_DIR / "albania_first_analysis_promotion_gate_checklist.csv"),
        "albania_first_analysis_promotion_action_queue": row_count(TEMP_DIR / "albania_first_analysis_promotion_action_queue.csv"),
        "albania_first_analysis_promotion_wave_ranking": row_count(RESULT_DIR / "albania_first_analysis_promotion_wave_ranking.csv"),
        "albania_first_analysis_promotion_summary": len(albania_first_analysis_summary),
        "albania_first_analysis_promotion_wave_rows": safe_int(next((row.get("value", "0") for row in albania_first_analysis_summary if row.get("metric") == "albania_first_analysis_promotion_wave_rows"), "0")),
        "albania_first_analysis_promotion_gate_rows": safe_int(next((row.get("value", "0") for row in albania_first_analysis_summary if row.get("metric") == "albania_first_analysis_promotion_gate_rows"), "0")),
        "albania_first_analysis_promotion_blocked_gate_rows": safe_int(next((row.get("value", "0") for row in albania_first_analysis_summary if row.get("metric") == "albania_first_analysis_promotion_blocked_gate_rows"), "0")),
        "albania_first_analysis_promotion_ready_wave_rows": safe_int(next((row.get("value", "0") for row in albania_first_analysis_summary if row.get("metric") == "albania_first_analysis_promotion_ready_wave_rows"), "0")),
        "albania_first_analysis_promotion_harmonized_ready_rows": safe_int(next((row.get("value", "0") for row in albania_first_analysis_summary if row.get("metric") == "albania_first_analysis_promotion_harmonized_ready_rows"), "0")),
        "albania_first_analysis_promotion_outcome_ready_rows": safe_int(next((row.get("value", "0") for row in albania_first_analysis_summary if row.get("metric") == "albania_first_analysis_promotion_outcome_ready_rows"), "0")),
        "albania_first_analysis_promotion_climate_linkage_ready_rows": safe_int(next((row.get("value", "0") for row in albania_first_analysis_summary if row.get("metric") == "albania_first_analysis_promotion_climate_linkage_ready_rows"), "0")),
        "albania_first_analysis_promotion_current_decision": next((row.get("value", "") for row in albania_first_analysis_summary if row.get("metric") == "albania_first_analysis_promotion_current_decision"), ""),
        "albania_existing_raw_wave_audit": row_count(TEMP_DIR / "albania_existing_raw_wave_audit.csv"),
        "albania_existing_raw_wave_audit_summary": len(albania_wave_summary),
        "albania_existing_raw_wave_harmonization_ready_rows": safe_int(next((row.get("value", "0") for row in albania_wave_summary if row.get("metric") == "albania_existing_raw_wave_harmonization_ready_rows"), "0")),
        "albania_existing_raw_wave_climate_linkage_ready_rows": safe_int(next((row.get("value", "0") for row in albania_wave_summary if row.get("metric") == "albania_existing_raw_wave_climate_linkage_ready_rows"), "0")),
        "alb2008_household_core_candidate": row_count(TEMP_DIR / "alb2008_household_core_candidate.csv"),
        "alb2008_household_core_merge_audit": row_count(TEMP_DIR / "alb2008_household_core_merge_audit.csv"),
        "alb2008_household_core_lineage": row_count(TEMP_DIR / "alb2008_household_core_lineage.csv"),
        "alb2008_household_core_candidate_summary": len(alb2008_core_summary),
        "alb2008_household_core_recipe_ready_rows": safe_int(next((row.get("value", "0") for row in alb2008_core_summary if row.get("metric") == "alb2008_household_core_recipe_ready_rows"), "0")),
        "alb2008_provisional_outcome_feasibility_audit": row_count(TEMP_DIR / "alb2008_provisional_outcome_feasibility_audit.csv"),
        "alb2008_provisional_outcome_feasibility_summary": len(alb2008_outcome_summary),
        "alb2008_provisional_outcome_ready_rows": safe_int(next((row.get("value", "0") for row in alb2008_outcome_summary if row.get("metric") == "alb2008_provisional_outcome_ready_rows"), "0")),
        "alb2008_outcome_semantics_raw_value_audit": row_count(TEMP_DIR / "alb2008_outcome_semantics_raw_value_audit.csv"),
        "alb2008_outcome_semantics_raw_value_summary": len(alb2008_semantics_summary),
        "alb2008_outcome_semantics_outcome_ready_rows": safe_int(next((row.get("value", "0") for row in alb2008_semantics_summary if row.get("metric") == "alb2008_outcome_semantics_outcome_ready_rows"), "0")),
        "alb2008_outcome_semantics_sdg382_ready_rows": safe_int(next((row.get("value", "0") for row in alb2008_semantics_summary if row.get("metric") == "alb2008_outcome_semantics_sdg382_ready_rows"), "0")),
        "alb2008_outcome_semantics_climate_linkage_ready_rows": safe_int(next((row.get("value", "0") for row in alb2008_semantics_summary if row.get("metric") == "alb2008_outcome_semantics_climate_linkage_ready_rows"), "0")),
        "alb2008_outcome_semantics_financial_oop_candidate_rows": safe_int(next((row.get("value", "0") for row in alb2008_semantics_summary if row.get("metric") == "alb2008_outcome_semantics_financial_oop_candidate_rows"), "0")),
        "alb2008_outcome_semantics_gift_candidate_rows": safe_int(next((row.get("value", "0") for row in alb2008_semantics_summary if row.get("metric") == "alb2008_outcome_semantics_gift_candidate_rows"), "0")),
        "alb2008_outcome_semantics_access_candidate_rows": safe_int(next((row.get("value", "0") for row in alb2008_semantics_summary if row.get("metric") == "alb2008_outcome_semantics_access_candidate_rows"), "0")),
        "alb2008_outcome_semantics_facility_proxy_rows": safe_int(next((row.get("value", "0") for row in alb2008_semantics_summary if row.get("metric") == "alb2008_outcome_semantics_facility_proxy_rows"), "0")),
        "alb2008_outcome_semantics_conditional_reason_rows": safe_int(next((row.get("value", "0") for row in alb2008_semantics_summary if row.get("metric") == "alb2008_outcome_semantics_conditional_reason_rows"), "0")),
        "alb2008_timing_geography_exhaustive_audit": row_count(TEMP_DIR / "alb2008_timing_geography_exhaustive_audit.csv"),
        "alb2008_timing_geography_exhaustive_summary": len(alb2008_timing_geo_summary),
        "alb2008_climate_linkage_ready_rows": safe_int(next((row.get("value", "0") for row in alb2008_timing_geo_summary if row.get("metric") == "alb2008_climate_linkage_ready_rows"), "0")),
        "alb2008_fallback_blocker_resolution_matrix": row_count(TEMP_DIR / "alb2008_fallback_blocker_resolution_matrix.csv"),
        "alb2008_fallback_blocker_resolution_summary": len(alb2008_fallback_blocker_summary),
        "alb2008_fallback_blocker_resolution_rows": safe_int(next((row.get("value", "0") for row in alb2008_fallback_blocker_summary if row.get("metric") == "alb2008_fallback_blocker_resolution_rows"), "0")),
        "alb2008_fallback_blocker_timing_rows": safe_int(next((row.get("value", "0") for row in alb2008_fallback_blocker_summary if row.get("metric") == "alb2008_fallback_blocker_timing_rows"), "0")),
        "alb2008_fallback_blocker_geography_rows": safe_int(next((row.get("value", "0") for row in alb2008_fallback_blocker_summary if row.get("metric") == "alb2008_fallback_blocker_geography_rows"), "0")),
        "alb2008_fallback_blocker_outcome_rows": safe_int(next((row.get("value", "0") for row in alb2008_fallback_blocker_summary if row.get("metric") == "alb2008_fallback_blocker_outcome_rows"), "0")),
        "alb2008_fallback_blocker_promotion_gate_rows": safe_int(next((row.get("value", "0") for row in alb2008_fallback_blocker_summary if row.get("metric") == "alb2008_fallback_blocker_promotion_gate_rows"), "0")),
        "alb2008_fallback_blocker_hard_blocked_rows": safe_int(next((row.get("value", "0") for row in alb2008_fallback_blocker_summary if row.get("metric") == "alb2008_fallback_blocker_hard_blocked_rows"), "0")),
        "alb2008_fallback_blocker_interview_timing_ready_rows": safe_int(next((row.get("value", "0") for row in alb2008_fallback_blocker_summary if row.get("metric") == "alb2008_fallback_blocker_interview_timing_ready_rows"), "0")),
        "alb2008_fallback_blocker_geography_ready_rows": safe_int(next((row.get("value", "0") for row in alb2008_fallback_blocker_summary if row.get("metric") == "alb2008_fallback_blocker_geography_ready_rows"), "0")),
        "alb2008_fallback_blocker_outcome_ready_rows": safe_int(next((row.get("value", "0") for row in alb2008_fallback_blocker_summary if row.get("metric") == "alb2008_fallback_blocker_outcome_ready_rows"), "0")),
        "alb2008_fallback_blocker_climate_linkage_ready_rows": safe_int(next((row.get("value", "0") for row in alb2008_fallback_blocker_summary if row.get("metric") == "alb2008_fallback_blocker_climate_linkage_ready_rows"), "0")),
        "alb2008_fallback_blocker_data_write_ready_rows": safe_int(next((row.get("value", "0") for row in alb2008_fallback_blocker_summary if row.get("metric") == "alb2008_fallback_blocker_data_write_ready_rows"), "0")),
        "alb2008_fallback_blocker_current_decision": next((row.get("value", "") for row in alb2008_fallback_blocker_summary if row.get("metric") == "alb2008_fallback_blocker_current_decision"), ""),
        "first_batch_dataset_verification_gate": row_count(RESULT_DIR / "first_batch_dataset_verification_gate.csv"),
        "first_batch_concept_verification_template": row_count(TEMP_DIR / "first_batch_concept_verification_template.csv"),
        "first_batch_variable_verification_template": row_count(TEMP_DIR / "first_batch_variable_verification_template.csv"),
        "first_batch_raw_verification_workbook_summary": row_count(RESULT_DIR / "first_batch_raw_verification_workbook_summary.csv"),
        "first_batch_datasets_ready_for_value_audit": count_status(RESULT_DIR / "first_batch_dataset_verification_gate.csv", "current_gate_status", "ready_for_manual_value_label_unit_key_audit"),
        "direct_read_bundle": row_count(RESULT_DIR / "direct_read_audit_bundle.csv"),
        "direct_read_manifest": row_count(RESULT_DIR / "direct_read_artifact_manifest.csv"),
        "direct_read_summary": row_count(RESULT_DIR / "direct_read_audit_bundle_summary.csv"),
        "direct_read_manifest_present": count_status(RESULT_DIR / "direct_read_artifact_manifest.csv", "current_status", "present_nonempty"),
        "direct_read_manifest_missing": sum(1 for row in read_csv_dicts(RESULT_DIR / "direct_read_artifact_manifest.csv") if row.get("current_status") != "present_nonempty"),
        "validation_reference_probe": row_count(TEMP_DIR / "validation_reference_source_probe.csv"),
        "validation_reference_samples": row_count(TEMP_DIR / "validation_reference_indicator_sample.csv"),
        "hefpi_uhc_series": row_count(TEMP_DIR / "hefpi_uhc_series_catalog.csv"),
        "hefpi_uhc_reference": row_count(TEMP_DIR / "hefpi_uhc_reference_sample.csv"),
        "design_scorecard": row_count(RESULT_DIR / "design_scorecard.csv"),
        "design_scorecard_current_audit": row_count(RESULT_DIR / "design_scorecard_current_audit.csv"),
        "design_no_go_threshold_audit": row_count(RESULT_DIR / "design_no_go_threshold_audit.csv"),
        "design_scorecard_current_summary": len(design_scorecard_current_summary),
        "design_scorecard_rows": safe_int(next((row.get("value", "0") for row in design_scorecard_current_summary if row.get("metric") == "design_scorecard_rows"), "0")),
        "design_scorecard_current_rows": safe_int(next((row.get("value", "0") for row in design_scorecard_current_summary if row.get("metric") == "design_scorecard_current_rows"), "0")),
        "design_scorecard_audit_rows": safe_int(next((row.get("value", "0") for row in design_scorecard_current_summary if row.get("metric") == "design_scorecard_audit_rows"), "0")),
        "design_no_go_threshold_rows": safe_int(next((row.get("value", "0") for row in design_scorecard_current_summary if row.get("metric") == "design_no_go_threshold_rows"), "0")),
        "design_no_go_failed_or_not_estimable_rows": safe_int(next((row.get("value", "0") for row in design_scorecard_current_summary if row.get("metric") == "design_no_go_failed_or_not_estimable_rows"), "0")),
        "design_scorecard_data_write_ready_rows": safe_int(next((row.get("value", "0") for row in design_scorecard_current_summary if row.get("metric") == "design_scorecard_data_write_ready_rows"), "0")),
        "design_scorecard_current_decision": next((row.get("value", "") for row in design_scorecard_current_summary if row.get("metric") == "design_scorecard_current_decision"), ""),
        "alb2002_promotion_gate_delta_audit": row_count(TEMP_DIR / "alb2002_promotion_gate_delta_audit.csv"),
        "alb2002_promotion_gate_delta_summary": len(alb2002_promotion_gate_delta_summary),
        "alb2002_promotion_gate_delta_rows": safe_int(next((row.get("value", "0") for row in alb2002_promotion_gate_delta_summary if row.get("metric") == "alb2002_promotion_gate_delta_rows"), "0")),
        "alb2002_promotion_gate_delta_review_ready_rows": safe_int(next((row.get("value", "0") for row in alb2002_promotion_gate_delta_summary if row.get("metric") == "alb2002_promotion_gate_delta_review_ready_rows"), "0")),
        "alb2002_promotion_gate_delta_documented_candidate_rows": safe_int(next((row.get("value", "0") for row in alb2002_promotion_gate_delta_summary if row.get("metric") == "alb2002_promotion_gate_delta_documented_candidate_rows"), "0")),
        "alb2002_promotion_gate_delta_hard_blocked_rows": safe_int(next((row.get("value", "0") for row in alb2002_promotion_gate_delta_summary if row.get("metric") == "alb2002_promotion_gate_delta_hard_blocked_rows"), "0")),
        "alb2002_promotion_gate_delta_promotion_ready_rows": safe_int(next((row.get("value", "0") for row in alb2002_promotion_gate_delta_summary if row.get("metric") == "alb2002_promotion_gate_delta_promotion_ready_rows"), "0")),
        "alb2002_promotion_gate_delta_data_write_ready_rows": safe_int(next((row.get("value", "0") for row in alb2002_promotion_gate_delta_summary if row.get("metric") == "alb2002_promotion_gate_delta_data_write_ready_rows"), "0")),
        "alb2002_promotion_gate_delta_decision": next((row.get("value", "") for row in alb2002_promotion_gate_delta_summary if row.get("metric") == "alb2002_promotion_gate_delta_decision"), ""),
        "alb2002_boundary_blocker_resolution_matrix": row_count(TEMP_DIR / "alb2002_boundary_blocker_resolution_matrix.csv"),
        "alb2002_boundary_blocker_resolution_summary": len(alb2002_boundary_blocker_summary),
        "alb2002_boundary_blocker_resolution_rows": safe_int(next((row.get("value", "0") for row in alb2002_boundary_blocker_summary if row.get("metric") == "alb2002_boundary_blocker_resolution_rows"), "0")),
        "alb2002_boundary_blocker_official_or_primary_lead_rows": safe_int(next((row.get("value", "0") for row in alb2002_boundary_blocker_summary if row.get("metric") == "alb2002_boundary_blocker_official_or_primary_lead_rows"), "0")),
        "alb2002_boundary_blocker_candidate_name_coverage_rows": safe_int(next((row.get("value", "0") for row in alb2002_boundary_blocker_summary if row.get("metric") == "alb2002_boundary_blocker_candidate_name_coverage_rows"), "0")),
        "alb2002_boundary_blocker_incompatible_or_negative_rows": safe_int(next((row.get("value", "0") for row in alb2002_boundary_blocker_summary if row.get("metric") == "alb2002_boundary_blocker_incompatible_or_negative_rows"), "0")),
        "alb2002_boundary_blocker_historical_2002_ready_rows": safe_int(next((row.get("value", "0") for row in alb2002_boundary_blocker_summary if row.get("metric") == "alb2002_boundary_blocker_historical_2002_ready_rows"), "0")),
        "alb2002_boundary_blocker_climate_linkage_ready_rows": safe_int(next((row.get("value", "0") for row in alb2002_boundary_blocker_summary if row.get("metric") == "alb2002_boundary_blocker_climate_linkage_ready_rows"), "0")),
        "alb2002_boundary_blocker_data_write_ready_rows": safe_int(next((row.get("value", "0") for row in alb2002_boundary_blocker_summary if row.get("metric") == "alb2002_boundary_blocker_data_write_ready_rows"), "0")),
        "alb2002_boundary_blocker_hard_blocked_rows": safe_int(next((row.get("value", "0") for row in alb2002_boundary_blocker_summary if row.get("metric") == "alb2002_boundary_blocker_hard_blocked_rows"), "0")),
        "alb2002_boundary_blocker_required_source_action_rows": safe_int(next((row.get("value", "0") for row in alb2002_boundary_blocker_summary if row.get("metric") == "alb2002_boundary_blocker_required_source_action_rows"), "0")),
        "alb2002_boundary_blocker_current_decision": next((row.get("value", "") for row in alb2002_boundary_blocker_summary if row.get("metric") == "alb2002_boundary_blocker_current_decision"), ""),
        "alb2002_outcome_blocker_resolution_matrix": row_count(TEMP_DIR / "alb2002_outcome_blocker_resolution_matrix.csv"),
        "alb2002_outcome_blocker_resolution_summary": len(alb2002_outcome_blocker_summary),
        "alb2002_outcome_blocker_resolution_rows": safe_int(next((row.get("value", "0") for row in alb2002_outcome_blocker_summary if row.get("metric") == "alb2002_outcome_blocker_resolution_rows"), "0")),
        "alb2002_outcome_blocker_financial_rows": safe_int(next((row.get("value", "0") for row in alb2002_outcome_blocker_summary if row.get("metric") == "alb2002_outcome_blocker_financial_rows"), "0")),
        "alb2002_outcome_blocker_access_rows": safe_int(next((row.get("value", "0") for row in alb2002_outcome_blocker_summary if row.get("metric") == "alb2002_outcome_blocker_access_rows"), "0")),
        "alb2002_outcome_blocker_composite_rows": safe_int(next((row.get("value", "0") for row in alb2002_outcome_blocker_summary if row.get("metric") == "alb2002_outcome_blocker_composite_rows"), "0")),
        "alb2002_outcome_blocker_candidate_not_promoted_rows": safe_int(next((row.get("value", "0") for row in alb2002_outcome_blocker_summary if row.get("metric") == "alb2002_outcome_blocker_candidate_not_promoted_rows"), "0")),
        "alb2002_outcome_blocker_low_event_candidate_rows": safe_int(next((row.get("value", "0") for row in alb2002_outcome_blocker_summary if row.get("metric") == "alb2002_outcome_blocker_low_event_candidate_rows"), "0")),
        "alb2002_outcome_blocker_hard_blocked_rows": safe_int(next((row.get("value", "0") for row in alb2002_outcome_blocker_summary if row.get("metric") == "alb2002_outcome_blocker_hard_blocked_rows"), "0")),
        "alb2002_outcome_blocker_outcome_ready_rows": safe_int(next((row.get("value", "0") for row in alb2002_outcome_blocker_summary if row.get("metric") == "alb2002_outcome_blocker_outcome_ready_rows"), "0")),
        "alb2002_outcome_blocker_sdg382_ready_rows": safe_int(next((row.get("value", "0") for row in alb2002_outcome_blocker_summary if row.get("metric") == "alb2002_outcome_blocker_sdg382_ready_rows"), "0")),
        "alb2002_outcome_blocker_climate_linkage_ready_rows": safe_int(next((row.get("value", "0") for row in alb2002_outcome_blocker_summary if row.get("metric") == "alb2002_outcome_blocker_climate_linkage_ready_rows"), "0")),
        "alb2002_outcome_blocker_data_write_ready_rows": safe_int(next((row.get("value", "0") for row in alb2002_outcome_blocker_summary if row.get("metric") == "alb2002_outcome_blocker_data_write_ready_rows"), "0")),
        "alb2002_outcome_blocker_current_decision": next((row.get("value", "") for row in alb2002_outcome_blocker_summary if row.get("metric") == "alb2002_outcome_blocker_current_decision"), ""),
        "alb2012_timing_geography_blocker_resolution_matrix": row_count(TEMP_DIR / "alb2012_timing_geography_blocker_resolution_matrix.csv"),
        "alb2012_timing_geography_blocker_resolution_summary": len(alb2012_blocker_summary),
        "alb2012_timing_geography_blocker_resolution_rows": safe_int(next((row.get("value", "0") for row in alb2012_blocker_summary if row.get("metric") == "alb2012_timing_geography_blocker_resolution_rows"), "0")),
        "alb2012_timing_geography_blocker_timing_rows": safe_int(next((row.get("value", "0") for row in alb2012_blocker_summary if row.get("metric") == "alb2012_timing_geography_blocker_timing_rows"), "0")),
        "alb2012_timing_geography_blocker_geography_rows": safe_int(next((row.get("value", "0") for row in alb2012_blocker_summary if row.get("metric") == "alb2012_timing_geography_blocker_geography_rows"), "0")),
        "alb2012_timing_geography_blocker_outcome_rows": safe_int(next((row.get("value", "0") for row in alb2012_blocker_summary if row.get("metric") == "alb2012_timing_geography_blocker_outcome_rows"), "0")),
        "alb2012_timing_geography_blocker_promotion_gate_rows": safe_int(next((row.get("value", "0") for row in alb2012_blocker_summary if row.get("metric") == "alb2012_timing_geography_blocker_promotion_gate_rows"), "0")),
        "alb2012_timing_geography_blocker_hard_blocked_rows": safe_int(next((row.get("value", "0") for row in alb2012_blocker_summary if row.get("metric") == "alb2012_timing_geography_blocker_hard_blocked_rows"), "0")),
        "alb2012_timing_geography_blocker_interview_timing_ready_rows": safe_int(next((row.get("value", "0") for row in alb2012_blocker_summary if row.get("metric") == "alb2012_timing_geography_blocker_interview_timing_ready_rows"), "0")),
        "alb2012_timing_geography_blocker_geography_ready_rows": safe_int(next((row.get("value", "0") for row in alb2012_blocker_summary if row.get("metric") == "alb2012_timing_geography_blocker_geography_ready_rows"), "0")),
        "alb2012_timing_geography_blocker_outcome_ready_rows": safe_int(next((row.get("value", "0") for row in alb2012_blocker_summary if row.get("metric") == "alb2012_timing_geography_blocker_outcome_ready_rows"), "0")),
        "alb2012_timing_geography_blocker_climate_linkage_ready_rows": safe_int(next((row.get("value", "0") for row in alb2012_blocker_summary if row.get("metric") == "alb2012_timing_geography_blocker_climate_linkage_ready_rows"), "0")),
        "alb2012_timing_geography_blocker_data_write_ready_rows": safe_int(next((row.get("value", "0") for row in alb2012_blocker_summary if row.get("metric") == "alb2012_timing_geography_blocker_data_write_ready_rows"), "0")),
        "alb2012_timing_geography_blocker_current_decision": next((row.get("value", "") for row in alb2012_blocker_summary if row.get("metric") == "alb2012_timing_geography_blocker_current_decision"), ""),
        "completion_complete": sum(1 for row in completion if row.get("status") == "complete"),
        "completion_incomplete": sum(1 for row in completion if row.get("status") == "incomplete"),
        "workspace_complete": sum(1 for row in workspace_validation if row.get("status") == "complete"),
        "workspace_incomplete": sum(1 for row in workspace_validation if row.get("status") == "incomplete"),
        "objective_trace_rows": len(objective_trace),
        "objective_guardrail_rows": len(objective_guardrails),
        "python_package_inventory": row_count(TEMP_DIR / "python_package_inventory.csv"),
        "python_environment_audit": row_count(RESULT_DIR / "python_environment_audit.csv"),
        "python_environment_summary": row_count(RESULT_DIR / "python_environment_summary.csv"),
        "python_environment_incomplete": sum(1 for row in read_csv_dicts(RESULT_DIR / "python_environment_audit.csv") if row.get("status") != "complete"),
    }
    return counts


def build_requirement_rows(counts: dict[str, int]) -> list[dict[str, str]]:
    reports = [
        REPORT_DIR / "README.md",
        REPORT_DIR / "source_audit.md",
        REPORT_DIR / "data_dictionary.md",
        REPORT_DIR / "outcome_construction.md",
        REPORT_DIR / "climate_linkage_audit.md",
        REPORT_DIR / "identification_audit.md",
        REPORT_DIR / "modeling_report.md",
        REPORT_DIR / "final_report.md",
        REPORT_DIR / "manual_data_access_guide.md",
        REPORT_DIR / "raw_data_request_packet.md",
        REPORT_DIR / "raw_ingestion_plan.md",
        REPORT_DIR / "raw_variable_verification_protocol.md",
        REPORT_DIR / "harmonization_recipe_gate.md",
        REPORT_DIR / "analysis_dataset_promotion_barriers.md",
        REPORT_DIR / "minimum_viable_acquisition_plan.md",
        REPORT_DIR / "public_external_raw_candidate_downloads.md",
        REPORT_DIR / "climate_exposure_plan.md",
        REPORT_DIR / "climate_validation_protocol.md",
        REPORT_DIR / "outcome_denominator_plan.md",
        REPORT_DIR / "sdg382_denominator_audit_plan.md",
        REPORT_DIR / "modeling_identification_plan.md",
        REPORT_DIR / "mechanism_analysis_protocol.md",
        REPORT_DIR / "empirical_readiness_dashboard.md",
        REPORT_DIR / "first_batch_raw_acquisition_checklist.md",
        REPORT_DIR / "first_batch_official_raw_access_probe.md",
        REPORT_DIR / "first_batch_manual_download_handoff.md",
        REPORT_DIR / "first_batch_public_documentation_audit.md",
        REPORT_DIR / "first_batch_file_source_traceability.md",
        REPORT_DIR / "first_batch_merge_key_lineage_plan.md",
        REPORT_DIR / "first_batch_raw_value_key_audit.md",
        REPORT_DIR / "alb2002_household_core_merge_audit.md",
        REPORT_DIR / "alb2002_provisional_outcome_feasibility.md",
        REPORT_DIR / "alb2002_outcome_semantics_raw_value_audit.md",
        REPORT_DIR / "alb2002_health_questionnaire_semantics_audit.md",
        REPORT_DIR / "alb2002_oop_aggregation_policy_audit.md",
        REPORT_DIR / "alb2002_skip_missing_semantics_audit.md",
        REPORT_DIR / "alb2002_oop_skip_value_decision_audit.md",
        REPORT_DIR / "alb2002_access_need_denominator_policy_audit.md",
        REPORT_DIR / "alb2002_consumption_sdg_denominator_policy_audit.md",
        REPORT_DIR / "alb2002_consumption_construction_source_audit.md",
        REPORT_DIR / "alb2002_consumption_aggregate_metadata_crosswalk_audit.md",
        REPORT_DIR / "alb2002_period_aligned_che_policy_audit.md",
        REPORT_DIR / "alb2002_minimum_recipe_promotion_packet.md",
        REPORT_DIR / "alb2002_boundary_source_resource_search_audit.md",
        REPORT_DIR / "alb2002_boundary_geometry_provenance_audit.md",
        REPORT_DIR / "alb2002_boundary_manual_verification_packet.md",
        REPORT_DIR / "alb2002_boundary_manual_source_followup.md",
        REPORT_DIR / "alb2002_gadm_boundary_lead_audit.md",
        REPORT_DIR / "alb2002_local_geography_artifact_audit.md",
        REPORT_DIR / "alb2005_documented_harmonization_review.md",
        REPORT_DIR / "alb2005_household_core_merge_audit.md",
        REPORT_DIR / "alb2005_provisional_outcome_feasibility.md",
        REPORT_DIR / "alb2005_outcome_semantics_raw_value_audit.md",
        REPORT_DIR / "alb2005_required_value_key_audit.md",
        REPORT_DIR / "alb2005_health_questionnaire_semantics_audit.md",
        REPORT_DIR / "alb2005_timing_geography_exhaustive_audit.md",
        REPORT_DIR / "alb2005_timing_geography_source_search_audit.md",
        REPORT_DIR / "alb2005_minimum_recipe_promotion_packet.md",
        REPORT_DIR / "alb2005_public_fieldwork_geo_metadata_audit.md",
        REPORT_DIR / "alb2005_diary_timing_candidate_audit.md",
        REPORT_DIR / "alb2005_extracted_module_coverage_audit.md",
        REPORT_DIR / "alb2005_fallback_blocker_resolution_matrix.md",
        REPORT_DIR / "albania_first_analysis_promotion_gate.md",
        REPORT_DIR / "albania_existing_raw_wave_audit.md",
        REPORT_DIR / "alb2008_household_core_merge_audit.md",
        REPORT_DIR / "alb2008_provisional_outcome_feasibility.md",
        REPORT_DIR / "alb2008_outcome_semantics_raw_value_audit.md",
        REPORT_DIR / "alb2008_timing_geography_exhaustive_audit.md",
        REPORT_DIR / "alb2008_fallback_blocker_resolution_matrix.md",
        REPORT_DIR / "first_batch_raw_verification_workbook.md",
        REPORT_DIR / "direct_read_audit_bundle.md",
    ]
    required_temp = [
        TEMP_DIR / "source_inventory.csv",
        TEMP_DIR / "country_wave_screening.csv",
        TEMP_DIR / "manual_download_manifest.csv",
        TEMP_DIR / "audit_log.md",
        TEMP_DIR / "iteration_notes.md",
        TEMP_DIR / "rejected_designs.md",
    ]
    rows: list[dict[str, str]] = []

    def add(
        req_id: str,
        section: str,
        requirement: str,
        status: str,
        evidence: str,
        artifacts: list[Path],
        gap: str = "",
    ) -> None:
        rows.append(
            {
                "requirement_id": req_id,
                "objective_section": section,
                "requirement": requirement,
                "status": status,
                "evidence": evidence,
                "evidence_artifacts": artifact_list(artifacts),
                "gap": gap,
            }
        )

    add(
        "workspace_structure",
        "workspace",
        "Create exact climate_uhc_ml directory structure with data, script, result, report, and temp.",
        status_done(all((TEMP_DIR.parent / name).is_dir() for name in ["data", "script", "result", "report", "temp"])),
        "all required directories exist" if all((TEMP_DIR.parent / name).is_dir() for name in ["data", "script", "result", "report", "temp"]) else "one or more required directories missing",
        [TEMP_DIR.parent / name for name in ["data", "script", "result", "report", "temp"]],
    )
    add(
        "required_reports",
        "workspace",
        "Maintain required human-readable reports.",
        status_done(all(file_ok(path) for path in reports[:8])),
        f"core required report files present={sum(1 for path in reports[:8] if file_ok(path))}/8",
        reports[:8],
        "" if all(file_ok(path) for path in reports[:8]) else "run setup/report generation",
    )
    add(
        "required_temp_files",
        "workspace",
        "Maintain required temp/source/audit files.",
        status_done(all(file_ok(path) for path in required_temp)),
        f"required temp files present={sum(1 for path in required_temp if file_ok(path))}/{len(required_temp)}",
        required_temp,
        "" if all(file_ok(path) for path in required_temp) else "run setup/inventory/acquisition scripts",
    )
    add(
        "phase0_official_sources",
        "phase0",
        "Verify official WHO/UNSD financial-protection and climate-health rationale before causal claims.",
        status_done(file_ok(REPORT_DIR / "source_audit.md") and counts["source_inventory"] > 0),
        f"source_inventory rows={counts['source_inventory']}; source_audit exists={file_ok(REPORT_DIR / 'source_audit.md')}",
        [REPORT_DIR / "source_audit.md", TEMP_DIR / "source_inventory.csv"],
    )
    add(
        "phase1_country_wave_inventory",
        "phase1",
        "Build the widest feasible public country-wave inventory before final country selection.",
        status_done(counts["country_wave_screening"] > 0 and counts["sample_gate"] > 0),
        f"country_wave_screening rows={counts['country_wave_screening']}; sample gate rows={counts['sample_gate']}; raw-final candidates={counts['sample_gate_raw_final']}",
        [TEMP_DIR / "country_wave_screening.csv", RESULT_DIR / "sample_selection_gate_audit.csv", REPORT_DIR / "sample_selection_audit.md"],
    )
    add(
        "phase2_manual_access_manifest",
        "phase2",
        "Download direct public data where feasible, create manual-download manifests for gated data, and do not fabricate unavailable files.",
        status_done(counts["manual_download_manifest"] > 0 and counts["manual_access_action_queue"] > 0 and counts["raw_download_intake"] > 0),
        f"manual manifest rows={counts['manual_download_manifest']}; action rows={counts['manual_access_action_queue']}; intake targets={counts['raw_download_intake']}; expected files={counts['raw_download_expected']}; minimum acquisition targets={counts['minimum_viable_acquisition_targets']}; raw-like files present={counts['raw_like_files']}",
        [TEMP_DIR / "manual_download_manifest.csv", TEMP_DIR / "manual_access_action_queue.csv", TEMP_DIR / "raw_download_intake_manifest.csv", TEMP_DIR / "raw_download_expected_files.csv", RESULT_DIR / "minimum_viable_acquisition_targets.csv", REPORT_DIR / "manual_data_access_guide.md", REPORT_DIR / "raw_data_request_packet.md", REPORT_DIR / "raw_download_intake_plan.md", REPORT_DIR / "minimum_viable_acquisition_plan.md"],
        "" if counts["manual_download_manifest"] > 0 else "create manual download manifest for gated datasets",
    )
    add(
        "phase2_public_external_raw_downloads",
        "phase2",
        "Download directly accessible public external raw archives when screened candidate links resolve without login, registration, or terms bypass.",
        status_done(counts["public_external_downloads"] > 0 and counts["public_external_downloaded"] > 0 and counts["public_external_download_summary"] > 0),
        f"candidate rows={counts['public_external_downloads']}; downloaded/existing rows={counts['public_external_downloaded']}; datasets={counts['public_external_datasets']}; summary rows={counts['public_external_download_summary']}",
        [TEMP_DIR / "public_external_raw_candidate_downloads.csv", RESULT_DIR / "public_external_raw_candidate_download_summary.csv", REPORT_DIR / "public_external_raw_candidate_downloads.md"],
        "" if counts["public_external_downloaded"] > 0 else "run script/44_download_public_external_raw_candidates.py after external repository probe",
    )
    add(
        "phase2_raw_file_inspection",
        "phase2",
        "Inspect raw files with schema extraction, checksums, row/column counts, and preserved labels.",
        blocked_if_raw(counts["raw_files"] > 0 and counts["raw_variables"] > 0),
        f"raw file inventory rows={counts['raw_files']}; raw variable rows={counts['raw_variables']}; raw-like targets={counts['raw_like_targets']}; intake ready targets={counts['raw_download_intake_ready']}; expected files not present={counts['raw_download_expected_not_present']}",
        [TEMP_DIR / "raw_schema_inventory" / "raw_file_inventory.csv", TEMP_DIR / "raw_schema_inventory" / "raw_variable_catalog.csv", TEMP_DIR / "raw_download_intake_manifest.csv", TEMP_DIR / "raw_download_expected_files.csv", REPORT_DIR / "raw_download_audit.md"],
        "" if counts["raw_files"] > 0 and counts["raw_variables"] > 0 else "manual raw files must be placed under temp/raw_downloads and inspected",
    )
    add(
        "phase3_variable_maps",
        "phase3",
        "Create variable maps for consumption, health expenditure, health need/access, geography, survey design, demographics, and shocks.",
        "partial_metadata_only" if counts["variable_maps"] > 0 and counts["raw_variables"] == 0 else status_done(counts["variable_maps"] > 0),
        f"variable-map rows={counts['variable_maps']}; variable-confidence rows={counts['variable_confidence']}; verification protocol rows={counts['raw_variable_verification_protocol']}; raw variable rows={counts['raw_variables']}",
        VARIABLE_MAP_FILES + [TEMP_DIR / "variable_map_confidence_audit.csv", TEMP_DIR / "raw_variable_verification_protocol.csv", REPORT_DIR / "raw_variable_verification_protocol.md"],
        "metadata-derived maps require raw-variable verification before harmonization" if counts["raw_variables"] == 0 else "",
    )
    add(
        "phase3_raw_variable_verification_protocol",
        "phase3",
        "Pre-specify raw-variable verification checks and harmonization scaffold before any analysis-ready data are built.",
        status_done(counts["raw_variable_verification_protocol"] > 0 and counts["harmonization_scaffold"] > 0 and counts["raw_variable_verification_summary"] > 0),
        f"protocol rows={counts['raw_variable_verification_protocol']}; scaffold rows={counts['harmonization_scaffold']}; value-audit-pending rows={counts['raw_variable_protocol_value_pending']}; raw-not-inspected rows={counts['raw_variable_protocol_not_inspected']}",
        [TEMP_DIR / "raw_variable_verification_protocol.csv", TEMP_DIR / "harmonization_recipe_scaffold.csv", RESULT_DIR / "raw_variable_verification_summary.csv", REPORT_DIR / "raw_variable_verification_protocol.md"],
        "" if counts["raw_variable_verification_protocol"] > 0 else "run raw-variable verification protocol after raw-ingestion planning",
    )
    add(
        "phase3_harmonization_recipe_gate",
        "phase3",
        "Promote metadata scaffold rows to harmonization recipe candidates only after raw file, raw variable, and value/unit/recall/key audits pass.",
        status_done(
            counts["harmonization_recipe_gate"] > 0
            and counts["harmonization_value_audit_template"] > 0
            and counts["harmonization_readiness"] > 0
            and counts["harmonization_recipe_gate_summary"] > 0
        ),
        f"gate rows={counts['harmonization_recipe_gate']}; value-audit template rows={counts['harmonization_value_audit_template']}; verified candidates={counts['harmonization_verified_candidates']}; readiness rows={counts['harmonization_readiness']}; ready country-waves={counts['harmonization_ready_country_waves']}",
        [TEMP_DIR / "harmonization_recipe_gate.csv", TEMP_DIR / "harmonization_value_audit_template.csv", TEMP_DIR / "harmonization_recipe_verified_candidates.csv", RESULT_DIR / "harmonization_readiness_matrix.csv", RESULT_DIR / "harmonization_recipe_gate_summary.csv", REPORT_DIR / "harmonization_recipe_gate.md"],
        "" if counts["harmonization_recipe_gate"] > 0 else "run script/33_build_harmonization_recipe_gate.py",
    )
    add(
        "cross_phase_analysis_dataset_promotion_barrier_audit",
        "phase3_phase5",
        "Reconcile the general harmonization gate, Albania-specific top-candidate gates, and data/ outputs before promoting any analysis-ready dataset.",
        status_done(
            counts["analysis_dataset_promotion_barrier_audit"] == 6
            and counts["analysis_dataset_promotion_barrier_summary"] > 0
            and counts["analysis_dataset_promotion_audit_rows"] == 6
            and counts["analysis_dataset_promotion_blocked_rows"] == 2
            and counts["analysis_dataset_promotion_promoted_rows"] == 4
            and counts["analysis_dataset_promotion_data_file_count"] == 4
            and counts["analysis_dataset_promotion_verified_recipe_candidates"] == 0
            and counts["analysis_dataset_promotion_ready_country_waves"] == 0
            and counts["analysis_dataset_promotion_alb2002_temp_core_rows"] == 3599
            and counts["analysis_dataset_promotion_alb2002_harmonized_ready_rows"] == 0
            and counts["analysis_dataset_promotion_alb2002_outcome_ready_rows"] == 0
            and counts["analysis_dataset_promotion_alb2002_climate_linkage_ready_rows"] == 0
            and counts["analysis_dataset_promotion_limited_harmonized_core_rows"] == 3599
            and counts["analysis_dataset_promotion_limited_harmonized_core_data_write_ready_rows"] == 3599
            and counts["analysis_dataset_promotion_limited_harmonized_core_final_outcome_ready_rows"] == 0
            and counts["analysis_dataset_promotion_limited_harmonized_core_climate_linkage_ready_rows"] == 0
            and counts["analysis_dataset_promotion_limited_harmonized_core_analysis_ready_rows"] == 0
            and counts["analysis_dataset_promotion_limited_financial_outcome_rows"] == 3599
            and counts["analysis_dataset_promotion_limited_financial_outcome_data_write_ready_rows"] == 3599
            and counts["analysis_dataset_promotion_limited_financial_outcome_che10_rows"] == 824
            and counts["analysis_dataset_promotion_limited_financial_outcome_che25_rows"] == 290
            and counts["analysis_dataset_promotion_limited_financial_outcome_sdg382_ready_rows"] == 0
            and counts["analysis_dataset_promotion_limited_financial_outcome_access_ready_rows"] == 0
            and counts["analysis_dataset_promotion_limited_financial_outcome_composite_ready_rows"] == 0
            and counts["analysis_dataset_promotion_limited_financial_outcome_climate_linkage_ready_rows"] == 0
            and counts["analysis_dataset_promotion_limited_financial_outcome_analysis_ready_rows"] == 0
            and counts["analysis_dataset_promotion_limited_climate_exposure_rows"] == 384
            and counts["analysis_dataset_promotion_limited_climate_exposure_data_write_ready_rows"] == 384
            and counts["analysis_dataset_promotion_limited_climate_exposure_climate_linkage_ready_rows"] == 0
            and counts["analysis_dataset_promotion_limited_climate_exposure_analysis_ready_rows"] == 0
            and counts["analysis_dataset_promotion_limited_climate_linked_rows"] == 14396
            and counts["analysis_dataset_promotion_limited_climate_linked_data_write_ready_rows"] == 14396
            and counts["analysis_dataset_promotion_limited_climate_linked_descriptive_ready_rows"] == 0
            and counts["analysis_dataset_promotion_limited_climate_linked_predictive_ml_ready_rows"] == 0
            and counts["analysis_dataset_promotion_limited_climate_linked_reduced_form_ready_rows"] == 0
            and counts["analysis_dataset_promotion_limited_climate_linked_robustness_ready_rows"] == 0
            and counts["analysis_dataset_promotion_limited_climate_linked_analysis_ready_rows"] == 0
            and counts["analysis_dataset_promotion_current_decision"] == "limited_core_financial_outcomes_climate_exposures_and_linked_diagnostics_promoted_models_still_blocked"
        ),
        f"audit rows={counts['analysis_dataset_promotion_barrier_audit']}; summary rows={counts['analysis_dataset_promotion_barrier_summary']}; blocked rows={counts['analysis_dataset_promotion_blocked_rows']}; promoted rows={counts['analysis_dataset_promotion_promoted_rows']}; data files={counts['analysis_dataset_promotion_data_file_count']}; verified recipe candidates={counts['analysis_dataset_promotion_verified_recipe_candidates']}; ready country-waves={counts['analysis_dataset_promotion_ready_country_waves']}; ALB_2002 temp core rows={counts['analysis_dataset_promotion_alb2002_temp_core_rows']}; limited core rows={counts['analysis_dataset_promotion_limited_harmonized_core_rows']}; limited financial rows={counts['analysis_dataset_promotion_limited_financial_outcome_rows']}; limited climate rows={counts['analysis_dataset_promotion_limited_climate_exposure_rows']}; limited linked rows={counts['analysis_dataset_promotion_limited_climate_linked_rows']}; limited linked analysis-ready={counts['analysis_dataset_promotion_limited_climate_linked_analysis_ready_rows']}; ALB_2002 harmonized ready={counts['analysis_dataset_promotion_alb2002_harmonized_ready_rows']}; ALB_2002 outcome ready={counts['analysis_dataset_promotion_alb2002_outcome_ready_rows']}; ALB_2002 climate ready={counts['analysis_dataset_promotion_alb2002_climate_linkage_ready_rows']}; decision={counts['analysis_dataset_promotion_current_decision']}",
        [TEMP_DIR / "analysis_dataset_promotion_barrier_audit.csv", RESULT_DIR / "analysis_dataset_promotion_barrier_summary.csv", REPORT_DIR / "analysis_dataset_promotion_barriers.md", DATA_DIR / "harmonized_household.csv", DATA_DIR / "household_outcomes.csv", DATA_DIR / "climate_exposures_nasa_power.csv", DATA_DIR / "climate_linked_household.csv"],
        "" if counts["analysis_dataset_promotion_promoted_rows"] == 4 and counts["analysis_dataset_promotion_data_file_count"] == 4 else "rerun script/98_audit_analysis_dataset_promotion_barriers.py and remove or justify premature data/ artifacts",
    )
    add(
        "phase3_harmonization",
        "phase3",
        "Build harmonized household/person analytical data only after schema inspection.",
        blocked_if_raw(counts["harmonized_household"] > 0),
        f"harmonized household rows={counts['harmonized_household']}; harmonization audit rows={counts['harmonization_audit']}; raw verified concepts={counts['raw_ingestion_verified_concepts']}; scaffold rows={counts['harmonization_scaffold']}; verified recipe candidates={counts['harmonization_verified_candidates']}",
        [DATA_DIR / "harmonized_household.csv", TEMP_DIR / "harmonization_audit.csv", TEMP_DIR / "raw_ingestion_plan.csv", TEMP_DIR / "harmonization_recipe_scaffold.csv", TEMP_DIR / "harmonization_recipe_verified_candidates.csv"],
        "" if counts["harmonized_household"] > 0 else "requires raw microdata and verified harmonization recipe",
    )
    add(
        "phase4_outcome_construction",
        "phase4",
        "Construct and audit financial-protection, access, and composite UHC outcomes with event rates and missingness.",
        blocked_if_raw(counts["household_outcomes"] > 0 and counts["outcome_audit_constructed"] > 0),
        f"household outcome rows={counts['household_outcomes']}; constructed outcome-audit rows={counts['outcome_audit_constructed']}; outcome plan rows={counts['outcome_plan']}",
        [DATA_DIR / "household_outcomes.csv", RESULT_DIR / "outcome_audit.csv", TEMP_DIR / "outcome_denominator_plan.csv", REPORT_DIR / "outcome_denominator_plan.md"],
        "" if counts["household_outcomes"] > 0 else "requires harmonized OOP, budget, need/access, survey design, and recall-period checks",
    )
    add(
        "phase4_sdg382_denominator_audit",
        "phase4",
        "Pre-specify the SDG 3.8.2 discretionary-budget denominator, SPL, PPP/CPI, and benchmark checks before construction.",
        status_done(counts["sdg382_denominator_requirements"] > 0 and counts["sdg382_denominator_source_matrix"] > 0 and counts["sdg382_denominator_readiness"] > 0 and counts["sdg382_denominator_summary"] > 0),
        f"requirement rows={counts['sdg382_denominator_requirements']}; source rows={counts['sdg382_denominator_source_matrix']}; country-wave rows={counts['sdg382_denominator_readiness']}; ready rows={counts['sdg382_denominator_ready']}; blocked rows={counts['sdg382_denominator_blocked']}",
        [TEMP_DIR / "sdg382_denominator_requirements.csv", RESULT_DIR / "sdg382_denominator_source_matrix.csv", RESULT_DIR / "sdg382_denominator_country_wave_readiness.csv", RESULT_DIR / "sdg382_denominator_summary.csv", REPORT_DIR / "sdg382_denominator_audit_plan.md"],
        "" if counts["sdg382_denominator_requirements"] > 0 else "run script/31_build_sdg382_denominator_audit_plan.py",
    )
    add(
        "phase5_climate_sources",
        "phase5",
        "Verify climate source endpoints and pre-specify exposure families and windows.",
        status_done(counts["climate_source_probe_ok"] > 0 and counts["climate_exposure_plan"] > 0 and counts["climate_exposure_specs"] > 0),
        f"climate source probe rows={counts['climate_source_probe']}; reachable/pass={counts['climate_source_probe_ok']}; exposure plan rows={counts['climate_exposure_plan']}; spec rows={counts['climate_exposure_specs']}; validation protocol rows={counts['climate_validation_protocol']}",
        [TEMP_DIR / "climate_source_probe.csv", TEMP_DIR / "climate_exposure_plan.csv", RESULT_DIR / "climate_exposure_specification.csv", RESULT_DIR / "climate_exposure_validation_protocol.csv", REPORT_DIR / "climate_exposure_plan.md", REPORT_DIR / "climate_validation_protocol.md"],
    )
    add(
        "phase5_climate_validation_protocol",
        "phase5",
        "Pre-specify climate linkage validation for timing, geolocation quality, units, baselines, maps, and source comparisons.",
        status_done(counts["climate_linkage_requirements"] > 0 and counts["climate_source_method_matrix"] > 0 and counts["climate_validation_protocol"] > 0 and counts["climate_linkage_readiness"] > 0 and counts["climate_validation_summary"] > 0),
        f"requirement rows={counts['climate_linkage_requirements']}; source rows={counts['climate_source_method_matrix']}; validation rows={counts['climate_validation_protocol']}; readiness rows={counts['climate_linkage_readiness']}; ready rows={counts['climate_linkage_ready_value']}; blocked rows={counts['climate_linkage_blocked_value']}",
        [TEMP_DIR / "climate_linkage_requirements.csv", RESULT_DIR / "climate_source_method_matrix.csv", RESULT_DIR / "climate_exposure_validation_protocol.csv", RESULT_DIR / "climate_linkage_readiness.csv", RESULT_DIR / "climate_validation_protocol_summary.csv", REPORT_DIR / "climate_validation_protocol.md"],
        "" if counts["climate_validation_protocol"] > 0 else "run script/32_build_climate_validation_protocol.py",
    )
    add(
        "phase5_climate_extraction",
        "phase5",
        "Construct climate exposures from verified geography and survey timing and audit linkage quality.",
        blocked_if_raw(counts["climate_exposures"] > 0 and counts["climate_audit"] > 0),
        f"climate exposure rows={counts['climate_exposures']}; climate audit rows={counts['climate_audit']}; climate-linked rows={counts['climate_linked']}",
        [DATA_DIR / "climate_exposures_nasa_power.csv", TEMP_DIR / "climate_extraction_audit.csv", DATA_DIR / "climate_linked_household.csv"],
        "" if counts["climate_exposures"] > 0 else "requires raw-verified geography/timing and harmonized linkage input",
    )
    add(
        "phase6_descriptive",
        "phase6",
        "Produce weighted prevalence, missingness, sample flow, and country-wave feasibility diagnostics before causal modeling.",
        blocked_if_raw(counts["descriptive_prevalence"] > 0 and counts["descriptive_missingness"] > 0),
        f"prevalence rows={counts['descriptive_prevalence']}; missingness rows={counts['descriptive_missingness']}; sample-flow rows={counts['sample_flow']}",
        [RESULT_DIR / "descriptive_weighted_prevalence.csv", RESULT_DIR / "descriptive_missingness.csv", RESULT_DIR / "sample_inclusion_flow.csv"],
        "" if counts["descriptive_prevalence"] > 0 else "requires climate-linked household outcomes",
    )
    add(
        "phase7_predictive_ml",
        "phase7",
        "Estimate and validate predictive ML with non-random validation splits before targeting claims.",
        blocked_if_raw(counts["predictive_metrics"] > 0),
        f"predictive audit rows={counts['predictive_audit']}; metric rows={counts['predictive_metrics']}; modeling predictive-ready rows={counts['modeling_predictive_ready']}",
        [RESULT_DIR / "predictive_ml_audit.csv", RESULT_DIR / "predictive_ml_metrics.csv", RESULT_DIR / "modeling_validation_plan.csv"],
        "" if counts["predictive_metrics"] > 0 else "requires constructed targets, climate-linked data, and leave-country/wave/time validation",
    )
    add(
        "phase8_reduced_form",
        "phase8",
        "Estimate reduced-form climate-shock models only after timing, geography, controls, and placebo readiness are auditable.",
        blocked_if_raw(counts["reduced_form_estimates"] > 0),
        f"causal-model audit rows={counts['causal_model_audit']}; estimate rows={counts['reduced_form_estimates']}; reduced-form ready rows={counts['modeling_reduced_ready']}",
        [RESULT_DIR / "causal_model_audit.csv", RESULT_DIR / "reduced_form_estimates.csv", RESULT_DIR / "falsification_placebo_plan.csv"],
        "" if counts["reduced_form_estimates"] > 0 else "requires climate-linked outcome data with exposure variation and placebo-ready design checks",
    )
    add(
        "phase9_causal_ml",
        "phase9",
        "Allow causal ML only after credible reduced-form identification; otherwise reject explicitly.",
        status_done(counts["causal_ml_policy_audit"] > 0 and (counts["causal_ml_rejected"] > 0 or counts["modeling_causal_ml_ready"] > 0)),
        f"causal ML policy audit rows={counts['causal_ml_policy_audit']}; rejected rows={counts['causal_ml_rejected']}; causal-ML-ready rows={counts['modeling_causal_ml_ready']}",
        [RESULT_DIR / "causal_ml_policy_audit.csv", TEMP_DIR / "modeling_identification_plan.csv", RESULT_DIR / "policy_learning_plan.csv"],
        "" if counts["causal_ml_policy_audit"] > 0 else "run causal-ML gate script after reduced-form audit",
    )
    add(
        "phase10_policy_learning",
        "phase10",
        "Evaluate policy targeting only after validated prediction or credible treatment-effect evidence, with benefit sensitivity.",
        blocked_if_raw(counts["modeling_policy_ready"] > 0 and counts["policy_learning_plan"] > 0),
        f"policy-learning plan rows={counts['policy_learning_plan']}; policy-ready rows={counts['modeling_policy_ready']}",
        [RESULT_DIR / "policy_learning_plan.csv", RESULT_DIR / "policy_targeting_simulation.csv", REPORT_DIR / "modeling_identification_plan.md"],
        "" if counts["modeling_policy_ready"] > 0 else "requires reduced-form identification and validation gates before policy-value simulation",
    )
    add(
        "phase11_mechanisms",
        "phase11",
        "Test mechanisms only where income, food insecurity, health need, OOP, coping, or related modules exist.",
        status_done(
            counts["mechanism_requirements"] > 0
            and counts["mechanism_pathway_protocol"] > 0
            and counts["mechanism_readiness"] > 0
            and counts["mechanism_summary"] > 0
        ),
        f"mechanism requirement rows={counts['mechanism_requirements']}; pathway rows={counts['mechanism_pathway_protocol']}; readiness rows={counts['mechanism_readiness']}; ready rows={counts['mechanism_ready']}; blocked rows={counts['mechanism_blocked']}; raw variable rows={counts['raw_variables']}",
        [TEMP_DIR / "mechanism_variable_requirements.csv", RESULT_DIR / "mechanism_pathway_protocol.csv", RESULT_DIR / "mechanism_readiness_matrix.csv", RESULT_DIR / "mechanism_analysis_protocol_summary.csv", REPORT_DIR / "mechanism_analysis_protocol.md"],
        "" if counts["mechanism_requirements"] > 0 else "run script/34_build_mechanism_analysis_protocol.py after modeling-identification planning",
    )
    add(
        "phase12_robustness",
        "phase12",
        "Attempt robustness and falsification checks after a primary reduced-form estimate exists.",
        blocked_if_raw(counts["robustness_attempted"] > 0),
        f"robustness result rows={counts['robustness_results']}; attempted rows={counts['robustness_attempted']}; falsification plan rows={counts['falsification_plan']}",
        [RESULT_DIR / "robustness_results.csv", RESULT_DIR / "falsification_placebo_plan.csv", RESULT_DIR / "robustness_audit.csv"],
        "" if counts["robustness_attempted"] > 0 else "requires a primary reduced-form estimate and refit/placebo checks",
    )
    add(
        "phase13_design_scorecard",
        "phase13",
        "Create design scorecard and enforce go/no-go rules.",
        status_done(counts["design_scorecard"] > 0 and counts["sample_gate_failed_rules"] > 0),
        f"design scorecard rows={counts['design_scorecard']}; failed no-go rules={counts['sample_gate_failed_rules']}; raw-final candidates={counts['sample_gate_raw_final']}",
        [RESULT_DIR / "design_scorecard.csv", RESULT_DIR / "sample_selection_gate_summary.csv", REPORT_DIR / "sample_selection_audit.md"],
    )
    add(
        "phase13_current_design_scorecard_no_go_audit",
        "phase13",
        "Refresh the current design scorecard from ALB_2002 linked-candidate diagnostics and keep estimation/policy-learning claims no-go until promoted data exist.",
        status_done(
            counts["design_scorecard"] == 38
            and counts["design_scorecard_current_audit"] == 4
            and counts["design_no_go_threshold_audit"] == 8
            and counts["design_scorecard_current_summary"] == 7
            and counts["design_scorecard_rows"] == 38
            and counts["design_scorecard_current_rows"] == 3
            and counts["design_scorecard_audit_rows"] == 4
            and counts["design_no_go_threshold_rows"] == 8
            and counts["design_no_go_failed_or_not_estimable_rows"] == 8
            and counts["design_scorecard_data_write_ready_rows"] == 0
            and counts["design_scorecard_current_decision"] == "fail_closed_design_scorecard_currently_no_go_for_estimation_or_policy_learning"
        ),
        f"scorecard rows={counts['design_scorecard']}; current audit rows={counts['design_scorecard_current_audit']}; threshold rows={counts['design_no_go_threshold_audit']}; summary rows={counts['design_scorecard_current_summary']}; current rows={counts['design_scorecard_current_rows']}; failed/not-estimable rows={counts['design_no_go_failed_or_not_estimable_rows']}; data-write-ready rows={counts['design_scorecard_data_write_ready_rows']}; decision={counts['design_scorecard_current_decision']}",
        [RESULT_DIR / "design_scorecard.csv", RESULT_DIR / "design_scorecard_current_audit.csv", RESULT_DIR / "design_no_go_threshold_audit.csv", RESULT_DIR / "design_scorecard_current_summary.csv", REPORT_DIR / "design_scorecard_audit.md"],
        "" if counts["design_scorecard_current_decision"] == "fail_closed_design_scorecard_currently_no_go_for_estimation_or_policy_learning" else "run script/110_build_current_design_scorecard.py after the ALB_2002 linked-candidate and promotion-barrier audits",
    )
    add(
        "cross_phase_alb2002_promotion_gate_delta_audit",
        "phase13",
        "Separate ALB_2002 evidence-rich promotion gates from hard blockers before any harmonized, outcome, climate, or linked data write.",
        status_done(
            counts["alb2002_promotion_gate_delta_audit"] == 10
            and counts["alb2002_promotion_gate_delta_summary"] == 7
            and counts["alb2002_promotion_gate_delta_rows"] == 10
            and counts["alb2002_promotion_gate_delta_review_ready_rows"] == 2
            and counts["alb2002_promotion_gate_delta_documented_candidate_rows"] == 6
            and counts["alb2002_promotion_gate_delta_hard_blocked_rows"] == 4
            and counts["alb2002_promotion_gate_delta_promotion_ready_rows"] == 0
            and counts["alb2002_promotion_gate_delta_data_write_ready_rows"] == 0
            and counts["alb2002_promotion_gate_delta_decision"] == "partial_gate_delta_documented_keep_data_empty_until_outcome_sdg_geography_gates_pass"
        ),
        f"audit rows={counts['alb2002_promotion_gate_delta_audit']}; summary rows={counts['alb2002_promotion_gate_delta_summary']}; review-ready rows={counts['alb2002_promotion_gate_delta_review_ready_rows']}; documented-candidate rows={counts['alb2002_promotion_gate_delta_documented_candidate_rows']}; hard-blocked rows={counts['alb2002_promotion_gate_delta_hard_blocked_rows']}; promotion-ready rows={counts['alb2002_promotion_gate_delta_promotion_ready_rows']}; data-write-ready rows={counts['alb2002_promotion_gate_delta_data_write_ready_rows']}; decision={counts['alb2002_promotion_gate_delta_decision']}",
        [TEMP_DIR / "alb2002_promotion_gate_delta_audit.csv", RESULT_DIR / "alb2002_promotion_gate_delta_summary.csv", REPORT_DIR / "alb2002_promotion_gate_delta_audit.md"],
        "" if counts["alb2002_promotion_gate_delta_data_write_ready_rows"] == 0 else "rerun script/111_audit_alb2002_promotion_gate_delta.py and keep data writes closed until hard blockers pass",
    )
    add(
        "cross_phase_alb2002_boundary_blocker_resolution_matrix",
        "phase5",
        "Consolidate ALB_2002 boundary-source evidence before any climate-linkage promotion or admin-level exposure construction.",
        status_done(
            counts["alb2002_boundary_blocker_resolution_matrix"] == 11
            and counts["alb2002_boundary_blocker_resolution_summary"] == 10
            and counts["alb2002_boundary_blocker_resolution_rows"] == 11
            and counts["alb2002_boundary_blocker_official_or_primary_lead_rows"] == 4
            and counts["alb2002_boundary_blocker_candidate_name_coverage_rows"] == 3
            and counts["alb2002_boundary_blocker_incompatible_or_negative_rows"] == 4
            and counts["alb2002_boundary_blocker_historical_2002_ready_rows"] == 0
            and counts["alb2002_boundary_blocker_climate_linkage_ready_rows"] == 0
            and counts["alb2002_boundary_blocker_data_write_ready_rows"] == 0
            and counts["alb2002_boundary_blocker_hard_blocked_rows"] == 11
            and counts["alb2002_boundary_blocker_required_source_action_rows"] == 7
            and counts["alb2002_boundary_blocker_current_decision"] == "blocked_no_alb2002_boundary_source_ready_for_climate_linkage"
        ),
        f"matrix rows={counts['alb2002_boundary_blocker_resolution_matrix']}; summary rows={counts['alb2002_boundary_blocker_resolution_summary']}; official leads={counts['alb2002_boundary_blocker_official_or_primary_lead_rows']}; candidate-name-coverage rows={counts['alb2002_boundary_blocker_candidate_name_coverage_rows']}; incompatible/negative rows={counts['alb2002_boundary_blocker_incompatible_or_negative_rows']}; historical-ready rows={counts['alb2002_boundary_blocker_historical_2002_ready_rows']}; climate-ready rows={counts['alb2002_boundary_blocker_climate_linkage_ready_rows']}; data-write-ready rows={counts['alb2002_boundary_blocker_data_write_ready_rows']}; hard-blocked rows={counts['alb2002_boundary_blocker_hard_blocked_rows']}; source-action rows={counts['alb2002_boundary_blocker_required_source_action_rows']}; decision={counts['alb2002_boundary_blocker_current_decision']}",
        [TEMP_DIR / "alb2002_boundary_blocker_resolution_matrix.csv", RESULT_DIR / "alb2002_boundary_blocker_resolution_summary.csv", REPORT_DIR / "alb2002_boundary_blocker_resolution_matrix.md"],
        "" if counts["alb2002_boundary_blocker_climate_linkage_ready_rows"] == 0 and counts["alb2002_boundary_blocker_data_write_ready_rows"] == 0 else "rerun script/112_build_alb2002_boundary_blocker_resolution_matrix.py and keep climate linkage closed until a verified historical source passes",
    )
    add(
        "phase4_alb2002_outcome_blocker_resolution_matrix",
        "phase4",
        "Consolidate ALB_2002 financial, access, composite, and SDG outcome candidates before any final outcome write.",
        status_done(
            counts["alb2002_outcome_blocker_resolution_matrix"] == 12
            and counts["alb2002_outcome_blocker_resolution_summary"] == 12
            and counts["alb2002_outcome_blocker_resolution_rows"] == 12
            and counts["alb2002_outcome_blocker_financial_rows"] == 4
            and counts["alb2002_outcome_blocker_access_rows"] == 5
            and counts["alb2002_outcome_blocker_composite_rows"] == 3
            and counts["alb2002_outcome_blocker_candidate_not_promoted_rows"] == 11
            and counts["alb2002_outcome_blocker_low_event_candidate_rows"] == 1
            and counts["alb2002_outcome_blocker_hard_blocked_rows"] == 1
            and counts["alb2002_outcome_blocker_outcome_ready_rows"] == 0
            and counts["alb2002_outcome_blocker_sdg382_ready_rows"] == 0
            and counts["alb2002_outcome_blocker_climate_linkage_ready_rows"] == 0
            and counts["alb2002_outcome_blocker_data_write_ready_rows"] == 0
            and counts["alb2002_outcome_blocker_current_decision"] == "blocked_no_alb2002_outcome_ready_for_promotion"
        ),
        f"matrix rows={counts['alb2002_outcome_blocker_resolution_matrix']}; summary rows={counts['alb2002_outcome_blocker_resolution_summary']}; financial rows={counts['alb2002_outcome_blocker_financial_rows']}; access rows={counts['alb2002_outcome_blocker_access_rows']}; composite rows={counts['alb2002_outcome_blocker_composite_rows']}; candidate-not-promoted rows={counts['alb2002_outcome_blocker_candidate_not_promoted_rows']}; low-event rows={counts['alb2002_outcome_blocker_low_event_candidate_rows']}; hard-blocked rows={counts['alb2002_outcome_blocker_hard_blocked_rows']}; outcome-ready rows={counts['alb2002_outcome_blocker_outcome_ready_rows']}; sdg382-ready rows={counts['alb2002_outcome_blocker_sdg382_ready_rows']}; climate-ready rows={counts['alb2002_outcome_blocker_climate_linkage_ready_rows']}; data-write-ready rows={counts['alb2002_outcome_blocker_data_write_ready_rows']}; decision={counts['alb2002_outcome_blocker_current_decision']}",
        [TEMP_DIR / "alb2002_outcome_blocker_resolution_matrix.csv", RESULT_DIR / "alb2002_outcome_blocker_resolution_summary.csv", REPORT_DIR / "alb2002_outcome_blocker_resolution_matrix.md"],
        "" if counts["alb2002_outcome_blocker_outcome_ready_rows"] == 0 and counts["alb2002_outcome_blocker_data_write_ready_rows"] == 0 else "rerun script/113_build_alb2002_outcome_blocker_resolution_matrix.py and keep outcome writes closed until numerator, denominator, SDG, access, and climate gates pass",
    )
    add(
        "cross_phase_alb2012_timing_geography_fallback_blocker",
        "phase5",
        "Consolidate ALB_2012 timing, geography, outcome, and first-analysis fallback evidence before substituting it for ALB_2002.",
        status_done(
            counts["alb2012_timing_geography_blocker_resolution_matrix"] == 10
            and counts["alb2012_timing_geography_blocker_resolution_summary"] == 12
            and counts["alb2012_timing_geography_blocker_resolution_rows"] == 10
            and counts["alb2012_timing_geography_blocker_timing_rows"] == 3
            and counts["alb2012_timing_geography_blocker_geography_rows"] == 3
            and counts["alb2012_timing_geography_blocker_outcome_rows"] == 2
            and counts["alb2012_timing_geography_blocker_promotion_gate_rows"] == 2
            and counts["alb2012_timing_geography_blocker_hard_blocked_rows"] == 10
            and counts["alb2012_timing_geography_blocker_interview_timing_ready_rows"] == 0
            and counts["alb2012_timing_geography_blocker_geography_ready_rows"] == 0
            and counts["alb2012_timing_geography_blocker_outcome_ready_rows"] == 0
            and counts["alb2012_timing_geography_blocker_climate_linkage_ready_rows"] == 0
            and counts["alb2012_timing_geography_blocker_data_write_ready_rows"] == 0
            and counts["alb2012_timing_geography_blocker_current_decision"] == "blocked_alb2012_no_timing_geography_fallback_ready"
        ),
        f"matrix rows={counts['alb2012_timing_geography_blocker_resolution_matrix']}; summary rows={counts['alb2012_timing_geography_blocker_resolution_summary']}; timing rows={counts['alb2012_timing_geography_blocker_timing_rows']}; geography rows={counts['alb2012_timing_geography_blocker_geography_rows']}; outcome rows={counts['alb2012_timing_geography_blocker_outcome_rows']}; promotion-gate rows={counts['alb2012_timing_geography_blocker_promotion_gate_rows']}; hard-blocked rows={counts['alb2012_timing_geography_blocker_hard_blocked_rows']}; interview-timing-ready rows={counts['alb2012_timing_geography_blocker_interview_timing_ready_rows']}; geography-ready rows={counts['alb2012_timing_geography_blocker_geography_ready_rows']}; outcome-ready rows={counts['alb2012_timing_geography_blocker_outcome_ready_rows']}; climate-ready rows={counts['alb2012_timing_geography_blocker_climate_linkage_ready_rows']}; data-write-ready rows={counts['alb2012_timing_geography_blocker_data_write_ready_rows']}; decision={counts['alb2012_timing_geography_blocker_current_decision']}",
        [TEMP_DIR / "alb2012_timing_geography_blocker_resolution_matrix.csv", RESULT_DIR / "alb2012_timing_geography_blocker_resolution_summary.csv", REPORT_DIR / "alb2012_timing_geography_blocker_resolution_matrix.md"],
        "" if counts["alb2012_timing_geography_blocker_climate_linkage_ready_rows"] == 0 and counts["alb2012_timing_geography_blocker_data_write_ready_rows"] == 0 else "rerun script/114_build_alb2012_timing_geography_blocker_resolution_matrix.py and keep ALB_2012 fallback promotion closed until timing, geography, and outcome gates pass",
    )
    add(
        "phase13_minimum_viable_acquisition_targets",
        "phase13",
        "Map no-go threshold tests to a practical raw-data acquisition sequence before final sample selection.",
        status_done(counts["minimum_viable_acquisition_targets"] > 0 and counts["minimum_viable_download_bundles"] > 0 and counts["minimum_viable_acquisition_summary"] > 0),
        f"target rows={counts['minimum_viable_acquisition_targets']}; bundle rows={counts['minimum_viable_download_bundles']}; financial-probe rows={counts['minimum_viable_financial_probe']}; double-failure-probe rows={counts['minimum_viable_double_probe']}",
        [RESULT_DIR / "minimum_viable_acquisition_targets.csv", TEMP_DIR / "minimum_viable_download_bundles.csv", RESULT_DIR / "minimum_viable_acquisition_summary.csv", REPORT_DIR / "minimum_viable_acquisition_plan.md"],
        "" if counts["minimum_viable_acquisition_targets"] > 0 else "run script/30_build_minimum_viable_acquisition_plan.py",
    )
    add(
        "cross_phase_empirical_readiness_dashboard",
        "phase13",
        "Consolidate acquisition, sample, harmonization, outcome, climate, modeling, mechanism, and go/no-go gates before final country selection.",
        status_done(counts["empirical_dashboard"] > 0 and counts["empirical_no_go"] > 0 and counts["empirical_dashboard_summary"] > 0),
        f"dashboard rows={counts['empirical_dashboard']}; no-go rows={counts['empirical_no_go']}; no-go pass rows={counts['empirical_no_go_pass']}; no-go blocked rows={counts['empirical_no_go_blocked']}",
        [RESULT_DIR / "empirical_readiness_dashboard.csv", RESULT_DIR / "empirical_no_go_threshold_status.csv", RESULT_DIR / "empirical_readiness_dashboard_summary.csv", REPORT_DIR / "empirical_readiness_dashboard.md"],
        "" if counts["empirical_dashboard"] > 0 else "run script/35_build_empirical_readiness_dashboard.py",
    )
    add(
        "cross_phase_first_batch_raw_acquisition",
        "phase13",
        "Define a concrete first manual raw-download batch to test the 6-country financial-protection and 10-wave double-failure no-go thresholds.",
        status_done(counts["first_batch_raw_acquisition_checklist"] > 0 and counts["first_batch_raw_file_targets"] > 0 and counts["first_batch_raw_acquisition_summary"] > 0),
        f"checklist rows={counts['first_batch_raw_acquisition_checklist']}; file target rows={counts['first_batch_raw_file_targets']}; summary rows={counts['first_batch_raw_acquisition_summary']}; raw tabular files present={counts['first_batch_raw_tabular_files']}; archives present={counts['first_batch_archive_files']}",
        [TEMP_DIR / "first_batch_raw_acquisition_checklist.csv", TEMP_DIR / "first_batch_raw_file_targets.csv", RESULT_DIR / "first_batch_raw_acquisition_summary.csv", REPORT_DIR / "first_batch_raw_acquisition_checklist.md"],
        "" if counts["first_batch_raw_acquisition_checklist"] > 0 else "run script/37_build_first_batch_raw_acquisition_checklist.py after minimum viable acquisition planning",
    )
    add(
        "cross_phase_first_batch_official_raw_access_probe",
        "phase2",
        "Probe official first-batch get-microdata pages for visible access gates and candidate direct links without downloading raw files or bypassing terms.",
        status_done(counts["first_batch_official_raw_access_probe"] > 0 and counts["first_batch_official_raw_access_summary"] > 0),
        f"probe rows={counts['first_batch_official_raw_access_probe']}; summary rows={counts['first_batch_official_raw_access_summary']}; access gate rows={counts['first_batch_access_gate_detected']}; possible direct raw routes={counts['first_batch_possible_direct_raw_routes']}; manual action required rows={counts['first_batch_manual_action_required']}",
        [TEMP_DIR / "first_batch_official_raw_access_probe.csv", RESULT_DIR / "first_batch_official_raw_access_summary.csv", REPORT_DIR / "first_batch_official_raw_access_probe.md"],
        "" if counts["first_batch_official_raw_access_probe"] > 0 else "run script/39_probe_first_batch_official_raw_access.py after first-batch raw acquisition checklist generation",
    )
    add(
        "cross_phase_first_batch_manual_download_handoff",
        "phase2",
        "Provide a concrete per-dataset manual-download handoff when automated raw access is blocked by account, registration, request, or terms workflows.",
        status_done(
            counts["first_batch_manual_download_handoff"] > 0
            and counts["first_batch_manual_download_file_queue"] > 0
            and counts["first_batch_manual_download_handoff_summary"] > 0
        ),
        f"handoff rows={counts['first_batch_manual_download_handoff']}; file queue rows={counts['first_batch_manual_download_file_queue']}; summary rows={counts['first_batch_manual_download_handoff_summary']}; manual required rows={counts['first_batch_handoff_manual_required']}; raw-ready rows={counts['first_batch_handoff_raw_ready']}",
        [TEMP_DIR / "first_batch_manual_download_handoff.csv", TEMP_DIR / "first_batch_manual_download_file_queue.csv", RESULT_DIR / "first_batch_manual_download_handoff_summary.csv", REPORT_DIR / "first_batch_manual_download_handoff.md"],
        "" if counts["first_batch_manual_download_handoff"] > 0 else "run script/40_build_first_batch_manual_download_handoff.py after first-batch access probe and verification workbook generation",
    )
    add(
        "cross_phase_first_batch_public_documentation_audit",
        "phase2",
        "Save first-batch public catalogs, metadata exports, data dictionaries, PDF documentation, and related-material snapshots before raw microdata access.",
        status_done(counts["first_batch_public_documentation_audit"] > 0 and counts["first_batch_public_documentation_summary"] > 0),
        f"documentation rows={counts['first_batch_public_documentation_audit']}; summary rows={counts['first_batch_public_documentation_summary']}; saved/reused rows={counts['first_batch_public_documentation_saved']}; failed rows={counts['first_batch_public_documentation_failed']}",
        [TEMP_DIR / "first_batch_public_documentation_audit.csv", RESULT_DIR / "first_batch_public_documentation_summary.csv", REPORT_DIR / "first_batch_public_documentation_audit.md"],
        "" if counts["first_batch_public_documentation_audit"] > 0 else "run script/41_build_first_batch_public_documentation_audit.py after first-batch manual download handoff generation",
    )
    add(
        "cross_phase_first_batch_file_source_traceability",
        "phase2",
        "Trace each first-batch manual-download file target to public schema files and candidate variable metadata before raw download.",
        status_done(counts["first_batch_file_source_traceability"] > 0 and counts["first_batch_file_source_traceability_summary"] > 0),
        f"trace rows={counts['first_batch_file_source_traceability']}; summary rows={counts['first_batch_file_source_traceability_summary']}; supported rows={counts['first_batch_file_source_supported']}; unsupported rows={counts['first_batch_file_source_unsupported']}",
        [TEMP_DIR / "first_batch_file_source_traceability.csv", RESULT_DIR / "first_batch_file_source_traceability_summary.csv", REPORT_DIR / "first_batch_file_source_traceability.md"],
        "" if counts["first_batch_file_source_traceability"] > 0 else "run script/42_build_first_batch_file_source_traceability.py after first-batch public documentation audit generation",
    )
    add(
        "cross_phase_first_batch_merge_key_lineage_plan",
        "phase3",
        "Map candidate household/person keys, survey design variables, timing variables, geography variables, and file lineage before raw harmonization.",
        status_done(
            counts["first_batch_merge_key_lineage_plan"] > 0
            and counts["first_batch_merge_key_candidates"] > 0
            and counts["first_batch_merge_key_lineage_summary"] > 0
        ),
        f"plan rows={counts['first_batch_merge_key_lineage_plan']}; candidate rows={counts['first_batch_merge_key_candidates']}; summary rows={counts['first_batch_merge_key_lineage_summary']}; planned rows={counts['first_batch_merge_key_planned']}; raw-ready rows={counts['first_batch_merge_key_raw_ready']}",
        [TEMP_DIR / "first_batch_merge_key_lineage_plan.csv", TEMP_DIR / "first_batch_merge_key_candidate_variables.csv", RESULT_DIR / "first_batch_merge_key_lineage_summary.csv", REPORT_DIR / "first_batch_merge_key_lineage_plan.md"],
        "" if counts["first_batch_merge_key_lineage_plan"] > 0 else "run script/43_build_first_batch_merge_key_lineage_plan.py after first-batch file-source traceability generation",
    )
    add(
        "cross_phase_first_batch_raw_value_key_audit",
        "phase3",
        "Read observed raw values and file-level key cardinality for raw-ready first-batch datasets before any harmonization recipe promotion.",
        status_done(
            counts["first_batch_raw_value_key_audit"] > 0
            and counts["first_batch_raw_merge_key_audit"] > 0
            and counts["first_batch_raw_value_key_summary"] > 0
            and counts["first_batch_harmonization_value_audit_auto"] > 0
            and counts["first_batch_harmonization_value_audit_auto_ready"] == 0
        ),
        f"value rows={counts['first_batch_raw_value_key_audit']}; value read-ok rows={counts['first_batch_raw_value_key_read_ok']}; key rows={counts['first_batch_raw_merge_key_audit']}; key read-ok rows={counts['first_batch_raw_merge_key_read_ok']}; auto value rows={counts['first_batch_harmonization_value_audit_auto']}; auto ready-for-recipe rows={counts['first_batch_harmonization_value_audit_auto_ready']}",
        [TEMP_DIR / "first_batch_raw_value_key_audit.csv", TEMP_DIR / "first_batch_raw_merge_key_audit.csv", TEMP_DIR / "first_batch_harmonization_value_audit_auto.csv", RESULT_DIR / "first_batch_raw_value_key_summary.csv", REPORT_DIR / "first_batch_raw_value_key_audit.md"],
        "" if counts["first_batch_raw_value_key_audit"] > 0 else "run script/45_audit_first_batch_raw_value_keys.py after first-batch merge-key lineage planning",
    )
    add(
        "cross_phase_alb2002_household_core_merge_audit",
        "phase3",
        "Build a temp-only ALB_2002 household core candidate with observed raw timing/geography evidence, and keep it out of data until outcome semantics and climate crosswalk pass.",
        status_done(
            counts["alb2002_household_core_candidate"] > 0
            and counts["alb2002_household_core_merge_audit"] > 0
            and counts["alb2002_household_core_lineage"] > 0
            and counts["alb2002_household_core_candidate_summary"] > 0
            and counts["alb2002_household_core_recipe_ready_rows"] == 0
        ),
        f"candidate rows={counts['alb2002_household_core_candidate']}; merge audit rows={counts['alb2002_household_core_merge_audit']}; lineage rows={counts['alb2002_household_core_lineage']}; summary rows={counts['alb2002_household_core_candidate_summary']}; recipe-ready rows={counts['alb2002_household_core_recipe_ready_rows']}",
        [TEMP_DIR / "alb2002_household_core_candidate.csv", TEMP_DIR / "alb2002_household_core_merge_audit.csv", TEMP_DIR / "alb2002_household_core_lineage.csv", RESULT_DIR / "alb2002_household_core_candidate_summary.csv", REPORT_DIR / "alb2002_household_core_merge_audit.md"],
        "" if counts["alb2002_household_core_candidate"] > 0 and counts["alb2002_household_core_recipe_ready_rows"] == 0 else "run script/54_audit_alb2002_household_core_merge.py and keep the output temp-only",
    )
    add(
        "cross_phase_alb2002_provisional_outcome_feasibility",
        "phase4",
        "Compute ALB_2002 provisional outcome event-rate diagnostics only after raw household-core assembly, and keep all final outcome promotion blocked.",
        status_done(
            counts["alb2002_provisional_outcome_feasibility_audit"] > 0
            and counts["alb2002_provisional_outcome_feasibility_summary"] > 0
            and counts["alb2002_provisional_outcome_ready_rows"] == 0
        ),
        f"audit rows={counts['alb2002_provisional_outcome_feasibility_audit']}; summary rows={counts['alb2002_provisional_outcome_feasibility_summary']}; ready rows={counts['alb2002_provisional_outcome_ready_rows']}",
        [TEMP_DIR / "alb2002_provisional_outcome_feasibility_audit.csv", RESULT_DIR / "alb2002_provisional_outcome_feasibility_summary.csv", REPORT_DIR / "alb2002_provisional_outcome_feasibility.md"],
        "" if counts["alb2002_provisional_outcome_feasibility_audit"] > 0 and counts["alb2002_provisional_outcome_ready_rows"] == 0 else "run script/55_audit_alb2002_provisional_outcome_feasibility.py and keep provisional outcome promotion blocked",
    )
    add(
        "cross_phase_alb2002_outcome_semantics_raw_value_audit",
        "phase4",
        "Audit ALB_2002 raw health-module labels, values, recall periods, units, and skip-pattern blockers before any final OOP/access outcome promotion.",
        status_done(
            counts["alb2002_outcome_semantics_raw_value_audit"] > 0
            and counts["alb2002_outcome_semantics_raw_value_summary"] > 0
            and counts["alb2002_outcome_semantics_outcome_ready_rows"] == 0
            and counts["alb2002_outcome_semantics_sdg382_ready_rows"] == 0
        ),
        f"audit rows={counts['alb2002_outcome_semantics_raw_value_audit']}; summary rows={counts['alb2002_outcome_semantics_raw_value_summary']}; OOP candidate rows={counts['alb2002_outcome_semantics_financial_oop_candidate_rows']}; access candidate rows={counts['alb2002_outcome_semantics_access_candidate_rows']}; conditional reason rows={counts['alb2002_outcome_semantics_conditional_reason_rows']}; outcome-ready rows={counts['alb2002_outcome_semantics_outcome_ready_rows']}; SDG382-ready rows={counts['alb2002_outcome_semantics_sdg382_ready_rows']}",
        [TEMP_DIR / "alb2002_outcome_semantics_raw_value_audit.csv", RESULT_DIR / "alb2002_outcome_semantics_raw_value_summary.csv", REPORT_DIR / "alb2002_outcome_semantics_raw_value_audit.md"],
        "" if counts["alb2002_outcome_semantics_raw_value_audit"] > 0 and counts["alb2002_outcome_semantics_outcome_ready_rows"] == 0 else "run script/60_audit_alb2002_outcome_semantics_raw_values.py and keep ALB_2002 raw outcomes blocked",
    )
    add(
        "cross_phase_alb2002_health_questionnaire_semantics_audit",
        "phase4",
        "Audit ALB_2002 health questionnaire text and raw skip paths for payment unit, recall-period, gift scope, access-barrier code, and zero/missing semantics before outcome promotion.",
        status_done(
            counts["alb2002_health_questionnaire_semantics_audit"] > 0
            and counts["alb2002_health_questionnaire_semantics_summary"] > 0
            and counts["alb2002_health_questionnaire_semantics_rows"] > 0
            and counts["alb2002_health_questionnaire_oop_item_rows"] == 25
            and counts["alb2002_health_questionnaire_gift_item_rows"] == 6
            and counts["alb2002_health_questionnaire_new_lek_unit_rows"] > 0
            and counts["alb2002_health_questionnaire_four_week_oop_rows"] == 17
            and counts["alb2002_health_questionnaire_twelve_month_oop_rows"] == 8
            and counts["alb2002_health_questionnaire_payment_positive_when_not_triggered_rows"] == 0
            and counts["alb2002_health_questionnaire_outcome_ready_rows"] == 0
            and counts["alb2002_health_questionnaire_sdg382_ready_rows"] == 0
            and counts["alb2002_health_questionnaire_climate_linkage_ready_rows"] == 0
        ),
        f"rows={counts['alb2002_health_questionnaire_semantics_rows']}; OOP item rows={counts['alb2002_health_questionnaire_oop_item_rows']}; gift rows={counts['alb2002_health_questionnaire_gift_item_rows']}; NEW LEKS rows={counts['alb2002_health_questionnaire_new_lek_unit_rows']}; four-week OOP rows={counts['alb2002_health_questionnaire_four_week_oop_rows']}; twelve-month OOP rows={counts['alb2002_health_questionnaire_twelve_month_oop_rows']}; positive skipped-payment rows={counts['alb2002_health_questionnaire_payment_positive_when_not_triggered_rows']}; outcome-ready rows={counts['alb2002_health_questionnaire_outcome_ready_rows']}; SDG382-ready rows={counts['alb2002_health_questionnaire_sdg382_ready_rows']}; climate-linkage-ready rows={counts['alb2002_health_questionnaire_climate_linkage_ready_rows']}; decision={counts['alb2002_health_questionnaire_current_decision']}",
        [TEMP_DIR / "alb2002_health_questionnaire_semantics_audit.csv", RESULT_DIR / "alb2002_health_questionnaire_semantics_summary.csv", REPORT_DIR / "alb2002_health_questionnaire_semantics_audit.md"],
        "" if counts["alb2002_health_questionnaire_semantics_audit"] > 0 and counts["alb2002_health_questionnaire_outcome_ready_rows"] == 0 and counts["alb2002_health_questionnaire_climate_linkage_ready_rows"] == 0 else "run script/89_audit_alb2002_health_questionnaire_semantics.py and keep ALB_2002 outcomes blocked until denominator, SDG, and climate gates pass",
    )
    add(
        "cross_phase_alb2002_oop_aggregation_policy_audit",
        "phase4",
        "Audit ALB_2002 OOP aggregation policy variants and CHE stress-test rates before promoting financial-protection outcomes.",
        status_done(
            counts["alb2002_oop_aggregation_policy_audit"] > 0
            and counts["alb2002_oop_aggregation_policy_summary"] > 0
            and counts["alb2002_oop_aggregation_policy_rows"] == 11
            and counts["alb2002_oop_aggregation_policy_core_4w_match_rows"] == 3599
            and counts["alb2002_oop_aggregation_policy_core_12m_match_rows"] == 3599
            and counts["alb2002_oop_aggregation_policy_outcome_ready_rows"] == 0
            and counts["alb2002_oop_aggregation_policy_recipe_ready_rows"] == 0
            and counts["alb2002_oop_aggregation_policy_sdg382_ready_rows"] == 0
            and counts["alb2002_oop_aggregation_policy_climate_linkage_ready_rows"] == 0
        ),
        f"policy rows={counts['alb2002_oop_aggregation_policy_rows']}; core 4w match rows={counts['alb2002_oop_aggregation_policy_core_4w_match_rows']}; core 12m match rows={counts['alb2002_oop_aggregation_policy_core_12m_match_rows']}; outcome-ready rows={counts['alb2002_oop_aggregation_policy_outcome_ready_rows']}; recipe-ready rows={counts['alb2002_oop_aggregation_policy_recipe_ready_rows']}; SDG382-ready rows={counts['alb2002_oop_aggregation_policy_sdg382_ready_rows']}; climate-linkage-ready rows={counts['alb2002_oop_aggregation_policy_climate_linkage_ready_rows']}; decision={counts['alb2002_oop_aggregation_policy_current_decision']}",
        [TEMP_DIR / "alb2002_oop_aggregation_policy_audit.csv", RESULT_DIR / "alb2002_oop_aggregation_policy_summary.csv", REPORT_DIR / "alb2002_oop_aggregation_policy_audit.md"],
        "" if counts["alb2002_oop_aggregation_policy_audit"] > 0 and counts["alb2002_oop_aggregation_policy_outcome_ready_rows"] == 0 and counts["alb2002_oop_aggregation_policy_climate_linkage_ready_rows"] == 0 else "run script/91_audit_alb2002_oop_aggregation_policy.py and keep ALB_2002 OOP outcomes blocked until scope, recall, SDG, and climate gates pass",
    )
    add(
        "cross_phase_alb2002_skip_missing_semantics_audit",
        "phase4",
        "Audit ALB_2002 skipped payment zero/missing semantics before any OOP or access outcome promotion.",
        status_done(
            counts["alb2002_skip_missing_semantics_audit"] > 0
            and counts["alb2002_skip_missing_semantics_summary"] > 0
            and counts["alb2002_skip_missing_semantics_rows"] == 12
            and counts["alb2002_skip_missing_payment_block_rows"] == 7
            and counts["alb2002_skip_missing_access_condition_rows"] == 5
            and counts["alb2002_skip_missing_payment_positive_when_not_triggered_rows"] == 0
            and counts["alb2002_skip_missing_payment_zero_cells_when_not_triggered"] == 11
            and counts["alb2002_skip_missing_payment_positive_cells_when_not_triggered"] == 0
            and counts["alb2002_skip_missing_outcome_ready_rows"] == 0
            and counts["alb2002_skip_missing_recipe_ready_rows"] == 0
            and counts["alb2002_skip_missing_sdg382_ready_rows"] == 0
            and counts["alb2002_skip_missing_climate_linkage_ready_rows"] == 0
        ),
        f"rows={counts['alb2002_skip_missing_semantics_rows']}; payment blocks={counts['alb2002_skip_missing_payment_block_rows']}; access condition blocks={counts['alb2002_skip_missing_access_condition_rows']}; positive skipped-payment rows={counts['alb2002_skip_missing_payment_positive_when_not_triggered_rows']}; zero skipped-payment cells={counts['alb2002_skip_missing_payment_zero_cells_when_not_triggered']}; positive skipped-payment cells={counts['alb2002_skip_missing_payment_positive_cells_when_not_triggered']}; outcome-ready rows={counts['alb2002_skip_missing_outcome_ready_rows']}; recipe-ready rows={counts['alb2002_skip_missing_recipe_ready_rows']}; SDG382-ready rows={counts['alb2002_skip_missing_sdg382_ready_rows']}; climate-linkage-ready rows={counts['alb2002_skip_missing_climate_linkage_ready_rows']}; decision={counts['alb2002_skip_missing_current_decision']}",
        [TEMP_DIR / "alb2002_skip_missing_semantics_audit.csv", RESULT_DIR / "alb2002_skip_missing_semantics_summary.csv", REPORT_DIR / "alb2002_skip_missing_semantics_audit.md"],
        "" if counts["alb2002_skip_missing_semantics_audit"] > 0 and counts["alb2002_skip_missing_payment_positive_when_not_triggered_rows"] == 0 and counts["alb2002_skip_missing_payment_positive_cells_when_not_triggered"] == 0 and counts["alb2002_skip_missing_outcome_ready_rows"] == 0 and counts["alb2002_skip_missing_climate_linkage_ready_rows"] == 0 else "run script/92_audit_alb2002_skip_missing_semantics.py and keep ALB_2002 outcomes blocked until zero/missing policy, OOP scope, SDG, and climate gates pass",
    )
    add(
        "cross_phase_alb2002_oop_skip_value_decision_audit",
        "phase4",
        "Document the ALB_2002 skipped-payment no-positive-leakage decision before narrowing the OOP aggregation blocker.",
        status_done(
            counts["alb2002_oop_skip_value_decision_audit"] > 0
            and counts["alb2002_oop_skip_value_decision_summary"] > 0
            and counts["alb2002_oop_skip_value_decision_rows"] == 5
            and counts["alb2002_oop_skip_value_payment_block_rows"] == 7
            and counts["alb2002_oop_skip_value_access_condition_block_rows"] == 5
            and counts["alb2002_oop_skip_value_payment_nonmissing_skipped_rows"] == 11
            and counts["alb2002_oop_skip_value_payment_nonmissing_skipped_cells"] == 11
            and counts["alb2002_oop_skip_value_payment_zero_skipped_cells"] == 11
            and counts["alb2002_oop_skip_value_payment_positive_skipped_rows"] == 0
            and counts["alb2002_oop_skip_value_payment_positive_skipped_cells"] == 0
            and counts["alb2002_oop_skip_value_zero_skip_policy_ready_rows"] == 4
            and counts["alb2002_oop_skip_value_oop_recall_scope_ready_rows"] == 0
            and counts["alb2002_oop_skip_value_oop_inclusion_scope_ready_rows"] == 0
            and counts["alb2002_oop_skip_value_recipe_ready_rows"] == 0
            and counts["alb2002_oop_skip_value_outcome_ready_rows"] == 0
            and counts["alb2002_oop_skip_value_sdg382_ready_rows"] == 0
            and counts["alb2002_oop_skip_value_climate_linkage_ready_rows"] == 0
            and counts["alb2002_oop_skip_value_current_decision"] == "documented_alb2002_oop_skipped_values_zero_only_but_oop_policy_not_ready"
        ),
        f"audit rows={counts['alb2002_oop_skip_value_decision_audit']}; summary rows={counts['alb2002_oop_skip_value_decision_summary']}; decision rows={counts['alb2002_oop_skip_value_decision_rows']}; payment blocks={counts['alb2002_oop_skip_value_payment_block_rows']}; access condition blocks={counts['alb2002_oop_skip_value_access_condition_block_rows']}; nonmissing skipped rows={counts['alb2002_oop_skip_value_payment_nonmissing_skipped_rows']}; nonmissing skipped cells={counts['alb2002_oop_skip_value_payment_nonmissing_skipped_cells']}; zero skipped cells={counts['alb2002_oop_skip_value_payment_zero_skipped_cells']}; positive skipped rows={counts['alb2002_oop_skip_value_payment_positive_skipped_rows']}; positive skipped cells={counts['alb2002_oop_skip_value_payment_positive_skipped_cells']}; zero-skip ready rows={counts['alb2002_oop_skip_value_zero_skip_policy_ready_rows']}; recall-ready rows={counts['alb2002_oop_skip_value_oop_recall_scope_ready_rows']}; inclusion-ready rows={counts['alb2002_oop_skip_value_oop_inclusion_scope_ready_rows']}; recipe-ready rows={counts['alb2002_oop_skip_value_recipe_ready_rows']}; outcome-ready rows={counts['alb2002_oop_skip_value_outcome_ready_rows']}; SDG382-ready rows={counts['alb2002_oop_skip_value_sdg382_ready_rows']}; climate-linkage-ready rows={counts['alb2002_oop_skip_value_climate_linkage_ready_rows']}; decision={counts['alb2002_oop_skip_value_current_decision']}",
        [TEMP_DIR / "alb2002_oop_skip_value_decision_audit.csv", RESULT_DIR / "alb2002_oop_skip_value_decision_summary.csv", REPORT_DIR / "alb2002_oop_skip_value_decision_audit.md"],
        "" if counts["alb2002_oop_skip_value_decision_audit"] > 0 and counts["alb2002_oop_skip_value_payment_positive_skipped_rows"] == 0 and counts["alb2002_oop_skip_value_payment_positive_skipped_cells"] == 0 and counts["alb2002_oop_skip_value_outcome_ready_rows"] == 0 and counts["alb2002_oop_skip_value_climate_linkage_ready_rows"] == 0 else "run script/97_audit_alb2002_oop_skip_value_decision.py and keep ALB_2002 OOP outcomes blocked until recall, inclusion, denominator, access, SDG, and climate gates pass",
    )
    add(
        "cross_phase_alb2002_access_need_denominator_policy_audit",
        "phase4",
        "Audit ALB_2002 access and health-need denominator policies before promoting forgone-care or double-failure outcomes.",
        status_done(
            counts["alb2002_access_need_denominator_policy_audit"] > 0
            and counts["alb2002_access_need_denominator_policy_summary"] > 0
            and counts["alb2002_access_need_denominator_policy_rows"] == 24
            and counts["alb2002_access_need_household_rows"] == 3599
            and counts["alb2002_access_need_q01_need_rows"] == 3247
            and counts["alb2002_access_need_person_need_household_rows"] == 2202
            and counts["alb2002_access_need_composite_any_access_barrier_rows"] == 1861
            and counts["alb2002_access_need_outcome_ready_rows"] == 0
            and counts["alb2002_access_need_recipe_ready_rows"] == 0
            and counts["alb2002_access_need_sdg382_ready_rows"] == 0
            and counts["alb2002_access_need_climate_linkage_ready_rows"] == 0
        ),
        f"rows={counts['alb2002_access_need_denominator_policy_rows']}; households={counts['alb2002_access_need_household_rows']}; q01 need rows={counts['alb2002_access_need_q01_need_rows']}; person need rows={counts['alb2002_access_need_person_need_household_rows']}; delayed rows={counts['alb2002_access_need_delayed_help_rows']}; referral-not-gone rows={counts['alb2002_access_need_referral_not_gone_rows']}; refused rows={counts['alb2002_access_need_refused_service_rows']}; composite any-access-barrier rows={counts['alb2002_access_need_composite_any_access_barrier_rows']}; low-event rows={counts['alb2002_access_need_low_event_rate_rows']}; outcome-ready rows={counts['alb2002_access_need_outcome_ready_rows']}; recipe-ready rows={counts['alb2002_access_need_recipe_ready_rows']}; SDG382-ready rows={counts['alb2002_access_need_sdg382_ready_rows']}; climate-linkage-ready rows={counts['alb2002_access_need_climate_linkage_ready_rows']}; decision={counts['alb2002_access_need_current_decision']}",
        [TEMP_DIR / "alb2002_access_need_denominator_policy_audit.csv", RESULT_DIR / "alb2002_access_need_denominator_policy_summary.csv", REPORT_DIR / "alb2002_access_need_denominator_policy_audit.md"],
        "" if counts["alb2002_access_need_denominator_policy_audit"] > 0 and counts["alb2002_access_need_outcome_ready_rows"] == 0 and counts["alb2002_access_need_climate_linkage_ready_rows"] == 0 else "run script/93_audit_alb2002_access_need_denominator_policy.py and keep ALB_2002 access outcomes blocked until denominator policy, OOP, SDG, and climate gates pass",
    )
    add(
        "cross_phase_alb2002_consumption_sdg_denominator_policy_audit",
        "phase4",
        "Audit ALB_2002 total-consumption, CHE, and SDG 3.8.2 denominator policy before promoting financial-protection outcomes.",
        status_done(
            counts["alb2002_consumption_sdg_denominator_policy_audit"] > 0
            and counts["alb2002_consumption_sdg_denominator_policy_summary"] > 0
            and counts["alb2002_consumption_sdg_denominator_policy_rows"] == 14
            and counts["alb2002_consumption_sdg_household_rows"] == 3599
            and counts["alb2002_consumption_sdg_positive_total_consumption_rows"] == 3599
            and counts["alb2002_consumption_sdg_positive_household_weight_rows"] == 3599
            and counts["alb2002_consumption_sdg_positive_household_size_rows"] == 3599
            and counts["alb2002_consumption_sdg_spl_ready_rows"] == 0
            and counts["alb2002_consumption_sdg_ppp_cpi_ready_rows"] == 0
            and counts["alb2002_consumption_sdg_discretionary_budget_ready_rows"] == 0
            and counts["alb2002_consumption_sdg_che_denominator_ready_rows"] == 0
            and counts["alb2002_consumption_sdg_recipe_ready_rows"] == 0
            and counts["alb2002_consumption_sdg_outcome_ready_rows"] == 0
            and counts["alb2002_consumption_sdg_sdg382_ready_rows"] == 0
            and counts["alb2002_consumption_sdg_climate_linkage_ready_rows"] == 0
        ),
        f"rows={counts['alb2002_consumption_sdg_denominator_policy_rows']}; households={counts['alb2002_consumption_sdg_household_rows']}; positive total rows={counts['alb2002_consumption_sdg_positive_total_consumption_rows']}; positive weight rows={counts['alb2002_consumption_sdg_positive_household_weight_rows']}; positive household-size rows={counts['alb2002_consumption_sdg_positive_household_size_rows']}; SPL-ready rows={counts['alb2002_consumption_sdg_spl_ready_rows']}; PPP/CPI-ready rows={counts['alb2002_consumption_sdg_ppp_cpi_ready_rows']}; discretionary-budget-ready rows={counts['alb2002_consumption_sdg_discretionary_budget_ready_rows']}; CHE-denominator-ready rows={counts['alb2002_consumption_sdg_che_denominator_ready_rows']}; recipe-ready rows={counts['alb2002_consumption_sdg_recipe_ready_rows']}; outcome-ready rows={counts['alb2002_consumption_sdg_outcome_ready_rows']}; SDG382-ready rows={counts['alb2002_consumption_sdg_sdg382_ready_rows']}; climate-linkage-ready rows={counts['alb2002_consumption_sdg_climate_linkage_ready_rows']}; decision={counts['alb2002_consumption_sdg_current_decision']}",
        [TEMP_DIR / "alb2002_consumption_sdg_denominator_policy_audit.csv", RESULT_DIR / "alb2002_consumption_sdg_denominator_policy_summary.csv", REPORT_DIR / "alb2002_consumption_sdg_denominator_policy_audit.md"],
        "" if counts["alb2002_consumption_sdg_denominator_policy_audit"] > 0 and counts["alb2002_consumption_sdg_outcome_ready_rows"] == 0 and counts["alb2002_consumption_sdg_sdg382_ready_rows"] == 0 and counts["alb2002_consumption_sdg_climate_linkage_ready_rows"] == 0 else "run script/94_audit_alb2002_consumption_sdg_denominator_policy.py and keep ALB_2002 financial outcomes blocked until consumption unit/period, OOP alignment, SPL, PPP/CPI, discretionary budget, and climate gates pass",
    )
    add(
        "cross_phase_alb2002_consumption_construction_source_audit",
        "phase4",
        "Use public ALB_2002 IHSN PDF, Stata code, and metadata JSON to document the total-budget denominator variant before any outcome promotion.",
        status_done(
            counts["alb2002_consumption_construction_source_audit"] > 0
            and counts["alb2002_consumption_construction_source_summary"] > 0
            and counts["alb2002_consumption_construction_source_audit_rows"] == 9
            and counts["alb2002_consumption_construction_public_pdf_present"] == 1
            and counts["alb2002_consumption_construction_program_zip_present"] == 1
            and counts["alb2002_consumption_construction_do_file_rows"] == 19
            and counts["alb2002_consumption_construction_totcons_do_present"] == 1
            and counts["alb2002_consumption_construction_poverty_do_present"] == 1
            and counts["alb2002_consumption_construction_metadata_json_present"] == 1
            and counts["alb2002_consumption_construction_documentation_ready_rows"] == 9
            and counts["alb2002_consumption_construction_released_variable_mapping_ready_rows"] == 3
            and counts["alb2002_consumption_construction_denominator_variant_ready_rows"] == 8
            and counts["alb2002_consumption_construction_recipe_ready_rows"] == 0
            and counts["alb2002_consumption_construction_outcome_ready_rows"] == 0
            and counts["alb2002_consumption_construction_sdg382_ready_rows"] == 0
            and counts["alb2002_consumption_construction_climate_linkage_ready_rows"] == 0
            and counts["alb2002_consumption_construction_current_decision"] == "documented_alb2002_consumption_aggregate_but_not_outcome_sdg_climate_ready"
        ),
        f"audit rows={counts['alb2002_consumption_construction_source_audit']}; summary rows={counts['alb2002_consumption_construction_source_summary']}; source rows={counts['alb2002_consumption_construction_source_audit_rows']}; public PDF={counts['alb2002_consumption_construction_public_pdf_present']}; program ZIP={counts['alb2002_consumption_construction_program_zip_present']}; do-file rows={counts['alb2002_consumption_construction_do_file_rows']}; totcons.do={counts['alb2002_consumption_construction_totcons_do_present']}; poverty.do={counts['alb2002_consumption_construction_poverty_do_present']}; metadata JSON={counts['alb2002_consumption_construction_metadata_json_present']}; documentation-ready rows={counts['alb2002_consumption_construction_documentation_ready_rows']}; released-variable-mapping rows={counts['alb2002_consumption_construction_released_variable_mapping_ready_rows']}; denominator-variant rows={counts['alb2002_consumption_construction_denominator_variant_ready_rows']}; recipe-ready rows={counts['alb2002_consumption_construction_recipe_ready_rows']}; outcome-ready rows={counts['alb2002_consumption_construction_outcome_ready_rows']}; SDG382-ready rows={counts['alb2002_consumption_construction_sdg382_ready_rows']}; climate-linkage-ready rows={counts['alb2002_consumption_construction_climate_linkage_ready_rows']}; decision={counts['alb2002_consumption_construction_current_decision']}",
        [TEMP_DIR / "alb2002_consumption_construction_source_audit.csv", RESULT_DIR / "alb2002_consumption_construction_source_summary.csv", REPORT_DIR / "alb2002_consumption_construction_source_audit.md"],
        "" if counts["alb2002_consumption_construction_source_audit"] > 0 and counts["alb2002_consumption_construction_documentation_ready_rows"] == 9 and counts["alb2002_consumption_construction_outcome_ready_rows"] == 0 and counts["alb2002_consumption_construction_sdg382_ready_rows"] == 0 and counts["alb2002_consumption_construction_climate_linkage_ready_rows"] == 0 else "run script/96_audit_alb2002_consumption_construction_sources.py and keep ALB_2002 outcome, SDG, and climate promotion blocked after denominator documentation",
    )
    add(
        "cross_phase_alb2002_consumption_aggregate_metadata_crosswalk_audit",
        "phase4",
        "Crosswalk ALB_2002 raw `totcons` evidence against public source documentation before accepting it as a documented total-budget candidate.",
        status_done(
            counts["alb2002_consumption_aggregate_crosswalk_audit"] > 0
            and counts["alb2002_consumption_aggregate_crosswalk_summary"] > 0
            and counts["alb2002_consumption_aggregate_crosswalk_rows"] == 11
            and counts["alb2002_consumption_aggregate_crosswalk_local_poverty_rows"] == 3599
            and counts["alb2002_consumption_aggregate_crosswalk_metadata_catalog_rows"] == 0
            and counts["alb2002_consumption_aggregate_crosswalk_raw_totcons_positive_rows"] == 3599
            and counts["alb2002_consumption_aggregate_crosswalk_candidate_totcons_match_rows"] == 3599
            and counts["alb2002_consumption_aggregate_crosswalk_questionnaire_aggregate_formula_hits"] == 0
            and counts["alb2002_consumption_aggregate_crosswalk_construction_source_rows"] == 9
            and counts["alb2002_consumption_aggregate_crosswalk_construction_do_file_rows"] == 19
            and counts["alb2002_consumption_aggregate_crosswalk_metadata_unit_period_ready_rows"] == 8
            and counts["alb2002_consumption_aggregate_crosswalk_official_documentation_ready_rows"] == 9
            and counts["alb2002_consumption_aggregate_crosswalk_released_variable_mapping_ready_rows"] == 3
            and counts["alb2002_consumption_aggregate_crosswalk_denominator_variant_ready_rows"] == 8
            and counts["alb2002_consumption_aggregate_crosswalk_recipe_ready_rows"] == 0
            and counts["alb2002_consumption_aggregate_crosswalk_outcome_ready_rows"] == 0
            and counts["alb2002_consumption_aggregate_crosswalk_sdg382_ready_rows"] == 0
            and counts["alb2002_consumption_aggregate_crosswalk_climate_linkage_ready_rows"] == 0
            and counts["alb2002_consumption_aggregate_crosswalk_current_decision"] == "documented_alb2002_consumption_aggregate_but_not_outcome_sdg_climate_ready"
        ),
        f"audit rows={counts['alb2002_consumption_aggregate_crosswalk_audit']}; summary rows={counts['alb2002_consumption_aggregate_crosswalk_summary']}; evidence rows={counts['alb2002_consumption_aggregate_crosswalk_rows']}; local poverty rows={counts['alb2002_consumption_aggregate_crosswalk_local_poverty_rows']}; metadata catalog rows={counts['alb2002_consumption_aggregate_crosswalk_metadata_catalog_rows']}; raw totcons positive rows={counts['alb2002_consumption_aggregate_crosswalk_raw_totcons_positive_rows']}; candidate totcons match rows={counts['alb2002_consumption_aggregate_crosswalk_candidate_totcons_match_rows']}; questionnaire aggregate-formula hits={counts['alb2002_consumption_aggregate_crosswalk_questionnaire_aggregate_formula_hits']}; construction-source rows={counts['alb2002_consumption_aggregate_crosswalk_construction_source_rows']}; construction do-file rows={counts['alb2002_consumption_aggregate_crosswalk_construction_do_file_rows']}; metadata unit/period ready rows={counts['alb2002_consumption_aggregate_crosswalk_metadata_unit_period_ready_rows']}; documentation-ready rows={counts['alb2002_consumption_aggregate_crosswalk_official_documentation_ready_rows']}; released-variable-mapping rows={counts['alb2002_consumption_aggregate_crosswalk_released_variable_mapping_ready_rows']}; denominator-variant rows={counts['alb2002_consumption_aggregate_crosswalk_denominator_variant_ready_rows']}; recipe-ready rows={counts['alb2002_consumption_aggregate_crosswalk_recipe_ready_rows']}; outcome-ready rows={counts['alb2002_consumption_aggregate_crosswalk_outcome_ready_rows']}; SDG382-ready rows={counts['alb2002_consumption_aggregate_crosswalk_sdg382_ready_rows']}; climate-linkage-ready rows={counts['alb2002_consumption_aggregate_crosswalk_climate_linkage_ready_rows']}; decision={counts['alb2002_consumption_aggregate_crosswalk_current_decision']}",
        [TEMP_DIR / "alb2002_consumption_aggregate_metadata_crosswalk_audit.csv", RESULT_DIR / "alb2002_consumption_aggregate_metadata_crosswalk_summary.csv", REPORT_DIR / "alb2002_consumption_aggregate_metadata_crosswalk_audit.md"],
        "" if counts["alb2002_consumption_aggregate_crosswalk_audit"] > 0 and counts["alb2002_consumption_aggregate_crosswalk_official_documentation_ready_rows"] == 9 and counts["alb2002_consumption_aggregate_crosswalk_outcome_ready_rows"] == 0 and counts["alb2002_consumption_aggregate_crosswalk_sdg382_ready_rows"] == 0 and counts["alb2002_consumption_aggregate_crosswalk_climate_linkage_ready_rows"] == 0 else "run script/96_audit_alb2002_consumption_construction_sources.py then script/95_audit_alb2002_consumption_aggregate_metadata_crosswalk.py; keep outcome, SDG, and climate gates closed until OOP, SPL/PPP/CPI, discretionary-budget, and geography evidence passes",
    )
    add(
        "cross_phase_alb2002_period_aligned_che_policy_audit",
        "phase4",
        "Align ALB_2002 four-week and twelve-month OOP candidates to the documented monthly total-budget denominator before any CHE outcome promotion.",
        status_done(
            counts["alb2002_period_aligned_che_audit"] > 0
            and counts["alb2002_period_aligned_che_summary"] > 0
            and counts["alb2002_period_aligned_che_policy_rows"] == 3
            and counts["alb2002_period_aligned_che_household_rows"] == 3599
            and counts["alb2002_period_aligned_che_denominator_rows"] == 3599
            and counts["alb2002_period_aligned_che_period_alignment_ready_rows"] == 3
            and counts["alb2002_period_aligned_che_combined_che10_rate"] != ""
            and counts["alb2002_period_aligned_che_combined_che25_rate"] != ""
            and counts["alb2002_period_aligned_che_outcome_ready_rows"] == 0
            and counts["alb2002_period_aligned_che_recipe_ready_rows"] == 0
            and counts["alb2002_period_aligned_che_sdg382_ready_rows"] == 0
            and counts["alb2002_period_aligned_che_climate_linkage_ready_rows"] == 0
            and counts["alb2002_period_aligned_che_current_decision"] == "blocked_alb2002_period_aligned_che_policy_not_outcome_ready"
        ),
        f"audit rows={counts['alb2002_period_aligned_che_audit']}; summary rows={counts['alb2002_period_aligned_che_summary']}; policy rows={counts['alb2002_period_aligned_che_policy_rows']}; household rows={counts['alb2002_period_aligned_che_household_rows']}; denominator rows={counts['alb2002_period_aligned_che_denominator_rows']}; period-alignment-ready rows={counts['alb2002_period_aligned_che_period_alignment_ready_rows']}; combined CHE10={counts['alb2002_period_aligned_che_combined_che10_rate']}; combined CHE25={counts['alb2002_period_aligned_che_combined_che25_rate']}; outcome-ready rows={counts['alb2002_period_aligned_che_outcome_ready_rows']}; recipe-ready rows={counts['alb2002_period_aligned_che_recipe_ready_rows']}; SDG382-ready rows={counts['alb2002_period_aligned_che_sdg382_ready_rows']}; climate-linkage rows={counts['alb2002_period_aligned_che_climate_linkage_ready_rows']}; decision={counts['alb2002_period_aligned_che_current_decision']}",
        [TEMP_DIR / "alb2002_period_aligned_che_policy_audit.csv", RESULT_DIR / "alb2002_period_aligned_che_policy_summary.csv", REPORT_DIR / "alb2002_period_aligned_che_policy_audit.md"],
        "" if counts["alb2002_period_aligned_che_policy_rows"] == 3 and counts["alb2002_period_aligned_che_outcome_ready_rows"] == 0 and counts["alb2002_period_aligned_che_climate_linkage_ready_rows"] == 0 else "run script/99_audit_alb2002_period_aligned_che_policy.py and keep CHE outputs as stress tests until OOP inclusion, recipe, benchmark, and geography gates pass",
    )
    add(
        "cross_phase_alb2002_che_candidate_outcome_construction",
        "phase4",
        "Construct temp-only household-level ALB_2002 CHE10/CHE25 candidates from the period-aligned combined OOP policy while keeping final outcome promotion blocked.",
        status_done(
            counts["alb2002_che_candidate_household_outcomes"] == 3599
            and counts["alb2002_che_candidate_outcome_lineage"] == 6
            and counts["alb2002_che_candidate_outcome_audit"] == 4
            and counts["alb2002_che_candidate_outcome_summary"] > 0
            and counts["alb2002_che_candidate_household_rows"] == 3599
            and counts["alb2002_che_candidate_denominator_rows"] == 3599
            and counts["alb2002_che_candidate_che10_rows"] == 824
            and counts["alb2002_che_candidate_che10_rate"] == "0.228952"
            and counts["alb2002_che_candidate_che25_rows"] == 290
            and counts["alb2002_che_candidate_che25_rate"] == "0.0805779"
            and counts["alb2002_che_candidate_outcome_promotion_ready_rows"] == 0
            and counts["alb2002_che_candidate_climate_linkage_ready_rows"] == 0
            and counts["alb2002_che_candidate_current_decision"] == "blocked_alb2002_che_candidate_not_promoted_due_recipe_sdg_climate_gates"
        ),
        f"household rows={counts['alb2002_che_candidate_household_outcomes']}; lineage rows={counts['alb2002_che_candidate_outcome_lineage']}; audit rows={counts['alb2002_che_candidate_outcome_audit']}; denominator rows={counts['alb2002_che_candidate_denominator_rows']}; CHE10 rows={counts['alb2002_che_candidate_che10_rows']}; CHE10 rate={counts['alb2002_che_candidate_che10_rate']}; CHE25 rows={counts['alb2002_che_candidate_che25_rows']}; CHE25 rate={counts['alb2002_che_candidate_che25_rate']}; outcome-promotion-ready rows={counts['alb2002_che_candidate_outcome_promotion_ready_rows']}; climate-ready rows={counts['alb2002_che_candidate_climate_linkage_ready_rows']}; decision={counts['alb2002_che_candidate_current_decision']}",
        [TEMP_DIR / "alb2002_che_candidate_household_outcomes.csv", TEMP_DIR / "alb2002_che_candidate_outcome_lineage.csv", RESULT_DIR / "alb2002_che_candidate_outcome_audit.csv", RESULT_DIR / "alb2002_che_candidate_outcome_summary.csv", REPORT_DIR / "alb2002_che_candidate_outcome_audit.md"],
        "" if counts["alb2002_che_candidate_household_outcomes"] == 3599 and counts["alb2002_che_candidate_outcome_promotion_ready_rows"] == 0 and counts["alb2002_che_candidate_current_decision"] == "blocked_alb2002_che_candidate_not_promoted_due_recipe_sdg_climate_gates" else "run script/101_build_alb2002_che_candidate_outcomes.py after the period-aligned CHE and minimum recipe audits; keep household outcomes temp-only until recipe, SDG, benchmark, and climate gates pass",
    )
    add(
        "cross_phase_alb2002_access_candidate_outcome_construction",
        "phase4",
        "Construct temp-only household-level ALB_2002 access, need, barrier, and composite candidates while keeping final access outcome promotion blocked.",
        status_done(
            counts["alb2002_access_candidate_household_outcomes"] == 3599
            and counts["alb2002_access_candidate_outcome_lineage"] == 8
            and counts["alb2002_access_candidate_outcome_audit"] == 13
            and counts["alb2002_access_candidate_outcome_summary"] > 0
            and counts["alb2002_access_candidate_household_rows"] == 3599
            and counts["alb2002_access_candidate_q01_need_rows"] == 3247
            and counts["alb2002_access_candidate_person_need_rows"] == 2202
            and counts["alb2002_access_candidate_q01_cost_difficulty_rows"] == 1623
            and counts["alb2002_access_candidate_composite_cost_rows"] == 1661
            and counts["alb2002_access_candidate_composite_any_rows"] == 1861
            and counts["alb2002_access_candidate_outcome_promotion_ready_rows"] == 0
            and counts["alb2002_access_candidate_recipe_ready_rows"] == 0
            and counts["alb2002_access_candidate_climate_linkage_ready_rows"] == 0
            and counts["alb2002_access_candidate_current_decision"] == "blocked_alb2002_access_candidate_not_promoted_due_denominator_skip_climate_gates"
        ),
        f"household rows={counts['alb2002_access_candidate_household_outcomes']}; lineage rows={counts['alb2002_access_candidate_outcome_lineage']}; audit rows={counts['alb2002_access_candidate_outcome_audit']}; q01 need rows={counts['alb2002_access_candidate_q01_need_rows']}; person-need rows={counts['alb2002_access_candidate_person_need_rows']}; q01 cost rows={counts['alb2002_access_candidate_q01_cost_difficulty_rows']}; composite cost rows={counts['alb2002_access_candidate_composite_cost_rows']}; composite any rows={counts['alb2002_access_candidate_composite_any_rows']}; outcome-promotion-ready rows={counts['alb2002_access_candidate_outcome_promotion_ready_rows']}; recipe-ready rows={counts['alb2002_access_candidate_recipe_ready_rows']}; climate-ready rows={counts['alb2002_access_candidate_climate_linkage_ready_rows']}; decision={counts['alb2002_access_candidate_current_decision']}",
        [TEMP_DIR / "alb2002_access_candidate_household_outcomes.csv", TEMP_DIR / "alb2002_access_candidate_outcome_lineage.csv", RESULT_DIR / "alb2002_access_candidate_outcome_audit.csv", RESULT_DIR / "alb2002_access_candidate_outcome_summary.csv", REPORT_DIR / "alb2002_access_candidate_outcome_audit.md"],
        "" if counts["alb2002_access_candidate_household_outcomes"] == 3599 and counts["alb2002_access_candidate_outcome_promotion_ready_rows"] == 0 and counts["alb2002_access_candidate_current_decision"] == "blocked_alb2002_access_candidate_not_promoted_due_denominator_skip_climate_gates" else "run script/105_build_alb2002_access_candidate_outcomes.py after the access/need denominator policy audit; keep household access outcomes temp-only until denominator, skip, recipe, financial-alignment, and climate gates pass",
    )
    add(
        "cross_phase_alb2002_uhc_composite_candidate_outcome_construction",
        "phase4",
        "Construct temp-only household-level ALB_2002 UHC double-failure, financial-only, access-only, both-failure, and coping candidates while keeping final composite outcome promotion blocked.",
        status_done(
            counts["alb2002_uhc_composite_candidate_outcomes"] == 3599
            and counts["alb2002_uhc_composite_candidate_lineage"] == 6
            and counts["alb2002_uhc_composite_candidate_audit"] == 10
            and counts["alb2002_uhc_composite_candidate_summary"] > 0
            and counts["alb2002_uhc_composite_candidate_household_rows"] == 3599
            and counts["alb2002_uhc_composite_candidate_che10_or_access_rows"] == 2004
            and counts["alb2002_uhc_composite_candidate_che25_or_access_rows"] == 1889
            and counts["alb2002_uhc_composite_candidate_both_che10_access_rows"] == 681
            and counts["alb2002_uhc_composite_candidate_coping_rows"] == 1476
            and counts["alb2002_uhc_composite_candidate_outcome_promotion_ready_rows"] == 0
            and counts["alb2002_uhc_composite_candidate_recipe_ready_rows"] == 0
            and counts["alb2002_uhc_composite_candidate_climate_linkage_ready_rows"] == 0
            and counts["alb2002_uhc_composite_candidate_current_decision"] == "blocked_alb2002_uhc_composite_candidate_not_promoted_due_outcome_recipe_climate_gates"
        ),
        f"household rows={counts['alb2002_uhc_composite_candidate_outcomes']}; lineage rows={counts['alb2002_uhc_composite_candidate_lineage']}; audit rows={counts['alb2002_uhc_composite_candidate_audit']}; CHE10-or-access rows={counts['alb2002_uhc_composite_candidate_che10_or_access_rows']}; CHE25-or-access rows={counts['alb2002_uhc_composite_candidate_che25_or_access_rows']}; both CHE10/access rows={counts['alb2002_uhc_composite_candidate_both_che10_access_rows']}; coping rows={counts['alb2002_uhc_composite_candidate_coping_rows']}; outcome-promotion-ready rows={counts['alb2002_uhc_composite_candidate_outcome_promotion_ready_rows']}; recipe-ready rows={counts['alb2002_uhc_composite_candidate_recipe_ready_rows']}; climate-ready rows={counts['alb2002_uhc_composite_candidate_climate_linkage_ready_rows']}; decision={counts['alb2002_uhc_composite_candidate_current_decision']}",
        [TEMP_DIR / "alb2002_uhc_composite_candidate_outcomes.csv", TEMP_DIR / "alb2002_uhc_composite_candidate_lineage.csv", RESULT_DIR / "alb2002_uhc_composite_candidate_audit.csv", RESULT_DIR / "alb2002_uhc_composite_candidate_summary.csv", REPORT_DIR / "alb2002_uhc_composite_candidate_audit.md"],
        "" if counts["alb2002_uhc_composite_candidate_outcomes"] == 3599 and counts["alb2002_uhc_composite_candidate_outcome_promotion_ready_rows"] == 0 and counts["alb2002_uhc_composite_candidate_current_decision"] == "blocked_alb2002_uhc_composite_candidate_not_promoted_due_outcome_recipe_climate_gates" else "run script/106_build_alb2002_uhc_composite_candidate_outcomes.py after the CHE and access candidate builders; keep household composite outcomes temp-only until financial, access, recipe, SDG, benchmark, and climate gates pass",
    )
    add(
        "cross_phase_alb2002_joined_analysis_candidate_dataset",
        "phase3_phase4_phase5",
        "Join ALB_2002 household core, timing, weights, admin geography, access signals, and temp CHE candidates into one temp-only analysis-candidate dataset while keeping harmonized/outcome/climate promotion blocked.",
        status_done(
            counts["alb2002_analysis_candidate_dataset"] == 3599
            and counts["alb2002_analysis_candidate_lineage"] == 6
            and counts["alb2002_analysis_candidate_readiness_audit"] == 12
            and counts["alb2002_analysis_candidate_readiness_summary"] > 0
            and counts["alb2002_analysis_candidate_rows"] == 3599
            and counts["alb2002_analysis_candidate_columns"] == 49
            and counts["alb2002_analysis_candidate_complete_candidate_gates"] == 9
            and counts["alb2002_analysis_candidate_missing_gates"] == 1
            and counts["alb2002_analysis_candidate_blocked_promotion_gates"] == 2
            and counts["alb2002_analysis_candidate_harmonized_ready_rows"] == 0
            and counts["alb2002_analysis_candidate_outcome_promotion_ready_rows"] == 0
            and counts["alb2002_analysis_candidate_climate_linkage_ready_rows"] == 0
            and counts["alb2002_analysis_candidate_data_write_ready_rows"] == 0
            and counts["alb2002_analysis_candidate_current_decision"] == "blocked_alb2002_analysis_candidate_not_promoted_due_recipe_outcome_climate_gates"
        ),
        f"candidate rows={counts['alb2002_analysis_candidate_dataset']}; lineage rows={counts['alb2002_analysis_candidate_lineage']}; audit rows={counts['alb2002_analysis_candidate_readiness_audit']}; columns={counts['alb2002_analysis_candidate_columns']}; complete candidate gates={counts['alb2002_analysis_candidate_complete_candidate_gates']}; missing gates={counts['alb2002_analysis_candidate_missing_gates']}; blocked promotion gates={counts['alb2002_analysis_candidate_blocked_promotion_gates']}; harmonized-ready rows={counts['alb2002_analysis_candidate_harmonized_ready_rows']}; outcome-promotion-ready rows={counts['alb2002_analysis_candidate_outcome_promotion_ready_rows']}; climate-ready rows={counts['alb2002_analysis_candidate_climate_linkage_ready_rows']}; data-write-ready rows={counts['alb2002_analysis_candidate_data_write_ready_rows']}; decision={counts['alb2002_analysis_candidate_current_decision']}",
        [TEMP_DIR / "alb2002_analysis_candidate_dataset.csv", TEMP_DIR / "alb2002_analysis_candidate_lineage.csv", RESULT_DIR / "alb2002_analysis_candidate_readiness_audit.csv", RESULT_DIR / "alb2002_analysis_candidate_readiness_summary.csv", REPORT_DIR / "alb2002_analysis_candidate_readiness_audit.md"],
        "" if counts["alb2002_analysis_candidate_dataset"] == 3599 and counts["alb2002_analysis_candidate_data_write_ready_rows"] == 0 and counts["alb2002_analysis_candidate_current_decision"] == "blocked_alb2002_analysis_candidate_not_promoted_due_recipe_outcome_climate_gates" else "run script/102_build_alb2002_analysis_candidate_dataset.py after the CHE candidate outcome builder; keep joined candidate data temp-only until harmonization, outcome, SDG, benchmark, and climate gates pass",
    )
    add(
        "cross_phase_alb2002_climate_centroid_exposure_stress_test",
        "phase5",
        "Compute temp-only ALB_2002 district-month climate exposure stress-test summaries at candidate ADM2 centroids without promoting climate linkage.",
        status_done(
            counts["alb2002_climate_centroid_exposure_input"] == 96
            and counts["alb2002_climate_centroid_exposure_candidates"] == 384
            and counts["alb2002_climate_centroid_nasa_api_manifest"] == 36
            and counts["alb2002_climate_centroid_exposure_audit"] == 5
            and counts["alb2002_climate_centroid_input_rows"] == 96
            and counts["alb2002_climate_centroid_distinct_district_rows"] == 36
            and counts["alb2002_climate_centroid_household_rows_covered"] == 3599
            and counts["alb2002_climate_centroid_exposure_rows"] == 384
            and counts["alb2002_climate_centroid_nasa_api_rows"] == 36
            and counts["alb2002_climate_centroid_nasa_failed_rows"] == 0
            and counts["alb2002_climate_centroid_precip_nonmissing_rows"] == 384
            and counts["alb2002_climate_centroid_temp_nonmissing_rows"] == 384
            and counts["alb2002_climate_centroid_boundary_year"] == 2013
            and counts["alb2002_climate_centroid_climate_linkage_ready_rows"] == 0
            and counts["alb2002_climate_centroid_data_write_ready_rows"] == 0
            and counts["alb2002_climate_centroid_current_decision"] == "blocked_alb2002_climate_centroid_exposures_not_promoted_due_boundary_vintage_source_and_baseline_gates"
        ),
        f"input rows={counts['alb2002_climate_centroid_exposure_input']}; exposure rows={counts['alb2002_climate_centroid_exposure_candidates']}; API manifest rows={counts['alb2002_climate_centroid_nasa_api_manifest']}; audit rows={counts['alb2002_climate_centroid_exposure_audit']}; districts={counts['alb2002_climate_centroid_distinct_district_rows']}; households covered={counts['alb2002_climate_centroid_household_rows_covered']}; API failed rows={counts['alb2002_climate_centroid_nasa_failed_rows']}; precip nonmissing rows={counts['alb2002_climate_centroid_precip_nonmissing_rows']}; temp nonmissing rows={counts['alb2002_climate_centroid_temp_nonmissing_rows']}; boundary year={counts['alb2002_climate_centroid_boundary_year']}; climate-ready rows={counts['alb2002_climate_centroid_climate_linkage_ready_rows']}; data-write-ready rows={counts['alb2002_climate_centroid_data_write_ready_rows']}; decision={counts['alb2002_climate_centroid_current_decision']}",
        [TEMP_DIR / "alb2002_climate_centroid_exposure_input.csv", TEMP_DIR / "alb2002_climate_centroid_exposure_candidates.csv", TEMP_DIR / "alb2002_climate_centroid_nasa_power_api_manifest.csv", RESULT_DIR / "alb2002_climate_centroid_exposure_audit.csv", RESULT_DIR / "alb2002_climate_centroid_exposure_summary.csv", REPORT_DIR / "alb2002_climate_centroid_exposure_audit.md"],
        "" if counts["alb2002_climate_centroid_exposure_candidates"] == 384 and counts["alb2002_climate_centroid_nasa_failed_rows"] == 0 and counts["alb2002_climate_centroid_climate_linkage_ready_rows"] == 0 and counts["alb2002_climate_centroid_current_decision"] == "blocked_alb2002_climate_centroid_exposures_not_promoted_due_boundary_vintage_source_and_baseline_gates" else "run script/103_build_alb2002_climate_centroid_exposure_candidates.py and keep outputs temp-only until historical geography, primary sources, and baselines pass",
    )
    add(
        "cross_phase_alb2002_climate_shock_candidate_diagnostics",
        "phase5",
        "Derive temp-only within-candidate ALB_2002 rainfall and temperature shock diagnostics without treating them as historical anomalies or accepted treatment variables.",
        status_done(
            counts["alb2002_climate_shock_candidate_exposures"] == 384
            and counts["alb2002_climate_shock_candidate_lineage"] == 7
            and counts["alb2002_climate_shock_candidate_audit"] == 8
            and counts["alb2002_climate_shock_candidate_summary"] > 0
            and counts["alb2002_climate_shock_candidate_exposure_rows"] == 384
            and counts["alb2002_climate_shock_candidate_source_centroid_rows"] == 384
            and counts["alb2002_climate_shock_candidate_lineage_rows"] == 7
            and counts["alb2002_climate_shock_candidate_audit_rows"] == 8
            and counts["alb2002_climate_shock_candidate_reference_group_rows"] == 16
            and counts["alb2002_climate_shock_candidate_min_reference_group_size"] == 3
            and counts["alb2002_climate_shock_candidate_precip_z_nonmissing_rows"] == 384
            and counts["alb2002_climate_shock_candidate_temp_z_nonmissing_rows"] == 384
            and counts["alb2002_climate_shock_candidate_low_rain_rows"] == 37
            and counts["alb2002_climate_shock_candidate_extreme_wet_rows"] == 44
            and counts["alb2002_climate_shock_candidate_extreme_heat_rows"] == 29
            and counts["alb2002_climate_shock_candidate_combined_stress_rows"] == 73
            and counts["alb2002_climate_shock_candidate_climate_linkage_ready_rows"] == 0
            and counts["alb2002_climate_shock_candidate_data_write_ready_rows"] == 0
            and counts["alb2002_climate_shock_candidate_current_decision"] == "blocked_alb2002_climate_shock_candidate_not_promoted_due_geography_baseline_primary_source_gates"
        ),
        f"shock rows={counts['alb2002_climate_shock_candidate_exposures']}; lineage rows={counts['alb2002_climate_shock_candidate_lineage']}; audit rows={counts['alb2002_climate_shock_candidate_audit']}; source centroid rows={counts['alb2002_climate_shock_candidate_source_centroid_rows']}; reference groups={counts['alb2002_climate_shock_candidate_reference_group_rows']}; min group size={counts['alb2002_climate_shock_candidate_min_reference_group_size']}; precip z rows={counts['alb2002_climate_shock_candidate_precip_z_nonmissing_rows']}; temp z rows={counts['alb2002_climate_shock_candidate_temp_z_nonmissing_rows']}; low-rain rows={counts['alb2002_climate_shock_candidate_low_rain_rows']}; extreme-wet rows={counts['alb2002_climate_shock_candidate_extreme_wet_rows']}; extreme-heat rows={counts['alb2002_climate_shock_candidate_extreme_heat_rows']}; combined-stress rows={counts['alb2002_climate_shock_candidate_combined_stress_rows']}; climate-ready rows={counts['alb2002_climate_shock_candidate_climate_linkage_ready_rows']}; data-write-ready rows={counts['alb2002_climate_shock_candidate_data_write_ready_rows']}; decision={counts['alb2002_climate_shock_candidate_current_decision']}",
        [TEMP_DIR / "alb2002_climate_shock_candidate_exposures.csv", TEMP_DIR / "alb2002_climate_shock_candidate_lineage.csv", RESULT_DIR / "alb2002_climate_shock_candidate_audit.csv", RESULT_DIR / "alb2002_climate_shock_candidate_summary.csv", REPORT_DIR / "alb2002_climate_shock_candidate_audit.md"],
        "" if counts["alb2002_climate_shock_candidate_exposures"] == 384 and counts["alb2002_climate_shock_candidate_precip_z_nonmissing_rows"] == 384 and counts["alb2002_climate_shock_candidate_climate_linkage_ready_rows"] == 0 and counts["alb2002_climate_shock_candidate_current_decision"] == "blocked_alb2002_climate_shock_candidate_not_promoted_due_geography_baseline_primary_source_gates" else "run script/107_build_alb2002_climate_shock_candidate_audit.py after centroid exposure construction; keep shock diagnostics temp-only until geography, primary source, and historical-baseline gates pass",
    )
    add(
        "cross_phase_alb2002_climate_outcome_linked_candidate",
        "phase5_phase6",
        "Mechanically join ALB_2002 temp household/outcome candidates to diagnostic climate-window rows while keeping the climate-linked analytical dataset blocked from promotion.",
        status_done(
            counts["alb2002_climate_outcome_linked_candidate"] == 14396
            and counts["alb2002_climate_outcome_linked_candidate_lineage"] == 7
            and counts["alb2002_climate_outcome_linked_candidate_audit"] == 7
            and counts["alb2002_climate_outcome_linked_candidate_summary"] > 0
            and counts["alb2002_climate_outcome_linked_candidate_rows"] == 14396
            and counts["alb2002_climate_outcome_linked_candidate_household_rows"] == 3599
            and counts["alb2002_climate_outcome_linked_candidate_window_rows"] == 4
            and counts["alb2002_climate_outcome_linked_candidate_district_month_cells"] == 96
            and counts["alb2002_climate_outcome_linked_candidate_lineage_rows"] == 7
            and counts["alb2002_climate_outcome_linked_candidate_audit_rows"] == 7
            and counts["alb2002_climate_outcome_linked_candidate_source_analysis_rows"] == 3599
            and counts["alb2002_climate_outcome_linked_candidate_source_uhc_rows"] == 3599
            and counts["alb2002_climate_outcome_linked_candidate_source_shock_rows"] == 384
            and counts["alb2002_climate_outcome_linked_candidate_expected_rows"] == 14396
            and counts["alb2002_climate_outcome_linked_candidate_unmatched_rows"] == 0
            and counts["alb2002_climate_outcome_linked_candidate_precip_z_rows"] == 14396
            and counts["alb2002_climate_outcome_linked_candidate_temp_z_rows"] == 14396
            and counts["alb2002_climate_outcome_linked_candidate_che10_or_access_rows"] == 8016
            and counts["alb2002_climate_outcome_linked_candidate_che25_or_access_rows"] == 7556
            and counts["alb2002_climate_outcome_linked_candidate_both_che10_access_rows"] == 2724
            and counts["alb2002_climate_outcome_linked_candidate_coping_rows"] == 5904
            and counts["alb2002_climate_outcome_linked_candidate_climate_linkage_ready_rows"] == 0
            and counts["alb2002_climate_outcome_linked_candidate_outcome_promotion_ready_rows"] == 0
            and counts["alb2002_climate_outcome_linked_candidate_harmonized_recipe_ready_rows"] == 0
            and counts["alb2002_climate_outcome_linked_candidate_data_write_ready_rows"] == 0
            and counts["alb2002_climate_outcome_linked_candidate_current_decision"] == "blocked_alb2002_climate_outcome_linked_candidate_not_promoted_due_recipe_outcome_geography_source_baseline_gates"
        ),
        f"linked rows={counts['alb2002_climate_outcome_linked_candidate']}; lineage rows={counts['alb2002_climate_outcome_linked_candidate_lineage']}; audit rows={counts['alb2002_climate_outcome_linked_candidate_audit']}; households={counts['alb2002_climate_outcome_linked_candidate_household_rows']}; windows={counts['alb2002_climate_outcome_linked_candidate_window_rows']}; district-month cells={counts['alb2002_climate_outcome_linked_candidate_district_month_cells']}; expected rows={counts['alb2002_climate_outcome_linked_candidate_expected_rows']}; unmatched rows={counts['alb2002_climate_outcome_linked_candidate_unmatched_rows']}; precip z rows={counts['alb2002_climate_outcome_linked_candidate_precip_z_rows']}; temp z rows={counts['alb2002_climate_outcome_linked_candidate_temp_z_rows']}; combined stress rows={counts['alb2002_climate_outcome_linked_candidate_combined_stress_rows']}; CHE10-or-access rows={counts['alb2002_climate_outcome_linked_candidate_che10_or_access_rows']}; CHE25-or-access rows={counts['alb2002_climate_outcome_linked_candidate_che25_or_access_rows']}; climate-ready rows={counts['alb2002_climate_outcome_linked_candidate_climate_linkage_ready_rows']}; outcome-ready rows={counts['alb2002_climate_outcome_linked_candidate_outcome_promotion_ready_rows']}; data-write-ready rows={counts['alb2002_climate_outcome_linked_candidate_data_write_ready_rows']}; decision={counts['alb2002_climate_outcome_linked_candidate_current_decision']}",
        [TEMP_DIR / "alb2002_climate_outcome_linked_candidate.csv", TEMP_DIR / "alb2002_climate_outcome_linked_candidate_lineage.csv", RESULT_DIR / "alb2002_climate_outcome_linked_candidate_audit.csv", RESULT_DIR / "alb2002_climate_outcome_linked_candidate_summary.csv", REPORT_DIR / "alb2002_climate_outcome_linked_candidate_audit.md"],
        "" if counts["alb2002_climate_outcome_linked_candidate"] == 14396 and counts["alb2002_climate_outcome_linked_candidate_unmatched_rows"] == 0 and counts["alb2002_climate_outcome_linked_candidate_climate_linkage_ready_rows"] == 0 and counts["alb2002_climate_outcome_linked_candidate_current_decision"] == "blocked_alb2002_climate_outcome_linked_candidate_not_promoted_due_recipe_outcome_geography_source_baseline_gates" else "run script/108_build_alb2002_climate_outcome_linked_candidate_audit.py after the shock diagnostics; keep linked candidate temp-only until recipe, outcome, geography, primary source, and historical-baseline gates pass",
    )
    add(
        "cross_phase_alb2002_linked_candidate_descriptive_screen",
        "phase5_phase6",
        "Summarize the ALB_2002 temp-only linked candidate in a descriptive audit screen without satisfying promoted descriptive diagnostics.",
        status_done(
            counts["alb2002_linked_candidate_descriptive_audit"] == 7
            and counts["alb2002_linked_candidate_descriptive_cells"] == 108
            and counts["alb2002_linked_candidate_descriptive_summary"] > 0
            and counts["alb2002_linked_candidate_descriptive_input_rows"] == 14396
            and counts["alb2002_linked_candidate_descriptive_household_rows"] == 3599
            and counts["alb2002_linked_candidate_descriptive_window_rows"] == 4
            and counts["alb2002_linked_candidate_descriptive_audit_rows"] == 7
            and counts["alb2002_linked_candidate_descriptive_cell_rows"] == 108
            and counts["alb2002_linked_candidate_descriptive_household_outcome_cell_rows"] == 4
            and counts["alb2002_linked_candidate_descriptive_subgroup_outcome_cell_rows"] == 24
            and counts["alb2002_linked_candidate_descriptive_climate_flag_cell_rows"] == 16
            and counts["alb2002_linked_candidate_descriptive_outcome_by_climate_flag_cell_rows"] == 64
            and counts["alb2002_linked_candidate_descriptive_che10_or_access_households"] == 2004
            and counts["alb2002_linked_candidate_descriptive_che25_or_access_households"] == 1889
            and counts["alb2002_linked_candidate_descriptive_both_che10_access_households"] == 681
            and counts["alb2002_linked_candidate_descriptive_coping_households"] == 1476
            and counts["alb2002_linked_candidate_descriptive_combined_stress_rows"] == 3092
            and counts["alb2002_linked_candidate_descriptive_climate_linkage_ready_rows"] == 0
            and counts["alb2002_linked_candidate_descriptive_outcome_promotion_ready_rows"] == 0
            and counts["alb2002_linked_candidate_descriptive_harmonized_recipe_ready_rows"] == 0
            and counts["alb2002_linked_candidate_descriptive_data_write_ready_rows"] == 0
            and counts["alb2002_linked_candidate_descriptive_current_decision"] == "blocked_alb2002_linked_candidate_descriptive_screen_not_promoted_due_unpromoted_inputs"
        ),
        f"input rows={counts['alb2002_linked_candidate_descriptive_input_rows']}; household rows={counts['alb2002_linked_candidate_descriptive_household_rows']}; window rows={counts['alb2002_linked_candidate_descriptive_window_rows']}; audit rows={counts['alb2002_linked_candidate_descriptive_audit']}; cell rows={counts['alb2002_linked_candidate_descriptive_cells']}; household cells={counts['alb2002_linked_candidate_descriptive_household_outcome_cell_rows']}; subgroup cells={counts['alb2002_linked_candidate_descriptive_subgroup_outcome_cell_rows']}; climate flag cells={counts['alb2002_linked_candidate_descriptive_climate_flag_cell_rows']}; outcome-by-climate cells={counts['alb2002_linked_candidate_descriptive_outcome_by_climate_flag_cell_rows']}; CHE10-or-access households={counts['alb2002_linked_candidate_descriptive_che10_or_access_households']}; CHE25-or-access households={counts['alb2002_linked_candidate_descriptive_che25_or_access_households']}; combined stress rows={counts['alb2002_linked_candidate_descriptive_combined_stress_rows']}; climate-ready rows={counts['alb2002_linked_candidate_descriptive_climate_linkage_ready_rows']}; outcome-ready rows={counts['alb2002_linked_candidate_descriptive_outcome_promotion_ready_rows']}; data-write-ready rows={counts['alb2002_linked_candidate_descriptive_data_write_ready_rows']}; decision={counts['alb2002_linked_candidate_descriptive_current_decision']}",
        [RESULT_DIR / "alb2002_linked_candidate_descriptive_audit.csv", RESULT_DIR / "alb2002_linked_candidate_descriptive_cells.csv", RESULT_DIR / "alb2002_linked_candidate_descriptive_summary.csv", REPORT_DIR / "alb2002_linked_candidate_descriptive_diagnostics.md"],
        "" if counts["alb2002_linked_candidate_descriptive_cells"] == 108 and counts["alb2002_linked_candidate_descriptive_data_write_ready_rows"] == 0 and counts["alb2002_linked_candidate_descriptive_current_decision"] == "blocked_alb2002_linked_candidate_descriptive_screen_not_promoted_due_unpromoted_inputs" else "run script/109_build_alb2002_linked_candidate_descriptive_diagnostics.py after the linked-candidate audit; do not use it as promoted descriptive diagnostics",
    )
    add(
        "cross_phase_alb2002_weight_design_evidence_audit",
        "phase3_phase4",
        "Verify ALB_2002 household weight and survey-design evidence before any harmonized data promotion or weighted inference.",
        status_done(
            counts["alb2002_weight_design_evidence_audit"] == 6
            and counts["alb2002_weight_design_evidence_summary"] > 0
            and counts["alb2002_weight_design_source_page_flag_rows"] == 9
            and counts["alb2002_weight_design_raw_weight_file_rows"] == 3599
            and counts["alb2002_weight_design_positive_weight_rows"] == 3599
            and counts["alb2002_weight_design_candidate_key_match_rows"] == 3599
            and counts["alb2002_weight_design_distinct_psu_rows"] == 450
            and counts["alb2002_weight_design_distinct_stratum_rows"] == 4
            and counts["alb2002_weight_design_weighted_inference_ready_rows"] == 0
            and counts["alb2002_weight_design_harmonized_promotion_ready_rows"] == 0
            and counts["alb2002_weight_design_current_decision"] == "blocked_alb2002_weight_design_semantics_not_promotion_ready"
        ),
        f"audit rows={counts['alb2002_weight_design_evidence_audit']}; summary rows={counts['alb2002_weight_design_evidence_summary']}; source flags={counts['alb2002_weight_design_source_page_flag_rows']}; raw weight rows={counts['alb2002_weight_design_raw_weight_file_rows']}; positive weights={counts['alb2002_weight_design_positive_weight_rows']}; key matches={counts['alb2002_weight_design_candidate_key_match_rows']}; distinct PSU={counts['alb2002_weight_design_distinct_psu_rows']}; distinct strata={counts['alb2002_weight_design_distinct_stratum_rows']}; weighted-inference ready rows={counts['alb2002_weight_design_weighted_inference_ready_rows']}; harmonized-ready rows={counts['alb2002_weight_design_harmonized_promotion_ready_rows']}; decision={counts['alb2002_weight_design_current_decision']}",
        [TEMP_DIR / "alb2002_weight_design_evidence_audit.csv", RESULT_DIR / "alb2002_weight_design_evidence_summary.csv", REPORT_DIR / "alb2002_weight_design_evidence_audit.md", TEMP_DIR / "source_snapshots" / "alb2002_worldbank_study_description_weight_design.html"],
        "" if counts["alb2002_weight_design_positive_weight_rows"] == 3599 and counts["alb2002_weight_design_candidate_key_match_rows"] == 3599 and counts["alb2002_weight_design_weighted_inference_ready_rows"] == 0 and counts["alb2002_weight_design_current_decision"] == "blocked_alb2002_weight_design_semantics_not_promotion_ready" else "run script/100_audit_alb2002_weight_design_evidence.py and keep weighted inference blocked until design semantics, weighting use, and promotion gates are verified",
    )
    add(
        "cross_phase_alb2002_sample_design_documentation_audit",
        "phase3_phase4",
        "Snapshot the official ALB_2002 Basic Information document and verify sample-design count concordance before weighted descriptive or harmonized-data promotion.",
        status_done(
            counts["alb2002_sample_design_documentation_audit"] == 7
            and counts["alb2002_sample_design_documentation_summary"] > 0
            and counts["alb2002_sample_design_pdf_available_rows"] == 1
            and counts["alb2002_sample_design_pdf_pages"] > 0
            and counts["alb2002_sample_design_official_450_psu_8_hh_rows"] == 1
            and counts["alb2002_sample_design_official_3599_final_rows"] == 1
            and counts["alb2002_sample_design_raw_weight_rows"] == 3599
            and counts["alb2002_sample_design_positive_weight_rows"] == 3599
            and counts["alb2002_sample_design_distinct_psu_rows"] == 450
            and counts["alb2002_sample_design_raw_design_concordance_rows"] == 1
            and counts["alb2002_sample_design_documentation_ready_rows"] == 1
            and counts["alb2002_sample_design_weighted_inference_ready_rows"] == 0
            and counts["alb2002_sample_design_harmonized_promotion_ready_rows"] == 0
            and counts["alb2002_sample_design_current_decision"] == "candidate_alb2002_sample_design_documented_not_promoted_due_downstream_gates"
        ),
        f"audit rows={counts['alb2002_sample_design_documentation_audit']}; summary rows={counts['alb2002_sample_design_documentation_summary']}; pdf available={counts['alb2002_sample_design_pdf_available_rows']}; pages={counts['alb2002_sample_design_pdf_pages']}; official 450x8 rows={counts['alb2002_sample_design_official_450_psu_8_hh_rows']}; official 3599 rows={counts['alb2002_sample_design_official_3599_final_rows']}; raw weight rows={counts['alb2002_sample_design_raw_weight_rows']}; positive weights={counts['alb2002_sample_design_positive_weight_rows']}; distinct PSU={counts['alb2002_sample_design_distinct_psu_rows']}; concordance rows={counts['alb2002_sample_design_raw_design_concordance_rows']}; documentation-ready rows={counts['alb2002_sample_design_documentation_ready_rows']}; weighted-inference-ready rows={counts['alb2002_sample_design_weighted_inference_ready_rows']}; decision={counts['alb2002_sample_design_current_decision']}",
        [TEMP_DIR / "alb2002_sample_design_documentation_audit.csv", RESULT_DIR / "alb2002_sample_design_documentation_summary.csv", REPORT_DIR / "alb2002_sample_design_documentation_audit.md", TEMP_DIR / "source_snapshots" / "alb2002_basic_information_document_sample_design.pdf", TEMP_DIR / "source_snapshots" / "alb2002_basic_information_document_sample_design.txt"],
        "" if counts["alb2002_sample_design_documentation_ready_rows"] == 1 and counts["alb2002_sample_design_weighted_inference_ready_rows"] == 0 else "run script/104_audit_alb2002_sample_design_documentation.py and keep weighted inference blocked until weight-use, variance, outcome, and climate gates pass",
    )
    add(
        "cross_phase_alb2002_minimum_recipe_promotion_packet",
        "phase4",
        "Map the top-ranked ALB_2002 temp candidate to explicit harmonization, outcome, SDG 3.8.2, and climate-linkage promotion gates before any data promotion.",
        status_done(
            counts["alb2002_minimum_recipe_promotion_action_rows"] > 0
            and counts["alb2002_minimum_recipe_promotion_gate_rows"] > 0
            and counts["alb2002_minimum_recipe_promotion_summary_rows"] > 0
            and counts["alb2002_minimum_recipe_promotion_blocked_gates"] > 0
            and counts["alb2002_minimum_recipe_promotion_candidate_gates"] > 0
            and counts["alb2002_minimum_recipe_promotion_weight_positive_rows"] == 3599
            and counts["alb2002_minimum_recipe_promotion_weight_key_match_rows"] == 3599
            and counts["alb2002_minimum_recipe_promotion_weighted_inference_ready_rows"] == 0
            and counts["alb2002_minimum_recipe_promotion_harmonized_ready_rows"] == 0
            and counts["alb2002_minimum_recipe_promotion_outcome_ready_rows"] == 0
            and counts["alb2002_minimum_recipe_promotion_sdg382_ready_rows"] == 0
            and counts["alb2002_minimum_recipe_promotion_climate_linkage_ready_rows"] == 0
        ),
        f"action rows={counts['alb2002_minimum_recipe_promotion_action_rows']}; gate rows={counts['alb2002_minimum_recipe_promotion_gate_rows']}; blocked gates={counts['alb2002_minimum_recipe_promotion_blocked_gates']}; candidate gates={counts['alb2002_minimum_recipe_promotion_candidate_gates']}; weight-positive rows={counts['alb2002_minimum_recipe_promotion_weight_positive_rows']}; weight-key-match rows={counts['alb2002_minimum_recipe_promotion_weight_key_match_rows']}; weighted-inference-ready rows={counts['alb2002_minimum_recipe_promotion_weighted_inference_ready_rows']}; harmonized-ready rows={counts['alb2002_minimum_recipe_promotion_harmonized_ready_rows']}; outcome-ready rows={counts['alb2002_minimum_recipe_promotion_outcome_ready_rows']}; SDG382-ready rows={counts['alb2002_minimum_recipe_promotion_sdg382_ready_rows']}; climate-linkage-ready rows={counts['alb2002_minimum_recipe_promotion_climate_linkage_ready_rows']}; decision={counts['alb2002_minimum_recipe_promotion_current_decision']}",
        [TEMP_DIR / "alb2002_minimum_recipe_promotion_action_queue.csv", TEMP_DIR / "alb2002_minimum_recipe_promotion_gate_checklist.csv", RESULT_DIR / "alb2002_minimum_recipe_promotion_summary.csv", REPORT_DIR / "alb2002_minimum_recipe_promotion_packet.md"],
        "" if counts["alb2002_minimum_recipe_promotion_action_rows"] > 0 and counts["alb2002_minimum_recipe_promotion_weight_positive_rows"] == 3599 and counts["alb2002_minimum_recipe_promotion_weighted_inference_ready_rows"] == 0 and counts["alb2002_minimum_recipe_promotion_harmonized_ready_rows"] == 0 and counts["alb2002_minimum_recipe_promotion_outcome_ready_rows"] == 0 and counts["alb2002_minimum_recipe_promotion_climate_linkage_ready_rows"] == 0 else "run script/90_build_alb2002_minimum_recipe_promotion_packet.py and keep ALB_2002 temp-only until minimum recipe, SDG, weight/design, and climate gates pass",
    )
    add(
        "cross_phase_alb2002_district_climate_crosswalk_audit",
        "phase5",
        "Build a temp-only ALB_2002 district climate-crosswalk template and public boundary metadata probe before any climate-linkage promotion.",
        status_done(
            counts["alb2002_district_climate_crosswalk_template"] > 0
            and counts["alb2002_district_boundary_source_probe"] > 0
            and counts["alb2002_district_climate_crosswalk_summary"] > 0
            and counts["alb2002_climate_linkage_ready_rows"] == 0
        ),
        f"template rows={counts['alb2002_district_climate_crosswalk_template']}; source rows={counts['alb2002_district_boundary_source_probe']}; summary rows={counts['alb2002_district_climate_crosswalk_summary']}; district rows={counts['alb2002_district_crosswalk_district_rows']}; source reachable rows={counts['alb2002_district_crosswalk_source_reachable_rows']}; climate-linkage ready rows={counts['alb2002_climate_linkage_ready_rows']}",
        [TEMP_DIR / "alb2002_district_climate_crosswalk_template.csv", TEMP_DIR / "alb2002_district_boundary_source_probe.csv", RESULT_DIR / "alb2002_district_climate_crosswalk_summary.csv", REPORT_DIR / "alb2002_district_climate_crosswalk_audit.md"],
        "" if counts["alb2002_district_climate_crosswalk_template"] > 0 and counts["alb2002_climate_linkage_ready_rows"] == 0 else "run script/56_audit_alb2002_district_climate_crosswalk.py and keep climate linkage blocked until boundary/crosswalk validation passes",
    )
    add(
        "cross_phase_alb2002_boundary_name_match_audit",
        "phase5",
        "Download and compare public current ADM2 boundary names against ALB_2002 survey district labels before any admin-level climate-linkage promotion.",
        status_done(
            counts["alb2002_boundary_name_match_audit"] > 0
            and counts["alb2002_boundary_geojson_inventory"] > 0
            and counts["alb2002_boundary_name_match_summary"] > 0
            and counts["alb2002_boundary_name_match_historical_year_ready_rows"] == 0
            and counts["alb2002_boundary_name_match_climate_linkage_ready_rows"] == 0
        ),
        f"match rows={counts['alb2002_boundary_name_match_audit']}; boundary features={counts['alb2002_boundary_geojson_inventory']}; summary rows={counts['alb2002_boundary_name_match_summary']}; exact matches={counts['alb2002_boundary_name_match_exact_rows']}; repaired matches={counts['alb2002_boundary_name_match_euro_repaired_rows']}; unmatched survey rows={counts['alb2002_boundary_name_match_unmatched_survey_rows']}; duplicate boundary-name keys={counts['alb2002_boundary_name_match_duplicate_boundary_name_keys']}; historical-ready rows={counts['alb2002_boundary_name_match_historical_year_ready_rows']}; climate-linkage ready rows={counts['alb2002_boundary_name_match_climate_linkage_ready_rows']}",
        [TEMP_DIR / "alb2002_boundary_name_match_audit.csv", TEMP_DIR / "alb2002_boundary_geojson_inventory.csv", RESULT_DIR / "alb2002_boundary_name_match_summary.csv", REPORT_DIR / "alb2002_boundary_name_match_audit.md"],
        "" if counts["alb2002_boundary_name_match_audit"] > 0 and counts["alb2002_boundary_name_match_historical_year_ready_rows"] == 0 and counts["alb2002_boundary_name_match_climate_linkage_ready_rows"] == 0 else "run script/64_audit_alb2002_boundary_name_match.py and keep ALB_2002 climate linkage blocked until boundary names, historical crosswalk, and no-GPS admin aggregation pass",
    )
    add(
        "cross_phase_alb2002_boundary_source_alternatives_audit",
        "phase5",
        "Audit public/current/historical boundary-source alternatives for ALB_2002 before any admin-level climate-linkage promotion.",
        status_done(
            counts["alb2002_boundary_source_alternative_audit"] > 0
            and counts["alb2002_boundary_source_alternative_summary"] > 0
            and counts["alb2002_boundary_source_alternative_historical_2002_boundary_ready_rows"] == 0
            and counts["alb2002_boundary_source_alternative_climate_linkage_ready_rows"] == 0
        ),
        f"source alternatives={counts['alb2002_boundary_source_alternative_rows']}; reachable/local rows={counts['alb2002_boundary_source_alternative_reachable_rows']}; historical-ready rows={counts['alb2002_boundary_source_alternative_historical_2002_boundary_ready_rows']}; climate-linkage-ready rows={counts['alb2002_boundary_source_alternative_climate_linkage_ready_rows']}",
        [TEMP_DIR / "alb2002_boundary_source_alternative_audit.csv", RESULT_DIR / "alb2002_boundary_source_alternative_summary.csv", REPORT_DIR / "alb2002_boundary_source_alternative_audit.md"],
        "" if counts["alb2002_boundary_source_alternative_audit"] > 0 and counts["alb2002_boundary_source_alternative_climate_linkage_ready_rows"] == 0 else "run script/69_audit_alb2002_boundary_source_alternatives.py and keep ALB_2002 climate linkage blocked until a public 2001/2002 district/GPS boundary source is verified",
    )
    add(
        "cross_phase_alb2002_boundary_resource_search_audit",
        "phase5",
        "Parse public boundary/gazetteer resources for ALB_2002 name coverage while keeping historical-boundary and climate-linkage promotion blocked.",
        status_done(
            counts["alb2002_boundary_resource_search_audit"] > 0
            and counts["alb2002_boundary_resource_search_summary"] > 0
            and counts["alb2002_boundary_resource_search_2002_historical_ready_rows"] == 0
            and counts["alb2002_boundary_resource_search_climate_linkage_ready_rows"] == 0
        ),
        f"candidate resources={counts['alb2002_boundary_resource_search_candidate_rows']}; complete-name-coverage resources={counts['alb2002_boundary_resource_search_complete_name_coverage_rows']}; exact-unit-count resources={counts['alb2002_boundary_resource_search_exact_unit_count_rows']}; best-candidate exact/repaired/alias matches={counts['alb2002_boundary_resource_search_best_candidate_exact_matches']}/{counts['alb2002_boundary_resource_search_best_candidate_repaired_matches']}/{counts['alb2002_boundary_resource_search_best_candidate_alias_matches']}; historical-ready rows={counts['alb2002_boundary_resource_search_2002_historical_ready_rows']}; climate-linkage-ready rows={counts['alb2002_boundary_resource_search_climate_linkage_ready_rows']}",
        [TEMP_DIR / "alb2002_boundary_source_resource_search_audit.csv", RESULT_DIR / "alb2002_boundary_source_resource_search_summary.csv", REPORT_DIR / "alb2002_boundary_source_resource_search_audit.md"],
        "" if counts["alb2002_boundary_resource_search_audit"] > 0 and counts["alb2002_boundary_resource_search_climate_linkage_ready_rows"] == 0 else "run script/79_audit_alb2002_boundary_source_resource_search.py and keep ALB_2002 climate linkage blocked until provenance, vintage, geometry, and raw-code crosswalk checks pass",
    )
    add(
        "cross_phase_alb2002_boundary_geometry_provenance_audit",
        "phase5",
        "Parse the strongest ALB_2002 boundary lead for geometry structure and companion metadata provenance before any climate-linkage promotion.",
        status_done(
            counts["alb2002_boundary_geometry_provenance_audit"] > 0
            and counts["alb2002_boundary_metadata_provenance_probe"] > 0
            and counts["alb2002_boundary_geometry_provenance_summary"] > 0
            and counts["alb2002_boundary_geometry_boundary_year_matches_2002_rows"] == 0
            and counts["alb2002_boundary_geometry_historical_2002_boundary_ready_rows"] == 0
            and counts["alb2002_boundary_geometry_climate_linkage_ready_rows"] == 0
        ),
        f"geometry rows={counts['alb2002_boundary_geometry_provenance_audit']}; metadata rows={counts['alb2002_boundary_metadata_provenance_probe']}; feature rows={counts['alb2002_boundary_geometry_feature_rows']}; coordinate-structure-ok rows={counts['alb2002_boundary_geometry_coordinate_structure_ok_rows']}; survey-key matched rows={counts['alb2002_boundary_geometry_survey_key_matched_rows']}; metadata boundary year={counts['alb2002_boundary_geometry_metadata_boundary_year']}; year-matches-2002 rows={counts['alb2002_boundary_geometry_boundary_year_matches_2002_rows']}; topology-validated rows={counts['alb2002_boundary_geometry_topology_validated_rows']}; historical-ready rows={counts['alb2002_boundary_geometry_historical_2002_boundary_ready_rows']}; climate-linkage-ready rows={counts['alb2002_boundary_geometry_climate_linkage_ready_rows']}",
        [TEMP_DIR / "alb2002_boundary_geometry_provenance_audit.csv", TEMP_DIR / "alb2002_boundary_metadata_provenance_probe.csv", RESULT_DIR / "alb2002_boundary_geometry_provenance_summary.csv", REPORT_DIR / "alb2002_boundary_geometry_provenance_audit.md"],
        "" if counts["alb2002_boundary_geometry_provenance_audit"] > 0 and counts["alb2002_boundary_geometry_climate_linkage_ready_rows"] == 0 else "run script/80_audit_alb2002_boundary_geometry_provenance.py and keep ALB_2002 climate linkage blocked until metadata vintage, topology, official 2002 boundary definitions, and raw-code crosswalks are verified",
    )
    add(
        "cross_phase_alb2002_boundary_manual_verification_packet",
        "phase5",
        "Create an ALB_2002 manual boundary verification packet that maps unresolved geography blockers to source-specific actions and pass/fail promotion gates.",
        status_done(
            counts["alb2002_boundary_manual_verification_action_rows"] > 0
            and counts["alb2002_boundary_manual_verification_gate_rows"] > 0
            and counts["alb2002_boundary_manual_verification_summary_rows"] > 0
            and counts["alb2002_boundary_manual_verification_pre2011_digital_map_absence_rows"] == 1
            and counts["alb2002_boundary_manual_verification_climate_linkage_ready_rows"] == 0
        ),
        f"action rows={counts['alb2002_boundary_manual_verification_action_rows']}; gate rows={counts['alb2002_boundary_manual_verification_gate_rows']}; candidate-evidence gates={counts['alb2002_boundary_manual_verification_candidate_evidence_gates']}; blocked gates={counts['alb2002_boundary_manual_verification_blocked_gates']}; high-priority actions={counts['alb2002_boundary_manual_verification_high_priority_actions']}; pre-2011 digital-map absence rows={counts['alb2002_boundary_manual_verification_pre2011_digital_map_absence_rows']}; climate-linkage-ready rows={counts['alb2002_boundary_manual_verification_climate_linkage_ready_rows']}",
        [TEMP_DIR / "alb2002_boundary_manual_verification_action_queue.csv", TEMP_DIR / "alb2002_boundary_promotion_gate_checklist.csv", RESULT_DIR / "alb2002_boundary_manual_verification_packet_summary.csv", REPORT_DIR / "alb2002_boundary_manual_verification_packet.md"],
        "" if counts["alb2002_boundary_manual_verification_action_rows"] > 0 and counts["alb2002_boundary_manual_verification_pre2011_digital_map_absence_rows"] == 1 and counts["alb2002_boundary_manual_verification_climate_linkage_ready_rows"] == 0 else "run script/81_build_alb2002_boundary_manual_verification_packet.py and keep ALB_2002 climate linkage blocked until the manual verification gates pass",
    )
    add(
        "cross_phase_alb2002_boundary_manual_source_followup",
        "phase5",
        "Follow up the ALB_2002 manual boundary source queue and record whether high-priority public/official leads provide 36-district-compatible 2001/2002 boundary evidence.",
        status_done(
            counts["alb2002_boundary_manual_source_followup_audit"] > 0
            and counts["alb2002_boundary_manual_source_followup_summary_rows"] > 0
            and counts["alb2002_boundary_manual_source_followup_rows"] == 7
            and counts["alb2002_boundary_manual_source_followup_conclusive_blocker_rows"] == 7
            and counts["alb2002_boundary_manual_source_followup_district_level_ready_rows"] == 0
            and counts["alb2002_boundary_manual_source_followup_climate_linkage_ready_rows"] == 0
            and counts["alb2002_boundary_manual_source_followup_unece_pre2011_map_status"] == "blocked_pre2011_digital_boundary_source_absence_documented"
        ),
        f"follow-up rows={counts['alb2002_boundary_manual_source_followup_rows']}; conclusive blocker rows={counts['alb2002_boundary_manual_source_followup_conclusive_blocker_rows']}; district-level-ready rows={counts['alb2002_boundary_manual_source_followup_district_level_ready_rows']}; climate-linkage-ready rows={counts['alb2002_boundary_manual_source_followup_climate_linkage_ready_rows']}; UNECE pre-2011 map status={counts['alb2002_boundary_manual_source_followup_unece_pre2011_map_status']}",
        [TEMP_DIR / "alb2002_boundary_manual_source_followup_audit.csv", RESULT_DIR / "alb2002_boundary_manual_source_followup_summary.csv", REPORT_DIR / "alb2002_boundary_manual_source_followup.md"],
        "" if counts["alb2002_boundary_manual_source_followup_audit"] > 0 and counts["alb2002_boundary_manual_source_followup_climate_linkage_ready_rows"] == 0 and counts["alb2002_boundary_manual_source_followup_unece_pre2011_map_status"] == "blocked_pre2011_digital_boundary_source_absence_documented" else "run script/82_audit_alb2002_boundary_manual_source_followup.py and keep ALB_2002 climate linkage blocked until a district-compatible 2001/2002 source is verified",
    )
    add(
        "cross_phase_alb2002_gadm_boundary_lead_audit",
        "phase5",
        "Audit public GADM Albania ADM2 shapefiles as a potential ALB_2002 district-boundary lead without promoting them until historical 2001/2002 provenance and duplicate-key issues are resolved.",
        status_done(
            counts["alb2002_gadm_boundary_lead_audit"] == 2
            and counts["alb2002_gadm_boundary_name_match_audit"] > 0
            and counts["alb2002_gadm_boundary_lead_summary_rows"] > 0
            and counts["alb2002_gadm_boundary_lead_candidate_rows"] == 2
            and counts["alb2002_gadm36_adm2_row_count"] == 37
            and counts["alb2002_gadm36_distinct_normalized_key_count"] == 36
            and counts["alb2002_gadm36_complete_name_coverage_rows"] == 1
            and counts["alb2002_gadm36_duplicate_boundary_key_count"] > 0
            and counts["alb2002_gadm_boundary_lead_historical_2002_ready_rows"] == 0
            and counts["alb2002_gadm_boundary_lead_climate_linkage_ready_rows"] == 0
        ),
        f"candidates={counts['alb2002_gadm_boundary_lead_candidate_rows']}; GADM 3.6 rows={counts['alb2002_gadm36_adm2_row_count']}; normalized keys={counts['alb2002_gadm36_distinct_normalized_key_count']}; complete name coverage={counts['alb2002_gadm36_complete_name_coverage_rows']}; duplicate keys={counts['alb2002_gadm36_duplicate_boundary_key_count']}; historical-ready rows={counts['alb2002_gadm_boundary_lead_historical_2002_ready_rows']}; climate-linkage-ready rows={counts['alb2002_gadm_boundary_lead_climate_linkage_ready_rows']}; decision={counts['alb2002_gadm_boundary_lead_current_decision']}",
        [
            TEMP_DIR / "alb2002_gadm_boundary_lead_audit.csv",
            TEMP_DIR / "alb2002_gadm_boundary_name_match_audit.csv",
            RESULT_DIR / "alb2002_gadm_boundary_lead_summary.csv",
            REPORT_DIR / "alb2002_gadm_boundary_lead_audit.md",
            TEMP_DIR / "source_snapshots" / "gadm36_ALB_shp.zip",
            TEMP_DIR / "source_snapshots" / "gadm41_ALB_shp.zip",
        ],
        "" if counts["alb2002_gadm_boundary_lead_candidate_rows"] == 2 and counts["alb2002_gadm_boundary_lead_climate_linkage_ready_rows"] == 0 else "run script/88_audit_alb2002_gadm_boundary_lead.py and keep ALB_2002 climate linkage blocked unless historical provenance and duplicate-key gates pass",
    )
    add(
        "cross_phase_alb2002_local_geography_artifact_audit",
        "phase5",
        "Scan ALB_2002 local raw package, raw schema, and questionnaire workbook for GPS, coordinate, EA, admin, and GIS artifacts before any climate-linkage promotion.",
        status_done(
            counts["alb2002_local_geo_artifact_audit"] > 0
            and counts["alb2002_local_geo_artifact_summary"] > 0
            and counts["alb2002_local_geo_artifact_coordinate_raw_variable_rows"] == 0
            and counts["alb2002_local_geo_artifact_local_coordinate_ready_rows"] == 0
            and counts["alb2002_local_geo_artifact_local_boundary_ready_rows"] == 0
            and counts["alb2002_local_geo_artifact_climate_linkage_ready_rows"] == 0
        ),
        f"files scanned={counts['alb2002_local_geo_artifact_files_scanned']}; raw coordinate variables={counts['alb2002_local_geo_artifact_coordinate_raw_variable_rows']}; questionnaire coordinate fields={counts['alb2002_local_geo_artifact_questionnaire_coordinate_field_rows']}; admin/sampling geography variables={counts['alb2002_local_geo_artifact_admin_variable_rows']}; local-coordinate-ready rows={counts['alb2002_local_geo_artifact_local_coordinate_ready_rows']}; local-boundary-ready rows={counts['alb2002_local_geo_artifact_local_boundary_ready_rows']}; climate-linkage-ready rows={counts['alb2002_local_geo_artifact_climate_linkage_ready_rows']}",
        [TEMP_DIR / "alb2002_local_geography_artifact_audit.csv", RESULT_DIR / "alb2002_local_geography_artifact_summary.csv", REPORT_DIR / "alb2002_local_geography_artifact_audit.md"],
        "" if counts["alb2002_local_geo_artifact_audit"] > 0 and counts["alb2002_local_geo_artifact_climate_linkage_ready_rows"] == 0 else "run script/70_audit_alb2002_local_geography_artifacts.py and keep ALB_2002 climate linkage blocked until raw coordinate values or boundary artifacts are verified",
    )
    add(
        "cross_phase_alb2012_raw_core_feasibility",
        "phase3",
        "Read ALB_2012 raw files into a temp-only core feasibility audit before any harmonization or climate-linkage promotion.",
        status_done(
            counts["alb2012_household_core_candidate"] > 0
            and counts["alb2012_raw_core_feasibility_audit"] > 0
            and counts["alb2012_raw_core_lineage"] > 0
            and counts["alb2012_raw_core_feasibility_summary"] > 0
            and counts["alb2012_household_core_recipe_ready_rows"] == 0
            and counts["alb2012_climate_linkage_ready_rows"] == 0
            and counts["alb2012_timing_signal_rows"] == 0
        ),
        f"candidate rows={counts['alb2012_household_core_candidate']}; audit rows={counts['alb2012_raw_core_feasibility_audit']}; lineage rows={counts['alb2012_raw_core_lineage']}; summary rows={counts['alb2012_raw_core_feasibility_summary']}; positive OOP4w rows={counts['alb2012_households_with_oop_4w_positive']}; recipe-ready rows={counts['alb2012_household_core_recipe_ready_rows']}; climate-linkage ready rows={counts['alb2012_climate_linkage_ready_rows']}; timing rows={counts['alb2012_timing_signal_rows']}",
        [TEMP_DIR / "alb2012_household_core_candidate.csv", TEMP_DIR / "alb2012_raw_core_feasibility_audit.csv", TEMP_DIR / "alb2012_raw_core_lineage.csv", RESULT_DIR / "alb2012_raw_core_feasibility_summary.csv", REPORT_DIR / "alb2012_raw_core_feasibility.md"],
        "" if counts["alb2012_household_core_candidate"] > 0 and counts["alb2012_household_core_recipe_ready_rows"] == 0 else "run script/57_audit_alb2012_raw_core_feasibility.py and keep ALB_2012 outputs temp-only",
    )
    add(
        "cross_phase_alb2012_provisional_outcome_feasibility",
        "phase4",
        "Audit ALB_2012 provisional OOP, access, need, and composite outcome signals without promoting final outcomes.",
        status_done(
            counts["alb2012_provisional_outcome_feasibility_audit"] > 0
            and counts["alb2012_provisional_outcome_feasibility_summary"] > 0
            and counts["alb2012_provisional_outcome_ready_rows"] == 0
            and counts["alb2012_provisional_climate_linkage_ready_rows"] == 0
        ),
        f"audit rows={counts['alb2012_provisional_outcome_feasibility_audit']}; summary rows={counts['alb2012_provisional_outcome_feasibility_summary']}; outcome-ready rows={counts['alb2012_provisional_outcome_ready_rows']}; climate-linkage ready rows={counts['alb2012_provisional_climate_linkage_ready_rows']}",
        [TEMP_DIR / "alb2012_provisional_outcome_feasibility_audit.csv", RESULT_DIR / "alb2012_provisional_outcome_feasibility_summary.csv", REPORT_DIR / "alb2012_provisional_outcome_feasibility.md"],
        "" if counts["alb2012_provisional_outcome_feasibility_audit"] > 0 and counts["alb2012_provisional_outcome_ready_rows"] == 0 else "run script/58_audit_alb2012_provisional_outcome_feasibility.py and keep ALB_2012 outcomes temp-only",
    )
    add(
        "cross_phase_alb2012_outcome_semantics_raw_value_audit",
        "phase4",
        "Audit ALB_2012 raw payment, gift, access, need, coping, and service-quality labels/values before any outcome or SDG 3.8.2 promotion.",
        status_done(
            counts["alb2012_outcome_semantics_raw_value_audit"] > 0
            and counts["alb2012_outcome_semantics_raw_value_summary"] > 0
            and counts["alb2012_outcome_semantics_outcome_ready_rows"] == 0
            and counts["alb2012_outcome_semantics_sdg382_ready_rows"] == 0
            and counts["alb2012_outcome_semantics_climate_linkage_ready_rows"] == 0
        ),
        f"audit rows={counts['alb2012_outcome_semantics_raw_value_audit']}; summary rows={counts['alb2012_outcome_semantics_raw_value_summary']}; OOP candidates={counts['alb2012_outcome_semantics_financial_oop_candidate_rows']}; gift candidates={counts['alb2012_outcome_semantics_gift_candidate_rows']}; access candidates={counts['alb2012_outcome_semantics_access_candidate_rows']}; service-quality proxy rows={counts['alb2012_outcome_semantics_service_quality_proxy_rows']}; conditional reason rows={counts['alb2012_outcome_semantics_conditional_reason_rows']}; outcome-ready rows={counts['alb2012_outcome_semantics_outcome_ready_rows']}; SDG 3.8.2-ready rows={counts['alb2012_outcome_semantics_sdg382_ready_rows']}; climate-linkage-ready rows={counts['alb2012_outcome_semantics_climate_linkage_ready_rows']}",
        [TEMP_DIR / "alb2012_outcome_semantics_raw_value_audit.csv", RESULT_DIR / "alb2012_outcome_semantics_raw_value_summary.csv", REPORT_DIR / "alb2012_outcome_semantics_raw_value_audit.md"],
        "" if counts["alb2012_outcome_semantics_raw_value_audit"] > 0 and counts["alb2012_outcome_semantics_outcome_ready_rows"] == 0 and counts["alb2012_outcome_semantics_sdg382_ready_rows"] == 0 and counts["alb2012_outcome_semantics_climate_linkage_ready_rows"] == 0 else "run script/63_audit_alb2012_outcome_semantics_raw_values.py and keep ALB_2012 outcome, SDG 3.8.2, and climate-linkage promotion blocked",
    )
    add(
        "cross_phase_alb2012_timing_geography_exhaustive_audit",
        "phase5",
        "Scan ALB_2012 raw files exhaustively for interview timing, GPS/coordinate, and usable geography evidence before any climate-linkage promotion.",
        status_done(
            counts["alb2012_timing_geography_exhaustive_audit"] > 0
            and counts["alb2012_timing_geography_exhaustive_summary"] > 0
            and counts["alb2012_interview_timing_verified_rows"] == 0
            and counts["alb2012_coordinate_candidate_rows"] == 0
            and counts["alb2012_timing_geography_climate_linkage_ready_rows"] == 0
        ),
        f"audit rows={counts['alb2012_timing_geography_exhaustive_audit']}; summary rows={counts['alb2012_timing_geography_exhaustive_summary']}; interview timing verified rows={counts['alb2012_interview_timing_verified_rows']}; coordinate candidate rows={counts['alb2012_coordinate_candidate_rows']}; climate-linkage ready rows={counts['alb2012_timing_geography_climate_linkage_ready_rows']}",
        [TEMP_DIR / "alb2012_timing_geography_exhaustive_audit.csv", RESULT_DIR / "alb2012_timing_geography_exhaustive_summary.csv", REPORT_DIR / "alb2012_timing_geography_exhaustive_audit.md"],
        "" if counts["alb2012_timing_geography_exhaustive_audit"] > 0 and counts["alb2012_timing_geography_climate_linkage_ready_rows"] == 0 else "run script/59_audit_alb2012_timing_geography_exhaustive.py and keep climate linkage blocked",
    )
    add(
        "cross_phase_alb2012_questionnaire_timing_field_audit",
        "phase5",
        "Audit ALB_2012 questionnaire control-sheet timing fields and prove they are not yet raw household timing values for climate windows.",
        status_done(
            counts["alb2012_questionnaire_timing_field_audit"] > 0
            and counts["alb2012_questionnaire_timing_raw_gap_audit"] > 0
            and counts["alb2012_questionnaire_timing_field_summary"] > 0
            and counts["alb2012_questionnaire_timing_raw_verified_interview_timing_rows"] == 0
            and counts["alb2012_questionnaire_timing_climate_linkage_ready_rows"] == 0
        ),
        f"field rows={counts['alb2012_questionnaire_timing_field_rows']}; raw gap rows={counts['alb2012_questionnaire_timing_raw_gap_rows']}; raw control candidate rows={counts['alb2012_questionnaire_timing_raw_control_candidate_rows']}; raw verified interview timing rows={counts['alb2012_questionnaire_timing_raw_verified_interview_timing_rows']}; climate-linkage ready rows={counts['alb2012_questionnaire_timing_climate_linkage_ready_rows']}",
        [TEMP_DIR / "alb2012_questionnaire_timing_field_audit.csv", TEMP_DIR / "alb2012_questionnaire_timing_raw_gap_audit.csv", RESULT_DIR / "alb2012_questionnaire_timing_field_summary.csv", REPORT_DIR / "alb2012_questionnaire_timing_field_audit.md"],
        "" if counts["alb2012_questionnaire_timing_field_audit"] > 0 and counts["alb2012_questionnaire_timing_raw_verified_interview_timing_rows"] == 0 and counts["alb2012_questionnaire_timing_climate_linkage_ready_rows"] == 0 else "run script/65_audit_alb2012_questionnaire_timing_fields.py and keep ALB_2012 climate linkage blocked until raw household interview timing is verified",
    )
    add(
        "cross_phase_albania_legacy_questionnaire_readability_audit",
        "phase2",
        "Inventory ALB_2002/2005/2008 legacy questionnaire workbooks and verify whether the current environment can read them before using questionnaire timing or skip-pattern evidence.",
        status_done(
            counts["albania_legacy_questionnaire_readability_audit"] > 0
            and counts["albania_legacy_questionnaire_readability_summary"] > 0
            and counts["albania_legacy_questionnaire_present_files"] == 5
            and counts["albania_legacy_questionnaire_read_ok_files"] == 5
            and counts["albania_legacy_questionnaire_timing_content_audit_ready_rows"] == 5
            and counts["albania_legacy_questionnaire_climate_linkage_ready_rows"] == 0
        ),
        f"present files={counts['albania_legacy_questionnaire_present_files']}; read-ok files={counts['albania_legacy_questionnaire_read_ok_files']}; missing-reader blocked files={counts['albania_legacy_questionnaire_missing_reader_blocked_files']}; timing-content-ready rows={counts['albania_legacy_questionnaire_timing_content_audit_ready_rows']}; climate-linkage ready rows={counts['albania_legacy_questionnaire_climate_linkage_ready_rows']}",
        [TEMP_DIR / "albania_legacy_questionnaire_readability_audit.csv", RESULT_DIR / "albania_legacy_questionnaire_readability_summary.csv", REPORT_DIR / "albania_legacy_questionnaire_readability_audit.md"],
        "" if counts["albania_legacy_questionnaire_readability_audit"] > 0 and counts["albania_legacy_questionnaire_read_ok_files"] == 5 and counts["albania_legacy_questionnaire_climate_linkage_ready_rows"] == 0 else "run script/66_audit_albania_legacy_questionnaire_readability.py before any legacy questionnaire content audit",
    )
    add(
        "cross_phase_albania_legacy_questionnaire_timing_field_audit",
        "phase5",
        "Audit readable ALB_2002/2005/2008 legacy questionnaire timing/control fields and keep them out of climate linkage unless raw household timing/geography gates pass.",
        status_done(
            counts["albania_legacy_questionnaire_timing_field_audit"] > 0
            and counts["albania_legacy_questionnaire_timing_raw_gap_audit"] > 0
            and counts["albania_legacy_questionnaire_timing_field_summary"] > 0
            and counts["albania_legacy_questionnaire_timing_raw_verified_interview_timing_rows"] > 0
            and counts["albania_legacy_questionnaire_timing_climate_linkage_ready_rows"] == 0
        ),
        f"field rows={counts['albania_legacy_questionnaire_timing_field_rows']}; raw gap rows={counts['albania_legacy_questionnaire_timing_raw_gap_rows']}; raw verified interview timing rows={counts['albania_legacy_questionnaire_timing_raw_verified_interview_timing_rows']}; climate-linkage ready rows={counts['albania_legacy_questionnaire_timing_climate_linkage_ready_rows']}",
        [TEMP_DIR / "albania_legacy_questionnaire_timing_field_audit.csv", TEMP_DIR / "albania_legacy_questionnaire_timing_raw_gap_audit.csv", RESULT_DIR / "albania_legacy_questionnaire_timing_field_summary.csv", REPORT_DIR / "albania_legacy_questionnaire_timing_field_audit.md"],
        "" if counts["albania_legacy_questionnaire_timing_field_audit"] > 0 and counts["albania_legacy_questionnaire_timing_climate_linkage_ready_rows"] == 0 else "run script/67_audit_albania_legacy_questionnaire_timing_fields.py and keep legacy questionnaire timing evidence out of climate linkage until raw timing/geography gates pass",
    )
    add(
        "cross_phase_alb2005_documented_harmonization_review",
        "phase3",
        "For raw-ready ALB_2005, verify documented candidates and false positives before harmonization recipe promotion.",
        status_done(
            counts["alb2005_documented_variable_evidence"] > 0
            and counts["alb2005_documented_harmonization_summary"] > 0
            and counts["alb2005_recipe_ready_rows"] == 0
        ),
        f"evidence rows={counts['alb2005_documented_variable_evidence']}; summary rows={counts['alb2005_documented_harmonization_summary']}; recipe-ready rows={counts['alb2005_recipe_ready_rows']}",
        [TEMP_DIR / "alb2005_documented_variable_evidence.csv", RESULT_DIR / "alb2005_documented_harmonization_summary.csv", REPORT_DIR / "alb2005_documented_harmonization_review.md"],
        "" if counts["alb2005_documented_variable_evidence"] > 0 and counts["alb2005_recipe_ready_rows"] == 0 else "run script/46_build_alb2005_documented_harmonization_review.py and keep recipe promotion blocked",
    )
    add(
        "cross_phase_alb2005_household_core_merge_audit",
        "phase3",
        "Build a temp-only ALB_2005 household core candidate only after merge-key coverage is audited, and keep it out of data until recipe gates pass.",
        status_done(
            counts["alb2005_household_core_candidate"] > 0
            and counts["alb2005_household_core_merge_audit"] > 0
            and counts["alb2005_household_core_lineage"] > 0
            and counts["alb2005_household_core_candidate_summary"] > 0
            and counts["alb2005_household_core_recipe_ready_rows"] == 0
        ),
        f"candidate rows={counts['alb2005_household_core_candidate']}; merge audit rows={counts['alb2005_household_core_merge_audit']}; lineage rows={counts['alb2005_household_core_lineage']}; summary rows={counts['alb2005_household_core_candidate_summary']}; recipe-ready rows={counts['alb2005_household_core_recipe_ready_rows']}",
        [TEMP_DIR / "alb2005_household_core_candidate.csv", TEMP_DIR / "alb2005_household_core_merge_audit.csv", TEMP_DIR / "alb2005_household_core_lineage.csv", RESULT_DIR / "alb2005_household_core_candidate_summary.csv", REPORT_DIR / "alb2005_household_core_merge_audit.md"],
        "" if counts["alb2005_household_core_candidate"] > 0 and counts["alb2005_household_core_recipe_ready_rows"] == 0 else "run script/47_audit_alb2005_household_core_merge.py and keep the output temp-only",
    )
    add(
        "cross_phase_alb2005_provisional_outcome_feasibility",
        "phase4",
        "Compute ALB_2005 provisional outcome event-rate diagnostics only after raw household-core assembly, and keep all final outcome promotion blocked.",
        status_done(
            counts["alb2005_provisional_outcome_feasibility_audit"] > 0
            and counts["alb2005_provisional_outcome_feasibility_summary"] > 0
            and counts["alb2005_provisional_outcome_ready_rows"] == 0
        ),
        f"audit rows={counts['alb2005_provisional_outcome_feasibility_audit']}; summary rows={counts['alb2005_provisional_outcome_feasibility_summary']}; ready rows={counts['alb2005_provisional_outcome_ready_rows']}",
        [TEMP_DIR / "alb2005_provisional_outcome_feasibility_audit.csv", RESULT_DIR / "alb2005_provisional_outcome_feasibility_summary.csv", REPORT_DIR / "alb2005_provisional_outcome_feasibility.md"],
        "" if counts["alb2005_provisional_outcome_feasibility_audit"] > 0 and counts["alb2005_provisional_outcome_ready_rows"] == 0 else "run script/48_audit_alb2005_provisional_outcome_feasibility.py and keep provisional outcome promotion blocked",
    )
    add(
        "cross_phase_alb2005_outcome_semantics_raw_value_audit",
        "phase4",
        "Audit ALB_2005 raw payment, gift, access, need, and coping labels/values before any outcome or SDG 3.8.2 promotion.",
        status_done(
            counts["alb2005_outcome_semantics_raw_value_audit"] > 0
            and counts["alb2005_outcome_semantics_raw_value_summary"] > 0
            and counts["alb2005_outcome_semantics_outcome_ready_rows"] == 0
            and counts["alb2005_outcome_semantics_sdg382_ready_rows"] == 0
            and counts["alb2005_outcome_semantics_climate_linkage_ready_rows"] == 0
        ),
        f"audit rows={counts['alb2005_outcome_semantics_raw_value_audit']}; summary rows={counts['alb2005_outcome_semantics_raw_value_summary']}; OOP candidates={counts['alb2005_outcome_semantics_financial_oop_candidate_rows']}; gift candidates={counts['alb2005_outcome_semantics_gift_candidate_rows']}; access candidates={counts['alb2005_outcome_semantics_access_candidate_rows']}; conditional reason rows={counts['alb2005_outcome_semantics_conditional_reason_rows']}; outcome-ready rows={counts['alb2005_outcome_semantics_outcome_ready_rows']}; SDG 3.8.2-ready rows={counts['alb2005_outcome_semantics_sdg382_ready_rows']}; climate-linkage-ready rows={counts['alb2005_outcome_semantics_climate_linkage_ready_rows']}",
        [TEMP_DIR / "alb2005_outcome_semantics_raw_value_audit.csv", RESULT_DIR / "alb2005_outcome_semantics_raw_value_summary.csv", REPORT_DIR / "alb2005_outcome_semantics_raw_value_audit.md"],
        "" if counts["alb2005_outcome_semantics_raw_value_audit"] > 0 and counts["alb2005_outcome_semantics_outcome_ready_rows"] == 0 and counts["alb2005_outcome_semantics_sdg382_ready_rows"] == 0 and counts["alb2005_outcome_semantics_climate_linkage_ready_rows"] == 0 else "run script/61_audit_alb2005_outcome_semantics_raw_values.py and keep ALB_2005 outcome, SDG 3.8.2, and climate-linkage promotion blocked",
    )
    add(
        "cross_phase_alb2005_timing_geography_exhaustive_audit",
        "phase5",
        "Exhaustively scan ALB_2005 raw timing/geography candidates before constructing climate-linkage inputs, and keep linkage blocked until interview timing and geography are verified.",
        status_done(
            counts["alb2005_timing_geography_exhaustive_audit"] > 0
            and counts["alb2005_timing_geography_exhaustive_summary"] > 0
            and counts["alb2005_climate_linkage_ready_rows"] == 0
        ),
        f"audit rows={counts['alb2005_timing_geography_exhaustive_audit']}; summary rows={counts['alb2005_timing_geography_exhaustive_summary']}; climate-linkage-ready rows={counts['alb2005_climate_linkage_ready_rows']}",
        [TEMP_DIR / "alb2005_timing_geography_exhaustive_audit.csv", RESULT_DIR / "alb2005_timing_geography_exhaustive_summary.csv", REPORT_DIR / "alb2005_timing_geography_exhaustive_audit.md"],
        "" if counts["alb2005_timing_geography_exhaustive_audit"] > 0 and counts["alb2005_climate_linkage_ready_rows"] == 0 else "run script/49_audit_alb2005_timing_geography_exhaustive.py and keep climate linkage blocked",
    )
    timing_source_decision = str(counts.get("alb2005_timing_geography_source_search_current_decision", ""))
    add(
        "cross_phase_alb2005_timing_geography_source_search_audit",
        "phase5",
        "Search ALB_2005 raw schema, file inventory, questionnaires, and upstream audit evidence for household interview timing and current-location geography before any climate-linkage promotion.",
        status_done(
            counts["alb2005_timing_geography_source_search_audit"] > 0
            and counts["alb2005_timing_geography_source_search_summary"] > 0
            and counts["alb2005_timing_geography_source_search_rows"] > 0
            and counts["alb2005_timing_geography_source_search_target_concepts"] == 5
            and counts["alb2005_timing_geography_source_search_local_files_scanned"] > 0
            and counts["alb2005_timing_geography_source_search_local_variables_scanned"] > 0
            and counts["alb2005_timing_geography_source_search_questionnaire_workbooks_scanned"] > 0
            and counts["alb2005_timing_geography_source_search_raw_targets_with_hits"] > 0
            and counts["alb2005_timing_geography_source_search_questionnaire_targets_with_hits"] == 5
            and counts["alb2005_timing_geography_source_search_legacy_questionnaire_timing_rows"] > 0
            and counts["alb2005_timing_geography_source_search_verified_household_timing_rows"] == 0
            and counts["alb2005_timing_geography_source_search_coordinate_candidate_rows"] == 0
            and counts["alb2005_timing_geography_source_search_partial_district_variable_rows"] > 0
            and counts["alb2005_timing_geography_source_search_partial_district_name_nonmissing_rows"] > 0
            and counts["alb2005_timing_geography_source_search_partial_district_code_nonmissing_rows"] > 0
            and counts["alb2005_timing_geography_source_search_required_value_key_timing_rows"] == 0
            and counts["alb2005_timing_geography_source_search_required_value_key_coordinate_rows"] == 0
            and counts["alb2005_timing_geography_source_search_geography_crosswalk_ready_rows"] == 0
            and counts["alb2005_timing_geography_source_search_interview_timing_ready_rows"] == 0
            and counts["alb2005_timing_geography_source_search_climate_linkage_ready_rows"] == 0
            and timing_source_decision == "blocked_alb2005_timing_geography_source_search_not_ready"
        ),
        f"audit rows={counts['alb2005_timing_geography_source_search_audit']}; summary rows={counts['alb2005_timing_geography_source_search_summary']}; evidence rows={counts['alb2005_timing_geography_source_search_rows']}; target concepts={counts['alb2005_timing_geography_source_search_target_concepts']}; local files scanned={counts['alb2005_timing_geography_source_search_local_files_scanned']}; local variables scanned={counts['alb2005_timing_geography_source_search_local_variables_scanned']}; questionnaire workbooks={counts['alb2005_timing_geography_source_search_questionnaire_workbooks_scanned']}; raw targets with hits={counts['alb2005_timing_geography_source_search_raw_targets_with_hits']}; questionnaire targets with hits={counts['alb2005_timing_geography_source_search_questionnaire_targets_with_hits']}; legacy timing rows={counts['alb2005_timing_geography_source_search_legacy_questionnaire_timing_rows']}; verified timing rows={counts['alb2005_timing_geography_source_search_verified_household_timing_rows']}; coordinate candidates={counts['alb2005_timing_geography_source_search_coordinate_candidate_rows']}; partial district variables={counts['alb2005_timing_geography_source_search_partial_district_variable_rows']}; district-name rows={counts['alb2005_timing_geography_source_search_partial_district_name_nonmissing_rows']}; district-code rows={counts['alb2005_timing_geography_source_search_partial_district_code_nonmissing_rows']}; required-value timing rows={counts['alb2005_timing_geography_source_search_required_value_key_timing_rows']}; required-value coordinate rows={counts['alb2005_timing_geography_source_search_required_value_key_coordinate_rows']}; geography-ready rows={counts['alb2005_timing_geography_source_search_geography_crosswalk_ready_rows']}; interview-ready rows={counts['alb2005_timing_geography_source_search_interview_timing_ready_rows']}; climate-ready rows={counts['alb2005_timing_geography_source_search_climate_linkage_ready_rows']}; decision={timing_source_decision}",
        [TEMP_DIR / "alb2005_timing_geography_source_search_audit.csv", RESULT_DIR / "alb2005_timing_geography_source_search_summary.csv", REPORT_DIR / "alb2005_timing_geography_source_search_audit.md"],
        "" if counts["alb2005_timing_geography_source_search_audit"] > 0 and counts["alb2005_timing_geography_source_search_verified_household_timing_rows"] == 0 and counts["alb2005_timing_geography_source_search_coordinate_candidate_rows"] == 0 and counts["alb2005_timing_geography_source_search_climate_linkage_ready_rows"] == 0 else "run script/78_audit_alb2005_timing_geography_source_search.py and keep ALB_2005 climate promotion blocked",
    )
    add(
        "cross_phase_alb2005_required_value_key_audit",
        "phase3",
        "Read ALB_2005 raw files for required value/key distributions, coverage, and labels while keeping recipe promotion blocked until timing, geography, unit, recall, and skip-pattern gates pass.",
        status_done(
            counts["alb2005_required_value_key_audit"] > 0
            and counts["alb2005_required_value_key_summary"] > 0
            and counts["alb2005_required_value_key_recipe_ready_rows"] == 0
            and counts["alb2005_required_value_key_not_promoted_rows"] > 0
            and counts["alb2005_required_value_key_interview_timing_verified_rows"] == 0
            and counts["alb2005_required_value_key_coordinate_ready_rows"] == 0
            and counts["alb2005_required_value_key_climate_linkage_ready_rows"] == 0
        ),
        f"audit rows={counts['alb2005_required_value_key_audit']}; summary rows={counts['alb2005_required_value_key_summary']}; total-consumption nonmissing={counts['alb2005_required_value_key_total_consumption_nonmissing_rows']}; OOP 4w positive households={counts['alb2005_required_value_key_oop_4w_household_positive_rows']}; OOP 12m positive households={counts['alb2005_required_value_key_oop_12m_household_positive_rows']}; district-code nonmissing={counts['alb2005_required_value_key_district_code_nonmissing_rows']}; timing rows={counts['alb2005_required_value_key_interview_timing_verified_rows']}; coordinate-ready rows={counts['alb2005_required_value_key_coordinate_ready_rows']}; climate-ready rows={counts['alb2005_required_value_key_climate_linkage_ready_rows']}; recipe-ready rows={counts['alb2005_required_value_key_recipe_ready_rows']}",
        [TEMP_DIR / "alb2005_required_value_key_audit.csv", RESULT_DIR / "alb2005_required_value_key_summary.csv", REPORT_DIR / "alb2005_required_value_key_audit.md"],
        "" if counts["alb2005_required_value_key_audit"] > 0 and counts["alb2005_required_value_key_recipe_ready_rows"] == 0 and counts["alb2005_required_value_key_climate_linkage_ready_rows"] == 0 else "run script/71_audit_alb2005_required_value_key_evidence.py and keep ALB_2005 recipe promotion blocked",
    )
    add(
        "cross_phase_alb2005_health_questionnaire_semantics_audit",
        "phase3",
        "Read the ALB_2005 health questionnaire to document OOP recall/unit/scope and access-barrier semantics while keeping recipe, outcome, and climate promotion blocked.",
        status_done(
            counts["alb2005_health_questionnaire_semantics_audit"] > 0
            and counts["alb2005_health_questionnaire_semantics_summary"] > 0
            and counts["alb2005_health_questionnaire_oop_item_rows"] > 0
            and counts["alb2005_health_questionnaire_old_lek_unit_rows"] > 0
            and counts["alb2005_health_questionnaire_access_rows"] > 0
            and counts["alb2005_health_questionnaire_recipe_ready_rows"] == 0
            and counts["alb2005_health_questionnaire_outcome_ready_rows"] == 0
            and counts["alb2005_health_questionnaire_climate_linkage_ready_rows"] == 0
        ),
        f"audit rows={counts['alb2005_health_questionnaire_semantics_audit']}; summary rows={counts['alb2005_health_questionnaire_semantics_summary']}; OOP item rows={counts['alb2005_health_questionnaire_oop_item_rows']}; old-lek rows={counts['alb2005_health_questionnaire_old_lek_unit_rows']}; access rows={counts['alb2005_health_questionnaire_access_rows']}; cost-barrier rows={counts['alb2005_health_questionnaire_cost_barrier_rows']}; recipe-ready rows={counts['alb2005_health_questionnaire_recipe_ready_rows']}; outcome-ready rows={counts['alb2005_health_questionnaire_outcome_ready_rows']}; climate-ready rows={counts['alb2005_health_questionnaire_climate_linkage_ready_rows']}",
        [TEMP_DIR / "alb2005_health_questionnaire_semantics_audit.csv", RESULT_DIR / "alb2005_health_questionnaire_semantics_summary.csv", REPORT_DIR / "alb2005_health_questionnaire_semantics_audit.md"],
        "" if counts["alb2005_health_questionnaire_semantics_audit"] > 0 and counts["alb2005_health_questionnaire_recipe_ready_rows"] == 0 and counts["alb2005_health_questionnaire_outcome_ready_rows"] == 0 and counts["alb2005_health_questionnaire_climate_linkage_ready_rows"] == 0 else "run script/72_audit_alb2005_health_questionnaire_semantics.py and keep ALB_2005 recipe/outcome/climate promotion blocked",
    )
    add(
        "cross_phase_alb2005_oop_aggregation_policy_audit",
        "phase4",
        "Stress-test ALB_2005 OOP aggregation choices against questionnaire-backed payment-scope evidence without constructing final outcomes.",
        status_done(
            counts["alb2005_oop_aggregation_policy_audit"] > 0
            and counts["alb2005_oop_aggregation_policy_summary"] > 0
            and counts["alb2005_oop_aggregation_policy_rows"] > 0
            and counts["alb2005_oop_aggregation_policy_questionnaire_oop_item_rows_observed"] > 0
            and counts["alb2005_oop_aggregation_policy_questionnaire_old_lek_rows_observed"] > 0
            and counts["alb2005_oop_aggregation_policy_outcome_ready_rows"] == 0
            and counts["alb2005_oop_aggregation_policy_recipe_ready_rows"] == 0
            and counts["alb2005_oop_aggregation_policy_climate_linkage_ready_rows"] == 0
        ),
        f"audit rows={counts['alb2005_oop_aggregation_policy_audit']}; summary rows={counts['alb2005_oop_aggregation_policy_summary']}; policies={counts['alb2005_oop_aggregation_policy_rows']}; households={counts['alb2005_oop_aggregation_policy_household_rows']}; total-consumption rows={counts['alb2005_oop_aggregation_policy_total_consumption_rows']}; questionnaire OOP rows={counts['alb2005_oop_aggregation_policy_questionnaire_oop_item_rows_observed']}; old-lek rows={counts['alb2005_oop_aggregation_policy_questionnaire_old_lek_rows_observed']}; outcome-ready rows={counts['alb2005_oop_aggregation_policy_outcome_ready_rows']}; recipe-ready rows={counts['alb2005_oop_aggregation_policy_recipe_ready_rows']}; climate-ready rows={counts['alb2005_oop_aggregation_policy_climate_linkage_ready_rows']}",
        [TEMP_DIR / "alb2005_oop_aggregation_policy_audit.csv", RESULT_DIR / "alb2005_oop_aggregation_policy_summary.csv", REPORT_DIR / "alb2005_oop_aggregation_policy_audit.md"],
        "" if counts["alb2005_oop_aggregation_policy_audit"] > 0 and counts["alb2005_oop_aggregation_policy_outcome_ready_rows"] == 0 and counts["alb2005_oop_aggregation_policy_recipe_ready_rows"] == 0 and counts["alb2005_oop_aggregation_policy_climate_linkage_ready_rows"] == 0 else "run script/73_audit_alb2005_oop_aggregation_policy.py and keep ALB_2005 outcome/recipe/climate promotion blocked",
    )
    add(
        "cross_phase_alb2005_skip_missing_semantics_audit",
        "phase4",
        "Audit ALB_2005 raw trigger/downstream skip and missing-code behavior before any outcome construction or harmonization recipe promotion.",
        status_done(
            counts["alb2005_skip_missing_semantics_audit"] > 0
            and counts["alb2005_skip_missing_semantics_summary"] > 0
            and counts["alb2005_skip_missing_semantics_rows"] > 0
            and counts["alb2005_skip_missing_payment_nonmissing_when_not_triggered_rows"] == 0
            and counts["alb2005_skip_missing_payment_positive_when_not_triggered_rows"] == 0
            and counts["alb2005_skip_missing_condition_nonmissing_when_not_triggered_rows"] == 0
            and counts["alb2005_skip_missing_condition_missing_when_triggered_rows"] == 0
            and counts["alb2005_skip_missing_financing_nonmissing_when_not_triggered_rows"] == 0
            and counts["alb2005_skip_missing_financing_missing_when_triggered_rows"] == 0
            and counts["alb2005_skip_missing_recipe_ready_rows"] == 0
            and counts["alb2005_skip_missing_outcome_ready_rows"] == 0
            and counts["alb2005_skip_missing_climate_linkage_ready_rows"] == 0
        ),
        f"audit rows={counts['alb2005_skip_missing_semantics_audit']}; summary rows={counts['alb2005_skip_missing_semantics_summary']}; skip rows={counts['alb2005_skip_missing_semantics_rows']}; payment nonmissing leaks={counts['alb2005_skip_missing_payment_nonmissing_when_not_triggered_rows']}; payment positive leaks={counts['alb2005_skip_missing_payment_positive_when_not_triggered_rows']}; condition leaks={counts['alb2005_skip_missing_condition_nonmissing_when_not_triggered_rows']}; condition missing when triggered={counts['alb2005_skip_missing_condition_missing_when_triggered_rows']}; financing leaks={counts['alb2005_skip_missing_financing_nonmissing_when_not_triggered_rows']}; financing missing when triggered={counts['alb2005_skip_missing_financing_missing_when_triggered_rows']}; zero-or-missing triggered payment rows={counts['alb2005_skip_missing_payment_zero_or_missing_when_triggered_rows']}; recipe-ready rows={counts['alb2005_skip_missing_recipe_ready_rows']}; outcome-ready rows={counts['alb2005_skip_missing_outcome_ready_rows']}; climate-ready rows={counts['alb2005_skip_missing_climate_linkage_ready_rows']}",
        [TEMP_DIR / "alb2005_skip_missing_semantics_audit.csv", RESULT_DIR / "alb2005_skip_missing_semantics_summary.csv", REPORT_DIR / "alb2005_skip_missing_semantics_audit.md"],
        "" if counts["alb2005_skip_missing_semantics_audit"] > 0 and counts["alb2005_skip_missing_recipe_ready_rows"] == 0 and counts["alb2005_skip_missing_outcome_ready_rows"] == 0 and counts["alb2005_skip_missing_climate_linkage_ready_rows"] == 0 else "run script/74_audit_alb2005_skip_missing_semantics.py and keep ALB_2005 recipe/outcome/climate promotion blocked",
    )
    unit_period_decision = str(counts.get("alb2005_consumption_oop_unit_period_current_decision", ""))
    add(
        "cross_phase_alb2005_consumption_oop_unit_period_audit",
        "phase4",
        "Audit ALB_2005 total-consumption unit/period evidence and OOP recall-period compatibility before any CHE, SDG 3.8.2, recipe, or climate-linkage promotion.",
        status_done(
            counts["alb2005_consumption_oop_unit_period_audit"] > 0
            and counts["alb2005_consumption_oop_unit_period_summary"] > 0
            and counts["alb2005_consumption_oop_unit_period_rows"] > 0
            and counts["alb2005_consumption_oop_unit_period_total_consumption_positive_rows"] > 0
            and counts["alb2005_consumption_oop_unit_period_rcons_positive_rows"] > 0
            and counts["alb2005_consumption_oop_unit_period_metadata_old_lek_rows"] > 0
            and counts["alb2005_consumption_oop_unit_period_oop_old_lek_rows"] > 0
            and counts["alb2005_consumption_oop_unit_period_four_week_oop_rows"] > 0
            and counts["alb2005_consumption_oop_unit_period_twelve_month_oop_rows"] > 0
            and counts["alb2005_consumption_oop_unit_period_questionnaire_nonfood_old_lek_rows"] > 0
            and counts["alb2005_consumption_oop_unit_period_sdg382_ready_rows"] == 0
            and counts["alb2005_consumption_oop_unit_period_recipe_ready_rows"] == 0
            and counts["alb2005_consumption_oop_unit_period_outcome_ready_rows"] == 0
            and counts["alb2005_consumption_oop_unit_period_climate_linkage_ready_rows"] == 0
            and unit_period_decision == "blocked_alb2005_consumption_oop_unit_period_not_ready"
        ),
        f"audit rows={counts['alb2005_consumption_oop_unit_period_audit']}; summary rows={counts['alb2005_consumption_oop_unit_period_summary']}; evidence rows={counts['alb2005_consumption_oop_unit_period_rows']}; positive total-consumption rows={counts['alb2005_consumption_oop_unit_period_total_consumption_positive_rows']}; positive rcons rows={counts['alb2005_consumption_oop_unit_period_rcons_positive_rows']}; metadata old-lek rows={counts['alb2005_consumption_oop_unit_period_metadata_old_lek_rows']}; OOP old-lek rows={counts['alb2005_consumption_oop_unit_period_oop_old_lek_rows']}; four-week OOP rows={counts['alb2005_consumption_oop_unit_period_four_week_oop_rows']}; twelve-month OOP rows={counts['alb2005_consumption_oop_unit_period_twelve_month_oop_rows']}; nonfood old-lek questionnaire rows={counts['alb2005_consumption_oop_unit_period_questionnaire_nonfood_old_lek_rows']}; SDG-ready rows={counts['alb2005_consumption_oop_unit_period_sdg382_ready_rows']}; recipe-ready rows={counts['alb2005_consumption_oop_unit_period_recipe_ready_rows']}; outcome-ready rows={counts['alb2005_consumption_oop_unit_period_outcome_ready_rows']}; climate-ready rows={counts['alb2005_consumption_oop_unit_period_climate_linkage_ready_rows']}; decision={unit_period_decision}",
        [TEMP_DIR / "alb2005_consumption_oop_unit_period_audit.csv", RESULT_DIR / "alb2005_consumption_oop_unit_period_summary.csv", REPORT_DIR / "alb2005_consumption_oop_unit_period_audit.md"],
        "" if counts["alb2005_consumption_oop_unit_period_audit"] > 0 and counts["alb2005_consumption_oop_unit_period_sdg382_ready_rows"] == 0 and counts["alb2005_consumption_oop_unit_period_recipe_ready_rows"] == 0 and counts["alb2005_consumption_oop_unit_period_outcome_ready_rows"] == 0 and counts["alb2005_consumption_oop_unit_period_climate_linkage_ready_rows"] == 0 else "run script/75_audit_alb2005_consumption_oop_unit_period.py and keep ALB_2005 SDG/recipe/outcome/climate promotion blocked",
    )
    aggregate_crosswalk_decision = str(counts.get("alb2005_consumption_aggregate_crosswalk_current_decision", ""))
    add(
        "cross_phase_alb2005_consumption_aggregate_metadata_crosswalk_audit",
        "phase4",
        "Crosswalk ALB_2005 public metadata aggregate/component variables against local poverty.sav before denominator reconstruction or variant choice.",
        status_done(
            counts["alb2005_consumption_aggregate_crosswalk_audit"] > 0
            and counts["alb2005_consumption_aggregate_crosswalk_summary"] > 0
            and counts["alb2005_consumption_aggregate_crosswalk_rows"] > 0
            and counts["alb2005_consumption_aggregate_crosswalk_metadata_rows"] > 0
            and counts["alb2005_consumption_aggregate_crosswalk_local_poverty_columns"] > 0
            and counts["alb2005_consumption_aggregate_crosswalk_metadata_present_local_rows"] == 1
            and counts["alb2005_consumption_aggregate_crosswalk_metadata_absent_local_rows"] > 0
            and counts["alb2005_consumption_aggregate_crosswalk_local_per_capita_component_rows"] > 0
            and counts["alb2005_consumption_aggregate_crosswalk_totcons_positive_rows"] > 0
            and counts["alb2005_consumption_aggregate_crosswalk_totcons05_local_rows"] == 0
            and counts["alb2005_consumption_aggregate_crosswalk_component_formula_reconstructable_rows"] == 0
            and counts["alb2005_consumption_aggregate_crosswalk_sdg382_ready_rows"] == 0
            and counts["alb2005_consumption_aggregate_crosswalk_recipe_ready_rows"] == 0
            and counts["alb2005_consumption_aggregate_crosswalk_outcome_ready_rows"] == 0
            and counts["alb2005_consumption_aggregate_crosswalk_climate_linkage_ready_rows"] == 0
            and aggregate_crosswalk_decision == "blocked_alb2005_consumption_aggregate_metadata_crosswalk_not_ready"
        ),
        f"audit rows={counts['alb2005_consumption_aggregate_crosswalk_audit']}; summary rows={counts['alb2005_consumption_aggregate_crosswalk_summary']}; evidence rows={counts['alb2005_consumption_aggregate_crosswalk_rows']}; metadata rows={counts['alb2005_consumption_aggregate_crosswalk_metadata_rows']}; local poverty columns={counts['alb2005_consumption_aggregate_crosswalk_local_poverty_columns']}; metadata present locally={counts['alb2005_consumption_aggregate_crosswalk_metadata_present_local_rows']}; metadata absent locally={counts['alb2005_consumption_aggregate_crosswalk_metadata_absent_local_rows']}; per-capita diagnostics={counts['alb2005_consumption_aggregate_crosswalk_local_per_capita_component_rows']}; positive totcons rows={counts['alb2005_consumption_aggregate_crosswalk_totcons_positive_rows']}; local totcons05 rows={counts['alb2005_consumption_aggregate_crosswalk_totcons05_local_rows']}; formula reconstructable rows={counts['alb2005_consumption_aggregate_crosswalk_component_formula_reconstructable_rows']}; SDG-ready rows={counts['alb2005_consumption_aggregate_crosswalk_sdg382_ready_rows']}; recipe-ready rows={counts['alb2005_consumption_aggregate_crosswalk_recipe_ready_rows']}; outcome-ready rows={counts['alb2005_consumption_aggregate_crosswalk_outcome_ready_rows']}; climate-ready rows={counts['alb2005_consumption_aggregate_crosswalk_climate_linkage_ready_rows']}; decision={aggregate_crosswalk_decision}",
        [TEMP_DIR / "alb2005_consumption_aggregate_metadata_crosswalk_audit.csv", RESULT_DIR / "alb2005_consumption_aggregate_metadata_crosswalk_summary.csv", REPORT_DIR / "alb2005_consumption_aggregate_metadata_crosswalk_audit.md"],
        "" if counts["alb2005_consumption_aggregate_crosswalk_audit"] > 0 and counts["alb2005_consumption_aggregate_crosswalk_sdg382_ready_rows"] == 0 and counts["alb2005_consumption_aggregate_crosswalk_recipe_ready_rows"] == 0 and counts["alb2005_consumption_aggregate_crosswalk_outcome_ready_rows"] == 0 and counts["alb2005_consumption_aggregate_crosswalk_climate_linkage_ready_rows"] == 0 else "run script/76_audit_alb2005_consumption_aggregate_metadata_crosswalk.py and keep ALB_2005 SDG/recipe/outcome/climate promotion blocked",
    )
    component_source_decision = str(counts.get("alb2005_consumption_component_source_search_current_decision", ""))
    add(
        "cross_phase_alb2005_consumption_component_source_search_audit",
        "phase4",
        "Search local ALB_2005 raw schema, questionnaires, and source-code-like files for public-metadata consumption components before denominator reconstruction.",
        status_done(
            counts["alb2005_consumption_component_source_search_audit"] > 0
            and counts["alb2005_consumption_component_source_search_summary"] > 0
            and counts["alb2005_consumption_component_source_search_rows"] > 0
            and counts["alb2005_consumption_component_source_search_target_variables"] == 9
            and counts["alb2005_consumption_component_source_search_local_files_scanned"] > 0
            and counts["alb2005_consumption_component_source_search_local_variables_scanned"] > 0
            and counts["alb2005_consumption_component_source_search_exact_target_variables_found"] == 1
            and counts["alb2005_consumption_component_source_search_exact_target_variables_missing"] == 8
            and counts["alb2005_consumption_component_source_search_construction_code_files_found"] == 0
            and counts["alb2005_consumption_component_source_search_construction_code_targets_found"] == 0
            and counts["alb2005_consumption_component_source_search_recipe_ready_rows"] == 0
            and counts["alb2005_consumption_component_source_search_outcome_ready_rows"] == 0
            and counts["alb2005_consumption_component_source_search_sdg382_ready_rows"] == 0
            and counts["alb2005_consumption_component_source_search_climate_linkage_ready_rows"] == 0
            and component_source_decision == "blocked_alb2005_consumption_component_source_search_not_ready"
        ),
        f"audit rows={counts['alb2005_consumption_component_source_search_audit']}; summary rows={counts['alb2005_consumption_component_source_search_summary']}; evidence rows={counts['alb2005_consumption_component_source_search_rows']}; targets={counts['alb2005_consumption_component_source_search_target_variables']}; local files scanned={counts['alb2005_consumption_component_source_search_local_files_scanned']}; local variables scanned={counts['alb2005_consumption_component_source_search_local_variables_scanned']}; exact target variables found={counts['alb2005_consumption_component_source_search_exact_target_variables_found']}; exact target variables missing={counts['alb2005_consumption_component_source_search_exact_target_variables_missing']}; label phrase targets={counts['alb2005_consumption_component_source_search_label_phrase_targets_found']}; questionnaire phrase targets={counts['alb2005_consumption_component_source_search_questionnaire_phrase_targets_found']}; construction code files={counts['alb2005_consumption_component_source_search_construction_code_files_found']}; construction code targets={counts['alb2005_consumption_component_source_search_construction_code_targets_found']}; recipe-ready rows={counts['alb2005_consumption_component_source_search_recipe_ready_rows']}; outcome-ready rows={counts['alb2005_consumption_component_source_search_outcome_ready_rows']}; SDG-ready rows={counts['alb2005_consumption_component_source_search_sdg382_ready_rows']}; climate-ready rows={counts['alb2005_consumption_component_source_search_climate_linkage_ready_rows']}; decision={component_source_decision}",
        [TEMP_DIR / "alb2005_consumption_component_source_search_audit.csv", RESULT_DIR / "alb2005_consumption_component_source_search_summary.csv", REPORT_DIR / "alb2005_consumption_component_source_search_audit.md"],
        "" if counts["alb2005_consumption_component_source_search_audit"] > 0 and counts["alb2005_consumption_component_source_search_recipe_ready_rows"] == 0 and counts["alb2005_consumption_component_source_search_outcome_ready_rows"] == 0 and counts["alb2005_consumption_component_source_search_sdg382_ready_rows"] == 0 and counts["alb2005_consumption_component_source_search_climate_linkage_ready_rows"] == 0 else "run script/77_audit_alb2005_consumption_component_source_search.py and keep ALB_2005 SDG/recipe/outcome/climate promotion blocked",
    )
    add(
        "cross_phase_alb2005_harmonization_value_decision_audit",
        "phase3",
        "Classify ALB_2005 harmonization gate blockers using wave-specific source evidence, while keeping value-audit and recipe promotion fail-closed.",
        status_done(
            counts["alb2005_harmonization_value_decision_audit"] > 0
            and counts["alb2005_harmonization_value_decision_summary"] > 0
            and counts["alb2005_harmonization_value_decision_recipe_ready_rows"] == 0
            and counts["alb2005_harmonization_value_decision_required_blocked_rows"] > 0
        ),
        f"audit rows={counts['alb2005_harmonization_value_decision_audit']}; summary rows={counts['alb2005_harmonization_value_decision_summary']}; recipe-ready rows={counts['alb2005_harmonization_value_decision_recipe_ready_rows']}; required blocked rows={counts['alb2005_harmonization_value_decision_required_blocked_rows']}",
        [TEMP_DIR / "alb2005_harmonization_value_decision_audit.csv", RESULT_DIR / "alb2005_harmonization_value_decision_summary.csv", REPORT_DIR / "alb2005_harmonization_value_decision_audit.md"],
        "" if counts["alb2005_harmonization_value_decision_audit"] > 0 and counts["alb2005_harmonization_value_decision_recipe_ready_rows"] == 0 and counts["alb2005_harmonization_value_decision_required_blocked_rows"] > 0 else "run script/68_build_alb2005_harmonization_value_decision_audit.py and keep ALB_2005 value decisions non-promotional",
    )
    add(
        "cross_phase_alb2005_minimum_recipe_promotion_packet",
        "phase3",
        "Map the raw-ready ALB_2005 temp candidate to explicit harmonization, outcome, and climate promotion gates before any analysis-ready data promotion.",
        status_done(
            counts["alb2005_minimum_recipe_promotion_action_rows"] > 0
            and counts["alb2005_minimum_recipe_promotion_gate_rows"] > 0
            and counts["alb2005_minimum_recipe_promotion_summary_rows"] > 0
            and counts["alb2005_minimum_recipe_promotion_blocked_gates"] > 0
            and counts["alb2005_minimum_recipe_promotion_harmonized_ready_rows"] == 0
            and counts["alb2005_minimum_recipe_promotion_outcome_ready_rows"] == 0
            and counts["alb2005_minimum_recipe_promotion_climate_linkage_ready_rows"] == 0
        ),
        f"action rows={counts['alb2005_minimum_recipe_promotion_action_rows']}; gate rows={counts['alb2005_minimum_recipe_promotion_gate_rows']}; blocked gates={counts['alb2005_minimum_recipe_promotion_blocked_gates']}; candidate gates={counts['alb2005_minimum_recipe_promotion_candidate_gates']}; harmonized-ready rows={counts['alb2005_minimum_recipe_promotion_harmonized_ready_rows']}; outcome-ready rows={counts['alb2005_minimum_recipe_promotion_outcome_ready_rows']}; climate-linkage-ready rows={counts['alb2005_minimum_recipe_promotion_climate_linkage_ready_rows']}; decision={counts['alb2005_minimum_recipe_promotion_current_decision']}",
        [TEMP_DIR / "alb2005_minimum_recipe_promotion_action_queue.csv", TEMP_DIR / "alb2005_minimum_recipe_promotion_gate_checklist.csv", RESULT_DIR / "alb2005_minimum_recipe_promotion_summary.csv", REPORT_DIR / "alb2005_minimum_recipe_promotion_packet.md"],
        "" if counts["alb2005_minimum_recipe_promotion_action_rows"] > 0 and counts["alb2005_minimum_recipe_promotion_harmonized_ready_rows"] == 0 and counts["alb2005_minimum_recipe_promotion_outcome_ready_rows"] == 0 and counts["alb2005_minimum_recipe_promotion_climate_linkage_ready_rows"] == 0 else "run script/83_build_alb2005_minimum_recipe_promotion_packet.py and keep ALB_2005 temp-only until minimum recipe gates pass",
    )
    add(
        "cross_phase_alb2005_public_fieldwork_geo_metadata_audit",
        "phase5",
        "Verify ALB_2005 public fieldwork/GPS/geography metadata while keeping household timing, coordinates, and climate linkage blocked until raw values pass.",
        status_done(
            counts["alb2005_public_fieldwork_geo_metadata_audit"] > 0
            and counts["alb2005_public_fieldwork_geo_metadata_summary"] > 0
            and counts["alb2005_public_fieldwork_geo_metadata_evidence_rows"] == 10
            and counts["alb2005_public_fieldwork_geo_metadata_verified_source_rows"] == 10
            and counts["alb2005_public_fieldwork_geo_metadata_source_missing_rows"] == 0
            and counts["alb2005_public_fieldwork_geo_metadata_household_timing_verified_rows"] == 0
            and counts["alb2005_public_fieldwork_geo_metadata_raw_coordinate_value_rows"] == 0
            and counts["alb2005_public_fieldwork_geo_metadata_climate_linkage_ready_rows"] == 0
        ),
        f"audit rows={counts['alb2005_public_fieldwork_geo_metadata_audit']}; summary rows={counts['alb2005_public_fieldwork_geo_metadata_summary']}; evidence rows={counts['alb2005_public_fieldwork_geo_metadata_evidence_rows']}; verified source rows={counts['alb2005_public_fieldwork_geo_metadata_verified_source_rows']}; missing source rows={counts['alb2005_public_fieldwork_geo_metadata_source_missing_rows']}; fieldwork rows={counts['alb2005_public_fieldwork_geo_metadata_fieldwork_period_evidence_rows']}; GPS claim rows={counts['alb2005_public_fieldwork_geo_metadata_gps_claim_rows']}; sampling geography rows={counts['alb2005_public_fieldwork_geo_metadata_sampling_geo_rows']}; household timing rows={counts['alb2005_public_fieldwork_geo_metadata_household_timing_verified_rows']}; raw coordinate rows={counts['alb2005_public_fieldwork_geo_metadata_raw_coordinate_value_rows']}; climate-linkage rows={counts['alb2005_public_fieldwork_geo_metadata_climate_linkage_ready_rows']}; decision={counts['alb2005_public_fieldwork_geo_metadata_current_decision']}",
        [TEMP_DIR / "alb2005_public_fieldwork_geo_metadata_audit.csv", RESULT_DIR / "alb2005_public_fieldwork_geo_metadata_summary.csv", REPORT_DIR / "alb2005_public_fieldwork_geo_metadata_audit.md"],
        "" if counts["alb2005_public_fieldwork_geo_metadata_verified_source_rows"] == 10 and counts["alb2005_public_fieldwork_geo_metadata_household_timing_verified_rows"] == 0 and counts["alb2005_public_fieldwork_geo_metadata_raw_coordinate_value_rows"] == 0 and counts["alb2005_public_fieldwork_geo_metadata_climate_linkage_ready_rows"] == 0 else "run script/84_audit_alb2005_public_fieldwork_geo_metadata.py and keep public metadata claims separate from climate-linkage promotion",
    )
    add(
        "cross_phase_alb2005_diary_timing_candidate_audit",
        "phase5",
        "Identify ALB_2005 bookmetadata diary beginning/finishing date candidates while blocking household timing promotion until raw values, merge coverage, and semantics pass.",
        status_done(
            counts["alb2005_diary_timing_candidate_audit"] > 0
            and counts["alb2005_diary_timing_candidate_summary"] > 0
            and counts["alb2005_diary_timing_candidate_audit_rows"] == 11
            and counts["alb2005_diary_timing_candidate_metadata_found_rows"] == 11
            and counts["alb2005_diary_timing_candidate_schema_file_rows"] > 0
            and counts["alb2005_diary_timing_candidate_raw_bookmetadata_files_present"] == 0
            and counts["alb2005_diary_timing_candidate_date_candidate_rows"] > 0
            and counts["alb2005_diary_timing_candidate_household_timing_promoted_rows"] == 0
            and counts["alb2005_diary_timing_candidate_climate_linkage_ready_rows"] == 0
        ),
        f"audit rows={counts['alb2005_diary_timing_candidate_audit']}; summary rows={counts['alb2005_diary_timing_candidate_summary']}; candidate rows={counts['alb2005_diary_timing_candidate_audit_rows']}; metadata found rows={counts['alb2005_diary_timing_candidate_metadata_found_rows']}; schema file rows={counts['alb2005_diary_timing_candidate_schema_file_rows']}; raw bookmetadata present={counts['alb2005_diary_timing_candidate_raw_bookmetadata_files_present']}; key candidate rows={counts['alb2005_diary_timing_candidate_key_candidate_rows']}; date candidate rows={counts['alb2005_diary_timing_candidate_date_candidate_rows']}; household timing promoted rows={counts['alb2005_diary_timing_candidate_household_timing_promoted_rows']}; climate-linkage rows={counts['alb2005_diary_timing_candidate_climate_linkage_ready_rows']}; decision={counts['alb2005_diary_timing_candidate_current_decision']}",
        [TEMP_DIR / "alb2005_diary_timing_candidate_audit.csv", RESULT_DIR / "alb2005_diary_timing_candidate_summary.csv", REPORT_DIR / "alb2005_diary_timing_candidate_audit.md"],
        "" if counts["alb2005_diary_timing_candidate_audit_rows"] == 11 and counts["alb2005_diary_timing_candidate_raw_bookmetadata_files_present"] == 0 and counts["alb2005_diary_timing_candidate_household_timing_promoted_rows"] == 0 and counts["alb2005_diary_timing_candidate_climate_linkage_ready_rows"] == 0 else "run script/85_audit_alb2005_diary_timing_candidates.py and keep bookmetadata timing candidates out of climate linkage until raw merge semantics pass",
    )
    add(
        "cross_phase_alb2005_extracted_module_coverage_audit",
        "phase2",
        "Compare ALB_2005 DDI modules to the local archive manifest and extracted package and document missing timing, food diary, design, and coordinate evidence before harmonization or climate linkage.",
        status_done(
            counts["alb2005_extracted_module_coverage_audit"] > 0
            and counts["alb2005_extracted_extra_files_audit"] > 0
            and counts["alb2005_archive_member_manifest"] > 0
            and counts["alb2005_extracted_module_coverage_summary"] > 0
            and counts["alb2005_extracted_module_coverage_ddi_module_rows"] == 68
            and counts["alb2005_archive_member_rows"] == 61
            and counts["alb2005_archive_sav_member_rows"] == 44
            and counts["alb2005_archive_questionnaire_member_rows"] == 2
            and counts["alb2005_archive_ddi_module_present_rows"] > 0
            and counts["alb2005_archive_ddi_module_absent_rows"] > 0
            and counts["alb2005_archive_critical_module_absent_rows"] > 0
            and counts["alb2005_archive_listing_status"] == "tar_listing_available"
            and counts["alb2005_extracted_module_coverage_present_rows"] > 0
            and counts["alb2005_extracted_module_coverage_missing_rows"] > 0
            and counts["alb2005_extracted_module_coverage_bookmetadata_missing_rows"] == 1
            and counts["alb2005_extracted_module_coverage_critical_missing_rows"] > 0
            and counts["alb2005_extracted_module_coverage_coordinate_metadata_variable_rows"] == 0
            and counts["alb2005_extracted_module_coverage_coordinate_extracted_file_rows"] == 0
            and counts["alb2005_extracted_module_coverage_harmonized_ready_rows"] == 0
            and counts["alb2005_extracted_module_coverage_household_timing_ready_rows"] == 0
            and counts["alb2005_extracted_module_coverage_climate_linkage_ready_rows"] == 0
        ),
        f"audit rows={counts['alb2005_extracted_module_coverage_audit']}; extra rows={counts['alb2005_extracted_extra_files_audit']}; archive manifest rows={counts['alb2005_archive_member_manifest']}; summary rows={counts['alb2005_extracted_module_coverage_summary']}; DDI modules={counts['alb2005_extracted_module_coverage_ddi_module_rows']}; archive members={counts['alb2005_archive_member_rows']}; archive sav files={counts['alb2005_archive_sav_member_rows']}; archive questionnaires={counts['alb2005_archive_questionnaire_member_rows']}; archive DDI present rows={counts['alb2005_archive_ddi_module_present_rows']}; archive DDI absent rows={counts['alb2005_archive_ddi_module_absent_rows']}; archive critical absent rows={counts['alb2005_archive_critical_module_absent_rows']}; archive listing status={counts['alb2005_archive_listing_status']}; present rows={counts['alb2005_extracted_module_coverage_present_rows']}; missing rows={counts['alb2005_extracted_module_coverage_missing_rows']}; extracted files={counts['alb2005_extracted_module_coverage_extracted_file_rows']}; bookmetadata missing rows={counts['alb2005_extracted_module_coverage_bookmetadata_missing_rows']}; food diary missing rows={counts['alb2005_extracted_module_coverage_food_diary_missing_rows']}; critical missing rows={counts['alb2005_extracted_module_coverage_critical_missing_rows']}; coordinate metadata variables={counts['alb2005_extracted_module_coverage_coordinate_metadata_variable_rows']}; coordinate extracted files={counts['alb2005_extracted_module_coverage_coordinate_extracted_file_rows']}; harmonized-ready rows={counts['alb2005_extracted_module_coverage_harmonized_ready_rows']}; household timing rows={counts['alb2005_extracted_module_coverage_household_timing_ready_rows']}; climate-linkage rows={counts['alb2005_extracted_module_coverage_climate_linkage_ready_rows']}; decision={counts['alb2005_extracted_module_coverage_current_decision']}",
        [TEMP_DIR / "alb2005_extracted_module_coverage_audit.csv", TEMP_DIR / "alb2005_extracted_extra_files_audit.csv", TEMP_DIR / "alb2005_archive_member_manifest.csv", RESULT_DIR / "alb2005_extracted_module_coverage_summary.csv", REPORT_DIR / "alb2005_extracted_module_coverage_audit.md"],
        "" if counts["alb2005_extracted_module_coverage_ddi_module_rows"] == 68 and counts["alb2005_archive_member_rows"] == 61 and counts["alb2005_archive_sav_member_rows"] == 44 and counts["alb2005_archive_listing_status"] == "tar_listing_available" and counts["alb2005_extracted_module_coverage_bookmetadata_missing_rows"] == 1 and counts["alb2005_extracted_module_coverage_coordinate_metadata_variable_rows"] == 0 and counts["alb2005_extracted_module_coverage_coordinate_extracted_file_rows"] == 0 and counts["alb2005_extracted_module_coverage_harmonized_ready_rows"] == 0 and counts["alb2005_extracted_module_coverage_household_timing_ready_rows"] == 0 and counts["alb2005_extracted_module_coverage_climate_linkage_ready_rows"] == 0 else "run script/86_audit_alb2005_extracted_module_coverage.py and keep ALB_2005 out of harmonized/climate data until missing modules or official substitutes pass review",
    )
    add(
        "cross_phase_alb2005_fallback_blocker_resolution_matrix",
        "phase3_phase5",
        "Consolidate ALB_2005 source-package, timing, geography, outcome, and first-analysis fallback blockers before substituting it for ALB_2002.",
        status_done(
            counts["alb2005_fallback_blocker_resolution_matrix"] == 12
            and counts["alb2005_fallback_blocker_resolution_summary"] == 14
            and counts["alb2005_fallback_blocker_resolution_rows"] == 12
            and counts["alb2005_fallback_blocker_raw_package_rows"] == 1
            and counts["alb2005_fallback_blocker_timing_rows"] == 3
            and counts["alb2005_fallback_blocker_geography_rows"] == 2
            and counts["alb2005_fallback_blocker_outcome_rows"] == 3
            and counts["alb2005_fallback_blocker_promotion_gate_rows"] == 3
            and counts["alb2005_fallback_blocker_hard_blocked_rows"] == 12
            and counts["alb2005_fallback_blocker_harmonized_ready_rows"] == 0
            and counts["alb2005_fallback_blocker_outcome_ready_rows"] == 0
            and counts["alb2005_fallback_blocker_interview_timing_ready_rows"] == 0
            and counts["alb2005_fallback_blocker_geography_ready_rows"] == 0
            and counts["alb2005_fallback_blocker_climate_linkage_ready_rows"] == 0
            and counts["alb2005_fallback_blocker_data_write_ready_rows"] == 0
            and counts["alb2005_fallback_blocker_current_decision"] == "blocked_alb2005_no_fallback_ready"
        ),
        f"matrix rows={counts['alb2005_fallback_blocker_resolution_matrix']}; summary rows={counts['alb2005_fallback_blocker_resolution_summary']}; raw-package rows={counts['alb2005_fallback_blocker_raw_package_rows']}; timing rows={counts['alb2005_fallback_blocker_timing_rows']}; geography rows={counts['alb2005_fallback_blocker_geography_rows']}; outcome rows={counts['alb2005_fallback_blocker_outcome_rows']}; promotion-gate rows={counts['alb2005_fallback_blocker_promotion_gate_rows']}; hard-blocked rows={counts['alb2005_fallback_blocker_hard_blocked_rows']}; harmonized-ready rows={counts['alb2005_fallback_blocker_harmonized_ready_rows']}; outcome-ready rows={counts['alb2005_fallback_blocker_outcome_ready_rows']}; interview-timing-ready rows={counts['alb2005_fallback_blocker_interview_timing_ready_rows']}; geography-ready rows={counts['alb2005_fallback_blocker_geography_ready_rows']}; climate-linkage-ready rows={counts['alb2005_fallback_blocker_climate_linkage_ready_rows']}; data-write-ready rows={counts['alb2005_fallback_blocker_data_write_ready_rows']}; decision={counts['alb2005_fallback_blocker_current_decision']}",
        [TEMP_DIR / "alb2005_fallback_blocker_resolution_matrix.csv", RESULT_DIR / "alb2005_fallback_blocker_resolution_summary.csv", REPORT_DIR / "alb2005_fallback_blocker_resolution_matrix.md"],
        "" if counts["alb2005_fallback_blocker_harmonized_ready_rows"] == 0 and counts["alb2005_fallback_blocker_outcome_ready_rows"] == 0 and counts["alb2005_fallback_blocker_climate_linkage_ready_rows"] == 0 and counts["alb2005_fallback_blocker_data_write_ready_rows"] == 0 else "rerun script/115_build_alb2005_fallback_blocker_resolution_matrix.py and keep ALB_2005 fallback promotion closed until source, timing, geography, and outcome gates pass",
    )
    add(
        "cross_phase_albania_first_analysis_promotion_gate",
        "phase3",
        "Rank local Albania raw waves for the first possible harmonized, outcome-audited, climate-linked analytical dataset while keeping data promotion blocked until all gates pass.",
        status_done(
            counts["albania_first_analysis_promotion_gate_checklist"] > 0
            and counts["albania_first_analysis_promotion_action_queue"] > 0
            and counts["albania_first_analysis_promotion_wave_ranking"] > 0
            and counts["albania_first_analysis_promotion_summary"] > 0
            and counts["albania_first_analysis_promotion_wave_rows"] == 4
            and counts["albania_first_analysis_promotion_gate_rows"] > 0
            and counts["albania_first_analysis_promotion_blocked_gate_rows"] > 0
            and counts["albania_first_analysis_promotion_ready_wave_rows"] == 0
            and counts["albania_first_analysis_promotion_harmonized_ready_rows"] == 0
            and counts["albania_first_analysis_promotion_outcome_ready_rows"] == 0
            and counts["albania_first_analysis_promotion_climate_linkage_ready_rows"] == 0
        ),
        f"wave rows={counts['albania_first_analysis_promotion_wave_rows']}; gate rows={counts['albania_first_analysis_promotion_gate_rows']}; blocked gates={counts['albania_first_analysis_promotion_blocked_gate_rows']}; ready waves={counts['albania_first_analysis_promotion_ready_wave_rows']}; harmonized-ready rows={counts['albania_first_analysis_promotion_harmonized_ready_rows']}; outcome-ready rows={counts['albania_first_analysis_promotion_outcome_ready_rows']}; climate-linkage-ready rows={counts['albania_first_analysis_promotion_climate_linkage_ready_rows']}; decision={counts['albania_first_analysis_promotion_current_decision']}",
        [TEMP_DIR / "albania_first_analysis_promotion_gate_checklist.csv", TEMP_DIR / "albania_first_analysis_promotion_action_queue.csv", RESULT_DIR / "albania_first_analysis_promotion_wave_ranking.csv", RESULT_DIR / "albania_first_analysis_promotion_summary.csv", REPORT_DIR / "albania_first_analysis_promotion_gate.md"],
        "" if counts["albania_first_analysis_promotion_wave_rows"] == 4 and counts["albania_first_analysis_promotion_ready_wave_rows"] == 0 and counts["albania_first_analysis_promotion_harmonized_ready_rows"] == 0 and counts["albania_first_analysis_promotion_outcome_ready_rows"] == 0 and counts["albania_first_analysis_promotion_climate_linkage_ready_rows"] == 0 else "run script/87_build_albania_first_analysis_promotion_gate.py and keep data promotion blocked until one wave passes harmonization, outcome, and climate-linkage gates",
    )
    add(
        "cross_phase_albania_existing_raw_wave_audit",
        "phase2",
        "Identify already-present Albania raw waves beyond ALB_2005 and keep them queued for wave-specific schema/value/key/timing audits before harmonization.",
        status_done(
            counts["albania_existing_raw_wave_audit"] > 0
            and counts["albania_existing_raw_wave_audit_summary"] > 0
            and counts["albania_existing_raw_wave_harmonization_ready_rows"] == 0
            and counts["albania_existing_raw_wave_climate_linkage_ready_rows"] == 0
        ),
        f"audit rows={counts['albania_existing_raw_wave_audit']}; summary rows={counts['albania_existing_raw_wave_audit_summary']}; harmonization-ready rows={counts['albania_existing_raw_wave_harmonization_ready_rows']}; climate-linkage-ready rows={counts['albania_existing_raw_wave_climate_linkage_ready_rows']}",
        [TEMP_DIR / "albania_existing_raw_wave_audit.csv", RESULT_DIR / "albania_existing_raw_wave_audit_summary.csv", REPORT_DIR / "albania_existing_raw_wave_audit.md"],
        "" if counts["albania_existing_raw_wave_audit"] > 0 and counts["albania_existing_raw_wave_harmonization_ready_rows"] == 0 and counts["albania_existing_raw_wave_climate_linkage_ready_rows"] == 0 else "run script/50_audit_existing_albania_raw_waves.py and keep waves blocked until wave-specific audits pass",
    )
    add(
        "cross_phase_alb2008_household_core_merge_audit",
        "phase3",
        "Build a temp-only ALB_2008 household core candidate after merge-key coverage is audited, and keep it out of data until recipe gates pass.",
        status_done(
            counts["alb2008_household_core_candidate"] > 0
            and counts["alb2008_household_core_merge_audit"] > 0
            and counts["alb2008_household_core_lineage"] > 0
            and counts["alb2008_household_core_candidate_summary"] > 0
            and counts["alb2008_household_core_recipe_ready_rows"] == 0
        ),
        f"candidate rows={counts['alb2008_household_core_candidate']}; merge audit rows={counts['alb2008_household_core_merge_audit']}; lineage rows={counts['alb2008_household_core_lineage']}; summary rows={counts['alb2008_household_core_candidate_summary']}; recipe-ready rows={counts['alb2008_household_core_recipe_ready_rows']}",
        [TEMP_DIR / "alb2008_household_core_candidate.csv", TEMP_DIR / "alb2008_household_core_merge_audit.csv", TEMP_DIR / "alb2008_household_core_lineage.csv", RESULT_DIR / "alb2008_household_core_candidate_summary.csv", REPORT_DIR / "alb2008_household_core_merge_audit.md"],
        "" if counts["alb2008_household_core_candidate"] > 0 and counts["alb2008_household_core_recipe_ready_rows"] == 0 else "run script/51_audit_alb2008_household_core_merge.py and keep the output temp-only",
    )
    add(
        "cross_phase_alb2008_provisional_outcome_feasibility",
        "phase4",
        "Compute ALB_2008 provisional outcome event-rate diagnostics only after raw household-core assembly, and keep all final outcome promotion blocked.",
        status_done(
            counts["alb2008_provisional_outcome_feasibility_audit"] > 0
            and counts["alb2008_provisional_outcome_feasibility_summary"] > 0
            and counts["alb2008_provisional_outcome_ready_rows"] == 0
        ),
        f"audit rows={counts['alb2008_provisional_outcome_feasibility_audit']}; summary rows={counts['alb2008_provisional_outcome_feasibility_summary']}; ready rows={counts['alb2008_provisional_outcome_ready_rows']}",
        [TEMP_DIR / "alb2008_provisional_outcome_feasibility_audit.csv", RESULT_DIR / "alb2008_provisional_outcome_feasibility_summary.csv", REPORT_DIR / "alb2008_provisional_outcome_feasibility.md"],
        "" if counts["alb2008_provisional_outcome_feasibility_audit"] > 0 and counts["alb2008_provisional_outcome_ready_rows"] == 0 else "run script/52_audit_alb2008_provisional_outcome_feasibility.py and keep provisional outcome promotion blocked",
    )
    add(
        "cross_phase_alb2008_outcome_semantics_raw_value_audit",
        "phase4",
        "Audit ALB_2008 raw payment, gift, access, need, coping, and service-quality labels/values before any outcome or SDG 3.8.2 promotion.",
        status_done(
            counts["alb2008_outcome_semantics_raw_value_audit"] > 0
            and counts["alb2008_outcome_semantics_raw_value_summary"] > 0
            and counts["alb2008_outcome_semantics_outcome_ready_rows"] == 0
            and counts["alb2008_outcome_semantics_sdg382_ready_rows"] == 0
            and counts["alb2008_outcome_semantics_climate_linkage_ready_rows"] == 0
        ),
        f"audit rows={counts['alb2008_outcome_semantics_raw_value_audit']}; summary rows={counts['alb2008_outcome_semantics_raw_value_summary']}; OOP candidates={counts['alb2008_outcome_semantics_financial_oop_candidate_rows']}; gift candidates={counts['alb2008_outcome_semantics_gift_candidate_rows']}; access candidates={counts['alb2008_outcome_semantics_access_candidate_rows']}; facility/service proxy rows={counts['alb2008_outcome_semantics_facility_proxy_rows']}; conditional reason rows={counts['alb2008_outcome_semantics_conditional_reason_rows']}; outcome-ready rows={counts['alb2008_outcome_semantics_outcome_ready_rows']}; SDG 3.8.2-ready rows={counts['alb2008_outcome_semantics_sdg382_ready_rows']}; climate-linkage-ready rows={counts['alb2008_outcome_semantics_climate_linkage_ready_rows']}",
        [TEMP_DIR / "alb2008_outcome_semantics_raw_value_audit.csv", RESULT_DIR / "alb2008_outcome_semantics_raw_value_summary.csv", REPORT_DIR / "alb2008_outcome_semantics_raw_value_audit.md"],
        "" if counts["alb2008_outcome_semantics_raw_value_audit"] > 0 and counts["alb2008_outcome_semantics_outcome_ready_rows"] == 0 and counts["alb2008_outcome_semantics_sdg382_ready_rows"] == 0 and counts["alb2008_outcome_semantics_climate_linkage_ready_rows"] == 0 else "run script/62_audit_alb2008_outcome_semantics_raw_values.py and keep ALB_2008 outcome, SDG 3.8.2, and climate-linkage promotion blocked",
    )
    add(
        "cross_phase_alb2008_timing_geography_exhaustive_audit",
        "phase5",
        "Exhaustively scan ALB_2008 raw timing/geography candidates before constructing climate-linkage inputs, and keep linkage blocked until interview timing and geography are verified.",
        status_done(
            counts["alb2008_timing_geography_exhaustive_audit"] > 0
            and counts["alb2008_timing_geography_exhaustive_summary"] > 0
            and counts["alb2008_climate_linkage_ready_rows"] == 0
        ),
        f"audit rows={counts['alb2008_timing_geography_exhaustive_audit']}; summary rows={counts['alb2008_timing_geography_exhaustive_summary']}; climate-linkage-ready rows={counts['alb2008_climate_linkage_ready_rows']}",
        [TEMP_DIR / "alb2008_timing_geography_exhaustive_audit.csv", RESULT_DIR / "alb2008_timing_geography_exhaustive_summary.csv", REPORT_DIR / "alb2008_timing_geography_exhaustive_audit.md"],
        "" if counts["alb2008_timing_geography_exhaustive_audit"] > 0 and counts["alb2008_climate_linkage_ready_rows"] == 0 else "run script/53_audit_alb2008_timing_geography_exhaustive.py and keep climate linkage blocked",
    )
    add(
        "cross_phase_alb2008_fallback_blocker_resolution_matrix",
        "phase5",
        "Consolidate ALB_2008 fallback timing, geography, outcome, and promotion blockers into one fail-closed matrix before any fallback analysis promotion.",
        status_done(
            counts["alb2008_fallback_blocker_resolution_matrix"] == 10
            and counts["alb2008_fallback_blocker_resolution_summary"] == 12
            and counts["alb2008_fallback_blocker_resolution_rows"] == 10
            and counts["alb2008_fallback_blocker_timing_rows"] == 3
            and counts["alb2008_fallback_blocker_geography_rows"] == 3
            and counts["alb2008_fallback_blocker_outcome_rows"] == 2
            and counts["alb2008_fallback_blocker_promotion_gate_rows"] == 2
            and counts["alb2008_fallback_blocker_hard_blocked_rows"] == 10
            and counts["alb2008_fallback_blocker_interview_timing_ready_rows"] == 0
            and counts["alb2008_fallback_blocker_geography_ready_rows"] == 0
            and counts["alb2008_fallback_blocker_outcome_ready_rows"] == 0
            and counts["alb2008_fallback_blocker_climate_linkage_ready_rows"] == 0
            and counts["alb2008_fallback_blocker_data_write_ready_rows"] == 0
            and counts["alb2008_fallback_blocker_current_decision"] == "blocked_alb2008_no_timing_geography_fallback_ready"
        ),
        f"matrix rows={counts['alb2008_fallback_blocker_resolution_matrix']}; summary rows={counts['alb2008_fallback_blocker_resolution_summary']}; timing={counts['alb2008_fallback_blocker_timing_rows']}; geography={counts['alb2008_fallback_blocker_geography_rows']}; outcome={counts['alb2008_fallback_blocker_outcome_rows']}; promotion_gate={counts['alb2008_fallback_blocker_promotion_gate_rows']}; hard-blocked rows={counts['alb2008_fallback_blocker_hard_blocked_rows']}; timing-ready rows={counts['alb2008_fallback_blocker_interview_timing_ready_rows']}; geography-ready rows={counts['alb2008_fallback_blocker_geography_ready_rows']}; outcome-ready rows={counts['alb2008_fallback_blocker_outcome_ready_rows']}; climate-linkage-ready rows={counts['alb2008_fallback_blocker_climate_linkage_ready_rows']}; data-write-ready rows={counts['alb2008_fallback_blocker_data_write_ready_rows']}; decision={counts['alb2008_fallback_blocker_current_decision']}",
        [TEMP_DIR / "alb2008_fallback_blocker_resolution_matrix.csv", RESULT_DIR / "alb2008_fallback_blocker_resolution_summary.csv", REPORT_DIR / "alb2008_fallback_blocker_resolution_matrix.md"],
        "" if counts["alb2008_fallback_blocker_resolution_matrix"] == 10 and counts["alb2008_fallback_blocker_hard_blocked_rows"] == 10 and counts["alb2008_fallback_blocker_climate_linkage_ready_rows"] == 0 and counts["alb2008_fallback_blocker_data_write_ready_rows"] == 0 else "run script/116_build_alb2008_fallback_blocker_resolution_matrix.py and keep ALB_2008 fallback promotion blocked",
    )
    add(
        "cross_phase_first_batch_raw_verification_workbook",
        "phase3",
        "Provide post-download raw evidence templates for concept and variable verification before harmonization recipe promotion.",
        status_done(
            counts["first_batch_dataset_verification_gate"] > 0
            and counts["first_batch_concept_verification_template"] > 0
            and counts["first_batch_variable_verification_template"] > 0
            and counts["first_batch_raw_verification_workbook_summary"] > 0
        ),
        f"dataset gate rows={counts['first_batch_dataset_verification_gate']}; concept template rows={counts['first_batch_concept_verification_template']}; variable template rows={counts['first_batch_variable_verification_template']}; summary rows={counts['first_batch_raw_verification_workbook_summary']}; datasets ready for value audit={counts['first_batch_datasets_ready_for_value_audit']}",
        [RESULT_DIR / "first_batch_dataset_verification_gate.csv", TEMP_DIR / "first_batch_concept_verification_template.csv", TEMP_DIR / "first_batch_variable_verification_template.csv", RESULT_DIR / "first_batch_raw_verification_workbook_summary.csv", REPORT_DIR / "first_batch_raw_verification_workbook.md"],
        "" if counts["first_batch_dataset_verification_gate"] > 0 else "run script/38_build_first_batch_raw_verification_workbook.py after first-batch raw acquisition checklist generation",
    )
    add(
        "cross_phase_direct_read_audit_bundle",
        "phase14",
        "Provide one compact direct-read audit index of current gates, no-go status, completion gaps, and curated artifact evidence.",
        status_done(counts["direct_read_bundle"] > 0 and counts["direct_read_manifest"] > 0 and counts["direct_read_summary"] > 0),
        f"bundle rows={counts['direct_read_bundle']}; manifest rows={counts['direct_read_manifest']}; summary rows={counts['direct_read_summary']}; manifest present={counts['direct_read_manifest_present']}; manifest missing={counts['direct_read_manifest_missing']}",
        [RESULT_DIR / "direct_read_audit_bundle.csv", RESULT_DIR / "direct_read_artifact_manifest.csv", RESULT_DIR / "direct_read_audit_bundle_summary.csv", REPORT_DIR / "direct_read_audit_bundle.md"],
        "" if counts["direct_read_bundle"] > 0 else "run script/36_build_direct_read_audit_bundle.py after empirical readiness dashboard generation",
    )
    add(
        "phase14_reporting",
        "phase14",
        "Write final report with empirical judgment, limitations, and next steps without overclaiming.",
        status_done(file_ok(REPORT_DIR / "final_report.md") and "No go for outcome construction" in text(REPORT_DIR / "final_report.md")),
        f"final_report exists={file_ok(REPORT_DIR / 'final_report.md')}; completion complete={counts['completion_complete']}; completion incomplete={counts['completion_incomplete']}",
        [REPORT_DIR / "final_report.md", RESULT_DIR / "completion_criteria_audit.csv"],
    )
    add(
        "reproducibility",
        "reproducibility",
        "Provide one-command reproduction through Makefile or run_all scripts, except documented manual downloads.",
        status_done(file_ok(TEMP_DIR.parent / "Makefile") and file_ok(SCRIPT_DIR / "run_all.sh") and file_ok(SCRIPT_DIR / "run_all.ps1")),
        f"Makefile exists={file_ok(TEMP_DIR.parent / 'Makefile')}; run_all.sh exists={file_ok(SCRIPT_DIR / 'run_all.sh')}; run_all.ps1 exists={file_ok(SCRIPT_DIR / 'run_all.ps1')}",
        [TEMP_DIR.parent / "Makefile", SCRIPT_DIR / "run_all.sh", SCRIPT_DIR / "run_all.ps1"],
    )
    add(
        "reproducibility_environment",
        "reproducibility",
        "Record Python runtime and package availability for the reproducible pipeline.",
        status_done(counts["python_package_inventory"] > 0 and counts["python_environment_audit"] > 0 and counts["python_environment_summary"] > 0),
        f"package inventory rows={counts['python_package_inventory']}; environment audit rows={counts['python_environment_audit']}; incomplete environment checks={counts['python_environment_incomplete']}",
        [TEMP_DIR / "python_package_inventory.csv", TEMP_DIR / "python_package_freeze.txt", RESULT_DIR / "python_environment_audit.csv", RESULT_DIR / "python_environment_summary.csv", REPORT_DIR / "reproducibility_environment.md"],
        "" if counts["python_environment_audit"] > 0 else "run script/28_audit_python_environment.py",
    )
    return rows


def build_guardrail_rows(counts: dict[str, int]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []

    def add(guardrail_id: str, guardrail: str, status: str, evidence: str, artifacts: list[Path], gap: str = "") -> None:
        rows.append(
            {
                "guardrail_id": guardrail_id,
                "guardrail": guardrail,
                "status": status,
                "evidence": evidence,
                "evidence_artifacts": artifact_list(artifacts),
                "gap": gap,
            }
        )

    raw_in_data = [path for path in DATA_DIR.rglob("*") if path.is_file() and path.suffix.lower() in RAW_EXTENSIONS]
    messy_report_files = [path for path in REPORT_DIR.rglob("*") if path.is_file() and path.suffix.lower() in MESSY_REPORT_EXTENSIONS]
    harmonized_exists = exists_any([DATA_DIR / "harmonized_household.csv", DATA_DIR / "harmonized_household.parquet"])
    climate_exposure_exists = exists_any([DATA_DIR / "climate_exposures_nasa_power.csv"])
    outcomes_exists = exists_any([DATA_DIR / "household_outcomes.csv", DATA_DIR / "household_outcomes.parquet"])
    linked_exists = exists_any([DATA_DIR / "climate_linked_household.csv", DATA_DIR / "climate_linked_household.parquet"])
    limited_harmonized_ok = harmonized_exists and counts["limited_harmonized_core_marker"] == 1
    limited_climate_ok = climate_exposure_exists and counts["limited_climate_exposure_marker"] == 1
    limited_outcome_ok = outcomes_exists and counts["limited_household_outcome_marker"] == 1
    limited_linked_ok = linked_exists and counts["limited_climate_linked_marker"] == 1
    final_report_text = text(REPORT_DIR / "final_report.md").lower()
    modeling_report_text = text(REPORT_DIR / "modeling_report.md").lower()
    rejected_text = text(TEMP_DIR / "rejected_designs.md").lower()

    add(
        "no_raw_in_data",
        "Do not put raw files in data/.",
        status_done(len(raw_in_data) == 0),
        f"raw-like files in data={len(raw_in_data)}",
        raw_in_data[:10] or [DATA_DIR],
        "" if not raw_in_data else "move raw-like files to temp/raw_downloads or remove unsupported artifacts",
    )
    add(
        "no_messy_report_files",
        "Do not put machine-readable logs or tables in report/.",
        status_done(len(messy_report_files) == 0),
        f"messy report files={len(messy_report_files)}",
        messy_report_files[:10] or [REPORT_DIR],
        "" if not messy_report_files else "move CSV/log/tmp/json files to temp or result",
    )
    add(
        "no_false_analysis_ready_data",
        "Do not create outcome-ready or climate-linked datasets while upstream gates are blocked; limited core/outcome/exposure/linked files must stay marked as non-final.",
        status_done((not linked_exists or limited_linked_ok) and (not harmonized_exists or limited_harmonized_ok) and (not climate_exposure_exists or limited_climate_ok) and (not outcomes_exists or limited_outcome_ok)),
        f"harmonized={harmonized_exists}; limited_harmonized_ok={limited_harmonized_ok}; climate_exposure={climate_exposure_exists}; limited_climate_ok={limited_climate_ok}; outcomes={outcomes_exists}; limited_outcome_ok={limited_outcome_ok}; climate_linked={linked_exists}; limited_linked_ok={limited_linked_ok}; raw files={counts['raw_files']}",
        [DATA_DIR / "harmonized_household.csv", DATA_DIR / "climate_exposures_nasa_power.csv", DATA_DIR / "household_outcomes.csv", DATA_DIR / "climate_linked_household.csv"],
        "" if (not linked_exists or limited_linked_ok) and (not harmonized_exists or limited_harmonized_ok) and (not climate_exposure_exists or limited_climate_ok) and (not outcomes_exists or limited_outcome_ok) else "remove false outcome/climate data outputs or restore limited guardrail markers",
    )
    add(
        "no_causal_overclaim",
        "Do not call climate estimates causal unless placebo, seasonality, geography, and timing checks support the design.",
        status_done("no go for sdg 3.8.2" in final_report_text and "climate linkage" in final_report_text and "predictive ml" in final_report_text),
        "final report preserves no-go language for SDG/access/climate/modeling",
        [REPORT_DIR / "final_report.md", REPORT_DIR / "identification_audit.md"],
        "" if "no go for sdg 3.8.2" in final_report_text and "climate linkage" in final_report_text else "regenerate reports with no-go language",
    )
    add(
        "causal_ml_after_identification",
        "Do not use causal ML to compensate for weak identification.",
        status_done("causal ml/policy learning" in rejected_text and "rejected until the reduced-form identification gate passes" in modeling_report_text),
        "rejected_designs and modeling_report reject premature causal ML/policy learning",
        [TEMP_DIR / "rejected_designs.md", REPORT_DIR / "modeling_report.md", RESULT_DIR / "policy_learning_plan.csv"],
        "" if "causal ml/policy learning" in rejected_text else "add explicit causal-ML rejection until reduced-form identification passes",
    )
    add(
        "no_post_treatment_mechanism_controls",
        "Do not use post-shock mechanism variables as controls in the main climate-effect model.",
        status_done(
            counts["mechanism_requirements"] > 0
            and "do not include post-shock" in text(REPORT_DIR / "mechanism_analysis_protocol.md").lower()
        ),
        f"mechanism requirement rows={counts['mechanism_requirements']}; mechanism readiness rows={counts['mechanism_readiness']}; mechanism ready rows={counts['mechanism_ready']}",
        [REPORT_DIR / "mechanism_analysis_protocol.md", TEMP_DIR / "mechanism_variable_requirements.csv", RESULT_DIR / "mechanism_readiness_matrix.csv"],
        "" if counts["mechanism_requirements"] > 0 else "run mechanism analysis protocol",
    )
    add(
        "sdg382_denominator_guard",
        "Do not treat SDG 3.8.2 as fully constructed unless the discretionary-budget denominator is correct.",
        status_done(
            (
                "do not construct sdg 3.8.2" in text(REPORT_DIR / "manual_data_access_guide.md").lower()
                or "sdg 3.8.2" in text(REPORT_DIR / "outcome_denominator_plan.md").lower()
            )
            and counts["sdg382_denominator_requirements"] > 0
            and counts["sdg382_denominator_ready"] == 0
        ),
        f"outcome reports keep SDG 3.8.2 denominator guarded; denominator requirement rows={counts['sdg382_denominator_requirements']}; ready rows={counts['sdg382_denominator_ready']}",
        [REPORT_DIR / "manual_data_access_guide.md", REPORT_DIR / "outcome_denominator_plan.md", REPORT_DIR / "sdg382_denominator_audit_plan.md", TEMP_DIR / "outcome_denominator_plan.csv", TEMP_DIR / "sdg382_denominator_requirements.csv"],
    )
    add(
        "no_final_sample_before_raw",
        "Do not select final countries until inventory and raw/variable screening support it.",
        status_done(counts["country_wave_screening"] > 0 and counts["sample_gate_raw_final"] == 0),
        f"screening rows={counts['country_wave_screening']}; raw-final candidates={counts['sample_gate_raw_final']}",
        [TEMP_DIR / "country_wave_screening.csv", RESULT_DIR / "sample_selection_gate_audit.csv"],
    )
    add(
        "manual_download_only_for_gated_sources",
        "If raw data cannot be auto-downloaded, use manual manifests and continue metadata auditing.",
        status_done(counts["manual_download_manifest"] > 0 and counts["metadata_quality_priority"] > 0 and counts["raw_download_intake"] > 0),
        f"manual manifest rows={counts['manual_download_manifest']}; metadata priority rows={counts['metadata_quality_priority']}; intake targets={counts['raw_download_intake']}; raw-like files={counts['raw_like_files']}",
        [TEMP_DIR / "manual_download_manifest.csv", TEMP_DIR / "metadata_quality_download_priority.csv", TEMP_DIR / "raw_download_intake_manifest.csv", REPORT_DIR / "manual_data_access_guide.md"],
    )
    add(
        "raw_lineage_before_harmonization",
        "Never overwrite original variables; keep raw variable lineage before harmonization.",
        "blocked_raw_microdata" if counts["raw_variables"] == 0 else status_done(counts["harmonization_audit"] > 0),
        f"raw variables={counts['raw_variables']}; harmonization audit rows={counts['harmonization_audit']}; verification protocol rows={counts['raw_variable_verification_protocol']}; scaffold rows={counts['harmonization_scaffold']}; verified candidate rows={counts['harmonization_verified_candidates']}",
        [TEMP_DIR / "raw_schema_inventory" / "raw_variable_catalog.csv", TEMP_DIR / "harmonized_lineage.csv", TEMP_DIR / "harmonization_audit.csv", TEMP_DIR / "raw_variable_verification_protocol.csv", TEMP_DIR / "harmonization_recipe_scaffold.csv", TEMP_DIR / "harmonization_recipe_verified_candidates.csv"],
        "raw lineage cannot be proven until raw variables exist" if counts["raw_variables"] == 0 else "",
    )
    add(
        "no_scaffold_to_recipe_shortcut",
        "Do not create a harmonization recipe from metadata scaffold rows before raw value audits pass.",
        status_done(not file_ok(TEMP_DIR / "harmonization_recipe.csv") or counts["harmonization_verified_candidates"] > 0),
        f"harmonization_recipe.csv exists={file_ok(TEMP_DIR / 'harmonization_recipe.csv')}; verified candidate rows={counts['harmonization_verified_candidates']}; recipe gate rows={counts['harmonization_recipe_gate']}",
        [TEMP_DIR / "harmonization_recipe_scaffold.csv", TEMP_DIR / "harmonization_recipe_gate.csv", TEMP_DIR / "harmonization_recipe_verified_candidates.csv", TEMP_DIR / "harmonization_recipe.csv"],
        "" if not file_ok(TEMP_DIR / "harmonization_recipe.csv") else "remove or justify recipe file with passed raw value audits",
    )
    add(
        "climate_linkage_before_claims",
        "Never claim climate exposure construction without verified timing/geography and climate-linkage diagnostics.",
        status_done(
            counts["climate_exposures"] == counts["alb2002_limited_climate_exposure_rows"]
            and counts["limited_climate_exposure_marker"] == 1
            and counts["climate_linked"] == counts["alb2002_limited_climate_linked_rows"]
            and counts["limited_climate_linked_marker"] == 1
            and counts["climate_linkage_ready_value"] == 0
            and counts["alb2002_limited_climate_linked_final_analysis_ready_rows"] == 0
        ),
        f"climate exposure rows={counts['climate_exposures']}; limited climate marker={counts['limited_climate_exposure_marker']}; limited climate rows={counts['alb2002_limited_climate_exposure_rows']}; climate-linked rows={counts['climate_linked']}; limited linked rows={counts['alb2002_limited_climate_linked_rows']}; limited linked marker={counts['limited_climate_linked_marker']}; climate-linkage-ready rows={counts['climate_linkage_ready_value']}; limited linked final-analysis-ready rows={counts['alb2002_limited_climate_linked_final_analysis_ready_rows']}",
        [DATA_DIR / "climate_exposures_nasa_power.csv", DATA_DIR / "climate_linked_household.csv", RESULT_DIR / "climate_linkage_readiness.csv", REPORT_DIR / "climate_validation_protocol.md"],
        "" if counts["climate_exposures"] == counts["alb2002_limited_climate_exposure_rows"] and counts["limited_climate_exposure_marker"] == 1 and counts["climate_linked"] == counts["alb2002_limited_climate_linked_rows"] and counts["limited_climate_linked_marker"] == 1 else "remove false climate-linked outputs or restore limited exposure/linkage guardrails",
    )
    return rows


def build_summary(requirements: list[dict[str, str]], guardrails: list[dict[str, str]], counts: dict[str, int]) -> list[dict[str, str]]:
    req_counts = Counter(row["status"] for row in requirements)
    guard_counts = Counter(row["status"] for row in guardrails)
    rows = [
        {"metric": "requirement_rows", "value": str(len(requirements)), "interpretation": "Objective requirement traceability rows."},
        {"metric": "guardrail_rows", "value": str(len(guardrails)), "interpretation": "Objective interpretation and directory guardrail rows."},
        {"metric": "raw_file_inventory_rows", "value": str(counts["raw_files"]), "interpretation": "Raw tabular files inspected."},
        {"metric": "raw_variable_catalog_rows", "value": str(counts["raw_variables"]), "interpretation": "Raw variables inspected."},
        {"metric": "public_external_download_rows", "value": str(counts["public_external_downloads"]), "interpretation": "Public external candidate raw download audit rows."},
        {"metric": "public_external_downloaded_rows", "value": str(counts["public_external_downloaded"]), "interpretation": "Public external raw archives downloaded or already present."},
        {"metric": "public_external_dataset_rows", "value": str(counts["public_external_datasets"]), "interpretation": "Datasets with public external raw archives present."},
        {"metric": "raw_variable_verification_protocol_rows", "value": str(counts["raw_variable_verification_protocol"]), "interpretation": "Raw-variable verification protocol rows."},
        {"metric": "harmonization_scaffold_rows", "value": str(counts["harmonization_scaffold"]), "interpretation": "Metadata-only harmonization scaffold rows."},
        {"metric": "harmonization_recipe_gate_rows", "value": str(counts["harmonization_recipe_gate"]), "interpretation": "Harmonization scaffold rows assessed by recipe gate."},
        {"metric": "harmonization_verified_candidate_rows", "value": str(counts["harmonization_verified_candidates"]), "interpretation": "Rows ready to promote into a verified harmonization recipe."},
        {"metric": "harmonization_ready_country_waves", "value": str(counts["harmonization_ready_country_waves"]), "interpretation": "Country-waves ready for verified recipe assembly."},
        {"metric": "analysis_dataset_promotion_audit_rows", "value": str(counts["analysis_dataset_promotion_audit_rows"]), "interpretation": "Analysis dataset promotion targets checked."},
        {"metric": "analysis_dataset_promotion_blocked_rows", "value": str(counts["analysis_dataset_promotion_blocked_rows"]), "interpretation": "Promotion targets blocked from data/."},
        {"metric": "analysis_dataset_promotion_promoted_rows", "value": str(counts["analysis_dataset_promotion_promoted_rows"]), "interpretation": "Promotion targets allowed for data/ writes; limited core/outcome/exposure/linked diagnostic files only while model-ready data remain blocked."},
        {"metric": "analysis_dataset_promotion_data_file_count", "value": str(counts["analysis_dataset_promotion_data_file_count"]), "interpretation": "Files currently present under data/."},
        {"metric": "analysis_dataset_promotion_verified_recipe_candidates", "value": str(counts["analysis_dataset_promotion_verified_recipe_candidates"]), "interpretation": "Verified recipe candidates carried into the promotion-barrier audit."},
        {"metric": "analysis_dataset_promotion_ready_country_waves", "value": str(counts["analysis_dataset_promotion_ready_country_waves"]), "interpretation": "Ready country-waves carried into the promotion-barrier audit."},
        {"metric": "analysis_dataset_promotion_alb2002_temp_core_rows", "value": str(counts["analysis_dataset_promotion_alb2002_temp_core_rows"]), "interpretation": "ALB_2002 temp core rows carried into the promotion-barrier audit."},
        {"metric": "analysis_dataset_promotion_alb2002_weight_positive_rows", "value": str(counts["analysis_dataset_promotion_alb2002_weight_positive_rows"]), "interpretation": "ALB_2002 positive household-weight rows carried into the promotion-barrier audit."},
        {"metric": "analysis_dataset_promotion_alb2002_weight_key_match_rows", "value": str(counts["analysis_dataset_promotion_alb2002_weight_key_match_rows"]), "interpretation": "ALB_2002 household-weight key matches carried into the promotion-barrier audit."},
        {"metric": "analysis_dataset_promotion_alb2002_weighted_inference_ready_rows", "value": str(counts["analysis_dataset_promotion_alb2002_weighted_inference_ready_rows"]), "interpretation": "ALB_2002 rows ready for promoted weighted inference; should remain zero."},
        {"metric": "analysis_dataset_promotion_alb2002_harmonized_ready_rows", "value": str(counts["analysis_dataset_promotion_alb2002_harmonized_ready_rows"]), "interpretation": "ALB_2002 harmonized rows ready for promotion; should remain zero."},
        {"metric": "analysis_dataset_promotion_alb2002_outcome_ready_rows", "value": str(counts["analysis_dataset_promotion_alb2002_outcome_ready_rows"]), "interpretation": "ALB_2002 outcome rows ready for promotion; should remain zero."},
        {"metric": "analysis_dataset_promotion_alb2002_climate_linkage_ready_rows", "value": str(counts["analysis_dataset_promotion_alb2002_climate_linkage_ready_rows"]), "interpretation": "ALB_2002 climate-linkage rows ready for promotion; should remain zero."},
        {"metric": "analysis_dataset_promotion_limited_harmonized_core_rows", "value": str(counts["analysis_dataset_promotion_limited_harmonized_core_rows"]), "interpretation": "Rows written to data/harmonized_household.csv under limited scope."},
        {"metric": "analysis_dataset_promotion_limited_harmonized_core_data_write_ready_rows", "value": str(counts["analysis_dataset_promotion_limited_harmonized_core_data_write_ready_rows"]), "interpretation": "Rows allowed for data/ write only as limited harmonized household core."},
        {"metric": "analysis_dataset_promotion_limited_harmonized_core_final_outcome_ready_rows", "value": str(counts["analysis_dataset_promotion_limited_harmonized_core_final_outcome_ready_rows"]), "interpretation": "Rows ready for final outcomes; should remain zero."},
        {"metric": "analysis_dataset_promotion_limited_harmonized_core_climate_linkage_ready_rows", "value": str(counts["analysis_dataset_promotion_limited_harmonized_core_climate_linkage_ready_rows"]), "interpretation": "Rows ready for climate linkage; should remain zero."},
        {"metric": "analysis_dataset_promotion_limited_climate_exposure_rows", "value": str(counts["analysis_dataset_promotion_limited_climate_exposure_rows"]), "interpretation": "Rows written to data/climate_exposures_nasa_power.csv under limited fallback scope."},
        {"metric": "analysis_dataset_promotion_limited_climate_exposure_data_write_ready_rows", "value": str(counts["analysis_dataset_promotion_limited_climate_exposure_data_write_ready_rows"]), "interpretation": "Rows allowed for data/ write only as limited fallback climate exposures."},
        {"metric": "analysis_dataset_promotion_limited_climate_exposure_climate_linkage_ready_rows", "value": str(counts["analysis_dataset_promotion_limited_climate_exposure_climate_linkage_ready_rows"]), "interpretation": "Rows ready for final climate linkage; should remain zero."},
        {"metric": "analysis_dataset_promotion_current_decision", "value": counts["analysis_dataset_promotion_current_decision"], "interpretation": "Current fail-closed analysis dataset promotion decision."},
        {"metric": "minimum_viable_acquisition_targets", "value": str(counts["minimum_viable_acquisition_targets"]), "interpretation": "Metadata-only acquisition target rows."},
        {"metric": "minimum_viable_download_bundles", "value": str(counts["minimum_viable_download_bundles"]), "interpretation": "Unique manual-download bundle rows."},
        {"metric": "sdg382_denominator_requirement_rows", "value": str(counts["sdg382_denominator_requirements"]), "interpretation": "SDG 3.8.2 denominator requirement rows."},
        {"metric": "sdg382_denominator_ready_rows", "value": str(counts["sdg382_denominator_ready"]), "interpretation": "Rows ready for household denominator value audit."},
        {"metric": "climate_linkage_requirement_rows", "value": str(counts["climate_linkage_requirements"]), "interpretation": "Climate linkage requirement rows."},
        {"metric": "climate_linkage_ready_value_rows", "value": str(counts["climate_linkage_ready_value"]), "interpretation": "Rows ready for climate linkage value audit."},
        {"metric": "mechanism_requirement_rows", "value": str(counts["mechanism_requirements"]), "interpretation": "Mechanism pathway concept requirement rows."},
        {"metric": "mechanism_readiness_rows", "value": str(counts["mechanism_readiness"]), "interpretation": "Country-wave pathway readiness rows."},
        {"metric": "mechanism_ready_rows", "value": str(counts["mechanism_ready"]), "interpretation": "Rows ready for mechanism analysis design."},
        {"metric": "mechanism_blocked_rows", "value": str(counts["mechanism_blocked"]), "interpretation": "Rows blocked by raw evidence or upstream gates."},
        {"metric": "empirical_dashboard_rows", "value": str(counts["empirical_dashboard"]), "interpretation": "Consolidated empirical readiness dashboard rows."},
        {"metric": "empirical_no_go_rows", "value": str(counts["empirical_no_go"]), "interpretation": "Go/no-go threshold status rows."},
        {"metric": "empirical_no_go_pass_rows", "value": str(counts["empirical_no_go_pass"]), "interpretation": "Go/no-go threshold rows currently passing."},
        {"metric": "empirical_no_go_blocked_rows", "value": str(counts["empirical_no_go_blocked"]), "interpretation": "Go/no-go threshold rows blocked or failing."},
        {"metric": "first_batch_raw_acquisition_checklist_rows", "value": str(counts["first_batch_raw_acquisition_checklist"]), "interpretation": "First-batch manual raw acquisition dataset rows."},
        {"metric": "first_batch_raw_file_target_rows", "value": str(counts["first_batch_raw_file_targets"]), "interpretation": "First-batch file/module target rows."},
        {"metric": "first_batch_raw_acquisition_summary_rows", "value": str(counts["first_batch_raw_acquisition_summary"]), "interpretation": "First-batch raw acquisition summary rows."},
        {"metric": "first_batch_official_raw_access_probe_rows", "value": str(counts["first_batch_official_raw_access_probe"]), "interpretation": "First-batch official get-microdata page probe rows."},
        {"metric": "first_batch_access_gate_detected_rows", "value": str(counts["first_batch_access_gate_detected"]), "interpretation": "First-batch rows with login, registration, request, or terms signals."},
        {"metric": "first_batch_possible_direct_raw_route_rows", "value": str(counts["first_batch_possible_direct_raw_routes"]), "interpretation": "First-batch rows with possible direct raw routes; links are not downloaded by the probe."},
        {"metric": "first_batch_manual_download_handoff_rows", "value": str(counts["first_batch_manual_download_handoff"]), "interpretation": "First-batch dataset-level manual download handoff rows."},
        {"metric": "first_batch_manual_download_file_queue_rows", "value": str(counts["first_batch_manual_download_file_queue"]), "interpretation": "First-batch deduplicated file/module queue rows."},
        {"metric": "first_batch_handoff_raw_ready_rows", "value": str(counts["first_batch_handoff_raw_ready"]), "interpretation": "First-batch handoff rows ready for raw schema and value audit."},
        {"metric": "first_batch_public_documentation_rows", "value": str(counts["first_batch_public_documentation_audit"]), "interpretation": "First-batch public documentation resource rows."},
        {"metric": "first_batch_public_documentation_saved_rows", "value": str(counts["first_batch_public_documentation_saved"]), "interpretation": "First-batch public documentation rows saved or reused."},
        {"metric": "first_batch_public_documentation_failed_rows", "value": str(counts["first_batch_public_documentation_failed"]), "interpretation": "First-batch public documentation rows that failed to fetch."},
        {"metric": "first_batch_file_source_traceability_rows", "value": str(counts["first_batch_file_source_traceability"]), "interpretation": "First-batch file-source traceability rows."},
        {"metric": "first_batch_file_source_supported_rows", "value": str(counts["first_batch_file_source_supported"]), "interpretation": "First-batch queued files supported by public schema and candidate examples."},
        {"metric": "first_batch_file_source_unsupported_rows", "value": str(counts["first_batch_file_source_unsupported"]), "interpretation": "First-batch queued files missing from public schema inventory."},
        {"metric": "first_batch_merge_key_lineage_plan_rows", "value": str(counts["first_batch_merge_key_lineage_plan"]), "interpretation": "First-batch dataset-level merge-key lineage plan rows."},
        {"metric": "first_batch_merge_key_candidate_rows", "value": str(counts["first_batch_merge_key_candidates"]), "interpretation": "First-batch key, design, timing, and geography candidate variable rows."},
        {"metric": "first_batch_merge_key_planned_rows", "value": str(counts["first_batch_merge_key_planned"]), "interpretation": "First-batch rows with metadata-planned key lineage before raw verification."},
        {"metric": "first_batch_merge_key_raw_ready_rows", "value": str(counts["first_batch_merge_key_raw_ready"]), "interpretation": "First-batch rows with raw files ready for value/key audit."},
        {"metric": "first_batch_raw_value_key_audit_rows", "value": str(counts["first_batch_raw_value_key_audit"]), "interpretation": "First-batch observed value-audit rows."},
        {"metric": "first_batch_raw_value_key_read_ok_rows", "value": str(counts["first_batch_raw_value_key_read_ok"]), "interpretation": "First-batch value-audit rows read successfully from raw files."},
        {"metric": "first_batch_raw_merge_key_audit_rows", "value": str(counts["first_batch_raw_merge_key_audit"]), "interpretation": "First-batch file-level key cardinality audit rows."},
        {"metric": "first_batch_harmonization_value_audit_auto_rows", "value": str(counts["first_batch_harmonization_value_audit_auto"]), "interpretation": "Fail-closed auto value-audit rows provided to the harmonization gate."},
        {"metric": "first_batch_harmonization_value_audit_auto_ready_rows", "value": str(counts["first_batch_harmonization_value_audit_auto_ready"]), "interpretation": "Auto value-audit rows marked ready for recipe; should remain zero."},
        {"metric": "alb2002_household_core_candidate_rows", "value": str(counts["alb2002_household_core_candidate"]), "interpretation": "ALB_2002 temp household core candidate rows."},
        {"metric": "alb2002_household_core_recipe_ready_rows", "value": str(counts["alb2002_household_core_recipe_ready_rows"]), "interpretation": "ALB_2002 household core rows ready for data promotion; should remain zero until gates pass."},
        {"metric": "alb2002_provisional_outcome_feasibility_rows", "value": str(counts["alb2002_provisional_outcome_feasibility_audit"]), "interpretation": "ALB_2002 provisional outcome feasibility audit rows."},
        {"metric": "alb2002_provisional_outcome_ready_rows", "value": str(counts["alb2002_provisional_outcome_ready_rows"]), "interpretation": "ALB_2002 provisional outcome rows ready for final promotion; should remain zero."},
        {"metric": "alb2002_outcome_semantics_raw_value_rows", "value": str(counts["alb2002_outcome_semantics_raw_value_audit"]), "interpretation": "ALB_2002 raw outcome-semantics value audit rows."},
        {"metric": "alb2002_outcome_semantics_outcome_ready_rows", "value": str(counts["alb2002_outcome_semantics_outcome_ready_rows"]), "interpretation": "ALB_2002 raw outcome-semantics rows ready for final promotion; should remain zero."},
        {"metric": "alb2002_outcome_semantics_sdg382_ready_rows", "value": str(counts["alb2002_outcome_semantics_sdg382_ready_rows"]), "interpretation": "ALB_2002 raw outcome-semantics rows ready for SDG 3.8.2 construction; should remain zero."},
        {"metric": "alb2002_health_questionnaire_semantics_rows", "value": str(counts["alb2002_health_questionnaire_semantics_rows"]), "interpretation": "ALB_2002 health questionnaire semantics and skip-path audit rows."},
        {"metric": "alb2002_health_questionnaire_oop_item_rows", "value": str(counts["alb2002_health_questionnaire_oop_item_rows"]), "interpretation": "ALB_2002 questionnaire-backed OOP payment item rows."},
        {"metric": "alb2002_health_questionnaire_gift_item_rows", "value": str(counts["alb2002_health_questionnaire_gift_item_rows"]), "interpretation": "ALB_2002 gift/payment-scope rows requiring inclusion policy."},
        {"metric": "alb2002_health_questionnaire_new_lek_unit_rows", "value": str(counts["alb2002_health_questionnaire_new_lek_unit_rows"]), "interpretation": "ALB_2002 questionnaire rows explicitly recording NEW LEKS units."},
        {"metric": "alb2002_health_questionnaire_four_week_oop_rows", "value": str(counts["alb2002_health_questionnaire_four_week_oop_rows"]), "interpretation": "ALB_2002 OOP item rows with four-week recall."},
        {"metric": "alb2002_health_questionnaire_twelve_month_oop_rows", "value": str(counts["alb2002_health_questionnaire_twelve_month_oop_rows"]), "interpretation": "ALB_2002 OOP item rows with twelve-month recall."},
        {"metric": "alb2002_health_questionnaire_payment_positive_when_not_triggered_rows", "value": str(counts["alb2002_health_questionnaire_payment_positive_when_not_triggered_rows"]), "interpretation": "ALB_2002 positive skipped-payment downstream rows; should remain zero."},
        {"metric": "alb2002_health_questionnaire_outcome_ready_rows", "value": str(counts["alb2002_health_questionnaire_outcome_ready_rows"]), "interpretation": "ALB_2002 questionnaire rows ready for final outcome promotion; should remain zero."},
        {"metric": "alb2002_health_questionnaire_sdg382_ready_rows", "value": str(counts["alb2002_health_questionnaire_sdg382_ready_rows"]), "interpretation": "ALB_2002 questionnaire rows ready for SDG 3.8.2 construction; should remain zero."},
        {"metric": "alb2002_health_questionnaire_climate_linkage_ready_rows", "value": str(counts["alb2002_health_questionnaire_climate_linkage_ready_rows"]), "interpretation": "ALB_2002 questionnaire rows ready for climate linkage; should remain zero."},
        {"metric": "alb2002_oop_aggregation_policy_rows", "value": str(counts["alb2002_oop_aggregation_policy_rows"]), "interpretation": "ALB_2002 OOP aggregation policy stress-test rows."},
        {"metric": "alb2002_oop_aggregation_policy_core_4w_match_rows", "value": str(counts["alb2002_oop_aggregation_policy_core_4w_match_rows"]), "interpretation": "Rows where recomputed four-week OOP matches the existing ALB_2002 core candidate sum."},
        {"metric": "alb2002_oop_aggregation_policy_core_12m_match_rows", "value": str(counts["alb2002_oop_aggregation_policy_core_12m_match_rows"]), "interpretation": "Rows where recomputed twelve-month OOP matches the existing ALB_2002 core candidate sum."},
        {"metric": "alb2002_oop_aggregation_policy_outcome_ready_rows", "value": str(counts["alb2002_oop_aggregation_policy_outcome_ready_rows"]), "interpretation": "ALB_2002 OOP policy rows ready for final outcome promotion; should remain zero."},
        {"metric": "alb2002_oop_aggregation_policy_sdg382_ready_rows", "value": str(counts["alb2002_oop_aggregation_policy_sdg382_ready_rows"]), "interpretation": "ALB_2002 OOP policy rows ready for SDG 3.8.2 construction; should remain zero."},
        {"metric": "alb2002_oop_aggregation_policy_climate_linkage_ready_rows", "value": str(counts["alb2002_oop_aggregation_policy_climate_linkage_ready_rows"]), "interpretation": "ALB_2002 OOP policy rows ready for climate linkage; should remain zero."},
        {"metric": "alb2002_skip_missing_semantics_rows", "value": str(counts["alb2002_skip_missing_semantics_rows"]), "interpretation": "ALB_2002 skip/missing semantics audit rows."},
        {"metric": "alb2002_skip_missing_payment_positive_when_not_triggered_rows", "value": str(counts["alb2002_skip_missing_payment_positive_when_not_triggered_rows"]), "interpretation": "ALB_2002 skipped payment rows with positive downstream values; should remain zero."},
        {"metric": "alb2002_skip_missing_payment_zero_cells_when_not_triggered", "value": str(counts["alb2002_skip_missing_payment_zero_cells_when_not_triggered"]), "interpretation": "ALB_2002 skipped payment downstream cells equal to zero; downstream decision audit records no positive leakage."},
        {"metric": "alb2002_skip_missing_payment_positive_cells_when_not_triggered", "value": str(counts["alb2002_skip_missing_payment_positive_cells_when_not_triggered"]), "interpretation": "ALB_2002 skipped payment downstream cells positive; should remain zero."},
        {"metric": "alb2002_skip_missing_outcome_ready_rows", "value": str(counts["alb2002_skip_missing_outcome_ready_rows"]), "interpretation": "ALB_2002 skip/missing rows ready for final outcome promotion; should remain zero."},
        {"metric": "alb2002_skip_missing_sdg382_ready_rows", "value": str(counts["alb2002_skip_missing_sdg382_ready_rows"]), "interpretation": "ALB_2002 skip/missing rows ready for SDG 3.8.2 construction; should remain zero."},
        {"metric": "alb2002_skip_missing_climate_linkage_ready_rows", "value": str(counts["alb2002_skip_missing_climate_linkage_ready_rows"]), "interpretation": "ALB_2002 skip/missing rows ready for climate linkage; should remain zero."},
        {"metric": "alb2002_oop_skip_value_decision_rows", "value": str(counts["alb2002_oop_skip_value_decision_rows"]), "interpretation": "ALB_2002 OOP skip-value decision audit rows."},
        {"metric": "alb2002_oop_skip_value_payment_zero_skipped_cells", "value": str(counts["alb2002_oop_skip_value_payment_zero_skipped_cells"]), "interpretation": "ALB_2002 zero-valued downstream payment cells when payment block was not triggered."},
        {"metric": "alb2002_oop_skip_value_payment_positive_skipped_rows", "value": str(counts["alb2002_oop_skip_value_payment_positive_skipped_rows"]), "interpretation": "ALB_2002 rows with positive downstream payment values when payment block was not triggered; should remain zero."},
        {"metric": "alb2002_oop_skip_value_payment_positive_skipped_cells", "value": str(counts["alb2002_oop_skip_value_payment_positive_skipped_cells"]), "interpretation": "ALB_2002 positive downstream payment cells when payment block was not triggered; should remain zero."},
        {"metric": "alb2002_oop_skip_value_zero_skip_policy_ready_rows", "value": str(counts["alb2002_oop_skip_value_zero_skip_policy_ready_rows"]), "interpretation": "ALB_2002 rows supporting the narrow no-positive-leakage skipped-payment decision."},
        {"metric": "alb2002_oop_skip_value_oop_recall_scope_ready_rows", "value": str(counts["alb2002_oop_skip_value_oop_recall_scope_ready_rows"]), "interpretation": "ALB_2002 OOP recall-scope rows accepted by the skip-value audit; should remain zero."},
        {"metric": "alb2002_oop_skip_value_oop_inclusion_scope_ready_rows", "value": str(counts["alb2002_oop_skip_value_oop_inclusion_scope_ready_rows"]), "interpretation": "ALB_2002 OOP inclusion-scope rows accepted by the skip-value audit; should remain zero."},
        {"metric": "alb2002_oop_skip_value_outcome_ready_rows", "value": str(counts["alb2002_oop_skip_value_outcome_ready_rows"]), "interpretation": "ALB_2002 OOP skip-value rows ready for outcome promotion; should remain zero."},
        {"metric": "alb2002_access_need_denominator_policy_rows", "value": str(counts["alb2002_access_need_denominator_policy_rows"]), "interpretation": "ALB_2002 access/need denominator policy audit rows."},
        {"metric": "alb2002_access_need_q01_need_rows", "value": str(counts["alb2002_access_need_q01_need_rows"]), "interpretation": "ALB_2002 households not coded as no-one-needed-health-care in m5b_q01."},
        {"metric": "alb2002_access_need_person_need_household_rows", "value": str(counts["alb2002_access_need_person_need_household_rows"]), "interpretation": "ALB_2002 households with any Health A chronic/disability or sudden-illness proxy."},
        {"metric": "alb2002_access_need_composite_any_access_barrier_rows", "value": str(counts["alb2002_access_need_composite_any_access_barrier_rows"]), "interpretation": "ALB_2002 composite any-access-barrier candidate rows; not a final outcome."},
        {"metric": "alb2002_access_need_low_event_rate_rows", "value": str(counts["alb2002_access_need_low_event_rate_rows"]), "interpretation": "ALB_2002 access/need denominator policies with event rate below 3 percent."},
        {"metric": "alb2002_access_need_outcome_ready_rows", "value": str(counts["alb2002_access_need_outcome_ready_rows"]), "interpretation": "ALB_2002 access/need rows ready for final outcome promotion; should remain zero."},
        {"metric": "alb2002_access_need_sdg382_ready_rows", "value": str(counts["alb2002_access_need_sdg382_ready_rows"]), "interpretation": "ALB_2002 access/need rows ready for SDG 3.8.2 construction; should remain zero."},
        {"metric": "alb2002_access_need_climate_linkage_ready_rows", "value": str(counts["alb2002_access_need_climate_linkage_ready_rows"]), "interpretation": "ALB_2002 access/need rows ready for climate linkage; should remain zero."},
        {"metric": "alb2002_consumption_sdg_denominator_policy_rows", "value": str(counts["alb2002_consumption_sdg_denominator_policy_rows"]), "interpretation": "ALB_2002 consumption/SDG denominator policy audit rows."},
        {"metric": "alb2002_consumption_sdg_positive_total_consumption_rows", "value": str(counts["alb2002_consumption_sdg_positive_total_consumption_rows"]), "interpretation": "ALB_2002 rows with positive total consumption in the temp candidate."},
        {"metric": "alb2002_consumption_sdg_spl_ready_rows", "value": str(counts["alb2002_consumption_sdg_spl_ready_rows"]), "interpretation": "ALB_2002 rows with SPL inputs accepted; should remain zero."},
        {"metric": "alb2002_consumption_sdg_ppp_cpi_ready_rows", "value": str(counts["alb2002_consumption_sdg_ppp_cpi_ready_rows"]), "interpretation": "ALB_2002 rows with PPP/CPI inputs accepted; should remain zero."},
        {"metric": "alb2002_consumption_sdg_discretionary_budget_ready_rows", "value": str(counts["alb2002_consumption_sdg_discretionary_budget_ready_rows"]), "interpretation": "ALB_2002 rows with discretionary budget accepted; should remain zero."},
        {"metric": "alb2002_consumption_sdg_che_denominator_ready_rows", "value": str(counts["alb2002_consumption_sdg_che_denominator_ready_rows"]), "interpretation": "ALB_2002 rows with CHE denominator accepted; should remain zero."},
        {"metric": "alb2002_consumption_sdg_outcome_ready_rows", "value": str(counts["alb2002_consumption_sdg_outcome_ready_rows"]), "interpretation": "ALB_2002 consumption/SDG rows ready for final outcome promotion; should remain zero."},
        {"metric": "alb2002_consumption_sdg_sdg382_ready_rows", "value": str(counts["alb2002_consumption_sdg_sdg382_ready_rows"]), "interpretation": "ALB_2002 rows ready for SDG 3.8.2 construction; should remain zero."},
        {"metric": "alb2002_consumption_sdg_climate_linkage_ready_rows", "value": str(counts["alb2002_consumption_sdg_climate_linkage_ready_rows"]), "interpretation": "ALB_2002 consumption/SDG rows ready for climate linkage; should remain zero."},
        {"metric": "alb2002_consumption_construction_source_audit_rows", "value": str(counts["alb2002_consumption_construction_source_audit_rows"]), "interpretation": "ALB_2002 public consumption-construction source audit rows."},
        {"metric": "alb2002_consumption_construction_do_file_rows", "value": str(counts["alb2002_consumption_construction_do_file_rows"]), "interpretation": "Extracted public ALB_2002 Stata do-files documenting consumption construction."},
        {"metric": "alb2002_consumption_construction_documentation_ready_rows", "value": str(counts["alb2002_consumption_construction_documentation_ready_rows"]), "interpretation": "ALB_2002 source-audit rows with accepted public construction documentation."},
        {"metric": "alb2002_consumption_construction_released_variable_mapping_ready_rows", "value": str(counts["alb2002_consumption_construction_released_variable_mapping_ready_rows"]), "interpretation": "ALB_2002 source-audit rows supporting local `totcons` to public `totcons3` mapping."},
        {"metric": "alb2002_consumption_construction_denominator_variant_ready_rows", "value": str(counts["alb2002_consumption_construction_denominator_variant_ready_rows"]), "interpretation": "ALB_2002 source-audit rows documenting the final total-budget denominator variant."},
        {"metric": "alb2002_consumption_construction_outcome_ready_rows", "value": str(counts["alb2002_consumption_construction_outcome_ready_rows"]), "interpretation": "ALB_2002 source-audit rows ready for outcome promotion; should remain zero."},
        {"metric": "alb2002_consumption_construction_sdg382_ready_rows", "value": str(counts["alb2002_consumption_construction_sdg382_ready_rows"]), "interpretation": "ALB_2002 source-audit rows ready for SDG 3.8.2 promotion; should remain zero."},
        {"metric": "alb2002_consumption_construction_climate_linkage_ready_rows", "value": str(counts["alb2002_consumption_construction_climate_linkage_ready_rows"]), "interpretation": "ALB_2002 source-audit rows ready for climate linkage; should remain zero."},
        {"metric": "alb2002_consumption_aggregate_crosswalk_rows", "value": str(counts["alb2002_consumption_aggregate_crosswalk_rows"]), "interpretation": "ALB_2002 aggregate metadata/local evidence crosswalk rows."},
        {"metric": "alb2002_consumption_aggregate_crosswalk_metadata_catalog_rows", "value": str(counts["alb2002_consumption_aggregate_crosswalk_metadata_catalog_rows"]), "interpretation": "Local master metadata rows available for ALB_2002 aggregate verification; public source evidence now sits in the construction-source audit instead."},
        {"metric": "alb2002_consumption_aggregate_crosswalk_raw_totcons_positive_rows", "value": str(counts["alb2002_consumption_aggregate_crosswalk_raw_totcons_positive_rows"]), "interpretation": "Positive raw `totcons` rows in local ALB_2002 Poverty_2002.sav."},
        {"metric": "alb2002_consumption_aggregate_crosswalk_candidate_totcons_match_rows", "value": str(counts["alb2002_consumption_aggregate_crosswalk_candidate_totcons_match_rows"]), "interpretation": "ALB_2002 candidate total_consumption rows exactly matching raw `totcons`."},
        {"metric": "alb2002_consumption_aggregate_crosswalk_questionnaire_aggregate_formula_hits", "value": str(counts["alb2002_consumption_aggregate_crosswalk_questionnaire_aggregate_formula_hits"]), "interpretation": "Questionnaire aggregate-formula evidence hits; source-code documentation is captured separately."},
        {"metric": "alb2002_consumption_aggregate_crosswalk_construction_source_rows", "value": str(counts["alb2002_consumption_aggregate_crosswalk_construction_source_rows"]), "interpretation": "Rows imported from the upstream ALB_2002 public consumption-construction source audit."},
        {"metric": "alb2002_consumption_aggregate_crosswalk_construction_do_file_rows", "value": str(counts["alb2002_consumption_aggregate_crosswalk_construction_do_file_rows"]), "interpretation": "Extracted public Stata do-files used as ALB_2002 denominator-construction evidence."},
        {"metric": "alb2002_consumption_aggregate_crosswalk_metadata_unit_period_ready_rows", "value": str(counts["alb2002_consumption_aggregate_crosswalk_metadata_unit_period_ready_rows"]), "interpretation": "ALB_2002 rows with denominator-variant and unit/period context documented by public sources."},
        {"metric": "alb2002_consumption_aggregate_crosswalk_official_documentation_ready_rows", "value": str(counts["alb2002_consumption_aggregate_crosswalk_official_documentation_ready_rows"]), "interpretation": "ALB_2002 rows with accepted public aggregate-construction documentation."},
        {"metric": "alb2002_consumption_aggregate_crosswalk_released_variable_mapping_ready_rows", "value": str(counts["alb2002_consumption_aggregate_crosswalk_released_variable_mapping_ready_rows"]), "interpretation": "ALB_2002 rows supporting the local `totcons` to public `totcons3` mapping."},
        {"metric": "alb2002_consumption_aggregate_crosswalk_denominator_variant_ready_rows", "value": str(counts["alb2002_consumption_aggregate_crosswalk_denominator_variant_ready_rows"]), "interpretation": "ALB_2002 rows documenting the total-budget denominator variant."},
        {"metric": "alb2002_consumption_aggregate_crosswalk_recipe_ready_rows", "value": str(counts["alb2002_consumption_aggregate_crosswalk_recipe_ready_rows"]), "interpretation": "ALB_2002 aggregate crosswalk rows ready for recipe promotion; should remain zero."},
        {"metric": "alb2002_consumption_aggregate_crosswalk_outcome_ready_rows", "value": str(counts["alb2002_consumption_aggregate_crosswalk_outcome_ready_rows"]), "interpretation": "ALB_2002 aggregate crosswalk rows ready for outcome promotion; should remain zero."},
        {"metric": "alb2002_consumption_aggregate_crosswalk_sdg382_ready_rows", "value": str(counts["alb2002_consumption_aggregate_crosswalk_sdg382_ready_rows"]), "interpretation": "ALB_2002 aggregate crosswalk rows ready for SDG 3.8.2 promotion; should remain zero."},
        {"metric": "alb2002_consumption_aggregate_crosswalk_climate_linkage_ready_rows", "value": str(counts["alb2002_consumption_aggregate_crosswalk_climate_linkage_ready_rows"]), "interpretation": "ALB_2002 aggregate crosswalk rows ready for climate linkage; should remain zero."},
        {"metric": "alb2002_period_aligned_che_policy_rows", "value": str(counts["alb2002_period_aligned_che_policy_rows"]), "interpretation": "ALB_2002 period-aligned CHE stress-test policy rows."},
        {"metric": "alb2002_period_aligned_che_period_alignment_ready_rows", "value": str(counts["alb2002_period_aligned_che_period_alignment_ready_rows"]), "interpretation": "ALB_2002 period-aligned CHE rows ready for stress testing, not outcome promotion."},
        {"metric": "alb2002_period_aligned_che_combined_che10_rate", "value": str(counts["alb2002_period_aligned_che_combined_che10_rate"]), "interpretation": "Combined monthly-equivalent unweighted CHE10 rate for ALB_2002 no-gifts-with-transport stress test."},
        {"metric": "alb2002_period_aligned_che_combined_che25_rate", "value": str(counts["alb2002_period_aligned_che_combined_che25_rate"]), "interpretation": "Combined monthly-equivalent unweighted CHE25 rate for ALB_2002 no-gifts-with-transport stress test."},
        {"metric": "alb2002_period_aligned_che_outcome_ready_rows", "value": str(counts["alb2002_period_aligned_che_outcome_ready_rows"]), "interpretation": "ALB_2002 period-aligned CHE rows promoted to final outcomes; should remain zero."},
        {"metric": "alb2002_period_aligned_che_current_decision", "value": str(counts["alb2002_period_aligned_che_current_decision"]), "interpretation": "Current ALB_2002 period-aligned CHE policy decision."},
        {"metric": "alb2002_che_candidate_household_rows", "value": str(counts["alb2002_che_candidate_household_rows"]), "interpretation": "ALB_2002 temp-only household CHE candidate rows."},
        {"metric": "alb2002_che_candidate_denominator_rows", "value": str(counts["alb2002_che_candidate_denominator_rows"]), "interpretation": "ALB_2002 CHE candidate rows with positive monthly total-budget candidate denominator."},
        {"metric": "alb2002_che_candidate_che10_rows", "value": str(counts["alb2002_che_candidate_che10_rows"]), "interpretation": "ALB_2002 candidate CHE10 rows under the period-aligned combined OOP policy."},
        {"metric": "alb2002_che_candidate_che10_rate", "value": str(counts["alb2002_che_candidate_che10_rate"]), "interpretation": "ALB_2002 candidate CHE10 rate; audit only."},
        {"metric": "alb2002_che_candidate_che25_rows", "value": str(counts["alb2002_che_candidate_che25_rows"]), "interpretation": "ALB_2002 candidate CHE25 rows under the period-aligned combined OOP policy."},
        {"metric": "alb2002_che_candidate_che25_rate", "value": str(counts["alb2002_che_candidate_che25_rate"]), "interpretation": "ALB_2002 candidate CHE25 rate; audit only."},
        {"metric": "alb2002_che_candidate_outcome_promotion_ready_rows", "value": str(counts["alb2002_che_candidate_outcome_promotion_ready_rows"]), "interpretation": "ALB_2002 candidate outcome rows ready for final promotion; should remain zero."},
        {"metric": "alb2002_che_candidate_current_decision", "value": str(counts["alb2002_che_candidate_current_decision"]), "interpretation": "Current ALB_2002 CHE candidate outcome decision."},
        {"metric": "alb2002_access_candidate_household_rows", "value": str(counts["alb2002_access_candidate_household_rows"]), "interpretation": "ALB_2002 temp-only household access candidate rows."},
        {"metric": "alb2002_access_candidate_q01_need_rows", "value": str(counts["alb2002_access_candidate_q01_need_rows"]), "interpretation": "ALB_2002 q01 household need candidate rows."},
        {"metric": "alb2002_access_candidate_person_need_rows", "value": str(counts["alb2002_access_candidate_person_need_rows"]), "interpretation": "ALB_2002 person-level need proxy rows aggregated to household."},
        {"metric": "alb2002_access_candidate_composite_cost_rows", "value": str(counts["alb2002_access_candidate_composite_cost_rows"]), "interpretation": "ALB_2002 temp-only composite cost-barrier candidate rows."},
        {"metric": "alb2002_access_candidate_composite_any_rows", "value": str(counts["alb2002_access_candidate_composite_any_rows"]), "interpretation": "ALB_2002 temp-only composite any-access-barrier candidate rows."},
        {"metric": "alb2002_access_candidate_outcome_promotion_ready_rows", "value": str(counts["alb2002_access_candidate_outcome_promotion_ready_rows"]), "interpretation": "ALB_2002 access candidate outcome rows ready for final promotion; should remain zero."},
        {"metric": "alb2002_access_candidate_current_decision", "value": str(counts["alb2002_access_candidate_current_decision"]), "interpretation": "Current ALB_2002 access candidate outcome decision."},
        {"metric": "alb2002_uhc_composite_candidate_household_rows", "value": str(counts["alb2002_uhc_composite_candidate_household_rows"]), "interpretation": "ALB_2002 temp-only composite UHC candidate rows."},
        {"metric": "alb2002_uhc_composite_candidate_che10_or_access_rows", "value": str(counts["alb2002_uhc_composite_candidate_che10_or_access_rows"]), "interpretation": "ALB_2002 temp-only CHE10-or-access candidate rows."},
        {"metric": "alb2002_uhc_composite_candidate_che25_or_access_rows", "value": str(counts["alb2002_uhc_composite_candidate_che25_or_access_rows"]), "interpretation": "ALB_2002 temp-only CHE25-or-access candidate rows."},
        {"metric": "alb2002_uhc_composite_candidate_both_che10_access_rows", "value": str(counts["alb2002_uhc_composite_candidate_both_che10_access_rows"]), "interpretation": "ALB_2002 temp-only both CHE10 and access-barrier candidate rows."},
        {"metric": "alb2002_uhc_composite_candidate_coping_rows", "value": str(counts["alb2002_uhc_composite_candidate_coping_rows"]), "interpretation": "ALB_2002 temp-only health-cost coping candidate rows."},
        {"metric": "alb2002_uhc_composite_candidate_outcome_promotion_ready_rows", "value": str(counts["alb2002_uhc_composite_candidate_outcome_promotion_ready_rows"]), "interpretation": "ALB_2002 composite UHC candidate rows ready for final promotion; should remain zero."},
        {"metric": "alb2002_uhc_composite_candidate_current_decision", "value": str(counts["alb2002_uhc_composite_candidate_current_decision"]), "interpretation": "Current ALB_2002 composite UHC candidate outcome decision."},
        {"metric": "alb2002_analysis_candidate_rows", "value": str(counts["alb2002_analysis_candidate_rows"]), "interpretation": "ALB_2002 temp-only joined analysis-candidate household rows."},
        {"metric": "alb2002_analysis_candidate_complete_candidate_gates", "value": str(counts["alb2002_analysis_candidate_complete_candidate_gates"]), "interpretation": "ALB_2002 analysis-candidate field families with complete observed coverage."},
        {"metric": "alb2002_analysis_candidate_missing_gates", "value": str(counts["alb2002_analysis_candidate_missing_gates"]), "interpretation": "ALB_2002 analysis-candidate field families with missing required coverage."},
        {"metric": "alb2002_analysis_candidate_data_write_ready_rows", "value": str(counts["alb2002_analysis_candidate_data_write_ready_rows"]), "interpretation": "ALB_2002 analysis-candidate rows allowed to be written to data/; should remain zero."},
        {"metric": "alb2002_analysis_candidate_current_decision", "value": str(counts["alb2002_analysis_candidate_current_decision"]), "interpretation": "Current ALB_2002 joined analysis-candidate decision."},
        {"metric": "alb2002_climate_centroid_input_rows", "value": str(counts["alb2002_climate_centroid_input_rows"]), "interpretation": "ALB_2002 observed district-month cells used for the temp-only climate centroid stress test."},
        {"metric": "alb2002_climate_centroid_exposure_rows", "value": str(counts["alb2002_climate_centroid_exposure_rows"]), "interpretation": "ALB_2002 temp-only NASA POWER district-centroid exposure rows."},
        {"metric": "alb2002_climate_centroid_nasa_api_rows", "value": str(counts["alb2002_climate_centroid_nasa_api_rows"]), "interpretation": "ALB_2002 district centroid API/cache manifest rows."},
        {"metric": "alb2002_climate_centroid_nasa_failed_rows", "value": str(counts["alb2002_climate_centroid_nasa_failed_rows"]), "interpretation": "ALB_2002 NASA POWER district centroid requests that failed."},
        {"metric": "alb2002_climate_centroid_precip_nonmissing_rows", "value": str(counts["alb2002_climate_centroid_precip_nonmissing_rows"]), "interpretation": "ALB_2002 centroid exposure rows with nonmissing precipitation summaries."},
        {"metric": "alb2002_climate_centroid_temp_nonmissing_rows", "value": str(counts["alb2002_climate_centroid_temp_nonmissing_rows"]), "interpretation": "ALB_2002 centroid exposure rows with nonmissing temperature summaries."},
        {"metric": "alb2002_climate_centroid_climate_linkage_ready_rows", "value": str(counts["alb2002_climate_centroid_climate_linkage_ready_rows"]), "interpretation": "ALB_2002 centroid exposure rows ready for promoted climate linkage; should remain zero."},
        {"metric": "alb2002_climate_centroid_data_write_ready_rows", "value": str(counts["alb2002_climate_centroid_data_write_ready_rows"]), "interpretation": "ALB_2002 centroid exposure rows allowed for data/ write; should remain zero."},
        {"metric": "alb2002_climate_shock_candidate_exposure_rows", "value": str(counts["alb2002_climate_shock_candidate_exposure_rows"]), "interpretation": "ALB_2002 temp-only climate shock diagnostic rows."},
        {"metric": "alb2002_climate_shock_candidate_reference_group_rows", "value": str(counts["alb2002_climate_shock_candidate_reference_group_rows"]), "interpretation": "ALB_2002 survey-month/window diagnostic reference groups."},
        {"metric": "alb2002_climate_shock_candidate_precip_z_nonmissing_rows", "value": str(counts["alb2002_climate_shock_candidate_precip_z_nonmissing_rows"]), "interpretation": "ALB_2002 diagnostic rainfall z-score rows."},
        {"metric": "alb2002_climate_shock_candidate_temp_z_nonmissing_rows", "value": str(counts["alb2002_climate_shock_candidate_temp_z_nonmissing_rows"]), "interpretation": "ALB_2002 diagnostic temperature z-score rows."},
        {"metric": "alb2002_climate_shock_candidate_low_rain_rows", "value": str(counts["alb2002_climate_shock_candidate_low_rain_rows"]), "interpretation": "ALB_2002 diagnostic low-rain rows."},
        {"metric": "alb2002_climate_shock_candidate_extreme_wet_rows", "value": str(counts["alb2002_climate_shock_candidate_extreme_wet_rows"]), "interpretation": "ALB_2002 diagnostic extreme-wet rows."},
        {"metric": "alb2002_climate_shock_candidate_extreme_heat_rows", "value": str(counts["alb2002_climate_shock_candidate_extreme_heat_rows"]), "interpretation": "ALB_2002 diagnostic extreme-heat rows."},
        {"metric": "alb2002_climate_shock_candidate_combined_stress_rows", "value": str(counts["alb2002_climate_shock_candidate_combined_stress_rows"]), "interpretation": "ALB_2002 diagnostic combined climate-stress rows; not accepted treatment variables."},
        {"metric": "alb2002_climate_shock_candidate_climate_linkage_ready_rows", "value": str(counts["alb2002_climate_shock_candidate_climate_linkage_ready_rows"]), "interpretation": "ALB_2002 shock diagnostic rows ready for promoted climate linkage; should remain zero."},
        {"metric": "alb2002_climate_shock_candidate_data_write_ready_rows", "value": str(counts["alb2002_climate_shock_candidate_data_write_ready_rows"]), "interpretation": "ALB_2002 shock diagnostic rows allowed for data/ write; should remain zero."},
        {"metric": "alb2002_climate_outcome_linked_candidate_rows", "value": str(counts["alb2002_climate_outcome_linked_candidate_rows"]), "interpretation": "ALB_2002 temp-only household-window climate/outcome linked candidate rows."},
        {"metric": "alb2002_climate_outcome_linked_candidate_household_rows", "value": str(counts["alb2002_climate_outcome_linked_candidate_household_rows"]), "interpretation": "ALB_2002 households represented in the linked candidate."},
        {"metric": "alb2002_climate_outcome_linked_candidate_window_rows", "value": str(counts["alb2002_climate_outcome_linked_candidate_window_rows"]), "interpretation": "Diagnostic exposure windows per household in the linked candidate."},
        {"metric": "alb2002_climate_outcome_linked_candidate_unmatched_rows", "value": str(counts["alb2002_climate_outcome_linked_candidate_unmatched_rows"]), "interpretation": "Linked candidate rows without a diagnostic climate window; should remain zero."},
        {"metric": "alb2002_climate_outcome_linked_candidate_precip_z_rows", "value": str(counts["alb2002_climate_outcome_linked_candidate_precip_z_rows"]), "interpretation": "ALB_2002 linked diagnostic rainfall z-score rows."},
        {"metric": "alb2002_climate_outcome_linked_candidate_temp_z_rows", "value": str(counts["alb2002_climate_outcome_linked_candidate_temp_z_rows"]), "interpretation": "ALB_2002 linked diagnostic temperature z-score rows."},
        {"metric": "alb2002_climate_outcome_linked_candidate_combined_stress_rows", "value": str(counts["alb2002_climate_outcome_linked_candidate_combined_stress_rows"]), "interpretation": "ALB_2002 linked diagnostic combined climate-stress rows; not accepted treatment variables."},
        {"metric": "alb2002_climate_outcome_linked_candidate_climate_linkage_ready_rows", "value": str(counts["alb2002_climate_outcome_linked_candidate_climate_linkage_ready_rows"]), "interpretation": "ALB_2002 linked rows ready for promoted climate linkage; should remain zero."},
        {"metric": "alb2002_climate_outcome_linked_candidate_outcome_promotion_ready_rows", "value": str(counts["alb2002_climate_outcome_linked_candidate_outcome_promotion_ready_rows"]), "interpretation": "ALB_2002 linked rows ready for outcome promotion; should remain zero."},
        {"metric": "alb2002_climate_outcome_linked_candidate_data_write_ready_rows", "value": str(counts["alb2002_climate_outcome_linked_candidate_data_write_ready_rows"]), "interpretation": "ALB_2002 linked rows allowed for data/ write; should remain zero."},
        {"metric": "alb2002_linked_candidate_descriptive_input_rows", "value": str(counts["alb2002_linked_candidate_descriptive_input_rows"]), "interpretation": "ALB_2002 temp-only linked household-window rows screened descriptively."},
        {"metric": "alb2002_linked_candidate_descriptive_household_rows", "value": str(counts["alb2002_linked_candidate_descriptive_household_rows"]), "interpretation": "Deduplicated ALB_2002 households used for candidate outcome rates."},
        {"metric": "alb2002_linked_candidate_descriptive_cell_rows", "value": str(counts["alb2002_linked_candidate_descriptive_cell_rows"]), "interpretation": "ALB_2002 linked-candidate descriptive screen cells; not promoted descriptive diagnostics."},
        {"metric": "alb2002_linked_candidate_descriptive_combined_stress_rows", "value": str(counts["alb2002_linked_candidate_descriptive_combined_stress_rows"]), "interpretation": "Long rows with diagnostic combined climate-stress flag in the descriptive screen."},
        {"metric": "alb2002_linked_candidate_descriptive_climate_linkage_ready_rows", "value": str(counts["alb2002_linked_candidate_descriptive_climate_linkage_ready_rows"]), "interpretation": "ALB_2002 descriptive-screen rows ready for promoted climate linkage; should remain zero."},
        {"metric": "alb2002_linked_candidate_descriptive_data_write_ready_rows", "value": str(counts["alb2002_linked_candidate_descriptive_data_write_ready_rows"]), "interpretation": "ALB_2002 descriptive-screen rows allowed for data/ write; should remain zero."},
        {"metric": "alb2002_weight_design_evidence_audit_rows", "value": str(counts["alb2002_weight_design_evidence_audit"]), "interpretation": "ALB_2002 household weight/design evidence audit rows."},
        {"metric": "alb2002_weight_design_source_page_flag_rows", "value": str(counts["alb2002_weight_design_source_page_flag_rows"]), "interpretation": "World Bank study-page weight/design source flags found by the audit."},
        {"metric": "alb2002_weight_design_raw_weight_file_rows", "value": str(counts["alb2002_weight_design_raw_weight_file_rows"]), "interpretation": "Rows read from the ALB_2002 household weight file."},
        {"metric": "alb2002_weight_design_positive_weight_rows", "value": str(counts["alb2002_weight_design_positive_weight_rows"]), "interpretation": "Rows with positive ALB_2002 household weights."},
        {"metric": "alb2002_weight_design_candidate_key_match_rows", "value": str(counts["alb2002_weight_design_candidate_key_match_rows"]), "interpretation": "ALB_2002 household-weight rows matching the temp core candidate by key."},
        {"metric": "alb2002_weight_design_distinct_psu_rows", "value": str(counts["alb2002_weight_design_distinct_psu_rows"]), "interpretation": "Distinct PSU values observed in the ALB_2002 household weight file."},
        {"metric": "alb2002_weight_design_distinct_stratum_rows", "value": str(counts["alb2002_weight_design_distinct_stratum_rows"]), "interpretation": "Distinct stratum values observed in the ALB_2002 household weight file."},
        {"metric": "alb2002_weight_design_weighted_inference_ready_rows", "value": str(counts["alb2002_weight_design_weighted_inference_ready_rows"]), "interpretation": "ALB_2002 rows ready for promoted weighted inference; should remain zero."},
        {"metric": "alb2002_weight_design_harmonized_promotion_ready_rows", "value": str(counts["alb2002_weight_design_harmonized_promotion_ready_rows"]), "interpretation": "ALB_2002 weight/design rows ready for harmonized data promotion; should remain zero."},
        {"metric": "alb2002_weight_design_current_decision", "value": str(counts["alb2002_weight_design_current_decision"]), "interpretation": "Current ALB_2002 weight/design evidence decision."},
        {"metric": "alb2002_sample_design_documentation_ready_rows", "value": str(counts["alb2002_sample_design_documentation_ready_rows"]), "interpretation": "ALB_2002 official sample-design documentation ready; not a data-promotion pass."},
        {"metric": "alb2002_sample_design_raw_design_concordance_rows", "value": str(counts["alb2002_sample_design_raw_design_concordance_rows"]), "interpretation": "ALB_2002 raw count evidence concordant with official sample-design documentation."},
        {"metric": "alb2002_sample_design_weighted_inference_ready_rows", "value": str(counts["alb2002_sample_design_weighted_inference_ready_rows"]), "interpretation": "ALB_2002 weighted inference ready rows after sample-design audit; should remain zero."},
        {"metric": "alb2002_sample_design_current_decision", "value": str(counts["alb2002_sample_design_current_decision"]), "interpretation": "Current ALB_2002 sample-design documentation decision."},
        {"metric": "alb2002_minimum_recipe_promotion_action_rows", "value": str(counts["alb2002_minimum_recipe_promotion_action_rows"]), "interpretation": "ALB_2002 minimum recipe promotion action rows."},
        {"metric": "alb2002_minimum_recipe_promotion_gate_rows", "value": str(counts["alb2002_minimum_recipe_promotion_gate_rows"]), "interpretation": "ALB_2002 minimum recipe promotion gate rows."},
        {"metric": "alb2002_minimum_recipe_promotion_blocked_gates", "value": str(counts["alb2002_minimum_recipe_promotion_blocked_gates"]), "interpretation": "ALB_2002 minimum recipe gates still blocked."},
        {"metric": "alb2002_minimum_recipe_promotion_weight_positive_rows", "value": str(counts["alb2002_minimum_recipe_promotion_weight_positive_rows"]), "interpretation": "Positive ALB_2002 household-weight rows surfaced in the promotion packet."},
        {"metric": "alb2002_minimum_recipe_promotion_weight_key_match_rows", "value": str(counts["alb2002_minimum_recipe_promotion_weight_key_match_rows"]), "interpretation": "ALB_2002 household-weight key matches surfaced in the promotion packet."},
        {"metric": "alb2002_minimum_recipe_promotion_weighted_inference_ready_rows", "value": str(counts["alb2002_minimum_recipe_promotion_weighted_inference_ready_rows"]), "interpretation": "ALB_2002 rows ready for promoted weighted inference in the promotion packet; should remain zero."},
        {"metric": "alb2002_minimum_recipe_promotion_harmonized_ready_rows", "value": str(counts["alb2002_minimum_recipe_promotion_harmonized_ready_rows"]), "interpretation": "ALB_2002 rows ready for harmonized data promotion; should remain zero."},
        {"metric": "alb2002_minimum_recipe_promotion_outcome_ready_rows", "value": str(counts["alb2002_minimum_recipe_promotion_outcome_ready_rows"]), "interpretation": "ALB_2002 rows ready for outcome promotion; should remain zero."},
        {"metric": "alb2002_minimum_recipe_promotion_sdg382_ready_rows", "value": str(counts["alb2002_minimum_recipe_promotion_sdg382_ready_rows"]), "interpretation": "ALB_2002 rows ready for SDG 3.8.2 promotion; should remain zero."},
        {"metric": "alb2002_minimum_recipe_promotion_climate_linkage_ready_rows", "value": str(counts["alb2002_minimum_recipe_promotion_climate_linkage_ready_rows"]), "interpretation": "ALB_2002 rows ready for climate linkage after minimum recipe gates; should remain zero."},
        {"metric": "alb2002_district_climate_crosswalk_rows", "value": str(counts["alb2002_district_climate_crosswalk_template"]), "interpretation": "ALB_2002 district climate crosswalk template rows."},
        {"metric": "alb2002_boundary_name_match_rows", "value": str(counts["alb2002_boundary_name_match_audit"]), "interpretation": "ALB_2002 survey district rows compared to public boundary names."},
        {"metric": "alb2002_boundary_name_match_unmatched_survey_rows", "value": str(counts["alb2002_boundary_name_match_unmatched_survey_rows"]), "interpretation": "ALB_2002 survey district rows without a current public boundary-name match."},
        {"metric": "alb2002_boundary_name_match_duplicate_boundary_name_keys", "value": str(counts["alb2002_boundary_name_match_duplicate_boundary_name_keys"]), "interpretation": "Duplicate boundary-name keys in the public current ADM2 GeoJSON."},
        {"metric": "alb2002_boundary_name_match_historical_year_ready_rows", "value": str(counts["alb2002_boundary_name_match_historical_year_ready_rows"]), "interpretation": "ALB_2002 boundary-name rows ready for 2002 historical crosswalk validation; should remain zero."},
        {"metric": "alb2002_boundary_name_match_climate_linkage_ready_rows", "value": str(counts["alb2002_boundary_name_match_climate_linkage_ready_rows"]), "interpretation": "ALB_2002 boundary-name rows ready for climate-linkage promotion; should remain zero."},
        {"metric": "alb2002_boundary_resource_search_candidate_rows", "value": str(counts["alb2002_boundary_resource_search_candidate_rows"]), "interpretation": "ALB_2002 public boundary/gazetteer resources parsed or probed."},
        {"metric": "alb2002_boundary_resource_search_complete_name_coverage_rows", "value": str(counts["alb2002_boundary_resource_search_complete_name_coverage_rows"]), "interpretation": "Boundary resources with complete ALB_2002 district-name coverage after documented repairs."},
        {"metric": "alb2002_boundary_resource_search_exact_unit_count_rows", "value": str(counts["alb2002_boundary_resource_search_exact_unit_count_rows"]), "interpretation": "Boundary resources with feature and distinct-key counts matching the 36 ALB_2002 district groups."},
        {"metric": "alb2002_boundary_resource_search_2002_historical_ready_rows", "value": str(counts["alb2002_boundary_resource_search_2002_historical_ready_rows"]), "interpretation": "Boundary resources verified as 2002 historical inputs; should remain zero."},
        {"metric": "alb2002_boundary_resource_search_climate_linkage_ready_rows", "value": str(counts["alb2002_boundary_resource_search_climate_linkage_ready_rows"]), "interpretation": "Boundary resources ready for climate-linkage promotion; should remain zero."},
        {"metric": "alb2002_boundary_geometry_feature_rows", "value": str(counts["alb2002_boundary_geometry_feature_rows"]), "interpretation": "Features parsed in the best ALB_2002 boundary lead."},
        {"metric": "alb2002_boundary_geometry_coordinate_structure_ok_rows", "value": str(counts["alb2002_boundary_geometry_coordinate_structure_ok_rows"]), "interpretation": "Boundary features with parseable coordinate structure; not topology validation."},
        {"metric": "alb2002_boundary_geometry_metadata_boundary_year", "value": str(counts["alb2002_boundary_geometry_metadata_boundary_year"]), "interpretation": "Boundary year reported by the candidate source metadata."},
        {"metric": "alb2002_boundary_geometry_boundary_year_matches_2002_rows", "value": str(counts["alb2002_boundary_geometry_boundary_year_matches_2002_rows"]), "interpretation": "Candidate source rows whose metadata directly verifies a 2002 boundary vintage; should remain zero."},
        {"metric": "alb2002_boundary_geometry_historical_2002_boundary_ready_rows", "value": str(counts["alb2002_boundary_geometry_historical_2002_boundary_ready_rows"]), "interpretation": "Geometry/provenance rows ready as verified 2002 historical boundary inputs; should remain zero."},
        {"metric": "alb2002_boundary_geometry_climate_linkage_ready_rows", "value": str(counts["alb2002_boundary_geometry_climate_linkage_ready_rows"]), "interpretation": "Geometry/provenance rows ready for climate-linkage promotion; should remain zero."},
        {"metric": "alb2002_boundary_manual_verification_action_rows", "value": str(counts["alb2002_boundary_manual_verification_action_rows"]), "interpretation": "Source/action rows in the ALB_2002 manual boundary verification packet."},
        {"metric": "alb2002_boundary_manual_verification_gate_rows", "value": str(counts["alb2002_boundary_manual_verification_gate_rows"]), "interpretation": "Pass/fail gate rows in the ALB_2002 manual boundary verification packet."},
        {"metric": "alb2002_boundary_manual_verification_blocked_gates", "value": str(counts["alb2002_boundary_manual_verification_blocked_gates"]), "interpretation": "Manual boundary verification gates still blocked."},
        {"metric": "alb2002_boundary_manual_verification_pre2011_digital_map_absence_rows", "value": str(counts["alb2002_boundary_manual_verification_pre2011_digital_map_absence_rows"]), "interpretation": "Negative-evidence rows documenting pre-2011 national digital map absence."},
        {"metric": "alb2002_boundary_manual_verification_climate_linkage_ready_rows", "value": str(counts["alb2002_boundary_manual_verification_climate_linkage_ready_rows"]), "interpretation": "Manual verification rows ready for climate-linkage promotion; should remain zero."},
        {"metric": "alb2002_boundary_manual_source_followup_rows", "value": str(counts["alb2002_boundary_manual_source_followup_rows"]), "interpretation": "Manual-source follow-up rows for ALB_2002 boundary leads."},
        {"metric": "alb2002_boundary_manual_source_followup_conclusive_blocker_rows", "value": str(counts["alb2002_boundary_manual_source_followup_conclusive_blocker_rows"]), "interpretation": "ALB_2002 source leads with documented source-specific blockers after follow-up."},
        {"metric": "alb2002_boundary_manual_source_followup_district_level_ready_rows", "value": str(counts["alb2002_boundary_manual_source_followup_district_level_ready_rows"]), "interpretation": "ALB_2002 source leads verified as district-level-ready after follow-up; should remain zero."},
        {"metric": "alb2002_boundary_manual_source_followup_climate_linkage_ready_rows", "value": str(counts["alb2002_boundary_manual_source_followup_climate_linkage_ready_rows"]), "interpretation": "ALB_2002 source leads ready for climate-linkage promotion after follow-up; should remain zero."},
        {"metric": "alb2002_boundary_manual_source_followup_unece_pre2011_map_status", "value": str(counts["alb2002_boundary_manual_source_followup_unece_pre2011_map_status"]), "interpretation": "UNECE/INSTAT pre-2011 national digital map availability blocker status."},
        {"metric": "alb2002_gadm_boundary_lead_candidate_rows", "value": str(counts["alb2002_gadm_boundary_lead_candidate_rows"]), "interpretation": "GADM Albania ADM2 source candidates audited for ALB_2002 district-boundary linkage."},
        {"metric": "alb2002_gadm36_adm2_row_count", "value": str(counts["alb2002_gadm36_adm2_row_count"]), "interpretation": "GADM 3.6 Albania ADM2 feature rows."},
        {"metric": "alb2002_gadm36_distinct_normalized_key_count", "value": str(counts["alb2002_gadm36_distinct_normalized_key_count"]), "interpretation": "GADM 3.6 normalized keys after documented district-name repairs."},
        {"metric": "alb2002_gadm36_complete_name_coverage_rows", "value": str(counts["alb2002_gadm36_complete_name_coverage_rows"]), "interpretation": "GADM 3.6 name-coverage flag for all 36 ALB_2002 district keys."},
        {"metric": "alb2002_gadm36_duplicate_boundary_key_count", "value": str(counts["alb2002_gadm36_duplicate_boundary_key_count"]), "interpretation": "Duplicated GADM 3.6 normalized keys that block automatic promotion."},
        {"metric": "alb2002_gadm_boundary_lead_climate_linkage_ready_rows", "value": str(counts["alb2002_gadm_boundary_lead_climate_linkage_ready_rows"]), "interpretation": "GADM boundary lead rows ready for climate-linkage promotion; should remain zero."},
        {"metric": "alb2002_climate_linkage_ready_rows", "value": str(counts["alb2002_climate_linkage_ready_rows"]), "interpretation": "ALB_2002 district rows ready for climate linkage; should remain zero."},
        {"metric": "alb2012_household_core_candidate_rows", "value": str(counts["alb2012_household_core_candidate"]), "interpretation": "ALB_2012 temp household core candidate rows."},
        {"metric": "alb2012_household_core_recipe_ready_rows", "value": str(counts["alb2012_household_core_recipe_ready_rows"]), "interpretation": "ALB_2012 household core rows ready for data promotion; should remain zero."},
        {"metric": "alb2012_climate_linkage_ready_rows", "value": str(counts["alb2012_climate_linkage_ready_rows"]), "interpretation": "ALB_2012 rows ready for climate linkage; should remain zero."},
        {"metric": "alb2012_provisional_outcome_rows", "value": str(counts["alb2012_provisional_outcome_feasibility_audit"]), "interpretation": "ALB_2012 provisional outcome feasibility audit rows."},
        {"metric": "alb2012_provisional_outcome_ready_rows", "value": str(counts["alb2012_provisional_outcome_ready_rows"]), "interpretation": "ALB_2012 provisional outcome rows ready for data promotion; should remain zero."},
        {"metric": "alb2012_outcome_semantics_raw_value_rows", "value": str(counts["alb2012_outcome_semantics_raw_value_audit"]), "interpretation": "ALB_2012 raw outcome-semantics value audit rows."},
        {"metric": "alb2012_outcome_semantics_outcome_ready_rows", "value": str(counts["alb2012_outcome_semantics_outcome_ready_rows"]), "interpretation": "ALB_2012 raw outcome-semantics rows ready for final promotion; should remain zero."},
        {"metric": "alb2012_outcome_semantics_sdg382_ready_rows", "value": str(counts["alb2012_outcome_semantics_sdg382_ready_rows"]), "interpretation": "ALB_2012 raw outcome-semantics rows ready for SDG 3.8.2 construction; should remain zero."},
        {"metric": "alb2012_outcome_semantics_climate_linkage_ready_rows", "value": str(counts["alb2012_outcome_semantics_climate_linkage_ready_rows"]), "interpretation": "ALB_2012 raw outcome-semantics rows ready for climate linkage; should remain zero."},
        {"metric": "alb2012_timing_geography_rows", "value": str(counts["alb2012_timing_geography_exhaustive_audit"]), "interpretation": "ALB_2012 timing/geography exhaustive audit rows."},
        {"metric": "alb2012_timing_geography_climate_linkage_ready_rows", "value": str(counts["alb2012_timing_geography_climate_linkage_ready_rows"]), "interpretation": "ALB_2012 timing/geography rows ready for climate linkage; should remain zero."},
        {"metric": "alb2012_questionnaire_timing_field_rows", "value": str(counts["alb2012_questionnaire_timing_field_rows"]), "interpretation": "ALB_2012 questionnaire control-sheet timing field rows."},
        {"metric": "alb2012_questionnaire_timing_raw_gap_rows", "value": str(counts["alb2012_questionnaire_timing_raw_gap_rows"]), "interpretation": "ALB_2012 raw SPSS timing-like rows that do not verify household interview timing."},
        {"metric": "alb2012_questionnaire_timing_raw_verified_interview_timing_rows", "value": str(counts["alb2012_questionnaire_timing_raw_verified_interview_timing_rows"]), "interpretation": "ALB_2012 verified raw household interview timing rows; should remain zero."},
        {"metric": "alb2012_questionnaire_timing_climate_linkage_ready_rows", "value": str(counts["alb2012_questionnaire_timing_climate_linkage_ready_rows"]), "interpretation": "ALB_2012 questionnaire timing rows ready for climate-linkage promotion; should remain zero."},
        {"metric": "albania_legacy_questionnaire_present_files", "value": str(counts["albania_legacy_questionnaire_present_files"]), "interpretation": "ALB_2002/2005/2008 legacy questionnaire files present locally."},
        {"metric": "albania_legacy_questionnaire_read_ok_files", "value": str(counts["albania_legacy_questionnaire_read_ok_files"]), "interpretation": "Legacy questionnaire .xls files readable in the current environment."},
        {"metric": "albania_legacy_questionnaire_missing_reader_blocked_files", "value": str(counts["albania_legacy_questionnaire_missing_reader_blocked_files"]), "interpretation": "Legacy questionnaire files blocked by missing .xls reader/converter."},
        {"metric": "albania_legacy_questionnaire_climate_linkage_ready_rows", "value": str(counts["albania_legacy_questionnaire_climate_linkage_ready_rows"]), "interpretation": "Legacy questionnaire rows ready for climate-linkage promotion; should remain zero."},
        {"metric": "albania_legacy_questionnaire_timing_field_rows", "value": str(counts["albania_legacy_questionnaire_timing_field_rows"]), "interpretation": "Legacy questionnaire timing/control field rows."},
        {"metric": "albania_legacy_questionnaire_timing_raw_gap_rows", "value": str(counts["albania_legacy_questionnaire_timing_raw_gap_rows"]), "interpretation": "Legacy raw SPSS timing-like rows reviewed after questionnaire timing audit."},
        {"metric": "albania_legacy_questionnaire_timing_raw_verified_interview_timing_rows", "value": str(counts["albania_legacy_questionnaire_timing_raw_verified_interview_timing_rows"]), "interpretation": "Verified raw household interview timing rows across ALB_2002/2005/2008."},
        {"metric": "albania_legacy_questionnaire_timing_climate_linkage_ready_rows", "value": str(counts["albania_legacy_questionnaire_timing_climate_linkage_ready_rows"]), "interpretation": "Legacy questionnaire timing rows ready for climate-linkage promotion; should remain zero."},
        {"metric": "alb2005_provisional_outcome_feasibility_rows", "value": str(counts["alb2005_provisional_outcome_feasibility_audit"]), "interpretation": "ALB_2005 provisional outcome feasibility audit rows."},
        {"metric": "alb2005_provisional_outcome_ready_rows", "value": str(counts["alb2005_provisional_outcome_ready_rows"]), "interpretation": "ALB_2005 provisional outcome rows ready for final promotion; should remain zero."},
        {"metric": "alb2005_outcome_semantics_raw_value_rows", "value": str(counts["alb2005_outcome_semantics_raw_value_audit"]), "interpretation": "ALB_2005 raw outcome-semantics value audit rows."},
        {"metric": "alb2005_outcome_semantics_outcome_ready_rows", "value": str(counts["alb2005_outcome_semantics_outcome_ready_rows"]), "interpretation": "ALB_2005 raw outcome-semantics rows ready for final promotion; should remain zero."},
        {"metric": "alb2005_outcome_semantics_sdg382_ready_rows", "value": str(counts["alb2005_outcome_semantics_sdg382_ready_rows"]), "interpretation": "ALB_2005 raw outcome-semantics rows ready for SDG 3.8.2 construction; should remain zero."},
        {"metric": "alb2005_outcome_semantics_climate_linkage_ready_rows", "value": str(counts["alb2005_outcome_semantics_climate_linkage_ready_rows"]), "interpretation": "ALB_2005 raw outcome-semantics rows ready for climate linkage; should remain zero."},
        {"metric": "alb2005_timing_geography_exhaustive_rows", "value": str(counts["alb2005_timing_geography_exhaustive_audit"]), "interpretation": "ALB_2005 timing/geography exhaustive audit rows."},
        {"metric": "alb2005_climate_linkage_ready_rows", "value": str(counts["alb2005_climate_linkage_ready_rows"]), "interpretation": "ALB_2005 rows ready for climate linkage; should remain zero until timing/geography are verified."},
        {"metric": "alb2005_timing_geography_source_search_rows", "value": str(counts["alb2005_timing_geography_source_search_rows"]), "interpretation": "ALB_2005 timing/geography source-search audit rows."},
        {"metric": "alb2005_timing_geography_source_search_local_files_scanned", "value": str(counts["alb2005_timing_geography_source_search_local_files_scanned"]), "interpretation": "Local ALB_2005 file rows scanned for timing/geography source evidence."},
        {"metric": "alb2005_timing_geography_source_search_local_variables_scanned", "value": str(counts["alb2005_timing_geography_source_search_local_variables_scanned"]), "interpretation": "Local ALB_2005 raw-variable rows scanned for timing/geography source evidence."},
        {"metric": "alb2005_timing_geography_source_search_verified_household_timing_rows", "value": str(counts["alb2005_timing_geography_source_search_verified_household_timing_rows"]), "interpretation": "Verified ALB_2005 household interview timing rows in source-search evidence; should remain zero."},
        {"metric": "alb2005_timing_geography_source_search_coordinate_candidate_rows", "value": str(counts["alb2005_timing_geography_source_search_coordinate_candidate_rows"]), "interpretation": "ALB_2005 coordinate/GPS candidate rows in source-search evidence; should remain zero."},
        {"metric": "alb2005_timing_geography_source_search_partial_district_name_nonmissing_rows", "value": str(counts["alb2005_timing_geography_source_search_partial_district_name_nonmissing_rows"]), "interpretation": "Partial ALB_2005 district-name rows observed upstream."},
        {"metric": "alb2005_timing_geography_source_search_partial_district_code_nonmissing_rows", "value": str(counts["alb2005_timing_geography_source_search_partial_district_code_nonmissing_rows"]), "interpretation": "Partial ALB_2005 district-code rows observed upstream."},
        {"metric": "alb2005_timing_geography_source_search_climate_linkage_ready_rows", "value": str(counts["alb2005_timing_geography_source_search_climate_linkage_ready_rows"]), "interpretation": "ALB_2005 timing/geography source-search rows ready for climate linkage; should remain zero."},
        {"metric": "alb2005_required_value_key_rows", "value": str(counts["alb2005_required_value_key_audit"]), "interpretation": "ALB_2005 required value/key audit rows."},
        {"metric": "alb2005_required_value_key_recipe_ready_rows", "value": str(counts["alb2005_required_value_key_recipe_ready_rows"]), "interpretation": "ALB_2005 rows promoted to a harmonization recipe by required value/key audit; should remain zero."},
        {"metric": "alb2005_required_value_key_not_promoted_rows", "value": str(counts["alb2005_required_value_key_not_promoted_rows"]), "interpretation": "ALB_2005 required value/key rows kept fail-closed."},
        {"metric": "alb2005_required_value_key_total_consumption_nonmissing_rows", "value": str(counts["alb2005_required_value_key_total_consumption_nonmissing_rows"]), "interpretation": "Nonmissing ALB_2005 total-consumption raw values in poverty.sav."},
        {"metric": "alb2005_required_value_key_oop_4w_household_positive_rows", "value": str(counts["alb2005_required_value_key_oop_4w_household_positive_rows"]), "interpretation": "Audit-only positive ALB_2005 four-week OOP household sums; not final outcomes."},
        {"metric": "alb2005_required_value_key_oop_12m_household_positive_rows", "value": str(counts["alb2005_required_value_key_oop_12m_household_positive_rows"]), "interpretation": "Audit-only positive ALB_2005 twelve-month OOP household sums; not final outcomes."},
        {"metric": "alb2005_required_value_key_district_code_nonmissing_rows", "value": str(counts["alb2005_required_value_key_district_code_nonmissing_rows"]), "interpretation": "Nonmissing partial ALB_2005 district-code rows."},
        {"metric": "alb2005_required_value_key_interview_timing_verified_rows", "value": str(counts["alb2005_required_value_key_interview_timing_verified_rows"]), "interpretation": "Verified ALB_2005 household interview timing rows; should remain zero."},
        {"metric": "alb2005_required_value_key_coordinate_ready_rows", "value": str(counts["alb2005_required_value_key_coordinate_ready_rows"]), "interpretation": "Verified ALB_2005 coordinate-ready rows; should remain zero."},
        {"metric": "alb2005_required_value_key_climate_linkage_ready_rows", "value": str(counts["alb2005_required_value_key_climate_linkage_ready_rows"]), "interpretation": "ALB_2005 climate-linkage-ready rows after required value/key audit; should remain zero."},
        {"metric": "alb2005_health_questionnaire_semantics_rows", "value": str(counts["alb2005_health_questionnaire_semantics_audit"]), "interpretation": "ALB_2005 health questionnaire semantics audit rows."},
        {"metric": "alb2005_health_questionnaire_oop_item_rows", "value": str(counts["alb2005_health_questionnaire_oop_item_rows"]), "interpretation": "Questionnaire-backed ALB_2005 OOP payment item rows."},
        {"metric": "alb2005_health_questionnaire_old_lek_unit_rows", "value": str(counts["alb2005_health_questionnaire_old_lek_unit_rows"]), "interpretation": "ALB_2005 health questionnaire rows with old-lek unit evidence."},
        {"metric": "alb2005_health_questionnaire_access_rows", "value": str(counts["alb2005_health_questionnaire_access_rows"]), "interpretation": "ALB_2005 questionnaire access/barrier rows."},
        {"metric": "alb2005_health_questionnaire_cost_barrier_rows", "value": str(counts["alb2005_health_questionnaire_cost_barrier_rows"]), "interpretation": "ALB_2005 access rows with cost-barrier codes."},
        {"metric": "alb2005_health_questionnaire_recipe_ready_rows", "value": str(counts["alb2005_health_questionnaire_recipe_ready_rows"]), "interpretation": "ALB_2005 questionnaire-semantics rows ready for recipe promotion; should remain zero."},
        {"metric": "alb2005_health_questionnaire_outcome_ready_rows", "value": str(counts["alb2005_health_questionnaire_outcome_ready_rows"]), "interpretation": "ALB_2005 questionnaire-semantics rows ready for outcome construction; should remain zero."},
        {"metric": "alb2005_health_questionnaire_climate_linkage_ready_rows", "value": str(counts["alb2005_health_questionnaire_climate_linkage_ready_rows"]), "interpretation": "ALB_2005 questionnaire-semantics rows ready for climate linkage; should remain zero."},
        {"metric": "alb2005_oop_aggregation_policy_rows", "value": str(counts["alb2005_oop_aggregation_policy_rows"]), "interpretation": "ALB_2005 OOP aggregation policy stress-test rows."},
        {"metric": "alb2005_oop_aggregation_policy_household_rows", "value": str(counts["alb2005_oop_aggregation_policy_household_rows"]), "interpretation": "Households in the ALB_2005 OOP aggregation policy audit."},
        {"metric": "alb2005_oop_aggregation_policy_total_consumption_rows", "value": str(counts["alb2005_oop_aggregation_policy_total_consumption_rows"]), "interpretation": "ALB_2005 households with positive total-consumption denominator in the stress test."},
        {"metric": "alb2005_oop_aggregation_policy_outcome_ready_rows", "value": str(counts["alb2005_oop_aggregation_policy_outcome_ready_rows"]), "interpretation": "ALB_2005 OOP policy rows ready for final outcome promotion; should remain zero."},
        {"metric": "alb2005_oop_aggregation_policy_recipe_ready_rows", "value": str(counts["alb2005_oop_aggregation_policy_recipe_ready_rows"]), "interpretation": "ALB_2005 OOP policy rows ready for recipe promotion; should remain zero."},
        {"metric": "alb2005_oop_aggregation_policy_climate_linkage_ready_rows", "value": str(counts["alb2005_oop_aggregation_policy_climate_linkage_ready_rows"]), "interpretation": "ALB_2005 OOP policy rows ready for climate linkage; should remain zero."},
        {"metric": "alb2005_skip_missing_semantics_rows", "value": str(counts["alb2005_skip_missing_semantics_rows"]), "interpretation": "ALB_2005 skip/missing semantics audit rows."},
        {"metric": "alb2005_skip_missing_payment_nonmissing_when_not_triggered_rows", "value": str(counts["alb2005_skip_missing_payment_nonmissing_when_not_triggered_rows"]), "interpretation": "Payment downstream nonmissing rows under negative triggers; should remain zero."},
        {"metric": "alb2005_skip_missing_payment_positive_when_not_triggered_rows", "value": str(counts["alb2005_skip_missing_payment_positive_when_not_triggered_rows"]), "interpretation": "Payment downstream positive rows under negative triggers; should remain zero."},
        {"metric": "alb2005_skip_missing_payment_zero_or_missing_when_triggered_rows", "value": str(counts["alb2005_skip_missing_payment_zero_or_missing_when_triggered_rows"]), "interpretation": "Triggered payment rows with no positive payment; requires zero/missing-code review before promotion."},
        {"metric": "alb2005_skip_missing_recipe_ready_rows", "value": str(counts["alb2005_skip_missing_recipe_ready_rows"]), "interpretation": "ALB_2005 skip/missing rows ready for recipe promotion; should remain zero."},
        {"metric": "alb2005_skip_missing_outcome_ready_rows", "value": str(counts["alb2005_skip_missing_outcome_ready_rows"]), "interpretation": "ALB_2005 skip/missing rows ready for outcome promotion; should remain zero."},
        {"metric": "alb2005_skip_missing_climate_linkage_ready_rows", "value": str(counts["alb2005_skip_missing_climate_linkage_ready_rows"]), "interpretation": "ALB_2005 skip/missing rows ready for climate linkage; should remain zero."},
        {"metric": "alb2005_consumption_oop_unit_period_rows", "value": str(counts["alb2005_consumption_oop_unit_period_rows"]), "interpretation": "ALB_2005 consumption/OOP unit-period audit rows."},
        {"metric": "alb2005_consumption_oop_unit_period_total_consumption_positive_rows", "value": str(counts["alb2005_consumption_oop_unit_period_total_consumption_positive_rows"]), "interpretation": "Positive total-consumption rows observed in the ALB_2005 unit-period audit."},
        {"metric": "alb2005_consumption_oop_unit_period_rcons_positive_rows", "value": str(counts["alb2005_consumption_oop_unit_period_rcons_positive_rows"]), "interpretation": "Positive per-capita consumption rows observed in the ALB_2005 unit-period audit."},
        {"metric": "alb2005_consumption_oop_unit_period_metadata_old_lek_rows", "value": str(counts["alb2005_consumption_oop_unit_period_metadata_old_lek_rows"]), "interpretation": "Public metadata aggregate labels with old-lek evidence."},
        {"metric": "alb2005_consumption_oop_unit_period_oop_old_lek_rows", "value": str(counts["alb2005_consumption_oop_unit_period_oop_old_lek_rows"]), "interpretation": "Questionnaire OOP rows with old-lek unit evidence."},
        {"metric": "alb2005_consumption_oop_unit_period_four_week_oop_rows", "value": str(counts["alb2005_consumption_oop_unit_period_four_week_oop_rows"]), "interpretation": "Questionnaire OOP rows with four-week recall."},
        {"metric": "alb2005_consumption_oop_unit_period_twelve_month_oop_rows", "value": str(counts["alb2005_consumption_oop_unit_period_twelve_month_oop_rows"]), "interpretation": "Questionnaire OOP rows with 12-month recall."},
        {"metric": "alb2005_consumption_oop_unit_period_sdg382_ready_rows", "value": str(counts["alb2005_consumption_oop_unit_period_sdg382_ready_rows"]), "interpretation": "ALB_2005 unit-period rows ready for SDG 3.8.2 denominator construction; should remain zero."},
        {"metric": "alb2005_consumption_oop_unit_period_recipe_ready_rows", "value": str(counts["alb2005_consumption_oop_unit_period_recipe_ready_rows"]), "interpretation": "ALB_2005 unit-period rows ready for recipe promotion; should remain zero."},
        {"metric": "alb2005_consumption_oop_unit_period_outcome_ready_rows", "value": str(counts["alb2005_consumption_oop_unit_period_outcome_ready_rows"]), "interpretation": "ALB_2005 unit-period rows ready for outcome promotion; should remain zero."},
        {"metric": "alb2005_consumption_oop_unit_period_climate_linkage_ready_rows", "value": str(counts["alb2005_consumption_oop_unit_period_climate_linkage_ready_rows"]), "interpretation": "ALB_2005 unit-period rows ready for climate linkage; should remain zero."},
        {"metric": "alb2005_consumption_aggregate_crosswalk_rows", "value": str(counts["alb2005_consumption_aggregate_crosswalk_rows"]), "interpretation": "ALB_2005 aggregate metadata/local raw crosswalk audit rows."},
        {"metric": "alb2005_consumption_aggregate_crosswalk_metadata_rows", "value": str(counts["alb2005_consumption_aggregate_crosswalk_metadata_rows"]), "interpretation": "Public metadata aggregate/component variables checked against local poverty.sav."},
        {"metric": "alb2005_consumption_aggregate_crosswalk_metadata_present_local_rows", "value": str(counts["alb2005_consumption_aggregate_crosswalk_metadata_present_local_rows"]), "interpretation": "Checked public metadata aggregate/component variables present locally."},
        {"metric": "alb2005_consumption_aggregate_crosswalk_metadata_absent_local_rows", "value": str(counts["alb2005_consumption_aggregate_crosswalk_metadata_absent_local_rows"]), "interpretation": "Checked public metadata aggregate/component variables absent locally."},
        {"metric": "alb2005_consumption_aggregate_crosswalk_totcons_positive_rows", "value": str(counts["alb2005_consumption_aggregate_crosswalk_totcons_positive_rows"]), "interpretation": "Positive local totcons rows in the aggregate crosswalk audit."},
        {"metric": "alb2005_consumption_aggregate_crosswalk_totcons05_local_rows", "value": str(counts["alb2005_consumption_aggregate_crosswalk_totcons05_local_rows"]), "interpretation": "Local totcons05 rows in poverty.sav; should remain zero in current extract."},
        {"metric": "alb2005_consumption_aggregate_crosswalk_component_formula_reconstructable_rows", "value": str(counts["alb2005_consumption_aggregate_crosswalk_component_formula_reconstructable_rows"]), "interpretation": "Whether public-metadata aggregate formula components are all locally reconstructable; should remain zero."},
        {"metric": "alb2005_consumption_aggregate_crosswalk_sdg382_ready_rows", "value": str(counts["alb2005_consumption_aggregate_crosswalk_sdg382_ready_rows"]), "interpretation": "ALB_2005 aggregate crosswalk rows ready for SDG 3.8.2 denominator construction; should remain zero."},
        {"metric": "alb2005_consumption_aggregate_crosswalk_recipe_ready_rows", "value": str(counts["alb2005_consumption_aggregate_crosswalk_recipe_ready_rows"]), "interpretation": "ALB_2005 aggregate crosswalk rows ready for recipe promotion; should remain zero."},
        {"metric": "alb2005_consumption_aggregate_crosswalk_outcome_ready_rows", "value": str(counts["alb2005_consumption_aggregate_crosswalk_outcome_ready_rows"]), "interpretation": "ALB_2005 aggregate crosswalk rows ready for outcome promotion; should remain zero."},
        {"metric": "alb2005_consumption_aggregate_crosswalk_climate_linkage_ready_rows", "value": str(counts["alb2005_consumption_aggregate_crosswalk_climate_linkage_ready_rows"]), "interpretation": "ALB_2005 aggregate crosswalk rows ready for climate linkage; should remain zero."},
        {"metric": "alb2005_consumption_component_source_search_rows", "value": str(counts["alb2005_consumption_component_source_search_rows"]), "interpretation": "ALB_2005 consumption component source-search audit rows."},
        {"metric": "alb2005_consumption_component_source_search_local_files_scanned", "value": str(counts["alb2005_consumption_component_source_search_local_files_scanned"]), "interpretation": "Local ALB_2005 file rows scanned for component source evidence."},
        {"metric": "alb2005_consumption_component_source_search_local_variables_scanned", "value": str(counts["alb2005_consumption_component_source_search_local_variables_scanned"]), "interpretation": "Local ALB_2005 raw-variable rows scanned for component source evidence."},
        {"metric": "alb2005_consumption_component_source_search_exact_target_variables_found", "value": str(counts["alb2005_consumption_component_source_search_exact_target_variables_found"]), "interpretation": "Public metadata target variables found exactly in local raw schema."},
        {"metric": "alb2005_consumption_component_source_search_exact_target_variables_missing", "value": str(counts["alb2005_consumption_component_source_search_exact_target_variables_missing"]), "interpretation": "Public metadata target variables missing from local raw schema."},
        {"metric": "alb2005_consumption_component_source_search_construction_code_files_found", "value": str(counts["alb2005_consumption_component_source_search_construction_code_files_found"]), "interpretation": "Local source-code-like files found under the ALB_2005 extract."},
        {"metric": "alb2005_consumption_component_source_search_construction_code_targets_found", "value": str(counts["alb2005_consumption_component_source_search_construction_code_targets_found"]), "interpretation": "Target variables with construction-code text hits."},
        {"metric": "alb2005_consumption_component_source_search_recipe_ready_rows", "value": str(counts["alb2005_consumption_component_source_search_recipe_ready_rows"]), "interpretation": "ALB_2005 component source-search rows ready for recipe promotion; should remain zero."},
        {"metric": "alb2005_consumption_component_source_search_outcome_ready_rows", "value": str(counts["alb2005_consumption_component_source_search_outcome_ready_rows"]), "interpretation": "ALB_2005 component source-search rows ready for outcome promotion; should remain zero."},
        {"metric": "alb2005_consumption_component_source_search_sdg382_ready_rows", "value": str(counts["alb2005_consumption_component_source_search_sdg382_ready_rows"]), "interpretation": "ALB_2005 component source-search rows ready for SDG 3.8.2 denominator construction; should remain zero."},
        {"metric": "alb2005_consumption_component_source_search_climate_linkage_ready_rows", "value": str(counts["alb2005_consumption_component_source_search_climate_linkage_ready_rows"]), "interpretation": "ALB_2005 component source-search rows ready for climate linkage; should remain zero."},
        {"metric": "alb2005_minimum_recipe_promotion_action_rows", "value": str(counts["alb2005_minimum_recipe_promotion_action_rows"]), "interpretation": "ALB_2005 minimum recipe promotion action rows."},
        {"metric": "alb2005_minimum_recipe_promotion_gate_rows", "value": str(counts["alb2005_minimum_recipe_promotion_gate_rows"]), "interpretation": "ALB_2005 minimum recipe promotion gate rows."},
        {"metric": "alb2005_minimum_recipe_promotion_blocked_gates", "value": str(counts["alb2005_minimum_recipe_promotion_blocked_gates"]), "interpretation": "ALB_2005 minimum recipe gates still blocked."},
        {"metric": "alb2005_minimum_recipe_promotion_harmonized_ready_rows", "value": str(counts["alb2005_minimum_recipe_promotion_harmonized_ready_rows"]), "interpretation": "ALB_2005 rows ready for harmonized data promotion; should remain zero."},
        {"metric": "alb2005_minimum_recipe_promotion_outcome_ready_rows", "value": str(counts["alb2005_minimum_recipe_promotion_outcome_ready_rows"]), "interpretation": "ALB_2005 rows ready for outcome promotion; should remain zero."},
        {"metric": "alb2005_minimum_recipe_promotion_climate_linkage_ready_rows", "value": str(counts["alb2005_minimum_recipe_promotion_climate_linkage_ready_rows"]), "interpretation": "ALB_2005 rows ready for climate linkage after minimum recipe gates; should remain zero."},
        {"metric": "alb2005_public_fieldwork_geo_metadata_evidence_rows", "value": str(counts["alb2005_public_fieldwork_geo_metadata_evidence_rows"]), "interpretation": "ALB_2005 public fieldwork/geography metadata evidence rows."},
        {"metric": "alb2005_public_fieldwork_geo_metadata_verified_source_rows", "value": str(counts["alb2005_public_fieldwork_geo_metadata_verified_source_rows"]), "interpretation": "ALB_2005 public fieldwork/geography metadata rows with source snippets verified."},
        {"metric": "alb2005_public_fieldwork_geo_metadata_source_missing_rows", "value": str(counts["alb2005_public_fieldwork_geo_metadata_source_missing_rows"]), "interpretation": "ALB_2005 public fieldwork/geography metadata rows with missing source evidence; should remain zero."},
        {"metric": "alb2005_public_fieldwork_geo_metadata_household_timing_verified_rows", "value": str(counts["alb2005_public_fieldwork_geo_metadata_household_timing_verified_rows"]), "interpretation": "ALB_2005 household timing rows verified after public metadata audit; should remain zero."},
        {"metric": "alb2005_public_fieldwork_geo_metadata_raw_coordinate_value_rows", "value": str(counts["alb2005_public_fieldwork_geo_metadata_raw_coordinate_value_rows"]), "interpretation": "ALB_2005 raw coordinate value rows verified after public metadata audit; should remain zero."},
        {"metric": "alb2005_public_fieldwork_geo_metadata_climate_linkage_ready_rows", "value": str(counts["alb2005_public_fieldwork_geo_metadata_climate_linkage_ready_rows"]), "interpretation": "ALB_2005 climate-linkage rows ready after public metadata audit; should remain zero."},
        {"metric": "alb2005_diary_timing_candidate_audit_rows", "value": str(counts["alb2005_diary_timing_candidate_audit_rows"]), "interpretation": "ALB_2005 bookmetadata diary timing candidate rows."},
        {"metric": "alb2005_diary_timing_candidate_metadata_found_rows", "value": str(counts["alb2005_diary_timing_candidate_metadata_found_rows"]), "interpretation": "ALB_2005 diary timing candidates found in metadata catalog and DDI."},
        {"metric": "alb2005_diary_timing_candidate_raw_bookmetadata_files_present", "value": str(counts["alb2005_diary_timing_candidate_raw_bookmetadata_files_present"]), "interpretation": "Raw bookmetadata files present under temp/raw_downloads; should remain zero in current metadata-only state."},
        {"metric": "alb2005_diary_timing_candidate_date_candidate_rows", "value": str(counts["alb2005_diary_timing_candidate_date_candidate_rows"]), "interpretation": "Diary beginning/finishing date candidate variables with nonzero DDI valid counts."},
        {"metric": "alb2005_diary_timing_candidate_household_timing_promoted_rows", "value": str(counts["alb2005_diary_timing_candidate_household_timing_promoted_rows"]), "interpretation": "ALB_2005 household timing rows promoted after diary candidate audit; should remain zero."},
        {"metric": "alb2005_diary_timing_candidate_climate_linkage_ready_rows", "value": str(counts["alb2005_diary_timing_candidate_climate_linkage_ready_rows"]), "interpretation": "ALB_2005 climate-linkage rows ready after diary candidate audit; should remain zero."},
        {"metric": "alb2005_extracted_module_coverage_ddi_module_rows", "value": str(counts["alb2005_extracted_module_coverage_ddi_module_rows"]), "interpretation": "ALB_2005 DDI/schema modules checked against extracted files."},
        {"metric": "alb2005_archive_member_manifest_rows", "value": str(counts["alb2005_archive_member_manifest"]), "interpretation": "Machine-readable ALB_2005 local archive member manifest rows."},
        {"metric": "alb2005_archive_member_rows", "value": str(counts["alb2005_archive_member_rows"]), "interpretation": "Members listed directly from the local ALB_2005 archive."},
        {"metric": "alb2005_archive_sav_member_rows", "value": str(counts["alb2005_archive_sav_member_rows"]), "interpretation": "SPSS .sav members listed directly from the local ALB_2005 archive."},
        {"metric": "alb2005_archive_questionnaire_member_rows", "value": str(counts["alb2005_archive_questionnaire_member_rows"]), "interpretation": "Questionnaire workbook members listed directly from the local ALB_2005 archive."},
        {"metric": "alb2005_archive_ddi_module_present_rows", "value": str(counts["alb2005_archive_ddi_module_present_rows"]), "interpretation": "ALB_2005 DDI/schema modules present in the local archive manifest."},
        {"metric": "alb2005_archive_ddi_module_absent_rows", "value": str(counts["alb2005_archive_ddi_module_absent_rows"]), "interpretation": "ALB_2005 DDI/schema modules absent from the local archive manifest."},
        {"metric": "alb2005_archive_critical_module_absent_rows", "value": str(counts["alb2005_archive_critical_module_absent_rows"]), "interpretation": "Critical ALB_2005 timing, food-diary, and design DDI modules absent from the archive manifest."},
        {"metric": "alb2005_archive_listing_status", "value": str(counts["alb2005_archive_listing_status"]), "interpretation": "Whether the local ALB_2005 archive member list was readable."},
        {"metric": "alb2005_extracted_module_coverage_present_rows", "value": str(counts["alb2005_extracted_module_coverage_present_rows"]), "interpretation": "ALB_2005 DDI modules present in extracted files."},
        {"metric": "alb2005_extracted_module_coverage_missing_rows", "value": str(counts["alb2005_extracted_module_coverage_missing_rows"]), "interpretation": "ALB_2005 DDI modules missing from extracted files."},
        {"metric": "alb2005_extracted_module_coverage_bookmetadata_missing_rows", "value": str(counts["alb2005_extracted_module_coverage_bookmetadata_missing_rows"]), "interpretation": "ALB_2005 bookmetadata_cl missing rows; should be one until raw module is obtained."},
        {"metric": "alb2005_extracted_module_coverage_critical_missing_rows", "value": str(counts["alb2005_extracted_module_coverage_critical_missing_rows"]), "interpretation": "ALB_2005 critical missing timing/food-diary/design modules."},
        {"metric": "alb2005_extracted_module_coverage_coordinate_metadata_variable_rows", "value": str(counts["alb2005_extracted_module_coverage_coordinate_metadata_variable_rows"]), "interpretation": "ALB_2005 coordinate/GPS metadata variable rows; zero means GPS claim remains unverified by variable catalog."},
        {"metric": "alb2005_extracted_module_coverage_coordinate_extracted_file_rows", "value": str(counts["alb2005_extracted_module_coverage_coordinate_extracted_file_rows"]), "interpretation": "ALB_2005 coordinate/GPS extracted file rows; should remain zero unless a coordinate file is found."},
        {"metric": "alb2005_extracted_module_coverage_climate_linkage_ready_rows", "value": str(counts["alb2005_extracted_module_coverage_climate_linkage_ready_rows"]), "interpretation": "ALB_2005 climate-linkage rows ready after extracted-module audit; should remain zero."},
        {"metric": "alb2005_fallback_blocker_resolution_rows", "value": str(counts["alb2005_fallback_blocker_resolution_rows"]), "interpretation": "ALB_2005 fallback blocker matrix rows."},
        {"metric": "alb2005_fallback_blocker_hard_blocked_rows", "value": str(counts["alb2005_fallback_blocker_hard_blocked_rows"]), "interpretation": "ALB_2005 rows hard-blocked from fallback promotion."},
        {"metric": "alb2005_fallback_blocker_harmonized_ready_rows", "value": str(counts["alb2005_fallback_blocker_harmonized_ready_rows"]), "interpretation": "ALB_2005 fallback rows ready for harmonized data; should remain zero."},
        {"metric": "alb2005_fallback_blocker_outcome_ready_rows", "value": str(counts["alb2005_fallback_blocker_outcome_ready_rows"]), "interpretation": "ALB_2005 fallback rows ready for outcome promotion; should remain zero."},
        {"metric": "alb2005_fallback_blocker_climate_linkage_ready_rows", "value": str(counts["alb2005_fallback_blocker_climate_linkage_ready_rows"]), "interpretation": "ALB_2005 fallback rows ready for climate linkage; should remain zero."},
        {"metric": "alb2005_fallback_blocker_data_write_ready_rows", "value": str(counts["alb2005_fallback_blocker_data_write_ready_rows"]), "interpretation": "Rows allowed for data/ write by the ALB_2005 fallback matrix; should remain zero."},
        {"metric": "alb2005_fallback_blocker_current_decision", "value": str(counts["alb2005_fallback_blocker_current_decision"]), "interpretation": "Current consolidated ALB_2005 fallback decision."},
        {"metric": "albania_first_analysis_promotion_wave_rows", "value": str(counts["albania_first_analysis_promotion_wave_rows"]), "interpretation": "Local Albania raw waves compared for first analysis promotion."},
        {"metric": "albania_first_analysis_promotion_gate_rows", "value": str(counts["albania_first_analysis_promotion_gate_rows"]), "interpretation": "First-analysis promotion gate checklist rows."},
        {"metric": "albania_first_analysis_promotion_blocked_gate_rows", "value": str(counts["albania_first_analysis_promotion_blocked_gate_rows"]), "interpretation": "First-analysis promotion gates still blocked."},
        {"metric": "albania_first_analysis_promotion_ready_wave_rows", "value": str(counts["albania_first_analysis_promotion_ready_wave_rows"]), "interpretation": "Albania waves ready for first analytical-sample promotion; should remain zero."},
        {"metric": "albania_first_analysis_promotion_harmonized_ready_rows", "value": str(counts["albania_first_analysis_promotion_harmonized_ready_rows"]), "interpretation": "Harmonized-ready rows across compared Albania waves; should remain zero."},
        {"metric": "albania_first_analysis_promotion_outcome_ready_rows", "value": str(counts["albania_first_analysis_promotion_outcome_ready_rows"]), "interpretation": "Outcome-ready rows across compared Albania waves; should remain zero."},
        {"metric": "albania_first_analysis_promotion_climate_linkage_ready_rows", "value": str(counts["albania_first_analysis_promotion_climate_linkage_ready_rows"]), "interpretation": "Climate-linkage-ready rows across compared Albania waves; should remain zero."},
        {"metric": "albania_existing_raw_wave_audit_rows", "value": str(counts["albania_existing_raw_wave_audit"]), "interpretation": "Existing Albania raw wave audit rows."},
        {"metric": "albania_existing_raw_wave_harmonization_ready_rows", "value": str(counts["albania_existing_raw_wave_harmonization_ready_rows"]), "interpretation": "Existing Albania raw waves ready for harmonized promotion; should remain zero until wave-specific audits pass."},
        {"metric": "albania_existing_raw_wave_climate_linkage_ready_rows", "value": str(counts["albania_existing_raw_wave_climate_linkage_ready_rows"]), "interpretation": "Existing Albania raw waves ready for climate-linkage promotion; should remain zero until timing/geography pass."},
        {"metric": "alb2008_household_core_candidate_rows", "value": str(counts["alb2008_household_core_candidate"]), "interpretation": "ALB_2008 temp household core candidate rows."},
        {"metric": "alb2008_household_core_recipe_ready_rows", "value": str(counts["alb2008_household_core_recipe_ready_rows"]), "interpretation": "ALB_2008 household core rows ready for data promotion; should remain zero until gates pass."},
        {"metric": "alb2008_provisional_outcome_feasibility_rows", "value": str(counts["alb2008_provisional_outcome_feasibility_audit"]), "interpretation": "ALB_2008 provisional outcome feasibility audit rows."},
        {"metric": "alb2008_provisional_outcome_ready_rows", "value": str(counts["alb2008_provisional_outcome_ready_rows"]), "interpretation": "ALB_2008 provisional outcome rows ready for final promotion; should remain zero."},
        {"metric": "alb2008_outcome_semantics_raw_value_rows", "value": str(counts["alb2008_outcome_semantics_raw_value_audit"]), "interpretation": "ALB_2008 raw outcome-semantics value audit rows."},
        {"metric": "alb2008_outcome_semantics_outcome_ready_rows", "value": str(counts["alb2008_outcome_semantics_outcome_ready_rows"]), "interpretation": "ALB_2008 raw outcome-semantics rows ready for final promotion; should remain zero."},
        {"metric": "alb2008_outcome_semantics_sdg382_ready_rows", "value": str(counts["alb2008_outcome_semantics_sdg382_ready_rows"]), "interpretation": "ALB_2008 raw outcome-semantics rows ready for SDG 3.8.2 construction; should remain zero."},
        {"metric": "alb2008_outcome_semantics_climate_linkage_ready_rows", "value": str(counts["alb2008_outcome_semantics_climate_linkage_ready_rows"]), "interpretation": "ALB_2008 raw outcome-semantics rows ready for climate linkage; should remain zero."},
        {"metric": "alb2008_timing_geography_exhaustive_rows", "value": str(counts["alb2008_timing_geography_exhaustive_audit"]), "interpretation": "ALB_2008 timing/geography exhaustive audit rows."},
        {"metric": "alb2008_climate_linkage_ready_rows", "value": str(counts["alb2008_climate_linkage_ready_rows"]), "interpretation": "ALB_2008 rows ready for climate linkage; should remain zero until timing/geography are verified."},
        {"metric": "alb2008_fallback_blocker_resolution_rows", "value": str(counts["alb2008_fallback_blocker_resolution_rows"]), "interpretation": "ALB_2008 fallback blocker matrix rows."},
        {"metric": "alb2008_fallback_blocker_hard_blocked_rows", "value": str(counts["alb2008_fallback_blocker_hard_blocked_rows"]), "interpretation": "ALB_2008 rows hard-blocked from fallback promotion."},
        {"metric": "alb2008_fallback_blocker_interview_timing_ready_rows", "value": str(counts["alb2008_fallback_blocker_interview_timing_ready_rows"]), "interpretation": "ALB_2008 fallback rows with verified interview timing; should remain zero."},
        {"metric": "alb2008_fallback_blocker_geography_ready_rows", "value": str(counts["alb2008_fallback_blocker_geography_ready_rows"]), "interpretation": "ALB_2008 fallback rows with promoted geography; should remain zero."},
        {"metric": "alb2008_fallback_blocker_outcome_ready_rows", "value": str(counts["alb2008_fallback_blocker_outcome_ready_rows"]), "interpretation": "ALB_2008 fallback rows ready for outcome promotion; should remain zero."},
        {"metric": "alb2008_fallback_blocker_climate_linkage_ready_rows", "value": str(counts["alb2008_fallback_blocker_climate_linkage_ready_rows"]), "interpretation": "ALB_2008 fallback rows ready for climate linkage; should remain zero."},
        {"metric": "alb2008_fallback_blocker_data_write_ready_rows", "value": str(counts["alb2008_fallback_blocker_data_write_ready_rows"]), "interpretation": "Rows allowed for data/ write by the ALB_2008 fallback matrix; should remain zero."},
        {"metric": "alb2008_fallback_blocker_current_decision", "value": str(counts["alb2008_fallback_blocker_current_decision"]), "interpretation": "Current consolidated ALB_2008 fallback decision."},
        {"metric": "alb2002_local_geo_artifact_rows", "value": str(counts["alb2002_local_geo_artifact_audit"]), "interpretation": "ALB_2002 local geography artifact audit rows."},
        {"metric": "alb2002_local_geo_artifact_summary_rows", "value": str(counts["alb2002_local_geo_artifact_summary"]), "interpretation": "ALB_2002 local geography artifact summary rows."},
        {"metric": "alb2002_local_geo_artifact_files_scanned", "value": str(counts["alb2002_local_geo_artifact_files_scanned"]), "interpretation": "Local extracted ALB_2002 files scanned for geography artifacts."},
        {"metric": "alb2002_local_geo_artifact_coordinate_raw_variable_rows", "value": str(counts["alb2002_local_geo_artifact_coordinate_raw_variable_rows"]), "interpretation": "Raw coordinate/GPS variable rows; should remain zero until a raw coordinate artifact is verified."},
        {"metric": "alb2002_local_geo_artifact_questionnaire_coordinate_field_rows", "value": str(counts["alb2002_local_geo_artifact_questionnaire_coordinate_field_rows"]), "interpretation": "Questionnaire coordinate/GPS field rows."},
        {"metric": "alb2002_local_geo_artifact_admin_variable_rows", "value": str(counts["alb2002_local_geo_artifact_admin_variable_rows"]), "interpretation": "Raw admin/sampling geography variable rows."},
        {"metric": "alb2002_local_geo_artifact_local_coordinate_ready_rows", "value": str(counts["alb2002_local_geo_artifact_local_coordinate_ready_rows"]), "interpretation": "Rows ready for point climate linkage from local coordinate artifacts; should remain zero."},
        {"metric": "alb2002_local_geo_artifact_local_boundary_ready_rows", "value": str(counts["alb2002_local_geo_artifact_local_boundary_ready_rows"]), "interpretation": "Rows ready for admin aggregation from local boundary artifacts; should remain zero."},
        {"metric": "alb2002_local_geo_artifact_climate_linkage_ready_rows", "value": str(counts["alb2002_local_geo_artifact_climate_linkage_ready_rows"]), "interpretation": "ALB_2002 rows ready for climate linkage after local artifact audit; should remain zero."},
        {"metric": "first_batch_dataset_verification_gate_rows", "value": str(counts["first_batch_dataset_verification_gate"]), "interpretation": "First-batch dataset verification gate rows."},
        {"metric": "first_batch_concept_verification_template_rows", "value": str(counts["first_batch_concept_verification_template"]), "interpretation": "First-batch concept verification template rows."},
        {"metric": "first_batch_variable_verification_template_rows", "value": str(counts["first_batch_variable_verification_template"]), "interpretation": "First-batch variable verification template rows."},
        {"metric": "direct_read_bundle_rows", "value": str(counts["direct_read_bundle"]), "interpretation": "Direct-read audit bundle rows."},
        {"metric": "direct_read_artifact_manifest_rows", "value": str(counts["direct_read_manifest"]), "interpretation": "Curated direct-read artifact manifest rows."},
        {"metric": "direct_read_summary_rows", "value": str(counts["direct_read_summary"]), "interpretation": "Direct-read bundle summary rows."},
        {"metric": "design_scorecard_rows", "value": str(counts["design_scorecard_rows"]), "interpretation": "Rows in the refreshed design scorecard."},
        {"metric": "design_scorecard_current_rows", "value": str(counts["design_scorecard_current_rows"]), "interpretation": "Current-state fail-closed design rows appended to the broad scorecard."},
        {"metric": "design_no_go_threshold_rows", "value": str(counts["design_no_go_threshold_rows"]), "interpretation": "Current design no-go threshold rows."},
        {"metric": "design_scorecard_data_write_ready_rows", "value": str(counts["design_scorecard_data_write_ready_rows"]), "interpretation": "Rows allowed for data/ write by the design scorecard; should remain zero."},
        {"metric": "design_scorecard_current_decision", "value": str(counts["design_scorecard_current_decision"]), "interpretation": "Current fail-closed design scorecard decision."},
        {"metric": "alb2002_promotion_gate_delta_rows", "value": str(counts["alb2002_promotion_gate_delta_rows"]), "interpretation": "ALB_2002 promotion gate delta rows."},
        {"metric": "alb2002_promotion_gate_delta_hard_blocked_rows", "value": str(counts["alb2002_promotion_gate_delta_hard_blocked_rows"]), "interpretation": "ALB_2002 hard-blocked promotion gate rows."},
        {"metric": "alb2002_promotion_gate_delta_data_write_ready_rows", "value": str(counts["alb2002_promotion_gate_delta_data_write_ready_rows"]), "interpretation": "Rows allowed for data/ write by the ALB_2002 gate-delta audit; should remain zero."},
        {"metric": "alb2002_promotion_gate_delta_decision", "value": str(counts["alb2002_promotion_gate_delta_decision"]), "interpretation": "Current ALB_2002 promotion-gate delta decision."},
        {"metric": "alb2002_boundary_blocker_resolution_rows", "value": str(counts["alb2002_boundary_blocker_resolution_rows"]), "interpretation": "ALB_2002 boundary blocker resolution rows."},
        {"metric": "alb2002_boundary_blocker_candidate_name_coverage_rows", "value": str(counts["alb2002_boundary_blocker_candidate_name_coverage_rows"]), "interpretation": "Public boundary leads with complete candidate name coverage but no climate-linkage promotion."},
        {"metric": "alb2002_boundary_blocker_climate_linkage_ready_rows", "value": str(counts["alb2002_boundary_blocker_climate_linkage_ready_rows"]), "interpretation": "Rows ready for ALB_2002 boundary climate-linkage promotion; should remain zero."},
        {"metric": "alb2002_boundary_blocker_data_write_ready_rows", "value": str(counts["alb2002_boundary_blocker_data_write_ready_rows"]), "interpretation": "Rows allowed for data/ write by the boundary blocker matrix; should remain zero."},
        {"metric": "alb2002_boundary_blocker_current_decision", "value": str(counts["alb2002_boundary_blocker_current_decision"]), "interpretation": "Current consolidated ALB_2002 boundary-source decision."},
        {"metric": "alb2002_outcome_blocker_resolution_rows", "value": str(counts["alb2002_outcome_blocker_resolution_rows"]), "interpretation": "ALB_2002 outcome blocker resolution rows."},
        {"metric": "alb2002_outcome_blocker_candidate_not_promoted_rows", "value": str(counts["alb2002_outcome_blocker_candidate_not_promoted_rows"]), "interpretation": "Candidate ALB_2002 outcome rows with evidence but no final promotion."},
        {"metric": "alb2002_outcome_blocker_outcome_ready_rows", "value": str(counts["alb2002_outcome_blocker_outcome_ready_rows"]), "interpretation": "Rows ready for final ALB_2002 outcome promotion; should remain zero."},
        {"metric": "alb2002_outcome_blocker_data_write_ready_rows", "value": str(counts["alb2002_outcome_blocker_data_write_ready_rows"]), "interpretation": "Rows allowed for data/ write by the outcome blocker matrix; should remain zero."},
        {"metric": "alb2002_outcome_blocker_current_decision", "value": str(counts["alb2002_outcome_blocker_current_decision"]), "interpretation": "Current consolidated ALB_2002 outcome-promotion decision."},
        {"metric": "alb2012_timing_geography_blocker_resolution_rows", "value": str(counts["alb2012_timing_geography_blocker_resolution_rows"]), "interpretation": "ALB_2012 fallback blocker matrix rows."},
        {"metric": "alb2012_timing_geography_blocker_hard_blocked_rows", "value": str(counts["alb2012_timing_geography_blocker_hard_blocked_rows"]), "interpretation": "ALB_2012 rows hard-blocked from fallback promotion."},
        {"metric": "alb2012_timing_geography_blocker_climate_linkage_ready_rows", "value": str(counts["alb2012_timing_geography_blocker_climate_linkage_ready_rows"]), "interpretation": "ALB_2012 fallback rows ready for climate linkage; should remain zero."},
        {"metric": "alb2012_timing_geography_blocker_data_write_ready_rows", "value": str(counts["alb2012_timing_geography_blocker_data_write_ready_rows"]), "interpretation": "Rows allowed for data/ write by the ALB_2012 fallback matrix; should remain zero."},
        {"metric": "alb2012_timing_geography_blocker_current_decision", "value": str(counts["alb2012_timing_geography_blocker_current_decision"]), "interpretation": "Current consolidated ALB_2012 fallback decision."},
        {"metric": "completion_criteria_complete", "value": str(counts["completion_complete"]), "interpretation": "Completion criteria currently complete."},
        {"metric": "completion_criteria_incomplete", "value": str(counts["completion_incomplete"]), "interpretation": "Completion criteria currently incomplete."},
    ]
    for status, count in sorted(req_counts.items()):
        rows.append({"metric": f"requirement_status_{status}", "value": str(count), "interpretation": "Objective requirement status count."})
    for status, count in sorted(guard_counts.items()):
        rows.append({"metric": f"guardrail_status_{status}", "value": str(count), "interpretation": "Guardrail status count."})
    return rows


def markdown_count_table(counter: Counter[str], label: str) -> str:
    lines = [f"| {label} | Count |", "|---|---:|"]
    for key, count in counter.most_common():
        lines.append(f"| {key or 'blank'} | {count} |")
    return "\n".join(lines)


def markdown_rows(rows: list[dict[str, str]], columns: list[str], limit: int = 20) -> str:
    lines = ["| " + " | ".join(columns) + " |", "|" + "|".join("---" for _ in columns) + "|"]
    for row in rows[:limit]:
        values = []
        for column in columns:
            value = row.get(column, "").replace("|", "/")
            if len(value) > 140:
                value = value[:137] + "..."
            values.append(value)
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines)


def write_report(requirements: list[dict[str, str]], guardrails: list[dict[str, str]], summaries: list[dict[str, str]]) -> None:
    req_counts = Counter(row["status"] for row in requirements)
    guard_counts = Counter(row["status"] for row in guardrails)
    unresolved = [row for row in requirements if row["status"] != "satisfied"]
    guard_unresolved = [row for row in guardrails if row["status"] != "satisfied"]
    lines = [
        "# Objective Traceability Audit",
        "",
        "Status: this audit maps the user objective to current workspace evidence. It is not a claim that the empirical project is complete.",
        "",
        "## Requirement Status",
        "",
        markdown_count_table(req_counts, "Requirement status"),
        "",
        "## Guardrail Status",
        "",
        markdown_count_table(guard_counts, "Guardrail status"),
        "",
        "## Summary Metrics",
        "",
        "| Metric | Value | Interpretation |",
        "|---|---:|---|",
    ]
    for row in summaries:
        lines.append(f"| {row['metric']} | {row['value']} | {row['interpretation']} |")
    lines.extend(
        [
            "",
            "## Unresolved Requirements",
            "",
            markdown_rows(unresolved, ["requirement_id", "objective_section", "status", "evidence", "gap"], 30)
            if unresolved
            else "All traced requirements are satisfied.",
            "",
            "## Unresolved Guardrails",
            "",
            markdown_rows(guard_unresolved, ["guardrail_id", "status", "evidence", "gap"], 20)
            if guard_unresolved
            else "All traced guardrails are satisfied.",
            "",
            "## Machine-Readable Outputs",
            "",
            "- `result/objective_requirement_traceability.csv`",
            "- `result/objective_guardrail_audit.csv`",
            "- `result/objective_traceability_summary.csv`",
        ]
    )
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    ensure_dirs()
    counts = current_counts()
    requirements = build_requirement_rows(counts)
    guardrails = build_guardrail_rows(counts)
    summaries = build_summary(requirements, guardrails, counts)
    write_csv(TRACE_PATH, requirements, TRACE_COLUMNS)
    write_csv(GUARDRAIL_PATH, guardrails, GUARDRAIL_COLUMNS)
    write_csv(SUMMARY_PATH, summaries, SUMMARY_COLUMNS)
    write_report(requirements, guardrails, summaries)
    req_counts = Counter(row["status"] for row in requirements)
    guard_counts = Counter(row["status"] for row in guardrails)
    append_log(
        TEMP_DIR / "audit_log.md",
        f"Objective traceability audit requirement_status={dict(req_counts)} guardrail_status={dict(guard_counts)}.",
    )
    print(f"Objective traceability requirements={len(requirements)} guardrails={len(guardrails)} raw_files={counts['raw_files']} raw_variables={counts['raw_variables']}.")


if __name__ == "__main__":
    main()
