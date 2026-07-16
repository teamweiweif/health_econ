from __future__ import annotations

from pathlib import Path
import zipfile

import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq


ROOT = Path(__file__).resolve().parents[2]
PANEL = ROOT / "data" / "analysis_ready" / "sipp_2018_2024_person_month_panel.parquet"
SCRATCH = ROOT / "temp" / "scratch" / "immigration_status_2018_2024.parquet"
OUT = ROOT / "result" / "idea_scan"
REPORT = ROOT / "report" / "63_public_charge_immigrant_chilling_test.md"


SUPPLEMENTAL_COLS = [
    "SSUID",
    "PNUM",
    "MONTHCODE",
    "ECITIZEN",
    "ACITIZEN",
    "EBORNUS",
    "ABORNUS",
    "ENATCIT",
    "ANATCIT",
]


def parse_int(raw: bytes) -> int | None:
    raw = raw.strip()
    if not raw:
        return None
    try:
        return int(raw)
    except ValueError:
        return None


def extract_immigration_status() -> pd.DataFrame:
    if SCRATCH.exists():
        return pd.read_parquet(SCRATCH)

    SCRATCH.parent.mkdir(parents=True, exist_ok=True)
    writer: pq.ParquetWriter | None = None
    total_rows = 0
    for year in range(2018, 2025):
        zip_path = ROOT / "temp" / "raw_downloads" / "census_sipp" / str(year) / "primary" / f"pu{year}_csv.zip"
        with zipfile.ZipFile(zip_path) as zf:
            csv_name = [name for name in zf.namelist() if name.lower().endswith(".csv")][0]
            with zf.open(csv_name, "r") as fh:
                header = fh.readline().decode("utf-8").rstrip("\r\n").split("|")
                indices = {col: header.index(col) for col in SUPPLEMENTAL_COLS}
                max_idx = max(indices.values())
                store: dict[str, list] = {col: [] for col in SUPPLEMENTAL_COLS}
                row_count = 0
                for line in fh:
                    parts = line.rstrip(b"\r\n").split(b"|", maxsplit=max_idx + 1)
                    for col in SUPPLEMENTAL_COLS:
                        idx = indices[col]
                        raw = parts[idx] if idx < len(parts) else b""
                        if col == "SSUID":
                            store[col].append(raw.decode("ascii", errors="ignore"))
                        else:
                            store[col].append(parse_int(raw))
                    row_count += 1
        df = pd.DataFrame(store)
        df["file_year"] = year
        for col in ["PNUM", "MONTHCODE", "ECITIZEN", "ACITIZEN", "EBORNUS", "ABORNUS", "ENATCIT", "ANATCIT"]:
            df[col] = pd.to_numeric(df[col], errors="coerce").astype("Int64")
        df["file_year"] = df["file_year"].astype("int16")
        table = pa.Table.from_pandas(df, preserve_index=False)
        if writer is None:
            writer = pq.ParquetWriter(SCRATCH, table.schema, compression="snappy")
        writer.write_table(table)
        total_rows += row_count
        print(f"extracted {year}: {row_count:,} rows", flush=True)
    if writer is not None:
        writer.close()
    print(f"wrote {SCRATCH} with {total_rows:,} rows", flush=True)
    return pd.read_parquet(SCRATCH)


def yes(s: pd.Series) -> pd.Series:
    return pd.to_numeric(s, errors="coerce").eq(1)


def bounded_numeric(s: pd.Series, lo: float, hi: float) -> pd.Series:
    out = pd.to_numeric(s, errors="coerce")
    return out.where(out.between(lo, hi, inclusive="both"))


def clean_weight(df: pd.DataFrame) -> pd.Series:
    w = pd.to_numeric(df.get("WPFINWGT"), errors="coerce")
    return w.where(w.gt(0))


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


def read_augmented_panel() -> pd.DataFrame:
    cols = [
        "SSUID",
        "PNUM",
        "MONTHCODE",
        "file_year",
        "reference_year",
        "reference_month",
        "state_fips",
        "person_id",
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
        "RTANF_MNYN",
        "RSSI_MNYN",
        "TFINCPOV",
        "TFCYINCPOV",
    ]
    base = pd.read_parquet(PANEL, columns=cols)
    imm = extract_immigration_status()
    base["SSUID"] = base["SSUID"].astype(str)
    imm["SSUID"] = imm["SSUID"].astype(str)
    for col in ["PNUM", "MONTHCODE"]:
        base[col] = pd.to_numeric(base[col], errors="coerce").astype("Int64")
        imm[col] = pd.to_numeric(imm[col], errors="coerce").astype("Int64")
    base["file_year"] = pd.to_numeric(base["file_year"], errors="coerce").astype("int16")
    imm["file_year"] = pd.to_numeric(imm["file_year"], errors="coerce").astype("int16")
    return base.merge(imm, on=["file_year", "SSUID", "PNUM", "MONTHCODE"], how="left", validate="one_to_one")


