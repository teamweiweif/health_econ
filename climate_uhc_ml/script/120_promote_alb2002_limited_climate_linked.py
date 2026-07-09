from __future__ import annotations

from typing import Any

import pandas as pd

from common import DATA_DIR, REPORT_DIR, RESULT_DIR, TEMP_DIR, append_log, ensure_dirs, write_csv


IDNO = "ALB_2002_LSMS_v01_M"
COUNTRY = "Albania"
SURVEY_NAME = "Living Standards Measurement Survey 2002"
WAVE = "2002"

HOUSEHOLD_PATH = DATA_DIR / "harmonized_household.csv"
OUTCOME_PATH = DATA_DIR / "household_outcomes.csv"
CLIMATE_PATH = DATA_DIR / "climate_exposures_nasa_power.csv"
OUTPUT_PATH = DATA_DIR / "climate_linked_household.csv"
CLIMATE_MERGE_AUDIT_PATH = TEMP_DIR / "climate_merge_audit.csv"
PROMOTION_AUDIT_PATH = TEMP_DIR / "alb2002_limited_climate_linked_promotion_audit.csv"
SUMMARY_PATH = RESULT_DIR / "alb2002_limited_climate_linked_promotion_summary.csv"
REPORT_PATH = REPORT_DIR / "alb2002_limited_climate_linked_promotion.md"

DECISION = "limited_che_outcome_nasa_admin2_climate_linked_promoted_models_still_blocked"
SCOPE = "alb2002_limited_che_admin2_centroid_nasa_power_window_linkage_not_final"
DATA_USE_LIMIT = "climate_linked_che_diagnostic_only_not_for_promoted_descriptive_ml_causal_or_policy_analysis"
PROMOTION_STATUS = "limited_climate_linked_promoted_diagnostic_only_descriptive_ml_causal_policy_blocked"

CLIMATE_MERGE_AUDIT_COLUMNS = ["check", "status", "detail", "microdata_path", "climate_path", "rows_microdata", "rows_climate", "rows_output", "output_path"]
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

OUTPUT_COLUMNS = [
    "country",
    "survey_name",
    "wave",
    "idno",
    "survey_year",
    "survey_month",
    "interview_date",
    "hhid",
    "household_weight",
    "strata",
    "psu",
    "admin1",
    "admin2",
    "admin2_code",
    "district_code",
    "district_name",
    "cluster_id",
    "geolocation_quality",
    "rural",
    "household_size",
    "children_under_5",
    "children_under_15",
    "elderly_60_plus",
    "elderly_65_plus",
    "hh_head_sex",
    "hh_head_age",
    "agriculture_livelihood",
    "health_insurance",
    "total_consumption",
    "oop_health_expenditure",
    "oop_share_total",
    "log_oop_plus_one",
    "che10_total_budget",
    "che25_total_budget",
    "positive_oop",
    "window_months",
    "start_date",
    "end_date",
    "n_days",
    "precip_total_mm",
    "precip_mean_mm_day",
    "precip_within_candidate_z",
    "precip_within_candidate_percentile",
    "temp_mean_c",
    "temp_max_c",
    "temp_min_c",
    "temp_within_candidate_z",
    "temp_within_candidate_percentile",
    "diagnostic_low_rain_z_le_m1",
    "diagnostic_severe_low_rain_z_le_m15",
    "diagnostic_extreme_wet_z_ge_15",
    "diagnostic_heat_z_ge_1",
    "diagnostic_extreme_heat_z_ge_15",
    "diagnostic_combined_climate_stress",
    "climate_source",
    "boundary_source",
    "boundary_year",
    "climate_exposure_scope",
    "climate_linked_scope",
    "data_use_limit",
    "limited_climate_linked_write_ready",
    "sdg382_ready",
    "access_outcome_ready",
    "composite_uhc_ready",
    "primary_chirps_ready",
    "primary_era5_ready",
    "historical_baseline_ready",
    "climate_linkage_ready",
    "descriptive_ready",
    "predictive_ml_ready",
    "reduced_form_ready",
    "robustness_ready",
    "final_analysis_ready",
    "promotion_status",
    "blocking_reason",
]


