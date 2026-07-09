from __future__ import annotations

import csv
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from common import PROJECT_ROOT, REPORT_DIR, RESULT_DIR, TEMP_DIR, append_log, ensure_dirs, write_csv


WAVE_PLAN_PATH = RESULT_DIR / "priority_promotion_acquisition_wave_plan.csv"
DOSSIER_PATH = TEMP_DIR / "priority_official_download_dossier.csv"
FULL_FILE_INVENTORY_PATH = TEMP_DIR / "priority_official_full_file_inventory.csv"
FILE_QUEUE_PATH = RESULT_DIR / "priority_promotion_acquisition_file_queue.csv"
RAW_RECEIPT_PATH = TEMP_DIR / "priority_raw_package_receipt_ledger.csv"
PUBLIC_DOC_DATASET_PATH = TEMP_DIR / "priority_public_documentation_dataset_receipt.csv"
METADATA_DATASET_PATH = TEMP_DIR / "priority_official_metadata_dataset_evidence.csv"

LEDGER_PATH = TEMP_DIR / "priority_credentialed_raw_acquisition_ledger.csv"
FULL_MANIFEST_PATH = TEMP_DIR / "priority_credentialed_raw_full_file_manifest.csv"
CORE_CHECKLIST_PATH = TEMP_DIR / "priority_credentialed_raw_core_file_checklist.csv"
SUMMARY_PATH = RESULT_DIR / "priority_credentialed_raw_acquisition_summary.csv"
REPORT_PATH = REPORT_DIR / "priority_credentialed_raw_acquisition_ledger.md"

RAW_ROOT = TEMP_DIR / "raw_downloads"

POST_DOWNLOAD_COMMANDS = [
    "python script/17_audit_raw_downloads.py",
    "python script/128_build_priority_archive_member_preflight.py",
    "python script/130_build_priority_raw_package_receipt_ledger.py",
    "python script/03_inspect_raw_schemas.py",
    "python script/29_build_raw_variable_verification_protocol.py",
    "python script/33_build_harmonization_recipe_gate.py",
    "python script/125_build_priority_climate_linkage_preflight.py",
    "python script/126_build_priority_raw_verification_workbook.py",
    "python script/140_build_priority_first_pass_variable_review_queue.py",
    "python script/141_build_priority_download_execution_packet.py",
    "python script/129_build_priority_manual_verification_decision_gate.py",
    "python script/132_build_priority_analysis_dataset_synthesis_blueprint.py",
    "python script/134_build_priority_country_wave_promotion_packets.py",
    "python script/127_enforce_promoted_data_gate.py",
    "python script/36_build_direct_read_audit_bundle.py",
    "python script/14_validate_workspace.py",
]

LEDGER_COLUMNS = [
    "acquisition_batch_rank",
    "batch_role",
    "country",
    "wave",
    "idno",
    "catalog_id",
    "survey_name",
    "official_get_microdata_url",
    "register_url",
    "terms_or_request_urls",
    "local_target_folder",
    "official_full_file_rows",
    "priority_core_file_rows",
    "priority_core_file_names",
    "public_documentation_status",
    "official_metadata_evidence_status",
    "raw_receipt_status",
    "receipt_original_file_count",
    "receipt_priority_targets_missing",
    "download_scope",
    "credentialed_acquisition_status",
    "next_manual_action",
    "post_download_validation_commands",
    "handoff_readme",
]

FULL_MANIFEST_COLUMNS = [
    "acquisition_batch_rank",
    "batch_role",
    "country",
    "wave",
    "idno",
    "catalog_id",
    "metadata_file_name",
    "metadata_file_description",
    "cases",
    "variable_count",
    "unit_guess",
    "module_guess",
    "priority_core_target",
    "current_receipt_status",
    "expected_local_name_patterns",
    "download_review_action",
]

