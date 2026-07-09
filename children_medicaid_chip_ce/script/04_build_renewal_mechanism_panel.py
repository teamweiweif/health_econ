from __future__ import annotations

import pandas as pd

from project_utils import DATA, RAW, STATE_ABBR_TO_FIPS, add_or_update_inventory, append_audit, clean_col, month_from_reporting_period, safe_div, save_parquet, sha256_file, source_row


RENAME = {
    "beneficiaries_with_a_renewal_initiated": "renewals_initiated",
    "beneficiaries_with_a_renewal_due": "renewals_due",
    "beneficiaries_whose_coverage_was_renewed_total": "renewed_total",
    "beneficiaries_whose_coverage_was_renewed_on_an_ex_parte_basis": "ex_parte_renewed",
    "beneficiaries_whose_coverage_was_renewed_based_on_a_renewal_form": "form_renewed",
    "beneficiaries_disenrolled_at_renewal_total": "disenrolled_total",
    "beneficiaries_determined_ineligible_at_renewal": "ineligible_terminations",
    "beneficiaries_disenrolled_for_procedural_reasons_at_renewal": "procedural_terminations",
    "beneficiaries_with_a_pending_renewal": "pending_renewals",
}


def choose_best(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["version_rank"] = df["original_or_updated"].map({"U": 2, "O": 1}).fillna(0)
    df = df.sort_values(["state_abbreviation", "reporting_period", "version_rank"])
    return df.groupby(["state_abbreviation", "reporting_period"], as_index=False).tail(1)


def main() -> None:
    files = sorted(RAW.glob("renewal-dataset-*-release.csv"))
    if not files:
        raise FileNotFoundError("CMS renewal CSV not found. Run script/01_acquire_sources.py first.")
    raw_path = files[0]
    df = pd.read_csv(raw_path)
    df.columns = [clean_col(c) for c in df.columns]
    df = choose_best(df)
    df["state_abbr"] = df["state_abbreviation"]
    df["state_fips"] = df["state_abbr"].map(STATE_ABBR_TO_FIPS)
    df["month"] = df["reporting_period"].map(month_from_reporting_period)
    df = df.rename(columns=RENAME)
    keep = ["state_name", "state_abbr", "state_fips", "month", "reporting_period", "original_or_updated"] + list(RENAME.values())
    out = df[keep].copy()
    for col in RENAME.values():
        out[col] = pd.to_numeric(out[col], errors="coerce")
    out["renewal_completion_rate"] = safe_div(out["renewed_total"] + out["disenrolled_total"], out["renewals_due"])
    out["ex_parte_renewal_rate_due"] = safe_div(out["ex_parte_renewed"], out["renewals_due"])
    out["ex_parte_renewal_rate_renewed"] = safe_div(out["ex_parte_renewed"], out["renewed_total"])
    out["form_renewal_rate_due"] = safe_div(out["form_renewed"], out["renewals_due"])
    out["termination_rate_due"] = safe_div(out["disenrolled_total"], out["renewals_due"])
    out["procedural_termination_rate_due"] = safe_div(out["procedural_terminations"], out["renewals_due"])
    out["procedural_termination_share"] = safe_div(out["procedural_terminations"], out["disenrolled_total"])
    out["ineligibility_termination_share"] = safe_div(out["ineligible_terminations"], out["disenrolled_total"])
    out["pending_renewal_share"] = safe_div(out["pending_renewals"], out["renewals_due"])
    out["month"] = out["month"].dt.strftime("%Y-%m-%d")
    save_parquet(out, DATA / "renewal_state_month.parquet")
    add_or_update_inventory(
        [
            source_row(
                "constructed_renewal_state_month",
                "CMS State Medicaid and CHIP Eligibility Processing Data",
                DATA / "renewal_state_month.parquet",
                period_covered=f"{out['month'].min()} to {out['month'].max()}",
                unit="state-month",
                row_count=len(out),
                column_count=len(out.columns),
                checksum=sha256_file(DATA / "renewal_state_month.parquet"),
                notes="Not child-specific; used as state-level mechanism and moderator.",
            )
        ]
    )
    append_audit("renewal mechanism panel built; outcomes are not child-specific")
    print(f"renewal panel rows={len(out)} months={out['month'].min()}..{out['month'].max()}")


if __name__ == "__main__":
    main()
