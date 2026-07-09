from __future__ import annotations

import csv
import math
import warnings
from collections import Counter
from pathlib import Path
from typing import Any

import pandas as pd

from common import REPORT_DIR, RESULT_DIR, TEMP_DIR, append_log, ensure_dirs, write_csv

try:
    import pyreadstat
except ImportError:  # pragma: no cover - environment audit reports this separately.
    pyreadstat = None


IDNO = "ALB_2005_LSMS_v01_M"
COUNTRY = "Albania"
SURVEY_NAME = "Living Standards Measurement Survey 2005"
WAVE = "2005"
RAW_ROOT = TEMP_DIR / "raw_extracted" / "lsms2005en_1e7f1965c4a5" / "lsms2005en" / "Data_2005"

TIMING_GEO_SUMMARY_PATH = RESULT_DIR / "alb2005_timing_geography_exhaustive_summary.csv"
VALUE_DECISION_SUMMARY_PATH = RESULT_DIR / "alb2005_harmonization_value_decision_summary.csv"
AUDIT_PATH = TEMP_DIR / "alb2005_required_value_key_audit.csv"
SUMMARY_PATH = RESULT_DIR / "alb2005_required_value_key_summary.csv"
REPORT_PATH = REPORT_DIR / "alb2005_required_value_key_audit.md"

DECISION = "blocked_alb2005_required_values_seen_but_recipe_not_ready"
NO_PROMOTION = "not_promoted_fail_closed"

FOUR_WEEK_OOP = [
    "m9a_q16",
    "m9a_q17",
    "m9a_q20",
    "m9a_q22",
    "m9a_q23",
    "m9a_q28",
    "m9a_q29",
    "m9a_q32",
    "m9a_q34",
    "m9a_q35",
    "m9a_q38",
    "m9a_q39",
    "m9a_q41",
    "m9a_q42",
    "m9a_q43",
    "m9a_q46",
    "m9a_q47",
    "m9a_q49",
    "m9a_q50",
    "m9a_q51",
    "m9a_q54",
    "m9a_q55",
    "m9a_q57",
    "m9a_q58",
    "m9a_q59",
    "m9a_q61",
]
TWELVE_MONTH_OOP = [
    "m9a_q68",
    "m9a_q69",
    "m9a_q71",
    "m9a_q72",
    "m9a_q73",
    "m9a_q76",
    "m9a_q77",
    "m9a_q79",
    "m9a_q80",
    "m9a_q81",
]

