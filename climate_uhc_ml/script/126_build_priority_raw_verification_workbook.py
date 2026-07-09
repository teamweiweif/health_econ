from __future__ import annotations

import csv
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from common import PROJECT_ROOT, REPORT_DIR, RESULT_DIR, TEMP_DIR, append_log, ensure_dirs, write_csv


WAVE_PLAN_PATH = RESULT_DIR / "priority_promotion_acquisition_wave_plan.csv"
RAW_INTAKE_GATE_PATH = TEMP_DIR / "priority_raw_intake_gate.csv"
CLIMATE_PREFLIGHT_PATH = TEMP_DIR / "priority_climate_linkage_preflight.csv"
CONCEPT_PATH = TEMP_DIR / "raw_ingestion_concept_checklist.csv"
PROTOCOL_PATH = TEMP_DIR / "raw_variable_verification_protocol.csv"
RAW_FILE_PATH = TEMP_DIR / "raw_schema_inventory" / "raw_file_inventory.csv"
RAW_VARIABLE_PATH = TEMP_DIR / "raw_schema_inventory" / "raw_variable_catalog.csv"

DATASET_GATE_PATH = RESULT_DIR / "priority_dataset_verification_gate.csv"
REQUIREMENT_CHECKLIST_PATH = TEMP_DIR / "priority_promotion_verification_checklist.csv"
CONCEPT_TEMPLATE_PATH = TEMP_DIR / "priority_concept_verification_template.csv"
VARIABLE_TEMPLATE_PATH = TEMP_DIR / "priority_variable_verification_template.csv"
SUMMARY_PATH = RESULT_DIR / "priority_raw_verification_workbook_summary.csv"
REPORT_PATH = REPORT_DIR / "priority_raw_verification_workbook.md"

FINANCIAL_CORE = {"total_consumption_or_income", "oop_health_expenditure", "survey_weight", "survey_timing", "climate_geography"}
DOUBLE_FAILURE_CORE = {"health_need", "care_or_barrier"}
DESIGN_CORE = {"household_id", "psu_cluster", "strata", "survey_weight", "survey_timing", "climate_geography"}

REQUIREMENTS = [
    {
        "requirement_id": "household_person_merge_keys",
        "mapped_concepts": ["household_id", "demographics"],
        "minimum_evidence": "Household/person IDs and module-level keys match across raw files; key cardinality and duplicates are documented.",
    },
    {
        "requirement_id": "weights_and_survey_design",
        "mapped_concepts": ["survey_weight", "psu_cluster", "strata"],
        "minimum_evidence": "Household/person weights, PSU/cluster, strata, and any design notes are verified from raw values and documentation.",
    },
    {
        "requirement_id": "consumption_or_income_aggregate",
        "mapped_concepts": ["total_consumption_or_income"],
        "minimum_evidence": "Survey-team consumption/income aggregate or documented reconstruction variables are verified with units and period.",
    },
    {
        "requirement_id": "oop_health_expenditure",
        "mapped_concepts": ["oop_health_expenditure"],
        "minimum_evidence": "OOP health spending variables are verified with payer scope, units, recall period, zero/missing semantics, and aggregation level.",
    },
    {
        "requirement_id": "illness_need_care_access",
        "mapped_concepts": ["health_need", "care_or_barrier", "insurance"],
        "minimum_evidence": "Illness/need denominator, care-seeking, forgone care, barrier categories, and insurance variables are verified.",
    },
    {
        "requirement_id": "survey_timing",
        "mapped_concepts": ["survey_timing"],
        "minimum_evidence": "Interview date/month/year or fieldwork timing is verified and can support pre-interview lag windows.",
    },
    {
        "requirement_id": "geography_climate_linkage",
        "mapped_concepts": ["climate_geography"],
        "minimum_evidence": "GPS, cluster, EA, or admin geography is verified with geolocation quality, displacement/suppression, and boundary/crosswalk notes.",
    },
    {
        "requirement_id": "missing_skip_units_recall",
        "mapped_concepts": [
            "household_id",
            "survey_weight",
            "total_consumption_or_income",
            "oop_health_expenditure",
            "health_need",
            "care_or_barrier",
            "survey_timing",
            "climate_geography",
        ],
        "minimum_evidence": "Missing codes, skip patterns, units, recall periods, valid ranges, and outlier handling are documented for all critical variables.",
    },
]