def read(path):
    if not path.exists():
        raise FileNotFoundError(f"Missing required limited input: {path}")
    return pd.read_csv(path, dtype=str, keep_default_na=False)


def norm_code(series: pd.Series) -> pd.Series:
    text = series.astype(str).str.strip()
    return text.str.replace(r"\.0$", "", regex=True)


def norm_month(series: pd.Series) -> pd.Series:
    text = series.astype(str).str.strip()
    return text.str.replace(r"\.0$", "", regex=True)


def nonmissing(frame: pd.DataFrame, column: str) -> int:
    if column not in frame.columns:
        return 0
    series = frame[column]
    return int((series.notna() & (series.astype(str).str.strip() != "")).sum())


def numeric_sum(frame: pd.DataFrame, column: str) -> int:
    if column not in frame.columns:
        return 0
    return int(pd.to_numeric(frame[column], errors="coerce").fillna(0).sum())


def blocking_reason() -> str:
    return (
        "This limited household-window file links ALB_2002 CHE10/CHE25 outcomes to NASA POWER admin2-centroid "
        "fallback exposure windows for audit only. SDG/access/composite outcomes, CHIRPS/ERA5 primary sources, "
        "historical climate baselines, verified 2002 boundaries/GPS, promoted descriptive diagnostics, predictive ML, "
        "reduced-form estimation, robustness, causal ML, policy learning, and final empirical analysis remain blocked."
    )


def require_markers(household: pd.DataFrame, outcomes: pd.DataFrame, climate: pd.DataFrame) -> None:
    checks = [
        (
            "harmonized core",
            household,
            "data_use_limit",
            "harmonized_household_core_only_not_for_final_outcome_or_climate_analysis",
        ),
        (
            "financial outcomes",
            outcomes,
            "data_use_limit",
            "outcome_che10_che25_only_not_for_final_sdg382_access_or_climate_analysis",
        ),
        (
            "climate exposure",
            climate,
            "data_use_limit",
            "climate_exposure_admin2_centroid_only_not_for_final_climate_linkage",
        ),
    ]
    for label, frame, column, value in checks:
        if column not in frame.columns or not frame[column].astype(str).str.strip().eq(value).any():
            raise ValueError(f"Input {label} does not carry the expected limited guardrail marker.")