AUDIT_COLUMNS = [
    "country",
    "survey_name",
    "wave",
    "idno",
    "concept",
    "harmonized_variable",
    "source_file",
    "raw_variables",
    "evidence_role",
    "row_count",
    "complete_key_rows",
    "distinct_key_count",
    "duplicate_key_rows",
    "base_rows",
    "base_rows_matched",
    "base_match_rate",
    "nonmissing_rows",
    "missing_rows",
    "nonmissing_rate",
    "distinct_values",
    "min_value",
    "max_value",
    "mean_value",
    "positive_numeric_rows",
    "zero_numeric_rows",
    "negative_numeric_rows",
    "top_values",
    "value_label_examples",
    "coverage_status",
    "value_status",
    "recipe_gate_status",
    "ready_for_recipe",
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


def compact_join(values: list[Any], limit: int = 12) -> str:
    out: list[str] = []
    seen: set[str] = set()
    for value in values:
        clean = " ".join(str(value).replace("\n", " ").split())
        if not clean or clean in seen:
            continue
        out.append(clean)
        seen.add(clean)
        if len(out) >= limit:
            break
    return "; ".join(out)


def read_sav(file_name: str, usecols: list[str] | None = None) -> tuple[pd.DataFrame, Any]:
    if pyreadstat is None:
        raise RuntimeError("pyreadstat is not available")
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        return pyreadstat.read_sav(str(RAW_ROOT / file_name), usecols=usecols, apply_value_formats=False)


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


def value_label_examples(meta: Any, variable: str, limit: int = 10) -> str:
    label_name = getattr(meta, "variable_to_label", {}).get(variable)
    labels = getattr(meta, "value_labels", {}).get(label_name, {}) if label_name else {}
    return compact_join([f"{fmt(code)}={label}" for code, label in labels.items()], limit)


def top_values(series: pd.Series, limit: int = 8) -> str:
    values = series.map(lambda v: "<missing>" if fmt(v) == "" else fmt(v))
    counts = values.value_counts(dropna=False).head(limit)
    return compact_join([f"{idx}:{int(count)}" for idx, count in counts.items()], limit)


def numeric_stats(series: pd.Series) -> dict[str, str]:
    numeric = pd.to_numeric(series, errors="coerce")
    nonmissing = numeric.dropna()
    return {
        "nonmissing_rows": str(int(nonmissing.shape[0])),
        "missing_rows": str(int(series.shape[0] - nonmissing.shape[0])),
        "nonmissing_rate": f"{nonmissing.shape[0] / series.shape[0]:.6f}" if series.shape[0] else "0",
        "distinct_values": str(int(nonmissing.nunique(dropna=True))),
        "min_value": fmt(nonmissing.min()) if len(nonmissing) else "",
        "max_value": fmt(nonmissing.max()) if len(nonmissing) else "",
        "mean_value": f"{nonmissing.mean():.6g}" if len(nonmissing) else "",
        "positive_numeric_rows": str(int((nonmissing > 0).sum())),
        "zero_numeric_rows": str(int((nonmissing == 0).sum())),
        "negative_numeric_rows": str(int((nonmissing < 0).sum())),
    }


def generic_stats(series: pd.Series) -> dict[str, str]:
    missing = series.map(lambda v: fmt(v) == "")
    nonmissing = series[~missing]
    numeric = numeric_stats(series)
    numeric["nonmissing_rows"] = str(int(nonmissing.shape[0]))
    numeric["missing_rows"] = str(int(missing.sum()))
    numeric["nonmissing_rate"] = f"{nonmissing.shape[0] / series.shape[0]:.6f}" if series.shape[0] else "0"
    numeric["distinct_values"] = str(int(nonmissing.map(fmt).nunique(dropna=True)))
    return numeric


def base_row(concept: str, harmonized_variable: str, source_file: str, raw_variables: str, evidence_role: str) -> dict[str, str]:
    return {
        "country": COUNTRY,
        "survey_name": SURVEY_NAME,
        "wave": WAVE,
        "idno": IDNO,
        "concept": concept,
        "harmonized_variable": harmonized_variable,
        "source_file": source_file,
        "raw_variables": raw_variables,
        "evidence_role": evidence_role,
        "row_count": "0",
        "complete_key_rows": "0",
        "distinct_key_count": "0",
        "duplicate_key_rows": "0",
        "base_rows": "0",
        "base_rows_matched": "0",
        "base_match_rate": "0",
        "nonmissing_rows": "0",
        "missing_rows": "0",
        "nonmissing_rate": "0",
        "distinct_values": "0",
        "min_value": "",
        "max_value": "",
        "mean_value": "",
        "positive_numeric_rows": "0",
        "zero_numeric_rows": "0",
        "negative_numeric_rows": "0",
        "top_values": "",
        "value_label_examples": "",
        "coverage_status": "not_verified",
        "value_status": "not_verified",
        "recipe_gate_status": "blocked_required_value_key_review",
        "ready_for_recipe": "0",
        "promotion_status": NO_PROMOTION,
        "blocking_reason": "Required ALB_2005 value/key evidence is not sufficient for harmonization recipe promotion.",
        "next_action": "Review raw values, units, recall periods, missing codes, merge keys, timing, and geography before any promotion.",
    }


def key_audit_row(
    concept: str,
    harmonized_variable: str,
    source_file: str,
    raw_variables: str,
    key_series: pd.Series,
    base_keys: set[str],
    allow_duplicates: bool,
    blocking_reason: str,
    next_action: str,
) -> dict[str, str]:
    row = base_row(concept, harmonized_variable, source_file, raw_variables, "merge_key_cardinality_and_coverage")
    keys = key_series.map(key_part)
    complete = keys != ""
    complete_rows = int(complete.sum())
    distinct = int(keys[complete].nunique(dropna=True))
    duplicates = max(complete_rows - distinct, 0)
    observed = set(keys[complete])
    matched = len(observed.intersection(base_keys))
    if complete_rows == 0:
        coverage = "blocked_no_complete_key_values"
    elif duplicates > 0 and not allow_duplicates:
        coverage = "blocked_duplicate_household_keys"
    elif matched == len(base_keys) and len(base_keys) > 0:
        coverage = "complete_base_key_coverage_value_review_required"
    elif matched > 0:
        coverage = "partial_base_key_coverage_value_review_required"
    else:
        coverage = "blocked_no_base_key_matches"
    row.update(
        {
            "row_count": str(int(key_series.shape[0])),
            "complete_key_rows": str(complete_rows),
            "distinct_key_count": str(distinct),
            "duplicate_key_rows": str(duplicates),
            "base_rows": str(len(base_keys)),
            "base_rows_matched": str(matched),
            "base_match_rate": f"{matched / len(base_keys):.6f}" if base_keys else "0",
            "coverage_status": coverage,
            "value_status": "key_values_seen_cardinality_review_required",
            "blocking_reason": blocking_reason,
            "next_action": next_action,
        }
    )
    return row


def variable_audit_row(
    concept: str,
    harmonized_variable: str,
    source_file: str,
    raw_variables: str,
    series: pd.Series,
    meta: Any,
    variable_for_labels: str,
    coverage_status: str,
    value_status: str,
    blocking_reason: str,
    next_action: str,
    numeric: bool = True,
) -> dict[str, str]:
    row = base_row(concept, harmonized_variable, source_file, raw_variables, "raw_value_distribution")
    stats = numeric_stats(series) if numeric else generic_stats(series)
    row.update(stats)
    row.update(
        {
            "row_count": str(int(series.shape[0])),
            "top_values": top_values(series),
            "value_label_examples": value_label_examples(meta, variable_for_labels),
            "coverage_status": coverage_status,
            "value_status": value_status,
            "blocking_reason": blocking_reason,
            "next_action": next_action,
        }
    )
    return row


def build_rows() -> list[dict[str, str]]:
    filters_cl, filters_cl_meta = read_sav("filters_cl.sav", ["M0_Q00", "M0_Q01", "HHID"])
    filters_cl = add_hhid_key(add_psu_hh_key(filters_cl, "M0_Q00", "M0_Q01"), "HHID")
    base_hhid = set(filters_cl.loc[filters_cl["hhid_key"] != "", "hhid_key"])
    base_psu_hh = set(filters_cl.loc[filters_cl["psu_hh_key"] != "", "psu_hh_key"])
    base_psu = set(filters_cl.loc[filters_cl["psu_key"] != "", "psu_key"])

    rows: list[dict[str, str]] = []
    rows.append(
        key_audit_row(
            "household_id",
            "hhid",
            "filters_cl.sav",
            "M0_Q00;M0_Q01;HHID",
            filters_cl["hhid_key"],
            base_hhid,
            allow_duplicates=False,
            blocking_reason="The base household key is internally unique in filters_cl.sav, but cross-file joins and raw value semantics still require review before recipe promotion.",
            next_action="Use this as the reference key only after linked poverty, health, geography, and weight files pass the same key audit.",
        )
    )
    rows[-1]["value_label_examples"] = value_label_examples(filters_cl_meta, "HHID")

    poverty, poverty_meta = read_sav("poverty.sav", ["PSU", "hh", "totcons", "rfood", "rnfood", "weight_retro"])
    poverty = add_psu_hh_key(poverty, "PSU", "hh")
    rows.append(
        key_audit_row(
            "household_id",
            "hhid",
            "poverty.sav",
            "PSU;hh",
            poverty["psu_hh_key"],
            base_psu_hh,
            allow_duplicates=False,
            blocking_reason="The poverty aggregate joins to most but not all base households; denominator construction cannot ignore missing aggregate coverage.",
            next_action="Explain why poverty.sav has fewer households than filters_cl.sav before using totcons as a universal denominator.",
        )
    )
    rows.append(
        variable_audit_row(
            "total_consumption_or_income",
            "total_consumption",
            "poverty.sav",
            "totcons",
            poverty["totcons"],
            poverty_meta,
            "totcons",
            "poverty_rows_partial_base_coverage",
            "raw_total_consumption_seen_unit_period_review_required",
            "Total consumption values are observed, but old/new lek scaling, household-total interpretation, period, missing rules, and denominator use remain unverified.",
            "Confirm currency unit, price basis, period, and household-total interpretation from documentation before any SDG/CHE denominator construction.",
        )
    )
    rows.append(
        variable_audit_row(
            "total_consumption_or_income",
            "food_consumption",
            "poverty.sav",
            "rfood",
            poverty["rfood"],
            poverty_meta,
            "rfood",
            "poverty_rows_partial_base_coverage",
            "raw_component_seen_scope_review_required",
            "The food component is visible but appears to be a component/per-capita-style measure; it is not verified as a direct household-total component.",
            "Review poverty aggregate documentation and reconstruction rules before using food consumption in outcomes or subgroup analysis.",
        )
    )
    rows.append(
        variable_audit_row(
            "total_consumption_or_income",
            "nonfood_consumption",
            "poverty.sav",
            "rnfood",
            poverty["rnfood"],
            poverty_meta,
            "rnfood",
            "poverty_rows_partial_base_coverage",
            "raw_component_seen_scope_review_required",
            "The nonfood component is visible but not verified as a direct household-total component.",
            "Review poverty aggregate documentation and reconstruction rules before using nonfood consumption in outcomes or subgroup analysis.",
        )
    )
    missing_income = base_row("total_consumption_or_income", "total_income", "", "", "required_variable_absent")
    missing_income.update(
        {
            "base_rows": str(len(base_hhid)),
            "coverage_status": "blocked_no_verified_total_income_candidate",
            "value_status": "absent_not_substitutable_with_consumption",
            "blocking_reason": "No verified ALB_2005 total income aggregate is identified; consumption evidence must not be relabeled as income.",
            "next_action": "Use consumption only where the outcome protocol allows consumption denominators, and keep income missing otherwise.",
        }
    )
    rows.append(missing_income)

    rows.append(
        variable_audit_row(
            "survey_weight",
            "household_weight",
            "poverty.sav",
            "weight_retro",
            poverty["weight_retro"],
            poverty_meta,
            "weight_retro",
            "poverty_rows_partial_base_coverage",
            "raw_weight_seen_design_review_required",
            "The poverty file includes weight_retro, but official survey-design use, population, and merge coverage still require review.",
            "Verify design documentation and decide whether household or person weights are needed before any weighted prevalence or model.",
        )
    )
    weight, weight_meta = read_sav("Weight_retro_2005.sav", ["psu", "weight_retro"])
    weight["psu_key"] = weight["psu"].map(key_part)
    rows.append(
        key_audit_row(
            "survey_weight",
            "household_weight",
            "Weight_retro_2005.sav",
            "psu;weight_retro",
            weight["psu_key"],
            base_psu,
            allow_duplicates=False,
            blocking_reason="The separate weight file is PSU-level, not household-level; design interpretation and household merge rules remain unresolved.",
            next_action="Confirm whether PSU-level weight_retro is intended to be assigned to all households in each PSU or only used through poverty.sav.",
        )
    )
    rows.append(
        variable_audit_row(
            "survey_weight",
            "household_weight",
            "Weight_retro_2005.sav",
            "weight_retro",
            weight["weight_retro"],
            weight_meta,
            "weight_retro",
            "psu_level_weight_file_seen",
            "raw_psu_weight_seen_design_review_required",
            "The separate weight file has one row per PSU, not a directly verified household weight row.",
            "Resolve survey-design documentation and merge level before any weighted analysis.",
        )
    )

    healtha, healtha_meta = read_sav("Modul_9A_healtha_cl.sav", ["hhid", *FOUR_WEEK_OOP, *TWELVE_MONTH_OOP])
    healtha = add_hhid_key(healtha, "hhid")
    rows.append(
        key_audit_row(
            "oop_health_expenditure",
            "oop_health_expenditure",
            "Modul_9A_healtha_cl.sav",
            "hhid",
            healtha["hhid_key"],
            base_hhid,
            allow_duplicates=True,
            blocking_reason="The health A file links to base households but is person-level; person-to-household aggregation and skip paths remain unresolved.",
            next_action="Verify the eligible person denominator and skip pattern for each payment item before aggregating OOP to households.",
        )
    )
    four_week_person = healtha[FOUR_WEEK_OOP].apply(pd.to_numeric, errors="coerce").fillna(0).sum(axis=1)
    twelve_month_person = healtha[TWELVE_MONTH_OOP].apply(pd.to_numeric, errors="coerce").fillna(0).sum(axis=1)
    four_week_household = four_week_person.groupby(healtha["hhid_key"]).sum()
    twelve_month_household = twelve_month_person.groupby(healtha["hhid_key"]).sum()
    rows.append(
        variable_audit_row(
            "oop_health_expenditure",
            "oop_health_expenditure_4w_component_sum",
            "Modul_9A_healtha_cl.sav",
            compact_join(FOUR_WEEK_OOP, 40),
            four_week_person,
            healtha_meta,
            "m9a_q16",
            "person_level_health_file_complete_base_coverage",
            "raw_person_payment_values_seen_aggregation_review_required",
            "Four-week health payment items are visible, but item scope, gift inclusion, zero/missing coding, and person-to-household aggregation are not yet validated.",
            "Map each payment variable to care context and questionnaire skip paths before constructing a household OOP measure.",
        )
    )
    rows.append(
        variable_audit_row(
            "oop_health_expenditure",
            "oop_health_expenditure_4w_household_sum_unreviewed",
            "Modul_9A_healtha_cl.sav",
            compact_join(FOUR_WEEK_OOP, 40),
            four_week_household,
            healtha_meta,
            "m9a_q16",
            "household_aggregate_computed_for_audit_only",
            "audit_only_household_sum_not_analysis_ready",
            "A household four-week sum can be computed for auditing, but it is not a validated outcome because component semantics and skip paths remain unresolved.",
            "Keep this as an audit-only distribution until an explicit OOP aggregation rule is approved.",
        )
    )
    rows.append(
        variable_audit_row(
            "oop_health_expenditure",
            "oop_health_expenditure_12m_component_sum",
            "Modul_9A_healtha_cl.sav",
            compact_join(TWELVE_MONTH_OOP, 40),
            twelve_month_person,
            healtha_meta,
            "m9a_q68",
            "person_level_health_file_complete_base_coverage",
            "raw_person_payment_values_seen_aggregation_review_required",
            "Twelve-month inpatient/dentist payment items are visible, but they cannot be pooled with four-week items without a documented period rule.",
            "Keep recall-period-specific OOP evidence separate unless annualization is justified.",
        )
    )
    rows.append(
        variable_audit_row(
            "oop_health_expenditure",
            "oop_health_expenditure_12m_household_sum_unreviewed",
            "Modul_9A_healtha_cl.sav",
            compact_join(TWELVE_MONTH_OOP, 40),
            twelve_month_household,
            healtha_meta,
            "m9a_q68",
            "household_aggregate_computed_for_audit_only",
            "audit_only_household_sum_not_analysis_ready",
            "A household twelve-month sum can be computed for auditing, but it is not a validated outcome because recall period and component scope remain unresolved.",
            "Keep annual payment items separate from four-week items until an outcome protocol is verified.",
        )
    )

    healthb_vars = ["hhid", "m9b_q01", "m9b_q04", "m9b_q05", "m9b_q06", "m9b_q07", "m9b_q08"]
    healthb, healthb_meta = read_sav("Modul_9B_healthb_cl.sav", healthb_vars)
    healthb = add_hhid_key(healthb, "hhid")
    rows.append(
        key_audit_row(
            "care_or_barrier",
            "care_access_barriers",
            "Modul_9B_healthb_cl.sav",
            "hhid",
            healthb["hhid_key"],
            base_hhid,
            allow_duplicates=False,
            blocking_reason="The health B household module covers base households, but access-denominator and conditional reason skip paths remain unresolved.",
            next_action="Use value labels with questionnaire skip logic before constructing forgone-care or barrier outcomes.",
        )
    )
    for variable, harmonized, reason, action in [
        ("m9b_q01", "difficulty_paying_for_health", "Difficulty-paying values include a no-one-needed-care category, so the denominator is not a simple need sample.", "Define the eligible health-need denominator before using this as UHC access/financial hardship evidence."),
        ("m9b_q04", "delayed_help_reason", "Delay-reason values are conditional on delayed help and require skip-pattern denominators.", "Confirm which households were asked this item and map cost/distance codes only within that denominator."),
        ("m9b_q05", "hospital_referral_not_gone_count", "Referral nonuse counts are not equivalent to all forgone care and require denominator review.", "Verify referral eligibility and count coding before constructing an access outcome."),
        ("m9b_q06", "hospital_referral_not_gone_reason", "Referral nonuse reasons include cost and distance codes but are conditional on nonuse.", "Use this only after verifying the m9b_q05 skip path and referral denominator."),
        ("m9b_q07", "refused_health_services", "Refused-service status is a useful access proxy but not equivalent to care need or care seeking.", "Verify refusal context and denominator before using as a supply/access barrier."),
        ("m9b_q08", "refused_health_services_reason", "Refusal reasons include cost/distance-like categories but are conditional on refusal.", "Map reason codes only after confirming the refusal denominator."),
    ]:
        rows.append(
            variable_audit_row(
                "care_or_barrier",
                harmonized,
                "Modul_9B_healthb_cl.sav",
                variable,
                healthb[variable],
                healthb_meta,
                variable,
                "household_module_complete_base_coverage",
                "categorical_values_seen_skip_pattern_review_required",
                reason,
                action,
            )
        )

    filters, filters_meta = read_sav("filters.sav", ["P0_Q00", "P0_Q01", "P11_Q5A", "P11_Q5B"])
    filters = add_psu_hh_key(filters, "P0_Q00", "P0_Q01")
    rows.append(
        key_audit_row(
            "climate_geography",
            "admin2",
            "filters.sav",
            "P0_Q00;P0_Q01;P11_Q5A;P11_Q5B",
            filters["psu_hh_key"],
            base_psu_hh,
            allow_duplicates=False,
            blocking_reason="The filters geography module covers only part of the base household roster and district values are sparse.",
            next_action="Resolve why only a subset has current district values and obtain a verified historical boundary or GPS/EA crosswalk before climate linkage.",
        )
    )
    rows.append(
        variable_audit_row(
            "climate_geography",
            "admin2_name",
            "filters.sav",
            "P11_Q5A",
            filters["P11_Q5A"],
            filters_meta,
            "P11_Q5A",
            "partial_household_geography",
            "raw_partial_district_name_seen_not_climate_ready",
            "District-name values exist only for a subset of filters.sav rows and are not a verified climate geography.",
            "Check full coverage and historical boundary consistency before using names for admin climate aggregation.",
            numeric=False,
        )
    )
    rows.append(
        variable_audit_row(
            "climate_geography",
            "admin2_code",
            "filters.sav",
            "P11_Q5B",
            filters["P11_Q5B"],
            filters_meta,
            "P11_Q5B",
            "partial_household_geography",
            "raw_partial_district_code_seen_not_climate_ready",
            "District-code values have labels, but coverage is partial and no verified 2005 boundary/GPS artifact is joined.",
            "Audit historical district polygons and no-GPS measurement error before any climate aggregation.",
        )
    )
    coordinate = base_row("climate_geography", "latitude;longitude", "", "", "required_coordinate_absent")
    coordinate.update(
        {
            "base_rows": str(len(base_hhid)),
            "coverage_status": "blocked_no_gps_or_coordinate_variable",
            "value_status": "absent_not_climate_ready",
            "blocking_reason": "No ALB_2005 latitude, longitude, GPS, or coordinate raw variable is verified in the local extracted files.",
            "next_action": "Use only verified GPS or a documented admin/EA boundary crosswalk; do not infer coordinates from PSU or district labels.",
        }
    )
    rows.append(coordinate)

    timing_summary = read_csv_dicts(TIMING_GEO_SUMMARY_PATH)
    timing = base_row("survey_timing", "survey_month;interview_date", "", "", "required_interview_timing_absent")
    timing.update(
        {
            "row_count": metric_value(timing_summary, "alb2005_interview_timing_candidate_rows", "0"),
            "nonmissing_rows": metric_value(timing_summary, "alb2005_interview_timing_verified_rows", "0"),
            "base_rows": str(len(base_hhid)),
            "coverage_status": "blocked_no_verified_household_interview_month_or_date",
            "value_status": "absent_not_climate_exposure_ready",
            "blocking_reason": "No verified raw household interview month/date exists for ALB_2005; recall-period and birth/event dates cannot define climate exposure windows.",
            "next_action": "Find a raw interview timing field or defensible official fieldwork calendar before any climate-linked recipe.",
        }
    )
    rows.append(timing)
    return rows


def summary_row(metric: str, value: Any, interpretation: str) -> dict[str, str]:
    return {"metric": metric, "value": fmt(value), "interpretation": interpretation}


def build_summary(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    concepts = Counter(row["concept"] for row in rows)
    coverage = Counter(row["coverage_status"] for row in rows)
    values = Counter(row["value_status"] for row in rows)
    value_decision = read_csv_dicts(VALUE_DECISION_SUMMARY_PATH)
    summary = [
        summary_row("alb2005_required_value_key_audit_rows", len(rows), "Rows in the ALB_2005 required value/key audit."),
        summary_row("alb2005_required_value_key_recipe_ready_rows", 0, "Rows promoted to a harmonization recipe by this audit; intentionally zero."),
        summary_row("alb2005_required_value_key_not_promoted_rows", len(rows), "Rows kept fail-closed after raw value/key inspection."),
        summary_row("alb2005_required_value_key_base_households", next((row["base_rows"] for row in rows if row["concept"] == "household_id"), "0"), "Base household rows from filters_cl.sav."),
        summary_row("alb2005_required_value_key_total_consumption_nonmissing_rows", next((row["nonmissing_rows"] for row in rows if row["harmonized_variable"] == "total_consumption"), "0"), "Nonmissing totcons values in poverty.sav."),
        summary_row("alb2005_required_value_key_oop_4w_household_positive_rows", next((row["positive_numeric_rows"] for row in rows if row["harmonized_variable"] == "oop_health_expenditure_4w_household_sum_unreviewed"), "0"), "Audit-only households with positive four-week OOP sum."),
        summary_row("alb2005_required_value_key_oop_12m_household_positive_rows", next((row["positive_numeric_rows"] for row in rows if row["harmonized_variable"] == "oop_health_expenditure_12m_household_sum_unreviewed"), "0"), "Audit-only households with positive twelve-month OOP sum."),
        summary_row("alb2005_required_value_key_district_code_nonmissing_rows", next((row["nonmissing_rows"] for row in rows if row["harmonized_variable"] == "admin2_code"), "0"), "Nonmissing partial district-code rows in filters.sav."),
        summary_row("alb2005_required_value_key_interview_timing_verified_rows", next((row["nonmissing_rows"] for row in rows if row["concept"] == "survey_timing"), "0"), "Verified household interview timing rows."),
        summary_row("alb2005_required_value_key_coordinate_ready_rows", 0, "Verified GPS/coordinate rows ready for climate linkage; intentionally zero."),
        summary_row("alb2005_required_value_key_climate_linkage_ready_rows", 0, "Rows ready for climate linkage after this audit; intentionally zero."),
        summary_row("alb2005_required_value_key_current_decision", DECISION, "Current fail-closed decision for ALB_2005 value/key evidence."),
        summary_row("alb2005_value_decision_recipe_ready_rows_observed", metric_value(value_decision, "alb2005_harmonization_value_decision_recipe_ready_rows", "0"), "Recipe-ready rows observed in the upstream value-decision audit."),
        summary_row("alb2005_value_decision_required_blocked_rows_observed", metric_value(value_decision, "alb2005_harmonization_value_decision_required_blocked_rows", "0"), "Required blocked rows observed in the upstream value-decision audit."),
    ]
    for concept, count in sorted(concepts.items()):
        summary.append(summary_row(f"alb2005_required_value_key_concept_{concept}", count, "Rows by audit concept."))
    for status, count in sorted(coverage.items()):
        summary.append(summary_row(f"alb2005_required_value_key_coverage_{status}", count, "Rows by coverage status."))
    for status, count in sorted(values.items()):
        summary.append(summary_row(f"alb2005_required_value_key_value_status_{status}", count, "Rows by value status."))
    return summary


def markdown_rows(rows: list[dict[str, str]], columns: list[str], limit: int = 20) -> str:
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


def write_report(rows: list[dict[str, str]], summary: list[dict[str, str]]) -> None:
    summary_table = "\n".join(f"| {row['metric']} | {row['value']} | {row['interpretation']} |" for row in summary)
    key_rows = [row for row in rows if row["evidence_role"] == "merge_key_cardinality_and_coverage"]
    value_rows = [row for row in rows if row["evidence_role"] == "raw_value_distribution"]
    absent_rows = [row for row in rows if "absent" in row["evidence_role"]]
    REPORT_PATH.write_text(
        f"""# ALB_2005 Required Value/Key Audit

Status: fail-closed raw value/key evidence audit. This audit reads ALB_2005 local raw SPSS files and records key coverage, candidate value distributions, value labels, and hard blockers for the minimum harmonization recipe. It does not write `data/`, does not construct validated outcomes, and does not promote any row to a recipe.

## Bottom Line

- Raw values are visible for household keys, total consumption, poverty weights, health payment items, selected access-barrier variables, and partial district codes.
- Recipe-ready rows from this audit: 0.
- Binding blockers remain: no verified household interview month/date, no GPS/coordinate variable, partial district coverage, unresolved OOP aggregation and recall semantics, unresolved consumption unit/period interpretation, and survey-design review.
- Current decision: `{DECISION}`.

## Summary

| Metric | Value | Interpretation |
|---|---:|---|
{summary_table}

## Key Coverage Rows

{markdown_rows(key_rows, ['concept', 'harmonized_variable', 'source_file', 'raw_variables', 'row_count', 'distinct_key_count', 'duplicate_key_rows', 'base_rows_matched', 'base_match_rate', 'coverage_status'], 20)}

## Value Evidence Rows

{markdown_rows(value_rows, ['concept', 'harmonized_variable', 'source_file', 'raw_variables', 'nonmissing_rows', 'positive_numeric_rows', 'max_value', 'top_values', 'value_status'], 24)}

## Explicit Absence Rows

{markdown_rows(absent_rows, ['concept', 'harmonized_variable', 'coverage_status', 'value_status', 'blocking_reason'], 10)}

## Interpretation

- `totcons`, `rfood`, and `rnfood` are observed in `poverty.sav`, but documentation must still verify unit, period, and household-total interpretation before financial-protection denominators are constructed.
- Health payment items are observed in `Modul_9A_healtha_cl.sav`, but four-week and twelve-month recall items must remain separate until a documented aggregation rule exists.
- Access-barrier value labels in `Modul_9B_healthb_cl.sav` contain cost and distance categories, but the denominator is conditional and must be reconstructed from questionnaire skip paths.
- `P11_Q5A/P11_Q5B` in `filters.sav` provide partial district evidence only; they are not full-coverage geography and are not a substitute for GPS or a verified 2005 boundary crosswalk.
- No verified ALB_2005 household interview timing exists, so climate exposure windows remain blocked.

## Machine-Readable Outputs

- `temp/alb2005_required_value_key_audit.csv`
- `result/alb2005_required_value_key_summary.csv`
""",
        encoding="utf-8",
    )


def main() -> None:
    ensure_dirs()
    rows = build_rows()
    summary = build_summary(rows)
    write_csv(AUDIT_PATH, rows, AUDIT_COLUMNS)
    write_csv(SUMMARY_PATH, summary, SUMMARY_COLUMNS)
    write_report(rows, summary)
    append_log(TEMP_DIR / "audit_log.md", f"Built ALB_2005 required value/key audit with decision {DECISION}.")
    print(f"ALB_2005 required value/key audit rows={len(rows)} decision={DECISION}.")


if __name__ == "__main__":
    main()
