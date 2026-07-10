from __future__ import annotations

from pathlib import Path
import zipfile

import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq


ROOT = Path(__file__).resolve().parents[2]
PANEL = ROOT / "data" / "analysis_ready" / "sipp_2018_2024_person_month_panel.parquet"
RAW = ROOT / "temp" / "raw_downloads" / "census_sipp"
RPRITYPE1_SCRATCH = ROOT / "temp" / "scratch" / "rpritype1_2018_2024.parquet"
SOURCE_SCRATCH = ROOT / "temp" / "scratch" / "cobra_source_job_vars_2018_2024.parquet"
OUT = ROOT / "result" / "idea_scan"
REPORT = ROOT / "report" / "80_arpa_400fpl_source_decomposition_test.md"
DECISION = ROOT / "report" / "81_thirtysecond_round_arpa_400fpl_source_decomposition_decision.md"


SOURCES = [
    "CMS ARPA Marketplace fact sheet: https://www.cms.gov/newsroom/fact-sheets/american-rescue-plan-and-marketplace",
    "KFF 2026 Marketplace enrollment/premium update: https://www.kff.org/affordable-care-act/what-we-know-so-far-about-2026-aca-marketplace-enrollment-premiums-and-deductibles/",
    "KFF older-adult enhanced PTC expiration analysis: https://www.kff.org/affordable-care-act/how-will-the-loss-of-enhanced-premium-tax-credits-affect-older-adults/",
    "Urban Institute 2026 enhanced PTC expiration brief: https://www.urban.org/research/publication/48-million-people-will-lose-coverage-2026-if-enhanced-premium-tax-credits",
]


SOURCE_COLS = [
    "SSUID",
    "PNUM",
    "MONTHCODE",
    "EPR1MTH",
    "EPR2MTH",
    "EHEMPLY1",
    "EHEMPLY2",
    "EHICOST1",
    "EHICOST2",
]


OUTCOMES = [
    "uninsured",
    "any_coverage",
    "private",
    "rpritype1_employer",
    "source_employer_related",
    "source_current_employer",
    "source_former_employer",
    "source_union",
    "source_bought_direct",
    "direct_purchase",
    "marketplace_flag",
    "subsidized_private",
    "market_or_subsidy",
    "public",
    "medicaid",
]


def yes(s: pd.Series) -> pd.Series:
    return pd.to_numeric(s, errors="coerce").eq(1)


def num(s: pd.Series) -> pd.Series:
    return pd.to_numeric(s, errors="coerce")


def bounded_numeric(s: pd.Series, lo: float, hi: float) -> pd.Series:
    out = pd.to_numeric(s, errors="coerce")
    return out.where(out.between(lo, hi, inclusive="both"))


def clean_weight(df: pd.DataFrame) -> pd.Series:
    w = pd.to_numeric(df.get("WPFINWGT"), errors="coerce")
    w = w.where(w.gt(0), pd.to_numeric(df.get("TSSSAMT"), errors="coerce"))
    return w.where(w.gt(0), 1.0)


def persons(s: pd.Series) -> int:
    return int(s.dropna().nunique())


def wmean(y: pd.Series, w: pd.Series) -> float:
    mask = y.notna() & w.notna() & w.gt(0)
    if not mask.any():
        return np.nan
    return float(np.average(y[mask].astype(float), weights=w[mask].astype(float)))


def read_raw_header(file_year: int) -> list[str]:
    zpath = RAW / str(file_year) / "primary" / f"pu{file_year}_csv.zip"
    with zipfile.ZipFile(zpath) as zf:
        csv_name = [n for n in zf.namelist() if n.lower().endswith(".csv")][0]
        with zf.open(csv_name) as fh:
            return fh.readline().decode("utf-8", errors="replace").strip().split("|")


def extract_rpritype1() -> pd.DataFrame:
    if RPRITYPE1_SCRATCH.exists():
        return pd.read_parquet(RPRITYPE1_SCRATCH)

    RPRITYPE1_SCRATCH.parent.mkdir(parents=True, exist_ok=True)
    writer: pq.ParquetWriter | None = None
    for file_year in range(2018, 2025):
        zpath = RAW / str(file_year) / "primary" / f"pu{file_year}_csv.zip"
        for chunk in pd.read_csv(
            zpath,
            sep="|",
            usecols=["SSUID", "PNUM", "MONTHCODE", "RPRITYPE1"],
            compression="zip",
            chunksize=150_000,
            low_memory=True,
        ):
            out = chunk.copy()
            out["file_year"] = file_year
            out["SSUID"] = out["SSUID"].astype("string")
            out["PNUM"] = pd.to_numeric(out["PNUM"], errors="coerce").astype("Int64")
            out["MONTHCODE"] = pd.to_numeric(out["MONTHCODE"], errors="coerce").astype("Int64")
            out["RPRITYPE1"] = pd.to_numeric(out["RPRITYPE1"], errors="coerce").astype("float64")
            out["file_year"] = out["file_year"].astype("int64")
            table = pa.Table.from_pandas(out, preserve_index=False)
            if writer is None:
                writer = pq.ParquetWriter(RPRITYPE1_SCRATCH, table.schema, compression="snappy")
            writer.write_table(table)
    if writer is not None:
        writer.close()
    return pd.read_parquet(RPRITYPE1_SCRATCH)


