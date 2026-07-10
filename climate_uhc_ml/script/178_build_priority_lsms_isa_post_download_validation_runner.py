from __future__ import annotations

import argparse
import csv
import subprocess
import sys
from pathlib import Path
from typing import Any

from common import PROJECT_ROOT, REPORT_DIR, RESULT_DIR, TEMP_DIR, append_log, ensure_dirs, write_csv


PROGRESS_PATH = TEMP_DIR / "priority_lsms_isa_manual_download_progress_tracker.csv"

RUN_PLAN_PATH = TEMP_DIR / "priority_lsms_isa_post_download_validation_run_plan.csv"
COMMAND_LOG_PATH = TEMP_DIR / "priority_lsms_isa_post_download_validation_command_log.csv"
SUMMARY_PATH = RESULT_DIR / "priority_lsms_isa_post_download_validation_runner_summary.csv"
REPORT_PATH = REPORT_DIR / "priority_lsms_isa_post_download_validation_runner.md"

RUN_PLAN_COLUMNS = [
    "download_rank",
    "country",
    "wave",
    "idno",
    "progress_status",
    "target_file_count",
    "validation_ready",
    "runner_decision",
    "command_rank",
    "command",
    "validation_command_scope",
    "execute_command",
    "local_target_folder",
    "packet_report_path",
]

COMMAND_LOG_COLUMNS = [
    "idno",
    "command_rank",
    "command",
    "attempted",
    "returncode",
    "stdout_tail",
    "stderr_tail",
]

SUMMARY_COLUMNS = ["metric", "value", "interpretation"]

READY_STATUS = "target_files_present_run_validation"
VALIDATION_COMMAND_ALLOWLIST = {
    "script/150_build_priority_lsms_isa_raw_package_receipt_checklist.py",
    "script/153_validate_priority_lsms_isa_official_file_receipt.py",
    "script/157_build_priority_lsms_isa_received_raw_schema_audit.py",
    "script/158_build_priority_lsms_isa_received_raw_value_profile.py",
    "script/159_build_priority_lsms_isa_received_raw_semantics_review.py",
}
VALIDATION_COMMAND_SCOPE = "batch_rebuild_after_selected_packet_ready"


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


def split_commands(command_text: str) -> list[str]:
    return [clean(part) for part in clean(command_text).split(";") if clean(part)]


def allowed_command(command: str) -> bool:
    parts = command.split()
    if len(parts) != 2:
        return False
    interpreter, script_path = parts
    return interpreter == "python" and script_path in VALIDATION_COMMAND_ALLOWLIST


def build_run_plan(progress_rows: list[dict[str, str]], execute: bool) -> list[dict[str, str]]:
    plan_rows: list[dict[str, str]] = []
    for progress in sorted(progress_rows, key=lambda r: safe_int(r.get("download_rank"), 9999)):
        ready = clean(progress.get("progress_status")) == READY_STATUS and safe_int(progress.get("target_file_count")) > 0
        commands = split_commands(progress.get("post_download_validation_commands", ""))
        if not commands:
            commands = [""]
        for command_rank, command in enumerate(commands, start=1):
            allowed = bool(command) and allowed_command(command)
            decision = "execute_validation_command" if ready and execute and allowed else "dry_run_or_not_ready"
            if ready and not allowed:
                decision = "blocked_unapproved_command"
            elif ready and not execute:
                decision = "ready_dry_run_requires_execute_flag"
            elif not ready:
                decision = "blocked_packet_not_validation_ready"
            plan_rows.append(
                {
                    "download_rank": clean(progress.get("download_rank")),
                    "country": clean(progress.get("country")),
                    "wave": clean(progress.get("wave")),
                    "idno": clean(progress.get("idno")),
                    "progress_status": clean(progress.get("progress_status")),
                    "target_file_count": clean(progress.get("target_file_count")),
                    "validation_ready": "1" if ready else "0",
                    "runner_decision": decision,
                    "command_rank": str(command_rank),
                    "command": command,
                    "validation_command_scope": VALIDATION_COMMAND_SCOPE if command else "",
                    "execute_command": "1" if decision == "execute_validation_command" else "0",
                    "local_target_folder": clean(progress.get("local_target_folder")),
                    "packet_report_path": clean(progress.get("packet_report_path")),
                }
            )
    return plan_rows


def tail(text: str, limit: int = 500) -> str:
    text = clean(text)
    if len(text) <= limit:
        return text
    return text[-limit:]


