from __future__ import annotations

import csv
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from pypdf import PdfReader

from common import PROJECT_ROOT, REPORT_DIR, RESULT_DIR, TEMP_DIR, append_log, ensure_dirs, write_csv


QUEUE_PATH = TEMP_DIR / "priority_lsms_isa_refocused_acquisition_queue.csv"
VALUE_PROFILE_PATH = TEMP_DIR / "priority_lsms_isa_received_raw_value_profile.csv"
KEY_PROFILE_PATH = TEMP_DIR / "priority_lsms_isa_received_raw_key_design_geography_profile.csv"
RAW_INTAKE_LEDGER_PATH = TEMP_DIR / "priority_lsms_isa_raw_package_intake_ledger.csv"
ARCHIVE_PREFLIGHT_PATH = TEMP_DIR / "priority_lsms_isa_archive_member_preflight.csv"

DOC_INVENTORY_PATH = TEMP_DIR / "priority_lsms_isa_focused_raw_value_documentation_inventory.csv"
VARIABLE_DECISION_PATH = TEMP_DIR / "priority_lsms_isa_focused_raw_value_variable_decisions.csv"
REQUIREMENT_DECISION_PATH = RESULT_DIR / "priority_lsms_isa_requirement_acceptance_decisions.csv"
SUMMARY_PATH = RESULT_DIR / "priority_lsms_isa_focused_raw_value_decision_summary.csv"
REPORT_PATH = REPORT_DIR / "priority_lsms_isa_focused_raw_value_decision_packet.md"

RAW_ROOT = TEMP_DIR / "raw_downloads"

REQUIREMENTS = [
    "household_person_keys",
    "weights_and_design",
    "consumption_or_income",
    "oop_health_expenditure",
    "health_need_and_access",
    "survey_timing",
    "climate_geography",
    "missing_codes_units_recall_skip_patterns",
]

DOC_INVENTORY_COLUMNS = [
    "download_priority_order",
    "queue_role",
    "country",
    "wave",
    "idno",
    "documentation_file",
    "documentation_file_name",
    "file_size_bytes",
    "page_count",
    "extracted_character_count",
    "health_terms_found",
    "consumption_terms_found",
    "timing_terms_found",
    "geography_terms_found",
    "extraction_status",
]

VARIABLE_COLUMNS = [
    "download_priority_order",
    "queue_role",
    "country",
    "wave",
    "idno",
    "requirement",
    "source_profile",
    "actual_member_name",
    "variable_name",
    "variable_role",
    "raw_variable_label",
    "has_value_labels",
    "row_count",
    "nonmissing_count",
    "missing_count",
    "distinct_nonmissing_count",
    "duplicate_if_key_count",
    "numeric_min",
    "numeric_max",
    "top_values",
    "possible_missing_codes",
    "detected_recall_period",
    "detected_unit_or_scale",
    "possible_skip_pattern",
    "raw_profile_status",
    "documentation_match_status",
    "documentation_file_name",
    "documentation_code_match",
    "documentation_label_term_hits",
    "documentation_context",
    "mechanical_raw_check_decision",
    "final_verification_decision",
    "remaining_blocker",
    "next_action",
]

REQUIREMENT_COLUMNS = [
    "download_priority_order",
    "queue_role",
    "country",
    "wave",
    "idno",
    "requirement",
    "variable_decision_rows",
    "mechanical_pass_rows",
    "documentation_code_match_rows",
    "documentation_label_match_rows",
    "variables_with_value_labels",
    "variables_with_nonmissing_values",
    "possible_missing_code_variables",
    "possible_skip_pattern_variables",
    "detected_recall_periods",
    "detected_units_or_scales",
    "top_candidate_variables",
    "mechanical_raw_check_decision",
    "final_verification_decision",
    "remaining_blocker",
    "next_action",
]

SUMMARY_COLUMNS = ["metric", "value", "interpretation"]

STOPWORDS = {
    "code",
    "total",
    "other",
    "what",
    "which",
    "where",
    "when",
    "this",
    "that",
    "with",
    "from",
    "have",
    "household",
    "identification",
    "section",
    "question",
    "value",
    "amount",
}

