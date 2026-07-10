from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
import pyarrow.parquet as pq


ROOT = Path(__file__).resolve().parents[2]
PANEL = ROOT / "data" / "analysis_ready" / "sipp_2018_2024_person_month_panel.parquet"
METADATA = ROOT / "data" / "metadata" / "variable_registry.csv"
OUT = ROOT / "result" / "idea_scan"
REPORT = ROOT / "report" / "10_new_idea_scan.md"


STATE = {
    "AL": "01",
    "AK": "02",
    "AZ": "04",
    "AR": "05",
    "CA": "06",
    "CO": "08",
    "CT": "09",
    "DE": "10",
    "DC": "11",
    "FL": "12",
    "GA": "13",
    "HI": "15",
    "ID": "16",
    "IL": "17",
    "IN": "18",
    "IA": "19",
    "KS": "20",
    "KY": "21",
    "LA": "22",
    "ME": "23",
    "MD": "24",
    "MA": "25",
    "MI": "26",
    "MN": "27",
    "MS": "28",
    "MO": "29",
    "MT": "30",
    "NE": "31",
    "NV": "32",
    "NH": "33",
    "NJ": "34",
    "NM": "35",
    "NY": "36",
    "NC": "37",
    "ND": "38",
    "OH": "39",
    "OK": "40",
    "OR": "41",
    "PA": "42",
    "RI": "44",
    "SC": "45",
    "SD": "46",
    "TN": "47",
    "TX": "48",
    "UT": "49",
    "VT": "50",
    "VA": "51",
    "WA": "53",
    "WV": "54",
    "WI": "55",
    "WY": "56",
}


# Expansion dates observable in or near the 2017-2023 reference window.
LATE_EXPANSION = {
    "VA": (2019, 1),
    "NE": (2020, 10),
    "OK": (2021, 7),
    "MO": (2021, 10),
    "SD": (2023, 7),
    "NC": (2023, 12),
}


# First program year for broad 1332 reinsurance states inside the SIPP window.
# The screen is not a final policy file; it only flags whether SIPP has enough
# individual-market observations to justify a proper state-policy build.
REINSURANCE_START = {
    "AK": 2017,
    "MN": 2018,
    "OR": 2018,
    "ME": 2019,
    "MD": 2019,
    "NJ": 2019,
    "WI": 2019,
    "CO": 2020,
    "DE": 2020,
    "MT": 2020,
    "ND": 2020,
    "NH": 2021,
    "PA": 2021,
    "GA": 2022,
    "VA": 2023,
}


REQUIRED_BY_IDEA = {
    "aca_ptc_400_fpl_cliff": [
        "TFINCPOV",
        "RHLTHMTH",
        "RPRITYPE2",
        "RMARKTPLACE",
        "EPRIEXCH1",
        "EPRISUBS1",
        "TAGE",
        "state_fips",
    ],
    "family_glitch_fix": [
        "RPRITYPE2",
        "RMARKTPLACE",
        "RDIRECTANN",
        "EPNSPOUSE",
        "person_id",
        "state_fips",
        "REMPLOYANN",
        "employer_offer_or_family_premium",
    ],
    "arkansas_medicaid_work_requirements": [
        "state_fips",
        "TAGE",
        "TFINCPOV",
        "EMDMTH",
        "RHLTHMTH",
        "RMESR",
        "RDIS",
        "RSSI_MNYN",
        "RSNAP_MNYN",
    ],
    "late_medicaid_expansion": [
        "state_fips",
        "reference_year",
        "reference_month",
        "TAGE",
        "TFINCPOV",
        "EMDMTH",
        "RHLTHMTH",
    ],
    "public_charge_immigrant_chilling": [
        "ECITIZEN",
        "ENATCIT",
        "TYRENTRY",
        "TIMSTAT",
        "EMDMTH",
        "RSNAP_MNYN",
        "RTANF_MNYN",
    ],
    "adult_postpartum_medicaid_extension": [
        "EPREGWORK",
        "EBIRTHWORK",
        "TPSTBRTHINT",
        "EMDMTH",
        "RHLTHMTH",
        "state_fips",
    ],
    "state_reinsurance_individual_market": [
        "state_fips",
        "reference_year",
        "TAGE",
        "TFINCPOV",
        "RPRITYPE2",
        "RMARKTPLACE",
        "EPRISUBS1",
        "RHLTHMTH",
    ],
}


