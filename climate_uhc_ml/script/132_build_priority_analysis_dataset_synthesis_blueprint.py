from __future__ import annotations

import csv
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from common import PROJECT_ROOT, REPORT_DIR, RESULT_DIR, TEMP_DIR, append_log, ensure_dirs, write_csv


WAVE_PLAN_PATH = RESULT_DIR / "priority_promotion_acquisition_wave_plan.csv"
VARIABLE_TEMPLATE_PATH = TEMP_DIR / "priority_variable_verification_template.csv"
CONCEPT_AUDIT_PATH = TEMP_DIR / "priority_manual_concept_decision_audit.csv"
VARIABLE_AUDIT_PATH = TEMP_DIR / "priority_manual_variable_decision_audit.csv"
RECEIPT_LEDGER_PATH = TEMP_DIR / "priority_raw_package_receipt_ledger.csv"
CLIMATE_PREFLIGHT_PATH = TEMP_DIR / "priority_climate_linkage_preflight.csv"
PROMOTED_REGISTRY_PATH = RESULT_DIR / "promoted_country_wave_registry.csv"
MWI2004_CHIRPS_ROUTE_SUMMARY_PATH = RESULT_DIR / "mwi2004_chirps_admin2_route_policy_summary.csv"
MWI2004_CHIRPS_EXTRACTION_SUMMARY_PATH = RESULT_DIR / "mwi2004_chirps_admin2_extraction_summary.csv"

BLUEPRINT_PATH = TEMP_DIR / "priority_analysis_dataset_synthesis_blueprint.csv"
JOIN_PLAN_PATH = TEMP_DIR / "priority_analysis_dataset_join_plan.csv"
SUMMARY_PATH = RESULT_DIR / "priority_analysis_dataset_synthesis_blueprint_summary.csv"
REPORT_PATH = REPORT_DIR / "priority_analysis_dataset_synthesis_blueprint.md"

RAW_ROOT = TEMP_DIR / "raw_downloads"

BLUEPRINT_COLUMNS = [
    "acquisition_batch_rank",
    "batch_role",
    "country",
    "wave",
    "idno",
    "promoted_dataset_layer",
    "output_column",
    "output_role",
    "required_for_final_dataset",
    "source_concepts",
    "expected_level",
    "derivation_type",
    "candidate_variable_rows",
    "high_confidence_candidate_rows",
    "candidate_files",
    "candidate_raw_variables",
    "manual_verified_variable_rows",
    "concept_manual_statuses",
    "raw_receipt_status",
    "climate_linkage_gate_status",
    "registry_analysis_ready_status",
    "current_synthesis_status",
    "blocking_reason",
    "post_raw_synthesis_action",
]

JOIN_COLUMNS = [
    "acquisition_batch_rank",
    "batch_role",
    "country",
    "wave",
    "idno",
    "base_household_key_status",
    "financial_inputs_status",
    "access_inputs_status",
    "survey_design_status",
    "timing_status",
    "climate_geography_status",
    "climate_route_status",
    "required_schema_columns",
    "synthesis_ready_columns",
    "blocked_columns",
    "join_plan_status",
    "next_action",
    "handoff_readme",
]

SUMMARY_COLUMNS = ["metric", "value", "interpretation"]


