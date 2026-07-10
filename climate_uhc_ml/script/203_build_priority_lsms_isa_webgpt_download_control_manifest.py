from __future__ import annotations

import csv
import re
from collections import defaultdict
from pathlib import Path
from typing import Any

from common import REPORT_DIR, RESULT_DIR, TEMP_DIR, append_log, ensure_dirs, write_csv


ROUTE_DECISION_PATH = RESULT_DIR / "priority_lsms_isa_acquisition_route_decision.csv"
BROWSER_STARTER_PATH = RESULT_DIR / "priority_lsms_isa_browser_download_starter.csv"
CREDENTIALED_PACKET_PATH = RESULT_DIR / "priority_lsms_isa_credentialed_fetch_command_packet.csv"
EXECUTION_BOARD_PATH = TEMP_DIR / "priority_lsms_isa_manual_download_execution_board.csv"
SCOPED_INCOMING_PATH = RESULT_DIR / "priority_lsms_isa_scoped_incoming_package_router.csv"
EXPECTED_FILE_MANIFEST_PATH = TEMP_DIR / "priority_lsms_isa_minimum_batch_expected_file_manifest.csv"
CORE_FILE_MANIFEST_PATH = TEMP_DIR / "priority_lsms_isa_minimum_batch_core_file_manifest.csv"

CONTROL_PATH = RESULT_DIR / "priority_lsms_isa_webgpt_download_control_manifest.csv"
CORE_EXPORT_PATH = RESULT_DIR / "priority_lsms_isa_webgpt_expected_core_file_manifest.csv"
SUMMARY_PATH = RESULT_DIR / "priority_lsms_isa_webgpt_download_control_summary.csv"
REPORT_PATH = REPORT_DIR / "priority_lsms_isa_webgpt_download_control_manifest.md"

CONTROL_COLUMNS = [
    "download_rank",
    "country",
    "wave",
    "idno",
    "catalog_id",
    "scope_role",
    "priority_country",
    "sixth_country_candidate",
    "official_get_microdata_url",
    "credentialed_download_url",
    "local_target_folder",
    "browser_open_command",
    "prepare_target_folder_command",
    "open_target_folder_command",
    "python_probe_command",
    "python_execute_command",
    "curl_cookiejar_execute_command",
    "post_download_validation_commands",
    "acquisition_route_decision",
    "incoming_route_status",
    "command_packet_status",
    "session_bootstrap_status",
    "expected_full_file_rows",
    "expected_core_file_rows",
    "target_file_count",
    "incoming_file_rows",
    "requirements_covered",
    "core_file_preview",
    "webgpt_download_status",
    "next_human_action",
    "post_download_success_condition",
    "data_write_gate_status",
    "modeling_gate_status",
]