def yes(series: pd.Series) -> pd.Series:
    return series.eq(1)


def wmean(x: pd.Series, w: pd.Series) -> float:
    mask = x.notna() & w.notna() & (w > 0)
    if not mask.any():
        return np.nan
    return float(np.average(x[mask].astype(float), weights=w[mask].astype(float)))


def clean_weight(df: pd.DataFrame) -> pd.Series:
    w = pd.to_numeric(df.get("WPFINWGT"), errors="coerce")
    if "TSSSAMT" in df.columns:
        w = w.where(w.gt(0), pd.to_numeric(df["TSSSAMT"], errors="coerce"))
    return w.where(w.gt(0), 1.0)


def persons(s: pd.Series) -> int:
    return int(s.dropna().nunique())


def summarize_group(df: pd.DataFrame, by: list[str], outcomes: list[str]) -> pd.DataFrame:
    rows = []
    for keys, g in df.groupby(by, dropna=False, observed=True):
        if not isinstance(keys, tuple):
            keys = (keys,)
        row = {name: value for name, value in zip(by, keys)}
        row["rows"] = int(len(g))
        row["persons"] = persons(g["person_id"])
        row["weighted_rows"] = float(g["weight"].sum())
        for out in outcomes:
            row[f"{out}_mean_w"] = wmean(g[out], g["weight"])
            row[f"{out}_events"] = int(g[out].fillna(False).sum())
        rows.append(row)
    return pd.DataFrame(rows)


def dd_from_group(
    table: pd.DataFrame,
    group_col: str,
    post_col: str,
    outcome_col: str,
    high_value: int = 1,
    low_value: int = 0,
) -> float:
    value = {}
    for _, row in table.iterrows():
        key = (int(row[group_col]), int(row[post_col]))
        value[key] = row[outcome_col]
    needed = [(high_value, 1), (high_value, 0), (low_value, 1), (low_value, 0)]
    if any(k not in value or pd.isna(value[k]) for k in needed):
        return np.nan
    return float((value[(high_value, 1)] - value[(high_value, 0)]) - (value[(low_value, 1)] - value[(low_value, 0)]))


