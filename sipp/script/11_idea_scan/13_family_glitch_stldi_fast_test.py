from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
PANEL = ROOT / "data" / "analysis_ready" / "sipp_2018_2024_person_month_panel.parquet"
OUT = ROOT / "result" / "idea_scan"
REPORT = ROOT / "report" / "28_family_glitch_stldi_fast_test.md"


SOURCES = [
    "Federal Register final rule, Affordability of Employer Coverage for Family Members of Employees: https://www.federalregister.gov/documents/2022/10/13/2022-22184/affordability-of-employer-coverage-for-family-members-of-employees",
    "CMS family glitch technical assistance PDF: https://www.cms.gov/marketplace/technical-assistance-resources/afford-employer-coverage-fixing-family-glitch.pdf",
    "Commonwealth Fund short-term plan state regulation issue brief: https://www.commonwealthfund.org/publications/issue-briefs/2019/may/states-step-up-protect-markets-consumers-short-term-plans",
    "Federal Register 2018 short-term limited-duration insurance final rule: https://www.federalregister.gov/documents/2018/08/03/2018-16568/short-term-limited-duration-insurance",
    "KFF short-term plan availability summary: https://www.kff.org/patient-consumer-protections/examining-short-term-limited-duration-health-plans-on-the-eve-of-aca-marketplace-open-enrollment/",
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
}

# Conservative "protective" STLDI coding for the 2018 federal expansion screen:
# bans or very restrictive/no-availability style regimes based on Commonwealth/KFF summaries.
STLDI_PROTECTIVE = {
    "06",  # CA
    "08",  # CO
    "09",  # CT
    "11",  # DC
    "15",  # HI
    "17",  # IL
    "23",  # ME
    "24",  # MD
    "25",  # MA
    "27",  # MN
    "34",  # NJ
    "35",  # NM
    "36",  # NY
    "44",  # RI
    "50",  # VT
    "53",  # WA
}


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


def build_person_year() -> pd.DataFrame:
    cols = [
        "SSUID",
        "PNUM",
        "SHHADID",
        "RFAMNUM",
        "person_id",
        "person_month_key",
        "reference_year",
        "reference_date",
        "state_fips",
        "TAGE",
        "TFINCPOV",
        "EHLTSTAT",
        "EPNSPOUSE",
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
    df["age"] = pd.to_numeric(df["TAGE"], errors="coerce")
    df["fpl"] = pd.to_numeric(df["TFINCPOV"], errors="coerce")
    df.loc[~df["fpl"].between(0, 20), "fpl"] = np.nan
    df["weight"] = clean_weight(df)
    df["healthy"] = pd.to_numeric(df["EHLTSTAT"], errors="coerce").between(1, 2).astype(float)
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
    df["adult"] = df["age"].ge(18)
    df["child"] = df["age"].lt(18)
    df["spouse_linked"] = df["EPNSPOUSE"].notna().astype(int)

    family_keys = ["SSUID", "SHHADID", "RFAMNUM", "reference_date"]
    fam = (
        df.groupby(family_keys, observed=True)
        .agg(
            family_persons=("PNUM", "nunique"),
            family_children=("child", "sum"),
            family_adults=("adult", "sum"),
            family_spouse_links=("spouse_linked", "sum"),
        )
        .reset_index()
    )
    df = df.merge(fam, on=family_keys, how="left")
    df["family_exposed"] = (
        df["family_persons"].ge(2) & (df["family_children"].gt(0) | df["family_spouse_links"].gt(0))
    ).astype(float)

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
            family_exposed=("family_exposed", "mean"),
            family_children=("family_children", "mean"),
            family_persons=("family_persons", "mean"),
        )
        .reset_index()
    )
    py["healthy"] = py["healthy"].ge(0.5).astype(int)
    py["family_exposed"] = py["family_exposed"].ge(0.5).astype(int)
    py["stldi_protective"] = py["state_fips"].isin(STLDI_PROTECTIVE).astype(int)
    py["stldi_permissive"] = 1 - py["stldi_protective"]
    py["state_name"] = py["state_fips"].map(STATE_NAMES)
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
        rows.append(
            {
                "model": model,
                "outcome": outcome,
                "term": term,
                "coef": b.get(term, np.nan),
                "se": serr.get(term, np.nan),
                "t": b.get(term, np.nan) / serr.get(term, np.nan) if serr.get(term, np.nan) else np.nan,
                "n_person_years": n,
                "n_persons": int(s["person_id"].nunique()),
                "n_states": int(s["state_fips"].nunique()),
                "weighted_mean": wmean(s[outcome], s["weight"]),
            }
        )
    return pd.DataFrame(rows)