def prep(df: pd.DataFrame, fpl_col: str, low_cut: float) -> tuple[pd.DataFrame, pd.DataFrame]:
    d = df.copy()
    d["state_fips"] = d["state_fips"].astype(str).str.zfill(2)
    d["age"] = bounded_numeric(d["TAGE"], 0, 100)
    d["female"] = pd.to_numeric(d["ESEX"], errors="coerce").eq(2).astype(float)
    d["black"] = pd.to_numeric(d["ERACE"], errors="coerce").eq(2).astype(float)
    d["hispanic"] = (yes(d["EORIGIN"]) | yes(d.get("EHISPAN"))).astype(float)
    d["disabled"] = yes(d["RDIS"]).astype(float)
    d["medicare"] = yes(d["RPUBTYPE1"]).astype(float)
    d["monthly_fpl"] = bounded_numeric(d["TFINCPOV"], 0, 10)
    d["annual_fpl"] = bounded_numeric(d["TFCYINCPOV"], 0, 10)
    d["weight"] = clean_weight(d)
    d["ym"] = d["reference_year"].astype(int).astype(str) + "-" + d["reference_month"].astype(int).astype(str).str.zfill(2)

    d["citizenship_valid"] = pd.to_numeric(d["ECITIZEN"], errors="coerce").isin([1, 2]).astype(int)
    d["noncitizen"] = pd.to_numeric(d["ECITIZEN"], errors="coerce").eq(2).astype(float)
    d["citizen"] = pd.to_numeric(d["ECITIZEN"], errors="coerce").eq(1).astype(float)
    d["foreign_born"] = pd.to_numeric(d["EBORNUS"], errors="coerce").eq(2).astype(float)
    d["naturalized_or_derived"] = pd.to_numeric(d["ENATCIT"], errors="coerce").isin([1, 2]).astype(float)

    d["any_coverage"] = yes(d["RHLTHMTH"]).astype(float)
    d["uninsured"] = pd.to_numeric(d["RHLTHMTH"], errors="coerce").eq(2).astype(float)
    d["private"] = yes(d["RPRIMTH"]).astype(float)
    d["public"] = yes(d["RPUBMTH"]).astype(float)
    d["medicaid"] = (yes(d["EMDMTH"]) | yes(d["RPUBTYPE2"])).astype(float)
    d["direct_purchase"] = (yes(d["RPRITYPE2"]) | yes(d["RMARKTPLACE"])).astype(float)
    d["marketplace_flag"] = (
        yes(d["RMARKTPLACE"]) | yes(d["EPRIEXCH1"]) | yes(d["EPRIEXCH2"]) | yes(d["EMDEXCH"])
    ).astype(float)
    d["market_or_subsidy"] = (
        d["direct_purchase"].eq(1)
        | d["marketplace_flag"].eq(1)
        | yes(d["EPRISUBS1"])
        | yes(d["EPRISUBS2"])
        | yes(d["EMDSUBS"])
    ).astype(float)
    d["snap_month"] = yes(d["RSNAP_MNYN"]).astype(float)
    d["tanf_month"] = yes(d["RTANF_MNYN"]).astype(float)
    d["ssi_month"] = yes(d["RSSI_MNYN"]).astype(float)

    d["chill_2019_2020"] = d["reference_year"].between(2019, 2020, inclusive="both").astype(float)
    d["reversal_2021_2023"] = d["reference_year"].between(2021, 2023, inclusive="both").astype(float)
    d["implementation_2020"] = d["reference_year"].eq(2020).astype(float)
    d["low_income"] = d[fpl_col].le(low_cut).astype(float)
    d["noncitizen_low"] = d["noncitizen"] * d["low_income"]
    d["noncitizen_chill"] = d["noncitizen"] * d["chill_2019_2020"]
    d["low_chill"] = d["low_income"] * d["chill_2019_2020"]
    d["noncitizen_low_chill"] = d["noncitizen"] * d["low_income"] * d["chill_2019_2020"]
    d["noncitizen_reversal"] = d["noncitizen"] * d["reversal_2021_2023"]
    d["low_reversal"] = d["low_income"] * d["reversal_2021_2023"]
    d["noncitizen_low_reversal"] = d["noncitizen"] * d["low_income"] * d["reversal_2021_2023"]
    d["noncitizen_impl2020"] = d["noncitizen"] * d["implementation_2020"]
    d["low_impl2020"] = d["low_income"] * d["implementation_2020"]
    d["noncitizen_low_impl2020"] = d["noncitizen"] * d["low_income"] * d["implementation_2020"]

    s = d[
        d["citizenship_valid"].eq(1)
        & d["age"].between(19, 64, inclusive="both")
        & d["medicare"].ne(1)
        & d[fpl_col].between(0, 6.0, inclusive="both")
        & d["weight"].gt(0)
    ].copy()

    parts: list[pd.Series | pd.DataFrame] = [
        pd.Series(1.0, index=s.index, name="const"),
        s["noncitizen"].rename("noncitizen"),
        s["low_income"].rename("low_income"),
        s["noncitizen_low"].rename("noncitizen_low"),
        s["noncitizen_chill"].rename("noncitizen_chill"),
        s["low_chill"].rename("low_chill"),
        s["noncitizen_low_chill"].rename("noncitizen_low_chill"),
        s["noncitizen_reversal"].rename("noncitizen_reversal"),
        s["low_reversal"].rename("low_reversal"),
        s["noncitizen_low_reversal"].rename("noncitizen_low_reversal"),
        s[fpl_col].rename("fpl"),
        (s[fpl_col] ** 2).rename("fpl_sq"),
        s["age"].rename("age"),
        (s["age"] ** 2).rename("age_sq"),
        s["female"].rename("female"),
        s["black"].rename("black"),
        s["hispanic"].rename("hispanic"),
        s["disabled"].rename("disabled"),
    ]
    parts.append(pd.get_dummies(s["state_fips"].astype(str), prefix="state", drop_first=True, dtype=float))
    parts.append(pd.get_dummies(s["ym"].astype(str), prefix="ym", drop_first=True, dtype=float))
    x = pd.concat(parts, axis=1)
    return s, x


