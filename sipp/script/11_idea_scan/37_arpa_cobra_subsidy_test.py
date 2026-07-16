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
SCRATCH = ROOT / "temp" / "scratch" / "cobra_source_job_vars_2018_2024.parquet"
OUT = ROOT / "result" / "idea_scan"
REPORT = ROOT / "report" / "74_arpa_cobra_subsidy_test.md"


SOURCES = [
    "DOL COBRA premium assistance FAQ: https://www.dol.gov/sites/dolgov/files/EBSA/about-ebsa/our-activities/resource-center/faqs/cobra-premium-assistance.pdf",
    "KFF ARPA private coverage affordability summary: https://www.kff.org/affordable-care-act/how-the-american-rescue-plan-will-improve-affordability-of-private-health-coverage/",
]


RAW_BASE_COLS = [
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
JOB_COLS = []
for _j in range(1, 8):
    JOB_COLS.extend([f"EJB{_j}_BMONTH", f"EJB{_j}_EMONTH", f"EJB{_j}_JBORSE", f"EJB{_j}_RSEND"])
RAW_COLS = RAW_BASE_COLS + JOB_COLS


def yes(s: pd.Series) -> pd.Series:
    return pd.to_numeric(s, errors="coerce").eq(1)


def num(s: pd.Series) -> pd.Series:
    return pd.to_numeric(s, errors="coerce")


def bounded_numeric(s: pd.Series, lo: float, hi: float) -> pd.Series:
    out = pd.to_numeric(s, errors="coerce")
    return out.where(out.between(lo, hi, inclusive="both"))


def clean_weight(df: pd.DataFrame) -> pd.Series:
    w = pd.to_numeric(df.get("WPFINWGT"), errors="coerce")
    return w.where(w.gt(0))


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


def extract_raw_source_job_vars() -> pd.DataFrame:
    if SCRATCH.exists():
        return pd.read_parquet(SCRATCH)

    SCRATCH.parent.mkdir(parents=True, exist_ok=True)
    writer: pq.ParquetWriter | None = None
    for file_year in range(2018, 2025):
        zpath = RAW / str(file_year) / "primary" / f"pu{file_year}_csv.zip"
        header = set(read_raw_header(file_year))
        usecols = [c for c in RAW_COLS if c in header]
        chunks = pd.read_csv(
            zpath,
            sep="|",
            usecols=usecols,
            compression="zip",
            chunksize=100_000,
            low_memory=True,
        )
        for chunk in chunks:
            out = chunk.copy()
            out["file_year"] = file_year
            for col in RAW_COLS:
                if col not in out.columns:
                    out[col] = np.nan
            out = out[RAW_COLS + ["file_year"]]
            out["SSUID"] = out["SSUID"].astype("string")
            for col in out.columns:
                if col != "SSUID":
                    out[col] = pd.to_numeric(out[col], errors="coerce")
            out["PNUM"] = out["PNUM"].astype("Int64")
            out["MONTHCODE"] = out["MONTHCODE"].astype("Int64")
            table = pa.Table.from_pandas(out, preserve_index=False)
            if writer is None:
                writer = pq.ParquetWriter(SCRATCH, table.schema, compression="snappy")
            writer.write_table(table)
    if writer is not None:
        writer.close()
    return pd.read_parquet(SCRATCH)


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
        "TMDPAY",
        "TVISDOC",
    ]
    base = pd.read_parquet(PANEL, columns=cols)
    raw = extract_raw_source_job_vars()
    base["SSUID"] = base["SSUID"].astype("string")
    raw["SSUID"] = raw["SSUID"].astype("string")
    for col in ["file_year", "PNUM", "MONTHCODE"]:
        base[col] = pd.to_numeric(base[col], errors="coerce").astype("Int64")
        raw[col] = pd.to_numeric(raw[col], errors="coerce").astype("Int64")
    return base.merge(raw, on=["file_year", "SSUID", "PNUM", "MONTHCODE"], how="left", validate="one_to_one")


