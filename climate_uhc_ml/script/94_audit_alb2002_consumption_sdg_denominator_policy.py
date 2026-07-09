from __future__ import annotations

import csv
import math
from pathlib import Path
from typing import Any

import pandas as pd

from common import REPORT_DIR, RESULT_DIR, TEMP_DIR, append_log, ensure_dirs, write_csv


IDNO = "ALB_2002_LSMS_v01_M"
COUNTRY = "Albania"
SURVEY_NAME = "Living Standards Measurement Survey 2002"
WAVE = "2002"

CANDIDATE_PATH = TEMP_DIR / "alb2002_household_core_candidate.csv"
LINEAGE_PATH = TEMP_DIR / "alb2002_household_core_lineage.csv"
SDG382_SUMMARY_PATH = RESULT_DIR / "sdg382_denominator_summary.csv"
OOP_POLICY_SUMMARY_PATH = RESULT_DIR / "alb2002_oop_aggregation_policy_summary.csv"
SKIP_MISSING_SUMMARY_PATH = RESULT_DIR / "alb2002_skip_missing_semantics_summary.csv"
ACCESS_NEED_SUMMARY_PATH = RESULT_DIR / "alb2002_access_need_denominator_policy_summary.csv"
MINIMUM_RECIPE_SUMMARY_PATH = RESULT_DIR / "alb2002_minimum_recipe_promotion_summary.csv"
DISTRICT_CROSSWALK_SUMMARY_PATH = RESULT_DIR / "alb2002_district_climate_crosswalk_summary.csv"

AUDIT_PATH = TEMP_DIR / "alb2002_consumption_sdg_denominator_policy_audit.csv"
SUMMARY_PATH = RESULT_DIR / "alb2002_consumption_sdg_denominator_policy_summary.csv"
REPORT_PATH = REPORT_DIR / "alb2002_consumption_sdg_denominator_policy_audit.md"

DECISION = "blocked_alb2002_consumption_sdg_denominator_policy_not_sdg_ready"
NO_PROMOTION = "not_promoted_denominator_policy_audit_only"

AUDIT_COLUMNS = [
    "country",
    "survey_name",
    "wave",
    "idno",
    "component_id",
    "component_family",
    "evidence_status",
    "source_artifacts",
    "observed_rows",
    "ready_rows",
    "blocked_rows",
    "diagnostic_value",
    "required_resolution",
    "promotion_status",
    "blocking_reason",
    "next_action",
]
SUMMARY_COLUMNS = ["metric", "value", "interpretation"]