DOC_TERM_BUCKETS = {
    "health_terms_found": ["health", "illness", "medical", "care", "clinic", "hospital"],
    "consumption_terms_found": ["consumption", "expenditure", "food", "non-food", "non food"],
    "timing_terms_found": ["interview", "date", "month", "fieldwork", "visit"],
    "geography_terms_found": ["latitude", "longitude", "gps", "cluster", "enumeration", "region", "district"],
}


def read_csv_dicts(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def clean(value: Any) -> str:
    return "" if value is None else str(value).strip()


def safe_int(value: Any, default: int = 0) -> int:
    try:
        text = clean(value)
        return int(float(text)) if text else default
    except (TypeError, ValueError):
        return default


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(PROJECT_ROOT)).replace("\\", "/")
    except ValueError:
        return str(path).replace("\\", "/")


def compact(value: Any, limit: int = 240) -> str:
    text = " ".join(clean(value).replace("|", "/").split())
    return text[: limit - 3] + "..." if len(text) > limit else text


def raw_folder_path(folder: str, idno: str) -> Path:
    folder_clean = clean(folder).replace("\\", "/").strip("/")
    if folder_clean:
        return PROJECT_ROOT / folder_clean
    return RAW_ROOT / idno


def by_id(rows: list[dict[str, str]], field: str = "idno") -> dict[str, list[dict[str, str]]]:
    out: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        idno = clean(row.get(field))
        if idno:
            out[idno].append(row)
    return out


def one_by_id(rows: list[dict[str, str]], field: str = "idno") -> dict[str, dict[str, str]]:
    out: dict[str, dict[str, str]] = {}
    for row in rows:
        idno = clean(row.get(field))
        if idno and idno not in out:
            out[idno] = row
    return out


def normalize_text(value: str) -> str:
    return re.sub(r"\s+", " ", value.lower())


def variable_terms(variable_name: str) -> list[str]:
    base = clean(variable_name).lower()
    terms = [base]
    if "_" in base:
        terms.append(base.replace("_", " "))
        terms.append(base.replace("_", ""))
    if base.startswith("s") and "q" in base:
        terms.append(base[1:])
    if base.startswith("hh_"):
        terms.append(base.replace("hh_", ""))
    return [term for term in dict.fromkeys(terms) if len(term) >= 3]


def label_terms(label: str) -> list[str]:
    words = re.findall(r"[a-zA-Z][a-zA-Z0-9_/-]{3,}", clean(label).lower())
    out = []
    for word in words:
        simple = word.strip("_/-")
        if simple and simple not in STOPWORDS and simple not in out:
            out.append(simple)
    return out[:8]


def find_context(text: str, term: str, limit: int = 220) -> str:
    if not term:
        return ""
    idx = text.lower().find(term.lower())
    if idx < 0:
        return ""
    return compact(text[max(0, idx - 80) : idx + limit], 280)


def extract_pdf_text(path: Path) -> tuple[int, str, str]:
    try:
        reader = PdfReader(str(path))
        text = "\n".join(page.extract_text() or "" for page in reader.pages)
        return len(reader.pages), text, "extracted"
    except Exception as exc:  # pragma: no cover - depends on local PDF parser state
        return 0, "", f"blocked_pdf_text_extraction_failed:{type(exc).__name__}:{exc}"


def documentation_rows_for_wave(wave: dict[str, str]) -> tuple[list[dict[str, str]], str, dict[str, str]]:
    idno = clean(wave.get("idno"))
    folder = raw_folder_path(wave.get("local_target_folder", ""), idno)
    rows: list[dict[str, str]] = []
    text_by_file: dict[str, str] = {}
    if not folder.exists():
        return rows, "", text_by_file
    for path in sorted(folder.glob("*.pdf")):
        pages, text, status = extract_pdf_text(path)
        norm = normalize_text(text)
        text_by_file[path.name] = text
        row = {
            "download_priority_order": clean(wave.get("download_priority_order")),
            "queue_role": clean(wave.get("queue_role")),
            "country": clean(wave.get("country")),
            "wave": clean(wave.get("wave")),
            "idno": idno,
            "documentation_file": rel(path),
            "documentation_file_name": path.name,
            "file_size_bytes": str(path.stat().st_size),
            "page_count": str(pages),
            "extracted_character_count": str(len(text)),
            "extraction_status": status,
        }
        for column, terms in DOC_TERM_BUCKETS.items():
            row[column] = "; ".join(term for term in terms if term in norm)
        rows.append(row)
    combined = "\n".join(text_by_file.values())
    return rows, combined, text_by_file


