from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path
from typing import Any

from common import PROJECT_ROOT, REPORT_DIR, RESULT_DIR, TEMP_DIR, append_log, ensure_dirs, sha256_file, write_csv


QUEUE_PATH = TEMP_DIR / "priority_lsms_isa_refocused_acquisition_queue.csv"
REQUIREMENT_MATRIX_PATH = TEMP_DIR / "priority_lsms_isa_refocused_requirement_matrix.csv"

LEDGER_PATH = TEMP_DIR / "priority_lsms_isa_raw_package_intake_ledger.csv"
FILE_MANIFEST_PATH = TEMP_DIR / "priority_lsms_isa_raw_package_file_manifest.csv"
ACCEPTANCE_MATRIX_PATH = TEMP_DIR / "priority_lsms_isa_raw_package_acceptance_matrix.csv"
SUMMARY_PATH = RESULT_DIR / "priority_lsms_isa_raw_package_intake_summary.csv"
REPORT_PATH = REPORT_DIR / "priority_lsms_isa_raw_package_intake_packet.md"

RAW_ROOT = TEMP_DIR / "raw_downloads"

RAW_TABULAR_EXTENSIONS = {".dta", ".sav", ".por", ".sas7bdat", ".xpt", ".csv", ".tsv", ".txt", ".xlsx", ".xls"}
ARCHIVE_EXTENSIONS = {".zip", ".rar", ".7z", ".tar", ".gz", ".tgz"}
DOCUMENTATION_EXTENSIONS = {".pdf", ".doc", ".docx", ".rtf", ".html", ".htm", ".xml", ".json", ".ddi", ".txt"}
GENERATED_HANDOFF_NAMES = {
    "_PRIORITY_DOWNLOAD_EXECUTION_PACKET.md",
    "_PRIORITY_LSMS_ISA_ALIGNMENT_AUDIT.md",
    "_PRIORITY_LSMS_ISA_REFOCUSED_ACQUISITION.md",
    "_PRIORITY_LSMS_ISA_RAW_PACKAGE_INTAKE.md",
}

POST_INTAKE_COMMANDS = [
    "python script/17_audit_raw_downloads.py",
    "python script/128_build_priority_archive_member_preflight.py",
    "python script/130_build_priority_raw_package_receipt_ledger.py",
    "python script/03_inspect_raw_schemas.py",
    "python script/29_build_raw_variable_verification_protocol.py",
    "python script/33_build_harmonization_recipe_gate.py",
    "python script/126_build_priority_raw_verification_workbook.py",
    "python script/129_build_priority_manual_verification_decision_gate.py",
    "python script/132_build_priority_analysis_dataset_synthesis_blueprint.py",
    "python script/134_build_priority_country_wave_promotion_packets.py",
    "python script/127_enforce_promoted_data_gate.py",
    "python script/36_build_direct_read_audit_bundle.py",
    "python script/14_validate_workspace.py",
]

LEDGER_COLUMNS = [
    "download_priority_order",
    "queue_role",
    "country",
    "wave",
    "idno",
    "survey_name",
    "official_get_microdata_url",
    "local_target_folder",
    "generated_handoff_file_count",
    "original_file_count",
    "archive_file_count",
    "raw_tabular_file_count",
    "documentation_file_count",
    "total_original_bytes",
    "raw_package_status",
    "intake_acceptance_status",
    "minimum_acceptance_rule",
    "next_action",
    "post_intake_commands",
    "handoff_readme",
]

FILE_MANIFEST_COLUMNS = [
    "download_priority_order",
    "country",
    "wave",
    "idno",
    "relative_path",
    "file_name",
    "suffix",
    "bytes",
    "sha256",
    "file_role",
    "generated_or_original",
]