def read_csv_dicts(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def metric_value(rows: list[dict[str, str]], metric: str, default: str = "0") -> str:
    return next((row.get("value", default) for row in rows if row.get("metric") == metric), default)


def fmt(value: Any) -> str:
    if value is None:
        return ""
    try:
        if pd.isna(value):
            return ""
    except TypeError:
        pass
    if isinstance(value, float):
        if not math.isfinite(value):
            return ""
        if value.is_integer():
            return str(int(value))
        return f"{value:.6g}"
    return str(value)


def int_text(value: Any) -> str:
    try:
        return str(int(float(str(value).strip())))
    except (TypeError, ValueError):
        return "0"


def numeric(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series, errors="coerce")


def stats(series: pd.Series) -> dict[str, str]:
    valid = numeric(series).replace([float("inf"), float("-inf")], pd.NA).dropna()
    if valid.empty:
        return {"nonmissing": "0", "positive": "0", "zero": "0", "negative": "0", "min": "", "p50": "", "p95": "", "max": "", "mean": ""}
    return {
        "nonmissing": str(int(valid.shape[0])),
        "positive": str(int((valid > 0).sum())),
        "zero": str(int((valid == 0).sum())),
        "negative": str(int((valid < 0).sum())),
        "min": fmt(float(valid.min())),
        "p50": fmt(float(valid.quantile(0.50))),
        "p95": fmt(float(valid.quantile(0.95))),
        "max": fmt(float(valid.max())),
        "mean": fmt(float(valid.mean())),
    }


def weighted_denominator(weight: pd.Series, mask: pd.Series) -> str:
    valid = mask.fillna(False).astype(bool) & weight.notna() & (weight > 0)
    if not valid.any():
        return "0"
    return fmt(float(weight.loc[valid].sum()))


def che_count_and_rate(oop: pd.Series, denominator: pd.Series, threshold: float) -> tuple[str, str]:
    valid = denominator.notna() & (denominator > 0)
    if not valid.any():
        return "0", ""
    share = numeric(oop).fillna(0) / denominator
    event = valid & (share > threshold)
    return str(int(event.sum())), fmt(float(event.sum() / valid.sum()))


def lineage_value(lineage: list[dict[str, str]], candidate_column: str, field: str) -> str:
    for row in lineage:
        if row.get("candidate_column") == candidate_column:
            return row.get(field, "")
    return ""


def audit_row(
    component_id: str,
    component_family: str,
    evidence_status: str,
    source_artifacts: list[str],
    observed_rows: Any,
    diagnostic_value: str,
    required_resolution: str,
    next_action: str,
    ready_rows: Any = 0,
) -> dict[str, str]:
    observed_int = int(int_text(observed_rows))
    ready_int = int(int_text(ready_rows))
    return {
        "country": COUNTRY,
        "survey_name": SURVEY_NAME,
        "wave": WAVE,
        "idno": IDNO,
        "component_id": component_id,
        "component_family": component_family,
        "evidence_status": evidence_status,
        "source_artifacts": ";".join(source_artifacts),
        "observed_rows": str(observed_int),
        "ready_rows": str(ready_int),
        "blocked_rows": str(max(observed_int - ready_int, 0)),
        "diagnostic_value": diagnostic_value,
        "required_resolution": required_resolution,
        "promotion_status": NO_PROMOTION,
        "blocking_reason": (
            "Observed ALB_2002 denominator evidence is not sufficient for SDG 3.8.2 or final CHE outcome construction until unit, "
            "period, price basis, SPL, PPP/CPI, OOP alignment, benchmarks, and promotion gates pass together."
        ),
        "next_action": next_action,
    }


def build_rows(candidate: pd.DataFrame) -> list[dict[str, str]]:
    lineage = read_csv_dicts(LINEAGE_PATH)
    sdg_summary = read_csv_dicts(SDG382_SUMMARY_PATH)
    oop_summary = read_csv_dicts(OOP_POLICY_SUMMARY_PATH)
    skip_summary = read_csv_dicts(SKIP_MISSING_SUMMARY_PATH)
    access_summary = read_csv_dicts(ACCESS_NEED_SUMMARY_PATH)
    recipe_summary = read_csv_dicts(MINIMUM_RECIPE_SUMMARY_PATH)
    crosswalk_summary = read_csv_dicts(DISTRICT_CROSSWALK_SUMMARY_PATH)

    total = numeric(candidate["total_consumption"])
    weight = numeric(candidate["household_weight"])
    household_size = numeric(candidate["household_size"])
    oop_4w = numeric(candidate["oop_4w_sum_unreviewed"]).fillna(0)
    oop_12m = numeric(candidate["oop_12m_sum_unreviewed"]).fillna(0)

    total_stats = stats(total)
    weight_stats = stats(weight)
    size_stats = stats(household_size)
    che10_4w_rows, che10_4w_rate = che_count_and_rate(oop_4w, total, 0.10)
    che25_4w_rows, che25_4w_rate = che_count_and_rate(oop_4w, total, 0.25)
    che10_12m_rows, che10_12m_rate = che_count_and_rate(oop_12m, total, 0.10)
    che25_12m_rows, che25_12m_rate = che_count_and_rate(oop_12m, total, 0.25)
    positive_total = total.notna() & (total > 0)

    total_lineage = (
        f"source_file={lineage_value(lineage, 'total_consumption', 'source_file')}; "
        f"raw_variables={lineage_value(lineage, 'total_consumption', 'raw_variables')}; "
        f"lineage_status={lineage_value(lineage, 'total_consumption', 'status')}"
    )

    return [
        audit_row(
            "source_team_total_consumption_candidate",
            "total_welfare_measure",
            "candidate_values_observed_unit_period_blocked",
            ["temp/alb2002_household_core_candidate.csv", "temp/alb2002_household_core_lineage.csv"],
            total_stats["nonmissing"],
            f"{total_lineage}; positive={total_stats['positive']}; zero={total_stats['zero']}; negative={total_stats['negative']}; min={total_stats['min']}; p50={total_stats['p50']}; p95={total_stats['p95']}; max={total_stats['max']}; mean={total_stats['mean']}",
            "Verify that totcons is the accepted total household consumption aggregate, including unit, reference period, price basis, and whether health spending is included.",
            "Find official ALB_2002 consumption-construction documentation/codebook evidence before accepting total_consumption as a financial-protection denominator.",
        ),
        audit_row(
            "household_size_daily_pc_conversion_candidate",
            "household_size_and_daily_pc_conversion",
            "candidate_values_observed_period_days_blocked",
            ["temp/alb2002_household_core_candidate.csv"],
            size_stats["positive"],
            f"household_size_positive={size_stats['positive']}; min={size_stats['min']}; p50={size_stats['p50']}; p95={size_stats['p95']}; max={size_stats['max']}; total_consumption_positive={total_stats['positive']}",
            "Verify the welfare reference period and exact period-day conversion before deriving per-capita daily welfare for SPL construction.",
            "Document whether the ALB_2002 total consumption aggregate is annual, monthly, four-week, or another period and align it with household size.",
        ),
        audit_row(
            "survey_weight_population_basis_candidate",
            "survey_weights_and_population_basis",
            "candidate_values_observed_design_semantics_blocked",
            ["temp/alb2002_household_core_candidate.csv", "temp/alb2002_household_core_lineage.csv"],
            weight_stats["positive"],
            f"positive_weight_rows={weight_stats['positive']}; min={weight_stats['min']}; p50={weight_stats['p50']}; max={weight_stats['max']}; weighted_positive_total_consumption_denominator={weighted_denominator(weight, positive_total)}",
            "Verify household-weight target population, normalization, and survey-design use before weighted SDG/CHE incidence.",
            "Use official LSMS documentation to confirm the weight semantics and whether strata/PSU fields must be carried into prevalence inference.",
        ),
        audit_row(
            "oop_welfare_period_alignment",
            "oop_health_expenditure_scope",
            "candidate_oop_observed_recall_alignment_blocked",
            ["result/alb2002_oop_aggregation_policy_summary.csv", "result/alb2002_skip_missing_semantics_summary.csv"],
            total_stats["positive"],
            f"oop_policy_rows={metric_value(oop_summary, 'alb2002_oop_aggregation_policy_rows')}; 4w_positive_rows={int((oop_4w > 0).sum())}; 12m_positive_rows={int((oop_12m > 0).sum())}; skipped_positive_rows={metric_value(skip_summary, 'alb2002_skip_missing_payment_positive_when_not_triggered_rows')}; zero_skipped_cells={metric_value(skip_summary, 'alb2002_skip_missing_payment_zero_cells_when_not_triggered')}",
            "Choose and document one OOP numerator scope whose recall period and payment/gift/transport treatment are compatible with the welfare denominator.",
            "Resolve OOP aggregation, skip/missing semantics, and recall-period comparability before treating CHE stress tests as outcome construction.",
        ),
        audit_row(
            "che10_total_consumption_stress_denominator",
            "che_total_budget_stress_test",
            "diagnostic_only_not_outcome_ready",
            ["temp/alb2002_household_core_candidate.csv", "result/alb2002_oop_aggregation_policy_summary.csv"],
            total_stats["positive"],
            f"4w_unreviewed_che10_rows={che10_4w_rows}; 4w_unreviewed_che10_rate={che10_4w_rate}; 12m_unreviewed_che10_rows={che10_12m_rows}; 12m_unreviewed_che10_rate={che10_12m_rate}; policy_max_che10_rate={metric_value(oop_summary, 'alb2002_oop_aggregation_policy_max_che10_rate')}",
            "CHE10 denominator can be stress-tested only after total-consumption and OOP scope are accepted together.",
            "Keep CHE10 as a diagnostic until OOP numerator, denominator unit/period, skip/missing, and recipe gates pass.",
        ),
        audit_row(
            "che25_total_consumption_stress_denominator",
            "che_total_budget_stress_test",
            "diagnostic_only_not_outcome_ready",
            ["temp/alb2002_household_core_candidate.csv", "result/alb2002_oop_aggregation_policy_summary.csv"],
            total_stats["positive"],
            f"4w_unreviewed_che25_rows={che25_4w_rows}; 4w_unreviewed_che25_rate={che25_4w_rate}; 12m_unreviewed_che25_rows={che25_12m_rows}; 12m_unreviewed_che25_rate={che25_12m_rate}; policy_max_che25_rate={metric_value(oop_summary, 'alb2002_oop_aggregation_policy_max_che25_rate')}",
            "CHE25 denominator can be stress-tested only after total-consumption and OOP scope are accepted together.",
            "Keep CHE25 as a diagnostic until OOP numerator, denominator unit/period, skip/missing, and recipe gates pass.",
        ),
        audit_row(
            "societal_poverty_line_formula",
            "sdg382_discretionary_budget",
            "missing_spl_policy_inputs",
            ["report/sdg382_denominator_audit_plan.md", "result/sdg382_denominator_summary.csv"],
            1,
            f"global_sdg382_ready_rows={metric_value(sdg_summary, 'ready_for_sdg382_construction_rows')}; global_blocked_country_wave_rows={metric_value(sdg_summary, 'blocked_country_wave_rows')}",
            "Construct or verify the societal poverty line in 2017 PPP daily per-capita terms for Albania 2002 before SDG 3.8.2 use.",
            "Verify exact SPL/PIP inputs and poverty-line formula; do not substitute CHE10/CHE25 for SDG 3.8.2.",
        ),
        audit_row(
            "ppp_2017_conversion_and_cpi_price_basis",
            "sdg382_discretionary_budget",
            "missing_ppp_cpi_price_basis",
            ["report/sdg382_denominator_audit_plan.md", "result/sdg382_denominator_source_matrix.csv"],
            1,
            "PPP 2017 conversion, survey currency year/month, and CPI/deflator assumptions are not accepted for this ALB_2002 denominator audit.",
            "Verify exact PPP/CPI/price-year handling consistent with the SDG 3.8.2 SPL denominator.",
            "Add source-backed PPP/CPI/price-basis evidence only after confirming the total-consumption period and currency basis.",
        ),
        audit_row(
            "household_discretionary_budget_construction",
            "sdg382_discretionary_budget",
            "blocked_no_household_spl_same_period_currency",
            ["report/sdg382_denominator_audit_plan.md"],
            total_stats["positive"],
            "household_discretionary_budget cannot be computed because household SPL in the same period/currency as total_consumption is not available.",
            "Compute household_discretionary_budget = total_welfare - household_spl_for_same_period_and_currency only after SPL, PPP/CPI, household size, and period conversions pass.",
            "Keep sdg382_discretionary_40 unconstructed until the discretionary budget can be audited at household level.",
        ),
        audit_row(
            "impoverishment_denominator_and_poverty_line",
            "impoverishing_health_spending",
            "blocked_no_pre_post_oop_poverty_line",
            ["report/outcome_construction.md", "report/sdg382_denominator_audit_plan.md"],
            total_stats["positive"],
            "Impoverishing health spending also needs a poverty line and pre/post-OOP welfare scale; no accepted ALB_2002 line exists in this audit.",
            "Verify poverty-line, welfare, OOP, household-size, period, and PPP/CPI assumptions before impoverishment outcomes.",
            "Do not construct impoverishing-health-spending indicators from unreviewed CHE stress denominators.",
        ),
        audit_row(
            "external_benchmark_validation",
            "validation_reference",
            "blocked_no_alb2002_household_outcome_benchmark",
            ["report/validation_reference_sources.md", "result/sdg382_denominator_source_matrix.csv"],
            1,
            f"HEFPI/WDI/source roles exist for validation, but household ALB_2002 outcomes are not constructed; global SDG denominator country-wave ready rows={metric_value(sdg_summary, 'ready_for_sdg382_construction_rows')}",
            "After household outcomes exist, compare Albania-year CHE/SDG/OOP shares with official reference sources and downgrade if benchmarks conflict.",
            "Use benchmarks only as validation after raw household construction, not as a substitute for household-level denominator evidence.",
        ),
        audit_row(
            "minimum_recipe_consumption_gate_alignment",
            "promotion_gate",
            "blocked_minimum_recipe_gate",
            ["result/alb2002_minimum_recipe_promotion_summary.csv", "temp/alb2002_minimum_recipe_promotion_gate_checklist.csv"],
            1,
            f"minimum_recipe_blocked_gates={metric_value(recipe_summary, 'alb2002_minimum_recipe_promotion_blocked_gates')}; harmonized_ready={metric_value(recipe_summary, 'alb2002_minimum_recipe_promotion_harmonized_ready_rows')}; outcome_ready={metric_value(recipe_summary, 'alb2002_minimum_recipe_promotion_outcome_ready_rows')}; sdg382_ready={metric_value(recipe_summary, 'alb2002_minimum_recipe_promotion_sdg382_ready_rows')}",
            "The consumption denominator can pass only as part of the full minimum recipe gate: key, weight, denominator, OOP, access, and geography decisions remain separated.",
            "Rerun the minimum recipe packet after denominator, OOP, access, and geography evidence changes.",
        ),
        audit_row(
            "access_and_double_failure_dependency",
            "composite_uhc_failure",
            "blocked_access_denominator_not_outcome_ready",
            ["result/alb2002_access_need_denominator_policy_summary.csv"],
            1,
            f"access_policy_rows={metric_value(access_summary, 'alb2002_access_need_denominator_policy_rows')}; access_outcome_ready={metric_value(access_summary, 'alb2002_access_need_outcome_ready_rows')}; access_sdg382_ready={metric_value(access_summary, 'alb2002_access_need_sdg382_ready_rows')}",
            "Composite UHC failure cannot be built from a financial denominator until access denominator and OOP/financial gates pass.",
            "Keep double-failure outcomes blocked until both financial and access outcome policies are accepted.",
        ),
        audit_row(
            "climate_linkage_dependency",
            "climate_linkage",
            "blocked_no_verified_geography",
            ["result/alb2002_district_climate_crosswalk_summary.csv", "report/climate_linkage_audit.md"],
            1,
            f"district_crosswalk_climate_ready_rows={metric_value(crosswalk_summary, 'alb2002_climate_linkage_ready_rows')}",
            "Even a valid financial denominator would not make ALB_2002 climate-ready without verified 2001/2002 district geography or GPS/EA-map evidence.",
            "Keep climate-linked data blocked until geography and timing pass after outcome construction.",
        ),
    ]


def summary_row(metric: str, value: Any, interpretation: str) -> dict[str, str]:
    return {"metric": metric, "value": fmt(value), "interpretation": interpretation}


def build_summary(rows: list[dict[str, str]], candidate: pd.DataFrame) -> list[dict[str, str]]:
    total = numeric(candidate["total_consumption"])
    weight = numeric(candidate["household_weight"])
    household_size = numeric(candidate["household_size"])
    oop_4w = numeric(candidate["oop_4w_sum_unreviewed"]).fillna(0)
    oop_12m = numeric(candidate["oop_12m_sum_unreviewed"]).fillna(0)
    total_stats = stats(total)
    weight_stats = stats(weight)
    size_stats = stats(household_size)
    che10_4w_rows, che10_4w_rate = che_count_and_rate(oop_4w, total, 0.10)
    che25_4w_rows, che25_4w_rate = che_count_and_rate(oop_4w, total, 0.25)
    che10_12m_rows, che10_12m_rate = che_count_and_rate(oop_12m, total, 0.10)
    che25_12m_rows, che25_12m_rate = che_count_and_rate(oop_12m, total, 0.25)
    ready_rows = sum(int(int_text(row["ready_rows"])) for row in rows)
    blocked_rows = sum(1 for row in rows if int(int_text(row["ready_rows"])) == 0)
    return [
        summary_row("alb2002_consumption_sdg_denominator_policy_rows", len(rows), "Rows in the ALB_2002 consumption/SDG denominator policy audit."),
        summary_row("alb2002_consumption_sdg_household_rows", len(candidate), "Household rows in the ALB_2002 temp core candidate."),
        summary_row("alb2002_consumption_sdg_total_consumption_rows", total_stats["nonmissing"], "Rows with nonmissing total consumption."),
        summary_row("alb2002_consumption_sdg_positive_total_consumption_rows", total_stats["positive"], "Rows with positive total consumption."),
        summary_row("alb2002_consumption_sdg_zero_total_consumption_rows", total_stats["zero"], "Rows with zero total consumption."),
        summary_row("alb2002_consumption_sdg_negative_total_consumption_rows", total_stats["negative"], "Rows with negative total consumption."),
        summary_row("alb2002_consumption_sdg_total_consumption_min", total_stats["min"], "Observed minimum total consumption."),
        summary_row("alb2002_consumption_sdg_total_consumption_p50", total_stats["p50"], "Observed median total consumption."),
        summary_row("alb2002_consumption_sdg_total_consumption_p95", total_stats["p95"], "Observed 95th percentile total consumption."),
        summary_row("alb2002_consumption_sdg_total_consumption_max", total_stats["max"], "Observed maximum total consumption."),
        summary_row("alb2002_consumption_sdg_household_weight_rows", weight_stats["nonmissing"], "Rows with nonmissing household weight."),
        summary_row("alb2002_consumption_sdg_positive_household_weight_rows", weight_stats["positive"], "Rows with positive household weight."),
        summary_row("alb2002_consumption_sdg_household_size_rows", size_stats["nonmissing"], "Rows with nonmissing household size."),
        summary_row("alb2002_consumption_sdg_positive_household_size_rows", size_stats["positive"], "Rows with positive household size."),
        summary_row("alb2002_consumption_sdg_che10_4w_unreviewed_rows", che10_4w_rows, "Diagnostic CHE10 rows using unreviewed four-week OOP over total consumption; not a final outcome."),
        summary_row("alb2002_consumption_sdg_che10_4w_unreviewed_rate", che10_4w_rate, "Diagnostic CHE10 rate using unreviewed four-week OOP over total consumption; not a final outcome."),
        summary_row("alb2002_consumption_sdg_che25_4w_unreviewed_rows", che25_4w_rows, "Diagnostic CHE25 rows using unreviewed four-week OOP over total consumption; not a final outcome."),
        summary_row("alb2002_consumption_sdg_che25_4w_unreviewed_rate", che25_4w_rate, "Diagnostic CHE25 rate using unreviewed four-week OOP over total consumption; not a final outcome."),
        summary_row("alb2002_consumption_sdg_che10_12m_unreviewed_rows", che10_12m_rows, "Diagnostic CHE10 rows using unreviewed twelve-month OOP over total consumption; not a final outcome."),
        summary_row("alb2002_consumption_sdg_che10_12m_unreviewed_rate", che10_12m_rate, "Diagnostic CHE10 rate using unreviewed twelve-month OOP over total consumption; not a final outcome."),
        summary_row("alb2002_consumption_sdg_che25_12m_unreviewed_rows", che25_12m_rows, "Diagnostic CHE25 rows using unreviewed twelve-month OOP over total consumption; not a final outcome."),
        summary_row("alb2002_consumption_sdg_che25_12m_unreviewed_rate", che25_12m_rate, "Diagnostic CHE25 rate using unreviewed twelve-month OOP over total consumption; not a final outcome."),
        summary_row("alb2002_consumption_sdg_policy_ready_rows", ready_rows, "Audit components accepted for promotion by this audit; intentionally zero."),
        summary_row("alb2002_consumption_sdg_blocked_component_rows", blocked_rows, "Audit components remaining blocked."),
        summary_row("alb2002_consumption_sdg_spl_ready_rows", 0, "Rows with accepted societal poverty line inputs; intentionally zero."),
        summary_row("alb2002_consumption_sdg_ppp_cpi_ready_rows", 0, "Rows with accepted PPP/CPI/price-basis inputs; intentionally zero."),
        summary_row("alb2002_consumption_sdg_discretionary_budget_ready_rows", 0, "Rows with accepted household discretionary budget construction; intentionally zero."),
        summary_row("alb2002_consumption_sdg_che_denominator_ready_rows", 0, "Rows with accepted CHE denominator construction; intentionally zero."),
        summary_row("alb2002_consumption_sdg_recipe_ready_rows", 0, "Rows promoted to harmonization recipe by this audit; intentionally zero."),
        summary_row("alb2002_consumption_sdg_outcome_ready_rows", 0, "Rows promoted to final outcome construction by this audit; intentionally zero."),
        summary_row("alb2002_consumption_sdg_sdg382_ready_rows", 0, "Rows promoted to SDG 3.8.2 construction by this audit; intentionally zero."),
        summary_row("alb2002_consumption_sdg_climate_linkage_ready_rows", 0, "Rows promoted to climate linkage by this audit; intentionally zero."),
        summary_row("alb2002_consumption_sdg_current_decision", DECISION, "Current fail-closed decision for the ALB_2002 consumption/SDG denominator policy audit."),
    ]


def count_by(rows: list[dict[str, str]], field: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    for row in rows:
        key = row.get(field, "")
        counts[key] = counts.get(key, 0) + 1
    return counts


def markdown_count_table(counts: dict[str, int], label: str) -> str:
    lines = [f"| {label} | Count |", "|---|---:|"]
    for key, count in sorted(counts.items()):
        lines.append(f"| {key or 'blank'} | {count} |")
    return "\n".join(lines)


def markdown_rows(rows: list[dict[str, str]], columns: list[str], limit: int = 30) -> str:
    lines = ["| " + " | ".join(columns) + " |", "|" + "|".join("---" for _ in columns) + "|"]
    for row in rows[:limit]:
        values = []
        for column in columns:
            value = (row.get(column, "") or "").replace("|", "/")
            if len(value) > 130:
                value = value[:127] + "..."
            values.append(value)
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines)


def write_report(rows: list[dict[str, str]], summary: list[dict[str, str]]) -> None:
    summary_table = "\n".join(f"| {row['metric']} | {row['value']} | {row['interpretation']} |" for row in summary)
    report = f"""# ALB_2002 Consumption and SDG Denominator Policy Audit

Status: fail-closed denominator-policy audit. This report quantifies the observed ALB_2002 total-consumption denominator evidence and identifies the missing SDG 3.8.2 inputs. It does not write `data/`, does not construct CHE/SDG outcomes, and does not promote any row to harmonization, outcome construction, or climate linkage.

## Bottom Line

- `total_consumption` is observed for all ALB_2002 household-core candidate rows, but the accepted unit, period, price basis, and inclusion scope are still unresolved.
- CHE10/CHE25 ratios using unreviewed OOP sums are diagnostic stress tests only, not final outcome construction.
- SDG 3.8.2 is blocked because the societal poverty line, 2017 PPP/CPI handling, household discretionary budget, and benchmark validation are not accepted.
- Recipe-ready, outcome-ready, SDG 3.8.2-ready, and climate-linkage-ready rows from this audit: 0.
- Current decision: `{DECISION}`.

## Summary

| Metric | Value | Interpretation |
|---|---:|---|
{summary_table}

## Component Families

{markdown_count_table(count_by(rows, 'component_family'), 'Component family')}

## Evidence Status

{markdown_count_table(count_by(rows, 'evidence_status'), 'Evidence status')}

## Component Audit

{markdown_rows(rows, ['component_id', 'component_family', 'evidence_status', 'observed_rows', 'ready_rows', 'diagnostic_value'], 30)}

## Interpretation

- The observed `totcons` field is promising denominator evidence, but the audit deliberately preserves the distinction between a visible survey aggregate and an accepted financial-protection denominator.
- Household size and household weights are visible, yet SDG 3.8.2 also requires period, daily per-capita conversion, SPL, PPP/CPI, and price-basis decisions.
- The OOP numerator is still blocked by recall-period, gift/payment scope, skip/missing, and aggregation-policy choices.
- The climate-UHC analysis remains blocked even if the financial denominator improves, because geography and outcome promotion gates are separate.

## Machine-Readable Outputs

- `temp/alb2002_consumption_sdg_denominator_policy_audit.csv`
- `result/alb2002_consumption_sdg_denominator_policy_summary.csv`
"""
    REPORT_PATH.write_text(report, encoding="utf-8")


def main() -> None:
    ensure_dirs()
    if not CANDIDATE_PATH.exists():
        raise FileNotFoundError(f"Missing required candidate table: {CANDIDATE_PATH}")
    candidate = pd.read_csv(CANDIDATE_PATH)
    rows = build_rows(candidate)
    summary = build_summary(rows, candidate)
    write_csv(AUDIT_PATH, rows, AUDIT_COLUMNS)
    write_csv(SUMMARY_PATH, summary, SUMMARY_COLUMNS)
    write_report(rows, summary)
    append_log(TEMP_DIR / "audit_log.md", f"Built ALB_2002 consumption/SDG denominator policy audit rows={len(rows)} decision={DECISION}.")
    print(f"ALB_2002 consumption/SDG denominator policy rows={len(rows)} decision={DECISION}.")


if __name__ == "__main__":
    main()
