from __future__ import annotations

import csv
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from common import REPORT_DIR, RESULT_DIR, TEMP_DIR, append_log, ensure_dirs, write_csv


FIRST_BATCH_PATH = TEMP_DIR / "first_batch_raw_acquisition_checklist.csv"
FIRST_BATCH_FILE_TARGETS_PATH = TEMP_DIR / "first_batch_raw_file_targets.csv"
CONCEPT_PATH = TEMP_DIR / "raw_ingestion_concept_checklist.csv"
PROTOCOL_PATH = TEMP_DIR / "raw_variable_verification_protocol.csv"
RAW_FILE_PATH = TEMP_DIR / "raw_schema_inventory" / "raw_file_inventory.csv"
RAW_VARIABLE_PATH = TEMP_DIR / "raw_schema_inventory" / "raw_variable_catalog.csv"

DATASET_GATE_PATH = RESULT_DIR / "first_batch_dataset_verification_gate.csv"
CONCEPT_TEMPLATE_PATH = TEMP_DIR / "first_batch_concept_verification_template.csv"
VARIABLE_TEMPLATE_PATH = TEMP_DIR / "first_batch_variable_verification_template.csv"
SUMMARY_PATH = RESULT_DIR / "first_batch_raw_verification_workbook_summary.csv"
REPORT_PATH = REPORT_DIR / "first_batch_raw_verification_workbook.md"

DATASET_GATE_COLUMNS = [
    "batch_rank",
    "country",
    "survey_name",
    "wave",
    "idno",
    "included_acquisition_sets",
    "raw_file_inventory_rows",
    "raw_variable_catalog_rows",
    "required_concept_rows",
    "concepts_with_metadata_support",
    "concepts_missing_metadata",
    "critical_concepts_missing_metadata",
    "concepts_ready_for_recipe_promotion",
    "current_gate_status",
    "next_action",
    "guardrail",
]

CONCEPT_COLUMNS = [
    "batch_rank",
    "country",
    "survey_name",
    "wave",
    "idno",
    "concept",
    "required_for",
    "is_financial_core",
    "is_double_failure_core",
    "is_design_core",
    "metadata_support_status",
    "high_confidence_rows",
    "moderate_confidence_rows",
    "candidate_files",
    "candidate_variables",
    "minimum_raw_evidence_needed",
    "verification_action",
    "raw_file_status",
    "raw_variable_status",
    "current_concept_gate",
    "fill_raw_file_used",
    "fill_raw_variable_used",
    "fill_value_label_pass",
    "fill_unit_or_recall_pass",
    "fill_merge_key_pass",
    "fill_sample_level_pass",
    "fill_missing_code_pass",
    "fill_promote_to_harmonization_recipe",
    "review_notes",
]

VARIABLE_COLUMNS = [
    "batch_rank",
    "country",
    "survey_name",
    "wave",
    "idno",
    "concept",
    "required_for",
    "candidate_rank_within_concept",
    "candidate_files",
    "candidate_raw_variable",
    "candidate_harmonized_variables",
    "raw_label",
    "metadata_confidence",
    "confidence_reason",
    "verification_checks",
    "minimum_raw_evidence_needed",
    "raw_file_status",
    "raw_variable_status",
    "verification_status",
    "harmonization_decision",
    "fill_raw_file_used",
    "fill_raw_variable_used",
    "fill_variable_label_verified",
    "fill_value_distribution_checked",
    "fill_missing_codes_documented",
    "fill_unit_recall_period_documented",
    "fill_merge_key_level_verified",
    "fill_outlier_or_skip_pattern_notes",
    "fill_promote_to_harmonization_recipe",
    "review_notes",
]

SUMMARY_COLUMNS = ["metric", "value", "interpretation"]

FINANCIAL_CORE = {"total_consumption_or_income", "oop_health_expenditure", "survey_weight", "survey_timing", "climate_geography"}
DOUBLE_FAILURE_CORE = {"health_need", "care_or_barrier"}
DESIGN_CORE = {"household_id", "psu_cluster", "strata", "survey_weight", "survey_timing", "climate_geography"}


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


def split_values(value: str) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for item in (value or "").replace(",", ";").split(";"):
        clean = item.strip()
        if clean and clean not in seen:
            out.append(clean)
            seen.add(clean)
    return out


def compact(values: list[str], limit: int = 20) -> str:
    seen: set[str] = set()
    out: list[str] = []
    for value in values:
        clean = (value or "").strip()
        if clean and clean not in seen:
            out.append(clean)
            seen.add(clean)
        if len(out) >= limit:
            break
    return ";".join(out)


