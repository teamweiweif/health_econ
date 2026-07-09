from __future__ import annotations

import csv
import math
import warnings
from pathlib import Path
from typing import Any

import pandas as pd

from common import REPORT_DIR, RESULT_DIR, TEMP_DIR, append_log, ensure_dirs, write_csv

try:
    import pyreadstat
except ImportError:  # pragma: no cover - environment audit covers this.
    pyreadstat = None


IDNO = "ALB_2002_LSMS_v01_M"
COUNTRY = "Albania"
SURVEY_NAME = "Living Standards Measurement Survey 2002"
WAVE = "2002"

RAW_ROOT = TEMP_DIR / "raw_extracted" / "lsms2002en_4dbf0b087520" / "lsms2002en" / "Data_2002"
HEALTH_A_PATH = RAW_ROOT / "Modul_5A_Health.sav"
HEALTH_B_PATH = RAW_ROOT / "Modul_5B_Health.sav"
CORE_PATH = TEMP_DIR / "alb2002_household_core_candidate.csv"

HEALTH_QUESTIONNAIRE_SUMMARY_PATH = RESULT_DIR / "alb2002_health_questionnaire_semantics_summary.csv"
SKIP_MISSING_SUMMARY_PATH = RESULT_DIR / "alb2002_skip_missing_semantics_summary.csv"
MINIMUM_RECIPE_SUMMARY_PATH = RESULT_DIR / "alb2002_minimum_recipe_promotion_summary.csv"
DISTRICT_CROSSWALK_SUMMARY_PATH = RESULT_DIR / "alb2002_district_climate_crosswalk_summary.csv"

AUDIT_PATH = TEMP_DIR / "alb2002_access_need_denominator_policy_audit.csv"
SUMMARY_PATH = RESULT_DIR / "alb2002_access_need_denominator_policy_summary.csv"
REPORT_PATH = REPORT_DIR / "alb2002_access_need_denominator_policy_audit.md"

DECISION = "blocked_alb2002_access_need_denominator_policy_not_outcome_ready"
NO_PROMOTION = "not_promoted_access_need_denominator_policy_audit_only"

HEALTH_A_VARIABLES = ["psu", "hh", "hhid", "m5a_q01", "m5a_q07"]
HEALTH_B_VARIABLES = [
    "psu",
    "hh",
    "hhid",
    "m5b_q01",
    "m5b_q02_",
    "m5b_q021",
    "m5b_q022",
    "m5b_q023",
    "m5b_q024",
    "m5b_q03",
    "m5b_q04",
    "m5b_q05",
    "m5b_q06",
    "m5b_q07",
    "m5b_q08",
    "m5b_q09",
    "m5b_q10",
]

