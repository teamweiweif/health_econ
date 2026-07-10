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

AUDIT_PATH = RESULT_DIR / "mwi2004_sdg382_discretionary_budget_parameter_audit.csv"
SUMMARY_PATH = RESULT_DIR / "mwi2004_sdg382_discretionary_budget_parameter_summary.csv"
REPORT_PATH = REPORT_DIR / "mwi2004_sdg382_discretionary_budget_parameter_audit.md"
HANDOFF_PATH = RAW_DIR / "_MWI2004_SDG382_DISCRETIONARY_BUDGET_PARAMETER_AUDIT.md"

OFFICIAL_METADATA_URL = "https://unstats.un.org/sdgs/metadata/files/Metadata-03-08-02.pdf"
OFFICIAL_METADATA_LAST_UPDATE = "2026-03-27"
OFFICIAL_SERIES = "SH_OOP_XPD_EARNNET40"
OFFICIAL_THRESHOLD = "0.40"

AUDIT_COLUMNS = ["component", "status", "raw_variables_or_source", "aggregate_evidence", "decision", "remaining_blocker"]
SUMMARY_COLUMNS = ["metric", "value", "interpretation"]


def clean(value: Any) -> str:
    if value is None:
        return ""
    return " ".join(str(value).split())


def fmt(value: Any, digits: int = 6) -> str:
    if value is None or pd.isna(value):
        return ""
    try:
        return f"{float(value):.{digits}g}"
    except (TypeError, ValueError):
        return clean(value)


def pct(numerator: float, denominator: float) -> str:
    if denominator == 0:
        return ""
    return f"{100.0 * numerator / denominator:.4f}"


def member_name(zip_path: Path, basename: str) -> str:
    with ZipFile(zip_path) as zf:
        for name in zf.namelist():
            if PurePosixPath(name).name.lower() == basename.lower():
                return name
    raise FileNotFoundError(f"{basename} not found in {zip_path}")


def read_member(zip_path: Path, basename: str, columns: list[str]) -> tuple[pd.DataFrame, dict[str, str]]:
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
        labels = dict(zip(getattr(meta, "column_names", []) or [], getattr(meta, "column_labels", []) or []))
        df, _ = pyreadstat.read_dta(str(raw_path), usecols=usecols)
        return df, {column: clean(labels.get(column)) for column in usecols}
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


def load_financial_frame() -> tuple[pd.DataFrame, dict[str, str]]:
    columns = ["case_id", "hhwght", "hhsize", "rexpagg", "rexp_cat06", "povline", "price_index"]
    df, labels = read_member(ZIP_PATH, "ihs2_pov.dta", columns)
    for column in columns:
        if column in df:
            df[column] = pd.to_numeric(df[column], errors="coerce")
    return df, labels


