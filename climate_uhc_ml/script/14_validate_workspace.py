from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path
from typing import Any

from common import DATA_DIR, PROJECT_ROOT, REPORT_DIR, RESULT_DIR, SCRIPT_DIR, TEMP_DIR, append_log, ensure_dirs, write_csv


AUDIT_PATH = RESULT_DIR / "workspace_validation_audit.csv"
REPORT_PATH = REPORT_DIR / "workspace_validation.md"

AUDIT_COLUMNS = ["category", "requirement", "status", "evidence", "gap"]

REQUIRED_DIRS = ["data", "script", "result", "report", "temp"]
REQUIRED_REPORTS = [
    "README.md",
    "source_audit.md",
    "data_dictionary.md",
    "outcome_construction.md",
    "climate_linkage_audit.md",
    "identification_audit.md",
    "modeling_report.md",
    "final_report.md",
    "public_documentation_audit.md",
    "raw_download_audit.md",
    "raw_download_intake_plan.md",
    "climate_source_probe.md",
    "validation_reference_sources.md",
    "sample_selection_audit.md",
    "metadata_candidate_quality_audit.md",
    "raw_ingestion_plan.md",
    "climate_exposure_plan.md",
    "outcome_denominator_plan.md",
    "modeling_identification_plan.md",
    "objective_traceability_audit.md",
    "reproducibility_environment.md",
    "raw_variable_verification_protocol.md",
    "harmonization_recipe_gate.md",
    "analysis_dataset_promotion_barriers.md",
    "design_scorecard_audit.md",
    "alb2002_promotion_gate_delta_audit.md",
    "alb2002_boundary_blocker_resolution_matrix.md",
    "alb2002_outcome_blocker_resolution_matrix.md",
    "minimum_viable_acquisition_plan.md",
    "public_external_raw_candidate_downloads.md",
    "sdg382_denominator_audit_plan.md",
    "climate_validation_protocol.md",
    "mechanism_analysis_protocol.md",
    "empirical_readiness_dashboard.md",
    "first_batch_raw_acquisition_checklist.md",
    "first_batch_official_raw_access_probe.md",
    "first_batch_manual_download_handoff.md",
    "first_batch_public_documentation_audit.md",
    "first_batch_file_source_traceability.md",
    "first_batch_merge_key_lineage_plan.md",
    "first_batch_raw_value_key_audit.md",
    "alb2002_household_core_merge_audit.md",
    "alb2002_provisional_outcome_feasibility.md",
    "alb2002_outcome_semantics_raw_value_audit.md",
    "alb2002_health_questionnaire_semantics_audit.md",
    "alb2002_oop_aggregation_policy_audit.md",
    "alb2002_skip_missing_semantics_audit.md",
    "alb2002_oop_skip_value_decision_audit.md",
    "alb2002_access_need_denominator_policy_audit.md",
    "alb2002_consumption_sdg_denominator_policy_audit.md",
    "alb2002_consumption_construction_source_audit.md",
    "alb2002_consumption_aggregate_metadata_crosswalk_audit.md",
    "alb2002_period_aligned_che_policy_audit.md",
    "alb2002_che_candidate_outcome_audit.md",
    "alb2002_access_candidate_outcome_audit.md",
    "alb2002_uhc_composite_candidate_audit.md",
    "alb2002_analysis_candidate_readiness_audit.md",
    "alb2002_harmonized_household_core_promotion.md",
    "alb2002_limited_financial_outcome_promotion.md",
    "alb2002_limited_climate_exposure_promotion.md",
    "alb2002_limited_climate_linked_promotion.md",
    "alb2002_climate_centroid_exposure_audit.md",
    "alb2002_climate_shock_candidate_audit.md",
    "alb2002_climate_outcome_linked_candidate_audit.md",
    "alb2002_linked_candidate_descriptive_diagnostics.md",
    "alb2002_weight_design_evidence_audit.md",
    "alb2002_sample_design_documentation_audit.md",
    "alb2002_minimum_recipe_promotion_packet.md",
    "alb2002_district_climate_crosswalk_audit.md",
    "alb2002_boundary_name_match_audit.md",
    "alb2002_boundary_source_alternative_audit.md",
    "alb2002_boundary_source_resource_search_audit.md",
    "alb2002_boundary_geometry_provenance_audit.md",
    "alb2002_boundary_manual_verification_packet.md",
    "alb2002_boundary_manual_source_followup.md",
    "alb2002_local_geography_artifact_audit.md",
    "alb2002_gadm_boundary_lead_audit.md",
    "alb2012_raw_core_feasibility.md",
    "alb2012_provisional_outcome_feasibility.md",
    "alb2012_outcome_semantics_raw_value_audit.md",
    "alb2012_timing_geography_exhaustive_audit.md",
    "alb2012_questionnaire_timing_field_audit.md",
    "alb2012_timing_geography_blocker_resolution_matrix.md",
    "albania_legacy_questionnaire_readability_audit.md",
    "albania_legacy_questionnaire_timing_field_audit.md",
    "alb2005_documented_harmonization_review.md",
    "alb2005_household_core_merge_audit.md",
    "alb2005_provisional_outcome_feasibility.md",
    "alb2005_outcome_semantics_raw_value_audit.md",
    "alb2005_timing_geography_exhaustive_audit.md",
    "alb2005_required_value_key_audit.md",
    "alb2005_health_questionnaire_semantics_audit.md",
    "alb2005_oop_aggregation_policy_audit.md",
    "alb2005_skip_missing_semantics_audit.md",
    "alb2005_consumption_oop_unit_period_audit.md",
    "alb2005_consumption_aggregate_metadata_crosswalk_audit.md",
    "alb2005_consumption_component_source_search_audit.md",
    "alb2005_timing_geography_source_search_audit.md",
    "alb2005_minimum_recipe_promotion_packet.md",
    "alb2005_public_fieldwork_geo_metadata_audit.md",
    "alb2005_diary_timing_candidate_audit.md",
    "alb2005_extracted_module_coverage_audit.md",
    "alb2005_fallback_blocker_resolution_matrix.md",
    "albania_first_analysis_promotion_gate.md",
    "albania_existing_raw_wave_audit.md",
    "alb2008_household_core_merge_audit.md",
    "alb2008_provisional_outcome_feasibility.md",
    "alb2008_outcome_semantics_raw_value_audit.md",
    "alb2008_timing_geography_exhaustive_audit.md",
    "alb2008_fallback_blocker_resolution_matrix.md",
    "first_batch_raw_verification_workbook.md",
    "direct_read_audit_bundle.md",
    "country_wave_promotion_registry.md",
    "priority_promotion_acquisition_plan.md",
    "priority_official_raw_access_probe.md",
    "priority_raw_intake_gate.md",
    "priority_archive_member_preflight.md",
    "priority_climate_linkage_preflight.md",
    "priority_raw_verification_workbook.md",
    "priority_manual_verification_decision_gate.md",
    "priority_raw_package_receipt_ledger.md",
    "priority_official_download_dossier.md",
    "priority_public_documentation_receipt.md",
    "priority_official_metadata_evidence_extract.md",
    "priority_credentialed_raw_acquisition_ledger.md",
    "priority_official_endpoint_matrix.md",
    "priority_core_file_endpoint_matrix.md",
    "priority_threshold_acquisition_campaign.md",
    "priority_first_pass_variable_review_queue.md",
    "priority_download_execution_packet.md",
    "priority_lsms_isa_alignment_audit.md",
    "priority_lsms_isa_refocused_acquisition_queue.md",
    "priority_lsms_isa_public_documentation_receipt.md",
    "priority_lsms_isa_variable_evidence_matrix.md",
    "priority_lsms_isa_raw_package_intake_packet.md",
    "priority_lsms_isa_archive_member_preflight.md",
    "priority_lsms_isa_raw_value_verification_workbook.md",
    "priority_lsms_isa_raw_package_receipt_checklist.md",
    "priority_lsms_isa_credentialed_raw_acquisition_workbench.md",
    "priority_lsms_isa_official_file_receipt_validator.md",
    "priority_lsms_isa_threshold_download_sequence.md",
    "priority_lsms_isa_minimum_batch_raw_intake_guide.md",
    "priority_lsms_isa_minimum_batch_endpoint_refresh.md",
    "priority_lsms_isa_incoming_raw_package_router.md",
    "priority_lsms_isa_threshold_gap_control_panel.md",
    "priority_lsms_isa_manual_download_packets.md",
    "priority_lsms_isa_manual_download_progress_tracker.md",
    "priority_lsms_isa_post_download_validation_runner.md",
    "priority_lsms_isa_manual_download_execution_board.md",
    "priority_lsms_isa_credentialed_download_handoff.md",
    "priority_lsms_isa_resource_download_route_probe.md",
    "priority_lsms_isa_download_acceptance_matrix.md",
    "priority_lsms_isa_local_target_readmes.md",
    "priority_lsms_isa_minimum_batch_raw_value_queue.md",
    "priority_lsms_isa_target_folder_receipt_smoke_test.md",
    "priority_lsms_isa_threshold_replacement_plan.md",
    "priority_lsms_isa_minimum_batch_climate_linkage_review_queue.md",
    "priority_lsms_isa_local_stray_raw_package_locator.md",
    "mwi2004_sdg382_discretionary_budget_parameter_audit.md",
    "mwi2004_sdg382_external_parameter_source_ledger.md",
    "mwi2004_sdg382_candidate_classification_precheck.md",
    "priority_lsms_isa_promotion_gate_dashboard.md",
    "priority_analysis_dataset_synthesis_blueprint.md",
    "priority_country_wave_promotion_packets.md",
    "priority_lsms_isa_country_wave_promotion_packets.md",
    "promoted_data_gate.md",
]
REQUIRED_TEMP = [
    "source_inventory.csv",
    "country_wave_screening.csv",
    "manual_download_manifest.csv",
    "audit_log.md",
    "iteration_notes.md",
    "rejected_designs.md",
]
REQUIRED_SCRIPTS = [
    "00_setup.py",
    "01_inventory_surveys.py",
    "02_acquire_microdata.py",
    "02_probe_external_repositories.py",
    "03_inspect_raw_schemas.py",
    "04_build_household_panel.py",
    "05_construct_outcomes.py",
    "06_extract_climate.py",
    "07_merge_microdata_climate.py",
    "08_descriptive_diagnostics.py",
    "09_predictive_ml.py",
    "10_causal_models.py",
    "11_causal_ml_policy_learning.py",
    "12_robustness.py",
    "13_write_reports.py",
    "14_validate_workspace.py",
    "15_prepare_manual_request_packet.py",
    "16_snapshot_public_documentation.py",
    "17_audit_raw_downloads.py",
    "18_probe_climate_sources.py",
    "19_probe_validation_reference_sources.py",
    "20_sample_selection_gate.py",
    "21_audit_metadata_variable_quality.py",
    "22_build_raw_ingestion_plan.py",
    "23_build_climate_exposure_plan.py",
    "24_build_outcome_denominator_plan.py",
    "25_build_modeling_identification_plan.py",
    "26_build_objective_traceability_audit.py",
    "27_build_raw_download_intake_package.py",
    "28_audit_python_environment.py",
    "29_build_raw_variable_verification_protocol.py",
    "30_build_minimum_viable_acquisition_plan.py",
    "31_build_sdg382_denominator_audit_plan.py",
    "32_build_climate_validation_protocol.py",
    "33_build_harmonization_recipe_gate.py",
    "34_build_mechanism_analysis_protocol.py",
    "35_build_empirical_readiness_dashboard.py",
    "36_build_direct_read_audit_bundle.py",
    "37_build_first_batch_raw_acquisition_checklist.py",
    "38_build_first_batch_raw_verification_workbook.py",
    "39_probe_first_batch_official_raw_access.py",
    "40_build_first_batch_manual_download_handoff.py",
    "41_build_first_batch_public_documentation_audit.py",
    "42_build_first_batch_file_source_traceability.py",
    "43_build_first_batch_merge_key_lineage_plan.py",
    "44_download_public_external_raw_candidates.py",
    "45_audit_first_batch_raw_value_keys.py",
    "46_build_alb2005_documented_harmonization_review.py",
    "47_audit_alb2005_household_core_merge.py",
    "48_audit_alb2005_provisional_outcome_feasibility.py",
    "49_audit_alb2005_timing_geography_exhaustive.py",
    "50_audit_existing_albania_raw_waves.py",
    "51_audit_alb2008_household_core_merge.py",
    "52_audit_alb2008_provisional_outcome_feasibility.py",
    "53_audit_alb2008_timing_geography_exhaustive.py",
    "54_audit_alb2002_household_core_merge.py",
    "55_audit_alb2002_provisional_outcome_feasibility.py",
    "56_audit_alb2002_district_climate_crosswalk.py",
    "57_audit_alb2012_raw_core_feasibility.py",
    "58_audit_alb2012_provisional_outcome_feasibility.py",
    "59_audit_alb2012_timing_geography_exhaustive.py",
    "60_audit_alb2002_outcome_semantics_raw_values.py",
    "61_audit_alb2005_outcome_semantics_raw_values.py",
    "62_audit_alb2008_outcome_semantics_raw_values.py",
    "63_audit_alb2012_outcome_semantics_raw_values.py",
    "64_audit_alb2002_boundary_name_match.py",
    "65_audit_alb2012_questionnaire_timing_fields.py",
    "66_audit_albania_legacy_questionnaire_readability.py",
    "67_audit_albania_legacy_questionnaire_timing_fields.py",
    "68_build_alb2005_harmonization_value_decision_audit.py",
    "69_audit_alb2002_boundary_source_alternatives.py",
    "70_audit_alb2002_local_geography_artifacts.py",
    "79_audit_alb2002_boundary_source_resource_search.py",
    "81_build_alb2002_boundary_manual_verification_packet.py",
    "82_audit_alb2002_boundary_manual_source_followup.py",
    "71_audit_alb2005_required_value_key_evidence.py",
    "72_audit_alb2005_health_questionnaire_semantics.py",
    "73_audit_alb2005_oop_aggregation_policy.py",
    "74_audit_alb2005_skip_missing_semantics.py",
    "75_audit_alb2005_consumption_oop_unit_period.py",
    "76_audit_alb2005_consumption_aggregate_metadata_crosswalk.py",
    "77_audit_alb2005_consumption_component_source_search.py",
    "78_audit_alb2005_timing_geography_source_search.py",
    "80_audit_alb2002_boundary_geometry_provenance.py",
    "83_build_alb2005_minimum_recipe_promotion_packet.py",
    "84_audit_alb2005_public_fieldwork_geo_metadata.py",
    "85_audit_alb2005_diary_timing_candidates.py",
    "86_audit_alb2005_extracted_module_coverage.py",
    "87_build_albania_first_analysis_promotion_gate.py",
    "88_audit_alb2002_gadm_boundary_lead.py",
    "89_audit_alb2002_health_questionnaire_semantics.py",
    "90_build_alb2002_minimum_recipe_promotion_packet.py",
    "91_audit_alb2002_oop_aggregation_policy.py",
    "92_audit_alb2002_skip_missing_semantics.py",
    "97_audit_alb2002_oop_skip_value_decision.py",
    "93_audit_alb2002_access_need_denominator_policy.py",
    "94_audit_alb2002_consumption_sdg_denominator_policy.py",
    "95_audit_alb2002_consumption_aggregate_metadata_crosswalk.py",
    "96_audit_alb2002_consumption_construction_sources.py",
    "99_audit_alb2002_period_aligned_che_policy.py",
    "100_audit_alb2002_weight_design_evidence.py",
    "101_build_alb2002_che_candidate_outcomes.py",
    "102_build_alb2002_analysis_candidate_dataset.py",
    "103_build_alb2002_climate_centroid_exposure_candidates.py",
    "104_audit_alb2002_sample_design_documentation.py",
    "105_build_alb2002_access_candidate_outcomes.py",
    "106_build_alb2002_uhc_composite_candidate_outcomes.py",
    "107_build_alb2002_climate_shock_candidate_audit.py",
    "108_build_alb2002_climate_outcome_linked_candidate_audit.py",
    "109_build_alb2002_linked_candidate_descriptive_diagnostics.py",
    "110_build_current_design_scorecard.py",
    "111_audit_alb2002_promotion_gate_delta.py",
    "112_build_alb2002_boundary_blocker_resolution_matrix.py",
    "113_build_alb2002_outcome_blocker_resolution_matrix.py",
    "114_build_alb2012_timing_geography_blocker_resolution_matrix.py",
    "115_build_alb2005_fallback_blocker_resolution_matrix.py",
    "116_build_alb2008_fallback_blocker_resolution_matrix.py",
    "117_promote_alb2002_harmonized_household_core.py",
    "119_promote_alb2002_limited_financial_outcomes.py",
    "118_promote_alb2002_limited_climate_exposures.py",
    "120_promote_alb2002_limited_climate_linked.py",
    "121_build_country_wave_promotion_registry.py",
    "122_build_priority_promotion_acquisition_plan.py",
    "123_probe_priority_official_raw_access.py",
    "124_build_priority_raw_intake_gate.py",
    "125_build_priority_climate_linkage_preflight.py",
    "126_build_priority_raw_verification_workbook.py",
    "127_enforce_promoted_data_gate.py",
    "128_build_priority_archive_member_preflight.py",
    "129_build_priority_manual_verification_decision_gate.py",
    "130_build_priority_raw_package_receipt_ledger.py",
    "131_build_priority_official_download_dossier.py",
    "133_build_priority_public_documentation_receipt.py",
    "135_build_priority_official_metadata_evidence_extract.py",
    "136_build_priority_credentialed_raw_acquisition_ledger.py",
    "137_probe_priority_official_endpoint_matrix.py",
    "138_probe_priority_core_file_endpoint_matrix.py",
    "139_build_priority_threshold_acquisition_campaign.py",
    "140_build_priority_first_pass_variable_review_queue.py",
    "141_build_priority_download_execution_packet.py",
    "142_build_priority_lsms_isa_alignment_audit.py",
    "143_build_priority_lsms_isa_refocused_acquisition_queue.py",
    "146_build_priority_lsms_isa_public_documentation_receipt.py",
    "147_build_priority_lsms_isa_variable_evidence_matrix.py",
    "144_build_priority_lsms_isa_raw_package_intake_packet.py",
    "145_build_priority_lsms_isa_archive_member_preflight.py",
    "149_build_priority_lsms_isa_raw_value_verification_workbook.py",
    "150_build_priority_lsms_isa_raw_package_receipt_checklist.py",
    "152_build_priority_lsms_isa_credentialed_raw_acquisition_workbench.py",
    "153_validate_priority_lsms_isa_official_file_receipt.py",
    "154_build_priority_lsms_isa_threshold_download_sequence.py",
    "155_build_priority_lsms_isa_minimum_batch_raw_intake_guide.py",
    "156_probe_priority_lsms_isa_minimum_batch_endpoint_refresh.py",
    "132_build_priority_analysis_dataset_synthesis_blueprint.py",
    "134_build_priority_country_wave_promotion_packets.py",
    "148_build_priority_lsms_isa_country_wave_promotion_packets.py",
    "151_refresh_refocused_promoted_country_wave_registry.py",
    "167_build_mwi2004_access_person_key_resolution_policy.py",
    "168_build_mwi2004_missing_units_recall_skip_policy.py",
    "169_build_mwi2004_chirps_admin2_route_policy.py",
    "170_extract_mwi2004_chirps_admin2_exposures.py",
    "171_build_mwi2004_promoted_household_climate_dataset.py",
    "189_build_mwi2004_sdg382_discretionary_budget_parameter_audit.py",
    "190_build_mwi2004_sdg382_external_parameter_source_ledger.py",
    "191_build_mwi2004_sdg382_candidate_classification_precheck.py",
    "172_build_priority_lsms_isa_next_raw_package_action_packet.py",
    "173_build_priority_lsms_isa_promotion_gate_dashboard.py",
    "174_build_priority_lsms_isa_incoming_raw_package_router.py",
    "175_build_priority_lsms_isa_threshold_gap_control_panel.py",
    "176_build_priority_lsms_isa_manual_download_packets.py",
    "177_build_priority_lsms_isa_manual_download_progress_tracker.py",
    "178_build_priority_lsms_isa_post_download_validation_runner.py",
    "179_build_priority_lsms_isa_manual_download_execution_board.py",
    "180_build_priority_lsms_isa_credentialed_download_handoff.py",
    "181_probe_priority_lsms_isa_resource_download_routes.py",
    "182_build_priority_lsms_isa_download_acceptance_matrix.py",
    "183_build_priority_lsms_isa_local_target_readmes.py",
    "184_build_priority_lsms_isa_minimum_batch_raw_value_queue.py",
    "185_build_priority_lsms_isa_target_folder_receipt_smoke_test.py",
    "186_build_priority_lsms_isa_threshold_replacement_plan.py",
    "187_build_priority_lsms_isa_minimum_batch_climate_linkage_review_queue.py",
    "188_build_priority_lsms_isa_local_stray_raw_package_locator.py",
    "98_audit_analysis_dataset_promotion_barriers.py",
]
PROMOTION_REPRODUCTION_SCRIPTS = [
    "157_build_priority_lsms_isa_received_raw_schema_audit.py",
    "158_build_priority_lsms_isa_received_raw_value_profile.py",
    "159_build_priority_lsms_isa_received_raw_semantics_review.py",
    "169_build_mwi2004_chirps_admin2_route_policy.py",
    "170_extract_mwi2004_chirps_admin2_exposures.py",
    "171_build_mwi2004_promoted_household_climate_dataset.py",
    "189_build_mwi2004_sdg382_discretionary_budget_parameter_audit.py",
    "190_build_mwi2004_sdg382_external_parameter_source_ledger.py",
    "191_build_mwi2004_sdg382_candidate_classification_precheck.py",
    "172_build_priority_lsms_isa_next_raw_package_action_packet.py",
    "174_build_priority_lsms_isa_incoming_raw_package_router.py",
    "175_build_priority_lsms_isa_threshold_gap_control_panel.py",
    "176_build_priority_lsms_isa_manual_download_packets.py",
    "177_build_priority_lsms_isa_manual_download_progress_tracker.py",
    "178_build_priority_lsms_isa_post_download_validation_runner.py",
    "179_build_priority_lsms_isa_manual_download_execution_board.py",
    "180_build_priority_lsms_isa_credentialed_download_handoff.py",
    "181_probe_priority_lsms_isa_resource_download_routes.py",
    "182_build_priority_lsms_isa_download_acceptance_matrix.py",
    "183_build_priority_lsms_isa_local_target_readmes.py",
    "184_build_priority_lsms_isa_minimum_batch_raw_value_queue.py",
    "185_build_priority_lsms_isa_target_folder_receipt_smoke_test.py",
    "186_build_priority_lsms_isa_threshold_replacement_plan.py",
    "187_build_priority_lsms_isa_minimum_batch_climate_linkage_review_queue.py",
    "188_build_priority_lsms_isa_local_stray_raw_package_locator.py",
    "173_build_priority_lsms_isa_promotion_gate_dashboard.py",
]
RAW_EXTENSIONS = {".dta", ".sav", ".por", ".sas7bdat", ".xpt", ".zip", ".tar", ".gz", ".tgz", ".rar", ".7z"}


def read_csv_dicts(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def file_ok(path: Path) -> bool:
    return path.exists() and path.is_file() and path.stat().st_size > 0


def row_count(path: Path) -> int:
    return len(read_csv_dicts(path))


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


def safe_int(value: Any, default: int = 0) -> int:
    try:
        return int(float(str(value).strip()))
    except (TypeError, ValueError):
        return default


def status(condition: bool) -> str:
    return "complete" if condition else "incomplete"


def add(rows: list[dict[str, Any]], category: str, requirement: str, state: str, evidence: str, gap: str = "") -> None:
    rows.append({"category": category, "requirement": requirement, "status": state, "evidence": evidence, "gap": gap})


def validate_dirs(rows: list[dict[str, Any]]) -> None:
    root = TEMP_DIR.parent
    for name in REQUIRED_DIRS:
        path = root / name
        add(rows, "workspace", f"`{name}/` directory exists", status(path.exists() and path.is_dir()), str(path), "" if path.exists() else "Create required workspace directory.")

    raw_in_data = [path for path in DATA_DIR.rglob("*") if path.is_file() and path.suffix.lower() in RAW_EXTENSIONS]
    add(
        rows,
        "directory_rules",
        "No raw microdata/archive files are stored in `data/`",
        "complete" if not raw_in_data else "failed",
        f"raw-like files in data={len(raw_in_data)}",
        "" if not raw_in_data else "; ".join(str(path.relative_to(TEMP_DIR.parent)) for path in raw_in_data[:20]),
    )

    messy_report_files = [path for path in REPORT_DIR.rglob("*") if path.is_file() and path.suffix.lower() in {".csv", ".log", ".tmp", ".json"}]
    add(
        rows,
        "directory_rules",
        "No machine-readable logs/tables are stored in `report/`",
        "complete" if not messy_report_files else "failed",
        f"messy report files={len(messy_report_files)}",
        "" if not messy_report_files else "; ".join(str(path.relative_to(TEMP_DIR.parent)) for path in messy_report_files[:20]),
    )


def validate_required_files(rows: list[dict[str, Any]]) -> None:
    for name in REQUIRED_REPORTS:
        path = REPORT_DIR / name
        add(rows, "required_reports", f"`report/{name}` exists and is non-empty", status(file_ok(path)), f"{path}; bytes={path.stat().st_size if path.exists() else 0}", "" if file_ok(path) else "Run report generation.")

    for name in REQUIRED_TEMP:
        path = TEMP_DIR / name
        add(rows, "required_temp", f"`temp/{name}` exists and is non-empty", status(file_ok(path)), f"{path}; bytes={path.stat().st_size if path.exists() else 0}", "" if file_ok(path) else "Run setup/inventory/acquisition/report stages.")

    for name in REQUIRED_SCRIPTS:
        path = SCRIPT_DIR / name
        add(rows, "required_scripts", f"`script/{name}` exists and is non-empty", status(file_ok(path)), f"{path}; bytes={path.stat().st_size if path.exists() else 0}", "" if file_ok(path) else "Restore required script.")

    runner_paths = [TEMP_DIR.parent / "Makefile", SCRIPT_DIR / "run_all.sh", SCRIPT_DIR / "run_all.ps1"]
    complete = all(file_ok(path) for path in runner_paths)
    add(
        rows,
        "reproducibility",
        "One-command runners exist for Unix/Windows paths",
        status(complete),
        "; ".join(f"{path.name}={path.exists()}" for path in runner_paths),
        "" if complete else "Expected Makefile, script/run_all.sh, and script/run_all.ps1.",
    )
    runner_text = {path.name: path.read_text(encoding="utf-8", errors="ignore") if path.exists() else "" for path in runner_paths}
    missing_runner_scripts = [
        f"{runner}:{script_name}"
        for runner, text in runner_text.items()
        for script_name in PROMOTION_REPRODUCTION_SCRIPTS
        if script_name not in text
    ]
    add(
        rows,
        "reproducibility",
        "One-command runners include the current 157-191 dataset-promotion gate chain",
        status(not missing_runner_scripts),
        f"checked_runners={len(runner_paths)}; required_scripts={len(PROMOTION_REPRODUCTION_SCRIPTS)}; missing={len(missing_runner_scripts)}",
        "" if not missing_runner_scripts else "; ".join(missing_runner_scripts[:20]),
    )


def validate_artifacts(rows: list[dict[str, Any]]) -> None:
    counts = {
        "source_inventory": row_count(TEMP_DIR / "source_inventory.csv"),
        "country_wave_screening": row_count(TEMP_DIR / "country_wave_screening.csv"),
        "manual_download_manifest": row_count(TEMP_DIR / "manual_download_manifest.csv"),
        "manual_file_checklist": row_count(TEMP_DIR / "manual_download_file_checklist.csv"),
        "manual_access_action_queue": row_count(TEMP_DIR / "manual_access_action_queue.csv"),
        "external_repository_probe": row_count(TEMP_DIR / "external_repository_probe.csv"),
        "worldbank_public_documentation_audit": row_count(TEMP_DIR / "worldbank_public_documentation_audit.csv"),
        "raw_download_file_manifest": row_count(TEMP_DIR / "raw_download_file_manifest.csv"),
        "raw_download_target_audit": row_count(TEMP_DIR / "raw_download_target_audit.csv"),
        "raw_download_intake_manifest": row_count(TEMP_DIR / "raw_download_intake_manifest.csv"),
        "raw_download_expected_files": row_count(TEMP_DIR / "raw_download_expected_files.csv"),
        "raw_download_intake_summary": row_count(RESULT_DIR / "raw_download_intake_summary.csv"),
        "climate_source_probe": row_count(TEMP_DIR / "climate_source_probe.csv"),
        "validation_reference_source_probe": row_count(TEMP_DIR / "validation_reference_source_probe.csv"),
        "validation_reference_indicator_sample": row_count(TEMP_DIR / "validation_reference_indicator_sample.csv"),
        "hefpi_uhc_series_catalog": row_count(TEMP_DIR / "hefpi_uhc_series_catalog.csv"),
        "hefpi_uhc_reference_sample": row_count(TEMP_DIR / "hefpi_uhc_reference_sample.csv"),
        "sample_selection_gate_audit": row_count(RESULT_DIR / "sample_selection_gate_audit.csv"),
        "sample_selection_gate_summary": row_count(RESULT_DIR / "sample_selection_gate_summary.csv"),
        "variable_map_confidence_audit": row_count(TEMP_DIR / "variable_map_confidence_audit.csv"),
        "metadata_quality_download_priority": row_count(TEMP_DIR / "metadata_quality_download_priority.csv"),
        "metadata_candidate_quality_audit": row_count(RESULT_DIR / "metadata_candidate_quality_audit.csv"),
        "metadata_candidate_quality_summary": row_count(RESULT_DIR / "metadata_candidate_quality_summary.csv"),
        "raw_ingestion_plan": row_count(TEMP_DIR / "raw_ingestion_plan.csv"),
        "raw_ingestion_concept_checklist": row_count(TEMP_DIR / "raw_ingestion_concept_checklist.csv"),
        "raw_ingestion_module_checklist": row_count(TEMP_DIR / "raw_ingestion_module_checklist.csv"),
        "raw_ingestion_plan_summary": row_count(RESULT_DIR / "raw_ingestion_plan_summary.csv"),
        "raw_variable_verification_protocol": row_count(TEMP_DIR / "raw_variable_verification_protocol.csv"),
        "harmonization_recipe_scaffold": row_count(TEMP_DIR / "harmonization_recipe_scaffold.csv"),
        "raw_variable_verification_summary": row_count(RESULT_DIR / "raw_variable_verification_summary.csv"),
        "harmonization_recipe_gate": row_count(TEMP_DIR / "harmonization_recipe_gate.csv"),
        "harmonization_value_audit_template": row_count(TEMP_DIR / "harmonization_value_audit_template.csv"),
        "harmonization_verified_candidates": row_count(TEMP_DIR / "harmonization_recipe_verified_candidates.csv"),
        "harmonization_readiness_matrix": row_count(RESULT_DIR / "harmonization_readiness_matrix.csv"),
        "harmonization_recipe_gate_summary": row_count(RESULT_DIR / "harmonization_recipe_gate_summary.csv"),
        "analysis_dataset_promotion_barrier_audit": row_count(TEMP_DIR / "analysis_dataset_promotion_barrier_audit.csv"),
        "analysis_dataset_promotion_barrier_summary": row_count(RESULT_DIR / "analysis_dataset_promotion_barrier_summary.csv"),
        "alb2002_harmonized_core_promotion_audit": row_count(TEMP_DIR / "alb2002_harmonized_household_core_promotion_audit.csv"),
        "alb2002_harmonized_core_promotion_summary": row_count(RESULT_DIR / "alb2002_harmonized_household_core_promotion_summary.csv"),
        "alb2002_limited_financial_outcome_promotion_audit": row_count(TEMP_DIR / "alb2002_limited_financial_outcome_promotion_audit.csv"),
        "alb2002_limited_financial_outcome_promotion_summary": row_count(RESULT_DIR / "alb2002_limited_financial_outcome_promotion_summary.csv"),
        "alb2002_limited_climate_exposure_promotion_audit": row_count(TEMP_DIR / "alb2002_limited_climate_exposure_promotion_audit.csv"),
        "alb2002_limited_climate_exposure_promotion_summary": row_count(RESULT_DIR / "alb2002_limited_climate_exposure_promotion_summary.csv"),
        "alb2002_limited_climate_linked_promotion_audit": row_count(TEMP_DIR / "alb2002_limited_climate_linked_promotion_audit.csv"),
        "alb2002_limited_climate_linked_promotion_summary": row_count(RESULT_DIR / "alb2002_limited_climate_linked_promotion_summary.csv"),
        "minimum_viable_acquisition_targets": row_count(RESULT_DIR / "minimum_viable_acquisition_targets.csv"),
        "minimum_viable_download_bundles": row_count(TEMP_DIR / "minimum_viable_download_bundles.csv"),
        "minimum_viable_acquisition_summary": row_count(RESULT_DIR / "minimum_viable_acquisition_summary.csv"),
        "public_external_downloads": row_count(TEMP_DIR / "public_external_raw_candidate_downloads.csv"),
        "public_external_download_summary": row_count(RESULT_DIR / "public_external_raw_candidate_download_summary.csv"),
        "climate_exposure_plan": row_count(TEMP_DIR / "climate_exposure_plan.csv"),
        "climate_exposure_specification": row_count(RESULT_DIR / "climate_exposure_specification.csv"),
        "climate_exposure_plan_summary": row_count(RESULT_DIR / "climate_exposure_plan_summary.csv"),
        "climate_linkage_requirements": row_count(TEMP_DIR / "climate_linkage_requirements.csv"),
        "climate_source_method_matrix": row_count(RESULT_DIR / "climate_source_method_matrix.csv"),
        "climate_exposure_validation_protocol": row_count(RESULT_DIR / "climate_exposure_validation_protocol.csv"),
        "climate_linkage_readiness": row_count(RESULT_DIR / "climate_linkage_readiness.csv"),
        "climate_validation_protocol_summary": row_count(RESULT_DIR / "climate_validation_protocol_summary.csv"),
        "outcome_denominator_plan": row_count(TEMP_DIR / "outcome_denominator_plan.csv"),
        "outcome_specification_plan": row_count(RESULT_DIR / "outcome_specification_plan.csv"),
        "outcome_denominator_plan_summary": row_count(RESULT_DIR / "outcome_denominator_plan_summary.csv"),
        "sdg382_denominator_requirements": row_count(TEMP_DIR / "sdg382_denominator_requirements.csv"),
        "sdg382_denominator_source_matrix": row_count(RESULT_DIR / "sdg382_denominator_source_matrix.csv"),
        "sdg382_denominator_country_wave_readiness": row_count(RESULT_DIR / "sdg382_denominator_country_wave_readiness.csv"),
        "sdg382_denominator_summary": row_count(RESULT_DIR / "sdg382_denominator_summary.csv"),
        "modeling_identification_plan": row_count(TEMP_DIR / "modeling_identification_plan.csv"),
        "modeling_validation_plan": row_count(RESULT_DIR / "modeling_validation_plan.csv"),
        "falsification_placebo_plan": row_count(RESULT_DIR / "falsification_placebo_plan.csv"),
        "policy_learning_plan": row_count(RESULT_DIR / "policy_learning_plan.csv"),
        "modeling_identification_plan_summary": row_count(RESULT_DIR / "modeling_identification_plan_summary.csv"),
        "mechanism_variable_requirements": row_count(TEMP_DIR / "mechanism_variable_requirements.csv"),
        "mechanism_pathway_protocol": row_count(RESULT_DIR / "mechanism_pathway_protocol.csv"),
        "mechanism_readiness_matrix": row_count(RESULT_DIR / "mechanism_readiness_matrix.csv"),
        "mechanism_analysis_protocol_summary": row_count(RESULT_DIR / "mechanism_analysis_protocol_summary.csv"),
        "empirical_readiness_dashboard": row_count(RESULT_DIR / "empirical_readiness_dashboard.csv"),
        "empirical_no_go_threshold_status": row_count(RESULT_DIR / "empirical_no_go_threshold_status.csv"),
        "empirical_readiness_dashboard_summary": row_count(RESULT_DIR / "empirical_readiness_dashboard_summary.csv"),
        "first_batch_raw_acquisition_checklist": row_count(TEMP_DIR / "first_batch_raw_acquisition_checklist.csv"),
        "first_batch_raw_file_targets": row_count(TEMP_DIR / "first_batch_raw_file_targets.csv"),
        "first_batch_raw_acquisition_summary": row_count(RESULT_DIR / "first_batch_raw_acquisition_summary.csv"),
        "first_batch_official_raw_access_probe": row_count(TEMP_DIR / "first_batch_official_raw_access_probe.csv"),
        "first_batch_official_raw_access_summary": row_count(RESULT_DIR / "first_batch_official_raw_access_summary.csv"),
        "first_batch_manual_download_handoff": row_count(TEMP_DIR / "first_batch_manual_download_handoff.csv"),
        "first_batch_manual_download_file_queue": row_count(TEMP_DIR / "first_batch_manual_download_file_queue.csv"),
        "first_batch_manual_download_handoff_summary": row_count(RESULT_DIR / "first_batch_manual_download_handoff_summary.csv"),
        "first_batch_public_documentation_audit": row_count(TEMP_DIR / "first_batch_public_documentation_audit.csv"),
        "first_batch_public_documentation_summary": row_count(RESULT_DIR / "first_batch_public_documentation_summary.csv"),
        "first_batch_file_source_traceability": row_count(TEMP_DIR / "first_batch_file_source_traceability.csv"),
        "first_batch_file_source_traceability_summary": row_count(RESULT_DIR / "first_batch_file_source_traceability_summary.csv"),
        "first_batch_merge_key_lineage_plan": row_count(TEMP_DIR / "first_batch_merge_key_lineage_plan.csv"),
        "first_batch_merge_key_candidate_variables": row_count(TEMP_DIR / "first_batch_merge_key_candidate_variables.csv"),
        "first_batch_merge_key_lineage_summary": row_count(RESULT_DIR / "first_batch_merge_key_lineage_summary.csv"),
        "first_batch_raw_value_key_audit": row_count(TEMP_DIR / "first_batch_raw_value_key_audit.csv"),
        "first_batch_raw_merge_key_audit": row_count(TEMP_DIR / "first_batch_raw_merge_key_audit.csv"),
        "first_batch_harmonization_value_audit_auto": row_count(TEMP_DIR / "first_batch_harmonization_value_audit_auto.csv"),
        "first_batch_raw_value_key_summary": row_count(RESULT_DIR / "first_batch_raw_value_key_summary.csv"),
        "alb2002_household_core_candidate": row_count(TEMP_DIR / "alb2002_household_core_candidate.csv"),
        "alb2002_household_core_merge_audit": row_count(TEMP_DIR / "alb2002_household_core_merge_audit.csv"),
        "alb2002_household_core_lineage": row_count(TEMP_DIR / "alb2002_household_core_lineage.csv"),
        "alb2002_household_core_candidate_summary": row_count(RESULT_DIR / "alb2002_household_core_candidate_summary.csv"),
        "alb2002_provisional_outcome_feasibility_audit": row_count(TEMP_DIR / "alb2002_provisional_outcome_feasibility_audit.csv"),
        "alb2002_provisional_outcome_feasibility_summary": row_count(RESULT_DIR / "alb2002_provisional_outcome_feasibility_summary.csv"),
        "alb2002_outcome_semantics_raw_value_audit": row_count(TEMP_DIR / "alb2002_outcome_semantics_raw_value_audit.csv"),
        "alb2002_outcome_semantics_raw_value_summary": row_count(RESULT_DIR / "alb2002_outcome_semantics_raw_value_summary.csv"),
        "alb2002_health_questionnaire_semantics_audit": row_count(TEMP_DIR / "alb2002_health_questionnaire_semantics_audit.csv"),
        "alb2002_health_questionnaire_semantics_summary": row_count(RESULT_DIR / "alb2002_health_questionnaire_semantics_summary.csv"),
        "alb2002_oop_aggregation_policy_audit": row_count(TEMP_DIR / "alb2002_oop_aggregation_policy_audit.csv"),
        "alb2002_oop_aggregation_policy_summary": row_count(RESULT_DIR / "alb2002_oop_aggregation_policy_summary.csv"),
        "alb2002_skip_missing_semantics_audit": row_count(TEMP_DIR / "alb2002_skip_missing_semantics_audit.csv"),
        "alb2002_skip_missing_semantics_summary": row_count(RESULT_DIR / "alb2002_skip_missing_semantics_summary.csv"),
        "alb2002_oop_skip_value_decision_audit": row_count(TEMP_DIR / "alb2002_oop_skip_value_decision_audit.csv"),
        "alb2002_oop_skip_value_decision_summary": row_count(RESULT_DIR / "alb2002_oop_skip_value_decision_summary.csv"),
        "alb2002_access_need_denominator_policy_audit": row_count(TEMP_DIR / "alb2002_access_need_denominator_policy_audit.csv"),
        "alb2002_access_need_denominator_policy_summary": row_count(RESULT_DIR / "alb2002_access_need_denominator_policy_summary.csv"),
        "alb2002_consumption_sdg_denominator_policy_audit": row_count(TEMP_DIR / "alb2002_consumption_sdg_denominator_policy_audit.csv"),
        "alb2002_consumption_sdg_denominator_policy_summary": row_count(RESULT_DIR / "alb2002_consumption_sdg_denominator_policy_summary.csv"),
        "alb2002_consumption_construction_source_audit": row_count(TEMP_DIR / "alb2002_consumption_construction_source_audit.csv"),
        "alb2002_consumption_construction_source_summary": row_count(RESULT_DIR / "alb2002_consumption_construction_source_summary.csv"),
        "alb2002_consumption_aggregate_metadata_crosswalk_audit": row_count(TEMP_DIR / "alb2002_consumption_aggregate_metadata_crosswalk_audit.csv"),
        "alb2002_consumption_aggregate_metadata_crosswalk_summary": row_count(RESULT_DIR / "alb2002_consumption_aggregate_metadata_crosswalk_summary.csv"),
        "alb2002_period_aligned_che_policy_audit": row_count(TEMP_DIR / "alb2002_period_aligned_che_policy_audit.csv"),
        "alb2002_period_aligned_che_policy_summary": row_count(RESULT_DIR / "alb2002_period_aligned_che_policy_summary.csv"),
        "alb2002_che_candidate_household_outcomes": row_count(TEMP_DIR / "alb2002_che_candidate_household_outcomes.csv"),
        "alb2002_che_candidate_outcome_lineage": row_count(TEMP_DIR / "alb2002_che_candidate_outcome_lineage.csv"),
        "alb2002_che_candidate_outcome_audit": row_count(RESULT_DIR / "alb2002_che_candidate_outcome_audit.csv"),
        "alb2002_che_candidate_outcome_summary": row_count(RESULT_DIR / "alb2002_che_candidate_outcome_summary.csv"),
        "alb2002_access_candidate_household_outcomes": row_count(TEMP_DIR / "alb2002_access_candidate_household_outcomes.csv"),
        "alb2002_access_candidate_outcome_lineage": row_count(TEMP_DIR / "alb2002_access_candidate_outcome_lineage.csv"),
        "alb2002_access_candidate_outcome_audit": row_count(RESULT_DIR / "alb2002_access_candidate_outcome_audit.csv"),
        "alb2002_access_candidate_outcome_summary": row_count(RESULT_DIR / "alb2002_access_candidate_outcome_summary.csv"),
        "alb2002_uhc_composite_candidate_outcomes": row_count(TEMP_DIR / "alb2002_uhc_composite_candidate_outcomes.csv"),
        "alb2002_uhc_composite_candidate_lineage": row_count(TEMP_DIR / "alb2002_uhc_composite_candidate_lineage.csv"),
        "alb2002_uhc_composite_candidate_audit": row_count(RESULT_DIR / "alb2002_uhc_composite_candidate_audit.csv"),
        "alb2002_uhc_composite_candidate_summary": row_count(RESULT_DIR / "alb2002_uhc_composite_candidate_summary.csv"),
        "alb2002_analysis_candidate_dataset": row_count(TEMP_DIR / "alb2002_analysis_candidate_dataset.csv"),
        "alb2002_analysis_candidate_lineage": row_count(TEMP_DIR / "alb2002_analysis_candidate_lineage.csv"),
        "alb2002_analysis_candidate_readiness_audit": row_count(RESULT_DIR / "alb2002_analysis_candidate_readiness_audit.csv"),
        "alb2002_analysis_candidate_readiness_summary": row_count(RESULT_DIR / "alb2002_analysis_candidate_readiness_summary.csv"),
        "alb2002_climate_centroid_exposure_input": row_count(TEMP_DIR / "alb2002_climate_centroid_exposure_input.csv"),
        "alb2002_climate_centroid_exposure_candidates": row_count(TEMP_DIR / "alb2002_climate_centroid_exposure_candidates.csv"),
        "alb2002_climate_centroid_nasa_api_manifest": row_count(TEMP_DIR / "alb2002_climate_centroid_nasa_power_api_manifest.csv"),
        "alb2002_climate_centroid_exposure_audit": row_count(RESULT_DIR / "alb2002_climate_centroid_exposure_audit.csv"),
        "alb2002_climate_centroid_exposure_summary": row_count(RESULT_DIR / "alb2002_climate_centroid_exposure_summary.csv"),
        "alb2002_climate_shock_candidate_exposures": row_count(TEMP_DIR / "alb2002_climate_shock_candidate_exposures.csv"),
        "alb2002_climate_shock_candidate_lineage": row_count(TEMP_DIR / "alb2002_climate_shock_candidate_lineage.csv"),
        "alb2002_climate_shock_candidate_audit": row_count(RESULT_DIR / "alb2002_climate_shock_candidate_audit.csv"),
        "alb2002_climate_shock_candidate_summary": row_count(RESULT_DIR / "alb2002_climate_shock_candidate_summary.csv"),
        "alb2002_climate_outcome_linked_candidate": row_count(TEMP_DIR / "alb2002_climate_outcome_linked_candidate.csv"),
        "alb2002_climate_outcome_linked_candidate_lineage": row_count(TEMP_DIR / "alb2002_climate_outcome_linked_candidate_lineage.csv"),
        "alb2002_climate_outcome_linked_candidate_audit": row_count(RESULT_DIR / "alb2002_climate_outcome_linked_candidate_audit.csv"),
        "alb2002_climate_outcome_linked_candidate_summary": row_count(RESULT_DIR / "alb2002_climate_outcome_linked_candidate_summary.csv"),
        "alb2002_linked_candidate_descriptive_audit": row_count(RESULT_DIR / "alb2002_linked_candidate_descriptive_audit.csv"),
        "alb2002_linked_candidate_descriptive_cells": row_count(RESULT_DIR / "alb2002_linked_candidate_descriptive_cells.csv"),
        "alb2002_linked_candidate_descriptive_summary": row_count(RESULT_DIR / "alb2002_linked_candidate_descriptive_summary.csv"),
        "alb2002_weight_design_evidence_audit": row_count(TEMP_DIR / "alb2002_weight_design_evidence_audit.csv"),
        "alb2002_weight_design_evidence_summary": row_count(RESULT_DIR / "alb2002_weight_design_evidence_summary.csv"),
        "alb2002_minimum_recipe_promotion_action_queue": row_count(TEMP_DIR / "alb2002_minimum_recipe_promotion_action_queue.csv"),
        "alb2002_minimum_recipe_promotion_gate_checklist": row_count(TEMP_DIR / "alb2002_minimum_recipe_promotion_gate_checklist.csv"),
        "alb2002_minimum_recipe_promotion_summary": row_count(RESULT_DIR / "alb2002_minimum_recipe_promotion_summary.csv"),
        "alb2002_district_climate_crosswalk_template": row_count(TEMP_DIR / "alb2002_district_climate_crosswalk_template.csv"),
        "alb2002_district_boundary_source_probe": row_count(TEMP_DIR / "alb2002_district_boundary_source_probe.csv"),
        "alb2002_district_climate_crosswalk_summary": row_count(RESULT_DIR / "alb2002_district_climate_crosswalk_summary.csv"),
        "alb2002_boundary_name_match_audit": row_count(TEMP_DIR / "alb2002_boundary_name_match_audit.csv"),
        "alb2002_boundary_geojson_inventory": row_count(TEMP_DIR / "alb2002_boundary_geojson_inventory.csv"),
        "alb2002_boundary_name_match_summary": row_count(RESULT_DIR / "alb2002_boundary_name_match_summary.csv"),
        "alb2002_boundary_source_alternative_audit": row_count(TEMP_DIR / "alb2002_boundary_source_alternative_audit.csv"),
        "alb2002_boundary_source_alternative_summary": row_count(RESULT_DIR / "alb2002_boundary_source_alternative_summary.csv"),
        "alb2002_boundary_source_resource_search_audit": row_count(TEMP_DIR / "alb2002_boundary_source_resource_search_audit.csv"),
        "alb2002_boundary_source_resource_search_summary": row_count(RESULT_DIR / "alb2002_boundary_source_resource_search_summary.csv"),
        "alb2002_boundary_geometry_provenance_audit": row_count(TEMP_DIR / "alb2002_boundary_geometry_provenance_audit.csv"),
        "alb2002_boundary_metadata_provenance_probe": row_count(TEMP_DIR / "alb2002_boundary_metadata_provenance_probe.csv"),
        "alb2002_boundary_geometry_provenance_summary": row_count(RESULT_DIR / "alb2002_boundary_geometry_provenance_summary.csv"),
        "alb2002_boundary_manual_verification_action_queue": row_count(TEMP_DIR / "alb2002_boundary_manual_verification_action_queue.csv"),
        "alb2002_boundary_promotion_gate_checklist": row_count(TEMP_DIR / "alb2002_boundary_promotion_gate_checklist.csv"),
        "alb2002_boundary_manual_verification_packet_summary": row_count(RESULT_DIR / "alb2002_boundary_manual_verification_packet_summary.csv"),
        "alb2002_boundary_manual_source_followup_audit": row_count(TEMP_DIR / "alb2002_boundary_manual_source_followup_audit.csv"),
        "alb2002_boundary_manual_source_followup_summary": row_count(RESULT_DIR / "alb2002_boundary_manual_source_followup_summary.csv"),
        "alb2002_local_geography_artifact_audit": row_count(TEMP_DIR / "alb2002_local_geography_artifact_audit.csv"),
        "alb2002_local_geography_artifact_summary": row_count(RESULT_DIR / "alb2002_local_geography_artifact_summary.csv"),
        "alb2012_household_core_candidate": row_count(TEMP_DIR / "alb2012_household_core_candidate.csv"),
        "alb2012_raw_core_feasibility_audit": row_count(TEMP_DIR / "alb2012_raw_core_feasibility_audit.csv"),
        "alb2012_raw_core_lineage": row_count(TEMP_DIR / "alb2012_raw_core_lineage.csv"),
        "alb2012_raw_core_feasibility_summary": row_count(RESULT_DIR / "alb2012_raw_core_feasibility_summary.csv"),
        "alb2012_provisional_outcome_feasibility_audit": row_count(TEMP_DIR / "alb2012_provisional_outcome_feasibility_audit.csv"),
        "alb2012_provisional_outcome_feasibility_summary": row_count(RESULT_DIR / "alb2012_provisional_outcome_feasibility_summary.csv"),
        "alb2012_outcome_semantics_raw_value_audit": row_count(TEMP_DIR / "alb2012_outcome_semantics_raw_value_audit.csv"),
        "alb2012_outcome_semantics_raw_value_summary": row_count(RESULT_DIR / "alb2012_outcome_semantics_raw_value_summary.csv"),
        "alb2012_timing_geography_exhaustive_audit": row_count(TEMP_DIR / "alb2012_timing_geography_exhaustive_audit.csv"),
        "alb2012_timing_geography_exhaustive_summary": row_count(RESULT_DIR / "alb2012_timing_geography_exhaustive_summary.csv"),
        "alb2012_questionnaire_timing_field_audit": row_count(TEMP_DIR / "alb2012_questionnaire_timing_field_audit.csv"),
        "alb2012_questionnaire_timing_raw_gap_audit": row_count(TEMP_DIR / "alb2012_questionnaire_timing_raw_gap_audit.csv"),
        "alb2012_questionnaire_timing_field_summary": row_count(RESULT_DIR / "alb2012_questionnaire_timing_field_summary.csv"),
        "albania_legacy_questionnaire_readability_audit": row_count(TEMP_DIR / "albania_legacy_questionnaire_readability_audit.csv"),
        "albania_legacy_questionnaire_readability_summary": row_count(RESULT_DIR / "albania_legacy_questionnaire_readability_summary.csv"),
        "albania_legacy_questionnaire_timing_field_audit": row_count(TEMP_DIR / "albania_legacy_questionnaire_timing_field_audit.csv"),
        "albania_legacy_questionnaire_timing_raw_gap_audit": row_count(TEMP_DIR / "albania_legacy_questionnaire_timing_raw_gap_audit.csv"),
        "albania_legacy_questionnaire_timing_field_summary": row_count(RESULT_DIR / "albania_legacy_questionnaire_timing_field_summary.csv"),
        "alb2005_documented_variable_evidence": row_count(TEMP_DIR / "alb2005_documented_variable_evidence.csv"),
        "alb2005_documented_harmonization_summary": row_count(RESULT_DIR / "alb2005_documented_harmonization_summary.csv"),
        "alb2005_household_core_candidate": row_count(TEMP_DIR / "alb2005_household_core_candidate.csv"),
        "alb2005_household_core_merge_audit": row_count(TEMP_DIR / "alb2005_household_core_merge_audit.csv"),
        "alb2005_household_core_lineage": row_count(TEMP_DIR / "alb2005_household_core_lineage.csv"),
        "alb2005_household_core_candidate_summary": row_count(RESULT_DIR / "alb2005_household_core_candidate_summary.csv"),
        "alb2005_provisional_outcome_feasibility_audit": row_count(TEMP_DIR / "alb2005_provisional_outcome_feasibility_audit.csv"),
        "alb2005_provisional_outcome_feasibility_summary": row_count(RESULT_DIR / "alb2005_provisional_outcome_feasibility_summary.csv"),
        "alb2005_outcome_semantics_raw_value_audit": row_count(TEMP_DIR / "alb2005_outcome_semantics_raw_value_audit.csv"),
        "alb2005_outcome_semantics_raw_value_summary": row_count(RESULT_DIR / "alb2005_outcome_semantics_raw_value_summary.csv"),
        "alb2005_timing_geography_exhaustive_audit": row_count(TEMP_DIR / "alb2005_timing_geography_exhaustive_audit.csv"),
        "alb2005_timing_geography_exhaustive_summary": row_count(RESULT_DIR / "alb2005_timing_geography_exhaustive_summary.csv"),
        "alb2005_harmonization_value_decision_audit": row_count(TEMP_DIR / "alb2005_harmonization_value_decision_audit.csv"),
        "alb2005_harmonization_value_decision_summary": row_count(RESULT_DIR / "alb2005_harmonization_value_decision_summary.csv"),
        "alb2005_required_value_key_audit": row_count(TEMP_DIR / "alb2005_required_value_key_audit.csv"),
        "alb2005_required_value_key_summary": row_count(RESULT_DIR / "alb2005_required_value_key_summary.csv"),
        "alb2005_health_questionnaire_semantics_audit": row_count(TEMP_DIR / "alb2005_health_questionnaire_semantics_audit.csv"),
        "alb2005_health_questionnaire_semantics_summary": row_count(RESULT_DIR / "alb2005_health_questionnaire_semantics_summary.csv"),
        "alb2005_oop_aggregation_policy_audit": row_count(TEMP_DIR / "alb2005_oop_aggregation_policy_audit.csv"),
        "alb2005_oop_aggregation_policy_summary": row_count(RESULT_DIR / "alb2005_oop_aggregation_policy_summary.csv"),
        "alb2005_skip_missing_semantics_audit": row_count(TEMP_DIR / "alb2005_skip_missing_semantics_audit.csv"),
        "alb2005_skip_missing_semantics_summary": row_count(RESULT_DIR / "alb2005_skip_missing_semantics_summary.csv"),
        "alb2005_consumption_oop_unit_period_audit": row_count(TEMP_DIR / "alb2005_consumption_oop_unit_period_audit.csv"),
        "alb2005_consumption_oop_unit_period_summary": row_count(RESULT_DIR / "alb2005_consumption_oop_unit_period_summary.csv"),
        "alb2005_consumption_aggregate_crosswalk_audit": row_count(TEMP_DIR / "alb2005_consumption_aggregate_metadata_crosswalk_audit.csv"),
        "alb2005_consumption_aggregate_crosswalk_summary": row_count(RESULT_DIR / "alb2005_consumption_aggregate_metadata_crosswalk_summary.csv"),
        "alb2005_consumption_component_source_search_audit": row_count(TEMP_DIR / "alb2005_consumption_component_source_search_audit.csv"),
        "alb2005_consumption_component_source_search_summary": row_count(RESULT_DIR / "alb2005_consumption_component_source_search_summary.csv"),
        "alb2005_timing_geography_source_search_audit": row_count(TEMP_DIR / "alb2005_timing_geography_source_search_audit.csv"),
        "alb2005_timing_geography_source_search_summary": row_count(RESULT_DIR / "alb2005_timing_geography_source_search_summary.csv"),
        "alb2005_minimum_recipe_promotion_action_queue": row_count(TEMP_DIR / "alb2005_minimum_recipe_promotion_action_queue.csv"),
        "alb2005_minimum_recipe_promotion_gate_checklist": row_count(TEMP_DIR / "alb2005_minimum_recipe_promotion_gate_checklist.csv"),
        "alb2005_minimum_recipe_promotion_summary": row_count(RESULT_DIR / "alb2005_minimum_recipe_promotion_summary.csv"),
        "alb2005_public_fieldwork_geo_metadata_audit": row_count(TEMP_DIR / "alb2005_public_fieldwork_geo_metadata_audit.csv"),
        "alb2005_public_fieldwork_geo_metadata_summary": row_count(RESULT_DIR / "alb2005_public_fieldwork_geo_metadata_summary.csv"),
        "alb2005_diary_timing_candidate_audit": row_count(TEMP_DIR / "alb2005_diary_timing_candidate_audit.csv"),
        "alb2005_diary_timing_candidate_summary": row_count(RESULT_DIR / "alb2005_diary_timing_candidate_summary.csv"),
        "alb2005_extracted_module_coverage_audit": row_count(TEMP_DIR / "alb2005_extracted_module_coverage_audit.csv"),
        "alb2005_extracted_extra_files_audit": row_count(TEMP_DIR / "alb2005_extracted_extra_files_audit.csv"),
        "alb2005_archive_member_manifest": row_count(TEMP_DIR / "alb2005_archive_member_manifest.csv"),
        "alb2005_extracted_module_coverage_summary": row_count(RESULT_DIR / "alb2005_extracted_module_coverage_summary.csv"),
        "alb2005_fallback_blocker_resolution_matrix": row_count(TEMP_DIR / "alb2005_fallback_blocker_resolution_matrix.csv"),
        "alb2005_fallback_blocker_resolution_summary": row_count(RESULT_DIR / "alb2005_fallback_blocker_resolution_summary.csv"),
        "albania_existing_raw_wave_audit": row_count(TEMP_DIR / "albania_existing_raw_wave_audit.csv"),
        "albania_existing_raw_wave_audit_summary": row_count(RESULT_DIR / "albania_existing_raw_wave_audit_summary.csv"),
        "alb2008_household_core_candidate": row_count(TEMP_DIR / "alb2008_household_core_candidate.csv"),
        "alb2008_household_core_merge_audit": row_count(TEMP_DIR / "alb2008_household_core_merge_audit.csv"),
        "alb2008_household_core_lineage": row_count(TEMP_DIR / "alb2008_household_core_lineage.csv"),
        "alb2008_household_core_candidate_summary": row_count(RESULT_DIR / "alb2008_household_core_candidate_summary.csv"),
        "alb2008_provisional_outcome_feasibility_audit": row_count(TEMP_DIR / "alb2008_provisional_outcome_feasibility_audit.csv"),
        "alb2008_provisional_outcome_feasibility_summary": row_count(RESULT_DIR / "alb2008_provisional_outcome_feasibility_summary.csv"),
        "alb2008_outcome_semantics_raw_value_audit": row_count(TEMP_DIR / "alb2008_outcome_semantics_raw_value_audit.csv"),
        "alb2008_outcome_semantics_raw_value_summary": row_count(RESULT_DIR / "alb2008_outcome_semantics_raw_value_summary.csv"),
        "alb2008_timing_geography_exhaustive_audit": row_count(TEMP_DIR / "alb2008_timing_geography_exhaustive_audit.csv"),
        "alb2008_timing_geography_exhaustive_summary": row_count(RESULT_DIR / "alb2008_timing_geography_exhaustive_summary.csv"),
        "alb2008_fallback_blocker_resolution_matrix": row_count(TEMP_DIR / "alb2008_fallback_blocker_resolution_matrix.csv"),
        "alb2008_fallback_blocker_resolution_summary": row_count(RESULT_DIR / "alb2008_fallback_blocker_resolution_summary.csv"),
        "first_batch_dataset_verification_gate": row_count(RESULT_DIR / "first_batch_dataset_verification_gate.csv"),
        "first_batch_concept_verification_template": row_count(TEMP_DIR / "first_batch_concept_verification_template.csv"),
        "first_batch_variable_verification_template": row_count(TEMP_DIR / "first_batch_variable_verification_template.csv"),
        "first_batch_raw_verification_workbook_summary": row_count(RESULT_DIR / "first_batch_raw_verification_workbook_summary.csv"),
        "direct_read_audit_bundle": row_count(RESULT_DIR / "direct_read_audit_bundle.csv"),
        "direct_read_artifact_manifest": row_count(RESULT_DIR / "direct_read_artifact_manifest.csv"),
        "direct_read_audit_bundle_summary": row_count(RESULT_DIR / "direct_read_audit_bundle_summary.csv"),
        "promoted_country_wave_registry": row_count(RESULT_DIR / "promoted_country_wave_registry.csv"),
        "country_wave_promotion_gate_audit": row_count(RESULT_DIR / "country_wave_promotion_gate_audit.csv"),
        "country_wave_promotion_summary": row_count(RESULT_DIR / "country_wave_promotion_summary.csv"),
        "priority_country_wave_download_queue": row_count(RESULT_DIR / "priority_country_wave_download_queue.csv"),
        "priority_promotion_acquisition_wave_plan": row_count(RESULT_DIR / "priority_promotion_acquisition_wave_plan.csv"),
        "priority_promotion_acquisition_file_queue": row_count(RESULT_DIR / "priority_promotion_acquisition_file_queue.csv"),
        "priority_promotion_acquisition_summary": row_count(RESULT_DIR / "priority_promotion_acquisition_summary.csv"),
        "priority_official_raw_access_probe": row_count(TEMP_DIR / "priority_official_raw_access_probe.csv"),
        "priority_official_raw_access_summary": row_count(RESULT_DIR / "priority_official_raw_access_summary.csv"),
        "priority_raw_intake_gate": row_count(TEMP_DIR / "priority_raw_intake_gate.csv"),
        "priority_raw_file_targets": row_count(TEMP_DIR / "priority_raw_file_targets.csv"),
        "priority_raw_intake_gate_summary": row_count(RESULT_DIR / "priority_raw_intake_gate_summary.csv"),
        "priority_archive_member_inventory": row_count(TEMP_DIR / "priority_archive_member_inventory.csv"),
        "priority_archive_completeness_matrix": row_count(TEMP_DIR / "priority_archive_completeness_matrix.csv"),
        "priority_archive_member_preflight_summary": row_count(RESULT_DIR / "priority_archive_member_preflight_summary.csv"),
        "priority_climate_linkage_preflight": row_count(TEMP_DIR / "priority_climate_linkage_preflight.csv"),
        "priority_climate_linkage_requirements": row_count(TEMP_DIR / "priority_climate_linkage_requirements.csv"),
        "priority_climate_linkage_preflight_summary": row_count(RESULT_DIR / "priority_climate_linkage_preflight_summary.csv"),
        "priority_dataset_verification_gate": row_count(RESULT_DIR / "priority_dataset_verification_gate.csv"),
        "priority_promotion_verification_checklist": row_count(TEMP_DIR / "priority_promotion_verification_checklist.csv"),
        "priority_concept_verification_template": row_count(TEMP_DIR / "priority_concept_verification_template.csv"),
        "priority_variable_verification_template": row_count(TEMP_DIR / "priority_variable_verification_template.csv"),
        "priority_raw_verification_workbook_summary": row_count(RESULT_DIR / "priority_raw_verification_workbook_summary.csv"),
        "priority_manual_verification_decision_gate": row_count(TEMP_DIR / "priority_manual_verification_decision_gate.csv"),
        "priority_manual_requirement_decision_audit": row_count(TEMP_DIR / "priority_manual_requirement_decision_audit.csv"),
        "priority_manual_concept_decision_audit": row_count(TEMP_DIR / "priority_manual_concept_decision_audit.csv"),
        "priority_manual_variable_decision_audit": row_count(TEMP_DIR / "priority_manual_variable_decision_audit.csv"),
        "priority_manual_verification_decision_summary": row_count(RESULT_DIR / "priority_manual_verification_decision_summary.csv"),
        "priority_raw_package_receipt_ledger": row_count(TEMP_DIR / "priority_raw_package_receipt_ledger.csv"),
        "priority_raw_package_file_manifest": row_count(TEMP_DIR / "priority_raw_package_file_manifest.csv"),
        "priority_raw_package_missing_targets": row_count(TEMP_DIR / "priority_raw_package_missing_targets.csv"),
        "priority_raw_package_receipt_summary": row_count(RESULT_DIR / "priority_raw_package_receipt_summary.csv"),
        "priority_official_download_dossier": row_count(TEMP_DIR / "priority_official_download_dossier.csv"),
        "priority_official_full_file_inventory": row_count(TEMP_DIR / "priority_official_full_file_inventory.csv"),
        "priority_official_documentation_links": row_count(TEMP_DIR / "priority_official_documentation_links.csv"),
        "priority_official_download_dossier_summary": row_count(RESULT_DIR / "priority_official_download_dossier_summary.csv"),
        "priority_public_documentation_receipt": row_count(TEMP_DIR / "priority_public_documentation_receipt.csv"),
        "priority_public_documentation_dataset_receipt": row_count(TEMP_DIR / "priority_public_documentation_dataset_receipt.csv"),
        "priority_public_documentation_receipt_summary": row_count(RESULT_DIR / "priority_public_documentation_receipt_summary.csv"),
        "priority_official_metadata_variable_evidence": row_count(TEMP_DIR / "priority_official_metadata_variable_evidence.csv"),
        "priority_official_metadata_category_evidence": row_count(TEMP_DIR / "priority_official_metadata_category_evidence.csv"),
        "priority_official_metadata_dataset_evidence": row_count(TEMP_DIR / "priority_official_metadata_dataset_evidence.csv"),
        "priority_official_metadata_evidence_summary": row_count(RESULT_DIR / "priority_official_metadata_evidence_summary.csv"),
        "priority_credentialed_raw_acquisition_ledger": row_count(TEMP_DIR / "priority_credentialed_raw_acquisition_ledger.csv"),
        "priority_credentialed_raw_full_file_manifest": row_count(TEMP_DIR / "priority_credentialed_raw_full_file_manifest.csv"),
        "priority_credentialed_raw_core_file_checklist": row_count(TEMP_DIR / "priority_credentialed_raw_core_file_checklist.csv"),
        "priority_credentialed_raw_acquisition_summary": row_count(RESULT_DIR / "priority_credentialed_raw_acquisition_summary.csv"),
        "priority_official_endpoint_matrix": row_count(TEMP_DIR / "priority_official_endpoint_matrix.csv"),
        "priority_official_endpoint_dataset_matrix": row_count(TEMP_DIR / "priority_official_endpoint_dataset_matrix.csv"),
        "priority_official_endpoint_matrix_summary": row_count(RESULT_DIR / "priority_official_endpoint_matrix_summary.csv"),
        "priority_core_file_endpoint_matrix": row_count(TEMP_DIR / "priority_core_file_endpoint_matrix.csv"),
        "priority_core_file_endpoint_dataset_matrix": row_count(TEMP_DIR / "priority_core_file_endpoint_dataset_matrix.csv"),
        "priority_core_file_endpoint_matrix_summary": row_count(RESULT_DIR / "priority_core_file_endpoint_matrix_summary.csv"),
        "priority_threshold_acquisition_campaign": row_count(TEMP_DIR / "priority_threshold_acquisition_campaign.csv"),
        "priority_threshold_country_coverage": row_count(TEMP_DIR / "priority_threshold_country_coverage.csv"),
        "priority_threshold_acquisition_campaign_summary": row_count(RESULT_DIR / "priority_threshold_acquisition_campaign_summary.csv"),
        "priority_first_pass_variable_review_queue": row_count(TEMP_DIR / "priority_first_pass_variable_review_queue.csv"),
        "priority_first_pass_requirement_coverage": row_count(TEMP_DIR / "priority_first_pass_requirement_coverage.csv"),
        "priority_first_pass_variable_review_summary": row_count(RESULT_DIR / "priority_first_pass_variable_review_summary.csv"),
        "priority_download_execution_packet": row_count(TEMP_DIR / "priority_download_execution_packet.csv"),
        "priority_download_file_acceptance_matrix": row_count(TEMP_DIR / "priority_download_file_acceptance_matrix.csv"),
        "priority_download_execution_packet_summary": row_count(RESULT_DIR / "priority_download_execution_packet_summary.csv"),
        "priority_lsms_isa_alignment_audit": row_count(TEMP_DIR / "priority_lsms_isa_alignment_audit.csv"),
        "priority_lsms_isa_replacement_candidates": row_count(TEMP_DIR / "priority_lsms_isa_replacement_candidates.csv"),
        "priority_lsms_isa_alignment_summary": row_count(RESULT_DIR / "priority_lsms_isa_alignment_summary.csv"),
        "priority_lsms_isa_refocused_wave_plan": row_count(RESULT_DIR / "priority_lsms_isa_refocused_wave_plan.csv"),
        "priority_lsms_isa_refocused_acquisition_queue": row_count(TEMP_DIR / "priority_lsms_isa_refocused_acquisition_queue.csv"),
        "priority_lsms_isa_refocused_requirement_matrix": row_count(TEMP_DIR / "priority_lsms_isa_refocused_requirement_matrix.csv"),
        "priority_lsms_isa_refocused_acquisition_summary": row_count(RESULT_DIR / "priority_lsms_isa_refocused_acquisition_summary.csv"),
        "priority_lsms_isa_public_documentation_receipt": row_count(TEMP_DIR / "priority_lsms_isa_public_documentation_receipt.csv"),
        "priority_lsms_isa_public_documentation_dataset_receipt": row_count(TEMP_DIR / "priority_lsms_isa_public_documentation_dataset_receipt.csv"),
        "priority_lsms_isa_public_documentation_catalog_digest": row_count(TEMP_DIR / "priority_lsms_isa_public_documentation_catalog_digest.csv"),
        "priority_lsms_isa_public_documentation_file_inventory": row_count(TEMP_DIR / "priority_lsms_isa_public_documentation_file_inventory.csv"),
        "priority_lsms_isa_public_documentation_receipt_summary": row_count(RESULT_DIR / "priority_lsms_isa_public_documentation_receipt_summary.csv"),
        "priority_lsms_isa_variable_evidence_matrix": row_count(TEMP_DIR / "priority_lsms_isa_variable_evidence_matrix.csv"),
        "priority_lsms_isa_requirement_variable_coverage": row_count(TEMP_DIR / "priority_lsms_isa_requirement_variable_coverage.csv"),
        "priority_lsms_isa_concept_file_shortlist": row_count(TEMP_DIR / "priority_lsms_isa_concept_file_shortlist.csv"),
        "priority_lsms_isa_variable_evidence_summary": row_count(RESULT_DIR / "priority_lsms_isa_variable_evidence_summary.csv"),
        "priority_lsms_isa_raw_package_intake_ledger": row_count(TEMP_DIR / "priority_lsms_isa_raw_package_intake_ledger.csv"),
        "priority_lsms_isa_raw_package_file_manifest": row_count(TEMP_DIR / "priority_lsms_isa_raw_package_file_manifest.csv"),
        "priority_lsms_isa_raw_package_acceptance_matrix": row_count(TEMP_DIR / "priority_lsms_isa_raw_package_acceptance_matrix.csv"),
        "priority_lsms_isa_raw_package_intake_summary": row_count(RESULT_DIR / "priority_lsms_isa_raw_package_intake_summary.csv"),
        "priority_lsms_isa_archive_member_preflight": row_count(TEMP_DIR / "priority_lsms_isa_archive_member_preflight.csv"),
        "priority_lsms_isa_archive_member_manifest": row_count(TEMP_DIR / "priority_lsms_isa_archive_member_manifest.csv"),
        "priority_lsms_isa_direct_file_preflight": row_count(TEMP_DIR / "priority_lsms_isa_direct_file_preflight.csv"),
        "priority_lsms_isa_archive_requirement_preflight": row_count(TEMP_DIR / "priority_lsms_isa_archive_requirement_preflight.csv"),
        "priority_lsms_isa_archive_member_preflight_summary": row_count(RESULT_DIR / "priority_lsms_isa_archive_member_preflight_summary.csv"),
        "priority_lsms_isa_raw_value_requirement_workbook": row_count(TEMP_DIR / "priority_lsms_isa_raw_value_requirement_workbook.csv"),
        "priority_lsms_isa_raw_value_variable_workbook": row_count(TEMP_DIR / "priority_lsms_isa_raw_value_variable_workbook.csv"),
        "priority_lsms_isa_raw_value_file_workbook": row_count(TEMP_DIR / "priority_lsms_isa_raw_value_file_workbook.csv"),
        "priority_lsms_isa_raw_value_verification_workbook_summary": row_count(RESULT_DIR / "priority_lsms_isa_raw_value_verification_workbook_summary.csv"),
        "priority_lsms_isa_raw_package_receipt_checklist": row_count(TEMP_DIR / "priority_lsms_isa_raw_package_receipt_checklist.csv"),
        "priority_lsms_isa_raw_package_requirement_receipt_checklist": row_count(TEMP_DIR / "priority_lsms_isa_raw_package_requirement_receipt_checklist.csv"),
        "priority_lsms_isa_raw_package_receipt_checklist_summary": row_count(RESULT_DIR / "priority_lsms_isa_raw_package_receipt_checklist_summary.csv"),
        "priority_lsms_isa_credentialed_raw_acquisition_workbench": row_count(TEMP_DIR / "priority_lsms_isa_credentialed_raw_acquisition_workbench.csv"),
        "priority_lsms_isa_credentialed_raw_full_file_manifest": row_count(TEMP_DIR / "priority_lsms_isa_credentialed_raw_full_file_manifest.csv"),
        "priority_lsms_isa_credentialed_raw_core_file_checklist": row_count(TEMP_DIR / "priority_lsms_isa_credentialed_raw_core_file_checklist.csv"),
        "priority_lsms_isa_credentialed_raw_acquisition_workbench_summary": row_count(RESULT_DIR / "priority_lsms_isa_credentialed_raw_acquisition_workbench_summary.csv"),
        "priority_lsms_isa_official_file_receipt_validation": row_count(TEMP_DIR / "priority_lsms_isa_official_file_receipt_validation.csv"),
        "priority_lsms_isa_official_file_receipt_file_match": row_count(TEMP_DIR / "priority_lsms_isa_official_file_receipt_file_match.csv"),
        "priority_lsms_isa_official_file_receipt_core_match": row_count(TEMP_DIR / "priority_lsms_isa_official_file_receipt_core_match.csv"),
        "priority_lsms_isa_official_file_receipt_validator_summary": row_count(RESULT_DIR / "priority_lsms_isa_official_file_receipt_validator_summary.csv"),
        "priority_lsms_isa_threshold_download_sequence": row_count(TEMP_DIR / "priority_lsms_isa_threshold_download_sequence.csv"),
        "priority_lsms_isa_threshold_minimum_batch": row_count(TEMP_DIR / "priority_lsms_isa_threshold_minimum_batch.csv"),
        "priority_lsms_isa_threshold_country_coverage": row_count(TEMP_DIR / "priority_lsms_isa_threshold_country_coverage.csv"),
        "priority_lsms_isa_threshold_download_sequence_summary": row_count(RESULT_DIR / "priority_lsms_isa_threshold_download_sequence_summary.csv"),
        "priority_lsms_isa_minimum_batch_raw_intake_guide": row_count(TEMP_DIR / "priority_lsms_isa_minimum_batch_raw_intake_guide.csv"),
        "priority_lsms_isa_minimum_batch_expected_file_manifest": row_count(TEMP_DIR / "priority_lsms_isa_minimum_batch_expected_file_manifest.csv"),
        "priority_lsms_isa_minimum_batch_core_file_manifest": row_count(TEMP_DIR / "priority_lsms_isa_minimum_batch_core_file_manifest.csv"),
        "priority_lsms_isa_minimum_batch_raw_intake_guide_summary": row_count(RESULT_DIR / "priority_lsms_isa_minimum_batch_raw_intake_guide_summary.csv"),
        "priority_lsms_isa_minimum_batch_endpoint_refresh": row_count(TEMP_DIR / "priority_lsms_isa_minimum_batch_endpoint_refresh.csv"),
        "priority_lsms_isa_minimum_batch_endpoint_dataset_status": row_count(TEMP_DIR / "priority_lsms_isa_minimum_batch_endpoint_dataset_status.csv"),
        "priority_lsms_isa_minimum_batch_endpoint_refresh_summary": row_count(RESULT_DIR / "priority_lsms_isa_minimum_batch_endpoint_refresh_summary.csv"),
        "priority_analysis_dataset_synthesis_blueprint": row_count(TEMP_DIR / "priority_analysis_dataset_synthesis_blueprint.csv"),
        "priority_analysis_dataset_join_plan": row_count(TEMP_DIR / "priority_analysis_dataset_join_plan.csv"),
        "priority_analysis_dataset_synthesis_blueprint_summary": row_count(RESULT_DIR / "priority_analysis_dataset_synthesis_blueprint_summary.csv"),
        "priority_country_wave_promotion_packet_index": row_count(TEMP_DIR / "priority_country_wave_promotion_packet_index.csv"),
        "priority_country_wave_promotion_packet_gate_matrix": row_count(TEMP_DIR / "priority_country_wave_promotion_packet_gate_matrix.csv"),
        "priority_country_wave_promotion_packet_action_queue": row_count(TEMP_DIR / "priority_country_wave_promotion_packet_action_queue.csv"),
        "priority_country_wave_promotion_packet_summary": row_count(RESULT_DIR / "priority_country_wave_promotion_packet_summary.csv"),
        "priority_lsms_isa_country_wave_promotion_packet_index": row_count(TEMP_DIR / "priority_lsms_isa_country_wave_promotion_packet_index.csv"),
        "priority_lsms_isa_country_wave_promotion_packet_gate_matrix": row_count(TEMP_DIR / "priority_lsms_isa_country_wave_promotion_packet_gate_matrix.csv"),
        "priority_lsms_isa_country_wave_promotion_packet_action_queue": row_count(TEMP_DIR / "priority_lsms_isa_country_wave_promotion_packet_action_queue.csv"),
        "priority_lsms_isa_country_wave_promotion_packet_summary": row_count(RESULT_DIR / "priority_lsms_isa_country_wave_promotion_packet_summary.csv"),
        "mwi2004_promoted_household_climate_dataset_summary": row_count(RESULT_DIR / "mwi2004_promoted_household_climate_dataset_summary.csv"),
        "mwi2004_promoted_household_climate_dataset_dictionary": row_count(RESULT_DIR / "mwi2004_promoted_household_climate_dataset_dictionary.csv"),
        "mwi2004_promoted_household_climate_dataset_validation": row_count(RESULT_DIR / "mwi2004_promoted_household_climate_dataset_validation.csv"),
        "mwi2004_sdg382_discretionary_budget_parameter_audit": row_count(RESULT_DIR / "mwi2004_sdg382_discretionary_budget_parameter_audit.csv"),
        "mwi2004_sdg382_discretionary_budget_parameter_summary": row_count(RESULT_DIR / "mwi2004_sdg382_discretionary_budget_parameter_summary.csv"),
        "mwi2004_sdg382_external_parameter_source_ledger": row_count(RESULT_DIR / "mwi2004_sdg382_external_parameter_source_ledger.csv"),
        "mwi2004_sdg382_external_parameter_candidate_summary": row_count(RESULT_DIR / "mwi2004_sdg382_external_parameter_candidate_summary.csv"),
        "mwi2004_sdg382_candidate_classification_precheck": row_count(RESULT_DIR / "mwi2004_sdg382_candidate_classification_precheck.csv"),
        "mwi2004_sdg382_candidate_classification_precheck_summary": row_count(RESULT_DIR / "mwi2004_sdg382_candidate_classification_precheck_summary.csv"),
        "priority_lsms_isa_next_raw_package_action_queue": row_count(TEMP_DIR / "priority_lsms_isa_next_raw_package_action_queue.csv"),
        "priority_lsms_isa_next_raw_package_core_files": row_count(TEMP_DIR / "priority_lsms_isa_next_raw_package_core_files.csv"),
        "priority_lsms_isa_next_raw_package_action_summary": row_count(RESULT_DIR / "priority_lsms_isa_next_raw_package_action_summary.csv"),
        "priority_lsms_isa_incoming_raw_package_route_plan": row_count(TEMP_DIR / "priority_lsms_isa_incoming_raw_package_route_plan.csv"),
        "priority_lsms_isa_incoming_raw_package_route_candidates": row_count(TEMP_DIR / "priority_lsms_isa_incoming_raw_package_route_candidates.csv"),
        "priority_lsms_isa_incoming_raw_package_router_summary": row_count(RESULT_DIR / "priority_lsms_isa_incoming_raw_package_router_summary.csv"),
        "priority_lsms_isa_threshold_gap_download_panel": row_count(TEMP_DIR / "priority_lsms_isa_threshold_gap_download_panel.csv"),
        "priority_lsms_isa_threshold_gap_country_panel": row_count(RESULT_DIR / "priority_lsms_isa_threshold_gap_country_panel.csv"),
        "priority_lsms_isa_threshold_gap_control_panel_summary": row_count(RESULT_DIR / "priority_lsms_isa_threshold_gap_control_panel_summary.csv"),
        "priority_lsms_isa_manual_download_packet_index": row_count(TEMP_DIR / "priority_lsms_isa_manual_download_packet_index.csv"),
        "priority_lsms_isa_manual_download_packet_core_files": row_count(TEMP_DIR / "priority_lsms_isa_manual_download_packet_core_files.csv"),
        "priority_lsms_isa_manual_download_packet_summary": row_count(RESULT_DIR / "priority_lsms_isa_manual_download_packet_summary.csv"),
        "priority_lsms_isa_manual_download_progress_tracker": row_count(TEMP_DIR / "priority_lsms_isa_manual_download_progress_tracker.csv"),
        "priority_lsms_isa_manual_download_progress_summary": row_count(RESULT_DIR / "priority_lsms_isa_manual_download_progress_summary.csv"),
        "priority_lsms_isa_post_download_validation_run_plan": row_count(TEMP_DIR / "priority_lsms_isa_post_download_validation_run_plan.csv"),
        "priority_lsms_isa_post_download_validation_command_log": row_count(TEMP_DIR / "priority_lsms_isa_post_download_validation_command_log.csv"),
        "priority_lsms_isa_post_download_validation_runner_summary": row_count(RESULT_DIR / "priority_lsms_isa_post_download_validation_runner_summary.csv"),
        "priority_lsms_isa_manual_download_execution_board": row_count(TEMP_DIR / "priority_lsms_isa_manual_download_execution_board.csv"),
        "priority_lsms_isa_manual_download_execution_board_summary": row_count(RESULT_DIR / "priority_lsms_isa_manual_download_execution_board_summary.csv"),
        "priority_lsms_isa_credentialed_download_handoff_plan": row_count(TEMP_DIR / "priority_lsms_isa_credentialed_download_handoff_plan.csv"),
        "priority_lsms_isa_credentialed_download_handoff_log": row_count(TEMP_DIR / "priority_lsms_isa_credentialed_download_handoff_log.csv"),
        "priority_lsms_isa_credentialed_download_handoff_summary": row_count(RESULT_DIR / "priority_lsms_isa_credentialed_download_handoff_summary.csv"),
        "priority_lsms_isa_resource_download_route_probe": row_count(TEMP_DIR / "priority_lsms_isa_resource_download_route_probe.csv"),
        "priority_lsms_isa_resource_download_route_probe_summary": row_count(RESULT_DIR / "priority_lsms_isa_resource_download_route_probe_summary.csv"),
        "priority_lsms_isa_download_acceptance_file_matrix": row_count(TEMP_DIR / "priority_lsms_isa_download_acceptance_file_matrix.csv"),
        "priority_lsms_isa_download_acceptance_requirement_matrix": row_count(TEMP_DIR / "priority_lsms_isa_download_acceptance_requirement_matrix.csv"),
        "priority_lsms_isa_download_acceptance_matrix_summary": row_count(RESULT_DIR / "priority_lsms_isa_download_acceptance_matrix_summary.csv"),
        "priority_lsms_isa_local_target_readme_manifest": row_count(TEMP_DIR / "priority_lsms_isa_local_target_readme_manifest.csv"),
        "priority_lsms_isa_local_target_readme_summary": row_count(RESULT_DIR / "priority_lsms_isa_local_target_readme_summary.csv"),
        "priority_lsms_isa_minimum_batch_raw_value_requirement_queue": row_count(TEMP_DIR / "priority_lsms_isa_minimum_batch_raw_value_requirement_queue.csv"),
        "priority_lsms_isa_minimum_batch_raw_value_variable_queue": row_count(TEMP_DIR / "priority_lsms_isa_minimum_batch_raw_value_variable_queue.csv"),
        "priority_lsms_isa_minimum_batch_raw_value_file_queue": row_count(TEMP_DIR / "priority_lsms_isa_minimum_batch_raw_value_file_queue.csv"),
        "priority_lsms_isa_minimum_batch_raw_value_queue_summary": row_count(RESULT_DIR / "priority_lsms_isa_minimum_batch_raw_value_queue_summary.csv"),
        "priority_lsms_isa_target_folder_receipt_status": row_count(TEMP_DIR / "priority_lsms_isa_target_folder_receipt_status.csv"),
        "priority_lsms_isa_target_folder_receipt_file_inventory": row_count(TEMP_DIR / "priority_lsms_isa_target_folder_receipt_file_inventory.csv"),
        "priority_lsms_isa_target_folder_receipt_smoke_test_summary": row_count(RESULT_DIR / "priority_lsms_isa_target_folder_receipt_smoke_test_summary.csv"),
        "priority_lsms_isa_threshold_replacement_candidate_rank": row_count(TEMP_DIR / "priority_lsms_isa_threshold_replacement_candidate_rank.csv"),
        "priority_lsms_isa_threshold_replacement_scenarios": row_count(TEMP_DIR / "priority_lsms_isa_threshold_replacement_scenarios.csv"),
        "priority_lsms_isa_threshold_replacement_strategy": row_count(TEMP_DIR / "priority_lsms_isa_threshold_replacement_strategy.csv"),
        "priority_lsms_isa_threshold_replacement_plan_summary": row_count(RESULT_DIR / "priority_lsms_isa_threshold_replacement_plan_summary.csv"),
        "priority_lsms_isa_minimum_batch_climate_linkage_review_queue": row_count(TEMP_DIR / "priority_lsms_isa_minimum_batch_climate_linkage_review_queue.csv"),
        "priority_lsms_isa_minimum_batch_climate_linkage_file_queue": row_count(TEMP_DIR / "priority_lsms_isa_minimum_batch_climate_linkage_file_queue.csv"),
        "priority_lsms_isa_minimum_batch_climate_linkage_review_summary": row_count(RESULT_DIR / "priority_lsms_isa_minimum_batch_climate_linkage_review_summary.csv"),
        "priority_lsms_isa_local_stray_raw_package_candidates": row_count(TEMP_DIR / "priority_lsms_isa_local_stray_raw_package_candidates.csv"),
        "priority_lsms_isa_local_stray_raw_package_route_plan": row_count(TEMP_DIR / "priority_lsms_isa_local_stray_raw_package_route_plan.csv"),
        "priority_lsms_isa_local_stray_raw_package_locator_summary": row_count(RESULT_DIR / "priority_lsms_isa_local_stray_raw_package_locator_summary.csv"),
        "priority_lsms_isa_promotion_gate_dashboard": row_count(TEMP_DIR / "priority_lsms_isa_promotion_gate_dashboard.csv"),
        "priority_lsms_isa_promotion_gate_requirement_dashboard": row_count(TEMP_DIR / "priority_lsms_isa_promotion_gate_requirement_dashboard.csv"),
        "priority_lsms_isa_promotion_gate_dashboard_summary": row_count(RESULT_DIR / "priority_lsms_isa_promotion_gate_dashboard_summary.csv"),
        "promoted_data_gate_manifest": row_count(TEMP_DIR / "promoted_data_gate_manifest.csv"),
        "promoted_data_gate_summary": row_count(RESULT_DIR / "promoted_data_gate_summary.csv"),
        "design_scorecard": row_count(RESULT_DIR / "design_scorecard.csv"),
        "design_scorecard_current_audit": row_count(RESULT_DIR / "design_scorecard_current_audit.csv"),
        "design_no_go_threshold_audit": row_count(RESULT_DIR / "design_no_go_threshold_audit.csv"),
        "design_scorecard_current_summary": row_count(RESULT_DIR / "design_scorecard_current_summary.csv"),
        "alb2002_promotion_gate_delta_audit": row_count(TEMP_DIR / "alb2002_promotion_gate_delta_audit.csv"),
        "alb2002_promotion_gate_delta_summary": row_count(RESULT_DIR / "alb2002_promotion_gate_delta_summary.csv"),
        "alb2002_boundary_blocker_resolution_matrix": row_count(TEMP_DIR / "alb2002_boundary_blocker_resolution_matrix.csv"),
        "alb2002_boundary_blocker_resolution_summary": row_count(RESULT_DIR / "alb2002_boundary_blocker_resolution_summary.csv"),
        "alb2002_outcome_blocker_resolution_matrix": row_count(TEMP_DIR / "alb2002_outcome_blocker_resolution_matrix.csv"),
        "alb2002_outcome_blocker_resolution_summary": row_count(RESULT_DIR / "alb2002_outcome_blocker_resolution_summary.csv"),
        "alb2012_timing_geography_blocker_resolution_matrix": row_count(TEMP_DIR / "alb2012_timing_geography_blocker_resolution_matrix.csv"),
        "alb2012_timing_geography_blocker_resolution_summary": row_count(RESULT_DIR / "alb2012_timing_geography_blocker_resolution_summary.csv"),
        "objective_requirement_traceability": row_count(RESULT_DIR / "objective_requirement_traceability.csv"),
        "objective_guardrail_audit": row_count(RESULT_DIR / "objective_guardrail_audit.csv"),
        "objective_traceability_summary": row_count(RESULT_DIR / "objective_traceability_summary.csv"),
        "python_package_inventory": row_count(TEMP_DIR / "python_package_inventory.csv"),
        "python_environment_audit": row_count(RESULT_DIR / "python_environment_audit.csv"),
        "python_environment_summary": row_count(RESULT_DIR / "python_environment_summary.csv"),
        "schema_studies": row_count(TEMP_DIR / "raw_schema_inventory" / "schema_study_inventory.csv"),
        "schema_files": row_count(TEMP_DIR / "raw_schema_inventory" / "schema_file_inventory.csv"),
        "metadata_variables": row_count(TEMP_DIR / "raw_schema_inventory" / "metadata_variable_catalog.csv"),
        "raw_files": row_count(TEMP_DIR / "raw_schema_inventory" / "raw_file_inventory.csv"),
        "raw_variables": row_count(TEMP_DIR / "raw_schema_inventory" / "raw_variable_catalog.csv"),
        "completion_criteria": row_count(RESULT_DIR / "completion_criteria_audit.csv"),
    }
    add(rows, "evidence", "Source inventory has rows", status(counts["source_inventory"] > 0), f"rows={counts['source_inventory']}")
    add(rows, "evidence", "Broad country-wave screening has rows", status(counts["country_wave_screening"] > 0), f"rows={counts['country_wave_screening']}")
    add(rows, "evidence", "Manual raw-data manifest exists for gated sources", status(counts["manual_download_manifest"] > 0), f"rows={counts['manual_download_manifest']}")
    add(rows, "evidence", "Manual file/module checklist exists", status(counts["manual_file_checklist"] > 0), f"rows={counts['manual_file_checklist']}")
    add(rows, "evidence", "Manual access action queue exists", status(counts["manual_access_action_queue"] > 0), f"rows={counts['manual_access_action_queue']}", "" if counts["manual_access_action_queue"] > 0 else "Run script/15_prepare_manual_request_packet.py.")
    add(rows, "evidence", "External repository direct-access probe has run", status(counts["external_repository_probe"] > 0), f"rows={counts['external_repository_probe']}", "" if counts["external_repository_probe"] > 0 else "Run script/02_probe_external_repositories.py to check public external repository links.")
    public_external = read_csv_dicts(TEMP_DIR / "public_external_raw_candidate_downloads.csv")
    public_external_present = sum(1 for row in public_external if row.get("download_status") in {"downloaded", "already_exists"})
    add(
        rows,
        "evidence",
        "Public external candidate raw links are verified and downloaded when directly accessible",
        status(counts["public_external_downloads"] > 0 and counts["public_external_download_summary"] > 0 and public_external_present > 0),
        f"candidate_rows={counts['public_external_downloads']}; summary_rows={counts['public_external_download_summary']}; downloaded_or_existing_rows={public_external_present}",
        ""
        if counts["public_external_downloads"] > 0
        and counts["public_external_download_summary"] > 0
        and public_external_present > 0
        else "Run script/44_download_public_external_raw_candidates.py after the external repository probe.",
    )
    wb_docs = read_csv_dicts(TEMP_DIR / "worldbank_public_documentation_audit.csv")
    wb_saved = sum(1 for row in wb_docs if row.get("status") == "saved")
    wb_gates = sum(1 for row in wb_docs if row.get("resource_type") == "get_microdata_html" and row.get("access_gate_detected") == "1")
    add(
        rows,
        "evidence",
        "Priority World Bank public documentation/access-gate snapshot has run",
        status(counts["worldbank_public_documentation_audit"] > 0 and wb_saved > 0),
        f"rows={counts['worldbank_public_documentation_audit']}; saved_resources={wb_saved}; get_microdata_access_gates={wb_gates}",
        "" if counts["worldbank_public_documentation_audit"] > 0 and wb_saved > 0 else "Run script/16_snapshot_public_documentation.py after manual_download_priority.csv exists.",
    )
    raw_manifest = read_csv_dicts(TEMP_DIR / "raw_download_file_manifest.csv")
    raw_targets = read_csv_dicts(TEMP_DIR / "raw_download_target_audit.csv")
    raw_like_files = sum(1 for row in raw_manifest if row.get("file_role") in {"archive", "raw_tabular_or_spreadsheet"})
    raw_like_targets = sum(1 for row in raw_targets if row.get("status") == "raw_or_archive_files_present")
    add(
        rows,
        "evidence",
        "Raw-download folder checksum/target audit has run",
        status(counts["raw_download_target_audit"] > 0),
        f"manifest_rows={counts['raw_download_file_manifest']}; target_rows={counts['raw_download_target_audit']}; raw_like_files={raw_like_files}; raw_like_targets={raw_like_targets}",
        "" if counts["raw_download_target_audit"] > 0 else "Run script/17_audit_raw_downloads.py after manual access actions are generated.",
    )
    intake_rows = read_csv_dicts(TEMP_DIR / "raw_download_intake_manifest.csv")
    expected_rows = read_csv_dicts(TEMP_DIR / "raw_download_expected_files.csv")
    intake_ready = sum(1 for row in intake_rows if row.get("intake_status") == "ready_for_raw_schema_inspection")
    intake_doc_only = sum(1 for row in intake_rows if row.get("intake_status") == "instructions_or_documentation_only")
    expected_not_present = sum(1 for row in expected_rows if row.get("expected_file_status") == "not_present")
    add(
        rows,
        "evidence",
        "Raw-download intake package maps target folders to expected files",
        status(counts["raw_download_intake_manifest"] > 0 and counts["raw_download_expected_files"] > 0 and counts["raw_download_intake_summary"] > 0),
        f"targets={counts['raw_download_intake_manifest']}; expected_files={counts['raw_download_expected_files']}; summary_rows={counts['raw_download_intake_summary']}; ready_for_schema={intake_ready}; instruction_or_doc_only={intake_doc_only}; expected_not_present={expected_not_present}",
        "" if counts["raw_download_intake_manifest"] > 0 and counts["raw_download_expected_files"] > 0 and counts["raw_download_intake_summary"] > 0 else "Run script/27_build_raw_download_intake_package.py after manual request packet generation.",
    )
    climate_probe = read_csv_dicts(TEMP_DIR / "climate_source_probe.csv")
    climate_probe_ok = sum(1 for row in climate_probe if row.get("status") in {"reachable_snapshot_saved", "pass_api_parameters_present"})
    add(
        rows,
        "evidence",
        "Official climate source endpoint probe has run",
        status(counts["climate_source_probe"] > 0 and climate_probe_ok > 0),
        f"rows={counts['climate_source_probe']}; reachable_or_pass={climate_probe_ok}",
        "" if counts["climate_source_probe"] > 0 and climate_probe_ok > 0 else "Run script/18_probe_climate_sources.py.",
    )
    validation_probe = read_csv_dicts(TEMP_DIR / "validation_reference_source_probe.csv")
    validation_ok = sum(1 for row in validation_probe if row.get("status") in {"reachable_snapshot_saved", "indicator_metadata_available"})
    validation_samples = read_csv_dicts(TEMP_DIR / "validation_reference_indicator_sample.csv")
    validation_sample_rows = sum(1 for row in validation_samples if row.get("status") == "sample_record")
    hefpi_uhc_reference = read_csv_dicts(TEMP_DIR / "hefpi_uhc_reference_sample.csv")
    hefpi_uhc_rows = sum(1 for row in hefpi_uhc_reference if row.get("status") == "hefpi_uhc_reference_record")
    add(
        rows,
        "evidence",
        "Outcome validation/reference source probe has run",
        status(counts["validation_reference_source_probe"] > 0 and validation_ok > 0),
        f"probe_rows={counts['validation_reference_source_probe']}; ok={validation_ok}; sample_records={validation_sample_rows}; hefpi_uhc_reference_records={hefpi_uhc_rows}",
        "" if counts["validation_reference_source_probe"] > 0 and validation_ok > 0 else "Run script/19_probe_validation_reference_sources.py.",
    )
    sample_gate = read_csv_dicts(RESULT_DIR / "sample_selection_gate_audit.csv")
    sample_gate_raw_final = sum(1 for row in sample_gate if row.get("eligible_for_final_sample") == "1")
    sample_gate_metadata_main = sum(1 for row in sample_gate if row.get("metadata_has_main_sample_core") == "1")
    sample_gate_failures = sum(1 for row in read_csv_dicts(RESULT_DIR / "sample_selection_gate_summary.csv") if row.get("status") == "fail")
    add(
        rows,
        "evidence",
        "Pre-specified sample-selection gate has run",
        status(counts["sample_selection_gate_audit"] > 0 and counts["sample_selection_gate_summary"] > 0),
        f"audit_rows={counts['sample_selection_gate_audit']}; summary_rows={counts['sample_selection_gate_summary']}; metadata_main_candidates={sample_gate_metadata_main}; raw_final_candidates={sample_gate_raw_final}; failed_no_go_rules={sample_gate_failures}",
        "" if counts["sample_selection_gate_audit"] > 0 and counts["sample_selection_gate_summary"] > 0 else "Run script/20_sample_selection_gate.py after screening/schema inspection.",
    )
    quality_rows = read_csv_dicts(RESULT_DIR / "metadata_candidate_quality_audit.csv")
    quality_financial = sum(1 for row in quality_rows if row.get("quality_has_main_financial_core") == "1")
    quality_double = sum(1 for row in quality_rows if row.get("quality_has_double_failure_core") == "1")
    false_positive_rows = sum(1 for row in read_csv_dicts(TEMP_DIR / "variable_map_confidence_audit.csv") if row.get("metadata_confidence") == "likely_false_positive")
    add(
        rows,
        "evidence",
        "Metadata variable-confidence audit has run",
        status(counts["variable_map_confidence_audit"] > 0 and counts["metadata_candidate_quality_audit"] > 0 and counts["metadata_candidate_quality_summary"] > 0 and counts["metadata_quality_download_priority"] > 0),
        f"variable_rows={counts['variable_map_confidence_audit']}; country_wave_rows={counts['metadata_candidate_quality_audit']}; priority_rows={counts['metadata_quality_download_priority']}; quality_financial={quality_financial}; quality_double={quality_double}; likely_false_positive_rows={false_positive_rows}",
        "" if counts["variable_map_confidence_audit"] > 0 and counts["metadata_candidate_quality_audit"] > 0 and counts["metadata_candidate_quality_summary"] > 0 and counts["metadata_quality_download_priority"] > 0 else "Run script/21_audit_metadata_variable_quality.py after variable maps and sample-selection gate exist.",
    )
    ingestion_rows = read_csv_dicts(TEMP_DIR / "raw_ingestion_plan.csv")
    ingestion_waiting = sum(1 for row in ingestion_rows if row.get("ingestion_gate_status") == "waiting_for_manual_download")
    ingestion_ready = sum(1 for row in ingestion_rows if row.get("ingestion_gate_status") == "ready_for_raw_schema_inspection")
    verified_concepts = sum(1 for row in read_csv_dicts(TEMP_DIR / "raw_ingestion_concept_checklist.csv") if row.get("raw_verification_status") == "raw_variables_inspected")
    add(
        rows,
        "evidence",
        "Raw-ingestion plan has been built from quality-screened metadata",
        status(counts["raw_ingestion_plan"] > 0 and counts["raw_ingestion_concept_checklist"] > 0 and counts["raw_ingestion_module_checklist"] > 0 and counts["raw_ingestion_plan_summary"] > 0),
        f"plan_rows={counts['raw_ingestion_plan']}; concept_rows={counts['raw_ingestion_concept_checklist']}; module_rows={counts['raw_ingestion_module_checklist']}; waiting={ingestion_waiting}; ready={ingestion_ready}; raw_verified_concepts={verified_concepts}",
        "" if counts["raw_ingestion_plan"] > 0 and counts["raw_ingestion_concept_checklist"] > 0 and counts["raw_ingestion_module_checklist"] > 0 and counts["raw_ingestion_plan_summary"] > 0 else "Run script/22_build_raw_ingestion_plan.py after metadata quality and raw-download audits.",
    )
    protocol_rows = read_csv_dicts(TEMP_DIR / "raw_variable_verification_protocol.csv")
    protocol_raw_pending = sum(1 for row in protocol_rows if row.get("verification_status") == "raw_not_inspected")
    protocol_value_pending = sum(1 for row in protocol_rows if row.get("verification_status") == "raw_variable_seen_value_audit_pending")
    add(
        rows,
        "evidence",
        "Raw-variable verification protocol and harmonization scaffold have been built",
        status(
            counts["raw_variable_verification_protocol"] > 0
            and counts["harmonization_recipe_scaffold"] > 0
            and counts["raw_variable_verification_summary"] > 0
        ),
        f"protocol_rows={counts['raw_variable_verification_protocol']}; scaffold_rows={counts['harmonization_recipe_scaffold']}; summary_rows={counts['raw_variable_verification_summary']}; raw_not_inspected={protocol_raw_pending}; value_audit_pending={protocol_value_pending}",
        ""
        if counts["raw_variable_verification_protocol"] > 0
        and counts["harmonization_recipe_scaffold"] > 0
        and counts["raw_variable_verification_summary"] > 0
        else "Run script/29_build_raw_variable_verification_protocol.py after raw-ingestion planning.",
    )
    recipe_gate = read_csv_dicts(TEMP_DIR / "harmonization_recipe_gate.csv")
    recipe_gate_ready = sum(1 for row in recipe_gate if row.get("recipe_gate_status") == "recipe_candidate_ready")
    recipe_gate_blocked = sum(1 for row in recipe_gate if row.get("recipe_gate_status") != "recipe_candidate_ready")
    readiness_rows = read_csv_dicts(RESULT_DIR / "harmonization_readiness_matrix.csv")
    readiness_ready = sum(1 for row in readiness_rows if row.get("readiness_status") == "ready_for_verified_recipe_assembly")
    add(
        rows,
        "evidence",
        "Harmonization recipe gate blocks scaffold promotion until raw value/unit/recall/key audits pass",
        status(
            counts["harmonization_recipe_gate"] > 0
            and counts["harmonization_value_audit_template"] > 0
            and counts["harmonization_readiness_matrix"] > 0
            and counts["harmonization_recipe_gate_summary"] > 0
        ),
        f"gate_rows={counts['harmonization_recipe_gate']}; value_audit_template_rows={counts['harmonization_value_audit_template']}; verified_candidate_rows={counts['harmonization_verified_candidates']}; readiness_rows={counts['harmonization_readiness_matrix']}; recipe_ready_rows={recipe_gate_ready}; blocked_rows={recipe_gate_blocked}; ready_country_waves={readiness_ready}",
        ""
        if counts["harmonization_recipe_gate"] > 0
        and counts["harmonization_value_audit_template"] > 0
        and counts["harmonization_readiness_matrix"] > 0
        and counts["harmonization_recipe_gate_summary"] > 0
        else "Run script/33_build_harmonization_recipe_gate.py after raw-variable verification protocol generation.",
    )
    analysis_promotion_summary = read_csv_dicts(RESULT_DIR / "analysis_dataset_promotion_barrier_summary.csv")
    analysis_promotion_rows = next((row.get("value", "0") for row in analysis_promotion_summary if row.get("metric") == "analysis_dataset_promotion_audit_rows"), "0")
    analysis_promotion_blocked = next((row.get("value", "0") for row in analysis_promotion_summary if row.get("metric") == "analysis_dataset_promotion_blocked_rows"), "0")
    analysis_promotion_promoted = next((row.get("value", "0") for row in analysis_promotion_summary if row.get("metric") == "analysis_dataset_promotion_promoted_rows"), "0")
    analysis_promotion_data_files = next((row.get("value", "0") for row in analysis_promotion_summary if row.get("metric") == "analysis_dataset_promotion_data_file_count"), "0")
    analysis_promotion_verified_candidates = next((row.get("value", "0") for row in analysis_promotion_summary if row.get("metric") == "analysis_dataset_promotion_verified_recipe_candidates"), "0")
    analysis_promotion_ready_waves = next((row.get("value", "0") for row in analysis_promotion_summary if row.get("metric") == "analysis_dataset_promotion_ready_country_waves"), "0")
    analysis_promotion_alb2002_temp = next((row.get("value", "0") for row in analysis_promotion_summary if row.get("metric") == "analysis_dataset_promotion_alb2002_temp_core_rows"), "0")
    analysis_promotion_alb2002_weight_positive = next((row.get("value", "0") for row in analysis_promotion_summary if row.get("metric") == "analysis_dataset_promotion_alb2002_weight_positive_rows"), "0")
    analysis_promotion_alb2002_weight_key_match = next((row.get("value", "0") for row in analysis_promotion_summary if row.get("metric") == "analysis_dataset_promotion_alb2002_weight_key_match_rows"), "0")
    analysis_promotion_alb2002_weighted_inference_ready = next((row.get("value", "0") for row in analysis_promotion_summary if row.get("metric") == "analysis_dataset_promotion_alb2002_weighted_inference_ready_rows"), "0")
    analysis_promotion_alb2002_harmonized = next((row.get("value", "0") for row in analysis_promotion_summary if row.get("metric") == "analysis_dataset_promotion_alb2002_harmonized_ready_rows"), "0")
    analysis_promotion_alb2002_outcome = next((row.get("value", "0") for row in analysis_promotion_summary if row.get("metric") == "analysis_dataset_promotion_alb2002_outcome_ready_rows"), "0")
    analysis_promotion_alb2002_climate = next((row.get("value", "0") for row in analysis_promotion_summary if row.get("metric") == "analysis_dataset_promotion_alb2002_climate_linkage_ready_rows"), "0")
    analysis_promotion_limited_core_rows = next((row.get("value", "0") for row in analysis_promotion_summary if row.get("metric") == "analysis_dataset_promotion_limited_harmonized_core_rows"), "0")
    analysis_promotion_limited_core_data_write_ready = next((row.get("value", "0") for row in analysis_promotion_summary if row.get("metric") == "analysis_dataset_promotion_limited_harmonized_core_data_write_ready_rows"), "0")
    analysis_promotion_limited_core_final_outcome_ready = next((row.get("value", "0") for row in analysis_promotion_summary if row.get("metric") == "analysis_dataset_promotion_limited_harmonized_core_final_outcome_ready_rows"), "0")
    analysis_promotion_limited_core_climate_ready = next((row.get("value", "0") for row in analysis_promotion_summary if row.get("metric") == "analysis_dataset_promotion_limited_harmonized_core_climate_linkage_ready_rows"), "0")
    analysis_promotion_limited_core_analysis_ready = next((row.get("value", "0") for row in analysis_promotion_summary if row.get("metric") == "analysis_dataset_promotion_limited_harmonized_core_analysis_ready_rows"), "0")
    analysis_promotion_limited_financial_rows = next((row.get("value", "0") for row in analysis_promotion_summary if row.get("metric") == "analysis_dataset_promotion_limited_financial_outcome_rows"), "0")
    analysis_promotion_limited_financial_data_write_ready = next((row.get("value", "0") for row in analysis_promotion_summary if row.get("metric") == "analysis_dataset_promotion_limited_financial_outcome_data_write_ready_rows"), "0")
    analysis_promotion_limited_financial_sdg_ready = next((row.get("value", "0") for row in analysis_promotion_summary if row.get("metric") == "analysis_dataset_promotion_limited_financial_outcome_sdg382_ready_rows"), "0")
    analysis_promotion_limited_financial_access_ready = next((row.get("value", "0") for row in analysis_promotion_summary if row.get("metric") == "analysis_dataset_promotion_limited_financial_outcome_access_ready_rows"), "0")
    analysis_promotion_limited_financial_composite_ready = next((row.get("value", "0") for row in analysis_promotion_summary if row.get("metric") == "analysis_dataset_promotion_limited_financial_outcome_composite_ready_rows"), "0")
    analysis_promotion_limited_financial_climate_ready = next((row.get("value", "0") for row in analysis_promotion_summary if row.get("metric") == "analysis_dataset_promotion_limited_financial_outcome_climate_linkage_ready_rows"), "0")
    analysis_promotion_limited_financial_analysis_ready = next((row.get("value", "0") for row in analysis_promotion_summary if row.get("metric") == "analysis_dataset_promotion_limited_financial_outcome_analysis_ready_rows"), "0")
    analysis_promotion_limited_climate_rows = next((row.get("value", "0") for row in analysis_promotion_summary if row.get("metric") == "analysis_dataset_promotion_limited_climate_exposure_rows"), "0")
    analysis_promotion_limited_climate_data_write_ready = next((row.get("value", "0") for row in analysis_promotion_summary if row.get("metric") == "analysis_dataset_promotion_limited_climate_exposure_data_write_ready_rows"), "0")
    analysis_promotion_limited_climate_linkage_ready = next((row.get("value", "0") for row in analysis_promotion_summary if row.get("metric") == "analysis_dataset_promotion_limited_climate_exposure_climate_linkage_ready_rows"), "0")
    analysis_promotion_limited_climate_analysis_ready = next((row.get("value", "0") for row in analysis_promotion_summary if row.get("metric") == "analysis_dataset_promotion_limited_climate_exposure_analysis_ready_rows"), "0")
    analysis_promotion_limited_linked_rows = next((row.get("value", "0") for row in analysis_promotion_summary if row.get("metric") == "analysis_dataset_promotion_limited_climate_linked_rows"), "0")
    analysis_promotion_limited_linked_data_write_ready = next((row.get("value", "0") for row in analysis_promotion_summary if row.get("metric") == "analysis_dataset_promotion_limited_climate_linked_data_write_ready_rows"), "0")
    analysis_promotion_limited_linked_descriptive_ready = next((row.get("value", "0") for row in analysis_promotion_summary if row.get("metric") == "analysis_dataset_promotion_limited_climate_linked_descriptive_ready_rows"), "0")
    analysis_promotion_limited_linked_predictive_ready = next((row.get("value", "0") for row in analysis_promotion_summary if row.get("metric") == "analysis_dataset_promotion_limited_climate_linked_predictive_ml_ready_rows"), "0")
    analysis_promotion_limited_linked_reduced_ready = next((row.get("value", "0") for row in analysis_promotion_summary if row.get("metric") == "analysis_dataset_promotion_limited_climate_linked_reduced_form_ready_rows"), "0")
    analysis_promotion_limited_linked_robustness_ready = next((row.get("value", "0") for row in analysis_promotion_summary if row.get("metric") == "analysis_dataset_promotion_limited_climate_linked_robustness_ready_rows"), "0")
    analysis_promotion_limited_linked_analysis_ready = next((row.get("value", "0") for row in analysis_promotion_summary if row.get("metric") == "analysis_dataset_promotion_limited_climate_linked_analysis_ready_rows"), "0")
    analysis_promotion_decision = next((row.get("value", "") for row in analysis_promotion_summary if row.get("metric") == "analysis_dataset_promotion_current_decision"), "")
    add(
        rows,
        "evidence",
        "Analysis dataset promotion barrier audit permits only the limited ALB_2002 core, CHE outcomes, and climate exposure while linkage and model gates remain blocked",
        status(
            counts["analysis_dataset_promotion_barrier_audit"] == 6
            and counts["analysis_dataset_promotion_barrier_summary"] > 0
            and file_ok(REPORT_DIR / "analysis_dataset_promotion_barriers.md")
            and file_ok(REPORT_DIR / "alb2002_harmonized_household_core_promotion.md")
            and file_ok(REPORT_DIR / "alb2002_limited_financial_outcome_promotion.md")
            and file_ok(REPORT_DIR / "alb2002_limited_climate_exposure_promotion.md")
            and file_ok(REPORT_DIR / "alb2002_limited_climate_linked_promotion.md")
            and counts["alb2002_harmonized_core_promotion_audit"] == 8
            and counts["alb2002_harmonized_core_promotion_summary"] > 0
            and counts["alb2002_limited_financial_outcome_promotion_audit"] == 5
            and counts["alb2002_limited_financial_outcome_promotion_summary"] > 0
            and counts["alb2002_limited_climate_exposure_promotion_audit"] == 6
            and counts["alb2002_limited_climate_exposure_promotion_summary"] > 0
            and counts["alb2002_limited_climate_linked_promotion_audit"] == 5
            and counts["alb2002_limited_climate_linked_promotion_summary"] > 0
            and analysis_promotion_rows == "6"
            and analysis_promotion_blocked == "2"
            and analysis_promotion_promoted == "4"
            and analysis_promotion_data_files == "4"
            and analysis_promotion_verified_candidates == "0"
            and analysis_promotion_ready_waves == "0"
            and analysis_promotion_alb2002_temp == "3599"
            and analysis_promotion_alb2002_weight_positive == "3599"
            and analysis_promotion_alb2002_weight_key_match == "3599"
            and analysis_promotion_alb2002_weighted_inference_ready == "0"
            and analysis_promotion_alb2002_harmonized == "0"
            and analysis_promotion_alb2002_outcome == "0"
            and analysis_promotion_alb2002_climate == "0"
            and analysis_promotion_limited_core_rows == "3599"
            and analysis_promotion_limited_core_data_write_ready == "3599"
            and analysis_promotion_limited_core_final_outcome_ready == "0"
            and analysis_promotion_limited_core_climate_ready == "0"
            and analysis_promotion_limited_core_analysis_ready == "0"
            and analysis_promotion_limited_financial_rows == "3599"
            and analysis_promotion_limited_financial_data_write_ready == "3599"
            and analysis_promotion_limited_financial_sdg_ready == "0"
            and analysis_promotion_limited_financial_access_ready == "0"
            and analysis_promotion_limited_financial_composite_ready == "0"
            and analysis_promotion_limited_financial_climate_ready == "0"
            and analysis_promotion_limited_financial_analysis_ready == "0"
            and analysis_promotion_limited_climate_rows == "384"
            and analysis_promotion_limited_climate_data_write_ready == "384"
            and analysis_promotion_limited_climate_linkage_ready == "0"
            and analysis_promotion_limited_climate_analysis_ready == "0"
            and analysis_promotion_limited_linked_rows == "14396"
            and analysis_promotion_limited_linked_data_write_ready == "14396"
            and analysis_promotion_limited_linked_descriptive_ready == "0"
            and analysis_promotion_limited_linked_predictive_ready == "0"
            and analysis_promotion_limited_linked_reduced_ready == "0"
            and analysis_promotion_limited_linked_robustness_ready == "0"
            and analysis_promotion_limited_linked_analysis_ready == "0"
            and analysis_promotion_decision == "limited_core_financial_outcomes_climate_exposures_and_linked_diagnostics_promoted_models_still_blocked"
        ),
        f"audit_rows={counts['analysis_dataset_promotion_barrier_audit']}; summary_rows={counts['analysis_dataset_promotion_barrier_summary']}; limited_core_audit_rows={counts['alb2002_harmonized_core_promotion_audit']}; limited_outcome_audit_rows={counts['alb2002_limited_financial_outcome_promotion_audit']}; limited_climate_audit_rows={counts['alb2002_limited_climate_exposure_promotion_audit']}; limited_linked_audit_rows={counts['alb2002_limited_climate_linked_promotion_audit']}; blocked={analysis_promotion_blocked}; promoted={analysis_promotion_promoted}; data_files={analysis_promotion_data_files}; verified_recipe_candidates={analysis_promotion_verified_candidates}; ready_country_waves={analysis_promotion_ready_waves}; alb2002_temp_core_rows={analysis_promotion_alb2002_temp}; alb2002_weight_positive={analysis_promotion_alb2002_weight_positive}; alb2002_weight_key_match={analysis_promotion_alb2002_weight_key_match}; alb2002_weighted_inference_ready={analysis_promotion_alb2002_weighted_inference_ready}; alb2002_harmonized_ready={analysis_promotion_alb2002_harmonized}; alb2002_outcome_ready={analysis_promotion_alb2002_outcome}; alb2002_climate_ready={analysis_promotion_alb2002_climate}; limited_core_rows={analysis_promotion_limited_core_rows}; limited_core_data_write_ready={analysis_promotion_limited_core_data_write_ready}; limited_core_final_outcome_ready={analysis_promotion_limited_core_final_outcome_ready}; limited_core_climate_ready={analysis_promotion_limited_core_climate_ready}; limited_financial_rows={analysis_promotion_limited_financial_rows}; limited_financial_data_write_ready={analysis_promotion_limited_financial_data_write_ready}; limited_financial_sdg_ready={analysis_promotion_limited_financial_sdg_ready}; limited_financial_access_ready={analysis_promotion_limited_financial_access_ready}; limited_financial_composite_ready={analysis_promotion_limited_financial_composite_ready}; limited_financial_climate_ready={analysis_promotion_limited_financial_climate_ready}; limited_climate_rows={analysis_promotion_limited_climate_rows}; limited_climate_data_write_ready={analysis_promotion_limited_climate_data_write_ready}; limited_climate_linkage_ready={analysis_promotion_limited_climate_linkage_ready}; limited_linked_rows={analysis_promotion_limited_linked_rows}; limited_linked_data_write_ready={analysis_promotion_limited_linked_data_write_ready}; limited_linked_descriptive_ready={analysis_promotion_limited_linked_descriptive_ready}; limited_linked_predictive_ready={analysis_promotion_limited_linked_predictive_ready}; limited_linked_reduced_ready={analysis_promotion_limited_linked_reduced_ready}; decision={analysis_promotion_decision}",
        ""
        if counts["analysis_dataset_promotion_barrier_audit"] == 6
        and counts["analysis_dataset_promotion_barrier_summary"] > 0
        and analysis_promotion_promoted == "4"
        and analysis_promotion_data_files == "4"
        and analysis_promotion_decision == "limited_core_financial_outcomes_climate_exposures_and_linked_diagnostics_promoted_models_still_blocked"
        else "Run script/98_audit_analysis_dataset_promotion_barriers.py after the harmonization and Albania promotion gates.",
    )
    design_scorecard_summary = read_csv_dicts(RESULT_DIR / "design_scorecard_current_summary.csv")
    design_scorecard_rows = next((row.get("value", "0") for row in design_scorecard_summary if row.get("metric") == "design_scorecard_rows"), "0")
    design_scorecard_current_rows = next((row.get("value", "0") for row in design_scorecard_summary if row.get("metric") == "design_scorecard_current_rows"), "0")
    design_scorecard_audit_rows = next((row.get("value", "0") for row in design_scorecard_summary if row.get("metric") == "design_scorecard_audit_rows"), "0")
    design_no_go_threshold_rows = next((row.get("value", "0") for row in design_scorecard_summary if row.get("metric") == "design_no_go_threshold_rows"), "0")
    design_no_go_failed_rows = next((row.get("value", "0") for row in design_scorecard_summary if row.get("metric") == "design_no_go_failed_or_not_estimable_rows"), "0")
    design_scorecard_data_write_rows = next((row.get("value", "0") for row in design_scorecard_summary if row.get("metric") == "design_scorecard_data_write_ready_rows"), "0")
    design_scorecard_decision = next((row.get("value", "") for row in design_scorecard_summary if row.get("metric") == "design_scorecard_current_decision"), "")
    add(
        rows,
        "evidence",
        "Current design scorecard refresh appends fail-closed current-state rows and keeps estimation/policy learning no-go",
        status(
            counts["design_scorecard"] == 38
            and counts["design_scorecard_current_audit"] == 4
            and counts["design_no_go_threshold_audit"] == 8
            and counts["design_scorecard_current_summary"] == 7
            and file_ok(REPORT_DIR / "design_scorecard_audit.md")
            and design_scorecard_rows == "38"
            and design_scorecard_current_rows == "3"
            and design_scorecard_audit_rows == "4"
            and design_no_go_threshold_rows == "8"
            and design_no_go_failed_rows == "8"
            and design_scorecard_data_write_rows == "0"
            and design_scorecard_decision == "fail_closed_design_scorecard_currently_no_go_for_estimation_or_policy_learning"
        ),
        f"scorecard_rows={counts['design_scorecard']}; current_audit_rows={counts['design_scorecard_current_audit']}; no_go_threshold_rows={counts['design_no_go_threshold_audit']}; summary_rows={counts['design_scorecard_current_summary']}; summary_scorecard_rows={design_scorecard_rows}; current_rows={design_scorecard_current_rows}; audit_rows={design_scorecard_audit_rows}; failed_or_not_estimable={design_no_go_failed_rows}; data_write_ready={design_scorecard_data_write_rows}; decision={design_scorecard_decision}",
        ""
        if counts["design_scorecard"] == 38
        and counts["design_scorecard_current_audit"] == 4
        and counts["design_no_go_threshold_audit"] == 8
        and counts["design_scorecard_current_summary"] == 7
        and design_scorecard_data_write_rows == "0"
        and design_scorecard_decision == "fail_closed_design_scorecard_currently_no_go_for_estimation_or_policy_learning"
        else "Run script/110_build_current_design_scorecard.py after ALB_2002 linked-candidate diagnostics and promotion-barrier audits.",
    )
    alb2002_gate_delta_summary = read_csv_dicts(RESULT_DIR / "alb2002_promotion_gate_delta_summary.csv")
    alb2002_gate_delta_rows = next((row.get("value", "0") for row in alb2002_gate_delta_summary if row.get("metric") == "alb2002_promotion_gate_delta_rows"), "0")
    alb2002_gate_delta_review_ready = next((row.get("value", "0") for row in alb2002_gate_delta_summary if row.get("metric") == "alb2002_promotion_gate_delta_review_ready_rows"), "0")
    alb2002_gate_delta_candidate = next((row.get("value", "0") for row in alb2002_gate_delta_summary if row.get("metric") == "alb2002_promotion_gate_delta_documented_candidate_rows"), "0")
    alb2002_gate_delta_hard_blocked = next((row.get("value", "0") for row in alb2002_gate_delta_summary if row.get("metric") == "alb2002_promotion_gate_delta_hard_blocked_rows"), "0")
    alb2002_gate_delta_promotion_ready = next((row.get("value", "0") for row in alb2002_gate_delta_summary if row.get("metric") == "alb2002_promotion_gate_delta_promotion_ready_rows"), "0")
    alb2002_gate_delta_data_write = next((row.get("value", "0") for row in alb2002_gate_delta_summary if row.get("metric") == "alb2002_promotion_gate_delta_data_write_ready_rows"), "0")
    alb2002_gate_delta_decision = next((row.get("value", "") for row in alb2002_gate_delta_summary if row.get("metric") == "alb2002_promotion_gate_delta_decision"), "")
    add(
        rows,
        "evidence",
        "ALB_2002 promotion-gate delta audit separates review-ready evidence from hard blockers while keeping data writes closed",
        status(
            counts["alb2002_promotion_gate_delta_audit"] == 10
            and counts["alb2002_promotion_gate_delta_summary"] == 7
            and file_ok(REPORT_DIR / "alb2002_promotion_gate_delta_audit.md")
            and alb2002_gate_delta_rows == "10"
            and alb2002_gate_delta_review_ready == "2"
            and alb2002_gate_delta_candidate == "6"
            and alb2002_gate_delta_hard_blocked == "4"
            and alb2002_gate_delta_promotion_ready == "0"
            and alb2002_gate_delta_data_write == "0"
            and alb2002_gate_delta_decision == "partial_gate_delta_documented_keep_data_empty_until_outcome_sdg_geography_gates_pass"
        ),
        f"audit_rows={counts['alb2002_promotion_gate_delta_audit']}; summary_rows={counts['alb2002_promotion_gate_delta_summary']}; review_ready={alb2002_gate_delta_review_ready}; documented_candidate={alb2002_gate_delta_candidate}; hard_blocked={alb2002_gate_delta_hard_blocked}; promotion_ready={alb2002_gate_delta_promotion_ready}; data_write_ready={alb2002_gate_delta_data_write}; decision={alb2002_gate_delta_decision}",
        ""
        if counts["alb2002_promotion_gate_delta_audit"] == 10
        and counts["alb2002_promotion_gate_delta_summary"] == 7
        and alb2002_gate_delta_data_write == "0"
        and alb2002_gate_delta_decision == "partial_gate_delta_documented_keep_data_empty_until_outcome_sdg_geography_gates_pass"
        else "Run script/111_audit_alb2002_promotion_gate_delta.py after ALB_2002 minimum-recipe, outcome, SDG, and climate-geography audits.",
    )
    alb2002_boundary_blocker_summary = read_csv_dicts(RESULT_DIR / "alb2002_boundary_blocker_resolution_summary.csv")
    alb2002_boundary_blocker_rows = next((row.get("value", "0") for row in alb2002_boundary_blocker_summary if row.get("metric") == "alb2002_boundary_blocker_resolution_rows"), "0")
    alb2002_boundary_blocker_official = next((row.get("value", "0") for row in alb2002_boundary_blocker_summary if row.get("metric") == "alb2002_boundary_blocker_official_or_primary_lead_rows"), "0")
    alb2002_boundary_blocker_candidates = next((row.get("value", "0") for row in alb2002_boundary_blocker_summary if row.get("metric") == "alb2002_boundary_blocker_candidate_name_coverage_rows"), "0")
    alb2002_boundary_blocker_incompatible = next((row.get("value", "0") for row in alb2002_boundary_blocker_summary if row.get("metric") == "alb2002_boundary_blocker_incompatible_or_negative_rows"), "0")
    alb2002_boundary_blocker_historical_ready = next((row.get("value", "0") for row in alb2002_boundary_blocker_summary if row.get("metric") == "alb2002_boundary_blocker_historical_2002_ready_rows"), "0")
    alb2002_boundary_blocker_climate_ready = next((row.get("value", "0") for row in alb2002_boundary_blocker_summary if row.get("metric") == "alb2002_boundary_blocker_climate_linkage_ready_rows"), "0")
    alb2002_boundary_blocker_data_write = next((row.get("value", "0") for row in alb2002_boundary_blocker_summary if row.get("metric") == "alb2002_boundary_blocker_data_write_ready_rows"), "0")
    alb2002_boundary_blocker_hard = next((row.get("value", "0") for row in alb2002_boundary_blocker_summary if row.get("metric") == "alb2002_boundary_blocker_hard_blocked_rows"), "0")
    alb2002_boundary_blocker_action = next((row.get("value", "0") for row in alb2002_boundary_blocker_summary if row.get("metric") == "alb2002_boundary_blocker_required_source_action_rows"), "0")
    alb2002_boundary_blocker_decision = next((row.get("value", "") for row in alb2002_boundary_blocker_summary if row.get("metric") == "alb2002_boundary_blocker_current_decision"), "")
    add(
        rows,
        "evidence",
        "ALB_2002 boundary-source blocker matrix consolidates official, public, current-boundary, and negative evidence while keeping climate linkage closed",
        status(
            counts["alb2002_boundary_blocker_resolution_matrix"] == 11
            and counts["alb2002_boundary_blocker_resolution_summary"] == 10
            and file_ok(REPORT_DIR / "alb2002_boundary_blocker_resolution_matrix.md")
            and alb2002_boundary_blocker_rows == "11"
            and alb2002_boundary_blocker_official == "4"
            and alb2002_boundary_blocker_candidates == "3"
            and alb2002_boundary_blocker_incompatible == "4"
            and alb2002_boundary_blocker_historical_ready == "0"
            and alb2002_boundary_blocker_climate_ready == "0"
            and alb2002_boundary_blocker_data_write == "0"
            and alb2002_boundary_blocker_hard == "11"
            and alb2002_boundary_blocker_action == "7"
            and alb2002_boundary_blocker_decision == "blocked_no_alb2002_boundary_source_ready_for_climate_linkage"
        ),
        f"matrix_rows={counts['alb2002_boundary_blocker_resolution_matrix']}; summary_rows={counts['alb2002_boundary_blocker_resolution_summary']}; official_leads={alb2002_boundary_blocker_official}; candidate_name_coverage={alb2002_boundary_blocker_candidates}; incompatible_or_negative={alb2002_boundary_blocker_incompatible}; historical_ready={alb2002_boundary_blocker_historical_ready}; climate_ready={alb2002_boundary_blocker_climate_ready}; data_write_ready={alb2002_boundary_blocker_data_write}; hard_blocked={alb2002_boundary_blocker_hard}; source_actions={alb2002_boundary_blocker_action}; decision={alb2002_boundary_blocker_decision}",
        ""
        if counts["alb2002_boundary_blocker_resolution_matrix"] == 11
        and counts["alb2002_boundary_blocker_resolution_summary"] == 10
        and alb2002_boundary_blocker_climate_ready == "0"
        and alb2002_boundary_blocker_data_write == "0"
        and alb2002_boundary_blocker_decision == "blocked_no_alb2002_boundary_source_ready_for_climate_linkage"
        else "Run script/112_build_alb2002_boundary_blocker_resolution_matrix.py after ALB_2002 boundary source, GADM, manual follow-up, and local geography audits.",
    )
    alb2002_outcome_blocker_summary = read_csv_dicts(RESULT_DIR / "alb2002_outcome_blocker_resolution_summary.csv")
    alb2002_outcome_blocker_rows = next((row.get("value", "0") for row in alb2002_outcome_blocker_summary if row.get("metric") == "alb2002_outcome_blocker_resolution_rows"), "0")
    alb2002_outcome_blocker_financial = next((row.get("value", "0") for row in alb2002_outcome_blocker_summary if row.get("metric") == "alb2002_outcome_blocker_financial_rows"), "0")
    alb2002_outcome_blocker_access = next((row.get("value", "0") for row in alb2002_outcome_blocker_summary if row.get("metric") == "alb2002_outcome_blocker_access_rows"), "0")
    alb2002_outcome_blocker_composite = next((row.get("value", "0") for row in alb2002_outcome_blocker_summary if row.get("metric") == "alb2002_outcome_blocker_composite_rows"), "0")
    alb2002_outcome_blocker_candidate = next((row.get("value", "0") for row in alb2002_outcome_blocker_summary if row.get("metric") == "alb2002_outcome_blocker_candidate_not_promoted_rows"), "0")
    alb2002_outcome_blocker_low_event = next((row.get("value", "0") for row in alb2002_outcome_blocker_summary if row.get("metric") == "alb2002_outcome_blocker_low_event_candidate_rows"), "0")
    alb2002_outcome_blocker_hard = next((row.get("value", "0") for row in alb2002_outcome_blocker_summary if row.get("metric") == "alb2002_outcome_blocker_hard_blocked_rows"), "0")
    alb2002_outcome_blocker_outcome_ready = next((row.get("value", "0") for row in alb2002_outcome_blocker_summary if row.get("metric") == "alb2002_outcome_blocker_outcome_ready_rows"), "0")
    alb2002_outcome_blocker_sdg_ready = next((row.get("value", "0") for row in alb2002_outcome_blocker_summary if row.get("metric") == "alb2002_outcome_blocker_sdg382_ready_rows"), "0")
    alb2002_outcome_blocker_climate_ready = next((row.get("value", "0") for row in alb2002_outcome_blocker_summary if row.get("metric") == "alb2002_outcome_blocker_climate_linkage_ready_rows"), "0")
    alb2002_outcome_blocker_data_write = next((row.get("value", "0") for row in alb2002_outcome_blocker_summary if row.get("metric") == "alb2002_outcome_blocker_data_write_ready_rows"), "0")
    alb2002_outcome_blocker_decision = next((row.get("value", "") for row in alb2002_outcome_blocker_summary if row.get("metric") == "alb2002_outcome_blocker_current_decision"), "")
    add(
        rows,
        "evidence",
        "ALB_2002 outcome blocker matrix consolidates CHE, access, composite, and SDG outcome evidence while keeping final outcome promotion closed",
        status(
            counts["alb2002_outcome_blocker_resolution_matrix"] == 12
            and counts["alb2002_outcome_blocker_resolution_summary"] == 12
            and file_ok(REPORT_DIR / "alb2002_outcome_blocker_resolution_matrix.md")
            and alb2002_outcome_blocker_rows == "12"
            and alb2002_outcome_blocker_financial == "4"
            and alb2002_outcome_blocker_access == "5"
            and alb2002_outcome_blocker_composite == "3"
            and alb2002_outcome_blocker_candidate == "11"
            and alb2002_outcome_blocker_low_event == "1"
            and alb2002_outcome_blocker_hard == "1"
            and alb2002_outcome_blocker_outcome_ready == "0"
            and alb2002_outcome_blocker_sdg_ready == "0"
            and alb2002_outcome_blocker_climate_ready == "0"
            and alb2002_outcome_blocker_data_write == "0"
            and alb2002_outcome_blocker_decision == "blocked_no_alb2002_outcome_ready_for_promotion"
        ),
        f"matrix_rows={counts['alb2002_outcome_blocker_resolution_matrix']}; summary_rows={counts['alb2002_outcome_blocker_resolution_summary']}; financial={alb2002_outcome_blocker_financial}; access={alb2002_outcome_blocker_access}; composite={alb2002_outcome_blocker_composite}; candidate_not_promoted={alb2002_outcome_blocker_candidate}; low_event={alb2002_outcome_blocker_low_event}; hard_blocked={alb2002_outcome_blocker_hard}; outcome_ready={alb2002_outcome_blocker_outcome_ready}; sdg382_ready={alb2002_outcome_blocker_sdg_ready}; climate_ready={alb2002_outcome_blocker_climate_ready}; data_write_ready={alb2002_outcome_blocker_data_write}; decision={alb2002_outcome_blocker_decision}",
        ""
        if counts["alb2002_outcome_blocker_resolution_matrix"] == 12
        and counts["alb2002_outcome_blocker_resolution_summary"] == 12
        and alb2002_outcome_blocker_outcome_ready == "0"
        and alb2002_outcome_blocker_data_write == "0"
        and alb2002_outcome_blocker_decision == "blocked_no_alb2002_outcome_ready_for_promotion"
        else "Run script/113_build_alb2002_outcome_blocker_resolution_matrix.py after ALB_2002 CHE, access, composite, SDG denominator, and climate-geography audits.",
    )
    alb2012_blocker_summary = read_csv_dicts(RESULT_DIR / "alb2012_timing_geography_blocker_resolution_summary.csv")
    alb2012_blocker_rows = next((row.get("value", "0") for row in alb2012_blocker_summary if row.get("metric") == "alb2012_timing_geography_blocker_resolution_rows"), "0")
    alb2012_blocker_timing = next((row.get("value", "0") for row in alb2012_blocker_summary if row.get("metric") == "alb2012_timing_geography_blocker_timing_rows"), "0")
    alb2012_blocker_geography = next((row.get("value", "0") for row in alb2012_blocker_summary if row.get("metric") == "alb2012_timing_geography_blocker_geography_rows"), "0")
    alb2012_blocker_outcome = next((row.get("value", "0") for row in alb2012_blocker_summary if row.get("metric") == "alb2012_timing_geography_blocker_outcome_rows"), "0")
    alb2012_blocker_promotion = next((row.get("value", "0") for row in alb2012_blocker_summary if row.get("metric") == "alb2012_timing_geography_blocker_promotion_gate_rows"), "0")
    alb2012_blocker_hard = next((row.get("value", "0") for row in alb2012_blocker_summary if row.get("metric") == "alb2012_timing_geography_blocker_hard_blocked_rows"), "0")
    alb2012_blocker_timing_ready = next((row.get("value", "0") for row in alb2012_blocker_summary if row.get("metric") == "alb2012_timing_geography_blocker_interview_timing_ready_rows"), "0")
    alb2012_blocker_geography_ready = next((row.get("value", "0") for row in alb2012_blocker_summary if row.get("metric") == "alb2012_timing_geography_blocker_geography_ready_rows"), "0")
    alb2012_blocker_outcome_ready = next((row.get("value", "0") for row in alb2012_blocker_summary if row.get("metric") == "alb2012_timing_geography_blocker_outcome_ready_rows"), "0")
    alb2012_blocker_climate_ready = next((row.get("value", "0") for row in alb2012_blocker_summary if row.get("metric") == "alb2012_timing_geography_blocker_climate_linkage_ready_rows"), "0")
    alb2012_blocker_data_write = next((row.get("value", "0") for row in alb2012_blocker_summary if row.get("metric") == "alb2012_timing_geography_blocker_data_write_ready_rows"), "0")
    alb2012_blocker_decision = next((row.get("value", "") for row in alb2012_blocker_summary if row.get("metric") == "alb2012_timing_geography_blocker_current_decision"), "")
    add(
        rows,
        "evidence",
        "ALB_2012 fallback blocker matrix consolidates timing, geography, outcome, and first-analysis evidence while keeping promotion closed",
        status(
            counts["alb2012_timing_geography_blocker_resolution_matrix"] == 10
            and counts["alb2012_timing_geography_blocker_resolution_summary"] == 12
            and file_ok(REPORT_DIR / "alb2012_timing_geography_blocker_resolution_matrix.md")
            and alb2012_blocker_rows == "10"
            and alb2012_blocker_timing == "3"
            and alb2012_blocker_geography == "3"
            and alb2012_blocker_outcome == "2"
            and alb2012_blocker_promotion == "2"
            and alb2012_blocker_hard == "10"
            and alb2012_blocker_timing_ready == "0"
            and alb2012_blocker_geography_ready == "0"
            and alb2012_blocker_outcome_ready == "0"
            and alb2012_blocker_climate_ready == "0"
            and alb2012_blocker_data_write == "0"
            and alb2012_blocker_decision == "blocked_alb2012_no_timing_geography_fallback_ready"
        ),
        f"matrix_rows={counts['alb2012_timing_geography_blocker_resolution_matrix']}; summary_rows={counts['alb2012_timing_geography_blocker_resolution_summary']}; timing={alb2012_blocker_timing}; geography={alb2012_blocker_geography}; outcome={alb2012_blocker_outcome}; promotion_gate={alb2012_blocker_promotion}; hard_blocked={alb2012_blocker_hard}; timing_ready={alb2012_blocker_timing_ready}; geography_ready={alb2012_blocker_geography_ready}; outcome_ready={alb2012_blocker_outcome_ready}; climate_ready={alb2012_blocker_climate_ready}; data_write_ready={alb2012_blocker_data_write}; decision={alb2012_blocker_decision}",
        ""
        if counts["alb2012_timing_geography_blocker_resolution_matrix"] == 10
        and counts["alb2012_timing_geography_blocker_resolution_summary"] == 12
        and alb2012_blocker_timing_ready == "0"
        and alb2012_blocker_climate_ready == "0"
        and alb2012_blocker_data_write == "0"
        and alb2012_blocker_decision == "blocked_alb2012_no_timing_geography_fallback_ready"
        else "Run script/114_build_alb2012_timing_geography_blocker_resolution_matrix.py after ALB_2012 timing/geography, questionnaire timing, and outcome audits.",
    )
    acquisition_targets = read_csv_dicts(RESULT_DIR / "minimum_viable_acquisition_targets.csv")
    acquisition_sets = len({row.get("acquisition_set", "") for row in acquisition_targets if row.get("acquisition_set", "")})
    acquisition_countries = len({row.get("country", "") for row in acquisition_targets if row.get("country", "")})
    add(
        rows,
        "evidence",
        "Minimum viable raw-data acquisition plan maps no-go thresholds to manual-download targets",
        status(
            counts["minimum_viable_acquisition_targets"] > 0
            and counts["minimum_viable_download_bundles"] > 0
            and counts["minimum_viable_acquisition_summary"] > 0
        ),
        f"target_rows={counts['minimum_viable_acquisition_targets']}; bundle_rows={counts['minimum_viable_download_bundles']}; summary_rows={counts['minimum_viable_acquisition_summary']}; acquisition_sets={acquisition_sets}; countries={acquisition_countries}",
        ""
        if counts["minimum_viable_acquisition_targets"] > 0
        and counts["minimum_viable_download_bundles"] > 0
        and counts["minimum_viable_acquisition_summary"] > 0
        else "Run script/30_build_minimum_viable_acquisition_plan.py after raw-variable verification protocol generation.",
    )
    climate_plan = read_csv_dicts(TEMP_DIR / "climate_exposure_plan.csv")
    climate_metadata_ready = sum(1 for row in climate_plan if row.get("climate_linkage_gate_status") == "metadata_ready_raw_unverified")
    climate_ready = sum(1 for row in climate_plan if row.get("climate_linkage_gate_status") == "ready_for_climate_linkage_input_build")
    climate_spec_blocked = sum(1 for row in read_csv_dicts(RESULT_DIR / "climate_exposure_specification.csv") if row.get("current_status") == "blocked_until_verified_geography_and_timing")
    add(
        rows,
        "evidence",
        "Climate exposure plan has been built from source probes and raw-ingestion concepts",
        status(counts["climate_exposure_plan"] > 0 and counts["climate_exposure_specification"] > 0 and counts["climate_exposure_plan_summary"] > 0),
        f"plan_rows={counts['climate_exposure_plan']}; spec_rows={counts['climate_exposure_specification']}; metadata_ready_raw_unverified={climate_metadata_ready}; ready_for_linkage={climate_ready}; blocked_specs={climate_spec_blocked}",
        "" if counts["climate_exposure_plan"] > 0 and counts["climate_exposure_specification"] > 0 and counts["climate_exposure_plan_summary"] > 0 else "Run script/23_build_climate_exposure_plan.py after climate source probe and raw-ingestion plan.",
    )
    climate_readiness = read_csv_dicts(RESULT_DIR / "climate_linkage_readiness.csv")
    climate_ready_value = sum(1 for row in climate_readiness if row.get("readiness_status") == "ready_for_climate_linkage_value_audit")
    climate_blocked_value = sum(1 for row in climate_readiness if row.get("readiness_status") != "ready_for_climate_linkage_value_audit")
    add(
        rows,
        "evidence",
        "Climate validation protocol maps timing, geolocation, units, baselines, and source checks",
        status(
            counts["climate_linkage_requirements"] > 0
            and counts["climate_source_method_matrix"] > 0
            and counts["climate_exposure_validation_protocol"] > 0
            and counts["climate_linkage_readiness"] > 0
            and counts["climate_validation_protocol_summary"] > 0
        ),
        f"requirement_rows={counts['climate_linkage_requirements']}; source_rows={counts['climate_source_method_matrix']}; validation_rows={counts['climate_exposure_validation_protocol']}; readiness_rows={counts['climate_linkage_readiness']}; summary_rows={counts['climate_validation_protocol_summary']}; ready={climate_ready_value}; blocked={climate_blocked_value}",
        ""
        if counts["climate_linkage_requirements"] > 0
        and counts["climate_source_method_matrix"] > 0
        and counts["climate_exposure_validation_protocol"] > 0
        and counts["climate_linkage_readiness"] > 0
        and counts["climate_validation_protocol_summary"] > 0
        else "Run script/32_build_climate_validation_protocol.py after climate exposure planning.",
    )
    outcome_plan = read_csv_dicts(TEMP_DIR / "outcome_denominator_plan.csv")
    outcome_metadata_ready = sum(1 for row in outcome_plan if row.get("outcome_gate_status") == "metadata_ready_raw_unverified")
    outcome_ready = sum(1 for row in outcome_plan if row.get("outcome_gate_status") == "ready_for_harmonized_outcome_construction")
    outcome_incomplete = sum(1 for row in outcome_plan if row.get("outcome_gate_status") == "metadata_incomplete_for_outcome")
    add(
        rows,
        "evidence",
        "Outcome denominator/readiness plan has been built",
        status(counts["outcome_denominator_plan"] > 0 and counts["outcome_specification_plan"] > 0 and counts["outcome_denominator_plan_summary"] > 0),
        f"plan_rows={counts['outcome_denominator_plan']}; spec_rows={counts['outcome_specification_plan']}; metadata_ready_raw_unverified={outcome_metadata_ready}; ready_for_construction={outcome_ready}; metadata_incomplete={outcome_incomplete}",
        "" if counts["outcome_denominator_plan"] > 0 and counts["outcome_specification_plan"] > 0 and counts["outcome_denominator_plan_summary"] > 0 else "Run script/24_build_outcome_denominator_plan.py after raw-ingestion and validation-reference probes.",
    )
    sdg_readiness = read_csv_dicts(RESULT_DIR / "sdg382_denominator_country_wave_readiness.csv")
    sdg_ready = sum(1 for row in sdg_readiness if row.get("readiness_status") == "ready_for_household_denominator_value_audit")
    sdg_blocked = sum(1 for row in sdg_readiness if row.get("readiness_status") != "ready_for_household_denominator_value_audit")
    add(
        rows,
        "evidence",
        "SDG 3.8.2 denominator audit plan has been built",
        status(
            counts["sdg382_denominator_requirements"] > 0
            and counts["sdg382_denominator_source_matrix"] > 0
            and counts["sdg382_denominator_country_wave_readiness"] > 0
            and counts["sdg382_denominator_summary"] > 0
        ),
        f"requirement_rows={counts['sdg382_denominator_requirements']}; source_rows={counts['sdg382_denominator_source_matrix']}; country_wave_rows={counts['sdg382_denominator_country_wave_readiness']}; summary_rows={counts['sdg382_denominator_summary']}; ready={sdg_ready}; blocked={sdg_blocked}",
        ""
        if counts["sdg382_denominator_requirements"] > 0
        and counts["sdg382_denominator_source_matrix"] > 0
        and counts["sdg382_denominator_country_wave_readiness"] > 0
        and counts["sdg382_denominator_summary"] > 0
        else "Run script/31_build_sdg382_denominator_audit_plan.py after outcome-denominator planning.",
    )
    modeling_plan = read_csv_dicts(TEMP_DIR / "modeling_identification_plan.csv")
    predictive_ready = sum(1 for row in modeling_plan if row.get("predictive_ml_gate_status") == "ready_for_nonrandom_validation_design")
    reduced_ready = sum(1 for row in modeling_plan if row.get("reduced_form_gate_status") == "ready_for_reduced_form_estimation_design")
    causal_ready = sum(1 for row in modeling_plan if row.get("causal_ml_policy_gate_status") == "ready_for_causal_ml_specification")
    policy_ready = sum(1 for row in modeling_plan if row.get("policy_learning_gate_status") == "ready_for_policy_learning_sensitivity_design")
    add(
        rows,
        "evidence",
        "Modeling/identification readiness plan has been built",
        status(
            counts["modeling_identification_plan"] > 0
            and counts["modeling_validation_plan"] > 0
            and counts["falsification_placebo_plan"] > 0
            and counts["policy_learning_plan"] > 0
            and counts["modeling_identification_plan_summary"] > 0
        ),
        f"plan_rows={counts['modeling_identification_plan']}; validation_rows={counts['modeling_validation_plan']}; falsification_rows={counts['falsification_placebo_plan']}; policy_rows={counts['policy_learning_plan']}; summary_rows={counts['modeling_identification_plan_summary']}; predictive_ready={predictive_ready}; reduced_form_ready={reduced_ready}; causal_ml_ready={causal_ready}; policy_ready={policy_ready}",
        "" if counts["modeling_identification_plan"] > 0 and counts["modeling_validation_plan"] > 0 and counts["falsification_placebo_plan"] > 0 and counts["policy_learning_plan"] > 0 and counts["modeling_identification_plan_summary"] > 0 else "Run script/25_build_modeling_identification_plan.py after outcome, climate, and raw-ingestion plans.",
    )
    mechanism_readiness = read_csv_dicts(RESULT_DIR / "mechanism_readiness_matrix.csv")
    mechanism_ready = sum(1 for row in mechanism_readiness if row.get("readiness_status") == "ready_for_mechanism_analysis_design")
    mechanism_blocked = sum(1 for row in mechanism_readiness if row.get("readiness_status") != "ready_for_mechanism_analysis_design")
    add(
        rows,
        "evidence",
        "Mechanism analysis protocol maps pathway variables to raw-evidence and post-treatment guardrails",
        status(
            counts["mechanism_variable_requirements"] > 0
            and counts["mechanism_pathway_protocol"] > 0
            and counts["mechanism_readiness_matrix"] > 0
            and counts["mechanism_analysis_protocol_summary"] > 0
        ),
        f"requirement_rows={counts['mechanism_variable_requirements']}; pathway_rows={counts['mechanism_pathway_protocol']}; readiness_rows={counts['mechanism_readiness_matrix']}; summary_rows={counts['mechanism_analysis_protocol_summary']}; ready={mechanism_ready}; blocked={mechanism_blocked}",
        ""
        if counts["mechanism_variable_requirements"] > 0
        and counts["mechanism_pathway_protocol"] > 0
        and counts["mechanism_readiness_matrix"] > 0
        and counts["mechanism_analysis_protocol_summary"] > 0
        else "Run script/34_build_mechanism_analysis_protocol.py after modeling-identification planning.",
    )
    empirical_dashboard = read_csv_dicts(RESULT_DIR / "empirical_readiness_dashboard.csv")
    empirical_stage_counts = Counter(row.get("current_stage", "") for row in empirical_dashboard)
    empirical_nogo = read_csv_dicts(RESULT_DIR / "empirical_no_go_threshold_status.csv")
    empirical_nogo_pass = sum(1 for row in empirical_nogo if row.get("status") == "pass")
    add(
        rows,
        "evidence",
        "Consolidated empirical readiness dashboard joins acquisition, data, outcome, climate, modeling, mechanism, and no-go gates",
        status(
            counts["empirical_readiness_dashboard"] > 0
            and counts["empirical_no_go_threshold_status"] > 0
            and counts["empirical_readiness_dashboard_summary"] > 0
        ),
        f"dashboard_rows={counts['empirical_readiness_dashboard']}; no_go_rows={counts['empirical_no_go_threshold_status']}; summary_rows={counts['empirical_readiness_dashboard_summary']}; no_go_pass={empirical_nogo_pass}; stages={dict(empirical_stage_counts)}",
        ""
        if counts["empirical_readiness_dashboard"] > 0
        and counts["empirical_no_go_threshold_status"] > 0
        and counts["empirical_readiness_dashboard_summary"] > 0
        else "Run script/35_build_empirical_readiness_dashboard.py after mechanism analysis protocol generation.",
    )
    first_batch = read_csv_dicts(TEMP_DIR / "first_batch_raw_acquisition_checklist.csv")
    first_batch_raw_tabular = sum(safe_int(row.get("raw_tabular_file_count"), 0) for row in first_batch)
    first_batch_archives = sum(safe_int(row.get("archive_file_count"), 0) for row in first_batch)
    add(
        rows,
        "evidence",
        "First-batch raw acquisition checklist identifies the smallest manual batch for testing 6-country and 10-wave no-go thresholds",
        status(
            counts["first_batch_raw_acquisition_checklist"] > 0
            and counts["first_batch_raw_file_targets"] > 0
            and counts["first_batch_raw_acquisition_summary"] > 0
        ),
        f"checklist_rows={counts['first_batch_raw_acquisition_checklist']}; file_target_rows={counts['first_batch_raw_file_targets']}; summary_rows={counts['first_batch_raw_acquisition_summary']}; first_batch_raw_tabular={first_batch_raw_tabular}; first_batch_archives={first_batch_archives}",
        ""
        if counts["first_batch_raw_acquisition_checklist"] > 0
        and counts["first_batch_raw_file_targets"] > 0
        and counts["first_batch_raw_acquisition_summary"] > 0
        else "Run script/37_build_first_batch_raw_acquisition_checklist.py after minimum viable acquisition planning.",
    )
    first_batch_access = read_csv_dicts(TEMP_DIR / "first_batch_official_raw_access_probe.csv")
    first_batch_access_gate = sum(1 for row in first_batch_access if row.get("access_gate_detected") == "1")
    first_batch_possible_direct = sum(1 for row in first_batch_access if row.get("direct_raw_route_status") == "possible_direct_raw_links_unverified")
    first_batch_manual_required = sum(1 for row in first_batch_access if row.get("manual_action_status") != "direct_link_review_required")
    add(
        rows,
        "evidence",
        "First-batch official raw access probe snapshots get-microdata pages without downloading raw files",
        status(
            counts["first_batch_official_raw_access_probe"] > 0
            and counts["first_batch_official_raw_access_summary"] > 0
        ),
        f"probe_rows={counts['first_batch_official_raw_access_probe']}; summary_rows={counts['first_batch_official_raw_access_summary']}; access_gate_rows={first_batch_access_gate}; possible_direct_raw_link_rows={first_batch_possible_direct}; manual_action_required_rows={first_batch_manual_required}",
        ""
        if counts["first_batch_official_raw_access_probe"] > 0
        and counts["first_batch_official_raw_access_summary"] > 0
        else "Run script/39_probe_first_batch_official_raw_access.py after first-batch raw acquisition checklist generation.",
    )
    first_batch_handoff = read_csv_dicts(TEMP_DIR / "first_batch_manual_download_handoff.csv")
    first_batch_handoff_manual = sum(1 for row in first_batch_handoff if row.get("handoff_status") == "manual_account_terms_download_required")
    first_batch_handoff_raw_ready = sum(1 for row in first_batch_handoff if row.get("handoff_status") == "ready_for_raw_schema_and_value_audit")
    add(
        rows,
        "evidence",
        "First-batch manual download handoff maps official gates to target folders, expected files, and post-download checks",
        status(
            counts["first_batch_manual_download_handoff"] > 0
            and counts["first_batch_manual_download_file_queue"] > 0
            and counts["first_batch_manual_download_handoff_summary"] > 0
        ),
        f"handoff_rows={counts['first_batch_manual_download_handoff']}; file_queue_rows={counts['first_batch_manual_download_file_queue']}; summary_rows={counts['first_batch_manual_download_handoff_summary']}; manual_account_terms_rows={first_batch_handoff_manual}; raw_ready_rows={first_batch_handoff_raw_ready}",
        ""
        if counts["first_batch_manual_download_handoff"] > 0
        and counts["first_batch_manual_download_file_queue"] > 0
        and counts["first_batch_manual_download_handoff_summary"] > 0
        else "Run script/40_build_first_batch_manual_download_handoff.py after first-batch access probe and verification workbook generation.",
    )
    first_batch_docs = read_csv_dicts(TEMP_DIR / "first_batch_public_documentation_audit.csv")
    first_batch_doc_saved = sum(1 for row in first_batch_docs if row.get("coverage_status") == "saved" or row.get("coverage_status", "").startswith("saved_existing_"))
    first_batch_doc_failed = sum(1 for row in first_batch_docs if row.get("coverage_status", "").startswith("failed"))
    add(
        rows,
        "evidence",
        "First-batch public documentation audit snapshots official catalog documentation and metadata endpoints",
        status(
            counts["first_batch_public_documentation_audit"] > 0
            and counts["first_batch_public_documentation_summary"] > 0
        ),
        f"documentation_rows={counts['first_batch_public_documentation_audit']}; summary_rows={counts['first_batch_public_documentation_summary']}; saved_or_reused_rows={first_batch_doc_saved}; failed_rows={first_batch_doc_failed}",
        ""
        if counts["first_batch_public_documentation_audit"] > 0
        and counts["first_batch_public_documentation_summary"] > 0
        else "Run script/41_build_first_batch_public_documentation_audit.py after first-batch manual download handoff generation.",
    )
    first_batch_file_source = read_csv_dicts(TEMP_DIR / "first_batch_file_source_traceability.csv")
    first_batch_file_source_supported = sum(1 for row in first_batch_file_source if row.get("source_trace_status") == "metadata_file_and_examples_supported")
    first_batch_file_source_unsupported = sum(1 for row in first_batch_file_source if row.get("source_trace_status", "").startswith("unsupported_"))
    add(
        rows,
        "evidence",
        "First-batch file-source traceability maps queued modules to public schema and variable metadata",
        status(
            counts["first_batch_file_source_traceability"] > 0
            and counts["first_batch_file_source_traceability_summary"] > 0
        ),
        f"trace_rows={counts['first_batch_file_source_traceability']}; summary_rows={counts['first_batch_file_source_traceability_summary']}; supported_rows={first_batch_file_source_supported}; unsupported_rows={first_batch_file_source_unsupported}",
        ""
        if counts["first_batch_file_source_traceability"] > 0
        and counts["first_batch_file_source_traceability_summary"] > 0
        else "Run script/42_build_first_batch_file_source_traceability.py after first-batch public documentation audit generation.",
    )
    first_batch_merge_key = read_csv_dicts(TEMP_DIR / "first_batch_merge_key_lineage_plan.csv")
    first_batch_merge_key_planned = sum(1 for row in first_batch_merge_key if row.get("merge_key_lineage_status") == "metadata_key_lineage_planned_raw_unverified")
    first_batch_merge_key_raw_ready = sum(1 for row in first_batch_merge_key if row.get("raw_gate_status") != "blocked_raw_microdata")
    add(
        rows,
        "evidence",
        "First-batch merge-key lineage plan maps candidate household/person keys, design variables, timing, and geography before raw verification",
        status(
            counts["first_batch_merge_key_lineage_plan"] > 0
            and counts["first_batch_merge_key_candidate_variables"] > 0
            and counts["first_batch_merge_key_lineage_summary"] > 0
        ),
        f"plan_rows={counts['first_batch_merge_key_lineage_plan']}; candidate_rows={counts['first_batch_merge_key_candidate_variables']}; summary_rows={counts['first_batch_merge_key_lineage_summary']}; planned_rows={first_batch_merge_key_planned}; raw_ready_rows={first_batch_merge_key_raw_ready}",
        ""
        if counts["first_batch_merge_key_lineage_plan"] > 0
        and counts["first_batch_merge_key_candidate_variables"] > 0
        and counts["first_batch_merge_key_lineage_summary"] > 0
        else "Run script/43_build_first_batch_merge_key_lineage_plan.py after first-batch file-source traceability generation.",
    )
    first_batch_value_rows = read_csv_dicts(TEMP_DIR / "first_batch_raw_value_key_audit.csv")
    first_batch_key_rows = read_csv_dicts(TEMP_DIR / "first_batch_raw_merge_key_audit.csv")
    first_batch_value_read_ok = sum(1 for row in first_batch_value_rows if row.get("read_status") == "read_ok")
    first_batch_auto_ready = sum(1 for row in read_csv_dicts(TEMP_DIR / "first_batch_harmonization_value_audit_auto.csv") if row.get("ready_for_recipe") == "1")
    add(
        rows,
        "evidence",
        "First-batch raw value/key audit summarizes observed values and key cardinality for raw-ready datasets without promoting recipes",
        status(
            counts["first_batch_raw_value_key_audit"] > 0
            and counts["first_batch_raw_merge_key_audit"] > 0
            and counts["first_batch_harmonization_value_audit_auto"] > 0
            and counts["first_batch_raw_value_key_summary"] > 0
            and first_batch_auto_ready == 0
        ),
        f"value_rows={counts['first_batch_raw_value_key_audit']}; value_read_ok={first_batch_value_read_ok}; key_rows={counts['first_batch_raw_merge_key_audit']}; auto_value_rows={counts['first_batch_harmonization_value_audit_auto']}; auto_ready_for_recipe={first_batch_auto_ready}; summary_rows={counts['first_batch_raw_value_key_summary']}",
        ""
        if counts["first_batch_raw_value_key_audit"] > 0
        and counts["first_batch_raw_merge_key_audit"] > 0
        and counts["first_batch_harmonization_value_audit_auto"] > 0
        and counts["first_batch_raw_value_key_summary"] > 0
        and first_batch_auto_ready == 0
        else "Run script/45_audit_first_batch_raw_value_keys.py after first-batch merge-key lineage planning; auto rows must remain ready_for_recipe=0.",
    )
    alb_summary = read_csv_dicts(RESULT_DIR / "alb2005_documented_harmonization_summary.csv")
    alb_recipe_ready = next((row.get("value", "0") for row in alb_summary if row.get("metric") == "alb2005_recipe_ready_rows"), "0")
    alb_decision = next((row.get("value", "") for row in alb_summary if row.get("metric") == "alb2005_current_decision"), "")
    add(
        rows,
        "evidence",
        "ALB_2005 documented harmonization review identifies supported candidates, false positives, and remaining blockers",
        status(
            counts["alb2005_documented_variable_evidence"] > 0
            and counts["alb2005_documented_harmonization_summary"] > 0
            and alb_recipe_ready == "0"
            and alb_decision == "not_ready_for_verified_recipe"
        ),
        f"evidence_rows={counts['alb2005_documented_variable_evidence']}; summary_rows={counts['alb2005_documented_harmonization_summary']}; recipe_ready_rows={alb_recipe_ready}; decision={alb_decision}",
        ""
        if counts["alb2005_documented_variable_evidence"] > 0
        and counts["alb2005_documented_harmonization_summary"] > 0
        and alb_recipe_ready == "0"
        and alb_decision == "not_ready_for_verified_recipe"
        else "Run script/46_build_alb2005_documented_harmonization_review.py after first-batch raw value/key audit.",
    )
    alb2002_core_summary = read_csv_dicts(RESULT_DIR / "alb2002_household_core_candidate_summary.csv")
    alb2002_core_ready = next((row.get("value", "0") for row in alb2002_core_summary if row.get("metric") == "alb2002_household_core_recipe_ready_rows"), "0")
    alb2002_core_decision = next((row.get("value", "") for row in alb2002_core_summary if row.get("metric") == "alb2002_household_core_current_decision"), "")
    add(
        rows,
        "evidence",
        "ALB_2002 household core merge audit builds a temp-only candidate with observed timing/geography and keeps data promotion blocked",
        status(
            counts["alb2002_household_core_candidate"] > 0
            and counts["alb2002_household_core_merge_audit"] > 0
            and counts["alb2002_household_core_lineage"] > 0
            and counts["alb2002_household_core_candidate_summary"] > 0
            and alb2002_core_ready == "0"
            and alb2002_core_decision == "temp_candidate_timing_geography_observed_outcome_semantics_pending"
        ),
        f"candidate_rows={counts['alb2002_household_core_candidate']}; merge_audit_rows={counts['alb2002_household_core_merge_audit']}; lineage_rows={counts['alb2002_household_core_lineage']}; summary_rows={counts['alb2002_household_core_candidate_summary']}; recipe_ready_rows={alb2002_core_ready}; decision={alb2002_core_decision}",
        ""
        if counts["alb2002_household_core_candidate"] > 0
        and counts["alb2002_household_core_merge_audit"] > 0
        and counts["alb2002_household_core_lineage"] > 0
        and counts["alb2002_household_core_candidate_summary"] > 0
        and alb2002_core_ready == "0"
        and alb2002_core_decision == "temp_candidate_timing_geography_observed_outcome_semantics_pending"
        else "Run script/54_audit_alb2002_household_core_merge.py and keep the candidate out of data/.",
    )
    alb2002_outcome_summary = read_csv_dicts(RESULT_DIR / "alb2002_provisional_outcome_feasibility_summary.csv")
    alb2002_outcome_ready = next((row.get("value", "0") for row in alb2002_outcome_summary if row.get("metric") == "alb2002_provisional_outcome_ready_rows"), "0")
    alb2002_outcome_decision = next((row.get("value", "") for row in alb2002_outcome_summary if row.get("metric") == "alb2002_provisional_outcome_current_decision"), "")
    add(
        rows,
        "evidence",
        "ALB_2002 provisional outcome feasibility audit computes raw event-rate diagnostics and keeps final outcomes blocked",
        status(
            counts["alb2002_provisional_outcome_feasibility_audit"] > 0
            and counts["alb2002_provisional_outcome_feasibility_summary"] > 0
            and alb2002_outcome_ready == "0"
            and alb2002_outcome_decision == "not_final_outcomes_outcome_semantics_climate_crosswalk_blocked"
        ),
        f"audit_rows={counts['alb2002_provisional_outcome_feasibility_audit']}; summary_rows={counts['alb2002_provisional_outcome_feasibility_summary']}; ready_rows={alb2002_outcome_ready}; decision={alb2002_outcome_decision}",
        ""
        if counts["alb2002_provisional_outcome_feasibility_audit"] > 0
        and counts["alb2002_provisional_outcome_feasibility_summary"] > 0
        and alb2002_outcome_ready == "0"
        and alb2002_outcome_decision == "not_final_outcomes_outcome_semantics_climate_crosswalk_blocked"
        else "Run script/55_audit_alb2002_provisional_outcome_feasibility.py and keep all provisional outcomes blocked from data/.",
    )
    alb2002_semantics_summary = read_csv_dicts(RESULT_DIR / "alb2002_outcome_semantics_raw_value_summary.csv")
    alb2002_semantics_ready = next((row.get("value", "0") for row in alb2002_semantics_summary if row.get("metric") == "alb2002_outcome_semantics_outcome_ready_rows"), "0")
    alb2002_semantics_sdg382_ready = next((row.get("value", "0") for row in alb2002_semantics_summary if row.get("metric") == "alb2002_outcome_semantics_sdg382_ready_rows"), "0")
    alb2002_semantics_decision = next((row.get("value", "") for row in alb2002_semantics_summary if row.get("metric") == "alb2002_outcome_semantics_current_decision"), "")
    add(
        rows,
        "evidence",
        "ALB_2002 raw OOP/access semantics audit records raw labels, values, and skip-pattern blockers while keeping outcome promotion blocked",
        status(
            counts["alb2002_outcome_semantics_raw_value_audit"] > 0
            and counts["alb2002_outcome_semantics_raw_value_summary"] > 0
            and alb2002_semantics_ready == "0"
            and alb2002_semantics_sdg382_ready == "0"
            and alb2002_semantics_decision == "blocked_outcome_semantics_units_recall_skip_patterns_unreviewed"
        ),
        f"audit_rows={counts['alb2002_outcome_semantics_raw_value_audit']}; summary_rows={counts['alb2002_outcome_semantics_raw_value_summary']}; outcome_ready_rows={alb2002_semantics_ready}; sdg382_ready_rows={alb2002_semantics_sdg382_ready}; decision={alb2002_semantics_decision}",
        ""
        if counts["alb2002_outcome_semantics_raw_value_audit"] > 0
        and counts["alb2002_outcome_semantics_raw_value_summary"] > 0
        and alb2002_semantics_ready == "0"
        and alb2002_semantics_sdg382_ready == "0"
        and alb2002_semantics_decision == "blocked_outcome_semantics_units_recall_skip_patterns_unreviewed"
        else "Run script/60_audit_alb2002_outcome_semantics_raw_values.py and keep ALB_2002 outcomes blocked pending manual semantics review.",
    )
    alb2002_health_questionnaire_summary = read_csv_dicts(RESULT_DIR / "alb2002_health_questionnaire_semantics_summary.csv")
    alb2002_health_questionnaire_ready = next((row.get("value", "0") for row in alb2002_health_questionnaire_summary if row.get("metric") == "alb2002_health_questionnaire_outcome_ready_rows"), "0")
    alb2002_health_questionnaire_sdg382_ready = next((row.get("value", "0") for row in alb2002_health_questionnaire_summary if row.get("metric") == "alb2002_health_questionnaire_sdg382_ready_rows"), "0")
    alb2002_health_questionnaire_climate_ready = next((row.get("value", "0") for row in alb2002_health_questionnaire_summary if row.get("metric") == "alb2002_health_questionnaire_climate_linkage_ready_rows"), "0")
    alb2002_health_questionnaire_decision = next((row.get("value", "") for row in alb2002_health_questionnaire_summary if row.get("metric") == "alb2002_health_questionnaire_current_decision"), "")
    add(
        rows,
        "evidence",
        "ALB_2002 health questionnaire semantics audit ties raw OOP/access variables to question text, new-lek units, recall periods, gift scope, and skip paths while keeping promotion blocked",
        status(
            counts["alb2002_health_questionnaire_semantics_audit"] > 0
            and counts["alb2002_health_questionnaire_semantics_summary"] > 0
            and alb2002_health_questionnaire_ready == "0"
            and alb2002_health_questionnaire_sdg382_ready == "0"
            and alb2002_health_questionnaire_climate_ready == "0"
            and alb2002_health_questionnaire_decision == "blocked_alb2002_questionnaire_semantics_seen_but_outcome_not_ready"
        ),
        f"audit_rows={counts['alb2002_health_questionnaire_semantics_audit']}; summary_rows={counts['alb2002_health_questionnaire_semantics_summary']}; outcome_ready_rows={alb2002_health_questionnaire_ready}; sdg382_ready_rows={alb2002_health_questionnaire_sdg382_ready}; climate_ready_rows={alb2002_health_questionnaire_climate_ready}; decision={alb2002_health_questionnaire_decision}",
        ""
        if counts["alb2002_health_questionnaire_semantics_audit"] > 0
        and counts["alb2002_health_questionnaire_semantics_summary"] > 0
        and alb2002_health_questionnaire_ready == "0"
        and alb2002_health_questionnaire_sdg382_ready == "0"
        and alb2002_health_questionnaire_climate_ready == "0"
        and alb2002_health_questionnaire_decision == "blocked_alb2002_questionnaire_semantics_seen_but_outcome_not_ready"
        else "Run script/89_audit_alb2002_health_questionnaire_semantics.py and keep ALB_2002 outcomes blocked pending recipe, SDG, and climate gates.",
    )
    alb2002_oop_policy_summary = read_csv_dicts(RESULT_DIR / "alb2002_oop_aggregation_policy_summary.csv")
    alb2002_oop_policy_rows = next((row.get("value", "0") for row in alb2002_oop_policy_summary if row.get("metric") == "alb2002_oop_aggregation_policy_rows"), "0")
    alb2002_oop_policy_core_4w_match = next((row.get("value", "0") for row in alb2002_oop_policy_summary if row.get("metric") == "alb2002_oop_aggregation_policy_core_4w_match_rows"), "0")
    alb2002_oop_policy_core_12m_match = next((row.get("value", "0") for row in alb2002_oop_policy_summary if row.get("metric") == "alb2002_oop_aggregation_policy_core_12m_match_rows"), "0")
    alb2002_oop_policy_outcome_ready = next((row.get("value", "0") for row in alb2002_oop_policy_summary if row.get("metric") == "alb2002_oop_aggregation_policy_outcome_ready_rows"), "0")
    alb2002_oop_policy_recipe_ready = next((row.get("value", "0") for row in alb2002_oop_policy_summary if row.get("metric") == "alb2002_oop_aggregation_policy_recipe_ready_rows"), "0")
    alb2002_oop_policy_sdg_ready = next((row.get("value", "0") for row in alb2002_oop_policy_summary if row.get("metric") == "alb2002_oop_aggregation_policy_sdg382_ready_rows"), "0")
    alb2002_oop_policy_climate_ready = next((row.get("value", "0") for row in alb2002_oop_policy_summary if row.get("metric") == "alb2002_oop_aggregation_policy_climate_linkage_ready_rows"), "0")
    alb2002_oop_policy_decision = next((row.get("value", "") for row in alb2002_oop_policy_summary if row.get("metric") == "alb2002_oop_aggregation_policy_current_decision"), "")
    add(
        rows,
        "evidence",
        "ALB_2002 OOP aggregation policy audit compares payment-scope and recall-period stress tests while keeping outcome promotion blocked",
        status(
            counts["alb2002_oop_aggregation_policy_audit"] > 0
            and counts["alb2002_oop_aggregation_policy_summary"] > 0
            and alb2002_oop_policy_rows == "11"
            and alb2002_oop_policy_core_4w_match == "3599"
            and alb2002_oop_policy_core_12m_match == "3599"
            and alb2002_oop_policy_outcome_ready == "0"
            and alb2002_oop_policy_recipe_ready == "0"
            and alb2002_oop_policy_sdg_ready == "0"
            and alb2002_oop_policy_climate_ready == "0"
            and alb2002_oop_policy_decision == "blocked_alb2002_oop_aggregation_policy_stress_test_not_outcome_ready"
        ),
        f"audit_rows={counts['alb2002_oop_aggregation_policy_audit']}; summary_rows={counts['alb2002_oop_aggregation_policy_summary']}; policy_rows={alb2002_oop_policy_rows}; core_4w_match_rows={alb2002_oop_policy_core_4w_match}; core_12m_match_rows={alb2002_oop_policy_core_12m_match}; outcome_ready={alb2002_oop_policy_outcome_ready}; recipe_ready={alb2002_oop_policy_recipe_ready}; sdg382_ready={alb2002_oop_policy_sdg_ready}; climate_ready={alb2002_oop_policy_climate_ready}; decision={alb2002_oop_policy_decision}",
        ""
        if counts["alb2002_oop_aggregation_policy_audit"] > 0
        and counts["alb2002_oop_aggregation_policy_summary"] > 0
        and alb2002_oop_policy_outcome_ready == "0"
        and alb2002_oop_policy_recipe_ready == "0"
        and alb2002_oop_policy_sdg_ready == "0"
        and alb2002_oop_policy_climate_ready == "0"
        and alb2002_oop_policy_decision == "blocked_alb2002_oop_aggregation_policy_stress_test_not_outcome_ready"
        else "Run script/91_audit_alb2002_oop_aggregation_policy.py and keep ALB_2002 outcomes blocked until OOP scope, SDG denominator, and climate gates pass.",
    )
    alb2002_skip_missing_summary = read_csv_dicts(RESULT_DIR / "alb2002_skip_missing_semantics_summary.csv")
    alb2002_skip_rows = next((row.get("value", "0") for row in alb2002_skip_missing_summary if row.get("metric") == "alb2002_skip_missing_semantics_rows"), "0")
    alb2002_skip_payment_blocks = next((row.get("value", "0") for row in alb2002_skip_missing_summary if row.get("metric") == "alb2002_skip_missing_payment_block_rows"), "0")
    alb2002_skip_condition_blocks = next((row.get("value", "0") for row in alb2002_skip_missing_summary if row.get("metric") == "alb2002_skip_missing_access_condition_rows"), "0")
    alb2002_skip_positive_rows = next((row.get("value", "0") for row in alb2002_skip_missing_summary if row.get("metric") == "alb2002_skip_missing_payment_positive_when_not_triggered_rows"), "0")
    alb2002_skip_zero_cells = next((row.get("value", "0") for row in alb2002_skip_missing_summary if row.get("metric") == "alb2002_skip_missing_payment_zero_cells_when_not_triggered"), "0")
    alb2002_skip_positive_cells = next((row.get("value", "0") for row in alb2002_skip_missing_summary if row.get("metric") == "alb2002_skip_missing_payment_positive_cells_when_not_triggered"), "0")
    alb2002_skip_outcome_ready = next((row.get("value", "0") for row in alb2002_skip_missing_summary if row.get("metric") == "alb2002_skip_missing_outcome_ready_rows"), "0")
    alb2002_skip_recipe_ready = next((row.get("value", "0") for row in alb2002_skip_missing_summary if row.get("metric") == "alb2002_skip_missing_recipe_ready_rows"), "0")
    alb2002_skip_sdg_ready = next((row.get("value", "0") for row in alb2002_skip_missing_summary if row.get("metric") == "alb2002_skip_missing_sdg382_ready_rows"), "0")
    alb2002_skip_climate_ready = next((row.get("value", "0") for row in alb2002_skip_missing_summary if row.get("metric") == "alb2002_skip_missing_climate_linkage_ready_rows"), "0")
    alb2002_skip_decision = next((row.get("value", "") for row in alb2002_skip_missing_summary if row.get("metric") == "alb2002_skip_missing_current_decision"), "")
    add(
        rows,
        "evidence",
        "ALB_2002 skip/missing audit documents zero-only skipped payment values while keeping outcome promotion blocked",
        status(
            counts["alb2002_skip_missing_semantics_audit"] > 0
            and counts["alb2002_skip_missing_semantics_summary"] > 0
            and alb2002_skip_rows == "12"
            and alb2002_skip_payment_blocks == "7"
            and alb2002_skip_condition_blocks == "5"
            and alb2002_skip_positive_rows == "0"
            and alb2002_skip_zero_cells == "11"
            and alb2002_skip_positive_cells == "0"
            and alb2002_skip_outcome_ready == "0"
            and alb2002_skip_recipe_ready == "0"
            and alb2002_skip_sdg_ready == "0"
            and alb2002_skip_climate_ready == "0"
            and alb2002_skip_decision == "blocked_alb2002_skip_missing_semantics_seen_but_recipe_not_ready"
        ),
        f"audit_rows={counts['alb2002_skip_missing_semantics_audit']}; summary_rows={counts['alb2002_skip_missing_semantics_summary']}; rows={alb2002_skip_rows}; payment_blocks={alb2002_skip_payment_blocks}; condition_blocks={alb2002_skip_condition_blocks}; positive_skipped_rows={alb2002_skip_positive_rows}; zero_skipped_cells={alb2002_skip_zero_cells}; positive_skipped_cells={alb2002_skip_positive_cells}; outcome_ready={alb2002_skip_outcome_ready}; recipe_ready={alb2002_skip_recipe_ready}; sdg382_ready={alb2002_skip_sdg_ready}; climate_ready={alb2002_skip_climate_ready}; decision={alb2002_skip_decision}",
        ""
        if counts["alb2002_skip_missing_semantics_audit"] > 0
        and counts["alb2002_skip_missing_semantics_summary"] > 0
        and alb2002_skip_positive_rows == "0"
        and alb2002_skip_positive_cells == "0"
        and alb2002_skip_outcome_ready == "0"
        and alb2002_skip_recipe_ready == "0"
        and alb2002_skip_sdg_ready == "0"
        and alb2002_skip_climate_ready == "0"
        and alb2002_skip_decision == "blocked_alb2002_skip_missing_semantics_seen_but_recipe_not_ready"
        else "Run script/92_audit_alb2002_skip_missing_semantics.py and keep ALB_2002 outcomes blocked until zero/missing, OOP scope, SDG, and climate gates pass.",
    )
    alb2002_oop_skip_value_summary = read_csv_dicts(RESULT_DIR / "alb2002_oop_skip_value_decision_summary.csv")
    alb2002_oop_skip_value_rows = next((row.get("value", "0") for row in alb2002_oop_skip_value_summary if row.get("metric") == "alb2002_oop_skip_value_decision_rows"), "0")
    alb2002_oop_skip_value_payment_blocks = next((row.get("value", "0") for row in alb2002_oop_skip_value_summary if row.get("metric") == "alb2002_oop_skip_value_payment_block_rows"), "0")
    alb2002_oop_skip_value_condition_blocks = next((row.get("value", "0") for row in alb2002_oop_skip_value_summary if row.get("metric") == "alb2002_oop_skip_value_access_condition_block_rows"), "0")
    alb2002_oop_skip_value_nonmissing_rows = next((row.get("value", "0") for row in alb2002_oop_skip_value_summary if row.get("metric") == "alb2002_oop_skip_value_payment_nonmissing_skipped_rows"), "0")
    alb2002_oop_skip_value_nonmissing_cells = next((row.get("value", "0") for row in alb2002_oop_skip_value_summary if row.get("metric") == "alb2002_oop_skip_value_payment_nonmissing_skipped_cells"), "0")
    alb2002_oop_skip_value_zero_cells = next((row.get("value", "0") for row in alb2002_oop_skip_value_summary if row.get("metric") == "alb2002_oop_skip_value_payment_zero_skipped_cells"), "0")
    alb2002_oop_skip_value_positive_rows = next((row.get("value", "0") for row in alb2002_oop_skip_value_summary if row.get("metric") == "alb2002_oop_skip_value_payment_positive_skipped_rows"), "0")
    alb2002_oop_skip_value_positive_cells = next((row.get("value", "0") for row in alb2002_oop_skip_value_summary if row.get("metric") == "alb2002_oop_skip_value_payment_positive_skipped_cells"), "0")
    alb2002_oop_skip_value_zero_ready = next((row.get("value", "0") for row in alb2002_oop_skip_value_summary if row.get("metric") == "alb2002_oop_skip_value_zero_skip_policy_ready_rows"), "0")
    alb2002_oop_skip_value_recall_ready = next((row.get("value", "0") for row in alb2002_oop_skip_value_summary if row.get("metric") == "alb2002_oop_skip_value_oop_recall_scope_ready_rows"), "0")
    alb2002_oop_skip_value_inclusion_ready = next((row.get("value", "0") for row in alb2002_oop_skip_value_summary if row.get("metric") == "alb2002_oop_skip_value_oop_inclusion_scope_ready_rows"), "0")
    alb2002_oop_skip_value_recipe_ready = next((row.get("value", "0") for row in alb2002_oop_skip_value_summary if row.get("metric") == "alb2002_oop_skip_value_recipe_ready_rows"), "0")
    alb2002_oop_skip_value_outcome_ready = next((row.get("value", "0") for row in alb2002_oop_skip_value_summary if row.get("metric") == "alb2002_oop_skip_value_outcome_ready_rows"), "0")
    alb2002_oop_skip_value_sdg_ready = next((row.get("value", "0") for row in alb2002_oop_skip_value_summary if row.get("metric") == "alb2002_oop_skip_value_sdg382_ready_rows"), "0")
    alb2002_oop_skip_value_climate_ready = next((row.get("value", "0") for row in alb2002_oop_skip_value_summary if row.get("metric") == "alb2002_oop_skip_value_climate_linkage_ready_rows"), "0")
    alb2002_oop_skip_value_decision = next((row.get("value", "") for row in alb2002_oop_skip_value_summary if row.get("metric") == "alb2002_oop_skip_value_current_decision"), "")
    add(
        rows,
        "evidence",
        "ALB_2002 OOP skip-value decision documents no positive skipped-payment leakage without promoting outcomes",
        status(
            counts["alb2002_oop_skip_value_decision_audit"] > 0
            and counts["alb2002_oop_skip_value_decision_summary"] > 0
            and alb2002_oop_skip_value_rows == "5"
            and alb2002_oop_skip_value_payment_blocks == "7"
            and alb2002_oop_skip_value_condition_blocks == "5"
            and alb2002_oop_skip_value_nonmissing_rows == "11"
            and alb2002_oop_skip_value_nonmissing_cells == "11"
            and alb2002_oop_skip_value_zero_cells == "11"
            and alb2002_oop_skip_value_positive_rows == "0"
            and alb2002_oop_skip_value_positive_cells == "0"
            and alb2002_oop_skip_value_zero_ready == "4"
            and alb2002_oop_skip_value_recall_ready == "0"
            and alb2002_oop_skip_value_inclusion_ready == "0"
            and alb2002_oop_skip_value_recipe_ready == "0"
            and alb2002_oop_skip_value_outcome_ready == "0"
            and alb2002_oop_skip_value_sdg_ready == "0"
            and alb2002_oop_skip_value_climate_ready == "0"
            and alb2002_oop_skip_value_decision == "documented_alb2002_oop_skipped_values_zero_only_but_oop_policy_not_ready"
        ),
        f"audit_rows={counts['alb2002_oop_skip_value_decision_audit']}; summary_rows={counts['alb2002_oop_skip_value_decision_summary']}; rows={alb2002_oop_skip_value_rows}; payment_blocks={alb2002_oop_skip_value_payment_blocks}; condition_blocks={alb2002_oop_skip_value_condition_blocks}; nonmissing_skipped_rows={alb2002_oop_skip_value_nonmissing_rows}; nonmissing_skipped_cells={alb2002_oop_skip_value_nonmissing_cells}; zero_skipped_cells={alb2002_oop_skip_value_zero_cells}; positive_skipped_rows={alb2002_oop_skip_value_positive_rows}; positive_skipped_cells={alb2002_oop_skip_value_positive_cells}; zero_skip_ready={alb2002_oop_skip_value_zero_ready}; recall_ready={alb2002_oop_skip_value_recall_ready}; inclusion_ready={alb2002_oop_skip_value_inclusion_ready}; recipe_ready={alb2002_oop_skip_value_recipe_ready}; outcome_ready={alb2002_oop_skip_value_outcome_ready}; sdg382_ready={alb2002_oop_skip_value_sdg_ready}; climate_ready={alb2002_oop_skip_value_climate_ready}; decision={alb2002_oop_skip_value_decision}",
        ""
        if counts["alb2002_oop_skip_value_decision_audit"] > 0
        and counts["alb2002_oop_skip_value_decision_summary"] > 0
        and alb2002_oop_skip_value_positive_rows == "0"
        and alb2002_oop_skip_value_positive_cells == "0"
        and alb2002_oop_skip_value_zero_ready == "4"
        and alb2002_oop_skip_value_recipe_ready == "0"
        and alb2002_oop_skip_value_outcome_ready == "0"
        and alb2002_oop_skip_value_sdg_ready == "0"
        and alb2002_oop_skip_value_climate_ready == "0"
        and alb2002_oop_skip_value_decision == "documented_alb2002_oop_skipped_values_zero_only_but_oop_policy_not_ready"
        else "Run script/97_audit_alb2002_oop_skip_value_decision.py and keep ALB_2002 OOP outcomes blocked until recall, inclusion, denominator, access, SDG, and climate gates pass.",
    )
    alb2002_access_need_summary = read_csv_dicts(RESULT_DIR / "alb2002_access_need_denominator_policy_summary.csv")
    alb2002_access_rows = next((row.get("value", "0") for row in alb2002_access_need_summary if row.get("metric") == "alb2002_access_need_denominator_policy_rows"), "0")
    alb2002_access_households = next((row.get("value", "0") for row in alb2002_access_need_summary if row.get("metric") == "alb2002_access_need_household_rows"), "0")
    alb2002_access_q01_need = next((row.get("value", "0") for row in alb2002_access_need_summary if row.get("metric") == "alb2002_access_need_q01_need_rows"), "0")
    alb2002_access_person_need = next((row.get("value", "0") for row in alb2002_access_need_summary if row.get("metric") == "alb2002_access_need_person_need_household_rows"), "0")
    alb2002_access_any_barrier = next((row.get("value", "0") for row in alb2002_access_need_summary if row.get("metric") == "alb2002_access_need_composite_any_access_barrier_rows"), "0")
    alb2002_access_low_event = next((row.get("value", "0") for row in alb2002_access_need_summary if row.get("metric") == "alb2002_access_need_low_event_rate_rows"), "0")
    alb2002_access_outcome_ready = next((row.get("value", "0") for row in alb2002_access_need_summary if row.get("metric") == "alb2002_access_need_outcome_ready_rows"), "0")
    alb2002_access_recipe_ready = next((row.get("value", "0") for row in alb2002_access_need_summary if row.get("metric") == "alb2002_access_need_recipe_ready_rows"), "0")
    alb2002_access_sdg_ready = next((row.get("value", "0") for row in alb2002_access_need_summary if row.get("metric") == "alb2002_access_need_sdg382_ready_rows"), "0")
    alb2002_access_climate_ready = next((row.get("value", "0") for row in alb2002_access_need_summary if row.get("metric") == "alb2002_access_need_climate_linkage_ready_rows"), "0")
    alb2002_access_decision = next((row.get("value", "") for row in alb2002_access_need_summary if row.get("metric") == "alb2002_access_need_current_decision"), "")
    add(
        rows,
        "evidence",
        "ALB_2002 access/need denominator policy audit separates need, access, cost, distance, and supply/admin denominators while keeping outcome promotion blocked",
        status(
            counts["alb2002_access_need_denominator_policy_audit"] > 0
            and counts["alb2002_access_need_denominator_policy_summary"] > 0
            and alb2002_access_rows == "24"
            and alb2002_access_households == "3599"
            and alb2002_access_q01_need == "3247"
            and alb2002_access_person_need == "2202"
            and alb2002_access_any_barrier == "1861"
            and alb2002_access_low_event == "3"
            and alb2002_access_outcome_ready == "0"
            and alb2002_access_recipe_ready == "0"
            and alb2002_access_sdg_ready == "0"
            and alb2002_access_climate_ready == "0"
            and alb2002_access_decision == "blocked_alb2002_access_need_denominator_policy_not_outcome_ready"
        ),
        f"audit_rows={counts['alb2002_access_need_denominator_policy_audit']}; summary_rows={counts['alb2002_access_need_denominator_policy_summary']}; rows={alb2002_access_rows}; households={alb2002_access_households}; q01_need_rows={alb2002_access_q01_need}; person_need_rows={alb2002_access_person_need}; any_access_barrier_rows={alb2002_access_any_barrier}; low_event_rows={alb2002_access_low_event}; outcome_ready={alb2002_access_outcome_ready}; recipe_ready={alb2002_access_recipe_ready}; sdg382_ready={alb2002_access_sdg_ready}; climate_ready={alb2002_access_climate_ready}; decision={alb2002_access_decision}",
        ""
        if counts["alb2002_access_need_denominator_policy_audit"] > 0
        and counts["alb2002_access_need_denominator_policy_summary"] > 0
        and alb2002_access_outcome_ready == "0"
        and alb2002_access_recipe_ready == "0"
        and alb2002_access_sdg_ready == "0"
        and alb2002_access_climate_ready == "0"
        and alb2002_access_decision == "blocked_alb2002_access_need_denominator_policy_not_outcome_ready"
        else "Run script/93_audit_alb2002_access_need_denominator_policy.py and keep ALB_2002 access outcomes blocked until denominator, trigger, value-code, OOP, SDG, and climate gates pass.",
    )
    alb2002_consumption_sdg_summary = read_csv_dicts(RESULT_DIR / "alb2002_consumption_sdg_denominator_policy_summary.csv")
    alb2002_consumption_sdg_rows = next((row.get("value", "0") for row in alb2002_consumption_sdg_summary if row.get("metric") == "alb2002_consumption_sdg_denominator_policy_rows"), "0")
    alb2002_consumption_sdg_households = next((row.get("value", "0") for row in alb2002_consumption_sdg_summary if row.get("metric") == "alb2002_consumption_sdg_household_rows"), "0")
    alb2002_consumption_sdg_positive_total = next((row.get("value", "0") for row in alb2002_consumption_sdg_summary if row.get("metric") == "alb2002_consumption_sdg_positive_total_consumption_rows"), "0")
    alb2002_consumption_sdg_weight_rows = next((row.get("value", "0") for row in alb2002_consumption_sdg_summary if row.get("metric") == "alb2002_consumption_sdg_positive_household_weight_rows"), "0")
    alb2002_consumption_sdg_size_rows = next((row.get("value", "0") for row in alb2002_consumption_sdg_summary if row.get("metric") == "alb2002_consumption_sdg_positive_household_size_rows"), "0")
    alb2002_consumption_sdg_spl_ready = next((row.get("value", "0") for row in alb2002_consumption_sdg_summary if row.get("metric") == "alb2002_consumption_sdg_spl_ready_rows"), "0")
    alb2002_consumption_sdg_ppp_cpi_ready = next((row.get("value", "0") for row in alb2002_consumption_sdg_summary if row.get("metric") == "alb2002_consumption_sdg_ppp_cpi_ready_rows"), "0")
    alb2002_consumption_sdg_discretionary_ready = next((row.get("value", "0") for row in alb2002_consumption_sdg_summary if row.get("metric") == "alb2002_consumption_sdg_discretionary_budget_ready_rows"), "0")
    alb2002_consumption_sdg_che_ready = next((row.get("value", "0") for row in alb2002_consumption_sdg_summary if row.get("metric") == "alb2002_consumption_sdg_che_denominator_ready_rows"), "0")
    alb2002_consumption_sdg_recipe_ready = next((row.get("value", "0") for row in alb2002_consumption_sdg_summary if row.get("metric") == "alb2002_consumption_sdg_recipe_ready_rows"), "0")
    alb2002_consumption_sdg_outcome_ready = next((row.get("value", "0") for row in alb2002_consumption_sdg_summary if row.get("metric") == "alb2002_consumption_sdg_outcome_ready_rows"), "0")
    alb2002_consumption_sdg_sdg_ready = next((row.get("value", "0") for row in alb2002_consumption_sdg_summary if row.get("metric") == "alb2002_consumption_sdg_sdg382_ready_rows"), "0")
    alb2002_consumption_sdg_climate_ready = next((row.get("value", "0") for row in alb2002_consumption_sdg_summary if row.get("metric") == "alb2002_consumption_sdg_climate_linkage_ready_rows"), "0")
    alb2002_consumption_sdg_decision = next((row.get("value", "") for row in alb2002_consumption_sdg_summary if row.get("metric") == "alb2002_consumption_sdg_current_decision"), "")
    add(
        rows,
        "evidence",
        "ALB_2002 consumption/SDG denominator policy audit quantifies denominator evidence while keeping CHE, SDG, outcome, recipe, and climate promotion blocked",
        status(
            counts["alb2002_consumption_sdg_denominator_policy_audit"] > 0
            and counts["alb2002_consumption_sdg_denominator_policy_summary"] > 0
            and alb2002_consumption_sdg_rows == "14"
            and alb2002_consumption_sdg_households == "3599"
            and alb2002_consumption_sdg_positive_total == "3599"
            and alb2002_consumption_sdg_weight_rows == "3599"
            and alb2002_consumption_sdg_size_rows == "3599"
            and alb2002_consumption_sdg_spl_ready == "0"
            and alb2002_consumption_sdg_ppp_cpi_ready == "0"
            and alb2002_consumption_sdg_discretionary_ready == "0"
            and alb2002_consumption_sdg_che_ready == "0"
            and alb2002_consumption_sdg_recipe_ready == "0"
            and alb2002_consumption_sdg_outcome_ready == "0"
            and alb2002_consumption_sdg_sdg_ready == "0"
            and alb2002_consumption_sdg_climate_ready == "0"
            and alb2002_consumption_sdg_decision == "blocked_alb2002_consumption_sdg_denominator_policy_not_sdg_ready"
        ),
        f"audit_rows={counts['alb2002_consumption_sdg_denominator_policy_audit']}; summary_rows={counts['alb2002_consumption_sdg_denominator_policy_summary']}; rows={alb2002_consumption_sdg_rows}; households={alb2002_consumption_sdg_households}; positive_total={alb2002_consumption_sdg_positive_total}; positive_weight={alb2002_consumption_sdg_weight_rows}; positive_household_size={alb2002_consumption_sdg_size_rows}; spl_ready={alb2002_consumption_sdg_spl_ready}; ppp_cpi_ready={alb2002_consumption_sdg_ppp_cpi_ready}; discretionary_ready={alb2002_consumption_sdg_discretionary_ready}; che_ready={alb2002_consumption_sdg_che_ready}; recipe_ready={alb2002_consumption_sdg_recipe_ready}; outcome_ready={alb2002_consumption_sdg_outcome_ready}; sdg382_ready={alb2002_consumption_sdg_sdg_ready}; climate_ready={alb2002_consumption_sdg_climate_ready}; decision={alb2002_consumption_sdg_decision}",
        ""
        if counts["alb2002_consumption_sdg_denominator_policy_audit"] > 0
        and counts["alb2002_consumption_sdg_denominator_policy_summary"] > 0
        and alb2002_consumption_sdg_recipe_ready == "0"
        and alb2002_consumption_sdg_outcome_ready == "0"
        and alb2002_consumption_sdg_sdg_ready == "0"
        and alb2002_consumption_sdg_climate_ready == "0"
        and alb2002_consumption_sdg_decision == "blocked_alb2002_consumption_sdg_denominator_policy_not_sdg_ready"
        else "Run script/94_audit_alb2002_consumption_sdg_denominator_policy.py and keep ALB_2002 financial outcomes blocked until consumption unit/period, OOP alignment, SPL, PPP/CPI, discretionary budget, and climate gates pass.",
    )
    alb2002_consumption_construction_summary = read_csv_dicts(RESULT_DIR / "alb2002_consumption_construction_source_summary.csv")
    alb2002_consumption_construction_rows = next((row.get("value", "0") for row in alb2002_consumption_construction_summary if row.get("metric") == "alb2002_consumption_construction_source_audit_rows"), "0")
    alb2002_consumption_construction_pdf_present = next((row.get("value", "0") for row in alb2002_consumption_construction_summary if row.get("metric") == "alb2002_consumption_construction_public_pdf_present"), "0")
    alb2002_consumption_construction_zip_present = next((row.get("value", "0") for row in alb2002_consumption_construction_summary if row.get("metric") == "alb2002_consumption_construction_program_zip_present"), "0")
    alb2002_consumption_construction_do_files = next((row.get("value", "0") for row in alb2002_consumption_construction_summary if row.get("metric") == "alb2002_consumption_construction_do_file_rows"), "0")
    alb2002_consumption_construction_totcons_do = next((row.get("value", "0") for row in alb2002_consumption_construction_summary if row.get("metric") == "alb2002_consumption_construction_totcons_do_present"), "0")
    alb2002_consumption_construction_poverty_do = next((row.get("value", "0") for row in alb2002_consumption_construction_summary if row.get("metric") == "alb2002_consumption_construction_poverty_do_present"), "0")
    alb2002_consumption_construction_metadata_json = next((row.get("value", "0") for row in alb2002_consumption_construction_summary if row.get("metric") == "alb2002_consumption_construction_metadata_json_present"), "0")
    alb2002_consumption_construction_documentation_ready = next((row.get("value", "0") for row in alb2002_consumption_construction_summary if row.get("metric") == "alb2002_consumption_construction_documentation_ready_rows"), "0")
    alb2002_consumption_construction_mapping_ready = next((row.get("value", "0") for row in alb2002_consumption_construction_summary if row.get("metric") == "alb2002_consumption_construction_released_variable_mapping_ready_rows"), "0")
    alb2002_consumption_construction_denominator_ready = next((row.get("value", "0") for row in alb2002_consumption_construction_summary if row.get("metric") == "alb2002_consumption_construction_denominator_variant_ready_rows"), "0")
    alb2002_consumption_construction_recipe_ready = next((row.get("value", "0") for row in alb2002_consumption_construction_summary if row.get("metric") == "alb2002_consumption_construction_recipe_ready_rows"), "0")
    alb2002_consumption_construction_outcome_ready = next((row.get("value", "0") for row in alb2002_consumption_construction_summary if row.get("metric") == "alb2002_consumption_construction_outcome_ready_rows"), "0")
    alb2002_consumption_construction_sdg_ready = next((row.get("value", "0") for row in alb2002_consumption_construction_summary if row.get("metric") == "alb2002_consumption_construction_sdg382_ready_rows"), "0")
    alb2002_consumption_construction_climate_ready = next((row.get("value", "0") for row in alb2002_consumption_construction_summary if row.get("metric") == "alb2002_consumption_construction_climate_linkage_ready_rows"), "0")
    alb2002_consumption_construction_decision = next((row.get("value", "") for row in alb2002_consumption_construction_summary if row.get("metric") == "alb2002_consumption_construction_current_decision"), "")
    add(
        rows,
        "evidence",
        "ALB_2002 public consumption-construction sources document the total-budget denominator variant without promoting outcomes",
        status(
            counts["alb2002_consumption_construction_source_audit"] > 0
            and counts["alb2002_consumption_construction_source_summary"] > 0
            and alb2002_consumption_construction_rows == "9"
            and alb2002_consumption_construction_pdf_present == "1"
            and alb2002_consumption_construction_zip_present == "1"
            and alb2002_consumption_construction_do_files == "19"
            and alb2002_consumption_construction_totcons_do == "1"
            and alb2002_consumption_construction_poverty_do == "1"
            and alb2002_consumption_construction_metadata_json == "1"
            and alb2002_consumption_construction_documentation_ready == "9"
            and alb2002_consumption_construction_mapping_ready == "3"
            and alb2002_consumption_construction_denominator_ready == "8"
            and alb2002_consumption_construction_recipe_ready == "0"
            and alb2002_consumption_construction_outcome_ready == "0"
            and alb2002_consumption_construction_sdg_ready == "0"
            and alb2002_consumption_construction_climate_ready == "0"
            and alb2002_consumption_construction_decision == "documented_alb2002_consumption_aggregate_but_not_outcome_sdg_climate_ready"
        ),
        f"audit_rows={counts['alb2002_consumption_construction_source_audit']}; summary_rows={counts['alb2002_consumption_construction_source_summary']}; rows={alb2002_consumption_construction_rows}; public_pdf={alb2002_consumption_construction_pdf_present}; program_zip={alb2002_consumption_construction_zip_present}; do_files={alb2002_consumption_construction_do_files}; totcons_do={alb2002_consumption_construction_totcons_do}; poverty_do={alb2002_consumption_construction_poverty_do}; metadata_json={alb2002_consumption_construction_metadata_json}; documentation_ready={alb2002_consumption_construction_documentation_ready}; released_variable_mapping_ready={alb2002_consumption_construction_mapping_ready}; denominator_variant_ready={alb2002_consumption_construction_denominator_ready}; recipe_ready={alb2002_consumption_construction_recipe_ready}; outcome_ready={alb2002_consumption_construction_outcome_ready}; sdg382_ready={alb2002_consumption_construction_sdg_ready}; climate_ready={alb2002_consumption_construction_climate_ready}; decision={alb2002_consumption_construction_decision}",
        ""
        if counts["alb2002_consumption_construction_source_audit"] > 0
        and counts["alb2002_consumption_construction_source_summary"] > 0
        and alb2002_consumption_construction_documentation_ready == "9"
        and alb2002_consumption_construction_mapping_ready == "3"
        and alb2002_consumption_construction_denominator_ready == "8"
        and alb2002_consumption_construction_recipe_ready == "0"
        and alb2002_consumption_construction_outcome_ready == "0"
        and alb2002_consumption_construction_sdg_ready == "0"
        and alb2002_consumption_construction_climate_ready == "0"
        and alb2002_consumption_construction_decision == "documented_alb2002_consumption_aggregate_but_not_outcome_sdg_climate_ready"
        else "Run script/96_audit_alb2002_consumption_construction_sources.py and keep ALB_2002 outcome, SDG, and climate promotion blocked after documenting the denominator variant.",
    )
    alb2002_consumption_aggregate_summary = read_csv_dicts(RESULT_DIR / "alb2002_consumption_aggregate_metadata_crosswalk_summary.csv")
    alb2002_consumption_aggregate_rows = next((row.get("value", "0") for row in alb2002_consumption_aggregate_summary if row.get("metric") == "alb2002_consumption_aggregate_crosswalk_rows"), "0")
    alb2002_consumption_aggregate_local_rows = next((row.get("value", "0") for row in alb2002_consumption_aggregate_summary if row.get("metric") == "alb2002_consumption_aggregate_crosswalk_local_poverty_rows"), "0")
    alb2002_consumption_aggregate_metadata_rows = next((row.get("value", "0") for row in alb2002_consumption_aggregate_summary if row.get("metric") == "alb2002_consumption_aggregate_crosswalk_metadata_catalog_rows"), "0")
    alb2002_consumption_aggregate_totcons_positive = next((row.get("value", "0") for row in alb2002_consumption_aggregate_summary if row.get("metric") == "alb2002_consumption_aggregate_crosswalk_raw_totcons_positive_rows"), "0")
    alb2002_consumption_aggregate_totcons_match = next((row.get("value", "0") for row in alb2002_consumption_aggregate_summary if row.get("metric") == "alb2002_consumption_aggregate_crosswalk_candidate_totcons_match_rows"), "0")
    alb2002_consumption_aggregate_formula_hits = next((row.get("value", "0") for row in alb2002_consumption_aggregate_summary if row.get("metric") == "alb2002_consumption_aggregate_crosswalk_questionnaire_aggregate_formula_hits"), "0")
    alb2002_consumption_aggregate_construction_source_rows = next((row.get("value", "0") for row in alb2002_consumption_aggregate_summary if row.get("metric") == "alb2002_consumption_aggregate_crosswalk_construction_source_rows"), "0")
    alb2002_consumption_aggregate_construction_do_files = next((row.get("value", "0") for row in alb2002_consumption_aggregate_summary if row.get("metric") == "alb2002_consumption_aggregate_crosswalk_construction_do_file_rows"), "0")
    alb2002_consumption_aggregate_unit_period_ready = next((row.get("value", "0") for row in alb2002_consumption_aggregate_summary if row.get("metric") == "alb2002_consumption_aggregate_crosswalk_metadata_unit_period_ready_rows"), "0")
    alb2002_consumption_aggregate_documentation_ready = next((row.get("value", "0") for row in alb2002_consumption_aggregate_summary if row.get("metric") == "alb2002_consumption_aggregate_crosswalk_official_documentation_ready_rows"), "0")
    alb2002_consumption_aggregate_mapping_ready = next((row.get("value", "0") for row in alb2002_consumption_aggregate_summary if row.get("metric") == "alb2002_consumption_aggregate_crosswalk_released_variable_mapping_ready_rows"), "0")
    alb2002_consumption_aggregate_denominator_ready = next((row.get("value", "0") for row in alb2002_consumption_aggregate_summary if row.get("metric") == "alb2002_consumption_aggregate_crosswalk_denominator_variant_ready_rows"), "0")
    alb2002_consumption_aggregate_recipe_ready = next((row.get("value", "0") for row in alb2002_consumption_aggregate_summary if row.get("metric") == "alb2002_consumption_aggregate_crosswalk_recipe_ready_rows"), "0")
    alb2002_consumption_aggregate_outcome_ready = next((row.get("value", "0") for row in alb2002_consumption_aggregate_summary if row.get("metric") == "alb2002_consumption_aggregate_crosswalk_outcome_ready_rows"), "0")
    alb2002_consumption_aggregate_sdg_ready = next((row.get("value", "0") for row in alb2002_consumption_aggregate_summary if row.get("metric") == "alb2002_consumption_aggregate_crosswalk_sdg382_ready_rows"), "0")
    alb2002_consumption_aggregate_climate_ready = next((row.get("value", "0") for row in alb2002_consumption_aggregate_summary if row.get("metric") == "alb2002_consumption_aggregate_crosswalk_climate_linkage_ready_rows"), "0")
    alb2002_consumption_aggregate_decision = next((row.get("value", "") for row in alb2002_consumption_aggregate_summary if row.get("metric") == "alb2002_consumption_aggregate_crosswalk_current_decision"), "")
    add(
        rows,
        "evidence",
        "ALB_2002 consumption aggregate metadata crosswalk verifies raw `totcons` as documented public `totcons3` while keeping promotion blocked",
        status(
            counts["alb2002_consumption_aggregate_metadata_crosswalk_audit"] > 0
            and counts["alb2002_consumption_aggregate_metadata_crosswalk_summary"] > 0
            and alb2002_consumption_aggregate_rows == "11"
            and alb2002_consumption_aggregate_local_rows == "3599"
            and alb2002_consumption_aggregate_metadata_rows == "0"
            and alb2002_consumption_aggregate_totcons_positive == "3599"
            and alb2002_consumption_aggregate_totcons_match == "3599"
            and alb2002_consumption_aggregate_formula_hits == "0"
            and alb2002_consumption_aggregate_construction_source_rows == "9"
            and alb2002_consumption_aggregate_construction_do_files == "19"
            and alb2002_consumption_aggregate_unit_period_ready == "8"
            and alb2002_consumption_aggregate_documentation_ready == "9"
            and alb2002_consumption_aggregate_mapping_ready == "3"
            and alb2002_consumption_aggregate_denominator_ready == "8"
            and alb2002_consumption_aggregate_recipe_ready == "0"
            and alb2002_consumption_aggregate_outcome_ready == "0"
            and alb2002_consumption_aggregate_sdg_ready == "0"
            and alb2002_consumption_aggregate_climate_ready == "0"
            and alb2002_consumption_aggregate_decision == "documented_alb2002_consumption_aggregate_but_not_outcome_sdg_climate_ready"
        ),
        f"audit_rows={counts['alb2002_consumption_aggregate_metadata_crosswalk_audit']}; summary_rows={counts['alb2002_consumption_aggregate_metadata_crosswalk_summary']}; rows={alb2002_consumption_aggregate_rows}; local_poverty_rows={alb2002_consumption_aggregate_local_rows}; metadata_catalog_rows={alb2002_consumption_aggregate_metadata_rows}; raw_totcons_positive={alb2002_consumption_aggregate_totcons_positive}; candidate_totcons_match={alb2002_consumption_aggregate_totcons_match}; questionnaire_formula_hits={alb2002_consumption_aggregate_formula_hits}; construction_source_rows={alb2002_consumption_aggregate_construction_source_rows}; construction_do_files={alb2002_consumption_aggregate_construction_do_files}; metadata_unit_period_ready={alb2002_consumption_aggregate_unit_period_ready}; documentation_ready={alb2002_consumption_aggregate_documentation_ready}; released_variable_mapping_ready={alb2002_consumption_aggregate_mapping_ready}; denominator_variant_ready={alb2002_consumption_aggregate_denominator_ready}; recipe_ready={alb2002_consumption_aggregate_recipe_ready}; outcome_ready={alb2002_consumption_aggregate_outcome_ready}; sdg382_ready={alb2002_consumption_aggregate_sdg_ready}; climate_ready={alb2002_consumption_aggregate_climate_ready}; decision={alb2002_consumption_aggregate_decision}",
        ""
        if counts["alb2002_consumption_aggregate_metadata_crosswalk_audit"] > 0
        and counts["alb2002_consumption_aggregate_metadata_crosswalk_summary"] > 0
        and alb2002_consumption_aggregate_documentation_ready == "9"
        and alb2002_consumption_aggregate_mapping_ready == "3"
        and alb2002_consumption_aggregate_denominator_ready == "8"
        and alb2002_consumption_aggregate_recipe_ready == "0"
        and alb2002_consumption_aggregate_outcome_ready == "0"
        and alb2002_consumption_aggregate_sdg_ready == "0"
        and alb2002_consumption_aggregate_climate_ready == "0"
        and alb2002_consumption_aggregate_decision == "documented_alb2002_consumption_aggregate_but_not_outcome_sdg_climate_ready"
        else "Run script/96_audit_alb2002_consumption_construction_sources.py then script/95_audit_alb2002_consumption_aggregate_metadata_crosswalk.py; keep ALB_2002 outcome, SDG, and climate promotion blocked until OOP, SPL/PPP/CPI, discretionary-budget, and geography gates pass.",
    )
    alb2002_period_aligned_che_summary = read_csv_dicts(RESULT_DIR / "alb2002_period_aligned_che_policy_summary.csv")
    alb2002_period_aligned_che_rows = next((row.get("value", "0") for row in alb2002_period_aligned_che_summary if row.get("metric") == "alb2002_period_aligned_che_policy_rows"), "0")
    alb2002_period_aligned_che_households = next((row.get("value", "0") for row in alb2002_period_aligned_che_summary if row.get("metric") == "alb2002_period_aligned_che_household_rows"), "0")
    alb2002_period_aligned_che_denominator_rows = next((row.get("value", "0") for row in alb2002_period_aligned_che_summary if row.get("metric") == "alb2002_period_aligned_che_denominator_rows"), "0")
    alb2002_period_aligned_che_ready = next((row.get("value", "0") for row in alb2002_period_aligned_che_summary if row.get("metric") == "alb2002_period_aligned_che_period_alignment_ready_rows"), "0")
    alb2002_period_aligned_che_che10 = next((row.get("value", "") for row in alb2002_period_aligned_che_summary if row.get("metric") == "alb2002_period_aligned_che_combined_che10_rate"), "")
    alb2002_period_aligned_che_che25 = next((row.get("value", "") for row in alb2002_period_aligned_che_summary if row.get("metric") == "alb2002_period_aligned_che_combined_che25_rate"), "")
    alb2002_period_aligned_che_outcome_ready = next((row.get("value", "0") for row in alb2002_period_aligned_che_summary if row.get("metric") == "alb2002_period_aligned_che_outcome_ready_rows"), "0")
    alb2002_period_aligned_che_recipe_ready = next((row.get("value", "0") for row in alb2002_period_aligned_che_summary if row.get("metric") == "alb2002_period_aligned_che_recipe_ready_rows"), "0")
    alb2002_period_aligned_che_sdg_ready = next((row.get("value", "0") for row in alb2002_period_aligned_che_summary if row.get("metric") == "alb2002_period_aligned_che_sdg382_ready_rows"), "0")
    alb2002_period_aligned_che_climate_ready = next((row.get("value", "0") for row in alb2002_period_aligned_che_summary if row.get("metric") == "alb2002_period_aligned_che_climate_linkage_ready_rows"), "0")
    alb2002_period_aligned_che_decision = next((row.get("value", "") for row in alb2002_period_aligned_che_summary if row.get("metric") == "alb2002_period_aligned_che_current_decision"), "")
    add(
        rows,
        "evidence",
        "ALB_2002 period-aligned CHE policy audit aligns OOP recall windows to monthly total budget while keeping outcome promotion blocked",
        status(
            counts["alb2002_period_aligned_che_policy_audit"] > 0
            and counts["alb2002_period_aligned_che_policy_summary"] > 0
            and alb2002_period_aligned_che_rows == "3"
            and alb2002_period_aligned_che_households == "3599"
            and alb2002_period_aligned_che_denominator_rows == "3599"
            and alb2002_period_aligned_che_ready == "3"
            and alb2002_period_aligned_che_che10 != ""
            and alb2002_period_aligned_che_che25 != ""
            and alb2002_period_aligned_che_outcome_ready == "0"
            and alb2002_period_aligned_che_recipe_ready == "0"
            and alb2002_period_aligned_che_sdg_ready == "0"
            and alb2002_period_aligned_che_climate_ready == "0"
            and alb2002_period_aligned_che_decision == "blocked_alb2002_period_aligned_che_policy_not_outcome_ready"
        ),
        f"audit_rows={counts['alb2002_period_aligned_che_policy_audit']}; summary_rows={counts['alb2002_period_aligned_che_policy_summary']}; policy_rows={alb2002_period_aligned_che_rows}; household_rows={alb2002_period_aligned_che_households}; denominator_rows={alb2002_period_aligned_che_denominator_rows}; period_alignment_ready={alb2002_period_aligned_che_ready}; combined_che10={alb2002_period_aligned_che_che10}; combined_che25={alb2002_period_aligned_che_che25}; outcome_ready={alb2002_period_aligned_che_outcome_ready}; recipe_ready={alb2002_period_aligned_che_recipe_ready}; sdg382_ready={alb2002_period_aligned_che_sdg_ready}; climate_ready={alb2002_period_aligned_che_climate_ready}; decision={alb2002_period_aligned_che_decision}",
        ""
        if counts["alb2002_period_aligned_che_policy_audit"] > 0
        and counts["alb2002_period_aligned_che_policy_summary"] > 0
        and alb2002_period_aligned_che_rows == "3"
        and alb2002_period_aligned_che_outcome_ready == "0"
        and alb2002_period_aligned_che_climate_ready == "0"
        and alb2002_period_aligned_che_decision == "blocked_alb2002_period_aligned_che_policy_not_outcome_ready"
        else "Run script/99_audit_alb2002_period_aligned_che_policy.py and keep CHE rows as diagnostics until OOP inclusion, recipe, benchmark, and geography gates pass.",
    )
    alb2002_che_candidate_summary = read_csv_dicts(RESULT_DIR / "alb2002_che_candidate_outcome_summary.csv")
    alb2002_che_candidate_households = next((row.get("value", "0") for row in alb2002_che_candidate_summary if row.get("metric") == "alb2002_che_candidate_household_rows"), "0")
    alb2002_che_candidate_denominator = next((row.get("value", "0") for row in alb2002_che_candidate_summary if row.get("metric") == "alb2002_che_candidate_denominator_rows"), "0")
    alb2002_che_candidate_che10_rows = next((row.get("value", "0") for row in alb2002_che_candidate_summary if row.get("metric") == "alb2002_che_candidate_che10_rows"), "0")
    alb2002_che_candidate_che10_rate = next((row.get("value", "") for row in alb2002_che_candidate_summary if row.get("metric") == "alb2002_che_candidate_che10_rate"), "")
    alb2002_che_candidate_che25_rows = next((row.get("value", "0") for row in alb2002_che_candidate_summary if row.get("metric") == "alb2002_che_candidate_che25_rows"), "0")
    alb2002_che_candidate_che25_rate = next((row.get("value", "") for row in alb2002_che_candidate_summary if row.get("metric") == "alb2002_che_candidate_che25_rate"), "")
    alb2002_che_candidate_promotion_ready = next((row.get("value", "0") for row in alb2002_che_candidate_summary if row.get("metric") == "alb2002_che_candidate_outcome_promotion_ready_rows"), "0")
    alb2002_che_candidate_climate_ready = next((row.get("value", "0") for row in alb2002_che_candidate_summary if row.get("metric") == "alb2002_che_candidate_climate_linkage_ready_rows"), "0")
    alb2002_che_candidate_decision = next((row.get("value", "") for row in alb2002_che_candidate_summary if row.get("metric") == "alb2002_che_candidate_current_decision"), "")
    add(
        rows,
        "evidence",
        "ALB_2002 household-level CHE10/CHE25 candidate outcomes are constructed in temp while final outcome promotion stays blocked",
        status(
            counts["alb2002_che_candidate_household_outcomes"] == 3599
            and counts["alb2002_che_candidate_outcome_lineage"] == 6
            and counts["alb2002_che_candidate_outcome_audit"] == 4
            and counts["alb2002_che_candidate_outcome_summary"] > 0
            and file_ok(REPORT_DIR / "alb2002_che_candidate_outcome_audit.md")
            and alb2002_che_candidate_households == "3599"
            and alb2002_che_candidate_denominator == "3599"
            and alb2002_che_candidate_che10_rows == "824"
            and alb2002_che_candidate_che10_rate == "0.228952"
            and alb2002_che_candidate_che25_rows == "290"
            and alb2002_che_candidate_che25_rate == "0.0805779"
            and alb2002_che_candidate_promotion_ready == "0"
            and alb2002_che_candidate_climate_ready == "0"
            and alb2002_che_candidate_decision == "blocked_alb2002_che_candidate_not_promoted_due_recipe_sdg_climate_gates"
        ),
        f"household_rows={counts['alb2002_che_candidate_household_outcomes']}; lineage_rows={counts['alb2002_che_candidate_outcome_lineage']}; audit_rows={counts['alb2002_che_candidate_outcome_audit']}; summary_rows={counts['alb2002_che_candidate_outcome_summary']}; denominator_rows={alb2002_che_candidate_denominator}; che10_rows={alb2002_che_candidate_che10_rows}; che10_rate={alb2002_che_candidate_che10_rate}; che25_rows={alb2002_che_candidate_che25_rows}; che25_rate={alb2002_che_candidate_che25_rate}; outcome_promotion_ready={alb2002_che_candidate_promotion_ready}; climate_ready={alb2002_che_candidate_climate_ready}; decision={alb2002_che_candidate_decision}",
        ""
        if counts["alb2002_che_candidate_household_outcomes"] == 3599
        and counts["alb2002_che_candidate_outcome_audit"] == 4
        and alb2002_che_candidate_promotion_ready == "0"
        and alb2002_che_candidate_climate_ready == "0"
        and alb2002_che_candidate_decision == "blocked_alb2002_che_candidate_not_promoted_due_recipe_sdg_climate_gates"
        else "Run script/101_build_alb2002_che_candidate_outcomes.py after the period-aligned CHE and minimum recipe audits; keep the rows in temp until recipe, SDG, benchmark, and climate gates pass.",
    )
    alb2002_access_candidate_summary = read_csv_dicts(RESULT_DIR / "alb2002_access_candidate_outcome_summary.csv")
    alb2002_access_candidate_households = next((row.get("value", "0") for row in alb2002_access_candidate_summary if row.get("metric") == "alb2002_access_candidate_household_rows"), "0")
    alb2002_access_candidate_q01_need = next((row.get("value", "0") for row in alb2002_access_candidate_summary if row.get("metric") == "alb2002_access_candidate_q01_need_rows"), "0")
    alb2002_access_candidate_person_need = next((row.get("value", "0") for row in alb2002_access_candidate_summary if row.get("metric") == "alb2002_access_candidate_person_need_rows"), "0")
    alb2002_access_candidate_q01_cost = next((row.get("value", "0") for row in alb2002_access_candidate_summary if row.get("metric") == "alb2002_access_candidate_q01_cost_difficulty_rows"), "0")
    alb2002_access_candidate_any = next((row.get("value", "0") for row in alb2002_access_candidate_summary if row.get("metric") == "alb2002_access_candidate_composite_any_rows"), "0")
    alb2002_access_candidate_cost = next((row.get("value", "0") for row in alb2002_access_candidate_summary if row.get("metric") == "alb2002_access_candidate_composite_cost_rows"), "0")
    alb2002_access_candidate_low_event = next((row.get("value", "0") for row in alb2002_access_candidate_summary if row.get("metric") == "alb2002_access_candidate_low_event_rate_rows"), "0")
    alb2002_access_candidate_promotion_ready = next((row.get("value", "0") for row in alb2002_access_candidate_summary if row.get("metric") == "alb2002_access_candidate_outcome_promotion_ready_rows"), "0")
    alb2002_access_candidate_recipe_ready = next((row.get("value", "0") for row in alb2002_access_candidate_summary if row.get("metric") == "alb2002_access_candidate_recipe_ready_rows"), "0")
    alb2002_access_candidate_sdg_ready = next((row.get("value", "0") for row in alb2002_access_candidate_summary if row.get("metric") == "alb2002_access_candidate_sdg382_ready_rows"), "0")
    alb2002_access_candidate_climate_ready = next((row.get("value", "0") for row in alb2002_access_candidate_summary if row.get("metric") == "alb2002_access_candidate_climate_linkage_ready_rows"), "0")
    alb2002_access_candidate_decision = next((row.get("value", "") for row in alb2002_access_candidate_summary if row.get("metric") == "alb2002_access_candidate_current_decision"), "")
    add(
        rows,
        "evidence",
        "ALB_2002 household-level access candidate outcomes are constructed in temp while final outcome promotion stays blocked",
        status(
            counts["alb2002_access_candidate_household_outcomes"] == 3599
            and counts["alb2002_access_candidate_outcome_lineage"] == 8
            and counts["alb2002_access_candidate_outcome_audit"] == 13
            and counts["alb2002_access_candidate_outcome_summary"] > 0
            and file_ok(REPORT_DIR / "alb2002_access_candidate_outcome_audit.md")
            and alb2002_access_candidate_households == "3599"
            and alb2002_access_candidate_q01_need == "3247"
            and alb2002_access_candidate_person_need == "2202"
            and alb2002_access_candidate_q01_cost == "1623"
            and alb2002_access_candidate_any == "1861"
            and alb2002_access_candidate_cost == "1661"
            and alb2002_access_candidate_low_event == "2"
            and alb2002_access_candidate_promotion_ready == "0"
            and alb2002_access_candidate_recipe_ready == "0"
            and alb2002_access_candidate_sdg_ready == "0"
            and alb2002_access_candidate_climate_ready == "0"
            and alb2002_access_candidate_decision == "blocked_alb2002_access_candidate_not_promoted_due_denominator_skip_climate_gates"
        ),
        f"household_rows={counts['alb2002_access_candidate_household_outcomes']}; lineage_rows={counts['alb2002_access_candidate_outcome_lineage']}; audit_rows={counts['alb2002_access_candidate_outcome_audit']}; summary_rows={counts['alb2002_access_candidate_outcome_summary']}; q01_need_rows={alb2002_access_candidate_q01_need}; person_need_rows={alb2002_access_candidate_person_need}; q01_cost_rows={alb2002_access_candidate_q01_cost}; any_barrier_rows={alb2002_access_candidate_any}; cost_barrier_rows={alb2002_access_candidate_cost}; low_event_rows={alb2002_access_candidate_low_event}; outcome_promotion_ready={alb2002_access_candidate_promotion_ready}; recipe_ready={alb2002_access_candidate_recipe_ready}; sdg382_ready={alb2002_access_candidate_sdg_ready}; climate_ready={alb2002_access_candidate_climate_ready}; decision={alb2002_access_candidate_decision}",
        ""
        if counts["alb2002_access_candidate_household_outcomes"] == 3599
        and counts["alb2002_access_candidate_outcome_audit"] == 13
        and alb2002_access_candidate_promotion_ready == "0"
        and alb2002_access_candidate_climate_ready == "0"
        and alb2002_access_candidate_decision == "blocked_alb2002_access_candidate_not_promoted_due_denominator_skip_climate_gates"
        else "Run script/105_build_alb2002_access_candidate_outcomes.py after the access/need denominator policy audit; keep access rows in temp until denominator, skip-path, recipe, financial-alignment, and climate gates pass.",
    )
    alb2002_uhc_composite_summary = read_csv_dicts(RESULT_DIR / "alb2002_uhc_composite_candidate_summary.csv")
    alb2002_uhc_composite_households = next((row.get("value", "0") for row in alb2002_uhc_composite_summary if row.get("metric") == "alb2002_uhc_composite_candidate_household_rows"), "0")
    alb2002_uhc_composite_che10_or_access = next((row.get("value", "0") for row in alb2002_uhc_composite_summary if row.get("metric") == "alb2002_uhc_composite_candidate_che10_or_access_rows"), "0")
    alb2002_uhc_composite_che25_or_access = next((row.get("value", "0") for row in alb2002_uhc_composite_summary if row.get("metric") == "alb2002_uhc_composite_candidate_che25_or_access_rows"), "0")
    alb2002_uhc_composite_both_che10 = next((row.get("value", "0") for row in alb2002_uhc_composite_summary if row.get("metric") == "alb2002_uhc_composite_candidate_both_che10_access_rows"), "0")
    alb2002_uhc_composite_coping = next((row.get("value", "0") for row in alb2002_uhc_composite_summary if row.get("metric") == "alb2002_uhc_composite_candidate_coping_rows"), "0")
    alb2002_uhc_composite_low_event = next((row.get("value", "0") for row in alb2002_uhc_composite_summary if row.get("metric") == "alb2002_uhc_composite_candidate_low_event_rate_rows"), "0")
    alb2002_uhc_composite_promotion_ready = next((row.get("value", "0") for row in alb2002_uhc_composite_summary if row.get("metric") == "alb2002_uhc_composite_candidate_outcome_promotion_ready_rows"), "0")
    alb2002_uhc_composite_recipe_ready = next((row.get("value", "0") for row in alb2002_uhc_composite_summary if row.get("metric") == "alb2002_uhc_composite_candidate_recipe_ready_rows"), "0")
    alb2002_uhc_composite_sdg_ready = next((row.get("value", "0") for row in alb2002_uhc_composite_summary if row.get("metric") == "alb2002_uhc_composite_candidate_sdg382_ready_rows"), "0")
    alb2002_uhc_composite_climate_ready = next((row.get("value", "0") for row in alb2002_uhc_composite_summary if row.get("metric") == "alb2002_uhc_composite_candidate_climate_linkage_ready_rows"), "0")
    alb2002_uhc_composite_decision = next((row.get("value", "") for row in alb2002_uhc_composite_summary if row.get("metric") == "alb2002_uhc_composite_candidate_current_decision"), "")
    add(
        rows,
        "evidence",
        "ALB_2002 household-level composite UHC candidate outcomes are constructed in temp while final outcome promotion stays blocked",
        status(
            counts["alb2002_uhc_composite_candidate_outcomes"] == 3599
            and counts["alb2002_uhc_composite_candidate_lineage"] == 6
            and counts["alb2002_uhc_composite_candidate_audit"] == 10
            and counts["alb2002_uhc_composite_candidate_summary"] > 0
            and file_ok(REPORT_DIR / "alb2002_uhc_composite_candidate_audit.md")
            and alb2002_uhc_composite_households == "3599"
            and alb2002_uhc_composite_che10_or_access == "2004"
            and alb2002_uhc_composite_che25_or_access == "1889"
            and alb2002_uhc_composite_both_che10 == "681"
            and alb2002_uhc_composite_coping == "1476"
            and alb2002_uhc_composite_low_event == "1"
            and alb2002_uhc_composite_promotion_ready == "0"
            and alb2002_uhc_composite_recipe_ready == "0"
            and alb2002_uhc_composite_sdg_ready == "0"
            and alb2002_uhc_composite_climate_ready == "0"
            and alb2002_uhc_composite_decision == "blocked_alb2002_uhc_composite_candidate_not_promoted_due_outcome_recipe_climate_gates"
        ),
        f"household_rows={counts['alb2002_uhc_composite_candidate_outcomes']}; lineage_rows={counts['alb2002_uhc_composite_candidate_lineage']}; audit_rows={counts['alb2002_uhc_composite_candidate_audit']}; summary_rows={counts['alb2002_uhc_composite_candidate_summary']}; che10_or_access_rows={alb2002_uhc_composite_che10_or_access}; che25_or_access_rows={alb2002_uhc_composite_che25_or_access}; both_che10_access_rows={alb2002_uhc_composite_both_che10}; coping_rows={alb2002_uhc_composite_coping}; low_event_rows={alb2002_uhc_composite_low_event}; outcome_promotion_ready={alb2002_uhc_composite_promotion_ready}; recipe_ready={alb2002_uhc_composite_recipe_ready}; sdg382_ready={alb2002_uhc_composite_sdg_ready}; climate_ready={alb2002_uhc_composite_climate_ready}; decision={alb2002_uhc_composite_decision}",
        ""
        if counts["alb2002_uhc_composite_candidate_outcomes"] == 3599
        and counts["alb2002_uhc_composite_candidate_audit"] == 10
        and alb2002_uhc_composite_promotion_ready == "0"
        and alb2002_uhc_composite_climate_ready == "0"
        and alb2002_uhc_composite_decision == "blocked_alb2002_uhc_composite_candidate_not_promoted_due_outcome_recipe_climate_gates"
        else "Run script/106_build_alb2002_uhc_composite_candidate_outcomes.py after the CHE and access candidate builders; keep composite outcomes in temp until financial, access, recipe, SDG, benchmark, and climate gates pass.",
    )
    alb2002_analysis_candidate_summary = read_csv_dicts(RESULT_DIR / "alb2002_analysis_candidate_readiness_summary.csv")
    alb2002_analysis_rows = next((row.get("value", "0") for row in alb2002_analysis_candidate_summary if row.get("metric") == "alb2002_analysis_candidate_rows"), "0")
    alb2002_analysis_columns = next((row.get("value", "0") for row in alb2002_analysis_candidate_summary if row.get("metric") == "alb2002_analysis_candidate_columns"), "0")
    alb2002_analysis_complete_gates = next((row.get("value", "0") for row in alb2002_analysis_candidate_summary if row.get("metric") == "alb2002_analysis_candidate_complete_candidate_gates"), "0")
    alb2002_analysis_missing_gates = next((row.get("value", "0") for row in alb2002_analysis_candidate_summary if row.get("metric") == "alb2002_analysis_candidate_missing_gates"), "0")
    alb2002_analysis_blocked_gates = next((row.get("value", "0") for row in alb2002_analysis_candidate_summary if row.get("metric") == "alb2002_analysis_candidate_blocked_promotion_gates"), "0")
    alb2002_analysis_harmonized_ready = next((row.get("value", "0") for row in alb2002_analysis_candidate_summary if row.get("metric") == "alb2002_analysis_candidate_harmonized_ready_rows"), "0")
    alb2002_analysis_outcome_ready = next((row.get("value", "0") for row in alb2002_analysis_candidate_summary if row.get("metric") == "alb2002_analysis_candidate_outcome_promotion_ready_rows"), "0")
    alb2002_analysis_climate_ready = next((row.get("value", "0") for row in alb2002_analysis_candidate_summary if row.get("metric") == "alb2002_analysis_candidate_climate_linkage_ready_rows"), "0")
    alb2002_analysis_data_write_ready = next((row.get("value", "0") for row in alb2002_analysis_candidate_summary if row.get("metric") == "alb2002_analysis_candidate_data_write_ready_rows"), "0")
    alb2002_analysis_decision = next((row.get("value", "") for row in alb2002_analysis_candidate_summary if row.get("metric") == "alb2002_analysis_candidate_current_decision"), "")
    add(
        rows,
        "evidence",
        "ALB_2002 joined analysis-candidate dataset is constructed in temp with harmonized/outcome/climate promotion still blocked",
        status(
            counts["alb2002_analysis_candidate_dataset"] == 3599
            and counts["alb2002_analysis_candidate_lineage"] == 6
            and counts["alb2002_analysis_candidate_readiness_audit"] == 12
            and counts["alb2002_analysis_candidate_readiness_summary"] > 0
            and file_ok(REPORT_DIR / "alb2002_analysis_candidate_readiness_audit.md")
            and alb2002_analysis_rows == "3599"
            and alb2002_analysis_columns == "49"
            and alb2002_analysis_complete_gates == "9"
            and alb2002_analysis_missing_gates == "1"
            and alb2002_analysis_blocked_gates == "2"
            and alb2002_analysis_harmonized_ready == "0"
            and alb2002_analysis_outcome_ready == "0"
            and alb2002_analysis_climate_ready == "0"
            and alb2002_analysis_data_write_ready == "0"
            and alb2002_analysis_decision == "blocked_alb2002_analysis_candidate_not_promoted_due_recipe_outcome_climate_gates"
        ),
        f"candidate_rows={counts['alb2002_analysis_candidate_dataset']}; lineage_rows={counts['alb2002_analysis_candidate_lineage']}; audit_rows={counts['alb2002_analysis_candidate_readiness_audit']}; summary_rows={counts['alb2002_analysis_candidate_readiness_summary']}; columns={alb2002_analysis_columns}; complete_candidate_gates={alb2002_analysis_complete_gates}; missing_gates={alb2002_analysis_missing_gates}; blocked_promotion_gates={alb2002_analysis_blocked_gates}; harmonized_ready={alb2002_analysis_harmonized_ready}; outcome_ready={alb2002_analysis_outcome_ready}; climate_ready={alb2002_analysis_climate_ready}; data_write_ready={alb2002_analysis_data_write_ready}; decision={alb2002_analysis_decision}",
        ""
        if counts["alb2002_analysis_candidate_dataset"] == 3599
        and counts["alb2002_analysis_candidate_readiness_audit"] == 12
        and alb2002_analysis_data_write_ready == "0"
        and alb2002_analysis_decision == "blocked_alb2002_analysis_candidate_not_promoted_due_recipe_outcome_climate_gates"
        else "Run script/102_build_alb2002_analysis_candidate_dataset.py after the CHE candidate outcome builder; keep the joined dataset in temp until recipe, outcome, SDG, benchmark, and climate gates pass.",
    )
    alb2002_weight_design_summary = read_csv_dicts(RESULT_DIR / "alb2002_weight_design_evidence_summary.csv")
    alb2002_weight_design_flags = next((row.get("value", "0") for row in alb2002_weight_design_summary if row.get("metric") == "alb2002_weight_design_source_page_flag_rows"), "0")
    alb2002_weight_design_raw_rows = next((row.get("value", "0") for row in alb2002_weight_design_summary if row.get("metric") == "alb2002_weight_design_raw_weight_file_rows"), "0")
    alb2002_weight_design_positive = next((row.get("value", "0") for row in alb2002_weight_design_summary if row.get("metric") == "alb2002_weight_design_positive_weight_rows"), "0")
    alb2002_weight_design_key_match = next((row.get("value", "0") for row in alb2002_weight_design_summary if row.get("metric") == "alb2002_weight_design_candidate_key_match_rows"), "0")
    alb2002_weight_design_psu = next((row.get("value", "0") for row in alb2002_weight_design_summary if row.get("metric") == "alb2002_weight_design_distinct_psu_rows"), "0")
    alb2002_weight_design_strata = next((row.get("value", "0") for row in alb2002_weight_design_summary if row.get("metric") == "alb2002_weight_design_distinct_stratum_rows"), "0")
    alb2002_weight_design_inference_ready = next((row.get("value", "0") for row in alb2002_weight_design_summary if row.get("metric") == "alb2002_weight_design_weighted_inference_ready_rows"), "0")
    alb2002_weight_design_harmonized_ready = next((row.get("value", "0") for row in alb2002_weight_design_summary if row.get("metric") == "alb2002_weight_design_harmonized_promotion_ready_rows"), "0")
    alb2002_weight_design_decision = next((row.get("value", "") for row in alb2002_weight_design_summary if row.get("metric") == "alb2002_weight_design_current_decision"), "")
    add(
        rows,
        "evidence",
        "ALB_2002 weight/design evidence audit verifies readable household weights but keeps weighted inference fail-closed",
        status(
            counts["alb2002_weight_design_evidence_audit"] == 6
            and counts["alb2002_weight_design_evidence_summary"] > 0
            and file_ok(REPORT_DIR / "alb2002_weight_design_evidence_audit.md")
            and alb2002_weight_design_flags == "9"
            and alb2002_weight_design_raw_rows == "3599"
            and alb2002_weight_design_positive == "3599"
            and alb2002_weight_design_key_match == "3599"
            and alb2002_weight_design_psu == "450"
            and alb2002_weight_design_strata == "4"
            and alb2002_weight_design_inference_ready == "0"
            and alb2002_weight_design_harmonized_ready == "0"
            and alb2002_weight_design_decision == "blocked_alb2002_weight_design_semantics_not_promotion_ready"
        ),
        f"audit_rows={counts['alb2002_weight_design_evidence_audit']}; summary_rows={counts['alb2002_weight_design_evidence_summary']}; source_flags={alb2002_weight_design_flags}; raw_weight_rows={alb2002_weight_design_raw_rows}; positive_weights={alb2002_weight_design_positive}; key_matches={alb2002_weight_design_key_match}; distinct_psu={alb2002_weight_design_psu}; distinct_strata={alb2002_weight_design_strata}; weighted_inference_ready={alb2002_weight_design_inference_ready}; harmonized_ready={alb2002_weight_design_harmonized_ready}; decision={alb2002_weight_design_decision}",
        ""
        if counts["alb2002_weight_design_evidence_audit"] == 6
        and counts["alb2002_weight_design_evidence_summary"] > 0
        and alb2002_weight_design_positive == "3599"
        and alb2002_weight_design_key_match == "3599"
        and alb2002_weight_design_inference_ready == "0"
        and alb2002_weight_design_harmonized_ready == "0"
        and alb2002_weight_design_decision == "blocked_alb2002_weight_design_semantics_not_promotion_ready"
        else "Run script/100_audit_alb2002_weight_design_evidence.py and keep weighted inference blocked until design semantics and promotion gates are verified.",
    )
    alb2002_minimum_recipe_summary = read_csv_dicts(RESULT_DIR / "alb2002_minimum_recipe_promotion_summary.csv")
    alb2002_minimum_recipe_actions = next((row.get("value", "0") for row in alb2002_minimum_recipe_summary if row.get("metric") == "alb2002_minimum_recipe_promotion_action_rows"), "0")
    alb2002_minimum_recipe_gates = next((row.get("value", "0") for row in alb2002_minimum_recipe_summary if row.get("metric") == "alb2002_minimum_recipe_promotion_gate_rows"), "0")
    alb2002_minimum_recipe_blocked = next((row.get("value", "0") for row in alb2002_minimum_recipe_summary if row.get("metric") == "alb2002_minimum_recipe_promotion_blocked_gates"), "0")
    alb2002_minimum_recipe_candidate = next((row.get("value", "0") for row in alb2002_minimum_recipe_summary if row.get("metric") == "alb2002_minimum_recipe_promotion_candidate_gates"), "0")
    alb2002_minimum_recipe_weight_positive = next((row.get("value", "0") for row in alb2002_minimum_recipe_summary if row.get("metric") == "alb2002_minimum_recipe_promotion_weight_design_positive_weight_rows"), "0")
    alb2002_minimum_recipe_weight_key_match = next((row.get("value", "0") for row in alb2002_minimum_recipe_summary if row.get("metric") == "alb2002_minimum_recipe_promotion_weight_design_key_match_rows"), "0")
    alb2002_minimum_recipe_weighted_inference_ready = next((row.get("value", "0") for row in alb2002_minimum_recipe_summary if row.get("metric") == "alb2002_minimum_recipe_promotion_weight_design_weighted_inference_ready_rows"), "0")
    alb2002_minimum_recipe_harmonized_ready = next((row.get("value", "0") for row in alb2002_minimum_recipe_summary if row.get("metric") == "alb2002_minimum_recipe_promotion_harmonized_ready_rows"), "0")
    alb2002_minimum_recipe_outcome_ready = next((row.get("value", "0") for row in alb2002_minimum_recipe_summary if row.get("metric") == "alb2002_minimum_recipe_promotion_outcome_ready_rows"), "0")
    alb2002_minimum_recipe_sdg_ready = next((row.get("value", "0") for row in alb2002_minimum_recipe_summary if row.get("metric") == "alb2002_minimum_recipe_promotion_sdg382_ready_rows"), "0")
    alb2002_minimum_recipe_climate_ready = next((row.get("value", "0") for row in alb2002_minimum_recipe_summary if row.get("metric") == "alb2002_minimum_recipe_promotion_climate_linkage_ready_rows"), "0")
    alb2002_minimum_recipe_decision = next((row.get("value", "") for row in alb2002_minimum_recipe_summary if row.get("metric") == "alb2002_minimum_recipe_promotion_current_decision"), "")
    add(
        rows,
        "evidence",
        "ALB_2002 minimum recipe promotion packet maps the top-ranked temp candidate to explicit harmonization, outcome, SDG, and climate gates",
        status(
            counts["alb2002_minimum_recipe_promotion_action_queue"] > 0
            and counts["alb2002_minimum_recipe_promotion_gate_checklist"] > 0
            and counts["alb2002_minimum_recipe_promotion_summary"] > 0
            and alb2002_minimum_recipe_actions == "6"
            and alb2002_minimum_recipe_gates == "10"
            and int(float(alb2002_minimum_recipe_blocked or "0")) > 0
            and int(float(alb2002_minimum_recipe_candidate or "0")) > 0
            and alb2002_minimum_recipe_weight_positive == "3599"
            and alb2002_minimum_recipe_weight_key_match == "3599"
            and alb2002_minimum_recipe_weighted_inference_ready == "0"
            and alb2002_minimum_recipe_harmonized_ready == "0"
            and alb2002_minimum_recipe_outcome_ready == "0"
            and alb2002_minimum_recipe_sdg_ready == "0"
            and alb2002_minimum_recipe_climate_ready == "0"
            and alb2002_minimum_recipe_decision == "blocked_alb2002_minimum_recipe_not_ready_for_promotion"
        ),
        f"action_rows={counts['alb2002_minimum_recipe_promotion_action_queue']}; gate_rows={counts['alb2002_minimum_recipe_promotion_gate_checklist']}; summary_rows={counts['alb2002_minimum_recipe_promotion_summary']}; summary_actions={alb2002_minimum_recipe_actions}; summary_gates={alb2002_minimum_recipe_gates}; blocked_gates={alb2002_minimum_recipe_blocked}; candidate_gates={alb2002_minimum_recipe_candidate}; weight_positive={alb2002_minimum_recipe_weight_positive}; weight_key_match={alb2002_minimum_recipe_weight_key_match}; weighted_inference_ready={alb2002_minimum_recipe_weighted_inference_ready}; harmonized_ready={alb2002_minimum_recipe_harmonized_ready}; outcome_ready={alb2002_minimum_recipe_outcome_ready}; sdg382_ready={alb2002_minimum_recipe_sdg_ready}; climate_ready={alb2002_minimum_recipe_climate_ready}; decision={alb2002_minimum_recipe_decision}",
        ""
        if counts["alb2002_minimum_recipe_promotion_action_queue"] > 0
        and counts["alb2002_minimum_recipe_promotion_gate_checklist"] > 0
        and counts["alb2002_minimum_recipe_promotion_summary"] > 0
        and alb2002_minimum_recipe_weight_positive == "3599"
        and alb2002_minimum_recipe_weight_key_match == "3599"
        and alb2002_minimum_recipe_weighted_inference_ready == "0"
        and alb2002_minimum_recipe_harmonized_ready == "0"
        and alb2002_minimum_recipe_outcome_ready == "0"
        and alb2002_minimum_recipe_sdg_ready == "0"
        and alb2002_minimum_recipe_climate_ready == "0"
        and alb2002_minimum_recipe_decision == "blocked_alb2002_minimum_recipe_not_ready_for_promotion"
        else "Run script/90_build_alb2002_minimum_recipe_promotion_packet.py and keep ALB_2002 in temp-only status until minimum recipe, SDG, and climate gates pass.",
    )
    alb2002_crosswalk_summary = read_csv_dicts(RESULT_DIR / "alb2002_district_climate_crosswalk_summary.csv")
    alb2002_crosswalk_ready = next((row.get("value", "0") for row in alb2002_crosswalk_summary if row.get("metric") == "alb2002_district_crosswalk_template_ready_rows"), "0")
    alb2002_climate_ready = next((row.get("value", "0") for row in alb2002_crosswalk_summary if row.get("metric") == "alb2002_climate_linkage_ready_rows"), "0")
    alb2002_crosswalk_decision = next((row.get("value", "") for row in alb2002_crosswalk_summary if row.get("metric") == "alb2002_district_crosswalk_current_decision"), "")
    alb2002_crosswalk_source_reachable = next((row.get("value", "0") for row in alb2002_crosswalk_summary if row.get("metric") == "alb2002_district_crosswalk_boundary_source_reachable_rows"), "0")
    add(
        rows,
        "evidence",
        "ALB_2002 district climate-crosswalk audit builds a temp-only admin template and keeps climate linkage blocked",
        status(
            counts["alb2002_district_climate_crosswalk_template"] > 0
            and counts["alb2002_district_boundary_source_probe"] > 0
            and counts["alb2002_district_climate_crosswalk_summary"] > 0
            and alb2002_crosswalk_ready == "0"
            and alb2002_climate_ready == "0"
            and alb2002_crosswalk_decision == "blocked_boundary_crosswalk_not_verified_no_gps"
        ),
        f"template_rows={counts['alb2002_district_climate_crosswalk_template']}; source_probe_rows={counts['alb2002_district_boundary_source_probe']}; summary_rows={counts['alb2002_district_climate_crosswalk_summary']}; source_reachable_rows={alb2002_crosswalk_source_reachable}; template_ready_rows={alb2002_crosswalk_ready}; climate_linkage_ready_rows={alb2002_climate_ready}; decision={alb2002_crosswalk_decision}",
        ""
        if counts["alb2002_district_climate_crosswalk_template"] > 0
        and counts["alb2002_district_boundary_source_probe"] > 0
        and counts["alb2002_district_climate_crosswalk_summary"] > 0
        and alb2002_crosswalk_ready == "0"
        and alb2002_climate_ready == "0"
        and alb2002_crosswalk_decision == "blocked_boundary_crosswalk_not_verified_no_gps"
        else "Run script/56_audit_alb2002_district_climate_crosswalk.py and keep climate linkage blocked until district boundaries/crosswalks pass.",
    )
    alb2002_boundary_match_summary = read_csv_dicts(RESULT_DIR / "alb2002_boundary_name_match_summary.csv")
    alb2002_boundary_exact = next((row.get("value", "0") for row in alb2002_boundary_match_summary if row.get("metric") == "alb2002_boundary_name_match_exact_rows"), "0")
    alb2002_boundary_repaired = next((row.get("value", "0") for row in alb2002_boundary_match_summary if row.get("metric") == "alb2002_boundary_name_match_euro_repaired_rows"), "0")
    alb2002_boundary_unmatched = next((row.get("value", "0") for row in alb2002_boundary_match_summary if row.get("metric") == "alb2002_boundary_name_match_unmatched_survey_rows"), "0")
    alb2002_boundary_duplicate_keys = next((row.get("value", "0") for row in alb2002_boundary_match_summary if row.get("metric") == "alb2002_boundary_name_match_duplicate_boundary_name_keys"), "0")
    alb2002_boundary_historical_ready = next((row.get("value", "0") for row in alb2002_boundary_match_summary if row.get("metric") == "alb2002_boundary_name_match_historical_year_ready_rows"), "0")
    alb2002_boundary_climate_ready = next((row.get("value", "0") for row in alb2002_boundary_match_summary if row.get("metric") == "alb2002_boundary_name_match_climate_linkage_ready_rows"), "0")
    alb2002_boundary_decision = next((row.get("value", "") for row in alb2002_boundary_match_summary if row.get("metric") == "alb2002_boundary_name_match_current_decision"), "")
    add(
        rows,
        "evidence",
        "ALB_2002 public boundary name-match audit compares current ADM2 names to survey district labels while keeping historical/climate promotion blocked",
        status(
            counts["alb2002_boundary_name_match_audit"] > 0
            and counts["alb2002_boundary_geojson_inventory"] > 0
            and counts["alb2002_boundary_name_match_summary"] > 0
            and alb2002_boundary_historical_ready == "0"
            and alb2002_boundary_climate_ready == "0"
            and alb2002_boundary_decision == "blocked_current_boundary_name_match_incomplete_historical_crosswalk_no_gps"
        ),
        f"match_rows={counts['alb2002_boundary_name_match_audit']}; boundary_features={counts['alb2002_boundary_geojson_inventory']}; summary_rows={counts['alb2002_boundary_name_match_summary']}; exact_matches={alb2002_boundary_exact}; repaired_matches={alb2002_boundary_repaired}; unmatched_survey_rows={alb2002_boundary_unmatched}; duplicate_boundary_keys={alb2002_boundary_duplicate_keys}; historical_ready={alb2002_boundary_historical_ready}; climate_ready={alb2002_boundary_climate_ready}; decision={alb2002_boundary_decision}",
        ""
        if counts["alb2002_boundary_name_match_audit"] > 0
        and counts["alb2002_boundary_geojson_inventory"] > 0
        and counts["alb2002_boundary_name_match_summary"] > 0
        and alb2002_boundary_historical_ready == "0"
        and alb2002_boundary_climate_ready == "0"
        and alb2002_boundary_decision == "blocked_current_boundary_name_match_incomplete_historical_crosswalk_no_gps"
        else "Run script/64_audit_alb2002_boundary_name_match.py and keep ALB_2002 climate linkage blocked until boundary names, historical crosswalk, polygons, and no-GPS aggregation pass.",
    )
    alb2002_source_alt_summary = read_csv_dicts(RESULT_DIR / "alb2002_boundary_source_alternative_summary.csv")
    alb2002_source_alt_rows = next((row.get("value", "0") for row in alb2002_source_alt_summary if row.get("metric") == "alb2002_boundary_source_alternative_rows"), "0")
    alb2002_source_alt_historical_ready = next((row.get("value", "0") for row in alb2002_source_alt_summary if row.get("metric") == "alb2002_boundary_source_alternative_historical_2002_boundary_ready_rows"), "0")
    alb2002_source_alt_climate_ready = next((row.get("value", "0") for row in alb2002_source_alt_summary if row.get("metric") == "alb2002_boundary_source_alternative_climate_linkage_ready_rows"), "0")
    alb2002_source_alt_decision = next((row.get("value", "") for row in alb2002_source_alt_summary if row.get("metric") == "alb2002_boundary_source_alternative_current_decision"), "")
    add(
        rows,
        "evidence",
        "ALB_2002 boundary source-alternatives audit reviews public/current/historical leads while keeping climate promotion blocked",
        status(
            counts["alb2002_boundary_source_alternative_audit"] > 0
            and counts["alb2002_boundary_source_alternative_summary"] > 0
            and alb2002_source_alt_historical_ready == "0"
            and alb2002_source_alt_climate_ready == "0"
            and alb2002_source_alt_decision == "blocked_no_public_2002_district_boundary_source_verified"
        ),
        f"audit_rows={counts['alb2002_boundary_source_alternative_audit']}; summary_rows={counts['alb2002_boundary_source_alternative_summary']}; source_rows={alb2002_source_alt_rows}; historical_ready={alb2002_source_alt_historical_ready}; climate_ready={alb2002_source_alt_climate_ready}; decision={alb2002_source_alt_decision}",
        ""
        if counts["alb2002_boundary_source_alternative_audit"] > 0
        and counts["alb2002_boundary_source_alternative_summary"] > 0
        and alb2002_source_alt_historical_ready == "0"
        and alb2002_source_alt_climate_ready == "0"
        and alb2002_source_alt_decision == "blocked_no_public_2002_district_boundary_source_verified"
        else "Run script/69_audit_alb2002_boundary_source_alternatives.py and keep ALB_2002 climate linkage blocked until a public 2001/2002 district/GPS boundary source is verified.",
    )
    alb2002_resource_summary = read_csv_dicts(RESULT_DIR / "alb2002_boundary_source_resource_search_summary.csv")
    alb2002_resource_candidate_rows = next((row.get("value", "0") for row in alb2002_resource_summary if row.get("metric") == "alb2002_boundary_resource_search_candidate_rows"), "0")
    alb2002_resource_complete_coverage = next((row.get("value", "0") for row in alb2002_resource_summary if row.get("metric") == "alb2002_boundary_resource_search_complete_name_coverage_rows"), "0")
    alb2002_resource_exact_unit_count = next((row.get("value", "0") for row in alb2002_resource_summary if row.get("metric") == "alb2002_boundary_resource_search_exact_unit_count_rows"), "0")
    alb2002_resource_historical_ready = next((row.get("value", "0") for row in alb2002_resource_summary if row.get("metric") == "alb2002_boundary_resource_search_2002_historical_ready_rows"), "0")
    alb2002_resource_climate_ready = next((row.get("value", "0") for row in alb2002_resource_summary if row.get("metric") == "alb2002_boundary_resource_search_climate_linkage_ready_rows"), "0")
    alb2002_resource_best_candidate = next((row.get("value", "") for row in alb2002_resource_summary if row.get("metric") == "alb2002_boundary_resource_search_best_candidate_id"), "")
    alb2002_resource_decision = next((row.get("value", "") for row in alb2002_resource_summary if row.get("metric") == "alb2002_boundary_resource_search_current_decision"), "")
    add(
        rows,
        "evidence",
        "ALB_2002 boundary resource search parses public boundary/gazetteer resources while keeping historical and climate promotion blocked",
        status(
            counts["alb2002_boundary_source_resource_search_audit"] > 0
            and counts["alb2002_boundary_source_resource_search_summary"] > 0
            and alb2002_resource_historical_ready == "0"
            and alb2002_resource_climate_ready == "0"
            and alb2002_resource_decision == "blocked_alb2002_boundary_resource_search_no_historical_climate_ready_source"
        ),
        f"audit_rows={counts['alb2002_boundary_source_resource_search_audit']}; summary_rows={counts['alb2002_boundary_source_resource_search_summary']}; candidate_rows={alb2002_resource_candidate_rows}; complete_name_coverage_rows={alb2002_resource_complete_coverage}; exact_unit_count_rows={alb2002_resource_exact_unit_count}; best_candidate={alb2002_resource_best_candidate}; historical_ready={alb2002_resource_historical_ready}; climate_ready={alb2002_resource_climate_ready}; decision={alb2002_resource_decision}",
        ""
        if counts["alb2002_boundary_source_resource_search_audit"] > 0
        and counts["alb2002_boundary_source_resource_search_summary"] > 0
        and alb2002_resource_historical_ready == "0"
        and alb2002_resource_climate_ready == "0"
        and alb2002_resource_decision == "blocked_alb2002_boundary_resource_search_no_historical_climate_ready_source"
        else "Run script/79_audit_alb2002_boundary_source_resource_search.py and keep ALB_2002 climate linkage blocked until the candidate boundary resource is provenance/vintage/crosswalk verified.",
    )
    alb2002_geometry_summary = read_csv_dicts(RESULT_DIR / "alb2002_boundary_geometry_provenance_summary.csv")
    alb2002_geometry_features = next((row.get("value", "0") for row in alb2002_geometry_summary if row.get("metric") == "alb2002_boundary_geometry_feature_rows"), "0")
    alb2002_geometry_year = next((row.get("value", "") for row in alb2002_geometry_summary if row.get("metric") == "alb2002_boundary_geometry_metadata_boundary_year"), "")
    alb2002_geometry_year_match = next((row.get("value", "0") for row in alb2002_geometry_summary if row.get("metric") == "alb2002_boundary_geometry_boundary_year_matches_2002_rows"), "0")
    alb2002_geometry_structure_ok = next((row.get("value", "0") for row in alb2002_geometry_summary if row.get("metric") == "alb2002_boundary_geometry_coordinate_structure_ok_rows"), "0")
    alb2002_geometry_historical_ready = next((row.get("value", "0") for row in alb2002_geometry_summary if row.get("metric") == "alb2002_boundary_geometry_historical_2002_boundary_ready_rows"), "0")
    alb2002_geometry_climate_ready = next((row.get("value", "0") for row in alb2002_geometry_summary if row.get("metric") == "alb2002_boundary_geometry_climate_linkage_ready_rows"), "0")
    alb2002_geometry_decision = next((row.get("value", "") for row in alb2002_geometry_summary if row.get("metric") == "alb2002_boundary_geometry_current_decision"), "")
    add(
        rows,
        "evidence",
        "ALB_2002 boundary geometry/provenance audit parses the best boundary lead while blocking promotion on 2013 metadata vintage",
        status(
            counts["alb2002_boundary_geometry_provenance_audit"] > 0
            and counts["alb2002_boundary_metadata_provenance_probe"] > 0
            and counts["alb2002_boundary_geometry_provenance_summary"] > 0
            and alb2002_geometry_year == "2013"
            and alb2002_geometry_year_match == "0"
            and alb2002_geometry_historical_ready == "0"
            and alb2002_geometry_climate_ready == "0"
            and alb2002_geometry_decision == "blocked_geoboundaries_2_0_1_boundary_year_2013_not_verified_2002"
        ),
        f"geometry_rows={counts['alb2002_boundary_geometry_provenance_audit']}; metadata_rows={counts['alb2002_boundary_metadata_provenance_probe']}; summary_rows={counts['alb2002_boundary_geometry_provenance_summary']}; features={alb2002_geometry_features}; coordinate_structure_ok={alb2002_geometry_structure_ok}; boundary_year={alb2002_geometry_year}; boundary_year_matches_2002={alb2002_geometry_year_match}; historical_ready={alb2002_geometry_historical_ready}; climate_ready={alb2002_geometry_climate_ready}; decision={alb2002_geometry_decision}",
        ""
        if counts["alb2002_boundary_geometry_provenance_audit"] > 0
        and counts["alb2002_boundary_metadata_provenance_probe"] > 0
        and counts["alb2002_boundary_geometry_provenance_summary"] > 0
        and alb2002_geometry_year == "2013"
        and alb2002_geometry_year_match == "0"
        and alb2002_geometry_historical_ready == "0"
        and alb2002_geometry_climate_ready == "0"
        and alb2002_geometry_decision == "blocked_geoboundaries_2_0_1_boundary_year_2013_not_verified_2002"
        else "Run script/80_audit_alb2002_boundary_geometry_provenance.py and keep ALB_2002 climate linkage blocked until boundary vintage, topology, official historical definitions, and raw district-code crosswalks are verified.",
    )
    alb2002_climate_centroid_summary = read_csv_dicts(RESULT_DIR / "alb2002_climate_centroid_exposure_summary.csv")
    alb2002_climate_centroid_inputs = next((row.get("value", "0") for row in alb2002_climate_centroid_summary if row.get("metric") == "alb2002_climate_centroid_input_rows"), "0")
    alb2002_climate_centroid_districts = next((row.get("value", "0") for row in alb2002_climate_centroid_summary if row.get("metric") == "alb2002_climate_centroid_distinct_district_rows"), "0")
    alb2002_climate_centroid_households = next((row.get("value", "0") for row in alb2002_climate_centroid_summary if row.get("metric") == "alb2002_climate_centroid_household_rows_covered"), "0")
    alb2002_climate_centroid_exposures = next((row.get("value", "0") for row in alb2002_climate_centroid_summary if row.get("metric") == "alb2002_climate_centroid_exposure_rows"), "0")
    alb2002_climate_centroid_api_rows = next((row.get("value", "0") for row in alb2002_climate_centroid_summary if row.get("metric") == "alb2002_climate_centroid_nasa_api_rows"), "0")
    alb2002_climate_centroid_api_failed = next((row.get("value", "0") for row in alb2002_climate_centroid_summary if row.get("metric") == "alb2002_climate_centroid_nasa_failed_rows"), "0")
    alb2002_climate_centroid_precip = next((row.get("value", "0") for row in alb2002_climate_centroid_summary if row.get("metric") == "alb2002_climate_centroid_precip_nonmissing_rows"), "0")
    alb2002_climate_centroid_temp = next((row.get("value", "0") for row in alb2002_climate_centroid_summary if row.get("metric") == "alb2002_climate_centroid_temp_nonmissing_rows"), "0")
    alb2002_climate_centroid_boundary_year = next((row.get("value", "0") for row in alb2002_climate_centroid_summary if row.get("metric") == "alb2002_climate_centroid_boundary_year"), "0")
    alb2002_climate_centroid_climate_ready = next((row.get("value", "0") for row in alb2002_climate_centroid_summary if row.get("metric") == "alb2002_climate_centroid_climate_linkage_ready_rows"), "0")
    alb2002_climate_centroid_data_write_ready = next((row.get("value", "0") for row in alb2002_climate_centroid_summary if row.get("metric") == "alb2002_climate_centroid_data_write_ready_rows"), "0")
    alb2002_climate_centroid_decision = next((row.get("value", "") for row in alb2002_climate_centroid_summary if row.get("metric") == "alb2002_climate_centroid_current_decision"), "")
    add(
        rows,
        "evidence",
        "ALB_2002 climate centroid exposure stress test computes temp-only NASA POWER window summaries while keeping climate promotion blocked",
        status(
            counts["alb2002_climate_centroid_exposure_input"] == 96
            and counts["alb2002_climate_centroid_exposure_candidates"] == 384
            and counts["alb2002_climate_centroid_nasa_api_manifest"] == 36
            and counts["alb2002_climate_centroid_exposure_audit"] == 5
            and counts["alb2002_climate_centroid_exposure_summary"] > 0
            and file_ok(REPORT_DIR / "alb2002_climate_centroid_exposure_audit.md")
            and alb2002_climate_centroid_inputs == "96"
            and alb2002_climate_centroid_districts == "36"
            and alb2002_climate_centroid_households == "3599"
            and alb2002_climate_centroid_exposures == "384"
            and alb2002_climate_centroid_api_rows == "36"
            and alb2002_climate_centroid_api_failed == "0"
            and alb2002_climate_centroid_precip == "384"
            and alb2002_climate_centroid_temp == "384"
            and alb2002_climate_centroid_boundary_year == "2013"
            and alb2002_climate_centroid_climate_ready == "0"
            and alb2002_climate_centroid_data_write_ready == "0"
            and alb2002_climate_centroid_decision == "blocked_alb2002_climate_centroid_exposures_not_promoted_due_boundary_vintage_source_and_baseline_gates"
        ),
        f"input_rows={counts['alb2002_climate_centroid_exposure_input']}; exposure_rows={counts['alb2002_climate_centroid_exposure_candidates']}; api_manifest_rows={counts['alb2002_climate_centroid_nasa_api_manifest']}; audit_rows={counts['alb2002_climate_centroid_exposure_audit']}; summary_rows={counts['alb2002_climate_centroid_exposure_summary']}; summary_inputs={alb2002_climate_centroid_inputs}; districts={alb2002_climate_centroid_districts}; households={alb2002_climate_centroid_households}; summary_exposures={alb2002_climate_centroid_exposures}; api_rows={alb2002_climate_centroid_api_rows}; api_failed={alb2002_climate_centroid_api_failed}; precip_nonmissing={alb2002_climate_centroid_precip}; temp_nonmissing={alb2002_climate_centroid_temp}; boundary_year={alb2002_climate_centroid_boundary_year}; climate_ready={alb2002_climate_centroid_climate_ready}; data_write_ready={alb2002_climate_centroid_data_write_ready}; decision={alb2002_climate_centroid_decision}",
        ""
        if counts["alb2002_climate_centroid_exposure_input"] == 96
        and counts["alb2002_climate_centroid_exposure_candidates"] == 384
        and counts["alb2002_climate_centroid_nasa_api_manifest"] == 36
        and counts["alb2002_climate_centroid_exposure_audit"] == 5
        and alb2002_climate_centroid_api_failed == "0"
        and alb2002_climate_centroid_climate_ready == "0"
        and alb2002_climate_centroid_data_write_ready == "0"
        and alb2002_climate_centroid_decision == "blocked_alb2002_climate_centroid_exposures_not_promoted_due_boundary_vintage_source_and_baseline_gates"
        else "Run script/103_build_alb2002_climate_centroid_exposure_candidates.py and keep outputs in temp/ until verified historical geography, primary climate sources, and baselines are accepted.",
    )
    alb2002_climate_shock_summary = read_csv_dicts(RESULT_DIR / "alb2002_climate_shock_candidate_summary.csv")
    alb2002_climate_shock_rows = next((row.get("value", "0") for row in alb2002_climate_shock_summary if row.get("metric") == "alb2002_climate_shock_candidate_exposure_rows"), "0")
    alb2002_climate_shock_source_rows = next((row.get("value", "0") for row in alb2002_climate_shock_summary if row.get("metric") == "alb2002_climate_shock_candidate_source_centroid_rows"), "0")
    alb2002_climate_shock_lineage_rows = next((row.get("value", "0") for row in alb2002_climate_shock_summary if row.get("metric") == "alb2002_climate_shock_candidate_lineage_rows"), "0")
    alb2002_climate_shock_audit_rows = next((row.get("value", "0") for row in alb2002_climate_shock_summary if row.get("metric") == "alb2002_climate_shock_candidate_audit_rows"), "0")
    alb2002_climate_shock_reference_groups = next((row.get("value", "0") for row in alb2002_climate_shock_summary if row.get("metric") == "alb2002_climate_shock_candidate_reference_group_rows"), "0")
    alb2002_climate_shock_min_group = next((row.get("value", "0") for row in alb2002_climate_shock_summary if row.get("metric") == "alb2002_climate_shock_candidate_min_reference_group_size"), "0")
    alb2002_climate_shock_precip_z = next((row.get("value", "0") for row in alb2002_climate_shock_summary if row.get("metric") == "alb2002_climate_shock_candidate_precip_z_nonmissing_rows"), "0")
    alb2002_climate_shock_temp_z = next((row.get("value", "0") for row in alb2002_climate_shock_summary if row.get("metric") == "alb2002_climate_shock_candidate_temp_z_nonmissing_rows"), "0")
    alb2002_climate_shock_low_rain = next((row.get("value", "0") for row in alb2002_climate_shock_summary if row.get("metric") == "alb2002_climate_shock_candidate_low_rain_rows"), "0")
    alb2002_climate_shock_severe_low_rain = next((row.get("value", "0") for row in alb2002_climate_shock_summary if row.get("metric") == "alb2002_climate_shock_candidate_severe_low_rain_rows"), "0")
    alb2002_climate_shock_extreme_wet = next((row.get("value", "0") for row in alb2002_climate_shock_summary if row.get("metric") == "alb2002_climate_shock_candidate_extreme_wet_rows"), "0")
    alb2002_climate_shock_heat = next((row.get("value", "0") for row in alb2002_climate_shock_summary if row.get("metric") == "alb2002_climate_shock_candidate_heat_rows"), "0")
    alb2002_climate_shock_extreme_heat = next((row.get("value", "0") for row in alb2002_climate_shock_summary if row.get("metric") == "alb2002_climate_shock_candidate_extreme_heat_rows"), "0")
    alb2002_climate_shock_cold = next((row.get("value", "0") for row in alb2002_climate_shock_summary if row.get("metric") == "alb2002_climate_shock_candidate_cold_rows"), "0")
    alb2002_climate_shock_combined = next((row.get("value", "0") for row in alb2002_climate_shock_summary if row.get("metric") == "alb2002_climate_shock_candidate_combined_stress_rows"), "0")
    alb2002_climate_shock_climate_ready = next((row.get("value", "0") for row in alb2002_climate_shock_summary if row.get("metric") == "alb2002_climate_shock_candidate_climate_linkage_ready_rows"), "0")
    alb2002_climate_shock_data_write = next((row.get("value", "0") for row in alb2002_climate_shock_summary if row.get("metric") == "alb2002_climate_shock_candidate_data_write_ready_rows"), "0")
    alb2002_climate_shock_decision = next((row.get("value", "") for row in alb2002_climate_shock_summary if row.get("metric") == "alb2002_climate_shock_candidate_current_decision"), "")
    add(
        rows,
        "evidence",
        "ALB_2002 climate shock candidate audit derives within-candidate diagnostic z-scores while keeping primary climate promotion blocked",
        status(
            counts["alb2002_climate_shock_candidate_exposures"] == 384
            and counts["alb2002_climate_shock_candidate_lineage"] == 7
            and counts["alb2002_climate_shock_candidate_audit"] == 8
            and counts["alb2002_climate_shock_candidate_summary"] > 0
            and file_ok(REPORT_DIR / "alb2002_climate_shock_candidate_audit.md")
            and alb2002_climate_shock_rows == "384"
            and alb2002_climate_shock_source_rows == "384"
            and alb2002_climate_shock_lineage_rows == "7"
            and alb2002_climate_shock_audit_rows == "8"
            and alb2002_climate_shock_reference_groups == "16"
            and alb2002_climate_shock_min_group == "3"
            and alb2002_climate_shock_precip_z == "384"
            and alb2002_climate_shock_temp_z == "384"
            and alb2002_climate_shock_low_rain == "37"
            and alb2002_climate_shock_severe_low_rain == "0"
            and alb2002_climate_shock_extreme_wet == "44"
            and alb2002_climate_shock_heat == "66"
            and alb2002_climate_shock_extreme_heat == "29"
            and alb2002_climate_shock_cold == "13"
            and alb2002_climate_shock_combined == "73"
            and alb2002_climate_shock_climate_ready == "0"
            and alb2002_climate_shock_data_write == "0"
            and alb2002_climate_shock_decision == "blocked_alb2002_climate_shock_candidate_not_promoted_due_geography_baseline_primary_source_gates"
        ),
        f"shock_rows={counts['alb2002_climate_shock_candidate_exposures']}; lineage_rows={counts['alb2002_climate_shock_candidate_lineage']}; audit_rows={counts['alb2002_climate_shock_candidate_audit']}; summary_rows={counts['alb2002_climate_shock_candidate_summary']}; summary_shock_rows={alb2002_climate_shock_rows}; source_centroid_rows={alb2002_climate_shock_source_rows}; reference_groups={alb2002_climate_shock_reference_groups}; min_group={alb2002_climate_shock_min_group}; precip_z={alb2002_climate_shock_precip_z}; temp_z={alb2002_climate_shock_temp_z}; low_rain={alb2002_climate_shock_low_rain}; severe_low_rain={alb2002_climate_shock_severe_low_rain}; extreme_wet={alb2002_climate_shock_extreme_wet}; heat={alb2002_climate_shock_heat}; extreme_heat={alb2002_climate_shock_extreme_heat}; cold={alb2002_climate_shock_cold}; combined={alb2002_climate_shock_combined}; climate_ready={alb2002_climate_shock_climate_ready}; data_write_ready={alb2002_climate_shock_data_write}; decision={alb2002_climate_shock_decision}",
        ""
        if counts["alb2002_climate_shock_candidate_exposures"] == 384
        and counts["alb2002_climate_shock_candidate_audit"] == 8
        and alb2002_climate_shock_precip_z == "384"
        and alb2002_climate_shock_temp_z == "384"
        and alb2002_climate_shock_climate_ready == "0"
        and alb2002_climate_shock_data_write == "0"
        and alb2002_climate_shock_decision == "blocked_alb2002_climate_shock_candidate_not_promoted_due_geography_baseline_primary_source_gates"
        else "Run script/107_build_alb2002_climate_shock_candidate_audit.py after the centroid exposure stress test; keep shock diagnostics temp-only until geography, primary climate sources, and historical baselines pass.",
    )
    alb2002_linked_summary = read_csv_dicts(RESULT_DIR / "alb2002_climate_outcome_linked_candidate_summary.csv")
    alb2002_linked_rows = next((row.get("value", "0") for row in alb2002_linked_summary if row.get("metric") == "alb2002_climate_outcome_linked_candidate_rows"), "0")
    alb2002_linked_households = next((row.get("value", "0") for row in alb2002_linked_summary if row.get("metric") == "alb2002_climate_outcome_linked_candidate_household_rows"), "0")
    alb2002_linked_windows = next((row.get("value", "0") for row in alb2002_linked_summary if row.get("metric") == "alb2002_climate_outcome_linked_candidate_window_rows"), "0")
    alb2002_linked_district_months = next((row.get("value", "0") for row in alb2002_linked_summary if row.get("metric") == "alb2002_climate_outcome_linked_candidate_district_month_cells"), "0")
    alb2002_linked_lineage_rows = next((row.get("value", "0") for row in alb2002_linked_summary if row.get("metric") == "alb2002_climate_outcome_linked_candidate_lineage_rows"), "0")
    alb2002_linked_audit_rows = next((row.get("value", "0") for row in alb2002_linked_summary if row.get("metric") == "alb2002_climate_outcome_linked_candidate_audit_rows"), "0")
    alb2002_linked_source_analysis_rows = next((row.get("value", "0") for row in alb2002_linked_summary if row.get("metric") == "alb2002_climate_outcome_linked_candidate_source_analysis_rows"), "0")
    alb2002_linked_source_uhc_rows = next((row.get("value", "0") for row in alb2002_linked_summary if row.get("metric") == "alb2002_climate_outcome_linked_candidate_source_uhc_rows"), "0")
    alb2002_linked_source_shock_rows = next((row.get("value", "0") for row in alb2002_linked_summary if row.get("metric") == "alb2002_climate_outcome_linked_candidate_source_shock_rows"), "0")
    alb2002_linked_expected_rows = next((row.get("value", "0") for row in alb2002_linked_summary if row.get("metric") == "alb2002_climate_outcome_linked_candidate_expected_rows"), "0")
    alb2002_linked_unmatched = next((row.get("value", "0") for row in alb2002_linked_summary if row.get("metric") == "alb2002_climate_outcome_linked_candidate_unmatched_rows"), "0")
    alb2002_linked_precip_z = next((row.get("value", "0") for row in alb2002_linked_summary if row.get("metric") == "alb2002_climate_outcome_linked_candidate_precip_z_rows"), "0")
    alb2002_linked_temp_z = next((row.get("value", "0") for row in alb2002_linked_summary if row.get("metric") == "alb2002_climate_outcome_linked_candidate_temp_z_rows"), "0")
    alb2002_linked_combined = next((row.get("value", "0") for row in alb2002_linked_summary if row.get("metric") == "alb2002_climate_outcome_linked_candidate_combined_stress_rows"), "0")
    alb2002_linked_che10_or_access = next((row.get("value", "0") for row in alb2002_linked_summary if row.get("metric") == "alb2002_climate_outcome_linked_candidate_che10_or_access_rows"), "0")
    alb2002_linked_che25_or_access = next((row.get("value", "0") for row in alb2002_linked_summary if row.get("metric") == "alb2002_climate_outcome_linked_candidate_che25_or_access_rows"), "0")
    alb2002_linked_both = next((row.get("value", "0") for row in alb2002_linked_summary if row.get("metric") == "alb2002_climate_outcome_linked_candidate_both_che10_access_rows"), "0")
    alb2002_linked_coping = next((row.get("value", "0") for row in alb2002_linked_summary if row.get("metric") == "alb2002_climate_outcome_linked_candidate_coping_rows"), "0")
    alb2002_linked_climate_ready = next((row.get("value", "0") for row in alb2002_linked_summary if row.get("metric") == "alb2002_climate_outcome_linked_candidate_climate_linkage_ready_rows"), "0")
    alb2002_linked_outcome_ready = next((row.get("value", "0") for row in alb2002_linked_summary if row.get("metric") == "alb2002_climate_outcome_linked_candidate_outcome_promotion_ready_rows"), "0")
    alb2002_linked_harmonized_ready = next((row.get("value", "0") for row in alb2002_linked_summary if row.get("metric") == "alb2002_climate_outcome_linked_candidate_harmonized_recipe_ready_rows"), "0")
    alb2002_linked_data_write = next((row.get("value", "0") for row in alb2002_linked_summary if row.get("metric") == "alb2002_climate_outcome_linked_candidate_data_write_ready_rows"), "0")
    alb2002_linked_decision = next((row.get("value", "") for row in alb2002_linked_summary if row.get("metric") == "alb2002_climate_outcome_linked_candidate_current_decision"), "")
    add(
        rows,
        "evidence",
        "ALB_2002 climate/outcome linked candidate mechanically joins household UHC candidates to diagnostic climate windows while keeping all promotion gates blocked",
        status(
            counts["alb2002_climate_outcome_linked_candidate"] == 14396
            and counts["alb2002_climate_outcome_linked_candidate_lineage"] == 7
            and counts["alb2002_climate_outcome_linked_candidate_audit"] == 7
            and counts["alb2002_climate_outcome_linked_candidate_summary"] > 0
            and file_ok(REPORT_DIR / "alb2002_climate_outcome_linked_candidate_audit.md")
            and alb2002_linked_rows == "14396"
            and alb2002_linked_households == "3599"
            and alb2002_linked_windows == "4"
            and alb2002_linked_district_months == "96"
            and alb2002_linked_lineage_rows == "7"
            and alb2002_linked_audit_rows == "7"
            and alb2002_linked_source_analysis_rows == "3599"
            and alb2002_linked_source_uhc_rows == "3599"
            and alb2002_linked_source_shock_rows == "384"
            and alb2002_linked_expected_rows == "14396"
            and alb2002_linked_unmatched == "0"
            and alb2002_linked_precip_z == "14396"
            and alb2002_linked_temp_z == "14396"
            and alb2002_linked_che10_or_access == "8016"
            and alb2002_linked_che25_or_access == "7556"
            and alb2002_linked_both == "2724"
            and alb2002_linked_coping == "5904"
            and alb2002_linked_climate_ready == "0"
            and alb2002_linked_outcome_ready == "0"
            and alb2002_linked_harmonized_ready == "0"
            and alb2002_linked_data_write == "0"
            and alb2002_linked_decision == "blocked_alb2002_climate_outcome_linked_candidate_not_promoted_due_recipe_outcome_geography_source_baseline_gates"
        ),
        f"linked_rows={counts['alb2002_climate_outcome_linked_candidate']}; lineage_rows={counts['alb2002_climate_outcome_linked_candidate_lineage']}; audit_rows={counts['alb2002_climate_outcome_linked_candidate_audit']}; summary_rows={counts['alb2002_climate_outcome_linked_candidate_summary']}; households={alb2002_linked_households}; windows={alb2002_linked_windows}; district_months={alb2002_linked_district_months}; expected_rows={alb2002_linked_expected_rows}; unmatched_rows={alb2002_linked_unmatched}; precip_z={alb2002_linked_precip_z}; temp_z={alb2002_linked_temp_z}; combined_stress={alb2002_linked_combined}; che10_or_access={alb2002_linked_che10_or_access}; che25_or_access={alb2002_linked_che25_or_access}; both_che10_access={alb2002_linked_both}; coping={alb2002_linked_coping}; harmonized_ready={alb2002_linked_harmonized_ready}; outcome_ready={alb2002_linked_outcome_ready}; climate_ready={alb2002_linked_climate_ready}; data_write_ready={alb2002_linked_data_write}; decision={alb2002_linked_decision}",
        ""
        if counts["alb2002_climate_outcome_linked_candidate"] == 14396
        and counts["alb2002_climate_outcome_linked_candidate_audit"] == 7
        and alb2002_linked_unmatched == "0"
        and alb2002_linked_climate_ready == "0"
        and alb2002_linked_outcome_ready == "0"
        and alb2002_linked_data_write == "0"
        and alb2002_linked_decision == "blocked_alb2002_climate_outcome_linked_candidate_not_promoted_due_recipe_outcome_geography_source_baseline_gates"
        else "Run script/108_build_alb2002_climate_outcome_linked_candidate_audit.py after the shock diagnostics; keep linked candidate temp-only until recipe, outcome, geography, primary source, and historical-baseline gates pass.",
    )
    alb2002_descriptive_summary = read_csv_dicts(RESULT_DIR / "alb2002_linked_candidate_descriptive_summary.csv")
    alb2002_descriptive_input_rows = next((row.get("value", "0") for row in alb2002_descriptive_summary if row.get("metric") == "alb2002_linked_candidate_descriptive_input_rows"), "0")
    alb2002_descriptive_households = next((row.get("value", "0") for row in alb2002_descriptive_summary if row.get("metric") == "alb2002_linked_candidate_descriptive_household_rows"), "0")
    alb2002_descriptive_windows = next((row.get("value", "0") for row in alb2002_descriptive_summary if row.get("metric") == "alb2002_linked_candidate_descriptive_window_rows"), "0")
    alb2002_descriptive_audit_rows = next((row.get("value", "0") for row in alb2002_descriptive_summary if row.get("metric") == "alb2002_linked_candidate_descriptive_audit_rows"), "0")
    alb2002_descriptive_cell_rows = next((row.get("value", "0") for row in alb2002_descriptive_summary if row.get("metric") == "alb2002_linked_candidate_descriptive_cell_rows"), "0")
    alb2002_descriptive_household_cells = next((row.get("value", "0") for row in alb2002_descriptive_summary if row.get("metric") == "alb2002_linked_candidate_descriptive_household_outcome_cell_rows"), "0")
    alb2002_descriptive_subgroup_cells = next((row.get("value", "0") for row in alb2002_descriptive_summary if row.get("metric") == "alb2002_linked_candidate_descriptive_subgroup_outcome_cell_rows"), "0")
    alb2002_descriptive_climate_cells = next((row.get("value", "0") for row in alb2002_descriptive_summary if row.get("metric") == "alb2002_linked_candidate_descriptive_climate_flag_cell_rows"), "0")
    alb2002_descriptive_outcome_climate_cells = next((row.get("value", "0") for row in alb2002_descriptive_summary if row.get("metric") == "alb2002_linked_candidate_descriptive_outcome_by_climate_flag_cell_rows"), "0")
    alb2002_descriptive_che10 = next((row.get("value", "0") for row in alb2002_descriptive_summary if row.get("metric") == "alb2002_linked_candidate_descriptive_che10_or_access_households"), "0")
    alb2002_descriptive_che25 = next((row.get("value", "0") for row in alb2002_descriptive_summary if row.get("metric") == "alb2002_linked_candidate_descriptive_che25_or_access_households"), "0")
    alb2002_descriptive_both = next((row.get("value", "0") for row in alb2002_descriptive_summary if row.get("metric") == "alb2002_linked_candidate_descriptive_both_che10_access_households"), "0")
    alb2002_descriptive_coping = next((row.get("value", "0") for row in alb2002_descriptive_summary if row.get("metric") == "alb2002_linked_candidate_descriptive_coping_households"), "0")
    alb2002_descriptive_low_rain = next((row.get("value", "0") for row in alb2002_descriptive_summary if row.get("metric") == "alb2002_linked_candidate_descriptive_low_rain_rows"), "0")
    alb2002_descriptive_extreme_wet = next((row.get("value", "0") for row in alb2002_descriptive_summary if row.get("metric") == "alb2002_linked_candidate_descriptive_extreme_wet_rows"), "0")
    alb2002_descriptive_extreme_heat = next((row.get("value", "0") for row in alb2002_descriptive_summary if row.get("metric") == "alb2002_linked_candidate_descriptive_extreme_heat_rows"), "0")
    alb2002_descriptive_combined = next((row.get("value", "0") for row in alb2002_descriptive_summary if row.get("metric") == "alb2002_linked_candidate_descriptive_combined_stress_rows"), "0")
    alb2002_descriptive_climate_ready = next((row.get("value", "0") for row in alb2002_descriptive_summary if row.get("metric") == "alb2002_linked_candidate_descriptive_climate_linkage_ready_rows"), "0")
    alb2002_descriptive_outcome_ready = next((row.get("value", "0") for row in alb2002_descriptive_summary if row.get("metric") == "alb2002_linked_candidate_descriptive_outcome_promotion_ready_rows"), "0")
    alb2002_descriptive_harmonized_ready = next((row.get("value", "0") for row in alb2002_descriptive_summary if row.get("metric") == "alb2002_linked_candidate_descriptive_harmonized_recipe_ready_rows"), "0")
    alb2002_descriptive_data_write = next((row.get("value", "0") for row in alb2002_descriptive_summary if row.get("metric") == "alb2002_linked_candidate_descriptive_data_write_ready_rows"), "0")
    alb2002_descriptive_source_decision = next((row.get("value", "") for row in alb2002_descriptive_summary if row.get("metric") == "alb2002_linked_candidate_descriptive_source_linked_decision"), "")
    alb2002_descriptive_decision = next((row.get("value", "") for row in alb2002_descriptive_summary if row.get("metric") == "alb2002_linked_candidate_descriptive_current_decision"), "")
    add(
        rows,
        "evidence",
        "ALB_2002 linked-candidate descriptive screen summarizes candidate rates without promoting descriptive diagnostics",
        status(
            counts["alb2002_linked_candidate_descriptive_audit"] == 7
            and counts["alb2002_linked_candidate_descriptive_cells"] == 108
            and counts["alb2002_linked_candidate_descriptive_summary"] > 0
            and file_ok(REPORT_DIR / "alb2002_linked_candidate_descriptive_diagnostics.md")
            and alb2002_descriptive_input_rows == "14396"
            and alb2002_descriptive_households == "3599"
            and alb2002_descriptive_windows == "4"
            and alb2002_descriptive_audit_rows == "7"
            and alb2002_descriptive_cell_rows == "108"
            and alb2002_descriptive_household_cells == "4"
            and alb2002_descriptive_subgroup_cells == "24"
            and alb2002_descriptive_climate_cells == "16"
            and alb2002_descriptive_outcome_climate_cells == "64"
            and alb2002_descriptive_che10 == "2004"
            and alb2002_descriptive_che25 == "1889"
            and alb2002_descriptive_both == "681"
            and alb2002_descriptive_coping == "1476"
            and alb2002_descriptive_low_rain == "1008"
            and alb2002_descriptive_extreme_wet == "1398"
            and alb2002_descriptive_extreme_heat == "1694"
            and alb2002_descriptive_combined == "3092"
            and alb2002_descriptive_climate_ready == "0"
            and alb2002_descriptive_outcome_ready == "0"
            and alb2002_descriptive_harmonized_ready == "0"
            and alb2002_descriptive_data_write == "0"
            and alb2002_descriptive_source_decision == "blocked_alb2002_climate_outcome_linked_candidate_not_promoted_due_recipe_outcome_geography_source_baseline_gates"
            and alb2002_descriptive_decision == "blocked_alb2002_linked_candidate_descriptive_screen_not_promoted_due_unpromoted_inputs"
        ),
        f"audit_rows={counts['alb2002_linked_candidate_descriptive_audit']}; cell_rows={counts['alb2002_linked_candidate_descriptive_cells']}; summary_rows={counts['alb2002_linked_candidate_descriptive_summary']}; input_rows={alb2002_descriptive_input_rows}; households={alb2002_descriptive_households}; windows={alb2002_descriptive_windows}; household_cells={alb2002_descriptive_household_cells}; subgroup_cells={alb2002_descriptive_subgroup_cells}; climate_flag_cells={alb2002_descriptive_climate_cells}; outcome_by_climate_cells={alb2002_descriptive_outcome_climate_cells}; che10_or_access_households={alb2002_descriptive_che10}; che25_or_access_households={alb2002_descriptive_che25}; both_che10_access_households={alb2002_descriptive_both}; coping_households={alb2002_descriptive_coping}; combined_stress_rows={alb2002_descriptive_combined}; harmonized_ready={alb2002_descriptive_harmonized_ready}; outcome_ready={alb2002_descriptive_outcome_ready}; climate_ready={alb2002_descriptive_climate_ready}; data_write_ready={alb2002_descriptive_data_write}; decision={alb2002_descriptive_decision}",
        ""
        if counts["alb2002_linked_candidate_descriptive_cells"] == 108
        and alb2002_descriptive_climate_ready == "0"
        and alb2002_descriptive_data_write == "0"
        and alb2002_descriptive_decision == "blocked_alb2002_linked_candidate_descriptive_screen_not_promoted_due_unpromoted_inputs"
        else "Run script/109_build_alb2002_linked_candidate_descriptive_diagnostics.py after the linked-candidate audit; keep this as a temp-only descriptive screen, not a promoted descriptive diagnostic.",
    )
    alb2002_manual_summary = read_csv_dicts(RESULT_DIR / "alb2002_boundary_manual_verification_packet_summary.csv")
    alb2002_manual_actions = next((row.get("value", "0") for row in alb2002_manual_summary if row.get("metric") == "alb2002_boundary_manual_verification_action_rows"), "0")
    alb2002_manual_gates = next((row.get("value", "0") for row in alb2002_manual_summary if row.get("metric") == "alb2002_boundary_manual_verification_gate_rows"), "0")
    alb2002_manual_blocked_gates = next((row.get("value", "0") for row in alb2002_manual_summary if row.get("metric") == "alb2002_boundary_manual_verification_blocked_gates"), "0")
    alb2002_manual_candidate_gates = next((row.get("value", "0") for row in alb2002_manual_summary if row.get("metric") == "alb2002_boundary_manual_verification_candidate_evidence_gates"), "0")
    alb2002_manual_pre2011_map_absence = next((row.get("value", "0") for row in alb2002_manual_summary if row.get("metric") == "alb2002_boundary_manual_verification_pre2011_digital_map_absence_rows"), "0")
    alb2002_manual_climate_ready = next((row.get("value", "0") for row in alb2002_manual_summary if row.get("metric") == "alb2002_boundary_manual_verification_climate_linkage_ready_rows"), "0")
    alb2002_manual_decision = next((row.get("value", "") for row in alb2002_manual_summary if row.get("metric") == "alb2002_boundary_manual_verification_current_decision"), "")
    add(
        rows,
        "evidence",
        "ALB_2002 boundary manual verification packet converts the geography blocker into source actions and promotion gates",
        status(
            counts["alb2002_boundary_manual_verification_action_queue"] > 0
            and counts["alb2002_boundary_promotion_gate_checklist"] > 0
            and counts["alb2002_boundary_manual_verification_packet_summary"] > 0
            and alb2002_manual_pre2011_map_absence == "1"
            and alb2002_manual_climate_ready == "0"
            and alb2002_manual_decision == "blocked_manual_boundary_verification_required_before_alb2002_climate_linkage"
        ),
        f"action_rows={counts['alb2002_boundary_manual_verification_action_queue']}; gate_rows={counts['alb2002_boundary_promotion_gate_checklist']}; summary_rows={counts['alb2002_boundary_manual_verification_packet_summary']}; summary_actions={alb2002_manual_actions}; summary_gates={alb2002_manual_gates}; candidate_gates={alb2002_manual_candidate_gates}; blocked_gates={alb2002_manual_blocked_gates}; pre2011_digital_map_absence={alb2002_manual_pre2011_map_absence}; climate_ready={alb2002_manual_climate_ready}; decision={alb2002_manual_decision}",
        ""
        if counts["alb2002_boundary_manual_verification_action_queue"] > 0
        and counts["alb2002_boundary_promotion_gate_checklist"] > 0
        and counts["alb2002_boundary_manual_verification_packet_summary"] > 0
        and alb2002_manual_pre2011_map_absence == "1"
        and alb2002_manual_climate_ready == "0"
        and alb2002_manual_decision == "blocked_manual_boundary_verification_required_before_alb2002_climate_linkage"
        else "Run script/81_build_alb2002_boundary_manual_verification_packet.py and keep ALB_2002 climate linkage blocked until manual boundary verification gates pass.",
    )
    alb2002_followup_summary = read_csv_dicts(RESULT_DIR / "alb2002_boundary_manual_source_followup_summary.csv")
    alb2002_followup_rows = next((row.get("value", "0") for row in alb2002_followup_summary if row.get("metric") == "alb2002_boundary_manual_source_followup_rows"), "0")
    alb2002_followup_blockers = next((row.get("value", "0") for row in alb2002_followup_summary if row.get("metric") == "alb2002_boundary_manual_source_followup_conclusive_blocker_rows"), "0")
    alb2002_followup_district_ready = next((row.get("value", "0") for row in alb2002_followup_summary if row.get("metric") == "alb2002_boundary_manual_source_followup_district_level_ready_rows"), "0")
    alb2002_followup_climate_ready = next((row.get("value", "0") for row in alb2002_followup_summary if row.get("metric") == "alb2002_boundary_manual_source_followup_climate_linkage_ready_rows"), "0")
    alb2002_followup_ipums_status = next((row.get("value", "") for row in alb2002_followup_summary if row.get("metric") == "alb2002_boundary_manual_source_followup_ipums_level_status"), "")
    alb2002_followup_unece_status = next((row.get("value", "") for row in alb2002_followup_summary if row.get("metric") == "alb2002_boundary_manual_source_followup_unece_pre2011_map_status"), "")
    alb2002_followup_decision = next((row.get("value", "") for row in alb2002_followup_summary if row.get("metric") == "alb2002_boundary_manual_source_followup_current_decision"), "")
    add(
        rows,
        "evidence",
        "ALB_2002 boundary manual source follow-up records IHGIS as prefecture-only, UNECE/INSTAT pre-2011 digital-map absence, and keeps all boundary leads blocked",
        status(
            counts["alb2002_boundary_manual_source_followup_audit"] > 0
            and counts["alb2002_boundary_manual_source_followup_summary"] > 0
            and alb2002_followup_rows == "7"
            and alb2002_followup_blockers == "7"
            and alb2002_followup_district_ready == "0"
            and alb2002_followup_climate_ready == "0"
            and alb2002_followup_ipums_status == "blocked_prefecture_g1_not_36_lsms_districts"
            and alb2002_followup_unece_status == "blocked_pre2011_digital_boundary_source_absence_documented"
            and alb2002_followup_decision == "blocked_followup_confirms_no_public_2002_district_boundary_source"
        ),
        f"audit_rows={counts['alb2002_boundary_manual_source_followup_audit']}; summary_rows={counts['alb2002_boundary_manual_source_followup_summary']}; followup_rows={alb2002_followup_rows}; conclusive_blockers={alb2002_followup_blockers}; district_ready={alb2002_followup_district_ready}; climate_ready={alb2002_followup_climate_ready}; ipums_status={alb2002_followup_ipums_status}; unece_status={alb2002_followup_unece_status}; decision={alb2002_followup_decision}",
        ""
        if counts["alb2002_boundary_manual_source_followup_audit"] > 0
        and counts["alb2002_boundary_manual_source_followup_summary"] > 0
        and alb2002_followup_rows == "7"
        and alb2002_followup_blockers == "7"
        and alb2002_followup_district_ready == "0"
        and alb2002_followup_climate_ready == "0"
        and alb2002_followup_ipums_status == "blocked_prefecture_g1_not_36_lsms_districts"
        and alb2002_followup_unece_status == "blocked_pre2011_digital_boundary_source_absence_documented"
        and alb2002_followup_decision == "blocked_followup_confirms_no_public_2002_district_boundary_source"
        else "Run script/82_audit_alb2002_boundary_manual_source_followup.py and keep ALB_2002 climate linkage blocked until a verified 2001/2002 district boundary source is found.",
    )
    alb2002_local_geo_summary = read_csv_dicts(RESULT_DIR / "alb2002_local_geography_artifact_summary.csv")
    alb2002_local_geo_coord_raw = next((row.get("value", "0") for row in alb2002_local_geo_summary if row.get("metric") == "alb2002_local_geo_artifact_coordinate_raw_variable_rows"), "0")
    alb2002_local_geo_questionnaire_coord = next((row.get("value", "0") for row in alb2002_local_geo_summary if row.get("metric") == "alb2002_local_geo_artifact_questionnaire_coordinate_field_rows"), "0")
    alb2002_local_geo_local_coordinate_ready = next((row.get("value", "0") for row in alb2002_local_geo_summary if row.get("metric") == "alb2002_local_geo_artifact_local_coordinate_ready_rows"), "0")
    alb2002_local_geo_local_boundary_ready = next((row.get("value", "0") for row in alb2002_local_geo_summary if row.get("metric") == "alb2002_local_geo_artifact_local_boundary_ready_rows"), "0")
    alb2002_local_geo_climate_ready = next((row.get("value", "0") for row in alb2002_local_geo_summary if row.get("metric") == "alb2002_local_geo_artifact_climate_linkage_ready_rows"), "0")
    alb2002_local_geo_decision = next((row.get("value", "") for row in alb2002_local_geo_summary if row.get("metric") == "alb2002_local_geo_artifact_current_decision"), "")
    add(
        rows,
        "evidence",
        "ALB_2002 local geography artifact audit keeps questionnaire GPS fields blocked until raw coordinate or boundary artifacts exist",
        status(
            counts["alb2002_local_geography_artifact_audit"] > 0
            and counts["alb2002_local_geography_artifact_summary"] > 0
            and alb2002_local_geo_coord_raw == "0"
            and alb2002_local_geo_local_coordinate_ready == "0"
            and alb2002_local_geo_local_boundary_ready == "0"
            and alb2002_local_geo_climate_ready == "0"
            and alb2002_local_geo_decision == "blocked_questionnaire_gps_fields_not_present_as_raw_coordinate_artifacts"
        ),
        f"audit_rows={counts['alb2002_local_geography_artifact_audit']}; summary_rows={counts['alb2002_local_geography_artifact_summary']}; raw_coordinate_variables={alb2002_local_geo_coord_raw}; questionnaire_coordinate_fields={alb2002_local_geo_questionnaire_coord}; local_coordinate_ready={alb2002_local_geo_local_coordinate_ready}; local_boundary_ready={alb2002_local_geo_local_boundary_ready}; climate_ready={alb2002_local_geo_climate_ready}; decision={alb2002_local_geo_decision}",
        ""
        if counts["alb2002_local_geography_artifact_audit"] > 0
        and counts["alb2002_local_geography_artifact_summary"] > 0
        and alb2002_local_geo_coord_raw == "0"
        and alb2002_local_geo_local_coordinate_ready == "0"
        and alb2002_local_geo_local_boundary_ready == "0"
        and alb2002_local_geo_climate_ready == "0"
        and alb2002_local_geo_decision == "blocked_questionnaire_gps_fields_not_present_as_raw_coordinate_artifacts"
        else "Run script/70_audit_alb2002_local_geography_artifacts.py and keep ALB_2002 climate linkage blocked until local raw coordinate values or boundary artifacts are verified.",
    )
    alb2012_summary = read_csv_dicts(RESULT_DIR / "alb2012_raw_core_feasibility_summary.csv")
    alb2012_recipe_ready = next((row.get("value", "0") for row in alb2012_summary if row.get("metric") == "alb2012_household_core_recipe_ready_rows"), "0")
    alb2012_climate_ready = next((row.get("value", "0") for row in alb2012_summary if row.get("metric") == "alb2012_climate_linkage_ready_rows"), "0")
    alb2012_timing_rows = next((row.get("value", "0") for row in alb2012_summary if row.get("metric") == "alb2012_timing_signal_rows"), "0")
    alb2012_decision = next((row.get("value", "") for row in alb2012_summary if row.get("metric") == "alb2012_raw_core_current_decision"), "")
    add(
        rows,
        "evidence",
        "ALB_2012 raw core feasibility audit builds a temp-only candidate and keeps harmonization/climate promotion blocked",
        status(
            counts["alb2012_household_core_candidate"] > 0
            and counts["alb2012_raw_core_feasibility_audit"] > 0
            and counts["alb2012_raw_core_lineage"] > 0
            and counts["alb2012_raw_core_feasibility_summary"] > 0
            and alb2012_recipe_ready == "0"
            and alb2012_climate_ready == "0"
            and alb2012_timing_rows == "0"
            and alb2012_decision == "temp_candidate_no_interview_timing_coarse_geography_outcome_semantics_pending"
        ),
        f"candidate_rows={counts['alb2012_household_core_candidate']}; audit_rows={counts['alb2012_raw_core_feasibility_audit']}; lineage_rows={counts['alb2012_raw_core_lineage']}; summary_rows={counts['alb2012_raw_core_feasibility_summary']}; recipe_ready_rows={alb2012_recipe_ready}; climate_linkage_ready_rows={alb2012_climate_ready}; timing_signal_rows={alb2012_timing_rows}; decision={alb2012_decision}",
        ""
        if counts["alb2012_household_core_candidate"] > 0
        and counts["alb2012_raw_core_feasibility_audit"] > 0
        and counts["alb2012_raw_core_lineage"] > 0
        and counts["alb2012_raw_core_feasibility_summary"] > 0
        and alb2012_recipe_ready == "0"
        and alb2012_climate_ready == "0"
        and alb2012_timing_rows == "0"
        and alb2012_decision == "temp_candidate_no_interview_timing_coarse_geography_outcome_semantics_pending"
        else "Run script/57_audit_alb2012_raw_core_feasibility.py and keep ALB_2012 out of data/ until timing/geography and value semantics pass.",
    )
    alb2012_outcome_summary = read_csv_dicts(RESULT_DIR / "alb2012_provisional_outcome_feasibility_summary.csv")
    alb2012_outcome_ready = next((row.get("value", "0") for row in alb2012_outcome_summary if row.get("metric") == "alb2012_provisional_outcome_ready_rows"), "0")
    alb2012_outcome_climate_ready = next((row.get("value", "0") for row in alb2012_outcome_summary if row.get("metric") == "alb2012_provisional_climate_linkage_ready_rows"), "0")
    alb2012_outcome_timing_rows = next((row.get("value", "0") for row in alb2012_outcome_summary if row.get("metric") == "alb2012_provisional_survey_month_rows"), "0")
    alb2012_outcome_date_rows = next((row.get("value", "0") for row in alb2012_outcome_summary if row.get("metric") == "alb2012_provisional_interview_date_rows"), "0")
    alb2012_outcome_decision = next((row.get("value", "") for row in alb2012_outcome_summary if row.get("metric") == "alb2012_provisional_outcome_current_decision"), "")
    add(
        rows,
        "evidence",
        "ALB_2012 provisional outcome feasibility audit keeps all outcome and climate promotion blocked",
        status(
            counts["alb2012_provisional_outcome_feasibility_audit"] > 0
            and counts["alb2012_provisional_outcome_feasibility_summary"] > 0
            and alb2012_outcome_ready == "0"
            and alb2012_outcome_climate_ready == "0"
            and alb2012_outcome_timing_rows == "0"
            and alb2012_outcome_date_rows == "0"
            and alb2012_outcome_decision == "not_final_outcomes_timing_geography_recall_semantics_blocked"
        ),
        f"audit_rows={counts['alb2012_provisional_outcome_feasibility_audit']}; summary_rows={counts['alb2012_provisional_outcome_feasibility_summary']}; outcome_ready_rows={alb2012_outcome_ready}; climate_linkage_ready_rows={alb2012_outcome_climate_ready}; survey_month_rows={alb2012_outcome_timing_rows}; interview_date_rows={alb2012_outcome_date_rows}; decision={alb2012_outcome_decision}",
        ""
        if counts["alb2012_provisional_outcome_feasibility_audit"] > 0
        and counts["alb2012_provisional_outcome_feasibility_summary"] > 0
        and alb2012_outcome_ready == "0"
        and alb2012_outcome_climate_ready == "0"
        and alb2012_outcome_timing_rows == "0"
        and alb2012_outcome_date_rows == "0"
        and alb2012_outcome_decision == "not_final_outcomes_timing_geography_recall_semantics_blocked"
        else "Run script/58_audit_alb2012_provisional_outcome_feasibility.py and keep ALB_2012 provisional outcomes out of data/.",
    )
    alb2012_semantics_summary = read_csv_dicts(RESULT_DIR / "alb2012_outcome_semantics_raw_value_summary.csv")
    alb2012_semantics_outcome_ready = next((row.get("value", "0") for row in alb2012_semantics_summary if row.get("metric") == "alb2012_outcome_semantics_outcome_ready_rows"), "0")
    alb2012_semantics_sdg_ready = next((row.get("value", "0") for row in alb2012_semantics_summary if row.get("metric") == "alb2012_outcome_semantics_sdg382_ready_rows"), "0")
    alb2012_semantics_climate_ready = next((row.get("value", "0") for row in alb2012_semantics_summary if row.get("metric") == "alb2012_outcome_semantics_climate_linkage_ready_rows"), "0")
    alb2012_semantics_decision = next((row.get("value", "") for row in alb2012_semantics_summary if row.get("metric") == "alb2012_outcome_semantics_current_decision"), "")
    add(
        rows,
        "evidence",
        "ALB_2012 raw outcome-semantics value audit documents payment, gift, access, need, coping, and service-quality fields while keeping promotion blocked",
        status(
            counts["alb2012_outcome_semantics_raw_value_audit"] > 0
            and counts["alb2012_outcome_semantics_raw_value_summary"] > 0
            and alb2012_semantics_outcome_ready == "0"
            and alb2012_semantics_sdg_ready == "0"
            and alb2012_semantics_climate_ready == "0"
            and alb2012_semantics_decision == "blocked_timing_geography_outcome_semantics_units_recall_skip_patterns"
        ),
        f"audit_rows={counts['alb2012_outcome_semantics_raw_value_audit']}; summary_rows={counts['alb2012_outcome_semantics_raw_value_summary']}; outcome_ready={alb2012_semantics_outcome_ready}; sdg382_ready={alb2012_semantics_sdg_ready}; climate_ready={alb2012_semantics_climate_ready}; decision={alb2012_semantics_decision}",
        ""
        if counts["alb2012_outcome_semantics_raw_value_audit"] > 0
        and counts["alb2012_outcome_semantics_raw_value_summary"] > 0
        and alb2012_semantics_outcome_ready == "0"
        and alb2012_semantics_sdg_ready == "0"
        and alb2012_semantics_climate_ready == "0"
        and alb2012_semantics_decision == "blocked_timing_geography_outcome_semantics_units_recall_skip_patterns"
        else "Run script/63_audit_alb2012_outcome_semantics_raw_values.py and keep all ALB_2012 outcome, SDG 3.8.2, and climate-linkage promotion blocked.",
    )
    alb2012_timing_geo_summary = read_csv_dicts(RESULT_DIR / "alb2012_timing_geography_exhaustive_summary.csv")
    alb2012_timing_geo_interview = next((row.get("value", "0") for row in alb2012_timing_geo_summary if row.get("metric") == "alb2012_interview_timing_verified_rows"), "0")
    alb2012_timing_geo_coordinates = next((row.get("value", "0") for row in alb2012_timing_geo_summary if row.get("metric") == "alb2012_coordinate_candidate_rows"), "0")
    alb2012_timing_geo_climate = next((row.get("value", "0") for row in alb2012_timing_geo_summary if row.get("metric") == "alb2012_climate_linkage_ready_rows"), "0")
    alb2012_timing_geo_decision = next((row.get("value", "") for row in alb2012_timing_geo_summary if row.get("metric") == "alb2012_timing_geography_current_decision"), "")
    add(
        rows,
        "evidence",
        "ALB_2012 exhaustive timing/geography audit keeps climate linkage blocked",
        status(
            counts["alb2012_timing_geography_exhaustive_audit"] > 0
            and counts["alb2012_timing_geography_exhaustive_summary"] > 0
            and alb2012_timing_geo_interview == "0"
            and alb2012_timing_geo_coordinates == "0"
            and alb2012_timing_geo_climate == "0"
            and alb2012_timing_geo_decision == "blocked_missing_interview_timing_coarse_prefecture_region_no_gps"
        ),
        f"audit_rows={counts['alb2012_timing_geography_exhaustive_audit']}; summary_rows={counts['alb2012_timing_geography_exhaustive_summary']}; verified_interview_timing_rows={alb2012_timing_geo_interview}; coordinate_candidate_rows={alb2012_timing_geo_coordinates}; climate_linkage_ready_rows={alb2012_timing_geo_climate}; decision={alb2012_timing_geo_decision}",
        ""
        if counts["alb2012_timing_geography_exhaustive_audit"] > 0
        and counts["alb2012_timing_geography_exhaustive_summary"] > 0
        and alb2012_timing_geo_interview == "0"
        and alb2012_timing_geo_coordinates == "0"
        and alb2012_timing_geo_climate == "0"
        and alb2012_timing_geo_decision == "blocked_missing_interview_timing_coarse_prefecture_region_no_gps"
        else "Run script/59_audit_alb2012_timing_geography_exhaustive.py and keep ALB_2012 climate linkage blocked until timing/geography pass.",
    )
    alb2012_questionnaire_summary = read_csv_dicts(RESULT_DIR / "alb2012_questionnaire_timing_field_summary.csv")
    alb2012_questionnaire_fields = next((row.get("value", "0") for row in alb2012_questionnaire_summary if row.get("metric") == "alb2012_questionnaire_timing_field_rows"), "0")
    alb2012_questionnaire_raw_gap = next((row.get("value", "0") for row in alb2012_questionnaire_summary if row.get("metric") == "alb2012_questionnaire_timing_raw_gap_rows"), "0")
    alb2012_questionnaire_raw_verified = next((row.get("value", "0") for row in alb2012_questionnaire_summary if row.get("metric") == "alb2012_questionnaire_timing_raw_verified_interview_timing_rows"), "0")
    alb2012_questionnaire_climate = next((row.get("value", "0") for row in alb2012_questionnaire_summary if row.get("metric") == "alb2012_questionnaire_timing_climate_linkage_ready_rows"), "0")
    alb2012_questionnaire_decision = next((row.get("value", "") for row in alb2012_questionnaire_summary if row.get("metric") == "alb2012_questionnaire_timing_current_decision"), "")
    add(
        rows,
        "evidence",
        "ALB_2012 questionnaire timing field audit documents form timing fields while keeping raw timing and climate linkage blocked",
        status(
            counts["alb2012_questionnaire_timing_field_audit"] > 0
            and counts["alb2012_questionnaire_timing_raw_gap_audit"] > 0
            and counts["alb2012_questionnaire_timing_field_summary"] > 0
            and alb2012_questionnaire_raw_verified == "0"
            and alb2012_questionnaire_climate == "0"
            and alb2012_questionnaire_decision == "blocked_questionnaire_timing_fields_not_in_raw_household_values"
        ),
        f"field_rows={alb2012_questionnaire_fields}; raw_gap_rows={alb2012_questionnaire_raw_gap}; summary_rows={counts['alb2012_questionnaire_timing_field_summary']}; raw_verified_interview_timing_rows={alb2012_questionnaire_raw_verified}; climate_linkage_ready_rows={alb2012_questionnaire_climate}; decision={alb2012_questionnaire_decision}",
        ""
        if counts["alb2012_questionnaire_timing_field_audit"] > 0
        and counts["alb2012_questionnaire_timing_raw_gap_audit"] > 0
        and counts["alb2012_questionnaire_timing_field_summary"] > 0
        and alb2012_questionnaire_raw_verified == "0"
        and alb2012_questionnaire_climate == "0"
        and alb2012_questionnaire_decision == "blocked_questionnaire_timing_fields_not_in_raw_household_values"
        else "Run script/65_audit_alb2012_questionnaire_timing_fields.py and keep ALB_2012 climate linkage blocked until raw household interview timing values are verified.",
    )
    albania_legacy_questionnaire_summary = read_csv_dicts(RESULT_DIR / "albania_legacy_questionnaire_readability_summary.csv")
    legacy_present = next((row.get("value", "0") for row in albania_legacy_questionnaire_summary if row.get("metric") == "albania_legacy_questionnaire_present_files"), "0")
    legacy_read_ok = next((row.get("value", "0") for row in albania_legacy_questionnaire_summary if row.get("metric") == "albania_legacy_questionnaire_read_ok_files"), "0")
    legacy_blocked = next((row.get("value", "0") for row in albania_legacy_questionnaire_summary if row.get("metric") == "albania_legacy_questionnaire_missing_reader_blocked_files"), "0")
    legacy_timing_ready = next((row.get("value", "0") for row in albania_legacy_questionnaire_summary if row.get("metric") == "albania_legacy_questionnaire_timing_content_audit_ready_rows"), "0")
    legacy_climate_ready = next((row.get("value", "0") for row in albania_legacy_questionnaire_summary if row.get("metric") == "albania_legacy_questionnaire_climate_linkage_ready_rows"), "0")
    legacy_decision = next((row.get("value", "") for row in albania_legacy_questionnaire_summary if row.get("metric") == "albania_legacy_questionnaire_current_decision"), "")
    add(
        rows,
        "evidence",
        "Albania legacy questionnaire readability audit documents .xls files and verifies they are readable before separate content extraction",
        status(
            counts["albania_legacy_questionnaire_readability_audit"] > 0
            and counts["albania_legacy_questionnaire_readability_summary"] > 0
            and legacy_present == "5"
            and legacy_read_ok == "5"
            and legacy_timing_ready == "5"
            and legacy_climate_ready == "0"
            and legacy_decision == "legacy_questionnaires_readable_content_audit_required"
        ),
        f"audit_rows={counts['albania_legacy_questionnaire_readability_audit']}; summary_rows={counts['albania_legacy_questionnaire_readability_summary']}; present_files={legacy_present}; read_ok_files={legacy_read_ok}; missing_reader_blocked_files={legacy_blocked}; timing_content_ready_rows={legacy_timing_ready}; climate_linkage_ready_rows={legacy_climate_ready}; decision={legacy_decision}",
        ""
        if counts["albania_legacy_questionnaire_readability_audit"] > 0
        and counts["albania_legacy_questionnaire_readability_summary"] > 0
        and legacy_present == "5"
        and legacy_read_ok == "5"
        and legacy_timing_ready == "5"
        and legacy_climate_ready == "0"
        and legacy_decision == "legacy_questionnaires_readable_content_audit_required"
        else "Run script/66_audit_albania_legacy_questionnaire_readability.py and keep legacy questionnaire content out of climate linkage until the separate content audit runs.",
    )
    albania_legacy_timing_summary = read_csv_dicts(RESULT_DIR / "albania_legacy_questionnaire_timing_field_summary.csv")
    legacy_timing_fields = next((row.get("value", "0") for row in albania_legacy_timing_summary if row.get("metric") == "albania_legacy_questionnaire_timing_field_rows"), "0")
    legacy_timing_raw_gap = next((row.get("value", "0") for row in albania_legacy_timing_summary if row.get("metric") == "albania_legacy_questionnaire_timing_raw_gap_rows"), "0")
    legacy_timing_raw_verified = next((row.get("value", "0") for row in albania_legacy_timing_summary if row.get("metric") == "albania_legacy_questionnaire_timing_raw_verified_interview_timing_rows"), "0")
    legacy_timing_climate = next((row.get("value", "0") for row in albania_legacy_timing_summary if row.get("metric") == "albania_legacy_questionnaire_timing_climate_linkage_ready_rows"), "0")
    legacy_timing_decision = next((row.get("value", "") for row in albania_legacy_timing_summary if row.get("metric") == "albania_legacy_questionnaire_timing_current_decision"), "")
    add(
        rows,
        "evidence",
        "Albania legacy questionnaire timing audit documents form timing fields while keeping climate linkage blocked",
        status(
            counts["albania_legacy_questionnaire_timing_field_audit"] > 0
            and counts["albania_legacy_questionnaire_timing_raw_gap_audit"] > 0
            and counts["albania_legacy_questionnaire_timing_field_summary"] > 0
            and safe_int(legacy_timing_raw_verified) > 0
            and legacy_timing_climate == "0"
            and legacy_timing_decision == "blocked_legacy_questionnaire_form_design_not_sufficient_for_climate_linkage"
        ),
        f"field_rows={legacy_timing_fields}; raw_gap_rows={legacy_timing_raw_gap}; summary_rows={counts['albania_legacy_questionnaire_timing_field_summary']}; raw_verified_interview_timing_rows={legacy_timing_raw_verified}; climate_linkage_ready_rows={legacy_timing_climate}; decision={legacy_timing_decision}",
        ""
        if counts["albania_legacy_questionnaire_timing_field_audit"] > 0
        and counts["albania_legacy_questionnaire_timing_raw_gap_audit"] > 0
        and counts["albania_legacy_questionnaire_timing_field_summary"] > 0
        and safe_int(legacy_timing_raw_verified) > 0
        and legacy_timing_climate == "0"
        and legacy_timing_decision == "blocked_legacy_questionnaire_form_design_not_sufficient_for_climate_linkage"
        else "Run script/67_audit_albania_legacy_questionnaire_timing_fields.py and keep legacy climate linkage blocked until raw timing/geography and outcome semantics pass.",
    )
    core_summary = read_csv_dicts(RESULT_DIR / "alb2005_household_core_candidate_summary.csv")
    core_ready = next((row.get("value", "0") for row in core_summary if row.get("metric") == "alb2005_household_core_recipe_ready_rows"), "0")
    core_decision = next((row.get("value", "") for row in core_summary if row.get("metric") == "alb2005_household_core_current_decision"), "")
    add(
        rows,
        "evidence",
        "ALB_2005 household core merge audit builds a temp-only candidate and keeps data promotion blocked",
        status(
            counts["alb2005_household_core_candidate"] > 0
            and counts["alb2005_household_core_merge_audit"] > 0
            and counts["alb2005_household_core_lineage"] > 0
            and counts["alb2005_household_core_candidate_summary"] > 0
            and core_ready == "0"
            and core_decision == "temp_candidate_not_analysis_ready"
        ),
        f"candidate_rows={counts['alb2005_household_core_candidate']}; merge_audit_rows={counts['alb2005_household_core_merge_audit']}; lineage_rows={counts['alb2005_household_core_lineage']}; summary_rows={counts['alb2005_household_core_candidate_summary']}; recipe_ready_rows={core_ready}; decision={core_decision}",
        ""
        if counts["alb2005_household_core_candidate"] > 0
        and counts["alb2005_household_core_merge_audit"] > 0
        and counts["alb2005_household_core_lineage"] > 0
        and counts["alb2005_household_core_candidate_summary"] > 0
        and core_ready == "0"
        and core_decision == "temp_candidate_not_analysis_ready"
        else "Run script/47_audit_alb2005_household_core_merge.py and keep the candidate out of data/.",
    )
    provisional_outcome_summary = read_csv_dicts(RESULT_DIR / "alb2005_provisional_outcome_feasibility_summary.csv")
    provisional_ready = next((row.get("value", "0") for row in provisional_outcome_summary if row.get("metric") == "alb2005_provisional_outcome_ready_rows"), "0")
    provisional_decision = next((row.get("value", "") for row in provisional_outcome_summary if row.get("metric") == "alb2005_provisional_outcome_current_decision"), "")
    add(
        rows,
        "evidence",
        "ALB_2005 provisional outcome feasibility audit computes raw event-rate diagnostics and keeps final outcomes blocked",
        status(
            counts["alb2005_provisional_outcome_feasibility_audit"] > 0
            and counts["alb2005_provisional_outcome_feasibility_summary"] > 0
            and provisional_ready == "0"
            and provisional_decision == "not_final_outcomes_timing_geography_recall_blocked"
        ),
        f"audit_rows={counts['alb2005_provisional_outcome_feasibility_audit']}; summary_rows={counts['alb2005_provisional_outcome_feasibility_summary']}; ready_rows={provisional_ready}; decision={provisional_decision}",
        ""
        if counts["alb2005_provisional_outcome_feasibility_audit"] > 0
        and counts["alb2005_provisional_outcome_feasibility_summary"] > 0
        and provisional_ready == "0"
        and provisional_decision == "not_final_outcomes_timing_geography_recall_blocked"
        else "Run script/48_audit_alb2005_provisional_outcome_feasibility.py and keep all provisional outcomes blocked from data/.",
    )
    semantics_summary = read_csv_dicts(RESULT_DIR / "alb2005_outcome_semantics_raw_value_summary.csv")
    semantics_outcome_ready = next((row.get("value", "0") for row in semantics_summary if row.get("metric") == "alb2005_outcome_semantics_outcome_ready_rows"), "0")
    semantics_sdg_ready = next((row.get("value", "0") for row in semantics_summary if row.get("metric") == "alb2005_outcome_semantics_sdg382_ready_rows"), "0")
    semantics_climate_ready = next((row.get("value", "0") for row in semantics_summary if row.get("metric") == "alb2005_outcome_semantics_climate_linkage_ready_rows"), "0")
    semantics_decision = next((row.get("value", "") for row in semantics_summary if row.get("metric") == "alb2005_outcome_semantics_current_decision"), "")
    add(
        rows,
        "evidence",
        "ALB_2005 raw outcome-semantics value audit documents payment, gift, access, and need fields while keeping promotion blocked",
        status(
            counts["alb2005_outcome_semantics_raw_value_audit"] > 0
            and counts["alb2005_outcome_semantics_raw_value_summary"] > 0
            and semantics_outcome_ready == "0"
            and semantics_sdg_ready == "0"
            and semantics_climate_ready == "0"
            and semantics_decision == "blocked_timing_geography_outcome_semantics_units_recall_skip_patterns"
        ),
        f"audit_rows={counts['alb2005_outcome_semantics_raw_value_audit']}; summary_rows={counts['alb2005_outcome_semantics_raw_value_summary']}; outcome_ready={semantics_outcome_ready}; sdg382_ready={semantics_sdg_ready}; climate_ready={semantics_climate_ready}; decision={semantics_decision}",
        ""
        if counts["alb2005_outcome_semantics_raw_value_audit"] > 0
        and counts["alb2005_outcome_semantics_raw_value_summary"] > 0
        and semantics_outcome_ready == "0"
        and semantics_sdg_ready == "0"
        and semantics_climate_ready == "0"
        and semantics_decision == "blocked_timing_geography_outcome_semantics_units_recall_skip_patterns"
        else "Run script/61_audit_alb2005_outcome_semantics_raw_values.py and keep all ALB_2005 outcome, SDG 3.8.2, and climate-linkage promotion blocked.",
    )
    timing_geo_summary = read_csv_dicts(RESULT_DIR / "alb2005_timing_geography_exhaustive_summary.csv")
    timing_geo_ready = next((row.get("value", "0") for row in timing_geo_summary if row.get("metric") == "alb2005_climate_linkage_ready_rows"), "0")
    timing_geo_decision = next((row.get("value", "") for row in timing_geo_summary if row.get("metric") == "alb2005_timing_geography_current_decision"), "")
    add(
        rows,
        "evidence",
        "ALB_2005 timing/geography exhaustive audit scans raw files and keeps climate linkage blocked",
        status(
            counts["alb2005_timing_geography_exhaustive_audit"] > 0
            and counts["alb2005_timing_geography_exhaustive_summary"] > 0
            and timing_geo_ready == "0"
            and timing_geo_decision == "blocked_missing_interview_timing_partial_geography_no_gps"
        ),
        f"audit_rows={counts['alb2005_timing_geography_exhaustive_audit']}; summary_rows={counts['alb2005_timing_geography_exhaustive_summary']}; climate_linkage_ready_rows={timing_geo_ready}; decision={timing_geo_decision}",
        ""
        if counts["alb2005_timing_geography_exhaustive_audit"] > 0
        and counts["alb2005_timing_geography_exhaustive_summary"] > 0
        and timing_geo_ready == "0"
        and timing_geo_decision == "blocked_missing_interview_timing_partial_geography_no_gps"
        else "Run script/49_audit_alb2005_timing_geography_exhaustive.py and keep climate linkage blocked until timing/geography pass.",
    )
    timing_source_summary = read_csv_dicts(RESULT_DIR / "alb2005_timing_geography_source_search_summary.csv")
    timing_source_rows = next((row.get("value", "0") for row in timing_source_summary if row.get("metric") == "alb2005_timing_geography_source_search_rows"), "0")
    timing_source_targets = next((row.get("value", "0") for row in timing_source_summary if row.get("metric") == "alb2005_timing_geography_source_search_target_concepts"), "0")
    timing_source_files = next((row.get("value", "0") for row in timing_source_summary if row.get("metric") == "alb2005_timing_geography_source_search_local_files_scanned"), "0")
    timing_source_variables = next((row.get("value", "0") for row in timing_source_summary if row.get("metric") == "alb2005_timing_geography_source_search_local_variables_scanned"), "0")
    timing_source_workbooks = next((row.get("value", "0") for row in timing_source_summary if row.get("metric") == "alb2005_timing_geography_source_search_questionnaire_workbooks_scanned"), "0")
    timing_source_raw_hits = next((row.get("value", "0") for row in timing_source_summary if row.get("metric") == "alb2005_timing_geography_source_search_raw_targets_with_hits"), "0")
    timing_source_questionnaire_hits = next((row.get("value", "0") for row in timing_source_summary if row.get("metric") == "alb2005_timing_geography_source_search_questionnaire_targets_with_hits"), "0")
    timing_source_legacy_timing = next((row.get("value", "0") for row in timing_source_summary if row.get("metric") == "alb2005_timing_geography_source_search_legacy_questionnaire_timing_rows"), "0")
    timing_source_verified_timing = next((row.get("value", "0") for row in timing_source_summary if row.get("metric") == "alb2005_timing_geography_source_search_verified_household_timing_rows"), "0")
    timing_source_coordinates = next((row.get("value", "0") for row in timing_source_summary if row.get("metric") == "alb2005_timing_geography_source_search_coordinate_candidate_rows"), "0")
    timing_source_partial_district = next((row.get("value", "0") for row in timing_source_summary if row.get("metric") == "alb2005_timing_geography_source_search_partial_district_variable_rows"), "0")
    timing_source_district_name = next((row.get("value", "0") for row in timing_source_summary if row.get("metric") == "alb2005_timing_geography_source_search_partial_district_name_nonmissing_rows"), "0")
    timing_source_district_code = next((row.get("value", "0") for row in timing_source_summary if row.get("metric") == "alb2005_timing_geography_source_search_partial_district_code_nonmissing_rows"), "0")
    timing_source_required_timing = next((row.get("value", "0") for row in timing_source_summary if row.get("metric") == "alb2005_timing_geography_source_search_required_value_key_timing_rows"), "0")
    timing_source_required_coordinate = next((row.get("value", "0") for row in timing_source_summary if row.get("metric") == "alb2005_timing_geography_source_search_required_value_key_coordinate_rows"), "0")
    timing_source_geo_ready = next((row.get("value", "0") for row in timing_source_summary if row.get("metric") == "alb2005_timing_geography_source_search_geography_crosswalk_ready_rows"), "0")
    timing_source_interview_ready = next((row.get("value", "0") for row in timing_source_summary if row.get("metric") == "alb2005_timing_geography_source_search_interview_timing_ready_rows"), "0")
    timing_source_climate = next((row.get("value", "0") for row in timing_source_summary if row.get("metric") == "alb2005_timing_geography_source_search_climate_linkage_ready_rows"), "0")
    timing_source_decision = next((row.get("value", "") for row in timing_source_summary if row.get("metric") == "alb2005_timing_geography_source_search_current_decision"), "")
    add(
        rows,
        "evidence",
        "ALB_2005 timing/geography source-search audit triangulates raw/schema/questionnaire leads while keeping climate linkage blocked",
        status(
            counts["alb2005_timing_geography_source_search_audit"] > 0
            and counts["alb2005_timing_geography_source_search_summary"] > 0
            and safe_int(timing_source_rows) > 0
            and safe_int(timing_source_targets) == 5
            and safe_int(timing_source_files) > 0
            and safe_int(timing_source_variables) > 0
            and safe_int(timing_source_workbooks) > 0
            and safe_int(timing_source_raw_hits) > 0
            and safe_int(timing_source_questionnaire_hits) == 5
            and safe_int(timing_source_legacy_timing) > 0
            and timing_source_verified_timing == "0"
            and timing_source_coordinates == "0"
            and safe_int(timing_source_partial_district) > 0
            and safe_int(timing_source_district_name) > 0
            and safe_int(timing_source_district_code) > 0
            and timing_source_required_timing == "0"
            and timing_source_required_coordinate == "0"
            and timing_source_geo_ready == "0"
            and timing_source_interview_ready == "0"
            and timing_source_climate == "0"
            and timing_source_decision == "blocked_alb2005_timing_geography_source_search_not_ready"
        ),
        f"audit_rows={counts['alb2005_timing_geography_source_search_audit']}; summary_rows={counts['alb2005_timing_geography_source_search_summary']}; rows={timing_source_rows}; target_concepts={timing_source_targets}; local_files={timing_source_files}; local_variables={timing_source_variables}; workbooks={timing_source_workbooks}; raw_targets_with_hits={timing_source_raw_hits}; questionnaire_targets_with_hits={timing_source_questionnaire_hits}; legacy_timing_rows={timing_source_legacy_timing}; verified_timing_rows={timing_source_verified_timing}; coordinate_candidates={timing_source_coordinates}; partial_district_variables={timing_source_partial_district}; district_name_rows={timing_source_district_name}; district_code_rows={timing_source_district_code}; required_timing_rows={timing_source_required_timing}; required_coordinate_rows={timing_source_required_coordinate}; geography_ready_rows={timing_source_geo_ready}; interview_timing_ready_rows={timing_source_interview_ready}; climate_ready_rows={timing_source_climate}; decision={timing_source_decision}",
        ""
        if counts["alb2005_timing_geography_source_search_audit"] > 0
        and counts["alb2005_timing_geography_source_search_summary"] > 0
        and timing_source_verified_timing == "0"
        and timing_source_coordinates == "0"
        and timing_source_geo_ready == "0"
        and timing_source_interview_ready == "0"
        and timing_source_climate == "0"
        and timing_source_decision == "blocked_alb2005_timing_geography_source_search_not_ready"
        else "Run script/78_audit_alb2005_timing_geography_source_search.py and keep ALB_2005 climate promotion blocked.",
    )
    value_decision_summary = read_csv_dicts(RESULT_DIR / "alb2005_harmonization_value_decision_summary.csv")
    value_decision_ready = next((row.get("value", "0") for row in value_decision_summary if row.get("metric") == "alb2005_harmonization_value_decision_recipe_ready_rows"), "0")
    value_decision_required_blocked = next((row.get("value", "0") for row in value_decision_summary if row.get("metric") == "alb2005_harmonization_value_decision_required_blocked_rows"), "0")
    value_decision_current = next((row.get("value", "") for row in value_decision_summary if row.get("metric") == "alb2005_harmonization_value_decision_current_decision"), "")
    add(
        rows,
        "evidence",
        "ALB_2005 harmonization value decision audit classifies gate blockers without recipe promotion",
        status(
            counts["alb2005_harmonization_value_decision_audit"] > 0
            and counts["alb2005_harmonization_value_decision_summary"] > 0
            and value_decision_ready == "0"
            and safe_int(value_decision_required_blocked) > 0
            and value_decision_current == "blocked_no_alb2005_value_decision_ready_for_recipe"
        ),
        f"audit_rows={counts['alb2005_harmonization_value_decision_audit']}; summary_rows={counts['alb2005_harmonization_value_decision_summary']}; recipe_ready_rows={value_decision_ready}; required_blocked_rows={value_decision_required_blocked}; decision={value_decision_current}",
        ""
        if counts["alb2005_harmonization_value_decision_audit"] > 0
        and counts["alb2005_harmonization_value_decision_summary"] > 0
        and value_decision_ready == "0"
        and safe_int(value_decision_required_blocked) > 0
        and value_decision_current == "blocked_no_alb2005_value_decision_ready_for_recipe"
        else "Run script/68_build_alb2005_harmonization_value_decision_audit.py and keep ALB_2005 recipe promotion blocked.",
    )
    minimum_recipe_summary = read_csv_dicts(RESULT_DIR / "alb2005_minimum_recipe_promotion_summary.csv")
    minimum_recipe_actions = next((row.get("value", "0") for row in minimum_recipe_summary if row.get("metric") == "alb2005_minimum_recipe_promotion_action_rows"), "0")
    minimum_recipe_gates = next((row.get("value", "0") for row in minimum_recipe_summary if row.get("metric") == "alb2005_minimum_recipe_promotion_gate_rows"), "0")
    minimum_recipe_blocked = next((row.get("value", "0") for row in minimum_recipe_summary if row.get("metric") == "alb2005_minimum_recipe_promotion_blocked_gates"), "0")
    minimum_recipe_harmonized_ready = next((row.get("value", "0") for row in minimum_recipe_summary if row.get("metric") == "alb2005_minimum_recipe_promotion_harmonized_ready_rows"), "0")
    minimum_recipe_outcome_ready = next((row.get("value", "0") for row in minimum_recipe_summary if row.get("metric") == "alb2005_minimum_recipe_promotion_outcome_ready_rows"), "0")
    minimum_recipe_climate_ready = next((row.get("value", "0") for row in minimum_recipe_summary if row.get("metric") == "alb2005_minimum_recipe_promotion_climate_linkage_ready_rows"), "0")
    minimum_recipe_decision = next((row.get("value", "") for row in minimum_recipe_summary if row.get("metric") == "alb2005_minimum_recipe_promotion_current_decision"), "")
    add(
        rows,
        "evidence",
        "ALB_2005 minimum recipe promotion packet maps the raw-ready temp candidate to explicit harmonization, outcome, and climate gates",
        status(
            counts["alb2005_minimum_recipe_promotion_action_queue"] > 0
            and counts["alb2005_minimum_recipe_promotion_gate_checklist"] > 0
            and counts["alb2005_minimum_recipe_promotion_summary"] > 0
            and minimum_recipe_actions == "6"
            and minimum_recipe_gates == "10"
            and safe_int(minimum_recipe_blocked) > 0
            and minimum_recipe_harmonized_ready == "0"
            and minimum_recipe_outcome_ready == "0"
            and minimum_recipe_climate_ready == "0"
            and minimum_recipe_decision == "blocked_alb2005_minimum_recipe_not_ready_for_promotion"
        ),
        f"action_rows={counts['alb2005_minimum_recipe_promotion_action_queue']}; gate_rows={counts['alb2005_minimum_recipe_promotion_gate_checklist']}; summary_rows={counts['alb2005_minimum_recipe_promotion_summary']}; summary_actions={minimum_recipe_actions}; summary_gates={minimum_recipe_gates}; blocked_gates={minimum_recipe_blocked}; harmonized_ready={minimum_recipe_harmonized_ready}; outcome_ready={minimum_recipe_outcome_ready}; climate_ready={minimum_recipe_climate_ready}; decision={minimum_recipe_decision}",
        ""
        if counts["alb2005_minimum_recipe_promotion_action_queue"] > 0
        and counts["alb2005_minimum_recipe_promotion_gate_checklist"] > 0
        and counts["alb2005_minimum_recipe_promotion_summary"] > 0
        and minimum_recipe_harmonized_ready == "0"
        and minimum_recipe_outcome_ready == "0"
        and minimum_recipe_climate_ready == "0"
        and minimum_recipe_decision == "blocked_alb2005_minimum_recipe_not_ready_for_promotion"
        else "Run script/83_build_alb2005_minimum_recipe_promotion_packet.py and keep ALB_2005 in temp-only status until minimum recipe gates pass.",
    )
    public_fieldwork_geo_summary = read_csv_dicts(RESULT_DIR / "alb2005_public_fieldwork_geo_metadata_summary.csv")
    public_fieldwork_geo_evidence = next((row.get("value", "0") for row in public_fieldwork_geo_summary if row.get("metric") == "alb2005_public_fieldwork_geo_metadata_evidence_rows"), "0")
    public_fieldwork_geo_verified = next((row.get("value", "0") for row in public_fieldwork_geo_summary if row.get("metric") == "alb2005_public_fieldwork_geo_metadata_verified_source_rows"), "0")
    public_fieldwork_geo_missing = next((row.get("value", "0") for row in public_fieldwork_geo_summary if row.get("metric") == "alb2005_public_fieldwork_geo_metadata_source_missing_rows"), "0")
    public_fieldwork_geo_timing = next((row.get("value", "0") for row in public_fieldwork_geo_summary if row.get("metric") == "alb2005_public_fieldwork_geo_metadata_household_timing_verified_rows"), "0")
    public_fieldwork_geo_coordinates = next((row.get("value", "0") for row in public_fieldwork_geo_summary if row.get("metric") == "alb2005_public_fieldwork_geo_metadata_raw_coordinate_value_rows"), "0")
    public_fieldwork_geo_climate = next((row.get("value", "0") for row in public_fieldwork_geo_summary if row.get("metric") == "alb2005_public_fieldwork_geo_metadata_climate_linkage_ready_rows"), "0")
    public_fieldwork_geo_decision = next((row.get("value", "") for row in public_fieldwork_geo_summary if row.get("metric") == "alb2005_public_fieldwork_geo_metadata_current_decision"), "")
    add(
        rows,
        "evidence",
        "ALB_2005 public fieldwork/geography metadata audit verifies source context while keeping climate linkage blocked",
        status(
            counts["alb2005_public_fieldwork_geo_metadata_audit"] > 0
            and counts["alb2005_public_fieldwork_geo_metadata_summary"] > 0
            and public_fieldwork_geo_evidence == "10"
            and public_fieldwork_geo_verified == "10"
            and public_fieldwork_geo_missing == "0"
            and public_fieldwork_geo_timing == "0"
            and public_fieldwork_geo_coordinates == "0"
            and public_fieldwork_geo_climate == "0"
            and public_fieldwork_geo_decision == "blocked_public_metadata_not_household_climate_linkage_ready"
        ),
        f"audit_rows={counts['alb2005_public_fieldwork_geo_metadata_audit']}; summary_rows={counts['alb2005_public_fieldwork_geo_metadata_summary']}; evidence_rows={public_fieldwork_geo_evidence}; verified_source_rows={public_fieldwork_geo_verified}; source_missing_rows={public_fieldwork_geo_missing}; household_timing_verified_rows={public_fieldwork_geo_timing}; raw_coordinate_value_rows={public_fieldwork_geo_coordinates}; climate_ready_rows={public_fieldwork_geo_climate}; decision={public_fieldwork_geo_decision}",
        ""
        if counts["alb2005_public_fieldwork_geo_metadata_audit"] > 0
        and counts["alb2005_public_fieldwork_geo_metadata_summary"] > 0
        and public_fieldwork_geo_verified == "10"
        and public_fieldwork_geo_missing == "0"
        and public_fieldwork_geo_timing == "0"
        and public_fieldwork_geo_coordinates == "0"
        and public_fieldwork_geo_climate == "0"
        and public_fieldwork_geo_decision == "blocked_public_metadata_not_household_climate_linkage_ready"
        else "Run script/84_audit_alb2005_public_fieldwork_geo_metadata.py and keep public timing/GPS metadata separate from climate-linkage promotion.",
    )
    diary_timing_summary = read_csv_dicts(RESULT_DIR / "alb2005_diary_timing_candidate_summary.csv")
    diary_timing_rows = next((row.get("value", "0") for row in diary_timing_summary if row.get("metric") == "alb2005_diary_timing_candidate_audit_rows"), "0")
    diary_timing_metadata = next((row.get("value", "0") for row in diary_timing_summary if row.get("metric") == "alb2005_diary_timing_candidate_metadata_found_rows"), "0")
    diary_timing_schema_rows = next((row.get("value", "0") for row in diary_timing_summary if row.get("metric") == "alb2005_diary_timing_candidate_schema_file_rows"), "0")
    diary_timing_raw_present = next((row.get("value", "0") for row in diary_timing_summary if row.get("metric") == "alb2005_diary_timing_candidate_raw_bookmetadata_files_present"), "0")
    diary_timing_date_candidates = next((row.get("value", "0") for row in diary_timing_summary if row.get("metric") == "alb2005_diary_timing_candidate_date_candidate_rows"), "0")
    diary_timing_promoted = next((row.get("value", "0") for row in diary_timing_summary if row.get("metric") == "alb2005_diary_timing_candidate_household_timing_promoted_rows"), "0")
    diary_timing_climate = next((row.get("value", "0") for row in diary_timing_summary if row.get("metric") == "alb2005_diary_timing_candidate_climate_linkage_ready_rows"), "0")
    diary_timing_decision = next((row.get("value", "") for row in diary_timing_summary if row.get("metric") == "alb2005_diary_timing_candidate_current_decision"), "")
    add(
        rows,
        "evidence",
        "ALB_2005 diary timing candidate audit records bookmetadata date/key candidates without promoting household timing",
        status(
            counts["alb2005_diary_timing_candidate_audit"] > 0
            and counts["alb2005_diary_timing_candidate_summary"] > 0
            and diary_timing_rows == "11"
            and diary_timing_metadata == "11"
            and safe_int(diary_timing_schema_rows) > 0
            and diary_timing_raw_present == "0"
            and safe_int(diary_timing_date_candidates) > 0
            and diary_timing_promoted == "0"
            and diary_timing_climate == "0"
            and diary_timing_decision == "blocked_diary_timing_metadata_candidate_no_raw_merge_semantics"
        ),
        f"audit_rows={counts['alb2005_diary_timing_candidate_audit']}; summary_rows={counts['alb2005_diary_timing_candidate_summary']}; candidate_rows={diary_timing_rows}; metadata_found_rows={diary_timing_metadata}; schema_rows={diary_timing_schema_rows}; raw_bookmetadata_present={diary_timing_raw_present}; date_candidate_rows={diary_timing_date_candidates}; household_timing_promoted_rows={diary_timing_promoted}; climate_ready_rows={diary_timing_climate}; decision={diary_timing_decision}",
        ""
        if counts["alb2005_diary_timing_candidate_audit"] > 0
        and counts["alb2005_diary_timing_candidate_summary"] > 0
        and diary_timing_rows == "11"
        and diary_timing_raw_present == "0"
        and diary_timing_promoted == "0"
        and diary_timing_climate == "0"
        and diary_timing_decision == "blocked_diary_timing_metadata_candidate_no_raw_merge_semantics"
        else "Run script/85_audit_alb2005_diary_timing_candidates.py and keep diary timing candidates out of climate linkage until raw values and merge semantics pass.",
    )
    extracted_module_summary = read_csv_dicts(RESULT_DIR / "alb2005_extracted_module_coverage_summary.csv")
    extracted_modules = next((row.get("value", "0") for row in extracted_module_summary if row.get("metric") == "alb2005_extracted_module_coverage_ddi_module_rows"), "0")
    extracted_present = next((row.get("value", "0") for row in extracted_module_summary if row.get("metric") == "alb2005_extracted_module_coverage_present_rows"), "0")
    extracted_missing = next((row.get("value", "0") for row in extracted_module_summary if row.get("metric") == "alb2005_extracted_module_coverage_missing_rows"), "0")
    extracted_archive_members = next((row.get("value", "0") for row in extracted_module_summary if row.get("metric") == "alb2005_archive_member_rows"), "0")
    extracted_archive_sav = next((row.get("value", "0") for row in extracted_module_summary if row.get("metric") == "alb2005_archive_sav_member_rows"), "0")
    extracted_archive_questionnaires = next((row.get("value", "0") for row in extracted_module_summary if row.get("metric") == "alb2005_archive_questionnaire_member_rows"), "0")
    extracted_archive_present = next((row.get("value", "0") for row in extracted_module_summary if row.get("metric") == "alb2005_archive_ddi_module_present_rows"), "0")
    extracted_archive_absent = next((row.get("value", "0") for row in extracted_module_summary if row.get("metric") == "alb2005_archive_ddi_module_absent_rows"), "0")
    extracted_archive_critical_absent = next((row.get("value", "0") for row in extracted_module_summary if row.get("metric") == "alb2005_archive_critical_module_absent_rows"), "0")
    extracted_archive_listing_status = next((row.get("value", "") for row in extracted_module_summary if row.get("metric") == "alb2005_archive_listing_status"), "")
    extracted_bookmetadata_missing = next((row.get("value", "0") for row in extracted_module_summary if row.get("metric") == "alb2005_extracted_module_coverage_bookmetadata_missing_rows"), "0")
    extracted_critical_missing = next((row.get("value", "0") for row in extracted_module_summary if row.get("metric") == "alb2005_extracted_module_coverage_critical_missing_rows"), "0")
    extracted_coordinate_vars = next((row.get("value", "0") for row in extracted_module_summary if row.get("metric") == "alb2005_extracted_module_coverage_coordinate_metadata_variable_rows"), "0")
    extracted_coordinate_files = next((row.get("value", "0") for row in extracted_module_summary if row.get("metric") == "alb2005_extracted_module_coverage_coordinate_extracted_file_rows"), "0")
    extracted_harmonized_ready = next((row.get("value", "0") for row in extracted_module_summary if row.get("metric") == "alb2005_extracted_module_coverage_harmonized_ready_rows"), "0")
    extracted_timing_ready = next((row.get("value", "0") for row in extracted_module_summary if row.get("metric") == "alb2005_extracted_module_coverage_household_timing_ready_rows"), "0")
    extracted_climate_ready = next((row.get("value", "0") for row in extracted_module_summary if row.get("metric") == "alb2005_extracted_module_coverage_climate_linkage_ready_rows"), "0")
    extracted_decision = next((row.get("value", "") for row in extracted_module_summary if row.get("metric") == "alb2005_extracted_module_coverage_current_decision"), "")
    add(
        rows,
        "evidence",
        "ALB_2005 extracted module coverage audit documents DDI modules missing from the local archive manifest and extracted package",
        status(
            counts["alb2005_extracted_module_coverage_audit"] > 0
            and counts["alb2005_extracted_extra_files_audit"] > 0
            and counts["alb2005_archive_member_manifest"] > 0
            and counts["alb2005_extracted_module_coverage_summary"] > 0
            and extracted_modules == "68"
            and safe_int(extracted_present) > 0
            and safe_int(extracted_missing) > 0
            and extracted_archive_members == "61"
            and extracted_archive_sav == "44"
            and extracted_archive_questionnaires == "2"
            and safe_int(extracted_archive_present) > 0
            and safe_int(extracted_archive_absent) > 0
            and safe_int(extracted_archive_critical_absent) > 0
            and extracted_archive_listing_status == "tar_listing_available"
            and extracted_bookmetadata_missing == "1"
            and safe_int(extracted_critical_missing) > 0
            and extracted_coordinate_vars == "0"
            and extracted_coordinate_files == "0"
            and extracted_harmonized_ready == "0"
            and extracted_timing_ready == "0"
            and extracted_climate_ready == "0"
            and extracted_decision == "blocked_extracted_package_missing_bookmetadata_and_coordinate_values"
        ),
        f"audit_rows={counts['alb2005_extracted_module_coverage_audit']}; extra_rows={counts['alb2005_extracted_extra_files_audit']}; archive_manifest_rows={counts['alb2005_archive_member_manifest']}; summary_rows={counts['alb2005_extracted_module_coverage_summary']}; ddi_modules={extracted_modules}; present={extracted_present}; missing={extracted_missing}; archive_members={extracted_archive_members}; archive_sav={extracted_archive_sav}; archive_questionnaires={extracted_archive_questionnaires}; archive_present={extracted_archive_present}; archive_absent={extracted_archive_absent}; archive_critical_absent={extracted_archive_critical_absent}; archive_listing={extracted_archive_listing_status}; bookmetadata_missing={extracted_bookmetadata_missing}; critical_missing={extracted_critical_missing}; coordinate_vars={extracted_coordinate_vars}; coordinate_files={extracted_coordinate_files}; harmonized_ready={extracted_harmonized_ready}; timing_ready={extracted_timing_ready}; climate_ready={extracted_climate_ready}; decision={extracted_decision}",
        ""
        if counts["alb2005_extracted_module_coverage_audit"] > 0
        and counts["alb2005_archive_member_manifest"] > 0
        and counts["alb2005_extracted_module_coverage_summary"] > 0
        and extracted_archive_members == "61"
        and extracted_archive_sav == "44"
        and extracted_archive_listing_status == "tar_listing_available"
        and extracted_bookmetadata_missing == "1"
        and extracted_coordinate_vars == "0"
        and extracted_coordinate_files == "0"
        and extracted_harmonized_ready == "0"
        and extracted_timing_ready == "0"
        and extracted_climate_ready == "0"
        and extracted_decision == "blocked_extracted_package_missing_bookmetadata_and_coordinate_values"
        else "Run script/86_audit_alb2005_extracted_module_coverage.py and keep ALB_2005 timing/climate promotion blocked until missing modules or substitutes are obtained.",
    )
    fallback_summary = read_csv_dicts(RESULT_DIR / "alb2005_fallback_blocker_resolution_summary.csv")
    fallback_rows = next((row.get("value", "0") for row in fallback_summary if row.get("metric") == "alb2005_fallback_blocker_resolution_rows"), "0")
    fallback_raw_package = next((row.get("value", "0") for row in fallback_summary if row.get("metric") == "alb2005_fallback_blocker_raw_package_rows"), "0")
    fallback_timing = next((row.get("value", "0") for row in fallback_summary if row.get("metric") == "alb2005_fallback_blocker_timing_rows"), "0")
    fallback_geography = next((row.get("value", "0") for row in fallback_summary if row.get("metric") == "alb2005_fallback_blocker_geography_rows"), "0")
    fallback_outcome = next((row.get("value", "0") for row in fallback_summary if row.get("metric") == "alb2005_fallback_blocker_outcome_rows"), "0")
    fallback_promotion = next((row.get("value", "0") for row in fallback_summary if row.get("metric") == "alb2005_fallback_blocker_promotion_gate_rows"), "0")
    fallback_hard_blocked = next((row.get("value", "0") for row in fallback_summary if row.get("metric") == "alb2005_fallback_blocker_hard_blocked_rows"), "0")
    fallback_harmonized_ready = next((row.get("value", "0") for row in fallback_summary if row.get("metric") == "alb2005_fallback_blocker_harmonized_ready_rows"), "0")
    fallback_outcome_ready = next((row.get("value", "0") for row in fallback_summary if row.get("metric") == "alb2005_fallback_blocker_outcome_ready_rows"), "0")
    fallback_timing_ready = next((row.get("value", "0") for row in fallback_summary if row.get("metric") == "alb2005_fallback_blocker_interview_timing_ready_rows"), "0")
    fallback_geography_ready = next((row.get("value", "0") for row in fallback_summary if row.get("metric") == "alb2005_fallback_blocker_geography_ready_rows"), "0")
    fallback_climate_ready = next((row.get("value", "0") for row in fallback_summary if row.get("metric") == "alb2005_fallback_blocker_climate_linkage_ready_rows"), "0")
    fallback_data_ready = next((row.get("value", "0") for row in fallback_summary if row.get("metric") == "alb2005_fallback_blocker_data_write_ready_rows"), "0")
    fallback_decision = next((row.get("value", "") for row in fallback_summary if row.get("metric") == "alb2005_fallback_blocker_current_decision"), "")
    add(
        rows,
        "evidence",
        "ALB_2005 fallback blocker resolution matrix consolidates source, timing, geography, outcome, and promotion stop rules without promoting data",
        status(
            counts["alb2005_fallback_blocker_resolution_matrix"] == 12
            and counts["alb2005_fallback_blocker_resolution_summary"] == 14
            and fallback_rows == "12"
            and fallback_raw_package == "1"
            and fallback_timing == "3"
            and fallback_geography == "2"
            and fallback_outcome == "3"
            and fallback_promotion == "3"
            and fallback_hard_blocked == "12"
            and fallback_harmonized_ready == "0"
            and fallback_outcome_ready == "0"
            and fallback_timing_ready == "0"
            and fallback_geography_ready == "0"
            and fallback_climate_ready == "0"
            and fallback_data_ready == "0"
            and fallback_decision == "blocked_alb2005_no_fallback_ready"
        ),
        f"matrix_rows={counts['alb2005_fallback_blocker_resolution_matrix']}; summary_rows={counts['alb2005_fallback_blocker_resolution_summary']}; summary_matrix_rows={fallback_rows}; raw_package={fallback_raw_package}; timing={fallback_timing}; geography={fallback_geography}; outcome={fallback_outcome}; promotion_gate={fallback_promotion}; hard_blocked={fallback_hard_blocked}; harmonized_ready={fallback_harmonized_ready}; outcome_ready={fallback_outcome_ready}; timing_ready={fallback_timing_ready}; geography_ready={fallback_geography_ready}; climate_ready={fallback_climate_ready}; data_ready={fallback_data_ready}; decision={fallback_decision}",
        ""
        if counts["alb2005_fallback_blocker_resolution_matrix"] == 12
        and counts["alb2005_fallback_blocker_resolution_summary"] == 14
        and fallback_hard_blocked == "12"
        and fallback_harmonized_ready == "0"
        and fallback_outcome_ready == "0"
        and fallback_timing_ready == "0"
        and fallback_geography_ready == "0"
        and fallback_climate_ready == "0"
        and fallback_data_ready == "0"
        and fallback_decision == "blocked_alb2005_no_fallback_ready"
        else "Run script/115_build_alb2005_fallback_blocker_resolution_matrix.py and keep ALB_2005 out of fallback promotion until source, timing, geography, and outcome gates pass.",
    )
    required_value_key_summary = read_csv_dicts(RESULT_DIR / "alb2005_required_value_key_summary.csv")
    required_value_key_ready = next((row.get("value", "0") for row in required_value_key_summary if row.get("metric") == "alb2005_required_value_key_recipe_ready_rows"), "0")
    required_value_key_not_promoted = next((row.get("value", "0") for row in required_value_key_summary if row.get("metric") == "alb2005_required_value_key_not_promoted_rows"), "0")
    required_value_key_timing = next((row.get("value", "0") for row in required_value_key_summary if row.get("metric") == "alb2005_required_value_key_interview_timing_verified_rows"), "0")
    required_value_key_coordinate = next((row.get("value", "0") for row in required_value_key_summary if row.get("metric") == "alb2005_required_value_key_coordinate_ready_rows"), "0")
    required_value_key_climate = next((row.get("value", "0") for row in required_value_key_summary if row.get("metric") == "alb2005_required_value_key_climate_linkage_ready_rows"), "0")
    required_value_key_decision = next((row.get("value", "") for row in required_value_key_summary if row.get("metric") == "alb2005_required_value_key_current_decision"), "")
    add(
        rows,
        "evidence",
        "ALB_2005 required value/key audit records raw value evidence while keeping recipe and climate promotion blocked",
        status(
            counts["alb2005_required_value_key_audit"] > 0
            and counts["alb2005_required_value_key_summary"] > 0
            and required_value_key_ready == "0"
            and safe_int(required_value_key_not_promoted) > 0
            and required_value_key_timing == "0"
            and required_value_key_coordinate == "0"
            and required_value_key_climate == "0"
            and required_value_key_decision == "blocked_alb2005_required_values_seen_but_recipe_not_ready"
        ),
        f"audit_rows={counts['alb2005_required_value_key_audit']}; summary_rows={counts['alb2005_required_value_key_summary']}; recipe_ready_rows={required_value_key_ready}; not_promoted_rows={required_value_key_not_promoted}; interview_timing_verified_rows={required_value_key_timing}; coordinate_ready_rows={required_value_key_coordinate}; climate_ready_rows={required_value_key_climate}; decision={required_value_key_decision}",
        ""
        if counts["alb2005_required_value_key_audit"] > 0
        and counts["alb2005_required_value_key_summary"] > 0
        and required_value_key_ready == "0"
        and safe_int(required_value_key_not_promoted) > 0
        and required_value_key_timing == "0"
        and required_value_key_coordinate == "0"
        and required_value_key_climate == "0"
        and required_value_key_decision == "blocked_alb2005_required_values_seen_but_recipe_not_ready"
        else "Run script/71_audit_alb2005_required_value_key_evidence.py and keep ALB_2005 recipe/climate promotion blocked.",
    )
    health_questionnaire_summary = read_csv_dicts(RESULT_DIR / "alb2005_health_questionnaire_semantics_summary.csv")
    health_questionnaire_oop = next((row.get("value", "0") for row in health_questionnaire_summary if row.get("metric") == "alb2005_health_questionnaire_oop_item_rows"), "0")
    health_questionnaire_old_lek = next((row.get("value", "0") for row in health_questionnaire_summary if row.get("metric") == "alb2005_health_questionnaire_old_lek_unit_rows"), "0")
    health_questionnaire_access = next((row.get("value", "0") for row in health_questionnaire_summary if row.get("metric") == "alb2005_health_questionnaire_access_rows"), "0")
    health_questionnaire_ready = next((row.get("value", "0") for row in health_questionnaire_summary if row.get("metric") == "alb2005_health_questionnaire_recipe_ready_rows"), "0")
    health_questionnaire_outcome = next((row.get("value", "0") for row in health_questionnaire_summary if row.get("metric") == "alb2005_health_questionnaire_outcome_ready_rows"), "0")
    health_questionnaire_climate = next((row.get("value", "0") for row in health_questionnaire_summary if row.get("metric") == "alb2005_health_questionnaire_climate_linkage_ready_rows"), "0")
    health_questionnaire_decision = next((row.get("value", "") for row in health_questionnaire_summary if row.get("metric") == "alb2005_health_questionnaire_current_decision"), "")
    add(
        rows,
        "evidence",
        "ALB_2005 health questionnaire semantics audit records OOP/access documentation while keeping recipe, outcome, and climate promotion blocked",
        status(
            counts["alb2005_health_questionnaire_semantics_audit"] > 0
            and counts["alb2005_health_questionnaire_semantics_summary"] > 0
            and safe_int(health_questionnaire_oop) > 0
            and safe_int(health_questionnaire_old_lek) > 0
            and safe_int(health_questionnaire_access) > 0
            and health_questionnaire_ready == "0"
            and health_questionnaire_outcome == "0"
            and health_questionnaire_climate == "0"
            and health_questionnaire_decision == "blocked_alb2005_questionnaire_semantics_seen_but_recipe_not_ready"
        ),
        f"audit_rows={counts['alb2005_health_questionnaire_semantics_audit']}; summary_rows={counts['alb2005_health_questionnaire_semantics_summary']}; oop_item_rows={health_questionnaire_oop}; old_lek_rows={health_questionnaire_old_lek}; access_rows={health_questionnaire_access}; recipe_ready_rows={health_questionnaire_ready}; outcome_ready_rows={health_questionnaire_outcome}; climate_ready_rows={health_questionnaire_climate}; decision={health_questionnaire_decision}",
        ""
        if counts["alb2005_health_questionnaire_semantics_audit"] > 0
        and counts["alb2005_health_questionnaire_semantics_summary"] > 0
        and safe_int(health_questionnaire_oop) > 0
        and safe_int(health_questionnaire_old_lek) > 0
        and safe_int(health_questionnaire_access) > 0
        and health_questionnaire_ready == "0"
        and health_questionnaire_outcome == "0"
        and health_questionnaire_climate == "0"
        and health_questionnaire_decision == "blocked_alb2005_questionnaire_semantics_seen_but_recipe_not_ready"
        else "Run script/72_audit_alb2005_health_questionnaire_semantics.py and keep ALB_2005 recipe/outcome/climate promotion blocked.",
    )
    oop_policy_summary = read_csv_dicts(RESULT_DIR / "alb2005_oop_aggregation_policy_summary.csv")
    oop_policy_rows = next((row.get("value", "0") for row in oop_policy_summary if row.get("metric") == "alb2005_oop_aggregation_policy_rows"), "0")
    oop_policy_q_oop = next((row.get("value", "0") for row in oop_policy_summary if row.get("metric") == "alb2005_oop_aggregation_policy_questionnaire_oop_item_rows_observed"), "0")
    oop_policy_q_old_lek = next((row.get("value", "0") for row in oop_policy_summary if row.get("metric") == "alb2005_oop_aggregation_policy_questionnaire_old_lek_rows_observed"), "0")
    oop_policy_outcome = next((row.get("value", "0") for row in oop_policy_summary if row.get("metric") == "alb2005_oop_aggregation_policy_outcome_ready_rows"), "0")
    oop_policy_recipe = next((row.get("value", "0") for row in oop_policy_summary if row.get("metric") == "alb2005_oop_aggregation_policy_recipe_ready_rows"), "0")
    oop_policy_climate = next((row.get("value", "0") for row in oop_policy_summary if row.get("metric") == "alb2005_oop_aggregation_policy_climate_linkage_ready_rows"), "0")
    oop_policy_decision = next((row.get("value", "") for row in oop_policy_summary if row.get("metric") == "alb2005_oop_aggregation_policy_current_decision"), "")
    add(
        rows,
        "evidence",
        "ALB_2005 OOP aggregation policy audit stress-tests payment-scope choices while keeping outcome, recipe, and climate promotion blocked",
        status(
            counts["alb2005_oop_aggregation_policy_audit"] > 0
            and counts["alb2005_oop_aggregation_policy_summary"] > 0
            and safe_int(oop_policy_rows) > 0
            and safe_int(oop_policy_q_oop) > 0
            and safe_int(oop_policy_q_old_lek) > 0
            and oop_policy_outcome == "0"
            and oop_policy_recipe == "0"
            and oop_policy_climate == "0"
            and oop_policy_decision == "blocked_alb2005_oop_aggregation_policy_stress_test_not_outcome_ready"
        ),
        f"audit_rows={counts['alb2005_oop_aggregation_policy_audit']}; summary_rows={counts['alb2005_oop_aggregation_policy_summary']}; policy_rows={oop_policy_rows}; questionnaire_oop_rows={oop_policy_q_oop}; old_lek_rows={oop_policy_q_old_lek}; outcome_ready_rows={oop_policy_outcome}; recipe_ready_rows={oop_policy_recipe}; climate_ready_rows={oop_policy_climate}; decision={oop_policy_decision}",
        ""
        if counts["alb2005_oop_aggregation_policy_audit"] > 0
        and counts["alb2005_oop_aggregation_policy_summary"] > 0
        and safe_int(oop_policy_rows) > 0
        and safe_int(oop_policy_q_oop) > 0
        and safe_int(oop_policy_q_old_lek) > 0
        and oop_policy_outcome == "0"
        and oop_policy_recipe == "0"
        and oop_policy_climate == "0"
        and oop_policy_decision == "blocked_alb2005_oop_aggregation_policy_stress_test_not_outcome_ready"
        else "Run script/73_audit_alb2005_oop_aggregation_policy.py and keep ALB_2005 outcome/recipe/climate promotion blocked.",
    )
    skip_missing_summary = read_csv_dicts(RESULT_DIR / "alb2005_skip_missing_semantics_summary.csv")
    skip_missing_rows = next((row.get("value", "0") for row in skip_missing_summary if row.get("metric") == "alb2005_skip_missing_semantics_rows"), "0")
    skip_missing_payment_leaks = next((row.get("value", "0") for row in skip_missing_summary if row.get("metric") == "alb2005_skip_missing_payment_nonmissing_when_not_triggered_rows"), "0")
    skip_missing_payment_positive_leaks = next((row.get("value", "0") for row in skip_missing_summary if row.get("metric") == "alb2005_skip_missing_payment_positive_when_not_triggered_rows"), "0")
    skip_missing_condition_leaks = next((row.get("value", "0") for row in skip_missing_summary if row.get("metric") == "alb2005_skip_missing_condition_nonmissing_when_not_triggered_rows"), "0")
    skip_missing_condition_missing = next((row.get("value", "0") for row in skip_missing_summary if row.get("metric") == "alb2005_skip_missing_condition_missing_when_triggered_rows"), "0")
    skip_missing_financing_leaks = next((row.get("value", "0") for row in skip_missing_summary if row.get("metric") == "alb2005_skip_missing_financing_nonmissing_when_not_triggered_rows"), "0")
    skip_missing_financing_missing = next((row.get("value", "0") for row in skip_missing_summary if row.get("metric") == "alb2005_skip_missing_financing_missing_when_triggered_rows"), "0")
    skip_missing_recipe = next((row.get("value", "0") for row in skip_missing_summary if row.get("metric") == "alb2005_skip_missing_recipe_ready_rows"), "0")
    skip_missing_outcome = next((row.get("value", "0") for row in skip_missing_summary if row.get("metric") == "alb2005_skip_missing_outcome_ready_rows"), "0")
    skip_missing_climate = next((row.get("value", "0") for row in skip_missing_summary if row.get("metric") == "alb2005_skip_missing_climate_linkage_ready_rows"), "0")
    skip_missing_decision = next((row.get("value", "") for row in skip_missing_summary if row.get("metric") == "alb2005_skip_missing_current_decision"), "")
    add(
        rows,
        "evidence",
        "ALB_2005 skip/missing semantics audit records raw trigger/downstream consistency while keeping recipe, outcome, and climate promotion blocked",
        status(
            counts["alb2005_skip_missing_semantics_audit"] > 0
            and counts["alb2005_skip_missing_semantics_summary"] > 0
            and safe_int(skip_missing_rows) > 0
            and skip_missing_payment_leaks == "0"
            and skip_missing_payment_positive_leaks == "0"
            and skip_missing_condition_leaks == "0"
            and skip_missing_condition_missing == "0"
            and skip_missing_financing_leaks == "0"
            and skip_missing_financing_missing == "0"
            and skip_missing_recipe == "0"
            and skip_missing_outcome == "0"
            and skip_missing_climate == "0"
            and skip_missing_decision == "blocked_alb2005_skip_missing_semantics_seen_but_recipe_not_ready"
        ),
        f"audit_rows={counts['alb2005_skip_missing_semantics_audit']}; summary_rows={counts['alb2005_skip_missing_semantics_summary']}; rows={skip_missing_rows}; payment_leaks={skip_missing_payment_leaks}; payment_positive_leaks={skip_missing_payment_positive_leaks}; condition_leaks={skip_missing_condition_leaks}; condition_missing_when_triggered={skip_missing_condition_missing}; financing_leaks={skip_missing_financing_leaks}; financing_missing_when_triggered={skip_missing_financing_missing}; recipe_ready_rows={skip_missing_recipe}; outcome_ready_rows={skip_missing_outcome}; climate_ready_rows={skip_missing_climate}; decision={skip_missing_decision}",
        ""
        if counts["alb2005_skip_missing_semantics_audit"] > 0
        and counts["alb2005_skip_missing_semantics_summary"] > 0
        and safe_int(skip_missing_rows) > 0
        and skip_missing_payment_leaks == "0"
        and skip_missing_payment_positive_leaks == "0"
        and skip_missing_condition_leaks == "0"
        and skip_missing_condition_missing == "0"
        and skip_missing_financing_leaks == "0"
        and skip_missing_financing_missing == "0"
        and skip_missing_recipe == "0"
        and skip_missing_outcome == "0"
        and skip_missing_climate == "0"
        and skip_missing_decision == "blocked_alb2005_skip_missing_semantics_seen_but_recipe_not_ready"
        else "Run script/74_audit_alb2005_skip_missing_semantics.py and keep ALB_2005 recipe/outcome/climate promotion blocked.",
    )
    unit_period_summary = read_csv_dicts(RESULT_DIR / "alb2005_consumption_oop_unit_period_summary.csv")
    unit_period_rows = next((row.get("value", "0") for row in unit_period_summary if row.get("metric") == "alb2005_consumption_oop_unit_period_rows"), "0")
    unit_period_totcons = next((row.get("value", "0") for row in unit_period_summary if row.get("metric") == "alb2005_consumption_oop_unit_period_total_consumption_positive_rows"), "0")
    unit_period_rcons = next((row.get("value", "0") for row in unit_period_summary if row.get("metric") == "alb2005_consumption_oop_unit_period_rcons_positive_rows"), "0")
    unit_period_metadata_old_lek = next((row.get("value", "0") for row in unit_period_summary if row.get("metric") == "alb2005_consumption_oop_unit_period_metadata_old_lek_rows_observed"), "0")
    unit_period_oop_old_lek = next((row.get("value", "0") for row in unit_period_summary if row.get("metric") == "alb2005_consumption_oop_unit_period_oop_old_lek_questionnaire_rows_observed"), "0")
    unit_period_four_week = next((row.get("value", "0") for row in unit_period_summary if row.get("metric") == "alb2005_consumption_oop_unit_period_four_week_oop_rows_observed"), "0")
    unit_period_twelve_month = next((row.get("value", "0") for row in unit_period_summary if row.get("metric") == "alb2005_consumption_oop_unit_period_twelve_month_oop_rows_observed"), "0")
    unit_period_nonfood_old_lek = next((row.get("value", "0") for row in unit_period_summary if row.get("metric") == "alb2005_consumption_oop_unit_period_questionnaire_nonfood_old_lek_rows_observed"), "0")
    unit_period_sdg = next((row.get("value", "0") for row in unit_period_summary if row.get("metric") == "alb2005_consumption_oop_unit_period_sdg382_ready_rows"), "0")
    unit_period_recipe = next((row.get("value", "0") for row in unit_period_summary if row.get("metric") == "alb2005_consumption_oop_unit_period_recipe_ready_rows"), "0")
    unit_period_outcome = next((row.get("value", "0") for row in unit_period_summary if row.get("metric") == "alb2005_consumption_oop_unit_period_outcome_ready_rows"), "0")
    unit_period_climate = next((row.get("value", "0") for row in unit_period_summary if row.get("metric") == "alb2005_consumption_oop_unit_period_climate_linkage_ready_rows"), "0")
    unit_period_decision = next((row.get("value", "") for row in unit_period_summary if row.get("metric") == "alb2005_consumption_oop_unit_period_current_decision"), "")
    add(
        rows,
        "evidence",
        "ALB_2005 consumption/OOP unit-period audit documents denominator and recall evidence while keeping SDG, recipe, outcome, and climate promotion blocked",
        status(
            counts["alb2005_consumption_oop_unit_period_audit"] > 0
            and counts["alb2005_consumption_oop_unit_period_summary"] > 0
            and safe_int(unit_period_rows) > 0
            and safe_int(unit_period_totcons) > 0
            and safe_int(unit_period_rcons) > 0
            and safe_int(unit_period_metadata_old_lek) > 0
            and safe_int(unit_period_oop_old_lek) > 0
            and safe_int(unit_period_four_week) > 0
            and safe_int(unit_period_twelve_month) > 0
            and safe_int(unit_period_nonfood_old_lek) > 0
            and unit_period_sdg == "0"
            and unit_period_recipe == "0"
            and unit_period_outcome == "0"
            and unit_period_climate == "0"
            and unit_period_decision == "blocked_alb2005_consumption_oop_unit_period_not_ready"
        ),
        f"audit_rows={counts['alb2005_consumption_oop_unit_period_audit']}; summary_rows={counts['alb2005_consumption_oop_unit_period_summary']}; rows={unit_period_rows}; positive_totcons={unit_period_totcons}; positive_rcons={unit_period_rcons}; metadata_old_lek_rows={unit_period_metadata_old_lek}; oop_old_lek_rows={unit_period_oop_old_lek}; four_week_rows={unit_period_four_week}; twelve_month_rows={unit_period_twelve_month}; nonfood_old_lek_rows={unit_period_nonfood_old_lek}; sdg_ready_rows={unit_period_sdg}; recipe_ready_rows={unit_period_recipe}; outcome_ready_rows={unit_period_outcome}; climate_ready_rows={unit_period_climate}; decision={unit_period_decision}",
        ""
        if counts["alb2005_consumption_oop_unit_period_audit"] > 0
        and counts["alb2005_consumption_oop_unit_period_summary"] > 0
        and safe_int(unit_period_rows) > 0
        and safe_int(unit_period_totcons) > 0
        and safe_int(unit_period_rcons) > 0
        and safe_int(unit_period_metadata_old_lek) > 0
        and safe_int(unit_period_oop_old_lek) > 0
        and safe_int(unit_period_four_week) > 0
        and safe_int(unit_period_twelve_month) > 0
        and safe_int(unit_period_nonfood_old_lek) > 0
        and unit_period_sdg == "0"
        and unit_period_recipe == "0"
        and unit_period_outcome == "0"
        and unit_period_climate == "0"
        and unit_period_decision == "blocked_alb2005_consumption_oop_unit_period_not_ready"
        else "Run script/75_audit_alb2005_consumption_oop_unit_period.py and keep ALB_2005 SDG/recipe/outcome/climate promotion blocked.",
    )
    aggregate_summary = read_csv_dicts(RESULT_DIR / "alb2005_consumption_aggregate_metadata_crosswalk_summary.csv")
    aggregate_rows = next((row.get("value", "0") for row in aggregate_summary if row.get("metric") == "alb2005_consumption_aggregate_crosswalk_rows"), "0")
    aggregate_metadata_rows = next((row.get("value", "0") for row in aggregate_summary if row.get("metric") == "alb2005_consumption_aggregate_crosswalk_metadata_rows"), "0")
    aggregate_local_columns = next((row.get("value", "0") for row in aggregate_summary if row.get("metric") == "alb2005_consumption_aggregate_crosswalk_local_poverty_columns"), "0")
    aggregate_present_local = next((row.get("value", "0") for row in aggregate_summary if row.get("metric") == "alb2005_consumption_aggregate_crosswalk_metadata_variables_present_in_local_raw_rows"), "0")
    aggregate_absent_local = next((row.get("value", "0") for row in aggregate_summary if row.get("metric") == "alb2005_consumption_aggregate_crosswalk_metadata_variables_absent_from_local_raw_rows"), "0")
    aggregate_per_capita = next((row.get("value", "0") for row in aggregate_summary if row.get("metric") == "alb2005_consumption_aggregate_crosswalk_local_per_capita_component_rows"), "0")
    aggregate_totcons = next((row.get("value", "0") for row in aggregate_summary if row.get("metric") == "alb2005_consumption_aggregate_crosswalk_totcons_positive_rows"), "0")
    aggregate_totcons05 = next((row.get("value", "0") for row in aggregate_summary if row.get("metric") == "alb2005_consumption_aggregate_crosswalk_totcons05_local_rows"), "0")
    aggregate_formula = next((row.get("value", "0") for row in aggregate_summary if row.get("metric") == "alb2005_consumption_aggregate_crosswalk_component_formula_reconstructable_rows"), "0")
    aggregate_sdg = next((row.get("value", "0") for row in aggregate_summary if row.get("metric") == "alb2005_consumption_aggregate_crosswalk_sdg382_ready_rows"), "0")
    aggregate_recipe = next((row.get("value", "0") for row in aggregate_summary if row.get("metric") == "alb2005_consumption_aggregate_crosswalk_recipe_ready_rows"), "0")
    aggregate_outcome = next((row.get("value", "0") for row in aggregate_summary if row.get("metric") == "alb2005_consumption_aggregate_crosswalk_outcome_ready_rows"), "0")
    aggregate_climate = next((row.get("value", "0") for row in aggregate_summary if row.get("metric") == "alb2005_consumption_aggregate_crosswalk_climate_linkage_ready_rows"), "0")
    aggregate_decision = next((row.get("value", "") for row in aggregate_summary if row.get("metric") == "alb2005_consumption_aggregate_crosswalk_current_decision"), "")
    add(
        rows,
        "evidence",
        "ALB_2005 aggregate metadata crosswalk documents public-metadata/local-raw mismatch while keeping SDG, recipe, outcome, and climate promotion blocked",
        status(
            counts["alb2005_consumption_aggregate_crosswalk_audit"] > 0
            and counts["alb2005_consumption_aggregate_crosswalk_summary"] > 0
            and safe_int(aggregate_rows) > 0
            and safe_int(aggregate_metadata_rows) > 0
            and safe_int(aggregate_local_columns) > 0
            and safe_int(aggregate_present_local) == 1
            and safe_int(aggregate_absent_local) > 0
            and safe_int(aggregate_per_capita) > 0
            and safe_int(aggregate_totcons) > 0
            and aggregate_totcons05 == "0"
            and aggregate_formula == "0"
            and aggregate_sdg == "0"
            and aggregate_recipe == "0"
            and aggregate_outcome == "0"
            and aggregate_climate == "0"
            and aggregate_decision == "blocked_alb2005_consumption_aggregate_metadata_crosswalk_not_ready"
        ),
        f"audit_rows={counts['alb2005_consumption_aggregate_crosswalk_audit']}; summary_rows={counts['alb2005_consumption_aggregate_crosswalk_summary']}; rows={aggregate_rows}; metadata_rows={aggregate_metadata_rows}; local_poverty_columns={aggregate_local_columns}; metadata_present_local={aggregate_present_local}; metadata_absent_local={aggregate_absent_local}; local_per_capita_components={aggregate_per_capita}; positive_totcons={aggregate_totcons}; totcons05_local_rows={aggregate_totcons05}; formula_reconstructable_rows={aggregate_formula}; sdg_ready_rows={aggregate_sdg}; recipe_ready_rows={aggregate_recipe}; outcome_ready_rows={aggregate_outcome}; climate_ready_rows={aggregate_climate}; decision={aggregate_decision}",
        ""
        if counts["alb2005_consumption_aggregate_crosswalk_audit"] > 0
        and counts["alb2005_consumption_aggregate_crosswalk_summary"] > 0
        and safe_int(aggregate_rows) > 0
        and safe_int(aggregate_totcons) > 0
        and aggregate_sdg == "0"
        and aggregate_recipe == "0"
        and aggregate_outcome == "0"
        and aggregate_climate == "0"
        and aggregate_decision == "blocked_alb2005_consumption_aggregate_metadata_crosswalk_not_ready"
        else "Run script/76_audit_alb2005_consumption_aggregate_metadata_crosswalk.py and keep ALB_2005 SDG/recipe/outcome/climate promotion blocked.",
    )
    component_source_summary = read_csv_dicts(RESULT_DIR / "alb2005_consumption_component_source_search_summary.csv")
    component_source_rows = next((row.get("value", "0") for row in component_source_summary if row.get("metric") == "alb2005_consumption_component_source_search_rows"), "0")
    component_source_targets = next((row.get("value", "0") for row in component_source_summary if row.get("metric") == "alb2005_consumption_component_source_search_target_variables"), "0")
    component_source_files = next((row.get("value", "0") for row in component_source_summary if row.get("metric") == "alb2005_consumption_component_source_search_local_files_scanned"), "0")
    component_source_variables = next((row.get("value", "0") for row in component_source_summary if row.get("metric") == "alb2005_consumption_component_source_search_local_variables_scanned"), "0")
    component_source_exact_found = next((row.get("value", "0") for row in component_source_summary if row.get("metric") == "alb2005_consumption_component_source_search_exact_target_variables_found"), "0")
    component_source_exact_missing = next((row.get("value", "0") for row in component_source_summary if row.get("metric") == "alb2005_consumption_component_source_search_exact_target_variables_missing"), "0")
    component_source_code_files = next((row.get("value", "0") for row in component_source_summary if row.get("metric") == "alb2005_consumption_component_source_search_construction_code_files_found"), "0")
    component_source_code_targets = next((row.get("value", "0") for row in component_source_summary if row.get("metric") == "alb2005_consumption_component_source_search_construction_code_targets_found"), "0")
    component_source_recipe = next((row.get("value", "0") for row in component_source_summary if row.get("metric") == "alb2005_consumption_component_source_search_recipe_ready_rows"), "0")
    component_source_outcome = next((row.get("value", "0") for row in component_source_summary if row.get("metric") == "alb2005_consumption_component_source_search_outcome_ready_rows"), "0")
    component_source_sdg = next((row.get("value", "0") for row in component_source_summary if row.get("metric") == "alb2005_consumption_component_source_search_sdg382_ready_rows"), "0")
    component_source_climate = next((row.get("value", "0") for row in component_source_summary if row.get("metric") == "alb2005_consumption_component_source_search_climate_linkage_ready_rows"), "0")
    component_source_decision = next((row.get("value", "") for row in component_source_summary if row.get("metric") == "alb2005_consumption_component_source_search_current_decision"), "")
    add(
        rows,
        "evidence",
        "ALB_2005 component source-search audit scans local raw/schema/questionnaire sources while keeping SDG, recipe, outcome, and climate promotion blocked",
        status(
            counts["alb2005_consumption_component_source_search_audit"] > 0
            and counts["alb2005_consumption_component_source_search_summary"] > 0
            and safe_int(component_source_rows) > 0
            and safe_int(component_source_targets) == 9
            and safe_int(component_source_files) > 0
            and safe_int(component_source_variables) > 0
            and safe_int(component_source_exact_found) == 1
            and safe_int(component_source_exact_missing) == 8
            and component_source_code_files == "0"
            and component_source_code_targets == "0"
            and component_source_recipe == "0"
            and component_source_outcome == "0"
            and component_source_sdg == "0"
            and component_source_climate == "0"
            and component_source_decision == "blocked_alb2005_consumption_component_source_search_not_ready"
        ),
        f"audit_rows={counts['alb2005_consumption_component_source_search_audit']}; summary_rows={counts['alb2005_consumption_component_source_search_summary']}; rows={component_source_rows}; targets={component_source_targets}; local_files={component_source_files}; local_variables={component_source_variables}; exact_found={component_source_exact_found}; exact_missing={component_source_exact_missing}; construction_code_files={component_source_code_files}; construction_code_targets={component_source_code_targets}; recipe_ready_rows={component_source_recipe}; outcome_ready_rows={component_source_outcome}; sdg_ready_rows={component_source_sdg}; climate_ready_rows={component_source_climate}; decision={component_source_decision}",
        ""
        if counts["alb2005_consumption_component_source_search_audit"] > 0
        and counts["alb2005_consumption_component_source_search_summary"] > 0
        and safe_int(component_source_exact_found) == 1
        and safe_int(component_source_exact_missing) == 8
        and component_source_recipe == "0"
        and component_source_outcome == "0"
        and component_source_sdg == "0"
        and component_source_climate == "0"
        and component_source_decision == "blocked_alb2005_consumption_component_source_search_not_ready"
        else "Run script/77_audit_alb2005_consumption_component_source_search.py and keep ALB_2005 SDG/recipe/outcome/climate promotion blocked.",
    )
    albania_wave_summary = read_csv_dicts(RESULT_DIR / "albania_existing_raw_wave_audit_summary.csv")
    albania_wave_harmonization_ready = next((row.get("value", "0") for row in albania_wave_summary if row.get("metric") == "albania_existing_raw_wave_harmonization_ready_rows"), "0")
    albania_wave_climate_ready = next((row.get("value", "0") for row in albania_wave_summary if row.get("metric") == "albania_existing_raw_wave_climate_linkage_ready_rows"), "0")
    add(
        rows,
        "evidence",
        "Existing Albania raw wave audit identifies present local raw waves and keeps harmonization/climate promotion blocked",
        status(
            counts["albania_existing_raw_wave_audit"] > 0
            and counts["albania_existing_raw_wave_audit_summary"] > 0
            and albania_wave_harmonization_ready == "0"
            and albania_wave_climate_ready == "0"
        ),
        f"audit_rows={counts['albania_existing_raw_wave_audit']}; summary_rows={counts['albania_existing_raw_wave_audit_summary']}; harmonization_ready_rows={albania_wave_harmonization_ready}; climate_linkage_ready_rows={albania_wave_climate_ready}",
        ""
        if counts["albania_existing_raw_wave_audit"] > 0
        and counts["albania_existing_raw_wave_audit_summary"] > 0
        and albania_wave_harmonization_ready == "0"
        and albania_wave_climate_ready == "0"
        else "Run script/50_audit_existing_albania_raw_waves.py and keep Albania waves blocked until wave-specific audits pass.",
    )
    alb2008_core_summary = read_csv_dicts(RESULT_DIR / "alb2008_household_core_candidate_summary.csv")
    alb2008_core_ready = next((row.get("value", "0") for row in alb2008_core_summary if row.get("metric") == "alb2008_household_core_recipe_ready_rows"), "0")
    alb2008_core_decision = next((row.get("value", "") for row in alb2008_core_summary if row.get("metric") == "alb2008_household_core_current_decision"), "")
    add(
        rows,
        "evidence",
        "ALB_2008 household core merge audit builds a temp-only candidate and keeps data promotion blocked",
        status(
            counts["alb2008_household_core_candidate"] > 0
            and counts["alb2008_household_core_merge_audit"] > 0
            and counts["alb2008_household_core_lineage"] > 0
            and counts["alb2008_household_core_candidate_summary"] > 0
            and alb2008_core_ready == "0"
            and alb2008_core_decision == "temp_candidate_not_analysis_ready"
        ),
        f"candidate_rows={counts['alb2008_household_core_candidate']}; merge_audit_rows={counts['alb2008_household_core_merge_audit']}; lineage_rows={counts['alb2008_household_core_lineage']}; summary_rows={counts['alb2008_household_core_candidate_summary']}; recipe_ready_rows={alb2008_core_ready}; decision={alb2008_core_decision}",
        ""
        if counts["alb2008_household_core_candidate"] > 0
        and counts["alb2008_household_core_merge_audit"] > 0
        and counts["alb2008_household_core_lineage"] > 0
        and counts["alb2008_household_core_candidate_summary"] > 0
        and alb2008_core_ready == "0"
        and alb2008_core_decision == "temp_candidate_not_analysis_ready"
        else "Run script/51_audit_alb2008_household_core_merge.py and keep the candidate out of data/.",
    )
    alb2008_outcome_summary = read_csv_dicts(RESULT_DIR / "alb2008_provisional_outcome_feasibility_summary.csv")
    alb2008_outcome_ready = next((row.get("value", "0") for row in alb2008_outcome_summary if row.get("metric") == "alb2008_provisional_outcome_ready_rows"), "0")
    alb2008_outcome_decision = next((row.get("value", "") for row in alb2008_outcome_summary if row.get("metric") == "alb2008_provisional_outcome_current_decision"), "")
    add(
        rows,
        "evidence",
        "ALB_2008 provisional outcome feasibility audit computes raw event-rate diagnostics and keeps final outcomes blocked",
        status(
            counts["alb2008_provisional_outcome_feasibility_audit"] > 0
            and counts["alb2008_provisional_outcome_feasibility_summary"] > 0
            and alb2008_outcome_ready == "0"
            and alb2008_outcome_decision == "not_final_outcomes_timing_geography_recall_blocked"
        ),
        f"audit_rows={counts['alb2008_provisional_outcome_feasibility_audit']}; summary_rows={counts['alb2008_provisional_outcome_feasibility_summary']}; ready_rows={alb2008_outcome_ready}; decision={alb2008_outcome_decision}",
        ""
        if counts["alb2008_provisional_outcome_feasibility_audit"] > 0
        and counts["alb2008_provisional_outcome_feasibility_summary"] > 0
        and alb2008_outcome_ready == "0"
        and alb2008_outcome_decision == "not_final_outcomes_timing_geography_recall_blocked"
        else "Run script/52_audit_alb2008_provisional_outcome_feasibility.py and keep all provisional outcomes blocked from data/.",
    )
    alb2008_semantics_summary = read_csv_dicts(RESULT_DIR / "alb2008_outcome_semantics_raw_value_summary.csv")
    alb2008_semantics_outcome_ready = next((row.get("value", "0") for row in alb2008_semantics_summary if row.get("metric") == "alb2008_outcome_semantics_outcome_ready_rows"), "0")
    alb2008_semantics_sdg_ready = next((row.get("value", "0") for row in alb2008_semantics_summary if row.get("metric") == "alb2008_outcome_semantics_sdg382_ready_rows"), "0")
    alb2008_semantics_climate_ready = next((row.get("value", "0") for row in alb2008_semantics_summary if row.get("metric") == "alb2008_outcome_semantics_climate_linkage_ready_rows"), "0")
    alb2008_semantics_decision = next((row.get("value", "") for row in alb2008_semantics_summary if row.get("metric") == "alb2008_outcome_semantics_current_decision"), "")
    add(
        rows,
        "evidence",
        "ALB_2008 raw outcome-semantics value audit documents payment, gift, access, need, and service-quality fields while keeping promotion blocked",
        status(
            counts["alb2008_outcome_semantics_raw_value_audit"] > 0
            and counts["alb2008_outcome_semantics_raw_value_summary"] > 0
            and alb2008_semantics_outcome_ready == "0"
            and alb2008_semantics_sdg_ready == "0"
            and alb2008_semantics_climate_ready == "0"
            and alb2008_semantics_decision == "blocked_timing_geography_outcome_semantics_units_recall_skip_patterns"
        ),
        f"audit_rows={counts['alb2008_outcome_semantics_raw_value_audit']}; summary_rows={counts['alb2008_outcome_semantics_raw_value_summary']}; outcome_ready={alb2008_semantics_outcome_ready}; sdg382_ready={alb2008_semantics_sdg_ready}; climate_ready={alb2008_semantics_climate_ready}; decision={alb2008_semantics_decision}",
        ""
        if counts["alb2008_outcome_semantics_raw_value_audit"] > 0
        and counts["alb2008_outcome_semantics_raw_value_summary"] > 0
        and alb2008_semantics_outcome_ready == "0"
        and alb2008_semantics_sdg_ready == "0"
        and alb2008_semantics_climate_ready == "0"
        and alb2008_semantics_decision == "blocked_timing_geography_outcome_semantics_units_recall_skip_patterns"
        else "Run script/62_audit_alb2008_outcome_semantics_raw_values.py and keep all ALB_2008 outcome, SDG 3.8.2, and climate-linkage promotion blocked.",
    )
    alb2008_timing_geo_summary = read_csv_dicts(RESULT_DIR / "alb2008_timing_geography_exhaustive_summary.csv")
    alb2008_timing_geo_ready = next((row.get("value", "0") for row in alb2008_timing_geo_summary if row.get("metric") == "alb2008_climate_linkage_ready_rows"), "0")
    alb2008_timing_geo_decision = next((row.get("value", "") for row in alb2008_timing_geo_summary if row.get("metric") == "alb2008_timing_geography_current_decision"), "")
    add(
        rows,
        "evidence",
        "ALB_2008 timing/geography exhaustive audit scans raw files and keeps climate linkage blocked",
        status(
            counts["alb2008_timing_geography_exhaustive_audit"] > 0
            and counts["alb2008_timing_geography_exhaustive_summary"] > 0
            and alb2008_timing_geo_ready == "0"
            and alb2008_timing_geo_decision == "blocked_missing_interview_timing_coarse_geography_no_gps"
        ),
        f"audit_rows={counts['alb2008_timing_geography_exhaustive_audit']}; summary_rows={counts['alb2008_timing_geography_exhaustive_summary']}; climate_linkage_ready_rows={alb2008_timing_geo_ready}; decision={alb2008_timing_geo_decision}",
        ""
        if counts["alb2008_timing_geography_exhaustive_audit"] > 0
        and counts["alb2008_timing_geography_exhaustive_summary"] > 0
        and alb2008_timing_geo_ready == "0"
        and alb2008_timing_geo_decision == "blocked_missing_interview_timing_coarse_geography_no_gps"
        else "Run script/53_audit_alb2008_timing_geography_exhaustive.py and keep climate linkage blocked until timing/geography pass.",
    )
    alb2008_fallback_summary = read_csv_dicts(RESULT_DIR / "alb2008_fallback_blocker_resolution_summary.csv")
    alb2008_fallback_rows = next((row.get("value", "0") for row in alb2008_fallback_summary if row.get("metric") == "alb2008_fallback_blocker_resolution_rows"), "0")
    alb2008_fallback_timing = next((row.get("value", "0") for row in alb2008_fallback_summary if row.get("metric") == "alb2008_fallback_blocker_timing_rows"), "0")
    alb2008_fallback_geography = next((row.get("value", "0") for row in alb2008_fallback_summary if row.get("metric") == "alb2008_fallback_blocker_geography_rows"), "0")
    alb2008_fallback_outcome = next((row.get("value", "0") for row in alb2008_fallback_summary if row.get("metric") == "alb2008_fallback_blocker_outcome_rows"), "0")
    alb2008_fallback_promotion = next((row.get("value", "0") for row in alb2008_fallback_summary if row.get("metric") == "alb2008_fallback_blocker_promotion_gate_rows"), "0")
    alb2008_fallback_hard_blocked = next((row.get("value", "0") for row in alb2008_fallback_summary if row.get("metric") == "alb2008_fallback_blocker_hard_blocked_rows"), "0")
    alb2008_fallback_timing_ready = next((row.get("value", "0") for row in alb2008_fallback_summary if row.get("metric") == "alb2008_fallback_blocker_interview_timing_ready_rows"), "0")
    alb2008_fallback_geography_ready = next((row.get("value", "0") for row in alb2008_fallback_summary if row.get("metric") == "alb2008_fallback_blocker_geography_ready_rows"), "0")
    alb2008_fallback_outcome_ready = next((row.get("value", "0") for row in alb2008_fallback_summary if row.get("metric") == "alb2008_fallback_blocker_outcome_ready_rows"), "0")
    alb2008_fallback_climate_ready = next((row.get("value", "0") for row in alb2008_fallback_summary if row.get("metric") == "alb2008_fallback_blocker_climate_linkage_ready_rows"), "0")
    alb2008_fallback_data_ready = next((row.get("value", "0") for row in alb2008_fallback_summary if row.get("metric") == "alb2008_fallback_blocker_data_write_ready_rows"), "0")
    alb2008_fallback_decision = next((row.get("value", "") for row in alb2008_fallback_summary if row.get("metric") == "alb2008_fallback_blocker_current_decision"), "")
    add(
        rows,
        "evidence",
        "ALB_2008 fallback blocker resolution matrix consolidates timing, geography, outcome, and promotion stop rules without promoting data",
        status(
            counts["alb2008_fallback_blocker_resolution_matrix"] == 10
            and counts["alb2008_fallback_blocker_resolution_summary"] == 12
            and alb2008_fallback_rows == "10"
            and alb2008_fallback_timing == "3"
            and alb2008_fallback_geography == "3"
            and alb2008_fallback_outcome == "2"
            and alb2008_fallback_promotion == "2"
            and alb2008_fallback_hard_blocked == "10"
            and alb2008_fallback_timing_ready == "0"
            and alb2008_fallback_geography_ready == "0"
            and alb2008_fallback_outcome_ready == "0"
            and alb2008_fallback_climate_ready == "0"
            and alb2008_fallback_data_ready == "0"
            and alb2008_fallback_decision == "blocked_alb2008_no_timing_geography_fallback_ready"
        ),
        f"matrix_rows={counts['alb2008_fallback_blocker_resolution_matrix']}; summary_rows={counts['alb2008_fallback_blocker_resolution_summary']}; summary_matrix_rows={alb2008_fallback_rows}; timing={alb2008_fallback_timing}; geography={alb2008_fallback_geography}; outcome={alb2008_fallback_outcome}; promotion_gate={alb2008_fallback_promotion}; hard_blocked={alb2008_fallback_hard_blocked}; timing_ready={alb2008_fallback_timing_ready}; geography_ready={alb2008_fallback_geography_ready}; outcome_ready={alb2008_fallback_outcome_ready}; climate_ready={alb2008_fallback_climate_ready}; data_ready={alb2008_fallback_data_ready}; decision={alb2008_fallback_decision}",
        ""
        if counts["alb2008_fallback_blocker_resolution_matrix"] == 10
        and counts["alb2008_fallback_blocker_resolution_summary"] == 12
        and alb2008_fallback_hard_blocked == "10"
        and alb2008_fallback_timing_ready == "0"
        and alb2008_fallback_geography_ready == "0"
        and alb2008_fallback_outcome_ready == "0"
        and alb2008_fallback_climate_ready == "0"
        and alb2008_fallback_data_ready == "0"
        and alb2008_fallback_decision == "blocked_alb2008_no_timing_geography_fallback_ready"
        else "Run script/116_build_alb2008_fallback_blocker_resolution_matrix.py and keep ALB_2008 out of fallback promotion until timing, geography, and outcome gates pass.",
    )
    first_batch_dataset_gate = read_csv_dicts(RESULT_DIR / "first_batch_dataset_verification_gate.csv")
    first_batch_ready = sum(1 for row in first_batch_dataset_gate if row.get("current_gate_status") == "ready_for_manual_value_label_unit_key_audit")
    add(
        rows,
        "evidence",
        "First-batch raw verification workbook provides dataset, concept, and variable templates for post-download promotion decisions",
        status(
            counts["first_batch_dataset_verification_gate"] > 0
            and counts["first_batch_concept_verification_template"] > 0
            and counts["first_batch_variable_verification_template"] > 0
            and counts["first_batch_raw_verification_workbook_summary"] > 0
        ),
        f"dataset_gate_rows={counts['first_batch_dataset_verification_gate']}; concept_template_rows={counts['first_batch_concept_verification_template']}; variable_template_rows={counts['first_batch_variable_verification_template']}; summary_rows={counts['first_batch_raw_verification_workbook_summary']}; datasets_ready_for_value_audit={first_batch_ready}",
        ""
        if counts["first_batch_dataset_verification_gate"] > 0
        and counts["first_batch_concept_verification_template"] > 0
        and counts["first_batch_variable_verification_template"] > 0
        and counts["first_batch_raw_verification_workbook_summary"] > 0
        else "Run script/38_build_first_batch_raw_verification_workbook.py after first-batch acquisition checklist generation.",
    )
    direct_manifest = read_csv_dicts(RESULT_DIR / "direct_read_artifact_manifest.csv")
    direct_present = sum(1 for row in direct_manifest if row.get("current_status") == "present_nonempty")
    direct_missing = sum(1 for row in direct_manifest if row.get("current_status") != "present_nonempty")
    add(
        rows,
        "evidence",
        "Direct-read audit bundle summarizes current gates, completion gaps, no-go rules, and curated artifact checksums",
        status(
            counts["direct_read_audit_bundle"] > 0
            and counts["direct_read_artifact_manifest"] > 0
            and counts["direct_read_audit_bundle_summary"] > 0
        ),
        f"bundle_rows={counts['direct_read_audit_bundle']}; manifest_rows={counts['direct_read_artifact_manifest']}; summary_rows={counts['direct_read_audit_bundle_summary']}; manifest_present={direct_present}; manifest_missing_or_empty={direct_missing}",
        ""
        if counts["direct_read_audit_bundle"] > 0
        and counts["direct_read_artifact_manifest"] > 0
        and counts["direct_read_audit_bundle_summary"] > 0
        else "Run script/36_build_direct_read_audit_bundle.py after empirical readiness dashboard generation.",
    )
    promotion_registry = read_csv_dicts(RESULT_DIR / "promoted_country_wave_registry.csv")
    promotion_summary = read_csv_dicts(RESULT_DIR / "country_wave_promotion_summary.csv")
    refocused_queue = read_csv_dicts(TEMP_DIR / "priority_lsms_isa_refocused_acquisition_queue.csv")
    registry_ids = {row.get("idno", "") for row in promotion_registry if row.get("idno")}
    refocused_ids = {row.get("idno", "") for row in refocused_queue if row.get("idno")}
    refocused_registry_coverage = len(registry_ids & refocused_ids)
    refocused_missing = len(refocused_ids - registry_ids)
    registry_extra_non_refocused = len(registry_ids - refocused_ids)
    albania_main_rows = sum(1 for row in promotion_registry if row.get("country") == "Albania")
    promoted_rows = sum(1 for row in promotion_registry if row.get("analysis_ready_status") == "promoted_analysis_ready")
    priority_rows = sum(1 for row in promotion_registry if row.get("priority_country") == "1")
    packet_count = len(list((REPORT_DIR / "country_wave_promotion_packets").glob("*.md"))) if (REPORT_DIR / "country_wave_promotion_packets").exists() else 0
    modeling_gate = next((row.get("value", "") for row in promotion_summary if row.get("metric") == "modeling_gate_status"), "")
    add(
        rows,
        "dataset_promotion",
        "Country-wave promotion registry exists and remains fail-closed until verified raw data pass gates",
        status(
            counts["promoted_country_wave_registry"] > 0
            and counts["country_wave_promotion_gate_audit"] > 0
            and counts["country_wave_promotion_summary"] > 0
            and counts["priority_country_wave_download_queue"] > 0
            and packet_count > 0
            and refocused_registry_coverage >= counts["priority_lsms_isa_refocused_acquisition_queue"]
            and refocused_missing == 0
            and registry_extra_non_refocused == 0
            and albania_main_rows == 0
            and modeling_gate == "blocked"
        ),
        f"registry_rows={counts['promoted_country_wave_registry']}; gate_rows={counts['country_wave_promotion_gate_audit']}; summary_rows={counts['country_wave_promotion_summary']}; queue_rows={counts['priority_country_wave_download_queue']}; priority_rows={priority_rows}; promoted_rows={promoted_rows}; packets={packet_count}; refocused_coverage={refocused_registry_coverage}; refocused_missing={refocused_missing}; registry_extra_non_refocused={registry_extra_non_refocused}; albania_main_rows={albania_main_rows}; modeling_gate={modeling_gate}",
        ""
        if counts["promoted_country_wave_registry"] > 0
        and counts["country_wave_promotion_gate_audit"] > 0
        and counts["country_wave_promotion_summary"] > 0
        and counts["priority_country_wave_download_queue"] > 0
        and packet_count > 0
        and refocused_registry_coverage >= counts["priority_lsms_isa_refocused_acquisition_queue"]
        and refocused_missing == 0
        and registry_extra_non_refocused == 0
        and albania_main_rows == 0
        and modeling_gate == "blocked"
        else "Run script/151_refresh_refocused_promoted_country_wave_registry.py after the LSMS/ISA promotion packets and keep modeling blocked until registry thresholds pass.",
    )
    priority_acq_summary = read_csv_dicts(RESULT_DIR / "priority_promotion_acquisition_summary.csv")
    priority_batch_rows = safe_int(next((row.get("value", "0") for row in priority_acq_summary if row.get("metric") == "priority_10_wave_batch_rows"), "0"), 0)
    priority_batch_countries = safe_int(next((row.get("value", "0") for row in priority_acq_summary if row.get("metric") == "priority_10_wave_batch_countries"), "0"), 0)
    sixth_backup_rows = safe_int(next((row.get("value", "0") for row in priority_acq_summary if row.get("metric") == "sixth_country_backup_rows"), "0"), 0)
    priority_acq_modeling_gate = next((row.get("value", "") for row in priority_acq_summary if row.get("metric") == "modeling_gate_status"), "")
    add(
        rows,
        "dataset_promotion",
        "Priority-first raw acquisition plan covers the requested countries and preserves the no-modeling gate",
        status(
            counts["priority_promotion_acquisition_wave_plan"] >= 10
            and counts["priority_promotion_acquisition_file_queue"] > 0
            and counts["priority_promotion_acquisition_summary"] > 0
            and file_ok(REPORT_DIR / "priority_promotion_acquisition_plan.md")
            and priority_batch_rows >= 10
            and priority_batch_countries >= 5
            and sixth_backup_rows >= 1
            and priority_acq_modeling_gate == "blocked"
        ),
        f"wave_plan_rows={counts['priority_promotion_acquisition_wave_plan']}; file_queue_rows={counts['priority_promotion_acquisition_file_queue']}; summary_rows={counts['priority_promotion_acquisition_summary']}; priority_batch_rows={priority_batch_rows}; priority_batch_countries={priority_batch_countries}; sixth_backup_rows={sixth_backup_rows}; modeling_gate={priority_acq_modeling_gate}",
        ""
        if counts["priority_promotion_acquisition_wave_plan"] >= 10
        and counts["priority_promotion_acquisition_file_queue"] > 0
        and counts["priority_promotion_acquisition_summary"] > 0
        and file_ok(REPORT_DIR / "priority_promotion_acquisition_plan.md")
        and priority_batch_rows >= 10
        and priority_batch_countries >= 5
        and sixth_backup_rows >= 1
        and priority_acq_modeling_gate == "blocked"
        else "Run script/122_build_priority_promotion_acquisition_plan.py after the promotion registry and raw-ingestion metadata are refreshed.",
    )
    priority_probe_summary = read_csv_dicts(RESULT_DIR / "priority_official_raw_access_summary.csv")
    priority_probe_rows = safe_int(next((row.get("value", "0") for row in priority_probe_summary if row.get("metric") == "priority_official_raw_access_probe_rows"), "0"), 0)
    priority_probe_batch_rows = safe_int(next((row.get("value", "0") for row in priority_probe_summary if row.get("metric") == "priority_10_wave_probe_rows"), "0"), 0)
    priority_probe_backup_rows = safe_int(next((row.get("value", "0") for row in priority_probe_summary if row.get("metric") == "sixth_country_backup_probe_rows"), "0"), 0)
    priority_probe_manual_rows = safe_int(next((row.get("value", "0") for row in priority_probe_summary if row.get("metric") == "manual_action_required_rows"), "0"), 0)
    priority_probe_modeling_gate = next((row.get("value", "") for row in priority_probe_summary if row.get("metric") == "modeling_gate_status"), "")
    add(
        rows,
        "dataset_promotion",
        "Priority official raw access probe covers the acquisition batch and documents access-gate status",
        status(
            counts["priority_official_raw_access_probe"] >= counts["priority_promotion_acquisition_wave_plan"]
            and counts["priority_official_raw_access_summary"] > 0
            and file_ok(REPORT_DIR / "priority_official_raw_access_probe.md")
            and priority_probe_rows >= 10
            and priority_probe_batch_rows >= 10
            and priority_probe_backup_rows >= 1
            and priority_probe_manual_rows >= 1
            and priority_probe_modeling_gate == "blocked"
        ),
        f"probe_rows={counts['priority_official_raw_access_probe']}; summary_rows={counts['priority_official_raw_access_summary']}; reported_rows={priority_probe_rows}; priority_10_rows={priority_probe_batch_rows}; backup_rows={priority_probe_backup_rows}; manual_action_rows={priority_probe_manual_rows}; modeling_gate={priority_probe_modeling_gate}",
        ""
        if counts["priority_official_raw_access_probe"] >= counts["priority_promotion_acquisition_wave_plan"]
        and counts["priority_official_raw_access_summary"] > 0
        and file_ok(REPORT_DIR / "priority_official_raw_access_probe.md")
        and priority_probe_rows >= 10
        and priority_probe_batch_rows >= 10
        and priority_probe_backup_rows >= 1
        and priority_probe_manual_rows >= 1
        and priority_probe_modeling_gate == "blocked"
        else "Run script/123_probe_priority_official_raw_access.py after the priority acquisition wave plan exists.",
    )
    priority_raw_gate_summary = read_csv_dicts(RESULT_DIR / "priority_raw_intake_gate_summary.csv")
    priority_raw_gate_rows = safe_int(next((row.get("value", "0") for row in priority_raw_gate_summary if row.get("metric") == "priority_raw_intake_gate_rows"), "0"), 0)
    priority_raw_gate_batch_rows = safe_int(next((row.get("value", "0") for row in priority_raw_gate_summary if row.get("metric") == "priority_raw_intake_priority_10_rows"), "0"), 0)
    priority_raw_gate_countries = safe_int(next((row.get("value", "0") for row in priority_raw_gate_summary if row.get("metric") == "priority_raw_intake_priority_10_countries"), "0"), 0)
    priority_raw_gate_backup_rows = safe_int(next((row.get("value", "0") for row in priority_raw_gate_summary if row.get("metric") == "priority_raw_intake_backup_rows"), "0"), 0)
    priority_raw_file_target_rows = safe_int(next((row.get("value", "0") for row in priority_raw_gate_summary if row.get("metric") == "priority_raw_file_target_rows"), "0"), 0)
    priority_raw_manual_blocked_rows = safe_int(next((row.get("value", "0") for row in priority_raw_gate_summary if row.get("metric") == "priority_raw_gate_blocked_manual_rows"), "0"), 0)
    priority_raw_schema_ready_rows = safe_int(next((row.get("value", "0") for row in priority_raw_gate_summary if row.get("metric") == "priority_raw_gate_schema_ready_rows"), "0"), 0)
    priority_raw_handoff_rows = safe_int(next((row.get("value", "0") for row in priority_raw_gate_summary if row.get("metric") == "priority_raw_handoff_readmes_written"), "0"), 0)
    priority_raw_modeling_gate = next((row.get("value", "") for row in priority_raw_gate_summary if row.get("metric") == "modeling_gate_status"), "")
    priority_raw_gate = read_csv_dicts(TEMP_DIR / "priority_raw_intake_gate.csv")
    priority_handoff_existing = sum(1 for row in priority_raw_gate if row.get("handoff_readme") and file_ok(PROJECT_ROOT / row.get("handoff_readme", "")))
    add(
        rows,
        "dataset_promotion",
        "Priority raw intake gate maps each acquisition wave to placement handoff files, required raw targets, and fail-closed promotion status",
        status(
            counts["priority_raw_intake_gate"] >= counts["priority_promotion_acquisition_wave_plan"]
            and counts["priority_raw_file_targets"] >= counts["priority_promotion_acquisition_file_queue"]
            and counts["priority_raw_intake_gate_summary"] > 0
            and file_ok(REPORT_DIR / "priority_raw_intake_gate.md")
            and priority_raw_gate_rows >= 10
            and priority_raw_gate_batch_rows >= 10
            and priority_raw_gate_countries >= 5
            and priority_raw_gate_backup_rows >= 1
            and priority_raw_file_target_rows >= counts["priority_promotion_acquisition_file_queue"]
            and priority_raw_manual_blocked_rows >= 1
            and priority_raw_schema_ready_rows == 0
            and priority_raw_handoff_rows >= priority_raw_gate_rows
            and priority_handoff_existing >= priority_raw_gate_rows
            and priority_raw_modeling_gate == "blocked"
        ),
        f"gate_rows={counts['priority_raw_intake_gate']}; file_target_rows={counts['priority_raw_file_targets']}; summary_rows={counts['priority_raw_intake_gate_summary']}; reported_gate_rows={priority_raw_gate_rows}; priority_10_rows={priority_raw_gate_batch_rows}; priority_countries={priority_raw_gate_countries}; backup_rows={priority_raw_gate_backup_rows}; reported_file_targets={priority_raw_file_target_rows}; manual_blocked_rows={priority_raw_manual_blocked_rows}; schema_ready_rows={priority_raw_schema_ready_rows}; handoff_rows={priority_raw_handoff_rows}; handoff_existing={priority_handoff_existing}; modeling_gate={priority_raw_modeling_gate}",
        ""
        if counts["priority_raw_intake_gate"] >= counts["priority_promotion_acquisition_wave_plan"]
        and counts["priority_raw_file_targets"] >= counts["priority_promotion_acquisition_file_queue"]
        and counts["priority_raw_intake_gate_summary"] > 0
        and file_ok(REPORT_DIR / "priority_raw_intake_gate.md")
        and priority_raw_gate_rows >= 10
        and priority_raw_gate_batch_rows >= 10
        and priority_raw_gate_countries >= 5
        and priority_raw_gate_backup_rows >= 1
        and priority_raw_file_target_rows >= counts["priority_promotion_acquisition_file_queue"]
        and priority_raw_manual_blocked_rows >= 1
        and priority_raw_schema_ready_rows == 0
        and priority_raw_handoff_rows >= priority_raw_gate_rows
        and priority_handoff_existing >= priority_raw_gate_rows
        and priority_raw_modeling_gate == "blocked"
        else "Run script/124_build_priority_raw_intake_gate.py after priority access probing and raw-download intake auditing.",
    )
    priority_archive_summary = read_csv_dicts(RESULT_DIR / "priority_archive_member_preflight_summary.csv")
    priority_archive_dataset_rows = safe_int(next((row.get("value", "0") for row in priority_archive_summary if row.get("metric") == "priority_archive_preflight_dataset_rows"), "0"), 0)
    priority_archive_target_rows = safe_int(next((row.get("value", "0") for row in priority_archive_summary if row.get("metric") == "priority_archive_preflight_file_target_rows"), "0"), 0)
    priority_archive_files_found = safe_int(next((row.get("value", "0") for row in priority_archive_summary if row.get("metric") == "priority_archive_files_found"), "0"), 0)
    priority_archive_member_rows = safe_int(next((row.get("value", "0") for row in priority_archive_summary if row.get("metric") == "priority_archive_member_rows"), "0"), 0)
    priority_direct_covered = safe_int(next((row.get("value", "0") for row in priority_archive_summary if row.get("metric") == "priority_targets_covered_by_direct_file"), "0"), 0)
    priority_archive_covered = safe_int(next((row.get("value", "0") for row in priority_archive_summary if row.get("metric") == "priority_targets_covered_by_archive_member"), "0"), 0)
    priority_archive_missing = safe_int(next((row.get("value", "0") for row in priority_archive_summary if row.get("metric") == "priority_targets_missing_direct_or_archive_member"), "0"), 0)
    priority_archive_all_covered = safe_int(next((row.get("value", "0") for row in priority_archive_summary if row.get("metric") == "priority_datasets_all_targets_covered"), "0"), 0)
    priority_archive_blocked_no_raw = safe_int(next((row.get("value", "0") for row in priority_archive_summary if row.get("metric") == "priority_datasets_blocked_no_raw_or_archive"), "0"), 0)
    priority_archive_modeling_gate = next((row.get("value", "") for row in priority_archive_summary if row.get("metric") == "modeling_gate_status"), "")
    add(
        rows,
        "dataset_promotion",
        "Priority archive member preflight checks placed direct files and archives against priority raw module targets before value verification",
        status(
            counts["priority_archive_completeness_matrix"] >= counts["priority_raw_file_targets"]
            and counts["priority_archive_member_preflight_summary"] > 0
            and file_ok(REPORT_DIR / "priority_archive_member_preflight.md")
            and priority_archive_dataset_rows >= counts["priority_promotion_acquisition_wave_plan"]
            and priority_archive_target_rows >= counts["priority_raw_file_targets"]
            and priority_direct_covered + priority_archive_covered + priority_archive_missing <= priority_archive_target_rows
            and priority_archive_modeling_gate == "blocked"
        ),
        f"inventory_rows={counts['priority_archive_member_inventory']}; completeness_rows={counts['priority_archive_completeness_matrix']}; summary_rows={counts['priority_archive_member_preflight_summary']}; dataset_rows={priority_archive_dataset_rows}; target_rows={priority_archive_target_rows}; archives_found={priority_archive_files_found}; member_rows={priority_archive_member_rows}; direct_covered={priority_direct_covered}; archive_covered={priority_archive_covered}; missing={priority_archive_missing}; all_covered={priority_archive_all_covered}; blocked_no_raw={priority_archive_blocked_no_raw}; modeling_gate={priority_archive_modeling_gate}",
        ""
        if counts["priority_archive_completeness_matrix"] >= counts["priority_raw_file_targets"]
        and counts["priority_archive_member_preflight_summary"] > 0
        and file_ok(REPORT_DIR / "priority_archive_member_preflight.md")
        and priority_archive_dataset_rows >= counts["priority_promotion_acquisition_wave_plan"]
        and priority_archive_target_rows >= counts["priority_raw_file_targets"]
        and priority_direct_covered + priority_archive_covered + priority_archive_missing <= priority_archive_target_rows
        and priority_archive_modeling_gate == "blocked"
        else "Run script/128_build_priority_archive_member_preflight.py after priority raw intake gate; keep it fail-closed until raw archives/direct files are placed.",
    )
    priority_climate_summary = read_csv_dicts(RESULT_DIR / "priority_climate_linkage_preflight_summary.csv")
    priority_climate_rows = safe_int(next((row.get("value", "0") for row in priority_climate_summary if row.get("metric") == "priority_climate_preflight_rows"), "0"), 0)
    priority_climate_batch_rows = safe_int(next((row.get("value", "0") for row in priority_climate_summary if row.get("metric") == "priority_climate_preflight_priority_10_rows"), "0"), 0)
    priority_climate_countries = safe_int(next((row.get("value", "0") for row in priority_climate_summary if row.get("metric") == "priority_climate_preflight_priority_10_countries"), "0"), 0)
    priority_climate_backup_rows = safe_int(next((row.get("value", "0") for row in priority_climate_summary if row.get("metric") == "priority_climate_preflight_backup_rows"), "0"), 0)
    priority_climate_requirements = safe_int(next((row.get("value", "0") for row in priority_climate_summary if row.get("metric") == "priority_climate_requirement_rows"), "0"), 0)
    priority_climate_source_ready_rows = safe_int(next((row.get("value", "0") for row in priority_climate_summary if row.get("metric") == "priority_chirps_era5_source_route_ready_rows"), "0"), 0)
    priority_accepted_chirps_era5_rows = safe_int(next((row.get("value", "0") for row in priority_climate_summary if row.get("metric") == "priority_accepted_chirps_era5_route_rows"), "0"), 0)
    priority_route_preflight_ready_rows = safe_int(next((row.get("value", "0") for row in priority_climate_summary if row.get("metric") == "priority_route_preflight_ready_needs_extraction_rows"), "0"), 0)
    priority_climate_blocked_rows = safe_int(next((row.get("value", "0") for row in priority_climate_summary if row.get("metric") == "priority_climate_blocked_raw_timing_geography_rows"), "0"), 0)
    priority_climate_handoff_rows = safe_int(next((row.get("value", "0") for row in priority_climate_summary if row.get("metric") == "priority_climate_handoff_readmes_written"), "0"), 0)
    priority_climate_source_groups_ready = safe_int(next((row.get("value", "0") for row in priority_climate_summary if row.get("metric") == "climate_source_route_groups_ready"), "0"), 0)
    priority_climate_modeling_gate = next((row.get("value", "") for row in priority_climate_summary if row.get("metric") == "modeling_gate_status"), "")
    priority_climate_preflight = read_csv_dicts(TEMP_DIR / "priority_climate_linkage_preflight.csv")
    priority_climate_handoff_existing = sum(1 for row in priority_climate_preflight if row.get("handoff_readme") and file_ok(PROJECT_ROOT / row.get("handoff_readme", "")))
    add(
        rows,
        "dataset_promotion",
        "Priority climate linkage preflight maps CHIRPS/ERA5 routes to raw timing/geography gates while keeping accepted climate linkage closed",
        status(
            counts["priority_climate_linkage_preflight"] >= counts["priority_promotion_acquisition_wave_plan"]
            and counts["priority_climate_linkage_requirements"] >= counts["priority_promotion_acquisition_wave_plan"]
            and counts["priority_climate_linkage_preflight_summary"] > 0
            and file_ok(REPORT_DIR / "priority_climate_linkage_preflight.md")
            and priority_climate_rows >= 10
            and priority_climate_batch_rows >= 10
            and priority_climate_countries >= 5
            and priority_climate_backup_rows >= 1
            and priority_climate_requirements >= priority_climate_rows
            and priority_climate_source_ready_rows >= priority_climate_rows
            and priority_accepted_chirps_era5_rows == 0
            and priority_climate_blocked_rows + priority_route_preflight_ready_rows >= priority_climate_rows
            and priority_climate_handoff_rows >= priority_climate_rows
            and priority_climate_handoff_existing >= priority_climate_rows
            and priority_climate_source_groups_ready >= 3
            and priority_climate_modeling_gate == "blocked"
        ),
        f"preflight_rows={counts['priority_climate_linkage_preflight']}; requirement_rows={counts['priority_climate_linkage_requirements']}; summary_rows={counts['priority_climate_linkage_preflight_summary']}; reported_rows={priority_climate_rows}; priority_10_rows={priority_climate_batch_rows}; priority_countries={priority_climate_countries}; backup_rows={priority_climate_backup_rows}; reported_requirements={priority_climate_requirements}; source_ready_rows={priority_climate_source_ready_rows}; accepted_chirps_era5_rows={priority_accepted_chirps_era5_rows}; route_preflight_ready_rows={priority_route_preflight_ready_rows}; blocked_raw_timing_geo_rows={priority_climate_blocked_rows}; handoff_rows={priority_climate_handoff_rows}; handoff_existing={priority_climate_handoff_existing}; source_groups_ready={priority_climate_source_groups_ready}; modeling_gate={priority_climate_modeling_gate}",
        ""
        if counts["priority_climate_linkage_preflight"] >= counts["priority_promotion_acquisition_wave_plan"]
        and counts["priority_climate_linkage_requirements"] >= counts["priority_promotion_acquisition_wave_plan"]
        and counts["priority_climate_linkage_preflight_summary"] > 0
        and file_ok(REPORT_DIR / "priority_climate_linkage_preflight.md")
        and priority_climate_rows >= 10
        and priority_climate_batch_rows >= 10
        and priority_climate_countries >= 5
        and priority_climate_backup_rows >= 1
        and priority_climate_requirements >= priority_climate_rows
        and priority_climate_source_ready_rows >= priority_climate_rows
        and priority_accepted_chirps_era5_rows == 0
        and priority_climate_blocked_rows + priority_route_preflight_ready_rows >= priority_climate_rows
        and priority_climate_handoff_rows >= priority_climate_rows
        and priority_climate_handoff_existing >= priority_climate_rows
        and priority_climate_source_groups_ready >= 3
        and priority_climate_modeling_gate == "blocked"
        else "Run script/125_build_priority_climate_linkage_preflight.py after climate validation protocol and priority raw intake gate exist.",
    )
    priority_raw_verification_summary = read_csv_dicts(RESULT_DIR / "priority_raw_verification_workbook_summary.csv")
    priority_dataset_gate_rows = safe_int(next((row.get("value", "0") for row in priority_raw_verification_summary if row.get("metric") == "priority_dataset_verification_gate_rows"), "0"), 0)
    priority_verification_batch_rows = safe_int(next((row.get("value", "0") for row in priority_raw_verification_summary if row.get("metric") == "priority_verification_priority_10_rows"), "0"), 0)
    priority_verification_countries = safe_int(next((row.get("value", "0") for row in priority_raw_verification_summary if row.get("metric") == "priority_verification_priority_10_countries"), "0"), 0)
    priority_verification_backup_rows = safe_int(next((row.get("value", "0") for row in priority_raw_verification_summary if row.get("metric") == "priority_verification_backup_rows"), "0"), 0)
    priority_requirement_rows = safe_int(next((row.get("value", "0") for row in priority_raw_verification_summary if row.get("metric") == "priority_requirement_checklist_rows"), "0"), 0)
    priority_concept_rows = safe_int(next((row.get("value", "0") for row in priority_raw_verification_summary if row.get("metric") == "priority_concept_template_rows"), "0"), 0)
    priority_variable_rows = safe_int(next((row.get("value", "0") for row in priority_raw_verification_summary if row.get("metric") == "priority_variable_template_rows"), "0"), 0)
    priority_datasets_ready = safe_int(next((row.get("value", "0") for row in priority_raw_verification_summary if row.get("metric") == "priority_datasets_ready_for_manual_value_audit"), "0"), 0)
    priority_requirements_ready = safe_int(next((row.get("value", "0") for row in priority_raw_verification_summary if row.get("metric") == "priority_requirements_ready_for_manual_audit"), "0"), 0)
    priority_raw_verification_handoffs = safe_int(next((row.get("value", "0") for row in priority_raw_verification_summary if row.get("metric") == "priority_raw_verification_handoff_readmes_written"), "0"), 0)
    priority_raw_verification_blocked = safe_int(next((row.get("value", "0") for row in priority_raw_verification_summary if row.get("metric") == "dataset_gate_blocked_raw_files_absent"), "0"), 0)
    priority_raw_verification_modeling_gate = next((row.get("value", "") for row in priority_raw_verification_summary if row.get("metric") == "modeling_gate_status"), "")
    priority_dataset_gate = read_csv_dicts(RESULT_DIR / "priority_dataset_verification_gate.csv")
    priority_raw_verification_handoff_existing = sum(1 for row in priority_dataset_gate if row.get("handoff_readme") and file_ok(PROJECT_ROOT / row.get("handoff_readme", "")))
    expected_priority_requirements = counts["priority_promotion_acquisition_wave_plan"] * 8
    add(
        rows,
        "dataset_promotion",
        "Priority raw verification workbook converts required promotion checks into fillable fail-closed dataset, requirement, concept, and variable gates",
        status(
            counts["priority_dataset_verification_gate"] >= counts["priority_promotion_acquisition_wave_plan"]
            and counts["priority_promotion_verification_checklist"] >= expected_priority_requirements
            and counts["priority_concept_verification_template"] >= counts["priority_promotion_acquisition_wave_plan"]
            and counts["priority_variable_verification_template"] >= counts["priority_raw_file_targets"]
            and counts["priority_raw_verification_workbook_summary"] > 0
            and file_ok(REPORT_DIR / "priority_raw_verification_workbook.md")
            and priority_dataset_gate_rows >= counts["priority_promotion_acquisition_wave_plan"]
            and priority_verification_batch_rows >= 10
            and priority_verification_countries >= 5
            and priority_verification_backup_rows >= 1
            and priority_requirement_rows >= expected_priority_requirements
            and priority_concept_rows >= counts["priority_promotion_acquisition_wave_plan"]
            and priority_variable_rows >= counts["priority_raw_file_targets"]
            and priority_datasets_ready == 0
            and priority_requirements_ready == 0
            and priority_raw_verification_blocked >= counts["priority_promotion_acquisition_wave_plan"]
            and priority_raw_verification_handoffs >= priority_dataset_gate_rows
            and priority_raw_verification_handoff_existing >= priority_dataset_gate_rows
            and priority_raw_verification_modeling_gate == "blocked"
        ),
        f"dataset_gate_rows={counts['priority_dataset_verification_gate']}; requirement_rows={counts['priority_promotion_verification_checklist']}; concept_rows={counts['priority_concept_verification_template']}; variable_rows={counts['priority_variable_verification_template']}; summary_rows={counts['priority_raw_verification_workbook_summary']}; reported_dataset_rows={priority_dataset_gate_rows}; priority_10_rows={priority_verification_batch_rows}; priority_countries={priority_verification_countries}; backup_rows={priority_verification_backup_rows}; reported_requirements={priority_requirement_rows}; reported_concepts={priority_concept_rows}; reported_variables={priority_variable_rows}; datasets_ready={priority_datasets_ready}; requirements_ready={priority_requirements_ready}; blocked_raw_files={priority_raw_verification_blocked}; handoff_rows={priority_raw_verification_handoffs}; handoff_existing={priority_raw_verification_handoff_existing}; modeling_gate={priority_raw_verification_modeling_gate}",
        ""
        if counts["priority_dataset_verification_gate"] >= counts["priority_promotion_acquisition_wave_plan"]
        and counts["priority_promotion_verification_checklist"] >= expected_priority_requirements
        and counts["priority_concept_verification_template"] >= counts["priority_promotion_acquisition_wave_plan"]
        and counts["priority_variable_verification_template"] >= counts["priority_raw_file_targets"]
        and counts["priority_raw_verification_workbook_summary"] > 0
        and file_ok(REPORT_DIR / "priority_raw_verification_workbook.md")
        and priority_dataset_gate_rows >= counts["priority_promotion_acquisition_wave_plan"]
        and priority_verification_batch_rows >= 10
        and priority_verification_countries >= 5
        and priority_verification_backup_rows >= 1
        and priority_requirement_rows >= expected_priority_requirements
        and priority_concept_rows >= counts["priority_promotion_acquisition_wave_plan"]
        and priority_variable_rows >= counts["priority_raw_file_targets"]
        and priority_datasets_ready == 0
        and priority_requirements_ready == 0
        and priority_raw_verification_blocked >= counts["priority_promotion_acquisition_wave_plan"]
        and priority_raw_verification_handoffs >= priority_dataset_gate_rows
        and priority_raw_verification_handoff_existing >= priority_dataset_gate_rows
        and priority_raw_verification_modeling_gate == "blocked"
        else "Run script/126_build_priority_raw_verification_workbook.py after priority raw intake and climate preflight gates exist.",
    )
    priority_manual_summary = read_csv_dicts(RESULT_DIR / "priority_manual_verification_decision_summary.csv")
    priority_manual_dataset_rows = safe_int(next((row.get("value", "0") for row in priority_manual_summary if row.get("metric") == "priority_manual_decision_dataset_rows"), "0"), 0)
    priority_manual_requirement_rows = safe_int(next((row.get("value", "0") for row in priority_manual_summary if row.get("metric") == "priority_manual_requirement_decision_rows"), "0"), 0)
    priority_manual_concept_rows = safe_int(next((row.get("value", "0") for row in priority_manual_summary if row.get("metric") == "priority_manual_concept_decision_rows"), "0"), 0)
    priority_manual_variable_rows = safe_int(next((row.get("value", "0") for row in priority_manual_summary if row.get("metric") == "priority_manual_variable_decision_rows"), "0"), 0)
    priority_manual_requirements_verified = safe_int(next((row.get("value", "0") for row in priority_manual_summary if row.get("metric") == "priority_manual_requirements_verified"), "0"), 0)
    priority_manual_concepts_verified = safe_int(next((row.get("value", "0") for row in priority_manual_summary if row.get("metric") == "priority_manual_concepts_verified"), "0"), 0)
    priority_manual_variables_verified = safe_int(next((row.get("value", "0") for row in priority_manual_summary if row.get("metric") == "priority_manual_variables_verified"), "0"), 0)
    priority_manual_financial_ready = safe_int(next((row.get("value", "0") for row in priority_manual_summary if row.get("metric") == "priority_financial_protection_manual_ready_countries"), "0"), 0)
    priority_manual_double_failure_ready = safe_int(next((row.get("value", "0") for row in priority_manual_summary if row.get("metric") == "priority_double_failure_manual_ready_waves"), "0"), 0)
    priority_manual_analysis_ready = safe_int(next((row.get("value", "0") for row in priority_manual_summary if row.get("metric") == "priority_analysis_ready_candidates"), "0"), 0)
    priority_manual_handoffs = safe_int(next((row.get("value", "0") for row in priority_manual_summary if row.get("metric") == "priority_manual_handoff_readmes_written"), "0"), 0)
    priority_manual_modeling_gate = next((row.get("value", "") for row in priority_manual_summary if row.get("metric") == "modeling_gate_status"), "")
    priority_manual_dataset_gate = read_csv_dicts(TEMP_DIR / "priority_manual_verification_decision_gate.csv")
    priority_manual_handoff_existing = sum(1 for row in priority_manual_dataset_gate if row.get("handoff_readme") and file_ok(PROJECT_ROOT / row.get("handoff_readme", "")))
    priority_manual_no_raw_present = (
        priority_archive_files_found == 0
        and priority_direct_covered == 0
        and priority_archive_covered == 0
        and priority_archive_missing >= counts["priority_raw_file_targets"]
    )
    priority_manual_zero_ready_ok = (
        not priority_manual_no_raw_present
        or (
            priority_manual_requirements_verified == 0
            and priority_manual_concepts_verified == 0
            and priority_manual_variables_verified == 0
            and priority_manual_financial_ready == 0
            and priority_manual_double_failure_ready == 0
            and priority_manual_analysis_ready == 0
        )
    )
    priority_manual_gate_ok = (
        counts["priority_manual_verification_decision_gate"] >= counts["priority_promotion_acquisition_wave_plan"]
        and counts["priority_manual_requirement_decision_audit"] >= counts["priority_promotion_verification_checklist"]
        and counts["priority_manual_concept_decision_audit"] >= counts["priority_concept_verification_template"]
        and counts["priority_manual_variable_decision_audit"] >= counts["priority_variable_verification_template"]
        and counts["priority_manual_verification_decision_summary"] > 0
        and file_ok(REPORT_DIR / "priority_manual_verification_decision_gate.md")
        and priority_manual_dataset_rows >= max(13, counts["priority_promotion_acquisition_wave_plan"])
        and priority_manual_requirement_rows >= max(104, counts["priority_promotion_verification_checklist"])
        and priority_manual_concept_rows >= max(169, counts["priority_concept_verification_template"])
        and priority_manual_variable_rows >= max(1214, counts["priority_variable_verification_template"])
        and priority_manual_zero_ready_ok
        and priority_manual_handoffs >= priority_manual_dataset_rows
        and priority_manual_handoff_existing >= priority_manual_dataset_rows
        and priority_manual_modeling_gate == "blocked"
    )
    add(
        rows,
        "dataset_promotion",
        "Priority manual verification decision gate consumes preserved fill-field evidence and remains fail-closed until raw-backed manual verification passes",
        status(priority_manual_gate_ok),
        f"dataset_rows={counts['priority_manual_verification_decision_gate']}; requirement_rows={counts['priority_manual_requirement_decision_audit']}; concept_rows={counts['priority_manual_concept_decision_audit']}; variable_rows={counts['priority_manual_variable_decision_audit']}; summary_rows={counts['priority_manual_verification_decision_summary']}; reported_dataset_rows={priority_manual_dataset_rows}; reported_requirements={priority_manual_requirement_rows}; reported_concepts={priority_manual_concept_rows}; reported_variables={priority_manual_variable_rows}; verified_requirements={priority_manual_requirements_verified}; verified_concepts={priority_manual_concepts_verified}; verified_variables={priority_manual_variables_verified}; financial_ready_countries={priority_manual_financial_ready}; double_failure_ready_waves={priority_manual_double_failure_ready}; analysis_ready_candidates={priority_manual_analysis_ready}; handoff_rows={priority_manual_handoffs}; handoff_existing={priority_manual_handoff_existing}; no_raw_present={priority_manual_no_raw_present}; modeling_gate={priority_manual_modeling_gate}",
        "" if priority_manual_gate_ok else "Run script/129_build_priority_manual_verification_decision_gate.py after script/126_build_priority_raw_verification_workbook.py; blank or ambiguous fill-fields must remain blocked.",
    )
    priority_receipt_summary = read_csv_dicts(RESULT_DIR / "priority_raw_package_receipt_summary.csv")
    priority_receipt_dataset_rows = safe_int(next((row.get("value", "0") for row in priority_receipt_summary if row.get("metric") == "priority_raw_receipt_dataset_rows"), "0"), 0)
    priority_receipt_original_file_rows = safe_int(next((row.get("value", "0") for row in priority_receipt_summary if row.get("metric") == "priority_raw_receipt_original_file_rows"), "0"), 0)
    priority_receipt_archive_files = safe_int(next((row.get("value", "0") for row in priority_receipt_summary if row.get("metric") == "priority_raw_receipt_archive_files"), "0"), 0)
    priority_receipt_raw_tabular_files = safe_int(next((row.get("value", "0") for row in priority_receipt_summary if row.get("metric") == "priority_raw_receipt_raw_tabular_files"), "0"), 0)
    priority_receipt_documentation_files = safe_int(next((row.get("value", "0") for row in priority_receipt_summary if row.get("metric") == "priority_raw_receipt_documentation_files"), "0"), 0)
    priority_receipt_targets = safe_int(next((row.get("value", "0") for row in priority_receipt_summary if row.get("metric") == "priority_raw_receipt_priority_targets"), "0"), 0)
    priority_receipt_targets_covered = safe_int(next((row.get("value", "0") for row in priority_receipt_summary if row.get("metric") == "priority_raw_receipt_priority_targets_covered"), "0"), 0)
    priority_receipt_targets_missing = safe_int(next((row.get("value", "0") for row in priority_receipt_summary if row.get("metric") == "priority_raw_receipt_priority_targets_missing"), "0"), 0)
    priority_receipt_missing_target_rows = safe_int(next((row.get("value", "0") for row in priority_receipt_summary if row.get("metric") == "priority_raw_receipt_missing_target_rows"), "0"), 0)
    priority_receipt_generated_ignored = safe_int(next((row.get("value", "0") for row in priority_receipt_summary if row.get("metric") == "priority_raw_receipt_generated_files_ignored"), "0"), 0)
    priority_receipt_complete_candidates = safe_int(next((row.get("value", "0") for row in priority_receipt_summary if row.get("metric") == "priority_raw_receipt_complete_package_candidates"), "0"), 0)
    priority_receipt_partial_candidates = safe_int(next((row.get("value", "0") for row in priority_receipt_summary if row.get("metric") == "priority_raw_receipt_partial_package_candidates"), "0"), 0)
    priority_receipt_missing_packages = safe_int(next((row.get("value", "0") for row in priority_receipt_summary if row.get("metric") == "priority_raw_receipt_missing_package_rows"), "0"), 0)
    priority_receipt_modeling_gate = next((row.get("value", "") for row in priority_receipt_summary if row.get("metric") == "modeling_gate_status"), "")
    priority_receipt_no_raw_ok = (
        not priority_manual_no_raw_present
        or (
            priority_receipt_original_file_rows == 0
            and priority_receipt_archive_files == 0
            and priority_receipt_raw_tabular_files == 0
            and priority_receipt_documentation_files == 0
            and priority_receipt_targets_covered == 0
            and priority_receipt_targets_missing >= counts["priority_raw_file_targets"]
            and priority_receipt_missing_target_rows >= counts["priority_raw_file_targets"]
            and priority_receipt_complete_candidates == 0
            and priority_receipt_partial_candidates == 0
            and priority_receipt_missing_packages >= counts["priority_promotion_acquisition_wave_plan"]
        )
    )
    priority_receipt_gate_ok = (
        counts["priority_raw_package_receipt_ledger"] >= counts["priority_promotion_acquisition_wave_plan"]
        and counts["priority_raw_package_file_manifest"] == priority_receipt_original_file_rows
        and (not priority_manual_no_raw_present or counts["priority_raw_package_missing_targets"] >= counts["priority_raw_file_targets"])
        and counts["priority_raw_package_receipt_summary"] > 0
        and file_ok(REPORT_DIR / "priority_raw_package_receipt_ledger.md")
        and priority_receipt_dataset_rows >= max(13, counts["priority_promotion_acquisition_wave_plan"])
        and priority_receipt_targets >= counts["priority_raw_file_targets"]
        and priority_receipt_generated_ignored >= counts["priority_promotion_acquisition_wave_plan"]
        and priority_receipt_no_raw_ok
        and priority_receipt_modeling_gate == "blocked"
    )
    add(
        rows,
        "dataset_promotion",
        "Priority raw package receipt ledger hashes original receipts, ignores generated handoffs, and preserves fail-closed package completeness status",
        status(priority_receipt_gate_ok),
        f"ledger_rows={counts['priority_raw_package_receipt_ledger']}; file_manifest_rows={counts['priority_raw_package_file_manifest']}; missing_target_rows={counts['priority_raw_package_missing_targets']}; summary_rows={counts['priority_raw_package_receipt_summary']}; reported_dataset_rows={priority_receipt_dataset_rows}; original_files={priority_receipt_original_file_rows}; archives={priority_receipt_archive_files}; raw_tabular={priority_receipt_raw_tabular_files}; documentation={priority_receipt_documentation_files}; targets={priority_receipt_targets}; covered={priority_receipt_targets_covered}; missing={priority_receipt_targets_missing}; missing_rows={priority_receipt_missing_target_rows}; generated_ignored={priority_receipt_generated_ignored}; complete_candidates={priority_receipt_complete_candidates}; partial_candidates={priority_receipt_partial_candidates}; missing_packages={priority_receipt_missing_packages}; no_raw_present={priority_manual_no_raw_present}; modeling_gate={priority_receipt_modeling_gate}",
        "" if priority_receipt_gate_ok else "Run script/130_build_priority_raw_package_receipt_ledger.py after priority archive/manual gates; generated handoff files must not count as original package evidence.",
    )
    priority_official_summary = read_csv_dicts(RESULT_DIR / "priority_official_download_dossier_summary.csv")
    priority_official_dossier_rows = safe_int(next((row.get("value", "0") for row in priority_official_summary if row.get("metric") == "priority_official_download_dossier_rows"), "0"), 0)
    priority_official_full_file_rows = safe_int(next((row.get("value", "0") for row in priority_official_summary if row.get("metric") == "priority_official_full_file_inventory_rows"), "0"), 0)
    priority_official_core_rows = safe_int(next((row.get("value", "0") for row in priority_official_summary if row.get("metric") == "priority_official_priority_core_file_rows"), "0"), 0)
    priority_official_link_rows = safe_int(next((row.get("value", "0") for row in priority_official_summary if row.get("metric") == "priority_official_documentation_link_rows"), "0"), 0)
    priority_official_pdf_links = safe_int(next((row.get("value", "0") for row in priority_official_summary if row.get("metric") == "priority_official_pdf_documentation_links"), "0"), 0)
    priority_official_ddi_links = safe_int(next((row.get("value", "0") for row in priority_official_summary if row.get("metric") == "priority_official_ddi_metadata_links"), "0"), 0)
    priority_official_json_links = safe_int(next((row.get("value", "0") for row in priority_official_summary if row.get("metric") == "priority_official_json_metadata_links"), "0"), 0)
    priority_official_data_dictionary_links = safe_int(next((row.get("value", "0") for row in priority_official_summary if row.get("metric") == "priority_official_data_dictionary_links"), "0"), 0)
    priority_official_no_package_rows = safe_int(next((row.get("value", "0") for row in priority_official_summary if row.get("metric") == "priority_official_no_original_package_rows"), "0"), 0)
    priority_official_receipt_candidates = safe_int(next((row.get("value", "0") for row in priority_official_summary if row.get("metric") == "priority_official_receipt_candidates"), "0"), 0)
    priority_official_modeling_gate = next((row.get("value", "") for row in priority_official_summary if row.get("metric") == "modeling_gate_status"), "")
    priority_official_gate_ok = (
        counts["priority_official_download_dossier"] >= counts["priority_promotion_acquisition_wave_plan"]
        and counts["priority_official_full_file_inventory"] >= 965
        and counts["priority_official_documentation_links"] >= counts["priority_promotion_acquisition_wave_plan"]
        and counts["priority_official_download_dossier_summary"] > 0
        and file_ok(REPORT_DIR / "priority_official_download_dossier.md")
        and priority_official_dossier_rows >= max(13, counts["priority_promotion_acquisition_wave_plan"])
        and priority_official_full_file_rows >= 965
        and priority_official_core_rows >= counts["priority_raw_file_targets"]
        and priority_official_link_rows >= counts["priority_promotion_acquisition_wave_plan"]
        and priority_official_ddi_links >= counts["priority_promotion_acquisition_wave_plan"]
        and priority_official_json_links >= counts["priority_promotion_acquisition_wave_plan"]
        and priority_official_data_dictionary_links >= counts["priority_promotion_acquisition_wave_plan"]
        and priority_official_pdf_links >= 10
        and (not priority_manual_no_raw_present or priority_official_no_package_rows >= counts["priority_promotion_acquisition_wave_plan"])
        and (not priority_manual_no_raw_present or priority_official_receipt_candidates == 0)
        and priority_official_modeling_gate == "blocked"
    )
    add(
        rows,
        "dataset_promotion",
        "Priority official download dossier expands from core targets to full metadata file inventories and official access/documentation links",
        status(priority_official_gate_ok),
        f"dossier_rows={counts['priority_official_download_dossier']}; full_inventory_rows={counts['priority_official_full_file_inventory']}; documentation_link_rows={counts['priority_official_documentation_links']}; summary_rows={counts['priority_official_download_dossier_summary']}; reported_dossiers={priority_official_dossier_rows}; reported_full_files={priority_official_full_file_rows}; reported_core_files={priority_official_core_rows}; links={priority_official_link_rows}; pdf={priority_official_pdf_links}; ddi={priority_official_ddi_links}; json={priority_official_json_links}; data_dictionary={priority_official_data_dictionary_links}; no_package_rows={priority_official_no_package_rows}; receipt_candidates={priority_official_receipt_candidates}; no_raw_present={priority_manual_no_raw_present}; modeling_gate={priority_official_modeling_gate}",
        "" if priority_official_gate_ok else "Run script/131_build_priority_official_download_dossier.py after priority receipt ledger; official links and full metadata file inventory must be present.",
    )
    priority_public_doc_summary = read_csv_dicts(RESULT_DIR / "priority_public_documentation_receipt_summary.csv")
    priority_public_doc_dataset_rows = safe_int(next((row.get("value", "0") for row in priority_public_doc_summary if row.get("metric") == "priority_public_documentation_dataset_rows"), "0"), 0)
    priority_public_doc_resource_rows = safe_int(next((row.get("value", "0") for row in priority_public_doc_summary if row.get("metric") == "priority_public_documentation_resource_rows"), "0"), 0)
    priority_public_doc_saved_rows = safe_int(next((row.get("value", "0") for row in priority_public_doc_summary if row.get("metric") == "priority_public_documentation_saved_rows"), "0"), 0)
    priority_public_doc_failed_rows = safe_int(next((row.get("value", "0") for row in priority_public_doc_summary if row.get("metric") == "priority_public_documentation_failed_rows"), "0"), 0)
    priority_public_doc_core_complete_rows = safe_int(next((row.get("value", "0") for row in priority_public_doc_summary if row.get("metric") == "priority_public_documentation_core_complete_dataset_rows"), "0"), 0)
    priority_public_doc_full_complete_rows = safe_int(next((row.get("value", "0") for row in priority_public_doc_summary if row.get("metric") == "priority_public_documentation_full_complete_dataset_rows"), "0"), 0)
    priority_public_doc_optional_pdf_missing_rows = safe_int(next((row.get("value", "0") for row in priority_public_doc_summary if row.get("metric") == "priority_public_documentation_optional_pdf_missing_dataset_rows"), "0"), 0)
    priority_public_doc_access_gate_rows = safe_int(next((row.get("value", "0") for row in priority_public_doc_summary if row.get("metric") == "priority_public_documentation_access_gate_rows"), "0"), 0)
    priority_public_doc_handoffs = safe_int(next((row.get("value", "0") for row in priority_public_doc_summary if row.get("metric") == "priority_public_documentation_handoff_readmes_written"), "0"), 0)
    priority_public_doc_modeling_gate = next((row.get("value", "") for row in priority_public_doc_summary if row.get("metric") == "modeling_gate_status"), "")
    priority_public_doc_gate_ok = (
        counts["priority_public_documentation_receipt"] >= counts["priority_promotion_acquisition_wave_plan"] * 6
        and counts["priority_public_documentation_dataset_receipt"] >= counts["priority_promotion_acquisition_wave_plan"]
        and counts["priority_public_documentation_receipt_summary"] > 0
        and file_ok(REPORT_DIR / "priority_public_documentation_receipt.md")
        and priority_public_doc_dataset_rows >= counts["priority_promotion_acquisition_wave_plan"]
        and priority_public_doc_resource_rows >= counts["priority_promotion_acquisition_wave_plan"] * 6
        and priority_public_doc_saved_rows >= 76
        and priority_public_doc_failed_rows == 0
        and priority_public_doc_core_complete_rows >= counts["priority_promotion_acquisition_wave_plan"]
        and priority_public_doc_full_complete_rows >= 10
        and priority_public_doc_optional_pdf_missing_rows <= 3
        and priority_public_doc_access_gate_rows >= counts["priority_promotion_acquisition_wave_plan"]
        and priority_public_doc_handoffs >= counts["priority_promotion_acquisition_wave_plan"]
        and priority_public_doc_modeling_gate == "blocked"
    )
    add(
        rows,
        "dataset_promotion",
        "Priority public documentation receipt saves official public metadata/documentation while preserving raw access blockers",
        status(priority_public_doc_gate_ok),
        f"receipt_rows={counts['priority_public_documentation_receipt']}; dataset_rows={counts['priority_public_documentation_dataset_receipt']}; summary_rows={counts['priority_public_documentation_receipt_summary']}; reported_datasets={priority_public_doc_dataset_rows}; resources={priority_public_doc_resource_rows}; saved={priority_public_doc_saved_rows}; failed={priority_public_doc_failed_rows}; core_complete={priority_public_doc_core_complete_rows}; full_complete={priority_public_doc_full_complete_rows}; optional_pdf_missing={priority_public_doc_optional_pdf_missing_rows}; access_gates={priority_public_doc_access_gate_rows}; handoffs={priority_public_doc_handoffs}; modeling_gate={priority_public_doc_modeling_gate}",
        "" if priority_public_doc_gate_ok else "Run script/133_build_priority_public_documentation_receipt.py after the priority official download dossier exists; public core documentation must be saved or reused without raw promotion.",
    )
    priority_metadata_summary = read_csv_dicts(RESULT_DIR / "priority_official_metadata_evidence_summary.csv")
    priority_metadata_dataset_rows = safe_int(next((row.get("value", "0") for row in priority_metadata_summary if row.get("metric") == "priority_official_metadata_dataset_rows"), "0"), 0)
    priority_metadata_candidate_rows = safe_int(next((row.get("value", "0") for row in priority_metadata_summary if row.get("metric") == "priority_official_metadata_candidate_variable_rows"), "0"), 0)
    priority_metadata_category_rows = safe_int(next((row.get("value", "0") for row in priority_metadata_summary if row.get("metric") == "priority_official_metadata_category_rows"), "0"), 0)
    priority_metadata_match_rows = safe_int(next((row.get("value", "0") for row in priority_metadata_summary if row.get("metric") == "priority_official_metadata_variable_match_rows"), "0"), 0)
    priority_metadata_file_match_rows = safe_int(next((row.get("value", "0") for row in priority_metadata_summary if row.get("metric") == "priority_official_metadata_variable_file_match_rows"), "0"), 0)
    priority_metadata_no_match_rows = safe_int(next((row.get("value", "0") for row in priority_metadata_summary if row.get("metric") == "priority_official_metadata_no_match_rows"), "0"), 0)
    priority_metadata_with_categories = safe_int(next((row.get("value", "0") for row in priority_metadata_summary if row.get("metric") == "priority_official_metadata_variables_with_categories"), "0"), 0)
    priority_metadata_with_valid_counts = safe_int(next((row.get("value", "0") for row in priority_metadata_summary if row.get("metric") == "priority_official_metadata_variables_with_valid_counts"), "0"), 0)
    priority_metadata_with_invalid_counts = safe_int(next((row.get("value", "0") for row in priority_metadata_summary if row.get("metric") == "priority_official_metadata_variables_with_invalid_counts"), "0"), 0)
    priority_metadata_complete_rows = safe_int(next((row.get("value", "0") for row in priority_metadata_summary if row.get("metric") == "priority_official_metadata_dataset_complete_rows"), "0"), 0)
    priority_metadata_handoffs = safe_int(next((row.get("value", "0") for row in priority_metadata_summary if row.get("metric") == "priority_official_metadata_handoff_readmes_written"), "0"), 0)
    priority_metadata_modeling_gate = next((row.get("value", "") for row in priority_metadata_summary if row.get("metric") == "modeling_gate_status"), "")
    priority_metadata_gate_ok = (
        counts["priority_official_metadata_variable_evidence"] >= 1214
        and counts["priority_official_metadata_category_evidence"] >= 4500
        and counts["priority_official_metadata_dataset_evidence"] >= counts["priority_promotion_acquisition_wave_plan"]
        and counts["priority_official_metadata_evidence_summary"] > 0
        and file_ok(REPORT_DIR / "priority_official_metadata_evidence_extract.md")
        and priority_metadata_dataset_rows >= counts["priority_promotion_acquisition_wave_plan"]
        and priority_metadata_candidate_rows >= 1214
        and priority_metadata_category_rows >= 4500
        and priority_metadata_match_rows >= 1190
        and priority_metadata_file_match_rows >= 1190
        and priority_metadata_no_match_rows <= 20
        and priority_metadata_with_categories >= 700
        and priority_metadata_with_valid_counts >= 1100
        and priority_metadata_with_invalid_counts >= 800
        and priority_metadata_complete_rows >= 3
        and priority_metadata_handoffs >= counts["priority_promotion_acquisition_wave_plan"]
        and priority_metadata_modeling_gate == "blocked"
    )
    add(
        rows,
        "dataset_promotion",
        "Priority official metadata evidence extract links candidate variables to official DDI/XML labels, categories, counts, and file mappings",
        status(priority_metadata_gate_ok),
        f"variable_rows={counts['priority_official_metadata_variable_evidence']}; category_rows={counts['priority_official_metadata_category_evidence']}; dataset_rows={counts['priority_official_metadata_dataset_evidence']}; summary_rows={counts['priority_official_metadata_evidence_summary']}; reported_datasets={priority_metadata_dataset_rows}; candidate_variables={priority_metadata_candidate_rows}; categories={priority_metadata_category_rows}; variable_matches={priority_metadata_match_rows}; file_matches={priority_metadata_file_match_rows}; no_matches={priority_metadata_no_match_rows}; variables_with_categories={priority_metadata_with_categories}; valid_counts={priority_metadata_with_valid_counts}; invalid_counts={priority_metadata_with_invalid_counts}; complete_datasets={priority_metadata_complete_rows}; handoffs={priority_metadata_handoffs}; modeling_gate={priority_metadata_modeling_gate}",
        "" if priority_metadata_gate_ok else "Run script/135_build_priority_official_metadata_evidence_extract.py after the public documentation receipt; metadata evidence is not raw value verification.",
    )
    priority_credentialed_summary = read_csv_dicts(RESULT_DIR / "priority_credentialed_raw_acquisition_summary.csv")
    priority_credentialed_dataset_rows = safe_int(next((row.get("value", "0") for row in priority_credentialed_summary if row.get("metric") == "priority_credentialed_acquisition_dataset_rows"), "0"), 0)
    priority_credentialed_priority_rows = safe_int(next((row.get("value", "0") for row in priority_credentialed_summary if row.get("metric") == "priority_credentialed_acquisition_priority_batch_rows"), "0"), 0)
    priority_credentialed_backup_rows = safe_int(next((row.get("value", "0") for row in priority_credentialed_summary if row.get("metric") == "priority_credentialed_acquisition_backup_rows"), "0"), 0)
    priority_credentialed_full_rows = safe_int(next((row.get("value", "0") for row in priority_credentialed_summary if row.get("metric") == "priority_credentialed_acquisition_full_file_rows"), "0"), 0)
    priority_credentialed_core_rows = safe_int(next((row.get("value", "0") for row in priority_credentialed_summary if row.get("metric") == "priority_credentialed_acquisition_core_file_rows"), "0"), 0)
    priority_credentialed_public_ready = safe_int(next((row.get("value", "0") for row in priority_credentialed_summary if row.get("metric") == "priority_credentialed_acquisition_public_documentation_ready_rows"), "0"), 0)
    priority_credentialed_metadata_ready = safe_int(next((row.get("value", "0") for row in priority_credentialed_summary if row.get("metric") == "priority_credentialed_acquisition_official_metadata_ready_rows"), "0"), 0)
    priority_credentialed_original_receipts = safe_int(next((row.get("value", "0") for row in priority_credentialed_summary if row.get("metric") == "priority_credentialed_acquisition_original_package_receipt_rows"), "0"), 0)
    priority_credentialed_missing_targets = safe_int(next((row.get("value", "0") for row in priority_credentialed_summary if row.get("metric") == "priority_credentialed_acquisition_targets_missing_before_download"), "0"), 0)
    priority_credentialed_handoffs = safe_int(next((row.get("value", "0") for row in priority_credentialed_summary if row.get("metric") == "priority_credentialed_acquisition_handoff_readmes_written"), "0"), 0)
    priority_credentialed_modeling_gate = next((row.get("value", "") for row in priority_credentialed_summary if row.get("metric") == "modeling_gate_status"), "")
    priority_credentialed_gate_ok = (
        counts["priority_credentialed_raw_acquisition_ledger"] >= counts["priority_promotion_acquisition_wave_plan"]
        and counts["priority_credentialed_raw_full_file_manifest"] >= 900
        and counts["priority_credentialed_raw_core_file_checklist"] >= counts["priority_promotion_acquisition_wave_plan"] * 12
        and counts["priority_credentialed_raw_acquisition_summary"] > 0
        and file_ok(REPORT_DIR / "priority_credentialed_raw_acquisition_ledger.md")
        and priority_credentialed_dataset_rows >= counts["priority_promotion_acquisition_wave_plan"]
        and priority_credentialed_priority_rows >= 10
        and priority_credentialed_backup_rows >= 3
        and priority_credentialed_full_rows >= 900
        and priority_credentialed_core_rows >= counts["priority_promotion_acquisition_wave_plan"] * 12
        and priority_credentialed_public_ready >= counts["priority_promotion_acquisition_wave_plan"]
        and priority_credentialed_metadata_ready >= counts["priority_promotion_acquisition_wave_plan"]
        and priority_credentialed_original_receipts == 0
        and priority_credentialed_missing_targets >= counts["priority_promotion_acquisition_wave_plan"] * 12
        and priority_credentialed_handoffs >= counts["priority_promotion_acquisition_wave_plan"]
        and priority_credentialed_modeling_gate == "blocked"
    )
    add(
        rows,
        "dataset_promotion",
        "Priority credentialed raw acquisition ledger converts official get-microdata pages and file inventories into per-wave download handoffs",
        status(priority_credentialed_gate_ok),
        f"ledger_rows={counts['priority_credentialed_raw_acquisition_ledger']}; full_file_rows={counts['priority_credentialed_raw_full_file_manifest']}; core_checklist_rows={counts['priority_credentialed_raw_core_file_checklist']}; summary_rows={counts['priority_credentialed_raw_acquisition_summary']}; reported_datasets={priority_credentialed_dataset_rows}; priority_rows={priority_credentialed_priority_rows}; backup_rows={priority_credentialed_backup_rows}; reported_full_files={priority_credentialed_full_rows}; reported_core_files={priority_credentialed_core_rows}; public_ready={priority_credentialed_public_ready}; metadata_ready={priority_credentialed_metadata_ready}; original_receipts={priority_credentialed_original_receipts}; missing_targets={priority_credentialed_missing_targets}; handoffs={priority_credentialed_handoffs}; modeling_gate={priority_credentialed_modeling_gate}",
        "" if priority_credentialed_gate_ok else "Run script/136_build_priority_credentialed_raw_acquisition_ledger.py after public documentation and official metadata evidence; this prepares credentialed download execution but does not verify raw values.",
    )
    priority_endpoint_summary = read_csv_dicts(RESULT_DIR / "priority_official_endpoint_matrix_summary.csv")
    priority_endpoint_dataset_rows = safe_int(next((row.get("value", "0") for row in priority_endpoint_summary if row.get("metric") == "priority_endpoint_matrix_dataset_rows"), "0"), 0)
    priority_endpoint_rows = safe_int(next((row.get("value", "0") for row in priority_endpoint_summary if row.get("metric") == "priority_endpoint_matrix_endpoint_rows"), "0"), 0)
    priority_endpoint_metadata_rows = safe_int(next((row.get("value", "0") for row in priority_endpoint_summary if row.get("metric") == "priority_endpoint_matrix_public_metadata_endpoint_rows"), "0"), 0)
    priority_endpoint_variable_api_rows = safe_int(next((row.get("value", "0") for row in priority_endpoint_summary if row.get("metric") == "priority_endpoint_matrix_variable_api_dataset_rows"), "0"), 0)
    priority_endpoint_gate_rows = safe_int(next((row.get("value", "0") for row in priority_endpoint_summary if row.get("metric") == "priority_endpoint_matrix_get_microdata_gate_dataset_rows"), "0"), 0)
    priority_endpoint_raw_candidates = safe_int(next((row.get("value", "0") for row in priority_endpoint_summary if row.get("metric") == "priority_endpoint_matrix_raw_download_candidate_rows"), "0"), 0)
    priority_endpoint_credentialed_required = safe_int(next((row.get("value", "0") for row in priority_endpoint_summary if row.get("metric") == "priority_endpoint_matrix_credentialed_download_required_rows"), "0"), 0)
    priority_endpoint_handoffs = safe_int(next((row.get("value", "0") for row in priority_endpoint_summary if row.get("metric") == "priority_endpoint_matrix_handoff_readmes_written"), "0"), 0)
    priority_endpoint_modeling_gate = next((row.get("value", "") for row in priority_endpoint_summary if row.get("metric") == "modeling_gate_status"), "")
    priority_endpoint_gate_ok = (
        counts["priority_official_endpoint_matrix"] >= counts["priority_promotion_acquisition_wave_plan"] * 8
        and counts["priority_official_endpoint_dataset_matrix"] >= counts["priority_promotion_acquisition_wave_plan"]
        and counts["priority_official_endpoint_matrix_summary"] > 0
        and file_ok(REPORT_DIR / "priority_official_endpoint_matrix.md")
        and priority_endpoint_dataset_rows >= counts["priority_promotion_acquisition_wave_plan"]
        and priority_endpoint_rows >= counts["priority_promotion_acquisition_wave_plan"] * 8
        and priority_endpoint_metadata_rows >= counts["priority_promotion_acquisition_wave_plan"] * 4
        and priority_endpoint_variable_api_rows >= 12
        and priority_endpoint_gate_rows >= counts["priority_promotion_acquisition_wave_plan"]
        and priority_endpoint_raw_candidates == 0
        and priority_endpoint_credentialed_required >= counts["priority_promotion_acquisition_wave_plan"]
        and priority_endpoint_handoffs >= counts["priority_promotion_acquisition_wave_plan"]
        and priority_endpoint_modeling_gate == "blocked"
    )
    add(
        rows,
        "dataset_promotion",
        "Priority official endpoint matrix confirms public API routes are metadata-only and official raw access remains credentialed",
        status(priority_endpoint_gate_ok),
        f"endpoint_rows={counts['priority_official_endpoint_matrix']}; dataset_rows={counts['priority_official_endpoint_dataset_matrix']}; summary_rows={counts['priority_official_endpoint_matrix_summary']}; reported_datasets={priority_endpoint_dataset_rows}; reported_endpoints={priority_endpoint_rows}; metadata_endpoints={priority_endpoint_metadata_rows}; variable_api_datasets={priority_endpoint_variable_api_rows}; get_microdata_gate_datasets={priority_endpoint_gate_rows}; raw_candidates={priority_endpoint_raw_candidates}; credentialed_required={priority_endpoint_credentialed_required}; handoffs={priority_endpoint_handoffs}; modeling_gate={priority_endpoint_modeling_gate}",
        "" if priority_endpoint_gate_ok else "Run script/137_probe_priority_official_endpoint_matrix.py after the official download dossier; endpoint evidence is metadata/access-gate evidence only.",
    )
    priority_core_file_endpoint_summary = read_csv_dicts(RESULT_DIR / "priority_core_file_endpoint_matrix_summary.csv")
    priority_core_file_endpoint_dataset_rows = safe_int(next((row.get("value", "0") for row in priority_core_file_endpoint_summary if row.get("metric") == "priority_core_file_endpoint_dataset_rows"), "0"), 0)
    priority_core_file_endpoint_core_rows = safe_int(next((row.get("value", "0") for row in priority_core_file_endpoint_summary if row.get("metric") == "priority_core_file_endpoint_core_file_rows"), "0"), 0)
    priority_core_file_endpoint_matrix_rows = safe_int(next((row.get("value", "0") for row in priority_core_file_endpoint_summary if row.get("metric") == "priority_core_file_endpoint_matrix_rows"), "0"), 0)
    priority_core_file_endpoint_metadata_refs = safe_int(next((row.get("value", "0") for row in priority_core_file_endpoint_summary if row.get("metric") == "priority_core_file_endpoint_metadata_reference_rows"), "0"), 0)
    priority_core_file_endpoint_probed_rows = safe_int(next((row.get("value", "0") for row in priority_core_file_endpoint_summary if row.get("metric") == "priority_core_file_endpoint_probed_download_rows"), "0"), 0)
    priority_core_file_endpoint_http_errors = safe_int(next((row.get("value", "0") for row in priority_core_file_endpoint_summary if row.get("metric") == "priority_core_file_endpoint_http_error_rows"), "0"), 0)
    priority_core_file_endpoint_empty_downloads = safe_int(next((row.get("value", "0") for row in priority_core_file_endpoint_summary if row.get("metric") == "priority_core_file_endpoint_empty_download_rows"), "0"), 0)
    priority_core_file_endpoint_request_failed = safe_int(next((row.get("value", "0") for row in priority_core_file_endpoint_summary if row.get("metric") == "priority_core_file_endpoint_request_failed_rows"), "0"), 0)
    priority_core_file_endpoint_raw_candidates = safe_int(next((row.get("value", "0") for row in priority_core_file_endpoint_summary if row.get("metric") == "priority_core_file_endpoint_raw_candidate_rows"), "0"), 0)
    priority_core_file_endpoint_no_public_raw = safe_int(next((row.get("value", "0") for row in priority_core_file_endpoint_summary if row.get("metric") == "priority_core_file_endpoint_download_routes_without_public_raw_rows"), "0"), 0)
    priority_core_file_endpoint_credentialed_required = safe_int(next((row.get("value", "0") for row in priority_core_file_endpoint_summary if row.get("metric") == "priority_core_file_endpoint_credentialed_download_required_rows"), "0"), 0)
    priority_core_file_endpoint_handoffs = safe_int(next((row.get("value", "0") for row in priority_core_file_endpoint_summary if row.get("metric") == "priority_core_file_endpoint_handoff_readmes_written"), "0"), 0)
    priority_core_file_endpoint_modeling_gate = next((row.get("value", "") for row in priority_core_file_endpoint_summary if row.get("metric") == "modeling_gate_status"), "")
    priority_core_file_endpoint_gate_ok = (
        counts["priority_core_file_endpoint_matrix"] >= counts["priority_raw_file_targets"] * 5
        and counts["priority_core_file_endpoint_dataset_matrix"] >= counts["priority_promotion_acquisition_wave_plan"]
        and counts["priority_core_file_endpoint_matrix_summary"] > 0
        and file_ok(REPORT_DIR / "priority_core_file_endpoint_matrix.md")
        and priority_core_file_endpoint_dataset_rows >= counts["priority_promotion_acquisition_wave_plan"]
        and priority_core_file_endpoint_core_rows >= counts["priority_raw_file_targets"]
        and priority_core_file_endpoint_matrix_rows >= counts["priority_raw_file_targets"] * 5
        and priority_core_file_endpoint_metadata_refs >= counts["priority_raw_file_targets"]
        and priority_core_file_endpoint_probed_rows >= counts["priority_raw_file_targets"] * 4
        and priority_core_file_endpoint_no_public_raw >= counts["priority_raw_file_targets"] * 4
        and priority_core_file_endpoint_http_errors + priority_core_file_endpoint_empty_downloads >= counts["priority_raw_file_targets"] * 4
        and priority_core_file_endpoint_request_failed == 0
        and priority_core_file_endpoint_raw_candidates == 0
        and priority_core_file_endpoint_credentialed_required >= counts["priority_promotion_acquisition_wave_plan"]
        and priority_core_file_endpoint_handoffs >= counts["priority_promotion_acquisition_wave_plan"]
        and priority_core_file_endpoint_modeling_gate == "blocked"
    )
    add(
        rows,
        "dataset_promotion",
        "Priority core-file endpoint matrix confirms file-level public routes do not expose accepted raw payloads",
        status(priority_core_file_endpoint_gate_ok),
        f"matrix_rows={counts['priority_core_file_endpoint_matrix']}; dataset_rows={counts['priority_core_file_endpoint_dataset_matrix']}; summary_rows={counts['priority_core_file_endpoint_matrix_summary']}; reported_datasets={priority_core_file_endpoint_dataset_rows}; core_files={priority_core_file_endpoint_core_rows}; reported_matrix_rows={priority_core_file_endpoint_matrix_rows}; metadata_refs={priority_core_file_endpoint_metadata_refs}; probed_download_routes={priority_core_file_endpoint_probed_rows}; http_errors={priority_core_file_endpoint_http_errors}; empty_downloads={priority_core_file_endpoint_empty_downloads}; request_failed={priority_core_file_endpoint_request_failed}; no_public_raw_routes={priority_core_file_endpoint_no_public_raw}; raw_candidates={priority_core_file_endpoint_raw_candidates}; credentialed_required={priority_core_file_endpoint_credentialed_required}; handoffs={priority_core_file_endpoint_handoffs}; modeling_gate={priority_core_file_endpoint_modeling_gate}",
        "" if priority_core_file_endpoint_gate_ok else "Run script/138_probe_priority_core_file_endpoint_matrix.py after the credentialed raw acquisition ledger; file-level endpoint evidence is not raw receipt.",
    )
    priority_threshold_summary = read_csv_dicts(RESULT_DIR / "priority_threshold_acquisition_campaign_summary.csv")
    priority_threshold_dataset_rows = safe_int(next((row.get("value", "0") for row in priority_threshold_summary if row.get("metric") == "priority_threshold_campaign_dataset_rows"), "0"), 0)
    priority_threshold_phase1_rows = safe_int(next((row.get("value", "0") for row in priority_threshold_summary if row.get("metric") == "priority_threshold_campaign_phase1_10_wave_rows"), "0"), 0)
    priority_threshold_phase2_rows = safe_int(next((row.get("value", "0") for row in priority_threshold_summary if row.get("metric") == "priority_threshold_campaign_phase2_sixth_country_backup_rows"), "0"), 0)
    priority_threshold_countries = safe_int(next((row.get("value", "0") for row in priority_threshold_summary if row.get("metric") == "priority_threshold_campaign_distinct_countries"), "0"), 0)
    priority_threshold_core_countries = safe_int(next((row.get("value", "0") for row in priority_threshold_summary if row.get("metric") == "priority_threshold_campaign_core_country_rows"), "0"), 0)
    priority_threshold_backup_countries = safe_int(next((row.get("value", "0") for row in priority_threshold_summary if row.get("metric") == "priority_threshold_campaign_backup_country_rows"), "0"), 0)
    priority_threshold_core_waves = safe_int(next((row.get("value", "0") for row in priority_threshold_summary if row.get("metric") == "priority_threshold_campaign_core_wave_rows"), "0"), 0)
    priority_threshold_backup_waves = safe_int(next((row.get("value", "0") for row in priority_threshold_summary if row.get("metric") == "priority_threshold_campaign_backup_wave_rows"), "0"), 0)
    priority_threshold_minimum_downloads = safe_int(next((row.get("value", "0") for row in priority_threshold_summary if row.get("metric") == "priority_threshold_campaign_minimum_download_rows_for_formal_thresholds"), "0"), 0)
    priority_threshold_recommended_downloads = safe_int(next((row.get("value", "0") for row in priority_threshold_summary if row.get("metric") == "priority_threshold_campaign_recommended_download_rows"), "0"), 0)
    priority_threshold_promoted = safe_int(next((row.get("value", "0") for row in priority_threshold_summary if row.get("metric") == "priority_threshold_campaign_current_promoted_analysis_ready_rows"), "0"), 0)
    priority_threshold_raw_received = safe_int(next((row.get("value", "0") for row in priority_threshold_summary if row.get("metric") == "priority_threshold_campaign_raw_package_received_rows"), "0"), 0)
    priority_threshold_raw_missing = safe_int(next((row.get("value", "0") for row in priority_threshold_summary if row.get("metric") == "priority_threshold_campaign_raw_package_missing_rows"), "0"), 0)
    priority_threshold_core_endpoint_ready = safe_int(next((row.get("value", "0") for row in priority_threshold_summary if row.get("metric") == "priority_threshold_campaign_core_file_endpoint_ready_rows"), "0"), 0)
    priority_threshold_handoffs = safe_int(next((row.get("value", "0") for row in priority_threshold_summary if row.get("metric") == "priority_threshold_campaign_handoff_readmes_written"), "0"), 0)
    priority_threshold_modeling_gate = next((row.get("value", "") for row in priority_threshold_summary if row.get("metric") == "modeling_gate_status"), "")
    priority_threshold_gate_ok = (
        counts["priority_threshold_acquisition_campaign"] >= counts["priority_promotion_acquisition_wave_plan"]
        and counts["priority_threshold_country_coverage"] >= 8
        and counts["priority_threshold_acquisition_campaign_summary"] > 0
        and file_ok(REPORT_DIR / "priority_threshold_acquisition_campaign.md")
        and priority_threshold_dataset_rows >= counts["priority_promotion_acquisition_wave_plan"]
        and priority_threshold_phase1_rows >= 10
        and priority_threshold_phase2_rows >= 3
        and priority_threshold_countries >= 8
        and priority_threshold_core_countries >= 5
        and priority_threshold_backup_countries >= 3
        and priority_threshold_core_waves >= 10
        and priority_threshold_backup_waves >= 3
        and priority_threshold_minimum_downloads == 11
        and priority_threshold_recommended_downloads >= counts["priority_promotion_acquisition_wave_plan"]
        and priority_threshold_promoted == 0
        and priority_threshold_raw_received == 0
        and priority_threshold_raw_missing >= counts["priority_promotion_acquisition_wave_plan"]
        and priority_threshold_core_endpoint_ready >= counts["priority_promotion_acquisition_wave_plan"]
        and priority_threshold_handoffs >= counts["priority_promotion_acquisition_wave_plan"]
        and priority_threshold_modeling_gate == "blocked"
    )
    add(
        rows,
        "dataset_promotion",
        "Priority threshold acquisition campaign maps 10-wave and sixth-country download requirements before raw receipt",
        status(priority_threshold_gate_ok),
        f"campaign_rows={counts['priority_threshold_acquisition_campaign']}; country_rows={counts['priority_threshold_country_coverage']}; summary_rows={counts['priority_threshold_acquisition_campaign_summary']}; reported_datasets={priority_threshold_dataset_rows}; phase1={priority_threshold_phase1_rows}; phase2={priority_threshold_phase2_rows}; countries={priority_threshold_countries}; core_countries={priority_threshold_core_countries}; backup_countries={priority_threshold_backup_countries}; core_waves={priority_threshold_core_waves}; backup_waves={priority_threshold_backup_waves}; minimum_downloads={priority_threshold_minimum_downloads}; recommended_downloads={priority_threshold_recommended_downloads}; promoted={priority_threshold_promoted}; raw_received={priority_threshold_raw_received}; raw_missing={priority_threshold_raw_missing}; core_endpoint_ready={priority_threshold_core_endpoint_ready}; handoffs={priority_threshold_handoffs}; modeling_gate={priority_threshold_modeling_gate}",
        "" if priority_threshold_gate_ok else "Run script/139_build_priority_threshold_acquisition_campaign.py after endpoint, credentialed acquisition, and packet artifacts are current.",
    )
    priority_first_pass_summary = read_csv_dicts(RESULT_DIR / "priority_first_pass_variable_review_summary.csv")
    priority_first_pass_dataset_rows = safe_int(next((row.get("value", "0") for row in priority_first_pass_summary if row.get("metric") == "priority_first_pass_dataset_rows"), "0"), 0)
    priority_first_pass_requirement_rows = safe_int(next((row.get("value", "0") for row in priority_first_pass_summary if row.get("metric") == "priority_first_pass_requirement_rows"), "0"), 0)
    priority_first_pass_selected_rows = safe_int(next((row.get("value", "0") for row in priority_first_pass_summary if row.get("metric") == "priority_first_pass_selected_variable_rows"), "0"), 0)
    priority_first_pass_countries = safe_int(next((row.get("value", "0") for row in priority_first_pass_summary if row.get("metric") == "priority_first_pass_distinct_countries"), "0"), 0)
    priority_first_pass_priority_rows = safe_int(next((row.get("value", "0") for row in priority_first_pass_summary if row.get("metric") == "priority_first_pass_priority_10_wave_rows"), "0"), 0)
    priority_first_pass_backup_rows = safe_int(next((row.get("value", "0") for row in priority_first_pass_summary if row.get("metric") == "priority_first_pass_backup_wave_rows"), "0"), 0)
    priority_first_pass_missing_coverage = safe_int(next((row.get("value", "0") for row in priority_first_pass_summary if row.get("metric") == "priority_first_pass_missing_requirement_coverage_rows"), "0"), 0)
    priority_first_pass_raw_received = safe_int(next((row.get("value", "0") for row in priority_first_pass_summary if row.get("metric") == "priority_first_pass_raw_package_received_rows"), "0"), 0)
    priority_first_pass_ready_after_download = safe_int(next((row.get("value", "0") for row in priority_first_pass_summary if row.get("metric") == "priority_first_pass_ready_after_download_rows"), "0"), 0)
    priority_first_pass_handoffs = safe_int(next((row.get("value", "0") for row in priority_first_pass_summary if row.get("metric") == "priority_first_pass_handoff_readmes_written"), "0"), 0)
    priority_first_pass_modeling_gate = next((row.get("value", "") for row in priority_first_pass_summary if row.get("metric") == "modeling_gate_status"), "")
    priority_first_pass_blocked_status_rows = safe_int(next((row.get("value", "0") for row in priority_first_pass_summary if row.get("metric") == "first_pass_review_status_blocked_raw_package_not_received"), "0"), 0)
    priority_first_pass_requirement_blocked_rows = safe_int(next((row.get("value", "0") for row in priority_first_pass_summary if row.get("metric") == "first_pass_requirement_status_blocked_raw_package_not_received"), "0"), 0)
    priority_first_pass_gate_ok = (
        counts["priority_first_pass_variable_review_queue"] >= counts["priority_promotion_acquisition_wave_plan"] * 8
        and counts["priority_first_pass_requirement_coverage"] >= counts["priority_promotion_acquisition_wave_plan"] * 8
        and counts["priority_first_pass_variable_review_summary"] > 0
        and file_ok(REPORT_DIR / "priority_first_pass_variable_review_queue.md")
        and priority_first_pass_dataset_rows >= counts["priority_promotion_acquisition_wave_plan"]
        and priority_first_pass_requirement_rows >= counts["priority_promotion_acquisition_wave_plan"] * 8
        and priority_first_pass_selected_rows >= counts["priority_promotion_acquisition_wave_plan"] * 8
        and priority_first_pass_countries >= 8
        and priority_first_pass_priority_rows >= 10
        and priority_first_pass_backup_rows >= 3
        and priority_first_pass_missing_coverage == 0
        and priority_first_pass_raw_received == 0
        and priority_first_pass_ready_after_download == 0
        and priority_first_pass_blocked_status_rows >= priority_first_pass_selected_rows
        and priority_first_pass_requirement_blocked_rows >= priority_first_pass_requirement_rows
        and priority_first_pass_handoffs >= counts["priority_promotion_acquisition_wave_plan"]
        and priority_first_pass_modeling_gate == "blocked"
    )
    add(
        rows,
        "dataset_promotion",
        "Priority first-pass variable review queue compresses metadata candidates into a post-download raw-value review queue without promoting data",
        status(priority_first_pass_gate_ok),
        f"queue_rows={counts['priority_first_pass_variable_review_queue']}; coverage_rows={counts['priority_first_pass_requirement_coverage']}; summary_rows={counts['priority_first_pass_variable_review_summary']}; reported_datasets={priority_first_pass_dataset_rows}; requirements={priority_first_pass_requirement_rows}; selected_variables={priority_first_pass_selected_rows}; countries={priority_first_pass_countries}; priority_waves={priority_first_pass_priority_rows}; backup_waves={priority_first_pass_backup_rows}; missing_coverage={priority_first_pass_missing_coverage}; raw_received={priority_first_pass_raw_received}; ready_after_download={priority_first_pass_ready_after_download}; blocked_status_rows={priority_first_pass_blocked_status_rows}; requirement_blocked_rows={priority_first_pass_requirement_blocked_rows}; handoffs={priority_first_pass_handoffs}; modeling_gate={priority_first_pass_modeling_gate}",
        "" if priority_first_pass_gate_ok else "Run script/140_build_priority_first_pass_variable_review_queue.py after the threshold campaign and raw verification workbook are current.",
    )
    priority_download_summary = read_csv_dicts(RESULT_DIR / "priority_download_execution_packet_summary.csv")
    priority_download_packet_rows = safe_int(next((row.get("value", "0") for row in priority_download_summary if row.get("metric") == "priority_download_execution_packet_rows"), "0"), 0)
    priority_download_priority_rows = safe_int(next((row.get("value", "0") for row in priority_download_summary if row.get("metric") == "priority_download_execution_priority_10_wave_rows"), "0"), 0)
    priority_download_backup_rows = safe_int(next((row.get("value", "0") for row in priority_download_summary if row.get("metric") == "priority_download_execution_backup_wave_rows"), "0"), 0)
    priority_download_countries = safe_int(next((row.get("value", "0") for row in priority_download_summary if row.get("metric") == "priority_download_execution_distinct_countries"), "0"), 0)
    priority_download_core_file_rows = safe_int(next((row.get("value", "0") for row in priority_download_summary if row.get("metric") == "priority_download_execution_core_file_rows"), "0"), 0)
    priority_download_requirement_rows = safe_int(next((row.get("value", "0") for row in priority_download_summary if row.get("metric") == "priority_download_execution_first_pass_requirement_rows"), "0"), 0)
    priority_download_variable_rows = safe_int(next((row.get("value", "0") for row in priority_download_summary if row.get("metric") == "priority_download_execution_first_pass_variable_rows"), "0"), 0)
    priority_download_raw_received = safe_int(next((row.get("value", "0") for row in priority_download_summary if row.get("metric") == "priority_download_execution_raw_package_received_rows"), "0"), 0)
    priority_download_handoffs = safe_int(next((row.get("value", "0") for row in priority_download_summary if row.get("metric") == "priority_download_execution_handoff_readmes_written"), "0"), 0)
    priority_download_ready_rows = safe_int(next((row.get("value", "0") for row in priority_download_summary if row.get("metric") == "download_execution_status_ready_for_manual_credentialed_download_no_raw_receipt"), "0"), 0)
    priority_download_file_blocked_rows = safe_int(next((row.get("value", "0") for row in priority_download_summary if row.get("metric") == "download_file_acceptance_status_blocked_no_raw_or_archive_file"), "0"), 0)
    priority_download_modeling_gate = next((row.get("value", "") for row in priority_download_summary if row.get("metric") == "modeling_gate_status"), "")
    priority_download_gate_ok = (
        counts["priority_download_execution_packet"] >= counts["priority_promotion_acquisition_wave_plan"]
        and counts["priority_download_file_acceptance_matrix"] >= counts["priority_promotion_acquisition_wave_plan"] * 12
        and counts["priority_download_execution_packet_summary"] > 0
        and file_ok(REPORT_DIR / "priority_download_execution_packet.md")
        and priority_download_packet_rows >= counts["priority_promotion_acquisition_wave_plan"]
        and priority_download_priority_rows >= 10
        and priority_download_backup_rows >= 3
        and priority_download_countries >= 8
        and priority_download_core_file_rows >= counts["priority_promotion_acquisition_wave_plan"] * 12
        and priority_download_requirement_rows >= counts["priority_promotion_acquisition_wave_plan"] * 8
        and priority_download_variable_rows >= priority_first_pass_selected_rows
        and priority_download_raw_received == 0
        and priority_download_ready_rows >= counts["priority_promotion_acquisition_wave_plan"]
        and priority_download_file_blocked_rows >= priority_download_core_file_rows
        and priority_download_handoffs >= counts["priority_promotion_acquisition_wave_plan"]
        and priority_download_modeling_gate == "blocked"
    )
    add(
        rows,
        "dataset_promotion",
        "Priority download execution packet links official credentialed URLs, target folders, core-file acceptance, and first-pass variable review before raw receipt",
        status(priority_download_gate_ok),
        f"packet_rows={counts['priority_download_execution_packet']}; file_rows={counts['priority_download_file_acceptance_matrix']}; summary_rows={counts['priority_download_execution_packet_summary']}; reported_packets={priority_download_packet_rows}; priority_waves={priority_download_priority_rows}; backup_waves={priority_download_backup_rows}; countries={priority_download_countries}; core_files={priority_download_core_file_rows}; requirements={priority_download_requirement_rows}; variables={priority_download_variable_rows}; raw_received={priority_download_raw_received}; ready_download_rows={priority_download_ready_rows}; blocked_file_rows={priority_download_file_blocked_rows}; handoffs={priority_download_handoffs}; modeling_gate={priority_download_modeling_gate}",
        "" if priority_download_gate_ok else "Run script/141_build_priority_download_execution_packet.py after first-pass review queue and credentialed acquisition ledgers are current.",
    )
    priority_lsms_summary = read_csv_dicts(RESULT_DIR / "priority_lsms_isa_alignment_summary.csv")
    priority_lsms_campaign_rows = safe_int(next((row.get("value", "0") for row in priority_lsms_summary if row.get("metric") == "priority_lsms_alignment_current_campaign_rows"), "0"), 0)
    priority_lsms_core_rows = safe_int(next((row.get("value", "0") for row in priority_lsms_summary if row.get("metric") == "priority_lsms_alignment_core_priority_wave_rows"), "0"), 0)
    priority_lsms_required_countries = safe_int(next((row.get("value", "0") for row in priority_lsms_summary if row.get("metric") == "priority_lsms_alignment_current_required_countries"), "0"), 0)
    priority_lsms_aligned_core = safe_int(next((row.get("value", "0") for row in priority_lsms_summary if row.get("metric") == "priority_lsms_alignment_aligned_core_wave_rows"), "0"), 0)
    priority_lsms_off_family_core = safe_int(next((row.get("value", "0") for row in priority_lsms_summary if row.get("metric") == "priority_lsms_alignment_off_family_core_wave_rows"), "0"), 0)
    priority_lsms_off_family_countries = safe_int(next((row.get("value", "0") for row in priority_lsms_summary if row.get("metric") == "priority_lsms_alignment_off_family_core_country_rows"), "0"), 0)
    priority_lsms_replacements = safe_int(next((row.get("value", "0") for row in priority_lsms_summary if row.get("metric") == "priority_lsms_alignment_strong_replacement_candidate_rows"), "0"), 0)
    priority_lsms_gap_rows = safe_int(next((row.get("value", "0") for row in priority_lsms_summary if row.get("metric") == "priority_lsms_alignment_inventory_gap_rows"), "0"), 0)
    priority_lsms_handoffs = safe_int(next((row.get("value", "0") for row in priority_lsms_summary if row.get("metric") == "priority_lsms_alignment_handoff_readmes_written"), "0"), 0)
    priority_lsms_decision = next((row.get("value", "") for row in priority_lsms_summary if row.get("metric") == "priority_lsms_alignment_campaign_decision"), "")
    priority_lsms_modeling_gate = next((row.get("value", "") for row in priority_lsms_summary if row.get("metric") == "modeling_gate_status"), "")
    priority_lsms_gate_ok = (
        counts["priority_lsms_isa_alignment_audit"] >= counts["priority_promotion_acquisition_wave_plan"]
        and counts["priority_lsms_isa_replacement_candidates"] >= 10
        and counts["priority_lsms_isa_alignment_summary"] > 0
        and file_ok(REPORT_DIR / "priority_lsms_isa_alignment_audit.md")
        and priority_lsms_campaign_rows >= counts["priority_promotion_acquisition_wave_plan"]
        and priority_lsms_core_rows >= 10
        and priority_lsms_required_countries >= 5
        and priority_lsms_aligned_core >= 8
        and priority_lsms_off_family_core >= 2
        and priority_lsms_off_family_countries >= 2
        and priority_lsms_replacements >= 10
        and priority_lsms_gap_rows == 0
        and priority_lsms_handoffs >= counts["priority_promotion_acquisition_wave_plan"]
        and priority_lsms_decision == "needs_core_wave_replacement_before_manual_download_execution"
        and priority_lsms_modeling_gate == "blocked"
    )
    add(
        rows,
        "dataset_promotion",
        "Priority LSMS/ISA alignment audit flags off-family Malawi/Uganda core waves and finds replacement candidates before manual downloads",
        status(priority_lsms_gate_ok),
        f"audit_rows={counts['priority_lsms_isa_alignment_audit']}; candidate_rows={counts['priority_lsms_isa_replacement_candidates']}; summary_rows={counts['priority_lsms_isa_alignment_summary']}; reported_campaign_rows={priority_lsms_campaign_rows}; core_rows={priority_lsms_core_rows}; required_countries={priority_lsms_required_countries}; aligned_core={priority_lsms_aligned_core}; off_family_core={priority_lsms_off_family_core}; off_family_countries={priority_lsms_off_family_countries}; strong_replacements={priority_lsms_replacements}; inventory_gaps={priority_lsms_gap_rows}; handoffs={priority_lsms_handoffs}; decision={priority_lsms_decision}; modeling_gate={priority_lsms_modeling_gate}",
        "" if priority_lsms_gate_ok else "Run script/142_build_priority_lsms_isa_alignment_audit.py after the download execution packet and country-wave screening are current.",
    )
    priority_refocused_summary = read_csv_dicts(RESULT_DIR / "priority_lsms_isa_refocused_acquisition_summary.csv")
    priority_refocused_plan_rows = safe_int(next((row.get("value", "0") for row in priority_refocused_summary if row.get("metric") == "priority_lsms_refocused_wave_plan_rows"), "0"), 0)
    priority_refocused_core_rows = safe_int(next((row.get("value", "0") for row in priority_refocused_summary if row.get("metric") == "priority_lsms_refocused_core_wave_rows"), "0"), 0)
    priority_refocused_core_countries = safe_int(next((row.get("value", "0") for row in priority_refocused_summary if row.get("metric") == "priority_lsms_refocused_core_required_countries"), "0"), 0)
    priority_refocused_core_aligned = safe_int(next((row.get("value", "0") for row in priority_refocused_summary if row.get("metric") == "priority_lsms_refocused_core_lsms_aligned_rows"), "0"), 0)
    priority_refocused_replaced = safe_int(next((row.get("value", "0") for row in priority_refocused_summary if row.get("metric") == "priority_lsms_refocused_replaced_off_family_core_rows"), "0"), 0)
    priority_refocused_queue_rows = safe_int(next((row.get("value", "0") for row in priority_refocused_summary if row.get("metric") == "priority_lsms_refocused_acquisition_queue_rows"), "0"), 0)
    priority_refocused_backup_rows = safe_int(next((row.get("value", "0") for row in priority_refocused_summary if row.get("metric") == "priority_lsms_refocused_replacement_backup_rows"), "0"), 0)
    priority_refocused_requirement_rows = safe_int(next((row.get("value", "0") for row in priority_refocused_summary if row.get("metric") == "priority_lsms_refocused_requirement_rows"), "0"), 0)
    priority_refocused_raw_received = safe_int(next((row.get("value", "0") for row in priority_refocused_summary if row.get("metric") == "priority_lsms_refocused_raw_package_received_rows"), "0"), 0)
    priority_refocused_handoffs = safe_int(next((row.get("value", "0") for row in priority_refocused_summary if row.get("metric") == "priority_lsms_refocused_handoff_readmes_written"), "0"), 0)
    priority_refocused_data_write = next((row.get("value", "") for row in priority_refocused_summary if row.get("metric") == "priority_lsms_refocused_data_write_status"), "")
    priority_refocused_modeling_gate = next((row.get("value", "") for row in priority_refocused_summary if row.get("metric") == "modeling_gate_status"), "")
    priority_refocused_gate_ok = (
        counts["priority_lsms_isa_refocused_wave_plan"] >= counts["priority_promotion_acquisition_wave_plan"]
        and counts["priority_lsms_isa_refocused_acquisition_queue"] >= counts["priority_promotion_acquisition_wave_plan"] + 6
        and counts["priority_lsms_isa_refocused_requirement_matrix"] >= counts["priority_lsms_isa_refocused_acquisition_queue"] * 8
        and counts["priority_lsms_isa_refocused_acquisition_summary"] > 0
        and file_ok(REPORT_DIR / "priority_lsms_isa_refocused_acquisition_queue.md")
        and priority_refocused_plan_rows >= counts["priority_promotion_acquisition_wave_plan"]
        and priority_refocused_core_rows >= 10
        and priority_refocused_core_countries >= 5
        and priority_refocused_core_aligned >= 10
        and priority_refocused_replaced >= 2
        and priority_refocused_queue_rows >= priority_refocused_plan_rows + 6
        and priority_refocused_backup_rows >= 6
        and priority_refocused_requirement_rows >= priority_refocused_queue_rows * 8
        and priority_refocused_raw_received == 0
        and priority_refocused_handoffs >= priority_refocused_queue_rows
        and priority_refocused_data_write == "blocked_no_promoted_rows"
        and priority_refocused_modeling_gate == "blocked"
    )
    add(
        rows,
        "dataset_promotion",
        "Priority LSMS/ISA refocused acquisition queue replaces off-family core waves with executable LSMS/ISA manual-download targets",
        status(priority_refocused_gate_ok),
        f"plan_rows={counts['priority_lsms_isa_refocused_wave_plan']}; queue_rows={counts['priority_lsms_isa_refocused_acquisition_queue']}; requirement_rows={counts['priority_lsms_isa_refocused_requirement_matrix']}; summary_rows={counts['priority_lsms_isa_refocused_acquisition_summary']}; reported_plan_rows={priority_refocused_plan_rows}; core_rows={priority_refocused_core_rows}; core_countries={priority_refocused_core_countries}; core_aligned={priority_refocused_core_aligned}; replaced={priority_refocused_replaced}; reported_queue_rows={priority_refocused_queue_rows}; backup_rows={priority_refocused_backup_rows}; reported_requirement_rows={priority_refocused_requirement_rows}; raw_received={priority_refocused_raw_received}; handoffs={priority_refocused_handoffs}; data_write={priority_refocused_data_write}; modeling_gate={priority_refocused_modeling_gate}",
        "" if priority_refocused_gate_ok else "Run script/143_build_priority_lsms_isa_refocused_acquisition_queue.py after the LSMS/ISA alignment audit is current.",
    )
    priority_lsms_public_docs_summary = read_csv_dicts(RESULT_DIR / "priority_lsms_isa_public_documentation_receipt_summary.csv")
    priority_lsms_public_docs_dataset_rows = safe_int(next((row.get("value", "0") for row in priority_lsms_public_docs_summary if row.get("metric") == "priority_lsms_isa_public_documentation_dataset_rows"), "0"), 0)
    priority_lsms_public_docs_resource_rows = safe_int(next((row.get("value", "0") for row in priority_lsms_public_docs_summary if row.get("metric") == "priority_lsms_isa_public_documentation_resource_rows"), "0"), 0)
    priority_lsms_public_docs_saved_rows = safe_int(next((row.get("value", "0") for row in priority_lsms_public_docs_summary if row.get("metric") == "priority_lsms_isa_public_documentation_saved_rows"), "0"), 0)
    priority_lsms_public_docs_failed_rows = safe_int(next((row.get("value", "0") for row in priority_lsms_public_docs_summary if row.get("metric") == "priority_lsms_isa_public_documentation_failed_rows"), "0"), 0)
    priority_lsms_public_docs_core_complete = safe_int(next((row.get("value", "0") for row in priority_lsms_public_docs_summary if row.get("metric") == "priority_lsms_isa_public_documentation_core_complete_dataset_rows"), "0"), 0)
    priority_lsms_public_docs_catalog_digest = safe_int(next((row.get("value", "0") for row in priority_lsms_public_docs_summary if row.get("metric") == "priority_lsms_isa_public_documentation_catalog_digest_rows"), "0"), 0)
    priority_lsms_public_docs_file_inventory = safe_int(next((row.get("value", "0") for row in priority_lsms_public_docs_summary if row.get("metric") == "priority_lsms_isa_public_documentation_file_inventory_rows"), "0"), 0)
    priority_lsms_public_docs_access_gates = safe_int(next((row.get("value", "0") for row in priority_lsms_public_docs_summary if row.get("metric") == "priority_lsms_isa_public_documentation_access_gate_rows"), "0"), 0)
    priority_lsms_public_docs_handoffs = safe_int(next((row.get("value", "0") for row in priority_lsms_public_docs_summary if row.get("metric") == "priority_lsms_isa_public_documentation_handoff_readmes_written"), "0"), 0)
    priority_lsms_public_docs_data_write = next((row.get("value", "") for row in priority_lsms_public_docs_summary if row.get("metric") == "priority_lsms_isa_public_documentation_data_write_status"), "")
    priority_lsms_public_docs_modeling_gate = next((row.get("value", "") for row in priority_lsms_public_docs_summary if row.get("metric") == "modeling_gate_status"), "")
    priority_lsms_public_docs_gate_ok = (
        counts["priority_lsms_isa_public_documentation_dataset_receipt"] >= counts["priority_lsms_isa_refocused_acquisition_queue"]
        and counts["priority_lsms_isa_public_documentation_receipt"] >= counts["priority_lsms_isa_refocused_acquisition_queue"] * 7
        and counts["priority_lsms_isa_public_documentation_receipt_summary"] > 0
        and file_ok(REPORT_DIR / "priority_lsms_isa_public_documentation_receipt.md")
        and priority_lsms_public_docs_dataset_rows >= priority_refocused_queue_rows
        and priority_lsms_public_docs_resource_rows >= priority_lsms_public_docs_dataset_rows * 7
        and priority_lsms_public_docs_saved_rows >= priority_lsms_public_docs_dataset_rows * 5
        and priority_lsms_public_docs_failed_rows == 0
        and priority_lsms_public_docs_core_complete >= priority_lsms_public_docs_dataset_rows
        and counts["priority_lsms_isa_public_documentation_catalog_digest"] >= priority_lsms_public_docs_dataset_rows
        and counts["priority_lsms_isa_public_documentation_file_inventory"] > priority_lsms_public_docs_dataset_rows
        and priority_lsms_public_docs_catalog_digest >= priority_lsms_public_docs_dataset_rows
        and priority_lsms_public_docs_file_inventory == counts["priority_lsms_isa_public_documentation_file_inventory"]
        and priority_lsms_public_docs_access_gates >= priority_lsms_public_docs_dataset_rows
        and priority_lsms_public_docs_handoffs >= priority_lsms_public_docs_dataset_rows
        and priority_lsms_public_docs_data_write == "blocked_no_promoted_rows"
        and priority_lsms_public_docs_modeling_gate == "blocked"
    )
    add(
        rows,
        "dataset_promotion",
        "Priority LSMS/ISA public documentation receipt covers the refocused queue with official metadata snapshots while preserving raw-data blockers",
        status(priority_lsms_public_docs_gate_ok),
        f"receipt_rows={counts['priority_lsms_isa_public_documentation_receipt']}; dataset_rows={counts['priority_lsms_isa_public_documentation_dataset_receipt']}; catalog_digest_rows={counts['priority_lsms_isa_public_documentation_catalog_digest']}; file_inventory_rows={counts['priority_lsms_isa_public_documentation_file_inventory']}; summary_rows={counts['priority_lsms_isa_public_documentation_receipt_summary']}; reported_datasets={priority_lsms_public_docs_dataset_rows}; resources={priority_lsms_public_docs_resource_rows}; saved={priority_lsms_public_docs_saved_rows}; failed={priority_lsms_public_docs_failed_rows}; core_complete={priority_lsms_public_docs_core_complete}; reported_catalog_digest={priority_lsms_public_docs_catalog_digest}; reported_file_inventory={priority_lsms_public_docs_file_inventory}; access_gates={priority_lsms_public_docs_access_gates}; handoffs={priority_lsms_public_docs_handoffs}; data_write={priority_lsms_public_docs_data_write}; modeling_gate={priority_lsms_public_docs_modeling_gate}",
        "" if priority_lsms_public_docs_gate_ok else "Run script/146_build_priority_lsms_isa_public_documentation_receipt.py after the refocused acquisition queue is current.",
    )
    priority_lsms_variable_summary = read_csv_dicts(RESULT_DIR / "priority_lsms_isa_variable_evidence_summary.csv")
    priority_lsms_variable_dataset_rows = safe_int(next((row.get("value", "0") for row in priority_lsms_variable_summary if row.get("metric") == "priority_lsms_variable_evidence_dataset_rows"), "0"), 0)
    priority_lsms_variable_requirement_rows = safe_int(next((row.get("value", "0") for row in priority_lsms_variable_summary if row.get("metric") == "priority_lsms_variable_evidence_requirement_rows"), "0"), 0)
    priority_lsms_variable_candidate_rows = safe_int(next((row.get("value", "0") for row in priority_lsms_variable_summary if row.get("metric") == "priority_lsms_variable_evidence_candidate_variable_rows"), "0"), 0)
    priority_lsms_variable_file_rows = safe_int(next((row.get("value", "0") for row in priority_lsms_variable_summary if row.get("metric") == "priority_lsms_variable_evidence_file_shortlist_rows"), "0"), 0)
    priority_lsms_variable_strong_requirement_rows = safe_int(next((row.get("value", "0") for row in priority_lsms_variable_summary if row.get("metric") == "priority_lsms_variable_evidence_strong_requirement_rows"), "0"), 0)
    priority_lsms_variable_docs_only_rows = safe_int(next((row.get("value", "0") for row in priority_lsms_variable_summary if row.get("metric") == "priority_lsms_variable_evidence_documentation_only_requirement_rows"), "0"), 0)
    priority_lsms_variable_no_candidate_rows = safe_int(next((row.get("value", "0") for row in priority_lsms_variable_summary if row.get("metric") == "priority_lsms_variable_evidence_no_candidate_requirement_rows"), "0"), 0)
    priority_lsms_variable_handoffs = safe_int(next((row.get("value", "0") for row in priority_lsms_variable_summary if row.get("metric") == "priority_lsms_variable_evidence_handoff_readmes_written"), "0"), 0)
    priority_lsms_variable_raw_verified = safe_int(next((row.get("value", "0") for row in priority_lsms_variable_summary if row.get("metric") == "priority_lsms_variable_evidence_raw_value_verified_rows"), "0"), 0)
    priority_lsms_variable_data_write = next((row.get("value", "") for row in priority_lsms_variable_summary if row.get("metric") == "priority_lsms_variable_evidence_data_write_status"), "")
    priority_lsms_variable_modeling_gate = next((row.get("value", "") for row in priority_lsms_variable_summary if row.get("metric") == "modeling_gate_status"), "")
    priority_lsms_variable_gate_ok = (
        counts["priority_lsms_isa_variable_evidence_matrix"] >= counts["priority_lsms_isa_refocused_acquisition_queue"] * 7
        and counts["priority_lsms_isa_requirement_variable_coverage"] >= counts["priority_lsms_isa_refocused_requirement_matrix"]
        and counts["priority_lsms_isa_concept_file_shortlist"] >= counts["priority_lsms_isa_refocused_acquisition_queue"] * 7
        and counts["priority_lsms_isa_variable_evidence_summary"] > 0
        and file_ok(REPORT_DIR / "priority_lsms_isa_variable_evidence_matrix.md")
        and priority_lsms_variable_dataset_rows >= priority_refocused_queue_rows
        and priority_lsms_variable_requirement_rows >= priority_refocused_requirement_rows
        and priority_lsms_variable_candidate_rows == counts["priority_lsms_isa_variable_evidence_matrix"]
        and priority_lsms_variable_file_rows == counts["priority_lsms_isa_concept_file_shortlist"]
        and priority_lsms_variable_strong_requirement_rows >= priority_lsms_variable_dataset_rows * 6
        and priority_lsms_variable_docs_only_rows >= priority_lsms_variable_dataset_rows
        and priority_lsms_variable_no_candidate_rows == 0
        and priority_lsms_variable_handoffs >= priority_lsms_variable_dataset_rows
        and priority_lsms_variable_raw_verified == 0
        and priority_lsms_variable_data_write == "blocked_no_promoted_rows"
        and priority_lsms_variable_modeling_gate == "blocked"
    )
    add(
        rows,
        "dataset_promotion",
        "Priority LSMS/ISA variable evidence matrix maps official public metadata candidates to promotion requirements without accepting raw values",
        status(priority_lsms_variable_gate_ok),
        f"matrix_rows={counts['priority_lsms_isa_variable_evidence_matrix']}; coverage_rows={counts['priority_lsms_isa_requirement_variable_coverage']}; file_rows={counts['priority_lsms_isa_concept_file_shortlist']}; summary_rows={counts['priority_lsms_isa_variable_evidence_summary']}; reported_datasets={priority_lsms_variable_dataset_rows}; reported_requirements={priority_lsms_variable_requirement_rows}; candidate_variables={priority_lsms_variable_candidate_rows}; file_shortlist={priority_lsms_variable_file_rows}; strong_requirements={priority_lsms_variable_strong_requirement_rows}; docs_only={priority_lsms_variable_docs_only_rows}; no_candidate={priority_lsms_variable_no_candidate_rows}; handoffs={priority_lsms_variable_handoffs}; raw_verified={priority_lsms_variable_raw_verified}; data_write={priority_lsms_variable_data_write}; modeling_gate={priority_lsms_variable_modeling_gate}",
        "" if priority_lsms_variable_gate_ok else "Run script/147_build_priority_lsms_isa_variable_evidence_matrix.py after the public documentation receipt is current.",
    )
    priority_raw_intake_summary = read_csv_dicts(RESULT_DIR / "priority_lsms_isa_raw_package_intake_summary.csv")
    priority_raw_intake_dataset_rows = safe_int(next((row.get("value", "0") for row in priority_raw_intake_summary if row.get("metric") == "priority_lsms_raw_intake_dataset_rows"), "0"), 0)
    priority_raw_intake_manifest_rows = safe_int(next((row.get("value", "0") for row in priority_raw_intake_summary if row.get("metric") == "priority_lsms_raw_intake_file_manifest_rows"), "0"), 0)
    priority_raw_intake_generated = safe_int(next((row.get("value", "0") for row in priority_raw_intake_summary if row.get("metric") == "priority_lsms_raw_intake_generated_handoff_files"), "0"), 0)
    priority_raw_intake_original = safe_int(next((row.get("value", "0") for row in priority_raw_intake_summary if row.get("metric") == "priority_lsms_raw_intake_original_file_rows"), "0"), 0)
    priority_raw_intake_archives = safe_int(next((row.get("value", "0") for row in priority_raw_intake_summary if row.get("metric") == "priority_lsms_raw_intake_archive_file_rows"), "0"), 0)
    priority_raw_intake_tabular = safe_int(next((row.get("value", "0") for row in priority_raw_intake_summary if row.get("metric") == "priority_lsms_raw_intake_raw_tabular_file_rows"), "0"), 0)
    priority_raw_intake_docs = safe_int(next((row.get("value", "0") for row in priority_raw_intake_summary if row.get("metric") == "priority_lsms_raw_intake_documentation_file_rows"), "0"), 0)
    priority_raw_intake_missing = safe_int(next((row.get("value", "0") for row in priority_raw_intake_summary if row.get("metric") == "priority_lsms_raw_intake_missing_package_rows"), "0"), 0)
    priority_raw_intake_requirements = safe_int(next((row.get("value", "0") for row in priority_raw_intake_summary if row.get("metric") == "priority_lsms_raw_intake_acceptance_requirement_rows"), "0"), 0)
    priority_raw_intake_blocked_requirements = safe_int(next((row.get("value", "0") for row in priority_raw_intake_summary if row.get("metric") == "priority_lsms_raw_intake_blocked_requirement_rows"), "0"), 0)
    priority_raw_intake_handoffs = safe_int(next((row.get("value", "0") for row in priority_raw_intake_summary if row.get("metric") == "priority_lsms_raw_intake_handoff_readmes_written"), "0"), 0)
    priority_raw_intake_data_write = next((row.get("value", "") for row in priority_raw_intake_summary if row.get("metric") == "priority_lsms_raw_intake_data_write_status"), "")
    priority_raw_intake_modeling_gate = next((row.get("value", "") for row in priority_raw_intake_summary if row.get("metric") == "modeling_gate_status"), "")
    priority_raw_intake_gate_ok = (
        counts["priority_lsms_isa_raw_package_intake_ledger"] >= counts["priority_lsms_isa_refocused_acquisition_queue"]
        and counts["priority_lsms_isa_raw_package_acceptance_matrix"] >= counts["priority_lsms_isa_refocused_requirement_matrix"]
        and counts["priority_lsms_isa_raw_package_intake_summary"] > 0
        and file_ok(REPORT_DIR / "priority_lsms_isa_raw_package_intake_packet.md")
        and priority_raw_intake_dataset_rows >= priority_refocused_queue_rows
        and priority_raw_intake_manifest_rows >= priority_raw_intake_generated
        and priority_raw_intake_generated >= priority_refocused_queue_rows
        and 0 <= priority_raw_intake_original <= priority_raw_intake_dataset_rows
        and 0 <= priority_raw_intake_archives <= priority_raw_intake_original
        and 0 <= priority_raw_intake_tabular <= priority_raw_intake_original
        and 0 <= priority_raw_intake_docs <= priority_raw_intake_original
        and 0 <= priority_raw_intake_missing <= priority_raw_intake_dataset_rows
        and priority_raw_intake_missing + priority_raw_intake_original >= priority_raw_intake_dataset_rows
        and priority_raw_intake_requirements >= priority_refocused_requirement_rows
        and priority_raw_intake_blocked_requirements >= priority_raw_intake_requirements
        and priority_raw_intake_handoffs >= priority_raw_intake_dataset_rows
        and priority_raw_intake_data_write == "blocked_no_promoted_rows"
        and priority_raw_intake_modeling_gate == "blocked"
    )
    add(
        rows,
        "dataset_promotion",
        "Priority LSMS/ISA raw-package intake packet scans refocused target folders and keeps all requirements blocked until package and review gates pass",
        status(priority_raw_intake_gate_ok),
        f"ledger_rows={counts['priority_lsms_isa_raw_package_intake_ledger']}; manifest_rows={counts['priority_lsms_isa_raw_package_file_manifest']}; acceptance_rows={counts['priority_lsms_isa_raw_package_acceptance_matrix']}; summary_rows={counts['priority_lsms_isa_raw_package_intake_summary']}; reported_datasets={priority_raw_intake_dataset_rows}; reported_manifest={priority_raw_intake_manifest_rows}; generated_handoffs={priority_raw_intake_generated}; original_files={priority_raw_intake_original}; archives={priority_raw_intake_archives}; raw_tabular={priority_raw_intake_tabular}; documentation={priority_raw_intake_docs}; missing_packages={priority_raw_intake_missing}; requirements={priority_raw_intake_requirements}; blocked_requirements={priority_raw_intake_blocked_requirements}; handoffs={priority_raw_intake_handoffs}; data_write={priority_raw_intake_data_write}; modeling_gate={priority_raw_intake_modeling_gate}",
        "" if priority_raw_intake_gate_ok else "Run script/144_build_priority_lsms_isa_raw_package_intake_packet.py after the refocused acquisition queue is current.",
    )
    priority_archive_preflight_summary = read_csv_dicts(RESULT_DIR / "priority_lsms_isa_archive_member_preflight_summary.csv")
    priority_archive_preflight_datasets = safe_int(next((row.get("value", "0") for row in priority_archive_preflight_summary if row.get("metric") == "priority_lsms_archive_preflight_dataset_rows"), "0"), 0)
    priority_archive_preflight_direct_files = safe_int(next((row.get("value", "0") for row in priority_archive_preflight_summary if row.get("metric") == "priority_lsms_archive_preflight_direct_file_rows"), "0"), 0)
    priority_archive_preflight_direct_archives = safe_int(next((row.get("value", "0") for row in priority_archive_preflight_summary if row.get("metric") == "priority_lsms_archive_preflight_direct_archive_rows"), "0"), 0)
    priority_archive_preflight_direct_raw = safe_int(next((row.get("value", "0") for row in priority_archive_preflight_summary if row.get("metric") == "priority_lsms_archive_preflight_direct_raw_tabular_rows"), "0"), 0)
    priority_archive_preflight_direct_docs = safe_int(next((row.get("value", "0") for row in priority_archive_preflight_summary if row.get("metric") == "priority_lsms_archive_preflight_direct_documentation_rows"), "0"), 0)
    priority_archive_preflight_public_docs = safe_int(next((row.get("value", "0") for row in priority_archive_preflight_summary if row.get("metric") == "priority_lsms_archive_preflight_public_documentation_snapshot_rows"), "0"), 0)
    priority_archive_preflight_members = safe_int(next((row.get("value", "0") for row in priority_archive_preflight_summary if row.get("metric") == "priority_lsms_archive_preflight_archive_member_rows"), "0"), 0)
    priority_archive_preflight_ready = safe_int(next((row.get("value", "0") for row in priority_archive_preflight_summary if row.get("metric") == "priority_lsms_archive_preflight_ready_dataset_rows"), "0"), 0)
    priority_archive_preflight_blocked = safe_int(next((row.get("value", "0") for row in priority_archive_preflight_summary if row.get("metric") == "priority_lsms_archive_preflight_blocked_dataset_rows"), "0"), 0)
    priority_archive_preflight_requirements = safe_int(next((row.get("value", "0") for row in priority_archive_preflight_summary if row.get("metric") == "priority_lsms_archive_preflight_requirement_rows"), "0"), 0)
    priority_archive_preflight_blocked_requirements = safe_int(next((row.get("value", "0") for row in priority_archive_preflight_summary if row.get("metric") == "priority_lsms_archive_preflight_blocked_requirement_rows"), "0"), 0)
    priority_archive_preflight_handoffs = safe_int(next((row.get("value", "0") for row in priority_archive_preflight_summary if row.get("metric") == "priority_lsms_archive_preflight_handoff_readmes_written"), "0"), 0)
    priority_archive_preflight_data_write = next((row.get("value", "") for row in priority_archive_preflight_summary if row.get("metric") == "priority_lsms_archive_preflight_data_write_status"), "")
    priority_archive_preflight_modeling_gate = next((row.get("value", "") for row in priority_archive_preflight_summary if row.get("metric") == "modeling_gate_status"), "")
    priority_archive_preflight_gate_ok = (
        counts["priority_lsms_isa_archive_member_preflight"] >= counts["priority_lsms_isa_refocused_acquisition_queue"]
        and counts["priority_lsms_isa_archive_requirement_preflight"] >= counts["priority_lsms_isa_refocused_requirement_matrix"]
        and counts["priority_lsms_isa_archive_member_preflight_summary"] > 0
        and file_ok(REPORT_DIR / "priority_lsms_isa_archive_member_preflight.md")
        and priority_archive_preflight_datasets >= priority_refocused_queue_rows
        and 0 <= priority_archive_preflight_direct_files <= priority_archive_preflight_datasets
        and 0 <= priority_archive_preflight_direct_archives <= priority_archive_preflight_direct_files
        and 0 <= priority_archive_preflight_direct_raw <= priority_archive_preflight_direct_files
        and 0 <= priority_archive_preflight_direct_docs <= priority_archive_preflight_direct_files
        and priority_archive_preflight_public_docs >= 0
        and priority_archive_preflight_members >= 0
        and 0 <= priority_archive_preflight_ready <= priority_archive_preflight_datasets
        and priority_archive_preflight_ready + priority_archive_preflight_blocked >= priority_archive_preflight_datasets
        and priority_archive_preflight_requirements >= priority_refocused_requirement_rows
        and 0 <= priority_archive_preflight_blocked_requirements <= priority_archive_preflight_requirements
        and priority_archive_preflight_handoffs >= priority_archive_preflight_datasets
        and priority_archive_preflight_data_write == "blocked_no_promoted_rows"
        and priority_archive_preflight_modeling_gate == "blocked"
    )
    add(
        rows,
        "dataset_promotion",
        "Priority LSMS/ISA archive/direct-file preflight checks raw package contents without extraction and remains blocked until documentation and review gates pass",
        status(priority_archive_preflight_gate_ok),
        f"preflight_rows={counts['priority_lsms_isa_archive_member_preflight']}; member_rows={counts['priority_lsms_isa_archive_member_manifest']}; direct_rows={counts['priority_lsms_isa_direct_file_preflight']}; requirement_rows={counts['priority_lsms_isa_archive_requirement_preflight']}; summary_rows={counts['priority_lsms_isa_archive_member_preflight_summary']}; reported_datasets={priority_archive_preflight_datasets}; direct_files={priority_archive_preflight_direct_files}; archives={priority_archive_preflight_direct_archives}; direct_raw={priority_archive_preflight_direct_raw}; direct_docs={priority_archive_preflight_direct_docs}; public_docs={priority_archive_preflight_public_docs}; archive_members={priority_archive_preflight_members}; ready={priority_archive_preflight_ready}; blocked={priority_archive_preflight_blocked}; reported_requirements={priority_archive_preflight_requirements}; blocked_requirements={priority_archive_preflight_blocked_requirements}; handoffs={priority_archive_preflight_handoffs}; data_write={priority_archive_preflight_data_write}; modeling_gate={priority_archive_preflight_modeling_gate}",
        "" if priority_archive_preflight_gate_ok else "Run script/145_build_priority_lsms_isa_archive_member_preflight.py after the raw-package intake packet is current.",
    )
    priority_lsms_raw_value_workbook_summary = read_csv_dicts(RESULT_DIR / "priority_lsms_isa_raw_value_verification_workbook_summary.csv")
    priority_lsms_workbook_datasets = safe_int(next((row.get("value", "0") for row in priority_lsms_raw_value_workbook_summary if row.get("metric") == "priority_lsms_raw_value_workbook_dataset_rows"), "0"), 0)
    priority_lsms_workbook_requirements = safe_int(next((row.get("value", "0") for row in priority_lsms_raw_value_workbook_summary if row.get("metric") == "priority_lsms_raw_value_workbook_requirement_rows"), "0"), 0)
    priority_lsms_workbook_variables = safe_int(next((row.get("value", "0") for row in priority_lsms_raw_value_workbook_summary if row.get("metric") == "priority_lsms_raw_value_workbook_variable_rows"), "0"), 0)
    priority_lsms_workbook_files = safe_int(next((row.get("value", "0") for row in priority_lsms_raw_value_workbook_summary if row.get("metric") == "priority_lsms_raw_value_workbook_file_rows"), "0"), 0)
    priority_lsms_workbook_handoffs = safe_int(next((row.get("value", "0") for row in priority_lsms_raw_value_workbook_summary if row.get("metric") == "priority_lsms_raw_value_workbook_handoff_readmes_written"), "0"), 0)
    priority_lsms_workbook_ready_review = safe_int(next((row.get("value", "0") for row in priority_lsms_raw_value_workbook_summary if row.get("metric") == "priority_lsms_raw_value_workbook_ready_for_manual_review_rows"), "0"), 0)
    priority_lsms_workbook_blocked_requirements = safe_int(next((row.get("value", "0") for row in priority_lsms_raw_value_workbook_summary if row.get("metric") == "priority_lsms_raw_value_workbook_blocked_requirement_rows"), "0"), 0)
    priority_lsms_workbook_raw_verified = safe_int(next((row.get("value", "0") for row in priority_lsms_raw_value_workbook_summary if row.get("metric") == "priority_lsms_raw_value_workbook_raw_value_verified_rows"), "0"), 0)
    priority_lsms_workbook_data_write = next((row.get("value", "") for row in priority_lsms_raw_value_workbook_summary if row.get("metric") == "priority_lsms_raw_value_workbook_data_write_status"), "")
    priority_lsms_workbook_modeling_gate = next((row.get("value", "") for row in priority_lsms_raw_value_workbook_summary if row.get("metric") == "modeling_gate_status"), "")
    priority_lsms_workbook_gate_ok = (
        counts["priority_lsms_isa_raw_value_requirement_workbook"] >= counts["priority_lsms_isa_refocused_requirement_matrix"]
        and counts["priority_lsms_isa_raw_value_variable_workbook"] >= counts["priority_lsms_isa_variable_evidence_matrix"]
        and counts["priority_lsms_isa_raw_value_file_workbook"] >= counts["priority_lsms_isa_concept_file_shortlist"]
        and counts["priority_lsms_isa_raw_value_verification_workbook_summary"] > 0
        and file_ok(REPORT_DIR / "priority_lsms_isa_raw_value_verification_workbook.md")
        and priority_lsms_workbook_datasets >= counts["priority_lsms_isa_refocused_acquisition_queue"]
        and priority_lsms_workbook_requirements == counts["priority_lsms_isa_raw_value_requirement_workbook"]
        and priority_lsms_workbook_variables == counts["priority_lsms_isa_raw_value_variable_workbook"]
        and priority_lsms_workbook_files == counts["priority_lsms_isa_raw_value_file_workbook"]
        and priority_lsms_workbook_handoffs >= counts["priority_lsms_isa_refocused_acquisition_queue"]
        and 0 <= priority_lsms_workbook_ready_review <= priority_lsms_workbook_requirements
        and priority_lsms_workbook_blocked_requirements + priority_lsms_workbook_ready_review >= priority_lsms_workbook_requirements
        and priority_lsms_workbook_raw_verified == 0
        and priority_lsms_workbook_data_write == "blocked_no_promoted_rows"
        and priority_lsms_workbook_modeling_gate == "blocked"
    )
    add(
        rows,
        "dataset_promotion",
        "Priority LSMS/ISA raw value verification workbook converts metadata candidates into fillable raw requirement, variable, and file review rows",
        status(priority_lsms_workbook_gate_ok),
        f"requirement_rows={counts['priority_lsms_isa_raw_value_requirement_workbook']}; variable_rows={counts['priority_lsms_isa_raw_value_variable_workbook']}; file_rows={counts['priority_lsms_isa_raw_value_file_workbook']}; summary_rows={counts['priority_lsms_isa_raw_value_verification_workbook_summary']}; reported_datasets={priority_lsms_workbook_datasets}; reported_requirements={priority_lsms_workbook_requirements}; reported_variables={priority_lsms_workbook_variables}; reported_files={priority_lsms_workbook_files}; handoffs={priority_lsms_workbook_handoffs}; ready_review={priority_lsms_workbook_ready_review}; blocked_requirements={priority_lsms_workbook_blocked_requirements}; raw_verified={priority_lsms_workbook_raw_verified}; data_write={priority_lsms_workbook_data_write}; modeling_gate={priority_lsms_workbook_modeling_gate}",
        "" if priority_lsms_workbook_gate_ok else "Run script/149_build_priority_lsms_isa_raw_value_verification_workbook.py after LSMS/ISA variable evidence, raw intake, and archive preflight outputs are current.",
    )
    priority_lsms_receipt_checklist_summary = read_csv_dicts(RESULT_DIR / "priority_lsms_isa_raw_package_receipt_checklist_summary.csv")
    priority_lsms_receipt_datasets = safe_int(next((row.get("value", "0") for row in priority_lsms_receipt_checklist_summary if row.get("metric") == "priority_lsms_receipt_checklist_dataset_rows"), "0"), 0)
    priority_lsms_receipt_requirements = safe_int(next((row.get("value", "0") for row in priority_lsms_receipt_checklist_summary if row.get("metric") == "priority_lsms_receipt_checklist_requirement_rows"), "0"), 0)
    priority_lsms_receipt_package_received = safe_int(next((row.get("value", "0") for row in priority_lsms_receipt_checklist_summary if row.get("metric") == "priority_lsms_receipt_checklist_package_received_rows"), "0"), 0)
    priority_lsms_receipt_public_docs = safe_int(next((row.get("value", "0") for row in priority_lsms_receipt_checklist_summary if row.get("metric") == "priority_lsms_receipt_checklist_public_documentation_snapshot_rows"), "0"), 0)
    priority_lsms_receipt_complete_received = safe_int(next((row.get("value", "0") for row in priority_lsms_receipt_checklist_summary if row.get("metric") == "priority_lsms_receipt_checklist_complete_package_received_rows"), "0"), 0)
    priority_lsms_receipt_ready_review = safe_int(next((row.get("value", "0") for row in priority_lsms_receipt_checklist_summary if row.get("metric") == "priority_lsms_receipt_checklist_ready_for_raw_value_review_rows"), "0"), 0)
    priority_lsms_receipt_blocked_no_original = safe_int(next((row.get("value", "0") for row in priority_lsms_receipt_checklist_summary if row.get("metric") == "priority_lsms_receipt_checklist_blocked_no_original_package_rows"), "0"), 0)
    priority_lsms_receipt_blocked_requirements = safe_int(next((row.get("value", "0") for row in priority_lsms_receipt_checklist_summary if row.get("metric") == "priority_lsms_receipt_checklist_blocked_requirement_rows"), "0"), 0)
    priority_lsms_receipt_handoffs = safe_int(next((row.get("value", "0") for row in priority_lsms_receipt_checklist_summary if row.get("metric") == "priority_lsms_receipt_checklist_handoff_readmes_written"), "0"), 0)
    priority_lsms_receipt_data_write = next((row.get("value", "") for row in priority_lsms_receipt_checklist_summary if row.get("metric") == "priority_lsms_receipt_checklist_data_write_status"), "")
    priority_lsms_receipt_modeling_gate = next((row.get("value", "") for row in priority_lsms_receipt_checklist_summary if row.get("metric") == "modeling_gate_status"), "")
    priority_lsms_receipt_gate_ok = (
        counts["priority_lsms_isa_raw_package_receipt_checklist"] >= counts["priority_lsms_isa_refocused_acquisition_queue"]
        and counts["priority_lsms_isa_raw_package_requirement_receipt_checklist"] >= counts["priority_lsms_isa_raw_value_requirement_workbook"]
        and counts["priority_lsms_isa_raw_package_receipt_checklist_summary"] > 0
        and file_ok(REPORT_DIR / "priority_lsms_isa_raw_package_receipt_checklist.md")
        and priority_lsms_receipt_datasets == counts["priority_lsms_isa_raw_package_receipt_checklist"]
        and priority_lsms_receipt_requirements == counts["priority_lsms_isa_raw_package_requirement_receipt_checklist"]
        and 0 <= priority_lsms_receipt_package_received <= priority_lsms_receipt_datasets
        and priority_lsms_receipt_public_docs >= 0
        and 0 <= priority_lsms_receipt_complete_received <= priority_lsms_receipt_package_received
        and priority_lsms_receipt_ready_review == priority_lsms_receipt_complete_received
        and priority_lsms_receipt_blocked_no_original + priority_lsms_receipt_package_received >= priority_lsms_receipt_datasets
        and priority_lsms_receipt_blocked_requirements + priority_lsms_receipt_ready_review * 8 >= priority_lsms_receipt_requirements
        and priority_lsms_receipt_handoffs >= counts["priority_lsms_isa_refocused_acquisition_queue"]
        and priority_lsms_receipt_data_write == "blocked_no_promoted_rows"
        and priority_lsms_receipt_modeling_gate == "blocked"
    )
    add(
        rows,
        "dataset_promotion",
        "Priority LSMS/ISA raw package receipt checklist defines complete-package receipt fields before raw-value review",
        status(priority_lsms_receipt_gate_ok),
        f"dataset_rows={counts['priority_lsms_isa_raw_package_receipt_checklist']}; requirement_rows={counts['priority_lsms_isa_raw_package_requirement_receipt_checklist']}; summary_rows={counts['priority_lsms_isa_raw_package_receipt_checklist_summary']}; reported_datasets={priority_lsms_receipt_datasets}; reported_requirements={priority_lsms_receipt_requirements}; package_received={priority_lsms_receipt_package_received}; public_docs={priority_lsms_receipt_public_docs}; complete_package_received={priority_lsms_receipt_complete_received}; ready_review={priority_lsms_receipt_ready_review}; blocked_no_original={priority_lsms_receipt_blocked_no_original}; blocked_requirements={priority_lsms_receipt_blocked_requirements}; handoffs={priority_lsms_receipt_handoffs}; data_write={priority_lsms_receipt_data_write}; modeling_gate={priority_lsms_receipt_modeling_gate}",
        "" if priority_lsms_receipt_gate_ok else "Run script/150_build_priority_lsms_isa_raw_package_receipt_checklist.py after the raw value workbook and raw package intake outputs are current.",
    )
    priority_lsms_credentialed_summary = read_csv_dicts(RESULT_DIR / "priority_lsms_isa_credentialed_raw_acquisition_workbench_summary.csv")
    priority_lsms_credentialed_datasets = safe_int(next((row.get("value", "0") for row in priority_lsms_credentialed_summary if row.get("metric") == "priority_lsms_credentialed_workbench_dataset_rows"), "0"), 0)
    priority_lsms_credentialed_full_files = safe_int(next((row.get("value", "0") for row in priority_lsms_credentialed_summary if row.get("metric") == "priority_lsms_credentialed_workbench_full_file_rows"), "0"), 0)
    priority_lsms_credentialed_core_files = safe_int(next((row.get("value", "0") for row in priority_lsms_credentialed_summary if row.get("metric") == "priority_lsms_credentialed_workbench_core_file_rows"), "0"), 0)
    priority_lsms_credentialed_access_gate = safe_int(next((row.get("value", "0") for row in priority_lsms_credentialed_summary if row.get("metric") == "priority_lsms_credentialed_workbench_access_gate_rows"), "0"), 0)
    priority_lsms_credentialed_received = safe_int(next((row.get("value", "0") for row in priority_lsms_credentialed_summary if row.get("metric") == "priority_lsms_credentialed_workbench_package_received_rows"), "0"), 0)
    priority_lsms_credentialed_targets_missing = safe_int(next((row.get("value", "0") for row in priority_lsms_credentialed_summary if row.get("metric") == "priority_lsms_credentialed_workbench_targets_missing_before_download"), "0"), 0)
    priority_lsms_credentialed_handoffs = safe_int(next((row.get("value", "0") for row in priority_lsms_credentialed_summary if row.get("metric") == "priority_lsms_credentialed_workbench_handoff_readmes_written"), "0"), 0)
    priority_lsms_credentialed_data_write = next((row.get("value", "") for row in priority_lsms_credentialed_summary if row.get("metric") == "priority_lsms_credentialed_workbench_data_write_status"), "")
    priority_lsms_credentialed_modeling_gate = next((row.get("value", "") for row in priority_lsms_credentialed_summary if row.get("metric") == "modeling_gate_status"), "")
    priority_lsms_credentialed_gate_ok = (
        counts["priority_lsms_isa_credentialed_raw_acquisition_workbench"] >= counts["priority_lsms_isa_refocused_acquisition_queue"]
        and counts["priority_lsms_isa_credentialed_raw_full_file_manifest"] >= counts["priority_lsms_isa_public_documentation_file_inventory"]
        and counts["priority_lsms_isa_credentialed_raw_core_file_checklist"] >= counts["priority_lsms_isa_concept_file_shortlist"]
        and counts["priority_lsms_isa_credentialed_raw_acquisition_workbench_summary"] > 0
        and file_ok(REPORT_DIR / "priority_lsms_isa_credentialed_raw_acquisition_workbench.md")
        and priority_lsms_credentialed_datasets == counts["priority_lsms_isa_credentialed_raw_acquisition_workbench"]
        and priority_lsms_credentialed_full_files == counts["priority_lsms_isa_credentialed_raw_full_file_manifest"]
        and priority_lsms_credentialed_core_files == counts["priority_lsms_isa_credentialed_raw_core_file_checklist"]
        and priority_lsms_credentialed_access_gate >= counts["priority_lsms_isa_refocused_acquisition_queue"]
        and 0 <= priority_lsms_credentialed_received <= priority_lsms_credentialed_datasets
        and 0 <= priority_lsms_credentialed_targets_missing <= priority_lsms_credentialed_core_files
        and (priority_lsms_credentialed_received > 0 or priority_lsms_credentialed_targets_missing >= priority_lsms_credentialed_core_files)
        and priority_lsms_credentialed_handoffs >= counts["priority_lsms_isa_refocused_acquisition_queue"]
        and priority_lsms_credentialed_data_write == "blocked_no_promoted_rows"
        and priority_lsms_credentialed_modeling_gate == "blocked"
    )
    add(
        rows,
        "dataset_promotion",
        "Priority LSMS/ISA credentialed raw acquisition workbench covers the full 19-wave queue with official file manifests and post-download commands",
        status(priority_lsms_credentialed_gate_ok),
        f"workbench_rows={counts['priority_lsms_isa_credentialed_raw_acquisition_workbench']}; full_file_rows={counts['priority_lsms_isa_credentialed_raw_full_file_manifest']}; core_file_rows={counts['priority_lsms_isa_credentialed_raw_core_file_checklist']}; summary_rows={counts['priority_lsms_isa_credentialed_raw_acquisition_workbench_summary']}; reported_datasets={priority_lsms_credentialed_datasets}; reported_full_files={priority_lsms_credentialed_full_files}; reported_core_files={priority_lsms_credentialed_core_files}; access_gate={priority_lsms_credentialed_access_gate}; package_received={priority_lsms_credentialed_received}; targets_missing={priority_lsms_credentialed_targets_missing}; handoffs={priority_lsms_credentialed_handoffs}; data_write={priority_lsms_credentialed_data_write}; modeling_gate={priority_lsms_credentialed_modeling_gate}",
        "" if priority_lsms_credentialed_gate_ok else "Run script/152_build_priority_lsms_isa_credentialed_raw_acquisition_workbench.py after public documentation, variable evidence, and receipt checklist outputs are current.",
    )
    priority_lsms_official_file_receipt_summary = read_csv_dicts(RESULT_DIR / "priority_lsms_isa_official_file_receipt_validator_summary.csv")
    priority_lsms_official_file_receipt_datasets = safe_int(next((row.get("value", "0") for row in priority_lsms_official_file_receipt_summary if row.get("metric") == "priority_lsms_official_file_receipt_dataset_rows"), "0"), 0)
    priority_lsms_official_file_receipt_expected = safe_int(next((row.get("value", "0") for row in priority_lsms_official_file_receipt_summary if row.get("metric") == "priority_lsms_official_file_receipt_expected_file_rows"), "0"), 0)
    priority_lsms_official_file_receipt_expected_matched = safe_int(next((row.get("value", "0") for row in priority_lsms_official_file_receipt_summary if row.get("metric") == "priority_lsms_official_file_receipt_expected_file_matched_rows"), "0"), 0)
    priority_lsms_official_file_receipt_expected_missing = safe_int(next((row.get("value", "0") for row in priority_lsms_official_file_receipt_summary if row.get("metric") == "priority_lsms_official_file_receipt_expected_file_missing_rows"), "0"), 0)
    priority_lsms_official_file_receipt_core = safe_int(next((row.get("value", "0") for row in priority_lsms_official_file_receipt_summary if row.get("metric") == "priority_lsms_official_file_receipt_core_file_rows"), "0"), 0)
    priority_lsms_official_file_receipt_core_matched = safe_int(next((row.get("value", "0") for row in priority_lsms_official_file_receipt_summary if row.get("metric") == "priority_lsms_official_file_receipt_core_file_matched_rows"), "0"), 0)
    priority_lsms_official_file_receipt_core_missing = safe_int(next((row.get("value", "0") for row in priority_lsms_official_file_receipt_summary if row.get("metric") == "priority_lsms_official_file_receipt_core_file_missing_rows"), "0"), 0)
    priority_lsms_official_file_receipt_core_complete = safe_int(next((row.get("value", "0") for row in priority_lsms_official_file_receipt_summary if row.get("metric") == "priority_lsms_official_file_receipt_core_complete_dataset_rows"), "0"), 0)
    priority_lsms_official_file_receipt_complete = safe_int(next((row.get("value", "0") for row in priority_lsms_official_file_receipt_summary if row.get("metric") == "priority_lsms_official_file_receipt_complete_dataset_rows"), "0"), 0)
    priority_lsms_official_file_receipt_handoffs = safe_int(next((row.get("value", "0") for row in priority_lsms_official_file_receipt_summary if row.get("metric") == "priority_lsms_official_file_receipt_handoff_readmes_written"), "0"), 0)
    priority_lsms_official_file_receipt_data_write = next((row.get("value", "") for row in priority_lsms_official_file_receipt_summary if row.get("metric") == "priority_lsms_official_file_receipt_data_write_status"), "")
    priority_lsms_official_file_receipt_modeling_gate = next((row.get("value", "") for row in priority_lsms_official_file_receipt_summary if row.get("metric") == "modeling_gate_status"), "")
    priority_lsms_official_file_receipt_gate_ok = (
        counts["priority_lsms_isa_official_file_receipt_validation"] >= counts["priority_lsms_isa_refocused_acquisition_queue"]
        and counts["priority_lsms_isa_official_file_receipt_file_match"] >= counts["priority_lsms_isa_credentialed_raw_full_file_manifest"]
        and counts["priority_lsms_isa_official_file_receipt_core_match"] >= counts["priority_lsms_isa_credentialed_raw_core_file_checklist"]
        and counts["priority_lsms_isa_official_file_receipt_validator_summary"] > 0
        and file_ok(REPORT_DIR / "priority_lsms_isa_official_file_receipt_validator.md")
        and priority_lsms_official_file_receipt_datasets == counts["priority_lsms_isa_official_file_receipt_validation"]
        and priority_lsms_official_file_receipt_expected == counts["priority_lsms_isa_official_file_receipt_file_match"]
        and priority_lsms_official_file_receipt_core == counts["priority_lsms_isa_official_file_receipt_core_match"]
        and priority_lsms_official_file_receipt_expected_matched + priority_lsms_official_file_receipt_expected_missing == priority_lsms_official_file_receipt_expected
        and priority_lsms_official_file_receipt_core_matched + priority_lsms_official_file_receipt_core_missing == priority_lsms_official_file_receipt_core
        and priority_lsms_official_file_receipt_core_complete <= priority_lsms_official_file_receipt_datasets
        and priority_lsms_official_file_receipt_complete <= priority_lsms_official_file_receipt_datasets
        and priority_lsms_official_file_receipt_handoffs >= counts["priority_lsms_isa_refocused_acquisition_queue"]
        and priority_lsms_official_file_receipt_data_write == "blocked_no_promoted_rows"
        and priority_lsms_official_file_receipt_modeling_gate == "blocked"
    )
    add(
        rows,
        "dataset_promotion",
        "Priority LSMS/ISA official file receipt validator compares local package contents against official DDI file names before raw-value review",
        status(priority_lsms_official_file_receipt_gate_ok),
        f"validation_rows={counts['priority_lsms_isa_official_file_receipt_validation']}; file_match_rows={counts['priority_lsms_isa_official_file_receipt_file_match']}; core_match_rows={counts['priority_lsms_isa_official_file_receipt_core_match']}; summary_rows={counts['priority_lsms_isa_official_file_receipt_validator_summary']}; reported_datasets={priority_lsms_official_file_receipt_datasets}; expected_files={priority_lsms_official_file_receipt_expected}; expected_matched={priority_lsms_official_file_receipt_expected_matched}; expected_missing={priority_lsms_official_file_receipt_expected_missing}; core_files={priority_lsms_official_file_receipt_core}; core_matched={priority_lsms_official_file_receipt_core_matched}; core_missing={priority_lsms_official_file_receipt_core_missing}; core_complete={priority_lsms_official_file_receipt_core_complete}; complete={priority_lsms_official_file_receipt_complete}; handoffs={priority_lsms_official_file_receipt_handoffs}; data_write={priority_lsms_official_file_receipt_data_write}; modeling_gate={priority_lsms_official_file_receipt_modeling_gate}",
        "" if priority_lsms_official_file_receipt_gate_ok else "Run script/153_validate_priority_lsms_isa_official_file_receipt.py after raw package intake, archive preflight, and credentialed acquisition workbench outputs are current.",
    )
    priority_lsms_threshold_sequence_summary = read_csv_dicts(RESULT_DIR / "priority_lsms_isa_threshold_download_sequence_summary.csv")
    priority_lsms_threshold_sequence_datasets = safe_int(next((row.get("value", "0") for row in priority_lsms_threshold_sequence_summary if row.get("metric") == "priority_lsms_threshold_sequence_dataset_rows"), "0"), 0)
    priority_lsms_threshold_sequence_countries = safe_int(next((row.get("value", "0") for row in priority_lsms_threshold_sequence_summary if row.get("metric") == "priority_lsms_threshold_sequence_country_rows"), "0"), 0)
    priority_lsms_threshold_sequence_priority_rows = safe_int(next((row.get("value", "0") for row in priority_lsms_threshold_sequence_summary if row.get("metric") == "priority_lsms_threshold_sequence_priority_country_rows"), "0"), 0)
    priority_lsms_threshold_sequence_minimum_downloads = safe_int(next((row.get("value", "0") for row in priority_lsms_threshold_sequence_summary if row.get("metric") == "priority_lsms_threshold_sequence_minimum_download_rows"), "0"), 0)
    priority_lsms_threshold_sequence_minimum_countries = safe_int(next((row.get("value", "0") for row in priority_lsms_threshold_sequence_summary if row.get("metric") == "priority_lsms_threshold_sequence_minimum_country_rows"), "0"), 0)
    priority_lsms_threshold_sequence_recommended_downloads = safe_int(next((row.get("value", "0") for row in priority_lsms_threshold_sequence_summary if row.get("metric") == "priority_lsms_threshold_sequence_recommended_download_rows"), "0"), 0)
    priority_lsms_threshold_sequence_recommended_countries = safe_int(next((row.get("value", "0") for row in priority_lsms_threshold_sequence_summary if row.get("metric") == "priority_lsms_threshold_sequence_recommended_country_rows"), "0"), 0)
    priority_lsms_threshold_sequence_expected = safe_int(next((row.get("value", "0") for row in priority_lsms_threshold_sequence_summary if row.get("metric") == "priority_lsms_threshold_sequence_expected_file_rows"), "0"), 0)
    priority_lsms_threshold_sequence_expected_matched = safe_int(next((row.get("value", "0") for row in priority_lsms_threshold_sequence_summary if row.get("metric") == "priority_lsms_threshold_sequence_expected_file_matched_rows"), "0"), 0)
    priority_lsms_threshold_sequence_core = safe_int(next((row.get("value", "0") for row in priority_lsms_threshold_sequence_summary if row.get("metric") == "priority_lsms_threshold_sequence_core_file_rows"), "0"), 0)
    priority_lsms_threshold_sequence_core_matched = safe_int(next((row.get("value", "0") for row in priority_lsms_threshold_sequence_summary if row.get("metric") == "priority_lsms_threshold_sequence_core_file_matched_rows"), "0"), 0)
    priority_lsms_threshold_sequence_raw_received = safe_int(next((row.get("value", "0") for row in priority_lsms_threshold_sequence_summary if row.get("metric") == "priority_lsms_threshold_sequence_raw_package_received_rows"), "0"), 0)
    priority_lsms_threshold_sequence_promoted = safe_int(next((row.get("value", "0") for row in priority_lsms_threshold_sequence_summary if row.get("metric") == "priority_lsms_threshold_sequence_promoted_analysis_ready_rows"), "0"), 0)
    priority_lsms_threshold_sequence_handoffs = safe_int(next((row.get("value", "0") for row in priority_lsms_threshold_sequence_summary if row.get("metric") == "priority_lsms_threshold_sequence_handoff_readmes_written"), "0"), 0)
    priority_lsms_threshold_sequence_data_write = next((row.get("value", "") for row in priority_lsms_threshold_sequence_summary if row.get("metric") == "priority_lsms_threshold_sequence_data_write_status"), "")
    priority_lsms_threshold_sequence_modeling_gate = next((row.get("value", "") for row in priority_lsms_threshold_sequence_summary if row.get("metric") == "modeling_gate_status"), "")
    priority_lsms_threshold_sequence_gate_ok = (
        counts["priority_lsms_isa_threshold_download_sequence"] >= counts["priority_lsms_isa_refocused_acquisition_queue"]
        and counts["priority_lsms_isa_threshold_minimum_batch"] == 11
        and counts["priority_lsms_isa_threshold_country_coverage"] >= 6
        and counts["priority_lsms_isa_threshold_download_sequence_summary"] > 0
        and file_ok(REPORT_DIR / "priority_lsms_isa_threshold_download_sequence.md")
        and priority_lsms_threshold_sequence_datasets == counts["priority_lsms_isa_threshold_download_sequence"]
        and priority_lsms_threshold_sequence_countries == counts["priority_lsms_isa_threshold_country_coverage"]
        and priority_lsms_threshold_sequence_priority_rows >= 16
        and priority_lsms_threshold_sequence_minimum_downloads == counts["priority_lsms_isa_threshold_minimum_batch"]
        and priority_lsms_threshold_sequence_minimum_countries >= 6
        and priority_lsms_threshold_sequence_recommended_downloads >= 13
        and priority_lsms_threshold_sequence_recommended_countries >= 8
        and priority_lsms_threshold_sequence_expected == counts["priority_lsms_isa_official_file_receipt_file_match"]
        and priority_lsms_threshold_sequence_core == counts["priority_lsms_isa_official_file_receipt_core_match"]
        and 0 <= priority_lsms_threshold_sequence_expected_matched <= priority_lsms_threshold_sequence_expected
        and 0 <= priority_lsms_threshold_sequence_core_matched <= priority_lsms_threshold_sequence_core
        and 0 <= priority_lsms_threshold_sequence_raw_received <= priority_lsms_threshold_sequence_datasets
        and 0 <= priority_lsms_threshold_sequence_promoted <= priority_lsms_threshold_sequence_datasets
        and priority_lsms_threshold_sequence_handoffs >= counts["priority_lsms_isa_refocused_acquisition_queue"]
        and priority_lsms_threshold_sequence_data_write == "blocked_no_promoted_rows"
        and priority_lsms_threshold_sequence_modeling_gate == "blocked"
    )
    add(
        rows,
        "dataset_promotion",
        "Priority LSMS/ISA threshold download sequence updates the old 13-wave campaign to the current 19-wave refocused queue",
        status(priority_lsms_threshold_sequence_gate_ok),
        f"sequence_rows={counts['priority_lsms_isa_threshold_download_sequence']}; minimum_rows={counts['priority_lsms_isa_threshold_minimum_batch']}; country_rows={counts['priority_lsms_isa_threshold_country_coverage']}; summary_rows={counts['priority_lsms_isa_threshold_download_sequence_summary']}; reported_datasets={priority_lsms_threshold_sequence_datasets}; countries={priority_lsms_threshold_sequence_countries}; priority_rows={priority_lsms_threshold_sequence_priority_rows}; minimum_downloads={priority_lsms_threshold_sequence_minimum_downloads}; minimum_countries={priority_lsms_threshold_sequence_minimum_countries}; recommended_downloads={priority_lsms_threshold_sequence_recommended_downloads}; recommended_countries={priority_lsms_threshold_sequence_recommended_countries}; expected_files={priority_lsms_threshold_sequence_expected}; expected_matched={priority_lsms_threshold_sequence_expected_matched}; core_files={priority_lsms_threshold_sequence_core}; core_matched={priority_lsms_threshold_sequence_core_matched}; raw_received={priority_lsms_threshold_sequence_raw_received}; promoted={priority_lsms_threshold_sequence_promoted}; handoffs={priority_lsms_threshold_sequence_handoffs}; data_write={priority_lsms_threshold_sequence_data_write}; modeling_gate={priority_lsms_threshold_sequence_modeling_gate}",
        "" if priority_lsms_threshold_sequence_gate_ok else "Run script/154_build_priority_lsms_isa_threshold_download_sequence.py after refocused queue and official file receipt validation outputs are current.",
    )
    priority_lsms_minimum_intake_summary = read_csv_dicts(RESULT_DIR / "priority_lsms_isa_minimum_batch_raw_intake_guide_summary.csv")
    priority_lsms_minimum_intake_waves = safe_int(next((row.get("value", "0") for row in priority_lsms_minimum_intake_summary if row.get("metric") == "priority_lsms_minimum_batch_country_wave_rows"), "0"), 0)
    priority_lsms_minimum_intake_countries = safe_int(next((row.get("value", "0") for row in priority_lsms_minimum_intake_summary if row.get("metric") == "priority_lsms_minimum_batch_country_rows"), "0"), 0)
    priority_lsms_minimum_intake_expected_full = safe_int(next((row.get("value", "0") for row in priority_lsms_minimum_intake_summary if row.get("metric") == "priority_lsms_minimum_batch_expected_full_file_rows"), "0"), 0)
    priority_lsms_minimum_intake_matched_full = safe_int(next((row.get("value", "0") for row in priority_lsms_minimum_intake_summary if row.get("metric") == "priority_lsms_minimum_batch_matched_full_file_rows"), "0"), 0)
    priority_lsms_minimum_intake_missing_full = safe_int(next((row.get("value", "0") for row in priority_lsms_minimum_intake_summary if row.get("metric") == "priority_lsms_minimum_batch_missing_full_file_rows"), "0"), 0)
    priority_lsms_minimum_intake_expected_core = safe_int(next((row.get("value", "0") for row in priority_lsms_minimum_intake_summary if row.get("metric") == "priority_lsms_minimum_batch_expected_core_file_rows"), "0"), 0)
    priority_lsms_minimum_intake_missing_core = safe_int(next((row.get("value", "0") for row in priority_lsms_minimum_intake_summary if row.get("metric") == "priority_lsms_minimum_batch_missing_core_file_rows"), "0"), 0)
    priority_lsms_minimum_intake_handoffs = safe_int(next((row.get("value", "0") for row in priority_lsms_minimum_intake_summary if row.get("metric") == "priority_lsms_minimum_batch_handoff_readmes_written"), "0"), 0)
    priority_lsms_minimum_intake_data_write = next((row.get("value", "") for row in priority_lsms_minimum_intake_summary if row.get("metric") == "priority_lsms_minimum_batch_data_write_status"), "")
    priority_lsms_minimum_intake_modeling_gate = next((row.get("value", "") for row in priority_lsms_minimum_intake_summary if row.get("metric") == "modeling_gate_status"), "")
    priority_lsms_minimum_intake_gate_ok = (
        counts["priority_lsms_isa_minimum_batch_raw_intake_guide"] == counts["priority_lsms_isa_threshold_minimum_batch"] == 11
        and counts["priority_lsms_isa_minimum_batch_expected_file_manifest"] == priority_lsms_minimum_intake_expected_full
        and counts["priority_lsms_isa_minimum_batch_core_file_manifest"] == priority_lsms_minimum_intake_expected_core
        and counts["priority_lsms_isa_minimum_batch_raw_intake_guide_summary"] > 0
        and file_ok(REPORT_DIR / "priority_lsms_isa_minimum_batch_raw_intake_guide.md")
        and priority_lsms_minimum_intake_waves == 11
        and priority_lsms_minimum_intake_countries >= 6
        and priority_lsms_minimum_intake_expected_full >= 800
        and priority_lsms_minimum_intake_expected_core >= 300
        and priority_lsms_minimum_intake_missing_full == priority_lsms_minimum_intake_expected_full - priority_lsms_minimum_intake_matched_full
        and priority_lsms_minimum_intake_missing_core <= priority_lsms_minimum_intake_expected_core
        and priority_lsms_minimum_intake_handoffs == 11
        and priority_lsms_minimum_intake_data_write == "blocked_no_value_verified_raw_packages"
        and priority_lsms_minimum_intake_modeling_gate == "blocked"
    )
    add(
        rows,
        "dataset_promotion",
        "Priority LSMS/ISA minimum-batch raw intake guide gives exact official file and core-file worklists for the 11-wave threshold batch",
        status(priority_lsms_minimum_intake_gate_ok),
        f"guide_rows={counts['priority_lsms_isa_minimum_batch_raw_intake_guide']}; expected_manifest_rows={counts['priority_lsms_isa_minimum_batch_expected_file_manifest']}; core_manifest_rows={counts['priority_lsms_isa_minimum_batch_core_file_manifest']}; summary_rows={counts['priority_lsms_isa_minimum_batch_raw_intake_guide_summary']}; reported_waves={priority_lsms_minimum_intake_waves}; countries={priority_lsms_minimum_intake_countries}; expected_full={priority_lsms_minimum_intake_expected_full}; matched_full={priority_lsms_minimum_intake_matched_full}; missing_full={priority_lsms_minimum_intake_missing_full}; expected_core={priority_lsms_minimum_intake_expected_core}; missing_core={priority_lsms_minimum_intake_missing_core}; handoffs={priority_lsms_minimum_intake_handoffs}; data_write={priority_lsms_minimum_intake_data_write}; modeling_gate={priority_lsms_minimum_intake_modeling_gate}",
        "" if priority_lsms_minimum_intake_gate_ok else "Run script/155_build_priority_lsms_isa_minimum_batch_raw_intake_guide.py after threshold sequence and official file receipt validation outputs are current.",
    )
    priority_lsms_minimum_endpoint_summary = read_csv_dicts(RESULT_DIR / "priority_lsms_isa_minimum_batch_endpoint_refresh_summary.csv")
    priority_lsms_minimum_endpoint_waves = safe_int(next((row.get("value", "0") for row in priority_lsms_minimum_endpoint_summary if row.get("metric") == "priority_lsms_minimum_endpoint_dataset_rows"), "0"), 0)
    priority_lsms_minimum_endpoint_countries = safe_int(next((row.get("value", "0") for row in priority_lsms_minimum_endpoint_summary if row.get("metric") == "priority_lsms_minimum_endpoint_country_rows"), "0"), 0)
    priority_lsms_minimum_endpoint_rows = safe_int(next((row.get("value", "0") for row in priority_lsms_minimum_endpoint_summary if row.get("metric") == "priority_lsms_minimum_endpoint_rows"), "0"), 0)
    priority_lsms_minimum_endpoint_metadata = safe_int(next((row.get("value", "0") for row in priority_lsms_minimum_endpoint_summary if row.get("metric") == "priority_lsms_minimum_endpoint_public_metadata_endpoint_rows"), "0"), 0)
    priority_lsms_minimum_endpoint_gate_rows = safe_int(next((row.get("value", "0") for row in priority_lsms_minimum_endpoint_summary if row.get("metric") == "priority_lsms_minimum_endpoint_get_microdata_gate_dataset_rows"), "0"), 0)
    priority_lsms_minimum_endpoint_raw_candidates = safe_int(next((row.get("value", "0") for row in priority_lsms_minimum_endpoint_summary if row.get("metric") == "priority_lsms_minimum_endpoint_raw_download_candidate_rows"), "0"), 0)
    priority_lsms_minimum_endpoint_credentialed = safe_int(next((row.get("value", "0") for row in priority_lsms_minimum_endpoint_summary if row.get("metric") == "priority_lsms_minimum_endpoint_credentialed_download_required_rows"), "0"), 0)
    priority_lsms_minimum_endpoint_handoffs = safe_int(next((row.get("value", "0") for row in priority_lsms_minimum_endpoint_summary if row.get("metric") == "priority_lsms_minimum_endpoint_handoff_readmes_written"), "0"), 0)
    priority_lsms_minimum_endpoint_data_write = next((row.get("value", "") for row in priority_lsms_minimum_endpoint_summary if row.get("metric") == "priority_lsms_minimum_endpoint_data_write_status"), "")
    priority_lsms_minimum_endpoint_modeling_gate = next((row.get("value", "") for row in priority_lsms_minimum_endpoint_summary if row.get("metric") == "modeling_gate_status"), "")
    priority_lsms_minimum_endpoint_gate_ok = (
        counts["priority_lsms_isa_minimum_batch_endpoint_refresh"] == priority_lsms_minimum_endpoint_rows
        and counts["priority_lsms_isa_minimum_batch_endpoint_dataset_status"] == priority_lsms_minimum_endpoint_waves
        and counts["priority_lsms_isa_minimum_batch_endpoint_refresh_summary"] > 0
        and file_ok(REPORT_DIR / "priority_lsms_isa_minimum_batch_endpoint_refresh.md")
        and priority_lsms_minimum_endpoint_waves == 11
        and priority_lsms_minimum_endpoint_countries >= 6
        and priority_lsms_minimum_endpoint_rows == 88
        and priority_lsms_minimum_endpoint_metadata >= 40
        and priority_lsms_minimum_endpoint_gate_rows == 11
        and 0 <= priority_lsms_minimum_endpoint_raw_candidates <= priority_lsms_minimum_endpoint_rows
        and priority_lsms_minimum_endpoint_credentialed >= 0
        and priority_lsms_minimum_endpoint_handoffs == 11
        and priority_lsms_minimum_endpoint_data_write == "blocked_no_raw_package_receipt"
        and priority_lsms_minimum_endpoint_modeling_gate == "blocked"
    )
    add(
        rows,
        "dataset_promotion",
        "Priority LSMS/ISA minimum-batch endpoint refresh checks current official World Bank routes for the exact 11-wave threshold batch",
        status(priority_lsms_minimum_endpoint_gate_ok),
        f"endpoint_rows={counts['priority_lsms_isa_minimum_batch_endpoint_refresh']}; dataset_rows={counts['priority_lsms_isa_minimum_batch_endpoint_dataset_status']}; summary_rows={counts['priority_lsms_isa_minimum_batch_endpoint_refresh_summary']}; reported_waves={priority_lsms_minimum_endpoint_waves}; countries={priority_lsms_minimum_endpoint_countries}; metadata_hits={priority_lsms_minimum_endpoint_metadata}; gate_waves={priority_lsms_minimum_endpoint_gate_rows}; raw_candidates={priority_lsms_minimum_endpoint_raw_candidates}; credentialed_required={priority_lsms_minimum_endpoint_credentialed}; handoffs={priority_lsms_minimum_endpoint_handoffs}; data_write={priority_lsms_minimum_endpoint_data_write}; modeling_gate={priority_lsms_minimum_endpoint_modeling_gate}",
        "" if priority_lsms_minimum_endpoint_gate_ok else "Run script/156_probe_priority_lsms_isa_minimum_batch_endpoint_refresh.py after the minimum-batch threshold file is current and network is available.",
    )
    priority_lsms_next_raw_package_summary = read_csv_dicts(RESULT_DIR / "priority_lsms_isa_next_raw_package_action_summary.csv")
    priority_lsms_next_raw_package_actions = safe_int(next((row.get("value", "0") for row in priority_lsms_next_raw_package_summary if row.get("metric") == "next_raw_package_action_rows"), "0"), 0)
    priority_lsms_next_raw_package_minimum_remaining = safe_int(next((row.get("value", "0") for row in priority_lsms_next_raw_package_summary if row.get("metric") == "minimum_batch_remaining_action_rows"), "0"), 0)
    priority_lsms_next_raw_package_backups = safe_int(next((row.get("value", "0") for row in priority_lsms_next_raw_package_summary if row.get("metric") == "backup_after_minimum_action_rows"), "0"), 0)
    priority_lsms_next_raw_package_core_rows = safe_int(next((row.get("value", "0") for row in priority_lsms_next_raw_package_summary if row.get("metric") == "core_file_action_rows"), "0"), 0)
    priority_lsms_next_raw_package_countries_if_pass = safe_int(next((row.get("value", "0") for row in priority_lsms_next_raw_package_summary if row.get("metric") == "countries_if_minimum_batch_passes"), "0"), 0)
    priority_lsms_next_raw_package_waves_if_pass = safe_int(next((row.get("value", "0") for row in priority_lsms_next_raw_package_summary if row.get("metric") == "country_waves_if_minimum_batch_passes"), "0"), 0)
    priority_lsms_next_raw_package_raw_candidates = safe_int(next((row.get("value", "0") for row in priority_lsms_next_raw_package_summary if row.get("metric") == "official_raw_download_candidate_rows"), "0"), 0)
    priority_lsms_next_raw_package_credentialed = safe_int(next((row.get("value", "0") for row in priority_lsms_next_raw_package_summary if row.get("metric") == "credentialed_download_required_rows"), "0"), 0)
    priority_lsms_next_raw_package_data_write = next((row.get("value", "") for row in priority_lsms_next_raw_package_summary if row.get("metric") == "data_write_gate_status"), "")
    priority_lsms_next_raw_package_modeling_gate = next((row.get("value", "") for row in priority_lsms_next_raw_package_summary if row.get("metric") == "modeling_gate_status"), "")
    priority_lsms_next_raw_package_gate_ok = (
        counts["priority_lsms_isa_next_raw_package_action_summary"] > 0
        and counts["priority_lsms_isa_next_raw_package_action_queue"] == priority_lsms_next_raw_package_actions
        and counts["priority_lsms_isa_next_raw_package_core_files"] == priority_lsms_next_raw_package_core_rows
        and file_ok(REPORT_DIR / "priority_lsms_isa_next_raw_package_action_packet.md")
        and priority_lsms_next_raw_package_actions >= 10
        and priority_lsms_next_raw_package_minimum_remaining == 10
        and priority_lsms_next_raw_package_backups >= 0
        and priority_lsms_next_raw_package_core_rows > 0
        and priority_lsms_next_raw_package_countries_if_pass == 6
        and priority_lsms_next_raw_package_waves_if_pass == 11
        and priority_lsms_next_raw_package_raw_candidates == 0
        and priority_lsms_next_raw_package_credentialed == 11
        and priority_lsms_next_raw_package_data_write == "blocked_raw_package_acquisition_required"
        and priority_lsms_next_raw_package_modeling_gate == "blocked"
    )
    add(
        rows,
        "dataset_promotion",
        "Priority LSMS/ISA next raw package action packet identifies the exact remaining raw package acquisitions before any additional data writes or ML",
        status(priority_lsms_next_raw_package_gate_ok),
        f"action_rows={counts['priority_lsms_isa_next_raw_package_action_queue']}; summary_rows={counts['priority_lsms_isa_next_raw_package_action_summary']}; core_rows={counts['priority_lsms_isa_next_raw_package_core_files']}; minimum_remaining={priority_lsms_next_raw_package_minimum_remaining}; backups={priority_lsms_next_raw_package_backups}; countries_if_pass={priority_lsms_next_raw_package_countries_if_pass}; waves_if_pass={priority_lsms_next_raw_package_waves_if_pass}; raw_candidates={priority_lsms_next_raw_package_raw_candidates}; credentialed_required={priority_lsms_next_raw_package_credentialed}; data_write={priority_lsms_next_raw_package_data_write}; modeling_gate={priority_lsms_next_raw_package_modeling_gate}",
        "" if priority_lsms_next_raw_package_gate_ok else "Run script/172_build_priority_lsms_isa_next_raw_package_action_packet.py after the endpoint refresh and threshold files are current.",
    )
    priority_lsms_incoming_router_summary = read_csv_dicts(RESULT_DIR / "priority_lsms_isa_incoming_raw_package_router_summary.csv")
    priority_lsms_incoming_router_folder = next((row.get("value", "") for row in priority_lsms_incoming_router_summary if row.get("metric") == "priority_lsms_incoming_router_incoming_folder_exists"), "")
    priority_lsms_incoming_router_action_waves = safe_int(next((row.get("value", "0") for row in priority_lsms_incoming_router_summary if row.get("metric") == "priority_lsms_incoming_router_action_country_wave_rows"), "0"), 0)
    priority_lsms_incoming_router_files = safe_int(next((row.get("value", "0") for row in priority_lsms_incoming_router_summary if row.get("metric") == "priority_lsms_incoming_router_incoming_file_rows"), "0"), 0)
    priority_lsms_incoming_router_candidates = safe_int(next((row.get("value", "0") for row in priority_lsms_incoming_router_summary if row.get("metric") == "priority_lsms_incoming_router_candidate_rows"), "0"), 0)
    priority_lsms_incoming_router_copy = safe_int(next((row.get("value", "0") for row in priority_lsms_incoming_router_summary if row.get("metric") == "priority_lsms_incoming_router_copy_candidate_rows"), "0"), 0)
    priority_lsms_incoming_router_manual = safe_int(next((row.get("value", "0") for row in priority_lsms_incoming_router_summary if row.get("metric") == "priority_lsms_incoming_router_manual_review_rows"), "0"), 0)
    priority_lsms_incoming_router_data_write = next((row.get("value", "") for row in priority_lsms_incoming_router_summary if row.get("metric") == "priority_lsms_incoming_router_data_write_status"), "")
    priority_lsms_incoming_router_modeling = next((row.get("value", "") for row in priority_lsms_incoming_router_summary if row.get("metric") == "modeling_gate_status"), "")
    priority_lsms_incoming_router_gate_ok = (
        counts["priority_lsms_isa_incoming_raw_package_router_summary"] > 0
        and counts["priority_lsms_isa_incoming_raw_package_route_plan"] == priority_lsms_incoming_router_files
        and counts["priority_lsms_isa_incoming_raw_package_route_candidates"] == priority_lsms_incoming_router_candidates
        and file_ok(REPORT_DIR / "priority_lsms_isa_incoming_raw_package_router.md")
        and priority_lsms_incoming_router_folder == "1"
        and priority_lsms_incoming_router_action_waves == counts["priority_lsms_isa_next_raw_package_action_queue"]
        and priority_lsms_incoming_router_files >= priority_lsms_incoming_router_copy
        and priority_lsms_incoming_router_files >= priority_lsms_incoming_router_manual
        and priority_lsms_incoming_router_data_write == "blocked_no_data_write"
        and priority_lsms_incoming_router_modeling == "blocked"
    )
    add(
        rows,
        "dataset_promotion",
        "Priority LSMS/ISA incoming raw package router scores manually downloaded files before target-folder copying",
        status(priority_lsms_incoming_router_gate_ok),
        f"incoming_folder={priority_lsms_incoming_router_folder}; action_waves={priority_lsms_incoming_router_action_waves}; incoming_files={priority_lsms_incoming_router_files}; candidate_rows={priority_lsms_incoming_router_candidates}; copy_candidates={priority_lsms_incoming_router_copy}; manual_review={priority_lsms_incoming_router_manual}; plan_rows={counts['priority_lsms_isa_incoming_raw_package_route_plan']}; data_write={priority_lsms_incoming_router_data_write}; modeling_gate={priority_lsms_incoming_router_modeling}",
        "" if priority_lsms_incoming_router_gate_ok else "Run script/174_build_priority_lsms_isa_incoming_raw_package_router.py after next raw package action queue is current.",
    )
    priority_lsms_threshold_gap_summary = read_csv_dicts(RESULT_DIR / "priority_lsms_isa_threshold_gap_control_panel_summary.csv")
    priority_lsms_threshold_gap_current_promoted = safe_int(next((row.get("value", "0") for row in priority_lsms_threshold_gap_summary if row.get("metric") == "current_promoted_analysis_ready_rows"), "0"), 0)
    priority_lsms_threshold_gap_current_countries = safe_int(next((row.get("value", "0") for row in priority_lsms_threshold_gap_summary if row.get("metric") == "current_promoted_country_rows"), "0"), 0)
    priority_lsms_threshold_gap_country_gap = safe_int(next((row.get("value", "0") for row in priority_lsms_threshold_gap_summary if row.get("metric") == "current_country_gap_to_threshold"), "0"), 0)
    priority_lsms_threshold_gap_wave_gap = safe_int(next((row.get("value", "0") for row in priority_lsms_threshold_gap_summary if row.get("metric") == "current_country_wave_gap_to_threshold"), "0"), 0)
    priority_lsms_threshold_gap_minimum_rows = safe_int(next((row.get("value", "0") for row in priority_lsms_threshold_gap_summary if row.get("metric") == "minimum_threshold_batch_rows"), "0"), 0)
    priority_lsms_threshold_gap_minimum_remaining = safe_int(next((row.get("value", "0") for row in priority_lsms_threshold_gap_summary if row.get("metric") == "minimum_threshold_batch_remaining_download_rows"), "0"), 0)
    priority_lsms_threshold_gap_countries_if_pass = safe_int(next((row.get("value", "0") for row in priority_lsms_threshold_gap_summary if row.get("metric") == "countries_if_minimum_remaining_passes"), "0"), 0)
    priority_lsms_threshold_gap_waves_if_pass = safe_int(next((row.get("value", "0") for row in priority_lsms_threshold_gap_summary if row.get("metric") == "country_waves_if_minimum_remaining_passes"), "0"), 0)
    priority_lsms_threshold_gap_country_buffer = safe_int(next((row.get("value", "0") for row in priority_lsms_threshold_gap_summary if row.get("metric") == "country_buffer_if_minimum_remaining_passes"), "0"), 0)
    priority_lsms_threshold_gap_wave_buffer = safe_int(next((row.get("value", "0") for row in priority_lsms_threshold_gap_summary if row.get("metric") == "country_wave_buffer_if_minimum_remaining_passes"), "0"), 0)
    priority_lsms_threshold_gap_missing_core = safe_int(next((row.get("value", "0") for row in priority_lsms_threshold_gap_summary if row.get("metric") == "minimum_batch_missing_core_file_rows"), "0"), 0)
    priority_lsms_threshold_gap_download_rows = safe_int(next((row.get("value", "0") for row in priority_lsms_threshold_gap_summary if row.get("metric") == "download_panel_rows"), "0"), 0)
    priority_lsms_threshold_gap_country_rows = safe_int(next((row.get("value", "0") for row in priority_lsms_threshold_gap_summary if row.get("metric") == "country_panel_rows"), "0"), 0)
    priority_lsms_threshold_gap_data_write = next((row.get("value", "") for row in priority_lsms_threshold_gap_summary if row.get("metric") == "data_write_gate_status"), "")
    priority_lsms_threshold_gap_modeling = next((row.get("value", "") for row in priority_lsms_threshold_gap_summary if row.get("metric") == "modeling_gate_status"), "")
    priority_lsms_threshold_gap_gate_ok = (
        counts["priority_lsms_isa_threshold_gap_control_panel_summary"] > 0
        and counts["priority_lsms_isa_threshold_gap_download_panel"] == priority_lsms_threshold_gap_download_rows
        and counts["priority_lsms_isa_threshold_gap_country_panel"] == priority_lsms_threshold_gap_country_rows
        and file_ok(REPORT_DIR / "priority_lsms_isa_threshold_gap_control_panel.md")
        and priority_lsms_threshold_gap_current_promoted == 1
        and priority_lsms_threshold_gap_current_countries == 1
        and priority_lsms_threshold_gap_country_gap == 5
        and priority_lsms_threshold_gap_wave_gap == 9
        and priority_lsms_threshold_gap_minimum_rows == counts["priority_lsms_isa_threshold_minimum_batch"]
        and priority_lsms_threshold_gap_minimum_remaining == priority_lsms_next_raw_package_minimum_remaining
        and priority_lsms_threshold_gap_countries_if_pass == 6
        and priority_lsms_threshold_gap_waves_if_pass == 11
        and priority_lsms_threshold_gap_country_buffer == 0
        and priority_lsms_threshold_gap_wave_buffer == 1
        and priority_lsms_threshold_gap_missing_core > 0
        and priority_lsms_threshold_gap_data_write == "blocked_no_new_data_write"
        and priority_lsms_threshold_gap_modeling == "blocked"
    )
    add(
        rows,
        "dataset_promotion",
        "Priority LSMS/ISA threshold gap control panel states the exact country/wave gap before any model rerun",
        status(priority_lsms_threshold_gap_gate_ok),
        f"download_rows={counts['priority_lsms_isa_threshold_gap_download_panel']}; country_rows={counts['priority_lsms_isa_threshold_gap_country_panel']}; summary_rows={counts['priority_lsms_isa_threshold_gap_control_panel_summary']}; current_promoted={priority_lsms_threshold_gap_current_promoted}; current_countries={priority_lsms_threshold_gap_current_countries}; country_gap={priority_lsms_threshold_gap_country_gap}; wave_gap={priority_lsms_threshold_gap_wave_gap}; minimum_remaining={priority_lsms_threshold_gap_minimum_remaining}; countries_if_pass={priority_lsms_threshold_gap_countries_if_pass}; waves_if_pass={priority_lsms_threshold_gap_waves_if_pass}; country_buffer={priority_lsms_threshold_gap_country_buffer}; wave_buffer={priority_lsms_threshold_gap_wave_buffer}; missing_core={priority_lsms_threshold_gap_missing_core}; data_write={priority_lsms_threshold_gap_data_write}; modeling_gate={priority_lsms_threshold_gap_modeling}",
        "" if priority_lsms_threshold_gap_gate_ok else "Run script/175_build_priority_lsms_isa_threshold_gap_control_panel.py after the next raw package action queue and incoming router are current.",
    )
    priority_lsms_manual_packet_summary = read_csv_dicts(RESULT_DIR / "priority_lsms_isa_manual_download_packet_summary.csv")
    priority_lsms_manual_packet_rows = safe_int(next((row.get("value", "0") for row in priority_lsms_manual_packet_summary if row.get("metric") == "manual_download_packet_rows"), "0"), 0)
    priority_lsms_manual_packet_priority_rows = safe_int(next((row.get("value", "0") for row in priority_lsms_manual_packet_summary if row.get("metric") == "manual_download_packet_priority_country_rows"), "0"), 0)
    priority_lsms_manual_packet_sixth_rows = safe_int(next((row.get("value", "0") for row in priority_lsms_manual_packet_summary if row.get("metric") == "manual_download_packet_sixth_country_rows"), "0"), 0)
    priority_lsms_manual_packet_missing_full = safe_int(next((row.get("value", "0") for row in priority_lsms_manual_packet_summary if row.get("metric") == "manual_download_packet_missing_full_file_rows"), "0"), 0)
    priority_lsms_manual_packet_core_rows = safe_int(next((row.get("value", "0") for row in priority_lsms_manual_packet_summary if row.get("metric") == "manual_download_packet_core_file_rows"), "0"), 0)
    priority_lsms_manual_packet_missing_core = safe_int(next((row.get("value", "0") for row in priority_lsms_manual_packet_summary if row.get("metric") == "manual_download_packet_missing_core_file_rows"), "0"), 0)
    priority_lsms_manual_packet_reports = safe_int(next((row.get("value", "0") for row in priority_lsms_manual_packet_summary if row.get("metric") == "manual_download_packet_reports_written"), "0"), 0)
    priority_lsms_manual_packet_data_write = next((row.get("value", "") for row in priority_lsms_manual_packet_summary if row.get("metric") == "data_write_gate_status"), "")
    priority_lsms_manual_packet_modeling = next((row.get("value", "") for row in priority_lsms_manual_packet_summary if row.get("metric") == "modeling_gate_status"), "")
    priority_lsms_manual_packet_report_files = len(list((REPORT_DIR / "priority_lsms_isa_manual_download_packets").glob("*.md"))) if (REPORT_DIR / "priority_lsms_isa_manual_download_packets").exists() else 0
    priority_lsms_manual_packet_gate_ok = (
        counts["priority_lsms_isa_manual_download_packet_summary"] > 0
        and counts["priority_lsms_isa_manual_download_packet_index"] == priority_lsms_manual_packet_rows
        and counts["priority_lsms_isa_manual_download_packet_core_files"] == priority_lsms_manual_packet_core_rows
        and file_ok(REPORT_DIR / "priority_lsms_isa_manual_download_packets.md")
        and priority_lsms_manual_packet_rows == priority_lsms_threshold_gap_minimum_remaining
        and priority_lsms_manual_packet_priority_rows == 9
        and priority_lsms_manual_packet_sixth_rows == 1
        and priority_lsms_manual_packet_missing_full == 838
        and priority_lsms_manual_packet_core_rows == priority_lsms_threshold_gap_missing_core
        and priority_lsms_manual_packet_missing_core == priority_lsms_threshold_gap_missing_core
        and priority_lsms_manual_packet_reports == priority_lsms_manual_packet_rows
        and priority_lsms_manual_packet_report_files == priority_lsms_manual_packet_rows
        and priority_lsms_manual_packet_data_write == "blocked_no_data_write"
        and priority_lsms_manual_packet_modeling == "blocked"
    )
    add(
        rows,
        "dataset_promotion",
        "Priority LSMS/ISA manual download packets give each remaining minimum-batch raw package a per-wave acquisition checklist",
        status(priority_lsms_manual_packet_gate_ok),
        f"index_rows={counts['priority_lsms_isa_manual_download_packet_index']}; core_rows={counts['priority_lsms_isa_manual_download_packet_core_files']}; summary_rows={counts['priority_lsms_isa_manual_download_packet_summary']}; packets={priority_lsms_manual_packet_rows}; priority_packets={priority_lsms_manual_packet_priority_rows}; sixth_country_packets={priority_lsms_manual_packet_sixth_rows}; missing_full={priority_lsms_manual_packet_missing_full}; missing_core={priority_lsms_manual_packet_missing_core}; reports={priority_lsms_manual_packet_reports}; report_files={priority_lsms_manual_packet_report_files}; data_write={priority_lsms_manual_packet_data_write}; modeling_gate={priority_lsms_manual_packet_modeling}",
        "" if priority_lsms_manual_packet_gate_ok else "Run script/176_build_priority_lsms_isa_manual_download_packets.py after the threshold gap control panel is current.",
    )
    priority_lsms_manual_progress_summary = read_csv_dicts(RESULT_DIR / "priority_lsms_isa_manual_download_progress_summary.csv")
    priority_lsms_manual_progress_packets = safe_int(next((row.get("value", "0") for row in priority_lsms_manual_progress_summary if row.get("metric") == "manual_download_progress_packet_rows"), "0"), 0)
    priority_lsms_manual_progress_target_files = safe_int(next((row.get("value", "0") for row in priority_lsms_manual_progress_summary if row.get("metric") == "manual_download_progress_target_file_rows"), "0"), 0)
    priority_lsms_manual_progress_incoming_routes = safe_int(next((row.get("value", "0") for row in priority_lsms_manual_progress_summary if row.get("metric") == "manual_download_progress_incoming_route_rows"), "0"), 0)
    priority_lsms_manual_progress_validation_ready = safe_int(next((row.get("value", "0") for row in priority_lsms_manual_progress_summary if row.get("metric") == "manual_download_progress_validation_ready_packets"), "0"), 0)
    priority_lsms_manual_progress_blocked_no_files = safe_int(next((row.get("value", "0") for row in priority_lsms_manual_progress_summary if row.get("metric") == "manual_download_progress_blocked_no_file_packets"), "0"), 0)
    priority_lsms_manual_progress_data_write = next((row.get("value", "") for row in priority_lsms_manual_progress_summary if row.get("metric") == "data_write_gate_status"), "")
    priority_lsms_manual_progress_modeling = next((row.get("value", "") for row in priority_lsms_manual_progress_summary if row.get("metric") == "modeling_gate_status"), "")
    priority_lsms_manual_progress_gate_ok = (
        counts["priority_lsms_isa_manual_download_progress_summary"] > 0
        and counts["priority_lsms_isa_manual_download_progress_tracker"] == priority_lsms_manual_progress_packets
        and file_ok(REPORT_DIR / "priority_lsms_isa_manual_download_progress_tracker.md")
        and priority_lsms_manual_progress_packets == priority_lsms_manual_packet_rows
        and priority_lsms_manual_progress_target_files == 0
        and priority_lsms_manual_progress_incoming_routes == 0
        and priority_lsms_manual_progress_validation_ready == 0
        and priority_lsms_manual_progress_blocked_no_files == priority_lsms_manual_packet_rows
        and priority_lsms_manual_progress_data_write == "blocked_no_data_write"
        and priority_lsms_manual_progress_modeling == "blocked"
    )
    add(
        rows,
        "dataset_promotion",
        "Priority LSMS/ISA manual download progress tracker links packet target folders to validation readiness",
        status(priority_lsms_manual_progress_gate_ok),
        f"tracker_rows={counts['priority_lsms_isa_manual_download_progress_tracker']}; summary_rows={counts['priority_lsms_isa_manual_download_progress_summary']}; packets={priority_lsms_manual_progress_packets}; target_files={priority_lsms_manual_progress_target_files}; incoming_routes={priority_lsms_manual_progress_incoming_routes}; validation_ready={priority_lsms_manual_progress_validation_ready}; blocked_no_files={priority_lsms_manual_progress_blocked_no_files}; data_write={priority_lsms_manual_progress_data_write}; modeling_gate={priority_lsms_manual_progress_modeling}",
        "" if priority_lsms_manual_progress_gate_ok else "Run script/177_build_priority_lsms_isa_manual_download_progress_tracker.py after manual download packets and incoming router are current.",
    )
    priority_lsms_post_download_validation_summary = read_csv_dicts(RESULT_DIR / "priority_lsms_isa_post_download_validation_runner_summary.csv")
    priority_lsms_post_download_validation_mode = next((row.get("value", "") for row in priority_lsms_post_download_validation_summary if row.get("metric") == "post_download_validation_runner_mode"), "")
    priority_lsms_post_download_validation_progress_packets = safe_int(next((row.get("value", "0") for row in priority_lsms_post_download_validation_summary if row.get("metric") == "post_download_validation_progress_packet_rows"), "0"), 0)
    priority_lsms_post_download_validation_ready_packets = safe_int(next((row.get("value", "0") for row in priority_lsms_post_download_validation_summary if row.get("metric") == "post_download_validation_ready_packet_rows"), "0"), 0)
    priority_lsms_post_download_validation_plan_rows = safe_int(next((row.get("value", "0") for row in priority_lsms_post_download_validation_summary if row.get("metric") == "post_download_validation_plan_rows"), "0"), 0)
    priority_lsms_post_download_validation_execute_commands = safe_int(next((row.get("value", "0") for row in priority_lsms_post_download_validation_summary if row.get("metric") == "post_download_validation_execute_command_rows"), "0"), 0)
    priority_lsms_post_download_validation_attempted = safe_int(next((row.get("value", "0") for row in priority_lsms_post_download_validation_summary if row.get("metric") == "post_download_validation_attempted_command_rows"), "0"), 0)
    priority_lsms_post_download_validation_failed = safe_int(next((row.get("value", "0") for row in priority_lsms_post_download_validation_summary if row.get("metric") == "post_download_validation_failed_command_rows"), "0"), 0)
    priority_lsms_post_download_validation_data_write = next((row.get("value", "") for row in priority_lsms_post_download_validation_summary if row.get("metric") == "data_write_gate_status"), "")
    priority_lsms_post_download_validation_modeling = next((row.get("value", "") for row in priority_lsms_post_download_validation_summary if row.get("metric") == "modeling_gate_status"), "")
    priority_lsms_post_download_validation_gate_ok = (
        counts["priority_lsms_isa_post_download_validation_runner_summary"] > 0
        and counts["priority_lsms_isa_post_download_validation_run_plan"] == priority_lsms_post_download_validation_plan_rows
        and counts["priority_lsms_isa_post_download_validation_command_log"] == priority_lsms_post_download_validation_plan_rows
        and file_ok(REPORT_DIR / "priority_lsms_isa_post_download_validation_runner.md")
        and priority_lsms_post_download_validation_mode == "dry_run"
        and priority_lsms_post_download_validation_progress_packets == priority_lsms_manual_progress_packets
        and priority_lsms_post_download_validation_ready_packets == priority_lsms_manual_progress_validation_ready
        and priority_lsms_post_download_validation_plan_rows == priority_lsms_manual_progress_packets * 5
        and priority_lsms_post_download_validation_execute_commands == 0
        and priority_lsms_post_download_validation_attempted == 0
        and priority_lsms_post_download_validation_failed == 0
        and priority_lsms_post_download_validation_data_write == "blocked_no_data_write"
        and priority_lsms_post_download_validation_modeling == "blocked"
    )
    add(
        rows,
        "dataset_promotion",
        "Priority LSMS/ISA post-download validation runner builds a dry-run plan and only executes allowlisted validation commands with explicit flag",
        status(priority_lsms_post_download_validation_gate_ok),
        f"plan_rows={counts['priority_lsms_isa_post_download_validation_run_plan']}; command_log_rows={counts['priority_lsms_isa_post_download_validation_command_log']}; summary_rows={counts['priority_lsms_isa_post_download_validation_runner_summary']}; mode={priority_lsms_post_download_validation_mode}; progress_packets={priority_lsms_post_download_validation_progress_packets}; ready_packets={priority_lsms_post_download_validation_ready_packets}; execute_commands={priority_lsms_post_download_validation_execute_commands}; attempted={priority_lsms_post_download_validation_attempted}; failed={priority_lsms_post_download_validation_failed}; data_write={priority_lsms_post_download_validation_data_write}; modeling_gate={priority_lsms_post_download_validation_modeling}",
        "" if priority_lsms_post_download_validation_gate_ok else "Run script/178_build_priority_lsms_isa_post_download_validation_runner.py in dry-run mode after the manual progress tracker is current.",
    )
    priority_lsms_manual_execution_summary = read_csv_dicts(RESULT_DIR / "priority_lsms_isa_manual_download_execution_board_summary.csv")
    priority_lsms_manual_execution_rows = safe_int(next((row.get("value", "0") for row in priority_lsms_manual_execution_summary if row.get("metric") == "manual_download_execution_board_rows"), "0"), 0)
    priority_lsms_manual_execution_priority_rows = safe_int(next((row.get("value", "0") for row in priority_lsms_manual_execution_summary if row.get("metric") == "manual_download_execution_board_priority_country_rows"), "0"), 0)
    priority_lsms_manual_execution_sixth_rows = safe_int(next((row.get("value", "0") for row in priority_lsms_manual_execution_summary if row.get("metric") == "manual_download_execution_board_sixth_country_rows"), "0"), 0)
    priority_lsms_manual_execution_target_files = safe_int(next((row.get("value", "0") for row in priority_lsms_manual_execution_summary if row.get("metric") == "manual_download_execution_board_target_file_rows"), "0"), 0)
    priority_lsms_manual_execution_incoming_routes = safe_int(next((row.get("value", "0") for row in priority_lsms_manual_execution_summary if row.get("metric") == "manual_download_execution_board_incoming_route_rows"), "0"), 0)
    priority_lsms_manual_execution_validation_ready = safe_int(next((row.get("value", "0") for row in priority_lsms_manual_execution_summary if row.get("metric") == "manual_download_execution_board_validation_ready_rows"), "0"), 0)
    priority_lsms_manual_execution_missing_full = safe_int(next((row.get("value", "0") for row in priority_lsms_manual_execution_summary if row.get("metric") == "manual_download_execution_board_missing_full_file_rows"), "0"), 0)
    priority_lsms_manual_execution_missing_core = safe_int(next((row.get("value", "0") for row in priority_lsms_manual_execution_summary if row.get("metric") == "manual_download_execution_board_missing_core_file_rows"), "0"), 0)
    priority_lsms_manual_execution_official_urls = safe_int(next((row.get("value", "0") for row in priority_lsms_manual_execution_summary if row.get("metric") == "manual_download_execution_board_official_url_rows"), "0"), 0)
    priority_lsms_manual_execution_countries_if_passes = safe_int(next((row.get("value", "0") for row in priority_lsms_manual_execution_summary if row.get("metric") == "countries_if_board_passes"), "0"), 0)
    priority_lsms_manual_execution_waves_if_passes = safe_int(next((row.get("value", "0") for row in priority_lsms_manual_execution_summary if row.get("metric") == "country_waves_if_board_passes"), "0"), 0)
    priority_lsms_manual_execution_data_write = next((row.get("value", "") for row in priority_lsms_manual_execution_summary if row.get("metric") == "data_write_gate_status"), "")
    priority_lsms_manual_execution_modeling = next((row.get("value", "") for row in priority_lsms_manual_execution_summary if row.get("metric") == "modeling_gate_status"), "")
    priority_lsms_manual_execution_gate_ok = (
        counts["priority_lsms_isa_manual_download_execution_board_summary"] > 0
        and counts["priority_lsms_isa_manual_download_execution_board"] == priority_lsms_manual_execution_rows
        and file_ok(REPORT_DIR / "priority_lsms_isa_manual_download_execution_board.md")
        and priority_lsms_manual_execution_rows == priority_lsms_manual_progress_packets
        and priority_lsms_manual_execution_priority_rows == 9
        and priority_lsms_manual_execution_sixth_rows == 1
        and priority_lsms_manual_execution_target_files == priority_lsms_manual_progress_target_files
        and priority_lsms_manual_execution_incoming_routes == priority_lsms_manual_progress_incoming_routes
        and priority_lsms_manual_execution_validation_ready == priority_lsms_manual_progress_validation_ready
        and priority_lsms_manual_execution_missing_full == priority_lsms_manual_packet_missing_full
        and priority_lsms_manual_execution_missing_core == priority_lsms_manual_packet_missing_core
        and priority_lsms_manual_execution_official_urls == priority_lsms_manual_execution_rows
        and priority_lsms_manual_execution_countries_if_passes == priority_lsms_threshold_gap_countries_if_pass
        and priority_lsms_manual_execution_waves_if_passes == priority_lsms_threshold_gap_waves_if_pass
        and priority_lsms_manual_execution_data_write == "blocked_no_data_write"
        and priority_lsms_manual_execution_modeling == "blocked"
    )
    add(
        rows,
        "dataset_promotion",
        "Priority LSMS/ISA manual download execution board gives one table of official URLs, target folders, missing-file counts, and validation commands",
        status(priority_lsms_manual_execution_gate_ok),
        f"board_rows={counts['priority_lsms_isa_manual_download_execution_board']}; summary_rows={counts['priority_lsms_isa_manual_download_execution_board_summary']}; priority_rows={priority_lsms_manual_execution_priority_rows}; sixth_country_rows={priority_lsms_manual_execution_sixth_rows}; target_files={priority_lsms_manual_execution_target_files}; incoming_routes={priority_lsms_manual_execution_incoming_routes}; validation_ready={priority_lsms_manual_execution_validation_ready}; missing_full={priority_lsms_manual_execution_missing_full}; missing_core={priority_lsms_manual_execution_missing_core}; official_urls={priority_lsms_manual_execution_official_urls}; countries_if_passes={priority_lsms_manual_execution_countries_if_passes}; waves_if_passes={priority_lsms_manual_execution_waves_if_passes}; data_write={priority_lsms_manual_execution_data_write}; modeling_gate={priority_lsms_manual_execution_modeling}",
        "" if priority_lsms_manual_execution_gate_ok else "Run script/179_build_priority_lsms_isa_manual_download_execution_board.py after progress and post-download validation runner outputs are current.",
    )
    priority_lsms_credentialed_handoff_summary = read_csv_dicts(RESULT_DIR / "priority_lsms_isa_credentialed_download_handoff_summary.csv")
    priority_lsms_credentialed_handoff_mode = next((row.get("value", "") for row in priority_lsms_credentialed_handoff_summary if row.get("metric") == "credentialed_download_handoff_mode"), "")
    priority_lsms_credentialed_handoff_rows = safe_int(next((row.get("value", "0") for row in priority_lsms_credentialed_handoff_summary if row.get("metric") == "credentialed_download_handoff_rows"), "0"), 0)
    priority_lsms_credentialed_handoff_cookie = safe_int(next((row.get("value", "0") for row in priority_lsms_credentialed_handoff_summary if row.get("metric") == "credentialed_download_handoff_cookie_file_present"), "0"), 0)
    priority_lsms_credentialed_handoff_header = safe_int(next((row.get("value", "0") for row in priority_lsms_credentialed_handoff_summary if row.get("metric") == "credentialed_download_handoff_header_file_present"), "0"), 0)
    priority_lsms_credentialed_handoff_attempted = safe_int(next((row.get("value", "0") for row in priority_lsms_credentialed_handoff_summary if row.get("metric") == "credentialed_download_handoff_request_attempted_rows"), "0"), 0)
    priority_lsms_credentialed_handoff_raw_payload = safe_int(next((row.get("value", "0") for row in priority_lsms_credentialed_handoff_summary if row.get("metric") == "credentialed_download_handoff_raw_payload_detected_rows"), "0"), 0)
    priority_lsms_credentialed_handoff_saved = safe_int(next((row.get("value", "0") for row in priority_lsms_credentialed_handoff_summary if row.get("metric") == "credentialed_download_handoff_saved_raw_file_rows"), "0"), 0)
    priority_lsms_credentialed_handoff_missing_session = safe_int(next((row.get("value", "0") for row in priority_lsms_credentialed_handoff_summary if row.get("metric") == "credentialed_download_handoff_missing_session_rows"), "0"), 0)
    priority_lsms_credentialed_handoff_data_write = next((row.get("value", "") for row in priority_lsms_credentialed_handoff_summary if row.get("metric") == "data_write_gate_status"), "")
    priority_lsms_credentialed_handoff_modeling = next((row.get("value", "") for row in priority_lsms_credentialed_handoff_summary if row.get("metric") == "modeling_gate_status"), "")
    priority_lsms_credentialed_handoff_gate_ok = (
        counts["priority_lsms_isa_credentialed_download_handoff_summary"] > 0
        and counts["priority_lsms_isa_credentialed_download_handoff_plan"] == priority_lsms_credentialed_handoff_rows
        and counts["priority_lsms_isa_credentialed_download_handoff_log"] == priority_lsms_credentialed_handoff_rows
        and file_ok(REPORT_DIR / "priority_lsms_isa_credentialed_download_handoff.md")
        and priority_lsms_credentialed_handoff_mode == "dry_run"
        and priority_lsms_credentialed_handoff_rows == priority_lsms_manual_execution_rows
        and priority_lsms_credentialed_handoff_cookie == 0
        and priority_lsms_credentialed_handoff_header == 0
        and priority_lsms_credentialed_handoff_attempted == 0
        and priority_lsms_credentialed_handoff_raw_payload == 0
        and priority_lsms_credentialed_handoff_saved == 0
        and priority_lsms_credentialed_handoff_missing_session == priority_lsms_manual_execution_rows
        and priority_lsms_credentialed_handoff_data_write == "blocked_no_data_write"
        and priority_lsms_credentialed_handoff_modeling == "blocked"
    )
    add(
        rows,
        "dataset_promotion",
        "Priority LSMS/ISA credentialed download handoff is fail-closed until a local World Bank session is provided",
        status(priority_lsms_credentialed_handoff_gate_ok),
        f"plan_rows={counts['priority_lsms_isa_credentialed_download_handoff_plan']}; log_rows={counts['priority_lsms_isa_credentialed_download_handoff_log']}; summary_rows={counts['priority_lsms_isa_credentialed_download_handoff_summary']}; mode={priority_lsms_credentialed_handoff_mode}; rows={priority_lsms_credentialed_handoff_rows}; cookie_file={priority_lsms_credentialed_handoff_cookie}; header_file={priority_lsms_credentialed_handoff_header}; attempted={priority_lsms_credentialed_handoff_attempted}; raw_payload={priority_lsms_credentialed_handoff_raw_payload}; saved={priority_lsms_credentialed_handoff_saved}; missing_session={priority_lsms_credentialed_handoff_missing_session}; data_write={priority_lsms_credentialed_handoff_data_write}; modeling_gate={priority_lsms_credentialed_handoff_modeling}",
        "" if priority_lsms_credentialed_handoff_gate_ok else "Run script/180_build_priority_lsms_isa_credentialed_download_handoff.py in dry-run mode unless a local session is intentionally provided for --probe or --execute.",
    )
    priority_lsms_resource_route_summary = read_csv_dicts(RESULT_DIR / "priority_lsms_isa_resource_download_route_probe_summary.csv")
    priority_lsms_resource_route_datasets = safe_int(next((row.get("value", "0") for row in priority_lsms_resource_route_summary if row.get("metric") == "resource_download_route_probe_datasets"), "0"), 0)
    priority_lsms_resource_route_files = safe_int(next((row.get("value", "0") for row in priority_lsms_resource_route_summary if row.get("metric") == "resource_download_route_probe_sampled_files"), "0"), 0)
    priority_lsms_resource_route_routes = safe_int(next((row.get("value", "0") for row in priority_lsms_resource_route_summary if row.get("metric") == "resource_download_route_probe_route_rows"), "0"), 0)
    priority_lsms_resource_route_attempted = safe_int(next((row.get("value", "0") for row in priority_lsms_resource_route_summary if row.get("metric") == "resource_download_route_probe_request_attempted_rows"), "0"), 0)
    priority_lsms_resource_route_raw = safe_int(next((row.get("value", "0") for row in priority_lsms_resource_route_summary if row.get("metric") == "resource_download_route_probe_raw_payload_candidate_rows"), "0"), 0)
    priority_lsms_resource_route_access = safe_int(next((row.get("value", "0") for row in priority_lsms_resource_route_summary if row.get("metric") == "resource_download_route_probe_access_gate_rows"), "0"), 0)
    priority_lsms_resource_route_dictionary = safe_int(next((row.get("value", "0") for row in priority_lsms_resource_route_summary if row.get("metric") == "resource_download_route_probe_data_dictionary_html_rows"), "0"), 0)
    priority_lsms_resource_route_http_error = safe_int(next((row.get("value", "0") for row in priority_lsms_resource_route_summary if row.get("metric") == "resource_download_route_probe_http_error_rows"), "0"), 0)
    priority_lsms_resource_route_failed = safe_int(next((row.get("value", "0") for row in priority_lsms_resource_route_summary if row.get("metric") == "resource_download_route_probe_request_failed_rows"), "0"), 0)
    priority_lsms_resource_route_data_write = next((row.get("value", "") for row in priority_lsms_resource_route_summary if row.get("metric") == "data_write_gate_status"), "")
    priority_lsms_resource_route_modeling = next((row.get("value", "") for row in priority_lsms_resource_route_summary if row.get("metric") == "modeling_gate_status"), "")
    priority_lsms_resource_route_gate_ok = (
        counts["priority_lsms_isa_resource_download_route_probe_summary"] > 0
        and counts["priority_lsms_isa_resource_download_route_probe"] == priority_lsms_resource_route_routes
        and file_ok(REPORT_DIR / "priority_lsms_isa_resource_download_route_probe.md")
        and priority_lsms_resource_route_datasets == priority_lsms_manual_execution_rows
        and priority_lsms_resource_route_files >= priority_lsms_resource_route_datasets
        and priority_lsms_resource_route_routes > 0
        and priority_lsms_resource_route_attempted == priority_lsms_resource_route_routes
        and priority_lsms_resource_route_raw == 0
        and priority_lsms_resource_route_failed == 0
        and priority_lsms_resource_route_access >= 0
        and priority_lsms_resource_route_dictionary >= 0
        and priority_lsms_resource_route_http_error >= 0
        and priority_lsms_resource_route_data_write == "blocked_no_data_write"
        and priority_lsms_resource_route_modeling == "blocked"
    )
    add(
        rows,
        "dataset_promotion",
        "Priority LSMS/ISA resource route probe checks public file-id routes without saving raw payloads",
        status(priority_lsms_resource_route_gate_ok),
        f"route_rows={counts['priority_lsms_isa_resource_download_route_probe']}; summary_rows={counts['priority_lsms_isa_resource_download_route_probe_summary']}; datasets={priority_lsms_resource_route_datasets}; sampled_files={priority_lsms_resource_route_files}; attempted={priority_lsms_resource_route_attempted}; raw_payload={priority_lsms_resource_route_raw}; access_gate={priority_lsms_resource_route_access}; data_dictionary_html={priority_lsms_resource_route_dictionary}; http_error={priority_lsms_resource_route_http_error}; request_failed={priority_lsms_resource_route_failed}; data_write={priority_lsms_resource_route_data_write}; modeling_gate={priority_lsms_resource_route_modeling}",
        "" if priority_lsms_resource_route_gate_ok else "Run script/181_probe_priority_lsms_isa_resource_download_routes.py after the manual download execution board is current and network is available.",
    )
    priority_lsms_download_acceptance_summary = read_csv_dicts(RESULT_DIR / "priority_lsms_isa_download_acceptance_matrix_summary.csv")
    priority_lsms_download_acceptance_datasets = safe_int(next((row.get("value", "0") for row in priority_lsms_download_acceptance_summary if row.get("metric") == "download_acceptance_dataset_rows"), "0"), 0)
    priority_lsms_download_acceptance_expected_files = safe_int(next((row.get("value", "0") for row in priority_lsms_download_acceptance_summary if row.get("metric") == "download_acceptance_expected_file_rows"), "0"), 0)
    priority_lsms_download_acceptance_requirement_rows = safe_int(next((row.get("value", "0") for row in priority_lsms_download_acceptance_summary if row.get("metric") == "download_acceptance_core_requirement_rows"), "0"), 0)
    priority_lsms_download_acceptance_core_files = safe_int(next((row.get("value", "0") for row in priority_lsms_download_acceptance_summary if row.get("metric") == "download_acceptance_core_file_rows"), "0"), 0)
    priority_lsms_download_acceptance_missing_files = safe_int(next((row.get("value", "0") for row in priority_lsms_download_acceptance_summary if row.get("metric") == "download_acceptance_missing_expected_file_rows"), "0"), 0)
    priority_lsms_download_acceptance_present_files = safe_int(next((row.get("value", "0") for row in priority_lsms_download_acceptance_summary if row.get("metric") == "download_acceptance_present_file_rows"), "0"), 0)
    priority_lsms_download_acceptance_blocked_reqs = safe_int(next((row.get("value", "0") for row in priority_lsms_download_acceptance_summary if row.get("metric") == "download_acceptance_missing_core_requirement_rows"), "0"), 0)
    priority_lsms_download_acceptance_ready_reqs = safe_int(next((row.get("value", "0") for row in priority_lsms_download_acceptance_summary if row.get("metric") == "download_acceptance_ready_requirement_rows"), "0"), 0)
    priority_lsms_download_acceptance_urls = safe_int(next((row.get("value", "0") for row in priority_lsms_download_acceptance_summary if row.get("metric") == "download_acceptance_official_url_rows"), "0"), 0)
    priority_lsms_download_acceptance_route_raw = safe_int(next((row.get("value", "0") for row in priority_lsms_download_acceptance_summary if row.get("metric") == "download_acceptance_resource_route_raw_payload_rows"), "0"), 0)
    priority_lsms_download_acceptance_route_failed = safe_int(next((row.get("value", "0") for row in priority_lsms_download_acceptance_summary if row.get("metric") == "download_acceptance_resource_route_request_failed_rows"), "0"), 0)
    priority_lsms_download_acceptance_data_write = next((row.get("value", "") for row in priority_lsms_download_acceptance_summary if row.get("metric") == "data_write_gate_status"), "")
    priority_lsms_download_acceptance_modeling = next((row.get("value", "") for row in priority_lsms_download_acceptance_summary if row.get("metric") == "modeling_gate_status"), "")
    priority_lsms_download_acceptance_gate_ok = (
        counts["priority_lsms_isa_download_acceptance_matrix_summary"] > 0
        and counts["priority_lsms_isa_download_acceptance_file_matrix"] == priority_lsms_download_acceptance_expected_files
        and counts["priority_lsms_isa_download_acceptance_requirement_matrix"] == priority_lsms_download_acceptance_requirement_rows
        and file_ok(REPORT_DIR / "priority_lsms_isa_download_acceptance_matrix.md")
        and priority_lsms_download_acceptance_datasets == priority_lsms_manual_execution_rows
        and priority_lsms_download_acceptance_expected_files == priority_lsms_manual_execution_missing_full
        and priority_lsms_download_acceptance_core_files == priority_lsms_manual_execution_missing_core
        and priority_lsms_download_acceptance_missing_files == priority_lsms_manual_execution_missing_full
        and priority_lsms_download_acceptance_present_files == 0
        and priority_lsms_download_acceptance_blocked_reqs == priority_lsms_download_acceptance_requirement_rows
        and priority_lsms_download_acceptance_ready_reqs == 0
        and priority_lsms_download_acceptance_urls == priority_lsms_manual_execution_rows
        and priority_lsms_download_acceptance_route_raw == priority_lsms_resource_route_raw
        and priority_lsms_download_acceptance_route_failed == priority_lsms_resource_route_failed
        and priority_lsms_download_acceptance_data_write == "blocked_no_data_write"
        and priority_lsms_download_acceptance_modeling == "blocked"
    )
    add(
        rows,
        "dataset_promotion",
        "Priority LSMS/ISA download acceptance matrix maps expected official files to requirement-level receipt gates",
        status(priority_lsms_download_acceptance_gate_ok),
        f"file_rows={counts['priority_lsms_isa_download_acceptance_file_matrix']}; requirement_rows={counts['priority_lsms_isa_download_acceptance_requirement_matrix']}; summary_rows={counts['priority_lsms_isa_download_acceptance_matrix_summary']}; datasets={priority_lsms_download_acceptance_datasets}; expected_files={priority_lsms_download_acceptance_expected_files}; core_files={priority_lsms_download_acceptance_core_files}; missing_files={priority_lsms_download_acceptance_missing_files}; present_files={priority_lsms_download_acceptance_present_files}; blocked_requirements={priority_lsms_download_acceptance_blocked_reqs}; ready_requirements={priority_lsms_download_acceptance_ready_reqs}; official_urls={priority_lsms_download_acceptance_urls}; route_raw={priority_lsms_download_acceptance_route_raw}; route_failed={priority_lsms_download_acceptance_route_failed}; data_write={priority_lsms_download_acceptance_data_write}; modeling_gate={priority_lsms_download_acceptance_modeling}",
        "" if priority_lsms_download_acceptance_gate_ok else "Run script/182_build_priority_lsms_isa_download_acceptance_matrix.py after the manual board, official file receipt validator, and resource route probe are current.",
    )
    priority_lsms_local_target_readme_summary = read_csv_dicts(RESULT_DIR / "priority_lsms_isa_local_target_readme_summary.csv")
    priority_lsms_local_target_readmes = safe_int(next((row.get("value", "0") for row in priority_lsms_local_target_readme_summary if row.get("metric") == "local_target_readme_rows"), "0"), 0)
    priority_lsms_local_target_expected_files = safe_int(next((row.get("value", "0") for row in priority_lsms_local_target_readme_summary if row.get("metric") == "local_target_readme_expected_file_rows"), "0"), 0)
    priority_lsms_local_target_missing_files = safe_int(next((row.get("value", "0") for row in priority_lsms_local_target_readme_summary if row.get("metric") == "local_target_readme_missing_expected_file_rows"), "0"), 0)
    priority_lsms_local_target_requirements = safe_int(next((row.get("value", "0") for row in priority_lsms_local_target_readme_summary if row.get("metric") == "local_target_readme_requirement_rows"), "0"), 0)
    priority_lsms_local_target_blocked_reqs = safe_int(next((row.get("value", "0") for row in priority_lsms_local_target_readme_summary if row.get("metric") == "local_target_readme_blocked_requirement_rows"), "0"), 0)
    priority_lsms_local_target_ready_reqs = safe_int(next((row.get("value", "0") for row in priority_lsms_local_target_readme_summary if row.get("metric") == "local_target_readme_ready_requirement_rows"), "0"), 0)
    priority_lsms_local_target_data_write = next((row.get("value", "") for row in priority_lsms_local_target_readme_summary if row.get("metric") == "data_write_gate_status"), "")
    priority_lsms_local_target_modeling = next((row.get("value", "") for row in priority_lsms_local_target_readme_summary if row.get("metric") == "modeling_gate_status"), "")
    priority_lsms_local_target_gate_ok = (
        counts["priority_lsms_isa_local_target_readme_summary"] > 0
        and counts["priority_lsms_isa_local_target_readme_manifest"] == priority_lsms_local_target_readmes
        and file_ok(REPORT_DIR / "priority_lsms_isa_local_target_readmes.md")
        and priority_lsms_local_target_readmes == priority_lsms_manual_execution_rows
        and priority_lsms_local_target_expected_files == priority_lsms_download_acceptance_expected_files
        and priority_lsms_local_target_missing_files == priority_lsms_download_acceptance_missing_files
        and priority_lsms_local_target_requirements == priority_lsms_download_acceptance_requirement_rows
        and priority_lsms_local_target_blocked_reqs == priority_lsms_download_acceptance_blocked_reqs
        and priority_lsms_local_target_ready_reqs == priority_lsms_download_acceptance_ready_reqs
        and priority_lsms_local_target_data_write == "blocked_no_data_write"
        and priority_lsms_local_target_modeling == "blocked"
    )
    add(
        rows,
        "dataset_promotion",
        "Priority LSMS/ISA local target readmes place acceptance instructions into ignored raw target folders",
        status(priority_lsms_local_target_gate_ok),
        f"manifest_rows={counts['priority_lsms_isa_local_target_readme_manifest']}; summary_rows={counts['priority_lsms_isa_local_target_readme_summary']}; readmes={priority_lsms_local_target_readmes}; expected_files={priority_lsms_local_target_expected_files}; missing_files={priority_lsms_local_target_missing_files}; requirements={priority_lsms_local_target_requirements}; blocked_requirements={priority_lsms_local_target_blocked_reqs}; ready_requirements={priority_lsms_local_target_ready_reqs}; data_write={priority_lsms_local_target_data_write}; modeling_gate={priority_lsms_local_target_modeling}",
        "" if priority_lsms_local_target_gate_ok else "Run script/183_build_priority_lsms_isa_local_target_readmes.py after the download acceptance matrix is current.",
    )
    priority_lsms_minimum_raw_value_summary = read_csv_dicts(RESULT_DIR / "priority_lsms_isa_minimum_batch_raw_value_queue_summary.csv")
    priority_lsms_minimum_raw_value_datasets = safe_int(next((row.get("value", "0") for row in priority_lsms_minimum_raw_value_summary if row.get("metric") == "minimum_batch_raw_value_queue_dataset_rows"), "0"), 0)
    priority_lsms_minimum_raw_value_requirements = safe_int(next((row.get("value", "0") for row in priority_lsms_minimum_raw_value_summary if row.get("metric") == "minimum_batch_raw_value_queue_requirement_rows"), "0"), 0)
    priority_lsms_minimum_raw_value_variables = safe_int(next((row.get("value", "0") for row in priority_lsms_minimum_raw_value_summary if row.get("metric") == "minimum_batch_raw_value_queue_variable_rows"), "0"), 0)
    priority_lsms_minimum_raw_value_files = safe_int(next((row.get("value", "0") for row in priority_lsms_minimum_raw_value_summary if row.get("metric") == "minimum_batch_raw_value_queue_file_rows"), "0"), 0)
    priority_lsms_minimum_raw_value_blocked_reqs = safe_int(next((row.get("value", "0") for row in priority_lsms_minimum_raw_value_summary if row.get("metric") == "minimum_batch_raw_value_queue_blocked_requirement_rows"), "0"), 0)
    priority_lsms_minimum_raw_value_ready_reqs = safe_int(next((row.get("value", "0") for row in priority_lsms_minimum_raw_value_summary if row.get("metric") == "minimum_batch_raw_value_queue_ready_requirement_rows"), "0"), 0)
    priority_lsms_minimum_raw_value_blocked_vars = safe_int(next((row.get("value", "0") for row in priority_lsms_minimum_raw_value_summary if row.get("metric") == "minimum_batch_raw_value_queue_blocked_variable_rows"), "0"), 0)
    priority_lsms_minimum_raw_value_blocked_files = safe_int(next((row.get("value", "0") for row in priority_lsms_minimum_raw_value_summary if row.get("metric") == "minimum_batch_raw_value_queue_blocked_file_rows"), "0"), 0)
    priority_lsms_minimum_raw_value_readmes = safe_int(next((row.get("value", "0") for row in priority_lsms_minimum_raw_value_summary if row.get("metric") == "minimum_batch_raw_value_queue_local_target_readmes"), "0"), 0)
    priority_lsms_minimum_raw_value_data_write = next((row.get("value", "") for row in priority_lsms_minimum_raw_value_summary if row.get("metric") == "data_write_gate_status"), "")
    priority_lsms_minimum_raw_value_modeling = next((row.get("value", "") for row in priority_lsms_minimum_raw_value_summary if row.get("metric") == "modeling_gate_status"), "")
    priority_lsms_minimum_raw_value_gate_ok = (
        counts["priority_lsms_isa_minimum_batch_raw_value_queue_summary"] > 0
        and counts["priority_lsms_isa_minimum_batch_raw_value_requirement_queue"] == priority_lsms_minimum_raw_value_requirements
        and counts["priority_lsms_isa_minimum_batch_raw_value_variable_queue"] == priority_lsms_minimum_raw_value_variables
        and counts["priority_lsms_isa_minimum_batch_raw_value_file_queue"] == priority_lsms_minimum_raw_value_files
        and file_ok(REPORT_DIR / "priority_lsms_isa_minimum_batch_raw_value_queue.md")
        and priority_lsms_minimum_raw_value_datasets == priority_lsms_manual_execution_rows
        and priority_lsms_minimum_raw_value_requirements == priority_lsms_manual_execution_rows * 8
        and priority_lsms_minimum_raw_value_files == priority_lsms_download_acceptance_core_files
        and priority_lsms_minimum_raw_value_blocked_reqs == priority_lsms_minimum_raw_value_requirements
        and priority_lsms_minimum_raw_value_ready_reqs == 0
        and priority_lsms_minimum_raw_value_blocked_vars == priority_lsms_minimum_raw_value_variables
        and priority_lsms_minimum_raw_value_blocked_files == priority_lsms_minimum_raw_value_files
        and priority_lsms_minimum_raw_value_readmes == priority_lsms_local_target_readmes
        and priority_lsms_minimum_raw_value_data_write == "blocked_no_data_write"
        and priority_lsms_minimum_raw_value_modeling == "blocked"
    )
    add(
        rows,
        "dataset_promotion",
        "Priority LSMS/ISA minimum-batch raw-value queue narrows review rows to the 10 manual packets",
        status(priority_lsms_minimum_raw_value_gate_ok),
        f"requirement_rows={counts['priority_lsms_isa_minimum_batch_raw_value_requirement_queue']}; variable_rows={counts['priority_lsms_isa_minimum_batch_raw_value_variable_queue']}; file_rows={counts['priority_lsms_isa_minimum_batch_raw_value_file_queue']}; summary_rows={counts['priority_lsms_isa_minimum_batch_raw_value_queue_summary']}; datasets={priority_lsms_minimum_raw_value_datasets}; blocked_requirements={priority_lsms_minimum_raw_value_blocked_reqs}; ready_requirements={priority_lsms_minimum_raw_value_ready_reqs}; blocked_variables={priority_lsms_minimum_raw_value_blocked_vars}; blocked_files={priority_lsms_minimum_raw_value_blocked_files}; local_readmes={priority_lsms_minimum_raw_value_readmes}; data_write={priority_lsms_minimum_raw_value_data_write}; modeling_gate={priority_lsms_minimum_raw_value_modeling}",
        "" if priority_lsms_minimum_raw_value_gate_ok else "Run script/184_build_priority_lsms_isa_minimum_batch_raw_value_queue.py after local target readmes and raw value workbook outputs are current.",
    )
    priority_lsms_target_smoke_summary = read_csv_dicts(RESULT_DIR / "priority_lsms_isa_target_folder_receipt_smoke_test_summary.csv")
    priority_lsms_target_smoke_datasets = safe_int(next((row.get("value", "0") for row in priority_lsms_target_smoke_summary if row.get("metric") == "priority_lsms_target_smoke_dataset_rows"), "0"), 0)
    priority_lsms_target_smoke_folders = safe_int(next((row.get("value", "0") for row in priority_lsms_target_smoke_summary if row.get("metric") == "priority_lsms_target_smoke_target_folders_present"), "0"), 0)
    priority_lsms_target_smoke_file_rows = safe_int(next((row.get("value", "0") for row in priority_lsms_target_smoke_summary if row.get("metric") == "priority_lsms_target_smoke_file_inventory_rows"), "0"), 0)
    priority_lsms_target_smoke_placeholders = safe_int(next((row.get("value", "0") for row in priority_lsms_target_smoke_summary if row.get("metric") == "priority_lsms_target_smoke_placeholder_instruction_rows"), "0"), 0)
    priority_lsms_target_smoke_raw_files = safe_int(next((row.get("value", "0") for row in priority_lsms_target_smoke_summary if row.get("metric") == "priority_lsms_target_smoke_candidate_raw_file_rows"), "0"), 0)
    priority_lsms_target_smoke_docs = safe_int(next((row.get("value", "0") for row in priority_lsms_target_smoke_summary if row.get("metric") == "priority_lsms_target_smoke_candidate_documentation_file_rows"), "0"), 0)
    priority_lsms_target_smoke_ready = safe_int(next((row.get("value", "0") for row in priority_lsms_target_smoke_summary if row.get("metric") == "priority_lsms_target_smoke_ready_for_receipt_validation_rows"), "0"), 0)
    priority_lsms_target_smoke_blocked_no_raw = safe_int(next((row.get("value", "0") for row in priority_lsms_target_smoke_summary if row.get("metric") == "priority_lsms_target_smoke_blocked_no_candidate_raw_rows"), "0"), 0)
    priority_lsms_target_smoke_docs_only = safe_int(next((row.get("value", "0") for row in priority_lsms_target_smoke_summary if row.get("metric") == "priority_lsms_target_smoke_documentation_only_rows"), "0"), 0)
    priority_lsms_target_smoke_manual = safe_int(next((row.get("value", "0") for row in priority_lsms_target_smoke_summary if row.get("metric") == "priority_lsms_target_smoke_manual_review_rows"), "0"), 0)
    priority_lsms_target_smoke_expected_match = safe_int(next((row.get("value", "0") for row in priority_lsms_target_smoke_summary if row.get("metric") == "priority_lsms_target_smoke_expected_name_match_rows"), "0"), 0)
    priority_lsms_target_smoke_core_match = safe_int(next((row.get("value", "0") for row in priority_lsms_target_smoke_summary if row.get("metric") == "priority_lsms_target_smoke_core_name_match_rows"), "0"), 0)
    priority_lsms_target_smoke_data_write = next((row.get("value", "") for row in priority_lsms_target_smoke_summary if row.get("metric") == "priority_lsms_target_smoke_data_write_status"), "")
    priority_lsms_target_smoke_modeling = next((row.get("value", "") for row in priority_lsms_target_smoke_summary if row.get("metric") == "modeling_gate_status"), "")
    priority_lsms_target_smoke_status_total = (
        priority_lsms_target_smoke_ready
        + priority_lsms_target_smoke_blocked_no_raw
        + priority_lsms_target_smoke_docs_only
        + priority_lsms_target_smoke_manual
    )
    priority_lsms_target_smoke_gate_ok = (
        counts["priority_lsms_isa_target_folder_receipt_smoke_test_summary"] > 0
        and counts["priority_lsms_isa_target_folder_receipt_status"] == priority_lsms_target_smoke_datasets
        and counts["priority_lsms_isa_target_folder_receipt_file_inventory"] == priority_lsms_target_smoke_file_rows
        and file_ok(REPORT_DIR / "priority_lsms_isa_target_folder_receipt_smoke_test.md")
        and priority_lsms_target_smoke_datasets == priority_lsms_manual_execution_rows
        and priority_lsms_target_smoke_folders == priority_lsms_target_smoke_datasets
        and priority_lsms_target_smoke_status_total == priority_lsms_target_smoke_datasets
        and priority_lsms_target_smoke_expected_match <= priority_lsms_target_smoke_datasets
        and priority_lsms_target_smoke_core_match <= priority_lsms_target_smoke_datasets
        and priority_lsms_target_smoke_data_write == "blocked_no_data_write"
        and priority_lsms_target_smoke_modeling == "blocked"
    )
    add(
        rows,
        "dataset_promotion",
        "Priority LSMS/ISA target-folder receipt smoke test separates instructions from candidate raw files before receipt validation",
        status(priority_lsms_target_smoke_gate_ok),
        f"status_rows={counts['priority_lsms_isa_target_folder_receipt_status']}; file_rows={counts['priority_lsms_isa_target_folder_receipt_file_inventory']}; summary_rows={counts['priority_lsms_isa_target_folder_receipt_smoke_test_summary']}; datasets={priority_lsms_target_smoke_datasets}; target_folders={priority_lsms_target_smoke_folders}; placeholders={priority_lsms_target_smoke_placeholders}; candidate_raw_files={priority_lsms_target_smoke_raw_files}; candidate_docs={priority_lsms_target_smoke_docs}; ready_for_receipt={priority_lsms_target_smoke_ready}; blocked_no_candidate_raw={priority_lsms_target_smoke_blocked_no_raw}; docs_only={priority_lsms_target_smoke_docs_only}; manual_review={priority_lsms_target_smoke_manual}; expected_match_rows={priority_lsms_target_smoke_expected_match}; core_match_rows={priority_lsms_target_smoke_core_match}; data_write={priority_lsms_target_smoke_data_write}; modeling_gate={priority_lsms_target_smoke_modeling}",
        "" if priority_lsms_target_smoke_gate_ok else "Run script/185_build_priority_lsms_isa_target_folder_receipt_smoke_test.py after local target readmes and manual target folders are current.",
    )
    priority_lsms_replacement_summary = read_csv_dicts(RESULT_DIR / "priority_lsms_isa_threshold_replacement_plan_summary.csv")
    priority_lsms_replacement_backups = safe_int(next((row.get("value", "0") for row in priority_lsms_replacement_summary if row.get("metric") == "priority_lsms_replacement_backup_candidate_rows"), "0"), 0)
    priority_lsms_replacement_scenarios = safe_int(next((row.get("value", "0") for row in priority_lsms_replacement_summary if row.get("metric") == "priority_lsms_replacement_scenario_rows"), "0"), 0)
    priority_lsms_replacement_strategies = safe_int(next((row.get("value", "0") for row in priority_lsms_replacement_summary if row.get("metric") == "priority_lsms_replacement_strategy_rows"), "0"), 0)
    priority_lsms_replacement_required = safe_int(next((row.get("value", "0") for row in priority_lsms_replacement_summary if row.get("metric") == "priority_lsms_replacement_required_for_threshold_rows"), "0"), 0)
    priority_lsms_replacement_optional = safe_int(next((row.get("value", "0") for row in priority_lsms_replacement_summary if row.get("metric") == "priority_lsms_replacement_optional_buffer_rows"), "0"), 0)
    priority_lsms_replacement_priority_backups = safe_int(next((row.get("value", "0") for row in priority_lsms_replacement_summary if row.get("metric") == "priority_lsms_replacement_priority_country_backup_rows"), "0"), 0)
    priority_lsms_replacement_new_country_backups = safe_int(next((row.get("value", "0") for row in priority_lsms_replacement_summary if row.get("metric") == "priority_lsms_replacement_new_country_backup_rows"), "0"), 0)
    priority_lsms_replacement_strict_countries = safe_int(next((row.get("value", "0") for row in priority_lsms_replacement_summary if row.get("metric") == "priority_lsms_replacement_strict_priority_countries"), "0"), 0)
    priority_lsms_replacement_strict_waves = safe_int(next((row.get("value", "0") for row in priority_lsms_replacement_summary if row.get("metric") == "priority_lsms_replacement_strict_priority_waves"), "0"), 0)
    priority_lsms_replacement_current_countries = safe_int(next((row.get("value", "0") for row in priority_lsms_replacement_summary if row.get("metric") == "priority_lsms_replacement_current_minimum_countries"), "0"), 0)
    priority_lsms_replacement_current_waves = safe_int(next((row.get("value", "0") for row in priority_lsms_replacement_summary if row.get("metric") == "priority_lsms_replacement_current_minimum_waves"), "0"), 0)
    priority_lsms_replacement_data_write = next((row.get("value", "") for row in priority_lsms_replacement_summary if row.get("metric") == "priority_lsms_replacement_data_write_status"), "")
    priority_lsms_replacement_modeling = next((row.get("value", "") for row in priority_lsms_replacement_summary if row.get("metric") == "modeling_gate_status"), "")
    priority_lsms_replacement_gate_ok = (
        counts["priority_lsms_isa_threshold_replacement_plan_summary"] > 0
        and counts["priority_lsms_isa_threshold_replacement_candidate_rank"] == priority_lsms_replacement_backups
        and counts["priority_lsms_isa_threshold_replacement_scenarios"] == priority_lsms_replacement_scenarios
        and counts["priority_lsms_isa_threshold_replacement_strategy"] == priority_lsms_replacement_strategies
        and file_ok(REPORT_DIR / "priority_lsms_isa_threshold_replacement_plan.md")
        and priority_lsms_replacement_scenarios == priority_lsms_manual_execution_rows
        and priority_lsms_replacement_backups == 8
        and priority_lsms_replacement_strategies == 3
        and priority_lsms_replacement_required == 2
        and priority_lsms_replacement_optional == 8
        and priority_lsms_replacement_priority_backups == 6
        and priority_lsms_replacement_new_country_backups == 2
        and priority_lsms_replacement_strict_countries == 5
        and priority_lsms_replacement_strict_waves == 10
        and priority_lsms_replacement_current_countries == 6
        and priority_lsms_replacement_current_waves == 11
        and priority_lsms_replacement_data_write == "blocked_no_data_write"
        and priority_lsms_replacement_modeling == "blocked"
    )
    add(
        rows,
        "dataset_promotion",
        "Priority LSMS/ISA threshold replacement plan preserves 6-country and 10-wave gates when a minimum-batch package fails",
        status(priority_lsms_replacement_gate_ok),
        f"candidate_rows={counts['priority_lsms_isa_threshold_replacement_candidate_rank']}; scenario_rows={counts['priority_lsms_isa_threshold_replacement_scenarios']}; strategy_rows={counts['priority_lsms_isa_threshold_replacement_strategy']}; summary_rows={counts['priority_lsms_isa_threshold_replacement_plan_summary']}; backups={priority_lsms_replacement_backups}; required_replacements={priority_lsms_replacement_required}; optional_buffers={priority_lsms_replacement_optional}; priority_backups={priority_lsms_replacement_priority_backups}; new_country_backups={priority_lsms_replacement_new_country_backups}; strict_priority={priority_lsms_replacement_strict_countries}_countries_{priority_lsms_replacement_strict_waves}_waves; current_minimum={priority_lsms_replacement_current_countries}_countries_{priority_lsms_replacement_current_waves}_waves; data_write={priority_lsms_replacement_data_write}; modeling_gate={priority_lsms_replacement_modeling}",
        "" if priority_lsms_replacement_gate_ok else "Run script/186_build_priority_lsms_isa_threshold_replacement_plan.py after the threshold gap panel, target smoke test, and next raw package action queue are current.",
    )
    priority_lsms_climate_review_summary = read_csv_dicts(RESULT_DIR / "priority_lsms_isa_minimum_batch_climate_linkage_review_summary.csv")
    priority_lsms_climate_review_datasets = safe_int(next((row.get("value", "0") for row in priority_lsms_climate_review_summary if row.get("metric") == "priority_lsms_minimum_climate_review_dataset_rows"), "0"), 0)
    priority_lsms_climate_review_files = safe_int(next((row.get("value", "0") for row in priority_lsms_climate_review_summary if row.get("metric") == "priority_lsms_minimum_climate_review_file_rows"), "0"), 0)
    priority_lsms_climate_review_timing_ready = safe_int(next((row.get("value", "0") for row in priority_lsms_climate_review_summary if row.get("metric") == "priority_lsms_minimum_climate_review_timing_ready_metadata_rows"), "0"), 0)
    priority_lsms_climate_review_geography_ready = safe_int(next((row.get("value", "0") for row in priority_lsms_climate_review_summary if row.get("metric") == "priority_lsms_minimum_climate_review_geography_ready_metadata_rows"), "0"), 0)
    priority_lsms_climate_review_point = safe_int(next((row.get("value", "0") for row in priority_lsms_climate_review_summary if row.get("metric") == "priority_lsms_minimum_climate_review_point_route_rows"), "0"), 0)
    priority_lsms_climate_review_admin = safe_int(next((row.get("value", "0") for row in priority_lsms_climate_review_summary if row.get("metric") == "priority_lsms_minimum_climate_review_admin_route_rows"), "0"), 0)
    priority_lsms_climate_review_manual = safe_int(next((row.get("value", "0") for row in priority_lsms_climate_review_summary if row.get("metric") == "priority_lsms_minimum_climate_review_manual_route_rows"), "0"), 0)
    priority_lsms_climate_review_raw_blocked = safe_int(next((row.get("value", "0") for row in priority_lsms_climate_review_summary if row.get("metric") == "priority_lsms_minimum_climate_review_raw_blocked_rows"), "0"), 0)
    priority_lsms_climate_review_source_ready = safe_int(next((row.get("value", "0") for row in priority_lsms_climate_review_summary if row.get("metric") == "priority_lsms_minimum_climate_review_source_ready_rows"), "0"), 0)
    priority_lsms_climate_review_accepted = safe_int(next((row.get("value", "0") for row in priority_lsms_climate_review_summary if row.get("metric") == "priority_lsms_minimum_climate_review_accepted_route_rows"), "0"), 0)
    priority_lsms_climate_review_data_write = next((row.get("value", "") for row in priority_lsms_climate_review_summary if row.get("metric") == "priority_lsms_minimum_climate_review_data_write_status"), "")
    priority_lsms_climate_review_modeling = next((row.get("value", "") for row in priority_lsms_climate_review_summary if row.get("metric") == "modeling_gate_status"), "")
    priority_lsms_climate_review_gate_ok = (
        counts["priority_lsms_isa_minimum_batch_climate_linkage_review_summary"] > 0
        and counts["priority_lsms_isa_minimum_batch_climate_linkage_review_queue"] == priority_lsms_climate_review_datasets
        and counts["priority_lsms_isa_minimum_batch_climate_linkage_file_queue"] == priority_lsms_climate_review_files
        and file_ok(REPORT_DIR / "priority_lsms_isa_minimum_batch_climate_linkage_review_queue.md")
        and priority_lsms_climate_review_datasets == priority_lsms_manual_execution_rows
        and priority_lsms_climate_review_timing_ready == priority_lsms_climate_review_datasets
        and priority_lsms_climate_review_geography_ready == priority_lsms_climate_review_datasets
        and (priority_lsms_climate_review_point + priority_lsms_climate_review_admin + priority_lsms_climate_review_manual) == priority_lsms_climate_review_datasets
        and priority_lsms_climate_review_raw_blocked <= priority_lsms_climate_review_datasets
        and priority_lsms_climate_review_source_ready == priority_lsms_climate_review_datasets
        and priority_lsms_climate_review_accepted == 0
        and priority_lsms_climate_review_data_write == "blocked_no_data_write"
        and priority_lsms_climate_review_modeling == "blocked"
    )
    add(
        rows,
        "dataset_promotion",
        "Priority LSMS/ISA minimum-batch climate linkage review queue maps the current 10 manual packets to timing/geography raw checks",
        status(priority_lsms_climate_review_gate_ok),
        f"review_rows={counts['priority_lsms_isa_minimum_batch_climate_linkage_review_queue']}; file_rows={counts['priority_lsms_isa_minimum_batch_climate_linkage_file_queue']}; summary_rows={counts['priority_lsms_isa_minimum_batch_climate_linkage_review_summary']}; datasets={priority_lsms_climate_review_datasets}; timing_metadata_ready={priority_lsms_climate_review_timing_ready}; geography_metadata_ready={priority_lsms_climate_review_geography_ready}; point_routes={priority_lsms_climate_review_point}; admin_routes={priority_lsms_climate_review_admin}; manual_routes={priority_lsms_climate_review_manual}; raw_blocked={priority_lsms_climate_review_raw_blocked}; source_ready={priority_lsms_climate_review_source_ready}; accepted_routes={priority_lsms_climate_review_accepted}; data_write={priority_lsms_climate_review_data_write}; modeling_gate={priority_lsms_climate_review_modeling}",
        "" if priority_lsms_climate_review_gate_ok else "Run script/187_build_priority_lsms_isa_minimum_batch_climate_linkage_review_queue.py after the manual board, target smoke test, and variable evidence matrix are current.",
    )
    priority_lsms_local_stray_summary = read_csv_dicts(RESULT_DIR / "priority_lsms_isa_local_stray_raw_package_locator_summary.csv")
    priority_lsms_local_stray_datasets = safe_int(next((row.get("value", "0") for row in priority_lsms_local_stray_summary if row.get("metric") == "priority_lsms_local_stray_raw_locator_dataset_rows"), "0"), 0)
    priority_lsms_local_stray_candidates = safe_int(next((row.get("value", "0") for row in priority_lsms_local_stray_summary if row.get("metric") == "priority_lsms_local_stray_raw_locator_candidate_file_rows"), "0"), 0)
    priority_lsms_local_stray_route_rows = safe_int(next((row.get("value", "0") for row in priority_lsms_local_stray_summary if row.get("metric") == "priority_lsms_local_stray_raw_locator_route_plan_rows"), "0"), 0)
    priority_lsms_local_stray_matched = safe_int(next((row.get("value", "0") for row in priority_lsms_local_stray_summary if row.get("metric") == "priority_lsms_local_stray_raw_locator_matched_idno_rows"), "0"), 0)
    priority_lsms_local_stray_outside = safe_int(next((row.get("value", "0") for row in priority_lsms_local_stray_summary if row.get("metric") == "priority_lsms_local_stray_raw_locator_outside_target_candidate_rows"), "0"), 0)
    priority_lsms_local_stray_incoming = safe_int(next((row.get("value", "0") for row in priority_lsms_local_stray_summary if row.get("metric") == "priority_lsms_local_stray_raw_locator_incoming_candidate_rows"), "0"), 0)
    priority_lsms_local_stray_already = safe_int(next((row.get("value", "0") for row in priority_lsms_local_stray_summary if row.get("metric") == "priority_lsms_local_stray_raw_locator_already_target_candidate_rows"), "0"), 0)
    priority_lsms_local_stray_data_write = next((row.get("value", "") for row in priority_lsms_local_stray_summary if row.get("metric") == "priority_lsms_local_stray_raw_locator_data_write_status"), "")
    priority_lsms_local_stray_raw_status = next((row.get("value", "") for row in priority_lsms_local_stray_summary if row.get("metric") == "priority_lsms_local_stray_raw_locator_raw_promotion_status"), "")
    priority_lsms_local_stray_modeling = next((row.get("value", "") for row in priority_lsms_local_stray_summary if row.get("metric") == "modeling_gate_status"), "")
    priority_lsms_local_stray_gate_ok = (
        counts["priority_lsms_isa_local_stray_raw_package_locator_summary"] > 0
        and counts["priority_lsms_isa_local_stray_raw_package_route_plan"] == priority_lsms_local_stray_route_rows
        and counts["priority_lsms_isa_local_stray_raw_package_candidates"] == priority_lsms_local_stray_candidates
        and file_ok(REPORT_DIR / "priority_lsms_isa_local_stray_raw_package_locator.md")
        and priority_lsms_local_stray_datasets == priority_lsms_manual_execution_rows
        and priority_lsms_local_stray_route_rows == priority_lsms_manual_execution_rows
        and (priority_lsms_local_stray_outside + priority_lsms_local_stray_incoming + priority_lsms_local_stray_already) <= priority_lsms_local_stray_candidates
        and priority_lsms_local_stray_matched <= priority_lsms_local_stray_datasets
        and priority_lsms_local_stray_data_write == "blocked_no_data_write"
        and priority_lsms_local_stray_raw_status in {"blocked_no_local_stray_raw_package_found", "blocked_pending_manual_review"}
        and priority_lsms_local_stray_modeling == "blocked"
    )
    add(
        rows,
        "dataset_promotion",
        "Priority LSMS/ISA local stray raw package locator searches the workspace for already-downloaded packages outside target folders",
        status(priority_lsms_local_stray_gate_ok),
        f"route_rows={counts['priority_lsms_isa_local_stray_raw_package_route_plan']}; candidate_rows={counts['priority_lsms_isa_local_stray_raw_package_candidates']}; summary_rows={counts['priority_lsms_isa_local_stray_raw_package_locator_summary']}; datasets={priority_lsms_local_stray_datasets}; matched_idnos={priority_lsms_local_stray_matched}; outside_target={priority_lsms_local_stray_outside}; incoming={priority_lsms_local_stray_incoming}; already_target={priority_lsms_local_stray_already}; raw_status={priority_lsms_local_stray_raw_status}; data_write={priority_lsms_local_stray_data_write}; modeling_gate={priority_lsms_local_stray_modeling}",
        "" if priority_lsms_local_stray_gate_ok else "Run script/188_build_priority_lsms_isa_local_stray_raw_package_locator.py after the manual board, acceptance matrix, and target smoke test are current.",
    )
    priority_lsms_promotion_gate_summary = read_csv_dicts(RESULT_DIR / "priority_lsms_isa_promotion_gate_dashboard_summary.csv")
    priority_lsms_promotion_gate_country_waves = safe_int(next((row.get("value", "0") for row in priority_lsms_promotion_gate_summary if row.get("metric") == "priority_lsms_promotion_gate_country_wave_rows"), "0"), 0)
    priority_lsms_promotion_gate_requirements = safe_int(next((row.get("value", "0") for row in priority_lsms_promotion_gate_summary if row.get("metric") == "priority_lsms_promotion_gate_requirement_rows"), "0"), 0)
    priority_lsms_promotion_gate_promoted = safe_int(next((row.get("value", "0") for row in priority_lsms_promotion_gate_summary if row.get("metric") == "priority_lsms_promotion_gate_promoted_rows"), "0"), 0)
    priority_lsms_promotion_gate_blocked_raw = safe_int(next((row.get("value", "0") for row in priority_lsms_promotion_gate_summary if row.get("metric") == "priority_lsms_promotion_gate_blocked_raw_package_rows"), "0"), 0)
    priority_lsms_promotion_gate_ready_packet = safe_int(next((row.get("value", "0") for row in priority_lsms_promotion_gate_summary if row.get("metric") == "priority_lsms_promotion_gate_ready_for_packet_rows"), "0"), 0)
    priority_lsms_promotion_gate_minimum_remaining = safe_int(next((row.get("value", "0") for row in priority_lsms_promotion_gate_summary if row.get("metric") == "priority_lsms_promotion_gate_minimum_remaining_rows"), "0"), 0)
    priority_lsms_promotion_gate_backups = safe_int(next((row.get("value", "0") for row in priority_lsms_promotion_gate_summary if row.get("metric") == "priority_lsms_promotion_gate_backup_rows"), "0"), 0)
    priority_lsms_promotion_gate_data_write = next((row.get("value", "") for row in priority_lsms_promotion_gate_summary if row.get("metric") == "data_write_gate_status"), "")
    priority_lsms_promotion_gate_modeling = next((row.get("value", "") for row in priority_lsms_promotion_gate_summary if row.get("metric") == "modeling_gate_status"), "")
    priority_lsms_promotion_gate_ok = (
        counts["priority_lsms_isa_promotion_gate_dashboard_summary"] > 0
        and counts["priority_lsms_isa_promotion_gate_dashboard"] == priority_lsms_promotion_gate_country_waves
        and counts["priority_lsms_isa_promotion_gate_requirement_dashboard"] == priority_lsms_promotion_gate_requirements
        and file_ok(REPORT_DIR / "priority_lsms_isa_promotion_gate_dashboard.md")
        and priority_lsms_promotion_gate_country_waves == 19
        and priority_lsms_promotion_gate_requirements == 152
        and priority_lsms_promotion_gate_promoted == 1
        and priority_lsms_promotion_gate_blocked_raw == 18
        and priority_lsms_promotion_gate_ready_packet == 0
        and priority_lsms_promotion_gate_minimum_remaining == 10
        and priority_lsms_promotion_gate_backups == 8
        and priority_lsms_promotion_gate_data_write == "blocked_for_unpromoted_rows"
        and priority_lsms_promotion_gate_modeling == "blocked"
    )
    add(
        rows,
        "dataset_promotion",
        "Priority LSMS/ISA promotion gate dashboard synthesizes receipt, schema, value, semantics, registry, and data-write gates",
        status(priority_lsms_promotion_gate_ok),
        f"country_waves={counts['priority_lsms_isa_promotion_gate_dashboard']}; requirement_rows={counts['priority_lsms_isa_promotion_gate_requirement_dashboard']}; summary_rows={counts['priority_lsms_isa_promotion_gate_dashboard_summary']}; promoted={priority_lsms_promotion_gate_promoted}; blocked_raw_package={priority_lsms_promotion_gate_blocked_raw}; ready_for_packet={priority_lsms_promotion_gate_ready_packet}; minimum_remaining={priority_lsms_promotion_gate_minimum_remaining}; backups={priority_lsms_promotion_gate_backups}; data_write={priority_lsms_promotion_gate_data_write}; modeling_gate={priority_lsms_promotion_gate_modeling}",
        "" if priority_lsms_promotion_gate_ok else "Run script/173_build_priority_lsms_isa_promotion_gate_dashboard.py after receipt/schema/value/semantics and registry outputs are current.",
    )
    priority_synthesis_summary = read_csv_dicts(RESULT_DIR / "priority_analysis_dataset_synthesis_blueprint_summary.csv")
    priority_synthesis_schema_rows = safe_int(next((row.get("value", "0") for row in priority_synthesis_summary if row.get("metric") == "priority_synthesis_blueprint_schema_rows"), "0"), 0)
    priority_synthesis_required_rows = safe_int(next((row.get("value", "0") for row in priority_synthesis_summary if row.get("metric") == "priority_synthesis_blueprint_required_rows"), "0"), 0)
    priority_synthesis_ready_required_rows = safe_int(next((row.get("value", "0") for row in priority_synthesis_summary if row.get("metric") == "priority_synthesis_blueprint_ready_required_rows"), "0"), 0)
    priority_synthesis_blocked_required_rows = safe_int(next((row.get("value", "0") for row in priority_synthesis_summary if row.get("metric") == "priority_synthesis_blueprint_blocked_required_rows"), "0"), 0)
    priority_synthesis_join_rows = safe_int(next((row.get("value", "0") for row in priority_synthesis_summary if row.get("metric") == "priority_synthesis_blueprint_join_plan_rows"), "0"), 0)
    priority_synthesis_join_ready_rows = safe_int(next((row.get("value", "0") for row in priority_synthesis_summary if row.get("metric") == "priority_synthesis_blueprint_join_ready_rows"), "0"), 0)
    priority_synthesis_candidate_variable_rows = safe_int(next((row.get("value", "0") for row in priority_synthesis_summary if row.get("metric") == "priority_synthesis_blueprint_candidate_variable_rows"), "0"), 0)
    priority_synthesis_manual_verified_rows = safe_int(next((row.get("value", "0") for row in priority_synthesis_summary if row.get("metric") == "priority_synthesis_blueprint_manual_verified_variable_rows"), "0"), 0)
    priority_synthesis_handoffs = safe_int(next((row.get("value", "0") for row in priority_synthesis_summary if row.get("metric") == "priority_synthesis_blueprint_handoff_readmes_written"), "0"), 0)
    priority_synthesis_modeling_gate = next((row.get("value", "") for row in priority_synthesis_summary if row.get("metric") == "modeling_gate_status"), "")
    priority_synthesis_gate_ok = (
        counts["priority_analysis_dataset_synthesis_blueprint"] >= 572
        and counts["priority_analysis_dataset_join_plan"] >= counts["priority_promotion_acquisition_wave_plan"]
        and counts["priority_analysis_dataset_synthesis_blueprint_summary"] > 0
        and file_ok(REPORT_DIR / "priority_analysis_dataset_synthesis_blueprint.md")
        and priority_synthesis_schema_rows >= 572
        and priority_synthesis_required_rows >= 325
        and priority_synthesis_blocked_required_rows >= priority_synthesis_required_rows
        and priority_synthesis_candidate_variable_rows >= 2700
        and priority_synthesis_join_rows >= counts["priority_promotion_acquisition_wave_plan"]
        and priority_synthesis_handoffs >= counts["priority_promotion_acquisition_wave_plan"]
        and (not priority_manual_no_raw_present or priority_synthesis_ready_required_rows == 0)
        and (not priority_manual_no_raw_present or priority_synthesis_join_ready_rows == 0)
        and (not priority_manual_no_raw_present or priority_synthesis_manual_verified_rows == 0)
        and priority_synthesis_modeling_gate == "blocked"
    )
    add(
        rows,
        "dataset_promotion",
        "Priority analysis dataset synthesis blueprint defines promoted household-climate schema, joins, and fail-closed blockers before data writes",
        status(priority_synthesis_gate_ok),
        f"blueprint_rows={counts['priority_analysis_dataset_synthesis_blueprint']}; join_rows={counts['priority_analysis_dataset_join_plan']}; summary_rows={counts['priority_analysis_dataset_synthesis_blueprint_summary']}; reported_schema_rows={priority_synthesis_schema_rows}; required_rows={priority_synthesis_required_rows}; ready_required={priority_synthesis_ready_required_rows}; blocked_required={priority_synthesis_blocked_required_rows}; reported_join_rows={priority_synthesis_join_rows}; join_ready={priority_synthesis_join_ready_rows}; candidate_variables={priority_synthesis_candidate_variable_rows}; manual_verified={priority_synthesis_manual_verified_rows}; handoffs={priority_synthesis_handoffs}; no_raw_present={priority_manual_no_raw_present}; modeling_gate={priority_synthesis_modeling_gate}",
        "" if priority_synthesis_gate_ok else "Run script/132_build_priority_analysis_dataset_synthesis_blueprint.py after manual verification and climate preflight gates.",
    )
    priority_packet_summary = read_csv_dicts(RESULT_DIR / "priority_country_wave_promotion_packet_summary.csv")
    priority_packet_rows = safe_int(next((row.get("value", "0") for row in priority_packet_summary if row.get("metric") == "priority_country_wave_packet_rows"), "0"), 0)
    priority_packet_priority_rows = safe_int(next((row.get("value", "0") for row in priority_packet_summary if row.get("metric") == "priority_country_wave_packet_priority_batch_rows"), "0"), 0)
    priority_packet_backup_rows = safe_int(next((row.get("value", "0") for row in priority_packet_summary if row.get("metric") == "priority_country_wave_packet_backup_rows"), "0"), 0)
    priority_packet_gate_rows = safe_int(next((row.get("value", "0") for row in priority_packet_summary if row.get("metric") == "priority_country_wave_packet_gate_rows"), "0"), 0)
    priority_packet_passed_gates = safe_int(next((row.get("value", "0") for row in priority_packet_summary if row.get("metric") == "priority_country_wave_packet_passed_gate_rows"), "0"), 0)
    priority_packet_failed_gates = safe_int(next((row.get("value", "0") for row in priority_packet_summary if row.get("metric") == "priority_country_wave_packet_failed_gate_rows"), "0"), 0)
    priority_packet_public_ready = safe_int(next((row.get("value", "0") for row in priority_packet_summary if row.get("metric") == "priority_country_wave_packet_public_documentation_ready_rows"), "0"), 0)
    priority_packet_metadata_ready = safe_int(next((row.get("value", "0") for row in priority_packet_summary if row.get("metric") == "priority_country_wave_packet_official_metadata_ready_rows"), "0"), 0)
    priority_packet_endpoint_ready = safe_int(next((row.get("value", "0") for row in priority_packet_summary if row.get("metric") == "priority_country_wave_packet_endpoint_matrix_ready_rows"), "0"), 0)
    priority_packet_credentialed_ready = safe_int(next((row.get("value", "0") for row in priority_packet_summary if row.get("metric") == "priority_country_wave_packet_credentialed_acquisition_ready_rows"), "0"), 0)
    priority_packet_raw_ready = safe_int(next((row.get("value", "0") for row in priority_packet_summary if row.get("metric") == "priority_country_wave_packet_raw_package_ready_rows"), "0"), 0)
    priority_packet_financial_ready = safe_int(next((row.get("value", "0") for row in priority_packet_summary if row.get("metric") == "priority_country_wave_packet_financial_ready_rows"), "0"), 0)
    priority_packet_access_ready = safe_int(next((row.get("value", "0") for row in priority_packet_summary if row.get("metric") == "priority_country_wave_packet_access_ready_rows"), "0"), 0)
    priority_packet_climate_ready = safe_int(next((row.get("value", "0") for row in priority_packet_summary if row.get("metric") == "priority_country_wave_packet_climate_ready_rows"), "0"), 0)
    priority_packet_analysis_ready = safe_int(next((row.get("value", "0") for row in priority_packet_summary if row.get("metric") == "priority_country_wave_packet_analysis_ready_rows"), "0"), 0)
    priority_packet_actions = safe_int(next((row.get("value", "0") for row in priority_packet_summary if row.get("metric") == "priority_country_wave_packet_action_rows"), "0"), 0)
    priority_packet_reports = safe_int(next((row.get("value", "0") for row in priority_packet_summary if row.get("metric") == "priority_country_wave_packet_reports_written"), "0"), 0)
    priority_packet_handoffs = safe_int(next((row.get("value", "0") for row in priority_packet_summary if row.get("metric") == "priority_country_wave_packet_handoffs_written"), "0"), 0)
    priority_packet_modeling_gate = next((row.get("value", "") for row in priority_packet_summary if row.get("metric") == "modeling_gate_status"), "")
    priority_packet_gate_ok = (
        counts["priority_country_wave_promotion_packet_index"] >= counts["priority_promotion_acquisition_wave_plan"]
        and counts["priority_country_wave_promotion_packet_gate_matrix"] >= counts["priority_promotion_acquisition_wave_plan"] * 14
        and counts["priority_country_wave_promotion_packet_action_queue"] >= counts["priority_promotion_acquisition_wave_plan"]
        and counts["priority_country_wave_promotion_packet_summary"] > 0
        and file_ok(REPORT_DIR / "priority_country_wave_promotion_packets.md")
        and priority_packet_rows >= counts["priority_promotion_acquisition_wave_plan"]
        and priority_packet_priority_rows >= 10
        and priority_packet_backup_rows >= 3
        and priority_packet_gate_rows >= counts["priority_promotion_acquisition_wave_plan"] * 14
        and priority_packet_passed_gates >= counts["priority_promotion_acquisition_wave_plan"] * 4
        and priority_packet_failed_gates >= counts["priority_promotion_acquisition_wave_plan"] * 10
        and priority_packet_public_ready >= counts["priority_promotion_acquisition_wave_plan"]
        and priority_packet_metadata_ready >= counts["priority_promotion_acquisition_wave_plan"]
        and priority_packet_endpoint_ready >= counts["priority_promotion_acquisition_wave_plan"]
        and priority_packet_credentialed_ready >= counts["priority_promotion_acquisition_wave_plan"]
        and priority_packet_raw_ready == 0
        and priority_packet_financial_ready == 0
        and priority_packet_access_ready == 0
        and priority_packet_climate_ready == 0
        and priority_packet_analysis_ready == 0
        and priority_packet_actions >= counts["priority_promotion_acquisition_wave_plan"]
        and priority_packet_reports >= counts["priority_promotion_acquisition_wave_plan"]
        and priority_packet_handoffs >= counts["priority_promotion_acquisition_wave_plan"]
        and priority_packet_modeling_gate == "blocked"
    )
    add(
        rows,
        "dataset_promotion",
        "Priority country-wave promotion packets consolidate documentation, raw, manual, climate, synthesis, and write gates per wave",
        status(priority_packet_gate_ok),
        f"index_rows={counts['priority_country_wave_promotion_packet_index']}; gate_rows={counts['priority_country_wave_promotion_packet_gate_matrix']}; action_rows={counts['priority_country_wave_promotion_packet_action_queue']}; summary_rows={counts['priority_country_wave_promotion_packet_summary']}; reported_packets={priority_packet_rows}; priority_rows={priority_packet_priority_rows}; backup_rows={priority_packet_backup_rows}; reported_gate_rows={priority_packet_gate_rows}; passed_gates={priority_packet_passed_gates}; failed_gates={priority_packet_failed_gates}; public_ready={priority_packet_public_ready}; metadata_ready={priority_packet_metadata_ready}; endpoint_ready={priority_packet_endpoint_ready}; credentialed_ready={priority_packet_credentialed_ready}; raw_ready={priority_packet_raw_ready}; financial_ready={priority_packet_financial_ready}; access_ready={priority_packet_access_ready}; climate_ready={priority_packet_climate_ready}; analysis_ready={priority_packet_analysis_ready}; actions={priority_packet_actions}; reports={priority_packet_reports}; handoffs={priority_packet_handoffs}; modeling_gate={priority_packet_modeling_gate}",
        "" if priority_packet_gate_ok else "Run script/134_build_priority_country_wave_promotion_packets.py after public documentation, synthesis, manual, climate, and receipt gates.",
    )
    priority_lsms_packet_summary = read_csv_dicts(RESULT_DIR / "priority_lsms_isa_country_wave_promotion_packet_summary.csv")
    priority_lsms_packet_rows = safe_int(next((row.get("value", "0") for row in priority_lsms_packet_summary if row.get("metric") == "priority_lsms_country_wave_packet_rows"), "0"), 0)
    priority_lsms_packet_core_rows = safe_int(next((row.get("value", "0") for row in priority_lsms_packet_summary if row.get("metric") == "priority_lsms_country_wave_packet_core_rows"), "0"), 0)
    priority_lsms_packet_backup_rows = safe_int(next((row.get("value", "0") for row in priority_lsms_packet_summary if row.get("metric") == "priority_lsms_country_wave_packet_backup_rows"), "0"), 0)
    priority_lsms_packet_gate_rows = safe_int(next((row.get("value", "0") for row in priority_lsms_packet_summary if row.get("metric") == "priority_lsms_country_wave_packet_gate_rows"), "0"), 0)
    priority_lsms_packet_passed_gates = safe_int(next((row.get("value", "0") for row in priority_lsms_packet_summary if row.get("metric") == "priority_lsms_country_wave_packet_passed_gate_rows"), "0"), 0)
    priority_lsms_packet_failed_gates = safe_int(next((row.get("value", "0") for row in priority_lsms_packet_summary if row.get("metric") == "priority_lsms_country_wave_packet_failed_gate_rows"), "0"), 0)
    priority_lsms_packet_public_ready = safe_int(next((row.get("value", "0") for row in priority_lsms_packet_summary if row.get("metric") == "priority_lsms_country_wave_packet_public_documentation_ready_rows"), "0"), 0)
    priority_lsms_packet_variable_ready = safe_int(next((row.get("value", "0") for row in priority_lsms_packet_summary if row.get("metric") == "priority_lsms_country_wave_packet_variable_evidence_ready_rows"), "0"), 0)
    priority_lsms_packet_raw_ready = safe_int(next((row.get("value", "0") for row in priority_lsms_packet_summary if row.get("metric") == "priority_lsms_country_wave_packet_raw_package_ready_rows"), "0"), 0)
    priority_lsms_packet_raw_verified = safe_int(next((row.get("value", "0") for row in priority_lsms_packet_summary if row.get("metric") == "priority_lsms_country_wave_packet_raw_value_verified_rows"), "0"), 0)
    priority_lsms_packet_financial_ready = safe_int(next((row.get("value", "0") for row in priority_lsms_packet_summary if row.get("metric") == "priority_lsms_country_wave_packet_financial_ready_rows"), "0"), 0)
    priority_lsms_packet_access_ready = safe_int(next((row.get("value", "0") for row in priority_lsms_packet_summary if row.get("metric") == "priority_lsms_country_wave_packet_access_ready_rows"), "0"), 0)
    priority_lsms_packet_climate_ready = safe_int(next((row.get("value", "0") for row in priority_lsms_packet_summary if row.get("metric") == "priority_lsms_country_wave_packet_climate_ready_rows"), "0"), 0)
    priority_lsms_packet_synthesis_ready = safe_int(next((row.get("value", "0") for row in priority_lsms_packet_summary if row.get("metric") == "priority_lsms_country_wave_packet_analysis_synthesis_ready_rows"), "0"), 0)
    priority_lsms_packet_analysis_ready = safe_int(next((row.get("value", "0") for row in priority_lsms_packet_summary if row.get("metric") == "priority_lsms_country_wave_packet_analysis_ready_rows"), "0"), 0)
    priority_lsms_packet_actions = safe_int(next((row.get("value", "0") for row in priority_lsms_packet_summary if row.get("metric") == "priority_lsms_country_wave_packet_action_rows"), "0"), 0)
    priority_lsms_packet_reports = safe_int(next((row.get("value", "0") for row in priority_lsms_packet_summary if row.get("metric") == "priority_lsms_country_wave_packet_reports_written"), "0"), 0)
    priority_lsms_packet_handoffs = safe_int(next((row.get("value", "0") for row in priority_lsms_packet_summary if row.get("metric") == "priority_lsms_country_wave_packet_handoffs_written"), "0"), 0)
    priority_lsms_packet_data_write = next((row.get("value", "") for row in priority_lsms_packet_summary if row.get("metric") == "priority_lsms_country_wave_packet_data_write_status"), "")
    priority_lsms_packet_modeling_gate = next((row.get("value", "") for row in priority_lsms_packet_summary if row.get("metric") == "modeling_gate_status"), "")
    priority_lsms_packet_gate_ok = (
        counts["priority_lsms_isa_country_wave_promotion_packet_index"] >= counts["priority_lsms_isa_refocused_acquisition_queue"]
        and counts["priority_lsms_isa_country_wave_promotion_packet_gate_matrix"] >= counts["priority_lsms_isa_refocused_acquisition_queue"] * 19
        and counts["priority_lsms_isa_country_wave_promotion_packet_action_queue"] >= counts["priority_lsms_isa_refocused_acquisition_queue"] - max(priority_lsms_packet_analysis_ready, 0)
        and counts["priority_lsms_isa_country_wave_promotion_packet_summary"] > 0
        and file_ok(REPORT_DIR / "priority_lsms_isa_country_wave_promotion_packets.md")
        and priority_lsms_packet_rows >= counts["priority_lsms_isa_refocused_acquisition_queue"]
        and priority_lsms_packet_core_rows >= 10
        and priority_lsms_packet_backup_rows >= 9
        and priority_lsms_packet_gate_rows >= counts["priority_lsms_isa_refocused_acquisition_queue"] * 19
        and priority_lsms_packet_passed_gates >= counts["priority_lsms_isa_refocused_acquisition_queue"] * 2
        and priority_lsms_packet_passed_gates + priority_lsms_packet_failed_gates >= priority_lsms_packet_gate_rows
        and priority_lsms_packet_public_ready >= counts["priority_lsms_isa_refocused_acquisition_queue"]
        and priority_lsms_packet_variable_ready >= counts["priority_lsms_isa_refocused_acquisition_queue"]
        and 0 <= priority_lsms_packet_raw_ready <= priority_lsms_packet_rows
        and 1 <= priority_lsms_packet_raw_verified <= priority_lsms_packet_rows
        and 1 <= priority_lsms_packet_financial_ready <= priority_lsms_packet_rows
        and 1 <= priority_lsms_packet_access_ready <= priority_lsms_packet_rows
        and 1 <= priority_lsms_packet_climate_ready <= priority_lsms_packet_rows
        and 1 <= priority_lsms_packet_synthesis_ready <= priority_lsms_packet_rows
        and 1 <= priority_lsms_packet_analysis_ready <= priority_lsms_packet_rows
        and priority_lsms_packet_actions >= counts["priority_lsms_isa_refocused_acquisition_queue"] - priority_lsms_packet_analysis_ready
        and priority_lsms_packet_reports >= counts["priority_lsms_isa_refocused_acquisition_queue"]
        and priority_lsms_packet_handoffs >= counts["priority_lsms_isa_refocused_acquisition_queue"]
        and priority_lsms_packet_data_write == "open_registry_has_promoted_rows"
        and priority_lsms_packet_modeling_gate == "blocked"
    )
    add(
        rows,
        "dataset_promotion",
        "Priority LSMS/ISA country-wave promotion packets cover every refocused target with fail-closed access, climate, synthesis, and registry gates",
        status(priority_lsms_packet_gate_ok),
        f"index_rows={counts['priority_lsms_isa_country_wave_promotion_packet_index']}; gate_rows={counts['priority_lsms_isa_country_wave_promotion_packet_gate_matrix']}; action_rows={counts['priority_lsms_isa_country_wave_promotion_packet_action_queue']}; summary_rows={counts['priority_lsms_isa_country_wave_promotion_packet_summary']}; reported_packets={priority_lsms_packet_rows}; core_rows={priority_lsms_packet_core_rows}; backup_rows={priority_lsms_packet_backup_rows}; reported_gate_rows={priority_lsms_packet_gate_rows}; passed_gates={priority_lsms_packet_passed_gates}; failed_gates={priority_lsms_packet_failed_gates}; public_ready={priority_lsms_packet_public_ready}; variable_ready={priority_lsms_packet_variable_ready}; raw_ready={priority_lsms_packet_raw_ready}; raw_verified={priority_lsms_packet_raw_verified}; financial_ready={priority_lsms_packet_financial_ready}; access_ready={priority_lsms_packet_access_ready}; climate_ready={priority_lsms_packet_climate_ready}; synthesis_ready={priority_lsms_packet_synthesis_ready}; analysis_ready={priority_lsms_packet_analysis_ready}; actions={priority_lsms_packet_actions}; reports={priority_lsms_packet_reports}; handoffs={priority_lsms_packet_handoffs}; data_write={priority_lsms_packet_data_write}; modeling_gate={priority_lsms_packet_modeling_gate}",
        "" if priority_lsms_packet_gate_ok else "Run script/148_build_priority_lsms_isa_country_wave_promotion_packets.py after LSMS/ISA documentation, variable evidence, raw intake, and archive preflight gates.",
    )
    mwi2004_promoted_summary = read_csv_dicts(RESULT_DIR / "mwi2004_promoted_household_climate_dataset_summary.csv")
    mwi2004_promoted_validation = read_csv_dicts(RESULT_DIR / "mwi2004_promoted_household_climate_dataset_validation.csv")
    mwi2004_promoted_status = next((row.get("value", "") for row in mwi2004_promoted_summary if row.get("metric") == "analysis_ready_status"), "")
    mwi2004_promoted_rows = safe_int(next((row.get("value", "0") for row in mwi2004_promoted_summary if row.get("metric") == "promoted_rows"), "0"), 0)
    mwi2004_promoted_validation_fail = sum(1 for row in mwi2004_promoted_validation if row.get("status") != "pass")
    mwi2004_promoted_ok = (
        counts["mwi2004_promoted_household_climate_dataset_summary"] > 0
        and counts["mwi2004_promoted_household_climate_dataset_dictionary"] >= 30
        and counts["mwi2004_promoted_household_climate_dataset_validation"] > 0
        and file_ok(REPORT_DIR / "mwi2004_promoted_household_climate_dataset.md")
        and file_ok(DATA_DIR / "mwi2004_household_climate_analysis.csv")
        and mwi2004_promoted_status == "promoted_analysis_ready"
        and mwi2004_promoted_rows > 0
        and mwi2004_promoted_validation_fail == 0
    )
    add(
        rows,
        "dataset_promotion",
        "Malawi 2004 promoted household-climate dataset has verified financial, access, and CHIRPS ADM2 exposure joins",
        status(mwi2004_promoted_ok),
        f"summary_rows={counts['mwi2004_promoted_household_climate_dataset_summary']}; dictionary_rows={counts['mwi2004_promoted_household_climate_dataset_dictionary']}; validation_rows={counts['mwi2004_promoted_household_climate_dataset_validation']}; status={mwi2004_promoted_status}; rows={mwi2004_promoted_rows}; validation_fail={mwi2004_promoted_validation_fail}; data_exists={(DATA_DIR / 'mwi2004_household_climate_analysis.csv').exists()}",
        "" if mwi2004_promoted_ok else "Run script/171_build_mwi2004_promoted_household_climate_dataset.py after Malawi financial/access/missing-unit and CHIRPS gates pass.",
    )
    mwi2004_sdg382_summary = read_csv_dicts(RESULT_DIR / "mwi2004_sdg382_discretionary_budget_parameter_summary.csv")
    mwi2004_sdg382_rows = safe_int(next((row.get("value", "0") for row in mwi2004_sdg382_summary if row.get("metric") == "household_rows_with_internal_sdg382_inputs"), "0"), 0)
    mwi2004_sdg382_internal_ready = next((row.get("value", "") for row in mwi2004_sdg382_summary if row.get("metric") == "raw_internal_sdg382_inputs_complete"), "")
    mwi2004_sdg382_ppp_cpi = next((row.get("value", "") for row in mwi2004_sdg382_summary if row.get("metric") == "external_ppp_cpi_parameters_verified"), "")
    mwi2004_sdg382_spl = next((row.get("value", "") for row in mwi2004_sdg382_summary if row.get("metric") == "spl_local_currency_verified"), "")
    mwi2004_sdg382_ready = next((row.get("value", "") for row in mwi2004_sdg382_summary if row.get("metric") == "sdg382_ready"), "")
    mwi2004_sdg382_data_write = next((row.get("value", "") for row in mwi2004_sdg382_summary if row.get("metric") == "data_write_gate_status"), "")
    mwi2004_sdg382_modeling = next((row.get("value", "") for row in mwi2004_sdg382_summary if row.get("metric") == "modeling_gate_status"), "")
    mwi2004_sdg382_gate_ok = (
        counts["mwi2004_sdg382_discretionary_budget_parameter_summary"] > 0
        and counts["mwi2004_sdg382_discretionary_budget_parameter_audit"] >= 10
        and file_ok(REPORT_DIR / "mwi2004_sdg382_discretionary_budget_parameter_audit.md")
        and mwi2004_sdg382_rows == mwi2004_promoted_rows
        and mwi2004_sdg382_internal_ready == "1"
        and mwi2004_sdg382_ppp_cpi == "0"
        and mwi2004_sdg382_spl == "0"
        and mwi2004_sdg382_ready == "0"
        and mwi2004_sdg382_data_write == "closed"
        and mwi2004_sdg382_modeling == "blocked"
    )
    add(
        rows,
        "dataset_promotion",
        "Malawi 2004 SDG 3.8.2 parameter audit verifies internal raw inputs and keeps discretionary-budget gate fail-closed",
        status(mwi2004_sdg382_gate_ok),
        f"audit_rows={counts['mwi2004_sdg382_discretionary_budget_parameter_audit']}; summary_rows={counts['mwi2004_sdg382_discretionary_budget_parameter_summary']}; internal_rows={mwi2004_sdg382_rows}; internal_ready={mwi2004_sdg382_internal_ready}; ppp_cpi_verified={mwi2004_sdg382_ppp_cpi}; spl_verified={mwi2004_sdg382_spl}; sdg382_ready={mwi2004_sdg382_ready}; data_write={mwi2004_sdg382_data_write}; modeling_gate={mwi2004_sdg382_modeling}",
        "" if mwi2004_sdg382_gate_ok else "Run script/189_build_mwi2004_sdg382_discretionary_budget_parameter_audit.py after Malawi financial inputs are current.",
    )
    mwi2004_sdg382_external_summary = read_csv_dicts(RESULT_DIR / "mwi2004_sdg382_external_parameter_candidate_summary.csv")
    mwi2004_sdg382_external_parameter_rows = safe_int(next((row.get("value", "0") for row in mwi2004_sdg382_external_summary if row.get("metric") == "parameter_rows"), "0"), 0)
    mwi2004_sdg382_external_ppp = next((row.get("value", "") for row in mwi2004_sdg382_external_summary if row.get("metric") == "private_consumption_ppp_source_verified"), "")
    mwi2004_sdg382_external_cpi = next((row.get("value", "") for row in mwi2004_sdg382_external_summary if row.get("metric") == "annual_cpi_bridge_source_verified"), "")
    mwi2004_sdg382_external_bridge = next((row.get("value", "") for row in mwi2004_sdg382_external_summary if row.get("metric") == "external_parameter_bridge_accepted"), "")
    mwi2004_sdg382_external_ready = next((row.get("value", "") for row in mwi2004_sdg382_external_summary if row.get("metric") == "sdg382_ready"), "")
    mwi2004_sdg382_external_data_write = next((row.get("value", "") for row in mwi2004_sdg382_external_summary if row.get("metric") == "data_write_gate_status"), "")
    mwi2004_sdg382_external_modeling = next((row.get("value", "") for row in mwi2004_sdg382_external_summary if row.get("metric") == "modeling_gate_status"), "")
    mwi2004_sdg382_external_gate_ok = (
        counts["mwi2004_sdg382_external_parameter_candidate_summary"] > 0
        and counts["mwi2004_sdg382_external_parameter_source_ledger"] == mwi2004_sdg382_external_parameter_rows
        and counts["mwi2004_sdg382_external_parameter_source_ledger"] >= 9
        and file_ok(REPORT_DIR / "mwi2004_sdg382_external_parameter_source_ledger.md")
        and mwi2004_sdg382_external_ppp == "1"
        and mwi2004_sdg382_external_cpi == "1"
        and mwi2004_sdg382_external_bridge == "0"
        and mwi2004_sdg382_external_ready == "0"
        and mwi2004_sdg382_external_data_write == "closed"
        and mwi2004_sdg382_external_modeling == "blocked"
    )
    add(
        rows,
        "dataset_promotion",
        "Malawi 2004 SDG 3.8.2 external parameter ledger captures PPP/CPI candidates but keeps bridge unaccepted",
        status(mwi2004_sdg382_external_gate_ok),
        f"ledger_rows={counts['mwi2004_sdg382_external_parameter_source_ledger']}; summary_rows={counts['mwi2004_sdg382_external_parameter_candidate_summary']}; parameter_rows={mwi2004_sdg382_external_parameter_rows}; ppp_source_verified={mwi2004_sdg382_external_ppp}; cpi_source_verified={mwi2004_sdg382_external_cpi}; bridge_accepted={mwi2004_sdg382_external_bridge}; sdg382_ready={mwi2004_sdg382_external_ready}; data_write={mwi2004_sdg382_external_data_write}; modeling_gate={mwi2004_sdg382_external_modeling}",
        "" if mwi2004_sdg382_external_gate_ok else "Run script/190_build_mwi2004_sdg382_external_parameter_source_ledger.py after the Malawi SDG 3.8.2 parameter audit is current.",
    )
    mwi2004_sdg382_precheck_summary = read_csv_dicts(RESULT_DIR / "mwi2004_sdg382_candidate_classification_precheck_summary.csv")
    mwi2004_sdg382_precheck_rows = safe_int(next((row.get("value", "0") for row in mwi2004_sdg382_precheck_summary if row.get("metric") == "household_rows"), "0"), 0)
    mwi2004_sdg382_precheck_nonpositive = safe_int(next((row.get("value", "0") for row in mwi2004_sdg382_precheck_summary if row.get("metric") == "nonpositive_discretionary_budget_rows"), "0"), 0)
    mwi2004_sdg382_precheck_strict_rows = safe_int(next((row.get("value", "0") for row in mwi2004_sdg382_precheck_summary if row.get("metric") == "positive_discretionary_candidate_sdg382_rows"), "0"), 0)
    mwi2004_sdg382_precheck_floor_rows = safe_int(next((row.get("value", "0") for row in mwi2004_sdg382_precheck_summary if row.get("metric") == "floor_variant_candidate_sdg382_rows"), "0"), 0)
    mwi2004_sdg382_precheck_bridge = next((row.get("value", "") for row in mwi2004_sdg382_precheck_summary if row.get("metric") == "external_parameter_bridge_accepted"), "")
    mwi2004_sdg382_precheck_written = next((row.get("value", "") for row in mwi2004_sdg382_precheck_summary if row.get("metric") == "candidate_classification_written_to_data"), "")
    mwi2004_sdg382_precheck_ready = next((row.get("value", "") for row in mwi2004_sdg382_precheck_summary if row.get("metric") == "sdg382_ready"), "")
    mwi2004_sdg382_precheck_data_write = next((row.get("value", "") for row in mwi2004_sdg382_precheck_summary if row.get("metric") == "data_write_gate_status"), "")
    mwi2004_sdg382_precheck_modeling = next((row.get("value", "") for row in mwi2004_sdg382_precheck_summary if row.get("metric") == "modeling_gate_status"), "")
    mwi2004_sdg382_precheck_gate_ok = (
        counts["mwi2004_sdg382_candidate_classification_precheck_summary"] > 0
        and counts["mwi2004_sdg382_candidate_classification_precheck"] == 2
        and file_ok(REPORT_DIR / "mwi2004_sdg382_candidate_classification_precheck.md")
        and mwi2004_sdg382_precheck_rows == mwi2004_promoted_rows
        and mwi2004_sdg382_precheck_nonpositive >= 0
        and mwi2004_sdg382_precheck_strict_rows >= 0
        and mwi2004_sdg382_precheck_floor_rows >= 0
        and mwi2004_sdg382_precheck_bridge == "0"
        and mwi2004_sdg382_precheck_written == "0"
        and mwi2004_sdg382_precheck_ready == "0"
        and mwi2004_sdg382_precheck_data_write == "closed"
        and mwi2004_sdg382_precheck_modeling == "blocked"
    )
    add(
        rows,
        "dataset_promotion",
        "Malawi 2004 SDG 3.8.2 candidate classification precheck reports aggregate diagnostics without writing data",
        status(mwi2004_sdg382_precheck_gate_ok),
        f"precheck_rows={counts['mwi2004_sdg382_candidate_classification_precheck']}; summary_rows={counts['mwi2004_sdg382_candidate_classification_precheck_summary']}; household_rows={mwi2004_sdg382_precheck_rows}; nonpositive_discretionary={mwi2004_sdg382_precheck_nonpositive}; strict_candidate_rows={mwi2004_sdg382_precheck_strict_rows}; floor_candidate_rows={mwi2004_sdg382_precheck_floor_rows}; bridge_accepted={mwi2004_sdg382_precheck_bridge}; written_to_data={mwi2004_sdg382_precheck_written}; sdg382_ready={mwi2004_sdg382_precheck_ready}; data_write={mwi2004_sdg382_precheck_data_write}; modeling_gate={mwi2004_sdg382_precheck_modeling}",
        "" if mwi2004_sdg382_precheck_gate_ok else "Run script/191_build_mwi2004_sdg382_candidate_classification_precheck.py after the Malawi SDG 3.8.2 external parameter ledger is current.",
    )
    promoted_data_gate_summary = read_csv_dicts(RESULT_DIR / "promoted_data_gate_summary.csv")
    promoted_registry_rows = safe_int(next((row.get("value", "0") for row in promoted_data_gate_summary if row.get("metric") == "registry_promoted_analysis_ready_rows"), "0"), 0)
    promoted_data_before = safe_int(next((row.get("value", "0") for row in promoted_data_gate_summary if row.get("metric") == "data_dataset_files_before_gate"), "0"), 0)
    promoted_data_after = safe_int(next((row.get("value", "0") for row in promoted_data_gate_summary if row.get("metric") == "data_dataset_files_after_gate"), "0"), 0)
    promoted_data_quarantined = safe_int(next((row.get("value", "0") for row in promoted_data_gate_summary if row.get("metric") == "quarantined_diagnostic_data_files"), "0"), 0)
    promoted_data_readme = safe_int(next((row.get("value", "0") for row in promoted_data_gate_summary if row.get("metric") == "data_readme_written"), "0"), 0)
    promoted_data_status = next((row.get("value", "") for row in promoted_data_gate_summary if row.get("metric") == "promoted_data_gate_status"), "")
    actual_data_dataset_files = [
        path for path in DATA_DIR.rglob("*")
        if path.is_file() and path.name not in {"README.md", ".gitkeep"}
    ]
    promoted_data_gate_ok = (
        counts["promoted_data_gate_summary"] > 0
        and file_ok(REPORT_DIR / "promoted_data_gate.md")
        and file_ok(DATA_DIR / "README.md")
        and promoted_data_readme == 1
        and promoted_data_status in {"closed_no_promoted_rows", "open_registry_has_promoted_rows"}
        and len(actual_data_dataset_files) == promoted_data_after
        and (
            (promoted_registry_rows == 0 and promoted_data_after == 0 and promoted_data_status == "closed_no_promoted_rows")
            or promoted_registry_rows > 0
        )
    )
    add(
        rows,
        "dataset_promotion",
        "Promoted data gate keeps `data/` reserved for registry-approved analysis-ready datasets",
        status(promoted_data_gate_ok),
        f"summary_rows={counts['promoted_data_gate_summary']}; manifest_rows={counts['promoted_data_gate_manifest']}; promoted_rows={promoted_registry_rows}; data_before={promoted_data_before}; data_after={promoted_data_after}; actual_data_dataset_files={len(actual_data_dataset_files)}; quarantined={promoted_data_quarantined}; data_readme={promoted_data_readme}; gate_status={promoted_data_status}",
        "" if promoted_data_gate_ok else "Run script/127_enforce_promoted_data_gate.py after the promotion registry is built.",
    )
    objective_trace = read_csv_dicts(RESULT_DIR / "objective_requirement_traceability.csv")
    objective_guardrails = read_csv_dicts(RESULT_DIR / "objective_guardrail_audit.csv")
    trace_satisfied = sum(1 for row in objective_trace if row.get("status") == "satisfied")
    trace_unresolved = sum(1 for row in objective_trace if row.get("status") != "satisfied")
    guardrail_satisfied = sum(1 for row in objective_guardrails if row.get("status") == "satisfied")
    guardrail_unresolved = sum(1 for row in objective_guardrails if row.get("status") != "satisfied")
    add(
        rows,
        "evidence",
        "Objective traceability audit maps goal requirements to current evidence",
        status(counts["objective_requirement_traceability"] > 0 and counts["objective_guardrail_audit"] > 0 and counts["objective_traceability_summary"] > 0),
        f"requirement_rows={counts['objective_requirement_traceability']}; requirement_satisfied={trace_satisfied}; requirement_unresolved={trace_unresolved}; guardrail_rows={counts['objective_guardrail_audit']}; guardrail_satisfied={guardrail_satisfied}; guardrail_unresolved={guardrail_unresolved}; summary_rows={counts['objective_traceability_summary']}",
        "" if counts["objective_requirement_traceability"] > 0 and counts["objective_guardrail_audit"] > 0 and counts["objective_traceability_summary"] > 0 else "Run script/26_build_objective_traceability_audit.py after modeling/readiness plans.",
    )
    env_audit = read_csv_dicts(RESULT_DIR / "python_environment_audit.csv")
    env_complete = sum(1 for row in env_audit if row.get("status") == "complete")
    env_incomplete = sum(1 for row in env_audit if row.get("status") != "complete")
    packages_missing = sum(1 for row in read_csv_dicts(TEMP_DIR / "python_package_inventory.csv") if row.get("installed") != "1")
    add(
        rows,
        "evidence",
        "Python environment/package audit has been recorded",
        status(counts["python_package_inventory"] > 0 and counts["python_environment_audit"] > 0 and counts["python_environment_summary"] > 0),
        f"package_rows={counts['python_package_inventory']}; audit_rows={counts['python_environment_audit']}; summary_rows={counts['python_environment_summary']}; audit_complete={env_complete}; audit_incomplete={env_incomplete}; tracked_packages_missing={packages_missing}",
        "" if counts["python_package_inventory"] > 0 and counts["python_environment_audit"] > 0 and counts["python_environment_summary"] > 0 else "Run script/28_audit_python_environment.py.",
    )
    add(rows, "evidence", "Metadata schema inventory is populated", status(counts["schema_studies"] > 0 and counts["schema_files"] > 0 and counts["metadata_variables"] > 0), f"studies={counts['schema_studies']}; files={counts['schema_files']}; variables={counts['metadata_variables']}")

    map_counts = []
    for path in sorted(TEMP_DIR.glob("variable_map_*.csv")):
        map_counts.append((path.name, row_count(path)))
    total_maps = sum(count for _, count in map_counts)
    add(rows, "evidence", "Variable maps are populated", status(total_maps > 0), f"total rows={total_maps}; " + "; ".join(f"{name}={count}" for name, count in map_counts), "" if total_maps > 0 else "Run script/03_inspect_raw_schemas.py after metadata acquisition.")

    raw_gate = counts["raw_files"] > 0 and counts["raw_variables"] > 0
    add(
        rows,
        "raw_microdata_gate",
        "At least one raw tabular microdata file has been inspected",
        status(raw_gate),
        f"raw_file_inventory rows={counts['raw_files']}; raw_variable_catalog rows={counts['raw_variables']}",
        "" if raw_gate else "Manual raw files must be placed in temp/raw_downloads and inspected before harmonization.",
    )


def validate_completion_and_guardrails(rows: list[dict[str, Any]]) -> None:
    completion = read_csv_dicts(RESULT_DIR / "completion_criteria_audit.csv")
    complete = sum(1 for row in completion if row.get("status") == "complete")
    incomplete = sum(1 for row in completion if row.get("status") == "incomplete")
    add(rows, "completion_criteria", "Completion criteria audit exists and is internally counted", status(bool(completion)), f"complete={complete}; incomplete={incomplete}; rows={len(completion)}")

    registry = read_csv_dicts(RESULT_DIR / "promoted_country_wave_registry.csv")
    promoted_registry_rows = sum(1 for row in registry if row.get("analysis_ready_status") == "promoted_analysis_ready")
    data_dataset_files = [
        path for path in DATA_DIR.rglob("*")
        if path.is_file() and path.name not in {"README.md", ".gitkeep"}
    ]
    unpromoted_data_ok = promoted_registry_rows > 0 or len(data_dataset_files) == 0
    add(
        rows,
        "guardrails",
        "No unpromoted dataset files remain in `data/` while the registry has zero promoted rows",
        "complete" if unpromoted_data_ok else "failed",
        f"promoted_registry_rows={promoted_registry_rows}; data_dataset_files={len(data_dataset_files)}; data_readme={(DATA_DIR / 'README.md').exists()}; files={'; '.join(str(path.relative_to(TEMP_DIR.parent)) for path in data_dataset_files[:8])}",
        "" if unpromoted_data_ok else "Run script/127_enforce_promoted_data_gate.py and keep diagnostic data under temp/diagnostic_data_quarantine/current/.",
    )

    final_text = (REPORT_DIR / "final_report.md").read_text(encoding="utf-8", errors="replace") if (REPORT_DIR / "final_report.md").exists() else ""
    rejected_text = (TEMP_DIR / "rejected_designs.md").read_text(encoding="utf-8", errors="replace") if (TEMP_DIR / "rejected_designs.md").exists() else ""
    final_lower = final_text.lower()
    no_overclaim = (
        "no go for sdg 3.8.2" in final_lower
        and "climate linkage" in final_lower
        and "predictive ml" in final_lower
        and "causal ml/policy learning" in rejected_text.lower()
    )
    add(
        rows,
        "guardrails",
        "Reports preserve no-go language and reject premature causal ML",
        status(no_overclaim),
        "final_report contains no-go language for SDG/access/climate/modeling; rejected_designs contains causal ML/policy learning gate" if no_overclaim else "required no-go/rejection text not found",
        "" if no_overclaim else "Regenerate reports and rejected-design log.",
    )


def write_report(rows: list[dict[str, Any]]) -> None:
    by_status: dict[str, int] = {}
    for row in rows:
        by_status[row["status"]] = by_status.get(row["status"], 0) + 1
    lines = [
        "# Workspace Validation",
        "",
        "Status: objective-level validation run completed. This is an audit of the workspace state, not a claim that the empirical project is complete.",
        "",
        "## Status Counts",
        "",
        "| Status | Count |",
        "|---|---:|",
    ]
    for key, count in sorted(by_status.items()):
        lines.append(f"| {key} | {count} |")
    lines.extend(["", "## Incomplete Or Failed Items", "", "| Category | Requirement | Status | Evidence | Gap |", "|---|---|---|---|---|"])
    for row in rows:
        if row["status"] != "complete":
            lines.append(f"| {row['category']} | {row['requirement']} | {row['status']} | {row['evidence']} | {row['gap']} |")
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    ensure_dirs()
    rows: list[dict[str, Any]] = []
    validate_dirs(rows)
    validate_required_files(rows)
    validate_artifacts(rows)
    validate_completion_and_guardrails(rows)
    write_csv(AUDIT_PATH, rows, AUDIT_COLUMNS)
    write_report(rows)
    complete = sum(1 for row in rows if row["status"] == "complete")
    incomplete = len(rows) - complete
    append_log(TEMP_DIR / "audit_log.md", f"Workspace validation complete={complete} incomplete_or_failed={incomplete}.")
    print(f"Workspace validation complete={complete} incomplete_or_failed={incomplete}.")


if __name__ == "__main__":
    main()
