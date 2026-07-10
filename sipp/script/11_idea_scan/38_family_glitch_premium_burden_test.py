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
SOURCE_SCRATCH = ROOT / "temp" / "scratch" / "cobra_source_job_vars_2018_2024.parquet"
PREMIUM_SCRATCH = ROOT / "temp" / "scratch" / "family_glitch_premium_vars_2018_2024.parquet"
OUT = ROOT / "result" / "idea_scan"
REPORT = ROOT / "report" / "76_family_glitch_premium_burden_test.md"


SOURCES = [
    "Federal Register final rule: https://www.federalregister.gov/documents/2022/10/13/2022-22184/affordability-of-employer-coverage-for-family-members-of-employees",
    "CMS technical assistance PDF: https://www.cms.gov/marketplace/technical-assistance-resources/afford-employer-coverage-fixing-family-glitch.pdf",
]


PREMIUM_COLS = ["SSUID", "PNUM", "MONTHCODE", "THIPAYC", "EWHIPAYC", "THIPAYS", "EWHIPAYS"]


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


def extract_premium_vars() -> pd.DataFrame:
    if PREMIUM_SCRATCH.exists():
        return pd.read_parquet(PREMIUM_SCRATCH)

    PREMIUM_SCRATCH.parent.mkdir(parents=True, exist_ok=True)
    writer: pq.ParquetWriter | None = None
    for file_year in range(2018, 2025):
        zpath = RAW / str(file_year) / "primary" / f"pu{file_year}_csv.zip"
        header = set(read_raw_header(file_year))
        usecols = [c for c in PREMIUM_COLS if c in header]
        for chunk in pd.read_csv(
            zpath,
            sep="|",
            usecols=usecols,
            compression="zip",
            chunksize=100_000,
            low_memory=True,
        ):
            out = chunk.copy()
            out["file_year"] = file_year
            for col in PREMIUM_COLS:
                if col not in out.columns:
                    out[col] = np.nan
            out = out[PREMIUM_COLS + ["file_year"]]
            out["SSUID"] = out["SSUID"].astype("string")
            for col in out.columns:
                if col != "SSUID":
                    out[col] = pd.to_numeric(out[col], errors="coerce")
            for col in ["THIPAYC", "EWHIPAYC", "THIPAYS", "EWHIPAYS"]:
                out[col] = out[col].astype("float64")
            out["PNUM"] = out["PNUM"].astype("Int64")
            out["MONTHCODE"] = out["MONTHCODE"].astype("Int64")
            out["file_year"] = out["file_year"].astype("int64")
            table = pa.Table.from_pandas(out, preserve_index=False)
            if writer is None:
                writer = pq.ParquetWriter(PREMIUM_SCRATCH, table.schema, compression="snappy")
            writer.write_table(table)
    if writer is not None:
        writer.close()
    return pd.read_parquet(PREMIUM_SCRATCH)


def read_source_vars() -> pd.DataFrame:
    if not SOURCE_SCRATCH.exists():
        raise FileNotFoundError(
            f"Missing {SOURCE_SCRATCH}. Run 37_arpa_cobra_subsidy_test.py first to create source/job vars."
        )
    cols = [
        "SSUID",
        "PNUM",
        "MONTHCODE",
        "file_year",
        "EPR1MTH",
        "EPR2MTH",
        "EHEMPLY1",
        "EHEMPLY2",
        "EHICOST1",
        "EHICOST2",
    ]
    return pd.read_parquet(SOURCE_SCRATCH, columns=cols)


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