def documentation_match(
    variable_name: str,
    raw_label: str,
    text_by_file: dict[str, str],
) -> tuple[str, str, str, str, str]:
    code_terms = variable_terms(variable_name)
    label_words = label_terms(raw_label)
    best_label_hits: list[str] = []
    for file_name, text in text_by_file.items():
        norm = normalize_text(text)
        for term in code_terms:
            if term and term in norm:
                return (
                    "documented_by_variable_code",
                    file_name,
                    term,
                    "",
                    find_context(text, term),
                )
        hits = [term for term in label_words if term in norm]
        if len(hits) > len(best_label_hits):
            best_label_hits = hits
            if len(hits) >= 2:
                context_term = hits[0]
                return (
                    "label_terms_found_needs_manual_confirmation",
                    file_name,
                    "",
                    "; ".join(hits[:8]),
                    find_context(text, context_term),
                )
    if best_label_hits:
        return (
            "weak_label_term_found_needs_manual_confirmation",
            "",
            "",
            "; ".join(best_label_hits[:8]),
            "",
        )
    return ("not_found_in_local_pdf_text", "", "", "", "")


def requirement_for_key_role(role: str) -> str:
    if role == "household_key_component":
        return "household_person_keys"
    if role in {"household_weight", "person_weight", "survey_weight", "strata", "psu"}:
        return "weights_and_design"
    if role in {"cluster_or_enumeration_area", "admin_geography_region", "latitude", "longitude"}:
        return "climate_geography"
    return ""


def mechanical_decision(row: dict[str, str], requirement: str, source_profile: str) -> tuple[str, str]:
    nonmissing = safe_int(row.get("nonmissing_count"))
    if nonmissing <= 0:
        return "blocked_no_nonmissing_raw_values", "Review whether this variable is a generated empty shell, skip-only field, or wrong candidate."
    if source_profile == "key_design_geography":
        role = clean(row.get("variable_role"))
        if role == "household_key_component" and safe_int(row.get("duplicate_if_key_count"), 1) == 0:
            return "mechanical_unique_key_pass_needs_documentation", "Confirm key role and joins across required modules."
        if role in {"cluster_or_enumeration_area", "admin_geography_region", "latitude", "longitude"}:
            return "mechanical_geography_profile_pass_needs_linkage_policy", "Confirm geography quality, displacement/admin route, and climate linkage level."
        return "mechanical_design_or_utility_profile_available", "Confirm role in official questionnaire/codebook and analysis level."
    if requirement in {"consumption_or_income", "oop_health_expenditure"}:
        if clean(row.get("detected_unit_or_scale")) or safe_int(row.get("positive_count")) > 0:
            return "mechanical_amount_profile_available_needs_unit_recall_documentation", "Confirm unit, currency, recall period, aggregation scope, and missing codes."
    if requirement == "health_need_and_access":
        return "mechanical_access_profile_available_needs_skip_denominator_documentation", "Confirm denominator, skip pattern, barrier coding, and person/household aggregation."
    if requirement == "survey_timing":
        return "mechanical_timing_profile_available_needs_date_window_confirmation", "Confirm interview date/month/year or fieldwork window."
    if requirement == "climate_geography":
        return "mechanical_geography_profile_available_needs_linkage_policy", "Confirm geography quality and CHIRPS/ERA5 linkage route."
    return "mechanical_raw_profile_available_needs_documentation", "Confirm raw labels, valid ranges, missing codes, units, recall periods, and skip patterns."


