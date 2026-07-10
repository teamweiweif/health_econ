from __future__ import annotations

import csv
from typing import Any

from common import REPORT_DIR, RESULT_DIR, TEMP_DIR, append_log, ensure_dirs, write_csv


IDNO = "MWI_2004_IHS-II_v01_M"
COUNTRY = "Malawi"
WAVE = "2004-2005"

PARAMETER_AUDIT_SUMMARY_PATH = RESULT_DIR / "mwi2004_sdg382_discretionary_budget_parameter_summary.csv"
LEDGER_PATH = RESULT_DIR / "mwi2004_sdg382_external_parameter_source_ledger.csv"
SUMMARY_PATH = RESULT_DIR / "mwi2004_sdg382_external_parameter_candidate_summary.csv"
REPORT_PATH = REPORT_DIR / "mwi2004_sdg382_external_parameter_source_ledger.md"

WORLD_BANK_API_BASE = "https://api.worldbank.org/v2/country/MWI/indicator"
SOURCE_CAPTURE_DATE = "2026-07-10"

PPP_PRIVATE_2017 = 249.104888916016
PPP_GDP_2017 = 262.308654785156
CPI_2004 = 55.6247640619101
CPI_2017 = 340.242124547702
OFFICIAL_IPL_2017_PPP = 2.15
OFFICIAL_RELATIVE_SPL_INTERCEPT_2017_PPP = 1.15
OFFICIAL_RELATIVE_SPL_SHARE = 0.50
OFFICIAL_SDG382_THRESHOLD = 0.40

LEDGER_COLUMNS = [
    "parameter",
    "value",
    "unit",
    "source",
    "source_url",
    "capture_date",
    "acceptance_status",
    "use_in_candidate_bridge",
    "remaining_blocker",
]
SUMMARY_COLUMNS = ["metric", "value", "interpretation"]


def clean(value: Any) -> str:
    if value is None:
        return ""
    return " ".join(str(value).split())


def fmt(value: Any, digits: int = 8) -> str:
    try:
        return f"{float(value):.{digits}g}"
    except (TypeError, ValueError):
        return clean(value)


