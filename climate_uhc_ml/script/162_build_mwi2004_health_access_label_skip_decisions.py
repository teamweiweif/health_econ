from __future__ import annotations

import os
import tempfile
from pathlib import Path, PurePosixPath
from typing import Any
from zipfile import ZipFile

import pandas as pd
import pyreadstat

from common import REPORT_DIR, RESULT_DIR, TEMP_DIR, append_log, ensure_dirs, write_csv


IDNO = "MWI_2004_IHS-II_v01_M"
COUNTRY = "Malawi"
WAVE = "2004-2005"
RAW_DIR = TEMP_DIR / "raw_downloads" / IDNO
ZIP_PATH = RAW_DIR / "MWI_2004_IHS-II_v01_M_Stata8.zip"

DECISION_PATH = RESULT_DIR / "mwi2004_health_access_label_skip_decisions.csv"
METRIC_PATH = TEMP_DIR / "mwi2004_health_access_skip_consistency_metrics.csv"
SUMMARY_PATH = RESULT_DIR / "mwi2004_health_access_label_skip_summary.csv"
REPORT_PATH = REPORT_DIR / "mwi2004_health_access_label_skip_decisions.md"
HANDOFF_PATH = RAW_DIR / "_MWI2004_HEALTH_ACCESS_LABEL_SKIP_DECISIONS.md"

HEALTH_COLUMNS = [
    "d04",
    "d07a",
    "d07b",
    "d08",
    "d09",
    "d10",
    "d11",
    "d15",
    "d17",
    "d18",
    "d20",
    "d21",
    "d26",
    "d27a",
    "d27b",
    "d36",
    "d37",
    "d38",
]

VARIABLE_ROLES = {
    "d04": "acute_illness_or_injury_need",
    "d07a": "care_seeking_action_problem_1",
    "d07b": "care_seeking_action_problem_2",
    "d08": "activity_limitation_from_recent_need",
    "d09": "activity_limitation_days",
    "d10": "other_household_member_activity_limitation",
    "d11": "other_household_member_activity_limitation_days",
    "d15": "hospitalization_need_last_12_months",
    "d17": "hospitalization_financing_coping",
    "d18": "traditional_healer_overnight_stay",
    "d20": "traditional_healer_financing_coping",
    "d21": "self_rated_health_change",
    "d26": "chronic_illness_need",
    "d27a": "chronic_illness_type_1",
    "d27b": "chronic_illness_type_2",
    "d36": "antenatal_care_access",
    "d37": "delivery_place",
    "d38": "delivery_attendant",
}

DECISION_COLUMNS = [
    "country",
    "wave",
    "idno",
    "member",
    "variable_name",
    "variable_label",
    "variable_role",
    "raw_value",
    "value_label",
    "raw_count",
    "construct_mapping",
    "proposed_indicator_use",
    "denominator_rule",
    "skip_rule",
    "acceptance_status",
    "remaining_blocker",
]

METRIC_COLUMNS = ["country", "wave", "idno", "metric", "value", "status", "interpretation"]
SUMMARY_COLUMNS = ["metric", "value", "interpretation"]


def clean(value: Any) -> str:
    if value is None:
        return ""
    return " ".join(str(value).split())


def fmt_value(value: Any) -> str:
    if value is None or pd.isna(value):
        return "Sysmiss"
    try:
        numeric = float(value)
        if numeric.is_integer():
            return str(int(numeric))
        return f"{numeric:.6g}"
    except (TypeError, ValueError):
        return clean(value)


def member_name(zip_path: Path, basename: str) -> str:
    with ZipFile(zip_path) as zf:
        for name in zf.namelist():
            if PurePosixPath(name).name.lower() == basename.lower():
                return name
    raise FileNotFoundError(f"{basename} not found in {zip_path}")


def read_member(zip_path: Path, basename: str, columns: list[str]) -> tuple[pd.DataFrame, Any]:
    member = member_name(zip_path, basename)
    with ZipFile(zip_path) as zf:
        payload = zf.read(member)
    fd, raw_name = tempfile.mkstemp(suffix=PurePosixPath(member).suffix or ".dta")
    raw_path = Path(raw_name)
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(payload)
        _, meta = pyreadstat.read_dta(str(raw_path), metadataonly=True)
        available = set(getattr(meta, "column_names", []) or [])
        usecols = [col for col in columns if col in available]
        return pyreadstat.read_dta(str(raw_path), apply_value_formats=False, usecols=usecols)
    finally:
        raw_path.unlink(missing_ok=True)