def read_augmented_months() -> pd.DataFrame:
    cols = [
        "SSUID",
        "PNUM",
        "MONTHCODE",
        "SHHADID",
        "RFAMNUM",
        "person_id",
        "person_month_key",
        "file_year",
        "reference_year",
        "reference_date",
        "reference_month",
        "state_fips",
        "TAGE",
        "ESEX",
        "ERACE",
        "EORIGIN",
        "EHISPAN",
        "EPNSPOUSE",
        "RDIS",
        "WPFINWGT",
        "TSSSAMT",
        "RHLTHMTH",
        "RPRIMTH",
        "RPUBMTH",
        "RPUBTYPE1",
        "EMDMTH",
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
        "THTOTINC",
        "TFTOTINC",
        "TMDPAY",
        "TVISDOC",
    ]
    base = pd.read_parquet(PANEL, columns=cols)
    src = read_source_vars()
    prem = extract_premium_vars()
    for frame in [base, src, prem]:
        frame["SSUID"] = frame["SSUID"].astype("string")
        for col in ["file_year", "PNUM", "MONTHCODE"]:
            frame[col] = pd.to_numeric(frame[col], errors="coerce").astype("Int64")
    merged = base.merge(src, on=["file_year", "SSUID", "PNUM", "MONTHCODE"], how="left", validate="one_to_one")
    merged = merged.merge(prem, on=["file_year", "SSUID", "PNUM", "MONTHCODE"], how="left", validate="one_to_one")
    return merged


def build_person_year(df: pd.DataFrame) -> pd.DataFrame:
    d = df.copy()
    d["state_fips"] = d["state_fips"].astype("string").str.zfill(2)
    d["age"] = bounded_numeric(d["TAGE"], 0, 100)
    d["female"] = num(d["ESEX"]).eq(2).astype(float)
    d["black"] = num(d["ERACE"]).eq(2).astype(float)
    d["hispanic"] = (num(d["EORIGIN"]).eq(1) | num(d["EHISPAN"]).eq(1)).astype(float)
    d["disabled"] = yes(d["RDIS"]).astype(float)
    d["fpl"] = bounded_numeric(d["TFINCPOV"], 0, 20)
    d["annual_fpl"] = bounded_numeric(d["TFCYINCPOV"], 0, 20)
    d["weight"] = clean_weight(d)
    d["medicare"] = yes(d["RPUBTYPE1"]).astype(float)
    d["any_coverage"] = yes(d["RHLTHMTH"]).astype(float)
    d["uninsured"] = num(d["RHLTHMTH"]).eq(2).astype(float)
    d["private"] = yes(d["RPRIMTH"]).astype(float)
    d["public"] = yes(d["RPUBMTH"]).astype(float)
    d["medicaid"] = yes(d["EMDMTH"]).astype(float)
    d["direct_market"] = (yes(d["RPRITYPE2"]) | yes(d["RMARKTPLACE"])).astype(float)
    d["exchange_subsidy"] = (
        yes(d["RMARKTPLACE"])
        | yes(d["EPRIEXCH1"])
        | yes(d["EPRIEXCH2"])
        | yes(d["EPRISUBS1"])
        | yes(d["EPRISUBS2"])
        | yes(d["EMDEXCH"])
        | yes(d["EMDSUBS"])
    ).astype(float)
    d["oop_any"] = bounded_numeric(d["TMDPAY"], 0, 200_000).gt(0).astype(float)
    d["doctor_any"] = bounded_numeric(d["TVISDOC"], 0, 200).gt(0).astype(float)

    epr1 = yes(d.get("EPR1MTH", pd.Series(index=d.index, dtype="float")))
    epr2 = yes(d.get("EPR2MTH", pd.Series(index=d.index, dtype="float")))
    emp1 = num(d.get("EHEMPLY1", pd.Series(index=d.index, dtype="float")))
    emp2 = num(d.get("EHEMPLY2", pd.Series(index=d.index, dtype="float")))
    d["current_employer_private"] = ((epr1 & emp1.eq(1)) | (epr2 & emp2.eq(1))).astype(float)
    d["former_employer_private"] = ((epr1 & emp1.eq(2)) | (epr2 & emp2.eq(2))).astype(float)
    d["union_private"] = ((epr1 & emp1.eq(3)) | (epr2 & emp2.eq(3))).astype(float)
    d["employer_related_private"] = (
        d["current_employer_private"].eq(1)
        | d["former_employer_private"].eq(1)
        | d["union_private"].eq(1)
    ).astype(float)
    d["bought_direct_source"] = ((epr1 & emp1.eq(4)) | (epr2 & emp2.eq(4))).astype(float)

    d["child"] = d["age"].lt(18)
    d["adult"] = d["age"].ge(18)
    d["spouse_linked"] = d["EPNSPOUSE"].notna().astype(float)
    family_keys = ["SSUID", "SHHADID", "RFAMNUM", "reference_date"]
    fam = (
        d.groupby(family_keys, observed=True)
        .agg(
            family_persons=("PNUM", "nunique"),
            family_children=("child", "sum"),
            family_adults=("adult", "sum"),
            family_spouse_links=("spouse_linked", "sum"),
        )
        .reset_index()
    )
    d = d.merge(fam, on=family_keys, how="left")
    d["family_exposed"] = (
        d["family_persons"].ge(2) & (d["family_children"].gt(0) | d["family_spouse_links"].gt(0))
    ).astype(float)

    d["premium_comp"] = bounded_numeric(d["THIPAYC"], 0, 999_000)
    d["premium_who"] = num(d["EWHIPAYC"])
    d["paid_for_family_or_others"] = d["premium_who"].isin([2, 3, 4]).astype(float)
    d["hh_month_income"] = bounded_numeric(d["THTOTINC"], 1, 10_000_000)
    d["fam_month_income"] = bounded_numeric(d["TFTOTINC"], 1, 10_000_000)

    py = (
        d.groupby(["person_id", "state_fips", "reference_year"], observed=True)
        .agg(
            months=("person_month_key", "size"),
            weight=("weight", "mean"),
            age=("age", "mean"),
            female=("female", "mean"),
            black=("black", "mean"),
            hispanic=("hispanic", "mean"),
            disabled=("disabled", "mean"),
            fpl=("fpl", "median"),
            annual_fpl=("annual_fpl", "median"),
            hh_month_income=("hh_month_income", "mean"),
            fam_month_income=("fam_month_income", "mean"),
            any_coverage=("any_coverage", "mean"),
            uninsured=("uninsured", "mean"),
            private=("private", "mean"),
            public=("public", "mean"),
            medicaid=("medicaid", "mean"),
            direct_market=("direct_market", "mean"),
            exchange_subsidy=("exchange_subsidy", "mean"),
            employer_related_private=("employer_related_private", "mean"),
            current_employer_private=("current_employer_private", "mean"),
            former_employer_private=("former_employer_private", "mean"),
            bought_direct_source=("bought_direct_source", "mean"),
            oop_any=("oop_any", "mean"),
            doctor_any=("doctor_any", "mean"),
            family_exposed=("family_exposed", "mean"),
            family_persons=("family_persons", "mean"),
            family_children=("family_children", "mean"),
            family_adults=("family_adults", "mean"),
            premium_comp=("premium_comp", "median"),
            premium_comp_max=("premium_comp", "max"),
            paid_for_family_or_others=("paid_for_family_or_others", "max"),
        )
        .reset_index()
    )
    py = py[py["months"].ge(6)].copy()
    py["family_exposed"] = py["family_exposed"].ge(0.5).astype(float)
    py["annual_hh_income"] = py["hh_month_income"] * 12
    py["premium_burden"] = py["premium_comp"] / py["annual_hh_income"]
    py["premium_burden"] = py["premium_burden"].where(py["premium_burden"].between(0, 1.5))
    py["premium_any"] = py["premium_comp"].gt(0).astype(float)
    py["premium_gt_0912"] = py["premium_burden"].gt(0.0912).astype(float)
    py["premium_gt_05"] = py["premium_burden"].gt(0.05).astype(float)
    return py


