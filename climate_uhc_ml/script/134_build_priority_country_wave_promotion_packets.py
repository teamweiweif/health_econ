from __future__ import annotations

import csv
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from common import PROJECT_ROOT, REPORT_DIR, RESULT_DIR, TEMP_DIR, append_log, ensure_dirs, write_csv


WAVE_PLAN_PATH = RESULT_DIR / "priority_promotion_acquisition_wave_plan.csv"
REGISTRY_PATH = RESULT_DIR / "promoted_country_wave_registry.csv"
RAW_RECEIPT_PATH = TEMP_DIR / "priority_raw_package_receipt_ledger.csv"
PUBLIC_DOC_DATASET_PATH = TEMP_DIR / "priority_public_documentation_dataset_receipt.csv"
PUBLIC_DOC_RESOURCE_PATH = TEMP_DIR / "priority_public_documentation_receipt.csv"
MANUAL_DECISION_PATH = TEMP_DIR / "priority_manual_verification_decision_gate.csv"
MANUAL_REQUIREMENT_PATH = TEMP_DIR / "priority_manual_requirement_decision_audit.csv"
MANUAL_CONCEPT_PATH = TEMP_DIR / "priority_manual_concept_decision_audit.csv"
CLIMATE_PREFLIGHT_PATH = TEMP_DIR / "priority_climate_linkage_preflight.csv"
SYNTHESIS_JOIN_PATH = TEMP_DIR / "priority_analysis_dataset_join_plan.csv"
FILE_QUEUE_PATH = RESULT_DIR / "priority_promotion_acquisition_file_queue.csv"
OFFICIAL_DOSSIER_PATH = TEMP_DIR / "priority_official_download_dossier.csv"

PACKET_DIR = REPORT_DIR / "priority_country_wave_promotion_packets"
INDEX_PATH = TEMP_DIR / "priority_country_wave_promotion_packet_index.csv"
GATE_MATRIX_PATH = TEMP_DIR / "priority_country_wave_promotion_packet_gate_matrix.csv"
ACTION_QUEUE_PATH = TEMP_DIR / "priority_country_wave_promotion_packet_action_queue.csv"
SUMMARY_PATH = RESULT_DIR / "priority_country_wave_promotion_packet_summary.csv"
REPORT_PATH = REPORT_DIR / "priority_country_wave_promotion_packets.md"

INDEX_COLUMNS = [
    "acquisition_batch_rank",
    "batch_role",
    "country",
    "wave",
    "idno",
    "survey_name",
    "official_url",
    "local_target_folder",
    "public_documentation_status",
    "raw_package_status",
    "manual_verification_status",
    "financial_protection_status",
    "access_forgone_care_status",
    "climate_linkage_status",
    "synthesis_join_status",
    "analysis_ready_status",
    "packet_status",
    "failed_gate_count",
    "next_blocking_action",
    "packet_report",
    "raw_folder_handoff",
]

GATE_COLUMNS = [
    "acquisition_batch_rank",
    "batch_role",
    "country",
    "wave",
    "idno",
    "gate",
    "status",
    "evidence",
    "required_action",
]

ACTION_COLUMNS = [
    "action_rank",
    "acquisition_batch_rank",
    "batch_role",
    "country",
    "wave",
    "idno",
    "blocking_stage",
    "required_action",
    "local_target_folder",
    "official_url",
    "packet_report",
]

SUMMARY_COLUMNS = ["metric", "value", "interpretation"]


def read_csv_dicts(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def clean(value: Any) -> str:
    return "" if value is None else str(value).strip()


def safe_int(value: Any, default: int = 0) -> int:
    try:
        text = clean(value)
        return int(float(text)) if text else default
    except (TypeError, ValueError):
        return default


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(PROJECT_ROOT)).replace("\\", "/")
    except ValueError:
        return str(path).replace("\\", "/")


def one_by_id(rows: list[dict[str, str]], field: str = "idno") -> dict[str, dict[str, str]]:
    out: dict[str, dict[str, str]] = {}
    for row in rows:
        idno = clean(row.get(field))
        if idno and idno not in out:
            out[idno] = row
    return out


