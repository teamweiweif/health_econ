from __future__ import annotations

import csv
import math
import re
import warnings
from collections import Counter
from pathlib import Path
from typing import Any, Callable

import pandas as pd

from common import REPORT_DIR, RESULT_DIR, TEMP_DIR, append_log, ensure_dirs, write_csv

try:
    import pyreadstat
except ImportError:  # pragma: no cover - environment audit covers this.
    pyreadstat = None


IDNO = "ALB_2002_LSMS_v01_M"
COUNTRY = "Albania"
SURVEY_NAME = "Living Standards Measurement Survey 2002"
WAVE = "2002"

RAW_ROOT = TEMP_DIR / "raw_extracted" / "lsms2002en_4dbf0b087520" / "lsms2002en"
QUESTIONNAIRE_PATH = RAW_ROOT / "Questionnaire 2002" / "LSMS02_Questionnaire.xls"
DATA_ROOT = RAW_ROOT / "Data_2002"
HEALTH_A_PATH = DATA_ROOT / "Modul_5A_Health.sav"
HEALTH_B_PATH = DATA_ROOT / "Modul_5B_Health.sav"

OUTCOME_SEMANTICS_SUMMARY_PATH = RESULT_DIR / "alb2002_outcome_semantics_raw_value_summary.csv"
CORE_SUMMARY_PATH = RESULT_DIR / "alb2002_household_core_candidate_summary.csv"
BOUNDARY_SUMMARY_PATH = RESULT_DIR / "alb2002_gadm_boundary_lead_summary.csv"

AUDIT_PATH = TEMP_DIR / "alb2002_health_questionnaire_semantics_audit.csv"
SUMMARY_PATH = RESULT_DIR / "alb2002_health_questionnaire_semantics_summary.csv"
REPORT_PATH = REPORT_DIR / "alb2002_health_questionnaire_semantics_audit.md"

DECISION = "blocked_alb2002_questionnaire_semantics_seen_but_outcome_not_ready"
NO_PROMOTION = "not_promoted_questionnaire_semantics_audit_only"

AUDIT_COLUMNS = [
    "country",
    "survey_name",
    "wave",
    "idno",
    "audit_family",
    "concept",
    "source_workbook",
    "sheet_name",
    "source_file",
    "raw_variable",
    "trigger_variable",
    "downstream_variables",
    "question_number",
    "question_context",
    "question_text",
    "recall_period",
    "unit_or_value_note",
    "skip_or_instruction_note",
    "value_code_evidence",
    "raw_label",
    "raw_row_count",
    "raw_nonmissing_rows",
    "raw_positive_numeric_rows",
    "raw_distinct_values",
    "trigger_positive_rows",
    "trigger_negative_rows",
    "trigger_missing_rows",
    "downstream_any_nonmissing_when_not_triggered_rows",
    "downstream_any_positive_when_not_triggered_rows",
    "downstream_zero_or_missing_when_triggered_rows",
    "dependent_missing_when_triggered_rows",
    "semantic_evidence_status",
    "ready_for_recipe",
    "ready_for_outcome",
    "sdg382_ready",
    "climate_linkage_ready",
    "promotion_status",
    "blocking_reason",
    "next_action",
]
SUMMARY_COLUMNS = ["metric", "value", "interpretation"]

FOUR_WEEK_PAYMENT_VARIABLES = [
    "m5a_q14",
    "m5a_q18",
    "m5a_q20",
    "m5a_q21",
    "m5a_q24",
    "m5a_q27",
    "m5a_q28",
    "m5a_q29",
    "m5a_q32",
    "m5a_q35",
    "m5a_q36",
    "m5a_q37",
    "m5a_q40",
    "m5a_q43",
    "m5a_q44",
    "m5a_q45",
    "m5a_q47",
]
TWELVE_MONTH_PAYMENT_VARIABLES = [
    "m5a_q53",
    "m5a_q56",
    "m5a_q57",
    "m5a_q58",
    "m5a_q61",
    "m5a_q64",
    "m5a_q65",
    "m5a_q66",
]
GIFT_PAYMENT_VARIABLES = ["m5a_q15", "m5a_q25", "m5a_q33", "m5a_q41", "m5a_q54", "m5a_q62"]
HEALTH_A_SELECTION_VARIABLES = ["m5a_q12", "m5a_q17", "m5a_q22", "m5a_q30", "m5a_q38", "m5a_q46", "m5a_q48", "m5a_q59"]

HEALTH_B_VARIABLES = [
    "m5b_q01",
    "m5b_q02_",
    "m5b_q021",
    "m5b_q022",
    "m5b_q023",
    "m5b_q024",
    "m5b_q03",
    "m5b_q04",
    "m5b_q05",
    "m5b_q06",
    "m5b_q07",
    "m5b_q08",
    "m5b_q09",
    "m5b_q10",
]

