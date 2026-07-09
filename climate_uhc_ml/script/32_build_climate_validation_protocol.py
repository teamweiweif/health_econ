from __future__ import annotations

import csv
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from common import REPORT_DIR, RESULT_DIR, TEMP_DIR, append_log, ensure_dirs, write_csv


BUNDLES_PATH = TEMP_DIR / "minimum_viable_download_bundles.csv"
CLIMATE_PLAN_PATH = TEMP_DIR / "climate_exposure_plan.csv"
SPEC_PATH = RESULT_DIR / "climate_exposure_specification.csv"
SOURCE_PROBE_PATH = TEMP_DIR / "climate_source_probe.csv"
CONCEPT_PATH = TEMP_DIR / "raw_ingestion_concept_checklist.csv"
RAW_VARIABLE_PATH = TEMP_DIR / "raw_schema_inventory" / "raw_variable_catalog.csv"

REQUIREMENTS_PATH = TEMP_DIR / "climate_linkage_requirements.csv"
SOURCE_MATRIX_PATH = RESULT_DIR / "climate_source_method_matrix.csv"
VALIDATION_PROTOCOL_PATH = RESULT_DIR / "climate_exposure_validation_protocol.csv"
READINESS_PATH = RESULT_DIR / "climate_linkage_readiness.csv"
SUMMARY_PATH = RESULT_DIR / "climate_validation_protocol_summary.csv"
REPORT_PATH = REPORT_DIR / "climate_validation_protocol.md"

REQUIREMENT_COLUMNS = [
    "bundle_rank",
    "country",
    "survey_name",
    "wave",
    "idno",
    "requirement_component",
    "required_evidence",
    "raw_concepts_required",
    "metadata_support_status",
    "raw_verification_status",
    "source_roles_required",
    "source_status",
    "current_gate_status",
    "blocking_gap",
    "planned_decision_rule",
]

SOURCE_COLUMNS = [
    "source_role",
    "source_name",
    "source_domain",
    "official_url",
    "probe_status",
    "saved_path",
    "intended_use",
    "unit_or_scale_guardrail",
    "current_limitation",
]

VALIDATION_COLUMNS = [
    "validation_check",
    "check_family",
    "primary_source",
    "comparison_source",
    "window_or_scale",
    "required_inputs",
    "pass_rule",
    "current_status",
    "blocking_gap",
]

READINESS_COLUMNS = [
    "bundle_rank",
    "country",
    "survey_name",
    "wave",
    "idno",
    "climate_plan_status",
    "requirement_rows",
    "metadata_supported_requirement_rows",
    "raw_verified_requirement_rows",
    "source_ready_requirement_rows",
    "blocked_requirement_rows",
    "readiness_status",
    "next_action",
]

SUMMARY_COLUMNS = ["metric", "value", "interpretation"]

