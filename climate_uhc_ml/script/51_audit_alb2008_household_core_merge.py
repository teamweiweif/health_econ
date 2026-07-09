from __future__ import annotations

import math
import warnings
from pathlib import Path
from typing import Any

import pandas as pd

from common import REPORT_DIR, RESULT_DIR, TEMP_DIR, append_log, ensure_dirs, write_csv

try:
    import pyreadstat
except ImportError:  # pragma: no cover - environment audit reports this separately.
    pyreadstat = None


IDNO = "ALB_2008_LSMS_v01_M"
COUNTRY = "Albania"
SURVEY_NAME = "Living Standards Measurement Survey 2008"
WAVE = "2008"
RAW_ROOT = TEMP_DIR / "raw_extracted" / "lsms_2008_eng_a54110ab32b9" / "LSMS 2008_eng" / "Data_2008"

MERGE_AUDIT_PATH = TEMP_DIR / "alb2008_household_core_merge_audit.csv"
LINEAGE_PATH = TEMP_DIR / "alb2008_household_core_lineage.csv"
CANDIDATE_PATH = TEMP_DIR / "alb2008_household_core_candidate.csv"
SUMMARY_PATH = RESULT_DIR / "alb2008_household_core_candidate_summary.csv"
REPORT_PATH = REPORT_DIR / "alb2008_household_core_merge_audit.md"

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


def read_sav(file_name: str, usecols: list[str] | None = None) -> tuple[pd.DataFrame, Any]:
    if pyreadstat is None:
        raise RuntimeError("pyreadstat is not available")
    path = RAW_ROOT / file_name
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        return pyreadstat.read_sav(str(path), usecols=usecols, apply_value_formats=False)


def sav_columns(file_name: str) -> list[str]:
    _, meta = read_sav(file_name, None)
    return list(meta.column_names)


def existing_columns(file_name: str, requested: list[str]) -> list[str]:
    available = set(sav_columns(file_name))
    return [col for col in requested if col in available]


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


def compact_join(values: list[Any], limit: int = 30) -> str:
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


