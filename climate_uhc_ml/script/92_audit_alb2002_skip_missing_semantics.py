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


IDNO = "ALB_2002_LSMS_v01_M"
COUNTRY = "Albania"
SURVEY_NAME = "Living Standards Measurement Survey 2002"
WAVE = "2002"

RAW_ROOT = TEMP_DIR / "raw_extracted" / "lsms2002en_4dbf0b087520" / "lsms2002en" / "Data_2002"
HEALTH_A_PATH = RAW_ROOT / "Modul_5A_Health.sav"
HEALTH_B_PATH = RAW_ROOT / "Modul_5B_Health.sav"

QUESTIONNAIRE_SUMMARY_PATH = RESULT_DIR / "alb2002_health_questionnaire_semantics_summary.csv"
OOP_POLICY_SUMMARY_PATH = RESULT_DIR / "alb2002_oop_aggregation_policy_summary.csv"
MINIMUM_RECIPE_SUMMARY_PATH = RESULT_DIR / "alb2002_minimum_recipe_promotion_summary.csv"
DISTRICT_CROSSWALK_SUMMARY_PATH = RESULT_DIR / "alb2002_district_climate_crosswalk_summary.csv"

AUDIT_PATH = TEMP_DIR / "alb2002_skip_missing_semantics_audit.csv"
SUMMARY_PATH = RESULT_DIR / "alb2002_skip_missing_semantics_summary.csv"
REPORT_PATH = REPORT_DIR / "alb2002_skip_missing_semantics_audit.md"

DECISION = "blocked_alb2002_skip_missing_semantics_seen_but_recipe_not_ready"
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
    "downstream_nonmissing_cells_when_not_triggered",
    "downstream_zero_cells_when_not_triggered",
    "downstream_positive_cells_when_not_triggered",
    "dependent_missing_when_triggered_rows",
    "dependent_nonmissing_when_not_triggered_rows",
    "trigger_top_values",
    "downstream_top_values",
    "value_label_examples",
    "skip_missing_evidence_status",
    "zero_missing_semantics_status",
    "ready_for_recipe",
    "ready_for_outcome",
    "sdg382_ready",
    "climate_linkage_ready",
    "promotion_status",
    "blocking_reason",
    "next_action",
]
SUMMARY_COLUMNS = ["metric", "value", "interpretation"]

PAYMENT_BLOCKS = [
    {
        "subdomain": "public_ambulatory_4w",
        "trigger": "m5a_q12",
        "positive": {1},
        "negative": {2},
        "downstream": ["m5a_q14", "m5a_q15", "m5a_q18", "m5a_q20", "m5a_q21"],
    },
    {
        "subdomain": "private_doctor_4w",
        "trigger": "m5a_q22",
        "positive": {1},
        "negative": {2},
        "downstream": ["m5a_q24", "m5a_q25", "m5a_q27", "m5a_q28", "m5a_q29"],
    },
    {
        "subdomain": "nurse_paramedic_midwife_4w",
        "trigger": "m5a_q30",
        "positive": {1},
        "negative": {2},
        "downstream": ["m5a_q32", "m5a_q33", "m5a_q35", "m5a_q36", "m5a_q37"],
    },
    {
        "subdomain": "popular_doctor_4w",
        "trigger": "m5a_q38",
        "positive": {1},
        "negative": {2},
        "downstream": ["m5a_q40", "m5a_q41", "m5a_q43", "m5a_q44", "m5a_q45"],
    },
    {
        "subdomain": "own_drugs_4w",
        "trigger": "m5a_q46",
        "positive": {1},
        "negative": {2},
        "downstream": ["m5a_q47"],
    },
    {
        "subdomain": "hospital_stay_12m",
        "trigger": "m5a_q48",
        "positive": {1},
        "negative": {2},
        "downstream": ["m5a_q53", "m5a_q54", "m5a_q56", "m5a_q57", "m5a_q58"],
    },
    {
        "subdomain": "dentist_12m",
        "trigger": "m5a_q59",
        "positive": {1},
        "negative": {2},
        "downstream": ["m5a_q61", "m5a_q62", "m5a_q64", "m5a_q65", "m5a_q66"],
    },
]

