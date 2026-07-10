from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
PANEL = ROOT / "data" / "analysis_ready" / "sipp_2018_2024_person_month_panel.parquet"
OUT = ROOT / "result" / "idea_scan"
REPORT = ROOT / "report" / "42_washington_wftc_fast_test.md"


SOURCES = [
    "Washington Working Families Tax Credit official site: https://workingfamiliescredit.wa.gov/",
    "Washington Working Families Tax Credit eligibility page: https://workingfamiliescredit.wa.gov/eligibility",
    "Washington Department of Revenue WFTC application window release: https://dor.wa.gov/about/news-releases/2026/working-families-tax-credit-application-window-opens-feb-1",
    "NCSL Earned Income Tax Credit Overview: https://www.ncsl.org/human-services/earned-income-tax-credit-overview",
]


STATE_NAMES = {
    "06": "California",
    "08": "Colorado",
    "16": "Idaho",
    "30": "Montana",
    "41": "Oregon",
    "53": "Washington",
}
REGIONAL_CONTROL_STATES = set(STATE_NAMES)
WASHINGTON = "53"


def yes(s: pd.Series) -> pd.Series:
    return s.eq(1)


def bounded_numeric(s: pd.Series, lo: float, hi: float) -> pd.Series:
    out = pd.to_numeric(s, errors="coerce")
    return out.where(out.between(lo, hi, inclusive="both"))


def clean_weight(df: pd.DataFrame) -> pd.Series:
    w = pd.to_numeric(df.get("WPFINWGT"), errors="coerce")
    w = w.where(w.gt(0), pd.to_numeric(df.get("TSSSAMT"), errors="coerce"))
    return w.where(w.gt(0), 1.0)


def wmean(y: pd.Series, w: pd.Series) -> float:
    mask = y.notna() & w.notna() & (w > 0)
    if not mask.any():
        return np.nan
    return float(np.average(y[mask].astype(float), weights=w[mask].astype(float)))


def wls_hc1(y: np.ndarray, x: np.ndarray, w: np.ndarray) -> tuple[np.ndarray, np.ndarray, int]:
    mask = np.isfinite(y) & np.isfinite(w) & (w > 0) & np.all(np.isfinite(x), axis=1)
    y = y[mask]
    x = x[mask]
    w = w[mask]
    if len(y) <= x.shape[1] + 5:
        return np.full(x.shape[1], np.nan), np.full(x.shape[1], np.nan), int(len(y))
    sw = np.sqrt(w / np.nanmean(w))
    xw = x * sw[:, None]
    yw = y * sw
    inv = np.linalg.pinv(xw.T @ xw)
    beta = inv @ (xw.T @ yw)
    resid = yw - xw @ beta
    meat = xw.T @ ((resid**2)[:, None] * xw)
    n, k = xw.shape
    cov = (n / max(n - k, 1)) * inv @ meat @ inv
    return beta, np.sqrt(np.diag(cov)), int(n)


def add_fe(parts: list[pd.Series | pd.DataFrame], d: pd.DataFrame, fe_cols: list[str]) -> pd.DataFrame:
    for col in fe_cols:
        parts.append(pd.get_dummies(d[col].astype(str), prefix=col, drop_first=True, dtype=float))
    return pd.concat(parts, axis=1)


