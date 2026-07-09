from __future__ import annotations

import csv
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from common import REPORT_DIR, RESULT_DIR, TEMP_DIR, append_log, ensure_dirs, write_csv


BUNDLES_PATH = TEMP_DIR / "minimum_viable_download_bundles.csv"
OUTCOME_PLAN_PATH = TEMP_DIR / "outcome_denominator_plan.csv"
CONCEPT_PATH = TEMP_DIR / "raw_ingestion_concept_checklist.csv"
PROTOCOL_PATH = TEMP_DIR / "raw_variable_verification_protocol.csv"
SOURCE_PROBE_PATH = TEMP_DIR / "validation_reference_source_probe.csv"
INDICATOR_SAMPLE_PATH = TEMP_DIR / "validation_reference_indicator_sample.csv"
HEFPI_SERIES_PATH = TEMP_DIR / "hefpi_uhc_series_catalog.csv"
HEFPI_REFERENCE_PATH = TEMP_DIR / "hefpi_uhc_reference_sample.csv"
RAW_VARIABLE_PATH = TEMP_DIR / "raw_schema_inventory" / "raw_variable_catalog.csv"
SDG_METADATA_PATH = TEMP_DIR / "source_snapshots" / "unstats_sdg_3_8_2_metadata.txt"
WHO_FINANCIAL_PATH = TEMP_DIR / "source_snapshots" / "who_financial_protection_sdg382_2025.md"

REQUIREMENTS_PATH = TEMP_DIR / "sdg382_denominator_requirements.csv"
SOURCE_MATRIX_PATH = RESULT_DIR / "sdg382_denominator_source_matrix.csv"
READINESS_PATH = RESULT_DIR / "sdg382_denominator_country_wave_readiness.csv"
SUMMARY_PATH = RESULT_DIR / "sdg382_denominator_summary.csv"
REPORT_PATH = REPORT_DIR / "sdg382_denominator_audit_plan.md"

REQUIREMENT_COLUMNS = [
    "bundle_rank",
    "country",
    "survey_name",
    "wave",
    "idno",
    "denominator_component",
    "required_evidence",
    "raw_concepts_required",
    "metadata_support_status",
    "raw_verification_status",
    "external_source_roles_required",
    "external_source_status",
    "current_gate_status",
    "blocking_gap",
    "formula_or_rule",
    "source_basis",
]

SOURCE_COLUMNS = [
    "source_role",
    "source_name",
    "indicator",
    "official_url",
    "probe_status",
    "saved_path",
    "current_use",
    "limitation",
]

READINESS_COLUMNS = [
    "bundle_rank",
    "country",
    "survey_name",
    "wave",
    "idno",
    "sdg382_outcome_plan_status",
    "component_rows",
    "metadata_supported_component_rows",
    "raw_verified_component_rows",
    "external_source_ready_component_rows",
    "blocked_component_rows",
    "readiness_status",
    "next_action",
]

SUMMARY_COLUMNS = ["metric", "value", "interpretation"]