HEALTH_B_QUESTION_MAP = {
    "m5b_q01": 1,
    "m5b_q02_": 2,
    "m5b_q021": 2,
    "m5b_q022": 2,
    "m5b_q023": 2,
    "m5b_q024": 2,
    "m5b_q03": 3,
    "m5b_q04": 4,
    "m5b_q05": 5,
    "m5b_q06": 6,
    "m5b_q07": 7,
    "m5b_q08": 8,
    "m5b_q09": 9,
    "m5b_q10": 10,
}
HEALTH_B_CONCEPT_MAP = {
    "m5b_q01": "access_affordability",
    "m5b_q02_": "coping_or_health_financing",
    "m5b_q021": "coping_or_health_financing",
    "m5b_q022": "coping_or_health_financing",
    "m5b_q023": "coping_or_health_financing",
    "m5b_q024": "coping_or_health_financing",
    "m5b_q03": "care_or_barrier",
    "m5b_q04": "care_or_barrier",
    "m5b_q05": "care_or_barrier",
    "m5b_q06": "care_or_barrier",
    "m5b_q07": "care_or_barrier",
    "m5b_q08": "care_or_barrier",
    "m5b_q09": "medicine_discount_coverage",
    "m5b_q10": "medicine_discount_access",
}

PAYMENT_SKIP_BLOCKS = [
    ("public_ambulatory_4w", "m5a_q12", ["m5a_q14", "m5a_q15", "m5a_q18", "m5a_q20", "m5a_q21"], "past_4_weeks"),
    ("private_doctor_4w", "m5a_q22", ["m5a_q24", "m5a_q25", "m5a_q27", "m5a_q28", "m5a_q29"], "past_4_weeks"),
    ("nurse_paramedic_midwife_4w", "m5a_q30", ["m5a_q32", "m5a_q33", "m5a_q35", "m5a_q36", "m5a_q37"], "past_4_weeks"),
    ("popular_doctor_4w", "m5a_q38", ["m5a_q40", "m5a_q41", "m5a_q43", "m5a_q44", "m5a_q45"], "past_4_weeks"),
    ("own_drugs_4w", "m5a_q46", ["m5a_q47"], "past_4_weeks"),
    ("hospital_stay_12m", "m5a_q48", ["m5a_q53", "m5a_q54", "m5a_q56", "m5a_q57", "m5a_q58"], "past_12_months"),
    ("dentist_12m", "m5a_q59", ["m5a_q61", "m5a_q62", "m5a_q64", "m5a_q65", "m5a_q66"], "past_12_months"),
]

CONDITIONAL_SKIP_BLOCKS = [
    ("raise_money_for_health_care_methods", "m5b_q01", lambda s: s.isin([1, 2]), "1-2", "3-4", ["m5b_q02_", "m5b_q021", "m5b_q022", "m5b_q023", "m5b_q024"]),
    ("delayed_or_no_help_reason", "m5b_q03", lambda s: s > 1, "2-5", "1", ["m5b_q04"]),
    ("hospital_referral_not_gone_reason", "m5b_q05", lambda s: s > 1, "2-5", "1", ["m5b_q06"]),
    ("refused_health_services_reason", "m5b_q07", lambda s: s == 1, "1", "2", ["m5b_q08"]),
    ("medicine_discount_access_reason", "m5b_q09", lambda s: s == 1, "1", "2", ["m5b_q10"]),
]


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
    if isinstance(value, float) and math.isfinite(value) and value.is_integer():
        value = int(value)
    text = " ".join(str(value).split())
    return text.encode("ascii", "replace").decode("ascii")


def compact_join(values: list[Any], limit: int = 12) -> str:
    out: list[str] = []
    seen: set[str] = set()
    for value in values:
        clean = clean_text(value)
        if not clean or clean in seen:
            continue
        out.append(clean)
        seen.add(clean)
        if len(out) >= limit:
            break
    return "; ".join(out)


def qnum(variable: str) -> int:
    match = re.search(r"_q0*([0-9]+)_?$", variable.lower())
    return int(match.group(1)) if match else 0


def read_sheet(sheet_name: str) -> pd.DataFrame:
    return pd.read_excel(QUESTIONNAIRE_PATH, sheet_name=sheet_name, header=None, dtype=object)


def read_sav(path: Path, usecols: list[str] | None = None) -> tuple[pd.DataFrame, Any]:
    if pyreadstat is None:
        raise RuntimeError("pyreadstat is not available")
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        return pyreadstat.read_sav(str(path), usecols=usecols, apply_value_formats=False)


