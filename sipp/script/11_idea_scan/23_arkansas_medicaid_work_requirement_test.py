from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
PANEL = ROOT / "data" / "analysis_ready" / "sipp_2018_2024_person_month_panel.parquet"
OUT = ROOT / "result" / "idea_scan"
REPORT = ROOT / "report" / "48_arkansas_medicaid_work_requirement_test.md"


SOURCES = [
    "KFF Medicaid work requirements resources: https://www.kff.org/medicaid/medicaid-work-requirements-tracker-resources/",
    "KFF 5 key facts about Medicaid work requirements: https://www.kff.org/medicaid/5-key-facts-about-medicaid-work-requirements/",
    "NEJM results from the first year in Arkansas: https://www.nejm.org/doi/full/10.1056/NEJMsr1901772",
    "Health Affairs two-year impacts: https://www.healthaffairs.org/doi/abs/10.1377/hlthaff.2020.00538",
]


REGIONAL_STATES = {
    "01": "Alabama",
    "05": "Arkansas",
    "21": "Kentucky",
    "22": "Louisiana",
    "28": "Mississippi",
    "29": "Missouri",
    "40": "Oklahoma",
    "47": "Tennessee",
    "48": "Texas",
}


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
    diag = np.diag(cov)
    se = np.sqrt(np.where(diag >= 0, diag, np.nan))
    return beta, se, int(n), g_count


def add_fe(parts: list[pd.Series | pd.DataFrame], d: pd.DataFrame, fe_cols: list[str]) -> pd.DataFrame:
    for col in fe_cols:
        parts.append(pd.get_dummies(d[col].astype(str), prefix=col, drop_first=True, dtype=float))
    return pd.concat(parts, axis=1)


def build_month_panel() -> pd.DataFrame:
    cols = [
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
        "RDIS",
        "WPFINWGT",
        "TSSSAMT",
        "RHLTHMTH",
        "RPRIMTH",
        "RPUBMTH",
        "EMDMTH",
        "RMCAIDANN",
        "RMWKWJB",
        "RMESR",
        "TPEARN",
    ]
    df = pd.read_parquet(PANEL, columns=cols)
    df = df[df["reference_year"].between(2017, 2019)].copy()
    df["state_fips"] = df["state_fips"].astype(str).str.zfill(2)
    df = df[df["state_fips"].isin(REGIONAL_STATES)].copy()
    df["age"] = bounded_numeric(df["TAGE"], 0, 100)
    df["fpl"] = bounded_numeric(df["TFINCPOV"], 0, 20)
    df["female"] = pd.to_numeric(df["ESEX"], errors="coerce").eq(2).astype(float)
    df["black"] = pd.to_numeric(df["ERACE"], errors="coerce").eq(2).astype(float)
    df["hispanic"] = yes(df["EHISPAN"]).astype(float)
    df["low_educ"] = pd.to_numeric(df["EEDUC"], errors="coerce").le(39).astype(float)
    df["disabled"] = yes(df["RDIS"]).astype(int)
    df["weight"] = clean_weight(df)

    df["medicaid"] = (yes(df["EMDMTH"]) | yes(df["RMCAIDANN"])).astype(float)
    df["public"] = yes(df["RPUBMTH"]).astype(float)
    df["private"] = yes(df["RPRIMTH"]).astype(float)
    df["any_coverage"] = yes(df["RHLTHMTH"]).astype(float)
    df["uninsured"] = df["RHLTHMTH"].eq(2).astype(float)
    df["employed_any_week"] = (
        pd.to_numeric(df["RMWKWJB"], errors="coerce").gt(0)
        | pd.to_numeric(df["RMESR"], errors="coerce").between(1, 5)
    ).astype(float)
    df["weeks_with_job"] = bounded_numeric(df["RMWKWJB"], 0, 5)
    earn = pd.to_numeric(df["TPEARN"], errors="coerce")
    df["earn_pos"] = earn.gt(0).astype(float)
    df["log_earnings"] = np.log1p(earn.clip(lower=0))

    df["month_id"] = df["reference_year"].astype(int) * 100 + df["reference_month"].astype(int)
    df["arkansas"] = df["state_fips"].eq("05").astype(int)
    df["target_30_49"] = df["age"].between(30, 49, inclusive="both").astype(int)
    df["active_jun_dec_2018"] = df["month_id"].between(201806, 201812, inclusive="both").astype(int)
    df["active_jun2018_mar2019"] = df["month_id"].between(201806, 201903, inclusive="both").astype(int)
    df["ar_target_x_2018_active"] = df["arkansas"] * df["target_30_49"] * df["active_jun_dec_2018"]
    df["ar_target_x_full_active"] = df["arkansas"] * df["target_30_49"] * df["active_jun2018_mar2019"]
    df["state_month"] = df["state_fips"] + "_" + df["month_id"].astype(str)
    df["state_target"] = df["state_fips"] + "_" + df["target_30_49"].astype(str)
    df["target_month"] = df["target_30_49"].astype(str) + "_" + df["month_id"].astype(str)

    baseline = (
        df[df["month_id"].between(201801, 201805, inclusive="both")]
        .groupby("person_id", observed=True)["medicaid"]
        .max()
        .rename("baseline_medicaid_jan_may_2018")
    )
    df = df.merge(baseline, on="person_id", how="left")
    df["baseline_medicaid_jan_may_2018"] = df["baseline_medicaid_jan_may_2018"].fillna(0).astype(int)
    return df