COMPONENTS = [
    {
        "component": "oop_health_expenditure_scope",
        "raw_concepts": ["oop_health_expenditure"],
        "external_roles": ["hefpi_bulk_csv_reference", "oop_macro_context"],
        "required": "Raw OOP health spending must cover household payments for health goods/services, exclude third-party reimbursement, and preserve recall period.",
        "formula": "positive OOP health expenditure is the numerator and must be comparable with the welfare denominator period",
        "source": "UNSD SDG 3.8.2 metadata and WHO financial protection topic page",
    },
    {
        "component": "total_welfare_measure",
        "raw_concepts": ["total_consumption_or_income"],
        "external_roles": [],
        "required": "Total household consumption or disposable income must include health spending and be source-team aggregate where available.",
        "formula": "prefer total consumption when both consumption and income exist; income is fallback only after comparability audit",
        "source": "UNSD metadata consumption/income denominator guidance",
    },
    {
        "component": "household_size_and_daily_pc_conversion",
        "raw_concepts": ["demographics"],
        "external_roles": [],
        "required": "Household size and welfare reference period are required to convert total welfare to per-capita daily values.",
        "formula": "per_capita_daily_welfare = household_total_welfare / household_size / period_days",
        "source": "UNSD metadata per-capita daily conversion guidance",
    },
    {
        "component": "societal_poverty_line_formula",
        "raw_concepts": ["total_consumption_or_income", "oop_health_expenditure"],
        "external_roles": ["poverty_line_context", "pip_societal_poverty_benchmark"],
        "required": "SPL must be computed in 2017 PPP daily per-capita terms from the greater of the international poverty line and the relative societal line.",
        "formula": "SPL = max(2.15, 1.15 + 0.5 * median(welfare_excluding_oop_health)) in 2017 PPP per capita per day",
        "source": "UNSD SDG 3.8.2 metadata definition lines for SPL",
    },
    {
        "component": "ppp_2017_conversion",
        "raw_concepts": ["survey_timing"],
        "external_roles": ["ppp_conversion_context", "pip_ppp_2017_benchmark"],
        "required": "PPP conversion must align local currency welfare values to 2017 PPP international dollars.",
        "formula": "local currency welfare is converted to 2017 PPP terms before applying the SPL threshold",
        "source": "UNSD metadata and World Bank PPP context sources",
    },
    {
        "component": "cpi_or_price_adjustment",
        "raw_concepts": ["survey_timing"],
        "external_roles": ["cpi_context"],
        "required": "Survey currency year/month and any CPI or deflator assumptions must be documented before cross-year conversion.",
        "formula": "deflate or inflate local currency values only with documented survey period and price index choice",
        "source": "WDI CPI context and UNSD comparability guidance",
    },
    {
        "component": "survey_weights_and_population_basis",
        "raw_concepts": ["survey_weight"],
        "external_roles": [],
        "required": "Survey weights must be verified for population proportions, weighted medians, event rates, and prevalence.",
        "formula": "weighted incidence = weighted population with positive OOP > 40 percent discretionary budget / weighted population",
        "source": "SDG indicator is a population proportion; survey design must be preserved",
    },
    {
        "component": "discretionary_budget_construction",
        "raw_concepts": ["total_consumption_or_income", "oop_health_expenditure", "demographics", "survey_timing"],
        "external_roles": ["poverty_line_context", "ppp_conversion_context", "cpi_context"],
        "required": "Household-level discretionary budget must be nonnegative/valid and traceable to welfare, SPL, PPP/CPI, household size, and period conversions.",
        "formula": "household_discretionary_budget = total_welfare - household_spl_for_same_period_and_currency",
        "source": "UNSD metadata definition of discretionary household budget",
    },
    {
        "component": "country_year_benchmark_checks",
        "raw_concepts": ["total_consumption_or_income", "oop_health_expenditure", "survey_weight"],
        "external_roles": ["hefpi_bulk_csv_reference", "poverty_line_context", "oop_macro_context", "pip_societal_poverty_benchmark"],
        "required": "After construction, compare welfare, poverty/SPL, OOP, and OOP share against external benchmark sources where available.",
        "formula": "benchmark checks are diagnostics only; failed checks should downgrade or exclude SDG 3.8.2 for that country-wave",
        "source": "UNSD metadata quality-assessment section and HEFPI/WDI reference probes",
    },
]

LOCAL_ONLY_EXTERNAL_ROLES = {
    "pip_societal_poverty_benchmark": "PIP societal-poverty benchmark not yet probed in this workspace.",
    "pip_ppp_2017_benchmark": "Exact PIP/2017 PPP benchmark not yet probed in this workspace.",
}


