from __future__ import annotations

import csv
import tarfile
import zipfile
from pathlib import Path, PurePosixPath
from typing import Any

from common import PROJECT_ROOT, REPORT_DIR, RESULT_DIR, TEMP_DIR, append_log, ensure_dirs, write_csv


BOARD_PATH = TEMP_DIR / "priority_lsms_isa_manual_download_execution_board.csv"
ACCEPTANCE_FILE_MATRIX_PATH = TEMP_DIR / "priority_lsms_isa_download_acceptance_file_matrix.csv"

STATUS_PATH = TEMP_DIR / "priority_lsms_isa_target_folder_receipt_status.csv"
FILE_INVENTORY_PATH = TEMP_DIR / "priority_lsms_isa_target_folder_receipt_file_inventory.csv"
SUMMARY_PATH = RESULT_DIR / "priority_lsms_isa_target_folder_receipt_smoke_test_summary.csv"
REPORT_PATH = REPORT_DIR / "priority_lsms_isa_target_folder_receipt_smoke_test.md"

ARCHIVE_SUFFIXES = {".zip", ".tar", ".tgz", ".gz"}
UNSUPPORTED_ARCHIVE_SUFFIXES = {".rar", ".7z"}
DIRECT_DATA_SUFFIXES = {".dta", ".sav", ".por", ".sas7bdat", ".xpt", ".csv", ".tsv", ".xlsx", ".xls"}
DATA_OR_ARCHIVE_SUFFIXES = DIRECT_DATA_SUFFIXES | ARCHIVE_SUFFIXES | UNSUPPORTED_ARCHIVE_SUFFIXES
DOCUMENTATION_SUFFIXES = {".pdf", ".doc", ".docx", ".html", ".htm", ".txt", ".rtf", ".xml", ".json"}

POST_RECEIPT_COMMANDS = (
    "python script/150_build_priority_lsms_isa_raw_package_receipt_checklist.py; "
    "python script/153_validate_priority_lsms_isa_official_file_receipt.py; "
    "python script/157_build_priority_lsms_isa_received_raw_schema_audit.py; "
    "python script/158_build_priority_lsms_isa_received_raw_value_profile.py; "
    "python script/159_build_priority_lsms_isa_received_raw_semantics_review.py; "
    "python script/148_build_priority_lsms_isa_country_wave_promotion_packets.py; "
    "python script/151_refresh_refocused_promoted_country_wave_registry.py; "
    "python script/173_build_priority_lsms_isa_promotion_gate_dashboard.py; "
    "python script/36_build_direct_read_audit_bundle.py; "
    "python script/14_validate_workspace.py"
)

STATUS_COLUMNS = [
    "download_rank",
    "country",
    "wave",
    "idno",
    "official_get_microdata_url",
    "local_target_folder",
    "target_folder_exists",
    "target_file_rows",
    "placeholder_instruction_rows",
    "candidate_raw_file_rows",
    "candidate_documentation_file_rows",
    "candidate_unknown_file_rows",
    "candidate_archive_rows",
    "candidate_direct_data_rows",
    "candidate_raw_total_bytes",
    "expected_full_file_rows",
    "expected_core_file_rows",
    "expected_file_name_matches",
    "expected_core_file_name_matches",
    "matched_expected_file_names",
    "matched_core_file_names",
    "receipt_smoke_status",
    "next_validation_action",
    "data_write_gate_status",
    "modeling_gate_status",
]

FILE_COLUMNS = [
    "download_rank",
    "country",
    "wave",
    "idno",
    "local_target_folder",
    "target_relative_path",
    "file_name",
    "file_extension",
    "file_bytes",
    "file_kind",
    "archive_read_status",
    "archive_member_count",
    "expected_file_name_matches",
    "expected_core_file_name_matches",
    "matched_expected_file_names",
    "matched_core_file_names",
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


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(PROJECT_ROOT)).replace("\\", "/")
    except ValueError:
        return str(path).replace("\\", "/")


def resolve_project_path(path_text: str) -> Path:
    text = clean(path_text).replace("\\", "/").strip("/")
    path = Path(text)
    if path.is_absolute():
        return path
    return PROJECT_ROOT / text


