from __future__ import annotations

import csv
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from common import REPORT_DIR, RESULT_DIR, TEMP_DIR, append_log, ensure_dirs, write_csv


PLAN_PATH = TEMP_DIR / "raw_ingestion_plan.csv"
CONCEPT_PATH = TEMP_DIR / "raw_ingestion_concept_checklist.csv"
MODULE_PATH = TEMP_DIR / "raw_ingestion_module_checklist.csv"
SUMMARY_PATH = RESULT_DIR / "raw_ingestion_plan_summary.csv"
REPORT_PATH = REPORT_DIR / "raw_ingestion_plan.md"

SUPPORTED_CONFIDENCE = {"high", "moderate"}

CONCEPTS = [
    {
        "concept": "household_id",
        "required_for": "harmonization",
        "map_category": "survey_design",
        "harmonized_variables": {"hhid"},
        "minimum_evidence": "household identifier available for module merges",
    },
    {
        "concept": "total_consumption_or_income",
        "required_for": "main_financial_sample",
        "map_category": "consumption",
        "harmonized_variables": {"total_consumption_or_income"},
        "minimum_evidence": "survey-team aggregate preferred; otherwise documented reconstruction components",
    },
    {
        "concept": "oop_health_expenditure",
        "required_for": "main_financial_sample",
        "map_category": "health_expenditure",
        "harmonized_variables": {"oop_health_expenditure"},
        "minimum_evidence": "out-of-pocket health spending amount with unit and recall period",
    },
    {
        "concept": "survey_weight",
        "required_for": "main_financial_sample",
        "map_category": "survey_design",
        "harmonized_variables": {"household_weight_or_person_weight"},
        "minimum_evidence": "household or person survey weight appropriate to the outcome unit",
    },
    {
        "concept": "survey_timing",
        "required_for": "main_financial_sample",
        "map_category": "survey_design",
        "harmonized_variables": {"interview_date_or_survey_month"},
        "minimum_evidence": "interview date/month or documented fieldwork month for climate lags",
    },
    {
        "concept": "climate_geography",
        "required_for": "main_financial_sample",
        "map_category": "geography",
        "harmonized_variables": {"admin1_or_admin2", "latitude_or_longitude"},
        "minimum_evidence": "admin geography, cluster, or GPS quality sufficient for climate linkage",
    },
    {
        "concept": "health_need",
        "required_for": "double_failure_sample",
        "map_category": "health_need_access",
        "harmonized_variables": {"illness_or_injury_need"},
        "minimum_evidence": "illness, injury, symptom, or other health-need denominator",
    },
    {
        "concept": "care_or_barrier",
        "required_for": "double_failure_sample",
        "map_category": "health_need_access",
        "harmonized_variables": {"care_sought", "care_not_sought_reason", "reason_not_sought_cost", "reason_not_sought_distance", "reason_not_sought_supply"},
        "minimum_evidence": "care-seeking or reason/barrier for not seeking care",
    },
    {
        "concept": "psu_cluster",
        "required_for": "survey_design_robustness",
        "map_category": "survey_design",
        "harmonized_variables": {"psu_or_cluster_id"},
        "minimum_evidence": "PSU, cluster, or enumeration area identifier for variance/clustering",
    },
    {
        "concept": "strata",
        "required_for": "survey_design_robustness",
        "map_category": "survey_design",
        "harmonized_variables": {"strata"},
        "minimum_evidence": "strata identifier if survey design requires it",
    },
    {
        "concept": "demographics",
        "required_for": "covariates_and_subgroups",
        "map_category": "demographics",
        "harmonized_variables": {"age", "sex", "education", "household_size", "household_head_marker", "asset_index_or_asset_variable"},
        "minimum_evidence": "age/sex/education/household structure/assets for adjustment and heterogeneity",
    },
    {
        "concept": "insurance",
        "required_for": "covariates_and_subgroups",
        "map_category": "health_expenditure",
        "harmonized_variables": {"health_insurance"},
        "minimum_evidence": "insurance or coverage variable, if available",
    },
    {
        "concept": "shocks_or_livelihood",
        "required_for": "mechanisms_and_heterogeneity",
        "map_category": "shocks",
        "harmonized_variables": {"shock_module_variable", "agriculture_livelihood", "coping_borrowed", "coping_sold_assets", "food_insecurity"},
        "minimum_evidence": "shock, agriculture/livelihood, coping, or food-insecurity variable",
    },
]