def read_panel() -> pd.DataFrame:
    cols = [
        "person_id",
        "person_month_key",
        "file_year",
        "reference_year",
        "reference_month",
        "state_fips",
        "TAGE",
        "ESEX",
        "ERACE",
        "EORIGIN",
        "EHISPAN",
        "EEDUC",
        "RDIS",
        "RDIS_ALT",
        "WPFINWGT",
        "TSSSAMT",
        "RHLTHMTH",
        "EMDMTH",
        "RPUBMTH",
        "RPUBTYPE1",
        "RPUBTYPE2",
        "RPRIMTH",
        "RPRITYPE2",
        "RMARKTPLACE",
        "EPRIEXCH1",
        "EPRIEXCH2",
        "EPRISUBS1",
        "EPRISUBS2",
        "EMDEXCH",
        "EMDSUBS",
        "RDIRECTANN",
        "RMCAIDANN",
        "RMESR",
        "RMWKWJB",
        "RSNAP_MNYN",
        "RTANF_MNYN",
        "RSSI_MNYN",
        "TPEARN",
        "TPTOTINC",
        "TFTOTINC",
        "THTOTINC",
        "TFINCPOV",
        "THINCPOV",
        "TFCYINCPOV",
        "THCYINCPOV",
        "TMDPAY",
        "TDAYSICK",
        "THOSPNIT",
        "TVISDOC",
    ]
    df = pd.read_parquet(PANEL, columns=cols)
    df["state_fips"] = df["state_fips"].astype(str).str.zfill(2)
    df["age"] = pd.to_numeric(df["TAGE"], errors="coerce")
    df["adult_19_64"] = df["age"].between(19, 64, inclusive="both")
    df["adult_26_64"] = df["age"].between(26, 64, inclusive="both")
    df["older_50_64"] = df["age"].between(50, 64, inclusive="both")
    df["month_index"] = df["reference_year"] * 12 + df["reference_month"]
    df["weight"] = clean_weight(df)
    df["fpl"] = pd.to_numeric(df["TFINCPOV"], errors="coerce")
    df.loc[(df["fpl"] < 0) | (df["fpl"] > 20), "fpl"] = np.nan
    df["fpl_annual"] = pd.to_numeric(df["TFCYINCPOV"], errors="coerce")
    df.loc[(df["fpl_annual"] < 0) | (df["fpl_annual"] > 20), "fpl_annual"] = np.nan
    df["any_coverage"] = yes(df["RHLTHMTH"])
    df["uninsured"] = df["RHLTHMTH"].eq(2)
    df["medicaid"] = yes(df["EMDMTH"]) | yes(df["RPUBTYPE2"])
    df["private"] = yes(df["RPRIMTH"])
    df["direct_purchase"] = yes(df["RPRITYPE2"]) | yes(df["RMARKTPLACE"]) | yes(df["RDIRECTANN"])
    df["marketplace"] = yes(df["RMARKTPLACE"]) | yes(df["EPRIEXCH1"]) | yes(df["EPRIEXCH2"]) | yes(df["EMDEXCH"])
    df["subsidized_private"] = yes(df["EPRISUBS1"]) | yes(df["EPRISUBS2"]) | yes(df["EMDSUBS"])
    df["market_or_subsidy"] = df["marketplace"] | df["subsidized_private"]
    df["working_any_week"] = pd.to_numeric(df["RMWKWJB"], errors="coerce").gt(0) | pd.to_numeric(df["RMESR"], errors="coerce").between(1, 5)
    df["disabled_or_ssi"] = yes(df["RDIS"]) | yes(df["RDIS_ALT"]) | yes(df["RSSI_MNYN"])
    df["oop_any"] = pd.to_numeric(df["TMDPAY"], errors="coerce").gt(0)
    df["doctor_any"] = pd.to_numeric(df["TVISDOC"], errors="coerce").gt(0)
    return df


def variable_availability(df: pd.DataFrame) -> pd.DataFrame:
    registry = pd.read_csv(METADATA, usecols=["variable_name", "years_present", "label_description"], dtype=str)
    registry_vars = set(registry["variable_name"])
    panel_vars = set(df.columns) | set(pq.ParquetFile(PANEL).schema.names)
    rows = []
    for idea, variables in REQUIRED_BY_IDEA.items():
        for var in variables:
            meta = registry.loc[registry["variable_name"].eq(var)].head(1)
            rows.append(
                {
                    "idea": idea,
                    "variable": var,
                    "in_current_parquet": var in panel_vars,
                    "in_metadata_registry": var in registry_vars,
                    "years_present": "" if meta.empty else meta.iloc[0]["years_present"],
                    "description": "" if meta.empty else meta.iloc[0]["label_description"],
                }
            )
    return pd.DataFrame(rows)


