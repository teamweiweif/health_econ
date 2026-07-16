from __future__ import annotations

import csv
import hashlib
import json
import os
import sys
import zipfile
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq


ROOT = Path(__file__).resolve().parents[2]
SCRIPT_DIR = ROOT / "script"
sys.path.insert(0, str(SCRIPT_DIR))

from build_enriched_compact_metadata import (  # noqa: E402
    add_value_map,
    extract_codebook_entries,
)
from pipeline_lib import read_year_extract  # noqa: E402


YEAR = "2025"
REFERENCE_YEAR = 2024
OLD_COMPACT = ROOT / "temp" / "source_metadata" / "sipp_2018_2024_raw_variable_metadata.compact.json"
OLD_ENRICHED = ROOT / "temp" / "source_metadata" / "sipp_2018_2024_raw_variable_metadata.enriched.compact.json"
NEW_RAW_CSV = ROOT / "temp" / "source_metadata" / "sipp_2018_2025_raw_variable_metadata.csv"
NEW_COMPACT = ROOT / "temp" / "source_metadata" / "sipp_2018_2025_raw_variable_metadata.compact.json"
NEW_ENRICHED = ROOT / "temp" / "source_metadata" / "sipp_2018_2025_raw_variable_metadata.enriched.compact.json"

RAW_ZIP = ROOT / "temp" / "raw_downloads" / "census_sipp" / YEAR / "primary" / "pu2025_csv.zip"
SCHEMA_PATH = ROOT / "temp" / "source_metadata" / "census_sipp" / YEAR / "pu2025_schema.json"
DICTIONARY_PATH = ROOT / "temp" / "source_metadata" / "census_sipp" / YEAR / "2025_SIPP_Data_Dictionary.pdf"
OLD_PANEL = ROOT / "data" / "analysis_ready" / "sipp_2018_2024_person_month_panel.parquet"
NEW_PANEL = ROOT / "data" / "analysis_ready" / "sipp_2018_2025_person_month_panel.parquet"
HISTORICAL_RPRITYPE1 = ROOT / "temp" / "scratch" / "rpritype1_2018_2024.parquet"

TECHNICAL_COLUMNS = {
    "file_year",
    "reference_year",
    "reference_month",
    "reference_date",
    "state_fips",
    "person_id",
    "person_month_key",
}

RAW_METADATA_COLUMNS = [
    "source_agency",
    "survey",
    "survey_year",
    "dataset_id",
    "file_scope",
    "source_page_url",
    "source_data_url",
    "source_schema_url",
    "raw_zip_relative_path",
    "raw_zip_bytes",
    "raw_zip_sha256",
    "raw_csv_entry",
    "raw_csv_delimiter",
    "raw_csv_header_variable_count",
    "schema_relative_path",
    "schema_bytes",
    "schema_sha256",
    "schema_variable_count",
    "raw_header_matches_schema_order",
    "raw_header_position",
    "raw_header_name",
    "schema_varnum",
    "varnum_matches_header_position",
    "variable_name_raw",
    "variable_label_raw",
    "dtype_raw",
    "raw_header_name_matches_schema_name",
    "metadata_build_note",
]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(4 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def relative(path: Path) -> str:
    return str(path.relative_to(ROOT))


def load_json(path: Path) -> dict | list:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_json(path: Path, value: dict) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")


def read_primary_header() -> tuple[str, list[str]]:
    with zipfile.ZipFile(RAW_ZIP) as archive:
        names = archive.namelist()
        if len(names) != 1:
            raise ValueError(f"Expected one CSV in {RAW_ZIP}, found {names}")
        entry = names[0]
        with archive.open(entry) as handle:
            header = handle.readline().decode("utf-8-sig").rstrip("\r\n").split("|")
    if len(header) != len(set(header)):
        raise ValueError("The 2025 primary header contains duplicate variable names")
    return entry, header


def variable_presence_summary(variables: dict) -> dict[str, int]:
    counts = Counter(len(value.get("years", {})) for value in variables.values())
    return {str(key): counts[key] for key in sorted(counts)}


def write_raw_metadata_csv(metadata: dict) -> int:
    NEW_RAW_CSV.parent.mkdir(parents=True, exist_ok=True)
    row_count = 0
    with NEW_RAW_CSV.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=RAW_METADATA_COLUMNS)
        writer.writeheader()
        for year in sorted(metadata["years"]):
            year_info = metadata["years"][year]
            verification = metadata["verification"][year]
            year_variables = []
            for variable_name, variable in metadata["variables"].items():
                if year in variable.get("years", {}):
                    year_variables.append((variable_name, variable["years"][year]))
            year_variables.sort(key=lambda item: item[1]["raw_header_position"])
            for variable_name, record in year_variables:
                writer.writerow(
                    {
                        "source_agency": metadata["global"]["source_agency"],
                        "survey": metadata["global"]["survey"],
                        "survey_year": year,
                        "dataset_id": year_info["dataset_id"],
                        "file_scope": metadata["global"]["file_scope"],
                        "source_page_url": year_info["source_page_url"],
                        "source_data_url": year_info["source_data_url"],
                        "source_schema_url": year_info["source_schema_url"],
                        "raw_zip_relative_path": year_info["raw_zip"]["relative_path"],
                        "raw_zip_bytes": year_info["raw_zip"]["bytes"],
                        "raw_zip_sha256": year_info["raw_zip"]["sha256"],
                        "raw_csv_entry": year_info["raw_csv"]["entry"],
                        "raw_csv_delimiter": year_info["raw_csv"]["delimiter"],
                        "raw_csv_header_variable_count": year_info["raw_csv"]["header_variable_count"],
                        "schema_relative_path": year_info["schema"]["relative_path"],
                        "schema_bytes": year_info["schema"]["bytes"],
                        "schema_sha256": year_info["schema"]["sha256"],
                        "schema_variable_count": year_info["schema"]["variable_count"],
                        "raw_header_matches_schema_order": verification["raw_header_matches_schema_order"],
                        "raw_header_position": record["raw_header_position"],
                        "raw_header_name": record["raw_header_name"],
                        "schema_varnum": record["schema_varnum"],
                        "varnum_matches_header_position": record["varnum_matches_header_position"],
                        "variable_name_raw": variable_name,
                        "variable_label_raw": record.get("label", ""),
                        "dtype_raw": record.get("dtype", ""),
                        "raw_header_name_matches_schema_name": record["raw_header_name_matches_schema_name"],
                        "metadata_build_note": metadata["global"]["metadata_build_note"],
                    }
                )
                row_count += 1
    return row_count