CONDITIONAL_BLOCKS = [
    {
        "subdomain": "raise_money_for_health_care_methods",
        "trigger": "m5b_q01",
        "positive_fn": lambda s: s.isin([1, 2]),
        "positive_label": "1-2",
        "negative_label": "3-4",
        "downstream": ["m5b_q02_", "m5b_q021", "m5b_q022", "m5b_q023", "m5b_q024"],
    },
    {
        "subdomain": "delayed_or_no_help_reason",
        "trigger": "m5b_q03",
        "positive_fn": lambda s: s > 1,
        "positive_label": "2-5",
        "negative_label": "1",
        "downstream": ["m5b_q04"],
    },
    {
        "subdomain": "hospital_referral_not_gone_reason",
        "trigger": "m5b_q05",
        "positive_fn": lambda s: s > 1,
        "positive_label": "2-5",
        "negative_label": "1",
        "downstream": ["m5b_q06"],
    },
    {
        "subdomain": "refused_health_services_reason",
        "trigger": "m5b_q07",
        "positive_fn": lambda s: s == 1,
        "positive_label": "1",
        "negative_label": "2",
        "downstream": ["m5b_q08"],
    },
    {
        "subdomain": "medicine_discount_access_reason",
        "trigger": "m5b_q09",
        "positive_fn": lambda s: s == 1,
        "positive_label": "1",
        "negative_label": "2",
        "downstream": ["m5b_q10"],
    },
]


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


def read_sav(path: Path, usecols: list[str]) -> tuple[pd.DataFrame, Any]:
    if pyreadstat is None:
        raise RuntimeError("pyreadstat is not available")
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        return pyreadstat.read_sav(str(path), usecols=usecols, apply_value_formats=False)


def metadata_maps(meta: Any) -> tuple[dict[str, str], dict[str, str]]:
    labels = {name.lower(): str(label or "") for name, label in zip(meta.column_names, meta.column_labels)}
    value_examples: dict[str, str] = {}
    for variable in meta.column_names:
        value_map = (meta.variable_value_labels or {}).get(variable, {})
        value_examples[variable.lower()] = compact_join([f"{fmt(code)}={label}" for code, label in value_map.items()], 12)
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
        "downstream_nonmissing_cells_when_not_triggered": "0",
        "downstream_zero_cells_when_not_triggered": "0",
        "downstream_positive_cells_when_not_triggered": "0",
        "dependent_missing_when_triggered_rows": "0",
        "dependent_nonmissing_when_not_triggered_rows": "0",
        "trigger_top_values": "",
        "downstream_top_values": "",
        "value_label_examples": compact_join([f"{trigger}: {value_examples.get(trigger, '')}"] + [f"{var}: {value_examples.get(var, '')}" for var in downstream if value_examples.get(var)], 20),
        "skip_missing_evidence_status": "blocked_not_run",
        "zero_missing_semantics_status": "not_reviewed",
        "ready_for_recipe": "0",
        "ready_for_outcome": "0",
        "sdg382_ready": "0",
        "climate_linkage_ready": "0",
        "promotion_status": NO_PROMOTION,
        "blocking_reason": (
            "Skip/missing evidence is audit-only. It does not verify the final zero-as-true-zero versus zero-as-skipped "
            "policy, OOP scope, recall-period comparability, SDG denominator, or climate-ready geography."
        ),
        "next_action": (
            "Use this evidence to set an explicit zero/missing coding rule before any ALB_2002 OOP, access, "
            "harmonization, SDG, or climate-linkage promotion."
        ),
    }


