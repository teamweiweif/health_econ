from __future__ import annotations

import csv
import json
import os
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.compute as pc
import pyarrow.parquet as pq


ROOT = Path(__file__).resolve().parents[2]
RAW_ROOT = ROOT / "temp" / "raw_downloads" / "census_sipp"
SOURCE_ROOT = ROOT / "temp" / "source_metadata" / "census_sipp"
PANEL = ROOT / "data" / "analysis_ready" / "sipp_2018_2025_person_month_panel.parquet"
LONGITUDINAL_ROOT = ROOT / "data" / "analysis_ready" / "longitudinal"
WEIGHT_ROOT = ROOT / "data" / "analysis_ready" / "longitudinal_weights"
REPLICATE_ROOT = ROOT / "data" / "analysis_ready" / "longitudinal_replicate_weights"
METADATA_ROOT = ROOT / "data" / "metadata"
AUDIT_ROOT = ROOT / "data" / "sample_audits"

PRODUCT_AUDIT = METADATA_ROOT / "sipp_longitudinal_product_audit_2019_2025.csv"
HEADER_AUDIT = METADATA_ROOT / "sipp_longitudinal_header_normalization_2019_2025.csv"
PANEL_AUDIT = AUDIT_ROOT / "sipp_latest_longitudinal_panel_counts.csv"
INCOMPLETE_PERSON_YEAR_AUDIT = (
    AUDIT_ROOT / "sipp_latest_longitudinal_incomplete_person_years.csv"
)

PERIODS = {
    2019: (2,),
    2020: (2, 3),
    2021: (2, 3, 4),
    2022: (2, 3),
    2023: (2, 3, 4),
    2024: (2, 3, 4),
    2025: (2, 3, 4),
}
REPWGT0_TOLERANCE = 2e-5


def write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def raw_paths(year: int, horizon: int) -> tuple[Path, Path]:
    lgt_name = "lgtwgt2019_csv.zip" if year == 2019 else f"lgtwgt{year}yr{horizon}_csv.zip"
    return (
        RAW_ROOT / str(year) / "longitudinal_weights" / lgt_name,
        RAW_ROOT
        / str(year)
        / "longitudinal_replicate_weights"
        / f"lgtrw{year}yr{horizon}_csv.zip",
    )


def schema_paths(year: int, horizon: int) -> tuple[Path, Path]:
    lgt_name = "lgtwgt2019_schema.json" if year == 2019 else f"lgtwgt{year}yr{horizon}_schema.json"
    rep_name = "lgtrw2019_schema.json" if year == 2019 else f"lgtrw{year}yr{horizon}_schema.json"
    return SOURCE_ROOT / str(year) / lgt_name, SOURCE_ROOT / str(year) / rep_name


def validation_paths(year: int, horizon: int) -> tuple[Path, Path]:
    if year == 2019:
        return (
            SOURCE_ROOT / "2019" / "lgtwgt2019_validate.xlsx",
            SOURCE_ROOT / "2019" / "lgtrepwgt2019yr2_validate.xlsx",
        )
    extension = "xls" if year == 2020 else "xlsx"
    return (
        SOURCE_ROOT / str(year) / f"lgtwgt{year}yr{horizon}_validate.{extension}",
        SOURCE_ROOT / str(year) / f"lgtrw{year}yr{horizon}_validate.{extension}",
    )


def normalize_name(name: str) -> str:
    normalized = name.strip().upper()
    return "SPANEL" if normalized == "PANEL" else normalized


