from __future__ import annotations

import csv
import math
import re
from collections import Counter
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
QUESTIONNAIRE_PATH = RAW_ROOT / "Questionnaire 2005" / "LSMS05_Questionnaire_part2.xls"
DATA_ROOT = RAW_ROOT / "Data_2005"
HEALTH_A_PATH = DATA_ROOT / "Modul_9A_healtha_cl.sav"
HEALTH_B_PATH = DATA_ROOT / "Modul_9B_healthb_cl.sav"

REQUIRED_VALUE_KEY_SUMMARY_PATH = RESULT_DIR / "alb2005_required_value_key_summary.csv"
VALUE_DECISION_SUMMARY_PATH = RESULT_DIR / "alb2005_harmonization_value_decision_summary.csv"

AUDIT_PATH = TEMP_DIR / "alb2005_health_questionnaire_semantics_audit.csv"
SUMMARY_PATH = RESULT_DIR / "alb2005_health_questionnaire_semantics_summary.csv"
REPORT_PATH = REPORT_DIR / "alb2005_health_questionnaire_semantics_audit.md"

DECISION = "blocked_alb2005_questionnaire_semantics_seen_but_recipe_not_ready"
NO_PROMOTION = "not_promoted_questionnaire_semantics_audit_only"

AUDIT_COLUMNS = [
    "country",
    "survey_name",
    "wave",
    "idno",
    "concept",
    "harmonized_variable",
    "source_workbook",
    "sheet_name",
    "source_file",
    "raw_variable",
    "raw_label",
    "question_number",
    "question_context",
    "question_text",
    "recall_period",
    "unit_or_value_note",
    "skip_or_instruction_note",
    "value_code_evidence",
    "raw_row_count",
    "raw_nonmissing_rows",
    "raw_positive_numeric_rows",
    "raw_distinct_values",
    "semantic_evidence_status",
    "ready_for_recipe",
    "ready_for_outcome",
    "climate_linkage_ready",
    "promotion_status",
    "blocking_reason",
    "next_action",
]
SUMMARY_COLUMNS = ["metric", "value", "interpretation"]


FOUR_WEEK_PAYMENT_VARIABLES = [
    "m9a_q16",
    "m9a_q17",
    "m9a_q20",
    "m9a_q22",
    "m9a_q23",
    "m9a_q28",
    "m9a_q29",
    "m9a_q32",
    "m9a_q34",
    "m9a_q35",
    "m9a_q38",
    "m9a_q39",
    "m9a_q41",
    "m9a_q42",
    "m9a_q43",
    "m9a_q46",
    "m9a_q47",
    "m9a_q49",
    "m9a_q50",
    "m9a_q51",
    "m9a_q54",
    "m9a_q55",
    "m9a_q57",
    "m9a_q58",
    "m9a_q59",
    "m9a_q61",
]
TWELVE_MONTH_PAYMENT_VARIABLES = [
    "m9a_q68",
    "m9a_q69",
    "m9a_q71",
    "m9a_q72",
    "m9a_q73",
    "m9a_q76",
    "m9a_q77",
    "m9a_q79",
    "m9a_q80",
    "m9a_q81",
]
HEALTH_A_SELECTION_VARIABLES = ["m9a_q12", "m9a_q24", "m9a_q36", "m9a_q44", "m9a_q52", "m9a_q60", "m9a_q62", "m9a_q74"]
HEALTH_B_VARIABLES = [
    "m9b_q01",
    "m9b_q02",
    "m9b_q023",
    "m9b_q024",
    "m9b_q025",
    "m9b_q026",
    "m9b_q03",
    "m9b_q04",
    "m9b_q05",
    "m9b_q06",
    "m9b_q07",
    "m9b_q08",
    "m9b_q09",
    "m9b_q10",
]