def by_id(rows: list[dict[str, str]], field: str = "idno") -> dict[str, list[dict[str, str]]]:
    out: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        idno = clean(row.get(field))
        if idno:
            out[idno].append(row)
    return out


def compact(values: list[str], limit: int = 8) -> str:
    out: list[str] = []
    seen: set[str] = set()
    for value in values:
        item = " ".join(clean(value).split())
        if item and item not in seen:
            out.append(item)
            seen.add(item)
        if len(out) >= limit:
            break
    return "; ".join(out)


def public_doc_ready(row: dict[str, str]) -> bool:
    return (
        clean(row.get("public_documentation_receipt_status")) in {
            "complete_full_public_documentation_receipt",
            "complete_core_public_documentation_receipt_optional_pdf_unlisted_or_missing",
        }
        and not clean(row.get("missing_core_resource_types"))
    )


def raw_package_ready(row: dict[str, str]) -> bool:
    return (
        safe_int(row.get("original_file_count")) > 0
        and safe_int(row.get("priority_targets_missing")) == 0
        and clean(row.get("receipt_status")) != "not_received_no_original_raw_package"
    )


def add_gate(
    gates: list[dict[str, str]],
    wave: dict[str, str],
    gate: str,
    passed: bool,
    evidence: str,
    required_action: str,
) -> None:
    gates.append(
        {
            "acquisition_batch_rank": wave.get("acquisition_batch_rank", ""),
            "batch_role": wave.get("batch_role", ""),
            "country": wave.get("country", ""),
            "wave": wave.get("wave", ""),
            "idno": wave.get("idno", ""),
            "gate": gate,
            "status": "pass" if passed else "fail",
            "evidence": evidence,
            "required_action": "" if passed else required_action,
        }
    )


def raw_folder_path(folder: str, idno: str) -> Path:
    folder_clean = clean(folder).replace("\\", "/").strip("/")
    if folder_clean:
        return PROJECT_ROOT / folder_clean
    return TEMP_DIR / "raw_downloads" / idno


def markdown_table(rows: list[dict[str, str]], columns: list[str], limit: int = 20) -> str:
    lines = ["| " + " | ".join(columns) + " |", "|" + "|".join("---" for _ in columns) + "|"]
    for row in rows[:limit]:
        values = []
        for column in columns:
            value = clean(row.get(column)).replace("|", "/")
            if len(value) > 120:
                value = value[:117] + "..."
            values.append(value)
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines)