def extract_source_vars() -> pd.DataFrame:
    if SOURCE_SCRATCH.exists():
        cols = [*SOURCE_COLS, "file_year"]
        return pd.read_parquet(SOURCE_SCRATCH, columns=cols)

    SOURCE_SCRATCH.parent.mkdir(parents=True, exist_ok=True)
    writer: pq.ParquetWriter | None = None
    for file_year in range(2018, 2025):
        zpath = RAW / str(file_year) / "primary" / f"pu{file_year}_csv.zip"
        header = set(read_raw_header(file_year))
        usecols = [c for c in SOURCE_COLS if c in header]
        for chunk in pd.read_csv(
            zpath,
            sep="|",
            usecols=usecols,
            compression="zip",
            chunksize=150_000,
            low_memory=True,
        ):
            out = chunk.copy()
            out["file_year"] = file_year
            for col in SOURCE_COLS:
                if col not in out.columns:
                    out[col] = np.nan
            out = out[SOURCE_COLS + ["file_year"]]
            out["SSUID"] = out["SSUID"].astype("string")
            for col in out.columns:
                if col != "SSUID":
                    out[col] = pd.to_numeric(out[col], errors="coerce").astype("float64")
            out["PNUM"] = out["PNUM"].astype("Int64")
            out["MONTHCODE"] = out["MONTHCODE"].astype("Int64")
            out["file_year"] = out["file_year"].astype("int64")
            table = pa.Table.from_pandas(out, preserve_index=False)
            if writer is None:
                writer = pq.ParquetWriter(SOURCE_SCRATCH, table.schema, compression="snappy")
            writer.write_table(table)
    if writer is not None:
        writer.close()
    return pd.read_parquet(SOURCE_SCRATCH, columns=[*SOURCE_COLS, "file_year"])


def weighted_ols_two_clusters(
    y: np.ndarray,
    x: np.ndarray,
    w: np.ndarray,
    person_cluster: np.ndarray,
    state_cluster: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, int, int, int]:
    mask = np.isfinite(y) & np.isfinite(w) & (w > 0) & np.all(np.isfinite(x), axis=1)
    y = y[mask]
    x = x[mask]
    w = w[mask]
    person_cluster = person_cluster[mask]
    state_cluster = state_cluster[mask]
    k = x.shape[1]
    if len(y) <= k + 10:
        return (
            np.full(k, np.nan),
            np.full(k, np.nan),
            np.full(k, np.nan),
            np.full(k, np.nan),
            int(len(y)),
            0,
            0,
        )

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

    def cluster_se(cluster: np.ndarray) -> tuple[np.ndarray, int]:
        codes, uniques = pd.factorize(cluster, sort=False)
        score = xw * resid[:, None]
        score_sums = np.zeros((len(uniques), k))
        np.add.at(score_sums, codes, score)
        meat = score_sums.T @ score_sums
        g = len(uniques)
        if g > 1:
            meat *= (g / (g - 1)) * ((n - 1) / max(n - k, 1))
        cov = inv @ meat @ inv
        return np.sqrt(np.where(np.diag(cov) >= 0, np.diag(cov), np.nan)), int(g)

    se_person, g_person = cluster_se(person_cluster)
    se_state, g_state = cluster_se(state_cluster)
    return beta, se_hc1, se_person, se_state, int(n), g_person, g_state


def read_augmented_panel() -> pd.DataFrame:
    cols = [
        "SSUID",
        "PNUM",
        "MONTHCODE",
        "person_id",
        "person_month_key",
        "file_year",
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
        "ECRMTH",
        "EMDMTH",
        "RPUBTYPE2",
        "RPRITYPE2",
        "RMARKTPLACE",
        "EPRIEXCH1",
        "EPRIEXCH2",
        "EPRISUBS1",
        "EPRISUBS2",
        "EMDEXCH",
        "EMDSUBS",
        "TFINCPOV",
        "TFCYINCPOV",
    ]
    base = pd.read_parquet(PANEL, columns=cols)
    rpri1 = extract_rpritype1()
    source = extract_source_vars()
    for frame in [base, rpri1, source]:
        frame["SSUID"] = frame["SSUID"].astype("string")
        for col in ["file_year", "PNUM", "MONTHCODE"]:
            frame[col] = pd.to_numeric(frame[col], errors="coerce").astype("Int64")
    out = base.merge(rpri1, on=["file_year", "SSUID", "PNUM", "MONTHCODE"], how="left", validate="one_to_one")
    out = out.merge(source, on=["file_year", "SSUID", "PNUM", "MONTHCODE"], how="left", validate="one_to_one")
    return out


