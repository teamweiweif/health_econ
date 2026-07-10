from __future__ import annotations

import csv
import os
import tempfile
from collections import Counter, defaultdict
from pathlib import Path, PurePosixPath
from typing import Any
from zipfile import ZipFile

import pandas as pd
import pyreadstat

from common import PROJECT_ROOT, REPORT_DIR, RESULT_DIR, TEMP_DIR, append_log, ensure_dirs, write_csv


RECEIPT_VALIDATION_PATH = TEMP_DIR / "priority_lsms_isa_official_file_receipt_validation.csv"
ARCHIVE_MEMBER_PATH = TEMP_DIR / "priority_lsms_isa_archive_member_manifest.csv"
DIRECT_FILE_PATH = TEMP_DIR / "priority_lsms_isa_direct_file_preflight.csv"
SCHEMA_EVIDENCE_PATH = TEMP_DIR / "priority_lsms_isa_received_raw_requirement_evidence.csv"
VARIABLE_SCHEMA_PATH = TEMP_DIR / "priority_lsms_isa_received_raw_variable_schema.csv"

VALUE_PROFILE_PATH = TEMP_DIR / "priority_lsms_isa_received_raw_value_profile.csv"
KEY_PROFILE_PATH = TEMP_DIR / "priority_lsms_isa_received_raw_key_design_geography_profile.csv"
REQUIREMENT_PROFILE_PATH = TEMP_DIR / "priority_lsms_isa_received_raw_value_requirement_profile.csv"
SUMMARY_PATH = RESULT_DIR / "priority_lsms_isa_received_raw_value_profile_summary.csv"
REPORT_PATH = REPORT_DIR / "priority_lsms_isa_received_raw_value_profile.md"

SPECIAL_CODE_CANDIDATES = {
    -99,
    -98,
    -97,
    -96,
    -9,
    -8,
    -7,
    -1,
    96,
    97,
    98,
    99,
    996,
    997,
    998,
    999,
    9996,
    9997,
    9998,
    9999,
}

UTILITY_VARIABLE_ROLES = {
    "case_id": "household_key",
    "hhid": "household_key_component",
    "hhmemid": "household_head_member_id",
    "psu": "survey_design_psu",
    "strata": "survey_design_strata",
    "hhwght": "survey_design_household_weight",
    "region": "admin_geography_region",
    "dist": "admin_geography_district",
    "add": "admin_geography_ag_development_district",
    "ea": "cluster_or_enumeration_area",
    "type": "urban_rural_ea_type",
    "ta": "admin_geography_traditional_authority",
}

VALUE_PROFILE_COLUMNS = [
    "download_priority_order",
    "queue_role",
    "country",
    "wave",
    "idno",
    "requirement",
    "actual_member_name",
    "variable_name",
    "raw_variable_label",
    "has_value_labels",
    "row_count",
    "nonmissing_count",
    "missing_count",
    "missing_rate",
    "distinct_nonmissing_count",
    "zero_count",
    "negative_count",
    "positive_count",
    "numeric_min",
    "numeric_p01",
    "numeric_p05",
    "numeric_p25",
    "numeric_p50",
    "numeric_p75",
    "numeric_p95",
    "numeric_p99",
    "numeric_max",
    "top_values",
    "possible_missing_codes",
    "detected_recall_period",
    "detected_unit_or_scale",
    "possible_skip_pattern",
    "value_profile_status",
]

KEY_PROFILE_COLUMNS = [
    "download_priority_order",
    "queue_role",
    "country",
    "wave",
    "idno",
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
    "zero_count",
    "negative_count",
    "positive_count",
    "numeric_min",
    "numeric_max",
    "top_values",
    "profile_status",
]

REQUIREMENT_PROFILE_COLUMNS = [
    "download_priority_order",
    "queue_role",
    "country",
    "wave",
    "idno",
    "requirement",
    "candidate_variable_rows",
    "profiled_variable_rows",
    "variables_with_nonmissing_values",
    "variables_with_value_labels",
    "detected_recall_periods",
    "detected_units_or_scales",
    "possible_missing_code_variables",
    "possible_skip_pattern_variables",
    "value_profile_requirement_status",
    "remaining_manual_review",
]