def execute_plan(plan_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    logs: list[dict[str, str]] = []
    for row in plan_rows:
        command = clean(row.get("command"))
        should_execute = clean(row.get("execute_command")) == "1"
        log_row = {
            "idno": clean(row.get("idno")),
            "command_rank": clean(row.get("command_rank")),
            "command": command,
            "attempted": "1" if should_execute else "0",
            "returncode": "",
            "stdout_tail": "",
            "stderr_tail": "",
        }
        if should_execute:
            proc = subprocess.run(
                command.split(),
                cwd=PROJECT_ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            log_row["returncode"] = str(proc.returncode)
            log_row["stdout_tail"] = tail(proc.stdout)
            log_row["stderr_tail"] = tail(proc.stderr)
        logs.append(log_row)
    return logs


def summary_row(metric: str, value: Any, interpretation: str) -> dict[str, str]:
    return {"metric": metric, "value": str(value), "interpretation": interpretation}


def build_summary(
    progress_rows: list[dict[str, str]],
    plan_rows: list[dict[str, str]],
    command_logs: list[dict[str, str]],
    execute: bool,
    progress_row_count_before_filter: int,
    filter_description: str,
) -> list[dict[str, str]]:
    ready_packets = {clean(row.get("idno")) for row in progress_rows if clean(row.get("progress_status")) == READY_STATUS and safe_int(row.get("target_file_count")) > 0}
    execute_commands = [row for row in plan_rows if clean(row.get("execute_command")) == "1"]
    attempted = [row for row in command_logs if clean(row.get("attempted")) == "1"]
    failed = [row for row in attempted if clean(row.get("returncode")) not in {"", "0"}]
    return [
        summary_row("post_download_validation_runner_mode", "execute" if execute else "dry_run", "Runner mode for this invocation."),
        summary_row("post_download_validation_runner_filter", filter_description, "Subset filter used for this invocation."),
        summary_row("post_download_validation_progress_rows_before_filter", progress_row_count_before_filter, "Progress rows available before optional filtering."),
        summary_row("post_download_validation_progress_packet_rows", len(progress_rows), "Manual-download progress rows considered by the runner."),
        summary_row("post_download_validation_ready_packet_rows", len(ready_packets), "Packets with local target files ready for validation."),
        summary_row("post_download_validation_plan_rows", len(plan_rows), "Command-plan rows written by the runner."),
        summary_row("post_download_validation_command_scope", VALIDATION_COMMAND_SCOPE, "Allowlisted validation scripts rebuild canonical batch audit outputs after selected packets are ready."),
        summary_row("post_download_validation_execute_command_rows", len(execute_commands), "Validation commands selected for execution."),
        summary_row("post_download_validation_attempted_command_rows", len(attempted), "Validation commands attempted in this invocation."),
        summary_row("post_download_validation_failed_command_rows", len(failed), "Attempted validation commands with nonzero return codes."),
        summary_row("data_write_gate_status", "blocked_no_data_write", "Post-download validation runner does not write promoted data."),
        summary_row("modeling_gate_status", "blocked", "No predictive, reduced-form, causal ML, or policy learning until registry thresholds pass."),
    ]


def markdown_table(rows: list[dict[str, str]], columns: list[str], limit: int = 30) -> str:
    if not rows:
        return "_No rows._"
    lines = ["| " + " | ".join(columns) + " |", "| " + " | ".join("---" for _ in columns) + " |"]
    for row in rows[:limit]:
        lines.append("| " + " | ".join(clean(row.get(column)).replace("|", "/") for column in columns) + " |")
    if len(rows) > limit:
        lines.append("| " + " | ".join("..." for _ in columns) + " |")
    return "\n".join(lines)


def write_report(summary_rows: list[dict[str, str]], plan_rows: list[dict[str, str]]) -> None:
    metric = {row["metric"]: row["value"] for row in summary_rows}
    lines = [
        "# Priority LSMS-ISA Post-Download Validation Runner",
        "",
        "Status: safe runner plan for post-download receipt, schema, value-profile,",
        "and semantics checks. Default mode is dry-run. Use `--execute` only after",
        "official raw package files are present in packet target folders.",
        "",
        "It does not download, copy, delete, extract, write promoted `data/`, or run models.",
        "`--idno` restricts which packet can trigger the runner; the allowlisted",
        "validation scripts rebuild the canonical batch audit outputs.",
        "",
        "## Summary",
        "",
        f"- Mode: {metric.get('post_download_validation_runner_mode', 'dry_run')}",
        f"- Filter: {metric.get('post_download_validation_runner_filter', 'all')}",
        f"- Progress rows before filter: {metric.get('post_download_validation_progress_rows_before_filter', '0')}",
        f"- Progress packets considered: {metric.get('post_download_validation_progress_packet_rows', '0')}",
        f"- Validation-ready packets: {metric.get('post_download_validation_ready_packet_rows', '0')}",
        f"- Plan rows: {metric.get('post_download_validation_plan_rows', '0')}",
        f"- Command scope: {metric.get('post_download_validation_command_scope', VALIDATION_COMMAND_SCOPE)}",
        f"- Execute command rows: {metric.get('post_download_validation_execute_command_rows', '0')}",
        f"- Attempted commands: {metric.get('post_download_validation_attempted_command_rows', '0')}",
        f"- Failed commands: {metric.get('post_download_validation_failed_command_rows', '0')}",
        "",
        "## Run Plan Preview",
        "",
        markdown_table(
            plan_rows,
            [
                "download_rank",
                "idno",
                "progress_status",
                "target_file_count",
                "runner_decision",
                "command_rank",
                "command",
                "validation_command_scope",
            ],
            limit=30,
        ),
        "",
        "## Outputs",
        "",
        "- `temp/priority_lsms_isa_post_download_validation_run_plan.csv`",
        "- `temp/priority_lsms_isa_post_download_validation_command_log.csv`",
        "- `result/priority_lsms_isa_post_download_validation_runner_summary.csv`",
        "",
        "## Commands",
        "",
        "```bash",
        "python script/178_build_priority_lsms_isa_post_download_validation_runner.py",
        "python script/178_build_priority_lsms_isa_post_download_validation_runner.py --idno ETH_2021_ESPS-W5_v02_M",
        "python script/178_build_priority_lsms_isa_post_download_validation_runner.py --idno ETH_2021_ESPS-W5_v02_M --execute",
        "```",
        "",
        "## Stop Rule",
        "",
        "The runner only handles post-download validation scripts. Data writes and",
        "models remain blocked until promoted registry thresholds pass.",
    ]
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build or execute the priority LSMS/ISA post-download validation run plan.")
    parser.add_argument("--execute", action="store_true", help="Execute allowlisted validation commands for packets with target files present.")
    parser.add_argument("--idno", action="append", default=[], help="Restrict to one IDNO; repeat to include several target waves.")
    return parser.parse_args()


def filter_progress_rows(progress_rows: list[dict[str, str]], idnos: list[str]) -> tuple[list[dict[str, str]], str]:
    wanted = {clean(idno) for idno in idnos if clean(idno)}
    if not wanted:
        return progress_rows, "all"
    selected = [row for row in progress_rows if clean(row.get("idno")) in wanted]
    if not selected:
        available = ", ".join(clean(row.get("idno")) for row in progress_rows[:20])
        raise SystemExit(f"No rows matched --idno {', '.join(sorted(wanted))}. Available examples: {available}")
    return selected, "idno=" + ";".join(sorted(wanted))


def main() -> None:
    args = parse_args()
    ensure_dirs()
    progress_rows = read_csv_dicts(PROGRESS_PATH)
    selected_rows, filter_description = filter_progress_rows(progress_rows, args.idno)
    plan_rows = build_run_plan(selected_rows, execute=args.execute)
    command_logs = execute_plan(plan_rows)
    summary_rows = build_summary(
        selected_rows,
        plan_rows,
        command_logs,
        execute=args.execute,
        progress_row_count_before_filter=len(progress_rows),
        filter_description=filter_description,
    )
    write_csv(RUN_PLAN_PATH, plan_rows, RUN_PLAN_COLUMNS)
    write_csv(COMMAND_LOG_PATH, command_logs, COMMAND_LOG_COLUMNS)
    write_csv(SUMMARY_PATH, summary_rows, SUMMARY_COLUMNS)
    write_report(summary_rows, plan_rows)
    append_log(TEMP_DIR / "audit_log.md", f"Built priority LSMS/ISA post-download validation runner plan filter={filter_description}.")
    print(
        "Priority LSMS/ISA post-download validation runner complete: "
        f"mode={'execute' if args.execute else 'dry_run'}, "
        f"filter={filter_description}, "
        f"ready_packets={next((row['value'] for row in summary_rows if row['metric'] == 'post_download_validation_ready_packet_rows'), '0')}, "
        f"execute_commands={next((row['value'] for row in summary_rows if row['metric'] == 'post_download_validation_execute_command_rows'), '0')}"
    )
    failed = next((row["value"] for row in summary_rows if row["metric"] == "post_download_validation_failed_command_rows"), "0")
    if failed != "0":
        sys.exit(1)


if __name__ == "__main__":
    main()
