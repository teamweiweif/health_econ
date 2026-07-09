from __future__ import annotations

import csv
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from common import REPORT_DIR, RESULT_DIR, TEMP_DIR, append_log, ensure_dirs, write_csv


CHECKLIST_PATH = TEMP_DIR / "first_batch_raw_acquisition_checklist.csv"
FILE_TARGETS_PATH = TEMP_DIR / "first_batch_raw_file_targets.csv"
ACCESS_PROBE_PATH = TEMP_DIR / "first_batch_official_raw_access_probe.csv"
DATASET_GATE_PATH = RESULT_DIR / "first_batch_dataset_verification_gate.csv"

HANDOFF_PATH = TEMP_DIR / "first_batch_manual_download_handoff.csv"
FILE_QUEUE_PATH = TEMP_DIR / "first_batch_manual_download_file_queue.csv"
SUMMARY_PATH = RESULT_DIR / "first_batch_manual_download_handoff_summary.csv"
REPORT_PATH = REPORT_DIR / "first_batch_manual_download_handoff.md"

POST_DOWNLOAD_COMMANDS = [
    "python script/17_audit_raw_downloads.py",
    "python script/03_inspect_raw_schemas.py",
    "python script/29_build_raw_variable_verification_protocol.py",
    "python script/33_build_harmonization_recipe_gate.py",
    "python script/35_build_empirical_readiness_dashboard.py",
    "python script/37_build_first_batch_raw_acquisition_checklist.py",
    "python script/38_build_first_batch_raw_verification_workbook.py",
]

HANDOFF_COLUMNS = [
    "batch_rank",
    "country",
    "survey_name",
    "wave",
    "idno",
    "included_acquisition_sets",
    "official_url",
    "final_url",
    "http_status",
    "access_gate_detected",
    "direct_raw_route_status",
    "manual_action_status",
    "register_link",
    "request_or_terms_links",
    "saved_access_snapshot",
    "snapshot_sha256",
    "local_target_folder",
    "raw_intake_status",
    "raw_file_inventory_rows",
    "raw_variable_catalog_rows",
    "expected_missing_rows",
    "core_file_queue_rows",
    "total_file_queue_rows",
    "financial_core_expected_files",
    "geography_timing_design_expected_files",
    "dataset_gate_status",
    "handoff_status",
    "manual_download_scope",
    "immediate_post_download_commands",
    "pass_after_download_evidence",
    "fail_closed_stop_rule",
]

FILE_QUEUE_COLUMNS = [
    "batch_rank",
    "idno",
    "country",
    "wave",
    "file_name",
    "target_reasons",
    "source_fields",
    "module_priority_role",
    "candidate_categories",
    "candidate_harmonized_variables",
    "candidate_variable_count",
    "candidate_raw_variables_examples",
    "expected_file_status",
    "present_matching_files",
    "verification_action",
]

SUMMARY_COLUMNS = ["metric", "value", "interpretation"]