def build_transition_pairs(py: pd.DataFrame) -> pd.DataFrame:
    outcomes = [
        "direct_market",
        "exchange_subsidy",
        "uninsured",
        "any_coverage",
        "private",
        "employer_related_private",
        "current_employer_private",
        "bought_direct_source",
        "oop_any",
        "doctor_any",
    ]
    base_cols = [
        "person_id",
        "state_fips",
        "reference_year",
        "weight",
        "age",
        "female",
        "black",
        "hispanic",
        "disabled",
        "fpl",
        "annual_fpl",
        "family_exposed",
        "family_persons",
        "family_children",
        "family_adults",
        "premium_comp",
        "premium_burden",
        "premium_any",
        "premium_gt_0912",
        "premium_gt_05",
        "paid_for_family_or_others",
        "employer_related_private",
        "current_employer_private",
        "direct_market",
        "exchange_subsidy",
        "any_coverage",
        "private",
        "uninsured",
        "bought_direct_source",
        "oop_any",
        "doctor_any",
    ]
    pyu = (
        py.sort_values(["person_id", "reference_year", "months", "weight"], ascending=[True, True, False, False])
        .drop_duplicates(["person_id", "reference_year"], keep="first")
        .copy()
    )
    rows = []
    by = {int(y): g.set_index("person_id") for y, g in pyu.groupby("reference_year", observed=True)}
    for y in [2019, 2020, 2021, 2022]:
        if y not in by or y + 1 not in by:
            continue
        idx = by[y].index.intersection(by[y + 1].index)
        b = by[y].loc[idx, base_cols[1:]].copy()
        f = by[y + 1].loc[idx, ["weight", *outcomes]].copy()
        pair = pd.DataFrame(index=idx)
        pair["person_id"] = idx
        pair["baseline_year"] = y
        pair["post_year"] = y + 1
        for col in base_cols[1:]:
            pair[col] = b[col].values
        pair["post_weight"] = f["weight"].values
        pair["analysis_weight"] = pair["weight"].where(pair["weight"].gt(0), pair["post_weight"])
        for outcome in outcomes:
            pair[f"{outcome}_base"] = b[outcome].values if outcome in b.columns else np.nan
            pair[f"{outcome}_post"] = f[outcome].values
            pair[f"d_{outcome}"] = pair[f"{outcome}_post"] - pair[f"{outcome}_base"]
        rows.append(pair.reset_index(drop=True))
    pairs = pd.concat(rows, ignore_index=True)
    pairs["actual_2022_2023"] = pairs["baseline_year"].eq(2022).astype(float)
    pairs["state_pair"] = pairs["state_fips"].astype("string") + "_" + pairs["baseline_year"].astype(str)
    return pairs


