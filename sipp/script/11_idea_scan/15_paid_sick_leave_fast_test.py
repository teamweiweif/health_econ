from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
PANEL = ROOT / "data" / "analysis_ready" / "sipp_2018_2024_person_month_panel.parquet"
OUT = ROOT / "result" / "idea_scan"
REPORT = ROOT / "report" / "32_paid_sick_leave_fast_test.md"


SOURCES = [
    "NCSL paid sick leave summary: https://www.ncsl.org/labor-and-employment/paid-sick-leave",
    "Washington L&I paid sick leave page: https://www.lni.wa.gov/workers-rights/leave/paid-sick-leave/",
    "New York Paid Sick Leave official page: https://www.ny.gov/programs/new-york-paid-sick-leave",
    "Colorado Department of Labor paid sick leave topic page: https://cdle.colorado.gov/dlss/labor-laws-by-topic/wage-and-hour-laws-including-paid-sick-leave",
    "Maryland Healthy Working Families Act FAQ: https://labor.maryland.gov/paidleave/paidleavefaqs.shtml",
    "New Mexico Department of Workforce Solutions Healthy Workplaces Act notice: https://www.dws.state.nm.us/Researchers/Publications/Economic-News/law-for-paid-sick-leave-goes-into-effect-july-2022-employers-are-encouraged-to-attend-nmdws-information-webinar",
]


STATE_NAMES = {
    "01": "Alabama",
    "02": "Alaska",
    "04": "Arizona",
    "05": "Arkansas",
    "06": "California",
    "08": "Colorado",
    "09": "Connecticut",
    "10": "Delaware",
    "11": "District of Columbia",
    "12": "Florida",
    "13": "Georgia",
    "15": "Hawaii",
    "16": "Idaho",
    "17": "Illinois",
    "18": "Indiana",
    "19": "Iowa",
    "20": "Kansas",
    "21": "Kentucky",
    "22": "Louisiana",
    "23": "Maine",
    "24": "Maryland",
    "25": "Massachusetts",
    "26": "Michigan",
    "27": "Minnesota",
    "28": "Mississippi",
    "29": "Missouri",
    "30": "Montana",
    "31": "Nebraska",
    "32": "Nevada",
    "33": "New Hampshire",
    "34": "New Jersey",
    "35": "New Mexico",
    "36": "New York",
    "37": "North Carolina",
    "38": "North Dakota",
    "39": "Ohio",
    "40": "Oklahoma",
    "41": "Oregon",
    "42": "Pennsylvania",
    "44": "Rhode Island",
    "45": "South Carolina",
    "46": "South Dakota",
    "47": "Tennessee",
    "48": "Texas",
    "49": "Utah",
    "50": "Vermont",
    "51": "Virginia",
    "53": "Washington",
    "54": "West Virginia",
    "55": "Wisconsin",
    "56": "Wyoming",
}

# Statewide paid sick leave laws newly active inside the 2017-2023 SIPP reference window.
# Partial-year 2018 adopters are coded in the first year with substantial/full exposure.
CLEAN_PAID_SICK_ACTIVE_YEAR = {
    "24": 2018,  # Maryland, effective Feb. 11, 2018.
    "53": 2018,  # Washington, effective Jan. 1, 2018.
    "34": 2019,  # New Jersey, effective Oct. 29, 2018; first full year is 2019.
    "44": 2019,  # Rhode Island, effective July 1, 2018; first full year is 2019.
    "08": 2021,  # Colorado, larger employers in 2021, all employers in 2022.
    "36": 2021,  # New York, use begins Jan. 1, 2021.
    "35": 2023,  # New Mexico, effective July 1, 2022; first full year is 2023.
}

# Broader/less clean paid leave coding used only as sensitivity.
BROAD_PAID_LEAVE_ACTIVE_YEAR = {
    **CLEAN_PAID_SICK_ACTIVE_YEAR,
    "26": 2019,  # Michigan Paid Medical Leave Act, more limited coverage.
    "32": 2020,  # Nevada paid leave for any reason, not classic sick leave.
    "23": 2021,  # Maine earned paid leave for any reason, not classic sick leave.
}


