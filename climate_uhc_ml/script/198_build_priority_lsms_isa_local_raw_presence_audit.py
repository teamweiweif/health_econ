from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

from common import PROJECT_ROOT, REPORT_DIR, RESULT_DIR, TEMP_DIR, append_log, ensure_dirs, write_csv


REGISTRY_PATH = RESULT_DIR / "promoted_country_wave_registry.csv"
STARTER_PATH = RESULT_DIR / "priority_lsms_isa_browser_download_starter.csv"
AUDIT_PATH = RESULT_DIR / "priority_lsms_isa_local_raw_presence_audit.csv"
NONREGISTRY_PATH = RESULT_DIR / "priority_lsms_isa_local_nonregistry_raw_files.csv"
SUMMARY_PATH = RESULT_DIR / "priority_lsms_isa_local_raw_presence_summary.csv"
REPORT_PATH = REPORT_DIR / "priority_lsms_isa_local_raw_presence_audit.md"

RAW_EXTENSIONS = {".dta", ".sav", ".por", ".sas7bdat", ".xpt", ".zip", ".rar", ".7z"}

AUDIT_COLUMNS = [
    "country",
    "wave",
    "idno",
    "priority_country",
    "minimum_batch_row",
    "analysis_ready_status",
    "raw_package_status",
    "raw_value_verification_status",
    "local_target_folder",
    "target_folder_exists",
    "raw_like_file_count",
    "raw_like_total_bytes",
    "raw_like_extensions",
    "raw_like_file_sample",
    "local_raw_presence_status",
    "promotion_implication",
    "next_action",
]

