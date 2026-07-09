from __future__ import annotations

import csv
import importlib.util
import math
from collections import Counter
from pathlib import Path
from typing import Any

import pandas as pd

from common import REPORT_DIR, RESULT_DIR, TEMP_DIR, append_log, ensure_dirs, write_csv

try:
    import pyreadstat
except ImportError:  # pragma: no cover - validated by the environment audit.
    pyreadstat = None


IDNO = "ALB_2005_LSMS_v01_M"
COUNTRY = "Albania"
SURVEY_NAME = "Living Standards Measurement Survey 2005"
WAVE = "2005"
RAW_FILE_INVENTORY_PATH = TEMP_DIR / "raw_schema_inventory" / "raw_file_inventory.csv"
RAW_VARIABLE_CATALOG_PATH = TEMP_DIR / "raw_schema_inventory" / "raw_variable_catalog.csv"
EVIDENCE_PATH = TEMP_DIR / "alb2005_documented_variable_evidence.csv"
SUMMARY_PATH = RESULT_DIR / "alb2005_documented_harmonization_summary.csv"
REPORT_PATH = REPORT_DIR / "alb2005_documented_harmonization_review.md"

EVIDENCE_COLUMNS = [
    "country",
    "survey_name",
    "wave",
    "idno",
    "evidence_domain",
    "harmonized_variable",
    "source_file",
    "source_path",
    "raw_variable",
    "raw_label",
    "value_label_examples",
    "row_count",
    "nonmissing_count",
    "missing_count",
    "distinct_count",
    "min_value",
    "max_value",
    "top_values",
    "documentation_support_status",
    "recipe_decision",
    "blocking_reason",
    "next_action",
]
SUMMARY_COLUMNS = ["metric", "value", "interpretation"]

OOP_VARIABLES = [
    "m9a_q20",
    "m9a_q22",
    "m9a_q32",
    "m9a_q34",
    "m9a_q41",
    "m9a_q42",
    "m9a_q49",
    "m9a_q50",
    "m9a_q57",
    "m9a_q58",
    "m9a_q61",
    "m9a_q68",
    "m9a_q71",
    "m9a_q72",
    "m9a_q79",
    "m9a_q80",
]

