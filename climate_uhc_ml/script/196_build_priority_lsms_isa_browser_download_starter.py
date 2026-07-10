from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

from common import PROJECT_ROOT, REPORT_DIR, RESULT_DIR, TEMP_DIR, append_log, ensure_dirs, write_csv


COMMAND_PACKET_PATH = RESULT_DIR / "priority_lsms_isa_credentialed_fetch_command_packet.csv"
STARTER_PATH = RESULT_DIR / "priority_lsms_isa_browser_download_starter.csv"
SUMMARY_PATH = RESULT_DIR / "priority_lsms_isa_browser_download_starter_summary.csv"
REPORT_PATH = REPORT_DIR / "priority_lsms_isa_browser_download_starter.md"
POWERSHELL_STARTER_PATH = TEMP_DIR / "priority_lsms_isa_browser_download_starter.ps1"

PRIORITY_COUNTRIES = {"Ethiopia", "Nigeria", "Malawi", "Tanzania", "Uganda"}
POST_DOWNLOAD_VALIDATION_SCOPE = "selected_idno_triggers_batch_rebuild"

STARTER_COLUMNS = [
    "download_rank",
    "canary_sequence_rank",
    "canary_role",
    "country",
    "wave",
    "idno",
    "official_get_microdata_url",
    "credentialed_download_url",
    "local_target_folder",
    "payload_target_path",
    "expected_core_file_rows",
    "target_file_count",
    "browser_open_command",
    "prepare_target_folder_command",
    "open_target_folder_command",
    "python_probe_command",
    "python_execute_command",
    "post_download_runner_dry_run_command",
    "post_download_runner_execute_command",
    "post_download_validation_scope",
    "post_download_validation_commands",
    "starter_status",
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


def ps_quote(value: str) -> str:
    return "'" + value.replace("'", "''") + "'"


def build_outputs() -> tuple[list[dict[str, str]], list[dict[str, str]], str]:
    command_rows = read_csv_dicts(COMMAND_PACKET_PATH)
    rows: list[dict[str, str]] = []

    sorted_rows = sorted(command_rows, key=lambda row: safe_int(row.get("download_rank"), 9999))
    for idx, row in enumerate(sorted_rows, start=1):
        idno = clean(row.get("idno"))
        country = clean(row.get("country"))
        url = clean(row.get("official_get_microdata_url"))
        target = clean(row.get("local_target_folder")).rstrip("/")
        payload = clean(row.get("payload_target_path"))
        canary_role = "first_canary" if idx == 1 else "follow_after_first_canary_passes"
        starter_status = "ready_for_browser_terms_acceptance" if url and target else "needs_review_missing_url_or_target"
        rows.append(
            {
                "download_rank": clean(row.get("download_rank")),
                "canary_sequence_rank": str(idx),
                "canary_role": canary_role,
                "country": country,
                "wave": clean(row.get("wave")),
                "idno": idno,
                "official_get_microdata_url": url,
                "credentialed_download_url": clean(row.get("credentialed_download_url")),
                "local_target_folder": target + "/" if target else "",
                "payload_target_path": payload,
                "expected_core_file_rows": clean(row.get("expected_core_file_rows")),
                "target_file_count": clean(row.get("target_file_count")),
                "browser_open_command": f"Start-Process {ps_quote(url)}",
                "prepare_target_folder_command": f"New-Item -ItemType Directory -Force -Path {ps_quote(target)}",
                "open_target_folder_command": f"Invoke-Item {ps_quote(target)}",
                "python_probe_command": clean(row.get("python_probe_command")),
                "python_execute_command": clean(row.get("python_execute_command")),
                "post_download_runner_dry_run_command": f"python script/178_build_priority_lsms_isa_post_download_validation_runner.py --idno {idno}",
                "post_download_runner_execute_command": f"python script/178_build_priority_lsms_isa_post_download_validation_runner.py --idno {idno} --execute",
                "post_download_validation_scope": POST_DOWNLOAD_VALIDATION_SCOPE,
                "post_download_validation_commands": clean(row.get("post_download_validation_commands")),
                "starter_status": starter_status,
                "data_write_gate_status": "blocked_no_data_write",
                "modeling_gate_status": "blocked",
            }
        )

    priority_country_rows = sum(1 for row in rows if row["country"] in PRIORITY_COUNTRIES)
    sixth_country_rows = len(rows) - priority_country_rows
    target_file_count = sum(safe_int(row.get("target_file_count")) for row in rows)
    expected_core_files = sum(safe_int(row.get("expected_core_file_rows")) for row in rows)
    ready_rows = sum(1 for row in rows if row["starter_status"] == "ready_for_browser_terms_acceptance")
    first_canary = next((row["idno"] for row in rows if row["canary_role"] == "first_canary"), "")

    summary = [
        {"metric": "browser_download_starter_rows", "value": str(len(rows)), "interpretation": "Minimum-batch rows covered by the browser download starter."},
        {"metric": "browser_download_starter_ready_rows", "value": str(ready_rows), "interpretation": "Rows with both official URL and local target folder commands."},
        {"metric": "browser_download_starter_priority_country_rows", "value": str(priority_country_rows), "interpretation": "Rows from Ethiopia, Nigeria, Malawi, Tanzania, or Uganda."},
        {"metric": "browser_download_starter_sixth_country_rows", "value": str(sixth_country_rows), "interpretation": "Rows included to meet the sixth-country threshold."},
        {"metric": "browser_download_starter_expected_core_file_rows", "value": str(expected_core_files), "interpretation": "Core raw-file rows expected after the packages are placed."},
        {"metric": "browser_download_starter_target_file_count", "value": str(target_file_count), "interpretation": "Existing target-folder files before browser/manual download."},
        {"metric": "browser_download_starter_first_canary_idno", "value": first_canary, "interpretation": "First wave to try before scaling the browser/manual download workflow."},
        {"metric": "post_download_validation_scope", "value": POST_DOWNLOAD_VALIDATION_SCOPE, "interpretation": "The per-IDNO runner command gates execution on one packet, while downstream validation scripts rebuild canonical batch outputs."},
        {"metric": "browser_download_starter_local_ps1_path", "value": rel(POWERSHELL_STARTER_PATH), "interpretation": "Local helper script generated under temp; not intended for Git commit."},
        {"metric": "data_write_gate_status", "value": "blocked_no_data_write", "interpretation": "This starter writes only command artifacts and a temp helper script, not promoted data."},
        {"metric": "modeling_gate_status", "value": "blocked", "interpretation": "No predictive, reduced-form, causal ML, or policy learning is opened."},
    ]
    return rows, summary, first_canary


def write_powershell_starter(rows: list[dict[str, str]]) -> None:
    lines = [
        "param(",
        "    [string]$Idno = ''",
        ")",
        "",
        "$Rows = @(",
    ]
    for row in rows:
        lines.extend(
            [
                "    [pscustomobject]@{",
                f"        Idno = {ps_quote(row['idno'])}",
                f"        Country = {ps_quote(row['country'])}",
                f"        Wave = {ps_quote(row['wave'])}",
                f"        Url = {ps_quote(row['official_get_microdata_url'])}",
                f"        Target = {ps_quote(row['local_target_folder'].rstrip('/'))}",
                f"        Probe = {ps_quote(row['python_probe_command'])}",
                f"        Execute = {ps_quote(row['python_execute_command'])}",
                f"        ValidationDryRun = {ps_quote(row['post_download_runner_dry_run_command'])}",
                f"        ValidationExecute = {ps_quote(row['post_download_runner_execute_command'])}",
                "    }",
            ]
        )
    lines.extend(
        [
            ")",
            "",
            "$Selected = if ($Idno) { $Rows | Where-Object { $_.Idno -eq $Idno } } else { $Rows }",
            "if (-not $Selected) { throw \"No starter row matched Idno '$Idno'.\" }",
            "",
            "foreach ($Row in $Selected) {",
            "    New-Item -ItemType Directory -Force -Path $Row.Target | Out-Null",
            "    Write-Host \"Opening World Bank page for $($Row.Idno): $($Row.Url)\"",
            "    Start-Process $Row.Url",
            "    Write-Host \"Target folder: $($Row.Target)\"",
            "    Write-Host \"After accepting terms or placing files, run:\"",
            "    Write-Host \"  $($Row.Probe)\"",
            "    Write-Host \"  $($Row.Execute)\"",
            "    Write-Host \"After files are present, run:\"",
            "    Write-Host \"  $($Row.ValidationDryRun)\"",
            "    Write-Host \"  $($Row.ValidationExecute)\"",
            "}",
            "",
        ]
    )
    POWERSHELL_STARTER_PATH.parent.mkdir(parents=True, exist_ok=True)
    POWERSHELL_STARTER_PATH.write_text("\n".join(lines), encoding="utf-8")


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


def write_report(rows: list[dict[str, str]], summary: list[dict[str, str]], first_canary: str) -> None:
    REPORT_PATH.write_text(
        f"""# Priority LSMS/ISA Browser Download Starter

This starter is a local browser/manual-download bridge for the 10 remaining
minimum-batch World Bank Microdata packages. It does not download files by
itself, does not include credentials, and does not write promoted data.

It generates a local helper script:

- `{rel(POWERSHELL_STARTER_PATH)}`

Use the first canary before scaling the workflow:

```powershell
powershell -ExecutionPolicy Bypass -File {rel(POWERSHELL_STARTER_PATH)} -Idno {first_canary}
```

After a package is downloaded or manually placed in the target folder, run the
per-IDNO probe/execute and post-download validation commands listed below.

## Summary

{markdown_table(summary, ['metric', 'value', 'interpretation'], 20)}

## Starter Rows

{markdown_table(rows, ['canary_sequence_rank', 'canary_role', 'country', 'wave', 'idno', 'starter_status', 'local_target_folder', 'python_probe_command'], 12)}

## Per-Wave Validation Runner

{markdown_table(rows, ['canary_sequence_rank', 'idno', 'post_download_runner_dry_run_command', 'post_download_runner_execute_command', 'post_download_validation_scope'], 12)}

The `--idno` runner commands are canary gates. Once the selected packet has
official raw files, the downstream validation scripts rebuild the canonical
batch receipt, schema, value-profile, and semantics outputs.

## Stop Rule

This starter only helps place official raw packages. Promotion remains blocked
until receipt, schema, value-profile, semantics, timing/geography, and
climate-linkage gates pass for a country-wave.
""",
        encoding="utf-8",
    )


def main() -> None:
    ensure_dirs()
    rows, summary, first_canary = build_outputs()
    write_powershell_starter(rows)
    write_csv(STARTER_PATH, rows, STARTER_COLUMNS)
    write_csv(SUMMARY_PATH, summary, SUMMARY_COLUMNS)
    write_report(rows, summary, first_canary)
    append_log(TEMP_DIR / "audit_log.md", f"Built priority LSMS/ISA browser download starter rows={len(rows)}.")
    print(f"Priority LSMS/ISA browser download starter rows={len(rows)}.")


if __name__ == "__main__":
    main()
