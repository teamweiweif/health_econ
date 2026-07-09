from __future__ import annotations

import csv
import math
from typing import Any

import pandas as pd

from common import REPORT_DIR, RESULT_DIR, TEMP_DIR, append_log, ensure_dirs, write_csv


CENTROID_EXPOSURE_PATH = TEMP_DIR / "alb2002_climate_centroid_exposure_candidates.csv"
CENTROID_SUMMARY_PATH = RESULT_DIR / "alb2002_climate_centroid_exposure_summary.csv"

SHOCK_PATH = TEMP_DIR / "alb2002_climate_shock_candidate_exposures.csv"
LINEAGE_PATH = TEMP_DIR / "alb2002_climate_shock_candidate_lineage.csv"
AUDIT_PATH = RESULT_DIR / "alb2002_climate_shock_candidate_audit.csv"
SUMMARY_PATH = RESULT_DIR / "alb2002_climate_shock_candidate_summary.csv"
REPORT_PATH = REPORT_DIR / "alb2002_climate_shock_candidate_audit.md"

DECISION = "blocked_alb2002_climate_shock_candidate_not_promoted_due_geography_baseline_primary_source_gates"
PROMOTION_STATUS = "temp_only_climate_shock_candidate_not_promoted"

SHOCK_COLUMNS = [
    "country",
    "survey_name",
    "wave",
    "idno",
    "survey_year",
    "survey_month",
    "exposure_anchor_date",
    "district_code",
    "district_name",
    "household_rows",
    "centroid_lon",
    "centroid_lat",
    "window_months",
    "start_date",
    "end_date",
    "n_days",
    "precip_total_mm",
    "precip_mean_mm_day",
    "temp_mean_c",
    "temp_max_c",
    "temp_min_c",
    "reference_group",
    "reference_group_rows",
    "precip_within_candidate_mean_mm",
    "precip_within_candidate_sd_mm",
    "precip_within_candidate_z",
    "precip_within_candidate_percentile",
    "temp_within_candidate_mean_c",
    "temp_within_candidate_sd_c",
    "temp_within_candidate_z",
    "temp_within_candidate_percentile",
    "diagnostic_low_rain_z_le_m1",
    "diagnostic_severe_low_rain_z_le_m15",
    "diagnostic_extreme_wet_z_ge_15",
    "diagnostic_heat_z_ge_1",
    "diagnostic_extreme_heat_z_ge_15",
    "diagnostic_cold_z_le_m15",
    "diagnostic_combined_climate_stress",
    "shock_measure_scope",
    "source",
    "boundary_source",
    "boundary_year",
    "exposure_quality_flag",
    "primary_chirps_ready",
    "primary_era5_ready",
    "historical_baseline_ready",
    "climate_linkage_ready",
    "data_write_ready",
    "promotion_status",
    "blocking_reason",
]

LINEAGE_COLUMNS = [
    "lineage_id",
    "derived_field",
    "source_fields",
    "source_artifacts",
    "formula_or_rule",
    "status",
    "blocking_reason",
]

AUDIT_COLUMNS = [
    "check_id",
    "check_label",
    "status",
    "rows_checked",
    "passing_rows",
    "failing_rows",
    "evidence",
    "promotion_ready_rows",
    "blocking_reason",
    "next_action",
]

SUMMARY_COLUMNS = ["metric", "value", "interpretation"]


