from __future__ import annotations

import os
import tempfile
from pathlib import Path, PurePosixPath
from typing import Any
from zipfile import ZipFile

import pandas as pd
import pyreadstat

from common import REPORT_DIR, RESULT_DIR, TEMP_DIR, append_log, ensure_dirs, write_csv


IDNO = "MWI_2004_IHS-II_v01_M"
COUNTRY = "Malawi"
WAVE = "2004-2005"
RAW_DIR = TEMP_DIR / "raw_downloads" / IDNO
ZIP_PATH = RAW_DIR / "MWI_2004_IHS-II_v01_M_Stata8.zip"

REQUIREMENT_EVIDENCE_PATH = TEMP_DIR / "mwi2004_raw_requirement_evidence.csv"
JOIN_EVIDENCE_PATH = TEMP_DIR / "mwi2004_raw_module_join_evidence.csv"
FINANCIAL_PROFILE_PATH = TEMP_DIR / "mwi2004_raw_financial_oop_profile.csv"
SUMMARY_PATH = RESULT_DIR / "mwi2004_raw_requirement_verification_summary.csv"
REPORT_PATH = REPORT_DIR / "mwi2004_raw_requirement_verification.md"
HANDOFF_PATH = RAW_DIR / "_MWI2004_RAW_REQUIREMENT_VERIFICATION.md"

REQUIREMENT_COLUMNS = [
    "country",
    "wave",
    "idno",
    "requirement",
    "raw_backed_evidence_status",
    "verification_decision",
    "source_members",
    "variables_checked",
    "evidence_summary",
    "remaining_manual_review",
    "data_write_gate_effect",
]

JOIN_COLUMNS = [
    "country",
    "wave",
    "idno",
    "evidence_type",
    "left_member",
    "right_member",
    "key_variables",
    "left_rows",
    "right_rows",
    "left_nonmissing_key_rows",
    "right_nonmissing_key_rows",
    "left_distinct_keys",
    "right_distinct_keys",
    "left_duplicate_key_rows",
    "right_duplicate_key_rows",
    "matched_left_distinct_keys",
    "unmatched_left_distinct_keys",
    "evidence_status",
    "notes",
]

FINANCIAL_COLUMNS = [
    "country",
    "wave",
    "idno",
    "metric",
    "source_member",
    "variables",
    "row_count",
    "nonmissing_count",
    "positive_count",
    "zero_count",
    "min",
    "p25",
    "median",
    "p75",
    "max",
    "mean",
    "evidence_status",
    "interpretation",
]

SUMMARY_COLUMNS = [
    "metric",
    "value",
    "interpretation",
]


REQUESTED_COLUMNS = {
    "ihs2_household.dta": [
        "case_id",
        "hhwght",
        "strata",
        "region",
        "dist",
        "ea",
        "ta",
        "type",
        "add",
        "idate",
        "V51",
        "hhsize",
        "rexpagg",
        "rexpfood",
        "rexpnfd",
        "rexp_cat06",
        "povline",
        "ultrapovline",
        "price_index",
    ],
    "ihs2_exp.dta": [
        "case_id",
        "hhwght",
        "strata",
        "region",
        "dist",
        "ea",
        "ta",
        "type",
        "add",
        "price_index",
        "exp_cat061",
        "exp_cat062",
        "exp_cat063",
        "rexp_cat061",
        "rexp_cat062",
        "rexp_cat063",
    ],
    "ihs2_pov.dta": [
        "case_id",
        "hhwght",
        "strata",
        "region",
        "dist",
        "ea",
        "ta",
        "type",
        "add",
        "V13",
        "hhsize",
        "rexpagg",
        "rexpfood",
        "rexpnfd",
        "rexp_cat06",
        "povline",
        "ultrapovline",
        "price_index",
    ],
    "ihs2_individ.dta": [
        "case_id",
        "memid",
        "age",
        "age_months",
        "b03",
        "b04",
        "dist",
        "ta",
        "ea",
        "strata",
    ],
    "sec_d.dta": [
        "case_id",
        "memid",
        "d04",
        "d07a",
        "d07b",
        "d12",
        "d13",
        "d14",
        "d15",
        "d16",
        "d17",
        "d18",
        "d19",
        "d20",
        "d21",
        "d26",
        "d27a",
        "d27b",
        "d36",
        "d37",
        "d38",
        "hhwght",
        "psu",
        "strata",
        "dist",
        "ta",
        "ea",
        "region",
        "type",
        "hhsize",
    ],
    "ihs2_ea_data.dta": [
        "dist",
        "ta",
        "ea",
        "access",
        "access2",
        "lz_name",
        "lz_abbrev",
        "lz_code",
    ],
}


