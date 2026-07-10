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

POLICY_PATH = RESULT_DIR / "mwi2004_health_access_construction_policy.csv"
SUMMARY_PATH = RESULT_DIR / "mwi2004_health_access_construction_policy_summary.csv"
REPORT_PATH = REPORT_DIR / "mwi2004_health_access_construction_policy.md"
HANDOFF_PATH = RAW_DIR / "_MWI2004_HEALTH_ACCESS_CONSTRUCTION_POLICY.md"

POLICY_COLUMNS = [
    "country",
    "wave",
    "idno",
    "policy_component",
    "candidate_rule",
    "raw_variables",
    "aggregate_count",
    "denominator_rule",
    "double_count_rule",
    "skip_exception_rule",
    "acceptance_status",
    "remaining_blocker",
]
SUMMARY_COLUMNS = ["metric", "value", "interpretation"]


def clean(value: Any) -> str:
    if value is None:
        return ""
    return " ".join(str(value).split())


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


def markdown_table(rows: list[dict[str, str]], columns: list[str], limit: int = 20) -> str:
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
    rule: str,
    variables: str,
    count: int,
    denominator: str,
    double_count: str,
    skip_rule: str,
    status: str,
    blocker: str,
) -> dict[str, str]:
    return {
        "country": COUNTRY,
        "wave": WAVE,
        "idno": IDNO,
        "policy_component": component,
        "candidate_rule": rule,
        "raw_variables": variables,
        "aggregate_count": str(count),
        "denominator_rule": denominator,
        "double_count_rule": double_count,
        "skip_exception_rule": skip_rule,
        "acceptance_status": status,
        "remaining_blocker": blocker,
    }


