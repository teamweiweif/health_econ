# Climate UHC ML

This workspace studies whether climate shocks increase household-level universal health coverage (UHC) failure through financial hardship, forgone care, or both. The active objective is now dataset promotion, not modeling.

Do not run new predictive, reduced-form, causal ML, or policy-learning models until `result/promoted_country_wave_registry.csv` shows at least 6 value-verified financial-protection countries, 10 double-failure-ready country-waves, and at least one accepted CHIRPS or ERA5 climate-linkage route.

Run the current dataset-promotion pipeline from the project root:

```powershell
powershell -ExecutionPolicy Bypass -File script/run_all.ps1
```

On systems with GNU Make:

```bash
make all
```

Equivalent script sequence if neither runner is convenient:

```bash
python script/30_build_minimum_viable_acquisition_plan.py
python script/17_audit_raw_downloads.py
python script/22_build_raw_ingestion_plan.py
python script/29_build_raw_variable_verification_protocol.py
python script/33_build_harmonization_recipe_gate.py
python script/121_build_country_wave_promotion_registry.py
python script/122_build_priority_promotion_acquisition_plan.py
python script/123_probe_priority_official_raw_access.py
python script/124_build_priority_raw_intake_gate.py
python script/128_build_priority_archive_member_preflight.py
python script/125_build_priority_climate_linkage_preflight.py
python script/126_build_priority_raw_verification_workbook.py
python script/129_build_priority_manual_verification_decision_gate.py
python script/130_build_priority_raw_package_receipt_ledger.py
python script/131_build_priority_official_download_dossier.py
python script/133_build_priority_public_documentation_receipt.py
python script/135_build_priority_official_metadata_evidence_extract.py
python script/136_build_priority_credentialed_raw_acquisition_ledger.py
python script/137_probe_priority_official_endpoint_matrix.py
python script/138_probe_priority_core_file_endpoint_matrix.py
python script/139_build_priority_threshold_acquisition_campaign.py
python script/140_build_priority_first_pass_variable_review_queue.py
python script/141_build_priority_download_execution_packet.py
python script/142_build_priority_lsms_isa_alignment_audit.py
python script/143_build_priority_lsms_isa_refocused_acquisition_queue.py
python script/146_build_priority_lsms_isa_public_documentation_receipt.py
python script/147_build_priority_lsms_isa_variable_evidence_matrix.py
python script/144_build_priority_lsms_isa_raw_package_intake_packet.py
python script/145_build_priority_lsms_isa_archive_member_preflight.py
python script/149_build_priority_lsms_isa_raw_value_verification_workbook.py
python script/150_build_priority_lsms_isa_raw_package_receipt_checklist.py
python script/152_build_priority_lsms_isa_credentialed_raw_acquisition_workbench.py
python script/153_validate_priority_lsms_isa_official_file_receipt.py
python script/154_build_priority_lsms_isa_threshold_download_sequence.py
python script/155_build_priority_lsms_isa_minimum_batch_raw_intake_guide.py
python script/156_probe_priority_lsms_isa_minimum_batch_endpoint_refresh.py
python script/157_build_priority_lsms_isa_received_raw_schema_audit.py
python script/158_build_priority_lsms_isa_received_raw_value_profile.py
python script/159_build_priority_lsms_isa_received_raw_semantics_review.py
python script/160_build_mwi2004_raw_requirement_verification.py
python script/162_build_mwi2004_health_access_label_skip_decisions.py
python script/163_build_mwi2004_health_exception_audit.py
python script/164_build_mwi2004_health_access_construction_policy.py
python script/165_build_mwi2004_financial_protection_construction_policy.py
python script/166_build_mwi2004_timing_geography_linkage_policy.py
python script/167_build_mwi2004_access_person_key_resolution_policy.py
python script/168_build_mwi2004_missing_units_recall_skip_policy.py
python script/161_build_mwi2004_requirement_acceptance_decisions.py
python script/169_build_mwi2004_chirps_admin2_route_policy.py
python script/170_extract_mwi2004_chirps_admin2_exposures.py
python script/171_build_mwi2004_promoted_household_climate_dataset.py
python script/132_build_priority_analysis_dataset_synthesis_blueprint.py
python script/134_build_priority_country_wave_promotion_packets.py
python script/148_build_priority_lsms_isa_country_wave_promotion_packets.py
python script/151_refresh_refocused_promoted_country_wave_registry.py
python script/127_enforce_promoted_data_gate.py
python script/172_build_priority_lsms_isa_next_raw_package_action_packet.py
python script/174_build_priority_lsms_isa_incoming_raw_package_router.py
python script/175_build_priority_lsms_isa_threshold_gap_control_panel.py
python script/176_build_priority_lsms_isa_manual_download_packets.py
python script/177_build_priority_lsms_isa_manual_download_progress_tracker.py
python script/173_build_priority_lsms_isa_promotion_gate_dashboard.py
python script/35_build_empirical_readiness_dashboard.py
python script/36_build_direct_read_audit_bundle.py
python script/26_build_objective_traceability_audit.py
python script/14_validate_workspace.py
```