def metadata_maps(meta: Any) -> tuple[dict[str, str], dict[str, str]]:
    labels = {name.lower(): clean_text(label) for name, label in zip(meta.column_names, meta.column_labels)}
    value_examples: dict[str, str] = {}
    for variable in meta.column_names:
        value_map = (meta.variable_value_labels or {}).get(variable, {})
        value_examples[variable.lower()] = compact_join([f"{fmt(code)}={label}" for code, label in value_map.items()], 12)
    return labels, value_examples


def raw_stats(df: pd.DataFrame, variable: str) -> dict[str, str]:
    if variable not in df.columns:
        return {"raw_row_count": "0", "raw_nonmissing_rows": "0", "raw_positive_numeric_rows": "0", "raw_distinct_values": "0"}
    series = df[variable]
    numeric = pd.to_numeric(series, errors="coerce")
    return {
        "raw_row_count": str(len(series)),
        "raw_nonmissing_rows": str(int(series.notna().sum())),
        "raw_positive_numeric_rows": str(int((numeric > 0).sum())),
        "raw_distinct_values": str(int(series.dropna().nunique())),
    }


def find_health_a_column(df: pd.DataFrame, question_number: int) -> int | None:
    target = f"-{question_number}"
    for col in range(df.shape[1]):
        if clean_text(df.iat[3, col]) == target:
            return col
    return None


def nearest_left_context(df: pd.DataFrame, col: int) -> str:
    for row in [2, 1, 0]:
        for left in range(col, -1, -1):
            text = clean_text(df.iat[row, left])
            if text:
                return text
    return ""


