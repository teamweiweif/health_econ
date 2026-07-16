from __future__ import annotations

import csv
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
RAW_ROOT = ROOT / "temp" / "raw_downloads" / "census_sipp"
PANEL = ROOT / "data" / "analysis_ready" / "sipp_2018_2025_person_month_panel.parquet"
AUDIT_ROOT = ROOT / "data" / "sample_audits"
PATCH_PATH = (
    ROOT
    / "data"
    / "analysis_ready"
    / "sipp_2018_2023_health_insurance_official_usernote_correction_patch.parquet"
)

V11_ALIGNMENT = AUDIT_ROOT / "sipp_v11_correction_panel_alignment.csv"
HEALTH_ALIGNMENT = AUDIT_ROOT / "sipp_health_source_panel_alignment.csv"
HEALTH_COUNTS = AUDIT_ROOT / "sipp_health_insurance_usernote_correction_counts.csv"
COMPLETION_CHECKS = AUDIT_ROOT / "sipp_panel_alignment_and_health_correction_checks.csv"

KEYS = ["SSUID", "PNUM", "MONTHCODE"]
INCOME_VARS = [
    "TSSSAMT",
    "TPTOTINC",
    "TFTOTINC",
    "THTOTINC",
    "TFINCPOV",
    "THINCPOV",
    "TFCYINCPOV",
    "THCYINCPOV",
]
HEALTH_INPUTS = [
    "EMC_EMONTH",
    "ECRMTH",
    "EMCPART1",
    "EMCPART2",
    "EMCPART3",
    "EMCPART4",
    "EMCPART5",
    "EMD_BMONTH",
    "EMD_EMONTH",
    "EMDMTH",
    "EOT_EMONTH",
    "EOTHCOVTYPE",
    "EPR1MTH",
    "EPR2MTH",
    "EMILITYPE",
    "RPUBTYPE1",
    "RPUBTYPE2",
    "RPRIMTH",
    "RPUBMTH",
    "RHLTHMTH",
]
CORRECTED_VARS = [
    "ECRMTH",
    "EMDMTH",
    "RPUBTYPE1",
    "RPUBTYPE2",
    "RPRIMTH",
    "RPUBMTH",
    "RHLTHMTH",
]

MONTHLY_HEALTH_NOTE = (
    "https://www.census.gov/programs-surveys/sipp/tech-documentation/user-notes/"
    "2023-usernotes/2023-monthly-hi-variables-error.html"
)
MEDICAID_END_NOTE = (
    "https://www.census.gov/programs-surveys/sipp/tech-documentation/user-notes/"
    "2022-usernotes/2022-medicaid-variable-error.html"
)


def write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def raw_path(year: int) -> Path:
    return RAW_ROOT / str(year) / "primary" / f"pu{year}_csv.zip"


def raw_columns(year: int) -> list[str]:
    return sorted(set(KEYS + HEALTH_INPUTS + (INCOME_VARS if year <= 2021 else [])))


def normalize_keys(frame: pd.DataFrame) -> pd.DataFrame:
    frame["SSUID"] = frame["SSUID"].astype("string").str.strip()
    frame["PNUM"] = pd.to_numeric(frame["PNUM"], errors="raise").astype("int64")
    frame["MONTHCODE"] = pd.to_numeric(frame["MONTHCODE"], errors="raise").astype("int64")
    return frame


def read_raw_chunks(year: int, usecols: list[str] | None = None):
    usecols = usecols or raw_columns(year)
    usecols = sorted(set(usecols))
    dtypes = {name: "float64" for name in usecols if name != "SSUID"}
    dtypes["SSUID"] = "string"
    reader = pd.read_csv(
        raw_path(year),
        sep="|",
        compression="zip",
        usecols=usecols,
        dtype=dtypes,
        chunksize=75_000,
        low_memory=True,
    )
    for frame in reader:
        yield normalize_keys(frame)


def read_person_max_month(year: int) -> pd.Series:
    groups = []
    for frame in read_raw_chunks(year, KEYS):
        groups.append(frame.groupby(["SSUID", "PNUM"], sort=False)["MONTHCODE"].max())
    combined = pd.concat(groups)
    return combined.groupby(level=[0, 1], sort=False).max()


def read_panel_year(year: int, columns: list[str]) -> pd.DataFrame:
    frame = pd.read_parquet(
        PANEL,
        columns=sorted(set(["file_year"] + KEYS + columns)),
        filters=[("file_year", "=", year)],
    )
    frame["SSUID"] = frame["SSUID"].astype("string").str.strip()
    frame["PNUM"] = pd.to_numeric(frame["PNUM"], errors="raise").astype("int64")
    frame["MONTHCODE"] = pd.to_numeric(frame["MONTHCODE"], errors="raise").astype("int64")
    if frame.duplicated(KEYS).any():
        raise ValueError(f"Panel {year} has duplicate person-month keys")
    return frame.drop(columns="file_year")