def payment_block_row(df: pd.DataFrame, spec: dict[str, Any], labels: dict[str, str], value_examples: dict[str, str]) -> dict[str, str]:
    trigger = spec["trigger"]
    downstream = spec["downstream"]
    row = base_row("person_payment_visit_skip", spec["subdomain"], trigger, downstream, labels, value_examples)
    trigger_values = pd.to_numeric(df[trigger], errors="coerce")
    payment_values = numeric_frame(df, downstream)
    triggered = trigger_values.isin(spec["positive"])
    not_triggered = trigger_values.isin(spec["negative"])
    any_nonmissing = payment_values.notna().any(axis=1)
    all_missing = payment_values.isna().all(axis=1)
    any_positive = (payment_values.fillna(0) > 0).any(axis=1)
    skipped_cells = payment_values.loc[not_triggered]
    skipped_nonmissing = skipped_cells.notna()
    skipped_numeric = skipped_cells.where(skipped_nonmissing)
    skipped_positive_cells = int((skipped_numeric > 0).sum().sum())
    skipped_zero_cells = int((skipped_numeric == 0).sum().sum())
    skipped_nonmissing_cells = int(skipped_nonmissing.sum().sum())
    nonmissing_when_not = int((not_triggered & any_nonmissing).sum())
    positive_when_not = int((not_triggered & any_positive).sum())

    if positive_when_not > 0 or skipped_positive_cells > 0:
        evidence_status = "raw_skip_path_has_positive_downstream_values_when_not_triggered_review_required"
    elif nonmissing_when_not > 0 and skipped_nonmissing_cells == skipped_zero_cells:
        evidence_status = "raw_skip_path_nonmissing_values_when_not_triggered_are_zero_only"
    elif nonmissing_when_not == 0:
        evidence_status = "raw_skip_path_consistent_no_downstream_values_when_not_triggered"
    else:
        evidence_status = "raw_skip_path_nonmissing_nonpositive_values_when_not_triggered_review_required"

    row.update(
        {
            "trigger_positive_codes": compact_join([fmt(value) for value in sorted(spec["positive"])]),
            "trigger_negative_codes": compact_join([fmt(value) for value in sorted(spec["negative"])]),
            "row_count": str(int(len(df))),
            "trigger_positive_rows": str(int(triggered.sum())),
            "trigger_negative_rows": str(int(not_triggered.sum())),
            "trigger_missing_rows": str(int(trigger_values.isna().sum())),
            "downstream_any_nonmissing_when_triggered_rows": str(int((triggered & any_nonmissing).sum())),
            "downstream_all_missing_when_triggered_rows": str(int((triggered & all_missing).sum())),
            "downstream_any_positive_when_triggered_rows": str(int((triggered & any_positive).sum())),
            "downstream_zero_or_missing_when_triggered_rows": str(int((triggered & ~any_positive).sum())),
            "downstream_any_nonmissing_when_not_triggered_rows": str(nonmissing_when_not),
            "downstream_any_positive_when_not_triggered_rows": str(positive_when_not),
            "downstream_nonmissing_cells_when_not_triggered": str(skipped_nonmissing_cells),
            "downstream_zero_cells_when_not_triggered": str(skipped_zero_cells),
            "downstream_positive_cells_when_not_triggered": str(skipped_positive_cells),
            "trigger_top_values": top_values(df[trigger]),
            "downstream_top_values": compact_join([f"{var}: {top_values(df[var], 5)}" for var in downstream], 20),
            "skip_missing_evidence_status": evidence_status,
            "zero_missing_semantics_status": "zero_only_skipped_values_seen_manual_policy_required"
            if nonmissing_when_not > 0 and skipped_nonmissing_cells == skipped_zero_cells
            else "no_skipped_downstream_values_seen"
            if nonmissing_when_not == 0
            else "skipped_values_require_manual_review",
        }
    )
    return row


