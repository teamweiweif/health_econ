from __future__ import annotations

import csv
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from common import PROJECT_ROOT, REPORT_DIR, RESULT_DIR, TEMP_DIR, append_log, ensure_dirs, write_csv


WAVE_PLAN_PATH = RESULT_DIR / "priority_promotion_acquisition_wave_plan.csv"
THRESHOLD_CAMPAIGN_PATH = TEMP_DIR / "priority_threshold_acquisition_campaign.csv"
OFFICIAL_DOSSIER_PATH = TEMP_DIR / "priority_official_download_dossier.csv"
CREDENTIALED_LEDGER_PATH = TEMP_DIR / "priority_credentialed_raw_acquisition_ledger.csv"
RECEIPT_LEDGER_PATH = TEMP_DIR / "priority_raw_package_receipt_ledger.csv"
CORE_FILE_CHECKLIST_PATH = TEMP_DIR / "priority_credentialed_raw_core_file_checklist.csv"
FIRST_PASS_QUEUE_PATH = TEMP_DIR / "priority_first_pass_variable_review_queue.csv"
FIRST_PASS_COVERAGE_PATH = TEMP_DIR / "priority_first_pass_requirement_coverage.csv"

PACKET_PATH = TEMP_DIR / "priority_download_execution_packet.csv"
FILE_ACCEPTANCE_PATH = TEMP_DIR / "priority_download_file_acceptance_matrix.csv"
SUMMARY_PATH = RESULT_DIR / "priority_download_execution_packet_summary.csv"
REPORT_PATH = REPORT_DIR / "priority_download_execution_packet.md"

RAW_ROOT = TEMP_DIR / "raw_downloads"

PACKET_COLUMNS = [
    "download_order",
    "acquisition_batch_rank",
    "batch_role",
    "campaign_phase",
    "threshold_role",
    "country",
    "wave",
    "idno",
    "survey_name",
    "official_get_microdata_url",
    "register_url",
    "terms_or_request_urls",
    "data_dictionary_url",
    "ddi_metadata_url",
    "json_metadata_url",
    "related_materials_url",
    "local_target_folder",
    "download_scope",
    "credentialed_acquisition_status",
    "raw_receipt_status",
    "receipt_original_file_count",
    "priority_core_file_rows",
    "priority_core_file_names",
    "priority_targets_missing",
    "first_pass_requirement_rows",
    "first_pass_selected_variable_rows",
    "download_execution_status",
    "minimum_acceptance_rule",
    "post_download_acceptance_commands",
    "promotion_stop_rule",
    "handoff_readme",
]

FILE_COLUMNS = [
    "download_order",
    "acquisition_batch_rank",
    "batch_role",
    "country",
    "wave",
    "idno",
    "core_file_rank",
    "metadata_file_name",
    "metadata_file_description",
    "candidate_categories",
    "candidate_harmonized_variables",
    "expected_local_name_patterns",
    "current_receipt_status",
    "file_acceptance_status",
    "post_download_verification",
]

SUMMARY_COLUMNS = ["metric", "value", "interpretation"]

POST_DOWNLOAD_COMMANDS = [
    "python script/17_audit_raw_downloads.py",
    "python script/128_build_priority_archive_member_preflight.py",
    "python script/130_build_priority_raw_package_receipt_ledger.py",
    "python script/03_inspect_raw_schemas.py",
    "python script/29_build_raw_variable_verification_protocol.py",
    "python script/33_build_harmonization_recipe_gate.py",
    "python script/125_build_priority_climate_linkage_preflight.py",
    "python script/126_build_priority_raw_verification_workbook.py",
    "python script/140_build_priority_first_pass_variable_review_queue.py",
    "python script/129_build_priority_manual_verification_decision_gate.py",
    "python script/132_build_priority_analysis_dataset_synthesis_blueprint.py",
    "python script/134_build_priority_country_wave_promotion_packets.py",
    "python script/127_enforce_promoted_data_gate.py",
    "python script/36_build_direct_read_audit_bundle.py",
    "python script/14_validate_workspace.py",
]


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
        key = clean(row.get(field))
        if key and key not in out:
            out[key] = row
    return out


