from __future__ import annotations

import csv
import importlib.util
import platform
import subprocess
import sys
from collections import Counter
from importlib import metadata
from pathlib import Path
from typing import Any

from common import REPORT_DIR, RESULT_DIR, TEMP_DIR, append_log, ensure_dirs, write_csv


INVENTORY_PATH = TEMP_DIR / "python_package_inventory.csv"
FREEZE_PATH = TEMP_DIR / "python_package_freeze.txt"
AUDIT_PATH = RESULT_DIR / "python_environment_audit.csv"
SUMMARY_PATH = RESULT_DIR / "python_environment_summary.csv"
REPORT_PATH = REPORT_DIR / "reproducibility_environment.md"

PACKAGE_COLUMNS = [
    "package",
    "import_name",
    "role",
    "requirement_level",
    "installed",
    "version",
    "import_check",
    "notes",
]

AUDIT_COLUMNS = ["check", "status", "evidence", "gap"]
SUMMARY_COLUMNS = ["metric", "value", "interpretation"]

PACKAGES = [
    {
        "package": "requests",
        "import_name": "requests",
        "role": "source inventory, source probes, documentation snapshots, NASA POWER fallback calls",
        "requirement_level": "required_for_metadata_pipeline",
    },
    {
        "package": "beautifulsoup4",
        "import_name": "bs4",
        "role": "HTML parsing for public source and metadata pages",
        "requirement_level": "required_for_metadata_pipeline",
    },
    {
        "package": "pandas",
        "import_name": "pandas",
        "role": "raw schema summaries, harmonization, outcomes, diagnostics, modeling inputs",
        "requirement_level": "required_for_empirical_pipeline",
    },
    {
        "package": "numpy",
        "import_name": "numpy",
        "role": "predictive and reduced-form model utilities",
        "requirement_level": "required_for_empirical_pipeline",
    },
    {
        "package": "python-dateutil",
        "import_name": "dateutil",
        "role": "climate exposure lag windows",
        "requirement_level": "required_for_climate_fallback",
    },
    {
        "package": "pyreadstat",
        "import_name": "pyreadstat",
        "role": "Stata/SPSS/SAS raw microdata schema and value-label inspection",
        "requirement_level": "required_after_raw_download_for_dta_sav_sas",
    },
    {
        "package": "openpyxl",
        "import_name": "openpyxl",
        "role": "Excel raw/documentation file inspection through pandas",
        "requirement_level": "recommended_after_raw_download",
    },
    {
        "package": "xlrd",
        "import_name": "xlrd",
        "role": "Legacy .xls questionnaire inspection for older public survey documentation",
        "requirement_level": "recommended_after_raw_download",
    },
    {
        "package": "pyarrow",
        "import_name": "pyarrow",
        "role": "Parquet/Feather raw or clean output support",
        "requirement_level": "recommended_after_raw_download",
    },
    {
        "package": "duckdb",
        "import_name": "duckdb",
        "role": "large tabular data exploration and joins",
        "requirement_level": "optional_scaling",
    },
    {
        "package": "polars",
        "import_name": "polars",
        "role": "large tabular data exploration and joins",
        "requirement_level": "optional_scaling",
    },
    {
        "package": "geopandas",
        "import_name": "geopandas",
        "role": "admin boundary linkage and geospatial validation",
        "requirement_level": "recommended_for_admin_climate_linkage",
    },
    {
        "package": "shapely",
        "import_name": "shapely",
        "role": "geometry operations for admin climate linkage",
        "requirement_level": "recommended_for_admin_climate_linkage",
    },
    {
        "package": "xarray",
        "import_name": "xarray",
        "role": "gridded climate data handling",
        "requirement_level": "recommended_for_chirps_era5_terraclimate",
    },
    {
        "package": "rasterio",
        "import_name": "rasterio",
        "role": "raster climate/geospatial extraction",
        "requirement_level": "recommended_for_chirps_era5_terraclimate",
    },
    {
        "package": "rioxarray",
        "import_name": "rioxarray",
        "role": "xarray/raster geospatial climate extraction",
        "requirement_level": "recommended_for_chirps_era5_terraclimate",
    },
    {
        "package": "netCDF4",
        "import_name": "netCDF4",
        "role": "NetCDF climate data support",
        "requirement_level": "recommended_for_era5_terraclimate",
    },
    {
        "package": "cdsapi",
        "import_name": "cdsapi",
        "role": "Copernicus ERA5-Land download API",
        "requirement_level": "optional_for_era5_download",
    },
    {
        "package": "scikit-learn",
        "import_name": "sklearn",
        "role": "predictive ML models, splits, and metrics",
        "requirement_level": "required_after_outcomes_for_predictive_ml",
    },
    {
        "package": "statsmodels",
        "import_name": "statsmodels",
        "role": "reduced-form regression and robust inference helpers",
        "requirement_level": "recommended_for_reduced_form",
    },
    {
        "package": "xgboost",
        "import_name": "xgboost",
        "role": "candidate gradient-boosting model",
        "requirement_level": "optional_predictive_ml",
    },
    {
        "package": "lightgbm",
        "import_name": "lightgbm",
        "role": "candidate gradient-boosting model",
        "requirement_level": "optional_predictive_ml",
    },
    {
        "package": "catboost",
        "import_name": "catboost",
        "role": "candidate gradient-boosting model",
        "requirement_level": "optional_predictive_ml",
    },
    {
        "package": "shap",
        "import_name": "shap",
        "role": "prediction explanation only, not causal interpretation",
        "requirement_level": "optional_prediction_explanation",
    },
    {
        "package": "econml",
        "import_name": "econml",
        "role": "causal ML estimators after identification gate",
        "requirement_level": "optional_causal_ml_after_identification",
    },
    {
        "package": "doubleml",
        "import_name": "doubleml",
        "role": "double/debiased ML after identification gate",
        "requirement_level": "optional_causal_ml_after_identification",
    },
    {
        "package": "causalml",
        "import_name": "causalml",
        "role": "causal ML estimators after identification gate",
        "requirement_level": "optional_causal_ml_after_identification",
    },
]