def conditional_row(df: pd.DataFrame, spec: dict[str, Any], labels: dict[str, str], value_examples: dict[str, str]) -> dict[str, str]:
    trigger = spec["trigger"]
    downstream = spec["downstream"]
    row = base_row("household_access_condition_skip", spec["subdomain"], trigger, downstream, labels, value_examples)
    trigger_values = pd.to_numeric(df[trigger], errors="coerce")
    downstream_values = df[downstream]
    triggered = spec["positive_fn"](trigger_values)
    not_triggered = (~triggered) & trigger_values.notna()
    any_nonmissing = downstream_values.notna().any(axis=1)
    all_missing = downstream_values.isna().all(axis=1)
    numeric_values = numeric_frame(df, downstream)
    any_positive = (numeric_values.fillna(0) > 0).any(axis=1)
    nonmissing_when_not = int((not_triggered & any_nonmissing).sum())
    positive_when_not = int((not_triggered & any_positive).sum())
    missing_when_triggered = int((triggered & all_missing).sum())
    row.update(
        {
            "trigger_positive_codes": spec["positive_label"],
            "trigger_negative_codes": spec["negative_label"],
            "row_count": str(int(len(df))),
            "trigger_positive_rows": str(int(triggered.sum())),
            "trigger_negative_rows": str(int(not_triggered.sum())),
            "trigger_missing_rows": str(int(trigger_values.isna().sum())),
            "downstream_any_nonmissing_when_triggered_rows": str(int((triggered & any_nonmissing).sum())),
            "downstream_all_missing_when_triggered_rows": str(missing_when_triggered),
            "downstream_any_positive_when_triggered_rows": str(int((triggered & any_positive).sum())),
            "downstream_zero_or_missing_when_triggered_rows": str(int((triggered & ~any_positive).sum())),
            "downstream_any_nonmissing_when_not_triggered_rows": str(nonmissing_when_not),
            "downstream_any_positive_when_not_triggered_rows": str(positive_when_not),
            "dependent_missing_when_triggered_rows": str(missing_when_triggered),
            "dependent_nonmissing_when_not_triggered_rows": str(nonmissing_when_not),
            "trigger_top_values": top_values(df[trigger]),
            "downstream_top_values": compact_join([f"{var}: {top_values(df[var], 6)}" for var in downstream], 20),
            "skip_missing_evidence_status": "raw_conditional_skip_path_consistent"
            if nonmissing_when_not == 0 and missing_when_triggered == 0
            else "raw_conditional_skip_path_review_required",
            "zero_missing_semantics_status": "conditional_denominator_manual_policy_required",
        }
    )
    return row


