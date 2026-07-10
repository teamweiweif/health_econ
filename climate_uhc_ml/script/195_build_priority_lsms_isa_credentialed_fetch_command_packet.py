from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

from common import PROJECT_ROOT, REPORT_DIR, RESULT_DIR, TEMP_DIR, append_log, ensure_dirs, write_csv


BOOTSTRAP_PATH = RESULT_DIR / "priority_lsms_isa_worldbank_session_bootstrap.csv"
COMMAND_PACKET_PATH = RESULT_DIR / "priority_lsms_isa_credentialed_fetch_command_packet.csv"
SUMMARY_PATH = RESULT_DIR / "priority_lsms_isa_credentialed_fetch_command_packet_summary.csv"
REPORT_PATH = REPORT_DIR / "priority_lsms_isa_credentialed_fetch_command_packet.md"

COOKIE_PATH = TEMP_DIR / "private" / "worldbank_session_cookies.txt"

PACKET_COLUMNS = [
    "download_rank",
    "country",
    "wave",
    "idno",
    "catalog_id",
    "command_packet_status",
    "session_bootstrap_status",
    "official_get_microdata_url",
    "credentialed_download_url",
    "local_target_folder",
    "payload_target_path",
    "expected_core_file_rows",
    "target_file_count",
    "cookie_file_present",
    "header_file_present",
    "manual_browser_action",
    "prepare_target_folder_command",
    "python_probe_command",
    "python_execute_command",
    "curl_cookiejar_execute_command",
    "post_download_validation_commands",
    "data_write_gate_status",
    "modeling_gate_status",
]
SUMMARY_COLUMNS = ["metric", "value", "interpretation"]


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


def read_csv_dicts(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(PROJECT_ROOT)).replace("\\", "/")
    except ValueError:
        return str(path).replace("\\", "/")


def local_payload_path(row: dict[str, str]) -> str:
    idno = clean(row.get("idno"))
    folder = clean(row.get("local_target_folder")).strip("/")
    if not folder:
        folder = f"temp/raw_downloads/{idno}"
    return f"{folder}/_credentialed_payloads/{idno}_worldbank_download_payload.bin"


def packet_status(row: dict[str, str]) -> str:
    status = clean(row.get("session_bootstrap_status"))
    if status == "local_files_ready_skip_session_bootstrap":
        return "local_files_ready_run_post_download_validation"
    if status == "session_material_present_ready_for_probe":
        return "ready_to_probe_with_local_session"
    if status == "session_material_present_needs_review":
        return "blocked_session_file_format_needs_review"
    return "blocked_missing_worldbank_session"