def group(rows: list[dict[str, str]], field: str) -> dict[str, list[dict[str, str]]]:
    out: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        key = clean(row.get(field))
        if key:
            out[key].append(row)
    return out


def compact(values: list[str], limit: int = 20, sep: str = ";") -> str:
    out: list[str] = []
    seen: set[str] = set()
    for value in values:
        item = clean(value)
        if item and item not in seen:
            out.append(item)
            seen.add(item)
        if len(out) >= limit:
            break
    return sep.join(out)


def raw_folder_path(folder: str, idno: str) -> Path:
    folder_clean = clean(folder).replace("\\", "/").strip("/")
    if folder_clean.startswith("temp/raw_downloads/"):
        return PROJECT_ROOT / folder_clean
    if folder_clean:
        return RAW_ROOT / folder_clean
    return RAW_ROOT / idno


def raw_received(receipt: dict[str, str]) -> bool:
    return safe_int(receipt.get("original_file_count")) > 0 or clean(receipt.get("receipt_status")) in {
        "complete_raw_package_candidate_ready_for_schema_and_manual_audit",
        "raw_targets_covered_documentation_review_needed",
    }


def execution_status(credentialed_status: str, receipt: dict[str, str], core_files: int, first_pass_rows: int) -> str:
    if raw_received(receipt):
        if safe_int(receipt.get("priority_targets_missing")) == 0:
            return "raw_received_ready_for_acceptance_commands"
        return "partial_raw_receipt_needs_missing_core_files"
    if credentialed_status == "ready_for_credentialed_manual_download" and core_files > 0 and first_pass_rows > 0:
        return "ready_for_manual_credentialed_download_no_raw_receipt"
    if credentialed_status == "ready_for_credentialed_manual_download":
        return "ready_for_manual_download_but_acceptance_inputs_incomplete"
    return "blocked_credentialed_download_plan_incomplete"


def file_acceptance_status(receipt_status: str) -> str:
    if receipt_status in {"complete_raw_package_candidate_ready_for_schema_and_manual_audit", "raw_targets_covered_documentation_review_needed"}:
        return "ready_for_file_presence_and_schema_acceptance"
    if receipt_status == "partial_raw_package_candidate_missing_priority_targets":
        return "blocked_missing_priority_core_file"
    return "blocked_no_raw_or_archive_file"


def markdown_table(rows: list[dict[str, str]], columns: list[str], limit: int = 30) -> str:
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


def markdown_counter(counter: Counter[str], label: str) -> str:
    lines = [f"| {label} | Count |", "|---|---:|"]
    for key, count in counter.most_common():
        lines.append(f"| `{key or 'blank'}` | {count} |")
    return "\n".join(lines)


def write_handoff(packet: dict[str, str], file_rows: list[dict[str, str]], first_pass_rows: list[dict[str, str]]) -> str:
    folder = raw_folder_path(packet.get("local_target_folder", ""), packet.get("idno", ""))
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / "_PRIORITY_DOWNLOAD_EXECUTION_PACKET.md"
    path.write_text(
        f"""# Priority Download Execution Packet

Dataset: `{packet.get('idno', '')}` - {packet.get('country', '')} {packet.get('wave', '')}

Download order: {packet.get('download_order', '')}

Official get-microdata URL: {packet.get('official_get_microdata_url', '')}

Target folder: `{packet.get('local_target_folder', '')}`

Current status: `{packet.get('download_execution_status', '')}`

Raw receipt: `{packet.get('raw_receipt_status', '')}`

## Manual Download Scope

Download the complete unchanged official raw package plus all documentation
through the permitted World Bank account, terms, or Data Access Agreement
workflow. Do not assemble an incomplete analysis package from only the listed
core files.

## Minimum Acceptance Rule

{packet.get('minimum_acceptance_rule', '')}

## Core Files To Confirm

{markdown_table(file_rows, ['core_file_rank', 'metadata_file_name', 'candidate_categories', 'expected_local_name_patterns', 'file_acceptance_status'], 40)}

## First-Pass Variables To Inspect

{markdown_table(first_pass_rows, ['requirement_id', 'concept', 'candidate_files', 'candidate_raw_variable', 'metadata_confidence', 'first_pass_review_status'], 40)}

## Post-Download Commands

{chr(10).join(f'- `{command}`' for command in POST_DOWNLOAD_COMMANDS)}

## Stop Rule

{packet.get('promotion_stop_rule', '')}
""",
        encoding="utf-8",
    )
    return rel(path)