SUMMARY_COLUMNS = ["metric", "value", "interpretation"]


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


def compact(value: Any, limit: int = 220) -> str:
    text = " ".join(clean(value).replace("|", "/").split())
    return text[: limit - 3] + "..." if len(text) > limit else text


def numeric_text(value: Any) -> str:
    if value is None or pd.isna(value):
        return ""
    try:
        return f"{float(value):.6g}"
    except (TypeError, ValueError):
        return compact(value, 60)


def member_key(member_name: str) -> str:
    return PurePosixPath(clean(member_name).replace("\\", "/")).name.lower()


def archive_lookup(member_rows: list[dict[str, str]]) -> dict[tuple[str, str], dict[str, str]]:
    out: dict[tuple[str, str], dict[str, str]] = {}
    for row in member_rows:
        idno = clean(row.get("idno"))
        name = member_key(row.get("member_name", ""))
        if idno and name:
            row["_raw_source_type"] = "archive_member"
            out[(idno, name)] = row
    return out


def direct_lookup(direct_rows: list[dict[str, str]]) -> dict[tuple[str, str], dict[str, str]]:
    out: dict[tuple[str, str], dict[str, str]] = {}
    for row in direct_rows:
        idno = clean(row.get("idno"))
        name = member_key(row.get("file_name", ""))
        if idno and name and name.endswith(".dta"):
            row["_raw_source_type"] = "direct_file"
            row["archive_relative_path"] = clean(row.get("relative_path"))
            row["member_name"] = clean(row.get("file_name"))
            row["member_role"] = clean(row.get("file_role"))
            out[(idno, name)] = row
    return out


