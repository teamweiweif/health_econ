from __future__ import annotations

import math
from typing import Iterable

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from project_utils import DATA, RESULT, append_audit


def residualize(df: pd.DataFrame, cols: list[str], fe_cols: list[str], max_iter: int = 100, tol: float = 1e-8) -> np.ndarray:
    arr = df[cols].astype(float).to_numpy()
    arr = arr - np.nanmean(arr, axis=0, keepdims=True)
    work = pd.DataFrame(arr, columns=cols, index=df.index)
    for _ in range(max_iter):
        old = work.to_numpy().copy()
        for fe in fe_cols:
            means = work.groupby(df[fe], observed=True).transform("mean")
            work = work - means
        diff = np.nanmax(np.abs(work.to_numpy() - old))
        if diff < tol:
            break
    return work.to_numpy()


def fe_ols(
    df: pd.DataFrame,
    y_col: str,
    x_cols: list[str],
    fe_cols: list[str],
    cluster_col: str,
) -> pd.DataFrame:
    cols = [y_col, *x_cols, *fe_cols, cluster_col]
    d = df[cols].dropna().copy()
    if len(d) < 50:
        return pd.DataFrame(
            [{"term": x, "estimate": np.nan, "std_error": np.nan, "t_stat": np.nan, "n": len(d)} for x in x_cols]
        )
    y = residualize(d, [y_col], fe_cols)[:, 0]
    x = residualize(d, x_cols, fe_cols)
    xtx = x.T @ x
    inv = np.linalg.pinv(xtx)
    beta = inv @ (x.T @ y)
    resid = y - x @ beta
    meat = np.zeros((len(x_cols), len(x_cols)))
    for _, idx in d.groupby(cluster_col, observed=True).indices.items():
        xg = x[idx, :]
        eg = resid[idx]
        score = xg.T @ eg
        meat += np.outer(score, score)
    g = d[cluster_col].nunique()
    n = len(d)
    k = len(x_cols)
    scale = (g / max(g - 1, 1)) * ((n - 1) / max(n - k, 1))
    vcov = scale * inv @ meat @ inv
    diag = np.diag(vcov)
    diag = np.where((diag < 0) & (diag > -1e-10), 0, diag)
    diag = np.where(diag >= 0, diag, np.nan)
    se = np.sqrt(diag)
    return pd.DataFrame(
        {
            "term": x_cols,
            "estimate": beta,
            "std_error": se,
            "t_stat": beta / se,
            "n": n,
            "clusters": g,
            "outcome": y_col,
            "fixed_effects": ";".join(fe_cols),
        }
    )


def prepare_panel() -> pd.DataFrame:
    panel = pd.read_parquet(DATA / "main_ddd_panel.parquet")
    panel["month"] = pd.to_datetime(panel["month"])
    panel = panel[panel["month"] >= pd.Timestamp("2019-01-01")].copy()
    panel["state_group_fe"] = panel["state_abbr"].astype(str) + "_" + panel["group"].astype(str)
    panel["state_month_fe"] = panel["state_abbr"].astype(str) + "_" + panel["month"].dt.strftime("%Y%m")
    panel["group_month_fe"] = panel["group"].astype(str) + "_" + panel["month"].dt.strftime("%Y%m")
    panel["month_fe"] = panel["month"].dt.strftime("%Y%m")
    panel["log_enrollment"] = pd.to_numeric(panel["log_enrollment"], errors="coerce")
    return panel