def screen_ptc(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    sample = df[
        df["adult_26_64"]
        & df["fpl_annual"].between(3.0, 5.0, inclusive="both")
        & df["reference_year"].between(2017, 2023)
    ].copy()
    sample["post_arpa"] = sample["reference_year"].ge(2021).astype(int)
    sample["above_400"] = sample["fpl_annual"].gt(4.0).astype(int)
    sample["near_bin"] = pd.cut(
        sample["fpl_annual"],
        bins=[3.0, 3.5, 4.0, 4.5, 5.0],
        labels=["300-350", "350-400", "400-450", "450-500"],
        right=True,
        include_lowest=True,
    )
    outcomes = ["direct_purchase", "marketplace", "subsidized_private", "market_or_subsidy", "uninsured", "any_coverage"]
    group = summarize_group(sample, ["post_arpa", "above_400"], outcomes)
    bin_group = summarize_group(sample, ["post_arpa", "near_bin", "older_50_64"], outcomes)

    dd_rows = []
    for out in outcomes:
        dd_rows.append(
            {
                "design": "PTC 400% FPL difference-in-discontinuities screen",
                "outcome": out,
                "dd_above400_minus_below400_post2021_minus_pre": dd_from_group(
                    group, "above_400", "post_arpa", f"{out}_mean_w"
                ),
                "rows": int(len(sample)),
                "persons": persons(sample["person_id"]),
                "above400_persons": persons(sample.loc[sample["above_400"].eq(1), "person_id"]),
                "below400_persons": persons(sample.loc[sample["above_400"].eq(0), "person_id"]),
                "above400_market_events": int(sample.loc[sample["above_400"].eq(1), "market_or_subsidy"].sum()),
                "above400_uninsured_events": int(sample.loc[sample["above_400"].eq(1), "uninsured"].sum()),
            }
        )
    return pd.DataFrame(dd_rows), bin_group


def screen_work_requirements(df: pd.DataFrame) -> pd.DataFrame:
    controls = [STATE[s] for s in ["LA", "MO", "MS", "OK", "TN", "TX"]]
    ar = STATE["AR"]
    sample = df[
        df["adult_19_64"]
        & df["fpl"].between(0.0, 1.38, inclusive="both")
        & df["reference_year"].between(2017, 2019)
        & df["state_fips"].isin([ar] + controls)
    ].copy()
    sample["arkansas"] = sample["state_fips"].eq(ar).astype(int)
    sample["age_30_49"] = sample["age"].between(30, 49, inclusive="both").astype(int)
    sample["workreq_window"] = (
        (sample["reference_year"].eq(2018) & sample["reference_month"].ge(6))
        | (sample["reference_year"].eq(2019) & sample["reference_month"].le(3))
    ).astype(int)
    sample["targeted"] = (sample["arkansas"].eq(1) & sample["age_30_49"].eq(1)).astype(int)
    outcomes = ["medicaid", "uninsured", "working_any_week"]
    g = summarize_group(sample, ["arkansas", "age_30_49", "workreq_window"], outcomes)
    g["candidate"] = "arkansas_medicaid_work_requirements"
    return g


def screen_late_expansions(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for st, (year, month) in LATE_EXPANSION.items():
        fips = STATE[st]
        event_month = year * 12 + month
        sample = df[
            df["adult_19_64"]
            & df["fpl"].between(0.0, 1.38, inclusive="both")
            & df["state_fips"].eq(fips)
            & df["month_index"].between(event_month - 12, event_month + 12)
        ].copy()
        sample["post"] = sample["month_index"].ge(event_month)
        rows.append(
            {
                "candidate": "late_medicaid_expansion",
                "state": st,
                "implementation": f"{year:04d}-{month:02d}",
                "rows": int(len(sample)),
                "persons": persons(sample["person_id"]),
                "pre_persons": persons(sample.loc[~sample["post"], "person_id"]),
                "post_persons": persons(sample.loc[sample["post"], "person_id"]),
                "medicaid_persons": persons(sample.loc[sample["medicaid"], "person_id"]),
                "uninsured_events": int(sample["uninsured"].sum()),
                "medicaid_mean_w_pre": wmean(sample.loc[~sample["post"], "medicaid"], sample.loc[~sample["post"], "weight"]),
                "medicaid_mean_w_post": wmean(sample.loc[sample["post"], "medicaid"], sample.loc[sample["post"], "weight"]),
                "uninsured_mean_w_pre": wmean(sample.loc[~sample["post"], "uninsured"], sample.loc[~sample["post"], "weight"]),
                "uninsured_mean_w_post": wmean(sample.loc[sample["post"], "uninsured"], sample.loc[sample["post"], "weight"]),
            }
        )
    return pd.DataFrame(rows)


def screen_reinsurance(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for st, start_year in REINSURANCE_START.items():
        fips = STATE[st]
        sample = df[
            df["adult_26_64"]
            & df["state_fips"].eq(fips)
            & df["reference_year"].between(start_year - 1, start_year + 1)
            & df["fpl"].between(1.5, 6.0, inclusive="both")
        ].copy()
        sample["post"] = sample["reference_year"].ge(start_year)
        rows.append(
            {
                "candidate": "state_reinsurance_individual_market",
                "state": st,
                "first_year": start_year,
                "rows": int(len(sample)),
                "persons": persons(sample["person_id"]),
                "pre_persons": persons(sample.loc[~sample["post"], "person_id"]),
                "post_persons": persons(sample.loc[sample["post"], "person_id"]),
                "direct_purchase_events": int(sample["direct_purchase"].sum()),
                "market_or_subsidy_events": int(sample["market_or_subsidy"].sum()),
                "uninsured_events": int(sample["uninsured"].sum()),
                "direct_purchase_mean_w_pre": wmean(sample.loc[~sample["post"], "direct_purchase"], sample.loc[~sample["post"], "weight"]),
                "direct_purchase_mean_w_post": wmean(sample.loc[sample["post"], "direct_purchase"], sample.loc[sample["post"], "weight"]),
            }
        )
    return pd.DataFrame(rows)


def build_candidate_summary(df: pd.DataFrame, availability: pd.DataFrame, ptc_dd: pd.DataFrame, work: pd.DataFrame, exp: pd.DataFrame, reins: pd.DataFrame) -> pd.DataFrame:
    missing = (
        availability.groupby("idea")
        .apply(lambda g: int((~g["in_current_parquet"]).sum()), include_groups=False)
        .rename("missing_current_parquet_vars")
        .reset_index()
    )
    rows = []
    ptc_first = ptc_dd.iloc[0]
    rows.append(
        {
            "rank": 1,
            "candidate": "aca_ptc_400_fpl_cliff",
            "policy_shock": "2021 ARPA/IRA enhanced premium tax credits removed the 400% FPL cliff through 2025; 2026 cliff return is current policy debate.",
            "identification": "Difference-in-discontinuities around 400% FPL, pre-2021 vs 2021-2023, with age/premium-intensity heterogeneity.",
            "rows": int(ptc_first["rows"]),
            "persons": int(ptc_first["persons"]),
            "key_support": f"above400 persons={int(ptc_first['above400_persons'])}; above400 market/subsidy events={int(ptc_first['above400_market_events'])}; above400 uninsured events={int(ptc_first['above400_uninsured_events'])}",
            "current_parquet_fit": "strong",
            "fast_verdict": "GO-TO-NEXT-TEST",
        }
    )
    late_total_persons = int(exp["persons"].sum())
    rows.append(
        {
            "rank": 2,
            "candidate": "late_medicaid_expansion",
            "policy_shock": "Late ACA Medicaid expansion adoptions in VA, NE, OK, MO, SD, NC within 2019-2023.",
            "identification": "Staggered state-month event study for low-income adults, best treated as validation/secondary unless a sharper mechanism is added.",
            "rows": int(exp["rows"].sum()),
            "persons": late_total_persons,
            "key_support": f"state-specific persons range={int(exp['persons'].min())}-{int(exp['persons'].max())}; NC/SD have very short post windows in SIPP.",
            "current_parquet_fit": "strong",
            "fast_verdict": "CONDITIONAL-BUT-LITERATURE-SATURATED",
        }
    )
    ar_people = persons(df.loc[df["state_fips"].eq(STATE["AR"]) & df["adult_19_64"], "person_id"])
    rows.append(
        {
            "rank": 3,
            "candidate": "arkansas_medicaid_work_requirements",
            "policy_shock": "Arkansas 2018-2019 Medicaid work/reporting requirement; policy is newly salient because 2025 federal law revives work requirements.",
            "identification": "Triple difference: Arkansas vs neighboring controls, target age 30-49 vs other adults, work-requirement months vs pre.",
            "rows": int(work["rows"].sum()),
            "persons": int(work["persons"].sum()),
            "key_support": f"Arkansas adult persons in full panel={ar_people}; target/control support is probably too thin for a top-econ main paper.",
            "current_parquet_fit": "strong",
            "fast_verdict": "FAST-NOGO-FOR-MAIN-PAPER",
        }
    )
    rows.append(
        {
            "rank": 4,
            "candidate": "state_reinsurance_individual_market",
            "policy_shock": "State 1332 reinsurance programs lower gross individual-market premiums, but may have ambiguous subsidized-enrollee effects.",
            "identification": "State adoption event study focused on individual-market/direct-purchase coverage.",
            "rows": int(reins["rows"].sum()),
            "persons": int(reins["persons"].sum()),
            "key_support": f"treated-state direct-purchase events={int(reins['direct_purchase_events'].sum())}; market/subsidy events={int(reins['market_or_subsidy_events'].sum())}",
            "current_parquet_fit": "moderate",
            "fast_verdict": "BACKUP-ONLY",
        }
    )
    for cand, verdict, fit, reason in [
        (
            "family_glitch_fix",
            "NOT-TESTABLE-WITH-CURRENT-PARQUET",
            "weak",
            "Needs employer offer/family premium and dependent-level eligibility; current 96-column parquet lacks the key treatment variable.",
        ),
        (
            "public_charge_immigrant_chilling",
            "NOT-TESTABLE-WITH-CURRENT-PARQUET",
            "weak",
            "Metadata contains citizenship/nativity variables, but current parquet does not include them; national timing is also heavily confounded by COVID.",
        ),
        (
            "adult_postpartum_medicaid_extension",
            "DEFER",
            "weak",
            "Metadata contains pregnancy/birth variables but current parquet does not; also drifts toward maternal/child coverage rather than the requested adult general agenda.",
        ),
    ]:
        rows.append(
            {
                "rank": len(rows) + 1,
                "candidate": cand,
                "policy_shock": "",
                "identification": "",
                "rows": 0,
                "persons": 0,
                "key_support": reason,
                "current_parquet_fit": fit,
                "fast_verdict": verdict,
            }
        )
    summary = pd.DataFrame(rows).merge(missing, left_on="candidate", right_on="idea", how="left").drop(columns=["idea"])
    return summary


def write_report(summary: pd.DataFrame, ptc_dd: pd.DataFrame, ptc_bins: pd.DataFrame, work: pd.DataFrame, exp: pd.DataFrame, reins: pd.DataFrame) -> None:
    top = summary.sort_values("rank").iloc[0]
    ptc_market = ptc_dd.loc[ptc_dd["outcome"].eq("market_or_subsidy")].iloc[0]
    ptc_unins = ptc_dd.loc[ptc_dd["outcome"].eq("uninsured")].iloc[0]
    work_target = work[
        work["arkansas"].eq(1) & work["age_30_49"].eq(1) & work["workreq_window"].eq(1)
    ]
    work_rows = 0 if work_target.empty else int(work_target.iloc[0]["rows"])
    work_persons = 0 if work_target.empty else int(work_target.iloc[0]["persons"])
    exp_lines = []
    for _, r in exp.sort_values(["implementation", "state"]).iterrows():
        exp_lines.append(
            f"- {r['state']} {r['implementation']}: persons={int(r['persons'])}, "
            f"pre={int(r['pre_persons'])}, post={int(r['post_persons'])}, "
            f"Medicaid weighted mean {r['medicaid_mean_w_pre']:.3f}->{r['medicaid_mean_w_post']:.3f}."
        )
    reins_top = reins.sort_values("direct_purchase_events", ascending=False).head(5)
    reins_lines = []
    for _, r in reins_top.iterrows():
        reins_lines.append(
            f"- {r['state']} {int(r['first_year'])}: persons={int(r['persons'])}, "
            f"direct-purchase events={int(r['direct_purchase_events'])}, "
            f"market/subsidy events={int(r['market_or_subsidy_events'])}."
        )

    report = f"""# New SIPP Idea Scan: Adult, Non-Unwinding Designs

## Bottom Line

The best next SIPP idea is **ACA enhanced premium tax credits and the 400% FPL subsidy cliff**.

Fast verdict: `{top['fast_verdict']}`.

The design is currently policy-relevant because enhanced premium tax credits removed the old
400% FPL cliff in 2021 and the cliff returned in 2026. SIPP 2018-2024 covers reference
years 2017-2023, so it can test the 2021 cliff-removal side now. It cannot test the 2026
return until newer SIPP data arrive.

## Why This Is The Leading Candidate

- It is adult-focused and avoids unwinding and child continuous eligibility.
- It has a sharp policy threshold: 400% FPL.
- The current parquet contains the needed monthly variables: income-to-poverty, insurance,
  direct purchase, marketplace/exchange/subsidy flags, age, state, employment, and medical
  utilization/spending.
- The SIPP contribution is not just Marketplace enrollment. It can observe people outside
  Marketplace administrative data: uninsured, direct-purchase, Medicaid/private transitions,
  employment, income volatility, and utilization.

## Fast Empirical Screen

Primary screen sample: adults 26-64, annual family income 300-500% FPL, reference years 2017-2023.

- Rows: {int(top['rows']):,}
- Persons: {int(top['persons']):,}
- Key support: {top['key_support']}
- Weighted DD screen, market/subsidy outcome: {ptc_market['dd_above400_minus_below400_post2021_minus_pre']:.4f}
- Weighted DD screen, uninsured outcome: {ptc_unins['dd_above400_minus_below400_post2021_minus_pre']:.4f}

This is not a final estimate. It is only enough to justify a proper next-stage
difference-in-discontinuities/RD-DID design with donut windows, bandwidth checks,
income-density diagnostics, and placebo thresholds.

## Main Testable Research Idea

**Question.** Did eliminating the ACA 400% FPL subsidy cliff change coverage and coverage
stability for middle-income adults who were just above the old eligibility cutoff?

**Design.** Difference-in-discontinuities around 400% FPL:

- running variable: `TFCYINCPOV`, where `4.0` equals 400% FPL;
- treated side: just above 400% FPL;
- comparison side: just below 400% FPL;
- pre period: 2017-2020;
- post period: 2021-2023;
- outcomes: direct-purchase/marketplace coverage, subsidized/exchange coverage,
  uninsured status, coverage loss, Medicaid/private transitions, utilization, and
  out-of-pocket medical spending;
- high-intensity heterogeneity: ages 50-64, because premiums and subsidy value are
  mechanically larger for older adults.

**Publication angle.** Existing public debate and many policy reports focus on Marketplace
enrollment and premiums. SIPP can ask whether a cliff-removal policy changes total insurance
coverage, off-Marketplace substitution, uninsured spells, and income-management behavior around
the cutoff.

## Candidate Ranking

| Rank | Candidate | Fast verdict | Fit with current parquet |
|---:|---|---|---|
"""
    for _, r in summary.sort_values("rank").iterrows():
        report += f"| {int(r['rank'])} | `{r['candidate']}` | {r['fast_verdict']} | {r['current_parquet_fit']} |\n"

    report += f"""

## Other Candidate Screens

### Arkansas Medicaid Work Requirements

Fast verdict: `FAST-NOGO-FOR-MAIN-PAPER`.

The policy is very current because national work requirements are back on the policy agenda,
but the historical SIPP event is too narrow. The target cell, Arkansas adults age 30-49 at
or below 138% FPL during the 2018-2019 implementation window, has:

- Rows: {work_rows:,}
- Persons: {work_persons:,}

This is useful for a robustness/sidebar exercise, not a top-economics main design.

### Late Medicaid Expansions

Fast verdict: `CONDITIONAL-BUT-LITERATURE-SATURATED`.

This is empirically feasible but not sufficiently novel unless paired with a sharper SIPP-only
mechanism such as income volatility, within-year coverage transitions, or labor-supply lock-in.

""" + "\n".join(exp_lines) + f"""

### State Reinsurance

Fast verdict: `BACKUP-ONLY`.

The policy is plausible but less sharp in SIPP because treatment intensity is state-premium
specific and individual-market cells are small. Largest treated-state support cells:

""" + "\n".join(reins_lines) + """

## Not Testable From The Uploaded Parquet Alone

- `family_glitch_fix`: needs employer offer/family premium and dependent-level eligibility.
- `public_charge_immigrant_chilling`: metadata has citizenship/nativity variables, but the current
  96-column parquet does not include them.
- `adult_postpartum_medicaid_extension`: metadata has pregnancy/birth variables, but the current
  parquet does not include them and the topic drifts toward maternal/child coverage.

## Next Stage

Build a dedicated `ptc_400fpl_cliff` pipeline:

1. Add polynomial/local-linear RD-DID estimates around 400% FPL, using `TFCYINCPOV`
   as the primary tax-year income proxy and `TFINCPOV` as a monthly-income sensitivity.
2. Run density and bunching diagnostics around 400% FPL before and after 2021.
3. Use bandwidths 300-500, 350-450, 375-425, and 390-410% FPL.
4. Use placebo thresholds at 300%, 350%, 450%, and 500% FPL.
5. Estimate age-intensity heterogeneity for 50-64 vs 26-49.
6. Separate outcomes into coverage, market/subsidy, uninsured spells, utilization, and OOP spending.
7. Do not use causal ML unless the RD-DID and placebo diagnostics pass.

## Source Checks Used For This Scan

- CMS: ARP expanded premium tax credits to marketplace consumers whose sticker
  premiums exceeded 8.5% of income and newly reached households above 400% FPL:
  https://www.cms.gov/newsroom/blog/inflation-reduction-act-tax-credits-improve-coverage-affordability-middle-income-americans
- IRS: ARPA temporarily eliminated the rule denying PTC when household income
  exceeded 400% FPL for 2021-2022:
  https://www.irs.gov/affordable-care-act/individuals-and-families/eligibility-for-the-premium-tax-credit
- KFF: enhanced PTCs expired at the end of 2025 and early 2026 enrollment drops
  were concentrated above the 400% FPL subsidy cliff:
  https://www.kff.org/affordable-care-act/what-we-know-so-far-about-2026-aca-marketplace-enrollment-premiums-and-deductibles/
- KFF: current Medicaid expansion implementation dates:
  https://www.kff.org/affordable-care-act/state-indicator/state-activity-around-expanding-medicaid-under-the-affordable-care-act/
- KFF: 2025 federal law work requirements begin January 1, 2027 for ACA expansion
  adults and certain 1115 waiver enrollees:
  https://www.kff.org/medicaid/medicaid-work-requirements-tracker-overview/
- KFF: Arkansas 2018 work/reporting requirements applied first to ages 30-49:
  https://www.kff.org/medicaid/state-data-for-medicaid-work-requirements-in-arkansas/
- CMS: Section 1332 state innovation waivers are the official policy route for
  state reinsurance programs:
  https://www.cms.gov/marketplace/states/section-1332-state-innovation-waivers

## Output Tables

- `result/idea_scan/idea_screen_candidate_summary.csv`
- `result/idea_scan/idea_screen_variable_availability.csv`
- `result/idea_scan/idea_screen_ptc_dd.csv`
- `result/idea_scan/idea_screen_ptc_bins.csv`
- `result/idea_scan/idea_screen_work_requirements.csv`
- `result/idea_scan/idea_screen_late_expansion.csv`
- `result/idea_scan/idea_screen_reinsurance.csv`
"""
    REPORT.write_text(report, encoding="utf-8")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    df = read_panel()
    availability = variable_availability(df)
    ptc_dd, ptc_bins = screen_ptc(df)
    work = screen_work_requirements(df)
    exp = screen_late_expansions(df)
    reins = screen_reinsurance(df)
    summary = build_candidate_summary(df, availability, ptc_dd, work, exp, reins)

    availability.to_csv(OUT / "idea_screen_variable_availability.csv", index=False)
    ptc_dd.to_csv(OUT / "idea_screen_ptc_dd.csv", index=False)
    ptc_bins.to_csv(OUT / "idea_screen_ptc_bins.csv", index=False)
    work.to_csv(OUT / "idea_screen_work_requirements.csv", index=False)
    exp.to_csv(OUT / "idea_screen_late_expansion.csv", index=False)
    reins.to_csv(OUT / "idea_screen_reinsurance.csv", index=False)
    summary.to_csv(OUT / "idea_screen_candidate_summary.csv", index=False)
    (OUT / "idea_screen_manifest.json").write_text(
        json.dumps(
            {
                "panel": str(PANEL),
                "metadata": str(METADATA),
                "rows": int(len(df)),
                "persons": persons(df["person_id"]),
                "outputs": sorted(p.name for p in OUT.glob("idea_screen_*")),
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    write_report(summary, ptc_dd, ptc_bins, work, exp, reins)
    print(f"Wrote idea scan outputs to {OUT}")
    print(f"Wrote report to {REPORT}")


if __name__ == "__main__":
    main()
