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


IDNO = "ALB_2005_LSMS_v01_M"
COUNTRY = "Albania"
SURVEY_NAME = "Living Standards Measurement Survey 2005"
WAVE = "2005"

RAW_ROOT = TEMP_DIR / "raw_extracted" / "lsms2005en_1e7f1965c4a5" / "lsms2005en"
DATA_ROOT = RAW_ROOT / "Data_2005"
QUESTIONNAIRE_ROOT = RAW_ROOT / "Questionnaire 2005"
PART2_WORKBOOK = QUESTIONNAIRE_ROOT / "LSMS05_Questionnaire_part2.xls"

METADATA_VARIABLE_CATALOG = TEMP_DIR / "raw_schema_inventory" / "metadata_variable_catalog.csv"
VALUE_DECISION_SUMMARY_PATH = RESULT_DIR / "alb2005_harmonization_value_decision_summary.csv"
REQUIRED_VALUE_KEY_SUMMARY_PATH = RESULT_DIR / "alb2005_required_value_key_summary.csv"
HEALTH_QUESTIONNAIRE_AUDIT_PATH = TEMP_DIR / "alb2005_health_questionnaire_semantics_audit.csv"
HEALTH_QUESTIONNAIRE_SUMMARY_PATH = RESULT_DIR / "alb2005_health_questionnaire_semantics_summary.csv"
OOP_POLICY_SUMMARY_PATH = RESULT_DIR / "alb2005_oop_aggregation_policy_summary.csv"
SKIP_MISSING_SUMMARY_PATH = RESULT_DIR / "alb2005_skip_missing_semantics_summary.csv"
TIMING_GEO_SUMMARY_PATH = RESULT_DIR / "alb2005_timing_geography_exhaustive_summary.csv"

AUDIT_PATH = TEMP_DIR / "alb2005_consumption_oop_unit_period_audit.csv"
SUMMARY_PATH = RESULT_DIR / "alb2005_consumption_oop_unit_period_summary.csv"
REPORT_PATH = REPORT_DIR / "alb2005_consumption_oop_unit_period_audit.md"

DECISION = "blocked_alb2005_consumption_oop_unit_period_not_ready"
NO_PROMOTION = "not_promoted_consumption_oop_unit_period_audit_only"

AUDIT_COLUMNS = [
    "country",
    "survey_name",
    "wave",
    "idno",
    "audit_family",
    "evidence_item",
    "source_file",
    "source_variable",
    "observed_label_or_text",
    "row_count",
    "nonmissing_rows",
    "positive_rows",
    "zero_rows",
    "min_value",
    "p50_value",
    "max_value",
    "unit_evidence",
    "period_evidence",
    "denominator_relevance",
    "evidence_status",
    "ready_for_recipe",
    "ready_for_outcome",
    "sdg382_ready",
    "climate_linkage_ready",
    "promotion_status",
    "blocking_reason",
    "next_action",
]
SUMMARY_COLUMNS = ["metric", "value", "interpretation"]

PER_CAPITA_COLUMNS = ["rcons", "rfood", "rnfood", "rutility", "reduexp", "rdurable"]
METADATA_CONSUMPTION_VARIABLES = ["food", "nfoodc", "nfood05", "totutil", "totutil05", "totcons", "totcons05"]


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
    text = " ".join(str(value).split())
    return text.encode("ascii", "replace").decode("ascii")


def compact_join(values: list[Any], limit: int = 20) -> str:
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


def read_sav(file_name: str, usecols: list[str] | None = None) -> tuple[pd.DataFrame, Any]:
    if pyreadstat is None:
        raise RuntimeError("pyreadstat is not available")
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        return pyreadstat.read_sav(str(DATA_ROOT / file_name), usecols=usecols, apply_value_formats=False)


def metadata_labels(meta: Any) -> dict[str, str]:
    return dict(zip(getattr(meta, "column_names", []), getattr(meta, "column_labels", [])))