def build_packets() -> tuple[list[dict[str, str]], list[dict[str, str]], list[str]]:
    waves = read_csv_dicts(WAVE_PLAN_PATH)
    campaign_by_id = one_by_id(read_csv_dicts(THRESHOLD_CAMPAIGN_PATH))
    dossier_by_id = one_by_id(read_csv_dicts(OFFICIAL_DOSSIER_PATH))
    credentialed_by_id = one_by_id(read_csv_dicts(CREDENTIALED_LEDGER_PATH))
    receipt_by_id = one_by_id(read_csv_dicts(RECEIPT_LEDGER_PATH))
    core_by_id = group(read_csv_dicts(CORE_FILE_CHECKLIST_PATH), "idno")
    first_pass_by_id = group(read_csv_dicts(FIRST_PASS_QUEUE_PATH), "idno")
    coverage_by_id = group(read_csv_dicts(FIRST_PASS_COVERAGE_PATH), "idno")

    packets: list[dict[str, str]] = []
    file_rows: list[dict[str, str]] = []
    handoffs: list[str] = []

    for order, wave in enumerate(sorted(waves, key=lambda row: safe_int(row.get("acquisition_batch_rank"), 9999)), start=1):
        idno = clean(wave.get("idno"))
        campaign = campaign_by_id.get(idno, {})
        dossier = dossier_by_id.get(idno, {})
        credentialed = credentialed_by_id.get(idno, {})
        receipt = receipt_by_id.get(idno, {})
        core_rows = core_by_id.get(idno, [])
        first_pass_rows = first_pass_by_id.get(idno, [])
        coverage_rows = coverage_by_id.get(idno, [])
        receipt_status = clean(receipt.get("receipt_status")) or clean(campaign.get("raw_receipt_status")) or "missing_receipt_status"
        credentialed_status = clean(credentialed.get("credentialed_acquisition_status")) or "missing_credentialed_acquisition_status"
        core_file_names = compact([row.get("metadata_file_name", "") for row in sorted(core_rows, key=lambda row: safe_int(row.get("core_file_rank"), 9999))], 30)
        packet = {
            "download_order": str(order),
            "acquisition_batch_rank": wave.get("acquisition_batch_rank", ""),
            "batch_role": wave.get("batch_role", ""),
            "campaign_phase": campaign.get("campaign_phase", ""),
            "threshold_role": campaign.get("threshold_role", ""),
            "country": wave.get("country", ""),
            "wave": wave.get("wave", ""),
            "idno": idno,
            "survey_name": wave.get("survey_name", ""),
            "official_get_microdata_url": clean(credentialed.get("official_get_microdata_url")) or clean(dossier.get("official_get_microdata_url")) or wave.get("official_url", ""),
            "register_url": clean(credentialed.get("register_url")) or clean(dossier.get("register_url")),
            "terms_or_request_urls": clean(credentialed.get("terms_or_request_urls")) or clean(dossier.get("terms_or_request_urls")),
            "data_dictionary_url": dossier.get("data_dictionary_url", ""),
            "ddi_metadata_url": dossier.get("ddi_metadata_url", ""),
            "json_metadata_url": dossier.get("json_metadata_url", ""),
            "related_materials_url": dossier.get("related_materials_url", ""),
            "local_target_folder": clean(credentialed.get("local_target_folder")) or clean(dossier.get("local_target_folder")) or wave.get("local_target_folder", ""),
            "download_scope": clean(credentialed.get("download_scope")) or "complete_official_raw_package_plus_all_documentation",
            "credentialed_acquisition_status": credentialed_status,
            "raw_receipt_status": receipt_status,
            "receipt_original_file_count": clean(receipt.get("original_file_count")) or "0",
            "priority_core_file_rows": str(len(core_rows)),
            "priority_core_file_names": core_file_names,
            "priority_targets_missing": clean(receipt.get("priority_targets_missing")) or str(len(core_rows)),
            "first_pass_requirement_rows": str(len(coverage_rows)),
            "first_pass_selected_variable_rows": str(len(first_pass_rows)),
            "download_execution_status": execution_status(credentialed_status, receipt, len(core_rows), len(first_pass_rows)),
            "minimum_acceptance_rule": f"Complete official package must be present; at least {len(core_rows)} priority core files/modules must be found directly or inside the official archive; all 8 promotion requirements and {len(first_pass_rows)} selected first-pass variables must remain raw-backed before any data/ write.",
            "post_download_acceptance_commands": "; ".join(POST_DOWNLOAD_COMMANDS),
            "promotion_stop_rule": "Do not write this country-wave into data/ until original package receipt, core-file coverage, raw schema inspection, manual value/unit/key review, outcome readiness, and accepted CHIRPS/ERA5 linkage all pass.",
            "handoff_readme": "",
        }
        per_file_rows: list[dict[str, str]] = []
        for core in sorted(core_rows, key=lambda row: safe_int(row.get("core_file_rank"), 9999)):
            file_row = {
                "download_order": str(order),
                "acquisition_batch_rank": wave.get("acquisition_batch_rank", ""),
                "batch_role": wave.get("batch_role", ""),
                "country": wave.get("country", ""),
                "wave": wave.get("wave", ""),
                "idno": idno,
                "core_file_rank": core.get("core_file_rank", ""),
                "metadata_file_name": core.get("metadata_file_name", ""),
                "metadata_file_description": core.get("metadata_file_description", ""),
                "candidate_categories": core.get("candidate_categories", ""),
                "candidate_harmonized_variables": core.get("candidate_harmonized_variables", ""),
                "expected_local_name_patterns": core.get("expected_local_name_patterns", ""),
                "current_receipt_status": receipt_status,
                "file_acceptance_status": file_acceptance_status(receipt_status),
                "post_download_verification": "Confirm this file/module exists directly or inside the complete official package, inspect schema, and connect accepted variables to the manual verification templates.",
            }
            per_file_rows.append(file_row)
            file_rows.append(file_row)
        packet["handoff_readme"] = write_handoff(packet, per_file_rows, first_pass_rows)
        handoffs.append(packet["handoff_readme"])
        packets.append(packet)

    return packets, file_rows, handoffs


