from __future__ import annotations

import math
import warnings
from typing import Any

import pandas as pd

from common import REPORT_DIR, RESULT_DIR, TEMP_DIR, append_log, ensure_dirs, write_csv

try:
    import pyreadstat
except ImportError:  # pragma: no cover - environment audit reports this separately.
    pyreadstat = None


IDNO = "ALB_2012_LSMS_v01_M_v01_A_PUF"
COUNTRY = "Albania"
SURVEY_NAME = "Living Standards Measurement Survey 2012"
WAVE = "2012"
RAW_ROOT = TEMP_DIR / "raw_extracted" / "lsms_2012_eng_7631729d2caf" / "LSMS 2012_eng" / "Data_LSMS 2012"

CANDIDATE_PATH = TEMP_DIR / "alb2012_household_core_candidate.csv"
AUDIT_PATH = TEMP_DIR / "alb2012_raw_core_feasibility_audit.csv"
LINEAGE_PATH = TEMP_DIR / "alb2012_raw_core_lineage.csv"
SUMMARY_PATH = RESULT_DIR / "alb2012_raw_core_feasibility_summary.csv"
REPORT_PATH = REPORT_DIR / "alb2012_raw_core_feasibility.md"

DECISION = "temp_candidate_no_interview_timing_coarse_geography_outcome_semantics_pending"
NO_PROMOTION = "not_ready_for_harmonization_or_climate_linkage"
BLOCKING_REASON = (
    "temp raw-core feasibility only; interview month/date is not observed, geography is prefecture/region/urban only, "
    "GPS is absent, and OOP/access variables require unit, recall-period, missing-code, skip-pattern, and merge review"
)

FOUR_WEEK_OOP = [
    "M9A_Q18",
    "M9A_Q19",
    "M9A_Q22",
    "M9A_Q24",
    "M9A_Q25",
    "M9A_Q30",
    "M9A_Q31",
    "M9A_Q34",
    "M9A_Q36",
    "M9A_Q37",
    "M9A_Q40",
    "M9A_Q41",
    "M9A_Q43",
    "M9A_Q44",
    "M9A_Q45",
    "M9A_Q48",
    "M9A_Q49",
    "M9A_Q51",
    "M9A_Q52",
    "M9A_Q53",
    "M9A_Q56",
    "M9A_Q57",
    "M9A_Q59",
    "M9A_Q60",
    "M9A_Q61",
    "M9A_Q63",
]
TWELVE_MONTH_OOP = [
    "M9A_Q70",
    "M9A_Q71",
    "M9A_Q73",
    "M9A_Q74",
    "M9A_Q75",
    "M9A_Q76",
    "M9A_Q79",
    "M9A_Q80",
    "M9A_Q82",
    "M9A_Q83",
    "M9A_Q84",
]

AUDIT_COLUMNS = [
    "country",
    "survey_name",
    "wave",
    "idno",
    "audit_domain",
    "audit_item",
    "source_file",
    "merge_key",
    "raw_variables",
    "row_count",
    "complete_key_rows",
    "distinct_key_count",
    "duplicate_key_rows",
    "base_rows",
    "base_rows_matched",
    "base_match_rate",
    "nonmissing_rows",
    "positive_or_signal_rows",
    "audit_status",
    "promotion_status",
    "blocking_reason",
]
LINEAGE_COLUMNS = [
    "country",
    "survey_name",
    "wave",
    "idno",
    "candidate_column",
    "source_file",
    "raw_variables",
    "transformation",
    "status",
    "blocking_reason",
]
SUMMARY_COLUMNS = ["metric", "value", "interpretation"]


def read_sav(file_name: str, usecols: list[str] | None = None) -> tuple[pd.DataFrame, Any]:
    if pyreadstat is None:
        raise RuntimeError("pyreadstat is not available")
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        return pyreadstat.read_sav(str(RAW_ROOT / file_name), usecols=usecols, apply_value_formats=False)


def sav_columns(file_name: str) -> list[str]:
    _, meta = read_sav(file_name)
    return list(meta.column_names)