def write_packet(
    wave: dict[str, str],
    index_row: dict[str, str],
    gates: list[dict[str, str]],
    public_resources: list[dict[str, str]],
    file_queue: list[dict[str, str]],
    req_rows: list[dict[str, str]],
    concept_rows: list[dict[str, str]],
) -> str:
    PACKET_DIR.mkdir(parents=True, exist_ok=True)
    path = PACKET_DIR / f"{wave['idno']}.md"
    failed = [row for row in gates if row["status"] != "pass"]
    resources = [
        {
            "resource_type": row.get("resource_type", ""),
            "receipt_status": row.get("receipt_status", ""),
            "saved_path": row.get("saved_path", ""),
        }
        for row in public_resources
    ]
    files = [
        {
            "file_rank": row.get("file_rank", ""),
            "file_name": row.get("file_name", ""),
            "candidate_categories": row.get("candidate_categories", ""),
            "candidate_harmonized_variables": row.get("candidate_harmonized_variables", ""),
        }
        for row in file_queue[:12]
    ]
    req_preview = [
        {
            "item_id": row.get("item_id", ""),
            "manual_decision_status": row.get("manual_decision_status", ""),
            "missing_or_failed_fields": row.get("missing_or_failed_fields", ""),
        }
        for row in req_rows[:8]
    ]
    concept_preview = [
        {
            "item_id": row.get("item_id", ""),
            "manual_decision_status": row.get("manual_decision_status", ""),
            "missing_or_failed_fields": row.get("missing_or_failed_fields", ""),
        }
        for row in concept_rows[:13]
    ]
    path.write_text(
        f"""# Priority Country-Wave Promotion Packet

Dataset: {wave.get('idno', '')} - {wave.get('country', '')} {wave.get('wave', '')}

Survey: {wave.get('survey_name', '')}

Official URL: {wave.get('official_url', '')}

Target raw folder: `{wave.get('local_target_folder', '')}`

Current packet status: `{index_row.get('packet_status', '')}`

Analysis-ready status: `{index_row.get('analysis_ready_status', '')}`

Next blocking action: {index_row.get('next_blocking_action', '')}

## Gate Matrix

{markdown_table(gates, ['gate', 'status', 'evidence', 'required_action'], 20)}

## Public Documentation Receipt

{markdown_table(resources, ['resource_type', 'receipt_status', 'saved_path'], 12)}

## Priority Raw File Queue

{markdown_table(files, ['file_rank', 'file_name', 'candidate_categories', 'candidate_harmonized_variables'], 12)}

## Manual Requirement Review Queue

{markdown_table(req_preview, ['item_id', 'manual_decision_status', 'missing_or_failed_fields'], 12)}

## Manual Concept Review Queue

{markdown_table(concept_preview, ['item_id', 'manual_decision_status', 'missing_or_failed_fields'], 16)}

## Stop Rule

Do not write this country-wave into `data/` until the complete original raw
package is received, priority raw modules are covered, required raw values and
merge keys are manually verified, financial/access outcomes are verified, and
an accepted CHIRPS or ERA5 linkage route exists.

Failed gates currently blocking promotion: {len(failed)}.
""",
        encoding="utf-8",
    )
    return rel(path)


def write_raw_handoff(wave: dict[str, str], packet_path: str, failed_count: int) -> str:
    folder = raw_folder_path(wave.get("local_target_folder", ""), wave.get("idno", ""))
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / "_PRIORITY_COUNTRY_WAVE_PROMOTION_PACKET.md"
    path.write_text(
        f"""# Priority Country-Wave Promotion Packet Handoff

Dataset: {wave.get('idno', '')} - {wave.get('country', '')} {wave.get('wave', '')}

Packet report: `{packet_path}`

Current status: blocked from `data/` promotion.

Failed gates: {failed_count}

Required next step: place the complete unchanged official raw package and
documentation in this folder, then rerun the priority receipt, archive,
schema, manual verification, climate-linkage, synthesis, promoted-data, bundle,
and validation gates.
""",
        encoding="utf-8",
    )
    return rel(path)


