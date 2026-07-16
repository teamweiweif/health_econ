from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
PANEL = ROOT / "data" / "analysis_ready" / "sipp_2018_2024_person_month_panel.parquet"
POLICY = ROOT / "result" / "idea_scan" / "ptc_premium_policy_state_year.csv"
OUT = ROOT / "result" / "idea_scan"
REPORT = ROOT / "report" / "21_ptc_premium_event_test.md"

FIPS_TO_STATE = {
    "01": "AL", "02": "AK", "04": "AZ", "05": "AR", "06": "CA", "08": "CO",
    "09": "CT", "10": "DE", "11": "DC", "12": "FL", "13": "GA", "15": "HI",
    "16": "ID", "17": "IL", "18": "IN", "19": "IA", "20": "KS", "21": "KY",
    "22": "LA", "23": "ME", "24": "MD", "25": "MA", "26": "MI", "27": "MN",
    "28": "MS", "29": "MO", "30": "MT", "31": "NE", "32": "NV", "33": "NH",
    "34": "NJ", "35": "NM", "36": "NY", "37": "NC", "38": "ND", "39": "OH",
    "40": "OK", "41": "OR", "42": "PA", "44": "RI", "45": "SC", "46": "SD",
    "47": "TN", "48": "TX", "49": "UT", "50": "VT", "51": "VA", "53": "WA",
    "54": "WV", "55": "WI", "56": "WY",
}


def yes(s: pd.Series) -> pd.Series:
    return s.eq(1)


def persons(s: pd.Series) -> int:
    return int(s.dropna().nunique())


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
    n, k = x.shape
    cov = (n / max(n - k, 1)) * inv @ meat @ inv
    return beta, np.sqrt(np.diag(cov))


def read_data() -> pd.DataFrame:
    policy = pd.read_csv(POLICY)
    cols = [
        "person_id", "reference_year", "state_fips", "TAGE", "WPFINWGT", "TSSSAMT",
        "RHLTHMTH", "RPRITYPE2", "RMARKTPLACE", "RPRIMTH", "EPRIEXCH1", "EPRIEXCH2",
        "EPRISUBS1", "EPRISUBS2", "EMDEXCH", "EMDSUBS", "TFCYINCPOV", "TMDPAY",
        "TVISDOC",
    ]
    df = pd.read_parquet(PANEL, columns=cols)
    df["state_fips"] = df["state_fips"].astype(str).str.zfill(2)
    df["state"] = df["state_fips"].map(FIPS_TO_STATE)
    df = df[df["reference_year"].between(2018, 2023)].copy()
    df = df.merge(policy, on=["reference_year", "state"], how="left")
    df = df[df["pre_2021_age60_excess_burden"].notna()].copy()
    df["age"] = pd.to_numeric(df["TAGE"], errors="coerce")
    df["annual_fpl"] = pd.to_numeric(df["TFCYINCPOV"], errors="coerce")
    df.loc[(df["annual_fpl"] < 0) | (df["annual_fpl"] > 20), "annual_fpl"] = np.nan
    df = df[df["age"].between(26, 64, inclusive="both") & df["annual_fpl"].between(3.0, 5.0, inclusive="both")].copy()
    df["above400"] = df["annual_fpl"].gt(4.0).astype(int)
    df["highpremium"] = df["high_pre_premium_burden"].fillna(0).astype(int)
    df["above_x_high"] = df["above400"] * df["highpremium"]
    df["weight"] = pd.to_numeric(df["WPFINWGT"], errors="coerce")
    df["weight"] = df["weight"].where(df["weight"].gt(0))
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


