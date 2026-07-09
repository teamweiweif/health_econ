from __future__ import annotations

import csv
import math
from typing import Any

import pandas as pd

from common import REPORT_DIR, RESULT_DIR, TEMP_DIR, append_log, ensure_dirs, write_csv


ANALYSIS_CANDIDATE_PATH = TEMP_DIR / "alb2002_analysis_candidate_dataset.csv"
UHC_COMPOSITE_PATH = TEMP_DIR / "alb2002_uhc_composite_candidate_outcomes.csv"
CLIMATE_SHOCK_PATH = TEMP_DIR / "alb2002_climate_shock_candidate_exposures.csv"
ANALYSIS_SUMMARY_PATH = RESULT_DIR / "alb2002_analysis_candidate_readiness_summary.csv"
UHC_SUMMARY_PATH = RESULT_DIR / "alb2002_uhc_composite_candidate_summary.csv"
SHOCK_SUMMARY_PATH = RESULT_DIR / "alb2002_climate_shock_candidate_summary.csv"

LINKED_PATH = TEMP_DIR / "alb2002_climate_outcome_linked_candidate.csv"
LINEAGE_PATH = TEMP_DIR / "alb2002_climate_outcome_linked_candidate_lineage.csv"
AUDIT_PATH = RESULT_DIR / "alb2002_climate_outcome_linked_candidate_audit.csv"
SUMMARY_PATH = RESULT_DIR / "alb2002_climate_outcome_linked_candidate_summary.csv"
REPORT_PATH = REPORT_DIR / "alb2002_climate_outcome_linked_candidate_audit.md"

DECISION = "blocked_alb2002_climate_outcome_linked_candidate_not_promoted_due_recipe_outcome_geography_source_baseline_gates"
PROMOTION_STATUS = "temp_only_climate_outcome_linked_candidate_not_promoted"

