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

POLICY_PATH = RESULT_DIR / "mwi2004_financial_protection_construction_policy.csv"
SUMMARY_PATH = RESULT_DIR / "mwi2004_financial_protection_construction_policy_summary.csv"
REPORT_PATH = REPORT_DIR / "mwi2004_financial_protection_construction_policy.md"
HANDOFF_PATH = RAW_DIR / "_MWI2004_FINANCIAL_PROTECTION_CONSTRUCTION_POLICY.md"

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


def fmt(value: Any) -> str:
    if value is None or pd.isna(value):
        return ""
    try:
        return f"{float(value):.6g}"
    except (TypeError, ValueError):
        return clean(value)


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


def key_count(df: pd.DataFrame, key: str) -> tuple[int, int, int]:
    nonmissing = int(df[key].notna().sum()) if key in df else 0
    distinct = int(df[key].dropna().nunique()) if key in df else 0
    duplicates = max(nonmissing - distinct, 0)
    return nonmissing, distinct, duplicates


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


def weighted_rate(indicator: pd.Series, weight: pd.Series) -> float:
    valid = indicator.notna() & weight.notna() & (weight > 0)
    if not bool(valid.any()):
        return float("nan")
    return float((indicator[valid].astype(float) * weight[valid]).sum() / weight[valid].sum())


