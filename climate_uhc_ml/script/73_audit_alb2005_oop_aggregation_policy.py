from __future__ import annotations

import csv
import math
from pathlib import Path
from typing import Any

import pandas as pd

from common import REPORT_DIR, RESULT_DIR, TEMP_DIR, append_log, ensure_dirs, write_csv

try:
    import pyreadstat
except ImportError:  # pragma: no cover - environment audit covers this.
    pyreadstat = None


IDNO = "ALB_2005_LSMS_v01_M"
COUNTRY = "Albania"
SURVEY_NAME = "Living Standards Measurement Survey 2005"
WAVE = "2005"
RAW_ROOT = TEMP_DIR / "raw_extracted" / "lsms2005en_1e7f1965c4a5" / "lsms2005en" / "Data_2005"

QUESTIONNAIRE_SUMMARY_PATH = RESULT_DIR / "alb2005_health_questionnaire_semantics_summary.csv"
REQUIRED_VALUE_KEY_SUMMARY_PATH = RESULT_DIR / "alb2005_required_value_key_summary.csv"
TIMING_GEO_SUMMARY_PATH = RESULT_DIR / "alb2005_timing_geography_exhaustive_summary.csv"

AUDIT_PATH = TEMP_DIR / "alb2005_oop_aggregation_policy_audit.csv"
SUMMARY_PATH = RESULT_DIR / "alb2005_oop_aggregation_policy_summary.csv"
REPORT_PATH = REPORT_DIR / "alb2005_oop_aggregation_policy_audit.md"

DECISION = "blocked_alb2005_oop_aggregation_policy_stress_test_not_outcome_ready"
NO_PROMOTION = "not_promoted_oop_policy_stress_test_only"

FOUR_WEEK_PROVIDER_BASE = ["m9a_q16", "m9a_q28", "m9a_q38", "m9a_q46", "m9a_q54"]
FOUR_WEEK_GIFTS = ["m9a_q17", "m9a_q29", "m9a_q39", "m9a_q47", "m9a_q55"]
FOUR_WEEK_MEDICINES = ["m9a_q20", "m9a_q32", "m9a_q41", "m9a_q49", "m9a_q57", "m9a_q61"]
FOUR_WEEK_LAB = ["m9a_q22", "m9a_q34", "m9a_q42", "m9a_q50", "m9a_q58"]
FOUR_WEEK_TRANSPORT = ["m9a_q23", "m9a_q35", "m9a_q43", "m9a_q51", "m9a_q59"]

TWELVE_MONTH_PROVIDER_BASE = ["m9a_q68", "m9a_q76"]
TWELVE_MONTH_GIFTS = ["m9a_q69", "m9a_q77"]
TWELVE_MONTH_MEDICINES = ["m9a_q71", "m9a_q79"]
TWELVE_MONTH_LAB = ["m9a_q72", "m9a_q80"]
TWELVE_MONTH_TRANSPORT = ["m9a_q73", "m9a_q81"]

ALL_HEALTH_A_VARIABLES = sorted(
    set(
        FOUR_WEEK_PROVIDER_BASE
        + FOUR_WEEK_GIFTS
        + FOUR_WEEK_MEDICINES
        + FOUR_WEEK_LAB
        + FOUR_WEEK_TRANSPORT
        + TWELVE_MONTH_PROVIDER_BASE
        + TWELVE_MONTH_GIFTS
        + TWELVE_MONTH_MEDICINES
        + TWELVE_MONTH_LAB
        + TWELVE_MONTH_TRANSPORT
    )
)