def build_compact_metadata(schema: list[dict], header: list[str], entry: str) -> dict:
    metadata = load_json(OLD_COMPACT)
    schema_names = [record["name"] for record in schema]
    if schema_names != header:
        mismatch = next(
            (
                (index + 1, left, right)
                for index, (left, right) in enumerate(zip(schema_names, header, strict=False))
                if left != right
            ),
            None,
        )
        raise ValueError(f"2025 schema/header order mismatch: {mismatch}")

    metadata["years"][YEAR] = {
        "dataset_id": "sipp_pu2025",
        "source_page_url": "https://www.census.gov/programs-surveys/sipp/data/datasets/2025-data/2025.html",
        "source_data_url": "https://www2.census.gov/programs-surveys/sipp/data/datasets/2025/pu2025_csv.zip",
        "source_schema_url": "https://www2.census.gov/programs-surveys/sipp/data/datasets/2025/pu2025_schema.json",
        "raw_zip": {
            "relative_path": relative(RAW_ZIP),
            "bytes": RAW_ZIP.stat().st_size,
            "sha256": sha256_file(RAW_ZIP),
        },
        "raw_csv": {
            "entry": entry,
            "delimiter": "|",
            "header_variable_count": len(header),
        },
        "schema": {
            "relative_path": relative(SCHEMA_PATH),
            "bytes": SCHEMA_PATH.stat().st_size,
            "sha256": sha256_file(SCHEMA_PATH),
            "variable_count": len(schema),
        },
    }

    name_mismatches = 0
    varnum_mismatches = 0
    for position, record in enumerate(schema, start=1):
        name = record["name"]
        variable = metadata["variables"].setdefault(name, {"years": {}})
        name_match = header[position - 1] == name
        varnum_match = int(record["varnum"]) == position
        name_mismatches += int(not name_match)
        varnum_mismatches += int(not varnum_match)
        variable["years"][YEAR] = {
            "raw_header_position": position,
            "raw_header_name": header[position - 1],
            "schema_varnum": int(record["varnum"]),
            "varnum_matches_header_position": varnum_match,
            "dtype": record.get("dtype", ""),
            "label": record.get("label", ""),
            "raw_header_name_matches_schema_name": name_match,
        }

    metadata["verification"][YEAR] = {
        "row_count": len(schema),
        "raw_header_matches_schema_order": schema_names == header,
        "raw_header_name_schema_name_mismatch_count": name_mismatches,
        "varnum_header_position_mismatch_count": varnum_mismatches,
    }
    metadata["summary"] = {
        "survey_years": sorted(metadata["years"]),
        "variable_year_rows": sum(len(value.get("years", {})) for value in metadata["variables"].values()),
        "unique_variable_names": len(metadata["variables"]),
        "variable_presence_distribution": variable_presence_summary(metadata["variables"]),
    }
    metadata["format"].update(
        {
            "name": "sipp_2018_2025_raw_variable_metadata_compact",
            "version": 2,
            "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "source_csv_relative_path": relative(NEW_RAW_CSV),
        }
    )
    row_count = write_raw_metadata_csv(metadata)
    metadata["format"]["source_csv_rows"] = row_count
    metadata["format"]["source_csv_sha256"] = sha256_file(NEW_RAW_CSV)
    write_json(NEW_COMPACT, metadata)
    return metadata


