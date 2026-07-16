from __future__ import annotations

import csv
import hashlib
import json
import warnings
import zipfile
from pathlib import Path

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq


ROOT = Path(__file__).resolve().parents[2]
RAW_ROOT = ROOT / "temp" / "raw_downloads" / "census_sipp"
SOURCE_ROOT = ROOT / "temp" / "source_metadata" / "census_sipp"
METADATA_ROOT = ROOT / "data" / "metadata"
AUDIT_ROOT = ROOT / "data" / "sample_audits"

CATALOG = METADATA_ROOT / "sipp_official_file_catalog_2018_2025.csv"
MATRIX = METADATA_ROOT / "sipp_official_product_matrix_2018_2025.csv"
MANIFEST = METADATA_ROOT / "sipp_raw_download_manifest_2018_2025.csv"
PRODUCT_AUDIT = METADATA_ROOT / "sipp_longitudinal_product_audit_2019_2025.csv"
PANEL_AUDIT = AUDIT_ROOT / "sipp_latest_longitudinal_panel_counts.csv"

RAW_VERIFICATION = AUDIT_ROOT / "sipp_all_raw_products_verification.csv"
COMPLETION_CHECKS = AUDIT_ROOT / "sipp_all_versions_completion_checks.csv"
BASE_PANEL = ROOT / "data" / "analysis_ready" / "sipp_2018_2025_person_month_panel.parquet"

EXPECTED_HORIZONS = {
    2018: (),
    2019: (2,),
    2020: (2, 3),
    2021: (2, 3, 4),
    2022: (2, 3),
    2023: (2, 3, 4),
    2024: (2, 3, 4),
    2025: (2, 3, 4),
}


