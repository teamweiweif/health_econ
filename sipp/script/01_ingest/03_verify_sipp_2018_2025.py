from __future__ import annotations

import hashlib
import json
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd
import pyarrow.parquet as pq


ROOT = Path(__file__).resolve().parents[2]
PANEL = ROOT / "data" / "analysis_ready" / "sipp_2018_2025_person_month_panel.parquet"
OLD_PANEL = ROOT / "data" / "analysis_ready" / "sipp_2018_2024_person_month_panel.parquet"
YEAR_EXTRACT = ROOT / "temp" / "scratch" / "sipp_2025_selected.parquet"
RPRITYPE1_HISTORY = ROOT / "temp" / "scratch" / "rpritype1_2018_2024.parquet"
SCHEMA_2024 = ROOT / "temp" / "source_metadata" / "census_sipp" / "2024" / "pu2024_schema.json"
SCHEMA_2025 = ROOT / "temp" / "source_metadata" / "census_sipp" / "2025" / "pu2025_schema.json"
RAW_2025 = ROOT / "temp" / "raw_downloads" / "census_sipp" / "2025" / "primary" / "pu2025_csv.zip"
VALIDATE_2025 = ROOT / "temp" / "source_metadata" / "census_sipp" / "2025" / "pu2025_validate.xlsx"
MANIFEST = ROOT / "data" / "metadata" / "sipp_2025_official_download_manifest.csv"
COUNTS = ROOT / "data" / "sample_audits" / "panel_build_yearly_counts_2018_2025.csv"
ENRICHED_META = (
    ROOT / "temp" / "source_metadata" / "sipp_2018_2025_raw_variable_metadata.enriched.compact.json"
)