DATASET_COLUMNS = [
    "acquisition_batch_rank",
    "batch_role",
    "country",
    "survey_name",
    "wave",
    "idno",
    "official_url",
    "local_target_folder",
    "raw_file_inventory_rows",
    "raw_variable_catalog_rows",
    "required_concept_rows",
    "concepts_with_metadata_support",
    "concepts_missing_metadata",
    "critical_concepts_missing_metadata",
    "requirements_ready_for_manual_audit",
    "concepts_ready_for_manual_value_audit",
    "variables_ready_for_manual_value_audit",
    "accepted_chirps_era5_route_status",
    "current_gate_status",
    "next_action",
    "handoff_readme",
    "guardrail",
]

REQUIREMENT_COLUMNS = [
    "acquisition_batch_rank",
    "batch_role",
    "country",
    "survey_name",
    "wave",
    "idno",
    "requirement_id",
    "mapped_concepts",
    "minimum_evidence",
    "mapped_concept_gate_summary",
    "raw_package_gate_status",
    "climate_gate_status",
    "current_requirement_gate",
    "fill_evidence_file_or_module",
    "fill_raw_variables_used",
    "fill_value_label_pass",
    "fill_unit_or_recall_pass",
    "fill_merge_key_or_level_pass",
    "fill_missing_skip_pattern_pass",
    "fill_promote_requirement",
    "review_notes",
]

