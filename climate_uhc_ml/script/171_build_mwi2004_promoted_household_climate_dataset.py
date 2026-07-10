from __future__ import annotations

import csv
import os
import tempfile
from pathlib import Path, PurePosixPath
from typing import Any
from zipfile import ZipFile

import pandas as pd
import pyreadstat

from common import DATA_DIR, REPORT_DIR, RESULT_DIR, TEMP_DIR, append_log, ensure_dirs, sha256_file, write_csv


IDNO = "MWI_2004_IHS-II_v01_M"
COUNTRY = "Malawi"
WAVE = "2004-2005"
RAW_DIR = TEMP_DIR / "raw_downloads" / IDNO
ZIP_PATH = RAW_DIR / "MWI_2004_IHS-II_v01_M_Stata8.zip"

FINANCIAL_SUMMARY_PATH = RESULT_DIR / "mwi2004_financial_protection_construction_policy_summary.csv"
ACCESS_SUMMARY_PATH = RESULT_DIR / "mwi2004_access_person_key_resolution_policy_summary.csv"
MISSING_UNITS_SUMMARY_PATH = RESULT_DIR / "mwi2004_missing_units_recall_skip_policy_summary.csv"
CLIMATE_SUMMARY_PATH = RESULT_DIR / "mwi2004_chirps_admin2_extraction_summary.csv"
CROSSWALK_PATH = RESULT_DIR / "mwi2004_chirps_admin2_crosswalk.csv"
LAG_WINDOW_PATH = RESULT_DIR / "mwi2004_chirps_admin2_lag_window_exposure.csv"

DATA_PATH = DATA_DIR / "mwi2004_household_climate_analysis.csv"
SUMMARY_PATH = RESULT_DIR / "mwi2004_promoted_household_climate_dataset_summary.csv"
DICTIONARY_PATH = RESULT_DIR / "mwi2004_promoted_household_climate_dataset_dictionary.csv"
VALIDATION_PATH = RESULT_DIR / "mwi2004_promoted_household_climate_dataset_validation.csv"
REPORT_PATH = REPORT_DIR / "mwi2004_promoted_household_climate_dataset.md"
HANDOFF_PATH = RAW_DIR / "_MWI2004_PROMOTED_HOUSEHOLD_CLIMATE_DATASET.md"

SUMMARY_COLUMNS = ["metric", "value", "interpretation"]
DICTIONARY_COLUMNS = ["column_name", "storage_type", "source", "definition", "analysis_note"]
VALIDATION_COLUMNS = ["validation_component", "status", "evidence", "required_action"]

LAGS = [1, 3, 6, 12]

FINAL_COLUMNS = [
    "country",
    "wave",
    "idno",
    "case_id",
    "household_weight",
    "strata",
    "psu",
    "raw_dist_code",
    "raw_dist_label",
    "adm2_name",
    "ta",
    "ea",
    "interview_date",
    "interview_month",
    "total_consumption_rexpagg",
    "oop_health_rexp_cat06",
    "oop_health_share_total",
    "che10_total_budget",
    "che25_total_budget",
    "sdg382_ready",
    "health_person_rows_matched",
    "acute_need_persons",
    "cost_barrier_forgone_care_persons",
    "household_any_acute_need",
    "household_any_cost_barrier_forgone_care",
    "uhc_failure_che10_or_cost_barrier",
    "uhc_failure_che25_or_cost_barrier",
    "both_che10_and_cost_barrier",
    "both_che25_and_cost_barrier",
    "chirps_precip_total_1m_mm",
    "chirps_precip_mean_1m_mm",
    "chirps_precip_total_3m_mm",
    "chirps_precip_mean_3m_mm",
    "chirps_precip_total_6m_mm",
    "chirps_precip_mean_6m_mm",
    "chirps_precip_total_12m_mm",
    "chirps_precip_mean_12m_mm",
]


def clean(value: Any) -> str:
    if value is None:
        return ""
    return " ".join(str(value).split())


def fmt(value: Any) -> str:
    if value is None or pd.isna(value):
        return ""
    try:
        return f"{float(value):.6g}"
    except (TypeError, ValueError):
        return clean(value)


def id_text(value: Any) -> str:
    if value is None or pd.isna(value):
        return ""
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return clean(value)