def build_output(household: pd.DataFrame, outcomes: pd.DataFrame, climate: pd.DataFrame) -> pd.DataFrame:
    household = household.copy()
    outcomes = outcomes.copy()
    climate = climate.copy()

    household["merge_admin2_code"] = norm_code(household["admin2_code"])
    household["merge_month"] = norm_month(household["survey_month"])
    outcomes["merge_hhid"] = outcomes["hhid"].astype(str).str.strip()
    household["merge_hhid"] = household["hhid"].astype(str).str.strip()
    climate["merge_admin2_code"] = norm_code(climate["district_code"])
    climate["merge_month"] = norm_month(climate["survey_month"])

    outcome_keep = [
        "merge_hhid",
        "oop_share_total",
        "log_oop_plus_one",
        "che10_total_budget",
        "che25_total_budget",
        "positive_oop",
        "sdg382_ready",
        "access_outcome_ready",
        "composite_uhc_ready",
    ]
    micro = household.merge(outcomes[[c for c in outcome_keep if c in outcomes.columns]], on="merge_hhid", how="left", validate="one_to_one")

    climate_keep = [
        "merge_admin2_code",
        "merge_month",
        "district_code",
        "district_name",
        "window_months",
        "start_date",
        "end_date",
        "n_days",
        "precip_total_mm",
        "precip_mean_mm_day",
        "precip_within_candidate_z",
        "precip_within_candidate_percentile",
        "temp_mean_c",
        "temp_max_c",
        "temp_min_c",
        "temp_within_candidate_z",
        "temp_within_candidate_percentile",
        "diagnostic_low_rain_z_le_m1",
        "diagnostic_severe_low_rain_z_le_m15",
        "diagnostic_extreme_wet_z_ge_15",
        "diagnostic_heat_z_ge_1",
        "diagnostic_extreme_heat_z_ge_15",
        "diagnostic_combined_climate_stress",
        "source",
        "boundary_source",
        "boundary_year",
        "climate_exposure_scope",
        "primary_chirps_ready",
        "primary_era5_ready",
        "historical_baseline_ready",
    ]
    linked = micro.merge(climate[[c for c in climate_keep if c in climate.columns]], on=["merge_admin2_code", "merge_month"], how="left", validate="many_to_many")

    out = pd.DataFrame(index=linked.index)
    direct_map = {
        "country": "country",
        "survey_name": "survey_name",
        "wave": "wave",
        "idno": "idno",
        "survey_year": "survey_year",
        "survey_month": "survey_month",
        "interview_date": "interview_date",
        "hhid": "hhid",
        "household_weight": "household_weight",
        "strata": "strata",
        "psu": "psu",
        "admin1": "admin1",
        "admin2": "admin2",
        "admin2_code": "admin2_code",
        "district_code": "district_code",
        "district_name": "district_name",
        "cluster_id": "cluster_id",
        "geolocation_quality": "geolocation_quality",
        "rural": "rural",
        "household_size": "household_size",
        "children_under_5": "children_under_5",
        "children_under_15": "children_under_15",
        "elderly_60_plus": "elderly_60_plus",
        "elderly_65_plus": "elderly_65_plus",
        "hh_head_sex": "hh_head_sex",
        "hh_head_age": "hh_head_age",
        "agriculture_livelihood": "agriculture_livelihood",
        "health_insurance": "health_insurance",
        "total_consumption": "total_consumption",
        "oop_health_expenditure": "oop_health_expenditure",
        "oop_share_total": "oop_share_total",
        "log_oop_plus_one": "log_oop_plus_one",
        "che10_total_budget": "che10_total_budget",
        "che25_total_budget": "che25_total_budget",
        "positive_oop": "positive_oop",
        "window_months": "window_months",
        "start_date": "start_date",
        "end_date": "end_date",
        "n_days": "n_days",
        "precip_total_mm": "precip_total_mm",
        "precip_mean_mm_day": "precip_mean_mm_day",
        "precip_within_candidate_z": "precip_within_candidate_z",
        "precip_within_candidate_percentile": "precip_within_candidate_percentile",
        "temp_mean_c": "temp_mean_c",
        "temp_max_c": "temp_max_c",
        "temp_min_c": "temp_min_c",
        "temp_within_candidate_z": "temp_within_candidate_z",
        "temp_within_candidate_percentile": "temp_within_candidate_percentile",
        "diagnostic_low_rain_z_le_m1": "diagnostic_low_rain_z_le_m1",
        "diagnostic_severe_low_rain_z_le_m15": "diagnostic_severe_low_rain_z_le_m15",
        "diagnostic_extreme_wet_z_ge_15": "diagnostic_extreme_wet_z_ge_15",
        "diagnostic_heat_z_ge_1": "diagnostic_heat_z_ge_1",
        "diagnostic_extreme_heat_z_ge_15": "diagnostic_extreme_heat_z_ge_15",
        "diagnostic_combined_climate_stress": "diagnostic_combined_climate_stress",
        "boundary_source": "boundary_source",
        "boundary_year": "boundary_year",
        "climate_exposure_scope": "climate_exposure_scope",
        "primary_chirps_ready": "primary_chirps_ready",
        "primary_era5_ready": "primary_era5_ready",
        "historical_baseline_ready": "historical_baseline_ready",
        "sdg382_ready": "sdg382_ready",
        "access_outcome_ready": "access_outcome_ready",
        "composite_uhc_ready": "composite_uhc_ready",
    }
    for target, source in direct_map.items():
        out[target] = linked[source] if source in linked.columns else ""
    out["climate_source"] = linked["source"] if "source" in linked.columns else "NASA POWER daily point API fallback"
    out["climate_linked_scope"] = SCOPE
    out["data_use_limit"] = DATA_USE_LIMIT
    out["limited_climate_linked_write_ready"] = "1"
    out["climate_linkage_ready"] = "0"
    out["descriptive_ready"] = "0"
    out["predictive_ml_ready"] = "0"
    out["reduced_form_ready"] = "0"
    out["robustness_ready"] = "0"
    out["final_analysis_ready"] = "0"
    out["promotion_status"] = PROMOTION_STATUS
    out["blocking_reason"] = blocking_reason()
    for column in OUTPUT_COLUMNS:
        if column not in out.columns:
            out[column] = ""
    return out[OUTPUT_COLUMNS]