def variable_label(meta: Any, variable: str) -> str:
    labels = dict(zip(getattr(meta, "column_names", []) or [], getattr(meta, "column_labels", []) or []))
    return clean(labels.get(variable, ""))


def value_labels(meta: Any, variable: str) -> dict[Any, str]:
    labels = getattr(meta, "variable_value_labels", {}) or {}
    mapping = labels.get(variable, {})
    return mapping if isinstance(mapping, dict) else {}


def label_for(mapping: dict[Any, str], value: Any) -> str:
    if value in mapping:
        return clean(mapping[value])
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return ""
    for key, label in mapping.items():
        try:
            if float(key) == numeric:
                return clean(label)
        except (TypeError, ValueError):
            continue
    return ""


def values_matching(meta: Any, variable: str, needles: list[str]) -> set[float]:
    out: set[float] = set()
    for value, label in value_labels(meta, variable).items():
        text = clean(label).lower()
        if any(needle in text for needle in needles):
            try:
                out.add(float(value))
            except (TypeError, ValueError):
                pass
    return out


def classify(variable: str, label: str, value: Any) -> tuple[str, str, str, str, str, str]:
    text = clean(label).lower()
    role = VARIABLE_ROLES.get(variable, "review")
    if variable in {"d04", "d15", "d18", "d26", "d36"}:
        if text == "yes":
            return (
                f"{role}_yes",
                "candidate_denominator_or_event_signal",
                "include when the relevant construct is used",
                "binary yes/no field; check upstream universe before use",
                "mapping_ready_policy_pending",
                "Needs final construct inclusion rule and universe confirmation.",
            )
        if text == "no":
            return (
                f"{role}_no",
                "candidate_negative_or_no_event_signal",
                "exclude from positive numerator; may remain in denominator depending construct",
                "binary yes/no field; check upstream universe before use",
                "mapping_ready_policy_pending",
                "Needs final denominator and skip/universe rule.",
            )
    if variable in {"d07a", "d07b"}:
        if "did nothing" in text and "no money" in text:
            return (
                "forgone_care_financial_barrier_candidate",
                "candidate_access_failure_numerator",
                "illness/injury respondents with no-money no-action response",
                "should be conditional on d04==Yes; avoid double-counting d07a and d07b",
                "mapping_ready_double_count_policy_pending",
                "Need final double-count policy across problem 1 and problem 2 actions.",
            )
        if "did nothing" in text:
            return (
                "no_care_no_serious_need_or_other_no_action_candidate",
                "not_financial_access_failure_by_default",
                "illness/injury respondents; classify separately from no-money barrier",
                "should be conditional on d04==Yes; avoid double-counting d07a and d07b",
                "mapping_ready_policy_pending",
                "Need final nonfinancial/no-need classification rule.",
            )
        if "gvt health" in text or "pvt health" in text or "hospital" in text or "clinic" in text:
            return (
                "formal_care_sought_candidate",
                "candidate_care_sought_signal",
                "illness/injury respondents with formal facility care",
                "should be conditional on d04==Yes; care-seeking categories may be multi-response",
                "mapping_ready_policy_pending",
                "Need final provider grouping rule.",
            )
        if "grocery" in text or "medicine" in text or "trad" in text or "healer" in text:
            return (
                "informal_or_self_care_candidate",
                "candidate_care_action_not_formal_facility",
                "illness/injury respondents with self-care, medicine purchase, or traditional care",
                "should be conditional on d04==Yes; care-seeking categories may be multi-response",
                "mapping_ready_policy_pending",
                "Need final formal-vs-informal care grouping rule.",
            )
        if "no other action" in text:
            return (
                "no_second_action_candidate",
                "secondary_action_absence",
                "do not treat as independent access failure without d07a context",
                "applies mainly to second action field",
                "mapping_ready_policy_pending",
                "Need final d07b handling rule.",
            )
    if variable in {"d17", "d20"}:
        if text == "yes":
            return (
                "borrow_sell_assets_for_health_cost_yes",
                "candidate_financial_coping_signal",
                "use as financial coping severity/context, not CHE numerator",
                "conditional on corresponding hospitalization/traditional-healer event",
                "mapping_ready_policy_pending",
                "Need final coping-use rule.",
            )
        if text == "no":
            return (
                "borrow_sell_assets_for_health_cost_no",
                "candidate_no_coping_signal",
                "exclude from coping positive numerator",
                "conditional on corresponding hospitalization/traditional-healer event",
                "mapping_ready_policy_pending",
                "Need final coping denominator rule.",
            )
    if variable == "d37":
        if "hospital" in text or "clinic" in text or "health" in text:
            return (
                "facility_delivery_candidate",
                "maternal_access_context_signal",
                "maternal-care context only; not core double-failure unless maternal module retained",
                "conditional on childbirth universe",
                "mapping_ready_policy_pending",
                "Need maternal module inclusion rule.",
            )
        if "home" in text or "traditional" in text:
            return (
                "nonfacility_delivery_candidate",
                "maternal_access_context_signal",
                "maternal-care context only; not core double-failure unless maternal module retained",
                "conditional on childbirth universe",
                "mapping_ready_policy_pending",
                "Need maternal module inclusion rule.",
            )
    if variable == "d38":
        if "doctor" in text or "nurse" in text or "midwife" in text or "clinical" in text:
            return (
                "skilled_delivery_attendant_candidate",
                "maternal_access_context_signal",
                "maternal-care context only; not core double-failure unless maternal module retained",
                "conditional on childbirth universe",
                "mapping_ready_policy_pending",
                "Need maternal module inclusion rule.",
            )
    return (
        f"{role}_review",
        "context_or_review_only",
        "retain for manual construct review",
        "review raw universe and upstream skips before use",
        "requires_manual_review",
        "No automatic construct mapping accepted.",
    )