def clean(value: Any) -> str:
    if value is None:
        return ""
    return " ".join(str(value).split())


def fmt_num(value: Any, digits: int = 6) -> str:
    if value is None or pd.isna(value):
        return ""
    try:
        return f"{float(value):.{digits}g}"
    except (TypeError, ValueError):
        return clean(value)


def markdown_table(rows: list[dict[str, Any]], columns: list[str], limit: int = 20) -> str:
    shown = rows[:limit]
    if not shown:
        return "_No rows._"
    header = "| " + " | ".join(columns) + " |"
    sep = "| " + " | ".join("---" for _ in columns) + " |"
    body = []
    for row in shown:
        body.append("| " + " | ".join(clean(row.get(col, "")).replace("|", "/") for col in columns) + " |")
    if len(rows) > limit:
        body.append("| " + " | ".join("..." for _ in columns) + " |")
    return "\n".join([header, sep, *body])


def zip_member_for_basename(zip_path: Path, basename: str) -> str:
    target = basename.lower()
    with ZipFile(zip_path) as zf:
        for name in zf.namelist():
            if PurePosixPath(name).name.lower() == target:
                return name
    raise FileNotFoundError(f"Could not find {basename} inside {zip_path}")


def read_dta_member(
    zip_path: Path,
    basename: str,
    requested_columns: list[str],
) -> tuple[pd.DataFrame, Any, list[str], list[str], str]:
    member_name = zip_member_for_basename(zip_path, basename)
    with ZipFile(zip_path) as zf:
        payload = zf.read(member_name)
    suffix = PurePosixPath(member_name).suffix or ".dta"
    fd, raw_name = tempfile.mkstemp(suffix=suffix)
    raw_path = Path(raw_name)
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(payload)
        _, meta = pyreadstat.read_dta(str(raw_path), metadataonly=True)
        available = list(getattr(meta, "column_names", []) or [])
        available_set = set(available)
        usecols = [col for col in requested_columns if col in available_set]
        missing = [col for col in requested_columns if col not in available_set]
        df, meta = pyreadstat.read_dta(str(raw_path), apply_value_formats=False, usecols=usecols)
        return df, meta, usecols, missing, member_name
    finally:
        raw_path.unlink(missing_ok=True)


def nonmissing_key_frame(df: pd.DataFrame, keys: list[str]) -> pd.DataFrame:
    if not all(key in df.columns for key in keys):
        return pd.DataFrame(columns=keys)
    return df[keys].dropna()


def distinct_key_count(df: pd.DataFrame, keys: list[str]) -> int:
    key_df = nonmissing_key_frame(df, keys)
    if key_df.empty:
        return 0
    return int(key_df.drop_duplicates().shape[0])


def duplicate_key_rows(df: pd.DataFrame, keys: list[str]) -> int:
    key_df = nonmissing_key_frame(df, keys)
    if key_df.empty:
        return 0
    return int(len(key_df) - key_df.drop_duplicates().shape[0])


def key_evidence_row(
    frames: dict[str, pd.DataFrame],
    left_member: str,
    keys: list[str],
    evidence_type: str,
    notes: str,
) -> dict[str, str]:
    df = frames[left_member]
    nonmissing = nonmissing_key_frame(df, keys)
    distinct = distinct_key_count(df, keys)
    dupes = duplicate_key_rows(df, keys)
    status = "unique_at_expected_level" if len(nonmissing) == len(df) and dupes == 0 else "not_unique_or_missing_keys"
    return {
        "country": COUNTRY,
        "wave": WAVE,
        "idno": IDNO,
        "evidence_type": evidence_type,
        "left_member": left_member,
        "right_member": "",
        "key_variables": ";".join(keys),
        "left_rows": str(len(df)),
        "right_rows": "",
        "left_nonmissing_key_rows": str(len(nonmissing)),
        "right_nonmissing_key_rows": "",
        "left_distinct_keys": str(distinct),
        "right_distinct_keys": "",
        "left_duplicate_key_rows": str(dupes),
        "right_duplicate_key_rows": "",
        "matched_left_distinct_keys": "",
        "unmatched_left_distinct_keys": "",
        "evidence_status": status,
        "notes": notes,
    }


