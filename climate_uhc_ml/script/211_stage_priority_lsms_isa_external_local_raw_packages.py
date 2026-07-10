from __future__ import annotations

import argparse
import csv
import shutil
from pathlib import Path
from typing import Any

from common import PROJECT_ROOT, REPORT_DIR, RESULT_DIR, TEMP_DIR, append_log, ensure_dirs, write_csv


INTAKE_DECISION_PATH = RESULT_DIR / "priority_lsms_isa_external_local_raw_intake_decision.csv"
PLAN_PATH = TEMP_DIR / "priority_lsms_isa_external_local_raw_staging_plan.csv"
FILE_MANIFEST_PATH = TEMP_DIR / "priority_lsms_isa_external_local_raw_staging_file_manifest.csv"
SUMMARY_PATH = RESULT_DIR / "priority_lsms_isa_external_local_raw_staging_summary.csv"
REPORT_PATH = REPORT_DIR / "priority_lsms_isa_external_local_raw_staging.md"

EXTERNAL_ALLOWED_ROOT = Path(
    r"D:\GlobalHealthPolicy Dropbox\Fan Bowei\HEALTH EXPENDITURE MEASUREMENT\HEALTH VS CONSUMPTION\Data"
)
TARGET_ROOT = TEMP_DIR / "raw_downloads"

RAW_OR_DOC_SUFFIXES = {
    ".dta",
    ".sav",
    ".por",
    ".sas7bdat",
    ".xpt",
    ".csv",
    ".tsv",
    ".xlsx",
    ".xls",
    ".zip",
    ".tar",
    ".gz",
    ".tgz",
    ".rar",
    ".7z",
    ".pdf",
    ".doc",
    ".docx",
    ".rtf",
    ".txt",
    ".xml",
    ".json",
    ".ddi",
}

PLAN_COLUMNS = [
    "download_priority_order",
    "country",
    "wave",
    "idno",
    "intake_decision",
    "external_candidate_folder",
    "copy_target_folder",
    "source_folder_exists",
    "target_folder_exists_before",
    "target_preexisting_payload_rows",
    "source_file_rows",
    "source_total_bytes",
    "staging_mode",
    "staging_decision",
    "staging_status",
    "post_stage_validation_commands",
    "data_write_gate_status",
    "modeling_gate_status",
]

FILE_COLUMNS = [
    "download_priority_order",
    "country",
    "wave",
    "idno",
    "source_relative_path",
    "source_file_name",
    "source_suffix",
    "source_bytes",
    "target_relative_path",
    "target_exists_before",
    "target_bytes_before",
    "file_staging_action",
    "copy_error",
    "data_write_gate_status",
    "modeling_gate_status",
]

SUMMARY_COLUMNS = ["metric", "value", "interpretation"]


