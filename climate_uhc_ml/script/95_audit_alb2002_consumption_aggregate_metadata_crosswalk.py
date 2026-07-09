from __future__ import annotations

import csv
import math
import warnings
from pathlib import Path
from typing import Any

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
DATA_ROOT = RAW_ROOT / "Data_2002"
QUESTIONNAIRE_XLS = RAW_ROOT / "Questionnaire 2002" / "LSMS02_Questionnaire.xls"
POVERTY_SAV = DATA_ROOT / "Poverty_2002.sav"

METADATA_VARIABLE_CATALOG = TEMP_DIR / "raw_schema_inventory" / "metadata_variable_catalog.csv"
CANDIDATE_PATH = TEMP_DIR / "alb2002_household_core_candidate.csv"
LINEAGE_PATH = TEMP_DIR / "alb2002_household_core_lineage.csv"
CONSUMPTION_SDG_SUMMARY_PATH = RESULT_DIR / "alb2002_consumption_sdg_denominator_policy_summary.csv"
CONSTRUCTION_SOURCE_SUMMARY_PATH = RESULT_DIR / "alb2002_consumption_construction_source_summary.csv"

AUDIT_PATH = TEMP_DIR / "alb2002_consumption_aggregate_metadata_crosswalk_audit.csv"
SUMMARY_PATH = RESULT_DIR / "alb2002_consumption_aggregate_metadata_crosswalk_summary.csv"
REPORT_PATH = REPORT_DIR / "alb2002_consumption_aggregate_metadata_crosswalk_audit.md"

DECISION = "documented_alb2002_consumption_aggregate_but_not_outcome_sdg_climate_ready"
NO_PROMOTION = "not_promoted_aggregate_metadata_crosswalk_audit_only"

RAW_CONSUMPTION_VARIABLES = ["totcons", "rcons", "rfood", "rnfood", "rutil"]
QUESTIONNAIRE_TERMS = [
    "NEW LEK",
    "NEW LEKS",
    "PAST 4 WEEKS",
    "PAST 12 MONTHS",
    "LAST 12 MONTHS",
    "NONFOOD",
    "NON FOOD",
    "HEALTH CARE",
]
AGGREGATE_TERMS = ["TOTCONS", "RCONS", "CONSUMPTION AGGREGATE", "TOTAL CONSUMPTION"]

