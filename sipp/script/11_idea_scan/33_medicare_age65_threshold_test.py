from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
PANEL = ROOT / "data" / "analysis_ready" / "sipp_2018_2024_person_month_panel.parquet"
OUT = ROOT / "result" / "idea_scan"
REPORT = ROOT / "report" / "67_medicare_age65_threshold_test.md"


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
        "TAGE_EHC",
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
        "TMDPAY",
        "TVISDOC",
        "TVISDENT",
        "THOSPNIT",
        "TFINCPOV",
        "TFCYINCPOV",
    ]
    df = pd.read_parquet(PANEL, columns=cols)
    df["state_fips"] = df["state_fips"].astype(str).str.zfill(2)
    df["ym"] = df["reference_year"].astype(int).astype(str) + "-" + df["reference_month"].astype(int).astype(str).str.zfill(2)
    df["age_monthly"] = bounded_numeric(df["TAGE_EHC"], 0, 100)
    df["age_static"] = bounded_numeric(df["TAGE"], 0, 100)
    df["age"] = df["age_monthly"].where(df["age_monthly"].notna(), df["age_static"])
    df["female"] = pd.to_numeric(df["ESEX"], errors="coerce").eq(2).astype(float)
    df["black"] = pd.to_numeric(df["ERACE"], errors="coerce").eq(2).astype(float)
    df["hispanic"] = (yes(df["EORIGIN"]) | yes(df.get("EHISPAN"))).astype(float)
    df["disabled"] = yes(df["RDIS"]).astype(float)
    df["monthly_fpl"] = bounded_numeric(df["TFINCPOV"], 0, 20)
    df["annual_fpl"] = bounded_numeric(df["TFCYINCPOV"], 0, 20)
    df["weight"] = clean_weight(df)

    df["any_coverage"] = yes(df["RHLTHMTH"]).astype(float)
    df["uninsured"] = pd.to_numeric(df["RHLTHMTH"], errors="coerce").eq(2).astype(float)
    df["private"] = yes(df["RPRIMTH"]).astype(float)
    df["public"] = yes(df["RPUBMTH"]).astype(float)
    df["medicare"] = yes(df["RPUBTYPE1"]).astype(float)
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
    df["oop_gt_0"] = pd.to_numeric(df["TMDPAY"], errors="coerce").gt(0).astype(float)
    df["oop_gt_1000"] = pd.to_numeric(df["TMDPAY"], errors="coerce").gt(1000).astype(float)
    df["doctor_visit_any"] = pd.to_numeric(df["TVISDOC"], errors="coerce").gt(0).astype(float)
    df["dentist_visit_any"] = pd.to_numeric(df["TVISDENT"], errors="coerce").gt(0).astype(float)
    df["hospital_night_any"] = pd.to_numeric(df["THOSPNIT"], errors="coerce").gt(0).astype(float)
    df["post_arpa"] = pd.to_numeric(df["reference_year"], errors="coerce").ge(2021).astype(float)
    return df