def existing_columns(file_name: str, requested: list[str]) -> list[str]:
    available = set(sav_columns(file_name))
    return [column for column in requested if column in available]


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


def compact_join(values: list[Any], limit: int = 40) -> str:
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


def add_psu_hh_key(df: pd.DataFrame, psu: str = "psu", hh: str = "hh") -> pd.DataFrame:
    out = df.copy()
    out["psu_key"] = out[psu].map(key_part)
    out["hh_key"] = out[hh].map(key_part)
    out["psu_hh_key"] = out["psu_key"] + "-" + out["hh_key"]
    out.loc[(out["psu_key"] == "") | (out["hh_key"] == ""), "psu_hh_key"] = ""
    return out


def numeric(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series, errors="coerce")


def row_sum(frame: pd.DataFrame, columns: list[str]) -> pd.Series:
    present = [column for column in columns if column in frame.columns]
    if not present:
        return pd.Series(0.0, index=frame.index)
    return frame[present].apply(pd.to_numeric, errors="coerce").fillna(0).sum(axis=1)


def bool_from_codes(series: pd.Series, true_codes: set[int]) -> pd.Series:
    return numeric(series).isin(true_codes)


def key_audit(
    audit_item: str,
    source_file: str,
    df: pd.DataFrame,
    key: str,
    base_keys: set[str],
    allow_many_to_one: bool,
    raw_variables: list[str],
) -> dict[str, str]:
    complete = df[key].astype(str).str.len() > 0
    complete_count = int(complete.sum())
    distinct = int(df.loc[complete, key].drop_duplicates().shape[0])
    duplicates = max(complete_count - distinct, 0)
    module_keys = set(df.loc[complete, key].astype(str))
    matched = len(base_keys.intersection(module_keys))
    unmatched_module_rows = int((~df.loc[complete, key].astype(str).isin(base_keys)).sum())
    if complete_count == 0:
        status = "blocked_no_complete_keys"
        reason = "module has no complete household merge keys"
    elif duplicates > 0 and not allow_many_to_one:
        status = "blocked_duplicate_household_keys"
        reason = "household-level module repeats the household merge key"
    elif matched == 0:
        status = "blocked_no_base_matches"
        reason = "module keys do not match base household keys"
    elif matched < len(base_keys):
        status = "partial_base_coverage_review_required"
        reason = "module covers only a subset of base households"
    else:
        status = "base_coverage_complete_merge_review_required"
        reason = "base household keys are covered, but values and semantics still require review"
    return {
        "country": COUNTRY,
        "survey_name": SURVEY_NAME,
        "wave": WAVE,
        "idno": IDNO,
        "audit_domain": "merge_key",
        "audit_item": audit_item,
        "source_file": source_file,
        "merge_key": key,
        "raw_variables": compact_join(raw_variables),
        "row_count": str(len(df)),
        "complete_key_rows": str(complete_count),
        "distinct_key_count": str(distinct),
        "duplicate_key_rows": str(duplicates),
        "base_rows": str(len(base_keys)),
        "base_rows_matched": str(matched),
        "base_match_rate": f"{matched / len(base_keys):.6f}" if base_keys else "0",
        "nonmissing_rows": "",
        "positive_or_signal_rows": str(max(unmatched_module_rows, 0)),
        "audit_status": status,
        "promotion_status": NO_PROMOTION,
        "blocking_reason": reason,
    }


def gate_row(audit_item: str, source_file: str, raw_variables: list[str], nonmissing: int, signal: int, status: str, reason: str) -> dict[str, str]:
    return {
        "country": COUNTRY,
        "survey_name": SURVEY_NAME,
        "wave": WAVE,
        "idno": IDNO,
        "audit_domain": "value_timing_geography",
        "audit_item": audit_item,
        "source_file": source_file,
        "merge_key": "",
        "raw_variables": compact_join(raw_variables),
        "row_count": "",
        "complete_key_rows": "",
        "distinct_key_count": "",
        "duplicate_key_rows": "",
        "base_rows": "",
        "base_rows_matched": "",
        "base_match_rate": "",
        "nonmissing_rows": str(nonmissing),
        "positive_or_signal_rows": str(signal),
        "audit_status": status,
        "promotion_status": NO_PROMOTION,
        "blocking_reason": reason,
    }


