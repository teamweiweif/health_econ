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

EXTERNAL_PARAMETER_SUMMARY_PATH = RESULT_DIR / "mwi2004_sdg382_external_parameter_candidate_summary.csv"
PRECHECK_SUMMARY_PATH = RESULT_DIR / "mwi2004_sdg382_candidate_classification_precheck_summary.csv"
AUDIT_PATH = RESULT_DIR / "mwi2004_sdg382_official_denominator_rule_audit.csv"
SUMMARY_PATH = RESULT_DIR / "mwi2004_sdg382_official_denominator_rule_summary.csv"
REPORT_PATH = REPORT_DIR / "mwi2004_sdg382_official_denominator_rule_audit.md"

OFFICIAL_METADATA_URL = "https://unstats.un.org/sdgs/metadata/files/Metadata-03-08-02.pdf"
OFFICIAL_METADATA_LAST_UPDATE = "2026-03-27"
THRESHOLD = 0.40

AUDIT_COLUMNS = [
    "component",
    "status",
    "value",
    "source",
    "evidence",
    "decision",
    "remaining_blocker",
]
SUMMARY_COLUMNS = ["metric", "value", "interpretation"]


def clean(value: Any) -> str:
    if value is None:
        return ""
    return " ".join(str(value).split())


def fmt(value: Any, digits: int = 8) -> str:
    if value is None or pd.isna(value):
        return ""
    try:
        return f"{float(value):.{digits}g}"
    except (TypeError, ValueError):
        return clean(value)


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


def read_member(zip_path: Path, basename: str, columns: list[str]) -> pd.DataFrame:
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
        missing = sorted(set(columns) - set(usecols))
        if missing:
            raise ValueError(f"Missing required columns in {basename}: {', '.join(missing)}")
        df, _ = pyreadstat.read_dta(str(raw_path), usecols=usecols)
        return df
    finally:
        raw_path.unlink(missing_ok=True)


def load_universe() -> pd.DataFrame:
    df = read_member(ZIP_PATH, "ihs2_pov.dta", ["case_id", "hhwght", "hhsize", "rexpagg", "rexp_cat06"])
    for column in ["hhwght", "hhsize", "rexpagg", "rexp_cat06"]:
        df[column] = pd.to_numeric(df[column], errors="coerce")
    universe = df[
        df["case_id"].notna()
        & (df["hhwght"] > 0)
        & (df["hhsize"] > 0)
        & (df["rexpagg"] > 0)
        & df["rexp_cat06"].notna()
    ].copy()
    universe["person_weight"] = universe["hhwght"] * universe["hhsize"]
    return universe


def weighted_sum(frame: pd.DataFrame, mask: pd.Series) -> float:
    return float(frame.loc[mask, "person_weight"].sum())