def build_person_year() -> pd.DataFrame:
    cols = [
        "person_id",
        "person_month_key",
        "reference_year",
        "state_fips",
        "TAGE",
        "ESEX",
        "ERACE",
        "EHISPAN",
        "EEDUC",
        "ERP",
        "TFINCPOV",
        "WPFINWGT",
        "TSSSAMT",
        "RMWKWJB",
        "RMESR",
        "TPEARN",
        "RSNAP_MNYN",
        "RSNAP_YRYN",
        "RFOODR",
        "RFOODS",
        "RHLTHMTH",
        "RPRIMTH",
        "RPUBMTH",
        "EMDMTH",
        "TMDPAY",
        "TVISDOC",
        "TDAYSICK",
    ]
    df = pd.read_parquet(PANEL, columns=cols)
    df = df[df["reference_year"].between(2018, 2023)].copy()
    df["state_fips"] = df["state_fips"].astype(str).str.zfill(2)
    df = df[df["state_fips"].isin(REGIONAL_CONTROL_STATES)].copy()
    df["age"] = pd.to_numeric(df["TAGE"], errors="coerce")
    df["female"] = df["ESEX"].eq(2).astype(float)
    df["low_educ"] = pd.to_numeric(df["EEDUC"], errors="coerce").le(39).astype(float)
    df["parent_ref"] = df["ERP"].eq(1).astype(float)
    df["black"] = pd.to_numeric(df["ERACE"], errors="coerce").eq(2).astype(float)
    df["hispanic"] = yes(df["EHISPAN"]).astype(float)
    df["fpl"] = bounded_numeric(df["TFINCPOV"], 0, 20)
    df["weight"] = clean_weight(df)
    df["worker_month"] = (
        pd.to_numeric(df["RMWKWJB"], errors="coerce").gt(0)
        | pd.to_numeric(df["RMESR"], errors="coerce").between(1, 5)
    ).astype(float)
    df["earnings"] = bounded_numeric(df["TPEARN"], -250_000, 1_000_000)
    df["snap_month"] = yes(df["RSNAP_MNYN"]).astype(float)
    df["snap_any"] = yes(df["RSNAP_YRYN"]).astype(float)
    df["food_score"] = bounded_numeric(df["RFOODR"], 0, 6)
    df["food_status"] = bounded_numeric(df["RFOODS"], 1, 3)
    df["food_insecure"] = df["food_status"].ge(2).astype(float)
    df["very_low_food"] = df["food_status"].eq(3).astype(float)
    df["any_coverage"] = yes(df["RHLTHMTH"]).astype(float)
    df["uninsured"] = df["RHLTHMTH"].eq(2).astype(float)
    df["private"] = yes(df["RPRIMTH"]).astype(float)
    df["public"] = (yes(df["RPUBMTH"]) | yes(df["EMDMTH"])).astype(float)
    df["doctor_any"] = pd.to_numeric(df["TVISDOC"], errors="coerce").gt(0).astype(float)
    df["oop_any"] = pd.to_numeric(df["TMDPAY"], errors="coerce").gt(0).astype(float)
    df["sick_days"] = bounded_numeric(df["TDAYSICK"], 0, 365)

    py = (
        df.groupby(["person_id", "state_fips", "reference_year"], observed=True)
        .agg(
            months=("person_month_key", "size"),
            weight=("weight", "mean"),
            age=("age", "mean"),
            female=("female", "max"),
            low_educ=("low_educ", "max"),
            parent_ref=("parent_ref", "max"),
            black=("black", "max"),
            hispanic=("hispanic", "max"),
            fpl=("fpl", "median"),
            worker_share=("worker_month", "mean"),
            annual_earnings=("earnings", "sum"),
            snap_any=("snap_any", "max"),
            snap_share=("snap_month", "mean"),
            food_insecure=("food_insecure", "max"),
            very_low_food=("very_low_food", "max"),
            food_score=("food_score", "max"),
            any_coverage=("any_coverage", "mean"),
            uninsured=("uninsured", "mean"),
            private=("private", "mean"),
            public=("public", "mean"),
            doctor_any=("doctor_any", "mean"),
            oop_any=("oop_any", "mean"),
            sick_days=("sick_days", "mean"),
        )
        .reset_index()
    )
    py["state_name"] = py["state_fips"].map(STATE_NAMES)
    py["washington"] = py["state_fips"].eq(WASHINGTON).astype(int)
    py["post_2023"] = py["reference_year"].eq(2023).astype(int)
    py["low_wage_worker"] = (
        py["age"].between(25, 64, inclusive="both")
        & py["months"].ge(6)
        & py["worker_share"].ge(0.5)
        & py["annual_earnings"].between(1, 40_000, inclusive="both")
        & py["fpl"].between(0, 3, inclusive="both")
    ).astype(int)
    py["broad_worker"] = (
        py["age"].between(25, 64, inclusive="both")
        & py["months"].ge(6)
        & py["worker_share"].ge(0.5)
        & py["annual_earnings"].between(1, 60_000, inclusive="both")
        & py["fpl"].between(0, 4, inclusive="both")
    ).astype(int)
    py["log_earnings"] = np.log1p(py["annual_earnings"].clip(lower=0))
    return py


