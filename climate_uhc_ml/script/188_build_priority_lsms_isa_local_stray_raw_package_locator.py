from __future__ import annotations

import csv
import os
import tarfile
import zipfile
from pathlib import Path, PurePosixPath
from typing import Any

from common import PROJECT_ROOT, REPORT_DIR, RESULT_DIR, TEMP_DIR, append_log, ensure_dirs, write_csv


BOARD_PATH = TEMP_DIR / "priority_lsms_isa_manual_download_execution_board.csv"
ACCEPTANCE_FILE_MATRIX_PATH = TEMP_DIR / "priority_lsms_isa_download_acceptance_file_matrix.csv"
TARGET_SMOKE_STATUS_PATH = TEMP_DIR / "priority_lsms_isa_target_folder_receipt_status.csv"

CANDIDATE_PATH = TEMP_DIR / "priority_lsms_isa_local_stray_raw_package_candidates.csv"
ROUTE_PLAN_PATH = TEMP_DIR / "priority_lsms_isa_local_stray_raw_package_route_plan.csv"
SUMMARY_PATH = RESULT_DIR / "priority_lsms_isa_local_stray_raw_package_locator_summary.csv"
REPORT_PATH = REPORT_DIR / "priority_lsms_isa_local_stray_raw_package_locator.md"

WORKSPACE_ROOT = PROJECT_ROOT.parent

DIRECT_DATA_SUFFIXES = {".dta", ".sav", ".por", ".sas7bdat", ".xpt", ".csv", ".tsv", ".xlsx", ".xls"}
ARCHIVE_SUFFIXES = {".zip", ".tar", ".tgz", ".gz", ".rar", ".7z"}
DOCUMENTATION_SUFFIXES = {".pdf", ".doc", ".docx", ".html", ".htm", ".txt", ".rtf", ".xml", ".json"}
SCAN_SUFFIXES = DIRECT_DATA_SUFFIXES | ARCHIVE_SUFFIXES | DOCUMENTATION_SUFFIXES
UNSUPPORTED_ARCHIVE_SUFFIXES = {".rar", ".7z"}

SKIP_DIR_NAMES = {
    ".git",
    ".agents",
    ".codex",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    "node_modules",
    ".venv",
    "venv",
    "env",
}
SKIP_PROJECT_SUBTREES = {
    "temp/api_cache",
    "temp/climate_cache",
    "temp/raw_downloads/climate_boundaries",
    "temp/raw_downloads/climate_chirps",
    "temp/raw_schema_inventory",
    "temp/source_snapshots",
}

CANDIDATE_COLUMNS = [
    "download_rank",
    "country",
    "wave",
    "idno",
    "source_scope",
    "candidate_relative_path",
    "file_name",
    "file_extension",
    "file_bytes",
    "file_kind",
    "location_status",
    "match_basis",
    "expected_file_name_matches",
    "expected_core_file_name_matches",
    "direct_expected_file_matches",
    "archive_member_expected_file_matches",
    "archive_read_status",
    "archive_member_count",
    "suggested_target_folder",
    "manual_review_action",
    "copy_command_powershell",
    "data_write_gate_status",
    "modeling_gate_status",
]

