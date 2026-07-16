from __future__ import annotations

from pathlib import Path
import zipfile

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
PANEL = ROOT / "data" / "analysis_ready" / "sipp_2018_2024_person_month_panel.parquet"
RAW = ROOT / "temp" / "raw_downloads" / "census_sipp"
SCRATCH = ROOT / "temp" / "scratch" / "ira_insulin_health_need_2020_2023.parquet"
OUT = ROOT / "result" / "idea_scan"
REPORT = ROOT / "report" / "69_ira_insulin_medicare_fast_test.md"


SOURCES = [
    "CMS IRA implementation fact sheet: https://www.cms.gov/newsroom/fact-sheets/anniversary-inflation-reduction-act-update-cms-implementation",
    "KFF Medicare Part D IRA changes: https://www.kff.org/medicare/changes-to-medicare-part-d-in-2024-and-2025-under-the-inflation-reduction-act-and-how-enrollees-will-benefit/",
    "KFF $35 insulin cap explainer: https://www.kff.org/medicare/the-facts-about-the-35-insulin-copay-cap-in-medicare/",
    "Johns Hopkins summary of 2026 JAMA claims study: https://publichealth.jhu.edu/2026/medicare-patients-out-of-pocket-costs-for-insulin-decrease-under-mandated-caps",
]


RAW_COLS = [
    "SSUID",
    "PNUM",
    "MONTHCODE",
    "EPRESDRG",
    "EDALYDRG",
    "RCONDBRIDGE1",
    "RCONDBRIDGE2",
    "RCONDBRIDGE3",
    "RCONDTYP1",
    "RCONDTYP2",
    "RCONDTYP3",
    "EHLTHCOND",
    "EDEBT_MED",
    "TMED_AMT",
    "TOTCMDPAY",
]


def yes(s: pd.Series) -> pd.Series:
    return pd.to_numeric(s, errors="coerce").eq(1)


def clean_weight(df: pd.DataFrame) -> pd.Series:
    w = pd.to_numeric(df.get("WPFINWGT"), errors="coerce")
    return w.where(w.gt(0))


def bounded_numeric(s: pd.Series, lo: float, hi: float) -> pd.Series:
    out = pd.to_numeric(s, errors="coerce")
    return out.where(out.between(lo, hi, inclusive="both"))


def wmean(y: pd.Series, w: pd.Series) -> float:
    mask = y.notna() & w.notna() & w.gt(0)
    if not mask.any():
        return np.nan
    return float(np.average(y[mask].astype(float), weights=w[mask].astype(float)))


def persons(s: pd.Series) -> int:
    return int(s.dropna().nunique())


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
    k = x.shape[1]
    if len(y) <= k + 10:
        return np.full(k, np.nan), np.full(k, np.nan), np.full(k, np.nan), int(len(y)), 0

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


def read_raw_header(file_year: int) -> list[str]:
    zpath = RAW / str(file_year) / "primary" / f"pu{file_year}_csv.zip"
    with zipfile.ZipFile(zpath) as zf:
        with zf.open(f"pu{file_year}.csv") as fh:
            return fh.readline().decode("utf-8", errors="replace").strip().split("|")


