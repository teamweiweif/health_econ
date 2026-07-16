from __future__ import annotations

from pathlib import Path
import io
import zipfile

import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.csv as pc
import pyarrow.parquet as pq


ROOT = Path(__file__).resolve().parents[2]
PANEL = ROOT / "data" / "analysis_ready" / "sipp_2018_2024_person_month_panel.parquet"
OUT = ROOT / "result" / "idea_scan"
SCRATCH = ROOT / "temp" / "scratch" / "rpritype1_2018_2024.parquet"
REPORT = ROOT / "report" / "54_arpa_400fpl_employer_mechanism_test.md"


def yes(s: pd.Series) -> pd.Series:
    return s.eq(1)


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


def wls_hc1_cluster(
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
    if len(y) <= x.shape[1] + 5:
        k = x.shape[1]
        return np.full(k, np.nan), np.full(k, np.nan), np.full(k, np.nan), int(len(y)), int(pd.Series(cluster).nunique())

    sw = np.sqrt(w / np.nanmean(w))
    xw = x * sw[:, None]
    yw = y * sw
    inv = np.linalg.pinv(xw.T @ xw)
    beta = inv @ (xw.T @ yw)
    resid = yw - xw @ beta

    meat_hc1 = xw.T @ ((resid**2)[:, None] * xw)
    n, k = xw.shape
    cov_hc1 = (n / max(n - k, 1)) * inv @ meat_hc1 @ inv
    se_hc1 = np.sqrt(np.where(np.diag(cov_hc1) >= 0, np.diag(cov_hc1), np.nan))

    codes, uniques = pd.factorize(cluster, sort=False)
    score_rows = xw * resid[:, None]
    score_sums = np.zeros((len(uniques), k))
    np.add.at(score_sums, codes, score_rows)
    meat = score_sums.T @ score_sums
    g_count = len(uniques)
    if g_count > 1:
        meat *= (g_count / (g_count - 1)) * ((n - 1) / max(n - k, 1))
    cov = inv @ meat @ inv
    se_cluster = np.sqrt(np.where(np.diag(cov) >= 0, np.diag(cov), np.nan))
    return beta, se_hc1, se_cluster, int(n), int(g_count)


def extract_rpritype1() -> pd.DataFrame:
    if SCRATCH.exists():
        return pd.read_parquet(SCRATCH)
    writer: pq.ParquetWriter | None = None
    for year in range(2018, 2025):
        zip_path = ROOT / "temp" / "raw_downloads" / "census_sipp" / str(year) / "primary" / f"pu{year}_csv.zip"
        with zipfile.ZipFile(zip_path) as z:
            csv_name = [n for n in z.namelist() if n.lower().endswith(".csv")][0]
            data = z.read(csv_name)
        table = pc.read_csv(
            io.BytesIO(data),
            read_options=pc.ReadOptions(use_threads=True),
            parse_options=pc.ParseOptions(delimiter="|"),
            convert_options=pc.ConvertOptions(
                include_columns=["SSUID", "PNUM", "MONTHCODE", "RPRITYPE1"],
                strings_can_be_null=True,
            ),
        )
        year_arr = pa.array([year] * table.num_rows, type=pa.int16())
        table = table.append_column("file_year", year_arr)
        df = table.to_pandas()
        df["PNUM"] = pd.to_numeric(df["PNUM"], errors="coerce").astype("Int64")
        df["MONTHCODE"] = pd.to_numeric(df["MONTHCODE"], errors="coerce").astype("Int64")
        df["RPRITYPE1"] = pd.to_numeric(df["RPRITYPE1"], errors="coerce").astype("float32")
        df["file_year"] = df["file_year"].astype("int16")
        out_table = pa.Table.from_pandas(df, preserve_index=False)
        if writer is None:
            SCRATCH.parent.mkdir(parents=True, exist_ok=True)
            writer = pq.ParquetWriter(SCRATCH, out_table.schema, compression="snappy")
        writer.write_table(out_table)
    if writer is not None:
        writer.close()
    return pd.read_parquet(SCRATCH)


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
        "TFCYINCPOV",
    ]
    base = pd.read_parquet(PANEL, columns=cols)
    emp = extract_rpritype1()
    base["SSUID"] = base["SSUID"].astype(str)
    emp["SSUID"] = emp["SSUID"].astype(str)
    base["file_year"] = pd.to_numeric(base["file_year"], errors="coerce").astype("int16")
    emp["file_year"] = pd.to_numeric(emp["file_year"], errors="coerce").astype("int16")
    base["PNUM"] = pd.to_numeric(base["PNUM"], errors="coerce").astype("Int64")
    base["MONTHCODE"] = pd.to_numeric(base["MONTHCODE"], errors="coerce").astype("Int64")
    emp["PNUM"] = pd.to_numeric(emp["PNUM"], errors="coerce").astype("Int64")
    emp["MONTHCODE"] = pd.to_numeric(emp["MONTHCODE"], errors="coerce").astype("Int64")
    base = base.merge(emp, on=["file_year", "SSUID", "PNUM", "MONTHCODE"], how="left", validate="one_to_one")
    return base