SPECS = [
    {
        "domain": "identity",
        "harmonized": "hhid",
        "file": "Modul_11_check_form_food_cl.sav",
        "variables": ["psu", "hh", "hhid"],
        "status": "documentation_supported_key_review_required",
        "decision": "candidate_for_future_recipe_after_manual_key_review",
        "blocking": "household ID variables exist, but cross-file cardinality and merge level still need manual verification",
        "next": "verify household uniqueness and joins across poverty, health, filters, and roster files",
    },
    {
        "domain": "identity",
        "harmonized": "hhid",
        "file": "filters_cl.sav",
        "variables": ["M0_Q00", "M0_Q01", "HHID"],
        "status": "documentation_supported_key_review_required",
        "decision": "candidate_for_future_recipe_after_manual_key_review",
        "blocking": "filter file keys exist, but relationship to analysis modules still needs manual verification",
        "next": "confirm PSU/household ID consistency with core modules",
    },
    {
        "domain": "survey_design",
        "harmonized": "household_weight",
        "file": "poverty.sav",
        "variables": ["weight_retro"],
        "status": "documentation_supported_design_review_required",
        "decision": "candidate_for_future_recipe_after_survey_design_review",
        "blocking": "weight variable exists, but final design use and merge target require documentation review",
        "next": "confirm official household weight use, population, and merge keys",
    },
    {
        "domain": "survey_design",
        "harmonized": "household_weight",
        "file": "Weight_retro_2005.sav",
        "variables": ["weight_retro"],
        "status": "documentation_supported_design_review_required",
        "decision": "candidate_for_future_recipe_after_survey_design_review",
        "blocking": "separate retro weight file exists, but merge coverage and intended use require review",
        "next": "verify whether this file supplements poverty.sav weights and how it joins to households",
    },
    {
        "domain": "consumption",
        "harmonized": "total_consumption",
        "file": "poverty.sav",
        "variables": ["totcons"],
        "status": "documentation_supported_unit_period_review_required",
        "decision": "candidate_for_future_recipe_after_unit_period_review",
        "blocking": "survey aggregate exists, but unit, price basis, period, and household-level interpretation need review",
        "next": "verify local-currency unit, old/new lek scaling, period, and whether aggregate is household total",
    },
    {
        "domain": "consumption",
        "harmonized": "food_consumption",
        "file": "poverty.sav",
        "variables": ["rfood"],
        "status": "documentation_supported_not_direct_household_total",
        "decision": "not_recipe_ready_per_capita_or_component_review_required",
        "blocking": "label indicates a per-capita food measure rather than a direct household total",
        "next": "decide whether to use only for denominator diagnostics or reconstruct household total with documentation",
    },
    {
        "domain": "consumption",
        "harmonized": "nonfood_consumption",
        "file": "poverty.sav",
        "variables": ["rnfood"],
        "status": "documentation_supported_not_direct_household_total",
        "decision": "not_recipe_ready_per_capita_or_component_review_required",
        "blocking": "label indicates a per-capita non-food measure rather than a direct household total",
        "next": "avoid treating this as household non-food total until documentation confirms unit and denominator",
    },
    {
        "domain": "oop_health_expenditure",
        "harmonized": "oop_health_expenditure",
        "file": "Modul_9A_healtha_cl.sav",
        "variables": OOP_VARIABLES,
        "status": "documentation_supported_aggregation_recall_review_required",
        "decision": "candidate_for_future_recipe_after_aggregation_recall_skip_review",
        "blocking": "multiple payment variables exist, but aggregation, recall period, skip patterns, and missing-code rules are unresolved",
        "next": "map each payment item to care context and construct a documented aggregation rule before outcomes",
    },
    {
        "domain": "health_need",
        "harmonized": "illness_or_injury_need",
        "file": "Modul_9A_healtha_cl.sav",
        "variables": ["m9a_q01", "m9a_q03", "m9a_q04", "m9a_q07"],
        "status": "documentation_supported_need_definition_review_required",
        "decision": "candidate_for_future_recipe_after_skip_pattern_denominator_review",
        "blocking": "health need variables exist but mix chronic/disability, diagnosis, disease category, and sudden illness concepts",
        "next": "choose illness/need denominator and verify skip patterns against questionnaire/codebook",
    },
    {
        "domain": "care_access",
        "harmonized": "care_not_sought",
        "file": "Modul_9B_healthb_cl.sav",
        "variables": ["m9b_q05", "m9b_q06"],
        "status": "documentation_supported_referral_nonuse_review_required",
        "decision": "candidate_for_future_recipe_after_skip_pattern_denominator_review",
        "blocking": "variables cover referral-to-hospital nonuse, not necessarily all forgone care after need",
        "next": "confirm denominator and whether hospital referral nonuse is an acceptable access outcome",
    },
    {
        "domain": "care_access",
        "harmonized": "reason_not_sought_cost",
        "file": "Modul_9B_healthb_cl.sav",
        "variables": ["m9b_q06"],
        "status": "documentation_supported_value_label_review_required",
        "decision": "candidate_for_future_recipe_after_value_label_and_denominator_review",
        "blocking": "cost category appears in value labels, but denominator and skip path are unresolved",
        "next": "confirm code for unable to afford treatment and denominator among referred-but-not-gone observations",
    },
    {
        "domain": "care_access",
        "harmonized": "reason_not_sought_distance",
        "file": "Modul_9B_healthb_cl.sav",
        "variables": ["m9b_q06"],
        "status": "documentation_supported_value_label_review_required",
        "decision": "candidate_for_future_recipe_after_value_label_and_denominator_review",
        "blocking": "distance/availability categories appear in value labels, but denominator and skip path are unresolved",
        "next": "confirm distance/transport code mapping and whether service availability should be separated",
    },
    {
        "domain": "geography",
        "harmonized": "admin1_or_admin2",
        "file": "filters.sav",
        "variables": ["P11_Q5B"],
        "status": "documentation_supported_weak_geography_coverage_review_required",
        "decision": "not_recipe_ready_missing_geography_coverage_review",
        "blocking": "district code exists in filters.sav but coverage and merge path to all households require review; no GPS is present",
        "next": "verify nonmissing coverage, district label semantics, and joins to household/person modules",
    },
    {
        "domain": "shock_module",
        "harmonized": "shock_module_variable",
        "file": "Modul_6E_migratione_cl.sav",
        "variables": ["m6e_q00", "m6e_q0a", "m6e_q01"],
        "status": "documentation_supported_shock_module_review_required",
        "decision": "candidate_for_future_mechanism_or_covariate_review",
        "blocking": "shock module variables exist, but they are not climate exposure variables and need household-level aggregation/interpretation",
        "next": "document serious illness/flood shock coding and decide whether to use as mechanism or covariate only",
    },
    {
        "domain": "false_positive",
        "harmonized": "household_weight_or_person_weight",
        "file": "Modul_10_fertility_cl.sav",
        "variables": ["m10_q13a", "m10_q13b"],
        "status": "blocked_false_positive",
        "decision": "blocked_false_positive",
        "blocking": "birth-weight variables are child health/fertility measures and are not survey design weights",
        "next": "exclude these variables from survey-weight candidates",
    },
]