ROUTE_COLUMNS = [
    "download_rank",
    "country",
    "wave",
    "idno",
    "local_target_folder",
    "target_receipt_smoke_status",
    "stray_candidate_rows",
    "already_target_candidate_rows",
    "incoming_candidate_rows",
    "outside_target_candidate_rows",
    "direct_expected_match_rows",
    "archive_member_match_rows",
    "core_expected_match_rows",
    "weak_archive_name_rows",
    "matched_expected_file_names",
    "matched_core_file_names",
    "route_status",
    "suggested_next_action",
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


def normalize_token(value: str) -> str:
    return "".join(ch for ch in clean(value).lower() if ch.isalnum())


def resolve_project_path(path_text: str) -> Path:
    text = clean(path_text).replace("\\", "/").strip("/")
    path = Path(text)
    if path.is_absolute():
        return path
    return PROJECT_ROOT / text


def path_is_relative_to(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
        return True
    except ValueError:
        return False


def display_path(path: Path) -> str:
    try:
        return str(path.relative_to(PROJECT_ROOT)).replace("\\", "/")
    except ValueError:
        pass
    try:
        return ("../" + str(path.relative_to(WORKSPACE_ROOT))).replace("\\", "/")
    except ValueError:
        return str(path).replace("\\", "/")


def powershell_quote(value: str) -> str:
    return "'" + value.replace("'", "''") + "'"


def source_scope(path: Path) -> str:
    if path_is_relative_to(path, PROJECT_ROOT):
        return "project_root"
    if path_is_relative_to(path, WORKSPACE_ROOT):
        return "workspace_root_outside_project"
    return "outside_known_workspace"


def classify_file(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix in DIRECT_DATA_SUFFIXES:
        return "direct_raw_data_candidate"
    if suffix in ARCHIVE_SUFFIXES:
        return "archive_raw_package_candidate"
    if suffix in DOCUMENTATION_SUFFIXES:
        return "documentation_candidate"
    return "other_candidate"


def location_status(path: Path, target_folder: Path) -> str:
    incoming = TEMP_DIR / "raw_downloads" / "_incoming"
    raw_downloads = TEMP_DIR / "raw_downloads"
    if path_is_relative_to(path, target_folder):
        return "already_in_target_folder"
    if path_is_relative_to(path, incoming):
        return "incoming_staging"
    if path_is_relative_to(path, raw_downloads):
        return "raw_downloads_other_folder"
    if path_is_relative_to(path, PROJECT_ROOT):
        return "project_outside_target_folder"
    if path_is_relative_to(path, WORKSPACE_ROOT):
        return "workspace_outside_project"
    return "outside_known_workspace"


def unique_join(values: list[str], limit: int = 20) -> str:
    seen: list[str] = []
    for value in values:
        for piece in clean(value).split(";"):
            text = clean(piece)
            if text and text not in seen:
                seen.append(text)
    if len(seen) > limit:
        return ";".join(seen[:limit] + [f"...{len(seen) - limit} more"])
    return ";".join(seen)


def rows_by_id(rows: list[dict[str, str]]) -> dict[str, list[dict[str, str]]]:
    out: dict[str, list[dict[str, str]]] = {}
    for row in rows:
        idno = clean(row.get("idno"))
        if idno:
            out.setdefault(idno, []).append(row)
    return out


def one_by_id(rows: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    out: dict[str, dict[str, str]] = {}
    for row in rows:
        idno = clean(row.get("idno"))
        if idno and idno not in out:
            out[idno] = row
    return out


def expected_lookup(rows: list[dict[str, str]]) -> dict[str, list[dict[str, str]]]:
    lookup: dict[str, list[dict[str, str]]] = {}
    for row in rows:
        expected = clean(row.get("expected_file_name"))
        if not expected:
            continue
        for key in key_variants(expected):
            lookup.setdefault(key, []).append(row)
    return lookup


def matching_expected_rows(names: list[str], lookup: dict[str, list[dict[str, str]]]) -> list[dict[str, str]]:
    matches: list[dict[str, str]] = []
    seen: set[tuple[str, str]] = set()
    for name in names:
        for key in key_variants(name):
            for row in lookup.get(key, []):
                marker = (clean(row.get("idno")), clean(row.get("expected_file_name")))
                if marker not in seen:
                    matches.append(row)
                    seen.add(marker)
    return matches


def archive_member_names(path: Path) -> tuple[str, list[str]]:
    suffix = path.suffix.lower()
    if suffix == ".zip":
        try:
            with zipfile.ZipFile(path) as zf:
                return "readable_zip", [name for name in zf.namelist() if not name.endswith("/")]
        except (OSError, zipfile.BadZipFile):
            return "unreadable_zip", []
    if suffix in {".tar", ".tgz"}:
        try:
            with tarfile.open(path) as tf:
                return "readable_tar", [member.name for member in tf.getmembers() if member.isfile()]
        except (OSError, tarfile.TarError):
            return "unreadable_tar", []
    if suffix == ".gz":
        return "plain_gzip_or_unlisted_archive", []
    if suffix in UNSUPPORTED_ARCHIVE_SUFFIXES:
        return "unsupported_archive_type", []
    return "not_archive", []


def should_skip_project_subtree(path: Path) -> bool:
    try:
        relative = str(path.relative_to(PROJECT_ROOT)).replace("\\", "/")
    except ValueError:
        return False
    return any(relative == subtree or relative.startswith(f"{subtree}/") for subtree in SKIP_PROJECT_SUBTREES)


def iter_scan_files(search_roots: list[Path]) -> tuple[list[Path], int, int]:
    files: list[Path] = []
    scanned_rows = 0
    unreadable_dirs = 0
    seen_dirs: set[Path] = set()

    for root in search_roots:
        if not root.exists() or not root.is_dir():
            continue
        try:
            resolved_root = root.resolve()
        except OSError:
            resolved_root = root
        if resolved_root in seen_dirs:
            continue
        seen_dirs.add(resolved_root)

        for current_root, dir_names, file_names in os.walk(root, topdown=True, onerror=lambda _err: None):
            current_path = Path(current_root)
            if should_skip_project_subtree(current_path):
                dir_names[:] = []
                continue
            before = len(dir_names)
            dir_names[:] = [name for name in dir_names if name not in SKIP_DIR_NAMES]
            unreadable_dirs += max(0, before - len(dir_names))

            for file_name in file_names:
                scanned_rows += 1
                path = current_path / file_name
                if path.name.startswith("_") and path.suffix.lower() in {".md", ".txt"}:
                    continue
                if path.suffix.lower() not in SCAN_SUFFIXES:
                    continue
                files.append(path)

    unique_files: list[Path] = []
    seen_files: set[str] = set()
    for path in files:
        try:
            marker = str(path.resolve()).lower()
        except OSError:
            marker = str(path).lower()
        if marker not in seen_files:
            unique_files.append(path)
            seen_files.add(marker)
    return unique_files, scanned_rows, unreadable_dirs


def idno_archive_name_match(path: Path, board_row: dict[str, str]) -> bool:
    if path.suffix.lower() not in ARCHIVE_SUFFIXES:
        return False
    name_token = normalize_token(path.name)
    idno_token = normalize_token(board_row.get("idno", ""))
    catalog_token = normalize_token(board_row.get("catalog_id", ""))
    return bool((idno_token and idno_token in name_token) or (catalog_token and catalog_token in name_token))


def path_context_matches(path: Path, board_row: dict[str, str]) -> bool:
    text = normalize_token(display_path(path))
    idno_token = normalize_token(board_row.get("idno", ""))
    catalog_token = normalize_token(board_row.get("catalog_id", ""))
    return bool((idno_token and idno_token in text) or (catalog_token and catalog_token in text))


def has_core_match(rows: list[dict[str, str]]) -> bool:
    return any(clean(row.get("priority_core_target")) == "1" for row in rows)


def candidate_rows_for_file(
    path: Path,
    board_by_id: dict[str, dict[str, str]],
    expected_by_key: dict[str, list[dict[str, str]]],
) -> tuple[list[dict[str, str]], str]:
    suffix = path.suffix.lower()
    archive_status, members = archive_member_names(path) if suffix in ARCHIVE_SUFFIXES else ("not_archive", [])
    direct_matches = matching_expected_rows([path.name], expected_by_key)
    archive_matches = matching_expected_rows(members, expected_by_key)
    matched_ids = sorted({clean(row.get("idno")) for row in direct_matches + archive_matches if clean(row.get("idno"))})

    for idno, board in board_by_id.items():
        if idno_archive_name_match(path, board) and idno not in matched_ids:
            matched_ids.append(idno)

    rows: list[dict[str, str]] = []
    for idno in matched_ids:
        board = board_by_id[idno]
        target_folder_text = clean(board.get("local_target_folder"))
        target_folder = resolve_project_path(target_folder_text)
        direct_for_id = [row for row in direct_matches if clean(row.get("idno")) == idno]
        archive_for_id = [row for row in archive_matches if clean(row.get("idno")) == idno]
        weak_archive = idno_archive_name_match(path, board) and not direct_for_id and not archive_for_id
        target_location_status = location_status(path, target_folder)
        context_match = path_context_matches(path, board)
        matched_core = has_core_match(direct_for_id + archive_for_id)
        if (
            (direct_for_id or archive_for_id)
            and target_location_status not in {"already_in_target_folder", "incoming_staging"}
            and not context_match
            and not matched_core
        ):
            continue
        expected_matches = unique_join([row.get("expected_file_name", "") for row in direct_for_id + archive_for_id])
        core_matches = unique_join(
            [row.get("expected_file_name", "") for row in direct_for_id + archive_for_id if clean(row.get("priority_core_target")) == "1"]
        )
        basis_parts: list[str] = []
        if direct_for_id:
            basis_parts.append("direct_filename_expected")
        if archive_for_id:
            basis_parts.append("archive_member_expected")
        if weak_archive:
            basis_parts.append("archive_name_idno_or_catalog")
        if not basis_parts:
            continue

        display = display_path(path)
        copy_command = (
            "Review first; then Copy-Item -LiteralPath "
            f"{powershell_quote(display)} -Destination {powershell_quote(target_folder_text)}"
        )
        rows.append(
            {
                "download_rank": clean(board.get("download_rank")),
                "country": clean(board.get("country")),
                "wave": clean(board.get("wave")),
                "idno": idno,
                "source_scope": source_scope(path),
                "candidate_relative_path": display,
                "file_name": path.name,
                "file_extension": suffix,
                "file_bytes": str(path.stat().st_size if path.exists() else 0),
                "file_kind": classify_file(path),
                "location_status": target_location_status,
                "match_basis": ";".join(basis_parts),
                "expected_file_name_matches": expected_matches,
                "expected_core_file_name_matches": core_matches,
                "direct_expected_file_matches": unique_join([row.get("expected_file_name", "") for row in direct_for_id]),
                "archive_member_expected_file_matches": unique_join([row.get("expected_file_name", "") for row in archive_for_id]),
                "archive_read_status": archive_status,
                "archive_member_count": str(len(members)),
                "suggested_target_folder": target_folder_text,
                "manual_review_action": "Do not trust or promote this file from the locator alone; manually confirm source, completeness, and terms before copying to the target folder.",
                "copy_command_powershell": copy_command,
                "data_write_gate_status": "blocked_no_data_write",
                "modeling_gate_status": "blocked",
            }
        )
    return rows, archive_status


def build_route_rows(
    board_rows: list[dict[str, str]],
    smoke_by_id: dict[str, dict[str, str]],
    candidate_rows: list[dict[str, str]],
) -> list[dict[str, str]]:
    by_id = rows_by_id(candidate_rows)
    route_rows: list[dict[str, str]] = []

    for board in board_rows:
        idno = clean(board.get("idno"))
        rows = by_id.get(idno, [])
        already = [row for row in rows if row.get("location_status") == "already_in_target_folder"]
        incoming = [row for row in rows if row.get("location_status") == "incoming_staging"]
        outside = [row for row in rows if row.get("location_status") not in {"already_in_target_folder", "incoming_staging"}]
        direct = [row for row in rows if "direct_filename_expected" in row.get("match_basis", "")]
        archive = [row for row in rows if "archive_member_expected" in row.get("match_basis", "")]
        weak = [row for row in rows if row.get("match_basis") == "archive_name_idno_or_catalog"]
        core = [row for row in rows if clean(row.get("expected_core_file_name_matches"))]

        if not rows:
            route_status = "no_local_stray_raw_package_found"
            next_action = "Complete the manual World Bank get-microdata download or place already downloaded files under the target folder or _incoming."
        elif outside or incoming:
            route_status = "manual_review_required_before_copy_to_target"
            next_action = "Review candidate provenance and terms, copy only verified files to the target folder, then rerun the target-folder receipt smoke test."
        else:
            route_status = "candidate_already_in_target_folder_rerun_receipt_gate"
            next_action = "Rerun the target-folder receipt smoke test and then receipt/schema/value validation; do not promote until all raw gates pass."

        route_rows.append(
            {
                "download_rank": clean(board.get("download_rank")),
                "country": clean(board.get("country")),
                "wave": clean(board.get("wave")),
                "idno": idno,
                "local_target_folder": clean(board.get("local_target_folder")),
                "target_receipt_smoke_status": clean(smoke_by_id.get(idno, {}).get("receipt_smoke_status")) or "target_not_in_smoke_test",
                "stray_candidate_rows": str(len(rows)),
                "already_target_candidate_rows": str(len(already)),
                "incoming_candidate_rows": str(len(incoming)),
                "outside_target_candidate_rows": str(len(outside)),
                "direct_expected_match_rows": str(len(direct)),
                "archive_member_match_rows": str(len(archive)),
                "core_expected_match_rows": str(len(core)),
                "weak_archive_name_rows": str(len(weak)),
                "matched_expected_file_names": unique_join([row.get("expected_file_name_matches", "") for row in rows]),
                "matched_core_file_names": unique_join([row.get("expected_core_file_name_matches", "") for row in rows]),
                "route_status": route_status,
                "suggested_next_action": next_action,
                "data_write_gate_status": "blocked_no_data_write",
                "modeling_gate_status": "blocked",
            }
        )
    return route_rows


def summary_rows(
    route_rows: list[dict[str, str]],
    candidate_rows: list[dict[str, str]],
    scanned_file_rows: int,
    considered_file_rows: int,
    unreadable_dir_rows: int,
    unreadable_archive_rows: int,
) -> list[dict[str, str]]:
    matched_routes = [row for row in route_rows if safe_int(row.get("stray_candidate_rows")) > 0]
    outside = [row for row in candidate_rows if row.get("location_status") not in {"already_in_target_folder", "incoming_staging"}]
    incoming = [row for row in candidate_rows if row.get("location_status") == "incoming_staging"]
    already = [row for row in candidate_rows if row.get("location_status") == "already_in_target_folder"]
    direct = [row for row in candidate_rows if "direct_filename_expected" in row.get("match_basis", "")]
    archive = [row for row in candidate_rows if "archive_member_expected" in row.get("match_basis", "")]
    core = [row for row in candidate_rows if clean(row.get("expected_core_file_name_matches"))]
    weak = [row for row in candidate_rows if row.get("match_basis") == "archive_name_idno_or_catalog"]
    return [
        {"metric": "priority_lsms_local_stray_raw_locator_dataset_rows", "value": str(len(route_rows)), "interpretation": "Current manual-download minimum-batch rows covered by the locator route plan."},
        {"metric": "priority_lsms_local_stray_raw_locator_scanned_file_rows", "value": str(scanned_file_rows), "interpretation": "Filesystem file rows seen under the bounded search roots before suffix filtering."},
        {"metric": "priority_lsms_local_stray_raw_locator_considered_file_rows", "value": str(considered_file_rows), "interpretation": "Candidate suffix files considered for raw/documentation/package matching."},
        {"metric": "priority_lsms_local_stray_raw_locator_candidate_file_rows", "value": str(len(candidate_rows)), "interpretation": "Local candidate files matching expected core/full names, archive members, or strong IDNO/catalog archive-name tokens."},
        {"metric": "priority_lsms_local_stray_raw_locator_matched_idno_rows", "value": str(len(matched_routes)), "interpretation": "Manual-download packet rows with at least one candidate local file outside the normal receipt gate."},
        {"metric": "priority_lsms_local_stray_raw_locator_route_plan_rows", "value": str(len(route_rows)), "interpretation": "One route-plan row per current minimum-batch manual packet."},
        {"metric": "priority_lsms_local_stray_raw_locator_outside_target_candidate_rows", "value": str(len(outside)), "interpretation": "Candidate files outside the correct target folder and outside _incoming."},
        {"metric": "priority_lsms_local_stray_raw_locator_incoming_candidate_rows", "value": str(len(incoming)), "interpretation": "Candidate files already staged under temp/raw_downloads/_incoming."},
        {"metric": "priority_lsms_local_stray_raw_locator_already_target_candidate_rows", "value": str(len(already)), "interpretation": "Candidate files already inside the expected target folder."},
        {"metric": "priority_lsms_local_stray_raw_locator_direct_expected_match_rows", "value": str(len(direct)), "interpretation": "Candidates whose filename directly matches an expected file name."},
        {"metric": "priority_lsms_local_stray_raw_locator_archive_member_match_rows", "value": str(len(archive)), "interpretation": "Candidates whose readable archive member list matches expected file names."},
        {"metric": "priority_lsms_local_stray_raw_locator_core_expected_match_rows", "value": str(len(core)), "interpretation": "Candidates matching at least one priority core expected file."},
        {"metric": "priority_lsms_local_stray_raw_locator_weak_archive_name_rows", "value": str(len(weak)), "interpretation": "Archive-name-only matches using IDNO or catalog tokens; these require extra manual scrutiny."},
        {"metric": "priority_lsms_local_stray_raw_locator_unreadable_directory_rows", "value": str(unreadable_dir_rows), "interpretation": "Skipped directory rows from explicit skip rules or inaccessible walk locations."},
        {"metric": "priority_lsms_local_stray_raw_locator_unreadable_archive_rows", "value": str(unreadable_archive_rows), "interpretation": "Candidate archive files whose members could not be listed."},
        {"metric": "priority_lsms_local_stray_raw_locator_data_write_status", "value": "blocked_no_data_write", "interpretation": "The locator does not copy, extract, harmonize, or write promoted data."},
        {"metric": "priority_lsms_local_stray_raw_locator_raw_promotion_status", "value": "blocked_pending_manual_review" if candidate_rows else "blocked_no_local_stray_raw_package_found", "interpretation": "Raw packages remain unaccepted until the normal receipt, schema, value, semantics, timing/geography, and climate-linkage gates pass."},
        {"metric": "modeling_gate_status", "value": "blocked", "interpretation": "No predictive, reduced-form, causal ML, or policy learning until registry thresholds pass."},
    ]


def markdown_table(rows: list[dict[str, str]], columns: list[str], limit: int = 40) -> str:
    if not rows:
        return "_No rows._"
    lines = ["| " + " | ".join(columns) + " |", "| " + " | ".join("---" for _ in columns) + " |"]
    for row in rows[:limit]:
        values: list[str] = []
        for column in columns:
            value = clean(row.get(column)).replace("|", "/")
            if len(value) > 110:
                value = value[:107] + "..."
            values.append(value)
        lines.append("| " + " | ".join(values) + " |")
    if len(rows) > limit:
        lines.append("| " + " | ".join("..." for _ in columns) + " |")
    return "\n".join(lines)


def write_report(route_rows: list[dict[str, str]], candidate_rows: list[dict[str, str]], summaries: list[dict[str, str]]) -> None:
    REPORT_PATH.write_text(
        f"""# Priority LSMS/ISA Local Stray Raw Package Locator

Status: non-destructive local locator for the current 10 minimum-batch manual-download packets.

This locator searches the local project/workspace tree for files that appear to
match the expected LSMS/ISA raw files or archive packages but are not already
handled by the normal target-folder receipt gate. It reads only file names,
sizes, and archive member listings. It does not copy, move, delete, extract,
harmonize, write `data/`, or run models.

## Summary

{markdown_table(summaries, ['metric', 'value', 'interpretation'], 30)}

## Route Plan

{markdown_table(route_rows, ['download_rank', 'idno', 'target_receipt_smoke_status', 'stray_candidate_rows', 'outside_target_candidate_rows', 'incoming_candidate_rows', 'already_target_candidate_rows', 'route_status'], 20)}

## Candidate Files

{markdown_table(candidate_rows, ['idno', 'candidate_relative_path', 'file_kind', 'location_status', 'match_basis', 'expected_core_file_name_matches'], 80)}

## Stop Rule

Any candidate found here is only a pointer for manual review. A country-wave
remains blocked until the complete official raw package is placed in the target
folder and passes receipt, schema, raw-value, semantics, timing/geography, and
climate-linkage validation.
""",
        encoding="utf-8",
    )


def build_outputs() -> tuple[list[dict[str, str]], list[dict[str, str]], list[dict[str, str]]]:
    board_rows = read_csv_dicts(BOARD_PATH)
    board_by_id = {clean(row.get("idno")): row for row in board_rows if clean(row.get("idno"))}
    expected_by_key = expected_lookup(read_csv_dicts(ACCEPTANCE_FILE_MATRIX_PATH))
    smoke_by_id = one_by_id(read_csv_dicts(TARGET_SMOKE_STATUS_PATH))

    scan_files, scanned_file_rows, unreadable_dir_rows = iter_scan_files([PROJECT_ROOT, WORKSPACE_ROOT])
    candidate_rows: list[dict[str, str]] = []
    unreadable_archive_rows = 0
    for path in scan_files:
        try:
            rows, archive_status = candidate_rows_for_file(path, board_by_id, expected_by_key)
        except OSError:
            continue
        if archive_status.startswith("unreadable"):
            unreadable_archive_rows += 1
        candidate_rows.extend(rows)

    candidate_rows = sorted(candidate_rows, key=lambda row: (safe_int(row.get("download_rank"), 9999), row.get("candidate_relative_path", "")))
    route_rows = build_route_rows(board_rows, smoke_by_id, candidate_rows)
    summaries = summary_rows(route_rows, candidate_rows, scanned_file_rows, len(scan_files), unreadable_dir_rows, unreadable_archive_rows)
    return candidate_rows, route_rows, summaries


def main() -> None:
    ensure_dirs()
    candidate_rows, route_rows, summaries = build_outputs()
    write_csv(CANDIDATE_PATH, candidate_rows, CANDIDATE_COLUMNS)
    write_csv(ROUTE_PLAN_PATH, route_rows, ROUTE_COLUMNS)
    write_csv(SUMMARY_PATH, summaries, SUMMARY_COLUMNS)
    write_report(route_rows, candidate_rows, summaries)
    append_log(
        TEMP_DIR / "audit_log.md",
        f"Built priority LSMS/ISA local stray raw package locator route_rows={len(route_rows)} candidate_rows={len(candidate_rows)}.",
    )
    print(f"Priority LSMS/ISA local stray raw package locator route_rows={len(route_rows)} candidate_rows={len(candidate_rows)}.")


if __name__ == "__main__":
    main()
