from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
PANEL = ROOT / "data" / "analysis_ready" / "sipp_2018_2024_person_month_panel.parquet"
OUT = ROOT / "result" / "idea_scan"
REPORT = ROOT / "report" / "36_snap_ea_household_test.md"


STATE_NAMES = {
    "01": "Alabama",
    "02": "Alaska",
    "04": "Arizona",
    "05": "Arkansas",
    "06": "California",
    "08": "Colorado",
    "09": "Connecticut",
    "10": "Delaware",
    "11": "District of Columbia",
    "12": "Florida",
    "13": "Georgia",
    "15": "Hawaii",
    "16": "Idaho",
    "17": "Illinois",
    "18": "Indiana",
    "19": "Iowa",
    "20": "Kansas",
    "21": "Kentucky",
    "22": "Louisiana",
    "23": "Maine",
    "24": "Maryland",
    "25": "Massachusetts",
    "26": "Michigan",
    "27": "Minnesota",
    "28": "Mississippi",
    "29": "Missouri",
    "30": "Montana",
    "31": "Nebraska",
    "32": "Nevada",
    "33": "New Hampshire",
    "34": "New Jersey",
    "35": "New Mexico",
    "36": "New York",
    "37": "North Carolina",
    "38": "North Dakota",
    "39": "Ohio",
    "40": "Oklahoma",
    "41": "Oregon",
    "42": "Pennsylvania",
    "44": "Rhode Island",
    "45": "South Carolina",
    "46": "South Dakota",
    "47": "Tennessee",
    "48": "Texas",
    "49": "Utah",
    "50": "Vermont",
    "51": "Virginia",
    "53": "Washington",
    "54": "West Virginia",
    "55": "Wisconsin",
    "56": "Wyoming",
}

EA_ACTIVE_YEAR = {
    "16": 2021,
    "38": 2021,
    "05": 2021,
    "31": 2021,
    "12": 2021,
    "46": 2021,
    "30": 2021,
    "29": 2021,
    "28": 2022,
    "47": 2022,
    "19": 2022,
    "56": 2022,
    "04": 2022,
    "21": 2022,
    "18": 2022,
    "13": 2022,
    "02": 2022,
}
SOUTH_CAROLINA = "45"


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