def grouped(rows: list[dict[str, str]], field: str) -> dict[str, list[dict[str, str]]]:
    out: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        value = row.get(field, "")
        if value:
            out[value].append(row)
    return out


def first_batch_by_id() -> dict[str, dict[str, str]]:
    rows = read_csv_dicts(FIRST_BATCH_PATH)
    return {row.get("idno", ""): row for row in rows if row.get("idno", "")}


def infer_idno(text: str, idnos: set[str]) -> str:
    low = (text or "").lower().replace("\\", "/")
    for idno in sorted(idnos, key=len, reverse=True):
        if idno and idno.lower() in low:
            return idno
    return ""


def raw_file_counts(raw_files: list[dict[str, str]], idnos: set[str]) -> Counter[str]:
    counts: Counter[str] = Counter()
    for row in raw_files:
        idno = infer_idno(" ".join(row.values()), idnos)
        if idno:
            counts[idno] += 1
    return counts


def raw_variable_counts(raw_variables: list[dict[str, str]], idnos: set[str]) -> Counter[str]:
    counts: Counter[str] = Counter()
    for row in raw_variables:
        idno = infer_idno(" ".join(row.values()), idnos)
        if idno:
            counts[idno] += 1
    return counts


def raw_files_present_for_id(raw_files: list[dict[str, str]], idno: str) -> list[str]:
    present = []
    idno_low = idno.lower()
    for row in raw_files:
        text = " ".join(row.values()).lower().replace("\\", "/")
        if idno_low in text:
            present.append(row.get("source_path", ""))
    return present


def raw_variables_present_for_id(raw_variables: list[dict[str, str]], idno: str) -> list[dict[str, str]]:
    idno_low = idno.lower()
    out = []
    for row in raw_variables:
        text = " ".join(row.values()).lower().replace("\\", "/")
        if idno_low in text:
            out.append(row)
    return out


def file_status(candidate_files: str, present_paths: list[str]) -> str:
    files = split_values(candidate_files)
    if not files:
        return "no_candidate_file_metadata"
    if not present_paths:
        return "raw_files_not_present"
    present_text = " ".join(present_paths).lower().replace("\\", "/")
    matches = [name for name in files if name.lower() in present_text]
    if matches:
        return "candidate_file_present"
    return "raw_files_present_candidate_file_not_matched"


def variable_status(candidate_variables: str, present_variables: list[dict[str, str]]) -> str:
    variables = split_values(candidate_variables)
    if not variables:
        return "no_candidate_variable_metadata"
    if not present_variables:
        return "raw_variable_catalog_absent"
    present_names = {row.get("variable_name", "").lower() for row in present_variables}
    matches = [name for name in variables if name.lower() in present_names]
    if matches:
        return "candidate_variable_present"
    return "raw_variable_catalog_present_candidate_not_matched"


def concept_gate(metadata_status: str, raw_file_status: str, raw_variable_status: str) -> str:
    if metadata_status == "missing_from_metadata":
        return "blocked_missing_metadata_candidate"
    if raw_file_status == "raw_files_not_present":
        return "blocked_raw_file_missing"
    if raw_variable_status == "raw_variable_catalog_absent":
        return "blocked_raw_variable_catalog_missing"
    if raw_file_status == "candidate_file_present" and raw_variable_status == "candidate_variable_present":
        return "ready_for_manual_value_label_unit_key_audit"
    return "blocked_raw_candidate_not_matched"


def verification_status(raw_file_status: str, raw_variable_status: str) -> tuple[str, str]:
    if raw_file_status == "candidate_file_present" and raw_variable_status == "candidate_variable_present":
        return "ready_for_manual_value_audit", "blocked_until_manual_value_label_unit_recall_key_audit_passes"
    if raw_file_status == "raw_files_not_present":
        return "raw_not_inspected", "blocked_until_raw_files_present"
    if raw_variable_status == "raw_variable_catalog_absent":
        return "raw_schema_not_inspected", "blocked_until_raw_variable_catalog_present"
    return "raw_candidate_not_matched", "blocked_until_candidate_file_and_variable_match"


