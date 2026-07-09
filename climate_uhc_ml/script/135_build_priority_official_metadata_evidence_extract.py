from __future__ import annotations

import csv
import re
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from common import PROJECT_ROOT, REPORT_DIR, RESULT_DIR, TEMP_DIR, append_log, ensure_dirs, write_csv


VARIABLE_TEMPLATE_PATH = TEMP_DIR / "priority_variable_verification_template.csv"
PUBLIC_DOC_RECEIPT_PATH = TEMP_DIR / "priority_public_documentation_receipt.csv"

VARIABLE_EVIDENCE_PATH = TEMP_DIR / "priority_official_metadata_variable_evidence.csv"
CATEGORY_EVIDENCE_PATH = TEMP_DIR / "priority_official_metadata_category_evidence.csv"
DATASET_EVIDENCE_PATH = TEMP_DIR / "priority_official_metadata_dataset_evidence.csv"
SUMMARY_PATH = RESULT_DIR / "priority_official_metadata_evidence_summary.csv"
REPORT_PATH = REPORT_DIR / "priority_official_metadata_evidence_extract.md"

RAW_ROOT = TEMP_DIR / "raw_downloads"
CATEGORY_LIMIT_PER_CANDIDATE = 10

VARIABLE_COLUMNS = [
    "candidate_row_id",
    "acquisition_batch_rank",
    "batch_role",
    "country",
    "wave",
    "idno",
    "concept",
    "required_for",
    "candidate_files",
    "candidate_raw_variable",
    "candidate_harmonized_variables",
    "template_raw_label",
    "metadata_confidence",
    "ddi_match_status",
    "ddi_match_count",
    "ddi_file_ids",
    "ddi_file_names",
    "ddi_file_descriptions",
    "ddi_variable_names",
    "ddi_variable_labels",
    "ddi_interval",
    "ddi_format_types",
    "ddi_valid_counts",
    "ddi_invalid_counts",
    "ddi_min_values",
    "ddi_max_values",
    "ddi_range_units",
    "ddi_category_count",
    "ddi_category_preview",
    "official_metadata_evidence_status",
    "raw_value_verification_status",
    "promotion_guardrail",
]

CATEGORY_COLUMNS = [
    "candidate_row_id",
    "idno",
    "concept",
    "candidate_raw_variable",
    "candidate_files",
    "ddi_variable_name",
    "ddi_file_name",
    "category_index",
    "category_value",
    "category_label",
    "category_frequency",
    "category_missing_flag",
    "category_truncation_status",
]

DATASET_COLUMNS = [
    "acquisition_batch_rank",
    "batch_role",
    "country",
    "wave",
    "idno",
    "candidate_variable_rows",
    "ddi_variable_match_rows",
    "ddi_file_match_rows",
    "ddi_name_only_match_rows",
    "ddi_no_match_rows",
    "variables_with_categories",
    "category_rows_extracted",
    "variables_with_valid_counts",
    "variables_with_invalid_counts",
    "variables_with_range_units",
    "ddi_resource_path",
    "ddi_resource_sha256",
    "official_metadata_evidence_status",
    "raw_value_verification_status",
    "handoff_readme",
]

SUMMARY_COLUMNS = ["metric", "value", "interpretation"]


def read_csv_dicts(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def clean(value: Any) -> str:
    return "" if value is None else str(value).strip()


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(PROJECT_ROOT)).replace("\\", "/")
    except ValueError:
        return str(path).replace("\\", "/")


def split_values(value: str) -> list[str]:
    out: list[str] = []
    seen: set[str] = set()
    for item in re.split(r"[;,]", clean(value)):
        item = item.strip()
        if item and item not in seen:
            out.append(item)
            seen.add(item)
    return out


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


def local_name(tag: str) -> str:
    return tag.split("}")[-1]


def child_text(element: ET.Element, tag_name: str) -> str:
    for child in list(element):
        if local_name(child.tag) == tag_name:
            return " ".join((child.text or "").split())
    return ""


def compact(values: list[str], limit: int = 8, sep: str = ";") -> str:
    out: list[str] = []
    seen: set[str] = set()
    for value in values:
        item = " ".join(clean(value).split())
        if item and item not in seen:
            out.append(item)
            seen.add(item)
        if len(out) >= limit:
            break
    return sep.join(out)


