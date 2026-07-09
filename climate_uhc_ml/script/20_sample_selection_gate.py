from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path
from typing import Any

from common import REPORT_DIR, RESULT_DIR, TEMP_DIR, append_log, ensure_dirs, write_csv


GATE_PATH = RESULT_DIR / "sample_selection_gate_audit.csv"
SUMMARY_PATH = RESULT_DIR / "sample_selection_gate_summary.csv"
REPORT_PATH = REPORT_DIR / "sample_selection_audit.md"

GATE_COLUMNS = [
    "country",
    "survey_name",
    "wave",
    "idno",
    "feasibility_score",
    "metadata_has_budget",
    "metadata_has_oop",
    "metadata_has_weight",
    "metadata_has_timing",
    "metadata_has_geography",
    "metadata_has_financial_core",
    "metadata_has_access_core",
    "metadata_has_main_sample_core",
    "raw_file_inspected",
    "raw_variable_verified",
    "harmonization_value_audit_ready",
    "eligible_for_final_sample",
    "eligible_for_access_secondary_sample",
    "status",
    "gap",
]

SUMMARY_COLUMNS = ["rule", "status", "count_or_value", "threshold", "interpretation"]


def read_csv_dicts(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def clean(value: Any) -> str:
    return "" if value is None else str(value).strip()


def is_present(value: Any) -> bool:
    text = clean(value).lower()
    if not text:
        return False
    missing_tokens = [
        "not found",
        "not available",
        "not determined",
        "requires raw",
        "none",
        "nan",
    ]
    return not any(token in text for token in missing_tokens)


def bool_text(value: bool) -> str:
    return "1" if value else "0"


def raw_verified_idnos() -> tuple[set[str], set[str]]:
    raw_files = read_csv_dicts(TEMP_DIR / "raw_schema_inventory" / "raw_file_inventory.csv")
    raw_vars = read_csv_dicts(TEMP_DIR / "raw_schema_inventory" / "raw_variable_catalog.csv")
    file_idnos: set[str] = set()
    var_idnos: set[str] = set()
    for row in raw_files:
        source = row.get("source_path", "") + " " + row.get("extracted_from", "")
        for token in source.replace("\\", "/").split("/"):
            if "_" in token and any(ch.isdigit() for ch in token):
                file_idnos.add(token)
    for row in raw_vars:
        source = row.get("source_path", "") + " " + row.get("extracted_from", "")
        for token in source.replace("\\", "/").split("/"):
            if "_" in token and any(ch.isdigit() for ch in token):
                var_idnos.add(token)
    return file_idnos, var_idnos


def harmonization_ready_idnos() -> set[str]:
    rows = read_csv_dicts(RESULT_DIR / "harmonization_readiness_matrix.csv")
    return {
        row.get("idno", "")
        for row in rows
        if row.get("idno", "") and row.get("readiness_status") == "ready_for_verified_recipe_assembly"
    }


def gate_rows() -> list[dict[str, str]]:
    screening = read_csv_dicts(TEMP_DIR / "country_wave_screening.csv")
    file_idnos, var_idnos = raw_verified_idnos()
    ready_idnos = harmonization_ready_idnos()
    rows: list[dict[str, str]] = []
    for row in screening:
        budget = is_present(row.get("total consumption or income aggregate", ""))
        oop = is_present(row.get("OOP health expenditure", ""))
        weight = is_present(row.get("weights", ""))
        timing = is_present(row.get("interview date", "")) or is_present(row.get("interview month", ""))
        geography = is_present(row.get("admin1/admin2 geography", "")) or is_present(row.get("GPS or cluster coordinates", ""))
        need = is_present(row.get("illness/injury/health need", ""))
        care = is_present(row.get("care-seeking", "")) or is_present(row.get("health-care utilization", ""))
        barrier = (
            is_present(row.get("reason for not seeking care", ""))
            or is_present(row.get("cost barrier", ""))
            or is_present(row.get("distance barrier", ""))
            or is_present(row.get("supply/drug/staff barrier", ""))
        )
        financial_core = budget and oop
        access_core = need and (care or barrier)
        main_core = financial_core and weight and timing and geography
        idno = row.get("idno", "")
        raw_file = idno in file_idnos
        raw_var = idno in var_idnos
        harmonization_ready = idno in ready_idnos
        final_eligible = main_core and raw_file and raw_var and harmonization_ready
        secondary_eligible = access_core and geography and timing and raw_file and raw_var and harmonization_ready
        gaps = []
        if not budget:
            gaps.append("budget_missing_or_metadata_weak")
        if not oop:
            gaps.append("oop_missing_or_metadata_weak")
        if not weight:
            gaps.append("weight_missing_or_metadata_weak")
        if not timing:
            gaps.append("timing_missing_or_metadata_weak")
        if not geography:
            gaps.append("geography_missing_or_metadata_weak")
        if not access_core:
            gaps.append("access_core_missing_or_metadata_weak")
        if not raw_file or not raw_var:
            gaps.append("raw_microdata_not_inspected")
        if raw_file and raw_var and not harmonization_ready:
            gaps.append("value_audit_or_verified_harmonization_recipe_not_ready")
        if final_eligible:
            status = "eligible_final_sample_value_verified"
        elif main_core and raw_file and raw_var:
            status = "raw_schema_candidate_pending_value_harmonization_audit"
        elif main_core:
            status = "metadata_main_sample_candidate_not_selectable"
        elif access_core and geography and timing:
            status = "metadata_secondary_access_candidate_not_selectable"
        else:
            status = "excluded_or_low_priority_until_raw_evidence"
        rows.append(
            {
                "country": row.get("country", ""),
                "survey_name": row.get("survey name", ""),
                "wave": row.get("wave/year", ""),
                "idno": idno,
                "feasibility_score": row.get("feasibility score from 0 to 5", ""),
                "metadata_has_budget": bool_text(budget),
                "metadata_has_oop": bool_text(oop),
                "metadata_has_weight": bool_text(weight),
                "metadata_has_timing": bool_text(timing),
                "metadata_has_geography": bool_text(geography),
                "metadata_has_financial_core": bool_text(financial_core),
                "metadata_has_access_core": bool_text(access_core),
                "metadata_has_main_sample_core": bool_text(main_core),
                "raw_file_inspected": bool_text(raw_file),
                "raw_variable_verified": bool_text(raw_var),
                "harmonization_value_audit_ready": bool_text(harmonization_ready),
                "eligible_for_final_sample": bool_text(final_eligible),
                "eligible_for_access_secondary_sample": bool_text(secondary_eligible),
                "status": status,
                "gap": ";".join(gaps),
            }
        )
    return rows


def summary_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    final_rows = [row for row in rows if row["eligible_for_final_sample"] == "1"]
    final_countries = {row["country"] for row in final_rows if row["country"]}
    double_rows = [
        row
        for row in final_rows
        if row["metadata_has_financial_core"] == "1" and row["metadata_has_access_core"] == "1"
    ]
    metadata_main_rows = [row for row in rows if row["metadata_has_main_sample_core"] == "1"]
    metadata_main_countries = {row["country"] for row in metadata_main_rows if row["country"]}
    raw_blocked = not final_rows
    out = [
        {
            "rule": "Main financial-protection sample has at least 6 value-verified countries with budget, OOP, geography, timing, and weights",
            "status": "pass" if len(final_countries) >= 6 else "fail",
            "count_or_value": str(len(final_countries)),
            "threshold": "6 countries",
            "interpretation": "Do not proceed with main multi-country financial-protection paper until this passes.",
        },
        {
            "rule": "At least 10 value-verified country-waves support both financial hardship and access/forgone-care outcomes",
            "status": "pass" if len(double_rows) >= 10 else "fail",
            "count_or_value": str(len(double_rows)),
            "threshold": "10 country-waves",
            "interpretation": "Keep UHC double failure secondary until this passes.",
        },
        {
            "rule": "Metadata-only main-sample candidates before raw inspection",
            "status": "informational",
            "count_or_value": f"{len(metadata_main_rows)} waves; {len(metadata_main_countries)} countries",
            "threshold": "not a selection rule",
            "interpretation": "Useful for download prioritization only; not valid for final analytical sample selection.",
        },
        {
            "rule": "Raw value and verified harmonization gate",
            "status": "fail" if raw_blocked else "pass",
            "count_or_value": str(len(final_rows)),
            "threshold": "at least 1 value-verified analytical row set before any final selection",
            "interpretation": "Current final sample selection is blocked if this fails.",
        },
    ]
    return out


def markdown_count_table(counter: Counter[str], key_name: str) -> str:
    lines = [f"| {key_name} | Count |", "|---|---:|"]
    for key, count in counter.most_common():
        lines.append(f"| {key or 'blank'} | {count} |")
    return "\n".join(lines)


def write_report(rows: list[dict[str, str]], summaries: list[dict[str, str]]) -> None:
    status_counts = Counter(row["status"] for row in rows)
    score_counts = Counter(row["feasibility_score"] or "blank" for row in rows)
    metadata_main = sum(1 for row in rows if row["metadata_has_main_sample_core"] == "1")
    raw_final = sum(1 for row in rows if row["eligible_for_final_sample"] == "1")
    lines = [
        "# Sample Selection Audit",
        "",
        "Status: final sample selection is blocked until raw microdata, raw values, merge keys, and harmonization recipes are verified. Metadata and raw-schema evidence are used only for prioritization and gate tracking.",
        "",
        "## Gate Counts",
        "",
        f"- Country-wave screening rows: {len(rows)}",
        f"- Metadata-only main-sample candidates: {metadata_main}",
        f"- Value-verified final-sample candidates: {raw_final}",
        "",
        markdown_count_table(status_counts, "Sample gate status"),
        "",
        markdown_count_table(score_counts, "Metadata feasibility score"),
        "",
        "## No-Go Rules",
        "",
        "| Rule | Status | Count/value | Threshold | Interpretation |",
        "|---|---|---:|---|---|",
    ]
    for row in summaries:
        lines.append(
            f"| {row['rule']} | {row['status']} | {row['count_or_value']} | {row['threshold']} | {row['interpretation']} |"
        )
    lines.extend(
        [
            "",
            "## Guardrail",
            "",
            "A survey with metadata hits for consumption, OOP health spending, timing, geography, and weights is not selected for analysis until raw files, raw variables, raw values, merge keys, and harmonization recipes are verified. This prevents result shopping and prevents final countries from being chosen from metadata-only or schema-only screens.",
            "",
            "## Machine-Readable Outputs",
            "",
            "- `result/sample_selection_gate_audit.csv`",
            "- `result/sample_selection_gate_summary.csv`",
        ]
    )
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    ensure_dirs()
    rows = gate_rows()
    summaries = summary_rows(rows)
    write_csv(GATE_PATH, rows, GATE_COLUMNS)
    write_csv(SUMMARY_PATH, summaries, SUMMARY_COLUMNS)
    write_report(rows, summaries)
    final_count = sum(1 for row in rows if row["eligible_for_final_sample"] == "1")
    metadata_count = sum(1 for row in rows if row["metadata_has_main_sample_core"] == "1")
    append_log(TEMP_DIR / "audit_log.md", f"Sample selection gate audited {len(rows)} country-waves; metadata_candidates={metadata_count}; raw_final_candidates={final_count}.")
    print(f"Sample selection gate rows={len(rows)} metadata_candidates={metadata_count} raw_final_candidates={final_count}")


if __name__ == "__main__":
    main()
