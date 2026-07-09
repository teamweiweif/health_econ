from __future__ import annotations

import csv
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from common import PROJECT_ROOT, REPORT_DIR, RESULT_DIR, TEMP_DIR, append_log, ensure_dirs, write_csv


WAVE_PLAN_PATH = RESULT_DIR / "priority_promotion_acquisition_wave_plan.csv"
ACCESS_PROBE_PATH = TEMP_DIR / "priority_official_raw_access_probe.csv"
SCHEMA_FILE_PATH = TEMP_DIR / "raw_schema_inventory" / "schema_file_inventory.csv"
PRIORITY_FILE_QUEUE_PATH = RESULT_DIR / "priority_promotion_acquisition_file_queue.csv"
RECEIPT_LEDGER_PATH = TEMP_DIR / "priority_raw_package_receipt_ledger.csv"

DOSSIER_PATH = TEMP_DIR / "priority_official_download_dossier.csv"
FULL_FILE_INVENTORY_PATH = TEMP_DIR / "priority_official_full_file_inventory.csv"
DOCUMENTATION_LINKS_PATH = TEMP_DIR / "priority_official_documentation_links.csv"
SUMMARY_PATH = RESULT_DIR / "priority_official_download_dossier_summary.csv"
REPORT_PATH = REPORT_DIR / "priority_official_download_dossier.md"

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
    "python script/127_enforce_promoted_data_gate.py",
    "python script/36_build_direct_read_audit_bundle.py",
    "python script/14_validate_workspace.py",
]

DOSSIER_COLUMNS = [
    "acquisition_batch_rank",
    "batch_role",
    "country",
    "wave",
    "idno",
    "survey_name",
    "catalog_id",
    "official_get_microdata_url",
    "login_url",
    "register_url",
    "terms_or_request_urls",
    "pdf_documentation_url",
    "ddi_metadata_url",
    "json_metadata_url",
    "data_dictionary_url",
    "related_materials_url",
    "local_target_folder",
    "metadata_full_file_rows",
    "priority_core_file_rows",
    "receipt_original_file_rows",
    "receipt_archive_files",
    "receipt_raw_tabular_files",
    "receipt_priority_targets_missing",
    "complete_package_dossier_status",
    "download_action",
    "post_download_commands",
    "handoff_readme",
]

FULL_FILE_COLUMNS = [
    "acquisition_batch_rank",
    "batch_role",
    "country",
    "wave",
    "idno",
    "catalog_id",
    "fid",
    "metadata_file_name",
    "metadata_file_description",
    "cases",
    "variable_count",
    "unit_guess",
    "module_guess",
    "source_url",
    "priority_core_target",
    "current_receipt_status",
    "download_review_action",
]

LINK_COLUMNS = [
    "acquisition_batch_rank",
    "batch_role",
    "country",
    "wave",
    "idno",
    "link_type",
    "url",
    "access_status",
    "use_in_download_workflow",
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
        text = str(value).strip()
        return int(float(text)) if text else default
    except (TypeError, ValueError):
        return default


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(PROJECT_ROOT)).replace("\\", "/")
    except ValueError:
        return str(path).replace("\\", "/")


def compact(values: list[str], limit: int = 8) -> str:
    out: list[str] = []
    seen: set[str] = set()
    for value in values:
        item = " ".join(clean(value).split())
        if item and item not in seen:
            out.append(item)
            seen.add(item)
        if len(out) >= limit:
            break
    return "; ".join(out)


def first_by(rows: list[dict[str, str]], field: str) -> dict[str, dict[str, str]]:
    out: dict[str, dict[str, str]] = {}
    for row in rows:
        key = clean(row.get(field))
        if key and key not in out:
            out[key] = row
    return out


def group(rows: list[dict[str, str]], field: str) -> dict[str, list[dict[str, str]]]:
    out: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        key = clean(row.get(field))
        if key:
            out[key].append(row)
    return out


def target_folder_path(folder: str, idno: str) -> Path:
    folder_clean = clean(folder).replace("\\", "/").strip("/")
    if folder_clean.startswith("temp/raw_downloads/"):
        return PROJECT_ROOT / folder_clean
    if folder_clean:
        return RAW_ROOT / folder_clean
    return RAW_ROOT / idno


def split_links(value: str) -> list[str]:
    links = []
    for item in clean(value).split(";"):
        url = item.strip()
        if url and url not in links:
            links.append(url)
    return links


