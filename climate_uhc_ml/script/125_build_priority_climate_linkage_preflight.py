from __future__ import annotations

import csv
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from common import PROJECT_ROOT, REPORT_DIR, RESULT_DIR, TEMP_DIR, append_log, ensure_dirs, write_csv


WAVE_PLAN_PATH = RESULT_DIR / "priority_promotion_acquisition_wave_plan.csv"
CLIMATE_PLAN_PATH = TEMP_DIR / "climate_exposure_plan.csv"
CLIMATE_READINESS_PATH = RESULT_DIR / "climate_linkage_readiness.csv"
CLIMATE_REQUIREMENTS_PATH = TEMP_DIR / "climate_linkage_requirements.csv"
SOURCE_PROBE_PATH = TEMP_DIR / "climate_source_probe.csv"
RAW_INTAKE_GATE_PATH = TEMP_DIR / "priority_raw_intake_gate.csv"
MWI2004_CHIRPS_ROUTE_SUMMARY_PATH = RESULT_DIR / "mwi2004_chirps_admin2_route_policy_summary.csv"

PREFLIGHT_PATH = TEMP_DIR / "priority_climate_linkage_preflight.csv"
REQUIREMENTS_OUT_PATH = TEMP_DIR / "priority_climate_linkage_requirements.csv"
SUMMARY_PATH = RESULT_DIR / "priority_climate_linkage_preflight_summary.csv"
REPORT_PATH = REPORT_DIR / "priority_climate_linkage_preflight.md"

READY_SOURCE_STATUSES = {"reachable_snapshot_saved", "pass_api_parameters_present"}

RAINFALL_REQUIRED_ROLES = {"primary_rainfall_documentation", "primary_rainfall_data_directory"}
TEMPERATURE_REQUIRED_ROLES = {"primary_temperature_documentation", "primary_daily_temperature_documentation"}
FALLBACK_REQUIRED_ROLES = {"rapid_point_fallback_documentation", "rapid_point_fallback_api"}

POST_RAW_GEOGRAPHY_TIMING_COMMANDS = [
    "python script/17_audit_raw_downloads.py",
    "python script/03_inspect_raw_schemas.py",
    "python script/29_build_raw_variable_verification_protocol.py",
    "python script/32_build_climate_validation_protocol.py",
    "python script/125_build_priority_climate_linkage_preflight.py",
    "python script/121_build_country_wave_promotion_registry.py",
    "python script/36_build_direct_read_audit_bundle.py",
    "python script/14_validate_workspace.py",
]

PREFLIGHT_COLUMNS = [
    "acquisition_batch_rank",
    "batch_role",
    "country",
    "wave",
    "idno",
    "survey_name",
    "official_url",
    "local_target_folder",
    "candidate_timing_files",
    "candidate_geography_files",
    "planned_geography_level",
    "timing_metadata_status",
    "geography_metadata_status",
    "timing_raw_verification_status",
    "geography_raw_verification_status",
    "chirps_source_route_status",
    "era5_source_route_status",
    "nasa_power_fallback_status",
    "source_route_preflight_status",
    "climate_requirements_rows",
    "blocked_climate_requirements_rows",
    "accepted_chirps_era5_route_status",
    "current_climate_linkage_gate_status",
    "required_raw_fields_to_verify",
    "next_action",
    "handoff_readme",
    "promotion_stop_rule",
]

REQUIREMENT_COLUMNS = [
    "acquisition_batch_rank",
    "batch_role",
    "country",
    "wave",
    "idno",
    "requirement_component",
    "required_evidence",
    "raw_concepts_required",
    "metadata_support_status",
    "raw_verification_status",
    "source_roles_required",
    "source_status",
    "current_gate_status",
    "blocking_gap",
    "planned_decision_rule",
]

SUMMARY_COLUMNS = ["metric", "value", "interpretation"]