def collect_health_a_evidence(df: pd.DataFrame, question_number: int) -> dict[str, str]:
    col = find_health_a_column(df, question_number)
    if col is None:
        return {
            "question_context": "",
            "question_text": "",
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
            upper = text.upper()
            if any(token in upper for token in ["NEW LEKS", "OLD LEKS", "TIMES", "DAYS", "MONTHS", "YEARS"]):
                unit_notes.append(text)
            if any(token in upper for token in ["EXCLUDE", "ZERO", ">>", "IF NO", "PLEASE REPORT"]):
                skip_notes.append(text)
            if row >= 18 and len(text) <= 90:
                value_notes.append(text)
    return {
        "question_context": nearest_left_context(df, col),
        "question_text": clean_text(df.iat[4, col]),
        "unit_or_value_note": compact_join(unit_notes, 12),
        "skip_or_instruction_note": compact_join(skip_notes, 12),
        "value_code_evidence": compact_join(value_notes, 12),
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
            "question_context": "PART B: ACCESS TO HEALTH CARE",
            "question_text": "",
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
        "question_context": "PART B: ACCESS TO HEALTH CARE",
        "question_text": clean_text(df.iat[start, 2]),
        "unit_or_value_note": "",
        "skip_or_instruction_note": compact_join(skip_notes, 12),
        "value_code_evidence": compact_join(options, 20),
    }


def recall_for_health_a(variable: str) -> str:
    question = qnum(variable)
    if question in {48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66}:
        return "past_12_months"
    if question in {12, 13, 14, 15, 17, 18, 20, 21, 22, 23, 24, 25, 27, 28, 29, 30, 31, 32, 33, 35, 36, 37, 38, 39, 40, 41, 43, 44, 45, 46, 47}:
        return "past_4_weeks"
    return ""


def base_row(audit_family: str, concept: str, source_file: str, raw_variable: str = "") -> dict[str, str]:
    return {
        "country": COUNTRY,
        "survey_name": SURVEY_NAME,
        "wave": WAVE,
        "idno": IDNO,
        "audit_family": audit_family,
        "concept": concept,
        "source_workbook": QUESTIONNAIRE_PATH.name,
        "sheet_name": "",
        "source_file": source_file,
        "raw_variable": raw_variable,
        "trigger_variable": "",
        "downstream_variables": "",
        "question_number": str(qnum(raw_variable)) if raw_variable else "",
        "question_context": "",
        "question_text": "",
        "recall_period": "",
        "unit_or_value_note": "",
        "skip_or_instruction_note": "",
        "value_code_evidence": "",
        "raw_label": "",
        "raw_row_count": "",
        "raw_nonmissing_rows": "",
        "raw_positive_numeric_rows": "",
        "raw_distinct_values": "",
        "trigger_positive_rows": "",
        "trigger_negative_rows": "",
        "trigger_missing_rows": "",
        "downstream_any_nonmissing_when_not_triggered_rows": "",
        "downstream_any_positive_when_not_triggered_rows": "",
        "downstream_zero_or_missing_when_triggered_rows": "",
        "dependent_missing_when_triggered_rows": "",
        "semantic_evidence_status": "",
        "ready_for_recipe": "0",
        "ready_for_outcome": "0",
        "sdg382_ready": "0",
        "climate_linkage_ready": "0",
        "promotion_status": NO_PROMOTION,
        "blocking_reason": (
            "Questionnaire and raw skip evidence strengthen ALB_2002 manual review, but final outcome promotion still "
            "requires denominator period/unit review, missing-code policy, person-to-household aggregation, SDG 3.8.2 "
            "inputs, and climate-ready geography."
        ),
        "next_action": (
            "Use this audit to decide OOP scope, recall-period separation, gift/transport policy, access-denominator "
            "rules, and missing/zero coding before any harmonization or outcome promotion."
        ),
    }


def health_a_status(concept: str, evidence: dict[str, str]) -> str:
    text = f"{evidence.get('question_text', '')} {evidence.get('unit_or_value_note', '')} {evidence.get('skip_or_instruction_note', '')}".upper()
    if concept == "gift_payment_scope":
        return "questionnaire_confirms_gift_value_item_scope_policy_required"
    if "EXCLUDE GIFTS" in text:
        return "questionnaire_confirms_provider_payment_excludes_gifts_medicines_lab_transport"
    if "NEW LEKS" in text:
        return "questionnaire_confirms_new_lek_payment_item_but_recall_scope_not_ready"
    if concept == "care_visit_selection_or_denominator":
        return "questionnaire_confirms_visit_selection_skip_path_but_denominator_not_ready"
    return "questionnaire_context_seen_not_recipe_ready"


def barrier_flags(text: str) -> set[str]:
    low = text.lower()
    flags: set[str] = set()
    if any(token in low for token in ["afford", "money", "pay", "treatment", "discount"]):
        flags.add("cost")
    if "too far" in low or "transport" in low:
        flags.add("distance")
    if any(token in low for token in ["unable to get to where services were available", "shortage", "services only provided", "referral", "bureaucratic"]):
        flags.add("supply_or_availability")
    return flags


def health_b_status(concept: str, evidence: dict[str, str]) -> str:
    text = f"{evidence.get('question_text', '')} {evidence.get('value_code_evidence', '')}".lower()
    if concept in {"care_or_barrier", "access_affordability", "medicine_discount_access"} and barrier_flags(text):
        return "questionnaire_confirms_access_barrier_codes_but_denominator_not_ready"
    if concept == "coping_or_health_financing":
        return "questionnaire_confirms_health_financing_coping_item_but_denominator_not_ready"
    if concept == "medicine_discount_coverage":
        return "questionnaire_confirms_medicine_discount_entitlement_but_not_failure_outcome"
    return "questionnaire_context_seen_not_recipe_ready"


def add_questionnaire_rows(rows: list[dict[str, str]], labels_a: dict[str, str], labels_b: dict[str, str], health_a: pd.DataFrame, health_b: pd.DataFrame, raw_a: pd.DataFrame, raw_b: pd.DataFrame) -> None:
    variables = HEALTH_A_SELECTION_VARIABLES + FOUR_WEEK_PAYMENT_VARIABLES + TWELVE_MONTH_PAYMENT_VARIABLES + GIFT_PAYMENT_VARIABLES
    for variable in variables:
        concept = "care_visit_selection_or_denominator"
        if variable in FOUR_WEEK_PAYMENT_VARIABLES or variable in TWELVE_MONTH_PAYMENT_VARIABLES:
            concept = "oop_health_expenditure_item"
        elif variable in GIFT_PAYMENT_VARIABLES:
            concept = "gift_payment_scope"
        evidence = collect_health_a_evidence(health_a, qnum(variable))
        row = base_row("health_a_questionnaire", concept, HEALTH_A_PATH.name, variable)
        row.update(evidence)
        row.update(raw_stats(raw_a, variable))
        row["sheet_name"] = "(5) HEALTH - A"
        row["raw_label"] = labels_a.get(variable, "")
        row["recall_period"] = recall_for_health_a(variable)
        row["semantic_evidence_status"] = health_a_status(concept, evidence)
        rows.append(row)

    for variable in HEALTH_B_VARIABLES:
        concept = HEALTH_B_CONCEPT_MAP[variable]
        evidence = collect_health_b_evidence(health_b, HEALTH_B_QUESTION_MAP[variable])
        row = base_row("health_b_questionnaire", concept, HEALTH_B_PATH.name, variable)
        row.update(evidence)
        row.update(raw_stats(raw_b, variable))
        row["sheet_name"] = "(5) HEALTH - B"
        row["raw_label"] = labels_b.get(variable, "")
        row["question_number"] = str(HEALTH_B_QUESTION_MAP[variable])
        row["recall_period"] = "past_12_months"
        row["semantic_evidence_status"] = health_b_status(concept, evidence)
        rows.append(row)


def numeric_frame(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    return df[columns].apply(pd.to_numeric, errors="coerce")


def top_values(series: pd.Series, limit: int = 8) -> str:
    counts = series.dropna().value_counts(dropna=True).head(limit)
    return compact_join([f"{fmt(idx)}:{int(count)}" for idx, count in counts.items()], limit)


def add_payment_skip_rows(rows: list[dict[str, str]], raw_a: pd.DataFrame, labels_a: dict[str, str]) -> None:
    for subdomain, trigger, downstream, recall in PAYMENT_SKIP_BLOCKS:
        trigger_values = pd.to_numeric(raw_a[trigger], errors="coerce")
        payment_values = numeric_frame(raw_a, downstream)
        triggered = trigger_values == 1
        not_triggered = trigger_values == 2
        any_nonmissing = payment_values.notna().any(axis=1)
        any_positive = (payment_values.fillna(0) > 0).any(axis=1)
        nonmissing_when_not = int((not_triggered & any_nonmissing).sum())
        positive_when_not = int((not_triggered & any_positive).sum())
        zero_or_missing_when_triggered = int((triggered & ~any_positive).sum())
        row = base_row("payment_skip_path", "oop_payment_skip_path", HEALTH_A_PATH.name)
        row.update(
            {
                "trigger_variable": trigger,
                "downstream_variables": ";".join(downstream),
                "question_number": str(qnum(trigger)),
                "question_context": subdomain,
                "question_text": labels_a.get(trigger, ""),
                "recall_period": recall,
                "raw_label": labels_a.get(trigger, ""),
                "raw_row_count": str(len(raw_a)),
                "trigger_positive_rows": str(int(triggered.sum())),
                "trigger_negative_rows": str(int(not_triggered.sum())),
                "trigger_missing_rows": str(int(trigger_values.isna().sum())),
                "downstream_any_nonmissing_when_not_triggered_rows": str(nonmissing_when_not),
                "downstream_any_positive_when_not_triggered_rows": str(positive_when_not),
                "downstream_zero_or_missing_when_triggered_rows": str(zero_or_missing_when_triggered),
                "value_code_evidence": f"{trigger}: {top_values(raw_a[trigger])}; downstream: {compact_join([f'{var} {top_values(raw_a[var], 4)}' for var in downstream], 10)}",
                "semantic_evidence_status": "raw_skip_path_positive_values_absent_when_not_triggered_but_zero_nonmissing_review_required"
                if positive_when_not == 0 and nonmissing_when_not > 0
                else "raw_skip_path_consistent_no_downstream_values_when_not_triggered"
                if positive_when_not == 0 and nonmissing_when_not == 0
                else "raw_skip_path_has_positive_downstream_values_when_not_triggered_review_required",
            }
        )
        rows.append(row)


def add_conditional_skip_rows(rows: list[dict[str, str]], raw_b: pd.DataFrame, labels_b: dict[str, str]) -> None:
    for subdomain, trigger, positive_fn, positive_codes, negative_codes, downstream in CONDITIONAL_SKIP_BLOCKS:
        trigger_values = pd.to_numeric(raw_b[trigger], errors="coerce")
        downstream_values = raw_b[downstream]
        triggered = positive_fn(trigger_values)
        not_triggered = (~triggered) & trigger_values.notna()
        any_nonmissing = downstream_values.notna().any(axis=1)
        any_positive = (numeric_frame(raw_b, downstream).fillna(0) > 0).any(axis=1)
        nonmissing_when_not = int((not_triggered & any_nonmissing).sum())
        missing_when_triggered = int((triggered & downstream_values.isna().all(axis=1)).sum())
        row = base_row("conditional_skip_path", "access_or_coping_skip_path", HEALTH_B_PATH.name)
        row.update(
            {
                "trigger_variable": trigger,
                "downstream_variables": ";".join(downstream),
                "question_number": str(HEALTH_B_QUESTION_MAP.get(trigger, "")),
                "question_context": subdomain,
                "question_text": labels_b.get(trigger, ""),
                "recall_period": "past_12_months",
                "raw_label": labels_b.get(trigger, ""),
                "raw_row_count": str(len(raw_b)),
                "trigger_positive_rows": str(int(triggered.sum())),
                "trigger_negative_rows": str(int(not_triggered.sum())),
                "trigger_missing_rows": str(int(trigger_values.isna().sum())),
                "unit_or_value_note": f"trigger positive codes={positive_codes}; trigger negative codes={negative_codes}",
                "downstream_any_nonmissing_when_not_triggered_rows": str(nonmissing_when_not),
                "downstream_any_positive_when_not_triggered_rows": str(int((not_triggered & any_positive).sum())),
                "dependent_missing_when_triggered_rows": str(missing_when_triggered),
                "value_code_evidence": f"{trigger}: {top_values(raw_b[trigger])}; downstream: {compact_join([f'{var} {top_values(raw_b[var], 6)}' for var in downstream], 10)}",
                "semantic_evidence_status": "raw_conditional_skip_path_consistent"
                if nonmissing_when_not == 0 and missing_when_triggered == 0
                else "raw_conditional_skip_path_review_required",
            }
        )
        rows.append(row)


def build_rows() -> list[dict[str, str]]:
    health_a_sheet = read_sheet("(5) HEALTH - A")
    health_b_sheet = read_sheet("(5) HEALTH - B")
    raw_a_vars = sorted(set(HEALTH_A_SELECTION_VARIABLES + FOUR_WEEK_PAYMENT_VARIABLES + TWELVE_MONTH_PAYMENT_VARIABLES + GIFT_PAYMENT_VARIABLES + [trigger for _, trigger, _, _ in PAYMENT_SKIP_BLOCKS] + [var for _, _, downstream, _ in PAYMENT_SKIP_BLOCKS for var in downstream]))
    raw_b_vars = sorted(set(HEALTH_B_VARIABLES + [trigger for _, trigger, *_ in CONDITIONAL_SKIP_BLOCKS] + [var for *_, downstream in CONDITIONAL_SKIP_BLOCKS for var in downstream]))
    raw_a, meta_a = read_sav(HEALTH_A_PATH, raw_a_vars)
    raw_b, meta_b = read_sav(HEALTH_B_PATH, raw_b_vars)
    labels_a, _ = metadata_maps(meta_a)
    labels_b, _ = metadata_maps(meta_b)

    rows: list[dict[str, str]] = []
    add_questionnaire_rows(rows, labels_a, labels_b, health_a_sheet, health_b_sheet, raw_a, raw_b)
    add_payment_skip_rows(rows, raw_a, labels_a)
    add_conditional_skip_rows(rows, raw_b, labels_b)
    return rows


def int_sum(rows: list[dict[str, str]], field: str, audit_family: str | None = None) -> int:
    selected = rows if audit_family is None else [row for row in rows if row["audit_family"] == audit_family]
    total = 0
    for row in selected:
        try:
            total += int(float(row.get(field, "0") or 0))
        except ValueError:
            pass
    return total


def summary_row(metric: str, value: Any, interpretation: str) -> dict[str, str]:
    return {"metric": metric, "value": fmt(value), "interpretation": interpretation}


def build_summary(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    outcome_summary = read_csv_dicts(OUTCOME_SEMANTICS_SUMMARY_PATH)
    core_summary = read_csv_dicts(CORE_SUMMARY_PATH)
    boundary_summary = read_csv_dicts(BOUNDARY_SUMMARY_PATH)
    questionnaire_rows = [row for row in rows if row["audit_family"].endswith("_questionnaire")]
    oop_rows = [row for row in rows if row["concept"] == "oop_health_expenditure_item"]
    gift_rows = [row for row in rows if row["concept"] == "gift_payment_scope"]
    access_rows = [row for row in rows if row["concept"] in {"care_or_barrier", "access_affordability", "medicine_discount_access"}]
    payment_skip_rows = [row for row in rows if row["audit_family"] == "payment_skip_path"]
    conditional_skip_rows = [row for row in rows if row["audit_family"] == "conditional_skip_path"]
    flags = Counter(flag for row in access_rows for flag in barrier_flags(f"{row['question_text']} {row['value_code_evidence']}"))
    return [
        summary_row("alb2002_health_questionnaire_semantics_rows", len(rows), "Rows in the ALB_2002 health questionnaire and skip-path audit."),
        summary_row("alb2002_health_questionnaire_questionnaire_rows", len(questionnaire_rows), "Questionnaire-backed health variable rows."),
        summary_row("alb2002_health_questionnaire_oop_item_rows", len(oop_rows), "Questionnaire-backed OOP payment item rows excluding gift-value rows."),
        summary_row("alb2002_health_questionnaire_gift_item_rows", len(gift_rows), "Gift/payment-scope rows that require inclusion-policy review."),
        summary_row("alb2002_health_questionnaire_new_lek_unit_rows", sum(1 for row in questionnaire_rows if "NEW LEKS" in row["unit_or_value_note"].upper()), "Rows where the questionnaire explicitly records new-lek units."),
        summary_row("alb2002_health_questionnaire_four_week_oop_rows", sum(1 for row in oop_rows if row["recall_period"] == "past_4_weeks"), "OOP item rows with past-four-week recall."),
        summary_row("alb2002_health_questionnaire_twelve_month_oop_rows", sum(1 for row in oop_rows if row["recall_period"] == "past_12_months"), "OOP item rows with past-12-month recall."),
        summary_row("alb2002_health_questionnaire_exclusion_note_rows", sum(1 for row in questionnaire_rows if "EXCLUDE" in row["skip_or_instruction_note"].upper()), "Questionnaire rows with explicit exclusion notes for gifts, medicines, laboratory, or transport."),
        summary_row("alb2002_health_questionnaire_zero_instruction_rows", sum(1 for row in questionnaire_rows if "ZERO" in row["skip_or_instruction_note"].upper()), "Questionnaire rows with explicit zero-payment instructions."),
        summary_row("alb2002_health_questionnaire_access_rows", len(access_rows), "Access, affordability, delayed-care, referral, refusal, or medicine-discount rows."),
        summary_row("alb2002_health_questionnaire_cost_barrier_rows", flags["cost"], "Access rows whose questionnaire options include cost or affordability barriers."),
        summary_row("alb2002_health_questionnaire_distance_barrier_rows", flags["distance"], "Access rows whose questionnaire options include distance barriers."),
        summary_row("alb2002_health_questionnaire_supply_barrier_rows", flags["supply_or_availability"], "Access rows whose questionnaire options include availability, service-region, referral, document, or shortage barriers."),
        summary_row("alb2002_health_questionnaire_payment_skip_rows", len(payment_skip_rows), "Person-level OOP payment skip-path rows audited."),
        summary_row("alb2002_health_questionnaire_payment_nonmissing_when_not_triggered_rows", int_sum(rows, "downstream_any_nonmissing_when_not_triggered_rows", "payment_skip_path"), "Payment downstream rows nonmissing when the visit/drug/stay/dentist trigger is negative."),
        summary_row("alb2002_health_questionnaire_payment_positive_when_not_triggered_rows", int_sum(rows, "downstream_any_positive_when_not_triggered_rows", "payment_skip_path"), "Payment downstream rows positive when the trigger is negative."),
        summary_row("alb2002_health_questionnaire_payment_zero_or_missing_when_triggered_rows", int_sum(rows, "downstream_zero_or_missing_when_triggered_rows", "payment_skip_path"), "Triggered payment rows with no positive downstream payment; requires zero/missing-code review."),
        summary_row("alb2002_health_questionnaire_conditional_skip_rows", len(conditional_skip_rows), "Household access/coping conditional skip rows audited."),
        summary_row("alb2002_health_questionnaire_conditional_nonmissing_when_not_triggered_rows", int_sum(rows, "downstream_any_nonmissing_when_not_triggered_rows", "conditional_skip_path"), "Conditional downstream rows nonmissing when the trigger condition is false."),
        summary_row("alb2002_health_questionnaire_conditional_missing_when_triggered_rows", int_sum(rows, "dependent_missing_when_triggered_rows", "conditional_skip_path"), "Conditional downstream rows missing when the trigger condition is true."),
        summary_row("alb2002_health_questionnaire_outcome_semantics_ready_observed", metric_value(outcome_summary, "alb2002_outcome_semantics_outcome_ready_rows"), "Outcome-ready rows observed in the upstream raw outcome-semantics audit."),
        summary_row("alb2002_health_questionnaire_core_recipe_ready_observed", metric_value(core_summary, "alb2002_household_core_recipe_ready_rows"), "Recipe-ready rows observed in the upstream household-core audit."),
        summary_row("alb2002_health_questionnaire_boundary_climate_ready_observed", metric_value(boundary_summary, "alb2002_gadm_boundary_lead_climate_linkage_ready_rows"), "Climate-linkage-ready rows observed in the GADM boundary lead audit."),
        summary_row("alb2002_health_questionnaire_recipe_ready_rows", 0, "Rows promoted to a harmonization recipe by this audit; intentionally zero."),
        summary_row("alb2002_health_questionnaire_outcome_ready_rows", 0, "Rows promoted to final outcome construction by this audit; intentionally zero."),
        summary_row("alb2002_health_questionnaire_sdg382_ready_rows", 0, "Rows promoted to SDG 3.8.2 construction by this audit; intentionally zero."),
        summary_row("alb2002_health_questionnaire_climate_linkage_ready_rows", 0, "Rows promoted to climate linkage by this audit; intentionally zero."),
        summary_row("alb2002_health_questionnaire_current_decision", DECISION, "Current fail-closed decision for ALB_2002 questionnaire-backed health semantics."),
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
    if len(rows) > limit:
        lines.append("| " + " | ".join(["..."] + [f"{len(rows) - limit} additional rows omitted"] + [""] * max(0, len(columns) - 2)) + " |")
    return "\n".join(lines)


def count_table(counter: Counter[str], label: str) -> str:
    lines = [f"| {label} | Count |", "|---|---:|"]
    for key, count in counter.most_common():
        lines.append(f"| {key or 'blank'} | {count} |")
    return "\n".join(lines)


def write_report(rows: list[dict[str, str]], summary: list[dict[str, str]]) -> None:
    summary_table = "\n".join(f"| {row['metric']} | {row['value']} | {row['interpretation']} |" for row in summary)
    status_counts = Counter(row["semantic_evidence_status"] for row in rows)
    concept_counts = Counter(row["concept"] for row in rows)
    oop_rows = [row for row in rows if row["concept"] in {"oop_health_expenditure_item", "gift_payment_scope"}]
    access_rows = [row for row in rows if row["audit_family"] == "health_b_questionnaire"]
    skip_rows = [row for row in rows if row["audit_family"].endswith("_skip_path")]
    report = f"""# ALB_2002 Health Questionnaire Semantics Audit

Status: fail-closed questionnaire and raw skip-path audit. This report reads the ALB_2002 health questionnaire workbook and SPSS health modules to document payment units, recall periods, payment-scope exclusions, gift rows, access-barrier value codes, and skip/missing evidence. It does not write `data/`, does not construct outcomes, and does not promote any row to harmonization, SDG 3.8.2, or climate linkage.

## Bottom Line

- The ALB_2002 health questionnaire is readable in the current Python environment.
- Health payment items are recorded in `NEW LEKS`, not old lek, and are split across past-four-week outpatient/self-medication contexts and past-12-month hospital/dentist contexts.
- Provider total-payment questions explicitly exclude gifts, medicines, laboratory work, and transport, while gift values are separate variables. OOP aggregation therefore needs a documented inclusion policy.
- Raw skip paths show no positive payment values when visit/stay/dentist triggers are negative, but a few skipped downstream fields are nonmissing zeros, so zero/missing semantics still require review.
- Health module B confirms cost, distance, supply/availability, refusal, medicine-discount, and health-financing/coping codes, but denominator rules remain blocked.
- Recipe-ready, outcome-ready, SDG 3.8.2-ready, and climate-linkage-ready rows from this audit: 0.
- Current decision: `{DECISION}`.

## Summary

| Metric | Value | Interpretation |
|---|---:|---|
{summary_table}

## Concept Counts

{count_table(concept_counts, 'Concept') if rows else 'No rows.'}

## Semantic Status Counts

{count_table(status_counts, 'Semantic status') if rows else 'No rows.'}

## OOP And Gift Questionnaire Rows

{markdown_rows(oop_rows, ['raw_variable', 'raw_label', 'question_text', 'recall_period', 'unit_or_value_note', 'skip_or_instruction_note', 'raw_nonmissing_rows', 'raw_positive_numeric_rows', 'semantic_evidence_status'], 45) if oop_rows else 'No OOP rows found.'}

## Access And Barrier Rows

{markdown_rows(access_rows, ['raw_variable', 'raw_label', 'question_text', 'value_code_evidence', 'skip_or_instruction_note', 'raw_nonmissing_rows', 'semantic_evidence_status'], 20) if access_rows else 'No access rows found.'}

## Skip-Path Rows

{markdown_rows(skip_rows, ['audit_family', 'question_context', 'trigger_variable', 'downstream_variables', 'trigger_positive_rows', 'trigger_negative_rows', 'downstream_any_nonmissing_when_not_triggered_rows', 'downstream_any_positive_when_not_triggered_rows', 'downstream_zero_or_missing_when_triggered_rows', 'semantic_evidence_status'], 20) if skip_rows else 'No skip-path rows found.'}

## Interpretation

- This audit moves ALB_2002 beyond raw value labels by tying candidate OOP/access variables to the questionnaire text.
- It does not resolve final OOP aggregation, gift/payment-scope policy, annualization, total-consumption denominator period, SDG discretionary-budget inputs, or person-to-household aggregation.
- The access-barrier evidence is promising, but denominator definitions must distinguish need, care seeking, delayed care, referral, refusal, medicine entitlement, and no-one-needed-care responses.
- Climate linkage remains independently blocked by the unresolved district-boundary/GPS evidence.

## Machine-Readable Outputs

- `temp/alb2002_health_questionnaire_semantics_audit.csv`
- `result/alb2002_health_questionnaire_semantics_summary.csv`
"""
    REPORT_PATH.write_text(report, encoding="utf-8")


def main() -> None:
    ensure_dirs()
    rows = build_rows()
    summary = build_summary(rows)
    write_csv(AUDIT_PATH, rows, AUDIT_COLUMNS)
    write_csv(SUMMARY_PATH, summary, SUMMARY_COLUMNS)
    write_report(rows, summary)
    append_log(TEMP_DIR / "audit_log.md", f"Built ALB_2002 health questionnaire semantics audit rows={len(rows)} decision={DECISION}.")
    print(f"ALB_2002 health questionnaire semantics rows={len(rows)} decision={DECISION}.")


if __name__ == "__main__":
    main()