def build_person_year() -> pd.DataFrame:
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
        "EHLTSTAT",
        "RDIS",
        "WPFINWGT",
        "TSSSAMT",
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
        "TVISDENT",
        "TDAYSICK",
        "RMESR",
        "RMWKWJB",
        "TPEARN",
    ]
    df = pd.read_parquet(PANEL, columns=cols)
    df = df[df["reference_year"].between(2017, 2023)].copy()
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
    df["adult"] = df["age"].between(18, 64, inclusive="both")
    df["female"] = df["ESEX"].eq(2).astype(float)
    df["low_educ"] = pd.to_numeric(df["EEDUC"], errors="coerce").le(39).astype(float)
    df["fpl"] = bounded_numeric(df["TFINCPOV"], 0, 20)
    df["healthy"] = pd.to_numeric(df["EHLTSTAT"], errors="coerce").between(1, 2).astype(float)
    df["disabled"] = yes(df["RDIS"]).astype(float)
    df["black"] = pd.to_numeric(df["ERACE"], errors="coerce").eq(2).astype(float)
    df["hispanic"] = yes(df["EHISPAN"]).astype(float)
    df["weight"] = clean_weight(df)
    df["snap_month"] = yes(df["RSNAP_MNYN"]).astype(float)
    df["snap_year"] = yes(df["RSNAP_YRYN"]).astype(float)
    df["food_score"] = bounded_numeric(df["RFOODR"], 0, 6)
    df["food_status"] = bounded_numeric(df["RFOODS"], 1, 3)
    df["food_insecure"] = df["food_status"].ge(2).astype(float)
    df["very_low_food"] = df["food_status"].eq(3).astype(float)
    df["any_coverage"] = yes(df["RHLTHMTH"]).astype(float)
    df["uninsured"] = df["RHLTHMTH"].eq(2).astype(float)
    df["private"] = yes(df["RPRIMTH"]).astype(float)
    df["public"] = (yes(df["RPUBMTH"]) | yes(df["EMDMTH"])).astype(float)
    df["doctor_any"] = bounded_numeric(df["TVISDOC"], 0, 200).gt(0).astype(float)
    df["doctor_visits"] = bounded_numeric(df["TVISDOC"], 0, 200)
    df["dental_any"] = bounded_numeric(df["TVISDENT"], 0, 100).gt(0).astype(float)
    df["oop_any"] = bounded_numeric(df["TMDPAY"], 0, 500_000).gt(0).astype(float)
    df["sick_days"] = bounded_numeric(df["TDAYSICK"], 0, 365)
    df["employed_month"] = (
        pd.to_numeric(df["RMWKWJB"], errors="coerce").gt(0)
        | pd.to_numeric(df["RMESR"], errors="coerce").between(1, 5)
    ).astype(float)
    df["monthly_earnings"] = bounded_numeric(df["TPEARN"], -250_000, 1_000_000)

    py = (
        df.groupby(["person_id", "hh_id", "state_fips", "reference_year"], observed=True)
        .agg(
            months=("person_month_key", "size"),
            weight=("weight", "mean"),
            age=("age", "mean"),
            adult=("adult", "max"),
            female=("female", "max"),
            low_educ=("low_educ", "max"),
            fpl=("fpl", "median"),
            healthy=("healthy", "mean"),
            disabled=("disabled", "max"),
            black=("black", "max"),
            hispanic=("hispanic", "max"),
            snap_share=("snap_month", "mean"),
            snap_any=("snap_year", "max"),
            food_score=("food_score", "max"),
            food_insecure=("food_insecure", "max"),
            very_low_food=("very_low_food", "max"),
            any_coverage=("any_coverage", "mean"),
            uninsured=("uninsured", "mean"),
            private=("private", "mean"),
            public=("public", "mean"),
            doctor_any=("doctor_any", "mean"),
            doctor_visits=("doctor_visits", "mean"),
            dental_any=("dental_any", "mean"),
            oop_any=("oop_any", "mean"),
            sick_days=("sick_days", "mean"),
            employed_share=("employed_month", "mean"),
            annual_earnings=("monthly_earnings", "sum"),
        )
        .reset_index()
    )
    py = py.sort_values(["person_id", "reference_year"])
    py["prev_reference_year"] = py.groupby("person_id")["reference_year"].shift(1)
    py["prev_snap_any"] = py.groupby("person_id")["snap_any"].shift(1)
    py["prev_fpl"] = py.groupby("person_id")["fpl"].shift(1)
    py["has_consecutive_lag"] = (
        py["reference_year"].sub(py["prev_reference_year"]).eq(1) & py["prev_snap_any"].notna()
    ).astype(int)
    py["lag_snap_target_person"] = (
        py["has_consecutive_lag"].eq(1) & py["prev_snap_any"].eq(1)
    ).astype(int)
    py["current_snap_target_person"] = py["snap_any"].eq(1).astype(int)
    return py


def build_household_year(py: pd.DataFrame) -> pd.DataFrame:
    hy = (
        py.groupby(["hh_id", "state_fips", "reference_year"], observed=True)
        .agg(
            household_members=("person_id", "nunique"),
            adult_members=("adult", "sum"),
            lag_observed_adults=("has_consecutive_lag", "sum"),
            lag_snap_persons=("lag_snap_target_person", "sum"),
            current_snap_persons=("current_snap_target_person", "sum"),
            weight=("weight", "mean"),
            age=("age", "mean"),
            female_share=("female", "mean"),
            low_educ_share=("low_educ", "mean"),
            fpl=("fpl", "median"),
            prev_fpl=("prev_fpl", "median"),
            healthy_share=("healthy", "mean"),
            disabled_any=("disabled", "max"),
            black_any=("black", "max"),
            hispanic_any=("hispanic", "max"),
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
            doctor_visits=("doctor_visits", "mean"),
            dental_any=("dental_any", "mean"),
            oop_any=("oop_any", "mean"),
            sick_days=("sick_days", "mean"),
            employed_share=("employed_share", "mean"),
            annual_earnings=("annual_earnings", "sum"),
        )
        .reset_index()
    )
    hy["state_name"] = hy["state_fips"].map(STATE_NAMES)
    hy["early_end_year"] = hy["state_fips"].map(EA_ACTIVE_YEAR)
    hy["early_end_state"] = hy["early_end_year"].notna().astype(int)
    hy["ea_ended_active"] = (
        hy["early_end_year"].notna() & hy["reference_year"].ge(hy["early_end_year"])
    ).astype(int)
    hy["relative_year"] = hy["reference_year"] - hy["early_end_year"]
    hy["lag_snap_target"] = hy["lag_snap_persons"].gt(0).astype(int)
    hy["current_snap_target"] = hy["current_snap_persons"].gt(0).astype(int)
    hy["log_earnings"] = np.log1p(hy["annual_earnings"].clip(lower=0))
    return hy