REQUIREMENTS = [
    {
        "component": "survey_timing_for_lags",
        "concepts": ["survey_timing"],
        "sources": [],
        "required": "Interview date, or at minimum verified interview month/year or fieldwork period, must be available for lag windows.",
        "decision": "Use exact interview date where possible; otherwise month-level windows with explicit measurement-error flag.",
    },
    {
        "component": "geography_or_coordinates",
        "concepts": ["climate_geography"],
        "sources": [],
        "required": "Latitude/longitude, cluster ID, admin geography, or documented geospatial linkage key must be verified from raw files.",
        "decision": "Prefer verified cluster/household point; fall back to admin aggregation only with documented measurement error.",
    },
    {
        "component": "geolocation_quality_and_displacement",
        "concepts": ["climate_geography"],
        "sources": [],
        "required": "GPS displacement, suppression, accuracy, coordinate CRS, and admin resolution must be recorded before point extraction.",
        "decision": "If GPS is displaced or suppressed, use buffer/admin aggregation and downgrade exposure precision.",
    },
    {
        "component": "rainfall_primary_chirps",
        "concepts": ["survey_timing", "climate_geography"],
        "sources": ["primary_rainfall_documentation", "primary_rainfall_data_directory"],
        "required": "CHIRPS daily/global precipitation source and file-level units must be available for verified place-time windows.",
        "decision": "Use CHIRPS for rainfall totals, anomalies, drought, and extreme wet indicators after unit and coverage checks.",
    },
    {
        "component": "temperature_primary_era5_land",
        "concepts": ["survey_timing", "climate_geography"],
        "sources": ["primary_temperature_documentation", "primary_daily_temperature_documentation"],
        "required": "ERA5-Land temperature product, statistic, time zone/date handling, and Kelvin/Celsius conversion must be verified.",
        "decision": "Use ERA5-Land as primary temperature source; convert Kelvin to Celsius only after request metadata confirms units.",
    },
    {
        "component": "nasa_power_fallback_and_crosscheck",
        "concepts": ["survey_timing", "climate_geography"],
        "sources": ["rapid_point_fallback_documentation", "rapid_point_fallback_api"],
        "required": "NASA POWER point API parameters and response metadata must be recorded for precipitation/temperature cross-checks.",
        "decision": "Use NASA POWER for rapid point fallback and random subset validation, not as unexamined replacement for CHIRPS/ERA5.",
    },
    {
        "component": "water_balance_robustness",
        "concepts": ["survey_timing", "climate_geography"],
        "sources": ["water_balance_robustness_documentation", "water_balance_robustness_catalog", "drought_robustness_documentation"],
        "required": "TerraClimate and SPEI variables require monthly scale, unit, and baseline documentation before robustness use.",
        "decision": "Use TerraClimate/SPEI only for robustness after source-specific units/scales and temporal matching are documented.",
    },
    {
        "component": "historical_baseline_construction",
        "concepts": ["survey_timing", "climate_geography"],
        "sources": ["primary_rainfall_documentation", "primary_temperature_documentation"],
        "required": "Historical baseline period, local grid/cell/admin aggregation, and percentile/z-score rule must be pre-specified.",
        "decision": "Construct anomalies against a documented local historical baseline; do not estimate z-scores from survey-period data only.",
    },
    {
        "component": "exposure_window_construction",
        "concepts": ["survey_timing", "climate_geography"],
        "sources": [],
        "required": "1, 3, 6, and 12 month pre-interview windows must be traceable to exact or month-level survey timing.",
        "decision": "Apply lag windows before the interview date/month; never use post-interview climate in treatment windows.",
    },
    {
        "component": "spatial_qc_mapping",
        "concepts": ["climate_geography"],
        "sources": [],
        "required": "Points/admin units must be mapped over climate grids and checked for country bounds, missing coordinates, and duplicate locations.",
        "decision": "Exclude or admin-aggregate locations failing spatial plausibility checks and report exposure precision downgrade.",
    },
    {
        "component": "cross_source_validation",
        "concepts": ["survey_timing", "climate_geography"],
        "sources": ["rapid_point_fallback_api"],
        "required": "Random subset comparisons must be planned for CHIRPS vs NASA/ERA5 precipitation and ERA5 vs NASA temperature.",
        "decision": "Flag source disagreements before causal modeling; do not treat one source as truth without diagnostics.",
    },
]

