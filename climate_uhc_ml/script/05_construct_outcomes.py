from __future__ import annotations

import argparse
import math
from pathlib import Path
from typing import Any

import pandas as pd

from common import DATA_DIR, REPORT_DIR, RESULT_DIR, TEMP_DIR, append_log, ensure_dirs, write_csv


INPUT_CANDIDATES = [
    DATA_DIR / "harmonized_household.csv",
    DATA_DIR / "harmonized_household.parquet",
    DATA_DIR / "household_panel.csv",
    DATA_DIR / "household_panel.parquet",
]

OUTCOME_PATH = DATA_DIR / "household_outcomes.csv"
AUDIT_PATH = RESULT_DIR / "outcome_audit.csv"
CONSTRUCTION_AUDIT_PATH = TEMP_DIR / "outcome_construction_audit.csv"

AUDIT_COLUMNS = [
    "country",
    "survey_name",
    "wave",
    "outcome",
    "status",
    "rows",
    "nonmissing",
    "missing_rate",
    "event_rate",
    "weighted_prevalence",
    "low_event_flag",
    "construction_rule",
    "required_columns",
    "missing_columns",
    "notes",
]

CONSTRUCTION_AUDIT_COLUMNS = ["check", "status", "detail", "input_path", "rows_input", "rows_output", "output_path"]

IDENTIFIER_COLUMNS = [
    "country",
    "survey_name",
    "wave",
    "survey_year",
    "survey_month",
    "interview_date",
    "hhid",
    "pid",
    "cluster_id",
    "household_weight",
]

EXPECTED_OUTCOMES = [
    "sdg382_discretionary_40",
    "che10_total_budget",
    "che25_total_budget",
    "capacity_to_pay_40",
    "impoverishing_health_spending",
    "oop_share_total",
    "log_oop_plus_one",
    "forgone_care_conditional_need",
    "forgone_care_cost_barrier",
    "forgone_care_distance_barrier",
    "forgone_care_supply_barrier",
    "delayed_or_unmet_care_outcome",
    "uhc_double_failure",
    "financial_only_failure",
    "access_only_failure",
    "both_financial_and_access_failure",
    "coping_failure",
]