def prep(df: pd.DataFrame, fpl_col: str, post_col: str, age_min: int, bandwidth: float) -> tuple[pd.DataFrame, pd.DataFrame]:
    d = df.copy()
    d["state_fips"] = d["state_fips"].astype(str).str.zfill(2)
    d["age"] = bounded_numeric(d["TAGE"], 0, 100)
    d["female"] = pd.to_numeric(d["ESEX"], errors="coerce").eq(2).astype(float)
    d["black"] = pd.to_numeric(d["ERACE"], errors="coerce").eq(2).astype(float)
    d["hispanic"] = yes(d["EHISPAN"]).astype(float)
    d["disabled"] = yes(d["RDIS"]).astype(float)
    d["monthly_fpl"] = bounded_numeric(d["TFINCPOV"], 0, 20)
    d["annual_fpl"] = bounded_numeric(d["TFCYINCPOV"], 0, 20)
    d["weight"] = clean_weight(d)
    d["month_id"] = d["reference_year"].astype(int) * 100 + d["reference_month"].astype(int)
    d["post_year2021"] = d["reference_year"].ge(2021).astype(int)
    d["post_apr2021"] = d["month_id"].ge(202104).astype(int)
    d["medicare"] = yes(d["RPUBTYPE1"]).astype(float)
    d["any_coverage"] = yes(d["RHLTHMTH"]).astype(float)
    d["uninsured"] = d["RHLTHMTH"].eq(2).astype(float)
    d["private"] = yes(d["RPRIMTH"]).astype(float)
    d["public"] = yes(d["RPUBMTH"]).astype(float)
    d["medicaid"] = yes(d["EMDMTH"]).astype(float)
    d["employer_private"] = yes(d["RPRITYPE1"]).astype(float)
    d["direct_purchase"] = (yes(d["RPRITYPE2"]) | yes(d["RMARKTPLACE"])).astype(float)
    d["marketplace_flag"] = (
        yes(d["RMARKTPLACE"]) | yes(d["EPRIEXCH1"]) | yes(d["EPRIEXCH2"]) | yes(d["EMDEXCH"])
    ).astype(float)
    d["subsidized_private"] = (yes(d["EPRISUBS1"]) | yes(d["EPRISUBS2"]) | yes(d["EMDSUBS"])).astype(float)
    d["market_or_subsidy"] = (
        d["direct_purchase"].eq(1) | d["marketplace_flag"].eq(1) | d["subsidized_private"].eq(1)
    ).astype(float)

    s = d[
        d["age"].between(age_min, 64, inclusive="both")
        & d["medicare"].ne(1)
        & d[fpl_col].between(4.0 - bandwidth, 4.0 + bandwidth, inclusive="both")
        & d["weight"].gt(0)
    ].copy()
    s["running"] = s[fpl_col] - 4.0
    s["above"] = s[fpl_col].gt(4.0).astype(float)
    s["post"] = s[post_col].astype(float)
    s["above_x_post"] = s["above"] * s["post"]
    s["kernel"] = (1 - (s["running"].abs() / bandwidth)).clip(lower=0)
    s["analysis_weight"] = s["weight"] * s["kernel"]

    parts: list[pd.Series | pd.DataFrame] = [
        pd.Series(1.0, index=s.index, name="const"),
        s["above"].rename("above"),
        s["post"].rename("post"),
        s["above_x_post"].rename("above_x_post"),
        s["running"].rename("running"),
        (s["running"] * s["above"]).rename("running_x_above"),
        (s["running"] * s["post"]).rename("running_x_post"),
        (s["running"] * s["above"] * s["post"]).rename("running_x_above_x_post"),
        s["age"].rename("age"),
        s["female"].rename("female"),
        s["black"].rename("black"),
        s["hispanic"].rename("hispanic"),
        s["disabled"].rename("disabled"),
    ]
    for col in ["reference_year", "reference_month", "state_fips"]:
        parts.append(pd.get_dummies(s[col].astype(str), prefix=col, drop_first=True, dtype=float))
    x = pd.concat(parts, axis=1)
    return s, x