def build_outputs() -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    if not ZIP_PATH.exists():
        raise FileNotFoundError(f"Missing raw package: {ZIP_PATH}")

    household, household_meta = read_member(
        ZIP_PATH,
        "ihs2_household.dta",
        ["case_id", "hhwght", "strata", "dist", "ta", "ea", "V51", "idate"],
    )
    pov, pov_meta = read_member(
        ZIP_PATH,
        "ihs2_pov.dta",
        ["case_id", "hhwght", "strata", "dist", "ta", "ea", "V13", "rexpagg", "rexp_cat06", "povline", "price_index", "hhsize"],
    )
    exp, exp_meta = read_member(
        ZIP_PATH,
        "ihs2_exp.dta",
        ["case_id", "hhwght", "strata", "dist", "ta", "ea", "rexp_cat061", "rexp_cat062", "rexp_cat063", "price_index", "hhsize"],
    )

    household_nonmissing, household_distinct, household_duplicates = key_count(household, "case_id")
    pov_nonmissing, pov_distinct, pov_duplicates = key_count(pov, "case_id")
    exp_nonmissing, exp_distinct, exp_duplicates = key_count(exp, "case_id")

    merged = (
        pov.merge(
            household[["case_id", "V51", "idate"]].rename(columns={"V51": "household_psu", "idate": "household_idate"}),
            on="case_id",
            how="left",
        )
        .merge(
            exp[["case_id", "rexp_cat061", "rexp_cat062", "rexp_cat063"]],
            on="case_id",
            how="left",
        )
    )
    for column in ["hhwght", "rexpagg", "rexp_cat06", "rexp_cat061", "rexp_cat062", "rexp_cat063", "povline", "price_index"]:
        merged[column] = pd.to_numeric(merged[column], errors="coerce")

    hhwght = merged["hhwght"]
    rexpagg = merged["rexpagg"]
    oop = merged["rexp_cat06"]
    component_sum = merged[["rexp_cat061", "rexp_cat062", "rexp_cat063"]].sum(axis=1, min_count=1)
    component_diff = (oop - component_sum).abs()
    share = oop / rexpagg.where(rexpagg > 0)
    che10 = share > 0.10
    che25 = share > 0.25

    analysis_mask = (
        merged["case_id"].notna()
        & (rexpagg > 0)
        & oop.notna()
        & hhwght.notna()
        & (hhwght > 0)
        & merged["strata"].notna()
        & merged["household_psu"].notna()
    )
    diff_within_cent = int((component_diff.dropna() <= 0.01).sum())
    diff_rows = int(component_diff.dropna().shape[0])
    che10_count = int((analysis_mask & che10).sum())
    che25_count = int((analysis_mask & che25).sum())

    policy_rows = [
        policy_row(
            "household_financial_universe",
            "Use one row per household case_id from ihs2_pov.dta after exact case_id joins to ihs2_household.dta and ihs2_exp.dta.",
            "case_id",
            int(analysis_mask.sum()),
            f"pov label={label(pov_meta, 'case_id')}; household rows={len(household)}; pov rows={len(pov)}; exp rows={len(exp)}.",
            f"household case_id distinct={household_distinct}/{household_nonmissing}; pov distinct={pov_distinct}/{pov_nonmissing}; exp distinct={exp_distinct}/{exp_nonmissing}; duplicate rows={household_duplicates + pov_duplicates + exp_duplicates}.",
            "raw_value_verified_for_che10_che25",
            "This verifies the household financial universe only; person-level access and climate-linked data remain blocked.",
        ),
        policy_row(
            "survey_weight_and_design",
            "Use hhwght as household weight, strata as district-by-urban/rural stratum, and V51/V13 as the household EA/PSU identifier for household-level financial estimates.",
            "hhwght;strata;V51;V13;dist;ta;ea",
            int(analysis_mask.sum()),
            f"hhwght={label(pov_meta, 'hhwght')}; strata={label(pov_meta, 'strata')}; V51={label(household_meta, 'V51')}; V13={label(pov_meta, 'V13')}.",
            f"positive hhwght={int((hhwght > 0).sum())}/{len(merged)}; strata distinct={merged['strata'].dropna().nunique()}; household_psu distinct={merged['household_psu'].dropna().nunique()}; dist+ta+ea distinct={merged[['dist', 'ta', 'ea']].dropna().drop_duplicates().shape[0]}.",
            "raw_value_verified_for_che10_che25",
            "Survey design is verified for household financial estimates; cluster choice must be rechecked for person-level access and future cross-country modeling.",
        ),
        policy_row(
            "che_denominator_total_consumption",
            "Use rexpagg as total annual household expenditure denominator for CHE10/CHE25.",
            "rexpagg",
            int((analysis_mask & (rexpagg > 0)).sum()),
            f"rexpagg={label(pov_meta, 'rexpagg')}; price_index={label(pov_meta, 'price_index')}; hhsize={label(pov_meta, 'hhsize')}.",
            f"positive rexpagg={int((rexpagg > 0).sum())}/{len(merged)}; min={fmt(rexpagg.min())}; median={fmt(rexpagg.median())}; max={fmt(rexpagg.max())}.",
            "raw_value_verified_for_che10_che25",
            "This accepts CHE10/CHE25 total-budget denominator only; SDG 3.8.2 discretionary-budget denominator remains blocked.",
        ),
        policy_row(
            "oop_health_spending",
            "Use rexp_cat06 as annual real household health OOP aggregate; use rexp_cat061-063 only as component consistency evidence.",
            "rexp_cat06;rexp_cat061;rexp_cat062;rexp_cat063",
            int(oop.notna().sum()),
            f"rexp_cat06={label(pov_meta, 'rexp_cat06')}; rexp_cat061={label(exp_meta, 'rexp_cat061')}; rexp_cat062={label(exp_meta, 'rexp_cat062')}; rexp_cat063={label(exp_meta, 'rexp_cat063')}.",
            f"rexp_cat06 nonmissing={int(oop.notna().sum())}/{len(merged)}; positive={int((oop > 0).sum())}; component diff<=0.01={diff_within_cent}/{diff_rows}; max diff={fmt(component_diff.max())}.",
            "raw_value_verified_for_che10_che25",
            "Health-module recall-period spending remains context only; promoted CHE uses the survey-team annual household aggregate.",
        ),
        policy_row(
            "che10_candidate",
            "Construct CHE10 as rexp_cat06 / rexpagg > 0.10 among verified household financial rows.",
            "rexp_cat06;rexpagg;hhwght;strata;V51",
            che10_count,
            "CHE10 is an older/common total-budget catastrophic health expenditure indicator, not the current SDG 3.8.2 indicator.",
            f"unweighted CHE10 rows={che10_count}; weighted rate={fmt(weighted_rate(che10.where(analysis_mask), hhwght))}.",
            "candidate_outcome_ready_after_data_write_gate",
            "Do not write the outcome to data/ until missing-code policy, synthesis, and registry write gate pass.",
        ),
        policy_row(
            "che25_candidate",
            "Construct CHE25 as rexp_cat06 / rexpagg > 0.25 among verified household financial rows.",
            "rexp_cat06;rexpagg;hhwght;strata;V51",
            che25_count,
            "CHE25 is an older/common total-budget catastrophic health expenditure indicator, not the current SDG 3.8.2 indicator.",
            f"unweighted CHE25 rows={che25_count}; weighted rate={fmt(weighted_rate(che25.where(analysis_mask), hhwght))}.",
            "candidate_outcome_ready_after_data_write_gate",
            "Do not write the outcome to data/ until missing-code policy, synthesis, and registry write gate pass.",
        ),
        policy_row(
            "sdg382_discretionary_budget",
            "Do not construct SDG 3.8.2 yet; the current raw file poverty line is documented but not accepted as the current societal poverty-line input.",
            "povline;price_index;hhsize;rexpagg;rexp_cat06",
            0,
            f"povline={label(pov_meta, 'povline')}; price_index={label(pov_meta, 'price_index')}.",
            f"povline positive={int((merged['povline'] > 0).sum())}/{len(merged)}; price_index positive={int((merged['price_index'] > 0).sum())}/{len(merged)}.",
            "blocked_sdg382_discretionary_budget_policy_required",
            "Need PPP/CPI/societal poverty-line policy before SDG 3.8.2 can be marked ready.",
        ),
    ]

    summary_rows = [
        {"metric": "country_wave", "value": IDNO, "interpretation": "Country-wave covered by this financial-protection construction policy."},
        {"metric": "household_financial_rows", "value": str(int(analysis_mask.sum())), "interpretation": "Rows meeting verified household financial input requirements for CHE10/CHE25 candidates."},
        {"metric": "household_case_id_duplicate_rows", "value": str(household_duplicates + pov_duplicates + exp_duplicates), "interpretation": "Duplicate household keys across household, poverty, and expenditure files."},
        {"metric": "positive_household_weight_rows", "value": str(int((hhwght > 0).sum())), "interpretation": "Rows with positive hhwght in the poverty/consumption file."},
        {"metric": "strata_distinct", "value": str(int(merged["strata"].dropna().nunique())), "interpretation": "Distinct survey strata in the household financial universe."},
        {"metric": "psu_distinct", "value": str(int(merged["household_psu"].dropna().nunique())), "interpretation": "Distinct V51 household EA/PSU identifiers after join."},
        {"metric": "rexpagg_positive_rows", "value": str(int((rexpagg > 0).sum())), "interpretation": "Positive total annual household expenditure rows."},
        {"metric": "rexp_cat06_nonmissing_rows", "value": str(int(oop.notna().sum())), "interpretation": "Nonmissing annual household health OOP aggregate rows."},
        {"metric": "oop_component_diff_le_0_01_rows", "value": f"{diff_within_cent}/{diff_rows}", "interpretation": "OOP aggregate-component agreement under 0.01 local currency tolerance."},
        {"metric": "che10_candidate_rows", "value": str(che10_count), "interpretation": "Candidate CHE10 rows among verified household financial inputs."},
        {"metric": "che10_candidate_weighted_rate", "value": fmt(weighted_rate(che10.where(analysis_mask), hhwght)), "interpretation": "Weighted CHE10 candidate rate; audit statistic only, not promoted data."},
        {"metric": "che25_candidate_rows", "value": str(che25_count), "interpretation": "Candidate CHE25 rows among verified household financial inputs."},
        {"metric": "che25_candidate_weighted_rate", "value": fmt(weighted_rate(che25.where(analysis_mask), hhwght)), "interpretation": "Weighted CHE25 candidate rate; audit statistic only, not promoted data."},
        {"metric": "weights_design_final_verified_for_financial", "value": "1", "interpretation": "Weight, strata, and household PSU fields are accepted for household financial CHE candidates."},
        {"metric": "consumption_or_income_final_verified_for_che", "value": "1", "interpretation": "rexpagg is accepted as CHE10/CHE25 total-budget denominator."},
        {"metric": "oop_health_expenditure_final_verified_for_che", "value": "1", "interpretation": "rexp_cat06 is accepted as annual household health OOP aggregate for CHE10/CHE25."},
        {"metric": "che10_che25_financial_inputs_ready", "value": "1", "interpretation": "Financial-protection inputs are raw-value verified for CHE10/CHE25 only."},
        {"metric": "sdg382_ready", "value": "0", "interpretation": "SDG 3.8.2 remains blocked by discretionary-budget/societal-poverty-line policy."},
        {"metric": "financial_policy_status", "value": "che10_che25_financial_inputs_verified_sdg382_blocked", "interpretation": "CHE10/CHE25 financial inputs accepted; SDG 3.8.2 and data writes remain blocked."},
        {"metric": "data_write_gate_status", "value": "closed", "interpretation": "No promoted dataset may be written from this policy artifact alone."},
    ]
    return policy_rows, summary_rows