def link_type(url: str) -> str:
    low = url.lower()
    if "pdf-documentation" in low or low.endswith(".pdf"):
        return "pdf_documentation"
    if "/metadata/export/" in low and "/ddi" in low:
        return "ddi_metadata"
    if "/metadata/export/" in low and "/json" in low:
        return "json_metadata"
    if "data-dictionary" in low:
        return "data_dictionary"
    if "related-materials" in low:
        return "related_materials"
    if "study-description" in low:
        return "study_description"
    if "terms" in low or "request" in low:
        return "terms_or_request"
    if "login" in low:
        return "login"
    if "register" in low:
        return "register"
    return "other_official_link"


def pick_link(links: list[str], target_type: str) -> str:
    return next((url for url in links if link_type(url) == target_type), "")


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


def status_for_receipt(receipt: dict[str, str]) -> str:
    if not receipt:
        return "receipt_ledger_missing"
    if safe_int(receipt.get("receipt_original_file_rows")) > 0:
        return "original_files_present_review_against_full_metadata_inventory"
    return "not_received_no_original_raw_package"


def dossier_status(receipt: dict[str, str], full_rows: int, priority_rows: int) -> str:
    if not receipt:
        return "blocked_receipt_ledger_missing"
    if safe_int(receipt.get("receipt_original_file_rows")) == 0:
        return "blocked_official_access_required_no_original_package"
    if safe_int(receipt.get("receipt_priority_targets_missing")) > 0:
        return "partial_receipt_missing_priority_targets"
    if full_rows == 0:
        return "receipt_present_metadata_inventory_missing"
    if priority_rows == 0:
        return "receipt_present_priority_target_mapping_missing"
    return "receipt_candidate_ready_for_schema_and_manual_audit"


def write_handoff(row: dict[str, str], full_files: list[dict[str, str]], links: list[dict[str, str]]) -> str:
    folder = target_folder_path(row.get("local_target_folder", ""), row.get("idno", ""))
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / "_PRIORITY_OFFICIAL_DOWNLOAD_DOSSIER.md"
    file_examples = [clean(item.get("metadata_file_name")) for item in full_files if clean(item.get("metadata_file_name"))]
    link_lines = [f"- {item['link_type']}: {item['url']}" for item in links if item.get("link_type") != "other_official_link"]
    path.write_text(
        f"""# Priority Official Download Dossier

Dataset: {row.get('idno', '')} - {row.get('country', '')} {row.get('wave', '')}

Status: {row.get('complete_package_dossier_status', '')}

Official get-microdata URL: {row.get('official_get_microdata_url', '')}

Target folder: {row.get('local_target_folder', '')}

Current receipt:

- Original files received: {row.get('receipt_original_file_rows', '0')}
- Archive files: {row.get('receipt_archive_files', '0')}
- Raw tabular files: {row.get('receipt_raw_tabular_files', '0')}
- Priority targets missing: {row.get('receipt_priority_targets_missing', '0')}

Official links:

{chr(10).join(link_lines[:12]) if link_lines else '- No metadata/documentation links captured.'}

Metadata file inventory examples:

{chr(10).join(f'- {name}' for name in file_examples[:30]) if file_examples else '- No metadata file inventory rows available.'}

Download action: {row.get('download_action', '')}

Post-download commands:

{chr(10).join(f'- `{command}`' for command in POST_DOWNLOAD_COMMANDS)}

Stop rule: do not write this wave into `data/` until the original package,
manual raw value/unit/key verification, and CHIRPS/ERA5 linkage gates pass.
""",
        encoding="utf-8",
    )
    return rel(path)