def dist_version(package: str) -> str:
    try:
        return metadata.version(package)
    except metadata.PackageNotFoundError:
        return ""


def package_row(spec: dict[str, str]) -> dict[str, str]:
    import_name = spec["import_name"]
    found = importlib.util.find_spec(import_name) is not None
    version = dist_version(spec["package"])
    if not version and spec["package"] != import_name:
        version = dist_version(import_name)
    return {
        "package": spec["package"],
        "import_name": import_name,
        "role": spec["role"],
        "requirement_level": spec["requirement_level"],
        "installed": "1" if found else "0",
        "version": version,
        "import_check": "importable" if found else "missing",
        "notes": "optional package; absence is not a current failure" if spec["requirement_level"].startswith("optional") else "",
    }


def write_freeze() -> tuple[str, str]:
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "freeze"],
            check=False,
            text=True,
            capture_output=True,
            timeout=60,
        )
    except Exception as exc:  # pragma: no cover - defensive runtime logging
        FREEZE_PATH.write_text(f"pip freeze failed: {exc}\n", encoding="utf-8")
        return "failed", str(exc)
    output = result.stdout if result.returncode == 0 else result.stderr
    FREEZE_PATH.write_text(output, encoding="utf-8")
    return ("complete" if result.returncode == 0 else "failed", f"returncode={result.returncode}; bytes={len(output.encode('utf-8', errors='replace'))}")


def audit_rows(package_rows: list[dict[str, str]], freeze_status: str, freeze_evidence: str) -> list[dict[str, str]]:
    required_metadata = [row for row in package_rows if row["requirement_level"] == "required_for_metadata_pipeline"]
    required_empirical = [
        row
        for row in package_rows
        if row["requirement_level"]
        in {
            "required_for_empirical_pipeline",
            "required_for_climate_fallback",
            "required_after_raw_download_for_dta_sav_sas",
            "required_after_outcomes_for_predictive_ml",
        }
    ]
    metadata_missing = [row["package"] for row in required_metadata if row["installed"] != "1"]
    empirical_missing = [row["package"] for row in required_empirical if row["installed"] != "1"]
    rows = [
        {
            "check": "python_runtime",
            "status": "complete",
            "evidence": f"python={sys.version.split()[0]}; executable={sys.executable}; platform={platform.platform()}",
            "gap": "",
        },
        {
            "check": "metadata_pipeline_required_packages",
            "status": "complete" if not metadata_missing else "incomplete",
            "evidence": "missing=" + ";".join(metadata_missing) if metadata_missing else f"required metadata packages importable={len(required_metadata)}",
            "gap": "" if not metadata_missing else "Install missing metadata-pipeline packages before rerunning source acquisition.",
        },
        {
            "check": "post_raw_empirical_required_packages",
            "status": "complete" if not empirical_missing else "incomplete",
            "evidence": "missing=" + ";".join(empirical_missing) if empirical_missing else f"post-raw empirical required packages importable={len(required_empirical)}",
            "gap": "" if not empirical_missing else "Install missing packages before raw schema inspection, climate extraction, prediction, or modeling.",
        },
        {
            "check": "pip_freeze_snapshot",
            "status": freeze_status,
            "evidence": freeze_evidence,
            "gap": "" if freeze_status == "complete" else "pip freeze could not be recorded.",
        },
    ]
    return rows


