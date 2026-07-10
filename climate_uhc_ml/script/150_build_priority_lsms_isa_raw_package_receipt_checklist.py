from __future__ import annotations

import csv
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from common import PROJECT_ROOT, REPORT_DIR, RESULT_DIR, TEMP_DIR, append_log, ensure_dirs, write_csv


QUEUE_PATH = TEMP_DIR / "priority_lsms_isa_refocused_acquisition_queue.csv"
RAW_INTAKE_LEDGER_PATH = TEMP_DIR / "priority_lsms_isa_raw_package_intake_ledger.csv"
ARCHIVE_PREFLIGHT_PATH = TEMP_DIR / "priority_lsms_isa_archive_member_preflight.csv"
REQUIREMENT_WORKBOOK_PATH = TEMP_DIR / "priority_lsms_isa_raw_value_requirement_workbook.csv"
PUBLIC_DOC_DATASET_PATH = TEMP_DIR / "priority_lsms_isa_public_documentation_dataset_receipt.csv"
PUBLIC_DOC_RESOURCE_PATH = TEMP_DIR / "priority_lsms_isa_public_documentation_receipt.csv"

CHECKLIST_PATH = TEMP_DIR / "priority_lsms_isa_raw_package_receipt_checklist.csv"
REQUIREMENT_CHECKLIST_PATH = TEMP_DIR / "priority_lsms_isa_raw_package_requirement_receipt_checklist.csv"
SUMMARY_PATH = RESULT_DIR / "priority_lsms_isa_raw_package_receipt_checklist_summary.csv"
REPORT_PATH = REPORT_DIR / "priority_lsms_isa_raw_package_receipt_checklist.md"

RAW_ROOT = TEMP_DIR / "raw_downloads"

POST_RECEIPT_COMMANDS = (
    "python script/17_audit_raw_downloads.py; "
    "python script/144_build_priority_lsms_isa_raw_package_intake_packet.py; "
    "python script/145_build_priority_lsms_isa_archive_member_preflight.py; "
    "python script/149_build_priority_lsms_isa_raw_value_verification_workbook.py; "
    "python script/150_build_priority_lsms_isa_raw_package_receipt_checklist.py; "
    "python script/132_build_priority_analysis_dataset_synthesis_blueprint.py; "
    "python script/148_build_priority_lsms_isa_country_wave_promotion_packets.py; "
    "python script/127_enforce_promoted_data_gate.py; "
    "python script/36_build_direct_read_audit_bundle.py; "
    "python script/14_validate_workspace.py"
)

REQUIRED_PACKAGE_SCOPE = (
    "Complete unchanged World Bank official package for this IDNO, including raw "
    "microdata modules, documentation, questionnaires, codebooks, DDI/XML, and "
    "any geography or timing supplements that the get-microdata package provides."
)

DATASET_COLUMNS = [
    "download_priority_order",
    "queue_role",
    "country",
    "wave",
    "idno",
    "survey_name",
    "official_get_microdata_url",
    "local_target_folder",
    "required_package_scope",
    "current_original_file_count",
    "current_archive_file_count",
    "current_raw_tabular_file_count",
    "current_documentation_file_count",
    "public_documentation_status",
    "public_documentation_snapshot_count",
    "public_documentation_snapshot_paths",
    "raw_package_status",
    "intake_acceptance_status",
    "archive_preflight_status",
    "current_receipt_status",
    "next_action",
    "post_receipt_commands",
    "fill_download_account_or_source",
    "fill_received_package_file_names",
    "fill_received_documentation_file_names",
    "fill_download_date",
    "fill_original_package_sha256_manifest_done",
    "fill_terms_or_daa_confirmed",
    "fill_complete_package_received",
    "fill_ready_for_raw_value_review",
    "review_notes",
    "handoff_readme",
]

