from __future__ import annotations

import math
import warnings
from pathlib import Path
from typing import Any

import pandas as pd

from common import REPORT_DIR, RESULT_DIR, TEMP_DIR, append_log, ensure_dirs, write_csv

try:
    import pyreadstat
except ImportError:  # pragma: no cover - validation reports this elsewhere.
    pyreadstat = None


IDNO = "ALB_2005_LSMS_v01_M"
COUNTRY = "Albania"
SURVEY_NAME = "Living Standards Measurement Survey 2005"
WAVE = "2005"
RAW_ROOT = TEMP_DIR / "raw_extracted" / "lsms2005en_1e7f1965c4a5" / "lsms2005en" / "Data_2005"

AUDIT_PATH = TEMP_DIR / "alb2005_timing_geography_exhaustive_audit.csv"
SUMMARY_PATH = RESULT_DIR / "alb2005_timing_geography_exhaustive_summary.csv"
REPORT_PATH = REPORT_DIR / "alb2005_timing_geography_exhaustive_audit.md"

AUDIT_COLUMNS = [
    "country",
    "survey_name",
    "wave",
    "idno",
    "source_file",
    "variable_name",
    "variable_label",
    "candidate_role",
    "candidate_reason",
    "row_count",
    "nonmissing_rows",
    "nonmissing_rate",
    "distinct_values",
    "min_value",
    "max_value",
    "top_values",
    "value_label_examples",
    "merge_key_observed",
    "household_base_match_rows",
    "household_base_match_rate",
    "geography_timing_status",
    "promotion_status",
    "blocking_reason",
]
SUMMARY_COLUMNS = ["metric", "value", "interpretation"]

DECISION = "blocked_missing_interview_timing_partial_geography_no_gps"
NO_PROMOTION = "not_ready_for_climate_linkage"