def build_outputs() -> tuple[list[dict[str, str]], list[dict[str, str]], list[dict[str, str]], list[dict[str, str]]]:
    waves = read_csv_dicts(WAVE_PLAN_PATH)
    access_by_id = first_by(read_csv_dicts(ACCESS_PROBE_PATH), "idno")
    receipt_by_id = first_by(read_csv_dicts(RECEIPT_LEDGER_PATH), "idno")
    schema_by_id = group(read_csv_dicts(SCHEMA_FILE_PATH), "idno")
    priority_by_id = group(read_csv_dicts(PRIORITY_FILE_QUEUE_PATH), "idno")

    dossier_rows: list[dict[str, str]] = []
    file_rows: list[dict[str, str]] = []
    link_rows: list[dict[str, str]] = []

    for wave in waves:
        idno = clean(wave.get("idno"))
        access = access_by_id.get(idno, {})
        receipt = receipt_by_id.get(idno, {})
        metadata_links = split_links(access.get("candidate_metadata_links", ""))
        terms_links = split_links(access.get("request_or_terms_links", ""))
        all_links = []
        for url in [access.get("login_link", ""), access.get("register_link", ""), *terms_links, *metadata_links]:
            url_clean = clean(url)
            if url_clean and url_clean not in all_links:
                all_links.append(url_clean)

        links_for_wave: list[dict[str, str]] = []
        for url in all_links:
            row = {
                "acquisition_batch_rank": wave.get("acquisition_batch_rank", ""),
                "batch_role": wave.get("batch_role", ""),
                "country": wave.get("country", ""),
                "wave": wave.get("wave", ""),
                "idno": idno,
                "link_type": link_type(url),
                "url": url,
                "access_status": "official_public_metadata_or_access_workflow_link",
                "use_in_download_workflow": "Use as official reference; do not bypass login, terms, registration, or data-access agreement gates.",
            }
            links_for_wave.append(row)
            link_rows.append(row)

        priority_names = {normalize_name(row.get("file_name", "")) for row in priority_by_id.get(idno, [])}
        receipt_status = status_for_receipt(receipt)
        for item in schema_by_id.get(idno, []):
            is_priority = normalize_name(item.get("file_name", "")) in priority_names
            file_rows.append(
                {
                    "acquisition_batch_rank": wave.get("acquisition_batch_rank", ""),
                    "batch_role": wave.get("batch_role", ""),
                    "country": wave.get("country", ""),
                    "wave": wave.get("wave", ""),
                    "idno": idno,
                    "catalog_id": item.get("catalog_id", wave.get("catalog_id", "")),
                    "fid": item.get("fid", ""),
                    "metadata_file_name": item.get("file_name", ""),
                    "metadata_file_description": item.get("file_description", ""),
                    "cases": item.get("cases", ""),
                    "variable_count": item.get("variable_count", ""),
                    "unit_guess": item.get("unit_guess", ""),
                    "module_guess": item.get("module_guess", ""),
                    "source_url": item.get("source_url", ""),
                    "priority_core_target": "1" if is_priority else "0",
                    "current_receipt_status": receipt_status,
                    "download_review_action": "After credentialed download, verify this metadata file has a corresponding raw file or documented reason for absence.",
                }
            )

        status = dossier_status(receipt, len(schema_by_id.get(idno, [])), len(priority_by_id.get(idno, [])))
        row = {
            "acquisition_batch_rank": wave.get("acquisition_batch_rank", ""),
            "batch_role": wave.get("batch_role", ""),
            "country": wave.get("country", ""),
            "wave": wave.get("wave", ""),
            "idno": idno,
            "survey_name": wave.get("survey_name", ""),
            "catalog_id": access.get("catalog_id", ""),
            "official_get_microdata_url": wave.get("official_url", access.get("official_url", "")),
            "login_url": access.get("login_link", ""),
            "register_url": access.get("register_link", ""),
            "terms_or_request_urls": compact(terms_links, limit=6),
            "pdf_documentation_url": pick_link(metadata_links, "pdf_documentation"),
            "ddi_metadata_url": pick_link(metadata_links, "ddi_metadata"),
            "json_metadata_url": pick_link(metadata_links, "json_metadata"),
            "data_dictionary_url": pick_link(metadata_links, "data_dictionary"),
            "related_materials_url": pick_link(metadata_links, "related_materials"),
            "local_target_folder": wave.get("local_target_folder", ""),
            "metadata_full_file_rows": str(len(schema_by_id.get(idno, []))),
            "priority_core_file_rows": str(len(priority_by_id.get(idno, []))),
            "receipt_original_file_rows": receipt.get("original_file_count", "0"),
            "receipt_archive_files": receipt.get("archive_file_count", "0"),
            "receipt_raw_tabular_files": receipt.get("raw_tabular_file_count", "0"),
            "receipt_priority_targets_missing": receipt.get("priority_targets_missing", ""),
            "complete_package_dossier_status": status,
            "download_action": "Use official account/login/terms workflow, download the complete unchanged raw package and all documentation, then place it in the target folder.",
            "post_download_commands": "; ".join(POST_DOWNLOAD_COMMANDS),
            "handoff_readme": "",
        }
        row["handoff_readme"] = write_handoff(row, schema_by_id.get(idno, []), links_for_wave)
        dossier_rows.append(row)

    return dossier_rows, file_rows, link_rows, build_summary(dossier_rows, file_rows, link_rows)


