from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path
from typing import Any

from common import PROJECT_ROOT, REPORT_DIR, RESULT_DIR, TEMP_DIR, append_log, ensure_dirs, write_csv


PACKET_INDEX_PATH = TEMP_DIR / "priority_lsms_isa_manual_download_packet_index.csv"
PACKET_CORE_PATH = TEMP_DIR / "priority_lsms_isa_manual_download_packet_core_files.csv"
PROGRESS_PATH = TEMP_DIR / "priority_lsms_isa_manual_download_progress_tracker.csv"
POST_DOWNLOAD_SUMMARY_PATH = RESULT_DIR / "priority_lsms_isa_post_download_validation_runner_summary.csv"
THRESHOLD_SUMMARY_PATH = RESULT_DIR / "priority_lsms_isa_threshold_gap_control_panel_summary.csv"

BOARD_PATH = TEMP_DIR / "priority_lsms_isa_manual_download_execution_board.csv"
SUMMARY_PATH = RESULT_DIR / "priority_lsms_isa_manual_download_execution_board_summary.csv"
REPORT_PATH = REPORT_DIR / "priority_lsms_isa_manual_download_execution_board.md"

BOARD_COLUMNS = [
    "download_rank",
    "country",
    "wave",
    "idno",
    "threshold_download_role",
    "official_get_microdata_url",
    "local_target_folder",
    "target_folder_exists",
    "target_file_count",
    "incoming_route_rows",
    "validation_ready",
    "expected_full_file_rows",
    "expected_missing_file_rows",
    "core_file_rows",
    "core_missing_file_rows",
    "requirements_covered",
    "core_file_preview",
    "packet_report_path",
    "progress_status",
    "manual_download_action",
    "post_download_dry_run_command",
    "post_download_execute_command",
    "post_download_runner_mode",
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


def csv_metric(rows: list[dict[str, str]], metric: str, default: str = "") -> str:
    return next((clean(row.get("value")) for row in rows if clean(row.get("metric")) == metric), default)


def resolve_project_path(path_text: str) -> Path:
    text = clean(path_text).replace("\\", "/")
    path = Path(text)
    if path.is_absolute():
        return path
    return PROJECT_ROOT / text


def rows_by_id(rows: list[dict[str, str]], key: str = "idno") -> dict[str, list[dict[str, str]]]:
    grouped: dict[str, list[dict[str, str]]] = {}
    for row in rows:
        grouped.setdefault(clean(row.get(key)), []).append(row)
    return grouped


def core_preview(rows: list[dict[str, str]], limit: int = 12) -> str:
    names: list[str] = []
    for row in rows:
        name = clean(row.get("expected_file_name"))
        if name and name not in names:
            names.append(name)
    return ";".join(names[:limit])


def shell_quote(path_text: str) -> str:
    return "'" + path_text.replace("'", "''") + "'"


def build_board_rows(
    packet_rows: list[dict[str, str]],
    core_rows: list[dict[str, str]],
    progress_rows: list[dict[str, str]],
    post_download_summary_rows: list[dict[str, str]],
) -> list[dict[str, str]]:
    core_by_id = rows_by_id(core_rows)
    progress_by_id = {clean(row.get("idno")): row for row in progress_rows}
    runner_mode = csv_metric(post_download_summary_rows, "post_download_validation_runner_mode", "missing")
    board_rows: list[dict[str, str]] = []
    for packet in sorted(packet_rows, key=lambda r: safe_int(r.get("download_rank"), 9999)):
        idno = clean(packet.get("idno"))
        progress = progress_by_id.get(idno, {})
        target_folder = clean(packet.get("local_target_folder"))
        target_path = resolve_project_path(target_folder)
        progress_status = clean(progress.get("progress_status")) or "missing_progress_tracker"
        validation_ready = "1" if progress_status == "target_files_present_run_validation" and safe_int(progress.get("target_file_count")) > 0 else "0"
        dry_run_command = "python script/178_build_priority_lsms_isa_post_download_validation_runner.py"
        execute_command = "python script/178_build_priority_lsms_isa_post_download_validation_runner.py --execute"
        manual_action = (
            "Open the official get-microdata URL, accept required World Bank terms, download the complete unchanged official package and documentation, "
            f"then place all files under {target_folder}. Verify with: Get-ChildItem -Recurse -File {shell_quote(str(target_path))}"
        )
        board_rows.append(
            {
                "download_rank": clean(packet.get("download_rank")),
                "country": clean(packet.get("country")),
                "wave": clean(packet.get("wave")),
                "idno": idno,
                "threshold_download_role": clean(packet.get("threshold_download_role")),
                "official_get_microdata_url": clean(packet.get("official_get_microdata_url")),
                "local_target_folder": target_folder,
                "target_folder_exists": clean(progress.get("target_folder_exists")) or ("1" if target_path.exists() else "0"),
                "target_file_count": clean(progress.get("target_file_count")) or "0",
                "incoming_route_rows": clean(progress.get("incoming_route_rows")) or "0",
                "validation_ready": validation_ready,
                "expected_full_file_rows": clean(packet.get("expected_full_file_rows")),
                "expected_missing_file_rows": clean(packet.get("expected_missing_file_rows")),
                "core_file_rows": clean(packet.get("core_file_rows")),
                "core_missing_file_rows": clean(packet.get("core_missing_file_rows")),
                "requirements_covered": clean(packet.get("requirements_covered")),
                "core_file_preview": core_preview(core_by_id.get(idno, [])),
                "packet_report_path": clean(packet.get("packet_report_path")),
                "progress_status": progress_status,
                "manual_download_action": manual_action,
                "post_download_dry_run_command": dry_run_command,
                "post_download_execute_command": execute_command,
                "post_download_runner_mode": runner_mode,
                "data_write_gate_status": "blocked_no_data_write",
                "modeling_gate_status": "blocked",
            }
        )
    return board_rows


def summary_row(metric: str, value: Any, interpretation: str) -> dict[str, str]:
    return {"metric": metric, "value": str(value), "interpretation": interpretation}


def build_summary(board_rows: list[dict[str, str]], threshold_summary_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    status_counts = Counter(clean(row.get("progress_status")) for row in board_rows)
    priority_countries = {"Ethiopia", "Nigeria", "Malawi", "Tanzania", "Uganda"}
    rows = [
        summary_row("manual_download_execution_board_rows", len(board_rows), "Manual-download execution rows in the current minimum-threshold board."),
        summary_row("manual_download_execution_board_priority_country_rows", sum(1 for row in board_rows if clean(row.get("country")) in priority_countries), "Rows in the priority Ethiopia/Nigeria/Malawi/Tanzania/Uganda family."),
        summary_row("manual_download_execution_board_sixth_country_rows", sum(1 for row in board_rows if clean(row.get("country")) not in priority_countries), "Rows outside the priority family needed to reach the six-country threshold."),
        summary_row("manual_download_execution_board_target_file_rows", sum(safe_int(row.get("target_file_count")) for row in board_rows), "Files currently present under board target folders."),
        summary_row("manual_download_execution_board_incoming_route_rows", sum(safe_int(row.get("incoming_route_rows")) for row in board_rows), "Incoming router rows currently linked to board targets."),
        summary_row("manual_download_execution_board_validation_ready_rows", sum(safe_int(row.get("validation_ready")) for row in board_rows), "Board rows ready for post-download validation."),
        summary_row("manual_download_execution_board_missing_full_file_rows", sum(safe_int(row.get("expected_missing_file_rows")) for row in board_rows), "Expected official full-file rows still missing across board targets."),
        summary_row("manual_download_execution_board_missing_core_file_rows", sum(safe_int(row.get("core_missing_file_rows")) for row in board_rows), "Requirement-linked core-file rows still missing across board targets."),
        summary_row("manual_download_execution_board_official_url_rows", sum(1 for row in board_rows if clean(row.get("official_get_microdata_url"))), "Board rows with official World Bank get-microdata URLs."),
        summary_row("countries_if_board_passes", csv_metric(threshold_summary_rows, "countries_if_minimum_remaining_passes", "0"), "Country count if the current minimum board passes all promotion gates."),
        summary_row("country_waves_if_board_passes", csv_metric(threshold_summary_rows, "country_waves_if_minimum_remaining_passes", "0"), "Country-wave count if the current minimum board passes all promotion gates."),
        summary_row("data_write_gate_status", "blocked_no_data_write", "The execution board never writes promoted data."),
        summary_row("modeling_gate_status", "blocked", "No predictive, reduced-form, causal ML, or policy learning until registry thresholds pass."),
    ]
    for status, count in sorted(status_counts.items()):
        rows.append(summary_row(f"manual_download_execution_board_status_{status}", count, "Board row count by local acquisition progress status."))
    return rows


def markdown_table(rows: list[dict[str, str]], columns: list[str], limit: int = 30) -> str:
    if not rows:
        return "_No rows._"
    lines = ["| " + " | ".join(columns) + " |", "| " + " | ".join("---" for _ in columns) + " |"]
    for row in rows[:limit]:
        lines.append("| " + " | ".join(clean(row.get(column)).replace("|", "/") for column in columns) + " |")
    if len(rows) > limit:
        lines.append("| " + " | ".join("..." for _ in columns) + " |")
    return "\n".join(lines)


def write_report(board_rows: list[dict[str, str]], summary_rows: list[dict[str, str]]) -> None:
    metric = {row["metric"]: row["value"] for row in summary_rows}
    lines = [
        "# Priority LSMS-ISA Manual Download Execution Board",
        "",
        "Status: one-table execution board for the remaining minimum-threshold",
        "manual downloads. It converts packet URLs, target folders, missing-file",
        "counts, core-file previews, and post-download commands into one checklist.",
        "",
        "It does not download, copy, delete, extract, write promoted `data/`, or run models.",
        "",
        "## Summary",
        "",
        f"- Board rows: {metric.get('manual_download_execution_board_rows', '0')}",
        f"- Priority-country rows: {metric.get('manual_download_execution_board_priority_country_rows', '0')}",
        f"- Sixth-country rows: {metric.get('manual_download_execution_board_sixth_country_rows', '0')}",
        f"- Validation-ready rows: {metric.get('manual_download_execution_board_validation_ready_rows', '0')}",
        f"- Target-folder files now present: {metric.get('manual_download_execution_board_target_file_rows', '0')}",
        f"- Incoming route rows now present: {metric.get('manual_download_execution_board_incoming_route_rows', '0')}",
        f"- Missing full-file rows: {metric.get('manual_download_execution_board_missing_full_file_rows', '0')}",
        f"- Missing core-file rows: {metric.get('manual_download_execution_board_missing_core_file_rows', '0')}",
        f"- Countries if the board passes: {metric.get('countries_if_board_passes', '0')}",
        f"- Country-waves if the board passes: {metric.get('country_waves_if_board_passes', '0')}",
        "",
        "## Execution Board",
        "",
        markdown_table(
            board_rows,
            [
                "download_rank",
                "country",
                "wave",
                "idno",
                "progress_status",
                "target_file_count",
                "expected_missing_file_rows",
                "core_missing_file_rows",
                "official_get_microdata_url",
                "local_target_folder",
            ],
            limit=20,
        ),
        "",
        "## After Files Are Placed",
        "",
        "1. Run `python script/177_build_priority_lsms_isa_manual_download_progress_tracker.py`.",
        "2. Run `python script/178_build_priority_lsms_isa_post_download_validation_runner.py` first as a dry run.",
        "3. If the plan marks a packet ready, run `python script/178_build_priority_lsms_isa_post_download_validation_runner.py --execute`.",
        "4. Refresh the promotion gates only after receipt, schema, value-profile, and semantics checks pass.",
        "",
        "## Outputs",
        "",
        "- `temp/priority_lsms_isa_manual_download_execution_board.csv`",
        "- `result/priority_lsms_isa_manual_download_execution_board_summary.csv`",
        "",
        "## Stop Rule",
        "",
        "This board is an acquisition-control artifact. Each country-wave still needs",
        "complete official-file receipt, raw-value verification, outcome/timing/",
        "geography checks, and accepted CHIRPS or ERA5 climate linkage before any",
        "`data/` write or model rerun.",
    ]
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    ensure_dirs()
    packet_rows = read_csv_dicts(PACKET_INDEX_PATH)
    core_rows = read_csv_dicts(PACKET_CORE_PATH)
    progress_rows = read_csv_dicts(PROGRESS_PATH)
    post_download_summary_rows = read_csv_dicts(POST_DOWNLOAD_SUMMARY_PATH)
    threshold_summary_rows = read_csv_dicts(THRESHOLD_SUMMARY_PATH)
    board_rows = build_board_rows(packet_rows, core_rows, progress_rows, post_download_summary_rows)
    summary_rows = build_summary(board_rows, threshold_summary_rows)
    write_csv(BOARD_PATH, board_rows, BOARD_COLUMNS)
    write_csv(SUMMARY_PATH, summary_rows, SUMMARY_COLUMNS)
    write_report(board_rows, summary_rows)
    append_log(TEMP_DIR / "audit_log.md", f"Built priority LSMS/ISA manual download execution board rows={len(board_rows)}.")
    print(f"Priority LSMS/ISA manual download execution board complete: rows={len(board_rows)}, validation_ready={sum(safe_int(row.get('validation_ready')) for row in board_rows)}")


if __name__ == "__main__":
    main()
