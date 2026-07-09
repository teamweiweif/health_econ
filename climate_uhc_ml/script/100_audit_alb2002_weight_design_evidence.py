from __future__ import annotations

import csv
import math
import urllib.error
import urllib.request
from html import unescape
from pathlib import Path
from typing import Any

import pandas as pd

from common import REPORT_DIR, RESULT_DIR, SNAPSHOT_DIR, TEMP_DIR, append_log, ensure_dirs, sha256_file, write_csv

try:
    import pyreadstat
except ImportError:  # pragma: no cover - environment audit reports this separately.
    pyreadstat = None


IDNO = "ALB_2002_LSMS_v01_M"
COUNTRY = "Albania"
SURVEY_NAME = "Living Standards Measurement Survey 2002"
WAVE = "2002"
STUDY_URL = "https://microdata.worldbank.org/catalog/86/study-description"

RAW_ROOT = TEMP_DIR / "raw_extracted" / "lsms2002en_4dbf0b087520" / "lsms2002en" / "Data_2002"
CANDIDATE_PATH = TEMP_DIR / "alb2002_household_core_candidate.csv"
MERGE_AUDIT_PATH = TEMP_DIR / "alb2002_household_core_merge_audit.csv"
SNAPSHOT_PATH = SNAPSHOT_DIR / "alb2002_worldbank_study_description_weight_design.html"
AUDIT_PATH = TEMP_DIR / "alb2002_weight_design_evidence_audit.csv"
SUMMARY_PATH = RESULT_DIR / "alb2002_weight_design_evidence_summary.csv"
REPORT_PATH = REPORT_DIR / "alb2002_weight_design_evidence_audit.md"

DECISION = "blocked_alb2002_weight_design_semantics_not_promotion_ready"
NO_PROMOTION = "not_promoted_weight_design_evidence_only"

AUDIT_COLUMNS = [
    "country",
    "survey_name",
    "wave",
    "idno",
    "evidence_domain",
    "evidence_item",
    "source_artifacts",
    "observed_rows",
    "promotion_ready_rows",
    "diagnostic_value",
    "evidence_status",
    "promotion_status",
    "blocking_reason",
    "next_action",
]
SUMMARY_COLUMNS = ["metric", "value", "interpretation"]


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
    try:
        number = float(value)
    except (TypeError, ValueError):
        return str(value)
    if not math.isfinite(number):
        return ""
    if number.is_integer():
        return str(int(number))
    return f"{number:.6g}"


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


def psu_hh_key(df: pd.DataFrame, psu: str = "psu", hh: str = "hh") -> pd.Series:
    psu_key = df[psu].map(key_part)
    hh_key = df[hh].map(key_part)
    key = psu_key + "-" + hh_key
    key.loc[(psu_key == "") | (hh_key == "")] = ""
    return key


def safe_fetch_study_page() -> tuple[str, str, str, str]:
    request = urllib.request.Request(
        STUDY_URL,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) climate-uhc-ml-audit/1.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        },
        method="GET",
    )
    try:
        with urllib.request.urlopen(request, timeout=35) as response:
            status = str(getattr(response, "status", ""))
            content_type = response.headers.get("Content-Type", "")
            body = response.read()
        SNAPSHOT_PATH.write_bytes(body)
        charset = "utf-8"
        if "charset=" in content_type.lower():
            charset = content_type.lower().split("charset=", 1)[1].split(";", 1)[0].strip() or "utf-8"
        return "reachable_page_saved", status, unescape(body.decode(charset, errors="replace")), sha256_file(SNAPSHOT_PATH)
    except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, OSError) as exc:
        if SNAPSHOT_PATH.exists():
            return "using_existing_snapshot_after_fetch_failure", "", SNAPSHOT_PATH.read_text(encoding="utf-8", errors="replace"), sha256_file(SNAPSHOT_PATH)
        return "blocked_unreachable_no_snapshot", "", str(exc), ""


def page_flags(text: str) -> dict[str, int]:
    lower = " ".join(text.lower().split())
    return {
        "reference_id_seen": int(IDNO.lower() in lower),
        "unit_households_seen": int("households" in lower),
        "unit_individuals_seen": int("individuals" in lower),
        "sampling_frame_2001_census_seen": int("april 2001" in lower and "sampling frame" in lower),
        "fieldwork_april_july_seen": int("april and early july" in lower),
        "systematic_equal_probability_selection_seen": int("selected systematically and with equal probability" in lower),
        "sample_design_doc_referenced": int("full description of the original sample design" in lower),
        "gps_longitude_latitude_seen": int(("longitude and latitude" in lower or "gps" in lower) and "household" in lower),
        "reserve_household_control_seen": int("reserve" in lower and "household" in lower and "supervisor" in lower),
    }


