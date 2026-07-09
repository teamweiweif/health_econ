from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

import pandas as pd

from common import DATA_DIR, REPORT_DIR, RESULT_DIR, TEMP_DIR, append_log, ensure_dirs, write_csv


IDNO = "ALB_2002_LSMS_v01_M"
COUNTRY = "Albania"
SURVEY_NAME = "Living Standards Measurement Survey 2002"
WAVE = "2002"

CENTROID_PATH = TEMP_DIR / "alb2002_climate_centroid_exposure_candidates.csv"
SHOCK_PATH = TEMP_DIR / "alb2002_climate_shock_candidate_exposures.csv"
OUTPUT_PATH = DATA_DIR / "climate_exposures_nasa_power.csv"
CLIMATE_AUDIT_PATH = TEMP_DIR / "climate_extraction_audit.csv"
PROMOTION_AUDIT_PATH = TEMP_DIR / "alb2002_limited_climate_exposure_promotion_audit.csv"
SUMMARY_PATH = RESULT_DIR / "alb2002_limited_climate_exposure_promotion_summary.csv"
REPORT_PATH = REPORT_DIR / "alb2002_limited_climate_exposure_promotion.md"

DECISION = "limited_nasa_admin2_centroid_climate_exposures_promoted_linkage_still_blocked"
SCOPE = "alb2002_admin2_centroid_nasa_power_fallback_no_historical_baseline"
DATA_USE_LIMIT = "climate_exposure_admin2_centroid_only_not_for_final_climate_linkage"
PROMOTION_STATUS = "limited_climate_exposure_promoted_linkage_and_causal_analysis_blocked"

OUTPUT_COLUMNS = [
    "country",
    "survey_name",
    "wave",
    "idno",
    "survey_year",
    "survey_month",
    "exposure_anchor_date",
    "district_code",
    "district_name",
    "geography_level",
    "latitude",
    "longitude",
    "centroid_lat",
    "centroid_lon",
    "boundary_source",
    "boundary_year",
    "geolocation_quality",
    "window_months",
    "start_date",
    "end_date",
    "n_days",
    "precip_total_mm",
    "precip_mean_mm_day",
    "temp_mean_c",
    "temp_max_c",
    "temp_min_c",
    "source",
    "climate_source_role",
    "reference_group",
    "reference_group_rows",
    "precip_within_candidate_z",
    "precip_within_candidate_percentile",
    "temp_within_candidate_z",
    "temp_within_candidate_percentile",
    "diagnostic_low_rain_z_le_m1",
    "diagnostic_severe_low_rain_z_le_m15",
    "diagnostic_extreme_wet_z_ge_15",
    "diagnostic_heat_z_ge_1",
    "diagnostic_extreme_heat_z_ge_15",
    "diagnostic_combined_climate_stress",
    "climate_exposure_scope",
    "data_use_limit",
    "primary_chirps_ready",
    "primary_era5_ready",
    "historical_baseline_ready",
    "climate_linkage_ready",
    "final_analysis_ready",
    "limited_data_write_ready",
    "promotion_status",
    "blocking_reason",
]

CLIMATE_AUDIT_COLUMNS = ["check", "status", "detail", "input_path", "rows", "valid_rows", "output_path"]

PROMOTION_AUDIT_COLUMNS = [
    "gate_id",
    "gate_label",
    "status",
    "rows_checked",
    "rows_passing",
    "rows_blocked",
    "evidence",
    "output_artifact",
    "next_action",
]

SUMMARY_COLUMNS = ["metric", "value", "interpretation"]