ACCEPTANCE_COLUMNS = [
    "download_priority_order",
    "queue_role",
    "country",
    "wave",
    "idno",
    "requirement",
    "metadata_status",
    "metadata_evidence_excerpt",
    "current_raw_package_status",
    "requirement_acceptance_status",
    "required_evidence",
    "raw_review_action",
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


def folder_for(row: dict[str, str]) -> Path:
    folder = clean(row.get("local_target_folder")).replace("\\", "/").strip("/")
    if folder.startswith("temp/raw_downloads/"):
        return PROJECT_ROOT / folder
    if folder:
        return PROJECT_ROOT / folder
    return RAW_ROOT / clean(row.get("idno"))


def is_generated_handoff(path: Path) -> bool:
    return path.name in GENERATED_HANDOFF_NAMES or (path.name.startswith("_") and path.suffix.lower() == ".md")


def file_role(path: Path) -> str:
    suffix = path.suffix.lower()
    name = path.name.lower()
    if is_generated_handoff(path):
        return "generated_handoff"
    if suffix in ARCHIVE_EXTENSIONS:
        return "official_archive_or_compressed_package_candidate"
    if suffix in RAW_TABULAR_EXTENSIONS:
        if any(token in name for token in ["questionnaire", "codebook", "dictionary", "basic", "manual", "readme"]):
            return "documentation_candidate"
        return "raw_tabular_or_workbook_candidate"
    if suffix in DOCUMENTATION_EXTENSIONS:
        return "documentation_candidate"
    return "original_other_candidate"


def file_manifest_for(row: dict[str, str]) -> list[dict[str, str]]:
    folder = folder_for(row)
    if not folder.exists():
        return []
    out: list[dict[str, str]] = []
    for path in sorted(p for p in folder.rglob("*") if p.is_file()):
        role = file_role(path)
        out.append(
            {
                "download_priority_order": clean(row.get("download_priority_order")),
                "country": clean(row.get("country")),
                "wave": clean(row.get("wave")),
                "idno": clean(row.get("idno")),
                "relative_path": rel(path),
                "file_name": path.name,
                "suffix": path.suffix.lower(),
                "bytes": str(path.stat().st_size),
                "sha256": sha256_file(path) if role != "generated_handoff" else "",
                "file_role": role,
                "generated_or_original": "generated" if role == "generated_handoff" else "original_candidate",
            }
        )
    return out


def raw_status(original_count: int, archive_count: int, tabular_count: int, doc_count: int) -> tuple[str, str, str]:
    if original_count == 0:
        return (
            "not_received_no_original_raw_package",
            "blocked_no_original_package",
            "Place the complete unchanged official raw package and all documentation in the target folder.",
        )
    if archive_count == 0 and tabular_count == 0:
        return (
            "documentation_only_or_unrecognized_original_files",
            "blocked_no_archive_or_raw_tabular_file",
            "Add the official raw archive or raw tabular files, then rerun intake.",
        )
    if doc_count == 0:
        return (
            "raw_payload_present_documentation_missing",
            "blocked_missing_documentation",
            "Add questionnaires, codebooks, basic information documents, and data dictionaries before schema/value review.",
        )
    return (
        "original_package_candidate_present",
        "ready_for_schema_and_manual_value_review",
        "Run the post-intake commands and verify every requirement against raw files and documentation.",
    )


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


def write_handoff(ledger_row: dict[str, str], acceptance_rows: list[dict[str, str]]) -> str:
    folder = folder_for(ledger_row)
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / "_PRIORITY_LSMS_ISA_RAW_PACKAGE_INTAKE.md"
    path.write_text(
        f"""# Priority LSMS-ISA Raw Package Intake

Dataset: `{ledger_row.get('idno', '')}` - {ledger_row.get('country', '')} {ledger_row.get('wave', '')}

Queue role: `{ledger_row.get('queue_role', '')}`

Official get-microdata URL: {ledger_row.get('official_get_microdata_url', '')}

Target folder: `{ledger_row.get('local_target_folder', '')}`

Current intake status: `{ledger_row.get('intake_acceptance_status', '')}`

Original files counted: {ledger_row.get('original_file_count', '0')}

Generated handoff files ignored: {ledger_row.get('generated_handoff_file_count', '0')}

## Minimum Acceptance Rule

{ledger_row.get('minimum_acceptance_rule', '')}

## Requirement Acceptance Snapshot

{markdown_table(acceptance_rows, ['requirement', 'metadata_status', 'requirement_acceptance_status'], 12)}

## Post-Intake Commands

{chr(10).join(f'- `{command}`' for command in POST_INTAKE_COMMANDS)}

## Stop Rule

Do not write this country-wave into `data/` until original package receipt,
schema inspection, manual value/unit/key review, outcome readiness, and
accepted CHIRPS/ERA5 climate linkage all pass.
""",
        encoding="utf-8",
    )
    return rel(path)


def build_ledger_and_files(queue_rows: list[dict[str, str]]) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    ledger: list[dict[str, str]] = []
    manifest: list[dict[str, str]] = []
    for row in queue_rows:
        files = file_manifest_for(row)
        manifest.extend(files)
        generated_count = sum(1 for item in files if item["generated_or_original"] == "generated")
        originals = [item for item in files if item["generated_or_original"] == "original_candidate"]
        archive_count = sum(1 for item in originals if item["file_role"] == "official_archive_or_compressed_package_candidate")
        tabular_count = sum(1 for item in originals if item["file_role"] == "raw_tabular_or_workbook_candidate")
        doc_count = sum(1 for item in originals if item["file_role"] == "documentation_candidate")
        original_bytes = sum(safe_int(item.get("bytes")) for item in originals)
        package_status, acceptance_status, next_action = raw_status(len(originals), archive_count, tabular_count, doc_count)
        ledger.append(
            {
                "download_priority_order": clean(row.get("download_priority_order")),
                "queue_role": clean(row.get("queue_role")),
                "country": clean(row.get("country")),
                "wave": clean(row.get("wave")),
                "idno": clean(row.get("idno")),
                "survey_name": clean(row.get("survey_name")),
                "official_get_microdata_url": clean(row.get("official_get_microdata_url")),
                "local_target_folder": clean(row.get("local_target_folder")),
                "generated_handoff_file_count": str(generated_count),
                "original_file_count": str(len(originals)),
                "archive_file_count": str(archive_count),
                "raw_tabular_file_count": str(tabular_count),
                "documentation_file_count": str(doc_count),
                "total_original_bytes": str(original_bytes),
                "raw_package_status": package_status,
                "intake_acceptance_status": acceptance_status,
                "minimum_acceptance_rule": "Complete unchanged official raw package plus all documentation must be present; generated handoff markdown does not count as raw receipt.",
                "next_action": next_action,
                "post_intake_commands": "; ".join(POST_INTAKE_COMMANDS),
                "handoff_readme": "",
            }
        )
    return ledger, manifest


def build_acceptance_matrix(ledger_rows: list[dict[str, str]], requirement_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    ledger_by_id = {clean(row.get("idno")): row for row in ledger_rows}
    rows: list[dict[str, str]] = []
    for requirement in requirement_rows:
        idno = clean(requirement.get("idno"))
        ledger = ledger_by_id.get(idno, {})
        package_status = clean(ledger.get("raw_package_status")) or "missing_from_intake_ledger"
        if package_status == "original_package_candidate_present":
            req_status = "ready_for_raw_requirement_review"
        else:
            req_status = "blocked_no_original_package"
        rows.append(
            {
                "download_priority_order": clean(requirement.get("download_priority_order")),
                "queue_role": clean(requirement.get("queue_role")),
                "country": clean(requirement.get("country")),
                "wave": clean(requirement.get("wave")),
                "idno": idno,
                "requirement": clean(requirement.get("requirement")),
                "metadata_status": clean(requirement.get("metadata_status")),
                "metadata_evidence_excerpt": clean(requirement.get("metadata_evidence_excerpt")),
                "current_raw_package_status": package_status,
                "requirement_acceptance_status": req_status,
                "required_evidence": "Original raw variables, labels, values, units, recall periods, missing codes, skip patterns, merge keys, and documentation must be reviewed directly.",
                "raw_review_action": clean(requirement.get("raw_review_action")) or "Verify directly in original raw package and documentation.",
            }
        )
    return rows


def build_summary(ledger_rows: list[dict[str, str]], manifest_rows: list[dict[str, str]], acceptance_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    role_counts = Counter(row["queue_role"] for row in ledger_rows)
    status_counts = Counter(row["intake_acceptance_status"] for row in ledger_rows)
    requirement_counts = Counter(row["requirement_acceptance_status"] for row in acceptance_rows)
    generated_count = sum(1 for row in manifest_rows if row["generated_or_original"] == "generated")
    original_count = sum(1 for row in manifest_rows if row["generated_or_original"] == "original_candidate")
    archive_count = sum(1 for row in manifest_rows if row["file_role"] == "official_archive_or_compressed_package_candidate")
    tabular_count = sum(1 for row in manifest_rows if row["file_role"] == "raw_tabular_or_workbook_candidate")
    doc_count = sum(1 for row in manifest_rows if row["file_role"] == "documentation_candidate")
    rows = [
        {"metric": "priority_lsms_raw_intake_dataset_rows", "value": str(len(ledger_rows)), "interpretation": "Refocused LSMS/ISA acquisition targets with raw-package intake ledger rows."},
        {"metric": "priority_lsms_raw_intake_file_manifest_rows", "value": str(len(manifest_rows)), "interpretation": "Files found under target folders, including generated handoffs and original candidates."},
        {"metric": "priority_lsms_raw_intake_generated_handoff_files", "value": str(generated_count), "interpretation": "Generated markdown handoffs ignored as raw receipt evidence."},
        {"metric": "priority_lsms_raw_intake_original_file_rows", "value": str(original_count), "interpretation": "Non-generated candidate original files found in refocused target folders."},
        {"metric": "priority_lsms_raw_intake_archive_file_rows", "value": str(archive_count), "interpretation": "Archive/compressed package candidates found."},
        {"metric": "priority_lsms_raw_intake_raw_tabular_file_rows", "value": str(tabular_count), "interpretation": "Raw tabular/workbook candidates found."},
        {"metric": "priority_lsms_raw_intake_documentation_file_rows", "value": str(doc_count), "interpretation": "Documentation candidates found."},
        {"metric": "priority_lsms_raw_intake_missing_package_rows", "value": str(sum(1 for row in ledger_rows if row["original_file_count"] == "0")), "interpretation": "Targets with no original package or documentation files yet."},
        {"metric": "priority_lsms_raw_intake_acceptance_requirement_rows", "value": str(len(acceptance_rows)), "interpretation": "Requirement rows carried into raw-package acceptance matrix."},
        {"metric": "priority_lsms_raw_intake_blocked_requirement_rows", "value": str(requirement_counts.get("blocked_no_original_package", 0)), "interpretation": "Requirement rows blocked because no original package is present."},
        {"metric": "priority_lsms_raw_intake_handoff_readmes_written", "value": str(sum(1 for row in ledger_rows if row.get("handoff_readme"))), "interpretation": "Per-target raw-package intake handoff files written."},
        {"metric": "priority_lsms_raw_intake_data_write_status", "value": "blocked_no_promoted_rows", "interpretation": "No country-wave may write to data/ from this intake packet."},
        {"metric": "modeling_gate_status", "value": "blocked", "interpretation": "Models remain blocked until raw-backed promotion thresholds and accepted climate linkage pass."},
    ]
    for role, count in sorted(role_counts.items()):
        rows.append({"metric": f"priority_lsms_raw_intake_queue_role_{role}", "value": str(count), "interpretation": "Raw-package intake row count by refocused queue role."})
    for state, count in sorted(status_counts.items()):
        rows.append({"metric": f"priority_lsms_raw_intake_status_{state}", "value": str(count), "interpretation": "Raw-package intake acceptance status count."})
    return rows


def write_report(ledger_rows: list[dict[str, str]], manifest_rows: list[dict[str, str]], acceptance_rows: list[dict[str, str]], summary_rows: list[dict[str, str]]) -> None:
    missing = [row for row in ledger_rows if row["intake_acceptance_status"] != "ready_for_schema_and_manual_value_review"]
    summary_table = "\n".join(f"| {row['metric']} | {row['value']} | {row['interpretation']} |" for row in summary_rows)
    REPORT_PATH.write_text(
        f"""# Priority LSMS-ISA Raw Package Intake Packet

Status: refocused LSMS/ISA manual-download intake gate. This packet tells where
each complete official raw package should be placed, scans the target folders,
and separates generated handoff files from actual original raw/documentation
receipt evidence.

## Summary

| Metric | Value | Interpretation |
|---|---:|---|
{summary_table}

## Current Intake Queue

{markdown_table(ledger_rows, ['download_priority_order', 'queue_role', 'country', 'wave', 'idno', 'original_file_count', 'archive_file_count', 'raw_tabular_file_count', 'documentation_file_count', 'intake_acceptance_status'], 25)}

## Blocked Targets

{markdown_table(missing, ['download_priority_order', 'country', 'idno', 'local_target_folder', 'intake_acceptance_status', 'next_action'], 25) if missing else 'No blocked targets were found.'}

## File Manifest Status

Generated handoff files are useful instructions but do not count as raw receipt.
Current file manifest rows: {len(manifest_rows)}.

## Machine-Readable Outputs

- `temp/priority_lsms_isa_raw_package_intake_ledger.csv`
- `temp/priority_lsms_isa_raw_package_file_manifest.csv`
- `temp/priority_lsms_isa_raw_package_acceptance_matrix.csv`
- `result/priority_lsms_isa_raw_package_intake_summary.csv`

## Guardrail

This intake packet does not download restricted microdata, does not bypass
credentialed World Bank access, and does not write any promoted data. `data/`
remains closed until all raw, outcome, and climate-linkage gates pass.
""",
        encoding="utf-8",
    )


def main() -> None:
    ensure_dirs()
    queue_rows = read_csv_dicts(QUEUE_PATH)
    requirement_rows = read_csv_dicts(REQUIREMENT_MATRIX_PATH)
    ledger_rows, manifest_rows = build_ledger_and_files(queue_rows)
    acceptance_rows = build_acceptance_matrix(ledger_rows, requirement_rows)
    by_id: dict[str, list[dict[str, str]]] = {}
    for row in acceptance_rows:
        by_id.setdefault(clean(row.get("idno")), []).append(row)
    for row in ledger_rows:
        row["handoff_readme"] = write_handoff(row, by_id.get(clean(row.get("idno")), []))
    summary_rows = build_summary(ledger_rows, manifest_rows, acceptance_rows)
    write_csv(LEDGER_PATH, ledger_rows, LEDGER_COLUMNS)
    write_csv(FILE_MANIFEST_PATH, manifest_rows, FILE_MANIFEST_COLUMNS)
    write_csv(ACCEPTANCE_MATRIX_PATH, acceptance_rows, ACCEPTANCE_COLUMNS)
    write_csv(SUMMARY_PATH, summary_rows, SUMMARY_COLUMNS)
    write_report(ledger_rows, manifest_rows, acceptance_rows, summary_rows)
    append_log(
        TEMP_DIR / "audit_log.md",
        f"Built priority LSMS-ISA raw package intake packet ledger_rows={len(ledger_rows)} acceptance_rows={len(acceptance_rows)} original_files={sum(1 for row in manifest_rows if row['generated_or_original'] == 'original_candidate')}.",
    )
    print(f"Priority LSMS-ISA raw package intake ledger rows={len(ledger_rows)} acceptance_rows={len(acceptance_rows)}.")


if __name__ == "__main__":
    main()
