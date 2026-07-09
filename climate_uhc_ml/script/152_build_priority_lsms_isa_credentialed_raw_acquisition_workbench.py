from __future__ import annotations

import csv
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from common import PROJECT_ROOT, REPORT_DIR, RESULT_DIR, TEMP_DIR, append_log, ensure_dirs, write_csv


QUEUE_PATH = TEMP_DIR / "priority_lsms_isa_refocused_acquisition_queue.csv"
DOC_DATASET_PATH = TEMP_DIR / "priority_lsms_isa_public_documentation_dataset_receipt.csv"
FILE_INVENTORY_PATH = TEMP_DIR / "priority_lsms_isa_public_documentation_file_inventory.csv"
FILE_SHORTLIST_PATH = TEMP_DIR / "priority_lsms_isa_concept_file_shortlist.csv"
REQUIREMENT_COVERAGE_PATH = TEMP_DIR / "priority_lsms_isa_requirement_variable_coverage.csv"
RECEIPT_PATH = TEMP_DIR / "priority_lsms_isa_raw_package_receipt_checklist.csv"

WORKBENCH_PATH = TEMP_DIR / "priority_lsms_isa_credentialed_raw_acquisition_workbench.csv"
FULL_FILE_MANIFEST_PATH = TEMP_DIR / "priority_lsms_isa_credentialed_raw_full_file_manifest.csv"
CORE_FILE_CHECKLIST_PATH = TEMP_DIR / "priority_lsms_isa_credentialed_raw_core_file_checklist.csv"
SUMMARY_PATH = RESULT_DIR / "priority_lsms_isa_credentialed_raw_acquisition_workbench_summary.csv"
REPORT_PATH = REPORT_DIR / "priority_lsms_isa_credentialed_raw_acquisition_workbench.md"

RAW_ROOT = TEMP_DIR / "raw_downloads"

POST_DOWNLOAD_COMMANDS = (
    "python script/17_audit_raw_downloads.py; "
    "python script/144_build_priority_lsms_isa_raw_package_intake_packet.py; "
    "python script/145_build_priority_lsms_isa_archive_member_preflight.py; "
    "python script/149_build_priority_lsms_isa_raw_value_verification_workbook.py; "
    "python script/150_build_priority_lsms_isa_raw_package_receipt_checklist.py; "
    "python script/152_build_priority_lsms_isa_credentialed_raw_acquisition_workbench.py; "
    "python script/153_validate_priority_lsms_isa_official_file_receipt.py; "
    "python script/154_build_priority_lsms_isa_threshold_download_sequence.py; "
    "python script/132_build_priority_analysis_dataset_synthesis_blueprint.py; "
    "python script/148_build_priority_lsms_isa_country_wave_promotion_packets.py; "
    "python script/151_refresh_refocused_promoted_country_wave_registry.py; "
    "python script/127_enforce_promoted_data_gate.py; "
    "python script/36_build_direct_read_audit_bundle.py; "
    "python script/14_validate_workspace.py"
)

DOWNLOAD_SCOPE = (
    "Download the complete unchanged official World Bank package for this IDNO, "
    "including all raw microdata files, archives, documentation, questionnaires, "
    "codebooks, DDI/XML, and geography/timing supplements exposed after login."
)

WORKBENCH_COLUMNS = [
    "download_priority_order",
    "queue_role",
    "country",
    "wave",
    "idno",
    "catalog_id",
    "survey_name",
    "official_get_microdata_url",
    "register_url",
    "terms_url",
    "local_target_folder",
    "official_full_file_rows",
    "core_file_checklist_rows",
    "requirement_rows",
    "priority_core_file_names",
    "public_documentation_status",
    "access_gate_detected",
    "current_receipt_status",
    "current_original_file_count",
    "current_archive_file_count",
    "current_raw_tabular_file_count",
    "current_documentation_file_count",
    "download_scope",
    "credentialed_acquisition_status",
    "next_manual_action",
    "post_download_validation_commands",
    "handoff_readme",
]