def float32_equal(left: pd.Series, right: pd.Series) -> np.ndarray:
    left_values = pd.to_numeric(left, errors="coerce").to_numpy(dtype="float32")
    right_values = pd.to_numeric(right, errors="coerce").to_numpy(dtype="float32")
    return (left_values == right_values) | (np.isnan(left_values) & np.isnan(right_values))


def initialize_alignment(
    year: int, variables: list[str], scope: str, panel_rows: int
) -> dict[str, dict]:
    return {
        variable: {
            "alignment_scope": scope,
            "file_year": year,
            "variable": variable,
            "raw_rows": 0,
            "panel_rows": panel_rows,
            "raw_only_keys": 0,
            "panel_only_keys": 0,
            "value_mismatches_after_float32_cast": 0,
            "max_absolute_difference_before_float32_cast": 0.0,
            "all_keys_and_values_match": False,
        }
        for variable in variables
    }


def update_alignment(
    accumulator: dict[str, dict], raw: pd.DataFrame, panel_indexed: pd.DataFrame
) -> None:
    raw_index = pd.MultiIndex.from_frame(raw[KEYS])
    if raw_index.duplicated().any():
        raise ValueError("Raw chunk has duplicate person-month keys")
    found = raw_index.isin(panel_indexed.index)
    aligned = panel_indexed.reindex(raw_index)
    for variable, record in accumulator.items():
        equal = float32_equal(raw[variable], aligned[variable])
        mismatch = found & ~equal
        raw_values = pd.to_numeric(raw.loc[mismatch, variable], errors="coerce")
        panel_values = pd.to_numeric(aligned.loc[mismatch, variable], errors="coerce")
        max_abs = (raw_values.to_numpy() - panel_values.to_numpy()).__abs__().max() if mismatch.any() else 0.0
        record["raw_rows"] += len(raw)
        record["raw_only_keys"] += int((~found).sum())
        record["value_mismatches_after_float32_cast"] += int(mismatch.sum())
        record["max_absolute_difference_before_float32_cast"] = max(
            float(record["max_absolute_difference_before_float32_cast"]), float(max_abs)
        )


def finalize_alignment(accumulator: dict[str, dict]) -> list[dict]:
    rows = []
    for record in accumulator.values():
        matched_raw = int(record["raw_rows"]) - int(record["raw_only_keys"])
        record["panel_only_keys"] = max(0, int(record["panel_rows"]) - matched_raw)
        record["all_keys_and_values_match"] = bool(
            int(record["raw_rows"]) == int(record["panel_rows"])
            and int(record["raw_only_keys"]) == 0
            and int(record["panel_only_keys"]) == 0
            and int(record["value_mismatches_after_float32_cast"]) == 0
        )
        rows.append(record)
    return rows


def corrected_copy(frame: pd.DataFrame, variable: str) -> pd.Series:
    return pd.to_numeric(frame[variable], errors="coerce").copy()


def values_differ(original: pd.Series, corrected: pd.Series) -> pd.Series:
    original_num = pd.to_numeric(original, errors="coerce")
    corrected_num = pd.to_numeric(corrected, errors="coerce")
    return ~((original_num.eq(corrected_num)) | (original_num.isna() & corrected_num.isna()))