def build_frame(df: pd.DataFrame, spec: str) -> tuple[pd.DataFrame, pd.DataFrame, str]:
    d = df[df["weight"].gt(0)].copy()
    if spec == "age60_70_pooled":
        d = d[d["age"].between(60, 70, inclusive="both")].copy()
        label = "Age 60-70 pooled age-65 local linear"
    elif spec == "age62_68_pooled":
        d = d[d["age"].between(62, 68, inclusive="both")].copy()
        label = "Age 62-68 pooled age-65 local linear"
    elif spec == "age60_70_rd_did_arpa":
        d = d[d["age"].between(60, 70, inclusive="both")].copy()
        label = "Age 60-70 RD-DID: age-65 discontinuity change after 2021"
    elif spec == "age62_68_rd_did_arpa":
        d = d[d["age"].between(62, 68, inclusive="both")].copy()
        label = "Age 62-68 RD-DID: age-65 discontinuity change after 2021"
    else:
        raise ValueError(spec)

    d["running"] = d["age"] - 65.0
    d["above65"] = d["age"].ge(65).astype(float)
    d["running_above65"] = d["running"] * d["above65"]
    d["above65_post_arpa"] = d["above65"] * d["post_arpa"]
    d["running_post_arpa"] = d["running"] * d["post_arpa"]
    d["running_above65_post_arpa"] = d["running"] * d["above65"] * d["post_arpa"]

    if "rd_did" in spec:
        parts: list[pd.Series | pd.DataFrame] = [
            pd.Series(1.0, index=d.index, name="const"),
            d["above65"].rename("above65"),
            d["post_arpa"].rename("post_arpa"),
            d["above65_post_arpa"].rename("above65_post_arpa"),
            d["running"].rename("running"),
            d["running_above65"].rename("running_above65"),
            d["running_post_arpa"].rename("running_post_arpa"),
            d["running_above65_post_arpa"].rename("running_above65_post_arpa"),
            d["monthly_fpl"].fillna(d["monthly_fpl"].median()).rename("monthly_fpl"),
            d["female"].rename("female"),
            d["black"].rename("black"),
            d["hispanic"].rename("hispanic"),
            d["disabled"].rename("disabled"),
        ]
        term = "above65_post_arpa"
    else:
        parts = [
            pd.Series(1.0, index=d.index, name="const"),
            d["above65"].rename("above65"),
            d["running"].rename("running"),
            d["running_above65"].rename("running_above65"),
            d["monthly_fpl"].fillna(d["monthly_fpl"].median()).rename("monthly_fpl"),
            d["female"].rename("female"),
            d["black"].rename("black"),
            d["hispanic"].rename("hispanic"),
            d["disabled"].rename("disabled"),
        ]
        term = "above65"
    parts.append(pd.get_dummies(d["ym"].astype(str), prefix="ym", drop_first=True, dtype=float))
    x = pd.concat(parts, axis=1)
    x.attrs["term"] = term
    return d, x, label


def estimate(d: pd.DataFrame, x: pd.DataFrame, outcomes: list[str], spec: str, label: str) -> pd.DataFrame:
    rows = []
    x_np = x.to_numpy(dtype=float)
    w_np = d["weight"].to_numpy(dtype=float)
    person_cluster = d["person_id"].to_numpy()
    term = x.attrs["term"]
    for outcome in outcomes:
        y = d[outcome].to_numpy(dtype=float)
        beta, se_hc1, se_person, n, g_person = weighted_ols_cluster(y, x_np, w_np, person_cluster)
        b = pd.Series(beta, index=x.columns)
        hc1 = pd.Series(se_hc1, index=x.columns)
        ps = pd.Series(se_person, index=x.columns)
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
                "se_person_cluster": ps.get(term, np.nan),
                "t_person_cluster": coef / ps.get(term, np.nan) if ps.get(term, np.nan) > 0 else np.nan,
                "n": n,
                "persons": int(d["person_id"].nunique()),
                "age_min": float(d["age"].min()),
                "age_max": float(d["age"].max()),
                "weighted_mean": wmean(d[outcome], d["weight"]),
            }
        )
    return pd.DataFrame(rows)


