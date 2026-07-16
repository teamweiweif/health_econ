from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
PANEL = ROOT / "data" / "analysis_ready" / "sipp_2018_2024_person_month_panel.parquet"
OUT = ROOT / "result" / "idea_scan"
REPORT = ROOT / "report" / "46_aca_reinsurance_fast_test.md"


SOURCES = [
    "KFF Section 1332 waiver tracker: https://www.kff.org/affordable-care-act/tracking-section-1332-state-innovation-waivers/",
    "CMS CCIIO 2024 Section 1332 data brief: https://www.cms.gov/files/document/cciio-data-brief-042024-508-final.pdf",
]


STATE_TO_FIPS = {
    "Alaska": "02",
    "Minnesota": "27",
    "Oregon": "41",
    "Maine": "23",
    "Maryland": "24",
    "New Jersey": "34",
    "Wisconsin": "55",
    "Colorado": "08",
    "Delaware": "10",
    "Montana": "30",
    "North Dakota": "38",
    "Rhode Island": "44",
    "Pennsylvania": "42",
    "New Hampshire": "33",
    "Georgia": "13",
    "Virginia": "51",
    "Idaho": "16",
}


PREMIUM_REDUCTION = {
    "Alaska": {2018: 30.18, 2019: 33.95, 2020: 37.12, 2021: 41.17, 2022: 38.05, 2023: 38.79},
    "Minnesota": {2018: 16.78, 2019: 20.16, 2020: 21.29, 2021: 21.31, 2022: 14.37, 2023: 20.38},
    "Oregon": {2018: 7.15, 2019: 6.71, 2020: 8.00, 2021: 8.05, 2022: 8.09, 2023: 8.59},
    "Maine": {2019: 13.86, 2020: 7.24, 2021: 9.11, 2022: 10.91, 2023: 12.46},
    "Maryland": {2019: 39.63, 2020: 35.83, 2021: 34.00, 2022: 29.80, 2023: 32.56},
    "New Jersey": {2019: 15.49, 2020: 16.93, 2021: 16.02, 2022: 16.03, 2023: 14.60},
    "Wisconsin": {2019: 9.92, 2020: 11.04, 2021: 13.04, 2022: 13.12, 2023: 12.50},
    "Colorado": {2020: 22.44, 2021: 18.47, 2022: 21.70, 2023: 19.66},
    "Delaware": {2020: 13.78, 2021: 15.80, 2022: 15.00, 2023: 15.60},
    "Montana": {2020: 8.89, 2021: 9.38, 2022: 9.22, 2023: 8.26},
    "North Dakota": {2020: 20.03, 2021: 12.14, 2022: 10.71, 2023: 8.38},
    "Rhode Island": {2020: 3.75, 2021: 6.40, 2022: 4.96, 2023: 5.47},
    "Pennsylvania": {2021: 4.92, 2022: 5.92, 2023: 4.34},
    "New Hampshire": {2021: 13.90, 2022: 13.96, 2023: 13.40},
    "Georgia": {2022: 16.68, 2023: 19.20},
    "Virginia": {2023: 17.14},
    "Idaho": {2023: 12.50},
}


def yes(s: pd.Series) -> pd.Series:
    return s.eq(1)


def bounded_numeric(s: pd.Series, lo: float, hi: float) -> pd.Series:
    out = pd.to_numeric(s, errors="coerce")
    return out.where(out.between(lo, hi, inclusive="both"))


def clean_weight(df: pd.DataFrame) -> pd.Series:
    w = pd.to_numeric(df.get("WPFINWGT"), errors="coerce")
    return w.where(w.gt(0))


def wmean(y: pd.Series, w: pd.Series) -> float:
    mask = y.notna() & w.notna() & (w > 0)
    if not mask.any():
        return np.nan
    return float(np.average(y[mask].astype(float), weights=w[mask].astype(float)))