HEALTH_B_QUESTION_MAP = {
    "m9b_q01": 1,
    "m9b_q02": 2,
    "m9b_q023": 2,
    "m9b_q024": 2,
    "m9b_q025": 2,
    "m9b_q026": 2,
    "m9b_q03": 3,
    "m9b_q04": 4,
    "m9b_q05": 5,
    "m9b_q06": 6,
    "m9b_q07": 7,
    "m9b_q08": 8,
    "m9b_q09": 9,
    "m9b_q10": 10,
}
HEALTH_B_CONCEPT_MAP = {
    "m9b_q01": ("care_or_barrier", "difficulty_paying_for_health"),
    "m9b_q02": ("coping_or_access_financing", "raise_money_for_health_care"),
    "m9b_q023": ("coping_or_access_financing", "raise_money_for_health_care"),
    "m9b_q024": ("coping_or_access_financing", "raise_money_for_health_care"),
    "m9b_q025": ("coping_or_access_financing", "raise_money_for_health_care"),
    "m9b_q026": ("coping_or_access_financing", "raise_money_for_health_care"),
    "m9b_q03": ("care_or_barrier", "delayed_or_no_help_count"),
    "m9b_q04": ("care_or_barrier", "delayed_or_no_help_reason"),
    "m9b_q05": ("care_or_barrier", "hospital_referral_not_gone_count"),
    "m9b_q06": ("care_or_barrier", "hospital_referral_not_gone_reason"),
    "m9b_q07": ("care_or_barrier", "refused_health_services"),
    "m9b_q08": ("care_or_barrier", "refused_health_services_reason"),
    "m9b_q09": ("insurance_or_medicine_access", "medicine_discount_entitlement"),
    "m9b_q10": ("insurance_or_medicine_access", "medicine_discount_access"),
}


def clean_text(value: Any) -> str:
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
            value = int(value)
    text = " ".join(str(value).split())
    return text.encode("ascii", "replace").decode("ascii")