def read_csv_dicts(path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def summary_value(rows: list[dict[str, str]], metric: str, default: str = "") -> str:
    for row in rows:
        if clean(row.get("metric")) == metric:
            return clean(row.get("value")) or default
    return default


def build_outputs() -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    upstream = read_csv_dicts(PARAMETER_AUDIT_SUMMARY_PATH)
    median_excluding_oop_raw = float(summary_value(upstream, "weighted_median_daily_consumption_excluding_oop_pc_raw", "nan"))
    internal_rows = summary_value(upstream, "household_rows_with_internal_sdg382_inputs", "0")
    positive_oop_rows = summary_value(upstream, "positive_oop_household_rows", "0")

    cpi_ratio_2017_to_2004 = CPI_2017 / CPI_2004
    median_excluding_oop_2017_ppp_private = median_excluding_oop_raw * cpi_ratio_2017_to_2004 / PPP_PRIVATE_2017
    relative_spl_2017_ppp = OFFICIAL_RELATIVE_SPL_INTERCEPT_2017_PPP + OFFICIAL_RELATIVE_SPL_SHARE * median_excluding_oop_2017_ppp_private
    candidate_spl_2017_ppp = max(OFFICIAL_IPL_2017_PPP, relative_spl_2017_ppp)
    candidate_spl_daily_raw_2004_mwk = candidate_spl_2017_ppp * PPP_PRIVATE_2017 / cpi_ratio_2017_to_2004

    ledger_rows = [
        {
            "parameter": "wdi_ppp_private_consumption_2017",
            "value": fmt(PPP_PRIVATE_2017, 12),
            "unit": "MWK per 2017 international dollar",
            "source": "World Bank WDI indicator PA.NUS.PRVT.PP",
            "source_url": f"{WORLD_BANK_API_BASE}/PA.NUS.PRVT.PP?format=json&date=2017&per_page=1000",
            "capture_date": SOURCE_CAPTURE_DATE,
            "acceptance_status": "candidate_preferred_not_final",
            "use_in_candidate_bridge": "1",
            "remaining_blocker": "Confirm this is the correct PPP concept for the official SDG 3.8.2 household consumption/income denominator.",
        },
        {
            "parameter": "wdi_ppp_gdp_2017_backup",
            "value": fmt(PPP_GDP_2017, 12),
            "unit": "MWK per 2017 international dollar",
            "source": "World Bank WDI indicator PA.NUS.PPP",
            "source_url": f"{WORLD_BANK_API_BASE}/PA.NUS.PPP?format=json&date=2017&per_page=1000",
            "capture_date": SOURCE_CAPTURE_DATE,
            "acceptance_status": "backup_not_selected",
            "use_in_candidate_bridge": "0",
            "remaining_blocker": "GDP PPP is kept only as a contrast; private consumption PPP is the preferred candidate for household welfare.",
        },
        {
            "parameter": "wdi_cpi_2004",
            "value": fmt(CPI_2004, 12),
            "unit": "CPI index, 2010=100",
            "source": "World Bank WDI indicator FP.CPI.TOTL",
            "source_url": f"{WORLD_BANK_API_BASE}/FP.CPI.TOTL?format=json&date=2004:2017&per_page=1000",
            "capture_date": SOURCE_CAPTURE_DATE,
            "acceptance_status": "candidate_not_final",
            "use_in_candidate_bridge": "1",
            "remaining_blocker": "Annual CPI 2004 may not exactly match the survey's February/March 2004 real-currency base.",
        },
        {
            "parameter": "wdi_cpi_2017",
            "value": fmt(CPI_2017, 12),
            "unit": "CPI index, 2010=100",
            "source": "World Bank WDI indicator FP.CPI.TOTL",
            "source_url": f"{WORLD_BANK_API_BASE}/FP.CPI.TOTL?format=json&date=2004:2017&per_page=1000",
            "capture_date": SOURCE_CAPTURE_DATE,
            "acceptance_status": "candidate_not_final",
            "use_in_candidate_bridge": "1",
            "remaining_blocker": "Annual CPI bridge still needs reconciliation with the survey deflator and real-currency base.",
        },
        {
            "parameter": "candidate_cpi_ratio_2017_to_2004",
            "value": fmt(cpi_ratio_2017_to_2004, 12),
            "unit": "ratio",
            "source": "derived from WDI FP.CPI.TOTL 2017 / 2004",
            "source_url": f"{WORLD_BANK_API_BASE}/FP.CPI.TOTL?format=json&date=2004:2017&per_page=1000",
            "capture_date": SOURCE_CAPTURE_DATE,
            "acceptance_status": "candidate_not_final",
            "use_in_candidate_bridge": "1",
            "remaining_blocker": "Use only as a candidate bridge until monthly/base-period consistency is checked.",
        },
        {
            "parameter": "official_ipl_2017_ppp",
            "value": fmt(OFFICIAL_IPL_2017_PPP, 12),
            "unit": "2017 PPP international dollars per person per day",
            "source": "UNSD SDG 3.8.2 metadata",
            "source_url": "https://unstats.un.org/sdgs/metadata/files/Metadata-03-08-02.pdf",
            "capture_date": SOURCE_CAPTURE_DATE,
            "acceptance_status": "official_formula_input",
            "use_in_candidate_bridge": "1",
            "remaining_blocker": "Formula input is official, but Malawi local-currency conversion is not final.",
        },
        {
            "parameter": "candidate_relative_spl_2017_ppp",
            "value": fmt(relative_spl_2017_ppp, 12),
            "unit": "2017 PPP international dollars per person per day",
            "source": "1.15 + 0.50 * median consumption/income excluding OOP",
            "source_url": "result/mwi2004_sdg382_discretionary_budget_parameter_summary.csv",
            "capture_date": SOURCE_CAPTURE_DATE,
            "acceptance_status": "candidate_not_final",
            "use_in_candidate_bridge": "1",
            "remaining_blocker": "Median is converted with the candidate annual CPI bridge; final SPL requires accepted PPP/CPI policy.",
        },
        {
            "parameter": "candidate_spl_2017_ppp",
            "value": fmt(candidate_spl_2017_ppp, 12),
            "unit": "2017 PPP international dollars per person per day",
            "source": "max(2.15, candidate relative SPL)",
            "source_url": "result/mwi2004_sdg382_external_parameter_source_ledger.csv",
            "capture_date": SOURCE_CAPTURE_DATE,
            "acceptance_status": "candidate_not_final",
            "use_in_candidate_bridge": "1",
            "remaining_blocker": "Local-currency SPL remains candidate because the CPI/base-period bridge is not accepted.",
        },
        {
            "parameter": "candidate_spl_daily_raw_2004_mwk",
            "value": fmt(candidate_spl_daily_raw_2004_mwk, 12),
            "unit": "candidate real 2004 MWK per person per day",
            "source": "candidate_spl_2017_ppp * PPP private 2017 / CPI ratio",
            "source_url": "result/mwi2004_sdg382_external_parameter_source_ledger.csv",
            "capture_date": SOURCE_CAPTURE_DATE,
            "acceptance_status": "candidate_not_final",
            "use_in_candidate_bridge": "0",
            "remaining_blocker": "Do not use for final SDG 3.8.2 classification until the bridge policy and denominator rule are accepted.",
        },
    ]
    summary_rows = [
        {"metric": "country_wave", "value": IDNO, "interpretation": "Country-wave covered by the SDG 3.8.2 external parameter ledger."},
        {"metric": "source_capture_date", "value": SOURCE_CAPTURE_DATE, "interpretation": "Date these official parameter candidates were captured for the project ledger."},
        {"metric": "parameter_rows", "value": str(len(ledger_rows)), "interpretation": "External and derived parameter rows in the source ledger."},
        {"metric": "household_rows_with_internal_sdg382_inputs", "value": internal_rows, "interpretation": "Internal Malawi raw rows inherited from the SDG parameter audit."},
        {"metric": "positive_oop_household_rows", "value": positive_oop_rows, "interpretation": "Households with positive OOP in the internal SDG frame."},
        {"metric": "wdi_ppp_private_consumption_2017", "value": fmt(PPP_PRIVATE_2017, 12), "interpretation": "Candidate private consumption PPP from World Bank WDI PA.NUS.PRVT.PP."},
        {"metric": "wdi_cpi_2004", "value": fmt(CPI_2004, 12), "interpretation": "Candidate CPI 2004 from World Bank WDI FP.CPI.TOTL."},
        {"metric": "wdi_cpi_2017", "value": fmt(CPI_2017, 12), "interpretation": "Candidate CPI 2017 from World Bank WDI FP.CPI.TOTL."},
        {"metric": "candidate_cpi_ratio_2017_to_2004", "value": fmt(cpi_ratio_2017_to_2004, 12), "interpretation": "Annual CPI bridge candidate; not accepted as final."},
        {"metric": "median_excluding_oop_2017_ppp_private_candidate", "value": fmt(median_excluding_oop_2017_ppp_private, 12), "interpretation": "Converted median using candidate annual CPI bridge and private consumption PPP."},
        {"metric": "candidate_relative_spl_2017_ppp", "value": fmt(relative_spl_2017_ppp, 12), "interpretation": "Relative SPL candidate from the current official formula."},
        {"metric": "candidate_spl_2017_ppp", "value": fmt(candidate_spl_2017_ppp, 12), "interpretation": "Candidate SPL after max with the 2017 IPL."},
        {"metric": "candidate_spl_daily_raw_2004_mwk", "value": fmt(candidate_spl_daily_raw_2004_mwk, 12), "interpretation": "Candidate SPL converted back to real 2004 MWK per person per day."},
        {"metric": "private_consumption_ppp_source_verified", "value": "1", "interpretation": "World Bank API value captured, but concept still needs final acceptance."},
        {"metric": "annual_cpi_bridge_source_verified", "value": "1", "interpretation": "World Bank CPI values captured, but annual bridge remains candidate."},
        {"metric": "external_parameter_bridge_accepted", "value": "0", "interpretation": "PPP/CPI bridge is not accepted for final SDG 3.8.2 classification."},
        {"metric": "sdg382_ready", "value": "0", "interpretation": "External parameter source ledger does not open the SDG 3.8.2 gate."},
        {"metric": "data_write_gate_status", "value": "closed", "interpretation": "This artifact writes no promoted household-level data."},
        {"metric": "modeling_gate_status", "value": "blocked", "interpretation": "No predictive, reduced-form, causal ML, or policy learning is opened."},
    ]
    return ledger_rows, summary_rows


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


def write_report(ledger_rows: list[dict[str, str]], summary_rows: list[dict[str, str]]) -> None:
    REPORT_PATH.write_text(
        f"""# Malawi 2004 SDG 3.8.2 External Parameter Source Ledger

Dataset: `{IDNO}` - {COUNTRY} {WAVE}

This artifact records official external parameter candidates for the Malawi
2004 SDG 3.8.2 discretionary-budget denominator. It captures World Bank WDI
PPP/CPI values and derives a candidate local-currency SPL bridge, but it keeps
the SDG gate closed because the annual CPI bridge has not yet been reconciled
with the survey's February/March 2004 real-currency base and the final
discretionary-budget denominator rule has not been accepted.

## Summary

{markdown_table(summary_rows, ['metric', 'value', 'interpretation'], 30)}

## Source Ledger

{markdown_table(ledger_rows, ['parameter', 'value', 'source', 'acceptance_status', 'remaining_blocker'], 30)}

## Gate Decision

The ledger narrows the SDG 3.8.2 blocker from missing external parameters to a
specific unresolved bridge: World Bank 2017 private-consumption PPP and annual
CPI values are captured, but the annual CPI 2004 value is not enough by itself
to accept the survey's February/March 2004 real-currency base. Therefore
`sdg382_ready` remains `0`, `data_write_gate_status` remains `closed`, and
`modeling_gate_status` remains `blocked`.
""",
        encoding="utf-8",
    )


def main() -> None:
    ensure_dirs()
    ledger_rows, summary_rows = build_outputs()
    write_csv(LEDGER_PATH, ledger_rows, LEDGER_COLUMNS)
    write_csv(SUMMARY_PATH, summary_rows, SUMMARY_COLUMNS)
    write_report(ledger_rows, summary_rows)
    append_log(TEMP_DIR / "audit_log.md", f"Built Malawi 2004 SDG 3.8.2 external parameter source ledger rows={len(ledger_rows)}.")
    print(f"Malawi 2004 SDG 3.8.2 external parameter source ledger rows={len(ledger_rows)}.")


if __name__ == "__main__":
    main()