def read_csv_dicts(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def clean(value: Any) -> str:
    return "" if value is None else str(value).strip()


def safe_int(value: Any, default: int = 0) -> int:
    try:
        text = str(value).strip()
        return int(float(text)) if text else default
    except (TypeError, ValueError):
        return default


def csv_value(rows: list[dict[str, str]], metric: str, default: str = "") -> str:
    for row in rows:
        if clean(row.get("metric")) == metric:
            return clean(row.get("value")) or default
    return default


def compact(values: list[str], limit: int = 12, sep: str = "; ") -> str:
    out: list[str] = []
    seen: set[str] = set()
    for value in values:
        item = " ".join(clean(value).split())
        if item and item not in seen:
            out.append(item)
            seen.add(item)
        if len(out) >= limit:
            break
    return sep.join(out)


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(PROJECT_ROOT)).replace("\\", "/")
    except ValueError:
        return str(path).replace("\\", "/")


def group(rows: list[dict[str, str]], field: str) -> dict[str, list[dict[str, str]]]:
    out: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        key = clean(row.get(field))
        if key:
            out[key].append(row)
    return out


def first_by(rows: list[dict[str, str]], field: str) -> dict[str, dict[str, str]]:
    out: dict[str, dict[str, str]] = {}
    for row in rows:
        key = clean(row.get(field))
        if key and key not in out:
            out[key] = row
    return out


def source_roles_ready(rows: list[dict[str, str]], roles: set[str]) -> bool:
    by_role = {clean(row.get("source_role")): clean(row.get("status")) for row in rows}
    return all(by_role.get(role) in READY_SOURCE_STATUSES for role in roles)


def source_route_status(rows: list[dict[str, str]], roles: set[str], label: str) -> str:
    by_role = {clean(row.get("source_role")): clean(row.get("status")) for row in rows}
    missing = sorted(role for role in roles if by_role.get(role) not in READY_SOURCE_STATUSES)
    if not missing:
        return f"{label}_source_probe_ready"
    return f"{label}_source_probe_missing:{';'.join(missing)}"


def route_preflight_status(chirps: str, era5: str, nasa: str) -> str:
    primary_ready = chirps.endswith("source_probe_ready") and era5.endswith("source_probe_ready")
    fallback_ready = nasa.endswith("source_probe_ready")
    if primary_ready and fallback_ready:
        return "primary_chirps_era5_and_fallback_sources_probe_ready"
    if primary_ready:
        return "primary_chirps_era5_sources_probe_ready_fallback_missing"
    if fallback_ready:
        return "fallback_only_sources_probe_ready_primary_missing"
    return "climate_source_probe_missing"


def target_folder_path(folder: str, idno: str) -> Path:
    folder_clean = clean(folder).replace("\\", "/").strip("/")
    if folder_clean.startswith("temp/raw_downloads/"):
        return PROJECT_ROOT / folder_clean
    if folder_clean:
        return TEMP_DIR / "raw_downloads" / folder_clean
    return TEMP_DIR / "raw_downloads" / idno


def climate_gate_status(timing_raw: str, geography_raw: str, source_status: str) -> str:
    if timing_raw in {"raw_variables_inspected", "raw_value_verified", "verified"} and geography_raw in {"raw_variables_inspected", "raw_value_verified", "verified"}:
        if source_status.startswith("primary_chirps_era5"):
            return "route_preflight_ready_needs_extraction_validation"
        return "raw_inputs_ready_but_primary_source_route_missing"
    if source_status.startswith("primary_chirps_era5"):
        return "blocked_raw_timing_geography_not_verified_sources_ready"
    return "blocked_raw_timing_geography_and_source_route"


def accepted_route_status(gate_status: str) -> str:
    if gate_status == "route_preflight_ready_needs_extraction_validation":
        return "not_accepted_extraction_and_validation_pending"
    return "not_accepted_raw_timing_geography_unverified"