def build_candidate_and_audit() -> tuple[pd.DataFrame, list[dict[str, str]], list[dict[str, str]], list[dict[str, str]]]:
    poverty, _ = read_sav(
        "poverty.sav",
        ["psu", "hh", "hhid", "prefecture", "urban", "region", "totcons", "rcons", "rfood", "rtotnfood", "rtotutil"],
    )
    poverty = add_psu_hh_key(poverty)
    base_keys = set(poverty["psu_hh_key"])
    candidate = pd.DataFrame(
        {
            "country": COUNTRY,
            "survey_name": SURVEY_NAME,
            "wave": WAVE,
            "idno": IDNO,
            "survey_year": 2012,
            "hhid": poverty["hhid"].map(key_part),
            "psu": poverty["psu_key"],
            "hh": poverty["hh_key"],
            "total_consumption": numeric(poverty["totcons"]),
            "real_consumption": numeric(poverty["rcons"]),
            "per_capita_food_consumption": numeric(poverty["rfood"]),
            "per_capita_nonfood_consumption": numeric(poverty["rtotnfood"]),
            "utility_consumption": numeric(poverty["rtotutil"]),
            "prefecture": poverty["prefecture"].map(fmt),
            "region": poverty["region"].map(fmt),
            "urban_rural_code": poverty["urban"].map(fmt),
            "survey_month": "",
            "interview_date": "",
            "geolocation_quality": "prefecture_region_urban_only_no_gps_no_interview_timing",
        },
        index=poverty.index,
    )
    candidate["psu_hh_key"] = poverty["psu_hh_key"]

    audit_rows: list[dict[str, str]] = [
        key_audit("base_consumption_poverty", "poverty.sav", poverty, "psu_hh_key", base_keys, False, list(poverty.columns))
    ]

    weight, _ = read_sav("Weight_lsms2012_retro.sav")
    weight = add_psu_hh_key(weight)
    audit_rows.append(key_audit("household_weight_retro", "Weight_lsms2012_retro.sav", weight, "psu_hh_key", base_keys, False, list(weight.columns)))
    candidate = candidate.merge(weight[["psu_hh_key", "pesha10tetor"]], on="psu_hh_key", how="left")
    candidate.rename(columns={"pesha10tetor": "household_weight"}, inplace=True)

    roster, _ = read_sav("Modul_1A_householdroster.sav", ["psu", "hh", "idcode", "hhid", "m1a_q02", "m1a_q03", "m1a_q05y"])
    roster = add_psu_hh_key(roster)
    audit_rows.append(key_audit("household_roster", "Modul_1A_householdroster.sav", roster, "psu_hh_key", base_keys, True, list(roster.columns)))
    age = numeric(roster["m1a_q05y"])
    roster["child_under5"] = age.lt(5)
    roster["child_under15"] = age.lt(15)
    roster["elderly_60plus"] = age.ge(60)
    roster["elderly_65plus"] = age.ge(65)
    roster_group = roster.groupby("psu_hh_key").agg(
        household_size=("idcode", "count"),
        children_under5=("child_under5", "sum"),
        children_under15=("child_under15", "sum"),
        elderly_60plus=("elderly_60plus", "sum"),
        elderly_65plus=("elderly_65plus", "sum"),
    )
    head = roster.loc[numeric(roster["m1a_q03"]).eq(1), ["psu_hh_key", "m1a_q02", "m1a_q05y"]].drop_duplicates("psu_hh_key")
    head = head.rename(columns={"m1a_q02": "head_sex", "m1a_q05y": "head_age"})
    candidate = candidate.merge(roster_group, on="psu_hh_key", how="left").merge(head, on="psu_hh_key", how="left")

    health_cols = ["psu", "hh", "M9A_Q03", "M9A_Q11", "M9A_Q85"] + existing_columns("modul_9A_health.sav", FOUR_WEEK_OOP + TWELVE_MONTH_OOP)
    health, _ = read_sav("modul_9A_health.sav", health_cols)
    health = add_psu_hh_key(health)
    audit_rows.append(key_audit("person_health_oop_need", "modul_9A_health.sav", health, "psu_hh_key", base_keys, True, health_cols))
    health["oop_4w_row_sum_unreviewed"] = row_sum(health, FOUR_WEEK_OOP)
    health["oop_12m_row_sum_unreviewed"] = row_sum(health, TWELVE_MONTH_OOP)
    health["chronic_illness_person"] = bool_from_codes(health["M9A_Q03"], {1})
    health["sudden_illness_person"] = bool_from_codes(health["M9A_Q11"], {1})
    health["health_license_person"] = bool_from_codes(health["M9A_Q85"], {1})
    health_group = health.groupby("psu_hh_key").agg(
        oop_4w_sum_unreviewed=("oop_4w_row_sum_unreviewed", "sum"),
        oop_12m_sum_unreviewed=("oop_12m_row_sum_unreviewed", "sum"),
        chronic_illness_any=("chronic_illness_person", "max"),
        sudden_illness_4w_any=("sudden_illness_person", "max"),
        health_license_any=("health_license_person", "max"),
    )
    candidate = candidate.merge(health_group, on="psu_hh_key", how="left")
    candidate["oop_4w_any_unreviewed"] = numeric(candidate["oop_4w_sum_unreviewed"]).gt(0)
    candidate["oop_12m_any_unreviewed"] = numeric(candidate["oop_12m_sum_unreviewed"]).gt(0)

    access_cols = [
        "psu",
        "hh",
        "M9B_Q01",
        "Q02_A",
        "Q02_B",
        "Q02_C",
        "Q02_D",
        "Q02_E",
        "M9B_Q03",
        "M9B_Q04",
        "M9B_Q05",
        "M9B_Q06",
        "M9B_Q07",
        "M9B_Q08",
        "M9B_Q10",
    ]
    access, _ = read_sav("Modul_9B_Access_to_Health_Care.sav", access_cols)
    access = add_psu_hh_key(access)
    audit_rows.append(key_audit("household_access_to_health", "Modul_9B_Access_to_Health_Care.sav", access, "psu_hh_key", base_keys, False, access_cols))
    access_features = pd.DataFrame(
        {
            "psu_hh_key": access["psu_hh_key"],
            "difficulty_pay_health": numeric(access["M9B_Q01"]).isin({1, 2}),
            "health_payment_money_raising_any_unreviewed": access[["Q02_A", "Q02_B", "Q02_C", "Q02_D", "Q02_E"]].apply(pd.to_numeric, errors="coerce").eq(1).any(axis=1),
            "delayed_help_any": numeric(access["M9B_Q03"]).gt(0),
            "delay_reason_cost": numeric(access["M9B_Q04"]).eq(4),
            "delay_reason_distance": numeric(access["M9B_Q04"]).eq(5),
            "hospital_referral_not_gone_any": numeric(access["M9B_Q05"]).gt(0),
            "not_gone_reason_cost": numeric(access["M9B_Q06"]).eq(2),
            "not_gone_reason_distance": numeric(access["M9B_Q06"]).isin({3, 6}),
            "refused_health_services_any": numeric(access["M9B_Q07"]).eq(1),
            "refused_reason_cost": numeric(access["M9B_Q08"]).eq(1),
            "refused_reason_distance": numeric(access["M9B_Q08"]).eq(2),
            "medicine_discount_cost_barrier": numeric(access["M9B_Q10"]).eq(5),
        }
    )
    candidate = candidate.merge(access_features, on="psu_hh_key", how="left")

    shocks_cols = ["psu", "hh", "M6D_Q00", "M6D_Q01", "M6D_2008", "M6D_2009", "M6D_2010", "M6D_2011", "M6D_2012"]
    shocks, _ = read_sav("Modul_6D_Shocks to the household.sav", shocks_cols)
    shocks = add_psu_hh_key(shocks)
    audit_rows.append(key_audit("household_shock_module", "Modul_6D_Shocks to the household.sav", shocks, "psu_hh_key", base_keys, True, shocks_cols))
    shock_cols = [column for column in ["M6D_Q01", "M6D_2008", "M6D_2009", "M6D_2010", "M6D_2011", "M6D_2012"] if column in shocks.columns]
    shocks["shock_any_2008_2012"] = shocks[shock_cols].apply(pd.to_numeric, errors="coerce").eq(1).any(axis=1)
    shock_group = shocks.groupby("psu_hh_key").agg(shock_any_2008_2012=("shock_any_2008_2012", "max"))
    candidate = candidate.merge(shock_group, on="psu_hh_key", how="left")

    candidate.drop(columns=["psu_hh_key"], inplace=True)
    candidate["core_candidate_status"] = DECISION
    candidate["blocking_reason"] = BLOCKING_REASON

    audit_rows.extend(
        [
            gate_row(
                "interview_timing",
                "all_2012_sav_files",
                [],
                0,
                0,
                "blocked_no_interview_month_or_date_signal",
                "No raw interview month/date field was identified; recall-period and event-history dates are not survey fieldwork timing.",
            ),
            gate_row(
                "current_geography",
                "poverty.sav",
                ["prefecture", "region", "urban"],
                int(candidate["region"].astype(str).str.len().gt(0).sum()),
                int(candidate["prefecture"].astype(str).str.len().gt(0).sum()),
                "blocked_coarse_prefecture_region_only_no_gps",
                "Current household geography is coarse prefecture/region/urban only; no district/admin2, cluster coordinates, or GPS are verified.",
            ),
            gate_row(
                "gps_coordinates",
                "all_2012_sav_files",
                [],
                0,
                0,
                "blocked_no_coordinate_signal",
                "No latitude, longitude, GPS, or coordinate variable was identified in the extracted public files.",
            ),
            gate_row(
                "oop_access_value_semantics",
                "modul_9A_health.sav;Modul_9B_Access_to_Health_Care.sav",
                FOUR_WEEK_OOP + TWELVE_MONTH_OOP + access_cols,
                int(candidate["oop_4w_sum_unreviewed"].notna().sum()),
                int(numeric(candidate["oop_4w_sum_unreviewed"]).gt(0).sum()),
                "blocked_units_recall_skip_patterns_unreviewed",
                "Observed OOP/access variation is present, but units, recall periods, skip patterns, missing codes, and household aggregation remain unverified.",
            ),
        ]
    )

    lineage = [
        {
            "candidate_column": "hhid;psu;hh;total_consumption;real_consumption;food/nonfood utility components",
            "source_file": "poverty.sav",
            "raw_variables": "hhid;psu;hh;totcons;rcons;rfood;rtotnfood;rtotutil",
            "transformation": "household-level base frame and survey-team consumption aggregates",
            "status": "candidate_value_review_required",
            "blocking_reason": "consumption units and cross-wave comparability require review before harmonization",
        },
        {
            "candidate_column": "household_weight",
            "source_file": "Weight_lsms2012_retro.sav",
            "raw_variables": "pesha10tetor",
            "transformation": "merge retro household weight on psu-hh key",
            "status": "candidate_design_review_required",
            "blocking_reason": "weight meaning, scaling, and survey design variables require documentation review",
        },
        {
            "candidate_column": "prefecture;region;urban_rural_code",
            "source_file": "poverty.sav",
            "raw_variables": "prefecture;region;urban",
            "transformation": "carry coarse current geography fields from poverty file",
            "status": "candidate_geography_blocked",
            "blocking_reason": "coarse geography only; no GPS/admin2 and no interview timing for climate linkage",
        },
        {
            "candidate_column": "household_size;children/elderly/head demographics",
            "source_file": "Modul_1A_householdroster.sav",
            "raw_variables": "idcode;m1a_q02;m1a_q03;m1a_q05y",
            "transformation": "aggregate roster age and head fields by household",
            "status": "candidate_value_review_required",
            "blocking_reason": "roster member universe and head coding require review",
        },
        {
            "candidate_column": "oop_4w_sum_unreviewed;oop_12m_sum_unreviewed;need/license proxies",
            "source_file": "modul_9A_health.sav",
            "raw_variables": compact_join(FOUR_WEEK_OOP + TWELVE_MONTH_OOP + ["M9A_Q03", "M9A_Q11", "M9A_Q85"]),
            "transformation": "person-level OOP payment item sums and need/license proxies by household",
            "status": "candidate_aggregation_review_required",
            "blocking_reason": "OOP items mix care contexts and recall periods; units, missing codes, and aggregation require review",
        },
        {
            "candidate_column": "difficulty/access/coping proxies",
            "source_file": "Modul_9B_Access_to_Health_Care.sav",
            "raw_variables": compact_join(access_cols),
            "transformation": "derive household-level unreviewed affordability, access, refusal, and coping proxies",
            "status": "candidate_skip_pattern_review_required",
            "blocking_reason": "access outcomes require skip-pattern, reason-code, and denominator validation",
        },
        {
            "candidate_column": "shock_any_2008_2012",
            "source_file": "Modul_6D_Shocks to the household.sav",
            "raw_variables": compact_join(shocks_cols),
            "transformation": "derive any-shock diagnostic across reported 2008-2012 shock columns",
            "status": "candidate_mechanism_review_required",
            "blocking_reason": "shock type semantics and timing are not climate exposure variables",
        },
    ]
    lineage = [{"country": COUNTRY, "survey_name": SURVEY_NAME, "wave": WAVE, "idno": IDNO, **row} for row in lineage]
    summary = build_summary(candidate, audit_rows)
    return candidate, audit_rows, lineage, summary


