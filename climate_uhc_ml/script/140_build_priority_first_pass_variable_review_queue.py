from __future__ import annotations

import csv
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from common import PROJECT_ROOT, REPORT_DIR, RESULT_DIR, TEMP_DIR, append_log, ensure_dirs, write_csv


WAVE_PLAN_PATH = RESULT_DIR / "priority_promotion_acquisition_wave_plan.csv"
CAMPAIGN_PATH = TEMP_DIR / "priority_threshold_acquisition_campaign.csv"
RECEIPT_PATH = TEMP_DIR / "priority_raw_package_receipt_ledger.csv"
REQUIREMENT_CHECKLIST_PATH = TEMP_DIR / "priority_promotion_verification_checklist.csv"
CONCEPT_TEMPLATE_PATH = TEMP_DIR / "priority_concept_verification_template.csv"
VARIABLE_TEMPLATE_PATH = TEMP_DIR / "priority_variable_verification_template.csv"

QUEUE_PATH = TEMP_DIR / "priority_first_pass_variable_review_queue.csv"
COVERAGE_PATH = TEMP_DIR / "priority_first_pass_requirement_coverage.csv"
SUMMARY_PATH = RESULT_DIR / "priority_first_pass_variable_review_summary.csv"
REPORT_PATH = REPORT_DIR / "priority_first_pass_variable_review_queue.md"

RAW_ROOT = TEMP_DIR / "raw_downloads"
MAX_VARIABLES_PER_CONCEPT = 2

FINANCIAL_CORE = {"total_consumption_or_income", "oop_health_expenditure", "survey_weight", "survey_timing", "climate_geography"}
DOUBLE_FAILURE_CORE = {"health_need", "care_or_barrier"}
DESIGN_CORE = {"household_id", "psu_cluster", "strata", "survey_weight", "survey_timing", "climate_geography"}

REQUIREMENTS = [
    {
        "requirement_id": "household_person_merge_keys",
        "mapped_concepts": ["household_id", "demographics"],
        "minimum_evidence": "Household/person IDs and module-level keys match across raw files; key cardinality and duplicates are documented.",
    },
    {
        "requirement_id": "weights_and_survey_design",
        "mapped_concepts": ["survey_weight", "psu_cluster", "strata"],
        "minimum_evidence": "Household/person weights, PSU/cluster, strata, and any design notes are verified from raw values and documentation.",
    },
    {
        "requirement_id": "consumption_or_income_aggregate",
        "mapped_concepts": ["total_consumption_or_income"],
        "minimum_evidence": "Survey-team consumption/income aggregate or documented reconstruction variables are verified with units and period.",
    },
    {
        "requirement_id": "oop_health_expenditure",
        "mapped_concepts": ["oop_health_expenditure"],
        "minimum_evidence": "OOP health spending variables are verified with payer scope, units, recall period, zero/missing semantics, and aggregation level.",
    },
    {
        "requirement_id": "illness_need_care_access",
        "mapped_concepts": ["health_need", "care_or_barrier", "insurance"],
        "minimum_evidence": "Illness/need denominator, care-seeking, forgone care, barrier categories, and insurance variables are verified.",
    },
    {
        "requirement_id": "survey_timing",
        "mapped_concepts": ["survey_timing"],
        "minimum_evidence": "Interview date/month/year or fieldwork timing is verified and can support pre-interview lag windows.",
    },
    {
        "requirement_id": "geography_climate_linkage",
        "mapped_concepts": ["climate_geography"],
        "minimum_evidence": "GPS, cluster, EA, or admin geography is verified with geolocation quality, displacement/suppression, and boundary/crosswalk notes.",
    },
    {
        "requirement_id": "missing_skip_units_recall",
        "mapped_concepts": [
            "household_id",
            "survey_weight",
            "total_consumption_or_income",
            "oop_health_expenditure",
            "health_need",
            "care_or_barrier",
            "survey_timing",
            "climate_geography",
        ],
        "minimum_evidence": "Missing codes, skip patterns, units, recall periods, valid ranges, and outlier handling are documented for all critical variables.",
    },
]

