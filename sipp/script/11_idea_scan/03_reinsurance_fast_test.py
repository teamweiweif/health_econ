from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
PANEL = ROOT / "data" / "analysis_ready" / "sipp_2018_2024_person_month_panel.parquet"
OUT = ROOT / "result" / "idea_scan"
REPORT = ROOT / "report" / "12_reinsurance_fast_test.md"


STATE = {
    "AK": "02",
    "CO": "08",
    "DE": "10",
    "GA": "13",
    "ME": "23",
    "MD": "24",
    "MN": "27",
    "MT": "30",
    "ND": "38",
    "NH": "33",
    "NJ": "34",
    "OR": "41",
    "PA": "42",
    "VA": "51",
    "WI": "55",
}


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


def yes(s: pd.Series) -> pd.Series:
    return s.eq(1)


def clean_weight(df: pd.DataFrame) -> pd.Series:
    w = pd.to_numeric(df.get("WPFINWGT"), errors="coerce")
    return w.where(w.gt(0))


def persons(s: pd.Series) -> int:
    return int(s.dropna().nunique())


def wmean(y: pd.Series, w: pd.Series) -> float:
    mask = y.notna() & w.notna() & (w > 0)
    if not mask.any():
        return np.nan
    return float(np.average(y[mask].astype(float), weights=w[mask].astype(float)))