def read_csv_dicts(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def row_count(path: Path) -> int:
    return len(read_csv_dicts(path))


def nonmissing(frame: pd.DataFrame, column: str) -> int:
    if column not in frame.columns:
        return 0
    series = frame[column]
    return int((series.notna() & (series.astype(str).str.strip() != "")).sum())


def safe_int(value: Any) -> int:
    try:
        return int(float(str(value).strip()))
    except (TypeError, ValueError):
        return 0


def blocking_reason() -> str:
    return (
        "NASA POWER daily summaries are promoted only as a limited fallback exposure file at candidate admin2 "
        "bounding-box centroids. They are not final climate-linkage inputs because 2001/2002 boundaries, exact GPS, "
        "CHIRPS rainfall, ERA5-Land temperature, and historical local anomaly baselines remain unresolved."
    )


def build_output(centroid: pd.DataFrame, shock: pd.DataFrame) -> pd.DataFrame:
    keys = ["district_code", "survey_month", "window_months", "start_date", "end_date"]
    shock_keep = [
        *keys,
        "reference_group",
        "reference_group_rows",
        "precip_within_candidate_z",
        "precip_within_candidate_percentile",
        "temp_within_candidate_z",
        "temp_within_candidate_percentile",
        "diagnostic_low_rain_z_le_m1",
        "diagnostic_severe_low_rain_z_le_m15",
        "diagnostic_extreme_wet_z_ge_15",
        "diagnostic_heat_z_ge_1",
        "diagnostic_extreme_heat_z_ge_15",
        "diagnostic_combined_climate_stress",
    ]
    missing = [column for column in keys if column not in centroid.columns or column not in shock.columns]
    if missing:
        raise ValueError(f"Missing climate exposure merge keys: {', '.join(sorted(set(missing)))}")

    data = centroid.merge(shock[[column for column in shock_keep if column in shock.columns]], on=keys, how="left", validate="one_to_one")
    out = pd.DataFrame(
        {
            "country": data.get("country", COUNTRY),
            "survey_name": data.get("survey_name", SURVEY_NAME),
            "wave": data.get("wave", WAVE),
            "idno": data.get("idno", IDNO),
            "survey_year": data.get("survey_year", ""),
            "survey_month": data.get("survey_month", ""),
            "exposure_anchor_date": data.get("exposure_anchor_date", ""),
            "district_code": data.get("district_code", ""),
            "district_name": data.get("district_name", ""),
            "geography_level": "admin2_bbox_centroid",
            "latitude": data.get("centroid_lat", ""),
            "longitude": data.get("centroid_lon", ""),
            "centroid_lat": data.get("centroid_lat", ""),
            "centroid_lon": data.get("centroid_lon", ""),
            "boundary_source": data.get("boundary_source", ""),
            "boundary_year": data.get("boundary_year", ""),
            "geolocation_quality": "candidate_admin2_bbox_centroid_not_verified_2002_boundary",
            "window_months": data.get("window_months", ""),
            "start_date": data.get("start_date", ""),
            "end_date": data.get("end_date", ""),
            "n_days": data.get("n_days", ""),
            "precip_total_mm": data.get("precip_total_mm", ""),
            "precip_mean_mm_day": data.get("precip_mean_mm_day", ""),
            "temp_mean_c": data.get("temp_mean_c", ""),
            "temp_max_c": data.get("temp_max_c", ""),
            "temp_min_c": data.get("temp_min_c", ""),
            "source": data.get("source", "NASA POWER daily point API fallback"),
            "climate_source_role": "nasa_power_fallback_not_primary_chirps_era5",
            "reference_group": data.get("reference_group", ""),
            "reference_group_rows": data.get("reference_group_rows", ""),
            "precip_within_candidate_z": data.get("precip_within_candidate_z", ""),
            "precip_within_candidate_percentile": data.get("precip_within_candidate_percentile", ""),
            "temp_within_candidate_z": data.get("temp_within_candidate_z", ""),
            "temp_within_candidate_percentile": data.get("temp_within_candidate_percentile", ""),
            "diagnostic_low_rain_z_le_m1": data.get("diagnostic_low_rain_z_le_m1", ""),
            "diagnostic_severe_low_rain_z_le_m15": data.get("diagnostic_severe_low_rain_z_le_m15", ""),
            "diagnostic_extreme_wet_z_ge_15": data.get("diagnostic_extreme_wet_z_ge_15", ""),
            "diagnostic_heat_z_ge_1": data.get("diagnostic_heat_z_ge_1", ""),
            "diagnostic_extreme_heat_z_ge_15": data.get("diagnostic_extreme_heat_z_ge_15", ""),
            "diagnostic_combined_climate_stress": data.get("diagnostic_combined_climate_stress", ""),
            "climate_exposure_scope": SCOPE,
            "data_use_limit": DATA_USE_LIMIT,
            "primary_chirps_ready": "0",
            "primary_era5_ready": "0",
            "historical_baseline_ready": "0",
            "climate_linkage_ready": "0",
            "final_analysis_ready": "0",
            "limited_data_write_ready": "1",
            "promotion_status": PROMOTION_STATUS,
            "blocking_reason": blocking_reason(),
        }
    )
    for column in OUTPUT_COLUMNS:
        if column not in out.columns:
            out[column] = ""
    return out[OUTPUT_COLUMNS]


def promotion_audit(output: pd.DataFrame) -> list[dict[str, Any]]:
    rows = len(output)
    distinct_districts = int(output["district_code"].nunique()) if rows else 0
    windows = int(output["window_months"].nunique()) if rows else 0
    precip = nonmissing(output, "precip_total_mm")
    temp = nonmissing(output, "temp_mean_c")
    z_precip = nonmissing(output, "precip_within_candidate_z")
    z_temp = nonmissing(output, "temp_within_candidate_z")
    return [
        {
            "gate_id": "source_rows",
            "gate_label": "NASA POWER fallback exposure rows",
            "status": "complete_limited_fallback",
            "rows_checked": rows,
            "rows_passing": rows,
            "rows_blocked": 0,
            "evidence": f"rows={rows}; districts={distinct_districts}; windows={windows}",
            "output_artifact": "data/climate_exposures_nasa_power.csv",
            "next_action": "Use as fallback exposure evidence only; do not treat as final climate-linked analysis input.",
        },
        {
            "gate_id": "value_coverage",
            "gate_label": "Precipitation and temperature value coverage",
            "status": "complete_limited_fallback" if precip == rows and temp == rows else "partial",
            "rows_checked": rows,
            "rows_passing": min(precip, temp),
            "rows_blocked": rows - min(precip, temp),
            "evidence": f"precip_nonmissing={precip}; temp_nonmissing={temp}",
            "output_artifact": "data/climate_exposures_nasa_power.csv",
            "next_action": "Compare against CHIRPS and ERA5-Land before final exposure claims.",
        },
        {
            "gate_id": "diagnostic_zscores",
            "gate_label": "Within-candidate diagnostic z-scores",
            "status": "complete_limited_diagnostic",
            "rows_checked": rows,
            "rows_passing": min(z_precip, z_temp),
            "rows_blocked": rows - min(z_precip, z_temp),
            "evidence": f"precip_z_rows={z_precip}; temp_z_rows={z_temp}",
            "output_artifact": "data/climate_exposures_nasa_power.csv",
            "next_action": "Replace with local historical baselines before interpreting shocks as anomalies.",
        },
        {
            "gate_id": "primary_source_gate",
            "gate_label": "Primary CHIRPS rainfall and ERA5-Land temperature",
            "status": "blocked_primary_sources_not_extracted",
            "rows_checked": rows,
            "rows_passing": 0,
            "rows_blocked": rows,
            "evidence": "primary_chirps_ready=0; primary_era5_ready=0",
            "output_artifact": "",
            "next_action": "Extract and compare CHIRPS/ERA5-Land or document why NASA fallback remains the only feasible source.",
        },
        {
            "gate_id": "historical_baseline_gate",
            "gate_label": "Historical local climate baseline",
            "status": "blocked_no_historical_baseline",
            "rows_checked": rows,
            "rows_passing": 0,
            "rows_blocked": rows,
            "evidence": "historical_baseline_ready=0",
            "output_artifact": "",
            "next_action": "Build historical local climatology before final drought/heat anomaly treatment definitions.",
        },
        {
            "gate_id": "climate_linkage_gate",
            "gate_label": "Climate-linked household analysis readiness",
            "status": "blocked_not_linkage_ready",
            "rows_checked": rows,
            "rows_passing": 0,
            "rows_blocked": rows,
            "evidence": "climate_linkage_ready=0; final_analysis_ready=0",
            "output_artifact": "",
            "next_action": "Verify geography and outcomes before writing climate-linked household data.",
        },
    ]


def climate_audit_rows(output: pd.DataFrame) -> list[dict[str, Any]]:
    return [
        {
            "check": "climate_input",
            "status": "complete_limited_admin2_centroid_input",
            "detail": "ALB_2002 candidate admin2 centroid exposure inputs exist; coordinates are centroids, not household GPS.",
            "input_path": "temp/alb2002_climate_centroid_exposure_candidates.csv",
            "rows": len(output),
            "valid_rows": len(output),
            "output_path": "data/climate_exposures_nasa_power.csv",
        },
        {
            "check": "climate_extraction",
            "status": "complete_limited_nasa_power_fallback",
            "detail": "NASA POWER fallback precipitation and temperature summaries are present for all ALB_2002 district-month-window cells.",
            "input_path": "temp/alb2002_climate_centroid_exposure_candidates.csv",
            "rows": len(output),
            "valid_rows": min(nonmissing(output, "precip_total_mm"), nonmissing(output, "temp_mean_c")),
            "output_path": "data/climate_exposures_nasa_power.csv",
        },
        {
            "check": "climate_guardrail",
            "status": "blocked_final_linkage",
            "detail": "Exposure file is limited fallback evidence only; no CHIRPS/ERA5 primary extraction, historical baseline, verified 2002 boundary, or final climate-linked household data.",
            "input_path": "data/climate_exposures_nasa_power.csv",
            "rows": len(output),
            "valid_rows": 0,
            "output_path": "",
        },
    ]


def summary_rows(output: pd.DataFrame, audit_rows: list[dict[str, Any]]) -> list[dict[str, str]]:
    rows = len(output)
    return [
        {"metric": "alb2002_limited_climate_exposure_promotion_audit_rows", "value": str(len(audit_rows)), "interpretation": "Rows in the limited climate exposure promotion audit."},
        {"metric": "alb2002_limited_climate_exposure_rows", "value": str(rows), "interpretation": "Rows written to data/climate_exposures_nasa_power.csv."},
        {"metric": "alb2002_limited_climate_exposure_distinct_district_rows", "value": str(output["district_code"].nunique() if rows else 0), "interpretation": "Distinct ALB_2002 admin2 district codes."},
        {"metric": "alb2002_limited_climate_exposure_window_rows", "value": str(output["window_months"].nunique() if rows else 0), "interpretation": "Exposure lag windows."},
        {"metric": "alb2002_limited_climate_exposure_precip_nonmissing_rows", "value": str(nonmissing(output, "precip_total_mm")), "interpretation": "Rows with nonmissing precipitation totals."},
        {"metric": "alb2002_limited_climate_exposure_temp_nonmissing_rows", "value": str(nonmissing(output, "temp_mean_c")), "interpretation": "Rows with nonmissing mean temperature."},
        {"metric": "alb2002_limited_climate_exposure_precip_z_rows", "value": str(nonmissing(output, "precip_within_candidate_z")), "interpretation": "Rows with within-candidate diagnostic rainfall z-scores."},
        {"metric": "alb2002_limited_climate_exposure_temp_z_rows", "value": str(nonmissing(output, "temp_within_candidate_z")), "interpretation": "Rows with within-candidate diagnostic temperature z-scores."},
        {"metric": "alb2002_limited_climate_exposure_limited_data_write_ready_rows", "value": str(safe_int(pd.to_numeric(output["limited_data_write_ready"], errors="coerce").fillna(0).sum()) if rows else 0), "interpretation": "Rows allowed in data/ only under limited fallback exposure scope."},
        {"metric": "alb2002_limited_climate_exposure_primary_chirps_ready_rows", "value": "0", "interpretation": "Rows ready with primary CHIRPS rainfall extraction."},
        {"metric": "alb2002_limited_climate_exposure_primary_era5_ready_rows", "value": "0", "interpretation": "Rows ready with primary ERA5-Land temperature extraction."},
        {"metric": "alb2002_limited_climate_exposure_historical_baseline_ready_rows", "value": "0", "interpretation": "Rows with accepted historical local climate baseline."},
        {"metric": "alb2002_limited_climate_exposure_climate_linkage_ready_rows", "value": "0", "interpretation": "Rows ready for final climate-linked household data."},
        {"metric": "alb2002_limited_climate_exposure_final_analysis_ready_rows", "value": "0", "interpretation": "Rows ready for final empirical analysis."},
        {"metric": "alb2002_limited_climate_exposure_current_decision", "value": DECISION, "interpretation": "Current limited climate exposure promotion decision."},
        {"metric": "alb2002_limited_climate_exposure_data_use_limit", "value": DATA_USE_LIMIT, "interpretation": "Guardrail embedded in every output row."},
    ]


def markdown_table(rows: list[dict[str, Any]], columns: list[str]) -> str:
    lines = ["| " + " | ".join(columns) + " |", "|" + "|".join("---" for _ in columns) + "|"]
    for row in rows:
        values = []
        for column in columns:
            value = str(row.get(column, "")).replace("|", "/")
            if len(value) > 120:
                value = value[:117] + "..."
            values.append(value)
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines)