def extract_health_need() -> pd.DataFrame:
    if SCRATCH.exists():
        return pd.read_parquet(SCRATCH)

    frames = []
    for file_year in [2021, 2022, 2023, 2024]:
        zpath = RAW / str(file_year) / "primary" / f"pu{file_year}_csv.zip"
        header = set(read_raw_header(file_year))
        usecols = [c for c in RAW_COLS if c in header]
        chunks = pd.read_csv(
            zpath,
            sep="|",
            usecols=usecols,
            compression="zip",
            chunksize=75_000,
            low_memory=True,
        )
        processed = []
        for df in chunks:
            df["reference_year"] = file_year - 1
            df["SSUID"] = df["SSUID"].astype("string")
            df["PNUM"] = pd.to_numeric(df["PNUM"], errors="coerce").astype("Int64")
            out = pd.DataFrame(index=df.index)
            out["person_id"] = df["SSUID"].astype(str) + "-" + df["PNUM"].astype(str)
            out["reference_year"] = df["reference_year"]
            out["rx_any"] = yes(df.get("EPRESDRG", pd.Series(index=df.index, dtype="float"))).astype(float)
            out["daily_rx"] = yes(df.get("EDALYDRG", pd.Series(index=df.index, dtype="float"))).astype(float)

            bridge_cols = [c for c in ["RCONDBRIDGE1", "RCONDBRIDGE2", "RCONDBRIDGE3"] if c in df.columns]
            cond_bridge = pd.DataFrame({c: pd.to_numeric(df[c], errors="coerce") for c in bridge_cols})
            out["diabetes_bridge"] = cond_bridge.eq(10).any(axis=1).astype(float) if bridge_cols else 0.0

            type_cols = [c for c in ["RCONDTYP1", "RCONDTYP2", "RCONDTYP3"] if c in df.columns]
            cond_type = pd.DataFrame({c: pd.to_numeric(df[c], errors="coerce") for c in type_cols})
            # Type 7 is endocrine disorders in the improved condition-type recode.
            out["endocrine_condition"] = cond_type.eq(7).any(axis=1).astype(float) if type_cols else 0.0

            out["limiting_health_condition"] = yes(
                df.get("EHLTHCOND", pd.Series(index=df.index, dtype="float"))
            ).astype(float)
            out["medical_debt"] = yes(df.get("EDEBT_MED", pd.Series(index=df.index, dtype="float"))).astype(float)
            out["medical_debt_amount"] = bounded_numeric(
                df.get("TMED_AMT", pd.Series(index=df.index, dtype="float")), 0, 1_000_000
            )
            out["otc_oop_amount"] = bounded_numeric(
                df.get("TOTCMDPAY", pd.Series(index=df.index, dtype="float")), 0, 99_000
            )
            processed.append(out)
        df = pd.concat(processed, ignore_index=True)
        annual = (
            df
            .groupby(["person_id", "reference_year"], observed=True)
            .agg(
                rx_any=("rx_any", "max"),
                daily_rx=("daily_rx", "max"),
                diabetes_bridge=("diabetes_bridge", "max"),
                endocrine_condition=("endocrine_condition", "max"),
                limiting_health_condition=("limiting_health_condition", "max"),
                medical_debt=("medical_debt", "max"),
                medical_debt_amount=("medical_debt_amount", "max"),
                otc_oop_amount=("otc_oop_amount", "mean"),
            )
            .reset_index()
        )
        frames.append(annual)

    out = pd.concat(frames, ignore_index=True)
    SCRATCH.parent.mkdir(parents=True, exist_ok=True)
    out.to_parquet(SCRATCH, index=False)
    return out