REQUIREMENT_COLUMNS = [
    "download_priority_order",
    "queue_role",
    "country",
    "wave",
    "idno",
    "survey_name",
    "requirement",
    "requirement_role",
    "candidate_variable_rows",
    "candidate_file_rows",
    "required_checks",
    "raw_package_status",
    "archive_preflight_status",
    "current_receipt_status",
    "current_verification_status",
    "fill_package_file_or_archive",
    "fill_archive_member_or_direct_file",
    "fill_documentation_file",
    "fill_checksum_verified",
    "fill_ready_for_raw_value_review",
    "fill_receipt_accepted",
    "review_notes",
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


def compact(values: list[str], limit: int = 6) -> str:
    seen: set[str] = set()
    out: list[str] = []
    for value in values:
        text = " ".join(clean(value).split())
        if text and text not in seen:
            out.append(text)
            seen.add(text)
        if len(out) >= limit:
            break
    return "; ".join(out)


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(PROJECT_ROOT)).replace("\\", "/")
    except ValueError:
        return str(path).replace("\\", "/")


def one_by_id(rows: list[dict[str, str]], field: str = "idno") -> dict[str, dict[str, str]]:
    out: dict[str, dict[str, str]] = {}
    for row in rows:
        idno = clean(row.get(field))
        if idno and idno not in out:
            out[idno] = row
    return out


def by_id(rows: list[dict[str, str]], field: str = "idno") -> dict[str, list[dict[str, str]]]:
    out: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        idno = clean(row.get(field))
        if idno:
            out[idno].append(row)
    return out


def raw_folder_path(folder: str, idno: str) -> Path:
    folder_clean = clean(folder).replace("\\", "/").strip("/")
    if folder_clean:
        return PROJECT_ROOT / folder_clean
    return RAW_ROOT / idno


def public_documentation_ready(row: dict[str, str]) -> bool:
    status = clean(row.get("public_documentation_receipt_status"))
    return status.startswith("complete_") and not clean(row.get("missing_core_resource_types"))


def receipt_status(raw_row: dict[str, str], archive_row: dict[str, str], public_documentation_count: int) -> str:
    if safe_int(raw_row.get("original_file_count")) == 0:
        return "blocked_no_original_package"
    raw_tabular_evidence = safe_int(raw_row.get("raw_tabular_file_count")) + safe_int(archive_row.get("archive_raw_tabular_member_rows"))
    if raw_tabular_evidence == 0:
        return "blocked_no_raw_tabular_file"
    documentation_evidence = safe_int(raw_row.get("documentation_file_count")) + safe_int(archive_row.get("archive_documentation_member_rows")) + public_documentation_count
    if documentation_evidence == 0:
        return "blocked_no_documentation_file"
    if clean(archive_row.get("archive_preflight_status")) != "ready_for_raw_receipt_schema_and_manual_review":
        return "receipt_candidate_needs_archive_preflight"
    return "ready_for_raw_value_review"


def next_action(status_value: str) -> str:
    if status_value == "blocked_no_original_package":
        return "Place the complete unchanged official raw package and all documentation in the target folder."
    if status_value == "blocked_no_raw_tabular_file":
        return "Confirm the received package contains raw tabular microdata files or archive members."
    if status_value == "blocked_no_documentation_file":
        return "Add official documentation, questionnaires, DDI/XML, or codebooks from the same package."
    if status_value == "receipt_candidate_needs_archive_preflight":
        return "Run the archive/direct-file preflight and confirm required raw/documentation members are visible."
    return "Proceed to raw value workbook review and fill only evidence-backed acceptance fields."


def markdown_table(rows: list[dict[str, str]], columns: list[str], limit: int = 30) -> str:
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