QUEUE_COLUMNS = [
    "acquisition_batch_rank",
    "batch_role",
    "campaign_phase",
    "threshold_role",
    "country",
    "wave",
    "idno",
    "requirement_id",
    "concept",
    "review_rank_within_wave",
    "review_rank_within_requirement_concept",
    "candidate_files",
    "candidate_raw_variable",
    "candidate_harmonized_variables",
    "raw_label",
    "metadata_confidence",
    "confidence_reason",
    "required_for",
    "is_financial_core",
    "is_double_failure_core",
    "is_design_core",
    "raw_receipt_status",
    "receipt_original_file_count",
    "current_concept_gate",
    "raw_file_status",
    "raw_variable_status",
    "verification_status",
    "first_pass_review_status",
    "post_download_review_action",
]

COVERAGE_COLUMNS = [
    "acquisition_batch_rank",
    "batch_role",
    "campaign_phase",
    "threshold_role",
    "country",
    "wave",
    "idno",
    "requirement_id",
    "mapped_concepts",
    "selected_concepts",
    "selected_variable_rows",
    "missing_concepts",
    "current_requirement_gate",
    "raw_receipt_status",
    "first_pass_requirement_status",
    "post_download_requirement_action",
]

SUMMARY_COLUMNS = ["metric", "value", "interpretation"]


def read_csv_dicts(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def clean(value: Any) -> str:
    return "" if value is None else str(value).strip()


def safe_int(value: Any, default: int = 0) -> int:
    try:
        text = clean(value)
        return int(float(text)) if text else default
    except (TypeError, ValueError):
        return default


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(PROJECT_ROOT)).replace("\\", "/")
    except ValueError:
        return str(path).replace("\\", "/")


def group(rows: list[dict[str, str]], field: str) -> dict[str, list[dict[str, str]]]:
    out: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        key = clean(row.get(field))
        if key:
            out[key].append(row)
    return out


def one_by_id(rows: list[dict[str, str]], field: str = "idno") -> dict[str, dict[str, str]]:
    out: dict[str, dict[str, str]] = {}
    for row in rows:
        key = clean(row.get(field))
        if key and key not in out:
            out[key] = row
    return out


def compact(values: list[str], limit: int = 20, sep: str = ";") -> str:
    out: list[str] = []
    seen: set[str] = set()
    for value in values:
        item = clean(value)
        if item and item not in seen:
            out.append(item)
            seen.add(item)
        if len(out) >= limit:
            break
    return sep.join(out)


def raw_folder_path(folder: str, idno: str) -> Path:
    folder_clean = clean(folder).replace("\\", "/").strip("/")
    if folder_clean.startswith("temp/raw_downloads/"):
        return PROJECT_ROOT / folder_clean
    if folder_clean:
        return RAW_ROOT / folder_clean
    return RAW_ROOT / idno


def confidence_rank(value: str) -> int:
    value = clean(value).lower()
    if value == "high":
        return 0
    if value == "moderate":
        return 1
    return 2


def variable_sort_key(row: dict[str, str]) -> tuple[int, int, int, str, str]:
    has_file = 0 if clean(row.get("candidate_files")) else 1
    return (
        confidence_rank(row.get("metadata_confidence", "")),
        safe_int(row.get("candidate_rank_within_concept"), 9999),
        has_file,
        clean(row.get("candidate_raw_variable")).lower(),
        clean(row.get("candidate_harmonized_variables")).lower(),
    )


def raw_package_received(receipt: dict[str, str]) -> bool:
    return safe_int(receipt.get("original_file_count")) > 0 or clean(receipt.get("receipt_status")) in {
        "complete_raw_package_candidate_ready_for_schema_and_manual_audit",
        "raw_targets_covered_documentation_review_needed",
    }


