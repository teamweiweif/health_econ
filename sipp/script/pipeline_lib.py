from __future__ import annotations

import json
import math
import os
import re
import shutil
import textwrap
import time
import warnings
import zipfile
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

warnings.filterwarnings("ignore", category=RuntimeWarning)

ROOT = Path(__file__).resolve().parents[1]
ATTACHMENT_PROMPT = Path(
    r"C:\Users\admin\.codex\attachments\3657460f-baf5-436a-8680-f6d6b587838e\pasted-text-1.txt"
)
PRIOR_SOURCE_DIR = Path(r"D:\GlobalHealthPolicy Dropbox\Fan Bowei\US Insurance Project")
META_JSON = ROOT / "temp" / "source_metadata" / "sipp_2018_2024_raw_variable_metadata.enriched.compact.json"

DIRS = [
    "data/analysis_ready",
    "data/policy",
    "data/metadata",
    "data/sample_audits",
    "script/00_setup",
    "script/01_ingest",
    "script/02_metadata_audit",
    "script/03_build_panel",
    "script/04_construct_variables",
    "script/05_policy_files",
    "script/06_descriptive_audit",
    "script/07_causal_models",
    "script/08_causal_ml",
    "script/09_sensitivity",
    "script/10_reporting",
    "result/tables",
    "result/figures",
    "result/models",
    "result/diagnostics",
    "result/logs",
    "report",
    "temp/raw_source_copies",
    "temp/scratch",
    "temp/web_snapshots",
    "temp/exploratory_outputs",
    "temp/failed_specs",
    "temp/gpt_reading_notes",
]

CORE_VARIABLES = [
    "SSUID",
    "PNUM",
    "MONTHCODE",
    "TSSSAMT",
    "SHHADID",
    "SPANEL",
    "SWAVE",
    "GHLFSAM",
    "GVARSTR",
    "WPFINWGT",
    "RFAMNUM",
    "RFAMREF",
    "TEHC_ST",
    "TST_INTV",
    "THHLDSTATUS",
    "TAGE",
    "TAGE_EHC",
    "ESEX",
    "ERACE",
    "EORIGIN",
    "EHISPAN",
    "EEDUC",
    "EMS",
    "RHLTHMTH",
    "RPRIMTH",
    "RPUBMTH",
    "RPUBTYPE1",
    "RPUBTYPE2",
    "RPUBTYPE3",
    "EMDMTH",
    "ECRMTH",
    "EMD_BMONTH",
    "EMD_EMONTH",
    "RMCAIDANN",
    "RMARKTPLACE",
    "RPRITYPE2",
    "EPRIEXCH1",
    "EPRIEXCH2",
    "EPRIPREM1",
    "EPRIPREM2",
    "EPRISUBS1",
    "EPRISUBS2",
    "EMDEXCH",
    "EMDPREM",
    "EMDSUBS",
    "RDIRECTANN",
    "THTOTINC",
    "TFTOTINC",
    "TPTOTINC",
    "THINCPOV",
    "TFINCPOV",
    "THCYINCPOV",
    "TFCYINCPOV",
    "TPEARN",
    "TJB1_MSUM",
    "RMESR",
    "RWKESR1",
    "RWKESR2",
    "RWKESR3",
    "RWKESR4",
    "RWKESR5",
    "RMWKWJB",
    "RSNAP_MNYN",
    "RSNAP_YRYN",
    "RTANF_MNYN",
    "RTANF_YRYN",
    "RSSI_MNYN",
    "RSSI_YRYN",
    "RWIC_MNYN",
    "RWIC_YRYN",
    "EUC1MNYN",
    "EUC2MNYN",
    "EUC3MNYN",
    "EHLTSTAT",
    "RDIS",
    "RDIS_ALT",
    "TMOVER",
    "TRESDUR",
    "EREFPAR",
    "ERP",
    "EPNSPOUSE",
    "ERESIDENCEID",
    "TMDPAY",
    "TVISDOC",
    "TVISDENT",
    "THOSPNIT",
    "TDAYSICK",
    "RFOODR",
    "RFOODS",
]

CONCEPTS = {
    "person_month_key": ["SSUID", "PNUM", "MONTHCODE", "SPANEL", "SWAVE"],
    "state_time": ["TEHC_ST", "TST_INTV", "MONTHCODE"],
    "weights": ["WPFINWGT", "GVARSTR"],
    "coverage_any_public_private": ["RHLTHMTH", "RPUBMTH", "RPRIMTH"],
    "medicaid": ["EMDMTH", "RPUBTYPE2", "EMD_BMONTH", "EMD_EMONTH", "RMCAIDANN"],
    "medicare_exclusion": ["ECRMTH", "RPUBTYPE1"],
    "direct_purchase_exchange": [
        "RMARKTPLACE",
        "RPRITYPE2",
        "EPRIEXCH1",
        "EPRIEXCH2",
        "EPRISUBS1",
        "EPRISUBS2",
        "EMDEXCH",
        "EMDSUBS",
        "RDIRECTANN",
    ],
    "income_poverty": ["TFINCPOV", "THINCPOV", "TFCYINCPOV", "THCYINCPOV", "TFTOTINC", "THTOTINC", "TPTOTINC"],
    "employment": ["RMESR", "RWKESR1", "RWKESR2", "RWKESR3", "RWKESR4", "RWKESR5", "RMWKWJB", "TPEARN"],
    "program_stack": ["RSNAP_MNYN", "RTANF_MNYN", "RSSI_MNYN", "RWIC_MNYN", "EUC1MNYN", "EUC2MNYN", "EUC3MNYN"],
    "health_need": ["EHLTSTAT", "RDIS", "RDIS_ALT"],
    "household_instability": ["TMOVER", "TRESDUR", "ERESIDENCEID", "ERP", "EPNSPOUSE"],
    "financial_utilization": ["TMDPAY", "TVISDOC", "TVISDENT", "THOSPNIT", "TDAYSICK", "RFOODR", "RFOODS"],
}

