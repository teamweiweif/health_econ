from __future__ import annotations

import os
import tempfile
from pathlib import Path, PurePosixPath
from typing import Any
from zipfile import ZipFile

import pandas as pd
import pyreadstat

from common import REPORT_DIR, RESULT_DIR, TEMP_DIR, append_log, ensure_dirs, write_csv


IDNO = "MWI_2004_IHS-II_v01_M"
COUNTRY = "Malawi"
WAVE = "2004-2005"
RAW_DIR = TEMP_DIR / "raw_downloads" / IDNO
ZIP_PATH = RAW_DIR / "MWI_2004_IHS-II_v01_M_Stata8.zip"

POLICY_PATH = RESULT_DIR / "mwi2004_timing_geography_linkage_policy.csv"
SUMMARY_PATH = RESULT_DIR / "mwi2004_timing_geography_linkage_policy_summary.csv"
REPORT_PATH = REPORT_DIR / "mwi2004_timing_geography_linkage_policy.md"
HANDOFF_PATH = RAW_DIR / "_MWI2004_TIMING_GEOGRAPHY_LINKAGE_POLICY.md"

POLICY_COLUMNS = [
    "country",
    "wave",
    "idno",
    "policy_component",
    "accepted_rule",
    "raw_variables",
    "aggregate_count",
    "raw_label_evidence",
    "numeric_evidence",
    "acceptance_status",
    "remaining_blocker",
    "data_write_gate_effect",
]
SUMMARY_COLUMNS = ["metric", "value", "interpretation"]


def clean(value: Any) -> str:
    if value is None:
        return ""
    return " ".join(str(value).split())


def member_name(zip_path: Path, basename: str) -> str:
    with ZipFile(zip_path) as zf:
        for name in zf.namelist():
            if PurePosixPath(name).name.lower() == basename.lower():
                return name
    raise FileNotFoundError(f"{basename} not found in {zip_path}")


def read_member(zip_path: Path, basename: str, columns: list[str]) -> tuple[pd.DataFrame, Any]:
    member = member_name(zip_path, basename)
    with ZipFile(zip_path) as zf:
        payload = zf.read(member)
    fd, raw_name = tempfile.mkstemp(suffix=PurePosixPath(member).suffix or ".dta")
    raw_path = Path(raw_name)
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(payload)
        _, meta = pyreadstat.read_dta(str(raw_path), metadataonly=True)
        available = set(getattr(meta, "column_names", []) or [])
        usecols = [column for column in columns if column in available]
        return pyreadstat.read_dta(str(raw_path), apply_value_formats=False, usecols=usecols)
    finally:
        raw_path.unlink(missing_ok=True)


def label(meta: Any, variable: str) -> str:
    names = getattr(meta, "column_names", []) or []
    labels = getattr(meta, "column_labels", []) or []
    return clean(dict(zip(names, labels)).get(variable, ""))


def date_bounds(series: pd.Series) -> tuple[pd.Series, str, str]:
    numeric = pd.to_numeric(series, errors="coerce")
    converted = pd.to_datetime(numeric, unit="D", origin="1960-01-01", errors="coerce")
    valid = converted.dropna()
    if valid.empty:
        return converted, "", ""
    return converted, valid.min().date().isoformat(), valid.max().date().isoformat()


def key_set(df: pd.DataFrame, keys: list[str]) -> set[tuple[Any, ...]]:
    key_df = df[keys].dropna().drop_duplicates()
    return {tuple(row) for row in key_df.itertuples(index=False, name=None)}


def policy_row(
    component: str,
    rule: str,
    variables: str,
    count: int | str,
    raw_label: str,
    numeric: str,
    status: str,
    blocker: str,
) -> dict[str, str]:
    return {
        "country": COUNTRY,
        "wave": WAVE,
        "idno": IDNO,
        "policy_component": component,
        "accepted_rule": rule,
        "raw_variables": variables,
        "aggregate_count": str(count),
        "raw_label_evidence": raw_label,
        "numeric_evidence": numeric,
        "acceptance_status": status,
        "remaining_blocker": blocker,
        "data_write_gate_effect": "does_not_open_data_gate",
    }


def markdown_table(rows: list[dict[str, str]], columns: list[str], limit: int = 25) -> str:
    if not rows:
        return "_No rows._"
    lines = ["| " + " | ".join(columns) + " |", "| " + " | ".join("---" for _ in columns) + " |"]
    for row in rows[:limit]:
        lines.append("| " + " | ".join(clean(row.get(column)).replace("|", "/") for column in columns) + " |")
    if len(rows) > limit:
        lines.append("| " + " | ".join("..." for _ in columns) + " |")
    return "\n".join(lines)