def read_zip_csv(path: Path) -> tuple[pd.DataFrame, str, list[str]]:
    with zipfile.ZipFile(path) as archive:
        entries = [item for item in archive.infolist() if not item.is_dir()]
        if len(entries) != 1 or not entries[0].filename.lower().endswith(".csv"):
            raise ValueError(f"Expected exactly one CSV entry in {path}, found {[x.filename for x in entries]}")
        entry = entries[0].filename
        with archive.open(entry) as handle:
            raw_header = handle.readline().decode("utf-8-sig").rstrip("\r\n").split("|")
        ssuid_name = next(name for name in raw_header if name.upper() == "SSUID")
        with archive.open(entry) as handle:
            frame = pd.read_csv(
                handle,
                sep="|",
                dtype={ssuid_name: "string"},
                low_memory=False,
            )

    normalized = [normalize_name(name) for name in frame.columns]
    if len(normalized) != len(set(normalized)):
        raise ValueError(f"Header normalization creates duplicate names in {path}")
    frame.columns = normalized
    frame["SSUID"] = frame["SSUID"].astype("string").str.zfill(14)
    frame["PNUM"] = pd.to_numeric(frame["PNUM"], errors="raise").astype("int64")
    frame["SPANEL"] = pd.to_numeric(frame["SPANEL"], errors="raise").astype("int64")
    return frame, entry, raw_header


def schema_normalized_names(path: Path) -> list[str]:
    records = json.loads(path.read_text(encoding="utf-8-sig"))
    return [normalize_name(record["name"]) for record in records]


def validation_n(path: Path) -> int:
    frame = pd.read_excel(path)
    if "N" not in frame.columns or frame.empty:
        raise ValueError(f"No N column found in {path}")
    values = pd.to_numeric(frame["N"], errors="coerce").dropna().astype("int64").unique()
    if len(values) != 1:
        raise ValueError(f"Validation N is not constant in {path}: {values.tolist()}")
    return int(values[0])


def key_index(frame: pd.DataFrame) -> pd.MultiIndex:
    return pd.MultiIndex.from_frame(frame[["SSUID", "PNUM", "SPANEL"]])


def output_weight_paths(year: int, horizon: int, lgt_zip: Path, rep_zip: Path) -> tuple[Path, Path]:
    return (
        WEIGHT_ROOT / str(year) / (lgt_zip.stem.replace("_csv", "") + ".parquet"),
        REPLICATE_ROOT / str(year) / (rep_zip.stem.replace("_csv", "") + ".parquet"),
    )