def read_csv_dicts(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def file_ok(path: Path) -> bool:
    return path.exists() and path.is_file() and path.stat().st_size > 0


def safe_int(value: Any, default: int = 999999) -> int:
    try:
        return int(str(value).strip())
    except (TypeError, ValueError):
        return default


def concept_index(rows: list[dict[str, str]]) -> dict[tuple[str, str], dict[str, str]]:
    return {(row.get("idno", ""), row.get("concept", "")): row for row in rows if row.get("idno") and row.get("concept")}


def count_by_id(rows: list[dict[str, str]], id_field: str = "idno") -> Counter[str]:
    return Counter(row.get(id_field, "") for row in rows if row.get(id_field, ""))


def source_role_status(rows: list[dict[str, str]]) -> dict[str, list[dict[str, str]]]:
    out: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        role = row.get("source_role", "")
        if role:
            out[role].append(row)
    return out


def role_ready(role: str, source_rows_by_role: dict[str, list[dict[str, str]]]) -> bool:
    if role in LOCAL_ONLY_EXTERNAL_ROLES:
        return False
    return any(row.get("status") in {"reachable_snapshot_saved", "indicator_metadata_available"} for row in source_rows_by_role.get(role, []))


def component_status(
    idno: str,
    component: dict[str, Any],
    concepts: dict[tuple[str, str], dict[str, str]],
    protocol_counts: Counter[str],
    raw_variable_counts: Counter[str],
    source_rows_by_role: dict[str, list[dict[str, str]]],
) -> dict[str, str]:
    raw_concepts = component["raw_concepts"]
    metadata_supported = []
    raw_verified = []
    missing_metadata = []
    for concept in raw_concepts:
        row = concepts.get((idno, concept), {})
        if row.get("metadata_support_status") == "metadata_supported_raw_unverified":
            metadata_supported.append(concept)
        else:
            missing_metadata.append(concept)
        if row.get("raw_verification_status") == "raw_variables_inspected":
            raw_verified.append(concept)

    external_roles = component["external_roles"]
    missing_external = [role for role in external_roles if not role_ready(role, source_rows_by_role)]
    ready_external = [role for role in external_roles if role_ready(role, source_rows_by_role)]

    if missing_metadata:
        gate = "metadata_missing"
        gap = "missing metadata concept support: " + ";".join(missing_metadata)
    elif raw_variable_counts[idno] == 0 or len(raw_verified) < len(raw_concepts):
        gate = "metadata_ready_raw_unverified"
        gap = "raw variables and values have not been inspected for required concepts"
    elif missing_external:
        gate = "external_source_missing"
        gap = "missing denominator/reference source roles: " + ";".join(missing_external)
    else:
        gate = "ready_for_denominator_value_audit"
        gap = "still requires household-level value distribution, outlier, and benchmark checks before interpretation"

    return {
        "metadata_support_status": "metadata_supported" if not missing_metadata else "metadata_incomplete",
        "raw_verification_status": "raw_verified" if raw_concepts and len(raw_verified) == len(raw_concepts) else "raw_not_verified",
        "external_source_status": "source_ready" if not external_roles or not missing_external else "source_missing:" + ";".join(missing_external),
        "current_gate_status": gate,
        "blocking_gap": gap,
        "protocol_rows_to_check": str(protocol_counts[idno]),
        "external_ready_roles": ";".join(ready_external),
    }


def build_requirement_rows(
    bundles: list[dict[str, str]],
    outcome_rows: list[dict[str, str]],
    concept_rows: list[dict[str, str]],
    protocol_rows: list[dict[str, str]],
    raw_variable_rows: list[dict[str, str]],
    source_rows: list[dict[str, str]],
) -> list[dict[str, str]]:
    concepts = concept_index(concept_rows)
    protocol_counts = count_by_id(protocol_rows, "idno")
    raw_variable_counts = count_by_id(raw_variable_rows, "idno")
    source_rows_by_role = source_role_status(source_rows)
    sdg_plan_by_id = {row.get("idno", ""): row for row in outcome_rows if row.get("outcome") == "sdg382_discretionary_40"}

    rows = []
    for bundle in bundles:
        idno = bundle.get("idno", "")
        if not idno:
            continue
        plan = sdg_plan_by_id.get(idno, {})
        for component in COMPONENTS:
            status = component_status(idno, component, concepts, protocol_counts, raw_variable_counts, source_rows_by_role)
            rows.append(
                {
                    "bundle_rank": bundle.get("bundle_rank", ""),
                    "country": bundle.get("country", ""),
                    "survey_name": bundle.get("survey_name", ""),
                    "wave": bundle.get("wave", ""),
                    "idno": idno,
                    "denominator_component": component["component"],
                    "required_evidence": component["required"],
                    "raw_concepts_required": ";".join(component["raw_concepts"]),
                    "metadata_support_status": status["metadata_support_status"],
                    "raw_verification_status": status["raw_verification_status"],
                    "external_source_roles_required": ";".join(component["external_roles"]),
                    "external_source_status": status["external_source_status"],
                    "current_gate_status": status["current_gate_status"],
                    "blocking_gap": status["blocking_gap"],
                    "formula_or_rule": component["formula"],
                    "source_basis": component["source"] + (f"; outcome plan status={plan.get('outcome_gate_status', 'missing_sdg382_plan')}" if plan else "; outcome plan row missing"),
                }
            )
    rows.sort(key=lambda row: (safe_int(row["bundle_rank"]), row["denominator_component"]))
    return rows


def build_source_matrix(source_rows: list[dict[str, str]], indicator_rows: list[dict[str, str]], hefpi_series: list[dict[str, str]], hefpi_reference: list[dict[str, str]]) -> list[dict[str, str]]:
    rows = []
    seen_roles: set[str] = set()
    for row in source_rows:
        role = row.get("source_role", "")
        if not role:
            continue
        seen_roles.add(role)
        rows.append(
            {
                "source_role": role,
                "source_name": row.get("source_name", ""),
                "indicator": row.get("indicator", ""),
                "official_url": row.get("official_url", ""),
                "probe_status": row.get("status", ""),
                "saved_path": row.get("saved_path", ""),
                "current_use": row.get("expected_use", ""),
                "limitation": row.get("unit_or_definition_note", ""),
            }
        )
    for role, limitation in LOCAL_ONLY_EXTERNAL_ROLES.items():
        if role not in seen_roles:
            rows.append(
                {
                    "source_role": role,
                    "source_name": "World Bank Poverty and Inequality Platform",
                    "indicator": "",
                    "official_url": "https://pip.worldbank.org/home",
                    "probe_status": "not_probed",
                    "saved_path": "",
                    "current_use": "Benchmark for societal poverty line and PPP base after raw welfare vector exists.",
                    "limitation": limitation,
                }
            )
    if file_ok(SDG_METADATA_PATH):
        rows.append(
            {
                "source_role": "official_sdg382_metadata",
                "source_name": "UNSD SDG 3.8.2 metadata",
                "indicator": "SH_OOP_XPD_EARNNET40",
                "official_url": "https://unstats.un.org/sdgs/metadata/files/Metadata-03-08-02.pdf",
                "probe_status": "local_snapshot_present",
                "saved_path": str(SDG_METADATA_PATH.relative_to(TEMP_DIR.parent)).replace("\\", "/"),
                "current_use": "Official formula basis for SDG 3.8.2 denominator guard.",
                "limitation": "Formula source only; does not provide household-level variables.",
            }
        )
    if file_ok(WHO_FINANCIAL_PATH):
        rows.append(
            {
                "source_role": "who_sdg382_2025_topic_page",
                "source_name": "WHO financial protection page",
                "indicator": "SDG 3.8.2 2025 definition",
                "official_url": "https://www.who.int/data/gho/data/themes/topics/financial-protection",
                "probe_status": "local_snapshot_present",
                "saved_path": str(WHO_FINANCIAL_PATH.relative_to(TEMP_DIR.parent)).replace("\\", "/"),
                "current_use": "Policy/source verification that 2025 SDG 3.8.2 uses 40 percent discretionary budget.",
                "limitation": "Topic page does not replace microdata construction.",
            }
        )
    rows.append(
        {
            "source_role": "hefpi_uhc_reference_records",
            "source_name": "World Bank HEFPI reference extract",
            "indicator": "multiple",
            "official_url": "https://databank.worldbank.org/data/download/HEFPI_CSV.zip",
            "probe_status": "records_available" if hefpi_reference else "no_records",
            "saved_path": f"temp/{HEFPI_REFERENCE_PATH.name}",
            "current_use": "Country-year validation after household outcomes are constructed.",
            "limitation": f"series_rows={len(hefpi_series)}; reference_rows={len(hefpi_reference)}; aggregate validation only.",
        }
    )
    rows.append(
        {
            "source_role": "wdi_indicator_samples",
            "source_name": "World Bank WDI indicator samples",
            "indicator": "multiple",
            "official_url": "https://api.worldbank.org/v2/indicator",
            "probe_status": "records_available" if indicator_rows else "no_records",
            "saved_path": f"temp/{INDICATOR_SAMPLE_PATH.name}",
            "current_use": "PPP, CPI, OOP macro context samples.",
            "limitation": "Samples are not household microdata and may not be the exact SDG 2017 PPP/PIP benchmark.",
        }
    )
    return rows


def build_readiness_rows(requirements: list[dict[str, str]], outcome_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    sdg_plan = {row.get("idno", ""): row for row in outcome_rows if row.get("outcome") == "sdg382_discretionary_40"}
    for row in requirements:
        grouped[row["idno"]].append(row)
    readiness = []
    for idno, rows in grouped.items():
        first = rows[0]
        metadata_supported = sum(1 for row in rows if row.get("metadata_support_status") == "metadata_supported")
        raw_verified = sum(1 for row in rows if row.get("raw_verification_status") == "raw_verified")
        external_ready = sum(1 for row in rows if row.get("external_source_status") == "source_ready")
        blocked = sum(1 for row in rows if row.get("current_gate_status") != "ready_for_denominator_value_audit")
        if blocked:
            status = "blocked_until_raw_and_external_denominator_audit"
            next_action = "place raw files, inspect schemas/values, verify exact 2017 PPP/PIP/SPL sources, then rerun denominator audit"
        else:
            status = "ready_for_household_denominator_value_audit"
            next_action = "construct trial denominator variables and run distribution/benchmark checks before outcome interpretation"
        readiness.append(
            {
                "bundle_rank": first.get("bundle_rank", ""),
                "country": first.get("country", ""),
                "survey_name": first.get("survey_name", ""),
                "wave": first.get("wave", ""),
                "idno": idno,
                "sdg382_outcome_plan_status": sdg_plan.get(idno, {}).get("outcome_gate_status", "missing_sdg382_plan"),
                "component_rows": str(len(rows)),
                "metadata_supported_component_rows": str(metadata_supported),
                "raw_verified_component_rows": str(raw_verified),
                "external_source_ready_component_rows": str(external_ready),
                "blocked_component_rows": str(blocked),
                "readiness_status": status,
                "next_action": next_action,
            }
        )
    readiness.sort(key=lambda row: safe_int(row["bundle_rank"]))
    return readiness


def build_summary_rows(requirements: list[dict[str, str]], readiness: list[dict[str, str]], sources: list[dict[str, str]]) -> list[dict[str, str]]:
    gate_counts = Counter(row.get("current_gate_status", "") for row in requirements)
    source_counts = Counter(row.get("probe_status", "") for row in sources)
    rows = [
        {"metric": "requirement_rows", "value": str(len(requirements)), "interpretation": "Country-wave denominator component requirement rows."},
        {"metric": "country_wave_rows", "value": str(len(readiness)), "interpretation": "Priority bundle country-waves assessed."},
        {"metric": "source_matrix_rows", "value": str(len(sources)), "interpretation": "Reference/source role rows."},
        {"metric": "ready_for_sdg382_construction_rows", "value": str(sum(1 for row in readiness if row.get("readiness_status") == "ready_for_household_denominator_value_audit")), "interpretation": "Rows ready for household denominator value audit."},
        {"metric": "blocked_country_wave_rows", "value": str(sum(1 for row in readiness if row.get("readiness_status") != "ready_for_household_denominator_value_audit")), "interpretation": "Rows still blocked by raw or exact external denominator inputs."},
    ]
    for gate, count in sorted(gate_counts.items()):
        rows.append({"metric": f"component_gate_{gate}", "value": str(count), "interpretation": "Denominator component gate count."})
    for status, count in sorted(source_counts.items()):
        rows.append({"metric": f"source_status_{status}", "value": str(count), "interpretation": "Source-matrix probe status count."})
    return rows


def markdown_count_table(counter: Counter[str], label: str) -> str:
    lines = [f"| {label} | Count |", "|---|---:|"]
    for key, count in counter.most_common():
        lines.append(f"| {key or 'blank'} | {count} |")
    return "\n".join(lines)


def markdown_table(rows: list[dict[str, str]], columns: list[str], limit: int = 12) -> str:
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


def write_report(requirements: list[dict[str, str]], readiness: list[dict[str, str]], sources: list[dict[str, str]], summary: list[dict[str, str]]) -> None:
    gate_counts = Counter(row.get("current_gate_status", "") for row in requirements)
    readiness_counts = Counter(row.get("readiness_status", "") for row in readiness)
    source_counts = Counter(row.get("probe_status", "") for row in sources)
    summary_table = "\n".join(f"| {row['metric']} | {row['value']} | {row['interpretation']} |" for row in summary)
    REPORT_PATH.write_text(
        f"""# SDG 3.8.2 Denominator Audit Plan

Status: denominator construction is blocked. This report is a fail-closed checklist for constructing `household_discretionary_budget`; it does not create SDG 3.8.2 outcomes.

## Official Rule Basis

The local UNSD metadata snapshot defines SDG 3.8.2 as positive OOP health expenditure exceeding 40 percent of household discretionary budget. It defines discretionary budget as total household consumption expenditure or income minus the societal poverty line. The SPL is in 2017 PPP daily per-capita terms and uses the greater of the international poverty line or the relative societal line.

## Counts

| Metric | Value | Interpretation |
|---|---:|---|
{summary_table}

## Component Gates

{markdown_count_table(gate_counts, 'Component gate status')}

## Country-Wave Readiness

{markdown_count_table(readiness_counts, 'Readiness status')}

{markdown_table(readiness, ['bundle_rank', 'country', 'wave', 'idno', 'component_rows', 'blocked_component_rows', 'readiness_status'], 15)}

## Source Matrix Status

{markdown_count_table(source_counts, 'Source status')}

## Guardrails

- Do not construct `sdg382_discretionary_40` from CHE10/CHE25 denominators.
- Do not infer SPL from a poverty-headcount indicator alone.
- Do not use WDI PPP/CPI context as the exact SDG denominator without verifying 2017 PPP/PIP compatibility.
- Do not interpret country-wave SDG 3.8.2 unless raw OOP, welfare, household size, survey period, weights, SPL, PPP/CPI, and benchmark checks pass.

## Outputs

- `temp/sdg382_denominator_requirements.csv`
- `result/sdg382_denominator_source_matrix.csv`
- `result/sdg382_denominator_country_wave_readiness.csv`
- `result/sdg382_denominator_summary.csv`
""",
        encoding="utf-8",
    )


def main() -> None:
    ensure_dirs()
    bundles = read_csv_dicts(BUNDLES_PATH)
    outcome_rows = read_csv_dicts(OUTCOME_PLAN_PATH)
    concept_rows = read_csv_dicts(CONCEPT_PATH)
    protocol_rows = read_csv_dicts(PROTOCOL_PATH)
    source_rows = read_csv_dicts(SOURCE_PROBE_PATH)
    indicator_rows = read_csv_dicts(INDICATOR_SAMPLE_PATH)
    hefpi_series = read_csv_dicts(HEFPI_SERIES_PATH)
    hefpi_reference = read_csv_dicts(HEFPI_REFERENCE_PATH)
    raw_variable_rows = read_csv_dicts(RAW_VARIABLE_PATH)

    requirements = build_requirement_rows(bundles, outcome_rows, concept_rows, protocol_rows, raw_variable_rows, source_rows)
    sources = build_source_matrix(source_rows, indicator_rows, hefpi_series, hefpi_reference)
    readiness = build_readiness_rows(requirements, outcome_rows)
    summary = build_summary_rows(requirements, readiness, sources)

    write_csv(REQUIREMENTS_PATH, requirements, REQUIREMENT_COLUMNS)
    write_csv(SOURCE_MATRIX_PATH, sources, SOURCE_COLUMNS)
    write_csv(READINESS_PATH, readiness, READINESS_COLUMNS)
    write_csv(SUMMARY_PATH, summary, SUMMARY_COLUMNS)
    write_report(requirements, readiness, sources, summary)
    append_log(TEMP_DIR / "audit_log.md", f"SDG382 denominator audit plan requirement_rows={len(requirements)} country_wave_rows={len(readiness)}.")
    print(f"SDG382 denominator audit plan requirement_rows={len(requirements)} country_wave_rows={len(readiness)}.")


if __name__ == "__main__":
    main()