STATE_FIPS = {
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

EXPANSION_DATES = {
    "02": "2015-09-01",
    "04": "2014-01-01",
    "05": "2014-01-01",
    "06": "2014-01-01",
    "08": "2014-01-01",
    "09": "2014-01-01",
    "10": "2014-01-01",
    "11": "2014-01-01",
    "15": "2014-01-01",
    "16": "2020-01-01",
    "17": "2014-01-01",
    "18": "2015-02-01",
    "19": "2014-01-01",
    "21": "2014-01-01",
    "22": "2016-07-01",
    "23": "2019-01-10",
    "24": "2014-01-01",
    "25": "2014-01-01",
    "26": "2014-04-01",
    "27": "2014-01-01",
    "29": "2021-10-01",
    "30": "2016-01-01",
    "31": "2020-10-01",
    "32": "2014-01-01",
    "33": "2014-08-15",
    "34": "2014-01-01",
    "35": "2014-01-01",
    "36": "2014-01-01",
    "37": "2023-12-01",
    "38": "2014-01-01",
    "39": "2014-01-01",
    "40": "2021-07-01",
    "41": "2014-01-01",
    "42": "2015-01-01",
    "44": "2014-01-01",
    "46": "2023-07-01",
    "49": "2020-01-01",
    "50": "2014-01-01",
    "51": "2019-01-01",
    "53": "2014-01-01",
    "54": "2014-01-01",
}

SOURCE_URLS = [
    "https://www.census.gov/programs-surveys/sipp/data/datasets.html",
    "https://www.census.gov/programs-surveys/sipp/data/datasets/2024-data/2024.html",
    "https://www.census.gov/programs-surveys/sipp/tech-documentation/data-dictionaries.html",
    "https://www.census.gov/programs-surveys/sipp/guidance/users-guide.html",
    "https://www.medicaid.gov/federal-policy-guidance/downloads/sho23002.pdf",
    "https://www.medicaid.gov/medicaid/enrollment-strategies/continuous-eligibility-medicaid-and-chip-coverage",
    "https://www.kff.org/medicaid/status-of-state-medicaid-expansion-decisions/",
    "https://www.kff.org/affordable-care-act/state-indicator/state-activity-around-expanding-medicaid-under-the-affordable-care-act/",
    "https://www.healthcare.gov/medicaid-chip/medicaid-expansion-and-you/",
    "https://www.macpac.gov/subtopic/medicaid-expansion/",
]


@dataclass
class RunContext:
    root: Path = ROOT
    metadata_json: Path = META_JSON
    raw_data_dir: Path = ROOT / "temp" / "raw_downloads" / "census_sipp"
    prior_source_dir: Path = PRIOR_SOURCE_DIR
    pasted_prompt: Path = ATTACHMENT_PROMPT


def log(message: str) -> None:
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    path = ROOT / "result" / "logs" / "pipeline.log"
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(f"[{ts}] {message}\n")
    print(message, flush=True)


def ensure_structure(ctx: RunContext | None = None) -> None:
    for rel in DIRS:
        (ROOT / rel).mkdir(parents=True, exist_ok=True)


def read_text_if_exists(path: Path, max_chars: int | None = None) -> str:
    if not path.exists():
        return ""
    text = path.read_text(encoding="utf-8", errors="replace")
    return text[:max_chars] if max_chars else text


def load_meta() -> dict:
    if not META_JSON.exists():
        raise FileNotFoundError(f"Missing metadata JSON: {META_JSON}")
    return json.loads(META_JSON.read_text(encoding="utf-8-sig"))


def years_from_meta(meta: dict) -> list[str]:
    return sorted(meta.get("years", {}).keys())


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def clean_name(value: str | float | int | None) -> str:
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return ""
    return str(value).strip()


def present_vars(meta: dict, candidates: list[str]) -> list[str]:
    variables = meta.get("variables", {})
    return [v for v in candidates if v in variables]


def variable_description(rec: dict) -> str:
    for yrec in rec.get("years", {}).values():
        cb = yrec.get("codebook") or {}
        desc = clean_name(cb.get("description"))
        if desc:
            return desc
        label = clean_name(yrec.get("variable_label_raw"))
        if label:
            return label
    return ""


def variable_universe(rec: dict) -> str:
    for yrec in rec.get("years", {}).values():
        cb = yrec.get("codebook") or {}
        universe = clean_name(cb.get("universe"))
        if universe:
            return universe
    return ""


def value_map_summary(meta: dict, rec: dict, max_len: int = 500) -> str:
    refs: list[str] = []
    for yrec in rec.get("years", {}).values():
        cb = yrec.get("codebook") or {}
        ref_key = cb.get("possible_values_ref")
        if ref_key and ref_key not in refs:
            refs.append(ref_key)
    summaries = []
    for ref_key in refs[:3]:
        vm = meta.get("value_maps", {}).get(ref_key, {})
        raw = clean_name(vm.get("possible_values_raw"))
        if raw:
            summaries.append(f"{ref_key}: {raw}")
    out = " | ".join(summaries)
    return out[:max_len]


def infer_level(name: str, desc: str) -> str:
    text = f"{name} {desc}".lower()
    if "annual" in text or name.endswith("ANN") or "_YRYN" in name:
        return "annual_or_reference_period"
    if "monthly" in text or "month" in text or name.endswith("MTH") or "_MNYN" in name or "MONTH" in name:
        return "monthly"
    if name.startswith("T") and "income" in text:
        return "monthly"
    if "household" in text or name.startswith("SH") or name.startswith("TH"):
        return "household_or_household_month"
    if "person" in text or name in {"SSUID", "PNUM", "TAGE", "ESEX", "ERACE"}:
        return "person_or_person_month"
    return "unknown"


def recommended_use(name: str) -> str:
    for concept, vars_ in CONCEPTS.items():
        if name in vars_:
            if concept == "medicaid" and name == "EMDMTH":
                return "primary monthly Medicaid measure after agreement audit against RPUBTYPE2"
            if concept == "medicaid" and name == "RPUBTYPE2":
                return "alternative monthly Medicaid measure for sensitivity"
            if concept == "income_poverty" and name == "TFINCPOV":
                return "primary family monthly income-to-poverty running variable"
            return concept
    return ""


def write_source_memos(ctx: RunContext | None = None) -> None:
    ensure_structure()
    ctx = ctx or RunContext()
    prior_files = [
        ctx.prior_source_dir / "HIGH_REASONING_MODEL_HANDOFF.md",
        ctx.prior_source_dir / "docs" / "current_exploration_handoff.md",
        ctx.prior_source_dir / "docs" / "churn_unwinding_post_round4_path_decision.md",
        ctx.prior_source_dir / "docs" / "research_directions_analysis.md",
        ctx.prior_source_dir / "docs" / "deep-research-report(1).md",
        ctx.prior_source_dir / "docs" / "deep-research-report(2).md",
    ]
    available_prior = [p for p in prior_files if p.exists()]
    source_notes = ROOT / "temp" / "web_snapshots" / "source_verification_notes.md"
    source_notes.write_text(
        textwrap.dedent(
            f"""\
            # Source Verification Notes

            Verification date: 2026-07-09.

            Official/current web sources checked:

            - Census SIPP datasets page: confirms access to SIPP data by year 2018-2024 and identifies 2024 as covering January-December 2023.
            - Census 2024 SIPP data page: confirms primary public-use microdata are available in SAS, Stata, and pipe-delimited text formats, with replicate weights also listed.
            - Census SIPP data dictionaries and users guide pages: confirm year-specific data dictionaries and user guides are current documentation sources.
            - CMS SHO-23-002: continuous enrollment condition ended March 31, 2023; terminations after renewal may occur on or after April 1, 2023.
            - Medicaid.gov continuous eligibility page: child 12-month CE is required effective January 1, 2024, so it is not fully evaluable in public SIPP through reference year 2023.
            - KFF expansion status and state indicator pages: current table reports ACA expansion implementation dates by state, including South Dakota July 1, 2023 and North Carolina December 1, 2023.
            - HealthCare.gov and MACPAC: adult expansion is framed as 133% FPL plus 5 percentage-point disregard, usually operationalized as 138% FPL.

            URLs:
            {chr(10).join(f"- {u}" for u in SOURCE_URLS)}
            """
        ),
        encoding="utf-8",
    )

    prior_summary = []
    for p in available_prior:
        text = read_text_if_exists(p, 2500)
        prior_summary.append(
            f"- `{p}`: read. Opening lines indicate: "
            + ("older unwinding diagnostic/risk branch and anti-overclaiming cautions" if "unwinding" in text.lower() else "general project context")
        )

    (ROOT / "report" / "01_source_reading_memo.md").write_text(
        textwrap.dedent(
            f"""\
            # Source Reading Memo

            ## Controlling Source

            The controlling instruction for this run is the pasted goal file:

            `{ctx.pasted_prompt}`

            It selects the SIPP-only adult Medicaid eligibility-boundary design as the immediate design to audit, with child continuous eligibility and 2023 unwinding burden as backups.

            ## Prior Local Materials Read

            {chr(10).join(prior_summary) if prior_summary else "- No prior local source files found."}

            The available prior local files mostly document an older SIPP + CMS unwinding diagnostic/risk-ranking branch. They explicitly warn against causal-effect, DML, causal-forest, and deployment-targeting claims unless identification improves. I therefore treat those files as cautionary background, not as the active design frame. The pasted objective is the active pivot to a SIPP-only adult-boundary audit.

            ## Verified Policy And Data Logic

            - Public SIPP files available locally and on Census cover survey file years 2018-2024, approximately reference years 2017-2023.
            - The 2024 SIPP file covers January-December 2023, so public SIPP does not yet fully evaluate the 2024 child 12-month CE mandate.
            - The PHE continuous enrollment condition ended on March 31, 2023; eligibility terminations after renewal can be effective on or after April 1, 2023.
            - ACA adult expansion eligibility is generally operationalized around 138% FPL in expansion states.

            ## Designs Recommended For Audit

            - Primary: adult near-boundary temporary income crossing around 138% FPL in expansion states.
            - Regime contrast: pre-PHE, PHE continuous enrollment, early unwinding through December 2023.
            - Outcomes: Medicaid exit, exit to uninsured, bridge to private/direct-purchase/exchange, and persistent uninsured gaps.
            - Backup 1: pre-2024 child continuous eligibility if adult-boundary event support fails.
            - Backup 2: 2023 early unwinding administrative-burden design only as early evidence unless state-month metrics provide credible support.

            ## Must Be Verified Rather Than Assumed

            - Exact variable meanings and availability from the local compact metadata JSON and official codebooks.
            - Whether `EMDMTH` and `RPUBTYPE2` agree enough to support a stable Medicaid measure.
            - Whether temporary cross-up events and exit-to-uninsured outcomes have enough support.
            - Whether conventional designs produce credible variation before any causal ML is considered.
            """
        ),
        encoding="utf-8",
    )

    (ROOT / "report" / "00_project_readme.md").write_text(
        textwrap.dedent(
            f"""\
            # SIPP Adult Medicaid Boundary Project

            ## Objective

            Build a reproducible empirical audit of whether temporary income eligibility-risk crossings near the adult Medicaid expansion boundary translate into Medicaid-to-uninsured transitions in SIPP 2017-2023, and whether administrative smoothing during the PHE muted that link.

            ## Local Paths

            - `LOCAL_SIPP_RAW_DATA_DIR`: `{ctx.raw_data_dir}`
            - `LOCAL_SIPP_METADATA_JSON`: `{ctx.metadata_json}`
            - `LOCAL_PRIOR_SOURCE_DIR`: `{ctx.prior_source_dir if ctx.prior_source_dir.exists() else "not found"}`
            - `LOCAL_CHAT_EXPORT_OR_NOTES`: `{ctx.pasted_prompt}`
            - `WORKSPACE_ROOT`: `{ROOT}`

            ## Execution Order

            Run from this directory:

            ```powershell
            python script/run_pipeline.py
            ```

            Phase-specific scripts are stored under `script/00_setup` through `script/10_reporting`; they call the shared implementation in `script/pipeline_lib.py`.

            ## Dependencies

            Required Python packages detected or used: `pandas`, `numpy`, `pyarrow`, `matplotlib`, `sklearn`, `openpyxl`.
            `statsmodels` is not available in the current environment, so transparent weighted linear probability models with robust standard errors are implemented directly with `numpy`.

            ## Storage Boundary

            Raw Census zips remain in `temp/raw_downloads/`. Yearly selected extracts are written to `temp/scratch/`. Clean analysis-ready files are written under `data/analysis_ready/`; reports and model summaries are written under `report/` and `result/`.
            """
        ),
        encoding="utf-8",
    )


def metadata_audit(ctx: RunContext | None = None) -> None:
    ensure_structure()
    meta = load_meta()
    variables = meta.get("variables", {})
    rows = []
    avail_rows = []
    for name, rec in variables.items():
        years = sorted(rec.get("years", {}).keys())
        desc = variable_description(rec)
        universe = variable_universe(rec)
        value_map = value_map_summary(meta, rec)
        row = {
            "variable_name": name,
            "years_present": ";".join(years),
            "n_years_present": len(years),
            "label_description": desc,
            "universe_restrictions": universe,
            "record_level_inferred": infer_level(name, desc),
            "code_list_or_range": value_map,
            "recommended_construction_use": recommended_use(name),
            "harmonization_safe_initial": len(years) == 7,
            "recoding_needed_initial": bool(value_map) or name in set(sum(CONCEPTS.values(), [])),
            "missingness_visible_in_metadata": "",
        }
        rows.append(row)
        for y in years:
            yrec = rec["years"][y]
            cb = yrec.get("codebook") or {}
            avail_rows.append(
                {
                    "variable_name": name,
                    "survey_year": y,
                    "dataset_id": meta.get("years", {}).get(y, {}).get("dataset_id"),
                    "schema_varnum": yrec.get("schema_varnum"),
                    "raw_header_position": yrec.get("raw_header_position"),
                    "description": cb.get("description") or yrec.get("variable_label_raw", ""),
                    "universe": cb.get("universe", ""),
                    "value_map": value_map_summary(meta, {"years": {y: yrec}}, 1000),
                }
            )

    registry = pd.DataFrame(rows).sort_values("variable_name")
    availability = pd.DataFrame(avail_rows).sort_values(["variable_name", "survey_year"])
    registry.to_csv(ROOT / "data" / "metadata" / "variable_registry.csv", index=False)
    availability.to_csv(ROOT / "data" / "metadata" / "variable_year_availability.csv", index=False)

    cross_rows = []
    for concept, vars_ in CONCEPTS.items():
        for v in vars_:
            rec = variables.get(v)
            cross_rows.append(
                {
                    "concept": concept,
                    "variable_name": v,
                    "present": rec is not None,
                    "years_present": ";".join(sorted((rec or {}).get("years", {}).keys())),
                    "description": variable_description(rec) if rec else "",
                    "primary_or_alternative": (
                        "primary"
                        if v in {"EMDMTH", "TFINCPOV", "RHLTHMTH", "WPFINWGT", "TEHC_ST"}
                        else "alternative_or_supporting"
                    ),
                    "construction_note": recommended_use(v),
                }
            )
    pd.DataFrame(cross_rows).to_csv(ROOT / "data" / "metadata" / "concept_crosswalk_initial.csv", index=False)

    core_present = present_vars(meta, CORE_VARIABLES)
    missing = sorted(set(CORE_VARIABLES) - set(core_present))
    report = ROOT / "report" / "02_metadata_audit.md"
    report.write_text(
        textwrap.dedent(
            f"""\
            # Metadata Audit

            Canonical metadata source: `{META_JSON}`

            ## Summary

            - Unique variables in compact metadata: {len(variables):,}
            - Variable-year rows: {len(availability):,}
            - Requested/core variables present: {len(core_present):,}
            - Requested/core variables missing: {len(missing):,}

            Missing or substituted variables:

            {chr(10).join(f"- `{v}`" for v in missing) if missing else "- None."}

            Important substitutions:

            - `TAGE` is present and used for age; `EAGE` is not present.
            - `EORIGIN` and, where available, `EHISPAN` are used for Hispanic origin; `ERACEHISP` is not present.
            - `ECRMTH` and `RPUBTYPE1` are used for Medicare exclusion.

            ## Outputs

            - `data/metadata/variable_registry.csv`
            - `data/metadata/variable_year_availability.csv`
            - `data/metadata/concept_crosswalk_initial.csv`

            ## Initial Construction Decisions

            - Medicaid is constructed primarily from `EMDMTH`, with `RPUBTYPE2` retained for agreement and sensitivity.
            - Any coverage is constructed from `RHLTHMTH`.
            - Direct-purchase/exchange bridge is constructed from `RPRITYPE2`, `RMARKTPLACE`, `EPRIEXCH*`, `EPRISUBS*`, `EMDEXCH`, and `EMDSUBS`.
            - Family monthly income-to-poverty (`TFINCPOV`) is the primary running variable; household ratio (`THINCPOV`) and calendar-year ratios are retained for sensitivity.
            - Annual recodes such as `RMCAIDANN` and `RDIRECTANN` begin only in 2022 and are not primary monthly measures.
            """
        ),
        encoding="utf-8",
    )
    log("metadata audit complete")


def vars_for_panel(meta: dict) -> list[str]:
    extras = []
    # Include all directly relevant core variables that exist; avoid raw thousands of columns.
    for v in CORE_VARIABLES:
        if v in meta.get("variables", {}):
            extras.append(v)
    return sorted(set(extras))


def as_numeric(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series.replace({"": np.nan, " ": np.nan}), errors="coerce")


def normalize_state(series: pd.Series) -> pd.Series:
    num = pd.to_numeric(series, errors="coerce")
    out = num.astype("Int64").astype(str).replace("<NA>", pd.NA).str.zfill(2)
    return out.where(out.isin(STATE_FIPS.keys()), pd.NA)


def optimize_frame(df: pd.DataFrame) -> pd.DataFrame:
    for col in df.columns:
        if col in {"SSUID", "person_id", "person_month_key", "state_fips", "SHHADID", "ERESIDENCEID"}:
            df[col] = df[col].astype("string")
            continue
        if col == "reference_date":
            continue
        if df[col].dtype == object or str(df[col].dtype) == "string":
            s = pd.to_numeric(df[col].replace({"": np.nan, " ": np.nan}), errors="coerce")
            df[col] = pd.to_numeric(s, downcast="float").astype("float32")
    return df


def read_year_extract(year: str, meta: dict, usecols: list[str]) -> dict:
    ymeta = meta["years"][year]
    zip_path = ROOT / ymeta["raw_zip"]["relative_path"]
    if not zip_path.exists():
        raise FileNotFoundError(zip_path)
    file_vars = set(meta["variables"].keys())
    selected = [v for v in usecols if v in file_vars and year in meta["variables"][v].get("years", {})]
    out = ROOT / "temp" / "scratch" / f"sipp_{year}_selected.parquet"
    chunks = []
    row_count = 0
    persons: set[str] = set()
    dup_count = 0
    missingness_acc: dict[str, int] = {v: 0 for v in selected}
    if out.exists():
        out.unlink()
    writer: pq.ParquetWriter | None = None
    schema: pa.Schema | None = None

    for chunk in pd.read_csv(
        zip_path,
        sep="|",
        compression="zip",
        usecols=lambda c: c in set(selected),
        dtype=str,
        chunksize=150_000,
        low_memory=False,
    ):
        row_count += len(chunk)
        for v in selected:
            if v in chunk.columns:
                missingness_acc[v] += int(chunk[v].isna().sum() + (chunk[v].astype(str).str.strip() == "").sum())
        chunk["file_year"] = int(year)
        chunk["reference_year"] = int(year) - 1
        chunk["reference_month"] = pd.to_numeric(chunk.get("MONTHCODE"), errors="coerce").astype("Int16")
        chunk["reference_date"] = pd.to_datetime(
            {
                "year": chunk["reference_year"].astype("Int32"),
                "month": chunk["reference_month"].astype("Int16"),
                "day": 1,
            },
            errors="coerce",
        )
        state_src = chunk["TEHC_ST"] if "TEHC_ST" in chunk.columns else chunk.get("TST_INTV")
        chunk["state_fips"] = normalize_state(state_src)
        chunk["SSUID"] = chunk["SSUID"].astype("string") if "SSUID" in chunk else pd.NA
        chunk["PNUM"] = pd.to_numeric(chunk["PNUM"], errors="coerce") if "PNUM" in chunk else pd.NA
        chunk["person_id"] = chunk["SSUID"].astype(str) + "-" + chunk["PNUM"].astype("Int64").astype(str)
        chunk["person_month_key"] = (
            chunk["file_year"].astype(str)
            + "-"
            + chunk["SSUID"].astype(str)
            + "-"
            + chunk["PNUM"].astype("Int64").astype(str)
            + "-"
            + chunk["reference_month"].astype("Int64").astype(str)
        )
        dup_count += int(chunk.duplicated(["SSUID", "PNUM", "MONTHCODE"]).sum())
        persons.update(chunk["person_id"].dropna().astype(str).unique().tolist())
        chunk = optimize_frame(chunk)
        table = pa.Table.from_pandas(chunk, preserve_index=False) if schema is None else pa.Table.from_pandas(chunk, schema=schema, preserve_index=False)
        if writer is None:
            schema = table.schema
            writer = pq.ParquetWriter(out, schema, compression="snappy")
        writer.write_table(table)
    if writer is not None:
        writer.close()

    return {
        "file_year": int(year),
        "reference_year": int(year) - 1,
        "rows": row_count,
        "unique_persons_seen": len(persons),
        "duplicate_ssuid_pnum_monthcode_within_file": dup_count,
        "selected_variable_count": len(selected),
        "parquet_path": rel(out),
        "raw_zip_path": rel(zip_path),
        "raw_zip_bytes": zip_path.stat().st_size,
    }


def build_panel(ctx: RunContext | None = None) -> None:
    ensure_structure()
    meta = load_meta()
    usecols = vars_for_panel(meta)
    audit_rows = []
    missing_rows = []
    for year in years_from_meta(meta):
        log(f"building selected extract for SIPP {year}")
        stats = read_year_extract(year, meta, usecols)
        audit_rows.append(stats)
        df = pd.read_parquet(ROOT / stats["parquet_path"])
        for col in usecols:
            if col in df.columns:
                missing_rows.append(
                    {
                        "file_year": year,
                        "variable_name": col,
                        "rows": len(df),
                        "missing": int(df[col].isna().sum()),
                        "missing_rate": float(df[col].isna().mean()),
                    }
                )
        del df

    yearly = [pd.read_parquet(ROOT / row["parquet_path"]) for row in audit_rows]
    panel = pd.concat(yearly, ignore_index=True, sort=False)
    panel = panel.sort_values(["person_id", "reference_date", "file_year", "reference_month"])
    panel.to_parquet(ROOT / "data" / "analysis_ready" / "sipp_2018_2024_person_month_panel.parquet", index=False)

    audit = pd.DataFrame(audit_rows)
    audit.to_csv(ROOT / "data" / "sample_audits" / "panel_build_yearly_counts.csv", index=False)
    pd.DataFrame(missing_rows).to_csv(ROOT / "data" / "sample_audits" / "selected_variable_missingness.csv", index=False)

    state_avail = panel.groupby(["file_year", "reference_year"])["state_fips"].agg(
        rows="size", missing_state=lambda s: int(s.isna().sum()), states_present=lambda s: int(s.nunique(dropna=True))
    )
    state_avail.reset_index().to_csv(ROOT / "data" / "sample_audits" / "state_variable_availability.csv", index=False)

    report = ROOT / "report" / "03_data_build_audit.md"
    report.write_text(
        textwrap.dedent(
            f"""\
            # Data Build Audit

            ## Input

            - Raw local SIPP directory: `{ROOT / "temp" / "raw_downloads" / "census_sipp"}`
            - Metadata JSON: `{META_JSON}`
            - Ingested format: Census pipe-delimited primary CSV files inside zip archives.

            ## Output

            - `data/analysis_ready/sipp_2018_2024_person_month_panel.parquet`
            - Yearly selected extracts in `temp/scratch/sipp_YYYY_selected.parquet`
            - Audit tables in `data/sample_audits/`

            ## File-Year Mapping

            SIPP file year is mapped to reference year as `file_year - 1`, consistent with the 2024 SIPP page stating that 2024 covers January-December 2023.

            ## Counts

            {audit.to_string(index=False)}

            ## Key Integrity Notes

            - `SSUID + PNUM + MONTHCODE` is checked within each file year.
            - The final technical row key includes `file_year` because the same `SSUID + PNUM + MONTHCODE` can recur across annual SIPP waves.
            - Replicate and longitudinal weights are noted by Census but not fully populated locally; this run uses `WPFINWGT` and reports unweighted robustness.
            """
        ),
        encoding="utf-8",
    )
    log("panel build complete")


def yes(series: pd.Series) -> pd.Series:
    return (pd.to_numeric(series, errors="coerce") == 1).astype("Int8")


def no(series: pd.Series) -> pd.Series:
    return (pd.to_numeric(series, errors="coerce") == 2).astype("Int8")


def month_diff(a: pd.Series, b: pd.Series) -> pd.Series:
    return (a.dt.year - b.dt.year) * 12 + (a.dt.month - b.dt.month)


def add_lags(df: pd.DataFrame, cols: list[str], max_lag: int = 3, max_lead: int = 3) -> pd.DataFrame:
    g = df.groupby("person_id", sort=False)
    for c in cols:
        if c not in df.columns:
            continue
        for k in range(1, max_lag + 1):
            df[f"{c}_lag{k}"] = g[c].shift(k)
        for k in range(1, max_lead + 1):
            df[f"{c}_lead{k}"] = g[c].shift(-k)
    df["date_lag1"] = g["reference_date"].shift(1)
    df["date_lead1"] = g["reference_date"].shift(-1)
    df["date_lead2"] = g["reference_date"].shift(-2)
    df["date_lead3"] = g["reference_date"].shift(-3)
    df["adjacent_lag1"] = (month_diff(df["reference_date"], df["date_lag1"]) == 1).astype("Int8")
    for k in [1, 2, 3]:
        df[f"adjacent_lead{k}"] = (month_diff(df[f"date_lead{k}"], df["reference_date"]) == k).astype("Int8")
    return df


def construct_variables(ctx: RunContext | None = None) -> None:
    ensure_structure()
    panel_path = ROOT / "data" / "analysis_ready" / "sipp_2018_2024_person_month_panel.parquet"
    if not panel_path.exists():
        build_panel()
    df = pd.read_parquet(panel_path)
    df = df.sort_values(["person_id", "reference_date", "file_year", "reference_month"]).reset_index(drop=True)

    for col in ["RHLTHMTH", "RPRIMTH", "RPUBMTH", "RPUBTYPE1", "RPUBTYPE2", "EMDMTH", "ECRMTH", "RPRITYPE2", "RMARKTPLACE"]:
        if col not in df.columns:
            df[col] = np.nan
    for col in ["EPRIEXCH1", "EPRIEXCH2", "EPRISUBS1", "EPRISUBS2", "EMDEXCH", "EMDSUBS"]:
        if col not in df.columns:
            df[col] = np.nan

    df["any_coverage_it"] = yes(df["RHLTHMTH"])
    df["uninsured_it"] = no(df["RHLTHMTH"])
    df["private_coverage_it"] = yes(df["RPRIMTH"])
    df["public_coverage_it"] = yes(df["RPUBMTH"])
    df["medicaid_it"] = yes(df["EMDMTH"])
    df["medicaid_alt_rpubtype2_it"] = yes(df["RPUBTYPE2"])
    df["medicare_it"] = ((yes(df["ECRMTH"]) == 1) | (yes(df["RPUBTYPE1"]) == 1)).astype("Int8")
    df["direct_purchase_or_marketplace_it"] = (
        (yes(df["RPRITYPE2"]) == 1) | (yes(df["RMARKTPLACE"]) == 1)
    ).astype("Int8")
    df["exchange_or_subsidized_private_it"] = (
        (yes(df["EPRIEXCH1"]) == 1)
        | (yes(df["EPRIEXCH2"]) == 1)
        | (yes(df["EPRISUBS1"]) == 1)
        | (yes(df["EPRISUBS2"]) == 1)
        | (yes(df["EMDEXCH"]) == 1)
        | (yes(df["EMDSUBS"]) == 1)
    ).astype("Int8")
    df["medicaid_definition_disagree"] = (df["medicaid_it"] != df["medicaid_alt_rpubtype2_it"]).astype("Int8")

    numeric_vars = [
        "TFINCPOV",
        "THINCPOV",
        "TFCYINCPOV",
        "THCYINCPOV",
        "TFTOTINC",
        "THTOTINC",
        "TPTOTINC",
        "TPEARN",
        "TAGE",
        "WPFINWGT",
        "RMWKWJB",
    ]
    for v in numeric_vars:
        if v in df.columns:
            df[v] = pd.to_numeric(df[v], errors="coerce")
    df["age"] = df.get("TAGE")
    df["weight"] = pd.to_numeric(df.get("WPFINWGT"), errors="coerce")
    df["income_poverty_ratio"] = pd.to_numeric(df.get("TFINCPOV"), errors="coerce")
    df.loc[df["income_poverty_ratio"] < 0, "income_poverty_ratio"] = np.nan
    df["income_poverty_ratio_hh"] = pd.to_numeric(df.get("THINCPOV"), errors="coerce")
    df["reference_period"] = pd.to_datetime(df["reference_date"])

    df = add_lags(
        df,
        [
            "any_coverage_it",
            "uninsured_it",
            "private_coverage_it",
            "public_coverage_it",
            "medicaid_it",
            "direct_purchase_or_marketplace_it",
            "exchange_or_subsidized_private_it",
            "income_poverty_ratio",
            "TPEARN",
            "RMESR",
            "RMWKWJB",
        ],
        3,
        3,
    )

    df["medicaid_spell_start_it"] = (
        (df["medicaid_it"] == 1)
        & ((df["medicaid_it_lag1"] != 1) | (df["adjacent_lag1"] != 1))
    ).astype("Int8")
    df["medicaid_spell_end_it"] = (
        (df["medicaid_it"] == 1)
        & ((df["medicaid_it_lead1"] != 1) | (df["adjacent_lead1"] != 1))
    ).astype("Int8")
    df["medicaid_exit_it"] = (
        (df["adjacent_lag1"] == 1) & (df["medicaid_it_lag1"] == 1) & (df["medicaid_it"] != 1)
    ).astype("Int8")
    df["exit_to_uninsured_it"] = ((df["medicaid_exit_it"] == 1) & (df["uninsured_it"] == 1)).astype("Int8")
    df["exit_to_private_it"] = ((df["medicaid_exit_it"] == 1) & (df["private_coverage_it"] == 1)).astype("Int8")
    df["exit_to_direct_purchase_exchange_it"] = (
        (df["medicaid_exit_it"] == 1)
        & ((df["direct_purchase_or_marketplace_it"] == 1) | (df["exchange_or_subsidized_private_it"] == 1))
    ).astype("Int8")
    df["exit_to_other_public_it"] = (
        (df["medicaid_exit_it"] == 1) & (df["public_coverage_it"] == 1) & (df["medicaid_it"] != 1)
    ).astype("Int8")
    df["any_coverage_loss_it"] = (
        (df["adjacent_lag1"] == 1) & (df["any_coverage_it_lag1"] == 1) & (df["uninsured_it"] == 1)
    ).astype("Int8")

    df["uninsured_1m_after_exit"] = ((df["medicaid_exit_it"] == 1) & (df["uninsured_it_lead1"] == 1) & (df["adjacent_lead1"] == 1)).astype("Int8")
    df["uninsured_2m_after_exit"] = ((df["medicaid_exit_it"] == 1) & (df["uninsured_it_lead2"] == 1) & (df["adjacent_lead2"] == 1)).astype("Int8")
    df["uninsured_3m_after_exit"] = ((df["medicaid_exit_it"] == 1) & (df["uninsured_it_lead3"] == 1) & (df["adjacent_lead3"] == 1)).astype("Int8")
    df["persistent_uninsured_2m"] = (
        (df["medicaid_exit_it"] == 1)
        & (df["uninsured_it"] == 1)
        & (df["uninsured_it_lead1"] == 1)
        & (df["adjacent_lead1"] == 1)
    ).astype("Int8")
    df["persistent_uninsured_3m"] = (
        (df["persistent_uninsured_2m"] == 1)
        & (df["uninsured_it_lead2"] == 1)
        & (df["adjacent_lead2"] == 1)
    ).astype("Int8")
    df["months_uninsured_after_first_exit"] = (
        (df["uninsured_it"] == 1).astype(int)
        + ((df["uninsured_it_lead1"] == 1) & (df["adjacent_lead1"] == 1)).astype(int)
        + ((df["uninsured_it_lead2"] == 1) & (df["adjacent_lead2"] == 1)).astype(int)
        + ((df["uninsured_it_lead3"] == 1) & (df["adjacent_lead3"] == 1)).astype(int)
    ).where(df["medicaid_exit_it"] == 1)

    df["reference_year"] = pd.to_numeric(df["reference_year"], errors="coerce").astype("Int16")
    df["churn_count_within_year"] = (
        df.groupby(["person_id", "reference_year"], sort=False)["any_coverage_loss_it"].transform("sum").astype("Int16")
    )
    df["medicaid_onoff_transition_count"] = (
        df.groupby(["person_id", "reference_year"], sort=False)["medicaid_exit_it"].transform("sum").astype("Int16")
    )

    threshold = 1.38
    ratio = df["income_poverty_ratio"]
    ratio_lag = df["income_poverty_ratio_lag1"]
    df["near_boundary_it"] = ratio.between(1.00, 1.75).astype("Int8")
    df["below_threshold_it"] = (ratio <= threshold).astype("Int8")
    df["above_threshold_it"] = (ratio > threshold).astype("Int8")
    df["cross_up_it"] = (
        (df["adjacent_lag1"] == 1) & (ratio_lag <= threshold) & (ratio > threshold)
    ).astype("Int8")
    df["cross_down_it"] = (
        (df["adjacent_lag1"] == 1) & (ratio_lag > threshold) & (ratio <= threshold)
    ).astype("Int8")
    for k in [1, 2, 3]:
        returns = []
        for j in range(1, k + 1):
            returns.append((df[f"income_poverty_ratio_lead{j}"] <= threshold) & (df[f"adjacent_lead{j}"] == 1))
        df[f"temporary_cross_up_{k}m"] = ((df["cross_up_it"] == 1) & np.logical_or.reduce(returns)).astype("Int8")
    df["sustained_cross_up"] = (
        (df["cross_up_it"] == 1)
        & (df["income_poverty_ratio_lead1"] > threshold)
        & (df["income_poverty_ratio_lead2"] > threshold)
        & (df["income_poverty_ratio_lead3"] > threshold)
        & (df["adjacent_lead1"] == 1)
        & (df["adjacent_lead2"] == 1)
        & (df["adjacent_lead3"] == 1)
    ).astype("Int8")
    df["income_volatility_abs"] = (ratio - ratio_lag).abs().where(df["adjacent_lag1"] == 1)
    df["income_volatility_pct"] = ((ratio - ratio_lag) / ratio_lag.replace(0, np.nan)).where(df["adjacent_lag1"] == 1)

    employed = pd.to_numeric(df.get("RMESR"), errors="coerce").isin([1, 2, 3, 4, 5]).astype("Int8")
    df["employed_it"] = employed
    df["employment_gain_it"] = ((df["employed_it"] == 1) & (df["RMESR_lag1"].isin([6, 7, 8])) & (df["adjacent_lag1"] == 1)).astype("Int8")
    df["employment_loss_it"] = ((df["employed_it"] == 0) & (pd.to_numeric(df["RMESR_lag1"], errors="coerce").isin([1, 2, 3, 4, 5])) & (df["adjacent_lag1"] == 1)).astype("Int8")
    df["earnings_jump_it"] = ((pd.to_numeric(df.get("TPEARN"), errors="coerce") - pd.to_numeric(df.get("TPEARN_lag1"), errors="coerce")) > 500).astype("Int8")
    df["earnings_loss_it"] = ((pd.to_numeric(df.get("TPEARN_lag1"), errors="coerce") - pd.to_numeric(df.get("TPEARN"), errors="coerce")) > 500).astype("Int8")
    df["employment_driven_crossing"] = ((df["temporary_cross_up_1m"] == 1) & ((df["employment_gain_it"] == 1) | (df["earnings_jump_it"] == 1))).astype("Int8")

    for c in ["RSNAP_MNYN", "RTANF_MNYN", "RSSI_MNYN", "RWIC_MNYN", "EUC1MNYN", "EUC2MNYN", "EUC3MNYN"]:
        if c not in df.columns:
            df[c] = np.nan
    df["program_stack_it"] = sum(yes(df[c]) for c in ["RSNAP_MNYN", "RTANF_MNYN", "RSSI_MNYN", "RWIC_MNYN", "EUC1MNYN", "EUC2MNYN", "EUC3MNYN"])
    df["health_need_it"] = (
        (yes(df.get("RDIS", pd.Series(index=df.index))) == 1)
        | (yes(df.get("RDIS_ALT", pd.Series(index=df.index))) == 1)
        | (pd.to_numeric(df.get("EHLTSTAT"), errors="coerce").isin([4, 5]))
    ).astype("Int8")
    df["household_instability_it"] = (
        (yes(df.get("TMOVER", pd.Series(index=df.index))) == 1)
        | (df.groupby("person_id")["ERESIDENCEID"].shift(1).astype("string") != df["ERESIDENCEID"].astype("string"))
    ).fillna(False).astype("Int8")

    first3 = df.groupby("person_id", sort=False).cumcount() < 3
    baseline = (
        df.loc[first3]
        .groupby("person_id")
        .agg(
            program_stack_i0=("program_stack_it", "max"),
            health_need_i0=("health_need_it", "max"),
            household_instability_i0=("household_instability_it", "max"),
            prior_churn_i0=("medicaid_exit_it", "sum"),
            income_volatility_i0=("income_volatility_abs", "mean"),
        )
        .reset_index()
    )
    df = df.merge(baseline, on="person_id", how="left")
    df["admin_match_proxy_i0"] = (df["program_stack_i0"].fillna(0) > 0).astype("Int8")

    # Regime and expansion status are merged after policy files are built.
    build_policy_files()
    policy = pd.read_csv(ROOT / "data" / "policy" / "state_month_policy_regime.csv", dtype={"state_fips": str})
    policy["reference_date"] = pd.to_datetime(policy["reference_date"])
    policy = policy.drop(columns=[c for c in ["reference_year", "reference_month"] if c in policy.columns])
    df = df.merge(policy, on=["state_fips", "reference_date"], how="left")

    coverage_cols = [
        "person_month_key",
        "person_id",
        "file_year",
        "reference_year",
        "reference_month",
        "reference_date",
        "state_fips",
        "age",
        "weight",
        "any_coverage_it",
        "medicaid_it",
        "medicaid_alt_rpubtype2_it",
        "public_coverage_it",
        "private_coverage_it",
        "uninsured_it",
        "direct_purchase_or_marketplace_it",
        "exchange_or_subsidized_private_it",
        "medicaid_spell_start_it",
        "medicaid_spell_end_it",
        "medicaid_exit_it",
        "exit_to_uninsured_it",
        "exit_to_private_it",
        "exit_to_direct_purchase_exchange_it",
        "exit_to_other_public_it",
        "any_coverage_loss_it",
        "uninsured_1m_after_exit",
        "uninsured_2m_after_exit",
        "uninsured_3m_after_exit",
        "persistent_uninsured_2m",
        "persistent_uninsured_3m",
        "months_uninsured_after_first_exit",
        "churn_count_within_year",
        "medicaid_onoff_transition_count",
    ]
    exposure_cols = coverage_cols + [
        "income_poverty_ratio",
        "income_poverty_ratio_lag1",
        "income_poverty_ratio_hh",
        "adjacent_lag1",
        "adjacent_lead1",
        "adjacent_lead2",
        "adjacent_lead3",
        "near_boundary_it",
        "below_threshold_it",
        "above_threshold_it",
        "cross_up_it",
        "cross_down_it",
        "temporary_cross_up_1m",
        "temporary_cross_up_2m",
        "temporary_cross_up_3m",
        "sustained_cross_up",
        "income_volatility_abs",
        "income_volatility_pct",
        "employment_gain_it",
        "employment_loss_it",
        "earnings_jump_it",
        "earnings_loss_it",
        "employment_driven_crossing",
        "program_stack_it",
        "program_stack_i0",
        "health_need_i0",
        "household_instability_i0",
        "prior_churn_i0",
        "income_volatility_i0",
        "admin_match_proxy_i0",
        "medicare_it",
        "expansion_state_month",
        "policy_regime",
        "pre_phe_regime",
        "phe_continuous_enrollment_regime",
        "early_unwinding_regime",
        "ESEX",
        "ERACE",
        "EORIGIN",
        "EHISPAN",
        "EEDUC",
        "ERP",
        "RSSI_MNYN",
        "RDIS",
        "RDIS_ALT",
        "RMESR",
    ]
    df[[c for c in coverage_cols if c in df.columns]].to_parquet(ROOT / "data" / "analysis_ready" / "coverage_transition_panel.parquet", index=False)
    df[[c for c in exposure_cols if c in df.columns]].to_parquet(ROOT / "data" / "analysis_ready" / "exposure_temporary_crossing_panel.parquet", index=False)

    make_transition_tables(df)
    report_variable_construction(df)
    log("variable construction complete")


def build_policy_files(ctx: RunContext | None = None) -> None:
    ensure_structure()
    months = pd.date_range("2017-01-01", "2023-12-01", freq="MS")
    rows = []
    expansion_rows = []
    for state_fips, state_name in STATE_FIPS.items():
        exp_date = EXPANSION_DATES.get(state_fips)
        exp_ts = pd.to_datetime(exp_date) if exp_date else pd.NaT
        for dt in months:
            pre = dt < pd.Timestamp("2020-03-01")
            phe = pd.Timestamp("2020-03-01") <= dt <= pd.Timestamp("2023-03-01")
            unwind = pd.Timestamp("2023-04-01") <= dt <= pd.Timestamp("2023-12-01")
            expansion = bool(pd.notna(exp_ts) and dt >= pd.Timestamp(exp_ts.year, exp_ts.month, 1))
            regime = "pre_phe" if pre else ("phe_continuous_enrollment" if phe else ("early_unwinding" if unwind else "other"))
            row = {
                "state_fips": state_fips,
                "state_name": state_name,
                "reference_date": dt.strftime("%Y-%m-%d"),
                "reference_year": dt.year,
                "reference_month": dt.month,
                "pre_phe_regime": int(pre),
                "phe_continuous_enrollment_regime": int(phe),
                "early_unwinding_regime": int(unwind),
                "policy_regime": regime,
                "expansion_state_month": int(expansion),
                "expansion_implementation_date": exp_date or "",
                "source": "KFF Medicaid expansion table; CMS SHO-23-002; Census SIPP release pages",
            }
            rows.append(row)
            expansion_rows.append(
                {
                    "state_fips": state_fips,
                    "state_name": state_name,
                    "reference_date": dt.strftime("%Y-%m-%d"),
                    "expansion_state_month": int(expansion),
                    "expansion_implementation_date": exp_date or "",
                    "source": "KFF State Health Facts expansion decision table, viewed 2026-07-09",
                }
            )
    pd.DataFrame(rows).to_csv(ROOT / "data" / "policy" / "state_month_policy_regime.csv", index=False)
    pd.DataFrame(expansion_rows).to_csv(ROOT / "data" / "policy" / "medicaid_expansion_state_month.csv", index=False)
    child_rows = []
    for state_fips, state_name in STATE_FIPS.items():
        for year in range(2017, 2024):
            child_rows.append(
                {
                    "state_fips": state_fips,
                    "state_name": state_name,
                    "year": year,
                    "child_ce_pre2024_state_year": "",
                    "source": "not built in this run; backup only and requires state-specific verification",
                }
            )
    pd.DataFrame(child_rows).to_csv(ROOT / "data" / "policy" / "child_ce_pre2024_state_year.csv", index=False)

    (ROOT / "report" / "05_empirical_design_memo.md").write_text(
        textwrap.dedent(
            """\
            # Empirical Design Memo

            ## Primary Design

            The primary design tests whether temporary cross-up events around the adult Medicaid expansion boundary translate into Medicaid exits, exit-to-uninsured, bridge coverage, and persistent uninsured gaps.

            ## Regime Logic

            - Pre-PHE: January 2017 through February 2020.
            - PHE continuous enrollment: March 2020 through March 2023.
            - Early unwinding: April 2023 through December 2023.

            CMS SHO-23-002 verifies that the continuous enrollment condition ended March 31, 2023 and that terminations after renewal could occur on or after April 1, 2023.

            ## Expansion Boundary

            The main adult MAGI boundary is 138% FPL in expansion states. In SIPP `TFINCPOV`, this is stored as `1.38`, not `138`. Robustness checks use 1.00, 1.33, 1.38, and 1.50 ratio units and multiple bandwidths.

            ## Identification Standard

            This is not assumed to be causal. The pipeline first checks support, transition counts, pre-period behavior, and robustness. Causal ML is prohibited unless conventional estimates pass the support and credibility screens.
            """
        ),
        encoding="utf-8",
    )


def make_transition_tables(df: pd.DataFrame) -> None:
    df = df.copy()
    df["prev_medicaid"] = df.groupby("person_id")["medicaid_it"].shift(1)
    conds = [
        ((df["prev_medicaid"] == 1) & (df["medicaid_it"] == 1)).fillna(False).to_numpy(dtype=bool),
        ((df["prev_medicaid"] == 1) & (df["exit_to_uninsured_it"] == 1)).fillna(False).to_numpy(dtype=bool),
        ((df["prev_medicaid"] == 1) & (df["exit_to_private_it"] == 1)).fillna(False).to_numpy(dtype=bool),
        ((df["prev_medicaid"] == 1) & (df["exit_to_direct_purchase_exchange_it"] == 1)).fillna(False).to_numpy(dtype=bool),
        ((df["prev_medicaid"] == 1) & (df["exit_to_other_public_it"] == 1)).fillna(False).to_numpy(dtype=bool),
        ((df["prev_medicaid"] == 1) & (df["medicaid_it"] != 1)).fillna(False).to_numpy(dtype=bool),
    ]
    df["path"] = np.select(
        conds,
        [
            "Medicaid_to_Medicaid",
            "Medicaid_to_uninsured",
            "Medicaid_to_private",
            "Medicaid_to_direct_purchase_exchange",
            "Medicaid_to_other_public",
            "Medicaid_to_unknown_missing",
        ],
        default="not_prior_medicaid",
    )
    matrix = (
        df[df["prev_medicaid"] == 1]
        .groupby(["reference_year", "path"])
        .size()
        .reset_index(name="n")
    )
    matrix.to_csv(ROOT / "result" / "tables" / "coverage_transition_matrix_by_year.csv", index=False)
    counts = (
        df.groupby(["reference_year", "policy_regime"])
        .agg(
            rows=("person_month_key", "size"),
            medicaid_months=("medicaid_it", "sum"),
            medicaid_exits=("medicaid_exit_it", "sum"),
            exit_to_uninsured=("exit_to_uninsured_it", "sum"),
            exit_to_direct_purchase_exchange=("exit_to_direct_purchase_exchange_it", "sum"),
            persistent_uninsured_2m=("persistent_uninsured_2m", "sum"),
            temporary_cross_up_1m=("temporary_cross_up_1m", "sum"),
            temporary_cross_up_2m=("temporary_cross_up_2m", "sum"),
            temporary_cross_up_3m=("temporary_cross_up_3m", "sum"),
        )
        .reset_index()
    )
    counts.to_csv(ROOT / "result" / "tables" / "coverage_outcome_counts_by_year_regime.csv", index=False)


def report_variable_construction(df: pd.DataFrame) -> None:
    agree = df[["medicaid_it", "medicaid_alt_rpubtype2_it"]].dropna()
    agreement = float((agree["medicaid_it"] == agree["medicaid_alt_rpubtype2_it"]).mean()) if len(agree) else np.nan
    summary = pd.Series(
        {
            "rows": df["person_month_key"].count(),
            "medicaid_months": df["medicaid_it"].sum(),
            "medicaid_exits": df["medicaid_exit_it"].sum(),
            "exit_to_uninsured": df["exit_to_uninsured_it"].sum(),
            "temporary_cross_up_1m": df["temporary_cross_up_1m"].sum(),
            "temporary_cross_up_2m": df["temporary_cross_up_2m"].sum(),
            "temporary_cross_up_3m": df["temporary_cross_up_3m"].sum(),
        }
    )
    (ROOT / "report" / "04_variable_construction_memo.md").write_text(
        textwrap.dedent(
            f"""\
            # Variable Construction Memo

            ## Coverage Measures

            - `any_coverage_it`: `RHLTHMTH == 1`
            - `uninsured_it`: `RHLTHMTH == 2`
            - `medicaid_it`: primary, `EMDMTH == 1`
            - `medicaid_alt_rpubtype2_it`: sensitivity, `RPUBTYPE2 == 1`
            - `direct_purchase_or_marketplace_it`: `RPRITYPE2 == 1` or `RMARKTPLACE == 1`
            - `exchange_or_subsidized_private_it`: exchange/subsidy indicators from private and Medicaid exchange variables.

            Primary Medicaid agreement between `EMDMTH` and `RPUBTYPE2`: {agreement:.4f}

            ## Income Shocks

            The primary running variable is `TFINCPOV`, stored as a ratio where `1.38` equals 138% FPL. The main threshold is 1.38 and the main near-boundary window is 1.00-1.75 ratio units, equivalent to 100-175% FPL. Temporary cross-up events return below threshold within 1, 2, or 3 contiguous months.

            ## Core Counts

            {summary.to_string()}

            ## Outputs

            - `data/analysis_ready/coverage_transition_panel.parquet`
            - `data/analysis_ready/exposure_temporary_crossing_panel.parquet`
            - `result/tables/coverage_transition_matrix_by_year.csv`
            - `result/tables/coverage_outcome_counts_by_year_regime.csv`
            """
        ),
        encoding="utf-8",
    )


def analysis_sample(df: pd.DataFrame, primary: bool = True, expansion_only: bool = True) -> pd.DataFrame:
    out = df.copy()
    out["adult_19_64"] = out["age"].between(19, 64)
    mask = out["adult_19_64"] & (out["medicare_it"] != 1) & out["income_poverty_ratio"].notna() & out["state_fips"].notna()
    if primary:
        mask &= (out["near_boundary_it"] == 1)
        mask &= ~(yes(out.get("RSSI_MNYN", pd.Series(index=out.index))) == 1)
        mask &= ~(yes(out.get("RDIS", pd.Series(index=out.index))) == 1)
        mask &= ~(yes(out.get("RDIS_ALT", pd.Series(index=out.index))) == 1)
    if expansion_only and "expansion_state_month" in out:
        mask &= out["expansion_state_month"] == 1
    return out.loc[mask].copy()


def descriptive_audit(ctx: RunContext | None = None) -> None:
    ensure_structure()
    path = ROOT / "data" / "analysis_ready" / "exposure_temporary_crossing_panel.parquet"
    if not path.exists():
        construct_variables()
    df = pd.read_parquet(path)
    sample = analysis_sample(df, primary=True, expansion_only=True)
    sample_counts = (
        sample.groupby(["reference_year", "policy_regime"])
        .agg(
            rows=("person_month_key", "size"),
            persons=("person_id", "nunique"),
            medicaid_months=("medicaid_it", "sum"),
            temporary_cross_up_1m=("temporary_cross_up_1m", "sum"),
            temporary_cross_up_2m=("temporary_cross_up_2m", "sum"),
            temporary_cross_up_3m=("temporary_cross_up_3m", "sum"),
            medicaid_exits=("medicaid_exit_it", "sum"),
            exit_to_uninsured=("exit_to_uninsured_it", "sum"),
            exit_to_private=("exit_to_private_it", "sum"),
            persistent_uninsured_2m=("persistent_uninsured_2m", "sum"),
            persistent_uninsured_3m=("persistent_uninsured_3m", "sum"),
        )
        .reset_index()
    )
    sample_counts.to_csv(ROOT / "result" / "tables" / "sample_counts_by_year_regime.csv", index=False)
    sample_counts.to_csv(ROOT / "result" / "tables" / "temporary_crossing_counts_by_year_regime.csv", index=False)

    tw_rows = []
    for threshold in [1.00, 1.33, 1.38, 1.50, 2.50]:
        for lo, hi in [(0.75, 2.00), (1.00, 1.75), (1.00, 2.00), (1.25, 1.75)]:
            near = df["income_poverty_ratio"].between(lo, hi)
            prev = df["income_poverty_ratio_lag1"] if "income_poverty_ratio_lag1" in df.columns else np.nan
            cross = (df["adjacent_lag1"] == 1) & (prev <= threshold) & (df["income_poverty_ratio"] > threshold) & near
            tw_rows.append(
                {
                    "threshold": threshold,
                    "window_low": lo,
                    "window_high": hi,
                    "rows": int(near.sum()),
                    "cross_up": int(cross.sum()),
                    "medicaid_exit_among_cross_up": int(((df["medicaid_exit_it"] == 1) & cross).sum()),
                    "exit_to_uninsured_among_cross_up": int(((df["exit_to_uninsured_it"] == 1) & cross).sum()),
                }
            )
    pd.DataFrame(tw_rows).to_csv(ROOT / "result" / "tables" / "crossing_outcome_counts_by_threshold_window.csv", index=False)

    make_figures(df, sample)
    go_no_go(sample, sample_counts)
    log("descriptive audit complete")


def make_figures(df: pd.DataFrame, sample: pd.DataFrame) -> None:
    import matplotlib.pyplot as plt

    figdir = ROOT / "result" / "figures"
    x = sample["income_poverty_ratio"].dropna()
    x = x[(x >= 0) & (x <= 3)]
    plt.figure(figsize=(8, 5))
    plt.hist(x, bins=60, color="#4169a8", alpha=0.85)
    plt.axvline(1.38, color="#b03a2e", linestyle="--", linewidth=1.5)
    plt.xlabel("Family income-to-poverty ratio (1.38 = 138% FPL)")
    plt.ylabel("Person-months")
    plt.tight_layout()
    plt.savefig(figdir / "income_crossing_distribution.png", dpi=150)
    plt.close()

    matrix = pd.read_csv(ROOT / "result" / "tables" / "coverage_transition_matrix_by_year.csv")
    pivot = matrix.pivot_table(index="reference_year", columns="path", values="n", fill_value=0)
    pivot.plot(kind="bar", stacked=True, figsize=(10, 5))
    plt.ylabel("Prior-Medicaid person-month transitions")
    plt.tight_layout()
    plt.savefig(figdir / "transition_path_decomposition.png", dpi=150)
    plt.close()

    gaps = df.loc[df["medicaid_exit_it"] == 1, "months_uninsured_after_first_exit"].dropna()
    plt.figure(figsize=(7, 4))
    gaps.value_counts().sort_index().plot(kind="bar", color="#2f7d62")
    plt.xlabel("Months uninsured within exit month plus next three months")
    plt.ylabel("Medicaid exits")
    plt.tight_layout()
    plt.savefig(figdir / "uninsured_gap_duration.png", dpi=150)
    plt.close()


def go_no_go(sample: pd.DataFrame, counts: pd.DataFrame) -> str:
    event_count = int(sample["temporary_cross_up_1m"].sum())
    exits = int(sample.loc[sample["temporary_cross_up_1m"] == 1, "medicaid_exit_it"].sum())
    uninsured = int(sample.loc[sample["temporary_cross_up_1m"] == 1, "exit_to_uninsured_it"].sum())
    persons = int(sample["person_id"].nunique())
    decision = "go"
    reasons = []
    if persons < 5_000:
        decision = "no-go"
        reasons.append("primary analytic sample has fewer than 5,000 persons")
    if event_count < 250:
        decision = "no-go"
        reasons.append("temporary cross-up event support is below 250")
    if exits < 50:
        decision = "no-go"
        reasons.append("Medicaid exits among temporary cross-up events are below 50")
    if uninsured < 25:
        decision = "conditional-go" if decision == "go" else decision
        reasons.append("exit-to-uninsured among cross-up events is thin")
    if not reasons:
        reasons.append("minimum event-support screens are met")
    text = textwrap.dedent(
        f"""\
        # Go/No-Go Decision

        ## Executive Decision

        `{decision.upper()}`

        ## Primary Adult-Boundary Support

        - Primary analytic persons: {persons:,}
        - Temporary cross-up events, return within 1 month: {event_count:,}
        - Medicaid exits among those cross-up events: {exits:,}
        - Exit-to-uninsured among those cross-up events: {uninsured:,}

        ## Reasons

        {chr(10).join(f"- {r}" for r in reasons)}

        ## Rule

        If the adult-boundary design is `NO-GO`, backup 1 is pre-2024 child continuous eligibility. If `CONDITIONAL-GO`, conventional models may be run, but causal ML remains off unless conventional results are credible and stable.
        """
    )
    (ROOT / "report" / "08_go_no_go_decision.md").write_text(text, encoding="utf-8")
    return decision


def weighted_lpm(df: pd.DataFrame, outcome: str, treatments: list[str], controls: list[str], fe: list[str], weight: str = "weight") -> pd.DataFrame:
    needed = [outcome, weight] + treatments + controls + fe
    d = df[[c for c in needed if c in df.columns]].copy()
    d = d.replace([np.inf, -np.inf], np.nan).dropna(subset=[outcome] + treatments)
    if len(d) < 100 or d[outcome].sum() < 5:
        return pd.DataFrame(
            [{"outcome": outcome, "term": t, "estimate": np.nan, "std_error": np.nan, "p_value": np.nan, "n": len(d), "events": float(d[outcome].sum()) if outcome in d else 0, "status": "insufficient_support"} for t in treatments]
        )
    y = pd.to_numeric(d[outcome], errors="coerce").astype(float).to_numpy()
    w = pd.to_numeric(d.get(weight), errors="coerce").fillna(1.0).astype(float)
    w = np.where(np.isfinite(w) & (w > 0), w, 1.0)
    w = w / np.nanmean(w)
    x_parts = []
    names = []
    for c in treatments + controls:
        if c not in d:
            continue
        s = pd.to_numeric(d[c], errors="coerce").fillna(0.0).astype(float)
        x_parts.append(s.to_numpy().reshape(-1, 1))
        names.append(c)
    for c in fe:
        if c not in d:
            continue
        dum = pd.get_dummies(d[c].astype("string"), prefix=c, drop_first=True, dtype=float)
        if dum.shape[1] > 0:
            x_parts.append(dum.to_numpy())
            names.extend(dum.columns.tolist())
    X = np.column_stack([np.ones(len(d))] + x_parts)
    names = ["Intercept"] + names
    sw = np.sqrt(w)
    Xw = X * sw[:, None]
    yw = y * sw
    try:
        beta, *_ = np.linalg.lstsq(Xw, yw, rcond=None)
        resid = y - X @ beta
        bread = np.linalg.pinv(X.T @ (w[:, None] * X))
        meat = X.T @ (((w * resid) ** 2)[:, None] * X)
        vcov = bread @ meat @ bread
        se = np.sqrt(np.maximum(np.diag(vcov), 0))
    except Exception as exc:
        return pd.DataFrame(
            [{"outcome": outcome, "term": t, "estimate": np.nan, "std_error": np.nan, "p_value": np.nan, "n": len(d), "events": float(np.nansum(y)), "status": f"model_failed:{type(exc).__name__}"} for t in treatments]
        )
    rows = []
    from scipy import stats

    for t in treatments:
        if t in names:
            idx = names.index(t)
            z = beta[idx] / se[idx] if se[idx] > 0 else np.nan
            p = 2 * (1 - stats.norm.cdf(abs(z))) if np.isfinite(z) else np.nan
            rows.append(
                {
                    "outcome": outcome,
                    "term": t,
                    "estimate": beta[idx],
                    "std_error": se[idx],
                    "p_value": p,
                    "n": len(d),
                    "events": float(np.nansum(y)),
                    "status": "estimated",
                }
            )
        else:
            rows.append({"outcome": outcome, "term": t, "estimate": np.nan, "std_error": np.nan, "p_value": np.nan, "n": len(d), "events": float(np.nansum(y)), "status": "term_not_in_design"})
    return pd.DataFrame(rows)


def causal_models(ctx: RunContext | None = None) -> None:
    ensure_structure()
    path = ROOT / "data" / "analysis_ready" / "exposure_temporary_crossing_panel.parquet"
    if not path.exists():
        descriptive_audit()
    df = pd.read_parquet(path)
    sample = analysis_sample(df, primary=True, expansion_only=True)
    sample["temporary_cross_up_1m_x_phe"] = sample["temporary_cross_up_1m"] * sample["phe_continuous_enrollment_regime"].fillna(0)
    sample["temporary_cross_up_1m_x_unwinding"] = sample["temporary_cross_up_1m"] * sample["early_unwinding_regime"].fillna(0)
    treatments = ["temporary_cross_up_1m", "temporary_cross_up_1m_x_phe", "temporary_cross_up_1m_x_unwinding"]
    controls = ["income_poverty_ratio", "age", "program_stack_i0", "health_need_i0", "household_instability_i0", "prior_churn_i0"]
    fe = ["state_fips", "reference_year", "reference_month"]
    outcomes = ["medicaid_exit_it", "exit_to_uninsured_it", "exit_to_direct_purchase_exchange_it", "persistent_uninsured_2m", "persistent_uninsured_3m"]
    rows = []
    for h in [0, 1, 2, 3]:
        d = sample.copy()
        for out in outcomes:
            outcome_col = out if h == 0 else f"{out}_h{h}"
            if h > 0:
                d[outcome_col] = d.groupby("person_id")[out].shift(-h)
            res = weighted_lpm(d, outcome_col, treatments, controls, fe)
            res["horizon_months"] = h
            res["model_family"] = "weighted_lpm_discrete_time_hazard"
            rows.append(res)
    main = pd.concat(rows, ignore_index=True)
    main.to_csv(ROOT / "result" / "tables" / "main_hazard_results.csv", index=False)
    main.to_csv(ROOT / "result" / "models" / "main_hazard_results_long.csv", index=False)
    event_study(sample)
    main_results_memo(main, sample)
    log("causal models complete")


def event_study(sample: pd.DataFrame) -> None:
    first_event = (
        sample.loc[sample["temporary_cross_up_1m"] == 1, ["person_id", "reference_date"]]
        .sort_values(["person_id", "reference_date"])
        .drop_duplicates("person_id")
        .rename(columns={"reference_date": "event_date"})
    )
    ev = sample.merge(first_event, on="person_id", how="inner")
    ev["event_time"] = month_diff(ev["reference_date"], ev["event_date"])
    ev = ev[ev["event_time"].between(-3, 3)]
    rows = []
    for outcome in ["medicaid_exit_it", "uninsured_it", "private_coverage_it", "direct_purchase_or_marketplace_it"]:
        for et, g in ev.groupby("event_time"):
            rows.append(
                {
                    "event_time": int(et),
                    "outcome": outcome,
                    "mean": float(pd.to_numeric(g[outcome], errors="coerce").mean()),
                    "n": len(g),
                    "events": float(pd.to_numeric(g[outcome], errors="coerce").sum()),
                    "note": "crossers only; descriptive event profile, not a causal event study",
                }
            )
    out = pd.DataFrame(rows)
    out.to_csv(ROOT / "result" / "tables" / "event_study_results.csv", index=False)
    import matplotlib.pyplot as plt

    for outcome, filename in [
        ("medicaid_exit_it", "event_study_medicaid_exit.png"),
        ("uninsured_it", "event_study_exit_to_uninsured.png"),
    ]:
        d = out[out["outcome"] == outcome]
        plt.figure(figsize=(7, 4))
        plt.plot(d["event_time"], d["mean"], marker="o", color="#3f6f5f")
        plt.axvline(0, color="#b03a2e", linestyle="--")
        plt.xlabel("Months relative to first temporary cross-up")
        plt.ylabel("Mean")
        plt.tight_layout()
        plt.savefig(ROOT / "result" / "figures" / filename, dpi=150)
        plt.close()


def main_results_memo(main: pd.DataFrame, sample: pd.DataFrame) -> None:
    est = main[(main["status"] == "estimated") & (main["term"] == "temporary_cross_up_1m")]
    lines = []
    for _, r in est.head(20).iterrows():
        lines.append(
            f"- {r['outcome']} h={int(r['horizon_months'])}: beta={r['estimate']:.5f}, se={r['std_error']:.5f}, p={r['p_value']:.3f}, n={int(r['n']):,}, events={r['events']:.0f}"
        )
    (ROOT / "report" / "06_main_results_memo.md").write_text(
        textwrap.dedent(
            f"""\
            # Main Results Memo

            ## Analytic Sample

            Primary sample: expansion-state adults age 19-64, no Medicare, not flagged SSI/disability/non-MAGI proxy, valid family income-to-poverty ratio, and in the 1.00-1.75 ratio-unit near-boundary window (100-175% FPL).

            - Rows: {len(sample):,}
            - Persons: {sample['person_id'].nunique():,}
            - Temporary cross-up 1-month events: {int(sample['temporary_cross_up_1m'].sum()):,}
            - Medicaid exits: {int(sample['medicaid_exit_it'].sum()):,}
            - Exit to uninsured: {int(sample['exit_to_uninsured_it'].sum()):,}

            ## Conventional Hazard Model

            Weighted linear probability models include state, reference-year, and month fixed effects, plus baseline controls. `statsmodels` is not installed, so robust standard errors are computed directly.

            {chr(10).join(lines) if lines else "- No estimable primary treatment coefficients."}

            ## Interpretation Boundary

            These are transparent conventional specifications, not proof of causal effects. Event-study outputs are descriptive crossers-only profiles unless and until a credible matched control/event design is established.
            """
        ),
        encoding="utf-8",
    )


def sensitivity(ctx: RunContext | None = None) -> None:
    ensure_structure()
    df = pd.read_parquet(ROOT / "data" / "analysis_ready" / "exposure_temporary_crossing_panel.parquet")
    rows = []
    for expansion_only in [True, False]:
        base = analysis_sample(df, primary=False, expansion_only=expansion_only)
        base = base[(base["age"].between(19, 64)) & (base["medicare_it"] != 1)]
        for threshold in [1.00, 1.33, 1.38, 1.50, 2.50]:
            for lo, hi in [(0.75, 2.00), (1.00, 1.75), (1.00, 2.00), (1.25, 1.75)]:
                d = base[base["income_poverty_ratio"].between(lo, hi)].copy()
                d["cross_spec"] = ((d["adjacent_lag1"] == 1) & (d["income_poverty_ratio_lag1"] <= threshold) & (d["income_poverty_ratio"] > threshold)).astype("Int8")
                for outcome in ["medicaid_exit_it", "exit_to_uninsured_it", "persistent_uninsured_2m"]:
                    res = weighted_lpm(d, outcome, ["cross_spec"], ["income_poverty_ratio", "age"], ["state_fips", "reference_year", "reference_month"])
                    r = res.iloc[0].to_dict()
                    r.update({"threshold": threshold, "window_low": lo, "window_high": hi, "expansion_only": expansion_only, "outcome": outcome, "cross_events": int(d["cross_spec"].sum())})
                    rows.append(r)
    sens = pd.DataFrame(rows)
    sens.to_csv(ROOT / "result" / "tables" / "sensitivity_summary.csv", index=False)
    log("sensitivity complete")


def causal_ml_audit(ctx: RunContext | None = None) -> None:
    ensure_structure()
    go = read_text_if_exists(ROOT / "report" / "08_go_no_go_decision.md")
    main = pd.read_csv(ROOT / "result" / "tables" / "main_hazard_results.csv") if (ROOT / "result" / "tables" / "main_hazard_results.csv").exists() else pd.DataFrame()
    estimated = main[main.get("status", pd.Series(dtype=str)) == "estimated"] if not main.empty else pd.DataFrame()
    decision_match = re.search(r"## Executive Decision\s+`([^`]+)`", go, flags=re.S)
    decision_raw = decision_match.group(1).strip().upper() if decision_match else ""
    credible = decision_raw == "GO" and not estimated.empty and int(estimated["events"].max()) >= 100
    if not credible:
        text = "Causal ML is not justified as a main contribution. The paper should be positioned as a conventional mechanism-oriented SIPP audit or, if support is weak, as a no-go/backup-design memo."
        (ROOT / "report" / "07_causal_ml_audit.md").write_text(
            textwrap.dedent(
                f"""\
                # Causal ML Audit

                ## Decision

                Not run.

                ## Reason

                {text}

                Causal ML was conditional on credible conventional variation, adequate event counts, overlap, stable CATE ranking, and out-of-sample policy value beyond simple rules. The current run does not clear that bar automatically.
                """
            ),
            encoding="utf-8",
        )
        return
    (ROOT / "report" / "07_causal_ml_audit.md").write_text(
        "# Causal ML Audit\n\nNot run automatically. Conventional support exists, but causal ML requires a separate preregistered validation step.\n",
        encoding="utf-8",
    )


def final_memo(ctx: RunContext | None = None) -> None:
    ensure_structure()
    paths = {
        "go": ROOT / "report" / "08_go_no_go_decision.md",
        "main": ROOT / "report" / "06_main_results_memo.md",
        "ml": ROOT / "report" / "07_causal_ml_audit.md",
    }
    go = read_text_if_exists(paths["go"])
    main = read_text_if_exists(paths["main"])
    ml = read_text_if_exists(paths["ml"])
    decision_match = re.search(r"## Executive Decision\s+`([^`]+)`", go, flags=re.S)
    decision_raw = decision_match.group(1).strip().upper() if decision_match else "UNDETERMINED"
    decision = decision_raw.replace("-", " ").lower()
    ml_decision_match = re.search(r"## Decision\s+([^\n]+)", ml, flags=re.S)
    ml_decision = ml_decision_match.group(1).strip() if ml_decision_match else "See report/07_causal_ml_audit.md."
    sample_counts = pd.read_csv(ROOT / "result" / "tables" / "sample_counts_by_year_regime.csv") if (ROOT / "result" / "tables" / "sample_counts_by_year_regime.csv").exists() else pd.DataFrame()
    final = textwrap.dedent(
        f"""\
        # Final Research Memo

        ## 1. Executive Verdict

        {decision.upper()}.

        The adult-boundary topic has been implemented as a full reproducible audit. The publishable claim depends on the support and robustness summarized in `report/08_go_no_go_decision.md`, `report/06_main_results_memo.md`, and `result/tables/sensitivity_summary.csv`.

        ## 2. Adult-Boundary Topic

        The project tests temporary family-income crossings above 138% FPL (`TFINCPOV = 1.38`) among near-boundary adults in expansion states. The design is not assumed causal; it is audited through event support, regime contrasts, hazard models, descriptive event profiles, and robustness checks.

        ## 3. Sample And Years

        SIPP file years 2018-2024 are mapped to reference years 2017-2023. The primary sample is adults age 19-64, not Medicare-covered, not SSI/disability flagged for the primary MAGI sample, in expansion-state months, and near 100-175% FPL.

        ## 4. Coverage Construction

        Medicaid uses `EMDMTH` as primary and `RPUBTYPE2` as sensitivity. Uninsured uses `RHLTHMTH == 2`; private uses `RPRIMTH`; direct-purchase/exchange uses `RPRITYPE2`, `RMARKTPLACE`, and exchange/subsidy variables.

        ## 5. Temporary Eligibility Shocks

        Primary exposure is a cross-up from `TFINCPOV <= 1.38` to `> 1.38` that returns below threshold within one month. Two- and three-month return windows, sustained crossings, alternative thresholds, and alternative bandwidths are reported.

        ## 6. Main Descriptive Facts

        See:

        - `result/tables/sample_counts_by_year_regime.csv`
        - `result/tables/temporary_crossing_counts_by_year_regime.csv`
        - `result/tables/coverage_transition_matrix_by_year.csv`
        - `result/figures/transition_path_decomposition.png`

        ## 7. Causal Estimates

        Main transparent hazard estimates are in `result/tables/main_hazard_results.csv`. Event-study profiles are descriptive and stored in `result/tables/event_study_results.csv`.

        ## 8. Robustness And Failed Specifications

        Robustness and placebo-threshold variants are stored in `result/tables/sensitivity_summary.csv`. Specifications with insufficient support are retained with `status=insufficient_support`.

        ## 9. Causal ML

        {ml_decision}

        Causal ML is not used as a headline unless conventional identification and support pass. This run writes the audit and avoids decorative ML.

        ## 10. Backup Recommendation

        If the adult-boundary result is `NO-GO`, the recommended backup is pre-2024 child continuous eligibility, with state-year policy verification before modeling. Early unwinding administrative burden is only an exploratory backup unless state-month burden metrics can be validated against individual transition timing.

        ## 11. Next Steps For Paper Writing

        - Use `report/06_main_results_memo.md` and `report/08_go_no_go_decision.md` as the decision core.
        - If conditional/go, write the paper as a mechanism-oriented SIPP coverage-transition paper with strong caveats.
        - If no-go, preserve this as a transparent failed adult-boundary audit and pivot to backup 1.
        """
    )
    (ROOT / "report" / "09_final_research_memo.md").write_text(final, encoding="utf-8")
    verify_artifacts()
    log("final memo complete")


def verify_artifacts() -> None:
    required = [
        "report/00_project_readme.md",
        "report/01_source_reading_memo.md",
        "report/02_metadata_audit.md",
        "report/03_data_build_audit.md",
        "report/04_variable_construction_memo.md",
        "report/05_empirical_design_memo.md",
        "report/06_main_results_memo.md",
        "report/07_causal_ml_audit.md",
        "report/08_go_no_go_decision.md",
        "report/09_final_research_memo.md",
        "data/metadata/variable_registry.csv",
        "data/metadata/concept_crosswalk_initial.csv",
        "data/analysis_ready/sipp_2018_2024_person_month_panel.parquet",
        "data/analysis_ready/coverage_transition_panel.parquet",
        "data/analysis_ready/exposure_temporary_crossing_panel.parquet",
        "data/policy/state_month_policy_regime.csv",
        "data/policy/medicaid_expansion_state_month.csv",
        "result/tables/sample_counts_by_year_regime.csv",
        "result/tables/temporary_crossing_counts_by_year_regime.csv",
        "result/tables/coverage_transition_matrix_by_year.csv",
        "result/tables/main_hazard_results.csv",
        "result/tables/event_study_results.csv",
        "result/tables/sensitivity_summary.csv",
        "result/figures/income_crossing_distribution.png",
        "result/figures/transition_path_decomposition.png",
        "result/figures/event_study_medicaid_exit.png",
        "result/figures/event_study_exit_to_uninsured.png",
        "result/figures/uninsured_gap_duration.png",
    ]
    rows = []
    for r in required:
        p = ROOT / r
        rows.append({"path": r, "exists": p.exists(), "bytes": p.stat().st_size if p.exists() else 0})
    pd.DataFrame(rows).to_csv(ROOT / "result" / "diagnostics" / "required_artifact_check.csv", index=False)


def run_all() -> None:
    ensure_structure()
    write_source_memos()
    metadata_audit()
    build_panel()
    construct_variables()
    descriptive_audit()
    causal_models()
    sensitivity()
    causal_ml_audit()
    final_memo()