def build_sample(py: pd.DataFrame, target_col: str) -> pd.DataFrame:
    d = py.copy()
    d["target"] = d[target_col].astype(int)
    d["wftc_treat"] = d["washington"] * d["post_2023"] * d["target"]
    d["state_year"] = d["state_fips"] + "_" + d["reference_year"].astype(str)
    d["state_target"] = d["state_fips"] + "_" + d["target"].astype(str)
    d["target_year"] = d["target"].astype(str) + "_" + d["reference_year"].astype(str)
    return d


def estimate(d: pd.DataFrame, outcomes: list[str], model: str) -> pd.DataFrame:
    rows = []
    term = "wftc_treat"
    controls = ["age", "female", "low_educ", "parent_ref", "black", "hispanic", "fpl"]
    for outcome in outcomes:
        s = d[d[outcome].notna() & d["weight"].gt(0)].copy()
        parts: list[pd.Series | pd.DataFrame] = [pd.Series(1.0, index=s.index, name="const"), s[term].astype(float)]
        for c in controls:
            parts.append(s[c].astype(float).rename(c))
        x = add_fe(parts, s, ["state_year", "state_target", "target_year"])
        beta, se, n = wls_hc1(s[outcome].to_numpy(dtype=float), x.to_numpy(dtype=float), s["weight"].to_numpy(dtype=float))
        b = pd.Series(beta, index=x.columns)
        serr = pd.Series(se, index=x.columns)
        se_term = serr.get(term, np.nan)
        rows.append(
            {
                "model": model,
                "outcome": outcome,
                "coef": b.get(term, np.nan),
                "se_hc1": se_term,
                "t": b.get(term, np.nan) / se_term if se_term else np.nan,
                "n_person_years": n,
                "n_persons": int(s["person_id"].nunique()),
                "n_states": int(s["state_fips"].nunique()),
                "weighted_mean": wmean(s[outcome], s["weight"]),
            }
        )
    return pd.DataFrame(rows)


def support(samples: dict[str, pd.DataFrame]) -> pd.DataFrame:
    rows = []
    for name, d in samples.items():
        treated = d[d["washington"].eq(1) & d["post_2023"].eq(1) & d["target"].eq(1)]
        rows.append(
            {
                "sample": name,
                "person_years": int(len(d)),
                "persons": int(d["person_id"].nunique()),
                "states": int(d["state_fips"].nunique()),
                "target_person_years": int(d["target"].sum()),
                "target_persons": int(d.loc[d["target"].eq(1), "person_id"].nunique()),
                "washington_2023_target_person_years": int(len(treated)),
                "washington_2023_target_persons": int(treated["person_id"].nunique()),
                "washington_2023_target_food_insecure_mean": float(treated["food_insecure"].mean()) if len(treated) else np.nan,
            }
        )
    return pd.DataFrame(rows)