def apply_official_health_corrections(
    year: int, frame: pd.DataFrame, max_month_values: np.ndarray
) -> tuple[pd.DataFrame, dict[str, pd.Series], dict[str, int]]:
    corrected: dict[str, pd.Series] = {
        variable: corrected_copy(frame, variable) for variable in CORRECTED_VARS
    }

    emd_end = corrected_copy(frame, "EMD_EMONTH")
    bad_medicaid_end = frame["EMD_BMONTH"].gt(frame["EMD_EMONTH"])
    emd_end.loc[bad_medicaid_end] = max_month_values[bad_medicaid_end.to_numpy()]

    medicare_expired = frame["EMC_EMONTH"].lt(frame["MONTHCODE"])
    medicaid_expired = emd_end.lt(frame["MONTHCODE"])
    other_expired = frame["EOT_EMONTH"].lt(frame["MONTHCODE"])

    corrected["ECRMTH"].loc[medicare_expired] = 2
    corrected["EMDMTH"].loc[medicaid_expired] = 2
    corrected["RPUBTYPE1"].loc[medicare_expired] = 2
    corrected["RPUBTYPE2"].loc[
        medicaid_expired | (other_expired & frame["EOTHCOVTYPE"].eq(1))
    ] = 2

    medicare_parts = {
        name: corrected_copy(frame, name) for name in [f"EMCPART{i}" for i in range(1, 6)]
    }
    for series in medicare_parts.values():
        series.loc[medicare_expired] = np.nan
    other_type = corrected_copy(frame, "EOTHCOVTYPE")
    other_type.loc[other_expired] = np.nan

    corrected["RPRIMTH"] = pd.Series(
        np.where(
            frame["EPR1MTH"].eq(1)
            | frame["EPR2MTH"].eq(1)
            | medicare_parts["EMCPART3"].eq(1)
            | frame["EMILITYPE"].eq(1),
            1,
            2,
        ),
        index=frame.index,
        dtype="float64",
    )
    corrected["RPUBMTH"] = pd.Series(
        np.where(
            medicare_parts["EMCPART1"].eq(1)
            | medicare_parts["EMCPART2"].eq(1)
            | medicare_parts["EMCPART4"].eq(1)
            | corrected["EMDMTH"].eq(1)
            | frame["EMILITYPE"].isin([2, 3])
            | other_type.eq(1),
            1,
            2,
        ),
        index=frame.index,
        dtype="float64",
    )
    corrected["RHLTHMTH"] = pd.Series(
        np.where(corrected["RPRIMTH"].eq(1) | corrected["RPUBMTH"].eq(1), 1, 2),
        index=frame.index,
        dtype="float64",
    )

    difference_flags = {
        variable: values_differ(frame[variable], corrected[variable])
        for variable in CORRECTED_VARS
    }
    any_difference = pd.concat(difference_flags, axis=1).any(axis=1)
    patch = frame.loc[any_difference, KEYS].copy()
    patch.insert(0, "file_year", year)
    patch["person_month_key"] = (
        patch["file_year"].astype(str)
        + "-"
        + patch["SSUID"].astype(str)
        + "-"
        + patch["PNUM"].astype(str)
        + "-"
        + patch["MONTHCODE"].astype(str)
    )
    patch["medicaid_end_month_order_error_flag"] = bad_medicaid_end.loc[any_difference].to_numpy()
    patch["medicare_spell_expired_flag"] = medicare_expired.loc[any_difference].to_numpy()
    patch["medicaid_spell_expired_flag"] = medicaid_expired.loc[any_difference].to_numpy()
    patch["other_coverage_spell_expired_flag"] = other_expired.loc[any_difference].to_numpy()
    for variable in CORRECTED_VARS:
        patch[f"{variable}_ORIGINAL"] = frame.loc[any_difference, variable].to_numpy()
        patch[f"{variable}_CENSUS_NOTE_CORRECTED"] = corrected[variable].loc[any_difference].to_numpy()

    diagnostics = {
        "medicaid_end_order_error_rows": int(bad_medicaid_end.sum()),
        "medicare_expired_rows": int(medicare_expired.sum()),
        "medicaid_expired_rows": int(medicaid_expired.sum()),
        "other_coverage_expired_rows": int(other_expired.sum()),
    }
    return patch, difference_flags, diagnostics


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
    if not PANEL.exists():
        raise FileNotFoundError(PANEL)

    income_alignment: list[dict] = []
    health_alignment: list[dict] = []
    health_counts: list[dict] = []
    patches: list[pd.DataFrame] = []

    for year in range(2018, 2024):
        print(f"READ RAW {year}: person-month maxima pass", flush=True)
        max_month_by_person = read_person_max_month(year)
        panel_columns = CORRECTED_VARS + (INCOME_VARS if year <= 2021 else [])
        panel = read_panel_year(year, panel_columns)
        panel_indexed = panel.set_index(KEYS)
        health_accumulator = initialize_alignment(
            year, CORRECTED_VARS, "health_source_fields", len(panel)
        )
        income_accumulator = (
            initialize_alignment(
                year, INCOME_VARS, "v1.1_corrected_income_fields", len(panel)
            )
            if year <= 2021
            else None
        )
        yearly_patches: list[pd.DataFrame] = []
        change_rows = {variable: 0 for variable in CORRECTED_VARS}
        change_persons = {variable: set() for variable in CORRECTED_VARS}
        diagnostic_totals = {
            "medicaid_end_order_error_rows": 0,
            "medicare_expired_rows": 0,
            "medicaid_expired_rows": 0,
            "other_coverage_expired_rows": 0,
        }
        source_rows = 0

        print(f"READ RAW {year}: alignment/correction pass", flush=True)
        for chunk_number, raw in enumerate(read_raw_chunks(year), start=1):
            source_rows += len(raw)
            update_alignment(health_accumulator, raw, panel_indexed)
            if income_accumulator is not None:
                update_alignment(income_accumulator, raw, panel_indexed)

            person_index = pd.MultiIndex.from_frame(raw[["SSUID", "PNUM"]])
            chunk_max_month = max_month_by_person.reindex(person_index).to_numpy()
            if pd.isna(chunk_max_month).any():
                raise ValueError(f"Missing person maximum month in {year} chunk {chunk_number}")
            patch, difference_flags, diagnostics = apply_official_health_corrections(
                year, raw, chunk_max_month
            )
            if len(patch):
                yearly_patches.append(patch)
            for variable, changed in difference_flags.items():
                change_rows[variable] += int(changed.sum())
                change_persons[variable].update(
                    zip(
                        raw.loc[changed, "SSUID"].astype(str),
                        raw.loc[changed, "PNUM"].astype(int),
                    )
                )
            for key, value in diagnostics.items():
                diagnostic_totals[key] += int(value)
            print(
                f"  {year} chunk={chunk_number} rows={source_rows:,} "
                f"patch_rows={sum(len(item) for item in yearly_patches):,}",
                flush=True,
            )

        health_alignment.extend(finalize_alignment(health_accumulator))
        if year <= 2021:
            assert income_accumulator is not None
            income_alignment.extend(finalize_alignment(income_accumulator))
        year_patch = pd.concat(yearly_patches, ignore_index=True) if yearly_patches else pd.DataFrame()
        if len(year_patch):
            patches.append(year_patch)
        for variable in CORRECTED_VARS:
            health_counts.append(
                {
                    "file_year": year,
                    "reference_year": year - 1,
                    "variable": variable,
                    "source_rows": source_rows,
                    "changed_person_months": change_rows[variable],
                    "changed_persons": len(change_persons[variable]),
                    "change_rate": change_rows[variable] / source_rows,
                    **diagnostic_totals,
                    "aggregate_private_recode_interpretation": (
                        "Uses EPR1MTH/EPR2MTH monthly plan indicators. The official web table "
                        "prints EHEMPLY{1:2}=1, which conflicts with the data dictionary, the "
                        "observed raw recode, and the note's stated affected-record scale."
                    ),
                    "official_monthly_health_note": MONTHLY_HEALTH_NOTE,
                    "official_medicaid_end_note": MEDICAID_END_NOTE,
                }
            )
        print(
            f"CORRECT {year}: patch_rows={len(year_patch):,} "
            f"rhlthmth_changes={change_rows['RHLTHMTH']:,}",
            flush=True,
        )

    write_csv(V11_ALIGNMENT, income_alignment)
    write_csv(HEALTH_ALIGNMENT, health_alignment)
    write_csv(HEALTH_COUNTS, health_counts)
    patch_all = pd.concat(patches, ignore_index=True)
    if patch_all.duplicated(["file_year"] + KEYS).any():
        raise ValueError("Correction patch has duplicate person-month keys")
    PATCH_PATH.parent.mkdir(parents=True, exist_ok=True)
    patch_all.to_parquet(PATCH_PATH, index=False, compression="snappy")

    checks: list[dict] = []
    add_check(
        checks,
        "v11_panel_alignment",
        "All 2018-2021 panel income/poverty fields exactly reproduce current v1.1 raw values after the panel's float32 storage cast",
        len(income_alignment) == 32 and all(row["all_keys_and_values_match"] for row in income_alignment),
        f"passed={sum(row['all_keys_and_values_match'] for row in income_alignment)}/{len(income_alignment)}",
    )
    add_check(
        checks,
        "health_source_panel_alignment",
        "All original health fields used by the correction patch match the current selected panel",
        len(health_alignment) == 42 and all(row["all_keys_and_values_match"] for row in health_alignment),
        f"passed={sum(row['all_keys_and_values_match'] for row in health_alignment)}/{len(health_alignment)}",
    )
    add_check(
        checks,
        "correction_patch_unique",
        "The official-user-note correction patch has unique file-year/person-month keys",
        not patch_all.duplicated(["file_year"] + KEYS).any(),
        f"patch_rows={len(patch_all)}; patch_persons={patch_all[['SSUID','PNUM']].drop_duplicates().shape[0]}",
    )
    add_check(
        checks,
        "official_scope",
        "Corrections are applied only to affected 2018-2023 file years; original official values remain available",
        set(patch_all["file_year"].unique()).issubset(set(range(2018, 2024)))
        and all(f"{variable}_ORIGINAL" in patch_all for variable in CORRECTED_VARS),
        f"file_years={sorted(patch_all['file_year'].unique().tolist())}",
    )
    write_csv(COMPLETION_CHECKS, checks)
    failed = [row for row in checks if not row["passed"]]
    print(
        f"ALIGNMENT/CORRECTION COMPLETE checks={len(checks)-len(failed)}/{len(checks)} "
        f"patch_rows={len(patch_all):,}",
        flush=True,
    )
    if failed:
        raise SystemExit(f"Failed checks: {[row['check_id'] for row in failed]}")


if __name__ == "__main__":
    main()
