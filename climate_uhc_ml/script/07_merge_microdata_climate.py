from __future__ import annotations

from pathlib import Path

import pandas as pd

from common import DATA_DIR, TEMP_DIR, append_log, ensure_dirs, write_csv


MICRODATA_CANDIDATES = [
    DATA_DIR / "harmonized_household.csv",
    DATA_DIR / "harmonized_household.parquet",
    DATA_DIR / "household_panel.csv",
    DATA_DIR / "household_panel.parquet",
    DATA_DIR / "climate_linkage_input.csv",
    DATA_DIR / "climate_linkage_input.parquet",
]

EXPOSURE_PATH = DATA_DIR / "climate_exposures_nasa_power.csv"
OUTPUT_PATH = DATA_DIR / "climate_linked_household.csv"
AUDIT_PATH = TEMP_DIR / "climate_merge_audit.csv"

AUDIT_COLUMNS = ["check", "status", "detail", "microdata_path", "climate_path", "rows_microdata", "rows_climate", "rows_output", "output_path"]

ID_COLUMNS = ["country", "survey_name", "wave", "hhid", "pid", "cluster_id", "latitude", "longitude", "interview_date"]
EXPOSURE_VALUE_COLUMNS = ["precip_total_mm", "precip_mean_mm_day", "temp_mean_c", "temp_max_c", "temp_min_c", "n_days"]


def find_microdata() -> Path | None:
    for path in MICRODATA_CANDIDATES:
        if path.exists():
            return path
    return None


def read_table(path: Path) -> pd.DataFrame:
    if path.suffix.lower() == ".parquet":
        return pd.read_parquet(path)
    return pd.read_csv(path)


def is_limited_harmonized_core(df: pd.DataFrame) -> bool:
    return (
        "data_use_limit" in df.columns
        and "outcome_status" in df.columns
        and df["data_use_limit"].astype(str).str.strip().eq("harmonized_household_core_only_not_for_final_outcome_or_climate_analysis").any()
        and df["outcome_status"].astype(str).str.strip().eq("candidate_inputs_not_final_outcomes").any()
    )


def is_limited_climate_exposure(df: pd.DataFrame) -> bool:
    return (
        "data_use_limit" in df.columns
        and df["data_use_limit"].astype(str).str.strip().eq("climate_exposure_admin2_centroid_only_not_for_final_climate_linkage").any()
    )


def normalize_keys(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    for col in ID_COLUMNS:
        if col not in out.columns:
            out[col] = ""
    out["latitude"] = pd.to_numeric(out["latitude"], errors="coerce").round(5)
    out["longitude"] = pd.to_numeric(out["longitude"], errors="coerce").round(5)
    if "interview_date" in out.columns:
        out["interview_date"] = pd.to_datetime(out["interview_date"], errors="coerce").dt.strftime("%Y-%m-%d")
    return out


def pivot_exposures(exposures: pd.DataFrame) -> pd.DataFrame:
    exposures = normalize_keys(exposures)
    required = set(ID_COLUMNS + ["window_months"])
    missing = [col for col in required if col not in exposures.columns]
    if missing:
        raise ValueError(f"climate exposure file missing columns: {', '.join(missing)}")
    available_values = [col for col in EXPOSURE_VALUE_COLUMNS if col in exposures.columns]
    if not available_values:
        raise ValueError("climate exposure file has no exposure value columns")
    pivot = exposures.pivot_table(
        index=ID_COLUMNS,
        columns="window_months",
        values=available_values,
        aggfunc="first",
    )
    pivot.columns = [f"{name}_{int(window)}m" for name, window in pivot.columns]
    return pivot.reset_index()


def write_audit(row: dict[str, object]) -> None:
    write_csv(AUDIT_PATH, [row], AUDIT_COLUMNS)


def main() -> None:
    ensure_dirs()
    micro_path = find_microdata()
    if micro_path is None:
        row = {
            "check": "climate_merge_inputs",
            "status": "blocked_no_harmonized_microdata",
            "detail": "No harmonized household/climate linkage input exists in data/.",
            "microdata_path": "",
            "climate_path": str(EXPOSURE_PATH.relative_to(TEMP_DIR.parent)) if EXPOSURE_PATH.exists() else "",
            "rows_microdata": 0,
            "rows_climate": 0,
            "rows_output": 0,
            "output_path": "",
        }
        write_audit(row)
        append_log(TEMP_DIR / "audit_log.md", "Climate merge blocked: no harmonized microdata input.")
        print("Climate merge blocked: no harmonized microdata input.")
        return
    if not EXPOSURE_PATH.exists():
        row = {
            "check": "climate_merge_inputs",
            "status": "blocked_no_climate_exposures",
            "detail": "No climate exposure file exists. Run script/06_extract_climate.py after harmonized geography/timing exists.",
            "microdata_path": str(micro_path.relative_to(TEMP_DIR.parent)),
            "climate_path": "",
            "rows_microdata": 0,
            "rows_climate": 0,
            "rows_output": 0,
            "output_path": "",
        }
        write_audit(row)
        append_log(TEMP_DIR / "audit_log.md", "Climate merge blocked: no climate exposure file.")
        print("Climate merge blocked: no climate exposure file.")
        return

    micro_raw = read_table(micro_path)
    climate = read_table(EXPOSURE_PATH)
    if is_limited_harmonized_core(micro_raw) or is_limited_climate_exposure(climate):
        if OUTPUT_PATH.exists():
            OUTPUT_PATH.unlink()
        row = {
            "check": "climate_merge_inputs",
            "status": "blocked_limited_inputs_not_final_climate_linkage",
            "detail": "Limited harmonized core and/or limited NASA admin2-centroid fallback exposures are not final climate-linkage inputs.",
            "microdata_path": str(micro_path.relative_to(TEMP_DIR.parent)),
            "climate_path": str(EXPOSURE_PATH.relative_to(TEMP_DIR.parent)),
            "rows_microdata": len(micro_raw),
            "rows_climate": len(climate),
            "rows_output": 0,
            "output_path": "",
        }
        write_audit(row)
        append_log(TEMP_DIR / "audit_log.md", "Climate merge blocked: limited inputs are not final climate-linkage inputs.")
        print("Climate merge blocked: limited inputs are not final climate-linkage inputs.")
        return

    micro = normalize_keys(micro_raw)
    climate_wide = pivot_exposures(climate)
    merged = micro.merge(climate_wide, on=ID_COLUMNS, how="left", validate="m:1")
    exposure_cols = [c for c in merged.columns if c.endswith(("1m", "3m", "6m", "12m"))]
    matched = int(merged[exposure_cols].notna().any(axis=1).sum()) if exposure_cols else 0
    merged.to_csv(OUTPUT_PATH, index=False, encoding="utf-8-sig")
    row = {
        "check": "climate_merge",
        "status": "complete" if matched > 0 else "complete_no_matches",
        "detail": f"Merged NASA POWER exposure summaries; rows with any exposure match={matched}.",
        "microdata_path": str(micro_path.relative_to(TEMP_DIR.parent)),
        "climate_path": str(EXPOSURE_PATH.relative_to(TEMP_DIR.parent)),
        "rows_microdata": len(micro),
        "rows_climate": len(climate),
        "rows_output": len(merged),
        "output_path": str(OUTPUT_PATH.relative_to(TEMP_DIR.parent)),
    }
    write_audit(row)
    append_log(TEMP_DIR / "audit_log.md", f"Climate merge wrote {len(merged)} rows with {matched} exposure matches.")
    print(f"Climate merge wrote {len(merged)} rows with {matched} exposure matches.")


if __name__ == "__main__":
    main()