def analytic_samples(pairs: pd.DataFrame) -> dict[str, pd.DataFrame]:
    base = pairs[
        pairs["age"].between(26, 64, inclusive="both")
        & pairs["fpl"].between(1.38, 6.0, inclusive="both")
        & pairs["family_exposed"].eq(1)
        & pairs["employer_related_private"].ge(0.5)
        & pairs["direct_market"].lt(0.1)
        & pairs["exchange_subsidy"].lt(0.1)
        & pairs["premium_any"].eq(1)
        & pairs["premium_burden"].notna()
        & pairs["analysis_weight"].gt(0)
    ].copy()
    paid_family = base[base["paid_for_family_or_others"].eq(1)].copy()
    high_burden = base[base["premium_gt_0912"].eq(1)].copy()
    return {
        "baseline_family_employer_premium_atrisk": base,
        "paid_for_family_or_others": paid_family,
        "premium_gt_0912_only": high_burden,
    }


def design_matrix(df: pd.DataFrame, high_col: str) -> tuple[pd.DataFrame, str]:
    x = pd.DataFrame(index=df.index)
    coef_name = f"{high_col}_x_actual"
    x["intercept"] = 1.0
    x[coef_name] = df[high_col].astype(float) * df["actual_2022_2023"].astype(float)
    x[high_col] = df[high_col].astype(float)
    x["actual_2022_2023"] = df["actual_2022_2023"].astype(float)
    x["age"] = df["age"].astype(float)
    x["female"] = df["female"].astype(float)
    x["black"] = df["black"].astype(float)
    x["hispanic"] = df["hispanic"].astype(float)
    x["disabled"] = df["disabled"].astype(float)
    x["fpl"] = df["fpl"].clip(0, 10).astype(float)
    x["family_persons"] = df["family_persons"].clip(1, 12).astype(float)
    x["family_children"] = df["family_children"].clip(0, 10).astype(float)
    for col in ["baseline_year", "state_fips"]:
        x = pd.concat([x, pd.get_dummies(df[col].astype("string"), prefix=col, drop_first=True, dtype=float)], axis=1)
    return x, coef_name


