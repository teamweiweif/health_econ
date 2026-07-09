from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path
from typing import Any

from common import REPORT_DIR, RESULT_DIR, TEMP_DIR, append_log, ensure_dirs, write_csv


PLAN_PATH = TEMP_DIR / "outcome_denominator_plan.csv"
SPEC_PATH = RESULT_DIR / "outcome_specification_plan.csv"
SUMMARY_PATH = RESULT_DIR / "outcome_denominator_plan_summary.csv"
REPORT_PATH = REPORT_DIR / "outcome_denominator_plan.md"

PLAN_COLUMNS = [
    "quality_rank",
    "country",
    "survey_name",
    "wave",
    "idno",
    "outcome",
    "outcome_family",
    "formula_or_rule",
    "required_raw_concepts",
    "metadata_supported_concepts",
    "missing_metadata_concepts",
    "raw_verified_concepts",
    "external_inputs_required",
    "external_inputs_status",
    "reference_validation_source",
    "outcome_gate_status",
    "blocking_gap",
]

SPEC_COLUMNS = [
    "outcome",
    "outcome_family",
    "formula_or_rule",
    "required_harmonized_fields",
    "external_inputs_required",
    "audit_requirements",
    "priority_status",
]

SUMMARY_COLUMNS = ["metric", "value", "interpretation"]