def promotion_audit(output: pd.DataFrame, expected_rows: int) -> list[dict[str, Any]]:
    rows = len(output)
    climate_rows = min(nonmissing(output, "precip_total_mm"), nonmissing(output, "temp_mean_c"))
    unmatched = rows - climate_rows
    return [
        {
            "gate_id": "limited_inputs",
            "gate_label": "Limited core, financial outcomes, and climate exposure inputs",
            "status": "complete_limited_inputs",
            "rows_checked": expected_rows,
            "rows_passing": rows,
            "rows_blocked": 0,
            "evidence": f"expected_rows={expected_rows}; output_rows={rows}",
            "output_artifact": "data/climate_linked_household.csv",
            "next_action": "Use only as a limited linkage diagnostic.",
        },
        {
            "gate_id": "linkage_coverage",
            "gate_label": "Admin2-month-window linkage coverage",
            "status": "complete_limited_linkage" if unmatched == 0 else "partial_limited_linkage",
            "rows_checked": rows,
            "rows_passing": climate_rows,
            "rows_blocked": unmatched,
            "evidence": f"climate_value_rows={climate_rows}; unmatched_rows={unmatched}",
            "output_artifact": "data/climate_linked_household.csv",
            "next_action": "Verify historical boundaries/GPS before final climate linkage.",
        },
        {
            "gate_id": "outcome_scope",
            "gate_label": "Limited CHE-only outcome scope",
            "status": "blocked_sdg_access_composite",
            "rows_checked": rows,
            "rows_passing": 0,
            "rows_blocked": rows,
            "evidence": "sdg382_ready=0; access_outcome_ready=0; composite_uhc_ready=0",
            "output_artifact": "",
            "next_action": "Resolve SDG/access/composite outcome gates before UHC-failure claims.",
        },
        {
            "gate_id": "climate_source_baseline",
            "gate_label": "Primary climate sources and historical baselines",
            "status": "blocked_primary_sources_and_baseline",
            "rows_checked": rows,
            "rows_passing": 0,
            "rows_blocked": rows,
            "evidence": "primary_chirps_ready=0; primary_era5_ready=0; historical_baseline_ready=0",
            "output_artifact": "",
            "next_action": "Extract CHIRPS/ERA5 and accepted historical baselines before shock interpretation.",
        },
        {
            "gate_id": "downstream_models",
            "gate_label": "Descriptive, predictive, causal, and robustness readiness",
            "status": "blocked_not_analysis_ready",
            "rows_checked": rows,
            "rows_passing": 0,
            "rows_blocked": rows,
            "evidence": "descriptive_ready=0; predictive_ml_ready=0; reduced_form_ready=0; robustness_ready=0; final_analysis_ready=0",
            "output_artifact": "",
            "next_action": "Keep descriptive diagnostics and models blocked until final linked inputs pass.",
        },
    ]