def build_outputs() -> tuple[list[dict[str, str]], list[dict[str, str]], list[dict[str, str]], list[dict[str, str]]]:
    waves = read_csv_dicts(WAVE_PLAN_PATH)
    registry_by_id = one_by_id(read_csv_dicts(REGISTRY_PATH))
    raw_by_id = one_by_id(read_csv_dicts(RAW_RECEIPT_PATH))
    public_dataset_by_id = one_by_id(read_csv_dicts(PUBLIC_DOC_DATASET_PATH))
    public_resource_by_id = by_id(read_csv_dicts(PUBLIC_DOC_RESOURCE_PATH))
    manual_by_id = one_by_id(read_csv_dicts(MANUAL_DECISION_PATH))
    req_by_id = by_id(read_csv_dicts(MANUAL_REQUIREMENT_PATH))
    concept_by_id = by_id(read_csv_dicts(MANUAL_CONCEPT_PATH))
    climate_by_id = one_by_id(read_csv_dicts(CLIMATE_PREFLIGHT_PATH))
    synthesis_by_id = one_by_id(read_csv_dicts(SYNTHESIS_JOIN_PATH))
    files_by_id = by_id(read_csv_dicts(FILE_QUEUE_PATH))
    dossier_by_id = one_by_id(read_csv_dicts(OFFICIAL_DOSSIER_PATH))

    index_rows: list[dict[str, str]] = []
    gate_rows: list[dict[str, str]] = []
    action_rows: list[dict[str, str]] = []

    for wave in waves:
        idno = wave.get("idno", "")
        registry = registry_by_id.get(idno, {})
        raw = raw_by_id.get(idno, {})
        public_dataset = public_dataset_by_id.get(idno, {})
        manual = manual_by_id.get(idno, {})
        climate = climate_by_id.get(idno, {})
        synthesis = synthesis_by_id.get(idno, {})
        dossier = dossier_by_id.get(idno, {})

        gates: list[dict[str, str]] = []
        public_ready = public_doc_ready(public_dataset)
        raw_ready = raw_package_ready(raw)
        archive_ready = safe_int(raw.get("priority_targets_missing")) == 0 and safe_int(raw.get("priority_file_targets")) > 0 and raw_ready
        requirements_ready = safe_int(manual.get("requirements_passed")) >= safe_int(manual.get("requirement_rows")) and safe_int(manual.get("requirement_rows")) > 0
        concepts_ready = safe_int(manual.get("concepts_passed")) >= safe_int(manual.get("concept_rows")) and safe_int(manual.get("concept_rows")) > 0
        variables_ready = safe_int(manual.get("variables_passed")) >= safe_int(manual.get("variable_rows")) and safe_int(manual.get("variable_rows")) > 0
        financial_ready = clean(manual.get("financial_protection_manual_ready")) == "1"
        access_ready = clean(manual.get("double_failure_manual_ready")) == "1"
        climate_ready = clean(climate.get("accepted_chirps_era5_route_status")).startswith("accepted")
        synthesis_ready = clean(synthesis.get("join_plan_status")) == "ready_for_promoted_dataset_build"
        registry_ready = clean(registry.get("analysis_ready_status")) == "promoted_analysis_ready"

        add_gate(
            gates,
            wave,
            "official_public_documentation_receipt",
            public_ready,
            f"status={public_dataset.get('public_documentation_receipt_status', '')}; saved={public_dataset.get('saved_resource_types', '')}; missing_core={public_dataset.get('missing_core_resource_types', '')}",
            "Run the priority public documentation receipt and save all core public documentation resources.",
        )
        add_gate(
            gates,
            wave,
            "complete_original_raw_package",
            raw_ready,
            f"receipt_status={raw.get('receipt_status', '')}; original_files={raw.get('original_file_count', '0')}; archives={raw.get('archive_file_count', '0')}; raw_tabular={raw.get('raw_tabular_file_count', '0')}; missing_targets={raw.get('priority_targets_missing', '')}",
            "Download/place the complete unchanged original raw package and documentation in the target folder.",
        )
        add_gate(
            gates,
            wave,
            "priority_raw_module_coverage",
            archive_ready,
            f"targets={raw.get('priority_file_targets', '0')}; covered={raw.get('priority_targets_covered_direct_or_archive', '0')}; missing={raw.get('priority_targets_missing', '')}",
            "Ensure every priority target module is present directly or inside the received archive.",
        )
        add_gate(
            gates,
            wave,
            "manual_requirement_verification",
            requirements_ready,
            f"requirements_passed={manual.get('requirements_passed', '0')}/{manual.get('requirement_rows', '0')}",
            "Verify merge keys, survey design, consumption/income, OOP, access, timing, geography, missing codes, units, and recall periods.",
        )
        add_gate(
            gates,
            wave,
            "manual_concept_verification",
            concepts_ready,
            f"concepts_passed={manual.get('concepts_passed', '0')}/{manual.get('concept_rows', '0')}",
            "Promote all required concepts only after raw variable value and level checks pass.",
        )
        add_gate(
            gates,
            wave,
            "manual_variable_verification",
            variables_ready,
            f"variables_passed={manual.get('variables_passed', '0')}/{manual.get('variable_rows', '0')}",
            "Manually verify selected raw variables before harmonization recipe review.",
        )
        add_gate(
            gates,
            wave,
            "financial_protection_value_ready",
            financial_ready,
            f"financial_requirements_passed={manual.get('financial_requirements_passed', '0')}; financial_concepts_passed={manual.get('financial_concepts_passed', '0')}",
            "Verify total consumption/income, OOP health expenditure, weights/design, and denominator semantics for CHE10/CHE25 and SDG 3.8.2 review.",
        )
        add_gate(
            gates,
            wave,
            "access_forgone_care_value_ready",
            access_ready,
            f"double_failure_requirements_passed={manual.get('double_failure_requirements_passed', '0')}; double_failure_concepts_passed={manual.get('double_failure_concepts_passed', '0')}",
            "Verify illness/need, care seeking, forgone-care, and barrier variables with raw values and skip patterns.",
        )
        add_gate(
            gates,
            wave,
            "accepted_chirps_era5_climate_linkage",
            climate_ready,
            f"accepted_route={climate.get('accepted_chirps_era5_route_status', '')}; gate={climate.get('current_climate_linkage_gate_status', '')}; planned_level={climate.get('planned_geography_level', '')}",
            "Verify timing/geography raw fields and accept a CHIRPS or ERA5 linkage route.",
        )
        add_gate(
            gates,
            wave,
            "analysis_dataset_synthesis_join",
            synthesis_ready,
            f"join_status={synthesis.get('join_plan_status', '')}; required_columns={synthesis.get('required_schema_columns', '0')}; ready_columns={synthesis.get('synthesis_ready_columns', '0')}; blocked_columns={synthesis.get('blocked_columns', '0')}",
            "Complete required schema-column verification and join readiness before any promoted dataset build.",
        )
        add_gate(
            gates,
            wave,
            "promoted_data_registry_write_gate",
            registry_ready,
            f"registry_analysis_ready={registry.get('analysis_ready_status', 'missing')}; rows={registry.get('rows', '0')}",
            "Write to data/ only after the promoted registry marks this wave as analysis-ready.",
        )

        failed = [row for row in gates if row["status"] != "pass"]
        if not raw_ready:
            next_action = "download_or_place_complete_original_raw_package"
            next_action_text = "Download/place the complete unchanged original raw package and documentation in local_target_folder."
        elif not archive_ready:
            next_action = "cover_priority_raw_modules"
            next_action_text = "Confirm the received raw package covers all priority target modules."
        elif not (requirements_ready and concepts_ready and variables_ready):
            next_action = "manual_value_key_unit_verification"
            next_action_text = "Complete manual raw value, key, unit, recall-period, missing-code, and skip-pattern verification."
        elif not climate_ready:
            next_action = "accept_chirps_or_era5_route"
            next_action_text = "Accept a CHIRPS or ERA5 climate-linkage route after timing/geography verification."
        elif not synthesis_ready:
            next_action = "complete_synthesis_join_review"
            next_action_text = "Complete promoted household-climate schema and join review."
        elif not registry_ready:
            next_action = "open_promoted_data_write_gate"
            next_action_text = "Refresh promoted registry and data write gate after all upstream gates pass."
        else:
            next_action = "ready_for_promoted_data_write"
            next_action_text = "All packet gates pass; write promoted dataset via the controlled pipeline."

        index_row = {
            "acquisition_batch_rank": wave.get("acquisition_batch_rank", ""),
            "batch_role": wave.get("batch_role", ""),
            "country": wave.get("country", ""),
            "wave": wave.get("wave", ""),
            "idno": idno,
            "survey_name": wave.get("survey_name", ""),
            "official_url": wave.get("official_url", dossier.get("official_get_microdata_url", "")),
            "local_target_folder": wave.get("local_target_folder", ""),
            "public_documentation_status": "ready" if public_ready else "blocked",
            "raw_package_status": raw.get("receipt_status", "missing"),
            "manual_verification_status": manual.get("manual_verification_status", "missing"),
            "financial_protection_status": "ready" if financial_ready else "blocked",
            "access_forgone_care_status": "ready" if access_ready else "blocked",
            "climate_linkage_status": "ready" if climate_ready else "blocked",
            "synthesis_join_status": synthesis.get("join_plan_status", "missing"),
            "analysis_ready_status": registry.get("analysis_ready_status", "not_promoted"),
            "packet_status": "ready_for_promoted_data_write" if not failed else "blocked_fail_closed",
            "failed_gate_count": str(len(failed)),
            "next_blocking_action": next_action,
            "packet_report": "",
            "raw_folder_handoff": "",
        }
        packet_path = write_packet(wave, index_row, gates, public_resource_by_id.get(idno, []), files_by_id.get(idno, []), req_by_id.get(idno, []), concept_by_id.get(idno, []))
        index_row["packet_report"] = packet_path
        index_row["raw_folder_handoff"] = write_raw_handoff(wave, packet_path, len(failed))
        index_rows.append(index_row)
        gate_rows.extend(gates)
        if failed:
            action_rows.append(
                {
                    "action_rank": "",
                    "acquisition_batch_rank": wave.get("acquisition_batch_rank", ""),
                    "batch_role": wave.get("batch_role", ""),
                    "country": wave.get("country", ""),
                    "wave": wave.get("wave", ""),
                    "idno": idno,
                    "blocking_stage": next_action,
                    "required_action": next_action_text,
                    "local_target_folder": wave.get("local_target_folder", ""),
                    "official_url": wave.get("official_url", ""),
                    "packet_report": packet_path,
                }
            )

    action_rows.sort(key=lambda row: safe_int(row.get("acquisition_batch_rank"), 999999))
    for rank, row in enumerate(action_rows, start=1):
        row["action_rank"] = str(rank)

    summary = build_summary(index_rows, gate_rows, action_rows)
    return index_rows, gate_rows, action_rows, summary


