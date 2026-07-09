from __future__ import annotations

import csv
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from common import REPORT_DIR, RESULT_DIR, TEMP_DIR, append_log, ensure_dirs, write_csv


QUEUE_PATH = TEMP_DIR / "first_batch_manual_download_file_queue.csv"
SCHEMA_FILE_PATH = TEMP_DIR / "raw_schema_inventory" / "schema_file_inventory.csv"
METADATA_VARIABLE_PATH = TEMP_DIR / "raw_schema_inventory" / "metadata_variable_catalog.csv"
DOC_AUDIT_PATH = TEMP_DIR / "first_batch_public_documentation_audit.csv"

TRACE_PATH = TEMP_DIR / "first_batch_file_source_traceability.csv"
SUMMARY_PATH = RESULT_DIR / "first_batch_file_source_traceability_summary.csv"
REPORT_PATH = REPORT_DIR / "first_batch_file_source_traceability.md"

TRACE_COLUMNS = [
    "batch_rank",
    "idno",
    "country",
    "wave",
    "file_name",
    "target_reasons",
    "candidate_categories",
    "candidate_harmonized_variables",
    "candidate_variable_count",
    "metadata_file_status",
    "metadata_variable_status",
    "candidate_examples_checked",
    "candidate_examples_found",
    "candidate_examples_missing",
    "schema_fid",
    "schema_cases",
    "schema_variable_count",
    "schema_unit_guess",
    "schema_module_guess",
    "schema_source_url",
    "public_data_dictionary_status",
    "public_metadata_json_status",
    "public_metadata_ddi_status",
    "public_pdf_documentation_status",
    "source_trace_status",
    "interpretation",
]

SUMMARY_COLUMNS = ["metric", "value", "interpretation"]