def summary_rows(output: pd.DataFrame, household_rows: int, climate_rows: int, audit_rows: list[dict[str, Any]]) -> list[dict[str, str]]:
    rows = len(output)
    expected = household_rows * int(output["window_months"].nunique()) if rows else 0
    climate_value_rows = min(nonmissing(output, "precip_total_mm"), nonmissing(output, "temp_mean_c"))
    return [
        {"metric": "alb2002_limited_climate_linked_promotion_audit_rows", "value": str(len(audit_rows)), "interpretation": "Rows in the limited climate-linked promotion audit."},
        {"metric": "alb2002_limited_climate_linked_rows", "value": str(rows), "interpretation": "Rows written to data/climate_linked_household.csv."},
        {"metric": "alb2002_limited_climate_linked_household_rows", "value": str(output["hhid"].nunique() if rows else 0), "interpretation": "Distinct households represented."},
        {"metric": "alb2002_limited_climate_linked_window_rows", "value": str(output["window_months"].nunique() if rows else 0), "interpretation": "Distinct exposure windows per household."},
        {"metric": "alb2002_limited_climate_linked_expected_rows", "value": str(expected), "interpretation": "Expected rows from household rows times windows."},
        {"metric": "alb2002_limited_climate_linked_source_household_rows", "value": str(household_rows), "interpretation": "Rows in the limited harmonized household core."},
        {"metric": "alb2002_limited_climate_linked_source_climate_rows", "value": str(climate_rows), "interpretation": "Rows in the limited climate exposure file."},
        {"metric": "alb2002_limited_climate_linked_climate_value_rows", "value": str(climate_value_rows), "interpretation": "Rows with nonmissing precipitation and temperature values."},
        {"metric": "alb2002_limited_climate_linked_unmatched_rows", "value": str(rows - climate_value_rows), "interpretation": "Rows without linked climate values."},
        {"metric": "alb2002_limited_climate_linked_che10_rows", "value": str(numeric_sum(output, "che10_total_budget")), "interpretation": "Long rows carrying CHE10 outcome."},
        {"metric": "alb2002_limited_climate_linked_che25_rows", "value": str(numeric_sum(output, "che25_total_budget")), "interpretation": "Long rows carrying CHE25 outcome."},
        {"metric": "alb2002_limited_climate_linked_combined_stress_rows", "value": str(numeric_sum(output, "diagnostic_combined_climate_stress")), "interpretation": "Long rows with diagnostic combined climate-stress flag."},
        {"metric": "alb2002_limited_climate_linked_limited_data_write_ready_rows", "value": str(rows), "interpretation": "Rows allowed in data/ only under limited climate-linked scope."},
        {"metric": "alb2002_limited_climate_linked_sdg382_ready_rows", "value": "0", "interpretation": "Rows ready for SDG 3.8.2."},
        {"metric": "alb2002_limited_climate_linked_access_ready_rows", "value": "0", "interpretation": "Rows ready for access outcomes."},
        {"metric": "alb2002_limited_climate_linked_primary_chirps_ready_rows", "value": "0", "interpretation": "Rows with primary CHIRPS extraction."},
        {"metric": "alb2002_limited_climate_linked_primary_era5_ready_rows", "value": "0", "interpretation": "Rows with primary ERA5 extraction."},
        {"metric": "alb2002_limited_climate_linked_historical_baseline_ready_rows", "value": "0", "interpretation": "Rows with historical climate baseline."},
        {"metric": "alb2002_limited_climate_linked_climate_linkage_ready_rows", "value": "0", "interpretation": "Rows ready for final climate linkage."},
        {"metric": "alb2002_limited_climate_linked_descriptive_ready_rows", "value": "0", "interpretation": "Rows ready for promoted descriptive diagnostics."},
        {"metric": "alb2002_limited_climate_linked_predictive_ml_ready_rows", "value": "0", "interpretation": "Rows ready for predictive ML."},
        {"metric": "alb2002_limited_climate_linked_reduced_form_ready_rows", "value": "0", "interpretation": "Rows ready for reduced-form estimation."},
        {"metric": "alb2002_limited_climate_linked_robustness_ready_rows", "value": "0", "interpretation": "Rows ready for robustness checks."},
        {"metric": "alb2002_limited_climate_linked_final_analysis_ready_rows", "value": "0", "interpretation": "Rows ready for final empirical analysis."},
        {"metric": "alb2002_limited_climate_linked_current_decision", "value": DECISION, "interpretation": "Current limited climate-linked promotion decision."},
        {"metric": "alb2002_limited_climate_linked_data_use_limit", "value": DATA_USE_LIMIT, "interpretation": "Guardrail embedded in every output row."},
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
        f"""# ALB_2002 Limited Climate-Linked Promotion

Status: limited household-window climate-linked file promoted. This writes `data/climate_linked_household.csv` by joining the limited ALB_2002 harmonized core, limited CHE10/CHE25 outcomes, and limited NASA POWER admin2-centroid exposure windows.

The file is not descriptive-ready, model-ready, causal-ready, policy-ready, or final-analysis-ready.

## Summary

{markdown_table(summary, ["metric", "value", "interpretation"])}

## Gate Audit

{markdown_table(audit_rows, ["gate_id", "status", "rows_passing", "rows_blocked", "next_action"])}

## Guardrails

- Every row carries `climate_linked_scope={SCOPE}`.
- Every row carries `data_use_limit={DATA_USE_LIMIT}`.
- `climate_linkage_ready`, `descriptive_ready`, `predictive_ml_ready`, `reduced_form_ready`, `robustness_ready`, and `final_analysis_ready` remain zero.

## Machine-Readable Outputs

- `data/climate_linked_household.csv`
- `temp/climate_merge_audit.csv`
- `temp/alb2002_limited_climate_linked_promotion_audit.csv`
- `result/alb2002_limited_climate_linked_promotion_summary.csv`
""",
        encoding="utf-8",
    )