SCHEMA_SPECS = [
    ("household_core", "country", "metadata", "yes", "metadata", "dataset", "metadata_constant"),
    ("household_core", "wave", "metadata", "yes", "metadata", "dataset", "metadata_constant"),
    ("household_core", "idno", "metadata", "yes", "metadata", "dataset", "metadata_constant"),
    ("household_core", "household_id", "base_key", "yes", "household_id", "household", "raw_variable"),
    ("survey_design", "survey_weight", "weight", "yes", "survey_weight", "household_or_person", "raw_variable"),
    ("survey_design", "psu_cluster", "design_key", "yes", "psu_cluster", "cluster", "raw_variable"),
    ("survey_design", "strata", "design_key", "recommended", "strata", "strata", "raw_variable"),
    ("timing", "survey_year", "time_key", "yes", "survey_timing", "household", "raw_variable"),
    ("timing", "survey_month", "time_key", "yes", "survey_timing", "household", "raw_variable"),
    ("timing", "interview_date", "time_key", "recommended", "survey_timing", "household", "raw_variable"),
    ("climate_geography", "admin1", "geo_key", "recommended", "climate_geography", "cluster_or_admin", "raw_variable"),
    ("climate_geography", "admin2", "geo_key", "recommended", "climate_geography", "cluster_or_admin", "raw_variable"),
    ("climate_geography", "cluster_id", "geo_key", "yes", "climate_geography", "cluster_or_admin", "raw_variable"),
    ("climate_geography", "latitude", "geo_key", "recommended", "climate_geography", "cluster_or_admin", "raw_variable"),
    ("climate_geography", "longitude", "geo_key", "recommended", "climate_geography", "cluster_or_admin", "raw_variable"),
    ("climate_geography", "geolocation_quality", "geo_qc", "yes", "climate_geography", "cluster_or_admin", "raw_variable"),
    ("climate_geography", "rural", "geo_covariate", "recommended", "climate_geography", "household_or_cluster", "raw_variable"),
    ("financial_inputs", "total_consumption", "financial_denominator", "yes", "total_consumption_or_income", "household", "raw_variable"),
    ("financial_inputs", "total_income", "financial_denominator", "recommended", "total_consumption_or_income", "household", "raw_variable"),
    ("financial_inputs", "food_consumption", "financial_denominator_component", "recommended", "total_consumption_or_income", "household", "raw_variable"),
    ("financial_inputs", "nonfood_consumption", "financial_denominator_component", "recommended", "total_consumption_or_income", "household", "raw_variable"),
    ("financial_inputs", "oop_health_expenditure", "financial_numerator", "yes", "oop_health_expenditure", "household_or_person", "raw_variable"),
    ("financial_outcomes", "che10", "derived_outcome", "yes", "oop_health_expenditure;total_consumption_or_income", "household", "derived_from_verified_inputs"),
    ("financial_outcomes", "che25", "derived_outcome", "yes", "oop_health_expenditure;total_consumption_or_income", "household", "derived_from_verified_inputs"),
    ("financial_outcomes", "sdg382_indicator", "derived_outcome", "yes", "oop_health_expenditure;total_consumption_or_income", "household", "derived_from_verified_inputs"),
    ("access_inputs", "illness_or_injury_need", "need_denominator", "yes", "health_need", "person_or_household", "raw_variable"),
    ("access_inputs", "care_sought", "care_access", "yes", "care_or_barrier", "person_or_household", "raw_variable"),
    ("access_inputs", "care_not_sought", "care_access", "recommended", "care_or_barrier", "person_or_household", "raw_variable"),
    ("access_inputs", "care_not_sought_reason", "care_barrier", "recommended", "care_or_barrier", "person_or_household", "raw_variable"),
    ("access_inputs", "health_facility_distance", "care_barrier", "recommended", "care_or_barrier", "person_or_household", "raw_variable"),
    ("access_outcomes", "forgone_care_access_failure", "derived_outcome", "yes", "health_need;care_or_barrier", "person_or_household", "derived_from_verified_inputs"),
    ("access_outcomes", "double_failure_indicator", "derived_outcome", "yes", "oop_health_expenditure;total_consumption_or_income;health_need;care_or_barrier", "household", "derived_from_verified_inputs"),
    ("climate_linked", "climate_source", "climate_metadata", "yes", "survey_timing;climate_geography", "household_or_cluster", "derived_from_verified_linkage"),
    ("climate_linked", "climate_window_start", "climate_window", "yes", "survey_timing", "household_or_cluster", "derived_from_verified_timing"),
    ("climate_linked", "climate_window_end", "climate_window", "yes", "survey_timing", "household_or_cluster", "derived_from_verified_timing"),
    ("climate_linked", "chirps_precip_anomaly", "climate_exposure", "yes", "survey_timing;climate_geography", "household_or_cluster", "derived_from_chirps"),
    ("climate_linked", "era5_heat_anomaly", "climate_exposure", "yes", "survey_timing;climate_geography", "household_or_cluster", "derived_from_era5"),
    ("climate_linked", "climate_shock_indicator", "climate_exposure", "yes", "survey_timing;climate_geography", "household_or_cluster", "derived_from_chirps_or_era5"),
    ("covariates", "age", "demographic_covariate", "recommended", "demographics", "person_or_household", "raw_variable"),
    ("covariates", "sex", "demographic_covariate", "recommended", "demographics", "person_or_household", "raw_variable"),
    ("covariates", "education", "socioeconomic_covariate", "optional", "demographics", "person_or_household", "raw_variable"),
    ("covariates", "insurance", "coverage_covariate", "optional", "insurance", "person_or_household", "raw_variable"),
    ("mechanisms", "shock_module_variable", "mechanism_covariate", "optional", "shocks_or_livelihood", "household", "raw_variable"),
    ("mechanisms", "agriculture_livelihood", "mechanism_covariate", "optional", "shocks_or_livelihood", "household", "raw_variable"),
]


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