NONREGISTRY_COLUMNS = [
    "folder_id",
    "relative_path",
    "extension",
    "bytes",
    "nonregistry_raw_status",
    "promotion_implication",
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


def target_path(value: str) -> Path:
    text = clean(value).replace("/", "\\").rstrip("\\")
    if not text:
        return TEMP_DIR / "raw_downloads" / "_missing_target"
    path = Path(text)
    if path.is_absolute():
        return path
    return PROJECT_ROOT / path


def raw_like_files(folder: Path) -> list[Path]:
    if not folder.exists():
        return []
    files: list[Path] = []
    for path in folder.rglob("*"):
        if not path.is_file():
            continue
        if path.suffix.lower() in RAW_EXTENSIONS:
            files.append(path)
    return sorted(files, key=lambda p: rel(p).lower())


def folder_id_for(path: Path) -> str:
    try:
        parts = path.relative_to(TEMP_DIR / "raw_downloads").parts
    except ValueError:
        return ""
    return parts[0] if parts else ""


def status_for(row: dict[str, str], count: int) -> tuple[str, str, str]:
    analysis_ready = clean(row.get("analysis_ready_status"))
    if count > 0 and analysis_ready == "promoted_analysis_ready":
        return (
            "raw_present_promoted",
            "Raw-like package evidence is present for an already promoted registry row.",
            "Keep current promoted-data gate; do not rerun models.",
        )
    if count > 0:
        return (
            "raw_present_requires_receipt_validation",
            "Raw-like files exist but promotion still requires receipt, schema, value, semantics, timing/geography, and climate-linkage gates.",
            "Run the post-download receipt and raw-value validation chain before any data write.",
        )
    return (
        "raw_absent_blocks_promotion",
        "No raw-like files are present in the registry target folder; promotion cannot start.",
        "Download or manually place the complete unchanged official raw package and documentation in the target folder.",
    )


def build_outputs() -> tuple[list[dict[str, str]], list[dict[str, str]], list[dict[str, str]]]:
    registry_rows = read_csv_dicts(REGISTRY_PATH)
    starter_idnos = {clean(row.get("idno")) for row in read_csv_dicts(STARTER_PATH)}
    registry_folders: set[str] = set()
    audit_rows: list[dict[str, str]] = []

    for row in registry_rows:
        idno = clean(row.get("idno"))
        folder = target_path(row.get("local_target_folder", ""))
        registry_folders.add(clean(row.get("local_target_folder")).strip("/"))
        files = raw_like_files(folder)
        extensions = sorted({path.suffix.lower() for path in files})
        sample = ";".join(rel(path) for path in files[:8])
        status, implication, next_action = status_for(row, len(files))
        audit_rows.append(
            {
                "country": clean(row.get("country")),
                "wave": clean(row.get("wave")),
                "idno": idno,
                "priority_country": clean(row.get("priority_country")),
                "minimum_batch_row": "1" if idno in starter_idnos else "0",
                "analysis_ready_status": clean(row.get("analysis_ready_status")),
                "raw_package_status": clean(row.get("raw_package_status")),
                "raw_value_verification_status": clean(row.get("raw_value_verification_status")),
                "local_target_folder": clean(row.get("local_target_folder")),
                "target_folder_exists": "1" if folder.exists() else "0",
                "raw_like_file_count": str(len(files)),
                "raw_like_total_bytes": str(sum(path.stat().st_size for path in files)),
                "raw_like_extensions": ";".join(extensions),
                "raw_like_file_sample": sample,
                "local_raw_presence_status": status,
                "promotion_implication": implication,
                "next_action": next_action,
            }
        )

    registry_ids = {clean(row.get("idno")) for row in registry_rows}
    nonregistry_rows: list[dict[str, str]] = []
    raw_root = TEMP_DIR / "raw_downloads"
    for path in raw_like_files(raw_root):
        folder_id = folder_id_for(path)
        if folder_id in registry_ids:
            continue
        status = "diagnostic_nonregistry_raw_not_main_sample" if folder_id.startswith("ALB_") else "nonregistry_raw_not_in_promotion_registry"
        implication = "Albania raw files remain diagnostic-only under the active objective." if folder_id.startswith("ALB_") else "Raw-like file is outside the current promotion registry and cannot promote a row without a new gate."
        nonregistry_rows.append(
            {
                "folder_id": folder_id,
                "relative_path": rel(path),
                "extension": path.suffix.lower(),
                "bytes": str(path.stat().st_size),
                "nonregistry_raw_status": status,
                "promotion_implication": implication,
            }
        )

    raw_present = [row for row in audit_rows if safe_int(row.get("raw_like_file_count")) > 0]
    raw_absent = [row for row in audit_rows if safe_int(row.get("raw_like_file_count")) == 0]
    minimum_absent = [row for row in raw_absent if clean(row.get("minimum_batch_row")) == "1"]
    diagnostic_albania = [row for row in nonregistry_rows if clean(row.get("folder_id")).startswith("ALB_")]
    summary = [
        {"metric": "local_raw_presence_registry_rows", "value": str(len(audit_rows)), "interpretation": "Promotion registry rows audited for local raw-like files."},
        {"metric": "local_raw_presence_registry_raw_present_rows", "value": str(len(raw_present)), "interpretation": "Registry rows with at least one local raw-like file."},
        {"metric": "local_raw_presence_registry_raw_absent_rows", "value": str(len(raw_absent)), "interpretation": "Registry rows with no local raw-like files in their target folder."},
        {"metric": "local_raw_presence_minimum_batch_raw_absent_rows", "value": str(len(minimum_absent)), "interpretation": "Minimum-batch rows still lacking local raw-like files."},
        {"metric": "local_raw_presence_nonregistry_raw_file_rows", "value": str(len(nonregistry_rows)), "interpretation": "Raw-like files under temp/raw_downloads that are outside the current promotion registry."},
        {"metric": "local_raw_presence_diagnostic_albania_raw_file_rows", "value": str(len(diagnostic_albania)), "interpretation": "Albania raw-like files retained as diagnostic-only, not a main empirical sample."},
        {"metric": "local_raw_presence_promoted_rows", "value": str(sum(1 for row in audit_rows if row.get("analysis_ready_status") == "promoted_analysis_ready")), "interpretation": "Registry rows currently promoted analysis-ready."},
        {"metric": "data_write_gate_status", "value": "blocked_no_data_write", "interpretation": "This audit writes only result/report artifacts and does not promote datasets."},
        {"metric": "modeling_gate_status", "value": "blocked", "interpretation": "No predictive, reduced-form, causal ML, or policy learning is opened."},
    ]
    return audit_rows, nonregistry_rows, summary


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


def write_report(audit_rows: list[dict[str, str]], nonregistry_rows: list[dict[str, str]], summary: list[dict[str, str]]) -> None:
    REPORT_PATH.write_text(
        f"""# Priority LSMS/ISA Local Raw Presence Audit

Status: local raw-file presence audit for all 19 promoted-registry rows plus
raw-like files found outside the current promotion registry.

It does not download, copy, extract, write promoted `data/`, or run models.

## Summary

{markdown_table(summary, ['metric', 'value', 'interpretation'], 20)}

## Registry Rows

{markdown_table(audit_rows, ['country', 'wave', 'idno', 'minimum_batch_row', 'analysis_ready_status', 'raw_like_file_count', 'local_raw_presence_status'], 30)}

## Nonregistry Raw-Like Files

{markdown_table(nonregistry_rows, ['folder_id', 'relative_path', 'extension', 'bytes', 'nonregistry_raw_status'], 20)}

## Use

Treat rows with `raw_absent_blocks_promotion` as acquisition blockers. Treat
Albania rows in the nonregistry table as diagnostic-only under the active
dataset-promotion objective. A registry row can only move toward `data/` after
the complete official package passes receipt, schema, value-profile,
semantics, timing/geography, and climate-linkage gates.
""",
        encoding="utf-8",
    )


def main() -> None:
    ensure_dirs()
    audit_rows, nonregistry_rows, summary = build_outputs()
    write_csv(AUDIT_PATH, audit_rows, AUDIT_COLUMNS)
    write_csv(NONREGISTRY_PATH, nonregistry_rows, NONREGISTRY_COLUMNS)
    write_csv(SUMMARY_PATH, summary, SUMMARY_COLUMNS)
    write_report(audit_rows, nonregistry_rows, summary)
    append_log(TEMP_DIR / "audit_log.md", f"Built priority LSMS/ISA local raw presence audit rows={len(audit_rows)}.")
    print(f"Priority LSMS/ISA local raw presence audit complete: registry_rows={len(audit_rows)}, nonregistry_raw_files={len(nonregistry_rows)}.")


if __name__ == "__main__":
    main()