VALIDATION_CHECKS = [
    {
        "check": "unit_check_chirps_precipitation",
        "family": "unit",
        "primary": "CHIRPS",
        "comparison": "source metadata",
        "window": "all rainfall windows",
        "inputs": "downloaded CHIRPS file metadata or API metadata; extracted rainfall values",
        "rule": "precipitation units documented as mm and nonnegative; impossible values flagged",
    },
    {
        "check": "unit_check_era5_temperature",
        "family": "unit",
        "primary": "ERA5-Land",
        "comparison": "request metadata/NASA POWER",
        "window": "all heat windows",
        "inputs": "ERA5 variable metadata; extracted temperature values",
        "rule": "Kelvin/Celsius conversion documented; plausible Celsius ranges after conversion",
    },
    {
        "check": "point_location_bounds_check",
        "family": "spatial",
        "primary": "survey coordinates/admin",
        "comparison": "country/admin boundaries",
        "window": "not applicable",
        "inputs": "raw-verified coordinates or admin IDs; country boundary/admin lookup",
        "rule": "points or centroids fall in expected country/admin unit, or are explicitly excluded/downgraded",
    },
    {
        "check": "gps_displacement_or_suppression_check",
        "family": "spatial",
        "primary": "survey geodata",
        "comparison": "survey documentation",
        "window": "not applicable",
        "inputs": "GPS quality/suppression/displacement fields and documentation",
        "rule": "displacement/suppression status recorded and exposure precision downgraded where needed",
    },
    {
        "check": "lag_window_no_post_treatment_check",
        "family": "timing",
        "primary": "survey timing",
        "comparison": "climate window dates",
        "window": "1m;3m;6m;12m",
        "inputs": "raw-verified interview date/month; generated climate window start/end dates",
        "rule": "all treatment windows end before or at interview timing rule; future climate reserved only for placebo",
    },
    {
        "check": "rainfall_cross_source_subset_check",
        "family": "cross_source",
        "primary": "CHIRPS",
        "comparison": "NASA POWER or ERA5 precipitation",
        "window": "1m;3m;6m;12m",
        "inputs": "random subset of verified points/admin units and dates",
        "rule": "correlation, mean difference, and extreme-disagreement flags reported before modeling",
    },
    {
        "check": "temperature_cross_source_subset_check",
        "family": "cross_source",
        "primary": "ERA5-Land",
        "comparison": "NASA POWER",
        "window": "1m;3m;6m;12m",
        "inputs": "random subset of verified points/admin units and dates",
        "rule": "correlation, mean difference, and heat-threshold disagreement flags reported before modeling",
    },
    {
        "check": "historical_baseline_not_survey_only_check",
        "family": "baseline",
        "primary": "CHIRPS/ERA5 historical series",
        "comparison": "pre-specified baseline years",
        "window": "anomaly/percentile windows",
        "inputs": "historical climate data preceding and spanning survey years",
        "rule": "z-scores/percentiles use documented historical baseline, not only survey observations",
    },
    {
        "check": "missingness_and_coverage_check",
        "family": "coverage",
        "primary": "all climate sources",
        "comparison": "country-wave sample",
        "window": "all windows",
        "inputs": "extracted exposure table and climate audit rows",
        "rule": "country-wave exposure missingness and source coverage reported before sample inclusion",
    },
]