def build_outputs() -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    if not ZIP_PATH.exists():
        raise FileNotFoundError(f"Missing raw package: {ZIP_PATH}")

    health, _ = read_member(
        ZIP_PATH,
        "sec_d.dta",
        ["case_id", "memid", "d04", "d07a", "d07b", "d15", "d17", "d18", "d20", "d26"],
    )
    roster, _ = read_member(ZIP_PATH, "ihs2_individ.dta", ["case_id", "memid"])

    roster_keys = key_set(roster, ["case_id", "memid"])
    health["_roster_match"] = [
        key in roster_keys for key in health[["case_id", "memid"]].itertuples(index=False, name=None)
    ]
    d04 = pd.to_numeric(health["d04"], errors="coerce")
    d07a = pd.to_numeric(health["d07a"], errors="coerce")
    d07b = pd.to_numeric(health["d07b"], errors="coerce")
    d15 = pd.to_numeric(health["d15"], errors="coerce")
    d17 = pd.to_numeric(health["d17"], errors="coerce")
    d18 = pd.to_numeric(health["d18"], errors="coerce")
    d20 = pd.to_numeric(health["d20"], errors="coerce")
    d26 = pd.to_numeric(health["d26"], errors="coerce")

    analytic_person = health["_roster_match"]
    acute_need = analytic_person & (d04 == 1)
    d07a_leak = analytic_person & d07a.notna() & (d04 != 1)
    d07b_leak = analytic_person & d07b.notna() & (d04 != 1)

    no_money = acute_need & ((d07a == 2) | (d07b == 2))
    did_nothing_not_serious = acute_need & ((d07a == 1) | (d07b == 1))
    no_second_action_only = acute_need & (d07b == 99)
    formal_core = acute_need & (d07a.isin([5, 7]) | d07b.isin([5, 7]))
    formal_extended = acute_need & (d07a.isin([5, 6, 7]) | d07b.isin([5, 6, 7]))
    informal_self = acute_need & (d07a.isin([3, 9, 10, 11]) | d07b.isin([3, 9, 10, 11]))
    any_action = acute_need & (
        d07a.notna()
        | d07b.notna()
    ) & ~((d07a.isin([1, 2])) & d07b.isna())
    hospitalization_need = analytic_person & (d15 == 1)
    hospitalization_coping = hospitalization_need & (d17 == 1)
    traditional_healer_need = analytic_person & (d18 == 1)
    traditional_healer_coping = traditional_healer_need & (d20 == 1)
    chronic_need = analytic_person & (d26 == 1)

    policy_rows = [
        policy_row(
            "analytic_person_universe",
            "Keep health rows with case_id+memid present in ihs2_individ.dta; do not export raw IDs.",
            "case_id;memid",
            int(analytic_person.sum()),
            "Roster-matched sec_d person rows.",
            "One row per case_id+memid in sec_d; unresolved duplicate policy if future waves differ.",
            "Nonroster health rows remain excluded only as a candidate policy, not final acceptance.",
            "candidate_policy_ready_exception_documentation_pending",
            "Need formal exception policy for 6 nonroster health rows and 2 roster-only health absences.",
        ),
        policy_row(
            "acute_need_denominator",
            "Recent illness/injury need equals d04==Yes among roster-matched health rows.",
            "d04",
            int(acute_need.sum()),
            "Roster-matched health rows with d04==Yes.",
            "One person-row counted once even if two illness problems/actions are listed.",
            "d07a/d07b values outside d04==Yes remain skip exceptions and are not included.",
            "candidate_policy_ready_skip_exception_pending",
            "Need accepted rule for 6 d07a skip-leakage rows outside d04==Yes.",
        ),
        policy_row(
            "financial_barrier_forgone_care",
            "Financial access failure candidate equals any d07a/d07b value labeled Did nothing, no money among acute-need rows.",
            "d04;d07a;d07b",
            int(no_money.sum()),
            "Roster-matched d04==Yes rows.",
            "Use row-level any(d07a==2, d07b==2), so a person is counted once.",
            "Ignore d07a/d07b outside d04==Yes unless a final skip-repair rule is accepted.",
            "candidate_policy_ready_double_count_policy_pending",
            "Need final double-count and missing-action policy before access outcome promotion.",
        ),
        policy_row(
            "nonfinancial_no_action_context",
            "Nonfinancial no-action context equals any d07a/d07b value labeled Did nothing, not serious among acute-need rows.",
            "d04;d07a;d07b",
            int(did_nothing_not_serious.sum()),
            "Roster-matched d04==Yes rows.",
            "Use row-level any(d07a==1, d07b==1).",
            "Do not treat as financial access failure without no-money label.",
            "candidate_context_policy_ready",
            "Need final decision whether this remains context only or becomes nonfinancial access barrier.",
        ),
        policy_row(
            "formal_care_core",
            "Core formal care equals government or private health facility in d07a/d07b among acute-need rows.",
            "d04;d07a;d07b",
            int(formal_core.sum()),
            "Roster-matched d04==Yes rows.",
            "Use row-level any(d07a/d07b in {government facility, private facility}).",
            "Exclude church/mission facility from core but include in sensitivity.",
            "candidate_policy_ready_provider_grouping_pending",
            "Need accepted provider grouping for church/mission facility, pharmacy, and traditional healer.",
        ),
        policy_row(
            "formal_care_extended_sensitivity",
            "Extended formal care adds church/mission facility to government/private facilities.",
            "d04;d07a;d07b",
            int(formal_extended.sum()),
            "Roster-matched d04==Yes rows.",
            "Use row-level any(d07a/d07b in {government, private, church/mission facility}).",
            "Sensitivity only until provider grouping is accepted.",
            "candidate_sensitivity_policy_ready",
            "Need final provider grouping decision.",
        ),
        policy_row(
            "informal_or_self_care_context",
            "Informal/self-care context includes medicine in stock, grocery medicine, traditional healer, and faith healer among acute-need rows.",
            "d04;d07a;d07b",
            int(informal_self.sum()),
            "Roster-matched d04==Yes rows.",
            "Use row-level any matching informal/self-care labels.",
            "Context/sensitivity only until provider grouping is accepted.",
            "candidate_context_policy_ready",
            "Need final formal/informal grouping decision.",
        ),
        policy_row(
            "hospitalization_coping_context",
            "Hospitalization cost-coping context equals d15==Yes and d17==Yes.",
            "d15;d17",
            int(hospitalization_coping.sum()),
            "Roster-matched d15==Yes rows.",
            "One person-row counted once.",
            "d17 skip leakage outside d15==Yes is zero in current audit.",
            "candidate_context_policy_ready",
            "Need final decision whether coping is context, mechanism, or severity outcome.",
        ),
        policy_row(
            "traditional_healer_coping_context",
            "Traditional-healer cost-coping context equals d18==Yes and d20==Yes.",
            "d18;d20",
            int(traditional_healer_coping.sum()),
            "Roster-matched d18==Yes rows.",
            "One person-row counted once.",
            "d20 skip leakage outside d18==Yes is zero in current audit.",
            "candidate_context_policy_ready",
            "Need final decision whether traditional-healer care is access, informal care, or context only.",
        ),
        policy_row(
            "chronic_need_context",
            "Chronic need context equals d26==Yes among roster-matched health rows.",
            "d26",
            int(chronic_need.sum()),
            "Roster-matched health rows with d26==Yes.",
            "One person-row counted once.",
            "Used as chronic-need context, not acute forgone-care denominator by default.",
            "candidate_context_policy_ready",
            "Need final decision whether chronic need enters double-failure denominator.",
        ),
        policy_row(
            "documented_skip_exceptions",
            "Document skip exceptions without repairing raw values: d07a leakage outside d04==Yes remains excluded and flagged.",
            "d04;d07a;d07b;d15;d17;d18;d20",
            int(d07a_leak.sum() + d07b_leak.sum()),
            "Not an outcome denominator.",
            "No person-level outcome is created from skip-exception rows.",
            "d07a leakage is separate from nonroster rows and must be reported as an active blocker.",
            "blocking_exception_policy_required",
            "Need accepted skip-leakage exclusion/repair rule before health/access final verification.",
        ),
    ]

    summary_rows = [
        {"metric": "country_wave", "value": IDNO, "interpretation": "Country-wave covered by this health/access construction policy."},
        {"metric": "analytic_roster_matched_health_rows", "value": str(int(analytic_person.sum())), "interpretation": "Candidate analytic person rows in sec_d matched to individual roster."},
        {"metric": "acute_need_denominator_rows", "value": str(int(acute_need.sum())), "interpretation": "Roster-matched d04==Yes rows."},
        {"metric": "financial_barrier_forgone_care_rows", "value": str(int(no_money.sum())), "interpretation": "Candidate no-money forgone-care rows counted once per person row."},
        {"metric": "formal_care_core_rows", "value": str(int(formal_core.sum())), "interpretation": "Candidate government/private facility care rows."},
        {"metric": "formal_care_extended_rows", "value": str(int(formal_extended.sum())), "interpretation": "Candidate formal care rows adding church/mission facility."},
        {"metric": "informal_or_self_care_rows", "value": str(int(informal_self.sum())), "interpretation": "Candidate informal/self-care context rows."},
        {"metric": "d07a_d07b_skip_exception_rows", "value": str(int(d07a_leak.sum() + d07b_leak.sum())), "interpretation": "d07a/d07b nonmissing rows outside d04==Yes under roster-matched candidate universe."},
        {"metric": "no_second_action_only_rows", "value": str(int(no_second_action_only.sum())), "interpretation": "Rows with d07b indicating no other action taken among acute-need rows."},
        {"metric": "hospitalization_need_rows", "value": str(int(hospitalization_need.sum())), "interpretation": "Roster-matched d15==Yes rows."},
        {"metric": "hospitalization_coping_rows", "value": str(int(hospitalization_coping.sum())), "interpretation": "Roster-matched d15==Yes and d17==Yes rows."},
        {"metric": "traditional_healer_need_rows", "value": str(int(traditional_healer_need.sum())), "interpretation": "Roster-matched d18==Yes rows."},
        {"metric": "traditional_healer_coping_rows", "value": str(int(traditional_healer_coping.sum())), "interpretation": "Roster-matched d18==Yes and d20==Yes rows."},
        {"metric": "chronic_need_context_rows", "value": str(int(chronic_need.sum())), "interpretation": "Roster-matched d26==Yes rows."},
        {"metric": "construction_policy_status", "value": "candidate_policy_ready_active_skip_and_provider_blockers", "interpretation": "Policy is explicit enough for review but not final verification."},
        {"metric": "final_health_access_verified", "value": "0", "interpretation": "Health/access construct is not final verified."},
        {"metric": "data_write_gate_status", "value": "closed", "interpretation": "No promoted data may be written from this policy artifact."},
    ]
    return policy_rows, summary_rows