def variable_decision_rows(
    wave: dict[str, str],
    value_rows: list[dict[str, str]],
    key_rows: list[dict[str, str]],
    text_by_file: dict[str, str],
) -> list[dict[str, str]]:
    out: list[dict[str, str]] = []
    for row in value_rows:
        requirement = clean(row.get("requirement"))
        status, doc_file, code_match, label_hits, context = documentation_match(
            clean(row.get("variable_name")),
            clean(row.get("raw_variable_label")),
            text_by_file,
        )
        mechanical, next_action = mechanical_decision(row, requirement, "value_profile")
        out.append(
            {
                "download_priority_order": clean(row.get("download_priority_order")) or clean(wave.get("download_priority_order")),
                "queue_role": clean(row.get("queue_role")) or clean(wave.get("queue_role")),
                "country": clean(row.get("country")) or clean(wave.get("country")),
                "wave": clean(row.get("wave")) or clean(wave.get("wave")),
                "idno": clean(row.get("idno")),
                "requirement": requirement,
                "source_profile": "value_profile",
                "actual_member_name": clean(row.get("actual_member_name")),
                "variable_name": clean(row.get("variable_name")),
                "variable_role": "",
                "raw_variable_label": clean(row.get("raw_variable_label")),
                "has_value_labels": clean(row.get("has_value_labels")),
                "row_count": clean(row.get("row_count")),
                "nonmissing_count": clean(row.get("nonmissing_count")),
                "missing_count": clean(row.get("missing_count")),
                "distinct_nonmissing_count": clean(row.get("distinct_nonmissing_count")),
                "duplicate_if_key_count": "",
                "numeric_min": clean(row.get("numeric_min")),
                "numeric_max": clean(row.get("numeric_max")),
                "top_values": clean(row.get("top_values")),
                "possible_missing_codes": clean(row.get("possible_missing_codes")),
                "detected_recall_period": clean(row.get("detected_recall_period")),
                "detected_unit_or_scale": clean(row.get("detected_unit_or_scale")),
                "possible_skip_pattern": clean(row.get("possible_skip_pattern")),
                "raw_profile_status": clean(row.get("value_profile_status")),
                "documentation_match_status": status,
                "documentation_file_name": doc_file,
                "documentation_code_match": code_match,
                "documentation_label_term_hits": label_hits,
                "documentation_context": context,
                "mechanical_raw_check_decision": mechanical,
                "final_verification_decision": "blocked_manual_acceptance_required",
                "remaining_blocker": "official documentation and reviewer acceptance still required before raw_value_verified",
                "next_action": next_action,
            }
        )
    for row in key_rows:
        requirement = requirement_for_key_role(clean(row.get("variable_role")))
        if not requirement:
            continue
        status, doc_file, code_match, label_hits, context = documentation_match(
            clean(row.get("variable_name")),
            clean(row.get("raw_variable_label")),
            text_by_file,
        )
        mechanical, next_action = mechanical_decision(row, requirement, "key_design_geography")
        out.append(
            {
                "download_priority_order": clean(row.get("download_priority_order")) or clean(wave.get("download_priority_order")),
                "queue_role": clean(row.get("queue_role")) or clean(wave.get("queue_role")),
                "country": clean(row.get("country")) or clean(wave.get("country")),
                "wave": clean(row.get("wave")) or clean(wave.get("wave")),
                "idno": clean(row.get("idno")),
                "requirement": requirement,
                "source_profile": "key_design_geography",
                "actual_member_name": clean(row.get("actual_member_name")),
                "variable_name": clean(row.get("variable_name")),
                "variable_role": clean(row.get("variable_role")),
                "raw_variable_label": clean(row.get("raw_variable_label")),
                "has_value_labels": clean(row.get("has_value_labels")),
                "row_count": clean(row.get("row_count")),
                "nonmissing_count": clean(row.get("nonmissing_count")),
                "missing_count": clean(row.get("missing_count")),
                "distinct_nonmissing_count": clean(row.get("distinct_nonmissing_count")),
                "duplicate_if_key_count": clean(row.get("duplicate_if_key_count")),
                "numeric_min": clean(row.get("numeric_min")),
                "numeric_max": clean(row.get("numeric_max")),
                "top_values": clean(row.get("top_values")),
                "possible_missing_codes": "",
                "detected_recall_period": "",
                "detected_unit_or_scale": "",
                "possible_skip_pattern": "",
                "raw_profile_status": clean(row.get("profile_status")),
                "documentation_match_status": status,
                "documentation_file_name": doc_file,
                "documentation_code_match": code_match,
                "documentation_label_term_hits": label_hits,
                "documentation_context": context,
                "mechanical_raw_check_decision": mechanical,
                "final_verification_decision": "blocked_manual_acceptance_required",
                "remaining_blocker": "official documentation and reviewer acceptance still required before raw_value_verified",
                "next_action": next_action,
            }
        )
    return out


