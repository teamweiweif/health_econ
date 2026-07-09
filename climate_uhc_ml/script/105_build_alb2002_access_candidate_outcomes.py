from __future__ import annotations

import csv
import math
import warnings
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

ACCESS_POLICY_SUMMARY_PATH = RESULT_DIR / "alb2002_access_need_denominator_policy_summary.csv"

HOUSEHOLD_OUTCOME_PATH = TEMP_DIR / "alb2002_access_candidate_household_outcomes.csv"
LINEAGE_PATH = TEMP_DIR / "alb2002_access_candidate_outcome_lineage.csv"
AUDIT_PATH = RESULT_DIR / "alb2002_access_candidate_outcome_audit.csv"
SUMMARY_PATH = RESULT_DIR / "alb2002_access_candidate_outcome_summary.csv"
REPORT_PATH = REPORT_DIR / "alb2002_access_candidate_outcome_audit.md"

DECISION = "blocked_alb2002_access_candidate_not_promoted_due_denominator_skip_climate_gates"
PROMOTION_STATUS = "temp_only_access_candidate_outcomes_not_promoted"

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

HOUSEHOLD_COLUMNS = [
    "country",
    "survey_name",
    "wave",
    "idno",
    "hhid",
    "survey_year",
    "survey_month",
    "interview_date",
    "psu",
    "stratum",
    "district_code",
    "district_name",
    "household_weight",
    "person_health_rows",
    "person_need_proxy_candidate",
    "q01_family_healthcare_need_candidate",
    "q01_cost_difficulty_candidate",
    "money_raising_any_candidate",
    "delayed_help_any_candidate",
    "delay_reason_cost_candidate",
    "delay_reason_distance_candidate",
    "hospital_referral_not_gone_candidate",
    "referral_reason_cost_candidate",
    "referral_reason_distance_candidate",
    "referral_reason_supply_acceptability_candidate",
    "refused_health_services_candidate",
    "refused_reason_cost_candidate",
    "refused_reason_distance_candidate",
    "refused_reason_supply_admin_candidate",
    "medicine_discount_entitlement_candidate",
    "medicine_discount_any_barrier_candidate",
    "medicine_discount_cost_barrier_candidate",
    "medicine_discount_supply_admin_barrier_candidate",
    "composite_cost_barrier_candidate",
    "composite_distance_barrier_candidate",
    "composite_supply_admin_barrier_candidate",
    "composite_delayed_refused_nonuse_candidate",
    "composite_any_access_barrier_candidate",
    "broad_access_denominator_valid",
    "candidate_policy_name",
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
    "outcome_id",
    "outcome_label",
    "outcome_family",
    "denominator_definition",
    "numerator_definition",
    "source_fields",
    "household_rows",
    "denominator_rows",
    "missing_rows",
    "event_rows",
    "event_rate",
    "weighted_event_rate",
    "low_event_rate_flag",
    "ready_for_outcome",
    "ready_for_recipe",
    "sdg382_ready",
    "climate_linkage_ready",
    "promotion_status",
    "blocking_reason",
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


def add_key(df: pd.DataFrame, psu: str = "psu", hh: str = "hh") -> pd.DataFrame:
    out = df.copy()
    out["psu_key"] = out[psu].map(key_part)
    out["hh_key"] = out[hh].map(key_part)
    out["psu_hh_key"] = out["psu_key"] + "-" + out["hh_key"]
    out.loc[(out["psu_key"] == "") | (out["hh_key"] == ""), "psu_hh_key"] = ""
    return out


def num(df: pd.DataFrame, column: str) -> pd.Series:
    if column not in df.columns:
        return pd.Series(float("nan"), index=df.index)
    return pd.to_numeric(df[column], errors="coerce")


def read_sav(path, usecols: list[str]) -> pd.DataFrame:
    if pyreadstat is None:
        raise RuntimeError("pyreadstat is not available")
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        df, _meta = pyreadstat.read_sav(str(path), usecols=usecols, apply_value_formats=False)
    return df


def blocking_reason() -> str:
    return (
        "Household-level access candidate outcomes are built from raw ALB_2002 Health A/B variables, "
        "but they remain temp-only because final access outcomes require a selected denominator, trigger-specific "
        "skip/missing policy, low-event handling, financial-outcome alignment, and climate-ready geography."
    )


def build_base() -> pd.DataFrame:
    if not CORE_PATH.exists():
        raise FileNotFoundError(f"Missing prerequisite: {CORE_PATH}")
    core = add_key(pd.read_csv(CORE_PATH, encoding="utf-8-sig"))
    health_a = add_key(read_sav(HEALTH_A_PATH, HEALTH_A_VARIABLES))
    health_b = add_key(read_sav(HEALTH_B_PATH, HEALTH_B_VARIABLES))

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
    return core.merge(person_agg, on="psu_hh_key", how="left").merge(
        health_b.drop(columns=["psu", "hh", "hhid", "psu_key", "hh_key"], errors="ignore"),
        on="psu_hh_key",
        how="left",
    )


def build_household_outcomes() -> pd.DataFrame:
    df = build_base()
    for column in ["person_health_rows", "household_any_chronic_or_disability", "household_any_sudden_illness_4w"]:
        df[column] = pd.to_numeric(df[column], errors="coerce").fillna(0)

    q01 = num(df, "m5b_q01")
    q03 = num(df, "m5b_q03")
    q04 = num(df, "m5b_q04")
    q05 = num(df, "m5b_q05")
    q06 = num(df, "m5b_q06")
    q07 = num(df, "m5b_q07")
    q08 = num(df, "m5b_q08")
    q09 = num(df, "m5b_q09")
    q10 = num(df, "m5b_q10")

    person_need = (df["household_any_chronic_or_disability"] > 0) | (df["household_any_sudden_illness_4w"] > 0)
    q01_need = q01.isin([1, 2, 3])
    q01_difficult = q01.isin([1, 2])
    q02_any = (
        (num(df, "m5b_q02_").fillna(0) == 1)
        | (num(df, "m5b_q021").fillna(0) == 1)
        | (num(df, "m5b_q022").fillna(0) == 1)
        | (num(df, "m5b_q023").fillna(0) == 1)
        | (num(df, "m5b_q024").fillna(0) == 1)
    )
    delayed = q03 > 1
    referral_not_gone = q05 > 1
    refused = q07 == 1
    medicine_entitled = q09 == 1

    delay_cost = delayed & (q04 == 4)
    delay_distance = delayed & (q04 == 5)
    referral_cost = referral_not_gone & (q06 == 2)
    referral_distance = referral_not_gone & q06.isin([3, 6])
    referral_supply = referral_not_gone & q06.isin([4, 5, 7])
    refused_cost = refused & (q08 == 1)
    refused_distance = refused & (q08 == 2)
    refused_supply_admin = refused & q08.isin([3, 4])
    medicine_any_barrier = medicine_entitled & q10.notna() & (q10 != 1)
    medicine_cost = medicine_entitled & (q10 == 5)
    medicine_supply_admin = medicine_entitled & q10.isin([2, 3, 4])

    composite_denominator = q01.notna() | q03.notna() | q05.notna() | q07.notna() | q09.notna()
    cost_barrier = q01_difficult | delay_cost | referral_cost | refused_cost | medicine_cost
    distance_barrier = delay_distance | referral_distance | refused_distance
    supply_admin_barrier = referral_supply | refused_supply_admin | medicine_supply_admin
    delayed_refused_nonuse = delayed | referral_not_gone | refused
    any_access_barrier = cost_barrier | distance_barrier | supply_admin_barrier | delayed_refused_nonuse

    return pd.DataFrame(
        {
            "country": df["country"],
            "survey_name": df["survey_name"],
            "wave": df["wave"],
            "idno": df["idno"],
            "hhid": df["hhid"],
            "survey_year": df["survey_year"],
            "survey_month": df["survey_month"],
            "interview_date": df["interview_date"],
            "psu": df["psu"],
            "stratum": df["stratum"],
            "district_code": df["district_code_identification"],
            "district_name": df["district_name_identification"],
            "household_weight": df["household_weight"],
            "person_health_rows": df["person_health_rows"],
            "person_need_proxy_candidate": person_need.astype(int),
            "q01_family_healthcare_need_candidate": q01_need.astype(int),
            "q01_cost_difficulty_candidate": q01_difficult.astype(int),
            "money_raising_any_candidate": q02_any.astype(int),
            "delayed_help_any_candidate": delayed.astype(int),
            "delay_reason_cost_candidate": delay_cost.astype(int),
            "delay_reason_distance_candidate": delay_distance.astype(int),
            "hospital_referral_not_gone_candidate": referral_not_gone.astype(int),
            "referral_reason_cost_candidate": referral_cost.astype(int),
            "referral_reason_distance_candidate": referral_distance.astype(int),
            "referral_reason_supply_acceptability_candidate": referral_supply.astype(int),
            "refused_health_services_candidate": refused.astype(int),
            "refused_reason_cost_candidate": refused_cost.astype(int),
            "refused_reason_distance_candidate": refused_distance.astype(int),
            "refused_reason_supply_admin_candidate": refused_supply_admin.astype(int),
            "medicine_discount_entitlement_candidate": medicine_entitled.astype(int),
            "medicine_discount_any_barrier_candidate": medicine_any_barrier.astype(int),
            "medicine_discount_cost_barrier_candidate": medicine_cost.astype(int),
            "medicine_discount_supply_admin_barrier_candidate": medicine_supply_admin.astype(int),
            "composite_cost_barrier_candidate": cost_barrier.astype(int),
            "composite_distance_barrier_candidate": distance_barrier.astype(int),
            "composite_supply_admin_barrier_candidate": supply_admin_barrier.astype(int),
            "composite_delayed_refused_nonuse_candidate": delayed_refused_nonuse.astype(int),
            "composite_any_access_barrier_candidate": any_access_barrier.astype(int),
            "broad_access_denominator_valid": composite_denominator.astype(int),
            "candidate_policy_name": "raw_health_ab_household_access_candidates",
            "candidate_dataset_status": "temp_only_access_candidate_not_promoted",
            "promotion_status": PROMOTION_STATUS,
            "blocking_reason": blocking_reason(),
        }
    )


def weighted_rate(event: pd.Series, denominator: pd.Series, weight: pd.Series) -> str:
    valid = denominator.fillna(False).astype(bool) & weight.notna() & (weight > 0)
    if not valid.any():
        return ""
    total_weight = float(weight.loc[valid].sum())
    if total_weight <= 0:
        return ""
    event_weight = float(weight.loc[valid & event.fillna(False).astype(bool)].sum())
    return fmt(event_weight / total_weight)


def audit_row(
    household: pd.DataFrame,
    outcome_id: str,
    label: str,
    family: str,
    denominator: pd.Series,
    event: pd.Series,
    denominator_definition: str,
    numerator_definition: str,
    source_fields: str,
    climate_ready: int,
) -> dict[str, str]:
    denominator_bool = denominator.fillna(False).astype(bool)
    event_bool = event.fillna(False).astype(bool) & denominator_bool
    denom_rows = int(denominator_bool.sum())
    event_rows = int(event_bool.sum())
    event_rate = event_rows / denom_rows if denom_rows else float("nan")
    return {
        "outcome_id": outcome_id,
        "outcome_label": label,
        "outcome_family": family,
        "denominator_definition": denominator_definition,
        "numerator_definition": numerator_definition,
        "source_fields": source_fields,
        "household_rows": str(len(household)),
        "denominator_rows": str(denom_rows),
        "missing_rows": str(len(household) - denom_rows),
        "event_rows": str(event_rows),
        "event_rate": fmt(event_rate),
        "weighted_event_rate": weighted_rate(event_bool, denominator_bool, pd.to_numeric(household["household_weight"], errors="coerce")),
        "low_event_rate_flag": str(int(denom_rows > 0 and event_rate < 0.03)),
        "ready_for_outcome": "0",
        "ready_for_recipe": "0",
        "sdg382_ready": "0",
        "climate_linkage_ready": str(climate_ready),
        "promotion_status": PROMOTION_STATUS,
        "blocking_reason": blocking_reason(),
    }


def build_audit(household: pd.DataFrame, climate_ready: int) -> list[dict[str, str]]:
    broad = pd.to_numeric(household["broad_access_denominator_valid"], errors="coerce").fillna(0).astype(bool)
    q01_need = pd.to_numeric(household["q01_family_healthcare_need_candidate"], errors="coerce").fillna(0).astype(bool)
    med_entitled = pd.to_numeric(household["medicine_discount_entitlement_candidate"], errors="coerce").fillna(0).astype(bool)
    return [
        audit_row(household, "person_need_proxy_candidate", "Any chronic/disability or sudden-illness need proxy", "need_denominator", broad, pd.to_numeric(household["person_need_proxy_candidate"], errors="coerce") > 0, "Any Health B access trigger is nonmissing.", "Any Health A person need proxy is observed in the household.", "m5a_q01;m5a_q07", climate_ready),
        audit_row(household, "q01_family_healthcare_need_candidate", "Family health-care need denominator from q01", "need_denominator", broad, q01_need, "Any Health B access trigger is nonmissing.", "m5b_q01 is not coded as no-one-needed-health-care.", "m5b_q01", climate_ready),
        audit_row(household, "q01_cost_difficulty_candidate", "Difficulty paying for family health care among q01 need", "cost_barrier", q01_need, pd.to_numeric(household["q01_cost_difficulty_candidate"], errors="coerce") > 0, "m5b_q01 indicates a household health-care need.", "m5b_q01 is very difficult or difficult.", "m5b_q01", climate_ready),
        audit_row(household, "money_raising_any_candidate", "Any money-raising method for health care", "coping_barrier", pd.to_numeric(household["q01_cost_difficulty_candidate"], errors="coerce") > 0, pd.to_numeric(household["money_raising_any_candidate"], errors="coerce") > 0, "m5b_q01 is very difficult or difficult.", "Any m5b_q02 method indicator equals 1.", "m5b_q02_;m5b_q021;m5b_q022;m5b_q023;m5b_q024", climate_ready),
        audit_row(household, "delayed_help_any_candidate", "Delayed or did not seek help after illness", "forgone_or_delayed_care", q01_need, pd.to_numeric(household["delayed_help_any_candidate"], errors="coerce") > 0, "m5b_q01 indicates a household health-care need.", "m5b_q03 is once or more.", "m5b_q03", climate_ready),
        audit_row(household, "hospital_referral_not_gone_candidate", "Hospital referral not gone", "forgone_or_delayed_care", q01_need, pd.to_numeric(household["hospital_referral_not_gone_candidate"], errors="coerce") > 0, "m5b_q01 indicates a household health-care need.", "m5b_q05 is once or more.", "m5b_q05", climate_ready),
        audit_row(household, "refused_health_services_candidate", "Any health-service refusal", "forgone_or_delayed_care", broad, pd.to_numeric(household["refused_health_services_candidate"], errors="coerce") > 0, "Any Health B access trigger is nonmissing.", "m5b_q07 is yes.", "m5b_q07", climate_ready),
        audit_row(household, "medicine_discount_any_barrier_candidate", "Medicine discount entitlement not always exercisable", "medicine_access_barrier", med_entitled, pd.to_numeric(household["medicine_discount_any_barrier_candidate"], errors="coerce") > 0, "m5b_q09 indicates medicine-discount entitlement.", "m5b_q10 is any no/other category rather than always able.", "m5b_q09;m5b_q10", climate_ready),
        audit_row(household, "composite_cost_barrier_candidate", "Composite cost barrier", "cost_barrier", broad, pd.to_numeric(household["composite_cost_barrier_candidate"], errors="coerce") > 0, "Any Health B access/cost trigger is nonmissing.", "Any affordability, delayed-care cost, referral cost, refusal cost, or medicine-discount cost barrier is observed.", "m5b_q01;m5b_q04;m5b_q06;m5b_q08;m5b_q10", climate_ready),
        audit_row(household, "composite_distance_barrier_candidate", "Composite distance barrier", "distance_barrier", broad, pd.to_numeric(household["composite_distance_barrier_candidate"], errors="coerce") > 0, "Any Health B access/distance trigger is nonmissing.", "Any delayed-care, referral, or refusal distance barrier is observed.", "m5b_q04;m5b_q06;m5b_q08", climate_ready),
        audit_row(household, "composite_supply_admin_barrier_candidate", "Composite supply/admin barrier", "supply_or_admin_barrier", broad, pd.to_numeric(household["composite_supply_admin_barrier_candidate"], errors="coerce") > 0, "Any Health B access/supply trigger is nonmissing.", "Any referral, refusal, or medicine discount supply/admin barrier is observed.", "m5b_q06;m5b_q08;m5b_q10", climate_ready),
        audit_row(household, "composite_delayed_refused_nonuse_candidate", "Composite delayed/refused/nonuse", "forgone_or_delayed_care", broad, pd.to_numeric(household["composite_delayed_refused_nonuse_candidate"], errors="coerce") > 0, "Any Health B access trigger is nonmissing.", "Delayed care, hospital referral not gone, or refused health services is observed.", "m5b_q03;m5b_q05;m5b_q07", climate_ready),
        audit_row(household, "composite_any_access_barrier_candidate", "Composite any access barrier", "access_failure_composite", broad, pd.to_numeric(household["composite_any_access_barrier_candidate"], errors="coerce") > 0, "Any Health B access trigger is nonmissing.", "Any cost, distance, supply/admin, delayed-care, referral nonuse, or refusal signal is observed.", "m5b_q01;m5b_q03;m5b_q04;m5b_q05;m5b_q06;m5b_q07;m5b_q08;m5b_q10", climate_ready),
    ]


def lineage_rows() -> list[dict[str, str]]:
    artifacts = "temp/alb2002_household_core_candidate.csv;temp/alb2002_access_need_denominator_policy_audit.csv;result/alb2002_access_need_denominator_policy_summary.csv"
    rows = [
        ("lineage_001", "person_need_proxy_candidate", "m5a_q01;m5a_q07", "Any person chronic/disability or sudden-illness proxy aggregated to household.", "Person-to-household need proxy is candidate-only."),
        ("lineage_002", "q01_family_healthcare_need_candidate", "m5b_q01", "m5b_q01 in 1,2,3; code 4 treated as no-one-needed-health-care.", "Broad household need denominator requires final acceptance."),
        ("lineage_003", "q01_cost_difficulty_candidate", "m5b_q01", "m5b_q01 in 1,2 among q01 need-coded households.", "Broad affordability is not the same as forgone care."),
        ("lineage_004", "delayed_help_any_candidate", "m5b_q03", "m5b_q03 greater than none.", "Delayed-care count coding and denominator require final review."),
        ("lineage_005", "hospital_referral_not_gone_candidate", "m5b_q05", "m5b_q05 greater than none.", "Referral nonuse has a narrower trigger than broad need."),
        ("lineage_006", "refused_health_services_candidate", "m5b_q07", "m5b_q07 yes.", "Ever-refusal scope and period require final review."),
        ("lineage_007", "medicine_discount_*_candidate", "m5b_q09;m5b_q10", "Medicine discount barriers among entitled households.", "Entitlement-specific barrier should not be pooled without a scope decision."),
        ("lineage_008", "composite_*_candidate", "m5b_q01;m5b_q03;m5b_q04;m5b_q05;m5b_q06;m5b_q07;m5b_q08;m5b_q10", "Union of cost, distance, supply/admin, delayed-care, referral nonuse, refusal, and medicine barriers.", "Composite mixes denominators and is a screening diagnostic only."),
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


def build_summary(household: pd.DataFrame, audit: list[dict[str, str]], climate_ready: int) -> list[dict[str, str]]:
    policy_summary = read_csv_dicts(ACCESS_POLICY_SUMMARY_PATH)
    audit_by_id = {row["outcome_id"]: row for row in audit}

    def event_rows(outcome_id: str) -> str:
        return audit_by_id.get(outcome_id, {}).get("event_rows", "0")

    def event_rate(outcome_id: str) -> str:
        return audit_by_id.get(outcome_id, {}).get("event_rate", "")

    def weighted_rate_value(outcome_id: str) -> str:
        return audit_by_id.get(outcome_id, {}).get("weighted_event_rate", "")

    return [
        summary_row("alb2002_access_candidate_household_rows", len(household), "Temp-only ALB_2002 household access candidate rows."),
        summary_row("alb2002_access_candidate_lineage_rows", 8, "Lineage rows for access candidate fields."),
        summary_row("alb2002_access_candidate_audit_rows", len(audit), "Outcome audit rows for access candidate fields."),
        summary_row("alb2002_access_candidate_q01_need_rows", event_rows("q01_family_healthcare_need_candidate"), "Households not coded as no-one-needed-care by m5b_q01."),
        summary_row("alb2002_access_candidate_person_need_rows", event_rows("person_need_proxy_candidate"), "Households with Health A person-level need proxy."),
        summary_row("alb2002_access_candidate_q01_cost_difficulty_rows", event_rows("q01_cost_difficulty_candidate"), "Households reporting difficult/very difficult health-care payment situation."),
        summary_row("alb2002_access_candidate_delayed_help_rows", event_rows("delayed_help_any_candidate"), "Households with delayed or not-sought help candidate."),
        summary_row("alb2002_access_candidate_referral_not_gone_rows", event_rows("hospital_referral_not_gone_candidate"), "Households with hospital referral not gone candidate."),
        summary_row("alb2002_access_candidate_refused_service_rows", event_rows("refused_health_services_candidate"), "Households with health-service refusal candidate."),
        summary_row("alb2002_access_candidate_medicine_discount_any_barrier_rows", event_rows("medicine_discount_any_barrier_candidate"), "Households with medicine-discount entitlement barrier candidate."),
        summary_row("alb2002_access_candidate_composite_cost_rows", event_rows("composite_cost_barrier_candidate"), "Composite cost-barrier candidate rows."),
        summary_row("alb2002_access_candidate_composite_cost_rate", event_rate("composite_cost_barrier_candidate"), "Composite cost-barrier unweighted candidate rate."),
        summary_row("alb2002_access_candidate_composite_cost_weighted_rate", weighted_rate_value("composite_cost_barrier_candidate"), "Composite cost-barrier weighted candidate rate."),
        summary_row("alb2002_access_candidate_composite_distance_rows", event_rows("composite_distance_barrier_candidate"), "Composite distance-barrier candidate rows."),
        summary_row("alb2002_access_candidate_composite_supply_admin_rows", event_rows("composite_supply_admin_barrier_candidate"), "Composite supply/admin-barrier candidate rows."),
        summary_row("alb2002_access_candidate_composite_nonuse_rows", event_rows("composite_delayed_refused_nonuse_candidate"), "Composite delayed/refused/nonuse candidate rows."),
        summary_row("alb2002_access_candidate_composite_any_rows", event_rows("composite_any_access_barrier_candidate"), "Composite any-access-barrier candidate rows."),
        summary_row("alb2002_access_candidate_composite_any_rate", event_rate("composite_any_access_barrier_candidate"), "Composite any-access-barrier unweighted candidate rate."),
        summary_row("alb2002_access_candidate_composite_any_weighted_rate", weighted_rate_value("composite_any_access_barrier_candidate"), "Composite any-access-barrier weighted candidate rate."),
        summary_row("alb2002_access_candidate_policy_rows_observed", metric_value(policy_summary, "alb2002_access_need_denominator_policy_rows"), "Upstream access/need policy audit rows consumed."),
        summary_row("alb2002_access_candidate_low_event_rate_rows", sum(1 for row in audit if row["low_event_rate_flag"] == "1"), "Candidate access outcomes with event rate below 3 percent."),
        summary_row("alb2002_access_candidate_outcome_promotion_ready_rows", 0, "Rows ready for final access-outcome promotion; intentionally zero."),
        summary_row("alb2002_access_candidate_recipe_ready_rows", 0, "Rows ready for harmonized recipe promotion; intentionally zero."),
        summary_row("alb2002_access_candidate_sdg382_ready_rows", 0, "Rows ready for SDG 3.8.2 construction; intentionally zero."),
        summary_row("alb2002_access_candidate_climate_linkage_ready_rows", climate_ready, "Rows ready for climate linkage; should remain zero until geography is verified."),
        summary_row("alb2002_access_candidate_current_decision", DECISION, "Current fail-closed access candidate outcome decision."),
    ]


def markdown_rows(rows: list[dict[str, str]], columns: list[str], limit: int = 25) -> str:
    lines = ["| " + " | ".join(columns) + " |", "|" + "|".join("---" for _ in columns) + "|"]
    for row in rows[:limit]:
        values = []
        for column in columns:
            value = str(row.get(column, "")).replace("|", "/")
            if len(value) > 135:
                value = value[:132] + "..."
            values.append(value)
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines)


def write_report(summary: list[dict[str, str]], audit: list[dict[str, str]], lineage: list[dict[str, str]]) -> None:
    summary_table = "\n".join(f"| {row['metric']} | {row['value']} | {row['interpretation']} |" for row in summary)
    REPORT_PATH.write_text(
        f"""# ALB_2002 Access Candidate Outcome Audit

Status: temp-only household-level access candidate outcome audit. This builds household access, need, barrier, and composite candidates from raw ALB_2002 Health A/B variables. It does not write `data/`, does not construct final access outcomes, and does not promote any row to harmonization, SDG 3.8.2, or climate linkage.

## Summary

| Metric | Value | Interpretation |
|---|---:|---|
{summary_table}

## Outcome Audit

{markdown_rows(audit, ['outcome_id', 'outcome_family', 'denominator_rows', 'event_rows', 'event_rate', 'weighted_event_rate', 'low_event_rate_flag', 'ready_for_outcome'])}

## Lineage

{markdown_rows(lineage, ['derived_field', 'source_fields', 'formula_or_rule', 'status', 'blocking_reason'])}

## Interpretation

- Candidate access outcomes are now available at household level in `temp/alb2002_access_candidate_household_outcomes.csv`.
- `m5b_q01` is the broadest need-denominator candidate, while delay, referral, refusal, and medicine-discount fields have narrower trigger-specific denominators.
- Composite access candidates are screening diagnostics only because they mix broad affordability, delayed care, referral nonuse, refusal, medicine entitlement, and conditional reason scopes.
- Outcome-promotion-ready, recipe-ready, SDG 3.8.2-ready, and climate-linkage-ready rows remain zero.

## Machine-Readable Outputs

- `temp/alb2002_access_candidate_household_outcomes.csv`
- `temp/alb2002_access_candidate_outcome_lineage.csv`
- `result/alb2002_access_candidate_outcome_audit.csv`
- `result/alb2002_access_candidate_outcome_summary.csv`
""",
        encoding="utf-8",
    )


def main() -> None:
    ensure_dirs()
    household = build_household_outcomes()
    # This artifact is a temp-only access outcome candidate; climate promotion
    # stays fail-closed even if a geography crosswalk later becomes available.
    climate_ready = 0
    audit = build_audit(household, climate_ready)
    lineage = lineage_rows()
    summary = build_summary(household, audit, climate_ready)

    write_csv(HOUSEHOLD_OUTCOME_PATH, household.fillna("").to_dict("records"), HOUSEHOLD_COLUMNS)
    write_csv(LINEAGE_PATH, lineage, LINEAGE_COLUMNS)
    write_csv(AUDIT_PATH, audit, AUDIT_COLUMNS)
    write_csv(SUMMARY_PATH, summary, SUMMARY_COLUMNS)
    write_report(summary, audit, lineage)
    append_log(TEMP_DIR / "audit_log.md", f"Built ALB_2002 access candidate outcome audit rows={len(household)} decision={DECISION}.")
    print(f"ALB_2002 access candidate outcomes rows={len(household)} decision={DECISION}.")


if __name__ == "__main__":
    main()