LINKED_COLUMNS = [
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
    "children_under5",
    "children_under15",
    "elderly_60plus",
    "elderly_65plus",
    "head_sex",
    "head_age",
    "agriculture_livelihood",
    "health_insurance_candidate",
    "total_consumption_monthly_candidate",
    "oop_health_expenditure_monthly_candidate",
    "oop_share_total_budget_candidate",
    "che10_total_budget_candidate",
    "che25_total_budget_candidate",
    "positive_oop_candidate",
    "illness_or_injury_need_candidate",
    "delayed_or_unmet_care_candidate",
    "forgone_care_cost_barrier_candidate",
    "forgone_care_distance_barrier_candidate",
    "forgone_care_supply_barrier_candidate",
    "composite_any_access_barrier_candidate",
    "composite_cost_barrier_candidate",
    "money_raising_any_candidate",
    "uhc_double_failure_che10_or_access_candidate",
    "uhc_double_failure_che25_or_access_candidate",
    "financial_only_che10_candidate",
    "access_only_vs_che10_candidate",
    "both_che10_access_candidate",
    "financial_only_che25_candidate",
    "access_only_vs_che25_candidate",
    "both_che25_access_candidate",
    "coping_health_cost_candidate",
    "financial_denominator_valid",
    "access_denominator_valid",
    "composite_denominator_valid",
    "window_months",
    "start_date",
    "end_date",
    "n_days",
    "precip_total_mm",
    "precip_within_candidate_z",
    "precip_within_candidate_percentile",
    "temp_mean_c",
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
    "climate_source",
    "boundary_source",
    "boundary_year",
    "exposure_quality_flag",
    "primary_chirps_ready",
    "primary_era5_ready",
    "historical_baseline_ready",
    "climate_linkage_ready",
    "outcome_promotion_ready",
    "harmonized_recipe_ready",
    "data_write_ready",
    "candidate_dataset_status",
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


def safe_int(value: Any) -> int:
    try:
        return int(float(str(value).strip()))
    except (TypeError, ValueError):
        return 0


def fmt(value: Any) -> str:
    number = safe_float(value)
    if math.isnan(number):
        return "" if value is None else str(value)
    if number.is_integer():
        return str(int(number))
    return f"{number:.6g}"


def hhid_key(series: pd.Series) -> pd.Series:
    return series.astype(str).str.strip().str.replace(r"\.0$", "", regex=True)


def numeric(frame: pd.DataFrame, column: str) -> pd.Series:
    return pd.to_numeric(frame[column], errors="coerce") if column in frame.columns else pd.Series(pd.NA, index=frame.index)


def nonmissing_count(frame: pd.DataFrame, column: str) -> int:
    if column not in frame.columns:
        return 0
    return int(frame[column].notna().sum() if pd.api.types.is_numeric_dtype(frame[column]) else (frame[column].astype(str).str.strip() != "").sum())


def positive_sum(frame: pd.DataFrame, column: str) -> int:
    return int(numeric(frame, column).fillna(0).sum()) if column in frame.columns else 0


def blocking_reason() -> str:
    return (
        "This household-window linked candidate merges temp-only ALB_2002 analysis/outcome candidates with temp-only "
        "within-candidate climate shock diagnostics. It remains outside data/ because the harmonized recipe, final "
        "outcome promotion, SDG/benchmark checks, verified historical geography, primary CHIRPS/ERA5 sources, and "
        "historical climate baselines have not passed together."
    )


def load_inputs() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    for path in [ANALYSIS_CANDIDATE_PATH, UHC_COMPOSITE_PATH, CLIMATE_SHOCK_PATH]:
        if not path.exists():
            raise FileNotFoundError(f"Missing prerequisite: {path}")
    analysis = pd.read_csv(ANALYSIS_CANDIDATE_PATH, encoding="utf-8-sig")
    uhc = pd.read_csv(UHC_COMPOSITE_PATH, encoding="utf-8-sig")
    shock = pd.read_csv(CLIMATE_SHOCK_PATH, encoding="utf-8-sig")
    return analysis, uhc, shock


def build_linked(analysis: pd.DataFrame, uhc: pd.DataFrame, shock: pd.DataFrame) -> pd.DataFrame:
    analysis = analysis.copy()
    uhc = uhc.copy()
    shock = shock.copy()

    analysis["hhid_key"] = hhid_key(analysis["hhid"])
    uhc["hhid_key"] = hhid_key(uhc["hhid"])
    if analysis["hhid_key"].duplicated().any() or uhc["hhid_key"].duplicated().any():
        raise ValueError("Non-unique household keys in analysis or UHC composite candidate input.")

    analysis["district_code"] = pd.to_numeric(analysis["admin2_code"], errors="coerce").astype("Int64")
    analysis["survey_month"] = pd.to_numeric(analysis["survey_month"], errors="coerce").astype("Int64")
    shock["district_code"] = pd.to_numeric(shock["district_code"], errors="coerce").astype("Int64")
    shock["survey_month"] = pd.to_numeric(shock["survey_month"], errors="coerce").astype("Int64")
    shock["window_months"] = pd.to_numeric(shock["window_months"], errors="coerce").astype("Int64")
    if shock.duplicated(["district_code", "survey_month", "window_months"]).any():
        raise ValueError("Non-unique district-month-window keys in climate shock candidate input.")

    uhc_fields = [
        "hhid_key",
        "composite_any_access_barrier_candidate",
        "composite_cost_barrier_candidate",
        "money_raising_any_candidate",
        "uhc_double_failure_che10_or_access_candidate",
        "uhc_double_failure_che25_or_access_candidate",
        "financial_only_che10_candidate",
        "access_only_vs_che10_candidate",
        "both_che10_access_candidate",
        "financial_only_che25_candidate",
        "access_only_vs_che25_candidate",
        "both_che25_access_candidate",
        "coping_health_cost_candidate",
        "financial_denominator_valid",
        "access_denominator_valid",
        "composite_denominator_valid",
    ]
    drop_overlap = [column for column in uhc_fields if column in analysis.columns and column != "hhid_key"]
    base = analysis.drop(columns=drop_overlap, errors="ignore").merge(
        uhc[uhc_fields],
        on="hhid_key",
        how="inner",
        validate="one_to_one",
    )
    if len(base) != len(analysis) or len(base) != len(uhc):
        raise ValueError(f"Household candidate merge changed row counts: analysis={len(analysis)} uhc={len(uhc)} linked={len(base)}")

    shock_fields = [
        "district_code",
        "survey_month",
        "window_months",
        "district_name",
        "start_date",
        "end_date",
        "n_days",
        "precip_total_mm",
        "precip_within_candidate_z",
        "precip_within_candidate_percentile",
        "temp_mean_c",
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
    ]
    linked = base.merge(
        shock[shock_fields],
        on=["district_code", "survey_month"],
        how="left",
        validate="many_to_many",
    )
    linked["climate_source"] = linked["source"]
    linked["admin2_code"] = linked["admin2_code"].apply(fmt)
    linked["district_code"] = linked["district_code"].apply(fmt)
    linked["survey_month"] = linked["survey_month"].apply(fmt)
    linked["window_months"] = linked["window_months"].apply(fmt)
    linked["outcome_promotion_ready"] = "0"
    linked["harmonized_recipe_ready"] = "0"
    linked["data_write_ready"] = "0"
    linked["candidate_dataset_status"] = "temp_only_household_window_climate_outcome_candidate_not_promoted"
    linked["promotion_status"] = PROMOTION_STATUS
    linked["blocking_reason"] = blocking_reason()
    linked = linked.drop(columns=["hhid_key", "source"], errors="ignore")
    return linked


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


def build_audit(analysis: pd.DataFrame, uhc: pd.DataFrame, shock: pd.DataFrame, linked: pd.DataFrame) -> list[dict[str, str]]:
    household_rows = len(analysis)
    window_rows = int(shock["window_months"].nunique())
    expected_rows = household_rows * window_rows
    matched_rows = nonmissing_count(linked, "window_months")
    distinct_households = linked["hhid"].nunique()
    precip_z = nonmissing_count(linked, "precip_within_candidate_z")
    temp_z = nonmissing_count(linked, "temp_within_candidate_z")
    return [
        audit_row(
            "household_inputs",
            "Analysis and composite UHC household inputs have one row per household",
            "complete_candidate_not_promoted" if len(analysis) == len(uhc) == analysis["hhid"].nunique() == uhc["hhid"].nunique() else "partial_or_failed",
            max(len(analysis), len(uhc)),
            min(len(analysis), len(uhc), analysis["hhid"].nunique(), uhc["hhid"].nunique()),
            f"analysis_rows={len(analysis)}; analysis_unique_hhid={analysis['hhid'].nunique()}; uhc_rows={len(uhc)}; uhc_unique_hhid={uhc['hhid'].nunique()}",
            "Household and outcome candidates are temp-only and not promoted.",
            "Promote only after harmonization, outcome, SDG, benchmark, and climate gates pass.",
        ),
        audit_row(
            "climate_input_keys",
            "Climate shock input has unique district-month-window rows",
            "complete_candidate_not_promoted" if not shock.duplicated(["district_code", "survey_month", "window_months"]).any() else "partial_or_failed",
            len(shock),
            len(shock) - int(shock.duplicated(["district_code", "survey_month", "window_months"]).sum()),
            f"shock_rows={len(shock)}; district_month_cells={shock[['district_code','survey_month']].drop_duplicates().shape[0]}; window_rows={window_rows}; duplicate_key_rows={int(shock.duplicated(['district_code','survey_month','window_months']).sum())}",
            "Climate shock rows are diagnostics from NASA POWER fallback centroids, not accepted climate exposures.",
            "Replace with verified CHIRPS/ERA5 historical-anomaly exposures after geography and baselines pass.",
        ),
        audit_row(
            "household_window_link",
            "Every household links to four diagnostic climate windows",
            "complete_candidate_not_promoted" if len(linked) == expected_rows and matched_rows == expected_rows and distinct_households == household_rows else "partial_or_failed",
            expected_rows,
            min(len(linked), matched_rows),
            f"linked_rows={len(linked)}; expected_rows={expected_rows}; distinct_households={distinct_households}; matched_rows={matched_rows}; unmatched_rows={len(linked) - matched_rows}",
            "The join is mechanically complete but remains an unpromoted stress test.",
            "Do not use this as an analysis dataset until promoted household, outcome, geography, source, and baseline gates pass.",
        ),
        audit_row(
            "outcome_coverage",
            "Candidate outcome fields are available in linked household-window rows",
            "complete_candidate_not_promoted" if nonmissing_count(linked, "uhc_double_failure_che10_or_access_candidate") == len(linked) else "partial_or_failed",
            len(linked),
            nonmissing_count(linked, "uhc_double_failure_che10_or_access_candidate"),
            f"che10_or_access_long_rows={positive_sum(linked, 'uhc_double_failure_che10_or_access_candidate')}; che25_or_access_long_rows={positive_sum(linked, 'uhc_double_failure_che25_or_access_candidate')}; coping_long_rows={positive_sum(linked, 'coping_health_cost_candidate')}; composite_denominator_rows={positive_sum(linked, 'composite_denominator_valid')}",
            "Outcome fields are candidate screens and cannot be interpreted as final UHC failure outcomes.",
            "Resolve OOP/access/SDG/benchmark gates before promoted descriptive or modeling outputs.",
        ),
        audit_row(
            "climate_diagnostic_coverage",
            "Diagnostic shock z-scores and flags are available in linked household-window rows",
            "complete_candidate_not_promoted" if precip_z == len(linked) and temp_z == len(linked) else "partial_or_failed",
            len(linked),
            min(precip_z, temp_z),
            f"precip_z_rows={precip_z}; temp_z_rows={temp_z}; low_rain_long_rows={positive_sum(linked, 'diagnostic_low_rain_z_le_m1')}; extreme_wet_long_rows={positive_sum(linked, 'diagnostic_extreme_wet_z_ge_15')}; extreme_heat_long_rows={positive_sum(linked, 'diagnostic_extreme_heat_z_ge_15')}; combined_stress_long_rows={positive_sum(linked, 'diagnostic_combined_climate_stress')}",
            "Climate diagnostics are within-candidate z-scores, not historical local anomalies or accepted treatments.",
            "Construct primary-source historical climate anomalies before reduced-form or predictive modeling.",
        ),
        audit_row(
            "geography_source_baseline_gates",
            "Climate geography, primary-source, and historical-baseline promotion gates remain closed",
            "blocked",
            len(linked),
            0,
            f"primary_chirps_ready={positive_sum(linked, 'primary_chirps_ready')}; primary_era5_ready={positive_sum(linked, 'primary_era5_ready')}; historical_baseline_ready={positive_sum(linked, 'historical_baseline_ready')}; climate_linkage_ready={positive_sum(linked, 'climate_linkage_ready')}",
            "Verified historical geography, primary CHIRPS/ERA5 extraction, and historical baselines are not accepted.",
            "Keep linked data out of data/ and out of models until these gates pass.",
        ),
        audit_row(
            "promotion",
            "Linked household-window candidate is not promoted to data",
            "blocked",
            len(linked),
            0,
            f"outcome_promotion_ready={positive_sum(linked, 'outcome_promotion_ready')}; harmonized_recipe_ready={positive_sum(linked, 'harmonized_recipe_ready')}; data_write_ready={positive_sum(linked, 'data_write_ready')}; decision={DECISION}",
            blocking_reason(),
            "Do not write data/climate_linked_household.* or estimate models from this candidate.",
        ),
    ]


def lineage_rows() -> list[dict[str, str]]:
    artifacts = "temp/alb2002_analysis_candidate_dataset.csv;temp/alb2002_uhc_composite_candidate_outcomes.csv;temp/alb2002_climate_shock_candidate_exposures.csv"
    rows = [
        ("lineage_001", "household_identity_design_covariates", "hhid;survey_year;survey_month;interview_date;household_weight;strata;psu;demographic covariates", artifacts, "Direct carry-forward from the ALB_2002 joined analysis candidate.", "candidate_not_promoted", "Analysis candidate remains outside data/."),
        ("lineage_002", "district_code_join_key", "admin2_code;district_code;survey_month", artifacts, "Normalize analysis admin2_code to district_code and join climate shocks by district_code and survey_month.", "candidate_not_promoted", "Admin2 is not verified 2001/2002 geography."),
        ("lineage_003", "window_months", "window_months", artifacts, "Expand each household to one row for each linked diagnostic exposure window.", "candidate_not_promoted", "Long household-window rows are a stress-test structure only."),
        ("lineage_004", "candidate_uhc_outcomes", "CHE, access, double-failure, financial-only, access-only, both-failure, coping fields", artifacts, "Carry final temp-only composite UHC candidate fields by hhid.", "candidate_not_promoted", "Outcome promotion gates remain blocked."),
        ("lineage_005", "diagnostic_climate_shock_fields", "precip/temp within-candidate z-scores and diagnostic flags", artifacts, "Carry shock diagnostics by district-month-window.", "candidate_not_promoted", "Diagnostics are not historical anomalies or accepted treatment variables."),
        ("lineage_006", "promotion_gate_fields", "primary_chirps_ready;primary_era5_ready;historical_baseline_ready;climate_linkage_ready;data_write_ready", artifacts, "Force all promotion/data-write readiness fields to zero.", "blocked", "Linked candidate cannot be used as promoted analysis data."),
        ("lineage_007", "blocking_reason", "upstream gate decisions", artifacts, "Record fail-closed interpretation in every linked row.", "blocked", "Recipe, outcome, geography, source, and baseline gates have not passed together."),
    ]
    return [
        {
            "lineage_id": row[0],
            "derived_field": row[1],
            "source_fields": row[2],
            "source_artifacts": row[3],
            "formula_or_rule": row[4],
            "status": row[5],
            "blocking_reason": row[6],
        }
        for row in rows
    ]


def summary_row(metric: str, value: Any, interpretation: str) -> dict[str, str]:
    return {"metric": metric, "value": fmt(value), "interpretation": interpretation}


def build_summary(linked: pd.DataFrame, audit: list[dict[str, str]], lineage: list[dict[str, str]]) -> list[dict[str, str]]:
    analysis_summary = read_csv_dicts(ANALYSIS_SUMMARY_PATH)
    uhc_summary = read_csv_dicts(UHC_SUMMARY_PATH)
    shock_summary = read_csv_dicts(SHOCK_SUMMARY_PATH)
    household_rows = linked["hhid"].nunique()
    return [
        summary_row("alb2002_climate_outcome_linked_candidate_rows", len(linked), "Temp-only long household-window climate/outcome candidate rows."),
        summary_row("alb2002_climate_outcome_linked_candidate_household_rows", household_rows, "Distinct ALB_2002 households represented."),
        summary_row("alb2002_climate_outcome_linked_candidate_window_rows", linked["window_months"].nunique(), "Distinct diagnostic exposure windows linked per household."),
        summary_row("alb2002_climate_outcome_linked_candidate_district_month_cells", linked[["district_code", "survey_month"]].drop_duplicates().shape[0], "District-month cells represented after linkage."),
        summary_row("alb2002_climate_outcome_linked_candidate_lineage_rows", len(lineage), "Lineage rows for the linked climate/outcome candidate."),
        summary_row("alb2002_climate_outcome_linked_candidate_audit_rows", len(audit), "Audit rows for linkage integrity and promotion gates."),
        summary_row("alb2002_climate_outcome_linked_candidate_source_analysis_rows", metric_value(analysis_summary, "alb2002_analysis_candidate_rows"), "Source joined analysis-candidate rows consumed."),
        summary_row("alb2002_climate_outcome_linked_candidate_source_uhc_rows", metric_value(uhc_summary, "alb2002_uhc_composite_candidate_household_rows"), "Source composite UHC candidate rows consumed."),
        summary_row("alb2002_climate_outcome_linked_candidate_source_shock_rows", metric_value(shock_summary, "alb2002_climate_shock_candidate_exposure_rows"), "Source climate shock diagnostic rows consumed."),
        summary_row("alb2002_climate_outcome_linked_candidate_expected_rows", household_rows * linked["window_months"].nunique(), "Expected rows if every household has all diagnostic windows."),
        summary_row("alb2002_climate_outcome_linked_candidate_unmatched_rows", int(linked["window_months"].astype(str).str.strip().eq("").sum()), "Rows with no linked climate window; should remain zero."),
        summary_row("alb2002_climate_outcome_linked_candidate_precip_z_rows", nonmissing_count(linked, "precip_within_candidate_z"), "Linked rows with diagnostic rainfall z-scores."),
        summary_row("alb2002_climate_outcome_linked_candidate_temp_z_rows", nonmissing_count(linked, "temp_within_candidate_z"), "Linked rows with diagnostic temperature z-scores."),
        summary_row("alb2002_climate_outcome_linked_candidate_low_rain_rows", positive_sum(linked, "diagnostic_low_rain_z_le_m1"), "Linked household-window rows with diagnostic low-rain flag."),
        summary_row("alb2002_climate_outcome_linked_candidate_extreme_wet_rows", positive_sum(linked, "diagnostic_extreme_wet_z_ge_15"), "Linked household-window rows with diagnostic extreme-wet flag."),
        summary_row("alb2002_climate_outcome_linked_candidate_extreme_heat_rows", positive_sum(linked, "diagnostic_extreme_heat_z_ge_15"), "Linked household-window rows with diagnostic extreme-heat flag."),
        summary_row("alb2002_climate_outcome_linked_candidate_combined_stress_rows", positive_sum(linked, "diagnostic_combined_climate_stress"), "Linked household-window rows with any diagnostic combined-stress flag."),
        summary_row("alb2002_climate_outcome_linked_candidate_che10_or_access_rows", positive_sum(linked, "uhc_double_failure_che10_or_access_candidate"), "Long rows carrying CHE10-or-access UHC candidate flag."),
        summary_row("alb2002_climate_outcome_linked_candidate_che25_or_access_rows", positive_sum(linked, "uhc_double_failure_che25_or_access_candidate"), "Long rows carrying CHE25-or-access UHC candidate flag."),
        summary_row("alb2002_climate_outcome_linked_candidate_both_che10_access_rows", positive_sum(linked, "both_che10_access_candidate"), "Long rows carrying both CHE10 and access-barrier candidate flag."),
        summary_row("alb2002_climate_outcome_linked_candidate_coping_rows", positive_sum(linked, "coping_health_cost_candidate"), "Long rows carrying health-cost coping candidate flag."),
        summary_row("alb2002_climate_outcome_linked_candidate_primary_chirps_ready_rows", positive_sum(linked, "primary_chirps_ready"), "Rows with primary CHIRPS accepted; intentionally zero."),
        summary_row("alb2002_climate_outcome_linked_candidate_primary_era5_ready_rows", positive_sum(linked, "primary_era5_ready"), "Rows with primary ERA5 accepted; intentionally zero."),
        summary_row("alb2002_climate_outcome_linked_candidate_historical_baseline_ready_rows", positive_sum(linked, "historical_baseline_ready"), "Rows with historical baseline accepted; intentionally zero."),
        summary_row("alb2002_climate_outcome_linked_candidate_climate_linkage_ready_rows", positive_sum(linked, "climate_linkage_ready"), "Rows ready for promoted climate linkage; intentionally zero."),
        summary_row("alb2002_climate_outcome_linked_candidate_outcome_promotion_ready_rows", positive_sum(linked, "outcome_promotion_ready"), "Rows ready for promoted outcomes; intentionally zero."),
        summary_row("alb2002_climate_outcome_linked_candidate_harmonized_recipe_ready_rows", positive_sum(linked, "harmonized_recipe_ready"), "Rows ready for harmonized recipe promotion; intentionally zero."),
        summary_row("alb2002_climate_outcome_linked_candidate_data_write_ready_rows", positive_sum(linked, "data_write_ready"), "Rows allowed to be written to data/; intentionally zero."),
        summary_row("alb2002_climate_outcome_linked_candidate_current_decision", DECISION, "Current fail-closed linked climate/outcome candidate decision."),
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
        f"""# ALB_2002 Climate Outcome Linked Candidate Audit

Status: temp-only household-window linkage audit. This joins the ALB_2002 analysis and composite UHC outcome candidates to the within-candidate climate shock diagnostics by district and survey month. It does not write `data/`, does not create an accepted climate-linked analytical dataset, and does not support descriptive, predictive, or causal claims.

## Summary

| Metric | Value | Interpretation |
|---|---:|---|
{summary_table}

## Linkage Audit

{markdown_rows(audit, ['check_id', 'status', 'rows_checked', 'passing_rows', 'promotion_ready_rows', 'evidence', 'blocking_reason'])}

## Lineage

{markdown_rows(lineage, ['derived_field', 'source_fields', 'formula_or_rule', 'status', 'blocking_reason'])}

## Interpretation

- The mechanical household-window linkage is complete for ALB_2002 candidate rows.
- The linked climate fields are diagnostic within-candidate z-scores, not historical anomalies or accepted climate-shock treatments.
- The linked outcome fields are temp-only UHC candidates, not promoted final outcomes.
- Harmonized-recipe-ready, outcome-promotion-ready, climate-linkage-ready, and data-write-ready rows remain zero.

## Machine-Readable Outputs

- `temp/alb2002_climate_outcome_linked_candidate.csv`
- `temp/alb2002_climate_outcome_linked_candidate_lineage.csv`
- `result/alb2002_climate_outcome_linked_candidate_audit.csv`
- `result/alb2002_climate_outcome_linked_candidate_summary.csv`
""",
        encoding="utf-8",
    )


def main() -> None:
    ensure_dirs()
    analysis, uhc, shock = load_inputs()
    linked = build_linked(analysis, uhc, shock)
    audit = build_audit(analysis, uhc, shock, linked)
    lineage = lineage_rows()
    summary = build_summary(linked, audit, lineage)
    write_csv(LINKED_PATH, linked.fillna("").to_dict("records"), LINKED_COLUMNS)
    write_csv(LINEAGE_PATH, lineage, LINEAGE_COLUMNS)
    write_csv(AUDIT_PATH, audit, AUDIT_COLUMNS)
    write_csv(SUMMARY_PATH, summary, SUMMARY_COLUMNS)
    write_report(summary, audit, lineage)
    append_log(TEMP_DIR / "audit_log.md", f"Built ALB_2002 climate outcome linked candidate rows={len(linked)} decision={DECISION}.")
    print(f"ALB_2002 climate outcome linked candidate rows={len(linked)} decision={DECISION}.")


if __name__ == "__main__":
    main()
