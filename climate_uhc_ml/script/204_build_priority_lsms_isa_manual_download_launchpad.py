from __future__ import annotations

import csv
import html
from collections import defaultdict
from pathlib import Path
from typing import Any

from common import REPORT_DIR, RESULT_DIR, TEMP_DIR, append_log, ensure_dirs, write_csv


CONTROL_PATH = RESULT_DIR / "priority_lsms_isa_webgpt_download_control_manifest.csv"

LAUNCHPAD_PATH = RESULT_DIR / "priority_lsms_isa_manual_download_launchpad.csv"
SUMMARY_PATH = RESULT_DIR / "priority_lsms_isa_manual_download_launchpad_summary.csv"
REPORT_PATH = REPORT_DIR / "priority_lsms_isa_manual_download_launchpad.md"
HTML_PATH = REPORT_DIR / "priority_lsms_isa_manual_download_launchpad.html"

LAUNCHPAD_COLUMNS = [
    "launch_rank",
    "canary_role",
    "country",
    "wave",
    "idno",
    "catalog_id",
    "official_get_microdata_url",
    "credentialed_download_url",
    "local_target_folder",
    "expected_full_file_rows",
    "expected_core_file_rows",
    "target_file_count",
    "incoming_file_rows",
    "requirements_covered",
    "launch_status",
    "open_target_folder_command",
    "prepare_target_folder_command",
    "python_probe_command",
    "python_execute_command",
    "post_download_validation_commands",
    "manual_placement_rule",
    "post_download_success_condition",
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


def html_escape(value: Any) -> str:
    return html.escape(clean(value), quote=True)


def launch_status(row: dict[str, str]) -> str:
    if safe_int(row.get("target_file_count")) > 0:
        return "target_files_present_run_validation"
    if safe_int(row.get("incoming_file_rows")) > 0:
        return "incoming_files_present_review_router"
    return "open_official_page_accept_terms_download_package"


def build_outputs() -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    control_rows = sorted(read_csv_dicts(CONTROL_PATH), key=lambda row: safe_int(row.get("download_rank"), 9999))
    launch_rows: list[dict[str, str]] = []
    for idx, row in enumerate(control_rows, start=1):
        idno = clean(row.get("idno"))
        canary_role = "first_canary" if idx == 1 else "follow_after_first_canary_passes"
        target = clean(row.get("local_target_folder"))
        launch_rows.append(
            {
                "launch_rank": str(idx),
                "canary_role": canary_role,
                "country": clean(row.get("country")),
                "wave": clean(row.get("wave")),
                "idno": idno,
                "catalog_id": clean(row.get("catalog_id")),
                "official_get_microdata_url": clean(row.get("official_get_microdata_url")),
                "credentialed_download_url": clean(row.get("credentialed_download_url")),
                "local_target_folder": target,
                "expected_full_file_rows": clean(row.get("expected_full_file_rows")),
                "expected_core_file_rows": clean(row.get("expected_core_file_rows")),
                "target_file_count": clean(row.get("target_file_count")),
                "incoming_file_rows": clean(row.get("incoming_file_rows")),
                "requirements_covered": clean(row.get("requirements_covered")),
                "launch_status": launch_status(row),
                "open_target_folder_command": clean(row.get("open_target_folder_command")),
                "prepare_target_folder_command": clean(row.get("prepare_target_folder_command")),
                "python_probe_command": clean(row.get("python_probe_command")),
                "python_execute_command": clean(row.get("python_execute_command")),
                "post_download_validation_commands": clean(row.get("post_download_validation_commands")),
                "manual_placement_rule": f"Download the complete unchanged official package after accepting World Bank terms, then place all files under {target} or temporarily under temp/raw_downloads/_incoming.",
                "post_download_success_condition": clean(row.get("post_download_success_condition")),
                "data_write_gate_status": "blocked_no_data_write",
                "modeling_gate_status": "blocked",
            }
        )

    countries = {row["country"] for row in launch_rows if row.get("country")}
    status_counts: dict[str, int] = defaultdict(int)
    for row in launch_rows:
        status_counts[row["launch_status"]] += 1
    summary = [
        {"metric": "manual_download_launchpad_rows", "value": str(len(launch_rows)), "interpretation": "Manual-download launchpad rows for the locked download-required waves."},
        {"metric": "manual_download_launchpad_country_rows", "value": str(len(countries)), "interpretation": "Countries covered by the launchpad."},
        {"metric": "manual_download_launchpad_priority_country_rows", "value": str(sum(1 for row in launch_rows if row.get("country") in {"Ethiopia", "Nigeria", "Malawi", "Tanzania", "Uganda"})), "interpretation": "Rows from priority countries."},
        {"metric": "manual_download_launchpad_sixth_country_rows", "value": str(sum(1 for row in launch_rows if row.get("country") not in {"Ethiopia", "Nigeria", "Malawi", "Tanzania", "Uganda"})), "interpretation": "Rows supplying the sixth country."},
        {"metric": "manual_download_launchpad_expected_full_file_rows", "value": str(sum(safe_int(row.get("expected_full_file_rows")) for row in launch_rows)), "interpretation": "Expected official file rows across launchpad targets."},
        {"metric": "manual_download_launchpad_expected_core_file_rows", "value": str(sum(safe_int(row.get("expected_core_file_rows")) for row in launch_rows)), "interpretation": "Expected core-file rows across launchpad targets."},
        {"metric": "manual_download_launchpad_target_file_rows", "value": str(sum(safe_int(row.get("target_file_count")) for row in launch_rows)), "interpretation": "Files currently present under exact target folders."},
        {"metric": "manual_download_launchpad_incoming_file_rows", "value": str(max((safe_int(row.get("incoming_file_rows")) for row in launch_rows), default=0)), "interpretation": "Files currently staged under temp/raw_downloads/_incoming."},
        {"metric": "manual_download_launchpad_open_official_page_rows", "value": str(status_counts.get("open_official_page_accept_terms_download_package", 0)), "interpretation": "Rows still requiring official page opening, terms acceptance, and package placement."},
        {"metric": "manual_download_launchpad_html_written", "value": "1", "interpretation": "Whether the clickable HTML launchpad was written."},
        {"metric": "data_write_gate_status", "value": "blocked_no_data_write", "interpretation": "The launchpad writes only acquisition-control artifacts."},
        {"metric": "modeling_gate_status", "value": "blocked", "interpretation": "No predictive, reduced-form, causal ML, or policy learning is opened."},
        *[
            {"metric": f"manual_download_launchpad_status_{status}", "value": str(count), "interpretation": "Manual-download launchpad status count."}
            for status, count in sorted(status_counts.items())
        ],
    ]
    return launch_rows, summary


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


def write_markdown(launch_rows: list[dict[str, str]], summary: list[dict[str, str]]) -> None:
    REPORT_PATH.write_text(
        f"""# Priority LSMS/ISA Manual Download Launchpad

Status: clickable manual-download launchpad for the 10 locked download-required
World Bank LSMS/ISA waves.

Use the HTML launchpad at `report/priority_lsms_isa_manual_download_launchpad.html`
to open official get-microdata pages and copy local target-folder paths. This
artifact does not download raw data, export credentials, write `data/`, or
promote country-waves.

## Summary

{markdown_table(summary, ['metric', 'value', 'interpretation'], 25)}

## Launch Rows

{markdown_table(launch_rows, ['launch_rank', 'canary_role', 'country', 'wave', 'idno', 'catalog_id', 'launch_status', 'expected_core_file_rows', 'target_file_count'], 20)}

## Commands

{markdown_table(launch_rows, ['launch_rank', 'idno', 'prepare_target_folder_command', 'open_target_folder_command', 'python_probe_command'], 20)}

## Stop Rule

Opening a page or placing files only starts package receipt validation. A wave
can only move toward promoted data after receipt, schema, value, semantics,
timing/geography, climate-linkage, and promotion-packet gates pass.
""",
        encoding="utf-8",
    )


def write_html(launch_rows: list[dict[str, str]], summary: list[dict[str, str]]) -> None:
    rows_html = []
    for row in launch_rows:
        rows_html.append(
            f"""
            <tr>
              <td>{html_escape(row['launch_rank'])}</td>
              <td><strong>{html_escape(row['country'])}</strong><br><span>{html_escape(row['wave'])}</span></td>
              <td><code>{html_escape(row['idno'])}</code><br><span>Catalog {html_escape(row['catalog_id'])}</span></td>
              <td><a href="{html_escape(row['official_get_microdata_url'])}" target="_blank" rel="noreferrer">Open official page</a><br><a href="{html_escape(row['credentialed_download_url'])}" target="_blank" rel="noreferrer">Credentialed download URL</a></td>
              <td><code>{html_escape(row['local_target_folder'])}</code><br><span>{html_escape(row['launch_status'])}</span></td>
              <td>{html_escape(row['expected_core_file_rows'])}</td>
              <td><code>{html_escape(row['python_probe_command'])}</code></td>
            </tr>
            """.strip()
        )

    summary_items = "\n".join(
        f"<li><strong>{html_escape(row['metric'])}</strong>: {html_escape(row['value'])}</li>"
        for row in summary
        if row.get("metric") in {
            "manual_download_launchpad_rows",
            "manual_download_launchpad_country_rows",
            "manual_download_launchpad_expected_core_file_rows",
            "manual_download_launchpad_open_official_page_rows",
            "data_write_gate_status",
            "modeling_gate_status",
        }
    )
    HTML_PATH.write_text(
        f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Priority LSMS/ISA Manual Download Launchpad</title>
  <style>
    :root {{
      color-scheme: light;
      --ink: #17202a;
      --muted: #53616f;
      --line: #c8d1d9;
      --bg: #f7f9fb;
      --panel: #ffffff;
      --accent: #0b6bcb;
    }}
    body {{
      margin: 0;
      font-family: Arial, Helvetica, sans-serif;
      color: var(--ink);
      background: var(--bg);
      font-size: 14px;
      line-height: 1.45;
    }}
    header {{
      padding: 24px 28px 14px;
      border-bottom: 1px solid var(--line);
      background: var(--panel);
    }}
    h1 {{
      margin: 0 0 8px;
      font-size: 24px;
      font-weight: 700;
      letter-spacing: 0;
    }}
    main {{
      padding: 18px 28px 28px;
    }}
    .summary {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
      gap: 8px 18px;
      margin: 0 0 18px;
      padding: 0;
      list-style: none;
    }}
    .summary li {{
      border-bottom: 1px solid var(--line);
      padding: 6px 0;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      background: var(--panel);
      table-layout: fixed;
    }}
    th, td {{
      border: 1px solid var(--line);
      padding: 8px;
      vertical-align: top;
      word-break: break-word;
    }}
    th {{
      text-align: left;
      background: #eaf2f8;
      font-weight: 700;
    }}
    code {{
      font-family: Consolas, Menlo, monospace;
      font-size: 12px;
    }}
    a {{
      color: var(--accent);
    }}
    span {{
      color: var(--muted);
      font-size: 12px;
    }}
    .note {{
      margin: 0 0 16px;
      max-width: 980px;
      color: var(--muted);
    }}
  </style>
</head>
<body>
  <header>
    <h1>Priority LSMS/ISA Manual Download Launchpad</h1>
    <p class="note">Open the official World Bank page, accept terms, download the complete unchanged package, and place it in the listed local target folder. This page stores no credentials and no raw data.</p>
  </header>
  <main>
    <ul class="summary">
      {summary_items}
    </ul>
    <table>
      <thead>
        <tr>
          <th>Rank</th>
          <th>Wave</th>
          <th>IDNO</th>
          <th>Links</th>
          <th>Target</th>
          <th>Core Files</th>
          <th>Probe Command</th>
        </tr>
      </thead>
      <tbody>
        {''.join(rows_html)}
      </tbody>
    </table>
  </main>
</body>
</html>
""",
        encoding="utf-8",
    )


def main() -> None:
    ensure_dirs()
    launch_rows, summary = build_outputs()
    write_csv(LAUNCHPAD_PATH, launch_rows, LAUNCHPAD_COLUMNS)
    write_csv(SUMMARY_PATH, summary, SUMMARY_COLUMNS)
    write_markdown(launch_rows, summary)
    write_html(launch_rows, summary)
    append_log(TEMP_DIR / "audit_log.md", f"Built priority LSMS/ISA manual download launchpad rows={len(launch_rows)}.")
    print(f"Priority LSMS/ISA manual download launchpad rows={len(launch_rows)}.")


if __name__ == "__main__":
    main()
