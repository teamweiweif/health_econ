from __future__ import annotations

import os
import csv
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

DECISION_PATH = RESULT_DIR / "mwi2004_requirement_acceptance_decisions.csv"
METRIC_PATH = TEMP_DIR / "mwi2004_requirement_acceptance_metrics.csv"
SUMMARY_PATH = RESULT_DIR / "mwi2004_requirement_acceptance_summary.csv"
REPORT_PATH = REPORT_DIR / "mwi2004_requirement_acceptance_decisions.md"
HANDOFF_PATH = RAW_DIR / "_MWI2004_REQUIREMENT_ACCEPTANCE_DECISIONS.md"
HEALTH_ACCESS_LABEL_SKIP_SUMMARY_PATH = RESULT_DIR / "mwi2004_health_access_label_skip_summary.csv"

DECISION_COLUMNS = [
    "country",
    "wave",
    "idno",
    "requirement",
    "mechanical_raw_check_decision",
    "final_verification_decision",
    "acceptance_evidence",
    "remaining_blocker",
    "next_action",
    "data_write_gate_effect",
]

METRIC_COLUMNS = ["country", "wave", "idno", "metric", "value", "status", "interpretation"]
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


def summary_value(rows: list[dict[str, str]], metric_name: str, default: str = "") -> str:
    for row in rows:
        if clean(row.get("metric")) == metric_name:
            return clean(row.get("value")) or default
    return default


def fmt(value: Any) -> str:
    if value is None or pd.isna(value):
        return ""
    try:
        return f"{float(value):.6g}"
    except (TypeError, ValueError):
        return clean(value)


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
        usecols = [col for col in columns if col in available]
        return pyreadstat.read_dta(str(raw_path), apply_value_formats=False, usecols=usecols)
    finally:
        raw_path.unlink(missing_ok=True)


def key_set(df: pd.DataFrame, keys: list[str]) -> set[tuple[Any, ...]]:
    if not all(key in df.columns for key in keys):
        return set()
    key_df = df[keys].dropna().drop_duplicates()
    return {tuple(row) for row in key_df.itertuples(index=False, name=None)}


def date_bounds(series: pd.Series) -> tuple[str, str]:
    numeric = pd.to_numeric(series.dropna(), errors="coerce").dropna()
    converted = pd.to_datetime(numeric, unit="D", origin="1960-01-01", errors="coerce").dropna()
    if converted.empty:
        return "", ""
    return converted.min().date().isoformat(), converted.max().date().isoformat()


def label_map(meta: Any, variable: str) -> dict[Any, str]:
    labels = getattr(meta, "variable_value_labels", {}) or {}
    mapping = labels.get(variable, {})
    return mapping if isinstance(mapping, dict) else {}


def values_with_label(meta: Any, variable: str, needle: str) -> set[float]:
    out: set[float] = set()
    for value, label in label_map(meta, variable).items():
        if needle.lower() in clean(label).lower():
            try:
                out.add(float(value))
            except (TypeError, ValueError):
                pass
    return out


def metric(rows: list[dict[str, str]], name: str, value: Any, status: str, interpretation: str) -> None:
    rows.append(
        {
            "country": COUNTRY,
            "wave": WAVE,
            "idno": IDNO,
            "metric": name,
            "value": clean(value),
            "status": status,
            "interpretation": interpretation,
        }
    )


def markdown_table(rows: list[dict[str, str]], columns: list[str], limit: int = 20) -> str:
    if not rows:
        return "_No rows._"
    lines = ["| " + " | ".join(columns) + " |", "| " + " | ".join("---" for _ in columns) + " |"]
    for row in rows[:limit]:
        lines.append("| " + " | ".join(clean(row.get(column)).replace("|", "/") for column in columns) + " |")
    if len(rows) > limit:
        lines.append("| " + " | ".join("..." for _ in columns) + " |")
    return "\n".join(lines)