def join_evidence_row(
    frames: dict[str, pd.DataFrame],
    left_member: str,
    right_member: str,
    keys: list[str],
    evidence_type: str,
    notes: str,
) -> dict[str, str]:
    left = frames[left_member]
    right = frames[right_member]
    left_keys = nonmissing_key_frame(left, keys).drop_duplicates()
    right_keys = nonmissing_key_frame(right, keys).drop_duplicates()
    if left_keys.empty or right_keys.empty:
        matched = 0
    else:
        matched = int(left_keys.merge(right_keys, on=keys, how="inner").shape[0])
    unmatched = int(max(len(left_keys) - matched, 0))
    status = "all_left_distinct_keys_matched" if len(left_keys) > 0 and unmatched == 0 else "unmatched_keys_require_review"
    return {
        "country": COUNTRY,
        "wave": WAVE,
        "idno": IDNO,
        "evidence_type": evidence_type,
        "left_member": left_member,
        "right_member": right_member,
        "key_variables": ";".join(keys),
        "left_rows": str(len(left)),
        "right_rows": str(len(right)),
        "left_nonmissing_key_rows": str(len(nonmissing_key_frame(left, keys))),
        "right_nonmissing_key_rows": str(len(nonmissing_key_frame(right, keys))),
        "left_distinct_keys": str(len(left_keys)),
        "right_distinct_keys": str(len(right_keys)),
        "left_duplicate_key_rows": str(duplicate_key_rows(left, keys)),
        "right_duplicate_key_rows": str(duplicate_key_rows(right, keys)),
        "matched_left_distinct_keys": str(matched),
        "unmatched_left_distinct_keys": str(unmatched),
        "evidence_status": status,
        "notes": notes,
    }


def numeric_profile(
    df: pd.DataFrame,
    source_member: str,
    variables: list[str],
    metric: str,
    interpretation: str,
    evidence_status: str = "raw_numeric_profile_available",
) -> dict[str, str]:
    present = [var for var in variables if var in df.columns]
    if not present:
        return {
            "country": COUNTRY,
            "wave": WAVE,
            "idno": IDNO,
            "metric": metric,
            "source_member": source_member,
            "variables": ";".join(variables),
            "row_count": str(len(df)),
            "evidence_status": "missing_requested_variables",
            "interpretation": interpretation,
        }
    series = pd.to_numeric(df[present[0]], errors="coerce")
    if len(present) > 1:
        series = pd.DataFrame({var: pd.to_numeric(df[var], errors="coerce") for var in present}).sum(axis=1, min_count=1)
    nonmissing = series.dropna()
    positive_count = int((nonmissing > 0).sum())
    zero_count = int((nonmissing == 0).sum())
    return {
        "country": COUNTRY,
        "wave": WAVE,
        "idno": IDNO,
        "metric": metric,
        "source_member": source_member,
        "variables": ";".join(present),
        "row_count": str(len(df)),
        "nonmissing_count": str(len(nonmissing)),
        "positive_count": str(positive_count),
        "zero_count": str(zero_count),
        "min": fmt_num(nonmissing.min() if len(nonmissing) else None),
        "p25": fmt_num(nonmissing.quantile(0.25) if len(nonmissing) else None),
        "median": fmt_num(nonmissing.median() if len(nonmissing) else None),
        "p75": fmt_num(nonmissing.quantile(0.75) if len(nonmissing) else None),
        "max": fmt_num(nonmissing.max() if len(nonmissing) else None),
        "mean": fmt_num(nonmissing.mean() if len(nonmissing) else None),
        "evidence_status": evidence_status,
        "interpretation": interpretation,
    }


def label_for(meta: Any, variable: str, value: Any) -> str:
    value_labels = getattr(meta, "variable_value_labels", {}) or {}
    labels = value_labels.get(variable, {})
    if not isinstance(labels, dict):
        return ""
    if value in labels:
        return clean(labels[value])
    try:
        as_float = float(value)
    except (TypeError, ValueError):
        return ""
    for key, label in labels.items():
        try:
            if float(key) == as_float:
                return clean(label)
        except (TypeError, ValueError):
            continue
    return ""


def top_values(df: pd.DataFrame, meta: Any, variable: str, limit: int = 6) -> str:
    if variable not in df.columns:
        return ""
    counts = df[variable].dropna().value_counts().head(limit)
    parts = []
    for value, count in counts.items():
        label = label_for(meta, variable, value)
        text = fmt_num(value)
        if label:
            text = f"{text}={label}"
        parts.append(f"{text} ({int(count)})")
    return "; ".join(parts)


def date_bounds(series: pd.Series) -> tuple[str, str, str]:
    nonmissing = series.dropna()
    if nonmissing.empty:
        return "", "", "no_nonmissing_dates"
    if pd.api.types.is_datetime64_any_dtype(nonmissing):
        return nonmissing.min().date().isoformat(), nonmissing.max().date().isoformat(), "datetime_values"
    numeric = pd.to_numeric(nonmissing, errors="coerce").dropna()
    if numeric.empty:
        return clean(nonmissing.min()), clean(nonmissing.max()), "non_numeric_non_datetime_values"
    converted = pd.to_datetime(numeric, unit="D", origin="1960-01-01", errors="coerce").dropna()
    if converted.empty:
        return fmt_num(numeric.min()), fmt_num(numeric.max()), "numeric_values_unconverted"
    return converted.min().date().isoformat(), converted.max().date().isoformat(), "stata_days_since_1960"