def build_outputs() -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    external_summary = read_csv_dicts(EXTERNAL_PARAMETER_SUMMARY_PATH)
    precheck_summary = read_csv_dicts(PRECHECK_SUMMARY_PATH)
    candidate_spl_daily = float(summary_value(external_summary, "candidate_spl_daily_raw_2004_mwk", "nan"))
    bridge_accepted = summary_value(external_summary, "external_parameter_bridge_accepted", "0")
    ppp_source_verified = summary_value(external_summary, "private_consumption_ppp_source_verified", "0")
    cpi_source_verified = summary_value(external_summary, "annual_cpi_bridge_source_verified", "0")
    precheck_positive_discretionary_rows = summary_value(precheck_summary, "positive_discretionary_candidate_sdg382_rows", "0")

    universe = load_universe()
    annual_spl = candidate_spl_daily * 365.0 * universe["hhsize"]
    discretionary_budget = universe["rexpagg"] - annual_spl
    positive_oop = universe["rexp_cat06"] > 0
    nonpositive_discretionary = discretionary_budget <= 0
    positive_discretionary = discretionary_budget > 0
    oop_share_positive_discretionary = universe["rexp_cat06"] / discretionary_budget.where(positive_discretionary)
    positive_discretionary_candidate = (
        positive_discretionary
        & positive_oop
        & (oop_share_positive_discretionary > THRESHOLD)
    )
    nonpositive_positive_oop_candidate = nonpositive_discretionary & positive_oop
    official_rule_candidate = nonpositive_positive_oop_candidate | positive_discretionary_candidate

    population_total = float(universe["person_weight"].sum())
    official_candidate_population = weighted_sum(universe, official_rule_candidate)
    official_candidate_rate = official_candidate_population / population_total if population_total else float("nan")
    nonpositive_population = weighted_sum(universe, nonpositive_discretionary)
    nonpositive_positive_oop_population = weighted_sum(universe, nonpositive_positive_oop_candidate)
    positive_discretionary_candidate_population = weighted_sum(universe, positive_discretionary_candidate)

    rows = [
        {
            "component": "official_negative_or_nonpositive_discretionary_rule",
            "status": "source_verified",
            "value": "accept_any_positive_oop_when_discretionary_budget_is_nonpositive",
            "source": OFFICIAL_METADATA_URL,
            "evidence": "UNSD metadata states that households below the societal poverty line have negative discretionary budget and any positive OOP exceeds a non-positive 40 percent threshold.",
            "decision": "official_denominator_rule_accepted",
            "remaining_blocker": "None for this denominator rule.",
        },
        {
            "component": "candidate_spl_bridge_status",
            "status": "blocked",
            "value": fmt(candidate_spl_daily, 12),
            "source": "result/mwi2004_sdg382_external_parameter_candidate_summary.csv",
            "evidence": f"ppp_source_verified={ppp_source_verified}; cpi_source_verified={cpi_source_verified}; external_parameter_bridge_accepted={bridge_accepted}",
            "decision": "candidate_spl_not_final",
            "remaining_blocker": "Accept the PPP concept and CPI/base-period bridge before final SDG 3.8.2 classification.",
        },
        {
            "component": "nonpositive_discretionary_bucket",
            "status": "computed_from_candidate_spl",
            "value": str(int(nonpositive_discretionary.sum())),
            "source": "temp/raw_downloads/MWI_2004_IHS-II_v01_M/MWI_2004_IHS-II_v01_M_Stata8.zip::ihs2_pov.dta",
            "evidence": f"weighted_population={fmt(nonpositive_population, 12)}; positive_oop_rows={int(nonpositive_positive_oop_candidate.sum())}; positive_oop_weighted_population={fmt(nonpositive_positive_oop_population, 12)}",
            "decision": "candidate_diagnostic_only",
            "remaining_blocker": "Bucket size depends on the candidate local-currency SPL bridge.",
        },
        {
            "component": "positive_discretionary_bucket",
            "status": "computed_from_candidate_spl",
            "value": str(int(positive_discretionary.sum())),
            "source": "temp/raw_downloads/MWI_2004_IHS-II_v01_M/MWI_2004_IHS-II_v01_M_Stata8.zip::ihs2_pov.dta",
            "evidence": f"candidate_sdg382_rows={int(positive_discretionary_candidate.sum())}; precheck_candidate_rows={precheck_positive_discretionary_rows}; candidate_weighted_population={fmt(positive_discretionary_candidate_population, 12)}",
            "decision": "candidate_diagnostic_only",
            "remaining_blocker": "Positive-discretionary classification is still tied to the candidate SPL bridge.",
        },
        {
            "component": "official_rule_candidate_classification",
            "status": "aggregate_stress_test",
            "value": str(int(official_rule_candidate.sum())),
            "source": "derived from official rule plus candidate Malawi 2004 SPL bridge",
            "evidence": f"weighted_population={fmt(official_candidate_population, 12)}; weighted_rate={fmt(official_candidate_rate, 12)}",
            "decision": "do_not_write_household_classification",
            "remaining_blocker": "Classification remains candidate because the local-currency SPL bridge is not accepted.",
        },
        {
            "component": "gate_decision",
            "status": "fail_closed",
            "value": "sdg382_ready=0",
            "source": "this audit",
            "evidence": "official_denominator_rule_accepted=1; external_parameter_bridge_accepted=0; candidate_classification_written_to_data=0",
            "decision": "keep_data_write_closed_and_modeling_blocked",
            "remaining_blocker": "Resolve the CPI/base-period and PPP/SPL bridge before promoting SDG 3.8.2.",
        },
    ]

    summary_rows = [
        {"metric": "country_wave", "value": IDNO, "interpretation": "Country-wave covered by the official denominator rule audit."},
        {"metric": "official_metadata_last_update", "value": OFFICIAL_METADATA_LAST_UPDATE, "interpretation": "Date printed in the current UNSD SDG 3.8.2 metadata file."},
        {"metric": "official_metadata_url", "value": OFFICIAL_METADATA_URL, "interpretation": "Primary source used for the denominator rule."},
        {"metric": "official_negative_discretionary_rule_verified", "value": "1", "interpretation": "Official metadata verifies that any positive OOP exceeds a nonpositive 40 percent discretionary-budget threshold."},
        {"metric": "official_denominator_rule_accepted", "value": "1", "interpretation": "The denominator rule is accepted as official; parameter conversion remains separate."},
        {"metric": "candidate_spl_daily_raw_2004_mwk", "value": fmt(candidate_spl_daily, 12), "interpretation": "Candidate local-currency SPL inherited from the external parameter ledger."},
        {"metric": "household_rows", "value": str(len(universe)), "interpretation": "Household rows in the internal Malawi SDG 3.8.2 frame."},
        {"metric": "weighted_population", "value": fmt(population_total, 12), "interpretation": "Population-weighted denominator for the aggregate stress test."},
        {"metric": "positive_oop_household_rows", "value": str(int(positive_oop.sum())), "interpretation": "Households with positive OOP health expenditure."},
        {"metric": "nonpositive_discretionary_budget_rows", "value": str(int(nonpositive_discretionary.sum())), "interpretation": "Rows where total consumption minus the candidate SPL is nonpositive."},
        {"metric": "positive_oop_nonpositive_discretionary_rows", "value": str(int(nonpositive_positive_oop_candidate.sum())), "interpretation": "Rows classified by the official nonpositive-discretionary rule under the candidate SPL."},
        {"metric": "positive_oop_nonpositive_discretionary_weighted_population", "value": fmt(nonpositive_positive_oop_population, 12), "interpretation": "Weighted population classified through the nonpositive-discretionary rule."},
        {"metric": "positive_discretionary_candidate_sdg382_rows", "value": str(int(positive_discretionary_candidate.sum())), "interpretation": "Candidate catastrophic rows among households with positive discretionary budget."},
        {"metric": "positive_discretionary_candidate_sdg382_weighted_population", "value": fmt(positive_discretionary_candidate_population, 12), "interpretation": "Weighted population classified among positive-discretionary rows."},
        {"metric": "official_rule_candidate_sdg382_rows", "value": str(int(official_rule_candidate.sum())), "interpretation": "Aggregate candidate classification using the official denominator rule plus candidate SPL."},
        {"metric": "official_rule_candidate_sdg382_weighted_population", "value": fmt(official_candidate_population, 12), "interpretation": "Weighted population for the official-rule candidate classification."},
        {"metric": "official_rule_candidate_sdg382_weighted_rate", "value": fmt(official_candidate_rate, 12), "interpretation": "Population-weighted candidate SDG 3.8.2 rate; not final."},
        {"metric": "external_parameter_bridge_accepted", "value": bridge_accepted, "interpretation": "Whether the PPP/CPI/base-period bridge is accepted for final SDG 3.8.2."},
        {"metric": "candidate_classification_written_to_data", "value": "0", "interpretation": "No household-level candidate SDG 3.8.2 classification was written to data/."},
        {"metric": "sdg382_ready", "value": "0", "interpretation": "The SDG 3.8.2 gate stays closed until the local-currency SPL bridge is accepted."},
        {"metric": "data_write_gate_status", "value": "closed", "interpretation": "This audit writes only aggregate result/report artifacts."},
        {"metric": "modeling_gate_status", "value": "blocked", "interpretation": "No predictive, reduced-form, causal ML, or policy learning is opened."},
    ]
    return rows, summary_rows


