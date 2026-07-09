from __future__ import annotations

import csv
import math
import re
from pathlib import Path
from typing import Any

import pandas as pd

from common import REPORT_DIR, RESULT_DIR, TEMP_DIR, append_log, ensure_dirs, write_csv


IDNO = "ALB_2012_LSMS_v01_M_v01_A_PUF"
COUNTRY = "Albania"
SURVEY_NAME = "Living Standards Measurement Survey 2012"
WAVE = "2012"

QUESTIONNAIRE_ROOT = TEMP_DIR / "raw_extracted" / "lsms_2012_eng_7631729d2caf" / "LSMS 2012_eng" / "Quesionaires_English"
WORKBOOK_SHEETS = {
    "LSMS_12  PART 1 Eng.xlsx": ["CONTROL SHEET"],
    "LSMS_12  PART 2 Eng.xlsx": ["SECTION 2 & PANEL INFORMATION"],
}
RAW_CATALOG_PATH = TEMP_DIR / "raw_schema_inventory" / "raw_variable_catalog.csv"
TIMING_GEO_SUMMARY_PATH = RESULT_DIR / "alb2012_timing_geography_exhaustive_summary.csv"

FIELD_AUDIT_PATH = TEMP_DIR / "alb2012_questionnaire_timing_field_audit.csv"
RAW_GAP_AUDIT_PATH = TEMP_DIR / "alb2012_questionnaire_timing_raw_gap_audit.csv"
SUMMARY_PATH = RESULT_DIR / "alb2012_questionnaire_timing_field_summary.csv"
REPORT_PATH = REPORT_DIR / "alb2012_questionnaire_timing_field_audit.md"

DECISION = "blocked_questionnaire_timing_fields_not_in_raw_household_values"
QUESTIONNAIRE_PROMOTION_STATUS = "not_raw_household_value_not_ready_for_climate_linkage"
RAW_PROMOTION_STATUS = "raw_household_interview_timing_not_verified"
QUESTIONNAIRE_BLOCKER = (
    "Questionnaire cell documents fieldwork/control-sheet design, but no raw household interview "
    "date/month value is verified in the public SPSS modules."
)
RAW_BLOCKER = (
    "Raw catalog hit is not a verified household interview date/month value for climate exposure "
    "windows."
)

FIELD_COLUMNS = [
    "country",
    "survey_name",
    "wave",
    "idno",
    "source_workbook",
    "sheet_name",
    "row_number",
    "column_number",
    "cell_text",
    "evidence_role",
    "timing_relevance",
    "promotion_status",
    "blocking_reason",
]
RAW_GAP_COLUMNS = [
    "country",
    "survey_name",
    "wave",
    "idno",
    "source_path",
    "file_format",
    "variable_name",
    "variable_label",
    "concept_hits",
    "catalog_status",
    "raw_gap_role",
    "promotion_status",
    "blocking_reason",
]
SUMMARY_COLUMNS = ["metric", "value", "interpretation"]

FIELD_PATTERNS = [
    re.compile(pattern, re.IGNORECASE)
    for pattern in [
        r"\bdate\b",
        r"day\s*/\s*mm\s*/\s*yy",
        r"\bbegin\b",
        r"\bend\b",
        r"\bstatus\b",
        r"\bremarks?\b",
        r"\bvisit[_ ]?[123]\b",
        r"\bsecond visit\b",
        r"\bstatus codes?\b",
        r"\bcomplete\b",
        r"\bincomplete\b",
        r"\bnot contacted\b",
        r"\brefused\b",
    ]
]
RAW_TIMING_PATTERNS = [
    re.compile(pattern, re.IGNORECASE)
    for pattern in [
        r"\binterview\b",
        r"\bfieldwork\b",
        r"\bsurvey date\b",
        r"\bsurvey month\b",
        r"\bvisit\b",
        r"\bdate\b",
        r"\bbegin\b",
        r"\bend\b",
        r"\bstatus\b",
        r"\bremark\b",
    ]
]


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
    return " ".join(str(value).split())