OUTCOMES = [
    {
        "outcome": "sdg382_discretionary_40",
        "family": "financial_protection",
        "rule": "OOP health expenditure > 40% of household discretionary budget; discretionary budget = total consumption/income minus societal poverty line",
        "concepts": {"oop_health_expenditure", "total_consumption_or_income", "survey_weight"},
        "external": {"societal_poverty_line", "ppp_conversion", "cpi_or_price_adjustment"},
        "reference": "WHO/UN SDG 3.8.2 metadata plus HEFPI financial-protection validation context",
        "priority": "preferred_after_denominator_audit",
    },
    {
        "outcome": "che10_total_budget",
        "family": "financial_protection",
        "rule": "OOP health expenditure > 10% of total consumption or income",
        "concepts": {"oop_health_expenditure", "total_consumption_or_income", "survey_weight"},
        "external": {"che10_country_reference"},
        "reference": "World Bank/HEFPI CHE10 reference indicators where available",
        "priority": "primary_fallback_until_sdg382_denominator_verified",
    },
    {
        "outcome": "che25_total_budget",
        "family": "financial_protection",
        "rule": "OOP health expenditure > 25% of total consumption or income",
        "concepts": {"oop_health_expenditure", "total_consumption_or_income", "survey_weight"},
        "external": {"che25_country_reference"},
        "reference": "World Bank/HEFPI CHE25 reference indicators where available",
        "priority": "primary_fallback_until_sdg382_denominator_verified",
    },
    {
        "outcome": "oop_share_total",
        "family": "financial_protection",
        "rule": "OOP health expenditure / total consumption or income",
        "concepts": {"oop_health_expenditure", "total_consumption_or_income"},
        "external": set(),
        "reference": "internal distribution and HEFPI macro/context checks",
        "priority": "diagnostic_continuous_outcome",
    },
    {
        "outcome": "log_oop_plus_one",
        "family": "financial_protection",
        "rule": "log(OOP health expenditure + 1), using raw local-currency units after recall-period checks",
        "concepts": {"oop_health_expenditure"},
        "external": set(),
        "reference": "internal distribution check",
        "priority": "diagnostic_continuous_outcome",
    },
    {
        "outcome": "capacity_to_pay_40",
        "family": "financial_protection",
        "rule": "OOP health expenditure > 40% of capacity to pay; construct only if capacity/subsistence denominator is documented",
        "concepts": {"oop_health_expenditure", "total_consumption_or_income", "survey_weight"},
        "external": {"capacity_to_pay_method"},
        "reference": "older WHO/World Bank financial-protection method, if denominator is defensible",
        "priority": "secondary_after_method_audit",
    },
    {
        "outcome": "impoverishing_health_spending",
        "family": "financial_protection",
        "rule": "Household above poverty line before OOP and below after OOP",
        "concepts": {"oop_health_expenditure", "total_consumption_or_income", "survey_weight"},
        "external": {"poverty_line", "ppp_conversion", "cpi_or_price_adjustment"},
        "reference": "HEFPI impoverishment indicators and World Bank poverty-line context",
        "priority": "secondary_after_poverty_line_audit",
    },
    {
        "outcome": "forgone_care_conditional_need",
        "family": "access",
        "rule": "Health need observed and care was not sought",
        "concepts": {"health_need", "care_or_barrier", "survey_weight"},
        "external": set(),
        "reference": "survey module definitions only; keep separate from financial sample if no budget/OOP",
        "priority": "primary_access_outcome",
    },
    {
        "outcome": "forgone_care_cost_barrier",
        "family": "access",
        "rule": "Health need or non-care episode with cost as reason for not seeking care",
        "concepts": {"health_need", "care_or_barrier", "survey_weight"},
        "external": set(),
        "reference": "survey module definitions only",
        "priority": "access_barrier_outcome",
    },
    {
        "outcome": "forgone_care_distance_barrier",
        "family": "access",
        "rule": "Health need or non-care episode with distance/transport as reason for not seeking care",
        "concepts": {"health_need", "care_or_barrier", "survey_weight"},
        "external": set(),
        "reference": "survey module definitions only",
        "priority": "access_barrier_outcome",
    },
    {
        "outcome": "forgone_care_supply_barrier",
        "family": "access",
        "rule": "Health need or non-care episode with provider/drug/staff/facility availability as reason for not seeking care",
        "concepts": {"health_need", "care_or_barrier", "survey_weight"},
        "external": set(),
        "reference": "survey module definitions only",
        "priority": "access_barrier_outcome",
    },
    {
        "outcome": "delayed_or_unmet_care",
        "family": "access",
        "rule": "Delayed care or unmet care, only where an exact survey module supports this construct",
        "concepts": {"health_need", "care_or_barrier", "survey_weight"},
        "external": set(),
        "reference": "survey module definitions only; do not proxy if module only supports general care-seeking",
        "priority": "secondary_access_outcome_if_exact_module_exists",
    },
    {
        "outcome": "uhc_double_failure",
        "family": "composite",
        "rule": "Financial hardship OR forgone care conditional on need",
        "concepts": {"oop_health_expenditure", "total_consumption_or_income", "health_need", "care_or_barrier", "survey_weight"},
        "external": {"che10_country_reference", "che25_country_reference"},
        "reference": "composite constructed only after separate financial/access outcomes pass event-rate and comparability checks",
        "priority": "secondary_until_10_country_waves_pass",
    },
    {
        "outcome": "financial_only_failure",
        "family": "composite",
        "rule": "Financial hardship observed and no observed forgone care",
        "concepts": {"oop_health_expenditure", "total_consumption_or_income", "health_need", "care_or_barrier", "survey_weight"},
        "external": {"che10_country_reference", "che25_country_reference"},
        "reference": "construct only after financial and access outcomes are separately audited",
        "priority": "secondary_composite",
    },
    {
        "outcome": "access_only_failure",
        "family": "composite",
        "rule": "Forgone care conditional on need and no observed catastrophic OOP",
        "concepts": {"oop_health_expenditure", "total_consumption_or_income", "health_need", "care_or_barrier", "survey_weight"},
        "external": {"che10_country_reference", "che25_country_reference"},
        "reference": "construct only after financial and access outcomes are separately audited",
        "priority": "secondary_composite",
    },
    {
        "outcome": "both_financial_and_access_failure",
        "family": "composite",
        "rule": "Financial hardship AND forgone care conditional on need",
        "concepts": {"oop_health_expenditure", "total_consumption_or_income", "health_need", "care_or_barrier", "survey_weight"},
        "external": {"che10_country_reference", "che25_country_reference"},
        "reference": "composite constructed only after separate financial/access outcomes pass event-rate and comparability checks",
        "priority": "secondary_composite",
    },
    {
        "outcome": "coping_failure",
        "family": "mechanism_or_composite",
        "rule": "Borrowing, selling assets, or reducing essential spending due to health costs if module supports it",
        "concepts": {"shocks_or_livelihood", "survey_weight"},
        "external": set(),
        "reference": "survey module definitions only; do not force where health-specific coping is absent",
        "priority": "mechanism_only_if_health_specific",
    },
]

EXTERNAL_SOURCE_MAP = {
    "societal_poverty_line": {"poverty_line_context", "hefpi_bulk_csv_reference"},
    "poverty_line": {"poverty_line_context", "hefpi_bulk_csv_reference"},
    "ppp_conversion": {"ppp_conversion_context"},
    "cpi_or_price_adjustment": {"cpi_context"},
    "che10_country_reference": {"che10_country_validation", "hefpi_bulk_csv_reference"},
    "che25_country_reference": {"che25_country_validation", "hefpi_bulk_csv_reference"},
    "capacity_to_pay_method": {"hefpi_bulk_csv_reference", "country_validation_portal"},
}