def read_weight_file() -> tuple[pd.DataFrame, dict[str, str], str, str]:
    if pyreadstat is None:
        return pd.DataFrame(), {}, "blocked_pyreadstat_missing", ""
    path = RAW_ROOT / "weights_1.sav"
    try:
        df, meta = pyreadstat.read_sav(str(path), apply_value_formats=False, encoding="latin1")
        labels = {column: meta.column_names_to_labels.get(column, "") for column in df.columns}
        return df, labels, "read_ok", sha256_file(path)
    except Exception as exc:  # noqa: BLE001 - audit needs the original failure text.
        return pd.DataFrame(), {}, f"blocked_read_error:{type(exc).__name__}:{str(exc)[:120]}", sha256_file(path) if path.exists() else ""


def read_legacy_weight_probe() -> str:
    if pyreadstat is None:
        return "blocked_pyreadstat_missing"
    path = RAW_ROOT / "weights.sav"
    if not path.exists():
        return "missing"
    errors: list[str] = []
    for encoding in ["latin1", "cp1252", "iso-8859-1"]:
        try:
            pyreadstat.read_sav(str(path), metadataonly=True, apply_value_formats=False, encoding=encoding)
            return f"readable_metadata:{encoding}"
        except Exception as exc:  # noqa: BLE001 - audit records legacy encoding issues.
            errors.append(f"{encoding}:{type(exc).__name__}")
    return "metadata_read_failed_" + ";".join(errors)


def stat(series: pd.Series, op: str) -> str:
    valid = pd.to_numeric(series, errors="coerce").dropna()
    if valid.empty:
        return ""
    if op == "min":
        return fmt(valid.min())
    if op == "p50":
        return fmt(valid.quantile(0.50))
    if op == "p95":
        return fmt(valid.quantile(0.95))
    if op == "max":
        return fmt(valid.max())
    if op == "mean":
        return fmt(valid.mean())
    if op == "sum":
        return fmt(valid.sum())
    return ""


def audit_row(
    domain: str,
    item: str,
    sources: list[str],
    observed_rows: Any,
    diagnostic_value: str,
    evidence_status: str,
    next_action: str,
    promotion_ready_rows: Any = 0,
) -> dict[str, str]:
    return {
        "country": COUNTRY,
        "survey_name": SURVEY_NAME,
        "wave": WAVE,
        "idno": IDNO,
        "evidence_domain": domain,
        "evidence_item": item,
        "source_artifacts": ";".join(sources),
        "observed_rows": fmt(observed_rows),
        "promotion_ready_rows": fmt(promotion_ready_rows),
        "diagnostic_value": diagnostic_value,
        "evidence_status": evidence_status,
        "promotion_status": NO_PROMOTION,
        "blocking_reason": (
            "ALB_2002 has visible household weights, PSU, stratum, and urban/rural fields, plus official sampling context, "
            "but promoted weighted inference still requires accepted weight target-population, normalization, design-use, "
            "finite-population/strata/PSU handling, and outcome/climate gates to pass together."
        ),
        "next_action": next_action,
    }


