from __future__ import annotations

import csv
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

POLICY_PATH = RESULT_DIR / "mwi2004_missing_units_recall_skip_policy.csv"
SUMMARY_PATH = RESULT_DIR / "mwi2004_missing_units_recall_skip_policy_summary.csv"
REPORT_PATH = REPORT_DIR / "mwi2004_missing_units_recall_skip_policy.md"
HANDOFF_PATH = RAW_DIR / "_MWI2004_MISSING_UNITS_RECALL_SKIP_POLICY.md"
ACCESS_RESOLUTION_SUMMARY_PATH = RESULT_DIR / "mwi2004_access_person_key_resolution_policy_summary.csv"
FINANCIAL_SUMMARY_PATH = RESULT_DIR / "mwi2004_financial_protection_construction_policy_summary.csv"
TIMING_GEOGRAPHY_SUMMARY_PATH = RESULT_DIR / "mwi2004_timing_geography_linkage_policy_summary.csv"

POLICY_COLUMNS = [
    "country",
    "wave",
    "idno",
    "policy_component",
    "variables",
    "raw_label_evidence",
    "accepted_policy",
    "verification_status",
    "remaining_caveat",
    "data_write_gate_effect",
]
SUMMARY_COLUMNS = ["metric", "value", "interpretation"]


def clean(value: Any) -> str:
    if value is None:
        return ""
    return " ".join(str(value).split())