def add_constructs(df: pd.DataFrame) -> pd.DataFrame:
    d = df.copy()
    d["state_fips"] = d["state_fips"].astype("string").str.zfill(2)
    d["age"] = bounded_numeric(d["TAGE"], 0, 100)
    d["female"] = num(d["ESEX"]).eq(2).astype(float)
    d["black"] = num(d["ERACE"]).eq(2).astype(float)
    d["hispanic"] = (num(d["EORIGIN"]).eq(1) | num(d["EHISPAN"]).eq(1)).astype(float)
    d["disabled"] = yes(d["RDIS"]).astype(float)
    d["fpl"] = bounded_numeric(d["TFINCPOV"], 0, 20)
    d["weight"] = clean_weight(d)
    d["seq_month"] = d["reference_year"].astype(int) * 12 + d["reference_month"].astype(int)
    d["month_id"] = d["reference_year"].astype(int) * 100 + d["reference_month"].astype(int)
    d["medicare"] = yes(d["RPUBTYPE1"]).astype(float)
    d["any_coverage"] = yes(d["RHLTHMTH"]).astype(float)
    d["uninsured"] = num(d["RHLTHMTH"]).eq(2).astype(float)
    d["private"] = yes(d["RPRIMTH"]).astype(float)
    d["public"] = yes(d["RPUBMTH"]).astype(float)
    d["medicaid"] = yes(d["EMDMTH"]).astype(float)
    d["direct_purchase"] = (yes(d["RPRITYPE2"]) | yes(d["RMARKTPLACE"])).astype(float)
    d["marketplace_flag"] = (
        yes(d["RMARKTPLACE"]) | yes(d["EPRIEXCH1"]) | yes(d["EPRIEXCH2"]) | yes(d["EMDEXCH"])
    ).astype(float)
    d["subsidized_private"] = (yes(d["EPRISUBS1"]) | yes(d["EPRISUBS2"]) | yes(d["EMDSUBS"])).astype(float)
    d["market_or_subsidy"] = (
        d["direct_purchase"].eq(1) | d["marketplace_flag"].eq(1) | d["subsidized_private"].eq(1)
    ).astype(float)
    d["oop_any"] = bounded_numeric(d["TMDPAY"], 0, 200_000).gt(0).astype(float)
    d["doctor_any"] = bounded_numeric(d["TVISDOC"], 0, 200).gt(0).astype(float)

    epr1 = yes(d.get("EPR1MTH", pd.Series(index=d.index, dtype="float")))
    epr2 = yes(d.get("EPR2MTH", pd.Series(index=d.index, dtype="float")))
    emp1 = num(d.get("EHEMPLY1", pd.Series(index=d.index, dtype="float")))
    emp2 = num(d.get("EHEMPLY2", pd.Series(index=d.index, dtype="float")))
    cost1 = num(d.get("EHICOST1", pd.Series(index=d.index, dtype="float")))
    cost2 = num(d.get("EHICOST2", pd.Series(index=d.index, dtype="float")))

    d["current_employer_private"] = ((epr1 & emp1.eq(1)) | (epr2 & emp2.eq(1))).astype(float)
    d["former_employer_private"] = ((epr1 & emp1.eq(2)) | (epr2 & emp2.eq(2))).astype(float)
    d["union_private"] = ((epr1 & emp1.eq(3)) | (epr2 & emp2.eq(3))).astype(float)
    d["bought_direct_source"] = ((epr1 & emp1.eq(4)) | (epr2 & emp2.eq(4))).astype(float)
    d["employer_related_private"] = (
        d["current_employer_private"].eq(1)
        | d["former_employer_private"].eq(1)
        | d["union_private"].eq(1)
    ).astype(float)
    d["former_premium_all_paid"] = (
        (epr1 & emp1.eq(2) & cost1.eq(1)) | (epr2 & emp2.eq(2) & cost2.eq(1))
    ).astype(float)
    d["former_premium_none_paid"] = (
        (epr1 & emp1.eq(2) & cost1.eq(3)) | (epr2 & emp2.eq(2) & cost2.eq(3))
    ).astype(float)

    d["involuntary_sep"] = False
    d["involuntary_sep_noseason"] = False
    d["voluntary_sep"] = False
    d["any_sep"] = False
    d["sep_reason_min"] = np.nan
    for j in range(1, 8):
        end = num(d.get(f"EJB{j}_EMONTH", pd.Series(index=d.index, dtype="float")))
        reason = num(d.get(f"EJB{j}_RSEND", pd.Series(index=d.index, dtype="float")))
        jtype = num(d.get(f"EJB{j}_JBORSE", pd.Series(index=d.index, dtype="float")))
        this_event = end.eq(num(d["MONTHCODE"])) & reason.between(1, 16, inclusive="both") & jtype.isin([1, 3])
        inv = this_event & reason.isin([1, 2, 3, 4, 5, 6])
        inv_noseason = this_event & reason.isin([1, 2, 3, 5, 6])
        vol = this_event & reason.isin([7, 8, 9, 10, 11, 12, 13, 14, 15, 16])
        d["any_sep"] = d["any_sep"] | this_event
        d["involuntary_sep"] = d["involuntary_sep"] | inv
        d["involuntary_sep_noseason"] = d["involuntary_sep_noseason"] | inv_noseason
        d["voluntary_sep"] = d["voluntary_sep"] | vol
        d["sep_reason_min"] = np.fmin(d["sep_reason_min"].fillna(99), reason.where(this_event, 99)).replace(99, np.nan)

    d = d.sort_values(["person_id", "seq_month"])
    lag_cols = [
        "current_employer_private",
        "employer_related_private",
        "former_employer_private",
        "private",
        "uninsured",
        "any_coverage",
    ]
    for col in lag_cols:
        d[f"lag_{col}"] = d.groupby("person_id", observed=True)[col].shift(1)
    return d


