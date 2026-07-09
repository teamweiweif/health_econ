from __future__ import annotations

import csv
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from common import REPORT_DIR, RESULT_DIR, TEMP_DIR, append_log, ensure_dirs, write_csv


QUALITY_PATH = RESULT_DIR / "metadata_candidate_quality_audit.csv"
PRIORITY_PATH = TEMP_DIR / "metadata_quality_download_priority.csv"
INTAKE_PATH = TEMP_DIR / "raw_download_intake_manifest.csv"
EXPECTED_PATH = TEMP_DIR / "raw_download_expected_files.csv"
CONCEPT_PATH = TEMP_DIR / "raw_ingestion_concept_checklist.csv"
MODULE_PATH = TEMP_DIR / "raw_ingestion_module_checklist.csv"
PROTOCOL_PATH = TEMP_DIR / "raw_variable_verification_protocol.csv"
RAW_FILE_PATH = TEMP_DIR / "raw_schema_inventory" / "raw_file_inventory.csv"
RAW_VARIABLE_PATH = TEMP_DIR / "raw_schema_inventory" / "raw_variable_catalog.csv"

TARGETS_PATH = RESULT_DIR / "minimum_viable_acquisition_targets.csv"
BUNDLES_PATH = TEMP_DIR / "minimum_viable_download_bundles.csv"
SUMMARY_PATH = RESULT_DIR / "minimum_viable_acquisition_summary.csv"
REPORT_PATH = REPORT_DIR / "minimum_viable_acquisition_plan.md"

TARGET_COLUMNS = [
    "acquisition_set",
    "target_rank",
    "country",
    "survey_name",
    "wave",
    "idno",
    "quality_rank",
    "quality_download_priority_tier",
    "official_url",
    "local_target_folder",
    "raw_intake_status",
    "expected_module_rows",
    "expected_core_module_rows",
    "expected_not_present_rows",
    "raw_file_inventory_rows",
    "raw_variable_catalog_rows",
    "high_confidence_rows",
    "moderate_confidence_rows",
    "concept_rows_to_verify",
    "protocol_rows_to_verify",
    "why_selected",
    "required_evidence_after_download",
    "not_final_sample_guardrail",
]

BUNDLE_COLUMNS = [
    "bundle_rank",
    "country",
    "survey_name",
    "wave",
    "idno",
    "included_acquisition_sets",
    "official_url",
    "local_target_folder",
    "raw_intake_status",
    "download_scope",
    "top_modules_to_verify_first",
    "financial_core_expected_files",
    "access_core_expected_files",
    "geography_timing_design_expected_files",
    "concepts_to_verify",
    "post_download_commands",
    "manual_action",
    "guardrail",
]

SUMMARY_COLUMNS = ["metric", "value", "interpretation"]

FINANCIAL_CORE_CONCEPTS = ["total_consumption_or_income", "oop_health_expenditure", "survey_weight", "survey_timing", "climate_geography"]
ACCESS_CORE_CONCEPTS = ["health_need", "care_or_barrier"]
GEOGRAPHY_TIMING_DESIGN_CONCEPTS = ["household_id", "survey_weight", "survey_timing", "climate_geography", "psu_cluster", "strata"]


