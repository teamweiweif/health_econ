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

POLICY_PATH = RESULT_DIR / "mwi2004_access_person_key_resolution_policy.csv"
SUMMARY_PATH = RESULT_DIR / "mwi2004_access_person_key_resolution_policy_summary.csv"
REPORT_PATH = REPORT_DIR / "mwi2004_access_person_key_resolution_policy.md"
HANDOFF_PATH = RAW_DIR / "_MWI2004_ACCESS_PERSON_KEY_RESOLUTION_POLICY.md"
LABEL_SKIP_SUMMARY_PATH = RESULT_DIR / "mwi2004_health_access_label_skip_summary.csv"
EXCEPTION_SUMMARY_PATH = RESULT_DIR / "mwi2004_health_exception_summary.csv"
CONSTRUCTION_SUMMARY_PATH = RESULT_DIR / "mwi2004_health_access_construction_policy_summary.csv"

POLICY_COLUMNS = [
    "country",
    "wave",
    "idno",
    "policy_component",
    "raw_variables",
    "aggregate_count",
    "accepted_rule",
    "evidence",
    "final_verification_decision",
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
        return pyreadstat.read_dta(str(raw_path), apply_value_formats=False, usecols=usecols)
    finally:
        raw_path.unlink(missing_ok=True)


def key_set(df: pd.DataFrame, keys: list[str]) -> set[tuple[Any, ...]]:
    key_df = df[keys].dropna().drop_duplicates()
    return {tuple(row) for row in key_df.itertuples(index=False, name=None)}


def label_for(meta: Any, variable: str, code: int) -> str:
    labels = getattr(meta, "variable_value_labels", {}) or {}
    mapping = labels.get(variable, {})
    return clean(mapping.get(code, ""))


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
    count: int,
    rule: str,
    evidence: str,
    decision: str,
    caveat: str,
) -> dict[str, str]:
    return {
        "country": COUNTRY,
        "wave": WAVE,
        "idno": IDNO,
        "policy_component": component,
        "raw_variables": variables,
        "aggregate_count": str(count),
        "accepted_rule": rule,
        "evidence": evidence,
        "final_verification_decision": decision,
        "remaining_caveat": caveat,
        "data_write_gate_effect": "does_not_open_data_gate",
    }


