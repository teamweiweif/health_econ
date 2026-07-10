from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

from common import PROJECT_ROOT, REPORT_DIR, RESULT_DIR, TEMP_DIR, append_log, ensure_dirs, write_csv


STARTER_PATH = RESULT_DIR / "priority_lsms_isa_browser_download_starter.csv"
FILE_MATRIX_PATH = TEMP_DIR / "priority_lsms_isa_download_acceptance_file_matrix.csv"
REQUIREMENT_MATRIX_PATH = TEMP_DIR / "priority_lsms_isa_download_acceptance_requirement_matrix.csv"
PROGRESS_PATH = TEMP_DIR / "priority_lsms_isa_manual_download_progress_tracker.csv"

RUNBOOK_PATH = RESULT_DIR / "priority_lsms_isa_first_canary_download_runbook.csv"
CORE_FILE_CHECKLIST_PATH = RESULT_DIR / "priority_lsms_isa_first_canary_core_file_checklist.csv"
REQUIREMENT_GATE_PATH = RESULT_DIR / "priority_lsms_isa_first_canary_requirement_gate_checklist.csv"
SUMMARY_PATH = RESULT_DIR / "priority_lsms_isa_first_canary_runbook_summary.csv"
REPORT_PATH = REPORT_DIR / "priority_lsms_isa_first_canary_runbook.md"

RUNBOOK_COLUMNS = [
    "canary_role",
    "download_rank",
    "country",
    "wave",
    "idno",
    "official_get_microdata_url",
    "credentialed_download_url",
    "local_target_folder",
    "payload_target_path",
    "expected_official_file_rows",
    "expected_unique_core_file_rows",
    "requirement_core_file_rows",
    "requirement_gate_rows",
    "target_file_count",
    "progress_status",
    "browser_open_command",
    "prepare_target_folder_command",
    "open_target_folder_command",
    "python_probe_command",
    "python_execute_command",
    "post_download_runner_dry_run_command",
    "post_download_runner_execute_command",
    "post_download_validation_scope",
    "data_write_gate_status",
    "modeling_gate_status",
    "next_action",
]