def write_report(summary: list[dict[str, str]], audit_rows: list[dict[str, Any]]) -> None:
    REPORT_PATH.write_text(
        f"""# ALB_2002 Limited Climate Exposure Promotion

Status: limited fallback exposure promoted. This writes `data/climate_exposures_nasa_power.csv` from existing NASA POWER admin2-centroid exposure candidates. It does not promote final climate linkage, causal shocks, CHIRPS rainfall, ERA5-Land temperature, historical anomaly baselines, or household-level GPS exposure.

## Summary

{markdown_table(summary, ["metric", "value", "interpretation"])}

## Gate Audit

{markdown_table(audit_rows, ["gate_id", "status", "rows_passing", "rows_blocked", "next_action"])}

## Guardrails

- Every row carries `climate_exposure_scope={SCOPE}`.
- Every row carries `data_use_limit={DATA_USE_LIMIT}`.
- `primary_chirps_ready`, `primary_era5_ready`, `historical_baseline_ready`, `climate_linkage_ready`, and `final_analysis_ready` remain zero.
- The file supports audit and fallback exposure inspection only; it is not sufficient for climate-linked household analysis.

## Machine-Readable Outputs

- `data/climate_exposures_nasa_power.csv`
- `temp/climate_extraction_audit.csv`
- `temp/alb2002_limited_climate_exposure_promotion_audit.csv`
- `result/alb2002_limited_climate_exposure_promotion_summary.csv`
""",
        encoding="utf-8",
    )