def csv_value(rows: list[dict[str, str]], metric: str, default: str = "") -> str:
    for row in rows:
        if clean(row.get("metric")) == metric:
            return clean(row.get("value")) or default
    return default


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(PROJECT_ROOT)).replace("\\", "/")
    except ValueError:
        return str(path).replace("\\", "/")


def split_values(value: str) -> list[str]:
    out: list[str] = []
    seen: set[str] = set()
    for item in clean(value).replace(",", ";").split(";"):
        token = clean(item)
        if token and token not in seen:
            out.append(token)
            seen.add(token)
    return out


def compact(values: list[str], limit: int = 12) -> str:
    out: list[str] = []
    seen: set[str] = set()
    for value in values:
        item = " ".join(clean(value).split())
        if item and item not in seen:
            out.append(item)
            seen.add(item)
        if len(out) >= limit:
            break
    return "; ".join(out)


def first_by(rows: list[dict[str, str]], field: str) -> dict[str, dict[str, str]]:
    out: dict[str, dict[str, str]] = {}
    for row in rows:
        key = clean(row.get(field))
        if key and key not in out:
            out[key] = row
    return out


def group(rows: list[dict[str, str]], field: str) -> dict[str, list[dict[str, str]]]:
    out: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        key = clean(row.get(field))
        if key:
            out[key].append(row)
    return out


def target_folder_path(folder: str, idno: str) -> Path:
    folder_clean = clean(folder).replace("\\", "/").strip("/")
    if folder_clean.startswith("temp/raw_downloads/"):
        return PROJECT_ROOT / folder_clean
    if folder_clean:
        return RAW_ROOT / folder_clean
    return RAW_ROOT / idno


def variable_item_id(row: dict[str, str]) -> str:
    return f"{clean(row.get('concept'))}:{clean(row.get('candidate_files'))}:{clean(row.get('candidate_raw_variable'))}"


def candidate_rows_for(
    rows: list[dict[str, str]],
    source_concepts: list[str],
    output_column: str,
    derivation_type: str,
) -> list[dict[str, str]]:
    if source_concepts == ["metadata"]:
        return []
    matches = []
    for row in rows:
        concept = clean(row.get("concept"))
        if concept not in source_concepts:
            continue
        hvars = split_values(row.get("candidate_harmonized_variables", ""))
        if derivation_type.startswith("derived_") or output_column in hvars or concept == output_column:
            matches.append(row)
    return matches


def concept_statuses(source_concepts: list[str], concept_audits: dict[str, dict[str, str]]) -> str:
    if source_concepts == ["metadata"]:
        return "metadata_constant"
    statuses = []
    for concept in source_concepts:
        row = concept_audits.get(concept, {})
        statuses.append(f"{concept}:{row.get('manual_decision_status', 'missing_concept_audit')}")
    return "; ".join(statuses)