def yes(s: pd.Series) -> pd.Series:
    return s.eq(1)


def clean_weight(df: pd.DataFrame) -> pd.Series:
    w = pd.to_numeric(df.get("WPFINWGT"), errors="coerce")
    return w.where(w.gt(0))


def wmean(y: pd.Series, w: pd.Series) -> float:
    mask = y.notna() & w.notna() & (w > 0)
    if not mask.any():
        return np.nan
    return float(np.average(y[mask].astype(float), weights=w[mask].astype(float)))


def wls_hc1(y: np.ndarray, x: np.ndarray, w: np.ndarray) -> tuple[np.ndarray, np.ndarray, int]:
    mask = np.isfinite(y) & np.isfinite(w) & (w > 0) & np.all(np.isfinite(x), axis=1)
    y = y[mask]
    x = x[mask]
    w = w[mask]
    if len(y) <= x.shape[1] + 5:
        return np.full(x.shape[1], np.nan), np.full(x.shape[1], np.nan), int(len(y))
    sw = np.sqrt(w / np.nanmean(w))
    xw = x * sw[:, None]
    yw = y * sw
    inv = np.linalg.pinv(xw.T @ xw)
    beta = inv @ (xw.T @ yw)
    resid = yw - xw @ beta
    meat = xw.T @ ((resid**2)[:, None] * xw)
    n, k = xw.shape
    cov = (n / max(n - k, 1)) * inv @ meat @ inv
    return beta, np.sqrt(np.diag(cov)), int(n)


def bounded_numeric(s: pd.Series, lo: float, hi: float) -> pd.Series:
    out = pd.to_numeric(s, errors="coerce")
    return out.where(out.between(lo, hi, inclusive="both"))


