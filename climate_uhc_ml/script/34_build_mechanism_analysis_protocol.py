from __future__ import annotations

import csv
from collections import Counter, defaultdict
from pathlib import Path

from common import REPORT_DIR, RESULT_DIR, TEMP_DIR, append_log, ensure_dirs, write_csv


BUNDLES_PATH = TEMP_DIR / "minimum_viable_download_bundles.csv"
CONCEPT_PATH = TEMP_DIR / "raw_ingestion_concept_checklist.csv"
RAW_VARIABLE_PATH = TEMP_DIR / "raw_schema_inventory" / "raw_variable_catalog.csv"
HARMONIZATION_READINESS_PATH = RESULT_DIR / "harmonization_readiness_matrix.csv"
CLIMATE_READINESS_PATH = RESULT_DIR / "climate_linkage_readiness.csv"
OUTCOME_PLAN_PATH = TEMP_DIR / "outcome_denominator_plan.csv"
MODELING_PLAN_PATH = TEMP_DIR / "modeling_identification_plan.csv"

REQUIREMENTS_PATH = TEMP_DIR / "mechanism_variable_requirements.csv"
PATHWAY_PROTOCOL_PATH = RESULT_DIR / "mechanism_pathway_protocol.csv"
READINESS_PATH = RESULT_DIR / "mechanism_readiness_matrix.csv"
SUMMARY_PATH = RESULT_DIR / "mechanism_analysis_protocol_summary.csv"
REPORT_PATH = REPORT_DIR / "mechanism_analysis_protocol.md"

REQUIREMENT_COLUMNS = [
    "bundle_rank",
    "country",
    "survey_name",
    "wave",
    "idno",
    "mechanism_pathway",
    "pathway_role",
    "concept",
    "required",
    "metadata_support_status",
    "high_confidence_rows",
    "moderate_confidence_rows",
    "candidate_files",
    "candidate_variables",
    "raw_verification_status",
    "current_gate_status",
    "blocking_gap",
    "post_treatment_guardrail",
]

PATHWAY_COLUMNS = [
    "mechanism_pathway",
    "causal_role",
    "minimum_inputs",
    "timing_rule",
    "allowed_analysis",
    "prohibited_use",
    "current_status",
    "evidence_required_before_claim",
    "interpretation_if_unavailable_or_failed",
]

READINESS_COLUMNS = [
    "bundle_rank",
    "country",
    "survey_name",
    "wave",
    "idno",
    "mechanism_pathway",
    "required_concept_rows",
    "recommended_concept_rows",
    "raw_verified_required_rows",
    "blocked_required_rows",
    "metadata_missing_required_rows",
    "harmonization_status",
    "climate_linkage_status",
    "outcome_status",
    "modeling_status",
    "readiness_status",
    "next_action",
]

SUMMARY_COLUMNS = ["metric", "value", "interpretation"]

BASE_REQUIRED = [
    ("household_id", "yes"),
    ("survey_timing", "yes"),
    ("climate_geography", "yes"),
]

BASE_RECOMMENDED = [
    ("survey_weight", "recommended"),
    ("psu_cluster", "recommended"),
    ("strata", "recommended"),
    ("demographics", "recommended"),
]