def member_label(meta_by_member: dict[str, Any], member: str, variable: str) -> str:
    meta = meta_by_member.get(member)
    if not meta:
        return ""
    labels = dict(zip(getattr(meta, "column_names", []) or [], getattr(meta, "column_labels", []) or []))
    return clean(labels.get(variable, ""))


def build_financial_rows(frames: dict[str, pd.DataFrame]) -> list[dict[str, str]]:
    rows = [
        numeric_profile(
            frames["ihs2_pov.dta"],
            "ihs2_pov.dta",
            ["rexpagg"],
            "total_annual_household_expenditure_real",
            "Candidate CHE denominator: survey-team total annual household expenditure, real local currency.",
        ),
        numeric_profile(
            frames["ihs2_pov.dta"],
            "ihs2_pov.dta",
            ["rexp_cat06"],
            "health_oop_annual_household_expenditure_real",
            "Candidate annual OOP health aggregate from poverty/consumption file.",
        ),
        numeric_profile(
            frames["ihs2_exp.dta"],
            "ihs2_exp.dta",
            ["rexp_cat061", "rexp_cat062", "rexp_cat063"],
            "health_oop_real_component_sum",
            "Sum of real annual health drugs, outpatient, and hospitalization expenditure components.",
        ),
        numeric_profile(
            frames["ihs2_pov.dta"],
            "ihs2_pov.dta",
            ["povline"],
            "poverty_line_local_currency_per_person_year",
            "Survey poverty line candidate; not yet accepted as the current SDG societal poverty line.",
        ),
    ]

    pov = frames["ihs2_pov.dta"]
    exp = frames["ihs2_exp.dta"]
    if {"case_id", "rexp_cat06", "rexpagg"}.issubset(pov.columns) and {
        "case_id",
        "rexp_cat061",
        "rexp_cat062",
        "rexp_cat063",
    }.issubset(exp.columns):
        exp_check = exp[["case_id", "rexp_cat061", "rexp_cat062", "rexp_cat063"]].copy()
        for col in ["rexp_cat061", "rexp_cat062", "rexp_cat063"]:
            exp_check[col] = pd.to_numeric(exp_check[col], errors="coerce")
        exp_check["health_real_component_sum"] = exp_check[["rexp_cat061", "rexp_cat062", "rexp_cat063"]].sum(axis=1, min_count=1)
        merged = pov[["case_id", "rexp_cat06", "rexpagg"]].merge(exp_check[["case_id", "health_real_component_sum"]], on="case_id", how="left")
        merged["aggregate_diff_abs"] = (
            pd.to_numeric(merged["rexp_cat06"], errors="coerce")
            - pd.to_numeric(merged["health_real_component_sum"], errors="coerce")
        ).abs()
        usable = merged.dropna(subset=["rexp_cat06", "health_real_component_sum"])
        exact_or_tiny = int((usable["aggregate_diff_abs"] <= 1e-6).sum()) if len(usable) else 0
        rows.append(
            {
                "country": COUNTRY,
                "wave": WAVE,
                "idno": IDNO,
                "metric": "oop_aggregate_matches_real_component_sum",
                "source_member": "ihs2_pov.dta;ihs2_exp.dta",
                "variables": "rexp_cat06;rexp_cat061;rexp_cat062;rexp_cat063",
                "row_count": str(len(merged)),
                "nonmissing_count": str(len(usable)),
                "positive_count": str(exact_or_tiny),
                "zero_count": str(int((usable["aggregate_diff_abs"] == 0).sum()) if len(usable) else 0),
                "min": fmt_num(usable["aggregate_diff_abs"].min() if len(usable) else None),
                "p25": fmt_num(usable["aggregate_diff_abs"].quantile(0.25) if len(usable) else None),
                "median": fmt_num(usable["aggregate_diff_abs"].median() if len(usable) else None),
                "p75": fmt_num(usable["aggregate_diff_abs"].quantile(0.75) if len(usable) else None),
                "max": fmt_num(usable["aggregate_diff_abs"].max() if len(usable) else None),
                "mean": fmt_num(usable["aggregate_diff_abs"].mean() if len(usable) else None),
                "evidence_status": "raw_oop_aggregate_component_consistency_profile_available",
                "interpretation": "positive_count is rows with absolute aggregate-component difference <= 1e-6.",
            }
        )

        denom = pd.to_numeric(merged["rexpagg"], errors="coerce")
        oop = pd.to_numeric(merged["rexp_cat06"], errors="coerce")
        share = oop / denom.where(denom > 0)
        share_nonmissing = share.dropna()
        rows.append(
            {
                "country": COUNTRY,
                "wave": WAVE,
                "idno": IDNO,
                "metric": "candidate_che_oop_share_of_total_consumption",
                "source_member": "ihs2_pov.dta",
                "variables": "rexp_cat06;rexpagg",
                "row_count": str(len(share)),
                "nonmissing_count": str(len(share_nonmissing)),
                "positive_count": str(int((share_nonmissing > 0).sum())),
                "zero_count": str(int((share_nonmissing == 0).sum())),
                "min": fmt_num(share_nonmissing.min() if len(share_nonmissing) else None),
                "p25": fmt_num(share_nonmissing.quantile(0.25) if len(share_nonmissing) else None),
                "median": fmt_num(share_nonmissing.median() if len(share_nonmissing) else None),
                "p75": fmt_num(share_nonmissing.quantile(0.75) if len(share_nonmissing) else None),
                "max": fmt_num(share_nonmissing.max() if len(share_nonmissing) else None),
                "mean": fmt_num(share_nonmissing.mean() if len(share_nonmissing) else None),
                "evidence_status": "candidate_che10_che25_share_profile_not_final_indicator",
                "interpretation": "Candidate OOP/total-consumption share only; final CHE10/CHE25 still requires denominator and missing/unit policy signoff.",
            }
        )

    health = frames["sec_d.dta"]
    rows.extend(
        [
            numeric_profile(
                health,
                "sec_d.dta",
                ["d12"],
                "individual_health_spend_past_4_weeks_all",
                "Health module raw individual health-spending candidate; not the annual household CHE aggregate.",
            ),
            numeric_profile(
                health,
                "sec_d.dta",
                ["d13", "d14"],
                "individual_medicine_spend_past_4_weeks_components",
                "Health module raw medicine-spending components for need/access review.",
            ),
            numeric_profile(
                health,
                "sec_d.dta",
                ["d16"],
                "individual_hospitalization_cost_last_12_months",
                "Health module raw hospitalization cost candidate.",
            ),
            numeric_profile(
                health,
                "sec_d.dta",
                ["d19"],
                "individual_traditional_healer_cost_last_12_months",
                "Health module raw traditional-healer cost candidate.",
            ),
        ]
    )
    return rows


