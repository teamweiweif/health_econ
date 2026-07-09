from __future__ import annotations

import csv
from typing import Any

import pandas as pd

from common import REPORT_DIR, RESULT_DIR, TEMP_DIR, append_log, ensure_dirs, write_csv


IDNO = "ALB_2002_LSMS_v01_M"
COUNTRY = "Albania"
SURVEY_NAME = "Living Standards Measurement Survey 2002"
WAVE = "2002"

CORE_PATH = TEMP_DIR / "alb2002_household_core_candidate.csv"
CHE_PATH = TEMP_DIR / "alb2002_che_candidate_household_outcomes.csv"
CORE_SUMMARY_PATH = RESULT_DIR / "alb2002_household_core_candidate_summary.csv"
CHE_SUMMARY_PATH = RESULT_DIR / "alb2002_che_candidate_outcome_summary.csv"
MINIMUM_RECIPE_SUMMARY_PATH = RESULT_DIR / "alb2002_minimum_recipe_promotion_summary.csv"
CROSSWALK_SUMMARY_PATH = RESULT_DIR / "alb2002_district_climate_crosswalk_summary.csv"

CANDIDATE_PATH = TEMP_DIR / "alb2002_analysis_candidate_dataset.csv"
LINEAGE_PATH = TEMP_DIR / "alb2002_analysis_candidate_lineage.csv"
AUDIT_PATH = RESULT_DIR / "alb2002_analysis_candidate_readiness_audit.csv"
SUMMARY_PATH = RESULT_DIR / "alb2002_analysis_candidate_readiness_summary.csv"
REPORT_PATH = REPORT_DIR / "alb2002_analysis_candidate_readiness_audit.md"

DECISION = "blocked_alb2002_analysis_candidate_not_promoted_due_recipe_outcome_climate_gates"
PROMOTION_STATUS = "temp_only_analysis_candidate_not_promoted"

CANDIDATE_COLUMNS = [
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
    "cluster_id",
    "latitude",
    "longitude",
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
    "sudden_illness_4w_any",
    "delayed_or_unmet_care_candidate",
    "forgone_care_cost_barrier_candidate",
    "forgone_care_distance_barrier_candidate",
    "forgone_care_supply_barrier_candidate",
    "uhc_double_failure_che10_or_access_candidate",
    "uhc_double_failure_che25_or_access_candidate",
    "coping_health_cost_candidate",
    "oop_4w_monthly_equivalent",
    "oop_12m_monthly_equivalent",
    "candidate_policy_name",
    "candidate_dataset_status",
    "promotion_status",
    "blocking_reason",
]

LINEAGE_COLUMNS = [
    "lineage_id",
    "harmonized_field",
    "source_fields",
    "source_artifacts",
    "transformation_or_rule",
    "status",
    "blocking_reason",
]