def build_person_year() -> pd.DataFrame:
    cols = [
        "person_id",
        "person_month_key",
        "reference_year",
        "state_fips",
        "TAGE",
        "TAGE_EHC",
        "ESEX",
        "ERACE",
        "EORIGIN",
        "EHISPAN",
        "RDIS",
        "TFINCPOV",
        "WPFINWGT",
        "TSSSAMT",
        "RHLTHMTH",
        "RPRIMTH",
        "RPUBMTH",
        "ECRMTH",
        "RPUBTYPE1",
        "EMDMTH",
        "RPUBTYPE2",
        "TMDPAY",
        "TVISDOC",
        "TVISDENT",
        "THOSPNIT",
    ]
    df = pd.read_parquet(PANEL, columns=cols)
    df = df[df["reference_year"].between(2020, 2023)].copy()
    df["state_fips"] = df["state_fips"].astype(str).str.zfill(2)
    df["age"] = bounded_numeric(df["TAGE_EHC"], 0, 100)
    df["age"] = df["age"].where(df["age"].notna(), bounded_numeric(df["TAGE"], 0, 100))
    df["fpl"] = bounded_numeric(df["TFINCPOV"], 0, 20)
    df["female"] = pd.to_numeric(df["ESEX"], errors="coerce").eq(2).astype(float)
    df["black"] = pd.to_numeric(df["ERACE"], errors="coerce").eq(2).astype(float)
    df["hispanic"] = (
        pd.to_numeric(df["EORIGIN"], errors="coerce").eq(1)
        | pd.to_numeric(df["EHISPAN"], errors="coerce").eq(1)
    ).astype(float)
    df["disabled"] = yes(df["RDIS"]).astype(float)
    df["weight"] = clean_weight(df)
    df["medicare"] = (yes(df["ECRMTH"]) | yes(df["RPUBTYPE1"])).astype(float)
    df["medicaid"] = (yes(df["EMDMTH"]) | yes(df["RPUBTYPE2"])).astype(float)
    df["public"] = yes(df["RPUBMTH"]).astype(float)
    df["private"] = yes(df["RPRIMTH"]).astype(float)
    df["any_coverage"] = yes(df["RHLTHMTH"]).astype(float)
    df["uninsured"] = pd.to_numeric(df["RHLTHMTH"], errors="coerce").eq(2).astype(float)
    df["oop_amount"] = bounded_numeric(df["TMDPAY"], 0, 200_000)
    df["log_oop"] = np.log1p(df["oop_amount"])
    df["oop_any"] = df["oop_amount"].gt(0).astype(float)
    df["oop_gt_500"] = df["oop_amount"].gt(500).astype(float)
    df["oop_gt_1000"] = df["oop_amount"].gt(1000).astype(float)
    df["oop_gt_2000"] = df["oop_amount"].gt(2000).astype(float)
    df["doctor_any"] = bounded_numeric(df["TVISDOC"], 0, 200).gt(0).astype(float)
    df["dental_any"] = bounded_numeric(df["TVISDENT"], 0, 100).gt(0).astype(float)
    df["hospital_any"] = bounded_numeric(df["THOSPNIT"], 0, 365).gt(0).astype(float)

    py = (
        df.groupby(["person_id", "state_fips", "reference_year"], observed=True)
        .agg(
            months=("person_month_key", "size"),
            weight=("weight", "mean"),
            age=("age", "mean"),
            fpl=("fpl", "median"),
            female=("female", "mean"),
            black=("black", "mean"),
            hispanic=("hispanic", "mean"),
            disabled=("disabled", "mean"),
            medicare=("medicare", "mean"),
            medicaid=("medicaid", "mean"),
            public=("public", "mean"),
            private=("private", "mean"),
            any_coverage=("any_coverage", "mean"),
            uninsured=("uninsured", "mean"),
            oop_amount=("oop_amount", "mean"),
            log_oop=("log_oop", "mean"),
            oop_any=("oop_any", "mean"),
            oop_gt_500=("oop_gt_500", "mean"),
            oop_gt_1000=("oop_gt_1000", "mean"),
            oop_gt_2000=("oop_gt_2000", "mean"),
            doctor_any=("doctor_any", "mean"),
            dental_any=("dental_any", "mean"),
            hospital_any=("hospital_any", "mean"),
        )
        .reset_index()
    )
    py = py[py["months"].ge(6)].copy()
    health = extract_health_need()
    py = py.merge(health, on=["person_id", "reference_year"], how="left")
    for col in [
        "rx_any",
        "daily_rx",
        "diabetes_bridge",
        "endocrine_condition",
        "limiting_health_condition",
        "medical_debt",
    ]:
        py[col] = py[col].fillna(0).astype(float)
    py["medical_debt_amount"] = py["medical_debt_amount"].fillna(0)
    py["otc_oop_amount"] = py["otc_oop_amount"].fillna(0)
    py["medicare_binary"] = py["medicare"].ge(0.5).astype(float)
    py["post_2023"] = py["reference_year"].eq(2023).astype(float)
    py["age2"] = py["age"] ** 2
    py["diabetes_or_daily_rx"] = py[["diabetes_bridge", "daily_rx"]].max(axis=1)
    return py


def design_matrix(df: pd.DataFrame, high_col: str) -> tuple[np.ndarray, list[str]]:
    medicare = df["medicare_binary"].astype(float)
    high = df[high_col].astype(float)
    post = df["post_2023"].astype(float)
    cols = {
        "triple_medicare_high_post": medicare * high * post,
        "medicare_x_high": medicare * high,
        "medicare_x_post": medicare * post,
        "high_x_post": high * post,
        "medicare": medicare,
        "high_need": high,
        "age": df["age"].astype(float),
        "age2": df["age2"].astype(float),
        "fpl": df["fpl"].astype(float),
        "female": df["female"].astype(float),
        "black": df["black"].astype(float),
        "hispanic": df["hispanic"].astype(float),
        "disabled": df["disabled"].astype(float),
    }
    x = pd.DataFrame(cols, index=df.index)
    year_dummies = pd.get_dummies(df["reference_year"].astype(int), prefix="year", drop_first=True, dtype=float)
    x = pd.concat([pd.Series(1.0, index=df.index, name="intercept"), x, year_dummies], axis=1)
    return x.to_numpy(float), x.columns.tolist()


def run_model(df: pd.DataFrame, high_col: str, outcome: str) -> dict[str, float | int | str]:
    sample = df[
        df["age"].between(50, 90, inclusive="both")
        & df["fpl"].between(0, 10, inclusive="both")
        & df["weight"].gt(0)
    ].copy()
    y = sample[outcome].astype(float).to_numpy()
    x, names = design_matrix(sample, high_col)
    beta, se_hc1, se_cluster, n, g = weighted_ols_cluster(
        y,
        x,
        sample["weight"].astype(float).to_numpy(),
        sample["person_id"].astype(str).to_numpy(),
    )
    idx = names.index("triple_medicare_high_post")
    return {
        "high_need": high_col,
        "outcome": outcome,
        "coef": float(beta[idx]),
        "se_hc1": float(se_hc1[idx]),
        "t_hc1": float(beta[idx] / se_hc1[idx]) if se_hc1[idx] > 0 else np.nan,
        "se_person_cluster": float(se_cluster[idx]),
        "t_person_cluster": float(beta[idx] / se_cluster[idx]) if se_cluster[idx] > 0 else np.nan,
        "n": n,
        "clusters_person": g,
    }