def build_dataset_rows(
    queue_rows: list[dict[str, str]],
    raw_by_id: dict[str, dict[str, str]],
    archive_by_id: dict[str, dict[str, str]],
    public_by_id: dict[str, dict[str, str]],
    public_resources_by_id: dict[str, list[dict[str, str]]],
) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for wave in queue_rows:
        idno = clean(wave.get("idno"))
        raw = raw_by_id.get(idno, {})
        archive = archive_by_id.get(idno, {})
        public = public_by_id.get(idno, {})
        public_resources = public_resources_by_id.get(idno, [])
        public_count = len(public_resources) if public_documentation_ready(public) else 0
        public_paths = compact([row.get("saved_path", "") for row in public_resources], 8)
        folder = raw_folder_path(clean(wave.get("local_target_folder")), idno)
        handoff_path = folder / "_PRIORITY_LSMS_ISA_RAW_PACKAGE_RECEIPT_CHECKLIST.md"
        status_value = receipt_status(raw, archive, public_count)
        rows.append(
            {
                "download_priority_order": clean(wave.get("download_priority_order")),
                "queue_role": clean(wave.get("queue_role")),
                "country": clean(wave.get("country")),
                "wave": clean(wave.get("wave")),
                "idno": idno,
                "survey_name": clean(wave.get("survey_name")),
                "official_get_microdata_url": clean(wave.get("official_get_microdata_url")),
                "local_target_folder": clean(wave.get("local_target_folder")),
                "required_package_scope": REQUIRED_PACKAGE_SCOPE,
                "current_original_file_count": str(safe_int(raw.get("original_file_count"))),
                "current_archive_file_count": str(safe_int(raw.get("archive_file_count"))),
                "current_raw_tabular_file_count": str(safe_int(raw.get("raw_tabular_file_count"))),
                "current_documentation_file_count": str(safe_int(raw.get("documentation_file_count"))),
                "public_documentation_status": clean(public.get("public_documentation_receipt_status")) or "missing",
                "public_documentation_snapshot_count": str(public_count),
                "public_documentation_snapshot_paths": public_paths,
                "raw_package_status": clean(raw.get("raw_package_status")) or "missing",
                "intake_acceptance_status": clean(raw.get("intake_acceptance_status")) or "missing",
                "archive_preflight_status": clean(archive.get("archive_preflight_status")) or "missing",
                "current_receipt_status": status_value,
                "next_action": next_action(status_value),
                "post_receipt_commands": POST_RECEIPT_COMMANDS,
                "fill_download_account_or_source": "",
                "fill_received_package_file_names": "",
                "fill_received_documentation_file_names": "",
                "fill_download_date": "",
                "fill_original_package_sha256_manifest_done": "",
                "fill_terms_or_daa_confirmed": "",
                "fill_complete_package_received": "",
                "fill_ready_for_raw_value_review": "",
                "review_notes": "",
                "handoff_readme": rel(handoff_path),
            }
        )
    return rows


def build_requirement_rows(
    requirement_workbook_rows: list[dict[str, str]],
    dataset_by_id: dict[str, dict[str, str]],
) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for row in requirement_workbook_rows:
        idno = clean(row.get("idno"))
        dataset = dataset_by_id.get(idno, {})
        rows.append(
            {
                "download_priority_order": clean(row.get("download_priority_order")),
                "queue_role": clean(row.get("queue_role")),
                "country": clean(row.get("country")),
                "wave": clean(row.get("wave")),
                "idno": idno,
                "survey_name": clean(row.get("survey_name")),
                "requirement": clean(row.get("requirement")),
                "requirement_role": clean(row.get("requirement_role")),
                "candidate_variable_rows": clean(row.get("candidate_variable_rows")),
                "candidate_file_rows": clean(row.get("candidate_file_rows")),
                "required_checks": clean(row.get("required_checks")),
                "raw_package_status": clean(dataset.get("intake_acceptance_status")) or clean(row.get("raw_package_status")) or "missing",
                "archive_preflight_status": clean(dataset.get("archive_preflight_status")) or clean(row.get("archive_preflight_status")) or "missing",
                "current_receipt_status": clean(dataset.get("current_receipt_status")) or "missing",
                "current_verification_status": clean(row.get("current_verification_status")) or "missing",
                "fill_package_file_or_archive": "",
                "fill_archive_member_or_direct_file": "",
                "fill_documentation_file": "",
                "fill_checksum_verified": "",
                "fill_ready_for_raw_value_review": "",
                "fill_receipt_accepted": "",
                "review_notes": "",
            }
        )
    return rows