def build_event_panel(d: pd.DataFrame) -> pd.DataFrame:
    outcomes = [
        "former_employer_private",
        "former_premium_all_paid",
        "former_premium_none_paid",
        "current_employer_private",
        "employer_related_private",
        "private",
        "uninsured",
        "any_coverage",
        "direct_purchase",
        "marketplace_flag",
        "market_or_subsidy",
        "public",
        "medicaid",
        "oop_any",
        "doctor_any",
    ]
    event = d[
        d["any_sep"]
        & (d["involuntary_sep"] | d["voluntary_sep"])
        & d["age"].between(26, 64, inclusive="both")
        & d["medicare"].ne(1)
        & d["weight"].gt(0)
        & d["reference_year"].between(2018, 2023, inclusive="both")
    ].copy()
    event = event[
        [
            "person_id",
            "seq_month",
            "reference_year",
            "reference_month",
            "state_fips",
            "weight",
            "age",
            "female",
            "black",
            "hispanic",
            "disabled",
            "fpl",
            "involuntary_sep",
            "involuntary_sep_noseason",
            "voluntary_sep",
            "sep_reason_min",
            "lag_current_employer_private",
            "lag_employer_related_private",
            "lag_private",
            "lag_uninsured",
            "lag_any_coverage",
        ]
    ].copy()
    event["involuntary"] = event["involuntary_sep"].astype(float)
    event["involuntary_noseason"] = event["involuntary_sep_noseason"].astype(float)
    event["subsidy_window"] = (
        event["reference_year"].eq(2021) & event["reference_month"].between(4, 9, inclusive="both")
    ).astype(float)
    event["apr_sep"] = event["reference_month"].between(4, 9, inclusive="both").astype(float)
    event["at_risk_lag_current_employer"] = event["lag_current_employer_private"].eq(1).astype(float)
    event["at_risk_lag_employer_related"] = event["lag_employer_related_private"].eq(1).astype(float)
    event["at_risk_lag_private"] = event["lag_private"].eq(1).astype(float)

    future = d[["person_id", "seq_month", *outcomes]].copy()
    for h in range(0, 4):
        tmp = future.copy()
        tmp["event_seq_month"] = tmp["seq_month"] - h
        tmp = tmp.drop(columns=["seq_month"])
        tmp = tmp.rename(columns={col: f"{col}_m{h}" for col in outcomes})
        event = event.merge(
            tmp,
            left_on=["person_id", "seq_month"],
            right_on=["person_id", "event_seq_month"],
            how="left",
        ).drop(columns=["event_seq_month"])

    for outcome in outcomes:
        event[f"{outcome}_m1_3"] = event[[f"{outcome}_m1", f"{outcome}_m2", f"{outcome}_m3"]].mean(axis=1)
        event[f"{outcome}_m0_3"] = event[
            [f"{outcome}_m0", f"{outcome}_m1", f"{outcome}_m2", f"{outcome}_m3"]
        ].mean(axis=1)
    return event