def read_csv_dicts(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def csv_value(rows: list[dict[str, str]], metric: str, default: str = "0") -> str:
    for row in rows:
        if row.get("metric") == metric:
            return row.get("value", default)
    return default


def field_hit(text: str) -> bool:
    return bool(text) and any(pattern.search(text) for pattern in FIELD_PATTERNS)


def raw_hit(name: str, label: str) -> bool:
    blob = f"{name} {label}"
    return any(pattern.search(blob) for pattern in RAW_TIMING_PATTERNS)


def field_role(text: str) -> tuple[str, str]:
    low = text.lower()
    if re.search(r"\bvisit[_ ]?[123]\b", low):
        return "visit_control_row", "questionnaire_visit_level_fieldwork_timing_design"
    if "second visit" in low:
        return "second_visit_instruction", "questionnaire_fieldwork_sequence_instruction"
    if "day/mm/yy" in low or re.search(r"\bdate\b", low):
        return "date_field_or_format", "questionnaire_fieldwork_date_design"
    if re.search(r"\bbegin\b|\bend\b", low):
        return "begin_end_time_field", "questionnaire_fieldwork_time_design"
    if "status code" in low:
        return "status_code_label", "questionnaire_completion_status_design"
    if re.search(r"\bstatus\b|\bcomplete\b|\bincomplete\b|\bnot contacted\b|\brefused\b", low):
        return "completion_status_field_or_code", "questionnaire_completion_status_design"
    if re.search(r"\bremarks?\b", low):
        return "remarks_field", "questionnaire_control_sheet_context"
    return "questionnaire_timing_keyword", "questionnaire_control_sheet_context"


def raw_gap_role(name: str, label: str, source_path: str) -> str:
    blob = f"{name} {label}".lower()
    source_low = source_path.lower()
    if "questionaires_english" in source_low or ".xlsx::" in source_low or ".xls::" in source_low:
        return "questionnaire_catalog_row_not_raw_household_value"
    if re.search(r"\b(interview|fieldwork|survey date|survey month)\b", blob):
        return "raw_control_timing_candidate_requires_review"
    if "birth" in blob or "date of birth" in blob:
        return "not_interview_timing_birth_or_fertility_context"
    if re.search(r"\b(migrat|moved|residen|living in 1990|abroad|born)\b", blob):
        return "not_interview_timing_migration_or_residence_history"
    if re.search(r"\b(past 4 weeks|past month|past 30 days|past 6 months|past 12 months|last 6 months|recall)\b", blob):
        return "not_interview_timing_recall_period_context"
    if re.search(r"\b(amount per month|monthly|months covered|number of months|months suffering|months breastfed)\b", blob):
        return "not_interview_timing_duration_or_payment_period"
    if re.search(r"\b(started|began|job|academic year|inhabit this dwelling|year of acquisition|assistance)\b", blob):
        return "not_interview_timing_event_history_context"
    if re.search(r"\bvisit\b", blob):
        return "not_interview_timing_health_or_module_visit_context"
    if re.search(r"\bstatus\b", blob):
        return "status_keyword_not_verified_interview_timing"
    return "timing_keyword_not_verified_interview_timing"


def build_field_audit() -> tuple[list[dict[str, str]], int]:
    rows: list[dict[str, str]] = []
    workbook_count = 0
    for workbook, sheets in WORKBOOK_SHEETS.items():
        path = QUESTIONNAIRE_ROOT / workbook
        if not path.exists():
            continue
        workbook_count += 1
        for sheet in sheets:
            frame = pd.read_excel(path, sheet_name=sheet, header=None, dtype=object, engine="openpyxl")
            for row_index, record in frame.iterrows():
                for col_index, value in enumerate(record.tolist()):
                    text = fmt(value)
                    if not field_hit(text):
                        continue
                    role, relevance = field_role(text)
                    rows.append(
                        {
                            "country": COUNTRY,
                            "survey_name": SURVEY_NAME,
                            "wave": WAVE,
                            "idno": IDNO,
                            "source_workbook": workbook,
                            "sheet_name": sheet,
                            "row_number": str(row_index + 1),
                            "column_number": str(col_index + 1),
                            "cell_text": text,
                            "evidence_role": role,
                            "timing_relevance": relevance,
                            "promotion_status": QUESTIONNAIRE_PROMOTION_STATUS,
                            "blocking_reason": QUESTIONNAIRE_BLOCKER,
                        }
                    )
    return rows, workbook_count


def build_raw_gap_audit() -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for row in read_csv_dicts(RAW_CATALOG_PATH):
        source_path = row.get("source_path", "")
        file_format = row.get("file_format", "")
        if "lsms_2012" not in source_path.lower():
            continue
        if file_format.lower() != ".sav" and "data_lsms 2012" not in source_path.lower():
            continue
        variable_name = row.get("variable_name", "")
        variable_label = row.get("variable_label", "")
        if not raw_hit(variable_name, variable_label):
            continue
        rows.append(
            {
                "country": COUNTRY,
                "survey_name": SURVEY_NAME,
                "wave": WAVE,
                "idno": IDNO,
                "source_path": source_path,
                "file_format": file_format,
                "variable_name": variable_name,
                "variable_label": variable_label,
                "concept_hits": row.get("concept_hits", ""),
                "catalog_status": row.get("status", ""),
                "raw_gap_role": raw_gap_role(variable_name, variable_label, source_path),
                "promotion_status": RAW_PROMOTION_STATUS,
                "blocking_reason": RAW_BLOCKER,
            }
        )
    return rows


def summary_row(metric: str, value: Any, interpretation: str) -> dict[str, str]:
    return {"metric": metric, "value": fmt(value), "interpretation": interpretation}


def build_summary(field_rows: list[dict[str, str]], raw_rows: list[dict[str, str]], workbook_count: int) -> list[dict[str, str]]:
    timing_geo_summary = read_csv_dicts(TIMING_GEO_SUMMARY_PATH)
    raw_control_candidates = sum(1 for row in raw_rows if row.get("raw_gap_role") == "raw_control_timing_candidate_requires_review")
    visit_rows = sum(1 for row in field_rows if row.get("evidence_role") == "visit_control_row")
    date_begin_end_status_rows = sum(
        1
        for row in field_rows
        if row.get("evidence_role")
        in {
            "date_field_or_format",
            "begin_end_time_field",
            "completion_status_field_or_code",
            "status_code_label",
        }
    )
    return [
        summary_row("alb2012_questionnaire_timing_workbooks_scanned", workbook_count, "ALB_2012 questionnaire workbooks scanned for control-sheet timing fields."),
        summary_row("alb2012_questionnaire_timing_field_rows", len(field_rows), "Questionnaire cells documenting date, begin/end, visit, status, or remarks fields."),
        summary_row("alb2012_questionnaire_timing_visit_rows", visit_rows, "Questionnaire cells documenting VISIT_1/VISIT_2/VISIT_3 control rows."),
        summary_row("alb2012_questionnaire_timing_date_begin_end_status_rows", date_begin_end_status_rows, "Questionnaire cells documenting date, begin/end, status, or status-code fields."),
        summary_row("alb2012_questionnaire_timing_raw_gap_rows", len(raw_rows), "ALB_2012 raw SPSS catalog rows with timing-like terms but not verified interview timing."),
        summary_row("alb2012_questionnaire_timing_raw_control_candidate_rows", raw_control_candidates, "Raw SPSS rows with interview/fieldwork/survey timing wording requiring review."),
        summary_row("alb2012_questionnaire_timing_raw_verified_interview_timing_rows", 0, "Verified household interview month/date values in raw SPSS modules."),
        summary_row("alb2012_questionnaire_timing_previous_exhaustive_verified_interview_rows", csv_value(timing_geo_summary, "alb2012_interview_timing_verified_rows", "0"), "Verified interview timing rows reported by the exhaustive raw timing/geography audit."),
        summary_row("alb2012_questionnaire_timing_previous_exhaustive_climate_ready_rows", csv_value(timing_geo_summary, "alb2012_climate_linkage_ready_rows", "0"), "Climate-linkage-ready rows reported by the exhaustive raw timing/geography audit."),
        summary_row("alb2012_questionnaire_timing_climate_linkage_ready_rows", 0, "Rows ready for climate-linkage input promotion after this questionnaire timing audit."),
        summary_row("alb2012_questionnaire_timing_current_decision", DECISION, "Current fail-closed decision for ALB_2012 questionnaire timing evidence."),
    ]


def count_table(rows: list[dict[str, str]], column: str) -> str:
    counts: dict[str, int] = {}
    for row in rows:
        key = row.get(column, "") or "blank"
        counts[key] = counts.get(key, 0) + 1
    lines = [f"| {column} | Rows |", "|---|---:|"]
    for key, count in sorted(counts.items()):
        lines.append(f"| {key.replace('|', '/')} | {count} |")
    return "\n".join(lines)


def markdown_rows(rows: list[dict[str, str]], columns: list[str], limit: int = 40) -> str:
    lines = ["| " + " | ".join(columns) + " |", "|" + "|".join("---" for _ in columns) + "|"]
    for row in rows[:limit]:
        values: list[str] = []
        for column in columns:
            value = (row.get(column, "") or "").replace("|", "/")
            if len(value) > 110:
                value = value[:107] + "..."
            values.append(value)
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines)