def receipt_lookup(rows: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    return {clean(row.get("idno")): row for row in rows if clean(row.get("idno"))}


def read_member(zip_path: Path, member_name: str, columns: list[str] | None = None) -> tuple[pd.DataFrame, Any]:
    with ZipFile(zip_path) as zf:
        payload = zf.read(member_name)
    suffix = PurePosixPath(member_name).suffix or ".tmp"
    fd, raw_name = tempfile.mkstemp(suffix=suffix)
    raw_path = Path(raw_name)
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(payload)
        kwargs: dict[str, Any] = {"apply_value_formats": False}
        if columns is not None:
            kwargs["usecols"] = columns
        df, meta = pyreadstat.read_dta(str(raw_path), **kwargs)
        return df, meta
    finally:
        raw_path.unlink(missing_ok=True)


def read_member_meta(zip_path: Path, member_name: str) -> Any:
    with ZipFile(zip_path) as zf:
        payload = zf.read(member_name)
    suffix = PurePosixPath(member_name).suffix or ".tmp"
    fd, raw_name = tempfile.mkstemp(suffix=suffix)
    raw_path = Path(raw_name)
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(payload)
        _, meta = pyreadstat.read_dta(str(raw_path), metadataonly=True)
        return meta
    finally:
        raw_path.unlink(missing_ok=True)


def raw_source_path(raw_source: dict[str, str]) -> Path:
    return PROJECT_ROOT / clean(raw_source.get("archive_relative_path")).replace("/", "\\")


def read_raw_source(raw_source: dict[str, str], member_name: str, columns: list[str] | None = None) -> tuple[pd.DataFrame, Any]:
    raw_path = raw_source_path(raw_source)
    if clean(raw_source.get("_raw_source_type")) == "direct_file":
        kwargs: dict[str, Any] = {"apply_value_formats": False}
        if columns is not None:
            kwargs["usecols"] = columns
        return pyreadstat.read_dta(str(raw_path), **kwargs)
    return read_member(raw_path, member_name, columns)


def variable_labels(meta: Any) -> dict[str, str]:
    return dict(zip(getattr(meta, "column_names", []) or [], getattr(meta, "column_labels", []) or []))


def value_labels(meta: Any, variable: str) -> dict[Any, str]:
    labels = getattr(meta, "variable_value_labels", {}) or {}
    value_map = labels.get(variable, {})
    return value_map if isinstance(value_map, dict) else {}


def value_label_text(labels: dict[Any, str], value: Any) -> str:
    if value in labels:
        return clean(labels[value])
    try:
        as_float = float(value)
    except (TypeError, ValueError):
        return ""
    for key, label in labels.items():
        try:
            if float(key) == as_float:
                return clean(label)
        except (TypeError, ValueError):
            continue
    return ""


def value_text(value: Any) -> str:
    if value is None or pd.isna(value):
        return ""
    if isinstance(value, pd.Timestamp):
        return value.date().isoformat()
    try:
        as_float = float(value)
        if as_float.is_integer():
            return str(int(as_float))
        return f"{as_float:.6g}"
    except (TypeError, ValueError):
        return compact(value, 80)


def top_values(series: pd.Series, labels: dict[Any, str]) -> str:
    parts: list[str] = []
    for value, count in series.dropna().value_counts(dropna=True).head(10).items():
        label = value_label_text(labels, value)
        token = value_text(value)
        if label:
            token = f"{token}={compact(label, 60)}"
        parts.append(f"{token}:{int(count)}")
    return "; ".join(parts)


def numeric_stats(series: pd.Series) -> dict[str, str]:
    numeric = pd.to_numeric(series, errors="coerce")
    nonmissing = numeric.dropna()
    if nonmissing.empty:
        return {
            "zero_count": "",
            "negative_count": "",
            "positive_count": "",
            "numeric_min": "",
            "numeric_p01": "",
            "numeric_p05": "",
            "numeric_p25": "",
            "numeric_p50": "",
            "numeric_p75": "",
            "numeric_p95": "",
            "numeric_p99": "",
            "numeric_max": "",
        }
    quantiles = nonmissing.quantile([0.01, 0.05, 0.25, 0.50, 0.75, 0.95, 0.99])
    return {
        "zero_count": str(int((nonmissing == 0).sum())),
        "negative_count": str(int((nonmissing < 0).sum())),
        "positive_count": str(int((nonmissing > 0).sum())),
        "numeric_min": numeric_text(nonmissing.min()),
        "numeric_p01": numeric_text(quantiles.loc[0.01]),
        "numeric_p05": numeric_text(quantiles.loc[0.05]),
        "numeric_p25": numeric_text(quantiles.loc[0.25]),
        "numeric_p50": numeric_text(quantiles.loc[0.50]),
        "numeric_p75": numeric_text(quantiles.loc[0.75]),
        "numeric_p95": numeric_text(quantiles.loc[0.95]),
        "numeric_p99": numeric_text(quantiles.loc[0.99]),
        "numeric_max": numeric_text(nonmissing.max()),
    }


def possible_missing_codes(series: pd.Series, labels: dict[Any, str]) -> str:
    numeric = pd.to_numeric(series, errors="coerce").dropna()
    codes = sorted({int(v) for v in numeric.unique() if float(v).is_integer() and int(v) in SPECIAL_CODE_CANDIDATES})
    label_hits: list[str] = []
    for value, label in labels.items():
        low = clean(label).lower()
        if any(token in low for token in ["missing", "refus", "don't know", "dont know", "not applicable", "n/a", "other"]):
            label_hits.append(f"{value_text(value)}={compact(label, 60)}")
    code_bits = [str(code) for code in codes]
    return "; ".join(code_bits + label_hits[:8])


def detect_recall_period(label: str) -> str:
    low = label.lower()
    patterns = [
        ("past_2_weeks", ["past 2 weeks", "past two weeks"]),
        ("past_4_weeks", ["past 4 wks", "past 4 weeks", "past four weeks"]),
        ("past_month", ["past month", "over past month"]),
        ("past_week", ["past one week", "past 1 week", "over the past one week"]),
        ("past_3_days", ["past 3 days", "past three days"]),
        ("past_12_months", ["past 12 months", "past year", "in the past year"]),
        ("calendar_year", ["calendar year", "which year"]),
        ("interview_month", ["month of interview"]),
        ("interview_date", ["interview date"]),
    ]
    found = [name for name, needles in patterns if any(needle in low for needle in needles)]
    return "; ".join(found)


def detect_unit_or_scale(label: str, variable: str) -> str:
    low = f"{label} {variable}".lower()
    hits: list[str] = []
    if any(token in low for token in ["spent", "spend", "cost", "paid", "expenditure", "consumption"]):
        hits.append("local_currency_amount_needs_unit_confirmation")
    if "distance" in low or "how far" in low:
        hits.append("distance_measure_needs_unit_confirmation")
    if "unit" in low:
        hits.append("unit_variable")
    if "month" in low:
        hits.append("month")
    if "year" in low:
        hits.append("year")
    if "weight" in low or variable.lower() == "hhwght":
        hits.append("survey_weight")
    return "; ".join(dict.fromkeys(hits))


def detect_skip_pattern(row_count: int, nonmissing: int, label: str) -> str:
    low = label.lower()
    hints: list[str] = []
    if nonmissing < row_count:
        hints.append("conditional_missingness")
    if any(token in low for token in ["if ", "did you", "have you", "only", "under", "over"]):
        hints.append("questionnaire_skip_likely")
    return "; ".join(hints)


def profile_series(series: pd.Series, labels: dict[Any, str], variable_label: str, variable_name: str) -> dict[str, str]:
    row_count = len(series)
    nonmissing = int(series.notna().sum())
    missing = row_count - nonmissing
    stats = numeric_stats(series)
    missing_rate = (missing / row_count) if row_count else 0
    return {
        "row_count": str(row_count),
        "nonmissing_count": str(nonmissing),
        "missing_count": str(missing),
        "missing_rate": f"{missing_rate:.4f}",
        "distinct_nonmissing_count": str(int(series.dropna().nunique())),
        **stats,
        "top_values": top_values(series, labels),
        "possible_missing_codes": possible_missing_codes(series, labels),
        "detected_recall_period": detect_recall_period(variable_label),
        "detected_unit_or_scale": detect_unit_or_scale(variable_label, variable_name),
        "possible_skip_pattern": detect_skip_pattern(row_count, nonmissing, variable_label),
    }


def value_profile_status(nonmissing: int, possible_missing: str, recall: str, unit: str, skip: str) -> str:
    if nonmissing == 0:
        return "value_profile_no_nonmissing_values"
    if possible_missing or recall or unit or skip:
        return "value_profile_available_needs_semantics_review"
    return "value_profile_available_needs_documentation_review"


def utility_profile_status(variable: str, role: str, row_count: int, nonmissing: int, distinct: int, negative: int) -> str:
    if nonmissing == 0:
        return "utility_variable_no_nonmissing_values"
    if role == "survey_design_household_weight":
        return "weight_positive_candidate" if negative == 0 else "weight_has_negative_values_needs_review"
    if "key" in role:
        return "unique_key_at_file_level" if distinct == row_count else "repeated_key_requires_secondary_line_key"
    if role.startswith("survey_design"):
        return "survey_design_variable_present"
    if "geography" in role or "cluster" in role or "urban_rural" in role:
        return "geography_variable_present_needs_linkage_review"
    return "utility_variable_present"


def build_value_profiles(
    evidence_rows: list[dict[str, str]],
    archives: dict[tuple[str, str], dict[str, str]],
) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    grouped: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in evidence_rows:
        if row.get("raw_variable_present") == "1":
            grouped[(clean(row.get("idno")), member_key(row.get("actual_member_name", "")))].append(row)

    for (idno, member), candidates in sorted(grouped.items()):
        archive_row = archives.get((idno, member), {})
        archive_path = raw_source_path(archive_row)
        member_name = clean(archive_row.get("member_name")) or candidates[0].get("actual_member_name", "")
        variables = sorted({clean(row.get("variable_name")) for row in candidates if clean(row.get("variable_name"))})
        if not archive_path.exists() or not variables:
            continue
        df, meta = read_raw_source(archive_row, member_name, variables)
        labels_by_variable = variable_labels(meta)
        for candidate in candidates:
            variable = clean(candidate.get("variable_name"))
            if variable not in df.columns:
                continue
            variable_label = clean(labels_by_variable.get(variable)) or clean(candidate.get("raw_variable_label"))
            labels = value_labels(meta, variable)
            profile = profile_series(df[variable], labels, variable_label, variable)
            nonmissing = safe_int(profile["nonmissing_count"])
            status = value_profile_status(
                nonmissing,
                profile["possible_missing_codes"],
                profile["detected_recall_period"],
                profile["detected_unit_or_scale"],
                profile["possible_skip_pattern"],
            )
            rows.append(
                {
                    "download_priority_order": clean(candidate.get("download_priority_order")),
                    "queue_role": clean(candidate.get("queue_role")),
                    "country": clean(candidate.get("country")),
                    "wave": clean(candidate.get("wave")),
                    "idno": idno,
                    "requirement": clean(candidate.get("requirement")),
                    "actual_member_name": member_name,
                    "variable_name": variable,
                    "raw_variable_label": variable_label,
                    "has_value_labels": "1" if labels else "0",
                    **profile,
                    "value_profile_status": status,
                }
            )
    return rows


def build_key_profiles(
    schema_rows: list[dict[str, str]],
    archives: dict[tuple[str, str], dict[str, str]],
) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    by_member: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in schema_rows:
        variable = clean(row.get("variable_name")).lower()
        if variable in UTILITY_VARIABLE_ROLES:
            by_member[(clean(row.get("idno")), member_key(row.get("member_name", "")))].append(row)

    for (idno, member), variables_rows in sorted(by_member.items()):
        archive_row = archives.get((idno, member), {})
        archive_path = raw_source_path(archive_row)
        member_name = clean(archive_row.get("member_name")) or clean(variables_rows[0].get("member_name"))
        variables = sorted({clean(row.get("variable_name")) for row in variables_rows})
        if not archive_path.exists() or not variables:
            continue
        df, meta = read_raw_source(archive_row, member_name, variables)
        labels_by_variable = variable_labels(meta)
        for variable in variables:
            if variable not in df.columns:
                continue
            variable_label = clean(labels_by_variable.get(variable))
            labels = value_labels(meta, variable)
            profile = profile_series(df[variable], labels, variable_label, variable)
            row_count = safe_int(profile["row_count"])
            nonmissing = safe_int(profile["nonmissing_count"])
            distinct = safe_int(profile["distinct_nonmissing_count"])
            negative = safe_int(profile["negative_count"])
            duplicate_if_key = max(nonmissing - distinct, 0)
            role = UTILITY_VARIABLE_ROLES.get(variable.lower(), "utility_variable")
            rows.append(
                {
                    "download_priority_order": clean(archive_row.get("download_priority_order")),
                    "queue_role": "",
                    "country": clean(archive_row.get("country")),
                    "wave": clean(archive_row.get("wave")),
                    "idno": idno,
                    "actual_member_name": member_name,
                    "variable_name": variable,
                    "variable_role": role,
                    "raw_variable_label": variable_label,
                    "has_value_labels": "1" if labels else "0",
                    "row_count": profile["row_count"],
                    "nonmissing_count": profile["nonmissing_count"],
                    "missing_count": profile["missing_count"],
                    "distinct_nonmissing_count": profile["distinct_nonmissing_count"],
                    "duplicate_if_key_count": str(duplicate_if_key) if "key" in role else "",
                    "zero_count": profile["zero_count"],
                    "negative_count": profile["negative_count"],
                    "positive_count": profile["positive_count"],
                    "numeric_min": profile["numeric_min"],
                    "numeric_max": profile["numeric_max"],
                    "top_values": profile["top_values"],
                    "profile_status": utility_profile_status(variable, role, row_count, nonmissing, distinct, negative),
                }
            )
    return rows


def build_requirement_profiles(
    evidence_rows: list[dict[str, str]],
    value_rows: list[dict[str, str]],
    receipt_by_id: dict[str, dict[str, str]],
) -> list[dict[str, str]]:
    candidates = Counter((clean(row.get("idno")), clean(row.get("requirement"))) for row in evidence_rows if row.get("raw_variable_present") == "1")
    grouped: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in value_rows:
        grouped[(clean(row.get("idno")), clean(row.get("requirement")))].append(row)

    rows: list[dict[str, str]] = []
    for key in sorted(set(candidates) | set(grouped)):
        idno, requirement = key
        profiles = grouped.get(key, [])
        receipt = receipt_by_id.get(idno, {})
        with_nonmissing = sum(1 for row in profiles if safe_int(row.get("nonmissing_count")) > 0)
        with_labels = sum(1 for row in profiles if row.get("has_value_labels") == "1")
        recall = sorted({clean(row.get("detected_recall_period")) for row in profiles if clean(row.get("detected_recall_period"))})
        units = sorted({clean(row.get("detected_unit_or_scale")) for row in profiles if clean(row.get("detected_unit_or_scale"))})
        missing_code_vars = sorted({row.get("variable_name", "") for row in profiles if clean(row.get("possible_missing_codes"))})
        skip_vars = sorted({row.get("variable_name", "") for row in profiles if clean(row.get("possible_skip_pattern"))})
        status = "value_profile_available_not_value_verified" if profiles else "blocked_no_value_profile"
        rows.append(
            {
                "download_priority_order": clean(receipt.get("download_priority_order")),
                "queue_role": clean(receipt.get("queue_role")),
                "country": clean(receipt.get("country")),
                "wave": clean(receipt.get("wave")),
                "idno": idno,
                "requirement": requirement,
                "candidate_variable_rows": str(candidates.get(key, 0)),
                "profiled_variable_rows": str(len(profiles)),
                "variables_with_nonmissing_values": str(with_nonmissing),
                "variables_with_value_labels": str(with_labels),
                "detected_recall_periods": "; ".join(recall),
                "detected_units_or_scales": "; ".join(units),
                "possible_missing_code_variables": "; ".join(missing_code_vars),
                "possible_skip_pattern_variables": "; ".join(skip_vars),
                "value_profile_requirement_status": status,
                "remaining_manual_review": "review questionnaire/codebook for units, recall periods, skip patterns, missing codes, accepted merge level, and outcome construction before promotion",
            }
        )
    return rows


def summarize(value_rows: list[dict[str, str]], key_rows: list[dict[str, str]], requirement_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    dataset_ids = {row.get("idno", "") for row in value_rows + key_rows if row.get("idno")}
    status_counts = Counter(row.get("value_profile_status", "") for row in value_rows)
    requirement_counts = Counter(row.get("value_profile_requirement_status", "") for row in requirement_rows)
    role_counts = Counter(row.get("variable_role", "") for row in key_rows)
    rows = [
        {"metric": "priority_lsms_received_raw_value_profile_dataset_rows", "value": str(len(dataset_ids)), "interpretation": "Datasets with received raw value-profile evidence."},
        {"metric": "priority_lsms_received_raw_value_profile_variable_rows", "value": str(len(value_rows)), "interpretation": "Candidate requirement variable rows with value-profile evidence."},
        {"metric": "priority_lsms_received_raw_value_profile_nonmissing_variable_rows", "value": str(sum(1 for row in value_rows if safe_int(row.get("nonmissing_count")) > 0)), "interpretation": "Candidate variables with at least one nonmissing raw value."},
        {"metric": "priority_lsms_received_raw_value_profile_value_label_rows", "value": str(sum(1 for row in value_rows if row.get("has_value_labels") == "1")), "interpretation": "Candidate variables with raw value-label metadata."},
        {"metric": "priority_lsms_received_raw_key_design_geography_profile_rows", "value": str(len(key_rows)), "interpretation": "Utility key, design, and geography variables profiled from received raw files."},
        {"metric": "priority_lsms_received_raw_value_requirement_profile_rows", "value": str(len(requirement_rows)), "interpretation": "Requirement-level value-profile summary rows."},
        {"metric": "priority_lsms_received_raw_value_profile_requirements_with_profiles", "value": str(sum(1 for row in requirement_rows if row.get("value_profile_requirement_status") == "value_profile_available_not_value_verified")), "interpretation": "Requirements with value-profile evidence available for manual review."},
        {"metric": "priority_lsms_received_raw_value_profile_raw_value_verified_rows", "value": "0", "interpretation": "No rows are value-verified until reviewer acceptance fields and documentation checks pass."},
        {"metric": "priority_lsms_received_raw_value_profile_data_write_status", "value": "blocked_value_profile_only", "interpretation": "Value-profile evidence does not write promoted analysis data."},
        {"metric": "modeling_gate_status", "value": "blocked", "interpretation": "Models remain blocked until promoted registry thresholds and climate linkage pass."},
    ]
    for status, count in sorted(status_counts.items()):
        rows.append({"metric": f"priority_lsms_received_raw_value_profile_status_{status}", "value": str(count), "interpretation": "Candidate variable value-profile status count."})
    for status, count in sorted(requirement_counts.items()):
        rows.append({"metric": f"priority_lsms_received_raw_value_requirement_status_{status}", "value": str(count), "interpretation": "Requirement value-profile status count."})
    for role, count in sorted(role_counts.items()):
        rows.append({"metric": f"priority_lsms_received_raw_key_design_geography_role_{role}", "value": str(count), "interpretation": "Utility key/design/geography variable role count."})
    return rows


def markdown_table(rows: list[dict[str, str]], columns: list[str], limit: int = 30) -> str:
    lines = ["| " + " | ".join(columns) + " |", "|" + "|".join("---" for _ in columns) + "|"]
    for row in rows[:limit]:
        lines.append("| " + " | ".join(compact(row.get(column), 100) for column in columns) + " |")
    return "\n".join(lines)


def write_handoffs(receipt_by_id: dict[str, dict[str, str]], requirement_rows: list[dict[str, str]], key_rows: list[dict[str, str]]) -> int:
    written = 0
    for idno, receipt in sorted(receipt_by_id.items()):
        reqs = [row for row in requirement_rows if row.get("idno") == idno]
        keys = [row for row in key_rows if row.get("idno") == idno]
        if not reqs and not keys:
            continue
        folder = PROJECT_ROOT / clean(receipt.get("local_target_folder")).replace("/", "\\")
        folder.mkdir(parents=True, exist_ok=True)
        path = folder / "_PRIORITY_LSMS_ISA_RECEIVED_RAW_VALUE_PROFILE.md"
        path.write_text(
            f"""# Priority LSMS-ISA Received Raw Value Profile

IDNO: `{idno}`

Country-wave: {receipt.get('country', '')} {receipt.get('wave', '')}

Status: value-distribution, key/design, and geography prefill evidence is
available for manual raw-value review. This file does not certify promotion.

## Requirement Profile

{markdown_table(reqs, ['requirement', 'profiled_variable_rows', 'variables_with_nonmissing_values', 'detected_recall_periods', 'detected_units_or_scales', 'value_profile_requirement_status'], 20)}

## Key / Design / Geography Profile

{markdown_table(keys, ['actual_member_name', 'variable_name', 'variable_role', 'nonmissing_count', 'distinct_nonmissing_count', 'profile_status'], 80)}

## Remaining Gate Meaning

This profile can prefill review, but the country-wave remains unpromoted until
documentation confirms units, recall periods, missing codes, skip universes,
merge levels, outcome formulas, and an accepted CHIRPS/ERA5 linkage route.
""",
            encoding="utf-8",
        )
        written += 1
    return written


def write_report(
    value_rows: list[dict[str, str]],
    key_rows: list[dict[str, str]],
    requirement_rows: list[dict[str, str]],
    summary_rows: list[dict[str, str]],
) -> None:
    summary_table = "\n".join(f"| {row['metric']} | {row['value']} | {row['interpretation']} |" for row in summary_rows)
    report = f"""# Priority LSMS-ISA Received Raw Value Profile

Status: metadata-only value-distribution and key/design/geography prefill for
received raw archives. No raw microdata are persisted and no dataset is
promoted by this audit.

## Summary

| metric | value | interpretation |
|---|---:|---|
{summary_table}

## Requirement-Level Profile

{markdown_table(requirement_rows, ['country', 'wave', 'idno', 'requirement', 'candidate_variable_rows', 'profiled_variable_rows', 'variables_with_nonmissing_values', 'detected_recall_periods', 'detected_units_or_scales', 'value_profile_requirement_status'], 40)}

## Selected Candidate Value Profiles

{markdown_table(value_rows, ['requirement', 'actual_member_name', 'variable_name', 'raw_variable_label', 'nonmissing_count', 'distinct_nonmissing_count', 'numeric_min', 'numeric_max', 'detected_recall_period', 'detected_unit_or_scale', 'value_profile_status'], 60)}

## Selected Key / Design / Geography Profiles

{markdown_table(key_rows, ['actual_member_name', 'variable_name', 'variable_role', 'nonmissing_count', 'distinct_nonmissing_count', 'numeric_min', 'numeric_max', 'profile_status'], 80)}

## Interpretation

The audit advances received raw packages from schema presence to value-profile
review evidence. It is still not raw-value verification. Promotion remains
blocked until reviewer acceptance, documentation cross-checks, harmonized
outcome construction, and climate linkage pass.
"""
    REPORT_PATH.write_text(report, encoding="utf-8")


def main() -> None:
    ensure_dirs()
    evidence_rows = read_csv_dicts(SCHEMA_EVIDENCE_PATH)
    schema_rows = read_csv_dicts(VARIABLE_SCHEMA_PATH)
    archives = archive_lookup(read_csv_dicts(ARCHIVE_MEMBER_PATH))
    archives.update(direct_lookup(read_csv_dicts(DIRECT_FILE_PATH)))
    receipts = receipt_lookup(read_csv_dicts(RECEIPT_VALIDATION_PATH))

    value_rows = build_value_profiles(evidence_rows, archives)
    key_rows = build_key_profiles(schema_rows, archives)
    requirement_rows = build_requirement_profiles(evidence_rows, value_rows, receipts)
    handoff_count = write_handoffs(receipts, requirement_rows, key_rows)
    summary_rows = summarize(value_rows, key_rows, requirement_rows)
    summary_rows.append({"metric": "priority_lsms_received_raw_value_profile_handoff_readmes_written", "value": str(handoff_count), "interpretation": "Per-dataset received raw value-profile handoffs written."})

    write_csv(VALUE_PROFILE_PATH, value_rows, VALUE_PROFILE_COLUMNS)
    write_csv(KEY_PROFILE_PATH, key_rows, KEY_PROFILE_COLUMNS)
    write_csv(REQUIREMENT_PROFILE_PATH, requirement_rows, REQUIREMENT_PROFILE_COLUMNS)
    write_csv(SUMMARY_PATH, summary_rows, SUMMARY_COLUMNS)
    write_report(value_rows, key_rows, requirement_rows, summary_rows)
    append_log(
        TEMP_DIR / "audit_log.md",
        f"Built priority LSMS/ISA received raw value profile variables={len(value_rows)} key_design_geo_rows={len(key_rows)} requirements={len(requirement_rows)}.",
    )
    print(
        "Priority LSMS/ISA received raw value profile "
        f"variables={len(value_rows)} key_design_geo_rows={len(key_rows)} requirements={len(requirement_rows)}."
    )


if __name__ == "__main__":
    main()
