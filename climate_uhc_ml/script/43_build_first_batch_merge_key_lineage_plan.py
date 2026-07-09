from __future__ import annotations

import csv
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from common import REPORT_DIR, RESULT_DIR, TEMP_DIR, append_log, ensure_dirs, write_csv


CONCEPT_TEMPLATE_PATH = TEMP_DIR / "first_batch_concept_verification_template.csv"
VARIABLE_TEMPLATE_PATH = TEMP_DIR / "first_batch_variable_verification_template.csv"
FILE_QUEUE_PATH = TEMP_DIR / "first_batch_manual_download_file_queue.csv"
FILE_TRACE_PATH = TEMP_DIR / "first_batch_file_source_traceability.csv"
RAW_FILE_INVENTORY_PATH = TEMP_DIR / "raw_schema_inventory" / "raw_file_inventory.csv"
RAW_VARIABLE_CATALOG_PATH = TEMP_DIR / "raw_schema_inventory" / "raw_variable_catalog.csv"

VARIABLE_MAP_PATHS = [
    TEMP_DIR / "variable_map_geography.csv",
    TEMP_DIR / "variable_map_survey_design.csv",
]

PLAN_PATH = TEMP_DIR / "first_batch_merge_key_lineage_plan.csv"
CANDIDATE_PATH = TEMP_DIR / "first_batch_merge_key_candidate_variables.csv"
SUMMARY_PATH = RESULT_DIR / "first_batch_merge_key_lineage_summary.csv"
REPORT_PATH = REPORT_DIR / "first_batch_merge_key_lineage_plan.md"

KEY_ROLES = [
    "household_id",
    "person_id",
    "survey_weight",
    "psu_cluster",
    "strata",
    "survey_timing",
    "geography",
]

PLAN_COLUMNS = [
    "batch_rank",
    "country",
    "survey_name",
    "wave",
    "idno",
    "household_id_candidate_files",
    "household_id_candidate_variables",
    "household_id_candidate_count",
    "person_id_candidate_files",
    "person_id_candidate_variables",
    "person_id_candidate_count",
    "merge_unit_assessment",
    "survey_weight_candidate_files",
    "survey_weight_candidate_variables",
    "survey_weight_candidate_count",
    "psu_candidate_files",
    "psu_candidate_variables",
    "psu_candidate_count",
    "strata_candidate_files",
    "strata_candidate_variables",
    "strata_candidate_count",
    "timing_candidate_files",
    "timing_candidate_variables",
    "timing_candidate_count",
    "geography_candidate_files",
    "geography_candidate_variables",
    "geography_candidate_count",
    "financial_core_files",
    "access_core_files",
    "design_geography_files",
    "metadata_supported_file_rows",
    "metadata_unsupported_file_rows",
    "merge_key_lineage_status",
    "raw_gate_status",
    "post_download_key_audit",
]