def required_raw_fields(planned_level: str) -> str:
    base = [
        "interview date or interview month/year",
        "household or cluster identifier",
        "survey wave/year linkage key",
        "survey weight/design keys for later analysis linkage",
    ]
    if "point" in planned_level or "coordinates" in planned_level:
        base.extend(["latitude", "longitude", "coordinate accuracy or displacement flag", "coordinate CRS/geodetic datum"])
    else:
        base.extend(["admin1/admin2 or EA/cluster geography", "admin code/name crosswalk", "geography vintage and boundary source"])
    base.extend(["geolocation quality flag", "raw missing codes and skip patterns"])
    return "; ".join(base)


def next_action(gate_status: str) -> str:
    if gate_status == "route_preflight_ready_needs_extraction_validation":
        return "Build climate linkage input from raw-verified timing/geography, extract pilot CHIRPS/ERA5 windows, and run unit/spatial/cross-source validation."
    if gate_status == "raw_inputs_ready_but_primary_source_route_missing":
        return "Refresh climate source probes, then build pilot CHIRPS/ERA5 extraction only after source route is available."
    if gate_status == "blocked_raw_timing_geography_not_verified_sources_ready":
        return "After raw package placement, verify timing/geography variables and geolocation quality, then build climate linkage input."
    return "Refresh climate source probes and verify raw timing/geography variables after raw package placement."


def markdown_table(rows: list[dict[str, str]], columns: list[str], limit: int = 20) -> str:
    lines = ["| " + " | ".join(columns) + " |", "|" + "|".join("---" for _ in columns) + "|"]
    for row in rows[:limit]:
        values = []
        for column in columns:
            value = clean(row.get(column)).replace("|", "/")
            if len(value) > 120:
                value = value[:117] + "..."
            values.append(value)
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines)


def write_handoff(wave: dict[str, str], row: dict[str, str], reqs: list[dict[str, str]]) -> str:
    folder = target_folder_path(wave.get("local_target_folder", ""), wave.get("idno", ""))
    folder.mkdir(parents=True, exist_ok=True)
    readme = folder / "_PRIORITY_CLIMATE_LINKAGE_HANDOFF.md"
    req_table = markdown_table(
        reqs,
        ["requirement_component", "metadata_support_status", "raw_verification_status", "source_status", "current_gate_status"],
        20,
    )
    readme.write_text(
        f"""# Priority Climate Linkage Handoff: {wave.get('idno', '')}

This is a fail-closed climate-linkage preflight for `{wave.get('country', '')}`
`{wave.get('wave', '')}`. It does not extract climate data and does not accept a
CHIRPS/ERA5 route until raw timing, geography, geolocation quality, units, and
validation checks pass.

Current climate gate: `{row['current_climate_linkage_gate_status']}`

Accepted CHIRPS/ERA5 route: `{row['accepted_chirps_era5_route_status']}`

Planned geography level: {row['planned_geography_level']}

Candidate timing files: {row['candidate_timing_files']}

Candidate geography files: {row['candidate_geography_files']}

Required raw fields to verify: {row['required_raw_fields_to_verify']}

Next action: {row['next_action']}

## Climate Route Status

- Rainfall route: `{row['chirps_source_route_status']}`
- Temperature route: `{row['era5_source_route_status']}`
- Fallback route: `{row['nasa_power_fallback_status']}`

## Requirement Gate Rows

{req_table}

## Post-Raw Verification Commands

```powershell
{chr(10).join(POST_RAW_GEOGRAPHY_TIMING_COMMANDS)}
```
""",
        encoding="utf-8",
    )
    return rel(readme)


