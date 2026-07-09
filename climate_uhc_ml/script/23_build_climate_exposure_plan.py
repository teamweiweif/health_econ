from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path
from typing import Any

from common import REPORT_DIR, RESULT_DIR, TEMP_DIR, append_log, ensure_dirs, write_csv


PLAN_PATH = TEMP_DIR / "climate_exposure_plan.csv"
SPEC_PATH = RESULT_DIR / "climate_exposure_specification.csv"
SUMMARY_PATH = RESULT_DIR / "climate_exposure_plan_summary.csv"
REPORT_PATH = REPORT_DIR / "climate_exposure_plan.md"

WINDOWS = ["1m", "3m", "6m", "12m"]

PLAN_COLUMNS = [
    "quality_rank",
    "country",
    "survey_name",
    "wave",
    "idno",
    "timing_metadata_status",
    "geography_metadata_status",
    "timing_raw_verification_status",
    "geography_raw_verification_status",
    "candidate_timing_files",
    "candidate_geography_files",
    "planned_geography_level",
    "primary_rainfall_source",
    "primary_temperature_source",
    "fallback_source",
    "robustness_sources",
    "planned_windows",
    "planned_exposure_families",
    "climate_linkage_gate_status",
    "blocking_gap",
]

SPEC_COLUMNS = [
    "exposure_family",
    "exposure_name",
    "primary_source",
    "fallback_or_robustness_source",
    "window",
    "raw_source_variable_or_product",
    "unit_or_scale",
    "construction_rule",
    "minimum_inputs_required",
    "current_status",
]

SUMMARY_COLUMNS = ["metric", "value", "interpretation"]


