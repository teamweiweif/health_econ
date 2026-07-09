from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from pathlib import Path
from typing import Any

import pandas as pd

from common import DATA_DIR, TEMP_DIR, append_log, ensure_dirs, write_csv


PROJECT_ROOT = TEMP_DIR.parent
RAW_SCHEMA_DIR = TEMP_DIR / "raw_schema_inventory"
RAW_DOWNLOAD_DIR = TEMP_DIR / "raw_downloads"
RAW_EXTRACT_DIR = TEMP_DIR / "raw_extracted"
RECIPE_PATH = TEMP_DIR / "harmonization_recipe.csv"
RECIPE_TEMPLATE_PATH = TEMP_DIR / "harmonization_recipe_template.csv"
AUDIT_PATH = TEMP_DIR / "harmonization_audit.csv"
LINEAGE_PATH = TEMP_DIR / "harmonized_lineage.csv"
OUTPUT_PATH = DATA_DIR / "harmonized_household.csv"

RECIPE_COLUMNS = [
    "country",
    "survey_name",
    "wave",
    "idno",
    "harmonized_variable",
    "source_path",
    "source_file",
    "raw_variable",
    "raw_label",
    "merge_level",
    "key_role",
    "required",
    "transformation",
    "unit",
    "recall_period",
    "quality_flag",
    "notes",
]

AUDIT_COLUMNS = [
    "phase",
    "status",
    "detail",
    "country",
    "survey_name",
    "wave",
    "idno",
    "input_path",
    "rows_input",
    "rows_output",
    "output_path",
    "required_action",
]

LINEAGE_COLUMNS = [
    "country",
    "survey_name",
    "wave",
    "idno",
    "harmonized_variable",
    "source_path",
    "raw_variable",
    "raw_label",
    "transformation",
    "unit",
    "recall_period",
    "merge_level",
    "key_role",
    "required",
    "quality_flag",
    "rows_nonmissing",
    "notes",
]

EXPECTED_HARMONIZED_COLUMNS = [
    "country",
    "survey_name",
    "wave",
    "survey_year",
    "survey_month",
    "interview_date",
    "hhid",
    "pid",
    "household_weight",
    "person_weight",
    "strata",
    "psu",
    "admin1",
    "admin2",
    "cluster_id",
    "latitude",
    "longitude",
    "geolocation_quality",
    "rural",
    "household_size",
    "children_under_5",
    "children_under_15",
    "elderly_60_plus",
    "elderly_65_plus",
    "hh_head_sex",
    "hh_head_age",
    "hh_head_education",
    "asset_index",
    "total_consumption",
    "total_income",
    "food_consumption",
    "nonfood_consumption",
    "oop_health_expenditure",
    "health_insurance",
    "illness_or_injury_need",
    "care_sought",
    "care_not_sought",
    "reason_not_sought_cost",
    "reason_not_sought_distance",
    "reason_not_sought_supply",
    "health_facility_distance",
    "coping_borrowed",
    "coping_sold_assets",
    "food_insecurity",
    "agriculture_livelihood",
    "employment_labor",
]

STRUCTURAL_KEYS = {"hhid", "pid", "cluster_id", "admin1", "admin2", "psu"}
CONTEXT_COLUMNS = ["country", "survey_name", "wave", "idno"]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build an audited harmonized household/person dataset from raw files and a recipe.")
    parser.add_argument("--recipe", type=Path, default=RECIPE_PATH, help="Harmonization recipe CSV.")
    parser.add_argument("--output", type=Path, default=OUTPUT_PATH, help="Output CSV path.")
    return parser.parse_args()


