from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
PANEL = ROOT / "data" / "analysis_ready" / "sipp_2018_2024_person_month_panel.parquet"
OUT = ROOT / "result" / "idea_scan"
REPORT = ROOT / "report" / "65_georgia_pathways_work_requirement_test.md"


CONTROL_STATES = {
    "01": "Alabama",
    "12": "Florida",
    "20": "Kansas",
    "28": "Mississippi",
    "45": "South Carolina",
    "47": "Tennessee",
    "48": "Texas",
    "55": "Wisconsin",
    "56": "Wyoming",
}
GEORGIA = "13"


def yes(s: pd.Series) -> pd.Series:
    return pd.to_numeric(s, errors="coerce").eq(1)


def clean_weight(df: pd.DataFrame) -> pd.Series:
    w = pd.to_numeric(df.get("WPFINWGT"), errors="coerce")
    w = w.where(w.gt(0), pd.to_numeric(df.get("TSSSAMT"), errors="coerce"))
    return w.where(w.gt(0), 1.0)


def bounded_numeric(s: pd.Series, lo: float, hi: float) -> pd.Series:
    out = pd.to_numeric(s, errors="coerce")
    return out.where(out.between(lo, hi, inclusive="both"))


def wmean(y: pd.Series, w: pd.Series) -> float:
    mask = y.notna() & w.notna() & w.gt(0)
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
        "reference_year",
        "reference_month",
        "state_fips",
        "TAGE",
        "ESEX",
        "ERACE",
        "EORIGIN",
        "EHISPAN",
        "RDIS",
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
        "RMESR",
        "RMWKWJB",
        "RWKESR1",
        "RWKESR2",
        "RWKESR3",
        "RWKESR4",
        "RWKESR5",
        "TPEARN",
        "TFINCPOV",
        "TFCYINCPOV",
    ]
    df = pd.read_parquet(PANEL, columns=cols)
    df["state_fips"] = df["state_fips"].astype(str).str.zfill(2)
    df["month_id"] = df["reference_year"].astype(int) * 100 + df["reference_month"].astype(int)
    df["ym"] = df["month_id"].astype(str)
    df["georgia"] = df["state_fips"].eq(GEORGIA).astype(float)
    df["control_state"] = df["state_fips"].isin(CONTROL_STATES).astype(int)
    df["analysis_state"] = (df["georgia"].eq(1) | df["control_state"].eq(1)).astype(int)
    df["age"] = bounded_numeric(df["TAGE"], 0, 100)
    df["female"] = pd.to_numeric(df["ESEX"], errors="coerce").eq(2).astype(float)
    df["black"] = pd.to_numeric(df["ERACE"], errors="coerce").eq(2).astype(float)
    df["hispanic"] = (yes(df["EORIGIN"]) | yes(df.get("EHISPAN"))).astype(float)
    df["disabled"] = yes(df["RDIS"]).astype(float)
    df["medicare"] = yes(df["RPUBTYPE1"]).astype(float)
    df["monthly_fpl"] = bounded_numeric(df["TFINCPOV"], 0, 10)
    df["annual_fpl"] = bounded_numeric(df["TFCYINCPOV"], 0, 10)
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
    df["market_or_subsidy"] = (
        df["direct_purchase"].eq(1)
        | df["marketplace_flag"].eq(1)
        | yes(df["EPRISUBS1"])
        | yes(df["EPRISUBS2"])
        | yes(df["EMDSUBS"])
    ).astype(float)
    df["snap_month"] = yes(df["RSNAP_MNYN"]).astype(float)
    df["earnings"] = pd.to_numeric(df["TPEARN"], errors="coerce").fillna(0)
    df["weekly_work_any"] = (
        yes(df["RWKESR1"]) | yes(df["RWKESR2"]) | yes(df["RWKESR3"]) | yes(df["RWKESR4"]) | yes(df["RWKESR5"])
    ).astype(float)
    df["work_activity_proxy"] = (
        df["earnings"].gt(0)
        | df["weekly_work_any"].eq(1)
        | pd.to_numeric(df["RMWKWJB"], errors="coerce").gt(0)
        | pd.to_numeric(df["RMESR"], errors="coerce").isin([1, 2, 3])
    ).astype(float)
    df["post_jul2023"] = df["month_id"].ge(202307).astype(float)
    df["post_sep2023"] = df["month_id"].ge(202309).astype(float)
    return df