def estimate(s: pd.DataFrame, x: pd.DataFrame, outcomes: list[str], spec: str) -> pd.DataFrame:
    rows = []
    x_np = x.to_numpy(dtype=float)
    w_np = s["weight"].to_numpy(dtype=float)
    state_cluster = s["state_fips"].to_numpy()
    person_cluster = s["person_id"].to_numpy()
    terms = ["noncitizen_low_chill", "noncitizen_low_reversal"]
    for outcome in outcomes:
        y = s[outcome].to_numpy(dtype=float)
        beta, se_hc1, se_state, n, g_state = weighted_ols_cluster(y, x_np, w_np, state_cluster)
        _, _, se_person, _, g_person = weighted_ols_cluster(y, x_np, w_np, person_cluster)
        b = pd.Series(beta, index=x.columns)
        hc1 = pd.Series(se_hc1, index=x.columns)
        st = pd.Series(se_state, index=x.columns)
        ps = pd.Series(se_person, index=x.columns)
        for term in terms:
            coef = b.get(term, np.nan)
            rows.append(
                {
                    "spec": spec,
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
                    "persons": int(s["person_id"].nunique()),
                    "states": int(s["state_fips"].nunique()),
                    "state_clusters": g_state,
                    "person_clusters": g_person,
                    "weighted_mean": wmean(s[outcome], s["weight"]),
                }
            )
    return pd.DataFrame(rows)