def build_person_year() -> pd.DataFrame:
    cols = [
        "person_id",
        "person_month_key",
        "reference_year",
        "state_fips",
        "TAGE",
        "EEDUC",
        "TFINCPOV",
        "EHLTSTAT",
        "WPFINWGT",
        "TSSSAMT",
        "RMESR",
        "RMWKWJB",
        "TPEARN",
        "RHLTHMTH",
        "RPRIMTH",
        "RPUBMTH",
        "EMDMTH",
        "TMDPAY",
        "TVISDOC",
        "THOSPNIT",
        "TDAYSICK",
    ]
    df = pd.read_parquet(PANEL, columns=cols)
    df = df[df["reference_year"].between(2017, 2023)].copy()
    df["state_fips"] = df["state_fips"].astype(str).str.zfill(2)
    df["age"] = pd.to_numeric(df["TAGE"], errors="coerce")
    df["educ"] = pd.to_numeric(df["EEDUC"], errors="coerce")
    df["fpl"] = bounded_numeric(df["TFINCPOV"], 0, 20)
    df["weight"] = clean_weight(df)
    df["healthy"] = pd.to_numeric(df["EHLTSTAT"], errors="coerce").between(1, 2).astype(float)
    df["employed_month"] = (
        pd.to_numeric(df["RMWKWJB"], errors="coerce").gt(0)
        | pd.to_numeric(df["RMESR"], errors="coerce").between(1, 5)
    ).astype(float)
    df["weeks_with_job"] = bounded_numeric(df["RMWKWJB"], 0, 5)
    df["monthly_earnings"] = bounded_numeric(df["TPEARN"], -250_000, 1_000_000)
    df["positive_earnings_month"] = df["monthly_earnings"].gt(0).astype(float)
    df["any_coverage"] = yes(df["RHLTHMTH"]).astype(float)
    df["uninsured"] = df["RHLTHMTH"].eq(2).astype(float)
    df["private"] = yes(df["RPRIMTH"]).astype(float)
    df["public"] = (yes(df["RPUBMTH"]) | yes(df["EMDMTH"])).astype(float)
    df["doctor_visits"] = bounded_numeric(df["TVISDOC"], 0, 200)
    df["doctor_any"] = df["doctor_visits"].gt(0).astype(float)
    df["hospital_nights"] = bounded_numeric(df["THOSPNIT"], 0, 365)
    df["hospital_any"] = df["hospital_nights"].gt(0).astype(float)
    df["oop_amount"] = bounded_numeric(df["TMDPAY"], 0, 500_000)
    df["oop_any"] = df["oop_amount"].gt(0).astype(float)
    df["sick_days"] = bounded_numeric(df["TDAYSICK"], 0, 365)
    df["sick_any"] = df["sick_days"].gt(0).astype(float)

    py = (
        df.groupby(["person_id", "state_fips", "reference_year"], observed=True)
        .agg(
            months=("person_month_key", "size"),
            weight=("weight", "mean"),
            age=("age", "mean"),
            educ=("educ", "max"),
            fpl=("fpl", "median"),
            healthy=("healthy", "mean"),
            employed_share=("employed_month", "mean"),
            weeks_with_job=("weeks_with_job", "mean"),
            annual_earnings=("monthly_earnings", "sum"),
            earnings_positive=("positive_earnings_month", "max"),
            any_coverage=("any_coverage", "mean"),
            uninsured=("uninsured", "mean"),
            private=("private", "mean"),
            public=("public", "mean"),
            doctor_visits=("doctor_visits", "mean"),
            doctor_any=("doctor_any", "mean"),
            hospital_any=("hospital_any", "mean"),
            oop_amount=("oop_amount", "mean"),
            oop_any=("oop_any", "mean"),
            sick_days=("sick_days", "mean"),
            sick_any=("sick_any", "mean"),
        )
        .reset_index()
    )
    py["state_name"] = py["state_fips"].map(STATE_NAMES)
    py["healthy"] = py["healthy"].ge(0.5).astype(int)
    py["worker"] = py["employed_share"].ge(0.5).astype(int)
    py["low_educ"] = py["educ"].le(39).astype(int)
    py["low_income"] = py["fpl"].le(2.5).astype(int)
    py["low_educ_or_income"] = ((py["low_educ"].eq(1)) | (py["low_income"].eq(1))).astype(int)
    py["log_earnings"] = np.log1p(py["annual_earnings"].clip(lower=0))
    py["clean_active_year"] = py["state_fips"].map(CLEAN_PAID_SICK_ACTIVE_YEAR)
    py["broad_active_year"] = py["state_fips"].map(BROAD_PAID_LEAVE_ACTIVE_YEAR)
    py["clean_adopter_state"] = py["clean_active_year"].notna().astype(int)
    py["broad_adopter_state"] = py["broad_active_year"].notna().astype(int)
    py["clean_policy_active"] = (
        py["clean_active_year"].notna() & py["reference_year"].ge(py["clean_active_year"])
    ).astype(int)
    py["broad_policy_active"] = (
        py["broad_active_year"].notna() & py["reference_year"].ge(py["broad_active_year"])
    ).astype(int)
    py["clean_relative_year"] = py["reference_year"] - py["clean_active_year"]
    return py


def add_fe(parts: list[pd.Series | pd.DataFrame], d: pd.DataFrame, fe_cols: list[str]) -> pd.DataFrame:
    for col in fe_cols:
        parts.append(pd.get_dummies(d[col].astype(str), prefix=col, drop_first=True, dtype=float))
    return pd.concat(parts, axis=1)


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
        parts: list[pd.Series | pd.DataFrame] = [pd.Series(1.0, index=s.index, name="const"), s[term].astype(float)]
        for c in controls:
            parts.append(s[c].astype(float).rename(c))
        x = add_fe(parts, s, fe_cols)
        beta, se, n = wls_hc1(s[outcome].to_numpy(dtype=float), x.to_numpy(dtype=float), s["weight"].to_numpy(dtype=float))
        b = pd.Series(beta, index=x.columns)
        serr = pd.Series(se, index=x.columns)
        se_term = serr.get(term, np.nan)
        rows.append(
            {
                "model": model,
                "outcome": outcome,
                "term": term,
                "coef": b.get(term, np.nan),
                "se": se_term,
                "t": b.get(term, np.nan) / se_term if se_term else np.nan,
                "n_person_years": n,
                "n_persons": int(s["person_id"].nunique()),
                "n_states": int(s["state_fips"].nunique()),
                "weighted_mean": wmean(s[outcome], s["weight"]),
            }
        )
    return pd.DataFrame(rows)