def convert_and_audit_weights() -> tuple[list[dict], list[dict], dict[int, pd.DataFrame]]:
    product_rows: list[dict] = []
    header_rows: list[dict] = []
    latest_weights: dict[int, pd.DataFrame] = {}

    for year, horizons in PERIODS.items():
        for horizon in horizons:
            print(f"WEIGHTS {year} {horizon}y", flush=True)
            lgt_zip, rep_zip = raw_paths(year, horizon)
            lgt_schema, rep_schema = schema_paths(year, horizon)
            lgt_validation, rep_validation = validation_paths(year, horizon)
            required = [lgt_zip, rep_zip, lgt_schema, rep_schema, lgt_validation, rep_validation]
            missing = [str(path) for path in required if not path.exists()]
            if missing:
                raise FileNotFoundError(f"Missing longitudinal source files: {missing}")

            lgt, lgt_entry, lgt_header = read_zip_csv(lgt_zip)
            rep, rep_entry, rep_header = read_zip_csv(rep_zip)
            weight_name = f"FINYR{horizon}"
            expected_rep_names = ["REPWGT0"] + [f"REPWGT{i}" for i in range(1, 241)]
            if weight_name not in lgt.columns:
                raise ValueError(f"{weight_name} is absent from {lgt_zip}")
            if any(name not in rep.columns for name in expected_rep_names):
                raise ValueError(f"Replicate columns are incomplete in {rep_zip}")

            lgt_names_normalized = [normalize_name(name) for name in lgt_header]
            rep_names_normalized = [normalize_name(name) for name in rep_header]
            lgt_schema_names = schema_normalized_names(lgt_schema)
            rep_schema_names = schema_normalized_names(rep_schema)
            if lgt_names_normalized != lgt_schema_names:
                raise ValueError(f"Longitudinal schema/header mismatch for {year} {horizon}y")
            if rep_names_normalized != rep_schema_names:
                raise ValueError(f"Replicate schema/header mismatch for {year} {horizon}y")

            lgt_official_n = validation_n(lgt_validation)
            rep_official_n = validation_n(rep_validation)
            if len(lgt) != lgt_official_n or len(rep) != rep_official_n:
                raise ValueError(
                    f"Official validation count mismatch for {year} {horizon}y: "
                    f"lgt={len(lgt)}/{lgt_official_n}, rep={len(rep)}/{rep_official_n}"
                )

            lgt_key = key_index(lgt)
            rep_key = key_index(rep)
            lgt_duplicates = int(lgt_key.duplicated().sum())
            rep_duplicates = int(rep_key.duplicated().sum())
            same_keys = set(lgt_key) == set(rep_key)
            if lgt_duplicates or rep_duplicates or not same_keys:
                raise ValueError(
                    f"Key failure for {year} {horizon}y: "
                    f"lgt_dup={lgt_duplicates}, rep_dup={rep_duplicates}, same={same_keys}"
                )

            comparison = lgt[["SSUID", "PNUM", "SPANEL", weight_name]].merge(
                rep[["SSUID", "PNUM", "SPANEL", "REPWGT0"]],
                on=["SSUID", "PNUM", "SPANEL"],
                how="inner",
                validate="one_to_one",
            )
            max_abs_difference = float(
                np.max(np.abs(comparison[weight_name].to_numpy() - comparison["REPWGT0"].to_numpy()))
            )
            if max_abs_difference > REPWGT0_TOLERANCE:
                raise ValueError(
                    f"REPWGT0 does not reproduce {weight_name} for {year} {horizon}y: "
                    f"max_abs_difference={max_abs_difference}"
                )
            if not (lgt[weight_name] > 0).all():
                raise ValueError(f"Nonpositive {weight_name} values found for {year} {horizon}y")

            lgt_out, rep_out = output_weight_paths(year, horizon, lgt_zip, rep_zip)
            lgt_out.parent.mkdir(parents=True, exist_ok=True)
            rep_out.parent.mkdir(parents=True, exist_ok=True)
            lgt.to_parquet(lgt_out, index=False, compression="zstd")
            rep.to_parquet(rep_out, index=False, compression="zstd")

            initial_values = sorted(pd.to_numeric(rep["INITIAL_YEAR"], errors="raise").unique().tolist())
            final_values = sorted(pd.to_numeric(rep["FINAL_YEAR"], errors="raise").unique().tolist())
            ctl_dates = sorted(rep["CTL_DATE"].astype(str).unique().tolist())
            expected_start = year - horizon
            expected_end = year - 1
            product_rows.append(
                {
                    "file_year": year,
                    "horizon_years": horizon,
                    "reference_start_year": expected_start,
                    "reference_end_year": expected_end,
                    "weight_variable": weight_name,
                    "longitudinal_raw_zip": str(lgt_zip.relative_to(ROOT)),
                    "replicate_raw_zip": str(rep_zip.relative_to(ROOT)),
                    "longitudinal_csv_entry": lgt_entry,
                    "replicate_csv_entry": rep_entry,
                    "longitudinal_rows": len(lgt),
                    "replicate_rows": len(rep),
                    "official_validation_rows": lgt_official_n,
                    "longitudinal_key_duplicates": lgt_duplicates,
                    "replicate_key_duplicates": rep_duplicates,
                    "key_sets_equal": same_keys,
                    "all_final_weights_positive": bool((lgt[weight_name] > 0).all()),
                    "repwgt0_max_abs_difference": max_abs_difference,
                    "repwgt0_comparison_tolerance": REPWGT0_TOLERANCE,
                    "spanel_values": "|".join(map(str, sorted(lgt["SPANEL"].unique().tolist()))),
                    "replicate_initial_year_values": "|".join(map(str, initial_values)),
                    "replicate_final_year_values": "|".join(map(str, final_values)),
                    "replicate_period_metadata_matches_expected": (
                        initial_values == [expected_start] and final_values == [expected_end]
                    ),
                    "replicate_ctl_date_values": "|".join(ctl_dates),
                    "longitudinal_parquet": str(lgt_out.relative_to(ROOT)),
                    "replicate_parquet": str(rep_out.relative_to(ROOT)),
                }
            )
            for file_role, raw_header, normalized_header in (
                ("longitudinal_weights", lgt_header, lgt_names_normalized),
                ("longitudinal_replicate_weights", rep_header, rep_names_normalized),
            ):
                header_rows.extend(
                    {
                        "file_year": year,
                        "horizon_years": horizon,
                        "file_role": file_role,
                        "column_position": position,
                        "raw_column_name": raw_name,
                        "normalized_column_name": normalized_name,
                        "name_changed": raw_name != normalized_name,
                    }
                    for position, (raw_name, normalized_name) in enumerate(
                        zip(raw_header, normalized_header, strict=True), start=1
                    )
                )
            if year == 2025:
                latest_weights[horizon] = lgt

    return product_rows, header_rows, latest_weights