def support_tables(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    sample = df[df["age"].between(50, 90, inclusive="both") & df["fpl"].between(0, 10, inclusive="both")].copy()
    support_rows = []
    for high_col in ["diabetes_bridge", "daily_rx", "diabetes_or_daily_rx"]:
        for post, label in [(0.0, "pre_2020_2022"), (1.0, "post_2023")]:
            for medicare in [0.0, 1.0]:
                cell = sample[
                    sample["post_2023"].eq(post)
                    & sample["medicare_binary"].eq(medicare)
                    & sample[high_col].eq(1)
                ]
                support_rows.append(
                    {
                        "high_need": high_col,
                        "period": label,
                        "medicare": int(medicare),
                        "rows": int(len(cell)),
                        "persons": persons(cell["person_id"]),
                        "weighted_share_med_debt": wmean(cell["medical_debt"], cell["weight"]) if len(cell) else np.nan,
                        "weighted_oop_amount": wmean(cell["oop_amount"], cell["weight"]) if len(cell) else np.nan,
                    }
                )
    support = pd.DataFrame(support_rows)

    raw_rows = []
    outcomes = [
        "oop_amount",
        "log_oop",
        "oop_gt_500",
        "oop_gt_1000",
        "oop_gt_2000",
        "medical_debt",
        "doctor_any",
        "hospital_any",
    ]
    for high_col in ["diabetes_bridge", "daily_rx", "diabetes_or_daily_rx"]:
        tmp = sample[sample[high_col].eq(1)].copy()
        for keys, g in tmp.groupby(["medicare_binary", "post_2023"], observed=True):
            row = {
                "high_need": high_col,
                "medicare": int(keys[0]),
                "post_2023": int(keys[1]),
                "rows": int(len(g)),
                "persons": persons(g["person_id"]),
            }
            for out in outcomes:
                row[out] = wmean(g[out], g["weight"])
            raw_rows.append(row)
    raw = pd.DataFrame(raw_rows)
    return support, raw


def write_report(py: pd.DataFrame, estimates: pd.DataFrame, support: pd.DataFrame, raw: pd.DataFrame) -> None:
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    support.to_csv(OUT / "ira_insulin_medicare_support.csv", index=False)
    raw.to_csv(OUT / "ira_insulin_medicare_raw_cells.csv", index=False)
    estimates.to_csv(OUT / "ira_insulin_medicare_estimates.csv", index=False)

    sample = py[py["age"].between(50, 90, inclusive="both") & py["fpl"].between(0, 10, inclusive="both")]
    post_treated_diab = support[
        support["high_need"].eq("diabetes_bridge")
        & support["period"].eq("post_2023")
        & support["medicare"].eq(1)
    ]
    post_treated_daily = support[
        support["high_need"].eq("daily_rx")
        & support["period"].eq("post_2023")
        & support["medicare"].eq(1)
    ]

    def fmt_est(high: str, outcome: str) -> str:
        r = estimates[(estimates["high_need"].eq(high)) & (estimates["outcome"].eq(outcome))]
        if r.empty:
            return "NA"
        row = r.iloc[0]
        return f"{row['coef']:.4f} (person-cluster t={row['t_person_cluster']:.2f})"

    lines = [
        "# IRA Medicare Insulin Cap SIPP Fast Test",
        "",
        "## Question",
        "",
        "Can SIPP support a quasi-experimental paper on the 2023 Inflation Reduction Act $35 Medicare insulin cap, using Medicare beneficiaries with diabetes or daily prescription-drug use as the exposed group?",
        "",
        "## Source Checks",
        "",
    ]
    lines += [f"- {s}" for s in SOURCES]
    lines += [
        "",
        "Key policy timing: the Part D insulin cap began January 1, 2023; the Part B insulin cap began July 1, 2023. Current public SIPP reaches reference year 2023 through the 2024 SIPP file, so this is a one-post-year screen.",
        "",
        "## Data Construction",
        "",
        "- Main panel: `data/analysis_ready/sipp_2018_2024_person_month_panel.parquet`.",
        "- Added raw health-need variables from 2021-2024 SIPP raw zip files, corresponding to reference years 2020-2023.",
        "- Added scratch file: `temp/scratch/ira_insulin_health_need_2020_2023.parquet`.",
        "- Diabetes proxy: any `RCONDBRIDGE1-3 == 10`.",
        "- Broader drug-need proxy: daily prescription medication, `EDALYDRG == 1`.",
        "- Outcomes: broad non-premium medical OOP (`TMDPAY`), high-OOP indicators, medical debt (`EDEBT_MED`), utilization checks.",
        "",
        "Important limitation: SIPP does not identify insulin use or prescription-drug-specific OOP spending in this compact analysis. The screen therefore tests diluted proxies, not the literal insulin transaction margin.",
        "",
        "## Support",
        "",
        f"- Age 50-90, FPL <= 1000% sample: {len(sample):,} person-years; {sample['person_id'].nunique():,} persons.",
    ]
    if not post_treated_diab.empty:
        r = post_treated_diab.iloc[0]
        lines.append(f"- Post-2023 Medicare + diabetes-proxy cell: {int(r['rows']):,} person-years; {int(r['persons']):,} persons.")
    if not post_treated_daily.empty:
        r = post_treated_daily.iloc[0]
        lines.append(f"- Post-2023 Medicare + daily-prescription cell: {int(r['rows']):,} person-years; {int(r['persons']):,} persons.")
    lines += [
        "",
        "## DDD Screen",
        "",
        "Specification: weighted OLS on person-year data, age 50-90, years 2020-2023. Key coefficient is `Medicare x high-need x 2023`, with all lower-order interactions, year fixed effects, age/age-squared, FPL, sex, race/ethnicity, and disability controls. Standard errors are person-clustered.",
        "",
        "Diabetes-proxy high need:",
        "",
        f"- OOP amount: {fmt_est('diabetes_bridge', 'oop_amount')}.",
        f"- log OOP: {fmt_est('diabetes_bridge', 'log_oop')}.",
        f"- OOP > $1,000: {fmt_est('diabetes_bridge', 'oop_gt_1000')}.",
        f"- Medical debt: {fmt_est('diabetes_bridge', 'medical_debt')}.",
        f"- Doctor any: {fmt_est('diabetes_bridge', 'doctor_any')}.",
        "",
        "Daily-prescription high need:",
        "",
        f"- OOP amount: {fmt_est('daily_rx', 'oop_amount')}.",
        f"- log OOP: {fmt_est('daily_rx', 'log_oop')}.",
        f"- OOP > $1,000: {fmt_est('daily_rx', 'oop_gt_1000')}.",
        f"- Medical debt: {fmt_est('daily_rx', 'medical_debt')}.",
        f"- Doctor any: {fmt_est('daily_rx', 'doctor_any')}.",
        "",
        "## Decision",
        "",
        "`IRA MEDICARE INSULIN CAP: POLICY-HOT BUT SIPP-NO-GO AS A MAIN CAUSAL PAPER`.",
        "",
        "Why:",
        "",
        "1. The policy is excellent and current, but the SIPP measurement is too indirect: no insulin-user flag, no Part D plan detail, and no prescription-drug-specific OOP outcome.",
        "2. Only one post-policy SIPP reference year is currently available.",
        "3. A 2026 JAMA claims-based study already analyzes insulin OOP directly with nearly 3.8 million insulin users, so the strongest contribution has moved to claims data rather than SIPP.",
        "4. SIPP can still be useful as a descriptive supplement for household financial spillovers, but not as the lead causal design.",
        "",
        "## Artifacts",
        "",
        "- `script/11_idea_scan/34_ira_insulin_medicare_fast_test.py`",
        "- `report/69_ira_insulin_medicare_fast_test.md`",
        "- `result/idea_scan/ira_insulin_medicare_estimates.csv`",
        "- `result/idea_scan/ira_insulin_medicare_support.csv`",
        "- `result/idea_scan/ira_insulin_medicare_raw_cells.csv`",
    ]
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    py = build_person_year()
    outcomes = [
        "oop_amount",
        "log_oop",
        "oop_gt_500",
        "oop_gt_1000",
        "oop_gt_2000",
        "medical_debt",
        "doctor_any",
        "dental_any",
        "hospital_any",
    ]
    rows = []
    for high_col in ["diabetes_bridge", "daily_rx", "diabetes_or_daily_rx"]:
        for outcome in outcomes:
            rows.append(run_model(py, high_col, outcome))
    estimates = pd.DataFrame(rows)
    support, raw = support_tables(py)
    write_report(py, estimates, support, raw)
    print(f"Wrote {REPORT}")
    print(f"Wrote {OUT / 'ira_insulin_medicare_estimates.csv'}")


if __name__ == "__main__":
    main()