def estimate_event(
    d: pd.DataFrame,
    exposure_col: str,
    rel_years: list[int],
    omitted: int,
    outcomes: list[str],
    model: str,
    controls: list[str],
    fe_cols: list[str],
) -> pd.DataFrame:
    d = d.copy()
    terms = []
    for rel in rel_years:
        if rel == omitted:
            continue
        label = f"m{abs(rel)}" if rel < 0 else f"p{rel}"
        term = f"{exposure_col}_rel_{label}"
        d[term] = (
            d[exposure_col].astype(float)
            * d["clean_adopter_state"].astype(float)
            * d["clean_relative_year"].eq(rel).astype(float)
        )
        terms.append(term)
    rows = []
    for outcome in outcomes:
        s = d[d[outcome].notna() & d["weight"].gt(0)].copy()
        parts: list[pd.Series | pd.DataFrame] = [pd.Series(1.0, index=s.index, name="const"), s[terms]]
        for c in controls:
            parts.append(s[c].astype(float).rename(c))
        x = add_fe(parts, s, fe_cols)
        beta, se, n = wls_hc1(s[outcome].to_numpy(dtype=float), x.to_numpy(dtype=float), s["weight"].to_numpy(dtype=float))
        b = pd.Series(beta, index=x.columns)
        serr = pd.Series(se, index=x.columns)
        for rel in rel_years:
            if rel == omitted:
                continue
            label = f"m{abs(rel)}" if rel < 0 else f"p{rel}"
            term = f"{exposure_col}_rel_{label}"
            se_term = serr.get(term, np.nan)
            rows.append(
                {
                    "model": model,
                    "outcome": outcome,
                    "relative_year": rel,
                    "term": term,
                    "coef": b.get(term, np.nan),
                    "se": se_term,
                    "t": b.get(term, np.nan) / se_term if se_term else np.nan,
                    "n_person_years": n,
                    "n_persons": int(s["person_id"].nunique()),
                    "n_states": int(s["state_fips"].nunique()),
                }
            )
    return pd.DataFrame(rows)


def build_sample(py: pd.DataFrame, target: str, worker_only: bool = True) -> pd.DataFrame:
    d = py[
        py["age"].between(18, 64, inclusive="both")
        & py["months"].ge(6)
        & py["fpl"].between(0, 10, inclusive="both")
        & py["educ"].between(31, 46, inclusive="both")
    ].copy()
    if worker_only:
        d = d[d["worker"].eq(1)].copy()
    if target == "low_educ":
        d["target_worker"] = d["low_educ"]
    elif target == "low_income":
        d["target_worker"] = d["low_income"]
    elif target == "low_educ_or_income":
        d["target_worker"] = d["low_educ_or_income"]
    elif target == "worker":
        d["target_worker"] = d["worker"]
    else:
        raise ValueError(target)
    d["clean_treat"] = d["clean_policy_active"] * d["target_worker"]
    d["broad_treat"] = d["broad_policy_active"] * d["target_worker"]
    d["state_year"] = d["state_fips"] + "_" + d["reference_year"].astype(str)
    d["state_target"] = d["state_fips"] + "_" + d["target_worker"].astype(str)
    d["target_year"] = d["target_worker"].astype(str) + "_" + d["reference_year"].astype(str)
    return d


