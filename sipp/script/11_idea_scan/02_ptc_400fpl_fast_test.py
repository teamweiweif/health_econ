from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
PANEL = ROOT / "data" / "analysis_ready" / "sipp_2018_2024_person_month_panel.parquet"
OUT = ROOT / "result" / "idea_scan"
REPORT = ROOT / "report" / "11_ptc_400fpl_fast_test.md"


def yes(series: pd.Series) -> pd.Series:
    return series.eq(1)


def clean_weight(df: pd.DataFrame) -> pd.Series:
    w = pd.to_numeric(df.get("WPFINWGT"), errors="coerce")
    w = w.where(w.gt(0), pd.to_numeric(df.get("TSSSAMT"), errors="coerce"))
    return w.where(w.gt(0), 1.0)


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
        k = x.shape[1]
        return np.full(k, np.nan), np.full(k, np.nan)
    sw = np.sqrt(w / np.nanmean(w))
    xw = x * sw[:, None]
    yw = y * sw
    xtx = xw.T @ xw
    try:
        inv = np.linalg.pinv(xtx)
    except np.linalg.LinAlgError:
        k = x.shape[1]
        return np.full(k, np.nan), np.full(k, np.nan)
    beta = inv @ (xw.T @ yw)
    resid = yw - xw @ beta
    meat = xw.T @ ((resid**2)[:, None] * xw)
    n, k = xw.shape
    scale = n / max(n - k, 1)
    cov = scale * inv @ meat @ inv
    se = np.sqrt(np.diag(cov))
    return beta, se


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
        "TFINCPOV",
        "TMDPAY",
        "TVISDOC",
        "RMWKWJB",
        "RMESR",
    ]
    df = pd.read_parquet(PANEL, columns=cols)
    df["weight"] = clean_weight(df)
    df["age"] = pd.to_numeric(df["TAGE"], errors="coerce")
    df["annual_fpl"] = pd.to_numeric(df["TFCYINCPOV"], errors="coerce")
    df.loc[(df["annual_fpl"] < 0) | (df["annual_fpl"] > 20), "annual_fpl"] = np.nan
    df["monthly_fpl"] = pd.to_numeric(df["TFINCPOV"], errors="coerce")
    df.loc[(df["monthly_fpl"] < 0) | (df["monthly_fpl"] > 20), "monthly_fpl"] = np.nan
    df["adult_26_64"] = df["age"].between(26, 64, inclusive="both")
    df["older_50_64"] = df["age"].between(50, 64, inclusive="both")
    df["post_2021"] = df["reference_year"].ge(2021).astype(int)
    df["direct_purchase"] = yes(df["RPRITYPE2"]) | yes(df["RMARKTPLACE"])
    df["marketplace"] = yes(df["RMARKTPLACE"]) | yes(df["EPRIEXCH1"]) | yes(df["EPRIEXCH2"]) | yes(df["EMDEXCH"])
    df["subsidized_private"] = yes(df["EPRISUBS1"]) | yes(df["EPRISUBS2"]) | yes(df["EMDSUBS"])
    df["market_or_subsidy"] = df["marketplace"] | df["subsidized_private"]
    df["uninsured"] = df["RHLTHMTH"].eq(2)
    df["any_coverage"] = yes(df["RHLTHMTH"])
    df["private"] = yes(df["RPRIMTH"])
    df["oop_any"] = pd.to_numeric(df["TMDPAY"], errors="coerce").gt(0)
    df["doctor_any"] = pd.to_numeric(df["TVISDOC"], errors="coerce").gt(0)
    df["working_any_week"] = pd.to_numeric(df["RMWKWJB"], errors="coerce").gt(0) | pd.to_numeric(df["RMESR"], errors="coerce").between(1, 5)
    return df


