from __future__ import annotations

import csv
from typing import Any

from common import REPORT_DIR, RESULT_DIR, TEMP_DIR, append_log, ensure_dirs, write_csv


PACKAGE_PATH = RESULT_DIR / "priority_lsms_isa_package_level_download_manifest.csv"
RECEIPT_PATH = RESULT_DIR / "priority_lsms_isa_post_download_receipt_handoff.csv"
LAUNCHPAD_PATH = RESULT_DIR / "priority_lsms_isa_manual_download_launchpad.csv"
SCOPE_LOCK_PATH = RESULT_DIR / "priority_lsms_isa_dataset_scope_lock.csv"
PROMOTION_SUMMARY_PATH = RESULT_DIR / "country_wave_promotion_summary.csv"

BOARD_PATH = RESULT_DIR / "priority_lsms_isa_acquisition_gap_receipt_board.csv"
SUMMARY_PATH = RESULT_DIR / "priority_lsms_isa_acquisition_gap_receipt_summary.csv"
REPORT_PATH = REPORT_DIR / "priority_lsms_isa_acquisition_gap_receipt_board.md"

BOARD_COLUMNS = [
    "download_rank",
    "country",
    "wave",
    "idno",
    "scope_role",
    "first_canary_flag",
    "official_get_microdata_url",
    "credentialed_download_url",
    "local_target_folder",
    "target_file_count",
    "incoming_file_rows",
    "expected_full_file_rows",
    "missing_expected_file_rows",
    "expected_core_file_rows",
    "missing_core_file_rows",
    "unique_core_file_rows",
    "requirement_gate_rows",
    "blocked_requirement_rows",
    "requirements_covered",
    "first_core_file_names",
    "receipt_status",
    "launch_status",
    "next_manual_action",
    "first_validation_command",
    "execute_validation_command",
    "canonical_post_download_sequence",
    "promotion_unlock_condition",
    "threshold_contribution",
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


def csv_value(rows: list[dict[str, str]], metric: str, default: str = "") -> str:
    return next((clean(row.get("value")) for row in rows if clean(row.get("metric")) == metric), default)


def by_id(rows: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    out: dict[str, dict[str, str]] = {}
    for row in rows:
        idno = clean(row.get("idno"))
        if idno and idno not in out:
            out[idno] = row
    return out


def status_for(target_files: int, incoming_files: int, missing_core_files: int) -> str:
    if target_files > 0 and missing_core_files == 0:
        return "local_files_present_core_receipt_ready_for_value_validation"
    if target_files > 0:
        return "local_files_present_receipt_validation_required"
    if incoming_files > 0:
        return "incoming_files_present_route_before_receipt_validation"
    return "blocked_no_local_package_or_incoming_files"


def scope_role_for(row: dict[str, str], scope_by_id: dict[str, dict[str, str]]) -> str:
    idno = clean(row.get("idno"))
    scope_role = clean(scope_by_id.get(idno, {}).get("scope_role"))
    if scope_role:
        return scope_role
    return "download_required_priority_country_wave" if clean(row.get("country")) != "Nepal" else "download_required_sixth_country_candidate"


def threshold_contribution_for(row: dict[str, str], scope_role: str) -> str:
    if scope_role == "download_required_sixth_country_candidate":
        return "adds_sixth_country_buffer_if_value_and_climate_verified"
    if clean(row.get("country")) in {"Ethiopia", "Nigeria", "Tanzania"}:
        return "adds_priority_multi_wave_depth_if_value_and_climate_verified"
    return "adds_priority_country_wave_if_value_and_climate_verified"


def build_board() -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    packages = sorted(read_csv_dicts(PACKAGE_PATH), key=lambda row: safe_int(row.get("download_rank"), 9999))
    receipt_by_id = by_id(read_csv_dicts(RECEIPT_PATH))
    launch_by_id = by_id(read_csv_dicts(LAUNCHPAD_PATH))
    scope_by_id = by_id(read_csv_dicts(SCOPE_LOCK_PATH))
    promotion_summary = read_csv_dicts(PROMOTION_SUMMARY_PATH)

    board: list[dict[str, str]] = []
    for package in packages:
        idno = clean(package.get("idno"))
        receipt = receipt_by_id.get(idno, {})
        launch = launch_by_id.get(idno, {})
        scope_role = scope_role_for(package, scope_by_id)
        target_files = safe_int(package.get("target_file_count"))
        incoming_files = safe_int(package.get("incoming_file_rows"))
        missing_core = safe_int(receipt.get("missing_core_file_rows"), safe_int(package.get("expected_core_file_rows")))
        missing_expected = safe_int(receipt.get("missing_expected_file_rows"), safe_int(package.get("expected_full_file_rows")))
        first_rank = safe_int(package.get("download_rank")) == 1
        receipt_status = status_for(target_files, incoming_files, missing_core)

        board.append(
            {
                "download_rank": clean(package.get("download_rank")),
                "country": clean(package.get("country")),
                "wave": clean(package.get("wave")),
                "idno": idno,
                "scope_role": scope_role,
                "first_canary_flag": "1" if first_rank else "0",
                "official_get_microdata_url": clean(package.get("official_get_microdata_url")),
                "credentialed_download_url": clean(package.get("credentialed_download_url")),
                "local_target_folder": clean(package.get("local_target_folder")),
                "target_file_count": str(target_files),
                "incoming_file_rows": str(incoming_files),
                "expected_full_file_rows": clean(package.get("expected_full_file_rows")),
                "missing_expected_file_rows": str(missing_expected),
                "expected_core_file_rows": clean(package.get("expected_core_file_rows")),
                "missing_core_file_rows": str(missing_core),
                "unique_core_file_rows": clean(package.get("unique_core_file_rows")),
                "requirement_gate_rows": clean(package.get("expected_requirement_gate_rows")),
                "blocked_requirement_rows": clean(package.get("blocked_requirement_gate_rows")),
                "requirements_covered": clean(package.get("requirements_covered")),
                "first_core_file_names": clean(package.get("first_core_file_names")),
                "receipt_status": receipt_status,
                "launch_status": clean(launch.get("launch_status")),
                "next_manual_action": "open_official_page_accept_terms_download_complete_package_then_place_under_target_or_incoming",
                "first_validation_command": clean(receipt.get("first_validation_command")),
                "execute_validation_command": clean(receipt.get("execute_validation_command")),
                "canonical_post_download_sequence": clean(receipt.get("canonical_post_download_sequence")),
                "promotion_unlock_condition": clean(receipt.get("promotion_unlock_condition")),
                "threshold_contribution": threshold_contribution_for(package, scope_role),
                "data_write_gate_status": "blocked_no_data_write",
                "modeling_gate_status": "blocked",
            }
        )

    countries = {row["country"] for row in board if row.get("country")}
    target_file_rows = sum(safe_int(row.get("target_file_count")) for row in board)
    incoming_file_rows = max((safe_int(row.get("incoming_file_rows")) for row in board), default=0)
    missing_package_rows = sum(1 for row in board if row.get("receipt_status") == "blocked_no_local_package_or_incoming_files")
    local_or_incoming_rows = len(board) - missing_package_rows
    blocked_requirement_rows = sum(safe_int(row.get("blocked_requirement_rows")) for row in board)
    missing_core_rows = sum(safe_int(row.get("missing_core_file_rows")) for row in board)
    missing_expected_rows = sum(safe_int(row.get("missing_expected_file_rows")) for row in board)
    current_promoted_rows = csv_value(promotion_summary, "promoted_analysis_ready_rows", "0")
    current_promoted_countries = csv_value(promotion_summary, "financial_protection_ready_countries", "0")
    current_double_failure_waves = csv_value(promotion_summary, "double_failure_ready_country_waves", "0")
    current_climate_ready_rows = csv_value(promotion_summary, "accepted_chirps_era5_climate_linkage_rows", "0")

    summary = [
        {"metric": "acquisition_gap_receipt_board_rows", "value": str(len(board)), "interpretation": "Download-required package rows in the acquisition gap and receipt board."},
        {"metric": "acquisition_gap_receipt_country_rows", "value": str(len(countries)), "interpretation": "Countries covered by the remaining package-download board."},
        {"metric": "current_promoted_analysis_ready_rows", "value": current_promoted_rows, "interpretation": "Currently promoted analysis-ready rows from the registry before these downloads."},
        {"metric": "current_financial_protection_ready_countries", "value": current_promoted_countries, "interpretation": "Current countries with value-verified financial-protection readiness."},
        {"metric": "current_double_failure_ready_country_waves", "value": current_double_failure_waves, "interpretation": "Current value-verified double-failure-ready country-waves."},
        {"metric": "current_accepted_climate_linkage_rows", "value": current_climate_ready_rows, "interpretation": "Current accepted CHIRPS/ERA5 climate-linkage rows."},
        {"metric": "target_financial_protection_ready_countries", "value": "6", "interpretation": "Goal threshold before modeling can resume."},
        {"metric": "target_double_failure_ready_country_waves", "value": "10", "interpretation": "Goal threshold before modeling can resume."},
        {"metric": "target_accepted_climate_linkage_rows", "value": "1", "interpretation": "Minimum climate-linkage threshold; more rows still need country-wave linkage for final data."},
        {"metric": "remaining_financial_country_gap", "value": str(max(0, 6 - safe_int(current_promoted_countries))), "interpretation": "Countries still needed before modeling can resume."},
        {"metric": "remaining_double_failure_wave_gap", "value": str(max(0, 10 - safe_int(current_double_failure_waves))), "interpretation": "Country-waves still needed before modeling can resume."},
        {"metric": "acquisition_gap_expected_full_file_rows", "value": str(sum(safe_int(row.get("expected_full_file_rows")) for row in board)), "interpretation": "Expected official file rows across the remaining download packages."},
        {"metric": "acquisition_gap_missing_expected_file_rows", "value": str(missing_expected_rows), "interpretation": "Expected official file rows currently missing."},
        {"metric": "acquisition_gap_expected_core_file_rows", "value": str(sum(safe_int(row.get("expected_core_file_rows")) for row in board)), "interpretation": "Requirement-linked core file rows across the remaining download packages."},
        {"metric": "acquisition_gap_missing_core_file_rows", "value": str(missing_core_rows), "interpretation": "Requirement-linked core file rows currently missing."},
        {"metric": "acquisition_gap_requirement_gate_rows", "value": str(sum(safe_int(row.get("requirement_gate_rows")) for row in board)), "interpretation": "Receipt-level requirement gates represented in the board."},
        {"metric": "acquisition_gap_blocked_requirement_rows", "value": str(blocked_requirement_rows), "interpretation": "Requirement gates still blocked by missing local packages/core files."},
        {"metric": "acquisition_gap_target_file_rows", "value": str(target_file_rows), "interpretation": "Files currently present under exact target folders."},
        {"metric": "acquisition_gap_incoming_file_rows", "value": str(incoming_file_rows), "interpretation": "Files currently staged under temp/raw_downloads/_incoming."},
        {"metric": "acquisition_gap_missing_package_rows", "value": str(missing_package_rows), "interpretation": "Download-required package rows with no local package or incoming file."},
        {"metric": "acquisition_gap_local_or_incoming_package_rows", "value": str(local_or_incoming_rows), "interpretation": "Rows with at least one local target or incoming candidate file."},
        {"metric": "acquisition_gap_first_canary_idno", "value": board[0]["idno"] if board else "", "interpretation": "First package to download and validate before scaling the batch."},
        {"metric": "data_write_gate_status", "value": "blocked_no_data_write", "interpretation": "This board does not write promoted data."},
        {"metric": "modeling_gate_status", "value": "blocked", "interpretation": "No predictive, reduced-form, causal ML, or policy learning is opened."},
    ]
    return board, summary


def markdown_table(rows: list[dict[str, str]], columns: list[str], limit: int = 30) -> str:
    if not rows:
        return "_No rows._"
    lines = ["| " + " | ".join(columns) + " |", "| " + " | ".join("---" for _ in columns) + " |"]
    for row in rows[:limit]:
        values: list[str] = []
        for column in columns:
            value = clean(row.get(column)).replace("|", "/")
            if len(value) > 100:
                value = value[:97] + "..."
            values.append(value)
        lines.append("| " + " | ".join(values) + " |")
    if len(rows) > limit:
        lines.append(f"| ... | ... | ... | ... | ... | ... | ... | ... | ... | ... | ... | ... |")
    return "\n".join(lines)


def write_report(board: list[dict[str, str]], summary: list[dict[str, str]]) -> None:
    summary_by_metric = {row["metric"]: row["value"] for row in summary}
    lines = [
        "# Priority LSMS/ISA Acquisition Gap Receipt Board",
        "",
        "Status: single execution board for the remaining locked World Bank raw-package downloads.",
        "",
        "This board reconciles the manual launchpad, package-level manifest, post-download receipt handoff, and promotion-threshold gap. It does not download files, move files, extract archives, write `data/`, or open any modeling gate.",
        "",
        "## Summary",
        "",
        markdown_table(summary, ["metric", "value", "interpretation"], limit=40),
        "",
        "## Threshold Gap",
        "",
        f"- Current promoted analysis-ready rows: {summary_by_metric.get('current_promoted_analysis_ready_rows', '0')}.",
        f"- Current financial-protection-ready countries: {summary_by_metric.get('current_financial_protection_ready_countries', '0')} of 6.",
        f"- Current double-failure-ready country-waves: {summary_by_metric.get('current_double_failure_ready_country_waves', '0')} of 10.",
        f"- Remaining financial country gap: {summary_by_metric.get('remaining_financial_country_gap', '0')}.",
        f"- Remaining double-failure wave gap: {summary_by_metric.get('remaining_double_failure_wave_gap', '0')}.",
        f"- Remaining download-required packages in this board: {summary_by_metric.get('acquisition_gap_missing_package_rows', '0')}.",
        "",
        "## Download And Receipt Board",
        "",
        markdown_table(
            board,
            [
                "download_rank",
                "country",
                "wave",
                "idno",
                "scope_role",
                "first_canary_flag",
                "target_file_count",
                "incoming_file_rows",
                "expected_full_file_rows",
                "missing_expected_file_rows",
                "expected_core_file_rows",
                "missing_core_file_rows",
                "receipt_status",
            ],
            limit=20,
        ),
        "",
        "## Execution Rule",
        "",
        "Download the first canary package first, place the complete unchanged official package under its target folder or under `_incoming`, then run the row-specific validation commands before scaling to the remaining packages.",
        "",
        "## Stop Rule",
        "",
        "A package receipt is not a promoted dataset. A country-wave can enter `data/` only after official package receipt, schema, raw value, semantics, timing/geography, climate-linkage, and promotion-packet gates all pass. Modeling stays blocked until the registry reaches 6 value-verified countries and 10 value-verified country-waves.",
    ]
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    ensure_dirs()
    board, summary = build_board()
    write_csv(BOARD_PATH, board, BOARD_COLUMNS)
    write_csv(SUMMARY_PATH, summary, SUMMARY_COLUMNS)
    write_report(board, summary)
    append_log(TEMP_DIR / "audit_log.md", f"Built priority LSMS/ISA acquisition gap receipt board rows={len(board)}.")
    print(f"Priority LSMS/ISA acquisition gap receipt board rows={len(board)}.")


if __name__ == "__main__":
    main()