AUDIT_COLUMNS = [
    "gate_id",
    "field_family",
    "required_for",
    "candidate_fields",
    "candidate_rows",
    "complete_rows",
    "partial_rows",
    "missing_rows",
    "observed_coverage_rate",
    "candidate_status",
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


def safe_numeric(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series, errors="coerce")


def safe_int(value: Any) -> int:
    try:
        return int(float(str(value).strip()))
    except (TypeError, ValueError):
        return 0


def fmt(value: Any) -> str:
    try:
        number = float(str(value).strip())
    except (TypeError, ValueError):
        return "" if value is None else str(value)
    if number.is_integer():
        return str(int(number))
    return f"{number:.6g}"


def nonmissing(series: pd.Series) -> pd.Series:
    return series.notna() & (series.astype(str).str.strip() != "")


def any_positive(frame: pd.DataFrame, columns: list[str]) -> pd.Series:
    values = [safe_numeric(frame[column]).fillna(0) for column in columns if column in frame.columns]
    if not values:
        return pd.Series(False, index=frame.index)
    out = values[0] > 0
    for value in values[1:]:
        out = out | (value > 0)
    return out


def blocking_reason() -> str:
    return (
        "This joined ALB_2002 candidate assembles household core, weights, timing, admin geography, access signals, "
        "and temp-only CHE10/CHE25 candidates, but it remains outside data/ because the harmonization recipe, final "
        "outcome promotion, SDG 3.8.2 denominator, benchmark comparison, and climate-geography gates have not passed."
    )


def build_candidate(core: pd.DataFrame, che: pd.DataFrame) -> pd.DataFrame:
    duplicate_core = int(core["hhid"].duplicated().sum())
    duplicate_che = int(che["hhid"].duplicated().sum())
    if duplicate_core or duplicate_che:
        raise ValueError(f"Non-unique hhid keys: core={duplicate_core} che={duplicate_che}")

    merged = core.merge(
        che[
            [
                "hhid",
                "total_consumption_monthly_candidate",
                "oop_4w_monthly_equivalent",
                "oop_12m_monthly_equivalent",
                "oop_combined_monthly_equivalent",
                "oop_share_total_budget_candidate",
                "che10_total_budget_candidate",
                "che25_total_budget_candidate",
                "positive_oop_candidate",
                "candidate_policy_name",
            ]
        ],
        on="hhid",
        how="left",
        validate="one_to_one",
    )

    access_cost = any_positive(merged, ["delay_reason_cost", "not_gone_reason_cost", "refused_reason_cost", "medicine_discount_cost_barrier"])
    access_distance = any_positive(merged, ["delay_reason_distance", "not_gone_reason_distance", "refused_reason_distance"])
    access_supply = any_positive(merged, ["refused_health_services_any"])
    unmet = any_positive(merged, ["delayed_help_any", "hospital_referral_not_gone_any", "refused_health_services_any"])
    need = any_positive(merged, ["illness_or_disability_any", "sudden_illness_4w_any"])
    che10 = safe_numeric(merged["che10_total_budget_candidate"]).fillna(0) > 0
    che25 = safe_numeric(merged["che25_total_budget_candidate"]).fillna(0) > 0

    out = pd.DataFrame(
        {
            "country": merged["country"],
            "survey_name": merged["survey_name"],
            "wave": merged["wave"],
            "idno": merged["idno"],
            "survey_year": merged["survey_year"],
            "survey_month": merged["survey_month"],
            "interview_date": merged["interview_date"],
            "hhid": merged["hhid"],
            "household_weight": merged["household_weight"],
            "strata": merged["stratum"],
            "psu": merged["psu"],
            "admin1": "",
            "admin2": merged["district_name_identification"],
            "admin2_code": merged["district_code_identification"],
            "cluster_id": merged["psu"],
            "latitude": "",
            "longitude": "",
            "geolocation_quality": merged["geolocation_quality"],
            "rural": merged["urban_rural_code_identification"],
            "household_size": merged["household_size"],
            "children_under5": merged["children_under5"],
            "children_under15": merged["children_under15"],
            "elderly_60plus": merged["elderly_60plus"],
            "elderly_65plus": merged["elderly_65plus"],
            "head_sex": merged["head_sex"],
            "head_age": merged["head_age"],
            "agriculture_livelihood": merged["agric_livelihood_any_candidate"],
            "health_insurance_candidate": merged["health_license_any"],
            "total_consumption_monthly_candidate": merged["total_consumption_monthly_candidate"],
            "oop_health_expenditure_monthly_candidate": merged["oop_combined_monthly_equivalent"],
            "oop_share_total_budget_candidate": merged["oop_share_total_budget_candidate"],
            "che10_total_budget_candidate": merged["che10_total_budget_candidate"],
            "che25_total_budget_candidate": merged["che25_total_budget_candidate"],
            "positive_oop_candidate": merged["positive_oop_candidate"],
            "illness_or_injury_need_candidate": need.astype(int),
            "sudden_illness_4w_any": merged["sudden_illness_4w_any"],
            "delayed_or_unmet_care_candidate": unmet.astype(int),
            "forgone_care_cost_barrier_candidate": access_cost.astype(int),
            "forgone_care_distance_barrier_candidate": access_distance.astype(int),
            "forgone_care_supply_barrier_candidate": access_supply.astype(int),
            "uhc_double_failure_che10_or_access_candidate": (che10 | unmet).astype(int),
            "uhc_double_failure_che25_or_access_candidate": (che25 | unmet).astype(int),
            "coping_health_cost_candidate": merged["health_payment_money_raising_any_unreviewed"],
            "oop_4w_monthly_equivalent": merged["oop_4w_monthly_equivalent"],
            "oop_12m_monthly_equivalent": merged["oop_12m_monthly_equivalent"],
            "candidate_policy_name": merged["candidate_policy_name"],
            "candidate_dataset_status": "joined_temp_analysis_candidate_not_promoted",
            "promotion_status": PROMOTION_STATUS,
            "blocking_reason": blocking_reason(),
        }
    )
    return out


def audit_gate(
    candidate: pd.DataFrame,
    gate_id: str,
    family: str,
    required_for: str,
    fields: list[str],
    status: str,
    block: str,
    next_action: str,
    promotion_ready_rows: int = 0,
) -> dict[str, str]:
    candidate_rows = len(candidate)
    masks = [nonmissing(candidate[field]) for field in fields if field in candidate.columns]
    if masks:
        complete = masks[0].copy()
        any_present = masks[0].copy()
        for mask in masks[1:]:
            complete = complete & mask
            any_present = any_present | mask
        complete_rows = int(complete.sum())
        partial_rows = int((any_present & ~complete).sum())
        missing_rows = int((~any_present).sum())
    else:
        complete_rows = 0
        partial_rows = 0
        missing_rows = candidate_rows
    return {
        "gate_id": gate_id,
        "field_family": family,
        "required_for": required_for,
        "candidate_fields": ";".join(fields),
        "candidate_rows": str(candidate_rows),
        "complete_rows": str(complete_rows),
        "partial_rows": str(partial_rows),
        "missing_rows": str(missing_rows),
        "observed_coverage_rate": fmt(complete_rows / candidate_rows) if candidate_rows else "",
        "candidate_status": status,
        "promotion_ready_rows": str(promotion_ready_rows),
        "blocking_reason": block,
        "next_action": next_action,
    }


def build_audit(candidate: pd.DataFrame, summaries: dict[str, list[dict[str, str]]]) -> list[dict[str, str]]:
    min_recipe = summaries["minimum_recipe"]
    crosswalk = summaries["crosswalk"]
    harmonized_ready = safe_int(metric_value(min_recipe, "alb2002_minimum_recipe_promotion_harmonized_ready_rows"))
    outcome_ready = safe_int(metric_value(min_recipe, "alb2002_minimum_recipe_promotion_outcome_ready_rows"))
    climate_ready = safe_int(metric_value(crosswalk, "alb2002_climate_linkage_ready_rows"))
    common_block = blocking_reason()
    return [
        audit_gate(candidate, "identity_keys", "identity", "harmonized_household", ["country", "survey_name", "wave", "idno", "hhid"], "candidate_complete", "", "Preserve one-row-per-household key checks in any promoted dataset."),
        audit_gate(candidate, "survey_design", "weights_design", "weighted_descriptive_and_modeling", ["household_weight", "strata", "psu"], "candidate_complete_not_promoted", "Weight/design semantics and variance-use rules still need acceptance.", "Finalize household weight normalization, target population, strata/PSU variance guidance, and survey-design reporting."),
        audit_gate(candidate, "interview_timing", "timing", "climate_linkage", ["survey_month", "interview_date"], "candidate_complete_not_promoted", "Timing values are observed, but exposure-window rules still need climate-linkage review.", "Document accepted exposure windows and seasonality controls before climate extraction."),
        audit_gate(candidate, "admin_geography", "admin_geography", "climate_linkage", ["admin2", "admin2_code", "cluster_id"], "candidate_complete_not_promoted", "Admin geography is observed but no verified 2001/2002 district boundary or coordinates are accepted.", "Resolve district-boundary provenance/crosswalk or obtain GPS/EA-map evidence before climate linkage."),
        audit_gate(candidate, "point_coordinates", "coordinates", "climate_linkage", ["latitude", "longitude"], "missing", "No raw coordinate values are present in the local ALB_2002 artifacts.", "Use only verified admin geography, or obtain official coordinate/EA-map artifacts."),
        audit_gate(candidate, "demographics", "covariates", "descriptive_ml_modeling", ["household_size", "children_under5", "children_under15", "elderly_60plus", "head_sex", "head_age"], "candidate_complete_not_promoted", "Covariates are visible but require final harmonization lineage acceptance.", "Carry lineage into a promoted harmonized recipe only after outcome and climate gates pass."),
        audit_gate(candidate, "consumption_denominator", "financial_denominator", "CHE10_CHE25_SDG382", ["total_consumption_monthly_candidate"], "candidate_complete_not_promoted", "Total-budget candidate is observed, but SDG 3.8.2 discretionary-budget and benchmark inputs remain unresolved.", "Resolve SPL/PPP/CPI/discretionary-budget and benchmark comparisons."),
        audit_gate(candidate, "oop_outcomes", "financial_outcomes", "household_outcomes", ["oop_health_expenditure_monthly_candidate", "oop_share_total_budget_candidate", "che10_total_budget_candidate", "che25_total_budget_candidate"], "candidate_complete_not_promoted", "CHE outcomes are temp-only mixed-recall candidates, not final promoted outcomes.", "Accept numerator scope, mixed-recall handling, gift/payment policy, and external benchmark checks before writing data/household_outcomes.csv.", outcome_ready),
        audit_gate(candidate, "access_outcomes", "access_outcomes", "household_outcomes", ["illness_or_injury_need_candidate", "delayed_or_unmet_care_candidate", "forgone_care_cost_barrier_candidate", "forgone_care_distance_barrier_candidate"], "candidate_complete_not_promoted", "Access/need indicators are candidate composites with unresolved denominator and skip-path semantics.", "Finalize access/need denominator policy and low-event handling before promotion."),
        audit_gate(candidate, "composite_uhc", "composite_outcomes", "household_outcomes", ["uhc_double_failure_che10_or_access_candidate", "uhc_double_failure_che25_or_access_candidate"], "candidate_complete_not_promoted", "Composite outcomes combine two unpromoted candidate families.", "Promote only after both financial and access outcome gates pass."),
        audit_gate(candidate, "harmonized_dataset_promotion", "promotion", "data/harmonized_household.csv", ["hhid"], "blocked", common_block, "Do not write to data/ until minimum recipe, outcome, SDG/benchmark, and climate-geography gates pass.", harmonized_ready),
        audit_gate(candidate, "climate_dataset_promotion", "promotion", "data/climate_linked_household.csv", ["admin2", "survey_month", "interview_date"], "blocked", common_block, "Construct climate linkage only after verified geography and exposure-window rules pass.", climate_ready),
    ]


def build_lineage() -> list[dict[str, str]]:
    rows = [
        ("lineage_001", "identity/timing/design fields", "hhid;survey_year;survey_month;interview_date;household_weight;stratum;psu", "temp/alb2002_household_core_candidate.csv", "direct carry-forward with renamed strata/admin fields", "candidate_not_promoted", "Household core is temp-only until minimum recipe promotion passes."),
        ("lineage_002", "admin2/admin2_code", "district_name_identification;district_code_identification", "temp/alb2002_household_core_candidate.csv", "district fields carried as admin2/admin2_code candidates", "candidate_not_promoted", "Boundary provenance and historical district crosswalk remain unresolved."),
        ("lineage_003", "demographic covariates", "household_size;children_under5;children_under15;elderly_60plus;head_sex;head_age", "temp/alb2002_household_core_candidate.csv", "direct carry-forward", "candidate_not_promoted", "Covariates are not promoted until the dataset recipe is accepted."),
        ("lineage_004", "financial protection candidates", "oop_combined_monthly_equivalent;oop_share_total_budget_candidate;che10_total_budget_candidate;che25_total_budget_candidate", "temp/alb2002_che_candidate_household_outcomes.csv", "direct carry-forward from period-aligned CHE candidate outcomes", "candidate_not_promoted", "Outcome and benchmark gates remain unresolved."),
        ("lineage_005", "access outcome candidates", "illness_or_disability_any;sudden_illness_4w_any;delayed_help_any;hospital_referral_not_gone_any;delay_reason_cost;not_gone_reason_cost;delay_reason_distance;not_gone_reason_distance;refused_health_services_any", "temp/alb2002_household_core_candidate.csv", "candidate household composites using any-positive component logic", "candidate_not_promoted", "Access/need denominator, skip semantics, and low-event-rate review remain unresolved."),
        ("lineage_006", "composite UHC candidates", "che10_total_budget_candidate;che25_total_budget_candidate;delayed_or_unmet_care_candidate", "temp/alb2002_analysis_candidate_dataset.csv", "financial hardship candidate OR unmet-care candidate", "candidate_not_promoted", "Composite outcomes cannot be promoted while component outcomes remain unpromoted."),
    ]
    return [
        {
            "lineage_id": row[0],
            "harmonized_field": row[1],
            "source_fields": row[2],
            "source_artifacts": row[3],
            "transformation_or_rule": row[4],
            "status": row[5],
            "blocking_reason": row[6],
        }
        for row in rows
    ]


def summary_row(metric: str, value: Any, interpretation: str) -> dict[str, str]:
    return {"metric": metric, "value": str(value), "interpretation": interpretation}


def build_summary(candidate: pd.DataFrame, audit: list[dict[str, str]], summaries: dict[str, list[dict[str, str]]]) -> list[dict[str, str]]:
    blocked = sum(1 for row in audit if row["candidate_status"] == "blocked")
    complete = sum(1 for row in audit if row["candidate_status"].startswith("candidate_complete"))
    missing = sum(1 for row in audit if row["candidate_status"] == "missing")
    che_summary = summaries["che"]
    min_recipe = summaries["minimum_recipe"]
    crosswalk = summaries["crosswalk"]
    return [
        summary_row("alb2002_analysis_candidate_rows", len(candidate), "Temp-only joined ALB_2002 analysis-candidate household rows."),
        summary_row("alb2002_analysis_candidate_columns", len(candidate.columns), "Columns in the temp-only ALB_2002 analysis-candidate dataset."),
        summary_row("alb2002_analysis_candidate_lineage_rows", 6, "Lineage rows for carried or derived analysis-candidate fields."),
        summary_row("alb2002_analysis_candidate_audit_rows", len(audit), "Readiness gate rows for the ALB_2002 analysis candidate."),
        summary_row("alb2002_analysis_candidate_complete_candidate_gates", complete, "Field families with complete observed candidate coverage, still not promoted."),
        summary_row("alb2002_analysis_candidate_missing_gates", missing, "Field families with missing required candidate coverage."),
        summary_row("alb2002_analysis_candidate_blocked_promotion_gates", blocked, "Promotion gates still blocked."),
        summary_row("alb2002_analysis_candidate_household_core_rows", metric_value(summaries["core"], "alb2002_household_core_candidate_rows"), "Upstream household-core rows consumed."),
        summary_row("alb2002_analysis_candidate_che10_rows", metric_value(che_summary, "alb2002_che_candidate_che10_rows"), "CHE10 candidate rows carried from the temp-only outcome audit."),
        summary_row("alb2002_analysis_candidate_che25_rows", metric_value(che_summary, "alb2002_che_candidate_che25_rows"), "CHE25 candidate rows carried from the temp-only outcome audit."),
        summary_row("alb2002_analysis_candidate_outcome_promotion_ready_rows", metric_value(che_summary, "alb2002_che_candidate_outcome_promotion_ready_rows"), "Rows ready for final outcome promotion; should remain zero."),
        summary_row("alb2002_analysis_candidate_harmonized_ready_rows", metric_value(min_recipe, "alb2002_minimum_recipe_promotion_harmonized_ready_rows"), "Rows ready for harmonized dataset promotion; should remain zero."),
        summary_row("alb2002_analysis_candidate_climate_linkage_ready_rows", metric_value(crosswalk, "alb2002_climate_linkage_ready_rows"), "Rows ready for climate linkage; should remain zero."),
        summary_row("alb2002_analysis_candidate_data_write_ready_rows", 0, "Rows allowed to be written under data/ by this audit; intentionally zero."),
        summary_row("alb2002_analysis_candidate_current_decision", DECISION, "Current fail-closed decision for the ALB_2002 analysis candidate."),
    ]


def markdown_table(rows: list[dict[str, str]], columns: list[str], max_rows: int | None = None) -> str:
    selected = rows if max_rows is None else rows[:max_rows]
    lines = ["| " + " | ".join(columns) + " |", "|" + "|".join("---" for _ in columns) + "|"]
    for row in selected:
        values = []
        for col in columns:
            value = str(row.get(col, "")).replace("|", "/")
            if len(value) > 160:
                value = value[:157] + "..."
            values.append(value)
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines)