def wls_cluster(
    y: np.ndarray, x: np.ndarray, w: np.ndarray, cluster: np.ndarray
) -> tuple[np.ndarray, np.ndarray, int, int]:
    mask = np.isfinite(y) & np.isfinite(w) & (w > 0) & np.all(np.isfinite(x), axis=1)
    y = y[mask]
    x = x[mask]
    w = w[mask]
    cluster = cluster[mask]
    if len(y) <= x.shape[1] + 5:
        return np.full(x.shape[1], np.nan), np.full(x.shape[1], np.nan), int(len(y)), int(pd.Series(cluster).nunique())
    sw = np.sqrt(w / np.nanmean(w))
    xw = x * sw[:, None]
    yw = y * sw
    inv = np.linalg.pinv(xw.T @ xw)
    beta = inv @ (xw.T @ yw)
    resid = yw - xw @ beta
    meat = np.zeros((xw.shape[1], xw.shape[1]))
    for g in pd.unique(cluster):
        idx = cluster == g
        score = xw[idx].T @ resid[idx]
        meat += np.outer(score, score)
    n, k = xw.shape
    g_count = int(pd.Series(cluster).nunique())
    if g_count > 1:
        meat *= (g_count / (g_count - 1)) * ((n - 1) / max(n - k, 1))
    cov = inv @ meat @ inv
    return beta, np.sqrt(np.diag(cov)), int(n), g_count


def add_fe(parts: list[pd.Series | pd.DataFrame], d: pd.DataFrame, fe_cols: list[str]) -> pd.DataFrame:
    for col in fe_cols:
        parts.append(pd.get_dummies(d[col].astype(str), prefix=col, drop_first=True, dtype=float))
    return pd.concat(parts, axis=1)


def build_policy() -> pd.DataFrame:
    rows = []
    for state, by_year in PREMIUM_REDUCTION.items():
        for year in range(2017, 2024):
            reduction = by_year.get(year, 0.0)
            rows.append(
                {
                    "state": state,
                    "state_fips": STATE_TO_FIPS[state],
                    "reference_year": year,
                    "premium_reduction_pct": reduction,
                    "premium_reduction_10pp": reduction / 10.0,
                    "reinsurance_active": int(reduction > 0),
                }
            )
    policy = pd.DataFrame(rows)

    all_states = pd.read_parquet(PANEL, columns=["state_fips"])["state_fips"].astype(str).str.zfill(2).unique()
    all_years = range(2017, 2024)
    grid = pd.MultiIndex.from_product([all_states, all_years], names=["state_fips", "reference_year"]).to_frame(index=False)
    policy = grid.merge(policy, on=["state_fips", "reference_year"], how="left")
    policy["state"] = policy["state"].fillna("")
    policy["premium_reduction_pct"] = policy["premium_reduction_pct"].fillna(0.0)
    policy["premium_reduction_10pp"] = policy["premium_reduction_10pp"].fillna(0.0)
    policy["reinsurance_active"] = policy["reinsurance_active"].fillna(0).astype(int)
    return policy.sort_values(["state_fips", "reference_year"])


def build_person_year(policy: pd.DataFrame) -> pd.DataFrame:
    cols = [
        "person_id",
        "person_month_key",
        "reference_year",
        "state_fips",
        "TAGE",
        "TFINCPOV",
        "EHLTSTAT",
        "WPFINWGT",
        "TSSSAMT",
        "RHLTHMTH",
        "RPRIMTH",
        "RPUBMTH",
        "RPRITYPE2",
        "RMARKTPLACE",
        "EPRIEXCH1",
        "EPRIEXCH2",
        "EPRISUBS1",
        "EPRISUBS2",
        "EMDEXCH",
        "EMDSUBS",
        "TMDPAY",
        "TVISDOC",
    ]
    df = pd.read_parquet(PANEL, columns=cols)
    df = df[df["reference_year"].between(2017, 2023)].copy()
    df["state_fips"] = df["state_fips"].astype(str).str.zfill(2)
    df["age"] = bounded_numeric(df["TAGE"], 0, 100)
    df["fpl"] = bounded_numeric(df["TFINCPOV"], 0, 20)
    df["healthy"] = pd.to_numeric(df["EHLTSTAT"], errors="coerce").between(1, 2).astype(float)
    df["weight"] = clean_weight(df)
    df["any_coverage"] = yes(df["RHLTHMTH"]).astype(float)
    df["uninsured"] = df["RHLTHMTH"].eq(2).astype(float)
    df["private"] = yes(df["RPRIMTH"]).astype(float)
    df["public"] = yes(df["RPUBMTH"]).astype(float)
    df["direct_market"] = (yes(df["RPRITYPE2"]) | yes(df["RMARKTPLACE"])).astype(float)
    df["exchange_subsidy"] = (
        yes(df["EPRIEXCH1"])
        | yes(df["EPRIEXCH2"])
        | yes(df["EPRISUBS1"])
        | yes(df["EPRISUBS2"])
        | yes(df["EMDEXCH"])
        | yes(df["EMDSUBS"])
    ).astype(float)
    df["oop_any"] = pd.to_numeric(df["TMDPAY"], errors="coerce").gt(0).astype(float)
    df["doctor_any"] = pd.to_numeric(df["TVISDOC"], errors="coerce").gt(0).astype(float)

    py = (
        df.groupby(["person_id", "state_fips", "reference_year"], observed=True)
        .agg(
            months=("person_month_key", "size"),
            weight=("weight", "mean"),
            age=("age", "mean"),
            fpl=("fpl", "median"),
            healthy=("healthy", "mean"),
            any_coverage=("any_coverage", "mean"),
            uninsured=("uninsured", "mean"),
            private=("private", "mean"),
            public=("public", "mean"),
            direct_market=("direct_market", "mean"),
            exchange_subsidy=("exchange_subsidy", "mean"),
            oop_any=("oop_any", "mean"),
            doctor_any=("doctor_any", "mean"),
        )
        .reset_index()
    )
    py["healthy"] = py["healthy"].ge(0.5).astype(int)
    py = py.merge(policy, on=["state_fips", "reference_year"], how="left")
    py["premium_reduction_pct"] = py["premium_reduction_pct"].fillna(0.0)
    py["premium_reduction_10pp"] = py["premium_reduction_10pp"].fillna(0.0)
    py["reinsurance_active"] = py["reinsurance_active"].fillna(0).astype(int)
    return py