MAIN_REQUIRED = {"household_id", "total_consumption_or_income", "oop_health_expenditure", "survey_weight", "survey_timing", "climate_geography"}
DOUBLE_REQUIRED = MAIN_REQUIRED | {"health_need", "care_or_barrier"}

PLAN_COLUMNS = [
    "quality_rank",
    "country",
    "survey_name",
    "wave",
    "idno",
    "official_url",
    "quality_download_priority_tier",
    "manual_priority_rank",
    "local_target_folder",
    "raw_download_status",
    "raw_like_file_count",
    "documentation_file_count",
    "main_required_concepts_supported",
    "main_required_concepts_total",
    "double_required_concepts_supported",
    "double_required_concepts_total",
    "module_rows",
    "core_module_rows",
    "ingestion_gate_status",
    "next_command_after_download",
    "blocking_gap",
]

CONCEPT_COLUMNS = [
    "quality_rank",
    "country",
    "survey_name",
    "wave",
    "idno",
    "concept",
    "required_for",
    "metadata_support_status",
    "high_confidence_rows",
    "moderate_confidence_rows",
    "candidate_files",
    "candidate_variables",
    "minimum_raw_evidence_needed",
    "raw_verification_status",
    "verification_action",
]

MODULE_COLUMNS = [
    "quality_rank",
    "country",
    "survey_name",
    "wave",
    "idno",
    "file_name",
    "module_guess",
    "unit_guess",
    "candidate_categories",
    "candidate_harmonized_variables",
    "required_concepts_indicated",
    "candidate_variable_count",
    "candidate_raw_variables_examples",
    "module_priority_role",
    "verification_action",
]

SUMMARY_COLUMNS = ["metric", "value", "interpretation"]