def build_concept_rows(first_batch: dict[str, dict[str, str]], raw_files: list[dict[str, str]], raw_variables: list[dict[str, str]]) -> list[dict[str, str]]:
    concepts_by_id = grouped(read_csv_dicts(CONCEPT_PATH), "idno")
    rows: list[dict[str, str]] = []
    for idno, batch in first_batch.items():
        present_paths = raw_files_present_for_id(raw_files, idno)
        present_vars = raw_variables_present_for_id(raw_variables, idno)
        for concept in concepts_by_id.get(idno, []):
            raw_file_status = file_status(concept.get("candidate_files", ""), present_paths)
            raw_variable_status = variable_status(concept.get("candidate_variables", ""), present_vars)
            concept_name = concept.get("concept", "")
            rows.append(
                {
                    "batch_rank": batch.get("batch_rank", ""),
                    "country": batch.get("country", ""),
                    "survey_name": batch.get("survey_name", ""),
                    "wave": batch.get("wave", ""),
                    "idno": idno,
                    "concept": concept_name,
                    "required_for": concept.get("required_for", ""),
                    "is_financial_core": "1" if concept_name in FINANCIAL_CORE else "0",
                    "is_double_failure_core": "1" if concept_name in DOUBLE_FAILURE_CORE else "0",
                    "is_design_core": "1" if concept_name in DESIGN_CORE else "0",
                    "metadata_support_status": concept.get("metadata_support_status", ""),
                    "high_confidence_rows": concept.get("high_confidence_rows", ""),
                    "moderate_confidence_rows": concept.get("moderate_confidence_rows", ""),
                    "candidate_files": concept.get("candidate_files", ""),
                    "candidate_variables": concept.get("candidate_variables", ""),
                    "minimum_raw_evidence_needed": concept.get("minimum_raw_evidence_needed", ""),
                    "verification_action": concept.get("verification_action", ""),
                    "raw_file_status": raw_file_status,
                    "raw_variable_status": raw_variable_status,
                    "current_concept_gate": concept_gate(concept.get("metadata_support_status", ""), raw_file_status, raw_variable_status),
                    "fill_raw_file_used": "",
                    "fill_raw_variable_used": "",
                    "fill_value_label_pass": "",
                    "fill_unit_or_recall_pass": "",
                    "fill_merge_key_pass": "",
                    "fill_sample_level_pass": "",
                    "fill_missing_code_pass": "",
                    "fill_promote_to_harmonization_recipe": "",
                    "review_notes": "",
                }
            )
    rows.sort(key=lambda row: (safe_int(row["batch_rank"]), row["concept"]))
    return rows


