from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
PANEL = ROOT / "data" / "analysis_ready" / "sipp_2018_2024_person_month_panel.parquet"
OUT = ROOT / "result" / "idea_scan"
REPORT = ROOT / "report" / "40_pandemic_ui_food_security_test.md"


SOURCES = [
    "U.S. Department of Labor UIPL 14-21 Change 1: https://www.dol.gov/node/162738",
    "St. Louis Fed, The End of Emergency Pandemic Unemployment Benefits in 2021: https://www.stlouisfed.org/on-the-economy/2022/apr/end-emergency-pandemic-unemployment-benefits-2021",
    "St. Louis Fed, Ending Pandemic Unemployment Benefits Linked to Job Growth: https://www.stlouisfed.org/on-the-economy/2022/aug/ending-pandemic-unemployment-benefits-linked-job-growth",
    "NBER WP 29575, Early Withdrawal of Pandemic Unemployment Insurance: https://www.nber.org/papers/w29575",
]


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

EARLY_EXIT_STATES = {
    "AL",
    "AK",
    "AZ",
    "AR",
    "FL",
    "GA",
    "ID",
    "IN",
    "IA",
    "LA",
    "MD",
    "MS",
    "MO",
    "MT",
    "NE",
    "NH",
    "ND",
    "OH",
    "OK",
    "SC",
    "SD",
    "TN",
    "TX",
    "UT",
    "WV",
    "WY",
}
EARLY_FIPS = {STATE[s] for s in EARLY_EXIT_STATES}


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


