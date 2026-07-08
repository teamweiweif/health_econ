from __future__ import annotations

import pandas as pd

from project_utils import DATA, RAW, STATE_ABBR_TO_FIPS, STATE_NAME_TO_ABBR, add_or_update_inventory, append_audit, parse_xlsx_first_sheet, save_parquet, sha256_file, source_row, to_number


AGE_MAP = {
    ".Under 19 years": "child_under19",
    ".19 - 64 years": "adult_19_64",
    "Under 19 years": "child_under19",
    "19 - 64 years": "adult_19_64",
}


def parse_hi05(path, year: int) -> pd.DataFrame:
    rows = parse_xlsx_first_sheet(path)
    out = []
    for row in rows:
        state = row.get("A", "")
        age = row.get("B", "")
        if state not in STATE_NAME_TO_ABBR or age not in AGE_MAP:
            continue
        abbr = STATE_NAME_TO_ABBR[state]
        out.append(
            {
                "year": year,
                "state": state,
                "state_abbr": abbr,
                "state_fips": STATE_ABBR_TO_FIPS[abbr],
                "age_group": AGE_MAP[age],
                "child_group": int(AGE_MAP[age] == "child_under19"),
                "population_thousands": to_number(row.get("C")),
                "any_insurance_thousands": to_number(row.get("E")),
                "any_insurance_percent": to_number(row.get("G")),
                "private_insurance_thousands": to_number(row.get("I")),
                "private_insurance_percent": to_number(row.get("K")),
                "public_insurance_thousands": to_number(row.get("Y")),
                "public_insurance_percent": to_number(row.get("AA")),
                "medicaid_thousands": to_number(row.get("AC")),
                "medicaid_percent": to_number(row.get("AE")),
                "uninsured_thousands": to_number(row.get("BA")),
                "uninsured_percent": to_number(row.get("BC")),
                "source_file": str(path.name),
            }
        )
    return pd.DataFrame(out)


def main() -> None:
    frames = []
    attempted = []
    for year in [2018, 2019, 2021, 2022, 2023, 2024]:
        path = RAW / f"census_hi05_acs_{year}.xlsx"
        attempted.append(str(path))
        if path.exists():
            frames.append(parse_hi05(path, year))
        elif (RAW / f"census_hi05_acs_{year}.xls").exists():
            append_audit(f"ACS HI05 {year} legacy XLS source found but not parsed by current XLSX parser")
    if not frames:
        raise FileNotFoundError("No Census HI05 ACS XLSX files found. Run script/01_acquire_sources.py first.")
    out = pd.concat(frames, ignore_index=True)
    out["post2024"] = (out["year"] >= 2024).astype(int)
    save_parquet(out, DATA / "acs_state_age_year.parquet")
    save_parquet(out, DATA / "validation_panel.parquet")
    add_or_update_inventory(
        [
            source_row(
                "constructed_acs_state_age_year",
                "Census ACS HI-05 public XLSX tables",
                DATA / "acs_state_age_year.parquet",
                period_covered=f"{out['year'].min()} to {out['year'].max()}, ACS 2020 omitted by Census 1-year release limitations",
                unit="state-age-year",
                row_count=len(out),
                column_count=len(out.columns),
                checksum=sha256_file(DATA / "acs_state_age_year.parquet"),
                notes="Validation panel from ACS published health insurance XLSX tables, not person-level PUMS. Legacy 2018 XLS is recorded but not parsed without an XLS reader.",
            )
        ]
    )
    append_audit("ACS validation panel built from Census HI-05 XLSX tables; Census API probe required key")
    print(f"ACS validation rows={len(out)} years={sorted(out['year'].unique())}")


if __name__ == "__main__":
    main()
