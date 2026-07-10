from __future__ import annotations

import csv
import math
import re
from typing import Any

from common import REPORT_DIR, RESULT_DIR, TEMP_DIR, append_log, ensure_dirs, write_csv


IDNO = "MWI_2004_IHS-II_v01_M"
COUNTRY = "Malawi"
WAVE = "2004-2005"

PARAMETER_AUDIT_PATH = RESULT_DIR / "mwi2004_sdg382_discretionary_budget_parameter_audit.csv"
EXTERNAL_LEDGER_PATH = RESULT_DIR / "mwi2004_sdg382_external_parameter_source_ledger.csv"
EXTERNAL_SUMMARY_PATH = RESULT_DIR / "mwi2004_sdg382_external_parameter_candidate_summary.csv"
DENOMINATOR_SUMMARY_PATH = RESULT_DIR / "mwi2004_sdg382_official_denominator_rule_summary.csv"

GATE_PATH = RESULT_DIR / "mwi2004_sdg382_spl_bridge_verification_gate.csv"
SUMMARY_PATH = RESULT_DIR / "mwi2004_sdg382_spl_bridge_verification_gate_summary.csv"
REPORT_PATH = REPORT_DIR / "mwi2004_sdg382_spl_bridge_verification_gate.md"

OFFICIAL_METADATA_URL = "https://unstats.un.org/sdgs/metadata/files/Metadata-03-08-02.pdf"
OFFICIAL_METADATA_LAST_UPDATE = "2026-03-27"
WORLD_BANK_API_REVALIDATION_DATE = "2026-07-10"
PPP_PRIVATE_2017_API_VALUE = 249.104888916016
CPI_2004_API_VALUE = 55.6247640619101
CPI_2017_API_VALUE = 340.242124547702
IPL_2017_PPP = 2.15

GATE_COLUMNS = [
    "component",
    "status",
    "value",
    "source",
    "evidence",
    "decision",
    "remaining_blocker",
]
SUMMARY_COLUMNS = ["metric", "value", "interpretation"]