def main() -> None:
    ensure_dirs()
    if not CENTROID_PATH.exists() or not SHOCK_PATH.exists():
        raise FileNotFoundError("Missing ALB_2002 centroid or shock candidate exposure input.")

    centroid = pd.read_csv(CENTROID_PATH, dtype=str, keep_default_na=False)
    shock = pd.read_csv(SHOCK_PATH, dtype=str, keep_default_na=False)
    output = build_output(centroid, shock)

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    output.to_csv(OUTPUT_PATH, index=False, encoding="utf-8-sig")

    audit_rows = promotion_audit(output)
    climate_rows = climate_audit_rows(output)
    summary = summary_rows(output, audit_rows)

    write_csv(CLIMATE_AUDIT_PATH, climate_rows, CLIMATE_AUDIT_COLUMNS)
    write_csv(PROMOTION_AUDIT_PATH, audit_rows, PROMOTION_AUDIT_COLUMNS)
    write_csv(SUMMARY_PATH, summary, SUMMARY_COLUMNS)
    write_report(summary, audit_rows)

    append_log(TEMP_DIR / "audit_log.md", f"Promoted limited ALB_2002 climate exposure rows={len(output)} decision={DECISION}.")
    print(f"Promoted limited ALB_2002 climate exposure rows={len(output)} decision={DECISION}.")


if __name__ == "__main__":
    main()