def build_frame(df: pd.DataFrame, spec: str) -> tuple[pd.DataFrame, pd.DataFrame, str, str]:
    d = df[
        df["analysis_state"].eq(1)
        & df["age"].between(19, 64, inclusive="both")
        & df["medicare"].ne(1)
        & df["weight"].gt(0)
        & df["reference_year"].between(2022, 2023, inclusive="both")
    ].copy()
    if spec == "monthly_000_200_postjul_low100":
        d = d[d["monthly_fpl"].between(0, 2.0, inclusive="both")].copy()
        d["target"] = d["monthly_fpl"].le(1.0).astype(float)
        post_col = "post_jul2023"
        label = "monthly FPL 0-200%, target <=100%, post July 2023"
        fpl_col = "monthly_fpl"
    elif spec == "monthly_000_200_postsep_low100":
        d = d[d["monthly_fpl"].between(0, 2.0, inclusive="both")].copy()
        d["target"] = d["monthly_fpl"].le(1.0).astype(float)
        post_col = "post_sep2023"
        label = "monthly FPL 0-200%, target <=100%, post September 2023"
        fpl_col = "monthly_fpl"
    elif spec == "monthly_work_proxy_postjul_low100":
        d = d[d["monthly_fpl"].between(0, 2.0, inclusive="both") & d["work_activity_proxy"].eq(1)].copy()
        d["target"] = d["monthly_fpl"].le(1.0).astype(float)
        post_col = "post_jul2023"
        label = "monthly FPL 0-200%, work-activity proxy, target <=100%, post July 2023"
        fpl_col = "monthly_fpl"
    elif spec == "annual_000_200_postjul_low100":
        d = d[d["annual_fpl"].between(0, 2.0, inclusive="both")].copy()
        d["target"] = d["annual_fpl"].le(1.0).astype(float)
        post_col = "post_jul2023"
        label = "annual FPL 0-200%, target <=100%, post July 2023"
        fpl_col = "annual_fpl"
    elif spec == "monthly_050_150_postjul_low100":
        d = d[d["monthly_fpl"].between(0.5, 1.5, inclusive="both")].copy()
        d["target"] = d["monthly_fpl"].le(1.0).astype(float)
        post_col = "post_jul2023"
        label = "monthly FPL 50-150%, local target <=100%, post July 2023"
        fpl_col = "monthly_fpl"
    else:
        raise ValueError(spec)

    d["ga_post"] = d["georgia"] * d[post_col]
    d["ga_target"] = d["georgia"] * d["target"]
    d["post_target"] = d[post_col] * d["target"]
    d["ga_post_target"] = d["georgia"] * d[post_col] * d["target"]

    parts: list[pd.Series | pd.DataFrame] = [
        pd.Series(1.0, index=d.index, name="const"),
        d["georgia"].rename("georgia"),
        d[post_col].rename("post"),
        d["target"].rename("target"),
        d["ga_post"].rename("ga_post"),
        d["ga_target"].rename("ga_target"),
        d["post_target"].rename("post_target"),
        d["ga_post_target"].rename("ga_post_target"),
        d[fpl_col].rename("fpl"),
        (d[fpl_col] ** 2).rename("fpl_sq"),
        d["age"].rename("age"),
        (d["age"] ** 2).rename("age_sq"),
        d["female"].rename("female"),
        d["black"].rename("black"),
        d["hispanic"].rename("hispanic"),
        d["disabled"].rename("disabled"),
        d["work_activity_proxy"].rename("work_activity_proxy"),
    ]
    parts.append(pd.get_dummies(d["state_fips"].astype(str), prefix="state", drop_first=True, dtype=float))
    parts.append(pd.get_dummies(d["ym"].astype(str), prefix="ym", drop_first=True, dtype=float))
    x = pd.concat(parts, axis=1)
    return d, x, label, post_col


def estimate(d: pd.DataFrame, x: pd.DataFrame, outcomes: list[str], spec: str, label: str) -> pd.DataFrame:
    rows = []
    x_np = x.to_numpy(dtype=float)
    w_np = d["weight"].to_numpy(dtype=float)
    state_cluster = d["state_fips"].to_numpy()
    person_cluster = d["person_id"].to_numpy()
    for outcome in outcomes:
        y = d[outcome].to_numpy(dtype=float)
        beta, se_hc1, se_state, n, g_state = weighted_ols_cluster(y, x_np, w_np, state_cluster)
        _, _, se_person, _, g_person = weighted_ols_cluster(y, x_np, w_np, person_cluster)
        b = pd.Series(beta, index=x.columns)
        hc1 = pd.Series(se_hc1, index=x.columns)
        st = pd.Series(se_state, index=x.columns)
        ps = pd.Series(se_person, index=x.columns)
        coef = b.get("ga_post_target", np.nan)
        rows.append(
            {
                "spec": spec,
                "label": label,
                "outcome": outcome,
                "term": "georgia_x_post_x_target_low100",
                "coef": coef,
                "se_hc1": hc1.get("ga_post_target", np.nan),
                "t_hc1": coef / hc1.get("ga_post_target", np.nan) if hc1.get("ga_post_target", np.nan) > 0 else np.nan,
                "se_state_cluster": st.get("ga_post_target", np.nan),
                "t_state_cluster": coef / st.get("ga_post_target", np.nan)
                if st.get("ga_post_target", np.nan) > 0
                else np.nan,
                "se_person_cluster": ps.get("ga_post_target", np.nan),
                "t_person_cluster": coef / ps.get("ga_post_target", np.nan)
                if ps.get("ga_post_target", np.nan) > 0
                else np.nan,
                "n": n,
                "persons": int(d["person_id"].nunique()),
                "states": int(d["state_fips"].nunique()),
                "state_clusters": g_state,
                "person_clusters": g_person,
                "weighted_mean": wmean(d[outcome], d["weight"]),
            }
        )
    return pd.DataFrame(rows)