def write_report(summary: list[dict[str, str]], audit: list[dict[str, str]], lineage: list[dict[str, str]]) -> None:
    REPORT_PATH.write_text(
        f"""# ALB_2002 Analysis Candidate Readiness Audit

Status: temp-only joined analysis-candidate audit. This creates `temp/alb2002_analysis_candidate_dataset.csv` from the ALB_2002 household core and temp CHE candidate outcomes. It does not write `data/`, does not declare a harmonized household dataset ready, and does not create climate-linked data.

## Summary

{markdown_table(summary, ['metric', 'value', 'interpretation'])}

## Readiness Gates

{markdown_table(audit, ['gate_id', 'field_family', 'candidate_rows', 'complete_rows', 'missing_rows', 'candidate_status', 'promotion_ready_rows', 'blocking_reason'])}

## Lineage

{markdown_table(lineage, ['lineage_id', 'harmonized_field', 'source_fields', 'status', 'blocking_reason'])}

## Interpretation

- The temp analysis candidate gives one joined ALB_2002 row per household for downstream inspection.
- Identity, timing, admin geography, weights, demographic covariates, total-budget denominator candidates, candidate CHE outcomes, and access composites are visible at household level.
- Point coordinates are absent, and admin geography remains blocked until historical district boundary or equivalent geography evidence is accepted.
- No row is promoted to `data/harmonized_household.csv`, `data/household_outcomes.csv`, or `data/climate_linked_household.csv`.

## Machine-Readable Outputs

- `temp/alb2002_analysis_candidate_dataset.csv`
- `temp/alb2002_analysis_candidate_lineage.csv`
- `result/alb2002_analysis_candidate_readiness_audit.csv`
- `result/alb2002_analysis_candidate_readiness_summary.csv`
""",
        encoding="utf-8",
    )


