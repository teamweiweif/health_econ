from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
PANEL = ROOT / "data" / "analysis_ready" / "sipp_2018_2024_person_month_panel.parquet"
OUT = ROOT / "result" / "idea_scan"
REPORT = ROOT / "report" / "34_snap_emergency_allotment_fast_test.md"


SOURCES = [
    "USDA, SNAP Emergency Allotments are Ending: https://www.usda.gov/about-usda/news/blog/snap-emergency-allotments-are-ending",
    "CBPP, Temporary Pandemic SNAP Benefits Will End in Remaining 35 States in March 2023: https://www.cbpp.org/research/food-assistance/temporary-pandemic-snap-benefits-will-end-in-remaining-35-states-in-march",
    "Federal Reserve FEDS 2023-046, Termination of SNAP Emergency Allotments, Food Sufficiency, and Economic Hardships: https://www.federalreserve.gov/econres/feds/files/2023046pap.pdf",
    "USDA FNS, Recent changes to SNAP benefit amounts infographic: https://fns-prod.azureedge.us/sites/default/files/resource-files/snap-sunset-ea.pdf",
]


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
    "72": "Puerto Rico",
}

# Exact termination months follow the Federal Reserve FEDS table, which cites USDA.
# For annual SIPP outcomes, active_year is the first reference year with meaningful exposure.
EA_END_MONTH = {
    "16": "2021-03",  # Idaho
    "38": "2021-05",  # North Dakota
    "05": "2021-06",  # Arkansas
    "31": "2021-07",  # Nebraska
    "12": "2021-07",  # Florida
    "46": "2021-07",  # South Dakota
    "30": "2021-07",  # Montana
    "29": "2021-08",  # Missouri
    "28": "2021-12",  # Mississippi
    "47": "2021-12",  # Tennessee
    "19": "2022-03",  # Iowa
    "56": "2022-04",  # Wyoming
    "04": "2022-04",  # Arizona
    "21": "2022-04",  # Kentucky
    "18": "2022-05",  # Indiana
    "13": "2022-05",  # Georgia
    "02": "2022-08",  # Alaska
}