def support_tables(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    base = df[
        df["analysis_state"].eq(1)
        & df["age"].between(19, 64, inclusive="both")
        & df["medicare"].ne(1)
        & df["reference_year"].between(2022, 2023, inclusive="both")
        & df["monthly_fpl"].between(0, 2.0, inclusive="both")
        & df["weight"].gt(0)
    ].copy()
    base["period"] = np.select(
        [base["month_id"].between(202201, 202306), base["month_id"].between(202307, 202312)],
        ["pre_2022_to_jun2023", "post_jul_dec2023"],
        default="other",
    )
    base["target_low100"] = base["monthly_fpl"].le(1.0).astype(int)
    base["ga_state"] = base["state_fips"].eq(GEORGIA).astype(int)

    rows = []
    for (ga, period, target), g in base.groupby(["ga_state", "period", "target_low100"], observed=True):
        if period == "other":
            continue
        row = {
            "georgia": int(ga),
            "period": period,
            "target_low100": int(target),
            "person_months": int(len(g)),
            "persons": int(g["person_id"].nunique()),
            "states": int(g["state_fips"].nunique()),
            "work_activity_proxy": wmean(g["work_activity_proxy"], g["weight"]),
            "medicaid": wmean(g["medicaid"], g["weight"]),
            "uninsured": wmean(g["uninsured"], g["weight"]),
            "any_coverage": wmean(g["any_coverage"], g["weight"]),
            "private": wmean(g["private"], g["weight"]),
            "direct_purchase": wmean(g["direct_purchase"], g["weight"]),
            "market_or_subsidy": wmean(g["market_or_subsidy"], g["weight"]),
            "snap_month": wmean(g["snap_month"], g["weight"]),
        }
        rows.append(row)
    cell = pd.DataFrame(rows).sort_values(["georgia", "period", "target_low100"])

    state_rows = []
    for state, g in base[base["target_low100"].eq(1)].groupby("state_fips", observed=True):
        state_rows.append(
            {
                "state_fips": state,
                "state_name": "Georgia" if state == GEORGIA else CONTROL_STATES.get(state, state),
                "person_months": int(len(g)),
                "persons": int(g["person_id"].nunique()),
                "post_person_months": int(g["month_id"].ge(202307).sum()),
                "post_persons": int(g.loc[g["month_id"].ge(202307), "person_id"].nunique()),
                "medicaid_pre": wmean(g.loc[g["month_id"].lt(202307), "medicaid"], g.loc[g["month_id"].lt(202307), "weight"]),
                "medicaid_post": wmean(g.loc[g["month_id"].ge(202307), "medicaid"], g.loc[g["month_id"].ge(202307), "weight"]),
                "uninsured_pre": wmean(g.loc[g["month_id"].lt(202307), "uninsured"], g.loc[g["month_id"].lt(202307), "weight"]),
                "uninsured_post": wmean(g.loc[g["month_id"].ge(202307), "uninsured"], g.loc[g["month_id"].ge(202307), "weight"]),
            }
        )
    state_support = pd.DataFrame(state_rows).sort_values("state_fips")
    return cell, state_support


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
        "work_activity_proxy",
    ]
    specs = [
        "monthly_000_200_postjul_low100",
        "monthly_000_200_postsep_low100",
        "monthly_work_proxy_postjul_low100",
        "annual_000_200_postjul_low100",
        "monthly_050_150_postjul_low100",
    ]
    estimates = []
    supports = []
    for spec in specs:
        d, x, label, post_col = build_frame(df, spec)
        estimates.append(estimate(d, x, outcomes, spec, label))
        treated = d[d["georgia"].eq(1) & d["target"].eq(1)]
        post_treated = treated[treated[post_col].eq(1)]
        supports.append(
            {
                "spec": spec,
                "label": label,
                "person_months": int(len(d)),
                "persons": int(d["person_id"].nunique()),
                "states": int(d["state_fips"].nunique()),
                "ga_target_person_months": int(len(treated)),
                "ga_target_persons": int(treated["person_id"].nunique()),
                "ga_post_target_person_months": int(len(post_treated)),
                "ga_post_target_persons": int(post_treated["person_id"].nunique()),
                "ga_post_target_medicaid_months": int(post_treated["medicaid"].sum()),
                "ga_post_target_uninsured_months": int(post_treated["uninsured"].sum()),
                "ga_post_target_work_proxy_months": int(post_treated["work_activity_proxy"].sum()),
            }
        )
    est = pd.concat(estimates, ignore_index=True)
    support = pd.DataFrame(supports)
    cell, state_support = support_tables(df)
    est.to_csv(OUT / "georgia_pathways_estimates.csv", index=False)
    support.to_csv(OUT / "georgia_pathways_support.csv", index=False)
    cell.to_csv(OUT / "georgia_pathways_cell_means.csv", index=False)
    state_support.to_csv(OUT / "georgia_pathways_state_support.csv", index=False)

    report = f"""# Georgia Pathways to Coverage Work-Requirement Quick Screen

## Purpose

This screen tests whether SIPP can support a current adult Medicaid work-requirement paper using
Georgia Pathways to Coverage. Georgia launched Pathways in 2023 as a partial Medicaid expansion for
adults age 19-64 with income up to 100% FPL, conditioned on qualifying activities.

## Policy Design Checked

Official Georgia Pathways pages say eligible adults must:

- be Georgia residents;
- be ages 19-64;
- have household income up to 100% FPL;
- not qualify for another Medicaid category;
- complete at least 80 hours of qualifying activities per month.

The program began in 2023; this screen uses July 2023 as the main start month and September 2023 as
a sensitivity because early implementation and coverage start timing may lag application.

## Empirical Design

- Unit: person-month.
- Years: 2022-2023 only.
- Treated state: Georgia.
- Controls: never-expansion comparison states with no full ACA expansion in this period.
- Main sample: adults age 19-64, non-Medicare, 0-200% monthly FPL.
- Target group: <=100% FPL.
- Comparison income group: 100-200% FPL.
- Main term: `Georgia x post-July-2023 x <=100% FPL`.
- Fixed effects: state and calendar year-month.
- Controls: FPL quadratic, age quadratic, sex, Black, Hispanic, disability, work-activity proxy.
- Inference: state-clustered and person-clustered standard errors.

## Support

{md_table(support, ['spec', 'person_months', 'persons', 'states', 'ga_target_person_months', 'ga_target_persons', 'ga_post_target_person_months', 'ga_post_target_persons', 'ga_post_target_medicaid_months', 'ga_post_target_uninsured_months', 'ga_post_target_work_proxy_months'])}

## Raw Cell Means

Main monthly-FPL support cells:

{md_table(cell, ['georgia', 'period', 'target_low100', 'person_months', 'persons', 'work_activity_proxy', 'medicaid', 'uninsured', 'any_coverage', 'private', 'direct_purchase', 'snap_month'])}

## State Support For Target <=100% FPL

{md_table(state_support, ['state_name', 'person_months', 'persons', 'post_person_months', 'post_persons', 'medicaid_pre', 'medicaid_post', 'uninsured_pre', 'uninsured_post'])}

## Main Estimates

Monthly FPL 0-200%, target <=100%, post July 2023:

{fmt(est, 'monthly_000_200_postjul_low100', outcomes)}

Post September 2023 sensitivity:

{fmt(est, 'monthly_000_200_postsep_low100', outcomes)}

Work-activity proxy sample:

{fmt(est, 'monthly_work_proxy_postjul_low100', outcomes)}

Annual-FPL sensitivity:

{fmt(est, 'annual_000_200_postjul_low100', outcomes)}

Local 50-150% FPL sensitivity:

{fmt(est, 'monthly_050_150_postjul_low100', outcomes)}

## Initial Interpretation

A viable SIPP paper would need enough Georgia post-launch target observations and a coherent pattern:
Medicaid/public coverage rising for <=100% FPL adults relative to 100-200% FPL adults and comparable
non-expansion states, or a precisely estimated null consistent with administrative barriers. If the
Georgia post-launch target cell has very few Medicaid months, the policy is important but SIPP is
not the right main dataset.

## Artifacts

- `script/11_idea_scan/32_georgia_pathways_work_requirement_test.py`
- `result/idea_scan/georgia_pathways_estimates.csv`
- `result/idea_scan/georgia_pathways_support.csv`
- `result/idea_scan/georgia_pathways_cell_means.csv`
- `result/idea_scan/georgia_pathways_state_support.csv`
"""
    REPORT.write_text(report, encoding="utf-8")
    print(support.to_string(index=False))
    print(est.to_string(index=False))


if __name__ == "__main__":
    main()