def compact_unique(values: list[str], limit: int = 10) -> str:
    out: list[str] = []
    for value in values:
        item = clean(value)
        if item and item not in out:
            out.append(item)
        if len(out) >= limit:
            break
    return "; ".join(out)


def requirement_decisions(
    waves: list[dict[str, str]],
    variable_rows: list[dict[str, str]],
) -> list[dict[str, str]]:
    by_wave_req: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in variable_rows:
        by_wave_req[(clean(row.get("idno")), clean(row.get("requirement")))].append(row)
    wave_by_id = {clean(row.get("idno")): row for row in waves if clean(row.get("idno"))}
    rows: list[dict[str, str]] = []
    for idno in sorted(wave_by_id, key=lambda item: safe_int(wave_by_id[item].get("download_priority_order"), 999999)):
        wave = wave_by_id[idno]
        for requirement in REQUIREMENTS:
            req_rows = by_wave_req.get((idno, requirement), [])
            if not req_rows:
                continue
            mechanical_pass = [
                row
                for row in req_rows
                if clean(row.get("mechanical_raw_check_decision")).startswith("mechanical_")
                and clean(row.get("mechanical_raw_check_decision")) != "blocked_no_nonmissing_raw_values"
            ]
            code_hits = [row for row in req_rows if clean(row.get("documentation_code_match"))]
            label_hits = [row for row in req_rows if clean(row.get("documentation_label_term_hits"))]
            value_labels = [row for row in req_rows if clean(row.get("has_value_labels")) == "1"]
            nonmissing = [row for row in req_rows if safe_int(row.get("nonmissing_count")) > 0]
            missing_vars = [row.get("variable_name", "") for row in req_rows if clean(row.get("possible_missing_codes"))]
            skip_vars = [row.get("variable_name", "") for row in req_rows if clean(row.get("possible_skip_pattern"))]
            recall = compact_unique([row.get("detected_recall_period", "") for row in req_rows])
            units = compact_unique([row.get("detected_unit_or_scale", "") for row in req_rows])
            top_vars = compact_unique([row.get("variable_name", "") for row in req_rows], limit=12)
            if not mechanical_pass:
                mechanical = "blocked_no_mechanical_raw_pass"
            elif code_hits or label_hits:
                mechanical = "mechanical_raw_profile_plus_documentation_hits_needs_reviewer_acceptance"
            else:
                mechanical = "mechanical_raw_profile_available_documentation_crosscheck_missing"
            rows.append(
                {
                    "download_priority_order": clean(wave.get("download_priority_order")),
                    "queue_role": clean(wave.get("queue_role")),
                    "country": clean(wave.get("country")),
                    "wave": clean(wave.get("wave")),
                    "idno": idno,
                    "requirement": requirement,
                    "variable_decision_rows": str(len(req_rows)),
                    "mechanical_pass_rows": str(len(mechanical_pass)),
                    "documentation_code_match_rows": str(len(code_hits)),
                    "documentation_label_match_rows": str(len(label_hits)),
                    "variables_with_value_labels": str(len(value_labels)),
                    "variables_with_nonmissing_values": str(len(nonmissing)),
                    "possible_missing_code_variables": compact_unique(missing_vars),
                    "possible_skip_pattern_variables": compact_unique(skip_vars),
                    "detected_recall_periods": recall,
                    "detected_units_or_scales": units,
                    "top_candidate_variables": top_vars,
                    "mechanical_raw_check_decision": mechanical,
                    "final_verification_decision": "blocked_manual_acceptance_required",
                    "remaining_blocker": "reviewer must confirm raw file, variable, value labels, units, recall periods, missing codes, skip patterns, merge level, and outcome/climate role",
                    "next_action": "Use the focused variable-decision rows and original PDF documentation to make a reviewer acceptance decision; rerun promotion packets after acceptance.",
                }
            )
    return rows