EA_ACTIVE_YEAR = {
    # Ended early enough to affect most or much of reference year 2021.
    "16": 2021,
    "38": 2021,
    "05": 2021,
    "31": 2021,
    "12": 2021,
    "46": 2021,
    "30": 2021,
    "29": 2021,
    # Late-2021 and 2022 exits are first coded as active in 2022.
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

# South Carolina ended in January 2023 after the federal decision to end EA nationally.
# It is excluded from the primary early-ending design.
SOUTH_CAROLINA = "45"


def yes(s: pd.Series) -> pd.Series:
    return s.eq(1)


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


def bounded_numeric(s: pd.Series, lo: float, hi: float) -> pd.Series:
    out = pd.to_numeric(s, errors="coerce")
    return out.where(out.between(lo, hi, inclusive="both"))


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
    df["age"] = pd.to_numeric(df["TAGE"], errors="coerce")
    df["female"] = df["ESEX"].eq(2).astype(float)
    df["educ"] = pd.to_numeric(df["EEDUC"], errors="coerce")
    df["low_educ"] = df["educ"].le(39).astype(float)
    df["fpl"] = bounded_numeric(df["TFINCPOV"], 0, 20)
    df["healthy"] = pd.to_numeric(df["EHLTSTAT"], errors="coerce").between(1, 2).astype(float)
    df["disabled"] = yes(df["RDIS"]).astype(float)
    df["hispanic"] = yes(df["EHISPAN"]).astype(float)
    df["black"] = pd.to_numeric(df["ERACE"], errors="coerce").eq(2).astype(float)
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
    df["doctor_visits"] = bounded_numeric(df["TVISDOC"], 0, 200)
    df["doctor_any"] = df["doctor_visits"].gt(0).astype(float)
    df["dental_any"] = bounded_numeric(df["TVISDENT"], 0, 100).gt(0).astype(float)
    df["oop_any"] = bounded_numeric(df["TMDPAY"], 0, 500_000).gt(0).astype(float)
    df["sick_days"] = bounded_numeric(df["TDAYSICK"], 0, 365)
    df["employed_month"] = (
        pd.to_numeric(df["RMWKWJB"], errors="coerce").gt(0)
        | pd.to_numeric(df["RMESR"], errors="coerce").between(1, 5)
    ).astype(float)
    df["monthly_earnings"] = bounded_numeric(df["TPEARN"], -250_000, 1_000_000)

    py = (
        df.groupby(["person_id", "state_fips", "reference_year"], observed=True)
        .agg(
            months=("person_month_key", "size"),
            weight=("weight", "mean"),
            age=("age", "mean"),
            female=("female", "max"),
            low_educ=("low_educ", "max"),
            fpl=("fpl", "median"),
            healthy=("healthy", "mean"),
            disabled=("disabled", "max"),
            hispanic=("hispanic", "max"),
            black=("black", "max"),
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
    py["state_name"] = py["state_fips"].map(STATE_NAMES)
    py["healthy"] = py["healthy"].ge(0.5).astype(int)
    py["worker"] = py["employed_share"].ge(0.5).astype(int)
    py["low_income"] = py["fpl"].le(3.0).astype(int)
    py["log_earnings"] = np.log1p(py["annual_earnings"].clip(lower=0))
    py["ea_end_year"] = py["state_fips"].map(EA_ACTIVE_YEAR)
    py["ea_end_month"] = py["state_fips"].map(EA_END_MONTH)
    py["early_end_state"] = py["ea_end_year"].notna().astype(int)
    py["ea_ended_active"] = (py["ea_end_year"].notna() & py["reference_year"].ge(py["ea_end_year"])).astype(int)
    py["relative_year"] = py["reference_year"] - py["ea_end_year"]

    py = py.sort_values(["person_id", "reference_year"])
    py["prev_reference_year"] = py.groupby("person_id")["reference_year"].shift(1)
    py["prev_snap_any"] = py.groupby("person_id")["snap_any"].shift(1)
    py["prev_fpl"] = py.groupby("person_id")["fpl"].shift(1)
    py["has_consecutive_lag"] = (
        py["reference_year"].sub(py["prev_reference_year"]).eq(1) & py["prev_snap_any"].notna()
    ).astype(int)
    py["lag_snap_target"] = (py["has_consecutive_lag"].eq(1) & py["prev_snap_any"].eq(1)).astype(int)
    py["current_snap_target"] = py["snap_any"].eq(1).astype(int)
    return py


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
                "n_person_years": n,
                "n_persons": int(s["person_id"].nunique()),
                "n_states": int(s["state_fips"].nunique()),
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
                    "n_person_years": n,
                    "n_persons": int(s["person_id"].nunique()),
                    "n_states": int(s["state_fips"].nunique()),
                }
            )
    return pd.DataFrame(rows)


def build_sample(py: pd.DataFrame, target: str, end_year: int, require_lag: bool) -> pd.DataFrame:
    d = py[
        py["age"].between(18, 64, inclusive="both")
        & py["months"].ge(6)
        & py["fpl"].between(0, 3, inclusive="both")
        & py["state_fips"].ne(SOUTH_CAROLINA)
        & py["reference_year"].between(2018, end_year, inclusive="both")
    ].copy()
    if require_lag:
        d = d[d["has_consecutive_lag"].eq(1)].copy()
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


def support(samples: dict[str, pd.DataFrame]) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    rows = []
    state_rows = []
    event_rows = []
    for name, d in samples.items():
        early_target = d[d["early_end_state"].eq(1) & d["target_snap"].eq(1)]
        active_target = d[d["ea_end_treat"].eq(1)]
        rows.append(
            {
                "sample": name,
                "person_years": int(len(d)),
                "persons": int(d["person_id"].nunique()),
                "states": int(d["state_fips"].nunique()),
                "target_person_years": int(d["target_snap"].sum()),
                "early_end_target_person_years": int(len(early_target)),
                "active_treated_person_years": int(len(active_target)),
                "active_treated_persons": int(active_target["person_id"].nunique()),
                "weighted_mean_food_insecure": wmean(d["food_insecure"], d["weight"]),
                "weighted_mean_very_low_food": wmean(d["very_low_food"], d["weight"]),
                "weighted_mean_food_score": wmean(d["food_score"], d["weight"]),
            }
        )
        by_state = (
            d[d["early_end_state"].eq(1) & d["target_snap"].eq(1)]
            .groupby(["state_fips", "state_name", "reference_year"], observed=True)
            .agg(
                person_years=("person_id", "size"),
                persons=("person_id", "nunique"),
                active=("ea_ended_active", "max"),
                food_insecure_mean=("food_insecure", "mean"),
                very_low_food_mean=("very_low_food", "mean"),
            )
            .reset_index()
        )
        by_state.insert(0, "sample", name)
        state_rows.append(by_state)
        ev = (
            d[d["early_end_state"].eq(1) & d["target_snap"].eq(1)]
            .groupby("relative_year", observed=True)
            .agg(person_years=("person_id", "size"), persons=("person_id", "nunique"))
            .reset_index()
        )
        ev.insert(0, "sample", name)
        event_rows.append(ev)
    return (
        pd.DataFrame(rows),
        pd.concat(state_rows, ignore_index=True) if state_rows else pd.DataFrame(),
        pd.concat(event_rows, ignore_index=True) if event_rows else pd.DataFrame(),
    )


def estimate_leave_one(d: pd.DataFrame, outcomes: list[str]) -> pd.DataFrame:
    rows = []
    for state in EA_ACTIVE_YEAR:
        dd = d[d["state_fips"].ne(state)].copy()
        if dd["ea_end_treat"].sum() == 0:
            continue
        est = estimate(
            dd,
            "ea_end_treat",
            outcomes,
            "snap_ea_lag_snap_leave_one",
            controls=["age", "female", "low_educ", "healthy", "disabled", "black", "hispanic", "prev_fpl"],
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
    samples = {
        "lag_snap_2018_2022": build_sample(py, "lag_snap", end_year=2022, require_lag=True),
        "lag_snap_2018_2023": build_sample(py, "lag_snap", end_year=2023, require_lag=True),
        "current_snap_2018_2022": build_sample(py, "current_snap", end_year=2022, require_lag=False),
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
    primary_outcomes = [
        "food_insecure",
        "very_low_food",
        "food_score",
        "snap_any",
        "doctor_any",
        "oop_any",
        "uninsured",
    ]
    controls_lag = ["age", "female", "low_educ", "healthy", "disabled", "black", "hispanic", "prev_fpl"]
    controls_current = ["age", "female", "low_educ", "healthy", "disabled", "black", "hispanic", "fpl"]

    estimates = pd.concat(
        [
            estimate(
                samples["lag_snap_2018_2022"],
                "ea_end_treat",
                outcomes,
                "snap_ea_early_end_lag_snap_2018_2022",
                controls=controls_lag,
                fe_cols=["state_year", "state_target", "target_year"],
            ),
            estimate(
                samples["lag_snap_2018_2023"],
                "ea_end_treat",
                outcomes,
                "snap_ea_early_end_lag_snap_2018_2023_including_federal_cliff",
                controls=controls_lag,
                fe_cols=["state_year", "state_target", "target_year"],
            ),
            estimate(
                samples["current_snap_2018_2022"],
                "ea_end_treat",
                outcomes,
                "snap_ea_early_end_current_snap_2018_2022",
                controls=controls_current,
                fe_cols=["state_year", "state_target", "target_year"],
            ),
        ],
        ignore_index=True,
    )
    events = estimate_event(
        samples["lag_snap_2018_2022"],
        "target_snap",
        rel_years=[-3, -2, -1, 0, 1],
        omitted=-1,
        outcomes=["food_insecure", "very_low_food", "food_score", "snap_any"],
        model="snap_ea_early_end_lag_snap_event",
        controls=controls_lag,
        fe_cols=["state_year", "state_target", "target_year"],
    )
    leave_one = estimate_leave_one(samples["lag_snap_2018_2022"], ["food_insecure", "very_low_food", "food_score"])
    sup, state_support, event_support = support(samples)

    py.to_parquet(OUT / "snap_ea_person_year_panel.parquet", index=False)
    estimates.to_csv(OUT / "snap_ea_estimates.csv", index=False)
    events.to_csv(OUT / "snap_ea_event.csv", index=False)
    leave_one.to_csv(OUT / "snap_ea_leave_one.csv", index=False)
    sup.to_csv(OUT / "snap_ea_support.csv", index=False)
    state_support.to_csv(OUT / "snap_ea_state_year_support.csv", index=False)
    event_support.to_csv(OUT / "snap_ea_event_support.csv", index=False)

    primary_sup = sup[sup["sample"].eq("lag_snap_2018_2022")].iloc[0]
    current_sup = sup[sup["sample"].eq("current_snap_2018_2022")].iloc[0]
    primary = estimates[estimates["model"].eq("snap_ea_early_end_lag_snap_2018_2022")].set_index("outcome")
    food = primary.loc["food_insecure"]
    very_low = primary.loc["very_low_food"]
    score = primary.loc["food_score"]
    snap = primary.loc["snap_any"]
    verdict = "NO-CLEAN-GO"
    if food["coef"] > 0.03 and food["t"] > 1.5 and score["coef"] > 0.15:
        verdict = "PROMISING-SNAP-EA-FOOD-INSECURITY-SIGNAL"
    elif food["coef"] > 0 and very_low["coef"] > 0 and score["coef"] > 0:
        verdict = "DIRECTIONAL-BUT-WEAK"

    report = f"""# SNAP Emergency Allotment Fast Test

## Question

Can current SIPP support an adult paper on SNAP Emergency Allotment termination, food
insecurity, and health/coverage spillovers?

## Source Checks

{chr(10).join(f"- {s}" for s in SOURCES)}

Policy coding:

- SNAP Emergency Allotments began during 2020.
- The primary design uses the 17 states that ended EA before the 2023 nationwide termination.
- South Carolina is excluded from the primary design because it ended in January 2023, after the
  federal decision to terminate EA nationwide.
- Main analysis period is reference years 2018-2022, so the 2023 nationwide cliff is not used as
  identifying variation.

## Data Construction

- Source parquet: `data/analysis_ready/sipp_2018_2024_person_month_panel.parquet`.
- Unit: person-year collapsed from monthly rows.
- Primary sample: low-income adults age 18-64, FPL <= 300%, valid consecutive prior-year record.
- Primary target: prior-year SNAP recipient, using lagged `RSNAP_YRYN`.
- Treatment: early-EA-ending state x active year x prior-year SNAP target.
- Fixed effects: state-year, state-target, target-year.

Outcomes:

- `food_insecure`: `RFOODS >= 2`.
- `very_low_food`: `RFOODS == 3`.
- `food_score`: `RFOODR`, count of affirmative food-security responses.
- program, utilization, coverage, and labor-market secondary outcomes.

Important measurement note: `RFOODS` and `RFOODR` are constant within person-year in this extract.
This is an annual SIPP screen, not a month-level event study.

## Support

Primary lagged-SNAP sample, 2018-2022:

- Person-years: {int(primary_sup['person_years']):,}.
- Persons: {int(primary_sup['persons']):,}.
- Target person-years: {int(primary_sup['target_person_years']):,}.
- Early-ending-state target person-years: {int(primary_sup['early_end_target_person_years']):,}.
- Active treated person-years: {int(primary_sup['active_treated_person_years']):,}.

Current-year SNAP sensitivity, 2018-2022:

- Person-years: {int(current_sup['person_years']):,}.
- Target person-years: {int(current_sup['target_person_years']):,}.
- Active treated person-years: {int(current_sup['active_treated_person_years']):,}.

## Main Estimates

Primary lagged-SNAP DDD, 2018-2022:

{fmt(estimates, 'snap_ea_early_end_lag_snap_2018_2022', primary_outcomes)}

Lagged-SNAP robustness including 2023 federal cliff:

{fmt(estimates, 'snap_ea_early_end_lag_snap_2018_2023_including_federal_cliff', primary_outcomes)}

Current-year SNAP sensitivity, 2018-2022:

{fmt(estimates, 'snap_ea_early_end_current_snap_2018_2022', primary_outcomes)}

## Event and Robustness Checks

Event estimates for early-ending states, omitting relative year -1, are saved in
`result/idea_scan/snap_ea_event.csv`.

Leave-one-early-ending-state estimates are saved in
`result/idea_scan/snap_ea_leave_one.csv`.

## Verdict

`{verdict}`

A clean GO would require:

- positive effects on `food_insecure`, `very_low_food`, and `food_score`;
- weak or no pre-policy differential movement;
- robustness to current-year SNAP and 2023-inclusive variants;
- and enough treated lagged-SNAP person-years to support state-timing heterogeneity.

This direction is more data-aligned than several insurance-side candidates because SIPP directly
observes food-security outcomes and monthly SNAP participation.

## Artifacts

- `script/11_idea_scan/16_snap_ea_fast_test.py`
- `result/idea_scan/snap_ea_person_year_panel.parquet`
- `result/idea_scan/snap_ea_support.csv`
- `result/idea_scan/snap_ea_state_year_support.csv`
- `result/idea_scan/snap_ea_event_support.csv`
- `result/idea_scan/snap_ea_estimates.csv`
- `result/idea_scan/snap_ea_event.csv`
- `result/idea_scan/snap_ea_leave_one.csv`
"""
    REPORT.write_text(report, encoding="utf-8")


if __name__ == "__main__":
    main()
