import math
import warnings
from typing import Any

import pandas as pd

from common import REPORT_DIR, RESULT_DIR, TEMP_DIR, append_log, ensure_dirs, write_csv

try:
    import pyreadstat
except ImportError:  # pragma: no cover - environment audit reports this separately.
    pyreadstat = None


IDNO = "ALB_2008_LSMS_v01_M"
COUNTRY = "Albania"
SURVEY_NAME = "Living Standards Measurement Survey 2008"
WAVE = "2008"
RAW_ROOT = TEMP_DIR / "raw_extracted" / "lsms_2008_eng_a54110ab32b9" / "LSMS 2008_eng" / "Data_2008"
CORE_PATH = TEMP_DIR / "alb2008_household_core_candidate.csv"

AUDIT_PATH = TEMP_DIR / "alb2008_outcome_semantics_raw_value_audit.csv"
SUMMARY_PATH = RESULT_DIR / "alb2008_outcome_semantics_raw_value_summary.csv"
REPORT_PATH = REPORT_DIR / "alb2008_outcome_semantics_raw_value_audit.md"

DECISION = "blocked_timing_geography_outcome_semantics_units_recall_skip_patterns"
BLOCKING_REASON = (
    "raw value/label evidence is available, but final outcome promotion remains blocked by missing verified interview "
    "timing, coarse geography/no GPS, OOP unit and recall-period comparability, gift/payment scope, missing-code "
    "review, questionnaire skip-pattern denominators, SDG discretionary-budget inputs, service-quality proxy "
    "interpretation, and cross-wave comparability"
)

AUDIT_COLUMNS = [
    "country",
    "survey_name",
    "wave",
    "idno",
    "outcome_domain",
    "candidate_variable",
    "source_file",
    "raw_variable",
    "raw_label",
    "source_unit",
    "row_count",
    "complete_key_rows",
    "distinct_household_keys",
    "base_households_matched",
    "base_match_rate",
    "nonmissing_rows",
    "distinct_values",
    "min_value",
    "max_value",
    "positive_numeric_rows",
    "negative_numeric_rows",
    "top_values",
    "value_label_examples",
    "recall_or_semantics_evidence",
    "skip_pattern_status",
    "unit_status",
    "merge_key_status",
    "promotion_status",
    "blocking_reason",
]
SUMMARY_COLUMNS = ["metric", "value", "interpretation"]

