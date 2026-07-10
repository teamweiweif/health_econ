from __future__ import annotations

import csv
from collections import Counter, defaultdict
from typing import Any

from common import REPORT_DIR, RESULT_DIR, TEMP_DIR, append_log, ensure_dirs, write_csv


BOARD_PATH = TEMP_DIR / "priority_lsms_isa_manual_download_execution_board.csv"
FULL_MANIFEST_PATH = TEMP_DIR / "priority_lsms_isa_minimum_batch_expected_file_manifest.csv"
CORE_MANIFEST_PATH = TEMP_DIR / "priority_lsms_isa_minimum_batch_core_file_manifest.csv"
FILE_MATCH_PATH = TEMP_DIR / "priority_lsms_isa_official_file_receipt_file_match.csv"
CORE_MATCH_PATH = TEMP_DIR / "priority_lsms_isa_official_file_receipt_core_match.csv"
RESOURCE_ROUTE_SUMMARY_PATH = RESULT_DIR / "priority_lsms_isa_resource_download_route_probe_summary.csv"

FILE_MATRIX_PATH = TEMP_DIR / "priority_lsms_isa_download_acceptance_file_matrix.csv"
REQUIREMENT_MATRIX_PATH = TEMP_DIR / "priority_lsms_isa_download_acceptance_requirement_matrix.csv"
SUMMARY_PATH = RESULT_DIR / "priority_lsms_isa_download_acceptance_matrix_summary.csv"
REPORT_PATH = REPORT_DIR / "priority_lsms_isa_download_acceptance_matrix.md"

FILE_COLUMNS = [
    "download_rank",
    "country",
    "wave",
    "idno",
    "catalog_id",
    "official_get_microdata_url",
    "local_target_folder",
    "file_id",
    "expected_file_name",
    "file_description",
    "case_quantity",
    "variable_quantity",
    "priority_core_target",
    "core_requirements",
    "core_top_variable_names",
    "current_official_file_match_status",
    "matched_local_locations",
    "acceptance_gate_status",
    "post_download_acceptance_action",
    "fill_received_file_or_archive_member",
    "fill_sha256_verified",
    "fill_units_recall_skip_reviewed",
    "fill_ready_for_raw_value_review",
    "data_write_gate_status",
    "modeling_gate_status",
]

REQUIREMENT_COLUMNS = [
    "download_rank",
    "country",
    "wave",
    "idno",
    "requirement",
    "core_file_rows",
    "core_matched_file_rows",
    "core_missing_file_rows",
    "unique_expected_core_files",
    "top_variable_names",
    "requirement_acceptance_status",
    "post_download_requirement_action",
    "data_write_gate_status",
    "modeling_gate_status",
]

SUMMARY_COLUMNS = ["metric", "value", "interpretation"]


def read_csv_dicts(path) -> list[dict[str, str]]:
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


def summary_row(metric: str, value: Any, interpretation: str) -> dict[str, str]:
    return {"metric": metric, "value": str(value), "interpretation": interpretation}


def csv_metric(rows: list[dict[str, str]], metric: str, default: str = "0") -> str:
    return next((clean(row.get("value")) for row in rows if clean(row.get("metric")) == metric), default)


def unique_join(values: list[str], limit: int = 12) -> str:
    seen: list[str] = []
    for value in values:
        text = clean(value)
        if text and text not in seen:
            seen.append(text)
    if len(seen) > limit:
        return ";".join(seen[:limit] + [f"...{len(seen) - limit} more"])
    return ";".join(seen)


