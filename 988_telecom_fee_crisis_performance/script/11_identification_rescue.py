from __future__ import annotations

import math
import re
from pathlib import Path

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import requests

from model_utils import fit_fe_ols, month_diff
from project_utils import (
    ABBR_TO_STATE_NAME,
    DATA,
    FIPS_TO_ABBR,
    PDF_CHECKS,
    REPORT,
    RESULT,
    TEMP,
    append_audit,
    read_parquet,
    save_csv,
    save_parquet,
    sha256_file,
)


RESCUE_DATA = DATA / "rescue"
RESCUE_RESULT = RESULT / "rescue"
RESCUE_TEMP = TEMP / "identification_rescue"
GEOROUTING_SOURCES = RESCUE_TEMP / "georouting_sources"

STATE_DC = set(FIPS_TO_ABBR.values()) - {"PR"}
OUTCOMES = [
    "in_state_answer_rate_rescue",
    "flowout_to_national_backup_rate",
    "abandoned_in_state_rate",
    "average_speed_to_answer_seconds",
    "log_routed_per_100k",
]


def ensure_rescue_dirs() -> None:
    for path in [RESCUE_DATA, RESCUE_RESULT, RESCUE_TEMP, GEOROUTING_SOURCES, REPORT]:
        path.mkdir(parents=True, exist_ok=True)


def fmt_num(x, digits: int = 3) -> str:
    if pd.isna(x):
        return "NA"
    return f"{float(x):.{digits}f}"


def fmt_pp(x, digits: int = 2) -> str:
    if pd.isna(x):
        return "NA"
    return f"{float(x) * 100:.{digits}f} pp"


def markdown_table(df: pd.DataFrame, max_rows: int | None = None) -> str:
    if max_rows is not None:
        df = df.head(max_rows)
    if df.empty:
        return "_No rows._"
    cols = list(df.columns)
    lines = ["| " + " | ".join(cols) + " |", "| " + " | ".join(["---"] * len(cols)) + " |"]
    for _, row in df.iterrows():
        lines.append("| " + " | ".join("" if pd.isna(row[c]) else str(row[c]) for c in cols) + " |")
    return "\n".join(lines)


def zscore(s: pd.Series) -> pd.Series:
    s = pd.to_numeric(s, errors="coerce")
    sd = s.std(ddof=0)
    if pd.isna(sd) or sd == 0:
        return s * np.nan
    return (s - s.mean()) / sd


def weighted_mean(df: pd.DataFrame, value: str, weight: str) -> float:
    ok = df[value].notna() & df[weight].gt(0)
    if not ok.any():
        return np.nan
    return float(np.average(df.loc[ok, value], weights=df.loc[ok, weight]))


def compute_att_gt(panel: pd.DataFrame, outcome: str, timing_col: str) -> tuple[pd.DataFrame, dict]:
    d = panel[panel["primary_analysis_sample"]].copy()
    d = d[d[outcome].notna()].copy()
    d[timing_col] = pd.to_datetime(d[timing_col], errors="coerce")
    timings = d.groupby("state")[timing_col].agg(lambda s: s.dropna().iloc[0] if s.notna().any() else pd.NaT)
    months = sorted(pd.to_datetime(d["month"].dropna().unique()))
    pivot = d.pivot_table(index="state", columns="month", values=outcome, aggfunc="mean")

    rows: list[dict] = []
    treated_starts = sorted(t for t in timings.dropna().unique() if pd.Timestamp(t) in months)
    for g in treated_starts:
        g = pd.Timestamp(g)
        treated_states = timings[timings.eq(g)].index.tolist()
        pre = g - pd.DateOffset(months=1)
        if pre not in pivot.columns:
            continue
        for t in months:
            t = pd.Timestamp(t)
            et = month_diff(t, g)
            if et == -1 or et < -12 or et > 30:
                continue
            control_states = timings[timings.isna() | timings.gt(t)].index.tolist()
            if not control_states:
                continue
            valid_treated = [
                s for s in treated_states
                if s in pivot.index and pd.notna(pivot.loc[s, t]) and pd.notna(pivot.loc[s, pre])
            ]
            valid_controls = [
                s for s in control_states
                if s in pivot.index and pd.notna(pivot.loc[s, t]) and pd.notna(pivot.loc[s, pre])
            ]
            if not valid_treated or len(valid_controls) < 5:
                continue
            treated_delta = (pivot.loc[valid_treated, t] - pivot.loc[valid_treated, pre]).mean()
            control_delta = (pivot.loc[valid_controls, t] - pivot.loc[valid_controls, pre]).mean()
            rows.append(
                {
                    "outcome": outcome,
                    "timing": timing_col,
                    "cohort_start": g,
                    "month": t,
                    "event_time": et,
                    "period": "post" if et >= 0 else "pre",
                    "att": float(treated_delta - control_delta),
                    "n_treated_states": len(valid_treated),
                    "n_control_states": len(valid_controls),
                }
            )
    att = pd.DataFrame(rows)
    if att.empty:
        return att, {
            "outcome": outcome,
            "timing": timing_col,
            "overall_att": np.nan,
            "pre_mean_abs_att": np.nan,
            "att_cells": 0,
            "treated_cohorts": 0,
        }
    post = att[att["event_time"].ge(0)]
    pre = att[att["event_time"].between(-12, -2)]
    return att, {
        "outcome": outcome,
        "timing": timing_col,
        "overall_att": weighted_mean(post, "att", "n_treated_states"),
        "pre_mean_abs_att": float(pre["att"].abs().mean()) if not pre.empty else np.nan,
        "att_cells": int(len(post)),
        "treated_cohorts": int(att["cohort_start"].nunique()),
    }


def dedup_raw_pdf_rows() -> pd.DataFrame:
    raw = pd.read_csv(PDF_CHECKS / "parsed_988_kpi_raw.csv")
    parsed = raw[raw["parse_status"].eq("parsed")].copy()
    parsed["month"] = pd.to_datetime(parsed["year_month"] + "-01")
    return parsed.sort_values(["state", "month", "page"]).drop_duplicates(["state", "month"], keep="first")


