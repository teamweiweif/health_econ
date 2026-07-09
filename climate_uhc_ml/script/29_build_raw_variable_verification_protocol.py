from __future__ import annotations

import csv
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from common import REPORT_DIR, RESULT_DIR, TEMP_DIR, append_log, ensure_dirs, write_csv


PRIORITY_PATH = TEMP_DIR / "metadata_quality_download_priority.csv"
CONCEPT_PATH = TEMP_DIR / "raw_ingestion_concept_checklist.csv"
CONFIDENCE_PATH = TEMP_DIR / "variable_map_confidence_audit.csv"
RAW_FILE_PATH = TEMP_DIR / "raw_schema_inventory" / "raw_file_inventory.csv"
RAW_VARIABLE_PATH = TEMP_DIR / "raw_schema_inventory" / "raw_variable_catalog.csv"

PROTOCOL_PATH = TEMP_DIR / "raw_variable_verification_protocol.csv"
SCAFFOLD_PATH = TEMP_DIR / "harmonization_recipe_scaffold.csv"
SUMMARY_PATH = RESULT_DIR / "raw_variable_verification_summary.csv"
REPORT_PATH = REPORT_DIR / "raw_variable_verification_protocol.md"

PROTOCOL_COLUMNS = [
    "quality_rank",
    "quality_download_priority_tier",
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
    "raw_file_status",
    "raw_variable_status",
    "verification_status",
    "verification_checks",
    "minimum_raw_evidence_needed",
    "verification_action",
    "harmonization_decision",
]

SCAFFOLD_COLUMNS = [
    "country",
    "survey_name",
    "wave",
    "idno",
    "harmonized_variable",
    "source_path",
    "source_file",
    "raw_variable",
    "raw_label",
    "merge_level",
    "key_role",
    "required",
    "transformation",
    "unit",
    "recall_period",
    "quality_flag",
    "notes",
    "concept",
    "raw_verification_status",
    "verification_required",
]

SUMMARY_COLUMNS = ["metric", "value", "interpretation"]

CONFIDENCE_RANK = {"high": 3, "moderate": 2, "low": 1, "likely_false_positive": 0, "": 0}

CONCEPT_CHECKS = {
    "household_id": "nonmissing rate; uniqueness at stated level; stable across modules; household/person merge behavior",
    "total_consumption_or_income": "numeric type; local currency unit; recall/reference period; aggregate source; negative/zero values; household level",
    "oop_health_expenditure": "numeric type; OOP scope; reimbursement/insurance exclusion; recall period; item vs aggregate; missing and zero coding",
    "survey_weight": "numeric positive weights; household vs person applicability; extreme weights; survey design documentation",
    "survey_timing": "parseable interview date/month/year; fieldwork calendar consistency; missing timing; usable lag windows",
    "climate_geography": "admin level or GPS availability; coordinate displacement/suppression; merge key; rural/admin consistency; climate linkage precision",
    "health_need": "need denominator definition; skip pattern; individual vs household level; recall period; missing and no-need coding",
    "care_or_barrier": "care-seeking denominator; barrier categories; cost/distance/supply coding; skip pattern; multiple responses",
    "psu_cluster": "cluster/EA identifier; sampling level; variance cluster suitability; merge consistency",
    "strata": "strata identifier; survey-design documentation; missing/empty strata; merge consistency",
    "demographics": "age/sex/education/household roster logic; household head definition; derived age-structure feasibility",
    "insurance": "insurance/coverage definition; individual vs household level; current coverage timing; public/private coding",
    "shocks_or_livelihood": "shock/livelihood/coping meaning; pre/post treatment timing; agriculture exposure; food insecurity and coping coding",
}

CONCEPT_HARMONIZED_VARIABLES = {
    "household_id": ["hhid"],
    "total_consumption_or_income": ["total_consumption", "total_income", "food_consumption", "nonfood_consumption"],
    "oop_health_expenditure": ["oop_health_expenditure"],
    "survey_weight": ["household_weight", "person_weight"],
    "survey_timing": ["survey_year", "survey_month", "interview_date"],
    "climate_geography": ["admin1", "admin2", "cluster_id", "latitude", "longitude", "geolocation_quality", "rural"],
    "health_need": ["illness_or_injury_need"],
    "care_or_barrier": [
        "care_sought",
        "care_not_sought",
        "reason_not_sought_cost",
        "reason_not_sought_distance",
        "reason_not_sought_supply",
        "health_facility_distance",
    ],
    "psu_cluster": ["psu", "cluster_id"],
    "strata": ["strata"],
    "demographics": [
        "household_size",
        "children_under_5",
        "children_under_15",
        "elderly_60_plus",
        "elderly_65_plus",
        "hh_head_sex",
        "hh_head_age",
        "hh_head_education",
        "asset_index",
    ],
    "insurance": ["health_insurance"],
    "shocks_or_livelihood": [
        "coping_borrowed",
        "coping_sold_assets",
        "food_insecurity",
        "agriculture_livelihood",
        "employment_labor",
    ],
}

