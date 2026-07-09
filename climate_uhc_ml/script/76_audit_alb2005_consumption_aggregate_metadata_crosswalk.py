from __future__ import annotations

import csv
import math
import warnings
from pathlib import Path
from typing import Any

import pandas as pd

from common import REPORT_DIR, RESULT_DIR, TEMP_DIR, append_log, ensure_dirs, write_csv

try:
    import pyreadstat
except ImportError:  # pragma: no cover - environment audit covers this.
    pyreadstat = None


IDNO = "ALB_2005_LSMS_v01_M"
COUNTRY = "Albania"
SURVEY_NAME = "Living Standards Measurement Survey 2005"
WAVE = "2005"

RAW_ROOT = TEMP_DIR / "raw_extracted" / "lsms2005en_1e7f1965c4a5" / "lsms2005en"
DATA_ROOT = RAW_ROOT / "Data_2005"
POVERTY_SAV = DATA_ROOT / "poverty.sav"

METADATA_VARIABLE_CATALOG = TEMP_DIR / "raw_schema_inventory" / "metadata_variable_catalog.csv"
UNIT_PERIOD_SUMMARY_PATH = RESULT_DIR / "alb2005_consumption_oop_unit_period_summary.csv"

AUDIT_PATH = TEMP_DIR / "alb2005_consumption_aggregate_metadata_crosswalk_audit.csv"
SUMMARY_PATH = RESULT_DIR / "alb2005_consumption_aggregate_metadata_crosswalk_summary.csv"
REPORT_PATH = REPORT_DIR / "alb2005_consumption_aggregate_metadata_crosswalk_audit.md"

DECISION = "blocked_alb2005_consumption_aggregate_metadata_crosswalk_not_ready"
NO_PROMOTION = "not_promoted_aggregate_metadata_crosswalk_audit_only"

METADATA_AGGREGATE_VARIABLES = [
    "food",
    "edu",
    "durcons",
    "nfoodc",
    "nfood05",
    "totutil",
    "totutil05",
    "totcons",
    "totcons05",
]

LOCAL_PER_CAPITA_COMPONENTS = ["rcons", "rfood", "rnfood", "rutility", "reduexp", "rdurable"]
FORMULA_COMPONENTS_REQUIRED = ["food", "edu", "durcons", "nfoodc", "totutil"]

AUDIT_COLUMNS = [
    "country",
    "survey_name",
    "wave",
    "idno",
    "audit_family",
    "evidence_item",
    "source_file",
    "source_variable",
    "public_metadata_label",
    "local_raw_label",
    "metadata_presence",
    "local_raw_presence",
    "local_raw_role",
    "row_count",
    "nonmissing_rows",
    "positive_rows",
    "zero_rows",
    "min_value",
    "p50_value",
    "max_value",
    "unit_evidence",
    "formula_evidence",
    "readiness_status",
    "ready_for_recipe",
    "ready_for_outcome",
    "sdg382_ready",
    "climate_linkage_ready",
    "promotion_status",
    "blocking_reason",
    "next_action",
]

SUMMARY_COLUMNS = ["metric", "value", "interpretation"]