def build_variable_rows(first_batch: dict[str, dict[str, str]], raw_files: list[dict[str, str]], raw_variables: list[dict[str, str]]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    protocol_rows = [row for row in read_csv_dicts(PROTOCOL_PATH) if row.get("idno", "") in first_batch]
    for protocol in protocol_rows:
        idno = protocol.get("idno", "")
        batch = first_batch[idno]
        present_paths = raw_files_present_for_id(raw_files, idno)
        present_vars = raw_variables_present_for_id(raw_variables, idno)
        raw_file_status = file_status(protocol.get("candidate_files", ""), present_paths)
        raw_variable_status = variable_status(protocol.get("candidate_raw_variable", ""), present_vars)
        status, decision = verification_status(raw_file_status, raw_variable_status)
        rows.append(
            {
                "batch_rank": batch.get("batch_rank", ""),
                "country": batch.get("country", ""),
                "survey_name": batch.get("survey_name", ""),
                "wave": batch.get("wave", ""),
                "idno": idno,
                "concept": protocol.get("concept", ""),
                "required_for": protocol.get("required_for", ""),
                "candidate_rank_within_concept": protocol.get("candidate_rank_within_concept", ""),
                "candidate_files": protocol.get("candidate_files", ""),
                "candidate_raw_variable": protocol.get("candidate_raw_variable", ""),
                "candidate_harmonized_variables": protocol.get("candidate_harmonized_variables", ""),
                "raw_label": protocol.get("raw_label", ""),
                "metadata_confidence": protocol.get("metadata_confidence", ""),
                "confidence_reason": protocol.get("confidence_reason", ""),
                "verification_checks": protocol.get("verification_checks", ""),
                "minimum_raw_evidence_needed": protocol.get("minimum_raw_evidence_needed", ""),
                "raw_file_status": raw_file_status,
                "raw_variable_status": raw_variable_status,
                "verification_status": status,
                "harmonization_decision": decision,
                "fill_raw_file_used": "",
                "fill_raw_variable_used": "",
                "fill_variable_label_verified": "",
                "fill_value_distribution_checked": "",
                "fill_missing_codes_documented": "",
                "fill_unit_recall_period_documented": "",
                "fill_merge_key_level_verified": "",
                "fill_outlier_or_skip_pattern_notes": "",
                "fill_promote_to_harmonization_recipe": "",
                "review_notes": "",
            }
        )
    rows.sort(key=lambda row: (safe_int(row["batch_rank"]), row["concept"], safe_int(row["candidate_rank_within_concept"])))
    return rows


def build_dataset_gate_rows(first_batch: dict[str, dict[str, str]], concept_rows: list[dict[str, str]], raw_files: list[dict[str, str]], raw_variables: list[dict[str, str]]) -> list[dict[str, str]]:
    concept_by_id = grouped(concept_rows, "idno")
    idnos = set(first_batch)
    file_counts = raw_file_counts(raw_files, idnos)
    variable_counts = raw_variable_counts(raw_variables, idnos)
    rows: list[dict[str, str]] = []
    for idno, batch in sorted(first_batch.items(), key=lambda item: safe_int(item[1].get("batch_rank"))):
        concepts = concept_by_id.get(idno, [])
        missing_metadata = [row["concept"] for row in concepts if row.get("metadata_support_status") == "missing_from_metadata"]
        critical_missing = [
            row["concept"]
            for row in concepts
            if row.get("metadata_support_status") == "missing_from_metadata"
            and (row.get("is_financial_core") == "1" or row.get("is_double_failure_core") == "1" or row.get("is_design_core") == "1")
        ]
        ready = [row for row in concepts if row.get("current_concept_gate") == "ready_for_manual_value_label_unit_key_audit"]
        if file_counts[idno] == 0:
            status = "blocked_raw_files_absent"
            next_action = "download complete original raw package into local target folder"
        elif variable_counts[idno] == 0:
            status = "blocked_raw_variable_catalog_absent"
            next_action = "run script/03_inspect_raw_schemas.py and verify raw variable catalog extraction"
        elif critical_missing:
            status = "blocked_critical_metadata_candidate_missing"
            next_action = "inspect codebooks/raw schemas manually for missing critical concepts or replace dataset"
        elif len(ready) == len([row for row in concepts if row.get("metadata_support_status") != "missing_from_metadata"]):
            status = "ready_for_manual_value_label_unit_key_audit"
            next_action = "fill concept and variable verification templates before any harmonization recipe promotion"
        else:
            status = "blocked_candidate_file_or_variable_not_matched"
            next_action = "map downloaded raw filenames/variables to candidate metadata and rerun workbook"
        rows.append(
            {
                "batch_rank": batch.get("batch_rank", ""),
                "country": batch.get("country", ""),
                "survey_name": batch.get("survey_name", ""),
                "wave": batch.get("wave", ""),
                "idno": idno,
                "included_acquisition_sets": batch.get("included_acquisition_sets", ""),
                "raw_file_inventory_rows": str(file_counts[idno]),
                "raw_variable_catalog_rows": str(variable_counts[idno]),
                "required_concept_rows": str(len(concepts)),
                "concepts_with_metadata_support": str(sum(1 for row in concepts if row.get("metadata_support_status") != "missing_from_metadata")),
                "concepts_missing_metadata": compact(missing_metadata),
                "critical_concepts_missing_metadata": compact(critical_missing),
                "concepts_ready_for_recipe_promotion": str(len(ready)),
                "current_gate_status": status,
                "next_action": next_action,
                "guardrail": "do not write data outputs or temp/harmonization_recipe.csv until all critical raw evidence fields pass",
            }
        )
    return rows


def build_summary(dataset_rows: list[dict[str, str]], concept_rows: list[dict[str, str]], variable_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    dataset_status = Counter(row["current_gate_status"] for row in dataset_rows)
    concept_gate = Counter(row["current_concept_gate"] for row in concept_rows)
    variable_status = Counter(row["verification_status"] for row in variable_rows)
    rows = [
        {"metric": "first_batch_dataset_gate_rows", "value": str(len(dataset_rows)), "interpretation": "Dataset-level verification gate rows."},
        {"metric": "first_batch_concept_template_rows", "value": str(len(concept_rows)), "interpretation": "Concept-level verification template rows."},
        {"metric": "first_batch_variable_template_rows", "value": str(len(variable_rows)), "interpretation": "Variable-level verification template rows."},
        {"metric": "datasets_ready_for_manual_value_audit", "value": str(dataset_status.get("ready_for_manual_value_label_unit_key_audit", 0)), "interpretation": "Datasets with raw schemas matched to critical concepts."},
        {"metric": "concepts_ready_for_manual_value_audit", "value": str(concept_gate.get("ready_for_manual_value_label_unit_key_audit", 0)), "interpretation": "Concept rows ready for value/label/unit/key audit."},
        {"metric": "variables_ready_for_manual_value_audit", "value": str(variable_status.get("ready_for_manual_value_audit", 0)), "interpretation": "Variable rows ready for value/label/unit/key audit."},
    ]
    for status, count in sorted(dataset_status.items()):
        rows.append({"metric": f"dataset_gate_{status}", "value": str(count), "interpretation": "Dataset gate status count."})
    for status, count in sorted(concept_gate.items()):
        rows.append({"metric": f"concept_gate_{status}", "value": str(count), "interpretation": "Concept gate status count."})
    for status, count in sorted(variable_status.items()):
        rows.append({"metric": f"variable_status_{status}", "value": str(count), "interpretation": "Variable verification status count."})
    return rows


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


def write_report(dataset_rows: list[dict[str, str]], concept_rows: list[dict[str, str]], variable_rows: list[dict[str, str]], summary: list[dict[str, str]]) -> None:
    dataset_status = Counter(row["current_gate_status"] for row in dataset_rows)
    concept_gate = Counter(row["current_concept_gate"] for row in concept_rows)
    variable_status = Counter(row["verification_status"] for row in variable_rows)
    summary_table = "\n".join(f"| {row['metric']} | {row['value']} | {row['interpretation']} |" for row in summary)
    REPORT_PATH.write_text(
        f"""# First-Batch Raw Verification Workbook

Status: fillable post-download verification workbook. It does not verify any dataset by itself. It converts the first-batch raw acquisition plan into dataset, concept, and variable rows that must be completed after raw files are downloaded and schema-inspected.

## Summary

| Metric | Value | Interpretation |
|---|---:|---|
{summary_table}

## Dataset Gate Status

{markdown_count_table(dataset_status, 'Dataset gate') if dataset_rows else 'No dataset gate rows exist.'}

## Concept Gate Status

{markdown_count_table(concept_gate, 'Concept gate') if concept_rows else 'No concept verification rows exist.'}

## Variable Verification Status

{markdown_count_table(variable_status, 'Variable status') if variable_rows else 'No variable verification rows exist.'}

## Dataset Gate Rows

{markdown_rows(dataset_rows, ['batch_rank', 'idno', 'country', 'wave', 'raw_file_inventory_rows', 'raw_variable_catalog_rows', 'current_gate_status', 'next_action'], 20)}

## How To Use

1. Download complete original raw packages into each first-batch target folder.
2. Run `python script/17_audit_raw_downloads.py` and `python script/03_inspect_raw_schemas.py`.
3. Rerun `python script/38_build_first_batch_raw_verification_workbook.py`.
4. Fill the blank `fill_*` columns in `temp/first_batch_concept_verification_template.csv` and `temp/first_batch_variable_verification_template.csv` only after inspecting raw values, labels, units, recall periods, missing codes, levels, and merge keys.
5. Promote a row toward `temp/harmonization_recipe.csv` only when all critical evidence fields pass.

## Guardrails

- Metadata-only candidate variables do not prove concept availability.
- A raw schema match still does not prove that values, units, recall periods, or skip patterns are usable.
- Do not construct outcomes, climate links, models, mechanisms, or policy simulations from this workbook alone.

## Machine-Readable Outputs

- `result/first_batch_dataset_verification_gate.csv`
- `temp/first_batch_concept_verification_template.csv`
- `temp/first_batch_variable_verification_template.csv`
- `result/first_batch_raw_verification_workbook_summary.csv`
""",
        encoding="utf-8",
    )


def main() -> None:
    ensure_dirs()
    first_batch = first_batch_by_id()
    raw_files = read_csv_dicts(RAW_FILE_PATH)
    raw_variables = read_csv_dicts(RAW_VARIABLE_PATH)
    concept_rows = build_concept_rows(first_batch, raw_files, raw_variables)
    variable_rows = build_variable_rows(first_batch, raw_files, raw_variables)
    dataset_rows = build_dataset_gate_rows(first_batch, concept_rows, raw_files, raw_variables)
    summary = build_summary(dataset_rows, concept_rows, variable_rows)
    write_csv(DATASET_GATE_PATH, dataset_rows, DATASET_GATE_COLUMNS)
    write_csv(CONCEPT_TEMPLATE_PATH, concept_rows, CONCEPT_COLUMNS)
    write_csv(VARIABLE_TEMPLATE_PATH, variable_rows, VARIABLE_COLUMNS)
    write_csv(SUMMARY_PATH, summary, SUMMARY_COLUMNS)
    write_report(dataset_rows, concept_rows, variable_rows, summary)
    append_log(
        TEMP_DIR / "audit_log.md",
        f"Built first-batch raw verification workbook dataset_rows={len(dataset_rows)} concept_rows={len(concept_rows)} variable_rows={len(variable_rows)}.",
    )
    print(f"First-batch raw verification workbook dataset_rows={len(dataset_rows)} concept_rows={len(concept_rows)} variable_rows={len(variable_rows)}.")


if __name__ == "__main__":
    main()