def review_status(receipt: dict[str, str], variable: dict[str, str], concept: dict[str, str]) -> str:
    if not raw_package_received(receipt):
        return "blocked_raw_package_not_received"
    if clean(variable.get("verification_status")) == "ready_for_manual_value_audit" and clean(concept.get("current_concept_gate")) == "ready_for_manual_value_label_unit_key_audit":
        return "ready_for_first_pass_raw_value_review_after_download"
    return "metadata_candidate_selected_raw_not_verified"


def requirement_status(receipt: dict[str, str], selected_count: int, missing_concepts: list[str], current_requirement_gate: str) -> str:
    if not raw_package_received(receipt):
        return "blocked_raw_package_not_received"
    if missing_concepts or selected_count == 0:
        return "blocked_missing_first_pass_variable_candidate"
    if current_requirement_gate == "ready_for_manual_requirement_audit":
        return "ready_for_first_pass_raw_value_review_after_download"
    return "metadata_candidates_selected_raw_not_verified"


def build_queue_and_coverage() -> tuple[list[dict[str, str]], list[dict[str, str]], list[str]]:
    waves = read_csv_dicts(WAVE_PLAN_PATH)
    campaign_by_id = one_by_id(read_csv_dicts(CAMPAIGN_PATH))
    receipt_by_id = one_by_id(read_csv_dicts(RECEIPT_PATH))
    requirement_by_key = {
        (clean(row.get("idno")), clean(row.get("requirement_id"))): row
        for row in read_csv_dicts(REQUIREMENT_CHECKLIST_PATH)
    }
    concept_by_key = {
        (clean(row.get("idno")), clean(row.get("concept"))): row
        for row in read_csv_dicts(CONCEPT_TEMPLATE_PATH)
    }
    variable_by_id = group(read_csv_dicts(VARIABLE_TEMPLATE_PATH), "idno")

    queue_rows: list[dict[str, str]] = []
    coverage_rows: list[dict[str, str]] = []
    handoffs: list[str] = []

    for wave in sorted(waves, key=lambda row: safe_int(row.get("acquisition_batch_rank"), 9999)):
        idno = clean(wave.get("idno"))
        campaign = campaign_by_id.get(idno, {})
        receipt = receipt_by_id.get(idno, {})
        vars_by_concept = group(variable_by_id.get(idno, []), "concept")
        selected_for_handoff: list[dict[str, str]] = []
        review_rank = 0

        for req in REQUIREMENTS:
            req_id = req["requirement_id"]
            mapped = req["mapped_concepts"]
            selected_concepts: list[str] = []
            missing_concepts: list[str] = []
            selected_count = 0

            for concept_name in mapped:
                concept = concept_by_key.get((idno, concept_name), {})
                candidates = sorted(vars_by_concept.get(concept_name, []), key=variable_sort_key)
                selected = candidates[:MAX_VARIABLES_PER_CONCEPT]
                if not selected:
                    missing_concepts.append(concept_name)
                    continue
                selected_concepts.append(concept_name)
                selected_count += len(selected)

                for rank_in_concept, variable in enumerate(selected, start=1):
                    review_rank += 1
                    row = {
                        "acquisition_batch_rank": wave.get("acquisition_batch_rank", ""),
                        "batch_role": wave.get("batch_role", ""),
                        "campaign_phase": campaign.get("campaign_phase", ""),
                        "threshold_role": campaign.get("threshold_role", ""),
                        "country": wave.get("country", ""),
                        "wave": wave.get("wave", ""),
                        "idno": idno,
                        "requirement_id": req_id,
                        "concept": concept_name,
                        "review_rank_within_wave": str(review_rank),
                        "review_rank_within_requirement_concept": str(rank_in_concept),
                        "candidate_files": variable.get("candidate_files", ""),
                        "candidate_raw_variable": variable.get("candidate_raw_variable", ""),
                        "candidate_harmonized_variables": variable.get("candidate_harmonized_variables", ""),
                        "raw_label": variable.get("raw_label", ""),
                        "metadata_confidence": variable.get("metadata_confidence", ""),
                        "confidence_reason": variable.get("confidence_reason", ""),
                        "required_for": variable.get("required_for", concept.get("required_for", "")),
                        "is_financial_core": "1" if concept_name in FINANCIAL_CORE else "0",
                        "is_double_failure_core": "1" if concept_name in DOUBLE_FAILURE_CORE else "0",
                        "is_design_core": "1" if concept_name in DESIGN_CORE else "0",
                        "raw_receipt_status": clean(receipt.get("receipt_status")) or clean(campaign.get("raw_receipt_status")) or "missing_receipt_status",
                        "receipt_original_file_count": clean(receipt.get("original_file_count")) or clean(campaign.get("receipt_original_file_count")) or "0",
                        "current_concept_gate": concept.get("current_concept_gate", "missing_concept_gate"),
                        "raw_file_status": variable.get("raw_file_status", ""),
                        "raw_variable_status": variable.get("raw_variable_status", ""),
                        "verification_status": variable.get("verification_status", ""),
                        "first_pass_review_status": review_status(receipt, variable, concept),
                        "post_download_review_action": "After complete original package receipt, inspect the listed file and variable for labels, values, missing and skip codes, units, recall period, merge level, and denominator semantics; then fill the verification templates and rerun the gates.",
                    }
                    queue_rows.append(row)
                    selected_for_handoff.append(row)

            checklist = requirement_by_key.get((idno, req_id), {})
            raw_status = clean(receipt.get("receipt_status")) or clean(campaign.get("raw_receipt_status")) or "missing_receipt_status"
            coverage_rows.append(
                {
                    "acquisition_batch_rank": wave.get("acquisition_batch_rank", ""),
                    "batch_role": wave.get("batch_role", ""),
                    "campaign_phase": campaign.get("campaign_phase", ""),
                    "threshold_role": campaign.get("threshold_role", ""),
                    "country": wave.get("country", ""),
                    "wave": wave.get("wave", ""),
                    "idno": idno,
                    "requirement_id": req_id,
                    "mapped_concepts": ";".join(mapped),
                    "selected_concepts": compact(selected_concepts),
                    "selected_variable_rows": str(selected_count),
                    "missing_concepts": compact(missing_concepts),
                    "current_requirement_gate": checklist.get("current_requirement_gate", "missing_requirement_gate"),
                    "raw_receipt_status": raw_status,
                    "first_pass_requirement_status": requirement_status(receipt, selected_count, missing_concepts, checklist.get("current_requirement_gate", "")),
                    "post_download_requirement_action": req["minimum_evidence"],
                }
            )

        handoffs.append(write_handoff(wave, campaign, selected_for_handoff))

    return queue_rows, coverage_rows, handoffs