def read_csv_dicts(path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def metric_value(rows: list[dict[str, str]], metric: str, default: str = "0") -> str:
    return next((row.get("value", default) for row in rows if row.get("metric") == metric), default)


def safe_float(value: Any) -> float:
    try:
        number = float(str(value).strip())
    except (TypeError, ValueError):
        return float("nan")
    return number if math.isfinite(number) else float("nan")


def fmt(value: Any) -> str:
    number = safe_float(value)
    if math.isnan(number):
        return "" if value is None else str(value)
    if number.is_integer():
        return str(int(number))
    return f"{number:.6g}"


def numeric(frame: pd.DataFrame, column: str) -> pd.Series:
    return pd.to_numeric(frame[column], errors="coerce") if column in frame.columns else pd.Series(dtype="float64")


def blocking_reason() -> str:
    return (
        "Within-candidate rainfall and temperature z-scores are computed only for diagnostic screening from NASA POWER "
        "fallback point summaries at candidate ADM2 centroids. They are not historical climate anomalies because verified "
        "2001/2002 geography, CHIRPS/ERA5 primary extraction, and local historical baselines remain unresolved."
    )


def add_group_diagnostics(frame: pd.DataFrame) -> pd.DataFrame:
    data = frame.copy()
    data["survey_month"] = pd.to_numeric(data["survey_month"], errors="coerce").astype("Int64")
    data["window_months"] = pd.to_numeric(data["window_months"], errors="coerce").astype("Int64")
    data["reference_group"] = "survey_month_" + data["survey_month"].astype(str) + "_window_" + data["window_months"].astype(str)
    group_cols = ["survey_month", "window_months"]
    group_size = data.groupby(group_cols)["district_code"].transform("size")
    data["reference_group_rows"] = group_size

    for source_col, prefix, mean_col, sd_col, z_col, percentile_col in [
        (
            "precip_total_mm",
            "precip",
            "precip_within_candidate_mean_mm",
            "precip_within_candidate_sd_mm",
            "precip_within_candidate_z",
            "precip_within_candidate_percentile",
        ),
        (
            "temp_mean_c",
            "temp",
            "temp_within_candidate_mean_c",
            "temp_within_candidate_sd_c",
            "temp_within_candidate_z",
            "temp_within_candidate_percentile",
        ),
    ]:
        values = numeric(data, source_col)
        mean = values.groupby([data[col] for col in group_cols]).transform("mean")
        sd = values.groupby([data[col] for col in group_cols]).transform(lambda s: s.std(ddof=0))
        z = ((values - mean) / sd).where(sd > 0)
        percentile = values.groupby([data[col] for col in group_cols]).rank(method="average", pct=True)
        data[mean_col] = mean
        data[sd_col] = sd
        data[z_col] = z
        data[percentile_col] = percentile

    precip_z = data["precip_within_candidate_z"]
    temp_z = data["temp_within_candidate_z"]
    data["diagnostic_low_rain_z_le_m1"] = (precip_z <= -1).fillna(False).astype(int)
    data["diagnostic_severe_low_rain_z_le_m15"] = (precip_z <= -1.5).fillna(False).astype(int)
    data["diagnostic_extreme_wet_z_ge_15"] = (precip_z >= 1.5).fillna(False).astype(int)
    data["diagnostic_heat_z_ge_1"] = (temp_z >= 1).fillna(False).astype(int)
    data["diagnostic_extreme_heat_z_ge_15"] = (temp_z >= 1.5).fillna(False).astype(int)
    data["diagnostic_cold_z_le_m15"] = (temp_z <= -1.5).fillna(False).astype(int)
    data["diagnostic_combined_climate_stress"] = (
        (data["diagnostic_severe_low_rain_z_le_m15"] == 1)
        | (data["diagnostic_extreme_wet_z_ge_15"] == 1)
        | (data["diagnostic_extreme_heat_z_ge_15"] == 1)
    ).astype(int)
    data["shock_measure_scope"] = "within_survey_month_window_candidate_district_distribution_not_historical_anomaly"
    data["primary_chirps_ready"] = "0"
    data["primary_era5_ready"] = "0"
    data["historical_baseline_ready"] = "0"
    data["climate_linkage_ready"] = "0"
    data["data_write_ready"] = "0"
    data["promotion_status"] = PROMOTION_STATUS
    data["blocking_reason"] = blocking_reason()
    return data


def bool_sum(frame: pd.DataFrame, column: str) -> int:
    return int(pd.to_numeric(frame[column], errors="coerce").fillna(0).sum()) if column in frame.columns else 0


def audit_row(check_id: str, label: str, status: str, rows_checked: int, passing: int, evidence: str, block: str, next_action: str) -> dict[str, str]:
    return {
        "check_id": check_id,
        "check_label": label,
        "status": status,
        "rows_checked": str(rows_checked),
        "passing_rows": str(passing),
        "failing_rows": str(max(rows_checked - passing, 0)),
        "evidence": evidence,
        "promotion_ready_rows": "0",
        "blocking_reason": block,
        "next_action": next_action,
    }


def build_audit(shocks: pd.DataFrame, centroid_summary: list[dict[str, str]]) -> list[dict[str, str]]:
    rows = len(shocks)
    reference_groups = int(shocks["reference_group"].nunique()) if rows else 0
    min_group = int(pd.to_numeric(shocks["reference_group_rows"], errors="coerce").min()) if rows else 0
    precip_nonmissing = int(shocks["precip_within_candidate_z"].notna().sum())
    temp_nonmissing = int(shocks["temp_within_candidate_z"].notna().sum())
    primary_ready = int(
        safe_float(metric_value(centroid_summary, "alb2002_climate_centroid_primary_chirps_ready_rows"))
        + safe_float(metric_value(centroid_summary, "alb2002_climate_centroid_primary_era5_ready_rows"))
    )
    baseline_ready = int(safe_float(metric_value(centroid_summary, "alb2002_climate_centroid_historical_baseline_ready_rows")))
    climate_ready = int(safe_float(metric_value(centroid_summary, "alb2002_climate_centroid_climate_linkage_ready_rows")))
    return [
        audit_row(
            "source_centroid_exposures",
            "Input centroid exposure rows are present",
            "complete_candidate_not_promoted" if rows else "missing",
            rows,
            rows,
            f"shock_rows={rows}; source_centroid_rows={metric_value(centroid_summary, 'alb2002_climate_centroid_exposure_rows')}",
            blocking_reason(),
            "Keep this as a temp-only derivative of the centroid exposure stress test.",
        ),
        audit_row(
            "reference_groups",
            "Within-candidate reference groups are defined by survey month and lag window",
            "complete_candidate_not_promoted" if reference_groups and min_group > 1 else "partial_or_failed",
            reference_groups,
            reference_groups if min_group > 1 else 0,
            f"reference_groups={reference_groups}; min_group_rows={min_group}; max_group_rows={int(pd.to_numeric(shocks['reference_group_rows'], errors='coerce').max()) if rows else 0}",
            "Reference groups are cross-sectional candidate districts, not historical local climatology.",
            "Replace these diagnostics with local historical baselines once accepted geography and primary climate sources are available.",
        ),
        audit_row(
            "diagnostic_zscores",
            "Within-candidate z-scores are computable for rainfall and temperature",
            "complete_candidate_not_promoted" if precip_nonmissing == rows and temp_nonmissing == rows else "partial_or_failed",
            rows,
            min(precip_nonmissing, temp_nonmissing),
            f"precip_z_nonmissing={precip_nonmissing}; temp_z_nonmissing={temp_nonmissing}",
            "These z-scores are diagnostic distributional flags only and cannot be interpreted as historical anomalies.",
            "Compute historical rainfall and heat anomalies against local multi-year baselines before climate-shock modeling.",
        ),
        audit_row(
            "diagnostic_shock_flags",
            "Diagnostic low-rain, wet, heat, and combined-stress flags are recorded",
            "complete_candidate_not_promoted",
            rows,
            bool_sum(shocks, "diagnostic_combined_climate_stress"),
            f"low_rain_z_le_m1={bool_sum(shocks, 'diagnostic_low_rain_z_le_m1')}; severe_low_rain_z_le_m15={bool_sum(shocks, 'diagnostic_severe_low_rain_z_le_m15')}; extreme_wet_z_ge_15={bool_sum(shocks, 'diagnostic_extreme_wet_z_ge_15')}; heat_z_ge_1={bool_sum(shocks, 'diagnostic_heat_z_ge_1')}; extreme_heat_z_ge_15={bool_sum(shocks, 'diagnostic_extreme_heat_z_ge_15')}; combined_stress={bool_sum(shocks, 'diagnostic_combined_climate_stress')}",
            "Diagnostic flags show candidate variation only; they are not accepted treatment variables.",
            "Use them to prioritize climate-source validation, not as causal-model treatments.",
        ),
        audit_row(
            "primary_sources",
            "Primary CHIRPS rainfall and ERA5-Land temperature extraction gate",
            "blocked",
            2,
            primary_ready,
            f"primary_chirps_ready={metric_value(centroid_summary, 'alb2002_climate_centroid_primary_chirps_ready_rows')}; primary_era5_ready={metric_value(centroid_summary, 'alb2002_climate_centroid_primary_era5_ready_rows')}",
            "NASA POWER fallback diagnostics do not satisfy the primary climate-source requirement.",
            "Extract CHIRPS rainfall and ERA5-Land temperature after geography is verified.",
        ),
        audit_row(
            "historical_baseline",
            "Historical local climate baseline gate",
            "blocked",
            rows,
            baseline_ready,
            f"historical_baseline_ready_rows={baseline_ready}",
            "No accepted local historical baseline exists for rainfall or temperature z-scores/percentiles.",
            "Build a multi-year local baseline for each accepted geography before interpreting shocks.",
        ),
        audit_row(
            "geography_vintage",
            "Historical geography and boundary-vintage gate",
            "blocked",
            rows,
            climate_ready,
            f"boundary_year={metric_value(centroid_summary, 'alb2002_climate_centroid_boundary_year', 'missing')}; climate_linkage_ready_rows={climate_ready}",
            "Candidate centroids use a current/2013 boundary source rather than verified 2001/2002 LSMS geography or GPS.",
            "Obtain verified historical district boundaries, GPS, EA maps, or an accepted crosswalk.",
        ),
        audit_row(
            "promotion",
            "Climate shock candidate promotion remains blocked",
            "blocked",
            rows,
            0,
            f"data_write_ready_rows=0; decision={DECISION}",
            blocking_reason(),
            "Do not write data/climate_exposures_* or data/climate_linked_household until geography, source, baseline, outcome, and harmonization gates pass.",
        ),
    ]


def lineage_rows() -> list[dict[str, str]]:
    artifacts = "temp/alb2002_climate_centroid_exposure_candidates.csv;result/alb2002_climate_centroid_exposure_summary.csv"
    rows = [
        ("lineage_001", "reference_group", "survey_month;window_months", "Survey-month-by-lag-window group used only for within-candidate diagnostics.", "Reference group is not historical climatology."),
        ("lineage_002", "precip_within_candidate_z", "precip_total_mm;survey_month;window_months", "(precip_total_mm - reference-group mean) / reference-group population SD.", "Rainfall z-score is not a CHIRPS or historical anomaly."),
        ("lineage_003", "temp_within_candidate_z", "temp_mean_c;survey_month;window_months", "(temp_mean_c - reference-group mean) / reference-group population SD.", "Temperature z-score is not an ERA5-Land or historical anomaly."),
        ("lineage_004", "diagnostic_low_rain/wet_flags", "precip_within_candidate_z", "Low-rain flag <= -1; severe low-rain flag <= -1.5; extreme-wet flag >= 1.5.", "Flags are prioritization diagnostics only."),
        ("lineage_005", "diagnostic_heat/cold_flags", "temp_within_candidate_z", "Heat flag >= 1; extreme-heat flag >= 1.5; cold flag <= -1.5.", "Flags are prioritization diagnostics only."),
        ("lineage_006", "diagnostic_combined_climate_stress", "diagnostic_severe_low_rain_z_le_m15;diagnostic_extreme_wet_z_ge_15;diagnostic_extreme_heat_z_ge_15", "Any severe low-rain, extreme-wet, or extreme-heat diagnostic flag.", "Combined flag is not a treatment variable."),
        ("lineage_007", "promotion_status", "primary_chirps_ready;primary_era5_ready;historical_baseline_ready;climate_linkage_ready", "Promotion remains zero until all climate-source, baseline, and geography gates pass.", "No data/ write is allowed."),
    ]
    return [
        {
            "lineage_id": row[0],
            "derived_field": row[1],
            "source_fields": row[2],
            "source_artifacts": artifacts,
            "formula_or_rule": row[3],
            "status": "candidate_not_promoted",
            "blocking_reason": row[4],
        }
        for row in rows
    ]


def summary_row(metric: str, value: Any, interpretation: str) -> dict[str, str]:
    return {"metric": metric, "value": fmt(value), "interpretation": interpretation}


def build_summary(shocks: pd.DataFrame, audit: list[dict[str, str]], lineage: list[dict[str, str]], centroid_summary: list[dict[str, str]]) -> list[dict[str, str]]:
    rows = len(shocks)
    group_sizes = pd.to_numeric(shocks["reference_group_rows"], errors="coerce") if rows else pd.Series(dtype="float64")
    return [
        summary_row("alb2002_climate_shock_candidate_exposure_rows", rows, "Temp-only climate shock diagnostic rows derived from centroid exposures."),
        summary_row("alb2002_climate_shock_candidate_source_centroid_rows", metric_value(centroid_summary, "alb2002_climate_centroid_exposure_rows"), "Source centroid exposure rows consumed."),
        summary_row("alb2002_climate_shock_candidate_lineage_rows", len(lineage), "Lineage rows for diagnostic shock fields."),
        summary_row("alb2002_climate_shock_candidate_audit_rows", len(audit), "Audit rows for diagnostic shock construction and promotion gates."),
        summary_row("alb2002_climate_shock_candidate_distinct_district_rows", shocks["district_code"].nunique() if rows else 0, "Distinct districts represented."),
        summary_row("alb2002_climate_shock_candidate_survey_month_rows", shocks["survey_month"].nunique() if rows else 0, "Distinct survey months represented."),
        summary_row("alb2002_climate_shock_candidate_window_rows", shocks["window_months"].nunique() if rows else 0, "Distinct lag windows represented."),
        summary_row("alb2002_climate_shock_candidate_reference_group_rows", shocks["reference_group"].nunique() if rows else 0, "Survey-month-by-window diagnostic reference groups."),
        summary_row("alb2002_climate_shock_candidate_min_reference_group_size", group_sizes.min() if rows else 0, "Smallest within-candidate reference group size."),
        summary_row("alb2002_climate_shock_candidate_max_reference_group_size", group_sizes.max() if rows else 0, "Largest within-candidate reference group size."),
        summary_row("alb2002_climate_shock_candidate_precip_z_nonmissing_rows", shocks["precip_within_candidate_z"].notna().sum() if rows else 0, "Rows with diagnostic rainfall z-scores."),
        summary_row("alb2002_climate_shock_candidate_temp_z_nonmissing_rows", shocks["temp_within_candidate_z"].notna().sum() if rows else 0, "Rows with diagnostic temperature z-scores."),
        summary_row("alb2002_climate_shock_candidate_low_rain_rows", bool_sum(shocks, "diagnostic_low_rain_z_le_m1"), "Rows with diagnostic low-rain z <= -1."),
        summary_row("alb2002_climate_shock_candidate_severe_low_rain_rows", bool_sum(shocks, "diagnostic_severe_low_rain_z_le_m15"), "Rows with diagnostic low-rain z <= -1.5."),
        summary_row("alb2002_climate_shock_candidate_extreme_wet_rows", bool_sum(shocks, "diagnostic_extreme_wet_z_ge_15"), "Rows with diagnostic wet z >= 1.5."),
        summary_row("alb2002_climate_shock_candidate_heat_rows", bool_sum(shocks, "diagnostic_heat_z_ge_1"), "Rows with diagnostic heat z >= 1."),
        summary_row("alb2002_climate_shock_candidate_extreme_heat_rows", bool_sum(shocks, "diagnostic_extreme_heat_z_ge_15"), "Rows with diagnostic heat z >= 1.5."),
        summary_row("alb2002_climate_shock_candidate_cold_rows", bool_sum(shocks, "diagnostic_cold_z_le_m15"), "Rows with diagnostic cold z <= -1.5."),
        summary_row("alb2002_climate_shock_candidate_combined_stress_rows", bool_sum(shocks, "diagnostic_combined_climate_stress"), "Rows with any severe low-rain, extreme-wet, or extreme-heat diagnostic flag."),
        summary_row("alb2002_climate_shock_candidate_primary_chirps_ready_rows", 0, "Rows with primary CHIRPS rainfall accepted; intentionally zero."),
        summary_row("alb2002_climate_shock_candidate_primary_era5_ready_rows", 0, "Rows with primary ERA5-Land temperature accepted; intentionally zero."),
        summary_row("alb2002_climate_shock_candidate_historical_baseline_ready_rows", 0, "Rows with local historical baselines accepted; intentionally zero."),
        summary_row("alb2002_climate_shock_candidate_climate_linkage_ready_rows", 0, "Rows ready for promoted climate linkage; intentionally zero."),
        summary_row("alb2002_climate_shock_candidate_data_write_ready_rows", 0, "Rows allowed to be written to data/; intentionally zero."),
        summary_row("alb2002_climate_shock_candidate_current_decision", DECISION, "Current fail-closed climate shock diagnostic decision."),
    ]


def markdown_rows(rows: list[dict[str, Any]], columns: list[str], limit: int = 25) -> str:
    lines = ["| " + " | ".join(columns) + " |", "|" + "|".join("---" for _ in columns) + "|"]
    for row in rows[:limit]:
        values = []
        for column in columns:
            value = str(row.get(column, "")).replace("|", "/")
            if len(value) > 130:
                value = value[:127] + "..."
            values.append(value)
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines)