def file_key(value: str) -> str:
    text = clean(value).replace("\\", "/")
    if not text:
        return ""
    key = PurePosixPath(text).name.lower()
    if key.endswith(".nsdstat"):
        return key[: -len(".nsdstat")] + ".dta"
    return key


def key_variants(value: str) -> set[str]:
    key = file_key(value)
    if not key:
        return set()
    variants = {key}
    suffix = PurePosixPath(key).suffix
    if suffix:
        variants.add(key[: -len(suffix)])
    return variants


def unique_join(values: list[str], limit: int = 16) -> str:
    seen: list[str] = []
    for value in values:
        text = clean(value)
        if text and text not in seen:
            seen.append(text)
    if len(seen) > limit:
        return ";".join(seen[:limit] + [f"...{len(seen) - limit} more"])
    return ";".join(seen)


def rows_by_id(rows: list[dict[str, str]]) -> dict[str, list[dict[str, str]]]:
    grouped: dict[str, list[dict[str, str]]] = {}
    for row in rows:
        idno = clean(row.get("idno"))
        if idno:
            grouped.setdefault(idno, []).append(row)
    return grouped


def classify_file(path: Path) -> str:
    name = path.name
    suffix = path.suffix.lower()
    if name.startswith("_") or suffix == ".md":
        return "placeholder_or_instruction"
    if suffix in DATA_OR_ARCHIVE_SUFFIXES:
        return "candidate_raw_data_or_archive"
    if suffix in DOCUMENTATION_SUFFIXES:
        return "candidate_documentation"
    return "candidate_unknown"


def list_target_files(target_folder: Path) -> list[Path]:
    if not target_folder.exists():
        return []
    return sorted((path for path in target_folder.rglob("*") if path.is_file()), key=lambda p: rel(p).lower())


def archive_member_names(path: Path) -> tuple[str, list[str]]:
    suffix = path.suffix.lower()
    if suffix == ".zip":
        try:
            with zipfile.ZipFile(path) as zf:
                return "readable_zip", [name for name in zf.namelist() if not name.endswith("/")]
        except (OSError, zipfile.BadZipFile):
            return "unreadable_zip", []
    if suffix in {".tar", ".tgz", ".gz"}:
        try:
            with tarfile.open(path) as tf:
                return "readable_tar", [member.name for member in tf.getmembers() if member.isfile()]
        except (OSError, tarfile.TarError):
            return "unreadable_tar_or_plain_gzip", []
    if suffix in UNSUPPORTED_ARCHIVE_SUFFIXES:
        return "unsupported_archive_type", []
    return "not_archive", []


def expected_name_sets(file_rows: list[dict[str, str]]) -> tuple[dict[str, str], dict[str, str]]:
    all_expected: dict[str, str] = {}
    core_expected: dict[str, str] = {}
    for row in file_rows:
        expected = clean(row.get("expected_file_name"))
        if not expected:
            continue
        for key in key_variants(expected):
            all_expected.setdefault(key, expected)
            if clean(row.get("priority_core_target")) == "1":
                core_expected.setdefault(key, expected)
    return all_expected, core_expected


def match_expected_names(actual_names: list[str], expected_lookup: dict[str, str]) -> list[str]:
    matches: list[str] = []
    for actual in actual_names:
        for key in key_variants(actual):
            expected = expected_lookup.get(key)
            if expected and expected not in matches:
                matches.append(expected)
    return matches


def file_inventory_row(
    board_row: dict[str, str],
    path: Path,
    target_folder: Path,
    expected_lookup: dict[str, str],
    core_lookup: dict[str, str],
) -> dict[str, str]:
    kind = classify_file(path)
    archive_status, members = archive_member_names(path) if kind == "candidate_raw_data_or_archive" else ("not_applicable", [])
    actual_names = [path.name] + members
    expected_matches = match_expected_names(actual_names, expected_lookup)
    core_matches = match_expected_names(actual_names, core_lookup)
    try:
        target_rel = str(path.relative_to(target_folder)).replace("\\", "/")
    except ValueError:
        target_rel = path.name
    return {
        "download_rank": clean(board_row.get("download_rank")),
        "country": clean(board_row.get("country")),
        "wave": clean(board_row.get("wave")),
        "idno": clean(board_row.get("idno")),
        "local_target_folder": clean(board_row.get("local_target_folder")),
        "target_relative_path": target_rel,
        "file_name": path.name,
        "file_extension": path.suffix.lower(),
        "file_bytes": str(path.stat().st_size),
        "file_kind": kind,
        "archive_read_status": archive_status,
        "archive_member_count": str(len(members)),
        "expected_file_name_matches": str(len(expected_matches)),
        "expected_core_file_name_matches": str(len(core_matches)),
        "matched_expected_file_names": unique_join(expected_matches),
        "matched_core_file_names": unique_join(core_matches),
        "data_write_gate_status": "blocked_no_data_write",
        "modeling_gate_status": "blocked",
    }