Raw files are not stored in `data/`. Direct downloads and source snapshots belong in `temp/`; analysis-ready datasets belong in `data/`.

Current status:

- Official UHC and climate-health anchors are verified in `report/source_audit.md`.
- World Bank Microdata Library screening is saved in `temp/country_wave_screening.csv`.
- Public metadata/documentation for priority studies is saved under `temp/raw_schema_inventory/`.
- Raw microdata downloads are not complete because priority World Bank studies require login or Data Access Agreement steps; see `temp/manual_download_manifest.csv` and the ranked queue in `temp/manual_download_priority.csv`.
- The manual raw-data handoff is summarized in `report/manual_data_access_guide.md`; the module-level checklist is `temp/manual_download_file_checklist.csv`.
- Long metadata acquisition runs checkpoint to `temp/acquisition_progress.csv` after each priority study. If acquisition is interrupted, rerun `python script/03_inspect_raw_schemas.py` and `python script/13_write_reports.py` to rebuild maps and reports from saved schema files.
- Direct-public external repository candidates are probed in `temp/external_repository_probe.csv`; the probe does not bypass login, registration, or terms gates.
- The objective-level validator writes `result/workspace_validation_audit.csv` and `report/workspace_validation.md`.
- The manual request packet writes `report/raw_data_request_packet.md`, `temp/manual_access_action_queue.csv`, and an updated `temp/raw_downloads/README.md`.
- Put manual raw files in `temp/raw_downloads/`, then rerun `make all` to refresh raw schema inspection, value-verification gates, harmonization gates, promotion registry, promotion packets, and reports.
- Create `temp/harmonization_recipe.csv` from `temp/harmonization_recipe_template.csv` after raw schema inspection. The project will not write `data/harmonized_household.csv` without verified raw files and explicit raw-to-harmonized mappings.
- The promotion registry is `result/promoted_country_wave_registry.csv`.
- The priority-first raw acquisition plan is `result/priority_promotion_acquisition_wave_plan.csv`.
- The priority official raw access probe is `result/priority_official_raw_access_summary.csv`.
- The priority raw intake gate is `result/priority_raw_intake_gate_summary.csv`.
- The priority archive/direct-file preflight is `result/priority_archive_member_preflight_summary.csv`.
- The priority climate linkage preflight is `result/priority_climate_linkage_preflight_summary.csv`.
- The priority raw verification workbook is `result/priority_raw_verification_workbook_summary.csv`.
- The priority manual verification decision gate is `result/priority_manual_verification_decision_summary.csv`.
- The priority raw package receipt ledger is `result/priority_raw_package_receipt_summary.csv`.
- The priority official download dossier is `result/priority_official_download_dossier_summary.csv`.
- The priority public documentation receipt is `result/priority_public_documentation_receipt_summary.csv`.
- The priority official metadata evidence extract is `result/priority_official_metadata_evidence_summary.csv`.
- The priority credentialed raw acquisition ledger is `result/priority_credentialed_raw_acquisition_summary.csv`.
- The priority official endpoint matrix is `result/priority_official_endpoint_matrix_summary.csv`.
- The priority core-file endpoint matrix is `result/priority_core_file_endpoint_matrix_summary.csv`.
- The priority threshold acquisition campaign is `result/priority_threshold_acquisition_campaign_summary.csv`.
- The priority first-pass variable review queue is `result/priority_first_pass_variable_review_summary.csv`.
- The priority download execution packet is `result/priority_download_execution_packet_summary.csv`.
- The priority LSMS/ISA alignment audit is `result/priority_lsms_isa_alignment_summary.csv`.
- The priority LSMS/ISA refocused acquisition queue is `result/priority_lsms_isa_refocused_acquisition_summary.csv`.
- The priority LSMS/ISA public documentation receipt is `result/priority_lsms_isa_public_documentation_receipt_summary.csv`; compact GPT-readable catalog/file digests are `temp/priority_lsms_isa_public_documentation_catalog_digest.csv` and `temp/priority_lsms_isa_public_documentation_file_inventory.csv`.
- The priority LSMS/ISA variable evidence matrix is `result/priority_lsms_isa_variable_evidence_summary.csv`; concept-level candidate variables and file shortlists are in `temp/priority_lsms_isa_variable_evidence_matrix.csv` and `temp/priority_lsms_isa_concept_file_shortlist.csv`.
- The priority LSMS/ISA raw package intake packet is `result/priority_lsms_isa_raw_package_intake_summary.csv`.
- The priority LSMS/ISA archive/direct-file preflight is `result/priority_lsms_isa_archive_member_preflight_summary.csv`.
- The priority LSMS/ISA raw value verification workbook is `result/priority_lsms_isa_raw_value_verification_workbook_summary.csv`.
- The priority LSMS/ISA raw package receipt checklist is `result/priority_lsms_isa_raw_package_receipt_checklist_summary.csv`.
- The priority LSMS/ISA credentialed raw acquisition workbench is `result/priority_lsms_isa_credentialed_raw_acquisition_workbench_summary.csv`.
- The priority LSMS/ISA official file receipt validator is `result/priority_lsms_isa_official_file_receipt_validator_summary.csv`.
- The priority LSMS/ISA threshold download sequence is `result/priority_lsms_isa_threshold_download_sequence_summary.csv`.
- The priority LSMS/ISA minimum-batch raw intake guide is `result/priority_lsms_isa_minimum_batch_raw_intake_guide_summary.csv`.
- The priority LSMS/ISA minimum-batch endpoint refresh is `result/priority_lsms_isa_minimum_batch_endpoint_refresh_summary.csv`.
- The priority LSMS/ISA next raw package action packet is `result/priority_lsms_isa_next_raw_package_action_summary.csv`.
- The priority LSMS/ISA incoming raw package router is `result/priority_lsms_isa_incoming_raw_package_router_summary.csv`; put uncertain manual downloads under `temp/raw_downloads/_incoming/` and review `temp/priority_lsms_isa_incoming_raw_package_route_plan.csv`.
- The priority LSMS/ISA threshold gap control panel is `result/priority_lsms_isa_threshold_gap_control_panel_summary.csv`; it shows the current country/wave gap and the 10 remaining minimum-batch raw package downloads.
- The priority LSMS/ISA manual download packets are indexed in `result/priority_lsms_isa_manual_download_packet_summary.csv` and `report/priority_lsms_isa_manual_download_packets.md`.
- The priority LSMS/ISA manual download progress tracker is `result/priority_lsms_isa_manual_download_progress_summary.csv`; it reports whether packet target folders contain files ready for validation.
- The priority LSMS/ISA promotion gate dashboard is `result/priority_lsms_isa_promotion_gate_dashboard_summary.csv`.
- The priority analysis dataset synthesis blueprint is `result/priority_analysis_dataset_synthesis_blueprint_summary.csv`.
- The priority country-wave promotion packets are indexed in `result/priority_country_wave_promotion_packet_summary.csv`.
- The refocused 19-wave LSMS/ISA country-wave promotion packets are indexed in `result/priority_lsms_isa_country_wave_promotion_packet_summary.csv`.
- The main promoted country-wave registry is refreshed from the refocused 19-wave LSMS/ISA queue in `result/promoted_country_wave_registry.csv`.
- Malawi 2004 is currently the only promoted analysis-ready household-climate country-wave; additional waves remain blocked until complete official raw packages are placed and pass receipt, value, semantics, timing/geography, and climate-linkage gates.
- The promoted-data gate is `result/promoted_data_gate_summary.csv`; if the registry has zero promoted rows, diagnostic CSVs are kept in `temp/diagnostic_data_quarantine/current/` rather than `data/`.
- Per-wave promotion packets are in `report/country_wave_promotion_packets/`.
- Refocused LSMS/ISA per-wave promotion packets are in `report/priority_lsms_isa_country_wave_promotion_packets/`.
- Albania remains a diagnostic template only unless its historical boundary, timing, and outcome gates are resolved.
