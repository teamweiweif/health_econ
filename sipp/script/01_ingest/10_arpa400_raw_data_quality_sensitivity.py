from __future__ import annotations

import importlib.util
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
BASE_SCRIPT = ROOT / "script" / "11_idea_scan" / "24_arpa_400fpl_cliff_diffdisc_test.py"
PATCH = (
    ROOT
    / "data"
    / "analysis_ready"
    / "sipp_2018_2023_health_insurance_official_usernote_correction_patch.parquet"
)
RESULT_ROOT = ROOT / "result" / "data_audit"
ESTIMATES = RESULT_ROOT / "arpa400_health_weight_data_quality_sensitivity.csv"
PATCH_SUPPORT = RESULT_ROOT / "arpa400_health_correction_patch_support.csv"
REPORT = ROOT / "report" / "107_arpa400_raw_data_quality_sensitivity.md"

CORRECTED_VARS = [
    "ECRMTH",
    "EMDMTH",
    "RPUBTYPE1",
    "RPUBTYPE2",
    "RPRIMTH",
    "RPUBMTH",
    "RHLTHMTH",
]
OUTCOMES = ["uninsured", "any_coverage", "private", "public", "medicaid"]


def load_base_module():
    spec = importlib.util.spec_from_file_location("arpa400_base_screen", BASE_SCRIPT)
    if spec is None or spec.loader is None:
        raise ImportError(BASE_SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def apply_valid_official_weight(frame: pd.DataFrame) -> pd.DataFrame:
    output = frame.copy()
    weight = pd.to_numeric(output["WPFINWGT"], errors="coerce")
    output["weight"] = weight.where(weight.gt(0))
    return output


def apply_health_patch(frame: pd.DataFrame, module) -> pd.DataFrame:
    patch_columns = ["person_month_key"] + [
        f"{variable}_CENSUS_NOTE_CORRECTED" for variable in CORRECTED_VARS
    ]
    patch = pd.read_parquet(PATCH, columns=patch_columns)
    if patch["person_month_key"].duplicated().any():
        raise ValueError("Health correction patch has duplicate person-month keys")
    output = frame.merge(patch, on="person_month_key", how="left", validate="many_to_one")
    corrected_columns = [f"{variable}_CENSUS_NOTE_CORRECTED" for variable in CORRECTED_VARS]
    output["health_note_patch_applied"] = output[corrected_columns].notna().any(axis=1)
    for variable in CORRECTED_VARS:
        corrected = f"{variable}_CENSUS_NOTE_CORRECTED"
        if variable in output:
            output[variable] = output[corrected].where(
                output[corrected].notna(), output[variable]
            )

    output["medicare"] = module.yes(output["RPUBTYPE1"]).astype(float)
    output["any_coverage"] = module.yes(output["RHLTHMTH"]).astype(float)
    output["uninsured"] = output["RHLTHMTH"].eq(2).astype(float)
    output["private"] = module.yes(output["RPRIMTH"]).astype(float)
    output["public"] = module.yes(output["RPUBMTH"]).astype(float)
    output["medicaid"] = module.yes(output["EMDMTH"]).astype(float)
    return output.drop(columns=corrected_columns)


def run_estimates(module, frame: pd.DataFrame, scenario: str) -> pd.DataFrame:
    rows = module.estimate_model(
        frame,
        OUTCOMES,
        scenario,
        "monthly_fpl",
        "post_year2021",
        26,
        4.0,
        0.5,
    )
    output = pd.DataFrame(rows)
    output.insert(0, "data_quality_scenario", scenario)
    return output


def build_patch_support(original: pd.DataFrame, corrected: pd.DataFrame) -> pd.DataFrame:
    sample = corrected[
        corrected["age"].between(26, 64, inclusive="both")
        & corrected["medicare"].ne(1)
        & corrected["monthly_fpl"].between(3.5, 4.5, inclusive="both")
        & corrected["weight"].gt(0)
    ].copy()
    original_outcomes = original.set_index("person_month_key")[OUTCOMES]
    for outcome in OUTCOMES:
        sample[f"original_{outcome}"] = original_outcomes[outcome].reindex(
            sample["person_month_key"]
        ).to_numpy()
        sample[f"changed_{outcome}"] = sample[outcome].ne(sample[f"original_{outcome}"])
    sample["above400"] = sample["monthly_fpl"].gt(4.0)
    rows = []
    for (post, above), group in sample.groupby(["post_year2021", "above400"], observed=True):
        record = {
            "post_year2021": int(post),
            "above400": bool(above),
            "person_months": len(group),
            "persons": group["person_id"].nunique(),
            "any_health_patch_row": int(group["health_note_patch_applied"].sum()),
        }
        for outcome in OUTCOMES:
            record[f"changed_{outcome}_rows"] = int(group[f"changed_{outcome}"].sum())
        rows.append(record)
    return pd.DataFrame(rows)


def format_estimate(frame: pd.DataFrame, scenario: str, outcome: str) -> str:
    row = frame.loc[
        frame["data_quality_scenario"].eq(scenario) & frame["outcome"].eq(outcome)
    ].iloc[0]
    return (
        f"coef={row['coef_above_x_post']:.6f}, "
        f"person-cluster SE={row['se_person_cluster']:.6f}, "
        f"t={row['t_person_cluster']:.3f}, N={int(row['n_person_months']):,}"
    )


def main() -> None:
    if not PATCH.exists():
        raise FileNotFoundError(PATCH)
    module = load_base_module()
    print("READ ARPA400 BASE PANEL", flush=True)
    original = module.read_panel()

    valid_weight = apply_valid_official_weight(original)
    corrected = apply_health_patch(valid_weight, module)
    scenarios = [
        run_estimates(module, original, "original_screen_code"),
        run_estimates(module, valid_weight, "official_positive_wpfinwgt_only"),
        run_estimates(
            module,
            corrected,
            "official_positive_wpfinwgt_plus_health_usernote_correction",
        ),
    ]
    estimates = pd.concat(scenarios, ignore_index=True)
    support = build_patch_support(original, corrected)
    RESULT_ROOT.mkdir(parents=True, exist_ok=True)
    estimates.to_csv(ESTIMATES, index=False)
    support.to_csv(PATCH_SUPPORT, index=False)

    original_uninsured = estimates.loc[
        estimates["data_quality_scenario"].eq("original_screen_code")
        & estimates["outcome"].eq("uninsured"),
        "coef_above_x_post",
    ].iloc[0]
    corrected_uninsured = estimates.loc[
        estimates["data_quality_scenario"].eq(
            "official_positive_wpfinwgt_plus_health_usernote_correction"
        )
        & estimates["outcome"].eq("uninsured"),
        "coef_above_x_post",
    ].iloc[0]
    delta = corrected_uninsured - original_uninsured

    lines = [
        "# ARPA 400% FPL Raw-Data Quality Sensitivity",
        "",
        "## Scope",
        "",
        "This is a data-quality sensitivity for the existing local-linear difference-in-discontinuities screen. It is not a final survey-design analysis because it still uses person-clustered standard errors rather than Census Fay-BRR replicate inference.",
        "",
        "## Scenarios",
        "",
        "1. `original_screen_code`: reproduces the existing script, including its invalid `TSSSAMT`/unit-weight fallback.",
        "2. `official_positive_wpfinwgt_only`: retains only positive official `WPFINWGT` values.",
        "3. `official_positive_wpfinwgt_plus_health_usernote_correction`: also applies the Census monthly-health user-note patch for affected 2018-2023 files.",
        "",
        "## Main Uninsured Result",
        "",
        f"- Original: {format_estimate(estimates, 'original_screen_code', 'uninsured')}.",
        f"- Corrected: {format_estimate(estimates, 'official_positive_wpfinwgt_plus_health_usernote_correction', 'uninsured')}.",
        f"- Coefficient change (corrected minus original): {delta:.6f}.",
        "",
        "## Outcome Comparison",
        "",
    ]
    for outcome in OUTCOMES:
        lines.append(
            f"- `{outcome}` original: {format_estimate(estimates, 'original_screen_code', outcome)}; "
            f"corrected: {format_estimate(estimates, 'official_positive_wpfinwgt_plus_health_usernote_correction', outcome)}."
        )
    lines.extend(
        [
            "",
            "## Interpretation Boundary",
            "",
            "The correction follows the official begin/end-month logic and uses `EPR1MTH/EPR2MTH` as the private-plan monthly indicators. The Census web table prints `EHEMPLY{1:2}=1`, but that conflicts with the official data dictionary, observed raw `RPRIMTH`, and the note's own affected-record range. That documentation inconsistency remains an open issue and is not concealed by this sensitivity.",
            "",
            "The Marketplace flag is also not an insurance-type variable: Census states that private, Medicaid, and other coverage can all be reported as Marketplace coverage. It must not be interpreted as clean nongroup Marketplace enrollment without additional source logic.",
            "",
            "## Outputs",
            "",
            f"- `{ESTIMATES.relative_to(ROOT)}`",
            f"- `{PATCH_SUPPORT.relative_to(ROOT)}`",
            f"- `{PATCH.relative_to(ROOT)}`",
        ]
    )
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(
        f"ARPA400 DATA QUALITY SENSITIVITY COMPLETE original={original_uninsured:.6f} "
        f"corrected={corrected_uninsured:.6f} delta={delta:.6f}",
        flush=True,
    )


if __name__ == "__main__":
    main()