def receipt_status(raw_rows: list[dict[str, str]], doc_rows: list[dict[str, str]], expected_matches: int, core_matches: int) -> str:
    if not raw_rows and not doc_rows:
        return "blocked_no_candidate_raw_or_documentation_files"
    if not raw_rows:
        return "blocked_documentation_only_no_candidate_raw_files"
    if any(row.get("archive_read_status", "").startswith("unreadable") for row in raw_rows):
        return "manual_review_unreadable_archive_candidate"
    if expected_matches > 0 or core_matches > 0:
        return "ready_for_official_receipt_validation"
    return "manual_review_candidate_raw_present_no_expected_name_match"


def next_action(status_value: str) -> str:
    if status_value == "ready_for_official_receipt_validation":
        return POST_RECEIPT_COMMANDS
    if status_value == "manual_review_unreadable_archive_candidate":
        return "Confirm the archive is the unchanged official World Bank package; if valid, use an external archive tool, then run the receipt validation chain."
    if status_value == "manual_review_candidate_raw_present_no_expected_name_match":
        return "Manually confirm package identity against the official catalog and expected filenames before receipt validation."
    return "Download or place the complete unchanged official raw package and documentation into this target folder."


def build_outputs() -> tuple[list[dict[str, str]], list[dict[str, str]], list[dict[str, str]]]:
    board_rows = read_csv_dicts(BOARD_PATH)
    file_rows_by_id = rows_by_id(read_csv_dicts(ACCEPTANCE_FILE_MATRIX_PATH))
    status_rows: list[dict[str, str]] = []
    file_inventory_rows: list[dict[str, str]] = []

    for board_row in board_rows:
        idno = clean(board_row.get("idno"))
        target_folder = resolve_project_path(board_row.get("local_target_folder", ""))
        expected_rows = file_rows_by_id.get(idno, [])
        expected_lookup, core_lookup = expected_name_sets(expected_rows)
        files = list_target_files(target_folder)
        folder_file_rows = [
            file_inventory_row(board_row, path, target_folder, expected_lookup, core_lookup)
            for path in files
        ]
        file_inventory_rows.extend(folder_file_rows)

        raw_rows = [row for row in folder_file_rows if row.get("file_kind") == "candidate_raw_data_or_archive"]
        doc_rows = [row for row in folder_file_rows if row.get("file_kind") == "candidate_documentation"]
        unknown_rows = [row for row in folder_file_rows if row.get("file_kind") == "candidate_unknown"]
        placeholder_rows = [row for row in folder_file_rows if row.get("file_kind") == "placeholder_or_instruction"]
        archive_rows = [row for row in raw_rows if row.get("archive_read_status") != "not_archive"]
        direct_rows = [row for row in raw_rows if row.get("archive_read_status") == "not_archive"]
        matched_expected: list[str] = []
        matched_core: list[str] = []
        for row in folder_file_rows:
            matched_expected.extend(clean(row.get("matched_expected_file_names")).split(";") if clean(row.get("matched_expected_file_names")) else [])
            matched_core.extend(clean(row.get("matched_core_file_names")).split(";") if clean(row.get("matched_core_file_names")) else [])
        status_value = receipt_status(raw_rows, doc_rows, len(set(matched_expected)), len(set(matched_core)))

        status_rows.append(
            {
                "download_rank": clean(board_row.get("download_rank")),
                "country": clean(board_row.get("country")),
                "wave": clean(board_row.get("wave")),
                "idno": idno,
                "official_get_microdata_url": clean(board_row.get("official_get_microdata_url")),
                "local_target_folder": clean(board_row.get("local_target_folder")),
                "target_folder_exists": "1" if target_folder.exists() else "0",
                "target_file_rows": str(len(folder_file_rows)),
                "placeholder_instruction_rows": str(len(placeholder_rows)),
                "candidate_raw_file_rows": str(len(raw_rows)),
                "candidate_documentation_file_rows": str(len(doc_rows)),
                "candidate_unknown_file_rows": str(len(unknown_rows)),
                "candidate_archive_rows": str(len(archive_rows)),
                "candidate_direct_data_rows": str(len(direct_rows)),
                "candidate_raw_total_bytes": str(sum(safe_int(row.get("file_bytes")) for row in raw_rows)),
                "expected_full_file_rows": str(len(expected_rows)),
                "expected_core_file_rows": str(sum(1 for row in expected_rows if clean(row.get("priority_core_target")) == "1")),
                "expected_file_name_matches": str(len(set(matched_expected))),
                "expected_core_file_name_matches": str(len(set(matched_core))),
                "matched_expected_file_names": unique_join(matched_expected),
                "matched_core_file_names": unique_join(matched_core),
                "receipt_smoke_status": status_value,
                "next_validation_action": next_action(status_value),
                "data_write_gate_status": "blocked_no_data_write",
                "modeling_gate_status": "blocked",
            }
        )

    ready_rows = [row for row in status_rows if row.get("receipt_smoke_status") == "ready_for_official_receipt_validation"]
    blocked_no_raw_rows = [row for row in status_rows if row.get("receipt_smoke_status") == "blocked_no_candidate_raw_or_documentation_files"]
    docs_only_rows = [row for row in status_rows if row.get("receipt_smoke_status") == "blocked_documentation_only_no_candidate_raw_files"]
    manual_review_rows = [row for row in status_rows if row.get("receipt_smoke_status", "").startswith("manual_review")]
    candidate_raw_rows = [row for row in file_inventory_rows if row.get("file_kind") == "candidate_raw_data_or_archive"]
    candidate_doc_rows = [row for row in file_inventory_rows if row.get("file_kind") == "candidate_documentation"]
    placeholder_rows = [row for row in file_inventory_rows if row.get("file_kind") == "placeholder_or_instruction"]

    summary_rows = [
        {"metric": "priority_lsms_target_smoke_dataset_rows", "value": str(len(status_rows)), "interpretation": "Manual-download packet target folders audited by the receipt smoke test."},
        {"metric": "priority_lsms_target_smoke_target_folders_present", "value": str(sum(1 for row in status_rows if row.get("target_folder_exists") == "1")), "interpretation": "Target folders currently present under temp/raw_downloads."},
        {"metric": "priority_lsms_target_smoke_file_inventory_rows", "value": str(len(file_inventory_rows)), "interpretation": "Files found under the target folders, including generated instructions."},
        {"metric": "priority_lsms_target_smoke_placeholder_instruction_rows", "value": str(len(placeholder_rows)), "interpretation": "Generated readmes or instruction files that do not count as raw receipt."},
        {"metric": "priority_lsms_target_smoke_candidate_raw_file_rows", "value": str(len(candidate_raw_rows)), "interpretation": "Non-placeholder files with raw data or archive extensions."},
        {"metric": "priority_lsms_target_smoke_candidate_documentation_file_rows", "value": str(len(candidate_doc_rows)), "interpretation": "Non-placeholder files with documentation extensions."},
        {"metric": "priority_lsms_target_smoke_ready_for_receipt_validation_rows", "value": str(len(ready_rows)), "interpretation": "Target folders with candidate raw files matching expected/core filenames."},
        {"metric": "priority_lsms_target_smoke_blocked_no_candidate_raw_rows", "value": str(len(blocked_no_raw_rows)), "interpretation": "Target folders that still contain no candidate raw or documentation files."},
        {"metric": "priority_lsms_target_smoke_documentation_only_rows", "value": str(len(docs_only_rows)), "interpretation": "Target folders with documentation but no candidate raw files."},
        {"metric": "priority_lsms_target_smoke_manual_review_rows", "value": str(len(manual_review_rows)), "interpretation": "Target folders with candidate raw files that need manual identity review before receipt validation."},
        {"metric": "priority_lsms_target_smoke_expected_name_match_rows", "value": str(sum(1 for row in status_rows if safe_int(row.get("expected_file_name_matches")) > 0)), "interpretation": "Target folders with at least one expected filename match."},
        {"metric": "priority_lsms_target_smoke_core_name_match_rows", "value": str(sum(1 for row in status_rows if safe_int(row.get("expected_core_file_name_matches")) > 0)), "interpretation": "Target folders with at least one core expected filename match."},
        {"metric": "priority_lsms_target_smoke_data_write_status", "value": "blocked_no_data_write", "interpretation": "Receipt smoke testing never writes promoted data."},
        {"metric": "modeling_gate_status", "value": "blocked", "interpretation": "No predictive, reduced-form, causal ML, or policy learning until registry thresholds pass."},
    ]
    return status_rows, file_inventory_rows, summary_rows