CONCEPT_COLUMNS = [
    "acquisition_batch_rank",
    "batch_role",
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
    "acquisition_batch_rank",
    "batch_role",
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


def read_csv_dicts(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def clean(value: Any) -> str:
    return "" if value is None else str(value).strip()


def safe_int(value: Any, default: int = 0) -> int:
    try:
        text = str(value).strip()
        return int(float(text)) if text else default
    except (TypeError, ValueError):
        return default


def split_values(value: str) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for item in (value or "").replace(",", ";").split(";"):
        item = item.strip()
        if item and item not in seen:
            out.append(item)
            seen.add(item)
    return out


def compact(values: list[str], limit: int = 20, sep: str = ";") -> str:
    out: list[str] = []
    seen: set[str] = set()
    for value in values:
        item = clean(value)
        if item and item not in seen:
            out.append(item)
            seen.add(item)
        if len(out) >= limit:
            break
    return sep.join(out)


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(PROJECT_ROOT)).replace("\\", "/")
    except ValueError:
        return str(path).replace("\\", "/")


def group(rows: list[dict[str, str]], field: str) -> dict[str, list[dict[str, str]]]:
    out: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        key = clean(row.get(field))
        if key:
            out[key].append(row)
    return out


def first_by(rows: list[dict[str, str]], field: str) -> dict[str, dict[str, str]]:
    out: dict[str, dict[str, str]] = {}
    for row in rows:
        key = clean(row.get(field))
        if key and key not in out:
            out[key] = row
    return out


def preserve_fill_values(
    rows: list[dict[str, str]],
    existing_path: Path,
    key_columns: list[str],
    fill_columns: list[str],
) -> list[dict[str, str]]:
    existing_rows = read_csv_dicts(existing_path)
    existing_by_key = {
        tuple(clean(row.get(column)) for column in key_columns): row
        for row in existing_rows
    }
    for row in rows:
        old = existing_by_key.get(tuple(clean(row.get(column)) for column in key_columns), {})
        for column in fill_columns:
            if clean(old.get(column)):
                row[column] = old.get(column, "")
    return rows


def wave_by_id() -> dict[str, dict[str, str]]:
    rows = read_csv_dicts(WAVE_PLAN_PATH)
    return {row.get("idno", ""): row for row in rows if row.get("idno", "")}


def infer_idno(text: str, idnos: set[str]) -> str:
    low = (text or "").lower().replace("\\", "/")
    for idno in sorted(idnos, key=len, reverse=True):
        if idno.lower() in low:
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
    out = []
    idno_low = idno.lower()
    for row in raw_files:
        text = " ".join(row.values()).lower().replace("\\", "/")
        if idno_low in text:
            out.append(row.get("source_path", ""))
    return out


def raw_variables_present_for_id(raw_variables: list[dict[str, str]], idno: str) -> list[dict[str, str]]:
    out = []
    idno_low = idno.lower()
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
    if any(name.lower() in present_text for name in files):
        return "candidate_file_present"
    return "raw_files_present_candidate_file_not_matched"


def variable_status(candidate_variables: str, present_variables: list[dict[str, str]]) -> str:
    variables = split_values(candidate_variables)
    if not variables:
        return "no_candidate_variable_metadata"
    if not present_variables:
        return "raw_variable_catalog_absent"
    present_names = {row.get("variable_name", "").lower() for row in present_variables}
    if any(name.lower() in present_names for name in variables):
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


def build_concept_rows(waves: dict[str, dict[str, str]], raw_files: list[dict[str, str]], raw_variables: list[dict[str, str]]) -> list[dict[str, str]]:
    concepts_by_id = group(read_csv_dicts(CONCEPT_PATH), "idno")
    rows: list[dict[str, str]] = []
    for idno, wave in waves.items():
        present_paths = raw_files_present_for_id(raw_files, idno)
        present_vars = raw_variables_present_for_id(raw_variables, idno)
        for concept in concepts_by_id.get(idno, []):
            raw_file_status = file_status(concept.get("candidate_files", ""), present_paths)
            raw_variable_status = variable_status(concept.get("candidate_variables", ""), present_vars)
            concept_name = concept.get("concept", "")
            rows.append(
                {
                    "acquisition_batch_rank": wave.get("acquisition_batch_rank", ""),
                    "batch_role": wave.get("batch_role", ""),
                    "country": wave.get("country", ""),
                    "survey_name": wave.get("survey_name", ""),
                    "wave": wave.get("wave", ""),
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
    rows.sort(key=lambda row: (safe_int(row["acquisition_batch_rank"]), row["concept"]))
    return rows


def build_variable_rows(waves: dict[str, dict[str, str]], raw_files: list[dict[str, str]], raw_variables: list[dict[str, str]]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    protocol_rows = [row for row in read_csv_dicts(PROTOCOL_PATH) if row.get("idno", "") in waves]
    for protocol in protocol_rows:
        idno = protocol.get("idno", "")
        wave = waves[idno]
        present_paths = raw_files_present_for_id(raw_files, idno)
        present_vars = raw_variables_present_for_id(raw_variables, idno)
        raw_file_status = file_status(protocol.get("candidate_files", ""), present_paths)
        raw_variable_status = variable_status(protocol.get("candidate_raw_variable", ""), present_vars)
        status, decision = verification_status(raw_file_status, raw_variable_status)
        rows.append(
            {
                "acquisition_batch_rank": wave.get("acquisition_batch_rank", ""),
                "batch_role": wave.get("batch_role", ""),
                "country": wave.get("country", ""),
                "survey_name": wave.get("survey_name", ""),
                "wave": wave.get("wave", ""),
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
    rows.sort(key=lambda row: (safe_int(row["acquisition_batch_rank"]), row["concept"], safe_int(row["candidate_rank_within_concept"])))
    return rows


def requirement_gate(mapped_concepts: list[str], concept_map: dict[str, dict[str, str]], raw_gate_status: str, climate_gate_status: str) -> tuple[str, str]:
    if raw_gate_status == "blocked_manual_raw_package_required":
        return "blocked_raw_package_required", "raw package absent"
    concept_gates = [concept_map.get(concept, {}).get("current_concept_gate", "concept_not_mapped") for concept in mapped_concepts]
    if any(gate in {"blocked_missing_metadata_candidate", "concept_not_mapped"} for gate in concept_gates):
        return "blocked_missing_metadata_candidate", compact(concept_gates)
    if any(gate != "ready_for_manual_value_label_unit_key_audit" for gate in concept_gates):
        return "blocked_raw_values_unverified", compact(concept_gates)
    if "geography" in ";".join(mapped_concepts) or "survey_timing" in mapped_concepts:
        if not climate_gate_status.startswith("route_preflight_ready"):
            return "blocked_climate_linkage_not_accepted", climate_gate_status
    return "ready_for_manual_requirement_audit", compact(concept_gates)


def build_requirement_rows(
    waves: dict[str, dict[str, str]],
    concept_rows: list[dict[str, str]],
    raw_gate_by_id: dict[str, dict[str, str]],
    climate_by_id: dict[str, dict[str, str]],
) -> list[dict[str, str]]:
    concepts_by_id = group(concept_rows, "idno")
    rows: list[dict[str, str]] = []
    for idno, wave in waves.items():
        concept_map = {row["concept"]: row for row in concepts_by_id.get(idno, [])}
        raw_gate_status = raw_gate_by_id.get(idno, {}).get("current_gate_status", "raw_gate_missing")
        climate_status = climate_by_id.get(idno, {}).get("current_climate_linkage_gate_status", "climate_preflight_missing")
        for req in REQUIREMENTS:
            mapped = req["mapped_concepts"]
            gate, summary = requirement_gate(mapped, concept_map, raw_gate_status, climate_status)
            rows.append(
                {
                    "acquisition_batch_rank": wave.get("acquisition_batch_rank", ""),
                    "batch_role": wave.get("batch_role", ""),
                    "country": wave.get("country", ""),
                    "survey_name": wave.get("survey_name", ""),
                    "wave": wave.get("wave", ""),
                    "idno": idno,
                    "requirement_id": req["requirement_id"],
                    "mapped_concepts": ";".join(mapped),
                    "minimum_evidence": req["minimum_evidence"],
                    "mapped_concept_gate_summary": summary,
                    "raw_package_gate_status": raw_gate_status,
                    "climate_gate_status": climate_status,
                    "current_requirement_gate": gate,
                    "fill_evidence_file_or_module": "",
                    "fill_raw_variables_used": "",
                    "fill_value_label_pass": "",
                    "fill_unit_or_recall_pass": "",
                    "fill_merge_key_or_level_pass": "",
                    "fill_missing_skip_pattern_pass": "",
                    "fill_promote_requirement": "",
                    "review_notes": "",
                }
            )
    return rows


def target_folder_path(folder: str, idno: str) -> Path:
    folder_clean = clean(folder).replace("\\", "/").strip("/")
    if folder_clean.startswith("temp/raw_downloads/"):
        return PROJECT_ROOT / folder_clean
    if folder_clean:
        return TEMP_DIR / "raw_downloads" / folder_clean
    return TEMP_DIR / "raw_downloads" / idno


def dataset_gate_status(file_count: int, variable_count: int, ready_requirements: int, total_requirements: int, accepted_route: str) -> tuple[str, str]:
    if file_count == 0:
        return "blocked_raw_files_absent", "Download/place complete original raw package and documentation into the target folder."
    if variable_count == 0:
        return "blocked_raw_variable_catalog_absent", "Run raw schema inspection and confirm expected modules were extracted."
    if ready_requirements < total_requirements:
        return "blocked_required_promotion_evidence_incomplete", "Fill requirement, concept, and variable verification templates after raw inspection."
    if not accepted_route.startswith("accepted"):
        return "blocked_climate_linkage_not_accepted", "Run climate linkage validation and accept CHIRPS/ERA5 route before data promotion."
    return "ready_for_harmonization_recipe_review", "Create harmonization recipe only after independent review of filled evidence columns."


def write_dataset_handoff(wave: dict[str, str], dataset_row: dict[str, str], req_rows: list[dict[str, str]]) -> str:
    folder = target_folder_path(wave.get("local_target_folder", ""), wave.get("idno", ""))
    folder.mkdir(parents=True, exist_ok=True)
    readme = folder / "_PRIORITY_RAW_VERIFICATION_WORKBOOK.md"
    req_table = markdown_rows(
        req_rows,
        ["requirement_id", "current_requirement_gate", "mapped_concepts", "minimum_evidence"],
        20,
    )
    readme.write_text(
        f"""# Priority Raw Verification Workbook: {wave.get('idno', '')}

This workbook is the post-download verification gate for `{wave.get('country', '')}`
`{wave.get('wave', '')}`. It does not verify the dataset by itself; all blank
`fill_*` columns in the machine-readable templates must be completed from raw
files, labels, values, units, recall periods, missing codes, skip patterns, and
merge-key checks.

Current dataset gate: `{dataset_row['current_gate_status']}`

Next action: {dataset_row['next_action']}

Accepted CHIRPS/ERA5 route: `{dataset_row['accepted_chirps_era5_route_status']}`

## Requirement Checklist

{req_table}

## Machine-Readable Templates

- `temp/priority_promotion_verification_checklist.csv`
- `temp/priority_concept_verification_template.csv`
- `temp/priority_variable_verification_template.csv`
- `result/priority_dataset_verification_gate.csv`

## Guardrail

Do not write this wave into `data/` until every requirement row, critical
concept row, and selected variable row has raw-backed evidence and the climate
linkage route is accepted.
""",
        encoding="utf-8",
    )
    return rel(readme)


def build_dataset_rows(
    waves: dict[str, dict[str, str]],
    concept_rows: list[dict[str, str]],
    variable_rows: list[dict[str, str]],
    requirement_rows: list[dict[str, str]],
    raw_files: list[dict[str, str]],
    raw_variables: list[dict[str, str]],
    climate_by_id: dict[str, dict[str, str]],
) -> list[dict[str, str]]:
    concepts_by_id = group(concept_rows, "idno")
    variables_by_id = group(variable_rows, "idno")
    requirements_by_id = group(requirement_rows, "idno")
    idnos = set(waves)
    file_counts = raw_file_counts(raw_files, idnos)
    variable_counts = raw_variable_counts(raw_variables, idnos)
    rows: list[dict[str, str]] = []
    for idno, wave in sorted(waves.items(), key=lambda item: safe_int(item[1].get("acquisition_batch_rank"))):
        concepts = concepts_by_id.get(idno, [])
        variables = variables_by_id.get(idno, [])
        requirements = requirements_by_id.get(idno, [])
        missing_metadata = [row["concept"] for row in concepts if row.get("metadata_support_status") == "missing_from_metadata"]
        critical_missing = [
            row["concept"]
            for row in concepts
            if row.get("metadata_support_status") == "missing_from_metadata"
            and (row.get("is_financial_core") == "1" or row.get("is_double_failure_core") == "1" or row.get("is_design_core") == "1")
        ]
        ready_concepts = [row for row in concepts if row.get("current_concept_gate") == "ready_for_manual_value_label_unit_key_audit"]
        ready_variables = [row for row in variables if row.get("verification_status") == "ready_for_manual_value_audit"]
        ready_requirements = [row for row in requirements if row.get("current_requirement_gate") == "ready_for_manual_requirement_audit"]
        accepted_route = climate_by_id.get(idno, {}).get("accepted_chirps_era5_route_status", "not_accepted_missing_climate_preflight")
        status, action = dataset_gate_status(file_counts[idno], variable_counts[idno], len(ready_requirements), len(requirements), accepted_route)
        dataset_row = {
            "acquisition_batch_rank": wave.get("acquisition_batch_rank", ""),
            "batch_role": wave.get("batch_role", ""),
            "country": wave.get("country", ""),
            "survey_name": wave.get("survey_name", ""),
            "wave": wave.get("wave", ""),
            "idno": idno,
            "official_url": wave.get("official_url", ""),
            "local_target_folder": wave.get("local_target_folder", ""),
            "raw_file_inventory_rows": str(file_counts[idno]),
            "raw_variable_catalog_rows": str(variable_counts[idno]),
            "required_concept_rows": str(len(concepts)),
            "concepts_with_metadata_support": str(sum(1 for row in concepts if row.get("metadata_support_status") != "missing_from_metadata")),
            "concepts_missing_metadata": compact(missing_metadata),
            "critical_concepts_missing_metadata": compact(critical_missing),
            "requirements_ready_for_manual_audit": str(len(ready_requirements)),
            "concepts_ready_for_manual_value_audit": str(len(ready_concepts)),
            "variables_ready_for_manual_value_audit": str(len(ready_variables)),
            "accepted_chirps_era5_route_status": accepted_route,
            "current_gate_status": status,
            "next_action": action,
            "handoff_readme": "",
            "guardrail": "do not write to data/ until raw evidence, requirement checklist, harmonization recipe, and accepted CHIRPS/ERA5 linkage all pass",
        }
        dataset_row["handoff_readme"] = write_dataset_handoff(wave, dataset_row, requirements)
        rows.append(dataset_row)
    return rows


def build_summary(
    dataset_rows: list[dict[str, str]],
    requirement_rows: list[dict[str, str]],
    concept_rows: list[dict[str, str]],
    variable_rows: list[dict[str, str]],
) -> list[dict[str, str]]:
    dataset_status = Counter(row["current_gate_status"] for row in dataset_rows)
    req_status = Counter(row["current_requirement_gate"] for row in requirement_rows)
    concept_status = Counter(row["current_concept_gate"] for row in concept_rows)
    variable_status = Counter(row["verification_status"] for row in variable_rows)
    role_counts = Counter(row["batch_role"] for row in dataset_rows)
    priority_countries = len({row["country"] for row in dataset_rows if row["batch_role"] == "priority_10_wave_batch"})
    handoff_count = sum(1 for row in dataset_rows if row.get("handoff_readme"))
    rows = [
        {"metric": "priority_dataset_verification_gate_rows", "value": str(len(dataset_rows)), "interpretation": "Dataset-level priority raw verification gate rows."},
        {"metric": "priority_verification_priority_10_rows", "value": str(role_counts.get("priority_10_wave_batch", 0)), "interpretation": "Immediate priority waves covered by the workbook."},
        {"metric": "priority_verification_priority_10_countries", "value": str(priority_countries), "interpretation": "Priority countries covered by the workbook."},
        {"metric": "priority_verification_backup_rows", "value": str(role_counts.get("sixth_country_backup_candidate", 0)), "interpretation": "Sixth-country backup rows covered by the workbook."},
        {"metric": "priority_requirement_checklist_rows", "value": str(len(requirement_rows)), "interpretation": "Explicit requirement checklist rows aligned to the dataset promotion objective."},
        {"metric": "priority_concept_template_rows", "value": str(len(concept_rows)), "interpretation": "Concept-level raw verification template rows."},
        {"metric": "priority_variable_template_rows", "value": str(len(variable_rows)), "interpretation": "Variable-level raw verification template rows."},
        {"metric": "priority_datasets_ready_for_manual_value_audit", "value": str(dataset_status.get("ready_for_harmonization_recipe_review", 0)), "interpretation": "Datasets with all promotion evidence ready for harmonization recipe review."},
        {"metric": "priority_requirements_ready_for_manual_audit", "value": str(req_status.get("ready_for_manual_requirement_audit", 0)), "interpretation": "Requirement rows ready for manual raw-backed review."},
        {"metric": "priority_concepts_ready_for_manual_value_audit", "value": str(concept_status.get("ready_for_manual_value_label_unit_key_audit", 0)), "interpretation": "Concept rows ready for manual value/label/unit/key audit."},
        {"metric": "priority_variables_ready_for_manual_value_audit", "value": str(variable_status.get("ready_for_manual_value_audit", 0)), "interpretation": "Variable rows ready for manual value/label/unit/key audit."},
        {"metric": "priority_raw_verification_handoff_readmes_written", "value": str(handoff_count), "interpretation": "Per-wave raw verification workbook README files written."},
        {"metric": "modeling_gate_status", "value": "blocked", "interpretation": "Models remain blocked until promoted registry thresholds and accepted climate linkage pass."},
    ]
    for status, count in sorted(dataset_status.items()):
        rows.append({"metric": f"dataset_gate_{status}", "value": str(count), "interpretation": "Dataset gate status count."})
    for status, count in sorted(req_status.items()):
        rows.append({"metric": f"requirement_gate_{status}", "value": str(count), "interpretation": "Requirement gate status count."})
    for status, count in sorted(concept_status.items()):
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
        lines.append(f"| `{key or 'blank'}` | {count} |")
    return "\n".join(lines)


def write_report(
    dataset_rows: list[dict[str, str]],
    requirement_rows: list[dict[str, str]],
    concept_rows: list[dict[str, str]],
    variable_rows: list[dict[str, str]],
    summary: list[dict[str, str]],
) -> None:
    dataset_status = Counter(row["current_gate_status"] for row in dataset_rows)
    req_status = Counter(row["current_requirement_gate"] for row in requirement_rows)
    concept_status = Counter(row["current_concept_gate"] for row in concept_rows)
    variable_status = Counter(row["verification_status"] for row in variable_rows)
    summary_table = "\n".join(f"| {row['metric']} | {row['value']} | {row['interpretation']} |" for row in summary)
    REPORT_PATH.write_text(
        f"""# Priority Raw Verification Workbook

Status: fillable post-download verification workbook for the current priority
10-wave batch and sixth-country backups. It does not verify any dataset by
itself and does not promote any row into `data/`.

## Summary

| Metric | Value | Interpretation |
|---|---:|---|
{summary_table}

## Dataset Gate Status

{markdown_count_table(dataset_status, 'Dataset gate') if dataset_rows else 'No dataset gate rows exist.'}

## Requirement Gate Status

{markdown_count_table(req_status, 'Requirement gate') if requirement_rows else 'No requirement rows exist.'}

## Concept Gate Status

{markdown_count_table(concept_status, 'Concept gate') if concept_rows else 'No concept verification rows exist.'}

## Variable Verification Status

{markdown_count_table(variable_status, 'Variable status') if variable_rows else 'No variable verification rows exist.'}

## Dataset Gate Rows

{markdown_rows(dataset_rows, ['acquisition_batch_rank', 'batch_role', 'idno', 'country', 'wave', 'raw_file_inventory_rows', 'raw_variable_catalog_rows', 'current_gate_status', 'next_action'], 20)}

## Requirement Checklist Preview

{markdown_rows(requirement_rows, ['acquisition_batch_rank', 'idno', 'requirement_id', 'current_requirement_gate', 'minimum_evidence'], 30)}

## How To Use

1. Download complete original raw packages into each priority target folder.
2. Run `python script/17_audit_raw_downloads.py` and `python script/03_inspect_raw_schemas.py`.
3. Rerun `python script/126_build_priority_raw_verification_workbook.py`.
4. Fill the blank `fill_*` columns in the requirement, concept, and variable templates only after inspecting raw values, labels, units, recall periods, missing codes, levels, skip patterns, and merge keys.
5. Promote a wave only when all requirement rows, critical concept rows, selected variable rows, and accepted CHIRPS/ERA5 linkage gates pass.

## Machine-Readable Outputs

- `result/priority_dataset_verification_gate.csv`
- `temp/priority_promotion_verification_checklist.csv`
- `temp/priority_concept_verification_template.csv`
- `temp/priority_variable_verification_template.csv`
- `result/priority_raw_verification_workbook_summary.csv`
""",
        encoding="utf-8",
    )


def main() -> None:
    ensure_dirs()
    waves = wave_by_id()
    raw_files = read_csv_dicts(RAW_FILE_PATH)
    raw_variables = read_csv_dicts(RAW_VARIABLE_PATH)
    raw_gate_by_id = first_by(read_csv_dicts(RAW_INTAKE_GATE_PATH), "idno")
    climate_by_id = first_by(read_csv_dicts(CLIMATE_PREFLIGHT_PATH), "idno")
    concept_rows = build_concept_rows(waves, raw_files, raw_variables)
    variable_rows = build_variable_rows(waves, raw_files, raw_variables)
    requirement_rows = build_requirement_rows(waves, concept_rows, raw_gate_by_id, climate_by_id)
    requirement_rows = preserve_fill_values(
        requirement_rows,
        REQUIREMENT_CHECKLIST_PATH,
        ["idno", "requirement_id"],
        [
            "fill_evidence_file_or_module",
            "fill_raw_variables_used",
            "fill_value_label_pass",
            "fill_unit_or_recall_pass",
            "fill_merge_key_or_level_pass",
            "fill_missing_skip_pattern_pass",
            "fill_promote_requirement",
            "review_notes",
        ],
    )
    concept_rows = preserve_fill_values(
        concept_rows,
        CONCEPT_TEMPLATE_PATH,
        ["idno", "concept"],
        [
            "fill_raw_file_used",
            "fill_raw_variable_used",
            "fill_value_label_pass",
            "fill_unit_or_recall_pass",
            "fill_merge_key_pass",
            "fill_sample_level_pass",
            "fill_missing_code_pass",
            "fill_promote_to_harmonization_recipe",
            "review_notes",
        ],
    )
    variable_rows = preserve_fill_values(
        variable_rows,
        VARIABLE_TEMPLATE_PATH,
        ["idno", "concept", "candidate_files", "candidate_raw_variable", "candidate_harmonized_variables"],
        [
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
        ],
    )
    dataset_rows = build_dataset_rows(waves, concept_rows, variable_rows, requirement_rows, raw_files, raw_variables, climate_by_id)
    summary = build_summary(dataset_rows, requirement_rows, concept_rows, variable_rows)
    write_csv(DATASET_GATE_PATH, dataset_rows, DATASET_COLUMNS)
    write_csv(REQUIREMENT_CHECKLIST_PATH, requirement_rows, REQUIREMENT_COLUMNS)
    write_csv(CONCEPT_TEMPLATE_PATH, concept_rows, CONCEPT_COLUMNS)
    write_csv(VARIABLE_TEMPLATE_PATH, variable_rows, VARIABLE_COLUMNS)
    write_csv(SUMMARY_PATH, summary, SUMMARY_COLUMNS)
    write_report(dataset_rows, requirement_rows, concept_rows, variable_rows, summary)
    append_log(
        TEMP_DIR / "audit_log.md",
        f"Built priority raw verification workbook dataset_rows={len(dataset_rows)} requirement_rows={len(requirement_rows)} concept_rows={len(concept_rows)} variable_rows={len(variable_rows)}.",
    )
    print(
        "Priority raw verification workbook "
        f"dataset_rows={len(dataset_rows)} requirement_rows={len(requirement_rows)} "
        f"concept_rows={len(concept_rows)} variable_rows={len(variable_rows)}."
    )


if __name__ == "__main__":
    main()