def estimate(df: pd.DataFrame, outcome: str) -> pd.DataFrame:
    sample = df.copy()
    interaction_cols = []
    for year in [2018, 2019, 2021, 2022, 2023]:
        col = f"above_high_x_{year}"
        sample[col] = sample["above_x_high"] * sample["reference_year"].eq(year).astype(int)
        interaction_cols.append(col)
    state_fe = pd.get_dummies(sample["state"], prefix="st", drop_first=True, dtype=float)
    year_fe = pd.get_dummies(sample["reference_year"].astype(str), prefix="yr", drop_first=True, dtype=float)
    x = pd.concat(
        [
            pd.Series(1.0, index=sample.index, name="const"),
            sample[interaction_cols + ["above_x_high", "above400", "highpremium"]],
            state_fe,
            year_fe,
        ],
        axis=1,
    )
    beta, se = wls_hc1(sample[outcome].astype(float).to_numpy(), x.to_numpy(float), sample["weight"].to_numpy(float))
    rows = []
    for year, col in zip([2018, 2019, 2021, 2022, 2023], interaction_cols):
        idx = list(x.columns).index(col)
        rows.append(
            {
                "outcome": outcome,
                "year": year,
                "reference_year": 2020,
                "coef_above400_highpremium_vs_2020": float(beta[idx]),
                "se_hc1": float(se[idx]),
                "t_stat": float(beta[idx] / se[idx]) if se[idx] > 0 else np.nan,
                "persons": persons(sample["person_id"]),
                "states": int(sample["state"].nunique()),
            }
        )
    return pd.DataFrame(rows)


def support(df: pd.DataFrame) -> pd.DataFrame:
    return df.groupby(["reference_year", "above400", "highpremium"], observed=True).agg(
        rows=("person_id", "size"),
        persons=("person_id", "nunique"),
        market_events=("market_or_subsidy", "sum"),
        uninsured_events=("uninsured", "sum"),
        states=("state", "nunique"),
    ).reset_index()


def write_report(est: pd.DataFrame, supp: pd.DataFrame) -> None:
    keep = est[est["outcome"].isin(["market_or_subsidy", "uninsured", "any_coverage", "direct_purchase", "oop_any"])].copy()
    cols = ["outcome", "year", "coef_above400_highpremium_vs_2020", "se_hc1", "t_stat"]
    lines = ["| " + " | ".join(cols) + " |", "|" + "|".join(["---"] * len(cols)) + "|"]
    for _, r in keep.sort_values(["outcome", "year"]).iterrows():
        vals = []
        for c in cols:
            v = r[c]
            vals.append(f"{v:.4f}" if isinstance(v, float) else str(v))
        lines.append("| " + " | ".join(vals) + " |")

    main = keep[(keep["outcome"].eq("market_or_subsidy"))]
    pre = main[main["year"].isin([2018, 2019])]
    post = main[main["year"].isin([2021, 2022, 2023])]
    if pre["t_stat"].abs().max() > 1.96:
        verdict = "PRETREND-CONCERN"
    elif post["coef_above400_highpremium_vs_2020"].mean() > 0:
        verdict = "DYNAMIC-SIGNAL-SUPPORTS-PREMIUM-INTENSITY-BUT-OUTCOME-MIXED"
    else:
        verdict = "NO-DYNAMIC-SUPPORT"

    report = f"""# PTC Premium-Intensity Dynamic Check

## Verdict

`{verdict}`

This checks whether the above-400 x high-premium signal is concentrated after ARPA rather than
being a pre-existing difference. The omitted reference year is 2020.

## Dynamic Coefficients

{chr(10).join(lines)}

## Interpretation

- A clean PTC story would show weak pre-2021 lead coefficients and coherent post-2021 changes:
  more marketplace/subsidized coverage and less uninsured or more any coverage.
- If market/subsidy rises but uninsured also rises, the idea remains promising but not clean.
- These are still screening standard errors, not final clustered inference.

## Outputs

- `result/idea_scan/ptc_premium_event_estimates.csv`
- `result/idea_scan/ptc_premium_event_support.csv`
"""
    REPORT.write_text(report, encoding="utf-8")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    df = read_data()
    outcomes = ["direct_purchase", "market_or_subsidy", "uninsured", "any_coverage", "private", "oop_any", "doctor_any"]
    est = pd.concat([estimate(df, outcome) for outcome in outcomes], ignore_index=True)
    supp = support(df)
    est.to_csv(OUT / "ptc_premium_event_estimates.csv", index=False)
    supp.to_csv(OUT / "ptc_premium_event_support.csv", index=False)
    write_report(est, supp)
    print(f"Wrote report to {REPORT}")


if __name__ == "__main__":
    main()