def support_tables(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    status = []
    for col in ["ECITIZEN", "EBORNUS", "ENATCIT", "ACITIZEN", "ABORNUS", "ANATCIT"]:
        vc = pd.to_numeric(df[col], errors="coerce").value_counts(dropna=False).sort_index()
        for value, n in vc.items():
            status.append({"variable": col, "value": value, "rows": int(n)})
    status_df = pd.DataFrame(status)

    d = df.copy()
    d["period"] = np.select(
        [
            d["reference_year"].between(2017, 2018, inclusive="both"),
            d["reference_year"].between(2019, 2020, inclusive="both"),
            d["reference_year"].between(2021, 2023, inclusive="both"),
        ],
        ["pre_2017_2018", "chill_2019_2020", "reversal_2021_2023"],
        default="other",
    )
    d["low250"] = bounded_numeric(d["TFINCPOV"], 0, 10).le(2.5).astype(int)
    d["noncitizen"] = pd.to_numeric(d["ECITIZEN"], errors="coerce").eq(2).astype(int)
    d["age"] = bounded_numeric(d["TAGE"], 0, 100)
    d["medicare"] = yes(d["RPUBTYPE1"]).astype(float)
    d["weight"] = clean_weight(d)
    for outcome, expr in {
        "medicaid": (yes(d["EMDMTH"]) | yes(d["RPUBTYPE2"])).astype(float),
        "snap_month": yes(d["RSNAP_MNYN"]).astype(float),
        "uninsured": pd.to_numeric(d["RHLTHMTH"], errors="coerce").eq(2).astype(float),
        "public": yes(d["RPUBMTH"]).astype(float),
        "private": yes(d["RPRIMTH"]).astype(float),
    }.items():
        d[outcome] = expr
    d = d[
        pd.to_numeric(d["ECITIZEN"], errors="coerce").isin([1, 2])
        & d["age"].between(19, 64, inclusive="both")
        & d["medicare"].ne(1)
        & bounded_numeric(d["TFINCPOV"], 0, 10).between(0, 6, inclusive="both")
        & d["weight"].gt(0)
    ].copy()
    cell_rows = []
    for (period, noncit, low), g in d.groupby(["period", "noncitizen", "low250"], observed=True):
        if period == "other":
            continue
        row = {
            "period": period,
            "noncitizen": int(noncit),
            "low250": int(low),
            "person_months": int(len(g)),
            "persons": int(g["person_id"].nunique()),
            "states": int(g["state_fips"].nunique()),
        }
        for outcome in ["medicaid", "snap_month", "uninsured", "public", "private"]:
            row[outcome] = wmean(g[outcome], g["weight"])
        cell_rows.append(row)
    cell_df = pd.DataFrame(cell_rows).sort_values(["period", "noncitizen", "low250"])

    person_support = (
        d.groupby(["period", "noncitizen"], observed=True)
        .agg(person_months=("person_id", "size"), persons=("person_id", "nunique"), states=("state_fips", "nunique"))
        .reset_index()
    )
    return status_df, cell_df, person_support


def md_table(df: pd.DataFrame, cols: list[str], max_rows: int | None = None) -> str:
    d = df[cols].copy()
    if max_rows is not None:
        d = d.head(max_rows)
    lines = ["| " + " | ".join(cols) + " |", "|" + "|".join(["---"] * len(cols)) + "|"]
    for _, r in d.iterrows():
        vals = []
        for c in cols:
            v = r[c]
            if isinstance(v, float):
                vals.append("" if np.isnan(v) else f"{v:.4f}")
            else:
                vals.append(str(v))
        lines.append("| " + " | ".join(vals) + " |")
    return "\n".join(lines)


def fmt(est: pd.DataFrame, spec: str, term: str, outcomes: list[str]) -> str:
    d = est[(est["spec"].eq(spec)) & (est["term"].eq(term))].set_index("outcome")
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
    df = read_augmented_panel()
    status_df, cell_df, person_support = support_tables(df)
    status_df.to_csv(OUT / "public_charge_status_value_counts.csv", index=False)
    cell_df.to_csv(OUT / "public_charge_cell_means.csv", index=False)
    person_support.to_csv(OUT / "public_charge_person_support.csv", index=False)

    outcomes = [
        "medicaid",
        "snap_month",
        "public",
        "uninsured",
        "any_coverage",
        "private",
        "direct_purchase",
        "marketplace_flag",
        "market_or_subsidy",
        "tanf_month",
        "ssi_month",
    ]
    specs = [("monthly_low250", "monthly_fpl", 2.5), ("monthly_low150", "monthly_fpl", 1.5), ("annual_low250", "annual_fpl", 2.5)]
    estimates = []
    support_rows = []
    for spec_name, fpl_col, low_cut in specs:
        s, x = prep(df, fpl_col, low_cut)
        estimates.append(estimate(s, x, outcomes, spec_name))
        support_rows.append(
            {
                "spec": spec_name,
                "fpl_col": fpl_col,
                "low_cut": low_cut,
                "person_months": int(len(s)),
                "persons": int(s["person_id"].nunique()),
                "states": int(s["state_fips"].nunique()),
                "noncitizen_person_months": int(s["noncitizen"].sum()),
                "low_noncitizen_person_months": int((s["noncitizen"] * s["low_income"]).sum()),
                "low_noncitizen_persons": int(s.loc[s["noncitizen"].eq(1) & s["low_income"].eq(1), "person_id"].nunique()),
            }
        )
    est = pd.concat(estimates, ignore_index=True)
    support = pd.DataFrame(support_rows)
    est.to_csv(OUT / "public_charge_ddd_estimates.csv", index=False)
    support.to_csv(OUT / "public_charge_model_support.csv", index=False)

    report = f"""# Public Charge Immigrant Chilling Effect Quick Screen

## Purpose

This test revisits a previously deferred adult idea: whether the Trump-era public charge rule
chilled Medicaid, SNAP, and coverage among low-income noncitizen adults. The compact SIPP parquet
did not include citizenship/nativity variables, so this script extracts `ECITIZEN`, `EBORNUS`, and
`ENATCIT` from the local raw SIPP CSV zips and merges them back to the person-month panel.

## Policy Timing Used

- Pre period: reference years 2017-2018.
- Chilling / final-rule period: reference years 2019-2020.
- Reversal / post-rule period: reference years 2021-2023.

The exact rule implementation was February 24, 2020, and DHS stopped applying the 2019 rule on
March 9, 2021. The broader chilling period starts earlier because the final rule was published in
2019 and the policy debate/reaction began before implementation.

## Supplemental Extraction

- Source raw zips: `temp/raw_downloads/census_sipp/YYYY/primary/puYYYY_csv.zip`.
- Extracted variables: `SSUID`, `PNUM`, `MONTHCODE`, `ECITIZEN`, `ACITIZEN`, `EBORNUS`, `ABORNUS`,
  `ENATCIT`, `ANATCIT`.
- Cached extract: `temp/scratch/immigration_status_2018_2024.parquet`.
- Merge key: `file_year + SSUID + PNUM + MONTHCODE`.

## Citizenship Variable Counts

{md_table(status_df[status_df['variable'].isin(['ECITIZEN', 'EBORNUS', 'ENATCIT'])], ['variable', 'value', 'rows'], max_rows=40)}

## Model Support

{md_table(support, ['spec', 'person_months', 'persons', 'states', 'noncitizen_person_months', 'low_noncitizen_person_months', 'low_noncitizen_persons'])}

## Raw Cell Means

Monthly FPL low-income cutoff at 250% FPL.

{md_table(cell_df, ['period', 'noncitizen', 'low250', 'person_months', 'persons', 'medicaid', 'snap_month', 'uninsured', 'public', 'private'])}

## DDD Design

Main term:

- `noncitizen x low_income x chill_2019_2020`

Reversal term:

- `noncitizen x low_income x reversal_2021_2023`

Controls and fixed effects:

- state fixed effects;
- calendar year-month fixed effects;
- FPL quadratic;
- age quadratic;
- sex, Black, Hispanic, disability.

The model is a difference-in-difference-in-differences comparing low-income noncitizens to
low-income citizens and higher-income noncitizens/citizens over time.

## Main Monthly-FPL 250% Cutoff Estimates

Chilling-period DDD term:

{fmt(est, 'monthly_low250', 'noncitizen_low_chill', outcomes)}

Reversal-period DDD term:

{fmt(est, 'monthly_low250', 'noncitizen_low_reversal', outcomes)}

## Low-Income 150% FPL Sensitivity

Chilling-period DDD term:

{fmt(est, 'monthly_low150', 'noncitizen_low_chill', outcomes)}

Reversal-period DDD term:

{fmt(est, 'monthly_low150', 'noncitizen_low_reversal', outcomes)}

## Annual-FPL 250% Cutoff Sensitivity

Chilling-period DDD term:

{fmt(est, 'annual_low250', 'noncitizen_low_chill', outcomes)}

Reversal-period DDD term:

{fmt(est, 'annual_low250', 'noncitizen_low_reversal', outcomes)}

## Initial Interpretation

A clean public-charge chilling story predicts negative effects on Medicaid/SNAP/public coverage and
positive effects on uninsurance for low-income noncitizens during 2019-2020, with possible rebound
after 2021. If the signs are mixed, or if Medicaid moves differently from SNAP, the design should
be treated as exploratory because the rule period overlaps the COVID-19 shock and the PHE.

## Artifacts

- `script/11_idea_scan/31_public_charge_immigrant_chilling_test.py`
- `temp/scratch/immigration_status_2018_2024.parquet`
- `result/idea_scan/public_charge_status_value_counts.csv`
- `result/idea_scan/public_charge_cell_means.csv`
- `result/idea_scan/public_charge_person_support.csv`
- `result/idea_scan/public_charge_model_support.csv`
- `result/idea_scan/public_charge_ddd_estimates.csv`
"""
    REPORT.write_text(report, encoding="utf-8")
    print(support.to_string(index=False))
    print(est.to_string(index=False))


if __name__ == "__main__":
    main()
