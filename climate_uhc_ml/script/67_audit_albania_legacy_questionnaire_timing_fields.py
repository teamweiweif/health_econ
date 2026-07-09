from __future__ import annotations

import csv
import math
import re
from pathlib import Path
from typing import Any

import pandas as pd

from common import REPORT_DIR, RESULT_DIR, TEMP_DIR, append_log, ensure_dirs, write_csv


COUNTRY = "Albania"
RAW_CATALOG_PATH = TEMP_DIR / "raw_schema_inventory" / "raw_variable_catalog.csv"

FIELD_AUDIT_PATH = TEMP_DIR / "albania_legacy_questionnaire_timing_field_audit.csv"
RAW_GAP_AUDIT_PATH = TEMP_DIR / "albania_legacy_questionnaire_timing_raw_gap_audit.csv"
SUMMARY_PATH = RESULT_DIR / "albania_legacy_questionnaire_timing_field_summary.csv"
REPORT_PATH = REPORT_DIR / "albania_legacy_questionnaire_timing_field_audit.md"

DECISION = "blocked_legacy_questionnaire_form_design_not_sufficient_for_climate_linkage"
QUESTIONNAIRE_PROMOTION_STATUS = "form_design_only_not_raw_household_value"
RAW_GAP_PROMOTION_STATUS = "raw_timing_not_verified_for_climate_windows"
ALB2002_RAW_PROMOTION_STATUS = "raw_timing_observed_but_not_questionnaire_derived_and_climate_blocked"
QUESTIONNAIRE_BLOCKER = (
    "Questionnaire cell documents fieldwork/control-sheet design, but it is not a household-level raw "
    "interview date/month value and cannot define climate exposure windows by itself."
)
RAW_GAP_BLOCKER = (
    "Raw catalog hit has timing-like wording but is not verified as a household interview timing value "
    "for climate exposure windows."
)
ALB2002_RAW_BLOCKER = (
    "ALB_2002 has raw household interview timing values from Modul_0_identification.sav, but climate "
    "linkage remains blocked until district boundary/crosswalk, no-GPS admin aggregation, outcome "
    "semantics, missing-code, unit, recall, and comparability checks pass."
)

QUESTIONNAIRES = [
    {
        "country": COUNTRY,
        "survey_name": "Living Standards Measurement Survey 2002",
        "wave": "2002",
        "idno": "ALB_2002_LSMS_v01_M",
        "relative_path": "temp/raw_extracted/lsms2002en_4dbf0b087520/lsms2002en/Questionnaire 2002/LSMS02_Questionnaire.xls",
        "questionnaire_role": "single_legacy_questionnaire",
        "target_sheets": ["CONTROL SHEET", "SECTION 2 & PANEL INFORMATION"],
    },
    {
        "country": COUNTRY,
        "survey_name": "Living Standards Measurement Survey 2005",
        "wave": "2005",
        "idno": "ALB_2005_LSMS_v01_M",
        "relative_path": "temp/raw_extracted/lsms2005en_1e7f1965c4a5/lsms2005en/Questionnaire 2005/LSMS05_questionnaire_part1.xls",
        "questionnaire_role": "part1_legacy_questionnaire",
        "target_sheets": ["CONTROL SHEET"],
    },
    {
        "country": COUNTRY,
        "survey_name": "Living Standards Measurement Survey 2005",
        "wave": "2005",
        "idno": "ALB_2005_LSMS_v01_M",
        "relative_path": "temp/raw_extracted/lsms2005en_1e7f1965c4a5/lsms2005en/Questionnaire 2005/LSMS05_Questionnaire_part2.xls",
        "questionnaire_role": "part2_legacy_questionnaire",
        "target_sheets": ["SECTION 2 & PANEL INFORMATION"],
    },
    {
        "country": COUNTRY,
        "survey_name": "Living Standards Measurement Survey 2008",
        "wave": "2008",
        "idno": "ALB_2008_LSMS_v01_M",
        "relative_path": "temp/raw_extracted/lsms_2008_eng_a54110ab32b9/LSMS 2008_eng/Questionnaire/FINAL LSMS08 PART 1 ENGLISH.xls",
        "questionnaire_role": "part1_legacy_questionnaire",
        "target_sheets": ["CONTROL SHEET"],
    },
    {
        "country": COUNTRY,
        "survey_name": "Living Standards Measurement Survey 2008",
        "wave": "2008",
        "idno": "ALB_2008_LSMS_v01_M",
        "relative_path": "temp/raw_extracted/lsms_2008_eng_a54110ab32b9/LSMS 2008_eng/Questionnaire/FINAL LSMS08 PART 2 ENGLISH1.xls",
        "questionnaire_role": "part2_legacy_questionnaire",
        "target_sheets": ["SECTION 2 & PANEL INFORMATION"],
    },
]