def support(samples: dict[str, pd.DataFrame]) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    rows = []
    state_rows = []
    event_rows = []
    for name, d in samples.items():
        clean_target = d[d["clean_adopter_state"].eq(1) & d["target_worker"].eq(1)]
        broad_target = d[d["broad_adopter_state"].eq(1) & d["target_worker"].eq(1)]
        rows.append(
            {
                "sample": name,
                "person_years": int(len(d)),
                "persons": int(d["person_id"].nunique()),
                "states": int(d["state_fips"].nunique()),
                "target_person_years": int(d["target_worker"].sum()),
                "clean_adopter_target_person_years": int(len(clean_target)),
                "clean_active_treated_person_years": int(d["clean_treat"].sum()),
                "clean_active_treated_persons": int(d.loc[d["clean_treat"].eq(1), "person_id"].nunique()),
                "broad_adopter_target_person_years": int(len(broad_target)),
                "broad_active_treated_person_years": int(d["broad_treat"].sum()),
                "weighted_mean_sick_days": wmean(d["sick_days"], d["weight"]),
                "weighted_mean_sick_any": wmean(d["sick_any"], d["weight"]),
                "weighted_mean_doctor_any": wmean(d["doctor_any"], d["weight"]),
            }
        )
        by_state = (
            d[d["clean_adopter_state"].eq(1) & d["target_worker"].eq(1)]
            .groupby(["state_fips", "state_name", "reference_year"], observed=True)
            .agg(
                person_years=("person_id", "size"),
                persons=("person_id", "nunique"),
                active=("clean_policy_active", "max"),
                sick_days_mean=("sick_days", "mean"),
                doctor_any_mean=("doctor_any", "mean"),
            )
            .reset_index()
        )
        by_state.insert(0, "sample", name)
        state_rows.append(by_state)
        ev = (
            d[d["clean_adopter_state"].eq(1) & d["target_worker"].eq(1)]
            .groupby("clean_relative_year", observed=True)
            .agg(person_years=("person_id", "size"), persons=("person_id", "nunique"))
            .reset_index()
            .rename(columns={"clean_relative_year": "relative_year"})
        )
        ev.insert(0, "sample", name)
        event_rows.append(ev)
    return (
        pd.DataFrame(rows),
        pd.concat(state_rows, ignore_index=True) if state_rows else pd.DataFrame(),
        pd.concat(event_rows, ignore_index=True) if event_rows else pd.DataFrame(),
    )


def estimate_leave_one(d: pd.DataFrame, outcomes: list[str]) -> pd.DataFrame:
    rows = []
    for state in CLEAN_PAID_SICK_ACTIVE_YEAR:
        dd = d[d["state_fips"].ne(state)].copy()
        if dd["clean_treat"].sum() == 0:
            continue
        est = estimate(
            dd,
            "clean_treat",
            outcomes,
            "paid_sick_leave_low_educ_leave_one",
            controls=["age", "fpl", "healthy"],
            fe_cols=["state_year", "state_target", "target_year"],
        )
        est.insert(1, "excluded_state", state)
        est.insert(2, "excluded_state_name", STATE_NAMES[state])
        rows.append(est)
    return pd.concat(rows, ignore_index=True) if rows else pd.DataFrame()