def design_matrix(df: pd.DataFrame, inv_col: str) -> tuple[pd.DataFrame, str]:
    x = pd.DataFrame(index=df.index)
    x["intercept"] = 1.0
    x["invol_x_subsidy"] = df[inv_col].astype(float) * df["subsidy_window"].astype(float)
    x["involuntary"] = df[inv_col].astype(float)
    x["age"] = df["age"].astype(float)
    x["fpl"] = df["fpl"].fillna(df["fpl"].median()).astype(float)
    x["female"] = df["female"].astype(float)
    x["black"] = df["black"].astype(float)
    x["hispanic"] = df["hispanic"].astype(float)
    x["disabled"] = df["disabled"].astype(float)
    x["lag_current_employer_private"] = df["lag_current_employer_private"].fillna(0).astype(float)
    x["lag_private"] = df["lag_private"].fillna(0).astype(float)
    x["lag_uninsured"] = df["lag_uninsured"].fillna(0).astype(float)
    for col in ["reference_year", "reference_month", "state_fips"]:
        x = pd.concat(
            [x, pd.get_dummies(df[col].astype("string"), prefix=col, drop_first=True, dtype=float)],
            axis=1,
        )
    return x, "invol_x_subsidy"


def run_event_model(event: pd.DataFrame, sample_name: str, sample: pd.DataFrame, inv_col: str, outcomes: list[str]) -> pd.DataFrame:
    rows = []
    x, coef_name = design_matrix(sample, inv_col)
    x_np = x.to_numpy(dtype=float)
    w = sample["weight"].to_numpy(dtype=float)
    cluster = sample["person_id"].astype(str).to_numpy()
    for outcome in outcomes:
        y = sample[outcome].to_numpy(dtype=float)
        beta, se_hc1, se_cluster, n, g = weighted_ols_cluster(y, x_np, w, cluster)
        b = pd.Series(beta, index=x.columns)
        h = pd.Series(se_hc1, index=x.columns)
        c = pd.Series(se_cluster, index=x.columns)
        rows.append(
            {
                "sample": sample_name,
                "inv_col": inv_col,
                "outcome": outcome,
                "coef_invol_x_subsidy": b.get(coef_name, np.nan),
                "se_hc1": h.get(coef_name, np.nan),
                "t_hc1": b.get(coef_name, np.nan) / h.get(coef_name, np.nan) if h.get(coef_name, np.nan) > 0 else np.nan,
                "se_person_cluster": c.get(coef_name, np.nan),
                "t_person_cluster": b.get(coef_name, np.nan) / c.get(coef_name, np.nan)
                if c.get(coef_name, np.nan) > 0
                else np.nan,
                "n_events": n,
                "n_persons": persons(sample["person_id"]),
                "n_clusters": g,
                "n_states": int(sample["state_fips"].nunique()),
                "treated_events": int((sample[inv_col].eq(1) & sample["subsidy_window"].eq(1)).sum()),
                "treated_persons": persons(sample.loc[sample[inv_col].eq(1) & sample["subsidy_window"].eq(1), "person_id"]),
                "treated_positive_outcomes": int(sample.loc[sample[inv_col].eq(1) & sample["subsidy_window"].eq(1), outcome].fillna(0).sum()),
                "weighted_mean": wmean(sample[outcome], sample["weight"]),
            }
        )
    return pd.DataFrame(rows)