def build_outputs() -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    if not ZIP_PATH.exists():
        raise FileNotFoundError(f"Missing raw package: {ZIP_PATH}")

    household, household_meta = read_member(
        ZIP_PATH,
        "ihs2_household.dta",
        ["case_id", "hhwght", "strata", "region", "dist", "ta", "ea", "V51", "idate", "type"],
    )
    ea_data, ea_meta = read_member(ZIP_PATH, "ihs2_ea_data.dta", ["dist", "ta", "ea", "access", "access2", "lz_code"])
    health, health_meta = read_member(ZIP_PATH, "sec_d.dta", ["case_id", "region", "dist", "ta", "ea", "psu", "type"])

    converted_dates, min_date, max_date = date_bounds(household["idate"])
    months = converted_dates.dt.to_period("M").astype(str)
    valid_months = months[converted_dates.notna()]
    month_counts = valid_months.value_counts().sort_index()
    month_list = ";".join(f"{month}:{count}" for month, count in month_counts.items())

    household_ea = key_set(household, ["dist", "ta", "ea"])
    ea_keys = key_set(ea_data, ["dist", "ta", "ea"])
    health_households = set(health["case_id"].dropna().drop_duplicates())
    household_case_ids = set(household["case_id"].dropna().drop_duplicates())
    health_ea = key_set(health, ["dist", "ta", "ea"])
    household_psu = set(household["V51"].dropna().drop_duplicates())
    health_psu = set(health["psu"].dropna().drop_duplicates())

    household_ea_matched = len(household_ea & ea_keys)
    household_ea_unmatched = len(household_ea - ea_keys)
    health_household_unmatched = len(health_households - household_case_ids)
    health_ea_unmatched = len(health_ea - household_ea)
    psu_overlap = len(health_psu & household_psu)

    policy_rows = [
        policy_row(
            "interview_date_anchor",
            "Use ihs2_household.idate as the household interview date, converted from Stata days since 1960-01-01.",
            "idate",
            int(converted_dates.notna().sum()),
            f"idate={label(household_meta, 'idate')}",
            f"nonmissing={int(converted_dates.notna().sum())}/{len(household)}; min={min_date}; max={max_date}; distinct_months={month_counts.shape[0]}.",
            "raw_value_verified_for_climate_timing",
            "Climate exposure windows are not extracted yet; this only accepts the raw timing anchor.",
        ),
        policy_row(
            "interview_month_window_policy",
            "Anchor climate exposure windows to interview month; candidate windows are 1, 3, 6, and 12 complete months before interview month.",
            "idate",
            int(month_counts.shape[0]),
            "Official/public metadata records 2004-03 through 2005-03 fieldwork; raw idate confirms month coverage.",
            f"month_counts={month_list}",
            "raw_value_verified_for_climate_timing",
            "Exact climate values still require CHIRPS/ERA5 extraction after geography route acceptance.",
        ),
        policy_row(
            "household_admin_ea_geography",
            "Use dist+ta+ea as the household EA/admin geography key; use V51 as the 8-digit EA/PSU identifier.",
            "dist;ta;ea;V51;region;type",
            len(household_ea),
            f"dist={label(household_meta, 'dist')}; ta={label(household_meta, 'ta')}; ea={label(household_meta, 'ea')}; V51={label(household_meta, 'V51')}; type={label(household_meta, 'type')}.",
            f"households={len(household)}; distinct dist+ta+ea={len(household_ea)}; distinct V51={len(household_psu)}; household_ea_unmatched_to_ea_file={household_ea_unmatched}.",
            "raw_value_verified_for_admin_ea_geography",
            "No household or cluster coordinates are accepted; boundary/crosswalk source remains required for climate extraction.",
        ),
        policy_row(
            "ea_auxiliary_join",
            "Join household dist+ta+ea to ihs2_ea_data for auxiliary EA attributes only; do not treat access fields as coordinates.",
            "dist;ta;ea;access;access2;lz_code",
            household_ea_matched,
            f"access={label(ea_meta, 'access')}; access2={label(ea_meta, 'access2')}; lz_code={label(ea_meta, 'lz_code')}.",
            f"ea_file_rows={len(ea_data)}; ea_keys={len(ea_keys)}; matched_household_ea={household_ea_matched}/{len(household_ea)}.",
            "raw_value_verified_for_admin_ea_geography",
            "EA auxiliary data improve geography context but do not solve historical boundary geometry.",
        ),
        policy_row(
            "person_module_geography_inheritance",
            "For person-level health/access work, inherit household geography through case_id after confirming health households join to ihs2_household.",
            "case_id;dist;ta;ea;psu",
            len(health_households),
            f"sec_d dist={label(health_meta, 'dist')}; sec_d psu={label(health_meta, 'psu')}.",
            f"health households={len(health_households)}; health_household_unmatched={health_household_unmatched}; health_ea_unmatched_to_household_ea={health_ea_unmatched}; health_psu_overlap_with_V51={psu_overlap}/{len(health_psu)}.",
            "raw_value_verified_for_admin_ea_geography",
            "Person-key exceptions remain a separate health/access blocker; geography inheritance does not resolve person-level construct validity.",
        ),
        policy_row(
            "chirps_era5_route_status",
            "Do not mark a CHIRPS or ERA5 route accepted yet; use admin/EA geography only after a boundary/crosswalk and aggregation method are documented.",
            "dist;ta;ea;V51;psu;idate",
            0,
            "Raw timing and EA/admin fields are verified; climate-source extraction is not performed in this artifact.",
            "accepted_chirps_era5_route=0; no GPS coordinate field accepted.",
            "blocked_boundary_crosswalk_and_exposure_aggregation_required",
            "Need historical or defensible current boundary/crosswalk for district/TA/EA, plus CHIRPS/ERA5 aggregation choice.",
        ),
    ]

    summary_rows = [
        {"metric": "country_wave", "value": IDNO, "interpretation": "Country-wave covered by this timing/geography linkage policy."},
        {"metric": "household_rows", "value": str(len(household)), "interpretation": "Household rows with raw timing/geography fields."},
        {"metric": "idate_nonmissing_rows", "value": str(int(converted_dates.notna().sum())), "interpretation": "Rows with convertible interview date."},
        {"metric": "interview_date_min", "value": min_date, "interpretation": "Earliest converted household interview date."},
        {"metric": "interview_date_max", "value": max_date, "interpretation": "Latest converted household interview date."},
        {"metric": "interview_month_count", "value": str(int(month_counts.shape[0])), "interpretation": "Distinct interview months."},
        {"metric": "interview_month_distribution", "value": month_list, "interpretation": "Household counts by interview month."},
        {"metric": "household_ea_distinct", "value": str(len(household_ea)), "interpretation": "Distinct household dist+ta+ea keys."},
        {"metric": "household_ea_matched_to_ea_file", "value": f"{household_ea_matched}/{len(household_ea)}", "interpretation": "Household EA/admin keys matched to ihs2_ea_data."},
        {"metric": "household_psu_distinct", "value": str(len(household_psu)), "interpretation": "Distinct household V51 EA/PSU identifiers."},
        {"metric": "health_households_unmatched_to_household", "value": str(health_household_unmatched), "interpretation": "Health-module households absent from household file."},
        {"metric": "health_ea_unmatched_to_household_ea", "value": str(health_ea_unmatched), "interpretation": "Health-module dist+ta+ea keys absent from household EA set."},
        {"metric": "survey_timing_final_verified", "value": "1", "interpretation": "Raw survey timing is accepted for climate-window anchoring."},
        {"metric": "climate_geography_final_verified", "value": "1", "interpretation": "Raw admin/EA geography is accepted as the candidate climate-linkage geography."},
        {"metric": "timing_geography_ready_for_climate", "value": "1", "interpretation": "Raw timing and admin/EA geography are ready for climate-route review."},
        {"metric": "gps_coordinate_ready", "value": "0", "interpretation": "No GPS coordinate field is accepted."},
        {"metric": "accepted_chirps_era5_route", "value": "0", "interpretation": "A CHIRPS/ERA5 route is still blocked by boundary/crosswalk and aggregation policy."},
        {"metric": "timing_geography_policy_status", "value": "raw_timing_admin_ea_geography_verified_climate_route_blocked", "interpretation": "Timing/geography raw values accepted; climate route remains blocked."},
        {"metric": "data_write_gate_status", "value": "closed", "interpretation": "No promoted dataset may be written from this policy artifact alone."},
    ]
    return policy_rows, summary_rows