def wls_hc1(y: np.ndarray, x: np.ndarray, w: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    mask = np.isfinite(y) & np.isfinite(w) & (w > 0) & np.all(np.isfinite(x), axis=1)
    y = y[mask]
    x = x[mask]
    w = w[mask]
    if len(y) <= x.shape[1] + 5:
        return np.full(x.shape[1], np.nan), np.full(x.shape[1], np.nan)
    sw = np.sqrt(w / np.nanmean(w))
    xw = x * sw[:, None]
    yw = y * sw
    inv = np.linalg.pinv(xw.T @ xw)
    beta = inv @ (xw.T @ yw)
    resid = yw - xw @ beta
    meat = xw.T @ ((resid**2)[:, None] * xw)
    n, k = xw.shape
    cov = (n / max(n - k, 1)) * inv @ meat @ inv
    return beta, np.sqrt(np.diag(cov))


def read_panel() -> pd.DataFrame:
    cols = [
        "person_id",
        "reference_year",
        "reference_month",
        "state_fips",
        "TAGE",
        "WPFINWGT",
        "TSSSAMT",
        "RHLTHMTH",
        "RPRITYPE2",
        "RMARKTPLACE",
        "RPRIMTH",
        "EPRIEXCH1",
        "EPRIEXCH2",
        "EPRISUBS1",
        "EPRISUBS2",
        "EMDEXCH",
        "EMDSUBS",
        "TFCYINCPOV",
        "TMDPAY",
        "TVISDOC",
    ]
    df = pd.read_parquet(PANEL, columns=cols)
    df["state_fips"] = df["state_fips"].astype(str).str.zfill(2)
    df["weight"] = clean_weight(df)
    df["age"] = pd.to_numeric(df["TAGE"], errors="coerce")
    df["annual_fpl"] = pd.to_numeric(df["TFCYINCPOV"], errors="coerce")
    df.loc[(df["annual_fpl"] < 0) | (df["annual_fpl"] > 20), "annual_fpl"] = np.nan
    df["adult_26_64"] = df["age"].between(26, 64, inclusive="both")
    df["above400"] = df["annual_fpl"].gt(4.0)
    start_by_fips = {STATE[st]: year for st, year in REINSURANCE_START.items()}
    df["reinsurance_start_year"] = df["state_fips"].map(start_by_fips)
    df["reinsurance_state"] = df["reinsurance_start_year"].notna()
    df["reinsurance_active"] = df["reinsurance_state"] & df["reference_year"].ge(df["reinsurance_start_year"])
    df["direct_purchase"] = yes(df["RPRITYPE2"]) | yes(df["RMARKTPLACE"])
    df["marketplace"] = yes(df["RMARKTPLACE"]) | yes(df["EPRIEXCH1"]) | yes(df["EPRIEXCH2"]) | yes(df["EMDEXCH"])
    df["subsidized_private"] = yes(df["EPRISUBS1"]) | yes(df["EPRISUBS2"]) | yes(df["EMDSUBS"])
    df["market_or_subsidy"] = df["marketplace"] | df["subsidized_private"]
    df["uninsured"] = df["RHLTHMTH"].eq(2)
    df["any_coverage"] = yes(df["RHLTHMTH"])
    df["private"] = yes(df["RPRIMTH"])
    df["oop_any"] = pd.to_numeric(df["TMDPAY"], errors="coerce").gt(0)
    df["doctor_any"] = pd.to_numeric(df["TVISDOC"], errors="coerce").gt(0)
    return df


def aggregate(df: pd.DataFrame, outcomes: list[str]) -> pd.DataFrame:
    sample = df[
        df["adult_26_64"]
        & df["annual_fpl"].between(1.5, 6.0, inclusive="both")
        & df["reference_year"].between(2017, 2023)
    ].copy()
    sample["above400"] = sample["above400"].astype(int)
    sample["reinsurance_active"] = sample["reinsurance_active"].astype(int)
    sample["reinsurance_state"] = sample["reinsurance_state"].astype(int)
    group_cols = ["state_fips", "reference_year", "reference_month", "above400", "reinsurance_active", "reinsurance_state"]
    rows = []
    for keys, g in sample.groupby(group_cols, observed=True):
        row = dict(zip(group_cols, keys))
        row["rows"] = int(len(g))
        row["persons"] = persons(g["person_id"])
        row["weight"] = float(g["weight"].sum())
        for out in outcomes:
            row[out] = wmean(g[out], g["weight"])
            row[f"{out}_events"] = int(g[out].sum())
        rows.append(row)
    return pd.DataFrame(rows)


def estimate(cell: pd.DataFrame, outcome: str, label: str) -> dict:
    work = cell.copy()
    work["active_x_above400"] = work["reinsurance_active"] * work["above400"]
    state_dummies = pd.get_dummies(work["state_fips"], prefix="st", drop_first=True, dtype=float)
    year_dummies = pd.get_dummies(work["reference_year"].astype(str), prefix="yr", drop_first=True, dtype=float)
    month_dummies = pd.get_dummies(work["reference_month"].astype(str), prefix="mo", drop_first=True, dtype=float)
    x = pd.concat(
        [
            pd.Series(1.0, index=work.index, name="const"),
            work[["active_x_above400", "reinsurance_active", "above400"]],
            state_dummies,
            year_dummies,
            month_dummies,
        ],
        axis=1,
    )
    beta, se = wls_hc1(work[outcome].to_numpy(float), x.to_numpy(float), work["weight"].to_numpy(float))
    coef_idx = list(x.columns).index("active_x_above400")
    treated = work[work["active_x_above400"].eq(1)]
    untreated = work[work["active_x_above400"].eq(0)]
    return {
        "sample": label,
        "outcome": outcome,
        "coef_active_x_above400": float(beta[coef_idx]),
        "se_hc1": float(se[coef_idx]),
        "t_stat": float(beta[coef_idx] / se[coef_idx]) if se[coef_idx] > 0 else np.nan,
        "cells": int(len(work)),
        "treated_cells": int(len(treated)),
        "treated_weight": float(treated["weight"].sum()),
        "treated_event_count": int(treated[f"{outcome}_events"].sum()),
        "weighted_mean_treated": wmean(treated[outcome], treated["weight"]),
        "weighted_mean_untreated": wmean(untreated[outcome], untreated["weight"]),
    }


def support_by_state(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for st, start in REINSURANCE_START.items():
        fips = STATE[st]
        sample = df[
            df["adult_26_64"]
            & df["state_fips"].eq(fips)
            & df["annual_fpl"].between(1.5, 6.0, inclusive="both")
            & df["reference_year"].between(max(2017, start - 1), min(2023, start + 1))
        ]
        rows.append(
            {
                "state": st,
                "start_year": start,
                "rows": int(len(sample)),
                "persons": persons(sample["person_id"]),
                "above400_persons": persons(sample.loc[sample["above400"], "person_id"]),
                "direct_purchase_events": int(sample["direct_purchase"].sum()),
                "market_or_subsidy_events": int(sample["market_or_subsidy"].sum()),
                "uninsured_events": int(sample["uninsured"].sum()),
            }
        )
    return pd.DataFrame(rows)


def write_report(est: pd.DataFrame, support: pd.DataFrame) -> None:
    main = est[est["sample"].eq("all_150_600_fpl")].copy()
    cols = ["outcome", "coef_active_x_above400", "se_hc1", "t_stat", "treated_cells", "treated_event_count"]
    lines = ["| " + " | ".join(cols) + " |", "|" + "|".join(["---"] * len(cols)) + "|"]
    for _, r in main.sort_values("outcome").iterrows():
        vals = []
        for c in cols:
            v = r[c]
            vals.append(f"{v:.4f}" if isinstance(v, float) else str(v))
        lines.append("| " + " | ".join(vals) + " |")
    top_states = support.sort_values("direct_purchase_events", ascending=False).head(6)
    state_lines = []
    for _, r in top_states.iterrows():
        state_lines.append(
            f"- {r['state']} {int(r['start_year'])}: persons={int(r['persons'])}, "
            f"above400 persons={int(r['above400_persons'])}, direct-purchase events={int(r['direct_purchase_events'])}, "
            f"market/subsidy events={int(r['market_or_subsidy_events'])}."
        )
    market = main.loc[main["outcome"].eq("direct_purchase")].iloc[0]
    if market["treated_event_count"] >= 1000 and market["coef_active_x_above400"] > 0 and abs(market["t_stat"]) >= 1.5:
        verdict = "PROMISING-SIGNAL"
    elif market["treated_event_count"] >= 1000:
        verdict = "SUPPORT-YES-SIGNAL-WEAK"
    else:
        verdict = "SUPPORT-THIN"
    report = f"""# State Reinsurance Fast DDD Test

## Verdict

`{verdict}`

This design has genuine state-policy variation and targets the adult individual market, but the
current fast cell-level DDD is not yet a clean top-field design. It remains a backup or a possible
component of a broader ACA affordability paper.

## Design Tested

Sample: adults 26-64, annual family income 150-600% FPL, reference years 2017-2023.

Treatment intensity: state reinsurance active x income above 400% FPL. The idea is that
reinsurance lowers gross individual-market premiums and should matter more for people above
the PTC eligibility cliff or otherwise weakly subsidized.

Model: weighted state-month-income-group cell regression with state, year, and month fixed effects.
Coefficient shown is `active x above400`.

{chr(10).join(lines)}

## Largest Treated-State Support Cells

{chr(10).join(state_lines)}

## Interpretation

- Support is adequate for descriptive and secondary analysis.
- The design is less sharp than the 400% FPL PTC cliff because reinsurance treatment intensity
  depends on state premium reductions, insurer pricing, and pass-through funding.
- A stronger version would merge official state-year premium impacts or county benchmark premiums
  and use continuous treatment intensity rather than a binary adoption indicator.

## Outputs

- `result/idea_scan/reinsurance_ddd_fast_estimates.csv`
- `result/idea_scan/reinsurance_support_by_state.csv`
"""
    REPORT.write_text(report, encoding="utf-8")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    outcomes = ["direct_purchase", "market_or_subsidy", "uninsured", "any_coverage", "private", "oop_any", "doctor_any"]
    df = read_panel()
    cell = aggregate(df, outcomes)
    estimates = [estimate(cell, out, "all_150_600_fpl") for out in outcomes]
    est = pd.DataFrame(estimates)
    support = support_by_state(df)
    cell.to_csv(OUT / "reinsurance_state_month_cells.csv", index=False)
    est.to_csv(OUT / "reinsurance_ddd_fast_estimates.csv", index=False)
    support.to_csv(OUT / "reinsurance_support_by_state.csv", index=False)
    write_report(est, support)
    print(f"Wrote report to {REPORT}")


if __name__ == "__main__":
    main()
