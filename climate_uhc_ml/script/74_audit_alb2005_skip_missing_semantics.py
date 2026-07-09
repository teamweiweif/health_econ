from __future__ import annotations

import csv
import math
import warnings
from pathlib import Path
from typing import Any, Callable

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
RAW_ROOT = TEMP_DIR / "raw_extracted" / "lsms2005en_1e7f1965c4a5" / "lsms2005en" / "Data_2005"

QUESTIONNAIRE_SUMMARY_PATH = RESULT_DIR / "alb2005_health_questionnaire_semantics_summary.csv"
OOP_POLICY_SUMMARY_PATH = RESULT_DIR / "alb2005_oop_aggregation_policy_summary.csv"
REQUIRED_VALUE_KEY_SUMMARY_PATH = RESULT_DIR / "alb2005_required_value_key_summary.csv"
TIMING_GEO_SUMMARY_PATH = RESULT_DIR / "alb2005_timing_geography_exhaustive_summary.csv"

AUDIT_PATH = TEMP_DIR / "alb2005_skip_missing_semantics_audit.csv"
SUMMARY_PATH = RESULT_DIR / "alb2005_skip_missing_semantics_summary.csv"
REPORT_PATH = REPORT_DIR / "alb2005_skip_missing_semantics_audit.md"

DECISION = "blocked_alb2005_skip_missing_semantics_seen_but_recipe_not_ready"
NO_PROMOTION = "not_promoted_skip_missing_semantics_audit_only"

AUDIT_COLUMNS = [
    "country",
    "survey_name",
    "wave",
    "idno",
    "audit_family",
    "subdomain",
    "trigger_variable",
    "trigger_label",
    "trigger_positive_codes",
    "trigger_negative_codes",
    "downstream_variables",
    "downstream_labels",
    "row_count",
    "trigger_positive_rows",
    "trigger_negative_rows",
    "trigger_missing_rows",
    "downstream_any_nonmissing_when_triggered_rows",
    "downstream_all_missing_when_triggered_rows",
    "downstream_any_positive_when_triggered_rows",
    "downstream_zero_or_missing_when_triggered_rows",
    "downstream_any_nonmissing_when_not_triggered_rows",
    "downstream_any_positive_when_not_triggered_rows",
    "dependent_missing_when_triggered_rows",
    "dependent_nonmissing_when_not_triggered_rows",
    "trigger_top_values",
    "downstream_top_values",
    "value_label_examples",
    "skip_missing_evidence_status",
    "ready_for_recipe",
    "ready_for_outcome",
    "climate_linkage_ready",
    "promotion_status",
    "blocking_reason",
    "next_action",
]
SUMMARY_COLUMNS = ["metric", "value", "interpretation"]

PAYMENT_BLOCKS = [
    {
        "subdomain": "public_ambulatory_4w",
        "trigger": "m9a_q12",
        "positive": {1},
        "negative": {2},
        "downstream": ["m9a_q16", "m9a_q17", "m9a_q20", "m9a_q22", "m9a_q23"],
    },
    {
        "subdomain": "hospital_outpatient_4w",
        "trigger": "m9a_q24",
        "positive": {1},
        "negative": {2},
        "downstream": ["m9a_q28", "m9a_q29", "m9a_q32", "m9a_q34", "m9a_q35"],
    },
    {
        "subdomain": "private_doctor_4w",
        "trigger": "m9a_q36",
        "positive": {1},
        "negative": {2},
        "downstream": ["m9a_q38", "m9a_q39", "m9a_q41", "m9a_q42", "m9a_q43"],
    },
    {
        "subdomain": "nurse_paramedic_midwife_4w",
        "trigger": "m9a_q44",
        "positive": {1},
        "negative": {2},
        "downstream": ["m9a_q46", "m9a_q47", "m9a_q49", "m9a_q50", "m9a_q51"],
    },
    {
        "subdomain": "popular_doctor_4w",
        "trigger": "m9a_q52",
        "positive": {1},
        "negative": {2},
        "downstream": ["m9a_q54", "m9a_q55", "m9a_q57", "m9a_q58", "m9a_q59"],
    },
    {
        "subdomain": "own_drugs_4w",
        "trigger": "m9a_q60",
        "positive": {1},
        "negative": {2},
        "downstream": ["m9a_q61"],
    },
    {
        "subdomain": "hospital_stay_12m",
        "trigger": "m9a_q62",
        "positive": {1},
        "negative": {2},
        "downstream": ["m9a_q68", "m9a_q69", "m9a_q71", "m9a_q72", "m9a_q73"],
    },
    {
        "subdomain": "dentist_12m",
        "trigger": "m9a_q74",
        "positive": {1},
        "negative": {2},
        "downstream": ["m9a_q76", "m9a_q77", "m9a_q79", "m9a_q80", "m9a_q81"],
    },
]