AUDIT_COLUMNS = [
    "country",
    "survey_name",
    "wave",
    "idno",
    "policy_name",
    "recall_scope",
    "annualization_factor",
    "included_components",
    "excluded_components",
    "source_variables",
    "formula",
    "household_rows",
    "total_consumption_denominator_rows",
    "positive_oop_rows",
    "positive_oop_rate",
    "weighted_denominator",
    "weighted_positive_oop_rate",
    "mean_oop",
    "p50_oop",
    "p95_oop",
    "max_oop",
    "mean_oop_share",
    "p50_oop_share",
    "p95_oop_share",
    "max_oop_share",
    "che10_rows",
    "che10_rate",
    "che10_weighted_rate",
    "che25_rows",
    "che25_rate",
    "che25_weighted_rate",
    "ready_for_outcome",
    "ready_for_recipe",
    "climate_linkage_ready",
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
        return f"{value:.6g}"
    return str(value)


def key_part(value: Any) -> str:
    if value is None:
        return ""
    try:
        if pd.isna(value):
            return ""
    except TypeError:
        pass
    try:
        number = float(value)
        if math.isfinite(number) and number.is_integer():
            return str(int(number))
    except (TypeError, ValueError):
        pass
    return str(value).strip()


def compact_join(values: list[str], limit: int = 40) -> str:
    out: list[str] = []
    seen: set[str] = set()
    for value in values:
        clean = str(value).strip()
        if not clean or clean in seen:
            continue
        out.append(clean)
        seen.add(clean)
        if len(out) >= limit:
            break
    return ";".join(out)


def read_sav(file_name: str, usecols: list[str]) -> pd.DataFrame:
    if pyreadstat is None:
        raise RuntimeError("pyreadstat is not available")
    df, _ = pyreadstat.read_sav(str(RAW_ROOT / file_name), usecols=usecols, apply_value_formats=False)
    return df


def add_psu_hh_key(df: pd.DataFrame, psu: str, hh: str) -> pd.DataFrame:
    out = df.copy()
    out["psu_key"] = out[psu].map(key_part)
    out["hh_key"] = out[hh].map(key_part)
    out["psu_hh_key"] = out["psu_key"] + "-" + out["hh_key"]
    out.loc[(out["psu_key"] == "") | (out["hh_key"] == ""), "psu_hh_key"] = ""
    return out


def add_hhid_key(df: pd.DataFrame, hhid: str) -> pd.DataFrame:
    out = df.copy()
    out["hhid_key"] = out[hhid].map(key_part)
    return out


def row_sum(df: pd.DataFrame, columns: list[str]) -> pd.Series:
    if not columns:
        return pd.Series(0.0, index=df.index)
    return df[columns].apply(pd.to_numeric, errors="coerce").fillna(0).sum(axis=1)


def nonmissing_quantiles(series: pd.Series) -> dict[str, str]:
    valid = pd.to_numeric(series, errors="coerce").replace([float("inf"), float("-inf")], pd.NA).dropna()
    if valid.empty:
        return {"mean": "", "p50": "", "p95": "", "max": ""}
    return {
        "mean": fmt(float(valid.mean())),
        "p50": fmt(float(valid.quantile(0.50))),
        "p95": fmt(float(valid.quantile(0.95))),
        "max": fmt(float(valid.max())),
    }


def weighted_rate(event: pd.Series, denominator: pd.Series, weight: pd.Series) -> str:
    valid = denominator.fillna(False).astype(bool) & weight.notna() & (weight > 0)
    if not valid.any():
        return ""
    numerator_weight = float(weight.loc[valid & event.fillna(False).astype(bool)].sum())
    denominator_weight = float(weight.loc[valid].sum())
    return fmt(numerator_weight / denominator_weight) if denominator_weight > 0 else ""


def build_household_base() -> pd.DataFrame:
    filters = read_sav("filters_cl.sav", ["M0_Q00", "M0_Q01", "HHID"])
    filters = add_hhid_key(add_psu_hh_key(filters, "M0_Q00", "M0_Q01"), "HHID")
    base = pd.DataFrame(
        {
            "hhid": filters["hhid_key"],
            "psu_hh_key": filters["psu_hh_key"],
        }
    )
    poverty = read_sav("poverty.sav", ["PSU", "hh", "totcons", "weight_retro"])
    poverty = add_psu_hh_key(poverty, "PSU", "hh")
    base = base.merge(
        poverty[["psu_hh_key", "totcons", "weight_retro"]].rename(
            columns={"totcons": "total_consumption", "weight_retro": "household_weight"}
        ),
        on="psu_hh_key",
        how="left",
    )
    return base


def build_household_oop_components() -> pd.DataFrame:
    healtha = read_sav("Modul_9A_healtha_cl.sav", ["hhid", *ALL_HEALTH_A_VARIABLES])
    healtha = add_hhid_key(healtha, "hhid")
    component_defs = {
        "oop_4w_provider_base": FOUR_WEEK_PROVIDER_BASE,
        "oop_4w_gifts": FOUR_WEEK_GIFTS,
        "oop_4w_medicines": FOUR_WEEK_MEDICINES,
        "oop_4w_lab": FOUR_WEEK_LAB,
        "oop_4w_transport": FOUR_WEEK_TRANSPORT,
        "oop_12m_provider_base": TWELVE_MONTH_PROVIDER_BASE,
        "oop_12m_gifts": TWELVE_MONTH_GIFTS,
        "oop_12m_medicines": TWELVE_MONTH_MEDICINES,
        "oop_12m_lab": TWELVE_MONTH_LAB,
        "oop_12m_transport": TWELVE_MONTH_TRANSPORT,
    }
    for output, variables in component_defs.items():
        healtha[output] = row_sum(healtha, variables)
    grouped = healtha.groupby("hhid_key", dropna=False)[list(component_defs.keys())].sum().reset_index()
    grouped = grouped.rename(columns={"hhid_key": "hhid"})
    return grouped


def build_candidate() -> pd.DataFrame:
    candidate = build_household_base()
    components = build_household_oop_components()
    candidate = candidate.merge(components, on="hhid", how="left")
    for column in components.columns:
        if column != "hhid":
            candidate[column] = pd.to_numeric(candidate[column], errors="coerce").fillna(0)
    return candidate


def policy_specs(candidate: pd.DataFrame) -> list[dict[str, Any]]:
    c = candidate
    four_week_no_gifts_with_transport = (
        c["oop_4w_provider_base"] + c["oop_4w_medicines"] + c["oop_4w_lab"] + c["oop_4w_transport"]
    )
    four_week_all = four_week_no_gifts_with_transport + c["oop_4w_gifts"]
    four_week_no_gifts_no_transport = c["oop_4w_provider_base"] + c["oop_4w_medicines"] + c["oop_4w_lab"]
    twelve_no_gifts_with_transport = (
        c["oop_12m_provider_base"] + c["oop_12m_medicines"] + c["oop_12m_lab"] + c["oop_12m_transport"]
    )
    twelve_all = twelve_no_gifts_with_transport + c["oop_12m_gifts"]
    twelve_no_gifts_no_transport = c["oop_12m_provider_base"] + c["oop_12m_medicines"] + c["oop_12m_lab"]
    return [
        {
            "policy_name": "oop_4w_provider_base_only",
            "recall_scope": "past_4_weeks",
            "annualization_factor": "1",
            "series": c["oop_4w_provider_base"],
            "included_components": "provider charges excluding gifts/medicines/lab/transport",
            "excluded_components": "gifts; medicines; lab; transport; all 12-month items",
            "source_variables": compact_join(FOUR_WEEK_PROVIDER_BASE),
            "formula": "sum(provider-charge four-week items only)",
        },
        {
            "policy_name": "oop_4w_no_gifts_with_transport",
            "recall_scope": "past_4_weeks",
            "annualization_factor": "1",
            "series": four_week_no_gifts_with_transport,
            "included_components": "provider charges; medicines; lab; transport; own-purchased drugs",
            "excluded_components": "gifts; all 12-month items",
            "source_variables": compact_join(FOUR_WEEK_PROVIDER_BASE + FOUR_WEEK_MEDICINES + FOUR_WEEK_LAB + FOUR_WEEK_TRANSPORT),
            "formula": "sum(four-week provider + medicine + lab + transport + own-drug items), excluding gifts",
        },
        {
            "policy_name": "oop_4w_all_observed_with_gifts_transport",
            "recall_scope": "past_4_weeks",
            "annualization_factor": "1",
            "series": four_week_all,
            "included_components": "provider charges; gifts; medicines; lab; transport; own-purchased drugs",
            "excluded_components": "all 12-month items",
            "source_variables": compact_join(FOUR_WEEK_PROVIDER_BASE + FOUR_WEEK_GIFTS + FOUR_WEEK_MEDICINES + FOUR_WEEK_LAB + FOUR_WEEK_TRANSPORT),
            "formula": "sum(all observed four-week payment items)",
        },
        {
            "policy_name": "oop_4w_no_gifts_no_transport",
            "recall_scope": "past_4_weeks",
            "annualization_factor": "1",
            "series": four_week_no_gifts_no_transport,
            "included_components": "provider charges; medicines; lab; own-purchased drugs",
            "excluded_components": "gifts; transport; all 12-month items",
            "source_variables": compact_join(FOUR_WEEK_PROVIDER_BASE + FOUR_WEEK_MEDICINES + FOUR_WEEK_LAB),
            "formula": "sum(four-week provider + medicine + lab + own-drug items), excluding gifts and transport",
        },
        {
            "policy_name": "oop_12m_provider_base_only",
            "recall_scope": "past_12_months_hospital_dentist",
            "annualization_factor": "1",
            "series": c["oop_12m_provider_base"],
            "included_components": "hospital-stay and dentist provider charges excluding gifts/medicines/lab/transport",
            "excluded_components": "gifts; medicines; lab; transport; all four-week outpatient/self-medication items",
            "source_variables": compact_join(TWELVE_MONTH_PROVIDER_BASE),
            "formula": "sum(provider-charge 12-month hospital and dentist items only)",
        },
        {
            "policy_name": "oop_12m_no_gifts_with_transport",
            "recall_scope": "past_12_months_hospital_dentist",
            "annualization_factor": "1",
            "series": twelve_no_gifts_with_transport,
            "included_components": "hospital/dentist provider charges; medicines; lab; transport",
            "excluded_components": "gifts; all four-week outpatient/self-medication items",
            "source_variables": compact_join(TWELVE_MONTH_PROVIDER_BASE + TWELVE_MONTH_MEDICINES + TWELVE_MONTH_LAB + TWELVE_MONTH_TRANSPORT),
            "formula": "sum(12-month hospital/dentist provider + medicine + lab + transport items), excluding gifts",
        },
        {
            "policy_name": "oop_12m_all_observed_with_gifts_transport",
            "recall_scope": "past_12_months_hospital_dentist",
            "annualization_factor": "1",
            "series": twelve_all,
            "included_components": "hospital/dentist provider charges; gifts; medicines; lab; transport",
            "excluded_components": "all four-week outpatient/self-medication items",
            "source_variables": compact_join(TWELVE_MONTH_PROVIDER_BASE + TWELVE_MONTH_GIFTS + TWELVE_MONTH_MEDICINES + TWELVE_MONTH_LAB + TWELVE_MONTH_TRANSPORT),
            "formula": "sum(all observed 12-month hospital/dentist payment items)",
        },
        {
            "policy_name": "oop_12m_no_gifts_no_transport",
            "recall_scope": "past_12_months_hospital_dentist",
            "annualization_factor": "1",
            "series": twelve_no_gifts_no_transport,
            "included_components": "hospital/dentist provider charges; medicines; lab",
            "excluded_components": "gifts; transport; all four-week outpatient/self-medication items",
            "source_variables": compact_join(TWELVE_MONTH_PROVIDER_BASE + TWELVE_MONTH_MEDICINES + TWELVE_MONTH_LAB),
            "formula": "sum(12-month hospital/dentist provider + medicine + lab items), excluding gifts and transport",
        },
        {
            "policy_name": "oop_annual_stress_no_gifts_with_transport",
            "recall_scope": "stress_annualized_four_week_plus_12m_hospital_dentist",
            "annualization_factor": "13_for_four_week_items_plus_1_for_12m_items",
            "series": (four_week_no_gifts_with_transport * 13) + twelve_no_gifts_with_transport,
            "included_components": "annualized four-week provider/medicine/lab/transport/own-drugs plus 12-month hospital/dentist provider/medicine/lab/transport",
            "excluded_components": "gifts",
            "source_variables": compact_join(FOUR_WEEK_PROVIDER_BASE + FOUR_WEEK_MEDICINES + FOUR_WEEK_LAB + FOUR_WEEK_TRANSPORT + TWELVE_MONTH_PROVIDER_BASE + TWELVE_MONTH_MEDICINES + TWELVE_MONTH_LAB + TWELVE_MONTH_TRANSPORT),
            "formula": "13 * four-week no-gifts-with-transport items + 12-month no-gifts-with-transport hospital/dentist items",
        },
        {
            "policy_name": "oop_annual_stress_all_observed_with_gifts_transport",
            "recall_scope": "stress_annualized_four_week_plus_12m_hospital_dentist",
            "annualization_factor": "13_for_four_week_items_plus_1_for_12m_items",
            "series": (four_week_all * 13) + twelve_all,
            "included_components": "annualized four-week all observed payment items plus 12-month hospital/dentist all observed payment items",
            "excluded_components": "none among observed payment items",
            "source_variables": compact_join(ALL_HEALTH_A_VARIABLES),
            "formula": "13 * all observed four-week payment items + all observed 12-month hospital/dentist payment items",
        },
        {
            "policy_name": "oop_annual_stress_no_gifts_no_transport",
            "recall_scope": "stress_annualized_four_week_plus_12m_hospital_dentist",
            "annualization_factor": "13_for_four_week_items_plus_1_for_12m_items",
            "series": (four_week_no_gifts_no_transport * 13) + twelve_no_gifts_no_transport,
            "included_components": "annualized four-week provider/medicine/lab/own-drugs plus 12-month hospital/dentist provider/medicine/lab",
            "excluded_components": "gifts; transport",
            "source_variables": compact_join(FOUR_WEEK_PROVIDER_BASE + FOUR_WEEK_MEDICINES + FOUR_WEEK_LAB + TWELVE_MONTH_PROVIDER_BASE + TWELVE_MONTH_MEDICINES + TWELVE_MONTH_LAB),
            "formula": "13 * four-week no-gifts-no-transport items + 12-month no-gifts-no-transport hospital/dentist items",
        },
    ]


def audit_row(candidate: pd.DataFrame, spec: dict[str, Any]) -> dict[str, str]:
    total = pd.to_numeric(candidate["total_consumption"], errors="coerce")
    weight = pd.to_numeric(candidate["household_weight"], errors="coerce")
    oop = pd.to_numeric(spec["series"], errors="coerce").fillna(0)
    denominator = total.notna() & (total > 0)
    positive = denominator & (oop > 0)
    share = (oop / total).where(denominator)
    che10 = denominator & (share > 0.10)
    che25 = denominator & (share > 0.25)
    oop_stats = nonmissing_quantiles(oop.where(denominator))
    share_stats = nonmissing_quantiles(share)
    weighted_denominator = float(weight.loc[denominator & weight.notna() & (weight > 0)].sum())
    return {
        "country": COUNTRY,
        "survey_name": SURVEY_NAME,
        "wave": WAVE,
        "idno": IDNO,
        "policy_name": spec["policy_name"],
        "recall_scope": spec["recall_scope"],
        "annualization_factor": spec["annualization_factor"],
        "included_components": spec["included_components"],
        "excluded_components": spec["excluded_components"],
        "source_variables": spec["source_variables"],
        "formula": spec["formula"],
        "household_rows": str(int(len(candidate))),
        "total_consumption_denominator_rows": str(int(denominator.sum())),
        "positive_oop_rows": str(int(positive.sum())),
        "positive_oop_rate": fmt(float(positive.sum() / denominator.sum())) if denominator.any() else "",
        "weighted_denominator": fmt(weighted_denominator),
        "weighted_positive_oop_rate": weighted_rate(oop > 0, denominator, weight),
        "mean_oop": oop_stats["mean"],
        "p50_oop": oop_stats["p50"],
        "p95_oop": oop_stats["p95"],
        "max_oop": oop_stats["max"],
        "mean_oop_share": share_stats["mean"],
        "p50_oop_share": share_stats["p50"],
        "p95_oop_share": share_stats["p95"],
        "max_oop_share": share_stats["max"],
        "che10_rows": str(int(che10.sum())),
        "che10_rate": fmt(float(che10.sum() / denominator.sum())) if denominator.any() else "",
        "che10_weighted_rate": weighted_rate(che10, denominator, weight),
        "che25_rows": str(int(che25.sum())),
        "che25_rate": fmt(float(che25.sum() / denominator.sum())) if denominator.any() else "",
        "che25_weighted_rate": weighted_rate(che25, denominator, weight),
        "ready_for_outcome": "0",
        "ready_for_recipe": "0",
        "climate_linkage_ready": "0",
        "promotion_status": NO_PROMOTION,
        "blocking_reason": (
            "Audit-only aggregation stress test. ALB_2005 still lacks final OOP inclusion policy, missing-code review, "
            "recall-period comparability, verified household interview timing, and climate-ready geography."
        ),
        "next_action": (
            "Use this table to choose and document an OOP inclusion policy only after consumption units, payment scope, "
            "gift/transport treatment, skip paths, timing, and geography are verified."
        ),
    }


def summary_row(metric: str, value: Any, interpretation: str) -> dict[str, str]:
    return {"metric": metric, "value": fmt(value), "interpretation": interpretation}


def build_summary(rows: list[dict[str, str]], candidate: pd.DataFrame) -> list[dict[str, str]]:
    questionnaire_summary = read_csv_dicts(QUESTIONNAIRE_SUMMARY_PATH)
    required_summary = read_csv_dicts(REQUIRED_VALUE_KEY_SUMMARY_PATH)
    timing_summary = read_csv_dicts(TIMING_GEO_SUMMARY_PATH)
    annual_rows = [row for row in rows if row["recall_scope"].startswith("stress_annualized")]
    max_che10 = max((float(row["che10_rate"]) for row in rows if row["che10_rate"]), default=0.0)
    max_che25 = max((float(row["che25_rate"]) for row in rows if row["che25_rate"]), default=0.0)
    return [
        summary_row("alb2005_oop_aggregation_policy_rows", len(rows), "Rows in the ALB_2005 OOP aggregation policy audit."),
        summary_row("alb2005_oop_aggregation_policy_household_rows", len(candidate), "Base household rows included in the stress test."),
        summary_row("alb2005_oop_aggregation_policy_total_consumption_rows", int((pd.to_numeric(candidate["total_consumption"], errors="coerce") > 0).sum()), "Households with positive total consumption denominator."),
        summary_row("alb2005_oop_aggregation_policy_four_week_policy_rows", sum(1 for row in rows if row["recall_scope"] == "past_4_weeks"), "Four-week OOP aggregation policies."),
        summary_row("alb2005_oop_aggregation_policy_twelve_month_policy_rows", sum(1 for row in rows if row["recall_scope"] == "past_12_months_hospital_dentist"), "Twelve-month hospital/dentist OOP aggregation policies."),
        summary_row("alb2005_oop_aggregation_policy_annual_stress_rows", len(annual_rows), "Annualized stress-test policies combining four-week and 12-month items."),
        summary_row("alb2005_oop_aggregation_policy_max_che10_rate", max_che10, "Maximum unweighted CHE10 stress-test rate across policies."),
        summary_row("alb2005_oop_aggregation_policy_max_che25_rate", max_che25, "Maximum unweighted CHE25 stress-test rate across policies."),
        summary_row("alb2005_oop_aggregation_policy_questionnaire_oop_item_rows_observed", metric_value(questionnaire_summary, "alb2005_health_questionnaire_oop_item_rows"), "Questionnaire OOP item rows observed upstream."),
        summary_row("alb2005_oop_aggregation_policy_questionnaire_old_lek_rows_observed", metric_value(questionnaire_summary, "alb2005_health_questionnaire_old_lek_unit_rows"), "Questionnaire old-lek unit rows observed upstream."),
        summary_row("alb2005_oop_aggregation_policy_required_value_key_recipe_ready_observed", metric_value(required_summary, "alb2005_required_value_key_recipe_ready_rows"), "Recipe-ready rows observed in the required value/key audit."),
        summary_row("alb2005_oop_aggregation_policy_timing_verified_rows_observed", metric_value(required_summary, "alb2005_required_value_key_interview_timing_verified_rows"), "Verified interview-timing rows observed in the required value/key audit."),
        summary_row("alb2005_oop_aggregation_policy_climate_ready_rows_observed", metric_value(timing_summary, "alb2005_climate_linkage_ready_rows"), "Climate-linkage-ready rows observed in the timing/geography audit."),
        summary_row("alb2005_oop_aggregation_policy_outcome_ready_rows", 0, "Rows promoted to final outcome construction by this audit; intentionally zero."),
        summary_row("alb2005_oop_aggregation_policy_recipe_ready_rows", 0, "Rows promoted to harmonization recipe by this audit; intentionally zero."),
        summary_row("alb2005_oop_aggregation_policy_climate_linkage_ready_rows", 0, "Rows promoted to climate linkage by this audit; intentionally zero."),
        summary_row("alb2005_oop_aggregation_policy_current_decision", DECISION, "Current fail-closed decision for ALB_2005 OOP aggregation stress tests."),
    ]


def markdown_rows(rows: list[dict[str, str]], columns: list[str], limit: int = 20) -> str:
    lines = ["| " + " | ".join(columns) + " |", "|" + "|".join("---" for _ in columns) + "|"]
    for row in rows[:limit]:
        values = []
        for column in columns:
            value = (row.get(column, "") or "").replace("|", "/")
            if len(value) > 140:
                value = value[:137] + "..."
            values.append(value)
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines)