def build_summary(index_rows: list[dict[str, str]], gate_rows: list[dict[str, str]], action_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    gate_counts = Counter(row["status"] for row in gate_rows)
    next_counts = Counter(row["next_blocking_action"] for row in index_rows)
    packet_counts = Counter(row["packet_status"] for row in index_rows)
    role_counts = Counter(row["batch_role"] for row in index_rows)
    rows = [
        {"metric": "priority_country_wave_packet_rows", "value": str(len(index_rows)), "interpretation": "Priority and backup country-wave promotion packets built."},
        {"metric": "priority_country_wave_packet_priority_batch_rows", "value": str(role_counts.get("priority_10_wave_batch", 0)), "interpretation": "Immediate priority wave packets."},
        {"metric": "priority_country_wave_packet_backup_rows", "value": str(role_counts.get("sixth_country_backup_candidate", 0)), "interpretation": "Sixth-country backup wave packets."},
        {"metric": "priority_country_wave_packet_gate_rows", "value": str(len(gate_rows)), "interpretation": "Gate rows across priority promotion packets."},
        {"metric": "priority_country_wave_packet_passed_gate_rows", "value": str(gate_counts.get("pass", 0)), "interpretation": "Packet gates currently passing."},
        {"metric": "priority_country_wave_packet_failed_gate_rows", "value": str(gate_counts.get("fail", 0)), "interpretation": "Packet gates still blocking promotion."},
        {"metric": "priority_country_wave_packet_public_documentation_ready_rows", "value": str(sum(1 for row in index_rows if row["public_documentation_status"] == "ready")), "interpretation": "Packets with complete core public documentation receipt."},
        {"metric": "priority_country_wave_packet_raw_package_ready_rows", "value": str(sum(1 for row in index_rows if row["raw_package_status"] != "not_received_no_original_raw_package")), "interpretation": "Packets with a non-empty original raw package receipt."},
        {"metric": "priority_country_wave_packet_financial_ready_rows", "value": str(sum(1 for row in index_rows if row["financial_protection_status"] == "ready")), "interpretation": "Packets ready for financial-protection outcomes."},
        {"metric": "priority_country_wave_packet_access_ready_rows", "value": str(sum(1 for row in index_rows if row["access_forgone_care_status"] == "ready")), "interpretation": "Packets ready for access/forgone-care outcomes."},
        {"metric": "priority_country_wave_packet_climate_ready_rows", "value": str(sum(1 for row in index_rows if row["climate_linkage_status"] == "ready")), "interpretation": "Packets with accepted CHIRPS/ERA5 climate-linkage route."},
        {"metric": "priority_country_wave_packet_analysis_ready_rows", "value": str(sum(1 for row in index_rows if row["analysis_ready_status"] == "promoted_analysis_ready")), "interpretation": "Packets ready for promoted data writes."},
        {"metric": "priority_country_wave_packet_action_rows", "value": str(len(action_rows)), "interpretation": "Next blocking actions across packets."},
        {"metric": "priority_country_wave_packet_reports_written", "value": str(sum(1 for row in index_rows if row.get("packet_report"))), "interpretation": "Per-wave packet markdown reports written."},
        {"metric": "priority_country_wave_packet_handoffs_written", "value": str(sum(1 for row in index_rows if row.get("raw_folder_handoff"))), "interpretation": "Per-wave raw-folder packet handoffs written."},
        {"metric": "modeling_gate_status", "value": "blocked", "interpretation": "Models remain blocked until promoted registry thresholds and accepted climate linkage pass."},
    ]
    for status, count in sorted(packet_counts.items()):
        rows.append({"metric": f"priority_country_wave_packet_status_{status}", "value": str(count), "interpretation": "Packet status count."})
    for action, count in sorted(next_counts.items()):
        rows.append({"metric": f"priority_country_wave_packet_next_action_{action}", "value": str(count), "interpretation": "Next blocking action count."})
    return rows


def write_report(index_rows: list[dict[str, str]], gate_rows: list[dict[str, str]], action_rows: list[dict[str, str]], summary: list[dict[str, str]]) -> None:
    summary_table = "\n".join(f"| {row['metric']} | {row['value']} | {row['interpretation']} |" for row in summary)
    failing_gates = [row for row in gate_rows if row["status"] != "pass"]
    REPORT_PATH.write_text(
        f"""# Priority Country-Wave Promotion Packets

Status: fail-closed packet layer for the priority dataset-promotion batch. This
is the packet handoff for moving from metadata-only candidates toward verified
analysis-ready household x climate datasets. It does not write data into
`data/`.

## Summary

| Metric | Value | Interpretation |
|---|---:|---|
{summary_table}

## Packet Index

{markdown_table(index_rows, ['acquisition_batch_rank', 'idno', 'country', 'wave', 'public_documentation_status', 'raw_package_status', 'financial_protection_status', 'access_forgone_care_status', 'climate_linkage_status', 'packet_status', 'next_blocking_action'], 20)}

## Next Blocking Actions

{markdown_table(action_rows, ['action_rank', 'idno', 'blocking_stage', 'required_action', 'local_target_folder'], 20)}

## Failed Gate Preview

{markdown_table(failing_gates, ['acquisition_batch_rank', 'idno', 'gate', 'status', 'evidence', 'required_action'], 30)}

## Machine-Readable Outputs

- `temp/priority_country_wave_promotion_packet_index.csv`
- `temp/priority_country_wave_promotion_packet_gate_matrix.csv`
- `temp/priority_country_wave_promotion_packet_action_queue.csv`
- `result/priority_country_wave_promotion_packet_summary.csv`
- `report/priority_country_wave_promotion_packets/`
""",
        encoding="utf-8",
    )


def main() -> None:
    ensure_dirs()
    index_rows, gate_rows, action_rows, summary = build_outputs()
    write_csv(INDEX_PATH, index_rows, INDEX_COLUMNS)
    write_csv(GATE_MATRIX_PATH, gate_rows, GATE_COLUMNS)
    write_csv(ACTION_QUEUE_PATH, action_rows, ACTION_COLUMNS)
    write_csv(SUMMARY_PATH, summary, SUMMARY_COLUMNS)
    write_report(index_rows, gate_rows, action_rows, summary)
    append_log(
        TEMP_DIR / "audit_log.md",
        f"Built priority country-wave promotion packets packets={len(index_rows)} gates={len(gate_rows)} actions={len(action_rows)}.",
    )
    print(f"Priority country-wave promotion packets rows={len(index_rows)} gates={len(gate_rows)}.")


if __name__ == "__main__":
    main()