def numeric_stats(series: pd.Series) -> dict[str, str]:
    valid = pd.to_numeric(series, errors="coerce").replace([float("inf"), float("-inf")], pd.NA).dropna()
    if valid.empty:
        return {
            "nonmissing_rows": "0",
            "positive_rows": "0",
            "zero_rows": "0",
            "min_value": "",
            "p50_value": "",
            "max_value": "",
        }
    return {
        "nonmissing_rows": str(int(valid.notna().sum())),
        "positive_rows": str(int((valid > 0).sum())),
        "zero_rows": str(int((valid == 0).sum())),
        "min_value": fmt(float(valid.min())),
        "p50_value": fmt(float(valid.median())),
        "max_value": fmt(float(valid.max())),
    }


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
        "observed_label_or_text": "",
        "row_count": "0",
        "nonmissing_rows": "0",
        "positive_rows": "0",
        "zero_rows": "0",
        "min_value": "",
        "p50_value": "",
        "max_value": "",
        "unit_evidence": "",
        "period_evidence": "",
        "denominator_relevance": "",
        "evidence_status": "blocked_not_run",
        "ready_for_recipe": "0",
        "ready_for_outcome": "0",
        "sdg382_ready": "0",
        "climate_linkage_ready": "0",
        "promotion_status": NO_PROMOTION,
        "blocking_reason": (
            "Audit-only evidence. It does not verify full denominator construction, SDG 3.8.2 discretionary-budget inputs, "
            "PPP/SPL/CPI handling, household interview timing, or climate-ready geography."
        ),
        "next_action": (
            "Use this as manual denominator evidence only after the period, unit conversion, missing codes, survey design, "
            "fieldwork timing, and geography gates are reviewed."
        ),
    }


def metadata_consumption_labels() -> tuple[list[dict[str, str]], str]:
    rows = [
        row
        for row in read_csv_dicts(METADATA_VARIABLE_CATALOG)
        if row.get("idno") == IDNO and metadata_variable_name(row).lower() in METADATA_CONSUMPTION_VARIABLES
    ]
    labels = compact_join([f"{metadata_variable_name(row)}: {metadata_variable_label(row)}" for row in rows], 12)
    return rows, labels


def metadata_variable_name(row: dict[str, str]) -> str:
    return row.get("variable_name") or row.get("name") or ""


def metadata_variable_label(row: dict[str, str]) -> str:
    return row.get("variable_label") or row.get("labl") or ""


def workbook_consumption_period_hits() -> dict[str, int | str]:
    stats: dict[str, int | str] = {
        "questionnaire_nonfood_old_lek_rows": 0,
        "questionnaire_nonfood_twelve_month_rows": 0,
        "questionnaire_consumption_period_rows": 0,
        "questionnaire_scan_status": "not_run",
        "questionnaire_period_examples": "",
    }
    if not PART2_WORKBOOK.exists():
        stats["questionnaire_scan_status"] = "missing_workbook"
        return stats
    try:
        workbook = pd.ExcelFile(PART2_WORKBOOK)
        examples: list[str] = []
        for sheet_name in workbook.sheet_names:
            df = pd.read_excel(workbook, sheet_name=sheet_name, header=None, dtype=object)
            sheet_upper = sheet_name.upper()
            for _, row in df.iterrows():
                line = clean_text(" ".join(clean_text(value) for value in row.tolist()))
                upper = line.upper()
                if not line:
                    continue
                is_consumption_sheet = any(token in sheet_upper for token in ["NON FOOD", "DWELLING", "SOCIAL ASSISTANCE", "OTHER INCOME"])
                has_period = any(token in upper for token in ["LAST 12 MONTHS", "PAST 12 MONTHS", "LAST MONTH", "MONTHLY", "30 DAYS"])
                if is_consumption_sheet and "OLD LEKS" in upper:
                    stats["questionnaire_nonfood_old_lek_rows"] = int(stats["questionnaire_nonfood_old_lek_rows"]) + 1
                if is_consumption_sheet and ("LAST 12 MONTHS" in upper or "PAST 12 MONTHS" in upper):
                    stats["questionnaire_nonfood_twelve_month_rows"] = int(stats["questionnaire_nonfood_twelve_month_rows"]) + 1
                if is_consumption_sheet and has_period:
                    stats["questionnaire_consumption_period_rows"] = int(stats["questionnaire_consumption_period_rows"]) + 1
                    if len(examples) < 8:
                        examples.append(f"{sheet_name}: {line[:180]}")
        stats["questionnaire_scan_status"] = "read_ok"
        stats["questionnaire_period_examples"] = compact_join(examples, 8)
    except Exception as exc:  # pragma: no cover - depends on optional Excel engines.
        stats["questionnaire_scan_status"] = f"read_failed_{type(exc).__name__}"
    return stats


def add_psu_hh_key(df: pd.DataFrame, psu: str, hh: str) -> pd.DataFrame:
    out = df.copy()
    out["psu_key"] = out[psu].map(key_part)
    out["hh_key"] = out[hh].map(key_part)
    out["psu_hh_key"] = out["psu_key"] + "-" + out["hh_key"]
    out.loc[(out["psu_key"] == "") | (out["hh_key"] == ""), "psu_hh_key"] = ""
    return out