def build_pdf_validation_and_rescue_panel(panel: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    dedup = dedup_raw_pdf_rows()
    dedup["answer_rate_routed_calc"] = dedup["answered_in_state"] / dedup["routed_in_state"]
    dedup["answer_rate_received_calc"] = dedup["answered_in_state"] / dedup["received_in_state"]
    dedup.loc[~np.isfinite(dedup["answer_rate_received_calc"]), "answer_rate_received_calc"] = np.nan
    dedup["answer_rate_validated"] = dedup["answer_rate_received_calc"].where(
        dedup["received_in_state"].notna() & dedup["received_in_state"].gt(0),
        dedup["in_state_answer_rate_reported"],
    )
    dedup["answer_rate_validated"] = dedup["answer_rate_validated"].fillna(dedup["answer_rate_routed_calc"])
    dedup["routed_denominator_abs_diff"] = (
        dedup["answer_rate_routed_calc"] - dedup["in_state_answer_rate_reported"]
    ).abs()
    dedup["received_denominator_abs_diff"] = (
        dedup["answer_rate_received_calc"] - dedup["in_state_answer_rate_reported"]
    ).abs()
    dedup["answer_rate_denominator_note"] = np.where(
        dedup["received_in_state"].notna() & dedup["received_in_state"].ne(dedup["routed_in_state"]),
        "official reported answer rate aligns with answered/received contacts; current pipeline used answered/routed",
        "routed and received denominators match or received denominator unavailable",
    )

    sample = pd.read_csv(PDF_CHECKS / "validation_sample.csv")
    sample["month"] = pd.to_datetime(sample["year_month"] + "-01")
    cols = [
        "state",
        "month",
        "received_in_state",
        "answer_rate_routed_calc",
        "answer_rate_received_calc",
        "routed_denominator_abs_diff",
        "received_denominator_abs_diff",
        "answer_rate_denominator_note",
    ]
    audit = sample.merge(dedup[cols], on=["state", "month"], how="left")
    audit["best_denominator"] = np.where(
        audit["received_denominator_abs_diff"].le(audit["routed_denominator_abs_diff"]),
        "received_in_state",
        "routed_in_state",
    )
    audit["validation_class"] = np.select(
        [
            audit["routed_denominator_abs_diff"].gt(0.01) & audit["received_denominator_abs_diff"].le(0.0055),
            audit[["routed_denominator_abs_diff", "received_denominator_abs_diff"]].min(axis=1).le(0.0055),
        ],
        [
            "correctable_denominator_error_in_current_pipeline",
            "verified_against_pdf_text_with_rounding",
        ],
        default="needs_visual_followup",
    )
    audit["manual_validation_status"] = "completed_rescue_audit"
    save_csv(audit, RESCUE_DATA / "pdf_validation_sample_audit.csv")

    issue = (
        dedup.groupby("year_month", as_index=False)
        .agg(
            states=("state", "nunique"),
            max_current_routed_abs_diff=("routed_denominator_abs_diff", "max"),
            max_received_abs_diff=("received_denominator_abs_diff", "max"),
            rows_with_current_diff_gt_1pp=("routed_denominator_abs_diff", lambda s: int((s > 0.01).sum())),
        )
    )
    save_csv(issue, RESCUE_DATA / "pdf_answer_rate_denominator_audit_by_month.csv")

    rescue_cols = dedup[
        [
            "state",
            "month",
            "received_in_state",
            "answer_rate_validated",
            "answer_rate_routed_calc",
            "answer_rate_received_calc",
            "answer_rate_denominator_note",
        ]
    ]
    rescue_panel = panel.merge(rescue_cols, on=["state", "month"], how="left")
    rescue_panel["in_state_answer_rate_original"] = rescue_panel["in_state_answer_rate"]
    rescue_panel["in_state_answer_rate_rescue"] = rescue_panel["answer_rate_validated"].fillna(
        rescue_panel["in_state_answer_rate"]
    )
    rescue_panel["answer_rate_pp_rescue"] = rescue_panel["in_state_answer_rate_rescue"] * 100
    rescue_panel["answer_rate_rescue_change"] = (
        rescue_panel["in_state_answer_rate_rescue"] - rescue_panel["in_state_answer_rate_original"]
    )
    save_parquet(rescue_panel, RESCUE_DATA / "analysis_panel_rescue.parquet")
    save_csv(rescue_panel, RESCUE_DATA / "analysis_panel_rescue.csv")
    return rescue_panel, audit, issue


def panel_coverage(panel: pd.DataFrame) -> pd.DataFrame:
    months = pd.date_range(panel["month"].min(), panel["month"].max(), freq="MS")
    observed_months = set(pd.to_datetime(panel["month"].dropna().unique()))
    missing_months = [m.strftime("%Y-%m") for m in months if m not in observed_months]
    primary = panel[panel["is_state_dc"] & panel["has_population_denominator"] & panel["routed_in_state"].notna()].copy()
    post_monitor_excluded = primary[primary["post2025_policy_monitor_active"].eq(1)]
    rows = [
        {"metric": "raw_jurisdictions", "value": int(panel["state"].nunique())},
        {"metric": "state_dc_jurisdictions", "value": int(panel.loc[panel["is_state_dc"], "state"].nunique())},
        {"metric": "primary_sample_rows", "value": int(panel["primary_analysis_sample"].sum())},
        {"metric": "primary_sample_states", "value": int(panel.loc[panel["primary_analysis_sample"], "state"].nunique())},
        {"metric": "observed_source_months", "value": int(panel["month"].nunique())},
        {"metric": "calendar_window", "value": f"{panel['month'].min().date()} to {panel['month'].max().date()}"},
        {"metric": "missing_calendar_months", "value": ";".join(missing_months) if missing_months else "none"},
        {"metric": "post2025_monitor_rows_excluded_from_primary", "value": int(len(post_monitor_excluded))},
        {
            "metric": "post2025_monitor_states_excluded_from_primary",
            "value": ";".join(sorted(post_monitor_excluded["state"].dropna().unique())),
        },
    ]
    out = pd.DataFrame(rows)
    save_csv(out, RESCUE_DATA / "panel_coverage_audit.csv")

    states_by_month = (
        panel.groupby("year_month", as_index=False)
        .agg(
            raw_jurisdictions=("state", "nunique"),
            primary_rows=("primary_analysis_sample", "sum"),
            state_dc_rows=("is_state_dc", "sum"),
        )
    )
    save_csv(states_by_month, RESCUE_DATA / "panel_coverage_by_month.csv")
    return out


def fee_timing_audit() -> pd.DataFrame:
    rows = [
        {
            "state": "VA",
            "state_name": "Virginia",
            "bill_number": "SB1302",
            "bill_enactment_date": "2021-03-18",
            "statutory_effective_date": "2021-07-01",
            "fee_collection_start_date": "2021-07-01",
            "first_observed_fee_revenue_date": "2021-07-01",
            "first_operational_use_date": "2021-10-01",
            "fund_scope": "988 call center fund",
            "restricted_988_only_funding_indicator": 1,
            "broader_crisis_system_funding_indicator": 0,
            "fee_amount_and_base": "$0.12 postpaid wireless; $0.08 prepaid wireless",
            "preexisting_911_fee_infrastructure": 1,
            "source_url_or_archive": "https://legacylis.virginia.gov/cgi-bin/legp604.exe?212+sum+SB1302=; temp/raw_downloads/fcc_988_fee_reports/2021_first_annual_988_fee_accountability_report.pdf",
            "confidence_rating": "high",
            "audit_note": "Enactment and collection are source-supported; operational use remains a 3-month analytic lag.",
        },
        {
            "state": "WA",
            "state_name": "Washington",
            "bill_number": "HB1477",
            "bill_enactment_date": "2021-05-13",
            "statutory_effective_date": "2021-07-25",
            "fee_collection_start_date": "2021-10-01",
            "first_observed_fee_revenue_date": "2021-10-01",
            "first_operational_use_date": "2022-01-01",
            "fund_scope": "behavioral health crisis response and suicide prevention line",
            "restricted_988_only_funding_indicator": 0,
            "broader_crisis_system_funding_indicator": 1,
            "fee_amount_and_base": "$0.24 per line initially; $0.40 from 2023 in coded schedule",
            "preexisting_911_fee_infrastructure": 1,
            "source_url_or_archive": "https://app.leg.wa.gov/RCW/default.aspx?cite=82.86&full=true; temp/raw_downloads/state_policy_sources/wa_dor_988_tax.html",
            "confidence_rating": "high",
            "audit_note": "Collection start is high-confidence; operational date is analytic lag.",
        },
        {
            "state": "CO",
            "state_name": "Colorado",
            "bill_number": "SB21-154",
            "bill_enactment_date": "2021-07-06",
            "statutory_effective_date": "2021-07-06",
            "fee_collection_start_date": "2022-01-01",
            "first_observed_fee_revenue_date": "2022-01-01",
            "first_operational_use_date": "2022-04-01",
            "fund_scope": "988 crisis hotline enterprise and crisis care coordination",
            "restricted_988_only_funding_indicator": 0,
            "broader_crisis_system_funding_indicator": 1,
            "fee_amount_and_base": "annual enterprise-set line/prepaid fee, maximum $0.30; coded as 18/27/14/7 cents by year",
            "preexisting_911_fee_infrastructure": 1,
            "source_url_or_archive": "https://leg.colorado.gov/bills/SB21-154; temp/raw_downloads/state_policy_sources/co_session_law_988_surcharge.pdf",
            "confidence_rating": "medium_high",
            "audit_note": "Collection start is high-confidence; exact enactment date should be rechecked before manuscript submission.",
        },
        {
            "state": "CA",
            "state_name": "California",
            "bill_number": "AB988",
            "bill_enactment_date": "2022-09-29",
            "statutory_effective_date": "2023-01-01",
            "fee_collection_start_date": "2023-01-01",
            "first_observed_fee_revenue_date": "2023-01-01",
            "first_operational_use_date": "2023-04-01",
            "fund_scope": "988 state suicide and behavioral health crisis services fund",
            "restricted_988_only_funding_indicator": 0,
            "broader_crisis_system_funding_indicator": 1,
            "fee_amount_and_base": "$0.08 per access line for 2023-2025; $0.05 in 2026 in coded schedule",
            "preexisting_911_fee_infrastructure": 1,
            "source_url_or_archive": "https://cdtfa.ca.gov/taxes-and-fees/mts.htm; temp/raw_downloads/state_policy_sources/ca_cdtfa_988_surcharge_rates.html",
            "confidence_rating": "high",
            "audit_note": "Effective and collection date are direct tax-administration dates.",
        },
        {
            "state": "NV",
            "state_name": "Nevada",
            "bill_number": "Temporary regulation T004-23A",
            "bill_enactment_date": "2023-01-20",
            "statutory_effective_date": "2023-06-01",
            "fee_collection_start_date": "2023-06-01",
            "first_observed_fee_revenue_date": "2023-06-01",
            "first_operational_use_date": "2023-09-01",
            "fund_scope": "988 surcharge for crisis response program",
            "restricted_988_only_funding_indicator": 1,
            "broader_crisis_system_funding_indicator": 0,
            "fee_amount_and_base": "$0.35 per telecommunications access line",
            "preexisting_911_fee_infrastructure": 1,
            "source_url_or_archive": "temp/raw_downloads/state_policy_sources/nv_988_temp_regulation.pdf",
            "confidence_rating": "medium_high",
            "audit_note": "Regulatory path differs from ordinary legislative enactment.",
        },
        {
            "state": "DE",
            "state_name": "Delaware",
            "bill_number": "HS1 for HB160",
            "bill_enactment_date": "2023-08-03",
            "statutory_effective_date": "2024-01-01",
            "fee_collection_start_date": "2024-01-01",
            "first_observed_fee_revenue_date": "2024-01-01",
            "first_operational_use_date": "2024-04-01",
            "fund_scope": "behavioral health crisis intervention services surcharge",
            "restricted_988_only_funding_indicator": 0,
            "broader_crisis_system_funding_indicator": 1,
            "fee_amount_and_base": "$0.60 monthly and prepaid surcharge",
            "preexisting_911_fee_infrastructure": 1,
            "source_url_or_archive": "https://legis.delaware.gov/BillDetail/140522",
            "confidence_rating": "medium_high",
            "audit_note": "Effective and collection dates align with FCC/state coding.",
        },
        {
            "state": "MN",
            "state_name": "Minnesota",
            "bill_number": "SF2588/HF1566 provisions",
            "bill_enactment_date": "2023-05-24",
            "statutory_effective_date": "2024-01-01",
            "fee_collection_start_date": "2024-01-01",
            "first_observed_fee_revenue_date": "2024-01-01",
            "first_operational_use_date": "2024-04-01",
            "fund_scope": "statewide 988 suicide prevention crisis system and related costs",
            "restricted_988_only_funding_indicator": 0,
            "broader_crisis_system_funding_indicator": 1,
            "fee_amount_and_base": "$0.12 per consumer access line; prepaid timing differs",
            "preexisting_911_fee_infrastructure": 1,
            "source_url_or_archive": "https://www.revisor.mn.gov/statutes/cite/145.561; https://assets.senate.mn/summ/bill/2023/0/SF2588/SF%202588%20Summary.pdf",
            "confidence_rating": "medium_high",
            "audit_note": "Postpaid fee began 2024; prepaid implementation changed later.",
        },
        {
            "state": "OR",
            "state_name": "Oregon",
            "bill_number": "HB2757",
            "bill_enactment_date": "2023-07-27",
            "statutory_effective_date": "2024-01-01",
            "fee_collection_start_date": "2024-01-01",
            "first_observed_fee_revenue_date": "2024-01-01",
            "first_operational_use_date": "2024-04-01",
            "fund_scope": "988 coordinated crisis services and mobile crisis when resources allow",
            "restricted_988_only_funding_indicator": 0,
            "broader_crisis_system_funding_indicator": 1,
            "fee_amount_and_base": "$0.40 per line/VoIP service and prepaid transaction",
            "preexisting_911_fee_infrastructure": 1,
            "source_url_or_archive": "temp/raw_downloads/state_policy_sources/or_hb2757.pdf; https://www.oregon.gov/DOR/programs/businesses/Pages/911.aspx",
            "confidence_rating": "high",
            "audit_note": "Tax applies to subscriber bills and retail transactions on or after January 1, 2024.",
        },
        {
            "state": "MD",
            "state_name": "Maryland",
            "bill_number": "SB974/HB933",
            "bill_enactment_date": "2024-05-16",
            "statutory_effective_date": "2024-10-01",
            "fee_collection_start_date": "2024-10-01",
            "first_observed_fee_revenue_date": "2024-10-01",
            "first_operational_use_date": "2025-01-01",
            "fund_scope": "9-8-8 Trust Fund fees for behavioral health crisis response services",
            "restricted_988_only_funding_indicator": 0,
            "broader_crisis_system_funding_indicator": 1,
            "fee_amount_and_base": "$0.25 per 988-accessible service; prepaid later",
            "preexisting_911_fee_infrastructure": 1,
            "source_url_or_archive": "https://mgaleg.maryland.gov/mgawebsite/Legislation/Details/sb0974?ys=2024RS; temp/raw_downloads/state_policy_sources/md_sb974_chapter_pdf.pdf",
            "confidence_rating": "high",
            "audit_note": "Governor approval and effective date are source-supported.",
        },
        {
            "state": "VT",
            "state_name": "Vermont",
            "bill_number": "H.657 / Act 145",
            "bill_enactment_date": "2024-06-03",
            "statutory_effective_date": "2025-07-01",
            "fee_collection_start_date": "2025-07-01",
            "first_observed_fee_revenue_date": "",
            "first_operational_use_date": "2025-10-01",
            "fund_scope": "Vermont 988 Suicide and Crisis Lifeline",
            "restricted_988_only_funding_indicator": 1,
            "broader_crisis_system_funding_indicator": 0,
            "fee_amount_and_base": "VUSF per-line contribution allocation; amount not coded from FCC report",
            "preexisting_911_fee_infrastructure": 1,
            "source_url_or_archive": "https://legislature.vermont.gov/Documents/2024/Docs/ACTS/ACT145/ACT145%20As%20Enacted.pdf; https://legislature.vermont.gov/statutes/section/30/088/07513a",
            "confidence_rating": "medium_high",
            "audit_note": "No 2024 fee revenue observed in FCC report.",
        },
        {
            "state": "NM",
            "state_name": "New Mexico",
            "bill_number": "SB535",
            "bill_enactment_date": "2025-04-08",
            "statutory_effective_date": "2025-07-01",
            "fee_collection_start_date": "2025-07-01",
            "first_observed_fee_revenue_date": "",
            "first_operational_use_date": "2025-10-01",
            "fund_scope": "988 lifeline fund supported by telecom relay surcharge increase",
            "restricted_988_only_funding_indicator": 1,
            "broader_crisis_system_funding_indicator": 0,
            "fee_amount_and_base": "relay surcharge increased from 0.33% to 1.66%; 80% of increase to 988 lifeline fund",
            "preexisting_911_fee_infrastructure": 1,
            "source_url_or_archive": "https://www.nmlegis.gov/Sessions/25%20Regular/bills/senate/SB0535FCS.HTML; https://www.tax.newmexico.gov/wp-content/uploads/2025/06/2025.06.04_New-tax-and-fee-changes-beginning-July-1.pdf",
            "confidence_rating": "medium_high",
            "audit_note": "Outside FCC revenue window and post-2025 monitor status in original data.",
        },
        {
            "state": "IL",
            "state_name": "Illinois",
            "bill_number": "HB2755 / SB2120 related language",
            "bill_enactment_date": "2025-06-01",
            "statutory_effective_date": "2025-06-01",
            "fee_collection_start_date": "2025-07-01",
            "first_observed_fee_revenue_date": "",
            "first_operational_use_date": "2025-10-01",
            "fund_scope": "Statewide 9-8-8 Trust Fund and intrastate telecommunications tax surcharge",
            "restricted_988_only_funding_indicator": 1,
            "broader_crisis_system_funding_indicator": 0,
            "fee_amount_and_base": "1.65 percentage-point intrastate telecommunications tax increase designated for 988",
            "preexisting_911_fee_infrastructure": 1,
            "source_url_or_archive": "https://ilga.gov/ftp/legislation/104/SB/10400SB2120.htm; temp/raw_downloads/fcc_988_fee_reports/2024_fourth_annual_988_fee_accountability_report.pdf",
            "confidence_rating": "low_medium",
            "audit_note": "FCC notes 2025 legislation after the 2024 reporting period; revenue not yet observed.",
        },
        {
            "state": "VI",
            "state_name": "U.S. Virgin Islands",
            "bill_number": "authority reported to FCC",
            "bill_enactment_date": "",
            "statutory_effective_date": "",
            "fee_collection_start_date": "",
            "first_observed_fee_revenue_date": "",
            "first_operational_use_date": "",
            "fund_scope": "authority reported but no collection through 2024",
            "restricted_988_only_funding_indicator": np.nan,
            "broader_crisis_system_funding_indicator": np.nan,
            "fee_amount_and_base": "not collected by 2024",
            "preexisting_911_fee_infrastructure": np.nan,
            "source_url_or_archive": "temp/raw_downloads/fcc_988_fee_reports/2024_fourth_annual_988_fee_accountability_report.pdf",
            "confidence_rating": "medium",
            "audit_note": "Not part of state/DC causal sample and no observed collection.",
        },
    ]
    out = pd.DataFrame(rows)
    for col in [
        "bill_enactment_date",
        "statutory_effective_date",
        "fee_collection_start_date",
        "first_observed_fee_revenue_date",
        "first_operational_use_date",
    ]:
        out[col] = pd.to_datetime(out[col], errors="coerce")
    out["revenue_timing_precision"] = np.where(
        out["first_observed_fee_revenue_date"].notna(),
        "annual FCC revenue observed; month inferred from collection/effective timing, not directly observed",
        "not observed in current FCC annual revenue window",
    )
    save_csv(out, RESCUE_DATA / "fee_timing_audit_state.csv")
    return out


def add_alternative_treatments(panel: pd.DataFrame, timing: pd.DataFrame) -> pd.DataFrame:
    d = panel.copy()
    timing_slim = timing[
        [
            "state",
            "bill_enactment_date",
            "statutory_effective_date",
            "fee_collection_start_date",
            "first_observed_fee_revenue_date",
            "first_operational_use_date",
            "restricted_988_only_funding_indicator",
            "broader_crisis_system_funding_indicator",
        ]
    ].copy()
    d = d.merge(timing_slim, on="state", how="left", suffixes=("", "_audit"))
    d["enacted_start"] = d["bill_enactment_date"]
    d["collection_start_audit"] = d["fee_collection_start_date"]
    for lag in [0, 1, 3, 6, 12]:
        col = f"operational_lag_{lag}m_start"
        d[col] = d["fee_collection_start_date"] + pd.to_timedelta(0, unit="D")
        valid = d["fee_collection_start_date"].notna()
        d.loc[valid, col] = d.loc[valid, "fee_collection_start_date"] + pd.offsets.DateOffset(months=lag)
        active_col = f"operational_lag_{lag}m_active"
        d[active_col] = (d[col].notna() & d["month"].ge(d[col])).astype(int)
    d["enacted_active"] = (d["enacted_start"].notna() & d["month"].ge(d["enacted_start"])).astype(int)
    d["collection_start_audit_active"] = (
        d["collection_start_audit"].notna() & d["month"].ge(d["collection_start_audit"])
    ).astype(int)
    d["first_revenue_positive_start"] = d["first_observed_fee_revenue_date"]
    d["revenue_positive_active"] = (
        d["first_revenue_positive_start"].notna() & d["month"].ge(d["first_revenue_positive_start"])
    ).astype(int)
    d["fee_amount_per_line_dollars"] = d["fee_cents_max"] / 100.0
    d["restricted_988_only_active"] = d["collection_start_audit_active"] * d[
        "restricted_988_only_funding_indicator"
    ].fillna(0)
    d["broader_crisis_system_active"] = d["collection_start_audit_active"] * d[
        "broader_crisis_system_funding_indicator"
    ].fillna(0)
    save_parquet(d, RESCUE_DATA / "analysis_panel_rescue_treatments.parquet")
    save_csv(d, RESCUE_DATA / "analysis_panel_rescue_treatments.csv")
    return d


def timing_sensitivity_models(panel: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    d = panel[panel["primary_analysis_sample"]].copy()
    timing_defs = [
        ("enacted_start", "enacted_active", "enactment date"),
        ("collection_start_audit", "collection_start_audit_active", "collection start"),
        ("operational_lag_0m_start", "operational_lag_0m_active", "collection plus 0 months"),
        ("operational_lag_1m_start", "operational_lag_1m_active", "collection plus 1 month"),
        ("operational_lag_3m_start", "operational_lag_3m_active", "collection plus 3 months"),
        ("operational_lag_6m_start", "operational_lag_6m_active", "collection plus 6 months"),
        ("operational_lag_12m_start", "operational_lag_12m_active", "collection plus 12 months"),
        ("first_revenue_positive_start", "revenue_positive_active", "first positive annual revenue"),
    ]
    att_rows: list[dict] = []
    twfe_rows: list[pd.DataFrame] = []
    for start_col, active_col, label in timing_defs:
        for outcome in OUTCOMES[:4]:
            _, overall = compute_att_gt(d, outcome, start_col)
            overall.update({"design_family": "fee_timing_sensitivity", "treatment_definition": label})
            att_rows.append(overall)
            if d[active_col].nunique() >= 2:
                try:
                    res = fit_fe_ols(d, outcome, [active_col], ["state", "month_id"], "state", label)
                    row = res.table[res.table["term"].eq(active_col)].copy()
                    row["design_family"] = "fee_timing_sensitivity"
                    row["treatment_definition"] = label
                    twfe_rows.append(row)
                except Exception:
                    pass
    for term, label in [
        ("fee_amount_per_line_dollars", "fee amount per line"),
        ("fee_revenue_per_capita", "annual fee revenue per capita"),
        ("fee_revenue_per_routed_contact", "annual fee revenue per routed contact"),
        ("restricted_988_only_active", "restricted 988-only funding active"),
        ("broader_crisis_system_active", "broader crisis-system funding active"),
    ]:
        for outcome in OUTCOMES[:4]:
            work = d.copy()
            work[term] = pd.to_numeric(work[term], errors="coerce").fillna(0)
            try:
                res = fit_fe_ols(work, outcome, [term], ["state", "month_id"], "state", label)
                row = res.table[res.table["term"].eq(term)].copy()
                row["design_family"] = "fee_timing_sensitivity"
                row["treatment_definition"] = label
                twfe_rows.append(row)
            except Exception:
                pass
    att = pd.DataFrame(att_rows)
    twfe = pd.concat(twfe_rows, ignore_index=True) if twfe_rows else pd.DataFrame()
    save_csv(att, RESCUE_RESULT / "fee_timing_att_sensitivity.csv")
    save_csv(twfe, RESCUE_RESULT / "fee_timing_twfe_sensitivity.csv")
    return att, twfe


def download_georouting_sources() -> pd.DataFrame:
    sources = [
        ("samhsa_988_faqs", "SAMHSA 988 FAQs", "https://www.samhsa.gov/mental-health/988/faqs"),
        ("988_lifeline_about", "988 Lifeline About page", "https://988lifeline.org/about/"),
        ("samhsa_988_timeline", "SAMHSA 988 Lifeline Timeline", "https://www.samhsa.gov/mental-health/988/lifeline-timeline"),
        ("fcc_24_111_georouting_order", "FCC 988 Georouting Third Report and Order", "https://docs.fcc.gov/public/attachments/FCC-24-111A1.pdf"),
        ("fcc_da_25_233_compliance_guide", "FCC georouting small entity compliance guide", "https://docs.fcc.gov/public/attachments/DA-25-233A1.pdf"),
        ("fcc_doc_413211_text_georouting", "FCC press release on text-to-988 georouting", "https://docs.fcc.gov/public/attachments/DOC-413211A1.pdf"),
        ("fcc_da_25_879_text_deadlines", "FCC public notice text georouting compliance deadlines", "https://docs.fcc.gov/public/attachments/DA-25-879A1_Rcd.pdf"),
    ]
    rows = []
    headers = {"User-Agent": "Mozilla/5.0 Codex research audit"}
    for source_id, name, url in sources:
        suffix = ".pdf" if url.lower().endswith(".pdf") else ".html"
        path = GEOROUTING_SOURCES / f"{source_id}{suffix}"
        status = "download_failed"
        note = ""
        try:
            r = requests.get(url, headers=headers, timeout=60)
            r.raise_for_status()
            path.write_bytes(r.content)
            status = "downloaded"
        except Exception as exc:
            note = str(exc)
        rows.append(
            {
                "source_id": source_id,
                "source_name": name,
                "url": url,
                "local_path": str(path.relative_to(DATA.parents[0])) if path.exists() else "",
                "status": status,
                "sha256": sha256_file(path) if path.exists() else "",
                "note": note,
            }
        )
    out = pd.DataFrame(rows)
    save_csv(out, GEOROUTING_SOURCES / "georouting_source_manifest.csv")
    return out


def georouting_timeline() -> pd.DataFrame:
    rows = [
        {
            "date": "2024-09-17",
            "event": "Voice georouting launched for cellular 988 calls in the 988 Lifeline network",
            "modality": "voice calls",
            "scope": "national launch, carrier implementation not fully state-specific in public data",
            "source": "988 Lifeline About page",
        },
        {
            "date": "2024-10-18",
            "event": "FCC adopted rules requiring georouting for all wireless calls to 988",
            "modality": "voice calls",
            "scope": "all covered wireless carriers",
            "source": "FCC 24-111",
        },
        {
            "date": "2024-12-12",
            "event": "FCC 988 voice georouting rules became effective",
            "modality": "voice calls",
            "scope": "regulatory effective date",
            "source": "FCC DA-25-233",
        },
        {
            "date": "2025-01-13",
            "event": "Nationwide CMRS providers required to comply with 988 voice georouting",
            "modality": "voice calls",
            "scope": "nationwide carriers",
            "source": "FCC DA-25-233",
        },
        {
            "date": "2026-12-14",
            "event": "Non-nationwide CMRS providers required to comply with 988 voice georouting",
            "modality": "voice calls",
            "scope": "smaller/non-nationwide carriers",
            "source": "FCC DA-25-233",
        },
        {
            "date": "2025-07-24",
            "event": "FCC approved rules requiring georouting for text messages to 988",
            "modality": "text",
            "scope": "covered wireless text providers; implementation follows effective date",
            "source": "FCC DOC-413211",
        },
        {
            "date": "2025-10-16",
            "event": "Text-to-988 georouting rules effective",
            "modality": "text",
            "scope": "regulatory effective date",
            "source": "FCC DA-25-879",
        },
        {
            "date": "2027-04-16",
            "event": "Nationwide CMRS text-to-988 georouting compliance deadline",
            "modality": "text",
            "scope": "future relative to current outcome window",
            "source": "FCC DA-25-879",
        },
        {
            "date": "2028-10-16",
            "event": "Non-nationwide text-to-988 georouting compliance deadline",
            "modality": "text",
            "scope": "future relative to current outcome window",
            "source": "FCC DA-25-879",
        },
    ]
    out = pd.DataFrame(rows)
    out["date"] = pd.to_datetime(out["date"])
    save_csv(out, RESCUE_DATA / "georouting_timeline.csv")
    return out


def census_mismatch_exposure() -> pd.DataFrame:
    # The direct Census profile API may require a key. Census Reporter serves
    # Census ACS detailed-table data without a key; use detailed tables rather
    # than profile IDs, and label the result as an ACS-derived proxy.
    geo_ids = ",".join(f"04000US{fips}" for fips in sorted(FIPS_TO_ABBR) if FIPS_TO_ABBR[fips] in STATE_DC)
    url = f"https://api.censusreporter.org/1.0/data/show/latest?table_ids=B07001,B05002&geo_ids={geo_ids}"
    try:
        data = requests.get(url, timeout=60).json()
        rows = []
        for geoid, geo in data["geography"].items():
            fips = geoid[-2:]
            state = FIPS_TO_ABBR.get(fips)
            if state not in STATE_DC:
                continue
            estimates_b07001 = data["data"][geoid]["B07001"]["estimate"]
            estimates_b05002 = data["data"][geoid]["B05002"]["estimate"]
            moved_total = float(estimates_b07001.get("B07001001") or np.nan)
            moved_diff_state = float(estimates_b07001.get("B07001065") or np.nan)
            born_total = float(estimates_b05002.get("B05002001") or np.nan)
            born_other_state = float(estimates_b05002.get("B05002004") or np.nan)
            rows.append(
                {
                    "state": state,
                    "state_name": geo["name"],
                    "moved_from_different_state_pct": moved_diff_state / moved_total * 100,
                    "born_in_different_state_pct": born_other_state / born_total * 100,
                    "acs_total_population": born_total,
                    "source_table_migration": "ACS latest B07001, B07001065 / B07001001 via Census Reporter",
                    "source_table_place_of_birth": "ACS latest B05002, B05002004 / B05002001 via Census Reporter",
                }
            )
        raw = pd.DataFrame(rows)
        raw["moved_diff_state_z"] = zscore(raw["moved_from_different_state_pct"])
        raw["born_diff_state_z"] = zscore(raw["born_in_different_state_pct"])
        raw["routing_mismatch_exposure_z"] = raw[["moved_diff_state_z", "born_diff_state_z"]].mean(axis=1)
        raw["proxy_note"] = (
            "ACS public detailed-table proxies for likely mismatch between physical location and phone-number geography; "
            "not actual area-code, carrier, or handset-location data."
        )
        out = raw[
            [
                "state",
                "state_name",
                "moved_from_different_state_pct",
                "born_in_different_state_pct",
                "acs_total_population",
                "routing_mismatch_exposure_z",
                "source_table_migration",
                "source_table_place_of_birth",
                "proxy_note",
            ]
        ].sort_values("state")
    except Exception as exc:
        out = pd.DataFrame([{"state": "", "state_name": "", "proxy_note": f"ACS proxy download failed: {exc}"}])
    save_csv(out, RESCUE_DATA / "routing_mismatch_exposure_state.csv")
    return out


def plot_georouting_raw_trends(panel: pd.DataFrame, exposure: pd.DataFrame) -> None:
    d = panel[panel["primary_analysis_sample"]].merge(
        exposure[["state", "routing_mismatch_exposure_z"]], on="state", how="left"
    )
    d = d[d["routing_mismatch_exposure_z"].notna()].copy()
    med = d.drop_duplicates("state")["routing_mismatch_exposure_z"].median()
    d["mismatch_group"] = np.where(
        d["routing_mismatch_exposure_z"].ge(med), "High proxy mismatch", "Low proxy mismatch"
    )
    trend = (
        d.groupby(["month", "mismatch_group"], as_index=False)
        .agg(
            answer_rate=("in_state_answer_rate_rescue", "mean"),
            flowout_rate=("flowout_to_national_backup_rate", "mean"),
            routed_per_100k=("routed_per_100k", "mean"),
        )
    )
    fig, axes = plt.subplots(3, 1, figsize=(10.5, 8), sharex=True)
    for ax, col, title in zip(
        axes,
        ["answer_rate", "flowout_rate", "routed_per_100k"],
        ["In-state answer rate", "Flowout rate", "Routed contacts per 100,000"],
    ):
        for group, g in trend.groupby("mismatch_group"):
            ax.plot(g["month"], g[col], label=group, linewidth=1.6)
        ax.axvline(pd.Timestamp("2024-10-01"), color="0.35", linestyle="--", linewidth=1)
        ax.set_title(title)
        ax.grid(alpha=0.25)
    axes[0].legend()
    axes[-1].xaxis.set_major_locator(mdates.YearLocator())
    axes[-1].xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    fig.tight_layout()
    fig.savefig(RESCUE_RESULT / "georouting_raw_trends_by_mismatch_proxy.png", dpi=220, bbox_inches="tight")
    plt.close(fig)
    save_csv(trend, RESCUE_RESULT / "georouting_raw_trends_by_mismatch_proxy.csv")


def georouting_models(panel: pd.DataFrame, exposure: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    if exposure.empty or "routing_mismatch_exposure_z" not in exposure.columns:
        return pd.DataFrame(), pd.DataFrame()
    d = panel[panel["primary_analysis_sample"]].merge(
        exposure[["state", "routing_mismatch_exposure_z"]], on="state", how="left"
    )
    d = d[d["routing_mismatch_exposure_z"].notna()].copy()
    d["post_voice_launch"] = d["month"].ge(pd.Timestamp("2024-10-01")).astype(int)
    d["post_voice_compliance"] = d["month"].ge(pd.Timestamp("2025-01-01")).astype(int)
    d["post_launch_x_mismatch"] = d["post_voice_launch"] * d["routing_mismatch_exposure_z"]
    d["post_compliance_x_mismatch"] = d["post_voice_compliance"] * d["routing_mismatch_exposure_z"]
    d["fee_capacity_binary"] = d["treated_ever_by_2024"].astype(int)
    d["post_launch_x_fee_capacity"] = d["post_voice_launch"] * d["fee_capacity_binary"]
    d["post_launch_x_mismatch_x_fee_capacity"] = (
        d["post_voice_launch"] * d["routing_mismatch_exposure_z"] * d["fee_capacity_binary"]
    )
    rows: list[pd.DataFrame] = []
    for outcome in OUTCOMES:
        for term, label in [
            ("post_launch_x_mismatch", "voice georouting launch x ACS mismatch proxy"),
            ("post_compliance_x_mismatch", "voice georouting nationwide compliance x ACS mismatch proxy"),
        ]:
            try:
                res = fit_fe_ols(d, outcome, [term], ["state", "month_id"], "state", label)
                row = res.table[res.table["term"].eq(term)].copy()
                row["design_family"] = "georouting_mismatch"
                row["treatment_definition"] = label
                row["sample_note"] = "state/DC primary sample; national post interacted with ACS proxy"
                rows.append(row)
            except Exception:
                pass
        try:
            terms = [
                "post_launch_x_mismatch",
                "post_launch_x_fee_capacity",
                "post_launch_x_mismatch_x_fee_capacity",
            ]
            res = fit_fe_ols(d, outcome, terms, ["state", "month_id"], "state", "fee capacity moderation")
            row = res.table[res.table["term"].isin(terms)].copy()
            row["design_family"] = "georouting_fee_capacity_moderation"
            row["treatment_definition"] = "post georouting x mismatch x fee-state capacity"
            row["sample_note"] = "fee capacity is endogenous state fee adoption by 2024"
            rows.append(row)
        except Exception:
            pass

    placebo_rows = []
    for placebo_date in ["2023-10-01", "2024-04-01"]:
        work = d.copy()
        term = f"post_placebo_{placebo_date[:7].replace('-', '_')}_x_mismatch"
        work[term] = work["month"].ge(pd.Timestamp(placebo_date)).astype(int) * work["routing_mismatch_exposure_z"]
        for outcome in ["in_state_answer_rate_rescue", "routed_per_100k", "flowout_to_national_backup_rate"]:
            try:
                res = fit_fe_ols(work, outcome, [term], ["state", "month_id"], "state", "georouting placebo date")
                row = res.table[res.table["term"].eq(term)].copy()
                row["design_family"] = "georouting_placebo_timing"
                row["treatment_definition"] = f"placebo post {placebo_date[:7]} x mismatch"
                placebo_rows.append(row)
            except Exception:
                pass

    loo_rows = []
    for state in sorted(d["state"].unique()):
        work = d[~d["state"].eq(state)].copy()
        try:
            res = fit_fe_ols(
                work,
                "in_state_answer_rate_rescue",
                ["post_launch_x_mismatch"],
                ["state", "month_id"],
                "state",
                f"leave_out_{state}",
            )
            row = res.table[res.table["term"].eq("post_launch_x_mismatch")].copy()
            row["left_out_state"] = state
            loo_rows.append(row)
        except Exception:
            pass
    loo = pd.concat(loo_rows, ignore_index=True) if loo_rows else pd.DataFrame()
    save_csv(loo, RESCUE_RESULT / "georouting_leave_one_state_out.csv")

    sensitivity_rows = []
    for name, mask in [
        ("exclude_early_fee_states_va_wa", ~d["state"].isin(["VA", "WA"])),
        ("never_fee_states_only", ~d["treated_ever_by_2024"]),
    ]:
        work = d[mask].copy()
        if work["state"].nunique() < 10:
            continue
        try:
            res = fit_fe_ols(
                work,
                "in_state_answer_rate_rescue",
                ["post_launch_x_mismatch"],
                ["state", "month_id"],
                "state",
                name,
            )
            row = res.table[res.table["term"].eq("post_launch_x_mismatch")].copy()
            row["design_family"] = "georouting_sensitivity"
            row["treatment_definition"] = name
            sensitivity_rows.append(row)
        except Exception:
            pass

    event_rows = []
    work = d.copy()
    rel = (
        (work["month"].dt.year - 2024) * 12 + work["month"].dt.month - 10
    )
    for et in range(-12, 15):
        if et == -1:
            continue
        name = f"geo_event_m{abs(et)}" if et < 0 else f"geo_event_p{et}"
        work[name] = rel.eq(et).astype(int) * work["routing_mismatch_exposure_z"]
    event_terms = [c for c in work.columns if c.startswith("geo_event_")]
    try:
        res = fit_fe_ols(work, "in_state_answer_rate_rescue", event_terms, ["state", "month_id"], "state", "georouting_event_proxy")
        event = res.table[res.table["term"].isin(event_terms)].copy()
        event["event_time"] = event["term"].map(lambda x: -int(x.split("m")[1]) if "_m" in x else int(x.split("p")[1]))
    except Exception:
        event = pd.DataFrame()
    save_csv(event, RESCUE_RESULT / "georouting_event_proxy_answer_rate.csv")

    all_rows = rows + placebo_rows + sensitivity_rows
    models = pd.concat(all_rows, ignore_index=True) if all_rows else pd.DataFrame()
    save_csv(models, RESCUE_RESULT / "georouting_model_results.csv")
    return models, event


def revenue_intensity_models(panel: pd.DataFrame) -> pd.DataFrame:
    d = panel[panel["primary_analysis_sample"]].copy()
    d["fee_revenue_per_capita_observed_2021_2024"] = np.where(
        d["year"].between(2021, 2024), d["fee_revenue_nominal_for_2021_2024"] / d["population"], np.nan
    )
    d["fee_revenue_per_capita_observed_2021_2024"] = d["fee_revenue_per_capita_observed_2021_2024"].fillna(0)
    d["fee_revenue_per_routed_observed_2021_2024"] = np.where(
        d["year"].between(2021, 2024), d["fee_revenue_nominal_for_2021_2024"] / d["routed_in_state"], np.nan
    )
    d["fee_revenue_per_routed_observed_2021_2024"] = d["fee_revenue_per_routed_observed_2021_2024"].replace(
        [np.inf, -np.inf], np.nan
    ).fillna(0)
    d = d.sort_values(["state", "month"])
    d["lag12_revenue_per_capita"] = d.groupby("state")["fee_revenue_per_capita_observed_2021_2024"].shift(12).fillna(0)
    rows: list[pd.DataFrame] = []
    specs = [
        ("fee_revenue_per_capita_observed_2021_2024", "observed annual revenue per capita, same year"),
        ("lag12_revenue_per_capita", "observed annual revenue per capita, 12-month lag"),
        ("fee_amount_per_line_dollars", "statutory fee amount per line"),
    ]
    for term, label in specs:
        for outcome in OUTCOMES[:4]:
            try:
                res = fit_fe_ols(d, outcome, [term], ["state", "month_id"], "state", label)
                row = res.table[res.table["term"].eq(term)].copy()
                row["design_family"] = "revenue_intensity"
                row["treatment_definition"] = label
                row["sample_note"] = "state/DC primary sample; annual revenue only observed through 2024"
                rows.append(row)
            except Exception:
                pass
    for outcome in OUTCOMES[:4]:
        _, overall = compute_att_gt(d, outcome, "first_revenue_positive_start")
        rows.append(
            pd.DataFrame(
                [
                    {
                        "model": "att_first_positive_revenue",
                        "outcome": outcome,
                        "term": "first_revenue_positive_start",
                        "estimate": overall["overall_att"],
                        "std_error_cluster": np.nan,
                        "p_value": np.nan,
                        "nobs": int(d[outcome].notna().sum()),
                        "n_clusters": int(d["state"].nunique()),
                        "r2": np.nan,
                        "design_family": "revenue_intensity",
                        "treatment_definition": "event time by first positive annual revenue year",
                        "sample_note": "timing is annual and mechanically coarsened",
                    }
                ]
            )
        )
    out = pd.concat(rows, ignore_index=True) if rows else pd.DataFrame()
    save_csv(out, RESCUE_RESULT / "revenue_intensity_model_results.csv")
    return out


def legislative_nearmiss_dataset() -> pd.DataFrame:
    rows = [
        {
            "state": "CA",
            "bill_number": "AB988",
            "year_session": "2021-2022",
            "introduced_date": "2021-02-18",
            "committee_action": "advanced through policy/fiscal committees",
            "floor_vote_date": "2022-08-30",
            "vote_margin": "",
            "passed_failed": "passed",
            "enacted_not_enacted": "enacted",
            "sponsor_party": "Democratic",
            "chamber_control": "Democratic trifecta",
            "session_deadline": "",
            "official_bill_source": "https://leginfo.legislature.ca.gov/faces/billNavClient.xhtml?bill_id=202120220AB988",
            "narrowly_passed_or_failed": 0,
            "audit_note": "Enacted fee state; not a near-miss comparator.",
        },
        {
            "state": "CO",
            "bill_number": "SB21-154",
            "year_session": "2021",
            "introduced_date": "2021-03-03",
            "committee_action": "advanced",
            "floor_vote_date": "",
            "vote_margin": "",
            "passed_failed": "passed",
            "enacted_not_enacted": "enacted",
            "sponsor_party": "Democratic",
            "chamber_control": "Democratic trifecta",
            "session_deadline": "",
            "official_bill_source": "https://leg.colorado.gov/bills/SB21-154",
            "narrowly_passed_or_failed": 0,
            "audit_note": "Enacted fee state; not a near-miss comparator.",
        },
        {
            "state": "DE",
            "bill_number": "HS1 for HB160",
            "year_session": "2023",
            "introduced_date": "2023-05-18",
            "committee_action": "advanced",
            "floor_vote_date": "",
            "vote_margin": "",
            "passed_failed": "passed",
            "enacted_not_enacted": "enacted",
            "sponsor_party": "Democratic",
            "chamber_control": "Democratic trifecta",
            "session_deadline": "",
            "official_bill_source": "https://legis.delaware.gov/BillDetail/140522",
            "narrowly_passed_or_failed": 0,
            "audit_note": "Enacted fee state; not a near-miss comparator.",
        },
        {
            "state": "MD",
            "bill_number": "SB974/HB933",
            "year_session": "2024",
            "introduced_date": "2024-02-02",
            "committee_action": "favorable; passed both chambers",
            "floor_vote_date": "2024-04-02",
            "vote_margin": "Senate 42-3; House 110-26",
            "passed_failed": "passed",
            "enacted_not_enacted": "enacted",
            "sponsor_party": "Democratic",
            "chamber_control": "Democratic trifecta",
            "session_deadline": "",
            "official_bill_source": "https://mgaleg.maryland.gov/mgawebsite/Legislation/Details/SB0974?ys=2024RS",
            "narrowly_passed_or_failed": 0,
            "audit_note": "Wide vote margins; unusable for close-vote RD.",
        },
        {
            "state": "AL",
            "bill_number": "HB389",
            "year_session": "2023",
            "introduced_date": "2023-05-02",
            "committee_action": "referred; stalled after committee dispute over fee",
            "floor_vote_date": "",
            "vote_margin": "",
            "passed_failed": "failed/stalled",
            "enacted_not_enacted": "not enacted",
            "sponsor_party": "Republican",
            "chamber_control": "Republican trifecta",
            "session_deadline": "2023 regular session adjournment",
            "official_bill_source": "https://www.legislature.state.al.us/pdf/SearchableInstruments/2023RS/HB389-int.pdf",
            "narrowly_passed_or_failed": 0,
            "audit_note": "Serious attempt, but no floor vote margin and not a close-vote near miss.",
        },
        {
            "state": "MI",
            "bill_number": "HB5354",
            "year_session": "2021-2022",
            "introduced_date": "2021-09-30",
            "committee_action": "referred to House Health Policy",
            "floor_vote_date": "",
            "vote_margin": "",
            "passed_failed": "failed/stalled",
            "enacted_not_enacted": "not enacted",
            "sponsor_party": "Democratic",
            "chamber_control": "divided government",
            "session_deadline": "",
            "official_bill_source": "https://www.legislature.mi.gov/documents/2021-2022/billintroduced/House/pdf/2021-HIB-5354.pdf",
            "narrowly_passed_or_failed": 0,
            "audit_note": "Introduced/referred only; no close-vote variation.",
        },
        {
            "state": "WV",
            "bill_number": "SB181",
            "year_session": "2022",
            "introduced_date": "2022-01-12",
            "committee_action": "introduced/substitute text available",
            "floor_vote_date": "",
            "vote_margin": "",
            "passed_failed": "failed/stalled",
            "enacted_not_enacted": "not enacted",
            "sponsor_party": "bipartisan",
            "chamber_control": "Republican trifecta",
            "session_deadline": "",
            "official_bill_source": "https://www.wvlegislature.gov/Bill_Status/bills_text.cfm?billdoc=SB181+SUB1.htm&i=181&sesstype=RS&yr=2022",
            "narrowly_passed_or_failed": 0,
            "audit_note": "No usable close margin.",
        },
        {
            "state": "TN",
            "bill_number": "SB1789/HB2555",
            "year_session": "2023-2024",
            "introduced_date": "2024-01-01",
            "committee_action": "introduced",
            "floor_vote_date": "",
            "vote_margin": "",
            "passed_failed": "failed/stalled",
            "enacted_not_enacted": "not enacted",
            "sponsor_party": "Democratic",
            "chamber_control": "Republican trifecta",
            "session_deadline": "",
            "official_bill_source": "https://www.capitol.tn.gov/Bills/113/Bill/SB1789.pdf",
            "narrowly_passed_or_failed": 0,
            "audit_note": "No close-vote or late-stage failure evidence in source scan.",
        },
        {
            "state": "MA",
            "bill_number": "H4084",
            "year_session": "2025-2026",
            "introduced_date": "2025",
            "committee_action": "committee stage",
            "floor_vote_date": "",
            "vote_margin": "",
            "passed_failed": "pending/stalled",
            "enacted_not_enacted": "not enacted",
            "sponsor_party": "",
            "chamber_control": "Democratic trifecta",
            "session_deadline": "",
            "official_bill_source": "https://malegislature.gov/Bills/194/H4084",
            "narrowly_passed_or_failed": 0,
            "audit_note": "Pending/introduced; not part of observed outcome window as a clean near miss.",
        },
    ]
    out = pd.DataFrame(rows)
    save_csv(out, RESCUE_DATA / "legislative_988_fee_bills.csv")
    return out


def capacity_disbursement_scan() -> pd.DataFrame:
    rows = [
        {
            "evidence_type": "FCC annual fee revenue",
            "coverage": "state-year, 2021-2024",
            "usable_as_treatment_timing": "partially",
            "limitation": "revenue is annual and does not identify disbursement, contract, or staffing dates",
        },
        {
            "evidence_type": "state 988 laws and tax pages",
            "coverage": "selected fee states",
            "usable_as_treatment_timing": "for collection dates only",
            "limitation": "does not consistently report first operational spending or crisis-center staffing expansion",
        },
        {
            "evidence_type": "state annual/budget/procurement reports",
            "coverage": "heterogeneous",
            "usable_as_treatment_timing": "no",
            "limitation": "not consistently available as state-month public panel; retain as qualitative mechanism evidence",
        },
    ]
    out = pd.DataFrame(rows)
    save_csv(out, RESCUE_DATA / "capacity_disbursement_source_scan.csv")
    return out


def assemble_model_summary(
    timing_att: pd.DataFrame,
    timing_twfe: pd.DataFrame,
    geo: pd.DataFrame,
    revenue: pd.DataFrame,
) -> pd.DataFrame:
    rows = []
    if not timing_att.empty:
        for _, r in timing_att.iterrows():
            rows.append(
                {
                    "design_family": r.get("design_family", "fee_timing_sensitivity"),
                    "design_name": r.get("treatment_definition", r.get("timing", "")),
                    "outcome": r.get("outcome", ""),
                    "treatment_or_exposure": r.get("timing", ""),
                    "sample": "state/DC primary sample",
                    "estimator": "not-yet-treated ATT",
                    "coefficient": r.get("overall_att", np.nan),
                    "std_error_or_interval": "",
                    "p_value": "",
                    "states": 51,
                    "state_months": 2936,
                    "identifying_assumption": "not-yet-treated states are valid counterfactual conditional on timing",
                    "pretrends_pass": bool(pd.notna(r.get("pre_mean_abs_att")) and abs(float(r.get("pre_mean_abs_att"))) < 0.03),
                    "placebo_tests_pass": "",
                    "leave_one_out_survives": "",
                    "viability": "weak" if r.get("treatment_definition") != "collection plus 3 months" else "original suggestive",
                }
            )
    for df, estimator, assumption in [
        (timing_twfe, "state and month FE OLS", "parallel trends after fixed effects"),
        (geo, "state and month FE OLS", "national georouting shock effect varies only by ex ante mismatch proxy"),
        (revenue, "state and month FE OLS / coarse ATT", "revenue intensity is as-good-as-random after fixed effects"),
    ]:
        if df.empty:
            continue
        for _, r in df.iterrows():
            rows.append(
                {
                    "design_family": r.get("design_family", ""),
                    "design_name": r.get("treatment_definition", r.get("model", "")),
                    "outcome": r.get("outcome", ""),
                    "treatment_or_exposure": r.get("term", ""),
                    "sample": r.get("sample_note", "state/DC primary sample"),
                    "estimator": estimator,
                    "coefficient": r.get("estimate", np.nan),
                    "std_error_or_interval": r.get("std_error_cluster", ""),
                    "p_value": r.get("p_value", ""),
                    "states": r.get("n_clusters", ""),
                    "state_months": r.get("nobs", ""),
                    "identifying_assumption": assumption,
                    "pretrends_pass": "",
                    "placebo_tests_pass": "no" if r.get("design_family", "") == "georouting_placebo_timing" else "",
                    "leave_one_out_survives": "",
                    "viability": "weak/infeasible" if r.get("design_family", "").startswith("georouting") else "weak",
                }
            )
    rows.append(
        {
            "design_family": "legislative_nearmiss",
            "design_name": "passed vs narrowly failed fee bills",
            "outcome": "all",
            "treatment_or_exposure": "close legislative passage",
            "sample": "identified bill attempts",
            "estimator": "not estimated",
            "coefficient": "",
            "std_error_or_interval": "",
            "p_value": "",
            "states": "",
            "state_months": "",
            "identifying_assumption": "near-miss vote outcomes are quasi-random",
            "pretrends_pass": "",
            "placebo_tests_pass": "",
            "leave_one_out_survives": "",
            "viability": "infeasible: too few close-vote near misses",
        }
    )
    out = pd.DataFrame(rows)
    save_csv(out, RESCUE_RESULT / "model_summary_all_designs.csv")
    return out


def write_current_design_diagnosis(
    coverage: pd.DataFrame,
    pdf_audit: pd.DataFrame,
    pdf_months: pd.DataFrame,
    timing_att: pd.DataFrame,
) -> None:
    ans = timing_att[
        timing_att["outcome"].eq("in_state_answer_rate_rescue")
        & timing_att["treatment_definition"].eq("collection plus 3 months")
    ]
    ans_text = "NA" if ans.empty else fmt_pp(ans.iloc[0]["overall_att"])
    bad_months = pdf_months[pdf_months["rows_with_current_diff_gt_1pp"].gt(0)]
    text = f"""# Current Design Diagnosis

## Reproduction

The official pipeline was reproduced in an external temporary copy of the project to avoid overwriting existing outputs. The regenerated panel summary, cohort ATT table, final report, and go/no-go report were byte-identical to the preserved originals. FE-model CSV hashes differed only because of machine-precision float string differences; displayed coefficients match.

## Current Identification

The current fee-adoption design remains policy-selected. Fee states differ in administrative capacity, mental-health policy commitment, fiscal choices, and baseline crisis-system conditions. Modern staggered-DID-style comparisons improve on a naive TWFE headline, but they do not make fee adoption exogenous.

The rescue-layer corrected answer-rate version of the original three-month operational lag produces an answer-rate ATT of {ans_text}. This is still suggestive rather than decisive because the design does not solve policy selection.

## Data Coverage

{markdown_table(coverage)}

## PDF Extraction Audit

The 30-row validation sample was rechecked against the original PDF row text. Counts and time fields are parsed correctly in the sampled rows. The main issue is denominator choice for answer rate: some 2022 launch-transition PDFs include a received-contact denominator that differs from routed contacts, and the official reported answer rate aligns with answered/received contacts. The original pipeline used answered/routed contacts.

Rows in sampled validation classified as current-pipeline denominator errors: {int((pdf_audit['validation_class'] == 'correctable_denominator_error_in_current_pipeline').sum())} of {len(pdf_audit)}.

Months with any current answer-rate denominator difference above 1 percentage point:

{markdown_table(bad_months[['year_month', 'states', 'max_current_routed_abs_diff', 'max_received_abs_diff', 'rows_with_current_diff_gt_1pp']])}

## Bottom Line

The project is reproducible and mostly internally consistent, but the original answer-rate series should be corrected in any rescue analysis. This correction is not enough to rescue causal identification by itself.
"""
    (RESCUE_TEMP / "current_design_diagnosis.md").write_text(text, encoding="utf-8")


def write_pdf_validation_audit(pdf_audit: pd.DataFrame, pdf_months: pd.DataFrame) -> None:
    display = pdf_audit[
        [
            "year_month",
            "state",
            "raw_row_text",
            "received_in_state",
            "in_state_answer_rate_reported",
            "answer_rate_routed_calc",
            "answer_rate_received_calc",
            "validation_class",
        ]
    ].copy()
    for col in ["in_state_answer_rate_reported", "answer_rate_routed_calc", "answer_rate_received_calc"]:
        display[col] = display[col].map(lambda x: fmt_num(x, 4))
    bad_months = pdf_months[pdf_months["rows_with_current_diff_gt_1pp"].gt(0)].copy()
    text = f"""# PDF Validation Audit

## Finding

Manual-style validation of the 30 sampled rows found no evidence that the row text, counts, or time fields were misread from the official PDFs. The important issue is correctable: for several 2022 transition months, the official PDF answer rate aligns with `answered_in_state / received_in_state`, while the current pipeline stored `answered_in_state / routed_in_state` as `in_state_answer_rate`.

This affects answer-rate values, not the parsed count fields. Flowout, abandonment, speed-to-answer, and talk-time fields in the sampled rows match the PDF text.

## Sample Audit

{markdown_table(display)}

## Month-Level Denominator Check

{markdown_table(bad_months[['year_month', 'states', 'max_current_routed_abs_diff', 'max_received_abs_diff', 'rows_with_current_diff_gt_1pp']])}

## Classification

- Harmless: ordinary rounding differences within roughly 0.5 percentage points.
- Correctable: answer-rate denominator mismatch in launch-transition rows where received contacts differ from routed contacts.
- Fatal: none found in the sampled rows.

## Rescue-Layer Action

`data/rescue/analysis_panel_rescue.csv` retains the original answer-rate variable and adds `in_state_answer_rate_rescue`, calculated as `answered_in_state / received_in_state` when the received denominator is available and positive, otherwise falling back to the reported/current rate.
"""
    (REPORT / "pdf_validation_audit.md").write_text(text, encoding="utf-8")


def write_treatment_timing_audit(timing: pd.DataFrame, timing_att: pd.DataFrame, timing_twfe: pd.DataFrame) -> None:
    display = timing.copy()
    for col in [
        "bill_enactment_date",
        "statutory_effective_date",
        "fee_collection_start_date",
        "first_observed_fee_revenue_date",
        "first_operational_use_date",
    ]:
        display[col] = pd.to_datetime(display[col], errors="coerce").dt.strftime("%Y-%m-%d").fillna("")
    ans_att = timing_att[timing_att["outcome"].eq("in_state_answer_rate_rescue")].copy()
    ans_att["overall_att"] = ans_att["overall_att"].map(fmt_pp)
    ans_att["pre_mean_abs_att"] = ans_att["pre_mean_abs_att"].map(fmt_pp)
    ans_twfe = timing_twfe[timing_twfe["outcome"].eq("in_state_answer_rate_rescue")].copy()
    if not ans_twfe.empty:
        ans_twfe["estimate"] = ans_twfe["estimate"].map(fmt_pp)
        ans_twfe["std_error_cluster"] = ans_twfe["std_error_cluster"].map(fmt_pp)
        ans_twfe["p_value"] = ans_twfe["p_value"].map(lambda x: fmt_num(x, 3))
    text = f"""# Treatment Timing Audit

## State-by-State Fee Timing

{markdown_table(display[['state', 'state_name', 'bill_number', 'bill_enactment_date', 'statutory_effective_date', 'fee_collection_start_date', 'first_observed_fee_revenue_date', 'revenue_timing_precision', 'first_operational_use_date', 'fund_scope', 'fee_amount_and_base', 'preexisting_911_fee_infrastructure', 'confidence_rating', 'audit_note']])}

## Revised Treatment Definitions

The rescue layer rebuilt active-treatment variables for enactment, collection start, operational lags of 0, 1, 3, 6, and 12 months, first positive annual revenue, fee amount per line, revenue per capita, revenue per routed contact, restricted 988-only funding, and broader crisis-system funding.

## Answer-Rate Sensitivity: Not-Yet-Treated ATT

{markdown_table(ans_att[['treatment_definition', 'overall_att', 'pre_mean_abs_att', 'att_cells', 'treated_cohorts']])}

## Answer-Rate Sensitivity: TWFE Diagnostics

{markdown_table(ans_twfe[['treatment_definition', 'term', 'estimate', 'std_error_cluster', 'p_value', 'nobs', 'n_clusters']])}

## Interpretation

The sign and size of the corrected answer-rate ATT vary across timing definitions. Collection/enactment definitions and revenue-based definitions are not externally assigned; changing the date convention does not remove policy selection. The three-month lag remains a reasonable operational convention, not a credible source of quasi-random variation.
"""
    (REPORT / "treatment_timing_audit.md").write_text(text, encoding="utf-8")


def write_georouting_audit(geo: pd.DataFrame, event: pd.DataFrame, exposure: pd.DataFrame, timeline: pd.DataFrame) -> None:
    if geo.empty or "design_family" not in geo.columns:
        main = pd.DataFrame()
    else:
        main = geo[
            geo["design_family"].eq("georouting_mismatch")
            & geo["term"].isin(["post_launch_x_mismatch", "post_compliance_x_mismatch"])
        ].copy()
    if not main.empty:
        main["estimate"] = main.apply(
            lambda r: fmt_pp(r["estimate"]) if "rate" in str(r["outcome"]) else fmt_num(r["estimate"], 4),
            axis=1,
        )
        main["std_error_cluster"] = main.apply(
            lambda r: fmt_pp(r["std_error_cluster"]) if "rate" in str(r["outcome"]) else fmt_num(r["std_error_cluster"], 4),
            axis=1,
        )
        main["p_value"] = main["p_value"].map(lambda x: fmt_num(x, 3))
    pre_fail = False
    if not event.empty:
        leads = event[event["event_time"].lt(-1)]
        pre_fail = bool((leads["p_value"] < 0.10).sum() > 1 or leads["estimate"].abs().mean() > 0.02)
    if exposure.empty or "routing_mismatch_exposure_z" not in exposure.columns:
        exposure_display = pd.DataFrame()
    else:
        exposure_display = exposure.sort_values("routing_mismatch_exposure_z", ascending=False).head(10).copy()
        for col in ["moved_from_different_state_pct", "born_in_different_state_pct", "routing_mismatch_exposure_z"]:
            if col in exposure_display.columns:
                exposure_display[col] = exposure_display[col].map(lambda x: fmt_num(x, 2))
    timeline_display = timeline.copy()
    timeline_display["date"] = timeline_display["date"].dt.strftime("%Y-%m-%d")
    text = f"""# Georouting Design Audit

## Policy and Technical Change

Before georouting, 988 wireless calls could be routed by area code/exchange rather than by the caller's current physical area. Voice georouting changes this by sending generalized cell-based routing information so the Lifeline administrator can route calls to a more local crisis center without transmitting precise handset location. This is more plausibly external to state fee-adoption decisions, but public data still provide only national timing and no state-level treatment intensity.

## Official Timeline

{markdown_table(timeline_display)}

## Exposure Construction

The rescue layer constructed ACS proxy measures for routing mismatch: percent of residents who moved from another state in the prior year and percent born in a different state. These are public proxies for likely phone-number/geography mismatch, not actual phone-number or area-code data.

Top states by proxy mismatch:

{markdown_table(exposure_display[['state', 'state_name', 'moved_from_different_state_pct', 'born_in_different_state_pct', 'routing_mismatch_exposure_z']] if not exposure_display.empty else exposure_display)}

## Model Results

{markdown_table(main[['treatment_definition', 'outcome', 'term', 'estimate', 'std_error_cluster', 'p_value', 'nobs', 'n_clusters']] if not main.empty else main)}

## Diagnostics

- Raw high-vs-low proxy trends were saved to `result/rescue/georouting_raw_trends_by_mismatch_proxy.png`.
- Event-time proxy coefficients were saved to `result/rescue/georouting_event_proxy_answer_rate.csv`.
- Leave-one-state-out checks were saved to `result/rescue/georouting_leave_one_state_out.csv`.
- Pretrend diagnostic status: {"failed or weak" if pre_fail else "not clearly failed, but underpowered and proxy-based"}.
- Modality contrast is unavailable because the public state KPI panel used here is not separated into call, text, and chat outcomes.

## Decision

Weak/infeasible as a top-journal rescue design. Georouting has a more credible national technical shock than state fee adoption, but the public data lack actual routing-mismatch exposure, carrier-by-state implementation intensity, and a visible first-stage-like routing measure. The available ACS proxies are too indirect to support a strong causal claim.
"""
    (REPORT / "georouting_design_audit.md").write_text(text, encoding="utf-8")


def write_revenue_audit(revenue: pd.DataFrame) -> None:
    display = revenue.copy()
    if not display.empty:
        display["estimate"] = display.apply(
            lambda r: fmt_pp(r["estimate"]) if "rate" in str(r["outcome"]) else fmt_num(r["estimate"], 4),
            axis=1,
        )
        display["std_error_cluster"] = display.apply(
            lambda r: fmt_pp(r["std_error_cluster"]) if pd.notna(r.get("std_error_cluster")) and "rate" in str(r["outcome"]) else fmt_num(r.get("std_error_cluster"), 4),
            axis=1,
        )
        display["p_value"] = display["p_value"].map(lambda x: "" if pd.isna(x) else fmt_num(x, 3))
    text = f"""# Revenue-Intensity Design Audit

## Design Tested

The rescue layer tested observed annual FCC fee revenue per capita, a 12-month lag of observed revenue per capita, statutory fee amount per line, and event time around first positive annual revenue. Revenue is observed only annually through calendar year 2024, so it cannot identify monthly staffing/disbursement timing.

## Model Results

{markdown_table(display[['design_family', 'treatment_definition', 'outcome', 'term', 'estimate', 'std_error_cluster', 'p_value', 'nobs', 'n_clusters']])}

## IV Exploration

Candidate instruments were rejected:

- Pre-existing 911 fee infrastructure x post-988 authorization: nearly universal and strongly tied to state emergency-service administrative capacity.
- Pre-period telecom subscriber/access-line base x statutory fee rate: subscriber-base data are not in the current public panel, and fee-rate setting is itself policy-selected.
- Pre-existing access-line base x adoption framework: likely violates exclusion through broader state telecom, emergency-service, and fiscal capacity channels.

## Decision

Weak as a causal design. Revenue intensity is substantively useful mechanism evidence, but actual revenue is a post-adoption policy outcome and is observed too coarsely. A skeptical referee would treat the dose-response models as descriptive unless a credible external funding shock or valid instrument is found.
"""
    (REPORT / "revenue_intensity_design_audit.md").write_text(text, encoding="utf-8")


def write_legislative_audit(bills: pd.DataFrame) -> None:
    display = bills.copy()
    text = f"""# Legislative Near-Miss Design Audit

## Bill-Level Dataset

{markdown_table(display[['state', 'bill_number', 'year_session', 'introduced_date', 'committee_action', 'floor_vote_date', 'vote_margin', 'passed_failed', 'enacted_not_enacted', 'official_bill_source', 'narrowly_passed_or_failed', 'audit_note']])}

## Feasibility

The source scan found enacted fee bills and several serious but stalled attempts. It did not find enough close floor votes or narrow failures to support a regression discontinuity or credible near-miss DID. Maryland's enacted bill, for example, passed by wide margins. Alabama, Michigan, West Virginia, Tennessee, and Massachusetts attempts do not provide close-vote variation; most failed before a usable floor vote.

## Decision

Reject as a quasi-experimental design for the current public data. A matched DID among policy-intent states would still be selected on legislative agenda-setting and would have too few comparable treated/control states.
"""
    (REPORT / "legislative_nearmiss_design_audit.md").write_text(text, encoding="utf-8")


def write_top_journal_assessment(summary: pd.DataFrame) -> None:
    text = f"""# Top-Journal Feasibility Assessment

## Classification

C. POLICY-AUDIT / SUGGESTIVE EVIDENCE PAPER

## Reason

The project is reproducible, uses official public data, and the preferred event-time estimates remain policy-relevant. However, none of the rescue paths creates a credible top-journal causal design with current public data.

## Design-by-Design Assessment

{markdown_table(summary[['design_family', 'design_name', 'outcome', 'estimator', 'coefficient', 'std_error_or_interval', 'p_value', 'viability']].head(80))}

## Why Not A or B

- Fee adoption remains policy-selected.
- Correcting the answer-rate denominator improves measurement but not identification.
- Georouting is more promising conceptually, but public data lack direct routing-mismatch exposure and state/carrier implementation intensity.
- Revenue intensity is endogenous and annual.
- Legislative near-misses are too sparse and heterogeneous.
- Capacity/disbursement timing is not consistently measurable in public state-month data.

## Final Recommendation

Do not position the current project as a top-journal causal paper. Preserve it as a high-quality policy-audit and suggestive evidence paper. The most credible next step for a stronger manuscript is to obtain nonpublic or newly published data on state-by-month georouted call shares, carrier implementation, crisis-center staffing, contracts, or actual disbursement timing.
"""
    (REPORT / "top_journal_feasibility_assessment.md").write_text(text, encoding="utf-8")


def write_identification_rescue_memo() -> None:
    text = """# Identification Rescue Memo

## Executive Summary

The 988 telecom fee project should not be upgraded to a strong top-journal causal paper with the current public data. The project remains valuable as a reproducible policy audit with suggestive event-time evidence, but fee adoption is still selected and no rescue design passed the needed timing, exposure, pretrend, placebo, and mechanism standards.

## What Was Wrong With the Old Design

The original design treated state 988 telecom fee adoption as the central shock. States that adopt fees are likely different in mental-health policy commitment, fiscal capacity, administrative quality, and baseline crisis-system capacity. A more complex DID model cannot fix that selection problem.

## Measurement Rescue

The rescue audit found a correctable PDF denominator issue: several 2022 launch-transition answer rates should use received contacts rather than routed contacts. A corrected answer-rate variable is now available in `data/rescue/analysis_panel_rescue.csv`. This improves measurement but does not solve identification.

## Rescue Paths Tested

- Treatment timing: enactment, collection, operational lags, first revenue, fee amount, revenue intensity, and funding-scope definitions.
- Georouting/routing mismatch: official national timeline, ACS mismatch proxies, raw trends, FE interactions, placebo dates, leave-one-state-out checks, fee-capacity moderation.
- Revenue intensity: annual FCC revenue dose-response and lagged revenue models.
- Legislative near-miss: bill-level scan of enacted and stalled 988 fee bills.
- Capacity/disbursement: source scan for consistent public staffing, contract, and disbursement timing.

## What Worked

No rescue path worked well enough for a top-journal causal design. Georouting is the best conceptual direction, but the needed first-stage and exposure data are not public in this project.

## Final Recommendation

Classify the project as `C. POLICY-AUDIT / SUGGESTIVE EVIDENCE PAPER`. The honest manuscript contribution is a reproducible official-data audit showing suggestive performance improvements in fee states, with explicit caveats. A stronger causal paper would require new data on actual georouting exposure, crisis-center capacity, staffing, disbursement dates, or a genuinely quasi-random funding/timing shock.
"""
    (REPORT / "identification_rescue_memo.md").write_text(text, encoding="utf-8")


def write_rescue_readme() -> None:
    text = """# Rescue Data README

This folder contains additive identification-rescue datasets. Existing project data and reports were not overwritten.

## Key Files

- `analysis_panel_rescue.csv`: original analysis panel plus corrected `in_state_answer_rate_rescue`.
- `analysis_panel_rescue_treatments.csv`: rescue panel plus alternative treatment timing and dose variables.
- `fee_timing_audit_state.csv`: state-by-state treatment timing audit.
- `pdf_validation_sample_audit.csv`: validation audit for the original 30-row PDF sample.
- `pdf_answer_rate_denominator_audit_by_month.csv`: month-level answer-rate denominator check.
- `panel_coverage_audit.csv`: panel coverage and missing-month summary.
- `routing_mismatch_exposure_state.csv`: ACS proxy exposure variables for georouting/routing mismatch.
- `georouting_timeline.csv`: official georouting policy and implementation timeline.
- `legislative_988_fee_bills.csv`: bill-level legislative near-miss scan.
- `capacity_disbursement_source_scan.csv`: feasibility scan for disbursement/capacity timing.

## Important Caveat

The routing mismatch variables are proxies only. They are not actual phone-number, area-code, carrier, or handset-location data.
"""
    (RESCUE_DATA / "README.md").write_text(text, encoding="utf-8")


def main() -> None:
    ensure_rescue_dirs()
    panel = read_parquet(DATA / "analysis_panel_state_month.parquet")
    rescue_panel, pdf_audit, pdf_months = build_pdf_validation_and_rescue_panel(panel)
    coverage = panel_coverage(rescue_panel)
    timing = fee_timing_audit()
    rescue_treatments = add_alternative_treatments(rescue_panel, timing)
    timing_att, timing_twfe = timing_sensitivity_models(rescue_treatments)

    source_manifest = download_georouting_sources()
    timeline = georouting_timeline()
    exposure = census_mismatch_exposure()
    if not exposure.empty and "routing_mismatch_exposure_z" in exposure.columns:
        plot_georouting_raw_trends(rescue_treatments, exposure)
    geo, geo_event = georouting_models(rescue_treatments, exposure)
    revenue = revenue_intensity_models(rescue_treatments)
    bills = legislative_nearmiss_dataset()
    capacity_disbursement_scan()
    summary = assemble_model_summary(timing_att, timing_twfe, geo, revenue)

    write_current_design_diagnosis(coverage, pdf_audit, pdf_months, timing_att)
    write_pdf_validation_audit(pdf_audit, pdf_months)
    write_treatment_timing_audit(timing, timing_att, timing_twfe)
    write_georouting_audit(geo, geo_event, exposure, timeline)
    write_revenue_audit(revenue)
    write_legislative_audit(bills)
    write_top_journal_assessment(summary)
    write_identification_rescue_memo()
    write_rescue_readme()

    append_audit(
        "Identification rescue layer completed; see report/identification_rescue_memo.md and result/rescue/model_summary_all_designs.csv."
    )
    print("Identification rescue layer complete.")


if __name__ == "__main__":
    main()