def build_outputs() -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    df, labels = load_financial_frame()
    universe = df[
        df["case_id"].notna()
        & (df["hhwght"] > 0)
        & (df["hhsize"] > 0)
        & (df["rexpagg"] > 0)
        & df["rexp_cat06"].notna()
    ].copy()
    universe["person_weight"] = universe["hhwght"] * universe["hhsize"]
    universe["consumption_excluding_oop"] = universe["rexpagg"] - universe["rexp_cat06"]
    universe["daily_total_consumption_pc_raw"] = universe["rexpagg"] / universe["hhsize"] / 365.0
    universe["daily_oop_pc_raw"] = universe["rexp_cat06"] / universe["hhsize"] / 365.0
    universe["daily_consumption_excluding_oop_pc_raw"] = universe["consumption_excluding_oop"] / universe["hhsize"] / 365.0
    universe["daily_survey_povline_pc_raw"] = universe["povline"] / 365.0

    rows = int(len(universe))
    positive_oop = int((universe["rexp_cat06"] > 0).sum())
    nonpositive_excluding_oop = int((universe["consumption_excluding_oop"] <= 0).sum())
    povline_rows = int(universe["povline"].notna().sum())
    price_rows = int(universe["price_index"].notna().sum())
    weighted_population = float(universe["person_weight"].sum())
    median_excl = weighted_quantile(universe["daily_consumption_excluding_oop_pc_raw"], universe["person_weight"], 0.5)
    median_total = weighted_quantile(universe["daily_total_consumption_pc_raw"], universe["person_weight"], 0.5)
    median_povline = weighted_quantile(universe["daily_survey_povline_pc_raw"], universe["person_weight"], 0.5)
    price_min = float(universe["price_index"].min())
    price_max = float(universe["price_index"].max())
    survey_povline_min = float(universe["daily_survey_povline_pc_raw"].min())
    survey_povline_max = float(universe["daily_survey_povline_pc_raw"].max())

    audit_rows = [
        {
            "component": "official_indicator_definition",
            "status": "source_checked_current_2026_metadata",
            "raw_variables_or_source": OFFICIAL_METADATA_URL,
            "aggregate_evidence": f"last_update={OFFICIAL_METADATA_LAST_UPDATE}; series={OFFICIAL_SERIES}; threshold={OFFICIAL_THRESHOLD}; denominator=household_discretionary_budget",
            "decision": "use_current_40pct_discretionary_budget_definition_for_sdg382_gate",
            "remaining_blocker": "",
        },
        {
            "component": "oop_health_expenditure",
            "status": "raw_internal_input_complete",
            "raw_variables_or_source": "ihs2_pov.dta rexp_cat06",
            "aggregate_evidence": f"label={labels.get('rexp_cat06', '')}; nonmissing_rows={rows}; positive_oop_rows={positive_oop}; positive_oop_percent={pct(positive_oop, rows)}",
            "decision": "oop_health_input_ready_for_parameterized_sdg382_test",
            "remaining_blocker": "Need final 2017 PPP/CPI/SPL parameterization before SDG 3.8.2 indicator can be accepted.",
        },
        {
            "component": "total_consumption_or_income",
            "status": "raw_internal_input_complete",
            "raw_variables_or_source": "ihs2_pov.dta rexpagg",
            "aggregate_evidence": f"label={labels.get('rexpagg', '')}; positive_total_consumption_rows={rows}; weighted_median_daily_total_pc_raw={fmt(median_total)}",
            "decision": "consumption_welfare_input_ready_for_parameterized_sdg382_test",
            "remaining_blocker": "Confirm real-currency base and 2017 PPP/CPI conversion before final SPL local-currency mapping.",
        },
        {
            "component": "household_size_population_weight",
            "status": "raw_internal_input_complete",
            "raw_variables_or_source": "ihs2_pov.dta hhsize; hhwght",
            "aggregate_evidence": f"hhsize_label={labels.get('hhsize', '')}; hhwght_label={labels.get('hhwght', '')}; analytic_households={rows}; weighted_population={fmt(weighted_population)}",
            "decision": "person_weighting_input_ready_for_aggregate_sdg382_rate_after_parameter_lock",
            "remaining_blocker": "No person-level SDG 3.8.2 rate should be published until the denominator parameter policy is accepted.",
        },
        {
            "component": "consumption_excluding_oop_for_spl_median",
            "status": "raw_internal_derivation_complete",
            "raw_variables_or_source": "rexpagg - rexp_cat06; hhsize; hhwght",
            "aggregate_evidence": f"weighted_median_daily_consumption_excluding_oop_pc_raw={fmt(median_excl)}; nonpositive_excluding_oop_rows={nonpositive_excluding_oop}",
            "decision": "median_component_ready_but_currency_conversion_missing",
            "remaining_blocker": "Need verified conversion from survey real local currency to 2017 PPP international dollars before SPL can be final.",
        },
        {
            "component": "survey_poverty_line_context",
            "status": "diagnostic_context_not_official_spl",
            "raw_variables_or_source": "ihs2_pov.dta povline",
            "aggregate_evidence": f"label={labels.get('povline', '')}; nonmissing_rows={povline_rows}; weighted_median_daily_povline_pc_raw={fmt(median_povline)}; daily_range_raw={fmt(survey_povline_min)}-{fmt(survey_povline_max)}",
            "decision": "use_as_context_only_not_sdg382_spl",
            "remaining_blocker": "Official 2026 SDG 3.8.2 SPL is max(2017 IPL, relative SPL formula), not the survey national poverty line by itself.",
        },
        {
            "component": "survey_price_index_context",
            "status": "diagnostic_context_not_complete_cpi_bridge",
            "raw_variables_or_source": "ihs2_pov.dta price_index",
            "aggregate_evidence": f"label={labels.get('price_index', '')}; nonmissing_rows={price_rows}; observed_range={fmt(price_min)}-{fmt(price_max)}",
            "decision": "use_as_context_only_until_cpi_ppp_bridge_is_documented",
            "remaining_blocker": "Need locked conversion from February/March 2004 real local currency to 2017 PPP terms.",
        },
        {
            "component": "external_2017_ppp_parameter",
            "status": "blocked_external_parameter_not_verified",
            "raw_variables_or_source": "World Bank/ICP 2017 PPP private consumption conversion factor",
            "aggregate_evidence": "not_stored_in_project_artifacts",
            "decision": "sdg382_not_ready",
            "remaining_blocker": "Fetch, source, and freeze the official 2017 PPP conversion factor appropriate for household consumption/income.",
        },
        {
            "component": "external_cpi_or_deflator_bridge",
            "status": "blocked_external_parameter_not_verified",
            "raw_variables_or_source": "CPI or price-deflator bridge from Malawi 2004 survey real-currency base to 2017",
            "aggregate_evidence": "not_stored_in_project_artifacts",
            "decision": "sdg382_not_ready",
            "remaining_blocker": "Fetch, source, and freeze the CPI/deflator bridge consistent with rexpagg/rexp_cat06 real currency base.",
        },
        {
            "component": "official_spl_local_currency",
            "status": "blocked_until_ppp_cpi_policy_locked",
            "raw_variables_or_source": "max(2.15 2017 PPP IPL, 1.15 2017 PPP + 50% median consumption/income excluding OOP)",
            "aggregate_evidence": f"median_excluding_oop_raw_available={fmt(median_excl)}; ppp_verified=0; cpi_bridge_verified=0",
            "decision": "sdg382_not_ready",
            "remaining_blocker": "Cannot compute final SPL in Malawi survey local currency until PPP and CPI/deflator parameters are verified.",
        },
        {
            "component": "sdg382_indicator_final",
            "status": "blocked_external_parameters",
            "raw_variables_or_source": "rexp_cat06; rexpagg; hhsize; hhwght; verified SPL local-currency parameter",
            "aggregate_evidence": "raw_internal_inputs_complete=1; external_ppp_cpi_parameters_verified=0; spl_verified=0",
            "decision": "keep_sdg382_ready_0",
            "remaining_blocker": "Do not mark SDG 3.8.2 ready until current 2026 metadata parameters are frozen and the final population-weighted 40% discretionary-budget indicator is validated.",
        },
    ]
    summary_rows = [
        {"metric": "country_wave", "value": IDNO, "interpretation": "Country-wave covered by the SDG 3.8.2 parameter audit."},
        {"metric": "official_metadata_url", "value": OFFICIAL_METADATA_URL, "interpretation": "Official UNSD SDG metadata PDF used for current indicator definition."},
        {"metric": "official_metadata_last_update", "value": OFFICIAL_METADATA_LAST_UPDATE, "interpretation": "Last update date recorded in the official SDG 3.8.2 metadata."},
        {"metric": "official_sdg382_series", "value": OFFICIAL_SERIES, "interpretation": "Official SDG 3.8.2 series code in the current metadata."},
        {"metric": "official_threshold_discretionary_budget", "value": OFFICIAL_THRESHOLD, "interpretation": "OOP health expenditure threshold over household discretionary budget."},
        {"metric": "household_rows_with_internal_sdg382_inputs", "value": str(rows), "interpretation": "Rows with case_id, positive weight, positive household size, positive total consumption, and nonmissing OOP."},
        {"metric": "positive_oop_household_rows", "value": str(positive_oop), "interpretation": "Households with positive OOP health expenditure; official numerator requires positive OOP."},
        {"metric": "weighted_population_internal_universe", "value": fmt(weighted_population), "interpretation": "Population-weighted denominator before final SDG 3.8.2 parameterization."},
        {"metric": "weighted_median_daily_total_consumption_pc_raw", "value": fmt(median_total), "interpretation": "Diagnostic raw-currency daily per-capita median total consumption."},
        {"metric": "weighted_median_daily_consumption_excluding_oop_pc_raw", "value": fmt(median_excl), "interpretation": "Diagnostic raw-currency median needed for the relative SPL formula after PPP/CPI conversion."},
        {"metric": "survey_povline_rows", "value": str(povline_rows), "interpretation": "Rows with survey poverty-line context; not the final official 2026 SPL by itself."},
        {"metric": "price_index_rows", "value": str(price_rows), "interpretation": "Rows with survey spatial/temporal price index context."},
        {"metric": "raw_internal_sdg382_inputs_complete", "value": "1", "interpretation": "OOP, total consumption, household size, and population weights are present for the internal SDG 3.8.2 frame."},
        {"metric": "external_ppp_cpi_parameters_verified", "value": "0", "interpretation": "Official 2017 PPP and CPI/deflator bridge have not been frozen in project artifacts."},
        {"metric": "spl_local_currency_verified", "value": "0", "interpretation": "Societal poverty line in Malawi survey local currency is not yet accepted."},
        {"metric": "sdg382_ready", "value": "0", "interpretation": "SDG 3.8.2 remains blocked by external parameter and SPL verification."},
        {"metric": "data_write_gate_status", "value": "closed", "interpretation": "This audit writes no promoted data and does not alter the existing promoted Malawi dataset."},
        {"metric": "modeling_gate_status", "value": "blocked", "interpretation": "No predictive, reduced-form, causal ML, or policy learning is opened by this parameter audit."},
    ]
    return audit_rows, summary_rows


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