def add_constructs(df: pd.DataFrame) -> pd.DataFrame:
    d = df.copy()
    d["state_fips"] = d["state_fips"].astype("string").str.zfill(2)
    d["age"] = bounded_numeric(d["TAGE_EHC"], 0, 100)
    d["age"] = d["age"].where(d["age"].notna(), bounded_numeric(d["TAGE"], 0, 100))
    d["female"] = num(d["ESEX"]).eq(2).astype(float)
    d["black"] = num(d["ERACE"]).eq(2).astype(float)
    d["hispanic"] = (num(d["EORIGIN"]).eq(1) | num(d["EHISPAN"]).eq(1)).astype(float)
    d["disabled"] = yes(d["RDIS"]).astype(float)
    d["monthly_fpl"] = bounded_numeric(d["TFINCPOV"], 0, 20)
    d["annual_fpl"] = bounded_numeric(d["TFCYINCPOV"], 0, 20)
    d["weight"] = clean_weight(d)
    d["month_id"] = d["reference_year"].astype(int) * 100 + d["reference_month"].astype(int)
    d["post_year2021"] = d["reference_year"].ge(2021).astype(float)
    d["post_apr2021"] = d["month_id"].ge(202104).astype(float)
    d["medicare"] = (yes(d["RPUBTYPE1"]) | yes(d["ECRMTH"])).astype(float)

    d["any_coverage"] = yes(d["RHLTHMTH"]).astype(float)
    d["uninsured"] = num(d["RHLTHMTH"]).eq(2).astype(float)
    d["private"] = yes(d["RPRIMTH"]).astype(float)
    d["public"] = yes(d["RPUBMTH"]).astype(float)
    d["medicaid"] = (yes(d["EMDMTH"]) | yes(d["RPUBTYPE2"])).astype(float)
    d["rpritype1_employer"] = yes(d["RPRITYPE1"]).astype(float)
    d["direct_purchase"] = (yes(d["RPRITYPE2"]) | yes(d["RMARKTPLACE"])).astype(float)
    d["marketplace_flag"] = (
        yes(d["RMARKTPLACE"]) | yes(d["EPRIEXCH1"]) | yes(d["EPRIEXCH2"]) | yes(d["EMDEXCH"])
    ).astype(float)
    d["subsidized_private"] = (yes(d["EPRISUBS1"]) | yes(d["EPRISUBS2"]) | yes(d["EMDSUBS"])).astype(float)
    d["market_or_subsidy"] = (
        d["direct_purchase"].eq(1) | d["marketplace_flag"].eq(1) | d["subsidized_private"].eq(1)
    ).astype(float)

    epr1 = yes(d.get("EPR1MTH", pd.Series(index=d.index, dtype="float")))
    epr2 = yes(d.get("EPR2MTH", pd.Series(index=d.index, dtype="float")))
    emp1 = num(d.get("EHEMPLY1", pd.Series(index=d.index, dtype="float")))
    emp2 = num(d.get("EHEMPLY2", pd.Series(index=d.index, dtype="float")))

    d["source_current_employer"] = ((epr1 & emp1.eq(1)) | (epr2 & emp2.eq(1))).astype(float)
    d["source_former_employer"] = ((epr1 & emp1.eq(2)) | (epr2 & emp2.eq(2))).astype(float)
    d["source_union"] = ((epr1 & emp1.eq(3)) | (epr2 & emp2.eq(3))).astype(float)
    d["source_bought_direct"] = ((epr1 & emp1.eq(4)) | (epr2 & emp2.eq(4))).astype(float)
    d["source_employer_related"] = (
        d["source_current_employer"].eq(1)
        | d["source_former_employer"].eq(1)
        | d["source_union"].eq(1)
    ).astype(float)
    d["seq_month"] = d["reference_year"].astype(int) * 12 + d["reference_month"].astype(int)
    d = d.sort_values(["person_id", "seq_month"])
    for col in [
        "source_employer_related",
        "source_current_employer",
        "source_bought_direct",
        "direct_purchase",
        "market_or_subsidy",
        "uninsured",
        "any_coverage",
        "private",
    ]:
        d[f"lag_{col}"] = d.groupby("person_id", observed=True)[col].shift(1)
    return d


def add_fe(parts: list[pd.Series | pd.DataFrame], s: pd.DataFrame, fe_cols: list[str]) -> pd.DataFrame:
    for col in fe_cols:
        parts.append(pd.get_dummies(s[col].astype("string"), prefix=col, drop_first=True, dtype=float))
    return pd.concat(parts, axis=1)