def write_report(policy_rows: list[dict[str, str]], summary_rows: list[dict[str, str]]) -> None:
    report = f"""# Malawi 2004 Financial-Protection Construction Policy

Dataset: `{IDNO}` - {COUNTRY} {WAVE}

This artifact accepts the raw-value policy for CHE10/CHE25 financial inputs
only. It does not construct SDG 3.8.2, does not write rows to `data/`, does not
resolve health/access gates, and does not accept a climate-linkage route.

## Summary

{markdown_table(summary_rows, ["metric", "value", "interpretation"], 30)}

## Policy Rows

{markdown_table(policy_rows, ["policy_component", "accepted_rule", "raw_variables", "aggregate_count", "acceptance_status", "remaining_blocker"], 20)}

## Accepted For CHE10/CHE25

- Household universe: unique `case_id` rows from `ihs2_pov.dta`, joined to
  `ihs2_household.dta` and `ihs2_exp.dta`.
- Survey design: `hhwght`, `strata`, and household EA/PSU identifier `V51`
  with `V13` as the same PSU-style field in the poverty file.
- Denominator: `rexpagg`, labeled total annual household expenditure.
- OOP: `rexp_cat06`, labeled health real annual household expenditure, checked
  against `rexp_cat061 + rexp_cat062 + rexp_cat063`.

## Still Blocked

- SDG 3.8.2 remains blocked until the discretionary-budget denominator and
  current societal poverty-line/PPP/CPI policy are accepted.
- Person-level health/access, missing/skip policy, climate linkage, synthesis,
  and registry write gates remain closed.
- Candidate CHE10/CHE25 counts in this artifact are audit statistics, not
  promoted analysis data.
"""
    REPORT_PATH.write_text(report, encoding="utf-8")
    HANDOFF_PATH.write_text(report, encoding="utf-8")


def main() -> None:
    ensure_dirs()
    policy_rows, summary_rows = build_outputs()
    write_csv(POLICY_PATH, policy_rows, POLICY_COLUMNS)
    write_csv(SUMMARY_PATH, summary_rows, SUMMARY_COLUMNS)
    write_report(policy_rows, summary_rows)
    append_log(TEMP_DIR / "audit_log.md", f"Built Malawi 2004 financial-protection construction policy for {IDNO}.")


if __name__ == "__main__":
    main()
