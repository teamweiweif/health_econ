from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

from common import PROJECT_ROOT, REPORT_DIR, RESULT_DIR, TEMP_DIR, append_log, ensure_dirs, write_csv


UNLOCK_BOARD_PATH = RESULT_DIR / "priority_lsms_isa_minimum_batch_promotion_unlock_board.csv"
CREDENTIALED_PLAN_PATH = TEMP_DIR / "priority_lsms_isa_credentialed_download_handoff_plan.csv"
SESSION_DIR = TEMP_DIR / "private"
COOKIE_PATH = SESSION_DIR / "worldbank_session_cookies.txt"
HEADER_PATH = SESSION_DIR / "worldbank_session_headers.txt"

BOOTSTRAP_PATH = RESULT_DIR / "priority_lsms_isa_worldbank_session_bootstrap.csv"
SUMMARY_PATH = RESULT_DIR / "priority_lsms_isa_worldbank_session_bootstrap_summary.csv"
REPORT_PATH = REPORT_DIR / "priority_lsms_isa_worldbank_session_bootstrap.md"

BOOTSTRAP_COLUMNS = [
    "download_rank",
    "country",
    "wave",
    "idno",
    "catalog_id",
    "session_bootstrap_status",
    "official_get_microdata_url",
    "credentialed_download_url",
    "local_target_folder",
    "cookie_file_present",
    "cookie_file_bytes",
    "cookie_file_format_status",
    "header_file_present",
    "header_file_bytes",
    "header_file_format_status",
    "unlock_status",
    "public_documentation_receipt_status",
    "expected_core_file_rows",
    "target_file_count",
    "probe_command",
    "execute_command",
    "safe_session_instruction",
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


def index_by_idno(rows: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    out: dict[str, dict[str, str]] = {}
    for row in rows:
        idno = clean(row.get("idno"))
        if idno and idno not in out:
            out[idno] = row
    return out


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(PROJECT_ROOT)).replace("\\", "/")
    except ValueError:
        return str(path).replace("\\", "/")


def file_bytes(path: Path) -> int:
    return path.stat().st_size if path.exists() and path.is_file() else 0


def cookie_format_status(path: Path) -> str:
    if not path.exists():
        return "missing"
    text = path.read_text(encoding="utf-8", errors="ignore").strip()
    if not text:
        return "present_empty"
    first_lines = [line.strip() for line in text.splitlines()[:5] if line.strip()]
    lowered = "\n".join(first_lines).lower()
    if "cookie:" in lowered:
        return "present_cookie_header_format"
    if "# netscape http cookie file" in lowered or any("\t" in line for line in first_lines):
        return "present_netscape_cookie_file_format"
    if "=" in text and ";" in text:
        return "present_raw_cookie_pairs_format"
    return "present_unrecognized_cookie_format_review_before_probe"


def header_format_status(path: Path) -> str:
    if not path.exists():
        return "missing"
    lines = [line.strip() for line in path.read_text(encoding="utf-8", errors="ignore").splitlines() if line.strip()]
    if not lines:
        return "present_empty"
    header_lines = [line for line in lines if ":" in line and not line.startswith("#")]
    if not header_lines:
        return "present_no_header_lines_review_before_probe"
    cookie_lines = [line for line in header_lines if line.lower().startswith("cookie:")]
    if cookie_lines:
        return "present_header_lines_with_cookie_review_or_move_cookie_to_cookie_file"
    return "present_header_lines_no_cookie_values"


def catalog_id_from_download_url(url: str) -> str:
    parts = clean(url).split("/catalog/")
    if len(parts) < 2:
        return ""
    return parts[1].split("/", 1)[0]


def build_outputs() -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    unlock_rows = read_csv_dicts(UNLOCK_BOARD_PATH)
    plan_by_idno = index_by_idno(read_csv_dicts(CREDENTIALED_PLAN_PATH))

    cookie_present = "1" if COOKIE_PATH.exists() else "0"
    header_present = "1" if HEADER_PATH.exists() else "0"
    cookie_bytes = file_bytes(COOKIE_PATH)
    header_bytes = file_bytes(HEADER_PATH)
    cookie_status = cookie_format_status(COOKIE_PATH)
    header_status = header_format_status(HEADER_PATH)
    session_material_present = cookie_present == "1" or header_present == "1"
    cookie_ready_for_probe = cookie_status in {
        "present_cookie_header_format",
        "present_netscape_cookie_file_format",
        "present_raw_cookie_pairs_format",
    }
    header_ready_for_probe = header_status in {
        "present_header_lines_with_cookie_review_or_move_cookie_to_cookie_file",
        "present_header_lines_no_cookie_values",
    }

    rows: list[dict[str, str]] = []
    for row in sorted(unlock_rows, key=lambda r: safe_int(r.get("download_rank"), 9999)):
        idno = clean(row.get("idno"))
        plan = plan_by_idno.get(idno, {})
        download_url = clean(plan.get("credentialed_download_url"))
        catalog_id = clean(plan.get("catalog_id")) or catalog_id_from_download_url(download_url)
        if clean(row.get("unlock_status")) == "ready_for_receipt_validation":
            status = "local_files_ready_skip_session_bootstrap"
        elif cookie_ready_for_probe or header_ready_for_probe:
            status = "session_material_present_ready_for_probe"
        elif session_material_present:
            status = "session_material_present_needs_review"
        else:
            status = "blocked_missing_worldbank_session_material"
        rows.append(
            {
                "download_rank": clean(row.get("download_rank")),
                "country": clean(row.get("country")),
                "wave": clean(row.get("wave")),
                "idno": idno,
                "catalog_id": catalog_id,
                "session_bootstrap_status": status,
                "official_get_microdata_url": clean(row.get("official_get_microdata_url")),
                "credentialed_download_url": download_url,
                "local_target_folder": clean(row.get("local_target_folder")),
                "cookie_file_present": cookie_present,
                "cookie_file_bytes": str(cookie_bytes),
                "cookie_file_format_status": cookie_status,
                "header_file_present": header_present,
                "header_file_bytes": str(header_bytes),
                "header_file_format_status": header_status,
                "unlock_status": clean(row.get("unlock_status")),
                "public_documentation_receipt_status": clean(row.get("public_documentation_receipt_status")),
                "expected_core_file_rows": clean(row.get("expected_core_file_rows")),
                "target_file_count": clean(row.get("target_file_count")),
                "probe_command": "python script/180_build_priority_lsms_isa_credentialed_download_handoff.py --probe",
                "execute_command": "python script/180_build_priority_lsms_isa_credentialed_download_handoff.py --execute",
                "safe_session_instruction": "Create temp/private/worldbank_session_cookies.txt from a logged-in World Bank Microdata browser session. Keep temp/private local-only and never commit it.",
                "post_download_validation_commands": clean(row.get("post_download_validation_commands")),
                "data_write_gate_status": "blocked_no_data_write",
                "modeling_gate_status": "blocked",
            }
        )

    status_counts: dict[str, int] = {}
    for row in rows:
        status_counts[row["session_bootstrap_status"]] = status_counts.get(row["session_bootstrap_status"], 0) + 1
    ready_for_probe = status_counts.get("session_material_present_ready_for_probe", 0)
    missing_session = status_counts.get("blocked_missing_worldbank_session_material", 0)
    summary = [
        {"metric": "worldbank_session_bootstrap_rows", "value": str(len(rows)), "interpretation": "Minimum-batch download rows covered by the session bootstrap."},
        {"metric": "worldbank_session_cookie_file_present", "value": cookie_present, "interpretation": "Whether temp/private/worldbank_session_cookies.txt exists. Contents are never exported."},
        {"metric": "worldbank_session_cookie_file_bytes", "value": str(cookie_bytes), "interpretation": "Cookie file size only; no credential values are reported."},
        {"metric": "worldbank_session_cookie_format_status", "value": cookie_status, "interpretation": "Redacted structural classification of the cookie file."},
        {"metric": "worldbank_session_header_file_present", "value": header_present, "interpretation": "Whether temp/private/worldbank_session_headers.txt exists. Contents are never exported."},
        {"metric": "worldbank_session_header_file_bytes", "value": str(header_bytes), "interpretation": "Header file size only; no header values are reported."},
        {"metric": "worldbank_session_header_format_status", "value": header_status, "interpretation": "Redacted structural classification of the header file."},
        {"metric": "worldbank_session_bootstrap_ready_for_probe_rows", "value": str(ready_for_probe), "interpretation": "Rows ready to run the credentialed --probe command."},
        {"metric": "worldbank_session_bootstrap_missing_session_rows", "value": str(missing_session), "interpretation": "Rows blocked because no local session material is present."},
        {"metric": "worldbank_session_bootstrap_status_blocked_missing_worldbank_session_material", "value": str(missing_session), "interpretation": "Status count."},
        {"metric": "data_write_gate_status", "value": "blocked_no_data_write", "interpretation": "This bootstrap writes only result/report artifacts and does not promote datasets."},
        {"metric": "modeling_gate_status", "value": "blocked", "interpretation": "No predictive, reduced-form, causal ML, or policy learning is opened."},
    ]
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
        f"""# Priority LSMS/ISA World Bank Session Bootstrap

This report captures the current credentialed-download session readiness for
the 10 minimum-batch World Bank Microdata packages. It is deliberately
redacted: it reports only whether local session files exist, their byte sizes,
and structural format checks. It never prints cookie or header values.

Local-only session files:

- `{rel(COOKIE_PATH)}`: Netscape cookie export, raw cookie pairs, or a `Cookie:` header from a logged-in World Bank Microdata browser session.
- `{rel(HEADER_PATH)}`: optional non-secret request headers. If a `Cookie:` header is placed here, review it before probing.

`temp/private/` is ignored by git. Keep those files local.

## Summary

{markdown_table(summary, ['metric', 'value', 'interpretation'], 20)}

## Bootstrap Rows

{markdown_table(rows, ['download_rank', 'country', 'wave', 'idno', 'session_bootstrap_status', 'credentialed_download_url', 'local_target_folder'], 12)}

## Commands

```bash
python script/180_build_priority_lsms_isa_credentialed_download_handoff.py --probe
python script/180_build_priority_lsms_isa_credentialed_download_handoff.py --execute
```

Run `--probe` first. Use `--execute` only after the official World Bank terms
have been accepted and the probe shows downloadable raw payloads.
""",
        encoding="utf-8",
    )


def main() -> None:
    ensure_dirs()
    rows, summary = build_outputs()
    write_csv(BOOTSTRAP_PATH, rows, BOOTSTRAP_COLUMNS)
    write_csv(SUMMARY_PATH, summary, SUMMARY_COLUMNS)
    write_report(rows, summary)
    append_log(TEMP_DIR / "audit_log.md", f"Built priority LSMS/ISA World Bank session bootstrap rows={len(rows)}.")
    print(f"Priority LSMS/ISA World Bank session bootstrap rows={len(rows)}.")


if __name__ == "__main__":
    main()