def prep_sample(py: pd.DataFrame, name: str) -> pd.DataFrame:
    if name == "all_2017_2023":
        d = py[py["reference_year"].between(2017, 2023)].copy()
    elif name == "pre_arpa_2017_2020":
        d = py[py["reference_year"].between(2017, 2020)].copy()
    else:
        raise ValueError(name)
    d = d[
        d["age"].between(26, 64, inclusive="both")
        & d["fpl"].between(1.38, 10.0, inclusive="both")
        & d["months"].ge(6)
        & ~d["state_fips"].eq("02")
    ].copy()
    d["high_income"] = d["fpl"].between(4.0, 10.0, inclusive="both").astype(int)
    d["target_x_reduction_10pp"] = d["high_income"] * d["premium_reduction_10pp"]
    d["target_x_active"] = d["high_income"] * d["reinsurance_active"]
    d["state_year"] = d["state_fips"] + "_" + d["reference_year"].astype(str)
    d["state_target"] = d["state_fips"] + "_" + d["high_income"].astype(str)
    d["target_year"] = d["high_income"].astype(str) + "_" + d["reference_year"].astype(str)
    return d


def estimate(
    d: pd.DataFrame,
    term: str,
    outcomes: list[str],
    model: str,
    controls: list[str],
    fe_cols: list[str],
) -> pd.DataFrame:
    rows = []
    for outcome in outcomes:
        s = d[d[outcome].notna() & d["weight"].gt(0)].copy()
        parts: list[pd.Series | pd.DataFrame] = [
            pd.Series(1.0, index=s.index, name="const"),
            s[term].astype(float),
        ]
        for c in controls:
            parts.append(s[c].astype(float).rename(c))
        x = add_fe(parts, s, fe_cols)
        beta, se, n, g = wls_cluster(
            s[outcome].to_numpy(dtype=float),
            x.to_numpy(dtype=float),
            s["weight"].to_numpy(dtype=float),
            s["state_fips"].to_numpy(),
        )
        b = pd.Series(beta, index=x.columns)
        serr = pd.Series(se, index=x.columns)
        rows.append(
            {
                "model": model,
                "outcome": outcome,
                "term": term,
                "coef": b.get(term, np.nan),
                "state_clustered_se": serr.get(term, np.nan),
                "state_clustered_t": b.get(term, np.nan) / serr.get(term, np.nan) if serr.get(term, np.nan) else np.nan,
                "n_person_years": n,
                "n_persons": int(s["person_id"].nunique()),
                "n_states": int(s["state_fips"].nunique()),
                "weighted_mean": wmean(s[outcome], s["weight"]),
            }
        )
    return pd.DataFrame(rows)