def write_report(audit_rows: list[dict[str, str]], summary_rows: list[dict[str, str]]) -> None:
    text = f"""# Malawi 2004 SDG 3.8.2 Discretionary-Budget Parameter Audit

Dataset: `{IDNO}` - {COUNTRY} {WAVE}

This artifact updates the Malawi 2004 SDG 3.8.2 gate to the current official
metadata definition: positive household OOP health expenditure exceeding 40% of
household discretionary budget. The discretionary budget is total household
consumption or income minus the societal poverty line (SPL).

It does not construct the final SDG 3.8.2 indicator, does not write `data/`,
and does not open modeling gates. It separates raw internal readiness from the
still-missing external PPP/CPI/SPL parameter lock.

Official metadata source: `{OFFICIAL_METADATA_URL}`; last update:
`{OFFICIAL_METADATA_LAST_UPDATE}`.

## Summary

{markdown_table(summary_rows, ['metric', 'value', 'interpretation'], 30)}

## Audit Rows

{markdown_table(audit_rows, ['component', 'status', 'aggregate_evidence', 'decision', 'remaining_blocker'], 30)}

## Gate Decision

Malawi 2004 has the internal raw ingredients needed to parameterize SDG 3.8.2:
OOP health expenditure, total consumption, household size, and population
weights. It remains fail-closed because the official 2017 PPP conversion, the
CPI/deflator bridge from the survey real-currency base to 2017, and the final
SPL local-currency parameter are not yet verified in project artifacts.
"""
    REPORT_PATH.write_text(text, encoding="utf-8")
    if RAW_DIR.exists():
        HANDOFF_PATH.write_text(
            f"""# Malawi 2004 SDG 3.8.2 Parameter Audit

Generated report: `report/mwi2004_sdg382_discretionary_budget_parameter_audit.md`

This audit writes aggregate metadata only. It does not copy, extract, or
publish raw household rows.
""",
            encoding="utf-8",
        )


def main() -> None:
    ensure_dirs()
    audit_rows, summary_rows = build_outputs()
    write_csv(AUDIT_PATH, audit_rows, AUDIT_COLUMNS)
    write_csv(SUMMARY_PATH, summary_rows, SUMMARY_COLUMNS)
    write_report(audit_rows, summary_rows)
    append_log(TEMP_DIR / "audit_log.md", f"Built Malawi 2004 SDG 3.8.2 discretionary-budget parameter audit rows={len(audit_rows)}.")
    print(f"Malawi 2004 SDG 3.8.2 parameter audit rows={len(audit_rows)}.")


if __name__ == "__main__":
    main()