GEOGRAPHY_TERMS = [
    "district",
    "region",
    "prefecture",
    "prefekt",
    "commune",
    "municipality",
    "village",
    "city",
    "urban",
    "rural",
    "gps",
    "latitude",
    "longitude",
    "coordinate",
    "cluster",
    "psu",
]
TIMING_TERMS = [
    "interview",
    "fieldwork",
    "survey date",
    "survey month",
    "visit",
    "date",
    "month",
    "year",
    "day",
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
    return str(value)


def key_part(value: Any) -> str:
    if value is None:
        return ""
    try:
        if pd.isna(value):
            return ""
    except TypeError:
        pass
    try:
        number = float(value)
        if math.isfinite(number) and number.is_integer():
            return str(int(number))
    except (TypeError, ValueError):
        pass
    return str(value).strip()


def compact_join(values: list[str], limit: int = 10) -> str:
    clean: list[str] = []
    seen: set[str] = set()
    for value in values:
        value = str(value).replace("\n", " ").strip()
        if not value or value in seen:
            continue
        clean.append(value)
        seen.add(value)
        if len(clean) >= limit:
            break
    return "; ".join(clean)


def read_sav(path: Path, usecols: list[str] | None = None, metadataonly: bool = False) -> tuple[pd.DataFrame, Any]:
    if pyreadstat is None:
        raise RuntimeError("pyreadstat is not available")
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        return pyreadstat.read_sav(
            str(path),
            usecols=usecols,
            metadataonly=metadataonly,
            apply_value_formats=False,
        )


def label_map(meta: Any) -> dict[str, str]:
    labels = meta.column_labels or [""] * len(meta.column_names)
    return dict(zip(meta.column_names, labels))


def candidate_hit(name: str, label: str) -> bool:
    blob = f"{name} {label}".lower()
    return any(term in blob for term in GEOGRAPHY_TERMS + TIMING_TERMS)


def classify_candidate(source_file: str, variable_name: str, label: str) -> tuple[str, str, str, str]:
    name = variable_name.lower()
    lab = (label or "").lower()
    blob = f"{name} {lab}"

    if source_file == "filters.sav" and variable_name in {"P11_Q5A", "P11_Q5B"}:
        return (
            "partial_current_district_candidate",
            "current household district variable in filters.sav",
            "partial_household_geography_candidate",
            "district coverage is partial and no GPS/coordinate linkage is present",
        )
    if name in {"psu", "m0_q00", "p0_q00", "psu_key"} or lab.strip() == "psu":
        return (
            "psu_cluster_key",
            "PSU/cluster-like key, not a coordinate or admin code",
            "cluster_key_no_coordinate",
            "PSU may support merges but cannot support climate linkage without coordinates or admin crosswalk",
        )
    if any(term in blob for term in ["gps", "latitude", "longitude", "coordinate"]):
        return (
            "coordinate_candidate",
            "coordinate-like label/name",
            "coordinate_candidate_requires_verification",
            "coordinate-like fields require value and displacement verification before climate linkage",
        )
    if "date of birth" in lab or "birth" in lab:
        return (
            "not_survey_timing_birth_date",
            "birth or fertility timing, not interview fieldwork timing",
            "rejected_not_interview_timing",
            "birth/fertility timing cannot define pre-interview climate exposure windows",
        )
    if any(term in blob for term in ["migrat", "moved", "abroad", "residen", "living in 1990", "born"]):
        return (
            "not_current_location_migration_history",
            "migration or historical residence timing/geography",
            "rejected_not_current_household_geography_or_timing",
            "migration history cannot substitute for current survey location and interview timing",
        )
    if any(term in blob for term in ["past 4 weeks", "past month", "past 30 days", "past 12 months", "last 6 months", "recall"]):
        return (
            "not_survey_timing_recall_period",
            "recall-period wording, not interview date/month",
            "rejected_not_interview_timing",
            "recall windows do not identify calendar month/date for climate exposure",
        )
    if any(term in blob for term in ["amount per month", "monthly", "months covered", "number of months", "months of process", "months suffering", "months breastfed"]):
        return (
            "not_survey_timing_duration_or_payment_period",
            "duration or payment-period wording, not fieldwork timing",
            "rejected_not_interview_timing",
            "durations/payment periods do not identify interview calendar timing",
        )
    if any(term in blob for term in ["started", "began", "job", "assistance", "inhabit this dwelling", "year of acquisition"]):
        return (
            "not_survey_timing_event_history",
            "event history timing, not interview fieldwork timing",
            "rejected_not_interview_timing",
            "event history variables cannot define survey month/date",
        )
    if any(term in blob for term in ["district", "city", "municipality", "commune", "village", "urban", "rural", "region"]):
        return (
            "geography_candidate_requires_context",
            "geography-like field requiring current-location and coverage review",
            "candidate_context_review_required",
            "geography-like variables need module context, coverage, and current-location validation before use",
        )
    if any(term in blob for term in ["interview", "fieldwork", "survey date", "survey month"]):
        return (
            "survey_timing_candidate_requires_context",
            "interview/fieldwork wording found",
            "candidate_context_review_required",
            "candidate requires raw value, calendar, and documentation verification",
        )
    if any(term in blob for term in ["visit"]):
        return (
            "not_survey_timing_visit_count",
            "visit wording appears to describe module visits or care visits",
            "rejected_not_interview_timing",
            "visit variables do not establish household interview date/month",
        )
    return (
        "timing_or_geography_keyword_review",
        "timing/geography keyword found but context is ambiguous",
        "candidate_context_review_required",
        "manual context review required before any climate-linkage use",
    )


def value_examples(meta: Any, variable_name: str) -> str:
    labels = getattr(meta, "variable_value_labels", {}) or {}
    value_map = labels.get(variable_name, {}) or {}
    examples = [f"{fmt(key)}={fmt(value)}" for key, value in list(value_map.items())[:10]]
    return compact_join(examples, 10)


def top_values(series: pd.Series) -> str:
    counts = series.dropna().map(fmt).value_counts().head(10)
    return compact_join([f"{idx}:{count}" for idx, count in counts.items()], 10)


def numeric_min_max(series: pd.Series) -> tuple[str, str]:
    numeric = pd.to_numeric(series, errors="coerce").dropna()
    if numeric.empty:
        return "", ""
    return fmt(float(numeric.min())), fmt(float(numeric.max()))


def build_base_keys() -> tuple[set[str], set[str], set[str]]:
    base_path = RAW_ROOT / "filters_cl.sav"
    base, _ = read_sav(base_path, ["M0_Q00", "M0_Q01", "HHID"])
    psu = base["M0_Q00"].map(key_part)
    hh = base["M0_Q01"].map(key_part)
    hhid = base["HHID"].map(key_part)
    psu_hh = psu + "-" + hh
    return set(hhid[hhid != ""]), set(psu_hh[psu_hh != "-"]), set(psu[psu != ""])


def merge_key_match(df: pd.DataFrame, base_hhid: set[str], base_psu_hh: set[str], base_psu: set[str]) -> tuple[str, int, str]:
    cols = {col.lower(): col for col in df.columns}
    if "hhid" in cols:
        keys = set(df[cols["hhid"]].map(key_part))
        keys.discard("")
        matched = len(keys.intersection(base_hhid))
        rate = matched / len(base_hhid) if base_hhid else 0
        return "hhid", matched, fmt(rate)
    pair_options = [("psu", "hh"), ("p0_q00", "p0_q01"), ("m0_q00", "m0_q01")]
    for psu_col, hh_col in pair_options:
        if psu_col in cols and hh_col in cols:
            psu = df[cols[psu_col]].map(key_part)
            hh = df[cols[hh_col]].map(key_part)
            keys = set(psu + "-" + hh)
            keys.discard("-")
            matched = len(keys.intersection(base_psu_hh))
            rate = matched / len(base_psu_hh) if base_psu_hh else 0
            return f"{cols[psu_col]}+{cols[hh_col]}", matched, fmt(rate)
    for psu_col in ["psu", "p0_q00", "m0_q00"]:
        if psu_col in cols:
            keys = set(df[cols[psu_col]].map(key_part))
            keys.discard("")
            matched = len(keys.intersection(base_psu))
            rate = matched / len(base_psu) if base_psu else 0
            return cols[psu_col], matched, fmt(rate)
    return "", 0, ""


def merge_key_columns(column_names: list[str]) -> list[str]:
    key_names = {"hhid", "psu", "hh", "p0_q00", "p0_q01", "m0_q00", "m0_q01"}
    return [name for name in column_names if name.lower() in key_names]


def build_audit() -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    if not RAW_ROOT.exists():
        raise FileNotFoundError(f"Missing ALB_2005 raw directory: {RAW_ROOT}")
    base_hhid, base_psu_hh, base_psu = build_base_keys()
    rows: list[dict[str, str]] = []
    source_files = sorted(RAW_ROOT.glob("*.sav"))
    read_failures = 0

    for path in source_files:
        try:
            _, meta = read_sav(path, metadataonly=True)
        except Exception as exc:  # pragma: no cover - audit records unusual raw failures.
            read_failures += 1
            rows.append(
                {
                    "country": COUNTRY,
                    "survey_name": SURVEY_NAME,
                    "wave": WAVE,
                    "idno": IDNO,
                    "source_file": path.name,
                    "geography_timing_status": "read_failed",
                    "promotion_status": NO_PROMOTION,
                    "blocking_reason": str(exc),
                }
            )
            continue

        labels = label_map(meta)
        candidate_cols = [name for name in meta.column_names if candidate_hit(name, labels.get(name, ""))]
        if not candidate_cols:
            continue
        key_cols = merge_key_columns(meta.column_names)
        read_cols = list(dict.fromkeys(candidate_cols + key_cols))
        df, meta_with_data = read_sav(path, usecols=read_cols)
        key_df = df[key_cols].copy() if key_cols else pd.DataFrame(index=df.index)
        merge_key, matched_rows, match_rate = merge_key_match(key_df, base_hhid, base_psu_hh, base_psu)
        row_count = len(df)

        for variable_name in candidate_cols:
            label = labels.get(variable_name, "")
            role, reason, status, blocker = classify_candidate(path.name, variable_name, label)
            series = df[variable_name] if variable_name in df.columns else pd.Series(dtype=object)
            nonmissing = int(series.notna().sum())
            distinct = int(series.dropna().nunique()) if nonmissing else 0
            min_value, max_value = numeric_min_max(series)
            rows.append(
                {
                    "country": COUNTRY,
                    "survey_name": SURVEY_NAME,
                    "wave": WAVE,
                    "idno": IDNO,
                    "source_file": path.name,
                    "variable_name": variable_name,
                    "variable_label": label,
                    "candidate_role": role,
                    "candidate_reason": reason,
                    "row_count": str(row_count),
                    "nonmissing_rows": str(nonmissing),
                    "nonmissing_rate": fmt(nonmissing / row_count if row_count else 0),
                    "distinct_values": str(distinct),
                    "min_value": min_value,
                    "max_value": max_value,
                    "top_values": top_values(series),
                    "value_label_examples": value_examples(meta_with_data, variable_name),
                    "merge_key_observed": merge_key,
                    "household_base_match_rows": str(matched_rows),
                    "household_base_match_rate": match_rate,
                    "geography_timing_status": status,
                    "promotion_status": NO_PROMOTION,
                    "blocking_reason": blocker,
                }
            )

    summary = build_summary(rows, len(source_files), read_failures)
    return rows, summary


def summary_row(metric: str, value: Any, interpretation: str) -> dict[str, str]:
    return {"metric": metric, "value": fmt(value), "interpretation": interpretation}


def count_role(rows: list[dict[str, str]], role: str) -> int:
    return sum(1 for row in rows if row.get("candidate_role") == role)


def build_summary(rows: list[dict[str, str]], source_file_count: int, read_failures: int) -> list[dict[str, str]]:
    partial_district = [
        row
        for row in rows
        if row.get("candidate_role") == "partial_current_district_candidate"
    ]
    partial_district_name = [
        row
        for row in rows
        if row.get("source_file") == "filters.sav" and row.get("variable_name") == "P11_Q5A"
    ]
    partial_district_code = [
        row
        for row in rows
        if row.get("source_file") == "filters.sav" and row.get("variable_name") == "P11_Q5B"
    ]
    partial_district_name_nonmissing = int(partial_district_name[0]["nonmissing_rows"]) if partial_district_name else 0
    partial_district_code_nonmissing = int(partial_district_code[0]["nonmissing_rows"]) if partial_district_code else 0
    coordinate_rows = sum(1 for row in rows if row.get("candidate_role") == "coordinate_candidate")
    survey_timing_candidates = sum(1 for row in rows if row.get("candidate_role") == "survey_timing_candidate_requires_context")
    rejected_timing = sum(1 for row in rows if row.get("geography_timing_status") == "rejected_not_interview_timing")
    rejected_history = sum(1 for row in rows if row.get("geography_timing_status") == "rejected_not_current_household_geography_or_timing")
    psu_rows = count_role(rows, "psu_cluster_key")
    return [
        summary_row("alb2005_timing_geography_audit_rows", len(rows), "Timing/geography keyword rows scanned from ALB_2005 raw files."),
        summary_row("alb2005_timing_geography_source_files_scanned", source_file_count, "ALB_2005 .sav files scanned."),
        summary_row("alb2005_timing_geography_read_failures", read_failures, "Raw files that could not be read by pyreadstat."),
        summary_row("alb2005_interview_timing_candidate_rows", survey_timing_candidates, "Rows with apparent interview/fieldwork timing wording requiring context."),
        summary_row("alb2005_interview_timing_verified_rows", 0, "Verified household interview month/date rows available for climate linkage."),
        summary_row("alb2005_rejected_non_interview_timing_rows", rejected_timing, "Rows rejected as birth, recall, duration, payment-period, or event-history timing."),
        summary_row("alb2005_rejected_migration_history_rows", rejected_history, "Rows rejected as migration or historical residence geography/timing."),
        summary_row("alb2005_psu_cluster_key_rows", psu_rows, "PSU/cluster-like key rows observed."),
        summary_row("alb2005_coordinate_candidate_rows", coordinate_rows, "GPS/latitude/longitude/coordinate candidate rows observed."),
        summary_row("alb2005_partial_current_district_candidate_rows", len(partial_district), "Rows for current household district name/code candidates in filters.sav."),
        summary_row("alb2005_partial_district_name_nonmissing_rows", partial_district_name_nonmissing, "Nonmissing rows for P11_Q5A district name in filters.sav."),
        summary_row("alb2005_partial_district_code_nonmissing_rows", partial_district_code_nonmissing, "Nonmissing rows for P11_Q5B district code in filters.sav."),
        summary_row("alb2005_geography_verified_full_coverage_rows", 0, "Verified full-coverage geography rows ready for climate linkage."),
        summary_row("alb2005_climate_linkage_ready_rows", 0, "Rows ready to support climate linkage input construction."),
        summary_row("alb2005_timing_geography_current_decision", DECISION, "Current ALB_2005 timing/geography decision."),
    ]


def markdown_rows(rows: list[dict[str, str]], columns: list[str], limit: int = 30) -> str:
    lines = ["| " + " | ".join(columns) + " |", "|" + "|".join("---" for _ in columns) + "|"]
    for row in rows[:limit]:
        values = []
        for column in columns:
            value = (row.get(column, "") or "").replace("|", "/")
            if len(value) > 100:
                value = value[:97] + "..."
            values.append(value)
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines)


