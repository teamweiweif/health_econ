from __future__ import annotations

import re

import pandas as pd
from pypdf import PdfReader

from project_utils import (
    DATA,
    RAW,
    REPORT,
    RESULT,
    STATE_ABBR_TO_FIPS,
    STATE_NAME_TO_ABBR,
    TEMP,
    add_or_update_inventory,
    append_audit,
    save_parquet,
    sha256_file,
    source_row,
)


KFF_POLICY_ROWS = [
    ("Alabama", "Y", "Y", ""),
    ("Alaska", "Y", "N/A (M-CHIP)", ""),
    ("Arizona", "", "", ""),
    ("Arkansas", "", "Y", ""),
    ("California", "Y", "N/A (M-CHIP)", ""),
    ("Colorado", "Y", "Y", ""),
    ("Connecticut", "", "", ""),
    ("Delaware", "", "Y", ""),
    ("District of Columbia", "", "N/A (M-CHIP)", ""),
    ("Florida", "Under Age 5", "Y", "Medicaid CE only under age 5; ages 5+ had six months CE."),
    ("Georgia", "", "", ""),
    ("Hawaii", "", "N/A (M-CHIP)", ""),
    ("Idaho", "Y", "Y", ""),
    ("Illinois", "Y", "N/A (M-CHIP)", ""),
    ("Indiana", "Under Age 3", "Under Age 3", "CE only under age 3."),
    ("Iowa", "Y", "Y", ""),
    ("Kansas", "Y", "Y", ""),
    ("Kentucky", "", "", ""),
    ("Louisiana", "Y", "Y", ""),
    ("Maine", "Y", "Y", ""),
    ("Maryland", "", "N/A (M-CHIP)", ""),
    ("Massachusetts", "", "", ""),
    ("Michigan", "Y", "N/A (M-CHIP)", ""),
    ("Minnesota", "", "N/A (M-CHIP)", ""),
    ("Mississippi", "Y", "Y", ""),
    ("Missouri", "", "", ""),
    ("Montana", "Y", "Y", ""),
    ("Nebraska", "", "N/A (M-CHIP)", ""),
    ("Nevada", "", "Y", ""),
    ("New Hampshire", "", "N/A (M-CHIP)", ""),
    ("New Jersey", "", "Y", ""),
    ("New Mexico", "Y", "N/A (M-CHIP)", ""),
    ("New York", "Y", "Y", ""),
    ("North Carolina", "Y", "Y", ""),
    ("North Dakota", "Y", "N/A (M-CHIP)", ""),
    ("Ohio", "Y", "N/A (M-CHIP)", ""),
    ("Oklahoma", "", "N/A (M-CHIP)", ""),
    ("Oregon", "Y", "Y", "Oregon also had multi-year CE authority for young children."),
    ("Pennsylvania", "Under Age 4", "Y", "Medicaid CE only under age 4."),
    ("Rhode Island", "", "N/A (M-CHIP)", ""),
    ("South Carolina", "Y", "N/A (M-CHIP)", ""),
    ("South Dakota", "", "", ""),
    ("Tennessee", "", "Y", ""),
    ("Texas", "", "Y", "CHIP CE was limited to income up to 185 percent FPL per KFF footnote."),
    ("Utah", "", "Y", ""),
    ("Vermont", "", "N/A (M-CHIP)", ""),
    ("Virginia", "", "", ""),
    ("Washington", "Y", "Y", ""),
    ("West Virginia", "Y", "Y", ""),
    ("Wisconsin", "", "", ""),
    ("Wyoming", "Y", "N/A (M-CHIP)", ""),
]


def extracted_kff_text() -> str:
    path = RAW / "kff_table5_child_ce_jan2023.pdf"
    if not path.exists():
        path = RAW / "kff_table5_continuous_eligibility_jan2023.pdf"
    if not path.exists():
        return "KFF Table 5 PDF was not found in temp/raw_downloads."
    page = PdfReader(path).pages[0]
    try:
        return page.extract_text(extraction_mode="layout")
    except TypeError:
        return page.extract_text() or ""


def status_any(status: str) -> int:
    return int(bool(status and status != "N/A (M-CHIP)"))


def status_full(status: str) -> int:
    return int(status == "Y")


def status_partial(status: str) -> int:
    return int(status.startswith("Under Age"))