def metric(rows: list[dict[str, str]], name: str, value: Any, status: str, interpretation: str) -> None:
    rows.append(
        {
            "country": COUNTRY,
            "wave": WAVE,
            "idno": IDNO,
            "metric": name,
            "value": clean(value),
            "status": status,
            "interpretation": interpretation,
        }
    )


def markdown_table(rows: list[dict[str, str]], columns: list[str], limit: int = 30) -> str:
    if not rows:
        return "_No rows._"
    lines = ["| " + " | ".join(columns) + " |", "| " + " | ".join("---" for _ in columns) + " |"]
    for row in rows[:limit]:
        lines.append("| " + " | ".join(clean(row.get(column)).replace("|", "/") for column in columns) + " |")
    if len(rows) > limit:
        lines.append("| " + " | ".join("..." for _ in columns) + " |")
    return "\n".join(lines)


def count_action_rows(df: pd.DataFrame, meta: Any, needles: list[str]) -> int:
    total = 0
    for variable in ["d07a", "d07b"]:
        values = values_matching(meta, variable, needles)
        if values:
            total += int(pd.to_numeric(df[variable], errors="coerce").isin(values).sum())
    return total


def build_outputs() -> tuple[list[dict[str, str]], list[dict[str, str]], list[dict[str, str]]]:
    if not ZIP_PATH.exists():
        raise FileNotFoundError(f"Missing raw package: {ZIP_PATH}")

    df, meta = read_member(ZIP_PATH, "sec_d.dta", HEALTH_COLUMNS)
    decisions: list[dict[str, str]] = []
    for variable in HEALTH_COLUMNS:
        if variable not in df.columns:
            continue
        mapping = value_labels(meta, variable)
        if not mapping:
            continue
        counts = df[variable].value_counts(dropna=False)
        for raw_value, raw_count in counts.items():
            if pd.isna(raw_value):
                label = "Sysmiss"
                construct = f"{VARIABLE_ROLES.get(variable, 'review')}_system_missing"
                proposed = "missing_or_skip_review"
                denominator = "exclude unless skip/universe rule requires structural missing"
                skip = "requires upstream skip/universe review"
                status = "requires_manual_review"
                blocker = "System missing values require skip/universe classification."
            else:
                label = label_for(mapping, raw_value)
                construct, proposed, denominator, skip, status, blocker = classify(variable, label, raw_value)
            decisions.append(
                {
                    "country": COUNTRY,
                    "wave": WAVE,
                    "idno": IDNO,
                    "member": "sec_d.dta",
                    "variable_name": variable,
                    "variable_label": variable_label(meta, variable),
                    "variable_role": VARIABLE_ROLES.get(variable, "review"),
                    "raw_value": fmt_value(raw_value),
                    "value_label": label,
                    "raw_count": str(int(raw_count)),
                    "construct_mapping": construct,
                    "proposed_indicator_use": proposed,
                    "denominator_rule": denominator,
                    "skip_rule": skip,
                    "acceptance_status": status,
                    "remaining_blocker": blocker,
                }
            )

    metrics: list[dict[str, str]] = []
    d04 = pd.to_numeric(df["d04"], errors="coerce")
    d15 = pd.to_numeric(df["d15"], errors="coerce")
    d18 = pd.to_numeric(df["d18"], errors="coerce")
    d17 = pd.to_numeric(df["d17"], errors="coerce")
    d20 = pd.to_numeric(df["d20"], errors="coerce")
    d07a = pd.to_numeric(df["d07a"], errors="coerce")
    d07b = pd.to_numeric(df["d07b"], errors="coerce")

    d07a_leak = int(d07a.notna().where(d04 != 1, False).sum())
    d07b_leak = int(d07b.notna().where(d04 != 1, False).sum())
    d17_leak = int(d17.notna().where(d15 != 1, False).sum())
    d20_leak = int(d20.notna().where(d18 != 1, False).sum())
    skip_leakage = d07a_leak + d07b_leak + d17_leak + d20_leak

    no_money = count_action_rows(df, meta, ["no money"])
    formal = count_action_rows(df, meta, ["gvt health", "pvt health", "hospital", "clinic"])
    informal = count_action_rows(df, meta, ["grocery", "medicine", "trad", "healer"])
    did_nothing = count_action_rows(df, meta, ["did nothing"])

    metric(metrics, "sec_d_rows", len(df), "pass", "Rows read from the health module.")
    metric(metrics, "d04_illness_injury_yes_rows", int((d04 == 1).sum()), "pass", "Recent illness/injury need denominator candidate.")
    metric(metrics, "d07a_nonmissing_when_d04_yes", int(d07a.notna().where(d04 == 1, False).sum()), "pass", "Problem 1 action rows among recent illness/injury respondents.")
    metric(metrics, "d07b_nonmissing_when_d04_yes", int(d07b.notna().where(d04 == 1, False).sum()), "review", "Problem 2 action rows among recent illness/injury respondents.")
    metric(metrics, "d07a_skip_leakage_when_d04_not_yes", d07a_leak, "pass" if d07a_leak == 0 else "blocker", "Problem 1 action nonmissing outside d04==Yes.")
    metric(metrics, "d07b_skip_leakage_when_d04_not_yes", d07b_leak, "pass" if d07b_leak == 0 else "blocker", "Problem 2 action nonmissing outside d04==Yes.")
    metric(metrics, "care_action_no_money_rows", no_money, "review", "d07a/d07b rows whose value labels indicate did nothing/no money.")
    metric(metrics, "care_action_did_nothing_rows", did_nothing, "review", "d07a/d07b rows whose value labels indicate did nothing for any reason.")
    metric(metrics, "care_action_formal_facility_rows", formal, "review", "d07a/d07b rows mapped to formal health facility care.")
    metric(metrics, "care_action_informal_or_self_care_rows", informal, "review", "d07a/d07b rows mapped to medicine purchase, traditional care, or self/informal care.")
    metric(metrics, "d15_hospitalization_yes_rows", int((d15 == 1).sum()), "pass", "Hospitalization need/severity candidate.")
    metric(metrics, "d17_skip_leakage_when_d15_not_yes", d17_leak, "pass" if d17_leak == 0 else "blocker", "Borrow/sell assets for hospitalization nonmissing outside d15==Yes.")
    metric(metrics, "d18_traditional_healer_overnight_yes_rows", int((d18 == 1).sum()), "review", "Traditional healer overnight-stay candidate.")
    metric(metrics, "d20_skip_leakage_when_d18_not_yes", d20_leak, "pass" if d20_leak == 0 else "blocker", "Borrow/sell assets for traditional healer nonmissing outside d18==Yes.")
    metric(metrics, "d26_chronic_illness_yes_rows", int((pd.to_numeric(df["d26"], errors="coerce") == 1).sum()), "pass", "Chronic illness need denominator candidate.")
    metric(metrics, "total_skip_leakage_rows", skip_leakage, "pass" if skip_leakage == 0 else "blocker", "Aggregate skip leakage across d07a/d07b/d17/d20 checks.")

    label_rows = len(decisions)
    mapped_rows = sum(1 for row in decisions if row["acceptance_status"].startswith("mapping_ready"))
    manual_rows = sum(1 for row in decisions if row["acceptance_status"] == "requires_manual_review")
    decision_status = (
        "label_skip_mapping_ready_not_final_verified"
        if label_rows and skip_leakage == 0
        else "label_skip_mapping_has_skip_or_manual_review_blockers"
    )
    summary = [
        {"metric": "country_wave", "value": IDNO, "interpretation": "Country-wave covered by this health/access label-skip decision artifact."},
        {"metric": "label_decision_rows", "value": str(label_rows), "interpretation": "Variable-value rows with value labels and proposed construct mappings."},
        {"metric": "mapping_ready_rows", "value": str(mapped_rows), "interpretation": "Variable-value rows with an explicit mapping ready for policy review."},
        {"metric": "manual_review_rows", "value": str(manual_rows), "interpretation": "Variable-value rows still requiring manual review."},
        {"metric": "financial_barrier_no_money_rows", "value": str(no_money), "interpretation": "d07a/d07b rows mapped to no-money no-action candidate access failure."},
        {"metric": "formal_facility_care_rows", "value": str(formal), "interpretation": "d07a/d07b rows mapped to formal facility care."},
        {"metric": "informal_or_self_care_rows", "value": str(informal), "interpretation": "d07a/d07b rows mapped to informal/self-care actions."},
        {"metric": "total_skip_leakage_rows", "value": str(skip_leakage), "interpretation": "Aggregate skip leakage across d07a/d07b/d17/d20 checks."},
        {"metric": "health_access_label_skip_decision", "value": decision_status, "interpretation": "Decision for the health/access label-skip mapping layer; still not final raw-value verification."},
        {"metric": "data_write_gate_status", "value": "closed", "interpretation": "This artifact cannot write data or open modeling gates."},
    ]
    return decisions, metrics, summary