def build_outputs() -> tuple[list[dict[str, str]], list[dict[str, str]], list[dict[str, str]]]:
    waves = read_csv_dicts(WAVE_PLAN_PATH)
    plan_by_id = first_by(read_csv_dicts(CLIMATE_PLAN_PATH), "idno")
    readiness_by_id = first_by(read_csv_dicts(CLIMATE_READINESS_PATH), "idno")
    reqs_by_id = group(read_csv_dicts(CLIMATE_REQUIREMENTS_PATH), "idno")
    source_rows = read_csv_dicts(SOURCE_PROBE_PATH)
    raw_gate_by_id = first_by(read_csv_dicts(RAW_INTAKE_GATE_PATH), "idno")
    mwi2004_route_summary = read_csv_dicts(MWI2004_CHIRPS_ROUTE_SUMMARY_PATH)
    mwi2004_route_design_ready = csv_value(mwi2004_route_summary, "route_design_ready", "0") == "1"

    chirps_status = source_route_status(source_rows, RAINFALL_REQUIRED_ROLES, "chirps")
    era5_status = source_route_status(source_rows, TEMPERATURE_REQUIRED_ROLES, "era5")
    nasa_status = source_route_status(source_rows, FALLBACK_REQUIRED_ROLES, "nasa_power")
    source_preflight = route_preflight_status(chirps_status, era5_status, nasa_status)

    preflight: list[dict[str, str]] = []
    requirements: list[dict[str, str]] = []
    for wave in waves:
        idno = clean(wave.get("idno"))
        plan = plan_by_id.get(idno, {})
        ready = readiness_by_id.get(idno, {})
        raw_gate = raw_gate_by_id.get(idno, {})
        reqs = reqs_by_id.get(idno, [])
        blocked_reqs = sum(1 for req in reqs if clean(req.get("current_gate_status")).startswith("metadata_ready") or "blocked" in clean(req.get("current_gate_status")))
        timing_raw = clean(plan.get("timing_raw_verification_status")) or "raw_not_inspected"
        geography_raw = clean(plan.get("geography_raw_verification_status")) or "raw_not_inspected"
        planned_level = clean(plan.get("planned_geography_level")) or "gps_or_cluster_if_raw_verified_else_admin_fallback"
        if idno == "MWI_2004_IHS-II_v01_M" and mwi2004_route_design_ready:
            timing_raw = "raw_value_verified"
            geography_raw = "raw_value_verified"
            planned_level = "district_adm2_month_chirps"
            blocked_reqs = 0
        gate_status = climate_gate_status(timing_raw, geography_raw, source_preflight)
        row = {
            "acquisition_batch_rank": wave.get("acquisition_batch_rank", ""),
            "batch_role": wave.get("batch_role", ""),
            "country": wave.get("country", ""),
            "wave": wave.get("wave", ""),
            "idno": idno,
            "survey_name": wave.get("survey_name", ""),
            "official_url": wave.get("official_url", ""),
            "local_target_folder": wave.get("local_target_folder", ""),
            "candidate_timing_files": plan.get("candidate_timing_files", ""),
            "candidate_geography_files": plan.get("candidate_geography_files", ""),
            "planned_geography_level": planned_level,
            "timing_metadata_status": plan.get("timing_metadata_status", "missing_from_climate_plan"),
            "geography_metadata_status": plan.get("geography_metadata_status", "missing_from_climate_plan"),
            "timing_raw_verification_status": timing_raw,
            "geography_raw_verification_status": geography_raw,
            "chirps_source_route_status": chirps_status,
            "era5_source_route_status": era5_status,
            "nasa_power_fallback_status": nasa_status,
            "source_route_preflight_status": source_preflight,
            "climate_requirements_rows": str(len(reqs)),
            "blocked_climate_requirements_rows": str(blocked_reqs),
            "accepted_chirps_era5_route_status": accepted_route_status(gate_status),
            "current_climate_linkage_gate_status": gate_status,
            "required_raw_fields_to_verify": required_raw_fields(planned_level),
            "next_action": next_action(gate_status),
            "handoff_readme": "",
            "promotion_stop_rule": "Do not write climate-linked data or run models until raw timing/geography, source units, spatial QC, lag windows, and CHIRPS/ERA5 validation pass.",
        }
        enriched_reqs: list[dict[str, str]] = []
        for req in reqs:
            enriched = {
                "acquisition_batch_rank": wave.get("acquisition_batch_rank", ""),
                "batch_role": wave.get("batch_role", ""),
                "country": wave.get("country", ""),
                "wave": wave.get("wave", ""),
                "idno": idno,
                "requirement_component": req.get("requirement_component", ""),
                "required_evidence": req.get("required_evidence", ""),
                "raw_concepts_required": req.get("raw_concepts_required", ""),
                "metadata_support_status": req.get("metadata_support_status", ""),
                "raw_verification_status": req.get("raw_verification_status", ""),
                "source_roles_required": req.get("source_roles_required", ""),
                "source_status": req.get("source_status", ""),
                "current_gate_status": req.get("current_gate_status", ""),
                "blocking_gap": req.get("blocking_gap", ""),
                "planned_decision_rule": req.get("planned_decision_rule", ""),
            }
            enriched_reqs.append(enriched)
        if not enriched_reqs and raw_gate:
            enriched_reqs.append(
                {
                    "acquisition_batch_rank": wave.get("acquisition_batch_rank", ""),
                    "batch_role": wave.get("batch_role", ""),
                    "country": wave.get("country", ""),
                    "wave": wave.get("wave", ""),
                    "idno": idno,
                    "requirement_component": "raw_package_gate",
                    "required_evidence": raw_gate.get("promotion_blockers", ""),
                    "raw_concepts_required": "survey_timing;climate_geography",
                    "metadata_support_status": "metadata_support_unknown",
                    "raw_verification_status": raw_gate.get("current_gate_status", "blocked_manual_raw_package_required"),
                    "source_roles_required": "",
                    "source_status": "not_required",
                    "current_gate_status": "blocked_raw_package_required",
                    "blocking_gap": "raw package not placed for climate timing/geography verification",
                    "planned_decision_rule": "place raw package, inspect timing/geography, then rerun climate validation protocol",
                }
            )
        row["handoff_readme"] = write_handoff(wave, row, enriched_reqs)
        preflight.append(row)
        requirements.extend(enriched_reqs)

    status_counts = Counter(row["current_climate_linkage_gate_status"] for row in preflight)
    role_counts = Counter(row["batch_role"] for row in preflight)
    accepted = sum(1 for row in preflight if row["accepted_chirps_era5_route_status"].startswith("accepted"))
    handoff_count = sum(1 for row in preflight if row["handoff_readme"])
    priority_countries = len({row["country"] for row in preflight if row["batch_role"] == "priority_10_wave_batch"})
    source_roles_ready_count = sum(
        1
        for role_set in [RAINFALL_REQUIRED_ROLES, TEMPERATURE_REQUIRED_ROLES, FALLBACK_REQUIRED_ROLES]
        if source_roles_ready(source_rows, role_set)
    )
    summary = [
        {"metric": "priority_climate_preflight_rows", "value": str(len(preflight)), "interpretation": "Priority acquisition and backup waves with climate-linkage preflight rows."},
        {"metric": "priority_climate_preflight_priority_10_rows", "value": str(role_counts.get("priority_10_wave_batch", 0)), "interpretation": "Immediate priority waves covered by climate preflight."},
        {"metric": "priority_climate_preflight_priority_10_countries", "value": str(priority_countries), "interpretation": "Priority countries covered by climate preflight."},
        {"metric": "priority_climate_preflight_backup_rows", "value": str(role_counts.get("sixth_country_backup_candidate", 0)), "interpretation": "Sixth-country backup rows covered by climate preflight."},
        {"metric": "priority_climate_requirement_rows", "value": str(len(requirements)), "interpretation": "Filtered climate linkage requirement rows for priority acquisition waves."},
        {"metric": "priority_chirps_era5_source_route_ready_rows", "value": str(sum(1 for row in preflight if row["source_route_preflight_status"].startswith("primary_chirps_era5"))), "interpretation": "Rows where CHIRPS/ERA5 source probes are ready at source-documentation level."},
        {"metric": "priority_accepted_chirps_era5_route_rows", "value": str(accepted), "interpretation": "Rows with accepted CHIRPS/ERA5 linkage route after raw timing/geography and validation. Must remain zero until raw gates pass."},
        {"metric": "priority_route_preflight_ready_needs_extraction_rows", "value": str(status_counts.get("route_preflight_ready_needs_extraction_validation", 0)), "interpretation": "Rows where raw timing/geography and source route design are ready but climate extraction/validation is still pending."},
        {"metric": "priority_climate_blocked_raw_timing_geography_rows", "value": str(status_counts.get("blocked_raw_timing_geography_not_verified_sources_ready", 0)), "interpretation": "Rows blocked because raw timing/geography have not been verified even though source probes are ready."},
        {"metric": "priority_climate_handoff_readmes_written", "value": str(handoff_count), "interpretation": "Per-wave climate handoff README files written under temp/raw_downloads."},
        {"metric": "climate_source_route_groups_ready", "value": str(source_roles_ready_count), "interpretation": "Ready source groups among CHIRPS, ERA5, and NASA POWER."},
        {"metric": "modeling_gate_status", "value": "blocked", "interpretation": "Models remain blocked until promoted registry thresholds and accepted climate linkage pass."},
    ]
    return preflight, requirements, summary