def read_csv_dicts(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def safe_int(value: Any, default: int = 999999) -> int:
    try:
        text = str(value).strip()
        return int(text)
    except (TypeError, ValueError):
        return default


def split_values(value: str) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for item in (value or "").replace(",", ";").split(";"):
        clean = item.strip()
        if clean and clean not in seen:
            out.append(clean)
            seen.add(clean)
    return out


def compact(values: list[str], limit: int = 12) -> str:
    seen: set[str] = set()
    out: list[str] = []
    for value in values:
        clean = (value or "").strip()
        if clean and clean not in seen:
            out.append(clean)
            seen.add(clean)
        if len(out) >= limit:
            break
    return ";".join(out)


def priority_index(priority_rows: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    return {row.get("idno", ""): row for row in priority_rows if row.get("idno")}


def quality_candidates(quality_rows: list[dict[str, str]], priorities: dict[str, dict[str, str]]) -> list[dict[str, str]]:
    out = []
    for row in quality_rows:
        idno = row.get("idno", "")
        if not idno:
            continue
        priority = priorities.get(idno, {})
        merged = dict(row)
        for field in [
            "quality_rank",
            "quality_download_priority_tier",
            "official_url",
            "manual_priority_rank",
            "manual_priority_score",
            "local_target_folder",
        ]:
            if priority.get(field):
                merged[field] = priority[field]
        if not merged.get("quality_rank"):
            merged["quality_rank"] = row.get("priority_rank", "")
        out.append(merged)
    return sorted(out, key=lambda row: (safe_int(row.get("quality_rank")), safe_int(row.get("manual_priority_rank")), row.get("country", ""), row.get("wave", "")))


def select_financial_6_country(candidates: list[dict[str, str]]) -> list[dict[str, str]]:
    selected = []
    seen_countries: set[str] = set()
    for row in candidates:
        if row.get("quality_has_main_financial_core") != "1":
            continue
        country = row.get("country", "")
        if not country or country in seen_countries:
            continue
        selected.append(row)
        seen_countries.add(country)
        if len(seen_countries) >= 6:
            break
    return selected


def select_double_failure_10_wave(candidates: list[dict[str, str]]) -> list[dict[str, str]]:
    return [row for row in candidates if row.get("quality_has_double_failure_core") == "1"][:10]


def select_panel_sequences(candidates: list[dict[str, str]], max_per_country: int = 3) -> list[dict[str, str]]:
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in candidates:
        if row.get("quality_has_main_financial_core") == "1":
            grouped[row.get("country", "")].append(row)
    selected = []
    for country, rows in sorted(grouped.items()):
        if not country or len(rows) < 2:
            continue
        selected.extend(rows[:max_per_country])
    selected.sort(key=lambda row: (safe_int(row.get("quality_rank")), row.get("country", ""), row.get("wave", "")))
    return selected


def select_access_secondary(candidates: list[dict[str, str]]) -> list[dict[str, str]]:
    return [row for row in candidates if row.get("quality_download_priority_tier") == "tier_3_quality_supported_access_only_download"]


def count_by_id(rows: list[dict[str, str]], id_field: str = "idno") -> Counter[str]:
    return Counter(row.get(id_field, "") for row in rows if row.get(id_field, ""))


def list_by_id(rows: list[dict[str, str]], id_field: str = "idno") -> dict[str, list[dict[str, str]]]:
    out: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        idno = row.get(id_field, "")
        if idno:
            out[idno].append(row)
    return out


def raw_counts_by_id(rows: list[dict[str, str]]) -> Counter[str]:
    counts: Counter[str] = Counter()
    for row in rows:
        idno = row.get("idno", "")
        if idno:
            counts[idno] += 1
    return counts


def expected_file_names(rows: list[dict[str, str]], concepts: list[str], limit: int = 10) -> str:
    names = []
    for row in rows:
        cats = split_values(row.get("candidate_categories", ""))
        hvars = split_values(row.get("candidate_harmonized_variables", ""))
        joined = set(cats + hvars)
        if any(concept in joined or concept in row.get("candidate_harmonized_variables", "") for concept in concepts):
            names.append(row.get("expected_file_name", ""))
    return compact(names, limit)


def module_names(rows: list[dict[str, str]], concepts: list[str], limit: int = 10) -> str:
    names = []
    for row in rows:
        indicated = split_values(row.get("required_concepts_indicated", ""))
        categories = split_values(row.get("candidate_categories", ""))
        if any(concept in indicated or concept in categories for concept in concepts):
            label = row.get("file_name", "")
            if label:
                names.append(f"{label} [{row.get('candidate_categories', '')}]")
    return compact(names, limit)


def build_target_rows(
    sets: dict[str, list[dict[str, str]]],
    intake_by_id: dict[str, dict[str, str]],
    expected_by_id: dict[str, list[dict[str, str]]],
    concepts_by_id: dict[str, list[dict[str, str]]],
    protocol_count_by_id: Counter[str],
    raw_file_counts: Counter[str],
    raw_variable_counts: Counter[str],
) -> list[dict[str, str]]:
    why = {
        "financial_6_country_probe": "first manual-download set to test the Phase 13 rule requiring at least 6 countries with consumption/OOP/geography/timing",
        "double_failure_10_wave_probe": "first 10 metadata-supported waves to test whether financial hardship plus forgone-care outcomes can be audited",
        "multi_wave_panel_sequence_probe": "multi-wave countries for timing, leave-wave validation, and possible fixed-effect designs after raw verification",
        "secondary_access_only_probe": "access-only candidates kept separate from financial-protection samples unless harmonization later supports pooling",
    }
    rows = []
    for set_name, selected in sets.items():
        for rank, row in enumerate(selected, start=1):
            idno = row.get("idno", "")
            intake = intake_by_id.get(idno, {})
            expected = expected_by_id.get(idno, [])
            expected_not_present = sum(1 for item in expected if item.get("expected_file_status") == "not_present")
            rows.append(
                {
                    "acquisition_set": set_name,
                    "target_rank": str(rank),
                    "country": row.get("country", ""),
                    "survey_name": row.get("survey_name", ""),
                    "wave": row.get("wave", ""),
                    "idno": idno,
                    "quality_rank": row.get("quality_rank", ""),
                    "quality_download_priority_tier": row.get("quality_download_priority_tier", ""),
                    "official_url": row.get("official_url", ""),
                    "local_target_folder": row.get("local_target_folder", f"temp/raw_downloads/{idno}/"),
                    "raw_intake_status": intake.get("intake_status", "not_in_intake_manifest"),
                    "expected_module_rows": intake.get("expected_module_rows", str(len(expected))),
                    "expected_core_module_rows": intake.get("expected_core_module_rows", ""),
                    "expected_not_present_rows": str(expected_not_present),
                    "raw_file_inventory_rows": str(raw_file_counts[idno]),
                    "raw_variable_catalog_rows": str(raw_variable_counts[idno]),
                    "high_confidence_rows": row.get("high_confidence_rows", ""),
                    "moderate_confidence_rows": row.get("moderate_confidence_rows", ""),
                    "concept_rows_to_verify": str(len(concepts_by_id.get(idno, []))),
                    "protocol_rows_to_verify": str(protocol_count_by_id[idno]),
                    "why_selected": why.get(set_name, "metadata-prioritized acquisition target"),
                    "required_evidence_after_download": "raw files present; raw schemas extracted; raw variables matched; units/recall/keys/missing codes verified; no final sample selection before audit passes",
                    "not_final_sample_guardrail": "metadata acquisition target only; not a final analytical sample and not evidence of causal or ML readiness",
                }
            )
    return rows


def build_bundle_rows(
    targets: list[dict[str, str]],
    expected_by_id: dict[str, list[dict[str, str]]],
    modules_by_id: dict[str, list[dict[str, str]]],
    concepts_by_id: dict[str, list[dict[str, str]]],
) -> list[dict[str, str]]:
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in targets:
        grouped[row["idno"]].append(row)
    rows = []
    for rank, (idno, items) in enumerate(sorted(grouped.items(), key=lambda kv: min(safe_int(row.get("quality_rank")) for row in kv[1])), start=1):
        first = sorted(items, key=lambda row: safe_int(row.get("quality_rank")))[0]
        expected = expected_by_id.get(idno, [])
        modules = modules_by_id.get(idno, [])
        concepts = concepts_by_id.get(idno, [])
        concept_names = compact([row.get("concept", "") for row in concepts], 20)
        rows.append(
            {
                "bundle_rank": str(rank),
                "country": first.get("country", ""),
                "survey_name": first.get("survey_name", ""),
                "wave": first.get("wave", ""),
                "idno": idno,
                "included_acquisition_sets": compact([row.get("acquisition_set", "") for row in items], 8),
                "official_url": first.get("official_url", ""),
                "local_target_folder": first.get("local_target_folder", f"temp/raw_downloads/{idno}/"),
                "raw_intake_status": first.get("raw_intake_status", ""),
                "download_scope": "download full original raw package and all documentation; use module names only as first-pass verification priorities",
                "top_modules_to_verify_first": module_names(modules, FINANCIAL_CORE_CONCEPTS + ACCESS_CORE_CONCEPTS + GEOGRAPHY_TIMING_DESIGN_CONCEPTS, 12),
                "financial_core_expected_files": expected_file_names(expected, FINANCIAL_CORE_CONCEPTS, 10),
                "access_core_expected_files": expected_file_names(expected, ACCESS_CORE_CONCEPTS, 10),
                "geography_timing_design_expected_files": expected_file_names(expected, GEOGRAPHY_TIMING_DESIGN_CONCEPTS, 10),
                "concepts_to_verify": concept_names,
                "post_download_commands": "python script/17_audit_raw_downloads.py; python script/03_inspect_raw_schemas.py; python script/29_build_raw_variable_verification_protocol.py; python script/33_build_harmonization_recipe_gate.py",
                "manual_action": "place original archives/files in local_target_folder, keeping source filenames intact",
                "guardrail": "do not create temp/harmonization_recipe.csv or data outputs until raw verification passes",
            }
        )
    return rows


def build_summary_rows(targets: list[dict[str, str]], bundles: list[dict[str, str]], quality_rows: list[dict[str, str]], raw_file_rows: list[dict[str, str]], raw_variable_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    set_counts = Counter(row.get("acquisition_set", "") for row in targets)
    country_counts = Counter(row.get("country", "") for row in targets)
    tier_counts = Counter(row.get("quality_download_priority_tier", "") for row in targets)
    rows = [
        {"metric": "target_rows", "value": str(len(targets)), "interpretation": "Acquisition target rows across all probe sets."},
        {"metric": "unique_bundle_datasets", "value": str(len(bundles)), "interpretation": "Unique dataset folders to populate."},
        {"metric": "unique_countries_in_targets", "value": str(len({row.get('country', '') for row in targets if row.get('country', '')})), "interpretation": "Countries represented by metadata-only targets."},
        {"metric": "financial_core_candidate_rows", "value": str(sum(1 for row in quality_rows if row.get("quality_has_main_financial_core") == "1")), "interpretation": "Metadata-only rows with budget/OOP/weight/timing/geography."},
        {"metric": "double_failure_candidate_rows", "value": str(sum(1 for row in quality_rows if row.get("quality_has_double_failure_core") == "1")), "interpretation": "Metadata-only rows with financial and access core indicators."},
        {"metric": "raw_file_inventory_rows", "value": str(len(raw_file_rows)), "interpretation": "Raw file rows currently inspected."},
        {"metric": "raw_variable_catalog_rows", "value": str(len(raw_variable_rows)), "interpretation": "Raw variable rows currently inspected."},
        {"metric": "target_rows_ready_for_analysis", "value": "0", "interpretation": "Targets are metadata-only until raw verification and harmonization pass."},
    ]
    for set_name, count in sorted(set_counts.items()):
        rows.append({"metric": f"target_set_{set_name}", "value": str(count), "interpretation": "Acquisition target count by probe set."})
    for tier, count in sorted(tier_counts.items()):
        rows.append({"metric": f"target_quality_tier_{tier}", "value": str(count), "interpretation": "Acquisition target count by metadata tier."})
    for country, count in sorted(country_counts.items()):
        rows.append({"metric": f"target_country_{country}", "value": str(count), "interpretation": "Acquisition target count by country across probe sets."})
    return rows


def markdown_count_table(counter: Counter[str], label: str) -> str:
    lines = [f"| {label} | Count |", "|---|---:|"]
    for key, count in counter.most_common():
        lines.append(f"| {key or 'blank'} | {count} |")
    return "\n".join(lines)


def markdown_table(rows: list[dict[str, str]], columns: list[str], limit: int = 20) -> str:
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


def write_report(targets: list[dict[str, str]], bundles: list[dict[str, str]], summary: list[dict[str, str]]) -> None:
    set_counts = Counter(row.get("acquisition_set", "") for row in targets)
    country_counts = Counter(row.get("country", "") for row in targets)
    summary_table = "\n".join(f"| {row['metric']} | {row['value']} | {row['interpretation']} |" for row in summary)
    REPORT_PATH.write_text(
        f"""# Minimum Viable Acquisition Plan

Status: metadata-only acquisition plan. These targets are not final analytical samples and do not prove outcome, climate-linkage, prediction, reduced-form, causal-ML, or policy-learning readiness.

## Purpose

This plan converts the objective's first hard no-go thresholds into a practical manual-download sequence:

- a six-country financial-core probe for consumption/OOP/geography/timing feasibility;
- a ten-wave double-failure probe for financial hardship plus forgone-care feasibility;
- multi-wave/panel sequence probes for timing, leave-wave validation, and possible fixed-effect designs;
- access-only secondary probes kept separate from the main financial-protection sample.

## Counts

| Metric | Value | Interpretation |
|---|---:|---|
{summary_table}

## Acquisition Sets

{markdown_count_table(set_counts, 'Acquisition set')}

## Country Coverage

{markdown_count_table(country_counts, 'Country')}

## First Bundle Rows

{markdown_table(bundles, ['bundle_rank', 'country', 'wave', 'idno', 'included_acquisition_sets', 'raw_intake_status', 'local_target_folder'], 20) if bundles else 'No bundles were generated.'}

## Guardrails

- Download the full original raw package and documentation for a target dataset; do not rely only on listed modules.
- Listed modules are first-pass verification priorities derived from metadata labels.
- Do not call these rows final sample selections.
- Do not build `data/` outputs until raw files, schemas, variables, units, recall periods, merge keys, missing codes, and lineage pass.
- Re-run `python script/17_audit_raw_downloads.py`, `python script/03_inspect_raw_schemas.py`, `python script/29_build_raw_variable_verification_protocol.py`, and `python script/33_build_harmonization_recipe_gate.py` after placing files.

## Outputs

- `result/minimum_viable_acquisition_targets.csv`
- `temp/minimum_viable_download_bundles.csv`
- `result/minimum_viable_acquisition_summary.csv`
""",
        encoding="utf-8",
    )


def main() -> None:
    ensure_dirs()
    quality_rows = read_csv_dicts(QUALITY_PATH)
    priorities = priority_index(read_csv_dicts(PRIORITY_PATH))
    candidates = quality_candidates(quality_rows, priorities)
    intake_by_id = {row.get("dataset_idno", ""): row for row in read_csv_dicts(INTAKE_PATH) if row.get("dataset_idno")}
    expected_by_id = list_by_id(read_csv_dicts(EXPECTED_PATH), "dataset_idno")
    concepts_by_id = list_by_id(read_csv_dicts(CONCEPT_PATH), "idno")
    modules_by_id = list_by_id(read_csv_dicts(MODULE_PATH), "idno")
    protocol_count_by_id = count_by_id(read_csv_dicts(PROTOCOL_PATH), "idno")
    raw_files = read_csv_dicts(RAW_FILE_PATH)
    raw_variables = read_csv_dicts(RAW_VARIABLE_PATH)
    raw_file_counts = raw_counts_by_id(raw_files)
    raw_variable_counts = raw_counts_by_id(raw_variables)

    sets = {
        "financial_6_country_probe": select_financial_6_country(candidates),
        "double_failure_10_wave_probe": select_double_failure_10_wave(candidates),
        "multi_wave_panel_sequence_probe": select_panel_sequences(candidates),
        "secondary_access_only_probe": select_access_secondary(candidates),
    }
    targets = build_target_rows(sets, intake_by_id, expected_by_id, concepts_by_id, protocol_count_by_id, raw_file_counts, raw_variable_counts)
    bundles = build_bundle_rows(targets, expected_by_id, modules_by_id, concepts_by_id)
    summary = build_summary_rows(targets, bundles, quality_rows, raw_files, raw_variables)

    write_csv(TARGETS_PATH, targets, TARGET_COLUMNS)
    write_csv(BUNDLES_PATH, bundles, BUNDLE_COLUMNS)
    write_csv(SUMMARY_PATH, summary, SUMMARY_COLUMNS)
    write_report(targets, bundles, summary)
    append_log(TEMP_DIR / "audit_log.md", f"Minimum viable acquisition plan target_rows={len(targets)} bundle_rows={len(bundles)}.")
    print(f"Minimum viable acquisition plan target_rows={len(targets)} bundle_rows={len(bundles)}.")


if __name__ == "__main__":
    main()