def read_csv_dicts(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def source_roles_ready() -> set[str]:
    rows = read_csv_dicts(TEMP_DIR / "validation_reference_source_probe.csv")
    return {
        row.get("source_role", "")
        for row in rows
        if row.get("status") in {"reachable_snapshot_saved", "indicator_metadata_available"}
    }


def concept_rows_by_idno() -> dict[str, dict[str, dict[str, str]]]:
    out: dict[str, dict[str, dict[str, str]]] = {}
    for row in read_csv_dicts(TEMP_DIR / "raw_ingestion_concept_checklist.csv"):
        out.setdefault(row.get("idno", ""), {})[row.get("concept", "")] = row
    return out


def external_status(required: set[str], ready_roles: set[str]) -> tuple[str, list[str]]:
    missing = []
    for item in required:
        roles = EXTERNAL_SOURCE_MAP.get(item, set())
        if roles and ready_roles.intersection(roles):
            continue
        missing.append(item)
    if not required:
        return "not_required", []
    return ("source_probe_ready" if not missing else "source_probe_missing", missing)


def plan_rows() -> list[dict[str, str]]:
    priorities = read_csv_dicts(TEMP_DIR / "metadata_quality_download_priority.csv")
    concepts_by_idno = concept_rows_by_idno()
    ready_roles = source_roles_ready()
    rows = []
    for priority in priorities:
        idno = priority.get("idno", "")
        concept_map = concepts_by_idno.get(idno, {})
        for outcome in OUTCOMES:
            required = outcome["concepts"]
            supported = []
            raw_verified = []
            missing = []
            for concept in sorted(required):
                row = concept_map.get(concept, {})
                if row.get("metadata_support_status") == "metadata_supported_raw_unverified":
                    supported.append(concept)
                else:
                    missing.append(concept)
                if row.get("raw_verification_status") == "raw_variables_inspected":
                    raw_verified.append(concept)
            ext_status, missing_external = external_status(outcome["external"], ready_roles)
            if missing:
                gate = "metadata_incomplete_for_outcome"
                gap = "metadata missing or weak for " + ";".join(missing)
            elif len(raw_verified) < len(required):
                gate = "metadata_ready_raw_unverified"
                gap = "raw harmonized variables must be inspected and mapped before outcome construction"
            elif missing_external:
                gate = "external_denominator_inputs_missing"
                gap = "external inputs missing: " + ";".join(missing_external)
            else:
                gate = "ready_for_harmonized_outcome_construction"
                gap = "requires harmonized data write and outcome audit before interpretation"
            rows.append(
                {
                    "quality_rank": priority.get("quality_rank", ""),
                    "country": priority.get("country", ""),
                    "survey_name": priority.get("survey_name", ""),
                    "wave": priority.get("wave", ""),
                    "idno": idno,
                    "outcome": outcome["outcome"],
                    "outcome_family": outcome["family"],
                    "formula_or_rule": outcome["rule"],
                    "required_raw_concepts": ";".join(sorted(required)),
                    "metadata_supported_concepts": ";".join(supported),
                    "missing_metadata_concepts": ";".join(missing),
                    "raw_verified_concepts": ";".join(raw_verified),
                    "external_inputs_required": ";".join(sorted(outcome["external"])),
                    "external_inputs_status": ext_status,
                    "reference_validation_source": outcome["reference"],
                    "outcome_gate_status": gate,
                    "blocking_gap": gap,
                }
            )
    return rows


def spec_rows() -> list[dict[str, str]]:
    rows = []
    for outcome in OUTCOMES:
        fields = []
        for concept in sorted(outcome["concepts"]):
            if concept == "oop_health_expenditure":
                fields.append("oop_health_expenditure")
            elif concept == "total_consumption_or_income":
                fields.append("total_consumption or total_income")
            elif concept == "survey_weight":
                fields.append("household_weight or person_weight")
            elif concept == "health_need":
                fields.append("illness_or_injury_need")
            elif concept == "care_or_barrier":
                fields.append("care_sought/care_not_sought or reason_not_sought_*")
            elif concept == "shocks_or_livelihood":
                fields.append("coping_borrowed/coping_sold_assets/food_insecurity or health-specific coping variables")
        rows.append(
            {
                "outcome": outcome["outcome"],
                "outcome_family": outcome["family"],
                "formula_or_rule": outcome["rule"],
                "required_harmonized_fields": ";".join(fields),
                "external_inputs_required": ";".join(sorted(outcome["external"])),
                "audit_requirements": "raw variable lineage; unit/recall-period check; missingness; event rate; weighted prevalence; country-wave comparability",
                "priority_status": outcome["priority"],
            }
        )
    return rows


def summary_rows(plans: list[dict[str, str]], specs: list[dict[str, str]]) -> list[dict[str, str]]:
    gate_counts = Counter(row.get("outcome_gate_status", "") for row in plans)
    family_counts = Counter(row.get("outcome_family", "") for row in plans)
    external_counts = Counter(row.get("external_inputs_status", "") for row in plans)
    rows = [
        {"metric": "outcome_plan_rows", "value": str(len(plans)), "interpretation": "Dataset-outcome readiness rows across quality-screened country-waves."},
        {"metric": "outcome_specification_rows", "value": str(len(specs)), "interpretation": "Unique outcome formula/specification rows."},
        {"metric": "metadata_ready_raw_unverified_outcome_rows", "value": str(gate_counts.get("metadata_ready_raw_unverified", 0)), "interpretation": "Outcome rows with metadata support but no raw verification."},
        {"metric": "ready_for_harmonized_outcome_construction_rows", "value": str(gate_counts.get("ready_for_harmonized_outcome_construction", 0)), "interpretation": "Outcome rows with raw-verified required concepts and source-probed external inputs."},
        {"metric": "external_source_probe_ready_rows", "value": str(external_counts.get("source_probe_ready", 0)), "interpretation": "Rows whose external validation/denominator source category has been probed."},
    ]
    for gate, count in sorted(gate_counts.items()):
        rows.append({"metric": f"gate_count_{gate}", "value": str(count), "interpretation": "Outcome construction gate status count."})
    for family, count in sorted(family_counts.items()):
        rows.append({"metric": f"family_count_{family}", "value": str(count), "interpretation": "Outcome family row count."})
    return rows


def markdown_count_table(counter: Counter[str], label: str) -> str:
    lines = [f"| {label} | Count |", "|---|---:|"]
    for key, count in counter.most_common():
        lines.append(f"| {key or 'blank'} | {count} |")
    return "\n".join(lines)


def write_report(plans: list[dict[str, str]], specs: list[dict[str, str]], summaries: list[dict[str, str]]) -> None:
    gate_counts = Counter(row.get("outcome_gate_status", "") for row in plans)
    family_counts = Counter(row.get("outcome_family", "") for row in plans)
    external_counts = Counter(row.get("external_inputs_status", "") for row in plans)
    lines = [
        "# Outcome Denominator Plan",
        "",
        "Status: outcome construction is planned but not executed. This report separates metadata-supported outcome readiness from raw-verified outcome construction.",
        "",
        "## Outcome Gate Counts",
        "",
        markdown_count_table(gate_counts, "Outcome gate status"),
        "",
        "## Outcome Families",
        "",
        markdown_count_table(family_counts, "Outcome family"),
        "",
        "## External Input Status",
        "",
        markdown_count_table(external_counts, "External input status"),
        "",
        "## Summary Metrics",
        "",
        "| Metric | Value | Interpretation |",
        "|---|---:|---|",
    ]
    for row in summaries:
        lines.append(f"| {row['metric']} | {row['value']} | {row['interpretation']} |")
    lines.extend(
        [
            "",
            "## Guardrail",
            "",
            "CHE10/CHE25 and access outcomes can be prioritized once raw OOP, budget, need/access, weights, and recall periods are verified. SDG 3.8.2, capacity-to-pay, and impoverishment outcomes require additional denominator choices such as societal poverty line, PPP, CPI/price adjustment, or capacity-to-pay method. None of these outcomes should be interpreted until `data/household_outcomes.*` exists and `result/outcome_audit.csv` reports constructed rows with event-rate and missingness checks.",
            "",
            "## Machine-Readable Outputs",
            "",
            "- `temp/outcome_denominator_plan.csv`",
            "- `result/outcome_specification_plan.csv`",
            "- `result/outcome_denominator_plan_summary.csv`",
        ]
    )
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    ensure_dirs()
    plans = plan_rows()
    specs = spec_rows()
    summaries = summary_rows(plans, specs)
    write_csv(PLAN_PATH, plans, PLAN_COLUMNS)
    write_csv(SPEC_PATH, specs, SPEC_COLUMNS)
    write_csv(SUMMARY_PATH, summaries, SUMMARY_COLUMNS)
    write_report(plans, specs, summaries)
    ready = sum(1 for row in plans if row.get("outcome_gate_status") == "ready_for_harmonized_outcome_construction")
    metadata_ready = sum(1 for row in plans if row.get("outcome_gate_status") == "metadata_ready_raw_unverified")
    append_log(TEMP_DIR / "audit_log.md", f"Outcome denominator plan rows={len(plans)} specs={len(specs)} metadata_ready_raw_unverified={metadata_ready} ready_for_construction={ready}.")
    print(f"Outcome denominator plan rows={len(plans)} specs={len(specs)} metadata_ready_raw_unverified={metadata_ready} ready_for_construction={ready}.")


if __name__ == "__main__":
    main()