def latest_panel_path(horizon: int) -> Path:
    start = 2025 - horizon
    end = 2024
    return LONGITUDINAL_ROOT / f"sipp_{start}_{end}_longitudinal_{horizon}y_person_month.parquet"


def build_latest_panel(horizon: int, weights: pd.DataFrame) -> tuple[dict, list[dict]]:
    weight_name = f"FINYR{horizon}"
    file_years = list(range(2026 - horizon, 2026))
    reference_years = list(range(2025 - horizon, 2025))
    output = latest_panel_path(horizon)
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_name(output.name + ".part")
    if temporary.exists():
        temporary.unlink()

    panel_file = pq.ParquetFile(PANEL)
    panel_schema = panel_file.schema_arrow
    output_schema = panel_schema.append(pa.field(weight_name, pa.float64(), nullable=True))
    merge_weights = weights[["SSUID", "PNUM", "SPANEL", weight_name]].copy()
    merge_weights["SPANEL"] = merge_weights["SPANEL"].astype("float64")
    writer = pq.ParquetWriter(temporary, output_schema, compression="zstd")
    written = 0
    try:
        for batch_number, batch in enumerate(panel_file.iter_batches(batch_size=125_000), start=1):
            table = pa.Table.from_batches([batch])
            mask = pc.is_in(table["file_year"], value_set=pa.array(file_years, type=pa.int64()))
            table = table.filter(mask)
            if table.num_rows == 0:
                continue
            frame = table.to_pandas()
            merged = frame.merge(
                merge_weights,
                on=["SSUID", "PNUM", "SPANEL"],
                how="inner",
                validate="many_to_one",
                sort=False,
            )
            if merged.empty:
                continue
            merged = merged[panel_schema.names + [weight_name]]
            out_table = pa.Table.from_pandas(merged, schema=output_schema, preserve_index=False)
            writer.write_table(out_table, row_group_size=125_000)
            written += len(merged)
            print(
                f"PANEL {horizon}y batch={batch_number} written={written:,}",
                flush=True,
            )
    finally:
        writer.close()
    os.replace(temporary, output)

    keys = ["SSUID", "PNUM", "SPANEL"]
    audit = pq.read_table(
        output,
        columns=keys
        + ["file_year", "reference_year", "reference_month", "person_month_key", weight_name],
    ).to_pandas()
    person_counts = audit.groupby(keys, observed=True).size()
    person_year_counts = audit.groupby(keys, observed=True)["file_year"].nunique()
    person_month_counts = audit.groupby(keys + ["file_year"], observed=True)["reference_month"].nunique()
    person_month_record_counts = audit.groupby(keys + ["file_year"], observed=True).size()
    final_weight_counts = audit.groupby(keys, observed=True)[weight_name].nunique()
    output_keys = key_index(audit[keys].drop_duplicates())
    weight_keys = key_index(weights[keys])

    month_lists = audit.groupby(keys + ["file_year"], observed=True)["reference_month"].agg(
        lambda values: sorted({int(value) for value in values})
    )
    incomplete_rows: list[dict] = []
    full_month_set = set(range(1, 13))
    for index, months in month_lists.items():
        if len(months) == 12:
            continue
        ssuid, pnum, spanel, file_year = index
        incomplete_rows.append(
            {
                "horizon_years": horizon,
                "weight_variable": weight_name,
                "SSUID": ssuid,
                "PNUM": int(pnum),
                "SPANEL": int(spanel),
                "file_year": int(file_year),
                "reference_year": int(file_year) - 1,
                "observed_month_count": len(months),
                "observed_months": "|".join(map(str, months)),
                "missing_month_count": 12 - len(months),
                "missing_months": "|".join(map(str, sorted(full_month_set - set(months)))),
                "handling": "preserved_official_rows_no_imputation",
            }
        )

    maximum_possible_rows = len(weights) * horizon * 12
    checks = {
        "output_rows": len(audit),
        "maximum_possible_rows_if_every_person_year_has_12_records": maximum_possible_rows,
        "missing_records_relative_to_full_12_month_grid": maximum_possible_rows - len(audit),
        "weighted_persons": len(weights),
        "output_persons": len(output_keys),
        "maximum_month_records_per_person": horizon * 12,
        "persons_with_full_horizon_months": int((person_counts == horizon * 12).sum()),
        "persons_with_expected_file_years": int((person_year_counts == horizon).sum()),
        "person_years_with_12_months": int((person_month_counts == 12).sum()),
        "expected_person_years": len(weights) * horizon,
        "incomplete_person_years": len(incomplete_rows),
        "person_years_with_at_least_one_month": int((person_month_counts >= 1).sum()),
        "person_years_with_more_than_12_records": int((person_month_record_counts > 12).sum()),
        "duplicate_person_month_keys": int(audit["person_month_key"].duplicated().sum()),
        "persons_with_constant_final_weight": int((final_weight_counts == 1).sum()),
        "key_sets_equal": set(output_keys) == set(weight_keys),
        "file_year_values": "|".join(map(str, sorted(audit["file_year"].unique()))),
        "reference_year_values": "|".join(map(str, sorted(audit["reference_year"].unique()))),
        "reference_month_values": "|".join(map(str, sorted(audit["reference_month"].unique()))),
    }
    passed = (
        0 < checks["output_rows"] <= maximum_possible_rows
        and checks["output_persons"] == len(weights)
        and checks["persons_with_expected_file_years"] == len(weights)
        and checks["person_years_with_at_least_one_month"] == len(weights) * horizon
        and checks["person_years_with_more_than_12_records"] == 0
        and checks["duplicate_person_month_keys"] == 0
        and checks["persons_with_constant_final_weight"] == len(weights)
        and checks["key_sets_equal"]
        and sorted(audit["file_year"].unique().tolist()) == file_years
        and sorted(audit["reference_year"].unique().tolist()) == reference_years
        and sorted(audit["reference_month"].unique().tolist()) == list(range(1, 13))
    )
    if not passed:
        raise ValueError(f"Latest {horizon}y longitudinal panel failed source-faithfulness checks: {checks}")

    summary = {
        "horizon_years": horizon,
        "reference_start_year": 2025 - horizon,
        "reference_end_year": 2024,
        "file_year_start": 2026 - horizon,
        "file_year_end": 2025,
        "weight_variable": weight_name,
        "output_relative_path": str(output.relative_to(ROOT)),
        "output_bytes": output.stat().st_size,
        "output_columns": len(output_schema),
        **checks,
        "all_source_faithfulness_checks_pass": passed,
    }
    return summary, incomplete_rows


def main() -> None:
    if not PANEL.exists():
        raise FileNotFoundError(PANEL)
    product_rows, header_rows, latest_weights = convert_and_audit_weights()
    write_csv(PRODUCT_AUDIT, product_rows)
    write_csv(HEADER_AUDIT, header_rows)
    if set(latest_weights) != {2, 3, 4}:
        raise ValueError(f"Latest longitudinal weights are incomplete: {sorted(latest_weights)}")

    panel_rows: list[dict] = []
    incomplete_rows: list[dict] = []
    for horizon in (2, 3, 4):
        panel_row, panel_incomplete_rows = build_latest_panel(horizon, latest_weights[horizon])
        panel_rows.append(panel_row)
        incomplete_rows.extend(panel_incomplete_rows)
    write_csv(PANEL_AUDIT, panel_rows)
    write_csv(INCOMPLETE_PERSON_YEAR_AUDIT, incomplete_rows)
    print(
        f"COMPLETE products={len(product_rows)} header_rows={len(header_rows)} "
        f"latest_panels={len(panel_rows)} incomplete_person_years={len(incomplete_rows)}",
        flush=True,
    )


if __name__ == "__main__":
    main()