def run_models(samples: dict[str, pd.DataFrame]) -> pd.DataFrame:
    outcomes = [
        "d_direct_market",
        "d_exchange_subsidy",
        "d_uninsured",
        "d_any_coverage",
        "d_private",
        "d_employer_related_private",
        "d_current_employer_private",
        "d_bought_direct_source",
        "d_oop_any",
        "d_doctor_any",
    ]
    rows = []
    for sample_name, s in samples.items():
        if len(s) < 100:
            continue
        for high_col in ["premium_gt_0912", "premium_gt_05"]:
            if s[high_col].sum() < 10 or (s[high_col].eq(0)).sum() < 10:
                continue
            x, coef_name = design_matrix(s, high_col)
            x_np = x.to_numpy(dtype=float)
            w = s["analysis_weight"].to_numpy(dtype=float)
            cluster = s["person_id"].astype(str).to_numpy()
            treated = s[s[high_col].eq(1) & s["actual_2022_2023"].eq(1)]
            for outcome in outcomes:
                y = s[outcome].to_numpy(dtype=float)
                beta, se_hc1, se_cl, n, g = weighted_ols_cluster(y, x_np, w, cluster)
                b = pd.Series(beta, index=x.columns)
                hc1 = pd.Series(se_hc1, index=x.columns)
                cl = pd.Series(se_cl, index=x.columns)
                rows.append(
                    {
                        "sample": sample_name,
                        "high_col": high_col,
                        "outcome": outcome,
                        "coef_high_x_2023": b.get(coef_name, np.nan),
                        "se_hc1": hc1.get(coef_name, np.nan),
                        "t_hc1": b.get(coef_name, np.nan) / hc1.get(coef_name, np.nan)
                        if hc1.get(coef_name, np.nan) > 0
                        else np.nan,
                        "se_person_cluster": cl.get(coef_name, np.nan),
                        "t_person_cluster": b.get(coef_name, np.nan) / cl.get(coef_name, np.nan)
                        if cl.get(coef_name, np.nan) > 0
                        else np.nan,
                        "n_pairs": n,
                        "n_persons": persons(s["person_id"]),
                        "n_clusters": g,
                        "n_states": int(s["state_fips"].nunique()),
                        "actual_high_pairs": int(len(treated)),
                        "actual_high_persons": persons(treated["person_id"]),
                        "weighted_mean_delta": wmean(s[outcome], s["analysis_weight"]),
                    }
                )
    return pd.DataFrame(rows)


def raw_support(samples: dict[str, pd.DataFrame]) -> tuple[pd.DataFrame, pd.DataFrame]:
    rows = []
    raw_rows = []
    for sample_name, s in samples.items():
        for high_col in ["premium_gt_0912", "premium_gt_05"]:
            for actual in [0.0, 1.0]:
                for high in [0.0, 1.0]:
                    cell = s[s["actual_2022_2023"].eq(actual) & s[high_col].eq(high)]
                    rows.append(
                        {
                            "sample": sample_name,
                            "high_col": high_col,
                            "actual_2022_2023": int(actual),
                            "high": int(high),
                            "pairs": int(len(cell)),
                            "persons": persons(cell["person_id"]),
                            "states": int(cell["state_fips"].nunique()) if len(cell) else 0,
                            "mean_premium_burden": wmean(cell["premium_burden"], cell["analysis_weight"])
                            if len(cell)
                            else np.nan,
                        }
                    )
                    if sample_name == "baseline_family_employer_premium_atrisk":
                        raw_rows.append(
                            {
                                "high_col": high_col,
                                "actual_2022_2023": int(actual),
                                "high": int(high),
                                "pairs": int(len(cell)),
                                "persons": persons(cell["person_id"]),
                                "d_direct_market": wmean(cell["d_direct_market"], cell["analysis_weight"])
                                if len(cell)
                                else np.nan,
                                "d_exchange_subsidy": wmean(cell["d_exchange_subsidy"], cell["analysis_weight"])
                                if len(cell)
                                else np.nan,
                                "d_uninsured": wmean(cell["d_uninsured"], cell["analysis_weight"])
                                if len(cell)
                                else np.nan,
                                "d_private": wmean(cell["d_private"], cell["analysis_weight"]) if len(cell) else np.nan,
                                "d_employer_related_private": wmean(
                                    cell["d_employer_related_private"], cell["analysis_weight"]
                                )
                                if len(cell)
                                else np.nan,
                            }
                        )
    return pd.DataFrame(rows), pd.DataFrame(raw_rows)