def estimate_model(s: pd.DataFrame, x: pd.DataFrame, outcomes: list[str], model: str) -> pd.DataFrame:
    rows = []
    x_np = x.to_numpy(dtype=float)
    w_np = s["analysis_weight"].to_numpy(dtype=float)
    cluster_np = s["person_id"].to_numpy()
    cell_base = s.groupby(["post", "above"], observed=True).agg(persons=("person_id", "nunique")).reset_index()
    for outcome in outcomes:
        beta, se_hc1, se_cluster, n, g = wls_hc1_cluster(s[outcome].to_numpy(dtype=float), x_np, w_np, cluster_np)
        b = pd.Series(beta, index=x.columns)
        hc1 = pd.Series(se_hc1, index=x.columns)
        cl = pd.Series(se_cluster, index=x.columns)
        events = s.groupby(["post", "above"], observed=True)[outcome].sum().reset_index(name="events")
        cell = cell_base.merge(events, on=["post", "above"], how="left")
        rows.append(
            {
                "model": model,
                "outcome": outcome,
                "coef_above_x_post": b.get("above_x_post", np.nan),
                "se_hc1": hc1.get("above_x_post", np.nan),
                "t_hc1": b.get("above_x_post", np.nan) / hc1.get("above_x_post", np.nan)
                if hc1.get("above_x_post", np.nan) > 0
                else np.nan,
                "se_person_cluster": cl.get("above_x_post", np.nan),
                "t_person_cluster": b.get("above_x_post", np.nan) / cl.get("above_x_post", np.nan)
                if cl.get("above_x_post", np.nan) > 0
                else np.nan,
                "n_person_months": n,
                "n_persons": int(s["person_id"].nunique()),
                "n_clusters": g,
                "n_states": int(s["state_fips"].nunique()),
                "min_cell_persons": int(cell["persons"].min()),
                "min_cell_events": int(cell["events"].min()),
                "weighted_mean": wmean(s[outcome], s["weight"]),
            }
        )
    return pd.DataFrame(rows)


def cell_means(s: pd.DataFrame, outcomes: list[str], model: str) -> pd.DataFrame:
    rows = []
    for (post, above), g in s.groupby(["post", "above"], observed=True):
        row = {
            "model": model,
            "post": int(post),
            "above": int(above),
            "person_months": int(len(g)),
            "persons": int(g["person_id"].nunique()),
        }
        for outcome in outcomes:
            row[outcome] = wmean(g[outcome], g["weight"])
        rows.append(row)
    return pd.DataFrame(rows)


def fmt(est: pd.DataFrame, model: str, outcomes: list[str]) -> str:
    d = est[est["model"].eq(model)].set_index("outcome")
    lines = []
    for outcome in outcomes:
        if outcome in d.index:
            r = d.loc[outcome]
            lines.append(
                f"- `{outcome}`: {r['coef_above_x_post']:+.4f}, HC1 se {r['se_hc1']:.4f}, "
                f"t {r['t_hc1']:.2f}; person-cluster se {r['se_person_cluster']:.4f}, "
                f"t {r['t_person_cluster']:.2f}."
            )
    return "\n".join(lines)