def estimate_event(
    d: pd.DataFrame,
    exposure_col: str,
    years: list[int],
    omitted: int,
    outcomes: list[str],
    model: str,
    controls: list[str],
    fe_cols: list[str],
) -> pd.DataFrame:
    d = d.copy()
    terms = []
    for year in years:
        if year == omitted:
            continue
        term = f"{exposure_col}_x_{year}"
        d[term] = d[exposure_col].astype(float) * d["reference_year"].eq(year).astype(float)
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
        for year in years:
            if year == omitted:
                continue
            term = f"{exposure_col}_x_{year}"
            rows.append(
                {
                    "model": model,
                    "outcome": outcome,
                    "year": year,
                    "relative_to_omitted": year - omitted,
                    "term": term,
                    "coef": b.get(term, np.nan),
                    "se": serr.get(term, np.nan),
                    "t": b.get(term, np.nan) / serr.get(term, np.nan) if serr.get(term, np.nan) else np.nan,
                    "n_person_years": n,
                    "n_persons": int(s["person_id"].nunique()),
                    "n_states": int(s["state_fips"].nunique()),
                }
            )
    return pd.DataFrame(rows)


def build_samples(py: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    fg = py[
        py["reference_year"].between(2019, 2023)
        & py["age"].between(26, 64, inclusive="both")
        & py["fpl"].between(1.38, 6.0, inclusive="both")
        & py["months"].ge(6)
    ].copy()
    fg["post_2023"] = fg["reference_year"].ge(2023).astype(int)
    fg["family_glitch_treat"] = fg["family_exposed"] * fg["post_2023"]
    fg["state_year"] = fg["state_fips"] + "_" + fg["reference_year"].astype(str)
    fg["state_family"] = fg["state_fips"] + "_" + fg["family_exposed"].astype(str)
    fg["family_year"] = fg["family_exposed"].astype(str) + "_" + fg["reference_year"].astype(str)

    stldi = py[
        py["reference_year"].between(2017, 2021)
        & py["age"].between(26, 64, inclusive="both")
        & py["fpl"].between(2.0, 8.0, inclusive="both")
        & py["months"].ge(6)
    ].copy()
    stldi["target_healthy_young"] = (
        stldi["age"].between(26, 44, inclusive="both") & stldi["healthy"].eq(1) & stldi["fpl"].between(3.0, 8.0)
    ).astype(int)
    stldi["post_2019"] = stldi["reference_year"].ge(2019).astype(int)
    stldi["stldi_treat"] = stldi["stldi_permissive"] * stldi["target_healthy_young"] * stldi["post_2019"]
    stldi["state_year"] = stldi["state_fips"] + "_" + stldi["reference_year"].astype(str)
    stldi["state_target"] = stldi["state_fips"] + "_" + stldi["target_healthy_young"].astype(str)
    stldi["target_year"] = stldi["target_healthy_young"].astype(str) + "_" + stldi["reference_year"].astype(str)
    return fg, stldi


def support(fg: pd.DataFrame, stldi: pd.DataFrame) -> pd.DataFrame:
    rows = []
    fg_target = fg[fg["family_exposed"].eq(1)]
    stldi_target = stldi[stldi["stldi_permissive"].eq(1) & stldi["target_healthy_young"].eq(1)]
    rows.append(
        {
            "sample": "family_glitch_26_64_138_600",
            "person_years": int(len(fg)),
            "persons": int(fg["person_id"].nunique()),
            "states": int(fg["state_fips"].nunique()),
            "target_person_years": int(len(fg_target)),
            "target_persons": int(fg_target["person_id"].nunique()),
            "active_treated_person_years": int(fg["family_glitch_treat"].sum()),
            "active_treated_persons": int(fg.loc[fg["family_glitch_treat"].eq(1), "person_id"].nunique()),
            "mean_direct_market": wmean(fg["direct_market"], fg["weight"]),
            "mean_exchange_subsidy": wmean(fg["exchange_subsidy"], fg["weight"]),
            "mean_uninsured": wmean(fg["uninsured"], fg["weight"]),
        }
    )
    rows.append(
        {
            "sample": "stldi_permissive_healthy_young_2017_2021",
            "person_years": int(len(stldi)),
            "persons": int(stldi["person_id"].nunique()),
            "states": int(stldi["state_fips"].nunique()),
            "target_person_years": int(len(stldi_target)),
            "target_persons": int(stldi_target["person_id"].nunique()),
            "active_treated_person_years": int(stldi["stldi_treat"].sum()),
            "active_treated_persons": int(stldi.loc[stldi["stldi_treat"].eq(1), "person_id"].nunique()),
            "mean_direct_market": wmean(stldi["direct_market"], stldi["weight"]),
            "mean_exchange_subsidy": wmean(stldi["exchange_subsidy"], stldi["weight"]),
            "mean_uninsured": wmean(stldi["uninsured"], stldi["weight"]),
        }
    )
    return pd.DataFrame(rows)


def estimate_family_transition(fg: pd.DataFrame, outcomes: list[str]) -> pd.DataFrame:
    base = fg[fg["reference_year"].isin([2022, 2023])].copy()
    wide_parts = []
    keep_cols = ["person_id", "state_fips", "reference_year", "weight", "age", "fpl", "healthy", "family_exposed", "family_persons", "family_children"]
    for outcome in outcomes:
        keep_cols.append(outcome)
    base = base[keep_cols].copy()
    wide = base.pivot_table(index="person_id", columns="reference_year", values=outcomes, aggfunc="first")
    wide.columns = [f"{a}_{int(b)}" for a, b in wide.columns]
    meta_2022 = base[base["reference_year"].eq(2022)].drop_duplicates("person_id").set_index("person_id")
    meta_2023 = base[base["reference_year"].eq(2023)].drop_duplicates("person_id").set_index("person_id")
    both = meta_2022.index.intersection(meta_2023.index)
    wide = wide.loc[wide.index.intersection(both)].copy()
    meta = meta_2022.loc[wide.index].copy()
    meta["weight"] = meta["weight"].where(meta["weight"].gt(0), 1.0)
    meta["baseline_employer_like_private"] = (
        (wide.get("private_2022", pd.Series(index=wide.index, dtype=float)) >= 0.5)
        & (wide.get("direct_market_2022", pd.Series(index=wide.index, dtype=float)) < 0.1)
        & (wide.get("exchange_subsidy_2022", pd.Series(index=wide.index, dtype=float)) < 0.1)
    ).astype(int)
    rows = []
    samples = {
        "all_observed_2022_2023": pd.Series(True, index=wide.index),
        "baseline_employer_like_private": meta["baseline_employer_like_private"].eq(1),
    }
    for sample_name, mask in samples.items():
        ids = wide.index[mask]
        if len(ids) == 0:
            continue
        for outcome in outcomes:
            c22 = f"{outcome}_2022"
            c23 = f"{outcome}_2023"
            if c22 not in wide.columns or c23 not in wide.columns:
                continue
            y = (wide.loc[ids, c23] - wide.loc[ids, c22]).astype(float)
            m = meta.loc[ids]
            x = pd.concat(
                [
                    pd.Series(1.0, index=ids, name="const"),
                    m["family_exposed"].astype(float).rename("family_exposed_2022"),
                    m["age"].astype(float),
                    m["fpl"].astype(float).clip(0, 8).rename("fpl_clip"),
                    m["healthy"].astype(float),
                    m["family_persons"].astype(float),
                    m["family_children"].astype(float),
                    pd.get_dummies(m["state_fips"], prefix="state", drop_first=True, dtype=float),
                ],
                axis=1,
            )
            beta, se, n = wls_hc1(y.to_numpy(dtype=float), x.to_numpy(dtype=float), m["weight"].to_numpy(dtype=float))
            b = pd.Series(beta, index=x.columns)
            serr = pd.Series(se, index=x.columns)
            rows.append(
                {
                    "model": "family_glitch_2022_2023_first_difference",
                    "sample": sample_name,
                    "outcome": outcome,
                    "term": "family_exposed_2022",
                    "coef": b.get("family_exposed_2022", np.nan),
                    "se": serr.get("family_exposed_2022", np.nan),
                    "t": b.get("family_exposed_2022", np.nan) / serr.get("family_exposed_2022", np.nan)
                    if serr.get("family_exposed_2022", np.nan)
                    else np.nan,
                    "n_persons": int(len(ids)),
                    "n_states": int(m["state_fips"].nunique()),
                    "treated_persons": int(m["family_exposed"].sum()),
                    "weighted_delta_mean": wmean(y, m["weight"]),
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
        lines.append(f"- `{outcome}`: {r['coef']:+.4f}, se {r['se']:.4f}, t {r['t']:.2f}.")
    return "\n".join(lines)


def fmt_transition(df: pd.DataFrame, sample: str, outcomes: list[str]) -> str:
    d = df[df["sample"].eq(sample)].set_index("outcome")
    lines = []
    for outcome in outcomes:
        if outcome not in d.index:
            continue
        r = d.loc[outcome]
        lines.append(f"- `{outcome}`: {r['coef']:+.4f}, se {r['se']:.4f}, t {r['t']:.2f}; n={int(r['n_persons']):,}.")
    return "\n".join(lines)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    py = build_person_year()
    fg, stldi = build_samples(py)
    outcomes = ["direct_market", "exchange_subsidy", "uninsured", "any_coverage", "private", "oop_any", "doctor_any"]
    stldi_outcomes = ["direct_market", "exchange_subsidy", "uninsured", "any_coverage", "private", "oop_any"]

    estimates = pd.concat(
        [
            estimate(
                fg,
                "family_glitch_treat",
                outcomes,
                "family_glitch_2023",
                controls=["age", "fpl", "healthy", "family_persons", "family_children"],
                fe_cols=["state_year", "state_family"],
            ),
            estimate(
                stldi,
                "stldi_treat",
                stldi_outcomes,
                "stldi_2018_expansion_permissive",
                controls=["age", "fpl", "healthy"],
                fe_cols=["state_year", "state_target", "target_year"],
            ),
        ],
        ignore_index=True,
    )
    events = pd.concat(
        [
            estimate_event(
                fg,
                "family_exposed",
                [2019, 2020, 2021, 2022, 2023],
                2022,
                ["direct_market", "exchange_subsidy", "uninsured"],
                "family_glitch_event",
                controls=["age", "fpl", "healthy", "family_persons", "family_children"],
                fe_cols=["state_year", "state_family"],
            ),
        ],
        ignore_index=True,
    )
    # Event helper needs a single exposure column; create it explicitly for STLDI and append.
    stldi_event = stldi.copy()
    stldi_event["stldi_permissive_target"] = stldi_event["stldi_permissive"] * stldi_event["target_healthy_young"]
    events = pd.concat(
        [
            events,
            estimate_event(
                stldi_event,
                "stldi_permissive_target",
                [2017, 2018, 2019, 2020, 2021],
                2018,
                ["direct_market", "exchange_subsidy", "uninsured"],
                "stldi_event",
                controls=["age", "fpl", "healthy"],
                fe_cols=["state_year", "state_target", "target_year"],
            ),
        ],
        ignore_index=True,
    )
    sup = support(fg, stldi)
    transition = estimate_family_transition(fg, outcomes)

    py.to_parquet(OUT / "family_glitch_stldi_person_year_panel.parquet", index=False)
    estimates.to_csv(OUT / "family_glitch_stldi_estimates.csv", index=False)
    events.to_csv(OUT / "family_glitch_stldi_event.csv", index=False)
    sup.to_csv(OUT / "family_glitch_stldi_support.csv", index=False)
    transition.to_csv(OUT / "family_glitch_transition_estimates.csv", index=False)

    fg_s = sup[sup["sample"].eq("family_glitch_26_64_138_600")].iloc[0]
    stldi_s = sup[sup["sample"].eq("stldi_permissive_healthy_young_2017_2021")].iloc[0]
    fg_direct = estimates[(estimates["model"].eq("family_glitch_2023")) & (estimates["outcome"].eq("direct_market"))].iloc[0]
    fg_exsub = estimates[(estimates["model"].eq("family_glitch_2023")) & (estimates["outcome"].eq("exchange_subsidy"))].iloc[0]
    stldi_exsub = estimates[
        (estimates["model"].eq("stldi_2018_expansion_permissive")) & (estimates["outcome"].eq("exchange_subsidy"))
    ].iloc[0]
    stldi_unins = estimates[
        (estimates["model"].eq("stldi_2018_expansion_permissive")) & (estimates["outcome"].eq("uninsured"))
    ].iloc[0]
    verdict = "NO-CLEAN-GO"
    if fg_direct["coef"] > 0.01 and fg_exsub["coef"] > 0.01 and fg_direct["t"] > 1.5:
        verdict = "FAMILY-GLITCH-DIRECTIONAL-SIGNAL"
    if stldi_exsub["coef"] < -0.01 and stldi_unins["coef"] <= 0 and abs(stldi_exsub["t"]) > 1.5:
        verdict = "STLDI-DIRECTIONAL-SIGNAL"

    report = f"""# Family Glitch and STLDI Fast Test

## Question

Can current SIPP support a new adult, non-child, non-unwinding health-insurance paper using either:

1. the 2023 ACA family-glitch fix; or
2. state regulatory heterogeneity around the 2018 federal short-term limited-duration insurance
   expansion?

## Source Checks

{chr(10).join(f"- {s}" for s in SOURCES)}

## Data Construction

- Source parquet: `data/analysis_ready/sipp_2018_2024_person_month_panel.parquet`.
- Unit: person-year collapsed from monthly rows.
- Family exposure is proxied from SIPP household/family structure, not from employer premium
  contributions.
- STLDI protective states are coded from Commonwealth/KFF summaries as states with bans or
  very restrictive/no-availability regimes.

## Family Glitch Fix

Design:

- Sample: adults age 26-64, 138-600% FPL, 2019-2023.
- Exposure: family-exposed adult in a multi-person family with spouse link or children.
- Treatment: `family_exposed x 2023`.
- Fixed effects: state-year and state-family.
- Family-year FE are intentionally not included because the treatment is a national 2023 family
  exposure shock and would be collinear with family-year indicators.

Support:

- Person-years: {int(fg_s['person_years']):,}.
- Persons: {int(fg_s['persons']):,}.
- Family-exposed person-years: {int(fg_s['target_person_years']):,}.
- Active treated person-years in 2023: {int(fg_s['active_treated_person_years']):,}.

Estimates:

{fmt(estimates, 'family_glitch_2023', outcomes)}

Same-person 2022 to 2023 first-difference check:

All observed persons:

{fmt_transition(transition, 'all_observed_2022_2023', ['direct_market', 'exchange_subsidy', 'uninsured', 'any_coverage', 'private'])}

Baseline employer-like private sample:

{fmt_transition(transition, 'baseline_employer_like_private', ['direct_market', 'exchange_subsidy', 'uninsured', 'any_coverage', 'private'])}

Key limitation:

- The compact SIPP parquet does not observe employer offer, family premium contribution, employee-only
  premium contribution, or whether family employer coverage is unaffordable. The treatment is a
  family-exposure proxy, not actual family-glitch eligibility.

## Short-Term Limited-Duration Insurance

Design:

- Sample: adults age 26-64, 200-800% FPL, 2017-2021.
- Target group: healthy adults age 26-44 with 300-800% FPL.
- Treatment: permissive STLDI state x target group x post-2019.
- Fixed effects: state-year, state-target, target-year.

Support:

- Person-years: {int(stldi_s['person_years']):,}.
- Persons: {int(stldi_s['persons']):,}.
- Permissive-state target person-years: {int(stldi_s['target_person_years']):,}.
- Active treated person-years: {int(stldi_s['active_treated_person_years']):,}.

Estimates:

{fmt(estimates, 'stldi_2018_expansion_permissive', stldi_outcomes)}

Key limitation:

- SIPP does not separately identify STLDI enrollment. Survey respondents may report STLDI as private
  direct-purchase coverage, as other private coverage, or not distinguish it from ACA-compliant nongroup
  coverage. Thus this is an indirect market-segmentation test.

## Verdict

`{verdict}`

A clean GO would require:

- Family glitch: a clear 2023 jump in direct-market or exchange/subsidized coverage among
  family-exposed adults, without offsetting uninsured increases and without earlier event movement.
- STLDI: a clear post-2019 shift away from exchange/subsidized ACA coverage, or into direct/off-
  marketplace private coverage, among healthy young higher-income adults in permissive states.

## Artifacts

- `script/11_idea_scan/13_family_glitch_stldi_fast_test.py`
- `result/idea_scan/family_glitch_stldi_person_year_panel.parquet`
- `result/idea_scan/family_glitch_stldi_support.csv`
- `result/idea_scan/family_glitch_stldi_estimates.csv`
- `result/idea_scan/family_glitch_stldi_event.csv`
- `result/idea_scan/family_glitch_transition_estimates.csv`
"""
    REPORT.write_text(report, encoding="utf-8")


if __name__ == "__main__":
    main()