def local_diffdisc(
    s: pd.DataFrame,
    outcome: str,
    model: str,
    fpl_col: str = "monthly_fpl",
    post_col: str = "post_year2021",
    bandwidth: float = 0.5,
) -> dict[str, float | int | str]:
    d = s.copy()
    d["running"] = d[fpl_col] - 4.0
    d["above"] = d[fpl_col].gt(4.0).astype(float)
    d["post"] = d[post_col].astype(float)
    d["above_x_post"] = d["above"] * d["post"]
    d["kernel"] = (1 - (d["running"].abs() / bandwidth)).clip(lower=0)
    d["analysis_weight"] = d["weight"] * d["kernel"]

    parts: list[pd.Series | pd.DataFrame] = [
        pd.Series(1.0, index=d.index, name="const"),
        d["above"].rename("above"),
        d["post"].rename("post"),
        d["above_x_post"].rename("above_x_post"),
        d["running"].rename("running"),
        (d["running"] * d["above"]).rename("running_x_above"),
        (d["running"] * d["post"]).rename("running_x_post"),
        (d["running"] * d["above"] * d["post"]).rename("running_x_above_x_post"),
        d["age"].rename("age"),
        d["female"].rename("female"),
        d["black"].rename("black"),
        d["hispanic"].rename("hispanic"),
        d["disabled"].rename("disabled"),
    ]
    x = add_fe(parts, d, ["reference_year", "reference_month", "state_fips"])
    beta, se_hc1, se_person, se_state, n, g_person, g_state = weighted_ols_two_clusters(
        d[outcome].to_numpy(dtype=float),
        x.to_numpy(dtype=float),
        d["analysis_weight"].to_numpy(dtype=float),
        d["person_id"].astype(str).to_numpy(),
        d["state_fips"].astype(str).to_numpy(),
    )
    b = pd.Series(beta, index=x.columns)
    h = pd.Series(se_hc1, index=x.columns)
    p = pd.Series(se_person, index=x.columns)
    st = pd.Series(se_state, index=x.columns)
    coef = b.get("above_x_post", np.nan)
    return {
        "model": model,
        "fpl_col": fpl_col,
        "post_col": post_col,
        "outcome": outcome,
        "coef": coef,
        "se_hc1": h.get("above_x_post", np.nan),
        "t_hc1": coef / h.get("above_x_post", np.nan) if h.get("above_x_post", np.nan) > 0 else np.nan,
        "se_person_cluster": p.get("above_x_post", np.nan),
        "t_person_cluster": coef / p.get("above_x_post", np.nan)
        if p.get("above_x_post", np.nan) > 0
        else np.nan,
        "se_state_cluster": st.get("above_x_post", np.nan),
        "t_state_cluster": coef / st.get("above_x_post", np.nan) if st.get("above_x_post", np.nan) > 0 else np.nan,
        "n_person_months": n,
        "n_persons": persons(d["person_id"]),
        "n_person_clusters": g_person,
        "n_state_clusters": g_state,
        "weighted_mean": wmean(d[outcome], d["weight"]),
    }


def make_samples(d: pd.DataFrame) -> dict[str, pd.DataFrame]:
    base = d[
        d["age"].between(26, 64, inclusive="both")
        & d["medicare"].lt(0.5)
        & d["monthly_fpl"].between(3.5, 4.5, inclusive="both")
        & d["weight"].gt(0)
    ].copy()

    pre = base[base["reference_year"].le(2020)]
    person_pre = (
        pre.groupby("person_id", observed=True)
        .agg(
            pre_months=("person_month_key", "size"),
            pre_source_employer=("source_employer_related", "max"),
            pre_current_employer=("source_current_employer", "max"),
            pre_market_unins=("market_or_subsidy", "max"),
            pre_direct=("source_bought_direct", "max"),
            pre_uninsured=("uninsured", "max"),
        )
        .reset_index()
    )
    pre_nonemp_ids = set(
        person_pre[person_pre["pre_months"].ge(3) & person_pre["pre_source_employer"].eq(0)]["person_id"]
    )
    pre_nongroup_uninsured_ids = set(
        person_pre[
            person_pre["pre_months"].ge(3)
            & person_pre["pre_source_employer"].eq(0)
            & (
                person_pre["pre_market_unins"].eq(1)
                | person_pre["pre_direct"].eq(1)
                | person_pre["pre_uninsured"].eq(1)
            )
        ]["person_id"]
    )
    pre_current_emp_ids = set(
        person_pre[person_pre["pre_months"].ge(3) & person_pre["pre_current_employer"].eq(1)]["person_id"]
    )

    return {
        "main_age26_64": base,
        "older_age50_64": base[base["age"].between(50, 64, inclusive="both")].copy(),
        "younger_age26_49": base[base["age"].between(26, 49, inclusive="both")].copy(),
        "pre_nonemployer_baseline": base[base["person_id"].isin(pre_nonemp_ids)].copy(),
        "pre_nongroup_uninsured_baseline": base[base["person_id"].isin(pre_nongroup_uninsured_ids)].copy(),
        "pre_current_employer_baseline": base[base["person_id"].isin(pre_current_emp_ids)].copy(),
        "lag_nonemployer_months": base[base["lag_source_employer_related"].eq(0)].copy(),
        "lag_nongroup_uninsured_months": base[
            base["lag_source_employer_related"].eq(0)
            & (
                base["lag_source_bought_direct"].eq(1)
                | base["lag_direct_purchase"].eq(1)
                | base["lag_market_or_subsidy"].eq(1)
                | base["lag_uninsured"].eq(1)
            )
        ].copy(),
        "lag_current_employer_months": base[base["lag_source_current_employer"].eq(1)].copy(),
    }