def build_outputs() -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    if not ZIP_PATH.exists():
        raise FileNotFoundError(f"Missing raw package: {ZIP_PATH}")

    label_summary = read_csv_dicts(LABEL_SKIP_SUMMARY_PATH)
    exception_summary = read_csv_dicts(EXCEPTION_SUMMARY_PATH)
    construction_summary = read_csv_dicts(CONSTRUCTION_SUMMARY_PATH)

    health, health_meta = read_member(
        ZIP_PATH,
        "sec_d.dta",
        ["case_id", "memid", "d04", "d07a", "d07b", "d15", "d17", "d18", "d20", "d26"],
    )
    roster, _ = read_member(ZIP_PATH, "ihs2_individ.dta", ["case_id", "memid"])

    roster_keys = key_set(roster, ["case_id", "memid"])
    health_keys = key_set(health, ["case_id", "memid"])
    health["_roster_match"] = [
        key in roster_keys for key in health[["case_id", "memid"]].itertuples(index=False, name=None)
    ]
    for column in ["d04", "d07a", "d07b", "d15", "d17", "d18", "d20", "d26"]:
        health[column] = pd.to_numeric(health[column], errors="coerce")

    matched = health["_roster_match"]
    acute_need = matched & (health["d04"] == 1)
    nonroster = ~matched
    d07a_skip_leak = matched & health["d07a"].notna() & (health["d04"] != 1)
    d07b_skip_leak = matched & health["d07b"].notna() & (health["d04"] != 1)
    no_money = acute_need & ((health["d07a"] == 2) | (health["d07b"] == 2))
    no_money_all_health = (health["d04"] == 1) & ((health["d07a"] == 2) | (health["d07b"] == 2))
    formal_core = acute_need & (health["d07a"].isin([5, 7]) | health["d07b"].isin([5, 7]))
    formal_extended = acute_need & (health["d07a"].isin([5, 6, 7]) | health["d07b"].isin([5, 6, 7]))
    pharmacy = acute_need & ((health["d07a"] == 8) | (health["d07b"] == 8))
    personal_remedies = acute_need & ((health["d07a"] == 4) | (health["d07b"] == 4))
    other_relatives = acute_need & (health["d07a"].isin([12, 13]) | health["d07b"].isin([12, 13]))
    d07a_skip_no_money = d07a_skip_leak & (health["d07a"] == 2)
    d07b_skip_no_money = d07b_skip_leak & (health["d07b"] == 2)
    nonroster_no_money = nonroster & ((health["d07a"] == 2) | (health["d07b"] == 2))
    nonroster_d04_yes = nonroster & (health["d04"] == 1)

    no_money_label = label_for(health_meta, "d07a", 2) or "Did nothing, no money"
    d04_yes_label = label_for(health_meta, "d04", 1) or "Yes"
    d04_no_label = label_for(health_meta, "d04", 2) or "No"
    d07a_skip_values = sorted({int(v) for v in health.loc[d07a_skip_leak, "d07a"].dropna().unique()})
    d07a_skip_labels = "; ".join(f"{value}={label_for(health_meta, 'd07a', value)}" for value in d07a_skip_values)

    policy_rows = [
        policy_row(
            "analytic_access_person_universe",
            "case_id; memid",
            int(matched.sum()),
            "Use only sec_d person rows whose case_id+memid appears in ihs2_individ.dta.",
            f"matched_health_rows={int(matched.sum())}; health_unmatched_to_roster={len(health_keys - roster_keys)}; roster_unmatched_to_health={len(roster_keys - health_keys)}.",
            "raw_value_verified_for_access_person_universe_with_documented_exclusions",
            "Six nonroster health rows and two roster-only rows are excluded from person-level access outcomes; raw IDs are not exported.",
        ),
        policy_row(
            "nonroster_health_rows",
            "case_id; memid; d04; d07a; d07b",
            int(nonroster.sum()),
            "Exclude nonroster health rows from person-level access outcomes and report them as documented exclusions.",
            f"nonroster_d04_yes={int(nonroster_d04_yes.sum())}; nonroster_no_money={int(nonroster_no_money.sum())}; exception_status={summary_value(exception_summary, 'exception_policy_status', 'missing')}.",
            "documented_exclusion_accepted_for_access_scope",
            "This does not prove full roster-module reconciliation for every possible health construct.",
        ),
        policy_row(
            "roster_only_rows",
            "case_id; memid",
            len(roster_keys - health_keys),
            "Do not impute health need or access outcomes for roster persons absent from sec_d.",
            "Roster-only rows have no health-module observation and are kept out of the access denominator.",
            "documented_exclusion_accepted_for_access_scope",
            "This is a no-imputation rule, not evidence of no illness or no forgone care.",
        ),
        policy_row(
            "acute_need_denominator",
            "d04",
            int(acute_need.sum()),
            "Define acute health need as d04==1 among roster-matched sec_d rows.",
            f"d04 labels: 1={d04_yes_label}; 2={d04_no_label}; construction_summary_denominator={summary_value(construction_summary, 'acute_need_denominator_rows', 'missing')}.",
            "raw_value_verified_for_acute_need_denominator",
            "Chronic need and hospitalization are context/mechanism only unless separately promoted.",
        ),
        policy_row(
            "cost_barrier_forgone_care",
            "d04; d07a; d07b",
            int(no_money.sum()),
            "Among roster-matched d04==1 rows, count a person once if d07a==2 or d07b==2.",
            f"d07a/d07b code 2 label={no_money_label}; matched_no_money={int(no_money.sum())}; all_health_no_money={int(no_money_all_health.sum())}; construction_summary_no_money={summary_value(construction_summary, 'financial_barrier_forgone_care_rows', 'missing')}.",
            "raw_value_verified_for_cost_barrier_forgone_care",
            "This verifies cost-barrier forgone care, not distance/supply access barriers.",
        ),
        policy_row(
            "d07a_d07b_skip_exceptions",
            "d04; d07a; d07b",
            int(d07a_skip_leak.sum() + d07b_skip_leak.sum()),
            "Do not repair d07a/d07b values outside d04==1; exclude them from the acute-need denominator and report the leakage.",
            f"d07a_leakage={int(d07a_skip_leak.sum())}; d07b_leakage={int(d07b_skip_leak.sum())}; d07a_skip_no_money={int(d07a_skip_no_money.sum())}; d07b_skip_no_money={int(d07b_skip_no_money.sum())}; d07a_skip_labels={d07a_skip_labels}.",
            "documented_exclusion_accepted_for_access_scope",
            "Excluded leakage rows are not used to repair access outcomes; their presence remains a survey-quality caveat.",
        ),
        policy_row(
            "provider_grouping_context",
            "d07a; d07b",
            int(formal_core.sum()),
            "Use government/private facilities as core formal care; add church/mission as an extended sensitivity.",
            f"formal_core={int(formal_core.sum())}; formal_extended={int(formal_extended.sum())}; pharmacy={int(pharmacy.sum())}; personal_remedies={int(personal_remedies.sum())}; other_or_relatives={int(other_relatives.sum())}.",
            "context_grouping_documented_not_required_for_cost_barrier_gate",
            "Provider grouping is context/sensitivity here and does not change the cost-barrier forgone-care numerator.",
        ),
    ]

    final_verified = (
        int(no_money.sum()) == int(no_money_all_health.sum())
        and int(nonroster_d04_yes.sum()) == 0
        and int(nonroster_no_money.sum()) == 0
        and int(d07a_skip_no_money.sum()) == 0
        and int(d07b_skip_no_money.sum()) == 0
        and int(acute_need.sum()) > 0
    )
    status_value = (
        "access_person_keys_and_cost_barrier_forgone_care_verified_with_documented_exclusions"
        if final_verified
        else "access_person_key_resolution_still_blocked"
    )
    summary_rows = [
        {"metric": "country_wave", "value": IDNO, "interpretation": "Country-wave covered by this access/person-key resolution policy."},
        {"metric": "access_resolution_status", "value": status_value, "interpretation": "Final access/person-key resolution decision for the stated cost-barrier forgone-care scope."},
        {"metric": "person_key_policy_final_verified_for_access", "value": "1" if final_verified else "0", "interpretation": "Whether person-key exceptions are accepted for the stated access outcome scope."},
        {"metric": "health_access_final_verified", "value": "1" if final_verified else "0", "interpretation": "Whether acute need and cost-barrier forgone care are raw-value verified under the documented exclusion policy."},
        {"metric": "access_forgone_care_inputs_ready", "value": "1" if final_verified else "0", "interpretation": "Whether Malawi 2004 can be counted as access/forgone-care ready for the stated cost-barrier outcome."},
        {"metric": "analytic_roster_matched_health_rows", "value": str(int(matched.sum())), "interpretation": "sec_d rows matched to the individual roster."},
        {"metric": "health_person_unmatched_to_roster", "value": str(len(health_keys - roster_keys)), "interpretation": "Health-module person keys excluded from the access universe; raw IDs not exported."},
        {"metric": "roster_person_unmatched_to_health", "value": str(len(roster_keys - health_keys)), "interpretation": "Roster person keys with no health-module observation; no access outcome is imputed."},
        {"metric": "nonroster_d04_yes_rows", "value": str(int(nonroster_d04_yes.sum())), "interpretation": "Nonroster health rows with acute illness/injury need."},
        {"metric": "nonroster_no_money_rows", "value": str(int(nonroster_no_money.sum())), "interpretation": "Nonroster health rows with no-money access action."},
        {"metric": "acute_need_denominator_rows", "value": str(int(acute_need.sum())), "interpretation": "Roster-matched d04==Yes rows."},
        {"metric": "cost_barrier_forgone_care_rows", "value": str(int(no_money.sum())), "interpretation": "Roster-matched acute-need rows with any no-money no-action label, counted once."},
        {"metric": "all_health_cost_barrier_rows", "value": str(int(no_money_all_health.sum())), "interpretation": "All sec_d d04==Yes rows with no-money label; used to show exclusions do not change the no-money count."},
        {"metric": "d07a_d07b_skip_exception_rows", "value": str(int(d07a_skip_leak.sum() + d07b_skip_leak.sum())), "interpretation": "Nonmissing d07a/d07b values outside d04==Yes under the roster-matched universe."},
        {"metric": "d07a_d07b_skip_exception_no_money_rows", "value": str(int(d07a_skip_no_money.sum() + d07b_skip_no_money.sum())), "interpretation": "Skip-exception rows carrying the no-money value; must be zero for accepted exclusion."},
        {"metric": "d07a_skip_exception_labels", "value": d07a_skip_labels, "interpretation": "Aggregate value-label evidence for excluded d07a skip exceptions."},
        {"metric": "formal_care_core_rows", "value": str(int(formal_core.sum())), "interpretation": "Government/private facility care rows among acute-need universe."},
        {"metric": "formal_care_extended_rows", "value": str(int(formal_extended.sum())), "interpretation": "Government/private/church/mission care rows among acute-need universe."},
        {"metric": "label_manual_review_rows", "value": summary_value(label_summary, "manual_review_rows", "0"), "interpretation": "Health/access label rows still requiring review outside the promoted cost-barrier rule."},
        {"metric": "data_write_gate_status", "value": "closed", "interpretation": "This policy verifies an input requirement but does not write promoted data."},
    ]
    return policy_rows, summary_rows