def support_tables(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    d = df[df["age"].between(60, 70, inclusive="both") & df["weight"].gt(0)].copy()
    age_rows = []
    for age, g in d.groupby("age", observed=True):
        age_rows.append(
            {
                "age": int(age),
                "person_months": int(len(g)),
                "persons": int(g["person_id"].nunique()),
                "medicare": wmean(g["medicare"], g["weight"]),
                "uninsured": wmean(g["uninsured"], g["weight"]),
                "direct_purchase": wmean(g["direct_purchase"], g["weight"]),
                "marketplace_flag": wmean(g["marketplace_flag"], g["weight"]),
                "private": wmean(g["private"], g["weight"]),
                "oop_gt_1000": wmean(g["oop_gt_1000"], g["weight"]),
                "doctor_visit_any": wmean(g["doctor_visit_any"], g["weight"]),
            }
        )
    age_support = pd.DataFrame(age_rows).sort_values("age")

    cell_rows = []
    d["age_side"] = np.where(d["age"].lt(65), "60_64", "65_70")
    d["period"] = np.where(d["post_arpa"].eq(1), "post_2021_2023", "pre_2017_2020")
    for (period, side), g in d.groupby(["period", "age_side"], observed=True):
        row = {
            "period": period,
            "age_side": side,
            "person_months": int(len(g)),
            "persons": int(g["person_id"].nunique()),
        }
        for outcome in [
            "medicare",
            "uninsured",
            "any_coverage",
            "private",
            "direct_purchase",
            "marketplace_flag",
            "market_or_subsidy",
            "oop_gt_1000",
            "doctor_visit_any",
        ]:
            row[outcome] = wmean(g[outcome], g["weight"])
        cell_rows.append(row)
    cell_support = pd.DataFrame(cell_rows).sort_values(["period", "age_side"])

    fpl_rows = []
    for label, g in [
        ("low_income_le250", d[d["monthly_fpl"].le(2.5)]),
        ("middle_income_250_600", d[d["monthly_fpl"].between(2.5, 6.0, inclusive="right")]),
        ("all_age60_70", d),
    ]:
        fpl_rows.append(
            {
                "sample": label,
                "person_months": int(len(g)),
                "persons": int(g["person_id"].nunique()),
                "pre_60_64_uninsured": wmean(
                    g[(g["post_arpa"].eq(0)) & (g["age"].lt(65))]["uninsured"],
                    g[(g["post_arpa"].eq(0)) & (g["age"].lt(65))]["weight"],
                ),
                "post_60_64_uninsured": wmean(
                    g[(g["post_arpa"].eq(1)) & (g["age"].lt(65))]["uninsured"],
                    g[(g["post_arpa"].eq(1)) & (g["age"].lt(65))]["weight"],
                ),
                "pre_60_64_market_or_subsidy": wmean(
                    g[(g["post_arpa"].eq(0)) & (g["age"].lt(65))]["market_or_subsidy"],
                    g[(g["post_arpa"].eq(0)) & (g["age"].lt(65))]["weight"],
                ),
                "post_60_64_market_or_subsidy": wmean(
                    g[(g["post_arpa"].eq(1)) & (g["age"].lt(65))]["market_or_subsidy"],
                    g[(g["post_arpa"].eq(1)) & (g["age"].lt(65))]["weight"],
                ),
            }
        )
    fpl_support = pd.DataFrame(fpl_rows)
    return age_support, cell_support, fpl_support


def md_table(df: pd.DataFrame, cols: list[str]) -> str:
    lines = ["| " + " | ".join(cols) + " |", "|" + "|".join(["---"] * len(cols)) + "|"]
    for _, row in df[cols].iterrows():
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
                f"- `{outcome}`: {r['coef']:+.4f}, HC1 se {r['se_hc1']:.4f}, t {r['t_hc1']:.2f}; "
                f"person-cluster se {r['se_person_cluster']:.4f}, t {r['t_person_cluster']:.2f}."
            )
    return "\n".join(lines)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    df = prep()
    outcomes = [
        "medicare",
        "uninsured",
        "any_coverage",
        "public",
        "private",
        "direct_purchase",
        "marketplace_flag",
        "market_or_subsidy",
        "medicaid",
        "oop_gt_0",
        "oop_gt_1000",
        "doctor_visit_any",
        "dentist_visit_any",
        "hospital_night_any",
    ]
    specs = ["age60_70_pooled", "age62_68_pooled", "age60_70_rd_did_arpa", "age62_68_rd_did_arpa"]
    estimates = []
    support_rows = []
    for spec in specs:
        d, x, label = build_frame(df, spec)
        estimates.append(estimate(d, x, outcomes, spec, label))
        support_rows.append(
            {
                "spec": spec,
                "label": label,
                "person_months": int(len(d)),
                "persons": int(d["person_id"].nunique()),
                "age_min": float(d["age"].min()),
                "age_max": float(d["age"].max()),
                "below65_person_months": int(d["age"].lt(65).sum()),
                "above65_person_months": int(d["age"].ge(65).sum()),
                "below65_persons": int(d.loc[d["age"].lt(65), "person_id"].nunique()),
                "above65_persons": int(d.loc[d["age"].ge(65), "person_id"].nunique()),
            }
        )
    est = pd.concat(estimates, ignore_index=True)
    support = pd.DataFrame(support_rows)
    age_support, cell_support, fpl_support = support_tables(df)
    est.to_csv(OUT / "medicare_age65_estimates.csv", index=False)
    support.to_csv(OUT / "medicare_age65_support.csv", index=False)
    age_support.to_csv(OUT / "medicare_age65_age_bins.csv", index=False)
    cell_support.to_csv(OUT / "medicare_age65_prepost_cells.csv", index=False)
    fpl_support.to_csv(OUT / "medicare_age65_fpl_prepost_support.csv", index=False)

    report = f"""# Medicare Age-65 Threshold / ARPA Older-Adult Coverage Screen

## Purpose

This screen tests a non-state-policy adult design: the Medicare eligibility threshold at age 65.
The policy question is current because older adults ages 50-64 are highly exposed to Marketplace
premium affordability, enhanced premium tax credit expiration, and periodic proposals to lower the
Medicare eligibility age to 60. The identification appeal is the age-65 statutory threshold.

The innovation would need to be narrower than a standard Medicare-at-65 RD, because that literature
already exists. The possible SIPP contribution is monthly coverage-path substitution in the recent
ACA/ARPA Marketplace era:

- uninsured -> Medicare at age 65;
- direct-purchase / Marketplace -> Medicare at age 65;
- whether the age-65 discontinuity changed after ARPA improved pre-65 Marketplace affordability.

## Data And Design

- Unit: person-month.
- Running variable: `TAGE_EHC`, monthly age during the reference year; falls back to `TAGE` if
  needed.
- Main window: ages 60-70.
- Narrow window: ages 62-68.
- Threshold: age >=65.
- Pooled RD term: `above65`.
- RD-DID term: `above65 x post_2021_2023`.
- Fixed effects: calendar year-month.
- Controls: FPL, sex, Black, Hispanic, disability.
- Inference: person-clustered standard errors.

## Support

{md_table(support, ['spec', 'person_months', 'persons', 'age_min', 'age_max', 'below65_person_months', 'above65_person_months', 'below65_persons', 'above65_persons'])}

## Age-Bin Means

{md_table(age_support, ['age', 'person_months', 'persons', 'medicare', 'uninsured', 'direct_purchase', 'marketplace_flag', 'private', 'oop_gt_1000', 'doctor_visit_any'])}

## Pre/Post Cells

{md_table(cell_support, ['period', 'age_side', 'person_months', 'persons', 'medicare', 'uninsured', 'any_coverage', 'private', 'direct_purchase', 'market_or_subsidy', 'oop_gt_1000', 'doctor_visit_any'])}

## Pre-65 Older Adult ARPA Descriptives

{md_table(fpl_support, ['sample', 'person_months', 'persons', 'pre_60_64_uninsured', 'post_60_64_uninsured', 'pre_60_64_market_or_subsidy', 'post_60_64_market_or_subsidy'])}

## Pooled Age-65 RD Estimates

Age 60-70:

{fmt(est, 'age60_70_pooled', outcomes)}

Age 62-68:

{fmt(est, 'age62_68_pooled', outcomes)}

## RD-DID: Did The Age-65 Discontinuity Change After ARPA?

Age 60-70:

{fmt(est, 'age60_70_rd_did_arpa', outcomes)}

Age 62-68:

{fmt(est, 'age62_68_rd_did_arpa', outcomes)}

## Initial Interpretation

A viable new paper would need more than the canonical Medicare first stage. It would need evidence
that recent Marketplace policy changed the pre-65 side of the threshold or the size/composition of
the age-65 coverage transition. If the only finding is that Medicare rises sharply at age 65 and
uninsurance falls, the design is empirically clean but not novel enough.

## Artifacts

- `script/11_idea_scan/33_medicare_age65_threshold_test.py`
- `result/idea_scan/medicare_age65_estimates.csv`
- `result/idea_scan/medicare_age65_support.csv`
- `result/idea_scan/medicare_age65_age_bins.csv`
- `result/idea_scan/medicare_age65_prepost_cells.csv`
- `result/idea_scan/medicare_age65_fpl_prepost_support.csv`
"""
    REPORT.write_text(report, encoding="utf-8")
    print(support.to_string(index=False))
    print(est.to_string(index=False))


if __name__ == "__main__":
    main()