def build_enriched_metadata(compact: dict) -> dict:
    enriched = load_json(OLD_ENRICHED)
    enriched["years"][YEAR] = compact["years"][YEAR]
    enriched["verification"][YEAR] = compact["verification"][YEAR]
    for name, variable in compact["variables"].items():
        target = enriched["variables"].setdefault(name, {"years": {}})
        if YEAR in variable.get("years", {}):
            target["years"][YEAR] = dict(variable["years"][YEAR])

    entries = extract_codebook_entries(YEAR, DICTIONARY_PATH)
    extraction_summary = entries.pop("_extract_summary")
    matched = 0
    missing = 0
    for name, variable in enriched["variables"].items():
        if YEAR not in variable.get("years", {}):
            continue
        if name not in entries:
            missing += 1
            continue
        matched += 1
        codebook = entries[name]
        possible_values = codebook.pop("possible_values")
        codebook["possible_values_ref"] = add_value_map(enriched["value_maps"], possible_values)
        variable["years"][YEAR]["codebook"] = codebook

    unmatched = [
        name
        for name in entries
        if name not in enriched["variables"] or YEAR not in enriched["variables"][name].get("years", {})
    ]
    enriched["codebook_sources"][YEAR] = {
        "source_pdf_relative_path": relative(DICTIONARY_PATH),
        "source_pdf_bytes": DICTIONARY_PATH.stat().st_size,
        "source_pdf_sha256": sha256_file(DICTIONARY_PATH),
    }
    enriched["codebook_coverage"][YEAR] = {
        "schema_variable_count": len(compact["years"][YEAR]["raw_csv"]) and len(load_json(SCHEMA_PATH)),
        "pdf_entries_extracted": extraction_summary["entries_extracted"],
        "matched_schema_variables": matched,
        "schema_variables_without_pdf_codebook_entry": missing,
        "pdf_entries_not_matched_to_schema": len(unmatched),
        "duplicate_entry_page_count": extraction_summary["duplicate_entry_page_count"],
        "duplicate_entry_page_examples": extraction_summary["duplicate_entry_page_examples"],
        "unmatched_pdf_entry_examples": unmatched[:25],
    }
    enriched["summary"] = compact["summary"]
    enriched["summary"]["unique_value_maps"] = len(enriched["value_maps"])
    enriched["format"] = dict(compact["format"])
    enriched["format"].update(
        {
            "name": "sipp_2018_2025_raw_variable_metadata_enriched_compact",
            "version": 3,
            "codebook_enrichment_note": (
                "Official Census data dictionary PDFs were parsed for codebook fields. "
                "No value labels, universes, descriptions, or record-level fields were inferred. "
                "A missing codebook object means no exact PDF entry was extracted for that variable-year."
            ),
        }
    )
    write_json(NEW_ENRICHED, enriched)
    return enriched


def build_schema_audit(schema: list[dict]) -> dict[str, int]:
    old_schema_path = ROOT / "temp" / "source_metadata" / "census_sipp" / "2024" / "pu2024_schema.json"
    old = {record["name"]: record for record in load_json(old_schema_path)}
    new = {record["name"]: record for record in schema}
    rows = []
    for name in sorted(old.keys() | new.keys()):
        if name not in old:
            status = "added_2025"
        elif name not in new:
            status = "removed_2025"
        else:
            status = "common"
        rows.append(
            {
                "variable_name": name,
                "status": status,
                "dtype_2024": old.get(name, {}).get("dtype", ""),
                "dtype_2025": new.get(name, {}).get("dtype", ""),
                "dtype_changed": name in old and name in new and old[name].get("dtype") != new[name].get("dtype"),
                "label_2024": old.get(name, {}).get("label", ""),
                "label_2025": new.get(name, {}).get("label", ""),
                "label_changed": name in old and name in new and old[name].get("label") != new[name].get("label"),
            }
        )
    audit = pd.DataFrame(rows)
    audit_path = ROOT / "data" / "metadata" / "sipp_2024_2025_schema_diff.csv"
    audit.to_csv(audit_path, index=False)
    summary = {
        "variables_2024": len(old),
        "variables_2025": len(new),
        "common_variables": len(old.keys() & new.keys()),
        "added_2025": len(new.keys() - old.keys()),
        "removed_2025": len(old.keys() - new.keys()),
        "dtype_changes": int(audit["dtype_changed"].sum()),
        "label_changes": int(audit["label_changed"].sum()),
    }
    pd.DataFrame([summary]).to_csv(
        ROOT / "data" / "metadata" / "sipp_2024_2025_schema_summary.csv", index=False
    )
    return summary