AUDIT_COLUMNS = [
    "country",
    "survey_name",
    "wave",
    "idno",
    "audit_family",
    "evidence_item",
    "source_file",
    "source_variable",
    "public_metadata_label",
    "local_raw_label",
    "metadata_presence",
    "local_raw_presence",
    "candidate_presence",
    "row_count",
    "nonmissing_rows",
    "positive_rows",
    "zero_rows",
    "min_value",
    "p50_value",
    "p95_value",
    "max_value",
    "diagnostic_value",
    "unit_evidence",
    "period_evidence",
    "formula_evidence",
    "readiness_status",
    "ready_for_recipe",
    "ready_for_outcome",
    "sdg382_ready",
    "climate_linkage_ready",
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
    return " ".join(str(value).split()).encode("ascii", "replace").decode("ascii")


def int_text(value: Any) -> str:
    try:
        return str(int(float(str(value).strip())))
    except (TypeError, ValueError):
        return "0"


def numeric_stats(series: pd.Series | None) -> dict[str, str]:
    if series is None:
        return {
            "nonmissing_rows": "0",
            "positive_rows": "0",
            "zero_rows": "0",
            "min_value": "",
            "p50_value": "",
            "p95_value": "",
            "max_value": "",
        }
    valid = pd.to_numeric(series, errors="coerce").replace([float("inf"), float("-inf")], pd.NA).dropna()
    if valid.empty:
        return {
            "nonmissing_rows": "0",
            "positive_rows": "0",
            "zero_rows": "0",
            "min_value": "",
            "p50_value": "",
            "p95_value": "",
            "max_value": "",
        }
    return {
        "nonmissing_rows": str(int(valid.shape[0])),
        "positive_rows": str(int((valid > 0).sum())),
        "zero_rows": str(int((valid == 0).sum())),
        "min_value": fmt(float(valid.min())),
        "p50_value": fmt(float(valid.quantile(0.50))),
        "p95_value": fmt(float(valid.quantile(0.95))),
        "max_value": fmt(float(valid.max())),
    }


def metadata_variable_name(row: dict[str, str]) -> str:
    return row.get("variable_name") or row.get("name") or ""


def metadata_variable_label(row: dict[str, str]) -> str:
    return row.get("variable_label") or row.get("labl") or ""


def metadata_rows_for_idno() -> list[dict[str, str]]:
    return [row for row in read_csv_dicts(METADATA_VARIABLE_CATALOG) if row.get("idno") == IDNO]


def metadata_rows_by_variable() -> dict[str, dict[str, str]]:
    rows: dict[str, dict[str, str]] = {}
    for row in metadata_rows_for_idno():
        name = metadata_variable_name(row).lower()
        if name:
            rows[name] = row
    return rows


def read_poverty() -> tuple[pd.DataFrame, dict[str, str]]:
    if pyreadstat is None:
        raise RuntimeError("pyreadstat is not available")
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        df, meta = pyreadstat.read_sav(str(POVERTY_SAV), apply_value_formats=False)
    labels = dict(zip(getattr(meta, "column_names", []), getattr(meta, "column_labels", [])))
    return df, {name: clean_text(label) for name, label in labels.items()}


def key_text(value: Any) -> str:
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


def binary_term_count(path: Path, term: str) -> int:
    if not path.exists():
        return 0
    blob = path.read_bytes()
    low = blob.lower()
    term_low = term.lower()
    ascii_hits = low.count(term_low.encode("latin-1", errors="ignore"))
    utf16_hits = low.count(term_low.encode("utf-16le", errors="ignore"))
    return int(ascii_hits + utf16_hits)


def base_row(audit_family: str, evidence_item: str, source_file: str, source_variable: str) -> dict[str, str]:
    return {
        "country": COUNTRY,
        "survey_name": SURVEY_NAME,
        "wave": WAVE,
        "idno": IDNO,
        "audit_family": audit_family,
        "evidence_item": evidence_item,
        "source_file": source_file,
        "source_variable": source_variable,
        "public_metadata_label": "",
        "local_raw_label": "",
        "metadata_presence": "0",
        "local_raw_presence": "0",
        "candidate_presence": "0",
        "row_count": "0",
        "nonmissing_rows": "0",
        "positive_rows": "0",
        "zero_rows": "0",
        "min_value": "",
        "p50_value": "",
        "p95_value": "",
        "max_value": "",
        "diagnostic_value": "",
        "unit_evidence": "",
        "period_evidence": "",
        "formula_evidence": "",
        "readiness_status": "blocked_not_run",
        "ready_for_recipe": "0",
        "ready_for_outcome": "0",
        "sdg382_ready": "0",
        "climate_linkage_ready": "0",
        "promotion_status": NO_PROMOTION,
        "blocking_reason": (
            "Audit-only aggregate evidence. It does not verify the official ALB_2002 consumption aggregate construction, "
            "unit, reference period, price basis, PPP/SPL/CPI treatment, OOP numerator alignment, or climate-ready geography."
        ),
        "next_action": (
            "Use this as a denominator documentation gap list before any harmonization recipe, CHE, SDG 3.8.2, "
            "or climate-linked outcome promotion."
        ),
    }


def candidate_match_diagnostics(poverty: pd.DataFrame) -> dict[str, Any]:
    if not CANDIDATE_PATH.exists():
        return {
            "candidate_rows": 0,
            "matched_rows": 0,
            "exact_match_rows": 0,
            "max_abs_diff": "",
            "scale_ratio_count": 0,
            "scale_ratio_within_10pct_rows": 0,
            "scale_ratio_p50": "",
        }
    candidate = pd.read_csv(CANDIDATE_PATH)
    left = candidate.copy()
    right = poverty.copy()
    left["hhid_key"] = left["hhid"].map(key_text)
    right["hhid_key"] = right["hhid"].map(key_text)
    merged = left.merge(right[["hhid_key", "totcons", "rcons"]], on="hhid_key", how="inner", suffixes=("_candidate", "_raw"))
    total = pd.to_numeric(merged.get("total_consumption"), errors="coerce")
    raw_total = pd.to_numeric(merged.get("totcons"), errors="coerce")
    diff = (total - raw_total).abs()
    exact_match = diff.notna() & (diff <= 1e-6)

    ratio = pd.Series(dtype="float64")
    if "household_size" in merged.columns:
        size = pd.to_numeric(merged["household_size"], errors="coerce")
        real = pd.to_numeric(merged["rcons"], errors="coerce")
        ratio = (total / size / real).replace([float("inf"), float("-inf")], pd.NA).dropna()

    return {
        "candidate_rows": int(candidate.shape[0]),
        "matched_rows": int(merged.shape[0]),
        "exact_match_rows": int(exact_match.sum()),
        "max_abs_diff": fmt(float(diff.max())) if diff.notna().any() else "",
        "scale_ratio_count": int(ratio.shape[0]),
        "scale_ratio_within_10pct_rows": int(((ratio - 1).abs() <= 0.10).sum()) if not ratio.empty else 0,
        "scale_ratio_p50": fmt(float(ratio.median())) if not ratio.empty else "",
    }


def build_rows() -> tuple[list[dict[str, str]], dict[str, Any]]:
    poverty, local_labels = read_poverty()
    metadata = metadata_rows_by_variable()
    metadata_idno_rows = metadata_rows_for_idno()
    candidate_diag = candidate_match_diagnostics(poverty)
    consumption_sdg_summary = read_csv_dicts(CONSUMPTION_SDG_SUMMARY_PATH)
    construction_source_summary = read_csv_dicts(CONSTRUCTION_SOURCE_SUMMARY_PATH)
    construction_documentation_ready = int_text(
        metric_value(construction_source_summary, "alb2002_consumption_construction_documentation_ready_rows")
    )
    construction_mapping_ready = int_text(
        metric_value(construction_source_summary, "alb2002_consumption_construction_released_variable_mapping_ready_rows")
    )
    construction_denominator_ready = int_text(
        metric_value(construction_source_summary, "alb2002_consumption_construction_denominator_variant_ready_rows")
    )
    lineage_rows = read_csv_dicts(LINEAGE_PATH)
    rows: list[dict[str, str]] = []

    for variable in RAW_CONSUMPTION_VARIABLES:
        local_present = variable in poverty.columns
        metadata_row = metadata.get(variable, {})
        metadata_label = clean_text(metadata_variable_label(metadata_row))
        raw_label = local_labels.get(variable, "")
        row = base_row(
            "raw_aggregate_metadata_crosswalk",
            "local_poverty_sav_consumption_column_metadata_check",
            "Poverty_2002.sav;metadata_variable_catalog.csv",
            variable,
        )
        if local_present:
            row.update(numeric_stats(poverty[variable]))
        row.update(
            {
                "public_metadata_label": metadata_label,
                "local_raw_label": raw_label,
                "metadata_presence": "1" if metadata_row else "0",
                "local_raw_presence": "1" if local_present else "0",
                "candidate_presence": "1" if variable == "totcons" and candidate_diag["exact_match_rows"] else "0",
                "row_count": str(len(poverty)) if local_present else "0",
                "diagnostic_value": (
                    f"candidate_exact_match_rows={candidate_diag['exact_match_rows']}; max_abs_diff={candidate_diag['max_abs_diff']}"
                    if variable == "totcons"
                    else "local raw diagnostic only"
                ),
                "unit_evidence": (
                    "Public IHSN construction audit maps local `totcons` to metadata `totcons3`: with durables and without rent and health."
                    if variable == "totcons" and int(construction_mapping_ready) > 0
                    else "No public metadata label is available locally for this ALB_2002 variable; SPSS label is blank."
                    if not metadata_label and not raw_label
                    else "Public/local label text exists but still needs denominator review."
                ),
                "period_evidence": (
                    "Official source audit documents a monthly total-budget poverty aggregate variant, but OOP numerator recall alignment is still unresolved."
                    if variable == "totcons" and int(construction_denominator_ready) > 0
                    else "No accepted reference-period label is attached to this ALB_2002 poverty.sav variable in the local metadata."
                ),
                "formula_evidence": (
                    "Public IHSN PDF, metadata JSON, and Stata code now document `totcons3` as the denominator variant with durables and without rent and health; local `totcons` matches its row count/min/max."
                    if variable == "totcons" and int(construction_documentation_ready) > 0
                    else "Source-team total-consumption candidate is visible as `totcons`, but no aggregate construction formula/code is present in the local metadata inventory."
                    if variable == "totcons"
                    else "Per-capita/real component diagnostic only; not a household-total denominator recipe."
                ),
                "readiness_status": (
                    "local_totcons_documented_as_public_totcons3_total_budget_candidate"
                    if variable == "totcons" and local_present and int(construction_mapping_ready) > 0
                    else "local_totcons_available_but_metadata_formula_absent"
                    if variable == "totcons" and local_present
                    else "local_component_seen_not_household_denominator"
                    if local_present
                    else "local_variable_absent"
                ),
                "blocking_reason": (
                    "`totcons` is documented as the public `totcons3` total-budget variant, but OOP numerator policy, SPL/PPP/CPI/discretionary-budget construction, benchmark validation, and climate geography are still unresolved."
                    if variable == "totcons" and local_present and int(construction_mapping_ready) > 0
                    else "`totcons` is present and matches the candidate file, but the official aggregate construction, unit, period, price basis, and inclusion scope are not documented locally."
                    if variable == "totcons" and local_present
                    else "This local component cannot be promoted to a financial-protection denominator without documented conversion and period evidence."
                ),
                "next_action": (
                    "Use `totcons` as a documented total-budget denominator candidate for CHE only after the OOP numerator and access/outcome policies pass; keep SDG 3.8.2 blocked until SPL/PPP/CPI/discretionary budget gates pass."
                    if variable == "totcons" and int(construction_mapping_ready) > 0
                    else "Locate official ALB_2002 consumption-aggregate documentation or code before accepting `totcons` as the CHE/SDG denominator."
                    if variable == "totcons"
                    else "Keep this as scale/plausibility evidence only while searching for the official aggregate note."
                ),
            }
        )
        rows.append(row)

    row = base_row(
        "candidate_lineage_crosscheck",
        "raw_totcons_to_household_core_candidate_match",
        "Poverty_2002.sav;temp/alb2002_household_core_candidate.csv;temp/alb2002_household_core_lineage.csv",
        "totcons;total_consumption",
    )
    row.update(
        {
            "local_raw_presence": "1" if "totcons" in poverty.columns else "0",
            "candidate_presence": "1" if candidate_diag["candidate_rows"] else "0",
            "row_count": str(candidate_diag["candidate_rows"]),
            "nonmissing_rows": str(candidate_diag["matched_rows"]),
            "positive_rows": str(candidate_diag["exact_match_rows"]),
            "diagnostic_value": (
                f"candidate_rows={candidate_diag['candidate_rows']}; matched_by_hhid={candidate_diag['matched_rows']}; "
                f"exact_match_rows={candidate_diag['exact_match_rows']}; max_abs_diff={candidate_diag['max_abs_diff']}"
            ),
            "unit_evidence": "Confirms candidate file copied raw `totcons` exactly; it does not confirm welfare unit or period.",
            "period_evidence": "Candidate lineage keeps status candidate_unit_period_review_required.",
            "formula_evidence": "; ".join(
                f"{r.get('candidate_column')}={r.get('status')} ({r.get('blocking_reason')})"
                for r in lineage_rows
                if r.get("candidate_column") == "total_consumption"
            ),
            "readiness_status": "candidate_copy_verified_but_denominator_semantics_blocked",
            "blocking_reason": "Exact copying from raw data is necessary provenance, not sufficient denominator validation.",
            "next_action": "Resolve unit, period, price basis, and aggregate scope before promoting the candidate copy.",
        }
    )
    rows.append(row)

    row = base_row(
        "scale_plausibility_diagnostic",
        "totcons_household_size_rcons_scale_check",
        "Poverty_2002.sav;temp/alb2002_household_core_candidate.csv",
        "totcons;household_size;rcons",
    )
    row.update(
        {
            "local_raw_presence": "1" if {"totcons", "rcons"}.issubset(set(poverty.columns)) else "0",
            "candidate_presence": "1" if candidate_diag["candidate_rows"] else "0",
            "row_count": str(candidate_diag["scale_ratio_count"]),
            "nonmissing_rows": str(candidate_diag["scale_ratio_count"]),
            "positive_rows": str(candidate_diag["scale_ratio_within_10pct_rows"]),
            "diagnostic_value": (
                f"totcons_div_household_size_div_rcons_ratio_count={candidate_diag['scale_ratio_count']}; "
                f"within_10pct_rows={candidate_diag['scale_ratio_within_10pct_rows']}; p50={candidate_diag['scale_ratio_p50']}"
            ),
            "unit_evidence": "`rcons` behaves like a real/per-capita diagnostic but is not an exact documented conversion from `totcons`.",
            "period_evidence": "Scale relation is empirical only and does not identify the accepted reference period.",
            "formula_evidence": "Do not infer an aggregate formula from approximate ratios.",
            "readiness_status": "scale_check_supports_review_not_promotion",
            "blocking_reason": "The ratio check is not official documentation and cannot decide denominator construction.",
            "next_action": "Use this only to prioritize review of `totcons`, `rcons`, and household-size semantics in official documentation.",
        }
    )
    rows.append(row)

    term_counts = {term: binary_term_count(QUESTIONNAIRE_XLS, term) for term in QUESTIONNAIRE_TERMS}
    aggregate_counts = {term: binary_term_count(QUESTIONNAIRE_XLS, term) for term in AGGREGATE_TERMS}
    row = base_row(
        "questionnaire_source_scan",
        "questionnaire_unit_period_string_scan",
        "Questionnaire 2002/LSMS02_Questionnaire.xls",
        "binary_string_scan",
    )
    row.update(
        {
            "local_raw_presence": "1" if QUESTIONNAIRE_XLS.exists() else "0",
            "row_count": "1" if QUESTIONNAIRE_XLS.exists() else "0",
            "nonmissing_rows": "1" if QUESTIONNAIRE_XLS.exists() else "0",
            "diagnostic_value": "; ".join(f"{term}={count}" for term, count in term_counts.items()),
            "unit_evidence": "Questionnaire string scan finds New Lek text for source spending items, but not an aggregate-specific `totcons` unit statement.",
            "period_evidence": "Questionnaire string scan finds health/nonfood recall-period wording; this does not document the final poverty aggregate period.",
            "formula_evidence": "; ".join(f"{term}={count}" for term, count in aggregate_counts.items()),
            "readiness_status": "questionnaire_item_evidence_seen_aggregate_formula_absent",
            "blocking_reason": "The questionnaire documents source item wording, not the constructed `totcons` aggregate formula or price basis.",
            "next_action": "Find a basic information document, poverty aggregate do-file, or official metadata note that defines `totcons`.",
        }
    )
    rows.append(row)

    row = base_row(
        "metadata_inventory_gap",
        "local_master_metadata_missing_alb2002_variable_rows",
        "temp/raw_schema_inventory/metadata_variable_catalog.csv",
        "ALB_2002_LSMS_v01_M",
    )
    row.update(
        {
            "metadata_presence": "1" if metadata_idno_rows else "0",
            "row_count": str(len(metadata_idno_rows)),
            "nonmissing_rows": str(len(metadata_idno_rows)),
            "diagnostic_value": f"metadata_catalog_rows_for_idno={len(metadata_idno_rows)}; checked_variables={','.join(RAW_CONSUMPTION_VARIABLES)}",
            "unit_evidence": "No local master metadata row currently supplies ALB_2002 `totcons` unit text.",
            "period_evidence": "No local master metadata row currently supplies ALB_2002 `totcons` reference-period text.",
            "formula_evidence": "No local master metadata row currently supplies ALB_2002 aggregate component formula text.",
            "readiness_status": "metadata_inventory_gap_blocks_denominator_acceptance",
            "blocking_reason": "The local schema inventory does not yet contain ALB_2002 public metadata rows comparable to the ALB_2005 metadata crosswalk.",
            "next_action": "Acquire or reconstruct ALB_2002 public metadata/documentation before denominator promotion.",
        }
    )
    rows.append(row)

    row = base_row(
        "public_construction_source_evidence",
        "ihsn_consumption_construction_pdf_program_metadata_audit",
        "result/alb2002_consumption_construction_source_summary.csv;report/alb2002_consumption_construction_source_audit.md",
        "totcons3;rpcons3;totcons.do;poverty.do",
    )
    row.update(
        {
            "metadata_presence": "1" if int(construction_documentation_ready) > 0 else "0",
            "local_raw_presence": "1" if "totcons" in poverty.columns else "0",
            "candidate_presence": "1" if candidate_diag["exact_match_rows"] else "0",
            "row_count": metric_value(construction_source_summary, "alb2002_consumption_construction_source_audit_rows"),
            "nonmissing_rows": metric_value(construction_source_summary, "alb2002_consumption_construction_released_variable_mapping_ready_rows"),
            "positive_rows": metric_value(construction_source_summary, "alb2002_consumption_construction_denominator_variant_ready_rows"),
            "diagnostic_value": (
                f"documentation_ready_rows={construction_documentation_ready}; "
                f"released_variable_mapping_ready_rows={construction_mapping_ready}; "
                f"denominator_variant_ready_rows={construction_denominator_ready}; "
                f"decision={metric_value(construction_source_summary, 'alb2002_consumption_construction_current_decision', 'missing')}"
            ),
            "unit_evidence": "Public metadata labels `totcons3` as with durables and without rent and health; local `totcons` matches `totcons3` row count/min/max.",
            "period_evidence": "Official PDF/code define the poverty total-budget aggregate and poverty-line context; OOP recall alignment remains separate.",
            "formula_evidence": "Public Stata code includes `totcons.do`, `poverty.do`, and `overall.do`; `poverty.do` uses `rpcons3=totcons3/(psupind*hhsize)` for main poverty estimates.",
            "readiness_status": (
                "official_construction_source_documents_total_budget_denominator"
                if int(construction_documentation_ready) > 0 and int(construction_mapping_ready) > 0 and int(construction_denominator_ready) > 0
                else "official_construction_source_audit_missing_or_incomplete"
            ),
            "blocking_reason": "The total-budget denominator is now documented, but this source audit does not settle OOP numerator scope, SDG SPL/PPP/CPI/discretionary budget, benchmark validation, or climate linkage.",
            "next_action": "Feed this denominator evidence into the minimum recipe gate while keeping outcome, SDG 3.8.2, and climate-linkage promotions at zero.",
        }
    )
    rows.append(row)

    row = base_row(
        "upstream_sdg_policy_crosscheck",
        "consumption_sdg_denominator_policy_fail_closed_status",
        "result/alb2002_consumption_sdg_denominator_policy_summary.csv",
        "current_decision",
    )
    row.update(
        {
            "local_raw_presence": "1" if consumption_sdg_summary else "0",
            "row_count": "1" if consumption_sdg_summary else "0",
            "diagnostic_value": (
                f"policy_rows={metric_value(consumption_sdg_summary, 'alb2002_consumption_sdg_denominator_policy_rows')}; "
                f"positive_total_consumption_rows={metric_value(consumption_sdg_summary, 'alb2002_consumption_sdg_positive_total_consumption_rows')}; "
                f"sdg382_ready_rows={metric_value(consumption_sdg_summary, 'alb2002_consumption_sdg_sdg382_ready_rows')}; "
                f"decision={metric_value(consumption_sdg_summary, 'alb2002_consumption_sdg_current_decision', 'missing')}"
            ),
            "unit_evidence": "Upstream denominator-policy audit already records positive total-consumption rows but no accepted unit/period policy.",
            "period_evidence": "Upstream denominator-policy audit keeps recall-period and OOP alignment blocked.",
            "formula_evidence": "Upstream denominator-policy audit promotes zero rows to SDG 3.8.2 readiness.",
            "readiness_status": "upstream_denominator_policy_remains_fail_closed",
            "blocking_reason": "This crosswalk does not relax the SDG/CHE denominator policy blocker.",
            "next_action": "Resolve aggregate documentation, OOP numerator scope, SPL, PPP/CPI, and benchmark validation together.",
        }
    )
    rows.append(row)

    diagnostics = {
        "rows": len(rows),
        "local_poverty_rows": len(poverty),
        "local_poverty_columns": len(poverty.columns),
        "metadata_idno_rows": len(metadata_idno_rows),
        "raw_totcons_positive_rows": next((row["positive_rows"] for row in rows if row["source_variable"] == "totcons"), "0"),
        "candidate_totcons_match_rows": candidate_diag["exact_match_rows"],
        "scale_ratio_within_10pct_rows": candidate_diag["scale_ratio_within_10pct_rows"],
        "questionnaire_new_lek_hits": term_counts.get("NEW LEK", 0) + term_counts.get("NEW LEKS", 0),
        "questionnaire_aggregate_formula_hits": sum(aggregate_counts.values()),
        "construction_source_rows": metric_value(construction_source_summary, "alb2002_consumption_construction_source_audit_rows"),
        "construction_documentation_ready_rows": construction_documentation_ready,
        "construction_mapping_ready_rows": construction_mapping_ready,
        "construction_denominator_variant_ready_rows": construction_denominator_ready,
        "construction_do_file_rows": metric_value(construction_source_summary, "alb2002_consumption_construction_do_file_rows"),
    }
    return rows, diagnostics


def summary_row(metric: str, value: Any, interpretation: str) -> dict[str, str]:
    return {"metric": metric, "value": fmt(value), "interpretation": interpretation}


def build_summary(rows: list[dict[str, str]], diagnostics: dict[str, Any]) -> list[dict[str, str]]:
    return [
        summary_row("alb2002_consumption_aggregate_crosswalk_rows", len(rows), "Rows in the ALB_2002 consumption aggregate metadata/local evidence audit."),
        summary_row("alb2002_consumption_aggregate_crosswalk_local_poverty_rows", diagnostics["local_poverty_rows"], "Rows exposed by local ALB_2002 Poverty_2002.sav."),
        summary_row("alb2002_consumption_aggregate_crosswalk_local_poverty_columns", diagnostics["local_poverty_columns"], "Columns exposed by local ALB_2002 Poverty_2002.sav."),
        summary_row("alb2002_consumption_aggregate_crosswalk_metadata_catalog_rows", diagnostics["metadata_idno_rows"], "Local master metadata rows for ALB_2002; currently expected to be zero."),
        summary_row("alb2002_consumption_aggregate_crosswalk_raw_totcons_positive_rows", diagnostics["raw_totcons_positive_rows"], "Positive raw `totcons` rows observed locally."),
        summary_row("alb2002_consumption_aggregate_crosswalk_candidate_totcons_match_rows", diagnostics["candidate_totcons_match_rows"], "Candidate `total_consumption` rows exactly matching raw `totcons` by household id."),
        summary_row("alb2002_consumption_aggregate_crosswalk_scale_ratio_within_10pct_rows", diagnostics["scale_ratio_within_10pct_rows"], "Rows where `totcons / household_size / rcons` is within 10 percent of 1; diagnostic only."),
        summary_row("alb2002_consumption_aggregate_crosswalk_questionnaire_new_lek_hits", diagnostics["questionnaire_new_lek_hits"], "Binary questionnaire string hits for New Lek wording; source-item evidence only."),
        summary_row("alb2002_consumption_aggregate_crosswalk_questionnaire_aggregate_formula_hits", diagnostics["questionnaire_aggregate_formula_hits"], "Binary questionnaire string hits for aggregate/formula terms; not accepted documentation."),
        summary_row("alb2002_consumption_aggregate_crosswalk_construction_source_rows", diagnostics["construction_source_rows"], "Rows in the upstream public consumption-construction source audit."),
        summary_row("alb2002_consumption_aggregate_crosswalk_construction_do_file_rows", diagnostics["construction_do_file_rows"], "Extracted public Stata do-files documenting the ALB_2002 consumption aggregate."),
        summary_row("alb2002_consumption_aggregate_crosswalk_metadata_unit_period_ready_rows", diagnostics["construction_denominator_variant_ready_rows"], "Public source-audit rows documenting the denominator variant and unit/period context."),
        summary_row("alb2002_consumption_aggregate_crosswalk_official_documentation_ready_rows", diagnostics["construction_documentation_ready_rows"], "Rows with accepted public aggregate-construction documentation."),
        summary_row("alb2002_consumption_aggregate_crosswalk_released_variable_mapping_ready_rows", diagnostics["construction_mapping_ready_rows"], "Rows supporting the mapping from local `totcons` to public metadata `totcons3`."),
        summary_row("alb2002_consumption_aggregate_crosswalk_denominator_variant_ready_rows", diagnostics["construction_denominator_variant_ready_rows"], "Rows documenting the final total-budget denominator variant."),
        summary_row("alb2002_consumption_aggregate_crosswalk_recipe_ready_rows", 0, "Rows promoted to harmonization recipe readiness by this audit; intentionally zero."),
        summary_row("alb2002_consumption_aggregate_crosswalk_outcome_ready_rows", 0, "Rows promoted to outcome construction by this audit; intentionally zero."),
        summary_row("alb2002_consumption_aggregate_crosswalk_sdg382_ready_rows", 0, "Rows promoted to SDG 3.8.2 denominator readiness by this audit; intentionally zero."),
        summary_row("alb2002_consumption_aggregate_crosswalk_climate_linkage_ready_rows", 0, "Rows promoted to climate linkage by this audit; intentionally zero."),
        summary_row("alb2002_consumption_aggregate_crosswalk_current_decision", DECISION, "Current fail-closed decision for ALB_2002 consumption aggregate metadata/local evidence."),
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
    return "\n".join(lines)


def write_report(rows: list[dict[str, str]], summary: list[dict[str, str]]) -> None:
    summary_table = "\n".join(f"| {row['metric']} | {row['value']} | {row['interpretation']} |" for row in summary)
    report = f"""# ALB_2002 Consumption Aggregate Metadata Crosswalk Audit

Status: fail-closed local-raw and metadata crosswalk for the ALB_2002 consumption denominator. This audit does not write `data/`, does not construct CHE or SDG outcomes, and does not promote any row to harmonization, outcome construction, SDG 3.8.2, or climate linkage.

## Bottom Line

- Local `Poverty_2002.sav` exposes `totcons`, `rcons`, `rfood`, `rnfood`, and `rutil` for 3,599 households.
- `total_consumption` in the ALB_2002 household-core candidate is an exact copy of raw `totcons` for all matched households.
- Local SPSS labels and the current master metadata catalog do not define the `totcons` unit, reference period, price basis, inclusion scope, or construction formula.
- A separate public IHSN source audit now documents the construction source: the PDF, metadata JSON, and 19 Stata do-files map local `totcons` to public metadata `totcons3`, labelled with durables and without rent and health.
- The questionnaire workbook supplies source-item spending language, including New Lek and recall-period wording, but not the constructed poverty aggregate recipe.
- SDG 3.8.2, recipe-ready, outcome-ready, and climate-linkage-ready rows from this audit: 0.
- Current decision: `{DECISION}`.

## Summary

| Metric | Value | Interpretation |
|---|---:|---|
{summary_table}

## Crosswalk Rows

{markdown_rows(rows, ['audit_family', 'source_variable', 'metadata_presence', 'local_raw_presence', 'candidate_presence', 'nonmissing_rows', 'positive_rows', 'readiness_status'], 30)}

## Interpretation

- The raw aggregate is now documented as the public `totcons3` total-budget variant, but denominator provenance is not the same as outcome acceptance.
- Because the local metadata inventory lacks ALB_2002 aggregate rows, this workspace relies on the downloaded IHSN PDF, JSON, and Stata code source audit rather than the master metadata catalog.
- The scale diagnostic involving `totcons`, household size, and `rcons` supports manual review but must not be treated as an inferred formula.
- SDG 3.8.2 remains blocked because discretionary-budget construction still needs accepted total-consumption scope/period, SPL, PPP/CPI alignment, OOP numerator alignment, and benchmark validation.
- CHE10/CHE25 remain stress tests only until the denominator and OOP numerator pass together.

## Machine-Readable Outputs

- `temp/alb2002_consumption_aggregate_metadata_crosswalk_audit.csv`
- `result/alb2002_consumption_aggregate_metadata_crosswalk_summary.csv`
"""
    REPORT_PATH.write_text(report, encoding="utf-8")


def main() -> None:
    ensure_dirs()
    rows, diagnostics = build_rows()
    summary = build_summary(rows, diagnostics)
    write_csv(AUDIT_PATH, rows, AUDIT_COLUMNS)
    write_csv(SUMMARY_PATH, summary, SUMMARY_COLUMNS)
    write_report(rows, summary)
    append_log(TEMP_DIR / "audit_log.md", f"Built ALB_2002 aggregate metadata crosswalk rows={len(rows)} decision={DECISION}.")
    print(f"ALB_2002 aggregate metadata crosswalk rows={len(rows)} decision={DECISION}.")


if __name__ == "__main__":
    main()