CANDIDATE_COLUMNS = [
    "batch_rank",
    "country",
    "survey_name",
    "wave",
    "idno",
    "concept",
    "lineage_role",
    "file_name",
    "raw_variable",
    "harmonized_variable",
    "raw_label",
    "metadata_confidence",
    "source_table",
    "metadata_file_status",
    "metadata_variable_status",
    "source_trace_status",
    "raw_verification_status",
    "post_download_check",
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


def row_count(path: Path) -> int:
    if not path.exists() or not path.is_file():
        return 0
    if path.suffix.lower() == ".csv":
        return len(read_csv_dicts(path))
    return 0


def split_semicolon(value: str) -> list[str]:
    out: list[str] = []
    seen: set[str] = set()
    for part in (value or "").split(";"):
        item = part.strip()
        if item and item not in seen:
            out.append(item)
            seen.add(item)
    return out


def unique_join(values: list[str], limit: int = 24) -> str:
    out: list[str] = []
    seen: set[str] = set()
    for value in values:
        item = (value or "").strip()
        if item and item not in seen:
            out.append(item)
            seen.add(item)
    return ";".join(out[:limit])


def normalize(value: str) -> str:
    return (value or "").strip().lower()


def dataset_key(row: dict[str, str]) -> tuple[str, str, str, str, str]:
    return (
        row.get("batch_rank", ""),
        row.get("country", ""),
        row.get("survey_name", ""),
        row.get("wave", ""),
        row.get("idno", ""),
    )


def role_from_concept(concept: str) -> str:
    mapping = {
        "household_id": "household_id",
        "psu_cluster": "psu_cluster",
        "strata": "strata",
        "survey_weight": "survey_weight",
        "survey_timing": "survey_timing",
        "climate_geography": "geography",
    }
    return mapping.get(concept, "")


def role_from_harmonized(harmonized: str) -> str:
    values = {normalize(value) for value in split_semicolon(harmonized)}
    if "hhid" in values:
        return "household_id"
    if "pid" in values:
        return "person_id"
    if "household_weight_or_person_weight" in values:
        return "survey_weight"
    if "psu_or_cluster_id" in values or "psu" in values or "cluster_id" in values:
        return "psu_cluster"
    if "strata" in values:
        return "strata"
    if "interview_date_or_survey_month" in values:
        return "survey_timing"
    if {"admin1_or_admin2", "latitude_or_longitude", "rural"} & values:
        return "geography"
    return ""


def trace_lookup(rows: list[dict[str, str]]) -> dict[tuple[str, str], dict[str, str]]:
    out: dict[tuple[str, str], dict[str, str]] = {}
    for row in rows:
        out[(row.get("idno", ""), row.get("file_name", ""))] = row
    return out


def add_candidate(
    candidates: list[dict[str, str]],
    trace_by_key: dict[tuple[str, str], dict[str, str]],
    base: dict[str, str],
    concept: str,
    lineage_role: str,
    file_name: str,
    raw_variable: str,
    harmonized_variable: str,
    raw_label: str,
    metadata_confidence: str,
    source_table: str,
) -> None:
    if not lineage_role or lineage_role not in KEY_ROLES:
        return
    trace = trace_by_key.get((base.get("idno", ""), file_name), {})
    if not trace:
        trace = {
            "metadata_file_status": "not_in_first_batch_file_source_trace",
            "metadata_variable_status": "not_in_first_batch_file_source_trace",
            "source_trace_status": "not_in_first_batch_file_source_trace",
        }
    candidates.append(
        {
            "batch_rank": base.get("batch_rank", ""),
            "country": base.get("country", ""),
            "survey_name": base.get("survey_name", ""),
            "wave": base.get("wave", ""),
            "idno": base.get("idno", ""),
            "concept": concept,
            "lineage_role": lineage_role,
            "file_name": file_name,
            "raw_variable": raw_variable,
            "harmonized_variable": harmonized_variable,
            "raw_label": raw_label,
            "metadata_confidence": metadata_confidence,
            "source_table": source_table,
            "metadata_file_status": trace.get("metadata_file_status", ""),
            "metadata_variable_status": trace.get("metadata_variable_status", ""),
            "source_trace_status": trace.get("source_trace_status", ""),
            "raw_verification_status": "raw_not_inspected",
            "post_download_check": post_download_check(lineage_role),
        }
    )


def post_download_check(lineage_role: str) -> str:
    checks = {
        "household_id": "verify household ID uniqueness, missingness, string/numeric type, and consistency across core files",
        "person_id": "verify person ID nesting within household ID and person-level merge cardinality",
        "survey_weight": "verify weight label, level, nonmissing positive distribution, and survey documentation",
        "psu_cluster": "verify PSU or cluster ID level, uniqueness within strata/geography, and clustering role",
        "strata": "verify stratum ID, empty strata, singleton strata, and relation to weights/PSUs",
        "survey_timing": "verify interview date/month/year values, fieldwork window, missing codes, and climate lag alignment",
        "geography": "verify admin/GPS level, coordinate precision or displacement, and climate aggregation level",
    }
    return checks.get(lineage_role, "inspect raw values, labels, missing codes, levels, and merge role before use")


def build_candidates(
    variable_template: list[dict[str, str]],
    variable_maps: list[dict[str, str]],
    trace_by_key: dict[tuple[str, str], dict[str, str]],
    allowed_idnos: set[str],
) -> list[dict[str, str]]:
    candidates: list[dict[str, str]] = []
    seen: set[tuple[str, str, str, str, str, str]] = set()

    for row in variable_template:
        if row.get("idno", "") not in allowed_idnos:
            continue
        concept = row.get("concept", "")
        lineage_role = role_from_concept(concept) or role_from_harmonized(row.get("candidate_harmonized_variables", ""))
        raw_variable = row.get("candidate_raw_variable", "")
        for file_name in split_semicolon(row.get("candidate_files", "")):
            key = (row.get("idno", ""), lineage_role, file_name, raw_variable, "first_batch_variable_verification_template", concept)
            if key in seen:
                continue
            seen.add(key)
            add_candidate(
                candidates,
                trace_by_key,
                row,
                concept,
                lineage_role,
                file_name,
                raw_variable,
                row.get("candidate_harmonized_variables", ""),
                row.get("raw_label", ""),
                row.get("metadata_confidence", ""),
                "first_batch_variable_verification_template",
            )

    for row in variable_maps:
        if row.get("idno", "") not in allowed_idnos:
            continue
        lineage_role = role_from_harmonized(row.get("harmonized_variable", ""))
        concept = f"variable_map_{lineage_role}" if lineage_role else "variable_map_other"
        file_name = row.get("file", "")
        raw_variable = row.get("raw_variable", "")
        key = (row.get("idno", ""), lineage_role, file_name, raw_variable, "variable_map_geography_or_survey_design", concept)
        if key in seen:
            continue
        seen.add(key)
        add_candidate(
            candidates,
            trace_by_key,
            row,
            concept,
            lineage_role,
            file_name,
            raw_variable,
            row.get("harmonized_variable", ""),
            row.get("raw_label", ""),
            row.get("quality_flag", ""),
            "variable_map_geography_or_survey_design",
        )

    candidates.sort(
        key=lambda row: (
            safe_int(row.get("batch_rank"), 9999),
            row.get("idno", ""),
            KEY_ROLES.index(row["lineage_role"]) if row.get("lineage_role") in KEY_ROLES else 999,
            row.get("file_name", ""),
            row.get("raw_variable", ""),
        )
    )
    return candidates


def grouped_candidates(candidates: list[dict[str, str]]) -> dict[str, dict[str, list[dict[str, str]]]]:
    grouped: dict[str, dict[str, list[dict[str, str]]]] = defaultdict(lambda: defaultdict(list))
    for row in candidates:
        grouped[row.get("idno", "")][row.get("lineage_role", "")].append(row)
    return grouped


def infer_idno_from_row(row: dict[str, str], known_idnos: set[str]) -> str:
    haystack = " ".join(str(value) for value in row.values()).lower().replace("\\", "/")
    for idno in sorted(known_idnos, key=len, reverse=True):
        if idno and idno.lower() in haystack:
            return idno
    return ""


def raw_counts_by_idno(known_idnos: set[str]) -> tuple[dict[str, int], dict[str, int]]:
    file_counts: dict[str, int] = defaultdict(int)
    variable_counts: dict[str, int] = defaultdict(int)
    for row in read_csv_dicts(RAW_FILE_INVENTORY_PATH):
        idno = infer_idno_from_row(row, known_idnos)
        if idno:
            file_counts[idno] += 1
    for row in read_csv_dicts(RAW_VARIABLE_CATALOG_PATH):
        idno = infer_idno_from_row(row, known_idnos)
        if idno:
            variable_counts[idno] += 1
    return file_counts, variable_counts


def core_files(rows: list[dict[str, str]], idno: str, contains: str) -> list[str]:
    out: list[str] = []
    for row in rows:
        if row.get("idno") != idno:
            continue
        haystack = ";".join(
            [
                row.get("target_reasons", ""),
                row.get("candidate_categories", ""),
                row.get("candidate_harmonized_variables", ""),
            ]
        ).lower()
        if contains in haystack:
            out.append(row.get("file_name", ""))
    return out


def role_summary(rows: list[dict[str, str]], role: str, value_key: str) -> str:
    return unique_join([row.get(value_key, "") for row in rows if row.get("lineage_role") == role])


def role_count(rows: list[dict[str, str]], role: str) -> int:
    return sum(1 for row in rows if row.get("lineage_role") == role)


def lineage_status(
    role_rows: list[dict[str, str]],
    unsupported_files: int,
    raw_files: int,
    raw_variables: int,
) -> tuple[str, str]:
    has_hhid = role_count(role_rows, "household_id") > 0
    has_timing = role_count(role_rows, "survey_timing") > 0
    has_geography = role_count(role_rows, "geography") > 0
    has_design = any(role_count(role_rows, role) > 0 for role in ["survey_weight", "psu_cluster", "strata"])

    if raw_files == 0 or raw_variables == 0:
        raw_gate = "blocked_raw_microdata"
    else:
        raw_gate = "raw_files_present_requires_value_key_audit"

    if not has_hhid:
        return "metadata_key_lineage_incomplete_no_household_id_raw_unverified", raw_gate
    if not has_timing or not has_geography:
        return "metadata_key_lineage_incomplete_no_timing_or_geography_raw_unverified", raw_gate
    if not has_design:
        return "metadata_key_lineage_incomplete_no_design_variable_raw_unverified", raw_gate
    if unsupported_files:
        return "metadata_key_lineage_has_unsupported_file_targets_raw_unverified", raw_gate
    return "metadata_key_lineage_planned_raw_unverified", raw_gate


def build_plan_rows(
    concept_template: list[dict[str, str]],
    queue_rows: list[dict[str, str]],
    trace_rows: list[dict[str, str]],
    candidates: list[dict[str, str]],
) -> list[dict[str, str]]:
    datasets: dict[str, dict[str, str]] = {}
    for row in concept_template + queue_rows:
        idno = row.get("idno", "")
        if idno and idno not in datasets:
            datasets[idno] = {
                "batch_rank": row.get("batch_rank", ""),
                "country": row.get("country", ""),
                "survey_name": row.get("survey_name", ""),
                "wave": row.get("wave", ""),
                "idno": idno,
            }

    by_idno_role = grouped_candidates(candidates)
    trace_by_idno: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in trace_rows:
        trace_by_idno[row.get("idno", "")].append(row)

    known_idnos = set(datasets)
    raw_file_counts, raw_variable_counts = raw_counts_by_idno(known_idnos)
    rows: list[dict[str, str]] = []
    for idno, base in datasets.items():
        role_rows = [candidate for role in KEY_ROLES for candidate in by_idno_role.get(idno, {}).get(role, [])]
        traces = trace_by_idno.get(idno, [])
        supported = sum(1 for row in traces if row.get("source_trace_status") == "metadata_file_and_examples_supported")
        unsupported = sum(1 for row in traces if row.get("source_trace_status", "").startswith("unsupported_"))
        status, raw_gate = lineage_status(role_rows, unsupported, raw_file_counts.get(idno, 0), raw_variable_counts.get(idno, 0))
        has_person = role_count(role_rows, "person_id") > 0
        merge_unit = "household_with_person_level_linkage_candidates" if has_person else "household_level_only_until_person_id_verified"
        rows.append(
            {
                **base,
                "household_id_candidate_files": role_summary(role_rows, "household_id", "file_name"),
                "household_id_candidate_variables": role_summary(role_rows, "household_id", "raw_variable"),
                "household_id_candidate_count": str(role_count(role_rows, "household_id")),
                "person_id_candidate_files": role_summary(role_rows, "person_id", "file_name"),
                "person_id_candidate_variables": role_summary(role_rows, "person_id", "raw_variable"),
                "person_id_candidate_count": str(role_count(role_rows, "person_id")),
                "merge_unit_assessment": merge_unit,
                "survey_weight_candidate_files": role_summary(role_rows, "survey_weight", "file_name"),
                "survey_weight_candidate_variables": role_summary(role_rows, "survey_weight", "raw_variable"),
                "survey_weight_candidate_count": str(role_count(role_rows, "survey_weight")),
                "psu_candidate_files": role_summary(role_rows, "psu_cluster", "file_name"),
                "psu_candidate_variables": role_summary(role_rows, "psu_cluster", "raw_variable"),
                "psu_candidate_count": str(role_count(role_rows, "psu_cluster")),
                "strata_candidate_files": role_summary(role_rows, "strata", "file_name"),
                "strata_candidate_variables": role_summary(role_rows, "strata", "raw_variable"),
                "strata_candidate_count": str(role_count(role_rows, "strata")),
                "timing_candidate_files": role_summary(role_rows, "survey_timing", "file_name"),
                "timing_candidate_variables": role_summary(role_rows, "survey_timing", "raw_variable"),
                "timing_candidate_count": str(role_count(role_rows, "survey_timing")),
                "geography_candidate_files": role_summary(role_rows, "geography", "file_name"),
                "geography_candidate_variables": role_summary(role_rows, "geography", "raw_variable"),
                "geography_candidate_count": str(role_count(role_rows, "geography")),
                "financial_core_files": unique_join(core_files(queue_rows, idno, "financial")),
                "access_core_files": unique_join(core_files(queue_rows, idno, "health_need_access")),
                "design_geography_files": unique_join(core_files(queue_rows, idno, "geography")),
                "metadata_supported_file_rows": str(supported),
                "metadata_unsupported_file_rows": str(unsupported),
                "merge_key_lineage_status": status,
                "raw_gate_status": raw_gate,
                "post_download_key_audit": "verify ID uniqueness/cardinality, design variables, timing granularity, geography precision, and file joins in raw values before promoting any harmonization recipe",
            }
        )
    rows.sort(key=lambda row: (safe_int(row.get("batch_rank"), 9999), row.get("idno", "")))
    return rows


def build_summary(plan_rows: list[dict[str, str]], candidates: list[dict[str, str]]) -> list[dict[str, str]]:
    status_counts = Counter(row.get("merge_key_lineage_status", "") for row in plan_rows)
    raw_counts = Counter(row.get("raw_gate_status", "") for row in plan_rows)
    role_counts = Counter(row.get("lineage_role", "") for row in candidates)
    datasets = {row.get("idno", "") for row in plan_rows if row.get("idno")}
    planned = sum(1 for row in plan_rows if row.get("merge_key_lineage_status") == "metadata_key_lineage_planned_raw_unverified")
    unsupported = sum(safe_int(row.get("metadata_unsupported_file_rows"), 0) for row in plan_rows)
    raw_ready = sum(1 for row in plan_rows if row.get("raw_gate_status") != "blocked_raw_microdata")
    rows = [
        {"metric": "first_batch_merge_key_lineage_plan_rows", "value": str(len(plan_rows)), "interpretation": "Dataset-level merge-key lineage planning rows."},
        {"metric": "first_batch_merge_key_lineage_dataset_rows", "value": str(len(datasets)), "interpretation": "First-batch datasets represented in the merge-key lineage plan."},
        {"metric": "first_batch_merge_key_candidate_variable_rows", "value": str(len(candidates)), "interpretation": "Long candidate key/design/timing/geography variable rows."},
        {"metric": "first_batch_merge_key_lineage_planned_rows", "value": str(planned), "interpretation": "Datasets with metadata-supported household key, design, timing, and geography candidates."},
        {"metric": "first_batch_merge_key_lineage_incomplete_rows", "value": str(len(plan_rows) - planned), "interpretation": "Datasets missing one or more metadata key-lineage domains or file support checks."},
        {"metric": "first_batch_merge_key_raw_ready_rows", "value": str(raw_ready), "interpretation": "Datasets with raw files and variables present for value/key audit."},
        {"metric": "first_batch_merge_key_metadata_unsupported_file_rows", "value": str(unsupported), "interpretation": "Unsupported first-batch file-source trace rows within merge-key planning."},
    ]
    for role in KEY_ROLES:
        rows.append({"metric": f"first_batch_merge_key_candidate_{role}_rows", "value": str(role_counts.get(role, 0)), "interpretation": "Candidate key-lineage variable rows by role."})
    for status, count in sorted(status_counts.items()):
        rows.append({"metric": f"merge_key_lineage_status_{status}", "value": str(count), "interpretation": "Dataset-level merge-key lineage status count."})
    for status, count in sorted(raw_counts.items()):
        rows.append({"metric": f"merge_key_raw_gate_status_{status}", "value": str(count), "interpretation": "Dataset-level raw gate status count."})
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


def write_report(plan_rows: list[dict[str, str]], candidates: list[dict[str, str]], summary: list[dict[str, str]]) -> None:
    status_counts = Counter(row["merge_key_lineage_status"] for row in plan_rows)
    raw_counts = Counter(row["raw_gate_status"] for row in plan_rows)
    role_counts = Counter(row["lineage_role"] for row in candidates)
    summary_table = "\n".join(f"| {row['metric']} | {row['value']} | {row['interpretation']} |" for row in summary)
    REPORT_PATH.write_text(
        f"""# First-Batch Merge-Key Lineage Plan

Status: metadata-only planning layer. This file identifies candidate household/person keys, survey design variables, timing variables, geography variables, and core file relationships for the first manual raw-download batch. It does not verify raw values, labels, merge cardinality, units, missing codes, or sample levels.

## Summary

| Metric | Value | Interpretation |
|---|---:|---|
{summary_table}

## Dataset Status

{markdown_count_table(status_counts, 'Merge-key lineage status') if plan_rows else 'No merge-key lineage rows exist.'}

## Raw Gate Status

{markdown_count_table(raw_counts, 'Raw gate status') if plan_rows else 'No raw gate rows exist.'}

## Candidate Roles

{markdown_count_table(role_counts, 'Candidate variable role') if candidates else 'No candidate key-lineage variables exist.'}

## Dataset-Level Plan

{markdown_rows(plan_rows, ['batch_rank', 'idno', 'household_id_candidate_count', 'person_id_candidate_count', 'survey_weight_candidate_count', 'psu_candidate_count', 'strata_candidate_count', 'timing_candidate_count', 'geography_candidate_count', 'merge_key_lineage_status', 'raw_gate_status'], 20) if plan_rows else 'No dataset-level plan rows exist.'}

## Candidate Variables

{markdown_rows(candidates, ['batch_rank', 'idno', 'lineage_role', 'file_name', 'raw_variable', 'harmonized_variable', 'source_trace_status'], 30) if candidates else 'No candidate variable rows exist.'}

## Guardrails

- Candidate keys and design variables are metadata-derived only.
- A planned lineage row is not a verified merge plan until raw files are downloaded and raw values are inspected.
- Do not create `data/` outputs, harmonization recipes, outcomes, climate-linked data, models, causal estimates, or policy simulations from this plan alone.
- After manual download, verify ID uniqueness, person-household nesting, merge cardinality, PSU/strata/weight distributions, timing granularity, geography precision, and missing-code semantics before promotion.

## Machine-Readable Outputs

- `temp/first_batch_merge_key_lineage_plan.csv`
- `temp/first_batch_merge_key_candidate_variables.csv`
- `result/first_batch_merge_key_lineage_summary.csv`
""",
        encoding="utf-8",
    )


def main() -> None:
    ensure_dirs()
    concept_template = read_csv_dicts(CONCEPT_TEMPLATE_PATH)
    variable_template = read_csv_dicts(VARIABLE_TEMPLATE_PATH)
    queue_rows = read_csv_dicts(FILE_QUEUE_PATH)
    trace_rows = read_csv_dicts(FILE_TRACE_PATH)
    variable_maps: list[dict[str, str]] = []
    for path in VARIABLE_MAP_PATHS:
        variable_maps.extend(read_csv_dicts(path))

    trace_by_key = trace_lookup(trace_rows)
    allowed_idnos = {row.get("idno", "") for row in concept_template + queue_rows if row.get("idno", "")}
    candidates = build_candidates(variable_template, variable_maps, trace_by_key, allowed_idnos)
    plan_rows = build_plan_rows(concept_template, queue_rows, trace_rows, candidates)
    summary = build_summary(plan_rows, candidates)

    write_csv(PLAN_PATH, plan_rows, PLAN_COLUMNS)
    write_csv(CANDIDATE_PATH, candidates, CANDIDATE_COLUMNS)
    write_csv(SUMMARY_PATH, summary, SUMMARY_COLUMNS)
    write_report(plan_rows, candidates, summary)
    planned = sum(1 for row in plan_rows if row.get("merge_key_lineage_status") == "metadata_key_lineage_planned_raw_unverified")
    append_log(TEMP_DIR / "audit_log.md", f"Built first-batch merge-key lineage plan rows={len(plan_rows)} planned={planned} candidates={len(candidates)}.")
    print(f"First-batch merge-key lineage plan rows={len(plan_rows)} planned={planned} candidates={len(candidates)}.")


if __name__ == "__main__":
    main()
