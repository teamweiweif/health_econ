from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
PANEL = ROOT / "data" / "analysis_ready" / "sipp_2018_2024_person_month_panel.parquet"
OUT = ROOT / "result" / "idea_scan"
REPORT = ROOT / "report" / "26_state_marketplace_subsidy_fast_test.md"


SOURCES = [
    "Maryland Health Benefit Exchange young adult subsidy report: https://www.marylandhbe.com/wp-content/uploads/2024/12/Report-on-the-Young-Adult-Subsidy-Program.pdf",
    "SHVS State Marketplace Subsidies report: https://shvs.org/wp-content/uploads/2026/03/SHVS_State-Marketplace-Subsidies-to-Support-Health-Insurance-Affordability_Final.pdf",
    "GetCoveredNJ Health Plan Savings: https://www.nj.gov/getcoverednj/financialhelp/premiums/",
    "Maryland Health Connection 2026 enrollment bulletin: https://content.govdelivery.com/accounts/MDHC/bulletins/405d2db",
]


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
    df = df[df["reference_year"].between(2019, 2023)].copy()
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
        parts: list[pd.Series | pd.DataFrame] = [
            pd.Series(1.0, index=s.index, name="const"),
            s[term].astype(float),
        ]
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
    prefix: str,
    year_terms: list[int],
    omitted_year: int,
    outcomes: list[str],
    model: str,
    controls: list[str],
    fe_cols: list[str],
) -> pd.DataFrame:
    d = d.copy()
    terms = []
    for year in year_terms:
        if year == omitted_year:
            continue
        term = f"{prefix}_{year}"
        d[term] = d[prefix].astype(float) * d["reference_year"].eq(year).astype(float)
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
        for year in year_terms:
            if year == omitted_year:
                continue
            term = f"{prefix}_{year}"
            rows.append(
                {
                    "model": model,
                    "outcome": outcome,
                    "year": year,
                    "relative_to_omitted": year - omitted_year,
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


def build_samples(py: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    md = py[
        py["age"].between(18, 44, inclusive="both")
        & py["fpl"].between(1.38, 4.0, inclusive="both")
        & py["months"].ge(6)
    ].copy()
    md["maryland"] = md["state_fips"].eq("24").astype(int)
    md["young_18_34"] = md["age"].between(18, 34, inclusive="both").astype(int)
    md["post_2022"] = md["reference_year"].ge(2022).astype(int)
    md["md_young"] = md["maryland"] * md["young_18_34"]
    md["yas_treat"] = md["md_young"] * md["post_2022"]
    md["state_year"] = md["state_fips"] + "_" + md["reference_year"].astype(str)
    md["state_young"] = md["state_fips"] + "_" + md["young_18_34"].astype(str)
    md["young_year"] = md["young_18_34"].astype(str) + "_" + md["reference_year"].astype(str)

    md_clean = py[
        py["age"].between(26, 44, inclusive="both")
        & py["fpl"].between(1.38, 4.0, inclusive="both")
        & py["months"].ge(6)
    ].copy()
    md_clean["maryland"] = md_clean["state_fips"].eq("24").astype(int)
    md_clean["young_26_34"] = md_clean["age"].between(26, 34, inclusive="both").astype(int)
    md_clean["post_2022"] = md_clean["reference_year"].ge(2022).astype(int)
    md_clean["md_young"] = md_clean["maryland"] * md_clean["young_26_34"]
    md_clean["yas_treat"] = md_clean["md_young"] * md_clean["post_2022"]
    md_clean["state_year"] = md_clean["state_fips"] + "_" + md_clean["reference_year"].astype(str)
    md_clean["state_young"] = md_clean["state_fips"] + "_" + md_clean["young_26_34"].astype(str)
    md_clean["young_year"] = md_clean["young_26_34"].astype(str) + "_" + md_clean["reference_year"].astype(str)

    nj = py[
        py["age"].between(26, 64, inclusive="both")
        & py["fpl"].between(1.38, 10.0, inclusive="both")
        & py["months"].ge(6)
    ].copy()
    nj["new_jersey"] = nj["state_fips"].eq("34").astype(int)
    nj["eligible_138_600"] = nj["fpl"].between(1.38, 6.0, inclusive="both").astype(int)
    nj["post_2021"] = nj["reference_year"].ge(2021).astype(int)
    nj["nj_eligible"] = nj["new_jersey"] * nj["eligible_138_600"]
    nj["njhps_treat"] = nj["nj_eligible"] * nj["post_2021"]
    nj["state_year"] = nj["state_fips"] + "_" + nj["reference_year"].astype(str)
    nj["state_eligible"] = nj["state_fips"] + "_" + nj["eligible_138_600"].astype(str)
    nj["eligible_year"] = nj["eligible_138_600"].astype(str) + "_" + nj["reference_year"].astype(str)
    return md, md_clean, nj


def support(md: pd.DataFrame, md_clean: pd.DataFrame, nj: pd.DataFrame) -> pd.DataFrame:
    rows = []
    specs = [
        ("maryland_yas_18_44_138_400", md, "maryland", "young_18_34", "yas_treat"),
        ("maryland_yas_clean_26_44_138_400", md_clean, "maryland", "young_26_34", "yas_treat"),
        ("new_jersey_njhps_26_64_138_1000", nj, "new_jersey", "eligible_138_600", "njhps_treat"),
    ]
    for name, d, state_col, target_col, treat_col in specs:
        treated_target = d[d[state_col].eq(1) & d[target_col].eq(1)]
        rows.append(
            {
                "sample": name,
                "person_years": int(len(d)),
                "persons": int(d["person_id"].nunique()),
                "states": int(d["state_fips"].nunique()),
                "policy_state_target_person_years": int(len(treated_target)),
                "policy_state_target_persons": int(treated_target["person_id"].nunique()),
                "active_treated_person_years": int(d[treat_col].sum()),
                "active_treated_persons": int(d.loc[d[treat_col].eq(1), "person_id"].nunique()),
                "mean_direct_market": wmean(d["direct_market"], d["weight"]),
                "mean_exchange_subsidy": wmean(d["exchange_subsidy"], d["weight"]),
                "mean_uninsured": wmean(d["uninsured"], d["weight"]),
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


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    py = build_person_year()
    md, md_clean, nj = build_samples(py)
    outcomes = ["direct_market", "exchange_subsidy", "uninsured", "any_coverage", "private", "oop_any", "doctor_any"]

    estimates = pd.concat(
        [
            estimate(
                md,
                "yas_treat",
                outcomes,
                "maryland_yas_18_34_vs_35_44",
                controls=["age", "fpl", "healthy"],
                fe_cols=["state_year", "state_young", "young_year"],
            ),
            estimate(
                md_clean,
                "yas_treat",
                outcomes,
                "maryland_yas_clean_26_34_vs_35_44",
                controls=["age", "fpl", "healthy"],
                fe_cols=["state_year", "state_young", "young_year"],
            ),
            estimate(
                nj,
                "njhps_treat",
                outcomes,
                "new_jersey_njhps_138_600_vs_600_1000",
                controls=["age", "fpl", "healthy"],
                fe_cols=["state_year", "state_eligible", "eligible_year"],
            ),
        ],
        ignore_index=True,
    )
    events = pd.concat(
        [
            estimate_event(
                md,
                "md_young",
                [2019, 2020, 2021, 2022, 2023],
                2021,
                ["direct_market", "exchange_subsidy", "uninsured"],
                "maryland_yas_18_34_event",
                controls=["age", "fpl", "healthy"],
                fe_cols=["state_year", "state_young", "young_year"],
            ),
            estimate_event(
                md_clean,
                "md_young",
                [2019, 2020, 2021, 2022, 2023],
                2021,
                ["direct_market", "exchange_subsidy", "uninsured"],
                "maryland_yas_clean_26_34_event",
                controls=["age", "fpl", "healthy"],
                fe_cols=["state_year", "state_young", "young_year"],
            ),
            estimate_event(
                nj,
                "nj_eligible",
                [2019, 2020, 2021, 2022, 2023],
                2020,
                ["direct_market", "exchange_subsidy", "uninsured"],
                "new_jersey_njhps_event",
                controls=["age", "fpl", "healthy"],
                fe_cols=["state_year", "state_eligible", "eligible_year"],
            ),
        ],
        ignore_index=True,
    )
    sup = support(md, md_clean, nj)

    py.to_parquet(OUT / "state_marketplace_subsidy_person_year_panel.parquet", index=False)
    estimates.to_csv(OUT / "state_marketplace_subsidy_estimates.csv", index=False)
    events.to_csv(OUT / "state_marketplace_subsidy_event.csv", index=False)
    sup.to_csv(OUT / "state_marketplace_subsidy_support.csv", index=False)

    md_s = sup[sup["sample"].eq("maryland_yas_18_44_138_400")].iloc[0]
    md_clean_s = sup[sup["sample"].eq("maryland_yas_clean_26_44_138_400")].iloc[0]
    nj_s = sup[sup["sample"].eq("new_jersey_njhps_26_64_138_1000")].iloc[0]
    md_direct = estimates[
        (estimates["model"].eq("maryland_yas_18_34_vs_35_44")) & (estimates["outcome"].eq("direct_market"))
    ].iloc[0]
    md_clean_direct = estimates[
        (estimates["model"].eq("maryland_yas_clean_26_34_vs_35_44")) & (estimates["outcome"].eq("direct_market"))
    ].iloc[0]
    nj_direct = estimates[
        (estimates["model"].eq("new_jersey_njhps_138_600_vs_600_1000"))
        & (estimates["outcome"].eq("direct_market"))
    ].iloc[0]
    verdict = "NO-CLEAN-GO"
    if md_direct["coef"] > 0.03 and md_clean_direct["coef"] > 0.02 and min(md_direct["t"], md_clean_direct["t"]) > 1.5:
        verdict = "POTENTIAL-GO-IF-SUPPORT-ACCEPTABLE"
    elif md_direct["coef"] > 0 and nj_direct["coef"] > 0:
        verdict = "DIRECTIONAL-SIGNAL-BUT-NOT-CLEAN"

    report = f"""# State Marketplace Subsidy Fast Test

## Question

Can current SIPP support a new adult, non-child, non-unwinding paper on state-funded Marketplace
subsidies?

This tests two policy shocks:

1. Maryland's 2022 young-adult Marketplace subsidy.
2. New Jersey Health Plan Savings, effective for 2021 coverage.

## Source Checks

{chr(10).join(f"- {s}" for s in SOURCES)}

Key policy facts from the source checks:

- Maryland has offered a young-adult subsidy since 2022; current summaries describe eligibility for
  young adults with income up to 400% FPL.
- SHVS describes young adults as disproportionately uninsured and potentially important for the
  Marketplace risk pool.
- New Jersey Health Plan Savings started lowering premiums for coverage beginning January 1,
  2021 and applies up to 600% FPL.

## Data Construction

- Source parquet: `data/analysis_ready/sipp_2018_2024_person_month_panel.parquet`.
- Unit: person-year collapsed from monthly SIPP observations.
- Outcomes: annual share of months in direct-purchase/Marketplace coverage,
  exchange/subsidized private coverage, uninsured, any coverage, private coverage, OOP any, doctor
  visit any.
- Models: weighted LPM screens with saturated DDD fixed effects.

## Maryland Young Adult Subsidy

Broad sample:

- Ages 18-44.
- Family income 138-400% FPL.
- Treated group: Maryland ages 18-34 in 2022+.
- Comparison: ages 35-44 and the same age groups in other states.
- Fixed effects: state-year, state-young, and young-year.

Support:

- Person-years: {int(md_s['person_years']):,}.
- Persons: {int(md_s['persons']):,}.
- Maryland target person-years: {int(md_s['policy_state_target_person_years']):,}.
- Active treated Maryland target person-years: {int(md_s['active_treated_person_years']):,}.

Estimates:

{fmt(estimates, 'maryland_yas_18_34_vs_35_44', outcomes)}

Cleaner adult sample:

- Ages 26-44, to avoid dependent-coverage confounding for ages under 26.
- Treated group: Maryland ages 26-34 in 2022+.

Support:

- Person-years: {int(md_clean_s['person_years']):,}.
- Persons: {int(md_clean_s['persons']):,}.
- Maryland target person-years: {int(md_clean_s['policy_state_target_person_years']):,}.
- Active treated Maryland target person-years: {int(md_clean_s['active_treated_person_years']):,}.

Estimates:

{fmt(estimates, 'maryland_yas_clean_26_34_vs_35_44', outcomes)}

## New Jersey Health Plan Savings

Sample:

- Ages 26-64.
- Family income 138-1000% FPL.
- Treated group: New Jersey residents at 138-600% FPL in 2021+.
- Comparison: 600-1000% FPL and the same income bands in other states.
- Fixed effects: state-year, state-eligible-income, eligible-income-year.

Support:

- Person-years: {int(nj_s['person_years']):,}.
- Persons: {int(nj_s['persons']):,}.
- New Jersey eligible person-years: {int(nj_s['policy_state_target_person_years']):,}.
- Active treated New Jersey eligible person-years: {int(nj_s['active_treated_person_years']):,}.

Estimates:

{fmt(estimates, 'new_jersey_njhps_138_600_vs_600_1000', outcomes)}

## Verdict

`{verdict}`

Interpretation:

- Maryland is the cleaner design because eligibility varies sharply by age and income, but SIPP has
  very little Maryland support in the eligible age-income cell.
- New Jersey has more support, but the 2021 policy is bundled with New Jersey's Marketplace
  transition and the ARPA federal subsidy expansion. The income-band DDD helps but does not make
  it a top-field design by itself.
- A clean GO would require large, consistent increases in direct-market or exchange/subsidized
  coverage with no offsetting increase in uninsured and no pre-trend in the event checks.

## Artifacts

- `script/11_idea_scan/12_state_marketplace_subsidy_fast_test.py`
- `result/idea_scan/state_marketplace_subsidy_person_year_panel.parquet`
- `result/idea_scan/state_marketplace_subsidy_support.csv`
- `result/idea_scan/state_marketplace_subsidy_estimates.csv`
- `result/idea_scan/state_marketplace_subsidy_event.csv`
"""
    REPORT.write_text(report, encoding="utf-8")


if __name__ == "__main__":
    main()