def add_fe(parts: list[pd.Series | pd.DataFrame], d: pd.DataFrame, fe_cols: list[str]) -> pd.DataFrame:
    for col in fe_cols:
        parts.append(pd.get_dummies(d[col].astype(str), prefix=col, drop_first=True, dtype=float))
    return pd.concat(parts, axis=1)


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
        parts: list[pd.Series | pd.DataFrame] = [pd.Series(1.0, index=s.index, name="const"), s[term].astype(float)]
        for c in controls:
            parts.append(s[c].astype(float).rename(c))
        x = add_fe(parts, s, fe_cols)
        beta, se, n = wls_hc1(s[outcome].to_numpy(dtype=float), x.to_numpy(dtype=float), s["weight"].to_numpy(dtype=float))
        b = pd.Series(beta, index=x.columns)
        serr = pd.Series(se, index=x.columns)
        se_term = serr.get(term, np.nan)
        rows.append(
            {
                "model": model,
                "outcome": outcome,
                "term": term,
                "coef": b.get(term, np.nan),
                "se": se_term,
                "t": b.get(term, np.nan) / se_term if se_term else np.nan,
                "n_household_years": n,
                "n_households": int(s["hh_id"].nunique()),
                "n_states": int(s["state_fips"].nunique()),
                "weighted_mean": wmean(s[outcome], s["weight"]),
            }
        )
    return pd.DataFrame(rows)