def build_summary(packets: list[dict[str, str]], file_rows: list[dict[str, str]], handoffs: list[str]) -> list[dict[str, str]]:
    status_counts = Counter(row["download_execution_status"] for row in packets)
    file_status_counts = Counter(row["file_acceptance_status"] for row in file_rows)
    batch_counts = Counter(row["batch_role"] for row in packets)
    raw_received = sum(1 for row in packets if safe_int(row.get("receipt_original_file_count")) > 0)
    total_first_pass = sum(safe_int(row.get("first_pass_selected_variable_rows")) for row in packets)
    total_requirements = sum(safe_int(row.get("first_pass_requirement_rows")) for row in packets)
    rows = [
        {"metric": "priority_download_execution_packet_rows", "value": str(len(packets)), "interpretation": "Dataset-level manual credentialed download execution packets."},
        {"metric": "priority_download_execution_priority_10_wave_rows", "value": str(batch_counts.get("priority_10_wave_batch", 0)), "interpretation": "Phase-1 priority waves covered by execution packets."},
        {"metric": "priority_download_execution_backup_wave_rows", "value": str(batch_counts.get("sixth_country_backup_candidate", 0)), "interpretation": "Sixth-country backup waves covered by execution packets."},
        {"metric": "priority_download_execution_distinct_countries", "value": str(len({row["country"] for row in packets if row.get("country")})), "interpretation": "Distinct countries covered by execution packets."},
        {"metric": "priority_download_execution_core_file_rows", "value": str(len(file_rows)), "interpretation": "Core file/module acceptance rows across execution packets."},
        {"metric": "priority_download_execution_first_pass_requirement_rows", "value": str(total_requirements), "interpretation": "First-pass requirement rows carried into execution packets."},
        {"metric": "priority_download_execution_first_pass_variable_rows", "value": str(total_first_pass), "interpretation": "First-pass selected variable rows carried into execution packets."},
        {"metric": "priority_download_execution_raw_package_received_rows", "value": str(raw_received), "interpretation": "Execution-packet datasets with any original package receipt."},
        {"metric": "priority_download_execution_handoff_readmes_written", "value": str(len([path for path in handoffs if path])), "interpretation": "Per-wave download execution handoff files written."},
        {"metric": "modeling_gate_status", "value": "blocked", "interpretation": "Models remain blocked until raw-backed promotion thresholds and accepted climate linkage pass."},
    ]
    for status, count in sorted(status_counts.items()):
        rows.append({"metric": f"download_execution_status_{status}", "value": str(count), "interpretation": "Dataset download execution status count."})
    for status, count in sorted(file_status_counts.items()):
        rows.append({"metric": f"download_file_acceptance_status_{status}", "value": str(count), "interpretation": "Core file acceptance status count."})
    return rows