def summary_row(metric: str, value: Any, interpretation: str) -> dict[str, str]:
    return {"metric": metric, "value": fmt(value), "interpretation": interpretation}


def build_summary(candidate: pd.DataFrame, audit_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    rows = [
        summary_row("alb2012_household_core_candidate_rows", len(candidate), "Rows in the ALB_2012 temp-only household core candidate."),
        summary_row("alb2012_household_core_recipe_ready_rows", 0, "Rows ready for harmonization recipe promotion after this audit."),
        summary_row("alb2012_climate_linkage_ready_rows", 0, "Rows ready for climate-linkage input promotion after this audit."),
        summary_row("alb2012_households_with_total_consumption", int(candidate["total_consumption"].notna().sum()), "Households with survey-team total consumption aggregate."),
        summary_row("alb2012_households_with_household_weight", int(candidate["household_weight"].notna().sum()), "Households with retro household weight candidate."),
        summary_row("alb2012_households_with_prefecture", int(candidate["prefecture"].astype(str).str.len().gt(0).sum()), "Households with coarse prefecture field."),
        summary_row("alb2012_households_with_region", int(candidate["region"].astype(str).str.len().gt(0).sum()), "Households with coarse region field."),
        summary_row("alb2012_households_with_survey_month", 0, "Households with raw interview month; none identified."),
        summary_row("alb2012_households_with_interview_date", 0, "Households with raw interview date; none identified."),
        summary_row("alb2012_households_with_oop_4w_positive", int(numeric(candidate["oop_4w_sum_unreviewed"]).gt(0).sum()), "Households with positive unreviewed four-week OOP item sum."),
        summary_row("alb2012_households_with_oop_12m_positive", int(numeric(candidate["oop_12m_sum_unreviewed"]).gt(0).sum()), "Households with positive unreviewed twelve-month OOP item sum."),
        summary_row("alb2012_households_with_access_affordability_proxy", int(candidate["difficulty_pay_health"].fillna(False).astype(bool).sum()), "Households with difficulty paying health care proxy."),
        summary_row("alb2012_households_with_shock_any_2008_2012", int(candidate["shock_any_2008_2012"].fillna(False).astype(bool).sum()), "Households with any unreviewed shock-module positive signal."),
        summary_row("alb2012_raw_core_audit_rows", len(audit_rows), "Rows in the ALB_2012 raw core feasibility audit."),
        summary_row("alb2012_merge_modules_complete_base_coverage", sum(1 for row in audit_rows if row["audit_status"] == "base_coverage_complete_merge_review_required"), "Merge-audit rows with complete base household key coverage."),
        summary_row("alb2012_timing_signal_rows", 0, "Raw interview timing rows identified for climate windows."),
        summary_row("alb2012_coordinate_signal_rows", 0, "Raw coordinate/GPS rows identified for climate linkage."),
        summary_row("alb2012_raw_core_current_decision", DECISION, "Current fail-closed decision for ALB_2012 raw core feasibility."),
    ]
    return rows


def markdown_rows(rows: list[dict[str, str]], columns: list[str], limit: int = 30) -> str:
    lines = ["| " + " | ".join(columns) + " |", "|" + "|".join("---" for _ in columns) + "|"]
    for row in rows[:limit]:
        values = []
        for column in columns:
            value = (row.get(column, "") or "").replace("|", "/")
            if len(value) > 110:
                value = value[:107] + "..."
            values.append(value)
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines)