def shorten(value: Any, limit: int = 180) -> str:
    text = " ".join(clean(value).split())
    if len(text) <= limit:
        return text
    return text[: limit - 3] + "..."


def receipt_by_idno() -> dict[str, dict[str, str]]:
    out: dict[str, dict[str, str]] = {}
    for row in read_csv_dicts(PUBLIC_DOC_RECEIPT_PATH):
        if row.get("resource_type") != "ddi_metadata":
            continue
        idno = row.get("idno", "")
        saved = row.get("saved_path", "")
        if idno and saved:
            out[idno] = row
    return out


def parse_ddi(path: Path) -> tuple[dict[str, dict[str, str]], list[dict[str, Any]]]:
    root = ET.parse(path).getroot()
    files: dict[str, dict[str, str]] = {}
    variables: list[dict[str, Any]] = []

    for element in root.iter():
        if local_name(element.tag) != "fileDscr":
            continue
        fid = element.attrib.get("ID", "")
        file_name = ""
        file_content = ""
        cases = ""
        variables_count = ""
        for child in element.iter():
            name = local_name(child.tag)
            text = " ".join((child.text or "").split())
            if name == "fileName":
                file_name = text
            elif name == "fileCont":
                file_content = text
            elif name == "caseQnty":
                cases = text
            elif name == "varQnty":
                variables_count = text
        if fid:
            files[fid] = {
                "file_id": fid,
                "file_name": file_name,
                "file_description": file_content,
                "cases": cases,
                "variable_count": variables_count,
                "normalized_file_name": normalize_name(file_name),
            }

    for element in root.iter():
        if local_name(element.tag) != "var":
            continue
        file_ids = split_values(element.attrib.get("files", "").replace(" ", ";"))
        sum_stats: dict[str, str] = {}
        categories: list[dict[str, str]] = []
        range_units = ""
        range_min = ""
        range_max = ""
        format_type = ""
        for child in list(element):
            name = local_name(child.tag)
            if name == "sumStat":
                stat_type = child.attrib.get("type", "")
                if stat_type:
                    sum_stats[stat_type] = " ".join((child.text or "").split())
            elif name == "valrng":
                for grand in list(child):
                    if local_name(grand.tag) == "range":
                        range_units = grand.attrib.get("UNITS", "")
                        range_min = grand.attrib.get("min", "")
                        range_max = grand.attrib.get("max", "")
            elif name == "catgry":
                cat = {
                    "value": "",
                    "label": "",
                    "frequency": "",
                    "missing_flag": child.attrib.get("missing", ""),
                }
                for grand in list(child):
                    grand_name = local_name(grand.tag)
                    text = " ".join((grand.text or "").split())
                    if grand_name == "catValu":
                        cat["value"] = text
                    elif grand_name == "labl":
                        cat["label"] = text
                    elif grand_name == "catStat" and grand.attrib.get("type") == "freq":
                        cat["frequency"] = text
                categories.append(cat)
            elif name == "varFormat":
                format_type = child.attrib.get("type", "")
        file_names = [files.get(fid, {}).get("file_name", "") for fid in file_ids]
        file_descriptions = [files.get(fid, {}).get("file_description", "") for fid in file_ids]
        variables.append(
            {
                "name": element.attrib.get("name", ""),
                "normalized_name": normalize_name(element.attrib.get("name", "")),
                "file_ids": file_ids,
                "file_names": file_names,
                "normalized_file_names": [normalize_name(name) for name in file_names],
                "file_descriptions": file_descriptions,
                "label": child_text(element, "labl"),
                "interval": element.attrib.get("intrvl", ""),
                "format_type": format_type,
                "valid_count": sum_stats.get("vald", ""),
                "invalid_count": sum_stats.get("invd", ""),
                "min_value": sum_stats.get("min") or range_min,
                "max_value": sum_stats.get("max") or range_max,
                "range_units": range_units,
                "categories": categories,
            }
        )
    return files, variables