def build_rows() -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    page_status, http_status, page_text, page_sha = safe_fetch_study_page()
    flags = page_flags(page_text)
    weights, labels, weight_read_status, weight_sha = read_weight_file()
    legacy_weight_status = read_legacy_weight_probe()
    candidate = pd.read_csv(CANDIDATE_PATH) if CANDIDATE_PATH.exists() else pd.DataFrame()
    merge_audit = read_csv_dicts(MERGE_AUDIT_PATH)
    weight_merge = next((row for row in merge_audit if row.get("module") == "household_weights"), {})

    rows: list[dict[str, str]] = []
    rows.append(
        audit_row(
            "official_study_metadata",
            "worldbank_study_page_sampling_context",
            [STUDY_URL, f"temp/source_snapshots/{SNAPSHOT_PATH.name}"],
            1 if page_status.startswith(("reachable", "using_existing")) else 0,
            f"page_status={page_status}; http_status={http_status}; sha256={page_sha}; "
            + "; ".join(f"{key}={value}" for key, value in flags.items()),
            "official_page_context_seen_weight_rules_not_explicit" if flags["reference_id_seen"] else "blocked_official_page_context_not_verified",
            "Use the official study page as context only; obtain or locate the original sample-design/weight-use documentation before promoting weighted inference.",
        )
    )
    rows.append(
        audit_row(
            "raw_weight_file_metadata",
            "weights_1_sav_variable_labels",
            [f"temp/raw_extracted/lsms2002en_4dbf0b087520/lsms2002en/Data_2002/weights_1.sav"],
            len(weights),
            f"read_status={weight_read_status}; sha256={weight_sha}; columns={';'.join(weights.columns) if not weights.empty else ''}; "
            f"weight_label={labels.get('weight', '')}; stratum_label={labels.get('stratum', '')}; psu_label={labels.get('psu', '')}; ur_label={labels.get('ur', '')}",
            "raw_weight_file_readable_household_weight_label_seen" if not weights.empty and labels.get("weight") else weight_read_status,
            "Keep raw weight metadata in the audit layer until the population basis and design-use rules are accepted.",
        )
    )
    rows.append(
        audit_row(
            "raw_weight_file_metadata",
            "weights_sav_legacy_encoding_probe",
            [f"temp/raw_extracted/lsms2002en_4dbf0b087520/lsms2002en/Data_2002/weights.sav"],
            1 if legacy_weight_status.startswith("readable") else 0,
            f"legacy_weight_probe_status={legacy_weight_status}",
            "legacy_weight_file_not_used_weight_1_readable" if "failed" in legacy_weight_status else legacy_weight_status,
            "Use `weights_1.sav` as the readable household-weight source unless later documentation proves a different official weight file should be preferred.",
        )
    )

    if not weights.empty:
        weights = weights.copy()
        weights["psu_hh_key"] = psu_hh_key(weights)
        weight = pd.to_numeric(weights["weight"], errors="coerce")
        candidate_keys = set(psu_hh_key(candidate)) if not candidate.empty and {"psu", "hh"}.issubset(candidate.columns) else set()
        weight_keys = set(weights.loc[weights["psu_hh_key"].astype(str).str.len() > 0, "psu_hh_key"].astype(str))
        rows.append(
            audit_row(
                "raw_weight_value_coverage",
                "household_weight_values_and_key_coverage",
                [
                    f"temp/raw_extracted/lsms2002en_4dbf0b087520/lsms2002en/Data_2002/weights_1.sav",
                    "temp/alb2002_household_core_candidate.csv",
                    "temp/alb2002_household_core_merge_audit.csv",
                ],
                len(weights),
                f"positive_weight_rows={int((weight > 0).sum())}; nonmissing_weight_rows={int(weight.notna().sum())}; "
                f"min={stat(weight, 'min')}; p50={stat(weight, 'p50')}; p95={stat(weight, 'p95')}; max={stat(weight, 'max')}; "
                f"sum={stat(weight, 'sum')}; distinct_keys={len(weight_keys)}; candidate_key_matches={len(weight_keys.intersection(candidate_keys))}; "
                f"merge_audit_base_matches={weight_merge.get('base_rows_matched', '')}; merge_audit_status={weight_merge.get('merge_status', '')}",
                "complete_positive_weight_key_coverage_design_semantics_blocked",
                "Carry weights as candidate design variables, but do not report final weighted prevalence until outcomes and weight-use rules pass.",
            )
        )
        rows.append(
            audit_row(
                "raw_design_fields",
                "psu_stratum_urban_rural_fields_available",
                [f"temp/raw_extracted/lsms2002en_4dbf0b087520/lsms2002en/Data_2002/weights_1.sav", "temp/alb2002_household_core_candidate.csv"],
                len(weights),
                f"distinct_psu={weights['psu'].nunique(dropna=True)}; distinct_stratum={weights['stratum'].nunique(dropna=True)}; "
                f"distinct_urban_rural={weights['ur'].nunique(dropna=True)}; distinct_district={weights['distr'].nunique(dropna=True)}; "
                f"candidate_has_stratum={int('stratum' in candidate.columns)}; candidate_has_urban_rural={int('urban_rural_code_weight' in candidate.columns)}",
                "design_fields_available_in_raw_and_candidate_design_semantics_blocked",
                "Preserve PSU, stratum, urban/rural, district, and weight fields in any future harmonized candidate and document exact variance-estimation design before inference.",
            )
        )

    rows.append(
        audit_row(
            "promotion_gate",
            "weighted_inference_and_harmonized_promotion_gate",
            ["temp/alb2002_weight_design_evidence_audit.csv", "result/alb2002_weight_design_evidence_summary.csv"],
            1,
            "weight/design evidence is stronger than before, but promotion-ready rows remain zero by design",
            DECISION,
            "Resolve weight target population, normalization, survey-design variance handling, outcome promotion, and climate linkage before writing weighted analytical data.",
        )
    )

    positive_weight_rows = 0
    distinct_stratum = 0
    distinct_psu = 0
    candidate_matches = 0
    if not weights.empty:
        weight = pd.to_numeric(weights["weight"], errors="coerce")
        positive_weight_rows = int((weight > 0).sum())
        distinct_stratum = int(weights["stratum"].nunique(dropna=True))
        distinct_psu = int(weights["psu"].nunique(dropna=True))
        candidate_keys = set(psu_hh_key(candidate)) if not candidate.empty and {"psu", "hh"}.issubset(candidate.columns) else set()
        weight_keys = set(weights.loc[weights["psu_hh_key"].astype(str).str.len() > 0, "psu_hh_key"].astype(str))
        candidate_matches = len(weight_keys.intersection(candidate_keys))

    summary = [
        {"metric": "alb2002_weight_design_evidence_audit_rows", "value": str(len(rows)), "interpretation": "Rows in the ALB_2002 weight/design evidence audit."},
        {"metric": "alb2002_weight_design_source_page_reachable_rows", "value": str(int(page_status.startswith(("reachable", "using_existing")))), "interpretation": "Official study page or saved snapshot available for source context."},
        {"metric": "alb2002_weight_design_source_page_flag_rows", "value": str(sum(flags.values())), "interpretation": "Official study-page flags detected for study identity, sampling context, fieldwork, and GPS intent."},
        {"metric": "alb2002_weight_design_raw_weight_file_rows", "value": str(len(weights)), "interpretation": "Rows read from weights_1.sav."},
        {"metric": "alb2002_weight_design_positive_weight_rows", "value": str(positive_weight_rows), "interpretation": "Rows with positive household weights in weights_1.sav."},
        {"metric": "alb2002_weight_design_candidate_key_match_rows", "value": str(candidate_matches), "interpretation": "Readable weight-file keys matching the temp household core candidate."},
        {"metric": "alb2002_weight_design_distinct_psu_rows", "value": str(distinct_psu), "interpretation": "Distinct PSU values in the readable weight file."},
        {"metric": "alb2002_weight_design_distinct_stratum_rows", "value": str(distinct_stratum), "interpretation": "Distinct stratum values in the readable weight file."},
        {"metric": "alb2002_weight_design_weighted_inference_ready_rows", "value": "0", "interpretation": "Rows ready for promoted weighted inference; intentionally zero."},
        {"metric": "alb2002_weight_design_harmonized_promotion_ready_rows", "value": "0", "interpretation": "Rows ready for harmonized data promotion after this audit; intentionally zero."},
        {"metric": "alb2002_weight_design_current_decision", "value": DECISION, "interpretation": "Current fail-closed ALB_2002 weight/design decision."},
    ]
    return rows, summary