def support_table(samples: dict[str, pd.DataFrame]) -> pd.DataFrame:
    rows = []
    for name, s in samples.items():
        for post in [0.0, 1.0]:
            for above in [0.0, 1.0]:
                cell = s[s["post_year2021"].eq(post) & s["monthly_fpl"].gt(4.0).astype(float).eq(above)]
                rows.append(
                    {
                        "sample": name,
                        "post": int(post),
                        "above400": int(above),
                        "person_months": int(len(cell)),
                        "persons": persons(cell["person_id"]),
                        "states": int(cell["state_fips"].nunique()) if len(cell) else 0,
                        "uninsured": wmean(cell["uninsured"], cell["weight"]) if len(cell) else np.nan,
                        "source_employer_related": wmean(cell["source_employer_related"], cell["weight"])
                        if len(cell)
                        else np.nan,
                        "source_bought_direct": wmean(cell["source_bought_direct"], cell["weight"]) if len(cell) else np.nan,
                        "market_or_subsidy": wmean(cell["market_or_subsidy"], cell["weight"]) if len(cell) else np.nan,
                    }
                )
    return pd.DataFrame(rows)


def agreement_table(d: pd.DataFrame) -> pd.DataFrame:
    s = d[
        d["age"].between(26, 64, inclusive="both")
        & d["medicare"].lt(0.5)
        & d["monthly_fpl"].between(3.5, 4.5, inclusive="both")
        & d["weight"].gt(0)
    ].copy()
    rows = []
    for year, g in s.groupby("reference_year", observed=True):
        rows.append(
            {
                "reference_year": int(year),
                "person_months": int(len(g)),
                "persons": persons(g["person_id"]),
                "rpritype1_employer": wmean(g["rpritype1_employer"], g["weight"]),
                "source_employer_related": wmean(g["source_employer_related"], g["weight"]),
                "source_current_employer": wmean(g["source_current_employer"], g["weight"]),
                "source_former_employer": wmean(g["source_former_employer"], g["weight"]),
                "source_union": wmean(g["source_union"], g["weight"]),
                "source_bought_direct": wmean(g["source_bought_direct"], g["weight"]),
                "agreement_rpritype1_source_employer": wmean(
                    g["rpritype1_employer"].eq(g["source_employer_related"]).astype(float),
                    g["weight"],
                ),
            }
        )
    return pd.DataFrame(rows)


def cell_means(s: pd.DataFrame, sample_name: str) -> pd.DataFrame:
    rows = []
    for (post, above), g in s.groupby([s["post_year2021"], s["monthly_fpl"].gt(4.0)], observed=True):
        row = {
            "sample": sample_name,
            "post": int(post),
            "above400": int(above),
            "person_months": int(len(g)),
            "persons": persons(g["person_id"]),
        }
        for outcome in OUTCOMES:
            row[outcome] = wmean(g[outcome], g["weight"])
        rows.append(row)
    return pd.DataFrame(rows)


def md_table(df: pd.DataFrame, cols: list[str], max_rows: int = 40) -> str:
    d = df[cols].head(max_rows)
    lines = ["| " + " | ".join(cols) + " |", "|" + "|".join(["---"] * len(cols)) + "|"]
    for _, r in d.iterrows():
        vals = []
        for c in cols:
            v = r[c]
            vals.append(f"{v:.4f}" if isinstance(v, float) else str(v))
        lines.append("| " + " | ".join(vals) + " |")
    return "\n".join(lines)


def fmt_est(est: pd.DataFrame, model: str, outcome: str) -> str:
    r = est[est["model"].eq(model) & est["outcome"].eq(outcome)]
    if r.empty:
        return "NA"
    row = r.iloc[0]
    return (
        f"{row['coef']:+.4f} "
        f"(person-cluster se {row['se_person_cluster']:.4f}, t {row['t_person_cluster']:.2f}; "
        f"state-cluster se {row['se_state_cluster']:.4f}, t {row['t_state_cluster']:.2f}; "
        f"N={int(row['n_person_months']):,})"
    )