def md_table(df: pd.DataFrame, cols: list[str]) -> str:
    lines = ["| " + " | ".join(cols) + " |", "|" + "|".join(["---"] * len(cols)) + "|"]
    for _, r in df[cols].iterrows():
        vals = []
        for c in cols:
            v = r[c]
            vals.append(f"{v:.4f}" if isinstance(v, float) else str(v))
        lines.append("| " + " | ".join(vals) + " |")
    return "\n".join(lines)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    df = read_augmented_panel()
    outcomes = [
        "uninsured",
        "any_coverage",
        "employer_private",
        "direct_purchase",
        "marketplace_flag",
        "market_or_subsidy",
        "private",
        "public",
        "medicaid",
    ]
    specs = [
        ("monthly_fpl_age26_64_postyear_bw050", "monthly_fpl", "post_year2021", 26, 0.50, outcomes),
        ("monthly_fpl_age21_64_postyear_bw050", "monthly_fpl", "post_year2021", 21, 0.50, outcomes[:6]),
        ("monthly_fpl_age26_64_postapr2021_bw050", "monthly_fpl", "post_apr2021", 26, 0.50, outcomes[:6]),
        ("annual_fpl_age26_64_postyear_bw050", "annual_fpl", "post_year2021", 26, 0.50, outcomes[:6]),
    ]
    estimates = []
    means = []
    supports = []
    for model, fpl_col, post_col, age_min, bw, model_outcomes in specs:
        s, x = prep(df, fpl_col, post_col, age_min, bw)
        estimates.append(estimate_model(s, x, model_outcomes, model))
        means.append(cell_means(s, model_outcomes, model))
        supports.append(
            {
                "model": model,
                "fpl_col": fpl_col,
                "post_col": post_col,
                "age_min": age_min,
                "bandwidth": bw,
                "person_months": int(len(s)),
                "persons": int(s["person_id"].nunique()),
                "states": int(s["state_fips"].nunique()),
                "missing_rpritype1": int(s["RPRITYPE1"].isna().sum()),
            }
        )
    est = pd.concat(estimates, ignore_index=True)
    cm = pd.concat(means, ignore_index=True)
    sup = pd.DataFrame(supports)
    est.to_csv(OUT / "arpa400_employer_mechanism_estimates.csv", index=False)
    cm.to_csv(OUT / "arpa400_employer_mechanism_cell_means.csv", index=False)
    sup.to_csv(OUT / "arpa400_employer_mechanism_support.csv", index=False)

    primary = "monthly_fpl_age26_64_postyear_bw050"
    april = "monthly_fpl_age26_64_postapr2021_bw050"
    annual = "annual_fpl_age26_64_postyear_bw050"
    primary_sup = sup[sup["model"].eq(primary)].iloc[0]
    report = f"""# ARPA 400% FPL Employer-Coverage Mechanism Test

## Purpose

This is a supplemental validation of the leading ARPA 400% FPL cliff design. The prior compact
analysis-ready parquet did not include `RPRITYPE1`, the monthly employer-related private coverage
recode. This script extracts `RPRITYPE1` directly from the local raw Census SIPP zips and merges it
back onto the person-month panel by `file_year`, `SSUID`, `PNUM`, and `MONTHCODE`.

## Source and Merge Check

- Raw zips: `temp/raw_downloads/census_sipp/YYYY/primary/puYYYY_csv.zip`.
- Supplemental extract: `temp/scratch/rpritype1_2018_2024.parquet`.
- Merge key: `file_year + SSUID + PNUM + MONTHCODE`.
- Main sample missing `RPRITYPE1` rows after merge: {int(primary_sup['missing_rpritype1']):,}.

## Main Support

- Main model: age 26-64, non-Medicare, 350-450% monthly FPL.
- Person-months: {int(primary_sup['person_months']):,}.
- Persons: {int(primary_sup['persons']):,}.
- States: {int(primary_sup['states']):,}.

## Raw Cell Means

{md_table(cm[cm['model'].eq(primary)], ['post', 'above', 'person_months', 'persons', 'uninsured', 'employer_private', 'direct_purchase', 'marketplace_flag', 'market_or_subsidy', 'private'])}

## Main Estimates

Monthly FPL, age 26-64, post = 2021-2023:

{fmt(est, primary, outcomes)}

Monthly FPL, age 21-64 sensitivity:

{fmt(est, 'monthly_fpl_age21_64_postyear_bw050', outcomes[:6])}

Monthly FPL, age 26-64, post = April 2021 onward:

{fmt(est, april, outcomes[:6])}

Annual FPL sensitivity:

{fmt(est, annual, outcomes[:6])}

## Interpretation

The employer coverage variable materially improves the mechanism audit. A clean ARPA cliff story
should show that the uninsured decline is not simply employer coverage substitution. The key check
is therefore whether `employer_private` moves little relative to direct purchase / Marketplace
proxies in the same difference-in-discontinuities design.

## Artifacts

- `script/11_idea_scan/26_arpa_400fpl_employer_mechanism_test.py`
- `temp/scratch/rpritype1_2018_2024.parquet`
- `result/idea_scan/arpa400_employer_mechanism_estimates.csv`
- `result/idea_scan/arpa400_employer_mechanism_cell_means.csv`
- `result/idea_scan/arpa400_employer_mechanism_support.csv`
"""
    REPORT.write_text(report, encoding="utf-8")
    print(sup.to_string(index=False))
    print(est.to_string(index=False))


if __name__ == "__main__":
    main()