FOUR_WEEK_OOP = [
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
TWELVE_MONTH_OOP = [
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


def oop_semantics(variable: str, recall: str) -> str:
    if variable in {"m9a_q17", "m9a_q29", "m9a_q39", "m9a_q47", "m9a_q55", "m9a_q69", "m9a_q77"}:
        return f"value of gifts in {recall}; whether gifts belong in OOP requires policy definition review"
    return f"health payment item in {recall}; care context and aggregation scope require review"


CANDIDATES = [
    *[
        {
            "outcome_domain": "financial_oop_4w",
            "candidate_variable": "oop_4w_sum_unreviewed_component",
            "source_file": "Modul_9A_health.sav",
            "raw_variable": var,
            "source_unit": "person",
            "recall_or_semantics_evidence": oop_semantics(var, "past 4 weeks"),
            "skip_pattern_status": "person_level_payment_item_skip_patterns_require_questionnaire_review",
            "unit_status": "local_currency_units_unverified",
        }
        for var in FOUR_WEEK_OOP
    ],
    *[
        {
            "outcome_domain": "financial_oop_12m",
            "candidate_variable": "oop_12m_sum_unreviewed_component",
            "source_file": "Modul_9A_health.sav",
            "raw_variable": var,
            "source_unit": "person",
            "recall_or_semantics_evidence": oop_semantics(var, "past 12 months"),
            "skip_pattern_status": "person_level_inpatient_or_dentist_skip_patterns_require_questionnaire_review",
            "unit_status": "local_currency_units_unverified",
        }
        for var in TWELVE_MONTH_OOP
    ],
    {
        "outcome_domain": "need_proxy",
        "candidate_variable": "illness_or_disability_any",
        "source_file": "Modul_9A_health.sav",
        "raw_variable": "m9a_q01",
        "source_unit": "person",
        "recall_or_semantics_evidence": "chronic illness or disability status, not acute need alone",
        "skip_pattern_status": "need denominator and chronic-condition scope require review",
        "unit_status": "categorical_value_labels_available",
    },
    {
        "outcome_domain": "need_proxy",
        "candidate_variable": "sudden_illness_4w_any",
        "source_file": "Modul_9A_health.sav",
        "raw_variable": "m9a_q07",
        "source_unit": "person",
        "recall_or_semantics_evidence": "sudden illness in past 4 weeks",
        "skip_pattern_status": "acute-need denominator and person-to-household aggregation require review",
        "unit_status": "categorical_value_labels_available",
    },
    {
        "outcome_domain": "coverage_proxy",
        "candidate_variable": "health_license_any",
        "source_file": "Modul_9A_health.sav",
        "raw_variable": "m9a_q82",
        "source_unit": "person",
        "recall_or_semantics_evidence": "health license/coverage proxy, not a UHC failure outcome",
        "skip_pattern_status": "coverage scope and person-to-household aggregation require review",
        "unit_status": "categorical_value_labels_available",
    },
    {
        "outcome_domain": "access_affordability_proxy",
        "candidate_variable": "difficulty_pay_health",
        "source_file": "Modul_9B_health.sav",
        "raw_variable": "m9b_q01",
        "source_unit": "household",
        "recall_or_semantics_evidence": "difficulty paying for health care; includes no-one-needed-care response",
        "skip_pattern_status": "denominator mixes health-need and no-need households; skip pattern requires review",
        "unit_status": "categorical_value_labels_available",
    },
    *[
        {
            "outcome_domain": "coping_proxy",
            "candidate_variable": "health_payment_money_raising_any_unreviewed",
            "source_file": "Modul_9B_health.sav",
            "raw_variable": var,
            "source_unit": "household",
            "recall_or_semantics_evidence": "method to raise money to pay health care",
            "skip_pattern_status": "multiple-response method coding and denominator require review",
            "unit_status": "categorical_value_labels_available",
        }
        for var in ["m9b_q02", "m9b_q020", "m9b_q021", "m9b_q022", "m9b_q023"]
    ],
    {
        "outcome_domain": "access_proxy",
        "candidate_variable": "delayed_help_any",
        "source_file": "Modul_9B_health.sav",
        "raw_variable": "m9b_q03",
        "source_unit": "household",
        "recall_or_semantics_evidence": "times household member was ill but delayed seeking help",
        "skip_pattern_status": "count coding and illness denominator require review",
        "unit_status": "count_or_categorical_semantics_unverified",
    },
    {
        "outcome_domain": "access_cost_or_distance_reason",
        "candidate_variable": "delay_reason_cost_or_distance",
        "source_file": "Modul_9B_health.sav",
        "raw_variable": "m9b_q04",
        "source_unit": "household",
        "recall_or_semantics_evidence": "reason for delaying help",
        "skip_pattern_status": "conditional reason variable; denominator must be delayed-help households",
        "unit_status": "categorical_value_labels_available",
    },
    {
        "outcome_domain": "access_proxy",
        "candidate_variable": "hospital_referral_not_gone_any",
        "source_file": "Modul_9B_health.sav",
        "raw_variable": "m9b_q05",
        "source_unit": "household",
        "recall_or_semantics_evidence": "times household member was referred to hospital but did not go",
        "skip_pattern_status": "hospital-referral denominator and count coding require review",
        "unit_status": "count_or_categorical_semantics_unverified",
    },
    {
        "outcome_domain": "access_cost_or_distance_reason",
        "candidate_variable": "not_gone_reason_cost_or_distance",
        "source_file": "Modul_9B_health.sav",
        "raw_variable": "m9b_q06",
        "source_unit": "household",
        "recall_or_semantics_evidence": "reason for not going to hospital after referral",
        "skip_pattern_status": "conditional reason variable; denominator must be referred-not-gone households",
        "unit_status": "categorical_value_labels_available",
    },
    {
        "outcome_domain": "access_proxy",
        "candidate_variable": "refused_health_services_any",
        "source_file": "Modul_9B_health.sav",
        "raw_variable": "m9b_q07",
        "source_unit": "household",
        "recall_or_semantics_evidence": "household member refused health services",
        "skip_pattern_status": "refusal scope and denominator require review",
        "unit_status": "categorical_value_labels_available",
    },
    {
        "outcome_domain": "access_cost_or_distance_reason",
        "candidate_variable": "refused_reason_cost_or_distance",
        "source_file": "Modul_9B_health.sav",
        "raw_variable": "m9b_q08",
        "source_unit": "household",
        "recall_or_semantics_evidence": "reason for refusal of health services",
        "skip_pattern_status": "conditional reason variable; denominator must be refused-service households",
        "unit_status": "categorical_value_labels_available",
    },
    {
        "outcome_domain": "coverage_proxy",
        "candidate_variable": "medicine_discount_entitlement",
        "source_file": "Modul_9B_health.sav",
        "raw_variable": "m9b_q09",
        "source_unit": "household",
        "recall_or_semantics_evidence": "members entitled to purchase medicines at discount",
        "skip_pattern_status": "entitlement scope and medicine-need denominator require review",
        "unit_status": "categorical_value_labels_available",
    },
    {
        "outcome_domain": "access_affordability_proxy",
        "candidate_variable": "medicine_discount_cost_barrier",
        "source_file": "Modul_9B_health.sav",
        "raw_variable": "m9b_q10",
        "source_unit": "household",
        "recall_or_semantics_evidence": "always able to exercise medicine-discount right; includes affordability, supply, paperwork, and prescribing barriers",
        "skip_pattern_status": "conditional on entitlement/need; barrier categories require separate denominators",
        "unit_status": "categorical_value_labels_available",
    },
    {
        "outcome_domain": "facility_access_proxy",
        "candidate_variable": "usual_health_facility_location",
        "source_file": "Modul_9C_health.sav",
        "raw_variable": "m9c_q03",
        "source_unit": "household",
        "recall_or_semantics_evidence": "usual/used health facility is within or outside city/village",
        "skip_pattern_status": "facility-use denominator and access interpretation require review",
        "unit_status": "categorical_value_labels_available",
    },
    {
        "outcome_domain": "facility_access_proxy",
        "candidate_variable": "health_facility_choice_reason",
        "source_file": "Modul_9C_health.sav",
        "raw_variable": "m9c_q04",
        "source_unit": "household",
        "recall_or_semantics_evidence": "reason for choosing health facility, including no local facility and lower expense",
        "skip_pattern_status": "choice reason is not a forgone-care outcome; denominator requires facility-use review",
        "unit_status": "categorical_value_labels_available",
    },
    *[
        {
            "outcome_domain": "service_quality_cost_supply_proxy",
            "candidate_variable": candidate,
            "source_file": "Modul_9C_health.sav",
            "raw_variable": var,
            "source_unit": "household",
            "recall_or_semantics_evidence": evidence,
            "skip_pattern_status": "perception proxy only; not final access or financial-protection outcome",
            "unit_status": "categorical_value_labels_available",
        }
        for var, candidate, evidence in [
            ("m9c_q05c", "current_medicine_supply_availability", "current perception of medicine/vaccine supply availability"),
            ("m9c_q05e", "current_official_costs_rating", "current perception of official health-service costs"),
            ("m9c_q05f", "current_money_or_gifts_demanded_rating", "current perception of money or gifts demanded"),
            ("m9c_q05g", "current_waiting_time_rating", "current perception of waiting time"),
            ("m9c_q09", "most_important_aspect_to_improve", "health-service improvement priority, including costs, gifts, supply, and waiting time"),
            ("m9c_q10", "willing_to_pay_more_for_improved_services", "willingness to pay more for improved services"),
        ]
    ],
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


def add_psu_hh_key(df: pd.DataFrame, psu: str = "psu", hh: str = "hh") -> pd.DataFrame:
    out = df.copy()
    out["psu_key"] = out[psu].map(key_part)
    out["hh_key"] = out[hh].map(key_part)
    out["psu_hh_key"] = out["psu_key"] + "-" + out["hh_key"]
    out.loc[(out["psu_key"] == "") | (out["hh_key"] == ""), "psu_hh_key"] = ""
    return out


def compact_join(values: list[str], limit: int = 8) -> str:
    clean = [str(value).replace("|", "/").strip() for value in values if str(value).strip()]
    return "; ".join(clean[:limit])


def read_sav(file_name: str, usecols: list[str]) -> tuple[pd.DataFrame, Any]:
    if pyreadstat is None:
        raise RuntimeError("pyreadstat is not available")
    path = RAW_ROOT / file_name
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        return pyreadstat.read_sav(str(path), usecols=usecols, apply_value_formats=False)


def metadata_maps(meta: Any) -> tuple[dict[str, str], dict[str, dict[Any, str]]]:
    labels = meta.column_labels or [""] * len(meta.column_names)
    label_map = {name: label or "" for name, label in zip(meta.column_names, labels)}
    value_label_map = meta.variable_value_labels or {}
    return label_map, value_label_map


def top_values(series: pd.Series, value_labels: dict[Any, str]) -> str:
    counts = series.dropna().value_counts(dropna=True).head(8)
    pieces: list[str] = []
    for value, count in counts.items():
        label = value_labels.get(value, "")
        if not label:
            try:
                label = value_labels.get(float(value), "")
            except (TypeError, ValueError):
                label = ""
        piece = f"{fmt(value)}:{int(count)}"
        if label:
            piece += f" ({label})"
        pieces.append(piece)
    return compact_join(pieces, limit=8)


def value_label_examples(value_labels: dict[Any, str]) -> str:
    pieces = [f"{fmt(key)}={str(label).replace('|', '/')}" for key, label in list(value_labels.items())[:8]]
    return compact_join(pieces, limit=8)


def numeric_stats(series: pd.Series) -> dict[str, str]:
    numeric = pd.to_numeric(series, errors="coerce")
    valid = numeric.dropna()
    if valid.empty:
        return {
            "min_value": "",
            "max_value": "",
            "positive_numeric_rows": "0",
            "negative_numeric_rows": "0",
        }
    return {
        "min_value": fmt(float(valid.min())),
        "max_value": fmt(float(valid.max())),
        "positive_numeric_rows": str(int((valid > 0).sum())),
        "negative_numeric_rows": str(int((valid < 0).sum())),
    }


def merge_status(df: pd.DataFrame, base_keys: set[str], source_unit: str) -> dict[str, str]:
    complete = df["psu_hh_key"].astype(str).str.len() > 0
    complete_count = int(complete.sum())
    distinct_keys = set(df.loc[complete, "psu_hh_key"].astype(str))
    matched = len(base_keys.intersection(distinct_keys))
    duplicate_note = "person_level_many_to_one_allowed" if source_unit == "person" else "household_level_key_expected"
    if not complete_count:
        status = "blocked_no_complete_keys"
    elif matched == len(base_keys):
        status = f"base_household_coverage_complete_{duplicate_note}_semantics_pending"
    elif matched > 0:
        status = f"partial_base_household_coverage_{duplicate_note}_semantics_pending"
    else:
        status = "blocked_no_base_household_matches"
    return {
        "complete_key_rows": str(complete_count),
        "distinct_household_keys": str(len(distinct_keys)),
        "base_households_matched": str(matched),
        "base_match_rate": f"{matched / len(base_keys):.6f}" if base_keys else "0",
        "merge_key_status": status,
    }


def build_audit() -> list[dict[str, str]]:
    if not CORE_PATH.exists():
        raise FileNotFoundError(f"Missing prerequisite: {CORE_PATH}")
    core = pd.read_csv(CORE_PATH, encoding="utf-8-sig")
    core = add_psu_hh_key(core, "psu", "hh")
    base_keys = {value for value in core["psu_hh_key"].astype(str) if value}
    by_file: dict[str, pd.DataFrame] = {}
    labels_by_file: dict[str, dict[str, str]] = {}
    value_labels_by_file: dict[str, dict[str, dict[Any, str]]] = {}
    for file_name in sorted({row["source_file"] for row in CANDIDATES}):
        variables = sorted({row["raw_variable"] for row in CANDIDATES if row["source_file"] == file_name})
        df, meta = read_sav(file_name, ["psu", "hh", *variables])
        df = add_psu_hh_key(df, "psu", "hh")
        by_file[file_name] = df
        labels, value_labels = metadata_maps(meta)
        labels_by_file[file_name] = labels
        value_labels_by_file[file_name] = value_labels

    rows: list[dict[str, str]] = []
    for spec in CANDIDATES:
        df = by_file[spec["source_file"]]
        raw_variable = spec["raw_variable"]
        series = df[raw_variable] if raw_variable in df.columns else pd.Series(pd.NA, index=df.index)
        value_labels = value_labels_by_file[spec["source_file"]].get(raw_variable, {})
        stats = numeric_stats(series)
        rows.append(
            {
                "country": COUNTRY,
                "survey_name": SURVEY_NAME,
                "wave": WAVE,
                "idno": IDNO,
                "outcome_domain": spec["outcome_domain"],
                "candidate_variable": spec["candidate_variable"],
                "source_file": spec["source_file"],
                "raw_variable": raw_variable,
                "raw_label": labels_by_file[spec["source_file"]].get(raw_variable, ""),
                "source_unit": spec["source_unit"],
                "row_count": str(len(df)),
                "nonmissing_rows": str(int(series.notna().sum())),
                "distinct_values": str(int(series.dropna().nunique())),
                "top_values": top_values(series, value_labels),
                "value_label_examples": value_label_examples(value_labels),
                "recall_or_semantics_evidence": spec["recall_or_semantics_evidence"],
                "skip_pattern_status": spec["skip_pattern_status"],
                "unit_status": spec["unit_status"],
                "promotion_status": "not_ready_raw_semantics_only",
                "blocking_reason": BLOCKING_REASON,
                **stats,
                **merge_status(df, base_keys, spec["source_unit"]),
            }
        )
    return rows


def summary_row(metric: str, value: Any, interpretation: str) -> dict[str, str]:
    return {"metric": metric, "value": fmt(value), "interpretation": interpretation}


def build_summary(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    source_files = sorted({row["source_file"] for row in rows})
    with_value_labels = sum(1 for row in rows if row["value_label_examples"])
    positive_numeric = sum(1 for row in rows if int(row["positive_numeric_rows"] or "0") > 0)
    complete_merge = sum(1 for row in rows if row["merge_key_status"].startswith("base_household_coverage_complete"))
    conditional_reason = sum(1 for row in rows if "conditional" in row["skip_pattern_status"])
    gift_rows = sum(1 for row in rows if "gift" in row["recall_or_semantics_evidence"].lower() or "gift" in row["raw_label"].lower())
    return [
        summary_row("alb2008_outcome_semantics_raw_value_audit_rows", len(rows), "Rows in the ALB_2008 raw value/semantics audit."),
        summary_row("alb2008_outcome_semantics_source_files_scanned", len(source_files), "Raw health modules scanned for outcome semantics."),
        summary_row("alb2008_outcome_semantics_financial_oop_candidate_rows", sum(1 for row in rows if row["outcome_domain"].startswith("financial_oop")), "Raw OOP payment/gift candidate rows."),
        summary_row("alb2008_outcome_semantics_gift_candidate_rows", gift_rows, "Raw gift-value or gift-perception rows whose inclusion in OOP/access definitions requires review."),
        summary_row("alb2008_outcome_semantics_access_candidate_rows", sum(1 for row in rows if row["outcome_domain"].startswith("access")), "Raw access/affordability candidate rows."),
        summary_row("alb2008_outcome_semantics_facility_proxy_rows", sum(1 for row in rows if row["outcome_domain"].startswith("facility") or row["outcome_domain"].startswith("service_quality")), "Raw facility access/service-quality proxy rows."),
        summary_row("alb2008_outcome_semantics_need_candidate_rows", sum(1 for row in rows if row["outcome_domain"] == "need_proxy"), "Raw health-need proxy rows."),
        summary_row("alb2008_outcome_semantics_coping_candidate_rows", sum(1 for row in rows if row["outcome_domain"] == "coping_proxy"), "Raw health-payment coping proxy rows."),
        summary_row("alb2008_outcome_semantics_rows_with_value_labels", with_value_labels, "Candidate rows with SPSS value-label metadata."),
        summary_row("alb2008_outcome_semantics_rows_with_positive_numeric_values", positive_numeric, "Candidate rows with at least one positive numeric value."),
        summary_row("alb2008_outcome_semantics_rows_with_complete_household_merge_coverage", complete_merge, "Candidate rows whose source module covers all base households."),
        summary_row("alb2008_outcome_semantics_conditional_reason_rows", conditional_reason, "Reason variables that are conditional on access-barrier events and need denominator review."),
        summary_row("alb2008_outcome_semantics_outcome_ready_rows", 0, "No ALB_2008 raw value/semantics row is ready for final outcome promotion."),
        summary_row("alb2008_outcome_semantics_sdg382_ready_rows", 0, "No ALB_2008 row establishes the SDG 3.8.2 discretionary-budget denominator."),
        summary_row("alb2008_outcome_semantics_climate_linkage_ready_rows", 0, "No ALB_2008 row has verified timing/geography for climate linkage."),
        summary_row("alb2008_outcome_semantics_current_decision", DECISION, "Current fail-closed decision for ALB_2008 raw outcome semantics."),
    ]


def markdown_rows(rows: list[dict[str, str]], columns: list[str], limit: int = 65) -> str:
    lines = ["| " + " | ".join(columns) + " |", "|" + "|".join("---" for _ in columns) + "|"]
    for row in rows[:limit]:
        values = []
        for column in columns:
            value = (row.get(column, "") or "").replace("|", "/")
            if len(value) > 120:
                value = value[:117] + "..."
            values.append(value)
        lines.append("| " + " | ".join(values) + " |")
    if len(rows) > limit:
        lines.append("| ... | " + f"{len(rows) - limit} more rows omitted" + " | | | | | | | | | | | | | | |")
    return "\n".join(lines)


def write_report(rows: list[dict[str, str]], summary: list[dict[str, str]]) -> None:
    summary_table = "\n".join(f"| {row['metric']} | {row['value']} | {row['interpretation']} |" for row in summary)
    report = f"""# ALB_2008 Outcome Semantics Raw Value Audit

Status: temp-only raw value and semantics audit. This script reads ALB_2008 health modules and candidate core keys to document raw OOP/access/need/coping/service-quality evidence. It does not write `data/`, does not construct final CHE or SDG 3.8.2 outcomes, and does not approve climate linkage.

## Summary

| Metric | Value | Interpretation |
|---|---:|---|
{summary_table}

## Candidate Raw Variables

{markdown_rows(rows, ['outcome_domain', 'candidate_variable', 'source_file', 'raw_variable', 'raw_label', 'nonmissing_rows', 'distinct_values', 'min_value', 'max_value', 'positive_numeric_rows', 'value_label_examples', 'skip_pattern_status', 'unit_status', 'merge_key_status', 'promotion_status'], 70)}

## Interpretation

- ALB_2008 has observable raw OOP payment variables in `Modul_9A_health.sav`, split between four-week payment/gift items and twelve-month hospital/dentist payment/gift items.
- Gift variables and service-quality questions about money/gifts demanded are present, but their role in OOP or access definitions requires a documented policy definition and questionnaire review.
- `Modul_9B_health.sav` has labelled access and affordability variables for delayed care, referral nonattendance, refusal, cost, distance, and medicine-discount barriers. Several are conditional reason variables and cannot define denominators without skip-pattern review.
- `Modul_9C_health.sav` contributes facility location, cost, supply, waiting-time, and willingness-to-pay perceptions. These are useful mechanism or service-quality signals, not final UHC failure outcomes.
- ALB_2008 still lacks verified interview timing and has only coarse non-GPS geography, so climate linkage remains blocked even if outcome semantics improve.

## Machine-Readable Outputs

- `temp/alb2008_outcome_semantics_raw_value_audit.csv`
- `result/alb2008_outcome_semantics_raw_value_summary.csv`
"""
    REPORT_PATH.write_text(report, encoding="utf-8")


def main() -> None:
    ensure_dirs()
    rows = build_audit()
    summary = build_summary(rows)
    write_csv(AUDIT_PATH, rows, AUDIT_COLUMNS)
    write_csv(SUMMARY_PATH, summary, SUMMARY_COLUMNS)
    write_report(rows, summary)
    append_log(TEMP_DIR / "audit_log.md", f"Built ALB_2008 outcome semantics raw value audit rows={len(rows)}; decision={DECISION}.")
    print(f"ALB_2008 outcome semantics raw value audit rows={len(rows)}; decision={DECISION}.")


if __name__ == "__main__":
    main()