def write_report(policy_rows: list[dict[str, str]], summary_rows: list[dict[str, str]]) -> None:
    report = f"""# Malawi 2004 Timing/Geography Linkage Policy

Dataset: `{IDNO}` - {COUNTRY} {WAVE}

This artifact accepts the raw interview timing and admin/EA geography fields
needed to review a climate-linkage route. It does not extract climate values,
does not accept CHIRPS/ERA5 linkage, and does not write promoted data.

## Summary

{markdown_table(summary_rows, ["metric", "value", "interpretation"], 30)}

## Policy Rows

{markdown_table(policy_rows, ["policy_component", "accepted_rule", "raw_variables", "aggregate_count", "acceptance_status", "remaining_blocker"], 20)}

## Accepted Raw Inputs

- Timing: `idate` converted as Stata days since 1960-01-01 and anchored at
  interview month.
- Geography: household `dist + ta + ea` and `V51` as the EA/admin geography;
  health-module rows inherit household geography through `case_id`.
- EA auxiliary data: `ihs2_ea_data.dta` joins completely to household
  `dist + ta + ea`, but `access`, `access2`, and `lz_code` are context fields,
  not coordinates.

## Still Blocked

- No GPS coordinate field is accepted.
- CHIRPS/ERA5 linkage remains blocked until a defensible boundary/crosswalk and
  exposure aggregation level are documented.
- Person-key exceptions, access outcome policy, missing/skip/unit/recall policy,
  and data writes remain blocked.
"""
    REPORT_PATH.write_text(report, encoding="utf-8")
    HANDOFF_PATH.write_text(report, encoding="utf-8")


def main() -> None:
    ensure_dirs()
    policy_rows, summary_rows = build_outputs()
    write_csv(POLICY_PATH, policy_rows, POLICY_COLUMNS)
    write_csv(SUMMARY_PATH, summary_rows, SUMMARY_COLUMNS)
    write_report(policy_rows, summary_rows)
    append_log(TEMP_DIR / "audit_log.md", f"Built Malawi 2004 timing/geography linkage policy for {IDNO}.")


if __name__ == "__main__":
    main()