def prepare_gap_panel() -> pd.DataFrame:
    panel = prepare_panel()
    id_cols = [
        "state_name",
        "state_abbr",
        "state_fips",
        "month",
        "newly_treated_any_child_ce",
        "newly_treated_medicaid_child_ce",
        "partial_pre2024_ce",
        "event_month",
    ]
    value_cols = [
        "enrollment",
        "log_enrollment",
        "aggregate_instability_proxy",
        "net_enrollment_loss_rate",
    ]
    wide = panel.pivot_table(index=id_cols, columns="group", values=value_cols, aggfunc="first").reset_index()
    wide.columns = [c if isinstance(c, str) else (c[0] if c[1] == "" else f"{c[0]}_{c[1]}") for c in wide.columns]
    for col in ["newly_treated_any_child_ce", "newly_treated_medicaid_child_ce", "partial_pre2024_ce"]:
        wide[col] = pd.to_numeric(wide[col], errors="coerce").fillna(0).astype(int)
    wide["post2024"] = (wide["month"] >= pd.Timestamp("2024-01-01")).astype(int)
    wide["did_any_newly_treated"] = wide["newly_treated_any_child_ce"] * wide["post2024"]
    wide["did_medicaid_newly_treated"] = wide["newly_treated_medicaid_child_ce"] * wide["post2024"]
    wide["did_partial_or_new"] = (
        ((wide["newly_treated_any_child_ce"] == 1) | (wide["partial_pre2024_ce"] == 1)).astype(int)
        * wide["post2024"]
    )
    wide["log_child_adult_gap"] = wide["log_enrollment_child"] - wide["log_enrollment_adult"]
    wide["instability_child_adult_gap"] = (
        wide["aggregate_instability_proxy_child"] - wide["aggregate_instability_proxy_adult"]
    )
    wide["loss_rate_child_adult_gap"] = (
        wide["net_enrollment_loss_rate_child"] - wide["net_enrollment_loss_rate_adult"]
    )
    wide["state_fe"] = wide["state_abbr"].astype(str)
    wide["month_fe"] = wide["month"].dt.strftime("%Y%m")
    return wide


def main() -> None:
    panel = prepare_gap_panel()
    fe_main = ["state_fe", "month_fe"]
    specs = [
        ("main_any_newly_treated_gap", "did_any_newly_treated", "log_child_adult_gap"),
        ("medicaid_newly_treated_gap", "did_medicaid_newly_treated", "log_child_adult_gap"),
        ("partial_or_new_gap", "did_partial_or_new", "log_child_adult_gap"),
        ("aggregate_instability_gap", "did_any_newly_treated", "instability_child_adult_gap"),
        ("net_loss_rate_gap", "did_any_newly_treated", "loss_rate_child_adult_gap"),
    ]
    rows = []
    for spec, treat, outcome in specs:
        res = fe_ols(panel, outcome, [treat], fe_main, "state_abbr")
        res.insert(0, "spec", spec)
        rows.append(res)
    out = pd.concat(rows, ignore_index=True)
    out.to_csv(RESULT / "main_ddd_table.csv", index=False)

    event = panel.copy()
    event = event[(event["event_month"] >= -36) & (event["event_month"] <= 27)].copy()
    event_terms = []
    for e in sorted(event["event_month"].dropna().astype(int).unique()):
        if e == -1:
            continue
        name = f"event_{e:+03d}".replace("+", "p").replace("-", "m")
        event[name] = event["newly_treated_any_child_ce"] * (event["event_month"].astype(int) == e).astype(int)
        event_terms.append(name)
    ev = fe_ols(event, "log_child_adult_gap", event_terms, fe_main, "state_abbr")
    ev["event_month"] = ev["term"].str.extract(r"event_([pm]\d+)")[0].map(lambda s: int(s.replace("p", "").replace("m", "-")) if isinstance(s, str) else np.nan)
    ev.to_csv(RESULT / "main_event_study_coefficients.csv", index=False)

    plot = ev.dropna(subset=["event_month", "estimate"]).sort_values("event_month")
    plt.figure(figsize=(11, 5))
    plt.axhline(0, color="black", linewidth=0.8)
    plt.axvline(0, color="black", linewidth=1, linestyle="--")
    plt.errorbar(plot["event_month"], plot["estimate"], yerr=1.96 * plot["std_error"], fmt="o", markersize=3)
    plt.xlabel("Months relative to January 2024")
    plt.ylabel("DID coefficient on log child-adult enrollment gap")
    plt.title("Event study: newly treated states and child-adult enrollment gap")
    plt.tight_layout()
    plt.savefig(RESULT / "child_adult_gap_event_study.png", dpi=180)
    plt.close()

    append_audit("main DDD estimated using child-adult/non-child gap implementation and dynamic event-study models")
    print("main models complete")


if __name__ == "__main__":
    main()