def roster_scaling_stats(poverty: pd.DataFrame) -> dict[str, Any]:
    roster, _ = read_sav("Modul_1A_household_rostera_cl.sav", ["psu", "hh"])
    roster = add_psu_hh_key(roster, "psu", "hh")
    hhsize = roster.groupby("psu_hh_key").size().rename("roster_count").reset_index()
    p = add_psu_hh_key(poverty, "PSU", "hh")
    merged = p.merge(hhsize, on="psu_hh_key", how="left")
    ratio = pd.to_numeric(merged["totcons"], errors="coerce") / pd.to_numeric(merged["rcons"], errors="coerce") / 12
    merged["implied_scale"] = ratio.replace([float("inf"), float("-inf")], pd.NA)
    merged["abs_diff_roster"] = (merged["implied_scale"] - merged["roster_count"]).abs()
    valid = merged["implied_scale"].dropna()
    return {
        "poverty_roster_join_rows": int(merged["roster_count"].notna().sum()),
        "roster_household_rows": int(len(hhsize)),
        "implied_scale_median": float(valid.median()) if not valid.empty else 0.0,
        "implied_scale_min": float(valid.min()) if not valid.empty else 0.0,
        "implied_scale_max": float(valid.max()) if not valid.empty else 0.0,
        "roster_count_median": float(hhsize["roster_count"].median()) if not hhsize.empty else 0.0,
        "abs_diff_le_0_1_rows": int((merged["abs_diff_roster"] <= 0.1).sum()),
        "abs_diff_le_0_01_rows": int((merged["abs_diff_roster"] <= 0.01).sum()),
        "max_abs_diff": float(merged["abs_diff_roster"].max()) if merged["abs_diff_roster"].notna().any() else 0.0,
    }