def markdown_table(rows: list[dict[str, str]], columns: list[str], limit: int = 25) -> str:
    lines = ["| " + " | ".join(columns) + " |", "|" + "|".join("---" for _ in columns) + "|"]
    for row in rows[:limit]:
        values = []
        for column in columns:
            value = clean(row.get(column)).replace("|", "/")
            if len(value) > 120:
                value = value[:117] + "..."
            values.append(value)
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines)


def markdown_counter(counter: Counter[str], label: str) -> str:
    lines = [f"| {label} | Count |", "|---|---:|"]
    for key, count in counter.most_common():
        lines.append(f"| `{key or 'blank'}` | {count} |")
    return "\n".join(lines)


def write_handoff(wave: dict[str, str], campaign: dict[str, str], selected_rows: list[dict[str, str]]) -> str:
    idno = clean(wave.get("idno"))
    folder = raw_folder_path(wave.get("local_target_folder", ""), idno)
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / "_PRIORITY_FIRST_PASS_VARIABLE_REVIEW_QUEUE.md"
    path.write_text(
        f"""# Priority First-Pass Variable Review Queue

Dataset: `{idno}` - {wave.get('country', '')} {wave.get('wave', '')}

Campaign phase: {campaign.get('campaign_phase', '')}

Threshold role: {campaign.get('threshold_role', '')}

Current raw receipt: {campaign.get('raw_receipt_status', 'missing_receipt_status')}

This is a compact first-pass queue for post-download raw-value review. It does
not verify raw values, does not promote any dataset, and does not write to
`data/`.

## Selected Variables

{markdown_table(selected_rows, ['requirement_id', 'concept', 'candidate_files', 'candidate_raw_variable', 'metadata_confidence', 'first_pass_review_status'], 40)}

## Post-Download Rule

Use the queue only after the complete original raw package and documentation
are present. For each selected variable, inspect labels, raw values, missing and
skip codes, units, recall periods, merge level, and denominator semantics.
Then fill:

- `temp/priority_promotion_verification_checklist.csv`
- `temp/priority_concept_verification_template.csv`
- `temp/priority_variable_verification_template.csv`

Do not promote this wave until the manual verification decision gate, synthesis
blueprint, country-wave packet, promoted-data gate, and accepted CHIRPS/ERA5
linkage all pass.
""",
        encoding="utf-8",
    )
    return rel(path)