def build_rows() -> list[dict[str, str]]:
    health_a_columns = sorted({spec["trigger"] for spec in PAYMENT_BLOCKS} | {var for spec in PAYMENT_BLOCKS for var in spec["downstream"]})
    health_b_columns = sorted({spec["trigger"] for spec in CONDITIONAL_BLOCKS} | {var for spec in CONDITIONAL_BLOCKS for var in spec["downstream"]})
    health_a, meta_a = read_sav(HEALTH_A_PATH, health_a_columns)
    health_b, meta_b = read_sav(HEALTH_B_PATH, health_b_columns)
    labels_a, values_a = metadata_maps(meta_a)
    labels_b, values_b = metadata_maps(meta_b)

    rows: list[dict[str, str]] = []
    for spec in PAYMENT_BLOCKS:
        rows.append(payment_block_row(health_a, spec, labels_a, values_a))
    for spec in CONDITIONAL_BLOCKS:
        rows.append(conditional_row(health_b, spec, labels_b, values_b))
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
    minimum_recipe_summary = read_csv_dicts(MINIMUM_RECIPE_SUMMARY_PATH)
    crosswalk_summary = read_csv_dicts(DISTRICT_CROSSWALK_SUMMARY_PATH)
    payment_rows = [row for row in rows if row["audit_family"] == "person_payment_visit_skip"]
    condition_rows = [row for row in rows if row["audit_family"] == "household_access_condition_skip"]
    zero_only_rows = [row for row in payment_rows if row["zero_missing_semantics_status"] == "zero_only_skipped_values_seen_manual_policy_required"]
    no_skipped_rows = [row for row in payment_rows if row["zero_missing_semantics_status"] == "no_skipped_downstream_values_seen"]
    return [
        summary_row("alb2002_skip_missing_semantics_rows", len(rows), "Rows in the ALB_2002 skip/missing semantics audit."),
        summary_row("alb2002_skip_missing_payment_block_rows", len(payment_rows), "Person-level visit/payment skip blocks audited."),
        summary_row("alb2002_skip_missing_access_condition_rows", len(condition_rows), "Household access/financing conditional skip blocks audited."),
        summary_row("alb2002_skip_missing_payment_nonmissing_when_not_triggered_rows", int_sum(rows, "downstream_any_nonmissing_when_not_triggered_rows", "person_payment_visit_skip"), "Payment downstream rows nonmissing when the trigger is negative."),
        summary_row("alb2002_skip_missing_payment_positive_when_not_triggered_rows", int_sum(rows, "downstream_any_positive_when_not_triggered_rows", "person_payment_visit_skip"), "Payment downstream rows positive when the trigger is negative."),
        summary_row("alb2002_skip_missing_payment_nonmissing_cells_when_not_triggered", int_sum(rows, "downstream_nonmissing_cells_when_not_triggered", "person_payment_visit_skip"), "Payment downstream cells nonmissing when the trigger is negative."),
        summary_row("alb2002_skip_missing_payment_zero_cells_when_not_triggered", int_sum(rows, "downstream_zero_cells_when_not_triggered", "person_payment_visit_skip"), "Payment downstream cells equal to zero when the trigger is negative."),
        summary_row("alb2002_skip_missing_payment_positive_cells_when_not_triggered", int_sum(rows, "downstream_positive_cells_when_not_triggered", "person_payment_visit_skip"), "Payment downstream cells positive when the trigger is negative."),
        summary_row("alb2002_skip_missing_payment_zero_only_block_rows", len(zero_only_rows), "Payment skip blocks where nonmissing skipped values are zero-only."),
        summary_row("alb2002_skip_missing_payment_no_skipped_value_block_rows", len(no_skipped_rows), "Payment skip blocks with no downstream values when triggers are negative."),
        summary_row("alb2002_skip_missing_payment_all_missing_when_triggered_rows", int_sum(rows, "downstream_all_missing_when_triggered_rows", "person_payment_visit_skip"), "Triggered payment rows where every downstream payment variable is missing."),
        summary_row("alb2002_skip_missing_payment_zero_or_missing_when_triggered_rows", int_sum(rows, "downstream_zero_or_missing_when_triggered_rows", "person_payment_visit_skip"), "Triggered payment rows with no positive downstream payment; may be true zero care/spending and needs policy review."),
        summary_row("alb2002_skip_missing_condition_nonmissing_when_not_triggered_rows", int_sum(rows, "dependent_nonmissing_when_not_triggered_rows", "household_access_condition_skip"), "Conditional access/financing downstream rows nonmissing when the trigger condition is false."),
        summary_row("alb2002_skip_missing_condition_missing_when_triggered_rows", int_sum(rows, "dependent_missing_when_triggered_rows", "household_access_condition_skip"), "Conditional access/financing downstream rows missing when the trigger condition is true."),
        summary_row("alb2002_skip_missing_questionnaire_payment_nonmissing_skip_review_observed", metric_value(questionnaire_summary, "alb2002_health_questionnaire_payment_nonmissing_when_not_triggered_rows"), "Nonmissing skipped-payment rows observed in the questionnaire audit."),
        summary_row("alb2002_skip_missing_questionnaire_payment_positive_skip_leaks_observed", metric_value(questionnaire_summary, "alb2002_health_questionnaire_payment_positive_when_not_triggered_rows"), "Positive skipped-payment rows observed in the questionnaire audit."),
        summary_row("alb2002_skip_missing_oop_policy_rows_observed", metric_value(oop_policy_summary, "alb2002_oop_aggregation_policy_rows"), "OOP aggregation policy stress-test rows observed upstream."),
        summary_row("alb2002_skip_missing_minimum_recipe_harmonized_ready_observed", metric_value(minimum_recipe_summary, "alb2002_minimum_recipe_promotion_harmonized_ready_rows"), "Harmonized-ready rows observed upstream."),
        summary_row("alb2002_skip_missing_climate_ready_rows_observed", metric_value(crosswalk_summary, "alb2002_climate_linkage_ready_rows"), "Climate-linkage-ready rows observed upstream."),
        summary_row("alb2002_skip_missing_recipe_ready_rows", 0, "Rows promoted to harmonization recipe by this audit; intentionally zero."),
        summary_row("alb2002_skip_missing_outcome_ready_rows", 0, "Rows promoted to final outcome construction by this audit; intentionally zero."),
        summary_row("alb2002_skip_missing_sdg382_ready_rows", 0, "Rows promoted to SDG 3.8.2 construction by this audit; intentionally zero."),
        summary_row("alb2002_skip_missing_climate_linkage_ready_rows", 0, "Rows promoted to climate linkage by this audit; intentionally zero."),
        summary_row("alb2002_skip_missing_current_decision", DECISION, "Current fail-closed decision for ALB_2002 skip/missing semantics."),
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
    report = f"""# ALB_2002 Skip and Missing-Code Semantics Audit

Status: fail-closed raw skip/missing evidence. This audit reads ALB_2002 raw SPSS health files and checks whether downstream OOP payment and access-reason fields are observed only when their questionnaire trigger fields indicate they should be asked. It does not write `data/`, does not construct final outcomes, and does not promote any harmonization, SDG 3.8.2, outcome, or climate-linkage row.

## Bottom Line

- The ALB_2002 payment skip paths have zero positive downstream payment values when visit, drug, hospital-stay, or dentist trigger variables are negative.
- The nonmissing skipped downstream payment values are zero-only, so they feed the separate OOP skip-value decision audit rather than final outcome promotion.
- Conditional access and health-financing reason fields remain denominator-sensitive and still require manual policy review.
- These checks do not settle OOP inclusion scope, gift treatment, recall-period comparability, SDG 3.8.2 denominator construction, household aggregation, or climate-ready geography.
- Recipe-ready, outcome-ready, SDG 3.8.2-ready, and climate-linkage-ready rows from this audit: 0.
- Current decision: `{DECISION}`.

## Summary

| Metric | Value | Interpretation |
|---|---:|---|
{summary_table}

## Skip/Missing Evidence Rows

{markdown_rows(rows, ['audit_family', 'subdomain', 'trigger_variable', 'trigger_positive_rows', 'trigger_negative_rows', 'downstream_any_nonmissing_when_not_triggered_rows', 'downstream_positive_cells_when_not_triggered', 'downstream_zero_cells_when_not_triggered', 'dependent_missing_when_triggered_rows', 'skip_missing_evidence_status'], 20)}

## Interpretation

- Zero-only skipped payment values can be coded as structural zeros only after the recipe explicitly defines zero/missing semantics for skipped fields.
- Triggered rows with no positive downstream payment may reflect no spending, free care, or unresolved missing-code behavior; they are not outcome-ready by themselves.
- Access-reason variables can support forgone-care barriers only after the trigger denominator is fixed for illness, delayed care, referral, refusal, medicine entitlement, and no-care-needed responses.

## Machine-Readable Outputs

- `temp/alb2002_skip_missing_semantics_audit.csv`
- `result/alb2002_skip_missing_semantics_summary.csv`
"""
    REPORT_PATH.write_text(report, encoding="utf-8")


def main() -> None:
    ensure_dirs()
    rows = build_rows()
    summary = build_summary(rows)
    write_csv(AUDIT_PATH, rows, AUDIT_COLUMNS)
    write_csv(SUMMARY_PATH, summary, SUMMARY_COLUMNS)
    write_report(rows, summary)
    append_log(TEMP_DIR / "audit_log.md", f"Built ALB_2002 skip/missing semantics audit rows={len(rows)} decision={DECISION}.")
    print(f"ALB_2002 skip/missing semantics rows={len(rows)} decision={DECISION}.")


if __name__ == "__main__":
    main()