TEMPLATE_COLUMNS = [
    "country",
    "survey_name",
    "wave",
    "survey_year",
    "survey_month",
    "interview_date",
    "hhid",
    "pid",
    "cluster_id",
    "household_weight",
    "total_consumption",
    "total_income",
    "oop_health_expenditure",
    "household_discretionary_budget",
    "capacity_to_pay",
    "poverty_line_total",
    "illness_or_injury_need",
    "care_sought",
    "care_not_sought",
    "reason_not_sought_cost",
    "reason_not_sought_distance",
    "reason_not_sought_supply",
    "delayed_or_unmet_care",
    "coping_borrowed",
    "coping_sold_assets",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Construct UHC financial-protection and access outcomes from harmonized data.")
    parser.add_argument("--input", type=Path, default=None, help="Optional harmonized household/person CSV or Parquet input.")
    return parser.parse_args()


def find_input(explicit: Path | None) -> Path | None:
    if explicit:
        return explicit if explicit.exists() else None
    for path in INPUT_CANDIDATES:
        if path.exists():
            return path
    return None


def read_table(path: Path) -> pd.DataFrame:
    if path.suffix.lower() == ".parquet":
        return pd.read_parquet(path)
    return pd.read_csv(path)


def write_construction_audit(row: dict[str, Any]) -> None:
    write_csv(CONSTRUCTION_AUDIT_PATH, [row], CONSTRUCTION_AUDIT_COLUMNS)


def write_template() -> None:
    template = TEMP_DIR / "harmonized_household_template.csv"
    if not template.exists():
        write_csv(
            template,
            [
                {
                    "country": "Exampleland",
                    "survey_name": "Example household survey",
                    "wave": "2021",
                    "survey_year": "2021",
                    "survey_month": "7",
                    "interview_date": "2021-07-15",
                    "hhid": "HH001",
                    "pid": "",
                    "cluster_id": "C001",
                    "household_weight": "1.0",
                    "total_consumption": "1000",
                    "total_income": "",
                    "oop_health_expenditure": "120",
                    "household_discretionary_budget": "",
                    "capacity_to_pay": "",
                    "poverty_line_total": "",
                    "illness_or_injury_need": "1",
                    "care_sought": "0",
                    "care_not_sought": "1",
                    "reason_not_sought_cost": "1",
                    "reason_not_sought_distance": "0",
                    "reason_not_sought_supply": "0",
                    "delayed_or_unmet_care": "",
                    "coping_borrowed": "0",
                    "coping_sold_assets": "0",
                }
            ],
            TEMPLATE_COLUMNS,
        )


def blocked_no_input_audit() -> list[dict[str, Any]]:
    return [
        {
            "country": "all",
            "survey_name": "all",
            "wave": "all",
            "outcome": outcome,
            "status": "blocked_no_harmonized_input",
            "rows": 0,
            "nonmissing": "",
            "missing_rate": "",
            "event_rate": "",
            "weighted_prevalence": "",
            "low_event_flag": "",
            "construction_rule": "",
            "required_columns": "harmonized household/person dataset",
            "missing_columns": "data/harmonized_household.csv or .parquet",
            "notes": "outcome not attempted because no harmonized analytical input exists",
        }
        for outcome in EXPECTED_OUTCOMES
    ]


def is_limited_harmonized_core(df: pd.DataFrame) -> bool:
    if "data_use_limit" not in df.columns or "outcome_status" not in df.columns:
        return False
    limits = set(df["data_use_limit"].astype(str).str.strip())
    statuses = set(df["outcome_status"].astype(str).str.strip())
    return (
        "harmonized_household_core_only_not_for_final_outcome_or_climate_analysis" in limits
        and "candidate_inputs_not_final_outcomes" in statuses
    )


def blocked_limited_core_audit(input_path: Path, rows_input: int) -> list[dict[str, Any]]:
    return [
        {
            "country": "Albania",
            "survey_name": "Living Standards Measurement Survey 2002",
            "wave": "2002",
            "outcome": outcome,
            "status": "blocked_limited_harmonized_core_not_final_outcome_input",
            "rows": rows_input,
            "nonmissing": "",
            "missing_rate": "",
            "event_rate": "",
            "weighted_prevalence": "",
            "low_event_flag": "",
            "construction_rule": "",
            "required_columns": "final outcome-ready harmonized input",
            "missing_columns": "",
            "notes": f"{input_path.as_posix()} is a limited ALB_2002 harmonized household core with candidate inputs only; outcome construction remains blocked.",
        }
        for outcome in EXPECTED_OUTCOMES
    ]


def numeric(df: pd.DataFrame, column: str) -> pd.Series:
    return pd.to_numeric(df[column], errors="coerce")


def binary(df: pd.DataFrame, column: str) -> pd.Series:
    series = df[column]
    if pd.api.types.is_bool_dtype(series):
        return series.astype("Int64")
    if pd.api.types.is_numeric_dtype(series):
        return (pd.to_numeric(series, errors="coerce") == 1).astype("Int64")
    lowered = series.astype(str).str.strip().str.lower()
    yes = lowered.isin(["1", "true", "yes", "y", "oui", "si"])
    no = lowered.isin(["0", "false", "no", "n", "non"])
    out = pd.Series(pd.NA, index=series.index, dtype="Int64")
    out[yes] = 1
    out[no] = 0
    return out


def first_existing(df: pd.DataFrame, names: list[str]) -> str | None:
    for name in names:
        if name in df.columns:
            return name
    return None


def total_budget_column(df: pd.DataFrame) -> str | None:
    return first_existing(df, ["total_consumption", "total_income", "total_consumption_or_income"])


def add_outcome(
    df: pd.DataFrame,
    outcome_name: str,
    values: pd.Series,
    constructed: dict[str, str],
    rule: str,
) -> None:
    df[outcome_name] = values
    constructed[outcome_name] = rule


def construct_financial(df: pd.DataFrame, constructed: dict[str, str], skipped: list[dict[str, str]]) -> str:
    total_col = total_budget_column(df)
    oop_col = "oop_health_expenditure" if "oop_health_expenditure" in df.columns else None
    financial_reference = ""

    if oop_col and total_col:
        oop = numeric(df, oop_col)
        total = numeric(df, total_col)
        valid = (oop >= 0) & (total > 0)
        share = pd.Series(pd.NA, index=df.index, dtype="Float64")
        share[valid] = oop[valid] / total[valid]
        add_outcome(df, "oop_share_total", share, constructed, f"{oop_col} / {total_col}; valid when OOP >= 0 and total > 0")
        add_outcome(df, "che10_total_budget", (share > 0.10).astype("Int64").where(share.notna()), constructed, "OOP health expenditure > 10% of total consumption/income")
        add_outcome(df, "che25_total_budget", (share > 0.25).astype("Int64").where(share.notna()), constructed, "OOP health expenditure > 25% of total consumption/income")
        log_oop = pd.Series(pd.NA, index=df.index, dtype="Float64")
        log_oop[oop >= 0] = (oop[oop >= 0] + 1).map(math.log)
        add_outcome(df, "log_oop_plus_one", log_oop, constructed, "log(oop_health_expenditure + 1), local-currency units")
        financial_reference = "che10_total_budget"
    else:
        skipped.append(skip_row("che10_total_budget", ["oop_health_expenditure", "total_consumption or total_income"], df.columns))
        skipped.append(skip_row("che25_total_budget", ["oop_health_expenditure", "total_consumption or total_income"], df.columns))
        skipped.append(skip_row("oop_share_total", ["oop_health_expenditure", "total_consumption or total_income"], df.columns))

    discretionary_col = first_existing(df, ["household_discretionary_budget", "discretionary_budget"])
    if oop_col and discretionary_col:
        oop = numeric(df, oop_col)
        discretionary = numeric(df, discretionary_col)
        valid = (oop > 0) & (discretionary > 0)
        out = pd.Series(pd.NA, index=df.index, dtype="Int64")
        out[valid] = (oop[valid] > 0.40 * discretionary[valid]).astype("int64")
        add_outcome(df, "sdg382_discretionary_40", out, constructed, f"positive {oop_col} > 40% of {discretionary_col}")
        financial_reference = "sdg382_discretionary_40"
    else:
        skipped.append(skip_row("sdg382_discretionary_40", ["oop_health_expenditure", "household_discretionary_budget or discretionary_budget"], df.columns))

    capacity_col = first_existing(df, ["capacity_to_pay", "household_capacity_to_pay"])
    if oop_col and capacity_col:
        oop = numeric(df, oop_col)
        capacity = numeric(df, capacity_col)
        valid = (oop > 0) & (capacity > 0)
        out = pd.Series(pd.NA, index=df.index, dtype="Int64")
        out[valid] = (oop[valid] > 0.40 * capacity[valid]).astype("int64")
        add_outcome(df, "capacity_to_pay_40", out, constructed, f"positive {oop_col} > 40% of {capacity_col}")
    else:
        skipped.append(skip_row("capacity_to_pay_40", ["oop_health_expenditure", "capacity_to_pay"], df.columns))

    poverty_col = first_existing(df, ["poverty_line_total", "societal_poverty_line_household"])
    if oop_col and total_col and poverty_col:
        oop = numeric(df, oop_col)
        total = numeric(df, total_col)
        poverty = numeric(df, poverty_col)
        valid = (oop >= 0) & total.notna() & poverty.notna()
        out = pd.Series(pd.NA, index=df.index, dtype="Int64")
        out[valid] = ((total[valid] >= poverty[valid]) & ((total[valid] - oop[valid]) < poverty[valid])).astype("int64")
        add_outcome(df, "impoverishing_health_spending", out, constructed, f"{total_col} >= {poverty_col} and {total_col} - {oop_col} < {poverty_col}")
    else:
        skipped.append(skip_row("impoverishing_health_spending", ["oop_health_expenditure", "total_consumption or total_income", "poverty_line_total or societal_poverty_line_household"], df.columns))

    return financial_reference


def construct_access(df: pd.DataFrame, constructed: dict[str, str], skipped: list[dict[str, str]]) -> None:
    need_col = "illness_or_injury_need" if "illness_or_injury_need" in df.columns else None
    care_sought_col = "care_sought" if "care_sought" in df.columns else None
    care_not_sought_col = "care_not_sought" if "care_not_sought" in df.columns else None

    if need_col and (care_sought_col or care_not_sought_col):
        need = binary(df, need_col)
        if care_not_sought_col:
            not_sought = binary(df, care_not_sought_col)
        else:
            sought = binary(df, care_sought_col)  # type: ignore[arg-type]
            not_sought = (sought == 0).astype("Int64").where(sought.notna())
        out = pd.Series(pd.NA, index=df.index, dtype="Int64")
        valid = need.notna() & not_sought.notna()
        out[valid] = ((need[valid] == 1) & (not_sought[valid] == 1)).astype("int64")
        add_outcome(df, "forgone_care_conditional_need", out, constructed, "illness_or_injury_need == 1 and care was not sought")
    else:
        skipped.append(skip_row("forgone_care_conditional_need", ["illness_or_injury_need", "care_sought or care_not_sought"], df.columns))

    for source, outname in [
        ("reason_not_sought_cost", "forgone_care_cost_barrier"),
        ("reason_not_sought_distance", "forgone_care_distance_barrier"),
        ("reason_not_sought_supply", "forgone_care_supply_barrier"),
    ]:
        if source in df.columns:
            barrier = binary(df, source)
            out = pd.Series(pd.NA, index=df.index, dtype="Int64")
            out[barrier.notna()] = (barrier[barrier.notna()] == 1).astype("int64")
            add_outcome(df, outname, out, constructed, f"{source} == 1")
        else:
            skipped.append(skip_row(outname, [source], df.columns))

    if "delayed_or_unmet_care" in df.columns:
        out = binary(df, "delayed_or_unmet_care")
        add_outcome(df, "delayed_or_unmet_care_outcome", out, constructed, "survey-specific delayed_or_unmet_care == 1")


def construct_composites(df: pd.DataFrame, constructed: dict[str, str], skipped: list[dict[str, str]], financial_reference: str) -> None:
    access = "forgone_care_conditional_need" if "forgone_care_conditional_need" in df.columns else ""
    if financial_reference and access:
        fin = binary(df, financial_reference)
        acc = binary(df, access)
        valid = fin.notna() | acc.notna()
        double = pd.Series(pd.NA, index=df.index, dtype="Int64")
        double[valid] = ((fin.fillna(0) == 1) | (acc.fillna(0) == 1))[valid].astype("int64")
        add_outcome(df, "uhc_double_failure", double, constructed, f"{financial_reference} OR {access}")

        financial_only = pd.Series(pd.NA, index=df.index, dtype="Int64")
        access_only = pd.Series(pd.NA, index=df.index, dtype="Int64")
        both = pd.Series(pd.NA, index=df.index, dtype="Int64")
        both_valid = fin.notna() & acc.notna()
        financial_only[both_valid] = ((fin[both_valid] == 1) & (acc[both_valid] == 0)).astype("int64")
        access_only[both_valid] = ((fin[both_valid] == 0) & (acc[both_valid] == 1)).astype("int64")
        both[both_valid] = ((fin[both_valid] == 1) & (acc[both_valid] == 1)).astype("int64")
        add_outcome(df, "financial_only_failure", financial_only, constructed, f"{financial_reference} == 1 and {access} == 0")
        add_outcome(df, "access_only_failure", access_only, constructed, f"{financial_reference} == 0 and {access} == 1")
        add_outcome(df, "both_financial_and_access_failure", both, constructed, f"{financial_reference} == 1 and {access} == 1")
    else:
        skipped.append(skip_row("uhc_double_failure", ["financial hardship outcome", "forgone_care_conditional_need"], df.columns))

    coping_sources = [c for c in ["coping_borrowed", "coping_sold_assets"] if c in df.columns]
    if coping_sources:
        vals = [binary(df, c) for c in coping_sources]
        any_coping = pd.concat(vals, axis=1)
        out = pd.Series(pd.NA, index=df.index, dtype="Int64")
        valid = any_coping.notna().any(axis=1)
        out[valid] = (any_coping.fillna(0).max(axis=1)[valid] == 1).astype("int64")
        add_outcome(df, "coping_failure", out, constructed, "any available coping_borrowed/coping_sold_assets == 1")
    else:
        skipped.append(skip_row("coping_failure", ["coping_borrowed or coping_sold_assets"], df.columns))


def skip_row(outcome: str, required: list[str], columns: pd.Index) -> dict[str, str]:
    missing = [col for col in required if " or " not in col and col not in columns]
    if any(" or " in col for col in required):
        missing = required
    return {
        "outcome": outcome,
        "required_columns": ";".join(required),
        "missing_columns": ";".join(missing),
    }


def weighted_prevalence(series: pd.Series, weights: pd.Series | None) -> float | str:
    if weights is None:
        return ""
    valid = series.notna() & weights.notna() & (weights > 0)
    if not valid.any():
        return ""
    return float((series[valid].astype(float) * weights[valid]).sum() / weights[valid].sum())


def audit_outcomes(df: pd.DataFrame, constructed: dict[str, str], skipped: list[dict[str, str]]) -> list[dict[str, Any]]:
    rows = []
    group_cols = [c for c in ["country", "survey_name", "wave"] if c in df.columns]
    weight = numeric(df, "household_weight") if "household_weight" in df.columns else None
    if group_cols:
        grouped = list(df.groupby(group_cols, dropna=False))
    else:
        grouped = [(("all",), df)]

    for outcome, rule in constructed.items():
        for key, sub in grouped:
            if not isinstance(key, tuple):
                key = (key,)
            key_map = dict(zip(group_cols, key))
            series = sub[outcome]
            nonmissing = int(series.notna().sum())
            event_rate: float | str = ""
            low_event = ""
            if nonmissing:
                event_rate = float(pd.to_numeric(series, errors="coerce").mean())
                if outcome not in {"oop_share_total", "log_oop_plus_one"} and event_rate < 0.03:
                    low_event = "event_rate_below_3_percent"
            wprev = weighted_prevalence(series, weight.loc[sub.index] if weight is not None else None)
            rows.append(
                {
                    "country": key_map.get("country", "all"),
                    "survey_name": key_map.get("survey_name", "all"),
                    "wave": key_map.get("wave", "all"),
                    "outcome": outcome,
                    "status": "constructed",
                    "rows": len(sub),
                    "nonmissing": nonmissing,
                    "missing_rate": float(1 - nonmissing / len(sub)) if len(sub) else "",
                    "event_rate": event_rate,
                    "weighted_prevalence": wprev,
                    "low_event_flag": low_event,
                    "construction_rule": rule,
                    "required_columns": "",
                    "missing_columns": "",
                    "notes": "audit from harmonized analytical input",
                }
            )

    for item in skipped:
        rows.append(
            {
                "country": "all",
                "survey_name": "all",
                "wave": "all",
                "outcome": item["outcome"],
                "status": "skipped_missing_columns",
                "rows": len(df),
                "nonmissing": "",
                "missing_rate": "",
                "event_rate": "",
                "weighted_prevalence": "",
                "low_event_flag": "",
                "construction_rule": "",
                "required_columns": item["required_columns"],
                "missing_columns": item["missing_columns"],
                "notes": "not constructed because required harmonized columns are absent",
            }
        )
    return rows


def write_report(audit_rows: list[dict[str, Any]], constructed: dict[str, str], input_path: Path | None, output_rows: int) -> None:
    constructed_rows = [r for r in audit_rows if r["status"] == "constructed"]
    skipped_rows = [r for r in audit_rows if r["status"] != "constructed"]
    constructed_names = sorted(constructed)
    skipped_names = sorted({r["outcome"] for r in skipped_rows})
    constructed_table = "\n".join(f"| `{name}` | {constructed[name]} |" for name in constructed_names) or "| none | none |"
    skipped_table = "\n".join(f"| `{name}` | skipped/missing inputs |" for name in skipped_names) or "| none | none |"
    status = "constructed outcomes from harmonized input" if constructed_rows else "no outcomes constructed; harmonized input missing or insufficient"
    report = f"""# Outcome Construction

Status: {status}.

Input: `{str(input_path.relative_to(TEMP_DIR.parent)) if input_path else 'none'}`

Output rows: {output_rows}

## Official Financial-Protection Definitions

| Outcome | Formula | Current status |
|---|---|---|
| `sdg382_discretionary_40` | positive OOP health expenditure > 40% of household discretionary budget | constructed only if OOP and an already harmonized discretionary-budget column exist |
| `che10_total_budget` | OOP health expenditure > 10% of total consumption/income | constructed when OOP plus total consumption/income exist |
| `che25_total_budget` | OOP health expenditure > 25% of total consumption/income | constructed when OOP plus total consumption/income exist |
| `capacity_to_pay_40` | OOP health expenditure > 40% of capacity to pay | constructed when OOP plus capacity-to-pay exist |
| `impoverishing_health_spending` | above poverty line before OOP and below after OOP | constructed when OOP, total budget, and household poverty line exist |

## Constructed Outcomes

| Outcome | Construction rule |
|---|---|
{constructed_table}

## Skipped Outcomes

| Outcome | Reason |
|---|---|
{skipped_table}

## Audit Files

- `result/outcome_audit.csv`
- `temp/outcome_construction_audit.csv`

## Caveats

- SDG 3.8.2 is not inferred from poverty-line fragments. It requires a harmonized discretionary-budget denominator.
- Recall periods and local-currency units must be audited before cross-country pooling.
- Event rates below 3% are flagged in `result/outcome_audit.csv`.
"""
    (REPORT_DIR / "outcome_construction.md").write_text(report, encoding="utf-8")


def main() -> None:
    ensure_dirs()
    write_template()
    args = parse_args()
    input_path = find_input(args.input)
    if input_path is None:
        audit_rows = blocked_no_input_audit()
        write_csv(AUDIT_PATH, audit_rows, AUDIT_COLUMNS)
        row = {
            "check": "outcome_input",
            "status": "blocked_no_harmonized_household_input",
            "detail": "No harmonized household/person dataset exists in data/.",
            "input_path": "",
            "rows_input": 0,
            "rows_output": 0,
            "output_path": "",
        }
        write_construction_audit(row)
        write_report(audit_rows, {}, None, 0)
        append_log(TEMP_DIR / "audit_log.md", "Outcome construction blocked: no harmonized household input.")
        print("Outcome construction blocked: no harmonized household input.")
        return

    df = read_table(input_path)
    original_rows = len(df)
    if is_limited_harmonized_core(df):
        if OUTCOME_PATH.exists():
            OUTCOME_PATH.unlink()
        audit_rows = blocked_limited_core_audit(input_path, original_rows)
        write_csv(AUDIT_PATH, audit_rows, AUDIT_COLUMNS)
        row = {
            "check": "outcome_construction",
            "status": "blocked_limited_harmonized_core_not_final_outcome_input",
            "detail": "limited harmonized core carries candidate inputs only; no final outcomes constructed",
            "input_path": str(input_path.relative_to(TEMP_DIR.parent)),
            "rows_input": original_rows,
            "rows_output": 0,
            "output_path": "",
        }
        write_construction_audit(row)
        write_report(audit_rows, {}, input_path, 0)
        append_log(TEMP_DIR / "audit_log.md", "Outcome construction blocked: limited harmonized core is not final outcome input.")
        print("Outcome construction blocked: limited harmonized core is not final outcome input.")
        return

    constructed: dict[str, str] = {}
    skipped: list[dict[str, str]] = []
    financial_reference = construct_financial(df, constructed, skipped)
    construct_access(df, constructed, skipped)
    construct_composites(df, constructed, skipped, financial_reference)

    if constructed:
        keep_cols = [c for c in IDENTIFIER_COLUMNS if c in df.columns] + list(constructed)
        if not keep_cols:
            keep_cols = list(constructed)
        OUTCOME_PATH.parent.mkdir(parents=True, exist_ok=True)
        df[keep_cols].to_csv(OUTCOME_PATH, index=False, encoding="utf-8-sig")
        output_rows = len(df)
        output_path = str(OUTCOME_PATH.relative_to(TEMP_DIR.parent))
    else:
        output_rows = 0
        output_path = ""

    audit_rows = audit_outcomes(df, constructed, skipped)
    write_csv(AUDIT_PATH, audit_rows, AUDIT_COLUMNS)
    row = {
        "check": "outcome_construction",
        "status": "complete" if constructed else "blocked_missing_required_columns",
        "detail": f"constructed={len(constructed)}; skipped={len(skipped)}",
        "input_path": str(input_path.relative_to(TEMP_DIR.parent)),
        "rows_input": original_rows,
        "rows_output": output_rows,
        "output_path": output_path,
    }
    write_construction_audit(row)
    write_report(audit_rows, constructed, input_path, output_rows)
    append_log(TEMP_DIR / "audit_log.md", f"Outcome construction status={row['status']}; constructed={len(constructed)}; skipped={len(skipped)}.")
    print(f"Outcome construction status={row['status']}; constructed={len(constructed)}; skipped={len(skipped)}.")


if __name__ == "__main__":
    main()