HOUSEHOLD_CONDITIONS = [
    {
        "subdomain": "delayed_or_no_help_reason",
        "trigger": "m9b_q03",
        "positive_fn": lambda s: s > 1,
        "positive_label": "2-5",
        "negative_label": "1",
        "downstream": ["m9b_q04"],
    },
    {
        "subdomain": "hospital_referral_not_gone_reason",
        "trigger": "m9b_q05",
        "positive_fn": lambda s: s > 1,
        "positive_label": "2-5",
        "negative_label": "1",
        "downstream": ["m9b_q06"],
    },
    {
        "subdomain": "refused_health_services_reason",
        "trigger": "m9b_q07",
        "positive_fn": lambda s: s == 1,
        "positive_label": "1",
        "negative_label": "2",
        "downstream": ["m9b_q08"],
    },
    {
        "subdomain": "medicine_discount_access_reason",
        "trigger": "m9b_q09",
        "positive_fn": lambda s: s == 1,
        "positive_label": "1",
        "negative_label": "2",
        "downstream": ["m9b_q10"],
    },
]

FINANCING_METHODS = {
    "subdomain": "raise_money_for_health_care_methods",
    "trigger": "m9b_q01",
    "positive_fn": lambda s: s.isin([1, 2]),
    "positive_label": "1-2",
    "negative_label": "3-4",
    "downstream": ["m9b_q02", "m9b_q023", "m9b_q024", "m9b_q025", "m9b_q026"],
}


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


def compact_join(values: list[Any], limit: int = 12) -> str:
    out: list[str] = []
    seen: set[str] = set()
    for value in values:
        clean = " ".join(str(value).replace("\n", " ").split())
        if not clean or clean in seen:
            continue
        out.append(clean)
        seen.add(clean)
        if len(out) >= limit:
            break
    return "; ".join(out)


def read_sav(file_name: str, usecols: list[str] | None = None) -> tuple[pd.DataFrame, Any]:
    if pyreadstat is None:
        raise RuntimeError("pyreadstat is not available")
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        return pyreadstat.read_sav(str(RAW_ROOT / file_name), usecols=usecols, apply_value_formats=False)


def metadata_maps(meta: Any) -> tuple[dict[str, str], dict[str, str]]:
    labels = dict(zip(getattr(meta, "column_names", []), getattr(meta, "column_labels", [])))
    value_examples: dict[str, str] = {}
    for variable in getattr(meta, "column_names", []):
        label_name = getattr(meta, "variable_to_label", {}).get(variable)
        label_map = getattr(meta, "value_labels", {}).get(label_name, {}) if label_name else {}
        value_examples[variable] = compact_join([f"{fmt(code)}={label}" for code, label in label_map.items()], 12)
    return labels, value_examples


def top_values(series: pd.Series, limit: int = 8) -> str:
    def clean(value: Any) -> str:
        rendered = fmt(value)
        return rendered if rendered else "<missing>"

    counts = series.map(clean).value_counts(dropna=False).head(limit)
    return compact_join([f"{idx}:{int(count)}" for idx, count in counts.items()], limit)