NO_VARIABLE_ROWS = [
    {
        "domain": "survey_timing",
        "harmonized": "survey_month_or_interview_date",
        "status": "blocked_missing_timing",
        "decision": "not_recipe_ready_missing_timing",
        "blocking": "no raw interview month/date variable has been verified for ALB_2005",
        "next": "inspect questionnaire and fieldwork documentation for month/date or defensible fieldwork window",
    },
    {
        "domain": "geography",
        "harmonized": "latitude_longitude",
        "status": "blocked_no_gps_coordinates",
        "decision": "not_recipe_ready_no_gps",
        "blocking": "no household or cluster latitude/longitude variable has been found in inspected ALB_2005 raw files",
        "next": "use documented admin geography only if coverage and climate aggregation polygons can be verified",
    },
]


def read_csv_dicts(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def project_path(path_text: str) -> Path:
    path = Path(path_text)
    return path if path.is_absolute() else TEMP_DIR.parent / path


def format_scalar(value: Any) -> str:
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


def compact_join(values: list[Any], limit: int = 20) -> str:
    out: list[str] = []
    seen: set[str] = set()
    for value in values:
        clean = str(value).strip()
        if not clean or clean in seen:
            continue
        out.append(clean)
        seen.add(clean)
        if len(out) >= limit:
            break
    return ";".join(out)


def find_file(raw_files: list[dict[str, str]], file_name: str) -> dict[str, str] | None:
    file_name_low = file_name.lower()
    matches = [
        row
        for row in raw_files
        if Path(row.get("source_path", "")).name.lower() == file_name_low
        and "lsms2005en" in row.get("source_path", "").lower()
    ]
    if not matches:
        return None
    matches.sort(key=lambda row: (0 if "data_2005" in row.get("source_path", "").lower() else 1, row.get("source_path", "")))
    return matches[0]


def find_variable(raw_variables: list[dict[str, str]], source_path: str, variable: str) -> dict[str, str] | None:
    variable_low = variable.lower()
    matches = [
        row
        for row in raw_variables
        if row.get("source_path", "") == source_path and row.get("variable_name", "").lower() == variable_low
    ]
    return matches[0] if matches else None


def summarize_series(series: pd.Series) -> dict[str, str]:
    nonmissing = series.dropna()
    row_count = len(series)
    numeric = pd.to_numeric(nonmissing, errors="coerce")
    numeric_nonmissing = numeric.dropna()
    is_numeric = pd.api.types.is_numeric_dtype(series) or (len(nonmissing) > 0 and len(numeric_nonmissing) / len(nonmissing) >= 0.9)
    top_values = [
        f"{format_scalar(value)}:{int(count)}"
        for value, count in nonmissing.astype(str).value_counts(dropna=True).head(8).items()
    ]
    out = {
        "row_count": str(row_count),
        "nonmissing_count": str(len(nonmissing)),
        "missing_count": str(row_count - len(nonmissing)),
        "distinct_count": str(nonmissing.nunique(dropna=True)),
        "min_value": "",
        "max_value": "",
        "top_values": compact_join(top_values, 8),
    }
    if is_numeric and len(numeric_nonmissing) > 0:
        out["min_value"] = format_scalar(numeric_nonmissing.min())
        out["max_value"] = format_scalar(numeric_nonmissing.max())
    return out


def value_label_examples(meta: Any, variable: str) -> str:
    if meta is None:
        return ""
    labels = {}
    variable_value_labels = getattr(meta, "variable_value_labels", {}) or {}
    if variable in variable_value_labels:
        labels = variable_value_labels.get(variable, {}) or {}
    if not labels:
        variable_to_label = getattr(meta, "variable_to_label", {}) or {}
        value_labels = getattr(meta, "value_labels", {}) or {}
        label_name = variable_to_label.get(variable)
        labels = value_labels.get(label_name, {}) if label_name else {}
    return compact_join([f"{format_scalar(code)}={label}" for code, label in list(labels.items())[:12]], 12)


def read_variable_summary(path_text: str, variable: str) -> tuple[dict[str, str], str]:
    path = project_path(path_text)
    if pyreadstat is None:
        return {}, "pyreadstat_not_available"
    if path.suffix.lower() != ".sav":
        return {}, f"unsupported_file_format_{path.suffix.lower() or 'blank'}"
    try:
        df, meta = pyreadstat.read_sav(str(path), usecols=[variable], apply_value_formats=False)
    except Exception as exc:  # pragma: no cover - data-reader errors depend on local files.
        return {}, f"{type(exc).__name__}: {str(exc)[:180]}"
    out = summarize_series(df[variable])
    out["value_label_examples"] = value_label_examples(meta, variable)
    return out, ""


def base_row(domain: str, harmonized: str) -> dict[str, str]:
    return {
        "country": COUNTRY,
        "survey_name": SURVEY_NAME,
        "wave": WAVE,
        "idno": IDNO,
        "evidence_domain": domain,
        "harmonized_variable": harmonized,
        "source_file": "",
        "source_path": "",
        "raw_variable": "",
        "raw_label": "",
        "value_label_examples": "",
        "row_count": "",
        "nonmissing_count": "",
        "missing_count": "",
        "distinct_count": "",
        "min_value": "",
        "max_value": "",
        "top_values": "",
        "documentation_support_status": "",
        "recipe_decision": "",
        "blocking_reason": "",
        "next_action": "",
    }


def build_evidence_rows(raw_files: list[dict[str, str]], raw_variables: list[dict[str, str]]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for spec in SPECS:
        file_row = find_file(raw_files, spec["file"])
        for variable in spec["variables"]:
            row = base_row(spec["domain"], spec["harmonized"])
            row.update(
                {
                    "source_file": spec["file"],
                    "raw_variable": variable,
                    "documentation_support_status": spec["status"],
                    "recipe_decision": spec["decision"],
                    "blocking_reason": spec["blocking"],
                    "next_action": spec["next"],
                }
            )
            if file_row is None:
                row["documentation_support_status"] = "blocked_expected_source_file_not_found"
                row["blocking_reason"] = f"expected source file {spec['file']} was not found in raw_file_inventory"
                rows.append(row)
                continue
            source_path = file_row.get("source_path", "")
            row["source_path"] = source_path
            variable_row = find_variable(raw_variables, source_path, variable)
            if variable_row is None:
                row["documentation_support_status"] = "blocked_expected_raw_variable_not_found"
                row["blocking_reason"] = f"expected raw variable {variable} was not found in {spec['file']}"
                rows.append(row)
                continue
            actual_variable = variable_row.get("variable_name", variable)
            row["raw_variable"] = actual_variable
            row["raw_label"] = variable_row.get("variable_label", "")
            summary, error = read_variable_summary(source_path, actual_variable)
            if error:
                row["blocking_reason"] = f"{row['blocking_reason']}; value read note: {error}"
                row["row_count"] = file_row.get("row_count", "")
            else:
                row.update(summary)
            rows.append(row)

    for item in NO_VARIABLE_ROWS:
        row = base_row(item["domain"], item["harmonized"])
        row.update(
            {
                "documentation_support_status": item["status"],
                "recipe_decision": item["decision"],
                "blocking_reason": item["blocking"],
                "next_action": item["next"],
            }
        )
        rows.append(row)

    questionnaire_rows = [
        row
        for row in raw_files
        if "lsms2005en" in row.get("source_path", "").lower()
        and Path(row.get("source_path", "")).suffix.lower() == ".xls"
    ]
    questionnaire_reader = importlib.util.find_spec("xlrd") is not None
    row = base_row("documentation_reader", "questionnaire_xls")
    row.update(
        {
            "source_file": compact_join([Path(item.get("source_path", "")).name for item in questionnaire_rows], 10),
            "source_path": compact_join([item.get("source_path", "") for item in questionnaire_rows], 10),
            "documentation_support_status": "documentation_reader_available" if questionnaire_reader else "blocked_optional_questionnaire_reader_missing",
            "recipe_decision": "not_recipe_ready_questionnaire_extraction_pending",
            "blocking_reason": "" if questionnaire_reader else "xlrd is not installed, so legacy XLS questionnaire extraction is left as an optional manual/documentation step",
            "next_action": "extract questionnaire text/tables if xlrd or another trusted XLS reader is installed; do not add a dependency just to promote recipe rows",
        }
    )
    rows.append(row)
    rows.sort(key=lambda item: (item["evidence_domain"], item["harmonized_variable"], item["source_file"], item["raw_variable"]))
    return rows


def build_summary(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    supported = sum(1 for row in rows if row.get("documentation_support_status", "").startswith("documentation_supported"))
    false_positive = sum(1 for row in rows if row.get("recipe_decision") == "blocked_false_positive")
    future_candidates = sum(1 for row in rows if row.get("recipe_decision", "").startswith("candidate_for_future"))
    timing_geo_blockers = sum(
        1
        for row in rows
        if row.get("recipe_decision") in {"not_recipe_ready_missing_timing", "not_recipe_ready_no_gps", "not_recipe_ready_missing_geography_coverage_review"}
    )
    rows_with_values = sum(1 for row in rows if row.get("nonmissing_count"))
    questionnaire_reader_available = "1" if any(row.get("documentation_support_status") == "documentation_reader_available" for row in rows) else "0"
    return [
        {"metric": "alb2005_documented_evidence_rows", "value": str(len(rows)), "interpretation": "Rows in the ALB_2005 documented harmonization review."},
        {"metric": "alb2005_rows_with_observed_value_summaries", "value": str(rows_with_values), "interpretation": "Rows where raw values were summarized from inspected SPSS files."},
        {"metric": "alb2005_documentation_supported_rows", "value": str(supported), "interpretation": "Rows with documentation/schema support but still requiring manual review."},
        {"metric": "alb2005_future_recipe_candidate_rows", "value": str(future_candidates), "interpretation": "Rows that may enter a future recipe only after manual key/unit/recall/skip review."},
        {"metric": "alb2005_false_positive_rows", "value": str(false_positive), "interpretation": "Rows explicitly rejected as false-positive harmonization candidates."},
        {"metric": "alb2005_timing_or_geography_blocker_rows", "value": str(timing_geo_blockers), "interpretation": "Rows blocking climate linkage because timing or geography evidence is insufficient."},
        {"metric": "alb2005_oop_candidate_rows", "value": str(sum(1 for row in rows if row.get("evidence_domain") == "oop_health_expenditure")), "interpretation": "Candidate OOP payment variables requiring aggregation/recall review."},
        {"metric": "alb2005_questionnaire_xls_reader_available", "value": questionnaire_reader_available, "interpretation": "Whether a trusted legacy XLS reader is available for questionnaire extraction."},
        {"metric": "alb2005_recipe_ready_rows", "value": "0", "interpretation": "This review does not promote any harmonization recipe rows."},
        {"metric": "alb2005_current_decision", "value": "not_ready_for_verified_recipe", "interpretation": "ALB_2005 remains blocked pending timing/geography, OOP aggregation, units, skip patterns, and merge-key review."},
    ]


def markdown_count_table(counter: Counter[str], label: str) -> str:
    lines = [f"| {label} | Count |", "|---|---:|"]
    for key, count in counter.most_common():
        lines.append(f"| {key or 'blank'} | {count} |")
    return "\n".join(lines)


def markdown_rows(rows: list[dict[str, str]], columns: list[str], limit: int = 18) -> str:
    lines = ["| " + " | ".join(columns) + " |", "|" + "|".join("---" for _ in columns) + "|"]
    for row in rows[:limit]:
        values = []
        for column in columns:
            value = (row.get(column, "") or "").replace("|", "/")
            if len(value) > 120:
                value = value[:117] + "..."
            values.append(value)
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines)


def write_report(rows: list[dict[str, str]], summary: list[dict[str, str]]) -> None:
    status_counts = Counter(row.get("documentation_support_status", "") for row in rows)
    decision_counts = Counter(row.get("recipe_decision", "") for row in rows)
    summary_table = "\n".join(f"| {row['metric']} | {row['value']} | {row['interpretation']} |" for row in summary)
    false_rows = [row for row in rows if row.get("recipe_decision") == "blocked_false_positive"]
    blockers = [
        row
        for row in rows
        if row.get("recipe_decision") in {"not_recipe_ready_missing_timing", "not_recipe_ready_no_gps", "not_recipe_ready_missing_geography_coverage_review"}
    ]
    candidate_rows = [row for row in rows if row.get("recipe_decision", "").startswith("candidate_for_future")]
    REPORT_PATH.write_text(
        f"""# ALB_2005 Documented Harmonization Review

Status: documentation-backed review only. This audit uses inspected ALB_2005 raw SPSS metadata and observed values to identify plausible future harmonization candidates and explicit false positives. It does not create or promote a harmonization recipe.

## Summary

| Metric | Value | Interpretation |
|---|---:|---|
{summary_table}

## Documentation Support Status

{markdown_count_table(status_counts, 'Status') if rows else 'No evidence rows exist.'}

## Recipe Decision

{markdown_count_table(decision_counts, 'Decision') if rows else 'No evidence rows exist.'}

## Candidate Rows Requiring Manual Review

{markdown_rows(candidate_rows, ['evidence_domain', 'harmonized_variable', 'source_file', 'raw_variable', 'raw_label', 'nonmissing_count', 'distinct_count', 'recipe_decision'], 22) if candidate_rows else 'No future candidate rows were identified.'}

## Explicit False Positives

{markdown_rows(false_rows, ['harmonized_variable', 'source_file', 'raw_variable', 'raw_label', 'recipe_decision', 'blocking_reason'], 10) if false_rows else 'No false-positive rows were identified.'}

## Timing And Geography Blockers

{markdown_rows(blockers, ['evidence_domain', 'harmonized_variable', 'source_file', 'raw_variable', 'nonmissing_count', 'distinct_count', 'recipe_decision', 'blocking_reason'], 10) if blockers else 'No timing/geography blockers were identified.'}

## Interpretation

- `weight_retro` and `totcons` are credible documented candidates for future review, not recipe-ready variables.
- The `m9a_*` payment variables are documented OOP candidates, but aggregation, recall period, care context, skip patterns, and missing-code semantics are unresolved.
- `m9b_q06` supports cost and distance/access-barrier review only after its referral/nonuse denominator is verified.
- `P11_Q5B` is a district-code candidate, but it is not GPS and its coverage/merge path must be verified before climate linkage.
- No interview month/date variable is currently verified for ALB_2005, so climate exposure timing remains blocked.
- `m10_q13a` and `m10_q13b` are birth-weight variables and must not be used as household/person survey weights.

## Machine-Readable Outputs

- `temp/alb2005_documented_variable_evidence.csv`
- `result/alb2005_documented_harmonization_summary.csv`
""",
        encoding="utf-8",
    )


def main() -> None:
    ensure_dirs()
    raw_files = read_csv_dicts(RAW_FILE_INVENTORY_PATH)
    raw_variables = read_csv_dicts(RAW_VARIABLE_CATALOG_PATH)
    evidence_rows = build_evidence_rows(raw_files, raw_variables)
    summary = build_summary(evidence_rows)
    write_csv(EVIDENCE_PATH, evidence_rows, EVIDENCE_COLUMNS)
    write_csv(SUMMARY_PATH, summary, SUMMARY_COLUMNS)
    write_report(evidence_rows, summary)
    append_log(TEMP_DIR / "audit_log.md", f"Built ALB_2005 documented harmonization review rows={len(evidence_rows)}.")
    print(f"ALB_2005 documented harmonization review rows={len(evidence_rows)}.")


if __name__ == "__main__":
    main()