def write_handoffs(
    dataset_rows: list[dict[str, str]],
    requirement_by_id: dict[str, list[dict[str, str]]],
) -> int:
    count = 0
    for row in dataset_rows:
        idno = clean(row.get("idno"))
        folder = raw_folder_path(clean(row.get("local_target_folder")), idno)
        folder.mkdir(parents=True, exist_ok=True)
        path = folder / "_PRIORITY_LSMS_ISA_RAW_PACKAGE_RECEIPT_CHECKLIST.md"
        req_rows = requirement_by_id.get(idno, [])
        path.write_text(
            f"""# Priority LSMS-ISA Raw Package Receipt Checklist

Dataset: `{idno}` - {row.get('country', '')} {row.get('wave', '')}

Official get-microdata URL: {row.get('official_get_microdata_url', '')}

Target folder: `{row.get('local_target_folder', '')}`

Current receipt status: `{row.get('current_receipt_status', '')}`

Required package scope: {REQUIRED_PACKAGE_SCOPE}

Official public documentation status: `{row.get('public_documentation_status', '')}`

Official public documentation snapshots: {row.get('public_documentation_snapshot_count', '0')}

## Receipt Fields To Fill

- Download account/source:
- Received package file names:
- Received documentation file names:
- Download date:
- Terms/DAA confirmed:
- SHA256 manifest completed:
- Complete package received:
- Ready for raw value review:

## Requirement Receipt Gate

{markdown_table(req_rows, ['requirement', 'requirement_role', 'candidate_variable_rows', 'candidate_file_rows', 'current_receipt_status', 'current_verification_status'], 12)}

## After Receipt

Run:

`{POST_RECEIPT_COMMANDS}`

## Stop Rule

Do not mark this wave as complete, value-verified, climate-linkage-ready, or
analysis-ready until the receipt fields and the raw-value workbook are filled
from original raw files and accepted.
""",
            encoding="utf-8",
        )
        count += 1
    return count


def build_summary(
    dataset_rows: list[dict[str, str]],
    requirement_rows: list[dict[str, str]],
    handoff_count: int,
) -> list[dict[str, str]]:
    dataset_status_counts = Counter(row.get("current_receipt_status", "") for row in dataset_rows)
    requirement_status_counts = Counter(row.get("current_receipt_status", "") for row in requirement_rows)
    package_received_rows = sum(1 for row in dataset_rows if safe_int(row.get("current_original_file_count")) > 0)
    complete_package_received_rows = dataset_status_counts.get("ready_for_raw_value_review", 0)
    rows = [
        {"metric": "priority_lsms_receipt_checklist_dataset_rows", "value": str(len(dataset_rows)), "interpretation": "Refocused LSMS/ISA dataset-level raw package receipt checklist rows."},
        {"metric": "priority_lsms_receipt_checklist_requirement_rows", "value": str(len(requirement_rows)), "interpretation": "Requirement-level receipt checklist rows joined to raw-value workbook gates."},
        {"metric": "priority_lsms_receipt_checklist_package_received_rows", "value": str(package_received_rows), "interpretation": "Datasets with at least one original non-generated package or documentation file in the target folder."},
        {"metric": "priority_lsms_receipt_checklist_public_documentation_snapshot_rows", "value": str(sum(safe_int(row.get("public_documentation_snapshot_count")) for row in dataset_rows)), "interpretation": "Saved official public documentation snapshots used as documentation evidence."},
        {"metric": "priority_lsms_receipt_checklist_complete_package_received_rows", "value": str(complete_package_received_rows), "interpretation": "Datasets whose local receipt appears complete enough for raw value review."},
        {"metric": "priority_lsms_receipt_checklist_ready_for_raw_value_review_rows", "value": str(complete_package_received_rows), "interpretation": "Dataset rows ready to proceed to raw value workbook review."},
        {"metric": "priority_lsms_receipt_checklist_blocked_no_original_package_rows", "value": str(dataset_status_counts.get("blocked_no_original_package", 0)), "interpretation": "Dataset rows still missing original official packages."},
        {"metric": "priority_lsms_receipt_checklist_blocked_requirement_rows", "value": str(len(requirement_rows) - requirement_status_counts.get("ready_for_raw_value_review", 0)), "interpretation": "Requirement rows blocked before raw value review."},
        {"metric": "priority_lsms_receipt_checklist_handoff_readmes_written", "value": str(handoff_count), "interpretation": "Per-wave raw-folder receipt checklist handoffs written."},
        {"metric": "priority_lsms_receipt_checklist_data_write_status", "value": "blocked_no_promoted_rows", "interpretation": "No country-wave may write to data/ from an unaccepted receipt checklist."},
        {"metric": "modeling_gate_status", "value": "blocked", "interpretation": "Models remain blocked until receipt, raw-value, climate-linkage, and promoted-registry thresholds pass."},
    ]
    for status_value, count in sorted(dataset_status_counts.items()):
        rows.append({"metric": f"priority_lsms_receipt_checklist_dataset_status_{status_value}", "value": str(count), "interpretation": "Dataset receipt status count."})
    for status_value, count in sorted(requirement_status_counts.items()):
        rows.append({"metric": f"priority_lsms_receipt_checklist_requirement_status_{status_value}", "value": str(count), "interpretation": "Requirement receipt status count."})
    return rows


