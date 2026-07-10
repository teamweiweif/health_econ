from __future__ import annotations

import re
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
PANEL = ROOT / "data" / "analysis_ready" / "sipp_2018_2024_person_month_panel.parquet"
OUT = ROOT / "result" / "idea_scan"
REPORT = ROOT / "report" / "44_minimum_wage_food_security_test.md"
DOL_HISTORY = "https://www.dol.gov/agencies/whd/state/minimum-wage/history"


STATE_TO_FIPS = {
    "Alabama": "01",
    "Alaska": "02",
    "Arizona": "04",
    "Arkansas": "05",
    "California": "06",
    "Colorado": "08",
    "Connecticut": "09",
    "Delaware": "10",
    "District of Columbia": "11",
    "Florida": "12",
    "Georgia": "13",
    "Hawaii": "15",
    "Idaho": "16",
    "Illinois": "17",
    "Indiana": "18",
    "Iowa": "19",
    "Kansas": "20",
    "Kentucky": "21",
    "Louisiana": "22",
    "Maine": "23",
    "Maryland": "24",
    "Massachusetts": "25",
    "Michigan": "26",
    "Minnesota": "27",
    "Mississippi": "28",
    "Missouri": "29",
    "Montana": "30",
    "Nebraska": "31",
    "Nevada": "32",
    "New Hampshire": "33",
    "New Jersey": "34",
    "New Mexico": "35",
    "New York": "36",
    "North Carolina": "37",
    "North Dakota": "38",
    "Ohio": "39",
    "Oklahoma": "40",
    "Oregon": "41",
    "Pennsylvania": "42",
    "Rhode Island": "44",
    "South Carolina": "45",
    "South Dakota": "46",
    "Tennessee": "47",
    "Texas": "48",
    "Utah": "49",
    "Vermont": "50",
    "Virginia": "51",
    "Washington": "53",
    "West Virginia": "54",
    "Wisconsin": "55",
    "Wyoming": "56",
}


def yes(s: pd.Series) -> pd.Series:
    return s.eq(1)


def bounded_numeric(s: pd.Series, lo: float, hi: float) -> pd.Series:
    out = pd.to_numeric(s, errors="coerce")
    return out.where(out.between(lo, hi, inclusive="both"))


def parse_wage(value: object) -> float:
    if pd.isna(value):
        return np.nan
    text = str(value)
    if "..." in text or text.strip() in {"", "nan", "N.A."}:
        return np.nan
    nums = re.findall(r"\d+(?:\.\d+)?", text.replace("$", ""))
    if not nums:
        return np.nan
    return max(float(x) for x in nums)


def read_minimum_wage_policy() -> pd.DataFrame:
    tables = pd.read_html(DOL_HISTORY)
    raw = pd.concat(tables, axis=1)
    raw = raw.loc[:, ~raw.columns.duplicated()]
    raw = raw.rename(columns={"State or other jurisdiction": "state"})
    year_cols = [c for c in raw.columns if str(c).isdigit()]
    federal_row = raw[raw["state"].eq("Federal (FLSA)")].iloc[0]
    federal = {int(y): parse_wage(federal_row[y]) for y in year_cols}
    rows = []
    for _, r in raw.iterrows():
        state = r["state"]
        if state not in STATE_TO_FIPS:
            continue
        for y in year_cols:
            year = int(y)
            if year < 2017 or year > 2024:
                continue
            state_wage = parse_wage(r[y])
            floor = federal.get(year, 7.25)
            effective = max(state_wage if pd.notna(state_wage) else floor, floor)
            rows.append({"state": state, "state_fips": STATE_TO_FIPS[state], "reference_year": year, "minimum_wage": effective})
    policy = pd.DataFrame(rows).sort_values(["state_fips", "reference_year"])
    policy["mw_lag"] = policy.groupby("state_fips")["minimum_wage"].shift(1)
    policy["mw_change"] = policy["minimum_wage"] - policy["mw_lag"]
    policy["mw_increase"] = policy["mw_change"].clip(lower=0).fillna(0)
    policy["mw_increase_50c"] = policy["mw_increase"].ge(0.5).astype(int)
    return policy