def read_csv_dicts(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def metric_value(rows: list[dict[str, str]], metric: str, default: str = "0") -> str:
    return next((row.get("value", default) for row in rows if row.get("metric") == metric), default)


def int_value(value: Any) -> int:
    try:
        return int(float(str(value).strip()))
    except (TypeError, ValueError):
        return 0


def qnum(variable: str) -> int:
    match = re.search(r"_q0*([0-9]+)$", variable.lower())
    return int(match.group(1)) if match else 0


def read_sheet(sheet_name: str) -> pd.DataFrame:
    return pd.read_excel(QUESTIONNAIRE_PATH, sheet_name=sheet_name, header=None, dtype=object)


def find_health_a_column(df: pd.DataFrame, question_number: int) -> int | None:
    target = f"-{question_number}"
    for col in range(df.shape[1]):
        if clean_text(df.iat[3, col]) == target:
            return col
    return None


def nearest_left_context(df: pd.DataFrame, col: int) -> str:
    for left in range(col, -1, -1):
        text = clean_text(df.iat[2, left])
        if text:
            return text
    return ""


def collect_health_a_evidence(df: pd.DataFrame, question_number: int) -> dict[str, str]:
    col = find_health_a_column(df, question_number)
    if col is None:
        return {
            "question_text": "",
            "question_context": "",
            "unit_or_value_note": "",
            "skip_or_instruction_note": "question number not found in questionnaire sheet",
            "value_code_evidence": "",
        }
    unit_notes: list[str] = []
    skip_notes: list[str] = []
    value_notes: list[str] = []
    for offset in range(0, 3):
        c = col + offset
        if c >= df.shape[1]:
            continue
        for row in range(5, 23):
            text = clean_text(df.iat[row, c])
            if not text:
                continue
            low = text.lower()
            if "old leks" in low or "times" == low or "days" == low:
                unit_notes.append(text)
            if offset == 0 and ("exclude" in low or "zero" in low or ">>" in text or "if no" in low):
                skip_notes.append(text)
            if offset > 0 and row >= 14:
                value_notes.append(text)
    return {
        "question_text": clean_text(df.iat[4, col]),
        "question_context": nearest_left_context(df, col),
        "unit_or_value_note": "; ".join(dict.fromkeys(unit_notes)),
        "skip_or_instruction_note": "; ".join(dict.fromkeys(skip_notes)),
        "value_code_evidence": "; ".join(dict.fromkeys(value_notes[:12])),
    }


def health_b_question_rows(df: pd.DataFrame) -> dict[int, int]:
    rows: dict[int, int] = {}
    for row in range(df.shape[0]):
        text = clean_text(df.iat[row, 0])
        if text.startswith("-"):
            try:
                rows[int(text.replace("-", ""))] = row
            except ValueError:
                pass
    return rows


def collect_health_b_evidence(df: pd.DataFrame, question_number: int) -> dict[str, str]:
    question_rows = health_b_question_rows(df)
    start = question_rows.get(question_number)
    if start is None:
        return {
            "question_text": "",
            "question_context": "PART B: ACCESS TO HEALTH CARE",
            "unit_or_value_note": "",
            "skip_or_instruction_note": "question number not found in questionnaire sheet",
            "value_code_evidence": "",
        }
    following = [row for q, row in question_rows.items() if q > question_number and row > start]
    end = min(following) if following else df.shape[0]
    options: list[str] = []
    skip_notes: list[str] = []
    for row in range(start + 1, end):
        label = clean_text(df.iat[row, 2]) if df.shape[1] > 2 else ""
        code = clean_text(df.iat[row, 3]) if df.shape[1] > 3 else ""
        skip = clean_text(df.iat[row, 4]) if df.shape[1] > 4 else ""
        if label or code:
            options.append(f"{label}={code}" if code else label)
        if skip:
            skip_notes.append(skip)
    return {
        "question_text": clean_text(df.iat[start, 2]),
        "question_context": "PART B: ACCESS TO HEALTH CARE",
        "unit_or_value_note": "",
        "skip_or_instruction_note": "; ".join(dict.fromkeys(skip_notes)),
        "value_code_evidence": "; ".join(dict.fromkeys(options[:16])),
    }


def read_raw_metadata(path: Path, variables: list[str]) -> tuple[dict[str, str], dict[str, dict[str, str]]]:
    labels: dict[str, str] = {}
    stats: dict[str, dict[str, str]] = {}
    if pyreadstat is None or not path.exists():
        return labels, stats
    _, meta = pyreadstat.read_sav(path, metadataonly=True)
    labels = {name.lower(): clean_text(label) for name, label in zip(meta.column_names, meta.column_labels)}
    read_vars = [name for name in meta.column_names if name.lower() in {var.lower() for var in variables}]
    if not read_vars:
        return labels, stats
    df, _ = pyreadstat.read_sav(path, usecols=read_vars)
    for column in df.columns:
        series = df[column]
        numeric = pd.to_numeric(series, errors="coerce")
        stats[column.lower()] = {
            "raw_row_count": str(len(series)),
            "raw_nonmissing_rows": str(int(series.notna().sum())),
            "raw_positive_numeric_rows": str(int((numeric > 0).sum())),
            "raw_distinct_values": str(int(series.dropna().nunique())),
        }
    return labels, stats


def recall_for_health_a(variable: str) -> str:
    question = qnum(variable)
    if question in {68, 69, 71, 72, 73, 76, 77, 79, 80, 81}:
        return "past_12_months"
    if question in {62, 63, 64, 65, 66, 67, 74, 75}:
        return "past_12_months_selection_or_context"
    return "past_4_weeks"


def status_for_row(concept: str, question_text: str, note: str, value_codes: str) -> str:
    blob = f"{question_text} {note} {value_codes}".lower()
    if concept == "oop_health_expenditure":
        if "old leks" in blob:
            return "questionnaire_confirms_old_lek_payment_item_but_aggregation_not_ready"
        return "questionnaire_payment_item_seen_but_unit_or_scope_review_required"
    if concept == "care_or_barrier":
        if "afford" in blob or "too far" in blob or "unable to get" in blob:
            return "questionnaire_confirms_access_barrier_codes_but_denominator_not_ready"
        return "questionnaire_confirms_access_question_but_skip_pattern_not_ready"
    if concept == "coping_or_access_financing":
        return "questionnaire_confirms_health_financing_coping_item_but_not_minimum_recipe"
    if concept == "insurance_or_medicine_access":
        return "questionnaire_confirms_medicine_discount_access_item_but_not_minimum_recipe"
    return "questionnaire_context_seen_not_recipe_ready"


def barrier_flags(text: str) -> set[str]:
    low = text.lower()
    flags: set[str] = set()
    if "afford" in low or "money" in low or "pay" in low or "expensive" in low:
        flags.add("cost")
    if "too far" in low or "transport" in low:
        flags.add("distance")
    if "unable to get to where services were available" in low or "shortage" in low or "services only provided" in low or "referral" in low:
        flags.add("supply_or_availability")
    return flags


def base_row(concept: str, harmonized_variable: str, source_file: str, raw_variable: str) -> dict[str, str]:
    return {
        "country": COUNTRY,
        "survey_name": SURVEY_NAME,
        "wave": WAVE,
        "idno": IDNO,
        "concept": concept,
        "harmonized_variable": harmonized_variable,
        "source_workbook": QUESTIONNAIRE_PATH.name,
        "sheet_name": "",
        "source_file": source_file,
        "raw_variable": raw_variable,
        "raw_label": "",
        "question_number": str(qnum(raw_variable)),
        "question_context": "",
        "question_text": "",
        "recall_period": "",
        "unit_or_value_note": "",
        "skip_or_instruction_note": "",
        "value_code_evidence": "",
        "raw_row_count": "",
        "raw_nonmissing_rows": "",
        "raw_positive_numeric_rows": "",
        "raw_distinct_values": "",
        "semantic_evidence_status": "",
        "ready_for_recipe": "0",
        "ready_for_outcome": "0",
        "climate_linkage_ready": "0",
        "promotion_status": NO_PROMOTION,
        "blocking_reason": (
            "Questionnaire semantics strengthen the manual review evidence, but ALB_2005 still lacks a verified "
            "household interview month/date, full climate-ready geography, and an audited household aggregation rule."
        ),
        "next_action": (
            "Use this row to review raw skip paths, missing/zero coding, recall-period separation, gift/transport "
            "policy, and person-to-household aggregation before any recipe or outcome promotion."
        ),
    }


def build_rows() -> list[dict[str, str]]:
    health_a = read_sheet("(9) HEALTH - A")
    health_b = read_sheet("(9) HEALTH - B")
    a_labels, a_stats = read_raw_metadata(HEALTH_A_PATH, HEALTH_A_SELECTION_VARIABLES + FOUR_WEEK_PAYMENT_VARIABLES + TWELVE_MONTH_PAYMENT_VARIABLES)
    b_labels, b_stats = read_raw_metadata(HEALTH_B_PATH, HEALTH_B_VARIABLES)

    rows: list[dict[str, str]] = []
    for variable in HEALTH_A_SELECTION_VARIABLES:
        question_number = qnum(variable)
        evidence = collect_health_a_evidence(health_a, question_number)
        row = base_row("oop_health_expenditure", "care_visit_selection_or_oop_denominator", HEALTH_A_PATH.name, variable)
        row.update(evidence)
        row.update(a_stats.get(variable, {}))
        row["raw_label"] = a_labels.get(variable, "")
        row["sheet_name"] = "(9) HEALTH - A"
        row["recall_period"] = recall_for_health_a(variable)
        row["semantic_evidence_status"] = "questionnaire_confirms_visit_selection_skip_path_but_denominator_not_ready"
        rows.append(row)

    for variable in FOUR_WEEK_PAYMENT_VARIABLES + TWELVE_MONTH_PAYMENT_VARIABLES:
        question_number = qnum(variable)
        evidence = collect_health_a_evidence(health_a, question_number)
        row = base_row("oop_health_expenditure", "oop_health_expenditure_item", HEALTH_A_PATH.name, variable)
        row.update(evidence)
        row.update(a_stats.get(variable, {}))
        row["raw_label"] = a_labels.get(variable, "")
        row["sheet_name"] = "(9) HEALTH - A"
        row["recall_period"] = recall_for_health_a(variable)
        row["semantic_evidence_status"] = status_for_row(row["concept"], row["question_text"], row["unit_or_value_note"], row["value_code_evidence"])
        rows.append(row)

    for variable in HEALTH_B_VARIABLES:
        concept, harmonized = HEALTH_B_CONCEPT_MAP[variable]
        question_number = HEALTH_B_QUESTION_MAP[variable]
        evidence = collect_health_b_evidence(health_b, question_number)
        row = base_row(concept, harmonized, HEALTH_B_PATH.name, variable)
        row.update(evidence)
        row.update(b_stats.get(variable, {}))
        row["raw_label"] = b_labels.get(variable, "")
        row["sheet_name"] = "(9) HEALTH - B"
        row["question_number"] = str(question_number)
        row["recall_period"] = "past_12_months" if question_number <= 10 else ""
        row["semantic_evidence_status"] = status_for_row(concept, row["question_text"], row["skip_or_instruction_note"], row["value_code_evidence"])
        rows.append(row)

    return rows


def summary_row(metric: str, value: Any, interpretation: str) -> dict[str, str]:
    return {"metric": metric, "value": str(value), "interpretation": interpretation}


def build_summary(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    required_summary = read_csv_dicts(REQUIRED_VALUE_KEY_SUMMARY_PATH)
    value_decision_summary = read_csv_dicts(VALUE_DECISION_SUMMARY_PATH)
    access_rows = [row for row in rows if row["concept"] == "care_or_barrier"]
    oop_rows = [row for row in rows if row["harmonized_variable"] == "oop_health_expenditure_item"]
    flags = Counter(flag for row in access_rows for flag in barrier_flags(row["value_code_evidence"]))
    status_counts = Counter(row["semantic_evidence_status"] for row in rows)
    summary = [
        summary_row("alb2005_health_questionnaire_semantics_rows", len(rows), "Rows in the ALB_2005 health questionnaire semantics audit."),
        summary_row("alb2005_health_questionnaire_oop_item_rows", len(oop_rows), "Questionnaire-backed OOP payment item rows."),
        summary_row("alb2005_health_questionnaire_visit_selection_rows", sum(1 for row in rows if row["harmonized_variable"] == "care_visit_selection_or_oop_denominator"), "Visit/stay/purchase selection rows needed for OOP denominators."),
        summary_row("alb2005_health_questionnaire_access_rows", len(access_rows), "Access, delayed-care, referral, refusal, and barrier rows from health module B."),
        summary_row("alb2005_health_questionnaire_four_week_oop_rows", sum(1 for row in oop_rows if row["recall_period"] == "past_4_weeks"), "OOP item rows with past-four-week recall."),
        summary_row("alb2005_health_questionnaire_twelve_month_oop_rows", sum(1 for row in oop_rows if row["recall_period"] == "past_12_months"), "OOP item rows with past-12-month recall."),
        summary_row("alb2005_health_questionnaire_old_lek_unit_rows", sum(1 for row in rows if "OLD LEKS" in row["unit_or_value_note"].upper()), "Rows where the questionnaire explicitly records old-lek units."),
        summary_row("alb2005_health_questionnaire_exclusion_note_rows", sum(1 for row in rows if "EXCLUDE" in row["skip_or_instruction_note"].upper()), "Rows with explicit exclusion notes for gifts, medicines, laboratory, or transport."),
        summary_row("alb2005_health_questionnaire_zero_instruction_rows", sum(1 for row in rows if "ZERO" in row["skip_or_instruction_note"].upper()), "Rows with explicit zero-payment instructions."),
        summary_row("alb2005_health_questionnaire_cost_barrier_rows", flags["cost"], "Access rows whose questionnaire options include cost or affordability barriers."),
        summary_row("alb2005_health_questionnaire_distance_barrier_rows", flags["distance"], "Access rows whose questionnaire options include distance or transport barriers."),
        summary_row("alb2005_health_questionnaire_supply_barrier_rows", flags["supply_or_availability"], "Access rows whose questionnaire options include availability, service-region, referral, or shortage barriers."),
        summary_row("alb2005_health_questionnaire_recipe_ready_rows", 0, "Rows promoted to a harmonization recipe by this audit; intentionally zero."),
        summary_row("alb2005_health_questionnaire_outcome_ready_rows", 0, "Rows promoted to constructed outcomes by this audit; intentionally zero."),
        summary_row("alb2005_health_questionnaire_climate_linkage_ready_rows", 0, "Rows promoted to climate linkage by this audit; intentionally zero."),
        summary_row("alb2005_health_questionnaire_required_value_key_recipe_ready_observed", metric_value(required_summary, "alb2005_required_value_key_recipe_ready_rows"), "Recipe-ready rows observed in the required value/key audit."),
        summary_row("alb2005_health_questionnaire_required_value_key_climate_ready_observed", metric_value(required_summary, "alb2005_required_value_key_climate_linkage_ready_rows"), "Climate-linkage-ready rows observed in the required value/key audit."),
        summary_row("alb2005_health_questionnaire_value_decision_recipe_ready_observed", metric_value(value_decision_summary, "alb2005_harmonization_value_decision_recipe_ready_rows"), "Recipe-ready rows observed in the value-decision audit."),
        summary_row("alb2005_health_questionnaire_current_decision", DECISION, "Current fail-closed decision for questionnaire-backed ALB_2005 health semantics."),
    ]
    for status, count in sorted(status_counts.items()):
        summary.append(summary_row(f"alb2005_health_questionnaire_status_{status}", count, "Rows by questionnaire semantic status."))
    return summary


def markdown_rows(rows: list[dict[str, str]], columns: list[str], limit: int = 18) -> str:
    lines = ["| " + " | ".join(columns) + " |", "|" + "|".join("---" for _ in columns) + "|"]
    for row in rows[:limit]:
        values = []
        for column in columns:
            value = (row.get(column, "") or "").replace("|", "/")
            if len(value) > 140:
                value = value[:137] + "..."
            values.append(value)
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines)


def markdown_count_table(counter: Counter[str], label: str) -> str:
    lines = [f"| {label} | Count |", "|---|---:|"]
    for key, count in counter.most_common():
        lines.append(f"| {key or 'blank'} | {count} |")
    return "\n".join(lines)


def write_report(rows: list[dict[str, str]], summary: list[dict[str, str]]) -> None:
    status_counts = Counter(row["semantic_evidence_status"] for row in rows)
    concept_counts = Counter(row["concept"] for row in rows)
    summary_table = "\n".join(f"| {row['metric']} | {row['value']} | {row['interpretation']} |" for row in summary)
    oop_rows = [row for row in rows if row["harmonized_variable"] == "oop_health_expenditure_item"]
    access_rows = [row for row in rows if row["concept"] == "care_or_barrier"]
    report = f"""# ALB_2005 Health Questionnaire Semantics Audit

Status: fail-closed questionnaire semantics audit. This report reads the ALB_2005 health questionnaire workbook and SPSS health modules to document recall periods, old-lek unit notes, payment-scope exclusions, zero-payment instructions, access-barrier value codes, and raw variable coverage. It does not write `data/`, does not construct outcomes, and does not promote any row to a harmonization recipe or climate linkage.

## Bottom Line

- The ALB_2005 health questionnaire is readable in the current Python environment.
- OOP payment questions are documented as old-lek payment items, split across past-four-week outpatient/self-medication contexts and past-12-month inpatient/dental contexts.
- Several provider-charge questions explicitly exclude gifts, medicines, laboratory work, and transport, so OOP aggregation must preserve item scope rather than blindly summing provider totals and components.
- Health module B documents 12-month access, delayed-care, referral, refusal, cost, distance, and service-availability barriers, but denominator and skip-pattern reconstruction still requires raw-value review.
- Recipe-ready, outcome-ready, and climate-linkage-ready rows from this audit: 0.
- Current decision: `{DECISION}`.

## Summary

| Metric | Value | Interpretation |
|---|---:|---|
{summary_table}

## Concept Counts

{markdown_count_table(concept_counts, 'Concept') if rows else 'No rows.'}

## Semantic Status Counts

{markdown_count_table(status_counts, 'Semantic status') if rows else 'No rows.'}

## OOP Questionnaire Rows

{markdown_rows(oop_rows, ['raw_variable', 'raw_label', 'question_text', 'recall_period', 'unit_or_value_note', 'skip_or_instruction_note', 'raw_nonmissing_rows', 'raw_positive_numeric_rows'], 40) if oop_rows else 'No OOP rows found.'}

## Access And Barrier Rows

{markdown_rows(access_rows, ['raw_variable', 'raw_label', 'question_text', 'value_code_evidence', 'skip_or_instruction_note', 'raw_nonmissing_rows', 'semantic_evidence_status'], 20) if access_rows else 'No access rows found.'}

## Interpretation

- This audit resolves one narrow documentation question: the questionnaire text is readable and confirms important health-module semantics for ALB_2005.
- It does not resolve household interview timing, GPS/coordinate absence, partial district coverage, household-level OOP aggregation, missing/zero coding, or whether gift/transport components should enter each final outcome family.
- Four-week and twelve-month OOP items must remain separate until an outcome protocol explicitly defines comparable recall-period transformations.
- Access-barrier rows must remain denominator-blocked until raw skip paths establish which households/persons were eligible for each question.

## Machine-Readable Outputs

- `temp/alb2005_health_questionnaire_semantics_audit.csv`
- `result/alb2005_health_questionnaire_semantics_summary.csv`
"""
    REPORT_PATH.write_text(report, encoding="utf-8")


def main() -> None:
    ensure_dirs()
    rows = build_rows()
    summary = build_summary(rows)
    write_csv(AUDIT_PATH, rows, AUDIT_COLUMNS)
    write_csv(SUMMARY_PATH, summary, SUMMARY_COLUMNS)
    write_report(rows, summary)
    append_log(
        TEMP_DIR / "audit_log.md",
        f"Built ALB_2005 health questionnaire semantics audit rows={len(rows)} decision={DECISION}.",
    )
    print(f"ALB_2005 health questionnaire semantics rows={len(rows)} decision={DECISION}.")


if __name__ == "__main__":
    main()