def main() -> None:
    ensure_dirs()
    household = read(HOUSEHOLD_PATH)
    outcomes = read(OUTCOME_PATH)
    climate = read(CLIMATE_PATH)
    require_markers(household, outcomes, climate)
    output = build_output(household, outcomes, climate)
    expected_rows = len(household) * (output["window_months"].nunique() if len(output) else 0)
    audit_rows = promotion_audit(output, expected_rows)
    summary = summary_rows(output, len(household), len(climate), audit_rows)

    output.to_csv(OUTPUT_PATH, index=False, encoding="utf-8-sig")
    write_csv(
        CLIMATE_MERGE_AUDIT_PATH,
        [
            {
                "check": "climate_merge",
                "status": "complete_limited_climate_linked_diagnostic",
                "detail": "Limited ALB_2002 CHE outcomes linked to limited NASA POWER admin2-centroid exposure windows; final analysis remains blocked.",
                "microdata_path": "data/harmonized_household.csv; data/household_outcomes.csv",
                "climate_path": "data/climate_exposures_nasa_power.csv",
                "rows_microdata": len(household),
                "rows_climate": len(climate),
                "rows_output": len(output),
                "output_path": "data/climate_linked_household.csv",
            }
        ],
        CLIMATE_MERGE_AUDIT_COLUMNS,
    )
    write_csv(PROMOTION_AUDIT_PATH, audit_rows, PROMOTION_AUDIT_COLUMNS)
    write_csv(SUMMARY_PATH, summary, SUMMARY_COLUMNS)
    write_report(summary, audit_rows)
    append_log(TEMP_DIR / "audit_log.md", f"Promoted limited ALB_2002 climate-linked rows={len(output)} decision={DECISION}.")
    print(f"Promoted limited ALB_2002 climate-linked rows={len(output)} decision={DECISION}.")


if __name__ == "__main__":
    main()