PATHWAYS = [
    {
        "mechanism_pathway": "income_consumption_decline",
        "causal_role": "mediator_or_secondary_outcome",
        "pathway_role": "economic_resource_channel",
        "concepts": BASE_REQUIRED + [("total_consumption_or_income", "yes")] + BASE_RECOMMENDED,
        "minimum_inputs": "total consumption or income, household ID, survey timing, climate geography",
        "timing_rule": "consumption/income must be measured after or during the shock exposure window; never include as a main-effect control if post-shock",
        "allowed_analysis": "separate reduced-form model of climate shock on consumption/income; heterogeneity descriptor only if pre-shock",
        "prohibited_use": "do not control for post-shock consumption/income in the main UHC failure climate-effect model",
        "evidence_required": "raw variable values, units, recall periods, deflators if used, timing relative to exposure, and household-level lineage",
        "fail_interpretation": "economic mechanism unsupported for that country-wave; do not force a pathway claim",
    },
    {
        "mechanism_pathway": "food_insecurity",
        "causal_role": "mediator_or_secondary_outcome",
        "pathway_role": "food_security_channel",
        "concepts": BASE_REQUIRED + [("shocks_or_livelihood", "yes")] + BASE_RECOMMENDED,
        "minimum_inputs": "food insecurity, crop/food shock, coping, or livelihood variables plus verified timing and geography",
        "timing_rule": "food insecurity must be contemporaneous or post-exposure; pre-exposure food security may be a moderator if clearly pre-shock",
        "allowed_analysis": "separate pathway model and subgroup description where modules support the construct",
        "prohibited_use": "do not relabel general asset or agriculture variables as food insecurity without raw wording support",
        "evidence_required": "raw questionnaire wording, response categories, recall period, and value distribution",
        "fail_interpretation": "food insecurity pathway remains untested in that country-wave",
    },
    {
        "mechanism_pathway": "health_need_illness",
        "causal_role": "mediator_or_secondary_outcome",
        "pathway_role": "health_need_channel",
        "concepts": BASE_REQUIRED + [("health_need", "yes")] + BASE_RECOMMENDED,
        "minimum_inputs": "illness, injury, symptoms, or health-need denominator with verified recall period",
        "timing_rule": "need window must be compatible with climate exposure lag; future need cannot be used to define treatment",
        "allowed_analysis": "climate shock to health-need reduced-form pathway and need-denominator audit",
        "prohibited_use": "do not mix person-level and household-level need denominators without explicit aggregation",
        "evidence_required": "raw skip patterns, denominator, recall period, person/household level, and missing-value handling",
        "fail_interpretation": "health-need channel cannot be separated from access or financial-protection outcomes",
    },
    {
        "mechanism_pathway": "forgone_care_after_need",
        "causal_role": "access_outcome_and_pathway",
        "pathway_role": "care_seeking_channel",
        "concepts": BASE_REQUIRED + [("health_need", "yes"), ("care_or_barrier", "yes")] + BASE_RECOMMENDED,
        "minimum_inputs": "health need denominator, care sought/not sought, and cost/distance/supply barrier variables",
        "timing_rule": "care-seeking module must refer to the same need episode or compatible recall period",
        "allowed_analysis": "access outcome model and pathway decomposition by barrier type",
        "prohibited_use": "do not infer forgone care for households without observed health need unless module supports it",
        "evidence_required": "raw skip pattern, barrier response coding, multiple-response handling, and denominator checks",
        "fail_interpretation": "access pathway is unavailable; keep double-failure outcome secondary or omit for that wave",
    },
    {
        "mechanism_pathway": "oop_share_conditional_on_seeking",
        "causal_role": "financial_protection_pathway",
        "pathway_role": "spending_conditional_on_utilization_channel",
        "concepts": BASE_REQUIRED
        + [("total_consumption_or_income", "yes"), ("oop_health_expenditure", "yes"), ("care_or_barrier", "recommended")]
        + BASE_RECOMMENDED,
        "minimum_inputs": "OOP health expenditure, total consumption/income, and preferably care-seeking/utilization",
        "timing_rule": "OOP and budget recall periods must be reconciled or kept as recall-specific outcomes",
        "allowed_analysis": "OOP share or log OOP among seekers, with denominator caveats",
        "prohibited_use": "do not annualize or standardize incompatible recall periods without documented justification",
        "evidence_required": "OOP scope, reimbursement/insurance treatment, recall period, currency unit, zero/missing coding, and denominator unit",
        "fail_interpretation": "financial-spending pathway cannot be interpreted beyond metadata planning",
    },
    {
        "mechanism_pathway": "coping_response_to_health_or_climate",
        "causal_role": "secondary_outcome_or_mechanism",
        "pathway_role": "coping_channel",
        "concepts": BASE_REQUIRED + [("shocks_or_livelihood", "yes"), ("oop_health_expenditure", "recommended")] + BASE_RECOMMENDED,
        "minimum_inputs": "borrowing, selling assets, reducing consumption, or other coping responses with reason/timing",
        "timing_rule": "coping must be tied to health spending or climate shock timing; otherwise label as broad vulnerability",
        "allowed_analysis": "separate coping outcome or descriptive vulnerability moderator if pre-shock",
        "prohibited_use": "do not treat generic borrowing/sales as health-cost coping without raw reason codes",
        "evidence_required": "reason for coping, timing, value coding, multiple-response handling, and relation to health/climate module",
        "fail_interpretation": "coping mechanism remains speculative and must be omitted from mechanism claims",
    },
    {
        "mechanism_pathway": "uhc_double_failure_composite",
        "causal_role": "composite_outcome",
        "pathway_role": "joint_financial_and_access_failure",
        "concepts": BASE_REQUIRED
        + [("total_consumption_or_income", "yes"), ("oop_health_expenditure", "yes"), ("health_need", "yes"), ("care_or_barrier", "yes")]
        + BASE_RECOMMENDED,
        "minimum_inputs": "financial-protection denominator and access/need denominator in the same country-wave",
        "timing_rule": "financial and access recall periods must be reported separately if not comparable",
        "allowed_analysis": "composite UHC failure only after financial and access components pass independent audits",
        "prohibited_use": "do not pool financial and access failures across country-waves where component definitions are not comparable",
        "evidence_required": "constructed CHE/SDG outcomes, forgone-care outcomes, event rates, missingness, and weighted prevalence",
        "fail_interpretation": "double-failure outcome remains secondary or unavailable; analyze financial and access outcomes separately",
    },
]