def fmt(est: pd.DataFrame, model: str, outcomes: list[str]) -> str:
    d = est[est["model"].eq(model)].set_index("outcome")
    lines = []
    for outcome in outcomes:
        if outcome in d.index:
            r = d.loc[outcome]
            lines.append(f"- `{outcome}`: {r['coef']:+.4f}, se {r['se_hc1']:.4f}, t {r['t']:.2f}.")
    return "\n".join(lines)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    py = build_person_year()
    samples = {
        "low_wage_worker": build_sample(py, "low_wage_worker"),
        "broad_worker": build_sample(py, "broad_worker"),
    }
    outcomes = [
        "food_insecure",
        "very_low_food",
        "food_score",
        "snap_any",
        "snap_share",
        "any_coverage",
        "uninsured",
        "public",
        "private",
        "doctor_any",
        "oop_any",
        "sick_days",
        "worker_share",
        "log_earnings",
    ]
    main_outcomes = ["food_insecure", "very_low_food", "food_score", "snap_any", "uninsured", "oop_any", "log_earnings"]
    estimates = pd.concat(
        [
            estimate(samples["low_wage_worker"], outcomes, "wftc_low_wage_worker"),
            estimate(samples["broad_worker"], outcomes, "wftc_broad_worker"),
        ],
        ignore_index=True,
    )
    sup = support(samples)

    py.to_parquet(OUT / "washington_wftc_person_year_panel.parquet", index=False)
    estimates.to_csv(OUT / "washington_wftc_estimates.csv", index=False)
    sup.to_csv(OUT / "washington_wftc_support.csv", index=False)

    s_low = sup[sup["sample"].eq("low_wage_worker")].iloc[0]
    primary = estimates[estimates["model"].eq("wftc_low_wage_worker")].set_index("outcome")
    food = primary.loc["food_insecure"]
    verdict = "NO-GO-SUPPORT"
    if s_low["washington_2023_target_person_years"] >= 150 and food["coef"] < -0.03 and abs(food["t"]) > 1.5:
        verdict = "PROMISING-WFTC-FOOD-SECURITY-SIGNAL"
    elif s_low["washington_2023_target_person_years"] >= 100:
        verdict = "DIRECTIONAL-BUT-THIN"

    report = f"""# Washington Working Families Tax Credit Fast Test

## Question

Can current SIPP support an adult low-wage-worker paper on Washington's Working Families Tax Credit
launch?

## Source Checks

{chr(10).join(f"- {s}" for s in SOURCES)}

The official Washington WFTC site describes the credit as a tax credit for Washington workers. The
eligibility page states that eligible individuals must have lived in Washington for at least 183 days,
be at least 25 and under 65 or have a qualifying child, file a federal tax return, and be eligible for
the federal EITC or ITIN-equivalent eligibility. Washington Department of Revenue states the program
launched in 2023.

## Design

- Unit: person-year, 2018-2023.
- Geography: Washington vs regional controls: California, Colorado, Idaho, Montana, Oregon.
- Primary target: age 25-64, FPL <= 300%, annual earnings $1-$40,000, employed in at least half of
  observed months.
- Treatment: Washington x 2023 x target worker.
- Fixed effects: state-year, state-target, target-year.
- Outcomes: food security, SNAP, coverage, medical OOP, labor-market outcomes.

This is a feasibility screen. The compact parquet does not observe tax filing, federal EITC
eligibility, ITIN/SSN eligibility, actual WFTC application, or refund receipt.

## Support

Primary low-wage worker target:

- Person-years: {int(s_low['person_years']):,}.
- Persons: {int(s_low['persons']):,}.
- Target person-years: {int(s_low['target_person_years']):,}.
- Washington 2023 target person-years: {int(s_low['washington_2023_target_person_years']):,}.
- Washington 2023 target persons: {int(s_low['washington_2023_target_persons']):,}.

## Main Estimates

Low-wage worker target:

{fmt(estimates, 'wftc_low_wage_worker', main_outcomes)}

Broad worker sensitivity:

{fmt(estimates, 'wftc_broad_worker', main_outcomes)}

## Verdict

`{verdict}`

A clean GO would require a much larger Washington 2023 target cell, credible tax-unit construction,
and a coherent improvement in food security or financial outcomes among likely eligible workers.

## Artifacts

- `script/11_idea_scan/20_washington_wftc_fast_test.py`
- `result/idea_scan/washington_wftc_person_year_panel.parquet`
- `result/idea_scan/washington_wftc_support.csv`
- `result/idea_scan/washington_wftc_estimates.csv`
"""
    REPORT.write_text(report, encoding="utf-8")


if __name__ == "__main__":
    main()