def write_report(policy_rows: list[dict[str, str]], summary_rows: list[dict[str, str]]) -> None:
    status_value = summary_value(summary_rows, "access_resolution_status", "missing")
    report = f"""# Malawi 2004 Access Person-Key Resolution Policy

Dataset: `{IDNO}` - {COUNTRY} {WAVE}

This artifact resolves the health-module person-key and skip-exception policy
for one narrow access construct: acute need (`d04==Yes`) and cost-barrier
forgone care (`d07a==2` or `d07b==2`) among roster-matched `sec_d` person rows.

It exports only aggregate evidence. Raw person IDs are not written.

## Summary

{markdown_table(summary_rows, ["metric", "value", "interpretation"], 30)}

## Policy Components

{markdown_table(policy_rows, ["policy_component", "aggregate_count", "accepted_rule", "final_verification_decision", "remaining_caveat"], 20)}

## Gate Decision

Status: `{status_value}`.

This verifies the Malawi 2004 access/forgone-care input for the stated
cost-barrier outcome only. It does not verify SDG 3.8.2, distance or supply
barrier outcomes, a CHIRPS/ERA5 climate route, or promoted data synthesis.
Therefore the data-write gate remains closed.
"""
    REPORT_PATH.write_text(report, encoding="utf-8")
    HANDOFF_PATH.write_text(report, encoding="utf-8")


def main() -> None:
    ensure_dirs()
    policy_rows, summary_rows = build_outputs()
    write_csv(POLICY_PATH, policy_rows, POLICY_COLUMNS)
    write_csv(SUMMARY_PATH, summary_rows, SUMMARY_COLUMNS)
    write_report(policy_rows, summary_rows)
    append_log(TEMP_DIR / "audit_log.md", f"Built Malawi 2004 access/person-key resolution policy for {IDNO}.")


if __name__ == "__main__":
    main()