def write_report(summary: list[dict[str, str]], audit: list[dict[str, str]], lineage: list[dict[str, str]]) -> None:
    summary_table = "\n".join(f"| {row['metric']} | {row['value']} | {row['interpretation']} |" for row in summary)
    REPORT_PATH.write_text(
        f"""# ALB_2002 Climate Shock Candidate Audit

Status: temp-only diagnostic climate-shock audit. This derives within-candidate rainfall and temperature z-scores from the ALB_2002 NASA POWER centroid exposure stress test. It does not create historical anomalies, accepted shock treatments, or any `data/` output.

## Summary

| Metric | Value | Interpretation |
|---|---:|---|
{summary_table}

## Readiness Audit

{markdown_rows(audit, ['check_id', 'status', 'rows_checked', 'passing_rows', 'promotion_ready_rows', 'evidence', 'blocking_reason'])}

## Lineage

{markdown_rows(lineage, ['derived_field', 'source_fields', 'formula_or_rule', 'status', 'blocking_reason'])}

## Interpretation

- The diagnostic z-scores compare districts within the same survey month and lag window; they are not local historical anomalies.
- NASA POWER remains a fallback source. CHIRPS rainfall and ERA5-Land temperature remain the primary climate-source requirement.
- Boundary vintage, historical geography/GPS, primary-source extraction, and historical baseline gates remain blocked.
- Climate-linkage-ready and data-write-ready rows remain zero.

## Machine-Readable Outputs

- `temp/alb2002_climate_shock_candidate_exposures.csv`
- `temp/alb2002_climate_shock_candidate_lineage.csv`
- `result/alb2002_climate_shock_candidate_audit.csv`
- `result/alb2002_climate_shock_candidate_summary.csv`
""",
        encoding="utf-8",
    )


