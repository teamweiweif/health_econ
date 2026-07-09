from __future__ import annotations

import csv
import math
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import pandas as pd

from common import REPORT_DIR, RESULT_DIR, TEMP_DIR, append_log, ensure_dirs, write_csv

try:
    import pyreadstat
except ImportError:  # pragma: no cover - the environment audit reports this separately.
    pyreadstat = None


MERGE_KEY_PLAN_PATH = TEMP_DIR / "first_batch_merge_key_lineage_plan.csv"
MERGE_KEY_CANDIDATE_PATH = TEMP_DIR / "first_batch_merge_key_candidate_variables.csv"
VARIABLE_TEMPLATE_PATH = TEMP_DIR / "first_batch_variable_verification_template.csv"
HARMONIZATION_SCAFFOLD_PATH = TEMP_DIR / "harmonization_recipe_scaffold.csv"
RAW_FILE_INVENTORY_PATH = TEMP_DIR / "raw_schema_inventory" / "raw_file_inventory.csv"
RAW_VARIABLE_CATALOG_PATH = TEMP_DIR / "raw_schema_inventory" / "raw_variable_catalog.csv"

VALUE_AUDIT_PATH = TEMP_DIR / "first_batch_raw_value_key_audit.csv"
KEY_AUDIT_PATH = TEMP_DIR / "first_batch_raw_merge_key_audit.csv"
AUTO_HARMONIZATION_VALUE_AUDIT_PATH = TEMP_DIR / "first_batch_harmonization_value_audit_auto.csv"
SUMMARY_PATH = RESULT_DIR / "first_batch_raw_value_key_summary.csv"
REPORT_PATH = REPORT_DIR / "first_batch_raw_value_key_audit.md"

MAX_RESOLVED_FILES_PER_CANDIDATE = 3
MAX_KEY_VARIABLES_PER_GROUP = 12
MISSING_CODE_CANDIDATES = {-99, -98, -97, -9, -8, -7, -6, -1, 98, 99, 997, 998, 999, 9998, 9999, 99999}
FALSE_SURVEY_WEIGHT_BIRTH_STATUS = "raw_variable_rejected_false_survey_weight_birth_measure"

VALUE_COLUMNS = [
    "batch_rank",
    "country",
    "survey_name",
    "wave",
    "idno",
    "audit_source",
    "concept",
    "harmonized_variable",
    "required",
    "merge_level",
    "key_role",
    "candidate_source_files",
    "candidate_raw_variable",
    "raw_label",
    "resolved_source_path",
    "resolved_file_name",
    "resolved_raw_variable",
    "variable_present",
    "candidate_file_match_status",
    "read_status",
    "row_count",
    "nonmissing_count",
    "missing_count",
    "distinct_count",
    "min_value",
    "max_value",
    "negative_count",
    "zero_count",
    "positive_count",
    "top_values",
    "value_label_count",
    "missing_code_candidates",
    "value_audit_status",
    "promotion_status",
    "blocking_reason",
]

KEY_COLUMNS = [
    "batch_rank",
    "country",
    "survey_name",
    "wave",
    "idno",
    "lineage_role",
    "resolved_source_path",
    "resolved_file_name",
    "key_variables",
    "variables_present",
    "read_status",
    "row_count",
    "complete_key_rows",
    "missing_key_rows",
    "distinct_key_count",
    "duplicate_key_rows",
    "uniqueness_ratio",
    "positive_weight_rows",
    "nonpositive_weight_rows",
    "nesting_or_level_status",
    "key_audit_status",
    "blocking_reason",
]

AUTO_VALUE_COLUMNS = [
    "country",
    "survey_name",
    "wave",
    "idno",
    "concept",
    "harmonized_variable",
    "source_file",
    "raw_variable",
    "raw_label",
    "value_audit_status",
    "ready_for_recipe",
    "confirmed_merge_level",
    "confirmed_key_role",
    "confirmed_unit",
    "confirmed_recall_period",
    "missing_code_rule",
    "valid_range_rule",
    "lineage_notes",
    "auditor",
    "audit_date",
]

SUMMARY_COLUMNS = ["metric", "value", "interpretation"]