def build_summary(
    dossier_rows: list[dict[str, str]],
    file_rows: list[dict[str, str]],
    link_rows: list[dict[str, str]],
) -> list[dict[str, str]]:
    status_counts = Counter(row.get("complete_package_dossier_status", "") for row in dossier_rows)
    link_counts = Counter(row.get("link_type", "") for row in link_rows)
    rows = [
        {"metric": "priority_official_download_dossier_rows", "value": str(len(dossier_rows)), "interpretation": "Priority and backup waves with official download dossiers."},
        {"metric": "priority_official_full_file_inventory_rows", "value": str(len(file_rows)), "interpretation": "Full official metadata file rows for priority and backup waves."},
        {"metric": "priority_official_priority_core_file_rows", "value": str(sum(safe_int(row.get("priority_core_target")) for row in file_rows)), "interpretation": "Rows from the full metadata inventory that also appear in the core priority file queue."},
        {"metric": "priority_official_documentation_link_rows", "value": str(len(link_rows)), "interpretation": "Official metadata/documentation/access workflow links captured for the dossiers."},
        {"metric": "priority_official_pdf_documentation_links", "value": str(link_counts.get("pdf_documentation", 0)), "interpretation": "PDF documentation links captured."},
        {"metric": "priority_official_ddi_metadata_links", "value": str(link_counts.get("ddi_metadata", 0)), "interpretation": "DDI metadata export links captured."},
        {"metric": "priority_official_json_metadata_links", "value": str(link_counts.get("json_metadata", 0)), "interpretation": "JSON metadata export links captured."},
        {"metric": "priority_official_data_dictionary_links", "value": str(link_counts.get("data_dictionary", 0)), "interpretation": "Data dictionary links captured."},
        {"metric": "priority_official_no_original_package_rows", "value": str(status_counts.get("blocked_official_access_required_no_original_package", 0)), "interpretation": "Dossiers still blocked because no original raw package is present."},
        {"metric": "priority_official_receipt_candidates", "value": str(status_counts.get("receipt_candidate_ready_for_schema_and_manual_audit", 0)), "interpretation": "Dossiers with receipt candidates ready for downstream audits."},
        {"metric": "modeling_gate_status", "value": "blocked", "interpretation": "Models remain blocked until promoted registry thresholds and accepted CHIRPS/ERA5 linkage pass."},
    ]
    for status, count in sorted(status_counts.items()):
        rows.append({"metric": f"priority_official_dossier_status_{status}", "value": str(count), "interpretation": "Download dossier status count."})
    return rows


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


def write_report(dossier_rows: list[dict[str, str]], summary: list[dict[str, str]]) -> None:
    summary_table = "\n".join(f"| {row['metric']} | {row['value']} | {row['interpretation']} |" for row in summary)
    REPORT_PATH.write_text(
        f"""# Priority Official Download Dossier

Status: official-source download and documentation dossier. This does not
download restricted microdata and does not bypass login, registration, terms,
or data-access agreement gates.

## Summary

| Metric | Value | Interpretation |
|---|---:|---|
{summary_table}

## Dataset Dossiers

{markdown_table(dossier_rows, ['acquisition_batch_rank', 'idno', 'country', 'wave', 'metadata_full_file_rows', 'priority_core_file_rows', 'receipt_original_file_rows', 'receipt_priority_targets_missing', 'complete_package_dossier_status'], 20)}

## Rule

Use these dossiers to obtain complete unchanged official raw packages and
documentation through the permitted access workflow. After files are placed
under `temp/raw_downloads/<IDNO>/`, rerun the receipt, archive, schema, manual
verification, climate-linkage, promoted-data, bundle, and validation gates.

## Machine-Readable Outputs

- `temp/priority_official_download_dossier.csv`
- `temp/priority_official_full_file_inventory.csv`
- `temp/priority_official_documentation_links.csv`
- `result/priority_official_download_dossier_summary.csv`
""",
        encoding="utf-8",
    )


def main() -> None:
    ensure_dirs()
    dossier_rows, file_rows, link_rows, summary = build_outputs()
    write_csv(DOSSIER_PATH, dossier_rows, DOSSIER_COLUMNS)
    write_csv(FULL_FILE_INVENTORY_PATH, file_rows, FULL_FILE_COLUMNS)
    write_csv(DOCUMENTATION_LINKS_PATH, link_rows, LINK_COLUMNS)
    write_csv(SUMMARY_PATH, summary, SUMMARY_COLUMNS)
    write_report(dossier_rows, summary)
    append_log(
        TEMP_DIR / "audit_log.md",
        f"Built priority official download dossier datasets={len(dossier_rows)} full_file_rows={len(file_rows)} links={len(link_rows)}.",
    )
    print(
        f"Priority official download dossier datasets={len(dossier_rows)} "
        f"full_file_rows={len(file_rows)} links={len(link_rows)}."
    )


if __name__ == "__main__":
    main()