CORE_COLUMNS = [
    "download_rank",
    "country",
    "wave",
    "idno",
    "catalog_id",
    "requirement",
    "file_rank",
    "file_id",
    "expected_file_name",
    "file_description",
    "candidate_variable_rows",
    "strong_candidate_variable_rows",
    "top_variable_names",
    "local_target_folder",
    "acceptance_check_after_download",
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


def by_id(rows: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    return {clean(row.get("idno")): row for row in rows if clean(row.get("idno"))}


def catalog_id_from_url(*values: str) -> str:
    for value in values:
        match = re.search(r"/catalog/(\d+)", clean(value))
        if match:
            return match.group(1)
    return ""


def grouped_count(rows: list[dict[str, str]], key: str) -> dict[str, int]:
    out: dict[str, int] = defaultdict(int)
    for row in rows:
        idno = clean(row.get(key))
        if idno:
            out[idno] += 1
    return out


def first_nonempty(*values: Any) -> str:
    for value in values:
        text = clean(value)
        if text:
            return text
    return ""


def build_outputs() -> tuple[list[dict[str, str]], list[dict[str, str]], list[dict[str, str]]]:
    route_rows = sorted(read_csv_dicts(ROUTE_DECISION_PATH), key=lambda row: safe_int(row.get("download_rank"), 9999))
    browser_by_id = by_id(read_csv_dicts(BROWSER_STARTER_PATH))
    credentialed_by_id = by_id(read_csv_dicts(CREDENTIALED_PACKET_PATH))
    board_by_id = by_id(read_csv_dicts(EXECUTION_BOARD_PATH))
    incoming_by_id = by_id(read_csv_dicts(SCOPED_INCOMING_PATH))
    expected_rows = read_csv_dicts(EXPECTED_FILE_MANIFEST_PATH)
    core_rows = read_csv_dicts(CORE_FILE_MANIFEST_PATH)
    expected_counts = grouped_count(expected_rows, "idno")
    core_counts = grouped_count(core_rows, "idno")
    route_ids = {clean(row.get("idno")) for row in route_rows if clean(row.get("idno"))}

    controls: list[dict[str, str]] = []
    for route in route_rows:
        idno = clean(route.get("idno"))
        browser = browser_by_id.get(idno, {})
        credentialed = credentialed_by_id.get(idno, {})
        board = board_by_id.get(idno, {})
        incoming = incoming_by_id.get(idno, {})
        official_url = first_nonempty(route.get("official_get_microdata_url"), browser.get("official_get_microdata_url"), credentialed.get("official_get_microdata_url"), board.get("official_get_microdata_url"))
        credentialed_url = first_nonempty(route.get("credentialed_download_url"), browser.get("credentialed_download_url"), credentialed.get("credentialed_download_url"))
        target_folder = first_nonempty(route.get("local_target_folder"), browser.get("local_target_folder"), credentialed.get("local_target_folder"), board.get("local_target_folder"))
        target_file_count = max(
            safe_int(route.get("target_file_count")),
            safe_int(browser.get("target_file_count")),
            safe_int(credentialed.get("target_file_count")),
            safe_int(board.get("target_file_count")),
        )
        incoming_file_rows = safe_int(incoming.get("incoming_file_rows"))
        command_packet_status = clean(credentialed.get("command_packet_status"))
        route_status = clean(incoming.get("route_status"))
        if target_file_count > 0:
            webgpt_status = "local_target_files_present_run_validation"
        elif incoming_file_rows > 0 and route_status == "copy_candidate_to_target_folder_after_review":
            webgpt_status = "incoming_file_candidate_review_and_copy"
        elif command_packet_status == "ready_for_credentialed_download":
            webgpt_status = "credentialed_download_ready"
        else:
            webgpt_status = "browser_manual_terms_acceptance_required"

        controls.append(
            {
                "download_rank": clean(route.get("download_rank")),
                "country": clean(route.get("country")),
                "wave": clean(route.get("wave")),
                "idno": idno,
                "catalog_id": first_nonempty(credentialed.get("catalog_id"), catalog_id_from_url(official_url, credentialed_url)),
                "scope_role": clean(route.get("scope_role")),
                "priority_country": clean(route.get("priority_country")),
                "sixth_country_candidate": clean(route.get("sixth_country_candidate")),
                "official_get_microdata_url": official_url,
                "credentialed_download_url": credentialed_url,
                "local_target_folder": target_folder,
                "browser_open_command": first_nonempty(route.get("browser_open_command"), browser.get("browser_open_command")),
                "prepare_target_folder_command": first_nonempty(route.get("prepare_target_folder_command"), browser.get("prepare_target_folder_command"), credentialed.get("prepare_target_folder_command")),
                "open_target_folder_command": first_nonempty(route.get("open_target_folder_command"), browser.get("open_target_folder_command")),
                "python_probe_command": first_nonempty(route.get("python_probe_command"), browser.get("python_probe_command"), credentialed.get("python_probe_command")),
                "python_execute_command": first_nonempty(route.get("python_execute_command"), browser.get("python_execute_command"), credentialed.get("python_execute_command")),
                "curl_cookiejar_execute_command": clean(credentialed.get("curl_cookiejar_execute_command")),
                "post_download_validation_commands": first_nonempty(route.get("post_download_validation_commands"), browser.get("post_download_validation_commands"), credentialed.get("post_download_validation_commands"), board.get("post_download_execute_command")),
                "acquisition_route_decision": clean(route.get("acquisition_route_decision")),
                "incoming_route_status": route_status,
                "command_packet_status": command_packet_status,
                "session_bootstrap_status": clean(credentialed.get("session_bootstrap_status")),
                "expected_full_file_rows": str(expected_counts.get(idno, safe_int(route.get("expected_full_file_rows")))),
                "expected_core_file_rows": str(core_counts.get(idno, safe_int(route.get("expected_core_file_rows")))),
                "target_file_count": str(target_file_count),
                "incoming_file_rows": str(incoming_file_rows),
                "requirements_covered": clean(board.get("requirements_covered")),
                "core_file_preview": clean(board.get("core_file_preview")),
                "webgpt_download_status": webgpt_status,
                "next_human_action": "Open the official get-microdata URL, accept World Bank terms, download the complete unchanged package, and place it in the local target folder or _incoming.",
                "post_download_success_condition": "Target folder contains the official package/files and post-download receipt, schema, value, semantics, timing/geography, climate-linkage, and promotion gates pass.",
                "data_write_gate_status": "blocked_no_data_write",
                "modeling_gate_status": "blocked",
            }
        )

    control_by_id = by_id(controls)
    core_export: list[dict[str, str]] = []
    for row in sorted(core_rows, key=lambda item: (safe_int(item.get("threshold_sequence_rank"), 9999), clean(item.get("idno")), safe_int(item.get("file_rank"), 9999), clean(item.get("requirement")))):
        idno = clean(row.get("idno"))
        if idno not in route_ids:
            continue
        control = control_by_id.get(idno, {})
        core_export.append(
            {
                "download_rank": clean(control.get("download_rank")) or clean(row.get("threshold_sequence_rank")),
                "country": clean(row.get("country")) or clean(control.get("country")),
                "wave": clean(row.get("wave")) or clean(control.get("wave")),
                "idno": idno,
                "catalog_id": clean(control.get("catalog_id")),
                "requirement": clean(row.get("requirement")),
                "file_rank": clean(row.get("file_rank")),
                "file_id": clean(row.get("file_id")),
                "expected_file_name": clean(row.get("expected_file_name")),
                "file_description": clean(row.get("file_description")),
                "candidate_variable_rows": clean(row.get("candidate_variable_rows")),
                "strong_candidate_variable_rows": clean(row.get("strong_candidate_variable_rows")),
                "top_variable_names": clean(row.get("top_variable_names")),
                "local_target_folder": clean(control.get("local_target_folder")),
                "acceptance_check_after_download": "Confirm this expected core file is present as a direct file or archive member before requirement verification.",
                "data_write_gate_status": "blocked_no_data_write",
                "modeling_gate_status": "blocked",
            }
        )

    countries = {row["country"] for row in controls if row.get("country")}
    status_counts = defaultdict(int)
    for row in controls:
        status_counts[row["webgpt_download_status"]] += 1
    summary = [
        {"metric": "webgpt_download_control_rows", "value": str(len(controls)), "interpretation": "Download-required waves in the Web GPT control manifest."},
        {"metric": "webgpt_download_control_country_rows", "value": str(len(countries)), "interpretation": "Countries covered by the download-required control manifest."},
        {"metric": "webgpt_download_control_priority_country_rows", "value": str(sum(1 for row in controls if row.get("priority_country") == "1")), "interpretation": "Rows from Ethiopia, Nigeria, Malawi, Tanzania, or Uganda."},
        {"metric": "webgpt_download_control_sixth_country_rows", "value": str(sum(1 for row in controls if row.get("sixth_country_candidate") == "1")), "interpretation": "Rows supplying the sixth country in the locked scope."},
        {"metric": "webgpt_download_control_expected_full_file_rows", "value": str(sum(safe_int(row.get("expected_full_file_rows")) for row in controls)), "interpretation": "Expected official file rows across the 10 download-required waves."},
        {"metric": "webgpt_download_control_expected_core_file_rows", "value": str(len(core_export)), "interpretation": "Expected core-file requirement rows exported for direct review."},
        {"metric": "webgpt_download_control_target_file_rows", "value": str(sum(safe_int(row.get("target_file_count")) for row in controls)), "interpretation": "Current files in exact target folders."},
        {"metric": "webgpt_download_control_incoming_file_rows", "value": str(max((safe_int(row.get("incoming_file_rows")) for row in controls), default=0)), "interpretation": "Current files staged under temp/raw_downloads/_incoming."},
        {"metric": "webgpt_download_control_browser_manual_rows", "value": str(status_counts.get("browser_manual_terms_acceptance_required", 0)), "interpretation": "Rows still requiring browser/manual terms acceptance or session material."},
        {"metric": "webgpt_download_control_data_write_status", "value": "blocked_no_data_write", "interpretation": "The download control manifest does not write promoted data."},
        {"metric": "modeling_gate_status", "value": "blocked", "interpretation": "No predictive, reduced-form, causal ML, or policy learning is opened."},
        *[
            {"metric": f"webgpt_download_control_status_{status}", "value": str(count), "interpretation": "Web GPT download control status count."}
            for status, count in sorted(status_counts.items())
        ],
    ]
    return controls, core_export, summary


def markdown_table(rows: list[dict[str, str]], columns: list[str], limit: int = 30) -> str:
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


def write_report(controls: list[dict[str, str]], core_export: list[dict[str, str]], summary: list[dict[str, str]]) -> None:
    REPORT_PATH.write_text(
        f"""# Priority LSMS/ISA Web GPT Download Control Manifest

Status: direct-read acquisition control manifest for the 10 download-required
LSMS/ISA waves in the locked dataset-promotion scope.

This report consolidates the official get-microdata URLs, credentialed
`/download` URLs, local target folders, command packets, incoming-file status,
and expected core-file checks into files under `result/` so a Web GPT reviewer
does not need to infer the download plan from scattered `temp/` artifacts.

It does not download raw files, export credentials, write `data/`, or promote
country-waves. The current stop rule remains: browser/manual World Bank terms
acceptance or session material is required before package receipt validation can
start.

## Summary

{markdown_table(summary, ['metric', 'value', 'interpretation'], 25)}

## Download Control

{markdown_table(controls, ['download_rank', 'country', 'wave', 'idno', 'catalog_id', 'webgpt_download_status', 'expected_core_file_rows', 'target_file_count', 'incoming_file_rows'], 20)}

## Core File Preview

{markdown_table(core_export, ['download_rank', 'idno', 'requirement', 'expected_file_name', 'file_description', 'top_variable_names'], 40)}

## Use Rule

Use `result/priority_lsms_isa_webgpt_download_control_manifest.csv` as the
one-table acquisition control board, and
`result/priority_lsms_isa_webgpt_expected_core_file_manifest.csv` as the
post-download core-file checklist. A country-wave can only move toward
promotion after complete official package receipt and all value, timing,
geography, climate-linkage, and promotion-packet gates pass.
""",
        encoding="utf-8",
    )


def main() -> None:
    ensure_dirs()
    controls, core_export, summary = build_outputs()
    write_csv(CONTROL_PATH, controls, CONTROL_COLUMNS)
    write_csv(CORE_EXPORT_PATH, core_export, CORE_COLUMNS)
    write_csv(SUMMARY_PATH, summary, SUMMARY_COLUMNS)
    write_report(controls, core_export, summary)
    append_log(TEMP_DIR / "audit_log.md", f"Built priority LSMS/ISA Web GPT download control manifest rows={len(controls)} core_rows={len(core_export)}.")
    print(f"Priority LSMS/ISA Web GPT download control rows={len(controls)} core_rows={len(core_export)}.")


if __name__ == "__main__":
    main()