def build_candidate_and_audits() -> tuple[pd.DataFrame, list[dict[str, str]], list[dict[str, str]], list[dict[str, str]]]:
    poverty_cols = ["psu", "hh", "hhid", "totcons", "rfood", "rnfood", "urbrur", "tirana_o", "area", "stratum"]
    poverty, _ = read_sav("poverty.sav", poverty_cols)
    poverty = add_psu_hh_key(poverty, "psu", "hh")
    base_keys = set(poverty["psu_hh_key"])
    candidate = pd.DataFrame(
        {
            "country": COUNTRY,
            "survey_name": SURVEY_NAME,
            "wave": WAVE,
            "idno": IDNO,
            "survey_year": 2008,
            "hhid": poverty["hhid"].map(key_part),
            "psu": poverty["psu_key"],
            "hh": poverty["hh_key"],
            "psu_hh_key": poverty["psu_hh_key"],
            "total_consumption": poverty["totcons"],
            "per_capita_food_consumption": poverty["rfood"],
            "per_capita_nonfood_consumption": poverty["rnfood"],
            "urban_rural_code": poverty["urbrur"],
            "tirana_other_code": poverty["tirana_o"],
            "area_code": poverty["area"],
            "stratum": poverty["stratum"],
        }
    )

    audits = [key_audit("base_poverty_aggregate", "poverty.sav", poverty, "psu_hh_key", base_keys, allow_many_to_one=False)]

    filters, _ = read_sav("filters_and_single.sav", ["psu", "hh", "m17_q01", "m17_q02", "m17_q07"])
    filters = add_psu_hh_key(filters, "psu", "hh")
    audits.append(key_audit("filters_and_single", "filters_and_single.sav", filters, "psu_hh_key", base_keys, allow_many_to_one=False))
    candidate = candidate.merge(
        filters[["psu_hh_key", "m17_q01", "m17_q02", "m17_q07"]].rename(
            columns={
                "m17_q01": "agric_land_owned_candidate",
                "m17_q02": "will_cultivate_candidate",
                "m17_q07": "livestock_owned_candidate",
            }
        ),
        on="psu_hh_key",
        how="left",
    )

    weight, _ = read_sav("Weight_retro_2008.sav", ["psu", "hh", "Weight_retro"])
    weight = add_psu_hh_key(weight, "psu", "hh")
    audits.append(key_audit("retro_weight_household", "Weight_retro_2008.sav", weight, "psu_hh_key", base_keys, allow_many_to_one=False))
    candidate = candidate.merge(
        weight[["psu_hh_key", "Weight_retro"]].rename(columns={"Weight_retro": "household_weight"}),
        on="psu_hh_key",
        how="left",
    )

    roster_cols = ["psu", "hh", "id", "m1a_q02", "m1a_q03", "m1a_q5y"]
    roster, _ = read_sav("Modul_1A_household_roster.sav", roster_cols)
    roster = add_psu_hh_key(roster, "psu", "hh")
    audits.append(key_audit("person_roster", "Modul_1A_household_roster.sav", roster, "psu_hh_key", base_keys, allow_many_to_one=True))
    roster["age_years"] = pd.to_numeric(roster["m1a_q5y"], errors="coerce")
    roster["is_head"] = pd.to_numeric(roster["m1a_q03"], errors="coerce") == 1
    roster_group = roster.groupby("psu_hh_key", dropna=False).agg(
        household_size=("id", "count"),
        children_under5=("age_years", lambda s: int((s < 5).sum())),
        children_under15=("age_years", lambda s: int((s < 15).sum())),
        elderly_60plus=("age_years", lambda s: int((s >= 60).sum())),
        elderly_65plus=("age_years", lambda s: int((s >= 65).sum())),
    )
    heads = roster.loc[roster["is_head"], ["psu_hh_key", "m1a_q02", "age_years"]].drop_duplicates("psu_hh_key")
    roster_group = roster_group.merge(
        heads.rename(columns={"m1a_q02": "head_sex", "age_years": "head_age"}),
        left_index=True,
        right_on="psu_hh_key",
        how="left",
    ).set_index("psu_hh_key")
    candidate = candidate.merge(roster_group.reset_index(), on="psu_hh_key", how="left")

    healtha_cols = existing_columns(
        "Modul_9A_health.sav",
        ["psu", "hh", "id", "m9a_q01", "m9a_q07", "m9a_q82"] + FOUR_WEEK_OOP + TWELVE_MONTH_OOP,
    )
    healtha, _ = read_sav("Modul_9A_health.sav", healtha_cols)
    healtha = add_psu_hh_key(healtha, "psu", "hh")
    audits.append(key_audit("person_health_a", "Modul_9A_health.sav", healtha, "psu_hh_key", base_keys, allow_many_to_one=True))
    healtha["person_has_chronic_or_disability"] = bool_from_codes(healtha["m9a_q01"], {1})
    healtha["person_had_sudden_illness_4w"] = bool_from_codes(healtha["m9a_q07"], {1})
    healtha["person_has_health_license"] = bool_from_codes(healtha["m9a_q82"], {1}) if "m9a_q82" in healtha.columns else False
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

    healthb_cols = ["psu", "hh", "m9b_q01", "m9b_q03", "m9b_q04", "m9b_q05", "m9b_q06", "m9b_q07", "m9b_q08"]
    healthb, _ = read_sav("Modul_9B_health.sav", healthb_cols)
    healthb = add_psu_hh_key(healthb, "psu", "hh")
    audits.append(key_audit("household_health_b", "Modul_9B_health.sav", healthb, "psu_hh_key", base_keys, allow_many_to_one=False))
    healthb["difficulty_pay_health"] = bool_from_codes(healthb["m9b_q01"], {1})
    healthb["delayed_help_any"] = pd.to_numeric(healthb["m9b_q03"], errors="coerce").fillna(0) > 0
    healthb["hospital_referral_not_gone_any"] = pd.to_numeric(healthb["m9b_q05"], errors="coerce").fillna(0) > 0
    healthb["delay_reason_cost"] = bool_from_codes(healthb["m9b_q04"], {2})
    healthb["delay_reason_distance"] = bool_from_codes(healthb["m9b_q04"], {3, 6})
    healthb["not_gone_reason_cost"] = bool_from_codes(healthb["m9b_q06"], {2})
    healthb["not_gone_reason_distance"] = bool_from_codes(healthb["m9b_q06"], {3, 6})
    healthb["refused_health_services_any"] = bool_from_codes(healthb["m9b_q07"], {1})
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
            ]
        ],
        on="psu_hh_key",
        how="left",
    )

    shock, _ = read_sav("Modul_6E_migration_e.sav", ["psu", "hh", "m6e_q00", "m6e_q01"])
    shock = add_psu_hh_key(shock, "psu", "hh")
    audits.append(key_audit("shock_module", "Modul_6E_migration_e.sav", shock, "psu_hh_key", base_keys, allow_many_to_one=True))
    shock["shock_yes"] = bool_from_codes(shock["m6e_q01"], {1})
    shock["shock_flood_damage"] = bool_from_codes(shock["m6e_q00"], {8}) & shock["shock_yes"]
    shock["shock_serious_illness"] = bool_from_codes(shock["m6e_q00"], {4}) & shock["shock_yes"]
    shock_group = shock.groupby("psu_hh_key", dropna=False).agg(
        reported_flood_damage_shock=("shock_flood_damage", "max"),
        reported_serious_illness_shock=("shock_serious_illness", "max"),
    )
    candidate = candidate.merge(shock_group.reset_index(), on="psu_hh_key", how="left")

    bool_cols = [
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
        "reported_flood_damage_shock",
        "reported_serious_illness_shock",
    ]
    for col in bool_cols:
        if col in candidate.columns:
            candidate[col] = candidate[col].fillna(False).astype(int)

    candidate["geolocation_quality"] = "coarse_area_stratum_no_gps"
    candidate.loc[candidate["area_code"].isna() & candidate["stratum"].isna(), "geolocation_quality"] = "missing_geography"
    candidate["survey_month"] = ""
    candidate["interview_date"] = ""
    candidate["core_candidate_status"] = "temp_candidate_not_analysis_ready"
    candidate["blocking_reason"] = "survey timing, climate geography, OOP aggregation/recall, access skip patterns, and cross-wave comparability remain unresolved"
    candidate = candidate.drop(columns=["psu_hh_key"])

    lineage_rows = [
        {
            "candidate_column": "total_consumption",
            "source_file": "poverty.sav",
            "raw_variables": "totcons",
            "transformation": "copy survey aggregate",
            "status": "candidate_unit_period_review_required",
            "blocking_reason": "unit and period require documentation review",
        },
        {
            "candidate_column": "household_weight",
            "source_file": "Weight_retro_2008.sav",
            "raw_variables": "Weight_retro",
            "transformation": "copy household-level retrospective weight by PSU-household key",
            "status": "candidate_design_review_required",
            "blocking_reason": "survey design use and population require documentation review",
        },
        {
            "candidate_column": "oop_4w_sum_unreviewed",
            "source_file": "Modul_9A_health.sav",
            "raw_variables": compact_join([col for col in FOUR_WEEK_OOP if col in healtha.columns], 40),
            "transformation": "person-level payment item sum by household",
            "status": "candidate_aggregation_review_required",
            "blocking_reason": "care-context, skip-pattern, missing-code, gift, transport, and recall comparability require review",
        },
        {
            "candidate_column": "oop_12m_sum_unreviewed",
            "source_file": "Modul_9A_health.sav",
            "raw_variables": compact_join([col for col in TWELVE_MONTH_OOP if col in healtha.columns], 40),
            "transformation": "person-level annual payment item sum by household",
            "status": "candidate_aggregation_review_required",
            "blocking_reason": "annual inpatient/dentist payment items must not be pooled with four-week items without a documented rule",
        },
        {
            "candidate_column": "area_code;stratum;urban_rural_code",
            "source_file": "poverty.sav",
            "raw_variables": "area;stratum;urbrur",
            "transformation": "copy coarse survey geography/design fields",
            "status": "blocked_coarse_geography_no_gps",
            "blocking_reason": "coarse area/stratum fields are not verified admin/GPS climate-linkage geography",
        },
        {
            "candidate_column": "survey_month;interview_date",
            "source_file": "",
            "raw_variables": "",
            "transformation": "not constructed",
            "status": "blocked_missing_timing",
            "blocking_reason": "no interview month/date variable has been verified",
        },
    ]
    lineage = [{"country": COUNTRY, "survey_name": SURVEY_NAME, "wave": WAVE, "idno": IDNO, **row} for row in lineage_rows]
    summary = build_summary_rows(candidate, audits)
    return candidate, audits, lineage, summary