def main() -> None:
    ensure_dirs()
    if not CENTROID_EXPOSURE_PATH.exists():
        raise FileNotFoundError(f"Missing prerequisite: {CENTROID_EXPOSURE_PATH}")
    centroid = pd.read_csv(CENTROID_EXPOSURE_PATH, encoding="utf-8-sig")
    shocks = add_group_diagnostics(centroid)
    lineage = lineage_rows()
    centroid_summary = read_csv_dicts(CENTROID_SUMMARY_PATH)
    audit = build_audit(shocks, centroid_summary)
    summary = build_summary(shocks, audit, lineage, centroid_summary)
    write_csv(SHOCK_PATH, shocks.fillna("").to_dict("records"), SHOCK_COLUMNS)
    write_csv(LINEAGE_PATH, lineage, LINEAGE_COLUMNS)
    write_csv(AUDIT_PATH, audit, AUDIT_COLUMNS)
    write_csv(SUMMARY_PATH, summary, SUMMARY_COLUMNS)
    write_report(summary, audit, lineage)
    append_log(TEMP_DIR / "audit_log.md", f"Built ALB_2002 climate shock candidate audit rows={len(shocks)} decision={DECISION}.")
    print(f"ALB_2002 climate shock candidate rows={len(shocks)} decision={DECISION}.")


if __name__ == "__main__":
    main()