def read_csv_dicts(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def safe_int(value: Any, default: int = 0) -> int:
    try:
        return int(float(str(value).strip()))
    except (TypeError, ValueError):
        return default


def split_values(value: str, limit: int | None = None) -> list[str]:
    out: list[str] = []
    seen: set[str] = set()
    for item in (value or "").replace(",", ";").split(";"):
        clean = item.strip()
        if not clean:
            continue
        key = clean.lower()
        if key in seen:
            continue
        out.append(clean)
        seen.add(key)
        if limit is not None and len(out) >= limit:
            break
    return out


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


def normalize_token(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", (value or "").lower())


def is_false_survey_weight_birth_measure(
    row: dict[str, str],
    variable_field: str,
    assume_survey_weight: bool = False,
) -> bool:
    role_text = normalize_token(
        " ".join(
            [
                row.get("concept", ""),
                row.get("harmonized_variable", ""),
                row.get("key_role", ""),
                row.get("lineage_role", ""),
            ]
        )
    )
    is_survey_weight = assume_survey_weight or "surveyweight" in role_text or "householdweight" in role_text or "personweight" in role_text
    if not is_survey_weight:
        return False
    variable = normalize_token(row.get(variable_field, "") or row.get("variable_name", "") or row.get("raw_variable", ""))
    label = (row.get("raw_label", "") or row.get("variable_label", "") or "").lower()
    if variable in {"m10q13a", "m10q13b"}:
        return True
    return "weight at birth" in label and variable not in {"weight", "pweight", "weightretro"}


def normalized_file_text(value: str) -> str:
    text = (value or "").replace("\\", "/").lower()
    pieces = [Path(text).name, Path(text).stem, text]
    return " ".join(normalize_token(piece) for piece in pieces if piece)


def file_matches(candidate_files: list[str], source_path: str) -> bool:
    if not candidate_files:
        return True
    source_norm = normalized_file_text(source_path)
    for item in candidate_files:
        item_norm = normalize_token(item)
        if item_norm and (item_norm in source_norm or source_norm in item_norm):
            return True
    return False


def infer_idno_from_row(row: dict[str, str], known_idnos: set[str]) -> str:
    haystack = " ".join(str(value) for value in row.values()).lower().replace("\\", "/")
    for idno in sorted(known_idnos, key=len, reverse=True):
        if idno and idno.lower() in haystack:
            return idno
    return ""


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


def read_table_columns(path: Path, columns: list[str]) -> tuple[pd.DataFrame | None, Any, str]:
    columns = list(dict.fromkeys(column for column in columns if column))
    if not columns:
        return pd.DataFrame(), None, ""
    suffix = path.suffix.lower()
    try:
        if suffix == ".sav":
            if pyreadstat is None:
                return None, None, "pyreadstat_not_available"
            df, meta = pyreadstat.read_sav(str(path), usecols=columns, apply_value_formats=False)
            return df, meta, ""
        if suffix == ".por":
            if pyreadstat is None:
                return None, None, "pyreadstat_not_available"
            df, meta = pyreadstat.read_por(str(path), usecols=columns)
            return df, meta, ""
        if suffix == ".dta":
            if pyreadstat is None:
                return None, None, "pyreadstat_not_available"
            df, meta = pyreadstat.read_dta(str(path), usecols=columns, apply_value_formats=False)
            return df, meta, ""
        if suffix == ".sas7bdat":
            if pyreadstat is None:
                return None, None, "pyreadstat_not_available"
            df, meta = pyreadstat.read_sas7bdat(str(path), usecols=columns)
            return df, meta, ""
        if suffix == ".xpt":
            if pyreadstat is None:
                return None, None, "pyreadstat_not_available"
            df, meta = pyreadstat.read_xport(str(path), usecols=columns)
            return df, meta, ""
        if suffix in {".csv", ".txt"}:
            df = pd.read_csv(path, usecols=lambda col: col in set(columns), low_memory=False)
            return df, None, ""
        if suffix == ".tsv":
            df = pd.read_csv(path, sep="\t", usecols=lambda col: col in set(columns), low_memory=False)
            return df, None, ""
        if suffix in {".xls", ".xlsx"}:
            df = pd.read_excel(path, usecols=lambda col: col in set(columns))
            return df, None, ""
    except Exception as exc:  # pragma: no cover - exact raw reader errors are data-dependent.
        return None, None, f"{type(exc).__name__}: {str(exc)[:220]}"
    return None, None, f"unsupported_file_format_{suffix or 'blank'}"


def value_label_count(meta: Any, variable: str) -> str:
    if meta is None:
        return ""
    variable_to_label = getattr(meta, "variable_to_label", {}) or {}
    value_labels = getattr(meta, "value_labels", {}) or {}
    label_name = variable_to_label.get(variable)
    if not label_name:
        return "0"
    labels = value_labels.get(label_name, {})
    return str(len(labels))


def summarize_series(series: pd.Series) -> dict[str, str]:
    nonmissing = series.dropna()
    row_count = len(series)
    distinct = nonmissing.nunique(dropna=True)
    numeric = pd.to_numeric(nonmissing, errors="coerce")
    numeric_nonmissing = numeric.dropna()
    is_numeric = pd.api.types.is_numeric_dtype(series) or (len(nonmissing) > 0 and len(numeric_nonmissing) / len(nonmissing) >= 0.9)
    out = {
        "row_count": str(row_count),
        "nonmissing_count": str(len(nonmissing)),
        "missing_count": str(row_count - len(nonmissing)),
        "distinct_count": str(distinct),
        "min_value": "",
        "max_value": "",
        "negative_count": "",
        "zero_count": "",
        "positive_count": "",
        "top_values": "",
        "missing_code_candidates": "",
    }
    if is_numeric and len(numeric_nonmissing) > 0:
        out["min_value"] = format_scalar(numeric_nonmissing.min())
        out["max_value"] = format_scalar(numeric_nonmissing.max())
        out["negative_count"] = str(int((numeric_nonmissing < 0).sum()))
        out["zero_count"] = str(int((numeric_nonmissing == 0).sum()))
        out["positive_count"] = str(int((numeric_nonmissing > 0).sum()))
        missing_hits = []
        rounded_values = {int(value) for value in numeric_nonmissing if float(value).is_integer()}
        for candidate in sorted(MISSING_CODE_CANDIDATES):
            if candidate in rounded_values:
                missing_hits.append(str(candidate))
        out["missing_code_candidates"] = compact_join(missing_hits, 20)
    top_values = []
    for value, count in nonmissing.astype(str).value_counts(dropna=True).head(8).items():
        top_values.append(f"{format_scalar(value)}:{int(count)}")
    out["top_values"] = compact_join(top_values, 8)
    return out


def raw_ready_plan_rows(plan_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    return [row for row in plan_rows if row.get("raw_gate_status") and row.get("raw_gate_status") != "blocked_raw_microdata"]


def build_variable_catalog(
    raw_variables: list[dict[str, str]],
    raw_files: list[dict[str, str]],
    known_idnos: set[str],
) -> tuple[dict[str, list[dict[str, str]]], dict[str, dict[str, dict[str, str]]]]:
    file_status_by_path: dict[str, dict[str, str]] = {}
    for row in raw_files:
        source_path = row.get("source_path", "")
        if source_path:
            file_status_by_path[source_path] = row

    by_idno_var: dict[str, list[dict[str, str]]] = defaultdict(list)
    by_idno_file_var: dict[str, dict[str, dict[str, str]]] = defaultdict(dict)
    for row in raw_variables:
        idno = row.get("idno", "") or infer_idno_from_row(row, known_idnos)
        variable = (row.get("variable_name", "") or row.get("raw_variable", "")).strip()
        if not idno or not variable:
            continue
        source_path = row.get("source_path", "")
        enriched = {**row}
        enriched["idno"] = idno
        enriched["source_file_status"] = file_status_by_path.get(source_path, {}).get("status", "")
        enriched["row_count"] = file_status_by_path.get(source_path, {}).get("row_count", "")
        enriched["column_count"] = file_status_by_path.get(source_path, {}).get("column_count", "")
        by_idno_var[(idno + "\n" + variable.lower())].append(enriched)
        by_idno_file_var[idno][source_path + "\n" + variable.lower()] = enriched
    return by_idno_var, by_idno_file_var


def lookup_variable_rows(
    variable_index: dict[str, list[dict[str, str]]],
    idno: str,
    raw_variable: str,
    candidate_files: list[str],
) -> tuple[list[dict[str, str]], str]:
    rows = variable_index.get(idno + "\n" + raw_variable.lower(), [])
    if not rows:
        return [], "raw_variable_not_found"
    matched = [row for row in rows if file_matches(candidate_files, row.get("source_path", ""))]
    if matched:
        matched.sort(key=lambda row: (safe_int(row.get("row_count"), 10**9), row.get("source_path", "")))
        return matched[:MAX_RESOLVED_FILES_PER_CANDIDATE], "candidate_file_matched"
    rows.sort(key=lambda row: (safe_int(row.get("row_count"), 10**9), row.get("source_path", "")))
    return rows[:MAX_RESOLVED_FILES_PER_CANDIDATE], "raw_variable_seen_outside_candidate_files"


def build_value_candidates(
    scaffold_rows: list[dict[str, str]],
    variable_template_rows: list[dict[str, str]],
    raw_ready_idnos: set[str],
    plan_by_idno: dict[str, dict[str, str]],
) -> list[dict[str, str]]:
    candidates: list[dict[str, str]] = []
    seen: set[tuple[str, str, str, str, str]] = set()

    for row in scaffold_rows:
        idno = row.get("idno", "")
        if idno not in raw_ready_idnos:
            continue
        for raw in split_values(row.get("raw_variable", "")):
            key = ("harmonization_scaffold", idno, row.get("harmonized_variable", ""), raw.lower(), row.get("source_file", ""))
            if key in seen:
                continue
            seen.add(key)
            plan = plan_by_idno.get(idno, {})
            candidates.append(
                {
                    "batch_rank": plan.get("batch_rank", ""),
                    "country": row.get("country", plan.get("country", "")),
                    "survey_name": row.get("survey_name", plan.get("survey_name", "")),
                    "wave": row.get("wave", plan.get("wave", "")),
                    "idno": idno,
                    "audit_source": "harmonization_scaffold",
                    "concept": row.get("concept", ""),
                    "harmonized_variable": row.get("harmonized_variable", ""),
                    "required": row.get("required", ""),
                    "merge_level": row.get("merge_level", ""),
                    "key_role": row.get("key_role", ""),
                    "candidate_source_files": row.get("source_file", ""),
                    "candidate_raw_variable": raw,
                    "raw_label": row.get("raw_label", ""),
                }
            )

    for row in variable_template_rows:
        idno = row.get("idno", "")
        if idno not in raw_ready_idnos:
            continue
        raw = row.get("candidate_raw_variable", "")
        if not raw:
            continue
        key = ("first_batch_variable_template", idno, row.get("candidate_harmonized_variables", ""), raw.lower(), row.get("candidate_files", ""))
        if key in seen:
            continue
        seen.add(key)
        candidates.append(
            {
                "batch_rank": row.get("batch_rank", ""),
                "country": row.get("country", ""),
                "survey_name": row.get("survey_name", ""),
                "wave": row.get("wave", ""),
                "idno": idno,
                "audit_source": "first_batch_variable_template",
                "concept": row.get("concept", ""),
                "harmonized_variable": row.get("candidate_harmonized_variables", ""),
                "required": row.get("required_for", ""),
                "merge_level": "",
                "key_role": "",
                "candidate_source_files": row.get("candidate_files", ""),
                "candidate_raw_variable": raw,
                "raw_label": row.get("raw_label", ""),
            }
        )

    candidates.sort(key=lambda row: (safe_int(row.get("batch_rank"), 9999), row.get("idno", ""), row.get("concept", ""), row.get("harmonized_variable", ""), row.get("candidate_raw_variable", "")))
    return candidates


def resolve_value_rows(candidates: list[dict[str, str]], variable_index: dict[str, list[dict[str, str]]]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for candidate in candidates:
        candidate_files = split_values(candidate.get("candidate_source_files", ""))
        candidate_false_weight = is_false_survey_weight_birth_measure(candidate, "candidate_raw_variable")
        matched_rows, match_status = lookup_variable_rows(
            variable_index,
            candidate.get("idno", ""),
            candidate.get("candidate_raw_variable", ""),
            candidate_files,
        )
        if not matched_rows:
            value_status = FALSE_SURVEY_WEIGHT_BIRTH_STATUS if candidate_false_weight else "raw_variable_not_found"
            blocking_reason = (
                "birth-weight variables are child health/fertility measures and are not survey design weights"
                if candidate_false_weight
                else "candidate raw variable was not found in raw_variable_catalog for the raw-ready dataset"
            )
            rows.append(
                {
                    **candidate,
                    "resolved_source_path": "",
                    "resolved_file_name": "",
                    "resolved_raw_variable": "",
                    "variable_present": "0",
                    "candidate_file_match_status": match_status,
                    "read_status": "not_attempted",
                    "value_audit_status": value_status,
                    "promotion_status": "not_promoted",
                    "blocking_reason": blocking_reason,
                }
            )
            continue
        for raw_row in matched_rows:
            source_path = raw_row.get("source_path", "")
            raw_label = candidate.get("raw_label", "") or raw_row.get("variable_label", "")
            if candidate_false_weight or is_false_survey_weight_birth_measure(raw_row, "variable_name", assume_survey_weight=True):
                rows.append(
                    {
                        **candidate,
                        "raw_label": raw_label,
                        "resolved_source_path": source_path,
                        "resolved_file_name": Path(source_path).name if source_path else "",
                        "resolved_raw_variable": raw_row.get("variable_name", ""),
                        "variable_present": "1",
                        "candidate_file_match_status": match_status,
                        "read_status": "not_attempted_rejected_false_positive",
                        "value_label_count": "",
                        "value_audit_status": FALSE_SURVEY_WEIGHT_BIRTH_STATUS,
                        "promotion_status": "not_promoted_false_positive",
                        "blocking_reason": "birth-weight variables are child health/fertility measures and are not survey design weights",
                    }
                )
                continue
            rows.append(
                {
                    **candidate,
                    "raw_label": raw_label,
                    "resolved_source_path": source_path,
                    "resolved_file_name": Path(source_path).name if source_path else "",
                    "resolved_raw_variable": raw_row.get("variable_name", ""),
                    "variable_present": "1",
                    "candidate_file_match_status": match_status,
                    "read_status": "pending",
                    "value_label_count": "",
                    "value_audit_status": "pending_raw_value_read",
                    "promotion_status": "not_promoted",
                    "blocking_reason": "",
                }
            )
    return rows


def build_key_groups(
    key_candidates: list[dict[str, str]],
    raw_ready_idnos: set[str],
    variable_index: dict[str, list[dict[str, str]]],
    plan_by_idno: dict[str, dict[str, str]],
) -> dict[tuple[str, str, str], dict[str, Any]]:
    groups: dict[tuple[str, str, str], dict[str, Any]] = {}
    for row in key_candidates:
        idno = row.get("idno", "")
        if idno not in raw_ready_idnos:
            continue
        role = row.get("lineage_role", "")
        raw_variable = row.get("raw_variable", "")
        if not role or not raw_variable:
            continue
        if is_false_survey_weight_birth_measure(row, "raw_variable", assume_survey_weight=role == "survey_weight"):
            continue
        candidate_files = split_values(row.get("file_name", ""))
        matched_rows, _ = lookup_variable_rows(variable_index, idno, raw_variable, candidate_files)
        for raw_row in matched_rows:
            if is_false_survey_weight_birth_measure(raw_row, "variable_name", assume_survey_weight=role == "survey_weight"):
                continue
            source_path = raw_row.get("source_path", "")
            key = (idno, source_path, role)
            plan = plan_by_idno.get(idno, {})
            group = groups.setdefault(
                key,
                {
                    "batch_rank": plan.get("batch_rank", row.get("batch_rank", "")),
                    "country": plan.get("country", row.get("country", "")),
                    "survey_name": plan.get("survey_name", row.get("survey_name", "")),
                    "wave": plan.get("wave", row.get("wave", "")),
                    "idno": idno,
                    "lineage_role": role,
                    "resolved_source_path": source_path,
                    "resolved_file_name": Path(source_path).name if source_path else "",
                    "variables": [],
                },
            )
            variable = raw_row.get("variable_name", "")
            if variable and variable not in group["variables"] and len(group["variables"]) < MAX_KEY_VARIABLES_PER_GROUP:
                group["variables"].append(variable)
    return groups


def fill_value_summaries(rows: list[dict[str, str]], read_cache: dict[str, tuple[pd.DataFrame | None, Any, str]]) -> list[dict[str, str]]:
    out: list[dict[str, str]] = []
    for row in rows:
        source_path = row.get("resolved_source_path", "")
        variable = row.get("resolved_raw_variable", "")
        if row.get("value_audit_status") == FALSE_SURVEY_WEIGHT_BIRTH_STATUS:
            out.append({column: row.get(column, "") for column in VALUE_COLUMNS})
            continue
        if row.get("variable_present") != "1":
            out.append({column: row.get(column, "") for column in VALUE_COLUMNS})
            continue
        df, meta, error = read_cache.get(source_path, (None, None, "raw_file_not_read"))
        if error:
            row.update(
                {
                    "read_status": f"read_failed:{error}",
                    "value_audit_status": "raw_value_read_failed",
                    "promotion_status": "not_promoted",
                    "blocking_reason": "raw file could not be read for value audit",
                }
            )
        elif df is None or variable not in df.columns:
            row.update(
                {
                    "read_status": "resolved_variable_missing_from_read_frame",
                    "value_audit_status": "raw_value_read_failed",
                    "promotion_status": "not_promoted",
                    "blocking_reason": "resolved variable was not returned by the raw reader",
                }
            )
        else:
            summary = summarize_series(df[variable])
            row.update(summary)
            row["read_status"] = "read_ok"
            row["value_label_count"] = value_label_count(meta, variable)
            if safe_int(summary["nonmissing_count"]) == 0:
                row["value_audit_status"] = "raw_value_all_missing_blocked"
                row["promotion_status"] = "not_promoted"
                row["blocking_reason"] = "raw variable was present but all values were missing"
            else:
                row["value_audit_status"] = "raw_value_summary_available_manual_interpretation_required"
                row["promotion_status"] = "not_promoted_manual_unit_recall_missing_code_key_review_required"
                if row.get("candidate_file_match_status") == "raw_variable_seen_outside_candidate_files":
                    row["blocking_reason"] = "raw variable was found, but not in a file matching the metadata candidate source name; lineage requires manual review"
                else:
                    row["blocking_reason"] = "values were summarized, but unit, recall period, missing-code semantics, skip patterns, and merge keys are not yet human-verified"
        out.append({column: row.get(column, "") for column in VALUE_COLUMNS})
    return out


def fill_key_summaries(groups: dict[tuple[str, str, str], dict[str, Any]], read_cache: dict[str, tuple[pd.DataFrame | None, Any, str]]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for _, group in sorted(groups.items(), key=lambda item: (safe_int(item[1].get("batch_rank"), 9999), item[1].get("idno", ""), item[1].get("resolved_file_name", ""), item[1].get("lineage_role", ""))):
        source_path = group.get("resolved_source_path", "")
        variables = list(group.get("variables", []))
        df, _, error = read_cache.get(source_path, (None, None, "raw_file_not_read"))
        row = {
            "batch_rank": group.get("batch_rank", ""),
            "country": group.get("country", ""),
            "survey_name": group.get("survey_name", ""),
            "wave": group.get("wave", ""),
            "idno": group.get("idno", ""),
            "lineage_role": group.get("lineage_role", ""),
            "resolved_source_path": source_path,
            "resolved_file_name": group.get("resolved_file_name", ""),
            "key_variables": compact_join(variables, MAX_KEY_VARIABLES_PER_GROUP),
            "variables_present": "",
            "read_status": "",
            "row_count": "",
            "complete_key_rows": "",
            "missing_key_rows": "",
            "distinct_key_count": "",
            "duplicate_key_rows": "",
            "uniqueness_ratio": "",
            "positive_weight_rows": "",
            "nonpositive_weight_rows": "",
            "nesting_or_level_status": "",
            "key_audit_status": "",
            "blocking_reason": "",
        }
        if error:
            row["read_status"] = f"read_failed:{error}"
            row["key_audit_status"] = "raw_key_read_failed"
            row["blocking_reason"] = "raw file could not be read for key audit"
            rows.append(row)
            continue
        if df is None:
            row["read_status"] = "raw_file_not_read"
            row["key_audit_status"] = "raw_key_read_failed"
            row["blocking_reason"] = "raw file was not available in the read cache"
            rows.append(row)
            continue
        present = [variable for variable in variables if variable in df.columns]
        row["variables_present"] = compact_join(present, MAX_KEY_VARIABLES_PER_GROUP)
        row["read_status"] = "read_ok"
        row["row_count"] = str(len(df))
        if not present:
            row["key_audit_status"] = "key_variables_missing_from_read_frame"
            row["blocking_reason"] = "candidate key variables were not returned by the raw reader"
            rows.append(row)
            continue
        key_df = df[present]
        complete = key_df.notna().all(axis=1)
        complete_key_rows = int(complete.sum())
        distinct_key_count = int(key_df.loc[complete].drop_duplicates().shape[0]) if complete_key_rows else 0
        duplicate_rows = max(complete_key_rows - distinct_key_count, 0)
        row["complete_key_rows"] = str(complete_key_rows)
        row["missing_key_rows"] = str(len(df) - complete_key_rows)
        row["distinct_key_count"] = str(distinct_key_count)
        row["duplicate_key_rows"] = str(duplicate_rows)
        row["uniqueness_ratio"] = f"{(distinct_key_count / complete_key_rows):.6f}" if complete_key_rows else "0"
        role = row["lineage_role"]
        if role == "survey_weight":
            numeric = pd.to_numeric(key_df[present[0]], errors="coerce")
            row["positive_weight_rows"] = str(int((numeric > 0).sum()))
            row["nonpositive_weight_rows"] = str(int((numeric <= 0).sum()))
            row["nesting_or_level_status"] = "weight_distribution_summary_only"
            if complete_key_rows == 0:
                row["key_audit_status"] = "weight_all_missing_blocked"
            elif int(row["nonpositive_weight_rows"]) > 0:
                row["key_audit_status"] = "weight_nonpositive_values_require_manual_review"
            else:
                row["key_audit_status"] = "weight_summary_available_manual_design_review_required"
        elif role in {"household_id", "person_id"}:
            row["nesting_or_level_status"] = "unique_at_file_row_level" if duplicate_rows == 0 and complete_key_rows > 0 else "repeats_at_file_row_level"
            if complete_key_rows == 0:
                row["key_audit_status"] = "id_all_missing_blocked"
            elif duplicate_rows == 0:
                row["key_audit_status"] = "key_unique_at_file_row_level_manual_cross_file_review_required"
            else:
                row["key_audit_status"] = "key_repeats_at_file_row_level_manual_merge_level_review_required"
        else:
            row["nesting_or_level_status"] = "distribution_summary_only"
            row["key_audit_status"] = "key_summary_available_manual_design_level_review_required" if complete_key_rows > 0 else "key_all_missing_blocked"
        row["blocking_reason"] = "merge role, file level, cross-file cardinality, and survey documentation remain manually unverified"
        rows.append(row)
    return rows


def build_auto_harmonization_value_rows(value_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    seen: set[tuple[str, str, str, str]] = set()
    for row in value_rows:
        if row.get("audit_source") != "harmonization_scaffold":
            continue
        key = (row.get("idno", ""), row.get("harmonized_variable", ""), row.get("candidate_raw_variable", "").lower(), row.get("resolved_source_path", ""))
        if key in seen:
            continue
        seen.add(key)
        if row.get("variable_present") != "1":
            status = "raw_variable_not_found"
            notes = "Auto audit did not find the raw variable in the raw catalog."
        elif row.get("value_audit_status") == FALSE_SURVEY_WEIGHT_BIRTH_STATUS:
            status = FALSE_SURVEY_WEIGHT_BIRTH_STATUS
            notes = row.get("blocking_reason", "")
        elif row.get("read_status") != "read_ok":
            status = "raw_value_read_failed"
            notes = row.get("blocking_reason", "")
        else:
            status = row.get("value_audit_status", "")
            notes = (
                f"Auto summary only: source={row.get('resolved_source_path', '')}; "
                f"nonmissing={row.get('nonmissing_count', '')}; distinct={row.get('distinct_count', '')}; "
                f"top_values={row.get('top_values', '')}; promotion remains blocked pending human unit, recall, missing-code, skip-pattern, and merge-key review."
            )
        valid_range = ""
        if row.get("min_value") or row.get("max_value"):
            valid_range = f"observed_min={row.get('min_value', '')}; observed_max={row.get('max_value', '')}"
        missing_rule = f"candidate_codes_seen={row.get('missing_code_candidates', '')}" if row.get("missing_code_candidates") else ""
        rows.append(
            {
                "country": row.get("country", ""),
                "survey_name": row.get("survey_name", ""),
                "wave": row.get("wave", ""),
                "idno": row.get("idno", ""),
                "concept": row.get("concept", ""),
                "harmonized_variable": row.get("harmonized_variable", ""),
                "source_file": row.get("resolved_file_name", "") or row.get("candidate_source_files", ""),
                "raw_variable": row.get("candidate_raw_variable", ""),
                "raw_label": row.get("raw_label", ""),
                "value_audit_status": status,
                "ready_for_recipe": "0",
                "confirmed_merge_level": "",
                "confirmed_key_role": row.get("key_role", ""),
                "confirmed_unit": "",
                "confirmed_recall_period": "",
                "missing_code_rule": missing_rule,
                "valid_range_rule": valid_range,
                "lineage_notes": notes,
                "auditor": "script/45_audit_first_batch_raw_value_keys.py",
                "audit_date": "",
            }
        )
    rows.sort(key=lambda item: (item.get("idno", ""), item.get("concept", ""), item.get("harmonized_variable", ""), item.get("raw_variable", "")))
    return rows


def build_summary(
    raw_ready_rows: list[dict[str, str]],
    value_candidates: list[dict[str, str]],
    value_rows: list[dict[str, str]],
    key_rows: list[dict[str, str]],
    auto_rows: list[dict[str, str]],
) -> list[dict[str, str]]:
    value_status = Counter(row.get("value_audit_status", "") for row in value_rows)
    key_status = Counter(row.get("key_audit_status", "") for row in key_rows)
    read_status = Counter(row.get("read_status", "") for row in value_rows)
    rows = [
        {"metric": "raw_ready_first_batch_dataset_rows", "value": str(len(raw_ready_rows)), "interpretation": "First-batch datasets with raw files and variables present for value/key audit."},
        {"metric": "raw_ready_first_batch_idnos", "value": compact_join([row.get("idno", "") for row in raw_ready_rows], 30), "interpretation": "IDNOs entering the raw value/key audit."},
        {"metric": "first_batch_value_candidate_rows", "value": str(len(value_candidates)), "interpretation": "Candidate raw variable rows gathered from the harmonization scaffold and first-batch variable template."},
        {"metric": "first_batch_value_audit_rows", "value": str(len(value_rows)), "interpretation": "Resolved or blocked long-form value-audit rows."},
        {"metric": "first_batch_value_rows_variable_present", "value": str(sum(1 for row in value_rows if row.get("variable_present") == "1")), "interpretation": "Value-audit rows whose candidate raw variable was found in the raw schema catalog."},
        {"metric": "first_batch_value_rows_read_ok", "value": str(sum(1 for row in value_rows if row.get("read_status") == "read_ok")), "interpretation": "Value-audit rows whose raw values were read successfully."},
        {"metric": "first_batch_value_rows_nonmissing", "value": str(sum(1 for row in value_rows if safe_int(row.get("nonmissing_count"), 0) > 0)), "interpretation": "Value-audit rows with at least one nonmissing observed raw value."},
        {"metric": "first_batch_false_survey_weight_birth_measure_rows", "value": str(sum(1 for row in value_rows if row.get("value_audit_status") == FALSE_SURVEY_WEIGHT_BIRTH_STATUS)), "interpretation": "Survey-weight candidates rejected because the raw variable is a birth-weight measure."},
        {"metric": "first_batch_auto_harmonization_value_audit_rows", "value": str(len(auto_rows)), "interpretation": "Fail-closed auto value-audit rows provided to the harmonization gate."},
        {"metric": "first_batch_key_audit_rows", "value": str(len(key_rows)), "interpretation": "File-level key/design/geography/timing cardinality audit rows."},
        {"metric": "first_batch_key_rows_read_ok", "value": str(sum(1 for row in key_rows if row.get("read_status") == "read_ok")), "interpretation": "Key-audit rows whose raw files were read successfully."},
        {"metric": "first_batch_recipe_promoted_rows", "value": "0", "interpretation": "This audit never promotes a harmonization recipe; manual unit/recall/missing-code/key review is still required."},
    ]
    for status, count in sorted(value_status.items()):
        rows.append({"metric": f"value_audit_status_{status or 'blank'}", "value": str(count), "interpretation": "First-batch raw value-audit status count."})
    for status, count in sorted(key_status.items()):
        rows.append({"metric": f"key_audit_status_{status or 'blank'}", "value": str(count), "interpretation": "First-batch raw key-audit status count."})
    for status, count in sorted(read_status.items()):
        rows.append({"metric": f"value_read_status_{status or 'blank'}", "value": str(count), "interpretation": "First-batch raw value read-status count."})
    return rows


def markdown_rows(rows: list[dict[str, str]], columns: list[str], limit: int = 18) -> str:
    lines = ["| " + " | ".join(columns) + " |", "|" + "|".join("---" for _ in columns) + "|"]
    for row in rows[:limit]:
        values = []
        for column in columns:
            value = (row.get(column, "") or "").replace("|", "/")
            if len(value) > 110:
                value = value[:107] + "..."
            values.append(value)
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines)


def markdown_count_table(counter: Counter[str], label: str) -> str:
    lines = [f"| {label} | Count |", "|---|---:|"]
    for key, count in counter.most_common():
        lines.append(f"| {key or 'blank'} | {count} |")
    return "\n".join(lines)


def write_report(summary: list[dict[str, str]], value_rows: list[dict[str, str]], key_rows: list[dict[str, str]]) -> None:
    value_status = Counter(row.get("value_audit_status", "") for row in value_rows)
    key_status = Counter(row.get("key_audit_status", "") for row in key_rows)
    value_read = Counter(row.get("read_status", "") for row in value_rows)
    summary_table = "\n".join(f"| {row['metric']} | {row['value']} | {row['interpretation']} |" for row in summary)
    REPORT_PATH.write_text(
        f"""# First-Batch Raw Value And Key Audit

Status: raw-value summary layer only. This audit reads observed values and key candidates for first-batch datasets whose raw files are already present. It does not promote a harmonization recipe or create analysis-ready data.

## Summary

| Metric | Value | Interpretation |
|---|---:|---|
{summary_table}

## Value Audit Status

{markdown_count_table(value_status, 'Value-audit status') if value_rows else 'No value-audit rows were generated.'}

## Value Read Status

{markdown_count_table(value_read, 'Value read status') if value_rows else 'No value read rows were generated.'}

## Key Audit Status

{markdown_count_table(key_status, 'Key-audit status') if key_rows else 'No key-audit rows were generated.'}

## Value Examples

{markdown_rows(value_rows, ['idno', 'concept', 'harmonized_variable', 'candidate_raw_variable', 'resolved_file_name', 'nonmissing_count', 'distinct_count', 'min_value', 'max_value', 'top_values', 'value_audit_status'], 20) if value_rows else 'No value examples available.'}

## Key Examples

{markdown_rows(key_rows, ['idno', 'lineage_role', 'resolved_file_name', 'key_variables', 'row_count', 'complete_key_rows', 'distinct_key_count', 'duplicate_key_rows', 'key_audit_status'], 20) if key_rows else 'No key examples available.'}

## Guardrails

- `raw_value_summary_available_manual_interpretation_required` means the raw values were read, not that the variable is harmonized.
- `key_*_manual_*_review_required` means cardinality was summarized, not that merge keys or survey design variables are verified.
- The generated auto value-audit sidecar sets `ready_for_recipe=0` for every row.
- Do not construct `data/harmonized_household.csv`, outcomes, climate linkage, models, causal estimates, or policy-learning outputs from this audit alone.

## Machine-Readable Outputs

- `temp/first_batch_raw_value_key_audit.csv`
- `temp/first_batch_raw_merge_key_audit.csv`
- `temp/first_batch_harmonization_value_audit_auto.csv`
- `result/first_batch_raw_value_key_summary.csv`
""",
        encoding="utf-8",
    )


def main() -> None:
    ensure_dirs()
    plan_rows = read_csv_dicts(MERGE_KEY_PLAN_PATH)
    raw_ready_rows = raw_ready_plan_rows(plan_rows)
    raw_ready_idnos = {row.get("idno", "") for row in raw_ready_rows if row.get("idno", "")}
    plan_by_idno = {row.get("idno", ""): row for row in raw_ready_rows if row.get("idno", "")}
    raw_files = read_csv_dicts(RAW_FILE_INVENTORY_PATH)
    raw_variables = read_csv_dicts(RAW_VARIABLE_CATALOG_PATH)
    variable_index, _ = build_variable_catalog(raw_variables, raw_files, raw_ready_idnos)

    value_candidates = build_value_candidates(
        read_csv_dicts(HARMONIZATION_SCAFFOLD_PATH),
        read_csv_dicts(VARIABLE_TEMPLATE_PATH),
        raw_ready_idnos,
        plan_by_idno,
    )
    value_rows_pending = resolve_value_rows(value_candidates, variable_index)

    key_groups = build_key_groups(
        read_csv_dicts(MERGE_KEY_CANDIDATE_PATH),
        raw_ready_idnos,
        variable_index,
        plan_by_idno,
    )

    needed_by_path: dict[str, set[str]] = defaultdict(set)
    for row in value_rows_pending:
        if (
            row.get("resolved_source_path")
            and row.get("resolved_raw_variable")
            and row.get("value_audit_status") != FALSE_SURVEY_WEIGHT_BIRTH_STATUS
        ):
            needed_by_path[row["resolved_source_path"]].add(row["resolved_raw_variable"])
    for group in key_groups.values():
        for variable in group.get("variables", []):
            if group.get("resolved_source_path"):
                needed_by_path[group["resolved_source_path"]].add(variable)

    read_cache: dict[str, tuple[pd.DataFrame | None, Any, str]] = {}
    for source_path, columns in sorted(needed_by_path.items()):
        path = Path(source_path)
        read_cache[source_path] = read_table_columns(path, sorted(columns))

    value_rows = fill_value_summaries(value_rows_pending, read_cache)
    key_rows = fill_key_summaries(key_groups, read_cache)
    auto_rows = build_auto_harmonization_value_rows(value_rows)
    summary = build_summary(raw_ready_rows, value_candidates, value_rows, key_rows, auto_rows)

    write_csv(VALUE_AUDIT_PATH, value_rows, VALUE_COLUMNS)
    write_csv(KEY_AUDIT_PATH, key_rows, KEY_COLUMNS)
    write_csv(AUTO_HARMONIZATION_VALUE_AUDIT_PATH, auto_rows, AUTO_VALUE_COLUMNS)
    write_csv(SUMMARY_PATH, summary, SUMMARY_COLUMNS)
    write_report(summary, value_rows, key_rows)
    append_log(
        TEMP_DIR / "audit_log.md",
        f"First-batch raw value/key audit raw_ready={len(raw_ready_rows)} value_rows={len(value_rows)} key_rows={len(key_rows)} auto_value_rows={len(auto_rows)}.",
    )
    print(f"First-batch raw value/key audit raw_ready={len(raw_ready_rows)} value_rows={len(value_rows)} key_rows={len(key_rows)} auto_value_rows={len(auto_rows)}.")


if __name__ == "__main__":
    main()