FULL_FILE_COLUMNS = [
    "download_priority_order",
    "queue_role",
    "country",
    "wave",
    "idno",
    "catalog_id",
    "file_id",
    "file_name",
    "file_description",
    "case_quantity",
    "variable_quantity",
    "source_saved_path",
    "priority_core_target",
    "current_receipt_status",
    "post_download_review_action",
]

CORE_FILE_COLUMNS = [
    "download_priority_order",
    "queue_role",
    "country",
    "wave",
    "idno",
    "requirement",
    "file_rank",
    "file_id",
    "file_name",
    "file_description",
    "candidate_variable_rows",
    "strong_candidate_variable_rows",
    "top_variable_names",
    "current_receipt_status",
    "post_download_verification",
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


def compact(values: list[str], limit: int = 12) -> str:
    seen: set[str] = set()
    out: list[str] = []
    for value in values:
        text = " ".join(clean(value).split())
        if text and text not in seen:
            out.append(text)
            seen.add(text)
        if len(out) >= limit:
            break
    return ";".join(out)


def raw_folder_path(folder: str, idno: str) -> Path:
    folder_clean = clean(folder).replace("\\", "/").strip("/")
    if folder_clean:
        return PROJECT_ROOT / folder_clean
    return RAW_ROOT / idno


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


def build_full_manifest(
    inventory_rows: list[dict[str, str]],
    receipt_by_id: dict[str, dict[str, str]],
    core_file_keys: set[tuple[str, str]],
) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for row in inventory_rows:
        idno = clean(row.get("idno"))
        receipt = receipt_by_id.get(idno, {})
        file_name = clean(row.get("file_name"))
        rows.append(
            {
                "download_priority_order": clean(row.get("download_priority_order")),
                "queue_role": clean(row.get("queue_role")),
                "country": clean(row.get("country")),
                "wave": clean(row.get("wave")),
                "idno": idno,
                "catalog_id": clean(row.get("catalog_id")),
                "file_id": clean(row.get("file_id")),
                "file_name": file_name,
                "file_description": clean(row.get("file_description")),
                "case_quantity": clean(row.get("case_quantity")),
                "variable_quantity": clean(row.get("variable_quantity")),
                "source_saved_path": clean(row.get("source_saved_path")),
                "priority_core_target": "1" if (idno, file_name) in core_file_keys else "0",
                "current_receipt_status": clean(receipt.get("current_receipt_status")) or "missing",
                "post_download_review_action": "Confirm this file or its archive member is present after the complete official package is placed locally.",
            }
        )
    return rows


def build_core_rows(shortlist_rows: list[dict[str, str]], receipt_by_id: dict[str, dict[str, str]]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for row in shortlist_rows:
        idno = clean(row.get("idno"))
        receipt = receipt_by_id.get(idno, {})
        rows.append(
            {
                "download_priority_order": clean(row.get("download_priority_order")),
                "queue_role": clean(row.get("queue_role")),
                "country": clean(row.get("country")),
                "wave": clean(row.get("wave")),
                "idno": idno,
                "requirement": clean(row.get("requirement")),
                "file_rank": clean(row.get("file_rank")),
                "file_id": clean(row.get("file_id")),
                "file_name": clean(row.get("file_name")),
                "file_description": clean(row.get("file_description")),
                "candidate_variable_rows": clean(row.get("candidate_variable_rows")),
                "strong_candidate_variable_rows": clean(row.get("strong_candidate_variable_rows")),
                "top_variable_names": clean(row.get("top_variable_names")),
                "current_receipt_status": clean(receipt.get("current_receipt_status")) or "missing",
                "post_download_verification": "After receipt, verify raw values, labels, units, recall periods, missing codes, skip patterns, and merge level for this requirement/file.",
            }
        )
    return rows


def write_handoff(row: dict[str, str], core_rows: list[dict[str, str]], full_rows: list[dict[str, str]]) -> str:
    idno = row.get("idno", "")
    folder = raw_folder_path(row.get("local_target_folder", ""), idno)
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / "_PRIORITY_LSMS_ISA_CREDENTIALED_RAW_ACQUISITION_WORKBENCH.md"
    path.write_text(
        f"""# Priority LSMS-ISA Credentialed Raw Acquisition Workbench

Dataset: `{idno}` - {row.get('country', '')} {row.get('wave', '')}

Official get-microdata URL: {row.get('official_get_microdata_url', '')}

Target folder: `{row.get('local_target_folder', '')}`

Current receipt status: `{row.get('current_receipt_status', '')}`

## Manual Download Action

{row.get('next_manual_action', '')}

Scope: {DOWNLOAD_SCOPE}

## Core Files To Confirm After Download

{markdown_table(core_rows, ['requirement', 'file_rank', 'file_name', 'candidate_variable_rows', 'top_variable_names'], 20)}

## Official File Manifest Preview

{markdown_table(full_rows, ['file_id', 'file_name', 'file_description', 'case_quantity', 'variable_quantity', 'priority_core_target'], 20)}

## After Placing Files

Run:

`{POST_DOWNLOAD_COMMANDS}`

## Stop Rule

Do not mark receipt, raw-value verification, climate linkage, or analysis
readiness as passed until the complete official package is present and the raw
value workbook evidence fields are filled from original files.
""",
        encoding="utf-8",
    )
    return rel(path)


def build_workbench(
    queue_rows: list[dict[str, str]],
    doc_by_id: dict[str, dict[str, str]],
    receipt_by_id: dict[str, dict[str, str]],
    inventory_by_id: dict[str, list[dict[str, str]]],
    core_by_id: dict[str, list[dict[str, str]]],
    requirement_by_id: dict[str, list[dict[str, str]]],
) -> tuple[list[dict[str, str]], int]:
    rows: list[dict[str, str]] = []
    handoff_count = 0
    for wave in queue_rows:
        idno = clean(wave.get("idno"))
        doc = doc_by_id.get(idno, {})
        receipt = receipt_by_id.get(idno, {})
        core_rows = core_by_id.get(idno, [])
        full_rows = inventory_by_id.get(idno, [])
        core_names = compact([row.get("file_name", "") for row in core_rows], 16)
        status_value = "ready_for_credentialed_manual_download" if clean(doc.get("public_documentation_receipt_status")).startswith("complete") else "blocked_public_documentation_incomplete"
        next_action = (
            "Open official_get_microdata_url, log in or register if required, accept official terms/Data Access Agreement, "
            "download the complete unchanged raw package plus all documentation, and place all files in local_target_folder."
        )
        row = {
            "download_priority_order": clean(wave.get("download_priority_order")),
            "queue_role": clean(wave.get("queue_role")),
            "country": clean(wave.get("country")),
            "wave": clean(wave.get("wave")),
            "idno": idno,
            "catalog_id": clean(doc.get("catalog_id")),
            "survey_name": clean(wave.get("survey_name")),
            "official_get_microdata_url": clean(wave.get("official_get_microdata_url")),
            "register_url": "https://microdata.worldbank.org/auth/register",
            "terms_url": "https://microdata.worldbank.org/terms-of-use",
            "local_target_folder": clean(wave.get("local_target_folder")),
            "official_full_file_rows": str(len(full_rows)),
            "core_file_checklist_rows": str(len(core_rows)),
            "requirement_rows": str(len(requirement_by_id.get(idno, []))),
            "priority_core_file_names": core_names,
            "public_documentation_status": clean(doc.get("public_documentation_receipt_status")) or "missing",
            "access_gate_detected": clean(doc.get("access_gate_detected")) or "missing",
            "current_receipt_status": clean(receipt.get("current_receipt_status")) or "missing",
            "current_original_file_count": clean(receipt.get("current_original_file_count")) or "0",
            "current_archive_file_count": clean(receipt.get("current_archive_file_count")) or "0",
            "current_raw_tabular_file_count": clean(receipt.get("current_raw_tabular_file_count")) or "0",
            "current_documentation_file_count": clean(receipt.get("current_documentation_file_count")) or "0",
            "download_scope": DOWNLOAD_SCOPE,
            "credentialed_acquisition_status": status_value,
            "next_manual_action": next_action,
            "post_download_validation_commands": POST_DOWNLOAD_COMMANDS,
            "handoff_readme": "",
        }
        row["handoff_readme"] = write_handoff(row, core_rows, full_rows)
        handoff_count += 1
        rows.append(row)
    return rows, handoff_count


def build_summary(
    workbench_rows: list[dict[str, str]],
    full_rows: list[dict[str, str]],
    core_rows: list[dict[str, str]],
    handoff_count: int,
) -> list[dict[str, str]]:
    status_counts = Counter(row.get("credentialed_acquisition_status", "") for row in workbench_rows)
    role_counts = Counter(row.get("queue_role", "") for row in workbench_rows)
    package_received = sum(1 for row in workbench_rows if safe_int(row.get("current_original_file_count")) > 0)
    rows = [
        {"metric": "priority_lsms_credentialed_workbench_dataset_rows", "value": str(len(workbench_rows)), "interpretation": "Refocused LSMS/ISA datasets covered by credentialed acquisition workbench."},
        {"metric": "priority_lsms_credentialed_workbench_full_file_rows", "value": str(len(full_rows)), "interpretation": "Official DDI file-description rows carried into full-file download review."},
        {"metric": "priority_lsms_credentialed_workbench_core_file_rows", "value": str(len(core_rows)), "interpretation": "Requirement/file rows to confirm after official raw download."},
        {"metric": "priority_lsms_credentialed_workbench_access_gate_rows", "value": str(sum(1 for row in workbench_rows if row.get("access_gate_detected") == "1")), "interpretation": "Datasets whose get-microdata page shows account, registration, terms, or request language."},
        {"metric": "priority_lsms_credentialed_workbench_package_received_rows", "value": str(package_received), "interpretation": "Datasets with at least one original non-generated package or documentation file already present."},
        {"metric": "priority_lsms_credentialed_workbench_targets_missing_before_download", "value": str(sum(safe_int(row.get("core_file_checklist_rows")) for row in workbench_rows if safe_int(row.get("current_original_file_count")) == 0)), "interpretation": "Core requirement/file rows still missing before credentialed download."},
        {"metric": "priority_lsms_credentialed_workbench_handoff_readmes_written", "value": str(handoff_count), "interpretation": "Per-wave credentialed acquisition workbench handoffs written."},
        {"metric": "priority_lsms_credentialed_workbench_data_write_status", "value": "blocked_no_promoted_rows", "interpretation": "Credentialed acquisition workbench does not permit data/ writes."},
        {"metric": "modeling_gate_status", "value": "blocked", "interpretation": "Models remain blocked until raw-backed promotion thresholds and accepted climate linkage pass."},
    ]
    for role, count in sorted(role_counts.items()):
        rows.append({"metric": f"priority_lsms_credentialed_workbench_queue_role_{role}", "value": str(count), "interpretation": "Dataset count by refocused queue role."})
    for status, count in sorted(status_counts.items()):
        rows.append({"metric": f"priority_lsms_credentialed_workbench_status_{status}", "value": str(count), "interpretation": "Credentialed acquisition status count."})
    return rows


def write_report(
    workbench_rows: list[dict[str, str]],
    full_rows: list[dict[str, str]],
    core_rows: list[dict[str, str]],
    summary_rows: list[dict[str, str]],
) -> None:
    summary_table = "\n".join(f"| {row['metric']} | {row['value']} | {row['interpretation']} |" for row in summary_rows)
    REPORT_PATH.write_text(
        f"""# Priority LSMS-ISA Credentialed Raw Acquisition Workbench

Status: 19-wave credentialed acquisition workbench for the refocused LSMS/ISA
promotion queue. It translates public official metadata into the manual login
download package, full-file manifest, core-file confirmation checklist, and
post-download validation commands.

This workbench does not bypass account, registration, terms, or request gates
and does not treat metadata as raw data.

## Summary

| Metric | Value | Interpretation |
|---|---:|---|
{summary_table}

## Dataset Workbench Preview

{markdown_table(workbench_rows, ['download_priority_order', 'idno', 'country', 'wave', 'official_full_file_rows', 'core_file_checklist_rows', 'current_receipt_status', 'credentialed_acquisition_status'], 30)}

## Core File Checklist Preview

{markdown_table(core_rows, ['download_priority_order', 'idno', 'requirement', 'file_rank', 'file_name', 'candidate_variable_rows', 'current_receipt_status'], 80)}

## Full Official File Manifest Preview

{markdown_table(full_rows, ['download_priority_order', 'idno', 'file_id', 'file_name', 'file_description', 'priority_core_target'], 80)}

## Machine-Readable Outputs

- `temp/priority_lsms_isa_credentialed_raw_acquisition_workbench.csv`
- `temp/priority_lsms_isa_credentialed_raw_full_file_manifest.csv`
- `temp/priority_lsms_isa_credentialed_raw_core_file_checklist.csv`
- `result/priority_lsms_isa_credentialed_raw_acquisition_workbench_summary.csv`

## Guardrails

- Complete official package receipt is required before raw-value verification.
- Generated markdown handoffs and public DDI metadata do not count as raw packages.
- No row may be promoted into `data/` until registry and climate-linkage gates pass.
""",
        encoding="utf-8",
    )


def main() -> None:
    ensure_dirs()
    queue_rows = read_csv_dicts(QUEUE_PATH)
    doc_by_id = one_by_id(read_csv_dicts(DOC_DATASET_PATH))
    receipt_by_id = one_by_id(read_csv_dicts(RECEIPT_PATH))
    inventory_rows = read_csv_dicts(FILE_INVENTORY_PATH)
    core_rows = build_core_rows(read_csv_dicts(FILE_SHORTLIST_PATH), receipt_by_id)
    requirement_by_id = by_id(read_csv_dicts(REQUIREMENT_COVERAGE_PATH))
    core_keys = {(row.get("idno", ""), row.get("file_name", "")) for row in core_rows}
    full_rows = build_full_manifest(inventory_rows, receipt_by_id, core_keys)
    workbench_rows, handoff_count = build_workbench(
        queue_rows,
        doc_by_id,
        receipt_by_id,
        by_id(full_rows),
        by_id(core_rows),
        requirement_by_id,
    )
    summary_rows = build_summary(workbench_rows, full_rows, core_rows, handoff_count)

    write_csv(WORKBENCH_PATH, workbench_rows, WORKBENCH_COLUMNS)
    write_csv(FULL_FILE_MANIFEST_PATH, full_rows, FULL_FILE_COLUMNS)
    write_csv(CORE_FILE_CHECKLIST_PATH, core_rows, CORE_FILE_COLUMNS)
    write_csv(SUMMARY_PATH, summary_rows, SUMMARY_COLUMNS)
    write_report(workbench_rows, full_rows, core_rows, summary_rows)
    append_log(
        TEMP_DIR / "audit_log.md",
        f"Built priority LSMS/ISA credentialed raw acquisition workbench datasets={len(workbench_rows)} core_files={len(core_rows)}.",
    )
    print(
        "Priority LSMS/ISA credentialed raw acquisition workbench "
        f"datasets={len(workbench_rows)} full_files={len(full_rows)} core_files={len(core_rows)}."
    )


if __name__ == "__main__":
    main()