def write_report(policy_rows: list[dict[str, str]], summary_rows: list[dict[str, str]]) -> None:
    report = f"""# Malawi 2004 Health Access Construction Policy

Dataset: `{IDNO}` - {COUNTRY} {WAVE}

This artifact proposes a candidate construction policy for acute illness,
care-seeking, no-money forgone care, provider grouping, and health-cost coping
using `sec_d.dta`. It exports only aggregate counts and rules. It does not
write person-level data and does not final-verify the health/access gate.

## Summary

{markdown_table(summary_rows, ["metric", "value", "interpretation"], 25)}

## Candidate Policy Components

{markdown_table(policy_rows, ["policy_component", "candidate_rule", "aggregate_count", "acceptance_status", "remaining_blocker"], 20)}

## Gate Decision

The construction policy is explicit enough for review, but not final. Active
blockers remain: the 6 `d07a` skip-exception rows outside `d04==Yes`, provider
grouping for church/mission/pharmacy/traditional care, double-count treatment
across `d07a` and `d07b`, and the roster/health person-key exceptions.
"""
    REPORT_PATH.write_text(report, encoding="utf-8")
    HANDOFF_PATH.write_text(report, encoding="utf-8")


def main() -> None:
    ensure_dirs()
    policy_rows, summary_rows = build_outputs()
    write_csv(POLICY_PATH, policy_rows, POLICY_COLUMNS)
    write_csv(SUMMARY_PATH, summary_rows, SUMMARY_COLUMNS)
    write_report(policy_rows, summary_rows)
    append_log(TEMP_DIR / "audit_log.md", f"Built Malawi 2004 health/access construction policy for {IDNO}.")


if __name__ == "__main__":
    main()