def read_csv_dicts(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def clean(value: Any) -> str:
    if value is None:
        return ""
    return " ".join(str(value).split())


def safe_int(value: Any, default: int = 0) -> int:
    try:
        text = clean(value)
        return int(float(text)) if text else default
    except (TypeError, ValueError):
        return default


def resolve_project_path(path_text: str) -> Path:
    text = clean(path_text).replace("\\", "/").strip("/")
    path = Path(text)
    if path.is_absolute():
        return path
    return PROJECT_ROOT / text


def is_relative_to(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(PROJECT_ROOT)).replace("\\", "/")
    except ValueError:
        return str(path).replace("\\", "/")


def list_files(folder: Path) -> list[Path]:
    if not folder.exists() or not folder.is_dir():
        return []
    return sorted((path for path in folder.rglob("*") if path.is_file()), key=lambda path: str(path).lower())


def payload_files(folder: Path) -> list[Path]:
    return [
        path
        for path in list_files(folder)
        if not path.name.startswith("_") and path.suffix.lower() in RAW_OR_DOC_SUFFIXES
    ]


def validation_commands(idno: str) -> str:
    return (
        "python script/144_build_priority_lsms_isa_raw_package_intake_packet.py; "
        "python script/145_build_priority_lsms_isa_archive_member_preflight.py; "
        "python script/150_build_priority_lsms_isa_raw_package_receipt_checklist.py; "
        "python script/153_validate_priority_lsms_isa_official_file_receipt.py; "
        f"python script/178_build_priority_lsms_isa_post_download_validation_runner.py --idno {idno}"
    )


def selected_rows(idnos: set[str], intake_decisions: set[str]) -> list[dict[str, str]]:
    rows = [
        row
        for row in read_csv_dicts(INTAKE_DECISION_PATH)
        if clean(row.get("intake_decision")) in intake_decisions
    ]
    if idnos:
        rows = [row for row in rows if clean(row.get("idno")) in idnos]
    return rows


def plan_for_row(row: dict[str, str], execute: bool, include_existing_targets: bool) -> tuple[dict[str, str], list[dict[str, str]]]:
    idno = clean(row.get("idno"))
    source = Path(clean(row.get("external_candidate_folder")))
    target = resolve_project_path(clean(row.get("copy_target_folder")))
    source_exists = source.exists() and source.is_dir() and is_relative_to(source, EXTERNAL_ALLOWED_ROOT)
    target_safe = is_relative_to(target, TARGET_ROOT)
    target_exists_before = target.exists()
    existing_payload = payload_files(target) if target_exists_before else []
    source_files = list_files(source) if source_exists else []

    if not source_exists:
        decision = "blocked_source_missing_or_outside_allowed_root"
    elif not target_safe:
        decision = "blocked_target_outside_temp_raw_downloads"
    elif existing_payload and not include_existing_targets:
        decision = "skipped_target_already_has_payload"
    elif execute:
        decision = "execute_copy_to_temp_raw_downloads"
    else:
        decision = "dry_run_would_copy_to_temp_raw_downloads"

    file_rows: list[dict[str, str]] = []
    copied = 0
    blocked = 0
    skipped = 0

    for source_file in source_files:
        source_rel = source_file.relative_to(source)
        target_file = target / source_rel
        exists_before = target_file.exists()
        target_bytes_before = target_file.stat().st_size if exists_before else 0
        action = decision
        error = ""
        if decision == "execute_copy_to_temp_raw_downloads":
            try:
                target_file.parent.mkdir(parents=True, exist_ok=True)
                if exists_before and target_bytes_before == source_file.stat().st_size:
                    action = "skipped_existing_same_size"
                    skipped += 1
                elif exists_before:
                    action = "blocked_destination_exists_size_mismatch"
                    blocked += 1
                else:
                    shutil.copy2(source_file, target_file)
                    action = "copied"
                    copied += 1
            except OSError as exc:
                action = "copy_failed"
                error = " ".join(f"{type(exc).__name__}: {exc}".split())[:300]
                blocked += 1
        elif decision.startswith("blocked"):
            blocked += 1
        else:
            skipped += 1
        file_rows.append(
            {
                "download_priority_order": clean(row.get("download_priority_order")),
                "country": clean(row.get("country")),
                "wave": clean(row.get("wave")),
                "idno": idno,
                "source_relative_path": str(source_rel).replace("\\", "/"),
                "source_file_name": source_file.name,
                "source_suffix": source_file.suffix.lower(),
                "source_bytes": str(source_file.stat().st_size),
                "target_relative_path": rel(target_file),
                "target_exists_before": "1" if exists_before else "0",
                "target_bytes_before": str(target_bytes_before),
                "file_staging_action": action,
                "copy_error": error,
                "data_write_gate_status": "blocked_no_data_write",
                "modeling_gate_status": "blocked",
            }
        )

    if decision == "execute_copy_to_temp_raw_downloads" and blocked == 0:
        status = "executed_copy_complete_provenance_not_accepted"
    elif decision == "execute_copy_to_temp_raw_downloads":
        status = "executed_copy_with_blocked_files_provenance_not_accepted"
    else:
        status = decision

    plan_row = {
        "download_priority_order": clean(row.get("download_priority_order")),
        "country": clean(row.get("country")),
        "wave": clean(row.get("wave")),
        "idno": idno,
        "intake_decision": clean(row.get("intake_decision")),
        "external_candidate_folder": str(source),
        "copy_target_folder": rel(target),
        "source_folder_exists": "1" if source_exists else "0",
        "target_folder_exists_before": "1" if target_exists_before else "0",
        "target_preexisting_payload_rows": str(len(existing_payload)),
        "source_file_rows": str(len(source_files)),
        "source_total_bytes": str(sum(path.stat().st_size for path in source_files)),
        "staging_mode": "execute" if execute else "dry_run",
        "staging_decision": decision,
        "staging_status": status,
        "post_stage_validation_commands": validation_commands(idno),
        "data_write_gate_status": "blocked_no_data_write",
        "modeling_gate_status": "blocked",
    }
    return plan_row, file_rows


def build_summary(plan_rows: list[dict[str, str]], file_rows: list[dict[str, str]], execute: bool) -> list[dict[str, str]]:
    executed_ids = {
        row.get("idno", "")
        for row in plan_rows
        if clean(row.get("staging_status")) == "executed_copy_complete_provenance_not_accepted"
    }
    return [
        {"metric": "external_local_raw_staging_mode", "value": "execute" if execute else "dry_run", "interpretation": "Whether this run copied files or only produced a plan."},
        {"metric": "external_local_raw_staging_plan_rows", "value": str(len(plan_rows)), "interpretation": "Explicitly selected intake-decision rows considered for external local staging."},
        {"metric": "external_local_raw_staging_file_manifest_rows", "value": str(len(file_rows)), "interpretation": "Source files covered by the staging plan or execution manifest."},
        {"metric": "external_local_raw_staging_executed_dataset_rows", "value": str(len(executed_ids)), "interpretation": "Datasets copied into temp/raw_downloads by this run."},
        {"metric": "external_local_raw_staging_copied_file_rows", "value": str(sum(1 for row in file_rows if row.get("file_staging_action") == "copied")), "interpretation": "Files copied into temp/raw_downloads by this run."},
        {"metric": "external_local_raw_staging_skipped_existing_file_rows", "value": str(sum(1 for row in file_rows if row.get("file_staging_action") == "skipped_existing_same_size")), "interpretation": "Destination files already present with the same size."},
        {"metric": "external_local_raw_staging_blocked_file_rows", "value": str(sum(1 for row in file_rows if row.get("file_staging_action", "").startswith("blocked") or row.get("file_staging_action") == "copy_failed")), "interpretation": "Files not copied because of safety or copy errors."},
        {"metric": "external_local_raw_staging_provenance_accepted_rows", "value": "0", "interpretation": "Staging does not accept external local provenance as official receipt."},
        {"metric": "data_write_gate_status", "value": "blocked_no_data_write", "interpretation": "Staging writes only temp/raw_downloads raw files and audit manifests, never clean data."},
        {"metric": "modeling_gate_status", "value": "blocked", "interpretation": "No predictive, reduced-form, causal ML, or policy learning is opened."},
    ]


def markdown_table(rows: list[dict[str, str]], columns: list[str], limit: int = 30) -> str:
    if not rows:
        return "_No rows._"
    lines = ["| " + " | ".join(columns) + " |", "| " + " | ".join("---" for _ in columns) + " |"]
    for row in rows[:limit]:
        values: list[str] = []
        for column in columns:
            value = clean(row.get(column)).replace("|", "/")
            if len(value) > 120:
                value = value[:117] + "..."
            values.append(value)
        lines.append("| " + " | ".join(values) + " |")
    if len(rows) > limit:
        lines.append("| " + " | ".join("..." for _ in columns) + " |")
    return "\n".join(lines)


def write_report(plan_rows: list[dict[str, str]], summary: list[dict[str, str]]) -> None:
    lines = [
        "# Priority LSMS/ISA External Local Raw Staging",
        "",
        "Status: controlled staging plan/execution log for copying external local raw-folder candidates into `temp/raw_downloads/`.",
        "",
        "This script never writes clean `data/`, never accepts official provenance, and never opens modeling. Raw staging is only a prerequisite for the existing receipt, schema, value, and promotion gates.",
        "",
        "## Summary",
        "",
        markdown_table(summary, ["metric", "value", "interpretation"], limit=20),
        "",
        "## Plan",
        "",
        markdown_table(
            plan_rows,
            [
                "country",
                "wave",
                "idno",
                "intake_decision",
                "source_file_rows",
                "source_total_bytes",
                "target_preexisting_payload_rows",
                "staging_status",
            ],
            limit=20,
        ),
        "",
        "## Follow-Up",
        "",
        "After any executed copy, rerun the raw intake, archive/direct-file preflight, receipt checklist, and official-file receipt validator before any schema/value or promotion decision.",
    ]
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true", help="Copy files into temp/raw_downloads. Default is dry-run.")
    parser.add_argument("--idno", action="append", default=[], help="Restrict to one IDNO. Can be repeated.")
    parser.add_argument(
        "--include-intake-decision",
        action="append",
        default=[],
        help=(
            "Include rows with this intake_decision. Can be repeated. "
            "Default: copy_review_ready_pending_official_provenance."
        ),
    )
    parser.add_argument("--include-existing-targets", action="store_true", help="Allow copying into targets that already contain raw/documentation payload files.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    ensure_dirs()
    idnos = {clean(value) for value in args.idno if clean(value)}
    intake_decisions = {clean(value) for value in args.include_intake_decision if clean(value)}
    if not intake_decisions:
        intake_decisions = {"copy_review_ready_pending_official_provenance"}
    plan_rows: list[dict[str, str]] = []
    file_rows: list[dict[str, str]] = []
    for row in selected_rows(idnos, intake_decisions):
        plan_row, row_file_rows = plan_for_row(row, args.execute, args.include_existing_targets)
        plan_rows.append(plan_row)
        file_rows.extend(row_file_rows)
    summary = build_summary(plan_rows, file_rows, args.execute)
    write_csv(PLAN_PATH, plan_rows, PLAN_COLUMNS)
    write_csv(FILE_MANIFEST_PATH, file_rows, FILE_COLUMNS)
    write_csv(SUMMARY_PATH, summary, SUMMARY_COLUMNS)
    write_report(plan_rows, summary)
    append_log(TEMP_DIR / "audit_log.md", f"Built priority LSMS/ISA external local raw staging {'execute' if args.execute else 'dry-run'}: plan_rows={len(plan_rows)} file_rows={len(file_rows)}.")
    print(f"Priority LSMS/ISA external local raw staging mode={'execute' if args.execute else 'dry_run'} plan_rows={len(plan_rows)} file_rows={len(file_rows)}.")


if __name__ == "__main__":
    main()