def match_variables(candidate: dict[str, str], variables: list[dict[str, Any]]) -> tuple[str, list[dict[str, Any]]]:
    candidate_vars = [normalize_name(value) for value in split_values(candidate.get("candidate_raw_variable", ""))]
    candidate_files = [normalize_name(value) for value in split_values(candidate.get("candidate_files", ""))]
    name_matches = [var for var in variables if var["normalized_name"] in candidate_vars]
    if not name_matches:
        return "no_ddi_variable_match", []
    if not candidate_files:
        return "ddi_variable_name_match_no_candidate_file", name_matches
    def same_file(candidate_file: str, ddi_file: str) -> bool:
        return bool(
            candidate_file
            and ddi_file
            and (
                candidate_file == ddi_file
                or candidate_file in ddi_file
                or ddi_file in candidate_file
            )
        )

    file_matches = [
        var
        for var in name_matches
        if any(same_file(candidate_file, ddi_file) for candidate_file in candidate_files for ddi_file in var["normalized_file_names"])
    ]
    if file_matches:
        return "ddi_variable_and_file_match", file_matches
    return "ddi_variable_name_match_file_unmatched", name_matches


def category_preview(categories: list[dict[str, str]]) -> str:
    parts = []
    for cat in categories[:5]:
        label = cat.get("label", "")
        value = cat.get("value", "")
        freq = cat.get("frequency", "")
        item = f"{shorten(value, 30)}={shorten(label, 60)}"
        if freq:
            item += f" (n={freq})"
        parts.append(item)
    if len(categories) > 5:
        parts.append(f"... +{len(categories) - 5} more")
    return shorten("; ".join(parts), 500)