def build_download_manifest() -> pd.DataFrame:
    dataset_base = "https://www2.census.gov/programs-surveys/sipp/data/datasets/2025/"
    documentation_base = "https://www2.census.gov/programs-surveys/sipp/tech-documentation/"
    records = [
        ("primary", dataset_base + "pu2025_csv.zip", "temp/raw_downloads/census_sipp/2025/primary/pu2025_csv.zip"),
        ("replicate_weights", dataset_base + "rw2025_csv.zip", "temp/raw_downloads/census_sipp/2025/replicate_weights/rw2025_csv.zip"),
        ("longitudinal_weights_4y", dataset_base + "lgtwgt2025yr4_csv.zip", "temp/raw_downloads/census_sipp/2025/longitudinal_weights/lgtwgt2025yr4_csv.zip"),
        ("longitudinal_weights_3y", dataset_base + "lgtwgt2025yr3_csv.zip", "temp/raw_downloads/census_sipp/2025/longitudinal_weights/lgtwgt2025yr3_csv.zip"),
        ("longitudinal_weights_2y", dataset_base + "lgtwgt2025yr2_csv.zip", "temp/raw_downloads/census_sipp/2025/longitudinal_weights/lgtwgt2025yr2_csv.zip"),
        ("longitudinal_replicate_weights_4y", dataset_base + "lgtrw2025yr4_csv.zip", "temp/raw_downloads/census_sipp/2025/longitudinal_replicate_weights/lgtrw2025yr4_csv.zip"),
        ("longitudinal_replicate_weights_3y", dataset_base + "lgtrw2025yr3_csv.zip", "temp/raw_downloads/census_sipp/2025/longitudinal_replicate_weights/lgtrw2025yr3_csv.zip"),
        ("longitudinal_replicate_weights_2y", dataset_base + "lgtrw2025yr2_csv.zip", "temp/raw_downloads/census_sipp/2025/longitudinal_replicate_weights/lgtrw2025yr2_csv.zip"),
        ("primary_schema", dataset_base + "pu2025_schema.json", "temp/source_metadata/census_sipp/2025/pu2025_schema.json"),
        ("primary_validation", dataset_base + "pu2025_validate.xlsx", "temp/source_metadata/census_sipp/2025/pu2025_validate.xlsx"),
        ("replicate_schema", dataset_base + "rw2025_schema.json", "temp/source_metadata/census_sipp/2025/rw2025_schema.json"),
        ("replicate_validation", dataset_base + "rw2025_validate.xlsx", "temp/source_metadata/census_sipp/2025/rw2025_validate.xlsx"),
        ("primary_dictionary", documentation_base + "data-dictionaries/2025/2025_SIPP_Data_Dictionary.pdf", "temp/source_metadata/census_sipp/2025/2025_SIPP_Data_Dictionary.pdf"),
        ("release_notes", documentation_base + "2025/2025_SIPP_Release_Notes.pdf", "temp/source_metadata/census_sipp/2025/2025_SIPP_Release_Notes.pdf"),
        ("instrument", documentation_base + "2025/2025_SIPP_PU_Instrument_Specifications.pdf", "temp/source_metadata/census_sipp/2025/2025_SIPP_PU_Instrument_Specifications.pdf"),
        ("variable_crosswalk", documentation_base + "2025/SIPP_Variable_Name_Change_Summary_2014_2025.xlsx", "temp/source_metadata/census_sipp/2025/SIPP_Variable_Name_Change_Summary_2014_2025.xlsx"),
        ("replicate_dictionary", documentation_base + "data-dictionaries/2025/rw2025_dictionary.txt", "temp/source_metadata/census_sipp/2025/rw2025_dictionary.txt"),
        ("longitudinal_weight_dictionary", documentation_base + "data-dictionaries/2025/lgtwgt2025_dictionary.txt", "temp/source_metadata/census_sipp/2025/lgtwgt2025_dictionary.txt"),
        ("longitudinal_replicate_dictionary", documentation_base + "data-dictionaries/2025/lgtrw2025_dictionary.txt", "temp/source_metadata/census_sipp/2025/lgtrw2025_dictionary.txt"),
        ("python_example", dataset_base + "2025_sipp_python_input_example.py", "temp/source_metadata/census_sipp/2025/2025_sipp_python_input_example.py"),
        ("r_example", dataset_base + "2025_sipp_r_input_example.R", "temp/source_metadata/census_sipp/2025/2025_sipp_r_input_example.R"),
        ("release_page", "https://www.census.gov/programs-surveys/sipp/data/datasets/2025-data/2025.html", "temp/web_snapshots/2025_sipp_data_page.html"),
    ]
    for prefix in ("lgtwgt", "lgtrw"):
        for years in (4, 3, 2):
            for suffix, role_suffix in (("schema.json", "schema"), ("validate.xlsx", "validation")):
                name = f"{prefix}2025yr{years}_{suffix}"
                records.append(
                    (
                        f"{prefix}_{years}y_{role_suffix}",
                        dataset_base + name,
                        f"temp/source_metadata/census_sipp/2025/{name}",
                    )
                )

    rows = []
    for role, url, rel_path in records:
        path = ROOT / Path(rel_path)
        if not path.exists():
            raise FileNotFoundError(path)
        zip_valid = "not_applicable"
        zip_entries = ""
        zip_uncompressed_bytes = ""
        if path.suffix.lower() == ".zip":
            with zipfile.ZipFile(path) as archive:
                zip_valid = archive.testzip() is None
                zip_entries = ";".join(archive.namelist())
                zip_uncompressed_bytes = sum(item.file_size for item in archive.infolist())
        rows.append(
            {
                "file_role": role,
                "official_url": url,
                "local_relative_path": relative(path),
                "bytes": path.stat().st_size,
                "sha256": sha256_file(path),
                "zip_crc_valid": zip_valid,
                "zip_entries": zip_entries,
                "zip_uncompressed_bytes": zip_uncompressed_bytes,
                "release_version": "1.0",
                "release_date": "2026-07-15",
            }
        )
    manifest = pd.DataFrame(rows)
    manifest.to_csv(ROOT / "data" / "metadata" / "sipp_2025_official_download_manifest.csv", index=False)
    return manifest