def support(d: pd.DataFrame, sample: str) -> pd.DataFrame:
    target = d[d["high_income"].eq(1)]
    active_target = d[d["high_income"].eq(1) & d["reinsurance_active"].eq(1)]
    rows = [
        {
            "sample": sample,
            "person_years": int(len(d)),
            "persons": int(d["person_id"].nunique()),
            "states": int(d["state_fips"].nunique()),
            "high_income_person_years": int(len(target)),
            "high_income_persons": int(target["person_id"].nunique()),
            "active_high_income_person_years": int(len(active_target)),
            "active_high_income_persons": int(active_target["person_id"].nunique()),
            "active_states": int(d.loc[d["reinsurance_active"].eq(1), "state_fips"].nunique()),
            "mean_premium_reduction_active": float(d.loc[d["reinsurance_active"].eq(1), "premium_reduction_pct"].mean()),
            "weighted_mean_direct_market": wmean(d["direct_market"], d["weight"]),
            "weighted_mean_uninsured": wmean(d["uninsured"], d["weight"]),
        }
    ]
    return pd.DataFrame(rows)


def year_support(d: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for year, g in d.groupby("reference_year", observed=True):
        rows.append(
            {
                "reference_year": int(year),
                "active_states": int(g.loc[g["reinsurance_active"].eq(1), "state_fips"].nunique()),
                "mean_active_premium_reduction": float(g.loc[g["reinsurance_active"].eq(1), "premium_reduction_pct"].mean()),
                "high_income_person_years": int(g["high_income"].sum()),
                "active_high_income_person_years": int((g["high_income"] * g["reinsurance_active"]).sum()),
            }
        )
    return pd.DataFrame(rows)


def fmt(est: pd.DataFrame, model: str, outcomes: list[str]) -> str:
    d = est[est["model"].eq(model)].set_index("outcome")
    lines = []
    for outcome in outcomes:
        if outcome not in d.index:
            continue
        r = d.loc[outcome]
        lines.append(
            f"- `{outcome}`: {r['coef']:+.4f}, state-clustered se {r['state_clustered_se']:.4f}, "
            f"t {r['state_clustered_t']:.2f}."
        )
    return "\n".join(lines)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    policy = build_policy()
    py = build_person_year(policy)
    all_d = prep_sample(py, "all_2017_2023")
    pre_arpa = prep_sample(py, "pre_arpa_2017_2020")
    outcomes = ["direct_market", "exchange_subsidy", "uninsured", "any_coverage", "private", "oop_any", "doctor_any"]
    controls = ["age", "fpl", "healthy"]
    fe_cols = ["state_year", "state_target", "target_year"]

    estimates = pd.concat(
        [
            estimate(
                all_d,
                "target_x_reduction_10pp",
                outcomes,
                "all_2017_2023_reduction_intensity",
                controls,
                fe_cols,
            ),
            estimate(all_d, "target_x_active", outcomes, "all_2017_2023_active_indicator", controls, fe_cols),
            estimate(
                pre_arpa,
                "target_x_reduction_10pp",
                outcomes,
                "pre_arpa_2017_2020_reduction_intensity",
                controls,
                fe_cols,
            ),
            estimate(pre_arpa, "target_x_active", outcomes, "pre_arpa_2017_2020_active_indicator", controls, fe_cols),
        ],
        ignore_index=True,
    )
    sup = pd.concat([support(all_d, "all_2017_2023"), support(pre_arpa, "pre_arpa_2017_2020")], ignore_index=True)
    ys = year_support(all_d)

    policy.to_csv(OUT / "aca_reinsurance_policy.csv", index=False)
    py.to_parquet(OUT / "aca_reinsurance_person_year_panel.parquet", index=False)
    estimates.to_csv(OUT / "aca_reinsurance_estimates.csv", index=False)
    sup.to_csv(OUT / "aca_reinsurance_support.csv", index=False)
    ys.to_csv(OUT / "aca_reinsurance_year_support.csv", index=False)

    all_s = sup[sup["sample"].eq("all_2017_2023")].iloc[0]
    pre_s = sup[sup["sample"].eq("pre_arpa_2017_2020")].iloc[0]
    main_dm = estimates[
        (estimates["model"].eq("pre_arpa_2017_2020_reduction_intensity"))
        & (estimates["outcome"].eq("direct_market"))
    ].iloc[0]
    main_unins = estimates[
        (estimates["model"].eq("pre_arpa_2017_2020_reduction_intensity")) & (estimates["outcome"].eq("uninsured"))
    ].iloc[0]
    verdict = "NO-CLEAN-GO"
    if main_dm["coef"] > 0.01 and main_dm["state_clustered_t"] > 1.5 and main_unins["coef"] < 0:
        verdict = "POTENTIAL-INSURANCE-GO"
    elif main_dm["coef"] > 0 and main_unins["coef"] < 0:
        verdict = "DIRECTIONAL-BUT-NOT-CLEAN"

    report = f"""# ACA State Reinsurance Fast Test

## Question

Can state ACA Section 1332 reinsurance programs support an adult SIPP paper on Marketplace
affordability and coverage?

## Source Checks

{chr(10).join(f"- {s}" for s in SOURCES)}

Key policy facts used here:

- KFF describes Section 1332 waivers as ACA innovation waivers and notes that most approved waivers
  have been used for state reinsurance programs.
- The CMS CCIIO data brief reports state first years of operation and actual SLCSP premium reductions
  under state reinsurance waivers.
- CMS reports that state reinsurance programs reduced statewide average SLCSP premiums by 3.75% to
  41.17% from 2018 through 2023 relative to no-waiver premiums.

## Design

- Unit: person-year collapsed from monthly SIPP observations.
- Sample: adults age 26-64 with family income 138-1000% FPL and at least six observed months.
- Primary exposed group: 400-1000% FPL adults, who are more exposed to gross premium reductions,
  especially before ARPA removed the hard 400% FPL subsidy cliff.
- Comparison group: 138-400% FPL adults in the same state-years.
- Treatment intensity: high-income target x CMS actual SLCSP premium reduction, scaled per 10
  percentage points.
- Alternative treatment: high-income target x any active reinsurance program.
- Fixed effects: state-year, state-target, target-year.
- Standard errors: clustered by state.
- Alaska is excluded because CMS notes its state reinsurance program began operating in 2017 before
  the approved 1332 waiver period.

## Support

All years, 2017-2023:

- Person-years: {int(all_s['person_years']):,}.
- Persons: {int(all_s['persons']):,}.
- States: {int(all_s['states']):,}.
- High-income target person-years: {int(all_s['high_income_person_years']):,}.
- Active reinsurance high-income person-years: {int(all_s['active_high_income_person_years']):,}.
- Active reinsurance states: {int(all_s['active_states']):,}.

Pre-ARPA years, 2017-2020:

- Person-years: {int(pre_s['person_years']):,}.
- Persons: {int(pre_s['persons']):,}.
- States: {int(pre_s['states']):,}.
- High-income target person-years: {int(pre_s['high_income_person_years']):,}.
- Active reinsurance high-income person-years: {int(pre_s['active_high_income_person_years']):,}.
- Active reinsurance states: {int(pre_s['active_states']):,}.

## Main Estimates

Pre-ARPA 2017-2020, premium-reduction intensity per 10 percentage points:

{fmt(estimates, 'pre_arpa_2017_2020_reduction_intensity', outcomes)}

Pre-ARPA 2017-2020, active reinsurance indicator:

{fmt(estimates, 'pre_arpa_2017_2020_active_indicator', outcomes)}

All years 2017-2023, premium-reduction intensity per 10 percentage points:

{fmt(estimates, 'all_2017_2023_reduction_intensity', outcomes)}

## Verdict

`{verdict}`

A clean GO requires a clear positive first stage on direct-market or exchange/subsidized coverage
among the high-income exposed group, preferably with lower uninsured months. If the direct-market
signal is not coherent in the pre-ARPA screen, this should not displace the stronger SNAP EA lead.

## Artifacts

- `script/11_idea_scan/22_aca_reinsurance_fast_test.py`
- `result/idea_scan/aca_reinsurance_policy.csv`
- `result/idea_scan/aca_reinsurance_person_year_panel.parquet`
- `result/idea_scan/aca_reinsurance_support.csv`
- `result/idea_scan/aca_reinsurance_year_support.csv`
- `result/idea_scan/aca_reinsurance_estimates.csv`
"""
    REPORT.write_text(report, encoding="utf-8")
    print(verdict)
    print(sup.to_string(index=False))
    print(estimates.to_string(index=False))


if __name__ == "__main__":
    main()