def fmt(est: pd.DataFrame, model: str, outcomes: list[str]) -> str:
    d = est[est["model"].eq(model)].set_index("outcome")
    lines = []
    for outcome in outcomes:
        if outcome not in d.index:
            continue
        r = d.loc[outcome]
        lines.append(f"- `{outcome}`: {r['coef']:+.4f}, se {r['se']:.4f}, t {r['t']:.2f}.")
    return "\n".join(lines)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    py = build_person_year()
    samples = {
        "worker_low_educ": build_sample(py, "low_educ", worker_only=True),
        "worker_low_income": build_sample(py, "low_income", worker_only=True),
        "worker_low_educ_or_income": build_sample(py, "low_educ_or_income", worker_only=True),
        "all_adults_worker_target": build_sample(py, "worker", worker_only=False),
    }
    outcomes = [
        "sick_days",
        "sick_any",
        "doctor_any",
        "doctor_visits",
        "hospital_any",
        "oop_any",
        "any_coverage",
        "uninsured",
        "private",
        "public",
        "earnings_positive",
        "log_earnings",
    ]
    primary_outcomes = ["sick_days", "sick_any", "doctor_any", "doctor_visits", "uninsured", "log_earnings"]

    estimates = pd.concat(
        [
            estimate(
                samples["worker_low_educ"],
                "clean_treat",
                outcomes,
                "paid_sick_leave_clean_worker_low_educ",
                controls=["age", "fpl", "healthy"],
                fe_cols=["state_year", "state_target", "target_year"],
            ),
            estimate(
                samples["worker_low_income"],
                "clean_treat",
                outcomes,
                "paid_sick_leave_clean_worker_low_income",
                controls=["age", "educ", "healthy"],
                fe_cols=["state_year", "state_target", "target_year"],
            ),
            estimate(
                samples["worker_low_educ_or_income"],
                "clean_treat",
                outcomes,
                "paid_sick_leave_clean_worker_low_educ_or_income",
                controls=["age", "healthy"],
                fe_cols=["state_year", "state_target", "target_year"],
            ),
            estimate(
                samples["all_adults_worker_target"],
                "clean_treat",
                outcomes + ["employed_share"],
                "paid_sick_leave_clean_all_adults_worker_target",
                controls=["age", "fpl", "educ", "healthy"],
                fe_cols=["state_year", "state_target", "target_year"],
            ),
            estimate(
                samples["worker_low_educ"],
                "broad_treat",
                outcomes,
                "paid_sick_leave_broad_worker_low_educ",
                controls=["age", "fpl", "healthy"],
                fe_cols=["state_year", "state_target", "target_year"],
            ),
        ],
        ignore_index=True,
    )
    events = estimate_event(
        samples["worker_low_educ"],
        "target_worker",
        rel_years=[-3, -2, -1, 0, 1, 2, 3],
        omitted=-1,
        outcomes=["sick_days", "sick_any", "doctor_any", "doctor_visits", "uninsured"],
        model="paid_sick_leave_clean_low_educ_event",
        controls=["age", "fpl", "healthy"],
        fe_cols=["state_year", "state_target", "target_year"],
    )
    leave_one = estimate_leave_one(samples["worker_low_educ"], ["sick_days", "sick_any", "doctor_any", "uninsured"])
    sup, state_support, event_support = support(samples)

    py.to_parquet(OUT / "paid_sick_leave_person_year_panel.parquet", index=False)
    estimates.to_csv(OUT / "paid_sick_leave_estimates.csv", index=False)
    events.to_csv(OUT / "paid_sick_leave_event.csv", index=False)
    leave_one.to_csv(OUT / "paid_sick_leave_leave_one.csv", index=False)
    sup.to_csv(OUT / "paid_sick_leave_support.csv", index=False)
    state_support.to_csv(OUT / "paid_sick_leave_state_year_support.csv", index=False)
    event_support.to_csv(OUT / "paid_sick_leave_event_support.csv", index=False)

    low = sup[sup["sample"].eq("worker_low_educ")].iloc[0]
    inc = sup[sup["sample"].eq("worker_low_income")].iloc[0]
    allw = sup[sup["sample"].eq("all_adults_worker_target")].iloc[0]
    primary = estimates[estimates["model"].eq("paid_sick_leave_clean_worker_low_educ")].set_index("outcome")
    doctor_any = primary.loc["doctor_any"]
    sick_days = primary.loc["sick_days"]
    log_earnings = primary.loc["log_earnings"]
    verdict = "NO-CLEAN-GO"
    if doctor_any["coef"] > 0.015 and doctor_any["t"] > 1.5 and log_earnings["coef"] > -0.02:
        verdict = "PROMISING-ACCESS-SIGNAL-BUT-NO-FIRST-STAGE"
    elif doctor_any["coef"] > 0 and sick_days["coef"] != 0:
        verdict = "DIRECTIONAL-BUT-WEAK"

    report = f"""# Paid Sick Leave Fast Test

## Question

Can the current public SIPP parquet support an adult, non-child, non-unwinding paper on state
paid sick leave mandates and worker health/utilization?

## Source Checks

{chr(10).join(f"- {s}" for s in SOURCES)}

Primary clean coding:

- Maryland: active in 2018.
- Washington: active in 2018.
- New Jersey: effective late 2018; first full-year active coding is 2019.
- Rhode Island: effective July 2018; first full-year active coding is 2019.
- Colorado: active in 2021 for larger employers and 2022 for all employers; coding starts in 2021.
- New York: accrual began September 2020 and use began January 2021; coding starts in 2021.
- New Mexico: effective July 2022; first full-year active coding is 2023.

Broad sensitivity adds Michigan, Nevada, and Maine, but these are less clean because Michigan's
law is more limited and Nevada/Maine are earned paid leave rather than classic paid sick leave.

## Data Construction

- Source parquet: `data/analysis_ready/sipp_2018_2024_person_month_panel.parquet`.
- Unit: person-year collapsed from monthly rows.
- Years: reference years 2017-2023.
- Primary sample: employed adults age 18-64 with at least six observed months and valid education/FPL.
- Primary target: high-school-or-less workers (`EEDUC <= 39`).
- Treatment: clean paid sick leave adopter x active year x target worker.
- Fixed effects: state-year, state-target, target-year.

Important measurement caveat: SIPP has `TDAYSICK`, days illness/injury kept the person in bed more
than half the day. It does not directly measure paid sick leave access, accrual, or leave use. This
screen can only test reduced-form health/utilization and labor-market patterns.

## Support

Primary low-education worker sample:

- Person-years: {int(low['person_years']):,}.
- Persons: {int(low['persons']):,}.
- Target worker person-years: {int(low['target_person_years']):,}.
- Clean-adopter target person-years: {int(low['clean_adopter_target_person_years']):,}.
- Clean active treated person-years: {int(low['clean_active_treated_person_years']):,}.

Low-income worker sample:

- Person-years: {int(inc['person_years']):,}.
- Target worker person-years: {int(inc['target_person_years']):,}.
- Clean active treated person-years: {int(inc['clean_active_treated_person_years']):,}.

All-adult worker-target sample:

- Person-years: {int(allw['person_years']):,}.
- Target worker person-years: {int(allw['target_person_years']):,}.
- Clean active treated person-years: {int(allw['clean_active_treated_person_years']):,}.

## Main Estimates

Primary low-education worker DDD:

{fmt(estimates, 'paid_sick_leave_clean_worker_low_educ', primary_outcomes)}

Low-income worker DDD:

{fmt(estimates, 'paid_sick_leave_clean_worker_low_income', primary_outcomes)}

All-adult worker-target DDD:

{fmt(estimates, 'paid_sick_leave_clean_all_adults_worker_target', primary_outcomes + ['employed_share'])}

Broad paid-leave sensitivity among low-education workers:

{fmt(estimates, 'paid_sick_leave_broad_worker_low_educ', primary_outcomes)}

## Event and Robustness Checks

Event coefficients for clean adopter states, omitting relative year -1, are saved in
`result/idea_scan/paid_sick_leave_event.csv`.

Leave-one-clean-adopter-state estimates are saved in
`result/idea_scan/paid_sick_leave_leave_one.csv`.

## Verdict

`{verdict}`

A clean GO would require:

- a coherent access or health-utilization response among plausibly binding workers;
- no large negative earnings/employment signal;
- event estimates without meaningful pre-policy differential movement;
- robustness to leaving out major adopter states;
- and, ideally, a direct first-stage measure of sick-leave access or use.

The last condition is not met in the current 96-column parquet. Therefore this idea can only become
credible if the reduced-form pattern is unusually strong and clean.

## Artifacts

- `script/11_idea_scan/15_paid_sick_leave_fast_test.py`
- `result/idea_scan/paid_sick_leave_person_year_panel.parquet`
- `result/idea_scan/paid_sick_leave_support.csv`
- `result/idea_scan/paid_sick_leave_state_year_support.csv`
- `result/idea_scan/paid_sick_leave_event_support.csv`
- `result/idea_scan/paid_sick_leave_estimates.csv`
- `result/idea_scan/paid_sick_leave_event.csv`
- `result/idea_scan/paid_sick_leave_leave_one.csv`
"""
    REPORT.write_text(report, encoding="utf-8")


if __name__ == "__main__":
    main()