def build_person_year() -> pd.DataFrame:
    cols = [
        "SSUID",
        "SHHADID",
        "RFAMNUM",
        "person_id",
        "person_month_key",
        "reference_year",
        "reference_month",
        "state_fips",
        "TAGE",
        "ESEX",
        "ERACE",
        "EHISPAN",
        "EEDUC",
        "TFINCPOV",
        "WPFINWGT",
        "TSSSAMT",
        "EUC1MNYN",
        "EUC2MNYN",
        "EUC3MNYN",
        "RMESR",
        "RMWKWJB",
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
    df = df[df["reference_year"].between(2020, 2021)].copy()
    df["state_fips"] = df["state_fips"].astype(str).str.zfill(2)
    df["age"] = pd.to_numeric(df["TAGE"], errors="coerce")
    df["prime_age"] = df["age"].between(25, 54, inclusive="both")
    df["fpl"] = bounded_numeric(df["TFINCPOV"], 0, 20)
    df["low_mid_income"] = df["fpl"].le(4)
    df["female"] = df["ESEX"].eq(2).astype(float)
    df["low_educ"] = pd.to_numeric(df["EEDUC"], errors="coerce").le(39).astype(float)
    df["black"] = pd.to_numeric(df["ERACE"], errors="coerce").eq(2).astype(float)
    df["hispanic"] = yes(df["EHISPAN"]).astype(float)
    df["weight"] = clean_weight(df)
    df["ui_any_month"] = (
        yes(df["EUC1MNYN"]) | yes(df["EUC2MNYN"]) | yes(df["EUC3MNYN"])
    ).astype(float)
    df["employed_month"] = (
        pd.to_numeric(df["RMWKWJB"], errors="coerce").gt(0)
        | pd.to_numeric(df["RMESR"], errors="coerce").between(1, 5)
    ).astype(float)
    df["no_job_month"] = pd.to_numeric(df["RMWKWJB"], errors="coerce").eq(0).astype(float)
    df["looking_layoff_month"] = pd.to_numeric(df["RMESR"], errors="coerce").eq(6).astype(float)
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

    # Define target from pre-termination 2021 months only.
    pre2021 = df[
        df["reference_year"].eq(2021)
        & df["reference_month"].between(1, 5)
        & df["prime_age"]
        & df["low_mid_income"]
    ]
    target = (
        pre2021.groupby("person_id", observed=True)
        .agg(
            target_ui=("ui_any_month", "max"),
            target_nonemployment=("no_job_month", "max"),
            target_layofflooking=("looking_layoff_month", "max"),
        )
        .reset_index()
    )
    target["target_broad"] = (
        target[["target_ui", "target_nonemployment", "target_layofflooking"]].max(axis=1)
    )

    py = (
        df[df["prime_age"] & df["low_mid_income"]]
        .groupby(["person_id", "state_fips", "reference_year"], observed=True)
        .agg(
            months=("person_month_key", "size"),
            weight=("weight", "mean"),
            age=("age", "mean"),
            fpl=("fpl", "median"),
            female=("female", "max"),
            low_educ=("low_educ", "max"),
            black=("black", "max"),
            hispanic=("hispanic", "max"),
            ui_any=("ui_any_month", "max"),
            ui_share=("ui_any_month", "mean"),
            employed_share=("employed_month", "mean"),
            no_job_share=("no_job_month", "mean"),
            earnings=("earnings", "sum"),
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
    py = py.merge(target, on="person_id", how="inner")
    for c in ["target_ui", "target_nonemployment", "target_layofflooking", "target_broad"]:
        py[c] = py[c].fillna(0).astype(int)
    py["post_2021"] = py["reference_year"].eq(2021).astype(int)
    py["early_exit"] = py["state_fips"].isin(EARLY_FIPS).astype(int)
    py["log_earnings"] = np.log1p(py["earnings"].clip(lower=0))
    return py


def build_sample(py: pd.DataFrame, target_col: str, require_balanced: bool = True) -> pd.DataFrame:
    d = py.copy()
    if require_balanced:
        counts = d.groupby("person_id")["reference_year"].nunique()
        balanced_ids = counts[counts.eq(2)].index
        d = d[d["person_id"].isin(balanced_ids)].copy()
    d["target"] = d[target_col].astype(int)
    d["early_x_target_x_post"] = d["early_exit"] * d["target"] * d["post_2021"]
    d["state_year"] = d["state_fips"] + "_" + d["reference_year"].astype(str)
    d["state_target"] = d["state_fips"] + "_" + d["target"].astype(str)
    d["target_year"] = d["target"].astype(str) + "_" + d["reference_year"].astype(str)
    return d


def estimate(d: pd.DataFrame, outcomes: list[str], model: str, controls: list[str]) -> pd.DataFrame:
    rows = []
    term = "early_x_target_x_post"
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
                "coef": b.get(term, np.nan),
                "state_clustered_se": se_term,
                "state_clustered_t": b.get(term, np.nan) / se_term if se_term else np.nan,
                "n_person_years": n,
                "n_persons": int(s["person_id"].nunique()),
                "n_states": int(s["state_fips"].nunique()),
                "n_clusters": g,
                "weighted_mean": wmean(s[outcome], s["weight"]),
            }
        )
    return pd.DataFrame(rows)


def support(samples: dict[str, pd.DataFrame]) -> pd.DataFrame:
    rows = []
    for name, d in samples.items():
        treated = d[d["early_exit"].eq(1) & d["target"].eq(1) & d["post_2021"].eq(1)]
        rows.append(
            {
                "sample": name,
                "person_years": int(len(d)),
                "persons": int(d["person_id"].nunique()),
                "states": int(d["state_fips"].nunique()),
                "target_person_years": int(d["target"].sum()),
                "target_persons": int(d.loc[d["target"].eq(1), "person_id"].nunique()),
                "early_target_2021_persons": int(treated["person_id"].nunique()),
                "early_target_2021_person_years": int(len(treated)),
                "control_target_2021_persons": int(
                    d.loc[d["early_exit"].eq(0) & d["target"].eq(1) & d["post_2021"].eq(1), "person_id"].nunique()
                ),
                "weighted_mean_food_insecure": wmean(d["food_insecure"], d["weight"]),
            }
        )
    return pd.DataFrame(rows)


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
    py = build_person_year()
    samples = {
        "balanced_target_ui": build_sample(py, "target_ui", require_balanced=True),
        "balanced_target_broad": build_sample(py, "target_broad", require_balanced=True),
        "unbalanced_target_ui": build_sample(py, "target_ui", require_balanced=False),
    }
    outcomes = [
        "food_insecure",
        "very_low_food",
        "food_score",
        "snap_any",
        "snap_share",
        "ui_any",
        "ui_share",
        "employed_share",
        "log_earnings",
        "any_coverage",
        "uninsured",
        "public",
        "private",
        "doctor_any",
        "oop_any",
        "sick_days",
    ]
    main_outcomes = [
        "food_insecure",
        "very_low_food",
        "food_score",
        "snap_any",
        "ui_any",
        "employed_share",
        "uninsured",
        "oop_any",
    ]
    controls = ["age", "fpl", "female", "low_educ", "black", "hispanic"]
    estimates = pd.concat(
        [
            estimate(samples["balanced_target_ui"], outcomes, "ui_food_balanced_target_ui", controls),
            estimate(samples["balanced_target_broad"], outcomes, "ui_food_balanced_target_broad", controls),
            estimate(samples["unbalanced_target_ui"], outcomes, "ui_food_unbalanced_target_ui", controls),
        ],
        ignore_index=True,
    )
    sup = support(samples)

    py.to_parquet(OUT / "pandemic_ui_food_person_year_panel.parquet", index=False)
    estimates.to_csv(OUT / "pandemic_ui_food_estimates.csv", index=False)
    sup.to_csv(OUT / "pandemic_ui_food_support.csv", index=False)

    s_ui = sup[sup["sample"].eq("balanced_target_ui")].iloc[0]
    s_broad = sup[sup["sample"].eq("balanced_target_broad")].iloc[0]
    primary = estimates[estimates["model"].eq("ui_food_balanced_target_ui")].set_index("outcome")
    food = primary.loc["food_insecure"]
    ui = primary.loc["ui_any"]
    verdict = "NO-CLEAN-GO"
    if food["coef"] > 0.04 and food["state_clustered_t"] > 1.5 and ui["coef"] < 0:
        verdict = "PROMISING-UI-FOOD-INSECURITY-SIGNAL"
    elif food["coef"] > 0:
        verdict = "DIRECTIONAL-BUT-WEAK"

    report = f"""# Pandemic UI Early Termination Food-Security Test

## Question

Does the 2021 early termination of federal pandemic unemployment benefits show a SIPP food-security
or safety-net spillover signal?

## Source Checks

{chr(10).join(f"- {s}" for s in SOURCES)}

The policy shock is already verified in the earlier UI screen: 26 states stopped at least FPUC before
the September 2021 federal expiration. This follow-up asks whether SIPP's direct food-security
outcomes make the design more useful than the previous insurance-only screen.

## Design

- Unit: person-year, reference years 2020 and 2021.
- Sample: prime-age adults 25-54 with FPL <= 400%.
- Primary target: received unemployment compensation in January-May 2021.
- Treatment: early-exit state x target x 2021.
- Fixed effects: state-year, state-target, target-year.
- Standard errors: clustered by state.

Important measurement note: `RFOODS` and `RFOODR` are annual household food-security measures
repeated on person records. This is a quick screen, not a final household-level estimator.

## Support

Balanced UI-recipient target sample:

- Person-years: {int(s_ui['person_years']):,}.
- Persons: {int(s_ui['persons']):,}.
- Target persons: {int(s_ui['target_persons']):,}.
- Early-exit target persons in 2021: {int(s_ui['early_target_2021_persons']):,}.
- Control target persons in 2021: {int(s_ui['control_target_2021_persons']):,}.

Balanced broad-risk target sample:

- Person-years: {int(s_broad['person_years']):,}.
- Persons: {int(s_broad['persons']):,}.
- Target persons: {int(s_broad['target_persons']):,}.
- Early-exit target persons in 2021: {int(s_broad['early_target_2021_persons']):,}.

## Main Estimates

Balanced UI-recipient target:

{fmt(estimates, 'ui_food_balanced_target_ui', main_outcomes)}

Balanced broad-risk target:

{fmt(estimates, 'ui_food_balanced_target_broad', main_outcomes)}

Unbalanced UI-recipient sensitivity:

{fmt(estimates, 'ui_food_unbalanced_target_ui', main_outcomes)}

## Verdict

`{verdict}`

A clean GO would require a negative first-stage effect on UI receipt, a coherent increase in food
insecurity or SNAP substitution, and enough target support that the estimate is not just a small-cell
artifact.

## Artifacts

- `script/11_idea_scan/19_pandemic_ui_food_security_test.py`
- `result/idea_scan/pandemic_ui_food_person_year_panel.parquet`
- `result/idea_scan/pandemic_ui_food_support.csv`
- `result/idea_scan/pandemic_ui_food_estimates.csv`
"""
    REPORT.write_text(report, encoding="utf-8")


if __name__ == "__main__":
    main()