CORE_CHECKLIST_COLUMNS = [
    "acquisition_batch_rank",
    "batch_role",
    "country",
    "wave",
    "idno",
    "core_file_rank",
    "metadata_file_name",
    "metadata_file_description",
    "candidate_categories",
    "candidate_harmonized_variables",
    "expected_local_name_patterns",
    "current_receipt_status",
    "post_download_verification",
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


def normalize_name(value: str) -> str:
    base = Path(clean(value).replace("\\", "/")).name.lower()
    for suffix in [".tar.gz", ".tar.bz2", ".tar.xz", ".sas7bdat"]:
        if base.endswith(suffix):
            base = base[: -len(suffix)]
            break
    else:
        suffix = Path(base).suffix
        if suffix:
            base = base[: -len(suffix)]
    return re.sub(r"[^a-z0-9]+", "", base)


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


def compact(values: list[str], limit: int = 12) -> str:
    out: list[str] = []
    seen: set[str] = set()
    for value in values:
        item = " ".join(clean(value).split())
        if item and item not in seen:
            out.append(item)
            seen.add(item)
        if len(out) >= limit:
            break
    return ";".join(out)


def expected_patterns(file_name: str) -> str:
    name = clean(file_name)
    if not name:
        return ""
    suffix = Path(name).suffix.lower()
    if suffix:
        return ";".join([name, f"{Path(name).stem}.*", f"*{Path(name).stem}*"])
    extensions = [".dta", ".sav", ".por", ".sas7bdat", ".xpt", ".csv"]
    return ";".join([name, f"{name}.*"] + [f"{name}{ext}" for ext in extensions] + [f"*{name}*"])


def raw_folder_path(folder: str, idno: str) -> Path:
    folder_clean = clean(folder).replace("\\", "/").strip("/")
    if folder_clean:
        return PROJECT_ROOT / folder_clean
    return RAW_ROOT / idno


def markdown_table(rows: list[dict[str, str]], columns: list[str], limit: int = 20) -> str:
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


def write_handoff(row: dict[str, str], core_rows: list[dict[str, str]]) -> str:
    folder = raw_folder_path(row.get("local_target_folder", ""), row.get("idno", ""))
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / "_PRIORITY_CREDENTIALED_RAW_ACQUISITION.md"
    path.write_text(
        f"""# Priority Credentialed Raw Acquisition Handoff

Dataset: {row.get('idno', '')} - {row.get('country', '')} {row.get('wave', '')}

Official get-microdata URL: {row.get('official_get_microdata_url', '')}

Target folder: `{row.get('local_target_folder', '')}`

Current status: {row.get('credentialed_acquisition_status', '')}

Required scope: download the complete unchanged official raw package and all
documentation available after the official login/register/terms workflow. Do
not download only the priority core files if the interface offers a full
package/archive.

Priority core files to confirm after download:

{markdown_table(core_rows, ['core_file_rank', 'metadata_file_name', 'candidate_categories', 'candidate_harmonized_variables'], 20)}

After placing files here, rerun:

`{row.get('post_download_validation_commands', '')}`
""",
        encoding="utf-8",
    )
    return rel(path)


def build_outputs() -> tuple[list[dict[str, str]], list[dict[str, str]], list[dict[str, str]], list[dict[str, str]]]:
    waves = read_csv_dicts(WAVE_PLAN_PATH)
    dossier_by_id = one_by_id(read_csv_dicts(DOSSIER_PATH))
    full_by_id = by_id(read_csv_dicts(FULL_FILE_INVENTORY_PATH))
    queue_by_id = by_id(read_csv_dicts(FILE_QUEUE_PATH))
    receipt_by_id = one_by_id(read_csv_dicts(RAW_RECEIPT_PATH))
    public_by_id = one_by_id(read_csv_dicts(PUBLIC_DOC_DATASET_PATH))
    metadata_by_id = one_by_id(read_csv_dicts(METADATA_DATASET_PATH))

    ledger_rows: list[dict[str, str]] = []
    full_manifest_rows: list[dict[str, str]] = []
    core_checklist_rows: list[dict[str, str]] = []

    for wave in waves:
        idno = wave.get("idno", "")
        dossier = dossier_by_id.get(idno, {})
        receipt = receipt_by_id.get(idno, {})
        public = public_by_id.get(idno, {})
        metadata = metadata_by_id.get(idno, {})
        full_rows = full_by_id.get(idno, [])
        queue_rows = queue_by_id.get(idno, [])
        queue_by_name = {normalize_name(row.get("file_name", "")): row for row in queue_rows}
        core_rows = [row for row in full_rows if clean(row.get("priority_core_target")) == "1"]
        core_names = compact([row.get("metadata_file_name", "") for row in core_rows], limit=20)
        receipt_status = receipt.get("receipt_status", "missing")
        original_files = safe_int(receipt.get("original_file_count"))
        missing_targets = safe_int(receipt.get("priority_targets_missing"))
        credentialed_status = (
            "downloaded_package_receipt_candidate"
            if original_files > 0 and missing_targets == 0
            else "partial_package_receipt_needs_review"
            if original_files > 0
            else "ready_for_credentialed_manual_download"
        )
        ledger_row = {
            "acquisition_batch_rank": wave.get("acquisition_batch_rank", ""),
            "batch_role": wave.get("batch_role", ""),
            "country": wave.get("country", ""),
            "wave": wave.get("wave", ""),
            "idno": idno,
            "catalog_id": dossier.get("catalog_id", ""),
            "survey_name": wave.get("survey_name", ""),
            "official_get_microdata_url": dossier.get("official_get_microdata_url", wave.get("official_url", "")),
            "register_url": dossier.get("register_url", ""),
            "terms_or_request_urls": dossier.get("terms_or_request_urls", ""),
            "local_target_folder": wave.get("local_target_folder", dossier.get("local_target_folder", "")),
            "official_full_file_rows": str(len(full_rows)),
            "priority_core_file_rows": str(len(core_rows)),
            "priority_core_file_names": core_names,
            "public_documentation_status": public.get("public_documentation_receipt_status", ""),
            "official_metadata_evidence_status": metadata.get("official_metadata_evidence_status", ""),
            "raw_receipt_status": receipt_status,
            "receipt_original_file_count": str(original_files),
            "receipt_priority_targets_missing": str(missing_targets),
            "download_scope": "complete_official_raw_package_plus_all_documentation",
            "credentialed_acquisition_status": credentialed_status,
            "next_manual_action": "Open official_get_microdata_url, log in or register if required, accept official terms/Data Access Agreement, download the complete unchanged raw package plus all documentation, and place all files in local_target_folder.",
            "post_download_validation_commands": clean(dossier.get("post_download_commands")) or "; ".join(POST_DOWNLOAD_COMMANDS),
            "handoff_readme": "",
        }

        for row in full_rows:
            full_manifest_rows.append(
                {
                    "acquisition_batch_rank": wave.get("acquisition_batch_rank", ""),
                    "batch_role": wave.get("batch_role", ""),
                    "country": wave.get("country", ""),
                    "wave": wave.get("wave", ""),
                    "idno": idno,
                    "catalog_id": dossier.get("catalog_id", ""),
                    "metadata_file_name": row.get("metadata_file_name", ""),
                    "metadata_file_description": row.get("metadata_file_description", ""),
                    "cases": row.get("cases", ""),
                    "variable_count": row.get("variable_count", ""),
                    "unit_guess": row.get("unit_guess", ""),
                    "module_guess": row.get("module_guess", ""),
                    "priority_core_target": row.get("priority_core_target", ""),
                    "current_receipt_status": row.get("current_receipt_status", ""),
                    "expected_local_name_patterns": expected_patterns(row.get("metadata_file_name", "")),
                    "download_review_action": row.get("download_review_action", ""),
                }
            )

        per_wave_core_checklist: list[dict[str, str]] = []
        for idx, row in enumerate(core_rows, start=1):
            queue = queue_by_name.get(normalize_name(row.get("metadata_file_name", "")), {})
            checklist_row = {
                "acquisition_batch_rank": wave.get("acquisition_batch_rank", ""),
                "batch_role": wave.get("batch_role", ""),
                "country": wave.get("country", ""),
                "wave": wave.get("wave", ""),
                "idno": idno,
                "core_file_rank": str(idx),
                "metadata_file_name": row.get("metadata_file_name", ""),
                "metadata_file_description": row.get("metadata_file_description", ""),
                "candidate_categories": queue.get("candidate_categories", ""),
                "candidate_harmonized_variables": queue.get("candidate_harmonized_variables", ""),
                "expected_local_name_patterns": expected_patterns(row.get("metadata_file_name", "")),
                "current_receipt_status": row.get("current_receipt_status", ""),
                "post_download_verification": "Confirm file exists directly or inside official archive, then run receipt, archive-member, raw schema, manual value, climate preflight, and promoted-data gates.",
            }
            core_checklist_rows.append(checklist_row)
            per_wave_core_checklist.append(checklist_row)

        ledger_row["handoff_readme"] = write_handoff(ledger_row, per_wave_core_checklist)
        ledger_rows.append(ledger_row)

    summary = build_summary(ledger_rows, full_manifest_rows, core_checklist_rows)
    return ledger_rows, full_manifest_rows, core_checklist_rows, summary


def build_summary(
    ledger_rows: list[dict[str, str]],
    full_manifest_rows: list[dict[str, str]],
    core_checklist_rows: list[dict[str, str]],
) -> list[dict[str, str]]:
    role_counts = Counter(row["batch_role"] for row in ledger_rows)
    status_counts = Counter(row["credentialed_acquisition_status"] for row in ledger_rows)
    public_ready = sum(1 for row in ledger_rows if row["public_documentation_status"].startswith("complete_"))
    metadata_ready = sum(1 for row in ledger_rows if row["official_metadata_evidence_status"] in {"complete_official_metadata_evidence_extract", "partial_official_metadata_evidence_extract"})
    rows = [
        {"metric": "priority_credentialed_acquisition_dataset_rows", "value": str(len(ledger_rows)), "interpretation": "Priority and backup datasets with credentialed raw-acquisition instructions."},
        {"metric": "priority_credentialed_acquisition_priority_batch_rows", "value": str(role_counts.get("priority_10_wave_batch", 0)), "interpretation": "Immediate priority waves in the credentialed acquisition ledger."},
        {"metric": "priority_credentialed_acquisition_backup_rows", "value": str(role_counts.get("sixth_country_backup_candidate", 0)), "interpretation": "Backup sixth-country waves in the credentialed acquisition ledger."},
        {"metric": "priority_credentialed_acquisition_full_file_rows", "value": str(len(full_manifest_rows)), "interpretation": "Official metadata file rows carried into the download review manifest."},
        {"metric": "priority_credentialed_acquisition_core_file_rows", "value": str(len(core_checklist_rows)), "interpretation": "Priority core file/module rows to confirm after official download."},
        {"metric": "priority_credentialed_acquisition_public_documentation_ready_rows", "value": str(public_ready), "interpretation": "Datasets with complete public documentation receipt before raw acquisition."},
        {"metric": "priority_credentialed_acquisition_official_metadata_ready_rows", "value": str(metadata_ready), "interpretation": "Datasets with official DDI/XML metadata evidence before raw acquisition."},
        {"metric": "priority_credentialed_acquisition_original_package_receipt_rows", "value": str(sum(1 for row in ledger_rows if safe_int(row["receipt_original_file_count"]) > 0)), "interpretation": "Datasets with any original raw/package files already received."},
        {"metric": "priority_credentialed_acquisition_targets_missing_before_download", "value": str(sum(safe_int(row["receipt_priority_targets_missing"]) for row in ledger_rows)), "interpretation": "Priority target files still missing before credentialed download."},
        {"metric": "priority_credentialed_acquisition_handoff_readmes_written", "value": str(sum(1 for row in ledger_rows if row.get("handoff_readme"))), "interpretation": "Per-wave credentialed raw acquisition handoff README files written."},
        {"metric": "modeling_gate_status", "value": "blocked", "interpretation": "Credentialed acquisition instructions do not satisfy raw value verification or climate-linkage promotion gates."},
    ]
    for status, count in sorted(status_counts.items()):
        rows.append({"metric": f"priority_credentialed_acquisition_status_{status}", "value": str(count), "interpretation": "Credentialed acquisition status count."})
    return rows


def write_report(
    ledger_rows: list[dict[str, str]],
    full_manifest_rows: list[dict[str, str]],
    core_checklist_rows: list[dict[str, str]],
    summary: list[dict[str, str]],
) -> None:
    summary_table = "\n".join(f"| {row['metric']} | {row['value']} | {row['interpretation']} |" for row in summary)
    REPORT_PATH.write_text(
        f"""# Priority Credentialed Raw Acquisition Ledger

Status: credentialed-download execution layer for the priority dataset-promotion
batch. This does not bypass World Bank login, registration, terms, or Data
Access Agreement gates. It turns the official metadata and download dossier
into a per-wave raw-package acquisition checklist.

## Summary

| Metric | Value | Interpretation |
|---|---:|---|
{summary_table}

## Dataset Ledger

{markdown_table(ledger_rows, ['acquisition_batch_rank', 'idno', 'official_full_file_rows', 'priority_core_file_rows', 'public_documentation_status', 'official_metadata_evidence_status', 'raw_receipt_status', 'credentialed_acquisition_status', 'local_target_folder'], 20)}

## Priority Core File Checklist Preview

{markdown_table(core_checklist_rows, ['acquisition_batch_rank', 'idno', 'core_file_rank', 'metadata_file_name', 'candidate_categories', 'candidate_harmonized_variables', 'current_receipt_status'], 30)}

## Guardrail

Download the complete unchanged official package when the official interface
permits it. The 12-file core checklist is for post-download verification, not a
license to assemble an incomplete analysis package from selected modules.

Do not write any country-wave into `data/` until original raw/package receipt,
priority module coverage, raw value checks, merge-key checks, outcome checks,
and accepted CHIRPS/ERA5 climate linkage all pass.

## Machine-Readable Outputs

- `temp/priority_credentialed_raw_acquisition_ledger.csv`
- `temp/priority_credentialed_raw_full_file_manifest.csv`
- `temp/priority_credentialed_raw_core_file_checklist.csv`
- `result/priority_credentialed_raw_acquisition_summary.csv`
""",
        encoding="utf-8",
    )


def main() -> None:
    ensure_dirs()
    ledger_rows, full_manifest_rows, core_checklist_rows, summary = build_outputs()
    write_csv(LEDGER_PATH, ledger_rows, LEDGER_COLUMNS)
    write_csv(FULL_MANIFEST_PATH, full_manifest_rows, FULL_MANIFEST_COLUMNS)
    write_csv(CORE_CHECKLIST_PATH, core_checklist_rows, CORE_CHECKLIST_COLUMNS)
    write_csv(SUMMARY_PATH, summary, SUMMARY_COLUMNS)
    write_report(ledger_rows, full_manifest_rows, core_checklist_rows, summary)
    append_log(
        TEMP_DIR / "audit_log.md",
        f"Built priority credentialed raw acquisition ledger datasets={len(ledger_rows)} full_files={len(full_manifest_rows)} core_files={len(core_checklist_rows)}.",
    )
    print(f"Priority credentialed raw acquisition ledger datasets={len(ledger_rows)} full_files={len(full_manifest_rows)} core_files={len(core_checklist_rows)}.")


if __name__ == "__main__":
    main()