def markdown_table(rows: list[dict[str, str]], columns: list[str], limit: int = 40) -> str:
    if not rows:
        return "_No rows._"
    lines = ["| " + " | ".join(columns) + " |", "| " + " | ".join("---" for _ in columns) + " |"]
    for row in rows[:limit]:
        values: list[str] = []
        for column in columns:
            value = clean(row.get(column)).replace("|", "/")
            if len(value) > 120:
                value = value[:117] + "..."
            values.append(value)
        lines.append("| " + " | ".join(values) + " |")
    if len(rows) > limit:
        lines.append("| " + " | ".join("..." for _ in columns) + " |")
    return "\n".join(lines)


def write_report(rows: list[dict[str, str]], summary_rows: list[dict[str, str]]) -> None:
    REPORT_PATH.write_text(
        f"""# Malawi 2004 SDG 3.8.2 Official Denominator Rule Audit

Dataset: `{IDNO}` - {COUNTRY} {WAVE}

This artifact resolves one narrow SDG 3.8.2 blocker: the official denominator
rule for households whose discretionary budget is nonpositive. The UNSD
metadata says that when household consumption or income is below the societal
poverty line, discretionary budget is negative, so any positive OOP health
expenditure exceeds a nonpositive 40 percent discretionary-budget threshold.

Official source: {OFFICIAL_METADATA_URL}

This does **not** promote Malawi 2004 SDG 3.8.2. The Malawi local-currency SPL
still depends on a candidate PPP/CPI/base-period bridge, so the classification
below is an aggregate stress test only. No household-level SDG 3.8.2 field is
written to `data/`, and modeling remains blocked.

## Summary

{markdown_table(summary_rows, ['metric', 'value', 'interpretation'], 35)}

## Audit Components

{markdown_table(rows, ['component', 'status', 'value', 'decision', 'remaining_blocker'], 20)}

## Gate Decision

`official_denominator_rule_accepted=1`, but
`external_parameter_bridge_accepted=0`, `candidate_classification_written_to_data=0`,
`sdg382_ready=0`, `data_write_gate_status=closed`, and
`modeling_gate_status=blocked`.
""",
        encoding="utf-8",
    )


def main() -> None:
    ensure_dirs()
    rows, summary_rows = build_outputs()
    write_csv(AUDIT_PATH, rows, AUDIT_COLUMNS)
    write_csv(SUMMARY_PATH, summary_rows, SUMMARY_COLUMNS)
    write_report(rows, summary_rows)
    append_log(TEMP_DIR / "audit_log.md", f"Built Malawi 2004 SDG 3.8.2 official denominator rule audit rows={len(rows)}.")
    print(f"Malawi 2004 SDG 3.8.2 official denominator rule audit rows={len(rows)}.")


if __name__ == "__main__":
    main()