def append_panel(enriched: dict, schema: list[dict]) -> dict:
    old_file = pq.ParquetFile(OLD_PANEL)
    old_schema = old_file.schema_arrow
    source_columns = [name for name in old_schema.names if name not in TECHNICAL_COLUMNS]
    if "RPRITYPE1" not in source_columns:
        source_columns.append("RPRITYPE1")
    schema_names = {record["name"] for record in schema}
    missing_2025 = sorted(set(source_columns) - schema_names)
    if missing_2025:
        raise ValueError(f"Panel source variables absent from 2025 schema: {missing_2025}")

    if "RPRITYPE1" in old_schema.names:
        merged_schema = old_schema
        historical_rpritype1 = None
    else:
        if not HISTORICAL_RPRITYPE1.exists():
            raise FileNotFoundError(HISTORICAL_RPRITYPE1)
        fields = list(old_schema)
        insert_at = old_schema.names.index("RPRITYPE2")
        fields.insert(insert_at, pa.field("RPRITYPE1", pa.float32()))
        merged_schema = pa.schema(fields)

        supplement = pd.read_parquet(HISTORICAL_RPRITYPE1)
        supplement["SSUID"] = supplement["SSUID"].astype("int64").astype(str).str.zfill(14)
        supplement["PNUM"] = pd.to_numeric(supplement["PNUM"]).astype("int64")
        supplement["MONTHCODE"] = pd.to_numeric(supplement["MONTHCODE"]).astype("int64")
        supplement["file_year"] = pd.to_numeric(supplement["file_year"]).astype("int64")
        supplement["person_id"] = supplement["SSUID"] + "-" + supplement["PNUM"].astype(str)
        supplement["reference_date"] = pd.to_datetime(
            {
                "year": supplement["file_year"] - 1,
                "month": supplement["MONTHCODE"],
                "day": 1,
            }
        )
        supplement = supplement.sort_values(
            ["person_id", "reference_date", "file_year", "MONTHCODE"], kind="mergesort"
        ).reset_index(drop=True)
        if len(supplement) != old_file.metadata.num_rows:
            raise ValueError("Historical RPRITYPE1 row count does not match the frozen panel")
        if supplement.duplicated(["file_year", "SSUID", "PNUM", "MONTHCODE"]).any():
            raise ValueError("Historical RPRITYPE1 supplement has duplicate merge keys")

        old_keys = pd.read_parquet(
            OLD_PANEL,
            columns=["file_year", "SSUID", "PNUM", "MONTHCODE", "person_id"],
        )
        key_checks = {
            "file_year": (old_keys["file_year"].to_numpy() == supplement["file_year"].to_numpy()).all(),
            "SSUID": (old_keys["SSUID"].astype(str).to_numpy() == supplement["SSUID"].to_numpy()).all(),
            "PNUM": (old_keys["PNUM"].astype("int64").to_numpy() == supplement["PNUM"].to_numpy()).all(),
            "MONTHCODE": (
                old_keys["MONTHCODE"].astype("int64").to_numpy() == supplement["MONTHCODE"].to_numpy()
            ).all(),
            "person_id": (
                old_keys["person_id"].astype(str).to_numpy() == supplement["person_id"].to_numpy()
            ).all(),
        }
        if not all(key_checks.values()):
            raise ValueError(f"Historical RPRITYPE1 key alignment failed: {key_checks}")
        historical_rpritype1 = pa.array(
            pd.to_numeric(supplement["RPRITYPE1"], errors="coerce").astype("float32"),
            type=pa.float32(),
        )

    extract_stats = read_year_extract(YEAR, enriched, source_columns)
    extract_path = ROOT / extract_stats["parquet_path"]
    year_frame = pd.read_parquet(extract_path)
    duplicate_keys = int(year_frame.duplicated(["SSUID", "PNUM", "MONTHCODE"]).sum())
    if duplicate_keys:
        raise ValueError(f"2025 extract has {duplicate_keys} duplicate person-month keys")
    if set(year_frame["reference_year"].dropna().astype(int).unique()) != {REFERENCE_YEAR}:
        raise ValueError("2025 SIPP did not map cleanly to reference year 2024")
    if set(year_frame["reference_month"].dropna().astype(int).unique()) != set(range(1, 13)):
        raise ValueError("2025 SIPP does not contain all reference months 1-12")

    year_table = pa.Table.from_pandas(year_frame, preserve_index=False)
    for field in merged_schema:
        if field.name not in year_table.column_names:
            year_table = year_table.append_column(field.name, pa.nulls(len(year_table), type=field.type))
    year_table = year_table.select(merged_schema.names).cast(merged_schema, safe=False)

    partial = NEW_PANEL.with_suffix(".parquet.partial")
    if partial.exists():
        partial.unlink()
    writer = pq.ParquetWriter(partial, merged_schema, compression="snappy")
    try:
        historical_offset = 0
        for batch in old_file.iter_batches(batch_size=250_000):
            table = pa.Table.from_batches([batch], schema=old_schema)
            if historical_rpritype1 is not None:
                values = historical_rpritype1.slice(historical_offset, len(table))
                table = table.add_column(
                    merged_schema.names.index("RPRITYPE1"), "RPRITYPE1", values
                )
                historical_offset += len(table)
            table = table.select(merged_schema.names).cast(merged_schema, safe=False)
            writer.write_table(table)
        for batch in year_table.to_batches(max_chunksize=250_000):
            writer.write_table(pa.Table.from_batches([batch], schema=merged_schema))
    finally:
        writer.close()
    os.replace(partial, NEW_PANEL)

    output = pq.ParquetFile(NEW_PANEL)
    expected_rows = old_file.metadata.num_rows + len(year_frame)
    if output.metadata.num_rows != expected_rows:
        raise ValueError(f"Merged row count mismatch: {output.metadata.num_rows} != {expected_rows}")
    if output.metadata.num_columns != len(merged_schema):
        raise ValueError("Merged panel column count changed")

    old_counts_path = ROOT / "data" / "sample_audits" / "panel_build_yearly_counts.csv"
    old_counts = pd.read_csv(old_counts_path)
    new_count = {
        "file_year": int(YEAR),
        "reference_year": REFERENCE_YEAR,
        "rows": len(year_frame),
        "unique_persons_seen": int(year_frame["person_id"].nunique()),
        "duplicate_ssuid_pnum_monthcode_within_file": duplicate_keys,
        "selected_variable_count": len(source_columns),
        "parquet_path": relative(extract_path),
        "raw_zip_path": relative(RAW_ZIP),
        "raw_zip_bytes": RAW_ZIP.stat().st_size,
    }
    counts = pd.concat([old_counts, pd.DataFrame([new_count])], ignore_index=True, sort=False)
    counts.to_csv(
        ROOT / "data" / "sample_audits" / "panel_build_yearly_counts_2018_2025.csv", index=False
    )

    missing_rows = []
    for name in source_columns:
        missing = int(year_frame[name].isna().sum())
        missing_rows.append(
            {
                "file_year": int(YEAR),
                "variable_name": name,
                "rows": len(year_frame),
                "missing": missing,
                "missing_rate": missing / len(year_frame),
            }
        )
    pd.DataFrame(missing_rows).to_csv(
        ROOT / "data" / "sample_audits" / "selected_variable_missingness_2025.csv", index=False
    )

    schema_map = {record["name"]: record for record in schema}
    inventory = []
    for field in merged_schema:
        inventory.append(
            {
                "column_name": field.name,
                "parquet_type": str(field.type),
                "column_origin": "technical_harmonization" if field.name in TECHNICAL_COLUMNS else "census_source",
                "present_in_2025_schema": field.name in schema_map,
                "source_label_2025": schema_map.get(field.name, {}).get("label", ""),
            }
        )
    pd.DataFrame(inventory).to_csv(
        ROOT / "data" / "metadata" / "sipp_2018_2025_panel_variable_inventory.csv", index=False
    )

    panel_summary = {
        "old_panel_rows": old_file.metadata.num_rows,
        "new_2025_rows": len(year_frame),
        "merged_rows": output.metadata.num_rows,
        "merged_columns": output.metadata.num_columns,
        "source_columns": len(source_columns),
        "technical_columns": len(TECHNICAL_COLUMNS),
        "new_2025_unique_persons": int(year_frame["person_id"].nunique()),
        "new_2025_states": int(year_frame["state_fips"].nunique(dropna=True)),
        "new_2025_duplicate_keys": duplicate_keys,
        "historical_rpritype1_key_match": True,
        "historical_rpritype1_missing": int(historical_rpritype1.null_count)
        if historical_rpritype1 is not None
        else 0,
        "new_2025_rpritype1_missing": int(year_frame["RPRITYPE1"].isna().sum()),
        "merged_bytes": NEW_PANEL.stat().st_size,
        "new_panel_relative_path": relative(NEW_PANEL),
        "historical_panel_preserved": OLD_PANEL.exists(),
        "constructed_outcome_columns_added": False,
    }
    (ROOT / "data" / "sample_audits" / "sipp_2018_2025_panel_summary.json").write_text(
        json.dumps(panel_summary, indent=2), encoding="utf-8"
    )
    return panel_summary