def build_outputs() -> tuple[list[dict[str, str]], list[dict[str, str]], list[dict[str, str]], list[dict[str, str]]]:
    receipts = receipt_by_idno()
    candidates = read_csv_dicts(VARIABLE_TEMPLATE_PATH)
    variables_by_idno: dict[str, list[dict[str, Any]]] = {}
    parse_status: dict[str, str] = {}

    for idno, receipt in receipts.items():
        path = PROJECT_ROOT / receipt.get("saved_path", "")
        if not path.exists():
            parse_status[idno] = "ddi_resource_missing"
            variables_by_idno[idno] = []
            continue
        try:
            _files, variables = parse_ddi(path)
            variables_by_idno[idno] = variables
            parse_status[idno] = "ddi_parsed"
        except Exception as exc:
            parse_status[idno] = f"ddi_parse_failed:{exc}"
            variables_by_idno[idno] = []

    variable_rows: list[dict[str, str]] = []
    category_rows: list[dict[str, str]] = []
    grouped_variable_rows: dict[str, list[dict[str, str]]] = defaultdict(list)

    for idx, candidate in enumerate(candidates, start=1):
        idno = candidate.get("idno", "")
        variables = variables_by_idno.get(idno, [])
        receipt = receipts.get(idno, {})
        match_status, matches = match_variables(candidate, variables)
        all_categories = [cat for match in matches for cat in match.get("categories", [])]
        official_status = (
            "official_ddi_variable_and_file_evidence_present"
            if match_status == "ddi_variable_and_file_match"
            else "official_ddi_variable_evidence_partial"
            if matches
            else "official_ddi_variable_evidence_missing"
        )
        row = {
            "candidate_row_id": str(idx),
            "acquisition_batch_rank": candidate.get("acquisition_batch_rank", ""),
            "batch_role": candidate.get("batch_role", ""),
            "country": candidate.get("country", ""),
            "wave": candidate.get("wave", ""),
            "idno": idno,
            "concept": candidate.get("concept", ""),
            "required_for": candidate.get("required_for", ""),
            "candidate_files": shorten(candidate.get("candidate_files", ""), 240),
            "candidate_raw_variable": shorten(candidate.get("candidate_raw_variable", ""), 120),
            "candidate_harmonized_variables": shorten(candidate.get("candidate_harmonized_variables", ""), 180),
            "template_raw_label": shorten(candidate.get("raw_label", ""), 220),
            "metadata_confidence": candidate.get("metadata_confidence", ""),
            "ddi_match_status": match_status if parse_status.get(idno) == "ddi_parsed" else parse_status.get(idno, "ddi_resource_missing"),
            "ddi_match_count": str(len(matches)),
            "ddi_file_ids": compact([fid for match in matches for fid in match.get("file_ids", [])], limit=12),
            "ddi_file_names": compact([name for match in matches for name in match.get("file_names", [])], limit=12),
            "ddi_file_descriptions": shorten(compact([desc for match in matches for desc in match.get("file_descriptions", [])], limit=5), 240),
            "ddi_variable_names": compact([match.get("name", "") for match in matches], limit=12),
            "ddi_variable_labels": shorten(compact([match.get("label", "") for match in matches], limit=5), 300),
            "ddi_interval": compact([match.get("interval", "") for match in matches], limit=4),
            "ddi_format_types": compact([match.get("format_type", "") for match in matches], limit=4),
            "ddi_valid_counts": compact([match.get("valid_count", "") for match in matches], limit=12),
            "ddi_invalid_counts": compact([match.get("invalid_count", "") for match in matches], limit=12),
            "ddi_min_values": compact([match.get("min_value", "") for match in matches], limit=8),
            "ddi_max_values": compact([match.get("max_value", "") for match in matches], limit=8),
            "ddi_range_units": compact([match.get("range_units", "") for match in matches], limit=4),
            "ddi_category_count": str(len(all_categories)),
            "ddi_category_preview": category_preview(all_categories),
            "official_metadata_evidence_status": official_status,
            "raw_value_verification_status": "not_raw_value_verified",
            "promotion_guardrail": "official DDI evidence supports pre-review only; raw values, units, missing codes, skip patterns, and merge keys must still be verified from original microdata before promotion",
        }
        variable_rows.append(row)
        grouped_variable_rows[idno].append(row)

        emitted = 0
        for match in matches:
            file_name = compact(match.get("file_names", []), limit=2)
            for cat_index, cat in enumerate(match.get("categories", []), start=1):
                if emitted >= CATEGORY_LIMIT_PER_CANDIDATE:
                    break
                category_rows.append(
                    {
                        "candidate_row_id": str(idx),
                        "idno": idno,
                        "concept": candidate.get("concept", ""),
                        "candidate_raw_variable": candidate.get("candidate_raw_variable", ""),
                        "candidate_files": candidate.get("candidate_files", ""),
                        "ddi_variable_name": match.get("name", ""),
                        "ddi_file_name": file_name,
                        "category_index": str(cat_index),
                        "category_value": shorten(cat.get("value", ""), 80),
                        "category_label": shorten(cat.get("label", ""), 180),
                        "category_frequency": cat.get("frequency", ""),
                        "category_missing_flag": cat.get("missing_flag", ""),
                        "category_truncation_status": "truncated_after_10_per_candidate" if len(all_categories) > CATEGORY_LIMIT_PER_CANDIDATE else "complete_for_candidate",
                    }
                )
                emitted += 1

    dataset_rows: list[dict[str, str]] = []
    candidate_by_idno: dict[str, list[dict[str, str]]] = defaultdict(list)
    for candidate in candidates:
        candidate_by_idno[candidate.get("idno", "")].append(candidate)
    for idno, rows in sorted(grouped_variable_rows.items(), key=lambda item: (int(item[1][0].get("acquisition_batch_rank") or 9999), item[0])):
        first = rows[0]
        match_rows = [row for row in rows if row["ddi_match_status"] in {"ddi_variable_and_file_match", "ddi_variable_name_match_file_unmatched", "ddi_variable_name_match_no_candidate_file"}]
        file_match_rows = [row for row in rows if row["ddi_match_status"] == "ddi_variable_and_file_match"]
        name_only_rows = [row for row in rows if row["ddi_match_status"].startswith("ddi_variable_name_match")]
        no_match_rows = [row for row in rows if row["ddi_match_status"] == "no_ddi_variable_match"]
        category_candidate_rows = [row for row in rows if int(row["ddi_category_count"] or 0) > 0]
        valid_rows = [row for row in rows if clean(row.get("ddi_valid_counts"))]
        invalid_rows = [row for row in rows if clean(row.get("ddi_invalid_counts"))]
        range_rows = [row for row in rows if clean(row.get("ddi_range_units"))]
        evidence_status = (
            "complete_official_metadata_evidence_extract"
            if len(match_rows) == len(rows) and len(file_match_rows) >= max(1, int(len(rows) * 0.8))
            else "partial_official_metadata_evidence_extract"
            if match_rows
            else "missing_official_metadata_evidence_extract"
        )
        handoff = write_handoff(idno, first, evidence_status, len(rows), len(match_rows), len(file_match_rows), len(no_match_rows))
        dataset_rows.append(
            {
                "acquisition_batch_rank": first.get("acquisition_batch_rank", ""),
                "batch_role": first.get("batch_role", ""),
                "country": first.get("country", ""),
                "wave": first.get("wave", ""),
                "idno": idno,
                "candidate_variable_rows": str(len(rows)),
                "ddi_variable_match_rows": str(len(match_rows)),
                "ddi_file_match_rows": str(len(file_match_rows)),
                "ddi_name_only_match_rows": str(len(name_only_rows)),
                "ddi_no_match_rows": str(len(no_match_rows)),
                "variables_with_categories": str(len(category_candidate_rows)),
                "category_rows_extracted": str(sum(1 for row in category_rows if row["idno"] == idno)),
                "variables_with_valid_counts": str(len(valid_rows)),
                "variables_with_invalid_counts": str(len(invalid_rows)),
                "variables_with_range_units": str(len(range_rows)),
                "ddi_resource_path": rows[0].get("ddi_resource_path", receipts.get(idno, {}).get("saved_path", "")),
                "ddi_resource_sha256": receipts.get(idno, {}).get("sha256", ""),
                "official_metadata_evidence_status": evidence_status,
                "raw_value_verification_status": "not_raw_value_verified",
                "handoff_readme": handoff,
            }
        )

    summary = build_summary(variable_rows, category_rows, dataset_rows)
    return variable_rows, category_rows, dataset_rows, summary