def clean_weight(df: pd.DataFrame) -> pd.Series:
    w = pd.to_numeric(df.get("WPFINWGT"), errors="coerce")
    w = w.where(w.gt(0), pd.to_numeric(df.get("TSSSAMT"), errors="coerce"))
    return w.where(w.gt(0), 1.0)


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


def build_household_year(policy: pd.DataFrame) -> pd.DataFrame:
    cols = [
        "SSUID",
        "SHHADID",
        "RFAMNUM",
        "person_id",
        "person_month_key",
        "reference_year",
        "state_fips",
        "TAGE",
        "ESEX",
        "ERACE",
        "EHISPAN",
        "EEDUC",
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
    df["hh_id"] = (
        df["SSUID"].astype(str)
        + "_"
        + df["SHHADID"].astype(str)
        + "_"
        + df["RFAMNUM"].astype(str)
        + "_"
        + df["reference_year"].astype(str)
    )
    df["age"] = pd.to_numeric(df["TAGE"], errors="coerce")
    df["adult"] = df["age"].between(19, 64, inclusive="both")
    df["prime"] = df["age"].between(25, 54, inclusive="both")
    df["female"] = df["ESEX"].eq(2).astype(float)
    df["low_educ"] = pd.to_numeric(df["EEDUC"], errors="coerce").le(39).astype(float)
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
        df.groupby(["person_id", "hh_id", "state_fips", "reference_year"], observed=True)
        .agg(
            months=("person_month_key", "size"),
            weight=("weight", "mean"),
            age=("age", "mean"),
            adult=("adult", "max"),
            prime=("prime", "max"),
            female=("female", "max"),
            low_educ=("low_educ", "max"),
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
    py["low_wage_worker_person"] = (
        py["adult"].eq(1)
        & py["months"].ge(6)
        & py["worker_share"].ge(0.5)
        & py["annual_earnings"].between(1, 35_000, inclusive="both")
        & py["fpl"].between(0, 3, inclusive="both")
    ).astype(int)
    py["low_educ_adult_person"] = (
        py["adult"].eq(1) & py["low_educ"].eq(1) & py["fpl"].between(0, 4, inclusive="both")
    ).astype(int)
    py["log_earnings"] = np.log1p(py["annual_earnings"].clip(lower=0))

    hy = (
        py.groupby(["hh_id", "state_fips", "reference_year"], observed=True)
        .agg(
            household_members=("person_id", "nunique"),
            adult_members=("adult", "sum"),
            target_low_wage=("low_wage_worker_person", "max"),
            target_low_educ=("low_educ_adult_person", "max"),
            weight=("weight", "mean"),
            age=("age", "mean"),
            female_share=("female", "mean"),
            black_any=("black", "max"),
            hispanic_any=("hispanic", "max"),
            fpl=("fpl", "median"),
            earnings_sum=("annual_earnings", "sum"),
            food_insecure=("food_insecure", "max"),
            very_low_food=("very_low_food", "max"),
            food_score=("food_score", "max"),
            snap_any=("snap_any", "max"),
            snap_share=("snap_share", "mean"),
            any_coverage=("any_coverage", "mean"),
            uninsured=("uninsured", "mean"),
            private=("private", "mean"),
            public=("public", "mean"),
            doctor_any=("doctor_any", "mean"),
            oop_any=("oop_any", "mean"),
            sick_days=("sick_days", "mean"),
            worker_share=("worker_share", "mean"),
            log_earnings=("log_earnings", "mean"),
        )
        .reset_index()
    )
    hy = hy.merge(policy, on=["state_fips", "reference_year"], how="left")
    return hy


def build_sample(hy: pd.DataFrame, target_col: str) -> pd.DataFrame:
    d = hy[hy["adult_members"].gt(0) & hy["mw_increase"].notna()].copy()
    d["target"] = d[target_col].astype(int)
    d["target_x_mw_increase"] = d["target"] * d["mw_increase"].fillna(0)
    d["target_x_mw_50c"] = d["target"] * d["mw_increase_50c"].fillna(0)
    d["state_year"] = d["state_fips"] + "_" + d["reference_year"].astype(str)
    d["state_target"] = d["state_fips"] + "_" + d["target"].astype(str)
    d["target_year"] = d["target"].astype(str) + "_" + d["reference_year"].astype(str)
    return d


def estimate(d: pd.DataFrame, term: str, outcomes: list[str], model: str) -> pd.DataFrame:
    rows = []
    controls = ["age", "female_share", "black_any", "hispanic_any", "fpl"]
    for outcome in outcomes:
        s = d[d[outcome].notna() & d["weight"].gt(0)].copy()
        parts: list[pd.Series | pd.DataFrame] = [pd.Series(1.0, index=s.index, name="const"), s[term].astype(float)]
        for c in controls:
            parts.append(s[c].astype(float).rename(c))
        x = add_fe(parts, s, ["state_year", "state_target", "target_year"])
        beta, se, n, g = wls_cluster(
            s[outcome].to_numpy(dtype=float),
            x.to_numpy(dtype=float),
            s["weight"].to_numpy(dtype=float),
            s["state_fips"].to_numpy(),
        )
        b = pd.Series(beta, index=x.columns)
        serr = pd.Series(se, index=x.columns)
        se_term = serr.get(term, np.nan)
        rows.append(
            {
                "model": model,
                "outcome": outcome,
                "term": term,
                "coef": b.get(term, np.nan),
                "state_clustered_se": se_term,
                "state_clustered_t": b.get(term, np.nan) / se_term if se_term else np.nan,
                "n_household_years": n,
                "n_households": int(s["hh_id"].nunique()),
                "n_states": int(s["state_fips"].nunique()),
                "n_clusters": g,
                "weighted_mean": wmean(s[outcome], s["weight"]),
            }
        )
    return pd.DataFrame(rows)


def support(samples: dict[str, pd.DataFrame], policy: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    rows = []
    for name, d in samples.items():
        treated = d[d["target"].eq(1) & d["mw_increase"].gt(0)]
        rows.append(
            {
                "sample": name,
                "household_years": int(len(d)),
                "households": int(d["hh_id"].nunique()),
                "states": int(d["state_fips"].nunique()),
                "target_household_years": int(d["target"].sum()),
                "target_households": int(d.loc[d["target"].eq(1), "hh_id"].nunique()),
                "target_with_any_mw_increase_household_years": int(len(treated)),
                "target_with_50c_increase_household_years": int(len(d[d["target"].eq(1) & d["mw_increase"].ge(0.5)])),
                "weighted_mean_food_insecure": wmean(d["food_insecure"], d["weight"]),
            }
        )
    year_support = (
        policy[policy["reference_year"].between(2018, 2023)]
        .groupby("reference_year", observed=True)
        .agg(
            states_with_any_increase=("mw_increase", lambda x: int((x > 0).sum())),
            states_with_50c_increase=("mw_increase", lambda x: int((x >= 0.5).sum())),
            mean_positive_increase=("mw_increase", lambda x: float(x[x > 0].mean()) if (x > 0).any() else 0.0),
        )
        .reset_index()
    )
    return pd.DataFrame(rows), year_support


def fmt(est: pd.DataFrame, model: str, outcomes: list[str]) -> str:
    d = est[est["model"].eq(model)].set_index("outcome")
    lines = []
    for outcome in outcomes:
        if outcome in d.index:
            r = d.loc[outcome]
            lines.append(
                f"- `{outcome}`: {r['coef']:+.4f}, state-clustered se {r['state_clustered_se']:.4f}, t {r['state_clustered_t']:.2f}."
            )
    return "\n".join(lines)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    policy = read_minimum_wage_policy()
    hy = build_household_year(policy)
    samples = {
        "household_low_wage": build_sample(hy, "target_low_wage"),
        "household_low_educ": build_sample(hy, "target_low_educ"),
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
            estimate(samples["household_low_wage"], "target_x_mw_increase", outcomes, "mw_food_low_wage_intensity"),
            estimate(samples["household_low_wage"], "target_x_mw_50c", outcomes, "mw_food_low_wage_50c"),
            estimate(samples["household_low_educ"], "target_x_mw_increase", outcomes, "mw_food_low_educ_intensity"),
        ],
        ignore_index=True,
    )
    sup, year_support = support(samples, policy)

    policy.to_csv(OUT / "minimum_wage_food_policy.csv", index=False)
    hy.to_parquet(OUT / "minimum_wage_food_household_year_panel.parquet", index=False)
    estimates.to_csv(OUT / "minimum_wage_food_estimates.csv", index=False)
    sup.to_csv(OUT / "minimum_wage_food_support.csv", index=False)
    year_support.to_csv(OUT / "minimum_wage_food_year_support.csv", index=False)

    s_low = sup[sup["sample"].eq("household_low_wage")].iloc[0]
    primary = estimates[estimates["model"].eq("mw_food_low_wage_intensity")].set_index("outcome")
    food = primary.loc["food_insecure"]
    snap = primary.loc["snap_any"]
    verdict = "NO-CLEAN-GO"
    if food["coef"] < -0.03 and food["state_clustered_t"] < -1.5 and snap["coef"] <= 0:
        verdict = "PROMISING-FOOD-SECURITY-SPILLOVER"
    elif food["coef"] < 0:
        verdict = "DIRECTIONAL-BUT-ID-WEAK"

    report = f"""# Minimum Wage Food-Security Spillover Test

## Question

Can current SIPP support an adult paper on state minimum-wage increases, food insecurity, and
safety-net or medical-financial spillovers?

## Source Check

- U.S. Department of Labor historical state minimum wage table:
  https://www.dol.gov/agencies/whd/state/minimum-wage/history
- U.S. Department of Labor current state minimum wage table:
  https://www.dol.gov/agencies/whd/minimum-wage/state

The policy file is reconstructed from the DOL historical state minimum wage table. Effective wage is
the maximum of the listed state wage and the federal floor. For ranges or firm-size variants, this
fast screen uses the highest listed statewide value, so it is a screening policy file rather than a
final statutory treatment panel.

## Design

- Unit: household-year, reference years 2018-2023.
- Primary target: household with at least one adult low-wage worker, defined as age 19-64, at least
  six observed months, employed in at least half of months, annual earnings $1-$35,000, and FPL <=
  300%.
- Secondary target: household with at least one low-education adult.
- Treatment intensity: state minimum-wage increase from prior year x target household.
- Fixed effects: state-year, state-target, target-year.
- Standard errors: clustered by state.

This is stronger than the earlier monthly insurance spillover screen because `RFOODS` and `RFOODR`
are household-year food-security outcomes.

## Support

Primary low-wage household target:

- Household-years: {int(s_low['household_years']):,}.
- Households: {int(s_low['households']):,}.
- Target household-years: {int(s_low['target_household_years']):,}.
- Target household-years with any minimum-wage increase: {int(s_low['target_with_any_mw_increase_household_years']):,}.
- Target household-years with at least $0.50 increase: {int(s_low['target_with_50c_increase_household_years']):,}.

## Main Estimates

Low-wage household, continuous increase intensity:

{fmt(estimates, 'mw_food_low_wage_intensity', main_outcomes)}

Low-wage household, >= $0.50 increase:

{fmt(estimates, 'mw_food_low_wage_50c', main_outcomes)}

Low-education household, continuous increase intensity:

{fmt(estimates, 'mw_food_low_educ_intensity', main_outcomes)}

## Verdict

`{verdict}`

A clean GO would require a robust reduction in food insecurity or SNAP reliance among plausibly
exposed households, stable signs across target definitions, and a sharper exposure measure than the
current compact parquet provides. The current parquet lacks occupation, industry, hourly wage, and
baseline statutory coverage/exemption details.

## Artifacts

- `script/11_idea_scan/21_minimum_wage_food_security_test.py`
- `result/idea_scan/minimum_wage_food_policy.csv`
- `result/idea_scan/minimum_wage_food_household_year_panel.parquet`
- `result/idea_scan/minimum_wage_food_support.csv`
- `result/idea_scan/minimum_wage_food_year_support.csv`
- `result/idea_scan/minimum_wage_food_estimates.csv`
"""
    REPORT.write_text(report, encoding="utf-8")


if __name__ == "__main__":
    main()