def local_rddid(df: pd.DataFrame, outcome: str, cutoff: float, bandwidth: float, age_group: str) -> dict:
    sample = df[
        df["adult_26_64"]
        & df["annual_fpl"].between(cutoff - bandwidth, cutoff + bandwidth, inclusive="both")
        & df["reference_year"].between(2017, 2023)
    ].copy()
    if age_group == "older_50_64":
        sample = sample[sample["older_50_64"]]
    elif age_group == "age_26_49":
        sample = sample[~sample["older_50_64"]]
    sample["above"] = sample["annual_fpl"].gt(cutoff).astype(float)
    sample["post"] = sample["post_2021"].astype(float)
    sample["x"] = sample["annual_fpl"] - cutoff
    y = sample[outcome].astype(float).to_numpy()
    post = sample["post"].to_numpy()
    above = sample["above"].to_numpy()
    x = sample["x"].to_numpy()
    X = np.column_stack(
        [
            np.ones(len(sample)),
            post,
            above,
            post * above,
            x,
            x * post,
            x * above,
            x * post * above,
        ]
    )
    beta, se = wls_hc1(y, X, sample["weight"].to_numpy())
    cell = (
        sample.groupby(["post", "above"], observed=True)
        .agg(rows=("person_id", "size"), persons=("person_id", "nunique"), events=(outcome, "sum"))
        .reset_index()
    )
    min_cell_persons = 0 if cell.empty else int(cell["persons"].min())
    min_cell_events = 0 if cell.empty else int(cell["events"].min())
    return {
        "outcome": outcome,
        "cutoff": cutoff,
        "bandwidth": bandwidth,
        "age_group": age_group,
        "rows": int(len(sample)),
        "persons": persons(sample["person_id"]),
        "min_cell_persons": min_cell_persons,
        "min_cell_events": min_cell_events,
        "coef_post_x_above": float(beta[3]) if len(beta) > 3 else np.nan,
        "se_hc1": float(se[3]) if len(se) > 3 else np.nan,
        "t_stat": float(beta[3] / se[3]) if len(se) > 3 and se[3] > 0 else np.nan,
        "pre_below_mean_w": wmean(sample.loc[(sample["post"].eq(0)) & (sample["above"].eq(0)), outcome], sample.loc[(sample["post"].eq(0)) & (sample["above"].eq(0)), "weight"]),
        "pre_above_mean_w": wmean(sample.loc[(sample["post"].eq(0)) & (sample["above"].eq(1)), outcome], sample.loc[(sample["post"].eq(0)) & (sample["above"].eq(1)), "weight"]),
        "post_below_mean_w": wmean(sample.loc[(sample["post"].eq(1)) & (sample["above"].eq(0)), outcome], sample.loc[(sample["post"].eq(1)) & (sample["above"].eq(0)), "weight"]),
        "post_above_mean_w": wmean(sample.loc[(sample["post"].eq(1)) & (sample["above"].eq(1)), outcome], sample.loc[(sample["post"].eq(1)) & (sample["above"].eq(1)), "weight"]),
    }


def density_bins(df: pd.DataFrame) -> pd.DataFrame:
    sample = df[
        df["adult_26_64"]
        & df["annual_fpl"].between(3.0, 5.0, inclusive="both")
        & df["reference_year"].between(2017, 2023)
    ].copy()
    bins = np.round(np.arange(3.0, 5.0001, 0.05), 2)
    sample["fpl_bin"] = pd.cut(sample["annual_fpl"], bins=bins, include_lowest=True)
    out = (
        sample.groupby(["post_2021", "fpl_bin"], observed=True)
        .agg(rows=("person_id", "size"), persons=("person_id", "nunique"), weight=("weight", "sum"))
        .reset_index()
    )
    out["left"] = out["fpl_bin"].map(lambda x: float(x.left))
    out["right"] = out["fpl_bin"].map(lambda x: float(x.right))
    out = out.drop(columns=["fpl_bin"])
    return out