def write_report(
    dataset_rows: list[dict[str, str]],
    requirement_rows: list[dict[str, str]],
    summary_rows: list[dict[str, str]],
) -> None:
    summary_table = "\n".join(f"| {row['metric']} | {row['value']} | {row['interpretation']} |" for row in summary_rows)
    REPORT_PATH.write_text(
        f"""# Priority LSMS-ISA Raw Package Receipt Checklist

Status: fail-closed receipt checklist for the 19-wave LSMS/ISA dataset
promotion campaign. This turns the current blocker into a concrete receipt
control sheet: what package must arrive, where it should be placed, and which
checks must pass before raw-value review or dataset synthesis can begin.

This checklist does not verify raw values and does not promote data.

## Summary

| Metric | Value | Interpretation |
|---|---:|---|
{summary_table}

## Dataset Receipt Checklist Preview

{markdown_table(dataset_rows, ['download_priority_order', 'idno', 'country', 'wave', 'current_original_file_count', 'current_raw_tabular_file_count', 'current_documentation_file_count', 'public_documentation_snapshot_count', 'current_receipt_status', 'next_action'], 30)}

## Requirement Receipt Checklist Preview

{markdown_table(requirement_rows, ['download_priority_order', 'idno', 'requirement', 'candidate_variable_rows', 'candidate_file_rows', 'current_receipt_status', 'current_verification_status'], 80)}

## Machine-Readable Outputs

- `temp/priority_lsms_isa_raw_package_receipt_checklist.csv`
- `temp/priority_lsms_isa_raw_package_requirement_receipt_checklist.csv`
- `result/priority_lsms_isa_raw_package_receipt_checklist_summary.csv`

## Guardrails

- Generated markdown handoffs do not count as raw package receipt.
- A package is not complete unless original raw files and documentation are present.
- Receipt readiness only opens raw-value review; it does not accept variables, outcomes, climate linkage, or promoted data writes.
- ML remains blocked until at least 6 countries and 10 country-waves pass value verification and climate-linkage gates.
""",
        encoding="utf-8",
    )


def main() -> None:
    ensure_dirs()
    queue_rows = read_csv_dicts(QUEUE_PATH)
    raw_by_id = one_by_id(read_csv_dicts(RAW_INTAKE_LEDGER_PATH))
    archive_by_id = one_by_id(read_csv_dicts(ARCHIVE_PREFLIGHT_PATH))
    public_by_id = one_by_id(read_csv_dicts(PUBLIC_DOC_DATASET_PATH))
    public_resource_rows: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in read_csv_dicts(PUBLIC_DOC_RESOURCE_PATH):
        if clean(row.get("receipt_status")) in {"saved", "saved_existing"}:
            public_resource_rows[clean(row.get("idno"))].append(row)
    requirement_workbook_rows = read_csv_dicts(REQUIREMENT_WORKBOOK_PATH)

    dataset_rows = build_dataset_rows(queue_rows, raw_by_id, archive_by_id, public_by_id, public_resource_rows)
    requirement_rows = build_requirement_rows(requirement_workbook_rows, one_by_id(dataset_rows))
    handoff_count = write_handoffs(dataset_rows, by_id(requirement_rows))
    summary_rows = build_summary(dataset_rows, requirement_rows, handoff_count)

    write_csv(CHECKLIST_PATH, dataset_rows, DATASET_COLUMNS)
    write_csv(REQUIREMENT_CHECKLIST_PATH, requirement_rows, REQUIREMENT_COLUMNS)
    write_csv(SUMMARY_PATH, summary_rows, SUMMARY_COLUMNS)
    write_report(dataset_rows, requirement_rows, summary_rows)
    append_log(
        TEMP_DIR / "audit_log.md",
        f"Built priority LSMS/ISA raw package receipt checklist datasets={len(dataset_rows)} requirements={len(requirement_rows)}.",
    )
    print(
        "Priority LSMS/ISA raw package receipt checklist "
        f"datasets={len(dataset_rows)} requirements={len(requirement_rows)}."
    )


if __name__ == "__main__":
    main()