def read_csv_dicts(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def clean(value: Any) -> str:
    return "" if value is None else str(value).strip()


def split_semicolon(value: str) -> set[str]:
    return {part.strip() for part in clean(value).split(";") if part.strip()}


def take_join(values: list[str], limit: int = 12) -> str:
    out = []
    seen = set()
    for value in values:
        if not value or value in seen:
            continue
        out.append(value)
        seen.add(value)
        if len(out) >= limit:
            break
    return ";".join(out)


def raw_idnos() -> set[str]:
    idnos = set()
    for row in read_csv_dicts(TEMP_DIR / "raw_schema_inventory" / "raw_file_inventory.csv"):
        source = " ".join(row.values()).replace("\\", "/")
        for token in source.split("/"):
            if "_" in token and any(char.isdigit() for char in token):
                idnos.add(token)
    for row in read_csv_dicts(TEMP_DIR / "raw_schema_inventory" / "raw_variable_catalog.csv"):
        source = " ".join(row.values()).replace("\\", "/")
        for token in source.split("/"):
            if "_" in token and any(char.isdigit() for char in token):
                idnos.add(token)
    return idnos


def concept_matches(row: dict[str, str], concept: dict[str, Any]) -> bool:
    return (
        row.get("map_category") == concept["map_category"]
        and row.get("harmonized_variable") in concept["harmonized_variables"]
        and row.get("metadata_confidence") in SUPPORTED_CONFIDENCE
    )


def build_concept_rows(priorities: list[dict[str, str]], variable_rows: list[dict[str, str]], verified_idnos: set[str]) -> list[dict[str, str]]:
    by_idno: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in variable_rows:
        by_idno[row.get("idno", "")].append(row)

    rows = []
    for priority in priorities:
        idno = priority.get("idno", "")
        for concept in CONCEPTS:
            candidates = [row for row in by_idno.get(idno, []) if concept_matches(row, concept)]
            candidates.sort(key=lambda row: (0 if row.get("metadata_confidence") == "high" else 1, row.get("file", ""), row.get("raw_variable", "")))
            high = sum(1 for row in candidates if row.get("metadata_confidence") == "high")
            moderate = sum(1 for row in candidates if row.get("metadata_confidence") == "moderate")
            support = "metadata_supported_raw_unverified" if candidates else "missing_from_metadata"
            raw_status = "raw_variables_inspected" if idno in verified_idnos else "raw_not_inspected"
            rows.append(
                {
                    "quality_rank": priority.get("quality_rank", ""),
                    "country": priority.get("country", ""),
                    "survey_name": priority.get("survey_name", ""),
                    "wave": priority.get("wave", ""),
                    "idno": idno,
                    "concept": concept["concept"],
                    "required_for": concept["required_for"],
                    "metadata_support_status": support,
                    "high_confidence_rows": str(high),
                    "moderate_confidence_rows": str(moderate),
                    "candidate_files": take_join([row.get("file", "") for row in candidates], 10),
                    "candidate_variables": take_join([row.get("raw_variable", "") for row in candidates], 16),
                    "minimum_raw_evidence_needed": concept["minimum_evidence"],
                    "raw_verification_status": raw_status,
                    "verification_action": "inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization",
                }
            )
    return rows


def concept_set_for_module(row: dict[str, str]) -> set[str]:
    hvars = split_semicolon(row.get("candidate_harmonized_variables", ""))
    concepts = set()
    if "hhid" in hvars:
        concepts.add("household_id")
    if "total_consumption_or_income" in hvars or {"food_consumption", "nonfood_consumption"} & hvars:
        concepts.add("total_consumption_or_income")
    if "oop_health_expenditure" in hvars:
        concepts.add("oop_health_expenditure")
    if "household_weight_or_person_weight" in hvars:
        concepts.add("survey_weight")
    if "interview_date_or_survey_month" in hvars:
        concepts.add("survey_timing")
    if {"admin1_or_admin2", "latitude_or_longitude"} & hvars:
        concepts.add("climate_geography")
    if "illness_or_injury_need" in hvars:
        concepts.add("health_need")
    if {"care_sought", "care_not_sought_reason", "reason_not_sought_cost", "reason_not_sought_distance", "reason_not_sought_supply"} & hvars:
        concepts.add("care_or_barrier")
    if "psu_or_cluster_id" in hvars:
        concepts.add("psu_cluster")
    if "strata" in hvars:
        concepts.add("strata")
    if {"age", "sex", "education", "household_size", "household_head_marker", "asset_index_or_asset_variable"} & hvars:
        concepts.add("demographics")
    if "health_insurance" in hvars:
        concepts.add("insurance")
    if {"shock_module_variable", "agriculture_livelihood", "coping_borrowed", "coping_sold_assets", "food_insecurity"} & hvars:
        concepts.add("shocks_or_livelihood")
    return concepts


def build_module_rows(priorities: list[dict[str, str]], checklist: list[dict[str, str]]) -> list[dict[str, str]]:
    priority_by_idno = {row.get("idno", ""): row for row in priorities}
    rows = []
    for row in checklist:
        idno = row.get("idno", "")
        if idno not in priority_by_idno:
            continue
        priority = priority_by_idno[idno]
        concepts = concept_set_for_module(row)
        if not concepts:
            continue
        if concepts & MAIN_REQUIRED:
            role = "core_main_sample_module_candidate"
        elif concepts & (DOUBLE_REQUIRED - MAIN_REQUIRED):
            role = "access_double_failure_module_candidate"
        else:
            role = "covariate_mechanism_or_design_module_candidate"
        rows.append(
            {
                "quality_rank": priority.get("quality_rank", ""),
                "country": priority.get("country", ""),
                "survey_name": priority.get("survey_name", ""),
                "wave": priority.get("wave", ""),
                "idno": idno,
                "file_name": row.get("file_name", ""),
                "module_guess": row.get("module_guess", ""),
                "unit_guess": row.get("unit_guess", ""),
                "candidate_categories": row.get("candidate_categories", ""),
                "candidate_harmonized_variables": row.get("candidate_harmonized_variables", ""),
                "required_concepts_indicated": ";".join(sorted(concepts)),
                "candidate_variable_count": row.get("candidate_variable_count", ""),
                "candidate_raw_variables_examples": row.get("candidate_raw_variables_examples", ""),
                "module_priority_role": role,
                "verification_action": "after download, confirm this file exists, inspect raw schema, check level/unit, and verify candidate variables before recipe use",
            }
        )
    rows.sort(key=lambda row: (int(row.get("quality_rank") or 9999), row.get("module_priority_role", ""), -int(row.get("candidate_variable_count") or 0), row.get("file_name", "")))
    return rows


def build_plan_rows(priorities: list[dict[str, str]], concept_rows: list[dict[str, str]], module_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    target_by_idno = {row.get("dataset_idno", ""): row for row in read_csv_dicts(TEMP_DIR / "raw_download_target_audit.csv")}
    concepts_by_idno: dict[str, list[dict[str, str]]] = defaultdict(list)
    modules_by_idno: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in concept_rows:
        concepts_by_idno[row.get("idno", "")].append(row)
    for row in module_rows:
        modules_by_idno[row.get("idno", "")].append(row)

    rows = []
    for priority in priorities:
        idno = priority.get("idno", "")
        concepts = concepts_by_idno.get(idno, [])
        supported = {row.get("concept", "") for row in concepts if row.get("metadata_support_status") == "metadata_supported_raw_unverified"}
        target = target_by_idno.get(idno, {})
        raw_like_count = int(target.get("raw_tabular_file_count") or 0) + int(target.get("archive_file_count") or 0)
        doc_count = int(target.get("documentation_file_count") or 0)
        missing_main = sorted(MAIN_REQUIRED - supported)
        missing_double = sorted(DOUBLE_REQUIRED - supported)
        if raw_like_count > 0:
            gate = "ready_for_raw_schema_inspection"
            gap = "run script/03_inspect_raw_schemas.py and verify raw variables"
        else:
            gate = "waiting_for_manual_download"
            gap = "place raw archives/files in target folder before schema inspection"
        rows.append(
            {
                "quality_rank": priority.get("quality_rank", ""),
                "country": priority.get("country", ""),
                "survey_name": priority.get("survey_name", ""),
                "wave": priority.get("wave", ""),
                "idno": idno,
                "official_url": priority.get("official_url", ""),
                "quality_download_priority_tier": priority.get("quality_download_priority_tier", ""),
                "manual_priority_rank": priority.get("manual_priority_rank", ""),
                "local_target_folder": priority.get("local_target_folder", f"temp/raw_downloads/{idno}/"),
                "raw_download_status": target.get("status", "not_in_raw_target_audit"),
                "raw_like_file_count": str(raw_like_count),
                "documentation_file_count": str(doc_count),
                "main_required_concepts_supported": str(len(MAIN_REQUIRED & supported)),
                "main_required_concepts_total": str(len(MAIN_REQUIRED)),
                "double_required_concepts_supported": str(len(DOUBLE_REQUIRED & supported)),
                "double_required_concepts_total": str(len(DOUBLE_REQUIRED)),
                "module_rows": str(len(modules_by_idno.get(idno, []))),
                "core_module_rows": str(sum(1 for row in modules_by_idno.get(idno, []) if row.get("module_priority_role") == "core_main_sample_module_candidate")),
                "ingestion_gate_status": gate,
                "next_command_after_download": "python script/17_audit_raw_downloads.py; python script/03_inspect_raw_schemas.py; python script/22_build_raw_ingestion_plan.py",
                "blocking_gap": gap + ("; metadata missing main concepts: " + ";".join(missing_main) if missing_main else "") + ("; metadata missing double-failure concepts: " + ";".join(concept for concept in missing_double if concept not in missing_main) if missing_double else ""),
            }
        )
    return rows


def summary_rows(plan_rows: list[dict[str, str]], concept_rows: list[dict[str, str]], module_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    gate_counts = Counter(row.get("ingestion_gate_status", "") for row in plan_rows)
    concept_supported = sum(1 for row in concept_rows if row.get("metadata_support_status") == "metadata_supported_raw_unverified")
    raw_verified = sum(1 for row in concept_rows if row.get("raw_verification_status") == "raw_variables_inspected")
    rows = [
        {"metric": "raw_ingestion_plan_rows", "value": str(len(plan_rows)), "interpretation": "Quality-screened country-waves with explicit target folders and next checks."},
        {"metric": "raw_ingestion_concept_rows", "value": str(len(concept_rows)), "interpretation": "Dataset-concept verification checklist rows."},
        {"metric": "raw_ingestion_module_rows", "value": str(len(module_rows)), "interpretation": "Candidate module/file rows to inspect after download."},
        {"metric": "metadata_supported_concept_rows", "value": str(concept_supported), "interpretation": "Concept rows supported by moderate/high metadata evidence, still raw-unverified."},
        {"metric": "raw_verified_concept_rows", "value": str(raw_verified), "interpretation": "Concept rows where raw variables have been inspected."},
    ]
    for gate, count in sorted(gate_counts.items()):
        rows.append({"metric": f"gate_count_{gate}", "value": str(count), "interpretation": "Raw ingestion gate status count."})
    return rows


def markdown_table(rows: list[dict[str, str]], columns: list[str], limit: int = 15) -> str:
    lines = ["| " + " | ".join(columns) + " |", "|" + "|".join("---" for _ in columns) + "|"]
    for row in rows[:limit]:
        values = []
        for column in columns:
            value = clean(row.get(column, "")).replace("|", "/")
            if len(value) > 120:
                value = value[:117] + "..."
            values.append(value)
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines)


def write_report(plan_rows: list[dict[str, str]], concept_rows: list[dict[str, str]], module_rows: list[dict[str, str]], summaries: list[dict[str, str]]) -> None:
    gate_counts = Counter(row.get("ingestion_gate_status", "") for row in plan_rows)
    concept_counts = Counter(row.get("concept", "") for row in concept_rows if row.get("metadata_support_status") == "metadata_supported_raw_unverified")
    lines = [
        "# Raw Ingestion Plan",
        "",
        "Status: raw ingestion is planned but not executed. These artifacts organize what must be checked after manual downloads; they do not verify raw data or select an analytical sample.",
        "",
        "## Gate Counts",
        "",
        "| Gate status | Count |",
        "|---|---:|",
    ]
    for key, count in sorted(gate_counts.items()):
        lines.append(f"| {key or 'blank'} | {count} |")
    lines.extend(
        [
            "",
            "## Summary Metrics",
            "",
            "| Metric | Value | Interpretation |",
            "|---|---:|---|",
        ]
    )
    for row in summaries:
        lines.append(f"| {row['metric']} | {row['value']} | {row['interpretation']} |")
    lines.extend(
        [
            "",
            "## First Download Targets",
            "",
            markdown_table(plan_rows, ["quality_rank", "country", "wave", "idno", "raw_download_status", "main_required_concepts_supported", "double_required_concepts_supported", "local_target_folder"], 12),
            "",
            "## Supported Concepts From Metadata",
            "",
            "| Concept | Supported rows |",
            "|---|---:|",
        ]
    )
    for concept, count in concept_counts.most_common():
        lines.append(f"| {concept} | {count} |")
    lines.extend(
        [
            "",
            "## Required Action After Manual Download",
            "",
            "1. Place original archives/files in the listed `temp/raw_downloads/<IDNO>/` folder.",
            "2. Run `python script/17_audit_raw_downloads.py` to checksum and classify files.",
            "3. Run `python script/03_inspect_raw_schemas.py` to create raw file and variable inventories.",
            "4. Re-run `python script/22_build_raw_ingestion_plan.py` and inspect whether raw verification status changes.",
            "5. Build `temp/harmonization_recipe.csv` only from raw-inspected variables with verified units, recall periods, missing values, levels, and merge keys.",
            "",
            "## Machine-Readable Outputs",
            "",
            "- `temp/raw_ingestion_plan.csv`",
            "- `temp/raw_ingestion_concept_checklist.csv`",
            "- `temp/raw_ingestion_module_checklist.csv`",
            "- `result/raw_ingestion_plan_summary.csv`",
        ]
    )
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    ensure_dirs()
    priorities = read_csv_dicts(TEMP_DIR / "metadata_quality_download_priority.csv")
    variable_rows = read_csv_dicts(TEMP_DIR / "variable_map_confidence_audit.csv")
    checklist = read_csv_dicts(TEMP_DIR / "manual_download_file_checklist.csv")
    verified = raw_idnos()
    concept_rows = build_concept_rows(priorities, variable_rows, verified)
    module_rows = build_module_rows(priorities, checklist)
    plan_rows = build_plan_rows(priorities, concept_rows, module_rows)
    summaries = summary_rows(plan_rows, concept_rows, module_rows)
    write_csv(PLAN_PATH, plan_rows, PLAN_COLUMNS)
    write_csv(CONCEPT_PATH, concept_rows, CONCEPT_COLUMNS)
    write_csv(MODULE_PATH, module_rows, MODULE_COLUMNS)
    write_csv(SUMMARY_PATH, summaries, SUMMARY_COLUMNS)
    write_report(plan_rows, concept_rows, module_rows, summaries)
    waiting = sum(1 for row in plan_rows if row.get("ingestion_gate_status") == "waiting_for_manual_download")
    ready = sum(1 for row in plan_rows if row.get("ingestion_gate_status") == "ready_for_raw_schema_inspection")
    append_log(TEMP_DIR / "audit_log.md", f"Raw ingestion plan rows={len(plan_rows)} concept_rows={len(concept_rows)} module_rows={len(module_rows)} waiting={waiting} ready={ready}.")
    print(f"Raw ingestion plan rows={len(plan_rows)} concept_rows={len(concept_rows)} module_rows={len(module_rows)} waiting={waiting} ready={ready}.")


if __name__ == "__main__":
    main()