def write_handoff(idno: str, first: dict[str, str], status: str, candidate_rows: int, matched_rows: int, file_match_rows: int, no_match_rows: int) -> str:
    folder = RAW_ROOT / idno
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / "_PRIORITY_OFFICIAL_METADATA_EVIDENCE.md"
    path.write_text(
        f"""# Priority Official Metadata Evidence

Dataset: {idno} - {first.get('country', '')} {first.get('wave', '')}

Status: {status}

Candidate variable rows: {candidate_rows}

DDI variable matches: {matched_rows}

DDI variable+file matches: {file_match_rows}

DDI no-match rows: {no_match_rows}

Guardrail: this is official DDI/XML metadata evidence only. It is useful for
pre-reviewing labels, categories, ranges, and file mappings, but it does not
verify raw values, units, missing codes, skip patterns, recall periods, merge
keys, or sample levels. Do not promote this wave until the original raw
microdata package is received and manually verified.
""",
        encoding="utf-8",
    )
    return rel(path)


def build_summary(variable_rows: list[dict[str, str]], category_rows: list[dict[str, str]], dataset_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    status_counts = Counter(row["official_metadata_evidence_status"] for row in variable_rows)
    match_counts = Counter(row["ddi_match_status"] for row in variable_rows)
    dataset_counts = Counter(row["official_metadata_evidence_status"] for row in dataset_rows)
    rows = [
        {"metric": "priority_official_metadata_dataset_rows", "value": str(len(dataset_rows)), "interpretation": "Priority datasets with official metadata evidence extracts."},
        {"metric": "priority_official_metadata_candidate_variable_rows", "value": str(len(variable_rows)), "interpretation": "Priority candidate variables checked against official DDI/XML metadata."},
        {"metric": "priority_official_metadata_category_rows", "value": str(len(category_rows)), "interpretation": "Official DDI category/value-label rows extracted for candidate variables, capped per candidate."},
        {"metric": "priority_official_metadata_variable_match_rows", "value": str(sum(1 for row in variable_rows if row["ddi_match_status"] != "no_ddi_variable_match")), "interpretation": "Candidate variables with a DDI variable-name match."},
        {"metric": "priority_official_metadata_variable_file_match_rows", "value": str(sum(1 for row in variable_rows if row["ddi_match_status"] == "ddi_variable_and_file_match")), "interpretation": "Candidate variables matching both DDI variable name and file name."},
        {"metric": "priority_official_metadata_no_match_rows", "value": str(match_counts.get("no_ddi_variable_match", 0)), "interpretation": "Candidate variables not found in parsed DDI metadata."},
        {"metric": "priority_official_metadata_variables_with_categories", "value": str(sum(1 for row in variable_rows if int(row["ddi_category_count"] or 0) > 0)), "interpretation": "Candidate variables with official category/value-label metadata."},
        {"metric": "priority_official_metadata_variables_with_valid_counts", "value": str(sum(1 for row in variable_rows if clean(row.get("ddi_valid_counts")))), "interpretation": "Candidate variables with DDI valid-count metadata."},
        {"metric": "priority_official_metadata_variables_with_invalid_counts", "value": str(sum(1 for row in variable_rows if clean(row.get("ddi_invalid_counts")))), "interpretation": "Candidate variables with DDI invalid-count metadata."},
        {"metric": "priority_official_metadata_dataset_complete_rows", "value": str(dataset_counts.get("complete_official_metadata_evidence_extract", 0)), "interpretation": "Datasets with complete official metadata evidence under current thresholds."},
        {"metric": "priority_official_metadata_handoff_readmes_written", "value": str(sum(1 for row in dataset_rows if row.get("handoff_readme"))), "interpretation": "Per-wave official metadata evidence handoff README files written."},
        {"metric": "modeling_gate_status", "value": "blocked", "interpretation": "Official metadata evidence does not satisfy raw value verification or climate-linkage promotion gates."},
    ]
    for status, count in sorted(status_counts.items()):
        rows.append({"metric": f"priority_official_metadata_variable_status_{status}", "value": str(count), "interpretation": "Variable-level official metadata evidence status count."})
    for status, count in sorted(match_counts.items()):
        rows.append({"metric": f"priority_official_metadata_match_status_{status}", "value": str(count), "interpretation": "DDI match status count."})
    for status, count in sorted(dataset_counts.items()):
        rows.append({"metric": f"priority_official_metadata_dataset_status_{status}", "value": str(count), "interpretation": "Dataset-level official metadata evidence status count."})
    return rows


def markdown_rows(rows: list[dict[str, str]], columns: list[str], limit: int = 20) -> str:
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


def write_report(variable_rows: list[dict[str, str]], category_rows: list[dict[str, str]], dataset_rows: list[dict[str, str]], summary: list[dict[str, str]]) -> None:
    summary_table = "\n".join(f"| {row['metric']} | {row['value']} | {row['interpretation']} |" for row in summary)
    no_match = [row for row in variable_rows if row["ddi_match_status"] == "no_ddi_variable_match"]
    REPORT_PATH.write_text(
        f"""# Priority Official Metadata Evidence Extract

Status: official DDI/XML metadata evidence extracted for the priority candidate
variables. This layer connects candidate variables to official file names,
variable labels, valid/invalid counts, ranges, and value categories where DDI
metadata expose them. It does not verify raw microdata values.

## Summary

| Metric | Value | Interpretation |
|---|---:|---|
{summary_table}

## Dataset Evidence

{markdown_rows(dataset_rows, ['acquisition_batch_rank', 'idno', 'candidate_variable_rows', 'ddi_variable_match_rows', 'ddi_file_match_rows', 'ddi_no_match_rows', 'official_metadata_evidence_status'], 20)}

## No-Match Candidate Variables

{markdown_rows(no_match, ['candidate_row_id', 'idno', 'concept', 'candidate_files', 'candidate_raw_variable', 'template_raw_label'], 25) if no_match else 'No candidate variables failed DDI variable-name matching.'}

## Guardrail

Official metadata is not raw value verification. Promotion still requires the
complete original raw package and manual checks of values, labels, units,
recall periods, missing codes, skip patterns, merge keys, sample levels, and
accepted CHIRPS/ERA5 linkage.

## Machine-Readable Outputs

- `temp/priority_official_metadata_variable_evidence.csv`
- `temp/priority_official_metadata_category_evidence.csv`
- `temp/priority_official_metadata_dataset_evidence.csv`
- `result/priority_official_metadata_evidence_summary.csv`
""",
        encoding="utf-8",
    )


def main() -> None:
    ensure_dirs()
    variable_rows, category_rows, dataset_rows, summary = build_outputs()
    write_csv(VARIABLE_EVIDENCE_PATH, variable_rows, VARIABLE_COLUMNS)
    write_csv(CATEGORY_EVIDENCE_PATH, category_rows, CATEGORY_COLUMNS)
    write_csv(DATASET_EVIDENCE_PATH, dataset_rows, DATASET_COLUMNS)
    write_csv(SUMMARY_PATH, summary, SUMMARY_COLUMNS)
    write_report(variable_rows, category_rows, dataset_rows, summary)
    append_log(
        TEMP_DIR / "audit_log.md",
        f"Built priority official metadata evidence extract variables={len(variable_rows)} categories={len(category_rows)} datasets={len(dataset_rows)}.",
    )
    print(f"Priority official metadata evidence variables={len(variable_rows)} categories={len(category_rows)} datasets={len(dataset_rows)}.")


if __name__ == "__main__":
    main()
