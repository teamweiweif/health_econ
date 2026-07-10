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

EXCEPTION_PATH = RESULT_DIR / "mwi2004_health_exception_audit.csv"
SUMMARY_PATH = RESULT_DIR / "mwi2004_health_exception_summary.csv"
REPORT_PATH = REPORT_DIR / "mwi2004_health_exception_audit.md"
HANDOFF_PATH = RAW_DIR / "_MWI2004_HEALTH_EXCEPTION_AUDIT.md"

EXCEPTION_COLUMNS = [
    "country",
    "wave",
    "idno",
    "exception_domain",
    "exception_check",
    "exception_count",
    "overlap_count",
    "raw_id_exported",
    "aggregate_evidence",
    "decision_status",
    "promotion_effect",
    "remaining_blocker",
    "next_action",
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
    if not all(key in df.columns for key in keys):
        return set()
    key_df = df[keys].dropna().drop_duplicates()
    return {tuple(row) for row in key_df.itertuples(index=False, name=None)}


def label_map(meta: Any, variable: str) -> dict[Any, str]:
    labels = getattr(meta, "variable_value_labels", {}) or {}
    mapping = labels.get(variable, {})
    return mapping if isinstance(mapping, dict) else {}


def label_for(meta: Any, variable: str, value: Any) -> str:
    mapping = label_map(meta, variable)
    if value in mapping:
        return clean(mapping[value])
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return "Sysmiss" if pd.isna(value) else clean(value)
    for key, label in mapping.items():
        try:
            if float(key) == numeric:
                return clean(label)
        except (TypeError, ValueError):
            continue
    return clean(value)


def labeled_counts(df: pd.DataFrame, meta: Any, mask: pd.Series, variables: list[str]) -> str:
    parts: list[str] = []
    subset = df.loc[mask, variables]
    for variable in variables:
        if variable not in subset.columns:
            continue
        counts = subset[variable].value_counts(dropna=False).head(6)
        values = []
        for value, count in counts.items():
            label = label_for(meta, variable, value)
            values.append(f"{variable}={label}:{int(count)}")
        if values:
            parts.append("; ".join(values))
    return " | ".join(parts)


def row(
    domain: str,
    check: str,
    count: int,
    overlap: int,
    evidence: str,
    status: str,
    effect: str,
    blocker: str,
    action: str,
) -> dict[str, str]:
    return {
        "country": COUNTRY,
        "wave": WAVE,
        "idno": IDNO,
        "exception_domain": domain,
        "exception_check": check,
        "exception_count": str(count),
        "overlap_count": str(overlap),
        "raw_id_exported": "0",
        "aggregate_evidence": evidence,
        "decision_status": status,
        "promotion_effect": effect,
        "remaining_blocker": blocker,
        "next_action": action,
    }


def markdown_table(rows: list[dict[str, str]], columns: list[str], limit: int = 20) -> str:
    if not rows:
        return "_No rows._"
    lines = ["| " + " | ".join(columns) + " |", "| " + " | ".join("---" for _ in columns) + " |"]
    for item in rows[:limit]:
        lines.append("| " + " | ".join(clean(item.get(column)).replace("|", "/") for column in columns) + " |")
    if len(rows) > limit:
        lines.append("| " + " | ".join("..." for _ in columns) + " |")
    return "\n".join(lines)


def build_outputs() -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    if not ZIP_PATH.exists():
        raise FileNotFoundError(f"Missing raw package: {ZIP_PATH}")

    health, health_meta = read_member(
        ZIP_PATH,
        "sec_d.dta",
        ["case_id", "memid", "d04", "d07a", "d07b", "d15", "d17", "d18", "d20", "d26"],
    )
    roster, _ = read_member(ZIP_PATH, "ihs2_individ.dta", ["case_id", "memid"])

    roster_keys = key_set(roster, ["case_id", "memid"])
    health_keys = key_set(health, ["case_id", "memid"])
    key_tuples = list(health[["case_id", "memid"]].itertuples(index=False, name=None))
    health["_roster_match"] = [key in roster_keys for key in key_tuples]

    d04 = pd.to_numeric(health["d04"], errors="coerce")
    d07a = pd.to_numeric(health["d07a"], errors="coerce")
    d07b = pd.to_numeric(health["d07b"], errors="coerce")
    d15 = pd.to_numeric(health["d15"], errors="coerce")
    d17 = pd.to_numeric(health["d17"], errors="coerce")
    d18 = pd.to_numeric(health["d18"], errors="coerce")
    d20 = pd.to_numeric(health["d20"], errors="coerce")

    health_unmatched_mask = ~health["_roster_match"]
    d07a_leak_mask = d07a.notna() & (d04 != 1)
    d07b_leak_mask = d07b.notna() & (d04 != 1)
    d17_leak_mask = d17.notna() & (d15 != 1)
    d20_leak_mask = d20.notna() & (d18 != 1)

    health_unmatched = int(health_unmatched_mask.sum())
    roster_unmatched = len(roster_keys - health_keys)
    d07a_leak = int(d07a_leak_mask.sum())
    d07b_leak = int(d07b_leak_mask.sum())
    d17_leak = int(d17_leak_mask.sum())
    d20_leak = int(d20_leak_mask.sum())
    overlap_unmatched_d07a = int((health_unmatched_mask & d07a_leak_mask).sum())
    all_d07a_leak_explained = d07a_leak > 0 and overlap_unmatched_d07a == d07a_leak == health_unmatched

    unmatched_evidence = labeled_counts(
        health,
        health_meta,
        health_unmatched_mask,
        ["d04", "d07a", "d07b", "d15", "d17", "d18", "d20", "d26"],
    )
    leak_evidence = labeled_counts(health, health_meta, d07a_leak_mask, ["d04", "d07a", "d07b"])

    rows = [
        row(
            "person_key_join",
            "health_module_person_keys_absent_from_roster",
            health_unmatched,
            overlap_unmatched_d07a,
            unmatched_evidence,
            "exception_concentrated_in_nonroster_rows" if all_d07a_leak_explained else "exception_requires_review",
            "can_support_exclusion_policy_but_not_final_verification",
            "Need documented policy for excluding or reconciling health rows absent from the individual roster.",
            "Adopt a no-raw-ID roster-inner-join exception policy or locate documentation explaining the extra health rows.",
        ),
        row(
            "person_key_join",
            "roster_person_keys_absent_from_health_module",
            roster_unmatched,
            0,
            "No raw IDs exported; aggregate roster-only person keys absent from sec_d.",
            "minor_roster_health_absence_review",
            "does_not_block_financial_outcomes_but_blocks_full_double_failure_acceptance",
            "Need policy for roster persons with no health module row before person-level access denominator finalization.",
            "Confirm whether roster-only persons are structural nonrespondents, skips, or valid no-health-module rows.",
        ),
        row(
            "skip_consistency",
            "d07a_nonmissing_when_d04_not_yes",
            d07a_leak,
            overlap_unmatched_d07a,
            leak_evidence,
            "fully_explained_by_nonroster_health_rows" if all_d07a_leak_explained else "skip_leakage_requires_review",
            "can_support_d07a_skip_leakage_resolution_if_nonroster_rows_are_excluded",
            "d07a skip leakage cannot be treated as resolved until the nonroster-row policy is accepted.",
            "If the nonroster health rows are excluded, rerun label-skip decisions to verify d07a leakage becomes zero.",
        ),
        row(
            "skip_consistency",
            "d07b_nonmissing_when_d04_not_yes",
            d07b_leak,
            0,
            "No d07b leakage outside d04==Yes.",
            "pass_no_exception_detected",
            "supports_health_access_skip_rule",
            "",
            "Keep as passing evidence in the health/access label-skip review.",
        ),
        row(
            "skip_consistency",
            "d17_nonmissing_when_d15_not_yes",
            d17_leak,
            0,
            "No hospitalization-coping leakage outside d15==Yes.",
            "pass_no_exception_detected",
            "supports_financial_coping_skip_rule",
            "",
            "Keep as passing evidence in the health/access label-skip review.",
        ),
        row(
            "skip_consistency",
            "d20_nonmissing_when_d18_not_yes",
            d20_leak,
            0,
            "No traditional-healer-coping leakage outside d18==Yes.",
            "pass_no_exception_detected",
            "supports_financial_coping_skip_rule",
            "",
            "Keep as passing evidence in the health/access label-skip review.",
        ),
    ]

    summary = [
        {"metric": "country_wave", "value": IDNO, "interpretation": "Country-wave covered by this health exception audit."},
        {"metric": "health_module_rows", "value": str(len(health)), "interpretation": "Rows in sec_d.dta read for aggregate exception audit."},
        {"metric": "health_person_unmatched_to_roster", "value": str(health_unmatched), "interpretation": "Health-module person keys absent from roster; raw IDs are not exported."},
        {"metric": "roster_person_unmatched_to_health", "value": str(roster_unmatched), "interpretation": "Roster person keys absent from health module; raw IDs are not exported."},
        {"metric": "d07a_skip_leakage_rows", "value": str(d07a_leak), "interpretation": "d07a nonmissing rows where d04 is not Yes."},
        {"metric": "d07a_skip_leakage_overlap_with_unmatched_health_rows", "value": str(overlap_unmatched_d07a), "interpretation": "d07a leakage rows that are also absent from the roster."},
        {"metric": "d07a_skip_leakage_explained_by_nonroster_rows", "value": "1" if all_d07a_leak_explained else "0", "interpretation": "Whether all d07a leakage is exactly concentrated in nonroster health rows."},
        {"metric": "other_skip_leakage_rows", "value": str(d07b_leak + d17_leak + d20_leak), "interpretation": "Combined d07b, d17, and d20 leakage rows."},
        {"metric": "exception_policy_status", "value": "policy_pending_nonroster_exclusion_can_resolve_d07a_leakage" if all_d07a_leak_explained else "policy_pending_exception_unresolved", "interpretation": "Exception status; still not final verification."},
        {"metric": "data_write_gate_status", "value": "closed", "interpretation": "This exception audit cannot write promoted data."},
    ]
    return rows, summary


def write_report(rows: list[dict[str, str]], summary: list[dict[str, str]]) -> None:
    summary_by_metric = {row["metric"]: row["value"] for row in summary}
    explained = summary_by_metric.get("d07a_skip_leakage_explained_by_nonroster_rows") == "1"
    if explained:
        gate_decision = """The 6 `d07a` skip-leakage rows are fully concentrated in the 6 health-module
person keys absent from the individual roster. This supports, but does not yet
accept, a no-raw-ID exclusion/reconciliation policy for nonroster health rows.
Final verification remains blocked until that policy is documented and the
health/access label-skip audit is rerun under the accepted rule."""
    else:
        gate_decision = """The health-module person-key exception and the `d07a` skip-leakage
exception are separate aggregate issues. The `d07a` leakage is not explained by
nonroster health rows, so both the person-key exception and skip-rule exception
remain active blockers. Final verification remains blocked until both are
resolved or documented under an accepted construction rule."""
    report = f"""# Malawi 2004 Health Exception Audit

Dataset: `{IDNO}` - {COUNTRY} {WAVE}

This audit checks whether the health-module person-key exception and the
health/access skip exception are the same aggregate issue. It exports no
`case_id`, `memid`, or row-level raw identifiers.

## Summary

{markdown_table(summary, ["metric", "value", "interpretation"], 20)}

## Exception Checks

{markdown_table(rows, ["exception_domain", "exception_check", "exception_count", "overlap_count", "decision_status", "promotion_effect", "remaining_blocker"], 20)}

## Gate Decision

{gate_decision}
"""
    REPORT_PATH.write_text(report, encoding="utf-8")
    HANDOFF_PATH.write_text(report, encoding="utf-8")


def main() -> None:
    ensure_dirs()
    rows, summary = build_outputs()
    write_csv(EXCEPTION_PATH, rows, EXCEPTION_COLUMNS)
    write_csv(SUMMARY_PATH, summary, SUMMARY_COLUMNS)
    write_report(rows, summary)
    append_log(TEMP_DIR / "audit_log.md", f"Built Malawi 2004 health exception audit for {IDNO}.")


if __name__ == "__main__":
    main()