def code_text(value: Any) -> str:
    if value is None or pd.isna(value):
        return ""
    try:
        number = float(value)
        if number.is_integer():
            return str(int(number))
    except (TypeError, ValueError):
        pass
    return clean(value)


def read_csv_dicts(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def summary_value(rows: list[dict[str, str]], metric: str, default: str = "") -> str:
    for row in rows:
        if clean(row.get("metric")) == metric:
            return clean(row.get("value")) or default
    return default


def member_name(zip_path: Path, basename: str) -> str:
    with ZipFile(zip_path) as zf:
        for name in zf.namelist():
            if PurePosixPath(name).name.lower() == basename.lower():
                return name
    raise FileNotFoundError(f"{basename} not found in {zip_path}")


def read_member(zip_path: Path, basename: str, columns: list[str], apply_value_formats: bool = False) -> pd.DataFrame:
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
        df, _ = pyreadstat.read_dta(str(raw_path), apply_value_formats=apply_value_formats, usecols=usecols)
        return df
    finally:
        raw_path.unlink(missing_ok=True)


def load_gate_flags() -> dict[str, str]:
    financial = read_csv_dicts(FINANCIAL_SUMMARY_PATH)
    access = read_csv_dicts(ACCESS_SUMMARY_PATH)
    missing_units = read_csv_dicts(MISSING_UNITS_SUMMARY_PATH)
    climate = read_csv_dicts(CLIMATE_SUMMARY_PATH)
    return {
        "financial_che10_che25_ready": "1" if summary_value(financial, "che10_che25_financial_inputs_ready", "0") == "1" else "0",
        "access_cost_barrier_ready": "1" if summary_value(access, "access_forgone_care_inputs_ready", "0") == "1" else "0",
        "missing_units_recall_skip_ready": "1" if summary_value(missing_units, "missing_units_recall_skip_policy_final_verified", "0") == "1" else "0",
        "climate_chirps_admin2_ready": "1" if summary_value(climate, "accepted_chirps_era5_route", "0") == "1" else "0",
        "financial_rows_expected": summary_value(financial, "household_financial_rows", "0"),
        "che10_rows_expected": summary_value(financial, "che10_candidate_rows", "0"),
        "che25_rows_expected": summary_value(financial, "che25_candidate_rows", "0"),
        "access_person_rows_expected": summary_value(access, "analytic_roster_matched_health_rows", "0"),
        "acute_need_persons_expected": summary_value(access, "acute_need_denominator_rows", "0"),
        "cost_barrier_persons_expected": summary_value(access, "cost_barrier_forgone_care_rows", "0"),
        "climate_lag_rows_expected": summary_value(climate, "lag_window_exposure_rows", "0"),
    }


def build_financial_households() -> pd.DataFrame:
    household = read_member(
        ZIP_PATH,
        "ihs2_household.dta",
        ["case_id", "hhwght", "strata", "dist", "ta", "ea", "V51", "idate"],
    )
    household_labels = read_member(
        ZIP_PATH,
        "ihs2_household.dta",
        ["case_id", "dist"],
        apply_value_formats=True,
    ).rename(columns={"dist": "raw_dist_label"})
    pov = read_member(
        ZIP_PATH,
        "ihs2_pov.dta",
        ["case_id", "hhwght", "strata", "dist", "ta", "ea", "V13", "rexpagg", "rexp_cat06", "povline", "price_index", "hhsize"],
    )
    exp = read_member(
        ZIP_PATH,
        "ihs2_exp.dta",
        ["case_id", "rexp_cat061", "rexp_cat062", "rexp_cat063"],
    )

    merged = (
        pov.merge(
            household[["case_id", "V51", "idate"]].rename(columns={"V51": "psu", "idate": "raw_interview_date"}),
            on="case_id",
            how="left",
        )
        .merge(household_labels[["case_id", "raw_dist_label"]], on="case_id", how="left")
        .merge(exp, on="case_id", how="left")
    )
    for column in [
        "hhwght",
        "strata",
        "dist",
        "ta",
        "ea",
        "psu",
        "raw_interview_date",
        "rexpagg",
        "rexp_cat06",
        "rexp_cat061",
        "rexp_cat062",
        "rexp_cat063",
    ]:
        if column in merged:
            merged[column] = pd.to_numeric(merged[column], errors="coerce")

    dates = pd.to_datetime(merged["raw_interview_date"], unit="D", origin="1960-01-01", errors="coerce")
    merged["interview_date"] = dates.dt.strftime("%Y-%m-%d").fillna("")
    merged["interview_month"] = dates.dt.to_period("M").astype(str)
    merged.loc[dates.isna(), "interview_month"] = ""
    merged["oop_health_share_total"] = merged["rexp_cat06"] / merged["rexpagg"].where(merged["rexpagg"] > 0)
    merged["che10_total_budget"] = (merged["oop_health_share_total"] > 0.10).astype(int)
    merged["che25_total_budget"] = (merged["oop_health_share_total"] > 0.25).astype(int)

    analysis_mask = (
        merged["case_id"].notna()
        & (merged["rexpagg"] > 0)
        & merged["rexp_cat06"].notna()
        & merged["hhwght"].notna()
        & (merged["hhwght"] > 0)
        & merged["strata"].notna()
        & merged["psu"].notna()
    )
    out = merged.loc[analysis_mask].copy()
    out["country"] = COUNTRY
    out["wave"] = WAVE
    out["idno"] = IDNO
    out["case_id"] = out["case_id"].map(id_text)
    out["household_weight"] = out["hhwght"]
    out["raw_dist_code"] = out["dist"].map(code_text)
    out["raw_dist_label"] = out["raw_dist_label"].map(clean)
    out["ta"] = out["ta"].map(code_text)
    out["ea"] = out["ea"].map(code_text)
    out["strata"] = out["strata"].map(code_text)
    out["psu"] = out["psu"].map(code_text)
    out["total_consumption_rexpagg"] = out["rexpagg"]
    out["oop_health_rexp_cat06"] = out["rexp_cat06"]
    out["sdg382_ready"] = 0
    return out


def build_access_households() -> pd.DataFrame:
    health = read_member(ZIP_PATH, "sec_d.dta", ["case_id", "memid", "d04", "d07a", "d07b"])
    roster = read_member(ZIP_PATH, "ihs2_individ.dta", ["case_id", "memid"])
    roster_keys = {
        tuple(row)
        for row in roster[["case_id", "memid"]].dropna().drop_duplicates().itertuples(index=False, name=None)
    }
    health["_roster_match"] = [
        key in roster_keys for key in health[["case_id", "memid"]].itertuples(index=False, name=None)
    ]
    for column in ["d04", "d07a", "d07b"]:
        health[column] = pd.to_numeric(health[column], errors="coerce")
    health["_matched_person"] = health["_roster_match"].astype(int)
    health["_acute_need"] = (health["_roster_match"] & (health["d04"] == 1)).astype(int)
    health["_cost_barrier"] = (
        health["_roster_match"]
        & (health["d04"] == 1)
        & ((health["d07a"] == 2) | (health["d07b"] == 2))
    ).astype(int)
    grouped = (
        health.groupby("case_id", dropna=False)[["_matched_person", "_acute_need", "_cost_barrier"]]
        .sum()
        .reset_index()
    )
    grouped["case_id"] = grouped["case_id"].map(id_text)
    grouped = grouped.rename(
        columns={
            "_matched_person": "health_person_rows_matched",
            "_acute_need": "acute_need_persons",
            "_cost_barrier": "cost_barrier_forgone_care_persons",
        }
    )
    return grouped


def district_crosswalk() -> dict[str, str]:
    rows = read_csv_dicts(CROSSWALK_PATH)
    return {
        code_text(row.get("raw_dist_code")): clean(row.get("normalized_adm2_name"))
        for row in rows
        if clean(row.get("route_role")) == "sampled_raw_district"
    }


def build_climate_wide() -> pd.DataFrame:
    lag = pd.read_csv(LAG_WINDOW_PATH, dtype=str, encoding="utf-8-sig")
    lag["raw_dist_code"] = lag["raw_dist_code"].map(code_text)
    lag["interview_month"] = lag["interview_month"].map(clean)
    base = lag[["raw_dist_code", "interview_month"]].drop_duplicates()
    wide = base.copy()
    for lag_months in LAGS:
        subset = lag.loc[lag["lag_months"] == str(lag_months), [
            "raw_dist_code",
            "interview_month",
            "precip_total_mm",
            "precip_mean_monthly_mm",
            "window_complete",
        ]].copy()
        subset = subset.drop_duplicates(["raw_dist_code", "interview_month"])
        subset = subset.rename(
            columns={
                "precip_total_mm": f"chirps_precip_total_{lag_months}m_mm",
                "precip_mean_monthly_mm": f"chirps_precip_mean_{lag_months}m_mm",
                "window_complete": f"chirps_window_complete_{lag_months}m",
            }
        )
        wide = wide.merge(subset, on=["raw_dist_code", "interview_month"], how="left")
    for column in wide.columns:
        if column.startswith("chirps_precip_"):
            wide[column] = pd.to_numeric(wide[column], errors="coerce")
    return wide


def build_dataset() -> pd.DataFrame:
    financial = build_financial_households()
    access = build_access_households()
    climate = build_climate_wide()
    crosswalk = district_crosswalk()

    df = financial.merge(access, on="case_id", how="left").merge(
        climate,
        on=["raw_dist_code", "interview_month"],
        how="left",
    )
    for column in ["health_person_rows_matched", "acute_need_persons", "cost_barrier_forgone_care_persons"]:
        df[column] = pd.to_numeric(df[column], errors="coerce").fillna(0).astype(int)
    df["adm2_name"] = df["raw_dist_code"].map(crosswalk).fillna("")
    df["household_any_acute_need"] = (df["acute_need_persons"] > 0).astype(int)
    df["household_any_cost_barrier_forgone_care"] = (df["cost_barrier_forgone_care_persons"] > 0).astype(int)
    df["uhc_failure_che10_or_cost_barrier"] = (
        (df["che10_total_budget"] == 1) | (df["household_any_cost_barrier_forgone_care"] == 1)
    ).astype(int)
    df["uhc_failure_che25_or_cost_barrier"] = (
        (df["che25_total_budget"] == 1) | (df["household_any_cost_barrier_forgone_care"] == 1)
    ).astype(int)
    df["both_che10_and_cost_barrier"] = (
        (df["che10_total_budget"] == 1) & (df["household_any_cost_barrier_forgone_care"] == 1)
    ).astype(int)
    df["both_che25_and_cost_barrier"] = (
        (df["che25_total_budget"] == 1) & (df["household_any_cost_barrier_forgone_care"] == 1)
    ).astype(int)
    return df


def validation_row(component: str, ok: bool, evidence: str, action: str) -> dict[str, str]:
    return {
        "validation_component": component,
        "status": "pass" if ok else "fail",
        "evidence": evidence,
        "required_action": "" if ok else action,
    }


def build_validation(df: pd.DataFrame, gates: dict[str, str], data_written: bool, dictionary_written: bool) -> list[dict[str, str]]:
    climate_value_cols = [
        f"chirps_precip_total_{lag_months}m_mm" for lag_months in LAGS
    ] + [
        f"chirps_precip_mean_{lag_months}m_mm" for lag_months in LAGS
    ]
    climate_complete = df[climate_value_cols].notna().all(axis=1) if not df.empty else pd.Series(dtype=bool)
    unique_case_ids = df["case_id"].nunique() if "case_id" in df else 0
    rows = [
        validation_row(
            "upstream_financial_gate",
            gates["financial_che10_che25_ready"] == "1",
            f"che10_che25_financial_inputs_ready={gates['financial_che10_che25_ready']}",
            "Rerun or repair script/165 financial-protection construction policy.",
        ),
        validation_row(
            "upstream_access_gate",
            gates["access_cost_barrier_ready"] == "1",
            f"access_forgone_care_inputs_ready={gates['access_cost_barrier_ready']}",
            "Rerun or repair script/167 access person-key resolution policy.",
        ),
        validation_row(
            "upstream_missing_units_gate",
            gates["missing_units_recall_skip_ready"] == "1",
            f"missing_units_recall_skip_policy_final_verified={gates['missing_units_recall_skip_ready']}",
            "Rerun or repair script/168 missing/units/recall/skip policy.",
        ),
        validation_row(
            "upstream_climate_gate",
            gates["climate_chirps_admin2_ready"] == "1",
            f"accepted_chirps_era5_route={gates['climate_chirps_admin2_ready']}",
            "Rerun or repair script/170 CHIRPS ADM2 extraction validation.",
        ),
        validation_row(
            "row_count_matches_financial_universe",
            str(len(df)) == gates["financial_rows_expected"] and len(df) > 0,
            f"rows={len(df)}; expected_financial_rows={gates['financial_rows_expected']}",
            "Recheck household financial universe filters and joins.",
        ),
        validation_row(
            "case_id_unique",
            unique_case_ids == len(df) and len(df) > 0,
            f"unique_case_ids={unique_case_ids}; rows={len(df)}",
            "Repair one-to-one household-level joins before promotion.",
        ),
        validation_row(
            "financial_outcomes_complete",
            df[["total_consumption_rexpagg", "oop_health_rexp_cat06", "oop_health_share_total", "che10_total_budget", "che25_total_budget"]].notna().all().all(),
            f"che10_rows={int(df['che10_total_budget'].sum())}; che25_rows={int(df['che25_total_budget'].sum())}",
            "Repair financial outcome construction before promotion.",
        ),
        validation_row(
            "access_household_aggregation_complete",
            df[["health_person_rows_matched", "acute_need_persons", "cost_barrier_forgone_care_persons"]].notna().all().all(),
            f"matched_persons={int(df['health_person_rows_matched'].sum())}; acute_need_persons={int(df['acute_need_persons'].sum())}; cost_barrier_persons={int(df['cost_barrier_forgone_care_persons'].sum())}",
            "Repair household access aggregation before promotion.",
        ),
        validation_row(
            "climate_lag_windows_complete",
            bool(climate_complete.all()) and len(df) > 0,
            f"household_rows={len(df)}; complete_climate_rows={int(climate_complete.sum())}",
            "Repair CHIRPS lag-window merge before promotion.",
        ),
        validation_row(
            "admin2_crosswalk_complete",
            df["adm2_name"].map(clean).ne("").all(),
            f"mapped_adm2_rows={int(df['adm2_name'].map(clean).ne('').sum())}; rows={len(df)}",
            "Repair raw district to ADM2 crosswalk before promotion.",
        ),
        validation_row(
            "data_file_written",
            data_written and DATA_PATH.exists() and DATA_PATH.stat().st_size > 0,
            f"path={DATA_PATH.relative_to(TEMP_DIR.parent)}; exists={int(DATA_PATH.exists())}; bytes={DATA_PATH.stat().st_size if DATA_PATH.exists() else 0}",
            "Write the promoted household-climate dataset only after all upstream gates pass.",
        ),
        validation_row(
            "dictionary_written",
            dictionary_written and DICTIONARY_PATH.exists() and DICTIONARY_PATH.stat().st_size > 0,
            f"path={DICTIONARY_PATH.relative_to(TEMP_DIR.parent)}; exists={int(DICTIONARY_PATH.exists())}",
            "Write the promoted dataset dictionary.",
        ),
    ]
    return rows


def build_dictionary(df: pd.DataFrame) -> list[dict[str, str]]:
    definitions = {
        "country": ("constant", "Country name."),
        "wave": ("constant", "Survey wave/year label."),
        "idno": ("constant", "World Bank Microdata Library study identifier."),
        "case_id": ("ihs2_pov.dta/ihs2_household.dta/sec_d.dta", "Household identifier used for promoted household-level joins."),
        "household_weight": ("ihs2_pov.dta hhwght", "Household survey weight."),
        "strata": ("ihs2_pov.dta strata", "Survey stratum code."),
        "psu": ("ihs2_household.dta V51", "Household EA/PSU code accepted for this household-level dataset."),
        "raw_dist_code": ("ihs2_pov.dta dist", "Raw district code in the Malawi 2004 microdata."),
        "raw_dist_label": ("ihs2_household.dta dist label", "Raw district value label from the household file."),
        "adm2_name": ("mwi2004_chirps_admin2_crosswalk.csv", "Matched Malawi ADM2 boundary name used for CHIRPS aggregation."),
        "ta": ("ihs2_pov.dta ta", "Traditional authority code."),
        "ea": ("ihs2_pov.dta ea", "Enumeration area code."),
        "interview_date": ("ihs2_household.dta idate", "Interview date converted from Stata days since 1960-01-01."),
        "interview_month": ("ihs2_household.dta idate", "Interview month used as the lag-window anchor."),
        "total_consumption_rexpagg": ("ihs2_pov.dta rexpagg", "Survey-team total annual household expenditure denominator for CHE10/CHE25."),
        "oop_health_rexp_cat06": ("ihs2_pov.dta rexp_cat06", "Annual real household health OOP expenditure aggregate."),
        "oop_health_share_total": ("constructed", "oop_health_rexp_cat06 divided by total_consumption_rexpagg."),
        "che10_total_budget": ("constructed", "Indicator for OOP health share of total consumption greater than 10 percent."),
        "che25_total_budget": ("constructed", "Indicator for OOP health share of total consumption greater than 25 percent."),
        "sdg382_ready": ("policy flag", "Always 0 in this release; SDG 3.8.2 discretionary-budget denominator remains blocked."),
        "health_person_rows_matched": ("sec_d.dta and ihs2_individ.dta", "Roster-matched health-module person rows in the household."),
        "acute_need_persons": ("sec_d.dta d04", "Roster-matched persons with acute illness/injury need, d04==1."),
        "cost_barrier_forgone_care_persons": ("sec_d.dta d07a/d07b", "Acute-need persons with no-money no-action code in d07a or d07b."),
        "household_any_acute_need": ("constructed", "Household indicator for at least one acute-need person."),
        "household_any_cost_barrier_forgone_care": ("constructed", "Household indicator for at least one cost-barrier forgone-care person."),
        "uhc_failure_che10_or_cost_barrier": ("constructed", "Household indicator for CHE10 or any cost-barrier forgone care."),
        "uhc_failure_che25_or_cost_barrier": ("constructed", "Household indicator for CHE25 or any cost-barrier forgone care."),
        "both_che10_and_cost_barrier": ("constructed", "Household indicator for both CHE10 and any cost-barrier forgone care."),
        "both_che25_and_cost_barrier": ("constructed", "Household indicator for both CHE25 and any cost-barrier forgone care."),
    }
    for lag_months in LAGS:
        definitions[f"chirps_precip_total_{lag_months}m_mm"] = (
            "mwi2004_chirps_admin2_lag_window_exposure.csv",
            f"Total CHIRPS monthly precipitation in the {lag_months}-month window before interview month, ADM2 average.",
        )
        definitions[f"chirps_precip_mean_{lag_months}m_mm"] = (
            "mwi2004_chirps_admin2_lag_window_exposure.csv",
            f"Mean monthly CHIRPS precipitation in the {lag_months}-month window before interview month, ADM2 average.",
        )
    rows: list[dict[str, str]] = []
    for column in FINAL_COLUMNS:
        source, definition = definitions.get(column, ("constructed", "Promoted dataset column."))
        rows.append(
            {
                "column_name": column,
                "storage_type": clean(df[column].dtype) if column in df else "missing",
                "source": source,
                "definition": definition,
                "analysis_note": "Promoted for descriptive dataset synthesis only; predictive/reduced-form/causal ML gates remain blocked.",
            }
        )
    return rows


def build_summary(df: pd.DataFrame, validation_rows: list[dict[str, str]], gates: dict[str, str]) -> list[dict[str, str]]:
    all_pass = all(row["status"] == "pass" for row in validation_rows)
    data_sha = sha256_file(DATA_PATH) if DATA_PATH.exists() and DATA_PATH.stat().st_size > 0 else ""
    data_bytes = DATA_PATH.stat().st_size if DATA_PATH.exists() else 0
    climate_complete = int(
        df[[f"chirps_precip_total_{lag}m_mm" for lag in LAGS] + [f"chirps_precip_mean_{lag}m_mm" for lag in LAGS]]
        .notna()
        .all(axis=1)
        .sum()
    )
    rows = [
        {"metric": "country_wave", "value": IDNO, "interpretation": "Country-wave covered by this promoted household-climate synthesis."},
        {"metric": "analysis_ready_status", "value": "promoted_analysis_ready" if all_pass else "not_promoted", "interpretation": "Promotion status after household financial/access/climate synthesis validation."},
        {"metric": "promoted_rows", "value": str(len(df)) if all_pass else "0", "interpretation": "Household rows in the promoted analysis-ready dataset."},
        {"metric": "data_path", "value": str(DATA_PATH.relative_to(TEMP_DIR.parent)).replace("\\", "/") if DATA_PATH.exists() else "", "interpretation": "Local promoted dataset path; raw/household-level data may remain local for publication control."},
        {"metric": "data_sha256", "value": data_sha, "interpretation": "SHA-256 of the local promoted household-climate dataset."},
        {"metric": "data_bytes", "value": str(data_bytes), "interpretation": "Size of the local promoted household-climate dataset."},
        {"metric": "financial_rows", "value": str(len(df)), "interpretation": "Rows from the verified financial-protection household universe."},
        {"metric": "che10_rows", "value": str(int(df["che10_total_budget"].sum())), "interpretation": "Households with CHE10 total-budget financial hardship."},
        {"metric": "che25_rows", "value": str(int(df["che25_total_budget"].sum())), "interpretation": "Households with CHE25 total-budget financial hardship."},
        {"metric": "sdg382_ready", "value": "0", "interpretation": "SDG 3.8.2 remains blocked by discretionary-budget/societal-poverty-line policy."},
        {"metric": "health_person_rows_matched", "value": str(int(df["health_person_rows_matched"].sum())), "interpretation": "Roster-matched health-module person rows aggregated to households."},
        {"metric": "acute_need_persons", "value": str(int(df["acute_need_persons"].sum())), "interpretation": "Roster-matched acute need persons in promoted households."},
        {"metric": "cost_barrier_forgone_care_persons", "value": str(int(df["cost_barrier_forgone_care_persons"].sum())), "interpretation": "Acute-need persons with no-money forgone care."},
        {"metric": "households_any_acute_need", "value": str(int(df["household_any_acute_need"].sum())), "interpretation": "Households with at least one acute-need person."},
        {"metric": "households_any_cost_barrier_forgone_care", "value": str(int(df["household_any_cost_barrier_forgone_care"].sum())), "interpretation": "Households with at least one cost-barrier forgone-care person."},
        {"metric": "uhc_failure_che10_or_cost_barrier_rows", "value": str(int(df["uhc_failure_che10_or_cost_barrier"].sum())), "interpretation": "Households with CHE10 or cost-barrier forgone care."},
        {"metric": "uhc_failure_che25_or_cost_barrier_rows", "value": str(int(df["uhc_failure_che25_or_cost_barrier"].sum())), "interpretation": "Households with CHE25 or cost-barrier forgone care."},
        {"metric": "both_che10_and_cost_barrier_rows", "value": str(int(df["both_che10_and_cost_barrier"].sum())), "interpretation": "Households with both CHE10 and cost-barrier forgone care."},
        {"metric": "both_che25_and_cost_barrier_rows", "value": str(int(df["both_che25_and_cost_barrier"].sum())), "interpretation": "Households with both CHE25 and cost-barrier forgone care."},
        {"metric": "climate_exposure_complete_rows", "value": str(climate_complete), "interpretation": "Household rows with complete CHIRPS 1/3/6/12 month exposure windows."},
        {"metric": "adm2_districts_linked", "value": str(df["adm2_name"].nunique()), "interpretation": "Matched ADM2 districts represented in the promoted household dataset."},
        {"metric": "validation_pass_rows", "value": str(sum(1 for row in validation_rows if row["status"] == "pass")), "interpretation": "Promotion validation checks passing."},
        {"metric": "validation_fail_rows", "value": str(sum(1 for row in validation_rows if row["status"] != "pass")), "interpretation": "Promotion validation checks failing."},
        {"metric": "upstream_financial_che10_che25_ready", "value": gates["financial_che10_che25_ready"], "interpretation": "Financial input gate consumed by this synthesis."},
        {"metric": "upstream_access_cost_barrier_ready", "value": gates["access_cost_barrier_ready"], "interpretation": "Access input gate consumed by this synthesis."},
        {"metric": "upstream_missing_units_recall_skip_ready", "value": gates["missing_units_recall_skip_ready"], "interpretation": "Missing/unit/recall/skip gate consumed by this synthesis."},
        {"metric": "upstream_climate_chirps_admin2_ready", "value": gates["climate_chirps_admin2_ready"], "interpretation": "CHIRPS ADM2 extraction gate consumed by this synthesis."},
        {"metric": "data_write_gate_status", "value": "open_promoted_dataset_written" if all_pass else "closed_validation_failed", "interpretation": "Controlled data/ write gate outcome for this synthesis."},
        {"metric": "modeling_gate_status", "value": "blocked", "interpretation": "No predictive ML, reduced-form, causal ML, or policy learning is opened by one promoted country-wave."},
    ]
    return rows


def markdown_table(rows: list[dict[str, str]], columns: list[str], limit: int = 30) -> str:
    if not rows:
        return "_No rows._"
    lines = ["| " + " | ".join(columns) + " |", "| " + " | ".join("---" for _ in columns) + " |"]
    for row in rows[:limit]:
        lines.append("| " + " | ".join(clean(row.get(column)).replace("|", "/") for column in columns) + " |")
    if len(rows) > limit:
        lines.append("| " + " | ".join("..." for _ in columns) + " |")
    return "\n".join(lines)


def write_report(summary_rows: list[dict[str, str]], validation_rows: list[dict[str, str]], dictionary_rows: list[dict[str, str]]) -> None:
    report = f"""# Malawi 2004 Promoted Household-Climate Dataset

Dataset: `{IDNO}` - {COUNTRY} {WAVE}

This artifact synthesizes the first controlled household-level analysis dataset
for the climate-UHC workspace. It joins verified CHE10/CHE25 financial inputs,
verified cost-barrier forgone-care access inputs, and validated CHIRPS ADM2
rainfall lag windows.

It does not construct SDG 3.8.2 and does not open predictive ML, reduced-form,
causal ML, or policy-learning gates.

## Summary

{markdown_table(summary_rows, ["metric", "value", "interpretation"], 35)}

## Validation

{markdown_table(validation_rows, ["validation_component", "status", "evidence", "required_action"], 25)}

## Dictionary Preview

{markdown_table(dictionary_rows, ["column_name", "source", "definition"], 20)}

## Publication Control

The local data file is written to `data/mwi2004_household_climate_analysis.csv`.
For repository publication, prefer the script, dictionary, validation, summary,
and this report unless household-level derived microdata redistribution is
explicitly approved.
"""
    REPORT_PATH.write_text(report, encoding="utf-8")
    HANDOFF_PATH.write_text(report, encoding="utf-8")


def main() -> None:
    ensure_dirs()
    if not ZIP_PATH.exists():
        raise FileNotFoundError(f"Missing raw package: {ZIP_PATH}")

    gates = load_gate_flags()
    df = build_dataset()
    dictionary_rows = build_dictionary(df)

    preliminary_validation = build_validation(df, gates, data_written=False, dictionary_written=False)
    can_write = all(
        row["status"] == "pass"
        for row in preliminary_validation
        if row["validation_component"] not in {"data_file_written", "dictionary_written"}
    )
    if can_write:
        write_csv(DICTIONARY_PATH, dictionary_rows, DICTIONARY_COLUMNS)
        DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
        df[FINAL_COLUMNS].to_csv(DATA_PATH, index=False, encoding="utf-8-sig")

    validation_rows = build_validation(
        df,
        gates,
        data_written=DATA_PATH.exists() and DATA_PATH.stat().st_size > 0,
        dictionary_written=DICTIONARY_PATH.exists() and DICTIONARY_PATH.stat().st_size > 0,
    )
    summary_rows = build_summary(df, validation_rows, gates)
    write_csv(VALIDATION_PATH, validation_rows, VALIDATION_COLUMNS)
    write_csv(SUMMARY_PATH, summary_rows, SUMMARY_COLUMNS)
    write_report(summary_rows, validation_rows, dictionary_rows)
    append_log(
        TEMP_DIR / "audit_log.md",
        f"Built Malawi 2004 promoted household-climate dataset rows={len(df)} status={summary_value(summary_rows, 'analysis_ready_status', 'missing')}.",
    )
    print(
        f"Malawi 2004 promoted household-climate dataset rows={len(df)} "
        f"status={summary_value(summary_rows, 'analysis_ready_status', 'missing')}."
    )


if __name__ == "__main__":
    main()
