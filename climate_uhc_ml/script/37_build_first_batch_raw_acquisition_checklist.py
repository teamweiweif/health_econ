from __future__ import annotations

import csv
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from common import REPORT_DIR, RESULT_DIR, TEMP_DIR, append_log, ensure_dirs, write_csv


BUNDLES_PATH = TEMP_DIR / "minimum_viable_download_bundles.csv"
INTAKE_PATH = TEMP_DIR / "raw_download_intake_manifest.csv"
EXPECTED_PATH = TEMP_DIR / "raw_download_expected_files.csv"
CONCEPT_PATH = TEMP_DIR / "raw_ingestion_concept_checklist.csv"
RAW_FILE_PATH = TEMP_DIR / "raw_schema_inventory" / "raw_file_inventory.csv"
RAW_VARIABLE_PATH = TEMP_DIR / "raw_schema_inventory" / "raw_variable_catalog.csv"

CHECKLIST_PATH = TEMP_DIR / "first_batch_raw_acquisition_checklist.csv"
FILE_TARGETS_PATH = TEMP_DIR / "first_batch_raw_file_targets.csv"
SUMMARY_PATH = RESULT_DIR / "first_batch_raw_acquisition_summary.csv"
REPORT_PATH = REPORT_DIR / "first_batch_raw_acquisition_checklist.md"

CHECKLIST_COLUMNS = [
    "batch_rank",
    "country",
    "survey_name",
    "wave",
    "idno",
    "included_acquisition_sets",
    "rules_tested_by_batch",
    "official_url",
    "local_target_folder",
    "raw_intake_status",
    "folder_exists",
    "file_count",
    "raw_tabular_file_count",
    "archive_file_count",
    "documentation_file_count",
    "expected_module_rows",
    "expected_core_module_rows",
    "expected_missing_rows",
    "financial_core_expected_files",
    "access_core_expected_files",
    "geography_timing_design_expected_files",
    "top_modules_to_verify_first",
    "concepts_to_verify",
    "download_instruction",
    "post_download_commands",
    "pass_after_download_evidence",
    "fail_closed_stop_rule",
]

FILE_TARGET_COLUMNS = [
    "batch_rank",
    "idno",
    "country",
    "wave",
    "file_name",
    "target_reason",
    "source_field",
    "module_priority_role",
    "candidate_categories",
    "candidate_harmonized_variables",
    "candidate_variable_count",
    "candidate_raw_variables_examples",
    "expected_file_status",
    "present_matching_files",
    "verification_action",
]

SUMMARY_COLUMNS = ["metric", "value", "interpretation"]

CORE_BATCH_SETS = {"financial_6_country_probe", "double_failure_10_wave_probe"}


