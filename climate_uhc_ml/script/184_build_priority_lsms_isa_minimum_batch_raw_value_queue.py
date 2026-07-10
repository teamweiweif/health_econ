from __future__ import annotations

import csv
from collections import Counter
from typing import Any

from common import REPORT_DIR, RESULT_DIR, TEMP_DIR, append_log, ensure_dirs, write_csv


BOARD_PATH = TEMP_DIR / "priority_lsms_isa_manual_download_execution_board.csv"
ACCEPTANCE_FILE_MATRIX_PATH = TEMP_DIR / "priority_lsms_isa_download_acceptance_file_matrix.csv"
ACCEPTANCE_REQUIREMENT_MATRIX_PATH = TEMP_DIR / "priority_lsms_isa_download_acceptance_requirement_matrix.csv"
LOCAL_TARGET_README_SUMMARY_PATH = RESULT_DIR / "priority_lsms_isa_local_target_readme_summary.csv"

RAW_VALUE_REQUIREMENT_WORKBOOK_PATH = TEMP_DIR / "priority_lsms_isa_raw_value_requirement_workbook.csv"
RAW_VALUE_VARIABLE_WORKBOOK_PATH = TEMP_DIR / "priority_lsms_isa_raw_value_variable_workbook.csv"
RAW_VALUE_FILE_WORKBOOK_PATH = TEMP_DIR / "priority_lsms_isa_raw_value_file_workbook.csv"

REQUIREMENT_QUEUE_PATH = TEMP_DIR / "priority_lsms_isa_minimum_batch_raw_value_requirement_queue.csv"
VARIABLE_QUEUE_PATH = TEMP_DIR / "priority_lsms_isa_minimum_batch_raw_value_variable_queue.csv"
FILE_QUEUE_PATH = TEMP_DIR / "priority_lsms_isa_minimum_batch_raw_value_file_queue.csv"
SUMMARY_PATH = RESULT_DIR / "priority_lsms_isa_minimum_batch_raw_value_queue_summary.csv"
REPORT_PATH = REPORT_DIR / "priority_lsms_isa_minimum_batch_raw_value_queue.md"

REQUIREMENT_ORDER = {
    "household_person_keys": 1,
    "weights_and_design": 2,
    "consumption_or_income": 3,
    "oop_health_expenditure": 4,
    "health_need_and_access": 5,
    "survey_timing": 6,
    "climate_geography": 7,
    "missing_codes_units_recall_skip_patterns": 8,
}

REQUIREMENT_QUEUE_COLUMNS = [
    "download_rank",
    "country",
    "wave",
    "idno",
    "requirement_review_order",
    "requirement",
    "requirement_role",
    "candidate_variable_rows",
    "candidate_file_rows",
    "acceptance_core_file_rows",
    "acceptance_core_missing_file_rows",
    "required_checks",
    "acceptance_rule",
    "current_verification_status",
    "minimum_batch_review_status",
    "promotion_effect_if_passed",
    "fill_raw_file_or_archive_member_used",
    "fill_raw_variables_verified",
    "fill_value_label_pass",
    "fill_unit_or_recall_pass",
    "fill_missing_code_pass",
    "fill_skip_pattern_pass",
    "fill_merge_key_or_level_pass",
    "fill_accept_requirement",
    "review_notes",
    "data_write_gate_status",
    "modeling_gate_status",
]

VARIABLE_QUEUE_COLUMNS = [
    "download_rank",
    "country",
    "wave",
    "idno",
    "requirement_review_order",
    "requirement",
    "requirement_role",
    "candidate_rank",
    "file_name",
    "variable_name",
    "variable_label",
    "match_score",
    "current_verification_status",
    "minimum_batch_review_status",
    "fill_raw_file_used",
    "fill_raw_variable_used",
    "fill_variable_label_verified",
    "fill_value_distribution_checked",
    "fill_missing_codes_documented",
    "fill_unit_recall_period_documented",
    "fill_merge_key_or_level_verified",
    "fill_skip_pattern_checked",
    "fill_promote_variable",
    "review_notes",
]