def markdown_table(rows: list[dict[str, str]], columns: list[str], limit: int = 40) -> str:
    if not rows:
        return "_No rows._"
    lines = ["| " + " | ".join(columns) + " |", "| " + " | ".join("---" for _ in columns) + " |"]
    for row in rows[:limit]:
        values: list[str] = []
        for column in columns:
            value = clean(row.get(column)).replace("|", "/")
            if len(value) > 90:
                value = value[:87] + "..."
            values.append(value)
        lines.append("| " + " | ".join(values) + " |")
    if len(rows) > limit:
        lines.append("| " + " | ".join("..." for _ in columns) + " |")
    return "\n".join(lines)


def write_report(status_rows: list[dict[str, str]], file_rows: list[dict[str, str]], summary_rows: list[dict[str, str]]) -> None:
    REPORT_PATH.write_text(
        f"""# Priority LSMS/ISA Target Folder Receipt Smoke Test

Status: non-destructive target-folder audit for the 10 minimum-batch manual downloads.

This smoke test scans each `temp/raw_downloads/<IDNO>/` target folder from the
manual execution board and separates generated instructions from candidate raw
data packages, candidate documentation, and unknown files. It also performs a
filename/member-name match against the official expected-file matrix where
possible. It does not move, delete, extract, promote, or write `data/` files.

## Summary

{markdown_table(summary_rows, ['metric', 'value', 'interpretation'], 30)}

## Target Folder Status

{markdown_table(status_rows, ['download_rank', 'idno', 'target_file_rows', 'candidate_raw_file_rows', 'candidate_documentation_file_rows', 'expected_file_name_matches', 'expected_core_file_name_matches', 'receipt_smoke_status'], 30)}

## Candidate File Preview

{markdown_table([row for row in file_rows if row.get('file_kind') != 'placeholder_or_instruction'], ['idno', 'target_relative_path', 'file_kind', 'file_bytes', 'archive_read_status', 'expected_file_name_matches', 'expected_core_file_name_matches'], 60)}

## Stop Rule

If `candidate_raw_file_rows` is zero, the country-wave remains blocked at raw
receipt. If candidate raw files are present but no expected filenames match,
manual identity review is required before running the receipt/schema/value
audit chain. Passing this smoke test is not analysis readiness; it only starts
official receipt validation.
""",
        encoding="utf-8",
    )


def main() -> None:
    ensure_dirs()
    status_rows, file_rows, summary_rows = build_outputs()
    write_csv(STATUS_PATH, status_rows, STATUS_COLUMNS)
    write_csv(FILE_INVENTORY_PATH, file_rows, FILE_COLUMNS)
    write_csv(SUMMARY_PATH, summary_rows, SUMMARY_COLUMNS)
    write_report(status_rows, file_rows, summary_rows)
    ready = sum(1 for row in status_rows if row.get("receipt_smoke_status") == "ready_for_official_receipt_validation")
    raw = sum(1 for row in file_rows if row.get("file_kind") == "candidate_raw_data_or_archive")
    append_log(
        TEMP_DIR / "audit_log.md",
        f"Built priority LSMS/ISA target folder receipt smoke test target_rows={len(status_rows)} candidate_raw_files={raw} ready_for_receipt={ready}.",
    )
    print(f"Priority LSMS/ISA target folder receipt smoke test targets={len(status_rows)} candidate_raw_files={raw} ready_for_receipt={ready}.")


if __name__ == "__main__":
    main()