def build_outputs() -> tuple[list[dict[str, str]], list[dict[str, str]], list[dict[str, str]], list[dict[str, str]]]:
    if not ZIP_PATH.exists():
        raise FileNotFoundError(f"Missing raw zip package: {ZIP_PATH}")

    frames: dict[str, pd.DataFrame] = {}
    meta_by_member: dict[str, Any] = {}
    missing_cols: dict[str, list[str]] = {}
    actual_members: dict[str, str] = {}
    for basename, requested in REQUESTED_COLUMNS.items():
        df, meta, used, missing, actual_member = read_dta_member(ZIP_PATH, basename, requested)
        frames[basename] = df
        meta_by_member[basename] = meta
        missing_cols[basename] = missing
        actual_members[basename] = actual_member

    join_rows: list[dict[str, str]] = []
    join_rows.extend(
        [
            key_evidence_row(
                frames,
                "ihs2_household.dta",
                ["case_id"],
                "household_key_uniqueness",
                "Household-level poverty/consumption-ready file should be unique by case_id.",
            ),
            key_evidence_row(
                frames,
                "ihs2_exp.dta",
                ["case_id"],
                "expenditure_key_uniqueness",
                "Annual expenditure component file should be unique by case_id.",
            ),
            key_evidence_row(
                frames,
                "ihs2_pov.dta",
                ["case_id"],
                "poverty_consumption_key_uniqueness",
                "Poverty/consumption file should be unique by case_id.",
            ),
            key_evidence_row(
                frames,
                "ihs2_individ.dta",
                ["case_id", "memid"],
                "person_key_uniqueness",
                "Individual roster should be unique by household-person key case_id+memid.",
            ),
            key_evidence_row(
                frames,
                "sec_d.dta",
                ["case_id", "memid"],
                "health_module_person_key_uniqueness",
                "Health module should join to individual roster on case_id+memid.",
            ),
        ]
    )
    join_rows.extend(
        [
            join_evidence_row(
                frames,
                "ihs2_household.dta",
                "ihs2_exp.dta",
                ["case_id"],
                "household_to_expenditure_join",
                "Confirms denominator/covariate household file can join to expenditure components.",
            ),
            join_evidence_row(
                frames,
                "ihs2_household.dta",
                "ihs2_pov.dta",
                ["case_id"],
                "household_to_poverty_consumption_join",
                "Confirms household file can join to poverty/consumption aggregate file.",
            ),
            join_evidence_row(
                frames,
                "ihs2_individ.dta",
                "ihs2_household.dta",
                ["case_id"],
                "individual_households_to_household_join",
                "Confirms all individual-module households exist in household file.",
            ),
            join_evidence_row(
                frames,
                "sec_d.dta",
                "ihs2_household.dta",
                ["case_id"],
                "health_module_households_to_household_join",
                "Confirms all health-module households exist in household file.",
            ),
            join_evidence_row(
                frames,
                "sec_d.dta",
                "ihs2_individ.dta",
                ["case_id", "memid"],
                "health_module_to_individual_join",
                "Confirms health module joins to individual roster on case_id+memid.",
            ),
            join_evidence_row(
                frames,
                "ihs2_household.dta",
                "ihs2_ea_data.dta",
                ["dist", "ta", "ea"],
                "household_admin_ea_to_ea_file_join",
                "Confirms household dist+ta+ea geography can join to EA-level auxiliary file.",
            ),
        ]
    )

    financial_rows = build_financial_rows(frames)

    hh = frames["ihs2_household.dta"]
    pov = frames["ihs2_pov.dta"]
    health = frames["sec_d.dta"]
    exp = frames["ihs2_exp.dta"]

    idate_min, idate_max, idate_type = date_bounds(hh["idate"]) if "idate" in hh.columns else ("", "", "idate_missing")
    health_top_values = "; ".join(
        f"{var}: {top_values(health, meta_by_member['sec_d.dta'], var)}"
        for var in ["d04", "d07a", "d07b", "d15", "d17", "d20", "d26"]
        if var in health.columns
    )
    weight_positive = int((pd.to_numeric(hh["hhwght"], errors="coerce").dropna() > 0).sum()) if "hhwght" in hh.columns else 0
    strata_distinct = hh["strata"].dropna().nunique() if "strata" in hh.columns else 0
    ea_distinct = hh[["dist", "ta", "ea"]].dropna().drop_duplicates().shape[0] if {"dist", "ta", "ea"}.issubset(hh.columns) else 0
    consumption_positive = int((pd.to_numeric(pov["rexpagg"], errors="coerce").dropna() > 0).sum()) if "rexpagg" in pov.columns else 0
    oop_nonmissing = int(pd.to_numeric(pov["rexp_cat06"], errors="coerce").dropna().shape[0]) if "rexp_cat06" in pov.columns else 0
    oop_component_nonmissing = int(
        exp[["rexp_cat061", "rexp_cat062", "rexp_cat063"]].apply(pd.to_numeric, errors="coerce").dropna(how="all").shape[0]
    ) if {"rexp_cat061", "rexp_cat062", "rexp_cat063"}.issubset(exp.columns) else 0

    requirement_rows = [
        {
            "country": COUNTRY,
            "wave": WAVE,
            "idno": IDNO,
            "requirement": "household_person_keys",
            "raw_backed_evidence_status": "raw_backed_key_join_evidence_ready",
            "verification_decision": "not_final_verified",
            "source_members": "ihs2_household.dta;ihs2_exp.dta;ihs2_pov.dta;ihs2_individ.dta;sec_d.dta",
            "variables_checked": "case_id;memid",
            "evidence_summary": "Household, expenditure, and poverty files are profiled for case_id uniqueness; individual and health modules are profiled for case_id+memid; join coverage rows are in mwi2004_raw_module_join_evidence.csv.",
            "remaining_manual_review": "Confirm official key definitions and any module-level exclusions in questionnaire/documentation before accepting full raw-value verification.",
            "data_write_gate_effect": "does_not_open_data_gate",
        },
        {
            "country": COUNTRY,
            "wave": WAVE,
            "idno": IDNO,
            "requirement": "weights_and_design",
            "raw_backed_evidence_status": "raw_backed_weight_design_evidence_ready",
            "verification_decision": "not_final_verified",
            "source_members": "ihs2_household.dta;sec_d.dta",
            "variables_checked": "hhwght;strata;dist;ta;ea;psu;type;region",
            "evidence_summary": f"Household hhwght positive rows={weight_positive}; strata distinct={strata_distinct}; dist+ta+ea distinct={ea_distinct}; sec_d includes hhwght, psu, strata, and geography fields.",
            "remaining_manual_review": "Confirm sample design documentation and whether PSU should be psu, V51/V13, or dist+ta+ea for each analytic file.",
            "data_write_gate_effect": "does_not_open_data_gate",
        },
        {
            "country": COUNTRY,
            "wave": WAVE,
            "idno": IDNO,
            "requirement": "consumption_or_income",
            "raw_backed_evidence_status": "raw_backed_denominator_candidate_ready",
            "verification_decision": "not_final_verified",
            "source_members": "ihs2_pov.dta;ihs2_household.dta",
            "variables_checked": "rexpagg;rexpfood;rexpnfd;povline;ultrapovline;price_index;hhsize",
            "evidence_summary": f"rexpagg candidate total annual household expenditure has positive rows={consumption_positive}; poverty-line and price-index fields are present for policy review.",
            "remaining_manual_review": "Accept denominator policy, units, household/person scaling, missing semantics, and current SDG 3.8.2 poverty-line mapping.",
            "data_write_gate_effect": "does_not_open_data_gate",
        },
        {
            "country": COUNTRY,
            "wave": WAVE,
            "idno": IDNO,
            "requirement": "oop_health_expenditure",
            "raw_backed_evidence_status": "raw_backed_oop_aggregate_candidate_ready",
            "verification_decision": "not_final_verified",
            "source_members": "ihs2_pov.dta;ihs2_exp.dta;sec_d.dta",
            "variables_checked": "rexp_cat06;rexp_cat061;rexp_cat062;rexp_cat063;d12;d13;d14;d16;d19",
            "evidence_summary": f"Annual household health aggregate rexp_cat06 nonmissing rows={oop_nonmissing}; real health component rows={oop_component_nonmissing}; health module has individual spending candidates for recall-period review.",
            "remaining_manual_review": "Confirm exact OOP definition, exclusions, recall-to-annual handling, and whether survey-team aggregate is preferred over section D item sums.",
            "data_write_gate_effect": "does_not_open_data_gate",
        },
        {
            "country": COUNTRY,
            "wave": WAVE,
            "idno": IDNO,
            "requirement": "health_need_and_access",
            "raw_backed_evidence_status": "raw_backed_health_need_access_candidate_ready",
            "verification_decision": "not_final_verified",
            "source_members": "sec_d.dta",
            "variables_checked": "d04;d07a;d07b;d15;d17;d20;d21;d26;d27a;d27b;d36;d37;d38",
            "evidence_summary": f"Health module has illness/injury, action taken, hospitalization, borrowing/selling assets, chronic illness, maternal-care variables. Top values: {health_top_values}",
            "remaining_manual_review": "Map value labels into illness, care-seeking, forgone-care/no-action, hospitalization, chronic-need, and maternal-care constructs; confirm skip patterns.",
            "data_write_gate_effect": "does_not_open_data_gate",
        },
        {
            "country": COUNTRY,
            "wave": WAVE,
            "idno": IDNO,
            "requirement": "survey_timing",
            "raw_backed_evidence_status": "raw_backed_interview_date_ready",
            "verification_decision": "not_final_verified",
            "source_members": "ihs2_household.dta",
            "variables_checked": "idate",
            "evidence_summary": f"idate raw bounds={idate_min} to {idate_max}; date interpretation={idate_type}.",
            "remaining_manual_review": "Confirm fieldwork timing against official documentation and decide month-level climate exposure window.",
            "data_write_gate_effect": "does_not_open_data_gate",
        },
        {
            "country": COUNTRY,
            "wave": WAVE,
            "idno": IDNO,
            "requirement": "climate_geography",
            "raw_backed_evidence_status": "raw_backed_admin_ea_geography_ready_not_climate_linkage_accepted",
            "verification_decision": "not_final_verified",
            "source_members": "ihs2_household.dta;ihs2_ea_data.dta;sec_d.dta",
            "variables_checked": "region;dist;ta;ea;V51;V13;psu;access;access2;lz_code",
            "evidence_summary": f"Household dist+ta+ea distinct combinations={ea_distinct}; EA auxiliary data available; no GPS coordinate field is accepted in this script.",
            "remaining_manual_review": "Choose and document CHIRPS or ERA5 linkage route using EA/admin geography; verify boundary crosswalk and exposure aggregation.",
            "data_write_gate_effect": "does_not_open_data_gate",
        },
        {
            "country": COUNTRY,
            "wave": WAVE,
            "idno": IDNO,
            "requirement": "missing_codes_units_recall_skip_patterns",
            "raw_backed_evidence_status": "raw_labels_and_value_profiles_ready_manual_policy_required",
            "verification_decision": "not_final_verified",
            "source_members": "ihs2_pov.dta;ihs2_exp.dta;sec_d.dta;official DDI metadata",
            "variables_checked": "financial aggregates; health need/access variables; date/geography/design variables",
            "evidence_summary": "Raw value labels and numeric profiles are available for focused review; labels from sec_d are included in top-value evidence where present.",
            "remaining_manual_review": "Finalize missing-code, skip-pattern, recall-period, unit, and construct-level inclusion rules before any analysis-ready promotion.",
            "data_write_gate_effect": "does_not_open_data_gate",
        },
    ]

    missing_requested_count = sum(len(v) for v in missing_cols.values())
    all_key_rows_matched = sum(1 for row in join_rows if row["evidence_status"] in {"unique_at_expected_level", "all_left_distinct_keys_matched"})
    summary_rows = [
        {
            "metric": "country_wave",
            "value": IDNO,
            "interpretation": "Focused raw requirement verification evidence generated for this country-wave.",
        },
        {
            "metric": "source_raw_package",
            "value": str(ZIP_PATH.relative_to(TEMP_DIR.parent)),
            "interpretation": "Original raw package read locally; raw package itself remains excluded from Git.",
        },
        {
            "metric": "members_read",
            "value": str(len(frames)),
            "interpretation": "Selected raw Stata members read from the received Malawi 2004 package.",
        },
        {
            "metric": "requirements_with_raw_backed_evidence",
            "value": str(len(requirement_rows)),
            "interpretation": "Promotion requirements with focused raw-backed evidence rows.",
        },
        {
            "metric": "key_or_join_checks_passing",
            "value": f"{all_key_rows_matched}/{len(join_rows)}",
            "interpretation": "Uniqueness and join checks whose mechanical raw-profile status passed.",
        },
        {
            "metric": "missing_requested_columns",
            "value": str(missing_requested_count),
            "interpretation": "Requested audit variables not found in selected raw members.",
        },
        {
            "metric": "raw_value_verification_decision",
            "value": "not_final_verified",
            "interpretation": "This script strengthens evidence but does not promote the country-wave or open the data write gate.",
        },
        {
            "metric": "data_write_gate_status",
            "value": "closed",
            "interpretation": "No output from this script is an analysis-ready household-climate dataset.",
        },
    ]

    return requirement_rows, join_rows, financial_rows, summary_rows