def read_csv_dicts(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def audit_row(
    phase: str,
    status: str,
    detail: str,
    *,
    country: str = "",
    survey_name: str = "",
    wave: str = "",
    idno: str = "",
    input_path: str = "",
    rows_input: Any = "",
    rows_output: Any = "",
    output_path: str = "",
    required_action: str = "",
) -> dict[str, Any]:
    return {
        "phase": phase,
        "status": status,
        "detail": detail,
        "country": country,
        "survey_name": survey_name,
        "wave": wave,
        "idno": idno,
        "input_path": input_path,
        "rows_input": rows_input,
        "rows_output": rows_output,
        "output_path": output_path,
        "required_action": required_action,
    }


def write_recipe_template() -> None:
    if RECIPE_TEMPLATE_PATH.exists():
        return
    required = {"country", "survey_name", "wave", "hhid"}
    recommended = {
        "survey_year",
        "survey_month",
        "household_weight",
        "admin1",
        "admin2",
        "cluster_id",
        "total_consumption",
        "oop_health_expenditure",
    }
    rows = []
    for name in EXPECTED_HARMONIZED_COLUMNS:
        context_only = name in {"country", "survey_name", "wave"}
        rows.append(
            {
                "country": "Exampleland",
                "survey_name": "Example household survey",
                "wave": "2021",
                "idno": "EXAMPLE_2021",
                "harmonized_variable": name,
                "source_path": "" if context_only else "temp/raw_downloads/example_household.dta",
                "source_file": "" if context_only else "example_household.dta",
                "raw_variable": "" if context_only else f"raw_{name}",
                "raw_label": "",
                "merge_level": "household" if name != "pid" else "person",
                "key_role": "base_key" if name in {"hhid", "pid"} else "",
                "required": "constant" if context_only else "yes" if name in required else "recommended" if name in recommended else "no",
                "transformation": "as_is",
                "unit": "",
                "recall_period": "",
                "quality_flag": "template_not_real",
                "notes": "Copy this file to temp/harmonization_recipe.csv and replace all example values with verified raw schema mappings.",
            }
        )
    write_csv(RECIPE_TEMPLATE_PATH, rows, RECIPE_COLUMNS)


def raw_file_rows() -> list[dict[str, str]]:
    rows = read_csv_dicts(RAW_SCHEMA_DIR / "raw_file_inventory.csv")
    return [row for row in rows if row.get("source_path") and row.get("status") != "failed"]


def has_physical_raw_files() -> bool:
    if not RAW_DOWNLOAD_DIR.exists():
        return False
    return any(path.is_file() and path.name.lower() != "readme.md" for path in RAW_DOWNLOAD_DIR.rglob("*"))


def is_required(value: str) -> bool:
    return str(value).strip().lower() in {"1", "true", "yes", "y", "required"}


def study_key(row: dict[str, str]) -> tuple[str, str, str, str]:
    return tuple((row.get(name) or "").strip() for name in CONTEXT_COLUMNS)  # type: ignore[return-value]


def split_sheet(source_path: str) -> tuple[str, str | None]:
    if "::" not in source_path:
        return source_path, None
    base, sheet = source_path.split("::", 1)
    return base, sheet or None


def resolve_source(source_path: str) -> tuple[Path | None, str | None]:
    base, sheet = split_sheet(source_path.strip())
    path = Path(base)
    candidates = []
    if path.is_absolute():
        candidates.append(path)
    else:
        candidates.extend(
            [
                PROJECT_ROOT / path,
                TEMP_DIR / path,
                RAW_DOWNLOAD_DIR / path.name,
                RAW_EXTRACT_DIR / path.name,
            ]
        )
    for candidate in candidates:
        if candidate.exists():
            return candidate, sheet
    for root in [RAW_DOWNLOAD_DIR, RAW_EXTRACT_DIR]:
        if root.exists():
            matches = list(root.rglob(path.name))
            if matches:
                return matches[0], sheet
    return None, sheet


def read_source_table(path: Path, sheet: str | None, columns: list[str]) -> pd.DataFrame:
    suffix = path.suffix.lower()
    wanted = [column for column in dict.fromkeys(columns) if column]
    wanted_set = set(wanted)
    if suffix in {".dta", ".sav", ".por", ".sas7bdat", ".xpt"}:
        try:
            import pyreadstat
        except Exception as exc:  # pragma: no cover - environment dependent
            raise RuntimeError(f"pyreadstat is required for {suffix}: {exc}") from exc
        readers = {
            ".dta": pyreadstat.read_dta,
            ".sav": pyreadstat.read_sav,
            ".por": pyreadstat.read_por,
            ".sas7bdat": pyreadstat.read_sas7bdat,
            ".xpt": pyreadstat.read_xport,
        }
        reader = readers[suffix]
        try:
            df, _ = reader(str(path), usecols=wanted)
        except TypeError:
            df, _ = reader(str(path))
        return df[[column for column in wanted if column in df.columns]]
    if suffix in {".csv", ".tsv", ".txt"}:
        sep = "\t" if suffix == ".tsv" else None if suffix == ".txt" else ","
        return pd.read_csv(
            path,
            sep=sep,
            engine="python",
            usecols=lambda column: str(column) in wanted_set,
            encoding_errors="replace",
        )
    if suffix in {".xlsx", ".xls"}:
        return pd.read_excel(path, sheet_name=sheet or 0, usecols=lambda column: str(column) in wanted_set)
    if suffix == ".parquet":
        return pd.read_parquet(path, columns=wanted)
    if suffix == ".feather":
        df = pd.read_feather(path)
        return df[[column for column in wanted if column in df.columns]]
    raise RuntimeError(f"unsupported raw format for harmonization: {suffix}")


def yes_no_series(series: pd.Series) -> pd.Series:
    lowered = series.astype(str).str.strip().str.lower()
    yes = lowered.isin(["1", "true", "yes", "y", "oui", "si"])
    no = lowered.isin(["0", "false", "no", "n", "non"])
    out = pd.Series(pd.NA, index=series.index, dtype="Int64")
    out[yes] = 1
    out[no] = 0
    return out


def transform_series(series: pd.Series, transformation: str) -> pd.Series:
    transform = (transformation or "as_is").strip().lower()
    if transform in {"", "as_is", "identity"}:
        return series
    if transform in {"numeric", "as_numeric"}:
        return pd.to_numeric(series, errors="coerce")
    if transform in {"string", "str"}:
        return series.astype("string")
    if transform in {"lower", "lowercase"}:
        return series.astype("string").str.lower()
    if transform in {"binary_yes_no", "yes_no", "indicator_yes"}:
        return yes_no_series(series)
    annualize = {
        "annualize_7day": 365.25 / 7,
        "annualize_2week": 365.25 / 14,
        "annualize_4week": 365.25 / 28,
        "annualize_30day": 365.25 / 30,
        "annualize_1month": 12,
        "annualize_month": 12,
        "annualize_quarter": 4,
    }
    if transform in annualize:
        return pd.to_numeric(series, errors="coerce") * annualize[transform]
    if transform.startswith("annualize_factor:"):
        factor = float(transform.split(":", 1)[1])
        return pd.to_numeric(series, errors="coerce") * factor
    raise RuntimeError(f"unsupported transformation '{transformation}'")


def active_recipe_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    active = []
    for row in rows:
        if not (row.get("source_path") or "").strip():
            continue
        if not (row.get("raw_variable") or "").strip():
            continue
        if not (row.get("harmonized_variable") or "").strip():
            continue
        active.append(row)
    return active


def key_columns(rows: list[dict[str, str]], columns: set[str]) -> list[str]:
    keys = []
    for row in rows:
        harmonized = (row.get("harmonized_variable") or "").strip()
        role = (row.get("key_role") or "").strip().lower()
        if harmonized in columns and (role or harmonized in {"hhid", "pid"}):
            keys.append(harmonized)
    if not keys:
        keys = [name for name in ["hhid", "pid", "cluster_id"] if name in columns]
    return list(dict.fromkeys(keys))


def build_source_table(source_path: str, rows: list[dict[str, str]]) -> tuple[pd.DataFrame | None, list[dict[str, Any]], dict[str, Any]]:
    audit: list[dict[str, Any]] = []
    resolved, sheet = resolve_source(source_path)
    context = {name: rows[0].get(name, "") for name in CONTEXT_COLUMNS}
    if resolved is None:
        audit.append(
            audit_row(
                "source_read",
                "failed_source_not_found",
                "Recipe source_path does not resolve to a raw or extracted file.",
                input_path=source_path,
                required_action="Correct source_path or rerun raw schema inspection after adding raw files.",
                **context,
            )
        )
        return None, audit, {"source_path": source_path, "rows_input": 0}
    raw_columns = [row.get("raw_variable", "").strip() for row in rows if row.get("raw_variable", "").strip()]
    try:
        raw_df = read_source_table(resolved, sheet, raw_columns)
    except Exception as exc:
        audit.append(
            audit_row(
                "source_read",
                "failed_read_error",
                str(exc),
                input_path=source_path,
                required_action="Inspect file format and recipe raw variables.",
                **context,
            )
        )
        return None, audit, {"source_path": source_path, "rows_input": 0}

    missing_required = [
        row.get("raw_variable", "").strip()
        for row in rows
        if is_required(row.get("required", "")) and row.get("raw_variable", "").strip() not in raw_df.columns
    ]
    if missing_required:
        audit.append(
            audit_row(
                "source_read",
                "failed_required_raw_variables_missing",
                ";".join(missing_required),
                input_path=source_path,
                rows_input=len(raw_df),
                required_action="Fix the recipe or raw file selection before harmonization.",
                **context,
            )
        )
        return None, audit, {"source_path": source_path, "rows_input": len(raw_df)}

    mapped: dict[str, pd.Series] = {}
    skipped_optional = []
    for row in rows:
        raw = row.get("raw_variable", "").strip()
        harmonized = row.get("harmonized_variable", "").strip()
        if not raw or not harmonized:
            continue
        if raw not in raw_df.columns:
            skipped_optional.append(raw)
            continue
        try:
            series = transform_series(raw_df[raw], row.get("transformation", "as_is"))
        except Exception as exc:
            if is_required(row.get("required", "")):
                audit.append(
                    audit_row(
                        "transformation",
                        "failed_required_transformation",
                        f"{harmonized} from {raw}: {exc}",
                        input_path=source_path,
                        rows_input=len(raw_df),
                        required_action="Fix transformation in temp/harmonization_recipe.csv.",
                        **context,
                    )
                )
                return None, audit, {"source_path": source_path, "rows_input": len(raw_df)}
            skipped_optional.append(raw)
            continue
        if harmonized in mapped:
            mapped[harmonized] = mapped[harmonized].combine_first(series)
        else:
            mapped[harmonized] = series

    if not mapped:
        audit.append(
            audit_row(
                "source_map",
                "failed_no_mapped_columns",
                "No recipe variables were available in this source.",
                input_path=source_path,
                rows_input=len(raw_df),
                required_action="Verify raw variable names against temp/raw_schema_inventory/raw_variable_catalog.csv.",
                **context,
            )
        )
        return None, audit, {"source_path": source_path, "rows_input": len(raw_df)}

    out = pd.DataFrame(mapped)
    for name in CONTEXT_COLUMNS:
        if context.get(name) and name not in out.columns:
            out[name] = context[name]

    status = "complete" if not skipped_optional else "complete_with_optional_missing"
    audit.append(
        audit_row(
            "source_map",
            status,
            f"Mapped {len(out.columns)} harmonized columns; optional missing raw variables={len(skipped_optional)}.",
            input_path=source_path,
            rows_input=len(raw_df),
            rows_output=len(out),
            **context,
        )
    )
    return out, audit, {"source_path": source_path, "rows_input": len(raw_df)}


def merge_study_tables(study_rows: list[dict[str, str]]) -> tuple[pd.DataFrame | None, list[dict[str, Any]]]:
    audit: list[dict[str, Any]] = []
    context = {name: study_rows[0].get(name, "") for name in CONTEXT_COLUMNS}
    by_source: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in study_rows:
        by_source[row.get("source_path", "").strip()].append(row)

    tables = []
    for source_path, rows in by_source.items():
        if not source_path:
            continue
        table, source_audit, meta = build_source_table(source_path, rows)
        audit.extend(source_audit)
        if table is not None:
            tables.append(
                {
                    "source_path": source_path,
                    "df": table,
                    "keys": key_columns(rows, set(table.columns)),
                    "rows_input": meta.get("rows_input", 0),
                    "base": any("base" in (row.get("key_role", "").lower()) or "root" in (row.get("key_role", "").lower()) for row in rows),
                }
            )
    if not tables:
        audit.append(
            audit_row(
                "study_build",
                "failed_no_readable_sources",
                "No source table could be read for this country-wave.",
                required_action="Add raw files and a verified harmonization recipe.",
                **context,
            )
        )
        return None, audit

    base_index = next((i for i, table in enumerate(tables) if table["base"]), 0)
    base = tables.pop(base_index)
    merged = base["df"].copy()
    audit.append(
        audit_row(
            "study_base",
            "complete",
            f"Selected base source {base['source_path']} with keys {','.join(base['keys'])}.",
            input_path=base["source_path"],
            rows_input=base["rows_input"],
            rows_output=len(merged),
            **context,
        )
    )

    for table in tables:
        right = table["df"]
        right_keys = [key for key in table["keys"] if key in right.columns and key in merged.columns]
        context_keys = [key for key in ["country", "survey_name", "wave", "idno"] if key in merged.columns and key in right.columns]
        structural = [key for key in right_keys if key in STRUCTURAL_KEYS]
        if not structural:
            audit.append(
                audit_row(
                    "study_merge",
                    "failed_no_explicit_structural_key",
                    f"Could not merge {table['source_path']} without a shared hhid, pid, cluster, admin, or psu key.",
                    input_path=table["source_path"],
                    rows_input=table["rows_input"],
                    rows_output=len(merged),
                    required_action="Mark merge keys in temp/harmonization_recipe.csv.",
                    **context,
                )
            )
            return None, audit
        merge_keys = list(dict.fromkeys(context_keys + structural))
        if right.duplicated(merge_keys).any():
            audit.append(
                audit_row(
                    "study_merge",
                    "failed_many_to_many_risk",
                    f"Right-hand source has duplicate merge keys: {','.join(merge_keys)}.",
                    input_path=table["source_path"],
                    rows_input=table["rows_input"],
                    rows_output=len(merged),
                    required_action="Aggregate person/item files first or include a more granular key such as pid.",
                    **context,
                )
            )
            return None, audit
        duplicates = [column for column in right.columns if column in merged.columns and column not in merge_keys]
        validate = "many_to_one" if merged.duplicated(merge_keys).any() else "one_to_one"
        try:
            merged_next = merged.merge(right, how="left", on=merge_keys, suffixes=("", "__right"), validate=validate)
        except Exception as exc:
            audit.append(
                audit_row(
                    "study_merge",
                    "failed_merge_error",
                    str(exc),
                    input_path=table["source_path"],
                    rows_input=table["rows_input"],
                    rows_output=len(merged),
                    required_action="Inspect merge keys and duplicate structure.",
                    **context,
                )
            )
            return None, audit
        for column in duplicates:
            right_column = f"{column}__right"
            if right_column in merged_next.columns:
                merged_next[column] = merged_next[column].combine_first(merged_next[right_column])
                merged_next = merged_next.drop(columns=[right_column])
        merged = merged_next
        audit.append(
            audit_row(
                "study_merge",
                "complete",
                f"Merged {table['source_path']} on {','.join(merge_keys)}.",
                input_path=table["source_path"],
                rows_input=table["rows_input"],
                rows_output=len(merged),
                **context,
            )
        )

    for name in CONTEXT_COLUMNS:
        if context.get(name) and name not in merged.columns:
            merged[name] = context[name]
    return merged, audit


def lineage_rows(recipe_rows: list[dict[str, str]], output: pd.DataFrame | None) -> list[dict[str, Any]]:
    rows = []
    for row in recipe_rows:
        harmonized = row.get("harmonized_variable", "").strip()
        nonmissing = ""
        if output is not None and harmonized in output.columns:
            nonmissing = int(output[harmonized].notna().sum())
        rows.append(
            {
                "country": row.get("country", ""),
                "survey_name": row.get("survey_name", ""),
                "wave": row.get("wave", ""),
                "idno": row.get("idno", ""),
                "harmonized_variable": harmonized,
                "source_path": row.get("source_path", ""),
                "raw_variable": row.get("raw_variable", ""),
                "raw_label": row.get("raw_label", ""),
                "transformation": row.get("transformation", ""),
                "unit": row.get("unit", ""),
                "recall_period": row.get("recall_period", ""),
                "merge_level": row.get("merge_level", ""),
                "key_role": row.get("key_role", ""),
                "required": row.get("required", ""),
                "quality_flag": row.get("quality_flag", ""),
                "rows_nonmissing": nonmissing,
                "notes": row.get("notes", ""),
            }
        )
    return rows


def write_blocked_audit(recipe: Path, output: Path, reason: str, detail: str, action: str) -> None:
    physical_raw = has_physical_raw_files()
    raw_rows = raw_file_rows()
    rows = [
        audit_row(
            "recipe_template",
            "complete",
            f"Template exists at {RECIPE_TEMPLATE_PATH}.",
            output_path=str(RECIPE_TEMPLATE_PATH.relative_to(PROJECT_ROOT)),
        ),
        audit_row(
            "raw_files",
            "complete" if raw_rows else reason,
            detail if not raw_rows else f"raw_file_inventory rows={len(raw_rows)}",
            input_path=str(RAW_SCHEMA_DIR / "raw_file_inventory.csv"),
            rows_input=len(raw_rows),
            required_action="" if raw_rows else action if not physical_raw else "Run python script/03_inspect_raw_schemas.py to refresh raw schema inventory.",
        ),
        audit_row(
            "harmonization_recipe",
            "complete" if recipe.exists() else "blocked_no_harmonization_recipe",
            f"Recipe path: {recipe}",
            input_path=str(recipe),
            required_action="" if recipe.exists() else "Copy temp/harmonization_recipe_template.csv to temp/harmonization_recipe.csv and replace example mappings with verified raw variables.",
        ),
        audit_row(
            "harmonized_output",
            reason,
            detail,
            output_path=str(output),
            required_action=action,
        ),
    ]
    write_csv(AUDIT_PATH, rows, AUDIT_COLUMNS)
    write_csv(LINEAGE_PATH, [], LINEAGE_COLUMNS)
    append_log(TEMP_DIR / "audit_log.md", f"Harmonization blocked: {reason} - {detail}")


def build_harmonized(recipe: Path, output: Path) -> None:
    write_recipe_template()
    raw_rows = raw_file_rows()
    if not raw_rows:
        write_blocked_audit(
            recipe,
            output,
            "blocked_no_raw_files",
            "No inspected tabular raw files are available.",
            "Place raw files in temp/raw_downloads and run python script/03_inspect_raw_schemas.py.",
        )
        print("Harmonization blocked: no inspected raw files.")
        return
    if not recipe.exists():
        write_blocked_audit(
            recipe,
            output,
            "blocked_no_harmonization_recipe",
            "No explicit raw-to-harmonized recipe exists.",
            "Create temp/harmonization_recipe.csv from the template and verified raw schema catalog.",
        )
        print("Harmonization blocked: no harmonization recipe.")
        return

    recipe_rows = active_recipe_rows(read_csv_dicts(recipe))
    if not recipe_rows:
        write_blocked_audit(
            recipe,
            output,
            "blocked_empty_harmonization_recipe",
            "The harmonization recipe has no active mappings.",
            "Add source_path, raw_variable, and harmonized_variable rows.",
        )
        print("Harmonization blocked: empty harmonization recipe.")
        return

    audit: list[dict[str, Any]] = [
        audit_row(
            "recipe_template",
            "complete",
            f"Template exists at {RECIPE_TEMPLATE_PATH}.",
            output_path=str(RECIPE_TEMPLATE_PATH.relative_to(PROJECT_ROOT)),
        ),
        audit_row(
            "harmonization_recipe",
            "complete",
            f"Active mapping rows={len(recipe_rows)}.",
            input_path=str(recipe),
            rows_input=len(recipe_rows),
        ),
    ]
    frames = []
    by_study: dict[tuple[str, str, str, str], list[dict[str, str]]] = defaultdict(list)
    for row in recipe_rows:
        by_study[study_key(row)].append(row)

    for rows in by_study.values():
        frame, study_audit = merge_study_tables(rows)
        audit.extend(study_audit)
        if frame is not None and len(frame) > 0:
            frames.append(frame)

    if not frames:
        audit.append(
            audit_row(
                "harmonized_output",
                "blocked_no_successful_study_builds",
                "No country-wave produced a harmonized dataframe.",
                output_path=str(output),
                required_action="Fix source paths, raw variables, merge keys, or transformations in temp/harmonization_recipe.csv.",
            )
        )
        write_csv(AUDIT_PATH, audit, AUDIT_COLUMNS)
        write_csv(LINEAGE_PATH, lineage_rows(recipe_rows, None), LINEAGE_COLUMNS)
        append_log(TEMP_DIR / "audit_log.md", "Harmonization blocked: no successful study builds.")
        print("Harmonization blocked: no successful study builds.")
        return

    harmonized = pd.concat(frames, ignore_index=True, sort=False)
    leading = [column for column in EXPECTED_HARMONIZED_COLUMNS if column in harmonized.columns]
    trailing = [column for column in harmonized.columns if column not in leading]
    harmonized = harmonized[leading + trailing]
    output.parent.mkdir(parents=True, exist_ok=True)
    harmonized.to_csv(output, index=False, encoding="utf-8-sig")
    write_csv(LINEAGE_PATH, lineage_rows(recipe_rows, harmonized), LINEAGE_COLUMNS)
    audit.append(
        audit_row(
            "harmonized_output",
            "complete" if len(frames) == len(by_study) else "partial",
            f"Wrote {len(harmonized)} rows and {len(harmonized.columns)} columns from {len(frames)} successful country-wave build(s).",
            rows_input=len(recipe_rows),
            rows_output=len(harmonized),
            output_path=str(output),
        )
    )
    write_csv(AUDIT_PATH, audit, AUDIT_COLUMNS)
    append_log(TEMP_DIR / "audit_log.md", f"Wrote harmonized household dataset rows={len(harmonized)} columns={len(harmonized.columns)}.")
    print(f"Wrote {output} with {len(harmonized)} rows and {len(harmonized.columns)} columns.")


def main() -> None:
    ensure_dirs()
    args = parse_args()
    build_harmonized(args.recipe, args.output)


if __name__ == "__main__":
    main()