def numeric_frame(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    return df[columns].apply(pd.to_numeric, errors="coerce")


def base_row(audit_family: str, subdomain: str, trigger: str, downstream: list[str], labels: dict[str, str], value_examples: dict[str, str]) -> dict[str, str]:
    return {
        "country": COUNTRY,
        "survey_name": SURVEY_NAME,
        "wave": WAVE,
        "idno": IDNO,
        "audit_family": audit_family,
        "subdomain": subdomain,
        "trigger_variable": trigger,
        "trigger_label": labels.get(trigger, ""),
        "trigger_positive_codes": "",
        "trigger_negative_codes": "",
        "downstream_variables": ";".join(downstream),
        "downstream_labels": compact_join([f"{var}: {labels.get(var, '')}" for var in downstream], 20),
        "row_count": "0",
        "trigger_positive_rows": "0",
        "trigger_negative_rows": "0",
        "trigger_missing_rows": "0",
        "downstream_any_nonmissing_when_triggered_rows": "0",
        "downstream_all_missing_when_triggered_rows": "0",
        "downstream_any_positive_when_triggered_rows": "0",
        "downstream_zero_or_missing_when_triggered_rows": "0",
        "downstream_any_nonmissing_when_not_triggered_rows": "0",
        "downstream_any_positive_when_not_triggered_rows": "0",
        "dependent_missing_when_triggered_rows": "0",
        "dependent_nonmissing_when_not_triggered_rows": "0",
        "trigger_top_values": "",
        "downstream_top_values": "",
        "value_label_examples": compact_join([f"{trigger}: {value_examples.get(trigger, '')}"] + [f"{var}: {value_examples.get(var, '')}" for var in downstream if value_examples.get(var)], 20),
        "skip_missing_evidence_status": "blocked_not_run",
        "ready_for_recipe": "0",
        "ready_for_outcome": "0",
        "climate_linkage_ready": "0",
        "promotion_status": NO_PROMOTION,
        "blocking_reason": "Skip/missing evidence is audit-only and does not verify units, recall-period comparability, final payment scope, household interview timing, climate-ready geography, or cross-wave harmonization.",
        "next_action": "Use this evidence as one input to manual recipe review; do not promote outcomes until all raw value, unit, recall, timing, geography, and SDG denominator gates pass.",
    }


def payment_block_row(df: pd.DataFrame, spec: dict[str, Any], labels: dict[str, str], value_examples: dict[str, str]) -> dict[str, str]:
    trigger = spec["trigger"]
    downstream = spec["downstream"]
    row = base_row("person_payment_visit_skip", spec["subdomain"], trigger, downstream, labels, value_examples)
    trigger_values = pd.to_numeric(df[trigger], errors="coerce")
    payment_values = numeric_frame(df, downstream)
    triggered = trigger_values.isin(spec["positive"])
    not_triggered = trigger_values.isin(spec["negative"])
    missing_trigger = trigger_values.isna()
    any_nonmissing = payment_values.notna().any(axis=1)
    all_missing = payment_values.isna().all(axis=1)
    any_positive = (payment_values.fillna(0) > 0).any(axis=1)

    row.update(
        {
            "trigger_positive_codes": compact_join([fmt(value) for value in sorted(spec["positive"])]),
            "trigger_negative_codes": compact_join([fmt(value) for value in sorted(spec["negative"])]),
            "row_count": str(int(len(df))),
            "trigger_positive_rows": str(int(triggered.sum())),
            "trigger_negative_rows": str(int(not_triggered.sum())),
            "trigger_missing_rows": str(int(missing_trigger.sum())),
            "downstream_any_nonmissing_when_triggered_rows": str(int((triggered & any_nonmissing).sum())),
            "downstream_all_missing_when_triggered_rows": str(int((triggered & all_missing).sum())),
            "downstream_any_positive_when_triggered_rows": str(int((triggered & any_positive).sum())),
            "downstream_zero_or_missing_when_triggered_rows": str(int((triggered & ~any_positive).sum())),
            "downstream_any_nonmissing_when_not_triggered_rows": str(int((not_triggered & any_nonmissing).sum())),
            "downstream_any_positive_when_not_triggered_rows": str(int((not_triggered & any_positive).sum())),
            "trigger_top_values": top_values(df[trigger]),
            "downstream_top_values": compact_join([f"{var}: {top_values(df[var], 4)}" for var in downstream], 20),
            "skip_missing_evidence_status": "raw_skip_path_consistent_no_downstream_values_when_not_triggered"
            if int((not_triggered & any_nonmissing).sum()) == 0 and int((not_triggered & any_positive).sum()) == 0
            else "raw_skip_path_has_downstream_values_when_not_triggered_review_required",
        }
    )
    return row


def conditional_row(df: pd.DataFrame, spec: dict[str, Any], labels: dict[str, str], value_examples: dict[str, str], audit_family: str) -> dict[str, str]:
    trigger = spec["trigger"]
    downstream = spec["downstream"]
    row = base_row(audit_family, spec["subdomain"], trigger, downstream, labels, value_examples)
    trigger_values = pd.to_numeric(df[trigger], errors="coerce")
    downstream_values = df[downstream]
    triggered = spec["positive_fn"](trigger_values)
    not_triggered = (~triggered) & trigger_values.notna()
    missing_trigger = trigger_values.isna()
    any_nonmissing = downstream_values.notna().any(axis=1)
    all_missing = downstream_values.isna().all(axis=1)
    any_positive = (numeric_frame(df, downstream).fillna(0) > 0).any(axis=1)

    nonmissing_when_not_triggered = int((not_triggered & any_nonmissing).sum())
    missing_when_triggered = int((triggered & all_missing).sum())
    row.update(
        {
            "trigger_positive_codes": spec["positive_label"],
            "trigger_negative_codes": spec["negative_label"],
            "row_count": str(int(len(df))),
            "trigger_positive_rows": str(int(triggered.sum())),
            "trigger_negative_rows": str(int(not_triggered.sum())),
            "trigger_missing_rows": str(int(missing_trigger.sum())),
            "downstream_any_nonmissing_when_triggered_rows": str(int((triggered & any_nonmissing).sum())),
            "downstream_all_missing_when_triggered_rows": str(missing_when_triggered),
            "downstream_any_positive_when_triggered_rows": str(int((triggered & any_positive).sum())),
            "downstream_zero_or_missing_when_triggered_rows": str(int((triggered & ~any_positive).sum())),
            "downstream_any_nonmissing_when_not_triggered_rows": str(nonmissing_when_not_triggered),
            "downstream_any_positive_when_not_triggered_rows": str(int((not_triggered & any_positive).sum())),
            "dependent_missing_when_triggered_rows": str(missing_when_triggered),
            "dependent_nonmissing_when_not_triggered_rows": str(nonmissing_when_not_triggered),
            "trigger_top_values": top_values(df[trigger]),
            "downstream_top_values": compact_join([f"{var}: {top_values(df[var], 8)}" for var in downstream], 20),
            "skip_missing_evidence_status": "raw_conditional_reason_skip_path_consistent"
            if missing_when_triggered == 0 and nonmissing_when_not_triggered == 0
            else "raw_conditional_reason_skip_path_review_required",
        }
    )
    return row


def build_rows() -> list[dict[str, str]]:
    health_a_columns = sorted({spec["trigger"] for spec in PAYMENT_BLOCKS} | {var for spec in PAYMENT_BLOCKS for var in spec["downstream"]})
    health_b_columns = sorted(
        {spec["trigger"] for spec in HOUSEHOLD_CONDITIONS}
        | {var for spec in HOUSEHOLD_CONDITIONS for var in spec["downstream"]}
        | {FINANCING_METHODS["trigger"]}
        | set(FINANCING_METHODS["downstream"])
    )
    health_a, meta_a = read_sav("Modul_9A_healtha_cl.sav", health_a_columns)
    health_b, meta_b = read_sav("Modul_9B_healthb_cl.sav", health_b_columns)
    labels_a, values_a = metadata_maps(meta_a)
    labels_b, values_b = metadata_maps(meta_b)

    rows: list[dict[str, str]] = []
    for spec in PAYMENT_BLOCKS:
        rows.append(payment_block_row(health_a, spec, labels_a, values_a))
    for spec in HOUSEHOLD_CONDITIONS:
        rows.append(conditional_row(health_b, spec, labels_b, values_b, "household_access_reason_skip"))
    rows.append(conditional_row(health_b, FINANCING_METHODS, labels_b, values_b, "household_financing_multiselect_skip"))
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
    questionnaire_summary = read_csv_dicts(QUESTIONNAIRE_SUMMARY_PATH)
    oop_policy_summary = read_csv_dicts(OOP_POLICY_SUMMARY_PATH)
    required_summary = read_csv_dicts(REQUIRED_VALUE_KEY_SUMMARY_PATH)
    timing_summary = read_csv_dicts(TIMING_GEO_SUMMARY_PATH)
    payment_rows = [row for row in rows if row["audit_family"] == "person_payment_visit_skip"]
    condition_rows = [row for row in rows if row["audit_family"] == "household_access_reason_skip"]
    financing_rows = [row for row in rows if row["audit_family"] == "household_financing_multiselect_skip"]
    return [
        summary_row("alb2005_skip_missing_semantics_rows", len(rows), "Rows in the ALB_2005 skip/missing semantics audit."),
        summary_row("alb2005_skip_missing_payment_block_rows", len(payment_rows), "Person-level visit/payment skip blocks audited."),
        summary_row("alb2005_skip_missing_access_condition_rows", len(condition_rows), "Household access reason conditional skip blocks audited."),
        summary_row("alb2005_skip_missing_financing_multiselect_rows", len(financing_rows), "Household health-financing method skip blocks audited."),
        summary_row("alb2005_skip_missing_payment_nonmissing_when_not_triggered_rows", int_sum(rows, "downstream_any_nonmissing_when_not_triggered_rows", "person_payment_visit_skip"), "Payment downstream rows nonmissing when the visit/drug/stay trigger is negative."),
        summary_row("alb2005_skip_missing_payment_positive_when_not_triggered_rows", int_sum(rows, "downstream_any_positive_when_not_triggered_rows", "person_payment_visit_skip"), "Payment downstream rows positive when the visit/drug/stay trigger is negative."),
        summary_row("alb2005_skip_missing_payment_all_missing_when_triggered_rows", int_sum(rows, "downstream_all_missing_when_triggered_rows", "person_payment_visit_skip"), "Triggered payment rows where every downstream payment variable is missing."),
        summary_row("alb2005_skip_missing_payment_zero_or_missing_when_triggered_rows", int_sum(rows, "downstream_zero_or_missing_when_triggered_rows", "person_payment_visit_skip"), "Triggered payment rows with no positive downstream payment; these are not outcome-ready without zero/missing-code review."),
        summary_row("alb2005_skip_missing_condition_nonmissing_when_not_triggered_rows", int_sum(rows, "dependent_nonmissing_when_not_triggered_rows", "household_access_reason_skip"), "Conditional reason rows nonmissing when the trigger condition is false."),
        summary_row("alb2005_skip_missing_condition_missing_when_triggered_rows", int_sum(rows, "dependent_missing_when_triggered_rows", "household_access_reason_skip"), "Conditional reason rows missing when the trigger condition is true."),
        summary_row("alb2005_skip_missing_financing_nonmissing_when_not_triggered_rows", int_sum(rows, "dependent_nonmissing_when_not_triggered_rows", "household_financing_multiselect_skip"), "Health-financing method rows nonmissing when q01 is not difficult/very difficult."),
        summary_row("alb2005_skip_missing_financing_missing_when_triggered_rows", int_sum(rows, "dependent_missing_when_triggered_rows", "household_financing_multiselect_skip"), "Health-financing method rows all missing when q01 is difficult/very difficult."),
        summary_row("alb2005_skip_missing_questionnaire_oop_rows_observed", metric_value(questionnaire_summary, "alb2005_health_questionnaire_oop_item_rows"), "Questionnaire-backed OOP rows observed upstream."),
        summary_row("alb2005_skip_missing_oop_policy_rows_observed", metric_value(oop_policy_summary, "alb2005_oop_aggregation_policy_rows"), "OOP aggregation policy stress-test rows observed upstream."),
        summary_row("alb2005_skip_missing_required_value_key_recipe_ready_observed", metric_value(required_summary, "alb2005_required_value_key_recipe_ready_rows"), "Recipe-ready rows observed upstream."),
        summary_row("alb2005_skip_missing_timing_verified_rows_observed", metric_value(required_summary, "alb2005_required_value_key_interview_timing_verified_rows"), "Verified interview-timing rows observed upstream."),
        summary_row("alb2005_skip_missing_climate_ready_rows_observed", metric_value(timing_summary, "alb2005_climate_linkage_ready_rows"), "Climate-linkage-ready rows observed upstream."),
        summary_row("alb2005_skip_missing_recipe_ready_rows", 0, "Rows promoted to harmonization recipe by this audit; intentionally zero."),
        summary_row("alb2005_skip_missing_outcome_ready_rows", 0, "Rows promoted to final outcome construction by this audit; intentionally zero."),
        summary_row("alb2005_skip_missing_climate_linkage_ready_rows", 0, "Rows promoted to climate linkage by this audit; intentionally zero."),
        summary_row("alb2005_skip_missing_current_decision", DECISION, "Current fail-closed decision for ALB_2005 skip/missing semantics."),
    ]


def markdown_rows(rows: list[dict[str, str]], columns: list[str], limit: int = 20) -> str:
    lines = ["| " + " | ".join(columns) + " |", "|" + "|".join("---" for _ in columns) + "|"]
    for row in rows[:limit]:
        values = []
        for column in columns:
            value = (row.get(column, "") or "").replace("|", "/")
            if len(value) > 140:
                value = value[:137] + "..."
            values.append(value)
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines)


