from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
PANEL = ROOT / "data" / "analysis_ready" / "sipp_2018_2024_person_month_panel.parquet"
OUT = ROOT / "result" / "idea_scan"
REPORT = ROOT / "report" / "60_late_medicaid_expansion_threshold_test.md"


LATE_EXPANSION_DATES = {
    "23": "2019-01",  # Maine
    "51": "2019-01",  # Virginia
    "16": "2020-01",  # Idaho
    "49": "2020-01",  # Utah
    "31": "2020-10",  # Nebraska
    "40": "2021-07",  # Oklahoma
    "29": "2021-10",  # Missouri
    "46": "2023-07",  # South Dakota
    "37": "2023-12",  # North Carolina
}

STATE_NAMES = {
    "01": "Alabama",
    "05": "Arkansas",
    "12": "Florida",
    "13": "Georgia",
    "16": "Idaho",
    "20": "Kansas",
    "23": "Maine",
    "28": "Mississippi",
    "29": "Missouri",
    "31": "Nebraska",
    "37": "North Carolina",
    "40": "Oklahoma",
    "45": "South Carolina",
    "46": "South Dakota",
    "47": "Tennessee",
    "48": "Texas",
    "49": "Utah",
    "51": "Virginia",
    "55": "Wisconsin",
    "56": "Wyoming",
}

NEVER_EXPANSION = {
    "01",  # Alabama
    "12",  # Florida
    "13",  # Georgia: partial Pathways in 2023, no full ACA expansion
    "20",  # Kansas
    "28",  # Mississippi
    "45",  # South Carolina
    "47",  # Tennessee
    "48",  # Texas
    "55",  # Wisconsin: covers adults to 100% FPL, not ACA expansion
    "56",  # Wyoming
}


def yes(s: pd.Series) -> pd.Series:
    return pd.to_numeric(s, errors="coerce").eq(1)


def clean_weight(df: pd.DataFrame) -> pd.Series:
    w = pd.to_numeric(df.get("WPFINWGT"), errors="coerce")
    return w.where(w.gt(0))


def bounded_numeric(s: pd.Series, lo: float, hi: float) -> pd.Series:
    out = pd.to_numeric(s, errors="coerce")
    return out.where(out.between(lo, hi, inclusive="both"))


def wmean(y: pd.Series, w: pd.Series) -> float:
    mask = y.notna() & w.notna() & (w > 0)
    if not mask.any():
        return np.nan
    return float(np.average(y[mask].astype(float), weights=w[mask].astype(float)))


def weighted_ols_cluster(
    y: np.ndarray,
    x: np.ndarray,
    w: np.ndarray,
    cluster: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, int, int]:
    mask = np.isfinite(y) & np.isfinite(w) & (w > 0) & np.all(np.isfinite(x), axis=1)
    y = y[mask]
    x = x[mask]
    w = w[mask]
    cluster = cluster[mask]
    if len(y) <= x.shape[1] + 10:
        k = x.shape[1]
        return np.full(k, np.nan), np.full(k, np.nan), np.full(k, np.nan), int(len(y)), int(pd.Series(cluster).nunique())

    sw = np.sqrt(w / np.nanmean(w))
    xw = x * sw[:, None]
    yw = y * sw
    inv = np.linalg.pinv(xw.T @ xw)
    beta = inv @ (xw.T @ yw)
    resid = yw - xw @ beta
    n, k = xw.shape

    meat_hc1 = xw.T @ ((resid**2)[:, None] * xw)
    cov_hc1 = (n / max(n - k, 1)) * inv @ meat_hc1 @ inv
    se_hc1 = np.sqrt(np.where(np.diag(cov_hc1) >= 0, np.diag(cov_hc1), np.nan))

    codes, uniques = pd.factorize(cluster, sort=False)
    score = xw * resid[:, None]
    score_sums = np.zeros((len(uniques), k))
    np.add.at(score_sums, codes, score)
    meat = score_sums.T @ score_sums
    g = len(uniques)
    if g > 1:
        meat *= (g / (g - 1)) * ((n - 1) / max(n - k, 1))
    cov_cluster = inv @ meat @ inv
    se_cluster = np.sqrt(np.where(np.diag(cov_cluster) >= 0, np.diag(cov_cluster), np.nan))
    return beta, se_hc1, se_cluster, int(n), int(g)