def write_report(rows: list[dict[str, str]], summary: list[dict[str, str]]) -> None:
    summary_table = "\n".join(f"| {row['metric']} | {row['value']} | {row['interpretation']} |" for row in summary)
    priority_rows = [
        row
        for row in rows
        if row.get("candidate_role")
        in {
            "partial_current_district_candidate",
            "coordinate_candidate",
            "survey_timing_candidate_requires_context",
            "psu_cluster_key",
        }
    ]
    rejected_rows = [
        row
        for row in rows
        if row.get("geography_timing_status", "").startswith("rejected_")
    ]
    REPORT_PATH.write_text(
        f"""# ALB_2005 Timing And Geography Exhaustive Audit

Status: raw-value timing/geography audit only. This report scans ALB_2005 raw SPSS files for timing and geography keyword hits and classifies whether they can support climate linkage. It does not construct climate exposures and does not write any file to `data/`.

## Summary

| Metric | Value | Interpretation |
|---|---:|---|
{summary_table}

## Priority Candidate Rows

{markdown_rows(priority_rows, ['source_file', 'variable_name', 'variable_label', 'candidate_role', 'nonmissing_rows', 'household_base_match_rows', 'geography_timing_status'], 40) if priority_rows else 'No priority timing/geography candidates were found.'}

## Rejected Timing/Geography Keyword Rows

{markdown_rows(rejected_rows, ['source_file', 'variable_name', 'variable_label', 'candidate_role', 'nonmissing_rows', 'geography_timing_status'], 40) if rejected_rows else 'No rejected timing/geography keyword rows were found.'}

## Interpretation

- No verified household interview month/date variable was found, so pre-interview 1, 3, 6, or 12 month climate windows remain blocked.
- `P11_Q5B` in `filters.sav` is the main current district-code candidate, but it is partial coverage only and has no GPS or coordinate information.
- PSU variables are merge/cluster keys, not climate locations, unless an official PSU-coordinate or admin crosswalk is obtained.
- Many date/month/year hits are birth dates, migration history, event history, illness durations, payment periods, or recall windows. They cannot substitute for survey fieldwork timing.
- ALB_2005 remains unusable for climate linkage until fieldwork timing and valid geography are documented.

## Machine-Readable Outputs

- `temp/alb2005_timing_geography_exhaustive_audit.csv`
- `result/alb2005_timing_geography_exhaustive_summary.csv`
""",
        encoding="utf-8",
    )


def main() -> None:
    ensure_dirs()
    rows, summary = build_audit()
    write_csv(AUDIT_PATH, rows, AUDIT_COLUMNS)
    write_csv(SUMMARY_PATH, summary, SUMMARY_COLUMNS)
    write_report(rows, summary)
    append_log(TEMP_DIR / "audit_log.md", f"Built ALB_2005 timing/geography exhaustive audit rows={len(rows)} decision={DECISION}.")
    print(f"ALB_2005 timing/geography exhaustive audit rows={len(rows)} decision={DECISION}.")


if __name__ == "__main__":
    main()