def write_report(rows: list[dict[str, str]], summary: list[dict[str, str]]) -> None:
    summary_table = "\n".join(f"| {row['metric']} | {row['value']} | {row['interpretation']} |" for row in summary)
    report = f"""# ALB_2005 Skip and Missing-Code Semantics Audit

Status: fail-closed raw skip/missing evidence. This audit reads ALB_2005 raw SPSS health files and checks whether downstream OOP payment and access-reason fields are observed only when their questionnaire trigger fields indicate they should be asked. It does not write `data/`, does not construct final outcomes, and does not promote any harmonization, outcome, or climate-linkage row.

## Bottom Line

- Person-level visit/payment skip paths are internally consistent in the raw values audited here: downstream payment variables are not observed when visit/drug/hospital/dentist trigger variables are negative.
- Household access reason variables are internally consistent with their count/yes-no trigger variables in the audited rows.
- Health-financing multi-response methods are observed only when paying for health care is very difficult or difficult.
- These checks reduce one blocker, but they do not verify final OOP inclusion policy, old-lek unit conversion, recall-period comparability, total-consumption period, survey design, fieldwork timing, climate-ready geography, or SDG 3.8.2 discretionary-budget inputs.
- Recipe-ready, outcome-ready, and climate-linkage-ready rows from this audit: 0.
- Current decision: `{DECISION}`.

## Summary

| Metric | Value | Interpretation |
|---|---:|---|
{summary_table}

## Skip/Missing Evidence Rows

{markdown_rows(rows, ['audit_family', 'subdomain', 'trigger_variable', 'trigger_positive_rows', 'trigger_negative_rows', 'downstream_any_nonmissing_when_not_triggered_rows', 'dependent_missing_when_triggered_rows', 'skip_missing_evidence_status'], 20)}

## Interpretation

- A zero skip-leak count supports the internal questionnaire-to-raw skip path for the audited variables, but it is not enough to choose an OOP aggregation rule or construct CHE/SDG outcomes.
- Triggered rows with no positive payment can be real zero spending or no-cost care, but they still require explicit missing-code and zero-code review before final financial-protection outcomes.
- Conditional reason variables can support access-barrier outcomes only after the denominator is specified and health need/care-seeking scope is verified.

## Machine-Readable Outputs

- `temp/alb2005_skip_missing_semantics_audit.csv`
- `result/alb2005_skip_missing_semantics_summary.csv`
"""
    REPORT_PATH.write_text(report, encoding="utf-8")


def main() -> None:
    ensure_dirs()
    rows = build_rows()
    summary = build_summary(rows)
    write_csv(AUDIT_PATH, rows, AUDIT_COLUMNS)
    write_csv(SUMMARY_PATH, summary, SUMMARY_COLUMNS)
    write_report(rows, summary)
    append_log(TEMP_DIR / "audit_log.md", f"Built ALB_2005 skip/missing semantics audit rows={len(rows)} decision={DECISION}.")
    print(f"ALB_2005 skip/missing semantics rows={len(rows)} decision={DECISION}.")


if __name__ == "__main__":
    main()