def fmt_est(est: pd.DataFrame, sample: str, high_col: str, outcome: str) -> str:
    r = est[(est["sample"].eq(sample)) & (est["high_col"].eq(high_col)) & (est["outcome"].eq(outcome))]
    if r.empty:
        return "NA"
    row = r.iloc[0]
    return (
        f"{row['coef_high_x_2023']:+.4f} "
        f"(person-cluster se {row['se_person_cluster']:.4f}, t {row['t_person_cluster']:.2f}; "
        f"actual high-burden pairs {int(row['actual_high_pairs'])})"
    )


def md_table(df: pd.DataFrame, cols: list[str], max_rows: int = 24) -> str:
    d = df[cols].head(max_rows)
    lines = ["| " + " | ".join(cols) + " |", "|" + "|".join(["---"] * len(cols)) + "|"]
    for _, r in d.iterrows():
        vals = []
        for c in cols:
            v = r[c]
            vals.append(f"{v:.4f}" if isinstance(v, float) else str(v))
        lines.append("| " + " | ".join(vals) + " |")
    return "\n".join(lines)


def write_report(py: pd.DataFrame, pairs: pd.DataFrame, support: pd.DataFrame, raw: pd.DataFrame, est: pd.DataFrame) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    py.to_parquet(OUT / "family_glitch_premium_person_year_panel.parquet", index=False)
    pairs.to_parquet(OUT / "family_glitch_premium_transition_pairs.parquet", index=False)
    support.to_csv(OUT / "family_glitch_premium_support.csv", index=False)
    raw.to_csv(OUT / "family_glitch_premium_raw_cells.csv", index=False)
    est.to_csv(OUT / "family_glitch_premium_estimates.csv", index=False)

    main = "baseline_family_employer_premium_atrisk"
    high = "premium_gt_0912"
    support_main = support[
        support["sample"].eq(main) & support["high_col"].eq(high) & support["actual_2022_2023"].eq(1)
    ]
    actual_high = support_main[support_main["high"].eq(1)]
    high_pairs = int(actual_high.iloc[0]["pairs"]) if not actual_high.empty else 0
    high_persons = int(actual_high.iloc[0]["persons"]) if not actual_high.empty else 0

    dm = est[(est["sample"].eq(main)) & (est["high_col"].eq(high)) & (est["outcome"].eq("d_direct_market"))]
    ex = est[(est["sample"].eq(main)) & (est["high_col"].eq(high)) & (est["outcome"].eq("d_exchange_subsidy"))]
    un = est[(est["sample"].eq(main)) & (est["high_col"].eq(high)) & (est["outcome"].eq("d_uninsured"))]
    verdict = "NO-GO"
    if (
        high_pairs >= 100
        and not dm.empty
        and dm.iloc[0]["coef_high_x_2023"] > 0
        and not ex.empty
        and ex.iloc[0]["coef_high_x_2023"] > 0
        and not un.empty
        and un.iloc[0]["coef_high_x_2023"] <= 0
    ):
        verdict = "CONDITIONAL GO / MECHANISM REFINEMENT"

    report = [
        "# Family Glitch Premium-Burden Refinement Test",
        "",
        "## Question",
        "",
        "Can the 2023 ACA family-glitch fix be tested more credibly in SIPP by focusing on family-exposed adults who had employer-related private coverage, paid comprehensive health-insurance premiums, and had high baseline premium burden before the 2023 rule change?",
        "",
        "## Source Checks",
        "",
    ]
    report += [f"- {s}" for s in SOURCES]
    report += [
        "",
        "The final rule changed affordability testing for family members so that family-member PTC eligibility depends on the employee share of the cost of covering the employee and family members, not self-only employee coverage. CMS technical assistance describes the case where self-only coverage can remain affordable for the employee while family coverage is unaffordable for family members.",
        "",
        "## Construction",
        "",
        "- Base panel: `data/analysis_ready/sipp_2018_2024_person_month_panel.parquet`.",
        "- Raw private-source supplement: `temp/scratch/cobra_source_job_vars_2018_2024.parquet`.",
        "- New raw premium supplement: `temp/scratch/family_glitch_premium_vars_2018_2024.parquet`.",
        "- Baseline at-risk sample: adults 26-64, 138-600% FPL, family-exposed, employer-related private coverage, no direct-market/exchange coverage, positive comprehensive premium payment.",
        "- High burden: baseline `THIPAYC / (12 x THTOTINC) > 9.12%`.",
        "- Design: transition DDD using baseline years 2019-2022; key term is `high premium burden x 2022->2023 transition`.",
        "",
        "Measurement caveat: `THIPAYC` is household premium payment, not the exact employee share for self-only versus family coverage. This is a mechanism-focused refinement, not direct statutory eligibility.",
        "",
        "## Support",
        "",
        f"- Actual 2022->2023 high-burden at-risk pairs at 9.12% cutoff: {high_pairs:,} pairs, {high_persons:,} persons.",
        "",
        md_table(
            support,
            ["sample", "high_col", "actual_2022_2023", "high", "pairs", "persons", "states", "mean_premium_burden"],
            max_rows=36,
        ),
        "",
        "## Raw Transition Means",
        "",
        "Main at-risk sample. Outcomes are post-year minus baseline-year coverage shares.",
        "",
        md_table(
            raw,
            [
                "high_col",
                "actual_2022_2023",
                "high",
                "pairs",
                "persons",
                "d_direct_market",
                "d_exchange_subsidy",
                "d_uninsured",
                "d_private",
                "d_employer_related_private",
            ],
            max_rows=16,
        ),
        "",
        "## Transition-DDD Estimates",
        "",
        "Main at-risk sample, high burden > 9.12%:",
        "",
        f"- Direct-market coverage: {fmt_est(est, main, high, 'd_direct_market')}.",
        f"- Exchange/subsidy proxy: {fmt_est(est, main, high, 'd_exchange_subsidy')}.",
        f"- Uninsured: {fmt_est(est, main, high, 'd_uninsured')}.",
        f"- Any coverage: {fmt_est(est, main, high, 'd_any_coverage')}.",
        f"- Private coverage: {fmt_est(est, main, high, 'd_private')}.",
        f"- Employer-related private: {fmt_est(est, main, high, 'd_employer_related_private')}.",
        "",
        "Main at-risk sample, high burden > 5% sensitivity:",
        "",
        f"- Direct-market coverage: {fmt_est(est, main, 'premium_gt_05', 'd_direct_market')}.",
        f"- Exchange/subsidy proxy: {fmt_est(est, main, 'premium_gt_05', 'd_exchange_subsidy')}.",
        f"- Uninsured: {fmt_est(est, main, 'premium_gt_05', 'd_uninsured')}.",
        f"- Private coverage: {fmt_est(est, main, 'premium_gt_05', 'd_private')}.",
        "",
        "## Decision",
        "",
        f"`FAMILY GLITCH PREMIUM-BURDEN REFINEMENT: {verdict}`.",
        "",
        "A clean paper needs a positive direct-market / exchange transition concentrated in high-premium-burden family-employer baseline households in 2022->2023, with no similar placebo transition in earlier pairs and no rise in uninsurance. This screen is the closest current SIPP can get without actual employer offer and family premium eligibility fields.",
        "",
        "## Artifacts",
        "",
        "- `script/11_idea_scan/38_family_glitch_premium_burden_test.py`",
        "- `report/76_family_glitch_premium_burden_test.md`",
        "- `result/idea_scan/family_glitch_premium_person_year_panel.parquet`",
        "- `result/idea_scan/family_glitch_premium_transition_pairs.parquet`",
        "- `result/idea_scan/family_glitch_premium_support.csv`",
        "- `result/idea_scan/family_glitch_premium_raw_cells.csv`",
        "- `result/idea_scan/family_glitch_premium_estimates.csv`",
    ]
    REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")


def main() -> None:
    df = read_augmented_months()
    py = build_person_year(df)
    pairs = build_transition_pairs(py)
    samples = analytic_samples(pairs)
    support, raw = raw_support(samples)
    est = run_models(samples)
    write_report(py, pairs, support, raw, est)
    print(f"Wrote {REPORT}")
    print(support.to_string(index=False))
    if not est.empty:
        cols = [
            "sample",
            "high_col",
            "outcome",
            "coef_high_x_2023",
            "se_person_cluster",
            "t_person_cluster",
            "actual_high_pairs",
        ]
        print(est[cols].to_string(index=False))


if __name__ == "__main__":
    main()