def build_rows() -> tuple[list[dict[str, str]], dict[str, Any]]:
    poverty, poverty_meta = read_sav("poverty.sav")
    labels = metadata_labels(poverty_meta)
    metadata_rows, metadata_label_text = metadata_consumption_labels()
    workbook_stats = workbook_consumption_period_hits()
    scaling = roster_scaling_stats(poverty)

    rows: list[dict[str, str]] = []

    row = base_row("consumption_denominator", "survey_total_consumption_raw_value", "poverty.sav", "totcons")
    row.update(
        {
            "observed_label_or_text": labels.get("totcons", ""),
            "row_count": str(len(poverty)),
            **numeric_stats(poverty["totcons"]),
            "unit_evidence": metadata_label_text or "poverty.sav label does not state currency unit",
            "period_evidence": "Raw poverty.sav label does not state recall or annual/monthly period; public metadata gives components but not enough period/price-basis detail for SDG/CHE promotion.",
            "denominator_relevance": "Candidate total-consumption denominator only; still not outcome-ready.",
            "evidence_status": "raw_total_consumption_seen_old_lek_metadata_period_unresolved",
            "blocking_reason": (
                "The total-consumption aggregate is positive and metadata says old lek, but period, price basis, missing rules, "
                "household-total interpretation, and SDG denominator adjustments are not fully verified."
            ),
            "next_action": "Confirm whether totcons is the correct annual household total, how old lek converts to analysis units, and whether CPI/PPP/SPL adjustments are available.",
        }
    )
    rows.append(row)

    row = base_row("consumption_denominator", "per_capita_consumption_raw_value", "poverty.sav", "rcons")
    row.update(
        {
            "observed_label_or_text": labels.get("rcons", ""),
            "row_count": str(len(poverty)),
            **numeric_stats(poverty["rcons"]),
            "unit_evidence": "Raw label indicates per-capita consumption but not currency conversion.",
            "period_evidence": "Internal scaling against totcons is informative but not documentation.",
            "denominator_relevance": "Useful denominator diagnostic; not a household total consumption denominator by itself.",
            "evidence_status": "raw_per_capita_consumption_seen_scope_review_required",
            "blocking_reason": "Per-capita consumption cannot substitute for household total consumption without a documented household-size/equivalence and period rule.",
            "next_action": "Use rcons only to cross-check scaling and period after official aggregate documentation is found.",
        }
    )
    rows.append(row)

    component_stats = []
    for column in PER_CAPITA_COLUMNS:
        stats = numeric_stats(poverty[column])
        component_stats.append(f"{column} positive={stats['positive_rows']} p50={stats['p50_value']}")
    row = base_row("consumption_denominator", "per_capita_component_values", "poverty.sav", ";".join(PER_CAPITA_COLUMNS))
    row.update(
        {
            "observed_label_or_text": compact_join([f"{column}: {labels.get(column, '')}" for column in PER_CAPITA_COLUMNS], 12),
            "row_count": str(len(poverty)),
            "nonmissing_rows": str(min(int(numeric_stats(poverty[column])["nonmissing_rows"]) for column in PER_CAPITA_COLUMNS)),
            "positive_rows": str(min(int(numeric_stats(poverty[column])["positive_rows"]) for column in PER_CAPITA_COLUMNS)),
            "unit_evidence": compact_join(component_stats, 12),
            "period_evidence": "Component labels are per-capita aggregates and do not independently document the household denominator period.",
            "denominator_relevance": "Component evidence supports plausibility review, not denominator promotion.",
            "evidence_status": "raw_per_capita_components_seen_not_household_totals",
            "blocking_reason": "The available raw component variables are per-capita measures, while the CHE/SDG denominator needs a verified household total or correctly converted aggregate.",
            "next_action": "Find the aggregate construction documentation or source code before reconstructing or decomposing total consumption.",
        }
    )
    rows.append(row)

    row = base_row("consumption_denominator", "metadata_old_lek_aggregate_labels", "metadata_variable_catalog.csv", ";".join(METADATA_CONSUMPTION_VARIABLES))
    row.update(
        {
            "observed_label_or_text": metadata_label_text,
            "row_count": str(len(metadata_rows)),
            "nonmissing_rows": str(len(metadata_rows)),
            "positive_rows": str(sum(1 for item in metadata_rows if "old lek" in metadata_variable_label(item).lower())),
            "unit_evidence": "Public metadata labels state old lek and new lek equals old lek divided by 10 for several aggregate variables.",
            "period_evidence": "Metadata labels identify formula components but still do not resolve recall-period harmonization or price-basis requirements for SDG 3.8.2.",
            "denominator_relevance": "Supports old/new lek review; not enough for final outcome construction.",
            "evidence_status": "metadata_old_lek_formula_labels_seen_period_unresolved",
            "blocking_reason": "Metadata labels improve unit evidence but are not a complete denominator recipe with period, price, poverty-line, and missing-code rules.",
            "next_action": "Trace whether local raw poverty.sav is totcons or totcons05 and obtain the official consumption aggregate note/codebook.",
        }
    )
    rows.append(row)

    row = base_row("consumption_denominator", "totcons_rcons_roster_scaling_check", "poverty.sav;Modul_1A_household_rostera_cl.sav", "totcons;rcons;psu;hh")
    row.update(
        {
            "observed_label_or_text": (
                f"totcons/rcons/12 median={fmt(scaling['implied_scale_median'])}; "
                f"roster household-size median={fmt(scaling['roster_count_median'])}; "
                f"abs diff <=0.1 rows={scaling['abs_diff_le_0_1_rows']}"
            ),
            "row_count": str(len(poverty)),
            "nonmissing_rows": str(scaling["poverty_roster_join_rows"]),
            "positive_rows": str(scaling["abs_diff_le_0_1_rows"]),
            "min_value": fmt(scaling["implied_scale_min"]),
            "p50_value": fmt(scaling["implied_scale_median"]),
            "max_value": fmt(scaling["implied_scale_max"]),
            "unit_evidence": "The ratio is household-size-like but does not equal raw roster counts for most households.",
            "period_evidence": "The ratio is consistent with possible annual/monthly scaling, but this remains an inference from values, not documentation.",
            "denominator_relevance": "Internal consistency check only; it cannot certify a CHE or SDG denominator.",
            "evidence_status": "internal_scaling_inference_not_denominator_documentation",
            "blocking_reason": "The value-scale check is not a substitute for an official aggregate construction note.",
            "next_action": "Use the check to target manual documentation review, not to promote outcomes.",
        }
    )
    rows.append(row)

    health_summary = read_csv_dicts(HEALTH_QUESTIONNAIRE_SUMMARY_PATH)
    oop_items = int(metric_value(health_summary, "alb2005_health_questionnaire_oop_item_rows", "0") or 0)
    old_lek_items = int(metric_value(health_summary, "alb2005_health_questionnaire_old_lek_unit_rows", "0") or 0)
    four_week_items = int(metric_value(health_summary, "alb2005_health_questionnaire_four_week_oop_rows", "0") or 0)
    twelve_month_items = int(metric_value(health_summary, "alb2005_health_questionnaire_twelve_month_oop_rows", "0") or 0)
    payment_audit = [row for row in read_csv_dicts(HEALTH_QUESTIONNAIRE_AUDIT_PATH) if row.get("concept") == "oop_health_expenditure"]
    payment_examples = compact_join([row.get("question_text", "") for row in payment_audit], 6)

    row = base_row("oop_unit_recall", "health_oop_old_lek_payment_items", "LSMS05_Questionnaire_part2.xls;Modul_9A_healtha_cl.sav", "health payment item variables")
    row.update(
        {
            "observed_label_or_text": payment_examples,
            "row_count": str(oop_items),
            "nonmissing_rows": str(oop_items),
            "positive_rows": str(old_lek_items),
            "unit_evidence": "Health questionnaire payment items explicitly use OLD LEKS.",
            "period_evidence": "Payment items split between past 4 weeks and past 12 months.",
            "denominator_relevance": "Numerator unit can be reviewed against the consumption denominator, but recall periods remain mixed.",
            "evidence_status": "questionnaire_old_lek_oop_items_seen_recall_mixed",
            "blocking_reason": "Old-lek OOP unit evidence is useful but does not solve recall-period harmonization or denominator period requirements.",
            "next_action": "Choose and document OOP scope, gift/transport inclusion, and annualization only after denominator period is verified.",
        }
    )
    rows.append(row)

    row = base_row("oop_unit_recall", "four_week_oop_recall_items", "LSMS05_Questionnaire_part2.xls;Modul_9A_healtha_cl.sav", "m9a_q16-m9a_q61")
    row.update(
        {
            "row_count": str(four_week_items),
            "nonmissing_rows": str(four_week_items),
            "positive_rows": str(four_week_items),
            "unit_evidence": "Four-week OOP rows use old-lek payment units.",
            "period_evidence": "Questionnaire rows explicitly refer to past 4 weeks for outpatient, provider, medicine, lab, transport, and own-drug payment items.",
            "denominator_relevance": "Cannot compare directly with annual consumption without a documented annualization rule.",
            "evidence_status": "four_week_oop_recall_seen_not_annual_denominator_ready",
            "blocking_reason": "Four-week OOP cannot be used as annual financial-protection numerator without a justified scaling rule.",
            "next_action": "Keep four-week OOP as a separate stress-test or annualize only under a documented sensitivity design.",
        }
    )
    rows.append(row)

    row = base_row("oop_unit_recall", "twelve_month_oop_recall_items", "LSMS05_Questionnaire_part2.xls;Modul_9A_healtha_cl.sav", "m9a_q68-m9a_q81")
    row.update(
        {
            "row_count": str(twelve_month_items),
            "nonmissing_rows": str(twelve_month_items),
            "positive_rows": str(twelve_month_items),
            "unit_evidence": "Twelve-month hospital/dentist OOP rows use old-lek payment units.",
            "period_evidence": "Questionnaire rows explicitly refer to past 12 months for hospital-stay and dentist payment items.",
            "denominator_relevance": "Closer to annual consumption but omits four-week outpatient/self-medication unless combined by policy.",
            "evidence_status": "twelve_month_oop_recall_seen_partial_scope_not_total_oop_ready",
            "blocking_reason": "Twelve-month rows cover hospital/dentist items only and cannot alone define total annual OOP.",
            "next_action": "Document whether hospital/dentist annual items are combined with annualized four-week items or kept as separate outcomes.",
        }
    )
    rows.append(row)

    row = base_row("questionnaire_consumption_period", "nonhealth_consumption_questionnaire_period_units", "LSMS05_Questionnaire_part2.xls", "nonfood/dwelling/social-assistance rows")
    row.update(
        {
            "observed_label_or_text": str(workbook_stats.get("questionnaire_period_examples", "")),
            "row_count": str(workbook_stats.get("questionnaire_consumption_period_rows", "0")),
            "nonmissing_rows": str(workbook_stats.get("questionnaire_nonfood_twelve_month_rows", "0")),
            "positive_rows": str(workbook_stats.get("questionnaire_nonfood_old_lek_rows", "0")),
            "unit_evidence": f"Workbook scan status={workbook_stats.get('questionnaire_scan_status', '')}; old-lek rows in nonhealth consumption sheets={workbook_stats.get('questionnaire_nonfood_old_lek_rows', 0)}.",
            "period_evidence": "Questionnaire nonhealth expenditure sections contain 12-month and monthly wording, but this does not document the final aggregate construction.",
            "denominator_relevance": "Supports component-period review; not enough to certify totcons period or SDG denominator.",
            "evidence_status": "questionnaire_consumption_period_units_seen_aggregate_recipe_missing",
            "blocking_reason": "Item-level questionnaire periods are not a full aggregate construction note and do not resolve price-basis or equivalence handling.",
            "next_action": "Find the consumption aggregate documentation/code before reconstructing or validating annual total consumption.",
        }
    )
    rows.append(row)

    skip_summary = read_csv_dicts(SKIP_MISSING_SUMMARY_PATH)
    row = base_row("remaining_blockers", "zero_missing_and_skip_semantics", "result/alb2005_skip_missing_semantics_summary.csv", "skip/missing summary")
    row.update(
        {
            "observed_label_or_text": f"triggered payment zero-or-missing rows={metric_value(skip_summary, 'alb2005_skip_missing_payment_zero_or_missing_when_triggered_rows')}",
            "row_count": metric_value(skip_summary, "alb2005_skip_missing_semantics_rows"),
            "nonmissing_rows": metric_value(skip_summary, "alb2005_skip_missing_payment_nonmissing_when_not_triggered_rows"),
            "positive_rows": metric_value(skip_summary, "alb2005_skip_missing_payment_positive_when_not_triggered_rows"),
            "unit_evidence": "Skip-leak checks reduce missing-code ambiguity for downstream variables under negative triggers.",
            "period_evidence": "They do not address recall-period harmonization or denominator period.",
            "denominator_relevance": "Necessary but insufficient for outcome construction.",
            "evidence_status": "skip_missing_semantics_seen_but_zero_review_remains",
            "blocking_reason": "Triggered rows with no positive payment still require zero/missing-code interpretation before final OOP aggregation.",
            "next_action": "Resolve zero-payment versus missing/no-cost semantics in the final OOP policy review.",
        }
    )
    rows.append(row)

    row = base_row("remaining_blockers", "sdg382_discretionary_budget_inputs", "source_audit;sdg382_denominator_plan;ALB_2005 audits", "societal_poverty_line;PPP;CPI;discretionary_budget")
    row.update(
        {
            "observed_label_or_text": "No ALB_2005 household-level SPL/PPP/CPI-adjusted discretionary-budget denominator is constructed.",
            "row_count": "1",
            "unit_evidence": "Local-currency old-lek evidence exists, but not an audited PPP/CPI/SPL conversion.",
            "period_evidence": "Total-consumption period and OOP annualization are unresolved.",
            "denominator_relevance": "Binding blocker for SDG 3.8.2.",
            "evidence_status": "sdg382_denominator_inputs_missing_or_unverified",
            "blocking_reason": "SDG 3.8.2 needs OOP over discretionary budget after poverty-line treatment; this audit has no verified SPL/PPP/CPI denominator.",
            "next_action": "Keep SDG 3.8.2 blocked until denominator, poverty-line, currency, and price adjustments are implemented and audited.",
        }
    )
    rows.append(row)

    timing_summary = read_csv_dicts(TIMING_GEO_SUMMARY_PATH)
    row = base_row("remaining_blockers", "climate_timing_geography_linkage", "result/alb2005_timing_geography_exhaustive_summary.csv", "interview_timing;coordinates;admin geography")
    row.update(
        {
            "observed_label_or_text": f"climate-ready rows={metric_value(timing_summary, 'alb2005_climate_linkage_ready_rows')}",
            "row_count": "1",
            "unit_evidence": "Not a currency-unit issue.",
            "period_evidence": "No verified household interview month/date exists for climate exposure windows.",
            "denominator_relevance": "Even a valid outcome denominator cannot be climate-linked without timing/geography.",
            "evidence_status": "climate_timing_geography_not_ready",
            "blocking_reason": "ALB_2005 remains blocked for climate linkage because timing and geography are not verified at analysis quality.",
            "next_action": "Find defensible household fieldwork timing and full-coverage geography before any climate-linked analysis.",
        }
    )
    rows.append(row)

    diagnostics = {
        "metadata_consumption_rows": len(metadata_rows),
        "metadata_old_lek_rows": sum(1 for item in metadata_rows if "old lek" in metadata_variable_label(item).lower()),
        "questionnaire_nonfood_old_lek_rows": int(workbook_stats.get("questionnaire_nonfood_old_lek_rows", 0)),
        "questionnaire_nonfood_twelve_month_rows": int(workbook_stats.get("questionnaire_nonfood_twelve_month_rows", 0)),
        "questionnaire_consumption_period_rows": int(workbook_stats.get("questionnaire_consumption_period_rows", 0)),
        "questionnaire_scan_status": workbook_stats.get("questionnaire_scan_status", ""),
        "oop_items": oop_items,
        "oop_old_lek_items": old_lek_items,
        "oop_four_week_items": four_week_items,
        "oop_twelve_month_items": twelve_month_items,
        **scaling,
    }
    return rows, diagnostics


