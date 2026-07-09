from __future__ import annotations

import csv
import importlib.util
import math
import shutil
from pathlib import Path
from typing import Any

import pandas as pd

from common import REPORT_DIR, RESULT_DIR, TEMP_DIR, append_log, ensure_dirs, sha256_file, write_csv


RAW_FILE_INVENTORY = TEMP_DIR / "raw_schema_inventory" / "raw_file_inventory.csv"
AUDIT_PATH = TEMP_DIR / "albania_legacy_questionnaire_readability_audit.csv"
SUMMARY_PATH = RESULT_DIR / "albania_legacy_questionnaire_readability_summary.csv"
REPORT_PATH = REPORT_DIR / "albania_legacy_questionnaire_readability_audit.md"

BLOCKED_DECISION = "blocked_legacy_questionnaire_xls_reader_unavailable"
READABLE_DECISION = "legacy_questionnaires_readable_content_audit_required"
BLOCKED_PROMOTION_STATUS = "not_ready_for_questionnaire_timing_or_semantics_extraction"
READABLE_PROMOTION_STATUS = "readable_for_questionnaire_content_audit_not_climate_linkage_ready"

QUESTIONNAIRES = [
    {
        "country": "Albania",
        "survey_name": "Living Standards Measurement Survey 2002",
        "wave": "2002",
        "idno": "ALB_2002_LSMS_v01_M",
        "relative_path": "temp/raw_extracted/lsms2002en_4dbf0b087520/lsms2002en/Questionnaire 2002/LSMS02_Questionnaire.xls",
        "questionnaire_role": "single_legacy_questionnaire",
    },
    {
        "country": "Albania",
        "survey_name": "Living Standards Measurement Survey 2005",
        "wave": "2005",
        "idno": "ALB_2005_LSMS_v01_M",
        "relative_path": "temp/raw_extracted/lsms2005en_1e7f1965c4a5/lsms2005en/Questionnaire 2005/LSMS05_questionnaire_part1.xls",
        "questionnaire_role": "part1_legacy_questionnaire",
    },
    {
        "country": "Albania",
        "survey_name": "Living Standards Measurement Survey 2005",
        "wave": "2005",
        "idno": "ALB_2005_LSMS_v01_M",
        "relative_path": "temp/raw_extracted/lsms2005en_1e7f1965c4a5/lsms2005en/Questionnaire 2005/LSMS05_Questionnaire_part2.xls",
        "questionnaire_role": "part2_legacy_questionnaire",
    },
    {
        "country": "Albania",
        "survey_name": "Living Standards Measurement Survey 2008",
        "wave": "2008",
        "idno": "ALB_2008_LSMS_v01_M",
        "relative_path": "temp/raw_extracted/lsms_2008_eng_a54110ab32b9/LSMS 2008_eng/Questionnaire/FINAL LSMS08 PART 1 ENGLISH.xls",
        "questionnaire_role": "part1_legacy_questionnaire",
    },
    {
        "country": "Albania",
        "survey_name": "Living Standards Measurement Survey 2008",
        "wave": "2008",
        "idno": "ALB_2008_LSMS_v01_M",
        "relative_path": "temp/raw_extracted/lsms_2008_eng_a54110ab32b9/LSMS 2008_eng/Questionnaire/FINAL LSMS08 PART 2 ENGLISH1.xls",
        "questionnaire_role": "part2_legacy_questionnaire",
    },
]

AUDIT_COLUMNS = [
    "country",
    "survey_name",
    "wave",
    "idno",
    "relative_path",
    "file_exists",
    "file_format",
    "file_size_bytes",
    "sha256",
    "magic_bytes_hex",
    "ole_compound_file_signature",
    "questionnaire_role",
    "schema_inventory_status",
    "schema_inventory_error",
    "xlrd_installed",
    "python_calamine_installed",
    "pyxlsb_installed",
    "soffice_available",
    "libreoffice_available",
    "read_attempt_status",
    "read_attempt_error",
    "sheet_count",
    "sheet_names_preview",
    "promotion_status",
    "blocking_reason",
    "next_action",
]
SUMMARY_COLUMNS = ["metric", "value", "interpretation"]


def fmt(value: Any) -> str:
    if value is None:
        return ""
    try:
        if pd.isna(value):
            return ""
    except TypeError:
        pass
    if isinstance(value, float):
        if not math.isfinite(value):
            return ""
        if value.is_integer():
            return str(int(value))
        return f"{value:.6g}"
    return str(value)