def build_outputs() -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    bootstrap_rows = read_csv_dicts(BOOTSTRAP_PATH)
    rows: list[dict[str, str]] = []

    for row in sorted(bootstrap_rows, key=lambda r: safe_int(r.get("download_rank"), 9999)):
        idno = clean(row.get("idno"))
        payload_path = local_payload_path(row)
        payload_folder = str(Path(payload_path).parent).replace("\\", "/")
        download_url = clean(row.get("credentialed_download_url"))
        rows.append(
            {
                "download_rank": clean(row.get("download_rank")),
                "country": clean(row.get("country")),
                "wave": clean(row.get("wave")),
                "idno": idno,
                "catalog_id": clean(row.get("catalog_id")),
                "command_packet_status": packet_status(row),
                "session_bootstrap_status": clean(row.get("session_bootstrap_status")),
                "official_get_microdata_url": clean(row.get("official_get_microdata_url")),
                "credentialed_download_url": download_url,
                "local_target_folder": clean(row.get("local_target_folder")),
                "payload_target_path": payload_path,
                "expected_core_file_rows": clean(row.get("expected_core_file_rows")),
                "target_file_count": clean(row.get("target_file_count")),
                "cookie_file_present": clean(row.get("cookie_file_present")),
                "header_file_present": clean(row.get("header_file_present")),
                "manual_browser_action": "Open the official get-microdata URL while logged in, accept terms, then either download manually into the local target folder or export a cookie jar to temp/private/worldbank_session_cookies.txt.",
                "prepare_target_folder_command": f"New-Item -ItemType Directory -Force -Path {payload_folder}",
                "python_probe_command": "python script/180_build_priority_lsms_isa_credentialed_download_handoff.py --probe",
                "python_execute_command": "python script/180_build_priority_lsms_isa_credentialed_download_handoff.py --execute",
                "curl_cookiejar_execute_command": f"curl.exe --location --fail --cookie {rel(COOKIE_PATH)} --output {payload_path} {download_url}",
                "post_download_validation_commands": clean(row.get("post_download_validation_commands")),
                "data_write_gate_status": "blocked_no_data_write",
                "modeling_gate_status": "blocked",
            }
        )

    status_counts: dict[str, int] = {}
    for row in rows:
        status = row["command_packet_status"]
        status_counts[status] = status_counts.get(status, 0) + 1

    countries = sorted({clean(row.get("country")) for row in rows if clean(row.get("country"))})
    expected_core_file_rows = sum(safe_int(row.get("expected_core_file_rows")) for row in rows)
    target_file_count = sum(safe_int(row.get("target_file_count")) for row in rows)
    ready_rows = status_counts.get("ready_to_probe_with_local_session", 0)
    missing_session_rows = status_counts.get("blocked_missing_worldbank_session", 0)

    summary = [
        {"metric": "credentialed_fetch_command_packet_rows", "value": str(len(rows)), "interpretation": "Minimum-batch credentialed download command rows."},
        {"metric": "credentialed_fetch_command_packet_countries", "value": str(len(countries)), "interpretation": "Distinct countries covered by the command packet."},
        {"metric": "credentialed_fetch_command_packet_country_list", "value": "; ".join(countries), "interpretation": "Countries covered by the command packet."},
        {"metric": "credentialed_fetch_command_packet_expected_core_file_rows", "value": str(expected_core_file_rows), "interpretation": "Expected core raw-file rows that would be checked after package receipt."},
        {"metric": "credentialed_fetch_command_packet_target_file_count", "value": str(target_file_count), "interpretation": "Existing non-generated target files currently found before download."},
        {"metric": "credentialed_fetch_command_packet_ready_to_probe_rows", "value": str(ready_rows), "interpretation": "Rows ready for credentialed probing with local session material."},
        {"metric": "credentialed_fetch_command_packet_missing_session_rows", "value": str(missing_session_rows), "interpretation": "Rows blocked because temp/private session material is absent."},
        {"metric": "data_write_gate_status", "value": "blocked_no_data_write", "interpretation": "This packet writes only result/report artifacts and does not promote datasets."},
        {"metric": "modeling_gate_status", "value": "blocked", "interpretation": "No predictive, reduced-form, causal ML, or policy learning is opened."},
    ]
    for status_name, count in sorted(status_counts.items()):
        summary.append({"metric": f"credentialed_fetch_command_packet_status_{status_name}", "value": str(count), "interpretation": "Command packet status count."})
    return rows, summary


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


def write_report(rows: list[dict[str, str]], summary: list[dict[str, str]]) -> None:
    REPORT_PATH.write_text(
        f"""# Priority LSMS/ISA Credentialed Fetch Command Packet

This packet turns the current minimum-batch World Bank Microdata download
board into per-wave fetch commands and post-download validation commands. It
does not download raw packages and does not include any cookie or header
values.

Local credential material, if used, must stay in `temp/private/`:

- `{rel(COOKIE_PATH)}`: Netscape cookie jar exported from a logged-in World Bank Microdata browser session.

The safer Python route is still `script/180_build_priority_lsms_isa_credentialed_download_handoff.py`,
because it checks response headers before saving raw payloads. The `curl.exe`
commands are included only as a cookie-jar fallback for cases where the browser
export is already a Netscape-format cookie file.

## Summary

{markdown_table(summary, ['metric', 'value', 'interpretation'], 20)}

## Command Rows

{markdown_table(rows, ['download_rank', 'country', 'wave', 'idno', 'command_packet_status', 'credentialed_download_url', 'payload_target_path'], 12)}

## Run Order

1. Log in to World Bank Microdata in a browser and accept the official terms for the target survey.
2. Export browser cookies to `{rel(COOKIE_PATH)}` or manually place the downloaded official raw package into the listed local target folder.
3. Run `python script/180_build_priority_lsms_isa_credentialed_download_handoff.py --probe`.
4. Run `python script/180_build_priority_lsms_isa_credentialed_download_handoff.py --execute` only if the probe confirms downloadable raw payloads.
5. Re-run the post-download validation command chain listed for the downloaded wave.

Data writes remain blocked until receipt, schema, value-profile, semantics,
timing/geography, and climate-linkage gates pass.
""",
        encoding="utf-8",
    )


def main() -> None:
    ensure_dirs()
    rows, summary = build_outputs()
    write_csv(COMMAND_PACKET_PATH, rows, PACKET_COLUMNS)
    write_csv(SUMMARY_PATH, summary, SUMMARY_COLUMNS)
    write_report(rows, summary)
    append_log(TEMP_DIR / "audit_log.md", f"Built priority LSMS/ISA credentialed fetch command packet rows={len(rows)}.")
    print(f"Priority LSMS/ISA credentialed fetch command packet rows={len(rows)}.")


if __name__ == "__main__":
    main()