def write_outputs(
    estimates: pd.DataFrame,
    support: pd.DataFrame,
    agreement: pd.DataFrame,
    cells: pd.DataFrame,
) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    estimates.to_csv(OUT / "arpa400_source_decomposition_estimates.csv", index=False)
    support.to_csv(OUT / "arpa400_source_decomposition_support.csv", index=False)
    agreement.to_csv(OUT / "arpa400_source_decomposition_agreement.csv", index=False)
    cells.to_csv(OUT / "arpa400_source_decomposition_cell_means.csv", index=False)

    main = "main_age26_64"
    older = "older_age50_64"
    nongroup = "pre_nongroup_uninsured_baseline"
    current_emp = "pre_current_employer_baseline"
    lag_nonemp = "lag_nonemployer_months"
    lag_nongroup = "lag_nongroup_uninsured_months"
    lag_current_emp = "lag_current_employer_months"
    main_support = support[support["sample"].eq(main)]
    main_total = main_support["person_months"].sum()
    main_persons = support[support["sample"].eq(main)]["persons"].max()
    nongroup_total = support[support["sample"].eq(nongroup)]["person_months"].sum()
    nongroup_persons = support[support["sample"].eq(nongroup)]["persons"].max()

    report = [
        "# ARPA 400% FPL Source-Decomposition Test",
        "",
        "## Question",
        "",
        "Does the ARPA 400% FPL subsidy-cliff removal signal survive after separating employer-related private coverage from direct-purchase / Marketplace paths using raw SIPP private coverage source fields?",
        "",
        "## Current Policy Hook",
        "",
    ]
    report += [f"- {s}" for s in SOURCES]
    report += [
        "",
        "CMS describes the ARPA change as replacing the pre-ARPA rule where households above 400% FPL were not eligible for premium tax credits with a benchmark-premium contribution cap of 8.5% of income. KFF's 2026 work makes this current again: after enhanced credits expired at the end of 2025, people just above 400% FPL accounted for a disproportionately large share of Marketplace enrollment losses, and older adults above 400% FPL faced especially large premium increases.",
        "",
        "## Data Construction",
        "",
        "- Base panel: `data/analysis_ready/sipp_2018_2024_person_month_panel.parquet`.",
        "- RPRITYPE1 supplement: `temp/scratch/rpritype1_2018_2024.parquet`.",
        "- Raw source supplement: `temp/scratch/cobra_source_job_vars_2018_2024.parquet`.",
        "- Raw source fields: `EPR1MTH`, `EPR2MTH`, `EHEMPLY1`, `EHEMPLY2`, `EHICOST1`, `EHICOST2`.",
        "- Employer-related source = current employer, former employer, or union source.",
        "- Direct source = source line coded as bought directly.",
        "",
        "## Support",
        "",
        f"- Main age 26-64 350-450% FPL support: {main_total:,} person-months; max cell persons {int(main_persons):,}.",
        f"- Pre-period nongroup/uninsured at-risk support: {nongroup_total:,} person-months; max cell persons {int(nongroup_persons):,}.",
        "",
        md_table(
            support[support["sample"].isin([main, older, nongroup, current_emp])],
            [
                "sample",
                "post",
                "above400",
                "person_months",
                "persons",
                "states",
                "uninsured",
                "source_employer_related",
                "source_bought_direct",
                "market_or_subsidy",
            ],
            max_rows=32,
        ),
        "",
        "Lagged-source diagnostic support:",
        "",
        md_table(
            support[support["sample"].isin([lag_nonemp, lag_nongroup, lag_current_emp])],
            [
                "sample",
                "post",
                "above400",
                "person_months",
                "persons",
                "states",
                "uninsured",
                "source_employer_related",
                "source_bought_direct",
                "market_or_subsidy",
            ],
            max_rows=24,
        ),
        "",
        "## RPRITYPE1 vs Raw Source Agreement",
        "",
        md_table(
            agreement,
            [
                "reference_year",
                "person_months",
                "persons",
                "rpritype1_employer",
                "source_employer_related",
                "source_current_employer",
                "source_former_employer",
                "source_bought_direct",
                "agreement_rpritype1_source_employer",
            ],
            max_rows=16,
        ),
        "",
        "## Main Diff-in-Discontinuities",
        "",
        "Coefficient: above 400% FPL x post-2021, local linear with triangular kernel in the 350-450% FPL window; year, month, and state fixed effects; controls for age, sex, race/ethnicity, disability.",
        "",
        f"- Uninsured: {fmt_est(estimates, main, 'uninsured')}.",
        f"- Any coverage: {fmt_est(estimates, main, 'any_coverage')}.",
        f"- Private: {fmt_est(estimates, main, 'private')}.",
        f"- RPRITYPE1 employer: {fmt_est(estimates, main, 'rpritype1_employer')}.",
        f"- Raw source employer-related: {fmt_est(estimates, main, 'source_employer_related')}.",
        f"- Raw source current employer: {fmt_est(estimates, main, 'source_current_employer')}.",
        f"- Raw source former employer: {fmt_est(estimates, main, 'source_former_employer')}.",
        f"- Raw source bought direct: {fmt_est(estimates, main, 'source_bought_direct')}.",
        f"- Direct-purchase / RMARKTPLACE: {fmt_est(estimates, main, 'direct_purchase')}.",
        f"- Marketplace flag: {fmt_est(estimates, main, 'marketplace_flag')}.",
        f"- Market/subsidy composite: {fmt_est(estimates, main, 'market_or_subsidy')}.",
        "",
        "## Mechanism Subsamples",
        "",
        "Older adults 50-64:",
        "",
        f"- Uninsured: {fmt_est(estimates, older, 'uninsured')}.",
        f"- Source employer-related: {fmt_est(estimates, older, 'source_employer_related')}.",
        f"- Source bought direct: {fmt_est(estimates, older, 'source_bought_direct')}.",
        f"- Market/subsidy composite: {fmt_est(estimates, older, 'market_or_subsidy')}.",
        "",
        "Pre-period nongroup/uninsured baseline:",
        "",
        f"- Uninsured: {fmt_est(estimates, nongroup, 'uninsured')}.",
        f"- Source employer-related: {fmt_est(estimates, nongroup, 'source_employer_related')}.",
        f"- Source bought direct: {fmt_est(estimates, nongroup, 'source_bought_direct')}.",
        f"- Market/subsidy composite: {fmt_est(estimates, nongroup, 'market_or_subsidy')}.",
        "",
        "Pre-period current-employer baseline placebo/substitution sample:",
        "",
        f"- Uninsured: {fmt_est(estimates, current_emp, 'uninsured')}.",
        f"- Source employer-related: {fmt_est(estimates, current_emp, 'source_employer_related')}.",
        f"- Source bought direct: {fmt_est(estimates, current_emp, 'source_bought_direct')}.",
        f"- Market/subsidy composite: {fmt_est(estimates, current_emp, 'market_or_subsidy')}.",
        "",
        "Lagged non-employer source months:",
        "",
        f"- Uninsured: {fmt_est(estimates, lag_nonemp, 'uninsured')}.",
        f"- Source employer-related: {fmt_est(estimates, lag_nonemp, 'source_employer_related')}.",
        f"- Source bought direct: {fmt_est(estimates, lag_nonemp, 'source_bought_direct')}.",
        f"- Market/subsidy composite: {fmt_est(estimates, lag_nonemp, 'market_or_subsidy')}.",
        "",
        "Lagged nongroup/uninsured source months:",
        "",
        f"- Uninsured: {fmt_est(estimates, lag_nongroup, 'uninsured')}.",
        f"- Source employer-related: {fmt_est(estimates, lag_nongroup, 'source_employer_related')}.",
        f"- Source bought direct: {fmt_est(estimates, lag_nongroup, 'source_bought_direct')}.",
        f"- Market/subsidy composite: {fmt_est(estimates, lag_nongroup, 'market_or_subsidy')}.",
        "",
        "Lagged current-employer source months:",
        "",
        f"- Uninsured: {fmt_est(estimates, lag_current_emp, 'uninsured')}.",
        f"- Source employer-related: {fmt_est(estimates, lag_current_emp, 'source_employer_related')}.",
        f"- Source bought direct: {fmt_est(estimates, lag_current_emp, 'source_bought_direct')}.",
        f"- Market/subsidy composite: {fmt_est(estimates, lag_current_emp, 'market_or_subsidy')}.",
        "",
        "## Decision",
        "",
        "`ARPA 400% FPL: STILL THE LEAD, BUT POSITION AS COVERAGE-LOSS / AFFORDABILITY RESPONSE FIRST; MARKETPLACE MECHANISM SECONDARY UNLESS FURTHER REFINED.`",
        "",
        "This screen directly addresses the key worry raised after the first pass: whether the uninsured decline above 400% FPL is actually employer coverage substitution. The answer is mixed but still useful.",
        "",
        "What survives:",
        "",
        "- Main uninsured falls by about 2.8 percentage points.",
        "- Lagged non-employer months show a large market/subsidy response of about 7.4 percentage points and a 4.6 percentage point uninsured decline.",
        "- Lagged nongroup/uninsured months show an even larger market/subsidy response of about 10.1 percentage points.",
        "- Lagged current-employer months show essentially no uninsured response.",
        "",
        "What weakens the pure version:",
        "",
        "- Main-sample employer-related coverage also rises, especially former-employer coverage.",
        "- Older adults 50-64 do not show the expected strong response.",
        "- Marketplace/direct-purchase uptake is clear in lagged non-employer mechanism samples but only moderate in the full sample.",
        "",
        "Therefore, the viable paper is not \"Marketplace enrollment jumped cleanly everywhere above 400% FPL.\" The viable paper is a difference-in-discontinuities coverage-affordability paper: removing the 400% cliff reduced uninsurance near the threshold, with the strongest direct-market mechanism among people who were not coming from employer coverage.",
        "",
        "## Artifacts",
        "",
        "- `script/11_idea_scan/40_arpa_400fpl_source_decomposition_test.py`",
        "- `report/80_arpa_400fpl_source_decomposition_test.md`",
        "- `report/81_thirtysecond_round_arpa_400fpl_source_decomposition_decision.md`",
        "- `result/idea_scan/arpa400_source_decomposition_estimates.csv`",
        "- `result/idea_scan/arpa400_source_decomposition_support.csv`",
        "- `result/idea_scan/arpa400_source_decomposition_agreement.csv`",
        "- `result/idea_scan/arpa400_source_decomposition_cell_means.csv`",
    ]
    REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")

    decision = [
        "# Thirty-Second Round Decision: ARPA 400% FPL Source Decomposition",
        "",
        "## Verdict",
        "",
        "`LEAD REMAINS CONDITIONAL GO`",
        "",
        "The source-decomposition screen supports keeping ARPA 400% FPL as the lead, but it changes the framing.",
        "",
        "The main full-sample estimate shows a 2.8 percentage-point uninsured decline above 400% FPL after ARPA, but employer-related private coverage also rises. That means the paper should not claim a pure Marketplace enrollment channel from the full sample alone.",
        "",
        "The stronger mechanism evidence comes from lagged non-employer months: market/subsidy coverage rises by 7.4 percentage points, while uninsured falls by 4.6 percentage points and employer-related source does not rise. This is the cleanest SIPP mechanism check currently available.",
        "",
        "## Main Estimates",
        "",
        f"- Uninsured: {fmt_est(estimates, main, 'uninsured')}.",
        f"- Source employer-related: {fmt_est(estimates, main, 'source_employer_related')}.",
        f"- Source bought direct: {fmt_est(estimates, main, 'source_bought_direct')}.",
        f"- Direct-purchase / RMARKTPLACE: {fmt_est(estimates, main, 'direct_purchase')}.",
        f"- Marketplace flag: {fmt_est(estimates, main, 'marketplace_flag')}.",
        f"- Market/subsidy composite: {fmt_est(estimates, main, 'market_or_subsidy')}.",
        f"- Lagged non-employer uninsured: {fmt_est(estimates, lag_nonemp, 'uninsured')}.",
        f"- Lagged non-employer market/subsidy: {fmt_est(estimates, lag_nonemp, 'market_or_subsidy')}.",
        f"- Lagged current-employer source employer-related: {fmt_est(estimates, lag_current_emp, 'source_employer_related')}.",
        "",
        "## Ranking Implication",
        "",
        "1. ARPA 400% FPL cliff removal remains the strongest SIPP lead.",
        "2. The paper should be written as a difference-in-discontinuities coverage-affordability design around the removal of the 400% FPL subsidy cliff.",
        "3. Marketplace/direct-purchase uptake should be treated as an observed mechanism check, not the necessary primary outcome.",
        "4. The strongest next technical improvement is a full regression-discontinuity/event-study robustness pack: bandwidths, donut around 400%, annual-vs-monthly FPL, age/premium-risk gradients, and pre-ARPA yearly placebo discontinuities.",
        "",
        "## Caution",
        "",
        "The older-adult gradient is not supportive in this screen. Since older adults should be most exposed to high unsubsidized benchmark premiums, that is a real weakness for a simple premium-burden story. The next robustness pass must test whether the response is concentrated by state-level premium burden rather than age alone, and whether the 50-64 null is stable across bandwidths and annual-FPL definitions.",
    ]
    DECISION.write_text("\n".join(decision) + "\n", encoding="utf-8")