def read_csv_dicts(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def safe_int(value: Any, default: int = 0) -> int:
    try:
        return int(float(str(value).strip()))
    except (TypeError, ValueError):
        return default


def split_semicolon(value: str) -> list[str]:
    out: list[str] = []
    seen: set[str] = set()
    for part in (value or "").split(";"):
        item = part.strip()
        if item and item not in seen:
            out.append(item)
            seen.add(item)
    return out


def is_saved(status: str) -> bool:
    return status == "saved" or status.startswith("saved_existing_")


def doc_status_by_idno_resource(rows: list[dict[str, str]]) -> dict[tuple[str, str], str]:
    out: dict[tuple[str, str], str] = {}
    for row in rows:
        out[(row.get("idno", ""), row.get("resource_type", ""))] = row.get("coverage_status", "")
    return out


def normalize_var(value: str) -> str:
    return (value or "").strip().lower()


def build_trace_rows() -> list[dict[str, str]]:
    queue = read_csv_dicts(QUEUE_PATH)
    schema_files = read_csv_dicts(SCHEMA_FILE_PATH)
    metadata_variables = read_csv_dicts(METADATA_VARIABLE_PATH)
    docs = doc_status_by_idno_resource(read_csv_dicts(DOC_AUDIT_PATH))

    schema_by_key = {(row.get("idno", ""), row.get("file_name", "")): row for row in schema_files}
    variable_sets: dict[tuple[str, str], set[str]] = defaultdict(set)
    for row in metadata_variables:
        variable_sets[(row.get("idno", ""), row.get("file_name", ""))].add(normalize_var(row.get("variable_name", "")))

    rows: list[dict[str, str]] = []
    for item in queue:
        key = (item.get("idno", ""), item.get("file_name", ""))
        schema = schema_by_key.get(key, {})
        variables = variable_sets.get(key, set())
        examples = split_semicolon(item.get("candidate_raw_variables_examples", ""))
        found = [var for var in examples if normalize_var(var) in variables]
        missing = [var for var in examples if normalize_var(var) not in variables]
        data_dict_status = docs.get((item.get("idno", ""), "data_dictionary_html"), "")
        json_status = docs.get((item.get("idno", ""), "metadata_json"), "")
        ddi_status = docs.get((item.get("idno", ""), "metadata_ddi_xml"), "")
        pdf_status = docs.get((item.get("idno", ""), "pdf_documentation"), "")
        metadata_file_status = "metadata_file_found" if schema else "metadata_file_not_found"
        if not schema:
            trace_status = "unsupported_queue_file_missing_from_schema_inventory"
            interpretation = "Queued module is not present in the public metadata file inventory; review before manual download targeting."
        elif examples and not found:
            trace_status = "metadata_file_found_candidate_examples_not_confirmed"
            interpretation = "The public file entry exists, but the queued candidate examples were not found in the metadata variable catalog."
        elif not is_saved(data_dict_status) or not is_saved(json_status):
            trace_status = "metadata_file_found_public_documentation_incomplete"
            interpretation = "The public file entry exists, but one or more public documentation snapshots are incomplete."
        else:
            trace_status = "metadata_file_and_examples_supported"
            interpretation = "Queued module is backed by public schema metadata and candidate variable examples; raw values still unverified."
        rows.append(
            {
                "batch_rank": item.get("batch_rank", ""),
                "idno": item.get("idno", ""),
                "country": item.get("country", ""),
                "wave": item.get("wave", ""),
                "file_name": item.get("file_name", ""),
                "target_reasons": item.get("target_reasons", ""),
                "candidate_categories": item.get("candidate_categories", ""),
                "candidate_harmonized_variables": item.get("candidate_harmonized_variables", ""),
                "candidate_variable_count": item.get("candidate_variable_count", ""),
                "metadata_file_status": metadata_file_status,
                "metadata_variable_status": "metadata_variables_found" if variables else "metadata_variables_not_found",
                "candidate_examples_checked": str(len(examples)),
                "candidate_examples_found": str(len(found)),
                "candidate_examples_missing": ";".join(missing[:20]),
                "schema_fid": schema.get("fid", ""),
                "schema_cases": schema.get("cases", ""),
                "schema_variable_count": schema.get("variable_count", ""),
                "schema_unit_guess": schema.get("unit_guess", ""),
                "schema_module_guess": schema.get("module_guess", ""),
                "schema_source_url": schema.get("source_url", ""),
                "public_data_dictionary_status": data_dict_status,
                "public_metadata_json_status": json_status,
                "public_metadata_ddi_status": ddi_status,
                "public_pdf_documentation_status": pdf_status,
                "source_trace_status": trace_status,
                "interpretation": interpretation,
            }
        )
    rows.sort(key=lambda row: (safe_int(row["batch_rank"], 9999), row["source_trace_status"], row["file_name"]))
    return rows


def build_summary(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    status_counts = Counter(row["source_trace_status"] for row in rows)
    file_status_counts = Counter(row["metadata_file_status"] for row in rows)
    variable_status_counts = Counter(row["metadata_variable_status"] for row in rows)
    datasets = {row["idno"] for row in rows if row.get("idno")}
    unsupported = sum(1 for row in rows if row["source_trace_status"].startswith("unsupported_"))
    examples_checked = sum(safe_int(row["candidate_examples_checked"]) for row in rows)
    examples_found = sum(safe_int(row["candidate_examples_found"]) for row in rows)
    rows_out = [
        {"metric": "first_batch_file_source_traceability_rows", "value": str(len(rows)), "interpretation": "First-batch queued file/module source traceability rows."},
        {"metric": "first_batch_file_source_traceability_dataset_rows", "value": str(len(datasets)), "interpretation": "Datasets represented in file-source traceability."},
        {"metric": "first_batch_file_source_traceability_unsupported_rows", "value": str(unsupported), "interpretation": "Queued files missing from public schema inventory."},
        {"metric": "first_batch_candidate_variable_examples_checked", "value": str(examples_checked), "interpretation": "Candidate raw-variable examples checked against metadata variable catalog."},
        {"metric": "first_batch_candidate_variable_examples_found", "value": str(examples_found), "interpretation": "Candidate examples found in metadata variable catalog."},
    ]
    for status, count in sorted(status_counts.items()):
        rows_out.append({"metric": f"source_trace_status_{status}", "value": str(count), "interpretation": "File-source trace status count."})
    for status, count in sorted(file_status_counts.items()):
        rows_out.append({"metric": f"metadata_file_status_{status}", "value": str(count), "interpretation": "Metadata file status count."})
    for status, count in sorted(variable_status_counts.items()):
        rows_out.append({"metric": f"metadata_variable_status_{status}", "value": str(count), "interpretation": "Metadata variable status count."})
    return rows_out


def markdown_rows(rows: list[dict[str, str]], columns: list[str], limit: int = 20) -> str:
    lines = ["| " + " | ".join(columns) + " |", "|" + "|".join("---" for _ in columns) + "|"]
    for row in rows[:limit]:
        values = []
        for column in columns:
            value = (row.get(column, "") or "").replace("|", "/")
            if len(value) > 120:
                value = value[:117] + "..."
            values.append(value)
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines)


def markdown_count_table(counter: Counter[str], label: str) -> str:
    lines = [f"| {label} | Count |", "|---|---:|"]
    for key, count in counter.most_common():
        lines.append(f"| {key or 'blank'} | {count} |")
    return "\n".join(lines)


def write_report(rows: list[dict[str, str]], summary: list[dict[str, str]]) -> None:
    status_counts = Counter(row["source_trace_status"] for row in rows)
    file_counts = Counter(row["metadata_file_status"] for row in rows)
    unresolved = [row for row in rows if row["source_trace_status"] != "metadata_file_and_examples_supported"]
    summary_table = "\n".join(f"| {row['metric']} | {row['value']} | {row['interpretation']} |" for row in summary)
    REPORT_PATH.write_text(
        f"""# First-Batch File Source Traceability

Status: metadata-source audit only. This checks whether first-batch manual file/module targets are backed by the public World Bank schema file inventory, metadata variable catalog, and public documentation snapshots. It does not verify raw files, raw values, labels, units, recall periods, missing codes, or merge keys.

## Summary

| Metric | Value | Interpretation |
|---|---:|---|
{summary_table}

## Source Trace Status

{markdown_count_table(status_counts, 'Source trace status') if rows else 'No file-source traceability rows exist.'}

## Metadata File Status

{markdown_count_table(file_counts, 'Metadata file status') if rows else 'No file-source traceability rows exist.'}

## Rows Needing Review

{markdown_rows(unresolved, ['batch_rank', 'idno', 'file_name', 'source_trace_status', 'candidate_examples_missing'], 25) if unresolved else 'All queued files have public schema and candidate-example support.'}

## Guardrails

- A supported source trace means the module name and example variables appear in public metadata only.
- This audit does not prove the raw file was downloaded or that values, labels, units, recall periods, missing codes, or merge keys are valid.
- Do not promote harmonization, outcomes, climate linkage, models, causal claims, or policy simulations from this audit alone.

## Machine-Readable Outputs

- `temp/first_batch_file_source_traceability.csv`
- `result/first_batch_file_source_traceability_summary.csv`
""",
        encoding="utf-8",
    )


def main() -> None:
    ensure_dirs()
    rows = build_trace_rows()
    summary = build_summary(rows)
    write_csv(TRACE_PATH, rows, TRACE_COLUMNS)
    write_csv(SUMMARY_PATH, summary, SUMMARY_COLUMNS)
    write_report(rows, summary)
    unsupported = sum(1 for row in rows if row["source_trace_status"].startswith("unsupported_"))
    append_log(TEMP_DIR / "audit_log.md", f"Built first-batch file source traceability rows={len(rows)} unsupported={unsupported}.")
    print(f"First-batch file source traceability rows={len(rows)} unsupported={unsupported}.")


if __name__ == "__main__":
    main()