def write_report(packets: list[dict[str, str]], file_rows: list[dict[str, str]], summary: list[dict[str, str]]) -> None:
    status_counts = Counter(row["download_execution_status"] for row in packets)
    file_status_counts = Counter(row["file_acceptance_status"] for row in file_rows)
    summary_table = "\n".join(f"| {row['metric']} | {row['value']} | {row['interpretation']} |" for row in summary)
    REPORT_PATH.write_text(
        f"""# Priority Download Execution Packet

Status: manual credentialed-download execution layer for the 13-wave
priority/backup campaign. This packet does not download restricted microdata,
does not bypass account, terms, or Data Access Agreement gates, and does not
promote any data. It gives the exact official route, target folder, core-file
acceptance matrix, and post-download commands needed to move from metadata
candidates to raw-backed promotion review.

## Summary

| Metric | Value | Interpretation |
|---|---:|---|
{summary_table}

## Dataset Status

{markdown_counter(status_counts, 'Download execution status') if packets else 'No packet rows exist.'}

## Core File Acceptance Status

{markdown_counter(file_status_counts, 'Core file status') if file_rows else 'No core file rows exist.'}

## Execution Queue

{markdown_table(packets, ['download_order', 'idno', 'country', 'wave', 'campaign_phase', 'official_get_microdata_url', 'local_target_folder', 'download_execution_status'], 20)}

## Core File Preview

{markdown_table(file_rows, ['download_order', 'idno', 'core_file_rank', 'metadata_file_name', 'expected_local_name_patterns', 'file_acceptance_status'], 40)}

## Post-Download Commands

{chr(10).join(f'- `{command}`' for command in POST_DOWNLOAD_COMMANDS)}

## Machine-Readable Outputs

- `temp/priority_download_execution_packet.csv`
- `temp/priority_download_file_acceptance_matrix.csv`
- `result/priority_download_execution_packet_summary.csv`

## Guardrail

The listed core files are an acceptance matrix, not permission to build an
incomplete dataset. Download and preserve the complete unchanged official
package plus documentation for each wave. `data/` remains closed until all
promotion gates pass.
""",
        encoding="utf-8",
    )


def main() -> None:
    ensure_dirs()
    packets, file_rows, handoffs = build_packets()
    summary = build_summary(packets, file_rows, handoffs)
    write_csv(PACKET_PATH, packets, PACKET_COLUMNS)
    write_csv(FILE_ACCEPTANCE_PATH, file_rows, FILE_COLUMNS)
    write_csv(SUMMARY_PATH, summary, SUMMARY_COLUMNS)
    write_report(packets, file_rows, summary)
    append_log(
        TEMP_DIR / "audit_log.md",
        f"Built priority download execution packet rows={len(packets)} file_acceptance_rows={len(file_rows)}.",
    )
    print(f"Priority download execution packet rows={len(packets)} file_acceptance_rows={len(file_rows)}.")


if __name__ == "__main__":
    main()