def build_policy_seed() -> pd.DataFrame:
    rows = []
    for state, medicaid_status, chip_status, notes in KFF_POLICY_ROWS:
        abbr = STATE_NAME_TO_ABBR[state]
        separate_chip = chip_status != "N/A (M-CHIP)"
        medicaid_any = status_any(medicaid_status)
        chip_any = status_any(chip_status)
        medicaid_full = status_full(medicaid_status)
        chip_full = status_full(chip_status)
        medicaid_partial = status_partial(medicaid_status)
        chip_partial = status_partial(chip_status)
        partial = int(
            medicaid_partial
            or chip_partial
            or (medicaid_any != chip_any and separate_chip)
            or state == "Texas"
        )
        rows.append(
            {
                "state": state,
                "state_abbr": abbr,
                "state_fips": STATE_ABBR_TO_FIPS[abbr],
                "pre2024_medicaid_child_12mo_ce": medicaid_full,
                "pre2024_chip_child_12mo_ce": chip_full if separate_chip else pd.NA,
                "pre2024_any_child_12mo_ce": int(medicaid_any or chip_any),
                "newly_treated_medicaid_child_ce": int(not medicaid_full),
                "newly_treated_chip_child_ce": int(separate_chip and not chip_full),
                "newly_treated_any_child_ce": int(not (medicaid_any or chip_any)),
                "partial_pre2024_ce": partial,
                "separate_chip_program": int(separate_chip),
                "medicaid_expansion_chip": pd.NA,
                "chip_premium_policy_pre2024": "",
                "premium_nonpayment_discontinuation_exposure": pd.NA,
                "chip_waiting_period_pre2024": "",
                "chip_lockout_pre2024": "",
                "medicaid_expansion_status": "",
                "unwinding_start_month": "2023-04",
                "unwinding_completion_month": "2023-12",
                "ex_parte_rate_baseline_if_available": pd.NA,
                "baseline_procedural_disenrollment_rate_if_available": pd.NA,
                "state_policy_notes": notes,
                "source_url_or_source_name": "KFF/Georgetown Table 5, January 2023; CMS SHO 23-004; CMS FAQ 10/27/2023",
                "confidence_level": "high_for_CE_table; low_for_unextracted_premium_lockout_fields",
                "kff_medicaid_child_ce_status": medicaid_status,
                "kff_chip_child_ce_status": chip_status,
            }
        )
    return pd.DataFrame(rows)


def month_range() -> pd.DatetimeIndex:
    pi_files = list(RAW.glob("pi-dataset-*-release.csv"))
    if pi_files:
        df = pd.read_csv(pi_files[0], usecols=["Reporting Period"])
        start = max(pd.Timestamp("2018-01-01"), pd.to_datetime(df["Reporting Period"].min(), format="%Y%m"))
        end = pd.to_datetime(df["Reporting Period"].max(), format="%Y%m")
        return pd.date_range(start=start, end=end, freq="MS")
    return pd.date_range("2018-01-01", "2026-03-01", freq="MS")


def write_reports(seed: pd.DataFrame, panel: pd.DataFrame, kff_text: str) -> None:
    REPORT.mkdir(exist_ok=True)
    (TEMP / "kff_table5_extracted_text.txt").write_text(kff_text, encoding="utf-8")
    timeline = """# Policy Timeline

## Verified Timeline

- 2022-12-29: The Consolidated Appropriations Act, 2023 was enacted. Section 5112 amended Medicaid and CHIP law to require 12 months of continuous eligibility for children under age 19.
- 2023-09-29: CMS issued SHO 23-004, explaining implementation of the mandatory 12-month CE requirement.
- 2023-10-27: CMS issued FAQs clarifying that, on or after 2024-01-01, CHIP coverage may not be terminated during a CE period for non-payment of premiums except under specified statutory exceptions.
- 2024-01-01: All states were required to provide 12 months of CE for children under age 19 in Medicaid and CHIP.
- 2024-11: CMS finalized regulatory codification of the children CE requirement in the OPPS/ASC final rule, according to the CMS continuous eligibility page.

## Source Files

- `temp/raw_downloads/cms_sho_23_004.pdf`
- `temp/raw_downloads/cms_faq_102723_child_ce_premium_nonpayment.pdf`
- `temp/source_snapshots/cms_continuous_eligibility_page.html`
- `temp/raw_downloads/kff_table5_child_ce_jan2023.pdf`
"""
    (REPORT / "policy_timeline.md").write_text(timeline, encoding="utf-8")
    policy_table = seed[
        [
            "state",
            "state_abbr",
            "kff_medicaid_child_ce_status",
            "kff_chip_child_ce_status",
            "pre2024_any_child_12mo_ce",
            "newly_treated_any_child_ce",
            "partial_pre2024_ce",
            "separate_chip_program",
            "state_policy_notes",
        ]
    ]
    policy_table.to_csv(RESULT / "policy_timing_table.csv", index=False)


def main() -> None:
    seed = build_policy_seed()
    DATA.mkdir(exist_ok=True)
    seed_path = TEMP / "policy_seed_child_ce_jan2023.csv"
    seed.to_csv(seed_path, index=False)

    months = pd.DataFrame({"month": month_range()})
    panel = seed.merge(months, how="cross")
    panel["child_ce_mandate_post_2024"] = (panel["month"] >= pd.Timestamp("2024-01-01")).astype(int)
    panel["month"] = panel["month"].dt.strftime("%Y-%m-%d")
    save_parquet(panel, DATA / "state_policy_month.parquet")
    kff_text = extracted_kff_text()
    write_reports(seed, panel, kff_text)
    add_or_update_inventory(
        [
            source_row(
                "constructed_policy_seed_child_ce_jan2023",
                "KFF/Georgetown Table 5 extracted from PDF",
                seed_path,
                period_covered="January 2023",
                unit="state",
                row_count=len(seed),
                column_count=len(seed.columns),
                checksum=sha256_file(seed_path),
                notes="Manual transcription from extracted PDF layout; extraction text preserved in temp.",
            )
        ]
    )
    append_audit("policy panel built from KFF Table 5 and CMS federal timeline")
    print(f"policy seed states={len(seed)} panel rows={len(panel)}")


if __name__ == "__main__":
    main()