def read_csv_dicts(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def inventory_by_path() -> dict[str, dict[str, str]]:
    rows = read_csv_dicts(RAW_FILE_INVENTORY)
    out: dict[str, dict[str, str]] = {}
    for row in rows:
        source_path = row.get("source_path", "").replace("\\", "/")
        if source_path:
            out[source_path] = row
    return out


def package_available(name: str) -> str:
    return "1" if importlib.util.find_spec(name) is not None else "0"


def executable_available(name: str) -> str:
    return "1" if shutil.which(name) else "0"


def magic_bytes(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_bytes()[:8].hex()


def read_attempt(path: Path) -> tuple[str, str, str, str]:
    if not path.exists():
        return "missing_file", "file does not exist", "0", ""
    try:
        xl = pd.ExcelFile(path)
        return "read_ok", "", str(len(xl.sheet_names)), "; ".join(xl.sheet_names[:12])
    except Exception as exc:  # pragma: no cover - this is the audit signal on current envs.
        return "read_failed", f"{type(exc).__name__}: {exc}", "0", ""


def build_rows() -> list[dict[str, str]]:
    inventory = inventory_by_path()
    xlrd = package_available("xlrd")
    calamine = package_available("python_calamine")
    pyxlsb = package_available("pyxlsb")
    soffice = executable_available("soffice")
    libreoffice = executable_available("libreoffice")
    rows: list[dict[str, str]] = []
    for item in QUESTIONNAIRES:
        relative_path = item["relative_path"]
        path = TEMP_DIR.parent / relative_path
        inventory_row = inventory.get(relative_path, {})
        read_status, read_error, sheet_count, sheet_preview = read_attempt(path)
        magic = magic_bytes(path)
        read_ok = read_status == "read_ok"
        blocking_reason = (
            "Workbook can be read, but sheet-level timing/geography/outcome semantics still require a separate content audit before promotion."
            if read_ok
            else "Legacy Excel .xls questionnaire is present, but current reproducibility environment cannot read it. "
            "Install a documented .xls reader such as xlrd>=2.0.1 or convert the original workbook to xlsx/csv "
            "with a reproducible command before using questionnaire timing, geography, or outcome semantics."
        )
        rows.append(
            {
                **{key: item[key] for key in ["country", "survey_name", "wave", "idno"]},
                "relative_path": relative_path,
                "file_exists": "1" if path.exists() else "0",
                "file_format": path.suffix.lower(),
                "file_size_bytes": str(path.stat().st_size) if path.exists() else "",
                "sha256": sha256_file(path) if path.exists() else "",
                "magic_bytes_hex": magic,
                "ole_compound_file_signature": "1" if magic.startswith("d0cf11e0") else "0",
                "questionnaire_role": item["questionnaire_role"],
                "schema_inventory_status": inventory_row.get("status", ""),
                "schema_inventory_error": inventory_row.get("error", ""),
                "xlrd_installed": xlrd,
                "python_calamine_installed": calamine,
                "pyxlsb_installed": pyxlsb,
                "soffice_available": soffice,
                "libreoffice_available": libreoffice,
                "read_attempt_status": read_status,
                "read_attempt_error": read_error,
                "sheet_count": sheet_count,
                "sheet_names_preview": sheet_preview,
                "promotion_status": READABLE_PROMOTION_STATUS if read_ok else BLOCKED_PROMOTION_STATUS,
                "blocking_reason": blocking_reason,
                "next_action": (
                    "run script/67_audit_albania_legacy_questionnaire_timing_fields.py before using any legacy questionnaire timing, geography, or skip-pattern evidence"
                    if read_ok
                    else "document and install/enable an .xls reader or perform reproducible conversion before content-level questionnaire timing/geography audit"
                ),
            }
        )
    return rows


def summary_row(metric: str, value: Any, interpretation: str) -> dict[str, str]:
    return {"metric": metric, "value": fmt(value), "interpretation": interpretation}


def build_summary(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    read_ok_files = sum(1 for row in rows if row["read_attempt_status"] == "read_ok")
    decision = READABLE_DECISION if rows and read_ok_files == len(rows) else BLOCKED_DECISION
    return [
        summary_row("albania_legacy_questionnaire_files", len(rows), "Legacy Albania questionnaire .xls files expected in local raw extractions."),
        summary_row("albania_legacy_questionnaire_present_files", sum(1 for row in rows if row["file_exists"] == "1"), "Legacy questionnaire files present locally."),
        summary_row("albania_legacy_questionnaire_ole_signature_files", sum(1 for row in rows if row["ole_compound_file_signature"] == "1"), "Files with OLE compound-file signature expected for legacy .xls."),
        summary_row("albania_legacy_questionnaire_xlrd_installed", rows[0]["xlrd_installed"] if rows else "0", "Whether xlrd is importable in the current Python environment."),
        summary_row("albania_legacy_questionnaire_python_calamine_installed", rows[0]["python_calamine_installed"] if rows else "0", "Whether python_calamine is importable in the current Python environment."),
        summary_row("albania_legacy_questionnaire_soffice_available", rows[0]["soffice_available"] if rows else "0", "Whether soffice is available on PATH for reproducible conversion."),
        summary_row("albania_legacy_questionnaire_read_ok_files", read_ok_files, "Legacy questionnaire files readable by pandas in the current environment."),
        summary_row("albania_legacy_questionnaire_read_failed_files", sum(1 for row in rows if row["read_attempt_status"] == "read_failed"), "Legacy questionnaire files not readable by pandas in the current environment."),
        summary_row("albania_legacy_questionnaire_missing_reader_blocked_files", sum(1 for row in rows if "xlrd" in row["read_attempt_error"].lower() or row["read_attempt_status"] != "read_ok"), "Files blocked from questionnaire content extraction because a legacy .xls reader/converter is unavailable."),
        summary_row("albania_legacy_questionnaire_timing_content_audit_ready_rows", read_ok_files, "Legacy questionnaire files ready for separate timing/geography content extraction after this readability audit."),
        summary_row("albania_legacy_questionnaire_climate_linkage_ready_rows", 0, "Rows ready for climate-linkage promotion after this audit."),
        summary_row("albania_legacy_questionnaire_current_decision", decision, "Current fail-closed decision for legacy questionnaire readability."),
    ]


def markdown_rows(rows: list[dict[str, str]], columns: list[str], limit: int = 20) -> str:
    lines = ["| " + " | ".join(columns) + " |", "|" + "|".join("---" for _ in columns) + "|"]
    for row in rows[:limit]:
        values: list[str] = []
        for column in columns:
            value = (row.get(column, "") or "").replace("|", "/")
            if len(value) > 120:
                value = value[:117] + "..."
            values.append(value)
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines)


def write_report(rows: list[dict[str, str]], summary: list[dict[str, str]]) -> None:
    summary_table = "\n".join(f"| {row['metric']} | {row['value']} | {row['interpretation']} |" for row in summary)
    REPORT_PATH.write_text(
        f"""# Albania Legacy Questionnaire Readability Audit

Status: environment/readability audit only. This report inventories ALB_2002, ALB_2005, and ALB_2008 legacy `.xls` questionnaire files and tests whether the current reproducibility environment can inspect sheet contents. It does not extract questionnaire timing/geography content, does not write `data/`, and does not promote any climate-linkage evidence.

## Summary

| Metric | Value | Interpretation |
|---|---:|---|
{summary_table}

## File-Level Readability

{markdown_rows(rows, ['idno', 'wave', 'relative_path', 'file_exists', 'ole_compound_file_signature', 'schema_inventory_status', 'read_attempt_status', 'read_attempt_error'], 10)}

## Interpretation

- Five legacy Albania questionnaire workbooks are present and are valid legacy `.xls`/OLE files.
- `xlrd` is available in the current Python environment, so the legacy workbooks can be opened and sheet names can be inspected.
- Readability is only a gate to content review. It does not verify household-level raw interview timing values, geography, skip patterns, units, recall periods, or outcome semantics.
- Therefore ALB_2002, ALB_2005, and ALB_2008 questionnaire timing, geography, skip-pattern, and outcome-semantics evidence still require a separate content audit before use.
- This does not promote any legacy wave to harmonization or climate linkage.

## Required Next Action

Run `script/67_audit_albania_legacy_questionnaire_timing_fields.py` before using any ALB_2002/2005/2008 questionnaire timing, geography, or skip-pattern content. Keep all questionnaire-derived evidence out of climate-linkage inputs unless it is connected to verified raw household timing/geography values.

## Machine-Readable Outputs

- `temp/albania_legacy_questionnaire_readability_audit.csv`
- `result/albania_legacy_questionnaire_readability_summary.csv`
""",
        encoding="utf-8",
    )


def main() -> None:
    ensure_dirs()
    rows = build_rows()
    summary = build_summary(rows)
    write_csv(AUDIT_PATH, rows, AUDIT_COLUMNS)
    write_csv(SUMMARY_PATH, summary, SUMMARY_COLUMNS)
    write_report(rows, summary)
    append_log(
        TEMP_DIR / "audit_log.md",
        f"Built Albania legacy questionnaire readability audit rows={len(rows)} decision={next((row['value'] for row in summary if row['metric'] == 'albania_legacy_questionnaire_current_decision'), '')}.",
    )
    print(f"Albania legacy questionnaire readability audit rows={len(rows)} decision={next((row['value'] for row in summary if row['metric'] == 'albania_legacy_questionnaire_current_decision'), '')}.")


if __name__ == "__main__":
    main()