def synthesis_status(
    required: str,
    derivation_type: str,
    candidate_count: int,
    verified_count: int,
    raw_receipt_status: str,
    climate_gate: str,
    analysis_ready_status: str,
) -> tuple[str, str]:
    if derivation_type == "metadata_constant":
        return "metadata_ready_not_sufficient_for_promotion", "metadata constants exist but source raw dataset is not promoted"
    if analysis_ready_status.startswith("promoted"):
        return "already_promoted", ""
    if raw_receipt_status == "not_received_no_original_raw_package":
        return "blocked_raw_package_absent", "complete original raw package absent"
    if candidate_count == 0:
        return "blocked_no_metadata_candidate", "no metadata candidate variable found for this output column"
    if derivation_type.startswith("derived_from_chirps") or derivation_type.startswith("derived_from_era5") or derivation_type == "derived_from_verified_linkage":
        if (
            "blocked" in climate_gate
            or "not_verified" in climate_gate
            or "not_accepted" in climate_gate
            or "extraction_validation" in climate_gate
            or "pending" in climate_gate
        ):
            return "blocked_climate_linkage_not_ready", "raw timing/geography, accepted CHIRPS/ERA5 route, extraction, and validation not complete"
    if verified_count == 0:
        return "blocked_manual_variable_verification_missing", "candidate raw variables have not passed manual value/unit/key verification"
    if required == "yes":
        return "ready_for_required_column_synthesis_review", ""
    return "ready_for_optional_column_synthesis_review", ""


def action_for(status: str) -> str:
    if status == "blocked_raw_package_absent":
        return "Place complete unchanged official raw package and documentation, then rerun receipt, schema, archive, and manual verification gates."
    if status == "blocked_no_metadata_candidate":
        return "Search full metadata inventory and questionnaire/codebook for a defensible source variable or document non-availability."
    if status == "blocked_climate_linkage_not_ready":
        return "Verify timing/geography raw values, geolocation quality, and accepted CHIRPS/ERA5 route before climate exposure construction."
    if status == "blocked_manual_variable_verification_missing":
        return "Complete manual label, value distribution, missing-code, unit/recall, merge-key, and promotion checks for candidate variables."
    if status.startswith("metadata_ready"):
        return "Carry metadata constants only after the country-wave is promoted."
    return "Build or review the promoted dataset column from verified inputs and record lineage."