def read_csv_dicts(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def metric_value(rows: list[dict[str, str]], metric: str, default: str = "0") -> str:
    return next((row.get("value", default) for row in rows if row.get("metric") == metric), default)


def fmt(value: Any) -> str:
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


def clean_text(value: Any) -> str:
    if value is None:
        return ""
    try:
        if pd.isna(value):
            return ""
    except TypeError:
        pass
    return " ".join(str(value).split()).encode("ascii", "replace").decode("ascii")


def metadata_variable_name(row: dict[str, str]) -> str:
    return row.get("variable_name") or row.get("name") or ""


def metadata_variable_label(row: dict[str, str]) -> str:
    return row.get("variable_label") or row.get("labl") or ""


def metadata_rows_by_variable() -> dict[str, dict[str, str]]:
    rows = {}
    for row in read_csv_dicts(METADATA_VARIABLE_CATALOG):
        if row.get("idno") != IDNO:
            continue
        if (row.get("file_name") or "").lower() != "poverty":
            continue
        name = metadata_variable_name(row).lower()
        if name:
            rows[name] = row
    return rows


def read_poverty() -> tuple[pd.DataFrame, dict[str, str]]:
    if pyreadstat is None:
        raise RuntimeError("pyreadstat is not available")
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        df, meta = pyreadstat.read_sav(str(POVERTY_SAV), apply_value_formats=False)
    labels = dict(zip(getattr(meta, "column_names", []), getattr(meta, "column_labels", [])))
    return df, {name: clean_text(label) for name, label in labels.items()}


def numeric_stats(series: pd.Series | None) -> dict[str, str]:
    if series is None:
        return {
            "nonmissing_rows": "0",
            "positive_rows": "0",
            "zero_rows": "0",
            "min_value": "",
            "p50_value": "",
            "max_value": "",
        }
    valid = pd.to_numeric(series, errors="coerce")
    valid = valid[valid.notna() & (valid != float("inf")) & (valid != float("-inf"))]
    if valid.empty:
        return {
            "nonmissing_rows": "0",
            "positive_rows": "0",
            "zero_rows": "0",
            "min_value": "",
            "p50_value": "",
            "max_value": "",
        }
    return {
        "nonmissing_rows": str(int(valid.notna().sum())),
        "positive_rows": str(int((valid > 0).sum())),
        "zero_rows": str(int((valid == 0).sum())),
        "min_value": fmt(float(valid.min())),
        "p50_value": fmt(float(valid.median())),
        "max_value": fmt(float(valid.max())),
    }


def base_row(audit_family: str, evidence_item: str, source_file: str, source_variable: str) -> dict[str, str]:
    return {
        "country": COUNTRY,
        "survey_name": SURVEY_NAME,
        "wave": WAVE,
        "idno": IDNO,
        "audit_family": audit_family,
        "evidence_item": evidence_item,
        "source_file": source_file,
        "source_variable": source_variable,
        "public_metadata_label": "",
        "local_raw_label": "",
        "metadata_presence": "0",
        "local_raw_presence": "0",
        "local_raw_role": "",
        "row_count": "0",
        "nonmissing_rows": "0",
        "positive_rows": "0",
        "zero_rows": "0",
        "min_value": "",
        "p50_value": "",
        "max_value": "",
        "unit_evidence": "",
        "formula_evidence": "",
        "readiness_status": "blocked_not_run",
        "ready_for_recipe": "0",
        "ready_for_outcome": "0",
        "sdg382_ready": "0",
        "climate_linkage_ready": "0",
        "promotion_status": NO_PROMOTION,
        "blocking_reason": (
            "Audit-only crosswalk evidence. It does not verify the official aggregate construction code, "
            "period, price basis, PPP/SPL/CPI treatment, OOP numerator annualization, household timing, or climate-ready geography."
        ),
        "next_action": (
            "Use this as a denominator documentation gap list before any harmonization recipe, CHE, SDG 3.8.2, "
            "or climate-linked outcome promotion."
        ),
    }


def build_rows() -> tuple[list[dict[str, str]], dict[str, Any]]:
    poverty, local_labels = read_poverty()
    local_columns = set(poverty.columns)
    metadata = metadata_rows_by_variable()
    rows: list[dict[str, str]] = []

    for variable in METADATA_AGGREGATE_VARIABLES:
        metadata_row = metadata.get(variable, {})
        metadata_label = clean_text(metadata_variable_label(metadata_row))
        local_present = variable in local_columns
        row = base_row(
            "metadata_aggregate_crosswalk",
            "public_metadata_aggregate_variable_local_raw_check",
            "metadata_variable_catalog.csv;poverty.sav",
            variable,
        )
        row.update(
            {
                "public_metadata_label": metadata_label,
                "local_raw_label": local_labels.get(variable, ""),
                "metadata_presence": "1" if metadata_row else "0",
                "local_raw_presence": "1" if local_present else "0",
                "local_raw_role": "household_total_candidate" if variable == "totcons" and local_present else ("not_available_in_local_poverty_sav" if not local_present else "local_raw_column"),
                "row_count": str(len(poverty)) if local_present else "0",
                **numeric_stats(poverty[variable] if local_present else None),
                "unit_evidence": (
                    "Public metadata label states old lek/new lek scaling."
                    if "old lek" in metadata_label.lower()
                    else "No old-lek unit text found in the public metadata label for this variable."
                ),
                "formula_evidence": (
                    metadata_label
                    if "sum of" in metadata_label.lower() or variable.startswith("totcons")
                    else "Component label only; no complete local reconstruction recipe."
                ),
                "readiness_status": (
                    "local_totcons_available_but_formula_components_absent"
                    if variable == "totcons" and local_present
                    else "public_metadata_variable_absent_from_local_raw_extract"
                    if not local_present
                    else "local_metadata_variable_seen_not_recipe_ready"
                ),
                "blocking_reason": (
                    "`totcons` is present locally and positive, but its public formula components and `totcons05` are not "
                    "available in the local poverty extract, so the aggregate cannot be independently reconstructed or variant-checked here."
                    if variable == "totcons" and local_present
                    else "The public metadata variable is not present in the local poverty.sav extract, so the documented aggregate formula cannot be reconstructed from local columns."
                    if not local_present
                    else "The local column exists, but this crosswalk alone does not document final denominator period, price basis, or SDG 3.8.2 treatment."
                ),
                "next_action": (
                    "Locate official aggregate construction documentation/code and determine whether `totcons` or `totcons05` is the intended denominator variant."
                    if variable.startswith("totcons")
                    else "Resolve why this public metadata aggregate/component is absent from the local extract before using the aggregate formula."
                ),
            }
        )
        rows.append(row)

    for variable in LOCAL_PER_CAPITA_COMPONENTS:
        metadata_row = metadata.get(variable, {})
        row = base_row(
            "local_per_capita_aggregate",
            "local_per_capita_component_column",
            "poverty.sav;metadata_variable_catalog.csv",
            variable,
        )
        row.update(
            {
                "public_metadata_label": clean_text(metadata_variable_label(metadata_row)),
                "local_raw_label": local_labels.get(variable, ""),
                "metadata_presence": "1" if metadata_row else "0",
                "local_raw_presence": "1" if variable in local_columns else "0",
                "local_raw_role": "per_capita_diagnostic_component",
                "row_count": str(len(poverty)) if variable in local_columns else "0",
                **numeric_stats(poverty[variable] if variable in local_columns else None),
                "unit_evidence": "Local raw label is per-capita; it does not independently document household-total currency or period.",
                "formula_evidence": "Useful as a scale/plausibility diagnostic but not a substitute for the missing aggregate construction recipe.",
                "readiness_status": "local_per_capita_component_seen_not_household_denominator",
                "blocking_reason": "Per-capita components cannot be promoted to CHE/SDG denominators without documented conversion to the household-total denominator and period.",
                "next_action": "Keep these as diagnostics while searching for the official total-consumption aggregate construction note/code.",
            }
        )
        rows.append(row)

    unit_period_summary = read_csv_dicts(UNIT_PERIOD_SUMMARY_PATH)
    row = base_row(
        "upstream_blocker_crosscheck",
        "unit_period_audit_fail_closed_status",
        "result/alb2005_consumption_oop_unit_period_summary.csv",
        "current_decision",
    )
    row.update(
        {
            "metadata_presence": "1" if unit_period_summary else "0",
            "local_raw_presence": "1" if POVERTY_SAV.exists() else "0",
            "row_count": "1",
            "unit_evidence": f"upstream_old_lek_metadata_rows={metric_value(unit_period_summary, 'alb2005_consumption_oop_unit_period_metadata_old_lek_rows_observed')}",
            "formula_evidence": f"upstream_decision={metric_value(unit_period_summary, 'alb2005_consumption_oop_unit_period_current_decision', 'missing')}",
            "readiness_status": "upstream_unit_period_audit_remains_fail_closed",
            "blocking_reason": "The upstream unit-period audit promotes zero rows to SDG, recipe, outcome, or climate linkage readiness.",
            "next_action": "Resolve aggregate recipe, unit/period, OOP annualization, and SDG discretionary-budget inputs before promotion.",
        }
    )
    rows.append(row)

    present_metadata = [row for row in rows if row["audit_family"] == "metadata_aggregate_crosswalk" and row["metadata_presence"] == "1"]
    present_in_local = [row for row in present_metadata if row["local_raw_presence"] == "1"]
    absent_from_local = [row for row in present_metadata if row["local_raw_presence"] != "1"]
    formula_reconstructable = all(component in local_columns for component in FORMULA_COMPONENTS_REQUIRED)
    diagnostics = {
        "local_poverty_columns": len(poverty.columns),
        "metadata_rows": len(present_metadata),
        "metadata_old_lek_rows": sum(1 for row in present_metadata if "old lek" in row["public_metadata_label"].lower()),
        "metadata_present_in_local_rows": len(present_in_local),
        "metadata_absent_from_local_rows": len(absent_from_local),
        "local_per_capita_component_rows": sum(1 for row in rows if row["audit_family"] == "local_per_capita_aggregate" and row["local_raw_presence"] == "1"),
        "totcons_positive_rows": next((row["positive_rows"] for row in rows if row["source_variable"] == "totcons"), "0"),
        "totcons05_local_rows": sum(1 for row in rows if row["source_variable"] == "totcons05" and row["local_raw_presence"] == "1"),
        "component_formula_reconstructable_rows": 1 if formula_reconstructable else 0,
    }
    return rows, diagnostics


def summary_row(metric: str, value: Any, interpretation: str) -> dict[str, str]:
    return {"metric": metric, "value": fmt(value), "interpretation": interpretation}


def build_summary(rows: list[dict[str, str]], diagnostics: dict[str, Any]) -> list[dict[str, str]]:
    return [
        summary_row("alb2005_consumption_aggregate_crosswalk_rows", len(rows), "Rows in the ALB_2005 consumption aggregate metadata crosswalk audit."),
        summary_row("alb2005_consumption_aggregate_crosswalk_metadata_rows", diagnostics["metadata_rows"], "Public metadata aggregate/component variables checked against local poverty.sav."),
        summary_row("alb2005_consumption_aggregate_crosswalk_metadata_old_lek_rows", diagnostics["metadata_old_lek_rows"], "Checked public metadata aggregate/component labels mentioning old lek."),
        summary_row("alb2005_consumption_aggregate_crosswalk_local_poverty_columns", diagnostics["local_poverty_columns"], "Columns exposed by local ALB_2005 poverty.sav."),
        summary_row("alb2005_consumption_aggregate_crosswalk_metadata_variables_present_in_local_raw_rows", diagnostics["metadata_present_in_local_rows"], "Checked public metadata aggregate/component variables present in local poverty.sav."),
        summary_row("alb2005_consumption_aggregate_crosswalk_metadata_variables_absent_from_local_raw_rows", diagnostics["metadata_absent_from_local_rows"], "Checked public metadata aggregate/component variables absent from local poverty.sav."),
        summary_row("alb2005_consumption_aggregate_crosswalk_local_per_capita_component_rows", diagnostics["local_per_capita_component_rows"], "Local per-capita component variables available for diagnostics only."),
        summary_row("alb2005_consumption_aggregate_crosswalk_totcons_positive_rows", diagnostics["totcons_positive_rows"], "Positive local `totcons` rows in poverty.sav."),
        summary_row("alb2005_consumption_aggregate_crosswalk_totcons05_local_rows", diagnostics["totcons05_local_rows"], "Local `totcons05` rows available in poverty.sav; should remain zero in current extract."),
        summary_row("alb2005_consumption_aggregate_crosswalk_component_formula_reconstructable_rows", diagnostics["component_formula_reconstructable_rows"], "Rows indicating whether required public-metadata formula components are all present locally; should remain zero."),
        summary_row("alb2005_consumption_aggregate_crosswalk_sdg382_ready_rows", 0, "Rows promoted to SDG 3.8.2 denominator readiness by this audit; intentionally zero."),
        summary_row("alb2005_consumption_aggregate_crosswalk_recipe_ready_rows", 0, "Rows promoted to a harmonization recipe by this audit; intentionally zero."),
        summary_row("alb2005_consumption_aggregate_crosswalk_outcome_ready_rows", 0, "Rows promoted to outcome construction by this audit; intentionally zero."),
        summary_row("alb2005_consumption_aggregate_crosswalk_climate_linkage_ready_rows", 0, "Rows promoted to climate linkage by this audit; intentionally zero."),
        summary_row("alb2005_consumption_aggregate_crosswalk_current_decision", DECISION, "Current fail-closed decision for ALB_2005 aggregate metadata/local raw crosswalk evidence."),
    ]


def markdown_rows(rows: list[dict[str, str]], columns: list[str], limit: int = 30) -> str:
    lines = ["| " + " | ".join(columns) + " |", "|" + "|".join("---" for _ in columns) + "|"]
    for row in rows[:limit]:
        values = []
        for column in columns:
            value = (row.get(column, "") or "").replace("|", "/")
            if len(value) > 150:
                value = value[:147] + "..."
            values.append(value)
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines)