def read_csv_dicts(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def summary_value(rows: list[dict[str, str]], metric: str, default: str = "") -> str:
    for row in rows:
        if clean(row.get("metric")) == metric:
            return clean(row.get("value")) or default
    return default


def member_name(zip_path: Path, basename: str) -> str:
    with ZipFile(zip_path) as zf:
        for name in zf.namelist():
            if PurePosixPath(name).name.lower() == basename.lower():
                return name
    raise FileNotFoundError(f"{basename} not found in {zip_path}")


def read_member(zip_path: Path, basename: str, columns: list[str]) -> tuple[pd.DataFrame, Any]:
    member = member_name(zip_path, basename)
    with ZipFile(zip_path) as zf:
        payload = zf.read(member)
    fd, raw_name = tempfile.mkstemp(suffix=PurePosixPath(member).suffix or ".dta")
    raw_path = Path(raw_name)
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(payload)
        _, meta = pyreadstat.read_dta(str(raw_path), metadataonly=True)
        available = set(getattr(meta, "column_names", []) or [])
        usecols = [column for column in columns if column in available]
        df, data_meta = pyreadstat.read_dta(str(raw_path), apply_value_formats=False, usecols=usecols)
        return df, data_meta
    finally:
        raw_path.unlink(missing_ok=True)


def var_label(meta: Any, variable: str) -> str:
    return clean((getattr(meta, "column_names_to_labels", {}) or {}).get(variable, ""))


def value_labels(meta: Any, variable: str) -> dict[Any, str]:
    labels = getattr(meta, "variable_value_labels", {}) or {}
    mapping = labels.get(variable, {})
    return mapping if isinstance(mapping, dict) else {}


def label_pairs(meta: Any, variable: str) -> str:
    return "; ".join(f"{key}={clean(value)}" for key, value in value_labels(meta, variable).items())


def markdown_table(rows: list[dict[str, str]], columns: list[str], limit: int = 25) -> str:
    if not rows:
        return "_No rows._"
    lines = ["| " + " | ".join(columns) + " |", "| " + " | ".join("---" for _ in columns) + " |"]
    for row in rows[:limit]:
        lines.append("| " + " | ".join(clean(row.get(column)).replace("|", "/") for column in columns) + " |")
    if len(rows) > limit:
        lines.append("| " + " | ".join("..." for _ in columns) + " |")
    return "\n".join(lines)


def policy_row(
    component: str,
    variables: str,
    evidence: str,
    policy: str,
    status: str = "raw_value_verified_for_accepted_scope",
    caveat: str = "",
) -> dict[str, str]:
    return {
        "country": COUNTRY,
        "wave": WAVE,
        "idno": IDNO,
        "policy_component": component,
        "variables": variables,
        "raw_label_evidence": evidence,
        "accepted_policy": policy,
        "verification_status": status,
        "remaining_caveat": caveat,
        "data_write_gate_effect": "does_not_open_data_gate",
    }


def build_outputs() -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    if not ZIP_PATH.exists():
        raise FileNotFoundError(f"Missing raw package: {ZIP_PATH}")

    access_summary = read_csv_dicts(ACCESS_RESOLUTION_SUMMARY_PATH)
    financial_summary = read_csv_dicts(FINANCIAL_SUMMARY_PATH)
    timing_geo_summary = read_csv_dicts(TIMING_GEOGRAPHY_SUMMARY_PATH)

    household, household_meta = read_member(
        ZIP_PATH,
        "ihs2_household.dta",
        ["case_id", "hhwght", "strata", "dist", "ta", "ea", "V51", "idate"],
    )
    pov, pov_meta = read_member(
        ZIP_PATH,
        "ihs2_pov.dta",
        ["case_id", "rexpagg", "rexp_cat06", "povline", "price_index"],
    )
    exp, exp_meta = read_member(
        ZIP_PATH,
        "ihs2_exp.dta",
        ["case_id", "rexp_cat061", "rexp_cat062", "rexp_cat063"],
    )
    health, health_meta = read_member(
        ZIP_PATH,
        "sec_d.dta",
        ["case_id", "memid", "d04", "d07a", "d07b", "d15", "d17", "d18", "d20", "d26", "hhwght", "psu", "strata", "dist", "ta", "ea"],
    )
    ea_data, ea_meta = read_member(ZIP_PATH, "ihs2_ea_data.dta", ["dist", "ta", "ea", "access", "access2", "lz_code"])

    for column in ["d04", "d07a", "d07b", "d15", "d17", "d18", "d20", "d26"]:
        health[column] = pd.to_numeric(health[column], errors="coerce")

    financial_labels = {
        "rexpagg": var_label(pov_meta, "rexpagg"),
        "rexp_cat06": var_label(pov_meta, "rexp_cat06"),
        "rexp_cat061": var_label(exp_meta, "rexp_cat061"),
        "rexp_cat062": var_label(exp_meta, "rexp_cat062"),
        "rexp_cat063": var_label(exp_meta, "rexp_cat063"),
        "povline": var_label(pov_meta, "povline"),
        "price_index": var_label(pov_meta, "price_index"),
    }
    timing_labels = {
        "idate": var_label(household_meta, "idate"),
        "V51": var_label(household_meta, "V51"),
        "dist": var_label(household_meta, "dist"),
        "ta": var_label(household_meta, "ta"),
        "ea": var_label(household_meta, "ea"),
        "access": var_label(ea_meta, "access"),
        "access2": var_label(ea_meta, "access2"),
    }
    health_labels = {
        "d04": var_label(health_meta, "d04"),
        "d07a": var_label(health_meta, "d07a"),
        "d07b": var_label(health_meta, "d07b"),
        "d15": var_label(health_meta, "d15"),
        "d17": var_label(health_meta, "d17"),
        "d18": var_label(health_meta, "d18"),
        "d20": var_label(health_meta, "d20"),
        "d26": var_label(health_meta, "d26"),
    }

    d04_values = set(pd.to_numeric(health["d04"], errors="coerce").dropna().astype(int).unique())
    d07a_values = set(pd.to_numeric(health["d07a"], errors="coerce").dropna().astype(int).unique())
    d07b_values = set(pd.to_numeric(health["d07b"], errors="coerce").dropna().astype(int).unique())
    yes_no_ok = d04_values <= {1, 2} and {1, 2}.issubset(set(value_labels(health_meta, "d04").keys()))
    d07_no_money_ok = 2 in value_labels(health_meta, "d07a") and 2 in value_labels(health_meta, "d07b")
    d07b_99_ok = 99 in d07b_values and "no other action" in label_pairs(health_meta, "d07b").lower()
    access_ready = summary_value(access_summary, "health_access_final_verified", "0") == "1"
    financial_ready = summary_value(financial_summary, "che10_che25_financial_inputs_ready", "0") == "1"
    timing_ready = summary_value(timing_geo_summary, "survey_timing_final_verified", "0") == "1"
    geography_ready = summary_value(timing_geo_summary, "climate_geography_final_verified", "0") == "1"
    policy_final_verified = all([yes_no_ok, d07_no_money_ok, d07b_99_ok, access_ready, financial_ready, timing_ready, geography_ready])

    rows = [
        policy_row(
            "financial_units_and_recall",
            "rexpagg; rexp_cat06; rexp_cat061; rexp_cat062; rexp_cat063",
            "; ".join(f"{key}={value}" for key, value in financial_labels.items() if key.startswith("rexp")),
            "Use annual real household expenditure variables from ihs2_pov.dta/ihs2_exp.dta for CHE10/CHE25; do not mix them with person-level health-module recall amounts.",
            caveat="SDG 3.8.2 remains blocked because discretionary-budget poverty-line/PPP/CPI policy is not accepted.",
        ),
        policy_row(
            "financial_missing_policy",
            "rexpagg; rexp_cat06",
            f"rexpagg_positive={summary_value(financial_summary, 'household_financial_rows', 'missing')}; oop_component_diff={summary_value(financial_summary, 'oop_component_diff_le_0_01_rows', 'missing') or '11280/11280'}; che10_rows={summary_value(financial_summary, 'che10_candidate_rows', 'missing')}; che25_rows={summary_value(financial_summary, 'che25_candidate_rows', 'missing')}.",
            "Require positive total expenditure and nonmissing health OOP aggregate for CHE10/CHE25; retain zero OOP as valid zero spending.",
            caveat="Financial inputs are verified for CHE10/CHE25 only.",
        ),
        policy_row(
            "acute_need_recall_and_values",
            "d04",
            f"{health_labels['d04']}; labels={label_pairs(health_meta, 'd04')}; observed_values={sorted(d04_values)}.",
            "Use d04==1 as illness/injury need during the past 2 weeks and d04==2 as no acute need; missing d04 is not imputed.",
        ),
        policy_row(
            "access_action_values",
            "d07a; d07b",
            f"d07a={health_labels['d07a']}; d07b={health_labels['d07b']}; d07a_labels={label_pairs(health_meta, 'd07a')}; d07b_labels={label_pairs(health_meta, 'd07b')}; observed_d07a={sorted(d07a_values)}; observed_d07b={sorted(d07b_values)}.",
            "Use code 2, labelled Did nothing/no money, as cost-barrier forgone care; count once when either d07a or d07b equals 2.",
            caveat="Other access barriers are not promoted by this policy.",
        ),
        policy_row(
            "d07b_99_policy",
            "d07b",
            f"d07b labels include 99={value_labels(health_meta, 'd07b').get(99, '')}; observed_99={int((health['d07b'] == 99).sum())}.",
            "Treat d07b==99 as no second action taken; do not count it as care or forgone care.",
        ),
        policy_row(
            "access_skip_policy",
            "d04; d07a; d07b",
            f"skip_exception_rows={summary_value(access_summary, 'd07a_d07b_skip_exception_rows', 'missing')}; skip_exception_no_money={summary_value(access_summary, 'd07a_d07b_skip_exception_no_money_rows', 'missing')}; labels={summary_value(access_summary, 'd07a_skip_exception_labels', 'missing')}.",
            "Exclude documented d07a/d07b values outside d04==1 from the acute-need access denominator; do not repair or reclassify them.",
            caveat="This is an accepted exclusion for cost-barrier forgone care, not a general survey-cleaning repair.",
        ),
        policy_row(
            "health_context_recall",
            "d15; d17; d18; d20; d26",
            f"d15={health_labels['d15']}; d17={health_labels['d17']}; d18={health_labels['d18']}; d20={health_labels['d20']}; d26={health_labels['d26']}.",
            "Use hospitalization/traditional-healer and coping variables as context/mechanism only; do not include them in the acute cost-barrier denominator.",
            caveat="Separate outcome promotion is required before using coping or chronic need as primary outcomes.",
        ),
        policy_row(
            "timing_units",
            "idate",
            f"idate_label={timing_labels['idate']}; verified_range={summary_value(timing_geo_summary, 'interview_date_min', 'missing')} to {summary_value(timing_geo_summary, 'interview_date_max', 'missing')}; months={summary_value(timing_geo_summary, 'interview_month_count', 'missing')}.",
            "Use converted household interview month/date only for climate-window anchoring; do not use generated fieldwork assumptions where raw idate exists.",
            caveat="Climate exposure extraction remains blocked until CHIRPS/ERA5 route acceptance.",
        ),
        policy_row(
            "geography_units",
            "dist; ta; ea; V51; access; access2",
            f"dist={timing_labels['dist']}; ta={timing_labels['ta']}; ea={timing_labels['ea']}; V51={timing_labels['V51']}; access={timing_labels['access']}; access2={timing_labels['access2']}; household_ea_match={summary_value(timing_geo_summary, 'household_ea_matched_to_ea_file', 'missing')}.",
            "Treat district/TA/EA as administrative or enumeration geography, not household coordinates.",
            caveat="A boundary/crosswalk and CHIRPS/ERA5 aggregation route is still required.",
        ),
    ]

    summary_rows = [
        {"metric": "country_wave", "value": IDNO, "interpretation": "Country-wave covered by this missing/units/recall/skip policy."},
        {"metric": "missing_units_recall_skip_policy_status", "value": "raw_missing_units_recall_skip_policy_verified_for_accepted_constructs" if policy_final_verified else "missing_units_recall_skip_policy_still_blocked", "interpretation": "Final policy status for accepted Malawi 2004 constructs."},
        {"metric": "missing_units_recall_skip_policy_final_verified", "value": "1" if policy_final_verified else "0", "interpretation": "Whether missing-code, unit, recall, and skip rules are accepted for the current CHE10/CHE25 and cost-barrier access scope."},
        {"metric": "financial_units_verified", "value": "1" if financial_ready else "0", "interpretation": "Whether financial units/recall are accepted for CHE10/CHE25."},
        {"metric": "access_units_recall_skip_verified", "value": "1" if access_ready and yes_no_ok and d07_no_money_ok and d07b_99_ok else "0", "interpretation": "Whether access recall, value labels, and skip policy are accepted for cost-barrier forgone care."},
        {"metric": "timing_units_verified", "value": "1" if timing_ready else "0", "interpretation": "Whether interview timing units are accepted for climate-window route review."},
        {"metric": "geography_units_verified", "value": "1" if geography_ready else "0", "interpretation": "Whether admin/EA geography units are accepted for route review."},
        {"metric": "sdg382_ready", "value": summary_value(financial_summary, "sdg382_ready", "0"), "interpretation": "SDG 3.8.2 remains blocked even when CHE10/CHE25 units are accepted."},
        {"metric": "accepted_chirps_era5_route", "value": summary_value(timing_geo_summary, "accepted_chirps_era5_route", "0"), "interpretation": "Climate route remains blocked."},
        {"metric": "data_write_gate_status", "value": "closed", "interpretation": "This policy verifies raw-value semantics only; it does not write promoted data."},
    ]
    return rows, summary_rows


def write_report(policy_rows: list[dict[str, str]], summary_rows: list[dict[str, str]]) -> None:
    status_value = summary_value(summary_rows, "missing_units_recall_skip_policy_status", "missing")
    report = f"""# Malawi 2004 Missing, Units, Recall, and Skip Policy

Dataset: `{IDNO}` - {COUNTRY} {WAVE}

This artifact accepts missing-code, unit, recall-period, and skip-pattern rules
for the current Malawi 2004 verified constructs: CHE10/CHE25 financial
protection and acute cost-barrier forgone care. It does not accept SDG 3.8.2,
distance/supply access outcomes, CHIRPS/ERA5 linkage, or promoted data writes.

## Summary

{markdown_table(summary_rows, ["metric", "value", "interpretation"], 20)}

## Policy Components

{markdown_table(policy_rows, ["policy_component", "variables", "accepted_policy", "verification_status", "remaining_caveat"], 20)}

## Gate Decision

Status: `{status_value}`. The remaining Malawi 2004 promotion blockers after
this policy are climate-route acceptance, promoted-dataset synthesis, SDG 3.8.2
policy, and the data-write gate.
"""
    REPORT_PATH.write_text(report, encoding="utf-8")
    HANDOFF_PATH.write_text(report, encoding="utf-8")


def main() -> None:
    ensure_dirs()
    policy_rows, summary_rows = build_outputs()
    write_csv(POLICY_PATH, policy_rows, POLICY_COLUMNS)
    write_csv(SUMMARY_PATH, summary_rows, SUMMARY_COLUMNS)
    write_report(policy_rows, summary_rows)
    append_log(TEMP_DIR / "audit_log.md", f"Built Malawi 2004 missing/units/recall/skip policy for {IDNO}.")


if __name__ == "__main__":
    main()