def build_summary(
    doc_rows: list[dict[str, str]],
    variable_rows: list[dict[str, str]],
    requirement_rows: list[dict[str, str]],
) -> list[dict[str, str]]:
    doc_counts = Counter(row.get("extraction_status", "") for row in doc_rows)
    doc_match_counts = Counter(row.get("documentation_match_status", "") for row in variable_rows)
    mechanical_counts = Counter(row.get("mechanical_raw_check_decision", "") for row in requirement_rows)
    rows = [
        {"metric": "priority_lsms_focused_raw_value_decision_dataset_rows", "value": str(len({row["idno"] for row in requirement_rows})), "interpretation": "Received raw datasets with focused decision rows."},
        {"metric": "priority_lsms_focused_raw_value_documentation_file_rows", "value": str(len(doc_rows)), "interpretation": "Local PDF documentation files parsed for received raw datasets."},
        {"metric": "priority_lsms_focused_raw_value_documentation_extracted_rows", "value": str(sum(1 for row in doc_rows if row["extraction_status"] == "extracted")), "interpretation": "PDF documentation files with extracted text."},
        {"metric": "priority_lsms_focused_raw_value_variable_decision_rows", "value": str(len(variable_rows)), "interpretation": "Variable-level focused raw value decision rows."},
        {"metric": "priority_lsms_focused_raw_value_requirement_decision_rows", "value": str(len(requirement_rows)), "interpretation": "Requirement-level focused raw value decision rows."},
        {"metric": "priority_lsms_focused_raw_value_requirement_raw_value_verified_rows", "value": "0", "interpretation": "No requirement is value-verified by this fail-closed documentation crosswalk."},
        {"metric": "priority_lsms_focused_raw_value_data_write_status", "value": "blocked_decision_packet_only", "interpretation": "Focused raw value decisions do not write promoted data."},
        {"metric": "modeling_gate_status", "value": "blocked", "interpretation": "Models remain blocked until promoted registry thresholds and climate linkage pass."},
    ]
    for status, count in sorted(doc_counts.items()):
        rows.append({"metric": f"priority_lsms_focused_raw_value_documentation_status_{status}", "value": str(count), "interpretation": "PDF extraction status count."})
    for status, count in sorted(doc_match_counts.items()):
        rows.append({"metric": f"priority_lsms_focused_raw_value_documentation_match_{status}", "value": str(count), "interpretation": "Variable documentation match status count."})
    for status, count in sorted(mechanical_counts.items()):
        rows.append({"metric": f"priority_lsms_focused_raw_value_requirement_mechanical_{status}", "value": str(count), "interpretation": "Requirement mechanical decision status count."})
    return rows


def markdown_table(rows: list[dict[str, str]], columns: list[str], limit: int = 30) -> str:
    lines = ["| " + " | ".join(columns) + " |", "|" + "|".join("---" for _ in columns) + "|"]
    for row in rows[:limit]:
        values = []
        for column in columns:
            value = clean(row.get(column)).replace("|", "/")
            if len(value) > 120:
                value = value[:117] + "..."
            values.append(value)
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines)