def one_by_id(rows: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    out: dict[str, dict[str, str]] = {}
    for row in rows:
        idno = clean(row.get("idno"))
        if idno and idno not in out:
            out[idno] = row
    return out


def by_id_file(rows: list[dict[str, str]], file_field: str) -> dict[tuple[str, str], list[dict[str, str]]]:
    out: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        idno = clean(row.get("idno"))
        file_id = clean(row.get("file_id"))
        file_name = clean(row.get(file_field)).lower()
        if idno and file_id:
            out[(idno, file_id)].append(row)
        if idno and file_name:
            out[(idno, file_name)].append(row)
    return out


def by_id_requirement(rows: list[dict[str, str]]) -> dict[tuple[str, str], list[dict[str, str]]]:
    out: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        idno = clean(row.get("idno"))
        requirement = clean(row.get("requirement"))
        if idno and requirement:
            out[(idno, requirement)].append(row)
    return out


def build_file_matrix(
    board_rows: list[dict[str, str]],
    full_rows: list[dict[str, str]],
    core_rows: list[dict[str, str]],
    file_match_rows: list[dict[str, str]],
) -> list[dict[str, str]]:
    board = one_by_id(board_rows)
    core_lookup = by_id_file(core_rows, "expected_file_name")
    match_lookup = by_id_file(file_match_rows, "expected_file_name")
    matrix: list[dict[str, str]] = []
    for row in sorted(full_rows, key=lambda r: (safe_int(r.get("threshold_sequence_rank"), 9999), clean(r.get("file_id")))):
        idno = clean(row.get("idno"))
        if idno not in board:
            continue
        file_id = clean(row.get("file_id"))
        file_name = clean(row.get("file_name"))
        core_matches = core_lookup.get((idno, file_id), []) or core_lookup.get((idno, file_name.lower()), [])
        file_matches = match_lookup.get((idno, file_id), []) or match_lookup.get((idno, file_name.lower()), [])
        match_statuses = [clean(match.get("official_file_match_status")) for match in file_matches]
        matched_locations = [clean(match.get("matched_local_locations")) for match in file_matches]
        current_match_status = "matched_expected_official_file" if any(status == "matched_expected_official_file" for status in match_statuses) else "missing_expected_official_file"
        acceptance = "present_needs_raw_value_review" if current_match_status == "matched_expected_official_file" else "missing_required_official_file"
        action = (
            "Run raw value and semantics review for this received official file."
            if acceptance == "present_needs_raw_value_review"
            else "Confirm this file or its archive member is present after placing the complete official package locally."
        )
        matrix.append(
            {
                "download_rank": clean(board[idno].get("download_rank")),
                "country": clean(row.get("country")),
                "wave": clean(row.get("wave")),
                "idno": idno,
                "catalog_id": clean(row.get("catalog_id")),
                "official_get_microdata_url": clean(board[idno].get("official_get_microdata_url")),
                "local_target_folder": clean(board[idno].get("local_target_folder")),
                "file_id": file_id,
                "expected_file_name": file_name,
                "file_description": clean(row.get("file_description")),
                "case_quantity": clean(row.get("case_quantity")),
                "variable_quantity": clean(row.get("variable_quantity")),
                "priority_core_target": "1" if core_matches else clean(row.get("priority_core_target")),
                "core_requirements": unique_join([core.get("requirement", "") for core in core_matches]),
                "core_top_variable_names": unique_join([core.get("top_variable_names", "") for core in core_matches], limit=8),
                "current_official_file_match_status": current_match_status,
                "matched_local_locations": unique_join(matched_locations, limit=8),
                "acceptance_gate_status": acceptance,
                "post_download_acceptance_action": action,
                "fill_received_file_or_archive_member": "",
                "fill_sha256_verified": "",
                "fill_units_recall_skip_reviewed": "",
                "fill_ready_for_raw_value_review": "",
                "data_write_gate_status": "blocked_no_data_write",
                "modeling_gate_status": "blocked",
            }
        )
    return matrix


def build_requirement_matrix(
    board_rows: list[dict[str, str]],
    core_rows: list[dict[str, str]],
    core_match_rows: list[dict[str, str]],
) -> list[dict[str, str]]:
    board = one_by_id(board_rows)
    match_by_req = by_id_requirement(core_match_rows)
    rows: list[dict[str, str]] = []
    for (idno, requirement), req_rows in sorted(by_id_requirement(core_rows).items(), key=lambda item: (safe_int(board.get(item[0][0], {}).get("download_rank"), 9999), item[0][1])):
        if idno not in board:
            continue
        matches = match_by_req.get((idno, requirement), [])
        matched = sum(1 for row in matches if clean(row.get("official_core_file_match_status")) == "matched_expected_core_file")
        total = len(req_rows)
        missing = max(total - matched, 0)
        status = "ready_for_raw_value_review" if missing == 0 and total > 0 else "blocked_missing_core_files"
        action = (
            "Proceed to requirement-level raw value, units, recall, skip, and merge-key review."
            if status == "ready_for_raw_value_review"
            else "After placing the complete official package, confirm all requirement-linked core files are present."
        )
        rows.append(
            {
                "download_rank": clean(board[idno].get("download_rank")),
                "country": clean(board[idno].get("country")),
                "wave": clean(board[idno].get("wave")),
                "idno": idno,
                "requirement": requirement,
                "core_file_rows": str(total),
                "core_matched_file_rows": str(matched),
                "core_missing_file_rows": str(missing),
                "unique_expected_core_files": unique_join([row.get("expected_file_name", "") for row in req_rows], limit=18),
                "top_variable_names": unique_join([row.get("top_variable_names", "") for row in req_rows], limit=10),
                "requirement_acceptance_status": status,
                "post_download_requirement_action": action,
                "data_write_gate_status": "blocked_no_data_write",
                "modeling_gate_status": "blocked",
            }
        )
    return rows


def build_summary(
    board_rows: list[dict[str, str]],
    file_rows: list[dict[str, str]],
    requirement_rows: list[dict[str, str]],
    route_summary: list[dict[str, str]],
) -> list[dict[str, str]]:
    file_status = Counter(row.get("acceptance_gate_status", "") for row in file_rows)
    req_status = Counter(row.get("requirement_acceptance_status", "") for row in requirement_rows)
    return [
        summary_row("download_acceptance_dataset_rows", len(board_rows), "Manual-download packet rows covered by the acceptance matrix."),
        summary_row("download_acceptance_expected_file_rows", len(file_rows), "Official expected file rows in the 10-packet acceptance matrix."),
        summary_row("download_acceptance_core_requirement_rows", len(requirement_rows), "Requirement-level acceptance rows built from core files."),
        summary_row("download_acceptance_core_file_rows", sum(safe_int(row.get("core_file_rows")) for row in requirement_rows), "Requirement-linked core file rows represented in the acceptance matrix."),
        summary_row("download_acceptance_missing_expected_file_rows", file_status.get("missing_required_official_file", 0), "Expected official files still absent from local target folders."),
        summary_row("download_acceptance_present_file_rows", file_status.get("present_needs_raw_value_review", 0), "Expected official files present locally but still needing raw value review."),
        summary_row("download_acceptance_missing_core_requirement_rows", req_status.get("blocked_missing_core_files", 0), "Requirement rows still blocked by missing core files."),
        summary_row("download_acceptance_ready_requirement_rows", req_status.get("ready_for_raw_value_review", 0), "Requirement rows whose core files are present and ready for raw value review."),
        summary_row("download_acceptance_official_url_rows", sum(1 for row in board_rows if clean(row.get("official_get_microdata_url"))), "Packet rows with official get-microdata URLs."),
        summary_row("download_acceptance_resource_route_raw_payload_rows", csv_metric(route_summary, "resource_download_route_probe_raw_payload_candidate_rows", "0"), "Public resource-route raw payload candidates from the latest route probe."),
        summary_row("download_acceptance_resource_route_request_failed_rows", csv_metric(route_summary, "resource_download_route_probe_request_failed_rows", "0"), "Failed public resource-route requests from the latest route probe."),
        summary_row("data_write_gate_status", "blocked_no_data_write", "The acceptance matrix is a receipt checklist only and never writes promoted data."),
        summary_row("modeling_gate_status", "blocked", "No predictive, reduced-form, causal ML, or policy learning until registry thresholds pass."),
    ]


def markdown_table(rows: list[dict[str, str]], columns: list[str], limit: int = 30) -> str:
    if not rows:
        return "_No rows._"
    lines = ["| " + " | ".join(columns) + " |", "| " + " | ".join("---" for _ in columns) + " |"]
    for row in rows[:limit]:
        values = []
        for column in columns:
            value = clean(row.get(column)).replace("|", "/")
            if len(value) > 100:
                value = value[:97] + "..."
            values.append(value)
        lines.append("| " + " | ".join(values) + " |")
    if len(rows) > limit:
        lines.append("| " + " | ".join("..." for _ in columns) + " |")
    return "\n".join(lines)


def write_report(file_rows: list[dict[str, str]], requirement_rows: list[dict[str, str]], summary_rows: list[dict[str, str]]) -> None:
    metric = {row["metric"]: row["value"] for row in summary_rows}
    dataset_rows: list[dict[str, str]] = []
    for idno in sorted({row.get("idno", "") for row in file_rows}, key=lambda value: safe_int(next((row.get("download_rank") for row in file_rows if row.get("idno") == value), 9999))):
        rows = [row for row in file_rows if row.get("idno") == idno]
        reqs = [row for row in requirement_rows if row.get("idno") == idno]
        first = rows[0] if rows else {}
        dataset_rows.append(
            {
                "download_rank": clean(first.get("download_rank")),
                "country": clean(first.get("country")),
                "wave": clean(first.get("wave")),
                "idno": idno,
                "expected_files": str(len(rows)),
                "missing_files": str(sum(1 for row in rows if row.get("acceptance_gate_status") == "missing_required_official_file")),
                "core_requirements": str(len(reqs)),
                "blocked_requirements": str(sum(1 for row in reqs if row.get("requirement_acceptance_status") == "blocked_missing_core_files")),
            }
        )

    lines = [
        "# Priority LSMS-ISA Download Acceptance Matrix",
        "",
        "Status: receipt checklist for the 10 remaining minimum-batch official raw packages.",
        "",
        "This matrix converts the official file manifest and requirement-linked core files into a file-by-file acceptance checklist. It does not download, copy, extract, write promoted `data/`, or run models.",
        "",
        "## Summary",
        "",
        f"- Packet datasets: {metric.get('download_acceptance_dataset_rows', '0')}",
        f"- Expected official files: {metric.get('download_acceptance_expected_file_rows', '0')}",
        f"- Requirement-level rows: {metric.get('download_acceptance_core_requirement_rows', '0')}",
        f"- Requirement-linked core file rows: {metric.get('download_acceptance_core_file_rows', '0')}",
        f"- Missing expected files: {metric.get('download_acceptance_missing_expected_file_rows', '0')}",
        f"- Ready requirement rows: {metric.get('download_acceptance_ready_requirement_rows', '0')}",
        f"- Public route raw payload candidates: {metric.get('download_acceptance_resource_route_raw_payload_rows', '0')}",
        f"- Data-write gate: {metric.get('data_write_gate_status', 'missing')}",
        f"- Modeling gate: {metric.get('modeling_gate_status', 'missing')}",
        "",
        "## Dataset Acceptance Status",
        "",
        markdown_table(dataset_rows, ["download_rank", "country", "wave", "idno", "expected_files", "missing_files", "core_requirements", "blocked_requirements"], 20),
        "",
        "## Requirement Preview",
        "",
        markdown_table(requirement_rows, ["download_rank", "idno", "requirement", "core_file_rows", "core_missing_file_rows", "requirement_acceptance_status"], 40),
        "",
        "## File Preview",
        "",
        markdown_table(file_rows, ["download_rank", "idno", "file_id", "expected_file_name", "priority_core_target", "core_requirements", "acceptance_gate_status"], 60),
        "",
        "## Use",
        "",
        "After a complete official package is placed in the packet target folder, rerun the raw-download audit, archive preflight, official file receipt validator, and this script. A wave must have all required files and requirement rows present before raw value, units, recall, missing-code, skip-pattern, merge-key, and design checks can promote it.",
    ]
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    ensure_dirs()
    board_rows = read_csv_dicts(BOARD_PATH)
    full_rows = read_csv_dicts(FULL_MANIFEST_PATH)
    core_rows = read_csv_dicts(CORE_MANIFEST_PATH)
    file_match_rows = read_csv_dicts(FILE_MATCH_PATH)
    core_match_rows = read_csv_dicts(CORE_MATCH_PATH)
    route_summary = read_csv_dicts(RESOURCE_ROUTE_SUMMARY_PATH)

    file_matrix = build_file_matrix(board_rows, full_rows, core_rows, file_match_rows)
    requirement_matrix = build_requirement_matrix(board_rows, core_rows, core_match_rows)
    summary_rows = build_summary(board_rows, file_matrix, requirement_matrix, route_summary)

    write_csv(FILE_MATRIX_PATH, file_matrix, FILE_COLUMNS)
    write_csv(REQUIREMENT_MATRIX_PATH, requirement_matrix, REQUIREMENT_COLUMNS)
    write_csv(SUMMARY_PATH, summary_rows, SUMMARY_COLUMNS)
    write_report(file_matrix, requirement_matrix, summary_rows)
    append_log(TEMP_DIR / "audit_log.md", f"Built priority LSMS/ISA download acceptance matrix: {len(file_matrix)} expected files, {len(requirement_matrix)} requirement rows.")


if __name__ == "__main__":
    main()