FIELD_COLUMNS = [
    "country",
    "survey_name",
    "wave",
    "idno",
    "relative_path",
    "questionnaire_role",
    "source_workbook",
    "sheet_name",
    "sheet_role",
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
        r"\binterviewer\b",
        r"\benumerator\b",
        r"\bfieldwork\b",
        r"\bcontact\b",
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
ALB2002_INTERVIEW_TIMING_VARIABLES = {"m0_q08d", "m0_q08m", "m0_q08y", "m0_q08d2", "m0_q08m2", "m0_q08y2", "m0_date"}


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


def csv_value(path: Path, metric: str, default: str = "0") -> str:
    for row in read_csv_dicts(path):
        if row.get("metric") == metric:
            return row.get("value", default)
    return default


def safe_int(value: Any, default: int = 0) -> int:
    try:
        return int(float(str(value).strip()))
    except (TypeError, ValueError):
        return default


def field_hit(text: str) -> bool:
    return bool(text) and any(pattern.search(text) for pattern in FIELD_PATTERNS)


def raw_hit(name: str, label: str) -> bool:
    blob = f"{name} {label}"
    return any(pattern.search(blob) for pattern in RAW_TIMING_PATTERNS)


def sheet_role(sheet_name: str) -> str:
    low = sheet_name.lower()
    if "control" in low:
        return "control_sheet"
    if "panel information" in low:
        return "panel_information"
    return "target_timing_sheet"


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
    if re.search(r"\binterviewer\b|\benumerator\b", low):
        return "enumerator_or_interviewer_instruction", "questionnaire_fieldwork_context"
    if re.search(r"\bfieldwork\b|\bcontact\b", low):
        return "fieldwork_contact_instruction", "questionnaire_fieldwork_context"
    return "questionnaire_timing_keyword", "questionnaire_control_sheet_context"


def wave_meta_from_source(source_path: str) -> tuple[str, str, str]:
    low = source_path.lower().replace("\\", "/")
    if "lsms2002en" in low:
        return "2002", "ALB_2002_LSMS_v01_M", "Living Standards Measurement Survey 2002"
    if "lsms2005en" in low:
        return "2005", "ALB_2005_LSMS_v01_M", "Living Standards Measurement Survey 2005"
    if "lsms_2008_eng" in low:
        return "2008", "ALB_2008_LSMS_v01_M", "Living Standards Measurement Survey 2008"
    return "", "", ""


def is_alb2002_verified_interview_timing(source_path: str, variable_name: str) -> bool:
    low_path = source_path.lower().replace("\\", "/")
    return "data_2002/modul_0_identification.sav" in low_path and variable_name.lower() in ALB2002_INTERVIEW_TIMING_VARIABLES


def raw_gap_role(source_path: str, name: str, label: str) -> str:
    blob = f"{name} {label}".lower()
    if is_alb2002_verified_interview_timing(source_path, name):
        return "raw_household_interview_timing_verified_alb2002"
    if name.lower().startswith("end_"):
        return "not_interview_timing_module_end_marker"
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
    if re.search(r"\b(interview|fieldwork|survey date|survey month)\b", blob):
        return "raw_control_timing_candidate_requires_review"
    return "timing_keyword_not_verified_interview_timing"


def build_field_audit() -> tuple[list[dict[str, str]], int, int, int, int]:
    rows: list[dict[str, str]] = []
    workbook_count = 0
    sheets_scanned = 0
    sheets_missing = 0
    sheet_read_errors = 0
    for item in QUESTIONNAIRES:
        path = TEMP_DIR.parent / str(item["relative_path"])
        if not path.exists():
            continue
        try:
            xl = pd.ExcelFile(path)
        except Exception:
            sheet_read_errors += len(item["target_sheets"])
            continue
        workbook_count += 1
        available = {sheet.lower(): sheet for sheet in xl.sheet_names}
        for target_sheet in item["target_sheets"]:
            sheet_name = available.get(str(target_sheet).lower())
            if not sheet_name:
                sheets_missing += 1
                continue
            try:
                frame = pd.read_excel(path, sheet_name=sheet_name, header=None, dtype=object)
            except Exception:
                sheet_read_errors += 1
                continue
            sheets_scanned += 1
            for row_index, record in frame.iterrows():
                for col_index, value in enumerate(record.tolist()):
                    text = fmt(value)
                    if not field_hit(text):
                        continue
                    role, relevance = field_role(text)
                    rows.append(
                        {
                            "country": str(item["country"]),
                            "survey_name": str(item["survey_name"]),
                            "wave": str(item["wave"]),
                            "idno": str(item["idno"]),
                            "relative_path": str(item["relative_path"]),
                            "questionnaire_role": str(item["questionnaire_role"]),
                            "source_workbook": path.name,
                            "sheet_name": sheet_name,
                            "sheet_role": sheet_role(sheet_name),
                            "row_number": str(row_index + 1),
                            "column_number": str(col_index + 1),
                            "cell_text": text,
                            "evidence_role": role,
                            "timing_relevance": relevance,
                            "promotion_status": QUESTIONNAIRE_PROMOTION_STATUS,
                            "blocking_reason": QUESTIONNAIRE_BLOCKER,
                        }
                    )
    return rows, workbook_count, sheets_scanned, sheets_missing, sheet_read_errors


def build_raw_gap_audit() -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for row in read_csv_dicts(RAW_CATALOG_PATH):
        source_path = row.get("source_path", "")
        file_format = row.get("file_format", "")
        if file_format.lower() != ".sav":
            continue
        wave, idno, survey_name = wave_meta_from_source(source_path)
        if not wave:
            continue
        variable_name = row.get("variable_name", "")
        variable_label = row.get("variable_label", "")
        if not raw_hit(variable_name, variable_label):
            continue
        role = raw_gap_role(source_path, variable_name, variable_label)
        verified_alb2002 = role == "raw_household_interview_timing_verified_alb2002"
        rows.append(
            {
                "country": COUNTRY,
                "survey_name": survey_name,
                "wave": wave,
                "idno": idno,
                "source_path": source_path,
                "file_format": file_format,
                "variable_name": variable_name,
                "variable_label": variable_label,
                "concept_hits": row.get("concept_hits", ""),
                "catalog_status": row.get("status", ""),
                "raw_gap_role": role,
                "promotion_status": ALB2002_RAW_PROMOTION_STATUS if verified_alb2002 else RAW_GAP_PROMOTION_STATUS,
                "blocking_reason": ALB2002_RAW_BLOCKER if verified_alb2002 else RAW_GAP_BLOCKER,
            }
        )
    return rows


def summary_row(metric: str, value: Any, interpretation: str) -> dict[str, str]:
    return {"metric": metric, "value": fmt(value), "interpretation": interpretation}


def build_summary(
    field_rows: list[dict[str, str]],
    raw_rows: list[dict[str, str]],
    workbook_count: int,
    sheets_scanned: int,
    sheets_missing: int,
    sheet_read_errors: int,
) -> list[dict[str, str]]:
    visit_rows = sum(1 for row in field_rows if row.get("evidence_role") == "visit_control_row")
    second_visit_rows = sum(1 for row in field_rows if row.get("evidence_role") == "second_visit_instruction")
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
    raw_verified_variable_rows = sum(1 for row in raw_rows if row.get("raw_gap_role") == "raw_household_interview_timing_verified_alb2002")
    raw_control_candidates = sum(1 for row in raw_rows if row.get("raw_gap_role") == "raw_control_timing_candidate_requires_review")
    alb2002_raw_verified = safe_int(csv_value(RESULT_DIR / "alb2002_household_core_candidate_summary.csv", "alb2002_households_with_interview_date", "0"))
    alb2005_raw_verified = safe_int(csv_value(RESULT_DIR / "alb2005_timing_geography_exhaustive_summary.csv", "alb2005_interview_timing_verified_rows", "0"))
    alb2008_raw_verified = safe_int(csv_value(RESULT_DIR / "alb2008_timing_geography_exhaustive_summary.csv", "alb2008_interview_timing_verified_rows", "0"))
    total_raw_verified = alb2002_raw_verified + alb2005_raw_verified + alb2008_raw_verified
    raw_verified_waves = sum(1 for value in [alb2002_raw_verified, alb2005_raw_verified, alb2008_raw_verified] if value > 0)
    return [
        summary_row("albania_legacy_questionnaire_timing_workbooks_scanned", workbook_count, "Legacy ALB_2002/2005/2008 questionnaire workbooks opened for timing/control content review."),
        summary_row("albania_legacy_questionnaire_timing_sheets_scanned", sheets_scanned, "Target control or panel-information sheets scanned."),
        summary_row("albania_legacy_questionnaire_timing_target_sheets_missing", sheets_missing, "Expected target sheets not found in opened workbooks."),
        summary_row("albania_legacy_questionnaire_timing_sheet_read_errors", sheet_read_errors, "Target sheets that could not be read."),
        summary_row("albania_legacy_questionnaire_timing_field_rows", len(field_rows), "Questionnaire cells documenting date, begin/end, visit, status, contact, or remarks fields."),
        summary_row("albania_legacy_questionnaire_timing_visit_rows", visit_rows, "Questionnaire cells documenting VISIT_1/VISIT_2/VISIT_3 control rows."),
        summary_row("albania_legacy_questionnaire_timing_second_visit_instruction_rows", second_visit_rows, "Questionnaire cells documenting second-visit instructions."),
        summary_row("albania_legacy_questionnaire_timing_date_begin_end_status_rows", date_begin_end_status_rows, "Questionnaire cells documenting date, begin/end, status, or status-code fields."),
        summary_row("albania_legacy_questionnaire_timing_raw_gap_rows", len(raw_rows), "ALB_2002/2005/2008 raw SPSS catalog rows with timing-like terms or verified ALB_2002 timing fields."),
        summary_row("albania_legacy_questionnaire_timing_raw_verified_variable_rows", raw_verified_variable_rows, "ALB_2002 raw catalog variables classified as verified interview timing fields."),
        summary_row("albania_legacy_questionnaire_timing_raw_control_candidate_rows", raw_control_candidates, "Raw SPSS rows with interview/fieldwork/survey timing wording requiring review."),
        summary_row("alb2002_legacy_questionnaire_timing_raw_verified_interview_timing_rows", alb2002_raw_verified, "ALB_2002 household rows with raw interview date from the existing household-core audit."),
        summary_row("alb2005_legacy_questionnaire_timing_raw_verified_interview_timing_rows", alb2005_raw_verified, "ALB_2005 verified raw household interview timing rows from the exhaustive timing/geography audit."),
        summary_row("alb2008_legacy_questionnaire_timing_raw_verified_interview_timing_rows", alb2008_raw_verified, "ALB_2008 verified raw household interview timing rows from the exhaustive timing/geography audit."),
        summary_row("albania_legacy_questionnaire_timing_raw_verified_interview_timing_waves", raw_verified_waves, "Legacy Albania waves with verified raw household interview timing rows."),
        summary_row("albania_legacy_questionnaire_timing_raw_verified_interview_timing_rows", total_raw_verified, "Total verified raw household interview timing rows already observed across ALB_2002/2005/2008."),
        summary_row("albania_legacy_questionnaire_timing_climate_linkage_ready_rows", 0, "Rows ready for climate-linkage input promotion after this questionnaire timing audit."),
        summary_row("albania_legacy_questionnaire_timing_current_decision", DECISION, "Current fail-closed decision for legacy questionnaire timing/control evidence."),
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
        f"""# Albania Legacy Questionnaire Timing Field Audit

Status: questionnaire/raw-gap audit only. This report reads ALB_2002, ALB_2005, and ALB_2008 legacy `.xls` questionnaire control or panel-information sheets and documents timing/control field evidence. It also checks the raw SPSS variable catalog for matching household interview timing values. It does not write `data/`, does not construct climate exposures, and does not promote any legacy Albania wave to climate linkage.

## Summary

| Metric | Value | Interpretation |
|---|---:|---|
{summary_table}

## Questionnaire Timing Field Evidence

{markdown_rows(field_rows, ['idno', 'source_workbook', 'sheet_name', 'row_number', 'column_number', 'cell_text', 'evidence_role', 'promotion_status'], 100) if field_rows else 'No legacy questionnaire timing field rows were found.'}

## Questionnaire Evidence Roles

{count_table(field_rows, 'evidence_role') if field_rows else 'No questionnaire evidence-role rows were found.'}

## Raw SPSS Timing Evidence And Gaps

{markdown_rows(raw_rows, ['idno', 'source_path', 'variable_name', 'variable_label', 'raw_gap_role', 'promotion_status'], 80) if raw_rows else 'No raw SPSS timing-like catalog rows were found.'}

## Raw Gap Roles

{count_table(raw_rows, 'raw_gap_role') if raw_rows else 'No raw gap-role rows were found.'}

## Interpretation

- The legacy questionnaire control sheets document `DATE`, `BEGIN`, `END`, `STATUS`, status codes, remarks/contact context, and repeated visit rows.
- These cells show that fieldwork timing and visit status were intended on the forms, but they are form-design evidence, not household-level raw timing values.
- ALB_2002 already has raw household interview timing values in the existing household-core audit; this was not discovered from the questionnaire and does not solve the remaining boundary, no-GPS/admin aggregation, outcome-semantics, unit, recall, and comparability gates.
- ALB_2005 and ALB_2008 still do not have verified raw household interview timing rows in the current exhaustive timing/geography audits.
- Climate-linkage-ready rows remain zero for all legacy Albania waves after this audit.

## Machine-Readable Outputs

- `temp/albania_legacy_questionnaire_timing_field_audit.csv`
- `temp/albania_legacy_questionnaire_timing_raw_gap_audit.csv`
- `result/albania_legacy_questionnaire_timing_field_summary.csv`
""",
        encoding="utf-8",
    )


def main() -> None:
    ensure_dirs()
    field_rows, workbook_count, sheets_scanned, sheets_missing, sheet_read_errors = build_field_audit()
    raw_rows = build_raw_gap_audit()
    summary = build_summary(field_rows, raw_rows, workbook_count, sheets_scanned, sheets_missing, sheet_read_errors)
    write_csv(FIELD_AUDIT_PATH, field_rows, FIELD_COLUMNS)
    write_csv(RAW_GAP_AUDIT_PATH, raw_rows, RAW_GAP_COLUMNS)
    write_csv(SUMMARY_PATH, summary, SUMMARY_COLUMNS)
    write_report(field_rows, raw_rows, summary)
    append_log(
        TEMP_DIR / "audit_log.md",
        f"Built Albania legacy questionnaire timing field audit field_rows={len(field_rows)} raw_gap_rows={len(raw_rows)} decision={DECISION}.",
    )
    print(f"Albania legacy questionnaire timing field audit rows={len(field_rows)} raw_gap_rows={len(raw_rows)} decision={DECISION}.")


if __name__ == "__main__":
    main()