CONCEPT_REQUIRED = {
    "household_id": "yes",
    "total_consumption_or_income": "yes",
    "oop_health_expenditure": "yes",
    "survey_weight": "recommended",
    "survey_timing": "yes",
    "climate_geography": "yes",
    "health_need": "recommended",
    "care_or_barrier": "recommended",
    "psu_cluster": "recommended",
    "strata": "recommended",
    "demographics": "recommended",
    "insurance": "no",
    "shocks_or_livelihood": "no",
}

MERGE_LEVEL = {
    "household_id": "household",
    "total_consumption_or_income": "household",
    "oop_health_expenditure": "household_or_person",
    "survey_weight": "household_or_person",
    "survey_timing": "household",
    "climate_geography": "cluster_or_admin",
    "health_need": "household_or_person",
    "care_or_barrier": "household_or_person",
    "psu_cluster": "cluster",
    "strata": "survey_design",
    "demographics": "household_or_person",
    "insurance": "household_or_person",
    "shocks_or_livelihood": "household",
}

KEY_ROLE_BY_HVAR = {
    "hhid": "base_key",
    "pid": "person_key",
    "cluster_id": "climate_or_cluster_key",
    "psu": "variance_cluster",
    "strata": "strata",
}


def read_csv_dicts(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def split_values(value: str, limit: int | None = None) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for item in (value or "").replace(",", ";").split(";"):
        clean = item.strip()
        if not clean or clean in seen:
            continue
        out.append(clean)
        seen.add(clean)
        if limit is not None and len(out) >= limit:
            break
    return out


def compact_join(values: list[str], limit: int = 12) -> str:
    clean = []
    seen = set()
    for value in values:
        value = (value or "").strip()
        if not value or value in seen:
            continue
        clean.append(value)
        seen.add(value)
        if len(clean) >= limit:
            break
    return ";".join(clean)


def best_confidence(rows: list[dict[str, str]]) -> str:
    if not rows:
        return "metadata_candidate_from_concept_checklist"
    return max((row.get("metadata_confidence", "") for row in rows), key=lambda value: CONFIDENCE_RANK.get(value, 0))


def raw_file_names(raw_files: list[dict[str, str]]) -> dict[str, set[str]]:
    names: dict[str, set[str]] = defaultdict(set)
    for row in raw_files:
        idno = row.get("idno", "")
        for field in ["file_name", "source_file", "source_path", "path"]:
            value = row.get(field, "")
            if value:
                names[idno].add(Path(value).name)
    return names


def raw_variable_names(raw_variables: list[dict[str, str]]) -> dict[str, set[str]]:
    names: dict[str, set[str]] = defaultdict(set)
    for row in raw_variables:
        idno = row.get("idno", "")
        for field in ["raw_variable", "variable", "variable_name", "name"]:
            value = row.get(field, "")
            if value:
                names[idno].add(value)
    return names


def confidence_index(rows: list[dict[str, str]], priority_ids: set[str]) -> dict[tuple[str, str], list[dict[str, str]]]:
    index: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        idno = row.get("idno", "")
        raw_variable = row.get("raw_variable", "")
        if idno not in priority_ids or not raw_variable:
            continue
        if row.get("metadata_confidence") == "likely_false_positive":
            continue
        index[(idno, raw_variable)].append(row)
    return index


def status_for_raw_file(idno: str, candidate_files: list[str], raw_files_by_idno: dict[str, set[str]]) -> str:
    present = raw_files_by_idno.get(idno, set())
    if not present:
        return "raw_files_not_present"
    if any(Path(name).name in present for name in candidate_files):
        return "candidate_file_present"
    return "raw_files_present_candidate_file_not_matched"


def status_for_raw_variable(idno: str, raw_variable: str, raw_vars_by_idno: dict[str, set[str]]) -> str:
    present = raw_vars_by_idno.get(idno, set())
    if not present:
        return "raw_variable_catalog_absent"
    if raw_variable in present:
        return "raw_variable_catalog_match"
    return "raw_variable_not_matched"


def build_protocol_rows(
    priorities: list[dict[str, str]],
    concepts: list[dict[str, str]],
    confidence: list[dict[str, str]],
    raw_files: list[dict[str, str]],
    raw_variables: list[dict[str, str]],
) -> list[dict[str, str]]:
    priority_by_idno = {row.get("idno", ""): row for row in priorities if row.get("idno")}
    priority_ids = set(priority_by_idno)
    confidence_by_var = confidence_index(confidence, priority_ids)
    raw_files_by_idno = raw_file_names(raw_files)
    raw_vars_by_idno = raw_variable_names(raw_variables)

    protocol: list[dict[str, str]] = []
    for concept_row in concepts:
        idno = concept_row.get("idno", "")
        if idno not in priority_by_idno:
            continue
        priority = priority_by_idno[idno]
        concept = concept_row.get("concept", "")
        candidate_files = split_values(concept_row.get("candidate_files", ""))
        candidate_vars = split_values(concept_row.get("candidate_variables", ""))
        if not candidate_vars:
            candidate_vars = [""]
        for rank, raw_variable in enumerate(candidate_vars, start=1):
            matches = confidence_by_var.get((idno, raw_variable), [])
            match_files = [row.get("file", "") for row in matches]
            match_hvars = [row.get("harmonized_variable", "") for row in matches]
            match_labels = [row.get("raw_label", "") for row in matches]
            candidate_files_for_var = split_values(";".join(match_files)) or candidate_files
            raw_file_status = status_for_raw_file(idno, candidate_files_for_var, raw_files_by_idno)
            raw_variable_status = status_for_raw_variable(idno, raw_variable, raw_vars_by_idno) if raw_variable else "no_metadata_candidate_variable"
            if raw_variable_status == "raw_variable_catalog_match":
                verification_status = "raw_variable_seen_value_audit_pending"
            else:
                verification_status = "raw_not_inspected"
            protocol.append(
                {
                    "quality_rank": priority.get("quality_rank", ""),
                    "quality_download_priority_tier": priority.get("quality_download_priority_tier", ""),
                    "country": concept_row.get("country", priority.get("country", "")),
                    "survey_name": concept_row.get("survey_name", priority.get("survey_name", "")),
                    "wave": concept_row.get("wave", priority.get("wave", "")),
                    "idno": idno,
                    "concept": concept,
                    "required_for": concept_row.get("required_for", ""),
                    "candidate_rank_within_concept": str(rank),
                    "candidate_files": compact_join(candidate_files_for_var, 20),
                    "candidate_raw_variable": raw_variable,
                    "candidate_harmonized_variables": compact_join(match_hvars or CONCEPT_HARMONIZED_VARIABLES.get(concept, []), 20),
                    "raw_label": compact_join(match_labels, 6),
                    "metadata_confidence": best_confidence(matches),
                    "confidence_reason": compact_join([row.get("confidence_reason", "") for row in matches], 3),
                    "raw_file_status": raw_file_status,
                    "raw_variable_status": raw_variable_status,
                    "verification_status": verification_status,
                    "verification_checks": CONCEPT_CHECKS.get(concept, "inspect raw values, labels, units, keys, level, and missing codes"),
                    "minimum_raw_evidence_needed": concept_row.get("minimum_raw_evidence_needed", ""),
                    "verification_action": concept_row.get(
                        "verification_action",
                        "inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization",
                    ),
                    "harmonization_decision": "blocked_until_raw_values_units_recall_keys_and_missing_codes_pass",
                }
            )
    protocol.sort(
        key=lambda row: (
            int(row["quality_rank"] or 9999),
            row["idno"],
            row["concept"],
            int(row["candidate_rank_within_concept"] or 9999),
            row["candidate_raw_variable"],
        )
    )
    return protocol


def build_scaffold_rows(
    priorities: list[dict[str, str]],
    concepts: list[dict[str, str]],
    protocol: list[dict[str, str]],
    raw_variables: list[dict[str, str]],
) -> list[dict[str, str]]:
    priority_by_idno = {row.get("idno", ""): row for row in priorities if row.get("idno")}
    protocol_by_key: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in protocol:
        protocol_by_key[(row.get("idno", ""), row.get("concept", ""))].append(row)
    raw_vars_by_idno = raw_variable_names(raw_variables)

    scaffold: list[dict[str, str]] = []
    for concept_row in concepts:
        idno = concept_row.get("idno", "")
        if idno not in priority_by_idno:
            continue
        priority = priority_by_idno[idno]
        concept = concept_row.get("concept", "")
        candidates = protocol_by_key[(idno, concept)]
        candidate_files = [row.get("candidate_files", "") for row in candidates]
        candidate_raw_vars = [row.get("candidate_raw_variable", "") for row in candidates]
        candidate_labels = [row.get("raw_label", "") for row in candidates]
        confidence_values = [row.get("metadata_confidence", "") for row in candidates]
        has_raw_var_match = any(row.get("candidate_raw_variable", "") in raw_vars_by_idno.get(idno, set()) for row in candidates)
        verification_status = "raw_variable_seen_value_audit_pending" if has_raw_var_match else "raw_not_inspected"
        quality_flag = "raw_seen_requires_value_audit" if has_raw_var_match else "metadata_candidate_requires_raw_verification"
        best = best_confidence([{"metadata_confidence": value} for value in confidence_values])

        for hvar in CONCEPT_HARMONIZED_VARIABLES.get(concept, []):
            scaffold.append(
                {
                    "country": concept_row.get("country", priority.get("country", "")),
                    "survey_name": concept_row.get("survey_name", priority.get("survey_name", "")),
                    "wave": concept_row.get("wave", priority.get("wave", "")),
                    "idno": idno,
                    "harmonized_variable": hvar,
                    "source_path": priority.get("local_target_folder", ""),
                    "source_file": compact_join(split_values(";".join(candidate_files)), 20),
                    "raw_variable": compact_join(candidate_raw_vars, 20),
                    "raw_label": compact_join(candidate_labels, 6),
                    "merge_level": MERGE_LEVEL.get(concept, "to_be_verified"),
                    "key_role": KEY_ROLE_BY_HVAR.get(hvar, ""),
                    "required": CONCEPT_REQUIRED.get(concept, "no"),
                    "transformation": "pending_raw_value_audit",
                    "unit": "pending_raw_value_audit",
                    "recall_period": "pending_raw_value_audit",
                    "quality_flag": quality_flag,
                    "notes": (
                        f"Scaffold only; metadata confidence={best}. Do not copy into temp/harmonization_recipe.csv "
                        "until raw labels, values, units, recall period, level, keys, missing codes, and lineage pass."
                    ),
                    "concept": concept,
                    "raw_verification_status": verification_status,
                    "verification_required": CONCEPT_CHECKS.get(concept, "raw value and lineage audit required"),
                }
            )
    scaffold.sort(key=lambda row: (int(priority_by_idno.get(row["idno"], {}).get("quality_rank", 9999)), row["idno"], row["concept"], row["harmonized_variable"]))
    return scaffold


def build_summary_rows(protocol: list[dict[str, str]], scaffold: list[dict[str, str]], raw_files: list[dict[str, str]], raw_variables: list[dict[str, str]]) -> list[dict[str, str]]:
    verification_counts = Counter(row.get("verification_status", "") for row in protocol)
    file_counts = Counter(row.get("raw_file_status", "") for row in protocol)
    concept_counts = Counter(row.get("concept", "") for row in protocol)
    confidence_counts = Counter(row.get("metadata_confidence", "") for row in protocol)
    rows = [
        {"metric": "protocol_rows", "value": str(len(protocol)), "interpretation": "Candidate raw variables requiring verification."},
        {"metric": "scaffold_rows", "value": str(len(scaffold)), "interpretation": "Harmonized-variable scaffold rows; not a usable recipe."},
        {"metric": "priority_dataset_count", "value": str(len({row.get("idno", "") for row in protocol})), "interpretation": "Quality-prioritized datasets included."},
        {"metric": "concept_count", "value": str(len(concept_counts)), "interpretation": "Raw-ingestion concepts represented."},
        {"metric": "raw_file_inventory_rows", "value": str(len(raw_files)), "interpretation": "Raw tabular file inventory rows currently available."},
        {"metric": "raw_variable_catalog_rows", "value": str(len(raw_variables)), "interpretation": "Raw variable catalog rows currently available."},
        {"metric": "scaffold_ready_for_recipe_rows", "value": "0", "interpretation": "No scaffold row is recipe-ready until raw value audits pass."},
    ]
    for status, count in sorted(verification_counts.items()):
        rows.append({"metric": f"verification_status_{status}", "value": str(count), "interpretation": "Protocol verification status count."})
    for status, count in sorted(file_counts.items()):
        rows.append({"metric": f"raw_file_status_{status}", "value": str(count), "interpretation": "Protocol raw-file status count."})
    for confidence, count in sorted(confidence_counts.items()):
        rows.append({"metric": f"metadata_confidence_{confidence}", "value": str(count), "interpretation": "Protocol metadata-confidence count."})
    return rows


def markdown_count_table(counter: Counter[str], label: str) -> str:
    lines = [f"| {label} | Count |", "|---|---:|"]
    for key, count in counter.most_common():
        lines.append(f"| {key or 'blank'} | {count} |")
    return "\n".join(lines)


def write_report(protocol: list[dict[str, str]], scaffold: list[dict[str, str]], summary: list[dict[str, str]]) -> None:
    status_counts = Counter(row.get("verification_status", "") for row in protocol)
    file_counts = Counter(row.get("raw_file_status", "") for row in protocol)
    confidence_counts = Counter(row.get("metadata_confidence", "") for row in protocol)
    concept_counts = Counter(row.get("concept", "") for row in protocol)
    summary_table = "\n".join(f"| {row['metric']} | {row['value']} | {row['interpretation']} |" for row in summary)
    concept_table = "\n".join(
        f"| {concept} | {CONCEPT_CHECKS.get(concept, 'raw verification required')} |" for concept in sorted(CONCEPT_CHECKS)
    )
    REPORT_PATH.write_text(
        f"""# Raw Variable Verification Protocol

Status: planning artifact only. No country-wave is harmonization-ready until raw files are present, raw schemas are inspected, and raw values, labels, units, recall periods, merge keys, missing codes, and lineage pass verification.

## Counts

| Metric | Value | Interpretation |
|---|---:|---|
{summary_table}

## Verification Status

{markdown_count_table(status_counts, 'Verification status') if protocol else 'No protocol rows exist yet.'}

## Raw File Status

{markdown_count_table(file_counts, 'Raw file status') if protocol else 'No protocol rows exist yet.'}

## Metadata Confidence

{markdown_count_table(confidence_counts, 'Metadata confidence') if protocol else 'No protocol rows exist yet.'}

## Concept Coverage

{markdown_count_table(concept_counts, 'Concept') if protocol else 'No protocol rows exist yet.'}

## Required Raw Checks

| Concept | Raw verification checks |
|---|---|
{concept_table}

## Outputs

- `temp/raw_variable_verification_protocol.csv`: candidate raw variables and concept-specific checks.
- `temp/harmonization_recipe_scaffold.csv`: scaffold rows for expected harmonized variables. This is not `temp/harmonization_recipe.csv` and must not be used as an analysis recipe without raw verification.
- `result/raw_variable_verification_summary.csv`: machine-readable counts.

## Next Actions After Manual Downloads

1. Place raw files or archives under the dataset folders in `temp/raw_downloads/`.
2. Run `python script/17_audit_raw_downloads.py` and `python script/03_inspect_raw_schemas.py`.
3. Re-run this protocol script and inspect rows with `raw_variable_seen_value_audit_pending`.
4. Only after raw checks pass, create `temp/harmonization_recipe.csv` from verified rows, not from metadata-only candidates.
""",
        encoding="utf-8",
    )


def main() -> None:
    ensure_dirs()
    priorities = read_csv_dicts(PRIORITY_PATH)
    concepts = read_csv_dicts(CONCEPT_PATH)
    confidence = read_csv_dicts(CONFIDENCE_PATH)
    raw_files = read_csv_dicts(RAW_FILE_PATH)
    raw_variables = read_csv_dicts(RAW_VARIABLE_PATH)

    protocol = build_protocol_rows(priorities, concepts, confidence, raw_files, raw_variables)
    scaffold = build_scaffold_rows(priorities, concepts, protocol, raw_variables)
    summary = build_summary_rows(protocol, scaffold, raw_files, raw_variables)

    write_csv(PROTOCOL_PATH, protocol, PROTOCOL_COLUMNS)
    write_csv(SCAFFOLD_PATH, scaffold, SCAFFOLD_COLUMNS)
    write_csv(SUMMARY_PATH, summary, SUMMARY_COLUMNS)
    write_report(protocol, scaffold, summary)
    append_log(
        TEMP_DIR / "audit_log.md",
        f"Raw-variable verification protocol rows={len(protocol)} scaffold_rows={len(scaffold)} raw_variable_rows={len(raw_variables)}.",
    )
    print(f"Raw variable verification protocol rows={len(protocol)} scaffold_rows={len(scaffold)}.")


if __name__ == "__main__":
    main()