def read_csv_dicts(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def safe_int(value: str, default: int = 9999) -> int:
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return default


def compact_join(values: list[str], limit: int = 20) -> str:
    out: list[str] = []
    seen: set[str] = set()
    for value in values:
        value = (value or "").strip()
        if not value or value in seen:
            continue
        out.append(value)
        seen.add(value)
        if len(out) >= limit:
            break
    return ";".join(out)


def concept_gate_status(concept_row: dict[str, str] | None) -> tuple[str, str]:
    if not concept_row:
        return "metadata_missing", "No metadata-supported candidate concept row exists for this country-wave."
    if concept_row.get("raw_verification_status") == "raw_variables_inspected":
        return "raw_concept_verified", ""
    if concept_row.get("metadata_support_status", "").startswith("metadata_supported"):
        return "metadata_ready_raw_unverified", "Raw files, variable values, units, recall periods, keys, and missing codes have not been verified."
    return "metadata_incomplete", "Metadata evidence is insufficient for this concept."


def build_requirement_rows(bundles: list[dict[str, str]], concept_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    concept_by_key = {(row.get("idno", ""), row.get("concept", "")): row for row in concept_rows}
    rows = []
    for bundle in bundles:
        for pathway in PATHWAYS:
            for concept, required in pathway["concepts"]:
                concept_row = concept_by_key.get((bundle.get("idno", ""), concept))
                gate, gap = concept_gate_status(concept_row)
                rows.append(
                    {
                        "bundle_rank": bundle.get("bundle_rank", ""),
                        "country": bundle.get("country", ""),
                        "survey_name": bundle.get("survey_name", ""),
                        "wave": bundle.get("wave", ""),
                        "idno": bundle.get("idno", ""),
                        "mechanism_pathway": pathway["mechanism_pathway"],
                        "pathway_role": pathway["pathway_role"],
                        "concept": concept,
                        "required": required,
                        "metadata_support_status": concept_row.get("metadata_support_status", "") if concept_row else "",
                        "high_confidence_rows": concept_row.get("high_confidence_rows", "") if concept_row else "0",
                        "moderate_confidence_rows": concept_row.get("moderate_confidence_rows", "") if concept_row else "0",
                        "candidate_files": concept_row.get("candidate_files", "") if concept_row else "",
                        "candidate_variables": concept_row.get("candidate_variables", "") if concept_row else "",
                        "raw_verification_status": concept_row.get("raw_verification_status", "") if concept_row else "missing",
                        "current_gate_status": gate,
                        "blocking_gap": gap,
                        "post_treatment_guardrail": "mechanism variables may be modeled as outcomes/mediators; do not add post-shock mediators as controls in the main climate effect model",
                    }
                )
    rows.sort(key=lambda row: (safe_int(row["bundle_rank"]), row["idno"], row["mechanism_pathway"], row["required"] != "yes", row["concept"]))
    return rows


def build_pathway_protocol(requirements: list[dict[str, str]]) -> list[dict[str, str]]:
    requirement_counts = Counter(row.get("current_gate_status", "") for row in requirements if row.get("required") == "yes")
    any_ready = requirement_counts.get("raw_concept_verified", 0) > 0
    rows = []
    for pathway in PATHWAYS:
        rows.append(
            {
                "mechanism_pathway": pathway["mechanism_pathway"],
                "causal_role": pathway["causal_role"],
                "minimum_inputs": pathway["minimum_inputs"],
                "timing_rule": pathway["timing_rule"],
                "allowed_analysis": pathway["allowed_analysis"],
                "prohibited_use": pathway["prohibited_use"],
                "current_status": "planned_raw_unverified" if not any_ready else "partially_ready_requires_pathway_specific_audit",
                "evidence_required_before_claim": pathway["evidence_required"],
                "interpretation_if_unavailable_or_failed": pathway["fail_interpretation"],
            }
        )
    return rows


def first_status(rows: list[dict[str, str]], idno: str, field: str, default: str) -> str:
    for row in rows:
        if row.get("idno") == idno:
            return row.get(field, default) or default
    return default


def outcome_status(outcome_rows: list[dict[str, str]], idno: str) -> str:
    rows = [row for row in outcome_rows if row.get("idno") == idno]
    if not rows:
        return "missing_outcome_plan"
    if any(row.get("outcome_gate_status") == "ready_for_harmonized_outcome_construction" for row in rows):
        return "ready_for_harmonized_outcome_construction"
    if any(row.get("outcome_gate_status") == "metadata_ready_raw_unverified" for row in rows):
        return "metadata_ready_raw_unverified"
    return "metadata_incomplete_for_outcome"


def modeling_status(modeling_rows: list[dict[str, str]], idno: str) -> str:
    rows = [row for row in modeling_rows if row.get("idno") == idno]
    if not rows:
        return "missing_modeling_plan"
    if any(row.get("reduced_form_gate_status") == "ready_for_reduced_form_estimation_design" for row in rows):
        return "ready_for_reduced_form_estimation_design"
    if any(row.get("reduced_form_gate_status") == "metadata_plan_only_raw_unverified" for row in rows):
        return "metadata_plan_only_raw_unverified"
    return "blocked_metadata_incomplete"


def readiness_status(
    blocked_required: int,
    metadata_missing: int,
    harmonization_status: str,
    climate_status: str,
    out_status: str,
    mod_status: str,
) -> tuple[str, str]:
    if metadata_missing:
        return "blocked_metadata_missing_for_required_mechanism_concepts", "expand metadata search or drop this mechanism for the country-wave"
    if blocked_required:
        return "blocked_until_required_raw_mechanism_concepts_verified", "inspect raw schemas and complete value/unit/recall/key audits for required mechanism concepts"
    if harmonization_status != "ready_for_verified_recipe_assembly":
        return "blocked_until_verified_harmonization_recipe", "promote verified harmonization recipe candidates and build harmonized household data"
    if climate_status != "ready_for_climate_linkage_value_audit":
        return "blocked_until_climate_linkage_value_audit", "verify timing/geography and extract climate exposures"
    if out_status != "ready_for_harmonized_outcome_construction":
        return "blocked_until_outcome_construction", "construct and audit the relevant UHC outcome family"
    if mod_status != "ready_for_reduced_form_estimation_design":
        return "blocked_until_main_effect_design_ready", "pass reduced-form identification design gates before mechanism interpretation"
    return "ready_for_mechanism_analysis_design", "pre-specify mechanism model and run only after main effect model is auditable"


def build_readiness(
    requirements: list[dict[str, str]],
    harmonization_rows: list[dict[str, str]],
    climate_rows: list[dict[str, str]],
    outcome_rows: list[dict[str, str]],
    modeling_rows: list[dict[str, str]],
) -> list[dict[str, str]]:
    grouped: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in requirements:
        grouped[(row["idno"], row["mechanism_pathway"])].append(row)

    rows = []
    for (_idno, _pathway), reqs in grouped.items():
        first = reqs[0]
        required = [row for row in reqs if row.get("required") == "yes"]
        recommended = [row for row in reqs if row.get("required") == "recommended"]
        raw_verified_required = [row for row in required if row.get("current_gate_status") == "raw_concept_verified"]
        blocked_required = [row for row in required if row.get("current_gate_status") != "raw_concept_verified"]
        metadata_missing = [row for row in required if row.get("current_gate_status") == "metadata_missing"]
        harmonization_status = first_status(harmonization_rows, first["idno"], "readiness_status", "missing_harmonization_readiness")
        climate_status = first_status(climate_rows, first["idno"], "readiness_status", "missing_climate_readiness")
        out_status = outcome_status(outcome_rows, first["idno"])
        mod_status = modeling_status(modeling_rows, first["idno"])
        status, action = readiness_status(
            len(blocked_required),
            len(metadata_missing),
            harmonization_status,
            climate_status,
            out_status,
            mod_status,
        )
        rows.append(
            {
                "bundle_rank": first.get("bundle_rank", ""),
                "country": first.get("country", ""),
                "survey_name": first.get("survey_name", ""),
                "wave": first.get("wave", ""),
                "idno": first.get("idno", ""),
                "mechanism_pathway": first.get("mechanism_pathway", ""),
                "required_concept_rows": str(len(required)),
                "recommended_concept_rows": str(len(recommended)),
                "raw_verified_required_rows": str(len(raw_verified_required)),
                "blocked_required_rows": str(len(blocked_required)),
                "metadata_missing_required_rows": str(len(metadata_missing)),
                "harmonization_status": harmonization_status,
                "climate_linkage_status": climate_status,
                "outcome_status": out_status,
                "modeling_status": mod_status,
                "readiness_status": status,
                "next_action": action,
            }
        )
    rows.sort(key=lambda row: (safe_int(row["bundle_rank"]), row["idno"], row["mechanism_pathway"]))
    return rows


def build_summary(requirements: list[dict[str, str]], protocol: list[dict[str, str]], readiness: list[dict[str, str]], raw_variables: list[dict[str, str]]) -> list[dict[str, str]]:
    gate_counts = Counter(row.get("current_gate_status", "") for row in requirements)
    readiness_counts = Counter(row.get("readiness_status", "") for row in readiness)
    pathway_counts = Counter(row.get("mechanism_pathway", "") for row in readiness)
    rows = [
        {"metric": "requirement_rows", "value": str(len(requirements)), "interpretation": "Country-wave pathway concept requirement rows."},
        {"metric": "pathway_protocol_rows", "value": str(len(protocol)), "interpretation": "Mechanism pathway protocol rows."},
        {"metric": "readiness_rows", "value": str(len(readiness)), "interpretation": "Country-wave by mechanism pathway readiness rows."},
        {"metric": "country_wave_rows", "value": str(len({row.get("idno", "") for row in readiness})), "interpretation": "Country-waves assessed."},
        {"metric": "mechanism_pathway_count", "value": str(len(pathway_counts)), "interpretation": "Mechanism pathways assessed."},
        {"metric": "ready_pathway_rows", "value": str(sum(1 for row in readiness if row.get("readiness_status") == "ready_for_mechanism_analysis_design")), "interpretation": "Country-wave pathway rows ready for mechanism analysis design."},
        {"metric": "blocked_pathway_rows", "value": str(sum(1 for row in readiness if row.get("readiness_status") != "ready_for_mechanism_analysis_design")), "interpretation": "Country-wave pathway rows blocked by raw evidence or upstream gates."},
        {"metric": "raw_variable_catalog_rows", "value": str(len(raw_variables)), "interpretation": "Inspected raw variable catalog rows."},
    ]
    for key, count in sorted(gate_counts.items()):
        rows.append({"metric": f"requirement_gate_{key}", "value": str(count), "interpretation": "Mechanism requirement gate status count."})
    for key, count in sorted(readiness_counts.items()):
        rows.append({"metric": f"readiness_status_{key}", "value": str(count), "interpretation": "Mechanism readiness status count."})
    for key, count in sorted(pathway_counts.items()):
        rows.append({"metric": f"pathway_rows_{key}", "value": str(count), "interpretation": "Country-wave readiness row count by pathway."})
    return rows


def markdown_count_table(counter: Counter[str], label: str) -> str:
    lines = [f"| {label} | Count |", "|---|---:|"]
    for key, count in counter.most_common():
        lines.append(f"| {key or 'blank'} | {count} |")
    return "\n".join(lines)


def markdown_rows(rows: list[dict[str, str]], columns: list[str], limit: int = 20) -> str:
    lines = ["| " + " | ".join(columns) + " |", "|" + "|".join("---" for _ in columns) + "|"]
    for row in rows[:limit]:
        values = []
        for column in columns:
            value = (row.get(column, "") or "").replace("|", "/")
            if len(value) > 120:
                value = value[:117] + "..."
            values.append(value)
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines)


def write_report(requirements: list[dict[str, str]], protocol: list[dict[str, str]], readiness: list[dict[str, str]], summary: list[dict[str, str]]) -> None:
    gate_counts = Counter(row.get("current_gate_status", "") for row in requirements)
    readiness_counts = Counter(row.get("readiness_status", "") for row in readiness)
    pathway_counts = Counter(row.get("mechanism_pathway", "") for row in readiness)
    summary_table = "\n".join(f"| {row['metric']} | {row['value']} | {row['interpretation']} |" for row in summary)
    REPORT_PATH.write_text(
        f"""# Mechanism Analysis Protocol

Status: planned and fail-closed. No mechanism claim is currently supported because raw mechanism variables, harmonized outcomes, climate linkage, and main-effect identification gates have not passed.

## Purpose

This protocol maps the Phase 11 mechanism pathways to required raw concepts and protects the main causal design from post-treatment controls. Mechanism variables may be modeled as separate outcomes or mediators only after raw values, timing, denominators, and lineage are audited.

## Counts

| Metric | Value | Interpretation |
|---|---:|---|
{summary_table}

## Requirement Gates

{markdown_count_table(gate_counts, 'Requirement gate status') if requirements else 'No requirement rows exist yet.'}

## Readiness

{markdown_count_table(readiness_counts, 'Readiness status') if readiness else 'No readiness rows exist yet.'}

## Pathway Coverage

{markdown_count_table(pathway_counts, 'Mechanism pathway') if readiness else 'No pathway rows exist yet.'}

{markdown_rows(readiness, ['bundle_rank', 'country', 'wave', 'idno', 'mechanism_pathway', 'blocked_required_rows', 'readiness_status'], 20) if readiness else ''}

## Guardrails

- Do not include post-shock income, food insecurity, health need, care-seeking, OOP spending, or coping variables as controls in the main climate-effect model.
- Do not force a mechanism where raw questionnaire wording, recall period, denominator, and value coding do not support it.
- Do not pool mechanism estimates across country-waves unless construct definitions and recall windows are comparable.
- If only the main outcome is supported, report mechanisms as unavailable rather than speculative.

## Outputs

- `temp/mechanism_variable_requirements.csv`
- `result/mechanism_pathway_protocol.csv`
- `result/mechanism_readiness_matrix.csv`
- `result/mechanism_analysis_protocol_summary.csv`
""",
        encoding="utf-8",
    )


def main() -> None:
    ensure_dirs()
    bundles = read_csv_dicts(BUNDLES_PATH)
    concept_rows = read_csv_dicts(CONCEPT_PATH)
    raw_variables = read_csv_dicts(RAW_VARIABLE_PATH)
    harmonization_rows = read_csv_dicts(HARMONIZATION_READINESS_PATH)
    climate_rows = read_csv_dicts(CLIMATE_READINESS_PATH)
    outcome_rows = read_csv_dicts(OUTCOME_PLAN_PATH)
    modeling_rows = read_csv_dicts(MODELING_PLAN_PATH)

    requirements = build_requirement_rows(bundles, concept_rows)
    protocol = build_pathway_protocol(requirements)
    readiness = build_readiness(requirements, harmonization_rows, climate_rows, outcome_rows, modeling_rows)
    summary = build_summary(requirements, protocol, readiness, raw_variables)

    write_csv(REQUIREMENTS_PATH, requirements, REQUIREMENT_COLUMNS)
    write_csv(PATHWAY_PROTOCOL_PATH, protocol, PATHWAY_COLUMNS)
    write_csv(READINESS_PATH, readiness, READINESS_COLUMNS)
    write_csv(SUMMARY_PATH, summary, SUMMARY_COLUMNS)
    write_report(requirements, protocol, readiness, summary)
    append_log(TEMP_DIR / "audit_log.md", f"Mechanism analysis protocol requirement_rows={len(requirements)} readiness_rows={len(readiness)}.")
    print(f"Mechanism analysis protocol requirement_rows={len(requirements)} readiness_rows={len(readiness)}.")


if __name__ == "__main__":
    main()