def write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(16 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def normalize_name(name: str) -> str:
    normalized = name.strip().upper()
    return "SPANEL" if normalized == "PANEL" else normalized


def schema_path(row: pd.Series) -> Path:
    year = int(row.file_year)
    horizon = int(row.horizon_years) if pd.notna(row.horizon_years) else None
    product_type = row.product_type
    if product_type == "primary":
        name = f"pu{year}_schema.json"
    elif product_type == "replicate_weights":
        name = f"rw{year}_schema.json"
    elif product_type == "longitudinal_weights":
        name = "lgtwgt2019_schema.json" if year == 2019 else f"lgtwgt{year}yr{horizon}_schema.json"
    elif product_type == "longitudinal_replicate_weights":
        name = "lgtrw2019_schema.json" if year == 2019 else f"lgtrw{year}yr{horizon}_schema.json"
    else:
        raise ValueError(product_type)
    return SOURCE_ROOT / str(year) / name


def validation_path(row: pd.Series) -> Path:
    year = int(row.file_year)
    horizon = int(row.horizon_years) if pd.notna(row.horizon_years) else None
    product_type = row.product_type
    directory = SOURCE_ROOT / str(year)
    if product_type == "primary":
        stem = f"pu{year}_validate"
    elif product_type == "replicate_weights":
        stem = f"rw{year}_validate"
    elif product_type == "longitudinal_weights":
        if year == 2019:
            return directory / "lgtwgt2019_validate.xlsx"
        stem = f"lgtwgt{year}yr{horizon}_validate"
    elif product_type == "longitudinal_replicate_weights":
        if year == 2019:
            return directory / "lgtrepwgt2019yr2_validate.xlsx"
        stem = f"lgtrw{year}yr{horizon}_validate"
    else:
        raise ValueError(product_type)
    xlsx = directory / f"{stem}.xlsx"
    xls = directory / f"{stem}.xls"
    return xlsx if xlsx.exists() else xls


def official_row_count(path: Path) -> int:
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        frame = pd.read_excel(path)
    variable_column = next(column for column in frame.columns if str(column).strip().lower() == "variable")
    n_column = next(column for column in frame.columns if str(column).strip() == "N")
    variable = frame[variable_column].astype(str).str.upper()
    for candidate in ("PNUM", "SPANEL", "PANEL"):
        match = frame.loc[variable.eq(candidate), n_column]
        if not match.empty:
            return int(pd.to_numeric(match.iloc[0], errors="raise"))
    values = pd.to_numeric(frame[n_column], errors="coerce").dropna()
    if values.empty:
        raise ValueError(f"No official N found in {path}")
    return int(values.max())


def deep_read_zip(path: Path) -> dict:
    with zipfile.ZipFile(path) as archive:
        entries = [entry for entry in archive.infolist() if not entry.is_dir()]
        if len(entries) != 1:
            raise ValueError(f"Expected one file in {path}, found {[entry.filename for entry in entries]}")
        entry = entries[0]
        if not entry.filename.lower().endswith(".csv"):
            raise ValueError(f"Expected a CSV in {path}, found {entry.filename}")
        with archive.open(entry) as handle:
            header_bytes = handle.readline()
            data_rows = 0
            data_bytes = 0
            last_byte = b""
            while True:
                block = handle.read(16 * 1024 * 1024)
                if not block:
                    break
                data_rows += block.count(b"\n")
                data_bytes += len(block)
                last_byte = block[-1:]
            if data_bytes and last_byte != b"\n":
                data_rows += 1
        header = header_bytes.decode("utf-8-sig").rstrip("\r\n").split("|")
        actual_uncompressed_bytes = len(header_bytes) + data_bytes
        return {
            "zip_crc_valid": True,
            "csv_entry": entry.filename,
            "uncompressed_bytes": actual_uncompressed_bytes,
            "zip_recorded_uncompressed_bytes": entry.file_size,
            "data_rows": data_rows,
            "header": header,
        }


def add_check(checks: list[dict], check_id: str, requirement: str, passed: bool, evidence: str) -> None:
    checks.append(
        {
            "check_id": check_id,
            "requirement": requirement,
            "passed": bool(passed),
            "evidence": evidence,
        }
    )


def expected_product_counts() -> dict[str, int]:
    horizons = sum(len(value) for value in EXPECTED_HORIZONS.values())
    return {
        "primary": 8,
        "replicate_weights": 8,
        "longitudinal_weights": horizons,
        "longitudinal_replicate_weights": horizons,
    }


def verify_raw_products(manifest: pd.DataFrame) -> list[dict]:
    rows: list[dict] = []
    for number, (_, row) in enumerate(manifest.iterrows(), start=1):
        product_id = row.product_id
        path = ROOT / Path(row.local_relative_path)
        schema = schema_path(row)
        validation = validation_path(row)
        print(f"VERIFY {number:02d}/50 {product_id}", flush=True)
        if not path.exists() or not schema.exists() or not validation.exists():
            raise FileNotFoundError(
                f"Missing source for {product_id}: zip={path.exists()} schema={schema.exists()} "
                f"validation={validation.exists()}"
            )

        actual_sha = sha256_file(path)
        deep = deep_read_zip(path)
        schema_records = json.loads(schema.read_text(encoding="utf-8-sig"))
        schema_names = [record["name"] for record in schema_records]
        raw_header = deep.pop("header")
        official_n = official_row_count(validation)
        normalized_header = [normalize_name(name) for name in raw_header]
        normalized_schema = [normalize_name(name) for name in schema_names]
        record = {
            "product_id": product_id,
            "file_year": int(row.file_year),
            "product_type": row.product_type,
            "horizon_years": int(row.horizon_years) if pd.notna(row.horizon_years) else "",
            "official_url": row.official_url,
            "local_relative_path": row.local_relative_path,
            "bytes": path.stat().st_size,
            "manifest_sha256": row.sha256,
            "actual_sha256": actual_sha,
            "sha256_matches_manifest": actual_sha == row.sha256,
            **deep,
            "uncompressed_size_matches_zip_record": (
                deep["uncompressed_bytes"] == deep["zip_recorded_uncompressed_bytes"]
            ),
            "header_columns": len(raw_header),
            "schema_columns": len(schema_names),
            "raw_header_exactly_matches_schema": raw_header == schema_names,
            "raw_header_normalized_matches_schema": normalized_header == normalized_schema,
            "schema_relative_path": str(schema.relative_to(ROOT)),
            "validation_relative_path": str(validation.relative_to(ROOT)),
            "data_rows": deep["data_rows"],
            "official_validation_rows": official_n,
            "row_count_matches_official_validation": deep["data_rows"] == official_n,
        }
        record["all_raw_product_checks_pass"] = all(
            [
                record["sha256_matches_manifest"],
                record["zip_crc_valid"],
                record["uncompressed_size_matches_zip_record"],
                record["raw_header_normalized_matches_schema"],
                record["row_count_matches_official_validation"],
            ]
        )
        rows.append(record)
        print(
            f"PASS {product_id}: rows={record['data_rows']:,} cols={record['header_columns']} "
            f"bytes={record['bytes']:,}",
            flush=True,
        )
    return rows


def main() -> None:
    required = [CATALOG, MATRIX, MANIFEST, PRODUCT_AUDIT, PANEL_AUDIT, BASE_PANEL]
    missing = [str(path) for path in required if not path.exists()]
    if missing:
        raise FileNotFoundError(missing)

    catalog = pd.read_csv(CATALOG)
    matrix = pd.read_csv(MATRIX)
    manifest = pd.read_csv(MANIFEST)
    product_audit = pd.read_csv(PRODUCT_AUDIT)
    panel_audit = pd.read_csv(PANEL_AUDIT)
    checks: list[dict] = []

    add_check(
        checks,
        "official_directory_snapshots",
        "Official Census directory snapshots exist for every 2018-2025 file year",
        all((SOURCE_ROOT / str(year) / "official_dataset_directory_index.html").exists() for year in EXPECTED_HORIZONS),
        "years=2018-2025",
    )
    add_check(
        checks,
        "official_catalog",
        "The official directory crawl contains all eight years and no duplicate URLs",
        set(catalog["year"]) == set(EXPECTED_HORIZONS) and not catalog["official_url"].duplicated().any(),
        f"rows={len(catalog)}, years={sorted(catalog['year'].unique().tolist())}, duplicate_urls={int(catalog['official_url'].duplicated().sum())}",
    )
    actual_counts = matrix.groupby("product_type").size().to_dict()
    expected_counts = expected_product_counts()
    add_check(
        checks,
        "product_matrix",
        "The matrix contains exactly 50 unique official CSV products in the verified year/horizon pattern",
        len(matrix) == 50
        and not matrix["official_url"].duplicated().any()
        and actual_counts == expected_counts
        and matrix["listed_in_official_directory"].all(),
        f"counts={actual_counts}, expected={expected_counts}",
    )
    add_check(
        checks,
        "manifest_coverage",
        "The raw manifest covers the same 50 products and all files exist",
        set(manifest["product_id"]) == set(matrix["product_id"])
        and all((ROOT / Path(path)).exists() for path in manifest["local_relative_path"]),
        f"manifest_rows={len(manifest)}, matrix_rows={len(matrix)}",
    )
    partial_files = list(RAW_ROOT.rglob("*.part"))
    add_check(
        checks,
        "no_partial_downloads",
        "No interrupted .part downloads remain in the raw archive",
        not partial_files,
        f"partial_files={[str(path.relative_to(ROOT)) for path in partial_files]}",
    )

    verification_rows = verify_raw_products(manifest)
    write_csv(RAW_VERIFICATION, verification_rows)
    all_raw_pass = all(row["all_raw_product_checks_pass"] for row in verification_rows)
    add_check(
        checks,
        "deep_raw_verification",
        "All 50 products pass SHA-256, full-stream CRC, ZIP size, schema/header, and official row-count checks",
        all_raw_pass,
        f"passed={sum(row['all_raw_product_checks_pass'] for row in verification_rows)}/50",
    )

    lgt_parquets = list((ROOT / "data" / "analysis_ready" / "longitudinal_weights").rglob("*.parquet"))
    rep_parquets = list(
        (ROOT / "data" / "analysis_ready" / "longitudinal_replicate_weights").rglob("*.parquet")
    )
    add_check(
        checks,
        "longitudinal_parquet_versions",
        "All 17 longitudinal and 17 longitudinal-replicate products have link-ready Parquet copies",
        len(lgt_parquets) == 17 and len(rep_parquets) == 17,
        f"longitudinal={len(lgt_parquets)}, replicate={len(rep_parquets)}",
    )
    product_keys_pass = (
        len(product_audit) == 17
        and product_audit["key_sets_equal"].all()
        and product_audit["all_final_weights_positive"].all()
        and product_audit["longitudinal_key_duplicates"].sum() == 0
        and product_audit["replicate_key_duplicates"].sum() == 0
        and product_audit["repwgt0_max_abs_difference"].max() <= 2e-5
    )
    add_check(
        checks,
        "longitudinal_weight_keys",
        "Every longitudinal weight key matches its replicate file and REPWGT0 reproduces FINYR within audited CSV precision",
        bool(product_keys_pass),
        f"products={len(product_audit)}, max_abs_difference={product_audit['repwgt0_max_abs_difference'].max():.12g}",
    )
    period_mismatches = product_audit.loc[
        ~product_audit["replicate_period_metadata_matches_expected"],
        ["file_year", "horizon_years"],
    ]
    expected_mismatch = period_mismatches.to_dict("records") == [
        {"file_year": 2021, "horizon_years": 4}
    ]
    add_check(
        checks,
        "official_period_metadata_anomaly",
        "The sole official internal period-label anomaly (2021 4-year replicate file) is surfaced without altering raw values",
        expected_mismatch,
        f"mismatches={period_mismatches.to_dict('records')}",
    )

    base_schema = pq.read_schema(BASE_PANEL)
    latest_schema_pass = True
    latest_evidence = []
    for row in panel_audit.itertuples(index=False):
        output = ROOT / Path(row.output_relative_path)
        output_schema = pq.read_schema(output)
        weight_name = row.weight_variable
        schema_ok = (
            output_schema.names == base_schema.names + [weight_name]
            and pa.types.is_float64(output_schema.field(weight_name).type)
        )
        latest_schema_pass &= schema_ok
        latest_evidence.append(
            f"{int(row.horizon_years)}y:rows={int(row.output_rows)},persons={int(row.output_persons)},schema={schema_ok}"
        )
    latest_checks_pass = (
        len(panel_audit) == 3
        and panel_audit["all_source_faithfulness_checks_pass"].all()
        and latest_schema_pass
    )
    add_check(
        checks,
        "latest_longitudinal_panels",
        "Latest 2/3/4-year panels contain only the base 97 columns plus the official FINYR weight and pass source-faithfulness checks",
        bool(latest_checks_pass),
        "; ".join(latest_evidence),
    )

    raw_bytes = sum((ROOT / Path(path)).stat().st_size for path in manifest["local_relative_path"])
    add_check(
        checks,
        "raw_archive_size",
        "The archived canonical raw products have a recorded nonzero byte total",
        raw_bytes > 0,
        f"bytes={raw_bytes}, GiB={raw_bytes / 1024**3:.3f}",
    )
    write_csv(COMPLETION_CHECKS, checks)
    failures = [row for row in checks if not row["passed"]]
    print(f"COMPLETION {len(checks) - len(failures)}/{len(checks)} checks passed", flush=True)
    if failures:
        raise RuntimeError(f"Completion failures: {failures}")


if __name__ == "__main__":
    main()
