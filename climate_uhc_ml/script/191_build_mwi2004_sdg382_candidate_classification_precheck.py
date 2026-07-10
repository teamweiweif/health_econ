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
PRECHECK_PATH = RESULT_DIR / "mwi2004_sdg382_candidate_classification_precheck.csv"
SUMMARY_PATH = RESULT_DIR / "mwi2004_sdg382_candidate_classification_precheck_summary.csv"
REPORT_PATH = REPORT_DIR / "mwi2004_sdg382_candidate_classification_precheck.md"

THRESHOLD = 0.40

PRECHECK_COLUMNS = [
    "denominator_policy_variant",
    "classification_status",
    "household_rows",
    "weighted_population",
    "positive_oop_household_rows",
    "nonpositive_discretionary_budget_rows",
    "nonpositive_discretionary_budget_population",
    "classified_household_rows",
    "candidate_sdg382_household_rows",
    "candidate_sdg382_weighted_population",
    "candidate_sdg382_weighted_rate",
    "max_candidate_oop_share",
    "p95_candidate_oop_share",
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
        df, _ = pyreadstat.read_dta(str(raw_path), usecols=usecols)
        return df
    finally:
        raw_path.unlink(missing_ok=True)


def weighted_quantile(values: pd.Series, weights: pd.Series, quantile: float) -> float:
    frame = pd.DataFrame({"value": pd.to_numeric(values, errors="coerce"), "weight": pd.to_numeric(weights, errors="coerce")})
    frame = frame.dropna()
    frame = frame[frame["weight"] > 0].sort_values("value")
    if frame.empty:
        return float("nan")
    cumulative = frame["weight"].cumsum()
    cutoff = quantile * frame["weight"].sum()
    return float(frame.loc[cumulative >= cutoff, "value"].iloc[0])


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


def variant_row(
    universe: pd.DataFrame,
    denominator: pd.Series,
    variant: str,
    classification_status: str,
    nonpositive_mask: pd.Series,
) -> dict[str, str]:
    valid = denominator > 0
    oop_share = universe["rexp_cat06"] / denominator.where(valid)
    classified = valid & oop_share.notna()
    candidate = classified & (universe["rexp_cat06"] > 0) & (oop_share > THRESHOLD)
    population_total = float(universe["person_weight"].sum())
    candidate_population = float(universe.loc[candidate, "person_weight"].sum())
    nonpositive_population = float(universe.loc[nonpositive_mask, "person_weight"].sum())
    weighted_rate = candidate_population / population_total if population_total else float("nan")
    return {
        "denominator_policy_variant": variant,
        "classification_status": classification_status,
        "household_rows": str(len(universe)),
        "weighted_population": fmt(population_total, 12),
        "positive_oop_household_rows": str(int((universe["rexp_cat06"] > 0).sum())),
        "nonpositive_discretionary_budget_rows": str(int(nonpositive_mask.sum())),
        "nonpositive_discretionary_budget_population": fmt(nonpositive_population, 12),
        "classified_household_rows": str(int(classified.sum())),
        "candidate_sdg382_household_rows": str(int(candidate.sum())),
        "candidate_sdg382_weighted_population": fmt(candidate_population, 12),
        "candidate_sdg382_weighted_rate": fmt(weighted_rate, 12),
        "max_candidate_oop_share": fmt(oop_share.loc[classified].max(), 12),
        "p95_candidate_oop_share": fmt(weighted_quantile(oop_share.loc[classified], universe.loc[classified, "person_weight"], 0.95), 12),
        "decision": "diagnostic_only_do_not_promote",
        "remaining_blocker": "Candidate PPP/CPI bridge and denominator floor rule are not accepted; SDG 3.8.2 remains not ready.",
    }


def build_outputs() -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    external_summary = read_csv_dicts(EXTERNAL_PARAMETER_SUMMARY_PATH)
    candidate_spl_daily = float(summary_value(external_summary, "candidate_spl_daily_raw_2004_mwk", "nan"))
    bridge_accepted = summary_value(external_summary, "external_parameter_bridge_accepted", "0")
    ppp_source_verified = summary_value(external_summary, "private_consumption_ppp_source_verified", "0")
    cpi_source_verified = summary_value(external_summary, "annual_cpi_bridge_source_verified", "0")

    universe = load_universe()
    annual_spl = candidate_spl_daily * 365.0 * universe["hhsize"]
    raw_discretionary = universe["rexpagg"] - annual_spl
    nonpositive = raw_discretionary <= 0

    rows = [
        variant_row(
            universe,
            raw_discretionary,
            "positive_discretionary_budget_only",
            "classify_only_positive_candidate_discretionary_budget",
            nonpositive,
        ),
        variant_row(
            universe,
            raw_discretionary.where(raw_discretionary > 0, universe["rexpagg"]),
            "floor_denominator_to_total_consumption_if_nonpositive",
            "sensitivity_variant_not_final",
            nonpositive,
        ),
    ]
    primary = rows[0]
    sensitivity = rows[1]
    summary_rows = [
        {"metric": "country_wave", "value": IDNO, "interpretation": "Country-wave covered by the candidate SDG 3.8.2 classification precheck."},
        {"metric": "candidate_spl_daily_raw_2004_mwk", "value": fmt(candidate_spl_daily, 12), "interpretation": "Candidate SPL from the external parameter source ledger; not final."},
        {"metric": "household_rows", "value": primary["household_rows"], "interpretation": "Household rows in the internal SDG 3.8.2 frame."},
        {"metric": "weighted_population", "value": primary["weighted_population"], "interpretation": "Population-weighted denominator before final SDG 3.8.2 acceptance."},
        {"metric": "positive_oop_household_rows", "value": primary["positive_oop_household_rows"], "interpretation": "Households with positive OOP health spending."},
        {"metric": "nonpositive_discretionary_budget_rows", "value": primary["nonpositive_discretionary_budget_rows"], "interpretation": "Rows where total consumption minus candidate SPL is nonpositive."},
        {"metric": "positive_discretionary_classified_rows", "value": primary["classified_household_rows"], "interpretation": "Rows classified under the strict positive-discretionary-budget diagnostic variant."},
        {"metric": "positive_discretionary_candidate_sdg382_rows", "value": primary["candidate_sdg382_household_rows"], "interpretation": "Candidate catastrophic rows under the strict diagnostic variant."},
        {"metric": "positive_discretionary_candidate_sdg382_weighted_rate", "value": primary["candidate_sdg382_weighted_rate"], "interpretation": "Population-weighted candidate rate under the strict diagnostic variant."},
        {"metric": "floor_variant_candidate_sdg382_rows", "value": sensitivity["candidate_sdg382_household_rows"], "interpretation": "Candidate catastrophic rows under the denominator-floor sensitivity variant."},
        {"metric": "floor_variant_candidate_sdg382_weighted_rate", "value": sensitivity["candidate_sdg382_weighted_rate"], "interpretation": "Population-weighted candidate rate under the denominator-floor sensitivity variant."},
        {"metric": "external_ppp_source_verified", "value": ppp_source_verified, "interpretation": "Whether PPP source candidate is captured in the external ledger."},
        {"metric": "external_cpi_source_verified", "value": cpi_source_verified, "interpretation": "Whether CPI source candidates are captured in the external ledger."},
        {"metric": "external_parameter_bridge_accepted", "value": bridge_accepted, "interpretation": "Whether the external PPP/CPI/base-period bridge is accepted."},
        {"metric": "candidate_classification_written_to_data", "value": "0", "interpretation": "No household-level candidate classification was written to data/."},
        {"metric": "sdg382_ready", "value": "0", "interpretation": "The candidate classification precheck does not open the SDG 3.8.2 gate."},
        {"metric": "data_write_gate_status", "value": "closed", "interpretation": "This precheck writes aggregate result/report artifacts only."},
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
        f"""# Malawi 2004 SDG 3.8.2 Candidate Classification Precheck

Dataset: `{IDNO}` - {COUNTRY} {WAVE}

This artifact stress-tests the candidate SDG 3.8.2 SPL bridge against Malawi
2004 raw financial inputs. It writes aggregate diagnostics only. It does not
write household-level candidate classifications to `data/`, does not update the
promotion registry, and does not open modeling gates.

Two denominator variants are shown because the external PPP/CPI bridge and the
final denominator floor rule are not accepted:

- `positive_discretionary_budget_only`: classify only rows with positive total
  consumption minus the candidate SPL.
- `floor_denominator_to_total_consumption_if_nonpositive`: sensitivity variant
  that uses total consumption where candidate discretionary budget is
  nonpositive.

## Summary

{markdown_table(summary_rows, ['metric', 'value', 'interpretation'], 30)}

## Candidate Variants

{markdown_table(rows, ['denominator_policy_variant', 'classification_status', 'nonpositive_discretionary_budget_rows', 'classified_household_rows', 'candidate_sdg382_household_rows', 'candidate_sdg382_weighted_rate', 'decision'], 10)}

## Gate Decision

This precheck narrows the remaining SDG 3.8.2 work to denominator policy:
candidate PPP/CPI/SPL values are available, but the CPI/base-period bridge and
denominator floor rule are still unaccepted. Therefore `sdg382_ready` remains
`0`, `data_write_gate_status` remains `closed`, and `modeling_gate_status`
remains `blocked`.
""",
        encoding="utf-8",
    )


def main() -> None:
    ensure_dirs()
    rows, summary_rows = build_outputs()
    write_csv(PRECHECK_PATH, rows, PRECHECK_COLUMNS)
    write_csv(SUMMARY_PATH, summary_rows, SUMMARY_COLUMNS)
    write_report(rows, summary_rows)
    append_log(TEMP_DIR / "audit_log.md", f"Built Malawi 2004 SDG 3.8.2 candidate classification precheck rows={len(rows)}.")
    print(f"Malawi 2004 SDG 3.8.2 candidate classification precheck rows={len(rows)}.")


if __name__ == "__main__":
    main()
