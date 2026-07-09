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


IDNO = "ALB_2002_LSMS_v01_M"
COUNTRY = "Albania"
SURVEY_NAME = "Living Standards Measurement Survey 2002"
WAVE = "2002"
RAW_ROOT = TEMP_DIR / "raw_extracted" / "lsms2002en_4dbf0b087520" / "lsms2002en" / "Data_2002"

MERGE_AUDIT_PATH = TEMP_DIR / "alb2002_household_core_merge_audit.csv"
LINEAGE_PATH = TEMP_DIR / "alb2002_household_core_lineage.csv"
CANDIDATE_PATH = TEMP_DIR / "alb2002_household_core_candidate.csv"
SUMMARY_PATH = RESULT_DIR / "alb2002_household_core_candidate_summary.csv"
REPORT_PATH = REPORT_DIR / "alb2002_household_core_merge_audit.md"

MERGE_AUDIT_COLUMNS = [
    "country",
    "survey_name",
    "wave",
    "idno",
    "module",
    "source_file",
    "merge_key",
    "row_count",
    "complete_key_rows",
    "distinct_key_count",
    "duplicate_key_rows",
    "base_rows",
    "base_rows_matched",
    "base_match_rate",
    "module_rows_unmatched_to_base",
    "merge_status",
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

FOUR_WEEK_OOP = [
    "m5a_q14",
    "m5a_q18",
    "m5a_q20",
    "m5a_q21",
    "m5a_q24",
    "m5a_q27",
    "m5a_q28",
    "m5a_q29",
    "m5a_q32",
    "m5a_q35",
    "m5a_q36",
    "m5a_q37",
    "m5a_q40",
    "m5a_q43",
    "m5a_q44",
    "m5a_q45",
    "m5a_q47",
]
TWELVE_MONTH_OOP = [
    "m5a_q53",
    "m5a_q56",
    "m5a_q57",
    "m5a_q58",
    "m5a_q61",
    "m5a_q64",
    "m5a_q65",
    "m5a_q66",
]


def read_sav(file_name: str, usecols: list[str] | None = None) -> tuple[pd.DataFrame, Any]:
    if pyreadstat is None:
        raise RuntimeError("pyreadstat is not available")
    path = RAW_ROOT / file_name
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        return pyreadstat.read_sav(str(path), usecols=usecols, apply_value_formats=False)


def format_scalar(value: Any) -> str:
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


def add_psu_hh_key(df: pd.DataFrame, psu: str, hh: str) -> pd.DataFrame:
    out = df.copy()
    out["psu_key"] = out[psu].map(key_part)
    out["hh_key"] = out[hh].map(key_part)
    out["psu_hh_key"] = out["psu_key"] + "-" + out["hh_key"]
    out.loc[(out["psu_key"] == "") | (out["hh_key"] == ""), "psu_hh_key"] = ""
    return out


def key_audit(
    module: str,
    file_name: str,
    df: pd.DataFrame,
    key: str,
    base_keys: set[str],
    allow_many_to_one: bool,
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
        reason = "module has no complete merge keys"
    elif duplicates > 0 and not allow_many_to_one:
        status = "blocked_duplicate_household_keys"
        reason = "household-level module repeats the merge key"
    elif matched == 0:
        status = "blocked_no_base_matches"
        reason = "module keys do not match base household keys"
    elif matched < len(base_keys):
        status = "partial_base_coverage_review_required"
        reason = "module covers only a subset of base households"
    else:
        status = "base_coverage_complete_merge_review_required"
        reason = "base household keys are covered, but variable semantics still require review"
    return {
        "country": COUNTRY,
        "survey_name": SURVEY_NAME,
        "wave": WAVE,
        "idno": IDNO,
        "module": module,
        "source_file": file_name,
        "merge_key": key,
        "row_count": str(len(df)),
        "complete_key_rows": str(complete_count),
        "distinct_key_count": str(distinct),
        "duplicate_key_rows": str(duplicates),
        "base_rows": str(len(base_keys)),
        "base_rows_matched": str(matched),
        "base_match_rate": f"{matched / len(base_keys):.6f}" if base_keys else "0",
        "module_rows_unmatched_to_base": str(unmatched_module_rows),
        "merge_status": status,
        "blocking_reason": reason,
    }


def bool_from_codes(series: pd.Series, true_codes: set[int]) -> pd.Series:
    numeric = pd.to_numeric(series, errors="coerce")
    return numeric.isin(true_codes)


def row_sum(frame: pd.DataFrame, columns: list[str]) -> pd.Series:
    present = [col for col in columns if col in frame.columns]
    if not present:
        return pd.Series(0.0, index=frame.index)
    return frame[present].apply(pd.to_numeric, errors="coerce").fillna(0).sum(axis=1)


def summarize_numeric(series: pd.Series) -> dict[str, str]:
    numeric = pd.to_numeric(series, errors="coerce")
    nonmissing = numeric.dropna()
    return {
        "nonmissing": str(len(nonmissing)),
        "distinct": str(nonmissing.nunique(dropna=True)),
        "min": format_scalar(nonmissing.min()) if len(nonmissing) else "",
        "max": format_scalar(nonmissing.max()) if len(nonmissing) else "",
        "mean": f"{nonmissing.mean():.6g}" if len(nonmissing) else "",
    }


def date_from_parts(year: pd.Series, month: pd.Series, day: pd.Series) -> pd.Series:
    frame = pd.DataFrame(
        {
            "year": pd.to_numeric(year, errors="coerce"),
            "month": pd.to_numeric(month, errors="coerce"),
            "day": pd.to_numeric(day, errors="coerce"),
        }
    )
    valid = frame["year"].between(1900, 2100) & frame["month"].between(1, 12) & frame["day"].between(1, 31)
    out = pd.Series("", index=frame.index, dtype=object)
    out.loc[valid] = pd.to_datetime(frame.loc[valid].astype(int), errors="coerce").dt.strftime("%Y-%m-%d").fillna("")
    return out


def build_candidate_and_audits() -> tuple[pd.DataFrame, list[dict[str, str]], list[dict[str, str]], list[dict[str, str]]]:
    poverty, _ = read_sav("Poverty_2002.sav", ["psu", "hh", "hhid", "totcons", "rcons", "rfood", "rnfood", "rutil"])
    poverty = add_psu_hh_key(poverty, "psu", "hh")
    base_keys = set(poverty["psu_hh_key"])
    candidate = pd.DataFrame(
        {
            "country": COUNTRY,
            "survey_name": SURVEY_NAME,
            "wave": WAVE,
            "idno": IDNO,
            "survey_year": 2002,
            "hhid": poverty["hhid"].map(key_part),
            "psu": poverty["psu_key"],
            "hh": poverty["hh_key"],
            "psu_hh_key": poverty["psu_hh_key"],
            "total_consumption": poverty["totcons"],
            "real_consumption": poverty["rcons"],
            "per_capita_food_consumption": poverty["rfood"],
            "per_capita_nonfood_consumption": poverty["rnfood"],
            "utility_consumption": poverty["rutil"],
        }
    )
    audits = [key_audit("base_poverty_aggregate", "Poverty_2002.sav", poverty, "psu_hh_key", base_keys, allow_many_to_one=False)]

    weights, _ = read_sav("weights_1.sav", ["psu", "hh", "hhid", "distr", "distr_n", "stratum", "ur", "hhsize", "weight"])
    weights = add_psu_hh_key(weights, "psu", "hh")
    audits.append(key_audit("household_weights", "weights_1.sav", weights, "psu_hh_key", base_keys, allow_many_to_one=False))
    candidate = candidate.merge(
        weights[["psu_hh_key", "distr", "distr_n", "stratum", "ur", "hhsize", "weight"]].rename(
            columns={
                "distr": "district_code_weight",
                "distr_n": "district_name_weight",
                "ur": "urban_rural_code_weight",
                "hhsize": "household_size_weight_file",
                "weight": "household_weight",
            }
        ),
        on="psu_hh_key",
        how="left",
    )

    ident_cols = ["psu", "hh", "hhid", "m0_q1a", "m0_q1b", "m0_q02", "m0_q08d", "m0_q08m", "m0_q08y", "m0_q08d2", "m0_q08m2", "m0_q08y2", "m0_q09", "m0_ur"]
    ident, _ = read_sav("Modul_0_identification.sav", ident_cols)
    ident = add_psu_hh_key(ident, "psu", "hh")
    audits.append(key_audit("identification_timing_geography", "Modul_0_identification.sav", ident, "psu_hh_key", base_keys, allow_many_to_one=False))
    ident["interview_date_primary"] = date_from_parts(ident["m0_q08y"], ident["m0_q08m"], ident["m0_q08d"])
    ident["interview_date_secondary"] = date_from_parts(ident["m0_q08y2"], ident["m0_q08m2"], ident["m0_q08d2"])
    candidate = candidate.merge(
        ident[
            [
                "psu_hh_key",
                "m0_q1a",
                "m0_q1b",
                "m0_q02",
                "m0_q08d",
                "m0_q08m",
                "m0_q08y",
                "m0_q08d2",
                "m0_q08m2",
                "m0_q08y2",
                "m0_q09",
                "m0_ur",
                "interview_date_primary",
                "interview_date_secondary",
            ]
        ].rename(
            columns={
                "m0_q1a": "district_code_identification",
                "m0_q1b": "district_name_identification",
                "m0_q02": "municipality_commune_code",
                "m0_q08d": "interview_day",
                "m0_q08m": "survey_month",
                "m0_q08y": "interview_year_raw",
                "m0_q08d2": "interview_day_secondary",
                "m0_q08m2": "survey_month_secondary",
                "m0_q08y2": "interview_year_secondary",
                "m0_q09": "enumerator_area",
                "m0_ur": "urban_rural_code_identification",
            }
        ),
        on="psu_hh_key",
        how="left",
    )
    candidate["interview_date"] = candidate["interview_date_primary"]
    candidate.loc[candidate["interview_date"].astype(str).str.len() == 0, "interview_date"] = candidate["interview_date_secondary"]
    candidate["interview_timing_quality"] = "raw_identification_day_month_year_present"
    candidate.loc[candidate["interview_date"].astype(str).str.len() == 0, "interview_timing_quality"] = "missing_interview_date"

    filters, _ = read_sav("filters.sav", ["PSU", "HH", "HHID", "MCA1_Q00", "MCA1_Q01", "MCE_Q01", "MDA_Q01"])
    filters = add_psu_hh_key(filters, "PSU", "HH")
    audits.append(key_audit("filters_household_screeners", "filters.sav", filters, "psu_hh_key", base_keys, allow_many_to_one=False))
    candidate = candidate.merge(
        filters[["psu_hh_key", "MCA1_Q00", "MCA1_Q01", "MCE_Q01", "MDA_Q01"]].rename(
            columns={
                "MCA1_Q00": "agric_livelihood_any_candidate",
                "MCA1_Q01": "farmed_last_crop_season_candidate",
                "MCE_Q01": "livestock_owned_candidate",
                "MDA_Q01": "nonag_enterprise_candidate",
            }
        ),
        on="psu_hh_key",
        how="left",
    )

    roster, _ = read_sav("Modul_1_hhroster.sav", ["psu", "hh", "m1_q00", "m1_q02", "m1_q03", "m1_q05y", "hhid"])
    roster = add_psu_hh_key(roster, "psu", "hh")
    audits.append(key_audit("person_roster", "Modul_1_hhroster.sav", roster, "psu_hh_key", base_keys, allow_many_to_one=True))
    roster["age_years"] = pd.to_numeric(roster["m1_q05y"], errors="coerce")
    roster["is_head"] = pd.to_numeric(roster["m1_q03"], errors="coerce") == 1
    roster_group = roster.groupby("psu_hh_key", dropna=False).agg(
        household_size=("m1_q00", "count"),
        children_under5=("age_years", lambda s: int((s < 5).sum())),
        children_under15=("age_years", lambda s: int((s < 15).sum())),
        elderly_60plus=("age_years", lambda s: int((s >= 60).sum())),
        elderly_65plus=("age_years", lambda s: int((s >= 65).sum())),
    )
    heads = roster.loc[roster["is_head"], ["psu_hh_key", "m1_q02", "age_years"]].drop_duplicates("psu_hh_key")
    roster_group = roster_group.merge(
        heads.rename(columns={"m1_q02": "head_sex", "age_years": "head_age"}),
        left_index=True,
        right_on="psu_hh_key",
        how="left",
    ).set_index("psu_hh_key")
    candidate = candidate.merge(roster_group.reset_index(), on="psu_hh_key", how="left")

    healtha_cols = ["psu", "hh", "hhid", "m5a_q00", "m5a_q01", "m5a_q07", "m5a_q67"] + FOUR_WEEK_OOP + TWELVE_MONTH_OOP
    healtha, _ = read_sav("Modul_5A_Health.sav", healtha_cols)
    healtha = add_psu_hh_key(healtha, "psu", "hh")
    audits.append(key_audit("person_health_a", "Modul_5A_Health.sav", healtha, "psu_hh_key", base_keys, allow_many_to_one=True))
    healtha["person_has_chronic_or_disability"] = bool_from_codes(healtha["m5a_q01"], {1})
    healtha["person_had_sudden_illness_4w"] = bool_from_codes(healtha["m5a_q07"], {1})
    healtha["person_has_health_license"] = bool_from_codes(healtha["m5a_q67"], {1})
    healtha["oop_4w_person_sum"] = row_sum(healtha, FOUR_WEEK_OOP)
    healtha["oop_12m_person_sum"] = row_sum(healtha, TWELVE_MONTH_OOP)
    healtha["oop_4w_person_any"] = healtha["oop_4w_person_sum"] > 0
    healtha["oop_12m_person_any"] = healtha["oop_12m_person_sum"] > 0
    healtha_group = healtha.groupby("psu_hh_key", dropna=False).agg(
        illness_or_disability_any=("person_has_chronic_or_disability", "max"),
        sudden_illness_4w_any=("person_had_sudden_illness_4w", "max"),
        health_license_any=("person_has_health_license", "max"),
        oop_4w_sum_unreviewed=("oop_4w_person_sum", "sum"),
        oop_12m_sum_unreviewed=("oop_12m_person_sum", "sum"),
        oop_4w_any_unreviewed=("oop_4w_person_any", "max"),
        oop_12m_any_unreviewed=("oop_12m_person_any", "max"),
    )
    candidate = candidate.merge(healtha_group.reset_index(), on="psu_hh_key", how="left")

    healthb_cols = ["psu", "hh", "hhid", "m5b_q01", "m5b_q02_", "m5b_q021", "m5b_q022", "m5b_q023", "m5b_q024", "m5b_q03", "m5b_q04", "m5b_q05", "m5b_q06", "m5b_q07", "m5b_q08", "m5b_q09", "m5b_q10"]
    healthb, _ = read_sav("Modul_5B_Health.sav", healthb_cols)
    healthb = add_psu_hh_key(healthb, "psu", "hh")
    audits.append(key_audit("household_health_b", "Modul_5B_Health.sav", healthb, "psu_hh_key", base_keys, allow_many_to_one=False))
    healthb["difficulty_pay_health"] = bool_from_codes(healthb["m5b_q01"], {1, 2})
    healthb["delayed_help_any"] = pd.to_numeric(healthb["m5b_q03"], errors="coerce").fillna(1) > 1
    healthb["hospital_referral_not_gone_any"] = pd.to_numeric(healthb["m5b_q05"], errors="coerce").fillna(1) > 1
    healthb["delay_reason_cost"] = bool_from_codes(healthb["m5b_q04"], {4})
    healthb["delay_reason_distance"] = bool_from_codes(healthb["m5b_q04"], {5})
    healthb["not_gone_reason_cost"] = bool_from_codes(healthb["m5b_q06"], {2})
    healthb["not_gone_reason_distance"] = bool_from_codes(healthb["m5b_q06"], {3, 6})
    healthb["refused_health_services_any"] = bool_from_codes(healthb["m5b_q07"], {1})
    healthb["refused_reason_cost"] = bool_from_codes(healthb["m5b_q08"], {1})
    healthb["refused_reason_distance"] = bool_from_codes(healthb["m5b_q08"], {2})
    money_raising_cols = ["m5b_q02_", "m5b_q021", "m5b_q022", "m5b_q023", "m5b_q024"]
    healthb["health_payment_money_raising_any_unreviewed"] = healthb[money_raising_cols].apply(pd.to_numeric, errors="coerce").fillna(0).eq(1).any(axis=1)
    healthb["medicine_discount_cost_barrier"] = bool_from_codes(healthb["m5b_q10"], {5})
    candidate = candidate.merge(
        healthb[
            [
                "psu_hh_key",
                "difficulty_pay_health",
                "delayed_help_any",
                "hospital_referral_not_gone_any",
                "delay_reason_cost",
                "delay_reason_distance",
                "not_gone_reason_cost",
                "not_gone_reason_distance",
                "refused_health_services_any",
                "refused_reason_cost",
                "refused_reason_distance",
                "health_payment_money_raising_any_unreviewed",
                "medicine_discount_cost_barrier",
            ]
        ],
        on="psu_hh_key",
        how="left",
    )

    bool_cols = [
        "agric_livelihood_any_candidate",
        "farmed_last_crop_season_candidate",
        "livestock_owned_candidate",
        "nonag_enterprise_candidate",
        "illness_or_disability_any",
        "sudden_illness_4w_any",
        "health_license_any",
        "oop_4w_any_unreviewed",
        "oop_12m_any_unreviewed",
        "difficulty_pay_health",
        "delayed_help_any",
        "hospital_referral_not_gone_any",
        "delay_reason_cost",
        "delay_reason_distance",
        "not_gone_reason_cost",
        "not_gone_reason_distance",
        "refused_health_services_any",
        "refused_reason_cost",
        "refused_reason_distance",
        "health_payment_money_raising_any_unreviewed",
        "medicine_discount_cost_barrier",
    ]
    for col in bool_cols:
        if col in candidate.columns:
            candidate[col] = candidate[col].fillna(False).astype(int)

    candidate["geolocation_quality"] = "district_admin_candidate_no_gps"
    candidate.loc[candidate["district_code_identification"].isna() & candidate["district_code_weight"].isna(), "geolocation_quality"] = "missing_geography"
    candidate["core_candidate_status"] = "temp_candidate_not_analysis_ready"
    candidate["blocking_reason"] = "OOP aggregation/recall, units, access skip patterns, district climate crosswalk, and cross-wave comparability remain unresolved"
    candidate = candidate.drop(columns=["psu_hh_key"])

    lineage_rows = [
        {
            "candidate_column": "total_consumption",
            "source_file": "Poverty_2002.sav",
            "raw_variables": "totcons",
            "transformation": "copy survey aggregate",
            "status": "candidate_unit_period_review_required",
            "blocking_reason": "unit and period require documentation review",
        },
        {
            "candidate_column": "household_weight",
            "source_file": "weights_1.sav",
            "raw_variables": "weight",
            "transformation": "copy household-level weight by PSU-household key",
            "status": "candidate_design_review_required",
            "blocking_reason": "survey design use and population require documentation review",
        },
        {
            "candidate_column": "survey_month;interview_date",
            "source_file": "Modul_0_identification.sav",
            "raw_variables": "m0_q08d;m0_q08m;m0_q08y;m0_q08d2;m0_q08m2;m0_q08y2",
            "transformation": "construct ISO date from raw interview day/month/year, primary then secondary fallback",
            "status": "candidate_timing_observed_requires_fieldwork_documentation",
            "blocking_reason": "raw interview date is observed but fieldwork calendar and comparability require documentation review before climate windows",
        },
        {
            "candidate_column": "district_code_identification;district_name_identification",
            "source_file": "Modul_0_identification.sav",
            "raw_variables": "m0_q1a;m0_q1b",
            "transformation": "copy district code/name candidate",
            "status": "candidate_admin_geography_requires_crosswalk",
            "blocking_reason": "district fields need official boundary/crosswalk and no GPS is available",
        },
        {
            "candidate_column": "oop_4w_sum_unreviewed",
            "source_file": "Modul_5A_Health.sav",
            "raw_variables": compact_join(FOUR_WEEK_OOP),
            "transformation": "person-level payment item sum by household",
            "status": "candidate_aggregation_review_required",
            "blocking_reason": "care-context, skip-pattern, missing-code, gift, transport, and recall comparability require review",
        },
        {
            "candidate_column": "oop_12m_sum_unreviewed",
            "source_file": "Modul_5A_Health.sav",
            "raw_variables": compact_join(TWELVE_MONTH_OOP),
            "transformation": "person-level annual hospital/dentist payment item sum by household",
            "status": "candidate_aggregation_review_required",
            "blocking_reason": "annual inpatient/dentist payment items must not be pooled with four-week items without a documented rule",
        },
        {
            "candidate_column": "difficulty_pay_health;delayed_help_any;cost/distance/refusal proxies",
            "source_file": "Modul_5B_Health.sav",
            "raw_variables": "m5b_q01;m5b_q03;m5b_q04;m5b_q05;m5b_q06;m5b_q07;m5b_q08;m5b_q10",
            "transformation": "derive household-level unreviewed access and affordability proxies from labelled response codes",
            "status": "candidate_skip_pattern_review_required",
            "blocking_reason": "access outcomes require skip-pattern and denominator validation before promotion",
        },
    ]
    lineage = [{"country": COUNTRY, "survey_name": SURVEY_NAME, "wave": WAVE, "idno": IDNO, **row} for row in lineage_rows]
    summary = build_summary_rows(candidate, audits)
    return candidate, audits, lineage, summary


def build_summary_rows(candidate: pd.DataFrame, audits: list[dict[str, str]]) -> list[dict[str, str]]:
    rows = [
        {"metric": "alb2002_household_core_candidate_rows", "value": str(len(candidate)), "interpretation": "Rows in the temp-only household core candidate table."},
        {"metric": "alb2002_household_core_recipe_ready_rows", "value": "0", "interpretation": "This audit never promotes analysis-ready harmonization rows."},
        {"metric": "alb2002_households_with_total_consumption", "value": str(int(candidate["total_consumption"].notna().sum())), "interpretation": "Base households with Poverty_2002.sav total consumption."},
        {"metric": "alb2002_households_with_household_weight", "value": str(int(candidate["household_weight"].notna().sum())), "interpretation": "Base households with candidate household weight."},
        {"metric": "alb2002_households_with_household_size", "value": str(int(candidate["household_size"].notna().sum())), "interpretation": "Base households with roster-derived household size."},
        {"metric": "alb2002_households_with_oop_4w_positive", "value": str(int((candidate["oop_4w_sum_unreviewed"] > 0).sum())), "interpretation": "Households with positive unreviewed four-week OOP item sum."},
        {"metric": "alb2002_households_with_oop_12m_positive", "value": str(int((candidate["oop_12m_sum_unreviewed"] > 0).sum())), "interpretation": "Households with positive unreviewed twelve-month OOP item sum."},
        {"metric": "alb2002_households_with_district_code", "value": str(int(candidate["district_code_identification"].notna().sum())), "interpretation": "Base households with district code from Modul_0_identification.sav."},
        {"metric": "alb2002_households_with_survey_month", "value": str(int(candidate["survey_month"].notna().sum())), "interpretation": "Base households with raw interview month."},
        {"metric": "alb2002_households_with_interview_date", "value": str(int(candidate["interview_date"].astype(str).str.len().gt(0).sum())), "interpretation": "Base households with constructed raw interview date."},
        {"metric": "alb2002_merge_modules_audited", "value": str(len(audits)), "interpretation": "Raw modules assessed for merge key coverage."},
        {"metric": "alb2002_merge_modules_complete_base_coverage", "value": str(sum(1 for row in audits if row["merge_status"] == "base_coverage_complete_merge_review_required")), "interpretation": "Modules whose distinct keys cover all base households."},
        {"metric": "alb2002_merge_modules_partial_base_coverage", "value": str(sum(1 for row in audits if row["merge_status"] == "partial_base_coverage_review_required")), "interpretation": "Modules covering only part of the base households."},
        {"metric": "alb2002_household_core_current_decision", "value": "temp_candidate_timing_geography_observed_outcome_semantics_pending", "interpretation": "ALB_2002 core candidate has observed timing/geography fields but remains blocked from data/."},
    ]
    for column in ["total_consumption", "household_weight", "household_size", "oop_4w_sum_unreviewed", "oop_12m_sum_unreviewed"]:
        stats = summarize_numeric(candidate[column])
        rows.append({"metric": f"alb2002_{column}_nonmissing", "value": stats["nonmissing"], "interpretation": f"Nonmissing {column} rows."})
        rows.append({"metric": f"alb2002_{column}_min", "value": stats["min"], "interpretation": f"Observed minimum for {column}."})
        rows.append({"metric": f"alb2002_{column}_max", "value": stats["max"], "interpretation": f"Observed maximum for {column}."})
        rows.append({"metric": f"alb2002_{column}_mean", "value": stats["mean"], "interpretation": f"Observed mean for {column}."})
    return rows


def markdown_rows(rows: list[dict[str, str]], columns: list[str], limit: int = 20) -> str:
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


def write_report(audits: list[dict[str, str]], lineage: list[dict[str, str]], summary: list[dict[str, str]]) -> None:
    summary_table = "\n".join(f"| {row['metric']} | {row['value']} | {row['interpretation']} |" for row in summary)
    REPORT_PATH.write_text(
        f"""# ALB_2002 Household Core Merge Audit

Status: temp-only candidate build. This audit tests whether ALB_2002 raw household/person modules can be merged into a reviewable household core. It does not write `data/harmonized_household.csv`, does not promote a harmonization recipe, and does not construct final outcomes.

## Summary

| Metric | Value | Interpretation |
|---|---:|---|
{summary_table}

## Merge Key Audit

{markdown_rows(audits, ['module', 'source_file', 'merge_key', 'row_count', 'distinct_key_count', 'base_rows_matched', 'base_match_rate', 'merge_status'], 20)}

## Candidate Lineage

{markdown_rows(lineage, ['candidate_column', 'source_file', 'raw_variables', 'transformation', 'status', 'blocking_reason'], 20)}

## Interpretation

- A temp household core can be assembled for review from the ALB_2002 raw files, with base rows from `Poverty_2002.sav`.
- Consumption, weights, household roster demographics, health module OOP items, health access proxies, district fields, and interview date/month fields have complete base merge coverage.
- The observed interview date/month fields are promising for future climate windows, but fieldwork documentation and cross-wave comparability still require review.
- District fields are candidate admin geography only; no GPS is available and a validated district boundary/crosswalk is still required before climate linkage.
- The OOP variables are deliberately named `*_unreviewed`; they mix care contexts and recall periods and are not final outcome variables.
- The candidate table stays in `temp/`; it is not an analysis-ready `data/` deliverable.

## Machine-Readable Outputs

- `temp/alb2002_household_core_candidate.csv`
- `temp/alb2002_household_core_merge_audit.csv`
- `temp/alb2002_household_core_lineage.csv`
- `result/alb2002_household_core_candidate_summary.csv`
""",
        encoding="utf-8",
    )


def main() -> None:
    ensure_dirs()
    candidate, audits, lineage, summary = build_candidate_and_audits()
    CANDIDATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    candidate.to_csv(CANDIDATE_PATH, index=False, encoding="utf-8-sig")
    write_csv(MERGE_AUDIT_PATH, audits, MERGE_AUDIT_COLUMNS)
    write_csv(LINEAGE_PATH, lineage, LINEAGE_COLUMNS)
    write_csv(SUMMARY_PATH, summary, SUMMARY_COLUMNS)
    write_report(audits, lineage, summary)
    append_log(TEMP_DIR / "audit_log.md", f"Built ALB_2002 household core temp candidate rows={len(candidate)}.")
    print(f"ALB_2002 household core temp candidate rows={len(candidate)}.")


if __name__ == "__main__":
    main()