def build_summary(queue_rows: list[dict[str, str]], coverage_rows: list[dict[str, str]], handoffs: list[str]) -> list[dict[str, str]]:
    queue_status = Counter(row["first_pass_review_status"] for row in queue_rows)
    req_status = Counter(row["first_pass_requirement_status"] for row in coverage_rows)
    batch_roles = Counter(row["batch_role"] for row in coverage_rows if row["requirement_id"] == REQUIREMENTS[0]["requirement_id"])
    countries = {row["country"] for row in coverage_rows if row.get("country")}
    raw_received_ids = {
        row["idno"]
        for row in coverage_rows
        if row.get("raw_receipt_status") in {"complete_raw_package_candidate_ready_for_schema_and_manual_audit", "raw_targets_covered_documentation_review_needed"}
    }
    missing_requirement_coverage = sum(1 for row in coverage_rows if clean(row.get("missing_concepts")) or safe_int(row.get("selected_variable_rows")) == 0)
    ready_after_download = queue_status.get("ready_for_first_pass_raw_value_review_after_download", 0)
    rows = [
        {"metric": "priority_first_pass_dataset_rows", "value": str(len({row["idno"] for row in coverage_rows})), "interpretation": "Priority and backup country-waves covered by the first-pass review queue."},
        {"metric": "priority_first_pass_requirement_rows", "value": str(len(coverage_rows)), "interpretation": "Country-wave requirement coverage rows in the first-pass queue."},
        {"metric": "priority_first_pass_selected_variable_rows", "value": str(len(queue_rows)), "interpretation": "Selected metadata candidate variables for first-pass post-download review."},
        {"metric": "priority_first_pass_distinct_countries", "value": str(len(countries)), "interpretation": "Distinct countries covered by the first-pass queue."},
        {"metric": "priority_first_pass_priority_10_wave_rows", "value": str(batch_roles.get("priority_10_wave_batch", 0)), "interpretation": "Phase-1 priority waves covered."},
        {"metric": "priority_first_pass_backup_wave_rows", "value": str(batch_roles.get("sixth_country_backup_candidate", 0)), "interpretation": "Sixth-country backup waves covered."},
        {"metric": "priority_first_pass_missing_requirement_coverage_rows", "value": str(missing_requirement_coverage), "interpretation": "Requirement rows lacking at least one selected variable candidate for a mapped concept."},
        {"metric": "priority_first_pass_raw_package_received_rows", "value": str(len(raw_received_ids)), "interpretation": "Covered datasets with complete or target-covered original raw package receipt."},
        {"metric": "priority_first_pass_ready_after_download_rows", "value": str(ready_after_download), "interpretation": "Selected variable rows ready for immediate first-pass raw value review."},
        {"metric": "priority_first_pass_handoff_readmes_written", "value": str(len([path for path in handoffs if path])), "interpretation": "Per-wave first-pass queue handoff README files written."},
        {"metric": "modeling_gate_status", "value": "blocked", "interpretation": "Models remain blocked until promoted registry thresholds and accepted climate linkage pass."},
    ]
    for status, count in sorted(queue_status.items()):
        rows.append({"metric": f"first_pass_review_status_{status}", "value": str(count), "interpretation": "Selected variable first-pass status count."})
    for status, count in sorted(req_status.items()):
        rows.append({"metric": f"first_pass_requirement_status_{status}", "value": str(count), "interpretation": "Requirement first-pass status count."})
    return rows