def main() -> None:
    ensure_dirs()
    if not CORE_PATH.exists():
        raise FileNotFoundError(f"Missing required input: {CORE_PATH}")
    if not CHE_PATH.exists():
        raise FileNotFoundError(f"Missing required input: {CHE_PATH}")

    core = pd.read_csv(CORE_PATH, dtype=str)
    che = pd.read_csv(CHE_PATH, dtype=str)
    candidate = build_candidate(core, che)
    lineage = build_lineage()
    summaries = {
        "core": read_csv_dicts(CORE_SUMMARY_PATH),
        "che": read_csv_dicts(CHE_SUMMARY_PATH),
        "minimum_recipe": read_csv_dicts(MINIMUM_RECIPE_SUMMARY_PATH),
        "crosswalk": read_csv_dicts(CROSSWALK_SUMMARY_PATH),
    }
    audit = build_audit(candidate, summaries)
    summary = build_summary(candidate, audit, summaries)

    write_csv(CANDIDATE_PATH, candidate.to_dict("records"), CANDIDATE_COLUMNS)
    write_csv(LINEAGE_PATH, lineage, LINEAGE_COLUMNS)
    write_csv(AUDIT_PATH, audit, AUDIT_COLUMNS)
    write_csv(SUMMARY_PATH, summary, SUMMARY_COLUMNS)
    write_report(summary, audit, lineage)
    append_log(TEMP_DIR / "audit_log.md", f"Built ALB_2002 analysis candidate rows={len(candidate)} decision={DECISION}.")
    print(f"ALB_2002 analysis candidate rows={len(candidate)} decision={DECISION}.")


if __name__ == "__main__":
    main()