def write_report(
    requirement_rows: list[dict[str, str]],
    join_rows: list[dict[str, str]],
    financial_rows: list[dict[str, str]],
    summary_rows: list[dict[str, str]],
) -> None:
    report = f"""# Malawi 2004 Raw Requirement Verification Evidence

Dataset: `{IDNO}` - {COUNTRY} {WAVE}

Purpose: move this country-wave from raw package receipt toward raw-value
verification by reading selected original Stata files and producing compact
evidence for keys, joins, weights/design, financial-protection inputs,
health-need/access variables, timing, and geography.

This is not a promoted analysis dataset. It does not write to `data/`, does
not mark Malawi 2004 as value-verified, and does not open the modeling gate.

## Summary

{markdown_table(summary_rows, ["metric", "value", "interpretation"], 20)}

## Requirement Evidence

{markdown_table(requirement_rows, ["requirement", "raw_backed_evidence_status", "verification_decision", "evidence_summary", "remaining_manual_review"], 12)}

## Key And Join Evidence

{markdown_table(join_rows, ["evidence_type", "left_member", "right_member", "key_variables", "left_distinct_keys", "right_distinct_keys", "matched_left_distinct_keys", "unmatched_left_distinct_keys", "evidence_status"], 20)}

## Financial And OOP Profiles

{markdown_table(financial_rows, ["metric", "source_member", "variables", "nonmissing_count", "positive_count", "min", "median", "max", "evidence_status"], 20)}

## Gate Decision

The correct gate decision remains `not_final_verified`. The next review step is
manual construct acceptance using these raw-backed profiles plus questionnaire
and DDI evidence:

- accept household/person key and module-level exclusions;
- accept survey design variables and weighting policy;
- accept CHE denominator and OOP aggregate definition;
- map illness/care-seeking/no-action labels into a double-failure outcome;
- accept interview-date to climate exposure timing;
- choose a CHIRPS or ERA5 linkage route from EA/admin geography;
- finalize missing-code, skip-pattern, unit, and recall-period rules.
"""
    REPORT_PATH.write_text(report, encoding="utf-8")
    HANDOFF_PATH.write_text(report, encoding="utf-8")


def main() -> None:
    ensure_dirs()
    requirement_rows, join_rows, financial_rows, summary_rows = build_outputs()
    write_csv(REQUIREMENT_EVIDENCE_PATH, requirement_rows, REQUIREMENT_COLUMNS)
    write_csv(JOIN_EVIDENCE_PATH, join_rows, JOIN_COLUMNS)
    write_csv(FINANCIAL_PROFILE_PATH, financial_rows, FINANCIAL_COLUMNS)
    write_csv(SUMMARY_PATH, summary_rows, SUMMARY_COLUMNS)
    write_report(requirement_rows, join_rows, financial_rows, summary_rows)
    append_log(TEMP_DIR / "audit_log.md", f"Built Malawi 2004 raw requirement verification evidence for {IDNO}.")


if __name__ == "__main__":
    main()