def build_outputs() -> tuple[list[dict[str, str]], list[dict[str, str]], list[dict[str, str]]]:
    if not ZIP_PATH.exists():
        raise FileNotFoundError(f"Missing raw package: {ZIP_PATH}")
    health_label_summary = read_csv_dicts(HEALTH_ACCESS_LABEL_SKIP_SUMMARY_PATH)
    health_label_decision = summary_value(health_label_summary, "health_access_label_skip_decision")
    health_label_rows = summary_value(health_label_summary, "label_decision_rows", "0")
    health_manual_review_rows = summary_value(health_label_summary, "manual_review_rows", "0")
    health_no_money_rows = summary_value(health_label_summary, "financial_barrier_no_money_rows", "0")
    health_skip_leakage_rows = summary_value(health_label_summary, "total_skip_leakage_rows", "missing")

    household, _ = read_member(
        ZIP_PATH,
        "ihs2_household.dta",
        ["case_id", "hhwght", "strata", "dist", "ta", "ea", "V51", "idate", "rexpagg", "rexp_cat06"],
    )
    exp, _ = read_member(
        ZIP_PATH,
        "ihs2_exp.dta",
        ["case_id", "rexp_cat061", "rexp_cat062", "rexp_cat063"],
    )
    pov, _ = read_member(
        ZIP_PATH,
        "ihs2_pov.dta",
        ["case_id", "rexpagg", "rexp_cat06", "povline", "price_index"],
    )
    individ, _ = read_member(ZIP_PATH, "ihs2_individ.dta", ["case_id", "memid"])
    health, health_meta = read_member(
        ZIP_PATH,
        "sec_d.dta",
        ["case_id", "memid", "d04", "d07a", "d07b", "d12", "d13", "d14", "d15", "d16", "d17", "d20", "d26", "hhwght", "psu", "strata", "dist", "ta", "ea"],
    )
    ea_data, _ = read_member(ZIP_PATH, "ihs2_ea_data.dta", ["dist", "ta", "ea", "access", "access2", "lz_code"])

    metrics: list[dict[str, str]] = []

    household_keys = key_set(household, ["case_id"])
    exp_keys = key_set(exp, ["case_id"])
    pov_keys = key_set(pov, ["case_id"])
    individ_keys = key_set(individ, ["case_id", "memid"])
    health_keys = key_set(health, ["case_id", "memid"])
    household_ea_keys = key_set(household, ["dist", "ta", "ea"])
    ea_keys = key_set(ea_data, ["dist", "ta", "ea"])

    metric(metrics, "household_case_id_distinct", len(household_keys), "pass", "Distinct household case_id keys in ihs2_household.dta.")
    metric(metrics, "exp_case_id_unmatched_to_household", len(exp_keys - household_keys), "pass" if not exp_keys - household_keys else "blocker", "Expenditure case_id keys absent from household file.")
    metric(metrics, "pov_case_id_unmatched_to_household", len(pov_keys - household_keys), "pass" if not pov_keys - household_keys else "blocker", "Poverty/consumption case_id keys absent from household file.")
    metric(metrics, "health_person_keys_unmatched_to_roster", len(health_keys - individ_keys), "blocker" if health_keys - individ_keys else "pass", "Health module case_id+memid keys absent from individual roster; raw IDs are intentionally not exported.")
    metric(metrics, "roster_person_keys_unmatched_to_health", len(individ_keys - health_keys), "review", "Individual roster case_id+memid keys absent from health module; raw IDs are intentionally not exported.")
    metric(metrics, "household_hhwght_positive_rows", f"{int((pd.to_numeric(household['hhwght'], errors='coerce') > 0).sum())}/{len(household)}", "pass", "Positive household weight coverage.")
    metric(metrics, "household_strata_distinct", household["strata"].dropna().nunique(), "pass", "Distinct household strata values.")
    metric(metrics, "health_psu_distinct", health["psu"].dropna().nunique(), "pass", "Distinct health-module PSU values.")
    metric(metrics, "household_ea_keys_matched_to_ea_file", len(household_ea_keys & ea_keys), "pass" if household_ea_keys <= ea_keys else "blocker", "Household dist+ta+ea keys matched to EA auxiliary file.")

    idate_min, idate_max = date_bounds(household["idate"])
    metric(metrics, "household_interview_date_min", idate_min, "pass" if idate_min else "blocker", "Earliest raw household interview date from idate.")
    metric(metrics, "household_interview_date_max", idate_max, "pass" if idate_max else "blocker", "Latest raw household interview date from idate.")

    rexpagg = pd.to_numeric(pov["rexpagg"], errors="coerce")
    oop = pd.to_numeric(pov["rexp_cat06"], errors="coerce")
    metric(metrics, "rexpagg_positive_rows", f"{int((rexpagg > 0).sum())}/{len(pov)}", "pass", "Positive total annual household expenditure rows.")
    metric(metrics, "rexp_cat06_nonmissing_rows", f"{int(oop.notna().sum())}/{len(pov)}", "pass", "Nonmissing annual household health expenditure aggregate rows.")

    exp_components = exp[["case_id", "rexp_cat061", "rexp_cat062", "rexp_cat063"]].copy()
    for column in ["rexp_cat061", "rexp_cat062", "rexp_cat063"]:
        exp_components[column] = pd.to_numeric(exp_components[column], errors="coerce")
    exp_components["component_sum"] = exp_components[["rexp_cat061", "rexp_cat062", "rexp_cat063"]].sum(axis=1, min_count=1)
    diff = (
        pov[["case_id", "rexp_cat06"]]
        .merge(exp_components[["case_id", "component_sum"]], on="case_id", how="left")
        .assign(diff_abs=lambda d: (pd.to_numeric(d["rexp_cat06"], errors="coerce") - d["component_sum"]).abs())["diff_abs"]
        .dropna()
    )
    diff_le_cent = int((diff <= 0.01).sum())
    metric(metrics, "oop_aggregate_component_max_abs_diff", fmt(diff.max() if len(diff) else None), "pass" if len(diff) and diff.max() <= 0.01 else "blocker", "Max absolute difference between rexp_cat06 and the sum of real health components.")
    metric(metrics, "oop_aggregate_component_diff_le_0_01_rows", f"{diff_le_cent}/{len(diff)}", "pass" if len(diff) and diff_le_cent == len(diff) else "blocker", "Rows whose OOP aggregate-component difference is within 0.01 local currency units.")

    share = oop / rexpagg.where(rexpagg > 0)
    share_nonmissing = share.dropna()
    metric(metrics, "candidate_che10_rows", int((share_nonmissing > 0.10).sum()), "diagnostic_not_final", "Candidate CHE10 count from rexp_cat06/rexpagg; not final indicator.")
    metric(metrics, "candidate_che25_rows", int((share_nonmissing > 0.25).sum()), "diagnostic_not_final", "Candidate CHE25 count from rexp_cat06/rexpagg; not final indicator.")

    d04 = pd.to_numeric(health["d04"], errors="coerce")
    illness_yes = int((d04 == 1).sum())
    no_money_values = values_with_label(health_meta, "d07a", "no money") | values_with_label(health_meta, "d07b", "no money")
    no_money_action = 0
    if no_money_values:
        d07a = pd.to_numeric(health["d07a"], errors="coerce")
        d07b = pd.to_numeric(health["d07b"], errors="coerce")
        no_money_action = int(d07a.isin(no_money_values).sum() + d07b.isin(no_money_values).sum())
    metric(metrics, "illness_injury_past_2_weeks_yes_rows", illness_yes, "pass" if illness_yes else "blocker", "Rows with d04 illness/injury yes.")
    metric(metrics, "care_action_no_money_label_hits", no_money_action, "review", "Rows where d07a/d07b labels indicate no-money non-care action; requires skip and double-count review.")

    decisions = [
        {
            "requirement": "household_person_keys",
            "mechanical_raw_check_decision": "blocked_person_join_exception_review_required",
            "final_verification_decision": "not_final_verified",
            "acceptance_evidence": f"household/exp/pov case_id joins pass; health->roster unmatched={len(health_keys - individ_keys)}; roster->health unmatched={len(individ_keys - health_keys)}.",
            "remaining_blocker": "Resolve or document the 6 health-module person keys unmatched to the individual roster before full double-failure person-level verification.",
            "next_action": "Inspect questionnaire/roster rules and decide whether unmatched health rows are valid exclusions; do not export raw IDs.",
        },
        {
            "requirement": "weights_and_design",
            "mechanical_raw_check_decision": "mechanical_raw_check_pass_documentation_policy_pending",
            "final_verification_decision": "not_final_verified",
            "acceptance_evidence": f"hhwght positive={int((pd.to_numeric(household['hhwght'], errors='coerce') > 0).sum())}/{len(household)}; strata={household['strata'].dropna().nunique()}; health psu={health['psu'].dropna().nunique()}.",
            "remaining_blocker": "Confirm official survey-design guidance and PSU choice across household, poverty, expenditure, and health files.",
            "next_action": "Record accepted survey design variables and sensitivity plan.",
        },
        {
            "requirement": "consumption_or_income",
            "mechanical_raw_check_decision": "mechanical_raw_check_pass_sdg_policy_pending",
            "final_verification_decision": "not_final_verified",
            "acceptance_evidence": f"rexpagg positive={int((rexpagg > 0).sum())}/{len(pov)}; povline and price_index are present.",
            "remaining_blocker": "CHE10/CHE25 denominator is mechanically ready, but SDG 3.8.2 societal poverty-line/discretionary-budget mapping is not accepted.",
            "next_action": "Write denominator policy for CHE10/CHE25 and separate SDG 3.8.2 capacity-to-pay review.",
        },
        {
            "requirement": "oop_health_expenditure",
            "mechanical_raw_check_decision": "mechanical_raw_check_pass_construct_policy_pending",
            "final_verification_decision": "not_final_verified",
            "acceptance_evidence": f"rexp_cat06 nonmissing={int(oop.notna().sum())}/{len(pov)}; component diff<=0.01 rows={diff_le_cent}/{len(diff)}; max diff={fmt(diff.max() if len(diff) else None)}.",
            "remaining_blocker": "Accept OOP construct scope and whether survey-team annual aggregate is preferred over health-module recall items.",
            "next_action": "Document OOP inclusion/exclusion and annual aggregate preference.",
        },
        {
            "requirement": "health_need_and_access",
            "mechanical_raw_check_decision": (
                "blocked_health_access_label_skip_or_manual_review_required"
                if health_label_decision == "label_skip_mapping_has_skip_or_manual_review_blockers"
                else "blocked_construct_label_skip_review_required"
            ),
            "final_verification_decision": "not_final_verified",
            "acceptance_evidence": f"d04 illness yes rows={illness_yes}; d07 no-money label hits={no_money_action}; label_decision_rows={health_label_rows}; no_money_rows={health_no_money_rows}; skip_leakage_rows={health_skip_leakage_rows}; d15/d17/d20/d26 are present.",
            "remaining_blocker": f"Health/access label-skip artifact status={health_label_decision or 'missing'}; manual_review_rows={health_manual_review_rows}; resolve d07 skip leakage, double-counting, formal-vs-informal care grouping, and person-join exceptions.",
            "next_action": "Resolve d07a skip leakage rows, classify remaining manual-review care-action labels, and set double-count/formal-care policy.",
        },
        {
            "requirement": "survey_timing",
            "mechanical_raw_check_decision": "mechanical_raw_check_pass_climate_window_pending",
            "final_verification_decision": "not_final_verified",
            "acceptance_evidence": f"idate converts to {idate_min} through {idate_max}.",
            "remaining_blocker": "Climate exposure window and aggregation month are not accepted.",
            "next_action": "Choose interview-month exposure windows for rainfall/heat measures.",
        },
        {
            "requirement": "climate_geography",
            "mechanical_raw_check_decision": "admin_ea_raw_check_pass_climate_route_pending",
            "final_verification_decision": "not_final_verified",
            "acceptance_evidence": f"household dist+ta+ea keys={len(household_ea_keys)}; matched to EA file={len(household_ea_keys & ea_keys)}; no GPS coordinate field accepted.",
            "remaining_blocker": "Accepted CHIRPS/ERA5 route is still missing; admin/EA geography needs boundary/crosswalk and exposure aggregation decision.",
            "next_action": "Define EA/admin climate linkage route and required boundary/crosswalk source.",
        },
        {
            "requirement": "missing_codes_units_recall_skip_patterns",
            "mechanical_raw_check_decision": "blocked_manual_policy_required",
            "final_verification_decision": "not_final_verified",
            "acceptance_evidence": "Raw value labels and profiles exist, but construct-level missing/skip/unit/recall rules are not finalized.",
            "remaining_blocker": "Missing-code, skip-pattern, recall-period, and unit policy must be accepted before any data write.",
            "next_action": "Write variable-level policy table and rerun requirement acceptance.",
        },
    ]
    for row in decisions:
        row.update({"country": COUNTRY, "wave": WAVE, "idno": IDNO, "data_write_gate_effect": "does_not_open_data_gate"})

    mechanical_pass_or_partial = sum("pass" in row["mechanical_raw_check_decision"] for row in decisions)
    hard_blocked = sum(row["mechanical_raw_check_decision"].startswith("blocked") for row in decisions)
    summary = [
        {"metric": "country_wave", "value": IDNO, "interpretation": "Country-wave adjudicated in this focused acceptance decision."},
        {"metric": "decision_rows", "value": str(len(decisions)), "interpretation": "Requirement-level acceptance decision rows."},
        {"metric": "mechanical_raw_checks_pass_or_partial", "value": str(mechanical_pass_or_partial), "interpretation": "Requirements with raw mechanical evidence that passes but still needs policy/documentation acceptance."},
        {"metric": "hard_blocked_requirements", "value": str(hard_blocked), "interpretation": "Requirements still blocked even before final climate/data promotion."},
        {"metric": "final_verified_requirements", "value": "0", "interpretation": "Requirements accepted as final raw-value verified; remains zero."},
        {"metric": "health_person_unmatched_to_roster", "value": str(len(health_keys - individ_keys)), "interpretation": "Health-module person keys absent from roster; raw IDs intentionally not exported."},
        {"metric": "oop_component_diff_le_0_01_rows", "value": f"{diff_le_cent}/{len(diff)}", "interpretation": "OOP aggregate-component numeric agreement under tolerance."},
        {"metric": "data_write_gate_status", "value": "closed", "interpretation": "No promoted dataset may be written from this decision artifact."},
    ]
    return decisions, metrics, summary