def write_report(rows: list[dict[str, str]], summary: list[dict[str, str]]) -> None:
    summary_table = "\n".join(f"| {row['metric']} | {row['value']} | {row['interpretation']} |" for row in summary)
    report = f"""# ALB_2005 OOP Aggregation Policy Audit

Status: fail-closed outcome-construction stress test. This audit uses ALB_2005 raw health-payment values and questionnaire-derived payment-scope evidence to compare OOP aggregation policies. It does not write `data/`, does not construct final CHE/SDG outcomes, and does not promote any row to harmonization, outcome, or climate linkage.

## Bottom Line

- The audit separates provider charges, gifts, medicines, laboratory work, transport, and own-purchased drugs instead of blindly summing all health-module payment fields.
- It compares four-week, 12-month hospital/dentist, and annualized stress-test OOP policies against the available `totcons` denominator.
- These are stress tests only. They remain blocked by final OOP inclusion policy, missing-code semantics, recall-period comparability, verified household interview timing, and climate-ready geography.
- Outcome-ready, recipe-ready, and climate-linkage-ready rows from this audit: 0.
- Current decision: `{DECISION}`.

## Summary

| Metric | Value | Interpretation |
|---|---:|---|
{summary_table}

## Policy Stress Tests

{markdown_rows(rows, ['policy_name', 'recall_scope', 'included_components', 'positive_oop_rows', 'che10_rows', 'che10_rate', 'che25_rows', 'che25_rate', 'p95_oop_share'], 20)}

## Interpretation

- Four-week policies are not directly comparable to annual total consumption unless an annualization rule is explicitly justified.
- The 12-month hospital/dentist policies omit four-week outpatient, provider, and self-medication spending unless combined in a documented stress-test rule.
- Gift and transport inclusion materially define the policy estimand and must be chosen before any financial-protection outcome is promoted.
- The available positive rates and CHE rates are useful for event-rate screening, not for manuscript claims.

## Machine-Readable Outputs

- `temp/alb2005_oop_aggregation_policy_audit.csv`
- `result/alb2005_oop_aggregation_policy_summary.csv`
"""
    REPORT_PATH.write_text(report, encoding="utf-8")


def main() -> None:
    ensure_dirs()
    candidate = build_candidate()
    rows = [audit_row(candidate, spec) for spec in policy_specs(candidate)]
    summary = build_summary(rows, candidate)
    write_csv(AUDIT_PATH, rows, AUDIT_COLUMNS)
    write_csv(SUMMARY_PATH, summary, SUMMARY_COLUMNS)
    write_report(rows, summary)
    append_log(TEMP_DIR / "audit_log.md", f"Built ALB_2005 OOP aggregation policy audit rows={len(rows)} decision={DECISION}.")
    print(f"ALB_2005 OOP aggregation policy rows={len(rows)} decision={DECISION}.")


if __name__ == "__main__":
    main()