def read_csv_dicts(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def safe_int(value: Any, default: int = 999999) -> int:
    try:
        return int(str(value).strip())
    except (TypeError, ValueError):
        return default


def concept_index(rows: list[dict[str, str]]) -> dict[tuple[str, str], dict[str, str]]:
    return {(row.get("idno", ""), row.get("concept", "")): row for row in rows if row.get("idno") and row.get("concept")}


def count_by_id(rows: list[dict[str, str]], id_field: str = "idno") -> Counter[str]:
    return Counter(row.get(id_field, "") for row in rows if row.get(id_field, ""))


def source_index(rows: list[dict[str, str]]) -> dict[str, list[dict[str, str]]]:
    out: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        role = row.get("source_role", "")
        if role:
            out[role].append(row)
    return out


def source_ready(role: str, by_role: dict[str, list[dict[str, str]]]) -> bool:
    return any(row.get("status") in {"reachable_snapshot_saved", "pass_api_parameters_present"} for row in by_role.get(role, []))


def source_status(roles: list[str], by_role: dict[str, list[dict[str, str]]]) -> str:
    if not roles:
        return "not_required"
    missing = [role for role in roles if not source_ready(role, by_role)]
    return "source_ready" if not missing else "source_missing:" + ";".join(missing)


def requirement_status(
    idno: str,
    req: dict[str, Any],
    concepts: dict[tuple[str, str], dict[str, str]],
    raw_counts: Counter[str],
    source_by_role: dict[str, list[dict[str, str]]],
) -> dict[str, str]:
    missing_metadata = []
    raw_verified = []
    for concept in req["concepts"]:
        row = concepts.get((idno, concept), {})
        if row.get("metadata_support_status") != "metadata_supported_raw_unverified":
            missing_metadata.append(concept)
        if row.get("raw_verification_status") == "raw_variables_inspected":
            raw_verified.append(concept)
    src_status = source_status(req["sources"], source_by_role)
    if missing_metadata:
        gate = "metadata_missing"
        gap = "missing metadata concept support: " + ";".join(missing_metadata)
    elif raw_counts[idno] == 0 or len(raw_verified) < len(req["concepts"]):
        gate = "metadata_ready_raw_unverified"
        gap = "raw timing/geography variables and values have not been inspected"
    elif src_status.startswith("source_missing"):
        gate = "source_missing"
        gap = src_status
    else:
        gate = "ready_for_climate_linkage_value_audit"
        gap = "still requires extracted values, maps, source comparisons, and missingness diagnostics"
    return {
        "metadata_support_status": "metadata_supported" if not missing_metadata else "metadata_incomplete",
        "raw_verification_status": "raw_verified" if req["concepts"] and len(raw_verified) == len(req["concepts"]) else "raw_not_verified",
        "source_status": src_status,
        "gate": gate,
        "gap": gap,
    }


def build_requirements(
    bundles: list[dict[str, str]],
    climate_plan: dict[str, dict[str, str]],
    concept_rows: list[dict[str, str]],
    source_rows: list[dict[str, str]],
    raw_variable_rows: list[dict[str, str]],
) -> list[dict[str, str]]:
    concepts = concept_index(concept_rows)
    raw_counts = count_by_id(raw_variable_rows, "idno")
    source_by_role = source_index(source_rows)
    rows = []
    for bundle in bundles:
        idno = bundle.get("idno", "")
        if not idno:
            continue
        for req in REQUIREMENTS:
            status = requirement_status(idno, req, concepts, raw_counts, source_by_role)
            rows.append(
                {
                    "bundle_rank": bundle.get("bundle_rank", ""),
                    "country": bundle.get("country", ""),
                    "survey_name": bundle.get("survey_name", ""),
                    "wave": bundle.get("wave", ""),
                    "idno": idno,
                    "requirement_component": req["component"],
                    "required_evidence": req["required"],
                    "raw_concepts_required": ";".join(req["concepts"]),
                    "metadata_support_status": status["metadata_support_status"],
                    "raw_verification_status": status["raw_verification_status"],
                    "source_roles_required": ";".join(req["sources"]),
                    "source_status": status["source_status"],
                    "current_gate_status": status["gate"],
                    "blocking_gap": status["gap"],
                    "planned_decision_rule": req["decision"] + f"; climate_plan_status={climate_plan.get(idno, {}).get('climate_linkage_gate_status', 'missing_climate_plan')}",
                }
            )
    return sorted(rows, key=lambda row: (safe_int(row["bundle_rank"]), row["requirement_component"]))


def build_source_matrix(source_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    domain_map = {
        "primary_rainfall": "rainfall",
        "primary_temperature": "temperature",
        "daily_temperature": "temperature",
        "rapid_point": "fallback",
        "water_balance": "water_balance",
        "drought": "drought",
    }
    out = []
    for row in source_rows:
        role = row.get("source_role", "")
        domain = "other"
        for key, value in domain_map.items():
            if key in role:
                domain = value
        out.append(
            {
                "source_role": role,
                "source_name": row.get("source_name", ""),
                "source_domain": domain,
                "official_url": row.get("official_url", ""),
                "probe_status": row.get("status", ""),
                "saved_path": row.get("saved_path", ""),
                "intended_use": row.get("expected_use", ""),
                "unit_or_scale_guardrail": row.get("unit_notes", ""),
                "current_limitation": "source probe only; no country-wave exposure values constructed",
            }
        )
    return out


def build_validation_protocol(spec_rows: list[dict[str, str]], requirement_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    blocked_requirements = sum(1 for row in requirement_rows if row.get("current_gate_status") != "ready_for_climate_linkage_value_audit")
    source_specs_ready = sum(1 for row in spec_rows if row.get("current_status") == "blocked_until_verified_geography_and_timing")
    rows = []
    for check in VALIDATION_CHECKS:
        if blocked_requirements:
            status = "blocked_until_verified_geography_and_timing"
            gap = "country-wave timing/geography remains raw-unverified"
        elif not source_specs_ready:
            status = "blocked_until_source_spec_ready"
            gap = "climate exposure specification source gates are not ready"
        else:
            status = "ready_for_extracted_value_validation"
            gap = "requires extracted exposure data and diagnostic outputs"
        rows.append(
            {
                "validation_check": check["check"],
                "check_family": check["family"],
                "primary_source": check["primary"],
                "comparison_source": check["comparison"],
                "window_or_scale": check["window"],
                "required_inputs": check["inputs"],
                "pass_rule": check["rule"],
                "current_status": status,
                "blocking_gap": gap,
            }
        )
    return rows


def build_readiness(requirement_rows: list[dict[str, str]], climate_plan_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    plan_by_id = {row.get("idno", ""): row for row in climate_plan_rows if row.get("idno")}
    for row in requirement_rows:
        grouped[row["idno"]].append(row)
    readiness = []
    for idno, rows in grouped.items():
        first = rows[0]
        metadata_supported = sum(1 for row in rows if row.get("metadata_support_status") == "metadata_supported")
        raw_verified = sum(1 for row in rows if row.get("raw_verification_status") == "raw_verified")
        source_ready_rows = sum(1 for row in rows if row.get("source_status") in {"source_ready", "not_required"})
        blocked = sum(1 for row in rows if row.get("current_gate_status") != "ready_for_climate_linkage_value_audit")
        if blocked:
            status = "blocked_until_raw_timing_geography_and_validation_inputs"
            next_action = "place raw files, inspect timing/geography variables, document geolocation quality, then extract pilot climate values"
        else:
            status = "ready_for_climate_linkage_value_audit"
            next_action = "construct climate_linkage_input and run extraction plus source/unit/spatial/timing diagnostics"
        readiness.append(
            {
                "bundle_rank": first.get("bundle_rank", ""),
                "country": first.get("country", ""),
                "survey_name": first.get("survey_name", ""),
                "wave": first.get("wave", ""),
                "idno": idno,
                "climate_plan_status": plan_by_id.get(idno, {}).get("climate_linkage_gate_status", "missing_climate_plan"),
                "requirement_rows": str(len(rows)),
                "metadata_supported_requirement_rows": str(metadata_supported),
                "raw_verified_requirement_rows": str(raw_verified),
                "source_ready_requirement_rows": str(source_ready_rows),
                "blocked_requirement_rows": str(blocked),
                "readiness_status": status,
                "next_action": next_action,
            }
        )
    return sorted(readiness, key=lambda row: safe_int(row["bundle_rank"]))


def build_summary(requirements: list[dict[str, str]], readiness: list[dict[str, str]], sources: list[dict[str, str]], validation: list[dict[str, str]]) -> list[dict[str, str]]:
    gate_counts = Counter(row.get("current_gate_status", "") for row in requirements)
    readiness_counts = Counter(row.get("readiness_status", "") for row in readiness)
    source_counts = Counter(row.get("probe_status", "") for row in sources)
    validation_counts = Counter(row.get("current_status", "") for row in validation)
    rows = [
        {"metric": "requirement_rows", "value": str(len(requirements)), "interpretation": "Country-wave climate linkage requirement rows."},
        {"metric": "country_wave_rows", "value": str(len(readiness)), "interpretation": "Priority bundle country-waves assessed."},
        {"metric": "source_matrix_rows", "value": str(len(sources)), "interpretation": "Climate source/method rows."},
        {"metric": "validation_protocol_rows", "value": str(len(validation)), "interpretation": "Climate exposure validation check rows."},
        {"metric": "ready_country_wave_rows", "value": str(sum(1 for row in readiness if row.get("readiness_status") == "ready_for_climate_linkage_value_audit")), "interpretation": "Country-waves ready for climate linkage value audit."},
        {"metric": "blocked_country_wave_rows", "value": str(sum(1 for row in readiness if row.get("readiness_status") != "ready_for_climate_linkage_value_audit")), "interpretation": "Country-waves blocked by raw timing/geography or validation inputs."},
    ]
    for gate, count in sorted(gate_counts.items()):
        rows.append({"metric": f"requirement_gate_{gate}", "value": str(count), "interpretation": "Requirement gate status count."})
    for status, count in sorted(readiness_counts.items()):
        rows.append({"metric": f"readiness_status_{status}", "value": str(count), "interpretation": "Country-wave readiness status count."})
    for status, count in sorted(source_counts.items()):
        rows.append({"metric": f"source_status_{status}", "value": str(count), "interpretation": "Climate source probe status count."})
    for status, count in sorted(validation_counts.items()):
        rows.append({"metric": f"validation_status_{status}", "value": str(count), "interpretation": "Validation protocol status count."})
    return rows


def markdown_count_table(counter: Counter[str], label: str) -> str:
    lines = [f"| {label} | Count |", "|---|---:|"]
    for key, count in counter.most_common():
        lines.append(f"| {key or 'blank'} | {count} |")
    return "\n".join(lines)


def markdown_table(rows: list[dict[str, str]], columns: list[str], limit: int = 12) -> str:
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


def write_report(requirements: list[dict[str, str]], sources: list[dict[str, str]], validation: list[dict[str, str]], readiness: list[dict[str, str]], summary: list[dict[str, str]]) -> None:
    gate_counts = Counter(row.get("current_gate_status", "") for row in requirements)
    readiness_counts = Counter(row.get("readiness_status", "") for row in readiness)
    validation_counts = Counter(row.get("current_status", "") for row in validation)
    source_counts = Counter(row.get("probe_status", "") for row in sources)
    summary_table = "\n".join(f"| {row['metric']} | {row['value']} | {row['interpretation']} |" for row in summary)
    REPORT_PATH.write_text(
        f"""# Climate Validation Protocol

Status: climate linkage and exposure validation are planned but blocked until raw survey timing and geography are verified. This report does not construct climate exposures.

## Purpose

This protocol converts Phase 5 climate requirements into fail-closed country-wave checks for timing, geolocation quality, source units, historical baselines, spatial plausibility, and cross-source validation.

## Counts

| Metric | Value | Interpretation |
|---|---:|---|
{summary_table}

## Requirement Gates

{markdown_count_table(gate_counts, 'Requirement gate status')}

## Country-Wave Readiness

{markdown_count_table(readiness_counts, 'Readiness status')}

{markdown_table(readiness, ['bundle_rank', 'country', 'wave', 'idno', 'blocked_requirement_rows', 'readiness_status'], 15)}

## Validation Checks

{markdown_count_table(validation_counts, 'Validation status')}

## Source Status

{markdown_count_table(source_counts, 'Source probe status')}

## Guardrails

- Do not extract climate values until raw timing and geography are verified.
- Do not use post-interview climate in treatment windows; future climate is only for placebo checks.
- Do not treat displaced or admin-only geography as exact household exposure.
- Do not use ERA5-Land temperature without documenting Kelvin/Celsius handling.
- Do not use CHIRPS, TerraClimate, SPEI, or NASA POWER without recording units/scales and extraction metadata.

## Outputs

- `temp/climate_linkage_requirements.csv`
- `result/climate_source_method_matrix.csv`
- `result/climate_exposure_validation_protocol.csv`
- `result/climate_linkage_readiness.csv`
- `result/climate_validation_protocol_summary.csv`
""",
        encoding="utf-8",
    )


def main() -> None:
    ensure_dirs()
    bundles = read_csv_dicts(BUNDLES_PATH)
    climate_plan_rows = read_csv_dicts(CLIMATE_PLAN_PATH)
    climate_plan = {row.get("idno", ""): row for row in climate_plan_rows if row.get("idno")}
    spec_rows = read_csv_dicts(SPEC_PATH)
    source_rows = read_csv_dicts(SOURCE_PROBE_PATH)
    concept_rows = read_csv_dicts(CONCEPT_PATH)
    raw_variable_rows = read_csv_dicts(RAW_VARIABLE_PATH)

    requirements = build_requirements(bundles, climate_plan, concept_rows, source_rows, raw_variable_rows)
    sources = build_source_matrix(source_rows)
    validation = build_validation_protocol(spec_rows, requirements)
    readiness = build_readiness(requirements, climate_plan_rows)
    summary = build_summary(requirements, readiness, sources, validation)

    write_csv(REQUIREMENTS_PATH, requirements, REQUIREMENT_COLUMNS)
    write_csv(SOURCE_MATRIX_PATH, sources, SOURCE_COLUMNS)
    write_csv(VALIDATION_PROTOCOL_PATH, validation, VALIDATION_COLUMNS)
    write_csv(READINESS_PATH, readiness, READINESS_COLUMNS)
    write_csv(SUMMARY_PATH, summary, SUMMARY_COLUMNS)
    write_report(requirements, sources, validation, readiness, summary)
    append_log(TEMP_DIR / "audit_log.md", f"Climate validation protocol requirement_rows={len(requirements)} country_wave_rows={len(readiness)} validation_rows={len(validation)}.")
    print(f"Climate validation protocol requirement_rows={len(requirements)} country_wave_rows={len(readiness)} validation_rows={len(validation)}.")


if __name__ == "__main__":
    main()