TECHNICAL_COLUMNS = {
    "file_year",
    "reference_year",
    "reference_month",
    "reference_date",
    "state_fips",
    "person_id",
    "person_month_key",
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(4 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def add_check(checks: list[dict], check_id: str, requirement: str, passed: bool, evidence: str) -> None:
    checks.append(
        {
            "check_id": check_id,
            "requirement": requirement,
            "passed": bool(passed),
            "evidence": evidence,
        }
    )


def main() -> None:
    checks: list[dict] = []
    required = [
        PANEL,
        OLD_PANEL,
        YEAR_EXTRACT,
        RPRITYPE1_HISTORY,
        SCHEMA_2024,
        SCHEMA_2025,
        RAW_2025,
        VALIDATE_2025,
        MANIFEST,
        COUNTS,
        ENRICHED_META,
    ]
    missing = [str(path) for path in required if not path.exists()]
    add_check(checks, "required_files", "All required source and output files exist", not missing, str(missing))
    if missing:
        finish(checks)
        return

    manifest = pd.read_csv(MANIFEST)
    manifest_missing = [
        rel for rel in manifest["local_relative_path"] if not (ROOT / Path(rel)).exists()
    ]
    add_check(
        checks,
        "manifest_files",
        "Every official-download manifest entry exists locally",
        not manifest_missing,
        f"entries={len(manifest)}, missing={manifest_missing}",
    )
    actual_hashes = {
        rel: sha256_file(ROOT / Path(rel)) for rel in manifest["local_relative_path"]
    }
    hash_mismatches = [
        rel
        for rel, expected in zip(
            manifest["local_relative_path"], manifest["sha256"], strict=True
        )
        if actual_hashes[rel] != expected
    ]
    add_check(
        checks,
        "manifest_sha256",
        "All archived official files match recorded SHA-256 hashes",
        not hash_mismatches,
        f"checked={len(actual_hashes)}, mismatches={hash_mismatches}",
    )
    zip_rows = manifest[manifest["local_relative_path"].str.lower().str.endswith(".zip")]
    crc_failures = []
    for rel in zip_rows["local_relative_path"]:
        with zipfile.ZipFile(ROOT / Path(rel)) as archive:
            if archive.testzip() is not None:
                crc_failures.append(rel)
    add_check(
        checks,
        "zip_crc",
        "All downloaded 2025 ZIP archives pass CRC validation",
        not crc_failures,
        f"checked={len(zip_rows)}, failures={crc_failures}",
    )
    official_domains = manifest["official_url"].str.contains(
        r"^https://www2?\.census\.gov/", regex=True
    ).all()
    add_check(
        checks,
        "official_urls",
        "Every manifest URL is an official Census URL",
        bool(official_domains),
        f"official={bool(official_domains)}",
    )

    schema_2024 = json.loads(SCHEMA_2024.read_text(encoding="utf-8-sig"))
    schema_2025 = json.loads(SCHEMA_2025.read_text(encoding="utf-8-sig"))
    names_2024 = [record["name"] for record in schema_2024]
    names_2025 = [record["name"] for record in schema_2025]
    add_check(
        checks,
        "schema_count",
        "The 2025 primary schema has 5,203 unique variables",
        len(names_2025) == 5203 and len(set(names_2025)) == 5203,
        f"variables={len(names_2025)}, unique={len(set(names_2025))}",
    )
    add_check(
        checks,
        "schema_name_set",
        "The 2024 and 2025 primary variable-name sets are identical",
        set(names_2024) == set(names_2025),
        f"2024={len(names_2024)}, 2025={len(names_2025)}, symmetric_diff={len(set(names_2024) ^ set(names_2025))}",
    )
    with zipfile.ZipFile(RAW_2025) as archive:
        entry = archive.namelist()[0]
        with archive.open(entry) as handle:
            raw_header = handle.readline().decode("utf-8-sig").rstrip("\r\n").split("|")
    add_check(
        checks,
        "schema_header_order",
        "The 2025 raw CSV header exactly matches official schema order",
        raw_header == names_2025,
        f"header={len(raw_header)}, schema={len(names_2025)}",
    )

    validation = pd.read_excel(VALIDATE_2025)
    official_n = int(validation.loc[validation["Variable"].eq("SPANEL"), "N"].iloc[0])
    year_pf = pq.ParquetFile(YEAR_EXTRACT)
    add_check(
        checks,
        "official_row_count",
        "The cleaned 2025 extract row count matches Census validation",
        year_pf.metadata.num_rows == official_n == 379215,
        f"official={official_n}, extract={year_pf.metadata.num_rows}",
    )

    panel_pf = pq.ParquetFile(PANEL)
    old_pf = pq.ParquetFile(OLD_PANEL)
    add_check(
        checks,
        "merged_dimensions",
        "Merged rows equal frozen historical rows plus 2025 rows, with 97 columns",
        panel_pf.metadata.num_rows == old_pf.metadata.num_rows + official_n
        and panel_pf.metadata.num_columns == 97,
        (
            f"merged={panel_pf.metadata.num_rows}x{panel_pf.metadata.num_columns}, "
            f"historical={old_pf.metadata.num_rows}x{old_pf.metadata.num_columns}, 2025={official_n}"
        ),
    )
    add_check(
        checks,
        "historical_panel_frozen",
        "The historical replication panel remains the original 4,051,455 x 96 file",
        old_pf.metadata.num_rows == 4051455
        and old_pf.metadata.num_columns == 96
        and "RPRITYPE1" not in old_pf.schema_arrow.names,
        f"rows={old_pf.metadata.num_rows}, columns={old_pf.metadata.num_columns}",
    )

    key_columns = [
        "file_year",
        "reference_year",
        "reference_month",
        "SSUID",
        "PNUM",
        "MONTHCODE",
        "person_month_key",
        "person_id",
        "state_fips",
        "RPRITYPE1",
        "WPFINWGT",
        "TFINCPOV",
        "THINCPOV",
        "RHLTHMTH",
        "RMARKTPLACE",
        "RPRITYPE2",
        "EMDMTH",
    ]
    panel = pd.read_parquet(PANEL, columns=key_columns)
    year_counts = (
        panel.groupby(["file_year", "reference_year"], dropna=False)
        .agg(
            rows=("person_month_key", "size"),
            persons=("person_id", "nunique"),
            months=("reference_month", "nunique"),
            states=("state_fips", "nunique"),
        )
        .reset_index()
    )
    expected_file_years = set(range(2018, 2026))
    expected_reference_years = set(range(2017, 2025))
    add_check(
        checks,
        "year_coverage",
        "Merged panel covers file years 2018-2025 and reference years 2017-2024",
        set(year_counts["file_year"].astype(int)) == expected_file_years
        and set(year_counts["reference_year"].astype(int)) == expected_reference_years,
        year_counts.to_json(orient="records"),
    )
    add_check(
        checks,
        "all_months",
        "Every file year contains all 12 reference months",
        year_counts["months"].eq(12).all(),
        year_counts[["file_year", "months"]].to_json(orient="records"),
    )
    duplicate_person_month_keys = int(panel["person_month_key"].duplicated().sum())
    add_check(
        checks,
        "technical_key_unique",
        "The merged technical person-month key is unique",
        duplicate_person_month_keys == 0,
        f"duplicates={duplicate_person_month_keys}",
    )
    year_2025 = panel[panel["file_year"].eq(2025)]
    duplicate_2025 = int(year_2025.duplicated(["SSUID", "PNUM", "MONTHCODE"]).sum())
    add_check(
        checks,
        "raw_key_2025_unique",
        "SSUID + PNUM + MONTHCODE is unique within 2025",
        duplicate_2025 == 0,
        f"duplicates={duplicate_2025}",
    )

    counts = pd.read_csv(COUNTS)
    observed_counts = year_counts.set_index("file_year")["rows"].astype(int).to_dict()
    audited_counts = counts.set_index("file_year")["rows"].astype(int).to_dict()
    add_check(
        checks,
        "year_count_audit",
        "Merged row counts by file year equal the build audit",
        observed_counts == audited_counts,
        f"observed={observed_counts}, audited={audited_counts}",
    )

    panel_columns = panel_pf.schema_arrow.names
    source_columns = [name for name in panel_columns if name not in TECHNICAL_COLUMNS]
    unknown_source_columns = sorted(set(source_columns) - set(names_2025))
    add_check(
        checks,
        "source_only_columns",
        "All 90 nontechnical panel columns are official 2025 Census source variables",
        len(source_columns) == 90 and not unknown_source_columns,
        f"source_columns={len(source_columns)}, unknown={unknown_source_columns}",
    )
    add_check(
        checks,
        "no_constructed_outcomes",
        "No constructed outcome, exposure, or result columns were added",
        not unknown_source_columns,
        "Nontechnical fields are a strict subset of the official schema",
    )

    supplement = pd.read_parquet(RPRITYPE1_HISTORY)
    supplement["SSUID"] = supplement["SSUID"].astype("int64").astype(str).str.zfill(14)
    supplement["PNUM"] = supplement["PNUM"].astype("int64")
    supplement["MONTHCODE"] = supplement["MONTHCODE"].astype("int64")
    supplement["file_year"] = supplement["file_year"].astype("int64")
    supplement["person_id"] = supplement["SSUID"] + "-" + supplement["PNUM"].astype(str)
    supplement["reference_date"] = pd.to_datetime(
        dict(
            year=supplement["file_year"] - 1,
            month=supplement["MONTHCODE"],
            day=1,
        )
    )
    supplement = supplement.sort_values(
        ["person_id", "reference_date", "file_year", "MONTHCODE"], kind="mergesort"
    ).reset_index(drop=True)
    historical_values = panel.loc[panel["file_year"].le(2024), "RPRITYPE1"].to_numpy()
    supplement_values = pd.to_numeric(supplement["RPRITYPE1"], errors="coerce").to_numpy()
    rpritype1_matches = np.array_equal(historical_values, supplement_values, equal_nan=True)
    add_check(
        checks,
        "rpritype1_history",
        "Historical RPRITYPE1 values exactly match the independently built supplement",
        rpritype1_matches,
        f"rows={len(historical_values)}, missing={int(pd.isna(historical_values).sum())}",
    )
    rpritype1_2025_missing = int(year_2025["RPRITYPE1"].isna().sum())
    add_check(
        checks,
        "rpritype1_2025",
        "RPRITYPE1 is present and nonmissing in the 2025 clean extract",
        rpritype1_2025_missing == 0,
        f"rows={len(year_2025)}, missing={rpritype1_2025_missing}",
    )

    metadata = json.loads(ENRICHED_META.read_text(encoding="utf-8-sig"))
    metadata_ok = (
        metadata["summary"]["survey_years"] == [str(year) for year in range(2018, 2026)]
        and metadata["years"]["2025"]["schema"]["variable_count"] == 5203
        and "2025" in metadata["codebook_coverage"]
    )
    add_check(
        checks,
        "metadata_coverage",
        "Updated enriched metadata covers 2018-2025 and includes the 2025 codebook audit",
        metadata_ok,
        (
            f"years={metadata['summary']['survey_years']}, "
            f"2025_schema={metadata['years']['2025']['schema']['variable_count']}, "
            f"2025_codebook_matches={metadata['codebook_coverage']['2025']['matched_schema_variables']}"
        ),
    )

    finish(checks)


def finish(checks: list[dict]) -> None:
    output = pd.DataFrame(checks)
    csv_path = ROOT / "data" / "sample_audits" / "sipp_2018_2025_completion_check.csv"
    output.to_csv(csv_path, index=False)
    passed = int(output["passed"].sum())
    total = len(output)
    lines = [
        "# SIPP 2018-2025 Completion Check",
        "",
        f"Result: {'PASS' if passed == total else 'FAIL'} ({passed}/{total} checks passed).",
        "",
        "| Check | Passed | Evidence |",
        "|---|---:|---|",
    ]
    for row in output.itertuples(index=False):
        evidence = str(row.evidence).replace("|", "\\|").replace("\n", " ")
        lines.append(f"| {row.check_id} | {str(bool(row.passed)).lower()} | {evidence} |")
    report_path = ROOT / "report" / "103_sipp_2018_2025_completion_check.md"
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"{'PASS' if passed == total else 'FAIL'}: {passed}/{total}")
    print(output[["check_id", "passed"]].to_string(index=False))
    if passed != total:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
