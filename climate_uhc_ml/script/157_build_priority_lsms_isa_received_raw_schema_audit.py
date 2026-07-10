from __future__ import annotations

import csv
import tempfile
from collections import Counter, defaultdict
from pathlib import Path, PurePosixPath
from typing import Any
from zipfile import BadZipFile, ZipFile

import pandas as pd
import pyreadstat

from common import PROJECT_ROOT, REPORT_DIR, RESULT_DIR, TEMP_DIR, append_log, ensure_dirs, write_csv


RECEIPT_VALIDATION_PATH = TEMP_DIR / "priority_lsms_isa_official_file_receipt_validation.csv"
ARCHIVE_MEMBER_PATH = TEMP_DIR / "priority_lsms_isa_archive_member_manifest.csv"
DIRECT_FILE_PATH = TEMP_DIR / "priority_lsms_isa_direct_file_preflight.csv"
VARIABLE_WORKBOOK_PATH = TEMP_DIR / "priority_lsms_isa_raw_value_variable_workbook.csv"

FILE_SCHEMA_PATH = TEMP_DIR / "priority_lsms_isa_received_raw_schema_file_inventory.csv"
VARIABLE_SCHEMA_PATH = TEMP_DIR / "priority_lsms_isa_received_raw_variable_schema.csv"
REQUIREMENT_EVIDENCE_PATH = TEMP_DIR / "priority_lsms_isa_received_raw_requirement_evidence.csv"
SUMMARY_PATH = RESULT_DIR / "priority_lsms_isa_received_raw_schema_audit_summary.csv"
REPORT_PATH = REPORT_DIR / "priority_lsms_isa_received_raw_schema_audit.md"

RAW_ALIAS_EXTENSIONS = (
    ".dta",
    ".sav",
    ".por",
    ".sas7bdat",
    ".xpt",
    ".csv",
    ".txt",
    ".xlsx",
    ".xls",
)

FILE_SCHEMA_COLUMNS = [
    "download_priority_order",
    "queue_role",
    "country",
    "wave",
    "idno",
    "archive_relative_path",
    "member_name",
    "member_key",
    "member_role",
    "read_status",
    "read_error",
    "row_count",
    "column_count",
]

VARIABLE_SCHEMA_COLUMNS = [
    "download_priority_order",
    "queue_role",
    "country",
    "wave",
    "idno",
    "member_name",
    "member_key",
    "variable_name",
    "variable_label",
    "readstat_type",
    "original_type",
    "has_value_labels",
]

REQUIREMENT_EVIDENCE_COLUMNS = [
    "download_priority_order",
    "queue_role",
    "country",
    "wave",
    "idno",
    "requirement",
    "expected_file_name",
    "expected_file_key",
    "actual_member_name",
    "actual_member_key",
    "variable_name",
    "metadata_variable_label",
    "raw_variable_label",
    "candidate_strength",
    "raw_variable_present",
    "value_scan_status",
    "value_scan_error",
    "row_count",
    "nonmissing_count",
    "missing_count",
    "distinct_nonmissing_count",
    "numeric_min",
    "numeric_max",
    "schema_evidence_status",
]

SUMMARY_COLUMNS = ["metric", "value", "interpretation"]