AUDIT_COLUMNS = [
    "country",
    "survey_name",
    "wave",
    "idno",
    "policy_name",
    "outcome_family",
    "source_scope",
    "denominator_definition",
    "numerator_definition",
    "source_variables",
    "value_code_evidence",
    "household_rows",
    "denominator_rows",
    "event_rows",
    "event_rate",
    "weighted_denominator",
    "weighted_event_rate",
    "missing_required_rows",
    "low_event_rate_flag",
    "denominator_status",
    "skip_path_status",
    "value_label_status",
    "ready_for_recipe",
    "ready_for_outcome",
    "sdg382_ready",
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


def compact_join(values: list[Any], limit: int = 20) -> str:
    out: list[str] = []
    seen: set[str] = set()
    for value in values:
        clean = " ".join(str(value).replace("\n", " ").replace("|", "/").split())
        if not clean or clean in seen:
            continue
        out.append(clean)
        seen.add(clean)
        if len(out) >= limit:
            break
    return "; ".join(out)


def add_key(df: pd.DataFrame, psu: str = "psu", hh: str = "hh") -> pd.DataFrame:
    out = df.copy()
    out["psu_key"] = out[psu].map(key_part)
    out["hh_key"] = out[hh].map(key_part)
    out["psu_hh_key"] = out["psu_key"] + "-" + out["hh_key"]
    out.loc[(out["psu_key"] == "") | (out["hh_key"] == ""), "psu_hh_key"] = ""
    return out


def read_sav(path: Path, usecols: list[str]) -> tuple[pd.DataFrame, Any]:
    if pyreadstat is None:
        raise RuntimeError("pyreadstat is not available")
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        return pyreadstat.read_sav(str(path), usecols=usecols, apply_value_formats=False)


def metadata_evidence(meta: Any, variables: list[str]) -> str:
    labels = {name: label or "" for name, label in zip(meta.column_names, meta.column_labels)}
    pieces: list[str] = []
    for variable in variables:
        label = labels.get(variable, "")
        value_map = (meta.variable_value_labels or {}).get(variable, {})
        value_bits = [f"{fmt(code)}={label}" for code, label in list(value_map.items())[:8]]
        pieces.append(f"{variable}: {label}" + (f" [{'; '.join(value_bits)}]" if value_bits else ""))
    return compact_join(pieces, 20)


def num(df: pd.DataFrame, column: str) -> pd.Series:
    if column not in df.columns:
        return pd.Series(float("nan"), index=df.index)
    return pd.to_numeric(df[column], errors="coerce")


def weighted_rate(event: pd.Series, denominator: pd.Series, weight: pd.Series) -> tuple[str, str]:
    valid = denominator.fillna(False).astype(bool) & weight.notna() & (weight > 0)
    denom_weight = float(weight.loc[valid].sum()) if valid.any() else 0.0
    event_weight = float(weight.loc[valid & event.fillna(False).astype(bool)].sum()) if valid.any() else 0.0
    if denom_weight <= 0:
        return "", ""
    return fmt(denom_weight), fmt(event_weight / denom_weight)


def audit_row(
    df: pd.DataFrame,
    policy_name: str,
    outcome_family: str,
    source_scope: str,
    denominator: pd.Series,
    event: pd.Series,
    denominator_definition: str,
    numerator_definition: str,
    source_variables: list[str],
    value_code_evidence: str,
    denominator_status: str,
    skip_path_status: str,
    value_label_status: str = "value_labels_seen_manual_policy_required",
) -> dict[str, str]:
    denominator_bool = denominator.fillna(False).astype(bool)
    event_bool = event.fillna(False).astype(bool) & denominator_bool
    denom_rows = int(denominator_bool.sum())
    event_rows = int(event_bool.sum())
    event_rate = event_rows / denom_rows if denom_rows else float("nan")
    weight = num(df, "household_weight")
    weighted_denominator, weighted_event_rate = weighted_rate(event_bool, denominator_bool, weight)
    return {
        "country": COUNTRY,
        "survey_name": SURVEY_NAME,
        "wave": WAVE,
        "idno": IDNO,
        "policy_name": policy_name,
        "outcome_family": outcome_family,
        "source_scope": source_scope,
        "denominator_definition": denominator_definition,
        "numerator_definition": numerator_definition,
        "source_variables": ";".join(source_variables),
        "value_code_evidence": value_code_evidence,
        "household_rows": str(len(df)),
        "denominator_rows": str(denom_rows),
        "event_rows": str(event_rows),
        "event_rate": fmt(event_rate),
        "weighted_denominator": weighted_denominator,
        "weighted_event_rate": weighted_event_rate,
        "missing_required_rows": str(max(len(df) - denom_rows, 0)),
        "low_event_rate_flag": "1" if denom_rows > 0 and event_rate < 0.03 else "0",
        "denominator_status": denominator_status,
        "skip_path_status": skip_path_status,
        "value_label_status": value_label_status,
        "ready_for_recipe": "0",
        "ready_for_outcome": "0",
        "sdg382_ready": "0",
        "climate_linkage_ready": "0",
        "promotion_status": NO_PROMOTION,
        "blocking_reason": (
            "Access/need denominator policy audit only. Final promotion still requires a selected denominator, "
            "person-to-household aggregation policy, missing-code rules, OOP/financial denominator gates, and climate-ready geography."
        ),
        "next_action": (
            "Choose a documented access outcome family only after the denominator, trigger, reason-code, and missing-code "
            "rules are accepted alongside financial-protection and geography gates."
        ),
    }


def build_base() -> tuple[pd.DataFrame, str, str]:
    if not CORE_PATH.exists():
        raise FileNotFoundError(f"Missing prerequisite: {CORE_PATH}")
    core = add_key(pd.read_csv(CORE_PATH, encoding="utf-8-sig"))
    health_a, meta_a = read_sav(HEALTH_A_PATH, HEALTH_A_VARIABLES)
    health_b, meta_b = read_sav(HEALTH_B_PATH, HEALTH_B_VARIABLES)
    health_a = add_key(health_a)
    health_b = add_key(health_b)

    health_a["person_chronic_or_disability"] = num(health_a, "m5a_q01") == 1
    health_a["person_sudden_illness_4w"] = num(health_a, "m5a_q07") == 1
    person_agg = (
        health_a.groupby("psu_hh_key", dropna=False)
        .agg(
            person_health_rows=("hhid", "size"),
            household_any_chronic_or_disability=("person_chronic_or_disability", "max"),
            household_any_sudden_illness_4w=("person_sudden_illness_4w", "max"),
        )
        .reset_index()
    )
    merged = core.merge(person_agg, on="psu_hh_key", how="left").merge(
        health_b.drop(columns=["psu", "hh", "hhid", "psu_key", "hh_key"], errors="ignore"),
        on="psu_hh_key",
        how="left",
    )
    for column in ["person_health_rows", "household_any_chronic_or_disability", "household_any_sudden_illness_4w"]:
        merged[column] = pd.to_numeric(merged[column], errors="coerce").fillna(0)
    merged["household_any_person_need"] = (
        (merged["household_any_chronic_or_disability"] > 0) | (merged["household_any_sudden_illness_4w"] > 0)
    )
    return merged, metadata_evidence(meta_a, ["m5a_q01", "m5a_q07"]), metadata_evidence(meta_b, HEALTH_B_VARIABLES[3:])


def build_rows() -> list[dict[str, str]]:
    df, health_a_evidence, health_b_evidence = build_base()
    rows: list[dict[str, str]] = []
    q01 = num(df, "m5b_q01")
    q03 = num(df, "m5b_q03")
    q04 = num(df, "m5b_q04")
    q05 = num(df, "m5b_q05")
    q06 = num(df, "m5b_q06")
    q07 = num(df, "m5b_q07")
    q08 = num(df, "m5b_q08")
    q09 = num(df, "m5b_q09")
    q10 = num(df, "m5b_q10")
    q02_any = (num(df, "m5b_q02_").fillna(0) == 1) | (num(df, "m5b_q021").fillna(0) == 1) | (num(df, "m5b_q022").fillna(0) == 1) | (num(df, "m5b_q023").fillna(0) == 1) | (num(df, "m5b_q024").fillna(0) == 1)

    q01_need = q01.isin([1, 2, 3])
    q01_difficult = q01.isin([1, 2])
    delayed = q03 > 1
    referral_not_gone = q05 > 1
    refused = q07 == 1
    medicine_entitled = q09 == 1

    policies = [
        (
            "person_any_chronic_or_sudden_need",
            "need_denominator",
            "person_to_household_health_a",
            df["person_health_rows"] > 0,
            df["household_any_person_need"],
            "Household has at least one Health A person row.",
            "Any household member has chronic/disability status yes or sudden illness in past four weeks.",
            ["m5a_q01", "m5a_q07"],
            health_a_evidence,
            "person_level_need_proxy_household_aggregation_required",
            "person_module_not_a_direct_forgone_care_denominator",
        ),
        (
            "q01_family_healthcare_need_denominator",
            "need_denominator",
            "household_health_b",
            q01.notna(),
            q01_need,
            "m5b_q01 is nonmissing.",
            "m5b_q01 is 1, 2, or 3, excluding no-one-needed-health-care code 4.",
            ["m5b_q01"],
            health_b_evidence,
            "household_need_denominator_candidate_no_one_needed_care_code_seen",
            "questionnaire_skip_to_access_items_requires_policy_review",
        ),
        (
            "q01_cost_affordability_difficulty_among_need",
            "cost_barrier",
            "household_health_b",
            q01_need,
            q01_difficult,
            "m5b_q01 indicates somebody needed health care.",
            "m5b_q01 is very difficult or difficult.",
            ["m5b_q01"],
            health_b_evidence,
            "cost_affordability_denominator_candidate",
            "broad_affordability_question_not_forgone_care_by_itself",
        ),
        (
            "money_raising_any_among_q01_difficult",
            "coping_barrier",
            "household_health_b",
            q01_difficult,
            q02_any,
            "m5b_q01 is very difficult or difficult.",
            "Any m5b_q02 method indicator equals 1.",
            ["m5b_q01", "m5b_q02_", "m5b_q021", "m5b_q022", "m5b_q023", "m5b_q024"],
            health_b_evidence,
            "coping_denominator_candidate",
            "multi_response_method_semantics_require_manual_review",
        ),
        (
            "delayed_help_any_among_q01_need",
            "forgone_or_delayed_care",
            "household_health_b",
            q03.notna(),
            delayed,
            "m5b_q03 is nonmissing.",
            "m5b_q03 is once, twice, three times, or four times or more.",
            ["m5b_q03"],
            health_b_evidence,
            "delayed_care_denominator_candidate",
            "count_coding_and_need_scope_require_manual_review",
        ),
        (
            "delay_reason_cost_conditional",
            "cost_barrier",
            "household_health_b",
            delayed & q04.notna(),
            q04 == 4,
            "m5b_q03 indicates delayed/not sought help and m5b_q04 is nonmissing.",
            "m5b_q04 is could not afford to pay.",
            ["m5b_q03", "m5b_q04"],
            health_b_evidence,
            "conditional_reason_denominator_candidate",
            "conditional_reason_denominator_requires_trigger_policy",
        ),
        (
            "delay_reason_distance_conditional",
            "distance_barrier",
            "household_health_b",
            delayed & q04.notna(),
            q04 == 5,
            "m5b_q03 indicates delayed/not sought help and m5b_q04 is nonmissing.",
            "m5b_q04 is too far.",
            ["m5b_q03", "m5b_q04"],
            health_b_evidence,
            "conditional_reason_denominator_candidate",
            "conditional_reason_denominator_requires_trigger_policy",
        ),
        (
            "hospital_referral_not_gone_any",
            "forgone_or_delayed_care",
            "household_health_b",
            q05.notna(),
            referral_not_gone,
            "m5b_q05 is nonmissing.",
            "m5b_q05 is once, twice, three times, or four times or more.",
            ["m5b_q05"],
            health_b_evidence,
            "referral_nonuse_denominator_candidate",
            "referral_need_scope_requires_manual_review",
        ),
        (
            "referral_reason_cost_conditional",
            "cost_barrier",
            "household_health_b",
            referral_not_gone & q06.notna(),
            q06 == 2,
            "m5b_q05 indicates referral not gone and m5b_q06 is nonmissing.",
            "m5b_q06 is unable to afford treatment.",
            ["m5b_q05", "m5b_q06"],
            health_b_evidence,
            "conditional_referral_reason_denominator_candidate",
            "conditional_reason_denominator_requires_trigger_policy",
        ),
        (
            "referral_reason_distance_conditional",
            "distance_barrier",
            "household_health_b",
            referral_not_gone & q06.notna(),
            q06.isin([3, 6]),
            "m5b_q05 indicates referral not gone and m5b_q06 is nonmissing.",
            "m5b_q06 is unable to get to services or too far.",
            ["m5b_q05", "m5b_q06"],
            health_b_evidence,
            "conditional_referral_reason_denominator_candidate",
            "conditional_reason_denominator_requires_trigger_policy",
        ),
        (
            "referral_reason_other_service_trust_conditional",
            "supply_or_acceptability_barrier",
            "household_health_b",
            referral_not_gone & q06.notna(),
            q06.isin([4, 5, 7]),
            "m5b_q05 indicates referral not gone and m5b_q06 is nonmissing.",
            "m5b_q06 is referred elsewhere, distrust, or other.",
            ["m5b_q05", "m5b_q06"],
            health_b_evidence,
            "conditional_referral_reason_denominator_candidate",
            "category_scope_requires_manual_supply_acceptability_policy",
        ),
        (
            "refused_health_services_any",
            "forgone_or_delayed_care",
            "household_health_b",
            q07.notna(),
            refused,
            "m5b_q07 is nonmissing.",
            "m5b_q07 is yes.",
            ["m5b_q07"],
            health_b_evidence,
            "refusal_denominator_candidate",
            "ever_refusal_scope_requires_period_policy",
        ),
        (
            "refused_reason_cost_conditional",
            "cost_barrier",
            "household_health_b",
            refused & q08.notna(),
            q08 == 1,
            "m5b_q07 indicates refused health services and m5b_q08 is nonmissing.",
            "m5b_q08 is could not afford to pay.",
            ["m5b_q07", "m5b_q08"],
            health_b_evidence,
            "conditional_refusal_reason_denominator_candidate",
            "conditional_reason_denominator_requires_trigger_policy",
        ),
        (
            "refused_reason_distance_conditional",
            "distance_barrier",
            "household_health_b",
            refused & q08.notna(),
            q08 == 2,
            "m5b_q07 indicates refused health services and m5b_q08 is nonmissing.",
            "m5b_q08 is unable to get to where services were available.",
            ["m5b_q07", "m5b_q08"],
            health_b_evidence,
            "conditional_refusal_reason_denominator_candidate",
            "conditional_reason_denominator_requires_trigger_policy",
        ),
        (
            "refused_reason_supply_admin_conditional",
            "supply_or_admin_barrier",
            "household_health_b",
            refused & q08.notna(),
            q08.isin([3, 4]),
            "m5b_q07 indicates refused health services and m5b_q08 is nonmissing.",
            "m5b_q08 is resident-region restriction or referral barrier.",
            ["m5b_q07", "m5b_q08"],
            health_b_evidence,
            "conditional_refusal_reason_denominator_candidate",
            "category_scope_requires_manual_supply_admin_policy",
        ),
        (
            "medicine_discount_entitlement",
            "coverage_denominator",
            "household_health_b",
            q09.notna(),
            medicine_entitled,
            "m5b_q09 is nonmissing.",
            "m5b_q09 is yes.",
            ["m5b_q09"],
            health_b_evidence,
            "coverage_denominator_candidate_not_failure_outcome",
            "entitlement_scope_not_a_direct_access_failure",
        ),
        (
            "medicine_discount_any_barrier",
            "medicine_access_barrier",
            "household_health_b",
            medicine_entitled & q10.notna(),
            q10 != 1,
            "m5b_q09 is yes and m5b_q10 is nonmissing.",
            "m5b_q10 is any no/other category rather than always able.",
            ["m5b_q09", "m5b_q10"],
            health_b_evidence,
            "medicine_access_denominator_candidate",
            "discount_entitlement_and_need_scope_require_manual_review",
        ),
        (
            "medicine_discount_cost_barrier",
            "cost_barrier",
            "household_health_b",
            medicine_entitled & q10.notna(),
            q10 == 5,
            "m5b_q09 is yes and m5b_q10 is nonmissing.",
            "m5b_q10 is even with discount difficult to afford.",
            ["m5b_q09", "m5b_q10"],
            health_b_evidence,
            "medicine_cost_denominator_candidate",
            "discount_entitlement_and_need_scope_require_manual_review",
        ),
        (
            "medicine_discount_supply_admin_barrier",
            "supply_or_admin_barrier",
            "household_health_b",
            medicine_entitled & q10.notna(),
            q10.isin([2, 3, 4]),
            "m5b_q09 is yes and m5b_q10 is nonmissing.",
            "m5b_q10 is document, shortage, or doctor prescribing barrier.",
            ["m5b_q09", "m5b_q10"],
            health_b_evidence,
            "medicine_supply_admin_denominator_candidate",
            "discount_entitlement_and_need_scope_require_manual_review",
        ),
    ]

    delay_cost = q04 == 4
    delay_distance = q04 == 5
    referral_cost = q06 == 2
    referral_distance = q06.isin([3, 6])
    referral_supply = q06.isin([4, 5, 7])
    refused_cost = q08 == 1
    refused_distance = q08 == 2
    refused_supply_admin = q08.isin([3, 4])
    medicine_cost = q10 == 5
    medicine_supply_admin = q10.isin([2, 3, 4])
    composite_denominator = q01.notna() | q03.notna() | q05.notna() | q07.notna() | q09.notna()
    cost_barrier = q01_difficult | delay_cost | referral_cost | refused_cost | medicine_cost
    distance_barrier = delay_distance | referral_distance | refused_distance
    supply_admin_barrier = referral_supply | refused_supply_admin | medicine_supply_admin
    delayed_refused_nonuse = delayed | referral_not_gone | refused
    any_access_barrier = cost_barrier | distance_barrier | supply_admin_barrier | delayed_refused_nonuse
    policies.extend(
        [
            (
                "composite_cost_barrier_candidate",
                "cost_barrier",
                "household_health_b_composite",
                composite_denominator,
                cost_barrier,
                "Any Health B access/cost trigger is nonmissing.",
                "Any affordability, delayed-care cost, referral cost, refusal cost, or medicine-discount cost barrier is observed.",
                ["m5b_q01", "m5b_q04", "m5b_q06", "m5b_q08", "m5b_q10"],
                health_b_evidence,
                "composite_cost_denominator_candidate",
                "composite_union_mixes_broad_affordability_and_conditional_reason_denominators",
            ),
            (
                "composite_distance_barrier_candidate",
                "distance_barrier",
                "household_health_b_composite",
                composite_denominator,
                distance_barrier,
                "Any Health B access/distance trigger is nonmissing.",
                "Any delayed-care, referral, or refusal distance barrier is observed.",
                ["m5b_q04", "m5b_q06", "m5b_q08"],
                health_b_evidence,
                "composite_distance_denominator_candidate",
                "composite_union_mixes_conditional_reason_denominators",
            ),
            (
                "composite_supply_admin_barrier_candidate",
                "supply_or_admin_barrier",
                "household_health_b_composite",
                composite_denominator,
                supply_admin_barrier,
                "Any Health B supply/admin trigger is nonmissing.",
                "Any referral, refusal, or medicine discount supply/admin barrier is observed.",
                ["m5b_q06", "m5b_q08", "m5b_q10"],
                health_b_evidence,
                "composite_supply_admin_denominator_candidate",
                "composite_union_mixes_conditional_reason_denominators",
            ),
            (
                "composite_delayed_refused_nonuse_candidate",
                "forgone_or_delayed_care",
                "household_health_b_composite",
                composite_denominator,
                delayed_refused_nonuse,
                "Any Health B access trigger is nonmissing.",
                "Delayed care, hospital referral not gone, or refused health services is observed.",
                ["m5b_q03", "m5b_q05", "m5b_q07"],
                health_b_evidence,
                "composite_nonuse_denominator_candidate",
                "composite_union_mixes_delay_referral_and_ever_refusal_scopes",
            ),
            (
                "composite_any_access_barrier_candidate",
                "access_failure_composite",
                "household_health_b_composite",
                composite_denominator,
                any_access_barrier,
                "Any Health B access trigger is nonmissing.",
                "Any cost, distance, supply/admin, delayed-care, referral nonuse, or refusal signal is observed.",
                ["m5b_q01", "m5b_q03", "m5b_q04", "m5b_q05", "m5b_q06", "m5b_q07", "m5b_q08", "m5b_q10"],
                health_b_evidence,
                "composite_access_denominator_candidate",
                "composite_union_too_broad_for_final_outcome_without_policy_review",
            ),
        ]
    )

    for policy in policies:
        rows.append(audit_row(df, *policy))
    return rows


def int_sum(rows: list[dict[str, str]], field: str, outcome_family: str | None = None) -> int:
    selected = rows if outcome_family is None else [row for row in rows if row["outcome_family"] == outcome_family]
    total = 0
    for row in selected:
        try:
            total += int(float(row.get(field, "0") or 0))
        except ValueError:
            pass
    return total


def summary_row(metric: str, value: Any, interpretation: str) -> dict[str, str]:
    return {"metric": metric, "value": fmt(value), "interpretation": interpretation}


def build_summary(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    questionnaire_summary = read_csv_dicts(HEALTH_QUESTIONNAIRE_SUMMARY_PATH)
    skip_summary = read_csv_dicts(SKIP_MISSING_SUMMARY_PATH)
    minimum_recipe_summary = read_csv_dicts(MINIMUM_RECIPE_SUMMARY_PATH)
    crosswalk_summary = read_csv_dicts(DISTRICT_CROSSWALK_SUMMARY_PATH)
    row_by_name = {row["policy_name"]: row for row in rows}

    def event_rows(name: str) -> str:
        return row_by_name.get(name, {}).get("event_rows", "0")

    def denominator_rows(name: str) -> str:
        return row_by_name.get(name, {}).get("denominator_rows", "0")

    return [
        summary_row("alb2002_access_need_denominator_policy_rows", len(rows), "Rows in the ALB_2002 access/need denominator policy audit."),
        summary_row("alb2002_access_need_household_rows", row_by_name.get("q01_family_healthcare_need_denominator", {}).get("household_rows", "0"), "Base household rows included in the access/need audit."),
        summary_row("alb2002_access_need_person_need_household_rows", event_rows("person_any_chronic_or_sudden_need"), "Households with any Health A chronic/disability or sudden-illness need proxy."),
        summary_row("alb2002_access_need_q01_need_rows", event_rows("q01_family_healthcare_need_denominator"), "Households not coded as no-one-needed-health-care in m5b_q01."),
        summary_row("alb2002_access_need_q01_cost_difficulty_rows", event_rows("q01_cost_affordability_difficulty_among_need"), "Households reporting very difficult or difficult payment situation among q01 need-coded households."),
        summary_row("alb2002_access_need_delayed_help_rows", event_rows("delayed_help_any_among_q01_need"), "Households with delayed/not-sought help count above none."),
        summary_row("alb2002_access_need_referral_not_gone_rows", event_rows("hospital_referral_not_gone_any"), "Households with hospital referral not gone count above none."),
        summary_row("alb2002_access_need_refused_service_rows", event_rows("refused_health_services_any"), "Households with any health-service refusal."),
        summary_row("alb2002_access_need_medicine_discount_any_barrier_rows", event_rows("medicine_discount_any_barrier"), "Households entitled to medicine discount but not always able to exercise it."),
        summary_row("alb2002_access_need_composite_cost_barrier_rows", event_rows("composite_cost_barrier_candidate"), "Composite cost-barrier candidate event rows."),
        summary_row("alb2002_access_need_composite_distance_barrier_rows", event_rows("composite_distance_barrier_candidate"), "Composite distance-barrier candidate event rows."),
        summary_row("alb2002_access_need_composite_supply_admin_barrier_rows", event_rows("composite_supply_admin_barrier_candidate"), "Composite supply/admin-barrier candidate event rows."),
        summary_row("alb2002_access_need_composite_any_access_barrier_rows", event_rows("composite_any_access_barrier_candidate"), "Composite any-access-barrier candidate event rows."),
        summary_row("alb2002_access_need_composite_any_access_barrier_denominator_rows", denominator_rows("composite_any_access_barrier_candidate"), "Composite any-access-barrier candidate denominator rows."),
        summary_row("alb2002_access_need_low_event_rate_rows", sum(1 for row in rows if row["low_event_rate_flag"] == "1"), "Candidate policies with unweighted event rate below 3 percent."),
        summary_row("alb2002_access_need_questionnaire_access_rows_observed", metric_value(questionnaire_summary, "alb2002_health_questionnaire_access_rows"), "Access rows observed upstream in the questionnaire audit."),
        summary_row("alb2002_access_need_skip_missing_rows_observed", metric_value(skip_summary, "alb2002_skip_missing_semantics_rows"), "Skip/missing audit rows observed upstream."),
        summary_row("alb2002_access_need_minimum_recipe_outcome_ready_observed", metric_value(minimum_recipe_summary, "alb2002_minimum_recipe_promotion_outcome_ready_rows"), "Outcome-ready rows observed upstream in the minimum recipe packet."),
        summary_row("alb2002_access_need_climate_ready_rows_observed", metric_value(crosswalk_summary, "alb2002_climate_linkage_ready_rows"), "Climate-linkage-ready rows observed upstream."),
        summary_row("alb2002_access_need_recipe_ready_rows", 0, "Rows promoted to harmonization recipe by this audit; intentionally zero."),
        summary_row("alb2002_access_need_outcome_ready_rows", 0, "Rows promoted to final outcome construction by this audit; intentionally zero."),
        summary_row("alb2002_access_need_sdg382_ready_rows", 0, "Rows promoted to SDG 3.8.2 construction by this audit; intentionally zero."),
        summary_row("alb2002_access_need_climate_linkage_ready_rows", 0, "Rows promoted to climate linkage by this audit; intentionally zero."),
        summary_row("alb2002_access_need_current_decision", DECISION, "Current fail-closed decision for ALB_2002 access/need denominator policies."),
    ]


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
    report = f"""# ALB_2002 Access and Need Denominator Policy Audit

Status: fail-closed denominator-policy audit. This report reads ALB_2002 raw Health A and Health B files and compares candidate need, forgone-care, cost, distance, supply/admin, medicine-access, coping, and composite access-denominator policies. It does not write `data/`, does not construct final access outcomes, and does not promote any row to harmonization, SDG 3.8.2, outcome construction, or climate linkage.

## Bottom Line

- ALB_2002 has usable raw access and need signals, including no-one-needed-care coding, delayed/not-sought care, referral nonuse, service refusal, medicine-discount barriers, and person-level illness proxies.
- The denominator options differ materially: broad family health-care need, delayed-care triggers, referral triggers, refusal triggers, medicine entitlement, and person-level illness proxies are not interchangeable.
- Cost, distance, and supply/admin barriers can be stress-tested, but final access outcomes require an explicit denominator and trigger policy.
- Recipe-ready, outcome-ready, SDG 3.8.2-ready, and climate-linkage-ready rows from this audit: 0.
- Current decision: `{DECISION}`.

## Summary

| Metric | Value | Interpretation |
|---|---:|---|
{summary_table}

## Candidate Denominator Policies

{markdown_rows(rows, ['policy_name', 'outcome_family', 'denominator_rows', 'event_rows', 'event_rate', 'weighted_event_rate', 'low_event_rate_flag', 'denominator_status', 'skip_path_status'], 35)}

## Interpretation

- `m5b_q01` is the clearest broad household denominator candidate because it separates households where no one needed health care from households reporting the difficulty of paying for care.
- Conditional reason variables such as `m5b_q04`, `m5b_q06`, and `m5b_q08` must remain tied to their trigger variables; using them over all households would inflate denominators and understate event rates.
- Medicine-discount access is policy-relevant but conditional on entitlement and should not be treated as a general forgone-care denominator without a separate scope decision.
- The composite candidates are screening diagnostics only; they mix broad affordability, delayed care, referral, refusal, and medicine-entitlement scopes.
- Climate linkage remains separately blocked by the unresolved district-boundary/GPS evidence.

## Machine-Readable Outputs

- `temp/alb2002_access_need_denominator_policy_audit.csv`
- `result/alb2002_access_need_denominator_policy_summary.csv`
"""
    REPORT_PATH.write_text(report, encoding="utf-8")


def main() -> None:
    ensure_dirs()
    rows = build_rows()
    summary = build_summary(rows)
    write_csv(AUDIT_PATH, rows, AUDIT_COLUMNS)
    write_csv(SUMMARY_PATH, summary, SUMMARY_COLUMNS)
    write_report(rows, summary)
    append_log(TEMP_DIR / "audit_log.md", f"Built ALB_2002 access/need denominator policy audit rows={len(rows)} decision={DECISION}.")
    print(f"ALB_2002 access/need denominator policy rows={len(rows)} decision={DECISION}.")


if __name__ == "__main__":
    main()