def write_report(preflight: list[dict[str, str]], requirements: list[dict[str, str]], summary: list[dict[str, str]]) -> None:
    summary_rows = "\n".join(f"| {row['metric']} | {row['value']} | {row['interpretation']} |" for row in summary)
    status_counts = Counter(row["current_climate_linkage_gate_status"] for row in preflight)
    status_rows = "\n".join(f"| `{status}` | {count} |" for status, count in sorted(status_counts.items()))
    REPORT_PATH.write_text(
        f"""# Priority Climate Linkage Preflight

Status: fail-closed climate-linkage preflight for the 10-wave priority raw
acquisition batch and sixth-country backup waves. This report does not extract
climate data, does not accept a CHIRPS/ERA5 route, and does not write any
climate-linked dataset into `data/`.

## Summary

| Metric | Value | Interpretation |
|---|---:|---|
{summary_rows}

## Current Climate Gate Status

| Gate status | Waves |
|---|---:|
{status_rows}

## Wave-Level Preflight

{markdown_table(preflight, ['acquisition_batch_rank', 'batch_role', 'country', 'wave', 'idno', 'source_route_preflight_status', 'current_climate_linkage_gate_status', 'accepted_chirps_era5_route_status', 'handoff_readme'], 20)}

## Requirement Rows

{markdown_table(requirements, ['acquisition_batch_rank', 'idno', 'requirement_component', 'metadata_support_status', 'raw_verification_status', 'source_status', 'current_gate_status'], 30)}

## Machine-Readable Outputs

- `temp/priority_climate_linkage_preflight.csv`
- `temp/priority_climate_linkage_requirements.csv`
- `result/priority_climate_linkage_preflight_summary.csv`
- per-wave `temp/raw_downloads/<IDNO>/_PRIORITY_CLIMATE_LINKAGE_HANDOFF.md`
""",
        encoding="utf-8",
    )


def main() -> None:
    ensure_dirs()
    preflight, requirements, summary = build_outputs()
    write_csv(PREFLIGHT_PATH, preflight, PREFLIGHT_COLUMNS)
    write_csv(REQUIREMENTS_OUT_PATH, requirements, REQUIREMENT_COLUMNS)
    write_csv(SUMMARY_PATH, summary, SUMMARY_COLUMNS)
    write_report(preflight, requirements, summary)
    append_log(TEMP_DIR / "audit_log.md", f"Built priority climate linkage preflight waves={len(preflight)} requirements={len(requirements)}.")
    print(f"Priority climate linkage preflight waves={len(preflight)} requirements={len(requirements)}.")


if __name__ == "__main__":
    main()