def read_csv_dicts(path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def clean(value: Any) -> str:
    if value is None:
        return ""
    return " ".join(str(value).split())


def fmt(value: Any, digits: int = 12) -> str:
    try:
        return f"{float(value):.{digits}g}"
    except (TypeError, ValueError):
        return clean(value)


def safe_float(value: Any, default: float = float("nan")) -> float:
    try:
        text = clean(value)
        return float(text) if text else default
    except (TypeError, ValueError):
        return default


def safe_int(value: Any, default: int = 0) -> int:
    try:
        text = clean(value)
        return int(float(text)) if text else default
    except (TypeError, ValueError):
        return default


def summary_value(rows: list[dict[str, str]], metric: str, default: str = "") -> str:
    for row in rows:
        if clean(row.get("metric")) == metric:
            return clean(row.get("value")) or default
    return default


def ledger_value(rows: list[dict[str, str]], parameter: str, default: str = "") -> str:
    for row in rows:
        if clean(row.get("parameter")) == parameter:
            return clean(row.get("value")) or default
    return default


def audit_row(rows: list[dict[str, str]], component: str) -> dict[str, str]:
    for row in rows:
        if clean(row.get("component")) == component:
            return row
    return {}


def extract_number(text: str, key: str, default: float = float("nan")) -> float:
    match = re.search(rf"{re.escape(key)}=([0-9.+\-eE]+)", text)
    if not match:
        return default
    return safe_float(match.group(1), default)


def close_to(left: float, right: float) -> bool:
    return math.isclose(left, right, rel_tol=1e-10, abs_tol=1e-8)


def gate_row(component: str, status: str, value: Any, source: str, evidence: str, decision: str, blocker: str) -> dict[str, str]:
    return {
        "component": component,
        "status": status,
        "value": fmt(value) if isinstance(value, (float, int)) else clean(value),
        "source": source,
        "evidence": evidence,
        "decision": decision,
        "remaining_blocker": blocker,
    }


def build_outputs() -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    parameter_rows = read_csv_dicts(PARAMETER_AUDIT_PATH)
    ledger_rows = read_csv_dicts(EXTERNAL_LEDGER_PATH)
    external_summary = read_csv_dicts(EXTERNAL_SUMMARY_PATH)
    denominator_summary = read_csv_dicts(DENOMINATOR_SUMMARY_PATH)

    ppp_private = safe_float(ledger_value(ledger_rows, "wdi_ppp_private_consumption_2017"))
    cpi_2004 = safe_float(ledger_value(ledger_rows, "wdi_cpi_2004"))
    cpi_2017 = safe_float(ledger_value(ledger_rows, "wdi_cpi_2017"))
    cpi_ratio = safe_float(summary_value(external_summary, "candidate_cpi_ratio_2017_to_2004"))
    relative_spl = safe_float(summary_value(external_summary, "candidate_relative_spl_2017_ppp"))
    spl_2017_ppp = safe_float(summary_value(external_summary, "candidate_spl_2017_ppp"))
    spl_daily_raw = safe_float(summary_value(external_summary, "candidate_spl_daily_raw_2004_mwk"))
    bridge_accepted = summary_value(external_summary, "external_parameter_bridge_accepted", "0")
    official_rule_accepted = summary_value(denominator_summary, "official_denominator_rule_accepted", "0")
    nonpositive_rows = safe_int(summary_value(denominator_summary, "nonpositive_discretionary_budget_rows", "0"))
    official_candidate_rows = safe_int(summary_value(denominator_summary, "official_rule_candidate_sdg382_rows", "0"))
    official_candidate_rate = summary_value(denominator_summary, "official_rule_candidate_sdg382_weighted_rate", "")

    povline_context = audit_row(parameter_rows, "survey_poverty_line_context")
    price_context = audit_row(parameter_rows, "survey_price_index_context")
    povline_daily = extract_number(clean(povline_context.get("aggregate_evidence")), "weighted_median_daily_povline_pc_raw")
    price_index_range = re.search(r"observed_range=([^;]+)", clean(price_context.get("aggregate_evidence")))
    price_index_range_text = price_index_range.group(1) if price_index_range else ""
    price_source = clean(price_context.get("raw_variables_or_source"))
    price_evidence = clean(price_context.get("aggregate_evidence"))
    base_label_has_month = "February/March 2004" in price_evidence or "February/March 2004" in clean(price_context.get("decision"))

    ppp_match = close_to(ppp_private, PPP_PRIVATE_2017_API_VALUE)
    cpi_2004_match = close_to(cpi_2004, CPI_2004_API_VALUE)
    cpi_2017_match = close_to(cpi_2017, CPI_2017_API_VALUE)
    source_values_revalidated = ppp_match and cpi_2004_match and cpi_2017_match
    annual_cpi_ratio_recomputed = cpi_2017 / cpi_2004 if cpi_2004 else float("nan")
    ratio_match = close_to(cpi_ratio, annual_cpi_ratio_recomputed)
    spl_recomputed = spl_2017_ppp * ppp_private / annual_cpi_ratio_recomputed if annual_cpi_ratio_recomputed else float("nan")
    spl_match = close_to(spl_daily_raw, spl_recomputed)
    ipl_binds = spl_2017_ppp == IPL_2017_PPP and relative_spl < IPL_2017_PPP
    spl_to_povline_ratio = spl_daily_raw / povline_daily if povline_daily else float("nan")
    annual_cpi_bridge_accepted = source_values_revalidated and ratio_match and spl_match and not base_label_has_month

    rows = [
        gate_row(
            "official_sdg382_formula",
            "verified_current_metadata",
            "SPL=max(2.15, 1.15 + 0.50 * median excluding OOP), 2017 PPP per capita daily",
            OFFICIAL_METADATA_URL,
            f"metadata_last_update={OFFICIAL_METADATA_LAST_UPDATE}; official_denominator_rule_accepted={official_rule_accepted}",
            "official_formula_verified",
            "",
        ),
        gate_row(
            "world_bank_ppp_private_consumption_2017",
            "source_value_revalidated" if ppp_match else "source_value_mismatch",
            ppp_private,
            "https://api.worldbank.org/v2/country/MWI/indicator/PA.NUS.PRVT.PP?format=json&date=2017&per_page=1000",
            f"api_revalidation_date={WORLD_BANK_API_REVALIDATION_DATE}; expected_api_value={fmt(PPP_PRIVATE_2017_API_VALUE)}; ledger_match={int(ppp_match)}",
            "use_as_candidate_ppp_concept",
            "PPP concept still remains tied to the bridge policy; source value itself is verified." if ppp_match else "Refresh World Bank PPP value before using this bridge.",
        ),
        gate_row(
            "world_bank_cpi_annual_values",
            "source_values_revalidated" if cpi_2004_match and cpi_2017_match else "source_value_mismatch",
            f"cpi_2004={fmt(cpi_2004)}; cpi_2017={fmt(cpi_2017)}",
            "https://api.worldbank.org/v2/country/MWI/indicator/FP.CPI.TOTL?format=json&date=2004:2017&per_page=1000",
            f"api_revalidation_date={WORLD_BANK_API_REVALIDATION_DATE}; expected_2004={fmt(CPI_2004_API_VALUE)}; expected_2017={fmt(CPI_2017_API_VALUE)}; match_2004={int(cpi_2004_match)}; match_2017={int(cpi_2017_match)}",
            "annual_cpi_values_verified",
            "Annual CPI values are verified, but annual CPI does not by itself verify the survey real-currency base.",
        ),
        gate_row(
            "candidate_cpi_ratio",
            "formula_recomputed" if ratio_match else "formula_mismatch",
            cpi_ratio,
            "World Bank FP.CPI.TOTL 2017 / 2004",
            f"recomputed_ratio={fmt(annual_cpi_ratio_recomputed)}; ratio_match={int(ratio_match)}",
            "candidate_ratio_reproducible",
            "Reproducible ratio is still only a candidate because the survey deflator base is February/March 2004.",
        ),
        gate_row(
            "candidate_spl_2017_ppp",
            "ipl_binds_relative_formula" if ipl_binds else "relative_formula_binds_or_needs_review",
            spl_2017_ppp,
            "UNSD SDG 3.8.2 SPL formula plus Malawi median excluding OOP",
            f"relative_spl_2017_ppp={fmt(relative_spl)}; ipl_2017_ppp={fmt(IPL_2017_PPP)}; ipl_binds={int(ipl_binds)}",
            "candidate_spl_2017_ppp_reproducible",
            "2017 PPP SPL is reproducible, but local-currency conversion remains candidate.",
        ),
        gate_row(
            "candidate_spl_local_currency",
            "formula_recomputed_candidate_not_accepted" if spl_match else "formula_mismatch",
            spl_daily_raw,
            "candidate_spl_2017_ppp * 2017 private consumption PPP / annual CPI ratio",
            f"recomputed_daily_raw_mwk={fmt(spl_recomputed)}; spl_match={int(spl_match)}; survey_povline_daily_raw_mwk={fmt(povline_daily)}; spl_to_survey_povline_ratio={fmt(spl_to_povline_ratio)}",
            "candidate_local_currency_spl_not_accepted",
            "The local-currency SPL depends on the annual CPI bridge; do not promote SDG 3.8.2 yet.",
        ),
        gate_row(
            "survey_real_currency_base",
            "base_period_mismatch_blocks_bridge" if base_label_has_month else "base_period_needs_review",
            price_index_range_text,
            price_source,
            price_evidence,
            "annual_cpi_bridge_not_accepted",
            "The raw survey price index is explicitly based at national February/March 2004; annual CPI 2004 is too coarse to accept as the final bridge without a documented base-period reconciliation.",
        ),
        gate_row(
            "candidate_classification_scale",
            "aggregate_stress_test_only",
            f"official_rule_candidate_rows={official_candidate_rows}",
            "result/mwi2004_sdg382_official_denominator_rule_summary.csv",
            f"nonpositive_discretionary_rows={nonpositive_rows}; official_rule_candidate_weighted_rate={official_candidate_rate}",
            "do_not_write_household_sdg382",
            "Candidate classification is sensitive to the unaccepted local-currency SPL bridge.",
        ),
        gate_row(
            "final_bridge_gate",
            "fail_closed",
            "sdg382_ready=0",
            "this verifier",
            f"source_values_revalidated={int(source_values_revalidated)}; annual_cpi_ratio_recomputed={int(ratio_match)}; local_spl_recomputed={int(spl_match)}; survey_base_period_bridge_accepted={int(annual_cpi_bridge_accepted)}; external_parameter_bridge_accepted={bridge_accepted}",
            "block_sdg382_until_survey_base_period_bridge_is_documented",
            "Need a documented conversion from the survey's February/March 2004 real MWK base to 2017 PPP terms, or an official accepted Malawi SDG 3.8.2 production source.",
        ),
    ]

    summary_rows = [
        {"metric": "country_wave", "value": IDNO, "interpretation": "Country-wave covered by the SPL bridge verification gate."},
        {"metric": "official_metadata_last_update", "value": OFFICIAL_METADATA_LAST_UPDATE, "interpretation": "Official UNSD SDG 3.8.2 metadata version checked for the formula."},
        {"metric": "world_bank_api_revalidation_date", "value": WORLD_BANK_API_REVALIDATION_DATE, "interpretation": "Date the PPP/CPI source values were rechecked against the official World Bank API."},
        {"metric": "wdi_ppp_private_consumption_2017_api_match", "value": str(int(ppp_match)), "interpretation": "Ledger private-consumption PPP value matches the official World Bank API value."},
        {"metric": "wdi_cpi_2004_api_match", "value": str(int(cpi_2004_match)), "interpretation": "Ledger 2004 CPI value matches the official World Bank API value."},
        {"metric": "wdi_cpi_2017_api_match", "value": str(int(cpi_2017_match)), "interpretation": "Ledger 2017 CPI value matches the official World Bank API value."},
        {"metric": "source_parameters_revalidated", "value": str(int(source_values_revalidated)), "interpretation": "All three external source values match the official API values used by the ledger."},
        {"metric": "candidate_cpi_ratio_recomputed", "value": str(int(ratio_match)), "interpretation": "The annual CPI 2017/2004 ratio is reproducible from source values."},
        {"metric": "candidate_local_currency_spl_recomputed", "value": str(int(spl_match)), "interpretation": "The candidate local-currency SPL is reproducible from PPP, CPI ratio, and SPL formula."},
        {"metric": "candidate_spl_2017_ppp", "value": fmt(spl_2017_ppp), "interpretation": "Candidate SPL in 2017 PPP international dollars per person per day."},
        {"metric": "candidate_spl_daily_raw_2004_mwk", "value": fmt(spl_daily_raw), "interpretation": "Candidate local-currency SPL in survey raw real 2004 MWK per person per day."},
        {"metric": "survey_povline_daily_raw_2004_mwk", "value": fmt(povline_daily), "interpretation": "Survey national poverty-line context; not the official SDG SPL by itself."},
        {"metric": "candidate_spl_to_survey_povline_ratio", "value": fmt(spl_to_povline_ratio), "interpretation": "Diagnostic ratio between candidate SDG SPL and survey poverty-line context."},
        {"metric": "survey_price_index_base_status", "value": "national_february_march_2004_base" if base_label_has_month else "base_not_identified", "interpretation": "Base-period evidence from the raw price_index label."},
        {"metric": "annual_cpi_bridge_base_period_accepted", "value": str(int(annual_cpi_bridge_accepted)), "interpretation": "Whether annual CPI is accepted as a final bridge to the survey real-currency base."},
        {"metric": "nonpositive_discretionary_budget_rows", "value": str(nonpositive_rows), "interpretation": "Rows with nonpositive discretionary budget under the candidate SPL."},
        {"metric": "official_rule_candidate_sdg382_rows", "value": str(official_candidate_rows), "interpretation": "Aggregate candidate SDG 3.8.2 rows under the official nonpositive rule and candidate SPL."},
        {"metric": "external_parameter_bridge_accepted", "value": "0", "interpretation": "The PPP/CPI source values are verified, but the survey-base bridge is not accepted."},
        {"metric": "local_currency_spl_accepted", "value": "0", "interpretation": "The local-currency SPL remains candidate."},
        {"metric": "sdg382_ready", "value": "0", "interpretation": "Malawi 2004 SDG 3.8.2 remains blocked."},
        {"metric": "registry_sdg382_status", "value": "blocked_spl_base_period_bridge_not_accepted_ppp_cpi_values_revalidated", "interpretation": "More precise registry blocker after this verifier."},
        {"metric": "data_write_gate_status", "value": "closed", "interpretation": "No household-level SDG 3.8.2 data are written."},
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
        f"""# Malawi 2004 SDG 3.8.2 SPL Bridge Verification Gate

Dataset: `{IDNO}` - {COUNTRY} {WAVE}

This verifier narrows the Malawi 2004 SDG 3.8.2 blocker. The current UNSD
metadata formula and the World Bank WDI source values for 2017 private
consumption PPP, 2004 CPI, and 2017 CPI are revalidated. The candidate SPL is
also reproducible.

The gate remains closed because the raw survey `price_index` context identifies
the real-currency base as national February/March 2004, while the candidate
bridge uses annual CPI 2004. Without a documented base-period reconciliation or
an official accepted Malawi SDG 3.8.2 production source, the local-currency SPL
cannot be accepted for a promoted household-level SDG 3.8.2 field.

## Summary

{markdown_table(summary_rows, ['metric', 'value', 'interpretation'], 35)}

## Gate Components

{markdown_table(rows, ['component', 'status', 'value', 'decision', 'remaining_blocker'], 25)}

## Decision

`source_parameters_revalidated=1`, but
`annual_cpi_bridge_base_period_accepted=0`, `local_currency_spl_accepted=0`,
`sdg382_ready=0`, `data_write_gate_status=closed`, and
`modeling_gate_status=blocked`.
""",
        encoding="utf-8",
    )


def main() -> None:
    ensure_dirs()
    rows, summary_rows = build_outputs()
    write_csv(GATE_PATH, rows, GATE_COLUMNS)
    write_csv(SUMMARY_PATH, summary_rows, SUMMARY_COLUMNS)
    write_report(rows, summary_rows)
    append_log(TEMP_DIR / "audit_log.md", f"Built Malawi 2004 SDG 3.8.2 SPL bridge verification gate rows={len(rows)}.")
    print(f"Malawi 2004 SDG 3.8.2 SPL bridge verification gate rows={len(rows)}.")


if __name__ == "__main__":
    main()