def write_report(rows: list[dict[str, str]], summary: list[dict[str, str]]) -> None:
    summary_table = "\n".join(f"| {row['metric']} | {row['value']} | {row['interpretation']} |" for row in summary)
    report = f"""# ALB_2005 Consumption Aggregate Metadata Crosswalk Audit

Status: fail-closed metadata/local-raw crosswalk. This audit compares public metadata aggregate/component variables for ALB_2005 `poverty` with the variables actually exposed by local `poverty.sav`. It does not write `data/`, does not construct CHE/SDG outcomes, and does not promote any row to harmonization, outcome construction, SDG 3.8.2, or climate linkage.

## Bottom Line

- Public metadata lists old-lek aggregate/component variables including `food`, `edu`, `durcons`, `nfoodc`, `nfood05`, `totutil`, `totutil05`, `totcons`, and `totcons05`.
- Local `poverty.sav` exposes `totcons`, `rcons`, and per-capita components, but the checked public-metadata formula components and `totcons05` are absent from this local extract.
- `totcons` is positive locally, but the local file cannot independently reconstruct or variant-check the documented formula from public metadata.
- Local per-capita fields (`rcons`, `rfood`, `rnfood`, `rutility`, `reduexp`, `rdurable`) are useful diagnostics only; they are not a documented household-total denominator recipe.
- SDG 3.8.2, recipe-ready, outcome-ready, and climate-linkage-ready rows from this audit: 0.
- Current decision: `{DECISION}`.

## Summary

| Metric | Value | Interpretation |
|---|---:|---|
{summary_table}

## Crosswalk Rows

{markdown_rows(rows, ['audit_family', 'source_variable', 'metadata_presence', 'local_raw_presence', 'local_raw_label', 'nonmissing_rows', 'positive_rows', 'readiness_status'], 30)}

## Interpretation

- The old-lek metadata evidence supports manual review but is not enough to build financial-protection outcomes.
- The aggregate formula cannot be locally reconstructed from the current `poverty.sav` extract because key public-metadata components are missing locally.
- The `totcons05` variant is public-metadata-visible but not locally available, so denominator variant choice remains unresolved.
- SDG 3.8.2 remains blocked because the discretionary-budget denominator still needs verified total-consumption scope/period, poverty-line treatment, PPP/CPI alignment, and OOP numerator annualization.
- Climate-linked analysis remains independently blocked by missing verified household interview timing and climate-ready geography.

## Machine-Readable Outputs

- `temp/alb2005_consumption_aggregate_metadata_crosswalk_audit.csv`
- `result/alb2005_consumption_aggregate_metadata_crosswalk_summary.csv`
"""
    REPORT_PATH.write_text(report, encoding="utf-8")


def main() -> None:
    ensure_dirs()
    rows, diagnostics = build_rows()
    summary = build_summary(rows, diagnostics)
    write_csv(AUDIT_PATH, rows, AUDIT_COLUMNS)
    write_csv(SUMMARY_PATH, summary, SUMMARY_COLUMNS)
    write_report(rows, summary)
    append_log(TEMP_DIR / "audit_log.md", f"Built ALB_2005 aggregate metadata crosswalk rows={len(rows)} decision={DECISION}.")
    print(f"ALB_2005 aggregate metadata crosswalk rows={len(rows)} decision={DECISION}.")


if __name__ == "__main__":
    main()