def summary_row(metric: str, value: Any, interpretation: str) -> dict[str, str]:
    return {"metric": metric, "value": fmt(value), "interpretation": interpretation}


def build_summary(rows: list[dict[str, str]], diagnostics: dict[str, Any]) -> list[dict[str, str]]:
    value_decision_summary = read_csv_dicts(VALUE_DECISION_SUMMARY_PATH)
    required_summary = read_csv_dicts(REQUIRED_VALUE_KEY_SUMMARY_PATH)
    oop_policy_summary = read_csv_dicts(OOP_POLICY_SUMMARY_PATH)
    skip_summary = read_csv_dicts(SKIP_MISSING_SUMMARY_PATH)
    return [
        summary_row("alb2005_consumption_oop_unit_period_rows", len(rows), "Rows in the ALB_2005 consumption/OOP unit-period audit."),
        summary_row("alb2005_consumption_oop_unit_period_total_consumption_nonmissing_rows", metric_value(required_summary, "alb2005_required_value_key_total_consumption_nonmissing_rows"), "Nonmissing ALB_2005 total-consumption rows observed upstream."),
        summary_row("alb2005_consumption_oop_unit_period_total_consumption_positive_rows", next((row["positive_rows"] for row in rows if row["evidence_item"] == "survey_total_consumption_raw_value"), "0"), "Positive total-consumption rows in poverty.sav."),
        summary_row("alb2005_consumption_oop_unit_period_rcons_positive_rows", next((row["positive_rows"] for row in rows if row["evidence_item"] == "per_capita_consumption_raw_value"), "0"), "Positive per-capita consumption rows in poverty.sav."),
        summary_row("alb2005_consumption_oop_unit_period_metadata_old_lek_rows_observed", diagnostics["metadata_old_lek_rows"], "Public metadata aggregate labels mentioning old lek."),
        summary_row("alb2005_consumption_oop_unit_period_oop_old_lek_questionnaire_rows_observed", diagnostics["oop_old_lek_items"], "Questionnaire OOP payment rows explicitly recorded in old lek."),
        summary_row("alb2005_consumption_oop_unit_period_four_week_oop_rows_observed", diagnostics["oop_four_week_items"], "Questionnaire OOP rows with past-four-week recall."),
        summary_row("alb2005_consumption_oop_unit_period_twelve_month_oop_rows_observed", diagnostics["oop_twelve_month_items"], "Questionnaire OOP rows with past-12-month recall."),
        summary_row("alb2005_consumption_oop_unit_period_questionnaire_nonfood_old_lek_rows_observed", diagnostics["questionnaire_nonfood_old_lek_rows"], "Nonhealth consumption/expenditure questionnaire rows with old-lek text."),
        summary_row("alb2005_consumption_oop_unit_period_questionnaire_consumption_period_rows_observed", diagnostics["questionnaire_consumption_period_rows"], "Nonhealth consumption/expenditure questionnaire rows with 12-month, monthly, or 30-day period text."),
        summary_row("alb2005_consumption_oop_unit_period_totcons_rcons_roster_join_rows", diagnostics["poverty_roster_join_rows"], "Poverty rows joined to raw roster household counts for scaling diagnostics."),
        summary_row("alb2005_consumption_oop_unit_period_totcons_rcons_implied_scale_median", diagnostics["implied_scale_median"], "Median of totcons/rcons/12, used only as an internal scaling diagnostic."),
        summary_row("alb2005_consumption_oop_unit_period_roster_hhsize_median", diagnostics["roster_count_median"], "Median raw roster household member count."),
        summary_row("alb2005_consumption_oop_unit_period_totcons_rcons_abs_diff_le_0_1_rows", diagnostics["abs_diff_le_0_1_rows"], "Rows where totcons/rcons/12 is within 0.1 of raw roster size."),
        summary_row("alb2005_consumption_oop_unit_period_value_decision_recipe_ready_observed", metric_value(value_decision_summary, "alb2005_harmonization_value_decision_recipe_ready_rows"), "Recipe-ready rows observed in upstream value-decision audit."),
        summary_row("alb2005_consumption_oop_unit_period_required_value_key_recipe_ready_observed", metric_value(required_summary, "alb2005_required_value_key_recipe_ready_rows"), "Recipe-ready rows observed in upstream required value/key audit."),
        summary_row("alb2005_consumption_oop_unit_period_oop_policy_rows_observed", metric_value(oop_policy_summary, "alb2005_oop_aggregation_policy_rows"), "OOP aggregation stress-test rows observed upstream."),
        summary_row("alb2005_consumption_oop_unit_period_skip_missing_rows_observed", metric_value(skip_summary, "alb2005_skip_missing_semantics_rows"), "Skip/missing audit rows observed upstream."),
        summary_row("alb2005_consumption_oop_unit_period_sdg382_ready_rows", 0, "Rows promoted to SDG 3.8.2 denominator readiness by this audit; intentionally zero."),
        summary_row("alb2005_consumption_oop_unit_period_recipe_ready_rows", 0, "Rows promoted to harmonization recipe by this audit; intentionally zero."),
        summary_row("alb2005_consumption_oop_unit_period_outcome_ready_rows", 0, "Rows promoted to outcome construction by this audit; intentionally zero."),
        summary_row("alb2005_consumption_oop_unit_period_climate_linkage_ready_rows", 0, "Rows promoted to climate linkage by this audit; intentionally zero."),
        summary_row("alb2005_consumption_oop_unit_period_current_decision", DECISION, "Current fail-closed decision for ALB_2005 denominator unit/period evidence."),
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
    report = f"""# ALB_2005 Consumption/OOP Unit and Period Audit

Status: fail-closed denominator evidence audit. This audit reviews ALB_2005 total-consumption, per-capita consumption, OOP payment-unit, and recall-period evidence. It does not write `data/`, does not construct CHE/SDG outcomes, and does not promote any row to harmonization, outcome construction, SDG 3.8.2, or climate linkage.

## Bottom Line

- `poverty.sav` contains positive `totcons` and `rcons` values for 3,638 households, and public metadata labels document old-lek aggregate variables.
- Health questionnaire payment items explicitly use old lek, but their recall periods are mixed: four-week outpatient/self-medication rows and 12-month hospital/dentist rows.
- Item-level nonhealth questionnaire sections contain old-lek and period wording, but the available local evidence still lacks the final aggregate construction note needed to certify total-consumption period, price basis, and denominator use.
- The internal `totcons / rcons / 12` check is household-size-like, but it does not match raw roster counts closely enough to serve as documentation.
- SDG 3.8.2, recipe-ready, outcome-ready, and climate-linkage-ready rows from this audit: 0.
- Current decision: `{DECISION}`.

## Summary

| Metric | Value | Interpretation |
|---|---:|---|
{summary_table}

## Evidence Rows

{markdown_rows(rows, ['audit_family', 'evidence_item', 'source_file', 'source_variable', 'nonmissing_rows', 'positive_rows', 'unit_evidence', 'period_evidence', 'evidence_status'], 30)}

## Interpretation

- Old-lek evidence is stronger than before, but old/new lek scaling alone is not sufficient for financial-protection outcomes.
- A valid CHE denominator still needs a documented total-consumption period, household-total scope, price basis, missing-code handling, and survey design treatment.
- SDG 3.8.2 additionally needs societal poverty line, PPP/CPI alignment, and discretionary-budget construction.
- Climate-linked analysis remains blocked independently by missing verified household interview timing and climate-ready geography.

## Machine-Readable Outputs

- `temp/alb2005_consumption_oop_unit_period_audit.csv`
- `result/alb2005_consumption_oop_unit_period_summary.csv`
"""
    REPORT_PATH.write_text(report, encoding="utf-8")


def main() -> None:
    ensure_dirs()
    rows, diagnostics = build_rows()
    summary = build_summary(rows, diagnostics)
    write_csv(AUDIT_PATH, rows, AUDIT_COLUMNS)
    write_csv(SUMMARY_PATH, summary, SUMMARY_COLUMNS)
    write_report(rows, summary)
    append_log(TEMP_DIR / "audit_log.md", f"Built ALB_2005 consumption/OOP unit-period audit rows={len(rows)} decision={DECISION}.")
    print(f"ALB_2005 consumption/OOP unit-period rows={len(rows)} decision={DECISION}.")


if __name__ == "__main__":
    main()