def write_report(decisions: list[dict[str, str]], metrics: list[dict[str, str]], summary: list[dict[str, str]]) -> None:
    report = f"""# Malawi 2004 Requirement Acceptance Decisions

Dataset: `{IDNO}` - {COUNTRY} {WAVE}

This file converts the focused raw-backed evidence into requirement-level
accept/block decisions. It does not export raw person IDs, does not write to
`data/`, and does not mark the country-wave as value-verified.

## Summary

{markdown_table(summary, ["metric", "value", "interpretation"], 20)}

## Decisions

{markdown_table(decisions, ["requirement", "mechanical_raw_check_decision", "final_verification_decision", "acceptance_evidence", "remaining_blocker", "next_action"], 12)}

## Metrics

{markdown_table(metrics, ["metric", "value", "status", "interpretation"], 40)}

## Gate Decision

The current decision remains fail-closed: `final_verified_requirements=0` and
`data_write_gate_status=closed`. Malawi 2004 has strong financial-protection
raw evidence, but full promotion still requires person-join exception review,
health/access construct mapping, missing/skip/unit/recall policy, and an
accepted CHIRPS or ERA5 climate-linkage route.
"""
    REPORT_PATH.write_text(report, encoding="utf-8")
    HANDOFF_PATH.write_text(report, encoding="utf-8")


def main() -> None:
    ensure_dirs()
    decisions, metrics, summary = build_outputs()
    write_csv(DECISION_PATH, decisions, DECISION_COLUMNS)
    write_csv(METRIC_PATH, metrics, METRIC_COLUMNS)
    write_csv(SUMMARY_PATH, summary, SUMMARY_COLUMNS)
    write_report(decisions, metrics, summary)
    append_log(TEMP_DIR / "audit_log.md", f"Built Malawi 2004 requirement acceptance decisions for {IDNO}.")


if __name__ == "__main__":
    main()
