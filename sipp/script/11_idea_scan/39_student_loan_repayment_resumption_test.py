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
SCRATCH = ROOT / "temp" / "scratch" / "student_loan_financial_vars_2018_2024.parquet"
OUT = ROOT / "result" / "idea_scan"
REPORT = ROOT / "report" / "78_student_loan_repayment_resumption_test.md"
DECISION = ROOT / "report" / "79_thirtyfirst_round_student_loan_repayment_decision.md"


SOURCES = [
    "GAO student loan repayment status blog: https://www.gao.gov/blog/when-student-loan-payment-pause-ended-did-borrowers-pay",
    "NCUA Letter to Credit Unions on resumption of federal student loan payments: https://ncua.gov/regulation-supervision/letters-credit-unions-other-guidance/resumption-federal-student-loan-payments",
    "U.S. Department of Education 2025 repayment/collections release: https://www.ed.gov/about/news/press-release/us-department-of-education-begin-federal-student-loan-collections-other-actions-help-borrowers-get-back-repayment",
]


RAW_COLS = [
    "SSUID",
    "PNUM",
    "MONTHCODE",
    "EDEBT_ED",
    "TDEBT_ED",
    "TOEDDEBTVAL",
    "EJSEDDEBT",
    "TJSEDDEBTVAL",
    "EDEBT_CC",
    "TDEBT_CC",
    "TOCCDEBTVAL",
    "EDEBT_MED",
    "TMED_AMT",
    "TDEBT_USEC",
    "TNETWORTH",
    "TVAL_BANK",
    "EAWBMORT",
    "EFOOD1",
    "EFOOD2",
    "EFOOD3",
    "EFOOD5",
    "EFOOD6",
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
    return w.where(w.gt(0))


def persons(s: pd.Series) -> int:
    return int(s.dropna().nunique())


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
        csv_name = [n for n in zf.namelist() if n.lower().endswith(".csv")][0]
        with zf.open(csv_name) as fh:
            return fh.readline().decode("utf-8", errors="replace").strip().split("|")


def extract_financial_vars() -> pd.DataFrame:
    if SCRATCH.exists():
        return pd.read_parquet(SCRATCH)

    SCRATCH.parent.mkdir(parents=True, exist_ok=True)
    writer: pq.ParquetWriter | None = None
    for file_year in range(2018, 2025):
        zpath = RAW / str(file_year) / "primary" / f"pu{file_year}_csv.zip"
        header = set(read_raw_header(file_year))
        usecols = [c for c in RAW_COLS if c in header]
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
            for col in RAW_COLS:
                if col not in out.columns:
                    out[col] = np.nan
            out = out[RAW_COLS + ["file_year"]]
            out["SSUID"] = out["SSUID"].astype("string")
            for col in out.columns:
                if col != "SSUID":
                    out[col] = pd.to_numeric(out[col], errors="coerce").astype("float64")
            out["PNUM"] = out["PNUM"].astype("Int64")
            out["MONTHCODE"] = out["MONTHCODE"].astype("Int64")
            out["file_year"] = out["file_year"].astype("int64")
            table = pa.Table.from_pandas(out, preserve_index=False)
            if writer is None:
                writer = pq.ParquetWriter(SCRATCH, table.schema, compression="snappy")
            writer.write_table(table)
    if writer is not None:
        writer.close()
    return pd.read_parquet(SCRATCH)


def build_annual_financial() -> pd.DataFrame:
    raw = extract_financial_vars()
    raw["person_id"] = raw["SSUID"].astype(str) + "-" + raw["PNUM"].astype(str)
    raw["reference_year"] = raw["file_year"].astype(int) - 1

    student_amount = bounded_numeric(raw["TDEBT_ED"], 0, 99_999_999)
    student_own_amount = bounded_numeric(raw["TOEDDEBTVAL"], 0, 9_999_999)
    student_joint_amount = bounded_numeric(raw["TJSEDDEBTVAL"], 0, 9_999_999)
    raw["student_debt"] = (
        yes(raw["EDEBT_ED"]) | student_amount.gt(0) | student_own_amount.gt(0) | student_joint_amount.gt(0)
    ).astype(float)
    raw["student_debt_amount"] = pd.concat([student_amount, student_own_amount, student_joint_amount], axis=1).max(axis=1)

    cc_amount = bounded_numeric(raw["TDEBT_CC"], 0, 99_999_999)
    cc_own_amount = bounded_numeric(raw["TOCCDEBTVAL"], 0, 9_999_999)
    raw["credit_card_debt"] = (yes(raw["EDEBT_CC"]) | cc_amount.gt(0) | cc_own_amount.gt(0)).astype(float)
    raw["credit_card_debt_amount"] = pd.concat([cc_amount, cc_own_amount], axis=1).max(axis=1)

    med_amount = bounded_numeric(raw["TMED_AMT"], 0, 9_999_999)
    raw["medical_debt"] = (yes(raw["EDEBT_MED"]) | med_amount.gt(0)).astype(float)
    raw["medical_debt_amount"] = med_amount

    raw["unsecured_debt_amount"] = bounded_numeric(raw["TDEBT_USEC"], 0, 99_999_999)
    raw["net_worth"] = bounded_numeric(raw["TNETWORTH"], -9_999_999_999, 9_999_999_999)
    raw["bank_assets"] = bounded_numeric(raw["TVAL_BANK"], 0, 99_999_999)
    raw["rent_mortgage_hardship"] = yes(raw["EAWBMORT"]).astype(float)
    raw["food_insecure"] = (
        num(raw["EFOOD1"]).isin([1, 2])
        | num(raw["EFOOD2"]).isin([1, 2])
        | yes(raw["EFOOD3"])
        | yes(raw["EFOOD5"])
        | yes(raw["EFOOD6"])
    ).astype(float)
    raw["food_severe"] = (
        yes(raw["EFOOD3"])
        | yes(raw["EFOOD5"])
        | yes(raw["EFOOD6"])
    ).astype(float)

    annual = (
        raw.groupby(["person_id", "reference_year"], observed=True)
        .agg(
            student_debt=("student_debt", "max"),
            student_debt_amount=("student_debt_amount", "max"),
            credit_card_debt=("credit_card_debt", "max"),
            credit_card_debt_amount=("credit_card_debt_amount", "max"),
            medical_debt=("medical_debt", "max"),
            medical_debt_amount=("medical_debt_amount", "max"),
            unsecured_debt_amount=("unsecured_debt_amount", "max"),
            net_worth=("net_worth", "median"),
            bank_assets=("bank_assets", "median"),
            rent_mortgage_hardship=("rent_mortgage_hardship", "max"),
            food_insecure=("food_insecure", "max"),
            food_severe=("food_severe", "max"),
        )
        .reset_index()
    )
    annual["log_student_debt_amount"] = np.log1p(annual["student_debt_amount"].fillna(0))
    annual["log_credit_card_debt_amount"] = np.log1p(annual["credit_card_debt_amount"].fillna(0))
    annual["log_medical_debt_amount"] = np.log1p(annual["medical_debt_amount"].fillna(0))
    annual["log_bank_assets"] = np.log1p(annual["bank_assets"].clip(lower=0).fillna(0))
    return annual


def read_monthly_panel() -> pd.DataFrame:
    cols = [
        "person_id",
        "person_month_key",
        "reference_year",
        "reference_month",
        "reference_date",
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
        "ECRMTH",
        "RPUBTYPE1",
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
        "TMDPAY",
        "TVISDOC",
        "TVISDENT",
        "THOSPNIT",
    ]
    df = pd.read_parquet(PANEL, columns=cols)
    df = df[df["reference_year"].between(2018, 2023)].copy()
    df["state_fips"] = df["state_fips"].astype("string").str.zfill(2)
    df["age"] = bounded_numeric(df["TAGE_EHC"], 0, 100)
    df["age"] = df["age"].where(df["age"].notna(), bounded_numeric(df["TAGE"], 0, 100))
    df["female"] = num(df["ESEX"]).eq(2).astype(float)
    df["black"] = num(df["ERACE"]).eq(2).astype(float)
    df["hispanic"] = (num(df["EORIGIN"]).eq(1) | num(df["EHISPAN"]).eq(1)).astype(float)
    df["disabled"] = yes(df["RDIS"]).astype(float)
    df["fpl"] = bounded_numeric(df["TFINCPOV"], 0, 20)
    df["annual_fpl"] = bounded_numeric(df["TFCYINCPOV"], 0, 20)
    df["weight"] = clean_weight(df)
    df["medicare"] = (yes(df["ECRMTH"]) | yes(df["RPUBTYPE1"])).astype(float)
    df["any_coverage"] = yes(df["RHLTHMTH"]).astype(float)
    df["uninsured"] = num(df["RHLTHMTH"]).eq(2).astype(float)
    df["private"] = yes(df["RPRIMTH"]).astype(float)
    df["public"] = yes(df["RPUBMTH"]).astype(float)
    df["medicaid"] = (yes(df["EMDMTH"]) | yes(df["RPUBTYPE2"])).astype(float)
    df["direct_market"] = (yes(df["RPRITYPE2"]) | yes(df["RMARKTPLACE"])).astype(float)
    df["exchange_subsidy"] = (
        yes(df["RMARKTPLACE"])
        | yes(df["EPRIEXCH1"])
        | yes(df["EPRIEXCH2"])
        | yes(df["EPRISUBS1"])
        | yes(df["EPRISUBS2"])
        | yes(df["EMDEXCH"])
        | yes(df["EMDSUBS"])
    ).astype(float)
    df["oop_amount"] = bounded_numeric(df["TMDPAY"], 0, 200_000)
    df["oop_any"] = df["oop_amount"].gt(0).astype(float)
    df["doctor_any"] = bounded_numeric(df["TVISDOC"], 0, 200).gt(0).astype(float)
    df["dental_any"] = bounded_numeric(df["TVISDENT"], 0, 100).gt(0).astype(float)
    df["hospital_any"] = bounded_numeric(df["THOSPNIT"], 0, 365).gt(0).astype(float)
    return df


def build_monthly_analysis(months: pd.DataFrame, annual: pd.DataFrame) -> pd.DataFrame:
    prev = annual.copy()
    prev["reference_year"] = prev["reference_year"].astype(int) + 1
    prev = prev.rename(columns={c: f"prev_{c}" for c in prev.columns if c not in ["person_id", "reference_year"]})

    df = months.merge(prev, on=["person_id", "reference_year"], how="left", validate="many_to_one")
    df = df[df["reference_year"].between(2019, 2023)].copy()
    df = df[df["reference_month"].isin([1, 2, 3, 4, 5, 6, 7, 8, 10, 11, 12])].copy()
    df["student_debt_prev"] = df["prev_student_debt"].fillna(0).astype(float)
    amount = df["prev_student_debt_amount"].fillna(0)
    df["student_debt_10k_prev"] = amount.gt(10_000).astype(float)
    df["student_debt_25k_prev"] = amount.gt(25_000).astype(float)
    df["oct_dec"] = df["reference_month"].isin([10, 11, 12]).astype(float)
    df["resume_2023"] = df["reference_year"].eq(2023).astype(float)
    df["post_resume_month"] = (df["resume_2023"].eq(1) & df["oct_dec"].eq(1)).astype(float)
    return df


def build_person_year(months: pd.DataFrame, annual: pd.DataFrame) -> pd.DataFrame:
    py = (
        months.groupby(["person_id", "state_fips", "reference_year"], observed=True)
        .agg(
            months=("person_month_key", "size"),
            weight=("weight", "mean"),
            age=("age", "mean"),
            fpl=("fpl", "median"),
            annual_fpl=("annual_fpl", "median"),
            female=("female", "mean"),
            black=("black", "mean"),
            hispanic=("hispanic", "mean"),
            disabled=("disabled", "mean"),
            medicare=("medicare", "mean"),
            any_coverage=("any_coverage", "mean"),
            uninsured=("uninsured", "mean"),
            private=("private", "mean"),
            public=("public", "mean"),
            medicaid=("medicaid", "mean"),
            direct_market=("direct_market", "mean"),
            exchange_subsidy=("exchange_subsidy", "mean"),
            oop_any=("oop_any", "mean"),
            oop_amount=("oop_amount", "mean"),
            doctor_any=("doctor_any", "mean"),
            dental_any=("dental_any", "mean"),
            hospital_any=("hospital_any", "mean"),
        )
        .reset_index()
    )
    py = py[py["months"].ge(6)].copy()
    py = py.merge(annual, on=["person_id", "reference_year"], how="left", validate="many_to_one")
    for col in [
        "student_debt",
        "credit_card_debt",
        "medical_debt",
        "rent_mortgage_hardship",
        "food_insecure",
        "food_severe",
    ]:
        py[col] = py[col].fillna(0).astype(float)
    for col in [
        "student_debt_amount",
        "credit_card_debt_amount",
        "medical_debt_amount",
        "unsecured_debt_amount",
        "bank_assets",
        "log_student_debt_amount",
        "log_credit_card_debt_amount",
        "log_medical_debt_amount",
        "log_bank_assets",
    ]:
        py[col] = py[col].fillna(0)
    return py


def build_annual_pairs(py: pd.DataFrame) -> pd.DataFrame:
    outcomes = [
        "food_insecure",
        "food_severe",
        "rent_mortgage_hardship",
        "medical_debt",
        "log_medical_debt_amount",
        "credit_card_debt",
        "log_credit_card_debt_amount",
        "log_bank_assets",
        "uninsured",
        "any_coverage",
        "private",
        "public",
        "medicaid",
        "direct_market",
        "exchange_subsidy",
        "oop_any",
        "doctor_any",
        "hospital_any",
    ]
    pyu = (
        py.sort_values(["person_id", "reference_year", "months", "weight"], ascending=[True, True, False, False])
        .drop_duplicates(["person_id", "reference_year"], keep="first")
        .copy()
    )
    by = {int(y): g.set_index("person_id") for y, g in pyu.groupby("reference_year", observed=True)}
    rows = []
    base_cols = [
        "state_fips",
        "reference_year",
        "weight",
        "age",
        "fpl",
        "annual_fpl",
        "female",
        "black",
        "hispanic",
        "disabled",
        "medicare",
        "student_debt",
        "student_debt_amount",
        "log_student_debt_amount",
        *outcomes,
    ]
    for y in [2018, 2019, 2020, 2021, 2022]:
        if y not in by or y + 1 not in by:
            continue
        idx = by[y].index.intersection(by[y + 1].index)
        b = by[y].loc[idx, base_cols].copy()
        f = by[y + 1].loc[idx, ["weight", *outcomes]].copy()
        pair = pd.DataFrame(index=idx)
        pair["person_id"] = idx
        pair["baseline_year"] = y
        pair["post_year"] = y + 1
        for col in base_cols:
            pair[col] = b[col].values
        pair["post_weight"] = f["weight"].values
        pair["analysis_weight"] = pair["weight"].where(pair["weight"].gt(0), pair["post_weight"])
        for outcome in outcomes:
            pair[f"{outcome}_base"] = b[outcome].values
            pair[f"{outcome}_post"] = f[outcome].values
            pair[f"d_{outcome}"] = pair[f"{outcome}_post"] - pair[f"{outcome}_base"]
        pair["actual_2022_2023"] = (y == 2022).astype(float) if hasattr(y == 2022, "astype") else float(y == 2022)
        pair["student_debt_base"] = pair["student_debt"].fillna(0).astype(float)
        amount = pair["student_debt_amount"].fillna(0)
        pair["student_debt_10k_base"] = amount.gt(10_000).astype(float)
        pair["student_debt_25k_base"] = amount.gt(25_000).astype(float)
        rows.append(pair.reset_index(drop=True))
    return pd.concat(rows, ignore_index=True)


def monthly_sample(df: pd.DataFrame) -> pd.DataFrame:
    s = df[
        df["age"].between(25, 64, inclusive="both")
        & df["medicare"].lt(0.5)
        & df["fpl"].between(0, 10, inclusive="both")
        & df["weight"].gt(0)
        & df["prev_student_debt"].notna()
    ].copy()
    return s


def annual_sample(pairs: pd.DataFrame) -> pd.DataFrame:
    s = pairs[
        pairs["age"].between(25, 64, inclusive="both")
        & pairs["medicare"].lt(0.5)
        & pairs["fpl"].between(0, 10, inclusive="both")
        & pairs["analysis_weight"].gt(0)
    ].copy()
    return s


def monthly_design_matrix(df: pd.DataFrame, exposure: str) -> tuple[pd.DataFrame, str]:
    exp = df[exposure].astype(float)
    octdec = df["oct_dec"].astype(float)
    y2023 = df["resume_2023"].astype(float)
    coef_name = f"{exposure}_x_octdec_x_2023"
    x = pd.DataFrame(index=df.index)
    x["intercept"] = 1.0
    x[coef_name] = exp * octdec * y2023
    x[f"{exposure}_x_octdec"] = exp * octdec
    x[f"{exposure}_x_2023"] = exp * y2023
    x["octdec_x_2023"] = octdec * y2023
    x[exposure] = exp
    x["octdec"] = octdec
    x["resume_2023"] = y2023
    x["age"] = df["age"].astype(float)
    x["age2"] = df["age"].astype(float) ** 2
    x["female"] = df["female"].astype(float)
    x["black"] = df["black"].astype(float)
    x["hispanic"] = df["hispanic"].astype(float)
    x["disabled"] = df["disabled"].astype(float)
    x["fpl"] = df["fpl"].clip(0, 10).astype(float)
    for col in ["reference_year", "reference_month", "state_fips"]:
        x = pd.concat([x, pd.get_dummies(df[col].astype("string"), prefix=col, drop_first=True, dtype=float)], axis=1)
    return x, coef_name


def annual_design_matrix(df: pd.DataFrame, exposure: str) -> tuple[pd.DataFrame, str]:
    exp = df[exposure].astype(float)
    actual = df["actual_2022_2023"].astype(float)
    coef_name = f"{exposure}_x_2022_2023"
    x = pd.DataFrame(index=df.index)
    x["intercept"] = 1.0
    x[coef_name] = exp * actual
    x[exposure] = exp
    x["actual_2022_2023"] = actual
    x["age"] = df["age"].astype(float)
    x["age2"] = df["age"].astype(float) ** 2
    x["female"] = df["female"].astype(float)
    x["black"] = df["black"].astype(float)
    x["hispanic"] = df["hispanic"].astype(float)
    x["disabled"] = df["disabled"].astype(float)
    x["fpl"] = df["fpl"].clip(0, 10).astype(float)
    for col in ["baseline_year", "state_fips"]:
        x = pd.concat([x, pd.get_dummies(df[col].astype("string"), prefix=col, drop_first=True, dtype=float)], axis=1)
    return x, coef_name


def run_monthly_models(s: pd.DataFrame) -> pd.DataFrame:
    outcomes = [
        "uninsured",
        "any_coverage",
        "private",
        "public",
        "medicaid",
        "direct_market",
        "exchange_subsidy",
        "oop_any",
        "doctor_any",
        "hospital_any",
    ]
    rows = []
    for exposure in ["student_debt_prev", "student_debt_10k_prev", "student_debt_25k_prev"]:
        if s[exposure].sum() < 100:
            continue
        x, coef_name = monthly_design_matrix(s, exposure)
        x_np = x.to_numpy(dtype=float)
        w = s["weight"].to_numpy(dtype=float)
        cluster = s["person_id"].astype(str).to_numpy()
        treated = s[s[exposure].eq(1) & s["post_resume_month"].eq(1)]
        for outcome in outcomes:
            y = s[outcome].to_numpy(dtype=float)
            beta, se_hc1, se_cl, n, g = weighted_ols_cluster(y, x_np, w, cluster)
            b = pd.Series(beta, index=x.columns)
            hc1 = pd.Series(se_hc1, index=x.columns)
            cl = pd.Series(se_cl, index=x.columns)
            rows.append(
                {
                    "model": "monthly_octdec_ddd",
                    "exposure": exposure,
                    "outcome": outcome,
                    "coef": b.get(coef_name, np.nan),
                    "se_hc1": hc1.get(coef_name, np.nan),
                    "t_hc1": b.get(coef_name, np.nan) / hc1.get(coef_name, np.nan)
                    if hc1.get(coef_name, np.nan) > 0
                    else np.nan,
                    "se_person_cluster": cl.get(coef_name, np.nan),
                    "t_person_cluster": b.get(coef_name, np.nan) / cl.get(coef_name, np.nan)
                    if cl.get(coef_name, np.nan) > 0
                    else np.nan,
                    "n": n,
                    "clusters_person": g,
                    "treated_post_months": int(len(treated)),
                    "treated_post_persons": persons(treated["person_id"]),
                    "n_states": int(s["state_fips"].nunique()),
                }
            )
    return pd.DataFrame(rows)


def run_annual_models(s: pd.DataFrame) -> pd.DataFrame:
    outcomes = [
        "d_food_insecure",
        "d_food_severe",
        "d_rent_mortgage_hardship",
        "d_medical_debt",
        "d_log_medical_debt_amount",
        "d_credit_card_debt",
        "d_log_credit_card_debt_amount",
        "d_log_bank_assets",
        "d_uninsured",
        "d_any_coverage",
        "d_direct_market",
        "d_exchange_subsidy",
        "d_oop_any",
        "d_doctor_any",
        "d_hospital_any",
    ]
    rows = []
    for exposure in ["student_debt_base", "student_debt_10k_base", "student_debt_25k_base"]:
        if s[exposure].sum() < 100:
            continue
        x, coef_name = annual_design_matrix(s, exposure)
        x_np = x.to_numpy(dtype=float)
        w = s["analysis_weight"].to_numpy(dtype=float)
        cluster = s["person_id"].astype(str).to_numpy()
        treated = s[s[exposure].eq(1) & s["actual_2022_2023"].eq(1)]
        for outcome in outcomes:
            y = s[outcome].to_numpy(dtype=float)
            beta, se_hc1, se_cl, n, g = weighted_ols_cluster(y, x_np, w, cluster)
            b = pd.Series(beta, index=x.columns)
            hc1 = pd.Series(se_hc1, index=x.columns)
            cl = pd.Series(se_cl, index=x.columns)
            rows.append(
                {
                    "model": "annual_pair_change_ddd",
                    "exposure": exposure,
                    "outcome": outcome,
                    "coef": b.get(coef_name, np.nan),
                    "se_hc1": hc1.get(coef_name, np.nan),
                    "t_hc1": b.get(coef_name, np.nan) / hc1.get(coef_name, np.nan)
                    if hc1.get(coef_name, np.nan) > 0
                    else np.nan,
                    "se_person_cluster": cl.get(coef_name, np.nan),
                    "t_person_cluster": b.get(coef_name, np.nan) / cl.get(coef_name, np.nan)
                    if cl.get(coef_name, np.nan) > 0
                    else np.nan,
                    "n": n,
                    "clusters_person": g,
                    "treated_post_months": np.nan,
                    "treated_post_persons": persons(treated["person_id"]),
                    "n_states": int(s["state_fips"].nunique()),
                }
            )
    return pd.DataFrame(rows)


def support_tables(monthly: pd.DataFrame, annual_pairs: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    support_rows = []
    for exposure in ["student_debt_prev", "student_debt_10k_prev", "student_debt_25k_prev"]:
        for year in [2019, 2020, 2021, 2022, 2023]:
            for octdec in [0.0, 1.0]:
                for exposed in [0.0, 1.0]:
                    cell = monthly[
                        monthly["reference_year"].eq(year)
                        & monthly["oct_dec"].eq(octdec)
                        & monthly[exposure].eq(exposed)
                    ]
                    support_rows.append(
                        {
                            "panel": "monthly",
                            "exposure": exposure,
                            "year": year,
                            "oct_dec": int(octdec),
                            "exposed": int(exposed),
                            "rows": int(len(cell)),
                            "persons": persons(cell["person_id"]),
                            "states": int(cell["state_fips"].nunique()) if len(cell) else 0,
                            "weighted_uninsured": wmean(cell["uninsured"], cell["weight"]) if len(cell) else np.nan,
                            "weighted_direct_market": wmean(cell["direct_market"], cell["weight"]) if len(cell) else np.nan,
                            "weighted_oop_any": wmean(cell["oop_any"], cell["weight"]) if len(cell) else np.nan,
                        }
                    )
    support = pd.DataFrame(support_rows)

    raw_rows = []
    for exposure in ["student_debt_prev", "student_debt_10k_prev", "student_debt_25k_prev"]:
        for y2023 in [0.0, 1.0]:
            for octdec in [0.0, 1.0]:
                for exposed in [0.0, 1.0]:
                    cell = monthly[
                        monthly["resume_2023"].eq(y2023)
                        & monthly["oct_dec"].eq(octdec)
                        & monthly[exposure].eq(exposed)
                    ]
                    row = {
                        "model": "monthly_octdec_ddd",
                        "exposure": exposure,
                        "resume_2023": int(y2023),
                        "oct_dec": int(octdec),
                        "exposed": int(exposed),
                        "rows": int(len(cell)),
                        "persons": persons(cell["person_id"]),
                    }
                    for outcome in [
                        "uninsured",
                        "any_coverage",
                        "private",
                        "public",
                        "direct_market",
                        "exchange_subsidy",
                        "oop_any",
                        "doctor_any",
                    ]:
                        row[outcome] = wmean(cell[outcome], cell["weight"]) if len(cell) else np.nan
                    raw_rows.append(row)

    for exposure in ["student_debt_base", "student_debt_10k_base", "student_debt_25k_base"]:
        for actual in [0.0, 1.0]:
            for exposed in [0.0, 1.0]:
                cell = annual_pairs[annual_pairs["actual_2022_2023"].eq(actual) & annual_pairs[exposure].eq(exposed)]
                row = {
                    "model": "annual_pair_change_ddd",
                    "exposure": exposure,
                    "resume_2023": int(actual),
                    "oct_dec": np.nan,
                    "exposed": int(exposed),
                    "rows": int(len(cell)),
                    "persons": persons(cell["person_id"]),
                }
                for outcome in [
                    "d_food_insecure",
                    "d_rent_mortgage_hardship",
                    "d_medical_debt",
                    "d_credit_card_debt",
                    "d_uninsured",
                    "d_direct_market",
                    "d_oop_any",
                    "d_doctor_any",
                ]:
                    row[outcome] = wmean(cell[outcome], cell["analysis_weight"]) if len(cell) else np.nan
                raw_rows.append(row)
    raw = pd.DataFrame(raw_rows)

    annual_support_rows = []
    for exposure in ["student_debt_base", "student_debt_10k_base", "student_debt_25k_base"]:
        for actual in [0.0, 1.0]:
            for exposed in [0.0, 1.0]:
                cell = annual_pairs[annual_pairs["actual_2022_2023"].eq(actual) & annual_pairs[exposure].eq(exposed)]
                annual_support_rows.append(
                    {
                        "panel": "annual_pairs",
                        "exposure": exposure,
                        "actual_2022_2023": int(actual),
                        "exposed": int(exposed),
                        "pairs": int(len(cell)),
                        "persons": persons(cell["person_id"]),
                        "states": int(cell["state_fips"].nunique()) if len(cell) else 0,
                        "mean_student_debt_amount_base": wmean(cell["student_debt_amount"], cell["analysis_weight"])
                        if len(cell)
                        else np.nan,
                    }
                )
    annual_support = pd.DataFrame(annual_support_rows)
    return support, raw, annual_support


def fmt_est(estimates: pd.DataFrame, model: str, exposure: str, outcome: str) -> str:
    r = estimates[
        estimates["model"].eq(model)
        & estimates["exposure"].eq(exposure)
        & estimates["outcome"].eq(outcome)
    ]
    if r.empty:
        return "NA"
    row = r.iloc[0]
    return (
        f"{row['coef']:+.4f} "
        f"(person-cluster se {row['se_person_cluster']:.4f}, t {row['t_person_cluster']:.2f}; "
        f"treated post persons {int(row['treated_post_persons'])})"
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


def write_outputs(
    monthly: pd.DataFrame,
    annual_pairs: pd.DataFrame,
    support: pd.DataFrame,
    raw: pd.DataFrame,
    annual_support: pd.DataFrame,
    estimates: pd.DataFrame,
) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    monthly.to_parquet(OUT / "student_loan_repayment_monthly_panel.parquet", index=False)
    annual_pairs.to_parquet(OUT / "student_loan_repayment_annual_pairs.parquet", index=False)
    support.to_csv(OUT / "student_loan_repayment_support.csv", index=False)
    raw.to_csv(OUT / "student_loan_repayment_raw_cells.csv", index=False)
    annual_support.to_csv(OUT / "student_loan_repayment_annual_support.csv", index=False)
    estimates.to_csv(OUT / "student_loan_repayment_estimates.csv", index=False)

    main_support = support[
        support["exposure"].eq("student_debt_prev")
        & support["year"].eq(2023)
        & support["oct_dec"].eq(1)
        & support["exposed"].eq(1)
    ]
    post_months = int(main_support.iloc[0]["rows"]) if not main_support.empty else 0
    post_persons = int(main_support.iloc[0]["persons"]) if not main_support.empty else 0
    annual_actual = annual_support[
        annual_support["exposure"].eq("student_debt_base")
        & annual_support["actual_2022_2023"].eq(1)
        & annual_support["exposed"].eq(1)
    ]
    annual_post_persons = int(annual_actual.iloc[0]["persons"]) if not annual_actual.empty else 0

    report = [
        "# Student Loan Repayment Resumption SIPP Screen",
        "",
        "## Question",
        "",
        "Can SIPP support a publishable adult-policy causal design around the resumption of federal student loan payments in October 2023, using prior student-loan debt holders as the exposed group and measuring coverage, care use, medical spending, and hardship outcomes?",
        "",
        "## Source Checks",
        "",
    ]
    report += [f"- {s}" for s in SOURCES]
    report += [
        "",
        "Policy timing used here: the pandemic-era federal student loan payment pause ended before the 2023 repayment restart; interest resumed in September 2023 and payments restarted in October 2023. Federal agencies also described an October 2023-September 2024 on-ramp, which weakens immediate delinquency consequences and makes a large short-run SIPP signal less likely.",
        "",
        "## Construction",
        "",
        "- Base panel: `data/analysis_ready/sipp_2018_2024_person_month_panel.parquet`.",
        "- Raw financial supplement: `temp/scratch/student_loan_financial_vars_2018_2024.parquet`.",
        "- Exposure: prior-year student/education debt from `EDEBT_ED`, `TDEBT_ED`, `TOEDDEBTVAL`, and joint education-debt fields.",
        "- Main monthly design: adult non-Medicare person-months age 25-64, years 2019-2023, excluding September; key coefficient is prior student debt x October-December x 2023.",
        "- Annual-pair design: changes from baseline year to following year, with the 2022->2023 pair as the treated restart pair.",
        "- Outcomes: insurance coverage, direct-market/exchange proxies, annual health care use/spending proxies, rent/mortgage hardship, food insecurity, medical debt, credit-card debt, and bank assets.",
        "",
        "Measurement caveat: SIPP observes student/education debt, not federal-loan repayment obligation, servicer status, monthly payment due, SAVE/IDR enrollment, delinquency, default, or the exact restart month for each borrower. This is a major identification limitation.",
        "",
        "## Support",
        "",
        f"- 2023 October-December monthly exposed support: {post_months:,} person-months; {post_persons:,} persons.",
        f"- 2022->2023 annual-pair exposed support: {annual_post_persons:,} persons.",
        "",
        md_table(
            support[
                support["exposure"].eq("student_debt_prev")
                & support["year"].isin([2022, 2023])
            ],
            [
                "panel",
                "exposure",
                "year",
                "oct_dec",
                "exposed",
                "rows",
                "persons",
                "states",
                "weighted_uninsured",
                "weighted_direct_market",
                "weighted_oop_any",
            ],
            max_rows=12,
        ),
        "",
        "## Raw Cells",
        "",
        md_table(
            raw[
                raw["exposure"].eq("student_debt_prev")
                & raw["model"].eq("monthly_octdec_ddd")
            ],
            [
                "model",
                "exposure",
                "resume_2023",
                "oct_dec",
                "exposed",
                "rows",
                "persons",
                "uninsured",
                "direct_market",
                "oop_any",
                "doctor_any",
            ],
            max_rows=8,
        ),
        "",
        "## Monthly DDD Estimates",
        "",
        "Main exposure: prior-year student debt. Coefficients are on `student_debt_prev x Oct-Dec x 2023`.",
        "",
        f"- Uninsured: {fmt_est(estimates, 'monthly_octdec_ddd', 'student_debt_prev', 'uninsured')}.",
        f"- Any coverage: {fmt_est(estimates, 'monthly_octdec_ddd', 'student_debt_prev', 'any_coverage')}.",
        f"- Direct-market coverage: {fmt_est(estimates, 'monthly_octdec_ddd', 'student_debt_prev', 'direct_market')}.",
        f"- Exchange/subsidy proxy: {fmt_est(estimates, 'monthly_octdec_ddd', 'student_debt_prev', 'exchange_subsidy')}.",
        f"- OOP-any proxy: {fmt_est(estimates, 'monthly_octdec_ddd', 'student_debt_prev', 'oop_any')}.",
        f"- Doctor-any proxy: {fmt_est(estimates, 'monthly_octdec_ddd', 'student_debt_prev', 'doctor_any')}.",
        "",
        "High-debt sensitivity, prior student debt > $25,000:",
        "",
        f"- Uninsured: {fmt_est(estimates, 'monthly_octdec_ddd', 'student_debt_25k_prev', 'uninsured')}.",
        f"- OOP-any proxy: {fmt_est(estimates, 'monthly_octdec_ddd', 'student_debt_25k_prev', 'oop_any')}.",
        f"- Doctor-any proxy: {fmt_est(estimates, 'monthly_octdec_ddd', 'student_debt_25k_prev', 'doctor_any')}.",
        "",
        "## Annual-Pair Estimates",
        "",
        "Main exposure: baseline student debt. Coefficients are on `student_debt_base x 2022->2023`.",
        "",
        f"- Food insecurity change: {fmt_est(estimates, 'annual_pair_change_ddd', 'student_debt_base', 'd_food_insecure')}.",
        f"- Rent/mortgage hardship change: {fmt_est(estimates, 'annual_pair_change_ddd', 'student_debt_base', 'd_rent_mortgage_hardship')}.",
        f"- Medical debt change: {fmt_est(estimates, 'annual_pair_change_ddd', 'student_debt_base', 'd_medical_debt')}.",
        f"- Credit-card debt change: {fmt_est(estimates, 'annual_pair_change_ddd', 'student_debt_base', 'd_credit_card_debt')}.",
        f"- Uninsured change: {fmt_est(estimates, 'annual_pair_change_ddd', 'student_debt_base', 'd_uninsured')}.",
        f"- Direct-market change: {fmt_est(estimates, 'annual_pair_change_ddd', 'student_debt_base', 'd_direct_market')}.",
        "",
        "## Decision",
        "",
        "`STUDENT LOAN REPAYMENT RESUMPTION: NO-GO AS MAIN SIPP HEALTH-INSURANCE PAPER`.",
        "",
        "The event is nationally important and the exposed sample is large enough, but SIPP lacks the decisive exposure and outcome variables for a top-field causal paper. The policy shock is federal, timing is concentrated in only three observable post-restart months, the on-ramp intentionally muted immediate adverse credit consequences, and public SIPP cannot separate federal loans from private education debt or observe actual payment-due changes.",
        "",
        "This can be a discarded diagnostic or a short descriptive appendix about household financial strain among debt holders, but it should not displace the ARPA 400% FPL subsidy-cliff design.",
        "",
        "## Artifacts",
        "",
        "- `script/11_idea_scan/39_student_loan_repayment_resumption_test.py`",
        "- `report/78_student_loan_repayment_resumption_test.md`",
        "- `report/79_thirtyfirst_round_student_loan_repayment_decision.md`",
        "- `result/idea_scan/student_loan_repayment_monthly_panel.parquet`",
        "- `result/idea_scan/student_loan_repayment_annual_pairs.parquet`",
        "- `result/idea_scan/student_loan_repayment_estimates.csv`",
        "- `result/idea_scan/student_loan_repayment_support.csv`",
        "- `result/idea_scan/student_loan_repayment_raw_cells.csv`",
        "- `result/idea_scan/student_loan_repayment_annual_support.csv`",
    ]
    REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")

    decision = [
        "# Thirty-First Round Decision: Student Loan Repayment Resumption",
        "",
        "## Verdict",
        "",
        "`NO-GO AS MAIN SIPP HEALTH-INSURANCE PAPER`",
        "",
        "The student loan repayment restart is a strong current-policy hook, but it is not a strong SIPP health-insurance causal paper with the current public data.",
        "",
        "## Why It Was Worth Testing",
        "",
        "- The repayment restart is recent and nationally salient.",
        "- SIPP has student/education debt variables from 2018-2024 and household hardship/debt outcomes.",
        "- The event timing is sharp at the national level: interest resumed in September 2023 and payments restarted in October 2023.",
        "",
        "## Main Empirical Problem",
        "",
        "SIPP does not observe the policy exposure cleanly. The key variables identify education debt, not federal repayment restart exposure. There is no monthly required payment, no federal/private distinction, no SAVE/IDR status, no servicer delinquency/default status, and only October-December 2023 is observed after repayment restart.",
        "",
        "## Support",
        "",
        f"- 2023 October-December exposed support: {post_months:,} person-months; {post_persons:,} persons.",
        f"- 2022->2023 exposed annual-pair support: {annual_post_persons:,} persons.",
        "",
        "The sample is not the limiting factor. The limiting factor is exposure validity and short post-period timing.",
        "",
        "## Results Summary",
        "",
        f"- Monthly uninsured: {fmt_est(estimates, 'monthly_octdec_ddd', 'student_debt_prev', 'uninsured')}.",
        f"- Monthly direct-market: {fmt_est(estimates, 'monthly_octdec_ddd', 'student_debt_prev', 'direct_market')}.",
        f"- Monthly OOP-any proxy: {fmt_est(estimates, 'monthly_octdec_ddd', 'student_debt_prev', 'oop_any')}.",
        f"- Annual food insecurity: {fmt_est(estimates, 'annual_pair_change_ddd', 'student_debt_base', 'd_food_insecure')}.",
        f"- Annual rent/mortgage hardship: {fmt_est(estimates, 'annual_pair_change_ddd', 'student_debt_base', 'd_rent_mortgage_hardship')}.",
        f"- Annual medical debt: {fmt_est(estimates, 'annual_pair_change_ddd', 'student_debt_base', 'd_medical_debt')}.",
        "",
        "Even if some coefficients move, they would be hard to interpret causally because the true repayment exposure is not measured and the restart coincides with broad 2023 macro and household-finance changes.",
        "",
        "## Ranking Implication",
        "",
        "This does not change the current lead ranking:",
        "",
        "1. ARPA 400% FPL subsidy-cliff removal remains the best SIPP lead.",
        "2. Late Medicaid expansion 100-138% FPL bridge remains the strongest Medicaid/uninsurance backup.",
        "3. ARPA UI / broader ARPA Marketplace affordability variants remain useful extensions.",
        "4. Family glitch, COBRA, and student-loan repayment restart should remain discarded diagnostics unless new direct exposure variables are added from outside SIPP.",
        "",
        "## Next Move",
        "",
        "The next productive step is not to rescue this student-loan idea. The practical path is to sharpen the ARPA 400% FPL design: rebuild the analysis-ready panel with employer-related private coverage/source fields such as `RPRITYPE1` or the raw `EHEMPLY` source variables, then separate direct-purchase uptake from employer coverage substitution.",
    ]
    DECISION.write_text("\n".join(decision) + "\n", encoding="utf-8")


def main() -> None:
    annual = build_annual_financial()
    months = read_monthly_panel()
    monthly = monthly_sample(build_monthly_analysis(months, annual))
    py = build_person_year(months, annual)
    annual_pairs = annual_sample(build_annual_pairs(py))
    support, raw, annual_support = support_tables(monthly, annual_pairs)
    monthly_est = run_monthly_models(monthly)
    annual_est = run_annual_models(annual_pairs)
    estimates = pd.concat([monthly_est, annual_est], ignore_index=True)
    write_outputs(monthly, annual_pairs, support, raw, annual_support, estimates)
    print(f"Wrote {REPORT}")
    print(f"Wrote {DECISION}")
    print(support[support["year"].isin([2022, 2023])].head(16).to_string(index=False))
    print(estimates[["model", "exposure", "outcome", "coef", "se_person_cluster", "t_person_cluster", "treated_post_persons"]].to_string(index=False))


if __name__ == "__main__":
    main()