def read_csv_dicts(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def clean(value: Any) -> str:
    return "" if value is None else str(value).strip()


def concept_by_idno(concept: str) -> dict[str, dict[str, str]]:
    rows = read_csv_dicts(TEMP_DIR / "raw_ingestion_concept_checklist.csv")
    return {row.get("idno", ""): row for row in rows if row.get("concept") == concept}


def source_ready(source_role: str) -> bool:
    rows = read_csv_dicts(TEMP_DIR / "climate_source_probe.csv")
    return any(row.get("source_role") == source_role and row.get("status") in {"reachable_snapshot_saved", "pass_api_parameters_present"} for row in rows)


def any_source_ready(roles: set[str]) -> bool:
    rows = read_csv_dicts(TEMP_DIR / "climate_source_probe.csv")
    return any(row.get("source_role") in roles and row.get("status") in {"reachable_snapshot_saved", "pass_api_parameters_present"} for row in rows)


def plan_rows() -> list[dict[str, str]]:
    priorities = read_csv_dicts(TEMP_DIR / "metadata_quality_download_priority.csv")
    timing = concept_by_idno("survey_timing")
    geography = concept_by_idno("climate_geography")
    rows = []
    for priority in priorities:
        idno = priority.get("idno", "")
        timing_row = timing.get(idno, {})
        geo_row = geography.get(idno, {})
        timing_supported = timing_row.get("metadata_support_status") == "metadata_supported_raw_unverified"
        geo_supported = geo_row.get("metadata_support_status") == "metadata_supported_raw_unverified"
        timing_raw = timing_row.get("raw_verification_status", "raw_not_inspected")
        geo_raw = geo_row.get("raw_verification_status", "raw_not_inspected")
        raw_verified = timing_raw == "raw_variables_inspected" and geo_raw == "raw_variables_inspected"
        if raw_verified:
            gate = "ready_for_climate_linkage_input_build"
            gap = "construct data/climate_linkage_input.csv from verified coordinates/geography and interview timing"
        elif timing_supported and geo_supported:
            gate = "metadata_ready_raw_unverified"
            gap = "raw survey timing and geography/GPS/admin variables must be inspected before exposure extraction"
        else:
            gate = "metadata_incomplete_for_climate_linkage"
            missing = []
            if not timing_supported:
                missing.append("survey_timing")
            if not geo_supported:
                missing.append("climate_geography")
            gap = "metadata missing or weak for " + ";".join(missing)
        geo_files = geo_row.get("candidate_files", "")
        planned_level = "gps_or_cluster_if_raw_verified_else_admin_fallback"
        if "geovariable" in geo_files.lower() or "gps" in geo_files.lower() or "latitude" in geo_row.get("candidate_variables", "").lower():
            planned_level = "cluster_or_household_point_if_coordinates_pass_quality_checks"
        rows.append(
            {
                "quality_rank": priority.get("quality_rank", ""),
                "country": priority.get("country", ""),
                "survey_name": priority.get("survey_name", ""),
                "wave": priority.get("wave", ""),
                "idno": idno,
                "timing_metadata_status": timing_row.get("metadata_support_status", "missing_from_metadata"),
                "geography_metadata_status": geo_row.get("metadata_support_status", "missing_from_metadata"),
                "timing_raw_verification_status": timing_raw,
                "geography_raw_verification_status": geo_raw,
                "candidate_timing_files": timing_row.get("candidate_files", ""),
                "candidate_geography_files": geo_files,
                "planned_geography_level": planned_level,
                "primary_rainfall_source": "CHIRPS daily/global precipitation",
                "primary_temperature_source": "ERA5-Land daily statistics or reanalysis",
                "fallback_source": "NASA POWER daily point API",
                "robustness_sources": "TerraClimate monthly water balance; SPEI drought index; NASA POWER cross-checks",
                "planned_windows": ",".join(WINDOWS),
                "planned_exposure_families": "rainfall_total;rainfall_anomaly;drought_indicator;extreme_wet_indicator;temperature_mean;heat_days;water_balance_or_spei",
                "climate_linkage_gate_status": gate,
                "blocking_gap": gap,
            }
        )
    return rows


def specification_rows() -> list[dict[str, str]]:
    specs = []
    source_status = {
        "CHIRPS daily/global precipitation": "source_probe_ready" if any_source_ready({"primary_rainfall_documentation", "primary_rainfall_data_directory"}) else "source_probe_missing",
        "ERA5-Land daily statistics or reanalysis": "source_probe_ready" if any_source_ready({"primary_temperature_documentation", "primary_daily_temperature_documentation"}) else "source_probe_missing",
        "NASA POWER daily point API": "source_probe_ready" if any_source_ready({"rapid_point_fallback_documentation", "rapid_point_fallback_api"}) else "source_probe_missing",
        "TerraClimate monthly water balance": "source_probe_ready" if any_source_ready({"water_balance_robustness_documentation", "water_balance_robustness_catalog"}) else "source_probe_missing",
        "SPEI drought index": "source_probe_ready" if source_ready("drought_robustness_documentation") else "source_probe_missing",
    }
    exposure_defs = [
        {
            "family": "rainfall",
            "name": "rainfall_total",
            "source": "CHIRPS daily/global precipitation",
            "fallback": "NASA POWER daily point API",
            "product": "daily precipitation",
            "unit": "mm over window",
            "rule": "sum daily precipitation over the pre-interview window at verified point or admin aggregation",
        },
        {
            "family": "rainfall",
            "name": "rainfall_z_score",
            "source": "CHIRPS daily/global precipitation",
            "fallback": "NASA POWER daily point API",
            "product": "daily/monthly precipitation baseline",
            "unit": "standard deviations",
            "rule": "standardize window rainfall against local historical baseline after baseline period is documented",
        },
        {
            "family": "rainfall",
            "name": "drought_indicator",
            "source": "CHIRPS daily/global precipitation",
            "fallback": "SPEI drought index",
            "product": "rainfall z-score or SPEI",
            "unit": "binary",
            "rule": "1 if rainfall z-score < -1, with severe drought at < -1.5; use SPEI as robustness only after scale is documented",
        },
        {
            "family": "rainfall",
            "name": "extreme_wet_indicator",
            "source": "CHIRPS daily/global precipitation",
            "fallback": "NASA POWER daily point API",
            "product": "rainfall z-score or percentile",
            "unit": "binary",
            "rule": "1 if rainfall z-score > 1.5 or percentile threshold is passed after local baseline construction",
        },
        {
            "family": "temperature",
            "name": "temperature_mean",
            "source": "ERA5-Land daily statistics or reanalysis",
            "fallback": "NASA POWER daily point API",
            "product": "daily mean temperature",
            "unit": "Celsius after unit conversion if raw product is Kelvin",
            "rule": "average daily mean temperature over the pre-interview window",
        },
        {
            "family": "temperature",
            "name": "heat_days_95p",
            "source": "ERA5-Land daily statistics or reanalysis",
            "fallback": "NASA POWER daily point API",
            "product": "daily maximum temperature",
            "unit": "days",
            "rule": "count days above local 95th percentile after historical baseline is constructed",
        },
        {
            "family": "water_balance",
            "name": "spei_or_water_deficit",
            "source": "TerraClimate monthly water balance",
            "fallback": "SPEI drought index",
            "product": "SPEI, water deficit, PET or related balance variable",
            "unit": "source-specific; must record scale and units",
            "rule": "extract monthly value matching the pre-interview window only as robustness after source units/scales are verified",
        },
    ]
    for exposure in exposure_defs:
        for window in WINDOWS:
            status = "blocked_until_verified_geography_and_timing"
            if source_status.get(exposure["source"]) != "source_probe_ready":
                status = "blocked_source_probe_missing"
            specs.append(
                {
                    "exposure_family": exposure["family"],
                    "exposure_name": exposure["name"],
                    "primary_source": exposure["source"],
                    "fallback_or_robustness_source": exposure["fallback"],
                    "window": window,
                    "raw_source_variable_or_product": exposure["product"],
                    "unit_or_scale": exposure["unit"],
                    "construction_rule": exposure["rule"],
                    "minimum_inputs_required": "verified latitude/longitude or admin geography; verified interview date/month; geolocation quality flag",
                    "current_status": status,
                }
            )
    return specs


def summary_rows(plans: list[dict[str, str]], specs: list[dict[str, str]]) -> list[dict[str, str]]:
    gate_counts = Counter(row.get("climate_linkage_gate_status", "") for row in plans)
    source_counts = Counter(row.get("current_status", "") for row in specs)
    rows = [
        {"metric": "climate_plan_country_waves", "value": str(len(plans)), "interpretation": "Quality-screened country-waves with dataset-level climate linkage plans."},
        {"metric": "climate_exposure_spec_rows", "value": str(len(specs)), "interpretation": "Pre-specified exposure family/window/source rows."},
        {"metric": "metadata_ready_raw_unverified_country_waves", "value": str(gate_counts.get("metadata_ready_raw_unverified", 0)), "interpretation": "Timing and geography appear plausible in metadata but raw files are not inspected."},
        {"metric": "ready_for_climate_linkage_input_build", "value": str(gate_counts.get("ready_for_climate_linkage_input_build", 0)), "interpretation": "Country-waves with raw-verified timing and geography."},
        {"metric": "blocked_until_verified_geography_and_timing_specs", "value": str(source_counts.get("blocked_until_verified_geography_and_timing", 0)), "interpretation": "Exposure specifications blocked by raw-data linkage inputs, not by source probing."},
    ]
    for gate, count in sorted(gate_counts.items()):
        rows.append({"metric": f"gate_count_{gate}", "value": str(count), "interpretation": "Dataset-level climate linkage gate count."})
    return rows


def markdown_count_table(counter: Counter[str], label: str) -> str:
    lines = [f"| {label} | Count |", "|---|---:|"]
    for key, count in counter.most_common():
        lines.append(f"| {key or 'blank'} | {count} |")
    return "\n".join(lines)


def write_report(plans: list[dict[str, str]], specs: list[dict[str, str]], summaries: list[dict[str, str]]) -> None:
    gate_counts = Counter(row.get("climate_linkage_gate_status", "") for row in plans)
    source_status = Counter(row.get("current_status", "") for row in specs)
    lines = [
        "# Climate Exposure Plan",
        "",
        "Status: exposure construction is planned but blocked until raw survey timing and geography are inspected. This report does not claim any climate exposure has been constructed.",
        "",
        "## Dataset Gate Counts",
        "",
        markdown_count_table(gate_counts, "Climate linkage gate status"),
        "",
        "## Exposure Specification Status",
        "",
        markdown_count_table(source_status, "Exposure spec status"),
        "",
        "## Summary Metrics",
        "",
        "| Metric | Value | Interpretation |",
        "|---|---:|---|",
    ]
    for row in summaries:
        lines.append(f"| {row['metric']} | {row['value']} | {row['interpretation']} |")
    lines.extend(
        [
            "",
            "## Source Hierarchy",
            "",
            "| Domain | Primary | Fallback / robustness |",
            "|---|---|---|",
            "| Rainfall | CHIRPS daily/global precipitation | NASA POWER point checks; ERA5-Land precipitation checks if needed |",
            "| Temperature | ERA5-Land daily statistics or reanalysis | NASA POWER point API |",
            "| Drought/water balance | CHIRPS-derived anomalies plus TerraClimate/SPEI robustness | SPEI scale-specific drought robustness |",
            "",
            "## Guardrail",
            "",
            "Climate linkage requires raw-verified survey timing and raw-verified geography or coordinates. Metadata-supported timing/geography is useful for planning downloads only; it is not sufficient for exposure extraction or causal timing assumptions.",
            "",
            "## Machine-Readable Outputs",
            "",
            "- `temp/climate_exposure_plan.csv`",
            "- `result/climate_exposure_specification.csv`",
            "- `result/climate_exposure_plan_summary.csv`",
        ]
    )
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    ensure_dirs()
    plans = plan_rows()
    specs = specification_rows()
    summaries = summary_rows(plans, specs)
    write_csv(PLAN_PATH, plans, PLAN_COLUMNS)
    write_csv(SPEC_PATH, specs, SPEC_COLUMNS)
    write_csv(SUMMARY_PATH, summaries, SUMMARY_COLUMNS)
    write_report(plans, specs, summaries)
    ready = sum(1 for row in plans if row.get("climate_linkage_gate_status") == "ready_for_climate_linkage_input_build")
    metadata_ready = sum(1 for row in plans if row.get("climate_linkage_gate_status") == "metadata_ready_raw_unverified")
    append_log(TEMP_DIR / "audit_log.md", f"Climate exposure plan rows={len(plans)} specs={len(specs)} metadata_ready_raw_unverified={metadata_ready} ready_for_linkage={ready}.")
    print(f"Climate exposure plan rows={len(plans)} specs={len(specs)} metadata_ready_raw_unverified={metadata_ready} ready_for_linkage={ready}.")


if __name__ == "__main__":
    main()