def write_handoff(row: dict[str, str], blocked_examples: list[dict[str, str]]) -> str:
    folder = target_folder_path(row.get("local_target_folder", ""), row.get("idno", ""))
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / "_PRIORITY_ANALYSIS_DATASET_SYNTHESIS_BLUEPRINT.md"
    lines = [
        "# Priority Analysis Dataset Synthesis Blueprint",
        "",
        f"Dataset: {row.get('idno', '')} - {row.get('country', '')} {row.get('wave', '')}",
        "",
        f"Join plan status: {row.get('join_plan_status', '')}",
        "",
        "Current synthesis evidence:",
        "",
        f"- Required schema columns: {row.get('required_schema_columns', '0')}",
        f"- Synthesis-ready columns: {row.get('synthesis_ready_columns', '0')}",
        f"- Blocked columns: {row.get('blocked_columns', '0')}",
        f"- Base household key: {row.get('base_household_key_status', '')}",
        f"- Financial inputs: {row.get('financial_inputs_status', '')}",
        f"- Access inputs: {row.get('access_inputs_status', '')}",
        f"- Climate route: {row.get('climate_route_status', '')}",
        "",
        "Blocked column examples:",
        "",
    ]
    if blocked_examples:
        for item in blocked_examples[:25]:
            lines.append(f"- {item.get('output_column', '')}: {item.get('current_synthesis_status', '')} ({item.get('blocking_reason', '')})")
    else:
        lines.append("- None")
    lines.extend(
        [
            "",
            f"Next action: {row.get('next_action', '')}",
            "",
            "Stop rule: do not write this wave into `data/` until all required schema columns are source-verified, outcome-ready, and climate-linkage-ready.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")
    return rel(path)


def build_outputs() -> tuple[list[dict[str, str]], list[dict[str, str]], list[dict[str, str]]]:
    waves = read_csv_dicts(WAVE_PLAN_PATH)
    vars_by_id = group(read_csv_dicts(VARIABLE_TEMPLATE_PATH), "idno")
    concept_audits_by_id = {
        idno: {clean(row.get("item_id")): row for row in rows}
        for idno, rows in group(read_csv_dicts(CONCEPT_AUDIT_PATH), "idno").items()
    }
    variable_audits_by_item = {
        (clean(row.get("idno")), clean(row.get("item_id"))): row
        for row in read_csv_dicts(VARIABLE_AUDIT_PATH)
    }
    receipt_by_id = first_by(read_csv_dicts(RECEIPT_LEDGER_PATH), "idno")
    climate_by_id = first_by(read_csv_dicts(CLIMATE_PREFLIGHT_PATH), "idno")
    registry_by_id = first_by(read_csv_dicts(PROMOTED_REGISTRY_PATH), "idno")
    mwi2004_route_summary = read_csv_dicts(MWI2004_CHIRPS_ROUTE_SUMMARY_PATH)
    mwi2004_extraction_summary = read_csv_dicts(MWI2004_CHIRPS_EXTRACTION_SUMMARY_PATH)
    mwi2004_route_design_ready = csv_value(mwi2004_route_summary, "route_design_ready", "0") == "1"
    mwi2004_extraction_validated = csv_value(mwi2004_extraction_summary, "accepted_chirps_era5_route", "0") == "1"
    mwi2004_route_gate = csv_value(
        mwi2004_route_summary,
        "current_climate_linkage_gate_status",
        "route_preflight_ready_needs_extraction_validation",
    )
    mwi2004_extraction_gate = csv_value(
        mwi2004_extraction_summary,
        "current_climate_linkage_gate_status",
        "accepted_chirps_admin2_extraction_validated",
    )

    blueprint_rows: list[dict[str, str]] = []
    join_rows: list[dict[str, str]] = []

    for wave in waves:
        idno = clean(wave.get("idno"))
        receipt = receipt_by_id.get(idno, {})
        raw_receipt_status = receipt.get("receipt_status", "receipt_ledger_missing")
        climate_gate = climate_by_id.get(idno, {}).get("current_climate_linkage_gate_status", "missing_climate_preflight")
        if idno == "MWI_2004_IHS-II_v01_M" and mwi2004_extraction_validated:
            climate_gate = mwi2004_extraction_gate
        elif idno == "MWI_2004_IHS-II_v01_M" and mwi2004_route_design_ready:
            climate_gate = mwi2004_route_gate
        analysis_ready = registry_by_id.get(idno, {}).get("analysis_ready_status", "not_in_registry")
        concept_audits = concept_audits_by_id.get(idno, {})
        variable_rows = vars_by_id.get(idno, [])
        per_wave_blueprint: list[dict[str, str]] = []

        for layer, output_col, output_role, required, concepts_text, expected_level, derivation_type in SCHEMA_SPECS:
            concepts = split_values(concepts_text)
            candidates = candidate_rows_for(variable_rows, concepts, output_col, derivation_type)
            high_candidates = [row for row in candidates if clean(row.get("metadata_confidence")).lower() == "high"]
            verified = [
                row for row in candidates
                if variable_audits_by_item.get((idno, variable_item_id(row)), {}).get("manual_decision_status") == "manual_verified"
            ]
            status, blocker = synthesis_status(
                required,
                derivation_type,
                len(candidates),
                len(verified),
                raw_receipt_status,
                climate_gate,
                analysis_ready,
            )
            out = {
                "acquisition_batch_rank": wave.get("acquisition_batch_rank", ""),
                "batch_role": wave.get("batch_role", ""),
                "country": wave.get("country", ""),
                "wave": wave.get("wave", ""),
                "idno": idno,
                "promoted_dataset_layer": layer,
                "output_column": output_col,
                "output_role": output_role,
                "required_for_final_dataset": required,
                "source_concepts": concepts_text,
                "expected_level": expected_level,
                "derivation_type": derivation_type,
                "candidate_variable_rows": str(len(candidates)),
                "high_confidence_candidate_rows": str(len(high_candidates)),
                "candidate_files": compact([row.get("candidate_files", "") for row in candidates], limit=15),
                "candidate_raw_variables": compact([row.get("candidate_raw_variable", "") for row in candidates], limit=20),
                "manual_verified_variable_rows": str(len(verified)),
                "concept_manual_statuses": concept_statuses(concepts, concept_audits),
                "raw_receipt_status": raw_receipt_status,
                "climate_linkage_gate_status": climate_gate,
                "registry_analysis_ready_status": analysis_ready,
                "current_synthesis_status": status,
                "blocking_reason": blocker,
                "post_raw_synthesis_action": action_for(status),
            }
            blueprint_rows.append(out)
            per_wave_blueprint.append(out)

        required_rows = [row for row in per_wave_blueprint if row["required_for_final_dataset"] == "yes"]
        ready_rows = [row for row in required_rows if row["current_synthesis_status"].startswith("ready_for")]
        blocked_rows = [row for row in required_rows if row["current_synthesis_status"].startswith("blocked")]
        status_by_column = {row["output_column"]: row["current_synthesis_status"] for row in per_wave_blueprint}
        join_status = "ready_for_promoted_dataset_build" if required_rows and len(ready_rows) == len(required_rows) else "blocked_required_schema_columns_not_verified"
        join = {
            "acquisition_batch_rank": wave.get("acquisition_batch_rank", ""),
            "batch_role": wave.get("batch_role", ""),
            "country": wave.get("country", ""),
            "wave": wave.get("wave", ""),
            "idno": idno,
            "base_household_key_status": status_by_column.get("household_id", "missing"),
            "financial_inputs_status": "ready" if all(status_by_column.get(col, "").startswith("ready_for") for col in ["total_consumption", "oop_health_expenditure"]) else "blocked",
            "access_inputs_status": "ready" if all(status_by_column.get(col, "").startswith("ready_for") for col in ["illness_or_injury_need", "care_sought"]) else "blocked",
            "survey_design_status": "ready" if all(status_by_column.get(col, "").startswith("ready_for") for col in ["survey_weight", "psu_cluster"]) else "blocked",
            "timing_status": "ready" if all(status_by_column.get(col, "").startswith("ready_for") for col in ["survey_year", "survey_month"]) else "blocked",
            "climate_geography_status": "ready" if all(status_by_column.get(col, "").startswith("ready_for") for col in ["cluster_id", "geolocation_quality"]) else "blocked",
            "climate_route_status": climate_gate,
            "required_schema_columns": str(len(required_rows)),
            "synthesis_ready_columns": str(len(ready_rows)),
            "blocked_columns": str(len(blocked_rows)),
            "join_plan_status": join_status,
            "next_action": "Complete raw package receipt and manual verification for blocked required schema columns before writing any promoted household-climate dataset.",
            "handoff_readme": "",
        }
        join["handoff_readme"] = write_handoff(join | {"local_target_folder": wave.get("local_target_folder", "")}, blocked_rows)
        join_rows.append(join)

    return blueprint_rows, join_rows, build_summary(blueprint_rows, join_rows)


def build_summary(blueprint_rows: list[dict[str, str]], join_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    status_counts = Counter(row["current_synthesis_status"] for row in blueprint_rows)
    required_rows = [row for row in blueprint_rows if row["required_for_final_dataset"] == "yes"]
    ready_required = [row for row in required_rows if row["current_synthesis_status"].startswith("ready_for")]
    join_counts = Counter(row["join_plan_status"] for row in join_rows)
    rows = [
        {"metric": "priority_synthesis_blueprint_schema_rows", "value": str(len(blueprint_rows)), "interpretation": "Target output-column rows for priority analysis dataset synthesis."},
        {"metric": "priority_synthesis_blueprint_required_rows", "value": str(len(required_rows)), "interpretation": "Required output columns across priority and backup waves."},
        {"metric": "priority_synthesis_blueprint_ready_required_rows", "value": str(len(ready_required)), "interpretation": "Required output columns ready for synthesis review."},
        {"metric": "priority_synthesis_blueprint_blocked_required_rows", "value": str(len(required_rows) - len(ready_required)), "interpretation": "Required output columns still blocked."},
        {"metric": "priority_synthesis_blueprint_join_plan_rows", "value": str(len(join_rows)), "interpretation": "Dataset-level join plans."},
        {"metric": "priority_synthesis_blueprint_join_ready_rows", "value": str(join_counts.get("ready_for_promoted_dataset_build", 0)), "interpretation": "Dataset-level join plans ready for promoted dataset build."},
        {"metric": "priority_synthesis_blueprint_candidate_variable_rows", "value": str(sum(safe_int(row.get("candidate_variable_rows")) for row in blueprint_rows)), "interpretation": "Metadata candidate variable rows connected to target output columns."},
        {"metric": "priority_synthesis_blueprint_manual_verified_variable_rows", "value": str(sum(safe_int(row.get("manual_verified_variable_rows")) for row in blueprint_rows)), "interpretation": "Candidate variable rows passing manual verification."},
        {"metric": "priority_synthesis_blueprint_handoff_readmes_written", "value": str(sum(1 for row in join_rows if row.get("handoff_readme"))), "interpretation": "Per-wave synthesis blueprint handoffs written."},
        {"metric": "modeling_gate_status", "value": "blocked", "interpretation": "Models remain blocked until promoted registry thresholds and accepted CHIRPS/ERA5 linkage pass."},
    ]
    for status, count in sorted(status_counts.items()):
        rows.append({"metric": f"priority_synthesis_status_{status}", "value": str(count), "interpretation": "Output-column synthesis status count."})
    for status, count in sorted(join_counts.items()):
        rows.append({"metric": f"priority_synthesis_join_status_{status}", "value": str(count), "interpretation": "Dataset-level join status count."})
    return rows


def markdown_table(rows: list[dict[str, str]], columns: list[str], limit: int = 25) -> str:
    lines = ["| " + " | ".join(columns) + " |", "|" + "|".join("---" for _ in columns) + "|"]
    for row in rows[:limit]:
        values = []
        for column in columns:
            value = clean(row.get(column)).replace("|", "/")
            if len(value) > 120:
                value = value[:117] + "..."
            values.append(value)
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines)


def write_report(blueprint_rows: list[dict[str, str]], join_rows: list[dict[str, str]], summary: list[dict[str, str]]) -> None:
    summary_table = "\n".join(f"| {row['metric']} | {row['value']} | {row['interpretation']} |" for row in summary)
    REPORT_PATH.write_text(
        f"""# Priority Analysis Dataset Synthesis Blueprint

Status: fail-closed promoted-dataset synthesis blueprint. This defines the
target household x climate schema and join plan, but does not write `data/`.

## Summary

| Metric | Value | Interpretation |
|---|---:|---|
{summary_table}

## Join Plans

{markdown_table(join_rows, ['acquisition_batch_rank', 'idno', 'country', 'wave', 'required_schema_columns', 'synthesis_ready_columns', 'blocked_columns', 'join_plan_status'], 20)}

## Required Schema Examples

{markdown_table([row for row in blueprint_rows if row['required_for_final_dataset'] == 'yes'], ['idno', 'promoted_dataset_layer', 'output_column', 'source_concepts', 'candidate_variable_rows', 'manual_verified_variable_rows', 'current_synthesis_status'], 30)}

## Rule

A country-wave may be written to `data/` only after every required schema
column has raw package receipt, source variable verification, manual
value/unit/key review, outcome readiness, and accepted CHIRPS/ERA5 climate
linkage. Metadata-only candidates remain blocked.

## Machine-Readable Outputs

- `temp/priority_analysis_dataset_synthesis_blueprint.csv`
- `temp/priority_analysis_dataset_join_plan.csv`
- `result/priority_analysis_dataset_synthesis_blueprint_summary.csv`
""",
        encoding="utf-8",
    )


def main() -> None:
    ensure_dirs()
    blueprint_rows, join_rows, summary = build_outputs()
    write_csv(BLUEPRINT_PATH, blueprint_rows, BLUEPRINT_COLUMNS)
    write_csv(JOIN_PLAN_PATH, join_rows, JOIN_COLUMNS)
    write_csv(SUMMARY_PATH, summary, SUMMARY_COLUMNS)
    write_report(blueprint_rows, join_rows, summary)
    append_log(
        TEMP_DIR / "audit_log.md",
        f"Built priority analysis dataset synthesis blueprint schema_rows={len(blueprint_rows)} join_rows={len(join_rows)}.",
    )
    print(f"Priority analysis dataset synthesis blueprint schema_rows={len(blueprint_rows)} join_rows={len(join_rows)}.")


if __name__ == "__main__":
    main()