def write_report(decisions: list[dict[str, str]], metrics: list[dict[str, str]], summary: list[dict[str, str]]) -> None:
    report = f"""# Malawi 2004 Health Access Label And Skip Decisions

Dataset: `{IDNO}` - {COUNTRY} {WAVE}

This artifact maps health/access value labels from `sec_d.dta` into candidate
construct roles for illness/need, care-seeking, forgone care, hospitalization,
coping, chronic illness, and maternal-care context. It exports only labels,
counts, and aggregate skip metrics. It does not export raw person identifiers,
does not write to `data/`, and does not mark the wave as value-verified.

## Summary

{markdown_table(summary, ["metric", "value", "interpretation"], 20)}

## Skip Metrics

{markdown_table(metrics, ["metric", "value", "status", "interpretation"], 30)}

## Label Decisions

{markdown_table(decisions, ["variable_name", "raw_value", "value_label", "raw_count", "construct_mapping", "proposed_indicator_use", "acceptance_status"], 60)}

## Gate Decision

The label/skip layer is ready for policy review, but final health/access
verification remains blocked until person-join exceptions, double-counting of
`d07a`/`d07b`, formal-vs-informal care grouping, maternal module inclusion, and
missing/unit/recall rules are accepted.
"""
    REPORT_PATH.write_text(report, encoding="utf-8")
    HANDOFF_PATH.write_text(report, encoding="utf-8")


def main() -> None:
    ensure_dirs()
    decisions, metrics, summary = build_outputs()
    write_csv(DECISION_PATH, decisions, DECISION_COLUMNS)
    write_csv(METRIC_PATH, metrics, METRIC_COLUMNS)
    write_csv(SUMMARY_PATH, summary, SUMMARY_COLUMNS)
    write_report(decisions, metrics, summary)
    append_log(TEMP_DIR / "audit_log.md", f"Built Malawi 2004 health/access label-skip decisions for {IDNO}.")


if __name__ == "__main__":
    main()