def estimate_cluster(
    d: pd.DataFrame,
    term: str,
    outcomes: list[str],
    model: str,
    controls: list[str],
    fe_cols: list[str],
    cluster_col: str,
) -> pd.DataFrame:
    rows = []
    for outcome in outcomes:
        s = d[d[outcome].notna() & d["weight"].gt(0)].copy()
        parts: list[pd.Series | pd.DataFrame] = [pd.Series(1.0, index=s.index, name="const"), s[term].astype(float)]
        for c in controls:
            parts.append(s[c].astype(float).rename(c))
        x = add_fe(parts, s, fe_cols)
        beta, se, n, g = wls_cluster(
            s[outcome].to_numpy(dtype=float),
            x.to_numpy(dtype=float),
            s["weight"].to_numpy(dtype=float),
            s[cluster_col].to_numpy(),
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


def estimate_event(
    d: pd.DataFrame,
    target_col: str,
    rel_years: list[int],
    omitted: int,
    outcomes: list[str],
    model: str,
    controls: list[str],
    fe_cols: list[str],
) -> pd.DataFrame:
    d = d.copy()
    terms = []
    for rel in rel_years:
        if rel == omitted:
            continue
        label = f"m{abs(rel)}" if rel < 0 else f"p{rel}"
        term = f"{target_col}_rel_{label}"
        d[term] = (
            d[target_col].astype(float)
            * d["early_end_state"].astype(float)
            * d["relative_year"].eq(rel).astype(float)
        )
        terms.append(term)
    rows = []
    for outcome in outcomes:
        s = d[d[outcome].notna() & d["weight"].gt(0)].copy()
        parts: list[pd.Series | pd.DataFrame] = [pd.Series(1.0, index=s.index, name="const"), s[terms]]
        for c in controls:
            parts.append(s[c].astype(float).rename(c))
        x = add_fe(parts, s, fe_cols)
        beta, se, n = wls_hc1(s[outcome].to_numpy(dtype=float), x.to_numpy(dtype=float), s["weight"].to_numpy(dtype=float))
        b = pd.Series(beta, index=x.columns)
        serr = pd.Series(se, index=x.columns)
        for rel in rel_years:
            if rel == omitted:
                continue
            label = f"m{abs(rel)}" if rel < 0 else f"p{rel}"
            term = f"{target_col}_rel_{label}"
            se_term = serr.get(term, np.nan)
            rows.append(
                {
                    "model": model,
                    "outcome": outcome,
                    "relative_year": rel,
                    "term": term,
                    "coef": b.get(term, np.nan),
                    "se": se_term,
                    "t": b.get(term, np.nan) / se_term if se_term else np.nan,
                    "n_household_years": n,
                    "n_households": int(s["hh_id"].nunique()),
                    "n_states": int(s["state_fips"].nunique()),
                }
            )
    return pd.DataFrame(rows)


def build_sample(hy: pd.DataFrame, target: str, end_year: int, require_lag: bool) -> pd.DataFrame:
    d = hy[
        hy["reference_year"].between(2018, end_year, inclusive="both")
        & hy["state_fips"].ne(SOUTH_CAROLINA)
        & hy["adult_members"].gt(0)
        & hy["fpl"].between(0, 3, inclusive="both")
    ].copy()
    if require_lag:
        d = d[d["lag_observed_adults"].gt(0)].copy()
    if target == "lag_snap":
        d["target_snap"] = d["lag_snap_target"]
    elif target == "current_snap":
        d["target_snap"] = d["current_snap_target"]
    else:
        raise ValueError(target)
    d["ea_end_treat"] = d["ea_ended_active"] * d["target_snap"]
    d["state_year"] = d["state_fips"] + "_" + d["reference_year"].astype(str)
    d["state_target"] = d["state_fips"] + "_" + d["target_snap"].astype(str)
    d["target_year"] = d["target_snap"].astype(str) + "_" + d["reference_year"].astype(str)
    return d


def support(samples: dict[str, pd.DataFrame]) -> tuple[pd.DataFrame, pd.DataFrame]:
    rows = []
    state_rows = []
    for name, d in samples.items():
        active = d[d["ea_end_treat"].eq(1)]
        rows.append(
            {
                "sample": name,
                "household_years": int(len(d)),
                "households": int(d["hh_id"].nunique()),
                "states": int(d["state_fips"].nunique()),
                "target_household_years": int(d["target_snap"].sum()),
                "early_end_target_household_years": int(
                    len(d[d["early_end_state"].eq(1) & d["target_snap"].eq(1)])
                ),
                "active_treated_household_years": int(len(active)),
                "weighted_mean_food_insecure": wmean(d["food_insecure"], d["weight"]),
                "weighted_mean_very_low_food": wmean(d["very_low_food"], d["weight"]),
                "weighted_mean_food_score": wmean(d["food_score"], d["weight"]),
            }
        )
        by_state = (
            d[d["early_end_state"].eq(1) & d["target_snap"].eq(1)]
            .groupby(["state_fips", "state_name", "reference_year"], observed=True)
            .agg(
                household_years=("hh_id", "size"),
                active=("ea_ended_active", "max"),
                food_insecure_mean=("food_insecure", "mean"),
                food_score_mean=("food_score", "mean"),
            )
            .reset_index()
        )
        by_state.insert(0, "sample", name)
        state_rows.append(by_state)
    return pd.DataFrame(rows), pd.concat(state_rows, ignore_index=True)


def estimate_leave_one(d: pd.DataFrame, outcomes: list[str]) -> pd.DataFrame:
    rows = []
    controls = ["age", "female_share", "low_educ_share", "healthy_share", "disabled_any", "black_any", "hispanic_any", "prev_fpl"]
    for state in EA_ACTIVE_YEAR:
        dd = d[d["state_fips"].ne(state)].copy()
        if dd["ea_end_treat"].sum() == 0:
            continue
        est = estimate(
            dd,
            "ea_end_treat",
            outcomes,
            "snap_ea_household_lag_snap_leave_one",
            controls=controls,
            fe_cols=["state_year", "state_target", "target_year"],
        )
        est.insert(1, "excluded_state", state)
        est.insert(2, "excluded_state_name", STATE_NAMES[state])
        rows.append(est)
    return pd.concat(rows, ignore_index=True) if rows else pd.DataFrame()


def fmt(est: pd.DataFrame, model: str, outcomes: list[str]) -> str:
    d = est[est["model"].eq(model)].set_index("outcome")
    lines = []
    for outcome in outcomes:
        if outcome not in d.index:
            continue
        r = d.loc[outcome]
        lines.append(f"- `{outcome}`: {r['coef']:+.4f}, se {r['se']:.4f}, t {r['t']:.2f}.")
    return "\n".join(lines)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    py = build_person_year()
    hy = build_household_year(py)
    samples = {
        "household_lag_snap_2018_2022": build_sample(hy, "lag_snap", 2022, require_lag=True),
        "household_lag_snap_2018_2023": build_sample(hy, "lag_snap", 2023, require_lag=True),
        "household_current_snap_2018_2022": build_sample(hy, "current_snap", 2022, require_lag=False),
    }
    outcomes = [
        "food_insecure",
        "very_low_food",
        "food_score",
        "snap_any",
        "snap_share",
        "doctor_any",
        "doctor_visits",
        "dental_any",
        "oop_any",
        "sick_days",
        "any_coverage",
        "uninsured",
        "public",
        "private",
        "employed_share",
        "log_earnings",
    ]
    primary_outcomes = ["food_insecure", "very_low_food", "food_score", "snap_any", "doctor_any", "oop_any", "uninsured"]
    controls_lag = ["age", "female_share", "low_educ_share", "healthy_share", "disabled_any", "black_any", "hispanic_any", "prev_fpl"]
    controls_current = ["age", "female_share", "low_educ_share", "healthy_share", "disabled_any", "black_any", "hispanic_any", "fpl"]

    estimates = pd.concat(
        [
            estimate(
                samples["household_lag_snap_2018_2022"],
                "ea_end_treat",
                outcomes,
                "snap_ea_household_lag_snap_2018_2022",
                controls_lag,
                ["state_year", "state_target", "target_year"],
            ),
            estimate(
                samples["household_lag_snap_2018_2023"],
                "ea_end_treat",
                outcomes,
                "snap_ea_household_lag_snap_2018_2023_including_federal_cliff",
                controls_lag,
                ["state_year", "state_target", "target_year"],
            ),
            estimate(
                samples["household_current_snap_2018_2022"],
                "ea_end_treat",
                outcomes,
                "snap_ea_household_current_snap_2018_2022",
                controls_current,
                ["state_year", "state_target", "target_year"],
            ),
        ],
        ignore_index=True,
    )
    cluster_estimates = pd.concat(
        [
            estimate_cluster(
                samples["household_lag_snap_2018_2022"],
                "ea_end_treat",
                primary_outcomes,
                "snap_ea_household_lag_snap_2018_2022_state_cluster",
                controls_lag,
                ["state_year", "state_target", "target_year"],
                "state_fips",
            ),
            estimate_cluster(
                samples["household_current_snap_2018_2022"],
                "ea_end_treat",
                primary_outcomes,
                "snap_ea_household_current_snap_2018_2022_state_cluster",
                controls_current,
                ["state_year", "state_target", "target_year"],
                "state_fips",
            ),
        ],
        ignore_index=True,
    )
    events = estimate_event(
        samples["household_lag_snap_2018_2022"],
        "target_snap",
        [-3, -2, -1, 0, 1],
        -1,
        ["food_insecure", "very_low_food", "food_score", "snap_any"],
        "snap_ea_household_lag_snap_event",
        controls_lag,
        ["state_year", "state_target", "target_year"],
    )
    leave_one = estimate_leave_one(samples["household_lag_snap_2018_2022"], ["food_insecure", "very_low_food", "food_score"])
    sup, state_support = support(samples)

    hy.to_parquet(OUT / "snap_ea_household_year_panel.parquet", index=False)
    estimates.to_csv(OUT / "snap_ea_household_estimates.csv", index=False)
    cluster_estimates.to_csv(OUT / "snap_ea_household_estimates_state_cluster.csv", index=False)
    events.to_csv(OUT / "snap_ea_household_event.csv", index=False)
    leave_one.to_csv(OUT / "snap_ea_household_leave_one.csv", index=False)
    sup.to_csv(OUT / "snap_ea_household_support.csv", index=False)
    state_support.to_csv(OUT / "snap_ea_household_state_year_support.csv", index=False)

    primary_sup = sup[sup["sample"].eq("household_lag_snap_2018_2022")].iloc[0]
    current_sup = sup[sup["sample"].eq("household_current_snap_2018_2022")].iloc[0]
    primary = estimates[estimates["model"].eq("snap_ea_household_lag_snap_2018_2022")].set_index("outcome")
    primary_cluster = cluster_estimates[
        cluster_estimates["model"].eq("snap_ea_household_lag_snap_2018_2022_state_cluster")
    ].set_index("outcome")
    food = primary.loc["food_insecure"]
    score = primary.loc["food_score"]
    food_cluster = primary_cluster.loc["food_insecure"]
    verdict = "NO-CLEAN-GO"
    if food["coef"] > 0.04 and food["t"] > 1.5 and score["coef"] > 0.10:
        verdict = "CONDITIONAL-HOUSEHOLD-LEVEL-LEAD"
    elif food["coef"] > 0:
        verdict = "DIRECTIONAL-BUT-WEAK"

    report = f"""# SNAP Emergency Allotment Household-Level Test

## Question

Does the SNAP Emergency Allotment signal survive when food-security outcomes are treated as
household-year outcomes rather than repeated person-year outcomes?

## Why This Test Was Needed

`RFOODS` and `RFOODR` are identical within every household-year in the compact parquet. The previous
person-year screen was useful, but it may overweight multi-adult households. This test collapses to
household-year before estimating the early-EA-ending design.

## Design

- Unit: household-year, identified by `SSUID + SHHADID + RFAMNUM + reference_year`.
- Sample: low-income households with at least one adult age 18-64 and FPL <= 300%.
- Primary target: any current adult in the household was observed in the prior year and received
  SNAP in that prior year.
- Treatment: early-EA-ending state x active year x lagged-SNAP household target.
- Main period: reference years 2018-2022, excluding South Carolina.
- Fixed effects: state-year, state-target, target-year.

## Support

Primary household lagged-SNAP sample, 2018-2022:

- Household-years: {int(primary_sup['household_years']):,}.
- Households: {int(primary_sup['households']):,}.
- Target household-years: {int(primary_sup['target_household_years']):,}.
- Early-ending-state target household-years: {int(primary_sup['early_end_target_household_years']):,}.
- Active treated household-years: {int(primary_sup['active_treated_household_years']):,}.

Current-year SNAP sensitivity, 2018-2022:

- Household-years: {int(current_sup['household_years']):,}.
- Target household-years: {int(current_sup['target_household_years']):,}.
- Active treated household-years: {int(current_sup['active_treated_household_years']):,}.

## Main Estimates

Primary household lagged-SNAP DDD, 2018-2022:

{fmt(estimates, 'snap_ea_household_lag_snap_2018_2022', primary_outcomes)}

State-clustered check for the primary `food_insecure` estimate:

- `food_insecure`: {food_cluster['coef']:+.4f}, state-clustered se {food_cluster['state_clustered_se']:.4f}, t {food_cluster['state_clustered_t']:.2f}.

Household lagged-SNAP robustness including 2023 federal cliff:

{fmt(estimates, 'snap_ea_household_lag_snap_2018_2023_including_federal_cliff', primary_outcomes)}

Household current-year SNAP sensitivity, 2018-2022:

{fmt(estimates, 'snap_ea_household_current_snap_2018_2022', primary_outcomes)}

## Verdict

`{verdict}`

The household-level test is stricter than the person-year screen. A genuine upgrade would require the
lagged-SNAP household estimates to remain positive on `food_insecure` and `food_score`, with no
large pre-period contradiction in the event file.

## Artifacts

- `script/11_idea_scan/17_snap_ea_household_test.py`
- `result/idea_scan/snap_ea_household_year_panel.parquet`
- `result/idea_scan/snap_ea_household_support.csv`
- `result/idea_scan/snap_ea_household_state_year_support.csv`
- `result/idea_scan/snap_ea_household_estimates.csv`
- `result/idea_scan/snap_ea_household_estimates_state_cluster.csv`
- `result/idea_scan/snap_ea_household_event.csv`
- `result/idea_scan/snap_ea_household_leave_one.csv`
"""
    REPORT.write_text(report, encoding="utf-8")


if __name__ == "__main__":
    main()