def write_report(
    doc_rows: list[dict[str, str]],
    variable_rows: list[dict[str, str]],
    requirement_rows: list[dict[str, str]],
    summary_rows: list[dict[str, str]],
) -> None:
    summary_table = "\n".join(f"| {row['metric']} | {row['value']} | {row['interpretation']} |" for row in summary_rows)
    doc_preview = markdown_table(
        doc_rows,
        ["idno", "documentation_file_name", "page_count", "extracted_character_count", "extraction_status"],
        12,
    )
    req_preview = markdown_table(
        requirement_rows,
        [
            "idno",
            "requirement",
            "mechanical_pass_rows",
            "documentation_code_match_rows",
            "documentation_label_match_rows",
            "mechanical_raw_check_decision",
            "final_verification_decision",
        ],
        20,
    )
    variable_preview = markdown_table(
        sorted(
            variable_rows,
            key=lambda row: (
                row.get("documentation_match_status") != "documented_by_variable_code",
                row.get("documentation_match_status") != "label_terms_found_needs_manual_confirmation",
                safe_int(row.get("download_priority_order"), 999999),
                row.get("requirement", ""),
            ),
        ),
        ["idno", "requirement", "variable_name", "raw_variable_label", "documentation_match_status", "documentation_file_name"],
        20,
    )
    REPORT_PATH.write_text(
        f"""# Priority LSMS-ISA Focused Raw Value Decision Packet

Status: fail-closed documentation crosswalk for received raw LSMS/ISA packages.
This packet does not mark any country-wave as value-verified and does not write
to `data/`. It narrows the next reviewer task by pairing raw value profiles with
local package PDF documentation.

## Summary

| Metric | Value | Interpretation |
|---|---:|---|
{summary_table}

## Documentation Parsed

{doc_preview}

## Requirement Decisions

{req_preview}

## Variable Documentation Hits

{variable_preview}

## Promotion Rule

Rows in `result/priority_lsms_isa_requirement_acceptance_decisions.csv` remain
`blocked_manual_acceptance_required`. A future reviewer or script may only turn
an item into `raw_value_verified` after checking raw files, value labels, units,
recall periods, missing codes, skip patterns, merge level, and the outcome or
climate-linkage role against official documentation.
""",
        encoding="utf-8",
    )


def build_outputs() -> tuple[list[dict[str, str]], list[dict[str, str]], list[dict[str, str]], list[dict[str, str]]]:
    queue_rows = read_csv_dicts(QUEUE_PATH)
    value_by_id = by_id(read_csv_dicts(VALUE_PROFILE_PATH))
    key_by_id = by_id(read_csv_dicts(KEY_PROFILE_PATH))
    intake_by_id = one_by_id(read_csv_dicts(RAW_INTAKE_LEDGER_PATH))
    archive_by_id = one_by_id(read_csv_dicts(ARCHIVE_PREFLIGHT_PATH))
    doc_rows: list[dict[str, str]] = []
    variable_rows: list[dict[str, str]] = []
    eligible_waves = [
        row
        for row in queue_rows
        if value_by_id.get(clean(row.get("idno"))) or key_by_id.get(clean(row.get("idno")))
    ]
    for wave in eligible_waves:
        idno = clean(wave.get("idno"))
        intake = intake_by_id.get(idno, {})
        archive = archive_by_id.get(idno, {})
        if safe_int(intake.get("original_file_count")) <= 0:
            continue
        if clean(archive.get("archive_preflight_status")) != "ready_for_raw_receipt_schema_and_manual_review":
            continue
        wave_doc_rows, _combined_text, text_by_file = documentation_rows_for_wave(wave)
        doc_rows.extend(wave_doc_rows)
        variable_rows.extend(variable_decision_rows(wave, value_by_id.get(idno, []), key_by_id.get(idno, []), text_by_file))
    requirement_rows = requirement_decisions(eligible_waves, variable_rows)
    summary_rows = build_summary(doc_rows, variable_rows, requirement_rows)
    return doc_rows, variable_rows, requirement_rows, summary_rows


def main() -> None:
    ensure_dirs()
    doc_rows, variable_rows, requirement_rows, summary_rows = build_outputs()
    write_csv(DOC_INVENTORY_PATH, doc_rows, DOC_INVENTORY_COLUMNS)
    write_csv(VARIABLE_DECISION_PATH, variable_rows, VARIABLE_COLUMNS)
    write_csv(REQUIREMENT_DECISION_PATH, requirement_rows, REQUIREMENT_COLUMNS)
    write_csv(SUMMARY_PATH, summary_rows, SUMMARY_COLUMNS)
    write_report(doc_rows, variable_rows, requirement_rows, summary_rows)
    append_log(
        TEMP_DIR / "audit_log.md",
        "Built priority LSMS/ISA focused raw value decision packet; no requirement value-verified and data/modeling gates remain blocked.",
    )
    print(
        "Priority LSMS/ISA focused raw value decisions "
        f"datasets={len({row['idno'] for row in requirement_rows})} "
        f"variables={len(variable_rows)} requirements={len(requirement_rows)}."
    )


if __name__ == "__main__":
    main()