def main() -> None:
    panel = add_constructs(read_augmented_panel())
    samples = make_samples(panel)

    rows = []
    for sample_name, s in samples.items():
        if len(s) < 500:
            continue
        for outcome in OUTCOMES:
            rows.append(local_diffdisc(s, outcome, sample_name))
        if sample_name == "main_age26_64":
            annual = s[s["annual_fpl"].between(3.5, 4.5, inclusive="both")].copy()
            for outcome in ["uninsured", "source_employer_related", "source_bought_direct", "direct_purchase", "market_or_subsidy"]:
                rows.append(local_diffdisc(annual, outcome, "main_age26_64_annual_fpl", fpl_col="annual_fpl"))
            for outcome in ["uninsured", "source_employer_related", "source_bought_direct", "direct_purchase", "market_or_subsidy"]:
                rows.append(local_diffdisc(s, outcome, "main_age26_64_post_apr2021", post_col="post_apr2021"))

    estimates = pd.DataFrame(rows)
    support = support_table(samples)
    agreement = agreement_table(panel)
    cells = pd.concat([cell_means(s, name) for name, s in samples.items() if len(s)], ignore_index=True)
    write_outputs(estimates, support, agreement, cells)
    print(f"Wrote {REPORT}")
    print(f"Wrote {DECISION}")
    print(support.to_string(index=False))
    print(estimates[["model", "outcome", "coef", "se_person_cluster", "t_person_cluster", "se_state_cluster", "t_state_cluster", "n_person_months", "n_persons"]].to_string(index=False))


if __name__ == "__main__":
    main()