def read_csv_dicts(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def safe_int(value: Any, default: int = 999999) -> int:
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


def by_id(rows: list[dict[str, str]], field: str) -> dict[str, dict[str, str]]:
    out: dict[str, dict[str, str]] = {}
    for row in rows:
        value = row.get(field, "")
        if value and value not in out:
            out[value] = row
    return out


def grouped(rows: list[dict[str, str]], field: str) -> dict[str, list[dict[str, str]]]:
    out: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        value = row.get(field, "")
        if value:
            out[value].append(row)
    return out


def selected_bundles(bundles: list[dict[str, str]]) -> list[dict[str, str]]:
    rows = []
    for row in bundles:
        sets = set(split_values(row.get("included_acquisition_sets", "")))
        if sets & CORE_BATCH_SETS:
            rows.append(row)
    rows.sort(key=lambda row: safe_int(row.get("bundle_rank")))
    return rows


def rules_for_sets(value: str) -> str:
    sets = set(split_values(value))
    rules = []
    if "financial_6_country_probe" in sets:
        rules.append("tests Phase 13 rule: at least 6 countries with consumption/OOP/geography/timing")
    if "double_failure_10_wave_probe" in sets:
        rules.append("tests Phase 13 rule: at least 10 country-waves with financial hardship plus forgone-care support")
    return "; ".join(rules)


def raw_count_by_id(rows: list[dict[str, str]]) -> Counter[str]:
    counts: Counter[str] = Counter()
    for row in rows:
        idno = row.get("idno", "")
        if idno:
            counts[idno] += 1
    return counts


def concept_summary(rows: list[dict[str, str]], limit: int = 12) -> str:
    pieces = []
    for row in rows:
        concept = row.get("concept", "")
        files = row.get("candidate_files", "")
        variables = row.get("candidate_variables", "")
        if concept:
            pieces.append(f"{concept}: files={files}; variables={variables}")
    return compact(pieces, limit)


def top_module_file_names(value: str, limit: int = 12) -> list[str]:
    names = [match.group(1).strip() for match in re.finditer(r"([^;\[\]]+?)\s*\[[^\]]*\]", value or "")]
    if not names:
        names = [piece.split("[", 1)[0].strip() for piece in split_values(value)]
    return [name for name in names if name][:limit]


def expected_index(rows: list[dict[str, str]]) -> dict[tuple[str, str], dict[str, str]]:
    out: dict[tuple[str, str], dict[str, str]] = {}
    for row in rows:
        idno = row.get("dataset_idno", "")
        file_name = row.get("expected_file_name", "")
        if idno and file_name and (idno, file_name) not in out:
            out[(idno, file_name)] = row
    return out


def target_files_for_bundle(bundle: dict[str, str]) -> list[dict[str, str]]:
    fields = [
        ("financial_core_expected_files", "financial core file"),
        ("access_core_expected_files", "access core file"),
        ("geography_timing_design_expected_files", "geography/timing/design file"),
    ]
    rows: list[dict[str, str]] = []
    seen: set[tuple[str, str]] = set()
    for field, reason in fields:
        for file_name in split_values(bundle.get(field, "")):
            key = (file_name, field)
            if file_name and key not in seen:
                rows.append({"file_name": file_name, "source_field": field, "target_reason": reason})
                seen.add(key)
    for file_name in top_module_file_names(bundle.get("top_modules_to_verify_first", "")):
        if not file_name:
            continue
        key = (file_name, "top_modules_to_verify_first")
        if key in seen:
            continue
        rows.append({"file_name": file_name, "source_field": "top_modules_to_verify_first", "target_reason": "top metadata-supported module to inspect first"})
        seen.add(key)
    return rows


def build_checklist_and_targets() -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    bundles = selected_bundles(read_csv_dicts(BUNDLES_PATH))
    intake_by_id = by_id(read_csv_dicts(INTAKE_PATH), "dataset_idno")
    expected_rows = read_csv_dicts(EXPECTED_PATH)
    expected_by_id = grouped(expected_rows, "dataset_idno")
    expected_by_key = expected_index(expected_rows)
    concepts_by_id = grouped(read_csv_dicts(CONCEPT_PATH), "idno")
    raw_file_counts = raw_count_by_id(read_csv_dicts(RAW_FILE_PATH))
    raw_variable_counts = raw_count_by_id(read_csv_dicts(RAW_VARIABLE_PATH))

    checklist: list[dict[str, str]] = []
    targets: list[dict[str, str]] = []
    for rank, bundle in enumerate(bundles, start=1):
        idno = bundle.get("idno", "")
        intake = intake_by_id.get(idno, {})
        expected = expected_by_id.get(idno, [])
        expected_missing = sum(1 for row in expected if row.get("expected_file_status") == "not_present")
        raw_file_rows = raw_file_counts.get(idno, 0)
        raw_variable_rows = raw_variable_counts.get(idno, 0)
        checklist.append(
            {
                "batch_rank": str(rank),
                "country": bundle.get("country", ""),
                "survey_name": bundle.get("survey_name", ""),
                "wave": bundle.get("wave", ""),
                "idno": idno,
                "included_acquisition_sets": bundle.get("included_acquisition_sets", ""),
                "rules_tested_by_batch": rules_for_sets(bundle.get("included_acquisition_sets", "")),
                "official_url": bundle.get("official_url", ""),
                "local_target_folder": bundle.get("local_target_folder", ""),
                "raw_intake_status": intake.get("intake_status", bundle.get("raw_intake_status", "")),
                "folder_exists": intake.get("folder_exists", ""),
                "file_count": intake.get("file_count", "0"),
                "raw_tabular_file_count": intake.get("raw_tabular_file_count", "0"),
                "archive_file_count": intake.get("archive_file_count", "0"),
                "documentation_file_count": intake.get("documentation_file_count", "0"),
                "expected_module_rows": intake.get("expected_module_rows", str(len(expected))),
                "expected_core_module_rows": intake.get("expected_core_module_rows", ""),
                "expected_missing_rows": str(expected_missing),
                "financial_core_expected_files": bundle.get("financial_core_expected_files", ""),
                "access_core_expected_files": bundle.get("access_core_expected_files", ""),
                "geography_timing_design_expected_files": bundle.get("geography_timing_design_expected_files", ""),
                "top_modules_to_verify_first": bundle.get("top_modules_to_verify_first", ""),
                "concepts_to_verify": concept_summary(concepts_by_id.get(idno, [])),
                "download_instruction": "download the complete original raw package plus all questionnaires/codebooks/documentation; keep archive and source filenames intact",
                "post_download_commands": "python script/17_audit_raw_downloads.py; python script/03_inspect_raw_schemas.py; python script/29_build_raw_variable_verification_protocol.py; python script/33_build_harmonization_recipe_gate.py; python script/35_build_empirical_readiness_dashboard.py; python script/37_build_first_batch_raw_acquisition_checklist.py",
                "pass_after_download_evidence": f"raw_file_inventory rows for idno >0 and raw_variable_catalog rows for idno >0; current raw_file_rows={raw_file_rows}; current raw_variable_rows={raw_variable_rows}",
                "fail_closed_stop_rule": "if any required concept lacks raw values, labels, units/recall period, merge key, or survey timing/geography evidence, do not promote the country-wave to harmonization/outcome/climate linkage",
            }
        )
        for target in target_files_for_bundle(bundle):
            expected_row = expected_by_key.get((idno, target["file_name"]), {})
            targets.append(
                {
                    "batch_rank": str(rank),
                    "idno": idno,
                    "country": bundle.get("country", ""),
                    "wave": bundle.get("wave", ""),
                    "file_name": target["file_name"],
                    "target_reason": target["target_reason"],
                    "source_field": target["source_field"],
                    "module_priority_role": expected_row.get("module_priority_role", ""),
                    "candidate_categories": expected_row.get("candidate_categories", ""),
                    "candidate_harmonized_variables": expected_row.get("candidate_harmonized_variables", ""),
                    "candidate_variable_count": expected_row.get("candidate_variable_count", ""),
                    "candidate_raw_variables_examples": expected_row.get("candidate_raw_variables_examples", ""),
                    "expected_file_status": expected_row.get("expected_file_status", "not_listed_in_expected_files"),
                    "present_matching_files": expected_row.get("present_matching_files", ""),
                    "verification_action": expected_row.get("verification_action", "inspect raw schema and verify values, labels, units, recall periods, levels, and merge keys before harmonization"),
                }
            )
    return checklist, targets


def build_summary(checklist: list[dict[str, str]], targets: list[dict[str, str]]) -> list[dict[str, str]]:
    countries = {row.get("country", "") for row in checklist if row.get("country", "")}
    financial_rows = [row for row in checklist if "financial_6_country_probe" in row.get("included_acquisition_sets", "")]
    double_rows = [row for row in checklist if "double_failure_10_wave_probe" in row.get("included_acquisition_sets", "")]
    intake_counts = Counter(row.get("raw_intake_status", "") for row in checklist)
    target_reason_counts = Counter(row.get("target_reason", "") for row in targets)
    rows = [
        {"metric": "first_batch_dataset_rows", "value": str(len(checklist)), "interpretation": "Dataset rows selected for the first manual raw acquisition batch."},
        {"metric": "first_batch_country_count", "value": str(len(countries)), "interpretation": "Unique countries in the first batch."},
        {"metric": "financial_probe_dataset_rows", "value": str(len(financial_rows)), "interpretation": "Rows testing the 6-country financial-protection no-go rule."},
        {"metric": "double_failure_probe_dataset_rows", "value": str(len(double_rows)), "interpretation": "Rows testing the 10-wave double-failure no-go rule."},
        {"metric": "first_batch_file_target_rows", "value": str(len(targets)), "interpretation": "File/module targets to inspect immediately after download."},
        {"metric": "first_batch_raw_tabular_file_rows", "value": str(sum(safe_int(row.get("raw_tabular_file_count"), 0) for row in checklist)), "interpretation": "Raw tabular files currently present across first-batch folders."},
        {"metric": "first_batch_archive_file_rows", "value": str(sum(safe_int(row.get("archive_file_count"), 0) for row in checklist)), "interpretation": "Raw archive files currently present across first-batch folders."},
    ]
    for status, count in sorted(intake_counts.items()):
        rows.append({"metric": f"first_batch_intake_status_{status or 'blank'}", "value": str(count), "interpretation": "First-batch raw intake status count."})
    for reason, count in sorted(target_reason_counts.items()):
        rows.append({"metric": f"first_batch_target_reason_{reason.replace('/', '_').replace(' ', '_') or 'blank'}", "value": str(count), "interpretation": "First-batch file target reason count."})
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


def write_report(checklist: list[dict[str, str]], targets: list[dict[str, str]], summary: list[dict[str, str]]) -> None:
    summary_table = "\n".join(f"| {row['metric']} | {row['value']} | {row['interpretation']} |" for row in summary)
    intake_counts = Counter(row.get("raw_intake_status", "") for row in checklist)
    target_counts = Counter(row.get("target_reason", "") for row in targets)
    report_targets = [row for row in targets if row.get("target_reason") in {"financial core file", "geography/timing/design file", "access core file"}]
    REPORT_PATH.write_text(
        f"""# First-Batch Raw Acquisition Checklist

Status: manual raw-data acquisition checklist only. It selects the smallest current batch that can test the first two Phase 13 no-go thresholds: 6 countries for financial protection and 10 country-waves for double-failure support. No dataset in this checklist is analysis-ready until raw files and raw variables are inspected.

## Summary

| Metric | Value | Interpretation |
|---|---:|---|
{summary_table}

## Intake Status

{markdown_count_table(intake_counts, 'Raw intake status') if checklist else 'No first-batch checklist rows exist.'}

## Target Reason Counts

{markdown_count_table(target_counts, 'Target reason') if targets else 'No first-batch file targets exist.'}

## Dataset Checklist

{markdown_rows(checklist, ['batch_rank', 'country', 'wave', 'idno', 'included_acquisition_sets', 'raw_intake_status', 'local_target_folder'], 20) if checklist else 'No first-batch datasets selected.'}

## Core File Targets

{markdown_rows(report_targets, ['batch_rank', 'idno', 'file_name', 'target_reason', 'expected_file_status', 'candidate_categories'], 60) if report_targets else 'No core file targets identified.'}

## Post-Download Verification

After placing complete original raw packages in the target folders, run:

```bash
python script/17_audit_raw_downloads.py
python script/03_inspect_raw_schemas.py
python script/29_build_raw_variable_verification_protocol.py
python script/33_build_harmonization_recipe_gate.py
python script/35_build_empirical_readiness_dashboard.py
python script/37_build_first_batch_raw_acquisition_checklist.py
```

Pass evidence for each dataset is raw file inventory rows and raw variable catalog rows linked to the dataset ID. Metadata-only module names are not enough.

## Stop Rules

- Do not create or promote `temp/harmonization_recipe.csv` from metadata-only hits.
- Do not write clean analytical data into `data/` until raw keys, levels, units, recall periods, missing codes, and labels are audited.
- Do not construct SDG 3.8.2 unless the discretionary-budget denominator can be verified from raw values.
- Do not estimate prediction, reduced-form, causal ML, policy learning, mechanisms, or robustness checks from this checklist alone.

## Machine-Readable Outputs

- `temp/first_batch_raw_acquisition_checklist.csv`
- `temp/first_batch_raw_file_targets.csv`
- `result/first_batch_raw_acquisition_summary.csv`
""",
        encoding="utf-8",
    )


def main() -> None:
    ensure_dirs()
    checklist, targets = build_checklist_and_targets()
    summary = build_summary(checklist, targets)
    write_csv(CHECKLIST_PATH, checklist, CHECKLIST_COLUMNS)
    write_csv(FILE_TARGETS_PATH, targets, FILE_TARGET_COLUMNS)
    write_csv(SUMMARY_PATH, summary, SUMMARY_COLUMNS)
    write_report(checklist, targets, summary)
    append_log(
        TEMP_DIR / "audit_log.md",
        f"Built first-batch raw acquisition checklist dataset_rows={len(checklist)} file_target_rows={len(targets)}.",
    )
    print(f"First-batch raw acquisition checklist dataset_rows={len(checklist)} file_target_rows={len(targets)}.")


if __name__ == "__main__":
    main()