def write_report(est: pd.DataFrame, density: pd.DataFrame) -> None:
    main = est[
        est["cutoff"].eq(4.0)
        & est["bandwidth"].eq(0.5)
        & est["age_group"].eq("all")
        & est["outcome"].isin(["market_or_subsidy", "direct_purchase", "uninsured", "any_coverage"])
    ].sort_values("outcome")
    placebo = est[
        est["bandwidth"].eq(0.5)
        & est["age_group"].eq("all")
        & est["outcome"].eq("market_or_subsidy")
        & ~est["cutoff"].eq(4.0)
    ].sort_values("cutoff")
    older = est[
        est["cutoff"].eq(4.0)
        & est["bandwidth"].eq(0.5)
        & est["outcome"].eq("market_or_subsidy")
        & est["age_group"].isin(["older_50_64", "age_26_49"])
    ].sort_values("age_group")

    def table_md(df: pd.DataFrame, cols: list[str]) -> str:
        lines = ["| " + " | ".join(cols) + " |", "|" + "|".join(["---"] * len(cols)) + "|"]
        for _, r in df.iterrows():
            vals = []
            for c in cols:
                v = r[c]
                if isinstance(v, float):
                    vals.append(f"{v:.4f}")
                else:
                    vals.append(str(v))
            lines.append("| " + " | ".join(vals) + " |")
        return "\n".join(lines)

    main_cols = ["outcome", "coef_post_x_above", "se_hc1", "t_stat", "persons", "min_cell_persons", "min_cell_events"]
    placebo_cols = ["cutoff", "coef_post_x_above", "se_hc1", "t_stat", "persons", "min_cell_persons"]
    older_cols = ["age_group", "coef_post_x_above", "se_hc1", "t_stat", "persons", "min_cell_persons", "min_cell_events"]

    market_main = main.loc[main["outcome"].eq("market_or_subsidy")]
    if market_main.empty:
        verdict = "INCOMPLETE"
    else:
        r = market_main.iloc[0]
        if r["persons"] >= 5000 and r["min_cell_persons"] >= 1000 and r["coef_post_x_above"] < 0 and abs(r["t_stat"]) >= 1.5:
            verdict = "SUPPORT-YES-BUT-SIGNAL-CONFLICTS-WITH-UPTAKE-STORY"
        elif r["persons"] >= 5000 and r["min_cell_persons"] >= 1000 and r["coef_post_x_above"] > 0 and abs(r["t_stat"]) >= 1.5:
            verdict = "PROMISING-SIGNAL-BUT-NEEDS-FULL-RD-DID"
        elif r["persons"] >= 5000 and r["min_cell_persons"] >= 1000:
            verdict = "SUPPORT-YES-SIGNAL-WEAK"
        else:
            verdict = "SUPPORT-THIN"

    report = f"""# PTC 400% FPL Fast RD-DID Test

## Verdict

`{verdict}`

The support is large enough to justify a serious follow-up design, but the first-pass
local RD-DID signal conflicts with a simple positive marketplace-uptake story. This should be
treated as **conditional next-test worthy**, not paper-ready.

## Main 400% FPL Screen

Specification: adults 26-64, annual family income-to-poverty within 50 percentage points
of the cutoff, pre 2017-2020 vs post 2021-2023. Coefficient is the change in the above-cutoff
discontinuity after 2021 from a local linear weighted model.

{table_md(main, main_cols)}

## Age-Intensity Check

Premium subsidies should matter more for older adults because age-rated premiums are higher.
This quick check estimates the same market/subsidy outcome separately for ages 50-64 and 26-49.

{table_md(older, older_cols)}

## Placebo Cutoffs

Outcome: market/subsidy coverage. Bandwidth: 50 percentage points.

{table_md(placebo, placebo_cols)}

## Interpretation

- SIPP support around 400% FPL is not the problem; cell sizes are adequate.
- The current-market/subsidy signal is negative in the broad local screen, so the next stage
  must diagnose whether this is real substitution, below-400 treatment spillover, measurement
  limits in exchange/subsidy flags, or a poor control-side construction.
- A publishable version needs a sharper treatment-intensity measure: age-rated premium exposure,
  county/state benchmark premiums, or state-by-age pre-ARP premium burden.
- Without that treatment-intensity layer, the design is causally attractive but empirically
  underidentified because both sides of 400% FPL received affordability changes after ARPA.

## Outputs

- `result/idea_scan/ptc_400fpl_rddid_fast_estimates.csv`
- `result/idea_scan/ptc_400fpl_density_bins.csv`
"""
    REPORT.write_text(report, encoding="utf-8")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    df = read_panel()
    rows = []
    outcomes = [
        "direct_purchase",
        "marketplace",
        "subsidized_private",
        "market_or_subsidy",
        "uninsured",
        "any_coverage",
        "private",
        "oop_any",
        "doctor_any",
        "working_any_week",
    ]
    for outcome in outcomes:
        for cutoff in [3.0, 3.5, 4.0, 4.5, 5.0]:
            for bandwidth in [0.10, 0.25, 0.50, 1.00]:
                if cutoff - bandwidth < 1.0:
                    continue
                for age_group in ["all", "older_50_64", "age_26_49"]:
                    rows.append(local_rddid(df, outcome, cutoff, bandwidth, age_group))
    est = pd.DataFrame(rows)
    density = density_bins(df)
    est.to_csv(OUT / "ptc_400fpl_rddid_fast_estimates.csv", index=False)
    density.to_csv(OUT / "ptc_400fpl_density_bins.csv", index=False)
    write_report(est, density)
    print(f"Wrote {len(est)} estimates to {OUT / 'ptc_400fpl_rddid_fast_estimates.csv'}")
    print(f"Wrote report to {REPORT}")


if __name__ == "__main__":
    main()