def build_summary_rows(candidate: pd.DataFrame, audits: list[dict[str, str]]) -> list[dict[str, str]]:
    rows = [
        {"metric": "alb2008_household_core_candidate_rows", "value": str(len(candidate)), "interpretation": "Rows in the temp-only household core candidate table."},
        {"metric": "alb2008_household_core_recipe_ready_rows", "value": "0", "interpretation": "This audit never promotes analysis-ready harmonization rows."},
        {"metric": "alb2008_households_with_total_consumption", "value": str(int(candidate["total_consumption"].notna().sum())), "interpretation": "Base households with poverty.sav total consumption."},
        {"metric": "alb2008_households_with_household_weight", "value": str(int(candidate["household_weight"].notna().sum())), "interpretation": "Base households with candidate household weight."},
        {"metric": "alb2008_households_with_household_size", "value": str(int(candidate["household_size"].notna().sum())), "interpretation": "Base households with roster-derived household size."},
        {"metric": "alb2008_households_with_oop_4w_positive", "value": str(int((candidate["oop_4w_sum_unreviewed"] > 0).sum())), "interpretation": "Households with positive unreviewed four-week OOP item sum."},
        {"metric": "alb2008_households_with_oop_12m_positive", "value": str(int((candidate["oop_12m_sum_unreviewed"] > 0).sum())), "interpretation": "Households with positive unreviewed twelve-month OOP item sum."},
        {"metric": "alb2008_households_with_coarse_area", "value": str(int(candidate["area_code"].notna().sum())), "interpretation": "Base households with coarse area code from poverty.sav."},
        {"metric": "alb2008_households_with_survey_month", "value": "0", "interpretation": "No interview month variable has been verified."},
        {"metric": "alb2008_merge_modules_audited", "value": str(len(audits)), "interpretation": "Raw modules assessed for merge key coverage."},
        {"metric": "alb2008_merge_modules_complete_base_coverage", "value": str(sum(1 for row in audits if row["merge_status"] == "base_coverage_complete_merge_review_required")), "interpretation": "Modules whose distinct keys cover all base households."},
        {"metric": "alb2008_merge_modules_partial_base_coverage", "value": str(sum(1 for row in audits if row["merge_status"] == "partial_base_coverage_review_required")), "interpretation": "Modules covering only part of the base households."},
        {"metric": "alb2008_household_core_current_decision", "value": "temp_candidate_not_analysis_ready", "interpretation": "ALB_2008 core candidate is useful for review but remains blocked from data/."},
    ]
    for column in ["total_consumption", "household_weight", "household_size", "oop_4w_sum_unreviewed", "oop_12m_sum_unreviewed"]:
        stats = summarize_numeric(candidate[column])
        rows.append({"metric": f"alb2008_{column}_nonmissing", "value": stats["nonmissing"], "interpretation": f"Nonmissing {column} rows."})
        rows.append({"metric": f"alb2008_{column}_min", "value": stats["min"], "interpretation": f"Observed minimum for {column}."})
        rows.append({"metric": f"alb2008_{column}_max", "value": stats["max"], "interpretation": f"Observed maximum for {column}."})
        rows.append({"metric": f"alb2008_{column}_mean", "value": stats["mean"], "interpretation": f"Observed mean for {column}."})
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
        f"""# ALB_2008 Household Core Merge Audit

Status: temp-only candidate build. This audit tests whether ALB_2008 raw household/person modules can be merged into a reviewable household core. It does not write `data/harmonized_household.csv`, does not promote a harmonization recipe, and does not construct final outcomes.

## Summary

| Metric | Value | Interpretation |
|---|---:|---|
{summary_table}

## Merge Key Audit

{markdown_rows(audits, ['module', 'source_file', 'merge_key', 'row_count', 'distinct_key_count', 'base_rows_matched', 'base_match_rate', 'merge_status'], 20)}

## Candidate Lineage

{markdown_rows(lineage, ['candidate_column', 'source_file', 'raw_variables', 'transformation', 'status', 'blocking_reason'], 20)}

## Interpretation

- A temp household core can be assembled for review from the ALB_2008 raw files, with base rows from `poverty.sav`.
- Consumption, weights, roster demographics, health module OOP items, health access proxies, and shock variables have meaningful merge coverage.
- The OOP variables are deliberately named `*_unreviewed`; they mix care contexts and recall periods and are not final outcome variables.
- `area`, `stratum`, and `urbrur` are coarse survey geography/design fields, not verified admin/GPS climate-linkage locations.
- No interview month/date has been verified, so reduced-form climate exposure timing remains blocked.
- The candidate table stays in `temp/`; it is not an analysis-ready `data/` deliverable.

## Machine-Readable Outputs

- `temp/alb2008_household_core_candidate.csv`
- `temp/alb2008_household_core_merge_audit.csv`
- `temp/alb2008_household_core_lineage.csv`
- `result/alb2008_household_core_candidate_summary.csv`
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
    append_log(TEMP_DIR / "audit_log.md", f"Built ALB_2008 household core temp candidate rows={len(candidate)}.")
    print(f"ALB_2008 household core temp candidate rows={len(candidate)}.")


if __name__ == "__main__":
    main()