CORE_FILE_COLUMNS = [
    "download_rank",
    "country",
    "wave",
    "idno",
    "file_id",
    "expected_file_name",
    "file_description",
    "priority_core_target",
    "core_requirements",
    "core_top_variable_names",
    "current_official_file_match_status",
    "matched_local_locations",
    "acceptance_gate_status",
    "post_download_acceptance_action",
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


def first_canary(starter_rows: list[dict[str, str]]) -> dict[str, str]:
    for row in starter_rows:
        if clean(row.get("canary_role")) == "first_canary":
            return row
    if starter_rows:
        return sorted(starter_rows, key=lambda row: safe_int(row.get("download_rank"), 9999))[0]
    raise SystemExit(f"No starter rows found at {rel(STARTER_PATH)}. Run script/196_build_priority_lsms_isa_browser_download_starter.py first.")


def row_for_id(rows: list[dict[str, str]], idno: str) -> dict[str, str]:
    for row in rows:
        if clean(row.get("idno")) == idno:
            return row
    return {}


def rows_for_id(rows: list[dict[str, str]], idno: str) -> list[dict[str, str]]:
    return [row for row in rows if clean(row.get("idno")) == idno]


def build_outputs() -> tuple[list[dict[str, str]], list[dict[str, str]], list[dict[str, str]], list[dict[str, str]]]:
    starter = first_canary(read_csv_dicts(STARTER_PATH))
    idno = clean(starter.get("idno"))
    progress = row_for_id(read_csv_dicts(PROGRESS_PATH), idno)
    file_rows = rows_for_id(read_csv_dicts(FILE_MATRIX_PATH), idno)
    requirement_rows = rows_for_id(read_csv_dicts(REQUIREMENT_MATRIX_PATH), idno)

    expected_official = len(file_rows)
    core_rows = [row for row in file_rows if clean(row.get("priority_core_target")) == "1"]
    requirement_core_file_rows = sum(safe_int(row.get("core_file_rows")) for row in requirement_rows)
    requirement_missing_core_file_rows = sum(safe_int(row.get("core_missing_file_rows")) for row in requirement_rows)
    target_file_count = safe_int(progress.get("target_file_count"))
    progress_status = clean(progress.get("progress_status")) or "not_refreshed"
    next_action = "open_world_bank_get_microdata_and_place_complete_official_package"
    if target_file_count > 0:
        next_action = "refresh_receipt_and_run_post_download_validation"

    runbook_rows = [
        {
            "canary_role": clean(starter.get("canary_role")),
            "download_rank": clean(starter.get("download_rank")),
            "country": clean(starter.get("country")),
            "wave": clean(starter.get("wave")),
            "idno": idno,
            "official_get_microdata_url": clean(starter.get("official_get_microdata_url")),
            "credentialed_download_url": clean(starter.get("credentialed_download_url")),
            "local_target_folder": clean(starter.get("local_target_folder")),
            "payload_target_path": clean(starter.get("payload_target_path")),
            "expected_official_file_rows": str(expected_official),
            "expected_unique_core_file_rows": str(len(core_rows)),
            "requirement_core_file_rows": str(requirement_core_file_rows),
            "requirement_gate_rows": str(len(requirement_rows)),
            "target_file_count": str(target_file_count),
            "progress_status": progress_status,
            "browser_open_command": clean(starter.get("browser_open_command")),
            "prepare_target_folder_command": clean(starter.get("prepare_target_folder_command")),
            "open_target_folder_command": clean(starter.get("open_target_folder_command")),
            "python_probe_command": clean(starter.get("python_probe_command")),
            "python_execute_command": clean(starter.get("python_execute_command")),
            "post_download_runner_dry_run_command": clean(starter.get("post_download_runner_dry_run_command")),
            "post_download_runner_execute_command": clean(starter.get("post_download_runner_execute_command")),
            "post_download_validation_scope": clean(starter.get("post_download_validation_scope")),
            "data_write_gate_status": "blocked_no_data_write",
            "modeling_gate_status": "blocked",
            "next_action": next_action,
        }
    ]

    core_checklist = [
        {column: clean(row.get(column)) for column in CORE_FILE_COLUMNS}
        for row in sorted(core_rows, key=lambda row: (safe_int(row.get("file_id", "F9999").lstrip("F"), 9999), clean(row.get("expected_file_name"))))
    ]
    requirement_checklist = [
        {column: clean(row.get(column)) for column in REQUIREMENT_COLUMNS}
        for row in sorted(requirement_rows, key=lambda row: clean(row.get("requirement")))
    ]
    missing_core = sum(1 for row in core_checklist if clean(row.get("current_official_file_match_status")) != "matched_expected_official_file")
    blocked_requirements = sum(1 for row in requirement_checklist if clean(row.get("requirement_acceptance_status")).startswith("blocked"))

    summary = [
        {"metric": "first_canary_idno", "value": idno, "interpretation": "IDNO selected as the first manual-download canary."},
        {"metric": "first_canary_country", "value": clean(starter.get("country")), "interpretation": "Country for the first canary."},
        {"metric": "first_canary_wave", "value": clean(starter.get("wave")), "interpretation": "Survey wave for the first canary."},
        {"metric": "first_canary_expected_official_file_rows", "value": str(expected_official), "interpretation": "Official file rows expected from the complete package."},
        {"metric": "first_canary_expected_unique_core_file_rows", "value": str(len(core_rows)), "interpretation": "Unique official core files to check immediately after package placement."},
        {"metric": "first_canary_requirement_core_file_rows", "value": str(requirement_core_file_rows), "interpretation": "Requirement-file linkage rows; one file can support multiple requirements."},
        {"metric": "first_canary_requirement_gate_rows", "value": str(len(requirement_rows)), "interpretation": "Promotion requirement rows covered by this canary."},
        {"metric": "first_canary_missing_unique_core_file_rows", "value": str(missing_core), "interpretation": "Unique core files still missing locally."},
        {"metric": "first_canary_missing_requirement_core_file_rows", "value": str(requirement_missing_core_file_rows), "interpretation": "Requirement-file linkage rows still blocked by missing files."},
        {"metric": "first_canary_blocked_requirement_rows", "value": str(blocked_requirements), "interpretation": "Requirement rows still blocked by missing files."},
        {"metric": "first_canary_target_file_count", "value": str(target_file_count), "interpretation": "Candidate raw files currently present in the target folder."},
        {"metric": "first_canary_progress_status", "value": progress_status, "interpretation": "Manual-download progress status for the canary."},
        {"metric": "data_write_gate_status", "value": "blocked_no_data_write", "interpretation": "This runbook writes only result/report artifacts."},
        {"metric": "modeling_gate_status", "value": "blocked", "interpretation": "No predictive, reduced-form, causal ML, or policy learning is opened."},
    ]
    return runbook_rows, core_checklist, requirement_checklist, summary


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


def write_report(runbook: list[dict[str, str]], core_rows: list[dict[str, str]], requirement_rows: list[dict[str, str]], summary: list[dict[str, str]]) -> None:
    row = runbook[0]
    REPORT_PATH.write_text(
        f"""# Priority LSMS/ISA First Canary Download Runbook

Status: one-wave execution runbook for the first manual-download canary. It
does not download, copy, extract, write promoted `data/`, or run models.

The canary is `{row['idno']}` ({row['country']} {row['wave']}). Use it before
scaling the remaining minimum-batch downloads.

## Summary

{markdown_table(summary, ['metric', 'value', 'interpretation'], 20)}

## Canary Commands

```powershell
{row['prepare_target_folder_command']}
{row['browser_open_command']}
{row['open_target_folder_command']}
```

After accepting World Bank terms and placing the complete unchanged official
package under `{row['local_target_folder']}`, run:

```bash
python script/177_build_priority_lsms_isa_manual_download_progress_tracker.py
{row['python_probe_command']}
{row['python_execute_command']}
{row['post_download_runner_dry_run_command']}
{row['post_download_runner_execute_command']}
```

## Requirement Gates

{markdown_table(requirement_rows, ['requirement', 'core_file_rows', 'core_matched_file_rows', 'core_missing_file_rows', 'requirement_acceptance_status'], 20)}

## Core File Checklist

{markdown_table(core_rows, ['file_id', 'expected_file_name', 'core_requirements', 'current_official_file_match_status', 'acceptance_gate_status'], 50)}

## Outputs

- `{rel(RUNBOOK_PATH)}`
- `{rel(CORE_FILE_CHECKLIST_PATH)}`
- `{rel(REQUIREMENT_GATE_PATH)}`
- `{rel(SUMMARY_PATH)}`

## Stop Rule

Do not write a promoted dataset after the canary download alone. Promotion still
requires receipt, schema, value-profile, semantics, timing/geography, and
climate-linkage gates to pass.
""",
        encoding="utf-8",
    )


def main() -> None:
    ensure_dirs()
    runbook, core_rows, requirement_rows, summary = build_outputs()
    write_csv(RUNBOOK_PATH, runbook, RUNBOOK_COLUMNS)
    write_csv(CORE_FILE_CHECKLIST_PATH, core_rows, CORE_FILE_COLUMNS)
    write_csv(REQUIREMENT_GATE_PATH, requirement_rows, REQUIREMENT_COLUMNS)
    write_csv(SUMMARY_PATH, summary, SUMMARY_COLUMNS)
    write_report(runbook, core_rows, requirement_rows, summary)
    append_log(TEMP_DIR / "audit_log.md", f"Built first canary download runbook idno={runbook[0]['idno']}.")
    print(f"Priority LSMS/ISA first canary runbook complete: idno={runbook[0]['idno']}, core_rows={len(core_rows)}.")


if __name__ == "__main__":
    main()