def support_tables(event: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    rows = []
    support_samples = {
        "aprsep_exclude2020_all": event[event["apr_sep"].eq(1) & event["reference_year"].ne(2020)],
        "aprsep_exclude2020_lag_current_employer": event[
            event["apr_sep"].eq(1) & event["reference_year"].ne(2020) & event["at_risk_lag_current_employer"].eq(1)
        ],
        "allmonths_exclude2020_all": event[event["reference_year"].ne(2020)],
        "allmonths_exclude2020_lag_current_employer": event[
            event["reference_year"].ne(2020) & event["at_risk_lag_current_employer"].eq(1)
        ],
    }
    for name, s in support_samples.items():
        for inv_col in ["involuntary", "involuntary_noseason"]:
            treated = s[s[inv_col].eq(1) & s["subsidy_window"].eq(1)]
            control_inv = s[s[inv_col].eq(1) & s["subsidy_window"].eq(0)]
            control_vol = s[s[inv_col].eq(0)]
            rows.append(
                {
                    "sample": name,
                    "inv_col": inv_col,
                    "events": int(len(s)),
                    "persons": persons(s["person_id"]),
                    "treated_events": int(len(treated)),
                    "treated_persons": persons(treated["person_id"]),
                    "control_invol_events": int(len(control_inv)),
                    "control_voluntary_events": int(len(control_vol)),
                    "treated_lag_current_employer_events": int(treated["at_risk_lag_current_employer"].sum()),
                    "treated_lag_private_events": int(treated["at_risk_lag_private"].sum()),
                    "states": int(s["state_fips"].nunique()) if len(s) else 0,
                }
            )
    support = pd.DataFrame(rows)

    raw_rows = []
    raw_outcomes = [
        "former_employer_private_m0_3",
        "former_premium_all_paid_m0_3",
        "employer_related_private_m0_3",
        "uninsured_m0_3",
        "direct_purchase_m0_3",
        "market_or_subsidy_m0_3",
        "any_coverage_m0_3",
    ]
    raw_sample = support_samples["aprsep_exclude2020_all"]
    for (subsidy, inv), g in raw_sample.groupby(["subsidy_window", "involuntary"], observed=True):
        row = {
            "subsidy_window": int(subsidy),
            "involuntary": int(inv),
            "events": int(len(g)),
            "persons": persons(g["person_id"]),
            "lag_current_employer_events": int(g["at_risk_lag_current_employer"].sum()),
        }
        for outcome in raw_outcomes:
            row[outcome] = wmean(g[outcome], g["weight"])
        raw_rows.append(row)
    raw = pd.DataFrame(raw_rows)
    return support, raw


def run_all_models(event: pd.DataFrame) -> pd.DataFrame:
    outcomes = [
        "former_employer_private_m0_3",
        "former_premium_all_paid_m0_3",
        "former_premium_none_paid_m0_3",
        "employer_related_private_m0_3",
        "current_employer_private_m0_3",
        "private_m0_3",
        "uninsured_m0_3",
        "any_coverage_m0_3",
        "direct_purchase_m0_3",
        "marketplace_flag_m0_3",
        "market_or_subsidy_m0_3",
        "public_m0_3",
        "medicaid_m0_3",
        "oop_any_m0_3",
        "doctor_any_m0_3",
        "former_employer_private_m1_3",
        "uninsured_m1_3",
        "direct_purchase_m1_3",
        "market_or_subsidy_m1_3",
    ]
    samples = {
        "aprsep_exclude2020_all": event[event["apr_sep"].eq(1) & event["reference_year"].ne(2020)].copy(),
        "aprsep_exclude2020_lag_current_employer": event[
            event["apr_sep"].eq(1) & event["reference_year"].ne(2020) & event["at_risk_lag_current_employer"].eq(1)
        ].copy(),
        "allmonths_exclude2020_all": event[event["reference_year"].ne(2020)].copy(),
        "allmonths_exclude2020_lag_current_employer": event[
            event["reference_year"].ne(2020) & event["at_risk_lag_current_employer"].eq(1)
        ].copy(),
    }
    frames = []
    for sample_name, s in samples.items():
        for inv_col in ["involuntary", "involuntary_noseason"]:
            use = s[(s[inv_col].eq(1)) | (s["voluntary_sep"].eq(1))].copy()
            if len(use) >= 250 and (use[inv_col].eq(1) & use["subsidy_window"].eq(1)).sum() >= 10:
                frames.append(run_event_model(event, sample_name, use, inv_col, outcomes))
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()


def fmt_est(est: pd.DataFrame, sample: str, outcome: str, inv_col: str = "involuntary") -> str:
    r = est[(est["sample"].eq(sample)) & (est["outcome"].eq(outcome)) & (est["inv_col"].eq(inv_col))]
    if r.empty:
        return "NA"
    row = r.iloc[0]
    return (
        f"{row['coef_invol_x_subsidy']:+.4f} "
        f"(person-cluster se {row['se_person_cluster']:.4f}, t {row['t_person_cluster']:.2f}; "
        f"treated events {int(row['treated_events'])}, persons {int(row['treated_persons'])})"
    )


def md_table(df: pd.DataFrame, cols: list[str]) -> str:
    lines = ["| " + " | ".join(cols) + " |", "|" + "|".join(["---"] * len(cols)) + "|"]
    for _, r in df[cols].iterrows():
        vals = []
        for c in cols:
            v = r[c]
            if isinstance(v, float):
                vals.append(f"{v:.4f}")
            else:
                vals.append(str(v))
        lines.append("| " + " | ".join(vals) + " |")
    return "\n".join(lines)


def write_report(event: pd.DataFrame, support: pd.DataFrame, raw: pd.DataFrame, est: pd.DataFrame) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    event.to_parquet(OUT / "arpa_cobra_event_panel.parquet", index=False)
    support.to_csv(OUT / "arpa_cobra_support.csv", index=False)
    raw.to_csv(OUT / "arpa_cobra_raw_cells.csv", index=False)
    est.to_csv(OUT / "arpa_cobra_estimates.csv", index=False)

    main_support = support[
        support["sample"].eq("aprsep_exclude2020_lag_current_employer") & support["inv_col"].eq("involuntary")
    ]
    all_support = support[support["sample"].eq("aprsep_exclude2020_all") & support["inv_col"].eq("involuntary")]
    all_treated = int(all_support.iloc[0]["treated_events"]) if not all_support.empty else 0
    risk_treated = int(main_support.iloc[0]["treated_events"]) if not main_support.empty else 0
    risk_persons = int(main_support.iloc[0]["treated_persons"]) if not main_support.empty else 0

    verdict = "NO-GO for a main SIPP paper"
    if risk_treated >= 75:
        cobra_coef = est[
            est["sample"].eq("aprsep_exclude2020_lag_current_employer")
            & est["outcome"].eq("former_employer_private_m0_3")
            & est["inv_col"].eq("involuntary")
        ]
        unins_coef = est[
            est["sample"].eq("aprsep_exclude2020_lag_current_employer")
            & est["outcome"].eq("uninsured_m0_3")
            & est["inv_col"].eq("involuntary")
        ]
        if (
            not cobra_coef.empty
            and cobra_coef.iloc[0]["coef_invol_x_subsidy"] > 0
            and not unins_coef.empty
            and unins_coef.iloc[0]["coef_invol_x_subsidy"] < 0
        ):
            verdict = "CONDITIONAL GO as a narrow mechanism appendix or short paper"

    report = [
        "# ARPA COBRA Premium Subsidy SIPP Fast Test",
        "",
        "## Question",
        "",
        "Did the temporary ARPA 100% COBRA premium subsidy in April-September 2021 help adults who involuntarily left jobs retain employer-related or former-employer private coverage and avoid uninsurance?",
        "",
        "## Source Checks",
        "",
    ]
    report += [f"- {s}" for s in SOURCES]
    report += [
        "",
        "DOL states that ARP COBRA premium assistance applied to coverage periods from April 1, 2021 through September 30, 2021 and to people eligible for COBRA due to reduction in hours or involuntary termination. KFF describes the same six-month subsidy window and notes that voluntary quits were not eligible.",
        "",
        "## SIPP Construction",
        "",
        "- Base panel: `data/analysis_ready/sipp_2018_2024_person_month_panel.parquet`.",
        "- Raw supplement: `temp/scratch/cobra_source_job_vars_2018_2024.parquet`.",
        "- COBRA proxy: private-plan source line coded as `Former Employer` (`EHEMPLY1/2 == 2`) while the plan line is active.",
        "- Stronger premium proxy: former-employer private coverage where `EHICOST1/2 == 1`, meaning employer/union pays all of the policy premium.",
        "- Separation event: any job spell whose `EJB*_EMONTH` equals the reference month and has a stop-work reason in `EJB*_RSEND`.",
        "- Treated event proxy: involuntary separation (`RSEND` 1-6) in April-September 2021.",
        "- Control events: voluntary separations and involuntary separations in the same calendar months of other non-2020 years.",
        "- Main at-risk sample: adults 26-64 with current-employer private coverage in the prior month.",
        "",
        "Important measurement caveat: SIPP does not directly label COBRA. The closest monthly proxy is former-employer private coverage, plus the premium-payment source question.",
        "",
        "## Support",
        "",
        f"- April-September non-2020 separation events, all adults 26-64: {all_treated:,} treated involuntary events in the subsidy window.",
        f"- Main at-risk April-September sample with lagged current-employer private coverage: {risk_treated:,} treated involuntary events and {risk_persons:,} treated persons.",
        "",
        md_table(
            support,
            [
                "sample",
                "inv_col",
                "events",
                "persons",
                "treated_events",
                "treated_persons",
                "control_invol_events",
                "control_voluntary_events",
                "treated_lag_current_employer_events",
            ],
        ),
        "",
        "## Raw Event Means",
        "",
        "April-September non-2020 sample. Outcomes average months 0-3 after separation.",
        "",
        md_table(
            raw,
            [
                "subsidy_window",
                "involuntary",
                "events",
                "persons",
                "lag_current_employer_events",
                "former_employer_private_m0_3",
                "former_premium_all_paid_m0_3",
                "employer_related_private_m0_3",
                "uninsured_m0_3",
                "direct_purchase_m0_3",
                "market_or_subsidy_m0_3",
                "any_coverage_m0_3",
            ],
        ),
        "",
        "## Event-DDD Screen",
        "",
        "Weighted event-level OLS. Key coefficient is `involuntary separation x April-September 2021 subsidy window`; models include year, month, and state fixed effects plus age, FPL, sex, race/ethnicity, disability, and lagged coverage controls. Standard errors are clustered by person.",
        "",
        "Main at-risk sample, April-September, excluding 2020:",
        "",
        f"- Former-employer private coverage, months 0-3: {fmt_est(est, 'aprsep_exclude2020_lag_current_employer', 'former_employer_private_m0_3')}.",
        f"- Premium all paid, months 0-3: {fmt_est(est, 'aprsep_exclude2020_lag_current_employer', 'former_premium_all_paid_m0_3')}.",
        f"- Employer-related private coverage, months 0-3: {fmt_est(est, 'aprsep_exclude2020_lag_current_employer', 'employer_related_private_m0_3')}.",
        f"- Uninsured, months 0-3: {fmt_est(est, 'aprsep_exclude2020_lag_current_employer', 'uninsured_m0_3')}.",
        f"- Direct purchase, months 0-3: {fmt_est(est, 'aprsep_exclude2020_lag_current_employer', 'direct_purchase_m0_3')}.",
        f"- Market/subsidy proxy, months 0-3: {fmt_est(est, 'aprsep_exclude2020_lag_current_employer', 'market_or_subsidy_m0_3')}.",
        "",
        "Broad April-September sample, excluding 2020:",
        "",
        f"- Former-employer private coverage, months 0-3: {fmt_est(est, 'aprsep_exclude2020_all', 'former_employer_private_m0_3')}.",
        f"- Premium all paid, months 0-3: {fmt_est(est, 'aprsep_exclude2020_all', 'former_premium_all_paid_m0_3')}.",
        f"- Uninsured, months 0-3: {fmt_est(est, 'aprsep_exclude2020_all', 'uninsured_m0_3')}.",
        f"- Direct purchase, months 0-3: {fmt_est(est, 'aprsep_exclude2020_all', 'direct_purchase_m0_3')}.",
        "",
        "## Decision",
        "",
        f"`ARPA COBRA SUBSIDY: {verdict}`.",
        "",
        "Why this ranking:",
        "",
        "- The policy is clean and official, but the empirical estimand is not as clean as the 400% FPL cliff because COBRA is only proxied, not directly observed.",
        "- The main at-risk treated cell is the binding support check; if it is small, this cannot sustain a top-field standalone paper.",
        "- A credible positive result would need former-employer coverage or all-premium-paid coverage to rise after involuntary separations in the subsidy window, with uninsured falling or at least not rising.",
        "- Even if directional, this is more likely a mechanism extension to the ARPA private-coverage portfolio than a replacement for the 400% FPL lead.",
        "",
        "## Artifacts",
        "",
        "- `script/11_idea_scan/37_arpa_cobra_subsidy_test.py`",
        "- `report/74_arpa_cobra_subsidy_test.md`",
        "- `result/idea_scan/arpa_cobra_event_panel.parquet`",
        "- `result/idea_scan/arpa_cobra_support.csv`",
        "- `result/idea_scan/arpa_cobra_raw_cells.csv`",
        "- `result/idea_scan/arpa_cobra_estimates.csv`",
    ]
    REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    df = read_augmented_panel()
    d = add_constructs(df)
    event = build_event_panel(d)
    support, raw = support_tables(event)
    est = run_all_models(event)
    write_report(event, support, raw, est)
    print(f"Wrote {REPORT}")
    print(support.to_string(index=False))
    if not est.empty:
        cols = ["sample", "inv_col", "outcome", "coef_invol_x_subsidy", "se_person_cluster", "t_person_cluster", "treated_events", "treated_persons"]
        print(est[cols].to_string(index=False))


if __name__ == "__main__":
    main()