FILE_QUEUE_COLUMNS = [
    "download_rank",
    "country",
    "wave",
    "idno",
    "requirement_review_order",
    "requirement",
    "requirement_role",
    "file_rank",
    "file_name",
    "file_description",
    "candidate_variable_rows",
    "strong_candidate_variable_rows",
    "top_variable_names",
    "acceptance_gate_status",
    "current_file_verification_status",
    "minimum_batch_review_status",
    "fill_file_present_direct_or_archive",
    "fill_file_readable",
    "fill_schema_extracted",
    "fill_required_variables_found",
    "fill_documentation_crosschecked",
    "fill_accept_file_for_requirement",
    "review_notes",
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


def csv_metric(rows: list[dict[str, str]], metric: str, default: str = "0") -> str:
    return next((clean(row.get("value")) for row in rows if clean(row.get("metric")) == metric), default)


def board_by_id(rows: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    return {clean(row.get("idno")): row for row in rows if clean(row.get("idno"))}


def acceptance_requirement_lookup(rows: list[dict[str, str]]) -> dict[tuple[str, str], dict[str, str]]:
    out: dict[tuple[str, str], dict[str, str]] = {}
    for row in rows:
        idno = clean(row.get("idno"))
        requirement = clean(row.get("requirement"))
        if idno and requirement:
            out[(idno, requirement)] = row
    return out


def acceptance_file_lookup(rows: list[dict[str, str]]) -> dict[tuple[str, str], str]:
    out: dict[tuple[str, str], str] = {}
    for row in rows:
        idno = clean(row.get("idno"))
        file_name = clean(row.get("expected_file_name")).lower()
        status = clean(row.get("acceptance_gate_status"))
        if idno and file_name:
            out[(idno, file_name)] = status
    return out


def review_status(status_value: str) -> str:
    if status_value == "ready_for_manual_raw_value_review":
        return "ready_after_package_receipt"
    return "blocked_until_official_raw_package_received"


def sort_key(row: dict[str, str]) -> tuple[int, int, int, str]:
    return (
        safe_int(row.get("download_rank"), 9999),
        safe_int(row.get("requirement_review_order"), 9999),
        safe_int(row.get("candidate_rank") or row.get("file_rank"), 9999),
        clean(row.get("variable_name") or row.get("file_name")),
    )


def build_requirement_queue(
    board_rows: list[dict[str, str]],
    requirement_rows: list[dict[str, str]],
    acceptance_rows: list[dict[str, str]],
) -> list[dict[str, str]]:
    board = board_by_id(board_rows)
    acceptance = acceptance_requirement_lookup(acceptance_rows)
    out: list[dict[str, str]] = []
    for row in requirement_rows:
        idno = clean(row.get("idno"))
        if idno not in board:
            continue
        requirement = clean(row.get("requirement"))
        accept = acceptance.get((idno, requirement), {})
        current_status = clean(row.get("current_verification_status"))
        out.append(
            {
                "download_rank": clean(board[idno].get("download_rank")),
                "country": clean(row.get("country")),
                "wave": clean(row.get("wave")),
                "idno": idno,
                "requirement_review_order": str(REQUIREMENT_ORDER.get(requirement, 999)),
                "requirement": requirement,
                "requirement_role": clean(row.get("requirement_role")),
                "candidate_variable_rows": clean(row.get("candidate_variable_rows")),
                "candidate_file_rows": clean(row.get("candidate_file_rows")),
                "acceptance_core_file_rows": clean(accept.get("core_file_rows")),
                "acceptance_core_missing_file_rows": clean(accept.get("core_missing_file_rows")),
                "required_checks": clean(row.get("required_checks")),
                "acceptance_rule": clean(row.get("acceptance_rule")),
                "current_verification_status": current_status,
                "minimum_batch_review_status": review_status(current_status),
                "promotion_effect_if_passed": clean(row.get("promotion_effect_if_passed")),
                "fill_raw_file_or_archive_member_used": "",
                "fill_raw_variables_verified": "",
                "fill_value_label_pass": "",
                "fill_unit_or_recall_pass": "",
                "fill_missing_code_pass": "",
                "fill_skip_pattern_pass": "",
                "fill_merge_key_or_level_pass": "",
                "fill_accept_requirement": "",
                "review_notes": "",
                "data_write_gate_status": "blocked_no_data_write",
                "modeling_gate_status": "blocked",
            }
        )
    return sorted(out, key=sort_key)


def build_variable_queue(board_rows: list[dict[str, str]], variable_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    board = board_by_id(board_rows)
    out: list[dict[str, str]] = []
    for row in variable_rows:
        idno = clean(row.get("idno"))
        if idno not in board:
            continue
        requirement = clean(row.get("requirement"))
        current_status = clean(row.get("current_verification_status"))
        out.append(
            {
                "download_rank": clean(board[idno].get("download_rank")),
                "country": clean(row.get("country")),
                "wave": clean(row.get("wave")),
                "idno": idno,
                "requirement_review_order": str(REQUIREMENT_ORDER.get(requirement, 999)),
                "requirement": requirement,
                "requirement_role": clean(row.get("requirement_role")),
                "candidate_rank": clean(row.get("candidate_rank")),
                "file_name": clean(row.get("file_name")),
                "variable_name": clean(row.get("variable_name")),
                "variable_label": clean(row.get("variable_label")),
                "match_score": clean(row.get("match_score")),
                "current_verification_status": current_status,
                "minimum_batch_review_status": review_status(current_status),
                "fill_raw_file_used": "",
                "fill_raw_variable_used": "",
                "fill_variable_label_verified": "",
                "fill_value_distribution_checked": "",
                "fill_missing_codes_documented": "",
                "fill_unit_recall_period_documented": "",
                "fill_merge_key_or_level_verified": "",
                "fill_skip_pattern_checked": "",
                "fill_promote_variable": "",
                "review_notes": "",
            }
        )
    return sorted(out, key=sort_key)


def build_file_queue(
    board_rows: list[dict[str, str]],
    file_rows: list[dict[str, str]],
    acceptance_file_rows: list[dict[str, str]],
) -> list[dict[str, str]]:
    board = board_by_id(board_rows)
    acceptance = acceptance_file_lookup(acceptance_file_rows)
    out: list[dict[str, str]] = []
    for row in file_rows:
        idno = clean(row.get("idno"))
        if idno not in board:
            continue
        requirement = clean(row.get("requirement"))
        current_status = clean(row.get("current_file_verification_status"))
        file_name = clean(row.get("file_name"))
        out.append(
            {
                "download_rank": clean(board[idno].get("download_rank")),
                "country": clean(row.get("country")),
                "wave": clean(row.get("wave")),
                "idno": idno,
                "requirement_review_order": str(REQUIREMENT_ORDER.get(requirement, 999)),
                "requirement": requirement,
                "requirement_role": clean(row.get("requirement_role")),
                "file_rank": clean(row.get("file_rank")),
                "file_name": file_name,
                "file_description": clean(row.get("file_description")),
                "candidate_variable_rows": clean(row.get("candidate_variable_rows")),
                "strong_candidate_variable_rows": clean(row.get("strong_candidate_variable_rows")),
                "top_variable_names": clean(row.get("top_variable_names")),
                "acceptance_gate_status": acceptance.get((idno, file_name.lower()), ""),
                "current_file_verification_status": current_status,
                "minimum_batch_review_status": review_status(current_status),
                "fill_file_present_direct_or_archive": "",
                "fill_file_readable": "",
                "fill_schema_extracted": "",
                "fill_required_variables_found": "",
                "fill_documentation_crosschecked": "",
                "fill_accept_file_for_requirement": "",
                "review_notes": "",
            }
        )
    return sorted(out, key=sort_key)


def summary_row(metric: str, value: Any, interpretation: str) -> dict[str, str]:
    return {"metric": metric, "value": str(value), "interpretation": interpretation}


def build_summary(
    board_rows: list[dict[str, str]],
    requirement_rows: list[dict[str, str]],
    variable_rows: list[dict[str, str]],
    file_rows: list[dict[str, str]],
    local_readme_summary: list[dict[str, str]],
) -> list[dict[str, str]]:
    req_status = Counter(row.get("minimum_batch_review_status", "") for row in requirement_rows)
    var_status = Counter(row.get("minimum_batch_review_status", "") for row in variable_rows)
    file_status = Counter(row.get("minimum_batch_review_status", "") for row in file_rows)
    return [
        summary_row("minimum_batch_raw_value_queue_dataset_rows", len(board_rows), "Manual-download packet datasets covered by the raw-value review queue."),
        summary_row("minimum_batch_raw_value_queue_requirement_rows", len(requirement_rows), "Requirement-level raw-value review rows for the 10-packet batch."),
        summary_row("minimum_batch_raw_value_queue_variable_rows", len(variable_rows), "Variable-level raw-value review rows for the 10-packet batch."),
        summary_row("minimum_batch_raw_value_queue_file_rows", len(file_rows), "File-level raw-value review rows for the 10-packet batch."),
        summary_row("minimum_batch_raw_value_queue_blocked_requirement_rows", req_status.get("blocked_until_official_raw_package_received", 0), "Requirement rows blocked until package receipt."),
        summary_row("minimum_batch_raw_value_queue_ready_requirement_rows", req_status.get("ready_after_package_receipt", 0), "Requirement rows ready for manual review after receipt."),
        summary_row("minimum_batch_raw_value_queue_blocked_variable_rows", var_status.get("blocked_until_official_raw_package_received", 0), "Variable rows blocked until package receipt."),
        summary_row("minimum_batch_raw_value_queue_blocked_file_rows", file_status.get("blocked_until_official_raw_package_received", 0), "File rows blocked until package receipt."),
        summary_row("minimum_batch_raw_value_queue_local_target_readmes", csv_metric(local_readme_summary, "local_target_readme_rows", "0"), "Local target readmes generated for this batch."),
        summary_row("data_write_gate_status", "blocked_no_data_write", "The queue is a review checklist only and never writes promoted data."),
        summary_row("modeling_gate_status", "blocked", "No predictive, reduced-form, causal ML, or policy learning until registry thresholds pass."),
    ]


def markdown_table(rows: list[dict[str, str]], columns: list[str], limit: int = 30) -> str:
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


def write_report(requirement_rows: list[dict[str, str]], variable_rows: list[dict[str, str]], file_rows: list[dict[str, str]], summary_rows: list[dict[str, str]]) -> None:
    metric = {row["metric"]: row["value"] for row in summary_rows}
    lines = [
        "# Priority LSMS-ISA Minimum-Batch Raw Value Queue",
        "",
        "Status: executable raw-value review queue for the 10 remaining minimum-batch downloads.",
        "",
        "This queue narrows the full 19-wave workbook to the 10 manual-download packets. It does not verify raw values, promote country-waves, write `data/`, or run models.",
        "",
        "## Summary",
        "",
        f"- Datasets: {metric.get('minimum_batch_raw_value_queue_dataset_rows', '0')}",
        f"- Requirement rows: {metric.get('minimum_batch_raw_value_queue_requirement_rows', '0')}",
        f"- Variable rows: {metric.get('minimum_batch_raw_value_queue_variable_rows', '0')}",
        f"- File rows: {metric.get('minimum_batch_raw_value_queue_file_rows', '0')}",
        f"- Blocked requirement rows: {metric.get('minimum_batch_raw_value_queue_blocked_requirement_rows', '0')}",
        f"- Ready requirement rows: {metric.get('minimum_batch_raw_value_queue_ready_requirement_rows', '0')}",
        f"- Local target readmes: {metric.get('minimum_batch_raw_value_queue_local_target_readmes', '0')}",
        f"- Data-write gate: {metric.get('data_write_gate_status', 'missing')}",
        f"- Modeling gate: {metric.get('modeling_gate_status', 'missing')}",
        "",
        "## Requirement Queue Preview",
        "",
        markdown_table(requirement_rows, ["download_rank", "idno", "requirement_review_order", "requirement", "candidate_variable_rows", "candidate_file_rows", "minimum_batch_review_status"], 35),
        "",
        "## File Queue Preview",
        "",
        markdown_table(file_rows, ["download_rank", "idno", "requirement", "file_rank", "file_name", "acceptance_gate_status", "minimum_batch_review_status"], 35),
        "",
        "## Variable Queue Preview",
        "",
        markdown_table(variable_rows, ["download_rank", "idno", "requirement", "candidate_rank", "file_name", "variable_name", "minimum_batch_review_status"], 35),
    ]
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    ensure_dirs()
    board_rows = read_csv_dicts(BOARD_PATH)
    acceptance_file_rows = read_csv_dicts(ACCEPTANCE_FILE_MATRIX_PATH)
    acceptance_requirement_rows = read_csv_dicts(ACCEPTANCE_REQUIREMENT_MATRIX_PATH)
    local_readme_summary = read_csv_dicts(LOCAL_TARGET_README_SUMMARY_PATH)

    requirement_queue = build_requirement_queue(board_rows, read_csv_dicts(RAW_VALUE_REQUIREMENT_WORKBOOK_PATH), acceptance_requirement_rows)
    variable_queue = build_variable_queue(board_rows, read_csv_dicts(RAW_VALUE_VARIABLE_WORKBOOK_PATH))
    file_queue = build_file_queue(board_rows, read_csv_dicts(RAW_VALUE_FILE_WORKBOOK_PATH), acceptance_file_rows)
    summary_rows = build_summary(board_rows, requirement_queue, variable_queue, file_queue, local_readme_summary)

    write_csv(REQUIREMENT_QUEUE_PATH, requirement_queue, REQUIREMENT_QUEUE_COLUMNS)
    write_csv(VARIABLE_QUEUE_PATH, variable_queue, VARIABLE_QUEUE_COLUMNS)
    write_csv(FILE_QUEUE_PATH, file_queue, FILE_QUEUE_COLUMNS)
    write_csv(SUMMARY_PATH, summary_rows, SUMMARY_COLUMNS)
    write_report(requirement_queue, variable_queue, file_queue, summary_rows)
    append_log(TEMP_DIR / "audit_log.md", f"Built priority LSMS/ISA minimum-batch raw value queue: {len(requirement_queue)} requirements, {len(variable_queue)} variables, {len(file_queue)} files.")


if __name__ == "__main__":
    main()