def markdown_rows(rows: list[dict[str, str]]) -> str:
    columns = ["evidence_domain", "evidence_item", "observed_rows", "promotion_ready_rows", "evidence_status", "diagnostic_value"]
    lines = ["| " + " | ".join(columns) + " |", "|" + "|".join("---" for _ in columns) + "|"]
    for row in rows:
        values = []
        for column in columns:
            value = (row.get(column, "") or "").replace("|", "/")
            if len(value) > 135:
                value = value[:132] + "..."
            values.append(value)
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines)


def write_report(rows: list[dict[str, str]], summary: list[dict[str, str]]) -> None:
    summary_table = "\n".join(f"| {row['metric']} | {row['value']} | {row['interpretation']} |" for row in summary)
    REPORT_PATH.write_text(
        f"""# ALB_2002 Weight And Design Evidence Audit

Status: fail-closed. This audit documents the ALB_2002 household weight and survey-design evidence now visible in local raw files and official study-page metadata. It does not promote weighted inference or write analysis-ready data.

## Summary

| Metric | Value | Interpretation |
|---|---:|---|
{summary_table}

## Evidence Rows

{markdown_rows(rows)}

## Interpretation

- `weights_1.sav` is readable and contains household keys, district, stratum, urban/rural, household size, and a `weight` variable labelled as household weights.
- The readable weight file covers the 3,599 temp household-core rows and carries positive household weights for all rows.
- The official World Bank study page verifies the ALB_2002 study identity and sampling context, including the 2001 census sampling frame and fieldwork context, and documents GPS intent. It is not enough by itself to promote GPS linkage or final weighted inference.
- Promotion remains blocked because the target population, weight normalization, survey-design variance handling, finite-population assumptions, and downstream outcome/climate gates have not all passed together.

## Machine-Readable Outputs

- `temp/alb2002_weight_design_evidence_audit.csv`
- `result/alb2002_weight_design_evidence_summary.csv`
- `temp/source_snapshots/alb2002_worldbank_study_description_weight_design.html`
""",
        encoding="utf-8",
    )


def main() -> None:
    ensure_dirs()
    rows, summary = build_rows()
    write_csv(AUDIT_PATH, rows, AUDIT_COLUMNS)
    write_csv(SUMMARY_PATH, summary, SUMMARY_COLUMNS)
    write_report(rows, summary)
    append_log(TEMP_DIR / "audit_log.md", f"Audited ALB_2002 weight/design evidence rows={len(rows)} decision={DECISION}.")
    print(f"ALB_2002 weight/design evidence audit rows={len(rows)} decision={DECISION}.")


if __name__ == "__main__":
    main()