def read_csv_dicts(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def safe_int(value: Any, default: int = 0) -> int:
    try:
        return int(float(str(value).strip()))
    except (TypeError, ValueError):
        return default


def join_unique(values: list[str]) -> str:
    out: list[str] = []
    seen: set[str] = set()
    for value in values:
        for part in str(value or "").split(";"):
            item = part.strip()
            if not item or item in seen:
                continue
            out.append(item)
            seen.add(item)
    return ";".join(out)


def indexed(rows: list[dict[str, str]], key: str) -> dict[str, dict[str, str]]:
    return {row.get(key, ""): row for row in rows if row.get(key)}


def handoff_status(checklist: dict[str, str], probe: dict[str, str], gate: dict[str, str]) -> str:
    raw_files = safe_int(gate.get("raw_file_inventory_rows") or checklist.get("raw_tabular_file_count"))
    raw_variables = safe_int(gate.get("raw_variable_catalog_rows"))
    if raw_files > 0 and raw_variables > 0:
        return "ready_for_raw_schema_and_value_audit"
    if probe.get("access_gate_detected") == "1":
        return "manual_account_terms_download_required"
    if probe.get("direct_raw_route_status") == "possible_direct_raw_links_unverified":
        return "manual_direct_link_review_required"
    return "manual_access_review_required"


def build_file_queue(file_targets: list[dict[str, str]]) -> list[dict[str, str]]:
    grouped: dict[tuple[str, str], dict[str, Any]] = {}
    for row in file_targets:
        key = (row.get("idno", ""), row.get("file_name", ""))
        if not key[0] or not key[1]:
            continue
        item = grouped.setdefault(
            key,
            {
                "batch_rank": row.get("batch_rank", ""),
                "idno": row.get("idno", ""),
                "country": row.get("country", ""),
                "wave": row.get("wave", ""),
                "file_name": row.get("file_name", ""),
                "target_reasons": [],
                "source_fields": [],
                "module_priority_role": row.get("module_priority_role", ""),
                "candidate_categories": [],
                "candidate_harmonized_variables": [],
                "candidate_variable_count": 0,
                "candidate_raw_variables_examples": [],
                "expected_file_status": row.get("expected_file_status", ""),
                "present_matching_files": row.get("present_matching_files", ""),
                "verification_action": row.get("verification_action", ""),
            },
        )
        item["target_reasons"].append(row.get("target_reason", ""))
        item["source_fields"].append(row.get("source_field", ""))
        item["candidate_categories"].append(row.get("candidate_categories", ""))
        item["candidate_harmonized_variables"].append(row.get("candidate_harmonized_variables", ""))
        item["candidate_raw_variables_examples"].append(row.get("candidate_raw_variables_examples", ""))
        item["candidate_variable_count"] = max(
            int(item["candidate_variable_count"]),
            safe_int(row.get("candidate_variable_count")),
        )

    queue: list[dict[str, str]] = []
    for item in grouped.values():
        queue.append(
            {
                "batch_rank": str(item["batch_rank"]),
                "idno": str(item["idno"]),
                "country": str(item["country"]),
                "wave": str(item["wave"]),
                "file_name": str(item["file_name"]),
                "target_reasons": join_unique(item["target_reasons"]),
                "source_fields": join_unique(item["source_fields"]),
                "module_priority_role": str(item["module_priority_role"]),
                "candidate_categories": join_unique(item["candidate_categories"]),
                "candidate_harmonized_variables": join_unique(item["candidate_harmonized_variables"]),
                "candidate_variable_count": str(item["candidate_variable_count"]),
                "candidate_raw_variables_examples": join_unique(item["candidate_raw_variables_examples"])[:500],
                "expected_file_status": str(item["expected_file_status"]),
                "present_matching_files": str(item["present_matching_files"]),
                "verification_action": str(item["verification_action"]),
            }
        )
    queue.sort(
        key=lambda row: (
            safe_int(row["batch_rank"], 9999),
            0 if "financial core file" in row["target_reasons"] else 1,
            0 if "geography/timing/design file" in row["target_reasons"] else 1,
            -safe_int(row["candidate_variable_count"]),
            row["file_name"],
        )
    )
    return queue


def build_handoff(
    checklist_rows: list[dict[str, str]],
    probe_by_idno: dict[str, dict[str, str]],
    gate_by_idno: dict[str, dict[str, str]],
    queue: list[dict[str, str]],
) -> list[dict[str, str]]:
    queue_counts = Counter(row["idno"] for row in queue)
    core_counts = Counter(row["idno"] for row in queue if "financial core file" in row["target_reasons"] or "geography/timing/design file" in row["target_reasons"])
    rows: list[dict[str, str]] = []
    for checklist in checklist_rows:
        idno = checklist.get("idno", "")
        probe = probe_by_idno.get(idno, {})
        gate = gate_by_idno.get(idno, {})
        rows.append(
            {
                "batch_rank": checklist.get("batch_rank", ""),
                "country": checklist.get("country", ""),
                "survey_name": checklist.get("survey_name", ""),
                "wave": checklist.get("wave", ""),
                "idno": idno,
                "included_acquisition_sets": checklist.get("included_acquisition_sets", ""),
                "official_url": checklist.get("official_url", ""),
                "final_url": probe.get("final_url", ""),
                "http_status": probe.get("http_status", ""),
                "access_gate_detected": probe.get("access_gate_detected", ""),
                "direct_raw_route_status": probe.get("direct_raw_route_status", ""),
                "manual_action_status": probe.get("manual_action_status", ""),
                "register_link": probe.get("register_link", ""),
                "request_or_terms_links": probe.get("request_or_terms_links", ""),
                "saved_access_snapshot": probe.get("saved_snapshot", ""),
                "snapshot_sha256": probe.get("snapshot_sha256", ""),
                "local_target_folder": checklist.get("local_target_folder", ""),
                "raw_intake_status": checklist.get("raw_intake_status", ""),
                "raw_file_inventory_rows": gate.get("raw_file_inventory_rows", "0"),
                "raw_variable_catalog_rows": gate.get("raw_variable_catalog_rows", "0"),
                "expected_missing_rows": checklist.get("expected_missing_rows", ""),
                "core_file_queue_rows": str(core_counts[idno]),
                "total_file_queue_rows": str(queue_counts[idno]),
                "financial_core_expected_files": checklist.get("financial_core_expected_files", ""),
                "geography_timing_design_expected_files": checklist.get("geography_timing_design_expected_files", ""),
                "dataset_gate_status": gate.get("current_gate_status", ""),
                "handoff_status": handoff_status(checklist, probe, gate),
                "manual_download_scope": "download complete original raw package plus all questionnaires, codebooks, data dictionaries, survey-design files, geography/GPS files if offered; keep source archive and filenames intact",
                "immediate_post_download_commands": "; ".join(POST_DOWNLOAD_COMMANDS),
                "pass_after_download_evidence": "raw_file_inventory rows for idno > 0; raw_variable_catalog rows for idno > 0; first-batch dataset gate no longer blocked_raw_files_absent",
                "fail_closed_stop_rule": "do not promote harmonization, outcomes, climate linkage, models, or causal claims until raw value, label, unit, recall-period, missing-code, merge-key, geography, and timing checks pass",
            }
        )
    rows.sort(key=lambda row: safe_int(row["batch_rank"], 9999))
    return rows


def build_summary(handoff: list[dict[str, str]], queue: list[dict[str, str]]) -> list[dict[str, str]]:
    handoff_counts = Counter(row["handoff_status"] for row in handoff)
    route_counts = Counter(row["direct_raw_route_status"] for row in handoff)
    queue_reason_counts: Counter[str] = Counter()
    for row in queue:
        for reason in row["target_reasons"].split(";"):
            if reason:
                queue_reason_counts[reason] += 1
    rows = [
        {"metric": "first_batch_handoff_rows", "value": str(len(handoff)), "interpretation": "Dataset-level manual download handoff rows."},
        {"metric": "first_batch_file_queue_rows", "value": str(len(queue)), "interpretation": "Deduplicated first-batch file/module queue rows."},
        {"metric": "first_batch_access_gate_rows", "value": str(sum(1 for row in handoff if row["access_gate_detected"] == "1")), "interpretation": "Dataset rows with official access-gate language."},
        {"metric": "first_batch_possible_direct_raw_route_rows", "value": str(sum(1 for row in handoff if row["direct_raw_route_status"] == "possible_direct_raw_links_unverified")), "interpretation": "Dataset rows with possible ungated direct raw route signals."},
        {"metric": "first_batch_raw_file_inventory_rows", "value": str(sum(safe_int(row["raw_file_inventory_rows"]) for row in handoff)), "interpretation": "Raw file inventory rows currently linked to handoff datasets."},
        {"metric": "first_batch_raw_variable_catalog_rows", "value": str(sum(safe_int(row["raw_variable_catalog_rows"]) for row in handoff)), "interpretation": "Raw variable catalog rows currently linked to handoff datasets."},
    ]
    for status, count in sorted(handoff_counts.items()):
        rows.append({"metric": f"handoff_status_{status or 'blank'}", "value": str(count), "interpretation": "Manual download handoff status count."})
    for status, count in sorted(route_counts.items()):
        rows.append({"metric": f"direct_raw_route_status_{status or 'blank'}", "value": str(count), "interpretation": "Direct raw route status count."})
    for reason, count in sorted(queue_reason_counts.items()):
        rows.append({"metric": f"file_queue_reason_{reason.replace('/', '_').replace(' ', '_')}", "value": str(count), "interpretation": "Deduplicated file queue target-reason count."})
    return rows


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


def markdown_count_table(counter: Counter[str], label: str) -> str:
    lines = [f"| {label} | Count |", "|---|---:|"]
    for key, count in counter.most_common():
        lines.append(f"| {key or 'blank'} | {count} |")
    return "\n".join(lines)


def write_report(handoff: list[dict[str, str]], queue: list[dict[str, str]], summary: list[dict[str, str]]) -> None:
    handoff_counts = Counter(row["handoff_status"] for row in handoff)
    route_counts = Counter(row["direct_raw_route_status"] for row in handoff)
    queue_by_idno: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in queue:
        queue_by_idno[row["idno"]].append(row)
    summary_table = "\n".join(f"| {row['metric']} | {row['value']} | {row['interpretation']} |" for row in summary)
    top_queue_lines: list[str] = []
    for row in handoff:
        idno = row["idno"]
        top_queue_lines.append(f"### {row['batch_rank']}. {idno}")
        top_queue_lines.append("")
        top_queue_lines.append(f"- Official URL: {row['official_url']}")
        top_queue_lines.append(f"- Local target folder: `{row['local_target_folder']}`")
        top_queue_lines.append(f"- Access status: `{row['handoff_status']}`; direct route: `{row['direct_raw_route_status']}`")
        top_queue_lines.append("")
        top_queue_lines.append(markdown_rows(queue_by_idno[idno], ["file_name", "target_reasons", "candidate_categories", "candidate_variable_count"], 8))
        top_queue_lines.append("")

    REPORT_PATH.write_text(
        f"""# First-Batch Manual Download Handoff

Status: manual-account handoff packet only. The official access probe found access-gate language for the first-batch datasets, and no raw file has been inspected. This packet tells a human exactly what to download and where to place it; it does not claim data access or raw verification.

## Summary

| Metric | Value | Interpretation |
|---|---:|---|
{summary_table}

## Handoff Status

{markdown_count_table(handoff_counts, 'Handoff status') if handoff else 'No handoff rows exist.'}

## Direct Raw Route Status

{markdown_count_table(route_counts, 'Direct raw route status') if handoff else 'No handoff rows exist.'}

## Dataset Actions

{markdown_rows(handoff, ['batch_rank', 'country', 'wave', 'idno', 'handoff_status', 'local_target_folder'], 20)}

## File Queue By Dataset

{chr(10).join(top_queue_lines) if top_queue_lines else 'No file queue rows exist.'}

## Manual Procedure

1. Open the official URL for a dataset and complete the required World Bank account, registration, request, or terms workflow.
2. Download the complete original raw package plus all questionnaires, codebooks, data dictionaries, survey-design files, and geography/GPS files if offered.
3. Place the original archives or files in the listed `temp/raw_downloads/<IDNO>/` folder. Keep source filenames intact.
4. Run the post-download commands listed in `temp/first_batch_manual_download_handoff.csv`.
5. Promote no country-wave until raw schemas, values, labels, units, recall periods, missing codes, merge keys, geography, and timing have passed the verification workbook.

## Guardrails

- Candidate files are metadata-derived inspection targets, not verified raw files.
- Access-page snapshots are evidence of the access workflow, not raw microdata.
- Do not create `temp/harmonization_recipe.csv`, clean `data/` outputs, outcomes, climate links, models, causal estimates, or policy simulations from this packet alone.

## Machine-Readable Outputs

- `temp/first_batch_manual_download_handoff.csv`
- `temp/first_batch_manual_download_file_queue.csv`
- `result/first_batch_manual_download_handoff_summary.csv`
""",
        encoding="utf-8",
    )


def main() -> None:
    ensure_dirs()
    checklist = read_csv_dicts(CHECKLIST_PATH)
    file_targets = read_csv_dicts(FILE_TARGETS_PATH)
    access_probe = read_csv_dicts(ACCESS_PROBE_PATH)
    dataset_gate = read_csv_dicts(DATASET_GATE_PATH)
    queue = build_file_queue(file_targets)
    handoff = build_handoff(checklist, indexed(access_probe, "idno"), indexed(dataset_gate, "idno"), queue)
    summary = build_summary(handoff, queue)
    write_csv(FILE_QUEUE_PATH, queue, FILE_QUEUE_COLUMNS)
    write_csv(HANDOFF_PATH, handoff, HANDOFF_COLUMNS)
    write_csv(SUMMARY_PATH, summary, SUMMARY_COLUMNS)
    write_report(handoff, queue, summary)
    append_log(TEMP_DIR / "audit_log.md", f"Built first-batch manual download handoff rows={len(handoff)} file_queue_rows={len(queue)}.")
    print(f"First-batch manual download handoff rows={len(handoff)} file_queue_rows={len(queue)}.")


if __name__ == "__main__":
    main()