def write_report(field_rows: list[dict[str, str]], raw_rows: list[dict[str, str]], summary: list[dict[str, str]]) -> None:
    summary_table = "\n".join(f"| {row['metric']} | {row['value']} | {row['interpretation']} |" for row in summary)
    REPORT_PATH.write_text(
        f"""# ALB_2012 Questionnaire Timing Field Audit

Status: questionnaire/raw-gap audit only. This report reads the ALB_2012 English questionnaire workbooks and documents control-sheet timing fields. It also checks the raw SPSS variable catalog for matching household interview timing values. It does not write `data/`, does not construct climate exposures, and does not promote ALB_2012 to climate linkage.

## Summary

| Metric | Value | Interpretation |
|---|---:|---|
{summary_table}

## Questionnaire Timing Field Evidence

{markdown_rows(field_rows, ['source_workbook', 'sheet_name', 'row_number', 'column_number', 'cell_text', 'evidence_role', 'promotion_status'], 80) if field_rows else 'No questionnaire timing field rows were found.'}

## Questionnaire Evidence Roles

{count_table(field_rows, 'evidence_role') if field_rows else 'No questionnaire evidence-role rows were found.'}

## Raw SPSS Timing Gap Evidence

{markdown_rows(raw_rows, ['source_path', 'variable_name', 'variable_label', 'raw_gap_role', 'promotion_status'], 60) if raw_rows else 'No raw SPSS timing-like catalog rows were found.'}

## Raw Gap Roles

{count_table(raw_rows, 'raw_gap_role') if raw_rows else 'No raw gap-role rows were found.'}

## Interpretation

- The questionnaire control sheets document `DATE`, `BEGIN`, `END`, `STATUS`, `REMARKS`, and repeated visit rows.
- These cells show that fieldwork timing and visit status were intended on the forms, but they are not household-level raw timing values.
- The raw SPSS module catalog still does not verify household interview month/date values.
- Birth dates, recall windows, health-service visit counts, migration/residence histories, and other event dates cannot define pre-interview climate exposure windows.
- ALB_2012 remains blocked for climate linkage until raw household timing values or official fieldwork-period metadata can be connected to household geography.

## Machine-Readable Outputs

- `temp/alb2012_questionnaire_timing_field_audit.csv`
- `temp/alb2012_questionnaire_timing_raw_gap_audit.csv`
- `result/alb2012_questionnaire_timing_field_summary.csv`
""",
        encoding="utf-8",
    )


def main() -> None:
    ensure_dirs()
    field_rows, workbook_count = build_field_audit()
    raw_rows = build_raw_gap_audit()
    summary = build_summary(field_rows, raw_rows, workbook_count)
    write_csv(FIELD_AUDIT_PATH, field_rows, FIELD_COLUMNS)
    write_csv(RAW_GAP_AUDIT_PATH, raw_rows, RAW_GAP_COLUMNS)
    write_csv(SUMMARY_PATH, summary, SUMMARY_COLUMNS)
    write_report(field_rows, raw_rows, summary)
    append_log(
        TEMP_DIR / "audit_log.md",
        f"Built ALB_2012 questionnaire timing field audit field_rows={len(field_rows)} raw_gap_rows={len(raw_rows)} decision={DECISION}.",
    )
    print(f"ALB_2012 questionnaire timing field audit rows={len(field_rows)} raw_gap_rows={len(raw_rows)} decision={DECISION}.")


if __name__ == "__main__":
    main()