def prep_sample(df: pd.DataFrame, sample: str) -> pd.DataFrame:
    base = df[
        df["age"].between(19, 64, inclusive="both")
        & df["fpl"].between(0, 1.38, inclusive="both")
        & df["disabled"].eq(0)
        & df["weight"].gt(0)
    ].copy()
    if sample == "fpl100_2017_2019":
        return base[base["fpl"].le(1.0)].copy()
    if sample == "fpl138_2017_2019":
        return base.copy()
    if sample == "baseline_medicaid_2018_fpl138":
        return base[
            base["baseline_medicaid_jan_may_2018"].eq(1)
            & base["month_id"].between(201801, 201812, inclusive="both")
        ].copy()
    raise ValueError(sample)


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
                "n_person_months": n,
                "n_persons": int(s["person_id"].nunique()),
                "n_states": int(s["state_fips"].nunique()),
                "weighted_mean": wmean(s[outcome], s["weight"]),
            }
        )
    return pd.DataFrame(rows)


def support(d: pd.DataFrame, sample: str, term: str) -> pd.DataFrame:
    ar_target = d[d["arkansas"].eq(1) & d["target_30_49"].eq(1)]
    active = d[d[term].eq(1)]
    return pd.DataFrame(
        [
            {
                "sample": sample,
                "term": term,
                "person_months": int(len(d)),
                "persons": int(d["person_id"].nunique()),
                "states": int(d["state_fips"].nunique()),
                "arkansas_target_person_months": int(len(ar_target)),
                "arkansas_target_persons": int(ar_target["person_id"].nunique()),
                "active_arkansas_target_person_months": int(len(active)),
                "active_arkansas_target_persons": int(active["person_id"].nunique()),
                "weighted_mean_medicaid": wmean(d["medicaid"], d["weight"]),
                "weighted_mean_uninsured": wmean(d["uninsured"], d["weight"]),
                "weighted_mean_employed": wmean(d["employed_any_week"], d["weight"]),
            }
        ]
    )


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
    panel = build_month_panel()
    outcomes = [
        "medicaid",
        "public",
        "uninsured",
        "any_coverage",
        "private",
        "employed_any_week",
        "weeks_with_job",
        "earn_pos",
        "log_earnings",
    ]
    controls = ["age", "fpl", "female", "black", "hispanic", "low_educ"]
    fe_cols = ["state_month", "state_target", "target_month"]

    fpl100 = prep_sample(panel, "fpl100_2017_2019")
    fpl138 = prep_sample(panel, "fpl138_2017_2019")
    baseline = prep_sample(panel, "baseline_medicaid_2018_fpl138")

    estimates = pd.concat(
        [
            estimate(fpl100, "ar_target_x_2018_active", outcomes, "fpl100_jun_dec_2018", controls, fe_cols),
            estimate(fpl138, "ar_target_x_2018_active", outcomes, "fpl138_jun_dec_2018", controls, fe_cols),
            estimate(fpl138, "ar_target_x_full_active", outcomes, "fpl138_jun2018_mar2019", controls, fe_cols),
            estimate(
                baseline,
                "ar_target_x_2018_active",
                outcomes,
                "baseline_medicaid_2018_jun_dec",
                controls,
                fe_cols,
            ),
        ],
        ignore_index=True,
    )
    sup = pd.concat(
        [
            support(fpl100, "fpl100_2017_2019", "ar_target_x_2018_active"),
            support(fpl138, "fpl138_2017_2019", "ar_target_x_2018_active"),
            support(fpl138, "fpl138_2017_2019", "ar_target_x_full_active"),
            support(baseline, "baseline_medicaid_2018_fpl138", "ar_target_x_2018_active"),
        ],
        ignore_index=True,
    )

    panel.to_parquet(OUT / "arkansas_workreq_person_month_panel.parquet", index=False)
    estimates.to_csv(OUT / "arkansas_workreq_estimates.csv", index=False)
    sup.to_csv(OUT / "arkansas_workreq_support.csv", index=False)

    s100 = sup[(sup["sample"].eq("fpl100_2017_2019")) & (sup["term"].eq("ar_target_x_2018_active"))].iloc[0]
    s138 = sup[(sup["sample"].eq("fpl138_2017_2019")) & (sup["term"].eq("ar_target_x_2018_active"))].iloc[0]
    sb = sup[sup["sample"].eq("baseline_medicaid_2018_fpl138")].iloc[0]
    main_med = estimates[(estimates["model"].eq("baseline_medicaid_2018_jun_dec")) & (estimates["outcome"].eq("medicaid"))].iloc[0]
    main_unins = estimates[
        (estimates["model"].eq("baseline_medicaid_2018_jun_dec")) & (estimates["outcome"].eq("uninsured"))
    ].iloc[0]
    main_emp = estimates[
        (estimates["model"].eq("baseline_medicaid_2018_jun_dec")) & (estimates["outcome"].eq("employed_any_week"))
    ].iloc[0]
    verdict = "NO-CLEAN-GO"
    active_people = int(sb["active_arkansas_target_persons"])
    if (
        active_people >= 50
        and main_med["coef"] < -0.03
        and main_unins["coef"] > 0.02
        and main_emp["coef"] <= 0.02
    ):
        verdict = "POTENTIAL-GO-COVERAGE-LOSS-NO-EMPLOYMENT-GAIN"
    elif main_med["coef"] < 0 and main_unins["coef"] > 0:
        verdict = "REPLICATION-SIGNAL-BUT-TREATED-CELL-TOO-THIN"

    report = f"""# Arkansas Medicaid Work-Requirement Fast Test

## Question

Can the 2018 Arkansas Medicaid work and reporting requirement support a new adult SIPP paper on
coverage loss, employment, and medical-financial spillovers?

## Source Checks

{chr(10).join(f"- {s}" for s in SOURCES)}

Key policy facts:

- Arkansas implemented Medicaid work and reporting requirements beginning June 2018.
- The initial implementation targeted adults ages 30-49; requirements for ages 19-29 were planned
  for January 2019.
- KFF summarizes the requirements as being in effect from June 2018 through March 2019 and reports
  more than 18,000 coverage losses.
- NEJM and Health Affairs studies found coverage losses without employment gains, so the SIPP
  contribution would need to be a credible replication plus added outcomes.

## Design

- Unit: person-month, reference months 2017-2019.
- Geography: Arkansas plus regional comparison states: {", ".join(REGIONAL_STATES.values())}.
- Primary target: ages 30-49, low-income, nondisabled adults.
- Treatment: Arkansas x target age x active requirement months.
- Main active window: June-December 2018.
- Sensitivity active window: June 2018-March 2019.
- Fixed effects: state-month, state-target, target-month.
- Standard errors: clustered by state, with only nine regional state clusters.

## Support

FPL <= 100%, 2017-2019:

- Person-months: {int(s100['person_months']):,}.
- Persons: {int(s100['persons']):,}.
- Arkansas target person-months: {int(s100['arkansas_target_person_months']):,}.
- Active Arkansas target person-months: {int(s100['active_arkansas_target_person_months']):,}.
- Active Arkansas target persons: {int(s100['active_arkansas_target_persons']):,}.

FPL <= 138%, 2017-2019:

- Person-months: {int(s138['person_months']):,}.
- Persons: {int(s138['persons']):,}.
- Arkansas target person-months: {int(s138['arkansas_target_person_months']):,}.
- Active Arkansas target person-months: {int(s138['active_arkansas_target_person_months']):,}.
- Active Arkansas target persons: {int(s138['active_arkansas_target_persons']):,}.

Baseline Medicaid sample, FPL <= 138%, 2018:

- Person-months: {int(sb['person_months']):,}.
- Persons: {int(sb['persons']):,}.
- Arkansas target person-months: {int(sb['arkansas_target_person_months']):,}.
- Active Arkansas target person-months: {int(sb['active_arkansas_target_person_months']):,}.
- Active Arkansas target persons: {int(sb['active_arkansas_target_persons']):,}.

## Main Estimates

FPL <= 100%, June-December 2018:

{fmt(estimates, 'fpl100_jun_dec_2018', outcomes)}

FPL <= 138%, June-December 2018:

{fmt(estimates, 'fpl138_jun_dec_2018', outcomes)}

Baseline Medicaid sample, June-December 2018:

{fmt(estimates, 'baseline_medicaid_2018_jun_dec', outcomes)}

## Verdict

`{verdict}`

This is a high-current-policy question, but a clean SIPP GO requires three things at once: a visible
Medicaid/public coverage loss, a corresponding uninsured increase, and no offsetting employment gain
large enough to change the interpretation. The design also has a serious limitation: it is a
single-state short-duration policy with only nine regional state clusters in this screen.

## Artifacts

- `script/11_idea_scan/23_arkansas_medicaid_work_requirement_test.py`
- `result/idea_scan/arkansas_workreq_person_month_panel.parquet`
- `result/idea_scan/arkansas_workreq_support.csv`
- `result/idea_scan/arkansas_workreq_estimates.csv`
"""
    REPORT.write_text(report, encoding="utf-8")
    print(verdict)
    print(sup.to_string(index=False))
    print(estimates.to_string(index=False))


if __name__ == "__main__":
    main()