def write_report(queue_rows: list[dict[str, str]], coverage_rows: list[dict[str, str]], summary: list[dict[str, str]]) -> None:
    queue_status = Counter(row["first_pass_review_status"] for row in queue_rows)
    req_status = Counter(row["first_pass_requirement_status"] for row in coverage_rows)
    concept_counts = Counter(row["concept"] for row in queue_rows)
    summary_table = "\n".join(f"| {row['metric']} | {row['value']} | {row['interpretation']} |" for row in summary)
    REPORT_PATH.write_text(
        f"""# Priority First-Pass Variable Review Queue

Status: compact review queue for the 13-wave priority/backup campaign. It
selects a minimum first-pass set of metadata candidate variables for each
country-wave promotion requirement. It is not raw-value verification and does
not promote any dataset.

## Summary

| Metric | Value | Interpretation |
|---|---:|---|
{summary_table}

## Selected Variable Status

{markdown_counter(queue_status, 'First-pass status') if queue_rows else 'No selected variable rows exist.'}

## Requirement Status

{markdown_counter(req_status, 'Requirement first-pass status') if coverage_rows else 'No requirement coverage rows exist.'}

## Concept Mix

{markdown_counter(concept_counts, 'Concept') if queue_rows else 'No concept rows exist.'}

## Coverage Preview

{markdown_table(coverage_rows, ['acquisition_batch_rank', 'idno', 'requirement_id', 'selected_variable_rows', 'missing_concepts', 'first_pass_requirement_status'], 30)}

## Selected Variable Preview

{markdown_table(queue_rows, ['acquisition_batch_rank', 'idno', 'requirement_id', 'concept', 'candidate_files', 'candidate_raw_variable', 'metadata_confidence', 'first_pass_review_status'], 40)}

## Use

1. Download the complete original raw package and documentation into each
   target folder.
2. Use this queue to inspect the first-pass variables for labels, raw values,
   missing and skip codes, units, recall periods, merge level, and denominator
   semantics.
3. Fill the existing requirement, concept, and variable verification templates.
4. Rerun `python script/129_build_priority_manual_verification_decision_gate.py`,
   `python script/132_build_priority_analysis_dataset_synthesis_blueprint.py`,
   `python script/134_build_priority_country_wave_promotion_packets.py`, and
   `python script/127_enforce_promoted_data_gate.py`.

## Machine-Readable Outputs

- `temp/priority_first_pass_variable_review_queue.csv`
- `temp/priority_first_pass_requirement_coverage.csv`
- `result/priority_first_pass_variable_review_summary.csv`
""",
        encoding="utf-8",
    )


def main() -> None:
    ensure_dirs()
    queue_rows, coverage_rows, handoffs = build_queue_and_coverage()
    summary = build_summary(queue_rows, coverage_rows, handoffs)
    write_csv(QUEUE_PATH, queue_rows, QUEUE_COLUMNS)
    write_csv(COVERAGE_PATH, coverage_rows, COVERAGE_COLUMNS)
    write_csv(SUMMARY_PATH, summary, SUMMARY_COLUMNS)
    write_report(queue_rows, coverage_rows, summary)
    append_log(
        TEMP_DIR / "audit_log.md",
        f"Built priority first-pass variable review queue rows={len(queue_rows)} requirements={len(coverage_rows)}.",
    )
    print(f"Priority first-pass variable review queue rows={len(queue_rows)} requirements={len(coverage_rows)}.")


if __name__ == "__main__":
    main()