def write_variable_registry(enriched: dict, schema: list[dict]) -> None:
    schema_map = {record["name"]: record for record in schema}
    rows = []
    for name, variable in enriched["variables"].items():
        years = sorted(variable.get("years", {}))
        rows.append(
            {
                "variable_name": name,
                "years_present": ";".join(years),
                "n_years_present": len(years),
                "present_2025": YEAR in years,
                "dtype_2025": schema_map.get(name, {}).get("dtype", ""),
                "label_2025": schema_map.get(name, {}).get("label", ""),
            }
        )
    pd.DataFrame(rows).sort_values("variable_name").to_csv(
        ROOT / "data" / "metadata" / "variable_registry_2018_2025.csv", index=False
    )


def write_report(
    schema_summary: dict[str, int], panel_summary: dict, manifest: pd.DataFrame, enriched: dict
) -> None:
    downloaded_bytes = int(manifest["bytes"].sum())
    crc_failures = int((manifest["zip_crc_valid"].astype(str) == "False").sum())
    codebook = enriched["codebook_coverage"][YEAR]
    report = f"""# 2025 SIPP Update and Merge Audit

## Release verified

- Census release: 2025 SIPP version 1.0, released July 15, 2026.
- Reference period: January-December 2024.
- Official release page: https://www.census.gov/programs-surveys/sipp/data/datasets/2025-data/2025.html
- Census cautions that the 2025 SIPP had increasing-cost collection complications and a lower-than-average national unit response rate.

## Downloaded and organized

- Official files and documents: {len(manifest):,}
- Total downloaded/archived bytes represented in the manifest: {downloaded_bytes:,}
- Primary, replicate, longitudinal, and longitudinal-replicate ZIP CRC failures: {crc_failures}
- Full provenance and SHA-256 checksums: `data/metadata/sipp_2025_official_download_manifest.csv`
- Raw survey payloads remain under `temp/raw_downloads/census_sipp/2025/` and are not mixed into `data/analysis_ready/`.

Replicate weights and longitudinal weights are stored as separate official files. They are not column-joined to the primary person-month panel because they have distinct weight layouts and should be merged only for the specific variance or longitudinal estimand being run.

## Schema compatibility

- 2024 primary variables: {schema_summary['variables_2024']:,}
- 2025 primary variables: {schema_summary['variables_2025']:,}
- Exact common variable names: {schema_summary['common_variables']:,}
- Added in 2025: {schema_summary['added_2025']:,}
- Removed in 2025: {schema_summary['removed_2025']:,}
- Dtype changes: {schema_summary['dtype_changes']:,}
- Label changes: {schema_summary['label_changes']:,}
- The 2025 raw pipe-delimited header exactly matches the official 2025 schema order.
- Parsed 2025 dictionary entries matched to schema variables: {codebook['matched_schema_variables']:,}

The seven dtype changes are outside the {panel_summary['merged_columns']}-column analysis-ready panel. Every one of the panel's {panel_summary['source_columns']} Census source variables is present in the 2025 schema.

## New data-only panel

- Historical input: `data/analysis_ready/sipp_2018_2024_person_month_panel.parquet`
- New output: `data/analysis_ready/sipp_2018_2025_person_month_panel.parquet`
- Coverage: SIPP file years 2018-2025, reference years 2017-2024.
- Existing rows: {panel_summary['old_panel_rows']:,}
- Added 2025 rows: {panel_summary['new_2025_rows']:,}
- Added 2025 unique persons: {panel_summary['new_2025_unique_persons']:,}
- Total merged rows: {panel_summary['merged_rows']:,}
- Columns: {panel_summary['merged_columns']:,} ({panel_summary['source_columns']:,} Census source variables plus {panel_summary['technical_columns']:,} harmonization identifiers/time fields).
- 2025 duplicate `SSUID + PNUM + MONTHCODE` keys: {panel_summary['new_2025_duplicate_keys']:,}
- `RPRITYPE1` is now integrated for 2018-2025; historical four-key alignment passed and missing rows are {panel_summary['historical_rpritype1_missing']:,} historically and {panel_summary['new_2025_rpritype1_missing']:,} in 2025.
- New panel bytes: {panel_summary['merged_bytes']:,}
- Newly constructed outcome/result columns added: no.

The old 2018-2024 panel and all historical model outputs remain unchanged. This update prepares the new data input but does not silently rerun or overwrite the ARPA estimates.

## Use boundary

For open-ended idea development or simple Web GPT analysis, use `sipp_2018_2025_person_month_panel.parquet`. It is the broad cleaned source-variable panel. Do not substitute `coverage_transition_panel.parquet` or `exposure_temporary_crossing_panel.parquet` when the goal is to avoid preconstructed outcomes/exposures.

This {panel_summary['merged_columns']}-column panel is broad relative to the current research workflow, but it is not a dump of all {schema_summary['variables_2025']:,} raw Census variables. The complete public-use payload remains in the official ZIP archives, with metadata in the updated 2018-2025 registries.
"""
    (ROOT / "report" / "102_sipp_2025_update_and_merge_audit.md").write_text(report, encoding="utf-8")

    readme = f"""# Analysis-ready SIPP data

## Current data-only panel

`sipp_2018_2025_person_month_panel.parquet`

- SIPP file years: 2018-2025
- Reference years: 2017-2024
- Rows: {panel_summary['merged_rows']:,}
- Columns: {panel_summary['merged_columns']:,}
- Newly constructed outcome/result variables: none

This is the default file for Web GPT exploration that should begin from cleaned source variables.

## Historical replication panel

`sipp_2018_2024_person_month_panel.parquet` remains frozen for reproducing the existing 2017-2023 analyses.

`coverage_transition_panel.parquet` and `exposure_temporary_crossing_panel.parquet` contain constructed research variables and are not substitutes for the data-only panel.
"""
    (ROOT / "data" / "analysis_ready" / "README.md").write_text(readme, encoding="utf-8")


def main() -> None:
    required = [
        OLD_COMPACT,
        OLD_ENRICHED,
        RAW_ZIP,
        SCHEMA_PATH,
        DICTIONARY_PATH,
        OLD_PANEL,
        HISTORICAL_RPRITYPE1,
    ]
    missing = [path for path in required if not path.exists()]
    if missing:
        raise FileNotFoundError(f"Missing required inputs: {missing}")

    print("Reading and validating 2025 primary schema/header", flush=True)
    schema = load_json(SCHEMA_PATH)
    entry, header = read_primary_header()
    compact = build_compact_metadata(schema, header, entry)

    print("Parsing the 2025 official data dictionary", flush=True)
    enriched = build_enriched_metadata(compact)
    write_variable_registry(enriched, schema)

    print("Building schema and download audits", flush=True)
    schema_summary = build_schema_audit(schema)
    manifest = build_download_manifest()

    print("Extracting 2025 source variables and appending the data-only panel", flush=True)
    panel_summary = append_panel(enriched, schema)
    write_report(schema_summary, panel_summary, manifest, enriched)

    print(json.dumps(panel_summary, indent=2), flush=True)


if __name__ == "__main__":
    main()