def prep() -> pd.DataFrame:
    cols = [
        "person_id",
        "SSUID",
        "PNUM",
        "MONTHCODE",
        "file_year",
        "reference_year",
        "reference_month",
        "state_fips",
        "TAGE",
        "ESEX",
        "ERACE",
        "EHISPAN",
        "EORIGIN",
        "RDIS",
        "RSSI_YRYN",
        "WPFINWGT",
        "TSSSAMT",
        "RHLTHMTH",
        "RPRIMTH",
        "RPUBMTH",
        "RPUBTYPE1",
        "RPUBTYPE2",
        "EMDMTH",
        "RPRITYPE2",
        "RMARKTPLACE",
        "EPRIEXCH1",
        "EPRIEXCH2",
        "EPRISUBS1",
        "EPRISUBS2",
        "EMDEXCH",
        "EMDSUBS",
        "RSNAP_MNYN",
        "TFINCPOV",
        "TFCYINCPOV",
    ]
    df = pd.read_parquet(PANEL, columns=cols)
    df["state_fips"] = df["state_fips"].astype(str).str.zfill(2)
    df["state_name"] = df["state_fips"].map(STATE_NAMES)
    df["month_id"] = pd.to_numeric(df["reference_year"], errors="coerce").astype(int) * 100 + pd.to_numeric(
        df["reference_month"], errors="coerce"
    ).astype(int)
    df["year_month"] = df["month_id"].astype(str)
    df["age"] = bounded_numeric(df["TAGE"], 0, 100)
    df["female"] = pd.to_numeric(df["ESEX"], errors="coerce").eq(2).astype(float)
    df["black"] = pd.to_numeric(df["ERACE"], errors="coerce").eq(2).astype(float)
    hisp = pd.to_numeric(df.get("EHISPAN"), errors="coerce").eq(1) | pd.to_numeric(df.get("EORIGIN"), errors="coerce").eq(1)
    df["hispanic"] = hisp.astype(float)
    df["disabled"] = yes(df["RDIS"]).astype(float)
    df["ssi_year"] = yes(df["RSSI_YRYN"]).astype(float)
    df["medicare"] = yes(df["RPUBTYPE1"]).astype(float)
    df["fpl_monthly"] = bounded_numeric(df["TFINCPOV"], 0, 10)
    df["fpl_annual"] = bounded_numeric(df["TFCYINCPOV"], 0, 10)
    df["weight"] = clean_weight(df)

    df["any_coverage"] = yes(df["RHLTHMTH"]).astype(float)
    df["uninsured"] = pd.to_numeric(df["RHLTHMTH"], errors="coerce").eq(2).astype(float)
    df["private"] = yes(df["RPRIMTH"]).astype(float)
    df["public"] = yes(df["RPUBMTH"]).astype(float)
    df["medicaid"] = (yes(df["EMDMTH"]) | yes(df["RPUBTYPE2"])).astype(float)
    df["direct_purchase"] = (yes(df["RPRITYPE2"]) | yes(df["RMARKTPLACE"])).astype(float)
    df["marketplace_flag"] = (
        yes(df["RMARKTPLACE"]) | yes(df["EPRIEXCH1"]) | yes(df["EPRIEXCH2"]) | yes(df["EMDEXCH"])
    ).astype(float)
    df["subsidized_private"] = (yes(df["EPRISUBS1"]) | yes(df["EPRISUBS2"]) | yes(df["EMDSUBS"])).astype(float)
    df["market_or_subsidy"] = (
        df["direct_purchase"].eq(1) | df["marketplace_flag"].eq(1) | df["subsidized_private"].eq(1)
    ).astype(float)
    df["snap_month"] = yes(df["RSNAP_MNYN"]).astype(float)

    df["late_expansion_state"] = df["state_fips"].isin(LATE_EXPANSION_DATES).astype(int)
    df["never_expansion_state"] = df["state_fips"].isin(NEVER_EXPANSION).astype(int)
    df["implementation_ym"] = df["state_fips"].map({k: int(v.replace("-", "")) for k, v in LATE_EXPANSION_DATES.items()})
    df["expansion_active"] = (
        df["late_expansion_state"].eq(1) & df["implementation_ym"].notna() & df["month_id"].ge(df["implementation_ym"])
    ).astype(float)
    df["ever_sample_state"] = (df["late_expansion_state"].eq(1) | df["never_expansion_state"].eq(1)).astype(int)
    df["months_since_expansion"] = np.nan
    active_or_late = df["late_expansion_state"].eq(1) & df["implementation_ym"].notna()
    df.loc[active_or_late, "months_since_expansion"] = (
        (df.loc[active_or_late, "month_id"] // 100 - df.loc[active_or_late, "implementation_ym"] // 100) * 12
        + (df.loc[active_or_late, "month_id"] % 100 - df.loc[active_or_late, "implementation_ym"] % 100)
    )
    return df


def build_model_frame(df: pd.DataFrame, spec: str) -> tuple[pd.DataFrame, pd.DataFrame, str]:
    d = df[
        df["ever_sample_state"].eq(1)
        & df["age"].between(19, 64, inclusive="both")
        & df["medicare"].ne(1)
        & df["weight"].gt(0)
    ].copy()

    if spec == "broad_000_250_monthly_fpl":
        d = d[d["fpl_monthly"].between(0.0, 2.5, inclusive="both")].copy()
        d["eligible"] = d["fpl_monthly"].le(1.38).astype(float)
        label = "monthly FPL 0-250%, eligible <=138%"
    elif spec == "near_100_250_monthly_fpl":
        d = d[d["fpl_monthly"].between(1.0, 2.5, inclusive="both")].copy()
        d["eligible"] = d["fpl_monthly"].le(1.38).astype(float)
        label = "monthly FPL 100-250%, eligible 100-138%"
    elif spec == "broad_000_250_annual_fpl":
        d = d[d["fpl_annual"].between(0.0, 2.5, inclusive="both")].copy()
        d["eligible"] = d["fpl_annual"].le(1.38).astype(float)
        label = "annual FPL 0-250%, eligible <=138%"
    elif spec == "near_100_250_annual_fpl":
        d = d[d["fpl_annual"].between(1.0, 2.5, inclusive="both")].copy()
        d["eligible"] = d["fpl_annual"].le(1.38).astype(float)
        label = "annual FPL 100-250%, eligible 100-138%"
    elif spec == "near_100_200_monthly_fpl_no_disabled_ssi":
        d = d[
            d["fpl_monthly"].between(1.0, 2.0, inclusive="both")
            & d["disabled"].ne(1)
            & d["ssi_year"].ne(1)
        ].copy()
        d["eligible"] = d["fpl_monthly"].le(1.38).astype(float)
        label = "monthly FPL 100-200%, eligible 100-138%, excluding disability/SSI"
    else:
        raise ValueError(spec)

    d["active_x_eligible"] = d["expansion_active"] * d["eligible"]
    fpl_col = "fpl_annual" if "annual" in spec else "fpl_monthly"
    parts: list[pd.Series | pd.DataFrame] = [
        pd.Series(1.0, index=d.index, name="const"),
        d["expansion_active"].rename("expansion_active"),
        d["eligible"].rename("eligible"),
        d["active_x_eligible"].rename("active_x_eligible"),
        d[fpl_col].rename("fpl"),
        (d[fpl_col] ** 2).rename("fpl_sq"),
        d["age"].rename("age"),
        (d["age"] ** 2).rename("age_sq"),
        d["female"].rename("female"),
        d["black"].rename("black"),
        d["hispanic"].rename("hispanic"),
        d["disabled"].rename("disabled"),
    ]
    parts.append(pd.get_dummies(d["state_fips"].astype(str), prefix="state", drop_first=True, dtype=float))
    parts.append(pd.get_dummies(d["year_month"].astype(str), prefix="ym", drop_first=True, dtype=float))
    x = pd.concat(parts, axis=1)
    return d, x, label


def estimate(df: pd.DataFrame, x: pd.DataFrame, outcomes: list[str], spec: str, label: str) -> pd.DataFrame:
    rows = []
    x_np = x.to_numpy(dtype=float)
    w_np = df["weight"].to_numpy(dtype=float)
    state_cluster = df["state_fips"].to_numpy()
    person_cluster = df["person_id"].to_numpy()
    for outcome in outcomes:
        y = df[outcome].to_numpy(dtype=float)
        beta_s, se_hc1, se_state, n, g_state = weighted_ols_cluster(y, x_np, w_np, state_cluster)
        _, _, se_person, _, g_person = weighted_ols_cluster(y, x_np, w_np, person_cluster)
        b = pd.Series(beta_s, index=x.columns)
        hc1 = pd.Series(se_hc1, index=x.columns)
        st = pd.Series(se_state, index=x.columns)
        ps = pd.Series(se_person, index=x.columns)
        term = "active_x_eligible"
        coef = b.get(term, np.nan)
        rows.append(
            {
                "spec": spec,
                "label": label,
                "outcome": outcome,
                "term": term,
                "coef": coef,
                "se_hc1": hc1.get(term, np.nan),
                "t_hc1": coef / hc1.get(term, np.nan) if hc1.get(term, np.nan) > 0 else np.nan,
                "se_state_cluster": st.get(term, np.nan),
                "t_state_cluster": coef / st.get(term, np.nan) if st.get(term, np.nan) > 0 else np.nan,
                "se_person_cluster": ps.get(term, np.nan),
                "t_person_cluster": coef / ps.get(term, np.nan) if ps.get(term, np.nan) > 0 else np.nan,
                "n": n,
                "persons": int(df["person_id"].nunique()),
                "states": int(df["state_fips"].nunique()),
                "state_clusters": g_state,
                "person_clusters": g_person,
                "weighted_mean": wmean(df[outcome], df["weight"]),
            }
        )
    return pd.DataFrame(rows)


def support_tables(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    low = df[
        df["ever_sample_state"].eq(1)
        & df["age"].between(19, 64, inclusive="both")
        & df["medicare"].ne(1)
        & df["fpl_monthly"].between(1.0, 1.38, inclusive="both")
        & df["weight"].gt(0)
    ].copy()
    rows = []
    for state, g in low[low["late_expansion_state"].eq(1)].groupby("state_fips"):
        impl = int(LATE_EXPANSION_DATES[state].replace("-", ""))
        pre = g[g["month_id"].lt(impl)]
        post = g[g["month_id"].ge(impl)]
        for period, h in [("pre", pre), ("post", post)]:
            rows.append(
                {
                    "state_fips": state,
                    "state_name": STATE_NAMES.get(state, state),
                    "implementation": LATE_EXPANSION_DATES[state],
                    "period": period,
                    "person_months": int(len(h)),
                    "persons": int(h["person_id"].nunique()),
                    "medicaid": wmean(h["medicaid"], h["weight"]) if len(h) else np.nan,
                    "uninsured": wmean(h["uninsured"], h["weight"]) if len(h) else np.nan,
                    "direct_purchase": wmean(h["direct_purchase"], h["weight"]) if len(h) else np.nan,
                    "market_or_subsidy": wmean(h["market_or_subsidy"], h["weight"]) if len(h) else np.nan,
                }
            )
    state_support = pd.DataFrame(rows)

    cell_rows = []
    d = df[
        df["ever_sample_state"].eq(1)
        & df["age"].between(19, 64, inclusive="both")
        & df["medicare"].ne(1)
        & df["fpl_monthly"].between(0.0, 2.5, inclusive="both")
        & df["weight"].gt(0)
    ].copy()
    d["eligible"] = d["fpl_monthly"].le(1.38).astype(int)
    for (active, elig), g in d.groupby(["expansion_active", "eligible"], observed=True):
        cell_rows.append(
            {
                "expansion_active": int(active),
                "eligible_le_138": int(elig),
                "person_months": int(len(g)),
                "persons": int(g["person_id"].nunique()),
                "states": int(g["state_fips"].nunique()),
                "medicaid": wmean(g["medicaid"], g["weight"]),
                "uninsured": wmean(g["uninsured"], g["weight"]),
                "direct_purchase": wmean(g["direct_purchase"], g["weight"]),
                "market_or_subsidy": wmean(g["market_or_subsidy"], g["weight"]),
                "snap_month": wmean(g["snap_month"], g["weight"]),
            }
        )
    cell_support = pd.DataFrame(cell_rows)
    return state_support, cell_support


def md_table(df: pd.DataFrame, cols: list[str], max_rows: int | None = None) -> str:
    d = df[cols].copy()
    if max_rows is not None:
        d = d.head(max_rows)
    lines = ["| " + " | ".join(cols) + " |", "|" + "|".join(["---"] * len(cols)) + "|"]
    for _, row in d.iterrows():
        vals = []
        for c in cols:
            v = row[c]
            if isinstance(v, float):
                vals.append("" if np.isnan(v) else f"{v:.4f}")
            else:
                vals.append(str(v))
        lines.append("| " + " | ".join(vals) + " |")
    return "\n".join(lines)


def fmt(est: pd.DataFrame, spec: str, outcomes: list[str]) -> str:
    d = est[est["spec"].eq(spec)].set_index("outcome")
    lines = []
    for outcome in outcomes:
        if outcome in d.index:
            r = d.loc[outcome]
            lines.append(
                f"- `{outcome}`: {r['coef']:+.4f}, state-cluster se {r['se_state_cluster']:.4f}, "
                f"t {r['t_state_cluster']:.2f}; person-cluster se {r['se_person_cluster']:.4f}, "
                f"t {r['t_person_cluster']:.2f}."
            )
    return "\n".join(lines)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    df = prep()
    outcomes = [
        "medicaid",
        "uninsured",
        "any_coverage",
        "public",
        "private",
        "direct_purchase",
        "marketplace_flag",
        "market_or_subsidy",
        "snap_month",
    ]
    specs = [
        "broad_000_250_monthly_fpl",
        "near_100_250_monthly_fpl",
        "broad_000_250_annual_fpl",
        "near_100_250_annual_fpl",
        "near_100_200_monthly_fpl_no_disabled_ssi",
    ]
    estimates = []
    supports = []
    for spec in specs:
        d, x, label = build_model_frame(df, spec)
        estimates.append(estimate(d, x, outcomes, spec, label))
        supports.append(
            {
                "spec": spec,
                "label": label,
                "person_months": int(len(d)),
                "persons": int(d["person_id"].nunique()),
                "states": int(d["state_fips"].nunique()),
                "treated_active_person_months": int(d["expansion_active"].sum()),
                "eligible_person_months": int(d["eligible"].sum()),
                "active_eligible_person_months": int(d["active_x_eligible"].sum()),
                "active_eligible_persons": int(d.loc[d["active_x_eligible"].eq(1), "person_id"].nunique()),
            }
        )
    est = pd.concat(estimates, ignore_index=True)
    support = pd.DataFrame(supports)
    state_support, cell_support = support_tables(df)

    est.to_csv(OUT / "late_medicaid_expansion_threshold_estimates.csv", index=False)
    support.to_csv(OUT / "late_medicaid_expansion_threshold_support.csv", index=False)
    state_support.to_csv(OUT / "late_medicaid_expansion_state_support.csv", index=False)
    cell_support.to_csv(OUT / "late_medicaid_expansion_cell_support.csv", index=False)

    report = f"""# Late Medicaid Expansion Threshold Test

## Purpose

This screen tests whether late ACA Medicaid expansion adoptions can support a publishable adult
SIPP design. The policy question remains live because KFF reports that, as of May 2026, 41 states
including DC have adopted expansion while 10 have not. The empirical problem is that the broad
Medicaid-expansion literature is already large, so a SIPP project needs a stronger contribution than
the usual "expansion increased Medicaid coverage" result.

## Design

- Unit: person-month.
- Sample states: late expansion states plus never-expansion states.
- Main adults: age 19-64, non-Medicare.
- Main income design: 0-250% monthly FPL, with `eligible <=138% FPL`.
- Narrow design: 100-250% monthly FPL, with `eligible = 100-138% FPL`.
- Treatment: state-month Medicaid expansion active after each late-adopter implementation month.
- Main term: `expansion_active x eligible`.
- Fixed effects: state and calendar year-month.
- Controls: FPL quadratic, age quadratic, sex, Black, Hispanic, disability.
- Inference: state-clustered and person-clustered standard errors.

Late expansion dates coded here:

- Maine and Virginia: 2019-01.
- Idaho and Utah: 2020-01.
- Nebraska: 2020-10.
- Oklahoma: 2021-07.
- Missouri: 2021-10.
- South Dakota: 2023-07.
- North Carolina: 2023-12.

## Support by Specification

{md_table(support, ['spec', 'person_months', 'persons', 'states', 'treated_active_person_months', 'eligible_person_months', 'active_eligible_person_months', 'active_eligible_persons'])}

## 100-138% FPL Treated-State Support

{md_table(state_support, ['state_name', 'implementation', 'period', 'person_months', 'persons', 'medicaid', 'uninsured', 'direct_purchase', 'market_or_subsidy'])}

## Broad Monthly-FPL DDD Estimates

Spec: 0-250% monthly FPL, eligible <=138%.

{fmt(est, 'broad_000_250_monthly_fpl', outcomes)}

## Narrow Monthly-FPL DDD Estimates

Spec: 100-250% monthly FPL, eligible 100-138%.

{fmt(est, 'near_100_250_monthly_fpl', outcomes)}

## Annual-FPL Robustness

Broad annual-FPL spec:

{fmt(est, 'broad_000_250_annual_fpl', outcomes)}

Narrow annual-FPL spec:

{fmt(est, 'near_100_250_annual_fpl', outcomes)}

## Non-Disability / Non-SSI Narrow Robustness

Spec: 100-200% monthly FPL, excluding disability and SSI.

{fmt(est, 'near_100_200_monthly_fpl_no_disabled_ssi', outcomes)}

## Initial Interpretation

A strong SIPP paper would need Medicaid increases and uninsured declines concentrated below 138%
FPL, with limited placebo movement above the threshold and enough treated-state support after
implementation. If the result is only "Medicaid rises" but uninsured does not fall, or if estimates
are unstable across monthly and annual FPL, the idea is empirically feasible but not novel enough
relative to the existing Medicaid-expansion literature.

## Artifacts

- `script/11_idea_scan/29_late_medicaid_expansion_threshold_test.py`
- `result/idea_scan/late_medicaid_expansion_threshold_estimates.csv`
- `result/idea_scan/late_medicaid_expansion_threshold_support.csv`
- `result/idea_scan/late_medicaid_expansion_state_support.csv`
- `result/idea_scan/late_medicaid_expansion_cell_support.csv`
"""
    REPORT.write_text(report, encoding="utf-8")
    print(support.to_string(index=False))
    print(est.to_string(index=False))


if __name__ == "__main__":
    main()
