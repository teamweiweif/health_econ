from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path
from typing import Any

from common import DATA_DIR, REPORT_DIR, RESULT_DIR, SCRIPT_DIR, TEMP_DIR, append_log, ensure_dirs, sha256_file, write_csv


BUNDLE_PATH = RESULT_DIR / "direct_read_audit_bundle.csv"
MANIFEST_PATH = RESULT_DIR / "direct_read_artifact_manifest.csv"
SUMMARY_PATH = RESULT_DIR / "direct_read_audit_bundle_summary.csv"
REPORT_PATH = REPORT_DIR / "direct_read_audit_bundle.md"

BUNDLE_COLUMNS = ["section", "item", "status", "value", "evidence_artifacts", "interpretation"]
MANIFEST_COLUMNS = ["artifact_group", "relative_path", "exists", "bytes", "rows", "sha256", "role", "current_status"]
SUMMARY_COLUMNS = ["metric", "value", "interpretation"]
BINARY_ROWLESS_SUFFIXES = {".xlsx", ".xls", ".zip", ".rar", ".7z", ".dta", ".sav", ".por", ".sas7bdat", ".xpt"}


CURATED_ARTIFACTS = [
    ("entry_reports", "README.md", "GitHub repository entry point and current status"),
    ("entry_reports", "report/WEB_GPT_START_HERE.md", "short Web GPT starting point"),
    ("entry_reports", "report/README.md", "human entry point and reproduction instructions"),
    ("entry_reports", "report/final_report.md", "current empirical judgment"),
    ("entry_reports", "report/source_audit.md", "official-source verification"),
    ("entry_reports", "report/objective_traceability_audit.md", "objective-to-artifact evidence map"),
    ("entry_reports", "report/workspace_validation.md", "workspace validation status"),
    ("entry_reports", "report/empirical_readiness_dashboard.md", "consolidated empirical readiness narrative"),
    ("entry_reports", "report/direct_read_audit_bundle.md", "single direct-read audit bundle"),
    ("dataset_promotion", "report/country_wave_promotion_registry.md", "dataset-promotion registry report and modeling gate"),
    ("dataset_promotion", "result/promoted_country_wave_registry.csv", "fail-closed country-wave promotion registry"),
    ("dataset_promotion", "result/country_wave_promotion_gate_audit.csv", "country-wave promotion gate audit"),
    ("dataset_promotion", "result/country_wave_promotion_summary.csv", "country-wave promotion threshold summary"),
    ("dataset_promotion", "result/priority_country_wave_download_queue.csv", "priority-country raw package download and promotion queue"),
    ("dataset_promotion", "report/priority_promotion_acquisition_plan.md", "priority-first raw acquisition and verification plan"),
    ("dataset_promotion", "result/priority_promotion_acquisition_wave_plan.csv", "priority 10-wave raw acquisition wave plan"),
    ("dataset_promotion", "result/priority_promotion_acquisition_file_queue.csv", "top core files/modules to verify after priority raw downloads"),
    ("dataset_promotion", "result/priority_promotion_acquisition_summary.csv", "priority acquisition plan summary"),
    ("dataset_promotion", "report/priority_official_raw_access_probe.md", "priority-batch official raw access probe report"),
    ("dataset_promotion", "temp/priority_official_raw_access_probe.csv", "priority-batch official raw access probe rows"),
    ("dataset_promotion", "result/priority_official_raw_access_summary.csv", "priority-batch official raw access summary"),
    ("dataset_promotion", "report/priority_raw_intake_gate.md", "priority raw package intake gate report"),
    ("dataset_promotion", "temp/priority_raw_intake_gate.csv", "priority raw package intake gate rows"),
    ("dataset_promotion", "temp/priority_raw_file_targets.csv", "priority raw file target gate rows"),
    ("dataset_promotion", "result/priority_raw_intake_gate_summary.csv", "priority raw package intake gate summary"),
    ("dataset_promotion", "report/priority_archive_member_preflight.md", "priority archive/direct-file completeness preflight report"),
    ("dataset_promotion", "temp/priority_archive_member_inventory.csv", "priority archive member inventory"),
    ("dataset_promotion", "temp/priority_archive_completeness_matrix.csv", "priority direct/archive file target completeness matrix"),
    ("dataset_promotion", "result/priority_archive_member_preflight_summary.csv", "priority archive member preflight summary"),
    ("dataset_promotion", "report/priority_climate_linkage_preflight.md", "priority climate linkage preflight report"),
    ("dataset_promotion", "temp/priority_climate_linkage_preflight.csv", "priority climate linkage preflight rows"),
    ("dataset_promotion", "temp/priority_climate_linkage_requirements.csv", "priority climate linkage requirement rows"),
    ("dataset_promotion", "result/priority_climate_linkage_preflight_summary.csv", "priority climate linkage preflight summary"),
    ("dataset_promotion", "report/priority_raw_verification_workbook.md", "priority raw verification workbook report"),
    ("dataset_promotion", "result/priority_dataset_verification_gate.csv", "priority dataset verification gate rows"),
    ("dataset_promotion", "temp/priority_promotion_verification_checklist.csv", "priority objective-aligned verification checklist"),
    ("dataset_promotion", "temp/priority_concept_verification_template.csv", "priority concept-level raw verification template"),
    ("dataset_promotion", "temp/priority_variable_verification_template.csv", "priority variable-level raw verification template"),
    ("dataset_promotion", "result/priority_raw_verification_workbook_summary.csv", "priority raw verification workbook summary"),
    ("dataset_promotion", "report/priority_manual_verification_decision_gate.md", "priority manual verification decision gate report"),
    ("dataset_promotion", "temp/priority_manual_verification_decision_gate.csv", "priority dataset manual verification decision rows"),
    ("dataset_promotion", "temp/priority_manual_requirement_decision_audit.csv", "priority requirement manual verification audit rows"),
    ("dataset_promotion", "temp/priority_manual_concept_decision_audit.csv", "priority concept manual verification audit rows"),
    ("dataset_promotion", "temp/priority_manual_variable_decision_audit.csv", "priority variable manual verification audit rows"),
    ("dataset_promotion", "result/priority_manual_verification_decision_summary.csv", "priority manual verification decision summary"),
    ("dataset_promotion", "report/priority_raw_package_receipt_ledger.md", "priority raw package receipt ledger report"),
    ("dataset_promotion", "temp/priority_raw_package_receipt_ledger.csv", "priority dataset-level raw package receipt ledger"),
    ("dataset_promotion", "temp/priority_raw_package_file_manifest.csv", "priority original package/file checksum manifest"),
    ("dataset_promotion", "temp/priority_raw_package_missing_targets.csv", "priority raw package missing target rows"),
    ("dataset_promotion", "result/priority_raw_package_receipt_summary.csv", "priority raw package receipt summary"),
    ("dataset_promotion", "report/priority_official_download_dossier.md", "priority official download dossier report"),
    ("dataset_promotion", "temp/priority_official_download_dossier.csv", "priority dataset-level official download dossier"),
    ("dataset_promotion", "temp/priority_official_full_file_inventory.csv", "priority full official metadata file inventory"),
    ("dataset_promotion", "temp/priority_official_documentation_links.csv", "priority official documentation and access workflow links"),
    ("dataset_promotion", "result/priority_official_download_dossier_summary.csv", "priority official download dossier summary"),
    ("dataset_promotion", "report/priority_public_documentation_receipt.md", "priority public documentation receipt report"),
    ("dataset_promotion", "temp/priority_public_documentation_receipt.csv", "priority public documentation resource receipt"),
    ("dataset_promotion", "temp/priority_public_documentation_dataset_receipt.csv", "priority dataset-level public documentation receipt"),
    ("dataset_promotion", "result/priority_public_documentation_receipt_summary.csv", "priority public documentation receipt summary"),
    ("dataset_promotion", "report/priority_official_metadata_evidence_extract.md", "priority official DDI/XML metadata evidence report"),
    ("dataset_promotion", "temp/priority_official_metadata_variable_evidence.csv", "priority official metadata candidate-variable evidence"),
    ("dataset_promotion", "temp/priority_official_metadata_category_evidence.csv", "priority official metadata category/value-label evidence"),
    ("dataset_promotion", "temp/priority_official_metadata_dataset_evidence.csv", "priority official metadata dataset-level evidence"),
    ("dataset_promotion", "result/priority_official_metadata_evidence_summary.csv", "priority official metadata evidence summary"),
    ("dataset_promotion", "report/priority_credentialed_raw_acquisition_ledger.md", "priority credentialed raw acquisition ledger report"),
    ("dataset_promotion", "temp/priority_credentialed_raw_acquisition_ledger.csv", "priority credentialed raw acquisition dataset ledger"),
    ("dataset_promotion", "temp/priority_credentialed_raw_full_file_manifest.csv", "priority credentialed raw full official file manifest"),
    ("dataset_promotion", "temp/priority_credentialed_raw_core_file_checklist.csv", "priority credentialed raw core file checklist"),
    ("dataset_promotion", "result/priority_credentialed_raw_acquisition_summary.csv", "priority credentialed raw acquisition summary"),
    ("dataset_promotion", "report/priority_official_endpoint_matrix.md", "priority official endpoint matrix report"),
    ("dataset_promotion", "temp/priority_official_endpoint_matrix.csv", "priority official endpoint matrix rows"),
    ("dataset_promotion", "temp/priority_official_endpoint_dataset_matrix.csv", "priority official endpoint dataset matrix"),
    ("dataset_promotion", "result/priority_official_endpoint_matrix_summary.csv", "priority official endpoint matrix summary"),
    ("dataset_promotion", "report/priority_core_file_endpoint_matrix.md", "priority core file endpoint matrix report"),
    ("dataset_promotion", "temp/priority_core_file_endpoint_matrix.csv", "priority core file endpoint matrix rows"),
    ("dataset_promotion", "temp/priority_core_file_endpoint_dataset_matrix.csv", "priority core file endpoint dataset matrix"),
    ("dataset_promotion", "result/priority_core_file_endpoint_matrix_summary.csv", "priority core file endpoint matrix summary"),
    ("dataset_promotion", "report/priority_threshold_acquisition_campaign.md", "priority threshold acquisition campaign report"),
    ("dataset_promotion", "temp/priority_threshold_acquisition_campaign.csv", "priority threshold acquisition campaign queue"),
    ("dataset_promotion", "temp/priority_threshold_country_coverage.csv", "priority threshold country coverage"),
    ("dataset_promotion", "result/priority_threshold_acquisition_campaign_summary.csv", "priority threshold acquisition campaign summary"),
    ("dataset_promotion", "report/priority_first_pass_variable_review_queue.md", "priority first-pass variable review queue report"),
    ("dataset_promotion", "temp/priority_first_pass_variable_review_queue.csv", "priority first-pass selected variable review queue"),
    ("dataset_promotion", "temp/priority_first_pass_requirement_coverage.csv", "priority first-pass requirement coverage"),
    ("dataset_promotion", "result/priority_first_pass_variable_review_summary.csv", "priority first-pass variable review summary"),
    ("dataset_promotion", "report/priority_download_execution_packet.md", "priority manual download execution packet report"),
    ("dataset_promotion", "temp/priority_download_execution_packet.csv", "priority manual download execution packet"),
    ("dataset_promotion", "temp/priority_download_file_acceptance_matrix.csv", "priority core-file acceptance matrix"),
    ("dataset_promotion", "result/priority_download_execution_packet_summary.csv", "priority manual download execution packet summary"),
    ("dataset_promotion", "report/priority_lsms_isa_alignment_audit.md", "priority LSMS/ISA family-alignment audit report"),
    ("dataset_promotion", "temp/priority_lsms_isa_alignment_audit.csv", "priority LSMS/ISA current-campaign alignment audit"),
    ("dataset_promotion", "temp/priority_lsms_isa_replacement_candidates.csv", "priority Malawi/Uganda LSMS/ISA replacement candidates"),
    ("dataset_promotion", "result/priority_lsms_isa_alignment_summary.csv", "priority LSMS/ISA alignment summary"),
    ("dataset_promotion", "report/priority_lsms_isa_refocused_acquisition_queue.md", "priority LSMS/ISA refocused acquisition queue report"),
    ("dataset_promotion", "result/priority_lsms_isa_refocused_wave_plan.csv", "priority LSMS/ISA refocused selected wave plan"),
    ("dataset_promotion", "temp/priority_lsms_isa_refocused_acquisition_queue.csv", "priority LSMS/ISA refocused manual acquisition queue"),
    ("dataset_promotion", "temp/priority_lsms_isa_refocused_requirement_matrix.csv", "priority LSMS/ISA refocused requirement matrix"),
    ("dataset_promotion", "result/priority_lsms_isa_refocused_acquisition_summary.csv", "priority LSMS/ISA refocused acquisition summary"),
    ("dataset_promotion", "report/priority_lsms_isa_public_documentation_receipt.md", "priority LSMS/ISA public documentation receipt report"),
    ("dataset_promotion", "temp/priority_lsms_isa_public_documentation_receipt.csv", "priority LSMS/ISA public documentation resource receipt"),
    ("dataset_promotion", "temp/priority_lsms_isa_public_documentation_dataset_receipt.csv", "priority LSMS/ISA public documentation dataset receipt"),
    ("dataset_promotion", "temp/priority_lsms_isa_public_documentation_catalog_digest.csv", "priority LSMS/ISA compact official catalog digest"),
    ("dataset_promotion", "temp/priority_lsms_isa_public_documentation_file_inventory.csv", "priority LSMS/ISA official DDI file inventory"),
    ("dataset_promotion", "result/priority_lsms_isa_public_documentation_receipt_summary.csv", "priority LSMS/ISA public documentation receipt summary"),
    ("dataset_promotion", "report/priority_lsms_isa_variable_evidence_matrix.md", "priority LSMS/ISA official variable evidence matrix report"),
    ("dataset_promotion", "temp/priority_lsms_isa_variable_evidence_matrix.csv", "priority LSMS/ISA candidate variable evidence matrix"),
    ("dataset_promotion", "temp/priority_lsms_isa_requirement_variable_coverage.csv", "priority LSMS/ISA requirement variable coverage"),
    ("dataset_promotion", "temp/priority_lsms_isa_concept_file_shortlist.csv", "priority LSMS/ISA concept file shortlist"),
    ("dataset_promotion", "result/priority_lsms_isa_variable_evidence_summary.csv", "priority LSMS/ISA official variable evidence summary"),
    ("dataset_promotion", "report/priority_lsms_isa_raw_package_intake_packet.md", "priority LSMS/ISA raw package intake packet report"),
    ("dataset_promotion", "temp/priority_lsms_isa_raw_package_intake_ledger.csv", "priority LSMS/ISA raw package intake ledger"),
    ("dataset_promotion", "temp/priority_lsms_isa_raw_package_file_manifest.csv", "priority LSMS/ISA raw package file manifest"),
    ("dataset_promotion", "temp/priority_lsms_isa_raw_package_acceptance_matrix.csv", "priority LSMS/ISA raw package acceptance matrix"),
    ("dataset_promotion", "result/priority_lsms_isa_raw_package_intake_summary.csv", "priority LSMS/ISA raw package intake summary"),
    ("dataset_promotion", "report/priority_lsms_isa_archive_member_preflight.md", "priority LSMS/ISA archive/direct-file preflight report"),
    ("dataset_promotion", "temp/priority_lsms_isa_archive_member_preflight.csv", "priority LSMS/ISA dataset archive/direct-file preflight"),
    ("dataset_promotion", "temp/priority_lsms_isa_archive_member_manifest.csv", "priority LSMS/ISA archive member manifest"),
    ("dataset_promotion", "temp/priority_lsms_isa_direct_file_preflight.csv", "priority LSMS/ISA direct original file preflight"),
    ("dataset_promotion", "temp/priority_lsms_isa_archive_requirement_preflight.csv", "priority LSMS/ISA requirement archive preflight"),
    ("dataset_promotion", "result/priority_lsms_isa_archive_member_preflight_summary.csv", "priority LSMS/ISA archive/direct-file preflight summary"),
    ("dataset_promotion", "report/priority_lsms_isa_raw_value_verification_workbook.md", "priority LSMS/ISA raw value verification workbook report"),
    ("dataset_promotion", "temp/priority_lsms_isa_raw_value_requirement_workbook.csv", "priority LSMS/ISA requirement raw value verification workbook"),
    ("dataset_promotion", "temp/priority_lsms_isa_raw_value_variable_workbook.csv", "priority LSMS/ISA variable raw value verification workbook"),
    ("dataset_promotion", "temp/priority_lsms_isa_raw_value_file_workbook.csv", "priority LSMS/ISA file raw value verification workbook"),
    ("dataset_promotion", "result/priority_lsms_isa_raw_value_verification_workbook_summary.csv", "priority LSMS/ISA raw value verification workbook summary"),
    ("dataset_promotion", "report/priority_lsms_isa_received_raw_schema_audit.md", "priority LSMS/ISA received raw schema audit report"),
    ("dataset_promotion", "temp/priority_lsms_isa_received_raw_schema_file_inventory.csv", "priority LSMS/ISA received raw schema file inventory"),
    ("dataset_promotion", "temp/priority_lsms_isa_received_raw_variable_schema.csv", "priority LSMS/ISA received raw variable schema"),
    ("dataset_promotion", "temp/priority_lsms_isa_received_raw_requirement_evidence.csv", "priority LSMS/ISA received raw requirement evidence"),
    ("dataset_promotion", "result/priority_lsms_isa_received_raw_schema_audit_summary.csv", "priority LSMS/ISA received raw schema audit summary"),
    ("dataset_promotion", "report/priority_lsms_isa_received_raw_value_profile.md", "priority LSMS/ISA received raw value profile report"),
    ("dataset_promotion", "temp/priority_lsms_isa_received_raw_value_profile.csv", "priority LSMS/ISA received raw candidate variable value profile"),
    ("dataset_promotion", "temp/priority_lsms_isa_received_raw_key_design_geography_profile.csv", "priority LSMS/ISA received raw key design geography profile"),
    ("dataset_promotion", "temp/priority_lsms_isa_received_raw_value_requirement_profile.csv", "priority LSMS/ISA received raw requirement value profile"),
    ("dataset_promotion", "result/priority_lsms_isa_received_raw_value_profile_summary.csv", "priority LSMS/ISA received raw value profile summary"),
    ("dataset_promotion", "report/priority_lsms_isa_received_raw_semantics_review.md", "priority LSMS/ISA received raw semantics review report"),
    ("dataset_promotion", "temp/priority_lsms_isa_received_raw_semantics_variable_review.csv", "priority LSMS/ISA received raw variable semantics review"),
    ("dataset_promotion", "temp/priority_lsms_isa_received_raw_semantics_requirement_review.csv", "priority LSMS/ISA received raw requirement semantics review"),
    ("dataset_promotion", "temp/priority_lsms_isa_received_raw_documentation_scope_review.csv", "priority LSMS/ISA received raw documentation scope review"),
    ("dataset_promotion", "result/priority_lsms_isa_received_raw_semantics_review_summary.csv", "priority LSMS/ISA received raw semantics review summary"),
    ("dataset_promotion", "report/mwi2004_raw_requirement_verification.md", "Malawi 2004 focused raw requirement verification report"),
    ("dataset_promotion", "temp/mwi2004_raw_requirement_evidence.csv", "Malawi 2004 focused requirement-level raw-backed evidence"),
    ("dataset_promotion", "temp/mwi2004_raw_module_join_evidence.csv", "Malawi 2004 focused key and module join evidence"),
    ("dataset_promotion", "temp/mwi2004_raw_financial_oop_profile.csv", "Malawi 2004 focused financial-protection and OOP profile"),
    ("dataset_promotion", "result/mwi2004_raw_requirement_verification_summary.csv", "Malawi 2004 focused raw requirement verification summary"),
    ("dataset_promotion", "report/mwi2004_requirement_acceptance_decisions.md", "Malawi 2004 focused requirement acceptance decision report"),
    ("dataset_promotion", "result/mwi2004_requirement_acceptance_decisions.csv", "Malawi 2004 requirement-level accept/block decision table"),
    ("dataset_promotion", "temp/mwi2004_requirement_acceptance_metrics.csv", "Malawi 2004 aggregate acceptance metrics without raw IDs"),
    ("dataset_promotion", "result/mwi2004_requirement_acceptance_summary.csv", "Malawi 2004 requirement acceptance summary"),
    ("dataset_promotion", "report/mwi2004_financial_protection_construction_policy.md", "Malawi 2004 financial-protection construction policy report"),
    ("dataset_promotion", "result/mwi2004_financial_protection_construction_policy.csv", "Malawi 2004 aggregate financial-protection construction policy"),
    ("dataset_promotion", "result/mwi2004_financial_protection_construction_policy_summary.csv", "Malawi 2004 financial-protection construction policy summary"),
    ("dataset_promotion", "report/mwi2004_sdg382_discretionary_budget_parameter_audit.md", "Malawi 2004 SDG 3.8.2 discretionary-budget parameter audit report"),
    ("dataset_promotion", "result/mwi2004_sdg382_discretionary_budget_parameter_audit.csv", "Malawi 2004 SDG 3.8.2 parameter audit table"),
    ("dataset_promotion", "result/mwi2004_sdg382_discretionary_budget_parameter_summary.csv", "Malawi 2004 SDG 3.8.2 parameter audit summary"),
    ("dataset_promotion", "report/mwi2004_sdg382_external_parameter_source_ledger.md", "Malawi 2004 SDG 3.8.2 external parameter source ledger report"),
    ("dataset_promotion", "result/mwi2004_sdg382_external_parameter_source_ledger.csv", "Malawi 2004 SDG 3.8.2 external parameter source ledger"),
    ("dataset_promotion", "result/mwi2004_sdg382_external_parameter_candidate_summary.csv", "Malawi 2004 SDG 3.8.2 external parameter candidate summary"),
    ("dataset_promotion", "report/mwi2004_sdg382_candidate_classification_precheck.md", "Malawi 2004 SDG 3.8.2 candidate classification precheck report"),
    ("dataset_promotion", "result/mwi2004_sdg382_candidate_classification_precheck.csv", "Malawi 2004 SDG 3.8.2 candidate classification precheck"),
    ("dataset_promotion", "result/mwi2004_sdg382_candidate_classification_precheck_summary.csv", "Malawi 2004 SDG 3.8.2 candidate classification precheck summary"),
    ("dataset_promotion", "report/mwi2004_sdg382_official_denominator_rule_audit.md", "Malawi 2004 SDG 3.8.2 official denominator rule audit report"),
    ("dataset_promotion", "result/mwi2004_sdg382_official_denominator_rule_audit.csv", "Malawi 2004 SDG 3.8.2 official denominator rule audit"),
    ("dataset_promotion", "result/mwi2004_sdg382_official_denominator_rule_summary.csv", "Malawi 2004 SDG 3.8.2 official denominator rule summary"),
    ("dataset_promotion", "report/mwi2004_timing_geography_linkage_policy.md", "Malawi 2004 timing/geography linkage policy report"),
    ("dataset_promotion", "result/mwi2004_timing_geography_linkage_policy.csv", "Malawi 2004 aggregate timing/geography linkage policy"),
    ("dataset_promotion", "result/mwi2004_timing_geography_linkage_policy_summary.csv", "Malawi 2004 timing/geography linkage policy summary"),
    ("dataset_promotion", "report/mwi2004_chirps_admin2_route_policy.md", "Malawi 2004 CHIRPS ADM2 route policy report"),
    ("dataset_promotion", "result/mwi2004_chirps_admin2_route_policy.csv", "Malawi 2004 CHIRPS ADM2 route policy table"),
    ("dataset_promotion", "result/mwi2004_chirps_admin2_crosswalk.csv", "Malawi 2004 raw district to ADM2 boundary crosswalk"),
    ("dataset_promotion", "result/mwi2004_chirps_admin2_required_downloads.csv", "Malawi 2004 required CHIRPS monthly download manifest"),
    ("dataset_promotion", "result/mwi2004_chirps_admin2_route_policy_summary.csv", "Malawi 2004 CHIRPS ADM2 route policy summary"),
    ("dataset_promotion", "report/mwi2004_chirps_admin2_extraction_validation.md", "Malawi 2004 CHIRPS ADM2 extraction validation report"),
    ("dataset_promotion", "result/mwi2004_chirps_admin2_download_audit.csv", "Malawi 2004 CHIRPS download audit"),
    ("dataset_promotion", "result/mwi2004_chirps_admin2_district_month_exposure.csv", "Malawi 2004 CHIRPS ADM2 district-month exposure table"),
    ("dataset_promotion", "result/mwi2004_chirps_admin2_lag_window_exposure.csv", "Malawi 2004 CHIRPS district-interview-month lag-window exposure table"),
    ("dataset_promotion", "result/mwi2004_chirps_admin2_extraction_validation.csv", "Malawi 2004 CHIRPS ADM2 extraction validation table"),
    ("dataset_promotion", "result/mwi2004_chirps_admin2_extraction_summary.csv", "Malawi 2004 CHIRPS ADM2 extraction summary"),
    ("dataset_promotion", "report/mwi2004_health_access_label_skip_decisions.md", "Malawi 2004 health/access label and skip decision report"),
    ("dataset_promotion", "result/mwi2004_health_access_label_skip_decisions.csv", "Malawi 2004 health/access value-label construct decisions"),
    ("dataset_promotion", "temp/mwi2004_health_access_skip_consistency_metrics.csv", "Malawi 2004 health/access aggregate skip consistency metrics"),
    ("dataset_promotion", "result/mwi2004_health_access_label_skip_summary.csv", "Malawi 2004 health/access label-skip summary"),
    ("dataset_promotion", "report/mwi2004_health_exception_audit.md", "Malawi 2004 health person-key and skip exception audit report"),
    ("dataset_promotion", "result/mwi2004_health_exception_audit.csv", "Malawi 2004 aggregate health exception audit without raw IDs"),
    ("dataset_promotion", "result/mwi2004_health_exception_summary.csv", "Malawi 2004 health exception audit summary"),
    ("dataset_promotion", "report/mwi2004_health_access_construction_policy.md", "Malawi 2004 candidate health/access construction policy report"),
    ("dataset_promotion", "result/mwi2004_health_access_construction_policy.csv", "Malawi 2004 aggregate candidate health/access construction policy"),
    ("dataset_promotion", "result/mwi2004_health_access_construction_policy_summary.csv", "Malawi 2004 candidate health/access construction policy summary"),
    ("dataset_promotion", "report/mwi2004_access_person_key_resolution_policy.md", "Malawi 2004 access person-key resolution policy report"),
    ("dataset_promotion", "result/mwi2004_access_person_key_resolution_policy.csv", "Malawi 2004 aggregate access person-key resolution policy"),
    ("dataset_promotion", "result/mwi2004_access_person_key_resolution_policy_summary.csv", "Malawi 2004 access person-key resolution policy summary"),
    ("dataset_promotion", "report/mwi2004_missing_units_recall_skip_policy.md", "Malawi 2004 missing, units, recall, and skip policy report"),
    ("dataset_promotion", "result/mwi2004_missing_units_recall_skip_policy.csv", "Malawi 2004 aggregate missing, units, recall, and skip policy"),
    ("dataset_promotion", "result/mwi2004_missing_units_recall_skip_policy_summary.csv", "Malawi 2004 missing, units, recall, and skip policy summary"),
    ("dataset_promotion", "report/mwi2004_promoted_household_climate_dataset.md", "Malawi 2004 promoted household-climate dataset synthesis report"),
    ("dataset_promotion", "result/mwi2004_promoted_household_climate_dataset_summary.csv", "Malawi 2004 promoted household-climate dataset summary"),
    ("dataset_promotion", "result/mwi2004_promoted_household_climate_dataset_dictionary.csv", "Malawi 2004 promoted household-climate dataset dictionary"),
    ("dataset_promotion", "result/mwi2004_promoted_household_climate_dataset_validation.csv", "Malawi 2004 promoted household-climate dataset validation"),
    ("dataset_promotion", "report/priority_lsms_isa_raw_package_receipt_checklist.md", "priority LSMS/ISA raw package receipt checklist report"),
    ("dataset_promotion", "temp/priority_lsms_isa_raw_package_receipt_checklist.csv", "priority LSMS/ISA dataset raw package receipt checklist"),
    ("dataset_promotion", "temp/priority_lsms_isa_raw_package_requirement_receipt_checklist.csv", "priority LSMS/ISA requirement raw package receipt checklist"),
    ("dataset_promotion", "result/priority_lsms_isa_raw_package_receipt_checklist_summary.csv", "priority LSMS/ISA raw package receipt checklist summary"),
    ("dataset_promotion", "report/priority_lsms_isa_credentialed_raw_acquisition_workbench.md", "priority LSMS/ISA credentialed raw acquisition workbench report"),
    ("dataset_promotion", "temp/priority_lsms_isa_credentialed_raw_acquisition_workbench.csv", "priority LSMS/ISA credentialed raw acquisition workbench"),
    ("dataset_promotion", "temp/priority_lsms_isa_credentialed_raw_full_file_manifest.csv", "priority LSMS/ISA credentialed raw full file manifest"),
    ("dataset_promotion", "temp/priority_lsms_isa_credentialed_raw_core_file_checklist.csv", "priority LSMS/ISA credentialed raw core file checklist"),
    ("dataset_promotion", "result/priority_lsms_isa_credentialed_raw_acquisition_workbench_summary.csv", "priority LSMS/ISA credentialed raw acquisition workbench summary"),
    ("dataset_promotion", "report/priority_lsms_isa_official_file_receipt_validator.md", "priority LSMS/ISA official file receipt validator report"),
    ("dataset_promotion", "temp/priority_lsms_isa_official_file_receipt_validation.csv", "priority LSMS/ISA official file receipt dataset validation"),
    ("dataset_promotion", "temp/priority_lsms_isa_official_file_receipt_file_match.csv", "priority LSMS/ISA official file receipt full-file match table"),
    ("dataset_promotion", "temp/priority_lsms_isa_official_file_receipt_core_match.csv", "priority LSMS/ISA official file receipt core-file match table"),
    ("dataset_promotion", "result/priority_lsms_isa_official_file_receipt_validator_summary.csv", "priority LSMS/ISA official file receipt validator summary"),
    ("dataset_promotion", "report/priority_lsms_isa_threshold_download_sequence.md", "priority LSMS/ISA threshold download sequence report"),
    ("dataset_promotion", "temp/priority_lsms_isa_threshold_download_sequence.csv", "priority LSMS/ISA threshold download sequence"),
    ("dataset_promotion", "temp/priority_lsms_isa_threshold_minimum_batch.csv", "priority LSMS/ISA threshold minimum batch"),
    ("dataset_promotion", "temp/priority_lsms_isa_threshold_country_coverage.csv", "priority LSMS/ISA threshold country coverage"),
    ("dataset_promotion", "result/priority_lsms_isa_threshold_download_sequence_summary.csv", "priority LSMS/ISA threshold download sequence summary"),
    ("dataset_promotion", "report/priority_lsms_isa_minimum_batch_raw_intake_guide.md", "priority LSMS/ISA minimum-batch raw intake guide report"),
    ("dataset_promotion", "temp/priority_lsms_isa_minimum_batch_raw_intake_guide.csv", "priority LSMS/ISA minimum-batch raw intake guide"),
    ("dataset_promotion", "temp/priority_lsms_isa_minimum_batch_expected_file_manifest.csv", "priority LSMS/ISA minimum-batch expected file manifest"),
    ("dataset_promotion", "temp/priority_lsms_isa_minimum_batch_core_file_manifest.csv", "priority LSMS/ISA minimum-batch core file manifest"),
    ("dataset_promotion", "result/priority_lsms_isa_minimum_batch_raw_intake_guide_summary.csv", "priority LSMS/ISA minimum-batch raw intake guide summary"),
    ("dataset_promotion", "report/priority_lsms_isa_minimum_batch_endpoint_refresh.md", "priority LSMS/ISA minimum-batch endpoint refresh report"),
    ("dataset_promotion", "temp/priority_lsms_isa_minimum_batch_endpoint_refresh.csv", "priority LSMS/ISA minimum-batch endpoint refresh"),
    ("dataset_promotion", "temp/priority_lsms_isa_minimum_batch_endpoint_dataset_status.csv", "priority LSMS/ISA minimum-batch endpoint dataset status"),
    ("dataset_promotion", "result/priority_lsms_isa_minimum_batch_endpoint_refresh_summary.csv", "priority LSMS/ISA minimum-batch endpoint refresh summary"),
    ("dataset_promotion", "report/priority_lsms_isa_next_raw_package_action_packet.md", "priority LSMS/ISA next raw package action packet"),
    ("dataset_promotion", "temp/priority_lsms_isa_next_raw_package_action_queue.csv", "priority LSMS/ISA next raw package action queue"),
    ("dataset_promotion", "temp/priority_lsms_isa_next_raw_package_core_files.csv", "priority LSMS/ISA next raw package core files"),
    ("dataset_promotion", "result/priority_lsms_isa_next_raw_package_action_summary.csv", "priority LSMS/ISA next raw package action summary"),
    ("dataset_promotion", "report/priority_lsms_isa_incoming_raw_package_router.md", "priority LSMS/ISA incoming raw package router report"),
    ("dataset_promotion", "temp/priority_lsms_isa_incoming_raw_package_route_plan.csv", "priority LSMS/ISA incoming raw package route plan"),
    ("dataset_promotion", "temp/priority_lsms_isa_incoming_raw_package_route_candidates.csv", "priority LSMS/ISA incoming raw package route candidates"),
    ("dataset_promotion", "result/priority_lsms_isa_incoming_raw_package_router_summary.csv", "priority LSMS/ISA incoming raw package router summary"),
    ("dataset_promotion", "report/priority_lsms_isa_threshold_gap_control_panel.md", "priority LSMS/ISA threshold gap control panel report"),
    ("dataset_promotion", "temp/priority_lsms_isa_threshold_gap_download_panel.csv", "priority LSMS/ISA threshold gap download control panel"),
    ("dataset_promotion", "result/priority_lsms_isa_threshold_gap_country_panel.csv", "priority LSMS/ISA threshold gap country control panel"),
    ("dataset_promotion", "result/priority_lsms_isa_threshold_gap_control_panel_summary.csv", "priority LSMS/ISA threshold gap control panel summary"),
    ("dataset_promotion", "report/priority_lsms_isa_manual_download_packets.md", "priority LSMS/ISA manual download packet index report"),
    ("dataset_promotion", "temp/priority_lsms_isa_manual_download_packet_index.csv", "priority LSMS/ISA manual download packet index"),
    ("dataset_promotion", "temp/priority_lsms_isa_manual_download_packet_core_files.csv", "priority LSMS/ISA manual download packet core-file rows"),
    ("dataset_promotion", "result/priority_lsms_isa_manual_download_packet_summary.csv", "priority LSMS/ISA manual download packet summary"),
    ("dataset_promotion", "report/priority_lsms_isa_manual_download_progress_tracker.md", "priority LSMS/ISA manual download progress tracker report"),
    ("dataset_promotion", "temp/priority_lsms_isa_manual_download_progress_tracker.csv", "priority LSMS/ISA manual download progress tracker"),
    ("dataset_promotion", "result/priority_lsms_isa_manual_download_progress_summary.csv", "priority LSMS/ISA manual download progress summary"),
    ("dataset_promotion", "report/priority_lsms_isa_post_download_validation_runner.md", "priority LSMS/ISA post-download validation runner report"),
    ("dataset_promotion", "temp/priority_lsms_isa_post_download_validation_run_plan.csv", "priority LSMS/ISA post-download validation run plan"),
    ("dataset_promotion", "temp/priority_lsms_isa_post_download_validation_command_log.csv", "priority LSMS/ISA post-download validation command log"),
    ("dataset_promotion", "result/priority_lsms_isa_post_download_validation_runner_summary.csv", "priority LSMS/ISA post-download validation runner summary"),
    ("dataset_promotion", "report/priority_lsms_isa_manual_download_execution_board.md", "priority LSMS/ISA manual download execution board report"),
    ("dataset_promotion", "temp/priority_lsms_isa_manual_download_execution_board.csv", "priority LSMS/ISA manual download execution board"),
    ("dataset_promotion", "result/priority_lsms_isa_manual_download_execution_board_summary.csv", "priority LSMS/ISA manual download execution board summary"),
    ("dataset_promotion", "report/priority_lsms_isa_credentialed_download_handoff.md", "priority LSMS/ISA credentialed download handoff report"),
    ("dataset_promotion", "temp/priority_lsms_isa_credentialed_download_handoff_plan.csv", "priority LSMS/ISA credentialed download handoff plan"),
    ("dataset_promotion", "temp/priority_lsms_isa_credentialed_download_handoff_log.csv", "priority LSMS/ISA credentialed download handoff log"),
    ("dataset_promotion", "result/priority_lsms_isa_credentialed_download_handoff_summary.csv", "priority LSMS/ISA credentialed download handoff summary"),
    ("dataset_promotion", "report/priority_lsms_isa_resource_download_route_probe.md", "priority LSMS/ISA public resource route probe report"),
    ("dataset_promotion", "temp/priority_lsms_isa_resource_download_route_probe.csv", "priority LSMS/ISA public resource route probe rows"),
    ("dataset_promotion", "result/priority_lsms_isa_resource_download_route_probe_summary.csv", "priority LSMS/ISA public resource route probe summary"),
    ("dataset_promotion", "report/priority_lsms_isa_download_acceptance_matrix.md", "priority LSMS/ISA download acceptance matrix report"),
    ("dataset_promotion", "temp/priority_lsms_isa_download_acceptance_file_matrix.csv", "priority LSMS/ISA download acceptance expected-file matrix"),
    ("dataset_promotion", "temp/priority_lsms_isa_download_acceptance_requirement_matrix.csv", "priority LSMS/ISA download acceptance requirement matrix"),
    ("dataset_promotion", "result/priority_lsms_isa_download_acceptance_matrix_summary.csv", "priority LSMS/ISA download acceptance matrix summary"),
    ("dataset_promotion", "report/priority_lsms_isa_local_target_readmes.md", "priority LSMS/ISA local target readmes report"),
    ("dataset_promotion", "temp/priority_lsms_isa_local_target_readme_manifest.csv", "priority LSMS/ISA local target readme manifest"),
    ("dataset_promotion", "result/priority_lsms_isa_local_target_readme_summary.csv", "priority LSMS/ISA local target readme summary"),
    ("dataset_promotion", "report/priority_lsms_isa_minimum_batch_raw_value_queue.md", "priority LSMS/ISA minimum-batch raw-value review queue report"),
    ("dataset_promotion", "temp/priority_lsms_isa_minimum_batch_raw_value_requirement_queue.csv", "priority LSMS/ISA minimum-batch requirement raw-value queue"),
    ("dataset_promotion", "temp/priority_lsms_isa_minimum_batch_raw_value_variable_queue.csv", "priority LSMS/ISA minimum-batch variable raw-value queue"),
    ("dataset_promotion", "temp/priority_lsms_isa_minimum_batch_raw_value_file_queue.csv", "priority LSMS/ISA minimum-batch file raw-value queue"),
    ("dataset_promotion", "result/priority_lsms_isa_minimum_batch_raw_value_queue_summary.csv", "priority LSMS/ISA minimum-batch raw-value queue summary"),
    ("dataset_promotion", "report/priority_lsms_isa_target_folder_receipt_smoke_test.md", "priority LSMS/ISA target-folder receipt smoke-test report"),
    ("dataset_promotion", "temp/priority_lsms_isa_target_folder_receipt_status.csv", "priority LSMS/ISA target-folder receipt status"),
    ("dataset_promotion", "temp/priority_lsms_isa_target_folder_receipt_file_inventory.csv", "priority LSMS/ISA target-folder receipt file inventory"),
    ("dataset_promotion", "result/priority_lsms_isa_target_folder_receipt_smoke_test_summary.csv", "priority LSMS/ISA target-folder receipt smoke-test summary"),
    ("dataset_promotion", "report/priority_lsms_isa_threshold_replacement_plan.md", "priority LSMS/ISA threshold replacement plan report"),
    ("dataset_promotion", "temp/priority_lsms_isa_threshold_replacement_candidate_rank.csv", "priority LSMS/ISA threshold replacement candidate rank"),
    ("dataset_promotion", "temp/priority_lsms_isa_threshold_replacement_scenarios.csv", "priority LSMS/ISA threshold replacement scenarios"),
    ("dataset_promotion", "temp/priority_lsms_isa_threshold_replacement_strategy.csv", "priority LSMS/ISA threshold replacement strategy table"),
    ("dataset_promotion", "result/priority_lsms_isa_threshold_replacement_plan_summary.csv", "priority LSMS/ISA threshold replacement plan summary"),
    ("dataset_promotion", "report/priority_lsms_isa_minimum_batch_climate_linkage_review_queue.md", "priority LSMS/ISA minimum-batch climate linkage review queue report"),
    ("dataset_promotion", "temp/priority_lsms_isa_minimum_batch_climate_linkage_review_queue.csv", "priority LSMS/ISA minimum-batch climate linkage review queue"),
    ("dataset_promotion", "temp/priority_lsms_isa_minimum_batch_climate_linkage_file_queue.csv", "priority LSMS/ISA minimum-batch climate linkage file queue"),
    ("dataset_promotion", "result/priority_lsms_isa_minimum_batch_climate_linkage_review_summary.csv", "priority LSMS/ISA minimum-batch climate linkage review summary"),
    ("dataset_promotion", "report/priority_lsms_isa_local_stray_raw_package_locator.md", "priority LSMS/ISA local stray raw package locator report"),
    ("dataset_promotion", "temp/priority_lsms_isa_local_stray_raw_package_candidates.csv", "priority LSMS/ISA local stray raw package candidates"),
    ("dataset_promotion", "temp/priority_lsms_isa_local_stray_raw_package_route_plan.csv", "priority LSMS/ISA local stray raw package route plan"),
    ("dataset_promotion", "result/priority_lsms_isa_local_stray_raw_package_locator_summary.csv", "priority LSMS/ISA local stray raw package locator summary"),
    ("dataset_promotion", "report/priority_lsms_isa_promotion_gate_dashboard.md", "priority LSMS/ISA promotion gate dashboard report"),
    ("dataset_promotion", "temp/priority_lsms_isa_promotion_gate_dashboard.csv", "priority LSMS/ISA country-wave promotion gate dashboard"),
    ("dataset_promotion", "temp/priority_lsms_isa_promotion_gate_requirement_dashboard.csv", "priority LSMS/ISA requirement-level promotion gate dashboard"),
    ("dataset_promotion", "result/priority_lsms_isa_promotion_gate_dashboard_summary.csv", "priority LSMS/ISA promotion gate dashboard summary"),
    ("dataset_promotion", "report/priority_lsms_isa_minimum_batch_promotion_unlock_board.md", "priority LSMS/ISA minimum-batch promotion unlock board report"),
    ("dataset_promotion", "result/priority_lsms_isa_minimum_batch_promotion_unlock_board.csv", "priority LSMS/ISA minimum-batch promotion unlock board"),
    ("dataset_promotion", "result/priority_lsms_isa_minimum_batch_promotion_unlock_summary.csv", "priority LSMS/ISA minimum-batch promotion unlock summary"),
    ("dataset_promotion", "report/priority_lsms_isa_worldbank_session_bootstrap.md", "priority LSMS/ISA World Bank session bootstrap report"),
    ("dataset_promotion", "result/priority_lsms_isa_worldbank_session_bootstrap.csv", "priority LSMS/ISA World Bank session bootstrap rows"),
    ("dataset_promotion", "result/priority_lsms_isa_worldbank_session_bootstrap_summary.csv", "priority LSMS/ISA World Bank session bootstrap summary"),
    ("dataset_promotion", "report/priority_lsms_isa_credentialed_fetch_command_packet.md", "priority LSMS/ISA credentialed fetch command packet report"),
    ("dataset_promotion", "result/priority_lsms_isa_credentialed_fetch_command_packet.csv", "priority LSMS/ISA credentialed fetch command packet rows"),
    ("dataset_promotion", "result/priority_lsms_isa_credentialed_fetch_command_packet_summary.csv", "priority LSMS/ISA credentialed fetch command packet summary"),
    ("dataset_promotion", "report/priority_lsms_isa_browser_download_starter.md", "priority LSMS/ISA browser download starter report"),
    ("dataset_promotion", "result/priority_lsms_isa_browser_download_starter.csv", "priority LSMS/ISA browser download starter rows"),
    ("dataset_promotion", "result/priority_lsms_isa_browser_download_starter_summary.csv", "priority LSMS/ISA browser download starter summary"),
    ("dataset_promotion", "report/priority_lsms_isa_first_canary_runbook.md", "priority LSMS/ISA first canary download runbook report"),
    ("dataset_promotion", "result/priority_lsms_isa_first_canary_download_runbook.csv", "priority LSMS/ISA first canary download runbook rows"),
    ("dataset_promotion", "result/priority_lsms_isa_first_canary_core_file_checklist.csv", "priority LSMS/ISA first canary core file checklist"),
    ("dataset_promotion", "result/priority_lsms_isa_first_canary_requirement_gate_checklist.csv", "priority LSMS/ISA first canary requirement gate checklist"),
    ("dataset_promotion", "result/priority_lsms_isa_first_canary_runbook_summary.csv", "priority LSMS/ISA first canary runbook summary"),
    ("dataset_promotion", "report/priority_lsms_isa_local_raw_presence_audit.md", "priority LSMS/ISA local raw presence audit report"),
    ("dataset_promotion", "result/priority_lsms_isa_local_raw_presence_audit.csv", "priority LSMS/ISA local raw presence audit rows"),
    ("dataset_promotion", "result/priority_lsms_isa_local_nonregistry_raw_files.csv", "priority LSMS/ISA local nonregistry raw-like files"),
    ("dataset_promotion", "result/priority_lsms_isa_local_raw_presence_summary.csv", "priority LSMS/ISA local raw presence summary"),
    ("dataset_promotion", "report/priority_lsms_isa_acquisition_to_promotion_handoff.md", "priority LSMS/ISA acquisition-to-promotion handoff report"),
    ("dataset_promotion", "result/priority_lsms_isa_acquisition_to_promotion_handoff.csv", "priority LSMS/ISA acquisition-to-promotion handoff rows"),
    ("dataset_promotion", "result/priority_lsms_isa_acquisition_to_promotion_gate_checklist.csv", "priority LSMS/ISA acquisition-to-promotion gate checklist"),
    ("dataset_promotion", "result/priority_lsms_isa_acquisition_to_promotion_handoff_summary.csv", "priority LSMS/ISA acquisition-to-promotion handoff summary"),
    ("dataset_promotion", "report/priority_lsms_isa_dataset_scope_lock.md", "priority LSMS/ISA dataset scope lock report"),
    ("dataset_promotion", "result/priority_lsms_isa_dataset_scope_lock.csv", "priority LSMS/ISA dataset scope lock rows"),
    ("dataset_promotion", "result/priority_lsms_isa_dataset_scope_lock_gate_matrix.csv", "priority LSMS/ISA dataset scope lock gate matrix"),
    ("dataset_promotion", "result/priority_lsms_isa_dataset_scope_lock_summary.csv", "priority LSMS/ISA dataset scope lock summary"),
    ("dataset_promotion", "report/priority_lsms_isa_acquisition_route_decision.md", "priority LSMS/ISA acquisition route decision report"),
    ("dataset_promotion", "result/priority_lsms_isa_acquisition_route_decision.csv", "priority LSMS/ISA acquisition route decision rows"),
    ("dataset_promotion", "result/priority_lsms_isa_acquisition_route_evidence.csv", "priority LSMS/ISA acquisition route evidence rows"),
    ("dataset_promotion", "result/priority_lsms_isa_acquisition_route_decision_summary.csv", "priority LSMS/ISA acquisition route decision summary"),
    ("dataset_promotion", "report/priority_lsms_isa_scoped_incoming_package_router.md", "priority LSMS/ISA scoped incoming package router report"),
    ("dataset_promotion", "result/priority_lsms_isa_scoped_incoming_package_router.csv", "priority LSMS/ISA scoped incoming package router rows"),
    ("dataset_promotion", "result/priority_lsms_isa_scoped_incoming_package_router_evidence.csv", "priority LSMS/ISA scoped incoming package router evidence rows"),
    ("dataset_promotion", "result/priority_lsms_isa_scoped_incoming_package_router_summary.csv", "priority LSMS/ISA scoped incoming package router summary"),
    ("dataset_promotion", "report/priority_lsms_isa_webgpt_download_control_manifest.md", "priority LSMS/ISA Web GPT download control manifest report"),
    ("dataset_promotion", "result/priority_lsms_isa_webgpt_download_control_manifest.csv", "priority LSMS/ISA Web GPT download control manifest"),
    ("dataset_promotion", "result/priority_lsms_isa_webgpt_expected_core_file_manifest.csv", "priority LSMS/ISA Web GPT expected core-file manifest"),
    ("dataset_promotion", "result/priority_lsms_isa_webgpt_download_control_summary.csv", "priority LSMS/ISA Web GPT download control summary"),
    ("dataset_promotion", "report/priority_analysis_dataset_synthesis_blueprint.md", "priority promoted dataset synthesis blueprint report"),
    ("dataset_promotion", "temp/priority_analysis_dataset_synthesis_blueprint.csv", "priority target household-climate schema blueprint"),
    ("dataset_promotion", "temp/priority_analysis_dataset_join_plan.csv", "priority dataset-level join plan"),
    ("dataset_promotion", "result/priority_analysis_dataset_synthesis_blueprint_summary.csv", "priority analysis dataset synthesis blueprint summary"),
    ("dataset_promotion", "report/priority_country_wave_promotion_packets.md", "priority country-wave promotion packet report"),
    ("dataset_promotion", "temp/priority_country_wave_promotion_packet_index.csv", "priority country-wave promotion packet index"),
    ("dataset_promotion", "temp/priority_country_wave_promotion_packet_gate_matrix.csv", "priority country-wave promotion packet gate matrix"),
    ("dataset_promotion", "temp/priority_country_wave_promotion_packet_action_queue.csv", "priority country-wave promotion packet action queue"),
    ("dataset_promotion", "result/priority_country_wave_promotion_packet_summary.csv", "priority country-wave promotion packet summary"),
    ("dataset_promotion", "report/priority_lsms_isa_country_wave_promotion_packets.md", "priority LSMS/ISA country-wave promotion packet report"),
    ("dataset_promotion", "temp/priority_lsms_isa_country_wave_promotion_packet_index.csv", "priority LSMS/ISA country-wave promotion packet index"),
    ("dataset_promotion", "temp/priority_lsms_isa_country_wave_promotion_packet_gate_matrix.csv", "priority LSMS/ISA country-wave promotion packet gate matrix"),
    ("dataset_promotion", "temp/priority_lsms_isa_country_wave_promotion_packet_action_queue.csv", "priority LSMS/ISA country-wave promotion packet action queue"),
    ("dataset_promotion", "result/priority_lsms_isa_country_wave_promotion_packet_summary.csv", "priority LSMS/ISA country-wave promotion packet summary"),
    ("dataset_promotion", "report/promoted_data_gate.md", "promoted data write gate report"),
    ("dataset_promotion", "result/promoted_data_gate_summary.csv", "promoted data write gate summary"),
    ("dataset_promotion", "temp/promoted_data_gate_manifest.csv", "promoted data quarantine/action manifest"),
    ("dataset_promotion", "data/README.md", "data directory promoted-data status note"),
    ("raw_access", "temp/source_inventory.csv", "source inventory"),
    ("raw_access", "temp/country_wave_screening.csv", "broad candidate country-wave screening"),
    ("raw_access", "temp/manual_download_manifest.csv", "manual raw-data access manifest"),
    ("raw_access", "temp/manual_download_priority.csv", "ranked manual download priorities"),
    ("raw_access", "temp/manual_download_file_checklist.csv", "file/module checklist for manual downloads"),
    ("raw_access", "temp/raw_download_intake_manifest.csv", "raw-download intake target status"),
    ("raw_access", "temp/raw_download_expected_files.csv", "expected raw files/modules"),
    ("raw_access", "temp/public_external_raw_candidate_downloads.csv", "public external raw candidate downloads"),
    ("raw_access", "result/public_external_raw_candidate_download_summary.csv", "public external raw candidate download summary"),
    ("raw_access", "report/public_external_raw_candidate_downloads.md", "public external raw candidate download report"),
    ("raw_access", "temp/first_batch_raw_acquisition_checklist.csv", "first-batch raw acquisition checklist"),
    ("raw_access", "temp/first_batch_raw_file_targets.csv", "first-batch file/module targets"),
    ("raw_access", "result/first_batch_raw_acquisition_summary.csv", "first-batch raw acquisition summary"),
    ("raw_access", "report/first_batch_raw_acquisition_checklist.md", "first-batch raw acquisition report"),
    ("raw_access", "temp/first_batch_official_raw_access_probe.csv", "first-batch official raw access probe"),
    ("raw_access", "result/first_batch_official_raw_access_summary.csv", "first-batch official raw access summary"),
    ("raw_access", "report/first_batch_official_raw_access_probe.md", "first-batch official raw access report"),
    ("raw_access", "temp/first_batch_manual_download_handoff.csv", "first-batch manual download handoff"),
    ("raw_access", "temp/first_batch_manual_download_file_queue.csv", "first-batch manual download file queue"),
    ("raw_access", "result/first_batch_manual_download_handoff_summary.csv", "first-batch manual download handoff summary"),
    ("raw_access", "report/first_batch_manual_download_handoff.md", "first-batch manual download handoff report"),
    ("raw_access", "temp/first_batch_public_documentation_audit.csv", "first-batch public documentation audit"),
    ("raw_access", "result/first_batch_public_documentation_summary.csv", "first-batch public documentation summary"),
    ("raw_access", "report/first_batch_public_documentation_audit.md", "first-batch public documentation report"),
    ("raw_access", "temp/first_batch_file_source_traceability.csv", "first-batch file source traceability"),
    ("raw_access", "result/first_batch_file_source_traceability_summary.csv", "first-batch file source traceability summary"),
    ("raw_access", "report/first_batch_file_source_traceability.md", "first-batch file source traceability report"),
    ("raw_access", "temp/first_batch_merge_key_lineage_plan.csv", "first-batch merge-key lineage plan"),
    ("raw_access", "temp/first_batch_merge_key_candidate_variables.csv", "first-batch merge-key candidate variables"),
    ("raw_access", "result/first_batch_merge_key_lineage_summary.csv", "first-batch merge-key lineage summary"),
    ("raw_access", "report/first_batch_merge_key_lineage_plan.md", "first-batch merge-key lineage report"),
    ("raw_access", "temp/first_batch_raw_value_key_audit.csv", "first-batch raw value audit"),
    ("raw_access", "temp/first_batch_raw_merge_key_audit.csv", "first-batch raw merge-key audit"),
    ("raw_access", "temp/first_batch_harmonization_value_audit_auto.csv", "first-batch fail-closed auto harmonization value audit"),
    ("raw_access", "result/first_batch_raw_value_key_summary.csv", "first-batch raw value/key audit summary"),
    ("raw_access", "report/first_batch_raw_value_key_audit.md", "first-batch raw value/key audit report"),
    ("raw_verification", "temp/alb2002_household_core_candidate.csv", "ALB_2002 temp household core candidate"),
    ("raw_verification", "temp/alb2002_household_core_merge_audit.csv", "ALB_2002 household core merge audit"),
    ("raw_verification", "temp/alb2002_household_core_lineage.csv", "ALB_2002 household core lineage"),
    ("raw_verification", "result/alb2002_household_core_candidate_summary.csv", "ALB_2002 household core candidate summary"),
    ("raw_verification", "report/alb2002_household_core_merge_audit.md", "ALB_2002 household core merge audit report"),
    ("raw_verification", "temp/alb2002_weight_design_evidence_audit.csv", "ALB_2002 weight/design evidence audit"),
    ("raw_verification", "result/alb2002_weight_design_evidence_summary.csv", "ALB_2002 weight/design evidence summary"),
    ("raw_verification", "report/alb2002_weight_design_evidence_audit.md", "ALB_2002 weight/design evidence report"),
    ("raw_verification", "temp/source_snapshots/alb2002_worldbank_study_description_weight_design.html", "ALB_2002 official study-page source snapshot for weight/design audit"),
    ("raw_verification", "temp/alb2002_sample_design_documentation_audit.csv", "ALB_2002 official sample-design documentation audit"),
    ("raw_verification", "result/alb2002_sample_design_documentation_summary.csv", "ALB_2002 official sample-design documentation summary"),
    ("raw_verification", "report/alb2002_sample_design_documentation_audit.md", "ALB_2002 official sample-design documentation report"),
    ("raw_verification", "temp/source_snapshots/alb2002_basic_information_document_sample_design.pdf", "ALB_2002 Basic Information PDF snapshot for sample-design audit"),
    ("raw_verification", "temp/source_snapshots/alb2002_basic_information_document_sample_design.txt", "ALB_2002 extracted Basic Information PDF text for sample-design audit"),
    ("climate_outcome", "temp/alb2002_provisional_outcome_feasibility_audit.csv", "ALB_2002 provisional outcome feasibility audit"),
    ("climate_outcome", "result/alb2002_provisional_outcome_feasibility_summary.csv", "ALB_2002 provisional outcome feasibility summary"),
    ("climate_outcome", "report/alb2002_provisional_outcome_feasibility.md", "ALB_2002 provisional outcome feasibility report"),
    ("climate_outcome", "temp/alb2002_outcome_semantics_raw_value_audit.csv", "ALB_2002 outcome semantics raw value audit"),
    ("climate_outcome", "result/alb2002_outcome_semantics_raw_value_summary.csv", "ALB_2002 outcome semantics raw value summary"),
    ("climate_outcome", "report/alb2002_outcome_semantics_raw_value_audit.md", "ALB_2002 outcome semantics raw value report"),
    ("climate_outcome", "temp/alb2002_health_questionnaire_semantics_audit.csv", "ALB_2002 health questionnaire semantics audit"),
    ("climate_outcome", "result/alb2002_health_questionnaire_semantics_summary.csv", "ALB_2002 health questionnaire semantics summary"),
    ("climate_outcome", "report/alb2002_health_questionnaire_semantics_audit.md", "ALB_2002 health questionnaire semantics report"),
    ("climate_outcome", "temp/alb2002_oop_aggregation_policy_audit.csv", "ALB_2002 OOP aggregation policy audit"),
    ("climate_outcome", "result/alb2002_oop_aggregation_policy_summary.csv", "ALB_2002 OOP aggregation policy summary"),
    ("climate_outcome", "report/alb2002_oop_aggregation_policy_audit.md", "ALB_2002 OOP aggregation policy report"),
    ("climate_outcome", "temp/alb2002_skip_missing_semantics_audit.csv", "ALB_2002 skip/missing semantics audit"),
    ("climate_outcome", "result/alb2002_skip_missing_semantics_summary.csv", "ALB_2002 skip/missing semantics summary"),
    ("climate_outcome", "report/alb2002_skip_missing_semantics_audit.md", "ALB_2002 skip/missing semantics report"),
    ("climate_outcome", "temp/alb2002_oop_skip_value_decision_audit.csv", "ALB_2002 OOP skip-value decision audit"),
    ("climate_outcome", "result/alb2002_oop_skip_value_decision_summary.csv", "ALB_2002 OOP skip-value decision summary"),
    ("climate_outcome", "report/alb2002_oop_skip_value_decision_audit.md", "ALB_2002 OOP skip-value decision report"),
    ("climate_outcome", "temp/alb2002_access_need_denominator_policy_audit.csv", "ALB_2002 access/need denominator policy audit"),
    ("climate_outcome", "result/alb2002_access_need_denominator_policy_summary.csv", "ALB_2002 access/need denominator policy summary"),
    ("climate_outcome", "report/alb2002_access_need_denominator_policy_audit.md", "ALB_2002 access/need denominator policy report"),
    ("climate_outcome", "temp/alb2002_consumption_sdg_denominator_policy_audit.csv", "ALB_2002 consumption/SDG denominator policy audit"),
    ("climate_outcome", "result/alb2002_consumption_sdg_denominator_policy_summary.csv", "ALB_2002 consumption/SDG denominator policy summary"),
    ("climate_outcome", "report/alb2002_consumption_sdg_denominator_policy_audit.md", "ALB_2002 consumption/SDG denominator policy report"),
    ("climate_outcome", "temp/alb2002_consumption_construction_source_audit.csv", "ALB_2002 public consumption-construction source audit"),
    ("climate_outcome", "result/alb2002_consumption_construction_source_summary.csv", "ALB_2002 public consumption-construction source summary"),
    ("climate_outcome", "report/alb2002_consumption_construction_source_audit.md", "ALB_2002 public consumption-construction source report"),
    ("climate_outcome", "temp/alb2002_consumption_aggregate_metadata_crosswalk_audit.csv", "ALB_2002 consumption aggregate metadata crosswalk audit"),
    ("climate_outcome", "result/alb2002_consumption_aggregate_metadata_crosswalk_summary.csv", "ALB_2002 consumption aggregate metadata crosswalk summary"),
    ("climate_outcome", "report/alb2002_consumption_aggregate_metadata_crosswalk_audit.md", "ALB_2002 consumption aggregate metadata crosswalk report"),
    ("climate_outcome", "temp/alb2002_period_aligned_che_policy_audit.csv", "ALB_2002 period-aligned CHE policy audit"),
    ("climate_outcome", "result/alb2002_period_aligned_che_policy_summary.csv", "ALB_2002 period-aligned CHE policy summary"),
    ("climate_outcome", "report/alb2002_period_aligned_che_policy_audit.md", "ALB_2002 period-aligned CHE policy report"),
    ("climate_outcome", "temp/alb2002_che_candidate_household_outcomes.csv", "ALB_2002 temp-only household CHE candidate outcomes"),
    ("climate_outcome", "temp/alb2002_che_candidate_outcome_lineage.csv", "ALB_2002 CHE candidate outcome lineage"),
    ("climate_outcome", "result/alb2002_che_candidate_outcome_audit.csv", "ALB_2002 CHE candidate outcome audit"),
    ("climate_outcome", "result/alb2002_che_candidate_outcome_summary.csv", "ALB_2002 CHE candidate outcome summary"),
    ("climate_outcome", "report/alb2002_che_candidate_outcome_audit.md", "ALB_2002 CHE candidate outcome report"),
    ("climate_outcome", "temp/alb2002_access_candidate_household_outcomes.csv", "ALB_2002 temp-only household access candidate outcomes"),
    ("climate_outcome", "temp/alb2002_access_candidate_outcome_lineage.csv", "ALB_2002 access candidate outcome lineage"),
    ("climate_outcome", "result/alb2002_access_candidate_outcome_audit.csv", "ALB_2002 access candidate outcome audit"),
    ("climate_outcome", "result/alb2002_access_candidate_outcome_summary.csv", "ALB_2002 access candidate outcome summary"),
    ("climate_outcome", "report/alb2002_access_candidate_outcome_audit.md", "ALB_2002 access candidate outcome report"),
    ("climate_outcome", "temp/alb2002_uhc_composite_candidate_outcomes.csv", "ALB_2002 temp-only composite UHC candidate outcomes"),
    ("climate_outcome", "temp/alb2002_uhc_composite_candidate_lineage.csv", "ALB_2002 composite UHC candidate lineage"),
    ("climate_outcome", "result/alb2002_uhc_composite_candidate_audit.csv", "ALB_2002 composite UHC candidate audit"),
    ("climate_outcome", "result/alb2002_uhc_composite_candidate_summary.csv", "ALB_2002 composite UHC candidate summary"),
    ("climate_outcome", "report/alb2002_uhc_composite_candidate_audit.md", "ALB_2002 composite UHC candidate report"),
    ("climate_outcome", "temp/alb2002_analysis_candidate_dataset.csv", "ALB_2002 temp-only joined analysis candidate dataset"),
    ("climate_outcome", "temp/alb2002_analysis_candidate_lineage.csv", "ALB_2002 analysis candidate lineage"),
    ("climate_outcome", "result/alb2002_analysis_candidate_readiness_audit.csv", "ALB_2002 analysis candidate readiness audit"),
    ("climate_outcome", "result/alb2002_analysis_candidate_readiness_summary.csv", "ALB_2002 analysis candidate readiness summary"),
    ("climate_outcome", "report/alb2002_analysis_candidate_readiness_audit.md", "ALB_2002 analysis candidate readiness report"),
    ("climate_outcome", "data/harmonized_household.csv", "ALB_2002 limited harmonized household core"),
    ("climate_outcome", "temp/harmonization_audit.csv", "limited harmonized household core audit"),
    ("climate_outcome", "temp/harmonized_lineage.csv", "limited harmonized household core lineage"),
    ("climate_outcome", "temp/alb2002_harmonized_household_core_promotion_audit.csv", "ALB_2002 limited harmonized core promotion audit"),
    ("climate_outcome", "result/alb2002_harmonized_household_core_promotion_summary.csv", "ALB_2002 limited harmonized core promotion summary"),
    ("climate_outcome", "report/alb2002_harmonized_household_core_promotion.md", "ALB_2002 limited harmonized core promotion report"),
    ("climate_outcome", "data/household_outcomes.csv", "ALB_2002 limited CHE-only household outcome file"),
    ("climate_outcome", "result/outcome_audit.csv", "limited outcome audit"),
    ("climate_outcome", "temp/outcome_construction_audit.csv", "limited outcome construction audit"),
    ("climate_outcome", "temp/alb2002_limited_financial_outcome_promotion_audit.csv", "ALB_2002 limited financial outcome promotion audit"),
    ("climate_outcome", "result/alb2002_limited_financial_outcome_promotion_summary.csv", "ALB_2002 limited financial outcome promotion summary"),
    ("climate_outcome", "report/alb2002_limited_financial_outcome_promotion.md", "ALB_2002 limited financial outcome promotion report"),
    ("climate_outcome", "temp/alb2002_climate_centroid_exposure_input.csv", "ALB_2002 temp-only climate centroid exposure inputs"),
    ("climate_outcome", "temp/alb2002_climate_centroid_exposure_candidates.csv", "ALB_2002 temp-only climate centroid exposure candidates"),
    ("climate_outcome", "temp/alb2002_climate_centroid_nasa_power_api_manifest.csv", "ALB_2002 NASA POWER centroid API/cache manifest"),
    ("climate_outcome", "result/alb2002_climate_centroid_exposure_audit.csv", "ALB_2002 climate centroid exposure audit"),
    ("climate_outcome", "result/alb2002_climate_centroid_exposure_summary.csv", "ALB_2002 climate centroid exposure summary"),
    ("climate_outcome", "report/alb2002_climate_centroid_exposure_audit.md", "ALB_2002 climate centroid exposure report"),
    ("climate_outcome", "temp/alb2002_climate_shock_candidate_exposures.csv", "ALB_2002 temp-only climate shock diagnostic candidates"),
    ("climate_outcome", "temp/alb2002_climate_shock_candidate_lineage.csv", "ALB_2002 climate shock diagnostic lineage"),
    ("climate_outcome", "result/alb2002_climate_shock_candidate_audit.csv", "ALB_2002 climate shock diagnostic audit"),
    ("climate_outcome", "result/alb2002_climate_shock_candidate_summary.csv", "ALB_2002 climate shock diagnostic summary"),
    ("climate_outcome", "report/alb2002_climate_shock_candidate_audit.md", "ALB_2002 climate shock diagnostic report"),
    ("climate_outcome", "data/climate_exposures_nasa_power.csv", "ALB_2002 limited NASA POWER admin2-centroid exposure file"),
    ("climate_outcome", "temp/climate_extraction_audit.csv", "limited climate exposure extraction audit"),
    ("climate_outcome", "temp/alb2002_limited_climate_exposure_promotion_audit.csv", "ALB_2002 limited climate exposure promotion audit"),
    ("climate_outcome", "result/alb2002_limited_climate_exposure_promotion_summary.csv", "ALB_2002 limited climate exposure promotion summary"),
    ("climate_outcome", "report/alb2002_limited_climate_exposure_promotion.md", "ALB_2002 limited climate exposure promotion report"),
    ("climate_outcome", "data/climate_linked_household.csv", "ALB_2002 limited CHE and NASA POWER climate-linked household-window file"),
    ("climate_outcome", "temp/climate_merge_audit.csv", "limited climate-linked merge audit"),
    ("climate_outcome", "temp/alb2002_limited_climate_linked_promotion_audit.csv", "ALB_2002 limited climate-linked promotion audit"),
    ("climate_outcome", "result/alb2002_limited_climate_linked_promotion_summary.csv", "ALB_2002 limited climate-linked promotion summary"),
    ("climate_outcome", "report/alb2002_limited_climate_linked_promotion.md", "ALB_2002 limited climate-linked promotion report"),
    ("climate_outcome", "temp/alb2002_climate_outcome_linked_candidate.csv", "ALB_2002 temp-only household-window climate/outcome linked candidate"),
    ("climate_outcome", "temp/alb2002_climate_outcome_linked_candidate_lineage.csv", "ALB_2002 climate/outcome linked candidate lineage"),
    ("climate_outcome", "result/alb2002_climate_outcome_linked_candidate_audit.csv", "ALB_2002 climate/outcome linked candidate audit"),
    ("climate_outcome", "result/alb2002_climate_outcome_linked_candidate_summary.csv", "ALB_2002 climate/outcome linked candidate summary"),
    ("climate_outcome", "report/alb2002_climate_outcome_linked_candidate_audit.md", "ALB_2002 climate/outcome linked candidate report"),
    ("climate_outcome", "result/alb2002_linked_candidate_descriptive_audit.csv", "ALB_2002 linked-candidate descriptive screen audit"),
    ("climate_outcome", "result/alb2002_linked_candidate_descriptive_cells.csv", "ALB_2002 linked-candidate descriptive screen cells"),
    ("climate_outcome", "result/alb2002_linked_candidate_descriptive_summary.csv", "ALB_2002 linked-candidate descriptive screen summary"),
    ("climate_outcome", "report/alb2002_linked_candidate_descriptive_diagnostics.md", "ALB_2002 linked-candidate descriptive screen report"),
    ("design_gate", "result/design_scorecard.csv", "broad and current design scorecard"),
    ("design_gate", "result/design_scorecard_current_audit.csv", "current design scorecard refresh audit"),
    ("design_gate", "result/design_no_go_threshold_audit.csv", "current design no-go threshold audit"),
    ("design_gate", "result/design_scorecard_current_summary.csv", "current design scorecard summary"),
    ("design_gate", "report/design_scorecard_audit.md", "current design scorecard report"),
    ("design_gate", "temp/alb2002_promotion_gate_delta_audit.csv", "ALB_2002 promotion gate delta audit"),
    ("design_gate", "result/alb2002_promotion_gate_delta_summary.csv", "ALB_2002 promotion gate delta summary"),
    ("design_gate", "report/alb2002_promotion_gate_delta_audit.md", "ALB_2002 promotion gate delta report"),
    ("design_gate", "temp/alb2002_boundary_blocker_resolution_matrix.csv", "ALB_2002 boundary blocker resolution matrix"),
    ("design_gate", "result/alb2002_boundary_blocker_resolution_summary.csv", "ALB_2002 boundary blocker resolution summary"),
    ("design_gate", "report/alb2002_boundary_blocker_resolution_matrix.md", "ALB_2002 boundary blocker resolution report"),
    ("design_gate", "temp/alb2002_outcome_blocker_resolution_matrix.csv", "ALB_2002 outcome blocker resolution matrix"),
    ("design_gate", "result/alb2002_outcome_blocker_resolution_summary.csv", "ALB_2002 outcome blocker resolution summary"),
    ("design_gate", "report/alb2002_outcome_blocker_resolution_matrix.md", "ALB_2002 outcome blocker resolution report"),
    ("raw_verification", "temp/alb2002_minimum_recipe_promotion_action_queue.csv", "ALB_2002 minimum recipe promotion action queue"),
    ("raw_verification", "temp/alb2002_minimum_recipe_promotion_gate_checklist.csv", "ALB_2002 minimum recipe promotion gate checklist"),
    ("raw_verification", "result/alb2002_minimum_recipe_promotion_summary.csv", "ALB_2002 minimum recipe promotion summary"),
    ("raw_verification", "report/alb2002_minimum_recipe_promotion_packet.md", "ALB_2002 minimum recipe promotion packet"),
    ("raw_verification", "temp/analysis_dataset_promotion_barrier_audit.csv", "analysis dataset promotion barrier audit"),
    ("raw_verification", "result/analysis_dataset_promotion_barrier_summary.csv", "analysis dataset promotion barrier summary"),
    ("raw_verification", "report/analysis_dataset_promotion_barriers.md", "analysis dataset promotion barrier report"),
    ("climate_outcome", "temp/alb2002_district_climate_crosswalk_template.csv", "ALB_2002 district climate crosswalk template"),
    ("climate_outcome", "temp/alb2002_district_boundary_source_probe.csv", "ALB_2002 public boundary source probe"),
    ("climate_outcome", "result/alb2002_district_climate_crosswalk_summary.csv", "ALB_2002 district climate crosswalk summary"),
    ("climate_outcome", "report/alb2002_district_climate_crosswalk_audit.md", "ALB_2002 district climate crosswalk report"),
    ("climate_outcome", "temp/alb2002_boundary_name_match_audit.csv", "ALB_2002 boundary name match audit"),
    ("climate_outcome", "temp/alb2002_boundary_geojson_inventory.csv", "ALB_2002 public boundary GeoJSON inventory"),
    ("climate_outcome", "temp/source_snapshots/alb2002_geoboundaries_alb_adm2_current.geojson", "ALB_2002 public boundary GeoJSON snapshot"),
    ("climate_outcome", "result/alb2002_boundary_name_match_summary.csv", "ALB_2002 boundary name match summary"),
    ("climate_outcome", "report/alb2002_boundary_name_match_audit.md", "ALB_2002 boundary name match report"),
    ("climate_outcome", "temp/alb2002_boundary_source_alternative_audit.csv", "ALB_2002 boundary source alternatives audit"),
    ("climate_outcome", "result/alb2002_boundary_source_alternative_summary.csv", "ALB_2002 boundary source alternatives summary"),
    ("climate_outcome", "report/alb2002_boundary_source_alternative_audit.md", "ALB_2002 boundary source alternatives report"),
    ("climate_outcome", "temp/alb2002_boundary_source_resource_search_audit.csv", "ALB_2002 boundary source resource search audit"),
    ("climate_outcome", "result/alb2002_boundary_source_resource_search_summary.csv", "ALB_2002 boundary source resource search summary"),
    ("climate_outcome", "report/alb2002_boundary_source_resource_search_audit.md", "ALB_2002 boundary source resource search report"),
    ("climate_outcome", "temp/source_snapshots/alb2002_geoboundaries_2_0_1_alb_adm2.geojson", "ALB_2002 geoBoundaries 2.0.1 boundary source snapshot"),
    ("climate_outcome", "temp/source_snapshots/alb2002_geoboundaries_2_0_1_alb_adm2_metadata.json", "ALB_2002 geoBoundaries 2.0.1 companion metadata snapshot"),
    ("climate_outcome", "temp/alb2002_boundary_geometry_provenance_audit.csv", "ALB_2002 boundary geometry/provenance audit"),
    ("climate_outcome", "temp/alb2002_boundary_metadata_provenance_probe.csv", "ALB_2002 boundary metadata provenance probe"),
    ("climate_outcome", "result/alb2002_boundary_geometry_provenance_summary.csv", "ALB_2002 boundary geometry/provenance summary"),
    ("climate_outcome", "report/alb2002_boundary_geometry_provenance_audit.md", "ALB_2002 boundary geometry/provenance report"),
    ("climate_outcome", "temp/alb2002_boundary_manual_verification_action_queue.csv", "ALB_2002 boundary manual verification action queue"),
    ("climate_outcome", "temp/alb2002_boundary_promotion_gate_checklist.csv", "ALB_2002 boundary promotion gate checklist"),
    ("climate_outcome", "result/alb2002_boundary_manual_verification_packet_summary.csv", "ALB_2002 boundary manual verification packet summary"),
    ("climate_outcome", "report/alb2002_boundary_manual_verification_packet.md", "ALB_2002 boundary manual verification packet report"),
    ("climate_outcome", "temp/alb2002_boundary_manual_source_followup_audit.csv", "ALB_2002 boundary manual source follow-up audit"),
    ("climate_outcome", "result/alb2002_boundary_manual_source_followup_summary.csv", "ALB_2002 boundary manual source follow-up summary"),
    ("climate_outcome", "report/alb2002_boundary_manual_source_followup.md", "ALB_2002 boundary manual source follow-up report"),
    ("climate_outcome", "temp/alb2002_gadm_boundary_lead_audit.csv", "ALB_2002 GADM boundary lead audit"),
    ("climate_outcome", "temp/alb2002_gadm_boundary_name_match_audit.csv", "ALB_2002 GADM boundary name match audit"),
    ("climate_outcome", "result/alb2002_gadm_boundary_lead_summary.csv", "ALB_2002 GADM boundary lead summary"),
    ("climate_outcome", "report/alb2002_gadm_boundary_lead_audit.md", "ALB_2002 GADM boundary lead report"),
    ("climate_outcome", "temp/source_snapshots/gadm36_ALB_shp.zip", "GADM 3.6 Albania shapefile snapshot"),
    ("climate_outcome", "temp/source_snapshots/gadm41_ALB_shp.zip", "GADM 4.1 Albania shapefile snapshot"),
    ("climate_outcome", "temp/source_snapshots/hdx_cod_ab_alb_package_show.json", "HDX COD-AB Albania package metadata snapshot"),
    ("climate_outcome", "temp/source_snapshots/hdx_alb_adm_gazetteer_2019.xlsx", "HDX COD-AB Albania 2019 gazetteer workbook snapshot"),
    ("climate_outcome", "temp/alb2002_local_geography_artifact_audit.csv", "ALB_2002 local geography artifact audit"),
    ("climate_outcome", "result/alb2002_local_geography_artifact_summary.csv", "ALB_2002 local geography artifact summary"),
    ("climate_outcome", "report/alb2002_local_geography_artifact_audit.md", "ALB_2002 local geography artifact report"),
    ("raw_verification", "temp/alb2012_household_core_candidate.csv", "ALB_2012 temp household core candidate"),
    ("raw_verification", "temp/alb2012_raw_core_feasibility_audit.csv", "ALB_2012 raw core feasibility audit"),
    ("raw_verification", "temp/alb2012_raw_core_lineage.csv", "ALB_2012 raw core lineage"),
    ("raw_verification", "result/alb2012_raw_core_feasibility_summary.csv", "ALB_2012 raw core feasibility summary"),
    ("raw_verification", "report/alb2012_raw_core_feasibility.md", "ALB_2012 raw core feasibility report"),
    ("climate_outcome", "temp/alb2012_provisional_outcome_feasibility_audit.csv", "ALB_2012 provisional outcome feasibility audit"),
    ("climate_outcome", "result/alb2012_provisional_outcome_feasibility_summary.csv", "ALB_2012 provisional outcome feasibility summary"),
    ("climate_outcome", "report/alb2012_provisional_outcome_feasibility.md", "ALB_2012 provisional outcome feasibility report"),
    ("climate_outcome", "temp/alb2012_outcome_semantics_raw_value_audit.csv", "ALB_2012 outcome semantics raw value audit"),
    ("climate_outcome", "result/alb2012_outcome_semantics_raw_value_summary.csv", "ALB_2012 outcome semantics raw value summary"),
    ("climate_outcome", "report/alb2012_outcome_semantics_raw_value_audit.md", "ALB_2012 outcome semantics raw value report"),
    ("climate_outcome", "temp/alb2012_timing_geography_exhaustive_audit.csv", "ALB_2012 timing/geography exhaustive audit"),
    ("climate_outcome", "result/alb2012_timing_geography_exhaustive_summary.csv", "ALB_2012 timing/geography exhaustive summary"),
    ("climate_outcome", "report/alb2012_timing_geography_exhaustive_audit.md", "ALB_2012 timing/geography exhaustive report"),
    ("climate_outcome", "temp/alb2012_questionnaire_timing_field_audit.csv", "ALB_2012 questionnaire timing field audit"),
    ("climate_outcome", "temp/alb2012_questionnaire_timing_raw_gap_audit.csv", "ALB_2012 questionnaire timing raw-gap audit"),
    ("climate_outcome", "result/alb2012_questionnaire_timing_field_summary.csv", "ALB_2012 questionnaire timing field summary"),
    ("climate_outcome", "report/alb2012_questionnaire_timing_field_audit.md", "ALB_2012 questionnaire timing field report"),
    ("climate_outcome", "temp/alb2012_timing_geography_blocker_resolution_matrix.csv", "ALB_2012 timing/geography blocker resolution matrix"),
    ("climate_outcome", "result/alb2012_timing_geography_blocker_resolution_summary.csv", "ALB_2012 timing/geography blocker resolution summary"),
    ("climate_outcome", "report/alb2012_timing_geography_blocker_resolution_matrix.md", "ALB_2012 timing/geography blocker resolution report"),
    ("raw_verification", "temp/albania_legacy_questionnaire_readability_audit.csv", "Albania legacy questionnaire readability audit"),
    ("raw_verification", "result/albania_legacy_questionnaire_readability_summary.csv", "Albania legacy questionnaire readability summary"),
    ("raw_verification", "report/albania_legacy_questionnaire_readability_audit.md", "Albania legacy questionnaire readability report"),
    ("raw_verification", "temp/albania_legacy_questionnaire_timing_field_audit.csv", "Albania legacy questionnaire timing field audit"),
    ("raw_verification", "temp/albania_legacy_questionnaire_timing_raw_gap_audit.csv", "Albania legacy questionnaire timing raw-gap audit"),
    ("raw_verification", "result/albania_legacy_questionnaire_timing_field_summary.csv", "Albania legacy questionnaire timing field summary"),
    ("raw_verification", "report/albania_legacy_questionnaire_timing_field_audit.md", "Albania legacy questionnaire timing field report"),
    ("raw_verification", "temp/alb2005_documented_variable_evidence.csv", "ALB_2005 documented variable evidence"),
    ("raw_verification", "result/alb2005_documented_harmonization_summary.csv", "ALB_2005 documented harmonization summary"),
    ("raw_verification", "report/alb2005_documented_harmonization_review.md", "ALB_2005 documented harmonization review"),
    ("raw_verification", "temp/alb2005_household_core_candidate.csv", "ALB_2005 temp household core candidate"),
    ("raw_verification", "temp/alb2005_household_core_merge_audit.csv", "ALB_2005 household core merge audit"),
    ("raw_verification", "temp/alb2005_household_core_lineage.csv", "ALB_2005 household core lineage"),
    ("raw_verification", "result/alb2005_household_core_candidate_summary.csv", "ALB_2005 household core candidate summary"),
    ("raw_verification", "report/alb2005_household_core_merge_audit.md", "ALB_2005 household core merge audit report"),
    ("climate_outcome", "temp/alb2005_provisional_outcome_feasibility_audit.csv", "ALB_2005 provisional outcome feasibility audit"),
    ("climate_outcome", "result/alb2005_provisional_outcome_feasibility_summary.csv", "ALB_2005 provisional outcome feasibility summary"),
    ("climate_outcome", "report/alb2005_provisional_outcome_feasibility.md", "ALB_2005 provisional outcome feasibility report"),
    ("climate_outcome", "temp/alb2005_outcome_semantics_raw_value_audit.csv", "ALB_2005 outcome semantics raw value audit"),
    ("climate_outcome", "result/alb2005_outcome_semantics_raw_value_summary.csv", "ALB_2005 outcome semantics raw value summary"),
    ("climate_outcome", "report/alb2005_outcome_semantics_raw_value_audit.md", "ALB_2005 outcome semantics raw value report"),
    ("climate_outcome", "temp/alb2005_timing_geography_exhaustive_audit.csv", "ALB_2005 timing/geography exhaustive audit"),
    ("climate_outcome", "result/alb2005_timing_geography_exhaustive_summary.csv", "ALB_2005 timing/geography exhaustive summary"),
    ("climate_outcome", "report/alb2005_timing_geography_exhaustive_audit.md", "ALB_2005 timing/geography exhaustive report"),
    ("raw_verification", "temp/alb2005_harmonization_value_decision_audit.csv", "ALB_2005 harmonization value decision audit"),
    ("raw_verification", "result/alb2005_harmonization_value_decision_summary.csv", "ALB_2005 harmonization value decision summary"),
    ("raw_verification", "report/alb2005_harmonization_value_decision_audit.md", "ALB_2005 harmonization value decision report"),
    ("raw_verification", "temp/alb2005_required_value_key_audit.csv", "ALB_2005 required value/key audit"),
    ("raw_verification", "result/alb2005_required_value_key_summary.csv", "ALB_2005 required value/key summary"),
    ("raw_verification", "report/alb2005_required_value_key_audit.md", "ALB_2005 required value/key report"),
    ("raw_verification", "temp/alb2005_health_questionnaire_semantics_audit.csv", "ALB_2005 health questionnaire semantics audit"),
    ("raw_verification", "result/alb2005_health_questionnaire_semantics_summary.csv", "ALB_2005 health questionnaire semantics summary"),
    ("raw_verification", "report/alb2005_health_questionnaire_semantics_audit.md", "ALB_2005 health questionnaire semantics report"),
    ("climate_outcome", "temp/alb2005_oop_aggregation_policy_audit.csv", "ALB_2005 OOP aggregation policy stress-test audit"),
    ("climate_outcome", "result/alb2005_oop_aggregation_policy_summary.csv", "ALB_2005 OOP aggregation policy stress-test summary"),
    ("climate_outcome", "report/alb2005_oop_aggregation_policy_audit.md", "ALB_2005 OOP aggregation policy stress-test report"),
    ("climate_outcome", "temp/alb2005_skip_missing_semantics_audit.csv", "ALB_2005 skip/missing semantics audit"),
    ("climate_outcome", "result/alb2005_skip_missing_semantics_summary.csv", "ALB_2005 skip/missing semantics summary"),
    ("climate_outcome", "report/alb2005_skip_missing_semantics_audit.md", "ALB_2005 skip/missing semantics report"),
    ("climate_outcome", "temp/alb2005_consumption_oop_unit_period_audit.csv", "ALB_2005 consumption/OOP unit-period audit"),
    ("climate_outcome", "result/alb2005_consumption_oop_unit_period_summary.csv", "ALB_2005 consumption/OOP unit-period summary"),
    ("climate_outcome", "report/alb2005_consumption_oop_unit_period_audit.md", "ALB_2005 consumption/OOP unit-period report"),
    ("climate_outcome", "temp/alb2005_consumption_aggregate_metadata_crosswalk_audit.csv", "ALB_2005 consumption aggregate metadata crosswalk audit"),
    ("climate_outcome", "result/alb2005_consumption_aggregate_metadata_crosswalk_summary.csv", "ALB_2005 consumption aggregate metadata crosswalk summary"),
    ("climate_outcome", "report/alb2005_consumption_aggregate_metadata_crosswalk_audit.md", "ALB_2005 consumption aggregate metadata crosswalk report"),
    ("climate_outcome", "temp/alb2005_consumption_component_source_search_audit.csv", "ALB_2005 consumption component source-search audit"),
    ("climate_outcome", "result/alb2005_consumption_component_source_search_summary.csv", "ALB_2005 consumption component source-search summary"),
    ("climate_outcome", "report/alb2005_consumption_component_source_search_audit.md", "ALB_2005 consumption component source-search report"),
    ("climate_outcome", "temp/alb2005_timing_geography_source_search_audit.csv", "ALB_2005 timing/geography source-search audit"),
    ("climate_outcome", "result/alb2005_timing_geography_source_search_summary.csv", "ALB_2005 timing/geography source-search summary"),
    ("climate_outcome", "report/alb2005_timing_geography_source_search_audit.md", "ALB_2005 timing/geography source-search report"),
    ("raw_verification", "temp/alb2005_minimum_recipe_promotion_action_queue.csv", "ALB_2005 minimum recipe promotion action queue"),
    ("raw_verification", "temp/alb2005_minimum_recipe_promotion_gate_checklist.csv", "ALB_2005 minimum recipe promotion gate checklist"),
    ("raw_verification", "result/alb2005_minimum_recipe_promotion_summary.csv", "ALB_2005 minimum recipe promotion summary"),
    ("raw_verification", "report/alb2005_minimum_recipe_promotion_packet.md", "ALB_2005 minimum recipe promotion packet"),
    ("raw_verification", "temp/alb2005_public_fieldwork_geo_metadata_audit.csv", "ALB_2005 public fieldwork/geography metadata audit"),
    ("raw_verification", "result/alb2005_public_fieldwork_geo_metadata_summary.csv", "ALB_2005 public fieldwork/geography metadata summary"),
    ("raw_verification", "report/alb2005_public_fieldwork_geo_metadata_audit.md", "ALB_2005 public fieldwork/geography metadata report"),
    ("raw_verification", "temp/source_snapshots/first_batch_public_documentation/1_ALB_2005_LSMS_v01_M/metadata_ddi_xml.xml", "ALB_2005 saved public DDI metadata source"),
    ("raw_verification", "temp/alb2005_diary_timing_candidate_audit.csv", "ALB_2005 diary timing candidate audit"),
    ("raw_verification", "result/alb2005_diary_timing_candidate_summary.csv", "ALB_2005 diary timing candidate summary"),
    ("raw_verification", "report/alb2005_diary_timing_candidate_audit.md", "ALB_2005 diary timing candidate report"),
    ("raw_verification", "temp/raw_schema_inventory/Albania_2005_ALB_2005_LSMS_v01_M/Albania_2005_ALB_2005_LSMS_v01_M_variable_catalog.csv", "ALB_2005 metadata variable catalog"),
    ("raw_verification", "temp/alb2005_extracted_module_coverage_audit.csv", "ALB_2005 extracted module coverage audit"),
    ("raw_verification", "temp/alb2005_extracted_extra_files_audit.csv", "ALB_2005 extracted extra files audit"),
    ("raw_verification", "temp/alb2005_archive_member_manifest.csv", "ALB_2005 local archive member manifest"),
    ("raw_verification", "result/alb2005_extracted_module_coverage_summary.csv", "ALB_2005 extracted module coverage summary"),
    ("raw_verification", "report/alb2005_extracted_module_coverage_audit.md", "ALB_2005 extracted module coverage report"),
    ("raw_verification", "temp/alb2005_fallback_blocker_resolution_matrix.csv", "ALB_2005 fallback blocker resolution matrix"),
    ("raw_verification", "result/alb2005_fallback_blocker_resolution_summary.csv", "ALB_2005 fallback blocker resolution summary"),
    ("raw_verification", "report/alb2005_fallback_blocker_resolution_matrix.md", "ALB_2005 fallback blocker resolution report"),
    ("raw_verification", "temp/albania_first_analysis_promotion_gate_checklist.csv", "Albania first analysis promotion gate checklist"),
    ("raw_verification", "temp/albania_first_analysis_promotion_action_queue.csv", "Albania first analysis promotion action queue"),
    ("raw_verification", "result/albania_first_analysis_promotion_wave_ranking.csv", "Albania first analysis promotion wave ranking"),
    ("raw_verification", "result/albania_first_analysis_promotion_summary.csv", "Albania first analysis promotion summary"),
    ("raw_verification", "report/albania_first_analysis_promotion_gate.md", "Albania first analysis promotion gate report"),
    ("raw_verification", "temp/raw_schema_inventory/Albania_2005_ALB_2005_LSMS_v01_M/Albania_2005_ALB_2005_LSMS_v01_M_schema_files.csv", "ALB_2005 metadata schema file catalog"),
    ("raw_verification", "temp/albania_existing_raw_wave_audit.csv", "existing Albania raw wave audit"),
    ("raw_verification", "result/albania_existing_raw_wave_audit_summary.csv", "existing Albania raw wave audit summary"),
    ("raw_verification", "report/albania_existing_raw_wave_audit.md", "existing Albania raw wave audit report"),
    ("raw_verification", "temp/alb2008_household_core_candidate.csv", "ALB_2008 temp household core candidate"),
    ("raw_verification", "temp/alb2008_household_core_merge_audit.csv", "ALB_2008 household core merge audit"),
    ("raw_verification", "temp/alb2008_household_core_lineage.csv", "ALB_2008 household core lineage"),
    ("raw_verification", "result/alb2008_household_core_candidate_summary.csv", "ALB_2008 household core candidate summary"),
    ("raw_verification", "report/alb2008_household_core_merge_audit.md", "ALB_2008 household core merge audit report"),
    ("climate_outcome", "temp/alb2008_provisional_outcome_feasibility_audit.csv", "ALB_2008 provisional outcome feasibility audit"),
    ("climate_outcome", "result/alb2008_provisional_outcome_feasibility_summary.csv", "ALB_2008 provisional outcome feasibility summary"),
    ("climate_outcome", "report/alb2008_provisional_outcome_feasibility.md", "ALB_2008 provisional outcome feasibility report"),
    ("climate_outcome", "temp/alb2008_outcome_semantics_raw_value_audit.csv", "ALB_2008 outcome semantics raw value audit"),
    ("climate_outcome", "result/alb2008_outcome_semantics_raw_value_summary.csv", "ALB_2008 outcome semantics raw value summary"),
    ("climate_outcome", "report/alb2008_outcome_semantics_raw_value_audit.md", "ALB_2008 outcome semantics raw value report"),
    ("climate_outcome", "temp/alb2008_timing_geography_exhaustive_audit.csv", "ALB_2008 timing/geography exhaustive audit"),
    ("climate_outcome", "result/alb2008_timing_geography_exhaustive_summary.csv", "ALB_2008 timing/geography exhaustive summary"),
    ("climate_outcome", "report/alb2008_timing_geography_exhaustive_audit.md", "ALB_2008 timing/geography exhaustive report"),
    ("climate_outcome", "temp/alb2008_fallback_blocker_resolution_matrix.csv", "ALB_2008 fallback blocker resolution matrix"),
    ("climate_outcome", "result/alb2008_fallback_blocker_resolution_summary.csv", "ALB_2008 fallback blocker resolution summary"),
    ("climate_outcome", "report/alb2008_fallback_blocker_resolution_matrix.md", "ALB_2008 fallback blocker resolution report"),
    ("raw_access", "result/first_batch_dataset_verification_gate.csv", "first-batch dataset verification gate"),
    ("raw_access", "temp/first_batch_concept_verification_template.csv", "first-batch concept verification template"),
    ("raw_access", "temp/first_batch_variable_verification_template.csv", "first-batch variable verification template"),
    ("raw_access", "result/first_batch_raw_verification_workbook_summary.csv", "first-batch raw verification workbook summary"),
    ("raw_access", "report/first_batch_raw_verification_workbook.md", "first-batch raw verification workbook report"),
    ("schema", "temp/raw_schema_inventory/schema_study_inventory.csv", "metadata study inventory"),
    ("schema", "temp/raw_schema_inventory/schema_file_inventory.csv", "metadata file inventory"),
    ("schema", "temp/raw_schema_inventory/metadata_variable_catalog.csv", "metadata variable catalog"),
    ("schema", "temp/raw_schema_inventory/raw_file_inventory.csv", "raw file inventory"),
    ("schema", "temp/raw_schema_inventory/raw_variable_catalog.csv", "raw variable catalog"),
    ("variable_maps", "temp/variable_map_consumption.csv", "candidate consumption variables"),
    ("variable_maps", "temp/variable_map_health_expenditure.csv", "candidate OOP health expenditure variables"),
    ("variable_maps", "temp/variable_map_health_need_access.csv", "candidate health need/access variables"),
    ("variable_maps", "temp/variable_map_geography.csv", "candidate geography/timing variables"),
    ("variable_maps", "temp/variable_map_survey_design.csv", "candidate survey design variables"),
    ("variable_maps", "temp/variable_map_demographics.csv", "candidate demographic variables"),
    ("variable_maps", "temp/variable_map_shocks.csv", "candidate shock variables"),
    ("variable_maps", "temp/variable_map_confidence_audit.csv", "metadata-confidence audit"),
    ("raw_verification", "temp/raw_variable_verification_protocol.csv", "raw-variable verification protocol"),
    ("raw_verification", "temp/harmonization_recipe_scaffold.csv", "metadata-only harmonization scaffold"),
    ("raw_verification", "temp/harmonization_recipe_gate.csv", "harmonization recipe gate"),
    ("raw_verification", "temp/harmonization_value_audit_template.csv", "value/unit/recall audit template"),
    ("raw_verification", "result/harmonization_readiness_matrix.csv", "harmonization readiness by country-wave"),
    ("climate_outcome", "result/climate_linkage_readiness.csv", "climate linkage readiness by country-wave"),
    ("climate_outcome", "result/sdg382_denominator_country_wave_readiness.csv", "SDG 3.8.2 denominator readiness"),
    ("climate_outcome", "temp/outcome_denominator_plan.csv", "outcome construction gate plan"),
    ("modeling", "temp/modeling_identification_plan.csv", "modeling and identification readiness plan"),
    ("modeling", "result/mechanism_readiness_matrix.csv", "mechanism readiness matrix"),
    ("modeling", "result/empirical_readiness_dashboard.csv", "consolidated country-wave empirical readiness dashboard"),
    ("modeling", "result/empirical_no_go_threshold_status.csv", "pre-specified go/no-go rule status"),
    ("traceability", "result/completion_criteria_audit.csv", "completion criteria audit"),
    ("traceability", "result/workspace_validation_audit.csv", "workspace validation audit"),
    ("traceability", "result/objective_requirement_traceability.csv", "objective requirement traceability"),
    ("traceability", "result/objective_guardrail_audit.csv", "objective guardrail audit"),
    ("traceability", "result/objective_traceability_summary.csv", "objective traceability summary"),
    ("traceability", "result/direct_read_audit_bundle.csv", "direct-read bundle table"),
    ("traceability", "result/direct_read_artifact_manifest.csv", "direct-read artifact manifest"),
    ("traceability", "result/direct_read_audit_bundle_summary.csv", "direct-read bundle summary"),
    ("reproducibility", "Makefile", "one-command reproduction target"),
    ("reproducibility", "script/run_all.sh", "Unix-like full pipeline runner"),
    ("reproducibility", "script/run_all.ps1", "Windows full pipeline runner"),
    ("reproducibility", "script/36_build_direct_read_audit_bundle.py", "direct-read bundle generator"),
    ("reproducibility", "script/37_build_first_batch_raw_acquisition_checklist.py", "first-batch raw acquisition checklist generator"),
    ("reproducibility", "script/38_build_first_batch_raw_verification_workbook.py", "first-batch raw verification workbook generator"),
    ("reproducibility", "script/39_probe_first_batch_official_raw_access.py", "first-batch official raw access probe generator"),
    ("reproducibility", "script/124_build_priority_raw_intake_gate.py", "priority raw package intake gate generator"),
    ("reproducibility", "script/125_build_priority_climate_linkage_preflight.py", "priority climate linkage preflight generator"),
    ("reproducibility", "script/126_build_priority_raw_verification_workbook.py", "priority raw verification workbook generator"),
    ("reproducibility", "script/127_enforce_promoted_data_gate.py", "promoted data write gate enforcer"),
    ("reproducibility", "script/128_build_priority_archive_member_preflight.py", "priority archive/direct-file preflight generator"),
    ("reproducibility", "script/129_build_priority_manual_verification_decision_gate.py", "priority manual verification decision gate generator"),
    ("reproducibility", "script/130_build_priority_raw_package_receipt_ledger.py", "priority raw package receipt ledger generator"),
    ("reproducibility", "script/131_build_priority_official_download_dossier.py", "priority official download dossier generator"),
    ("reproducibility", "script/133_build_priority_public_documentation_receipt.py", "priority public documentation receipt generator"),
    ("reproducibility", "script/135_build_priority_official_metadata_evidence_extract.py", "priority official metadata evidence extractor"),
    ("reproducibility", "script/136_build_priority_credentialed_raw_acquisition_ledger.py", "priority credentialed raw acquisition ledger generator"),
    ("reproducibility", "script/137_probe_priority_official_endpoint_matrix.py", "priority official endpoint matrix probe"),
    ("reproducibility", "script/138_probe_priority_core_file_endpoint_matrix.py", "priority core file endpoint matrix probe"),
    ("reproducibility", "script/139_build_priority_threshold_acquisition_campaign.py", "priority threshold acquisition campaign generator"),
    ("reproducibility", "script/140_build_priority_first_pass_variable_review_queue.py", "priority first-pass variable review queue generator"),
    ("reproducibility", "script/141_build_priority_download_execution_packet.py", "priority manual download execution packet generator"),
    ("reproducibility", "script/142_build_priority_lsms_isa_alignment_audit.py", "priority LSMS/ISA alignment audit generator"),
    ("reproducibility", "script/143_build_priority_lsms_isa_refocused_acquisition_queue.py", "priority LSMS/ISA refocused acquisition queue generator"),
    ("reproducibility", "script/146_build_priority_lsms_isa_public_documentation_receipt.py", "priority LSMS/ISA public documentation receipt generator"),
    ("reproducibility", "script/147_build_priority_lsms_isa_variable_evidence_matrix.py", "priority LSMS/ISA official variable evidence matrix generator"),
    ("reproducibility", "script/144_build_priority_lsms_isa_raw_package_intake_packet.py", "priority LSMS/ISA raw package intake packet generator"),
    ("reproducibility", "script/145_build_priority_lsms_isa_archive_member_preflight.py", "priority LSMS/ISA archive/direct-file preflight generator"),
    ("reproducibility", "script/149_build_priority_lsms_isa_raw_value_verification_workbook.py", "priority LSMS/ISA raw value verification workbook generator"),
    ("reproducibility", "script/158_build_priority_lsms_isa_received_raw_value_profile.py", "priority LSMS/ISA received raw value profile generator"),
    ("reproducibility", "script/159_build_priority_lsms_isa_received_raw_semantics_review.py", "priority LSMS/ISA received raw semantics review generator"),
    ("reproducibility", "script/160_build_mwi2004_raw_requirement_verification.py", "Malawi 2004 focused raw requirement verification generator"),
    ("reproducibility", "script/161_build_mwi2004_requirement_acceptance_decisions.py", "Malawi 2004 focused requirement acceptance decision generator"),
    ("reproducibility", "script/162_build_mwi2004_health_access_label_skip_decisions.py", "Malawi 2004 health/access label-skip decision generator"),
    ("reproducibility", "script/163_build_mwi2004_health_exception_audit.py", "Malawi 2004 health person-key and skip exception audit generator"),
    ("reproducibility", "script/164_build_mwi2004_health_access_construction_policy.py", "Malawi 2004 candidate health/access construction policy generator"),
    ("reproducibility", "script/165_build_mwi2004_financial_protection_construction_policy.py", "Malawi 2004 financial-protection construction policy generator"),
    ("reproducibility", "script/189_build_mwi2004_sdg382_discretionary_budget_parameter_audit.py", "Malawi 2004 SDG 3.8.2 parameter audit generator"),
    ("reproducibility", "script/190_build_mwi2004_sdg382_external_parameter_source_ledger.py", "Malawi 2004 SDG 3.8.2 external parameter source ledger generator"),
    ("reproducibility", "script/191_build_mwi2004_sdg382_candidate_classification_precheck.py", "Malawi 2004 SDG 3.8.2 candidate classification precheck generator"),
    ("reproducibility", "script/192_build_mwi2004_sdg382_official_denominator_rule_audit.py", "Malawi 2004 SDG 3.8.2 official denominator rule audit generator"),
    ("reproducibility", "script/166_build_mwi2004_timing_geography_linkage_policy.py", "Malawi 2004 timing/geography linkage policy generator"),
    ("reproducibility", "script/167_build_mwi2004_access_person_key_resolution_policy.py", "Malawi 2004 access person-key resolution policy generator"),
    ("reproducibility", "script/168_build_mwi2004_missing_units_recall_skip_policy.py", "Malawi 2004 missing, units, recall, and skip policy generator"),
    ("reproducibility", "script/169_build_mwi2004_chirps_admin2_route_policy.py", "Malawi 2004 CHIRPS ADM2 route policy generator"),
    ("reproducibility", "script/170_extract_mwi2004_chirps_admin2_exposures.py", "Malawi 2004 CHIRPS ADM2 extraction generator"),
    ("reproducibility", "script/171_build_mwi2004_promoted_household_climate_dataset.py", "Malawi 2004 promoted household-climate dataset generator"),
    ("reproducibility", "script/172_build_priority_lsms_isa_next_raw_package_action_packet.py", "priority LSMS/ISA next raw package action packet generator"),
    ("reproducibility", "script/174_build_priority_lsms_isa_incoming_raw_package_router.py", "priority LSMS/ISA incoming raw package router generator"),
    ("reproducibility", "script/175_build_priority_lsms_isa_threshold_gap_control_panel.py", "priority LSMS/ISA threshold gap control panel generator"),
    ("reproducibility", "script/176_build_priority_lsms_isa_manual_download_packets.py", "priority LSMS/ISA manual download packet generator"),
    ("reproducibility", "script/177_build_priority_lsms_isa_manual_download_progress_tracker.py", "priority LSMS/ISA manual download progress tracker generator"),
    ("reproducibility", "script/178_build_priority_lsms_isa_post_download_validation_runner.py", "priority LSMS/ISA post-download validation runner generator"),
    ("reproducibility", "script/179_build_priority_lsms_isa_manual_download_execution_board.py", "priority LSMS/ISA manual download execution board generator"),
    ("reproducibility", "script/180_build_priority_lsms_isa_credentialed_download_handoff.py", "priority LSMS/ISA credentialed download handoff generator"),
    ("reproducibility", "script/181_probe_priority_lsms_isa_resource_download_routes.py", "priority LSMS/ISA public resource download route probe"),
    ("reproducibility", "script/182_build_priority_lsms_isa_download_acceptance_matrix.py", "priority LSMS/ISA download acceptance matrix generator"),
    ("reproducibility", "script/183_build_priority_lsms_isa_local_target_readmes.py", "priority LSMS/ISA local target readme generator"),
    ("reproducibility", "script/184_build_priority_lsms_isa_minimum_batch_raw_value_queue.py", "priority LSMS/ISA minimum-batch raw-value queue generator"),
    ("reproducibility", "script/185_build_priority_lsms_isa_target_folder_receipt_smoke_test.py", "priority LSMS/ISA target-folder receipt smoke-test generator"),
    ("reproducibility", "script/186_build_priority_lsms_isa_threshold_replacement_plan.py", "priority LSMS/ISA threshold replacement plan generator"),
    ("reproducibility", "script/187_build_priority_lsms_isa_minimum_batch_climate_linkage_review_queue.py", "priority LSMS/ISA minimum-batch climate linkage review queue generator"),
    ("reproducibility", "script/188_build_priority_lsms_isa_local_stray_raw_package_locator.py", "priority LSMS/ISA local stray raw package locator generator"),
    ("reproducibility", "script/173_build_priority_lsms_isa_promotion_gate_dashboard.py", "priority LSMS/ISA promotion gate dashboard generator"),
    ("reproducibility", "script/193_build_priority_lsms_isa_minimum_batch_promotion_unlock_board.py", "priority LSMS/ISA minimum-batch promotion unlock board generator"),
    ("reproducibility", "script/194_build_priority_lsms_isa_worldbank_session_bootstrap.py", "priority LSMS/ISA World Bank session bootstrap generator"),
    ("reproducibility", "script/195_build_priority_lsms_isa_credentialed_fetch_command_packet.py", "priority LSMS/ISA credentialed fetch command packet generator"),
    ("reproducibility", "script/196_build_priority_lsms_isa_browser_download_starter.py", "priority LSMS/ISA browser download starter generator"),
    ("reproducibility", "script/197_build_priority_lsms_isa_first_canary_runbook.py", "priority LSMS/ISA first canary runbook generator"),
    ("reproducibility", "script/198_build_priority_lsms_isa_local_raw_presence_audit.py", "priority LSMS/ISA local raw presence audit generator"),
    ("reproducibility", "script/199_build_priority_lsms_isa_acquisition_to_promotion_handoff.py", "priority LSMS/ISA acquisition-to-promotion handoff generator"),
    ("reproducibility", "script/200_build_priority_lsms_isa_dataset_scope_lock.py", "priority LSMS/ISA dataset scope lock generator"),
    ("reproducibility", "script/201_build_priority_lsms_isa_acquisition_route_decision.py", "priority LSMS/ISA acquisition route decision generator"),
    ("reproducibility", "script/202_build_priority_lsms_isa_scoped_incoming_package_router.py", "priority LSMS/ISA scoped incoming package router generator"),
    ("reproducibility", "script/203_build_priority_lsms_isa_webgpt_download_control_manifest.py", "priority LSMS/ISA Web GPT download control manifest generator"),
    ("reproducibility", "script/150_build_priority_lsms_isa_raw_package_receipt_checklist.py", "priority LSMS/ISA raw package receipt checklist generator"),
    ("reproducibility", "script/152_build_priority_lsms_isa_credentialed_raw_acquisition_workbench.py", "priority LSMS/ISA credentialed raw acquisition workbench generator"),
    ("reproducibility", "script/153_validate_priority_lsms_isa_official_file_receipt.py", "priority LSMS/ISA official file receipt validator"),
    ("reproducibility", "script/154_build_priority_lsms_isa_threshold_download_sequence.py", "priority LSMS/ISA threshold download sequence generator"),
    ("reproducibility", "script/155_build_priority_lsms_isa_minimum_batch_raw_intake_guide.py", "priority LSMS/ISA minimum-batch raw intake guide generator"),
    ("reproducibility", "script/156_probe_priority_lsms_isa_minimum_batch_endpoint_refresh.py", "priority LSMS/ISA minimum-batch endpoint refresh generator"),
    ("reproducibility", "script/132_build_priority_analysis_dataset_synthesis_blueprint.py", "priority analysis dataset synthesis blueprint generator"),
    ("reproducibility", "script/134_build_priority_country_wave_promotion_packets.py", "priority country-wave promotion packet generator"),
    ("reproducibility", "script/148_build_priority_lsms_isa_country_wave_promotion_packets.py", "priority LSMS/ISA country-wave promotion packet generator"),
    ("reproducibility", "script/151_refresh_refocused_promoted_country_wave_registry.py", "refocused LSMS/ISA promoted registry refresher"),
    ("reproducibility", "script/40_build_first_batch_manual_download_handoff.py", "first-batch manual download handoff generator"),
    ("reproducibility", "script/41_build_first_batch_public_documentation_audit.py", "first-batch public documentation audit generator"),
    ("reproducibility", "script/42_build_first_batch_file_source_traceability.py", "first-batch file source traceability generator"),
    ("reproducibility", "script/43_build_first_batch_merge_key_lineage_plan.py", "first-batch merge-key lineage generator"),
    ("reproducibility", "script/44_download_public_external_raw_candidates.py", "public external raw candidate downloader"),
    ("reproducibility", "script/45_audit_first_batch_raw_value_keys.py", "first-batch raw value/key audit generator"),
    ("reproducibility", "script/54_audit_alb2002_household_core_merge.py", "ALB_2002 household core merge audit generator"),
    ("reproducibility", "script/100_audit_alb2002_weight_design_evidence.py", "ALB_2002 weight/design evidence audit generator"),
    ("reproducibility", "script/55_audit_alb2002_provisional_outcome_feasibility.py", "ALB_2002 provisional outcome feasibility generator"),
    ("reproducibility", "script/60_audit_alb2002_outcome_semantics_raw_values.py", "ALB_2002 outcome semantics raw value audit generator"),
    ("reproducibility", "script/89_audit_alb2002_health_questionnaire_semantics.py", "ALB_2002 health questionnaire semantics audit generator"),
    ("reproducibility", "script/91_audit_alb2002_oop_aggregation_policy.py", "ALB_2002 OOP aggregation policy audit generator"),
    ("reproducibility", "script/92_audit_alb2002_skip_missing_semantics.py", "ALB_2002 skip/missing semantics audit generator"),
    ("reproducibility", "script/97_audit_alb2002_oop_skip_value_decision.py", "ALB_2002 OOP skip-value decision audit generator"),
    ("reproducibility", "script/93_audit_alb2002_access_need_denominator_policy.py", "ALB_2002 access/need denominator policy audit generator"),
    ("reproducibility", "script/105_build_alb2002_access_candidate_outcomes.py", "ALB_2002 access candidate outcome generator"),
    ("reproducibility", "script/94_audit_alb2002_consumption_sdg_denominator_policy.py", "ALB_2002 consumption/SDG denominator policy audit generator"),
    ("reproducibility", "script/96_audit_alb2002_consumption_construction_sources.py", "ALB_2002 public consumption-construction source audit generator"),
    ("reproducibility", "script/95_audit_alb2002_consumption_aggregate_metadata_crosswalk.py", "ALB_2002 consumption aggregate metadata crosswalk generator"),
    ("reproducibility", "script/99_audit_alb2002_period_aligned_che_policy.py", "ALB_2002 period-aligned CHE policy audit generator"),
    ("reproducibility", "script/90_build_alb2002_minimum_recipe_promotion_packet.py", "ALB_2002 minimum recipe promotion packet generator"),
    ("reproducibility", "script/101_build_alb2002_che_candidate_outcomes.py", "ALB_2002 CHE candidate outcome generator"),
    ("reproducibility", "script/106_build_alb2002_uhc_composite_candidate_outcomes.py", "ALB_2002 composite UHC candidate outcome generator"),
    ("reproducibility", "script/102_build_alb2002_analysis_candidate_dataset.py", "ALB_2002 joined analysis candidate generator"),
    ("reproducibility", "script/117_promote_alb2002_harmonized_household_core.py", "ALB_2002 limited harmonized household core generator"),
    ("reproducibility", "script/119_promote_alb2002_limited_financial_outcomes.py", "ALB_2002 limited financial outcome generator"),
    ("reproducibility", "script/103_build_alb2002_climate_centroid_exposure_candidates.py", "ALB_2002 climate centroid exposure candidate generator"),
    ("reproducibility", "script/107_build_alb2002_climate_shock_candidate_audit.py", "ALB_2002 climate shock diagnostic candidate generator"),
    ("reproducibility", "script/118_promote_alb2002_limited_climate_exposures.py", "ALB_2002 limited climate exposure generator"),
    ("reproducibility", "script/120_promote_alb2002_limited_climate_linked.py", "ALB_2002 limited climate-linked diagnostic generator"),
    ("reproducibility", "script/108_build_alb2002_climate_outcome_linked_candidate_audit.py", "ALB_2002 climate/outcome linked candidate generator"),
    ("reproducibility", "script/109_build_alb2002_linked_candidate_descriptive_diagnostics.py", "ALB_2002 linked-candidate descriptive screen generator"),
    ("reproducibility", "script/110_build_current_design_scorecard.py", "current design scorecard generator"),
    ("reproducibility", "script/111_audit_alb2002_promotion_gate_delta.py", "ALB_2002 promotion gate delta audit generator"),
    ("reproducibility", "script/112_build_alb2002_boundary_blocker_resolution_matrix.py", "ALB_2002 boundary blocker resolution matrix generator"),
    ("reproducibility", "script/113_build_alb2002_outcome_blocker_resolution_matrix.py", "ALB_2002 outcome blocker resolution matrix generator"),
    ("reproducibility", "script/98_audit_analysis_dataset_promotion_barriers.py", "analysis dataset promotion barrier audit generator"),
    ("reproducibility", "script/56_audit_alb2002_district_climate_crosswalk.py", "ALB_2002 district climate crosswalk generator"),
    ("reproducibility", "script/64_audit_alb2002_boundary_name_match.py", "ALB_2002 public boundary name match audit generator"),
    ("reproducibility", "script/69_audit_alb2002_boundary_source_alternatives.py", "ALB_2002 boundary source alternatives audit generator"),
    ("reproducibility", "script/70_audit_alb2002_local_geography_artifacts.py", "ALB_2002 local geography artifact audit generator"),
    ("reproducibility", "script/79_audit_alb2002_boundary_source_resource_search.py", "ALB_2002 boundary source resource-search audit generator"),
    ("reproducibility", "script/80_audit_alb2002_boundary_geometry_provenance.py", "ALB_2002 boundary geometry/provenance audit generator"),
    ("reproducibility", "script/81_build_alb2002_boundary_manual_verification_packet.py", "ALB_2002 boundary manual verification packet generator"),
    ("reproducibility", "script/82_audit_alb2002_boundary_manual_source_followup.py", "ALB_2002 boundary manual source follow-up generator"),
    ("reproducibility", "script/88_audit_alb2002_gadm_boundary_lead.py", "ALB_2002 GADM boundary lead audit generator"),
    ("reproducibility", "script/57_audit_alb2012_raw_core_feasibility.py", "ALB_2012 raw core feasibility generator"),
    ("reproducibility", "script/58_audit_alb2012_provisional_outcome_feasibility.py", "ALB_2012 provisional outcome feasibility generator"),
    ("reproducibility", "script/63_audit_alb2012_outcome_semantics_raw_values.py", "ALB_2012 outcome semantics raw value audit generator"),
    ("reproducibility", "script/59_audit_alb2012_timing_geography_exhaustive.py", "ALB_2012 timing/geography exhaustive audit generator"),
    ("reproducibility", "script/65_audit_alb2012_questionnaire_timing_fields.py", "ALB_2012 questionnaire timing field audit generator"),
    ("reproducibility", "script/114_build_alb2012_timing_geography_blocker_resolution_matrix.py", "ALB_2012 timing/geography blocker resolution generator"),
    ("reproducibility", "script/66_audit_albania_legacy_questionnaire_readability.py", "Albania legacy questionnaire readability audit generator"),
    ("reproducibility", "script/67_audit_albania_legacy_questionnaire_timing_fields.py", "Albania legacy questionnaire timing field audit generator"),
    ("reproducibility", "script/48_audit_alb2005_provisional_outcome_feasibility.py", "ALB_2005 provisional outcome feasibility generator"),
    ("reproducibility", "script/61_audit_alb2005_outcome_semantics_raw_values.py", "ALB_2005 outcome semantics raw value audit generator"),
    ("reproducibility", "script/49_audit_alb2005_timing_geography_exhaustive.py", "ALB_2005 timing/geography exhaustive audit generator"),
    ("reproducibility", "script/68_build_alb2005_harmonization_value_decision_audit.py", "ALB_2005 harmonization value decision audit generator"),
    ("reproducibility", "script/71_audit_alb2005_required_value_key_evidence.py", "ALB_2005 required value/key audit generator"),
    ("reproducibility", "script/72_audit_alb2005_health_questionnaire_semantics.py", "ALB_2005 health questionnaire semantics audit generator"),
    ("reproducibility", "script/73_audit_alb2005_oop_aggregation_policy.py", "ALB_2005 OOP aggregation policy audit generator"),
    ("reproducibility", "script/74_audit_alb2005_skip_missing_semantics.py", "ALB_2005 skip/missing semantics audit generator"),
    ("reproducibility", "script/75_audit_alb2005_consumption_oop_unit_period.py", "ALB_2005 consumption/OOP unit-period audit generator"),
    ("reproducibility", "script/76_audit_alb2005_consumption_aggregate_metadata_crosswalk.py", "ALB_2005 consumption aggregate metadata crosswalk audit generator"),
    ("reproducibility", "script/77_audit_alb2005_consumption_component_source_search.py", "ALB_2005 consumption component source-search audit generator"),
    ("reproducibility", "script/78_audit_alb2005_timing_geography_source_search.py", "ALB_2005 timing/geography source-search audit generator"),
    ("reproducibility", "script/83_build_alb2005_minimum_recipe_promotion_packet.py", "ALB_2005 minimum recipe promotion packet generator"),
    ("reproducibility", "script/84_audit_alb2005_public_fieldwork_geo_metadata.py", "ALB_2005 public fieldwork/geography metadata audit generator"),
    ("reproducibility", "script/85_audit_alb2005_diary_timing_candidates.py", "ALB_2005 diary timing candidate audit generator"),
    ("reproducibility", "script/86_audit_alb2005_extracted_module_coverage.py", "ALB_2005 extracted module coverage audit generator"),
    ("reproducibility", "script/87_build_albania_first_analysis_promotion_gate.py", "Albania first analysis promotion gate generator"),
    ("reproducibility", "script/115_build_alb2005_fallback_blocker_resolution_matrix.py", "ALB_2005 fallback blocker resolution generator"),
    ("reproducibility", "script/50_audit_existing_albania_raw_waves.py", "existing Albania raw wave audit generator"),
    ("reproducibility", "script/51_audit_alb2008_household_core_merge.py", "ALB_2008 household core merge audit generator"),
    ("reproducibility", "script/52_audit_alb2008_provisional_outcome_feasibility.py", "ALB_2008 provisional outcome feasibility generator"),
    ("reproducibility", "script/62_audit_alb2008_outcome_semantics_raw_values.py", "ALB_2008 outcome semantics raw value audit generator"),
    ("reproducibility", "script/53_audit_alb2008_timing_geography_exhaustive.py", "ALB_2008 timing/geography exhaustive audit generator"),
    ("reproducibility", "script/116_build_alb2008_fallback_blocker_resolution_matrix.py", "ALB_2008 fallback blocker resolution generator"),
]

GENERATED_ARTIFACTS = {BUNDLE_PATH, MANIFEST_PATH, SUMMARY_PATH, REPORT_PATH}


def read_csv_dicts(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def row_count(path: Path) -> int:
    if not path.exists() or not path.is_file():
        return 0
    if path.suffix.lower() == ".csv":
        return len(read_csv_dicts(path))
    if path.suffix.lower() in BINARY_ROWLESS_SUFFIXES:
        return 0
    try:
        return len(path.read_text(encoding="utf-8", errors="replace").splitlines())
    except UnicodeDecodeError:
        return 0


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(TEMP_DIR.parent)).replace("\\", "/")
    except ValueError:
        return str(path).replace("\\", "/")


def project_path(relative_path: str) -> Path:
    return TEMP_DIR.parent / relative_path


def status_from_exists(path: Path) -> str:
    return "present" if path.exists() and path.is_file() and path.stat().st_size > 0 else "missing"


def csv_value(rows: list[dict[str, str]], metric: str, default: str = "0") -> str:
    for row in rows:
        if row.get("metric") == metric:
            return row.get("value", default)
    return default


def int_value(value: Any, default: int = 0) -> int:
    try:
        return int(float(str(value)))
    except (TypeError, ValueError):
        return default


def artifact_list(paths: list[Path]) -> str:
    return ";".join(rel(path) for path in paths)


def add_bundle(
    rows: list[dict[str, str]],
    section: str,
    item: str,
    status: str,
    value: str,
    artifacts: list[Path],
    interpretation: str,
) -> None:
    rows.append(
        {
            "section": section,
            "item": item,
            "status": status,
            "value": value,
            "evidence_artifacts": artifact_list(artifacts),
            "interpretation": interpretation,
        }
    )


def build_manifest() -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for group, relative_path, role in CURATED_ARTIFACTS:
        path = project_path(relative_path)
        exists = path.exists() and path.is_file()
        is_generated = any(path == generated for generated in GENERATED_ARTIFACTS)
        rows.append(
            {
                "artifact_group": group,
                "relative_path": relative_path,
                "exists": "1" if exists else "0",
                "bytes": str(path.stat().st_size) if exists else "0",
                "rows": str(row_count(path)) if exists else "0",
                "sha256": "" if is_generated else sha256_file(path) if exists else "",
                "role": role,
                "current_status": "present_nonempty" if exists and path.stat().st_size > 0 else "missing_or_empty",
            }
        )
    return rows


def build_bundle(manifest: list[dict[str, str]]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    completion = read_csv_dicts(RESULT_DIR / "completion_criteria_audit.csv")
    workspace_validation = read_csv_dicts(RESULT_DIR / "workspace_validation_audit.csv")
    empirical_summary = read_csv_dicts(RESULT_DIR / "empirical_readiness_dashboard_summary.csv")
    no_go = read_csv_dicts(RESULT_DIR / "empirical_no_go_threshold_status.csv")
    dashboard = read_csv_dicts(RESULT_DIR / "empirical_readiness_dashboard.csv")
    first_batch_summary = read_csv_dicts(RESULT_DIR / "first_batch_raw_acquisition_summary.csv")
    first_batch = read_csv_dicts(TEMP_DIR / "first_batch_raw_acquisition_checklist.csv")
    first_batch_access_summary = read_csv_dicts(RESULT_DIR / "first_batch_official_raw_access_summary.csv")
    priority_raw_intake_summary = read_csv_dicts(RESULT_DIR / "priority_raw_intake_gate_summary.csv")
    priority_archive_summary = read_csv_dicts(RESULT_DIR / "priority_archive_member_preflight_summary.csv")
    priority_climate_preflight_summary = read_csv_dicts(RESULT_DIR / "priority_climate_linkage_preflight_summary.csv")
    priority_raw_verification_summary = read_csv_dicts(RESULT_DIR / "priority_raw_verification_workbook_summary.csv")
    priority_manual_verification_summary = read_csv_dicts(RESULT_DIR / "priority_manual_verification_decision_summary.csv")
    priority_receipt_summary = read_csv_dicts(RESULT_DIR / "priority_raw_package_receipt_summary.csv")
    priority_official_download_summary = read_csv_dicts(RESULT_DIR / "priority_official_download_dossier_summary.csv")
    priority_public_documentation_summary = read_csv_dicts(RESULT_DIR / "priority_public_documentation_receipt_summary.csv")
    priority_official_metadata_summary = read_csv_dicts(RESULT_DIR / "priority_official_metadata_evidence_summary.csv")
    priority_credentialed_acquisition_summary = read_csv_dicts(RESULT_DIR / "priority_credentialed_raw_acquisition_summary.csv")
    priority_endpoint_matrix_summary = read_csv_dicts(RESULT_DIR / "priority_official_endpoint_matrix_summary.csv")
    priority_core_file_endpoint_summary = read_csv_dicts(RESULT_DIR / "priority_core_file_endpoint_matrix_summary.csv")
    priority_threshold_campaign_summary = read_csv_dicts(RESULT_DIR / "priority_threshold_acquisition_campaign_summary.csv")
    priority_first_pass_summary = read_csv_dicts(RESULT_DIR / "priority_first_pass_variable_review_summary.csv")
    priority_download_execution_summary = read_csv_dicts(RESULT_DIR / "priority_download_execution_packet_summary.csv")
    priority_lsms_alignment_summary = read_csv_dicts(RESULT_DIR / "priority_lsms_isa_alignment_summary.csv")
    priority_lsms_refocused_summary = read_csv_dicts(RESULT_DIR / "priority_lsms_isa_refocused_acquisition_summary.csv")
    priority_lsms_public_docs_summary = read_csv_dicts(RESULT_DIR / "priority_lsms_isa_public_documentation_receipt_summary.csv")
    priority_lsms_variable_evidence_summary = read_csv_dicts(RESULT_DIR / "priority_lsms_isa_variable_evidence_summary.csv")
    priority_lsms_raw_intake_summary = read_csv_dicts(RESULT_DIR / "priority_lsms_isa_raw_package_intake_summary.csv")
    priority_lsms_archive_preflight_summary = read_csv_dicts(RESULT_DIR / "priority_lsms_isa_archive_member_preflight_summary.csv")
    priority_lsms_raw_value_workbook_summary = read_csv_dicts(RESULT_DIR / "priority_lsms_isa_raw_value_verification_workbook_summary.csv")
    priority_lsms_received_raw_schema_summary = read_csv_dicts(RESULT_DIR / "priority_lsms_isa_received_raw_schema_audit_summary.csv")
    priority_lsms_received_raw_value_profile_summary = read_csv_dicts(RESULT_DIR / "priority_lsms_isa_received_raw_value_profile_summary.csv")
    priority_lsms_received_raw_semantics_summary = read_csv_dicts(RESULT_DIR / "priority_lsms_isa_received_raw_semantics_review_summary.csv")
    mwi2004_raw_requirement_summary = read_csv_dicts(RESULT_DIR / "mwi2004_raw_requirement_verification_summary.csv")
    mwi2004_acceptance_summary = read_csv_dicts(RESULT_DIR / "mwi2004_requirement_acceptance_summary.csv")
    mwi2004_financial_policy_summary = read_csv_dicts(RESULT_DIR / "mwi2004_financial_protection_construction_policy_summary.csv")
    mwi2004_sdg382_parameter_summary = read_csv_dicts(RESULT_DIR / "mwi2004_sdg382_discretionary_budget_parameter_summary.csv")
    mwi2004_sdg382_external_parameter_summary = read_csv_dicts(RESULT_DIR / "mwi2004_sdg382_external_parameter_candidate_summary.csv")
    mwi2004_sdg382_candidate_precheck_summary = read_csv_dicts(RESULT_DIR / "mwi2004_sdg382_candidate_classification_precheck_summary.csv")
    mwi2004_sdg382_denominator_rule_summary = read_csv_dicts(RESULT_DIR / "mwi2004_sdg382_official_denominator_rule_summary.csv")
    mwi2004_timing_geography_summary = read_csv_dicts(RESULT_DIR / "mwi2004_timing_geography_linkage_policy_summary.csv")
    mwi2004_chirps_route_summary = read_csv_dicts(RESULT_DIR / "mwi2004_chirps_admin2_route_policy_summary.csv")
    mwi2004_chirps_extraction_summary = read_csv_dicts(RESULT_DIR / "mwi2004_chirps_admin2_extraction_summary.csv")
    mwi2004_health_access_summary = read_csv_dicts(RESULT_DIR / "mwi2004_health_access_label_skip_summary.csv")
    mwi2004_health_exception_summary = read_csv_dicts(RESULT_DIR / "mwi2004_health_exception_summary.csv")
    mwi2004_health_policy_summary = read_csv_dicts(RESULT_DIR / "mwi2004_health_access_construction_policy_summary.csv")
    mwi2004_access_resolution_summary = read_csv_dicts(RESULT_DIR / "mwi2004_access_person_key_resolution_policy_summary.csv")
    mwi2004_missing_units_summary = read_csv_dicts(RESULT_DIR / "mwi2004_missing_units_recall_skip_policy_summary.csv")
    mwi2004_promoted_dataset_summary = read_csv_dicts(RESULT_DIR / "mwi2004_promoted_household_climate_dataset_summary.csv")
    priority_lsms_receipt_checklist_summary = read_csv_dicts(RESULT_DIR / "priority_lsms_isa_raw_package_receipt_checklist_summary.csv")
    priority_lsms_credentialed_workbench_summary = read_csv_dicts(RESULT_DIR / "priority_lsms_isa_credentialed_raw_acquisition_workbench_summary.csv")
    priority_lsms_official_file_receipt_summary = read_csv_dicts(RESULT_DIR / "priority_lsms_isa_official_file_receipt_validator_summary.csv")
    priority_lsms_threshold_sequence_summary = read_csv_dicts(RESULT_DIR / "priority_lsms_isa_threshold_download_sequence_summary.csv")
    priority_lsms_minimum_intake_summary = read_csv_dicts(RESULT_DIR / "priority_lsms_isa_minimum_batch_raw_intake_guide_summary.csv")
    priority_lsms_minimum_endpoint_summary = read_csv_dicts(RESULT_DIR / "priority_lsms_isa_minimum_batch_endpoint_refresh_summary.csv")
    priority_lsms_next_raw_package_summary = read_csv_dicts(RESULT_DIR / "priority_lsms_isa_next_raw_package_action_summary.csv")
    priority_lsms_incoming_router_summary = read_csv_dicts(RESULT_DIR / "priority_lsms_isa_incoming_raw_package_router_summary.csv")
    priority_lsms_threshold_gap_summary = read_csv_dicts(RESULT_DIR / "priority_lsms_isa_threshold_gap_control_panel_summary.csv")
    priority_lsms_manual_download_packet_summary = read_csv_dicts(RESULT_DIR / "priority_lsms_isa_manual_download_packet_summary.csv")
    priority_lsms_manual_download_progress_summary = read_csv_dicts(RESULT_DIR / "priority_lsms_isa_manual_download_progress_summary.csv")
    priority_lsms_post_download_validation_summary = read_csv_dicts(RESULT_DIR / "priority_lsms_isa_post_download_validation_runner_summary.csv")
    priority_lsms_manual_download_execution_board_summary = read_csv_dicts(RESULT_DIR / "priority_lsms_isa_manual_download_execution_board_summary.csv")
    priority_lsms_credentialed_download_handoff_summary = read_csv_dicts(RESULT_DIR / "priority_lsms_isa_credentialed_download_handoff_summary.csv")
    priority_lsms_resource_download_route_probe_summary = read_csv_dicts(RESULT_DIR / "priority_lsms_isa_resource_download_route_probe_summary.csv")
    priority_lsms_download_acceptance_summary = read_csv_dicts(RESULT_DIR / "priority_lsms_isa_download_acceptance_matrix_summary.csv")
    priority_lsms_local_target_readme_summary = read_csv_dicts(RESULT_DIR / "priority_lsms_isa_local_target_readme_summary.csv")
    priority_lsms_minimum_batch_raw_value_queue_summary = read_csv_dicts(RESULT_DIR / "priority_lsms_isa_minimum_batch_raw_value_queue_summary.csv")
    priority_lsms_target_folder_smoke_summary = read_csv_dicts(RESULT_DIR / "priority_lsms_isa_target_folder_receipt_smoke_test_summary.csv")
    priority_lsms_threshold_replacement_summary = read_csv_dicts(RESULT_DIR / "priority_lsms_isa_threshold_replacement_plan_summary.csv")
    priority_lsms_minimum_climate_review_summary = read_csv_dicts(RESULT_DIR / "priority_lsms_isa_minimum_batch_climate_linkage_review_summary.csv")
    priority_lsms_local_stray_locator_summary = read_csv_dicts(RESULT_DIR / "priority_lsms_isa_local_stray_raw_package_locator_summary.csv")
    priority_lsms_promotion_gate_summary = read_csv_dicts(RESULT_DIR / "priority_lsms_isa_promotion_gate_dashboard_summary.csv")
    priority_lsms_unlock_summary = read_csv_dicts(RESULT_DIR / "priority_lsms_isa_minimum_batch_promotion_unlock_summary.csv")
    priority_lsms_worldbank_session_summary = read_csv_dicts(RESULT_DIR / "priority_lsms_isa_worldbank_session_bootstrap_summary.csv")
    priority_lsms_fetch_command_summary = read_csv_dicts(RESULT_DIR / "priority_lsms_isa_credentialed_fetch_command_packet_summary.csv")
    priority_lsms_browser_starter_summary = read_csv_dicts(RESULT_DIR / "priority_lsms_isa_browser_download_starter_summary.csv")
    priority_lsms_first_canary_summary = read_csv_dicts(RESULT_DIR / "priority_lsms_isa_first_canary_runbook_summary.csv")
    priority_lsms_raw_presence_summary = read_csv_dicts(RESULT_DIR / "priority_lsms_isa_local_raw_presence_summary.csv")
    priority_lsms_handoff_summary = read_csv_dicts(RESULT_DIR / "priority_lsms_isa_acquisition_to_promotion_handoff_summary.csv")
    priority_lsms_scope_lock_summary = read_csv_dicts(RESULT_DIR / "priority_lsms_isa_dataset_scope_lock_summary.csv")
    priority_lsms_acquisition_route_summary = read_csv_dicts(RESULT_DIR / "priority_lsms_isa_acquisition_route_decision_summary.csv")
    priority_lsms_scoped_incoming_summary = read_csv_dicts(RESULT_DIR / "priority_lsms_isa_scoped_incoming_package_router_summary.csv")
    priority_lsms_webgpt_download_summary = read_csv_dicts(RESULT_DIR / "priority_lsms_isa_webgpt_download_control_summary.csv")
    priority_synthesis_summary = read_csv_dicts(RESULT_DIR / "priority_analysis_dataset_synthesis_blueprint_summary.csv")
    priority_packet_summary = read_csv_dicts(RESULT_DIR / "priority_country_wave_promotion_packet_summary.csv")
    priority_lsms_packet_summary = read_csv_dicts(RESULT_DIR / "priority_lsms_isa_country_wave_promotion_packet_summary.csv")
    promoted_data_gate_summary = read_csv_dicts(RESULT_DIR / "promoted_data_gate_summary.csv")
    public_external_summary = read_csv_dicts(RESULT_DIR / "public_external_raw_candidate_download_summary.csv")
    first_batch_handoff_summary = read_csv_dicts(RESULT_DIR / "first_batch_manual_download_handoff_summary.csv")
    first_batch_documentation_summary = read_csv_dicts(RESULT_DIR / "first_batch_public_documentation_summary.csv")
    first_batch_file_source_summary = read_csv_dicts(RESULT_DIR / "first_batch_file_source_traceability_summary.csv")
    first_batch_merge_key_summary = read_csv_dicts(RESULT_DIR / "first_batch_merge_key_lineage_summary.csv")
    first_batch_value_key_summary = read_csv_dicts(RESULT_DIR / "first_batch_raw_value_key_summary.csv")
    alb2002_core_summary = read_csv_dicts(RESULT_DIR / "alb2002_household_core_candidate_summary.csv")
    alb2002_weight_design_summary = read_csv_dicts(RESULT_DIR / "alb2002_weight_design_evidence_summary.csv")
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
    alb2002_harmonized_core_summary = read_csv_dicts(RESULT_DIR / "alb2002_harmonized_household_core_promotion_summary.csv")
    alb2002_limited_financial_summary = read_csv_dicts(RESULT_DIR / "alb2002_limited_financial_outcome_promotion_summary.csv")
    alb2002_climate_centroid_summary = read_csv_dicts(RESULT_DIR / "alb2002_climate_centroid_exposure_summary.csv")
    alb2002_climate_shock_summary = read_csv_dicts(RESULT_DIR / "alb2002_climate_shock_candidate_summary.csv")
    alb2002_limited_climate_summary = read_csv_dicts(RESULT_DIR / "alb2002_limited_climate_exposure_promotion_summary.csv")
    alb2002_limited_linked_summary = read_csv_dicts(RESULT_DIR / "alb2002_limited_climate_linked_promotion_summary.csv")
    alb2002_climate_outcome_linked_summary = read_csv_dicts(RESULT_DIR / "alb2002_climate_outcome_linked_candidate_summary.csv")
    alb2002_linked_candidate_descriptive_summary = read_csv_dicts(RESULT_DIR / "alb2002_linked_candidate_descriptive_summary.csv")
    alb2002_minimum_recipe_summary = read_csv_dicts(RESULT_DIR / "alb2002_minimum_recipe_promotion_summary.csv")
    analysis_promotion_summary = read_csv_dicts(RESULT_DIR / "analysis_dataset_promotion_barrier_summary.csv")
    design_scorecard_current_summary = read_csv_dicts(RESULT_DIR / "design_scorecard_current_summary.csv")
    alb2002_promotion_gate_delta_summary = read_csv_dicts(RESULT_DIR / "alb2002_promotion_gate_delta_summary.csv")
    alb2002_boundary_blocker_summary = read_csv_dicts(RESULT_DIR / "alb2002_boundary_blocker_resolution_summary.csv")
    alb2002_outcome_blocker_summary = read_csv_dicts(RESULT_DIR / "alb2002_outcome_blocker_resolution_summary.csv")
    alb2002_crosswalk_summary = read_csv_dicts(RESULT_DIR / "alb2002_district_climate_crosswalk_summary.csv")
    alb2002_boundary_name_summary = read_csv_dicts(RESULT_DIR / "alb2002_boundary_name_match_summary.csv")
    alb2002_boundary_source_summary = read_csv_dicts(RESULT_DIR / "alb2002_boundary_source_alternative_summary.csv")
    alb2002_boundary_resource_summary = read_csv_dicts(RESULT_DIR / "alb2002_boundary_source_resource_search_summary.csv")
    alb2002_boundary_geometry_summary = read_csv_dicts(RESULT_DIR / "alb2002_boundary_geometry_provenance_summary.csv")
    alb2002_boundary_manual_summary = read_csv_dicts(RESULT_DIR / "alb2002_boundary_manual_verification_packet_summary.csv")
    alb2002_boundary_followup_summary = read_csv_dicts(RESULT_DIR / "alb2002_boundary_manual_source_followup_summary.csv")
    alb2002_local_geo_summary = read_csv_dicts(RESULT_DIR / "alb2002_local_geography_artifact_summary.csv")
    alb2002_gadm_summary = read_csv_dicts(RESULT_DIR / "alb2002_gadm_boundary_lead_summary.csv")
    alb2012_summary = read_csv_dicts(RESULT_DIR / "alb2012_raw_core_feasibility_summary.csv")
    alb2012_outcome_summary = read_csv_dicts(RESULT_DIR / "alb2012_provisional_outcome_feasibility_summary.csv")
    alb2012_semantics_summary = read_csv_dicts(RESULT_DIR / "alb2012_outcome_semantics_raw_value_summary.csv")
    alb2012_timing_geo_summary = read_csv_dicts(RESULT_DIR / "alb2012_timing_geography_exhaustive_summary.csv")
    alb2012_questionnaire_timing_summary = read_csv_dicts(RESULT_DIR / "alb2012_questionnaire_timing_field_summary.csv")
    alb2012_blocker_summary = read_csv_dicts(RESULT_DIR / "alb2012_timing_geography_blocker_resolution_summary.csv")
    albania_legacy_questionnaire_summary = read_csv_dicts(RESULT_DIR / "albania_legacy_questionnaire_readability_summary.csv")
    albania_legacy_questionnaire_timing_summary = read_csv_dicts(RESULT_DIR / "albania_legacy_questionnaire_timing_field_summary.csv")
    alb2005_summary = read_csv_dicts(RESULT_DIR / "alb2005_documented_harmonization_summary.csv")
    alb2005_core_summary = read_csv_dicts(RESULT_DIR / "alb2005_household_core_candidate_summary.csv")
    alb2005_outcome_summary = read_csv_dicts(RESULT_DIR / "alb2005_provisional_outcome_feasibility_summary.csv")
    alb2005_semantics_summary = read_csv_dicts(RESULT_DIR / "alb2005_outcome_semantics_raw_value_summary.csv")
    alb2005_timing_geo_summary = read_csv_dicts(RESULT_DIR / "alb2005_timing_geography_exhaustive_summary.csv")
    alb2005_required_value_key_summary = read_csv_dicts(RESULT_DIR / "alb2005_required_value_key_summary.csv")
    alb2005_health_questionnaire_summary = read_csv_dicts(RESULT_DIR / "alb2005_health_questionnaire_semantics_summary.csv")
    alb2005_oop_policy_summary = read_csv_dicts(RESULT_DIR / "alb2005_oop_aggregation_policy_summary.csv")
    alb2005_skip_missing_summary = read_csv_dicts(RESULT_DIR / "alb2005_skip_missing_semantics_summary.csv")
    alb2005_unit_period_summary = read_csv_dicts(RESULT_DIR / "alb2005_consumption_oop_unit_period_summary.csv")
    alb2005_aggregate_crosswalk_summary = read_csv_dicts(RESULT_DIR / "alb2005_consumption_aggregate_metadata_crosswalk_summary.csv")
    alb2005_component_source_summary = read_csv_dicts(RESULT_DIR / "alb2005_consumption_component_source_search_summary.csv")
    alb2005_timing_geo_source_summary = read_csv_dicts(RESULT_DIR / "alb2005_timing_geography_source_search_summary.csv")
    alb2005_minimum_recipe_summary = read_csv_dicts(RESULT_DIR / "alb2005_minimum_recipe_promotion_summary.csv")
    alb2005_public_fieldwork_geo_summary = read_csv_dicts(RESULT_DIR / "alb2005_public_fieldwork_geo_metadata_summary.csv")
    alb2005_diary_timing_summary = read_csv_dicts(RESULT_DIR / "alb2005_diary_timing_candidate_summary.csv")
    alb2005_extracted_module_summary = read_csv_dicts(RESULT_DIR / "alb2005_extracted_module_coverage_summary.csv")
    albania_first_analysis_summary = read_csv_dicts(RESULT_DIR / "albania_first_analysis_promotion_summary.csv")
    alb2005_fallback_blocker_summary = read_csv_dicts(RESULT_DIR / "alb2005_fallback_blocker_resolution_summary.csv")
    albania_wave_summary = read_csv_dicts(RESULT_DIR / "albania_existing_raw_wave_audit_summary.csv")
    alb2008_core_summary = read_csv_dicts(RESULT_DIR / "alb2008_household_core_candidate_summary.csv")
    alb2008_outcome_summary = read_csv_dicts(RESULT_DIR / "alb2008_provisional_outcome_feasibility_summary.csv")
    alb2008_semantics_summary = read_csv_dicts(RESULT_DIR / "alb2008_outcome_semantics_raw_value_summary.csv")
    alb2008_timing_geo_summary = read_csv_dicts(RESULT_DIR / "alb2008_timing_geography_exhaustive_summary.csv")
    alb2008_fallback_blocker_summary = read_csv_dicts(RESULT_DIR / "alb2008_fallback_blocker_resolution_summary.csv")
    first_batch_verification_summary = read_csv_dicts(RESULT_DIR / "first_batch_raw_verification_workbook_summary.csv")
    objective_summary = read_csv_dicts(RESULT_DIR / "objective_traceability_summary.csv")

    variable_map_paths = [
        TEMP_DIR / "variable_map_consumption.csv",
        TEMP_DIR / "variable_map_health_expenditure.csv",
        TEMP_DIR / "variable_map_health_need_access.csv",
        TEMP_DIR / "variable_map_geography.csv",
        TEMP_DIR / "variable_map_survey_design.csv",
        TEMP_DIR / "variable_map_demographics.csv",
        TEMP_DIR / "variable_map_shocks.csv",
    ]
    variable_map_rows = sum(row_count(path) for path in variable_map_paths)
    raw_file_rows = row_count(TEMP_DIR / "raw_schema_inventory" / "raw_file_inventory.csv")
    raw_variable_rows = row_count(TEMP_DIR / "raw_schema_inventory" / "raw_variable_catalog.csv")
    data_files = [path for path in DATA_DIR.rglob("*") if path.is_file()]
    analysis_ready_rows = sum(row_count(path) for path in data_files if path.suffix.lower() == ".csv")
    completion_complete = sum(1 for row in completion if row.get("status") == "complete")
    completion_incomplete = sum(1 for row in completion if row.get("status") == "incomplete")
    workspace_complete = sum(1 for row in workspace_validation if row.get("status") == "complete")
    workspace_incomplete = sum(1 for row in workspace_validation if row.get("status") == "incomplete")

    raw_claim_status = "raw_schema_claims_only_no_analysis_dataset_claims" if raw_file_rows and raw_variable_rows else "metadata_protocol_only_no_empirical_claims"
    raw_claim_value = f"raw_file_inventory_rows={raw_file_rows}; raw_variable_catalog_rows={raw_variable_rows}" if raw_file_rows and raw_variable_rows else "no raw microdata inspected"
    add_bundle(
        rows,
        "state",
        "allowed_claim_boundary",
        raw_claim_status,
        raw_claim_value,
        [REPORT_DIR / "final_report.md", RESULT_DIR / "empirical_readiness_dashboard.csv"],
        "The workspace can support raw schema and variable-label claims for inspected files only; it still cannot support harmonized-data, outcome, climate-linkage, model, mechanism, causal, or policy-value claims.",
    )
    add_bundle(
        rows,
        "state",
        "raw_microdata_gate",
        "raw_schema_inspected_harmonization_pending" if raw_file_rows and raw_variable_rows else "blocked_raw_microdata",
        f"raw_file_inventory_rows={raw_file_rows}; raw_variable_catalog_rows={raw_variable_rows}",
        [TEMP_DIR / "raw_schema_inventory" / "raw_file_inventory.csv", TEMP_DIR / "raw_schema_inventory" / "raw_variable_catalog.csv"],
        "Raw files have been schema-inspected, but harmonization still requires verified raw values, units, recall periods, missing codes, and merge keys." if raw_file_rows and raw_variable_rows else "Manual raw files must be placed under temp/raw_downloads and inspected before harmonization or analysis.",
    )
    add_bundle(
        rows,
        "state",
        "analysis_ready_data",
        "not_available",
        f"data_files={len(data_files)}; csv_rows={analysis_ready_rows}",
        [DATA_DIR],
        "No clean analysis-ready household, outcome, climate-exposure, or climate-linked dataset is available.",
    )
    add_bundle(
        rows,
        "coverage",
        "source_inventory",
        "complete" if row_count(TEMP_DIR / "source_inventory.csv") > 0 else "missing",
        str(row_count(TEMP_DIR / "source_inventory.csv")),
        [TEMP_DIR / "source_inventory.csv"],
        "Official/public source inventory rows.",
    )
    add_bundle(
        rows,
        "coverage",
        "country_wave_screening",
        "complete" if row_count(TEMP_DIR / "country_wave_screening.csv") > 0 else "missing",
        str(row_count(TEMP_DIR / "country_wave_screening.csv")),
        [TEMP_DIR / "country_wave_screening.csv"],
        "Broad country-wave screening rows before final sample selection.",
    )
    add_bundle(
        rows,
        "coverage",
        "manual_download_manifest",
        "complete" if row_count(TEMP_DIR / "manual_download_manifest.csv") > 0 else "missing",
        str(row_count(TEMP_DIR / "manual_download_manifest.csv")),
        [TEMP_DIR / "manual_download_manifest.csv"],
        "Raw-data sources requiring login, terms acceptance, or manual download.",
    )
    add_bundle(
        rows,
        "coverage",
        "first_batch_raw_acquisition",
        "manual_download_required" if first_batch else "missing",
        f"datasets={csv_value(first_batch_summary, 'first_batch_dataset_rows', '0')}; countries={csv_value(first_batch_summary, 'first_batch_country_count', '0')}; file_targets={csv_value(first_batch_summary, 'first_batch_file_target_rows', '0')}",
        [TEMP_DIR / "first_batch_raw_acquisition_checklist.csv", TEMP_DIR / "first_batch_raw_file_targets.csv", RESULT_DIR / "first_batch_raw_acquisition_summary.csv", REPORT_DIR / "first_batch_raw_acquisition_checklist.md"],
        "Smallest current manual download batch for testing the 6-country financial-protection and 10-wave double-failure gates.",
    )
    if first_batch_summary:
        add_bundle(
            rows,
            "raw_acquisition_gate",
            "first_batch_current_raw_files",
            "blocked_raw_microdata",
            f"raw_tabular={csv_value(first_batch_summary, 'first_batch_raw_tabular_file_rows', '0')}; archives={csv_value(first_batch_summary, 'first_batch_archive_file_rows', '0')}",
            [RESULT_DIR / "first_batch_raw_acquisition_summary.csv"],
            "First-batch folders currently contain no raw tabular/archive evidence sufficient to start raw schema inspection.",
        )
    add_bundle(
        rows,
        "raw_access_gate",
        "first_batch_official_raw_access_probe",
        "manual_review_required",
        f"probe_rows={csv_value(first_batch_access_summary, 'first_batch_access_probe_rows', '0')}; access_gate_rows={csv_value(first_batch_access_summary, 'access_gate_detected_rows', '0')}; possible_direct_rows={csv_value(first_batch_access_summary, 'possible_direct_raw_link_rows', '0')}",
        [TEMP_DIR / "first_batch_official_raw_access_probe.csv", RESULT_DIR / "first_batch_official_raw_access_summary.csv", REPORT_DIR / "first_batch_official_raw_access_probe.md"],
        "Official get-microdata page probe; does not download raw files or bypass login, registration, request, or terms gates.",
    )
    add_bundle(
        rows,
        "priority_bundle",
        "priority_raw_intake_gate",
        "manual_raw_package_required",
        f"gate_rows={csv_value(priority_raw_intake_summary, 'priority_raw_intake_gate_rows', '0')}; priority_10_rows={csv_value(priority_raw_intake_summary, 'priority_raw_intake_priority_10_rows', '0')}; backup_rows={csv_value(priority_raw_intake_summary, 'priority_raw_intake_backup_rows', '0')}; file_targets={csv_value(priority_raw_intake_summary, 'priority_raw_file_target_rows', '0')}; manual_blocked={csv_value(priority_raw_intake_summary, 'priority_raw_gate_blocked_manual_rows', '0')}; schema_ready={csv_value(priority_raw_intake_summary, 'priority_raw_gate_schema_ready_rows', '0')}; handoffs={csv_value(priority_raw_intake_summary, 'priority_raw_handoff_readmes_written', '0')}",
        [TEMP_DIR / "priority_raw_intake_gate.csv", TEMP_DIR / "priority_raw_file_targets.csv", RESULT_DIR / "priority_raw_intake_gate_summary.csv", REPORT_DIR / "priority_raw_intake_gate.md"],
        "Priority 10-wave and backup raw-intake gate converts the acquisition plan into per-folder handoff files and fail-closed post-download promotion checks.",
    )
    add_bundle(
        rows,
        "priority_bundle",
        "priority_archive_member_preflight",
        "blocked_no_raw_or_archive_file" if csv_value(priority_archive_summary, "priority_datasets_blocked_no_raw_or_archive", "0") != "0" else "archive_or_direct_coverage_checked",
        f"datasets={csv_value(priority_archive_summary, 'priority_archive_preflight_dataset_rows', '0')}; targets={csv_value(priority_archive_summary, 'priority_archive_preflight_file_target_rows', '0')}; archives={csv_value(priority_archive_summary, 'priority_archive_files_found', '0')}; members={csv_value(priority_archive_summary, 'priority_archive_member_rows', '0')}; direct_covered={csv_value(priority_archive_summary, 'priority_targets_covered_by_direct_file', '0')}; archive_covered={csv_value(priority_archive_summary, 'priority_targets_covered_by_archive_member', '0')}; missing={csv_value(priority_archive_summary, 'priority_targets_missing_direct_or_archive_member', '0')}",
        [TEMP_DIR / "priority_archive_member_inventory.csv", TEMP_DIR / "priority_archive_completeness_matrix.csv", RESULT_DIR / "priority_archive_member_preflight_summary.csv", REPORT_DIR / "priority_archive_member_preflight.md"],
        "Archive/direct-file preflight checks whether placed raw archives or tabular files cover priority modules before any raw value verification or data promotion.",
    )
    add_bundle(
        rows,
        "priority_bundle",
        "priority_climate_linkage_preflight",
        "blocked_raw_timing_geography_not_verified",
        f"preflight_rows={csv_value(priority_climate_preflight_summary, 'priority_climate_preflight_rows', '0')}; priority_10_rows={csv_value(priority_climate_preflight_summary, 'priority_climate_preflight_priority_10_rows', '0')}; backup_rows={csv_value(priority_climate_preflight_summary, 'priority_climate_preflight_backup_rows', '0')}; requirements={csv_value(priority_climate_preflight_summary, 'priority_climate_requirement_rows', '0')}; source_ready={csv_value(priority_climate_preflight_summary, 'priority_chirps_era5_source_route_ready_rows', '0')}; accepted_routes={csv_value(priority_climate_preflight_summary, 'priority_accepted_chirps_era5_route_rows', '0')}; handoffs={csv_value(priority_climate_preflight_summary, 'priority_climate_handoff_readmes_written', '0')}",
        [TEMP_DIR / "priority_climate_linkage_preflight.csv", TEMP_DIR / "priority_climate_linkage_requirements.csv", RESULT_DIR / "priority_climate_linkage_preflight_summary.csv", REPORT_DIR / "priority_climate_linkage_preflight.md"],
        "Priority climate preflight keeps CHIRPS/ERA5 linkage fail-closed until raw timing/geography, geolocation quality, units, lag windows, and source validation pass.",
    )
    add_bundle(
        rows,
        "priority_bundle",
        "priority_raw_verification_workbook",
        "blocked_raw_files_absent",
        f"dataset_gates={csv_value(priority_raw_verification_summary, 'priority_dataset_verification_gate_rows', '0')}; requirements={csv_value(priority_raw_verification_summary, 'priority_requirement_checklist_rows', '0')}; concepts={csv_value(priority_raw_verification_summary, 'priority_concept_template_rows', '0')}; variables={csv_value(priority_raw_verification_summary, 'priority_variable_template_rows', '0')}; dataset_ready={csv_value(priority_raw_verification_summary, 'priority_datasets_ready_for_manual_value_audit', '0')}; requirements_ready={csv_value(priority_raw_verification_summary, 'priority_requirements_ready_for_manual_audit', '0')}; handoffs={csv_value(priority_raw_verification_summary, 'priority_raw_verification_handoff_readmes_written', '0')}",
        [RESULT_DIR / "priority_dataset_verification_gate.csv", TEMP_DIR / "priority_promotion_verification_checklist.csv", TEMP_DIR / "priority_concept_verification_template.csv", TEMP_DIR / "priority_variable_verification_template.csv", RESULT_DIR / "priority_raw_verification_workbook_summary.csv", REPORT_DIR / "priority_raw_verification_workbook.md"],
        "Priority raw verification workbook converts the objective's required checks into fillable dataset, requirement, concept, and variable gates; all remain fail-closed until raw evidence is placed and audited.",
    )
    add_bundle(
        rows,
        "priority_bundle",
        "priority_manual_verification_decision_gate",
        "blocked_manual_verification_incomplete" if csv_value(priority_manual_verification_summary, "priority_analysis_ready_candidates", "0") == "0" else "manual_verification_candidates_ready",
        f"datasets={csv_value(priority_manual_verification_summary, 'priority_manual_decision_dataset_rows', '0')}; requirements={csv_value(priority_manual_verification_summary, 'priority_manual_requirement_decision_rows', '0')}; concepts={csv_value(priority_manual_verification_summary, 'priority_manual_concept_decision_rows', '0')}; variables={csv_value(priority_manual_verification_summary, 'priority_manual_variable_decision_rows', '0')}; requirements_verified={csv_value(priority_manual_verification_summary, 'priority_manual_requirements_verified', '0')}; concepts_verified={csv_value(priority_manual_verification_summary, 'priority_manual_concepts_verified', '0')}; variables_verified={csv_value(priority_manual_verification_summary, 'priority_manual_variables_verified', '0')}; financial_ready_countries={csv_value(priority_manual_verification_summary, 'priority_financial_protection_manual_ready_countries', '0')}; double_failure_ready_waves={csv_value(priority_manual_verification_summary, 'priority_double_failure_manual_ready_waves', '0')}; analysis_ready={csv_value(priority_manual_verification_summary, 'priority_analysis_ready_candidates', '0')}",
        [TEMP_DIR / "priority_manual_verification_decision_gate.csv", TEMP_DIR / "priority_manual_requirement_decision_audit.csv", TEMP_DIR / "priority_manual_concept_decision_audit.csv", TEMP_DIR / "priority_manual_variable_decision_audit.csv", RESULT_DIR / "priority_manual_verification_decision_summary.csv", REPORT_DIR / "priority_manual_verification_decision_gate.md"],
        "Priority manual verification decision gate consumes preserved fill-field evidence from the workbook and blocks promotion until source-backed manual requirement, concept, and variable checks pass.",
    )
    add_bundle(
        rows,
        "priority_bundle",
        "priority_raw_package_receipt_ledger",
        "not_received_no_original_raw_package" if csv_value(priority_receipt_summary, "priority_raw_receipt_missing_package_rows", "0") != "0" else "raw_package_receipt_candidates_present",
        f"datasets={csv_value(priority_receipt_summary, 'priority_raw_receipt_dataset_rows', '0')}; original_files={csv_value(priority_receipt_summary, 'priority_raw_receipt_original_file_rows', '0')}; archives={csv_value(priority_receipt_summary, 'priority_raw_receipt_archive_files', '0')}; raw_tabular={csv_value(priority_receipt_summary, 'priority_raw_receipt_raw_tabular_files', '0')}; documentation={csv_value(priority_receipt_summary, 'priority_raw_receipt_documentation_files', '0')}; targets={csv_value(priority_receipt_summary, 'priority_raw_receipt_priority_targets', '0')}; covered={csv_value(priority_receipt_summary, 'priority_raw_receipt_priority_targets_covered', '0')}; missing={csv_value(priority_receipt_summary, 'priority_raw_receipt_priority_targets_missing', '0')}; generated_ignored={csv_value(priority_receipt_summary, 'priority_raw_receipt_generated_files_ignored', '0')}; complete_candidates={csv_value(priority_receipt_summary, 'priority_raw_receipt_complete_package_candidates', '0')}",
        [TEMP_DIR / "priority_raw_package_receipt_ledger.csv", TEMP_DIR / "priority_raw_package_file_manifest.csv", TEMP_DIR / "priority_raw_package_missing_targets.csv", RESULT_DIR / "priority_raw_package_receipt_summary.csv", REPORT_DIR / "priority_raw_package_receipt_ledger.md"],
        "Priority receipt ledger ignores generated handoffs/placeholders and records only unchanged original package/documentation files, hashes, and missing target modules before downstream schema/manual verification.",
    )
    add_bundle(
        rows,
        "priority_bundle",
        "priority_official_download_dossier",
        "blocked_official_access_required_no_original_package" if csv_value(priority_official_download_summary, "priority_official_no_original_package_rows", "0") != "0" else "official_download_receipt_candidates_present",
        f"dossiers={csv_value(priority_official_download_summary, 'priority_official_download_dossier_rows', '0')}; full_file_rows={csv_value(priority_official_download_summary, 'priority_official_full_file_inventory_rows', '0')}; core_rows={csv_value(priority_official_download_summary, 'priority_official_priority_core_file_rows', '0')}; links={csv_value(priority_official_download_summary, 'priority_official_documentation_link_rows', '0')}; pdf={csv_value(priority_official_download_summary, 'priority_official_pdf_documentation_links', '0')}; ddi={csv_value(priority_official_download_summary, 'priority_official_ddi_metadata_links', '0')}; json={csv_value(priority_official_download_summary, 'priority_official_json_metadata_links', '0')}; no_original_package={csv_value(priority_official_download_summary, 'priority_official_no_original_package_rows', '0')}; receipt_candidates={csv_value(priority_official_download_summary, 'priority_official_receipt_candidates', '0')}",
        [TEMP_DIR / "priority_official_download_dossier.csv", TEMP_DIR / "priority_official_full_file_inventory.csv", TEMP_DIR / "priority_official_documentation_links.csv", RESULT_DIR / "priority_official_download_dossier_summary.csv", REPORT_DIR / "priority_official_download_dossier.md"],
        "Official download dossier expands from the 156 core targets to the full metadata-derived file inventory and records official access, documentation, DDI, JSON, and data-dictionary links for credentialed package acquisition.",
    )
    add_bundle(
        rows,
        "priority_bundle",
        "priority_public_documentation_receipt",
        "core_public_documentation_saved_raw_gate_still_blocked" if csv_value(priority_public_documentation_summary, "priority_public_documentation_core_complete_dataset_rows", "0") != "0" else "public_documentation_missing",
        f"datasets={csv_value(priority_public_documentation_summary, 'priority_public_documentation_dataset_rows', '0')}; resources={csv_value(priority_public_documentation_summary, 'priority_public_documentation_resource_rows', '0')}; saved={csv_value(priority_public_documentation_summary, 'priority_public_documentation_saved_rows', '0')}; failed={csv_value(priority_public_documentation_summary, 'priority_public_documentation_failed_rows', '0')}; core_complete={csv_value(priority_public_documentation_summary, 'priority_public_documentation_core_complete_dataset_rows', '0')}; full_complete={csv_value(priority_public_documentation_summary, 'priority_public_documentation_full_complete_dataset_rows', '0')}; optional_pdf_missing={csv_value(priority_public_documentation_summary, 'priority_public_documentation_optional_pdf_missing_dataset_rows', '0')}; access_gates={csv_value(priority_public_documentation_summary, 'priority_public_documentation_access_gate_rows', '0')}; saved_bytes={csv_value(priority_public_documentation_summary, 'priority_public_documentation_saved_bytes', '0')}",
        [TEMP_DIR / "priority_public_documentation_receipt.csv", TEMP_DIR / "priority_public_documentation_dataset_receipt.csv", RESULT_DIR / "priority_public_documentation_receipt_summary.csv", REPORT_DIR / "priority_public_documentation_receipt.md"],
        "Public documentation receipt downloads or reuses official DDI/XML, JSON, data dictionary, related-material, get-microdata, and listed PDF resources for priority waves while preserving the raw-microdata access gate.",
    )
    add_bundle(
        rows,
        "priority_bundle",
        "priority_official_metadata_evidence_extract",
        "official_metadata_evidence_present_raw_gate_still_blocked" if csv_value(priority_official_metadata_summary, "priority_official_metadata_candidate_variable_rows", "0") != "0" else "official_metadata_evidence_missing",
        f"datasets={csv_value(priority_official_metadata_summary, 'priority_official_metadata_dataset_rows', '0')}; candidate_variables={csv_value(priority_official_metadata_summary, 'priority_official_metadata_candidate_variable_rows', '0')}; categories={csv_value(priority_official_metadata_summary, 'priority_official_metadata_category_rows', '0')}; variable_matches={csv_value(priority_official_metadata_summary, 'priority_official_metadata_variable_match_rows', '0')}; file_matches={csv_value(priority_official_metadata_summary, 'priority_official_metadata_variable_file_match_rows', '0')}; no_matches={csv_value(priority_official_metadata_summary, 'priority_official_metadata_no_match_rows', '0')}; variables_with_categories={csv_value(priority_official_metadata_summary, 'priority_official_metadata_variables_with_categories', '0')}; dataset_complete={csv_value(priority_official_metadata_summary, 'priority_official_metadata_dataset_complete_rows', '0')}; handoffs={csv_value(priority_official_metadata_summary, 'priority_official_metadata_handoff_readmes_written', '0')}; modeling_gate={csv_value(priority_official_metadata_summary, 'modeling_gate_status', 'missing')}",
        [TEMP_DIR / "priority_official_metadata_variable_evidence.csv", TEMP_DIR / "priority_official_metadata_category_evidence.csv", TEMP_DIR / "priority_official_metadata_dataset_evidence.csv", RESULT_DIR / "priority_official_metadata_evidence_summary.csv", REPORT_DIR / "priority_official_metadata_evidence_extract.md"],
        "Official DDI/XML metadata evidence links candidate variables to official labels, categories, counts, and file mappings for pre-review only; promotion still requires original raw packages and raw value verification.",
    )
    add_bundle(
        rows,
        "priority_bundle",
        "priority_credentialed_raw_acquisition_ledger",
        "ready_for_credentialed_manual_download" if csv_value(priority_credentialed_acquisition_summary, "priority_credentialed_acquisition_dataset_rows", "0") != "0" else "credentialed_acquisition_ledger_missing",
        f"datasets={csv_value(priority_credentialed_acquisition_summary, 'priority_credentialed_acquisition_dataset_rows', '0')}; priority_rows={csv_value(priority_credentialed_acquisition_summary, 'priority_credentialed_acquisition_priority_batch_rows', '0')}; backup_rows={csv_value(priority_credentialed_acquisition_summary, 'priority_credentialed_acquisition_backup_rows', '0')}; full_files={csv_value(priority_credentialed_acquisition_summary, 'priority_credentialed_acquisition_full_file_rows', '0')}; core_files={csv_value(priority_credentialed_acquisition_summary, 'priority_credentialed_acquisition_core_file_rows', '0')}; public_docs_ready={csv_value(priority_credentialed_acquisition_summary, 'priority_credentialed_acquisition_public_documentation_ready_rows', '0')}; metadata_ready={csv_value(priority_credentialed_acquisition_summary, 'priority_credentialed_acquisition_official_metadata_ready_rows', '0')}; original_receipts={csv_value(priority_credentialed_acquisition_summary, 'priority_credentialed_acquisition_original_package_receipt_rows', '0')}; targets_missing={csv_value(priority_credentialed_acquisition_summary, 'priority_credentialed_acquisition_targets_missing_before_download', '0')}; handoffs={csv_value(priority_credentialed_acquisition_summary, 'priority_credentialed_acquisition_handoff_readmes_written', '0')}; modeling_gate={csv_value(priority_credentialed_acquisition_summary, 'modeling_gate_status', 'missing')}",
        [TEMP_DIR / "priority_credentialed_raw_acquisition_ledger.csv", TEMP_DIR / "priority_credentialed_raw_full_file_manifest.csv", TEMP_DIR / "priority_credentialed_raw_core_file_checklist.csv", RESULT_DIR / "priority_credentialed_raw_acquisition_summary.csv", REPORT_DIR / "priority_credentialed_raw_acquisition_ledger.md"],
        "Credentialed raw acquisition ledger gives the exact official get-microdata workflow, complete-package scope, target folder, full official file manifest, core-file checklist, and post-download validation commands; it does not bypass account, terms, or raw value verification gates.",
    )
    add_bundle(
        rows,
        "priority_bundle",
        "priority_official_endpoint_matrix",
        "public_metadata_only_raw_gate_confirmed" if csv_value(priority_endpoint_matrix_summary, "priority_endpoint_matrix_raw_download_candidate_rows", "0") == "0" and csv_value(priority_endpoint_matrix_summary, "priority_endpoint_matrix_dataset_rows", "0") != "0" else "endpoint_matrix_needs_manual_review",
        f"datasets={csv_value(priority_endpoint_matrix_summary, 'priority_endpoint_matrix_dataset_rows', '0')}; endpoints={csv_value(priority_endpoint_matrix_summary, 'priority_endpoint_matrix_endpoint_rows', '0')}; public_metadata_endpoints={csv_value(priority_endpoint_matrix_summary, 'priority_endpoint_matrix_public_metadata_endpoint_rows', '0')}; variable_api_datasets={csv_value(priority_endpoint_matrix_summary, 'priority_endpoint_matrix_variable_api_dataset_rows', '0')}; get_microdata_gate_datasets={csv_value(priority_endpoint_matrix_summary, 'priority_endpoint_matrix_get_microdata_gate_dataset_rows', '0')}; raw_candidates={csv_value(priority_endpoint_matrix_summary, 'priority_endpoint_matrix_raw_download_candidate_rows', '0')}; credentialed_required={csv_value(priority_endpoint_matrix_summary, 'priority_endpoint_matrix_credentialed_download_required_rows', '0')}; handoffs={csv_value(priority_endpoint_matrix_summary, 'priority_endpoint_matrix_handoff_readmes_written', '0')}; modeling_gate={csv_value(priority_endpoint_matrix_summary, 'modeling_gate_status', 'missing')}",
        [TEMP_DIR / "priority_official_endpoint_matrix.csv", TEMP_DIR / "priority_official_endpoint_dataset_matrix.csv", RESULT_DIR / "priority_official_endpoint_matrix_summary.csv", REPORT_DIR / "priority_official_endpoint_matrix.md"],
        "Endpoint matrix probes catalog/API/metadata/get-microdata routes and confirms public routes are metadata-only while official raw package acquisition remains credentialed.",
    )
    add_bundle(
        rows,
        "priority_bundle",
        "priority_core_file_endpoint_matrix",
        "file_level_routes_confirmed_non_public_raw" if csv_value(priority_core_file_endpoint_summary, "priority_core_file_endpoint_raw_candidate_rows", "0") == "0" and csv_value(priority_core_file_endpoint_summary, "priority_core_file_endpoint_dataset_rows", "0") != "0" else "core_file_endpoint_matrix_needs_manual_review",
        f"datasets={csv_value(priority_core_file_endpoint_summary, 'priority_core_file_endpoint_dataset_rows', '0')}; core_files={csv_value(priority_core_file_endpoint_summary, 'priority_core_file_endpoint_core_file_rows', '0')}; matrix_rows={csv_value(priority_core_file_endpoint_summary, 'priority_core_file_endpoint_matrix_rows', '0')}; metadata_refs={csv_value(priority_core_file_endpoint_summary, 'priority_core_file_endpoint_metadata_reference_rows', '0')}; probed_download_routes={csv_value(priority_core_file_endpoint_summary, 'priority_core_file_endpoint_probed_download_rows', '0')}; http_errors={csv_value(priority_core_file_endpoint_summary, 'priority_core_file_endpoint_http_error_rows', '0')}; empty_downloads={csv_value(priority_core_file_endpoint_summary, 'priority_core_file_endpoint_empty_download_rows', '0')}; request_failed={csv_value(priority_core_file_endpoint_summary, 'priority_core_file_endpoint_request_failed_rows', '0')}; raw_candidates={csv_value(priority_core_file_endpoint_summary, 'priority_core_file_endpoint_raw_candidate_rows', '0')}; credentialed_required={csv_value(priority_core_file_endpoint_summary, 'priority_core_file_endpoint_credentialed_download_required_rows', '0')}; handoffs={csv_value(priority_core_file_endpoint_summary, 'priority_core_file_endpoint_handoff_readmes_written', '0')}; modeling_gate={csv_value(priority_core_file_endpoint_summary, 'modeling_gate_status', 'missing')}",
        [TEMP_DIR / "priority_core_file_endpoint_matrix.csv", TEMP_DIR / "priority_core_file_endpoint_dataset_matrix.csv", RESULT_DIR / "priority_core_file_endpoint_matrix_summary.csv", REPORT_DIR / "priority_core_file_endpoint_matrix.md"],
        "Core-file endpoint matrix probes common file-level World Bank/NADA download route patterns for the 156 priority modules and confirms they do not expose public raw payloads; official credentialed package receipt is still required.",
    )
    add_bundle(
        rows,
        "priority_bundle",
        "priority_threshold_acquisition_campaign",
        "threshold_campaign_ready_raw_missing" if csv_value(priority_threshold_campaign_summary, "priority_threshold_campaign_dataset_rows", "0") != "0" and csv_value(priority_threshold_campaign_summary, "priority_threshold_campaign_raw_package_received_rows", "0") == "0" else "threshold_campaign_needs_review",
        f"datasets={csv_value(priority_threshold_campaign_summary, 'priority_threshold_campaign_dataset_rows', '0')}; phase1_10_wave_rows={csv_value(priority_threshold_campaign_summary, 'priority_threshold_campaign_phase1_10_wave_rows', '0')}; phase2_backup_rows={csv_value(priority_threshold_campaign_summary, 'priority_threshold_campaign_phase2_sixth_country_backup_rows', '0')}; countries={csv_value(priority_threshold_campaign_summary, 'priority_threshold_campaign_distinct_countries', '0')}; core_countries={csv_value(priority_threshold_campaign_summary, 'priority_threshold_campaign_core_country_rows', '0')}; backup_countries={csv_value(priority_threshold_campaign_summary, 'priority_threshold_campaign_backup_country_rows', '0')}; minimum_downloads={csv_value(priority_threshold_campaign_summary, 'priority_threshold_campaign_minimum_download_rows_for_formal_thresholds', '0')}; recommended_downloads={csv_value(priority_threshold_campaign_summary, 'priority_threshold_campaign_recommended_download_rows', '0')}; raw_received={csv_value(priority_threshold_campaign_summary, 'priority_threshold_campaign_raw_package_received_rows', '0')}; raw_missing={csv_value(priority_threshold_campaign_summary, 'priority_threshold_campaign_raw_package_missing_rows', '0')}; core_endpoint_ready={csv_value(priority_threshold_campaign_summary, 'priority_threshold_campaign_core_file_endpoint_ready_rows', '0')}; handoffs={csv_value(priority_threshold_campaign_summary, 'priority_threshold_campaign_handoff_readmes_written', '0')}; modeling_gate={csv_value(priority_threshold_campaign_summary, 'modeling_gate_status', 'missing')}",
        [TEMP_DIR / "priority_threshold_acquisition_campaign.csv", TEMP_DIR / "priority_threshold_country_coverage.csv", RESULT_DIR / "priority_threshold_acquisition_campaign_summary.csv", REPORT_DIR / "priority_threshold_acquisition_campaign.md"],
        "Threshold acquisition campaign maps the 13 priority/backup waves to the actual 10-wave and 6-country modeling guardrails, showing the first 10 waves cover only five countries and at least one backup country must verify for financial protection.",
    )
    add_bundle(
        rows,
        "priority_bundle",
        "priority_first_pass_variable_review_queue",
        "first_pass_queue_ready_raw_missing" if csv_value(priority_first_pass_summary, "priority_first_pass_selected_variable_rows", "0") != "0" and csv_value(priority_first_pass_summary, "priority_first_pass_raw_package_received_rows", "0") == "0" else "first_pass_queue_needs_review",
        f"datasets={csv_value(priority_first_pass_summary, 'priority_first_pass_dataset_rows', '0')}; requirements={csv_value(priority_first_pass_summary, 'priority_first_pass_requirement_rows', '0')}; selected_variables={csv_value(priority_first_pass_summary, 'priority_first_pass_selected_variable_rows', '0')}; countries={csv_value(priority_first_pass_summary, 'priority_first_pass_distinct_countries', '0')}; priority_waves={csv_value(priority_first_pass_summary, 'priority_first_pass_priority_10_wave_rows', '0')}; backup_waves={csv_value(priority_first_pass_summary, 'priority_first_pass_backup_wave_rows', '0')}; missing_requirement_coverage={csv_value(priority_first_pass_summary, 'priority_first_pass_missing_requirement_coverage_rows', '0')}; raw_received={csv_value(priority_first_pass_summary, 'priority_first_pass_raw_package_received_rows', '0')}; ready_after_download={csv_value(priority_first_pass_summary, 'priority_first_pass_ready_after_download_rows', '0')}; handoffs={csv_value(priority_first_pass_summary, 'priority_first_pass_handoff_readmes_written', '0')}; modeling_gate={csv_value(priority_first_pass_summary, 'modeling_gate_status', 'missing')}",
        [TEMP_DIR / "priority_first_pass_variable_review_queue.csv", TEMP_DIR / "priority_first_pass_requirement_coverage.csv", RESULT_DIR / "priority_first_pass_variable_review_summary.csv", REPORT_DIR / "priority_first_pass_variable_review_queue.md"],
        "First-pass queue compresses the large metadata candidate workbook into a per-requirement list of variables to inspect after official raw packages are received; it is review guidance, not raw-value verification.",
    )
    add_bundle(
        rows,
        "priority_bundle",
        "priority_download_execution_packet",
        "download_execution_ready_raw_missing" if csv_value(priority_download_execution_summary, "priority_download_execution_packet_rows", "0") != "0" and csv_value(priority_download_execution_summary, "priority_download_execution_raw_package_received_rows", "0") == "0" else "download_execution_needs_review",
        f"packets={csv_value(priority_download_execution_summary, 'priority_download_execution_packet_rows', '0')}; priority_waves={csv_value(priority_download_execution_summary, 'priority_download_execution_priority_10_wave_rows', '0')}; backup_waves={csv_value(priority_download_execution_summary, 'priority_download_execution_backup_wave_rows', '0')}; countries={csv_value(priority_download_execution_summary, 'priority_download_execution_distinct_countries', '0')}; core_files={csv_value(priority_download_execution_summary, 'priority_download_execution_core_file_rows', '0')}; requirements={csv_value(priority_download_execution_summary, 'priority_download_execution_first_pass_requirement_rows', '0')}; first_pass_variables={csv_value(priority_download_execution_summary, 'priority_download_execution_first_pass_variable_rows', '0')}; raw_received={csv_value(priority_download_execution_summary, 'priority_download_execution_raw_package_received_rows', '0')}; handoffs={csv_value(priority_download_execution_summary, 'priority_download_execution_handoff_readmes_written', '0')}; modeling_gate={csv_value(priority_download_execution_summary, 'modeling_gate_status', 'missing')}",
        [TEMP_DIR / "priority_download_execution_packet.csv", TEMP_DIR / "priority_download_file_acceptance_matrix.csv", RESULT_DIR / "priority_download_execution_packet_summary.csv", REPORT_DIR / "priority_download_execution_packet.md"],
        "Download execution packet is the credentialed manual-acquisition control sheet: official URL, target folder, 12-file acceptance matrix, first-pass verification load, and post-download command chain per wave.",
    )
    add_bundle(
        rows,
        "priority_bundle",
        "priority_lsms_isa_alignment_audit",
        "core_wave_replacement_needed_before_download_execution" if csv_value(priority_lsms_alignment_summary, "priority_lsms_alignment_off_family_core_wave_rows", "0") != "0" else "core_wave_families_aligned",
        f"campaign_rows={csv_value(priority_lsms_alignment_summary, 'priority_lsms_alignment_current_campaign_rows', '0')}; core_waves={csv_value(priority_lsms_alignment_summary, 'priority_lsms_alignment_core_priority_wave_rows', '0')}; aligned_core={csv_value(priority_lsms_alignment_summary, 'priority_lsms_alignment_aligned_core_wave_rows', '0')}; off_family_core={csv_value(priority_lsms_alignment_summary, 'priority_lsms_alignment_off_family_core_wave_rows', '0')}; strong_replacements={csv_value(priority_lsms_alignment_summary, 'priority_lsms_alignment_strong_replacement_candidate_rows', '0')}; decision={csv_value(priority_lsms_alignment_summary, 'priority_lsms_alignment_campaign_decision', 'missing')}; modeling_gate={csv_value(priority_lsms_alignment_summary, 'modeling_gate_status', 'missing')}",
        [TEMP_DIR / "priority_lsms_isa_alignment_audit.csv", TEMP_DIR / "priority_lsms_isa_replacement_candidates.csv", RESULT_DIR / "priority_lsms_isa_alignment_summary.csv", REPORT_DIR / "priority_lsms_isa_alignment_audit.md"],
        "LSMS/ISA alignment audit separates the usable 13-wave download execution controls from family-suitability risk, flagging Malawi MTM and Uganda SAGE as off-family core waves that should be replaced or augmented with IHS/IHPS and UNPS candidates.",
    )
    add_bundle(
        rows,
        "priority_bundle",
        "priority_lsms_isa_refocused_acquisition_queue",
        "refocused_manual_download_queue_ready_raw_missing" if csv_value(priority_lsms_refocused_summary, "priority_lsms_refocused_raw_package_received_rows", "0") == "0" and csv_value(priority_lsms_refocused_summary, "priority_lsms_refocused_wave_plan_rows", "0") != "0" else "refocused_queue_needs_review",
        f"plan_rows={csv_value(priority_lsms_refocused_summary, 'priority_lsms_refocused_wave_plan_rows', '0')}; core_waves={csv_value(priority_lsms_refocused_summary, 'priority_lsms_refocused_core_wave_rows', '0')}; core_required_countries={csv_value(priority_lsms_refocused_summary, 'priority_lsms_refocused_core_required_countries', '0')}; core_lsms_aligned={csv_value(priority_lsms_refocused_summary, 'priority_lsms_refocused_core_lsms_aligned_rows', '0')}; replaced_off_family={csv_value(priority_lsms_refocused_summary, 'priority_lsms_refocused_replaced_off_family_core_rows', '0')}; queue_rows={csv_value(priority_lsms_refocused_summary, 'priority_lsms_refocused_acquisition_queue_rows', '0')}; backup_rows={csv_value(priority_lsms_refocused_summary, 'priority_lsms_refocused_replacement_backup_rows', '0')}; requirement_rows={csv_value(priority_lsms_refocused_summary, 'priority_lsms_refocused_requirement_rows', '0')}; raw_received={csv_value(priority_lsms_refocused_summary, 'priority_lsms_refocused_raw_package_received_rows', '0')}; data_write={csv_value(priority_lsms_refocused_summary, 'priority_lsms_refocused_data_write_status', 'missing')}; modeling_gate={csv_value(priority_lsms_refocused_summary, 'modeling_gate_status', 'missing')}",
        [RESULT_DIR / "priority_lsms_isa_refocused_wave_plan.csv", TEMP_DIR / "priority_lsms_isa_refocused_acquisition_queue.csv", TEMP_DIR / "priority_lsms_isa_refocused_requirement_matrix.csv", RESULT_DIR / "priority_lsms_isa_refocused_acquisition_summary.csv", REPORT_DIR / "priority_lsms_isa_refocused_acquisition_queue.md"],
        "Refocused acquisition queue makes the corrected manual-download path explicit: replace Malawi MTM and Uganda SAGE in the core campaign with LSMS/ISA-family Malawi IHS/IHPS and Uganda UNPS targets, while retaining backup waves for raw-review failure risk.",
    )
    add_bundle(
        rows,
        "priority_bundle",
        "priority_lsms_isa_public_documentation_receipt",
        "public_documentation_complete_raw_still_blocked" if csv_value(priority_lsms_public_docs_summary, "priority_lsms_isa_public_documentation_core_complete_dataset_rows", "0") == csv_value(priority_lsms_public_docs_summary, "priority_lsms_isa_public_documentation_dataset_rows", "-1") and csv_value(priority_lsms_public_docs_summary, "priority_lsms_isa_public_documentation_dataset_rows", "0") != "0" else "public_documentation_needs_review",
        f"datasets={csv_value(priority_lsms_public_docs_summary, 'priority_lsms_isa_public_documentation_dataset_rows', '0')}; resources={csv_value(priority_lsms_public_docs_summary, 'priority_lsms_isa_public_documentation_resource_rows', '0')}; saved={csv_value(priority_lsms_public_docs_summary, 'priority_lsms_isa_public_documentation_saved_rows', '0')}; failed={csv_value(priority_lsms_public_docs_summary, 'priority_lsms_isa_public_documentation_failed_rows', '0')}; core_complete={csv_value(priority_lsms_public_docs_summary, 'priority_lsms_isa_public_documentation_core_complete_dataset_rows', '0')}; catalog_digest={csv_value(priority_lsms_public_docs_summary, 'priority_lsms_isa_public_documentation_catalog_digest_rows', '0')}; file_inventory={csv_value(priority_lsms_public_docs_summary, 'priority_lsms_isa_public_documentation_file_inventory_rows', '0')}; access_gates={csv_value(priority_lsms_public_docs_summary, 'priority_lsms_isa_public_documentation_access_gate_rows', '0')}; data_write={csv_value(priority_lsms_public_docs_summary, 'priority_lsms_isa_public_documentation_data_write_status', 'missing')}; modeling_gate={csv_value(priority_lsms_public_docs_summary, 'modeling_gate_status', 'missing')}",
        [TEMP_DIR / "priority_lsms_isa_public_documentation_receipt.csv", TEMP_DIR / "priority_lsms_isa_public_documentation_dataset_receipt.csv", TEMP_DIR / "priority_lsms_isa_public_documentation_catalog_digest.csv", TEMP_DIR / "priority_lsms_isa_public_documentation_file_inventory.csv", RESULT_DIR / "priority_lsms_isa_public_documentation_receipt_summary.csv", REPORT_DIR / "priority_lsms_isa_public_documentation_receipt.md"],
        "Refocused 19-wave public documentation receipt saves official public metadata and documentation snapshots for LSMS/ISA acquisition, but raw package receipt and value verification remain required.",
    )
    add_bundle(
        rows,
        "priority_bundle",
        "priority_lsms_isa_variable_evidence_matrix",
        "metadata_variable_candidates_ready_raw_review_required" if csv_value(priority_lsms_variable_evidence_summary, "priority_lsms_variable_evidence_no_candidate_requirement_rows", "0") == "0" and csv_value(priority_lsms_variable_evidence_summary, "priority_lsms_variable_evidence_dataset_rows", "0") != "0" else "metadata_variable_candidates_need_review",
        f"datasets={csv_value(priority_lsms_variable_evidence_summary, 'priority_lsms_variable_evidence_dataset_rows', '0')}; requirements={csv_value(priority_lsms_variable_evidence_summary, 'priority_lsms_variable_evidence_requirement_rows', '0')}; candidate_variables={csv_value(priority_lsms_variable_evidence_summary, 'priority_lsms_variable_evidence_candidate_variable_rows', '0')}; file_shortlist={csv_value(priority_lsms_variable_evidence_summary, 'priority_lsms_variable_evidence_file_shortlist_rows', '0')}; strong_requirements={csv_value(priority_lsms_variable_evidence_summary, 'priority_lsms_variable_evidence_strong_requirement_rows', '0')}; docs_only={csv_value(priority_lsms_variable_evidence_summary, 'priority_lsms_variable_evidence_documentation_only_requirement_rows', '0')}; no_candidate={csv_value(priority_lsms_variable_evidence_summary, 'priority_lsms_variable_evidence_no_candidate_requirement_rows', '0')}; raw_verified={csv_value(priority_lsms_variable_evidence_summary, 'priority_lsms_variable_evidence_raw_value_verified_rows', 'missing')}; data_write={csv_value(priority_lsms_variable_evidence_summary, 'priority_lsms_variable_evidence_data_write_status', 'missing')}; modeling_gate={csv_value(priority_lsms_variable_evidence_summary, 'modeling_gate_status', 'missing')}",
        [TEMP_DIR / "priority_lsms_isa_variable_evidence_matrix.csv", TEMP_DIR / "priority_lsms_isa_requirement_variable_coverage.csv", TEMP_DIR / "priority_lsms_isa_concept_file_shortlist.csv", RESULT_DIR / "priority_lsms_isa_variable_evidence_summary.csv", REPORT_DIR / "priority_lsms_isa_variable_evidence_matrix.md"],
        "Official public metadata variable evidence maps each refocused wave to concept-level candidate variables and files for raw review, but no raw values are accepted or promoted.",
    )
    add_bundle(
        rows,
        "priority_bundle",
        "priority_lsms_isa_raw_package_intake_packet",
        "raw_package_intake_ready_no_original_files" if csv_value(priority_lsms_raw_intake_summary, "priority_lsms_raw_intake_original_file_rows", "0") == "0" and csv_value(priority_lsms_raw_intake_summary, "priority_lsms_raw_intake_dataset_rows", "0") != "0" else "raw_package_intake_needs_review",
        f"datasets={csv_value(priority_lsms_raw_intake_summary, 'priority_lsms_raw_intake_dataset_rows', '0')}; manifest_rows={csv_value(priority_lsms_raw_intake_summary, 'priority_lsms_raw_intake_file_manifest_rows', '0')}; generated_handoffs={csv_value(priority_lsms_raw_intake_summary, 'priority_lsms_raw_intake_generated_handoff_files', '0')}; original_files={csv_value(priority_lsms_raw_intake_summary, 'priority_lsms_raw_intake_original_file_rows', '0')}; archives={csv_value(priority_lsms_raw_intake_summary, 'priority_lsms_raw_intake_archive_file_rows', '0')}; raw_tabular={csv_value(priority_lsms_raw_intake_summary, 'priority_lsms_raw_intake_raw_tabular_file_rows', '0')}; documentation={csv_value(priority_lsms_raw_intake_summary, 'priority_lsms_raw_intake_documentation_file_rows', '0')}; missing_packages={csv_value(priority_lsms_raw_intake_summary, 'priority_lsms_raw_intake_missing_package_rows', '0')}; acceptance_requirements={csv_value(priority_lsms_raw_intake_summary, 'priority_lsms_raw_intake_acceptance_requirement_rows', '0')}; blocked_requirements={csv_value(priority_lsms_raw_intake_summary, 'priority_lsms_raw_intake_blocked_requirement_rows', '0')}; data_write={csv_value(priority_lsms_raw_intake_summary, 'priority_lsms_raw_intake_data_write_status', 'missing')}; modeling_gate={csv_value(priority_lsms_raw_intake_summary, 'modeling_gate_status', 'missing')}",
        [TEMP_DIR / "priority_lsms_isa_raw_package_intake_ledger.csv", TEMP_DIR / "priority_lsms_isa_raw_package_file_manifest.csv", TEMP_DIR / "priority_lsms_isa_raw_package_acceptance_matrix.csv", RESULT_DIR / "priority_lsms_isa_raw_package_intake_summary.csv", REPORT_DIR / "priority_lsms_isa_raw_package_intake_packet.md"],
        "Raw package intake packet scans the exact refocused target folders, ignores generated markdown handoffs, and keeps every requirement blocked until a complete official raw package plus documentation is present.",
    )
    add_bundle(
        rows,
        "priority_bundle",
        "priority_lsms_isa_archive_member_preflight",
        "archive_preflight_ready_no_original_files" if csv_value(priority_lsms_archive_preflight_summary, "priority_lsms_archive_preflight_direct_file_rows", "0") == "0" and csv_value(priority_lsms_archive_preflight_summary, "priority_lsms_archive_preflight_dataset_rows", "0") != "0" else "archive_preflight_needs_review",
        f"datasets={csv_value(priority_lsms_archive_preflight_summary, 'priority_lsms_archive_preflight_dataset_rows', '0')}; direct_files={csv_value(priority_lsms_archive_preflight_summary, 'priority_lsms_archive_preflight_direct_file_rows', '0')}; direct_archives={csv_value(priority_lsms_archive_preflight_summary, 'priority_lsms_archive_preflight_direct_archive_rows', '0')}; direct_raw={csv_value(priority_lsms_archive_preflight_summary, 'priority_lsms_archive_preflight_direct_raw_tabular_rows', '0')}; direct_docs={csv_value(priority_lsms_archive_preflight_summary, 'priority_lsms_archive_preflight_direct_documentation_rows', '0')}; archive_members={csv_value(priority_lsms_archive_preflight_summary, 'priority_lsms_archive_preflight_archive_member_rows', '0')}; archive_raw_members={csv_value(priority_lsms_archive_preflight_summary, 'priority_lsms_archive_preflight_archive_raw_tabular_member_rows', '0')}; archive_doc_members={csv_value(priority_lsms_archive_preflight_summary, 'priority_lsms_archive_preflight_archive_documentation_member_rows', '0')}; ready_datasets={csv_value(priority_lsms_archive_preflight_summary, 'priority_lsms_archive_preflight_ready_dataset_rows', '0')}; blocked_datasets={csv_value(priority_lsms_archive_preflight_summary, 'priority_lsms_archive_preflight_blocked_dataset_rows', '0')}; blocked_requirements={csv_value(priority_lsms_archive_preflight_summary, 'priority_lsms_archive_preflight_blocked_requirement_rows', '0')}; data_write={csv_value(priority_lsms_archive_preflight_summary, 'priority_lsms_archive_preflight_data_write_status', 'missing')}; modeling_gate={csv_value(priority_lsms_archive_preflight_summary, 'modeling_gate_status', 'missing')}",
        [TEMP_DIR / "priority_lsms_isa_archive_member_preflight.csv", TEMP_DIR / "priority_lsms_isa_archive_member_manifest.csv", TEMP_DIR / "priority_lsms_isa_direct_file_preflight.csv", TEMP_DIR / "priority_lsms_isa_archive_requirement_preflight.csv", RESULT_DIR / "priority_lsms_isa_archive_member_preflight_summary.csv", REPORT_DIR / "priority_lsms_isa_archive_member_preflight.md"],
        "Archive/direct-file preflight reads zip/tar member names where possible, without extracting or converting data, and keeps every refocused target blocked until archive/direct raw and documentation evidence exists.",
    )
    add_bundle(
        rows,
        "priority_bundle",
        "priority_lsms_isa_raw_value_verification_workbook",
        "workbook_ready_blocked_no_original_files" if csv_value(priority_lsms_raw_value_workbook_summary, "priority_lsms_raw_value_workbook_ready_for_manual_review_rows", "0") == "0" and csv_value(priority_lsms_raw_value_workbook_summary, "priority_lsms_raw_value_workbook_dataset_rows", "0") != "0" else "workbook_needs_review",
        f"datasets={csv_value(priority_lsms_raw_value_workbook_summary, 'priority_lsms_raw_value_workbook_dataset_rows', '0')}; requirements={csv_value(priority_lsms_raw_value_workbook_summary, 'priority_lsms_raw_value_workbook_requirement_rows', '0')}; variables={csv_value(priority_lsms_raw_value_workbook_summary, 'priority_lsms_raw_value_workbook_variable_rows', '0')}; files={csv_value(priority_lsms_raw_value_workbook_summary, 'priority_lsms_raw_value_workbook_file_rows', '0')}; handoffs={csv_value(priority_lsms_raw_value_workbook_summary, 'priority_lsms_raw_value_workbook_handoff_readmes_written', '0')}; ready_review={csv_value(priority_lsms_raw_value_workbook_summary, 'priority_lsms_raw_value_workbook_ready_for_manual_review_rows', '0')}; blocked_requirements={csv_value(priority_lsms_raw_value_workbook_summary, 'priority_lsms_raw_value_workbook_blocked_requirement_rows', '0')}; raw_verified={csv_value(priority_lsms_raw_value_workbook_summary, 'priority_lsms_raw_value_workbook_raw_value_verified_rows', '0')}; data_write={csv_value(priority_lsms_raw_value_workbook_summary, 'priority_lsms_raw_value_workbook_data_write_status', 'missing')}; modeling_gate={csv_value(priority_lsms_raw_value_workbook_summary, 'modeling_gate_status', 'missing')}",
        [TEMP_DIR / "priority_lsms_isa_raw_value_requirement_workbook.csv", TEMP_DIR / "priority_lsms_isa_raw_value_variable_workbook.csv", TEMP_DIR / "priority_lsms_isa_raw_value_file_workbook.csv", RESULT_DIR / "priority_lsms_isa_raw_value_verification_workbook_summary.csv", REPORT_DIR / "priority_lsms_isa_raw_value_verification_workbook.md"],
        "Raw value verification workbook turns official candidate variables and files into fillable requirement, variable, and file review rows; all rows remain unverified until original raw files are checked.",
    )
    add_bundle(
        rows,
        "priority_bundle",
        "priority_lsms_isa_received_raw_schema_audit",
        "received_raw_schema_ready_for_manual_value_review"
        if csv_value(priority_lsms_received_raw_schema_summary, "priority_lsms_received_raw_requirement_candidate_present_rows", "0") != "0"
        else "received_raw_schema_needs_review",
        f"datasets={csv_value(priority_lsms_received_raw_schema_summary, 'priority_lsms_received_raw_schema_dataset_rows', '0')}; files={csv_value(priority_lsms_received_raw_schema_summary, 'priority_lsms_received_raw_schema_file_rows', '0')}; readable_files={csv_value(priority_lsms_received_raw_schema_summary, 'priority_lsms_received_raw_schema_readable_file_rows', '0')}; variables={csv_value(priority_lsms_received_raw_schema_summary, 'priority_lsms_received_raw_schema_variable_rows', '0')}; candidate_rows={csv_value(priority_lsms_received_raw_schema_summary, 'priority_lsms_received_raw_requirement_candidate_rows', '0')}; present_candidates={csv_value(priority_lsms_received_raw_schema_summary, 'priority_lsms_received_raw_requirement_candidate_present_rows', '0')}; failed_files={csv_value(priority_lsms_received_raw_schema_summary, 'priority_lsms_received_raw_schema_failed_file_rows', '0')}; data_write={csv_value(priority_lsms_received_raw_schema_summary, 'priority_lsms_received_raw_schema_data_write_status', 'missing')}; modeling_gate={csv_value(priority_lsms_received_raw_schema_summary, 'modeling_gate_status', 'missing')}",
        [TEMP_DIR / "priority_lsms_isa_received_raw_schema_file_inventory.csv", TEMP_DIR / "priority_lsms_isa_received_raw_variable_schema.csv", TEMP_DIR / "priority_lsms_isa_received_raw_requirement_evidence.csv", RESULT_DIR / "priority_lsms_isa_received_raw_schema_audit_summary.csv", REPORT_DIR / "priority_lsms_isa_received_raw_schema_audit.md"],
        "Received raw schema audit reads the locally received official archive into metadata-only schema and value-stat evidence, making Malawi ready for manual raw value review while keeping data writes and modeling blocked.",
    )
    add_bundle(
        rows,
        "priority_bundle",
        "priority_lsms_isa_received_raw_value_profile",
        "received_raw_value_profile_ready_for_manual_value_review"
        if csv_value(priority_lsms_received_raw_value_profile_summary, "priority_lsms_received_raw_value_profile_variable_rows", "0") != "0"
        else "received_raw_value_profile_needs_review",
        f"datasets={csv_value(priority_lsms_received_raw_value_profile_summary, 'priority_lsms_received_raw_value_profile_dataset_rows', '0')}; variables={csv_value(priority_lsms_received_raw_value_profile_summary, 'priority_lsms_received_raw_value_profile_variable_rows', '0')}; nonmissing_variables={csv_value(priority_lsms_received_raw_value_profile_summary, 'priority_lsms_received_raw_value_profile_nonmissing_variable_rows', '0')}; value_label_variables={csv_value(priority_lsms_received_raw_value_profile_summary, 'priority_lsms_received_raw_value_profile_value_label_rows', '0')}; key_design_geo_rows={csv_value(priority_lsms_received_raw_value_profile_summary, 'priority_lsms_received_raw_key_design_geography_profile_rows', '0')}; requirement_profiles={csv_value(priority_lsms_received_raw_value_profile_summary, 'priority_lsms_received_raw_value_requirement_profile_rows', '0')}; requirements_with_profiles={csv_value(priority_lsms_received_raw_value_profile_summary, 'priority_lsms_received_raw_value_profile_requirements_with_profiles', '0')}; raw_verified={csv_value(priority_lsms_received_raw_value_profile_summary, 'priority_lsms_received_raw_value_profile_raw_value_verified_rows', '0')}; data_write={csv_value(priority_lsms_received_raw_value_profile_summary, 'priority_lsms_received_raw_value_profile_data_write_status', 'missing')}; modeling_gate={csv_value(priority_lsms_received_raw_value_profile_summary, 'modeling_gate_status', 'missing')}",
        [TEMP_DIR / "priority_lsms_isa_received_raw_value_profile.csv", TEMP_DIR / "priority_lsms_isa_received_raw_key_design_geography_profile.csv", TEMP_DIR / "priority_lsms_isa_received_raw_value_requirement_profile.csv", RESULT_DIR / "priority_lsms_isa_received_raw_value_profile_summary.csv", REPORT_DIR / "priority_lsms_isa_received_raw_value_profile.md"],
        "Received raw value profile reads candidate variables and utility key/design/geography fields from the local official archive into distribution evidence for manual verification; it still does not certify raw-value verification or write promoted data.",
    )
    add_bundle(
        rows,
        "priority_bundle",
        "priority_lsms_isa_received_raw_semantics_review",
        "received_raw_semantics_review_ready_for_manual_value_review"
        if csv_value(priority_lsms_received_raw_semantics_summary, "priority_lsms_received_raw_semantics_requirement_rows", "0") != "0"
        else "received_raw_semantics_review_needs_review",
        f"datasets={csv_value(priority_lsms_received_raw_semantics_summary, 'priority_lsms_received_raw_semantics_dataset_rows', '0')}; variables={csv_value(priority_lsms_received_raw_semantics_summary, 'priority_lsms_received_raw_semantics_variable_rows', '0')}; ddi_documented_variables={csv_value(priority_lsms_received_raw_semantics_summary, 'priority_lsms_received_raw_semantics_ddi_documented_variable_rows', '0')}; requirements={csv_value(priority_lsms_received_raw_semantics_summary, 'priority_lsms_received_raw_semantics_requirement_rows', '0')}; documentation_scope={csv_value(priority_lsms_received_raw_semantics_summary, 'priority_lsms_received_raw_semantics_documentation_scope_rows', '0')}; missing_unit_recall_skip_rows={csv_value(priority_lsms_received_raw_semantics_summary, 'priority_lsms_received_raw_semantics_missing_codes_units_recall_skip_requirement_rows', '0')}; raw_verified={csv_value(priority_lsms_received_raw_semantics_summary, 'priority_lsms_received_raw_semantics_raw_value_verified_rows', '0')}; data_write={csv_value(priority_lsms_received_raw_semantics_summary, 'priority_lsms_received_raw_semantics_data_write_status', 'missing')}; modeling_gate={csv_value(priority_lsms_received_raw_semantics_summary, 'modeling_gate_status', 'missing')}",
        [TEMP_DIR / "priority_lsms_isa_received_raw_semantics_variable_review.csv", TEMP_DIR / "priority_lsms_isa_received_raw_semantics_requirement_review.csv", TEMP_DIR / "priority_lsms_isa_received_raw_documentation_scope_review.csv", RESULT_DIR / "priority_lsms_isa_received_raw_semantics_review_summary.csv", REPORT_DIR / "priority_lsms_isa_received_raw_semantics_review.md"],
        "Received raw semantics review aligns official DDI/catalog documentation to value profiles for units, recall periods, missing-code, skip-pattern, and merge-level review; it still does not certify raw-value verification or write promoted data.",
    )
    add_bundle(
        rows,
        "priority_bundle",
        "mwi2004_raw_requirement_verification",
        "mwi2004_raw_backed_evidence_ready_not_final_verified"
        if csv_value(mwi2004_raw_requirement_summary, "requirements_with_raw_backed_evidence", "0") != "0"
        else "mwi2004_raw_requirement_verification_missing",
        f"country_wave={csv_value(mwi2004_raw_requirement_summary, 'country_wave', 'missing')}; members_read={csv_value(mwi2004_raw_requirement_summary, 'members_read', '0')}; requirements={csv_value(mwi2004_raw_requirement_summary, 'requirements_with_raw_backed_evidence', '0')}; key_or_join_checks={csv_value(mwi2004_raw_requirement_summary, 'key_or_join_checks_passing', '0')}; missing_requested_columns={csv_value(mwi2004_raw_requirement_summary, 'missing_requested_columns', '0')}; raw_value_decision={csv_value(mwi2004_raw_requirement_summary, 'raw_value_verification_decision', 'missing')}; data_write={csv_value(mwi2004_raw_requirement_summary, 'data_write_gate_status', 'missing')}",
        [TEMP_DIR / "mwi2004_raw_requirement_evidence.csv", TEMP_DIR / "mwi2004_raw_module_join_evidence.csv", TEMP_DIR / "mwi2004_raw_financial_oop_profile.csv", RESULT_DIR / "mwi2004_raw_requirement_verification_summary.csv", REPORT_DIR / "mwi2004_raw_requirement_verification.md"],
        "Focused Malawi 2004 raw requirement verification reads selected original Stata files into aggregate key, join, financial, OOP, timing, geography, and health-need/access evidence while keeping final verification, data writes, and modeling blocked.",
    )
    add_bundle(
        rows,
        "priority_bundle",
        "mwi2004_requirement_acceptance_decisions",
        "mwi2004_acceptance_decisions_fail_closed"
        if csv_value(mwi2004_acceptance_summary, "decision_rows", "0") != "0"
        else "mwi2004_acceptance_decisions_missing",
        f"country_wave={csv_value(mwi2004_acceptance_summary, 'country_wave', 'missing')}; decisions={csv_value(mwi2004_acceptance_summary, 'decision_rows', '0')}; mechanical_pass_or_partial={csv_value(mwi2004_acceptance_summary, 'mechanical_raw_checks_pass_or_partial', '0')}; hard_blocked={csv_value(mwi2004_acceptance_summary, 'hard_blocked_requirements', '0')}; final_verified={csv_value(mwi2004_acceptance_summary, 'final_verified_requirements', '0')}; health_unmatched={csv_value(mwi2004_acceptance_summary, 'health_person_unmatched_to_roster', 'missing')}; oop_tolerance={csv_value(mwi2004_acceptance_summary, 'oop_component_diff_le_0_01_rows', 'missing')}; data_write={csv_value(mwi2004_acceptance_summary, 'data_write_gate_status', 'missing')}",
        [RESULT_DIR / "mwi2004_requirement_acceptance_decisions.csv", TEMP_DIR / "mwi2004_requirement_acceptance_metrics.csv", RESULT_DIR / "mwi2004_requirement_acceptance_summary.csv", REPORT_DIR / "mwi2004_requirement_acceptance_decisions.md"],
        "Focused Malawi 2004 acceptance decisions convert raw evidence into requirement-level pass/block actions without exporting raw IDs and without opening full promotion or data writes.",
    )
    add_bundle(
        rows,
        "priority_bundle",
        "mwi2004_financial_protection_construction_policy",
        "mwi2004_che10_che25_financial_inputs_verified_sdg_blocked"
        if csv_value(mwi2004_financial_policy_summary, "financial_policy_status", "missing") == "che10_che25_financial_inputs_verified_sdg382_blocked"
        else "mwi2004_financial_policy_missing",
        f"country_wave={csv_value(mwi2004_financial_policy_summary, 'country_wave', 'missing')}; household_rows={csv_value(mwi2004_financial_policy_summary, 'household_financial_rows', 'missing')}; che10_rows={csv_value(mwi2004_financial_policy_summary, 'che10_candidate_rows', 'missing')}; che10_weighted={csv_value(mwi2004_financial_policy_summary, 'che10_candidate_weighted_rate', 'missing')}; che25_rows={csv_value(mwi2004_financial_policy_summary, 'che25_candidate_rows', 'missing')}; che25_weighted={csv_value(mwi2004_financial_policy_summary, 'che25_candidate_weighted_rate', 'missing')}; financial_inputs_ready={csv_value(mwi2004_financial_policy_summary, 'che10_che25_financial_inputs_ready', '0')}; sdg382_ready={csv_value(mwi2004_financial_policy_summary, 'sdg382_ready', '0')}; data_write={csv_value(mwi2004_financial_policy_summary, 'data_write_gate_status', 'missing')}",
        [RESULT_DIR / "mwi2004_financial_protection_construction_policy.csv", RESULT_DIR / "mwi2004_financial_protection_construction_policy_summary.csv", REPORT_DIR / "mwi2004_financial_protection_construction_policy.md"],
        "Focused Malawi 2004 financial policy accepts household CHE10/CHE25 inputs from raw labels and numeric consistency checks while keeping SDG 3.8.2 and data writes blocked.",
    )
    add_bundle(
        rows,
        "priority_bundle",
        "mwi2004_sdg382_discretionary_budget_parameter_audit",
        "mwi2004_sdg382_internal_inputs_ready_external_parameters_blocked"
        if csv_value(mwi2004_sdg382_parameter_summary, "raw_internal_sdg382_inputs_complete", "0") == "1"
        and csv_value(mwi2004_sdg382_parameter_summary, "sdg382_ready", "1") == "0"
        else "mwi2004_sdg382_parameter_audit_missing_or_inconsistent",
        f"country_wave={csv_value(mwi2004_sdg382_parameter_summary, 'country_wave', 'missing')}; metadata_update={csv_value(mwi2004_sdg382_parameter_summary, 'official_metadata_last_update', 'missing')}; threshold={csv_value(mwi2004_sdg382_parameter_summary, 'official_threshold_discretionary_budget', 'missing')}; internal_rows={csv_value(mwi2004_sdg382_parameter_summary, 'household_rows_with_internal_sdg382_inputs', '0')}; positive_oop={csv_value(mwi2004_sdg382_parameter_summary, 'positive_oop_household_rows', '0')}; median_excl_oop_raw={csv_value(mwi2004_sdg382_parameter_summary, 'weighted_median_daily_consumption_excluding_oop_pc_raw', 'missing')}; external_ppp_cpi_verified={csv_value(mwi2004_sdg382_parameter_summary, 'external_ppp_cpi_parameters_verified', '0')}; spl_verified={csv_value(mwi2004_sdg382_parameter_summary, 'spl_local_currency_verified', '0')}; sdg382_ready={csv_value(mwi2004_sdg382_parameter_summary, 'sdg382_ready', '0')}; data_write={csv_value(mwi2004_sdg382_parameter_summary, 'data_write_gate_status', 'missing')}",
        [RESULT_DIR / "mwi2004_sdg382_discretionary_budget_parameter_audit.csv", RESULT_DIR / "mwi2004_sdg382_discretionary_budget_parameter_summary.csv", REPORT_DIR / "mwi2004_sdg382_discretionary_budget_parameter_audit.md"],
        "Malawi 2004 SDG 3.8.2 parameter audit aligns with the current 2026 official discretionary-budget metadata, verifies internal raw inputs, and keeps the SDG gate fail-closed until PPP/CPI/SPL parameters are frozen.",
    )
    add_bundle(
        rows,
        "priority_bundle",
        "mwi2004_sdg382_external_parameter_source_ledger",
        "mwi2004_sdg382_external_parameters_captured_bridge_unaccepted"
        if csv_value(mwi2004_sdg382_external_parameter_summary, "private_consumption_ppp_source_verified", "0") == "1"
        and csv_value(mwi2004_sdg382_external_parameter_summary, "external_parameter_bridge_accepted", "1") == "0"
        else "mwi2004_sdg382_external_parameter_source_ledger_missing_or_inconsistent",
        f"country_wave={csv_value(mwi2004_sdg382_external_parameter_summary, 'country_wave', 'missing')}; parameter_rows={csv_value(mwi2004_sdg382_external_parameter_summary, 'parameter_rows', '0')}; ppp_private_2017={csv_value(mwi2004_sdg382_external_parameter_summary, 'wdi_ppp_private_consumption_2017', 'missing')}; cpi_2004={csv_value(mwi2004_sdg382_external_parameter_summary, 'wdi_cpi_2004', 'missing')}; cpi_2017={csv_value(mwi2004_sdg382_external_parameter_summary, 'wdi_cpi_2017', 'missing')}; cpi_ratio={csv_value(mwi2004_sdg382_external_parameter_summary, 'candidate_cpi_ratio_2017_to_2004', 'missing')}; candidate_spl_raw={csv_value(mwi2004_sdg382_external_parameter_summary, 'candidate_spl_daily_raw_2004_mwk', 'missing')}; bridge_accepted={csv_value(mwi2004_sdg382_external_parameter_summary, 'external_parameter_bridge_accepted', 'missing')}; sdg382_ready={csv_value(mwi2004_sdg382_external_parameter_summary, 'sdg382_ready', 'missing')}; modeling_gate={csv_value(mwi2004_sdg382_external_parameter_summary, 'modeling_gate_status', 'missing')}",
        [RESULT_DIR / "mwi2004_sdg382_external_parameter_source_ledger.csv", RESULT_DIR / "mwi2004_sdg382_external_parameter_candidate_summary.csv", REPORT_DIR / "mwi2004_sdg382_external_parameter_source_ledger.md"],
        "Malawi 2004 external parameter source ledger captures World Bank 2017 PPP and 2004/2017 CPI candidates, derives a candidate SPL bridge, and keeps SDG 3.8.2 blocked until the survey base-period bridge is accepted.",
    )
    add_bundle(
        rows,
        "priority_bundle",
        "mwi2004_sdg382_candidate_classification_precheck",
        "mwi2004_sdg382_candidate_classification_precheck_current_gate_closed"
        if csv_value(mwi2004_sdg382_candidate_precheck_summary, "candidate_classification_written_to_data", "1") == "0"
        and csv_value(mwi2004_sdg382_candidate_precheck_summary, "sdg382_ready", "1") == "0"
        else "mwi2004_sdg382_candidate_classification_precheck_missing_or_overopened",
        f"country_wave={csv_value(mwi2004_sdg382_candidate_precheck_summary, 'country_wave', 'missing')}; spl_daily={csv_value(mwi2004_sdg382_candidate_precheck_summary, 'candidate_spl_daily_raw_2004_mwk', 'missing')}; rows={csv_value(mwi2004_sdg382_candidate_precheck_summary, 'household_rows', '0')}; nonpositive_discretionary={csv_value(mwi2004_sdg382_candidate_precheck_summary, 'nonpositive_discretionary_budget_rows', '0')}; strict_candidate_rows={csv_value(mwi2004_sdg382_candidate_precheck_summary, 'positive_discretionary_candidate_sdg382_rows', '0')}; strict_rate={csv_value(mwi2004_sdg382_candidate_precheck_summary, 'positive_discretionary_candidate_sdg382_weighted_rate', 'missing')}; floor_candidate_rows={csv_value(mwi2004_sdg382_candidate_precheck_summary, 'floor_variant_candidate_sdg382_rows', '0')}; floor_rate={csv_value(mwi2004_sdg382_candidate_precheck_summary, 'floor_variant_candidate_sdg382_weighted_rate', 'missing')}; bridge_accepted={csv_value(mwi2004_sdg382_candidate_precheck_summary, 'external_parameter_bridge_accepted', 'missing')}; sdg382_ready={csv_value(mwi2004_sdg382_candidate_precheck_summary, 'sdg382_ready', 'missing')}; data_write={csv_value(mwi2004_sdg382_candidate_precheck_summary, 'data_write_gate_status', 'missing')}",
        [RESULT_DIR / "mwi2004_sdg382_candidate_classification_precheck.csv", RESULT_DIR / "mwi2004_sdg382_candidate_classification_precheck_summary.csv", REPORT_DIR / "mwi2004_sdg382_candidate_classification_precheck.md"],
        "Malawi 2004 candidate SDG 3.8.2 classification precheck reports aggregate-only denominator stress tests under candidate PPP/CPI/SPL parameters without writing household-level SDG data or opening the SDG gate.",
    )
    add_bundle(
        rows,
        "priority_bundle",
        "mwi2004_sdg382_official_denominator_rule_audit",
        "mwi2004_sdg382_official_denominator_rule_accepted_spl_bridge_blocked"
        if csv_value(mwi2004_sdg382_denominator_rule_summary, "official_denominator_rule_accepted", "0") == "1"
        and csv_value(mwi2004_sdg382_denominator_rule_summary, "external_parameter_bridge_accepted", "1") == "0"
        and csv_value(mwi2004_sdg382_denominator_rule_summary, "sdg382_ready", "1") == "0"
        else "mwi2004_sdg382_official_denominator_rule_audit_missing_or_overopened",
        f"country_wave={csv_value(mwi2004_sdg382_denominator_rule_summary, 'country_wave', 'missing')}; metadata_update={csv_value(mwi2004_sdg382_denominator_rule_summary, 'official_metadata_last_update', 'missing')}; official_rule_accepted={csv_value(mwi2004_sdg382_denominator_rule_summary, 'official_denominator_rule_accepted', '0')}; nonpositive_discretionary={csv_value(mwi2004_sdg382_denominator_rule_summary, 'nonpositive_discretionary_budget_rows', '0')}; positive_oop_nonpositive={csv_value(mwi2004_sdg382_denominator_rule_summary, 'positive_oop_nonpositive_discretionary_rows', '0')}; official_rule_candidate_rows={csv_value(mwi2004_sdg382_denominator_rule_summary, 'official_rule_candidate_sdg382_rows', '0')}; official_rule_candidate_rate={csv_value(mwi2004_sdg382_denominator_rule_summary, 'official_rule_candidate_sdg382_weighted_rate', 'missing')}; bridge_accepted={csv_value(mwi2004_sdg382_denominator_rule_summary, 'external_parameter_bridge_accepted', 'missing')}; sdg382_ready={csv_value(mwi2004_sdg382_denominator_rule_summary, 'sdg382_ready', 'missing')}; data_write={csv_value(mwi2004_sdg382_denominator_rule_summary, 'data_write_gate_status', 'missing')}",
        [RESULT_DIR / "mwi2004_sdg382_official_denominator_rule_audit.csv", RESULT_DIR / "mwi2004_sdg382_official_denominator_rule_summary.csv", REPORT_DIR / "mwi2004_sdg382_official_denominator_rule_audit.md"],
        "Malawi 2004 official denominator rule audit accepts the UNSD rule for nonpositive discretionary budgets, but leaves SDG 3.8.2 as candidate-only because the local-currency SPL bridge remains unaccepted.",
    )
    add_bundle(
        rows,
        "priority_bundle",
        "mwi2004_timing_geography_linkage_policy",
        "mwi2004_timing_admin_ea_verified_climate_route_blocked"
        if csv_value(mwi2004_timing_geography_summary, "timing_geography_policy_status", "missing") == "raw_timing_admin_ea_geography_verified_climate_route_blocked"
        else "mwi2004_timing_geography_policy_missing",
        f"country_wave={csv_value(mwi2004_timing_geography_summary, 'country_wave', 'missing')}; idate_rows={csv_value(mwi2004_timing_geography_summary, 'idate_nonmissing_rows', 'missing')}; date_min={csv_value(mwi2004_timing_geography_summary, 'interview_date_min', 'missing')}; date_max={csv_value(mwi2004_timing_geography_summary, 'interview_date_max', 'missing')}; months={csv_value(mwi2004_timing_geography_summary, 'interview_month_count', 'missing')}; household_ea={csv_value(mwi2004_timing_geography_summary, 'household_ea_distinct', 'missing')}; ea_match={csv_value(mwi2004_timing_geography_summary, 'household_ea_matched_to_ea_file', 'missing')}; timing_verified={csv_value(mwi2004_timing_geography_summary, 'survey_timing_final_verified', '0')}; geography_verified={csv_value(mwi2004_timing_geography_summary, 'climate_geography_final_verified', '0')}; accepted_route={csv_value(mwi2004_timing_geography_summary, 'accepted_chirps_era5_route', '0')}; data_write={csv_value(mwi2004_timing_geography_summary, 'data_write_gate_status', 'missing')}",
        [RESULT_DIR / "mwi2004_timing_geography_linkage_policy.csv", RESULT_DIR / "mwi2004_timing_geography_linkage_policy_summary.csv", REPORT_DIR / "mwi2004_timing_geography_linkage_policy.md"],
        "Focused Malawi 2004 timing/geography policy accepts raw interview-month timing and admin/EA geography for climate-route review while keeping CHIRPS/ERA5 route acceptance and data writes blocked.",
    )
    add_bundle(
        rows,
        "priority_bundle",
        "mwi2004_chirps_admin2_route_policy",
        "mwi2004_chirps_admin2_route_design_ready_extraction_pending"
        if csv_value(mwi2004_chirps_route_summary, "route_design_ready", "0") == "1"
        else "mwi2004_chirps_admin2_route_policy_missing_or_blocked",
        f"country_wave={csv_value(mwi2004_chirps_route_summary, 'country_wave', 'missing')}; status={csv_value(mwi2004_chirps_route_summary, 'climate_route_policy_status', 'missing')}; route_design_ready={csv_value(mwi2004_chirps_route_summary, 'route_design_ready', '0')}; raw_districts={csv_value(mwi2004_chirps_route_summary, 'raw_district_rows', '0')}; boundary_features={csv_value(mwi2004_chirps_route_summary, 'boundary_adm2_features', '0')}; matches={csv_value(mwi2004_chirps_route_summary, 'raw_district_boundary_matches', '0')}; unmatched={csv_value(mwi2004_chirps_route_summary, 'raw_district_boundary_unmatched', '0')}; required_chirps_months={csv_value(mwi2004_chirps_route_summary, 'required_chirps_months', '0')}; accepted_route={csv_value(mwi2004_chirps_route_summary, 'accepted_chirps_era5_route', '0')}; data_write={csv_value(mwi2004_chirps_route_summary, 'data_write_gate_status', 'missing')}",
        [RESULT_DIR / "mwi2004_chirps_admin2_route_policy.csv", RESULT_DIR / "mwi2004_chirps_admin2_crosswalk.csv", RESULT_DIR / "mwi2004_chirps_admin2_required_downloads.csv", RESULT_DIR / "mwi2004_chirps_admin2_route_policy_summary.csv", REPORT_DIR / "mwi2004_chirps_admin2_route_policy.md"],
        "Focused Malawi 2004 CHIRPS route policy maps raw district labels to Malawi ADM2 boundaries and creates the monthly CHIRPS download manifest, but keeps extraction, validation, promoted climate linkage, and data writes blocked.",
    )
    add_bundle(
        rows,
        "priority_bundle",
        "mwi2004_chirps_admin2_extraction_validation",
        "mwi2004_chirps_admin2_extraction_validated"
        if csv_value(mwi2004_chirps_extraction_summary, "accepted_chirps_era5_route", "0") == "1"
        else "mwi2004_chirps_admin2_extraction_missing_or_blocked",
        f"country_wave={csv_value(mwi2004_chirps_extraction_summary, 'country_wave', 'missing')}; files={csv_value(mwi2004_chirps_extraction_summary, 'chirps_files_downloaded_readable', '0')}/{csv_value(mwi2004_chirps_extraction_summary, 'chirps_files_required', '0')}; district_month_rows={csv_value(mwi2004_chirps_extraction_summary, 'district_month_exposure_rows', '0')}; lag_rows={csv_value(mwi2004_chirps_extraction_summary, 'lag_window_exposure_rows', '0')}; lag_complete={csv_value(mwi2004_chirps_extraction_summary, 'lag_window_complete_rows', '0')}; precip_min={csv_value(mwi2004_chirps_extraction_summary, 'mean_precip_min_mm', 'missing')}; precip_max={csv_value(mwi2004_chirps_extraction_summary, 'mean_precip_max_mm', 'missing')}; accepted_route={csv_value(mwi2004_chirps_extraction_summary, 'accepted_chirps_era5_route', '0')}; data_write={csv_value(mwi2004_chirps_extraction_summary, 'data_write_gate_status', 'missing')}",
        [RESULT_DIR / "mwi2004_chirps_admin2_download_audit.csv", RESULT_DIR / "mwi2004_chirps_admin2_district_month_exposure.csv", RESULT_DIR / "mwi2004_chirps_admin2_lag_window_exposure.csv", RESULT_DIR / "mwi2004_chirps_admin2_extraction_validation.csv", RESULT_DIR / "mwi2004_chirps_admin2_extraction_summary.csv", REPORT_DIR / "mwi2004_chirps_admin2_extraction_validation.md"],
        "Focused Malawi 2004 CHIRPS extraction validates local monthly GeoTIFF downloads, extracts ADM2 district-month rainfall, and builds district-interview-month lag windows without writing a promoted household dataset.",
    )
    add_bundle(
        rows,
        "priority_bundle",
        "mwi2004_health_access_label_skip_decisions",
        "mwi2004_health_access_label_skip_blockers_identified"
        if csv_value(mwi2004_health_access_summary, "label_decision_rows", "0") != "0"
        else "mwi2004_health_access_label_skip_missing",
        f"country_wave={csv_value(mwi2004_health_access_summary, 'country_wave', 'missing')}; label_rows={csv_value(mwi2004_health_access_summary, 'label_decision_rows', '0')}; mapping_ready={csv_value(mwi2004_health_access_summary, 'mapping_ready_rows', '0')}; manual_review={csv_value(mwi2004_health_access_summary, 'manual_review_rows', '0')}; no_money_rows={csv_value(mwi2004_health_access_summary, 'financial_barrier_no_money_rows', 'missing')}; formal_care={csv_value(mwi2004_health_access_summary, 'formal_facility_care_rows', 'missing')}; skip_leakage={csv_value(mwi2004_health_access_summary, 'total_skip_leakage_rows', 'missing')}; decision={csv_value(mwi2004_health_access_summary, 'health_access_label_skip_decision', 'missing')}; data_write={csv_value(mwi2004_health_access_summary, 'data_write_gate_status', 'missing')}",
        [RESULT_DIR / "mwi2004_health_access_label_skip_decisions.csv", TEMP_DIR / "mwi2004_health_access_skip_consistency_metrics.csv", RESULT_DIR / "mwi2004_health_access_label_skip_summary.csv", REPORT_DIR / "mwi2004_health_access_label_skip_decisions.md"],
        "Focused Malawi 2004 health/access label-skip decisions map raw value labels into illness, care-seeking, forgone-care, coping, chronic, and maternal-care roles while preserving final verification and data-write blockers.",
    )
    add_bundle(
        rows,
        "priority_bundle",
        "mwi2004_health_exception_audit",
        "mwi2004_health_exceptions_unresolved"
        if csv_value(mwi2004_health_exception_summary, "exception_policy_status", "missing") == "policy_pending_exception_unresolved"
        else "mwi2004_health_exceptions_need_review",
        f"country_wave={csv_value(mwi2004_health_exception_summary, 'country_wave', 'missing')}; health_unmatched={csv_value(mwi2004_health_exception_summary, 'health_person_unmatched_to_roster', 'missing')}; roster_unmatched={csv_value(mwi2004_health_exception_summary, 'roster_person_unmatched_to_health', 'missing')}; d07a_leakage={csv_value(mwi2004_health_exception_summary, 'd07a_skip_leakage_rows', 'missing')}; overlap={csv_value(mwi2004_health_exception_summary, 'd07a_skip_leakage_overlap_with_unmatched_health_rows', 'missing')}; explained_by_nonroster={csv_value(mwi2004_health_exception_summary, 'd07a_skip_leakage_explained_by_nonroster_rows', 'missing')}; other_leakage={csv_value(mwi2004_health_exception_summary, 'other_skip_leakage_rows', 'missing')}; data_write={csv_value(mwi2004_health_exception_summary, 'data_write_gate_status', 'missing')}",
        [RESULT_DIR / "mwi2004_health_exception_audit.csv", RESULT_DIR / "mwi2004_health_exception_summary.csv", REPORT_DIR / "mwi2004_health_exception_audit.md"],
        "Focused Malawi 2004 health exception audit tests whether person-key exceptions explain skip leakage, exports no raw IDs, and keeps health/access verification blocked when exceptions are separate.",
    )
    add_bundle(
        rows,
        "priority_bundle",
        "mwi2004_health_access_construction_policy",
        "mwi2004_health_access_policy_ready_fail_closed"
        if csv_value(mwi2004_health_policy_summary, "construction_policy_status", "missing") == "candidate_policy_ready_active_skip_and_provider_blockers"
        else "mwi2004_health_access_policy_missing",
        f"country_wave={csv_value(mwi2004_health_policy_summary, 'country_wave', 'missing')}; denominator={csv_value(mwi2004_health_policy_summary, 'acute_need_denominator_rows', 'missing')}; no_money={csv_value(mwi2004_health_policy_summary, 'financial_barrier_forgone_care_rows', 'missing')}; formal_core={csv_value(mwi2004_health_policy_summary, 'formal_care_core_rows', 'missing')}; formal_extended={csv_value(mwi2004_health_policy_summary, 'formal_care_extended_rows', 'missing')}; informal_self={csv_value(mwi2004_health_policy_summary, 'informal_or_self_care_rows', 'missing')}; skip_exceptions={csv_value(mwi2004_health_policy_summary, 'd07a_d07b_skip_exception_rows', 'missing')}; final_verified={csv_value(mwi2004_health_policy_summary, 'final_health_access_verified', '0')}; data_write={csv_value(mwi2004_health_policy_summary, 'data_write_gate_status', 'missing')}",
        [RESULT_DIR / "mwi2004_health_access_construction_policy.csv", RESULT_DIR / "mwi2004_health_access_construction_policy_summary.csv", REPORT_DIR / "mwi2004_health_access_construction_policy.md"],
        "Focused Malawi 2004 construction policy proposes an aggregate health/access denominator, no-money forgone-care rule, provider grouping sensitivities, and coping context while keeping final verification and data writes blocked.",
    )
    add_bundle(
        rows,
        "priority_bundle",
        "mwi2004_access_person_key_resolution_policy",
        "mwi2004_access_cost_barrier_verified_with_documented_exclusions"
        if csv_value(mwi2004_access_resolution_summary, "health_access_final_verified", "0") == "1"
        else "mwi2004_access_resolution_still_blocked",
        f"country_wave={csv_value(mwi2004_access_resolution_summary, 'country_wave', 'missing')}; status={csv_value(mwi2004_access_resolution_summary, 'access_resolution_status', 'missing')}; matched_rows={csv_value(mwi2004_access_resolution_summary, 'analytic_roster_matched_health_rows', 'missing')}; denominator={csv_value(mwi2004_access_resolution_summary, 'acute_need_denominator_rows', 'missing')}; no_money={csv_value(mwi2004_access_resolution_summary, 'cost_barrier_forgone_care_rows', 'missing')}; health_unmatched={csv_value(mwi2004_access_resolution_summary, 'health_person_unmatched_to_roster', 'missing')}; roster_unmatched={csv_value(mwi2004_access_resolution_summary, 'roster_person_unmatched_to_health', 'missing')}; skip_no_money={csv_value(mwi2004_access_resolution_summary, 'd07a_d07b_skip_exception_no_money_rows', 'missing')}; access_ready={csv_value(mwi2004_access_resolution_summary, 'access_forgone_care_inputs_ready', '0')}; data_write={csv_value(mwi2004_access_resolution_summary, 'data_write_gate_status', 'missing')}",
        [RESULT_DIR / "mwi2004_access_person_key_resolution_policy.csv", RESULT_DIR / "mwi2004_access_person_key_resolution_policy_summary.csv", REPORT_DIR / "mwi2004_access_person_key_resolution_policy.md"],
        "Focused Malawi 2004 access/person-key policy accepts cost-barrier forgone care for roster-matched d04==Yes rows with documented nonroster and skip-leakage exclusions, while keeping data writes and climate linkage blocked.",
    )
    add_bundle(
        rows,
        "priority_bundle",
        "mwi2004_missing_units_recall_skip_policy",
        "mwi2004_missing_units_recall_skip_verified"
        if csv_value(mwi2004_missing_units_summary, "missing_units_recall_skip_policy_final_verified", "0") == "1"
        else "mwi2004_missing_units_recall_skip_still_blocked",
        f"country_wave={csv_value(mwi2004_missing_units_summary, 'country_wave', 'missing')}; status={csv_value(mwi2004_missing_units_summary, 'missing_units_recall_skip_policy_status', 'missing')}; financial_units={csv_value(mwi2004_missing_units_summary, 'financial_units_verified', '0')}; access_units={csv_value(mwi2004_missing_units_summary, 'access_units_recall_skip_verified', '0')}; timing_units={csv_value(mwi2004_missing_units_summary, 'timing_units_verified', '0')}; geography_units={csv_value(mwi2004_missing_units_summary, 'geography_units_verified', '0')}; sdg382_ready={csv_value(mwi2004_missing_units_summary, 'sdg382_ready', '0')}; accepted_route={csv_value(mwi2004_missing_units_summary, 'accepted_chirps_era5_route', '0')}; data_write={csv_value(mwi2004_missing_units_summary, 'data_write_gate_status', 'missing')}",
        [RESULT_DIR / "mwi2004_missing_units_recall_skip_policy.csv", RESULT_DIR / "mwi2004_missing_units_recall_skip_policy_summary.csv", REPORT_DIR / "mwi2004_missing_units_recall_skip_policy.md"],
        "Focused Malawi 2004 policy accepts units, recall periods, missing values, and skip handling for CHE10/CHE25 and cost-barrier access while keeping SDG 3.8.2, climate linkage, and data writes blocked.",
    )
    add_bundle(
        rows,
        "priority_bundle",
        "mwi2004_promoted_household_climate_dataset",
        "mwi2004_promoted_household_climate_dataset_ready"
        if csv_value(mwi2004_promoted_dataset_summary, "analysis_ready_status", "not_promoted") == "promoted_analysis_ready"
        else "mwi2004_promoted_household_climate_dataset_missing_or_blocked",
        f"country_wave={csv_value(mwi2004_promoted_dataset_summary, 'country_wave', 'missing')}; status={csv_value(mwi2004_promoted_dataset_summary, 'analysis_ready_status', 'missing')}; rows={csv_value(mwi2004_promoted_dataset_summary, 'promoted_rows', '0')}; che10={csv_value(mwi2004_promoted_dataset_summary, 'che10_rows', '0')}; che25={csv_value(mwi2004_promoted_dataset_summary, 'che25_rows', '0')}; cost_barrier_households={csv_value(mwi2004_promoted_dataset_summary, 'households_any_cost_barrier_forgone_care', '0')}; both_che10_cost={csv_value(mwi2004_promoted_dataset_summary, 'both_che10_and_cost_barrier_rows', '0')}; climate_complete={csv_value(mwi2004_promoted_dataset_summary, 'climate_exposure_complete_rows', '0')}; data_write={csv_value(mwi2004_promoted_dataset_summary, 'data_write_gate_status', 'missing')}; modeling_gate={csv_value(mwi2004_promoted_dataset_summary, 'modeling_gate_status', 'missing')}",
        [RESULT_DIR / "mwi2004_promoted_household_climate_dataset_summary.csv", RESULT_DIR / "mwi2004_promoted_household_climate_dataset_dictionary.csv", RESULT_DIR / "mwi2004_promoted_household_climate_dataset_validation.csv", REPORT_DIR / "mwi2004_promoted_household_climate_dataset.md"],
        "Focused Malawi 2004 promoted synthesis joins verified CHE10/CHE25, cost-barrier access, and CHIRPS ADM2 lag windows into the first household-climate analysis dataset while leaving SDG 3.8.2 and all modeling gates blocked.",
    )
    add_bundle(
        rows,
        "priority_bundle",
        "priority_lsms_isa_raw_package_receipt_checklist",
        "receipt_checklist_ready_no_original_files" if csv_value(priority_lsms_receipt_checklist_summary, "priority_lsms_receipt_checklist_package_received_rows", "0") == "0" and csv_value(priority_lsms_receipt_checklist_summary, "priority_lsms_receipt_checklist_dataset_rows", "0") != "0" else "receipt_checklist_needs_review",
        f"datasets={csv_value(priority_lsms_receipt_checklist_summary, 'priority_lsms_receipt_checklist_dataset_rows', '0')}; requirements={csv_value(priority_lsms_receipt_checklist_summary, 'priority_lsms_receipt_checklist_requirement_rows', '0')}; package_received={csv_value(priority_lsms_receipt_checklist_summary, 'priority_lsms_receipt_checklist_package_received_rows', '0')}; complete_package_received={csv_value(priority_lsms_receipt_checklist_summary, 'priority_lsms_receipt_checklist_complete_package_received_rows', '0')}; ready_review={csv_value(priority_lsms_receipt_checklist_summary, 'priority_lsms_receipt_checklist_ready_for_raw_value_review_rows', '0')}; blocked_no_original={csv_value(priority_lsms_receipt_checklist_summary, 'priority_lsms_receipt_checklist_blocked_no_original_package_rows', '0')}; blocked_requirements={csv_value(priority_lsms_receipt_checklist_summary, 'priority_lsms_receipt_checklist_blocked_requirement_rows', '0')}; handoffs={csv_value(priority_lsms_receipt_checklist_summary, 'priority_lsms_receipt_checklist_handoff_readmes_written', '0')}; data_write={csv_value(priority_lsms_receipt_checklist_summary, 'priority_lsms_receipt_checklist_data_write_status', 'missing')}; modeling_gate={csv_value(priority_lsms_receipt_checklist_summary, 'modeling_gate_status', 'missing')}",
        [TEMP_DIR / "priority_lsms_isa_raw_package_receipt_checklist.csv", TEMP_DIR / "priority_lsms_isa_raw_package_requirement_receipt_checklist.csv", RESULT_DIR / "priority_lsms_isa_raw_package_receipt_checklist_summary.csv", REPORT_DIR / "priority_lsms_isa_raw_package_receipt_checklist.md"],
        "Receipt checklist converts each refocused wave into a package-level and requirement-level intake control sheet: official package scope, target folder, fill fields, and post-receipt commands before raw-value review.",
    )
    add_bundle(
        rows,
        "priority_bundle",
        "priority_lsms_isa_credentialed_raw_acquisition_workbench",
        "ready_for_manual_credentialed_download" if csv_value(priority_lsms_credentialed_workbench_summary, "priority_lsms_credentialed_workbench_package_received_rows", "0") == "0" and csv_value(priority_lsms_credentialed_workbench_summary, "priority_lsms_credentialed_workbench_dataset_rows", "0") != "0" else "credentialed_workbench_needs_review",
        f"datasets={csv_value(priority_lsms_credentialed_workbench_summary, 'priority_lsms_credentialed_workbench_dataset_rows', '0')}; full_files={csv_value(priority_lsms_credentialed_workbench_summary, 'priority_lsms_credentialed_workbench_full_file_rows', '0')}; core_files={csv_value(priority_lsms_credentialed_workbench_summary, 'priority_lsms_credentialed_workbench_core_file_rows', '0')}; access_gate={csv_value(priority_lsms_credentialed_workbench_summary, 'priority_lsms_credentialed_workbench_access_gate_rows', '0')}; package_received={csv_value(priority_lsms_credentialed_workbench_summary, 'priority_lsms_credentialed_workbench_package_received_rows', '0')}; targets_missing={csv_value(priority_lsms_credentialed_workbench_summary, 'priority_lsms_credentialed_workbench_targets_missing_before_download', '0')}; handoffs={csv_value(priority_lsms_credentialed_workbench_summary, 'priority_lsms_credentialed_workbench_handoff_readmes_written', '0')}; data_write={csv_value(priority_lsms_credentialed_workbench_summary, 'priority_lsms_credentialed_workbench_data_write_status', 'missing')}; modeling_gate={csv_value(priority_lsms_credentialed_workbench_summary, 'modeling_gate_status', 'missing')}",
        [TEMP_DIR / "priority_lsms_isa_credentialed_raw_acquisition_workbench.csv", TEMP_DIR / "priority_lsms_isa_credentialed_raw_full_file_manifest.csv", TEMP_DIR / "priority_lsms_isa_credentialed_raw_core_file_checklist.csv", RESULT_DIR / "priority_lsms_isa_credentialed_raw_acquisition_workbench_summary.csv", REPORT_DIR / "priority_lsms_isa_credentialed_raw_acquisition_workbench.md"],
        "Credentialed raw acquisition workbench covers all 19 refocused waves with official get-microdata links, full DDI file manifests, core file confirmation rows, and post-download validation commands.",
    )
    add_bundle(
        rows,
        "priority_bundle",
        "priority_lsms_isa_official_file_receipt_validator",
        "blocked_no_original_package" if csv_value(priority_lsms_official_file_receipt_summary, "priority_lsms_official_file_receipt_original_or_member_rows", "0") == "0" and csv_value(priority_lsms_official_file_receipt_summary, "priority_lsms_official_file_receipt_dataset_rows", "0") != "0" else "official_file_receipt_needs_review",
        f"datasets={csv_value(priority_lsms_official_file_receipt_summary, 'priority_lsms_official_file_receipt_dataset_rows', '0')}; expected_files={csv_value(priority_lsms_official_file_receipt_summary, 'priority_lsms_official_file_receipt_expected_file_rows', '0')}; expected_matched={csv_value(priority_lsms_official_file_receipt_summary, 'priority_lsms_official_file_receipt_expected_file_matched_rows', '0')}; expected_missing={csv_value(priority_lsms_official_file_receipt_summary, 'priority_lsms_official_file_receipt_expected_file_missing_rows', '0')}; core_files={csv_value(priority_lsms_official_file_receipt_summary, 'priority_lsms_official_file_receipt_core_file_rows', '0')}; core_matched={csv_value(priority_lsms_official_file_receipt_summary, 'priority_lsms_official_file_receipt_core_file_matched_rows', '0')}; core_missing={csv_value(priority_lsms_official_file_receipt_summary, 'priority_lsms_official_file_receipt_core_file_missing_rows', '0')}; handoffs={csv_value(priority_lsms_official_file_receipt_summary, 'priority_lsms_official_file_receipt_handoff_readmes_written', '0')}; data_write={csv_value(priority_lsms_official_file_receipt_summary, 'priority_lsms_official_file_receipt_data_write_status', 'missing')}; modeling_gate={csv_value(priority_lsms_official_file_receipt_summary, 'modeling_gate_status', 'missing')}",
        [TEMP_DIR / "priority_lsms_isa_official_file_receipt_validation.csv", TEMP_DIR / "priority_lsms_isa_official_file_receipt_file_match.csv", TEMP_DIR / "priority_lsms_isa_official_file_receipt_core_match.csv", RESULT_DIR / "priority_lsms_isa_official_file_receipt_validator_summary.csv", REPORT_DIR / "priority_lsms_isa_official_file_receipt_validator.md"],
        "Official file receipt validator compares local direct files and readable archive members against official DDI file names before any schema, value, climate, or data-write gate can pass.",
    )
    add_bundle(
        rows,
        "priority_bundle",
        "priority_lsms_isa_threshold_download_sequence",
        "ready_for_manual_threshold_downloads" if csv_value(priority_lsms_threshold_sequence_summary, "priority_lsms_threshold_sequence_dataset_rows", "0") != "0" and csv_value(priority_lsms_threshold_sequence_summary, "priority_lsms_threshold_sequence_raw_package_received_rows", "0") == "0" else "threshold_sequence_needs_review",
        f"datasets={csv_value(priority_lsms_threshold_sequence_summary, 'priority_lsms_threshold_sequence_dataset_rows', '0')}; countries={csv_value(priority_lsms_threshold_sequence_summary, 'priority_lsms_threshold_sequence_country_rows', '0')}; minimum_downloads={csv_value(priority_lsms_threshold_sequence_summary, 'priority_lsms_threshold_sequence_minimum_download_rows', '0')}; minimum_countries={csv_value(priority_lsms_threshold_sequence_summary, 'priority_lsms_threshold_sequence_minimum_country_rows', '0')}; recommended_downloads={csv_value(priority_lsms_threshold_sequence_summary, 'priority_lsms_threshold_sequence_recommended_download_rows', '0')}; expected_files={csv_value(priority_lsms_threshold_sequence_summary, 'priority_lsms_threshold_sequence_expected_file_rows', '0')}; expected_matched={csv_value(priority_lsms_threshold_sequence_summary, 'priority_lsms_threshold_sequence_expected_file_matched_rows', '0')}; core_files={csv_value(priority_lsms_threshold_sequence_summary, 'priority_lsms_threshold_sequence_core_file_rows', '0')}; core_matched={csv_value(priority_lsms_threshold_sequence_summary, 'priority_lsms_threshold_sequence_core_file_matched_rows', '0')}; raw_received={csv_value(priority_lsms_threshold_sequence_summary, 'priority_lsms_threshold_sequence_raw_package_received_rows', '0')}; promoted={csv_value(priority_lsms_threshold_sequence_summary, 'priority_lsms_threshold_sequence_promoted_analysis_ready_rows', '0')}; modeling_gate={csv_value(priority_lsms_threshold_sequence_summary, 'modeling_gate_status', 'missing')}",
        [TEMP_DIR / "priority_lsms_isa_threshold_download_sequence.csv", TEMP_DIR / "priority_lsms_isa_threshold_minimum_batch.csv", TEMP_DIR / "priority_lsms_isa_threshold_country_coverage.csv", RESULT_DIR / "priority_lsms_isa_threshold_download_sequence_summary.csv", REPORT_DIR / "priority_lsms_isa_threshold_download_sequence.md"],
        "Threshold download sequence orders the 19-wave refocused queue into a minimum 11-download path, a recommended 13-download threshold batch, and six same-country backup waves while preserving no-data-write gates.",
    )
    add_bundle(
        rows,
        "priority_bundle",
        "priority_lsms_isa_minimum_batch_raw_intake_guide",
        "ready_for_minimum_batch_manual_intake" if csv_value(priority_lsms_minimum_intake_summary, "priority_lsms_minimum_batch_country_wave_rows", "0") == "11" and csv_value(priority_lsms_minimum_intake_summary, "priority_lsms_minimum_batch_matched_core_file_rows", "0") == "0" else "minimum_batch_intake_needs_review",
        f"waves={csv_value(priority_lsms_minimum_intake_summary, 'priority_lsms_minimum_batch_country_wave_rows', '0')}; countries={csv_value(priority_lsms_minimum_intake_summary, 'priority_lsms_minimum_batch_country_rows', '0')}; expected_full_files={csv_value(priority_lsms_minimum_intake_summary, 'priority_lsms_minimum_batch_expected_full_file_rows', '0')}; missing_full_files={csv_value(priority_lsms_minimum_intake_summary, 'priority_lsms_minimum_batch_missing_full_file_rows', '0')}; expected_core_files={csv_value(priority_lsms_minimum_intake_summary, 'priority_lsms_minimum_batch_expected_core_file_rows', '0')}; missing_core_files={csv_value(priority_lsms_minimum_intake_summary, 'priority_lsms_minimum_batch_missing_core_file_rows', '0')}; handoffs={csv_value(priority_lsms_minimum_intake_summary, 'priority_lsms_minimum_batch_handoff_readmes_written', '0')}; data_write={csv_value(priority_lsms_minimum_intake_summary, 'priority_lsms_minimum_batch_data_write_status', 'missing')}; modeling_gate={csv_value(priority_lsms_minimum_intake_summary, 'modeling_gate_status', 'missing')}",
        [TEMP_DIR / "priority_lsms_isa_minimum_batch_raw_intake_guide.csv", TEMP_DIR / "priority_lsms_isa_minimum_batch_expected_file_manifest.csv", TEMP_DIR / "priority_lsms_isa_minimum_batch_core_file_manifest.csv", RESULT_DIR / "priority_lsms_isa_minimum_batch_raw_intake_guide_summary.csv", REPORT_DIR / "priority_lsms_isa_minimum_batch_raw_intake_guide.md"],
        "Minimum-batch raw intake guide turns the 11-wave threshold batch into exact official-package placement folders, full expected file manifests, core file manifests, and per-wave post-download commands.",
    )
    add_bundle(
        rows,
        "priority_bundle",
        "priority_lsms_isa_minimum_batch_endpoint_refresh",
        "credentialed_download_required_no_public_raw_route" if csv_value(priority_lsms_minimum_endpoint_summary, "priority_lsms_minimum_endpoint_credentialed_download_required_rows", "0") == csv_value(priority_lsms_minimum_endpoint_summary, "priority_lsms_minimum_endpoint_dataset_rows", "-1") and csv_value(priority_lsms_minimum_endpoint_summary, "priority_lsms_minimum_endpoint_raw_download_candidate_rows", "1") == "0" else "endpoint_refresh_needs_review",
        f"waves={csv_value(priority_lsms_minimum_endpoint_summary, 'priority_lsms_minimum_endpoint_dataset_rows', '0')}; countries={csv_value(priority_lsms_minimum_endpoint_summary, 'priority_lsms_minimum_endpoint_country_rows', '0')}; endpoints={csv_value(priority_lsms_minimum_endpoint_summary, 'priority_lsms_minimum_endpoint_rows', '0')}; metadata_hits={csv_value(priority_lsms_minimum_endpoint_summary, 'priority_lsms_minimum_endpoint_public_metadata_endpoint_rows', '0')}; gate_waves={csv_value(priority_lsms_minimum_endpoint_summary, 'priority_lsms_minimum_endpoint_get_microdata_gate_dataset_rows', '0')}; raw_candidates={csv_value(priority_lsms_minimum_endpoint_summary, 'priority_lsms_minimum_endpoint_raw_download_candidate_rows', '0')}; credentialed_required={csv_value(priority_lsms_minimum_endpoint_summary, 'priority_lsms_minimum_endpoint_credentialed_download_required_rows', '0')}; handoffs={csv_value(priority_lsms_minimum_endpoint_summary, 'priority_lsms_minimum_endpoint_handoff_readmes_written', '0')}; data_write={csv_value(priority_lsms_minimum_endpoint_summary, 'priority_lsms_minimum_endpoint_data_write_status', 'missing')}; modeling_gate={csv_value(priority_lsms_minimum_endpoint_summary, 'modeling_gate_status', 'missing')}",
        [TEMP_DIR / "priority_lsms_isa_minimum_batch_endpoint_refresh.csv", TEMP_DIR / "priority_lsms_isa_minimum_batch_endpoint_dataset_status.csv", RESULT_DIR / "priority_lsms_isa_minimum_batch_endpoint_refresh_summary.csv", REPORT_DIR / "priority_lsms_isa_minimum_batch_endpoint_refresh.md"],
        "Minimum-batch endpoint refresh re-probes official World Bank metadata and get-microdata routes for the exact 11-wave threshold batch without downloading or accepting raw payloads.",
    )
    add_bundle(
        rows,
        "priority_bundle",
        "priority_lsms_isa_next_raw_package_action_packet",
        "minimum_batch_raw_package_actions_ready"
        if csv_value(priority_lsms_next_raw_package_summary, "minimum_batch_remaining_action_rows", "0") == "10"
        else "next_raw_package_action_packet_needs_review",
        f"actions={csv_value(priority_lsms_next_raw_package_summary, 'next_raw_package_action_rows', '0')}; minimum_remaining={csv_value(priority_lsms_next_raw_package_summary, 'minimum_batch_remaining_action_rows', '0')}; backups={csv_value(priority_lsms_next_raw_package_summary, 'backup_after_minimum_action_rows', '0')}; core_file_rows={csv_value(priority_lsms_next_raw_package_summary, 'core_file_action_rows', '0')}; current_promoted={csv_value(priority_lsms_next_raw_package_summary, 'current_promoted_analysis_ready_rows', '0')}; countries_if_minimum_passes={csv_value(priority_lsms_next_raw_package_summary, 'countries_if_minimum_batch_passes', '0')}; waves_if_minimum_passes={csv_value(priority_lsms_next_raw_package_summary, 'country_waves_if_minimum_batch_passes', '0')}; raw_endpoint_candidates={csv_value(priority_lsms_next_raw_package_summary, 'official_raw_download_candidate_rows', '0')}; credentialed_required={csv_value(priority_lsms_next_raw_package_summary, 'credentialed_download_required_rows', '0')}; data_write={csv_value(priority_lsms_next_raw_package_summary, 'data_write_gate_status', 'missing')}; modeling_gate={csv_value(priority_lsms_next_raw_package_summary, 'modeling_gate_status', 'missing')}",
        [TEMP_DIR / "priority_lsms_isa_next_raw_package_action_queue.csv", TEMP_DIR / "priority_lsms_isa_next_raw_package_core_files.csv", RESULT_DIR / "priority_lsms_isa_next_raw_package_action_summary.csv", REPORT_DIR / "priority_lsms_isa_next_raw_package_action_packet.md"],
        "Next raw package action packet converts the minimum-batch endpoint/access blocker into a file-level acquisition queue for the remaining 10 threshold waves plus backups.",
    )
    add_bundle(
        rows,
        "priority_bundle",
        "priority_lsms_isa_incoming_raw_package_router",
        "incoming_router_ready"
        if csv_value(priority_lsms_incoming_router_summary, "priority_lsms_incoming_router_action_country_wave_rows", "0") == "18"
        and csv_value(priority_lsms_incoming_router_summary, "priority_lsms_incoming_router_data_write_status", "missing") == "blocked_no_data_write"
        else "incoming_router_needs_review",
        f"incoming_folder={csv_value(priority_lsms_incoming_router_summary, 'priority_lsms_incoming_router_incoming_folder_exists', '0')}; action_waves={csv_value(priority_lsms_incoming_router_summary, 'priority_lsms_incoming_router_action_country_wave_rows', '0')}; incoming_files={csv_value(priority_lsms_incoming_router_summary, 'priority_lsms_incoming_router_incoming_file_rows', '0')}; candidates={csv_value(priority_lsms_incoming_router_summary, 'priority_lsms_incoming_router_candidate_rows', '0')}; copy_candidates={csv_value(priority_lsms_incoming_router_summary, 'priority_lsms_incoming_router_copy_candidate_rows', '0')}; manual_review={csv_value(priority_lsms_incoming_router_summary, 'priority_lsms_incoming_router_manual_review_rows', '0')}; data_write={csv_value(priority_lsms_incoming_router_summary, 'priority_lsms_incoming_router_data_write_status', 'missing')}; modeling_gate={csv_value(priority_lsms_incoming_router_summary, 'modeling_gate_status', 'missing')}",
        [TEMP_DIR / "priority_lsms_isa_incoming_raw_package_route_plan.csv", TEMP_DIR / "priority_lsms_isa_incoming_raw_package_route_candidates.csv", RESULT_DIR / "priority_lsms_isa_incoming_raw_package_router_summary.csv", REPORT_DIR / "priority_lsms_isa_incoming_raw_package_router.md"],
        "Incoming raw package router lets downloaded official packages be dropped into temp/raw_downloads/_incoming and scored against expected IDNO/file manifests before manual copying.",
    )
    add_bundle(
        rows,
        "priority_bundle",
        "priority_lsms_isa_threshold_gap_control_panel",
        "threshold_gap_control_panel_current"
        if csv_value(priority_lsms_threshold_gap_summary, "minimum_threshold_batch_remaining_download_rows", "0") == "10"
        and csv_value(priority_lsms_threshold_gap_summary, "data_write_gate_status", "missing") == "blocked_no_new_data_write"
        else "threshold_gap_control_panel_needs_review",
        f"current_promoted={csv_value(priority_lsms_threshold_gap_summary, 'current_promoted_analysis_ready_rows', '0')}; current_countries={csv_value(priority_lsms_threshold_gap_summary, 'current_promoted_country_rows', '0')}; country_gap={csv_value(priority_lsms_threshold_gap_summary, 'current_country_gap_to_threshold', '0')}; wave_gap={csv_value(priority_lsms_threshold_gap_summary, 'current_country_wave_gap_to_threshold', '0')}; minimum_remaining_downloads={csv_value(priority_lsms_threshold_gap_summary, 'minimum_threshold_batch_remaining_download_rows', '0')}; countries_if_minimum_passes={csv_value(priority_lsms_threshold_gap_summary, 'countries_if_minimum_remaining_passes', '0')}; waves_if_minimum_passes={csv_value(priority_lsms_threshold_gap_summary, 'country_waves_if_minimum_remaining_passes', '0')}; country_buffer={csv_value(priority_lsms_threshold_gap_summary, 'country_buffer_if_minimum_remaining_passes', '0')}; wave_buffer={csv_value(priority_lsms_threshold_gap_summary, 'country_wave_buffer_if_minimum_remaining_passes', '0')}; missing_core_files={csv_value(priority_lsms_threshold_gap_summary, 'minimum_batch_missing_core_file_rows', '0')}; modeling_gate={csv_value(priority_lsms_threshold_gap_summary, 'modeling_gate_status', 'missing')}",
        [TEMP_DIR / "priority_lsms_isa_threshold_gap_download_panel.csv", RESULT_DIR / "priority_lsms_isa_threshold_gap_country_panel.csv", RESULT_DIR / "priority_lsms_isa_threshold_gap_control_panel_summary.csv", REPORT_DIR / "priority_lsms_isa_threshold_gap_control_panel.md"],
        "Threshold gap control panel states the exact remaining minimum-batch raw downloads and the current country/wave buffer before any model can be rerun.",
    )
    add_bundle(
        rows,
        "priority_bundle",
        "priority_lsms_isa_manual_download_packets",
        "manual_download_packets_current"
        if csv_value(priority_lsms_manual_download_packet_summary, "manual_download_packet_rows", "0") == "10"
        and csv_value(priority_lsms_manual_download_packet_summary, "data_write_gate_status", "missing") == "blocked_no_data_write"
        else "manual_download_packets_need_review",
        f"packets={csv_value(priority_lsms_manual_download_packet_summary, 'manual_download_packet_rows', '0')}; priority_country_packets={csv_value(priority_lsms_manual_download_packet_summary, 'manual_download_packet_priority_country_rows', '0')}; sixth_country_packets={csv_value(priority_lsms_manual_download_packet_summary, 'manual_download_packet_sixth_country_rows', '0')}; missing_full_files={csv_value(priority_lsms_manual_download_packet_summary, 'manual_download_packet_missing_full_file_rows', '0')}; core_file_rows={csv_value(priority_lsms_manual_download_packet_summary, 'manual_download_packet_core_file_rows', '0')}; missing_core_files={csv_value(priority_lsms_manual_download_packet_summary, 'manual_download_packet_missing_core_file_rows', '0')}; reports={csv_value(priority_lsms_manual_download_packet_summary, 'manual_download_packet_reports_written', '0')}; modeling_gate={csv_value(priority_lsms_manual_download_packet_summary, 'modeling_gate_status', 'missing')}",
        [TEMP_DIR / "priority_lsms_isa_manual_download_packet_index.csv", TEMP_DIR / "priority_lsms_isa_manual_download_packet_core_files.csv", RESULT_DIR / "priority_lsms_isa_manual_download_packet_summary.csv", REPORT_DIR / "priority_lsms_isa_manual_download_packets.md"],
        "Manual download packets turn each remaining minimum-batch raw package into a per-wave official link, local target folder, core-file checklist, and post-download validation command.",
    )
    add_bundle(
        rows,
        "priority_bundle",
        "priority_lsms_isa_manual_download_progress_tracker",
        "manual_download_progress_current"
        if csv_value(priority_lsms_manual_download_progress_summary, "manual_download_progress_packet_rows", "0") == "10"
        and csv_value(priority_lsms_manual_download_progress_summary, "data_write_gate_status", "missing") == "blocked_no_data_write"
        else "manual_download_progress_needs_review",
        f"packets={csv_value(priority_lsms_manual_download_progress_summary, 'manual_download_progress_packet_rows', '0')}; target_files={csv_value(priority_lsms_manual_download_progress_summary, 'manual_download_progress_target_file_rows', '0')}; incoming_routes={csv_value(priority_lsms_manual_download_progress_summary, 'manual_download_progress_incoming_route_rows', '0')}; validation_ready={csv_value(priority_lsms_manual_download_progress_summary, 'manual_download_progress_validation_ready_packets', '0')}; blocked_no_files={csv_value(priority_lsms_manual_download_progress_summary, 'manual_download_progress_blocked_no_file_packets', '0')}; modeling_gate={csv_value(priority_lsms_manual_download_progress_summary, 'modeling_gate_status', 'missing')}",
        [TEMP_DIR / "priority_lsms_isa_manual_download_progress_tracker.csv", RESULT_DIR / "priority_lsms_isa_manual_download_progress_summary.csv", REPORT_DIR / "priority_lsms_isa_manual_download_progress_tracker.md"],
        "Manual download progress tracker links each packet to local target-folder and incoming-route status so newly placed files can move into validation without guessing.",
    )
    add_bundle(
        rows,
        "priority_bundle",
        "priority_lsms_isa_post_download_validation_runner",
        "post_download_validation_dry_run_current"
        if csv_value(priority_lsms_post_download_validation_summary, "post_download_validation_runner_mode", "missing") == "dry_run"
        and csv_value(priority_lsms_post_download_validation_summary, "data_write_gate_status", "missing") == "blocked_no_data_write"
        else "post_download_validation_runner_needs_review",
        f"mode={csv_value(priority_lsms_post_download_validation_summary, 'post_download_validation_runner_mode', 'missing')}; ready_packets={csv_value(priority_lsms_post_download_validation_summary, 'post_download_validation_ready_packet_rows', '0')}; plan_rows={csv_value(priority_lsms_post_download_validation_summary, 'post_download_validation_plan_rows', '0')}; execute_commands={csv_value(priority_lsms_post_download_validation_summary, 'post_download_validation_execute_command_rows', '0')}; attempted={csv_value(priority_lsms_post_download_validation_summary, 'post_download_validation_attempted_command_rows', '0')}; failed={csv_value(priority_lsms_post_download_validation_summary, 'post_download_validation_failed_command_rows', '0')}; modeling_gate={csv_value(priority_lsms_post_download_validation_summary, 'modeling_gate_status', 'missing')}",
        [TEMP_DIR / "priority_lsms_isa_post_download_validation_run_plan.csv", TEMP_DIR / "priority_lsms_isa_post_download_validation_command_log.csv", RESULT_DIR / "priority_lsms_isa_post_download_validation_runner_summary.csv", REPORT_DIR / "priority_lsms_isa_post_download_validation_runner.md"],
        "Post-download validation runner builds a dry-run plan, and can explicitly execute allowlisted receipt/schema/value/semantics checks once packet target folders contain official raw files.",
    )
    add_bundle(
        rows,
        "priority_bundle",
        "priority_lsms_isa_manual_download_execution_board",
        "manual_download_execution_board_current"
        if csv_value(priority_lsms_manual_download_execution_board_summary, "manual_download_execution_board_rows", "0") == "10"
        and csv_value(priority_lsms_manual_download_execution_board_summary, "data_write_gate_status", "missing") == "blocked_no_data_write"
        else "manual_download_execution_board_needs_review",
        f"rows={csv_value(priority_lsms_manual_download_execution_board_summary, 'manual_download_execution_board_rows', '0')}; priority_country_rows={csv_value(priority_lsms_manual_download_execution_board_summary, 'manual_download_execution_board_priority_country_rows', '0')}; sixth_country_rows={csv_value(priority_lsms_manual_download_execution_board_summary, 'manual_download_execution_board_sixth_country_rows', '0')}; target_files={csv_value(priority_lsms_manual_download_execution_board_summary, 'manual_download_execution_board_target_file_rows', '0')}; incoming_routes={csv_value(priority_lsms_manual_download_execution_board_summary, 'manual_download_execution_board_incoming_route_rows', '0')}; validation_ready={csv_value(priority_lsms_manual_download_execution_board_summary, 'manual_download_execution_board_validation_ready_rows', '0')}; missing_full_files={csv_value(priority_lsms_manual_download_execution_board_summary, 'manual_download_execution_board_missing_full_file_rows', '0')}; missing_core_files={csv_value(priority_lsms_manual_download_execution_board_summary, 'manual_download_execution_board_missing_core_file_rows', '0')}; countries_if_passes={csv_value(priority_lsms_manual_download_execution_board_summary, 'countries_if_board_passes', '0')}; waves_if_passes={csv_value(priority_lsms_manual_download_execution_board_summary, 'country_waves_if_board_passes', '0')}; modeling_gate={csv_value(priority_lsms_manual_download_execution_board_summary, 'modeling_gate_status', 'missing')}",
        [TEMP_DIR / "priority_lsms_isa_manual_download_execution_board.csv", RESULT_DIR / "priority_lsms_isa_manual_download_execution_board_summary.csv", REPORT_DIR / "priority_lsms_isa_manual_download_execution_board.md"],
        "Manual download execution board gives one table of official URLs, target folders, missing-file counts, core-file previews, and post-download validation commands for the 10 remaining threshold packets.",
    )
    add_bundle(
        rows,
        "priority_bundle",
        "priority_lsms_isa_credentialed_download_handoff",
        "credentialed_download_handoff_waiting_for_session"
        if csv_value(priority_lsms_credentialed_download_handoff_summary, "credentialed_download_handoff_rows", "0") == "10"
        and csv_value(priority_lsms_credentialed_download_handoff_summary, "credentialed_download_handoff_mode", "missing") == "dry_run"
        and csv_value(priority_lsms_credentialed_download_handoff_summary, "credentialed_download_handoff_saved_raw_file_rows", "0") == "0"
        and csv_value(priority_lsms_credentialed_download_handoff_summary, "data_write_gate_status", "missing") == "blocked_no_data_write"
        else "credentialed_download_handoff_needs_review",
        f"mode={csv_value(priority_lsms_credentialed_download_handoff_summary, 'credentialed_download_handoff_mode', 'missing')}; rows={csv_value(priority_lsms_credentialed_download_handoff_summary, 'credentialed_download_handoff_rows', '0')}; cookie_file={csv_value(priority_lsms_credentialed_download_handoff_summary, 'credentialed_download_handoff_cookie_file_present', '0')}; header_file={csv_value(priority_lsms_credentialed_download_handoff_summary, 'credentialed_download_handoff_header_file_present', '0')}; attempted={csv_value(priority_lsms_credentialed_download_handoff_summary, 'credentialed_download_handoff_request_attempted_rows', '0')}; raw_payload={csv_value(priority_lsms_credentialed_download_handoff_summary, 'credentialed_download_handoff_raw_payload_detected_rows', '0')}; saved={csv_value(priority_lsms_credentialed_download_handoff_summary, 'credentialed_download_handoff_saved_raw_file_rows', '0')}; missing_session={csv_value(priority_lsms_credentialed_download_handoff_summary, 'credentialed_download_handoff_missing_session_rows', '0')}; modeling_gate={csv_value(priority_lsms_credentialed_download_handoff_summary, 'modeling_gate_status', 'missing')}",
        [TEMP_DIR / "priority_lsms_isa_credentialed_download_handoff_plan.csv", TEMP_DIR / "priority_lsms_isa_credentialed_download_handoff_log.csv", RESULT_DIR / "priority_lsms_isa_credentialed_download_handoff_summary.csv", REPORT_DIR / "priority_lsms_isa_credentialed_download_handoff.md"],
        "Credentialed download handoff can use local-only World Bank cookies or headers to probe and explicitly execute official get-microdata downloads after login and terms acceptance.",
    )
    add_bundle(
        rows,
        "priority_bundle",
        "priority_lsms_isa_resource_download_route_probe",
        "resource_download_routes_no_public_raw_payload"
        if csv_value(priority_lsms_resource_download_route_probe_summary, "resource_download_route_probe_datasets", "0") == "10"
        and csv_value(priority_lsms_resource_download_route_probe_summary, "resource_download_route_probe_raw_payload_candidate_rows", "1") == "0"
        and csv_value(priority_lsms_resource_download_route_probe_summary, "data_write_gate_status", "missing") == "blocked_no_data_write"
        else "resource_download_route_probe_needs_review",
        f"datasets={csv_value(priority_lsms_resource_download_route_probe_summary, 'resource_download_route_probe_datasets', '0')}; sampled_files={csv_value(priority_lsms_resource_download_route_probe_summary, 'resource_download_route_probe_sampled_files', '0')}; route_rows={csv_value(priority_lsms_resource_download_route_probe_summary, 'resource_download_route_probe_route_rows', '0')}; raw_payload={csv_value(priority_lsms_resource_download_route_probe_summary, 'resource_download_route_probe_raw_payload_candidate_rows', '0')}; access_gate={csv_value(priority_lsms_resource_download_route_probe_summary, 'resource_download_route_probe_access_gate_rows', '0')}; data_dictionary_html={csv_value(priority_lsms_resource_download_route_probe_summary, 'resource_download_route_probe_data_dictionary_html_rows', '0')}; http_error={csv_value(priority_lsms_resource_download_route_probe_summary, 'resource_download_route_probe_http_error_rows', '0')}; request_failed={csv_value(priority_lsms_resource_download_route_probe_summary, 'resource_download_route_probe_request_failed_rows', '0')}; modeling_gate={csv_value(priority_lsms_resource_download_route_probe_summary, 'modeling_gate_status', 'missing')}",
        [TEMP_DIR / "priority_lsms_isa_resource_download_route_probe.csv", RESULT_DIR / "priority_lsms_isa_resource_download_route_probe_summary.csv", REPORT_DIR / "priority_lsms_isa_resource_download_route_probe.md"],
        "Resource download route probe checks common World Bank file-id/data-dictionary routes for the 10 manual packets without cookies, raw saves, or data writes.",
    )
    add_bundle(
        rows,
        "priority_bundle",
        "priority_lsms_isa_download_acceptance_matrix",
        "download_acceptance_matrix_current"
        if csv_value(priority_lsms_download_acceptance_summary, "download_acceptance_dataset_rows", "0") == "10"
        and csv_value(priority_lsms_download_acceptance_summary, "download_acceptance_missing_expected_file_rows", "0") == csv_value(priority_lsms_manual_download_execution_board_summary, "manual_download_execution_board_missing_full_file_rows", "-1")
        and csv_value(priority_lsms_download_acceptance_summary, "data_write_gate_status", "missing") == "blocked_no_data_write"
        else "download_acceptance_matrix_needs_review",
        f"datasets={csv_value(priority_lsms_download_acceptance_summary, 'download_acceptance_dataset_rows', '0')}; expected_files={csv_value(priority_lsms_download_acceptance_summary, 'download_acceptance_expected_file_rows', '0')}; core_files={csv_value(priority_lsms_download_acceptance_summary, 'download_acceptance_core_file_rows', '0')}; missing_files={csv_value(priority_lsms_download_acceptance_summary, 'download_acceptance_missing_expected_file_rows', '0')}; present_files={csv_value(priority_lsms_download_acceptance_summary, 'download_acceptance_present_file_rows', '0')}; blocked_requirements={csv_value(priority_lsms_download_acceptance_summary, 'download_acceptance_missing_core_requirement_rows', '0')}; ready_requirements={csv_value(priority_lsms_download_acceptance_summary, 'download_acceptance_ready_requirement_rows', '0')}; raw_route_candidates={csv_value(priority_lsms_download_acceptance_summary, 'download_acceptance_resource_route_raw_payload_rows', '0')}; modeling_gate={csv_value(priority_lsms_download_acceptance_summary, 'modeling_gate_status', 'missing')}",
        [TEMP_DIR / "priority_lsms_isa_download_acceptance_file_matrix.csv", TEMP_DIR / "priority_lsms_isa_download_acceptance_requirement_matrix.csv", RESULT_DIR / "priority_lsms_isa_download_acceptance_matrix_summary.csv", REPORT_DIR / "priority_lsms_isa_download_acceptance_matrix.md"],
        "Download acceptance matrix turns the 10 manual packets into expected-file and requirement-level receipt gates before raw value review or data promotion.",
    )
    add_bundle(
        rows,
        "priority_bundle",
        "priority_lsms_isa_local_target_readmes",
        "local_target_readmes_current"
        if csv_value(priority_lsms_local_target_readme_summary, "local_target_readme_rows", "0") == "10"
        and csv_value(priority_lsms_local_target_readme_summary, "local_target_readme_missing_expected_file_rows", "0") == csv_value(priority_lsms_download_acceptance_summary, "download_acceptance_missing_expected_file_rows", "-1")
        and csv_value(priority_lsms_local_target_readme_summary, "data_write_gate_status", "missing") == "blocked_no_data_write"
        else "local_target_readmes_need_review",
        f"readmes={csv_value(priority_lsms_local_target_readme_summary, 'local_target_readme_rows', '0')}; expected_files={csv_value(priority_lsms_local_target_readme_summary, 'local_target_readme_expected_file_rows', '0')}; missing_files={csv_value(priority_lsms_local_target_readme_summary, 'local_target_readme_missing_expected_file_rows', '0')}; requirements={csv_value(priority_lsms_local_target_readme_summary, 'local_target_readme_requirement_rows', '0')}; blocked_requirements={csv_value(priority_lsms_local_target_readme_summary, 'local_target_readme_blocked_requirement_rows', '0')}; ready_requirements={csv_value(priority_lsms_local_target_readme_summary, 'local_target_readme_ready_requirement_rows', '0')}; modeling_gate={csv_value(priority_lsms_local_target_readme_summary, 'modeling_gate_status', 'missing')}",
        [TEMP_DIR / "priority_lsms_isa_local_target_readme_manifest.csv", RESULT_DIR / "priority_lsms_isa_local_target_readme_summary.csv", REPORT_DIR / "priority_lsms_isa_local_target_readmes.md"],
        "Local target readmes put the download acceptance checklist directly into each ignored temp/raw_downloads/<IDNO>/ target folder and expose a GitHub-readable manifest.",
    )
    add_bundle(
        rows,
        "priority_bundle",
        "priority_lsms_isa_minimum_batch_raw_value_queue",
        "minimum_batch_raw_value_queue_current"
        if csv_value(priority_lsms_minimum_batch_raw_value_queue_summary, "minimum_batch_raw_value_queue_dataset_rows", "0") == "10"
        and csv_value(priority_lsms_minimum_batch_raw_value_queue_summary, "minimum_batch_raw_value_queue_requirement_rows", "0") == "80"
        and csv_value(priority_lsms_minimum_batch_raw_value_queue_summary, "data_write_gate_status", "missing") == "blocked_no_data_write"
        else "minimum_batch_raw_value_queue_needs_review",
        f"datasets={csv_value(priority_lsms_minimum_batch_raw_value_queue_summary, 'minimum_batch_raw_value_queue_dataset_rows', '0')}; requirements={csv_value(priority_lsms_minimum_batch_raw_value_queue_summary, 'minimum_batch_raw_value_queue_requirement_rows', '0')}; variables={csv_value(priority_lsms_minimum_batch_raw_value_queue_summary, 'minimum_batch_raw_value_queue_variable_rows', '0')}; files={csv_value(priority_lsms_minimum_batch_raw_value_queue_summary, 'minimum_batch_raw_value_queue_file_rows', '0')}; blocked_requirements={csv_value(priority_lsms_minimum_batch_raw_value_queue_summary, 'minimum_batch_raw_value_queue_blocked_requirement_rows', '0')}; ready_requirements={csv_value(priority_lsms_minimum_batch_raw_value_queue_summary, 'minimum_batch_raw_value_queue_ready_requirement_rows', '0')}; target_readmes={csv_value(priority_lsms_minimum_batch_raw_value_queue_summary, 'minimum_batch_raw_value_queue_local_target_readmes', '0')}; modeling_gate={csv_value(priority_lsms_minimum_batch_raw_value_queue_summary, 'modeling_gate_status', 'missing')}",
        [TEMP_DIR / "priority_lsms_isa_minimum_batch_raw_value_requirement_queue.csv", TEMP_DIR / "priority_lsms_isa_minimum_batch_raw_value_variable_queue.csv", TEMP_DIR / "priority_lsms_isa_minimum_batch_raw_value_file_queue.csv", RESULT_DIR / "priority_lsms_isa_minimum_batch_raw_value_queue_summary.csv", REPORT_DIR / "priority_lsms_isa_minimum_batch_raw_value_queue.md"],
        "Minimum-batch raw-value queue narrows the full 19-wave workbook to the 10 manual-download packets so receipt can move straight into requirement, file, and variable review.",
    )
    add_bundle(
        rows,
        "priority_bundle",
        "priority_lsms_isa_target_folder_receipt_smoke_test",
        "target_folder_receipt_smoke_current"
        if csv_value(priority_lsms_target_folder_smoke_summary, "priority_lsms_target_smoke_dataset_rows", "0") == "10"
        and csv_value(priority_lsms_target_folder_smoke_summary, "priority_lsms_target_smoke_data_write_status", "missing") == "blocked_no_data_write"
        else "target_folder_receipt_smoke_needs_review",
        f"datasets={csv_value(priority_lsms_target_folder_smoke_summary, 'priority_lsms_target_smoke_dataset_rows', '0')}; target_folders_present={csv_value(priority_lsms_target_folder_smoke_summary, 'priority_lsms_target_smoke_target_folders_present', '0')}; files={csv_value(priority_lsms_target_folder_smoke_summary, 'priority_lsms_target_smoke_file_inventory_rows', '0')}; placeholders={csv_value(priority_lsms_target_folder_smoke_summary, 'priority_lsms_target_smoke_placeholder_instruction_rows', '0')}; candidate_raw_files={csv_value(priority_lsms_target_folder_smoke_summary, 'priority_lsms_target_smoke_candidate_raw_file_rows', '0')}; candidate_docs={csv_value(priority_lsms_target_folder_smoke_summary, 'priority_lsms_target_smoke_candidate_documentation_file_rows', '0')}; ready_for_receipt={csv_value(priority_lsms_target_folder_smoke_summary, 'priority_lsms_target_smoke_ready_for_receipt_validation_rows', '0')}; blocked_no_candidate_raw={csv_value(priority_lsms_target_folder_smoke_summary, 'priority_lsms_target_smoke_blocked_no_candidate_raw_rows', '0')}; manual_review={csv_value(priority_lsms_target_folder_smoke_summary, 'priority_lsms_target_smoke_manual_review_rows', '0')}; modeling_gate={csv_value(priority_lsms_target_folder_smoke_summary, 'modeling_gate_status', 'missing')}",
        [TEMP_DIR / "priority_lsms_isa_target_folder_receipt_status.csv", TEMP_DIR / "priority_lsms_isa_target_folder_receipt_file_inventory.csv", RESULT_DIR / "priority_lsms_isa_target_folder_receipt_smoke_test_summary.csv", REPORT_DIR / "priority_lsms_isa_target_folder_receipt_smoke_test.md"],
        "Target-folder receipt smoke test separates generated instructions from real candidate raw packages in the 10 minimum-batch folders before receipt/schema/value validation.",
    )
    add_bundle(
        rows,
        "priority_bundle",
        "priority_lsms_isa_threshold_replacement_plan",
        "threshold_replacement_plan_current"
        if csv_value(priority_lsms_threshold_replacement_summary, "priority_lsms_replacement_scenario_rows", "0") == "10"
        and csv_value(priority_lsms_threshold_replacement_summary, "priority_lsms_replacement_data_write_status", "missing") == "blocked_no_data_write"
        else "threshold_replacement_plan_needs_review",
        f"backup_candidates={csv_value(priority_lsms_threshold_replacement_summary, 'priority_lsms_replacement_backup_candidate_rows', '0')}; scenarios={csv_value(priority_lsms_threshold_replacement_summary, 'priority_lsms_replacement_scenario_rows', '0')}; strategies={csv_value(priority_lsms_threshold_replacement_summary, 'priority_lsms_replacement_strategy_rows', '0')}; required_replacements={csv_value(priority_lsms_threshold_replacement_summary, 'priority_lsms_replacement_required_for_threshold_rows', '0')}; optional_buffers={csv_value(priority_lsms_threshold_replacement_summary, 'priority_lsms_replacement_optional_buffer_rows', '0')}; strict_priority_countries={csv_value(priority_lsms_threshold_replacement_summary, 'priority_lsms_replacement_strict_priority_countries', '0')}; strict_priority_waves={csv_value(priority_lsms_threshold_replacement_summary, 'priority_lsms_replacement_strict_priority_waves', '0')}; current_minimum_countries={csv_value(priority_lsms_threshold_replacement_summary, 'priority_lsms_replacement_current_minimum_countries', '0')}; current_minimum_waves={csv_value(priority_lsms_threshold_replacement_summary, 'priority_lsms_replacement_current_minimum_waves', '0')}; modeling_gate={csv_value(priority_lsms_threshold_replacement_summary, 'modeling_gate_status', 'missing')}",
        [TEMP_DIR / "priority_lsms_isa_threshold_replacement_candidate_rank.csv", TEMP_DIR / "priority_lsms_isa_threshold_replacement_scenarios.csv", TEMP_DIR / "priority_lsms_isa_threshold_replacement_strategy.csv", RESULT_DIR / "priority_lsms_isa_threshold_replacement_plan_summary.csv", REPORT_DIR / "priority_lsms_isa_threshold_replacement_plan.md"],
        "Threshold replacement plan explains why Nepal is currently used as the sixth-country candidate and which backup wave should replace each single minimum-batch failure.",
    )
    add_bundle(
        rows,
        "priority_bundle",
        "priority_lsms_isa_minimum_batch_climate_linkage_review_queue",
        "minimum_batch_climate_linkage_review_current"
        if csv_value(priority_lsms_minimum_climate_review_summary, "priority_lsms_minimum_climate_review_dataset_rows", "0") == "10"
        and csv_value(priority_lsms_minimum_climate_review_summary, "priority_lsms_minimum_climate_review_data_write_status", "missing") == "blocked_no_data_write"
        else "minimum_batch_climate_linkage_review_needs_review",
        f"datasets={csv_value(priority_lsms_minimum_climate_review_summary, 'priority_lsms_minimum_climate_review_dataset_rows', '0')}; file_rows={csv_value(priority_lsms_minimum_climate_review_summary, 'priority_lsms_minimum_climate_review_file_rows', '0')}; timing_metadata_ready={csv_value(priority_lsms_minimum_climate_review_summary, 'priority_lsms_minimum_climate_review_timing_ready_metadata_rows', '0')}; geography_metadata_ready={csv_value(priority_lsms_minimum_climate_review_summary, 'priority_lsms_minimum_climate_review_geography_ready_metadata_rows', '0')}; point_routes={csv_value(priority_lsms_minimum_climate_review_summary, 'priority_lsms_minimum_climate_review_point_route_rows', '0')}; admin_routes={csv_value(priority_lsms_minimum_climate_review_summary, 'priority_lsms_minimum_climate_review_admin_route_rows', '0')}; raw_blocked={csv_value(priority_lsms_minimum_climate_review_summary, 'priority_lsms_minimum_climate_review_raw_blocked_rows', '0')}; source_ready={csv_value(priority_lsms_minimum_climate_review_summary, 'priority_lsms_minimum_climate_review_source_ready_rows', '0')}; accepted_routes={csv_value(priority_lsms_minimum_climate_review_summary, 'priority_lsms_minimum_climate_review_accepted_route_rows', '0')}; modeling_gate={csv_value(priority_lsms_minimum_climate_review_summary, 'modeling_gate_status', 'missing')}",
        [TEMP_DIR / "priority_lsms_isa_minimum_batch_climate_linkage_review_queue.csv", TEMP_DIR / "priority_lsms_isa_minimum_batch_climate_linkage_file_queue.csv", RESULT_DIR / "priority_lsms_isa_minimum_batch_climate_linkage_review_summary.csv", REPORT_DIR / "priority_lsms_isa_minimum_batch_climate_linkage_review_queue.md"],
        "Minimum-batch climate linkage review queue maps the current 10 manual packets to timing/geography raw checks and CHIRPS/ERA5 route status before any climate extraction.",
    )
    add_bundle(
        rows,
        "priority_bundle",
        "priority_lsms_isa_local_stray_raw_package_locator",
        "local_stray_raw_locator_current"
        if csv_value(priority_lsms_local_stray_locator_summary, "priority_lsms_local_stray_raw_locator_dataset_rows", "0") == "10"
        and csv_value(priority_lsms_local_stray_locator_summary, "priority_lsms_local_stray_raw_locator_data_write_status", "missing") == "blocked_no_data_write"
        else "local_stray_raw_locator_needs_review",
        f"datasets={csv_value(priority_lsms_local_stray_locator_summary, 'priority_lsms_local_stray_raw_locator_dataset_rows', '0')}; scanned_files={csv_value(priority_lsms_local_stray_locator_summary, 'priority_lsms_local_stray_raw_locator_scanned_file_rows', '0')}; considered_files={csv_value(priority_lsms_local_stray_locator_summary, 'priority_lsms_local_stray_raw_locator_considered_file_rows', '0')}; candidates={csv_value(priority_lsms_local_stray_locator_summary, 'priority_lsms_local_stray_raw_locator_candidate_file_rows', '0')}; matched_idnos={csv_value(priority_lsms_local_stray_locator_summary, 'priority_lsms_local_stray_raw_locator_matched_idno_rows', '0')}; outside_target={csv_value(priority_lsms_local_stray_locator_summary, 'priority_lsms_local_stray_raw_locator_outside_target_candidate_rows', '0')}; incoming={csv_value(priority_lsms_local_stray_locator_summary, 'priority_lsms_local_stray_raw_locator_incoming_candidate_rows', '0')}; already_target={csv_value(priority_lsms_local_stray_locator_summary, 'priority_lsms_local_stray_raw_locator_already_target_candidate_rows', '0')}; raw_status={csv_value(priority_lsms_local_stray_locator_summary, 'priority_lsms_local_stray_raw_locator_raw_promotion_status', 'missing')}; modeling_gate={csv_value(priority_lsms_local_stray_locator_summary, 'modeling_gate_status', 'missing')}",
        [TEMP_DIR / "priority_lsms_isa_local_stray_raw_package_candidates.csv", TEMP_DIR / "priority_lsms_isa_local_stray_raw_package_route_plan.csv", RESULT_DIR / "priority_lsms_isa_local_stray_raw_package_locator_summary.csv", REPORT_DIR / "priority_lsms_isa_local_stray_raw_package_locator.md"],
        "Local stray raw package locator searches only file names, sizes, and archive member lists to find already-downloaded packages that may have been placed outside their expected target folders.",
    )
    add_bundle(
        rows,
        "priority_bundle",
        "priority_lsms_isa_promotion_gate_dashboard",
        "promotion_gate_dashboard_current"
        if csv_value(priority_lsms_promotion_gate_summary, "priority_lsms_promotion_gate_promoted_rows", "0") == "1"
        and csv_value(priority_lsms_promotion_gate_summary, "priority_lsms_promotion_gate_blocked_raw_package_rows", "0") == "18"
        else "promotion_gate_dashboard_needs_review",
        f"country_waves={csv_value(priority_lsms_promotion_gate_summary, 'priority_lsms_promotion_gate_country_wave_rows', '0')}; requirement_rows={csv_value(priority_lsms_promotion_gate_summary, 'priority_lsms_promotion_gate_requirement_rows', '0')}; promoted={csv_value(priority_lsms_promotion_gate_summary, 'priority_lsms_promotion_gate_promoted_rows', '0')}; blocked_raw_package={csv_value(priority_lsms_promotion_gate_summary, 'priority_lsms_promotion_gate_blocked_raw_package_rows', '0')}; ready_for_packet={csv_value(priority_lsms_promotion_gate_summary, 'priority_lsms_promotion_gate_ready_for_packet_rows', '0')}; minimum_remaining={csv_value(priority_lsms_promotion_gate_summary, 'priority_lsms_promotion_gate_minimum_remaining_rows', '0')}; backups={csv_value(priority_lsms_promotion_gate_summary, 'priority_lsms_promotion_gate_backup_rows', '0')}; data_write={csv_value(priority_lsms_promotion_gate_summary, 'data_write_gate_status', 'missing')}; modeling_gate={csv_value(priority_lsms_promotion_gate_summary, 'modeling_gate_status', 'missing')}",
        [TEMP_DIR / "priority_lsms_isa_promotion_gate_dashboard.csv", TEMP_DIR / "priority_lsms_isa_promotion_gate_requirement_dashboard.csv", RESULT_DIR / "priority_lsms_isa_promotion_gate_dashboard_summary.csv", REPORT_DIR / "priority_lsms_isa_promotion_gate_dashboard.md"],
        "Promotion gate dashboard combines registry, raw receipt, schema, value-profile, and semantics evidence into one fail-closed country-wave and requirement view.",
    )
    add_bundle(
        rows,
        "priority_bundle",
        "priority_lsms_isa_minimum_batch_promotion_unlock_board",
        "minimum_batch_unlock_board_current_all_raw_files_absent"
        if csv_value(priority_lsms_unlock_summary, "minimum_batch_unlock_board_rows", "0") == "10"
        and csv_value(priority_lsms_unlock_summary, "minimum_batch_unlock_public_documentation_complete_rows", "0") == "10"
        and csv_value(priority_lsms_unlock_summary, "minimum_batch_unlock_validation_ready_rows", "1") == "0"
        else "minimum_batch_unlock_board_needs_review",
        f"rows={csv_value(priority_lsms_unlock_summary, 'minimum_batch_unlock_board_rows', '0')}; public_docs_complete={csv_value(priority_lsms_unlock_summary, 'minimum_batch_unlock_public_documentation_complete_rows', '0')}; validation_ready={csv_value(priority_lsms_unlock_summary, 'minimum_batch_unlock_validation_ready_rows', '0')}; blocked_no_files={csv_value(priority_lsms_unlock_summary, 'minimum_batch_unlock_blocked_no_local_or_incoming_files', '0')}; missing_expected_files={csv_value(priority_lsms_unlock_summary, 'minimum_batch_unlock_missing_expected_file_rows', '0')}; missing_core_requirements={csv_value(priority_lsms_unlock_summary, 'minimum_batch_unlock_missing_core_requirement_rows', '0')}; projected_countries={csv_value(priority_lsms_unlock_summary, 'projected_country_rows_if_all_minimum_batch_promoted', '0')}; projected_waves={csv_value(priority_lsms_unlock_summary, 'projected_country_wave_rows_if_all_minimum_batch_promoted', '0')}; modeling_gate={csv_value(priority_lsms_unlock_summary, 'modeling_gate_status', 'missing')}",
        [RESULT_DIR / "priority_lsms_isa_minimum_batch_promotion_unlock_board.csv", RESULT_DIR / "priority_lsms_isa_minimum_batch_promotion_unlock_summary.csv", REPORT_DIR / "priority_lsms_isa_minimum_batch_promotion_unlock_board.md"],
        "Minimum-batch promotion unlock board condenses the 10 package URLs, target folders, public-documentation receipt, local raw-file gap, and projected 6-country/11-wave threshold contribution into one fail-closed execution matrix.",
    )
    add_bundle(
        rows,
        "priority_bundle",
        "priority_lsms_isa_worldbank_session_bootstrap",
        "worldbank_session_bootstrap_current_missing_session_material"
        if csv_value(priority_lsms_worldbank_session_summary, "worldbank_session_bootstrap_rows", "0") == "10"
        and csv_value(priority_lsms_worldbank_session_summary, "worldbank_session_bootstrap_ready_for_probe_rows", "1") == "0"
        else "worldbank_session_bootstrap_needs_review",
        f"rows={csv_value(priority_lsms_worldbank_session_summary, 'worldbank_session_bootstrap_rows', '0')}; cookie_present={csv_value(priority_lsms_worldbank_session_summary, 'worldbank_session_cookie_file_present', '0')}; cookie_status={csv_value(priority_lsms_worldbank_session_summary, 'worldbank_session_cookie_format_status', 'missing')}; header_present={csv_value(priority_lsms_worldbank_session_summary, 'worldbank_session_header_file_present', '0')}; header_status={csv_value(priority_lsms_worldbank_session_summary, 'worldbank_session_header_format_status', 'missing')}; ready_for_probe={csv_value(priority_lsms_worldbank_session_summary, 'worldbank_session_bootstrap_ready_for_probe_rows', '0')}; missing_session={csv_value(priority_lsms_worldbank_session_summary, 'worldbank_session_bootstrap_missing_session_rows', '0')}; modeling_gate={csv_value(priority_lsms_worldbank_session_summary, 'modeling_gate_status', 'missing')}",
        [RESULT_DIR / "priority_lsms_isa_worldbank_session_bootstrap.csv", RESULT_DIR / "priority_lsms_isa_worldbank_session_bootstrap_summary.csv", REPORT_DIR / "priority_lsms_isa_worldbank_session_bootstrap.md"],
        "World Bank session bootstrap records only redacted local session-file readiness for credentialed /download probing; no cookie or header values are exported.",
    )
    add_bundle(
        rows,
        "priority_bundle",
        "priority_lsms_isa_credentialed_fetch_command_packet",
        "credentialed_fetch_command_packet_current_missing_session_material"
        if csv_value(priority_lsms_fetch_command_summary, "credentialed_fetch_command_packet_rows", "0") == "10"
        and csv_value(priority_lsms_fetch_command_summary, "credentialed_fetch_command_packet_ready_to_probe_rows", "1") == "0"
        else "credentialed_fetch_command_packet_needs_review",
        f"rows={csv_value(priority_lsms_fetch_command_summary, 'credentialed_fetch_command_packet_rows', '0')}; countries={csv_value(priority_lsms_fetch_command_summary, 'credentialed_fetch_command_packet_countries', '0')}; country_list={csv_value(priority_lsms_fetch_command_summary, 'credentialed_fetch_command_packet_country_list', '')}; expected_core_files={csv_value(priority_lsms_fetch_command_summary, 'credentialed_fetch_command_packet_expected_core_file_rows', '0')}; target_files={csv_value(priority_lsms_fetch_command_summary, 'credentialed_fetch_command_packet_target_file_count', '0')}; ready_for_probe={csv_value(priority_lsms_fetch_command_summary, 'credentialed_fetch_command_packet_ready_to_probe_rows', '0')}; missing_session={csv_value(priority_lsms_fetch_command_summary, 'credentialed_fetch_command_packet_missing_session_rows', '0')}; modeling_gate={csv_value(priority_lsms_fetch_command_summary, 'modeling_gate_status', 'missing')}",
        [RESULT_DIR / "priority_lsms_isa_credentialed_fetch_command_packet.csv", RESULT_DIR / "priority_lsms_isa_credentialed_fetch_command_packet_summary.csv", REPORT_DIR / "priority_lsms_isa_credentialed_fetch_command_packet.md"],
        "Credentialed fetch command packet converts the minimum-batch /download URLs into per-wave command rows, target payload paths, and post-download validation chains without exporting credentials or raw data.",
    )
    add_bundle(
        rows,
        "priority_bundle",
        "priority_lsms_isa_browser_download_starter",
        "browser_download_starter_ready_for_manual_terms_acceptance"
        if csv_value(priority_lsms_browser_starter_summary, "browser_download_starter_rows", "0") == "10"
        and csv_value(priority_lsms_browser_starter_summary, "browser_download_starter_ready_rows", "0") == "10"
        else "browser_download_starter_needs_review",
        f"rows={csv_value(priority_lsms_browser_starter_summary, 'browser_download_starter_rows', '0')}; ready_rows={csv_value(priority_lsms_browser_starter_summary, 'browser_download_starter_ready_rows', '0')}; priority_countries={csv_value(priority_lsms_browser_starter_summary, 'browser_download_starter_priority_country_rows', '0')}; sixth_country={csv_value(priority_lsms_browser_starter_summary, 'browser_download_starter_sixth_country_rows', '0')}; expected_core_files={csv_value(priority_lsms_browser_starter_summary, 'browser_download_starter_expected_core_file_rows', '0')}; target_files={csv_value(priority_lsms_browser_starter_summary, 'browser_download_starter_target_file_count', '0')}; first_canary={csv_value(priority_lsms_browser_starter_summary, 'browser_download_starter_first_canary_idno', '')}; local_ps1={csv_value(priority_lsms_browser_starter_summary, 'browser_download_starter_local_ps1_path', '')}; modeling_gate={csv_value(priority_lsms_browser_starter_summary, 'modeling_gate_status', 'missing')}",
        [RESULT_DIR / "priority_lsms_isa_browser_download_starter.csv", RESULT_DIR / "priority_lsms_isa_browser_download_starter_summary.csv", REPORT_DIR / "priority_lsms_isa_browser_download_starter.md"],
        "Browser download starter gives a first-canary workflow, browser/open-folder commands, and per-IDNO probe commands for manual World Bank terms acceptance and raw package placement.",
    )
    add_bundle(
        rows,
        "priority_bundle",
        "priority_lsms_isa_first_canary_runbook",
        "first_canary_download_runbook_current_raw_missing"
        if csv_value(priority_lsms_first_canary_summary, "first_canary_idno", "") != ""
        and csv_value(priority_lsms_first_canary_summary, "first_canary_target_file_count", "1") == "0"
        else "first_canary_download_runbook_needs_review",
        f"idno={csv_value(priority_lsms_first_canary_summary, 'first_canary_idno', '')}; country={csv_value(priority_lsms_first_canary_summary, 'first_canary_country', '')}; wave={csv_value(priority_lsms_first_canary_summary, 'first_canary_wave', '')}; official_files={csv_value(priority_lsms_first_canary_summary, 'first_canary_expected_official_file_rows', '0')}; unique_core_files={csv_value(priority_lsms_first_canary_summary, 'first_canary_expected_unique_core_file_rows', '0')}; requirement_core_file_rows={csv_value(priority_lsms_first_canary_summary, 'first_canary_requirement_core_file_rows', '0')}; requirement_gates={csv_value(priority_lsms_first_canary_summary, 'first_canary_requirement_gate_rows', '0')}; target_files={csv_value(priority_lsms_first_canary_summary, 'first_canary_target_file_count', '0')}; progress={csv_value(priority_lsms_first_canary_summary, 'first_canary_progress_status', '')}; modeling_gate={csv_value(priority_lsms_first_canary_summary, 'modeling_gate_status', 'missing')}",
        [RESULT_DIR / "priority_lsms_isa_first_canary_download_runbook.csv", RESULT_DIR / "priority_lsms_isa_first_canary_core_file_checklist.csv", RESULT_DIR / "priority_lsms_isa_first_canary_requirement_gate_checklist.csv", RESULT_DIR / "priority_lsms_isa_first_canary_runbook_summary.csv", REPORT_DIR / "priority_lsms_isa_first_canary_runbook.md"],
        "First canary runbook condenses the Ethiopia 2021-2022 get-microdata URL, target folder, unique core files, requirement gates, and post-download validation commands into one execution artifact.",
    )
    add_bundle(
        rows,
        "priority_bundle",
        "priority_lsms_isa_local_raw_presence_audit",
        "local_raw_presence_current_only_mwi2004_registry_raw"
        if csv_value(priority_lsms_raw_presence_summary, "local_raw_presence_registry_raw_present_rows", "0") == "1"
        and csv_value(priority_lsms_raw_presence_summary, "local_raw_presence_minimum_batch_raw_absent_rows", "0") == "10"
        else "local_raw_presence_needs_review",
        f"registry_rows={csv_value(priority_lsms_raw_presence_summary, 'local_raw_presence_registry_rows', '0')}; registry_raw_present={csv_value(priority_lsms_raw_presence_summary, 'local_raw_presence_registry_raw_present_rows', '0')}; registry_raw_absent={csv_value(priority_lsms_raw_presence_summary, 'local_raw_presence_registry_raw_absent_rows', '0')}; minimum_batch_raw_absent={csv_value(priority_lsms_raw_presence_summary, 'local_raw_presence_minimum_batch_raw_absent_rows', '0')}; nonregistry_raw_files={csv_value(priority_lsms_raw_presence_summary, 'local_raw_presence_nonregistry_raw_file_rows', '0')}; diagnostic_albania_raw_files={csv_value(priority_lsms_raw_presence_summary, 'local_raw_presence_diagnostic_albania_raw_file_rows', '0')}; modeling_gate={csv_value(priority_lsms_raw_presence_summary, 'modeling_gate_status', 'missing')}",
        [RESULT_DIR / "priority_lsms_isa_local_raw_presence_audit.csv", RESULT_DIR / "priority_lsms_isa_local_nonregistry_raw_files.csv", RESULT_DIR / "priority_lsms_isa_local_raw_presence_summary.csv", REPORT_DIR / "priority_lsms_isa_local_raw_presence_audit.md"],
        "Local raw presence audit checks every promoted-registry row for raw-like files and keeps Albania raw files diagnostic-only outside the main promotion registry.",
    )
    add_bundle(
        rows,
        "priority_bundle",
        "priority_lsms_isa_acquisition_to_promotion_handoff",
        "acquisition_to_promotion_handoff_current_raw_acquisition_blocked"
        if csv_value(priority_lsms_handoff_summary, "acquisition_to_promotion_acquire_raw_rows", "0") == "18"
        and csv_value(priority_lsms_handoff_summary, "acquisition_to_promotion_minimum_batch_acquire_rows", "0") == "10"
        and csv_value(priority_lsms_handoff_summary, "modeling_gate_status", "missing") == "blocked"
        else "acquisition_to_promotion_handoff_needs_review",
        f"handoff_rows={csv_value(priority_lsms_handoff_summary, 'acquisition_to_promotion_handoff_rows', '0')}; gate_rows={csv_value(priority_lsms_handoff_summary, 'acquisition_to_promotion_gate_rows', '0')}; minimum_acquire={csv_value(priority_lsms_handoff_summary, 'acquisition_to_promotion_minimum_batch_acquire_rows', '0')}; promoted_current={csv_value(priority_lsms_handoff_summary, 'acquisition_to_promotion_promoted_keep_current_rows', '0')}; raw_validation_ready={csv_value(priority_lsms_handoff_summary, 'acquisition_to_promotion_raw_validation_ready_rows', '0')}; acquire_raw={csv_value(priority_lsms_handoff_summary, 'acquisition_to_promotion_acquire_raw_rows', '0')}; modeling_gate={csv_value(priority_lsms_handoff_summary, 'modeling_gate_status', 'missing')}",
        [RESULT_DIR / "priority_lsms_isa_acquisition_to_promotion_handoff.csv", RESULT_DIR / "priority_lsms_isa_acquisition_to_promotion_gate_checklist.csv", RESULT_DIR / "priority_lsms_isa_acquisition_to_promotion_handoff_summary.csv", REPORT_DIR / "priority_lsms_isa_acquisition_to_promotion_handoff.md"],
        "Acquisition-to-promotion handoff maps all registry waves to the next raw acquisition, receipt/schema/value, climate-linkage, promotion-packet, and registry-refresh gates without opening modeling.",
    )
    add_bundle(
        rows,
        "priority_bundle",
        "priority_lsms_isa_dataset_scope_lock",
        "dataset_scope_locked_6_countries_11_waves_10_downloads_required"
        if csv_value(priority_lsms_scope_lock_summary, "dataset_scope_lock_rows", "0") == "11"
        and csv_value(priority_lsms_scope_lock_summary, "dataset_scope_lock_country_rows", "0") == "6"
        and csv_value(priority_lsms_scope_lock_summary, "dataset_scope_lock_download_required_rows", "0") == "10"
        and csv_value(priority_lsms_scope_lock_summary, "modeling_gate_status", "missing") == "blocked"
        else "dataset_scope_lock_needs_review",
        f"scope_rows={csv_value(priority_lsms_scope_lock_summary, 'dataset_scope_lock_rows', '0')}; countries={csv_value(priority_lsms_scope_lock_summary, 'dataset_scope_lock_country_rows', '0')}; priority_waves={csv_value(priority_lsms_scope_lock_summary, 'dataset_scope_lock_priority_country_wave_rows', '0')}; nonpriority_waves={csv_value(priority_lsms_scope_lock_summary, 'dataset_scope_lock_nonpriority_country_wave_rows', '0')}; download_required={csv_value(priority_lsms_scope_lock_summary, 'dataset_scope_lock_download_required_rows', '0')}; promoted_anchor={csv_value(priority_lsms_scope_lock_summary, 'dataset_scope_lock_promoted_anchor_rows', '0')}; raw_missing_download={csv_value(priority_lsms_scope_lock_summary, 'dataset_scope_lock_raw_missing_download_required_rows', '0')}; period={csv_value(priority_lsms_scope_lock_summary, 'dataset_scope_lock_wave_period_min', '')}..{csv_value(priority_lsms_scope_lock_summary, 'dataset_scope_lock_wave_period_max', '')}; modeling_gate={csv_value(priority_lsms_scope_lock_summary, 'modeling_gate_status', 'missing')}",
        [RESULT_DIR / "priority_lsms_isa_dataset_scope_lock.csv", RESULT_DIR / "priority_lsms_isa_dataset_scope_lock_gate_matrix.csv", RESULT_DIR / "priority_lsms_isa_dataset_scope_lock_summary.csv", REPORT_DIR / "priority_lsms_isa_dataset_scope_lock.md"],
        "Dataset scope lock fixes the 6-country 11-wave target and separates the one implemented Malawi anchor from the 10 official raw packages still required.",
    )
    add_bundle(
        rows,
        "priority_bundle",
        "priority_lsms_isa_acquisition_route_decision",
        "all_download_required_waves_need_browser_manual_terms_acceptance"
        if csv_value(priority_lsms_acquisition_route_summary, "acquisition_route_decision_rows", "0") == "10"
        and csv_value(priority_lsms_acquisition_route_summary, "acquisition_route_decision_browser_manual_required_rows", "0") == "10"
        and csv_value(priority_lsms_acquisition_route_summary, "modeling_gate_status", "missing") == "blocked"
        else "acquisition_route_decision_needs_review",
        f"route_rows={csv_value(priority_lsms_acquisition_route_summary, 'acquisition_route_decision_rows', '0')}; countries={csv_value(priority_lsms_acquisition_route_summary, 'acquisition_route_decision_country_rows', '0')}; local_files={csv_value(priority_lsms_acquisition_route_summary, 'acquisition_route_decision_local_files_present_rows', '0')}; public_raw_candidates={csv_value(priority_lsms_acquisition_route_summary, 'acquisition_route_decision_public_raw_candidate_rows', '0')}; credentialed_probe_ready={csv_value(priority_lsms_acquisition_route_summary, 'acquisition_route_decision_credentialed_probe_ready_rows', '0')}; browser_manual_required={csv_value(priority_lsms_acquisition_route_summary, 'acquisition_route_decision_browser_manual_required_rows', '0')}; access_gate_rows={csv_value(priority_lsms_acquisition_route_summary, 'acquisition_route_decision_access_gate_rows', '0')}; expected_core_files={csv_value(priority_lsms_acquisition_route_summary, 'acquisition_route_decision_expected_core_file_rows', '0')}; modeling_gate={csv_value(priority_lsms_acquisition_route_summary, 'modeling_gate_status', 'missing')}",
        [RESULT_DIR / "priority_lsms_isa_acquisition_route_decision.csv", RESULT_DIR / "priority_lsms_isa_acquisition_route_evidence.csv", RESULT_DIR / "priority_lsms_isa_acquisition_route_decision_summary.csv", REPORT_DIR / "priority_lsms_isa_acquisition_route_decision.md"],
        "Acquisition route decision consolidates public route probes, access-gate evidence, session readiness, browser/manual commands, local raw counts, and post-download validation commands for the 10 download-required waves.",
    )
    add_bundle(
        rows,
        "priority_bundle",
        "priority_lsms_isa_scoped_incoming_package_router",
        "waiting_for_incoming_packages"
        if csv_value(priority_lsms_scoped_incoming_summary, "scoped_incoming_router_target_rows", "0") == "10"
        and csv_value(priority_lsms_scoped_incoming_summary, "scoped_incoming_router_pending_drop_rows", "0") == "10"
        and csv_value(priority_lsms_scoped_incoming_summary, "modeling_gate_status", "missing") == "blocked"
        else "scoped_incoming_router_needs_review",
        f"targets={csv_value(priority_lsms_scoped_incoming_summary, 'scoped_incoming_router_target_rows', '0')}; countries={csv_value(priority_lsms_scoped_incoming_summary, 'scoped_incoming_router_country_rows', '0')}; incoming_files={csv_value(priority_lsms_scoped_incoming_summary, 'scoped_incoming_router_incoming_file_rows', '0')}; evidence_rows={csv_value(priority_lsms_scoped_incoming_summary, 'scoped_incoming_router_candidate_evidence_rows', '0')}; expected_core_files={csv_value(priority_lsms_scoped_incoming_summary, 'scoped_incoming_router_expected_core_file_rows', '0')}; copy_candidates={csv_value(priority_lsms_scoped_incoming_summary, 'scoped_incoming_router_copy_candidate_rows', '0')}; pending_drop={csv_value(priority_lsms_scoped_incoming_summary, 'scoped_incoming_router_pending_drop_rows', '0')}; manual_review={csv_value(priority_lsms_scoped_incoming_summary, 'scoped_incoming_router_manual_review_rows', '0')}; modeling_gate={csv_value(priority_lsms_scoped_incoming_summary, 'modeling_gate_status', 'missing')}",
        [RESULT_DIR / "priority_lsms_isa_scoped_incoming_package_router.csv", RESULT_DIR / "priority_lsms_isa_scoped_incoming_package_router_evidence.csv", RESULT_DIR / "priority_lsms_isa_scoped_incoming_package_router_summary.csv", REPORT_DIR / "priority_lsms_isa_scoped_incoming_package_router.md"],
        "Scoped incoming package router maps files dropped into temp/raw_downloads/_incoming to the 10 locked download-required waves, without moving raw files or opening data writes.",
    )
    add_bundle(
        rows,
        "priority_bundle",
        "priority_lsms_isa_webgpt_download_control_manifest",
        "browser_manual_terms_acceptance_required"
        if csv_value(priority_lsms_webgpt_download_summary, "webgpt_download_control_rows", "0") == "10"
        and csv_value(priority_lsms_webgpt_download_summary, "webgpt_download_control_expected_core_file_rows", "0") == "323"
        and csv_value(priority_lsms_webgpt_download_summary, "modeling_gate_status", "missing") == "blocked"
        else "webgpt_download_control_needs_review",
        f"rows={csv_value(priority_lsms_webgpt_download_summary, 'webgpt_download_control_rows', '0')}; countries={csv_value(priority_lsms_webgpt_download_summary, 'webgpt_download_control_country_rows', '0')}; priority_rows={csv_value(priority_lsms_webgpt_download_summary, 'webgpt_download_control_priority_country_rows', '0')}; sixth_country_rows={csv_value(priority_lsms_webgpt_download_summary, 'webgpt_download_control_sixth_country_rows', '0')}; expected_full_files={csv_value(priority_lsms_webgpt_download_summary, 'webgpt_download_control_expected_full_file_rows', '0')}; expected_core_files={csv_value(priority_lsms_webgpt_download_summary, 'webgpt_download_control_expected_core_file_rows', '0')}; target_files={csv_value(priority_lsms_webgpt_download_summary, 'webgpt_download_control_target_file_rows', '0')}; incoming_files={csv_value(priority_lsms_webgpt_download_summary, 'webgpt_download_control_incoming_file_rows', '0')}; browser_manual={csv_value(priority_lsms_webgpt_download_summary, 'webgpt_download_control_browser_manual_rows', '0')}; modeling_gate={csv_value(priority_lsms_webgpt_download_summary, 'modeling_gate_status', 'missing')}",
        [RESULT_DIR / "priority_lsms_isa_webgpt_download_control_manifest.csv", RESULT_DIR / "priority_lsms_isa_webgpt_expected_core_file_manifest.csv", RESULT_DIR / "priority_lsms_isa_webgpt_download_control_summary.csv", REPORT_DIR / "priority_lsms_isa_webgpt_download_control_manifest.md"],
        "Web GPT download control manifest consolidates official URLs, local target folders, command packets, incoming status, and expected core-file checks for the 10 download-required waves.",
    )
    add_bundle(
        rows,
        "priority_bundle",
        "priority_analysis_dataset_synthesis_blueprint",
        "blocked_required_schema_columns_not_verified" if csv_value(priority_synthesis_summary, "priority_synthesis_blueprint_join_ready_rows", "0") == "0" else "synthesis_join_candidates_ready",
        f"schema_rows={csv_value(priority_synthesis_summary, 'priority_synthesis_blueprint_schema_rows', '0')}; required_rows={csv_value(priority_synthesis_summary, 'priority_synthesis_blueprint_required_rows', '0')}; ready_required={csv_value(priority_synthesis_summary, 'priority_synthesis_blueprint_ready_required_rows', '0')}; blocked_required={csv_value(priority_synthesis_summary, 'priority_synthesis_blueprint_blocked_required_rows', '0')}; join_rows={csv_value(priority_synthesis_summary, 'priority_synthesis_blueprint_join_plan_rows', '0')}; join_ready={csv_value(priority_synthesis_summary, 'priority_synthesis_blueprint_join_ready_rows', '0')}; candidate_variables={csv_value(priority_synthesis_summary, 'priority_synthesis_blueprint_candidate_variable_rows', '0')}; manual_verified_variables={csv_value(priority_synthesis_summary, 'priority_synthesis_blueprint_manual_verified_variable_rows', '0')}",
        [TEMP_DIR / "priority_analysis_dataset_synthesis_blueprint.csv", TEMP_DIR / "priority_analysis_dataset_join_plan.csv", RESULT_DIR / "priority_analysis_dataset_synthesis_blueprint_summary.csv", REPORT_DIR / "priority_analysis_dataset_synthesis_blueprint.md"],
        "Synthesis blueprint defines the target promoted household-climate schema, source concepts, candidate variables, required joins, and fail-closed blockers before any data/ write.",
    )
    add_bundle(
        rows,
        "priority_bundle",
        "priority_country_wave_promotion_packets",
        "blocked_fail_closed" if csv_value(priority_packet_summary, "priority_country_wave_packet_analysis_ready_rows", "0") == "0" else "packet_candidates_ready_for_data_write",
        f"packets={csv_value(priority_packet_summary, 'priority_country_wave_packet_rows', '0')}; gates={csv_value(priority_packet_summary, 'priority_country_wave_packet_gate_rows', '0')}; passed_gates={csv_value(priority_packet_summary, 'priority_country_wave_packet_passed_gate_rows', '0')}; failed_gates={csv_value(priority_packet_summary, 'priority_country_wave_packet_failed_gate_rows', '0')}; public_docs_ready={csv_value(priority_packet_summary, 'priority_country_wave_packet_public_documentation_ready_rows', '0')}; metadata_ready={csv_value(priority_packet_summary, 'priority_country_wave_packet_official_metadata_ready_rows', '0')}; endpoint_matrix_ready={csv_value(priority_packet_summary, 'priority_country_wave_packet_endpoint_matrix_ready_rows', '0')}; credentialed_acquisition_ready={csv_value(priority_packet_summary, 'priority_country_wave_packet_credentialed_acquisition_ready_rows', '0')}; raw_package_ready={csv_value(priority_packet_summary, 'priority_country_wave_packet_raw_package_ready_rows', '0')}; financial_ready={csv_value(priority_packet_summary, 'priority_country_wave_packet_financial_ready_rows', '0')}; access_ready={csv_value(priority_packet_summary, 'priority_country_wave_packet_access_ready_rows', '0')}; climate_ready={csv_value(priority_packet_summary, 'priority_country_wave_packet_climate_ready_rows', '0')}; analysis_ready={csv_value(priority_packet_summary, 'priority_country_wave_packet_analysis_ready_rows', '0')}",
        [TEMP_DIR / "priority_country_wave_promotion_packet_index.csv", TEMP_DIR / "priority_country_wave_promotion_packet_gate_matrix.csv", TEMP_DIR / "priority_country_wave_promotion_packet_action_queue.csv", RESULT_DIR / "priority_country_wave_promotion_packet_summary.csv", REPORT_DIR / "priority_country_wave_promotion_packets.md"],
        "Priority packets consolidate public documentation, raw receipt, manual verification, climate preflight, synthesis join, and registry write gates for each target wave.",
    )
    add_bundle(
        rows,
        "priority_bundle",
        "priority_lsms_isa_country_wave_promotion_packets",
        "blocked_fail_closed" if csv_value(priority_lsms_packet_summary, "priority_lsms_country_wave_packet_analysis_ready_rows", "0") == "0" else "packet_candidates_ready_for_data_write",
        f"packets={csv_value(priority_lsms_packet_summary, 'priority_lsms_country_wave_packet_rows', '0')}; gates={csv_value(priority_lsms_packet_summary, 'priority_lsms_country_wave_packet_gate_rows', '0')}; passed_gates={csv_value(priority_lsms_packet_summary, 'priority_lsms_country_wave_packet_passed_gate_rows', '0')}; failed_gates={csv_value(priority_lsms_packet_summary, 'priority_lsms_country_wave_packet_failed_gate_rows', '0')}; public_docs_ready={csv_value(priority_lsms_packet_summary, 'priority_lsms_country_wave_packet_public_documentation_ready_rows', '0')}; variable_evidence_ready={csv_value(priority_lsms_packet_summary, 'priority_lsms_country_wave_packet_variable_evidence_ready_rows', '0')}; raw_package_ready={csv_value(priority_lsms_packet_summary, 'priority_lsms_country_wave_packet_raw_package_ready_rows', '0')}; raw_value_verified={csv_value(priority_lsms_packet_summary, 'priority_lsms_country_wave_packet_raw_value_verified_rows', '0')}; financial_ready={csv_value(priority_lsms_packet_summary, 'priority_lsms_country_wave_packet_financial_ready_rows', '0')}; access_ready={csv_value(priority_lsms_packet_summary, 'priority_lsms_country_wave_packet_access_ready_rows', '0')}; climate_ready={csv_value(priority_lsms_packet_summary, 'priority_lsms_country_wave_packet_climate_ready_rows', '0')}; analysis_ready={csv_value(priority_lsms_packet_summary, 'priority_lsms_country_wave_packet_analysis_ready_rows', '0')}",
        [TEMP_DIR / "priority_lsms_isa_country_wave_promotion_packet_index.csv", TEMP_DIR / "priority_lsms_isa_country_wave_promotion_packet_gate_matrix.csv", TEMP_DIR / "priority_lsms_isa_country_wave_promotion_packet_action_queue.csv", RESULT_DIR / "priority_lsms_isa_country_wave_promotion_packet_summary.csv", REPORT_DIR / "priority_lsms_isa_country_wave_promotion_packets.md"],
        "Refocused 19-wave LSMS/ISA packets consolidate public documentation, variable evidence, raw intake, archive preflight, raw-value requirements, climate linkage, synthesis, and registry write gates for each target wave.",
    )
    add_bundle(
        rows,
        "priority_bundle",
        "promoted_data_gate",
        csv_value(promoted_data_gate_summary, "promoted_data_gate_status", "missing"),
        f"promoted_rows={csv_value(promoted_data_gate_summary, 'registry_promoted_analysis_ready_rows', '0')}; data_before={csv_value(promoted_data_gate_summary, 'data_dataset_files_before_gate', '0')}; data_after={csv_value(promoted_data_gate_summary, 'data_dataset_files_after_gate', '0')}; quarantined={csv_value(promoted_data_gate_summary, 'quarantined_diagnostic_data_files', '0')}",
        [RESULT_DIR / "promoted_data_gate_summary.csv", TEMP_DIR / "promoted_data_gate_manifest.csv", REPORT_DIR / "promoted_data_gate.md", DATA_DIR / "README.md"],
        "Promoted data gate keeps data/ reserved for registry-approved datasets and moves pre-promotion diagnostic CSVs to temp/diagnostic_data_quarantine/current/.",
    )
    add_bundle(
        rows,
        "raw_access_gate",
        "public_external_raw_candidate_downloads",
        "raw_archives_available_requires_value_verification" if int_value(csv_value(public_external_summary, "public_external_downloaded_or_existing_rows", "0")) > 0 else "missing",
        f"candidate_rows={csv_value(public_external_summary, 'public_external_candidate_rows', '0')}; downloaded_or_existing={csv_value(public_external_summary, 'public_external_downloaded_or_existing_rows', '0')}; datasets={csv_value(public_external_summary, 'public_external_dataset_rows', '0')}; bytes={csv_value(public_external_summary, 'public_external_downloaded_bytes', '0')}",
        [TEMP_DIR / "public_external_raw_candidate_downloads.csv", RESULT_DIR / "public_external_raw_candidate_download_summary.csv", REPORT_DIR / "public_external_raw_candidate_downloads.md"],
        "Direct public external raw archives downloaded from screened candidate links; archive/schema evidence still requires downstream raw value and harmonization audits.",
    )
    add_bundle(
        rows,
        "raw_access_gate",
        "first_batch_manual_download_handoff",
        "manual_raw_download_required",
        f"handoff_rows={csv_value(first_batch_handoff_summary, 'first_batch_handoff_rows', '0')}; file_queue_rows={csv_value(first_batch_handoff_summary, 'first_batch_file_queue_rows', '0')}; raw_file_rows={csv_value(first_batch_handoff_summary, 'first_batch_raw_file_inventory_rows', '0')}; raw_variable_rows={csv_value(first_batch_handoff_summary, 'first_batch_raw_variable_catalog_rows', '0')}",
        [TEMP_DIR / "first_batch_manual_download_handoff.csv", TEMP_DIR / "first_batch_manual_download_file_queue.csv", RESULT_DIR / "first_batch_manual_download_handoff_summary.csv", REPORT_DIR / "first_batch_manual_download_handoff.md"],
        "Per-dataset manual handoff tying official access-gate evidence to target folders, expected raw modules, and post-download verification commands.",
    )
    add_bundle(
        rows,
        "raw_access_gate",
        "first_batch_public_documentation_audit",
        "metadata_only_requires_raw_verification",
        f"dataset_rows={csv_value(first_batch_documentation_summary, 'first_batch_documentation_dataset_rows', '0')}; resource_rows={csv_value(first_batch_documentation_summary, 'first_batch_documentation_resource_rows', '0')}; saved_rows={csv_value(first_batch_documentation_summary, 'first_batch_documentation_saved_rows', '0')}; complete_datasets={csv_value(first_batch_documentation_summary, 'first_batch_documentation_complete_dataset_rows', '0')}; failed_rows={csv_value(first_batch_documentation_summary, 'first_batch_documentation_failed_rows', '0')}",
        [TEMP_DIR / "first_batch_public_documentation_audit.csv", RESULT_DIR / "first_batch_public_documentation_summary.csv", REPORT_DIR / "first_batch_public_documentation_audit.md"],
        "First-batch coverage audit for public catalog documentation, metadata exports, data dictionaries, PDFs, and related-material pages; still not raw microdata.",
    )
    add_bundle(
        rows,
        "raw_access_gate",
        "first_batch_file_source_traceability",
        "metadata_only_requires_raw_verification",
        f"trace_rows={csv_value(first_batch_file_source_summary, 'first_batch_file_source_traceability_rows', '0')}; datasets={csv_value(first_batch_file_source_summary, 'first_batch_file_source_traceability_dataset_rows', '0')}; unsupported={csv_value(first_batch_file_source_summary, 'first_batch_file_source_traceability_unsupported_rows', '0')}; examples_found={csv_value(first_batch_file_source_summary, 'first_batch_candidate_variable_examples_found', '0')}",
        [TEMP_DIR / "first_batch_file_source_traceability.csv", RESULT_DIR / "first_batch_file_source_traceability_summary.csv", REPORT_DIR / "first_batch_file_source_traceability.md"],
        "File-level trace from first-batch manual queue to public schema and variable metadata; confirms queue support but not raw-file availability.",
    )
    add_bundle(
        rows,
        "raw_verification_gate",
        "first_batch_merge_key_lineage_plan",
        "metadata_only_requires_raw_verification",
        f"plan_rows={csv_value(first_batch_merge_key_summary, 'first_batch_merge_key_lineage_plan_rows', '0')}; candidate_rows={csv_value(first_batch_merge_key_summary, 'first_batch_merge_key_candidate_variable_rows', '0')}; planned_rows={csv_value(first_batch_merge_key_summary, 'first_batch_merge_key_lineage_planned_rows', '0')}; raw_ready_rows={csv_value(first_batch_merge_key_summary, 'first_batch_merge_key_raw_ready_rows', '0')}",
        [TEMP_DIR / "first_batch_merge_key_lineage_plan.csv", TEMP_DIR / "first_batch_merge_key_candidate_variables.csv", RESULT_DIR / "first_batch_merge_key_lineage_summary.csv", REPORT_DIR / "first_batch_merge_key_lineage_plan.md"],
        "Metadata-only plan for household/person keys, survey design variables, timing, geography, and file lineage; merge cardinality and raw values remain unverified.",
    )
    value_key_read_ok = int_value(csv_value(first_batch_value_key_summary, "first_batch_value_rows_read_ok", "0"))
    add_bundle(
        rows,
        "raw_verification_gate",
        "first_batch_raw_value_key_audit",
        "raw_value_summary_available_manual_review_required" if value_key_read_ok > 0 else "blocked_raw_value_key_audit",
        f"raw_ready={csv_value(first_batch_value_key_summary, 'raw_ready_first_batch_dataset_rows', '0')}; value_rows={csv_value(first_batch_value_key_summary, 'first_batch_value_audit_rows', '0')}; read_ok={csv_value(first_batch_value_key_summary, 'first_batch_value_rows_read_ok', '0')}; key_rows={csv_value(first_batch_value_key_summary, 'first_batch_key_audit_rows', '0')}; promoted={csv_value(first_batch_value_key_summary, 'first_batch_recipe_promoted_rows', '0')}",
        [TEMP_DIR / "first_batch_raw_value_key_audit.csv", TEMP_DIR / "first_batch_raw_merge_key_audit.csv", TEMP_DIR / "first_batch_harmonization_value_audit_auto.csv", RESULT_DIR / "first_batch_raw_value_key_summary.csv", REPORT_DIR / "first_batch_raw_value_key_audit.md"],
        "Observed raw values and file-level key cardinality were summarized for raw-ready first-batch datasets; every auto value-audit row remains ready_for_recipe=0 pending manual unit, recall-period, missing-code, skip-pattern, and merge-key review.",
    )
    add_bundle(
        rows,
        "raw_verification_gate",
        "alb2002_household_core_merge_audit",
        csv_value(alb2002_core_summary, "alb2002_household_core_current_decision", "missing"),
        f"candidate_rows={csv_value(alb2002_core_summary, 'alb2002_household_core_candidate_rows', '0')}; consumption_rows={csv_value(alb2002_core_summary, 'alb2002_households_with_total_consumption', '0')}; weight_rows={csv_value(alb2002_core_summary, 'alb2002_households_with_household_weight', '0')}; oop4w_positive={csv_value(alb2002_core_summary, 'alb2002_households_with_oop_4w_positive', '0')}; district_rows={csv_value(alb2002_core_summary, 'alb2002_households_with_district_code', '0')}; survey_month_rows={csv_value(alb2002_core_summary, 'alb2002_households_with_survey_month', '0')}; interview_date_rows={csv_value(alb2002_core_summary, 'alb2002_households_with_interview_date', '0')}; recipe_ready={csv_value(alb2002_core_summary, 'alb2002_household_core_recipe_ready_rows', '0')}",
        [TEMP_DIR / "alb2002_household_core_candidate.csv", TEMP_DIR / "alb2002_household_core_merge_audit.csv", TEMP_DIR / "alb2002_household_core_lineage.csv", RESULT_DIR / "alb2002_household_core_candidate_summary.csv", REPORT_DIR / "alb2002_household_core_merge_audit.md"],
        "A temp-only ALB_2002 household core candidate exists for review with observed raw interview date/month and district fields, but it remains outside data/ because OOP aggregation/recall, units, access skip patterns, district climate crosswalk, and cross-wave comparability are unresolved.",
    )
    add_bundle(
        rows,
        "raw_verification_gate",
        "alb2002_weight_design_evidence_audit",
        csv_value(alb2002_weight_design_summary, "alb2002_weight_design_current_decision", "missing"),
        f"audit_rows={csv_value(alb2002_weight_design_summary, 'alb2002_weight_design_evidence_audit_rows', '0')}; source_flags={csv_value(alb2002_weight_design_summary, 'alb2002_weight_design_source_page_flag_rows', '0')}; raw_weight_rows={csv_value(alb2002_weight_design_summary, 'alb2002_weight_design_raw_weight_file_rows', '0')}; positive_weights={csv_value(alb2002_weight_design_summary, 'alb2002_weight_design_positive_weight_rows', '0')}; key_matches={csv_value(alb2002_weight_design_summary, 'alb2002_weight_design_candidate_key_match_rows', '0')}; distinct_psu={csv_value(alb2002_weight_design_summary, 'alb2002_weight_design_distinct_psu_rows', '0')}; distinct_strata={csv_value(alb2002_weight_design_summary, 'alb2002_weight_design_distinct_stratum_rows', '0')}; weighted_inference_ready={csv_value(alb2002_weight_design_summary, 'alb2002_weight_design_weighted_inference_ready_rows', '0')}; harmonized_ready={csv_value(alb2002_weight_design_summary, 'alb2002_weight_design_harmonized_promotion_ready_rows', '0')}",
        [TEMP_DIR / "alb2002_weight_design_evidence_audit.csv", RESULT_DIR / "alb2002_weight_design_evidence_summary.csv", REPORT_DIR / "alb2002_weight_design_evidence_audit.md", TEMP_DIR / "source_snapshots" / "alb2002_worldbank_study_description_weight_design.html"],
        "ALB_2002 weight/design audit verifies readable household weights and design fields, plus official study-page sampling context, but keeps weighted inference and harmonized data promotion at zero.",
    )
    add_bundle(
        rows,
        "climate_outcome_gate",
        "alb2002_che_candidate_outcomes",
        csv_value(alb2002_che_candidate_summary, "alb2002_che_candidate_current_decision", "missing"),
        f"household_rows={csv_value(alb2002_che_candidate_summary, 'alb2002_che_candidate_household_rows', '0')}; denominator_rows={csv_value(alb2002_che_candidate_summary, 'alb2002_che_candidate_denominator_rows', '0')}; che10_rows={csv_value(alb2002_che_candidate_summary, 'alb2002_che_candidate_che10_rows', '0')}; che10_rate={csv_value(alb2002_che_candidate_summary, 'alb2002_che_candidate_che10_rate', '0')}; che25_rows={csv_value(alb2002_che_candidate_summary, 'alb2002_che_candidate_che25_rows', '0')}; che25_rate={csv_value(alb2002_che_candidate_summary, 'alb2002_che_candidate_che25_rate', '0')}; outcome_promotion_ready={csv_value(alb2002_che_candidate_summary, 'alb2002_che_candidate_outcome_promotion_ready_rows', '0')}; climate_ready={csv_value(alb2002_che_candidate_summary, 'alb2002_che_candidate_climate_linkage_ready_rows', '0')}",
        [TEMP_DIR / "alb2002_che_candidate_household_outcomes.csv", TEMP_DIR / "alb2002_che_candidate_outcome_lineage.csv", RESULT_DIR / "alb2002_che_candidate_outcome_audit.csv", RESULT_DIR / "alb2002_che_candidate_outcome_summary.csv", REPORT_DIR / "alb2002_che_candidate_outcome_audit.md"],
        "ALB_2002 household-level CHE10/CHE25 candidate outcomes are constructed in temp for audit, but no outcome rows are promoted to data/ because recipe, SDG, benchmark, and climate-geography gates remain blocked.",
    )
    add_bundle(
        rows,
        "climate_outcome_gate",
        "alb2002_access_candidate_outcomes",
        csv_value(alb2002_access_candidate_summary, "alb2002_access_candidate_current_decision", "missing"),
        f"household_rows={csv_value(alb2002_access_candidate_summary, 'alb2002_access_candidate_household_rows', '0')}; q01_need_rows={csv_value(alb2002_access_candidate_summary, 'alb2002_access_candidate_q01_need_rows', '0')}; person_need_rows={csv_value(alb2002_access_candidate_summary, 'alb2002_access_candidate_person_need_rows', '0')}; composite_any_rows={csv_value(alb2002_access_candidate_summary, 'alb2002_access_candidate_composite_any_rows', '0')}; composite_any_weighted={csv_value(alb2002_access_candidate_summary, 'alb2002_access_candidate_composite_any_weighted_rate', '0')}; composite_cost_rows={csv_value(alb2002_access_candidate_summary, 'alb2002_access_candidate_composite_cost_rows', '0')}; outcome_promotion_ready={csv_value(alb2002_access_candidate_summary, 'alb2002_access_candidate_outcome_promotion_ready_rows', '0')}; climate_ready={csv_value(alb2002_access_candidate_summary, 'alb2002_access_candidate_climate_linkage_ready_rows', '0')}",
        [TEMP_DIR / "alb2002_access_candidate_household_outcomes.csv", TEMP_DIR / "alb2002_access_candidate_outcome_lineage.csv", RESULT_DIR / "alb2002_access_candidate_outcome_audit.csv", RESULT_DIR / "alb2002_access_candidate_outcome_summary.csv", REPORT_DIR / "alb2002_access_candidate_outcome_audit.md"],
        "ALB_2002 household-level access, need, barrier, and composite candidates are constructed in temp for audit, but no access outcome rows are promoted to data/ because denominator, skip, recipe, financial-alignment, and climate-geography gates remain blocked.",
    )
    add_bundle(
        rows,
        "climate_outcome_gate",
        "alb2002_uhc_composite_candidate_outcomes",
        csv_value(alb2002_uhc_composite_summary, "alb2002_uhc_composite_candidate_current_decision", "missing"),
        f"household_rows={csv_value(alb2002_uhc_composite_summary, 'alb2002_uhc_composite_candidate_household_rows', '0')}; che10_or_access_rows={csv_value(alb2002_uhc_composite_summary, 'alb2002_uhc_composite_candidate_che10_or_access_rows', '0')}; che10_or_access_weighted={csv_value(alb2002_uhc_composite_summary, 'alb2002_uhc_composite_candidate_che10_or_access_weighted_rate', '0')}; che25_or_access_rows={csv_value(alb2002_uhc_composite_summary, 'alb2002_uhc_composite_candidate_che25_or_access_rows', '0')}; both_che10_access_rows={csv_value(alb2002_uhc_composite_summary, 'alb2002_uhc_composite_candidate_both_che10_access_rows', '0')}; coping_rows={csv_value(alb2002_uhc_composite_summary, 'alb2002_uhc_composite_candidate_coping_rows', '0')}; outcome_promotion_ready={csv_value(alb2002_uhc_composite_summary, 'alb2002_uhc_composite_candidate_outcome_promotion_ready_rows', '0')}; climate_ready={csv_value(alb2002_uhc_composite_summary, 'alb2002_uhc_composite_candidate_climate_linkage_ready_rows', '0')}",
        [TEMP_DIR / "alb2002_uhc_composite_candidate_outcomes.csv", TEMP_DIR / "alb2002_uhc_composite_candidate_lineage.csv", RESULT_DIR / "alb2002_uhc_composite_candidate_audit.csv", RESULT_DIR / "alb2002_uhc_composite_candidate_summary.csv", REPORT_DIR / "alb2002_uhc_composite_candidate_audit.md"],
        "ALB_2002 household-level UHC double-failure, financial-only, access-only, both-failure, and coping candidates are constructed in temp for audit, but no composite outcome rows are promoted to data/ because upstream financial, access, recipe, SDG, benchmark, and climate gates remain blocked.",
    )
    add_bundle(
        rows,
        "climate_outcome_gate",
        "alb2002_analysis_candidate_dataset",
        csv_value(alb2002_analysis_candidate_summary, "alb2002_analysis_candidate_current_decision", "missing"),
        f"candidate_rows={csv_value(alb2002_analysis_candidate_summary, 'alb2002_analysis_candidate_rows', '0')}; columns={csv_value(alb2002_analysis_candidate_summary, 'alb2002_analysis_candidate_columns', '0')}; complete_candidate_gates={csv_value(alb2002_analysis_candidate_summary, 'alb2002_analysis_candidate_complete_candidate_gates', '0')}; missing_gates={csv_value(alb2002_analysis_candidate_summary, 'alb2002_analysis_candidate_missing_gates', '0')}; blocked_promotion_gates={csv_value(alb2002_analysis_candidate_summary, 'alb2002_analysis_candidate_blocked_promotion_gates', '0')}; harmonized_ready={csv_value(alb2002_analysis_candidate_summary, 'alb2002_analysis_candidate_harmonized_ready_rows', '0')}; outcome_ready={csv_value(alb2002_analysis_candidate_summary, 'alb2002_analysis_candidate_outcome_promotion_ready_rows', '0')}; climate_ready={csv_value(alb2002_analysis_candidate_summary, 'alb2002_analysis_candidate_climate_linkage_ready_rows', '0')}; data_write_ready={csv_value(alb2002_analysis_candidate_summary, 'alb2002_analysis_candidate_data_write_ready_rows', '0')}",
        [TEMP_DIR / "alb2002_analysis_candidate_dataset.csv", TEMP_DIR / "alb2002_analysis_candidate_lineage.csv", RESULT_DIR / "alb2002_analysis_candidate_readiness_audit.csv", RESULT_DIR / "alb2002_analysis_candidate_readiness_summary.csv", REPORT_DIR / "alb2002_analysis_candidate_readiness_audit.md"],
        "ALB_2002 household core, timing, admin geography, weights, access signals, and temp CHE candidate outcomes are joined for audit in temp, with harmonized/outcome/climate data promotion still blocked.",
    )
    add_bundle(
        rows,
        "climate_outcome_gate",
        "alb2002_climate_centroid_exposure_candidates",
        csv_value(alb2002_climate_centroid_summary, "alb2002_climate_centroid_current_decision", "missing"),
        f"input_rows={csv_value(alb2002_climate_centroid_summary, 'alb2002_climate_centroid_input_rows', '0')}; exposure_rows={csv_value(alb2002_climate_centroid_summary, 'alb2002_climate_centroid_exposure_rows', '0')}; districts={csv_value(alb2002_climate_centroid_summary, 'alb2002_climate_centroid_distinct_district_rows', '0')}; households={csv_value(alb2002_climate_centroid_summary, 'alb2002_climate_centroid_household_rows_covered', '0')}; api_rows={csv_value(alb2002_climate_centroid_summary, 'alb2002_climate_centroid_nasa_api_rows', '0')}; api_failed={csv_value(alb2002_climate_centroid_summary, 'alb2002_climate_centroid_nasa_failed_rows', '0')}; precip_nonmissing={csv_value(alb2002_climate_centroid_summary, 'alb2002_climate_centroid_precip_nonmissing_rows', '0')}; temp_nonmissing={csv_value(alb2002_climate_centroid_summary, 'alb2002_climate_centroid_temp_nonmissing_rows', '0')}; boundary_year={csv_value(alb2002_climate_centroid_summary, 'alb2002_climate_centroid_boundary_year', 'missing')}; climate_ready={csv_value(alb2002_climate_centroid_summary, 'alb2002_climate_centroid_climate_linkage_ready_rows', '0')}; data_write_ready={csv_value(alb2002_climate_centroid_summary, 'alb2002_climate_centroid_data_write_ready_rows', '0')}",
        [TEMP_DIR / "alb2002_climate_centroid_exposure_input.csv", TEMP_DIR / "alb2002_climate_centroid_exposure_candidates.csv", TEMP_DIR / "alb2002_climate_centroid_nasa_power_api_manifest.csv", RESULT_DIR / "alb2002_climate_centroid_exposure_audit.csv", RESULT_DIR / "alb2002_climate_centroid_exposure_summary.csv", REPORT_DIR / "alb2002_climate_centroid_exposure_audit.md"],
        "ALB_2002 district-month climate summaries are computed at candidate ADM2 bounding-box centroids as a temp-only NASA POWER stress test, while primary CHIRPS/ERA5, historical baseline, and climate-linkage promotion gates remain blocked.",
    )
    add_bundle(
        rows,
        "climate_outcome_gate",
        "alb2002_climate_shock_candidate_diagnostics",
        csv_value(alb2002_climate_shock_summary, "alb2002_climate_shock_candidate_current_decision", "missing"),
        f"shock_rows={csv_value(alb2002_climate_shock_summary, 'alb2002_climate_shock_candidate_exposure_rows', '0')}; source_centroid_rows={csv_value(alb2002_climate_shock_summary, 'alb2002_climate_shock_candidate_source_centroid_rows', '0')}; reference_groups={csv_value(alb2002_climate_shock_summary, 'alb2002_climate_shock_candidate_reference_group_rows', '0')}; min_group={csv_value(alb2002_climate_shock_summary, 'alb2002_climate_shock_candidate_min_reference_group_size', '0')}; precip_z={csv_value(alb2002_climate_shock_summary, 'alb2002_climate_shock_candidate_precip_z_nonmissing_rows', '0')}; temp_z={csv_value(alb2002_climate_shock_summary, 'alb2002_climate_shock_candidate_temp_z_nonmissing_rows', '0')}; low_rain={csv_value(alb2002_climate_shock_summary, 'alb2002_climate_shock_candidate_low_rain_rows', '0')}; extreme_wet={csv_value(alb2002_climate_shock_summary, 'alb2002_climate_shock_candidate_extreme_wet_rows', '0')}; extreme_heat={csv_value(alb2002_climate_shock_summary, 'alb2002_climate_shock_candidate_extreme_heat_rows', '0')}; combined={csv_value(alb2002_climate_shock_summary, 'alb2002_climate_shock_candidate_combined_stress_rows', '0')}; climate_ready={csv_value(alb2002_climate_shock_summary, 'alb2002_climate_shock_candidate_climate_linkage_ready_rows', '0')}; data_write_ready={csv_value(alb2002_climate_shock_summary, 'alb2002_climate_shock_candidate_data_write_ready_rows', '0')}",
        [TEMP_DIR / "alb2002_climate_shock_candidate_exposures.csv", TEMP_DIR / "alb2002_climate_shock_candidate_lineage.csv", RESULT_DIR / "alb2002_climate_shock_candidate_audit.csv", RESULT_DIR / "alb2002_climate_shock_candidate_summary.csv", REPORT_DIR / "alb2002_climate_shock_candidate_audit.md"],
        "ALB_2002 within-candidate rainfall and temperature z-scores are documented as diagnostic flags only; they are not historical anomalies or accepted treatment variables because primary climate sources, baselines, and verified geography remain blocked.",
    )
    add_bundle(
        rows,
        "climate_outcome_gate",
        "alb2002_climate_outcome_linked_candidate",
        csv_value(alb2002_climate_outcome_linked_summary, "alb2002_climate_outcome_linked_candidate_current_decision", "missing"),
        f"linked_rows={csv_value(alb2002_climate_outcome_linked_summary, 'alb2002_climate_outcome_linked_candidate_rows', '0')}; households={csv_value(alb2002_climate_outcome_linked_summary, 'alb2002_climate_outcome_linked_candidate_household_rows', '0')}; windows={csv_value(alb2002_climate_outcome_linked_summary, 'alb2002_climate_outcome_linked_candidate_window_rows', '0')}; district_months={csv_value(alb2002_climate_outcome_linked_summary, 'alb2002_climate_outcome_linked_candidate_district_month_cells', '0')}; unmatched={csv_value(alb2002_climate_outcome_linked_summary, 'alb2002_climate_outcome_linked_candidate_unmatched_rows', '0')}; precip_z={csv_value(alb2002_climate_outcome_linked_summary, 'alb2002_climate_outcome_linked_candidate_precip_z_rows', '0')}; temp_z={csv_value(alb2002_climate_outcome_linked_summary, 'alb2002_climate_outcome_linked_candidate_temp_z_rows', '0')}; combined={csv_value(alb2002_climate_outcome_linked_summary, 'alb2002_climate_outcome_linked_candidate_combined_stress_rows', '0')}; climate_ready={csv_value(alb2002_climate_outcome_linked_summary, 'alb2002_climate_outcome_linked_candidate_climate_linkage_ready_rows', '0')}; outcome_ready={csv_value(alb2002_climate_outcome_linked_summary, 'alb2002_climate_outcome_linked_candidate_outcome_promotion_ready_rows', '0')}; data_write_ready={csv_value(alb2002_climate_outcome_linked_summary, 'alb2002_climate_outcome_linked_candidate_data_write_ready_rows', '0')}",
        [TEMP_DIR / "alb2002_climate_outcome_linked_candidate.csv", TEMP_DIR / "alb2002_climate_outcome_linked_candidate_lineage.csv", RESULT_DIR / "alb2002_climate_outcome_linked_candidate_audit.csv", RESULT_DIR / "alb2002_climate_outcome_linked_candidate_summary.csv", REPORT_DIR / "alb2002_climate_outcome_linked_candidate_audit.md"],
        "ALB_2002 household rows are mechanically expanded to diagnostic climate-window rows and linked to temp UHC candidates. The output remains temp-only because recipe, outcome-promotion, geography, primary climate-source, and historical-baseline gates are blocked.",
    )
    add_bundle(
        rows,
        "climate_outcome_gate",
        "alb2002_linked_candidate_descriptive_screen",
        csv_value(alb2002_linked_candidate_descriptive_summary, "alb2002_linked_candidate_descriptive_current_decision", "missing"),
        f"input_rows={csv_value(alb2002_linked_candidate_descriptive_summary, 'alb2002_linked_candidate_descriptive_input_rows', '0')}; households={csv_value(alb2002_linked_candidate_descriptive_summary, 'alb2002_linked_candidate_descriptive_household_rows', '0')}; windows={csv_value(alb2002_linked_candidate_descriptive_summary, 'alb2002_linked_candidate_descriptive_window_rows', '0')}; audit_rows={csv_value(alb2002_linked_candidate_descriptive_summary, 'alb2002_linked_candidate_descriptive_audit_rows', '0')}; cell_rows={csv_value(alb2002_linked_candidate_descriptive_summary, 'alb2002_linked_candidate_descriptive_cell_rows', '0')}; household_cells={csv_value(alb2002_linked_candidate_descriptive_summary, 'alb2002_linked_candidate_descriptive_household_outcome_cell_rows', '0')}; subgroup_cells={csv_value(alb2002_linked_candidate_descriptive_summary, 'alb2002_linked_candidate_descriptive_subgroup_outcome_cell_rows', '0')}; climate_flag_cells={csv_value(alb2002_linked_candidate_descriptive_summary, 'alb2002_linked_candidate_descriptive_climate_flag_cell_rows', '0')}; outcome_by_climate_cells={csv_value(alb2002_linked_candidate_descriptive_summary, 'alb2002_linked_candidate_descriptive_outcome_by_climate_flag_cell_rows', '0')}; climate_ready={csv_value(alb2002_linked_candidate_descriptive_summary, 'alb2002_linked_candidate_descriptive_climate_linkage_ready_rows', '0')}; outcome_ready={csv_value(alb2002_linked_candidate_descriptive_summary, 'alb2002_linked_candidate_descriptive_outcome_promotion_ready_rows', '0')}; data_write_ready={csv_value(alb2002_linked_candidate_descriptive_summary, 'alb2002_linked_candidate_descriptive_data_write_ready_rows', '0')}",
        [RESULT_DIR / "alb2002_linked_candidate_descriptive_audit.csv", RESULT_DIR / "alb2002_linked_candidate_descriptive_cells.csv", RESULT_DIR / "alb2002_linked_candidate_descriptive_summary.csv", REPORT_DIR / "alb2002_linked_candidate_descriptive_diagnostics.md"],
        "ALB_2002 candidate rates are summarized for audit readability only. This screen does not satisfy promoted descriptive diagnostics, because the underlying outcome, climate, recipe, survey-design, and data-write gates remain blocked.",
    )
    add_bundle(
        rows,
        "climate_outcome_gate",
        "alb2002_provisional_outcome_feasibility",
        csv_value(alb2002_outcome_summary, "alb2002_provisional_outcome_current_decision", "missing"),
        f"audit_rows={csv_value(alb2002_outcome_summary, 'alb2002_provisional_outcome_audit_rows', '0')}; financial_tests={csv_value(alb2002_outcome_summary, 'alb2002_provisional_financial_stress_test_rows', '0')}; access_proxies={csv_value(alb2002_outcome_summary, 'alb2002_provisional_access_proxy_rows', '0')}; low_event_rate={csv_value(alb2002_outcome_summary, 'alb2002_provisional_low_event_rate_rows', '0')}; ready={csv_value(alb2002_outcome_summary, 'alb2002_provisional_outcome_ready_rows', '0')}",
        [TEMP_DIR / "alb2002_provisional_outcome_feasibility_audit.csv", RESULT_DIR / "alb2002_provisional_outcome_feasibility_summary.csv", REPORT_DIR / "alb2002_provisional_outcome_feasibility.md"],
        "ALB_2002 raw OOP/access fields have provisional event-rate diagnostics, but no SDG 3.8.2, final CHE, climate-linked, descriptive, causal, ML, or policy outcome is constructed.",
    )
    add_bundle(
        rows,
        "climate_outcome_gate",
        "alb2002_outcome_semantics_raw_value_audit",
        csv_value(alb2002_semantics_summary, "alb2002_outcome_semantics_current_decision", "missing"),
        f"audit_rows={csv_value(alb2002_semantics_summary, 'alb2002_outcome_semantics_raw_value_audit_rows', '0')}; source_files={csv_value(alb2002_semantics_summary, 'alb2002_outcome_semantics_source_files_scanned', '0')}; oop_candidates={csv_value(alb2002_semantics_summary, 'alb2002_outcome_semantics_financial_oop_candidate_rows', '0')}; access_candidates={csv_value(alb2002_semantics_summary, 'alb2002_outcome_semantics_access_candidate_rows', '0')}; value_label_rows={csv_value(alb2002_semantics_summary, 'alb2002_outcome_semantics_rows_with_value_labels', '0')}; conditional_reason_rows={csv_value(alb2002_semantics_summary, 'alb2002_outcome_semantics_conditional_reason_rows', '0')}; outcome_ready={csv_value(alb2002_semantics_summary, 'alb2002_outcome_semantics_outcome_ready_rows', '0')}; sdg382_ready={csv_value(alb2002_semantics_summary, 'alb2002_outcome_semantics_sdg382_ready_rows', '0')}",
        [TEMP_DIR / "alb2002_outcome_semantics_raw_value_audit.csv", RESULT_DIR / "alb2002_outcome_semantics_raw_value_summary.csv", REPORT_DIR / "alb2002_outcome_semantics_raw_value_audit.md"],
        "ALB_2002 raw health module labels and values are now audited for OOP/access semantics. The audit strengthens the evidence trail but keeps CHE, SDG 3.8.2, and forgone-care outcome promotion blocked pending unit, recall, missing-code, and skip-pattern review.",
    )
    add_bundle(
        rows,
        "climate_outcome_gate",
        "alb2002_health_questionnaire_semantics_audit",
        csv_value(alb2002_health_questionnaire_summary, "alb2002_health_questionnaire_current_decision", "missing"),
        f"rows={csv_value(alb2002_health_questionnaire_summary, 'alb2002_health_questionnaire_semantics_rows', '0')}; oop_items={csv_value(alb2002_health_questionnaire_summary, 'alb2002_health_questionnaire_oop_item_rows', '0')}; gift_items={csv_value(alb2002_health_questionnaire_summary, 'alb2002_health_questionnaire_gift_item_rows', '0')}; new_lek_rows={csv_value(alb2002_health_questionnaire_summary, 'alb2002_health_questionnaire_new_lek_unit_rows', '0')}; four_week_oop={csv_value(alb2002_health_questionnaire_summary, 'alb2002_health_questionnaire_four_week_oop_rows', '0')}; twelve_month_oop={csv_value(alb2002_health_questionnaire_summary, 'alb2002_health_questionnaire_twelve_month_oop_rows', '0')}; payment_positive_skip_leaks={csv_value(alb2002_health_questionnaire_summary, 'alb2002_health_questionnaire_payment_positive_when_not_triggered_rows', '0')}; payment_nonmissing_skip_review={csv_value(alb2002_health_questionnaire_summary, 'alb2002_health_questionnaire_payment_nonmissing_when_not_triggered_rows', '0')}; outcome_ready={csv_value(alb2002_health_questionnaire_summary, 'alb2002_health_questionnaire_outcome_ready_rows', '0')}; climate_ready={csv_value(alb2002_health_questionnaire_summary, 'alb2002_health_questionnaire_climate_linkage_ready_rows', '0')}",
        [TEMP_DIR / "alb2002_health_questionnaire_semantics_audit.csv", RESULT_DIR / "alb2002_health_questionnaire_semantics_summary.csv", REPORT_DIR / "alb2002_health_questionnaire_semantics_audit.md"],
        "ALB_2002 questionnaire evidence now confirms NEW LEKS payment units, mixed four-week and twelve-month OOP recall, gift/payment-scope rows, access-barrier codes, and raw skip-path diagnostics. It still promotes zero outcome, SDG, or climate-linkage rows.",
    )
    add_bundle(
        rows,
        "climate_outcome_gate",
        "alb2002_oop_aggregation_policy_audit",
        csv_value(alb2002_oop_policy_summary, "alb2002_oop_aggregation_policy_current_decision", "missing"),
        f"policy_rows={csv_value(alb2002_oop_policy_summary, 'alb2002_oop_aggregation_policy_rows', '0')}; household_rows={csv_value(alb2002_oop_policy_summary, 'alb2002_oop_aggregation_policy_household_rows', '0')}; core_4w_match={csv_value(alb2002_oop_policy_summary, 'alb2002_oop_aggregation_policy_core_4w_match_rows', '0')}; core_12m_match={csv_value(alb2002_oop_policy_summary, 'alb2002_oop_aggregation_policy_core_12m_match_rows', '0')}; max_che10={csv_value(alb2002_oop_policy_summary, 'alb2002_oop_aggregation_policy_max_che10_rate', '0')}; max_che25={csv_value(alb2002_oop_policy_summary, 'alb2002_oop_aggregation_policy_max_che25_rate', '0')}; outcome_ready={csv_value(alb2002_oop_policy_summary, 'alb2002_oop_aggregation_policy_outcome_ready_rows', '0')}; sdg382_ready={csv_value(alb2002_oop_policy_summary, 'alb2002_oop_aggregation_policy_sdg382_ready_rows', '0')}; climate_ready={csv_value(alb2002_oop_policy_summary, 'alb2002_oop_aggregation_policy_climate_linkage_ready_rows', '0')}",
        [TEMP_DIR / "alb2002_oop_aggregation_policy_audit.csv", RESULT_DIR / "alb2002_oop_aggregation_policy_summary.csv", REPORT_DIR / "alb2002_oop_aggregation_policy_audit.md"],
        "ALB_2002 OOP aggregation policy audit compares four-week, 12-month, gift, transport, and annualized stress-test variants against total consumption. It confirms the existing core OOP sums match the recomputed no-gifts-with-transport policy but keeps all outcome, SDG, and climate promotion rows at zero.",
    )
    add_bundle(
        rows,
        "climate_outcome_gate",
        "alb2002_skip_missing_semantics_audit",
        csv_value(alb2002_skip_missing_summary, "alb2002_skip_missing_current_decision", "missing"),
        f"rows={csv_value(alb2002_skip_missing_summary, 'alb2002_skip_missing_semantics_rows', '0')}; payment_blocks={csv_value(alb2002_skip_missing_summary, 'alb2002_skip_missing_payment_block_rows', '0')}; condition_blocks={csv_value(alb2002_skip_missing_summary, 'alb2002_skip_missing_access_condition_rows', '0')}; positive_skipped_rows={csv_value(alb2002_skip_missing_summary, 'alb2002_skip_missing_payment_positive_when_not_triggered_rows', '0')}; zero_skipped_cells={csv_value(alb2002_skip_missing_summary, 'alb2002_skip_missing_payment_zero_cells_when_not_triggered', '0')}; positive_skipped_cells={csv_value(alb2002_skip_missing_summary, 'alb2002_skip_missing_payment_positive_cells_when_not_triggered', '0')}; outcome_ready={csv_value(alb2002_skip_missing_summary, 'alb2002_skip_missing_outcome_ready_rows', '0')}; sdg382_ready={csv_value(alb2002_skip_missing_summary, 'alb2002_skip_missing_sdg382_ready_rows', '0')}; climate_ready={csv_value(alb2002_skip_missing_summary, 'alb2002_skip_missing_climate_linkage_ready_rows', '0')}",
        [TEMP_DIR / "alb2002_skip_missing_semantics_audit.csv", RESULT_DIR / "alb2002_skip_missing_semantics_summary.csv", REPORT_DIR / "alb2002_skip_missing_semantics_audit.md"],
        "ALB_2002 skip/missing semantics audit shows skipped downstream payment values are zero-only with no positive skipped-payment leaks. The downstream skip-value decision is documented separately; outcome, SDG, recipe, and climate promotion remain closed pending OOP scope, denominator, access, and geography gates.",
    )
    add_bundle(
        rows,
        "climate_outcome_gate",
        "alb2002_oop_skip_value_decision_audit",
        csv_value(alb2002_oop_skip_value_summary, "alb2002_oop_skip_value_current_decision", "missing"),
        f"rows={csv_value(alb2002_oop_skip_value_summary, 'alb2002_oop_skip_value_decision_rows', '0')}; payment_blocks={csv_value(alb2002_oop_skip_value_summary, 'alb2002_oop_skip_value_payment_block_rows', '0')}; condition_blocks={csv_value(alb2002_oop_skip_value_summary, 'alb2002_oop_skip_value_access_condition_block_rows', '0')}; nonmissing_skipped_cells={csv_value(alb2002_oop_skip_value_summary, 'alb2002_oop_skip_value_payment_nonmissing_skipped_cells', '0')}; zero_skipped_cells={csv_value(alb2002_oop_skip_value_summary, 'alb2002_oop_skip_value_payment_zero_skipped_cells', '0')}; positive_skipped_rows={csv_value(alb2002_oop_skip_value_summary, 'alb2002_oop_skip_value_payment_positive_skipped_rows', '0')}; positive_skipped_cells={csv_value(alb2002_oop_skip_value_summary, 'alb2002_oop_skip_value_payment_positive_skipped_cells', '0')}; zero_skip_ready={csv_value(alb2002_oop_skip_value_summary, 'alb2002_oop_skip_value_zero_skip_policy_ready_rows', '0')}; recall_ready={csv_value(alb2002_oop_skip_value_summary, 'alb2002_oop_skip_value_oop_recall_scope_ready_rows', '0')}; inclusion_ready={csv_value(alb2002_oop_skip_value_summary, 'alb2002_oop_skip_value_oop_inclusion_scope_ready_rows', '0')}; outcome_ready={csv_value(alb2002_oop_skip_value_summary, 'alb2002_oop_skip_value_outcome_ready_rows', '0')}; sdg382_ready={csv_value(alb2002_oop_skip_value_summary, 'alb2002_oop_skip_value_sdg382_ready_rows', '0')}; climate_ready={csv_value(alb2002_oop_skip_value_summary, 'alb2002_oop_skip_value_climate_linkage_ready_rows', '0')}",
        [TEMP_DIR / "alb2002_oop_skip_value_decision_audit.csv", RESULT_DIR / "alb2002_oop_skip_value_decision_summary.csv", REPORT_DIR / "alb2002_oop_skip_value_decision_audit.md"],
        "ALB_2002 OOP skip-value decision audit narrows skipped downstream payment handling to a no-positive-leakage decision while leaving recall scope, inclusion scope, outcome, SDG, and climate promotion closed.",
    )
    add_bundle(
        rows,
        "climate_outcome_gate",
        "alb2002_access_need_denominator_policy_audit",
        csv_value(alb2002_access_need_summary, "alb2002_access_need_current_decision", "missing"),
        f"rows={csv_value(alb2002_access_need_summary, 'alb2002_access_need_denominator_policy_rows', '0')}; households={csv_value(alb2002_access_need_summary, 'alb2002_access_need_household_rows', '0')}; person_need={csv_value(alb2002_access_need_summary, 'alb2002_access_need_person_need_household_rows', '0')}; q01_need={csv_value(alb2002_access_need_summary, 'alb2002_access_need_q01_need_rows', '0')}; delayed={csv_value(alb2002_access_need_summary, 'alb2002_access_need_delayed_help_rows', '0')}; referral_not_gone={csv_value(alb2002_access_need_summary, 'alb2002_access_need_referral_not_gone_rows', '0')}; refused={csv_value(alb2002_access_need_summary, 'alb2002_access_need_refused_service_rows', '0')}; any_access_barrier={csv_value(alb2002_access_need_summary, 'alb2002_access_need_composite_any_access_barrier_rows', '0')}; low_event={csv_value(alb2002_access_need_summary, 'alb2002_access_need_low_event_rate_rows', '0')}; outcome_ready={csv_value(alb2002_access_need_summary, 'alb2002_access_need_outcome_ready_rows', '0')}; climate_ready={csv_value(alb2002_access_need_summary, 'alb2002_access_need_climate_linkage_ready_rows', '0')}",
        [TEMP_DIR / "alb2002_access_need_denominator_policy_audit.csv", RESULT_DIR / "alb2002_access_need_denominator_policy_summary.csv", REPORT_DIR / "alb2002_access_need_denominator_policy_audit.md"],
        "ALB_2002 access/need denominator policy audit separates broad need, person-level illness need, delayed care, referral nonuse, refusal, medicine access, and composite barrier candidates. It keeps promotion rows at zero pending explicit denominator policy and remaining OOP/geography gates.",
    )
    add_bundle(
        rows,
        "climate_outcome_gate",
        "alb2002_consumption_sdg_denominator_policy_audit",
        csv_value(alb2002_consumption_sdg_summary, "alb2002_consumption_sdg_current_decision", "missing"),
        f"rows={csv_value(alb2002_consumption_sdg_summary, 'alb2002_consumption_sdg_denominator_policy_rows', '0')}; households={csv_value(alb2002_consumption_sdg_summary, 'alb2002_consumption_sdg_household_rows', '0')}; positive_total_consumption={csv_value(alb2002_consumption_sdg_summary, 'alb2002_consumption_sdg_positive_total_consumption_rows', '0')}; positive_weight={csv_value(alb2002_consumption_sdg_summary, 'alb2002_consumption_sdg_positive_household_weight_rows', '0')}; positive_household_size={csv_value(alb2002_consumption_sdg_summary, 'alb2002_consumption_sdg_positive_household_size_rows', '0')}; spl_ready={csv_value(alb2002_consumption_sdg_summary, 'alb2002_consumption_sdg_spl_ready_rows', '0')}; ppp_cpi_ready={csv_value(alb2002_consumption_sdg_summary, 'alb2002_consumption_sdg_ppp_cpi_ready_rows', '0')}; discretionary_ready={csv_value(alb2002_consumption_sdg_summary, 'alb2002_consumption_sdg_discretionary_budget_ready_rows', '0')}; che_ready={csv_value(alb2002_consumption_sdg_summary, 'alb2002_consumption_sdg_che_denominator_ready_rows', '0')}; outcome_ready={csv_value(alb2002_consumption_sdg_summary, 'alb2002_consumption_sdg_outcome_ready_rows', '0')}; sdg382_ready={csv_value(alb2002_consumption_sdg_summary, 'alb2002_consumption_sdg_sdg382_ready_rows', '0')}; climate_ready={csv_value(alb2002_consumption_sdg_summary, 'alb2002_consumption_sdg_climate_linkage_ready_rows', '0')}",
        [TEMP_DIR / "alb2002_consumption_sdg_denominator_policy_audit.csv", RESULT_DIR / "alb2002_consumption_sdg_denominator_policy_summary.csv", REPORT_DIR / "alb2002_consumption_sdg_denominator_policy_audit.md"],
        "ALB_2002 consumption/SDG denominator policy audit verifies that total consumption, weights, and household size are visible for all candidate rows, but keeps CHE, SDG 3.8.2, outcome, recipe, and climate promotion blocked until unit/period, SPL, PPP/CPI, discretionary-budget, OOP, and geography gates pass.",
    )
    add_bundle(
        rows,
        "climate_outcome_gate",
        "alb2002_consumption_construction_source_audit",
        csv_value(alb2002_consumption_construction_summary, "alb2002_consumption_construction_current_decision", "missing"),
        f"rows={csv_value(alb2002_consumption_construction_summary, 'alb2002_consumption_construction_source_audit_rows', '0')}; public_pdf={csv_value(alb2002_consumption_construction_summary, 'alb2002_consumption_construction_public_pdf_present', '0')}; program_zip={csv_value(alb2002_consumption_construction_summary, 'alb2002_consumption_construction_program_zip_present', '0')}; do_files={csv_value(alb2002_consumption_construction_summary, 'alb2002_consumption_construction_do_file_rows', '0')}; totcons_do={csv_value(alb2002_consumption_construction_summary, 'alb2002_consumption_construction_totcons_do_present', '0')}; poverty_do={csv_value(alb2002_consumption_construction_summary, 'alb2002_consumption_construction_poverty_do_present', '0')}; metadata_json={csv_value(alb2002_consumption_construction_summary, 'alb2002_consumption_construction_metadata_json_present', '0')}; documentation_ready={csv_value(alb2002_consumption_construction_summary, 'alb2002_consumption_construction_documentation_ready_rows', '0')}; released_mapping_ready={csv_value(alb2002_consumption_construction_summary, 'alb2002_consumption_construction_released_variable_mapping_ready_rows', '0')}; denominator_variant_ready={csv_value(alb2002_consumption_construction_summary, 'alb2002_consumption_construction_denominator_variant_ready_rows', '0')}; outcome_ready={csv_value(alb2002_consumption_construction_summary, 'alb2002_consumption_construction_outcome_ready_rows', '0')}; sdg382_ready={csv_value(alb2002_consumption_construction_summary, 'alb2002_consumption_construction_sdg382_ready_rows', '0')}; climate_ready={csv_value(alb2002_consumption_construction_summary, 'alb2002_consumption_construction_climate_linkage_ready_rows', '0')}",
        [TEMP_DIR / "alb2002_consumption_construction_source_audit.csv", RESULT_DIR / "alb2002_consumption_construction_source_summary.csv", REPORT_DIR / "alb2002_consumption_construction_source_audit.md"],
        "ALB_2002 public IHSN source evidence documents the total-budget denominator variant and maps local `totcons` to public metadata `totcons3`; it still promotes zero outcome, SDG 3.8.2, or climate-linkage rows.",
    )
    add_bundle(
        rows,
        "climate_outcome_gate",
        "alb2002_consumption_aggregate_metadata_crosswalk",
        csv_value(alb2002_consumption_aggregate_summary, "alb2002_consumption_aggregate_crosswalk_current_decision", "missing"),
        f"rows={csv_value(alb2002_consumption_aggregate_summary, 'alb2002_consumption_aggregate_crosswalk_rows', '0')}; local_poverty_rows={csv_value(alb2002_consumption_aggregate_summary, 'alb2002_consumption_aggregate_crosswalk_local_poverty_rows', '0')}; metadata_catalog_rows={csv_value(alb2002_consumption_aggregate_summary, 'alb2002_consumption_aggregate_crosswalk_metadata_catalog_rows', '0')}; raw_totcons_positive={csv_value(alb2002_consumption_aggregate_summary, 'alb2002_consumption_aggregate_crosswalk_raw_totcons_positive_rows', '0')}; candidate_totcons_match={csv_value(alb2002_consumption_aggregate_summary, 'alb2002_consumption_aggregate_crosswalk_candidate_totcons_match_rows', '0')}; questionnaire_formula_hits={csv_value(alb2002_consumption_aggregate_summary, 'alb2002_consumption_aggregate_crosswalk_questionnaire_aggregate_formula_hits', '0')}; construction_source_rows={csv_value(alb2002_consumption_aggregate_summary, 'alb2002_consumption_aggregate_crosswalk_construction_source_rows', '0')}; construction_do_files={csv_value(alb2002_consumption_aggregate_summary, 'alb2002_consumption_aggregate_crosswalk_construction_do_file_rows', '0')}; documentation_ready={csv_value(alb2002_consumption_aggregate_summary, 'alb2002_consumption_aggregate_crosswalk_official_documentation_ready_rows', '0')}; released_mapping_ready={csv_value(alb2002_consumption_aggregate_summary, 'alb2002_consumption_aggregate_crosswalk_released_variable_mapping_ready_rows', '0')}; denominator_variant_ready={csv_value(alb2002_consumption_aggregate_summary, 'alb2002_consumption_aggregate_crosswalk_denominator_variant_ready_rows', '0')}; outcome_ready={csv_value(alb2002_consumption_aggregate_summary, 'alb2002_consumption_aggregate_crosswalk_outcome_ready_rows', '0')}; sdg382_ready={csv_value(alb2002_consumption_aggregate_summary, 'alb2002_consumption_aggregate_crosswalk_sdg382_ready_rows', '0')}; climate_ready={csv_value(alb2002_consumption_aggregate_summary, 'alb2002_consumption_aggregate_crosswalk_climate_linkage_ready_rows', '0')}",
        [TEMP_DIR / "alb2002_consumption_aggregate_metadata_crosswalk_audit.csv", RESULT_DIR / "alb2002_consumption_aggregate_metadata_crosswalk_summary.csv", REPORT_DIR / "alb2002_consumption_aggregate_metadata_crosswalk_audit.md"],
        "ALB_2002 aggregate crosswalk now verifies that candidate total_consumption exactly copies raw `totcons` and that public IHSN sources map it to the released `totcons3` total-budget variant. OOP numerator, SDG, and climate gates remain closed.",
    )
    add_bundle(
        rows,
        "climate_outcome_gate",
        "alb2002_period_aligned_che_policy_audit",
        csv_value(alb2002_period_aligned_che_summary, "alb2002_period_aligned_che_current_decision", "missing"),
        f"policy_rows={csv_value(alb2002_period_aligned_che_summary, 'alb2002_period_aligned_che_policy_rows', '0')}; household_rows={csv_value(alb2002_period_aligned_che_summary, 'alb2002_period_aligned_che_household_rows', '0')}; denominator_rows={csv_value(alb2002_period_aligned_che_summary, 'alb2002_period_aligned_che_denominator_rows', '0')}; period_alignment_ready={csv_value(alb2002_period_aligned_che_summary, 'alb2002_period_aligned_che_period_alignment_ready_rows', '0')}; combined_che10={csv_value(alb2002_period_aligned_che_summary, 'alb2002_period_aligned_che_combined_che10_rate', '')}; combined_che10_weighted={csv_value(alb2002_period_aligned_che_summary, 'alb2002_period_aligned_che_combined_che10_weighted_rate', '')}; combined_che25={csv_value(alb2002_period_aligned_che_summary, 'alb2002_period_aligned_che_combined_che25_rate', '')}; combined_che25_weighted={csv_value(alb2002_period_aligned_che_summary, 'alb2002_period_aligned_che_combined_che25_weighted_rate', '')}; outcome_ready={csv_value(alb2002_period_aligned_che_summary, 'alb2002_period_aligned_che_outcome_ready_rows', '0')}; climate_ready={csv_value(alb2002_period_aligned_che_summary, 'alb2002_period_aligned_che_climate_linkage_ready_rows', '0')}",
        [TEMP_DIR / "alb2002_period_aligned_che_policy_audit.csv", RESULT_DIR / "alb2002_period_aligned_che_policy_summary.csv", REPORT_DIR / "alb2002_period_aligned_che_policy_audit.md"],
        "ALB_2002 monthly-equivalent CHE stress tests align four-week and twelve-month OOP with the documented monthly total-budget denominator, but they remain non-promoted diagnostics.",
    )
    add_bundle(
        rows,
        "raw_verification_gate",
        "alb2002_minimum_recipe_promotion_packet",
        csv_value(alb2002_minimum_recipe_summary, "alb2002_minimum_recipe_promotion_current_decision", "missing"),
        f"action_rows={csv_value(alb2002_minimum_recipe_summary, 'alb2002_minimum_recipe_promotion_action_rows', '0')}; gate_rows={csv_value(alb2002_minimum_recipe_summary, 'alb2002_minimum_recipe_promotion_gate_rows', '0')}; blocked_gates={csv_value(alb2002_minimum_recipe_summary, 'alb2002_minimum_recipe_promotion_blocked_gates', '0')}; candidate_gates={csv_value(alb2002_minimum_recipe_summary, 'alb2002_minimum_recipe_promotion_candidate_gates', '0')}; harmonized_ready={csv_value(alb2002_minimum_recipe_summary, 'alb2002_minimum_recipe_promotion_harmonized_ready_rows', '0')}; outcome_ready={csv_value(alb2002_minimum_recipe_summary, 'alb2002_minimum_recipe_promotion_outcome_ready_rows', '0')}; sdg382_ready={csv_value(alb2002_minimum_recipe_summary, 'alb2002_minimum_recipe_promotion_sdg382_ready_rows', '0')}; climate_ready={csv_value(alb2002_minimum_recipe_summary, 'alb2002_minimum_recipe_promotion_climate_linkage_ready_rows', '0')}",
        [TEMP_DIR / "alb2002_minimum_recipe_promotion_action_queue.csv", TEMP_DIR / "alb2002_minimum_recipe_promotion_gate_checklist.csv", RESULT_DIR / "alb2002_minimum_recipe_promotion_summary.csv", REPORT_DIR / "alb2002_minimum_recipe_promotion_packet.md"],
        "ALB_2002 minimum-promotion packet consolidates the current top-ranked candidate into explicit household, outcome, SDG, and climate gates. It keeps harmonized, outcome, SDG 3.8.2, and climate-linkage promotion at zero.",
    )
    add_bundle(
        rows,
        "climate_outcome_gate",
        "alb2002_limited_harmonized_household_core",
        csv_value(alb2002_harmonized_core_summary, "alb2002_harmonized_household_core_current_decision", "missing"),
        f"rows={csv_value(alb2002_harmonized_core_summary, 'alb2002_harmonized_household_core_rows', '0')}; columns={csv_value(alb2002_harmonized_core_summary, 'alb2002_harmonized_household_core_columns', '0')}; identity_rows={csv_value(alb2002_harmonized_core_summary, 'alb2002_harmonized_household_core_identity_rows', '0')}; timing_rows={csv_value(alb2002_harmonized_core_summary, 'alb2002_harmonized_household_core_timing_rows', '0')}; weight_rows={csv_value(alb2002_harmonized_core_summary, 'alb2002_harmonized_household_core_weight_rows', '0')}; admin2_rows={csv_value(alb2002_harmonized_core_summary, 'alb2002_harmonized_household_core_admin2_rows', '0')}; coordinate_rows={csv_value(alb2002_harmonized_core_summary, 'alb2002_harmonized_household_core_coordinate_rows', '0')}; limited_data_write_ready={csv_value(alb2002_harmonized_core_summary, 'alb2002_harmonized_household_core_limited_data_write_ready_rows', '0')}; final_outcome_ready={csv_value(alb2002_harmonized_core_summary, 'alb2002_harmonized_household_core_final_outcome_ready_rows', '0')}; climate_ready={csv_value(alb2002_harmonized_core_summary, 'alb2002_harmonized_household_core_climate_linkage_ready_rows', '0')}; analysis_ready={csv_value(alb2002_harmonized_core_summary, 'alb2002_harmonized_household_core_analysis_ready_rows', '0')}",
        [DATA_DIR / "harmonized_household.csv", TEMP_DIR / "harmonization_audit.csv", TEMP_DIR / "harmonized_lineage.csv", TEMP_DIR / "alb2002_harmonized_household_core_promotion_audit.csv", RESULT_DIR / "alb2002_harmonized_household_core_promotion_summary.csv", REPORT_DIR / "alb2002_harmonized_household_core_promotion.md"],
        "ALB_2002 limited harmonized household core is written for inspection only and carries guardrail markers blocking final outcome, climate-linkage, and empirical-analysis use.",
    )
    add_bundle(
        rows,
        "climate_outcome_gate",
        "alb2002_limited_financial_outcome_promotion",
        csv_value(alb2002_limited_financial_summary, "alb2002_limited_financial_outcome_current_decision", "missing"),
        f"rows={csv_value(alb2002_limited_financial_summary, 'alb2002_limited_financial_outcome_rows', '0')}; che10_rows={csv_value(alb2002_limited_financial_summary, 'alb2002_limited_financial_outcome_che10_rows', '0')}; che10_weighted={csv_value(alb2002_limited_financial_summary, 'alb2002_limited_financial_outcome_che10_weighted_rate', '')}; che25_rows={csv_value(alb2002_limited_financial_summary, 'alb2002_limited_financial_outcome_che25_rows', '0')}; che25_weighted={csv_value(alb2002_limited_financial_summary, 'alb2002_limited_financial_outcome_che25_weighted_rate', '')}; limited_data_write_ready={csv_value(alb2002_limited_financial_summary, 'alb2002_limited_financial_outcome_limited_data_write_ready_rows', '0')}; sdg382_ready={csv_value(alb2002_limited_financial_summary, 'alb2002_limited_financial_outcome_sdg382_ready_rows', '0')}; access_ready={csv_value(alb2002_limited_financial_summary, 'alb2002_limited_financial_outcome_access_ready_rows', '0')}; composite_ready={csv_value(alb2002_limited_financial_summary, 'alb2002_limited_financial_outcome_composite_ready_rows', '0')}; climate_ready={csv_value(alb2002_limited_financial_summary, 'alb2002_limited_financial_outcome_climate_linkage_ready_rows', '0')}; analysis_ready={csv_value(alb2002_limited_financial_summary, 'alb2002_limited_financial_outcome_final_analysis_ready_rows', '0')}",
        [DATA_DIR / "household_outcomes.csv", RESULT_DIR / "outcome_audit.csv", TEMP_DIR / "outcome_construction_audit.csv", TEMP_DIR / "alb2002_limited_financial_outcome_promotion_audit.csv", RESULT_DIR / "alb2002_limited_financial_outcome_promotion_summary.csv", REPORT_DIR / "alb2002_limited_financial_outcome_promotion.md"],
        "ALB_2002 limited CHE10/CHE25 outcomes are written for financial-protection inspection only. SDG 3.8.2, access, composite UHC, climate-linkage, and empirical-analysis gates remain closed.",
    )
    add_bundle(
        rows,
        "climate_outcome_gate",
        "alb2002_limited_climate_exposure_promotion",
        csv_value(alb2002_limited_climate_summary, "alb2002_limited_climate_exposure_current_decision", "missing"),
        f"rows={csv_value(alb2002_limited_climate_summary, 'alb2002_limited_climate_exposure_rows', '0')}; districts={csv_value(alb2002_limited_climate_summary, 'alb2002_limited_climate_exposure_distinct_district_rows', '0')}; windows={csv_value(alb2002_limited_climate_summary, 'alb2002_limited_climate_exposure_window_rows', '0')}; precip_nonmissing={csv_value(alb2002_limited_climate_summary, 'alb2002_limited_climate_exposure_precip_nonmissing_rows', '0')}; temp_nonmissing={csv_value(alb2002_limited_climate_summary, 'alb2002_limited_climate_exposure_temp_nonmissing_rows', '0')}; precip_z={csv_value(alb2002_limited_climate_summary, 'alb2002_limited_climate_exposure_precip_z_rows', '0')}; temp_z={csv_value(alb2002_limited_climate_summary, 'alb2002_limited_climate_exposure_temp_z_rows', '0')}; limited_data_write_ready={csv_value(alb2002_limited_climate_summary, 'alb2002_limited_climate_exposure_limited_data_write_ready_rows', '0')}; chirps_ready={csv_value(alb2002_limited_climate_summary, 'alb2002_limited_climate_exposure_primary_chirps_ready_rows', '0')}; era5_ready={csv_value(alb2002_limited_climate_summary, 'alb2002_limited_climate_exposure_primary_era5_ready_rows', '0')}; baseline_ready={csv_value(alb2002_limited_climate_summary, 'alb2002_limited_climate_exposure_historical_baseline_ready_rows', '0')}; linkage_ready={csv_value(alb2002_limited_climate_summary, 'alb2002_limited_climate_exposure_climate_linkage_ready_rows', '0')}; analysis_ready={csv_value(alb2002_limited_climate_summary, 'alb2002_limited_climate_exposure_final_analysis_ready_rows', '0')}",
        [DATA_DIR / "climate_exposures_nasa_power.csv", TEMP_DIR / "climate_extraction_audit.csv", TEMP_DIR / "alb2002_limited_climate_exposure_promotion_audit.csv", RESULT_DIR / "alb2002_limited_climate_exposure_promotion_summary.csv", REPORT_DIR / "alb2002_limited_climate_exposure_promotion.md"],
        "ALB_2002 limited NASA POWER admin2-centroid exposure rows are promoted for fallback exposure inspection only. Final CHIRPS/ERA5, historical-baseline, climate-linkage, and causal-analysis gates remain closed.",
    )
    add_bundle(
        rows,
        "climate_outcome_gate",
        "alb2002_limited_climate_linked_promotion",
        csv_value(alb2002_limited_linked_summary, "alb2002_limited_climate_linked_current_decision", "missing"),
        f"rows={csv_value(alb2002_limited_linked_summary, 'alb2002_limited_climate_linked_rows', '0')}; households={csv_value(alb2002_limited_linked_summary, 'alb2002_limited_climate_linked_household_rows', '0')}; windows={csv_value(alb2002_limited_linked_summary, 'alb2002_limited_climate_linked_window_rows', '0')}; expected={csv_value(alb2002_limited_linked_summary, 'alb2002_limited_climate_linked_expected_rows', '0')}; climate_value_rows={csv_value(alb2002_limited_linked_summary, 'alb2002_limited_climate_linked_climate_value_rows', '0')}; unmatched={csv_value(alb2002_limited_linked_summary, 'alb2002_limited_climate_linked_unmatched_rows', '0')}; che10_long_rows={csv_value(alb2002_limited_linked_summary, 'alb2002_limited_climate_linked_che10_rows', '0')}; che25_long_rows={csv_value(alb2002_limited_linked_summary, 'alb2002_limited_climate_linked_che25_rows', '0')}; combined_stress={csv_value(alb2002_limited_linked_summary, 'alb2002_limited_climate_linked_combined_stress_rows', '0')}; limited_data_write_ready={csv_value(alb2002_limited_linked_summary, 'alb2002_limited_climate_linked_limited_data_write_ready_rows', '0')}; sdg382_ready={csv_value(alb2002_limited_linked_summary, 'alb2002_limited_climate_linked_sdg382_ready_rows', '0')}; access_ready={csv_value(alb2002_limited_linked_summary, 'alb2002_limited_climate_linked_access_ready_rows', '0')}; climate_linkage_ready={csv_value(alb2002_limited_linked_summary, 'alb2002_limited_climate_linked_climate_linkage_ready_rows', '0')}; descriptive_ready={csv_value(alb2002_limited_linked_summary, 'alb2002_limited_climate_linked_descriptive_ready_rows', '0')}; predictive_ready={csv_value(alb2002_limited_linked_summary, 'alb2002_limited_climate_linked_predictive_ml_ready_rows', '0')}; reduced_ready={csv_value(alb2002_limited_linked_summary, 'alb2002_limited_climate_linked_reduced_form_ready_rows', '0')}; robustness_ready={csv_value(alb2002_limited_linked_summary, 'alb2002_limited_climate_linked_robustness_ready_rows', '0')}; analysis_ready={csv_value(alb2002_limited_linked_summary, 'alb2002_limited_climate_linked_final_analysis_ready_rows', '0')}",
        [DATA_DIR / "climate_linked_household.csv", TEMP_DIR / "climate_merge_audit.csv", TEMP_DIR / "alb2002_limited_climate_linked_promotion_audit.csv", RESULT_DIR / "alb2002_limited_climate_linked_promotion_summary.csv", REPORT_DIR / "alb2002_limited_climate_linked_promotion.md"],
        "ALB_2002 limited household-window file links CHE10/CHE25 outcomes to NASA POWER admin2-centroid windows for audit only. Descriptive, predictive, reduced-form, robustness, causal ML, policy, and final-analysis gates remain closed.",
    )
    add_bundle(
        rows,
        "raw_verification_gate",
        "analysis_dataset_promotion_barrier_audit",
        csv_value(analysis_promotion_summary, "analysis_dataset_promotion_current_decision", "missing"),
        f"rows={csv_value(analysis_promotion_summary, 'analysis_dataset_promotion_audit_rows', '0')}; blocked={csv_value(analysis_promotion_summary, 'analysis_dataset_promotion_blocked_rows', '0')}; promoted={csv_value(analysis_promotion_summary, 'analysis_dataset_promotion_promoted_rows', '0')}; data_files={csv_value(analysis_promotion_summary, 'analysis_dataset_promotion_data_file_count', '0')}; verified_recipe_candidates={csv_value(analysis_promotion_summary, 'analysis_dataset_promotion_verified_recipe_candidates', '0')}; ready_country_waves={csv_value(analysis_promotion_summary, 'analysis_dataset_promotion_ready_country_waves', '0')}; alb2002_temp_core_rows={csv_value(analysis_promotion_summary, 'analysis_dataset_promotion_alb2002_temp_core_rows', '0')}; limited_core_rows={csv_value(analysis_promotion_summary, 'analysis_dataset_promotion_limited_harmonized_core_rows', '0')}; limited_core_data_write_ready={csv_value(analysis_promotion_summary, 'analysis_dataset_promotion_limited_harmonized_core_data_write_ready_rows', '0')}; limited_core_final_outcome_ready={csv_value(analysis_promotion_summary, 'analysis_dataset_promotion_limited_harmonized_core_final_outcome_ready_rows', '0')}; limited_financial_rows={csv_value(analysis_promotion_summary, 'analysis_dataset_promotion_limited_financial_outcome_rows', '0')}; limited_financial_che10={csv_value(analysis_promotion_summary, 'analysis_dataset_promotion_limited_financial_outcome_che10_rows', '0')}; limited_financial_che25={csv_value(analysis_promotion_summary, 'analysis_dataset_promotion_limited_financial_outcome_che25_rows', '0')}; limited_financial_sdg_access_composite_ready={csv_value(analysis_promotion_summary, 'analysis_dataset_promotion_limited_financial_outcome_sdg382_ready_rows', '0')}/{csv_value(analysis_promotion_summary, 'analysis_dataset_promotion_limited_financial_outcome_access_ready_rows', '0')}/{csv_value(analysis_promotion_summary, 'analysis_dataset_promotion_limited_financial_outcome_composite_ready_rows', '0')}; limited_financial_climate_ready={csv_value(analysis_promotion_summary, 'analysis_dataset_promotion_limited_financial_outcome_climate_linkage_ready_rows', '0')}; limited_climate_rows={csv_value(analysis_promotion_summary, 'analysis_dataset_promotion_limited_climate_exposure_rows', '0')}; limited_climate_data_write_ready={csv_value(analysis_promotion_summary, 'analysis_dataset_promotion_limited_climate_exposure_data_write_ready_rows', '0')}; limited_climate_linkage_ready={csv_value(analysis_promotion_summary, 'analysis_dataset_promotion_limited_climate_exposure_climate_linkage_ready_rows', '0')}; limited_linked_rows={csv_value(analysis_promotion_summary, 'analysis_dataset_promotion_limited_climate_linked_rows', '0')}; limited_linked_data_write_ready={csv_value(analysis_promotion_summary, 'analysis_dataset_promotion_limited_climate_linked_data_write_ready_rows', '0')}; limited_linked_descriptive_predictive_reduced_robust_analysis_ready={csv_value(analysis_promotion_summary, 'analysis_dataset_promotion_limited_climate_linked_descriptive_ready_rows', '0')}/{csv_value(analysis_promotion_summary, 'analysis_dataset_promotion_limited_climate_linked_predictive_ml_ready_rows', '0')}/{csv_value(analysis_promotion_summary, 'analysis_dataset_promotion_limited_climate_linked_reduced_form_ready_rows', '0')}/{csv_value(analysis_promotion_summary, 'analysis_dataset_promotion_limited_climate_linked_robustness_ready_rows', '0')}/{csv_value(analysis_promotion_summary, 'analysis_dataset_promotion_limited_climate_linked_analysis_ready_rows', '0')}; alb2002_harmonized_ready={csv_value(analysis_promotion_summary, 'analysis_dataset_promotion_alb2002_harmonized_ready_rows', '0')}; alb2002_outcome_ready={csv_value(analysis_promotion_summary, 'analysis_dataset_promotion_alb2002_outcome_ready_rows', '0')}; alb2002_climate_ready={csv_value(analysis_promotion_summary, 'analysis_dataset_promotion_alb2002_climate_linkage_ready_rows', '0')}",
        [TEMP_DIR / "analysis_dataset_promotion_barrier_audit.csv", RESULT_DIR / "analysis_dataset_promotion_barrier_summary.csv", REPORT_DIR / "analysis_dataset_promotion_barriers.md"],
        "Promotion audit allows the limited ALB_2002 harmonized household core, CHE-only financial outcomes, fallback climate exposure file, and linked diagnostic file, while keeping all descriptive/model-ready data blocked.",
    )
    add_bundle(
        rows,
        "design_gate",
        "current_design_scorecard",
        csv_value(design_scorecard_current_summary, "design_scorecard_current_decision", "missing"),
        f"scorecard_rows={csv_value(design_scorecard_current_summary, 'design_scorecard_rows', '0')}; current_rows={csv_value(design_scorecard_current_summary, 'design_scorecard_current_rows', '0')}; audit_rows={csv_value(design_scorecard_current_summary, 'design_scorecard_audit_rows', '0')}; no_go_thresholds={csv_value(design_scorecard_current_summary, 'design_no_go_threshold_rows', '0')}; failed_or_not_estimable={csv_value(design_scorecard_current_summary, 'design_no_go_failed_or_not_estimable_rows', '0')}; data_write_ready={csv_value(design_scorecard_current_summary, 'design_scorecard_data_write_ready_rows', '0')}",
        [RESULT_DIR / "design_scorecard.csv", RESULT_DIR / "design_scorecard_current_audit.csv", RESULT_DIR / "design_no_go_threshold_audit.csv", RESULT_DIR / "design_scorecard_current_summary.csv", REPORT_DIR / "design_scorecard_audit.md"],
        "Current scorecard preserves broad metadata rows, appends current fail-closed design rows, and records that estimation, transportable targeting, causal ML, policy learning, and descriptive-paper claims remain no-go.",
    )
    add_bundle(
        rows,
        "design_gate",
        "alb2002_promotion_gate_delta",
        csv_value(alb2002_promotion_gate_delta_summary, "alb2002_promotion_gate_delta_decision", "missing"),
        f"gate_rows={csv_value(alb2002_promotion_gate_delta_summary, 'alb2002_promotion_gate_delta_rows', '0')}; review_ready={csv_value(alb2002_promotion_gate_delta_summary, 'alb2002_promotion_gate_delta_review_ready_rows', '0')}; documented_candidate={csv_value(alb2002_promotion_gate_delta_summary, 'alb2002_promotion_gate_delta_documented_candidate_rows', '0')}; hard_blocked={csv_value(alb2002_promotion_gate_delta_summary, 'alb2002_promotion_gate_delta_hard_blocked_rows', '0')}; promotion_ready={csv_value(alb2002_promotion_gate_delta_summary, 'alb2002_promotion_gate_delta_promotion_ready_rows', '0')}; data_write_ready={csv_value(alb2002_promotion_gate_delta_summary, 'alb2002_promotion_gate_delta_data_write_ready_rows', '0')}",
        [TEMP_DIR / "alb2002_promotion_gate_delta_audit.csv", RESULT_DIR / "alb2002_promotion_gate_delta_summary.csv", REPORT_DIR / "alb2002_promotion_gate_delta_audit.md"],
        "ALB_2002 promotion delta separates evidence-rich review candidates from hard blockers while keeping all data writes and promoted analytical claims closed.",
    )
    add_bundle(
        rows,
        "design_gate",
        "alb2002_boundary_blocker_resolution",
        csv_value(alb2002_boundary_blocker_summary, "alb2002_boundary_blocker_current_decision", "missing"),
        f"matrix_rows={csv_value(alb2002_boundary_blocker_summary, 'alb2002_boundary_blocker_resolution_rows', '0')}; official_leads={csv_value(alb2002_boundary_blocker_summary, 'alb2002_boundary_blocker_official_or_primary_lead_rows', '0')}; candidate_name_coverage={csv_value(alb2002_boundary_blocker_summary, 'alb2002_boundary_blocker_candidate_name_coverage_rows', '0')}; incompatible_or_negative={csv_value(alb2002_boundary_blocker_summary, 'alb2002_boundary_blocker_incompatible_or_negative_rows', '0')}; historical_ready={csv_value(alb2002_boundary_blocker_summary, 'alb2002_boundary_blocker_historical_2002_ready_rows', '0')}; climate_ready={csv_value(alb2002_boundary_blocker_summary, 'alb2002_boundary_blocker_climate_linkage_ready_rows', '0')}; data_write_ready={csv_value(alb2002_boundary_blocker_summary, 'alb2002_boundary_blocker_data_write_ready_rows', '0')}",
        [TEMP_DIR / "alb2002_boundary_blocker_resolution_matrix.csv", RESULT_DIR / "alb2002_boundary_blocker_resolution_summary.csv", REPORT_DIR / "alb2002_boundary_blocker_resolution_matrix.md"],
        "ALB_2002 boundary matrix consolidates official, public, current-boundary, and negative evidence while keeping climate linkage and data writes closed.",
    )
    add_bundle(
        rows,
        "design_gate",
        "alb2002_outcome_blocker_resolution",
        csv_value(alb2002_outcome_blocker_summary, "alb2002_outcome_blocker_current_decision", "missing"),
        f"matrix_rows={csv_value(alb2002_outcome_blocker_summary, 'alb2002_outcome_blocker_resolution_rows', '0')}; financial={csv_value(alb2002_outcome_blocker_summary, 'alb2002_outcome_blocker_financial_rows', '0')}; access={csv_value(alb2002_outcome_blocker_summary, 'alb2002_outcome_blocker_access_rows', '0')}; composite={csv_value(alb2002_outcome_blocker_summary, 'alb2002_outcome_blocker_composite_rows', '0')}; candidate_not_promoted={csv_value(alb2002_outcome_blocker_summary, 'alb2002_outcome_blocker_candidate_not_promoted_rows', '0')}; hard_blocked={csv_value(alb2002_outcome_blocker_summary, 'alb2002_outcome_blocker_hard_blocked_rows', '0')}; outcome_ready={csv_value(alb2002_outcome_blocker_summary, 'alb2002_outcome_blocker_outcome_ready_rows', '0')}; data_write_ready={csv_value(alb2002_outcome_blocker_summary, 'alb2002_outcome_blocker_data_write_ready_rows', '0')}",
        [TEMP_DIR / "alb2002_outcome_blocker_resolution_matrix.csv", RESULT_DIR / "alb2002_outcome_blocker_resolution_summary.csv", REPORT_DIR / "alb2002_outcome_blocker_resolution_matrix.md"],
        "ALB_2002 outcome matrix consolidates CHE, access, composite, and SDG blocker evidence while keeping final outcome promotion and data writes closed.",
    )
    add_bundle(
        rows,
        "climate_outcome_gate",
        "alb2002_district_climate_crosswalk",
        csv_value(alb2002_crosswalk_summary, "alb2002_district_crosswalk_current_decision", "missing"),
        f"district_groups={csv_value(alb2002_crosswalk_summary, 'alb2002_district_crosswalk_district_rows', '0')}; household_rows={csv_value(alb2002_crosswalk_summary, 'alb2002_district_crosswalk_household_rows', '0')}; survey_month_rows={csv_value(alb2002_crosswalk_summary, 'alb2002_district_crosswalk_survey_month_rows', '0')}; interview_date_rows={csv_value(alb2002_crosswalk_summary, 'alb2002_district_crosswalk_interview_date_rows', '0')}; source_rows={csv_value(alb2002_crosswalk_summary, 'alb2002_district_crosswalk_boundary_source_rows', '0')}; source_reachable={csv_value(alb2002_crosswalk_summary, 'alb2002_district_crosswalk_boundary_source_reachable_rows', '0')}; climate_ready={csv_value(alb2002_crosswalk_summary, 'alb2002_climate_linkage_ready_rows', '0')}",
        [TEMP_DIR / "alb2002_district_climate_crosswalk_template.csv", TEMP_DIR / "alb2002_district_boundary_source_probe.csv", RESULT_DIR / "alb2002_district_climate_crosswalk_summary.csv", REPORT_DIR / "alb2002_district_climate_crosswalk_audit.md"],
        "ALB_2002 district names/codes are converted into a review template and public ADM2 boundary metadata is probed, but no polygons, centroids, GPS, verified historical crosswalk, climate linkage input, or exposure values are created.",
    )
    add_bundle(
        rows,
        "climate_outcome_gate",
        "alb2002_boundary_name_match_audit",
        csv_value(alb2002_boundary_name_summary, "alb2002_boundary_name_match_current_decision", "missing"),
        f"survey_districts={csv_value(alb2002_boundary_name_summary, 'alb2002_boundary_name_match_survey_district_rows', '0')}; boundary_features={csv_value(alb2002_boundary_name_summary, 'alb2002_boundary_name_match_geojson_feature_rows', '0')}; exact_matches={csv_value(alb2002_boundary_name_summary, 'alb2002_boundary_name_match_exact_rows', '0')}; repaired_matches={csv_value(alb2002_boundary_name_summary, 'alb2002_boundary_name_match_euro_repaired_rows', '0')}; unmatched_survey={csv_value(alb2002_boundary_name_summary, 'alb2002_boundary_name_match_unmatched_survey_rows', '0')}; duplicate_boundary_keys={csv_value(alb2002_boundary_name_summary, 'alb2002_boundary_name_match_duplicate_boundary_name_keys', '0')}; historical_ready={csv_value(alb2002_boundary_name_summary, 'alb2002_boundary_name_match_historical_year_ready_rows', '0')}; climate_ready={csv_value(alb2002_boundary_name_summary, 'alb2002_boundary_name_match_climate_linkage_ready_rows', '0')}",
        [TEMP_DIR / "alb2002_boundary_name_match_audit.csv", TEMP_DIR / "alb2002_boundary_geojson_inventory.csv", TEMP_DIR / "source_snapshots" / "alb2002_geoboundaries_alb_adm2_current.geojson", RESULT_DIR / "alb2002_boundary_name_match_summary.csv", REPORT_DIR / "alb2002_boundary_name_match_audit.md"],
        "ALB_2002 current public ADM2 boundary names were compared against survey district labels. Name evidence remains incomplete because KORCE is unmatched, duplicate current-boundary name keys exist, 2021 boundaries are not verified as 2002 districts, and no GPS support exists.",
    )
    add_bundle(
        rows,
        "climate_outcome_gate",
        "alb2002_boundary_source_alternatives_audit",
        csv_value(alb2002_boundary_source_summary, "alb2002_boundary_source_alternative_current_decision", "missing"),
        f"source_rows={csv_value(alb2002_boundary_source_summary, 'alb2002_boundary_source_alternative_rows', '0')}; reachable={csv_value(alb2002_boundary_source_summary, 'alb2002_boundary_source_alternative_reachable_rows', '0')}; current_or_post2015={csv_value(alb2002_boundary_source_summary, 'alb2002_boundary_source_alternative_current_or_post2015_rows', '0')}; lsms_maps_documented={csv_value(alb2002_boundary_source_summary, 'alb2002_boundary_source_alternative_lsms_maps_documented_rows', '0')}; gps_documented={csv_value(alb2002_boundary_source_summary, 'alb2002_boundary_source_alternative_gps_documented_rows', '0')}; historical_ready={csv_value(alb2002_boundary_source_summary, 'alb2002_boundary_source_alternative_historical_2002_boundary_ready_rows', '0')}; climate_ready={csv_value(alb2002_boundary_source_summary, 'alb2002_boundary_source_alternative_climate_linkage_ready_rows', '0')}",
        [TEMP_DIR / "alb2002_boundary_source_alternative_audit.csv", RESULT_DIR / "alb2002_boundary_source_alternative_summary.csv", REPORT_DIR / "alb2002_boundary_source_alternative_audit.md"],
        "ALB_2002 public/current/historical boundary-source alternatives were audited without GIS downloads. Source leads remain useful but not promotion-ready because no public 2001/2002 district/GPS boundary source is verified and joined to the 36 observed survey district groups.",
    )
    add_bundle(
        rows,
        "climate_outcome_gate",
        "alb2002_boundary_source_resource_search_audit",
        csv_value(alb2002_boundary_resource_summary, "alb2002_boundary_resource_search_current_decision", "missing"),
        f"candidate_resources={csv_value(alb2002_boundary_resource_summary, 'alb2002_boundary_resource_search_candidate_rows', '0')}; parseable={csv_value(alb2002_boundary_resource_summary, 'alb2002_boundary_resource_search_parseable_resource_rows', '0')}; complete_name_coverage={csv_value(alb2002_boundary_resource_summary, 'alb2002_boundary_resource_search_complete_name_coverage_rows', '0')}; exact_unit_count={csv_value(alb2002_boundary_resource_summary, 'alb2002_boundary_resource_search_exact_unit_count_rows', '0')}; best_candidate={csv_value(alb2002_boundary_resource_summary, 'alb2002_boundary_resource_search_best_candidate_id', 'missing')}; best_exact={csv_value(alb2002_boundary_resource_summary, 'alb2002_boundary_resource_search_best_candidate_exact_matches', '0')}; best_repaired={csv_value(alb2002_boundary_resource_summary, 'alb2002_boundary_resource_search_best_candidate_repaired_matches', '0')}; best_alias={csv_value(alb2002_boundary_resource_summary, 'alb2002_boundary_resource_search_best_candidate_alias_matches', '0')}; historical_ready={csv_value(alb2002_boundary_resource_summary, 'alb2002_boundary_resource_search_2002_historical_ready_rows', '0')}; climate_ready={csv_value(alb2002_boundary_resource_summary, 'alb2002_boundary_resource_search_climate_linkage_ready_rows', '0')}",
        [TEMP_DIR / "alb2002_boundary_source_resource_search_audit.csv", RESULT_DIR / "alb2002_boundary_source_resource_search_summary.csv", REPORT_DIR / "alb2002_boundary_source_resource_search_audit.md", TEMP_DIR / "source_snapshots" / "alb2002_geoboundaries_2_0_1_alb_adm2.geojson", TEMP_DIR / "source_snapshots" / "hdx_cod_ab_alb_package_show.json", TEMP_DIR / "source_snapshots" / "hdx_alb_adm_gazetteer_2019.xlsx"],
        "ALB_2002 public boundary resources were parsed directly. geoBoundaries 2.0.1 is the strongest name-coverage lead, but it remains blocked until boundary vintage, provenance, geometry validity, and raw district-code crosswalks are verified.",
    )
    add_bundle(
        rows,
        "climate_outcome_gate",
        "alb2002_boundary_geometry_provenance_audit",
        csv_value(alb2002_boundary_geometry_summary, "alb2002_boundary_geometry_current_decision", "missing"),
        f"features={csv_value(alb2002_boundary_geometry_summary, 'alb2002_boundary_geometry_feature_rows', '0')}; coordinate_structure_ok={csv_value(alb2002_boundary_geometry_summary, 'alb2002_boundary_geometry_coordinate_structure_ok_rows', '0')}; survey_key_matched={csv_value(alb2002_boundary_geometry_summary, 'alb2002_boundary_geometry_survey_key_matched_rows', '0')}; boundary_year={csv_value(alb2002_boundary_geometry_summary, 'alb2002_boundary_geometry_metadata_boundary_year', 'missing')}; boundary_update={csv_value(alb2002_boundary_geometry_summary, 'alb2002_boundary_geometry_metadata_boundary_update', 'missing')}; source={csv_value(alb2002_boundary_geometry_summary, 'alb2002_boundary_geometry_metadata_boundary_source', 'missing')}; year_matches_2002={csv_value(alb2002_boundary_geometry_summary, 'alb2002_boundary_geometry_boundary_year_matches_2002_rows', '0')}; topology_validated={csv_value(alb2002_boundary_geometry_summary, 'alb2002_boundary_geometry_topology_validated_rows', '0')}; historical_ready={csv_value(alb2002_boundary_geometry_summary, 'alb2002_boundary_geometry_historical_2002_boundary_ready_rows', '0')}; climate_ready={csv_value(alb2002_boundary_geometry_summary, 'alb2002_boundary_geometry_climate_linkage_ready_rows', '0')}",
        [TEMP_DIR / "alb2002_boundary_geometry_provenance_audit.csv", TEMP_DIR / "alb2002_boundary_metadata_provenance_probe.csv", RESULT_DIR / "alb2002_boundary_geometry_provenance_summary.csv", REPORT_DIR / "alb2002_boundary_geometry_provenance_audit.md", TEMP_DIR / "source_snapshots" / "alb2002_geoboundaries_2_0_1_alb_adm2_metadata.json"],
        "The best ALB_2002 boundary lead has parseable geometry and complete survey-key name coverage, but companion metadata reports boundaryYear 2013 and OpenStreetMap/Wambacher provenance, so it remains blocked for 2002 climate linkage.",
    )
    add_bundle(
        rows,
        "climate_outcome_gate",
        "alb2002_boundary_manual_verification_packet",
        csv_value(alb2002_boundary_manual_summary, "alb2002_boundary_manual_verification_current_decision", "missing"),
        f"actions={csv_value(alb2002_boundary_manual_summary, 'alb2002_boundary_manual_verification_action_rows', '0')}; gates={csv_value(alb2002_boundary_manual_summary, 'alb2002_boundary_manual_verification_gate_rows', '0')}; candidate_gates={csv_value(alb2002_boundary_manual_summary, 'alb2002_boundary_manual_verification_candidate_evidence_gates', '0')}; blocked_gates={csv_value(alb2002_boundary_manual_summary, 'alb2002_boundary_manual_verification_blocked_gates', '0')}; high_priority_actions={csv_value(alb2002_boundary_manual_summary, 'alb2002_boundary_manual_verification_high_priority_actions', '0')}; pre2011_digital_map_absence={csv_value(alb2002_boundary_manual_summary, 'alb2002_boundary_manual_verification_pre2011_digital_map_absence_rows', '0')}; climate_ready={csv_value(alb2002_boundary_manual_summary, 'alb2002_boundary_manual_verification_climate_linkage_ready_rows', '0')}",
        [TEMP_DIR / "alb2002_boundary_manual_verification_action_queue.csv", TEMP_DIR / "alb2002_boundary_promotion_gate_checklist.csv", RESULT_DIR / "alb2002_boundary_manual_verification_packet_summary.csv", REPORT_DIR / "alb2002_boundary_manual_verification_packet.md"],
        "The ALB_2002 geography blocker is now converted into source-specific manual actions and explicit promotion gates. The packet is actionable, but climate linkage remains blocked until those gates pass.",
    )
    add_bundle(
        rows,
        "climate_outcome_gate",
        "alb2002_boundary_manual_source_followup",
        csv_value(alb2002_boundary_followup_summary, "alb2002_boundary_manual_source_followup_current_decision", "missing"),
        f"followup_rows={csv_value(alb2002_boundary_followup_summary, 'alb2002_boundary_manual_source_followup_rows', '0')}; conclusive_blockers={csv_value(alb2002_boundary_followup_summary, 'alb2002_boundary_manual_source_followup_conclusive_blocker_rows', '0')}; district_ready={csv_value(alb2002_boundary_followup_summary, 'alb2002_boundary_manual_source_followup_district_level_ready_rows', '0')}; climate_ready={csv_value(alb2002_boundary_followup_summary, 'alb2002_boundary_manual_source_followup_climate_linkage_ready_rows', '0')}; ipums_status={csv_value(alb2002_boundary_followup_summary, 'alb2002_boundary_manual_source_followup_ipums_level_status', 'missing')}; unece_pre2011_map_status={csv_value(alb2002_boundary_followup_summary, 'alb2002_boundary_manual_source_followup_unece_pre2011_map_status', 'missing')}",
        [TEMP_DIR / "alb2002_boundary_manual_source_followup_audit.csv", RESULT_DIR / "alb2002_boundary_manual_source_followup_summary.csv", REPORT_DIR / "alb2002_boundary_manual_source_followup.md"],
        "Manual-source follow-up records source-specific blockers. IHGIS is downgraded to prefecture-level only, UNECE/INSTAT evidence documents pre-2011 national digital-map absence, and no public source is promoted for ALB_2002 climate linkage.",
    )
    add_bundle(
        rows,
        "climate_outcome_gate",
        "alb2002_gadm_boundary_lead_audit",
        csv_value(alb2002_gadm_summary, "alb2002_gadm_boundary_lead_current_decision", "missing"),
        f"candidates={csv_value(alb2002_gadm_summary, 'alb2002_gadm_boundary_lead_candidate_rows', '0')}; gadm36_rows={csv_value(alb2002_gadm_summary, 'alb2002_gadm36_adm2_row_count', '0')}; gadm36_keys={csv_value(alb2002_gadm_summary, 'alb2002_gadm36_distinct_normalized_key_count', '0')}; gadm36_district_rows={csv_value(alb2002_gadm_summary, 'alb2002_gadm36_engtype_district_rows', '0')}; gadm36_complete_name_coverage={csv_value(alb2002_gadm_summary, 'alb2002_gadm36_complete_name_coverage_rows', '0')}; gadm36_duplicate_keys={csv_value(alb2002_gadm_summary, 'alb2002_gadm36_duplicate_boundary_key_count', '0')}; historical_ready={csv_value(alb2002_gadm_summary, 'alb2002_gadm_boundary_lead_historical_2002_ready_rows', '0')}; climate_ready={csv_value(alb2002_gadm_summary, 'alb2002_gadm_boundary_lead_climate_linkage_ready_rows', '0')}",
        [
            TEMP_DIR / "alb2002_gadm_boundary_lead_audit.csv",
            TEMP_DIR / "alb2002_gadm_boundary_name_match_audit.csv",
            RESULT_DIR / "alb2002_gadm_boundary_lead_summary.csv",
            REPORT_DIR / "alb2002_gadm_boundary_lead_audit.md",
            TEMP_DIR / "source_snapshots" / "gadm36_ALB_shp.zip",
            TEMP_DIR / "source_snapshots" / "gadm41_ALB_shp.zip",
        ],
        "GADM 3.6 is a useful public district/Rreth lead, but duplicate SHKODER and missing official 2001/2002 provenance keep ALB_2002 climate linkage blocked.",
    )
    add_bundle(
        rows,
        "climate_outcome_gate",
        "alb2002_local_geography_artifact_audit",
        csv_value(alb2002_local_geo_summary, "alb2002_local_geo_artifact_current_decision", "missing"),
        f"files_scanned={csv_value(alb2002_local_geo_summary, 'alb2002_local_geo_artifact_files_scanned', '0')}; raw_coordinate_variables={csv_value(alb2002_local_geo_summary, 'alb2002_local_geo_artifact_coordinate_raw_variable_rows', '0')}; questionnaire_coordinate_fields={csv_value(alb2002_local_geo_summary, 'alb2002_local_geo_artifact_questionnaire_coordinate_field_rows', '0')}; admin_variables={csv_value(alb2002_local_geo_summary, 'alb2002_local_geo_artifact_admin_variable_rows', '0')}; local_coordinate_ready={csv_value(alb2002_local_geo_summary, 'alb2002_local_geo_artifact_local_coordinate_ready_rows', '0')}; local_boundary_ready={csv_value(alb2002_local_geo_summary, 'alb2002_local_geo_artifact_local_boundary_ready_rows', '0')}; climate_ready={csv_value(alb2002_local_geo_summary, 'alb2002_local_geo_artifact_climate_linkage_ready_rows', '0')}",
        [TEMP_DIR / "alb2002_local_geography_artifact_audit.csv", RESULT_DIR / "alb2002_local_geography_artifact_summary.csv", REPORT_DIR / "alb2002_local_geography_artifact_audit.md"],
        "ALB_2002 local package and questionnaire evidence show longitude/latitude fields and admin/sampling geography, but no raw coordinate variables, verified boundary artifact, or climate-linkage-ready row exists.",
    )
    add_bundle(
        rows,
        "raw_verification_gate",
        "alb2012_raw_core_feasibility",
        csv_value(alb2012_summary, "alb2012_raw_core_current_decision", "missing"),
        f"candidate_rows={csv_value(alb2012_summary, 'alb2012_household_core_candidate_rows', '0')}; consumption_rows={csv_value(alb2012_summary, 'alb2012_households_with_total_consumption', '0')}; weight_rows={csv_value(alb2012_summary, 'alb2012_households_with_household_weight', '0')}; oop4w_positive={csv_value(alb2012_summary, 'alb2012_households_with_oop_4w_positive', '0')}; access_affordability={csv_value(alb2012_summary, 'alb2012_households_with_access_affordability_proxy', '0')}; timing_rows={csv_value(alb2012_summary, 'alb2012_timing_signal_rows', '0')}; climate_ready={csv_value(alb2012_summary, 'alb2012_climate_linkage_ready_rows', '0')}",
        [TEMP_DIR / "alb2012_household_core_candidate.csv", TEMP_DIR / "alb2012_raw_core_feasibility_audit.csv", TEMP_DIR / "alb2012_raw_core_lineage.csv", RESULT_DIR / "alb2012_raw_core_feasibility_summary.csv", REPORT_DIR / "alb2012_raw_core_feasibility.md"],
        "ALB_2012 has a temp raw-core review candidate with consumption, weights, OOP/access proxies, and shocks, but no harmonization or climate linkage is promoted because interview timing is missing, geography is coarse prefecture/region only, GPS is absent, and value semantics are unreviewed.",
    )
    add_bundle(
        rows,
        "climate_outcome_gate",
        "alb2012_provisional_outcome_feasibility",
        csv_value(alb2012_outcome_summary, "alb2012_provisional_outcome_current_decision", "missing"),
        f"audit_rows={csv_value(alb2012_outcome_summary, 'alb2012_provisional_outcome_audit_rows', '0')}; financial_tests={csv_value(alb2012_outcome_summary, 'alb2012_provisional_financial_stress_test_rows', '0')}; access_proxies={csv_value(alb2012_outcome_summary, 'alb2012_provisional_access_proxy_rows', '0')}; need_proxies={csv_value(alb2012_outcome_summary, 'alb2012_provisional_need_proxy_rows', '0')}; low_event_rate={csv_value(alb2012_outcome_summary, 'alb2012_provisional_low_event_rate_rows', '0')}; ready={csv_value(alb2012_outcome_summary, 'alb2012_provisional_outcome_ready_rows', '0')}; climate_ready={csv_value(alb2012_outcome_summary, 'alb2012_provisional_climate_linkage_ready_rows', '0')}",
        [TEMP_DIR / "alb2012_provisional_outcome_feasibility_audit.csv", RESULT_DIR / "alb2012_provisional_outcome_feasibility_summary.csv", REPORT_DIR / "alb2012_provisional_outcome_feasibility.md"],
        "ALB_2012 raw OOP/access/need fields have provisional event-rate diagnostics, but no SDG 3.8.2, final CHE, climate-linked, descriptive, causal, ML, or policy outcome is constructed.",
    )
    add_bundle(
        rows,
        "climate_outcome_gate",
        "alb2012_outcome_semantics_raw_value_audit",
        csv_value(alb2012_semantics_summary, "alb2012_outcome_semantics_current_decision", "missing"),
        f"audit_rows={csv_value(alb2012_semantics_summary, 'alb2012_outcome_semantics_raw_value_audit_rows', '0')}; source_files={csv_value(alb2012_semantics_summary, 'alb2012_outcome_semantics_source_files_scanned', '0')}; oop_candidates={csv_value(alb2012_semantics_summary, 'alb2012_outcome_semantics_financial_oop_candidate_rows', '0')}; gift_candidates={csv_value(alb2012_semantics_summary, 'alb2012_outcome_semantics_gift_candidate_rows', '0')}; access_candidates={csv_value(alb2012_semantics_summary, 'alb2012_outcome_semantics_access_candidate_rows', '0')}; service_quality_proxies={csv_value(alb2012_semantics_summary, 'alb2012_outcome_semantics_service_quality_proxy_rows', '0')}; value_label_rows={csv_value(alb2012_semantics_summary, 'alb2012_outcome_semantics_rows_with_value_labels', '0')}; conditional_reason_rows={csv_value(alb2012_semantics_summary, 'alb2012_outcome_semantics_conditional_reason_rows', '0')}; outcome_ready={csv_value(alb2012_semantics_summary, 'alb2012_outcome_semantics_outcome_ready_rows', '0')}; sdg382_ready={csv_value(alb2012_semantics_summary, 'alb2012_outcome_semantics_sdg382_ready_rows', '0')}; climate_ready={csv_value(alb2012_semantics_summary, 'alb2012_outcome_semantics_climate_linkage_ready_rows', '0')}",
        [TEMP_DIR / "alb2012_outcome_semantics_raw_value_audit.csv", RESULT_DIR / "alb2012_outcome_semantics_raw_value_summary.csv", REPORT_DIR / "alb2012_outcome_semantics_raw_value_audit.md"],
        "ALB_2012 payment, gift, access, need, coping, and service-quality labels and values are audited. Promotion remains blocked by timing/geography, gift policy, units, recall periods, missing-code review, skip-pattern denominators, and service-quality proxy interpretation.",
    )
    add_bundle(
        rows,
        "climate_outcome_gate",
        "alb2012_timing_geography_exhaustive_audit",
        csv_value(alb2012_timing_geo_summary, "alb2012_timing_geography_current_decision", "missing"),
        f"audit_rows={csv_value(alb2012_timing_geo_summary, 'alb2012_timing_geography_audit_rows', '0')}; source_files={csv_value(alb2012_timing_geo_summary, 'alb2012_timing_geography_source_files_scanned', '0')}; interview_timing_verified={csv_value(alb2012_timing_geo_summary, 'alb2012_interview_timing_verified_rows', '0')}; coordinate_candidates={csv_value(alb2012_timing_geo_summary, 'alb2012_coordinate_candidate_rows', '0')}; coarse_geography_households={csv_value(alb2012_timing_geo_summary, 'alb2012_coarse_geography_household_rows', '0')}; climate_ready={csv_value(alb2012_timing_geo_summary, 'alb2012_climate_linkage_ready_rows', '0')}",
        [TEMP_DIR / "alb2012_timing_geography_exhaustive_audit.csv", RESULT_DIR / "alb2012_timing_geography_exhaustive_summary.csv", REPORT_DIR / "alb2012_timing_geography_exhaustive_audit.md"],
        "ALB_2012 raw timing/geography keywords were scanned. Interview month/date is not verified, no coordinate candidates were found, and the available geography is coarse prefecture/region/urban, so climate linkage remains blocked.",
    )
    add_bundle(
        rows,
        "climate_outcome_gate",
        "alb2012_questionnaire_timing_field_audit",
        csv_value(alb2012_questionnaire_timing_summary, "alb2012_questionnaire_timing_current_decision", "missing"),
        f"field_rows={csv_value(alb2012_questionnaire_timing_summary, 'alb2012_questionnaire_timing_field_rows', '0')}; raw_gap_rows={csv_value(alb2012_questionnaire_timing_summary, 'alb2012_questionnaire_timing_raw_gap_rows', '0')}; raw_control_candidates={csv_value(alb2012_questionnaire_timing_summary, 'alb2012_questionnaire_timing_raw_control_candidate_rows', '0')}; raw_verified_interview_timing={csv_value(alb2012_questionnaire_timing_summary, 'alb2012_questionnaire_timing_raw_verified_interview_timing_rows', '0')}; climate_ready={csv_value(alb2012_questionnaire_timing_summary, 'alb2012_questionnaire_timing_climate_linkage_ready_rows', '0')}",
        [TEMP_DIR / "alb2012_questionnaire_timing_field_audit.csv", TEMP_DIR / "alb2012_questionnaire_timing_raw_gap_audit.csv", RESULT_DIR / "alb2012_questionnaire_timing_field_summary.csv", REPORT_DIR / "alb2012_questionnaire_timing_field_audit.md"],
        "ALB_2012 questionnaire control sheets contain date/begin/end/status/visit fields, but raw household interview timing values are not verified in the SPSS modules, so climate windows remain blocked.",
    )
    add_bundle(
        rows,
        "climate_outcome_gate",
        "alb2012_timing_geography_blocker_resolution",
        csv_value(alb2012_blocker_summary, "alb2012_timing_geography_blocker_current_decision", "missing"),
        f"matrix_rows={csv_value(alb2012_blocker_summary, 'alb2012_timing_geography_blocker_resolution_rows', '0')}; timing={csv_value(alb2012_blocker_summary, 'alb2012_timing_geography_blocker_timing_rows', '0')}; geography={csv_value(alb2012_blocker_summary, 'alb2012_timing_geography_blocker_geography_rows', '0')}; outcome={csv_value(alb2012_blocker_summary, 'alb2012_timing_geography_blocker_outcome_rows', '0')}; promotion_gate={csv_value(alb2012_blocker_summary, 'alb2012_timing_geography_blocker_promotion_gate_rows', '0')}; hard_blocked={csv_value(alb2012_blocker_summary, 'alb2012_timing_geography_blocker_hard_blocked_rows', '0')}; timing_ready={csv_value(alb2012_blocker_summary, 'alb2012_timing_geography_blocker_interview_timing_ready_rows', '0')}; climate_ready={csv_value(alb2012_blocker_summary, 'alb2012_timing_geography_blocker_climate_linkage_ready_rows', '0')}; data_write_ready={csv_value(alb2012_blocker_summary, 'alb2012_timing_geography_blocker_data_write_ready_rows', '0')}",
        [TEMP_DIR / "alb2012_timing_geography_blocker_resolution_matrix.csv", RESULT_DIR / "alb2012_timing_geography_blocker_resolution_summary.csv", REPORT_DIR / "alb2012_timing_geography_blocker_resolution_matrix.md"],
        "ALB_2012 fallback matrix consolidates timing, geography, outcome, and first-analysis promotion evidence while keeping interview timing, climate linkage, and data writes closed.",
    )
    add_bundle(
        rows,
        "raw_verification_gate",
        "albania_legacy_questionnaire_readability",
        csv_value(albania_legacy_questionnaire_summary, "albania_legacy_questionnaire_current_decision", "missing"),
        f"present_files={csv_value(albania_legacy_questionnaire_summary, 'albania_legacy_questionnaire_present_files', '0')}; read_ok={csv_value(albania_legacy_questionnaire_summary, 'albania_legacy_questionnaire_read_ok_files', '0')}; missing_reader_blocked={csv_value(albania_legacy_questionnaire_summary, 'albania_legacy_questionnaire_missing_reader_blocked_files', '0')}; timing_ready={csv_value(albania_legacy_questionnaire_summary, 'albania_legacy_questionnaire_timing_content_audit_ready_rows', '0')}; climate_ready={csv_value(albania_legacy_questionnaire_summary, 'albania_legacy_questionnaire_climate_linkage_ready_rows', '0')}",
        [TEMP_DIR / "albania_legacy_questionnaire_readability_audit.csv", RESULT_DIR / "albania_legacy_questionnaire_readability_summary.csv", REPORT_DIR / "albania_legacy_questionnaire_readability_audit.md"],
        "ALB_2002/2005/2008 legacy .xls questionnaires are present and readable, but readability is only a prerequisite for a separate content audit.",
    )
    add_bundle(
        rows,
        "raw_verification_gate",
        "albania_legacy_questionnaire_timing_field_audit",
        csv_value(albania_legacy_questionnaire_timing_summary, "albania_legacy_questionnaire_timing_current_decision", "missing"),
        f"field_rows={csv_value(albania_legacy_questionnaire_timing_summary, 'albania_legacy_questionnaire_timing_field_rows', '0')}; raw_gap_rows={csv_value(albania_legacy_questionnaire_timing_summary, 'albania_legacy_questionnaire_timing_raw_gap_rows', '0')}; raw_verified_interview_timing={csv_value(albania_legacy_questionnaire_timing_summary, 'albania_legacy_questionnaire_timing_raw_verified_interview_timing_rows', '0')}; climate_ready={csv_value(albania_legacy_questionnaire_timing_summary, 'albania_legacy_questionnaire_timing_climate_linkage_ready_rows', '0')}",
        [TEMP_DIR / "albania_legacy_questionnaire_timing_field_audit.csv", TEMP_DIR / "albania_legacy_questionnaire_timing_raw_gap_audit.csv", RESULT_DIR / "albania_legacy_questionnaire_timing_field_summary.csv", REPORT_DIR / "albania_legacy_questionnaire_timing_field_audit.md"],
        "Legacy Albania questionnaire control fields document date/begin/end/status/visit form design; only ALB_2002 has verified raw interview timing so far, and climate linkage remains blocked.",
    )
    add_bundle(
        rows,
        "raw_verification_gate",
        "alb2005_documented_harmonization_review",
        csv_value(alb2005_summary, "alb2005_current_decision", "missing"),
        f"evidence_rows={csv_value(alb2005_summary, 'alb2005_documented_evidence_rows', '0')}; future_candidates={csv_value(alb2005_summary, 'alb2005_future_recipe_candidate_rows', '0')}; false_positives={csv_value(alb2005_summary, 'alb2005_false_positive_rows', '0')}; recipe_ready={csv_value(alb2005_summary, 'alb2005_recipe_ready_rows', '0')}",
        [TEMP_DIR / "alb2005_documented_variable_evidence.csv", RESULT_DIR / "alb2005_documented_harmonization_summary.csv", REPORT_DIR / "alb2005_documented_harmonization_review.md"],
        "ALB_2005 has documented candidates such as weight_retro, totcons, OOP payments, need/access variables, and district code, but remains not recipe-ready because timing/geography, OOP aggregation/recall, skip patterns, units, and merge keys are unresolved; fertility birth-weight variables are explicitly rejected as survey weights.",
    )
    add_bundle(
        rows,
        "raw_verification_gate",
        "alb2005_household_core_merge_audit",
        csv_value(alb2005_core_summary, "alb2005_household_core_current_decision", "missing"),
        f"candidate_rows={csv_value(alb2005_core_summary, 'alb2005_household_core_candidate_rows', '0')}; consumption_rows={csv_value(alb2005_core_summary, 'alb2005_households_with_total_consumption', '0')}; district_rows={csv_value(alb2005_core_summary, 'alb2005_households_with_partial_district_code', '0')}; survey_month_rows={csv_value(alb2005_core_summary, 'alb2005_households_with_survey_month', '0')}; recipe_ready={csv_value(alb2005_core_summary, 'alb2005_household_core_recipe_ready_rows', '0')}",
        [TEMP_DIR / "alb2005_household_core_candidate.csv", TEMP_DIR / "alb2005_household_core_merge_audit.csv", TEMP_DIR / "alb2005_household_core_lineage.csv", RESULT_DIR / "alb2005_household_core_candidate_summary.csv", REPORT_DIR / "alb2005_household_core_merge_audit.md"],
        "A temp-only ALB_2005 household core candidate exists for review, but it remains outside data/ because poverty coverage is partial, geography is partial/no-GPS, survey timing is missing, and OOP/access variables are unreviewed.",
    )
    add_bundle(
        rows,
        "climate_outcome_gate",
        "alb2005_provisional_outcome_feasibility",
        csv_value(alb2005_outcome_summary, "alb2005_provisional_outcome_current_decision", "missing"),
        f"audit_rows={csv_value(alb2005_outcome_summary, 'alb2005_provisional_outcome_audit_rows', '0')}; financial_tests={csv_value(alb2005_outcome_summary, 'alb2005_provisional_financial_stress_test_rows', '0')}; access_proxies={csv_value(alb2005_outcome_summary, 'alb2005_provisional_access_proxy_rows', '0')}; low_event_rate={csv_value(alb2005_outcome_summary, 'alb2005_provisional_low_event_rate_rows', '0')}; ready={csv_value(alb2005_outcome_summary, 'alb2005_provisional_outcome_ready_rows', '0')}",
        [TEMP_DIR / "alb2005_provisional_outcome_feasibility_audit.csv", RESULT_DIR / "alb2005_provisional_outcome_feasibility_summary.csv", REPORT_DIR / "alb2005_provisional_outcome_feasibility.md"],
        "ALB_2005 raw OOP/access fields have provisional event-rate diagnostics, but no SDG 3.8.2, final CHE, climate-linked, descriptive, causal, ML, or policy outcome is constructed.",
    )
    add_bundle(
        rows,
        "climate_outcome_gate",
        "alb2005_outcome_semantics_raw_value_audit",
        csv_value(alb2005_semantics_summary, "alb2005_outcome_semantics_current_decision", "missing"),
        f"audit_rows={csv_value(alb2005_semantics_summary, 'alb2005_outcome_semantics_raw_value_audit_rows', '0')}; source_files={csv_value(alb2005_semantics_summary, 'alb2005_outcome_semantics_source_files_scanned', '0')}; oop_candidates={csv_value(alb2005_semantics_summary, 'alb2005_outcome_semantics_financial_oop_candidate_rows', '0')}; gift_candidates={csv_value(alb2005_semantics_summary, 'alb2005_outcome_semantics_gift_candidate_rows', '0')}; access_candidates={csv_value(alb2005_semantics_summary, 'alb2005_outcome_semantics_access_candidate_rows', '0')}; value_label_rows={csv_value(alb2005_semantics_summary, 'alb2005_outcome_semantics_rows_with_value_labels', '0')}; conditional_reason_rows={csv_value(alb2005_semantics_summary, 'alb2005_outcome_semantics_conditional_reason_rows', '0')}; outcome_ready={csv_value(alb2005_semantics_summary, 'alb2005_outcome_semantics_outcome_ready_rows', '0')}; sdg382_ready={csv_value(alb2005_semantics_summary, 'alb2005_outcome_semantics_sdg382_ready_rows', '0')}; climate_ready={csv_value(alb2005_semantics_summary, 'alb2005_outcome_semantics_climate_linkage_ready_rows', '0')}",
        [TEMP_DIR / "alb2005_outcome_semantics_raw_value_audit.csv", RESULT_DIR / "alb2005_outcome_semantics_raw_value_summary.csv", REPORT_DIR / "alb2005_outcome_semantics_raw_value_audit.md"],
        "ALB_2005 raw health payment, gift, access, need, coping, and coverage labels and values have been audited; promotion remains blocked by timing/geography, gift policy, units, recall periods, missing-code review, and skip-pattern denominators.",
    )
    add_bundle(
        rows,
        "climate_outcome_gate",
        "alb2005_timing_geography_exhaustive_audit",
        csv_value(alb2005_timing_geo_summary, "alb2005_timing_geography_current_decision", "missing"),
        f"audit_rows={csv_value(alb2005_timing_geo_summary, 'alb2005_timing_geography_audit_rows', '0')}; interview_timing_verified={csv_value(alb2005_timing_geo_summary, 'alb2005_interview_timing_verified_rows', '0')}; coordinate_candidates={csv_value(alb2005_timing_geo_summary, 'alb2005_coordinate_candidate_rows', '0')}; district_name_rows={csv_value(alb2005_timing_geo_summary, 'alb2005_partial_district_name_nonmissing_rows', '0')}; district_code_rows={csv_value(alb2005_timing_geo_summary, 'alb2005_partial_district_code_nonmissing_rows', '0')}; climate_ready={csv_value(alb2005_timing_geo_summary, 'alb2005_climate_linkage_ready_rows', '0')}",
        [TEMP_DIR / "alb2005_timing_geography_exhaustive_audit.csv", RESULT_DIR / "alb2005_timing_geography_exhaustive_summary.csv", REPORT_DIR / "alb2005_timing_geography_exhaustive_audit.md"],
        "ALB_2005 raw timing/geography keywords were scanned. Interview month/date is not verified, no coordinate candidates were found, and district evidence is partial, so climate linkage remains blocked.",
    )
    add_bundle(
        rows,
        "climate_outcome_gate",
        "alb2005_timing_geography_source_search_audit",
        csv_value(alb2005_timing_geo_source_summary, "alb2005_timing_geography_source_search_current_decision", "missing"),
        f"rows={csv_value(alb2005_timing_geo_source_summary, 'alb2005_timing_geography_source_search_rows', '0')}; targets={csv_value(alb2005_timing_geo_source_summary, 'alb2005_timing_geography_source_search_target_concepts', '0')}; local_files={csv_value(alb2005_timing_geo_source_summary, 'alb2005_timing_geography_source_search_local_files_scanned', '0')}; local_variables={csv_value(alb2005_timing_geo_source_summary, 'alb2005_timing_geography_source_search_local_variables_scanned', '0')}; raw_hits={csv_value(alb2005_timing_geo_source_summary, 'alb2005_timing_geography_source_search_raw_targets_with_hits', '0')}; questionnaire_hits={csv_value(alb2005_timing_geo_source_summary, 'alb2005_timing_geography_source_search_questionnaire_targets_with_hits', '0')}; verified_timing={csv_value(alb2005_timing_geo_source_summary, 'alb2005_timing_geography_source_search_verified_household_timing_rows', '0')}; coordinates={csv_value(alb2005_timing_geo_source_summary, 'alb2005_timing_geography_source_search_coordinate_candidate_rows', '0')}; district_name_rows={csv_value(alb2005_timing_geo_source_summary, 'alb2005_timing_geography_source_search_partial_district_name_nonmissing_rows', '0')}; district_code_rows={csv_value(alb2005_timing_geo_source_summary, 'alb2005_timing_geography_source_search_partial_district_code_nonmissing_rows', '0')}; geography_ready={csv_value(alb2005_timing_geo_source_summary, 'alb2005_timing_geography_source_search_geography_crosswalk_ready_rows', '0')}; interview_ready={csv_value(alb2005_timing_geo_source_summary, 'alb2005_timing_geography_source_search_interview_timing_ready_rows', '0')}; climate_ready={csv_value(alb2005_timing_geo_source_summary, 'alb2005_timing_geography_source_search_climate_linkage_ready_rows', '0')}",
        [TEMP_DIR / "alb2005_timing_geography_source_search_audit.csv", RESULT_DIR / "alb2005_timing_geography_source_search_summary.csv", REPORT_DIR / "alb2005_timing_geography_source_search_audit.md"],
        "ALB_2005 timing/geography source-search evidence triangulates raw schema, local file inventory, questionnaires, and upstream audits. It finds raw/questionnaire leads but no verified household interview timing, no coordinates, and no promotion-ready geography crosswalk, so climate linkage remains blocked.",
    )
    add_bundle(
        rows,
        "raw_verification_gate",
        "alb2005_required_value_key_audit",
        csv_value(alb2005_required_value_key_summary, "alb2005_required_value_key_current_decision", "missing"),
        f"audit_rows={csv_value(alb2005_required_value_key_summary, 'alb2005_required_value_key_audit_rows', '0')}; total_consumption_nonmissing={csv_value(alb2005_required_value_key_summary, 'alb2005_required_value_key_total_consumption_nonmissing_rows', '0')}; oop4w_positive_households={csv_value(alb2005_required_value_key_summary, 'alb2005_required_value_key_oop_4w_household_positive_rows', '0')}; oop12m_positive_households={csv_value(alb2005_required_value_key_summary, 'alb2005_required_value_key_oop_12m_household_positive_rows', '0')}; district_code_nonmissing={csv_value(alb2005_required_value_key_summary, 'alb2005_required_value_key_district_code_nonmissing_rows', '0')}; timing_verified={csv_value(alb2005_required_value_key_summary, 'alb2005_required_value_key_interview_timing_verified_rows', '0')}; coordinate_ready={csv_value(alb2005_required_value_key_summary, 'alb2005_required_value_key_coordinate_ready_rows', '0')}; climate_ready={csv_value(alb2005_required_value_key_summary, 'alb2005_required_value_key_climate_linkage_ready_rows', '0')}; recipe_ready={csv_value(alb2005_required_value_key_summary, 'alb2005_required_value_key_recipe_ready_rows', '0')}",
        [TEMP_DIR / "alb2005_required_value_key_audit.csv", RESULT_DIR / "alb2005_required_value_key_summary.csv", REPORT_DIR / "alb2005_required_value_key_audit.md"],
        "ALB_2005 raw values are visible for keys, total consumption, OOP items, access barriers, weights, and partial district codes, but all recipe and climate-linkage promotion remains blocked by timing, geography, unit, recall, and skip-pattern gates.",
    )
    add_bundle(
        rows,
        "raw_verification_gate",
        "alb2005_health_questionnaire_semantics_audit",
        csv_value(alb2005_health_questionnaire_summary, "alb2005_health_questionnaire_current_decision", "missing"),
        f"rows={csv_value(alb2005_health_questionnaire_summary, 'alb2005_health_questionnaire_semantics_rows', '0')}; oop_items={csv_value(alb2005_health_questionnaire_summary, 'alb2005_health_questionnaire_oop_item_rows', '0')}; old_lek_rows={csv_value(alb2005_health_questionnaire_summary, 'alb2005_health_questionnaire_old_lek_unit_rows', '0')}; access_rows={csv_value(alb2005_health_questionnaire_summary, 'alb2005_health_questionnaire_access_rows', '0')}; cost_barrier_rows={csv_value(alb2005_health_questionnaire_summary, 'alb2005_health_questionnaire_cost_barrier_rows', '0')}; recipe_ready={csv_value(alb2005_health_questionnaire_summary, 'alb2005_health_questionnaire_recipe_ready_rows', '0')}; outcome_ready={csv_value(alb2005_health_questionnaire_summary, 'alb2005_health_questionnaire_outcome_ready_rows', '0')}; climate_ready={csv_value(alb2005_health_questionnaire_summary, 'alb2005_health_questionnaire_climate_linkage_ready_rows', '0')}",
        [TEMP_DIR / "alb2005_health_questionnaire_semantics_audit.csv", RESULT_DIR / "alb2005_health_questionnaire_semantics_summary.csv", REPORT_DIR / "alb2005_health_questionnaire_semantics_audit.md"],
        "ALB_2005 questionnaire text confirms old-lek OOP item units, recall separation, payment-scope exclusions, zero-payment instructions, and access-barrier codes, but recipe, outcome, and climate-linkage promotion remain blocked until raw skip paths, aggregation policy, timing, and geography pass.",
    )
    add_bundle(
        rows,
        "climate_outcome_gate",
        "alb2005_oop_aggregation_policy_audit",
        csv_value(alb2005_oop_policy_summary, "alb2005_oop_aggregation_policy_current_decision", "missing"),
        f"policy_rows={csv_value(alb2005_oop_policy_summary, 'alb2005_oop_aggregation_policy_rows', '0')}; households={csv_value(alb2005_oop_policy_summary, 'alb2005_oop_aggregation_policy_household_rows', '0')}; total_consumption_rows={csv_value(alb2005_oop_policy_summary, 'alb2005_oop_aggregation_policy_total_consumption_rows', '0')}; questionnaire_oop_rows={csv_value(alb2005_oop_policy_summary, 'alb2005_oop_aggregation_policy_questionnaire_oop_item_rows_observed', '0')}; old_lek_rows={csv_value(alb2005_oop_policy_summary, 'alb2005_oop_aggregation_policy_questionnaire_old_lek_rows_observed', '0')}; outcome_ready={csv_value(alb2005_oop_policy_summary, 'alb2005_oop_aggregation_policy_outcome_ready_rows', '0')}; recipe_ready={csv_value(alb2005_oop_policy_summary, 'alb2005_oop_aggregation_policy_recipe_ready_rows', '0')}; climate_ready={csv_value(alb2005_oop_policy_summary, 'alb2005_oop_aggregation_policy_climate_linkage_ready_rows', '0')}",
        [TEMP_DIR / "alb2005_oop_aggregation_policy_audit.csv", RESULT_DIR / "alb2005_oop_aggregation_policy_summary.csv", REPORT_DIR / "alb2005_oop_aggregation_policy_audit.md"],
        "ALB_2005 OOP aggregation policies are stress-tested against raw values and questionnaire payment-scope evidence, but these rows are not final CHE/SDG outcomes and remain blocked from recipe, outcome, and climate-linkage promotion.",
    )
    add_bundle(
        rows,
        "climate_outcome_gate",
        "alb2005_skip_missing_semantics_audit",
        csv_value(alb2005_skip_missing_summary, "alb2005_skip_missing_current_decision", "missing"),
        f"rows={csv_value(alb2005_skip_missing_summary, 'alb2005_skip_missing_semantics_rows', '0')}; payment_leaks={csv_value(alb2005_skip_missing_summary, 'alb2005_skip_missing_payment_nonmissing_when_not_triggered_rows', '0')}; payment_positive_leaks={csv_value(alb2005_skip_missing_summary, 'alb2005_skip_missing_payment_positive_when_not_triggered_rows', '0')}; condition_leaks={csv_value(alb2005_skip_missing_summary, 'alb2005_skip_missing_condition_nonmissing_when_not_triggered_rows', '0')}; condition_missing_when_triggered={csv_value(alb2005_skip_missing_summary, 'alb2005_skip_missing_condition_missing_when_triggered_rows', '0')}; financing_leaks={csv_value(alb2005_skip_missing_summary, 'alb2005_skip_missing_financing_nonmissing_when_not_triggered_rows', '0')}; financing_missing_when_triggered={csv_value(alb2005_skip_missing_summary, 'alb2005_skip_missing_financing_missing_when_triggered_rows', '0')}; recipe_ready={csv_value(alb2005_skip_missing_summary, 'alb2005_skip_missing_recipe_ready_rows', '0')}; outcome_ready={csv_value(alb2005_skip_missing_summary, 'alb2005_skip_missing_outcome_ready_rows', '0')}; climate_ready={csv_value(alb2005_skip_missing_summary, 'alb2005_skip_missing_climate_linkage_ready_rows', '0')}",
        [TEMP_DIR / "alb2005_skip_missing_semantics_audit.csv", RESULT_DIR / "alb2005_skip_missing_semantics_summary.csv", REPORT_DIR / "alb2005_skip_missing_semantics_audit.md"],
        "ALB_2005 raw trigger/downstream skip paths are audited for payment, access reason, and health-financing fields, but these rows remain outside recipes and final outcomes until units, zero/missing semantics, recall periods, timing, geography, and SDG denominator gates pass.",
    )
    add_bundle(
        rows,
        "climate_outcome_gate",
        "alb2005_consumption_oop_unit_period_audit",
        csv_value(alb2005_unit_period_summary, "alb2005_consumption_oop_unit_period_current_decision", "missing"),
        f"rows={csv_value(alb2005_unit_period_summary, 'alb2005_consumption_oop_unit_period_rows', '0')}; positive_totcons={csv_value(alb2005_unit_period_summary, 'alb2005_consumption_oop_unit_period_total_consumption_positive_rows', '0')}; positive_rcons={csv_value(alb2005_unit_period_summary, 'alb2005_consumption_oop_unit_period_rcons_positive_rows', '0')}; metadata_old_lek={csv_value(alb2005_unit_period_summary, 'alb2005_consumption_oop_unit_period_metadata_old_lek_rows_observed', '0')}; oop_old_lek={csv_value(alb2005_unit_period_summary, 'alb2005_consumption_oop_unit_period_oop_old_lek_questionnaire_rows_observed', '0')}; four_week_oop={csv_value(alb2005_unit_period_summary, 'alb2005_consumption_oop_unit_period_four_week_oop_rows_observed', '0')}; twelve_month_oop={csv_value(alb2005_unit_period_summary, 'alb2005_consumption_oop_unit_period_twelve_month_oop_rows_observed', '0')}; sdg_ready={csv_value(alb2005_unit_period_summary, 'alb2005_consumption_oop_unit_period_sdg382_ready_rows', '0')}; recipe_ready={csv_value(alb2005_unit_period_summary, 'alb2005_consumption_oop_unit_period_recipe_ready_rows', '0')}; outcome_ready={csv_value(alb2005_unit_period_summary, 'alb2005_consumption_oop_unit_period_outcome_ready_rows', '0')}; climate_ready={csv_value(alb2005_unit_period_summary, 'alb2005_consumption_oop_unit_period_climate_linkage_ready_rows', '0')}",
        [TEMP_DIR / "alb2005_consumption_oop_unit_period_audit.csv", RESULT_DIR / "alb2005_consumption_oop_unit_period_summary.csv", REPORT_DIR / "alb2005_consumption_oop_unit_period_audit.md"],
        "ALB_2005 now has explicit denominator-unit and recall-period evidence for total consumption and OOP items, but SDG 3.8.2, CHE outcomes, recipe promotion, and climate linkage remain blocked until total-consumption period, price basis, SPL/PPP/CPI, annualization, timing, and geography are verified.",
    )
    add_bundle(
        rows,
        "climate_outcome_gate",
        "alb2005_consumption_aggregate_metadata_crosswalk_audit",
        csv_value(alb2005_aggregate_crosswalk_summary, "alb2005_consumption_aggregate_crosswalk_current_decision", "missing"),
        f"rows={csv_value(alb2005_aggregate_crosswalk_summary, 'alb2005_consumption_aggregate_crosswalk_rows', '0')}; metadata_rows={csv_value(alb2005_aggregate_crosswalk_summary, 'alb2005_consumption_aggregate_crosswalk_metadata_rows', '0')}; local_poverty_columns={csv_value(alb2005_aggregate_crosswalk_summary, 'alb2005_consumption_aggregate_crosswalk_local_poverty_columns', '0')}; metadata_present_local={csv_value(alb2005_aggregate_crosswalk_summary, 'alb2005_consumption_aggregate_crosswalk_metadata_variables_present_in_local_raw_rows', '0')}; metadata_absent_local={csv_value(alb2005_aggregate_crosswalk_summary, 'alb2005_consumption_aggregate_crosswalk_metadata_variables_absent_from_local_raw_rows', '0')}; per_capita_components={csv_value(alb2005_aggregate_crosswalk_summary, 'alb2005_consumption_aggregate_crosswalk_local_per_capita_component_rows', '0')}; positive_totcons={csv_value(alb2005_aggregate_crosswalk_summary, 'alb2005_consumption_aggregate_crosswalk_totcons_positive_rows', '0')}; totcons05_local={csv_value(alb2005_aggregate_crosswalk_summary, 'alb2005_consumption_aggregate_crosswalk_totcons05_local_rows', '0')}; formula_reconstructable={csv_value(alb2005_aggregate_crosswalk_summary, 'alb2005_consumption_aggregate_crosswalk_component_formula_reconstructable_rows', '0')}; sdg_ready={csv_value(alb2005_aggregate_crosswalk_summary, 'alb2005_consumption_aggregate_crosswalk_sdg382_ready_rows', '0')}; recipe_ready={csv_value(alb2005_aggregate_crosswalk_summary, 'alb2005_consumption_aggregate_crosswalk_recipe_ready_rows', '0')}; outcome_ready={csv_value(alb2005_aggregate_crosswalk_summary, 'alb2005_consumption_aggregate_crosswalk_outcome_ready_rows', '0')}; climate_ready={csv_value(alb2005_aggregate_crosswalk_summary, 'alb2005_consumption_aggregate_crosswalk_climate_linkage_ready_rows', '0')}",
        [TEMP_DIR / "alb2005_consumption_aggregate_metadata_crosswalk_audit.csv", RESULT_DIR / "alb2005_consumption_aggregate_metadata_crosswalk_summary.csv", REPORT_DIR / "alb2005_consumption_aggregate_metadata_crosswalk_audit.md"],
        "ALB_2005 public metadata exposes old-lek aggregate/component variables, but local poverty.sav exposes only `totcons` from that checked formula set plus per-capita diagnostics; denominator reconstruction, `totcons05` variant choice, SDG 3.8.2, recipes, outcomes, and climate linkage remain blocked.",
    )
    add_bundle(
        rows,
        "climate_outcome_gate",
        "alb2005_consumption_component_source_search_audit",
        csv_value(alb2005_component_source_summary, "alb2005_consumption_component_source_search_current_decision", "missing"),
        f"rows={csv_value(alb2005_component_source_summary, 'alb2005_consumption_component_source_search_rows', '0')}; targets={csv_value(alb2005_component_source_summary, 'alb2005_consumption_component_source_search_target_variables', '0')}; local_files={csv_value(alb2005_component_source_summary, 'alb2005_consumption_component_source_search_local_files_scanned', '0')}; local_variables={csv_value(alb2005_component_source_summary, 'alb2005_consumption_component_source_search_local_variables_scanned', '0')}; exact_found={csv_value(alb2005_component_source_summary, 'alb2005_consumption_component_source_search_exact_target_variables_found', '0')}; exact_missing={csv_value(alb2005_component_source_summary, 'alb2005_consumption_component_source_search_exact_target_variables_missing', '0')}; label_phrase_targets={csv_value(alb2005_component_source_summary, 'alb2005_consumption_component_source_search_label_phrase_targets_found', '0')}; questionnaire_phrase_targets={csv_value(alb2005_component_source_summary, 'alb2005_consumption_component_source_search_questionnaire_phrase_targets_found', '0')}; construction_code_files={csv_value(alb2005_component_source_summary, 'alb2005_consumption_component_source_search_construction_code_files_found', '0')}; construction_code_targets={csv_value(alb2005_component_source_summary, 'alb2005_consumption_component_source_search_construction_code_targets_found', '0')}; sdg_ready={csv_value(alb2005_component_source_summary, 'alb2005_consumption_component_source_search_sdg382_ready_rows', '0')}; recipe_ready={csv_value(alb2005_component_source_summary, 'alb2005_consumption_component_source_search_recipe_ready_rows', '0')}; outcome_ready={csv_value(alb2005_component_source_summary, 'alb2005_consumption_component_source_search_outcome_ready_rows', '0')}; climate_ready={csv_value(alb2005_component_source_summary, 'alb2005_consumption_component_source_search_climate_linkage_ready_rows', '0')}",
        [TEMP_DIR / "alb2005_consumption_component_source_search_audit.csv", RESULT_DIR / "alb2005_consumption_component_source_search_summary.csv", REPORT_DIR / "alb2005_consumption_component_source_search_audit.md"],
        "ALB_2005 local raw/schema/questionnaire search finds only `totcons` as an exact public-metadata target variable and no local construction-code files; item/module leads remain manual review leads, not an outcome-ready denominator recipe.",
    )
    add_bundle(
        rows,
        "raw_verification_gate",
        "alb2005_minimum_recipe_promotion_packet",
        csv_value(alb2005_minimum_recipe_summary, "alb2005_minimum_recipe_promotion_current_decision", "missing"),
        f"action_rows={csv_value(alb2005_minimum_recipe_summary, 'alb2005_minimum_recipe_promotion_action_rows', '0')}; gate_rows={csv_value(alb2005_minimum_recipe_summary, 'alb2005_minimum_recipe_promotion_gate_rows', '0')}; blocked_gates={csv_value(alb2005_minimum_recipe_summary, 'alb2005_minimum_recipe_promotion_blocked_gates', '0')}; candidate_gates={csv_value(alb2005_minimum_recipe_summary, 'alb2005_minimum_recipe_promotion_candidate_gates', '0')}; harmonized_ready={csv_value(alb2005_minimum_recipe_summary, 'alb2005_minimum_recipe_promotion_harmonized_ready_rows', '0')}; outcome_ready={csv_value(alb2005_minimum_recipe_summary, 'alb2005_minimum_recipe_promotion_outcome_ready_rows', '0')}; climate_ready={csv_value(alb2005_minimum_recipe_summary, 'alb2005_minimum_recipe_promotion_climate_linkage_ready_rows', '0')}",
        [TEMP_DIR / "alb2005_minimum_recipe_promotion_action_queue.csv", TEMP_DIR / "alb2005_minimum_recipe_promotion_gate_checklist.csv", RESULT_DIR / "alb2005_minimum_recipe_promotion_summary.csv", REPORT_DIR / "alb2005_minimum_recipe_promotion_packet.md"],
        "The ALB_2005 raw-ready temp candidate is now mapped to explicit promotion gates. No harmonized household data, final outcomes, or climate-linkage rows are promoted until household frame, weights, denominator, OOP, access, timing, and geography gates pass.",
    )
    add_bundle(
        rows,
        "raw_verification_gate",
        "alb2005_public_fieldwork_geo_metadata_audit",
        csv_value(alb2005_public_fieldwork_geo_summary, "alb2005_public_fieldwork_geo_metadata_current_decision", "missing"),
        f"evidence_rows={csv_value(alb2005_public_fieldwork_geo_summary, 'alb2005_public_fieldwork_geo_metadata_evidence_rows', '0')}; verified_source_rows={csv_value(alb2005_public_fieldwork_geo_summary, 'alb2005_public_fieldwork_geo_metadata_verified_source_rows', '0')}; source_missing_rows={csv_value(alb2005_public_fieldwork_geo_summary, 'alb2005_public_fieldwork_geo_metadata_source_missing_rows', '0')}; fieldwork_rows={csv_value(alb2005_public_fieldwork_geo_summary, 'alb2005_public_fieldwork_geo_metadata_fieldwork_period_evidence_rows', '0')}; gps_claim_rows={csv_value(alb2005_public_fieldwork_geo_summary, 'alb2005_public_fieldwork_geo_metadata_gps_claim_rows', '0')}; sampling_geo_rows={csv_value(alb2005_public_fieldwork_geo_summary, 'alb2005_public_fieldwork_geo_metadata_sampling_geo_rows', '0')}; household_timing_verified={csv_value(alb2005_public_fieldwork_geo_summary, 'alb2005_public_fieldwork_geo_metadata_household_timing_verified_rows', '0')}; raw_coordinate_rows={csv_value(alb2005_public_fieldwork_geo_summary, 'alb2005_public_fieldwork_geo_metadata_raw_coordinate_value_rows', '0')}; climate_ready={csv_value(alb2005_public_fieldwork_geo_summary, 'alb2005_public_fieldwork_geo_metadata_climate_linkage_ready_rows', '0')}",
        [TEMP_DIR / "alb2005_public_fieldwork_geo_metadata_audit.csv", RESULT_DIR / "alb2005_public_fieldwork_geo_metadata_summary.csv", REPORT_DIR / "alb2005_public_fieldwork_geo_metadata_audit.md", TEMP_DIR / "source_snapshots" / "first_batch_public_documentation" / "1_ALB_2005_LSMS_v01_M" / "metadata_ddi_xml.xml"],
        "ALB_2005 public DDI metadata verifies the May to early-July 2005 main fieldwork window, October agriculture/community follow-up, sampling geography context, and a public GPS-collection claim. It still does not verify row-level household timing or raw coordinate values, so climate linkage remains blocked.",
    )
    add_bundle(
        rows,
        "raw_verification_gate",
        "alb2005_diary_timing_candidate_audit",
        csv_value(alb2005_diary_timing_summary, "alb2005_diary_timing_candidate_current_decision", "missing"),
        f"candidate_rows={csv_value(alb2005_diary_timing_summary, 'alb2005_diary_timing_candidate_audit_rows', '0')}; metadata_found_rows={csv_value(alb2005_diary_timing_summary, 'alb2005_diary_timing_candidate_metadata_found_rows', '0')}; schema_file_rows={csv_value(alb2005_diary_timing_summary, 'alb2005_diary_timing_candidate_schema_file_rows', '0')}; raw_bookmetadata_present={csv_value(alb2005_diary_timing_summary, 'alb2005_diary_timing_candidate_raw_bookmetadata_files_present', '0')}; key_candidate_rows={csv_value(alb2005_diary_timing_summary, 'alb2005_diary_timing_candidate_key_candidate_rows', '0')}; date_candidate_rows={csv_value(alb2005_diary_timing_summary, 'alb2005_diary_timing_candidate_date_candidate_rows', '0')}; household_timing_promoted={csv_value(alb2005_diary_timing_summary, 'alb2005_diary_timing_candidate_household_timing_promoted_rows', '0')}; climate_ready={csv_value(alb2005_diary_timing_summary, 'alb2005_diary_timing_candidate_climate_linkage_ready_rows', '0')}",
        [TEMP_DIR / "alb2005_diary_timing_candidate_audit.csv", RESULT_DIR / "alb2005_diary_timing_candidate_summary.csv", REPORT_DIR / "alb2005_diary_timing_candidate_audit.md", TEMP_DIR / "raw_schema_inventory" / "Albania_2005_ALB_2005_LSMS_v01_M" / "Albania_2005_ALB_2005_LSMS_v01_M_variable_catalog.csv"],
        "`bookmetadata_cl` exposes diary beginning/finishing day/month/year metadata candidates and key variables, but no raw bookmetadata file is present and diary dates are not accepted household interview timing until raw values, merge coverage, and protocol semantics pass.",
    )
    add_bundle(
        rows,
        "raw_verification_gate",
        "alb2005_extracted_module_coverage_audit",
        csv_value(alb2005_extracted_module_summary, "alb2005_extracted_module_coverage_current_decision", "missing"),
        f"ddi_modules={csv_value(alb2005_extracted_module_summary, 'alb2005_extracted_module_coverage_ddi_module_rows', '0')}; present={csv_value(alb2005_extracted_module_summary, 'alb2005_extracted_module_coverage_present_rows', '0')}; missing={csv_value(alb2005_extracted_module_summary, 'alb2005_extracted_module_coverage_missing_rows', '0')}; archive_members={csv_value(alb2005_extracted_module_summary, 'alb2005_archive_member_rows', '0')}; archive_sav={csv_value(alb2005_extracted_module_summary, 'alb2005_archive_sav_member_rows', '0')}; archive_absent={csv_value(alb2005_extracted_module_summary, 'alb2005_archive_ddi_module_absent_rows', '0')}; archive_critical_absent={csv_value(alb2005_extracted_module_summary, 'alb2005_archive_critical_module_absent_rows', '0')}; archive_listing={csv_value(alb2005_extracted_module_summary, 'alb2005_archive_listing_status', 'missing')}; extracted_files={csv_value(alb2005_extracted_module_summary, 'alb2005_extracted_module_coverage_extracted_file_rows', '0')}; bookmetadata_missing={csv_value(alb2005_extracted_module_summary, 'alb2005_extracted_module_coverage_bookmetadata_missing_rows', '0')}; food_diary_missing={csv_value(alb2005_extracted_module_summary, 'alb2005_extracted_module_coverage_food_diary_missing_rows', '0')}; critical_missing={csv_value(alb2005_extracted_module_summary, 'alb2005_extracted_module_coverage_critical_missing_rows', '0')}; coordinate_vars={csv_value(alb2005_extracted_module_summary, 'alb2005_extracted_module_coverage_coordinate_metadata_variable_rows', '0')}; coordinate_files={csv_value(alb2005_extracted_module_summary, 'alb2005_extracted_module_coverage_coordinate_extracted_file_rows', '0')}; climate_ready={csv_value(alb2005_extracted_module_summary, 'alb2005_extracted_module_coverage_climate_linkage_ready_rows', '0')}",
        [TEMP_DIR / "alb2005_extracted_module_coverage_audit.csv", TEMP_DIR / "alb2005_extracted_extra_files_audit.csv", TEMP_DIR / "alb2005_archive_member_manifest.csv", RESULT_DIR / "alb2005_extracted_module_coverage_summary.csv", REPORT_DIR / "alb2005_extracted_module_coverage_audit.md"],
        "The ALB_2005 local archive manifest and extracted folder both lack DDI `bookmetadata_cl`, food-diary modules, and coordinate evidence; this explains why diary timing and climate linkage remain blocked despite useful public metadata.",
    )
    add_bundle(
        rows,
        "raw_verification_gate",
        "alb2005_fallback_blocker_resolution_matrix",
        csv_value(alb2005_fallback_blocker_summary, "alb2005_fallback_blocker_current_decision", "missing"),
        f"rows={csv_value(alb2005_fallback_blocker_summary, 'alb2005_fallback_blocker_resolution_rows', '0')}; raw_package={csv_value(alb2005_fallback_blocker_summary, 'alb2005_fallback_blocker_raw_package_rows', '0')}; timing={csv_value(alb2005_fallback_blocker_summary, 'alb2005_fallback_blocker_timing_rows', '0')}; geography={csv_value(alb2005_fallback_blocker_summary, 'alb2005_fallback_blocker_geography_rows', '0')}; outcome={csv_value(alb2005_fallback_blocker_summary, 'alb2005_fallback_blocker_outcome_rows', '0')}; promotion_gate={csv_value(alb2005_fallback_blocker_summary, 'alb2005_fallback_blocker_promotion_gate_rows', '0')}; hard_blocked={csv_value(alb2005_fallback_blocker_summary, 'alb2005_fallback_blocker_hard_blocked_rows', '0')}; harmonized_ready={csv_value(alb2005_fallback_blocker_summary, 'alb2005_fallback_blocker_harmonized_ready_rows', '0')}; outcome_ready={csv_value(alb2005_fallback_blocker_summary, 'alb2005_fallback_blocker_outcome_ready_rows', '0')}; timing_ready={csv_value(alb2005_fallback_blocker_summary, 'alb2005_fallback_blocker_interview_timing_ready_rows', '0')}; geography_ready={csv_value(alb2005_fallback_blocker_summary, 'alb2005_fallback_blocker_geography_ready_rows', '0')}; climate_ready={csv_value(alb2005_fallback_blocker_summary, 'alb2005_fallback_blocker_climate_linkage_ready_rows', '0')}; data_ready={csv_value(alb2005_fallback_blocker_summary, 'alb2005_fallback_blocker_data_write_ready_rows', '0')}",
        [TEMP_DIR / "alb2005_fallback_blocker_resolution_matrix.csv", RESULT_DIR / "alb2005_fallback_blocker_resolution_summary.csv", REPORT_DIR / "alb2005_fallback_blocker_resolution_matrix.md"],
        "Consolidates ALB_2005 missing-module, public timing/GPS, diary-date, partial-geography, OOP/denominator/access, and fallback-promotion blockers into one fail-closed decision; all promoted readiness and data-write rows remain zero.",
    )
    add_bundle(
        rows,
        "raw_verification_gate",
        "albania_first_analysis_promotion_gate",
        csv_value(albania_first_analysis_summary, "albania_first_analysis_promotion_current_decision", "missing"),
        f"waves={csv_value(albania_first_analysis_summary, 'albania_first_analysis_promotion_wave_rows', '0')}; gates={csv_value(albania_first_analysis_summary, 'albania_first_analysis_promotion_gate_rows', '0')}; blocked_gates={csv_value(albania_first_analysis_summary, 'albania_first_analysis_promotion_blocked_gate_rows', '0')}; ready_waves={csv_value(albania_first_analysis_summary, 'albania_first_analysis_promotion_ready_wave_rows', '0')}; top_ranked={csv_value(albania_first_analysis_summary, 'albania_first_analysis_promotion_top_ranked_idno', '')}; top_blocker={csv_value(albania_first_analysis_summary, 'albania_first_analysis_promotion_top_ranked_primary_blocker', '')}",
        [TEMP_DIR / "albania_first_analysis_promotion_gate_checklist.csv", TEMP_DIR / "albania_first_analysis_promotion_action_queue.csv", RESULT_DIR / "albania_first_analysis_promotion_wave_ranking.csv", RESULT_DIR / "albania_first_analysis_promotion_summary.csv", REPORT_DIR / "albania_first_analysis_promotion_gate.md"],
        "Ranks local Albania raw waves for the first possible analytical dataset and keeps promotion blocked until harmonization, outcome, and climate-linkage gates pass.",
    )
    add_bundle(
        rows,
        "raw_verification_gate",
        "albania_existing_raw_wave_audit",
        csv_value(albania_wave_summary, "albania_existing_raw_wave_current_decision", "missing"),
        f"waves={csv_value(albania_wave_summary, 'albania_existing_raw_wave_rows', '0')}; archives={csv_value(albania_wave_summary, 'albania_existing_raw_wave_archive_present_rows', '0')}; extracted={csv_value(albania_wave_summary, 'albania_existing_raw_wave_extracted_rows', '0')}; unintegrated={csv_value(albania_wave_summary, 'albania_existing_raw_wave_unintegrated_rows', '0')}; raw_files={csv_value(albania_wave_summary, 'albania_existing_raw_wave_total_raw_tabular_files', '0')}; harmonization_ready={csv_value(albania_wave_summary, 'albania_existing_raw_wave_harmonization_ready_rows', '0')}; climate_ready={csv_value(albania_wave_summary, 'albania_existing_raw_wave_climate_linkage_ready_rows', '0')}",
        [TEMP_DIR / "albania_existing_raw_wave_audit.csv", RESULT_DIR / "albania_existing_raw_wave_audit_summary.csv", REPORT_DIR / "albania_existing_raw_wave_audit.md"],
        "Existing Albania waves remain promotion-blocked. ALB_2002 now has temp household-core, provisional outcome, raw outcome-semantics, district crosswalk, and boundary name-match diagnostics but no climate-linkage promotion; ALB_2005, ALB_2008, and ALB_2012 now have raw outcome-semantics diagnostics but no outcome, SDG, or climate-linkage promotion; ALB_2012 also has raw-core, provisional outcome, and timing/geography diagnostics but no timing/GPS climate support.",
    )
    add_bundle(
        rows,
        "raw_verification_gate",
        "alb2008_household_core_merge_audit",
        csv_value(alb2008_core_summary, "alb2008_household_core_current_decision", "missing"),
        f"candidate_rows={csv_value(alb2008_core_summary, 'alb2008_household_core_candidate_rows', '0')}; consumption_rows={csv_value(alb2008_core_summary, 'alb2008_households_with_total_consumption', '0')}; weight_rows={csv_value(alb2008_core_summary, 'alb2008_households_with_household_weight', '0')}; oop4w_positive={csv_value(alb2008_core_summary, 'alb2008_households_with_oop_4w_positive', '0')}; area_rows={csv_value(alb2008_core_summary, 'alb2008_households_with_coarse_area', '0')}; survey_month_rows={csv_value(alb2008_core_summary, 'alb2008_households_with_survey_month', '0')}; recipe_ready={csv_value(alb2008_core_summary, 'alb2008_household_core_recipe_ready_rows', '0')}",
        [TEMP_DIR / "alb2008_household_core_candidate.csv", TEMP_DIR / "alb2008_household_core_merge_audit.csv", TEMP_DIR / "alb2008_household_core_lineage.csv", RESULT_DIR / "alb2008_household_core_candidate_summary.csv", REPORT_DIR / "alb2008_household_core_merge_audit.md"],
        "A temp-only ALB_2008 household core candidate exists for review, but it remains outside data/ because timing, climate-ready geography, OOP/access semantics, and cross-wave comparability are unresolved.",
    )
    add_bundle(
        rows,
        "climate_outcome_gate",
        "alb2008_provisional_outcome_feasibility",
        csv_value(alb2008_outcome_summary, "alb2008_provisional_outcome_current_decision", "missing"),
        f"audit_rows={csv_value(alb2008_outcome_summary, 'alb2008_provisional_outcome_audit_rows', '0')}; financial_tests={csv_value(alb2008_outcome_summary, 'alb2008_provisional_financial_stress_test_rows', '0')}; access_proxies={csv_value(alb2008_outcome_summary, 'alb2008_provisional_access_proxy_rows', '0')}; low_event_rate={csv_value(alb2008_outcome_summary, 'alb2008_provisional_low_event_rate_rows', '0')}; ready={csv_value(alb2008_outcome_summary, 'alb2008_provisional_outcome_ready_rows', '0')}",
        [TEMP_DIR / "alb2008_provisional_outcome_feasibility_audit.csv", RESULT_DIR / "alb2008_provisional_outcome_feasibility_summary.csv", REPORT_DIR / "alb2008_provisional_outcome_feasibility.md"],
        "ALB_2008 raw OOP/access fields have provisional event-rate diagnostics, but no SDG 3.8.2, final CHE, climate-linked, descriptive, causal, ML, or policy outcome is constructed.",
    )
    add_bundle(
        rows,
        "climate_outcome_gate",
        "alb2008_outcome_semantics_raw_value_audit",
        csv_value(alb2008_semantics_summary, "alb2008_outcome_semantics_current_decision", "missing"),
        f"audit_rows={csv_value(alb2008_semantics_summary, 'alb2008_outcome_semantics_raw_value_audit_rows', '0')}; source_files={csv_value(alb2008_semantics_summary, 'alb2008_outcome_semantics_source_files_scanned', '0')}; oop_candidates={csv_value(alb2008_semantics_summary, 'alb2008_outcome_semantics_financial_oop_candidate_rows', '0')}; gift_candidates={csv_value(alb2008_semantics_summary, 'alb2008_outcome_semantics_gift_candidate_rows', '0')}; access_candidates={csv_value(alb2008_semantics_summary, 'alb2008_outcome_semantics_access_candidate_rows', '0')}; facility_proxies={csv_value(alb2008_semantics_summary, 'alb2008_outcome_semantics_facility_proxy_rows', '0')}; value_label_rows={csv_value(alb2008_semantics_summary, 'alb2008_outcome_semantics_rows_with_value_labels', '0')}; conditional_reason_rows={csv_value(alb2008_semantics_summary, 'alb2008_outcome_semantics_conditional_reason_rows', '0')}; outcome_ready={csv_value(alb2008_semantics_summary, 'alb2008_outcome_semantics_outcome_ready_rows', '0')}; sdg382_ready={csv_value(alb2008_semantics_summary, 'alb2008_outcome_semantics_sdg382_ready_rows', '0')}; climate_ready={csv_value(alb2008_semantics_summary, 'alb2008_outcome_semantics_climate_linkage_ready_rows', '0')}",
        [TEMP_DIR / "alb2008_outcome_semantics_raw_value_audit.csv", RESULT_DIR / "alb2008_outcome_semantics_raw_value_summary.csv", REPORT_DIR / "alb2008_outcome_semantics_raw_value_audit.md"],
        "ALB_2008 raw health payment, gift, access, need, coping, and service-quality labels and values have been audited; promotion remains blocked by timing/geography, gift policy, units, recall periods, missing-code review, skip-pattern denominators, and service-quality proxy interpretation.",
    )
    add_bundle(
        rows,
        "climate_outcome_gate",
        "alb2008_timing_geography_exhaustive_audit",
        csv_value(alb2008_timing_geo_summary, "alb2008_timing_geography_current_decision", "missing"),
        f"audit_rows={csv_value(alb2008_timing_geo_summary, 'alb2008_timing_geography_audit_rows', '0')}; interview_timing_verified={csv_value(alb2008_timing_geo_summary, 'alb2008_interview_timing_verified_rows', '0')}; coordinate_candidates={csv_value(alb2008_timing_geo_summary, 'alb2008_coordinate_candidate_rows', '0')}; coarse_geography_households={csv_value(alb2008_timing_geo_summary, 'alb2008_coarse_geography_household_rows', '0')}; climate_ready={csv_value(alb2008_timing_geo_summary, 'alb2008_climate_linkage_ready_rows', '0')}",
        [TEMP_DIR / "alb2008_timing_geography_exhaustive_audit.csv", RESULT_DIR / "alb2008_timing_geography_exhaustive_summary.csv", REPORT_DIR / "alb2008_timing_geography_exhaustive_audit.md"],
        "ALB_2008 raw timing/geography keywords were scanned. Interview month/date is not verified, no coordinate candidates were found, and the available geography is coarse survey area/stratum, so climate linkage remains blocked.",
    )
    add_bundle(
        rows,
        "climate_outcome_gate",
        "alb2008_fallback_blocker_resolution_matrix",
        csv_value(alb2008_fallback_blocker_summary, "alb2008_fallback_blocker_current_decision", "missing"),
        f"rows={csv_value(alb2008_fallback_blocker_summary, 'alb2008_fallback_blocker_resolution_rows', '0')}; timing={csv_value(alb2008_fallback_blocker_summary, 'alb2008_fallback_blocker_timing_rows', '0')}; geography={csv_value(alb2008_fallback_blocker_summary, 'alb2008_fallback_blocker_geography_rows', '0')}; outcome={csv_value(alb2008_fallback_blocker_summary, 'alb2008_fallback_blocker_outcome_rows', '0')}; promotion_gate={csv_value(alb2008_fallback_blocker_summary, 'alb2008_fallback_blocker_promotion_gate_rows', '0')}; hard_blocked={csv_value(alb2008_fallback_blocker_summary, 'alb2008_fallback_blocker_hard_blocked_rows', '0')}; timing_ready={csv_value(alb2008_fallback_blocker_summary, 'alb2008_fallback_blocker_interview_timing_ready_rows', '0')}; geography_ready={csv_value(alb2008_fallback_blocker_summary, 'alb2008_fallback_blocker_geography_ready_rows', '0')}; outcome_ready={csv_value(alb2008_fallback_blocker_summary, 'alb2008_fallback_blocker_outcome_ready_rows', '0')}; climate_ready={csv_value(alb2008_fallback_blocker_summary, 'alb2008_fallback_blocker_climate_linkage_ready_rows', '0')}; data_ready={csv_value(alb2008_fallback_blocker_summary, 'alb2008_fallback_blocker_data_write_ready_rows', '0')}",
        [TEMP_DIR / "alb2008_fallback_blocker_resolution_matrix.csv", RESULT_DIR / "alb2008_fallback_blocker_resolution_summary.csv", REPORT_DIR / "alb2008_fallback_blocker_resolution_matrix.md"],
        "Consolidates ALB_2008 missing interview timing, rejected non-interview timing hits, coarse non-GPS geography, provisional OOP/access semantics, and fallback-promotion blockers into one fail-closed decision; all promoted readiness and data-write rows remain zero.",
    )
    add_bundle(
        rows,
        "raw_verification_gate",
        "first_batch_raw_verification_workbook",
        "blocked_raw_microdata",
        f"dataset_gates={csv_value(first_batch_verification_summary, 'first_batch_dataset_gate_rows', '0')}; concept_rows={csv_value(first_batch_verification_summary, 'first_batch_concept_template_rows', '0')}; variable_rows={csv_value(first_batch_verification_summary, 'first_batch_variable_template_rows', '0')}; datasets_ready={csv_value(first_batch_verification_summary, 'datasets_ready_for_manual_value_audit', '0')}",
        [RESULT_DIR / "first_batch_dataset_verification_gate.csv", TEMP_DIR / "first_batch_concept_verification_template.csv", TEMP_DIR / "first_batch_variable_verification_template.csv", RESULT_DIR / "first_batch_raw_verification_workbook_summary.csv", REPORT_DIR / "first_batch_raw_verification_workbook.md"],
        "Post-download workbook for proving raw concept and variable evidence before any harmonization recipe or data output is promoted.",
    )
    add_bundle(
        rows,
        "coverage",
        "variable_maps",
        "metadata_only_requires_raw_verification" if variable_map_rows > 0 else "missing",
        str(variable_map_rows),
        variable_map_paths,
        "Candidate variable-map rows are metadata-derived and must not be treated as verified raw variables.",
    )

    ready_metrics = [
        ("harmonization_ready_country_waves", "result/harmonization_readiness_matrix.csv"),
        ("sdg382_ready_country_waves", "result/sdg382_denominator_country_wave_readiness.csv"),
        ("climate_ready_country_waves", "result/climate_linkage_readiness.csv"),
        ("outcome_ready_country_waves", "temp/outcome_denominator_plan.csv"),
        ("reduced_form_ready_country_waves", "temp/modeling_identification_plan.csv"),
        ("mechanism_ready_country_waves", "result/mechanism_readiness_matrix.csv"),
    ]
    for metric, artifact in ready_metrics:
        value = csv_value(empirical_summary, metric, "0")
        add_bundle(
            rows,
            "readiness",
            metric,
            "ready" if int_value(value) > 0 else "blocked_raw_microdata",
            value,
            [project_path(artifact)],
            "Country-wave rows ready at this gate. Zero means the project remains in metadata/protocol mode.",
        )

    add_bundle(
        rows,
        "go_no_go",
        "pre_specified_rules",
        "blocked_raw_microdata",
        f"pass={csv_value(empirical_summary, 'no_go_pass_rows', '0')}; blocked={csv_value(empirical_summary, 'no_go_blocked_rows', '0')}",
        [RESULT_DIR / "empirical_no_go_threshold_status.csv", REPORT_DIR / "empirical_readiness_dashboard.md"],
        "All current no-go rules are blocked or failing until raw microdata, outcome, climate, and validation gates pass.",
    )
    for row in no_go:
        add_bundle(
            rows,
            "go_no_go_rule",
            row.get("rule_id", ""),
            row.get("status", ""),
            row.get("current_value", ""),
            [RESULT_DIR / "empirical_no_go_threshold_status.csv"],
            f"{row.get('go_no_go_rule', '')} Next action: {row.get('next_action', '')}",
        )

    add_bundle(
        rows,
        "traceability",
        "completion_criteria",
        "incomplete",
        f"complete={completion_complete}; incomplete={completion_incomplete}",
        [RESULT_DIR / "completion_criteria_audit.csv"],
        "The project is not complete because analysis-ready data, outcomes, climate linkage, models, causal ML/policy learning, and robustness checks are absent.",
    )
    for row in completion:
        if row.get("status") != "incomplete":
            continue
        add_bundle(
            rows,
            "completion_gap",
            row.get("criterion", ""),
            row.get("status", ""),
            row.get("evidence", ""),
            [RESULT_DIR / "completion_criteria_audit.csv"],
            row.get("gap", ""),
        )

    add_bundle(
        rows,
        "traceability",
        "workspace_validation",
        "incomplete" if workspace_incomplete else "complete",
        f"complete={workspace_complete}; incomplete_or_failed={workspace_incomplete}; rows={len(workspace_validation)}",
        [RESULT_DIR / "workspace_validation_audit.csv", REPORT_DIR / "workspace_validation.md"],
        "Workspace validation is expected to remain incomplete only at the raw microdata gate while raw files are absent.",
    )
    add_bundle(
        rows,
        "traceability",
        "objective_traceability",
        "available" if objective_summary else "missing",
        f"summary_rows={len(objective_summary)}",
        [RESULT_DIR / "objective_traceability_summary.csv", REPORT_DIR / "objective_traceability_audit.md"],
        "Objective traceability maps pasted goal requirements to current evidence and guardrails.",
    )

    for row in dashboard[:10]:
        label = f"{row.get('bundle_rank', '')}: {row.get('country', '')} {row.get('wave', '')} {row.get('idno', '')}".strip()
        add_bundle(
            rows,
            "priority_bundle",
            label,
            row.get("current_stage", ""),
            row.get("analysis_claim_status", ""),
            [RESULT_DIR / "empirical_readiness_dashboard.csv"],
            row.get("next_blocking_action", ""),
        )

    manifest_counts = Counter(row["current_status"] for row in manifest)
    add_bundle(
        rows,
        "artifact_manifest",
        "curated_artifacts",
        "available" if manifest_counts.get("present_nonempty", 0) > 0 else "missing",
        f"present={manifest_counts.get('present_nonempty', 0)}; missing_or_empty={manifest_counts.get('missing_or_empty', 0)}",
        [MANIFEST_PATH],
        "Curated artifact manifest with row counts and checksums for direct reviewer/GPT intake.",
    )
    return rows


def build_summary(bundle: list[dict[str, str]], manifest: list[dict[str, str]]) -> list[dict[str, str]]:
    section_counts = Counter(row["section"] for row in bundle)
    status_counts = Counter(row["status"] for row in bundle)
    manifest_counts = Counter(row["current_status"] for row in manifest)
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
    alb2005_fallback_blocker_summary = read_csv_dicts(RESULT_DIR / "alb2005_fallback_blocker_resolution_summary.csv")
    alb2008_fallback_blocker_summary = read_csv_dicts(RESULT_DIR / "alb2008_fallback_blocker_resolution_summary.csv")
    promoted_data_gate_summary = read_csv_dicts(RESULT_DIR / "promoted_data_gate_summary.csv")
    priority_archive_summary = read_csv_dicts(RESULT_DIR / "priority_archive_member_preflight_summary.csv")
    priority_manual_verification_summary = read_csv_dicts(RESULT_DIR / "priority_manual_verification_decision_summary.csv")
    priority_receipt_summary = read_csv_dicts(RESULT_DIR / "priority_raw_package_receipt_summary.csv")
    priority_official_download_summary = read_csv_dicts(RESULT_DIR / "priority_official_download_dossier_summary.csv")
    priority_public_documentation_summary = read_csv_dicts(RESULT_DIR / "priority_public_documentation_receipt_summary.csv")
    priority_official_metadata_summary = read_csv_dicts(RESULT_DIR / "priority_official_metadata_evidence_summary.csv")
    priority_credentialed_acquisition_summary = read_csv_dicts(RESULT_DIR / "priority_credentialed_raw_acquisition_summary.csv")
    priority_endpoint_matrix_summary = read_csv_dicts(RESULT_DIR / "priority_official_endpoint_matrix_summary.csv")
    priority_core_file_endpoint_summary = read_csv_dicts(RESULT_DIR / "priority_core_file_endpoint_matrix_summary.csv")
    priority_threshold_campaign_summary = read_csv_dicts(RESULT_DIR / "priority_threshold_acquisition_campaign_summary.csv")
    priority_first_pass_summary = read_csv_dicts(RESULT_DIR / "priority_first_pass_variable_review_summary.csv")
    priority_download_execution_summary = read_csv_dicts(RESULT_DIR / "priority_download_execution_packet_summary.csv")
    priority_lsms_alignment_summary = read_csv_dicts(RESULT_DIR / "priority_lsms_isa_alignment_summary.csv")
    priority_lsms_refocused_summary = read_csv_dicts(RESULT_DIR / "priority_lsms_isa_refocused_acquisition_summary.csv")
    priority_lsms_public_docs_summary = read_csv_dicts(RESULT_DIR / "priority_lsms_isa_public_documentation_receipt_summary.csv")
    priority_lsms_variable_evidence_summary = read_csv_dicts(RESULT_DIR / "priority_lsms_isa_variable_evidence_summary.csv")
    priority_lsms_raw_intake_summary = read_csv_dicts(RESULT_DIR / "priority_lsms_isa_raw_package_intake_summary.csv")
    priority_lsms_archive_preflight_summary = read_csv_dicts(RESULT_DIR / "priority_lsms_isa_archive_member_preflight_summary.csv")
    priority_lsms_raw_value_workbook_summary = read_csv_dicts(RESULT_DIR / "priority_lsms_isa_raw_value_verification_workbook_summary.csv")
    priority_lsms_received_raw_schema_summary = read_csv_dicts(RESULT_DIR / "priority_lsms_isa_received_raw_schema_audit_summary.csv")
    priority_lsms_received_raw_value_profile_summary = read_csv_dicts(RESULT_DIR / "priority_lsms_isa_received_raw_value_profile_summary.csv")
    priority_lsms_received_raw_semantics_summary = read_csv_dicts(RESULT_DIR / "priority_lsms_isa_received_raw_semantics_review_summary.csv")
    mwi2004_raw_requirement_summary = read_csv_dicts(RESULT_DIR / "mwi2004_raw_requirement_verification_summary.csv")
    mwi2004_acceptance_summary = read_csv_dicts(RESULT_DIR / "mwi2004_requirement_acceptance_summary.csv")
    mwi2004_financial_policy_summary = read_csv_dicts(RESULT_DIR / "mwi2004_financial_protection_construction_policy_summary.csv")
    mwi2004_sdg382_parameter_summary = read_csv_dicts(RESULT_DIR / "mwi2004_sdg382_discretionary_budget_parameter_summary.csv")
    mwi2004_sdg382_external_parameter_summary = read_csv_dicts(RESULT_DIR / "mwi2004_sdg382_external_parameter_candidate_summary.csv")
    mwi2004_sdg382_candidate_precheck_summary = read_csv_dicts(RESULT_DIR / "mwi2004_sdg382_candidate_classification_precheck_summary.csv")
    mwi2004_sdg382_denominator_rule_summary = read_csv_dicts(RESULT_DIR / "mwi2004_sdg382_official_denominator_rule_summary.csv")
    mwi2004_timing_geography_summary = read_csv_dicts(RESULT_DIR / "mwi2004_timing_geography_linkage_policy_summary.csv")
    mwi2004_chirps_route_summary = read_csv_dicts(RESULT_DIR / "mwi2004_chirps_admin2_route_policy_summary.csv")
    mwi2004_chirps_extraction_summary = read_csv_dicts(RESULT_DIR / "mwi2004_chirps_admin2_extraction_summary.csv")
    mwi2004_health_access_summary = read_csv_dicts(RESULT_DIR / "mwi2004_health_access_label_skip_summary.csv")
    mwi2004_health_exception_summary = read_csv_dicts(RESULT_DIR / "mwi2004_health_exception_summary.csv")
    mwi2004_health_policy_summary = read_csv_dicts(RESULT_DIR / "mwi2004_health_access_construction_policy_summary.csv")
    mwi2004_access_resolution_summary = read_csv_dicts(RESULT_DIR / "mwi2004_access_person_key_resolution_policy_summary.csv")
    mwi2004_missing_units_summary = read_csv_dicts(RESULT_DIR / "mwi2004_missing_units_recall_skip_policy_summary.csv")
    mwi2004_promoted_dataset_summary = read_csv_dicts(RESULT_DIR / "mwi2004_promoted_household_climate_dataset_summary.csv")
    priority_lsms_receipt_checklist_summary = read_csv_dicts(RESULT_DIR / "priority_lsms_isa_raw_package_receipt_checklist_summary.csv")
    priority_lsms_credentialed_workbench_summary = read_csv_dicts(RESULT_DIR / "priority_lsms_isa_credentialed_raw_acquisition_workbench_summary.csv")
    priority_lsms_official_file_receipt_summary = read_csv_dicts(RESULT_DIR / "priority_lsms_isa_official_file_receipt_validator_summary.csv")
    priority_lsms_threshold_sequence_summary = read_csv_dicts(RESULT_DIR / "priority_lsms_isa_threshold_download_sequence_summary.csv")
    priority_lsms_minimum_intake_summary = read_csv_dicts(RESULT_DIR / "priority_lsms_isa_minimum_batch_raw_intake_guide_summary.csv")
    priority_lsms_minimum_endpoint_summary = read_csv_dicts(RESULT_DIR / "priority_lsms_isa_minimum_batch_endpoint_refresh_summary.csv")
    priority_lsms_next_raw_package_summary = read_csv_dicts(RESULT_DIR / "priority_lsms_isa_next_raw_package_action_summary.csv")
    priority_lsms_incoming_router_summary = read_csv_dicts(RESULT_DIR / "priority_lsms_isa_incoming_raw_package_router_summary.csv")
    priority_lsms_threshold_gap_summary = read_csv_dicts(RESULT_DIR / "priority_lsms_isa_threshold_gap_control_panel_summary.csv")
    priority_lsms_manual_download_packet_summary = read_csv_dicts(RESULT_DIR / "priority_lsms_isa_manual_download_packet_summary.csv")
    priority_lsms_manual_download_progress_summary = read_csv_dicts(RESULT_DIR / "priority_lsms_isa_manual_download_progress_summary.csv")
    priority_lsms_post_download_validation_summary = read_csv_dicts(RESULT_DIR / "priority_lsms_isa_post_download_validation_runner_summary.csv")
    priority_lsms_manual_download_execution_board_summary = read_csv_dicts(RESULT_DIR / "priority_lsms_isa_manual_download_execution_board_summary.csv")
    priority_lsms_credentialed_download_handoff_summary = read_csv_dicts(RESULT_DIR / "priority_lsms_isa_credentialed_download_handoff_summary.csv")
    priority_lsms_promotion_gate_summary = read_csv_dicts(RESULT_DIR / "priority_lsms_isa_promotion_gate_dashboard_summary.csv")
    priority_lsms_unlock_summary = read_csv_dicts(RESULT_DIR / "priority_lsms_isa_minimum_batch_promotion_unlock_summary.csv")
    priority_lsms_worldbank_session_summary = read_csv_dicts(RESULT_DIR / "priority_lsms_isa_worldbank_session_bootstrap_summary.csv")
    priority_lsms_fetch_command_summary = read_csv_dicts(RESULT_DIR / "priority_lsms_isa_credentialed_fetch_command_packet_summary.csv")
    priority_lsms_browser_starter_summary = read_csv_dicts(RESULT_DIR / "priority_lsms_isa_browser_download_starter_summary.csv")
    priority_lsms_first_canary_summary = read_csv_dicts(RESULT_DIR / "priority_lsms_isa_first_canary_runbook_summary.csv")
    priority_lsms_raw_presence_summary = read_csv_dicts(RESULT_DIR / "priority_lsms_isa_local_raw_presence_summary.csv")
    priority_lsms_handoff_summary = read_csv_dicts(RESULT_DIR / "priority_lsms_isa_acquisition_to_promotion_handoff_summary.csv")
    priority_lsms_scope_lock_summary = read_csv_dicts(RESULT_DIR / "priority_lsms_isa_dataset_scope_lock_summary.csv")
    priority_lsms_acquisition_route_summary = read_csv_dicts(RESULT_DIR / "priority_lsms_isa_acquisition_route_decision_summary.csv")
    priority_lsms_scoped_incoming_summary = read_csv_dicts(RESULT_DIR / "priority_lsms_isa_scoped_incoming_package_router_summary.csv")
    priority_lsms_webgpt_download_summary = read_csv_dicts(RESULT_DIR / "priority_lsms_isa_webgpt_download_control_summary.csv")
    priority_synthesis_summary = read_csv_dicts(RESULT_DIR / "priority_analysis_dataset_synthesis_blueprint_summary.csv")
    priority_packet_summary = read_csv_dicts(RESULT_DIR / "priority_country_wave_promotion_packet_summary.csv")
    priority_lsms_packet_summary = read_csv_dicts(RESULT_DIR / "priority_lsms_isa_country_wave_promotion_packet_summary.csv")
    data_dataset_files = [
        path for path in DATA_DIR.rglob("*")
        if path.is_file() and path.name not in {"README.md", ".gitkeep"}
    ]
    rows = [
        {"metric": "bundle_rows", "value": str(len(bundle)), "interpretation": "Rows in result/direct_read_audit_bundle.csv."},
        {"metric": "manifest_rows", "value": str(len(manifest)), "interpretation": "Curated artifact rows in result/direct_read_artifact_manifest.csv."},
        {"metric": "manifest_present_nonempty", "value": str(manifest_counts.get("present_nonempty", 0)), "interpretation": "Curated artifacts present and non-empty."},
        {"metric": "manifest_missing_or_empty", "value": str(manifest_counts.get("missing_or_empty", 0)), "interpretation": "Curated artifacts missing or empty."},
        {"metric": "raw_file_inventory_rows", "value": str(row_count(TEMP_DIR / "raw_schema_inventory" / "raw_file_inventory.csv")), "interpretation": "Raw tabular files inspected."},
        {"metric": "raw_variable_catalog_rows", "value": str(row_count(TEMP_DIR / "raw_schema_inventory" / "raw_variable_catalog.csv")), "interpretation": "Raw variables inspected."},
        {"metric": "analysis_ready_data_files", "value": str(len(data_dataset_files)), "interpretation": "Dataset-like files currently present in data/, excluding README/.gitkeep."},
        {"metric": "promoted_data_gate_status", "value": csv_value(promoted_data_gate_summary, "promoted_data_gate_status", "missing"), "interpretation": "Current promoted-data write gate status."},
        {"metric": "promoted_data_gate_registry_promoted_rows", "value": csv_value(promoted_data_gate_summary, "registry_promoted_analysis_ready_rows", "0"), "interpretation": "Registry rows currently allowed to write promoted datasets into data/."},
        {"metric": "promoted_data_gate_quarantined_files", "value": csv_value(promoted_data_gate_summary, "quarantined_diagnostic_data_files", "0"), "interpretation": "Pre-promotion diagnostic files moved from data/ to temp/."},
        {"metric": "priority_lsms_isa_public_documentation_dataset_rows", "value": csv_value(priority_lsms_public_docs_summary, "priority_lsms_isa_public_documentation_dataset_rows", "0"), "interpretation": "Refocused LSMS/ISA waves covered by the public documentation receipt."},
        {"metric": "priority_lsms_isa_public_documentation_core_complete_rows", "value": csv_value(priority_lsms_public_docs_summary, "priority_lsms_isa_public_documentation_core_complete_dataset_rows", "0"), "interpretation": "Refocused LSMS/ISA waves with all core public metadata/documentation resources saved."},
        {"metric": "priority_lsms_isa_public_documentation_file_inventory_rows", "value": csv_value(priority_lsms_public_docs_summary, "priority_lsms_isa_public_documentation_file_inventory_rows", "0"), "interpretation": "Official DDI file-description rows extracted into a compact GPT-readable table."},
        {"metric": "priority_lsms_isa_public_documentation_access_gate_rows", "value": csv_value(priority_lsms_public_docs_summary, "priority_lsms_isa_public_documentation_access_gate_rows", "0"), "interpretation": "Refocused LSMS/ISA waves whose official get-microdata page still shows credentialed access language."},
        {"metric": "priority_lsms_isa_variable_evidence_candidate_rows", "value": csv_value(priority_lsms_variable_evidence_summary, "priority_lsms_variable_evidence_candidate_variable_rows", "0"), "interpretation": "Concept-level official metadata candidate variables shortlisted for raw review."},
        {"metric": "priority_lsms_isa_variable_evidence_requirement_rows", "value": csv_value(priority_lsms_variable_evidence_summary, "priority_lsms_variable_evidence_requirement_rows", "0"), "interpretation": "Requirement-by-wave variable evidence coverage rows."},
        {"metric": "priority_lsms_isa_variable_evidence_file_shortlist_rows", "value": csv_value(priority_lsms_variable_evidence_summary, "priority_lsms_variable_evidence_file_shortlist_rows", "0"), "interpretation": "Official DDI files shortlisted by concept for raw package checking."},
        {"metric": "priority_lsms_isa_raw_value_workbook_requirement_rows", "value": csv_value(priority_lsms_raw_value_workbook_summary, "priority_lsms_raw_value_workbook_requirement_rows", "0"), "interpretation": "Requirement-level raw value verification workbook rows."},
        {"metric": "priority_lsms_isa_raw_value_workbook_variable_rows", "value": csv_value(priority_lsms_raw_value_workbook_summary, "priority_lsms_raw_value_workbook_variable_rows", "0"), "interpretation": "Variable-level raw value verification workbook rows."},
        {"metric": "priority_lsms_isa_raw_value_workbook_file_rows", "value": csv_value(priority_lsms_raw_value_workbook_summary, "priority_lsms_raw_value_workbook_file_rows", "0"), "interpretation": "File-level raw value verification workbook rows."},
        {"metric": "priority_lsms_isa_received_raw_schema_file_rows", "value": csv_value(priority_lsms_received_raw_schema_summary, "priority_lsms_received_raw_schema_file_rows", "0"), "interpretation": "Received official raw archive files included in the metadata-only schema audit."},
        {"metric": "priority_lsms_isa_received_raw_schema_readable_file_rows", "value": csv_value(priority_lsms_received_raw_schema_summary, "priority_lsms_received_raw_schema_readable_file_rows", "0"), "interpretation": "Received official raw files readable by the schema audit."},
        {"metric": "priority_lsms_isa_received_raw_schema_variable_rows", "value": csv_value(priority_lsms_received_raw_schema_summary, "priority_lsms_received_raw_schema_variable_rows", "0"), "interpretation": "Variables extracted from the received official raw archive schema."},
        {"metric": "priority_lsms_isa_received_raw_schema_candidate_present_rows", "value": csv_value(priority_lsms_received_raw_schema_summary, "priority_lsms_received_raw_requirement_candidate_present_rows", "0"), "interpretation": "Requirement candidate variables present in the received official raw archive."},
        {"metric": "priority_lsms_isa_received_raw_value_profile_variable_rows", "value": csv_value(priority_lsms_received_raw_value_profile_summary, "priority_lsms_received_raw_value_profile_variable_rows", "0"), "interpretation": "Candidate requirement variables with received raw value-profile evidence."},
        {"metric": "priority_lsms_isa_received_raw_value_profile_nonmissing_variable_rows", "value": csv_value(priority_lsms_received_raw_value_profile_summary, "priority_lsms_received_raw_value_profile_nonmissing_variable_rows", "0"), "interpretation": "Candidate variables with at least one nonmissing raw value."},
        {"metric": "priority_lsms_isa_received_raw_key_design_geography_profile_rows", "value": csv_value(priority_lsms_received_raw_value_profile_summary, "priority_lsms_received_raw_key_design_geography_profile_rows", "0"), "interpretation": "Utility key, design, and geography variables profiled from received raw files."},
        {"metric": "priority_lsms_isa_received_raw_value_profile_requirements_with_profiles", "value": csv_value(priority_lsms_received_raw_value_profile_summary, "priority_lsms_received_raw_value_profile_requirements_with_profiles", "0"), "interpretation": "Requirements with value-profile evidence available for manual review."},
        {"metric": "priority_lsms_isa_received_raw_semantics_variable_rows", "value": csv_value(priority_lsms_received_raw_semantics_summary, "priority_lsms_received_raw_semantics_variable_rows", "0"), "interpretation": "Variable-level semantics review rows from value and utility profiles."},
        {"metric": "priority_lsms_isa_received_raw_semantics_ddi_documented_variable_rows", "value": csv_value(priority_lsms_received_raw_semantics_summary, "priority_lsms_received_raw_semantics_ddi_documented_variable_rows", "0"), "interpretation": "Profiled variables matched to official DDI documentation."},
        {"metric": "priority_lsms_isa_received_raw_semantics_requirement_rows", "value": csv_value(priority_lsms_received_raw_semantics_summary, "priority_lsms_received_raw_semantics_requirement_rows", "0"), "interpretation": "Requirement-level semantics review rows."},
        {"metric": "priority_lsms_isa_received_raw_semantics_missing_codes_units_recall_skip_requirement_rows", "value": csv_value(priority_lsms_received_raw_semantics_summary, "priority_lsms_received_raw_semantics_missing_codes_units_recall_skip_requirement_rows", "0"), "interpretation": "Documentation-semantics gate rows backed by review evidence."},
        {"metric": "mwi2004_raw_requirement_verification_requirements", "value": csv_value(mwi2004_raw_requirement_summary, "requirements_with_raw_backed_evidence", "0"), "interpretation": "Malawi 2004 promotion requirements with focused raw-backed verification evidence."},
        {"metric": "mwi2004_raw_requirement_verification_key_or_join_checks", "value": csv_value(mwi2004_raw_requirement_summary, "key_or_join_checks_passing", "0"), "interpretation": "Malawi 2004 mechanical uniqueness and join checks passing in focused raw review."},
        {"metric": "mwi2004_raw_requirement_verification_decision", "value": csv_value(mwi2004_raw_requirement_summary, "raw_value_verification_decision", "missing"), "interpretation": "Focused Malawi 2004 decision; it should remain not_final_verified until manual construct and climate-linkage acceptance pass."},
        {"metric": "mwi2004_requirement_acceptance_decision_rows", "value": csv_value(mwi2004_acceptance_summary, "decision_rows", "0"), "interpretation": "Malawi 2004 requirement-level accept/block decisions."},
        {"metric": "mwi2004_requirement_acceptance_mechanical_pass_or_partial", "value": csv_value(mwi2004_acceptance_summary, "mechanical_raw_checks_pass_or_partial", "0"), "interpretation": "Requirements with mechanical raw evidence that passes but remains short of final verification."},
        {"metric": "mwi2004_requirement_acceptance_final_verified", "value": csv_value(mwi2004_acceptance_summary, "final_verified_requirements", "0"), "interpretation": "Requirements accepted as final verified for their stated scope; this does not by itself open data writes."},
        {"metric": "mwi2004_financial_policy_status", "value": csv_value(mwi2004_financial_policy_summary, "financial_policy_status", "missing"), "interpretation": "Malawi 2004 CHE10/CHE25 financial policy status."},
        {"metric": "mwi2004_financial_policy_household_rows", "value": csv_value(mwi2004_financial_policy_summary, "household_financial_rows", "0"), "interpretation": "Household rows with verified financial inputs for CHE10/CHE25 candidates."},
        {"metric": "mwi2004_financial_policy_che10_rows", "value": csv_value(mwi2004_financial_policy_summary, "che10_candidate_rows", "0"), "interpretation": "Candidate CHE10 rows from accepted financial inputs."},
        {"metric": "mwi2004_financial_policy_che25_rows", "value": csv_value(mwi2004_financial_policy_summary, "che25_candidate_rows", "0"), "interpretation": "Candidate CHE25 rows from accepted financial inputs."},
        {"metric": "mwi2004_financial_policy_sdg382_ready", "value": csv_value(mwi2004_financial_policy_summary, "sdg382_ready", "0"), "interpretation": "Whether SDG 3.8.2 is ready; should remain zero."},
        {"metric": "mwi2004_sdg382_parameter_internal_inputs_complete", "value": csv_value(mwi2004_sdg382_parameter_summary, "raw_internal_sdg382_inputs_complete", "0"), "interpretation": "Whether Malawi 2004 has raw OOP, consumption, household size, and weights needed before parameterizing current SDG 3.8.2."},
        {"metric": "mwi2004_sdg382_parameter_external_ppp_cpi_verified", "value": csv_value(mwi2004_sdg382_parameter_summary, "external_ppp_cpi_parameters_verified", "0"), "interpretation": "Whether 2017 PPP and CPI/deflator parameters have been frozen for Malawi 2004 SDG 3.8.2."},
        {"metric": "mwi2004_sdg382_parameter_sdg382_ready", "value": csv_value(mwi2004_sdg382_parameter_summary, "sdg382_ready", "0"), "interpretation": "Current Malawi 2004 SDG 3.8.2 readiness under the 2026 discretionary-budget metadata."},
        {"metric": "mwi2004_sdg382_external_parameter_ppp_private_2017", "value": csv_value(mwi2004_sdg382_external_parameter_summary, "wdi_ppp_private_consumption_2017", "missing"), "interpretation": "World Bank private-consumption PPP candidate captured for Malawi 2017."},
        {"metric": "mwi2004_sdg382_external_parameter_cpi_ratio_candidate", "value": csv_value(mwi2004_sdg382_external_parameter_summary, "candidate_cpi_ratio_2017_to_2004", "missing"), "interpretation": "Annual CPI candidate bridge from 2004 to 2017; not final."},
        {"metric": "mwi2004_sdg382_external_parameter_bridge_accepted", "value": csv_value(mwi2004_sdg382_external_parameter_summary, "external_parameter_bridge_accepted", "0"), "interpretation": "Whether the external PPP/CPI bridge is accepted for final SDG 3.8.2 classification."},
        {"metric": "mwi2004_sdg382_candidate_precheck_nonpositive_discretionary_rows", "value": csv_value(mwi2004_sdg382_candidate_precheck_summary, "nonpositive_discretionary_budget_rows", "0"), "interpretation": "Rows with nonpositive candidate discretionary budget under Malawi 2004 candidate SPL."},
        {"metric": "mwi2004_sdg382_candidate_precheck_strict_candidate_rows", "value": csv_value(mwi2004_sdg382_candidate_precheck_summary, "positive_discretionary_candidate_sdg382_rows", "0"), "interpretation": "Candidate SDG 3.8.2 household rows under the strict positive-discretionary-budget diagnostic variant."},
        {"metric": "mwi2004_sdg382_candidate_precheck_floor_candidate_rows", "value": csv_value(mwi2004_sdg382_candidate_precheck_summary, "floor_variant_candidate_sdg382_rows", "0"), "interpretation": "Candidate SDG 3.8.2 household rows under the denominator-floor sensitivity variant."},
        {"metric": "mwi2004_sdg382_candidate_precheck_written_to_data", "value": csv_value(mwi2004_sdg382_candidate_precheck_summary, "candidate_classification_written_to_data", "1"), "interpretation": "Whether household-level candidate SDG 3.8.2 classifications were written to data; should remain zero."},
        {"metric": "mwi2004_sdg382_official_denominator_rule_accepted", "value": csv_value(mwi2004_sdg382_denominator_rule_summary, "official_denominator_rule_accepted", "0"), "interpretation": "Whether the official nonpositive-discretionary-budget rule is accepted from UNSD metadata."},
        {"metric": "mwi2004_sdg382_official_rule_candidate_rows", "value": csv_value(mwi2004_sdg382_denominator_rule_summary, "official_rule_candidate_sdg382_rows", "0"), "interpretation": "Aggregate candidate SDG 3.8.2 rows using the official denominator rule plus the candidate SPL bridge."},
        {"metric": "mwi2004_sdg382_official_rule_candidate_rate", "value": csv_value(mwi2004_sdg382_denominator_rule_summary, "official_rule_candidate_sdg382_weighted_rate", "missing"), "interpretation": "Weighted candidate rate under the official rule; not final because the SPL bridge is not accepted."},
        {"metric": "mwi2004_sdg382_official_rule_bridge_accepted", "value": csv_value(mwi2004_sdg382_denominator_rule_summary, "external_parameter_bridge_accepted", "0"), "interpretation": "Whether the Malawi local-currency SPL bridge is accepted; should remain zero."},
        {"metric": "mwi2004_timing_geography_policy_status", "value": csv_value(mwi2004_timing_geography_summary, "timing_geography_policy_status", "missing"), "interpretation": "Malawi 2004 timing/geography raw-value policy status."},
        {"metric": "mwi2004_timing_geography_idate_rows", "value": csv_value(mwi2004_timing_geography_summary, "idate_nonmissing_rows", "0"), "interpretation": "Rows with verified raw household interview date."},
        {"metric": "mwi2004_timing_geography_months", "value": csv_value(mwi2004_timing_geography_summary, "interview_month_count", "0"), "interpretation": "Distinct interview months for climate-window anchoring."},
        {"metric": "mwi2004_timing_geography_household_ea", "value": csv_value(mwi2004_timing_geography_summary, "household_ea_distinct", "0"), "interpretation": "Distinct household EA/admin keys."},
        {"metric": "mwi2004_timing_geography_ready_for_route_review", "value": csv_value(mwi2004_timing_geography_summary, "timing_geography_ready_for_climate", "0"), "interpretation": "Whether raw timing and geography are ready for climate-route review."},
        {"metric": "mwi2004_timing_geography_accepted_chirps_era5_route", "value": csv_value(mwi2004_timing_geography_summary, "accepted_chirps_era5_route", "0"), "interpretation": "Whether CHIRPS/ERA5 route is accepted; should remain zero."},
        {"metric": "mwi2004_chirps_admin2_route_design_ready", "value": csv_value(mwi2004_chirps_route_summary, "route_design_ready", "0"), "interpretation": "Whether Malawi 2004 has a CHIRPS ADM2 route design ready for raster extraction."},
        {"metric": "mwi2004_chirps_admin2_raw_boundary_matches", "value": csv_value(mwi2004_chirps_route_summary, "raw_district_boundary_matches", "0"), "interpretation": "Raw Malawi 2004 district labels matched to ADM2 boundary names."},
        {"metric": "mwi2004_chirps_admin2_required_months", "value": csv_value(mwi2004_chirps_route_summary, "required_chirps_months", "0"), "interpretation": "CHIRPS monthly GeoTIFF files required for planned lag windows."},
        {"metric": "mwi2004_chirps_admin2_accepted_route", "value": csv_value(mwi2004_chirps_route_summary, "accepted_chirps_era5_route", "0"), "interpretation": "Promoted climate linkage gate remains closed until extraction validation passes."},
        {"metric": "mwi2004_chirps_admin2_extraction_files", "value": csv_value(mwi2004_chirps_extraction_summary, "chirps_files_downloaded_readable", "0"), "interpretation": "CHIRPS monthly files downloaded and readable for Malawi 2004 extraction."},
        {"metric": "mwi2004_chirps_admin2_district_month_rows", "value": csv_value(mwi2004_chirps_extraction_summary, "district_month_exposure_rows", "0"), "interpretation": "ADM2 district-month rainfall exposure rows."},
        {"metric": "mwi2004_chirps_admin2_lag_window_rows", "value": csv_value(mwi2004_chirps_extraction_summary, "lag_window_exposure_rows", "0"), "interpretation": "Raw district-interview-month lag-window exposure rows."},
        {"metric": "mwi2004_chirps_admin2_extraction_accepted_route", "value": csv_value(mwi2004_chirps_extraction_summary, "accepted_chirps_era5_route", "0"), "interpretation": "Whether CHIRPS extraction validation opens the climate-linkage route gate."},
        {"metric": "mwi2004_health_access_label_rows", "value": csv_value(mwi2004_health_access_summary, "label_decision_rows", "0"), "interpretation": "Health/access variable-value rows mapped into candidate construct decisions."},
        {"metric": "mwi2004_health_access_no_money_rows", "value": csv_value(mwi2004_health_access_summary, "financial_barrier_no_money_rows", "0"), "interpretation": "d07a/d07b rows mapped to no-money no-action candidate access failure."},
        {"metric": "mwi2004_health_access_skip_leakage_rows", "value": csv_value(mwi2004_health_access_summary, "total_skip_leakage_rows", "0"), "interpretation": "Aggregate skip leakage rows found in the health/access label-skip audit."},
        {"metric": "mwi2004_health_exception_d07a_overlap", "value": csv_value(mwi2004_health_exception_summary, "d07a_skip_leakage_overlap_with_unmatched_health_rows", "missing"), "interpretation": "Overlap between d07a skip leakage and health-module person keys absent from the roster."},
        {"metric": "mwi2004_health_exception_explained_by_nonroster", "value": csv_value(mwi2004_health_exception_summary, "d07a_skip_leakage_explained_by_nonroster_rows", "missing"), "interpretation": "Whether d07a skip leakage is fully explained by nonroster health rows."},
        {"metric": "mwi2004_health_exception_policy_status", "value": csv_value(mwi2004_health_exception_summary, "exception_policy_status", "missing"), "interpretation": "Exception audit status for person-key and skip-leakage resolution."},
        {"metric": "mwi2004_health_access_policy_status", "value": csv_value(mwi2004_health_policy_summary, "construction_policy_status", "missing"), "interpretation": "Candidate health/access construction policy status."},
        {"metric": "mwi2004_health_access_policy_denominator_rows", "value": csv_value(mwi2004_health_policy_summary, "acute_need_denominator_rows", "0"), "interpretation": "Roster-matched d04==Yes rows under the candidate access denominator."},
        {"metric": "mwi2004_health_access_policy_no_money_rows", "value": csv_value(mwi2004_health_policy_summary, "financial_barrier_forgone_care_rows", "0"), "interpretation": "Candidate no-money forgone-care rows counted once per person row."},
        {"metric": "mwi2004_health_access_resolution_status", "value": csv_value(mwi2004_access_resolution_summary, "access_resolution_status", "missing"), "interpretation": "Malawi 2004 access/person-key resolution status."},
        {"metric": "mwi2004_health_access_resolution_denominator_rows", "value": csv_value(mwi2004_access_resolution_summary, "acute_need_denominator_rows", "0"), "interpretation": "Accepted roster-matched acute-need denominator rows."},
        {"metric": "mwi2004_health_access_resolution_no_money_rows", "value": csv_value(mwi2004_access_resolution_summary, "cost_barrier_forgone_care_rows", "0"), "interpretation": "Accepted cost-barrier forgone-care rows."},
        {"metric": "mwi2004_health_access_resolution_skip_no_money_rows", "value": csv_value(mwi2004_access_resolution_summary, "d07a_d07b_skip_exception_no_money_rows", "0"), "interpretation": "No-money rows among documented skip exceptions; must be zero for accepted exclusion."},
        {"metric": "mwi2004_health_access_policy_final_verified", "value": csv_value(mwi2004_access_resolution_summary, "health_access_final_verified", "0"), "interpretation": "Whether Malawi 2004 acute need and cost-barrier access are final verified for the stated scope."},
        {"metric": "mwi2004_missing_units_recall_skip_status", "value": csv_value(mwi2004_missing_units_summary, "missing_units_recall_skip_policy_status", "missing"), "interpretation": "Malawi 2004 missing, units, recall, and skip policy status."},
        {"metric": "mwi2004_missing_units_recall_skip_final_verified", "value": csv_value(mwi2004_missing_units_summary, "missing_units_recall_skip_policy_final_verified", "0"), "interpretation": "Whether missing, units, recall, and skip policy is final verified for accepted constructs."},
        {"metric": "mwi2004_promoted_dataset_status", "value": csv_value(mwi2004_promoted_dataset_summary, "analysis_ready_status", "not_promoted"), "interpretation": "Whether the Malawi 2004 household-climate synthesis is promoted analysis-ready."},
        {"metric": "mwi2004_promoted_dataset_rows", "value": csv_value(mwi2004_promoted_dataset_summary, "promoted_rows", "0"), "interpretation": "Household rows in the local promoted Malawi 2004 dataset."},
        {"metric": "mwi2004_promoted_dataset_che10_rows", "value": csv_value(mwi2004_promoted_dataset_summary, "che10_rows", "0"), "interpretation": "Promoted Malawi 2004 CHE10 household rows."},
        {"metric": "mwi2004_promoted_dataset_che25_rows", "value": csv_value(mwi2004_promoted_dataset_summary, "che25_rows", "0"), "interpretation": "Promoted Malawi 2004 CHE25 household rows."},
        {"metric": "mwi2004_promoted_dataset_cost_barrier_households", "value": csv_value(mwi2004_promoted_dataset_summary, "households_any_cost_barrier_forgone_care", "0"), "interpretation": "Promoted Malawi 2004 households with any cost-barrier forgone care."},
        {"metric": "mwi2004_promoted_dataset_climate_complete_rows", "value": csv_value(mwi2004_promoted_dataset_summary, "climate_exposure_complete_rows", "0"), "interpretation": "Promoted Malawi 2004 household rows with complete 1/3/6/12 month CHIRPS exposures."},
        {"metric": "mwi2004_promoted_dataset_data_write_gate", "value": csv_value(mwi2004_promoted_dataset_summary, "data_write_gate_status", "missing"), "interpretation": "Controlled data-write gate outcome for the Malawi 2004 promoted synthesis."},
        {"metric": "priority_lsms_isa_receipt_checklist_dataset_rows", "value": csv_value(priority_lsms_receipt_checklist_summary, "priority_lsms_receipt_checklist_dataset_rows", "0"), "interpretation": "Dataset-level raw package receipt checklist rows."},
        {"metric": "priority_lsms_isa_receipt_checklist_requirement_rows", "value": csv_value(priority_lsms_receipt_checklist_summary, "priority_lsms_receipt_checklist_requirement_rows", "0"), "interpretation": "Requirement-level raw package receipt checklist rows."},
        {"metric": "priority_lsms_isa_receipt_checklist_package_received_rows", "value": csv_value(priority_lsms_receipt_checklist_summary, "priority_lsms_receipt_checklist_package_received_rows", "0"), "interpretation": "Refocused LSMS/ISA waves with original package receipt evidence."},
        {"metric": "priority_lsms_isa_credentialed_workbench_dataset_rows", "value": csv_value(priority_lsms_credentialed_workbench_summary, "priority_lsms_credentialed_workbench_dataset_rows", "0"), "interpretation": "Credentialed raw acquisition workbench dataset rows."},
        {"metric": "priority_lsms_isa_credentialed_workbench_core_file_rows", "value": csv_value(priority_lsms_credentialed_workbench_summary, "priority_lsms_credentialed_workbench_core_file_rows", "0"), "interpretation": "Core file rows to confirm after official package download."},
        {"metric": "priority_lsms_isa_credentialed_workbench_package_received_rows", "value": csv_value(priority_lsms_credentialed_workbench_summary, "priority_lsms_credentialed_workbench_package_received_rows", "0"), "interpretation": "Credentialed workbench waves with original package receipt evidence."},
        {"metric": "priority_lsms_isa_official_file_receipt_expected_file_rows", "value": csv_value(priority_lsms_official_file_receipt_summary, "priority_lsms_official_file_receipt_expected_file_rows", "0"), "interpretation": "Official DDI files expected after package receipt."},
        {"metric": "priority_lsms_isa_official_file_receipt_expected_file_matched_rows", "value": csv_value(priority_lsms_official_file_receipt_summary, "priority_lsms_official_file_receipt_expected_file_matched_rows", "0"), "interpretation": "Expected official DDI files matched locally."},
        {"metric": "priority_lsms_isa_official_file_receipt_core_file_missing_rows", "value": csv_value(priority_lsms_official_file_receipt_summary, "priority_lsms_official_file_receipt_core_file_missing_rows", "0"), "interpretation": "Core expected files still missing locally."},
        {"metric": "priority_lsms_isa_threshold_sequence_minimum_download_rows", "value": csv_value(priority_lsms_threshold_sequence_summary, "priority_lsms_threshold_sequence_minimum_download_rows", "0"), "interpretation": "Minimum downloads needed to test 10-wave and 6-country thresholds if every wave passes verification."},
        {"metric": "priority_lsms_isa_threshold_sequence_recommended_download_rows", "value": csv_value(priority_lsms_threshold_sequence_summary, "priority_lsms_threshold_sequence_recommended_download_rows", "0"), "interpretation": "Recommended threshold downloads including all sixth-country candidates."},
        {"metric": "priority_lsms_isa_threshold_sequence_raw_package_received_rows", "value": csv_value(priority_lsms_threshold_sequence_summary, "priority_lsms_threshold_sequence_raw_package_received_rows", "0"), "interpretation": "Threshold sequence rows with non-blocked official file receipt status."},
        {"metric": "priority_lsms_isa_minimum_batch_expected_full_file_rows", "value": csv_value(priority_lsms_minimum_intake_summary, "priority_lsms_minimum_batch_expected_full_file_rows", "0"), "interpretation": "Expected official DDI file rows across the 11-wave minimum batch."},
        {"metric": "priority_lsms_isa_minimum_batch_missing_core_file_rows", "value": csv_value(priority_lsms_minimum_intake_summary, "priority_lsms_minimum_batch_missing_core_file_rows", "0"), "interpretation": "Core official files still missing locally for the 11-wave minimum batch."},
        {"metric": "priority_lsms_isa_minimum_endpoint_credentialed_download_required_rows", "value": csv_value(priority_lsms_minimum_endpoint_summary, "priority_lsms_minimum_endpoint_credentialed_download_required_rows", "0"), "interpretation": "Minimum-batch waves still requiring credentialed World Bank download after endpoint refresh."},
        {"metric": "priority_lsms_isa_minimum_endpoint_raw_download_candidate_rows", "value": csv_value(priority_lsms_minimum_endpoint_summary, "priority_lsms_minimum_endpoint_raw_download_candidate_rows", "0"), "interpretation": "Raw download candidate endpoints detected by the minimum-batch endpoint refresh."},
        {"metric": "priority_lsms_isa_next_raw_package_actions", "value": csv_value(priority_lsms_next_raw_package_summary, "next_raw_package_action_rows", "0"), "interpretation": "Country-waves in the next raw package acquisition queue."},
        {"metric": "priority_lsms_isa_next_raw_package_minimum_remaining", "value": csv_value(priority_lsms_next_raw_package_summary, "minimum_batch_remaining_action_rows", "0"), "interpretation": "Remaining minimum-batch waves requiring complete official raw packages."},
        {"metric": "priority_lsms_isa_next_raw_package_core_file_rows", "value": csv_value(priority_lsms_next_raw_package_summary, "core_file_action_rows", "0"), "interpretation": "Core requirement-file rows to confirm after raw package placement."},
        {"metric": "priority_lsms_isa_next_raw_package_countries_if_pass", "value": csv_value(priority_lsms_next_raw_package_summary, "countries_if_minimum_batch_passes", "0"), "interpretation": "Countries covered if the current promoted row plus remaining minimum batch all pass verification."},
        {"metric": "priority_lsms_isa_next_raw_package_waves_if_pass", "value": csv_value(priority_lsms_next_raw_package_summary, "country_waves_if_minimum_batch_passes", "0"), "interpretation": "Country-waves covered if the current promoted row plus remaining minimum batch all pass verification."},
        {"metric": "priority_lsms_isa_incoming_router_incoming_files", "value": csv_value(priority_lsms_incoming_router_summary, "priority_lsms_incoming_router_incoming_file_rows", "0"), "interpretation": "Files currently staged under temp/raw_downloads/_incoming for route scoring."},
        {"metric": "priority_lsms_isa_incoming_router_copy_candidates", "value": csv_value(priority_lsms_incoming_router_summary, "priority_lsms_incoming_router_copy_candidate_rows", "0"), "interpretation": "Incoming files with a single suggested country-wave target folder."},
        {"metric": "priority_lsms_isa_incoming_router_manual_review_rows", "value": csv_value(priority_lsms_incoming_router_summary, "priority_lsms_incoming_router_manual_review_rows", "0"), "interpretation": "Incoming files that need manual route review."},
        {"metric": "priority_lsms_isa_threshold_gap_current_country_gap", "value": csv_value(priority_lsms_threshold_gap_summary, "current_country_gap_to_threshold", "0"), "interpretation": "Additional value-verified countries needed from the current promoted registry."},
        {"metric": "priority_lsms_isa_threshold_gap_current_wave_gap", "value": csv_value(priority_lsms_threshold_gap_summary, "current_country_wave_gap_to_threshold", "0"), "interpretation": "Additional value-verified country-waves needed from the current promoted registry."},
        {"metric": "priority_lsms_isa_threshold_gap_minimum_remaining_downloads", "value": csv_value(priority_lsms_threshold_gap_summary, "minimum_threshold_batch_remaining_download_rows", "0"), "interpretation": "Minimum-batch raw package downloads still required."},
        {"metric": "priority_lsms_isa_threshold_gap_countries_if_minimum_passes", "value": csv_value(priority_lsms_threshold_gap_summary, "countries_if_minimum_remaining_passes", "0"), "interpretation": "Countries covered if all remaining minimum-batch downloads later pass verification."},
        {"metric": "priority_lsms_isa_threshold_gap_waves_if_minimum_passes", "value": csv_value(priority_lsms_threshold_gap_summary, "country_waves_if_minimum_remaining_passes", "0"), "interpretation": "Country-waves covered if all remaining minimum-batch downloads later pass verification."},
        {"metric": "priority_lsms_isa_threshold_gap_country_buffer", "value": csv_value(priority_lsms_threshold_gap_summary, "country_buffer_if_minimum_remaining_passes", "0"), "interpretation": "Country-count buffer above the 6-country threshold after the minimum batch passes."},
        {"metric": "priority_lsms_isa_threshold_gap_wave_buffer", "value": csv_value(priority_lsms_threshold_gap_summary, "country_wave_buffer_if_minimum_remaining_passes", "0"), "interpretation": "Country-wave buffer above the 10-wave threshold after the minimum batch passes."},
        {"metric": "priority_lsms_isa_manual_download_packet_rows", "value": csv_value(priority_lsms_manual_download_packet_summary, "manual_download_packet_rows", "0"), "interpretation": "Remaining minimum-batch waves with per-wave manual download packets."},
        {"metric": "priority_lsms_isa_manual_download_packet_core_rows", "value": csv_value(priority_lsms_manual_download_packet_summary, "manual_download_packet_core_file_rows", "0"), "interpretation": "Core-file rows listed across manual download packets."},
        {"metric": "priority_lsms_isa_manual_download_packet_reports", "value": csv_value(priority_lsms_manual_download_packet_summary, "manual_download_packet_reports_written", "0"), "interpretation": "Per-IDNO markdown packet reports written."},
        {"metric": "priority_lsms_isa_manual_download_progress_validation_ready", "value": csv_value(priority_lsms_manual_download_progress_summary, "manual_download_progress_validation_ready_packets", "0"), "interpretation": "Manual download packets with local target files ready for validation."},
        {"metric": "priority_lsms_isa_manual_download_progress_blocked_no_files", "value": csv_value(priority_lsms_manual_download_progress_summary, "manual_download_progress_blocked_no_file_packets", "0"), "interpretation": "Manual download packets still lacking local target files or incoming route matches."},
        {"metric": "priority_lsms_isa_manual_download_progress_target_files", "value": csv_value(priority_lsms_manual_download_progress_summary, "manual_download_progress_target_file_rows", "0"), "interpretation": "Non-generated files currently found under packet target folders."},
        {"metric": "priority_lsms_isa_post_download_validation_ready_packets", "value": csv_value(priority_lsms_post_download_validation_summary, "post_download_validation_ready_packet_rows", "0"), "interpretation": "Packets ready for post-download validation."},
        {"metric": "priority_lsms_isa_post_download_validation_plan_rows", "value": csv_value(priority_lsms_post_download_validation_summary, "post_download_validation_plan_rows", "0"), "interpretation": "Post-download validation command-plan rows."},
        {"metric": "priority_lsms_isa_post_download_validation_execute_commands", "value": csv_value(priority_lsms_post_download_validation_summary, "post_download_validation_execute_command_rows", "0"), "interpretation": "Validation commands selected for execution in the latest runner invocation."},
        {"metric": "priority_lsms_isa_manual_download_execution_board_rows", "value": csv_value(priority_lsms_manual_download_execution_board_summary, "manual_download_execution_board_rows", "0"), "interpretation": "Manual-download execution board rows."},
        {"metric": "priority_lsms_isa_manual_download_execution_board_target_files", "value": csv_value(priority_lsms_manual_download_execution_board_summary, "manual_download_execution_board_target_file_rows", "0"), "interpretation": "Files currently present under execution-board target folders."},
        {"metric": "priority_lsms_isa_manual_download_execution_board_validation_ready", "value": csv_value(priority_lsms_manual_download_execution_board_summary, "manual_download_execution_board_validation_ready_rows", "0"), "interpretation": "Execution-board rows ready for post-download validation."},
        {"metric": "priority_lsms_isa_credentialed_download_handoff_rows", "value": csv_value(priority_lsms_credentialed_download_handoff_summary, "credentialed_download_handoff_rows", "0"), "interpretation": "Credentialed World Bank download handoff rows."},
        {"metric": "priority_lsms_isa_credentialed_download_handoff_attempted", "value": csv_value(priority_lsms_credentialed_download_handoff_summary, "credentialed_download_handoff_request_attempted_rows", "0"), "interpretation": "Credentialed download handoff rows where /download was requested."},
        {"metric": "priority_lsms_isa_credentialed_download_handoff_saved", "value": csv_value(priority_lsms_credentialed_download_handoff_summary, "credentialed_download_handoff_saved_raw_file_rows", "0"), "interpretation": "Credentialed download handoff rows where raw payloads were saved."},
        {"metric": "priority_lsms_isa_promotion_gate_country_waves", "value": csv_value(priority_lsms_promotion_gate_summary, "priority_lsms_promotion_gate_country_wave_rows", "0"), "interpretation": "Country-waves tracked by the promotion gate dashboard."},
        {"metric": "priority_lsms_isa_promotion_gate_promoted_rows", "value": csv_value(priority_lsms_promotion_gate_summary, "priority_lsms_promotion_gate_promoted_rows", "0"), "interpretation": "Country-waves already promoted analysis-ready in the gate dashboard."},
        {"metric": "priority_lsms_isa_promotion_gate_blocked_raw_package_rows", "value": csv_value(priority_lsms_promotion_gate_summary, "priority_lsms_promotion_gate_blocked_raw_package_rows", "0"), "interpretation": "Country-waves still blocked at complete official raw package receipt."},
        {"metric": "priority_lsms_isa_promotion_gate_requirement_rows", "value": csv_value(priority_lsms_promotion_gate_summary, "priority_lsms_promotion_gate_requirement_rows", "0"), "interpretation": "Requirement-level gate rows tracked by the promotion dashboard."},
        {"metric": "priority_lsms_isa_unlock_board_rows", "value": csv_value(priority_lsms_unlock_summary, "minimum_batch_unlock_board_rows", "0"), "interpretation": "Minimum-batch promotion unlock board rows."},
        {"metric": "priority_lsms_isa_unlock_board_public_docs_complete", "value": csv_value(priority_lsms_unlock_summary, "minimum_batch_unlock_public_documentation_complete_rows", "0"), "interpretation": "Minimum-batch rows with complete public documentation receipt."},
        {"metric": "priority_lsms_isa_unlock_board_validation_ready", "value": csv_value(priority_lsms_unlock_summary, "minimum_batch_unlock_validation_ready_rows", "0"), "interpretation": "Minimum-batch rows ready for receipt validation after local package placement."},
        {"metric": "priority_lsms_isa_unlock_board_projected_countries", "value": csv_value(priority_lsms_unlock_summary, "projected_country_rows_if_all_minimum_batch_promoted", "0"), "interpretation": "Projected country count if every current minimum-batch package passes all promotion gates."},
        {"metric": "priority_lsms_isa_unlock_board_projected_waves", "value": csv_value(priority_lsms_unlock_summary, "projected_country_wave_rows_if_all_minimum_batch_promoted", "0"), "interpretation": "Projected country-wave count if every current minimum-batch package passes all promotion gates."},
        {"metric": "priority_lsms_isa_worldbank_session_bootstrap_rows", "value": csv_value(priority_lsms_worldbank_session_summary, "worldbank_session_bootstrap_rows", "0"), "interpretation": "Minimum-batch rows covered by the redacted World Bank session bootstrap."},
        {"metric": "priority_lsms_isa_worldbank_session_ready_for_probe", "value": csv_value(priority_lsms_worldbank_session_summary, "worldbank_session_bootstrap_ready_for_probe_rows", "0"), "interpretation": "Rows ready for credentialed /download probing."},
        {"metric": "priority_lsms_isa_worldbank_session_missing_session", "value": csv_value(priority_lsms_worldbank_session_summary, "worldbank_session_bootstrap_missing_session_rows", "0"), "interpretation": "Rows blocked because local session material is absent."},
        {"metric": "priority_lsms_isa_worldbank_session_cookie_present", "value": csv_value(priority_lsms_worldbank_session_summary, "worldbank_session_cookie_file_present", "0"), "interpretation": "Whether the local cookie file exists; contents are never included."},
        {"metric": "priority_lsms_isa_credentialed_fetch_command_packet_rows", "value": csv_value(priority_lsms_fetch_command_summary, "credentialed_fetch_command_packet_rows", "0"), "interpretation": "Minimum-batch rows with credentialed fetch commands."},
        {"metric": "priority_lsms_isa_credentialed_fetch_command_packet_countries", "value": csv_value(priority_lsms_fetch_command_summary, "credentialed_fetch_command_packet_countries", "0"), "interpretation": "Distinct countries covered by the fetch command packet."},
        {"metric": "priority_lsms_isa_credentialed_fetch_expected_core_files", "value": csv_value(priority_lsms_fetch_command_summary, "credentialed_fetch_command_packet_expected_core_file_rows", "0"), "interpretation": "Expected core raw-file rows to check after package receipt."},
        {"metric": "priority_lsms_isa_credentialed_fetch_ready_for_probe", "value": csv_value(priority_lsms_fetch_command_summary, "credentialed_fetch_command_packet_ready_to_probe_rows", "0"), "interpretation": "Fetch command rows ready for credentialed probing."},
        {"metric": "priority_lsms_isa_credentialed_fetch_missing_session", "value": csv_value(priority_lsms_fetch_command_summary, "credentialed_fetch_command_packet_missing_session_rows", "0"), "interpretation": "Fetch command rows blocked because local session material is absent."},
        {"metric": "priority_lsms_isa_browser_download_starter_rows", "value": csv_value(priority_lsms_browser_starter_summary, "browser_download_starter_rows", "0"), "interpretation": "Minimum-batch rows with browser/manual download starter commands."},
        {"metric": "priority_lsms_isa_browser_download_starter_ready", "value": csv_value(priority_lsms_browser_starter_summary, "browser_download_starter_ready_rows", "0"), "interpretation": "Starter rows with official URLs and target folders."},
        {"metric": "priority_lsms_isa_browser_download_first_canary", "value": csv_value(priority_lsms_browser_starter_summary, "browser_download_starter_first_canary_idno", ""), "interpretation": "First wave to try before scaling manual/browser downloads."},
        {"metric": "priority_lsms_isa_browser_download_target_files", "value": csv_value(priority_lsms_browser_starter_summary, "browser_download_starter_target_file_count", "0"), "interpretation": "Existing target-folder files before browser/manual download."},
        {"metric": "priority_lsms_isa_first_canary_idno", "value": csv_value(priority_lsms_first_canary_summary, "first_canary_idno", ""), "interpretation": "First canary IDNO covered by the dedicated download runbook."},
        {"metric": "priority_lsms_isa_first_canary_unique_core_files", "value": csv_value(priority_lsms_first_canary_summary, "first_canary_expected_unique_core_file_rows", "0"), "interpretation": "Unique core files in the first canary checklist."},
        {"metric": "priority_lsms_isa_first_canary_requirement_core_file_rows", "value": csv_value(priority_lsms_first_canary_summary, "first_canary_requirement_core_file_rows", "0"), "interpretation": "Requirement-file linkage rows in the first canary checklist."},
        {"metric": "priority_lsms_isa_first_canary_target_files", "value": csv_value(priority_lsms_first_canary_summary, "first_canary_target_file_count", "0"), "interpretation": "Current first canary target-folder file count."},
        {"metric": "priority_lsms_isa_local_raw_presence_registry_rows", "value": csv_value(priority_lsms_raw_presence_summary, "local_raw_presence_registry_rows", "0"), "interpretation": "Promotion registry rows audited for local raw-like files."},
        {"metric": "priority_lsms_isa_local_raw_presence_registry_raw_present", "value": csv_value(priority_lsms_raw_presence_summary, "local_raw_presence_registry_raw_present_rows", "0"), "interpretation": "Registry rows with local raw-like files."},
        {"metric": "priority_lsms_isa_local_raw_presence_minimum_batch_raw_absent", "value": csv_value(priority_lsms_raw_presence_summary, "local_raw_presence_minimum_batch_raw_absent_rows", "0"), "interpretation": "Minimum-batch rows still lacking local raw-like files."},
        {"metric": "priority_lsms_isa_local_raw_presence_diagnostic_albania_raw_files", "value": csv_value(priority_lsms_raw_presence_summary, "local_raw_presence_diagnostic_albania_raw_file_rows", "0"), "interpretation": "Registry-outside Albania raw files retained as diagnostic-only."},
        {"metric": "priority_lsms_isa_acquisition_to_promotion_handoff_rows", "value": csv_value(priority_lsms_handoff_summary, "acquisition_to_promotion_handoff_rows", "0"), "interpretation": "Registry rows mapped from raw acquisition to promotion-refresh gates."},
        {"metric": "priority_lsms_isa_acquisition_to_promotion_gate_rows", "value": csv_value(priority_lsms_handoff_summary, "acquisition_to_promotion_gate_rows", "0"), "interpretation": "Verification-gate checklist rows in the acquisition-to-promotion handoff."},
        {"metric": "priority_lsms_isa_acquisition_to_promotion_minimum_batch_acquire_rows", "value": csv_value(priority_lsms_handoff_summary, "acquisition_to_promotion_minimum_batch_acquire_rows", "0"), "interpretation": "Minimum-batch rows still blocked at official raw package acquisition."},
        {"metric": "priority_lsms_isa_acquisition_to_promotion_acquire_raw_rows", "value": csv_value(priority_lsms_handoff_summary, "acquisition_to_promotion_acquire_raw_rows", "0"), "interpretation": "Registry rows still blocked at official raw package acquisition."},
        {"metric": "priority_lsms_isa_dataset_scope_lock_rows", "value": csv_value(priority_lsms_scope_lock_summary, "dataset_scope_lock_rows", "0"), "interpretation": "Locked target country-wave rows for the dataset-promotion campaign."},
        {"metric": "priority_lsms_isa_dataset_scope_lock_country_rows", "value": csv_value(priority_lsms_scope_lock_summary, "dataset_scope_lock_country_rows", "0"), "interpretation": "Countries represented if all locked target rows pass promotion gates."},
        {"metric": "priority_lsms_isa_dataset_scope_lock_download_required_rows", "value": csv_value(priority_lsms_scope_lock_summary, "dataset_scope_lock_download_required_rows", "0"), "interpretation": "Locked target rows still requiring official raw package acquisition."},
        {"metric": "priority_lsms_isa_dataset_scope_lock_promoted_anchor_rows", "value": csv_value(priority_lsms_scope_lock_summary, "dataset_scope_lock_promoted_anchor_rows", "0"), "interpretation": "Locked target rows already promoted as current anchors."},
        {"metric": "priority_lsms_isa_dataset_scope_lock_wave_period_min", "value": csv_value(priority_lsms_scope_lock_summary, "dataset_scope_lock_wave_period_min", ""), "interpretation": "Earliest wave label in the locked target scope."},
        {"metric": "priority_lsms_isa_dataset_scope_lock_wave_period_max", "value": csv_value(priority_lsms_scope_lock_summary, "dataset_scope_lock_wave_period_max", ""), "interpretation": "Latest wave label in the locked target scope."},
        {"metric": "priority_lsms_isa_acquisition_route_decision_rows", "value": csv_value(priority_lsms_acquisition_route_summary, "acquisition_route_decision_rows", "0"), "interpretation": "Download-required waves with a consolidated acquisition-route decision."},
        {"metric": "priority_lsms_isa_acquisition_route_decision_local_files_present_rows", "value": csv_value(priority_lsms_acquisition_route_summary, "acquisition_route_decision_local_files_present_rows", "0"), "interpretation": "Download-required waves with local non-generated files ready for validation."},
        {"metric": "priority_lsms_isa_acquisition_route_decision_public_raw_candidate_rows", "value": csv_value(priority_lsms_acquisition_route_summary, "acquisition_route_decision_public_raw_candidate_rows", "0"), "interpretation": "Download-required waves with public raw-route candidate evidence requiring terms review."},
        {"metric": "priority_lsms_isa_acquisition_route_decision_credentialed_probe_ready_rows", "value": csv_value(priority_lsms_acquisition_route_summary, "acquisition_route_decision_credentialed_probe_ready_rows", "0"), "interpretation": "Download-required waves with local redacted session material available for credentialed probing."},
        {"metric": "priority_lsms_isa_acquisition_route_decision_browser_manual_required_rows", "value": csv_value(priority_lsms_acquisition_route_summary, "acquisition_route_decision_browser_manual_required_rows", "0"), "interpretation": "Download-required waves currently requiring browser/manual World Bank terms acceptance."},
        {"metric": "priority_lsms_isa_scoped_incoming_router_targets", "value": csv_value(priority_lsms_scoped_incoming_summary, "scoped_incoming_router_target_rows", "0"), "interpretation": "Locked download-required waves covered by the scoped incoming router."},
        {"metric": "priority_lsms_isa_scoped_incoming_router_incoming_files", "value": csv_value(priority_lsms_scoped_incoming_summary, "scoped_incoming_router_incoming_file_rows", "0"), "interpretation": "Files currently staged under temp/raw_downloads/_incoming for the scoped router."},
        {"metric": "priority_lsms_isa_scoped_incoming_router_pending_drop_rows", "value": csv_value(priority_lsms_scoped_incoming_summary, "scoped_incoming_router_pending_drop_rows", "0"), "interpretation": "Scoped target waves still waiting for an incoming package drop."},
        {"metric": "priority_lsms_isa_scoped_incoming_router_copy_candidates", "value": csv_value(priority_lsms_scoped_incoming_summary, "scoped_incoming_router_copy_candidate_rows", "0"), "interpretation": "Scoped target waves with a suggested incoming file to copy after review."},
        {"metric": "priority_lsms_isa_webgpt_download_control_rows", "value": csv_value(priority_lsms_webgpt_download_summary, "webgpt_download_control_rows", "0"), "interpretation": "Download-required waves in the direct-read Web GPT control manifest."},
        {"metric": "priority_lsms_isa_webgpt_download_expected_full_files", "value": csv_value(priority_lsms_webgpt_download_summary, "webgpt_download_control_expected_full_file_rows", "0"), "interpretation": "Expected official file rows in the Web GPT download control manifest."},
        {"metric": "priority_lsms_isa_webgpt_download_expected_core_files", "value": csv_value(priority_lsms_webgpt_download_summary, "webgpt_download_control_expected_core_file_rows", "0"), "interpretation": "Expected core-file rows exported for direct review."},
        {"metric": "priority_lsms_isa_webgpt_download_browser_manual_rows", "value": csv_value(priority_lsms_webgpt_download_summary, "webgpt_download_control_browser_manual_rows", "0"), "interpretation": "Web GPT control rows still requiring browser/manual World Bank terms acceptance."},
        {"metric": "priority_lsms_isa_country_wave_packet_rows", "value": csv_value(priority_lsms_packet_summary, "priority_lsms_country_wave_packet_rows", "0"), "interpretation": "Refocused LSMS/ISA country-wave promotion packets built."},
        {"metric": "priority_lsms_isa_country_wave_packet_failed_gates", "value": csv_value(priority_lsms_packet_summary, "priority_lsms_country_wave_packet_failed_gate_rows", "0"), "interpretation": "Refocused LSMS/ISA packet gates still blocking promotion."},
        {"metric": "priority_lsms_isa_country_wave_packet_analysis_ready_rows", "value": csv_value(priority_lsms_packet_summary, "priority_lsms_country_wave_packet_analysis_ready_rows", "0"), "interpretation": "Refocused LSMS/ISA packets currently approved for promoted data writes."},
        {"metric": "priority_archive_preflight_targets", "value": csv_value(priority_archive_summary, "priority_archive_preflight_file_target_rows", "0"), "interpretation": "Priority file targets checked against direct files and archive members."},
        {"metric": "priority_archive_preflight_missing_targets", "value": csv_value(priority_archive_summary, "priority_targets_missing_direct_or_archive_member", "0"), "interpretation": "Priority file targets still missing after direct/archive member preflight."},
        {"metric": "priority_manual_verification_dataset_rows", "value": csv_value(priority_manual_verification_summary, "priority_manual_decision_dataset_rows", "0"), "interpretation": "Priority waves evaluated by the manual verification decision gate."},
        {"metric": "priority_manual_verification_requirement_rows", "value": csv_value(priority_manual_verification_summary, "priority_manual_requirement_decision_rows", "0"), "interpretation": "Requirement rows evaluated by the manual verification decision gate."},
        {"metric": "priority_manual_verification_concept_rows", "value": csv_value(priority_manual_verification_summary, "priority_manual_concept_decision_rows", "0"), "interpretation": "Concept rows evaluated by the manual verification decision gate."},
        {"metric": "priority_manual_verification_variable_rows", "value": csv_value(priority_manual_verification_summary, "priority_manual_variable_decision_rows", "0"), "interpretation": "Variable rows evaluated by the manual verification decision gate."},
        {"metric": "priority_manual_verification_financial_ready_countries", "value": csv_value(priority_manual_verification_summary, "priority_financial_protection_manual_ready_countries", "0"), "interpretation": "Countries passing financial-protection manual verification."},
        {"metric": "priority_manual_verification_double_failure_ready_waves", "value": csv_value(priority_manual_verification_summary, "priority_double_failure_manual_ready_waves", "0"), "interpretation": "Country-waves passing double-failure manual verification."},
        {"metric": "priority_manual_verification_analysis_ready_candidates", "value": csv_value(priority_manual_verification_summary, "priority_analysis_ready_candidates", "0"), "interpretation": "Country-waves ready for harmonization-recipe review after manual verification."},
        {"metric": "priority_raw_receipt_original_file_rows", "value": csv_value(priority_receipt_summary, "priority_raw_receipt_original_file_rows", "0"), "interpretation": "Original package/documentation files counted in priority receipt folders, excluding generated handoffs."},
        {"metric": "priority_raw_receipt_priority_targets_missing", "value": csv_value(priority_receipt_summary, "priority_raw_receipt_priority_targets_missing", "0"), "interpretation": "Priority target modules still missing from original package/archive receipt coverage."},
        {"metric": "priority_raw_receipt_missing_package_rows", "value": csv_value(priority_receipt_summary, "priority_raw_receipt_missing_package_rows", "0"), "interpretation": "Priority datasets with no original raw package/tabular receipt yet."},
        {"metric": "priority_raw_receipt_complete_package_candidates", "value": csv_value(priority_receipt_summary, "priority_raw_receipt_complete_package_candidates", "0"), "interpretation": "Priority datasets with original package receipt candidates ready for downstream schema/manual audits."},
        {"metric": "priority_official_download_full_file_rows", "value": csv_value(priority_official_download_summary, "priority_official_full_file_inventory_rows", "0"), "interpretation": "Full official metadata file rows available for credentialed package acquisition checks."},
        {"metric": "priority_official_download_documentation_links", "value": csv_value(priority_official_download_summary, "priority_official_documentation_link_rows", "0"), "interpretation": "Official metadata/documentation/access workflow links in the download dossier."},
        {"metric": "priority_official_download_no_original_package_rows", "value": csv_value(priority_official_download_summary, "priority_official_no_original_package_rows", "0"), "interpretation": "Download dossiers still blocked because no original raw package is present."},
        {"metric": "priority_public_documentation_dataset_rows", "value": csv_value(priority_public_documentation_summary, "priority_public_documentation_dataset_rows", "0"), "interpretation": "Priority datasets with public documentation receipt rows."},
        {"metric": "priority_public_documentation_resource_rows", "value": csv_value(priority_public_documentation_summary, "priority_public_documentation_resource_rows", "0"), "interpretation": "Priority public documentation resources attempted or reused."},
        {"metric": "priority_public_documentation_saved_rows", "value": csv_value(priority_public_documentation_summary, "priority_public_documentation_saved_rows", "0"), "interpretation": "Priority public documentation resources saved or reused locally."},
        {"metric": "priority_public_documentation_core_complete_dataset_rows", "value": csv_value(priority_public_documentation_summary, "priority_public_documentation_core_complete_dataset_rows", "0"), "interpretation": "Priority datasets with complete core public documentation receipts."},
        {"metric": "priority_official_metadata_candidate_variable_rows", "value": csv_value(priority_official_metadata_summary, "priority_official_metadata_candidate_variable_rows", "0"), "interpretation": "Priority candidate variables checked against official DDI/XML metadata."},
        {"metric": "priority_official_metadata_variable_file_match_rows", "value": csv_value(priority_official_metadata_summary, "priority_official_metadata_variable_file_match_rows", "0"), "interpretation": "Priority candidate variables with both DDI variable and file evidence."},
        {"metric": "priority_official_metadata_no_match_rows", "value": csv_value(priority_official_metadata_summary, "priority_official_metadata_no_match_rows", "0"), "interpretation": "Priority candidate variables not matched in parsed official DDI metadata."},
        {"metric": "priority_official_metadata_variables_with_categories", "value": csv_value(priority_official_metadata_summary, "priority_official_metadata_variables_with_categories", "0"), "interpretation": "Priority candidate variables with official category/value-label evidence."},
        {"metric": "priority_credentialed_acquisition_dataset_rows", "value": csv_value(priority_credentialed_acquisition_summary, "priority_credentialed_acquisition_dataset_rows", "0"), "interpretation": "Priority datasets with credentialed raw-acquisition instructions."},
        {"metric": "priority_credentialed_acquisition_full_file_rows", "value": csv_value(priority_credentialed_acquisition_summary, "priority_credentialed_acquisition_full_file_rows", "0"), "interpretation": "Official metadata file rows in the credentialed acquisition manifest."},
        {"metric": "priority_credentialed_acquisition_core_file_rows", "value": csv_value(priority_credentialed_acquisition_summary, "priority_credentialed_acquisition_core_file_rows", "0"), "interpretation": "Priority core file rows to confirm after official raw download."},
        {"metric": "priority_credentialed_acquisition_targets_missing_before_download", "value": csv_value(priority_credentialed_acquisition_summary, "priority_credentialed_acquisition_targets_missing_before_download", "0"), "interpretation": "Priority target modules still missing before credentialed download."},
        {"metric": "priority_endpoint_matrix_endpoint_rows", "value": csv_value(priority_endpoint_matrix_summary, "priority_endpoint_matrix_endpoint_rows", "0"), "interpretation": "Official endpoint probes across priority and backup datasets."},
        {"metric": "priority_endpoint_matrix_variable_api_dataset_rows", "value": csv_value(priority_endpoint_matrix_summary, "priority_endpoint_matrix_variable_api_dataset_rows", "0"), "interpretation": "Datasets with a public variable metadata API endpoint."},
        {"metric": "priority_endpoint_matrix_raw_download_candidate_rows", "value": csv_value(priority_endpoint_matrix_summary, "priority_endpoint_matrix_raw_download_candidate_rows", "0"), "interpretation": "Raw download candidate endpoints detected by the official endpoint matrix."},
        {"metric": "priority_endpoint_matrix_credentialed_download_required_rows", "value": csv_value(priority_endpoint_matrix_summary, "priority_endpoint_matrix_credentialed_download_required_rows", "0"), "interpretation": "Datasets still requiring credentialed raw download."},
        {"metric": "priority_core_file_endpoint_core_file_rows", "value": csv_value(priority_core_file_endpoint_summary, "priority_core_file_endpoint_core_file_rows", "0"), "interpretation": "Priority core file rows covered by the file endpoint matrix."},
        {"metric": "priority_core_file_endpoint_probed_download_rows", "value": csv_value(priority_core_file_endpoint_summary, "priority_core_file_endpoint_probed_download_rows", "0"), "interpretation": "File-level download route probes for priority core files."},
        {"metric": "priority_core_file_endpoint_raw_candidate_rows", "value": csv_value(priority_core_file_endpoint_summary, "priority_core_file_endpoint_raw_candidate_rows", "0"), "interpretation": "Potential public raw file candidates detected by the core-file endpoint matrix."},
        {"metric": "priority_core_file_endpoint_credentialed_download_required_rows", "value": csv_value(priority_core_file_endpoint_summary, "priority_core_file_endpoint_credentialed_download_required_rows", "0"), "interpretation": "Datasets still requiring credentialed raw package acquisition after file-level route probes."},
        {"metric": "priority_threshold_campaign_phase1_10_wave_rows", "value": csv_value(priority_threshold_campaign_summary, "priority_threshold_campaign_phase1_10_wave_rows", "0"), "interpretation": "Core campaign rows for the 10 country-wave double-failure threshold."},
        {"metric": "priority_threshold_campaign_phase2_sixth_country_backup_rows", "value": csv_value(priority_threshold_campaign_summary, "priority_threshold_campaign_phase2_sixth_country_backup_rows", "0"), "interpretation": "Backup-country rows retained for the sixth financial-protection country threshold."},
        {"metric": "priority_threshold_campaign_minimum_download_rows_for_formal_thresholds", "value": csv_value(priority_threshold_campaign_summary, "priority_threshold_campaign_minimum_download_rows_for_formal_thresholds", "0"), "interpretation": "Minimum raw downloads needed if every selected wave verifies."},
        {"metric": "priority_threshold_campaign_recommended_download_rows", "value": csv_value(priority_threshold_campaign_summary, "priority_threshold_campaign_recommended_download_rows", "0"), "interpretation": "Recommended raw downloads including backup countries to reduce threshold failure risk."},
        {"metric": "priority_first_pass_dataset_rows", "value": csv_value(priority_first_pass_summary, "priority_first_pass_dataset_rows", "0"), "interpretation": "Priority and backup country-waves covered by the first-pass review queue."},
        {"metric": "priority_first_pass_requirement_rows", "value": csv_value(priority_first_pass_summary, "priority_first_pass_requirement_rows", "0"), "interpretation": "Requirement coverage rows in the first-pass variable review queue."},
        {"metric": "priority_first_pass_selected_variable_rows", "value": csv_value(priority_first_pass_summary, "priority_first_pass_selected_variable_rows", "0"), "interpretation": "Selected metadata candidate variables queued for first-pass raw-value review after download."},
        {"metric": "priority_first_pass_raw_package_received_rows", "value": csv_value(priority_first_pass_summary, "priority_first_pass_raw_package_received_rows", "0"), "interpretation": "First-pass queue datasets with complete or target-covered original raw package receipt."},
        {"metric": "priority_first_pass_ready_after_download_rows", "value": csv_value(priority_first_pass_summary, "priority_first_pass_ready_after_download_rows", "0"), "interpretation": "Selected variable rows ready for immediate first-pass raw-value review."},
        {"metric": "priority_download_execution_packet_rows", "value": csv_value(priority_download_execution_summary, "priority_download_execution_packet_rows", "0"), "interpretation": "Manual credentialed download execution packet rows."},
        {"metric": "priority_download_execution_core_file_rows", "value": csv_value(priority_download_execution_summary, "priority_download_execution_core_file_rows", "0"), "interpretation": "Core file acceptance rows carried into the download execution packet."},
        {"metric": "priority_download_execution_first_pass_variable_rows", "value": csv_value(priority_download_execution_summary, "priority_download_execution_first_pass_variable_rows", "0"), "interpretation": "First-pass selected variable rows carried into the download execution packet."},
        {"metric": "priority_download_execution_raw_package_received_rows", "value": csv_value(priority_download_execution_summary, "priority_download_execution_raw_package_received_rows", "0"), "interpretation": "Download execution packet datasets with original raw package receipt."},
        {"metric": "priority_lsms_alignment_current_campaign_rows", "value": csv_value(priority_lsms_alignment_summary, "priority_lsms_alignment_current_campaign_rows", "0"), "interpretation": "Current priority/backup campaign rows audited for LSMS/ISA family alignment."},
        {"metric": "priority_lsms_alignment_off_family_core_wave_rows", "value": csv_value(priority_lsms_alignment_summary, "priority_lsms_alignment_off_family_core_wave_rows", "0"), "interpretation": "Core priority waves that should be replaced or augmented before manual download execution."},
        {"metric": "priority_lsms_alignment_strong_replacement_candidate_rows", "value": csv_value(priority_lsms_alignment_summary, "priority_lsms_alignment_strong_replacement_candidate_rows", "0"), "interpretation": "Strong Malawi/Uganda LSMS/ISA replacement candidates found in the screening inventory."},
        {"metric": "priority_lsms_alignment_campaign_decision", "value": csv_value(priority_lsms_alignment_summary, "priority_lsms_alignment_campaign_decision", "missing"), "interpretation": "Family-alignment campaign decision before credentialed downloads."},
        {"metric": "priority_lsms_refocused_wave_plan_rows", "value": csv_value(priority_lsms_refocused_summary, "priority_lsms_refocused_wave_plan_rows", "0"), "interpretation": "Selected wave-plan rows after replacing off-family core waves."},
        {"metric": "priority_lsms_refocused_core_lsms_aligned_rows", "value": csv_value(priority_lsms_refocused_summary, "priority_lsms_refocused_core_lsms_aligned_rows", "0"), "interpretation": "Refocused core rows aligned with LSMS/ISA or LSMS-style survey families."},
        {"metric": "priority_lsms_refocused_acquisition_queue_rows", "value": csv_value(priority_lsms_refocused_summary, "priority_lsms_refocused_acquisition_queue_rows", "0"), "interpretation": "Refocused selected and backup manual acquisition targets."},
        {"metric": "priority_lsms_refocused_requirement_rows", "value": csv_value(priority_lsms_refocused_summary, "priority_lsms_refocused_requirement_rows", "0"), "interpretation": "Requirement rows for refocused selected and backup targets."},
        {"metric": "priority_lsms_refocused_data_write_status", "value": csv_value(priority_lsms_refocused_summary, "priority_lsms_refocused_data_write_status", "missing"), "interpretation": "Promoted-data write status for the refocused queue."},
        {"metric": "priority_lsms_raw_intake_dataset_rows", "value": csv_value(priority_lsms_raw_intake_summary, "priority_lsms_raw_intake_dataset_rows", "0"), "interpretation": "Refocused LSMS/ISA targets covered by raw-package intake ledger."},
        {"metric": "priority_lsms_raw_intake_original_file_rows", "value": csv_value(priority_lsms_raw_intake_summary, "priority_lsms_raw_intake_original_file_rows", "0"), "interpretation": "Non-generated original package/documentation candidates found in target folders."},
        {"metric": "priority_lsms_raw_intake_missing_package_rows", "value": csv_value(priority_lsms_raw_intake_summary, "priority_lsms_raw_intake_missing_package_rows", "0"), "interpretation": "Refocused targets with no original package files yet."},
        {"metric": "priority_lsms_raw_intake_blocked_requirement_rows", "value": csv_value(priority_lsms_raw_intake_summary, "priority_lsms_raw_intake_blocked_requirement_rows", "0"), "interpretation": "Raw-package acceptance requirements still blocked."},
        {"metric": "priority_lsms_raw_intake_data_write_status", "value": csv_value(priority_lsms_raw_intake_summary, "priority_lsms_raw_intake_data_write_status", "missing"), "interpretation": "Promoted-data write status for the raw intake packet."},
        {"metric": "priority_lsms_archive_preflight_dataset_rows", "value": csv_value(priority_lsms_archive_preflight_summary, "priority_lsms_archive_preflight_dataset_rows", "0"), "interpretation": "Refocused targets covered by archive/direct-file preflight."},
        {"metric": "priority_lsms_archive_preflight_direct_file_rows", "value": csv_value(priority_lsms_archive_preflight_summary, "priority_lsms_archive_preflight_direct_file_rows", "0"), "interpretation": "Direct non-generated original files detected by archive preflight."},
        {"metric": "priority_lsms_archive_preflight_archive_member_rows", "value": csv_value(priority_lsms_archive_preflight_summary, "priority_lsms_archive_preflight_archive_member_rows", "0"), "interpretation": "Readable archive member rows detected without extraction."},
        {"metric": "priority_lsms_archive_preflight_blocked_dataset_rows", "value": csv_value(priority_lsms_archive_preflight_summary, "priority_lsms_archive_preflight_blocked_dataset_rows", "0"), "interpretation": "Refocused targets still blocked before schema/manual raw review."},
        {"metric": "priority_lsms_archive_preflight_blocked_requirement_rows", "value": csv_value(priority_lsms_archive_preflight_summary, "priority_lsms_archive_preflight_blocked_requirement_rows", "0"), "interpretation": "Archive preflight requirement rows still blocked."},
        {"metric": "priority_lsms_archive_preflight_data_write_status", "value": csv_value(priority_lsms_archive_preflight_summary, "priority_lsms_archive_preflight_data_write_status", "missing"), "interpretation": "Promoted-data write status for archive preflight."},
        {"metric": "priority_synthesis_blueprint_schema_rows", "value": csv_value(priority_synthesis_summary, "priority_synthesis_blueprint_schema_rows", "0"), "interpretation": "Target output-column rows for promoted household-climate dataset synthesis."},
        {"metric": "priority_synthesis_blueprint_blocked_required_rows", "value": csv_value(priority_synthesis_summary, "priority_synthesis_blueprint_blocked_required_rows", "0"), "interpretation": "Required promoted-dataset output columns still blocked."},
        {"metric": "priority_synthesis_blueprint_join_ready_rows", "value": csv_value(priority_synthesis_summary, "priority_synthesis_blueprint_join_ready_rows", "0"), "interpretation": "Priority country-waves ready for promoted dataset build joins."},
        {"metric": "priority_country_wave_packet_rows", "value": csv_value(priority_packet_summary, "priority_country_wave_packet_rows", "0"), "interpretation": "Priority country-wave promotion packets built."},
        {"metric": "priority_country_wave_packet_passed_gate_rows", "value": csv_value(priority_packet_summary, "priority_country_wave_packet_passed_gate_rows", "0"), "interpretation": "Priority packet gates currently passing."},
        {"metric": "priority_country_wave_packet_failed_gate_rows", "value": csv_value(priority_packet_summary, "priority_country_wave_packet_failed_gate_rows", "0"), "interpretation": "Priority packet gates still blocking promotion."},
        {"metric": "priority_country_wave_packet_official_metadata_ready_rows", "value": csv_value(priority_packet_summary, "priority_country_wave_packet_official_metadata_ready_rows", "0"), "interpretation": "Priority packets with official DDI/XML metadata evidence extracted."},
        {"metric": "priority_country_wave_packet_endpoint_matrix_ready_rows", "value": csv_value(priority_packet_summary, "priority_country_wave_packet_endpoint_matrix_ready_rows", "0"), "interpretation": "Priority packets with official endpoint matrix completed."},
        {"metric": "priority_country_wave_packet_credentialed_acquisition_ready_rows", "value": csv_value(priority_packet_summary, "priority_country_wave_packet_credentialed_acquisition_ready_rows", "0"), "interpretation": "Priority packets with credentialed raw acquisition ledger prepared."},
        {"metric": "priority_country_wave_packet_analysis_ready_rows", "value": csv_value(priority_packet_summary, "priority_country_wave_packet_analysis_ready_rows", "0"), "interpretation": "Priority packets ready for promoted data writes."},
        {"metric": "analysis_dataset_promotion_audit_rows", "value": csv_value(analysis_promotion_summary, "analysis_dataset_promotion_audit_rows", "0"), "interpretation": "Analysis dataset promotion targets checked."},
        {"metric": "analysis_dataset_promotion_blocked_rows", "value": csv_value(analysis_promotion_summary, "analysis_dataset_promotion_blocked_rows", "0"), "interpretation": "Promotion targets blocked from data/."},
        {"metric": "analysis_dataset_promotion_promoted_rows", "value": csv_value(analysis_promotion_summary, "analysis_dataset_promotion_promoted_rows", "0"), "interpretation": "Promotion targets allowed for data/ writes; limited core/outcome/exposure/linked diagnostic files are allowed while model-ready data remain blocked."},
        {"metric": "analysis_dataset_promotion_data_file_count", "value": csv_value(analysis_promotion_summary, "analysis_dataset_promotion_data_file_count", "0"), "interpretation": "Files currently present under data/."},
        {"metric": "analysis_dataset_promotion_verified_recipe_candidates", "value": csv_value(analysis_promotion_summary, "analysis_dataset_promotion_verified_recipe_candidates", "0"), "interpretation": "Verified recipe candidates carried into the promotion-barrier audit."},
        {"metric": "analysis_dataset_promotion_ready_country_waves", "value": csv_value(analysis_promotion_summary, "analysis_dataset_promotion_ready_country_waves", "0"), "interpretation": "Ready country-waves carried into the promotion-barrier audit."},
        {"metric": "analysis_dataset_promotion_alb2002_temp_core_rows", "value": csv_value(analysis_promotion_summary, "analysis_dataset_promotion_alb2002_temp_core_rows", "0"), "interpretation": "ALB_2002 temp core rows carried into the promotion-barrier audit."},
        {"metric": "analysis_dataset_promotion_alb2002_weight_positive_rows", "value": csv_value(analysis_promotion_summary, "analysis_dataset_promotion_alb2002_weight_positive_rows", "0"), "interpretation": "ALB_2002 positive household-weight rows carried into the promotion-barrier audit."},
        {"metric": "analysis_dataset_promotion_alb2002_weight_key_match_rows", "value": csv_value(analysis_promotion_summary, "analysis_dataset_promotion_alb2002_weight_key_match_rows", "0"), "interpretation": "ALB_2002 weight-file key matches carried into the promotion-barrier audit."},
        {"metric": "analysis_dataset_promotion_alb2002_weighted_inference_ready_rows", "value": csv_value(analysis_promotion_summary, "analysis_dataset_promotion_alb2002_weighted_inference_ready_rows", "0"), "interpretation": "ALB_2002 rows ready for promoted weighted inference; should remain zero."},
        {"metric": "analysis_dataset_promotion_alb2002_harmonized_ready_rows", "value": csv_value(analysis_promotion_summary, "analysis_dataset_promotion_alb2002_harmonized_ready_rows", "0"), "interpretation": "ALB_2002 harmonized rows ready for promotion; should remain zero."},
        {"metric": "analysis_dataset_promotion_alb2002_outcome_ready_rows", "value": csv_value(analysis_promotion_summary, "analysis_dataset_promotion_alb2002_outcome_ready_rows", "0"), "interpretation": "ALB_2002 outcome rows ready for promotion; should remain zero."},
        {"metric": "analysis_dataset_promotion_alb2002_climate_linkage_ready_rows", "value": csv_value(analysis_promotion_summary, "analysis_dataset_promotion_alb2002_climate_linkage_ready_rows", "0"), "interpretation": "ALB_2002 climate-linkage rows ready for promotion; should remain zero."},
        {"metric": "analysis_dataset_promotion_limited_harmonized_core_rows", "value": csv_value(analysis_promotion_summary, "analysis_dataset_promotion_limited_harmonized_core_rows", "0"), "interpretation": "Rows written to data/harmonized_household.csv under limited scope."},
        {"metric": "analysis_dataset_promotion_limited_harmonized_core_data_write_ready_rows", "value": csv_value(analysis_promotion_summary, "analysis_dataset_promotion_limited_harmonized_core_data_write_ready_rows", "0"), "interpretation": "Rows allowed for data/ write only as limited harmonized household core."},
        {"metric": "analysis_dataset_promotion_limited_harmonized_core_final_outcome_ready_rows", "value": csv_value(analysis_promotion_summary, "analysis_dataset_promotion_limited_harmonized_core_final_outcome_ready_rows", "0"), "interpretation": "Rows ready for final outcomes; should remain zero."},
        {"metric": "analysis_dataset_promotion_limited_harmonized_core_climate_linkage_ready_rows", "value": csv_value(analysis_promotion_summary, "analysis_dataset_promotion_limited_harmonized_core_climate_linkage_ready_rows", "0"), "interpretation": "Rows ready for climate linkage; should remain zero."},
        {"metric": "analysis_dataset_promotion_limited_financial_outcome_rows", "value": csv_value(analysis_promotion_summary, "analysis_dataset_promotion_limited_financial_outcome_rows", "0"), "interpretation": "Rows written to data/household_outcomes.csv under limited CHE-only scope."},
        {"metric": "analysis_dataset_promotion_limited_financial_outcome_data_write_ready_rows", "value": csv_value(analysis_promotion_summary, "analysis_dataset_promotion_limited_financial_outcome_data_write_ready_rows", "0"), "interpretation": "Rows allowed for data/ write only as limited CHE10/CHE25 outcomes."},
        {"metric": "analysis_dataset_promotion_limited_financial_outcome_che10_rows", "value": csv_value(analysis_promotion_summary, "analysis_dataset_promotion_limited_financial_outcome_che10_rows", "0"), "interpretation": "Limited CHE10 outcome rows."},
        {"metric": "analysis_dataset_promotion_limited_financial_outcome_che25_rows", "value": csv_value(analysis_promotion_summary, "analysis_dataset_promotion_limited_financial_outcome_che25_rows", "0"), "interpretation": "Limited CHE25 outcome rows."},
        {"metric": "analysis_dataset_promotion_limited_financial_outcome_sdg382_ready_rows", "value": csv_value(analysis_promotion_summary, "analysis_dataset_promotion_limited_financial_outcome_sdg382_ready_rows", "0"), "interpretation": "Rows ready for SDG 3.8.2; should remain zero."},
        {"metric": "analysis_dataset_promotion_limited_financial_outcome_access_ready_rows", "value": csv_value(analysis_promotion_summary, "analysis_dataset_promotion_limited_financial_outcome_access_ready_rows", "0"), "interpretation": "Rows ready for access outcomes; should remain zero."},
        {"metric": "analysis_dataset_promotion_limited_financial_outcome_composite_ready_rows", "value": csv_value(analysis_promotion_summary, "analysis_dataset_promotion_limited_financial_outcome_composite_ready_rows", "0"), "interpretation": "Rows ready for composite outcomes; should remain zero."},
        {"metric": "analysis_dataset_promotion_limited_financial_outcome_climate_linkage_ready_rows", "value": csv_value(analysis_promotion_summary, "analysis_dataset_promotion_limited_financial_outcome_climate_linkage_ready_rows", "0"), "interpretation": "Rows ready for climate linkage; should remain zero."},
        {"metric": "analysis_dataset_promotion_limited_climate_exposure_rows", "value": csv_value(analysis_promotion_summary, "analysis_dataset_promotion_limited_climate_exposure_rows", "0"), "interpretation": "Rows written to data/climate_exposures_nasa_power.csv under limited fallback scope."},
        {"metric": "analysis_dataset_promotion_limited_climate_exposure_data_write_ready_rows", "value": csv_value(analysis_promotion_summary, "analysis_dataset_promotion_limited_climate_exposure_data_write_ready_rows", "0"), "interpretation": "Rows allowed for data/ write only as limited fallback climate exposures."},
        {"metric": "analysis_dataset_promotion_limited_climate_exposure_climate_linkage_ready_rows", "value": csv_value(analysis_promotion_summary, "analysis_dataset_promotion_limited_climate_exposure_climate_linkage_ready_rows", "0"), "interpretation": "Rows ready for final climate linkage; should remain zero."},
        {"metric": "analysis_dataset_promotion_limited_climate_linked_rows", "value": csv_value(analysis_promotion_summary, "analysis_dataset_promotion_limited_climate_linked_rows", "0"), "interpretation": "Rows written to data/climate_linked_household.csv under limited diagnostic scope."},
        {"metric": "analysis_dataset_promotion_limited_climate_linked_data_write_ready_rows", "value": csv_value(analysis_promotion_summary, "analysis_dataset_promotion_limited_climate_linked_data_write_ready_rows", "0"), "interpretation": "Rows allowed for data/ write only as a limited linked diagnostic."},
        {"metric": "analysis_dataset_promotion_limited_climate_linked_descriptive_ready_rows", "value": csv_value(analysis_promotion_summary, "analysis_dataset_promotion_limited_climate_linked_descriptive_ready_rows", "0"), "interpretation": "Limited linked rows ready for descriptive diagnostics; should remain zero."},
        {"metric": "analysis_dataset_promotion_limited_climate_linked_predictive_ml_ready_rows", "value": csv_value(analysis_promotion_summary, "analysis_dataset_promotion_limited_climate_linked_predictive_ml_ready_rows", "0"), "interpretation": "Limited linked rows ready for predictive ML; should remain zero."},
        {"metric": "analysis_dataset_promotion_limited_climate_linked_reduced_form_ready_rows", "value": csv_value(analysis_promotion_summary, "analysis_dataset_promotion_limited_climate_linked_reduced_form_ready_rows", "0"), "interpretation": "Limited linked rows ready for reduced-form estimation; should remain zero."},
        {"metric": "analysis_dataset_promotion_limited_climate_linked_robustness_ready_rows", "value": csv_value(analysis_promotion_summary, "analysis_dataset_promotion_limited_climate_linked_robustness_ready_rows", "0"), "interpretation": "Limited linked rows ready for robustness checks; should remain zero."},
        {"metric": "analysis_dataset_promotion_limited_climate_linked_analysis_ready_rows", "value": csv_value(analysis_promotion_summary, "analysis_dataset_promotion_limited_climate_linked_analysis_ready_rows", "0"), "interpretation": "Limited linked rows ready for final analysis; should remain zero."},
        {"metric": "analysis_dataset_promotion_current_decision", "value": csv_value(analysis_promotion_summary, "analysis_dataset_promotion_current_decision", "missing"), "interpretation": "Current fail-closed analysis dataset promotion decision."},
        {"metric": "alb2002_harmonized_household_core_rows", "value": csv_value(alb2002_harmonized_core_summary, "alb2002_harmonized_household_core_rows", "0"), "interpretation": "Rows in the limited ALB_2002 harmonized household core."},
        {"metric": "alb2002_harmonized_household_core_final_outcome_ready_rows", "value": csv_value(alb2002_harmonized_core_summary, "alb2002_harmonized_household_core_final_outcome_ready_rows", "0"), "interpretation": "Limited-core rows ready for final outcomes; should remain zero."},
        {"metric": "alb2002_harmonized_household_core_climate_linkage_ready_rows", "value": csv_value(alb2002_harmonized_core_summary, "alb2002_harmonized_household_core_climate_linkage_ready_rows", "0"), "interpretation": "Limited-core rows ready for climate linkage; should remain zero."},
        {"metric": "alb2002_limited_financial_outcome_rows", "value": csv_value(alb2002_limited_financial_summary, "alb2002_limited_financial_outcome_rows", "0"), "interpretation": "Rows in the limited ALB_2002 CHE-only outcome file."},
        {"metric": "alb2002_limited_financial_outcome_che10_rows", "value": csv_value(alb2002_limited_financial_summary, "alb2002_limited_financial_outcome_che10_rows", "0"), "interpretation": "Limited CHE10 rows."},
        {"metric": "alb2002_limited_financial_outcome_che25_rows", "value": csv_value(alb2002_limited_financial_summary, "alb2002_limited_financial_outcome_che25_rows", "0"), "interpretation": "Limited CHE25 rows."},
        {"metric": "alb2002_limited_financial_outcome_climate_linkage_ready_rows", "value": csv_value(alb2002_limited_financial_summary, "alb2002_limited_financial_outcome_climate_linkage_ready_rows", "0"), "interpretation": "Limited-outcome rows ready for climate linkage; should remain zero."},
        {"metric": "alb2002_limited_climate_exposure_rows", "value": csv_value(alb2002_limited_climate_summary, "alb2002_limited_climate_exposure_rows", "0"), "interpretation": "Rows in the limited ALB_2002 NASA POWER exposure file."},
        {"metric": "alb2002_limited_climate_exposure_climate_linkage_ready_rows", "value": csv_value(alb2002_limited_climate_summary, "alb2002_limited_climate_exposure_climate_linkage_ready_rows", "0"), "interpretation": "Limited-exposure rows ready for final climate linkage; should remain zero."},
        {"metric": "alb2002_limited_climate_linked_rows", "value": csv_value(alb2002_limited_linked_summary, "alb2002_limited_climate_linked_rows", "0"), "interpretation": "Rows in the limited ALB_2002 climate-linked diagnostic file."},
        {"metric": "alb2002_limited_climate_linked_household_rows", "value": csv_value(alb2002_limited_linked_summary, "alb2002_limited_climate_linked_household_rows", "0"), "interpretation": "Households in the limited climate-linked diagnostic file."},
        {"metric": "alb2002_limited_climate_linked_window_rows", "value": csv_value(alb2002_limited_linked_summary, "alb2002_limited_climate_linked_window_rows", "0"), "interpretation": "Exposure windows per household in the limited linked file."},
        {"metric": "alb2002_limited_climate_linked_final_analysis_ready_rows", "value": csv_value(alb2002_limited_linked_summary, "alb2002_limited_climate_linked_final_analysis_ready_rows", "0"), "interpretation": "Limited linked rows ready for final analysis; should remain zero."},
        {"metric": "design_scorecard_rows", "value": csv_value(design_scorecard_current_summary, "design_scorecard_rows", "0"), "interpretation": "Rows in result/design_scorecard.csv after the current fail-closed refresh."},
        {"metric": "design_scorecard_current_rows", "value": csv_value(design_scorecard_current_summary, "design_scorecard_current_rows", "0"), "interpretation": "Current-state design rows appended to the broad metadata scorecard."},
        {"metric": "design_no_go_threshold_rows", "value": csv_value(design_scorecard_current_summary, "design_no_go_threshold_rows", "0"), "interpretation": "Current design no-go threshold rows."},
        {"metric": "design_scorecard_data_write_ready_rows", "value": csv_value(design_scorecard_current_summary, "design_scorecard_data_write_ready_rows", "0"), "interpretation": "Rows allowed for data/ write by the design scorecard; should remain zero."},
        {"metric": "design_scorecard_current_decision", "value": csv_value(design_scorecard_current_summary, "design_scorecard_current_decision", "missing"), "interpretation": "Current fail-closed design scorecard decision."},
        {"metric": "alb2002_promotion_gate_delta_rows", "value": csv_value(alb2002_promotion_gate_delta_summary, "alb2002_promotion_gate_delta_rows", "0"), "interpretation": "ALB_2002 promotion gate delta rows."},
        {"metric": "alb2002_promotion_gate_delta_hard_blocked_rows", "value": csv_value(alb2002_promotion_gate_delta_summary, "alb2002_promotion_gate_delta_hard_blocked_rows", "0"), "interpretation": "ALB_2002 hard-blocked promotion gates."},
        {"metric": "alb2002_promotion_gate_delta_data_write_ready_rows", "value": csv_value(alb2002_promotion_gate_delta_summary, "alb2002_promotion_gate_delta_data_write_ready_rows", "0"), "interpretation": "Rows allowed for data/ write by the ALB_2002 promotion delta audit; should remain zero."},
        {"metric": "alb2002_promotion_gate_delta_decision", "value": csv_value(alb2002_promotion_gate_delta_summary, "alb2002_promotion_gate_delta_decision", "missing"), "interpretation": "Current ALB_2002 promotion-gate delta decision."},
        {"metric": "alb2002_boundary_blocker_resolution_rows", "value": csv_value(alb2002_boundary_blocker_summary, "alb2002_boundary_blocker_resolution_rows", "0"), "interpretation": "ALB_2002 boundary blocker resolution rows."},
        {"metric": "alb2002_boundary_blocker_candidate_name_coverage_rows", "value": csv_value(alb2002_boundary_blocker_summary, "alb2002_boundary_blocker_candidate_name_coverage_rows", "0"), "interpretation": "Public boundary leads with complete candidate name coverage but no promotion."},
        {"metric": "alb2002_boundary_blocker_climate_linkage_ready_rows", "value": csv_value(alb2002_boundary_blocker_summary, "alb2002_boundary_blocker_climate_linkage_ready_rows", "0"), "interpretation": "Rows ready for ALB_2002 boundary climate-linkage promotion; should remain zero."},
        {"metric": "alb2002_boundary_blocker_current_decision", "value": csv_value(alb2002_boundary_blocker_summary, "alb2002_boundary_blocker_current_decision", "missing"), "interpretation": "Current consolidated ALB_2002 boundary-source decision."},
        {"metric": "alb2002_outcome_blocker_resolution_rows", "value": csv_value(alb2002_outcome_blocker_summary, "alb2002_outcome_blocker_resolution_rows", "0"), "interpretation": "ALB_2002 outcome blocker resolution rows."},
        {"metric": "alb2002_outcome_blocker_candidate_not_promoted_rows", "value": csv_value(alb2002_outcome_blocker_summary, "alb2002_outcome_blocker_candidate_not_promoted_rows", "0"), "interpretation": "Candidate ALB_2002 outcome rows with evidence but no final promotion."},
        {"metric": "alb2002_outcome_blocker_outcome_ready_rows", "value": csv_value(alb2002_outcome_blocker_summary, "alb2002_outcome_blocker_outcome_ready_rows", "0"), "interpretation": "Rows ready for final ALB_2002 outcome promotion; should remain zero."},
        {"metric": "alb2002_outcome_blocker_current_decision", "value": csv_value(alb2002_outcome_blocker_summary, "alb2002_outcome_blocker_current_decision", "missing"), "interpretation": "Current consolidated ALB_2002 outcome promotion decision."},
        {"metric": "alb2012_timing_geography_blocker_resolution_rows", "value": csv_value(alb2012_blocker_summary, "alb2012_timing_geography_blocker_resolution_rows", "0"), "interpretation": "ALB_2012 fallback blocker rows."},
        {"metric": "alb2012_timing_geography_blocker_hard_blocked_rows", "value": csv_value(alb2012_blocker_summary, "alb2012_timing_geography_blocker_hard_blocked_rows", "0"), "interpretation": "ALB_2012 rows hard-blocked from fallback promotion."},
        {"metric": "alb2012_timing_geography_blocker_climate_linkage_ready_rows", "value": csv_value(alb2012_blocker_summary, "alb2012_timing_geography_blocker_climate_linkage_ready_rows", "0"), "interpretation": "Rows ready for ALB_2012 climate-linkage fallback; should remain zero."},
        {"metric": "alb2012_timing_geography_blocker_current_decision", "value": csv_value(alb2012_blocker_summary, "alb2012_timing_geography_blocker_current_decision", "missing"), "interpretation": "Current consolidated ALB_2012 fallback decision."},
        {"metric": "alb2005_fallback_blocker_resolution_rows", "value": csv_value(alb2005_fallback_blocker_summary, "alb2005_fallback_blocker_resolution_rows", "0"), "interpretation": "ALB_2005 fallback blocker rows."},
        {"metric": "alb2005_fallback_blocker_hard_blocked_rows", "value": csv_value(alb2005_fallback_blocker_summary, "alb2005_fallback_blocker_hard_blocked_rows", "0"), "interpretation": "ALB_2005 rows hard-blocked from fallback promotion."},
        {"metric": "alb2005_fallback_blocker_harmonized_ready_rows", "value": csv_value(alb2005_fallback_blocker_summary, "alb2005_fallback_blocker_harmonized_ready_rows", "0"), "interpretation": "Rows ready for ALB_2005 harmonized-data fallback; should remain zero."},
        {"metric": "alb2005_fallback_blocker_outcome_ready_rows", "value": csv_value(alb2005_fallback_blocker_summary, "alb2005_fallback_blocker_outcome_ready_rows", "0"), "interpretation": "Rows ready for ALB_2005 outcome fallback; should remain zero."},
        {"metric": "alb2005_fallback_blocker_interview_timing_ready_rows", "value": csv_value(alb2005_fallback_blocker_summary, "alb2005_fallback_blocker_interview_timing_ready_rows", "0"), "interpretation": "Rows with verified ALB_2005 fallback interview timing; should remain zero."},
        {"metric": "alb2005_fallback_blocker_geography_ready_rows", "value": csv_value(alb2005_fallback_blocker_summary, "alb2005_fallback_blocker_geography_ready_rows", "0"), "interpretation": "Rows with promoted ALB_2005 fallback geography; should remain zero."},
        {"metric": "alb2005_fallback_blocker_climate_linkage_ready_rows", "value": csv_value(alb2005_fallback_blocker_summary, "alb2005_fallback_blocker_climate_linkage_ready_rows", "0"), "interpretation": "Rows ready for ALB_2005 climate-linkage fallback; should remain zero."},
        {"metric": "alb2005_fallback_blocker_data_write_ready_rows", "value": csv_value(alb2005_fallback_blocker_summary, "alb2005_fallback_blocker_data_write_ready_rows", "0"), "interpretation": "Rows allowed for ALB_2005 fallback data/ writes; should remain zero."},
        {"metric": "alb2005_fallback_blocker_current_decision", "value": csv_value(alb2005_fallback_blocker_summary, "alb2005_fallback_blocker_current_decision", "missing"), "interpretation": "Current consolidated ALB_2005 fallback decision."},
        {"metric": "alb2008_fallback_blocker_resolution_rows", "value": csv_value(alb2008_fallback_blocker_summary, "alb2008_fallback_blocker_resolution_rows", "0"), "interpretation": "ALB_2008 fallback blocker rows."},
        {"metric": "alb2008_fallback_blocker_hard_blocked_rows", "value": csv_value(alb2008_fallback_blocker_summary, "alb2008_fallback_blocker_hard_blocked_rows", "0"), "interpretation": "ALB_2008 rows hard-blocked from fallback promotion."},
        {"metric": "alb2008_fallback_blocker_interview_timing_ready_rows", "value": csv_value(alb2008_fallback_blocker_summary, "alb2008_fallback_blocker_interview_timing_ready_rows", "0"), "interpretation": "Rows with verified ALB_2008 fallback interview timing; should remain zero."},
        {"metric": "alb2008_fallback_blocker_geography_ready_rows", "value": csv_value(alb2008_fallback_blocker_summary, "alb2008_fallback_blocker_geography_ready_rows", "0"), "interpretation": "Rows with promoted ALB_2008 fallback geography; should remain zero."},
        {"metric": "alb2008_fallback_blocker_outcome_ready_rows", "value": csv_value(alb2008_fallback_blocker_summary, "alb2008_fallback_blocker_outcome_ready_rows", "0"), "interpretation": "Rows ready for ALB_2008 outcome fallback; should remain zero."},
        {"metric": "alb2008_fallback_blocker_climate_linkage_ready_rows", "value": csv_value(alb2008_fallback_blocker_summary, "alb2008_fallback_blocker_climate_linkage_ready_rows", "0"), "interpretation": "Rows ready for ALB_2008 climate-linkage fallback; should remain zero."},
        {"metric": "alb2008_fallback_blocker_data_write_ready_rows", "value": csv_value(alb2008_fallback_blocker_summary, "alb2008_fallback_blocker_data_write_ready_rows", "0"), "interpretation": "Rows allowed for ALB_2008 fallback data/ writes; should remain zero."},
        {"metric": "alb2008_fallback_blocker_current_decision", "value": csv_value(alb2008_fallback_blocker_summary, "alb2008_fallback_blocker_current_decision", "missing"), "interpretation": "Current consolidated ALB_2008 fallback decision."},
        {"metric": "no_go_pass_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "empirical_readiness_dashboard_summary.csv"), "no_go_pass_rows", "0"), "interpretation": "Pre-specified no-go rows passing."},
        {"metric": "no_go_blocked_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "empirical_readiness_dashboard_summary.csv"), "no_go_blocked_rows", "0"), "interpretation": "Pre-specified no-go rows blocked or failing."},
        {"metric": "alb2002_household_core_recipe_ready_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2002_household_core_candidate_summary.csv"), "alb2002_household_core_recipe_ready_rows", "0"), "interpretation": "ALB_2002 household core rows ready for data promotion."},
        {"metric": "alb2002_weight_design_positive_weight_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2002_weight_design_evidence_summary.csv"), "alb2002_weight_design_positive_weight_rows", "0"), "interpretation": "ALB_2002 readable positive household-weight rows."},
        {"metric": "alb2002_weight_design_candidate_key_match_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2002_weight_design_evidence_summary.csv"), "alb2002_weight_design_candidate_key_match_rows", "0"), "interpretation": "ALB_2002 readable weight-file key matches to the temp core."},
        {"metric": "alb2002_weight_design_weighted_inference_ready_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2002_weight_design_evidence_summary.csv"), "alb2002_weight_design_weighted_inference_ready_rows", "0"), "interpretation": "ALB_2002 rows ready for promoted weighted inference; should remain zero."},
        {"metric": "alb2002_che_candidate_household_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2002_che_candidate_outcome_summary.csv"), "alb2002_che_candidate_household_rows", "0"), "interpretation": "ALB_2002 temp-only household CHE candidate rows."},
        {"metric": "alb2002_che_candidate_che10_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2002_che_candidate_outcome_summary.csv"), "alb2002_che_candidate_che10_rows", "0"), "interpretation": "ALB_2002 candidate CHE10 rows under the period-aligned combined OOP policy."},
        {"metric": "alb2002_che_candidate_che10_weighted_rate", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2002_che_candidate_outcome_summary.csv"), "alb2002_che_candidate_che10_weighted_rate", "0"), "interpretation": "ALB_2002 candidate weighted CHE10 rate; audit only."},
        {"metric": "alb2002_che_candidate_che25_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2002_che_candidate_outcome_summary.csv"), "alb2002_che_candidate_che25_rows", "0"), "interpretation": "ALB_2002 candidate CHE25 rows under the period-aligned combined OOP policy."},
        {"metric": "alb2002_che_candidate_che25_weighted_rate", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2002_che_candidate_outcome_summary.csv"), "alb2002_che_candidate_che25_weighted_rate", "0"), "interpretation": "ALB_2002 candidate weighted CHE25 rate; audit only."},
        {"metric": "alb2002_che_candidate_outcome_promotion_ready_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2002_che_candidate_outcome_summary.csv"), "alb2002_che_candidate_outcome_promotion_ready_rows", "0"), "interpretation": "ALB_2002 candidate outcome rows ready for final promotion; should remain zero."},
        {"metric": "alb2002_access_candidate_household_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2002_access_candidate_outcome_summary.csv"), "alb2002_access_candidate_household_rows", "0"), "interpretation": "ALB_2002 temp-only household access candidate rows."},
        {"metric": "alb2002_access_candidate_composite_any_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2002_access_candidate_outcome_summary.csv"), "alb2002_access_candidate_composite_any_rows", "0"), "interpretation": "ALB_2002 temp-only composite any-access-barrier rows."},
        {"metric": "alb2002_access_candidate_composite_any_weighted_rate", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2002_access_candidate_outcome_summary.csv"), "alb2002_access_candidate_composite_any_weighted_rate", "0"), "interpretation": "ALB_2002 candidate weighted composite any-access-barrier rate; audit only."},
        {"metric": "alb2002_access_candidate_outcome_promotion_ready_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2002_access_candidate_outcome_summary.csv"), "alb2002_access_candidate_outcome_promotion_ready_rows", "0"), "interpretation": "ALB_2002 access candidate rows ready for final promotion; should remain zero."},
        {"metric": "alb2002_uhc_composite_candidate_household_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2002_uhc_composite_candidate_summary.csv"), "alb2002_uhc_composite_candidate_household_rows", "0"), "interpretation": "ALB_2002 temp-only composite UHC candidate rows."},
        {"metric": "alb2002_uhc_composite_candidate_che10_or_access_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2002_uhc_composite_candidate_summary.csv"), "alb2002_uhc_composite_candidate_che10_or_access_rows", "0"), "interpretation": "ALB_2002 temp-only CHE10-or-access candidate rows."},
        {"metric": "alb2002_uhc_composite_candidate_che10_or_access_weighted_rate", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2002_uhc_composite_candidate_summary.csv"), "alb2002_uhc_composite_candidate_che10_or_access_weighted_rate", "0"), "interpretation": "ALB_2002 candidate weighted CHE10-or-access rate; audit only."},
        {"metric": "alb2002_uhc_composite_candidate_che25_or_access_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2002_uhc_composite_candidate_summary.csv"), "alb2002_uhc_composite_candidate_che25_or_access_rows", "0"), "interpretation": "ALB_2002 temp-only CHE25-or-access candidate rows."},
        {"metric": "alb2002_uhc_composite_candidate_outcome_promotion_ready_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2002_uhc_composite_candidate_summary.csv"), "alb2002_uhc_composite_candidate_outcome_promotion_ready_rows", "0"), "interpretation": "ALB_2002 composite UHC candidate rows ready for final promotion; should remain zero."},
        {"metric": "alb2002_analysis_candidate_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2002_analysis_candidate_readiness_summary.csv"), "alb2002_analysis_candidate_rows", "0"), "interpretation": "ALB_2002 temp-only joined analysis-candidate household rows."},
        {"metric": "alb2002_analysis_candidate_complete_candidate_gates", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2002_analysis_candidate_readiness_summary.csv"), "alb2002_analysis_candidate_complete_candidate_gates", "0"), "interpretation": "ALB_2002 candidate field families with complete observed coverage, still not promoted."},
        {"metric": "alb2002_analysis_candidate_missing_gates", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2002_analysis_candidate_readiness_summary.csv"), "alb2002_analysis_candidate_missing_gates", "0"), "interpretation": "ALB_2002 candidate field families with missing required coverage."},
        {"metric": "alb2002_analysis_candidate_harmonized_ready_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2002_analysis_candidate_readiness_summary.csv"), "alb2002_analysis_candidate_harmonized_ready_rows", "0"), "interpretation": "ALB_2002 analysis-candidate rows ready for harmonized data promotion; should remain zero."},
        {"metric": "alb2002_analysis_candidate_data_write_ready_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2002_analysis_candidate_readiness_summary.csv"), "alb2002_analysis_candidate_data_write_ready_rows", "0"), "interpretation": "ALB_2002 analysis-candidate rows allowed to be written to data/; should remain zero."},
        {"metric": "alb2002_climate_centroid_input_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2002_climate_centroid_exposure_summary.csv"), "alb2002_climate_centroid_input_rows", "0"), "interpretation": "ALB_2002 observed district-month cells used for the temp-only climate centroid stress test."},
        {"metric": "alb2002_climate_centroid_exposure_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2002_climate_centroid_exposure_summary.csv"), "alb2002_climate_centroid_exposure_rows", "0"), "interpretation": "ALB_2002 temp-only NASA POWER centroid exposure rows."},
        {"metric": "alb2002_climate_centroid_nasa_api_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2002_climate_centroid_exposure_summary.csv"), "alb2002_climate_centroid_nasa_api_rows", "0"), "interpretation": "ALB_2002 district centroid API/cache manifest rows."},
        {"metric": "alb2002_climate_centroid_nasa_failed_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2002_climate_centroid_exposure_summary.csv"), "alb2002_climate_centroid_nasa_failed_rows", "0"), "interpretation": "ALB_2002 NASA POWER district centroid requests that failed."},
        {"metric": "alb2002_climate_centroid_climate_linkage_ready_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2002_climate_centroid_exposure_summary.csv"), "alb2002_climate_centroid_climate_linkage_ready_rows", "0"), "interpretation": "ALB_2002 centroid exposure rows ready for promoted climate linkage; should remain zero."},
        {"metric": "alb2002_climate_centroid_data_write_ready_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2002_climate_centroid_exposure_summary.csv"), "alb2002_climate_centroid_data_write_ready_rows", "0"), "interpretation": "ALB_2002 centroid exposure rows allowed for data/ write; should remain zero."},
        {"metric": "alb2002_climate_shock_candidate_exposure_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2002_climate_shock_candidate_summary.csv"), "alb2002_climate_shock_candidate_exposure_rows", "0"), "interpretation": "ALB_2002 temp-only climate shock diagnostic rows."},
        {"metric": "alb2002_climate_shock_candidate_reference_group_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2002_climate_shock_candidate_summary.csv"), "alb2002_climate_shock_candidate_reference_group_rows", "0"), "interpretation": "ALB_2002 survey-month/window diagnostic reference groups."},
        {"metric": "alb2002_climate_shock_candidate_precip_z_nonmissing_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2002_climate_shock_candidate_summary.csv"), "alb2002_climate_shock_candidate_precip_z_nonmissing_rows", "0"), "interpretation": "ALB_2002 diagnostic rainfall z-score rows."},
        {"metric": "alb2002_climate_shock_candidate_temp_z_nonmissing_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2002_climate_shock_candidate_summary.csv"), "alb2002_climate_shock_candidate_temp_z_nonmissing_rows", "0"), "interpretation": "ALB_2002 diagnostic temperature z-score rows."},
        {"metric": "alb2002_climate_shock_candidate_combined_stress_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2002_climate_shock_candidate_summary.csv"), "alb2002_climate_shock_candidate_combined_stress_rows", "0"), "interpretation": "ALB_2002 diagnostic combined climate-stress rows; not accepted treatments."},
        {"metric": "alb2002_climate_shock_candidate_climate_linkage_ready_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2002_climate_shock_candidate_summary.csv"), "alb2002_climate_shock_candidate_climate_linkage_ready_rows", "0"), "interpretation": "ALB_2002 shock diagnostic rows ready for promoted climate linkage; should remain zero."},
        {"metric": "alb2002_climate_shock_candidate_data_write_ready_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2002_climate_shock_candidate_summary.csv"), "alb2002_climate_shock_candidate_data_write_ready_rows", "0"), "interpretation": "ALB_2002 shock diagnostic rows allowed for data/ write; should remain zero."},
        {"metric": "alb2002_climate_outcome_linked_candidate_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2002_climate_outcome_linked_candidate_summary.csv"), "alb2002_climate_outcome_linked_candidate_rows", "0"), "interpretation": "ALB_2002 temp-only household-window climate/outcome linked candidate rows."},
        {"metric": "alb2002_climate_outcome_linked_candidate_household_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2002_climate_outcome_linked_candidate_summary.csv"), "alb2002_climate_outcome_linked_candidate_household_rows", "0"), "interpretation": "ALB_2002 households represented in the linked candidate."},
        {"metric": "alb2002_climate_outcome_linked_candidate_window_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2002_climate_outcome_linked_candidate_summary.csv"), "alb2002_climate_outcome_linked_candidate_window_rows", "0"), "interpretation": "Diagnostic exposure windows per household in the linked candidate."},
        {"metric": "alb2002_climate_outcome_linked_candidate_unmatched_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2002_climate_outcome_linked_candidate_summary.csv"), "alb2002_climate_outcome_linked_candidate_unmatched_rows", "0"), "interpretation": "Linked rows without diagnostic climate windows; should remain zero."},
        {"metric": "alb2002_climate_outcome_linked_candidate_combined_stress_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2002_climate_outcome_linked_candidate_summary.csv"), "alb2002_climate_outcome_linked_candidate_combined_stress_rows", "0"), "interpretation": "ALB_2002 linked diagnostic combined climate-stress rows; not accepted treatment variables."},
        {"metric": "alb2002_climate_outcome_linked_candidate_climate_linkage_ready_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2002_climate_outcome_linked_candidate_summary.csv"), "alb2002_climate_outcome_linked_candidate_climate_linkage_ready_rows", "0"), "interpretation": "ALB_2002 linked rows ready for promoted climate linkage; should remain zero."},
        {"metric": "alb2002_climate_outcome_linked_candidate_data_write_ready_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2002_climate_outcome_linked_candidate_summary.csv"), "alb2002_climate_outcome_linked_candidate_data_write_ready_rows", "0"), "interpretation": "ALB_2002 linked rows allowed for data/ write; should remain zero."},
        {"metric": "alb2002_linked_candidate_descriptive_input_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2002_linked_candidate_descriptive_summary.csv"), "alb2002_linked_candidate_descriptive_input_rows", "0"), "interpretation": "ALB_2002 temp-only linked household-window rows screened descriptively."},
        {"metric": "alb2002_linked_candidate_descriptive_household_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2002_linked_candidate_descriptive_summary.csv"), "alb2002_linked_candidate_descriptive_household_rows", "0"), "interpretation": "Deduplicated ALB_2002 households used for candidate outcome rates."},
        {"metric": "alb2002_linked_candidate_descriptive_cell_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2002_linked_candidate_descriptive_summary.csv"), "alb2002_linked_candidate_descriptive_cell_rows", "0"), "interpretation": "Temp-only descriptive screen cell rows; not promoted descriptive diagnostics."},
        {"metric": "alb2002_linked_candidate_descriptive_combined_stress_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2002_linked_candidate_descriptive_summary.csv"), "alb2002_linked_candidate_descriptive_combined_stress_rows", "0"), "interpretation": "Long rows with diagnostic combined climate-stress flag in the descriptive screen."},
        {"metric": "alb2002_linked_candidate_descriptive_climate_linkage_ready_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2002_linked_candidate_descriptive_summary.csv"), "alb2002_linked_candidate_descriptive_climate_linkage_ready_rows", "0"), "interpretation": "Rows ready for promoted climate linkage in the descriptive screen; should remain zero."},
        {"metric": "alb2002_linked_candidate_descriptive_data_write_ready_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2002_linked_candidate_descriptive_summary.csv"), "alb2002_linked_candidate_descriptive_data_write_ready_rows", "0"), "interpretation": "Rows allowed for data/ write from the descriptive screen; should remain zero."},
        {"metric": "alb2002_provisional_outcome_ready_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2002_provisional_outcome_feasibility_summary.csv"), "alb2002_provisional_outcome_ready_rows", "0"), "interpretation": "ALB_2002 provisional outcome rows ready for final outcome promotion."},
        {"metric": "alb2002_outcome_semantics_outcome_ready_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2002_outcome_semantics_raw_value_summary.csv"), "alb2002_outcome_semantics_outcome_ready_rows", "0"), "interpretation": "ALB_2002 raw semantics rows ready for final outcome promotion."},
        {"metric": "alb2002_outcome_semantics_sdg382_ready_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2002_outcome_semantics_raw_value_summary.csv"), "alb2002_outcome_semantics_sdg382_ready_rows", "0"), "interpretation": "ALB_2002 raw semantics rows ready for SDG 3.8.2 construction."},
        {"metric": "alb2002_health_questionnaire_semantics_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2002_health_questionnaire_semantics_summary.csv"), "alb2002_health_questionnaire_semantics_rows", "0"), "interpretation": "ALB_2002 questionnaire-backed health semantics and skip-path rows."},
        {"metric": "alb2002_health_questionnaire_new_lek_unit_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2002_health_questionnaire_semantics_summary.csv"), "alb2002_health_questionnaire_new_lek_unit_rows", "0"), "interpretation": "ALB_2002 questionnaire rows explicitly recording NEW LEKS payment units."},
        {"metric": "alb2002_health_questionnaire_four_week_oop_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2002_health_questionnaire_semantics_summary.csv"), "alb2002_health_questionnaire_four_week_oop_rows", "0"), "interpretation": "ALB_2002 OOP item rows with past-four-week recall."},
        {"metric": "alb2002_health_questionnaire_twelve_month_oop_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2002_health_questionnaire_semantics_summary.csv"), "alb2002_health_questionnaire_twelve_month_oop_rows", "0"), "interpretation": "ALB_2002 OOP item rows with past-12-month recall."},
        {"metric": "alb2002_health_questionnaire_payment_positive_when_not_triggered_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2002_health_questionnaire_semantics_summary.csv"), "alb2002_health_questionnaire_payment_positive_when_not_triggered_rows", "0"), "interpretation": "ALB_2002 skipped payment downstream rows with positive values; should remain zero."},
        {"metric": "alb2002_health_questionnaire_outcome_ready_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2002_health_questionnaire_semantics_summary.csv"), "alb2002_health_questionnaire_outcome_ready_rows", "0"), "interpretation": "ALB_2002 questionnaire rows ready for final outcome promotion; should remain zero."},
        {"metric": "alb2002_health_questionnaire_sdg382_ready_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2002_health_questionnaire_semantics_summary.csv"), "alb2002_health_questionnaire_sdg382_ready_rows", "0"), "interpretation": "ALB_2002 questionnaire rows ready for SDG 3.8.2 construction; should remain zero."},
        {"metric": "alb2002_health_questionnaire_climate_linkage_ready_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2002_health_questionnaire_semantics_summary.csv"), "alb2002_health_questionnaire_climate_linkage_ready_rows", "0"), "interpretation": "ALB_2002 questionnaire rows ready for climate linkage; should remain zero."},
        {"metric": "alb2002_oop_aggregation_policy_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2002_oop_aggregation_policy_summary.csv"), "alb2002_oop_aggregation_policy_rows", "0"), "interpretation": "ALB_2002 OOP aggregation policy stress-test rows."},
        {"metric": "alb2002_oop_aggregation_policy_max_che10_rate", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2002_oop_aggregation_policy_summary.csv"), "alb2002_oop_aggregation_policy_max_che10_rate", "0"), "interpretation": "Maximum unweighted CHE10 rate across ALB_2002 stress-test policies; not a final estimate."},
        {"metric": "alb2002_oop_aggregation_policy_max_che25_rate", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2002_oop_aggregation_policy_summary.csv"), "alb2002_oop_aggregation_policy_max_che25_rate", "0"), "interpretation": "Maximum unweighted CHE25 rate across ALB_2002 stress-test policies; not a final estimate."},
        {"metric": "alb2002_oop_aggregation_policy_core_4w_match_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2002_oop_aggregation_policy_summary.csv"), "alb2002_oop_aggregation_policy_core_4w_match_rows", "0"), "interpretation": "ALB_2002 rows where recomputed four-week OOP matches the existing core candidate sum."},
        {"metric": "alb2002_oop_aggregation_policy_core_12m_match_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2002_oop_aggregation_policy_summary.csv"), "alb2002_oop_aggregation_policy_core_12m_match_rows", "0"), "interpretation": "ALB_2002 rows where recomputed 12-month OOP matches the existing core candidate sum."},
        {"metric": "alb2002_oop_aggregation_policy_outcome_ready_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2002_oop_aggregation_policy_summary.csv"), "alb2002_oop_aggregation_policy_outcome_ready_rows", "0"), "interpretation": "ALB_2002 OOP policy rows ready for outcome promotion; should remain zero."},
        {"metric": "alb2002_oop_aggregation_policy_sdg382_ready_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2002_oop_aggregation_policy_summary.csv"), "alb2002_oop_aggregation_policy_sdg382_ready_rows", "0"), "interpretation": "ALB_2002 OOP policy rows ready for SDG 3.8.2 promotion; should remain zero."},
        {"metric": "alb2002_oop_aggregation_policy_climate_linkage_ready_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2002_oop_aggregation_policy_summary.csv"), "alb2002_oop_aggregation_policy_climate_linkage_ready_rows", "0"), "interpretation": "ALB_2002 OOP policy rows ready for climate linkage; should remain zero."},
        {"metric": "alb2002_skip_missing_semantics_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2002_skip_missing_semantics_summary.csv"), "alb2002_skip_missing_semantics_rows", "0"), "interpretation": "ALB_2002 skip/missing semantics audit rows."},
        {"metric": "alb2002_skip_missing_payment_positive_when_not_triggered_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2002_skip_missing_semantics_summary.csv"), "alb2002_skip_missing_payment_positive_when_not_triggered_rows", "0"), "interpretation": "ALB_2002 skipped payment rows with positive downstream values; should remain zero."},
        {"metric": "alb2002_skip_missing_payment_zero_cells_when_not_triggered", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2002_skip_missing_semantics_summary.csv"), "alb2002_skip_missing_payment_zero_cells_when_not_triggered", "0"), "interpretation": "ALB_2002 skipped payment downstream cells equal zero; downstream decision audit records no positive leakage."},
        {"metric": "alb2002_skip_missing_payment_positive_cells_when_not_triggered", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2002_skip_missing_semantics_summary.csv"), "alb2002_skip_missing_payment_positive_cells_when_not_triggered", "0"), "interpretation": "ALB_2002 skipped payment downstream cells positive; should remain zero."},
        {"metric": "alb2002_skip_missing_outcome_ready_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2002_skip_missing_semantics_summary.csv"), "alb2002_skip_missing_outcome_ready_rows", "0"), "interpretation": "ALB_2002 skip/missing rows ready for outcome promotion; should remain zero."},
        {"metric": "alb2002_skip_missing_sdg382_ready_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2002_skip_missing_semantics_summary.csv"), "alb2002_skip_missing_sdg382_ready_rows", "0"), "interpretation": "ALB_2002 skip/missing rows ready for SDG 3.8.2 promotion; should remain zero."},
        {"metric": "alb2002_skip_missing_climate_linkage_ready_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2002_skip_missing_semantics_summary.csv"), "alb2002_skip_missing_climate_linkage_ready_rows", "0"), "interpretation": "ALB_2002 skip/missing rows ready for climate linkage; should remain zero."},
        {"metric": "alb2002_oop_skip_value_decision_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2002_oop_skip_value_decision_summary.csv"), "alb2002_oop_skip_value_decision_rows", "0"), "interpretation": "ALB_2002 OOP skip-value decision audit rows."},
        {"metric": "alb2002_oop_skip_value_payment_zero_skipped_cells", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2002_oop_skip_value_decision_summary.csv"), "alb2002_oop_skip_value_payment_zero_skipped_cells", "0"), "interpretation": "ALB_2002 zero-valued downstream payment cells when payment block was not triggered."},
        {"metric": "alb2002_oop_skip_value_payment_positive_skipped_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2002_oop_skip_value_decision_summary.csv"), "alb2002_oop_skip_value_payment_positive_skipped_rows", "0"), "interpretation": "ALB_2002 rows with positive downstream payment values when payment block was not triggered; should remain zero."},
        {"metric": "alb2002_oop_skip_value_payment_positive_skipped_cells", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2002_oop_skip_value_decision_summary.csv"), "alb2002_oop_skip_value_payment_positive_skipped_cells", "0"), "interpretation": "ALB_2002 positive downstream payment cells when payment block was not triggered; should remain zero."},
        {"metric": "alb2002_oop_skip_value_zero_skip_policy_ready_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2002_oop_skip_value_decision_summary.csv"), "alb2002_oop_skip_value_zero_skip_policy_ready_rows", "0"), "interpretation": "ALB_2002 rows supporting the narrow no-positive-leakage skipped-payment decision."},
        {"metric": "alb2002_oop_skip_value_oop_recall_scope_ready_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2002_oop_skip_value_decision_summary.csv"), "alb2002_oop_skip_value_oop_recall_scope_ready_rows", "0"), "interpretation": "ALB_2002 OOP recall scope rows accepted by skip-value audit; should remain zero."},
        {"metric": "alb2002_oop_skip_value_oop_inclusion_scope_ready_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2002_oop_skip_value_decision_summary.csv"), "alb2002_oop_skip_value_oop_inclusion_scope_ready_rows", "0"), "interpretation": "ALB_2002 OOP inclusion scope rows accepted by skip-value audit; should remain zero."},
        {"metric": "alb2002_oop_skip_value_outcome_ready_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2002_oop_skip_value_decision_summary.csv"), "alb2002_oop_skip_value_outcome_ready_rows", "0"), "interpretation": "ALB_2002 OOP skip-value rows ready for outcome promotion; should remain zero."},
        {"metric": "alb2002_access_need_denominator_policy_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2002_access_need_denominator_policy_summary.csv"), "alb2002_access_need_denominator_policy_rows", "0"), "interpretation": "ALB_2002 access/need denominator policy audit rows."},
        {"metric": "alb2002_access_need_q01_need_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2002_access_need_denominator_policy_summary.csv"), "alb2002_access_need_q01_need_rows", "0"), "interpretation": "ALB_2002 households not coded as no-one-needed-health-care in m5b_q01."},
        {"metric": "alb2002_access_need_person_need_household_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2002_access_need_denominator_policy_summary.csv"), "alb2002_access_need_person_need_household_rows", "0"), "interpretation": "ALB_2002 households with any Health A chronic/disability or sudden-illness proxy."},
        {"metric": "alb2002_access_need_composite_any_access_barrier_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2002_access_need_denominator_policy_summary.csv"), "alb2002_access_need_composite_any_access_barrier_rows", "0"), "interpretation": "ALB_2002 composite any-access-barrier candidate rows; not a final outcome."},
        {"metric": "alb2002_access_need_low_event_rate_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2002_access_need_denominator_policy_summary.csv"), "alb2002_access_need_low_event_rate_rows", "0"), "interpretation": "ALB_2002 access/need policies with event rate below 3 percent."},
        {"metric": "alb2002_access_need_outcome_ready_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2002_access_need_denominator_policy_summary.csv"), "alb2002_access_need_outcome_ready_rows", "0"), "interpretation": "ALB_2002 access/need rows ready for outcome promotion; should remain zero."},
        {"metric": "alb2002_access_need_climate_linkage_ready_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2002_access_need_denominator_policy_summary.csv"), "alb2002_access_need_climate_linkage_ready_rows", "0"), "interpretation": "ALB_2002 access/need rows ready for climate linkage; should remain zero."},
        {"metric": "alb2002_consumption_sdg_denominator_policy_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2002_consumption_sdg_denominator_policy_summary.csv"), "alb2002_consumption_sdg_denominator_policy_rows", "0"), "interpretation": "ALB_2002 consumption/SDG denominator policy audit rows."},
        {"metric": "alb2002_consumption_sdg_positive_total_consumption_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2002_consumption_sdg_denominator_policy_summary.csv"), "alb2002_consumption_sdg_positive_total_consumption_rows", "0"), "interpretation": "ALB_2002 rows with positive total consumption in the temp candidate."},
        {"metric": "alb2002_consumption_sdg_che10_4w_unreviewed_rate", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2002_consumption_sdg_denominator_policy_summary.csv"), "alb2002_consumption_sdg_che10_4w_unreviewed_rate", "0"), "interpretation": "Diagnostic ALB_2002 CHE10 rate using unreviewed four-week OOP; not a final outcome."},
        {"metric": "alb2002_consumption_sdg_che25_12m_unreviewed_rate", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2002_consumption_sdg_denominator_policy_summary.csv"), "alb2002_consumption_sdg_che25_12m_unreviewed_rate", "0"), "interpretation": "Diagnostic ALB_2002 CHE25 rate using unreviewed 12-month OOP; not a final outcome."},
        {"metric": "alb2002_consumption_sdg_spl_ready_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2002_consumption_sdg_denominator_policy_summary.csv"), "alb2002_consumption_sdg_spl_ready_rows", "0"), "interpretation": "ALB_2002 rows with SPL inputs accepted; should remain zero."},
        {"metric": "alb2002_consumption_sdg_ppp_cpi_ready_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2002_consumption_sdg_denominator_policy_summary.csv"), "alb2002_consumption_sdg_ppp_cpi_ready_rows", "0"), "interpretation": "ALB_2002 rows with PPP/CPI inputs accepted; should remain zero."},
        {"metric": "alb2002_consumption_sdg_discretionary_budget_ready_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2002_consumption_sdg_denominator_policy_summary.csv"), "alb2002_consumption_sdg_discretionary_budget_ready_rows", "0"), "interpretation": "ALB_2002 rows with discretionary-budget construction accepted; should remain zero."},
        {"metric": "alb2002_consumption_sdg_outcome_ready_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2002_consumption_sdg_denominator_policy_summary.csv"), "alb2002_consumption_sdg_outcome_ready_rows", "0"), "interpretation": "ALB_2002 consumption/SDG rows ready for outcome promotion; should remain zero."},
        {"metric": "alb2002_consumption_sdg_sdg382_ready_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2002_consumption_sdg_denominator_policy_summary.csv"), "alb2002_consumption_sdg_sdg382_ready_rows", "0"), "interpretation": "ALB_2002 rows ready for SDG 3.8.2 construction; should remain zero."},
        {"metric": "alb2002_consumption_sdg_climate_linkage_ready_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2002_consumption_sdg_denominator_policy_summary.csv"), "alb2002_consumption_sdg_climate_linkage_ready_rows", "0"), "interpretation": "ALB_2002 consumption/SDG rows ready for climate linkage; should remain zero."},
        {"metric": "alb2002_consumption_construction_source_audit_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2002_consumption_construction_source_summary.csv"), "alb2002_consumption_construction_source_audit_rows", "0"), "interpretation": "ALB_2002 public consumption-construction source audit rows."},
        {"metric": "alb2002_consumption_construction_do_file_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2002_consumption_construction_source_summary.csv"), "alb2002_consumption_construction_do_file_rows", "0"), "interpretation": "Extracted public ALB_2002 Stata do-files documenting consumption construction."},
        {"metric": "alb2002_consumption_construction_documentation_ready_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2002_consumption_construction_source_summary.csv"), "alb2002_consumption_construction_documentation_ready_rows", "0"), "interpretation": "ALB_2002 source-audit rows with accepted public construction documentation."},
        {"metric": "alb2002_consumption_construction_released_variable_mapping_ready_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2002_consumption_construction_source_summary.csv"), "alb2002_consumption_construction_released_variable_mapping_ready_rows", "0"), "interpretation": "ALB_2002 source-audit rows supporting local `totcons` to public `totcons3` mapping."},
        {"metric": "alb2002_consumption_construction_denominator_variant_ready_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2002_consumption_construction_source_summary.csv"), "alb2002_consumption_construction_denominator_variant_ready_rows", "0"), "interpretation": "ALB_2002 source-audit rows documenting the final total-budget denominator variant."},
        {"metric": "alb2002_consumption_construction_outcome_ready_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2002_consumption_construction_source_summary.csv"), "alb2002_consumption_construction_outcome_ready_rows", "0"), "interpretation": "ALB_2002 source-audit rows ready for outcome promotion; should remain zero."},
        {"metric": "alb2002_consumption_construction_sdg382_ready_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2002_consumption_construction_source_summary.csv"), "alb2002_consumption_construction_sdg382_ready_rows", "0"), "interpretation": "ALB_2002 source-audit rows ready for SDG 3.8.2 promotion; should remain zero."},
        {"metric": "alb2002_consumption_construction_climate_linkage_ready_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2002_consumption_construction_source_summary.csv"), "alb2002_consumption_construction_climate_linkage_ready_rows", "0"), "interpretation": "ALB_2002 source-audit rows ready for climate linkage; should remain zero."},
        {"metric": "alb2002_consumption_aggregate_crosswalk_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2002_consumption_aggregate_metadata_crosswalk_summary.csv"), "alb2002_consumption_aggregate_crosswalk_rows", "0"), "interpretation": "ALB_2002 consumption aggregate metadata/local evidence crosswalk rows."},
        {"metric": "alb2002_consumption_aggregate_crosswalk_metadata_catalog_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2002_consumption_aggregate_metadata_crosswalk_summary.csv"), "alb2002_consumption_aggregate_crosswalk_metadata_catalog_rows", "0"), "interpretation": "Local master metadata rows available for ALB_2002 aggregate verification; public source evidence now sits in the construction-source audit instead."},
        {"metric": "alb2002_consumption_aggregate_crosswalk_candidate_totcons_match_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2002_consumption_aggregate_metadata_crosswalk_summary.csv"), "alb2002_consumption_aggregate_crosswalk_candidate_totcons_match_rows", "0"), "interpretation": "ALB_2002 candidate total_consumption rows exactly matching raw `totcons`."},
        {"metric": "alb2002_consumption_aggregate_crosswalk_construction_source_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2002_consumption_aggregate_metadata_crosswalk_summary.csv"), "alb2002_consumption_aggregate_crosswalk_construction_source_rows", "0"), "interpretation": "Rows imported from the upstream ALB_2002 public consumption-construction source audit."},
        {"metric": "alb2002_consumption_aggregate_crosswalk_construction_do_file_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2002_consumption_aggregate_metadata_crosswalk_summary.csv"), "alb2002_consumption_aggregate_crosswalk_construction_do_file_rows", "0"), "interpretation": "Extracted public Stata do-files used as ALB_2002 denominator-construction evidence."},
        {"metric": "alb2002_consumption_aggregate_crosswalk_official_documentation_ready_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2002_consumption_aggregate_metadata_crosswalk_summary.csv"), "alb2002_consumption_aggregate_crosswalk_official_documentation_ready_rows", "0"), "interpretation": "ALB_2002 rows with accepted public aggregate-construction documentation."},
        {"metric": "alb2002_consumption_aggregate_crosswalk_released_variable_mapping_ready_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2002_consumption_aggregate_metadata_crosswalk_summary.csv"), "alb2002_consumption_aggregate_crosswalk_released_variable_mapping_ready_rows", "0"), "interpretation": "ALB_2002 rows supporting the local `totcons` to public `totcons3` mapping."},
        {"metric": "alb2002_consumption_aggregate_crosswalk_denominator_variant_ready_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2002_consumption_aggregate_metadata_crosswalk_summary.csv"), "alb2002_consumption_aggregate_crosswalk_denominator_variant_ready_rows", "0"), "interpretation": "ALB_2002 rows documenting the total-budget denominator variant."},
        {"metric": "alb2002_consumption_aggregate_crosswalk_sdg382_ready_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2002_consumption_aggregate_metadata_crosswalk_summary.csv"), "alb2002_consumption_aggregate_crosswalk_sdg382_ready_rows", "0"), "interpretation": "ALB_2002 aggregate crosswalk rows ready for SDG 3.8.2 promotion; should remain zero."},
        {"metric": "alb2002_period_aligned_che_policy_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2002_period_aligned_che_policy_summary.csv"), "alb2002_period_aligned_che_policy_rows", "0"), "interpretation": "ALB_2002 period-aligned CHE stress-test policy rows."},
        {"metric": "alb2002_period_aligned_che_period_alignment_ready_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2002_period_aligned_che_policy_summary.csv"), "alb2002_period_aligned_che_period_alignment_ready_rows", "0"), "interpretation": "ALB_2002 period-aligned CHE rows ready for stress testing, not outcome promotion."},
        {"metric": "alb2002_period_aligned_che_combined_che10_rate", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2002_period_aligned_che_policy_summary.csv"), "alb2002_period_aligned_che_combined_che10_rate", ""), "interpretation": "Combined monthly-equivalent unweighted CHE10 rate for ALB_2002 no-gifts-with-transport stress test."},
        {"metric": "alb2002_period_aligned_che_combined_che25_rate", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2002_period_aligned_che_policy_summary.csv"), "alb2002_period_aligned_che_combined_che25_rate", ""), "interpretation": "Combined monthly-equivalent unweighted CHE25 rate for ALB_2002 no-gifts-with-transport stress test."},
        {"metric": "alb2002_period_aligned_che_outcome_ready_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2002_period_aligned_che_policy_summary.csv"), "alb2002_period_aligned_che_outcome_ready_rows", "0"), "interpretation": "ALB_2002 period-aligned CHE rows promoted to final outcomes; should remain zero."},
        {"metric": "alb2002_period_aligned_che_current_decision", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2002_period_aligned_che_policy_summary.csv"), "alb2002_period_aligned_che_current_decision", "missing"), "interpretation": "Current ALB_2002 period-aligned CHE policy decision."},
        {"metric": "alb2002_minimum_recipe_promotion_action_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2002_minimum_recipe_promotion_summary.csv"), "alb2002_minimum_recipe_promotion_action_rows", "0"), "interpretation": "ALB_2002 minimum recipe promotion action rows."},
        {"metric": "alb2002_minimum_recipe_promotion_gate_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2002_minimum_recipe_promotion_summary.csv"), "alb2002_minimum_recipe_promotion_gate_rows", "0"), "interpretation": "ALB_2002 minimum recipe promotion gate rows."},
        {"metric": "alb2002_minimum_recipe_promotion_blocked_gates", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2002_minimum_recipe_promotion_summary.csv"), "alb2002_minimum_recipe_promotion_blocked_gates", "0"), "interpretation": "ALB_2002 minimum recipe gates still blocked."},
        {"metric": "alb2002_minimum_recipe_promotion_harmonized_ready_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2002_minimum_recipe_promotion_summary.csv"), "alb2002_minimum_recipe_promotion_harmonized_ready_rows", "0"), "interpretation": "ALB_2002 rows ready for harmonized data promotion; should remain zero."},
        {"metric": "alb2002_minimum_recipe_promotion_outcome_ready_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2002_minimum_recipe_promotion_summary.csv"), "alb2002_minimum_recipe_promotion_outcome_ready_rows", "0"), "interpretation": "ALB_2002 rows ready for outcome promotion; should remain zero."},
        {"metric": "alb2002_minimum_recipe_promotion_sdg382_ready_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2002_minimum_recipe_promotion_summary.csv"), "alb2002_minimum_recipe_promotion_sdg382_ready_rows", "0"), "interpretation": "ALB_2002 rows ready for SDG 3.8.2 promotion; should remain zero."},
        {"metric": "alb2002_minimum_recipe_promotion_climate_linkage_ready_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2002_minimum_recipe_promotion_summary.csv"), "alb2002_minimum_recipe_promotion_climate_linkage_ready_rows", "0"), "interpretation": "ALB_2002 rows ready for climate linkage after minimum recipe gates; should remain zero."},
        {"metric": "alb2002_climate_linkage_ready_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2002_district_climate_crosswalk_summary.csv"), "alb2002_climate_linkage_ready_rows", "0"), "interpretation": "ALB_2002 district crosswalk rows ready for climate linkage."},
        {"metric": "alb2002_boundary_name_match_unmatched_survey_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2002_boundary_name_match_summary.csv"), "alb2002_boundary_name_match_unmatched_survey_rows", "0"), "interpretation": "ALB_2002 survey district rows unmatched to public current boundary names."},
        {"metric": "alb2002_boundary_name_match_duplicate_boundary_name_keys", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2002_boundary_name_match_summary.csv"), "alb2002_boundary_name_match_duplicate_boundary_name_keys", "0"), "interpretation": "Duplicate public current boundary-name keys in the ALB_2002 boundary audit."},
        {"metric": "alb2002_boundary_name_match_historical_year_ready_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2002_boundary_name_match_summary.csv"), "alb2002_boundary_name_match_historical_year_ready_rows", "0"), "interpretation": "ALB_2002 boundary-name rows ready for 2002 historical boundary validation."},
        {"metric": "alb2002_boundary_name_match_climate_linkage_ready_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2002_boundary_name_match_summary.csv"), "alb2002_boundary_name_match_climate_linkage_ready_rows", "0"), "interpretation": "ALB_2002 boundary-name rows ready for climate-linkage promotion."},
        {"metric": "alb2002_boundary_resource_search_complete_name_coverage_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2002_boundary_source_resource_search_summary.csv"), "alb2002_boundary_resource_search_complete_name_coverage_rows", "0"), "interpretation": "ALB_2002 boundary resources with complete district-name coverage after documented repairs."},
        {"metric": "alb2002_boundary_resource_search_exact_unit_count_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2002_boundary_source_resource_search_summary.csv"), "alb2002_boundary_resource_search_exact_unit_count_rows", "0"), "interpretation": "ALB_2002 boundary resources whose feature and distinct-key counts match the 36 district groups."},
        {"metric": "alb2002_boundary_resource_search_2002_historical_ready_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2002_boundary_source_resource_search_summary.csv"), "alb2002_boundary_resource_search_2002_historical_ready_rows", "0"), "interpretation": "ALB_2002 boundary resources verified as 2002 historical inputs."},
        {"metric": "alb2002_boundary_resource_search_climate_linkage_ready_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2002_boundary_source_resource_search_summary.csv"), "alb2002_boundary_resource_search_climate_linkage_ready_rows", "0"), "interpretation": "ALB_2002 boundary resources ready for climate-linkage promotion."},
        {"metric": "alb2002_boundary_geometry_feature_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2002_boundary_geometry_provenance_summary.csv"), "alb2002_boundary_geometry_feature_rows", "0"), "interpretation": "Features parsed in the best ALB_2002 boundary lead."},
        {"metric": "alb2002_boundary_geometry_metadata_boundary_year", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2002_boundary_geometry_provenance_summary.csv"), "alb2002_boundary_geometry_metadata_boundary_year", "0"), "interpretation": "Boundary year reported by the candidate boundary metadata."},
        {"metric": "alb2002_boundary_geometry_boundary_year_matches_2002_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2002_boundary_geometry_provenance_summary.csv"), "alb2002_boundary_geometry_boundary_year_matches_2002_rows", "0"), "interpretation": "Candidate geometry rows whose metadata verifies a 2002 boundary vintage."},
        {"metric": "alb2002_boundary_geometry_historical_2002_boundary_ready_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2002_boundary_geometry_provenance_summary.csv"), "alb2002_boundary_geometry_historical_2002_boundary_ready_rows", "0"), "interpretation": "Geometry/provenance rows ready as verified 2002 boundary inputs."},
        {"metric": "alb2002_boundary_geometry_climate_linkage_ready_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2002_boundary_geometry_provenance_summary.csv"), "alb2002_boundary_geometry_climate_linkage_ready_rows", "0"), "interpretation": "Geometry/provenance rows ready for climate-linkage promotion."},
        {"metric": "alb2002_boundary_manual_verification_action_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2002_boundary_manual_verification_packet_summary.csv"), "alb2002_boundary_manual_verification_action_rows", "0"), "interpretation": "Manual source/action rows for resolving ALB_2002 boundary verification."},
        {"metric": "alb2002_boundary_manual_verification_gate_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2002_boundary_manual_verification_packet_summary.csv"), "alb2002_boundary_manual_verification_gate_rows", "0"), "interpretation": "Manual boundary promotion-gate checklist rows."},
        {"metric": "alb2002_boundary_manual_verification_blocked_gates", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2002_boundary_manual_verification_packet_summary.csv"), "alb2002_boundary_manual_verification_blocked_gates", "0"), "interpretation": "Manual boundary verification gates still blocked."},
        {"metric": "alb2002_boundary_manual_verification_pre2011_digital_map_absence_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2002_boundary_manual_verification_packet_summary.csv"), "alb2002_boundary_manual_verification_pre2011_digital_map_absence_rows", "0"), "interpretation": "Negative-evidence rows documenting pre-2011 national digital map absence."},
        {"metric": "alb2002_boundary_manual_verification_climate_linkage_ready_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2002_boundary_manual_verification_packet_summary.csv"), "alb2002_boundary_manual_verification_climate_linkage_ready_rows", "0"), "interpretation": "Manual verification packet rows ready for climate-linkage promotion."},
        {"metric": "alb2002_boundary_manual_source_followup_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2002_boundary_manual_source_followup_summary.csv"), "alb2002_boundary_manual_source_followup_rows", "0"), "interpretation": "Manual-source follow-up rows for ALB_2002 boundary leads."},
        {"metric": "alb2002_boundary_manual_source_followup_conclusive_blocker_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2002_boundary_manual_source_followup_summary.csv"), "alb2002_boundary_manual_source_followup_conclusive_blocker_rows", "0"), "interpretation": "ALB_2002 source leads with documented blockers after follow-up."},
        {"metric": "alb2002_boundary_manual_source_followup_district_level_ready_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2002_boundary_manual_source_followup_summary.csv"), "alb2002_boundary_manual_source_followup_district_level_ready_rows", "0"), "interpretation": "ALB_2002 source leads verified as district-level-ready after follow-up."},
        {"metric": "alb2002_boundary_manual_source_followup_climate_linkage_ready_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2002_boundary_manual_source_followup_summary.csv"), "alb2002_boundary_manual_source_followup_climate_linkage_ready_rows", "0"), "interpretation": "ALB_2002 source leads ready for climate-linkage promotion after follow-up."},
        {"metric": "alb2002_boundary_manual_source_followup_unece_pre2011_map_status", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2002_boundary_manual_source_followup_summary.csv"), "alb2002_boundary_manual_source_followup_unece_pre2011_map_status", "missing"), "interpretation": "UNECE/INSTAT pre-2011 national digital map availability blocker status."},
        {"metric": "alb2002_gadm_boundary_lead_candidate_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2002_gadm_boundary_lead_summary.csv"), "alb2002_gadm_boundary_lead_candidate_rows", "0"), "interpretation": "GADM Albania ADM2 source candidates audited for ALB_2002 boundary linkage."},
        {"metric": "alb2002_gadm36_adm2_row_count", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2002_gadm_boundary_lead_summary.csv"), "alb2002_gadm36_adm2_row_count", "0"), "interpretation": "GADM 3.6 Albania ADM2 feature rows."},
        {"metric": "alb2002_gadm36_distinct_normalized_key_count", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2002_gadm_boundary_lead_summary.csv"), "alb2002_gadm36_distinct_normalized_key_count", "0"), "interpretation": "GADM 3.6 normalized district keys after documented name repairs."},
        {"metric": "alb2002_gadm36_complete_name_coverage_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2002_gadm_boundary_lead_summary.csv"), "alb2002_gadm36_complete_name_coverage_rows", "0"), "interpretation": "Whether GADM 3.6 covers all ALB_2002 district keys by normalized name."},
        {"metric": "alb2002_gadm36_duplicate_boundary_key_count", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2002_gadm_boundary_lead_summary.csv"), "alb2002_gadm36_duplicate_boundary_key_count", "0"), "interpretation": "Duplicated GADM 3.6 normalized district keys that block automatic promotion."},
        {"metric": "alb2002_gadm_boundary_lead_climate_linkage_ready_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2002_gadm_boundary_lead_summary.csv"), "alb2002_gadm_boundary_lead_climate_linkage_ready_rows", "0"), "interpretation": "GADM boundary lead rows ready for ALB_2002 climate-linkage promotion; should remain zero."},
        {"metric": "alb2012_household_core_recipe_ready_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2012_raw_core_feasibility_summary.csv"), "alb2012_household_core_recipe_ready_rows", "0"), "interpretation": "ALB_2012 household core rows ready for data promotion."},
        {"metric": "alb2012_climate_linkage_ready_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2012_raw_core_feasibility_summary.csv"), "alb2012_climate_linkage_ready_rows", "0"), "interpretation": "ALB_2012 rows ready for climate linkage."},
        {"metric": "alb2012_provisional_outcome_ready_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2012_provisional_outcome_feasibility_summary.csv"), "alb2012_provisional_outcome_ready_rows", "0"), "interpretation": "ALB_2012 provisional outcome rows ready for final outcome promotion."},
        {"metric": "alb2012_outcome_semantics_outcome_ready_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2012_outcome_semantics_raw_value_summary.csv"), "alb2012_outcome_semantics_outcome_ready_rows", "0"), "interpretation": "ALB_2012 raw semantics rows ready for final outcome promotion."},
        {"metric": "alb2012_outcome_semantics_sdg382_ready_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2012_outcome_semantics_raw_value_summary.csv"), "alb2012_outcome_semantics_sdg382_ready_rows", "0"), "interpretation": "ALB_2012 raw semantics rows ready for SDG 3.8.2 construction."},
        {"metric": "alb2012_outcome_semantics_climate_linkage_ready_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2012_outcome_semantics_raw_value_summary.csv"), "alb2012_outcome_semantics_climate_linkage_ready_rows", "0"), "interpretation": "ALB_2012 raw semantics rows ready for climate linkage."},
        {"metric": "alb2012_timing_geography_climate_linkage_ready_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2012_timing_geography_exhaustive_summary.csv"), "alb2012_climate_linkage_ready_rows", "0"), "interpretation": "ALB_2012 timing/geography rows ready for climate linkage."},
        {"metric": "alb2012_questionnaire_timing_field_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2012_questionnaire_timing_field_summary.csv"), "alb2012_questionnaire_timing_field_rows", "0"), "interpretation": "ALB_2012 questionnaire timing/control field rows."},
        {"metric": "alb2012_questionnaire_timing_raw_verified_interview_timing_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2012_questionnaire_timing_field_summary.csv"), "alb2012_questionnaire_timing_raw_verified_interview_timing_rows", "0"), "interpretation": "ALB_2012 raw household interview timing rows verified after questionnaire review."},
        {"metric": "alb2012_questionnaire_timing_climate_linkage_ready_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2012_questionnaire_timing_field_summary.csv"), "alb2012_questionnaire_timing_climate_linkage_ready_rows", "0"), "interpretation": "ALB_2012 questionnaire timing rows ready for climate linkage."},
        {"metric": "albania_legacy_questionnaire_present_files", "value": csv_value(read_csv_dicts(RESULT_DIR / "albania_legacy_questionnaire_readability_summary.csv"), "albania_legacy_questionnaire_present_files", "0"), "interpretation": "ALB_2002/2005/2008 legacy questionnaire files present locally."},
        {"metric": "albania_legacy_questionnaire_read_ok_files", "value": csv_value(read_csv_dicts(RESULT_DIR / "albania_legacy_questionnaire_readability_summary.csv"), "albania_legacy_questionnaire_read_ok_files", "0"), "interpretation": "Legacy questionnaire files readable in the current environment."},
        {"metric": "albania_legacy_questionnaire_climate_linkage_ready_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "albania_legacy_questionnaire_readability_summary.csv"), "albania_legacy_questionnaire_climate_linkage_ready_rows", "0"), "interpretation": "Legacy questionnaire rows ready for climate linkage."},
        {"metric": "albania_legacy_questionnaire_timing_field_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "albania_legacy_questionnaire_timing_field_summary.csv"), "albania_legacy_questionnaire_timing_field_rows", "0"), "interpretation": "Legacy questionnaire timing/control field rows."},
        {"metric": "albania_legacy_questionnaire_timing_raw_verified_interview_timing_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "albania_legacy_questionnaire_timing_field_summary.csv"), "albania_legacy_questionnaire_timing_raw_verified_interview_timing_rows", "0"), "interpretation": "Verified raw household interview timing rows across legacy Albania waves."},
        {"metric": "albania_legacy_questionnaire_timing_climate_linkage_ready_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "albania_legacy_questionnaire_timing_field_summary.csv"), "albania_legacy_questionnaire_timing_climate_linkage_ready_rows", "0"), "interpretation": "Legacy questionnaire timing rows ready for climate linkage."},
        {"metric": "alb2005_recipe_ready_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2005_documented_harmonization_summary.csv"), "alb2005_recipe_ready_rows", "0"), "interpretation": "ALB_2005 documented review rows ready for recipe promotion."},
        {"metric": "alb2005_household_core_recipe_ready_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2005_household_core_candidate_summary.csv"), "alb2005_household_core_recipe_ready_rows", "0"), "interpretation": "ALB_2005 household core rows ready for data promotion."},
        {"metric": "alb2005_provisional_outcome_ready_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2005_provisional_outcome_feasibility_summary.csv"), "alb2005_provisional_outcome_ready_rows", "0"), "interpretation": "ALB_2005 provisional outcome rows ready for final outcome promotion."},
        {"metric": "alb2005_outcome_semantics_outcome_ready_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2005_outcome_semantics_raw_value_summary.csv"), "alb2005_outcome_semantics_outcome_ready_rows", "0"), "interpretation": "ALB_2005 raw semantics rows ready for final outcome promotion."},
        {"metric": "alb2005_outcome_semantics_sdg382_ready_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2005_outcome_semantics_raw_value_summary.csv"), "alb2005_outcome_semantics_sdg382_ready_rows", "0"), "interpretation": "ALB_2005 raw semantics rows ready for SDG 3.8.2 construction."},
        {"metric": "alb2005_outcome_semantics_climate_linkage_ready_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2005_outcome_semantics_raw_value_summary.csv"), "alb2005_outcome_semantics_climate_linkage_ready_rows", "0"), "interpretation": "ALB_2005 raw semantics rows ready for climate linkage."},
        {"metric": "alb2005_climate_linkage_ready_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2005_timing_geography_exhaustive_summary.csv"), "alb2005_climate_linkage_ready_rows", "0"), "interpretation": "ALB_2005 timing/geography rows ready for climate linkage."},
        {"metric": "alb2005_timing_geography_source_search_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2005_timing_geography_source_search_summary.csv"), "alb2005_timing_geography_source_search_rows", "0"), "interpretation": "ALB_2005 timing/geography source-search audit rows."},
        {"metric": "alb2005_timing_geography_source_search_local_files_scanned", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2005_timing_geography_source_search_summary.csv"), "alb2005_timing_geography_source_search_local_files_scanned", "0"), "interpretation": "Local ALB_2005 file rows scanned for timing/geography source evidence."},
        {"metric": "alb2005_timing_geography_source_search_local_variables_scanned", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2005_timing_geography_source_search_summary.csv"), "alb2005_timing_geography_source_search_local_variables_scanned", "0"), "interpretation": "Local ALB_2005 raw-variable rows scanned for timing/geography source evidence."},
        {"metric": "alb2005_timing_geography_source_search_verified_household_timing_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2005_timing_geography_source_search_summary.csv"), "alb2005_timing_geography_source_search_verified_household_timing_rows", "0"), "interpretation": "Verified ALB_2005 household interview timing rows in source-search evidence."},
        {"metric": "alb2005_timing_geography_source_search_coordinate_candidate_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2005_timing_geography_source_search_summary.csv"), "alb2005_timing_geography_source_search_coordinate_candidate_rows", "0"), "interpretation": "ALB_2005 coordinate/GPS candidate rows in source-search evidence."},
        {"metric": "alb2005_timing_geography_source_search_climate_linkage_ready_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2005_timing_geography_source_search_summary.csv"), "alb2005_timing_geography_source_search_climate_linkage_ready_rows", "0"), "interpretation": "ALB_2005 timing/geography source-search rows ready for climate linkage; should remain zero."},
        {"metric": "alb2005_harmonization_value_decision_recipe_ready_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2005_harmonization_value_decision_summary.csv"), "alb2005_harmonization_value_decision_recipe_ready_rows", "0"), "interpretation": "ALB_2005 value-decision rows ready for recipe promotion."},
        {"metric": "alb2005_harmonization_value_decision_required_blocked_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2005_harmonization_value_decision_summary.csv"), "alb2005_harmonization_value_decision_required_blocked_rows", "0"), "interpretation": "ALB_2005 required value-decision rows still blocked."},
        {"metric": "alb2005_required_value_key_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2005_required_value_key_summary.csv"), "alb2005_required_value_key_audit_rows", "0"), "interpretation": "ALB_2005 required value/key audit rows."},
        {"metric": "alb2005_required_value_key_recipe_ready_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2005_required_value_key_summary.csv"), "alb2005_required_value_key_recipe_ready_rows", "0"), "interpretation": "ALB_2005 required value/key rows ready for recipe promotion."},
        {"metric": "alb2005_required_value_key_climate_linkage_ready_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2005_required_value_key_summary.csv"), "alb2005_required_value_key_climate_linkage_ready_rows", "0"), "interpretation": "ALB_2005 required value/key rows ready for climate linkage."},
        {"metric": "alb2005_health_questionnaire_semantics_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2005_health_questionnaire_semantics_summary.csv"), "alb2005_health_questionnaire_semantics_rows", "0"), "interpretation": "ALB_2005 health questionnaire semantics audit rows."},
        {"metric": "alb2005_health_questionnaire_oop_item_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2005_health_questionnaire_semantics_summary.csv"), "alb2005_health_questionnaire_oop_item_rows", "0"), "interpretation": "ALB_2005 questionnaire-backed OOP item rows."},
        {"metric": "alb2005_health_questionnaire_recipe_ready_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2005_health_questionnaire_semantics_summary.csv"), "alb2005_health_questionnaire_recipe_ready_rows", "0"), "interpretation": "ALB_2005 questionnaire-semantics rows ready for recipe promotion."},
        {"metric": "alb2005_health_questionnaire_outcome_ready_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2005_health_questionnaire_semantics_summary.csv"), "alb2005_health_questionnaire_outcome_ready_rows", "0"), "interpretation": "ALB_2005 questionnaire-semantics rows ready for outcome construction."},
        {"metric": "alb2005_health_questionnaire_climate_linkage_ready_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2005_health_questionnaire_semantics_summary.csv"), "alb2005_health_questionnaire_climate_linkage_ready_rows", "0"), "interpretation": "ALB_2005 questionnaire-semantics rows ready for climate linkage."},
        {"metric": "alb2005_oop_aggregation_policy_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2005_oop_aggregation_policy_summary.csv"), "alb2005_oop_aggregation_policy_rows", "0"), "interpretation": "ALB_2005 OOP aggregation policy stress-test rows."},
        {"metric": "alb2005_oop_aggregation_policy_total_consumption_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2005_oop_aggregation_policy_summary.csv"), "alb2005_oop_aggregation_policy_total_consumption_rows", "0"), "interpretation": "ALB_2005 stress-test rows with positive total-consumption denominator."},
        {"metric": "alb2005_oop_aggregation_policy_outcome_ready_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2005_oop_aggregation_policy_summary.csv"), "alb2005_oop_aggregation_policy_outcome_ready_rows", "0"), "interpretation": "ALB_2005 OOP policy rows ready for final outcome promotion."},
        {"metric": "alb2005_oop_aggregation_policy_recipe_ready_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2005_oop_aggregation_policy_summary.csv"), "alb2005_oop_aggregation_policy_recipe_ready_rows", "0"), "interpretation": "ALB_2005 OOP policy rows ready for recipe promotion."},
        {"metric": "alb2005_oop_aggregation_policy_climate_linkage_ready_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2005_oop_aggregation_policy_summary.csv"), "alb2005_oop_aggregation_policy_climate_linkage_ready_rows", "0"), "interpretation": "ALB_2005 OOP policy rows ready for climate linkage."},
        {"metric": "alb2005_skip_missing_semantics_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2005_skip_missing_semantics_summary.csv"), "alb2005_skip_missing_semantics_rows", "0"), "interpretation": "ALB_2005 skip/missing semantics audit rows."},
        {"metric": "alb2005_skip_missing_payment_nonmissing_when_not_triggered_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2005_skip_missing_semantics_summary.csv"), "alb2005_skip_missing_payment_nonmissing_when_not_triggered_rows", "0"), "interpretation": "Payment downstream nonmissing rows when trigger is negative."},
        {"metric": "alb2005_skip_missing_payment_zero_or_missing_when_triggered_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2005_skip_missing_semantics_summary.csv"), "alb2005_skip_missing_payment_zero_or_missing_when_triggered_rows", "0"), "interpretation": "Triggered payment rows with no positive payment."},
        {"metric": "alb2005_skip_missing_recipe_ready_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2005_skip_missing_semantics_summary.csv"), "alb2005_skip_missing_recipe_ready_rows", "0"), "interpretation": "ALB_2005 skip/missing rows ready for recipe promotion."},
        {"metric": "alb2005_skip_missing_outcome_ready_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2005_skip_missing_semantics_summary.csv"), "alb2005_skip_missing_outcome_ready_rows", "0"), "interpretation": "ALB_2005 skip/missing rows ready for outcome promotion."},
        {"metric": "alb2005_skip_missing_climate_linkage_ready_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2005_skip_missing_semantics_summary.csv"), "alb2005_skip_missing_climate_linkage_ready_rows", "0"), "interpretation": "ALB_2005 skip/missing rows ready for climate linkage."},
        {"metric": "alb2005_consumption_aggregate_crosswalk_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2005_consumption_aggregate_metadata_crosswalk_summary.csv"), "alb2005_consumption_aggregate_crosswalk_rows", "0"), "interpretation": "ALB_2005 aggregate metadata/local raw crosswalk audit rows."},
        {"metric": "alb2005_consumption_aggregate_crosswalk_metadata_present_local_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2005_consumption_aggregate_metadata_crosswalk_summary.csv"), "alb2005_consumption_aggregate_crosswalk_metadata_variables_present_in_local_raw_rows", "0"), "interpretation": "Public metadata aggregate/component variables present locally."},
        {"metric": "alb2005_consumption_aggregate_crosswalk_metadata_absent_local_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2005_consumption_aggregate_metadata_crosswalk_summary.csv"), "alb2005_consumption_aggregate_crosswalk_metadata_variables_absent_from_local_raw_rows", "0"), "interpretation": "Public metadata aggregate/component variables absent locally."},
        {"metric": "alb2005_consumption_aggregate_crosswalk_totcons_positive_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2005_consumption_aggregate_metadata_crosswalk_summary.csv"), "alb2005_consumption_aggregate_crosswalk_totcons_positive_rows", "0"), "interpretation": "Positive local totcons rows in the crosswalk audit."},
        {"metric": "alb2005_consumption_aggregate_crosswalk_totcons05_local_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2005_consumption_aggregate_metadata_crosswalk_summary.csv"), "alb2005_consumption_aggregate_crosswalk_totcons05_local_rows", "0"), "interpretation": "Local totcons05 rows in poverty.sav; should remain zero in current extract."},
        {"metric": "alb2005_consumption_aggregate_crosswalk_component_formula_reconstructable_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2005_consumption_aggregate_metadata_crosswalk_summary.csv"), "alb2005_consumption_aggregate_crosswalk_component_formula_reconstructable_rows", "0"), "interpretation": "Whether checked public aggregate formula components are locally reconstructable; should remain zero."},
        {"metric": "alb2005_consumption_aggregate_crosswalk_sdg382_ready_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2005_consumption_aggregate_metadata_crosswalk_summary.csv"), "alb2005_consumption_aggregate_crosswalk_sdg382_ready_rows", "0"), "interpretation": "ALB_2005 aggregate crosswalk rows ready for SDG 3.8.2 construction; should remain zero."},
        {"metric": "alb2005_consumption_aggregate_crosswalk_recipe_ready_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2005_consumption_aggregate_metadata_crosswalk_summary.csv"), "alb2005_consumption_aggregate_crosswalk_recipe_ready_rows", "0"), "interpretation": "ALB_2005 aggregate crosswalk rows ready for recipe promotion; should remain zero."},
        {"metric": "alb2005_consumption_aggregate_crosswalk_outcome_ready_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2005_consumption_aggregate_metadata_crosswalk_summary.csv"), "alb2005_consumption_aggregate_crosswalk_outcome_ready_rows", "0"), "interpretation": "ALB_2005 aggregate crosswalk rows ready for outcome promotion; should remain zero."},
        {"metric": "alb2005_consumption_aggregate_crosswalk_climate_linkage_ready_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2005_consumption_aggregate_metadata_crosswalk_summary.csv"), "alb2005_consumption_aggregate_crosswalk_climate_linkage_ready_rows", "0"), "interpretation": "ALB_2005 aggregate crosswalk rows ready for climate linkage; should remain zero."},
        {"metric": "alb2005_consumption_component_source_search_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2005_consumption_component_source_search_summary.csv"), "alb2005_consumption_component_source_search_rows", "0"), "interpretation": "ALB_2005 consumption component source-search audit rows."},
        {"metric": "alb2005_consumption_component_source_search_exact_target_variables_found", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2005_consumption_component_source_search_summary.csv"), "alb2005_consumption_component_source_search_exact_target_variables_found", "0"), "interpretation": "Public metadata target variables found exactly in local raw schema."},
        {"metric": "alb2005_consumption_component_source_search_exact_target_variables_missing", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2005_consumption_component_source_search_summary.csv"), "alb2005_consumption_component_source_search_exact_target_variables_missing", "0"), "interpretation": "Public metadata target variables missing from local raw schema."},
        {"metric": "alb2005_consumption_component_source_search_construction_code_files_found", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2005_consumption_component_source_search_summary.csv"), "alb2005_consumption_component_source_search_construction_code_files_found", "0"), "interpretation": "Local source-code-like files found under the ALB_2005 extract."},
        {"metric": "alb2005_consumption_component_source_search_construction_code_targets_found", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2005_consumption_component_source_search_summary.csv"), "alb2005_consumption_component_source_search_construction_code_targets_found", "0"), "interpretation": "Target variables with local construction-code text hits."},
        {"metric": "alb2005_consumption_component_source_search_sdg382_ready_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2005_consumption_component_source_search_summary.csv"), "alb2005_consumption_component_source_search_sdg382_ready_rows", "0"), "interpretation": "ALB_2005 source-search rows ready for SDG 3.8.2 construction; should remain zero."},
        {"metric": "alb2005_consumption_component_source_search_recipe_ready_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2005_consumption_component_source_search_summary.csv"), "alb2005_consumption_component_source_search_recipe_ready_rows", "0"), "interpretation": "ALB_2005 source-search rows ready for recipe promotion; should remain zero."},
        {"metric": "alb2005_consumption_component_source_search_outcome_ready_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2005_consumption_component_source_search_summary.csv"), "alb2005_consumption_component_source_search_outcome_ready_rows", "0"), "interpretation": "ALB_2005 source-search rows ready for outcome promotion; should remain zero."},
        {"metric": "alb2005_consumption_component_source_search_climate_linkage_ready_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2005_consumption_component_source_search_summary.csv"), "alb2005_consumption_component_source_search_climate_linkage_ready_rows", "0"), "interpretation": "ALB_2005 source-search rows ready for climate linkage; should remain zero."},
        {"metric": "alb2005_minimum_recipe_promotion_action_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2005_minimum_recipe_promotion_summary.csv"), "alb2005_minimum_recipe_promotion_action_rows", "0"), "interpretation": "ALB_2005 minimum recipe promotion action rows."},
        {"metric": "alb2005_minimum_recipe_promotion_gate_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2005_minimum_recipe_promotion_summary.csv"), "alb2005_minimum_recipe_promotion_gate_rows", "0"), "interpretation": "ALB_2005 minimum recipe promotion gate rows."},
        {"metric": "alb2005_minimum_recipe_promotion_blocked_gates", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2005_minimum_recipe_promotion_summary.csv"), "alb2005_minimum_recipe_promotion_blocked_gates", "0"), "interpretation": "ALB_2005 minimum recipe gates still blocked."},
        {"metric": "alb2005_minimum_recipe_promotion_harmonized_ready_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2005_minimum_recipe_promotion_summary.csv"), "alb2005_minimum_recipe_promotion_harmonized_ready_rows", "0"), "interpretation": "ALB_2005 rows ready for harmonized data promotion; should remain zero."},
        {"metric": "alb2005_minimum_recipe_promotion_climate_linkage_ready_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2005_minimum_recipe_promotion_summary.csv"), "alb2005_minimum_recipe_promotion_climate_linkage_ready_rows", "0"), "interpretation": "ALB_2005 rows ready for climate linkage after minimum recipe gates; should remain zero."},
        {"metric": "alb2005_public_fieldwork_geo_metadata_evidence_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2005_public_fieldwork_geo_metadata_summary.csv"), "alb2005_public_fieldwork_geo_metadata_evidence_rows", "0"), "interpretation": "ALB_2005 public fieldwork/geography metadata evidence rows."},
        {"metric": "alb2005_public_fieldwork_geo_metadata_verified_source_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2005_public_fieldwork_geo_metadata_summary.csv"), "alb2005_public_fieldwork_geo_metadata_verified_source_rows", "0"), "interpretation": "ALB_2005 public fieldwork/geography metadata rows with source snippets verified."},
        {"metric": "alb2005_public_fieldwork_geo_metadata_source_missing_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2005_public_fieldwork_geo_metadata_summary.csv"), "alb2005_public_fieldwork_geo_metadata_source_missing_rows", "0"), "interpretation": "ALB_2005 public fieldwork/geography metadata rows with missing source evidence; should remain zero."},
        {"metric": "alb2005_public_fieldwork_geo_metadata_household_timing_verified_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2005_public_fieldwork_geo_metadata_summary.csv"), "alb2005_public_fieldwork_geo_metadata_household_timing_verified_rows", "0"), "interpretation": "ALB_2005 household timing rows verified after public metadata audit; should remain zero."},
        {"metric": "alb2005_public_fieldwork_geo_metadata_raw_coordinate_value_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2005_public_fieldwork_geo_metadata_summary.csv"), "alb2005_public_fieldwork_geo_metadata_raw_coordinate_value_rows", "0"), "interpretation": "ALB_2005 raw coordinate rows verified after public metadata audit; should remain zero."},
        {"metric": "alb2005_public_fieldwork_geo_metadata_climate_linkage_ready_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2005_public_fieldwork_geo_metadata_summary.csv"), "alb2005_public_fieldwork_geo_metadata_climate_linkage_ready_rows", "0"), "interpretation": "ALB_2005 climate-linkage rows ready after public metadata audit; should remain zero."},
        {"metric": "alb2005_diary_timing_candidate_audit_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2005_diary_timing_candidate_summary.csv"), "alb2005_diary_timing_candidate_audit_rows", "0"), "interpretation": "ALB_2005 bookmetadata diary timing candidate rows."},
        {"metric": "alb2005_diary_timing_candidate_metadata_found_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2005_diary_timing_candidate_summary.csv"), "alb2005_diary_timing_candidate_metadata_found_rows", "0"), "interpretation": "ALB_2005 diary timing candidates found in metadata catalog and DDI."},
        {"metric": "alb2005_diary_timing_candidate_raw_bookmetadata_files_present", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2005_diary_timing_candidate_summary.csv"), "alb2005_diary_timing_candidate_raw_bookmetadata_files_present", "0"), "interpretation": "Raw bookmetadata files present under temp/raw_downloads; should remain zero in current metadata-only state."},
        {"metric": "alb2005_diary_timing_candidate_date_candidate_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2005_diary_timing_candidate_summary.csv"), "alb2005_diary_timing_candidate_date_candidate_rows", "0"), "interpretation": "Diary beginning/finishing date candidate variables with nonzero DDI valid counts."},
        {"metric": "alb2005_diary_timing_candidate_household_timing_promoted_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2005_diary_timing_candidate_summary.csv"), "alb2005_diary_timing_candidate_household_timing_promoted_rows", "0"), "interpretation": "ALB_2005 household timing rows promoted after diary candidate audit; should remain zero."},
        {"metric": "alb2005_diary_timing_candidate_climate_linkage_ready_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2005_diary_timing_candidate_summary.csv"), "alb2005_diary_timing_candidate_climate_linkage_ready_rows", "0"), "interpretation": "ALB_2005 climate-linkage rows ready after diary candidate audit; should remain zero."},
        {"metric": "alb2005_extracted_module_coverage_ddi_module_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2005_extracted_module_coverage_summary.csv"), "alb2005_extracted_module_coverage_ddi_module_rows", "0"), "interpretation": "ALB_2005 DDI/schema modules checked against extracted files."},
        {"metric": "alb2005_archive_member_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2005_extracted_module_coverage_summary.csv"), "alb2005_archive_member_rows", "0"), "interpretation": "Members listed directly from the local ALB_2005 archive."},
        {"metric": "alb2005_archive_sav_member_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2005_extracted_module_coverage_summary.csv"), "alb2005_archive_sav_member_rows", "0"), "interpretation": "SPSS .sav members listed directly from the local ALB_2005 archive."},
        {"metric": "alb2005_archive_ddi_module_absent_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2005_extracted_module_coverage_summary.csv"), "alb2005_archive_ddi_module_absent_rows", "0"), "interpretation": "ALB_2005 DDI/schema modules absent from the local archive manifest."},
        {"metric": "alb2005_archive_critical_module_absent_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2005_extracted_module_coverage_summary.csv"), "alb2005_archive_critical_module_absent_rows", "0"), "interpretation": "Critical ALB_2005 timing, food-diary, and design DDI modules absent from the local archive manifest."},
        {"metric": "alb2005_archive_listing_status", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2005_extracted_module_coverage_summary.csv"), "alb2005_archive_listing_status", "missing"), "interpretation": "Whether the local ALB_2005 archive member list was readable."},
        {"metric": "alb2005_extracted_module_coverage_present_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2005_extracted_module_coverage_summary.csv"), "alb2005_extracted_module_coverage_present_rows", "0"), "interpretation": "ALB_2005 DDI modules present in extracted files."},
        {"metric": "alb2005_extracted_module_coverage_missing_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2005_extracted_module_coverage_summary.csv"), "alb2005_extracted_module_coverage_missing_rows", "0"), "interpretation": "ALB_2005 DDI modules missing from extracted files."},
        {"metric": "alb2005_extracted_module_coverage_bookmetadata_missing_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2005_extracted_module_coverage_summary.csv"), "alb2005_extracted_module_coverage_bookmetadata_missing_rows", "0"), "interpretation": "ALB_2005 bookmetadata_cl missing rows."},
        {"metric": "alb2005_extracted_module_coverage_critical_missing_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2005_extracted_module_coverage_summary.csv"), "alb2005_extracted_module_coverage_critical_missing_rows", "0"), "interpretation": "ALB_2005 critical missing timing/food-diary/design modules."},
        {"metric": "alb2005_extracted_module_coverage_coordinate_metadata_variable_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2005_extracted_module_coverage_summary.csv"), "alb2005_extracted_module_coverage_coordinate_metadata_variable_rows", "0"), "interpretation": "ALB_2005 coordinate/GPS metadata variable rows."},
        {"metric": "alb2005_extracted_module_coverage_coordinate_extracted_file_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2005_extracted_module_coverage_summary.csv"), "alb2005_extracted_module_coverage_coordinate_extracted_file_rows", "0"), "interpretation": "ALB_2005 coordinate/GPS extracted file rows."},
        {"metric": "alb2005_extracted_module_coverage_climate_linkage_ready_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2005_extracted_module_coverage_summary.csv"), "alb2005_extracted_module_coverage_climate_linkage_ready_rows", "0"), "interpretation": "ALB_2005 climate-linkage rows ready after extracted-module audit; should remain zero."},
        {"metric": "albania_first_analysis_promotion_wave_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "albania_first_analysis_promotion_summary.csv"), "albania_first_analysis_promotion_wave_rows", "0"), "interpretation": "Local Albania raw waves compared for first analysis promotion."},
        {"metric": "albania_first_analysis_promotion_gate_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "albania_first_analysis_promotion_summary.csv"), "albania_first_analysis_promotion_gate_rows", "0"), "interpretation": "First-analysis promotion gate rows."},
        {"metric": "albania_first_analysis_promotion_blocked_gate_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "albania_first_analysis_promotion_summary.csv"), "albania_first_analysis_promotion_blocked_gate_rows", "0"), "interpretation": "First-analysis promotion gates still blocked."},
        {"metric": "albania_first_analysis_promotion_ready_wave_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "albania_first_analysis_promotion_summary.csv"), "albania_first_analysis_promotion_ready_wave_rows", "0"), "interpretation": "Albania waves ready for first analytical-sample promotion; should remain zero."},
        {"metric": "albania_first_analysis_promotion_top_ranked_idno", "value": csv_value(read_csv_dicts(RESULT_DIR / "albania_first_analysis_promotion_summary.csv"), "albania_first_analysis_promotion_top_ranked_idno", ""), "interpretation": "Top-ranked local Albania wave for next manual evidence work."},
        {"metric": "albania_first_analysis_promotion_current_decision", "value": csv_value(read_csv_dicts(RESULT_DIR / "albania_first_analysis_promotion_summary.csv"), "albania_first_analysis_promotion_current_decision", "missing"), "interpretation": "Current first-analysis promotion decision."},
        {"metric": "albania_existing_raw_wave_harmonization_ready_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "albania_existing_raw_wave_audit_summary.csv"), "albania_existing_raw_wave_harmonization_ready_rows", "0"), "interpretation": "Existing Albania raw waves ready for harmonized data promotion."},
        {"metric": "albania_existing_raw_wave_climate_linkage_ready_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "albania_existing_raw_wave_audit_summary.csv"), "albania_existing_raw_wave_climate_linkage_ready_rows", "0"), "interpretation": "Existing Albania raw waves ready for climate-linkage input promotion."},
        {"metric": "alb2008_household_core_recipe_ready_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2008_household_core_candidate_summary.csv"), "alb2008_household_core_recipe_ready_rows", "0"), "interpretation": "ALB_2008 household core rows ready for data promotion."},
        {"metric": "alb2008_provisional_outcome_ready_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2008_provisional_outcome_feasibility_summary.csv"), "alb2008_provisional_outcome_ready_rows", "0"), "interpretation": "ALB_2008 provisional outcome rows ready for final outcome promotion."},
        {"metric": "alb2008_outcome_semantics_outcome_ready_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2008_outcome_semantics_raw_value_summary.csv"), "alb2008_outcome_semantics_outcome_ready_rows", "0"), "interpretation": "ALB_2008 raw semantics rows ready for final outcome promotion."},
        {"metric": "alb2008_outcome_semantics_sdg382_ready_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2008_outcome_semantics_raw_value_summary.csv"), "alb2008_outcome_semantics_sdg382_ready_rows", "0"), "interpretation": "ALB_2008 raw semantics rows ready for SDG 3.8.2 construction."},
        {"metric": "alb2008_outcome_semantics_climate_linkage_ready_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2008_outcome_semantics_raw_value_summary.csv"), "alb2008_outcome_semantics_climate_linkage_ready_rows", "0"), "interpretation": "ALB_2008 raw semantics rows ready for climate linkage."},
        {"metric": "alb2008_climate_linkage_ready_rows", "value": csv_value(read_csv_dicts(RESULT_DIR / "alb2008_timing_geography_exhaustive_summary.csv"), "alb2008_climate_linkage_ready_rows", "0"), "interpretation": "ALB_2008 timing/geography rows ready for climate linkage."},
    ]
    for section, count in sorted(section_counts.items()):
        rows.append({"metric": f"bundle_section_{section}", "value": str(count), "interpretation": "Direct-read bundle section count."})
    for status, count in sorted(status_counts.items()):
        rows.append({"metric": f"bundle_status_{status}", "value": str(count), "interpretation": "Direct-read bundle status count."})
    return rows


def markdown_rows(rows: list[dict[str, str]], columns: list[str], limit: int = 20) -> str:
    lines = ["| " + " | ".join(columns) + " |", "|" + "|".join("---" for _ in columns) + "|"]
    for row in rows[:limit]:
        values = []
        for column in columns:
            value = (row.get(column, "") or "").replace("|", "/")
            if len(value) > 120:
                value = value[:117] + "..."
            values.append(value)
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines)


def markdown_count_table(counter: Counter[str], label: str) -> str:
    lines = [f"| {label} | Count |", "|---|---:|"]
    for key, count in counter.most_common():
        lines.append(f"| {key or 'blank'} | {count} |")
    return "\n".join(lines)


def write_report(bundle: list[dict[str, str]], manifest: list[dict[str, str]], summary: list[dict[str, str]]) -> None:
    section_counts = Counter(row["section"] for row in bundle)
    status_counts = Counter(row["status"] for row in bundle)
    manifest_counts = Counter(row["current_status"] for row in manifest)
    completion_gaps = [row for row in bundle if row["section"] == "completion_gap"]
    no_go_rules = [row for row in bundle if row["section"] == "go_no_go_rule"]
    priorities = [row for row in bundle if row["section"] == "priority_bundle"]
    missing_artifacts = [row for row in manifest if row["current_status"] != "present_nonempty"]
    raw_file_rows = int_value(csv_value(summary, "raw_file_inventory_rows", "0"))
    raw_status_line = (
        "Raw schemas and first-batch value/key summaries exist, but no harmonized analytical dataset has been promoted."
        if raw_file_rows > 0
        else "The workspace remains metadata/protocol-only because no raw tabular microdata files or raw variable catalogs have been inspected."
    )
    summary_table = "\n".join(f"| {row['metric']} | {row['value']} | {row['interpretation']} |" for row in summary)
    REPORT_PATH.write_text(
        f"""# Direct-Read Audit Bundle

Status: reviewer/GPT-facing index only. {raw_status_line}

## Bottom Line

- Allowed evidence: official-source verification, public metadata/schema inventory, manual-download planning, public raw archive/schema evidence where present, first-batch raw value/key summaries, metadata-derived candidate maps, and fail-closed analysis protocols.
- Not allowed evidence yet: constructed UHC outcomes, climate-linked household data, descriptive prevalence, predictive ML, reduced-form causal estimates, mechanism analysis, causal ML, policy learning, or robustness results.
- Binding blocker: complete manual unit, recall-period, missing-code, skip-pattern, merge-key, and documentation review before promoting any country-wave into a harmonization recipe.

## Summary Metrics

| Metric | Value | Interpretation |
|---|---:|---|
{summary_table}

## Bundle Sections

{markdown_count_table(section_counts, 'Section') if bundle else 'No bundle rows exist.'}

## Bundle Status

{markdown_count_table(status_counts, 'Status') if bundle else 'No bundle rows exist.'}

## Completion Gaps

{markdown_rows(completion_gaps, ['item', 'status', 'value', 'interpretation'], 20) if completion_gaps else 'No incomplete completion criteria were found.'}

## Go/No-Go Rules

{markdown_rows(no_go_rules, ['item', 'status', 'value', 'interpretation'], 12) if no_go_rules else 'No go/no-go rows were found.'}

## Priority Raw-Data Bundles

{markdown_rows(priorities, ['item', 'status', 'value', 'interpretation'], 10) if priorities else 'No priority bundle rows were found.'}

## Artifact Manifest

{markdown_count_table(manifest_counts, 'Artifact status') if manifest else 'No artifact manifest rows exist.'}

Missing or empty curated artifacts:

{markdown_rows(missing_artifacts, ['artifact_group', 'relative_path', 'current_status', 'role'], 20) if missing_artifacts else 'None among curated artifacts.'}

## Reproduction Notes

The deterministic downstream audit layer can be refreshed with:

```bash
python script/54_audit_alb2002_household_core_merge.py
python script/55_audit_alb2002_provisional_outcome_feasibility.py
python script/60_audit_alb2002_outcome_semantics_raw_values.py
python script/89_audit_alb2002_health_questionnaire_semantics.py
python script/91_audit_alb2002_oop_aggregation_policy.py
python script/92_audit_alb2002_skip_missing_semantics.py
python script/97_audit_alb2002_oop_skip_value_decision.py
python script/93_audit_alb2002_access_need_denominator_policy.py
python script/105_build_alb2002_access_candidate_outcomes.py
python script/94_audit_alb2002_consumption_sdg_denominator_policy.py
python script/96_audit_alb2002_consumption_construction_sources.py
python script/95_audit_alb2002_consumption_aggregate_metadata_crosswalk.py
python script/99_audit_alb2002_period_aligned_che_policy.py
python script/100_audit_alb2002_weight_design_evidence.py
python script/56_audit_alb2002_district_climate_crosswalk.py
python script/64_audit_alb2002_boundary_name_match.py
python script/79_audit_alb2002_boundary_source_resource_search.py
python script/80_audit_alb2002_boundary_geometry_provenance.py
python script/69_audit_alb2002_boundary_source_alternatives.py
python script/70_audit_alb2002_local_geography_artifacts.py
python script/82_audit_alb2002_boundary_manual_source_followup.py
python script/88_audit_alb2002_gadm_boundary_lead.py
python script/81_build_alb2002_boundary_manual_verification_packet.py
python script/90_build_alb2002_minimum_recipe_promotion_packet.py
python script/101_build_alb2002_che_candidate_outcomes.py
python script/106_build_alb2002_uhc_composite_candidate_outcomes.py
python script/102_build_alb2002_analysis_candidate_dataset.py
python script/117_promote_alb2002_harmonized_household_core.py
python script/05_construct_outcomes.py
python script/119_promote_alb2002_limited_financial_outcomes.py
python script/103_build_alb2002_climate_centroid_exposure_candidates.py
python script/107_build_alb2002_climate_shock_candidate_audit.py
python script/118_promote_alb2002_limited_climate_exposures.py
python script/07_merge_microdata_climate.py
python script/120_promote_alb2002_limited_climate_linked.py
python script/108_build_alb2002_climate_outcome_linked_candidate_audit.py
python script/109_build_alb2002_linked_candidate_descriptive_diagnostics.py
python script/90_build_alb2002_minimum_recipe_promotion_packet.py
python script/98_audit_analysis_dataset_promotion_barriers.py
python script/110_build_current_design_scorecard.py
python script/111_audit_alb2002_promotion_gate_delta.py
python script/112_build_alb2002_boundary_blocker_resolution_matrix.py
python script/113_build_alb2002_outcome_blocker_resolution_matrix.py
python script/57_audit_alb2012_raw_core_feasibility.py
python script/58_audit_alb2012_provisional_outcome_feasibility.py
python script/63_audit_alb2012_outcome_semantics_raw_values.py
python script/59_audit_alb2012_timing_geography_exhaustive.py
python script/65_audit_alb2012_questionnaire_timing_fields.py
python script/114_build_alb2012_timing_geography_blocker_resolution_matrix.py
python script/66_audit_albania_legacy_questionnaire_readability.py
python script/67_audit_albania_legacy_questionnaire_timing_fields.py
python script/48_audit_alb2005_provisional_outcome_feasibility.py
python script/61_audit_alb2005_outcome_semantics_raw_values.py
python script/49_audit_alb2005_timing_geography_exhaustive.py
python script/71_audit_alb2005_required_value_key_evidence.py
python script/72_audit_alb2005_health_questionnaire_semantics.py
python script/73_audit_alb2005_oop_aggregation_policy.py
python script/74_audit_alb2005_skip_missing_semantics.py
python script/75_audit_alb2005_consumption_oop_unit_period.py
python script/76_audit_alb2005_consumption_aggregate_metadata_crosswalk.py
python script/77_audit_alb2005_consumption_component_source_search.py
python script/78_audit_alb2005_timing_geography_source_search.py
python script/83_build_alb2005_minimum_recipe_promotion_packet.py
python script/84_audit_alb2005_public_fieldwork_geo_metadata.py
python script/85_audit_alb2005_diary_timing_candidates.py
python script/86_audit_alb2005_extracted_module_coverage.py
python script/87_build_albania_first_analysis_promotion_gate.py
python script/115_build_alb2005_fallback_blocker_resolution_matrix.py
python script/51_audit_alb2008_household_core_merge.py
python script/52_audit_alb2008_provisional_outcome_feasibility.py
python script/62_audit_alb2008_outcome_semantics_raw_values.py
python script/53_audit_alb2008_timing_geography_exhaustive.py
python script/116_build_alb2008_fallback_blocker_resolution_matrix.py
python script/50_audit_existing_albania_raw_waves.py
python script/33_build_harmonization_recipe_gate.py
python script/68_build_alb2005_harmonization_value_decision_audit.py
python script/35_build_empirical_readiness_dashboard.py
python script/36_build_direct_read_audit_bundle.py
python script/28_audit_python_environment.py
python script/26_build_objective_traceability_audit.py
python script/13_write_reports.py
python script/14_validate_workspace.py
```

The full `script/run_all.ps1`, `script/run_all.sh`, and `Makefile` runners include acquisition/probe stages and may take longer. Empirical estimation remains blocked until raw files are manually obtained and inspected.

## Machine-Readable Outputs

- `result/direct_read_audit_bundle.csv`
- `result/direct_read_artifact_manifest.csv`
- `result/direct_read_audit_bundle_summary.csv`
""",
        encoding="utf-8",
    )


def main() -> None:
    ensure_dirs()
    manifest = build_manifest()
    bundle = build_bundle(manifest)
    summary = build_summary(bundle, manifest)
    write_csv(BUNDLE_PATH, bundle, BUNDLE_COLUMNS)
    write_csv(SUMMARY_PATH, summary, SUMMARY_COLUMNS)
    write_report(bundle, manifest, summary)

    manifest = build_manifest()
    bundle = build_bundle(manifest)
    summary = build_summary(bundle, manifest)
    write_csv(BUNDLE_PATH, bundle, BUNDLE_COLUMNS)
    write_csv(SUMMARY_PATH, summary, SUMMARY_COLUMNS)
    write_report(bundle, manifest, summary)
    write_csv(MANIFEST_PATH, manifest, MANIFEST_COLUMNS)
    append_log(
        TEMP_DIR / "audit_log.md",
        f"Direct-read audit bundle rows={len(bundle)} manifest_rows={len(manifest)}.",
    )
    print(f"Direct-read audit bundle rows={len(bundle)} manifest_rows={len(manifest)}.")


if __name__ == "__main__":
    main()