def summary_rows(package_rows: list[dict[str, str]], audits: list[dict[str, str]]) -> list[dict[str, str]]:
    install_counts = Counter("installed" if row["installed"] == "1" else "missing" for row in package_rows)
    level_counts = Counter(row["requirement_level"] for row in package_rows)
    audit_counts = Counter(row["status"] for row in audits)
    rows = [
        {"metric": "python_version", "value": sys.version.split()[0], "interpretation": "Python runtime used for the audit."},
        {"metric": "package_rows", "value": str(len(package_rows)), "interpretation": "Tracked packages/imports relevant to the objective and current scripts."},
        {"metric": "packages_installed", "value": str(install_counts.get("installed", 0)), "interpretation": "Tracked packages importable in this environment."},
        {"metric": "packages_missing", "value": str(install_counts.get("missing", 0)), "interpretation": "Tracked packages not importable; optional missing packages are planning gaps only."},
    ]
    for level, count in sorted(level_counts.items()):
        rows.append({"metric": f"requirement_level_{level}", "value": str(count), "interpretation": "Tracked package requirement level count."})
    for status, count in sorted(audit_counts.items()):
        rows.append({"metric": f"environment_audit_status_{status}", "value": str(count), "interpretation": "Environment audit status count."})
    return rows


def markdown_count_table(counter: Counter[str], label: str) -> str:
    lines = [f"| {label} | Count |", "|---|---:|"]
    for key, count in counter.most_common():
        lines.append(f"| {key or 'blank'} | {count} |")
    return "\n".join(lines)


def markdown_rows(rows: list[dict[str, str]], columns: list[str], limit: int = 30) -> str:
    lines = ["| " + " | ".join(columns) + " |", "|" + "|".join("---" for _ in columns) + "|"]
    for row in rows[:limit]:
        values = []
        for column in columns:
            value = str(row.get(column, "")).replace("|", "/")
            if len(value) > 120:
                value = value[:117] + "..."
            values.append(value)
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines)


def write_report(package_rows: list[dict[str, str]], audits: list[dict[str, str]], summaries: list[dict[str, str]]) -> None:
    install_counts = Counter("installed" if row["installed"] == "1" else "missing" for row in package_rows)
    level_counts = Counter(row["requirement_level"] for row in package_rows)
    audit_counts = Counter(row["status"] for row in audits)
    missing_rows = [row for row in package_rows if row["installed"] != "1"]
    lines = [
        "# Reproducibility Environment",
        "",
        "Status: Python runtime and package availability have been audited. Missing optional causal/geospatial/ML packages are planning gaps, not evidence that the metadata pipeline is invalid.",
        "",
        "## Runtime",
        "",
        f"- Python: `{sys.version.split()[0]}`",
        f"- Executable: `{sys.executable}`",
        f"- Platform: `{platform.platform()}`",
        "",
        "## Package Availability",
        "",
        markdown_count_table(install_counts, "Package import status"),
        "",
        "## Requirement Levels",
        "",
        markdown_count_table(level_counts, "Requirement level"),
        "",
        "## Audit Status",
        "",
        markdown_count_table(audit_counts, "Audit status"),
        "",
        "## Missing Tracked Packages",
        "",
        markdown_rows(missing_rows, ["package", "import_name", "requirement_level", "role"], 40) if missing_rows else "All tracked packages are importable.",
        "",
        "## Machine-Readable Outputs",
        "",
        "- `temp/python_package_inventory.csv`",
        "- `temp/python_package_freeze.txt`",
        "- `result/python_environment_audit.csv`",
        "- `result/python_environment_summary.csv`",
        "",
        "## Guardrail",
        "",
        "This audit documents runtime readiness only. It does not bypass the raw-microdata gate, and it does not justify estimating outcomes, predictive models, reduced-form models, causal ML, or policy simulations before analytical data exist.",
    ]
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    ensure_dirs()
    package_rows = [package_row(spec) for spec in PACKAGES]
    freeze_status, freeze_evidence = write_freeze()
    audits = audit_rows(package_rows, freeze_status, freeze_evidence)
    summaries = summary_rows(package_rows, audits)
    write_csv(INVENTORY_PATH, package_rows, PACKAGE_COLUMNS)
    write_csv(AUDIT_PATH, audits, AUDIT_COLUMNS)
    write_csv(SUMMARY_PATH, summaries, SUMMARY_COLUMNS)
    write_report(package_rows, audits, summaries)
    missing_required = sum(1 for row in audits if row["status"] != "complete")
    append_log(TEMP_DIR / "audit_log.md", f"Python environment audit package_rows={len(package_rows)} incomplete_checks={missing_required}.")
    print(f"Python environment audit package_rows={len(package_rows)} incomplete_checks={missing_required}.")


if __name__ == "__main__":
    main()