def read_csv_dicts(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def clean(value: Any) -> str:
    return "" if value is None else str(value).strip()


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


def file_key(value: str) -> str:
    text = clean(value).replace("\\", "/")
    if not text:
        return ""
    return PurePosixPath(text).name.lower()


def expected_lookup_keys(expected_name: str) -> list[str]:
    key = file_key(expected_name)
    if not key:
        return []
    keys = [key]
    if key.endswith(".nsdstat"):
        stem = key[: -len(".nsdstat")]
        keys.extend(f"{stem}{ext}" for ext in RAW_ALIAS_EXTENSIONS)
    elif not PurePosixPath(key).suffix:
        keys.extend(f"{key}{ext}" for ext in RAW_ALIAS_EXTENSIONS)
    return keys


def compact_error(error: Exception) -> str:
    return " ".join(f"{type(error).__name__}: {error}".split())[:500]


def value_label_flag(meta: Any, variable_name: str) -> str:
    labels = getattr(meta, "variable_value_labels", {}) or {}
    return "1" if variable_name in labels and labels.get(variable_name) else "0"


def type_lookup(meta: Any, attr: str, variable_name: str) -> str:
    values = getattr(meta, attr, {}) or {}
    if isinstance(values, dict):
        return clean(values.get(variable_name))
    return ""


def numeric_text(value: Any) -> str:
    if value is None or pd.isna(value):
        return ""
    try:
        return f"{float(value):.6g}"
    except (TypeError, ValueError):
        return ""


def scan_series(series: pd.Series) -> dict[str, str]:
    row_count = len(series)
    nonmissing = int(series.notna().sum())
    missing = row_count - nonmissing
    distinct = int(series.dropna().nunique())
    numeric = pd.to_numeric(series, errors="coerce")
    numeric_nonmissing = numeric.dropna()
    return {
        "row_count": str(row_count),
        "nonmissing_count": str(nonmissing),
        "missing_count": str(missing),
        "distinct_nonmissing_count": str(distinct),
        "numeric_min": numeric_text(numeric_nonmissing.min()) if not numeric_nonmissing.empty else "",
        "numeric_max": numeric_text(numeric_nonmissing.max()) if not numeric_nonmissing.empty else "",
    }


def readable_receipts(rows: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    out: dict[str, dict[str, str]] = {}
    for row in rows:
        if clean(row.get("official_file_receipt_status")) == "official_file_receipt_complete_pending_schema_value_review":
            out[clean(row.get("idno"))] = row
    return out


def archive_members_by_id(
    member_rows: list[dict[str, str]],
    receipt_ids: set[str],
) -> dict[str, list[dict[str, str]]]:
    out: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in member_rows:
        idno = clean(row.get("idno"))
        if idno in receipt_ids and file_key(row.get("member_name", "")).endswith(".dta"):
            row["_raw_source_type"] = "archive_member"
            out[idno].append(row)
    return out


def direct_files_by_id(
    direct_rows: list[dict[str, str]],
    receipt_ids: set[str],
) -> dict[str, list[dict[str, str]]]:
    out: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in direct_rows:
        idno = clean(row.get("idno"))
        if idno not in receipt_ids or not file_key(row.get("file_name", "")).endswith(".dta"):
            continue
        row["_raw_source_type"] = "direct_file"
        row["archive_relative_path"] = clean(row.get("relative_path"))
        row["member_name"] = clean(row.get("file_name"))
        row["member_role"] = clean(row.get("file_role"))
        out[idno].append(row)
    return out


def workbook_by_id_member(workbook_rows: list[dict[str, str]]) -> dict[str, dict[str, list[dict[str, str]]]]:
    out: dict[str, dict[str, list[dict[str, str]]]] = defaultdict(lambda: defaultdict(list))
    for row in workbook_rows:
        idno = clean(row.get("idno"))
        expected_name = clean(row.get("file_name"))
        variable = clean(row.get("variable_name"))
        if not idno or not expected_name or not variable:
            continue
        for key in expected_lookup_keys(expected_name):
            out[idno][key].append(row)
    return out


def read_member_metadata(zip_path: Path, member_name: str) -> tuple[Any, list[str]]:
    with ZipFile(zip_path) as zf:
        payload = zf.read(member_name)
    with tempfile.TemporaryDirectory() as td:
        raw_path = Path(td) / PurePosixPath(member_name).name
        raw_path.write_bytes(payload)
        _, meta = pyreadstat.read_dta(str(raw_path), metadataonly=True)
    return meta, list(meta.column_names)


def read_member_values(zip_path: Path, member_name: str, columns: list[str]) -> pd.DataFrame:
    if not columns:
        return pd.DataFrame()
    with ZipFile(zip_path) as zf:
        payload = zf.read(member_name)
    with tempfile.TemporaryDirectory() as td:
        raw_path = Path(td) / PurePosixPath(member_name).name
        raw_path.write_bytes(payload)
        df, _ = pyreadstat.read_dta(str(raw_path), usecols=columns)
    return df


def read_direct_metadata(raw_path: Path) -> tuple[Any, list[str]]:
    _, meta = pyreadstat.read_dta(str(raw_path), metadataonly=True)
    return meta, list(meta.column_names)


def read_direct_values(raw_path: Path, columns: list[str]) -> pd.DataFrame:
    if not columns:
        return pd.DataFrame()
    df, _ = pyreadstat.read_dta(str(raw_path), usecols=columns)
    return df


def build_schema_rows() -> tuple[list[dict[str, str]], list[dict[str, str]], list[dict[str, str]], list[dict[str, str]]]:
    receipt_by_id = readable_receipts(read_csv_dicts(RECEIPT_VALIDATION_PATH))
    receipt_ids = set(receipt_by_id)
    members_by_id = archive_members_by_id(read_csv_dicts(ARCHIVE_MEMBER_PATH), receipt_ids)
    direct_by_id = direct_files_by_id(read_csv_dicts(DIRECT_FILE_PATH), receipt_ids)
    for idno, rows in direct_by_id.items():
        members_by_id[idno].extend(rows)
    workbook = workbook_by_id_member(read_csv_dicts(VARIABLE_WORKBOOK_PATH))

    file_rows: list[dict[str, str]] = []
    variable_rows: list[dict[str, str]] = []
    evidence_rows: list[dict[str, str]] = []
    handoff_rows: list[dict[str, str]] = []

    for idno, members in sorted(members_by_id.items()):
        receipt = receipt_by_id[idno]
        for member in sorted(members, key=lambda row: clean(row.get("member_name"))):
            member_name = clean(member.get("member_name"))
            member_key = file_key(member_name)
            archive_relative = clean(member.get("archive_relative_path"))
            raw_path = PROJECT_ROOT / archive_relative.replace("/", "\\")
            raw_source_type = clean(member.get("_raw_source_type")) or "archive_member"
            base = {
                "download_priority_order": clean(receipt.get("download_priority_order")),
                "queue_role": clean(receipt.get("queue_role")),
                "country": clean(receipt.get("country")),
                "wave": clean(receipt.get("wave")),
                "idno": idno,
                "archive_relative_path": archive_relative,
                "member_name": member_name,
                "member_key": member_key,
                "member_role": clean(member.get("member_role")),
            }
            candidates = workbook.get(idno, {}).get(member_key, [])
            try:
                if raw_source_type == "direct_file":
                    meta, column_names = read_direct_metadata(raw_path)
                else:
                    meta, column_names = read_member_metadata(raw_path, member_name)
                labels = dict(zip(meta.column_names, meta.column_labels))
                file_rows.append(
                    {
                        **base,
                        "read_status": "readable_metadata",
                        "read_error": "",
                        "row_count": str(safe_int(getattr(meta, "number_rows", 0))),
                        "column_count": str(len(column_names)),
                    }
                )
                for variable in column_names:
                    variable_rows.append(
                        {
                            **{key: base[key] for key in ["download_priority_order", "queue_role", "country", "wave", "idno", "member_name", "member_key"]},
                            "variable_name": variable,
                            "variable_label": clean(labels.get(variable)),
                            "readstat_type": type_lookup(meta, "readstat_variable_types", variable),
                            "original_type": type_lookup(meta, "original_variable_types", variable),
                            "has_value_labels": value_label_flag(meta, variable),
                        }
                    )

                candidate_names = sorted({clean(row.get("variable_name")) for row in candidates if clean(row.get("variable_name")) in column_names})
                value_stats: dict[str, dict[str, str]] = {}
                value_scan_error = ""
                if candidate_names:
                    try:
                        if raw_source_type == "direct_file":
                            df = read_direct_values(raw_path, candidate_names)
                        else:
                            df = read_member_values(raw_path, member_name, candidate_names)
                        for variable in candidate_names:
                            value_stats[variable] = scan_series(df[variable])
                    except Exception as error:  # pragma: no cover - depends on legacy file quirks
                        value_scan_error = compact_error(error)

                for candidate in candidates:
                    variable = clean(candidate.get("variable_name"))
                    present = variable in column_names
                    stats = value_stats.get(variable, {})
                    evidence_rows.append(
                        {
                            "download_priority_order": clean(receipt.get("download_priority_order")),
                            "queue_role": clean(receipt.get("queue_role")),
                            "country": clean(receipt.get("country")),
                            "wave": clean(receipt.get("wave")),
                            "idno": idno,
                            "requirement": clean(candidate.get("requirement")),
                            "expected_file_name": clean(candidate.get("file_name")),
                            "expected_file_key": file_key(candidate.get("file_name", "")),
                            "actual_member_name": member_name,
                            "actual_member_key": member_key,
                            "variable_name": variable,
                            "metadata_variable_label": clean(candidate.get("variable_label")),
                            "raw_variable_label": clean(labels.get(variable)) if present else "",
                            "candidate_strength": clean(candidate.get("candidate_strength")),
                            "raw_variable_present": "1" if present else "0",
                            "value_scan_status": "value_stats_scanned" if stats else ("not_scanned_variable_missing" if not present else "not_scanned_read_error"),
                            "value_scan_error": value_scan_error if present and not stats else "",
                            "row_count": stats.get("row_count", ""),
                            "nonmissing_count": stats.get("nonmissing_count", ""),
                            "missing_count": stats.get("missing_count", ""),
                            "distinct_nonmissing_count": stats.get("distinct_nonmissing_count", ""),
                            "numeric_min": stats.get("numeric_min", ""),
                            "numeric_max": stats.get("numeric_max", ""),
                            "schema_evidence_status": "raw_schema_variable_present_needs_unit_skip_review" if present else "missing_from_readable_raw_schema",
                        }
                    )
            except (BadZipFile, KeyError, pyreadstat.ReadstatError, OSError) as error:
                file_rows.append(
                    {
                        **base,
                        "read_status": "failed_metadata_read",
                        "read_error": compact_error(error),
                        "row_count": "",
                        "column_count": "",
                    }
                )
                for candidate in candidates:
                    evidence_rows.append(
                        {
                            "download_priority_order": clean(receipt.get("download_priority_order")),
                            "queue_role": clean(receipt.get("queue_role")),
                            "country": clean(receipt.get("country")),
                            "wave": clean(receipt.get("wave")),
                            "idno": idno,
                            "requirement": clean(candidate.get("requirement")),
                            "expected_file_name": clean(candidate.get("file_name")),
                            "expected_file_key": file_key(candidate.get("file_name", "")),
                            "actual_member_name": member_name,
                            "actual_member_key": member_key,
                            "variable_name": clean(candidate.get("variable_name")),
                            "metadata_variable_label": clean(candidate.get("variable_label")),
                            "raw_variable_label": "",
                            "candidate_strength": clean(candidate.get("candidate_strength")),
                            "raw_variable_present": "0",
                            "value_scan_status": "not_scanned_file_unreadable",
                            "value_scan_error": compact_error(error),
                            "row_count": "",
                            "nonmissing_count": "",
                            "missing_count": "",
                            "distinct_nonmissing_count": "",
                            "numeric_min": "",
                            "numeric_max": "",
                            "schema_evidence_status": "missing_from_readable_raw_schema",
                        }
                    )

        handoff_rows.append(write_handoff(receipt, [row for row in file_rows if row.get("idno") == idno], [row for row in evidence_rows if row.get("idno") == idno]))

    return file_rows, variable_rows, evidence_rows, handoff_rows


def markdown_table(rows: list[dict[str, str]], columns: list[str], limit: int = 20) -> str:
    lines = ["| " + " | ".join(columns) + " |", "|" + "|".join("---" for _ in columns) + "|"]
    for row in rows[:limit]:
        values: list[str] = []
        for column in columns:
            value = clean(row.get(column)).replace("|", "/")
            if len(value) > 120:
                value = value[:117] + "..."
            values.append(value)
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines)


def summarize(file_rows: list[dict[str, str]], variable_rows: list[dict[str, str]], evidence_rows: list[dict[str, str]], handoff_rows: list[str]) -> list[dict[str, str]]:
    dataset_ids = {row.get("idno", "") for row in file_rows}
    readable_files = sum(1 for row in file_rows if row.get("read_status") == "readable_metadata")
    present_evidence = sum(1 for row in evidence_rows if row.get("raw_variable_present") == "1")
    status_counts = Counter(row.get("schema_evidence_status", "") for row in evidence_rows)
    requirement_counts = Counter(row.get("requirement", "") for row in evidence_rows if row.get("raw_variable_present") == "1")
    rows = [
        {"metric": "priority_lsms_received_raw_schema_dataset_rows", "value": str(len(dataset_ids)), "interpretation": "Datasets with complete official-file receipt scanned directly from received raw archives."},
        {"metric": "priority_lsms_received_raw_schema_file_rows", "value": str(len(file_rows)), "interpretation": "Archive members attempted for schema extraction."},
        {"metric": "priority_lsms_received_raw_schema_readable_file_rows", "value": str(readable_files), "interpretation": "Archive members readable by pyreadstat metadata scan."},
        {"metric": "priority_lsms_received_raw_schema_failed_file_rows", "value": str(len(file_rows) - readable_files), "interpretation": "Archive members that could not be read for metadata."},
        {"metric": "priority_lsms_received_raw_schema_variable_rows", "value": str(len(variable_rows)), "interpretation": "Raw schema variable rows extracted without persisting raw microdata."},
        {"metric": "priority_lsms_received_raw_requirement_candidate_rows", "value": str(len(evidence_rows)), "interpretation": "Metadata candidate variables checked against readable raw schemas."},
        {"metric": "priority_lsms_received_raw_requirement_candidate_present_rows", "value": str(present_evidence), "interpretation": "Candidate variables present in the received raw schemas."},
        {"metric": "priority_lsms_received_raw_schema_handoff_readmes_written", "value": str(len(handoff_rows)), "interpretation": "Per-dataset raw schema audit handoff readmes written under temp/raw_downloads."},
        {"metric": "priority_lsms_received_raw_schema_data_write_status", "value": "blocked_schema_evidence_only", "interpretation": "Schema evidence does not write analysis-ready data."},
        {"metric": "modeling_gate_status", "value": "blocked", "interpretation": "Models remain blocked until promoted registry thresholds pass."},
    ]
    for status, count in sorted(status_counts.items()):
        rows.append({"metric": f"priority_lsms_received_raw_schema_status_{status}", "value": str(count), "interpretation": "Candidate variable schema evidence status count."})
    for requirement, count in sorted(requirement_counts.items()):
        rows.append({"metric": f"priority_lsms_received_raw_schema_requirement_present_{requirement}", "value": str(count), "interpretation": "Present raw-schema candidate variable count by requirement."})
    return rows


def write_handoff(receipt: dict[str, str], file_rows: list[dict[str, str]], evidence_rows: list[dict[str, str]]) -> str:
    idno = clean(receipt.get("idno"))
    folder = PROJECT_ROOT / clean(receipt.get("local_target_folder")).replace("/", "\\")
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / "_PRIORITY_LSMS_ISA_RECEIVED_RAW_SCHEMA_AUDIT.md"
    present_by_requirement = Counter(row.get("requirement", "") for row in evidence_rows if row.get("raw_variable_present") == "1")
    requirement_rows = [
        {"requirement": requirement, "present_candidate_rows": str(count)}
        for requirement, count in sorted(present_by_requirement.items())
    ]
    path.write_text(
        f"""# Priority LSMS-ISA Received Raw Schema Audit

IDNO: `{idno}`

Country-wave: {receipt.get('country', '')} {receipt.get('wave', '')}

Status: metadata and selected value-stat scan of received raw archive members.
This handoff does not promote the dataset and does not persist raw microdata.

## File Readability

{markdown_table(file_rows, ['member_name', 'read_status', 'row_count', 'column_count', 'read_error'], 80)}

## Present Candidate Variables By Requirement

{markdown_table(requirement_rows, ['requirement', 'present_candidate_rows'], 20) if requirement_rows else 'No candidate variables were confirmed in readable raw schemas.'}

## Remaining Gate Meaning

Confirmed raw schema presence is necessary but not sufficient. Promotion still
requires human-readable documentation, accepted merge keys, survey design,
units, recall periods, skip patterns, missing-value semantics, outcome
construction, and climate-linkage evidence.
""",
        encoding="utf-8",
    )
    return rel(path)


def write_report(file_rows: list[dict[str, str]], evidence_rows: list[dict[str, str]], summary_rows: list[dict[str, str]]) -> None:
    summary_table = "\n".join(f"| {row['metric']} | {row['value']} | {row['interpretation']} |" for row in summary_rows)
    dataset_rows: list[dict[str, str]] = []
    for idno in sorted({row.get("idno", "") for row in file_rows}):
        files = [row for row in file_rows if row.get("idno") == idno]
        evidence = [row for row in evidence_rows if row.get("idno") == idno]
        first = files[0] if files else {}
        dataset_rows.append(
            {
                "country": first.get("country", ""),
                "wave": first.get("wave", ""),
                "idno": idno,
                "readable_files": str(sum(1 for row in files if row.get("read_status") == "readable_metadata")),
                "file_rows": str(len(files)),
                "present_candidate_variables": str(sum(1 for row in evidence if row.get("raw_variable_present") == "1")),
                "candidate_variables": str(len(evidence)),
            }
        )
    REPORT_PATH.write_text(
        f"""# Priority LSMS-ISA Received Raw Schema Audit

Status: direct schema and selected value-stat audit of received LSMS/ISA raw
archives. The script extracts each Stata member to an operating-system temp
file, reads metadata and candidate-variable statistics, then discards the raw
copy. No raw microdata are written to `data/`.

## Summary

| Metric | Value | Interpretation |
|---|---:|---|
{summary_table}

## Dataset Coverage

{markdown_table(dataset_rows, ['country', 'wave', 'idno', 'readable_files', 'file_rows', 'present_candidate_variables', 'candidate_variables'], 50)}

## Outputs

- `temp/priority_lsms_isa_received_raw_schema_file_inventory.csv`
- `temp/priority_lsms_isa_received_raw_variable_schema.csv`
- `temp/priority_lsms_isa_received_raw_requirement_evidence.csv`
- `result/priority_lsms_isa_received_raw_schema_audit_summary.csv`

## Interpretation

This is a schema-evidence layer between raw-package receipt and full
raw-value verification. It can show that candidate variables exist in the
received raw files and have nonmissing observations, but it cannot by itself
settle units, recall periods, skip patterns, missing codes, or promotion.
""",
        encoding="utf-8",
    )


def main() -> None:
    ensure_dirs()
    file_rows, variable_rows, evidence_rows, handoff_rows = build_schema_rows()
    summary_rows = summarize(file_rows, variable_rows, evidence_rows, handoff_rows)
    write_csv(FILE_SCHEMA_PATH, file_rows, FILE_SCHEMA_COLUMNS)
    write_csv(VARIABLE_SCHEMA_PATH, variable_rows, VARIABLE_SCHEMA_COLUMNS)
    write_csv(REQUIREMENT_EVIDENCE_PATH, evidence_rows, REQUIREMENT_EVIDENCE_COLUMNS)
    write_csv(SUMMARY_PATH, summary_rows, SUMMARY_COLUMNS)
    write_report(file_rows, evidence_rows, summary_rows)
    append_log(
        TEMP_DIR / "audit_log.md",
        "Priority LSMS/ISA received raw schema audit "
        f"datasets={len({row.get('idno', '') for row in file_rows})} files={len(file_rows)} variables={len(variable_rows)} evidence_rows={len(evidence_rows)}.",
    )
    print(
        "Priority LSMS/ISA received raw schema audit "
        f"datasets={len({row.get('idno', '') for row in file_rows})} files={len(file_rows)} variables={len(variable_rows)} evidence_rows={len(evidence_rows)}."
    )


if __name__ == "__main__":
    main()