def write_report(audit_rows: list[dict[str, str]], lineage: list[dict[str, str]], summary: list[dict[str, str]]) -> None:
    summary_table = "\n".join(f"| {row['metric']} | {row['value']} | {row['interpretation']} |" for row in summary)
    REPORT_PATH.write_text(
        f"""# ALB_2012 Raw Core Feasibility Audit

Status: temp-only raw feasibility audit. This audit reads locally extracted ALB_2012 SPSS files, checks household merge coverage for core modules, and creates a review candidate in `temp/`. It does not write `data/harmonized_household.csv`, does not create final outcomes, and does not create climate-linkage inputs.

## Summary

| Metric | Value | Interpretation |
|---|---:|---|
{summary_table}

## Audit Rows

{markdown_rows(audit_rows, ['audit_domain', 'audit_item', 'source_file', 'row_count', 'distinct_key_count', 'base_rows_matched', 'audit_status'], 30)}

## Candidate Lineage

{markdown_rows(lineage, ['candidate_column', 'source_file', 'raw_variables', 'transformation', 'status', 'blocking_reason'], 30)}

## Interpretation

- ALB_2012 has a reviewable household base with total consumption, retro weights, roster demographics, health OOP/access proxies, and shock-module signals.
- The base frame has 6,671 household rows from `poverty.sav`.
- This is not a harmonized dataset: OOP units, recall periods, missing codes, skip patterns, survey design semantics, and access denominators are not verified.
- Climate linkage remains blocked because no raw interview month/date or GPS/coordinate field is identified, and current geography is coarse prefecture/region/urban only.
- All outputs stay in `temp/`, `result/`, and `report/`; `data/` remains untouched.

## Machine-Readable Outputs

- `temp/alb2012_household_core_candidate.csv`
- `temp/alb2012_raw_core_feasibility_audit.csv`
- `temp/alb2012_raw_core_lineage.csv`
- `result/alb2012_raw_core_feasibility_summary.csv`
""",
        encoding="utf-8",
    )


def main() -> None:
    ensure_dirs()
    candidate, audit_rows, lineage, summary = build_candidate_and_audit()
    candidate.to_csv(CANDIDATE_PATH, index=False, encoding="utf-8-sig")
    write_csv(AUDIT_PATH, audit_rows, AUDIT_COLUMNS)
    write_csv(LINEAGE_PATH, lineage, LINEAGE_COLUMNS)
    write_csv(SUMMARY_PATH, summary, SUMMARY_COLUMNS)
    write_report(audit_rows, lineage, summary)
    append_log(TEMP_DIR / "audit_log.md", f"Built ALB_2012 raw core feasibility audit rows={len(audit_rows)} decision={DECISION}.")
    print(f"ALB_2012 raw core feasibility audit rows={len(audit_rows)} decision={DECISION}.")


if __name__ == "__main__":
    main()
