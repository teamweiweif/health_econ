from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

from common import REPORT_DIR, RESULT_DIR, TEMP_DIR, append_log, ensure_dirs, write_csv


AUDIT_PATH = TEMP_DIR / "alb2002_boundary_blocker_resolution_matrix.csv"
SUMMARY_PATH = RESULT_DIR / "alb2002_boundary_blocker_resolution_summary.csv"
REPORT_PATH = REPORT_DIR / "alb2002_boundary_blocker_resolution_matrix.md"

DECISION = "blocked_no_alb2002_boundary_source_ready_for_climate_linkage"

AUDIT_COLUMNS = [
    "source_id",
    "source_family",
    "source_name",
    "source_url",
    "observed_unit_or_level",
    "name_coverage_status",
    "historical_vintage_status",
    "official_provenance_status",
    "raw_code_crosswalk_status",
    "geometry_status",
    "climate_linkage_ready_rows",
    "data_write_ready_rows",
    "blocker_class",
    "blocker_summary",
    "next_resolution_step",
    "evidence_files",
]
SUMMARY_COLUMNS = ["metric", "value", "interpretation"]


def read_csv_dicts(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def first_row(rows: list[dict[str, str]], field: str, value: str) -> dict[str, str]:
    return next((row for row in rows if row.get(field) == value), {})


def metric_value(rows: list[dict[str, str]], metric: str, default: str = "0") -> str:
    return next((row.get("value", default) for row in rows if row.get("metric") == metric), default)


def safe_int(value: Any, default: int = 0) -> int:
    try:
        return int(float(str(value).strip()))
    except (TypeError, ValueError):
        return default


def summary_row(metric: str, value: Any, interpretation: str) -> dict[str, str]:
    return {"metric": metric, "value": str(value), "interpretation": interpretation}


def row(
    source_id: str,
    source_family: str,
    source_name: str,
    source_url: str,
    observed_unit_or_level: str,
    name_coverage_status: str,
    historical_vintage_status: str,
    official_provenance_status: str,
    raw_code_crosswalk_status: str,
    geometry_status: str,
    blocker_class: str,
    blocker_summary: str,
    next_resolution_step: str,
    evidence_files: list[str],
    climate_linkage_ready_rows: int = 0,
) -> dict[str, str]:
    return {
        "source_id": source_id,
        "source_family": source_family,
        "source_name": source_name,
        "source_url": source_url,
        "observed_unit_or_level": observed_unit_or_level,
        "name_coverage_status": name_coverage_status,
        "historical_vintage_status": historical_vintage_status,
        "official_provenance_status": official_provenance_status,
        "raw_code_crosswalk_status": raw_code_crosswalk_status,
        "geometry_status": geometry_status,
        "climate_linkage_ready_rows": str(climate_linkage_ready_rows),
        "data_write_ready_rows": "0",
        "blocker_class": blocker_class,
        "blocker_summary": blocker_summary,
        "next_resolution_step": next_resolution_step,
        "evidence_files": "; ".join(evidence_files),
    }


def build_matrix() -> list[dict[str, str]]:
    source_resource = read_csv_dicts(TEMP_DIR / "alb2002_boundary_source_resource_search_audit.csv")
    source_alternative = read_csv_dicts(TEMP_DIR / "alb2002_boundary_source_alternative_audit.csv")
    followup = read_csv_dicts(TEMP_DIR / "alb2002_boundary_manual_source_followup_audit.csv")
    gadm = read_csv_dicts(TEMP_DIR / "alb2002_gadm_boundary_lead_audit.csv")
    geometry_summary = read_csv_dicts(RESULT_DIR / "alb2002_boundary_geometry_provenance_summary.csv")
    local_geo = read_csv_dicts(RESULT_DIR / "alb2002_local_geography_artifact_summary.csv")
    boundary_name = read_csv_dicts(RESULT_DIR / "alb2002_boundary_name_match_summary.csv")

    geob_current = first_row(source_resource, "candidate_id", "geoboundaries_current_pinned_adm2")
    geob_201 = first_row(source_resource, "candidate_id", "geoboundaries_2_0_1_adm2")
    hdx_resource = first_row(source_resource, "candidate_id", "hdx_cod_ab_alb_2019_gazetteer_adm2")
    asig_alt = first_row(source_alternative, "candidate_id", "asig_geoportal_current")
    worldbank = first_row(followup, "candidate_id", "worldbank_alb2002_lsms_study")
    instat = first_row(followup, "candidate_id", "instat_census_2001")
    ipums = first_row(followup, "candidate_id", "ipums_ihgis_alb2001")
    unece = first_row(followup, "candidate_id", "unece_instat_2011_gis_paper")
    gadm36 = first_row(gadm, "candidate_id", "gadm36_alb_adm2")
    gadm41 = first_row(gadm, "candidate_id", "gadm41_alb_adm2")

    district_rows = metric_value(boundary_name, "alb2002_boundary_name_match_survey_district_rows")
    local_coordinate_ready = metric_value(local_geo, "alb2002_local_geo_artifact_local_coordinate_ready_rows")
    local_boundary_ready = metric_value(local_geo, "alb2002_local_geo_artifact_local_boundary_ready_rows")
    geob_201_features = metric_value(geometry_summary, "alb2002_boundary_geometry_feature_rows")
    geob_201_matches = metric_value(geometry_summary, "alb2002_boundary_geometry_survey_key_matched_rows")
    geob_201_year = metric_value(geometry_summary, "alb2002_boundary_geometry_metadata_boundary_year", "missing")
    geob_201_source = metric_value(geometry_summary, "alb2002_boundary_geometry_metadata_boundary_source", "missing")

    rows = [
        row(
            "alb2002_raw_survey_geography",
            "raw_microdata",
            "ALB_2002 household district identifiers",
            "",
            f"observed district codes/names; survey_district_rows={district_rows}",
            "observed_raw_district_keys_not_boundary_coverage",
            "survey_year_2002_observed_but_no_boundary_artifact",
            "official_survey_microdata_context_only",
            "raw_code_values_observed_no_boundary_feature_crosswalk",
            "no_coordinate_or_ea_boundary_artifact",
            "raw_artifact_absence",
            f"Raw district and timing keys exist, but local coordinate-ready rows={local_coordinate_ready} and local boundary-ready rows={local_boundary_ready}.",
            "Request/download official GPS, EA-map, district-codebook, or historical boundary artifacts before climate linkage.",
            ["result/alb2002_boundary_name_match_summary.csv", "result/alb2002_local_geography_artifact_summary.csv"],
        ),
        row(
            "worldbank_alb2002_lsms_study",
            "official_survey_lead",
            worldbank.get("source_name", "World Bank Microdata Library ALB_2002 LSMS study page"),
            worldbank.get("source_url", "https://microdata.worldbank.org/catalog/86/study-description"),
            worldbank.get("boundary_level_claim", "survey ancillary geography may exist, artifact not obtained"),
            "potentially_compatible_if_artifacts_obtained",
            "survey_context_2002_but_artifact_not_obtained",
            "official_survey_source",
            "blocked_no_obtained_gps_ea_or_code_crosswalk",
            "not_obtained",
            "artifact_access_blocker",
            worldbank.get("reviewer_interpretation", "Official study context is useful, but no climate-linkage geography artifact has been obtained."),
            worldbank.get("next_action", "Request/download all official ALB_2002 geography ancillary files before climate-linkage promotion."),
            ["temp/alb2002_boundary_manual_source_followup_audit.csv"],
        ),
        row(
            "instat_census_2001",
            "official_census_lead",
            instat.get("source_name", "INSTAT Census of Population and Housing page"),
            instat.get("source_url", "https://www.instat.gov.al/en/themes/censuses/census-of-population-and-housing/"),
            instat.get("boundary_level_claim", "official census context only"),
            "not_boundary_name_coverage",
            "official_2001_context_without_boundary_file",
            "official_census_context",
            "blocked_no_district_commune_ea_code_list",
            "not_obtained",
            "official_context_without_file",
            instat.get("reviewer_interpretation", "Official census context alone does not produce an analysis-ready boundary layer."),
            instat.get("next_action", "Search/request official 2001 district, commune, EA, or cartography boundary artifacts with codes."),
            ["temp/alb2002_boundary_manual_source_followup_audit.csv"],
        ),
        row(
            "geoboundaries_2_0_1_adm2",
            "public_boundary_lead",
            geob_201.get("source_name", "geoBoundaries 2.0.1 Albania ADM2 GeoJSON"),
            geob_201.get("source_url", "https://www.geoboundaries.org/data/geoBoundaries-2_0_1/ALB/ADM2/geoBoundaries-2_0_1-ALB-ADM2.geojson"),
            f"ADM2 geometry; features={geob_201_features}; matched_survey_keys={geob_201_matches}",
            "complete_name_coverage_candidate",
            f"blocked_boundary_year_{geob_201_year}_not_verified_2002",
            f"public_nonofficial_source={geob_201_source}",
            "name_match_crosswalk_only_not_official_code_crosswalk",
            "coordinate_structure_ok_topology_not_validated",
            "historical_vintage_blocker",
            geob_201.get("blocking_reason", "Complete name coverage exists, but historical 2002 boundary validity is not verified."),
            "Verify historical continuity or obtain an official 2001/2002 district boundary before using this geometry.",
            ["temp/alb2002_boundary_source_resource_search_audit.csv", "result/alb2002_boundary_geometry_provenance_summary.csv"],
        ),
        row(
            "gadm36_alb_adm2",
            "public_boundary_lead",
            gadm36.get("source_name", "GADM 3.6 Albania shapefile"),
            gadm36.get("source_url", "https://geodata.ucdavis.edu/gadm/gadm3.6/shp/gadm36_ALB_shp.zip"),
            f"ADM2/Rreth/District; rows={gadm36.get('adm2_row_count', '0')}; distinct_keys={gadm36.get('adm2_distinct_normalized_key_count', '0')}",
            "complete_name_coverage_candidate",
            gadm36.get("historical_2002_provenance_status", "blocked_no_verified_official_2001_2002_boundary_provenance"),
            "public_nonofficial_or_unverified_historical_source",
            "duplicate_shkoder_and_no_official_code_crosswalk",
            "shapefile_snapshot_present_topology_not_promoted",
            "duplicate_key_and_provenance_blocker",
            gadm36.get("blocking_reason", "GADM 3.6 has useful name coverage but duplicate SHKODER rows and no verified 2002 provenance."),
            "Resolve duplicate SHKODER and prove official 2001/2002 vintage before any climate-linkage promotion.",
            ["temp/alb2002_gadm_boundary_lead_audit.csv"],
        ),
        row(
            "gadm41_alb_adm2",
            "public_boundary_lead",
            gadm41.get("source_name", "GADM 4.1 Albania shapefile"),
            gadm41.get("source_url", "https://geodata.ucdavis.edu/gadm/gadm4.1/shp/gadm41_ALB_shp.zip"),
            f"ADM2; rows={gadm41.get('adm2_row_count', '0')}; district_type_rows={gadm41.get('adm2_engtype_district_rows', '0')}",
            "complete_name_coverage_candidate",
            gadm41.get("historical_2002_provenance_status", "blocked_no_verified_official_2001_2002_boundary_provenance"),
            "public_nonofficial_or_unverified_historical_source",
            "duplicate_shkoder_and_no_official_code_crosswalk",
            "shapefile_snapshot_present_type_fields_not_district_ready",
            "provenance_and_type_blocker",
            gadm41.get("blocking_reason", "GADM 4.1 names align after repairs, but type/provenance is insufficient for 2002 climate linkage."),
            "Use only as a comparison unless source provenance, district typing, and historical vintage are proven.",
            ["temp/alb2002_gadm_boundary_lead_audit.csv"],
        ),
        row(
            "geoboundaries_current_pinned_adm2",
            "current_boundary_reference",
            geob_current.get("source_name", "geoBoundaries gbOpen Albania ADM2 current pinned snapshot"),
            geob_current.get("source_url", "https://github.com/wmgeolab/geoBoundaries/raw/9469f09/releaseData/gbOpen/ALB/ADM2/geoBoundaries-ALB-ADM2.geojson"),
            f"current ADM2; features={geob_current.get('feature_count', '0')}; distinct_keys={geob_current.get('distinct_boundary_key_count', '0')}",
            "incomplete_or_duplicate_name_coverage_current_boundary",
            "current_2021_not_historical_2002",
            "public_current_boundary_source",
            "name_only_current_boundary_not_official_code_crosswalk",
            "geojson_snapshot_present_not_historical_promoted",
            "current_boundary_not_historical",
            geob_current.get("blocking_reason", "Current public ADM2 boundaries are not verified as 2002 LSMS district boundaries."),
            "Keep as a current-boundary comparison only unless official historical continuity evidence is obtained.",
            ["temp/alb2002_boundary_source_resource_search_audit.csv"],
        ),
        row(
            "ipums_ihgis_alb2001",
            "historical_census_gis_lead",
            ipums.get("source_name", "IPUMS IHGIS Albania 2001 census GIS boundary files"),
            ipums.get("source_url", "https://ihgis.ipums.org/geography-gis"),
            ipums.get("boundary_level_claim", "prefectures g1 only in visible catalog evidence"),
            "not_36_district_name_coverage",
            "historical_2001_context_but_wrong_visible_level",
            "external_census_gis_catalog",
            "blocked_prefecture_level_not_36_district_crosswalk",
            "not_obtained",
            "level_mismatch",
            ipums.get("reviewer_interpretation", "Visible catalog evidence is not sufficient for ALB_2002 district climate linkage."),
            ipums.get("next_action", "Revisit only if a separate Albania 2001 district/g2 boundary file or crosswalk is found."),
            ["temp/alb2002_boundary_manual_source_followup_audit.csv"],
        ),
        row(
            "asig_geoportal_current",
            "official_geoportal_lead",
            asig_alt.get("source_name", "ASIG Geoportal Albania data catalog"),
            asig_alt.get("source_url", "https://geoportal.asig.gov.al/en/data"),
            asig_alt.get("source_year_claim", "current administrative map / 2019 local-government division metadata"),
            "not_verified",
            "historical_2001_2002_layer_not_verified",
            "official_current_geoportal_lead",
            "blocked_no_downloaded_historical_layer_or_codes",
            "not_obtained",
            "historical_layer_not_verified",
            asig_alt.get("blocking_reason", "No public 2001/2002 LSMS district, EA, or GPS boundary artifact was verified from ASIG."),
            "Manually search or request a historical 2001/2002 administrative, census, commune, or EA layer.",
            ["temp/alb2002_boundary_source_alternative_audit.csv"],
        ),
        row(
            "hdx_cod_ab_alb_2019_gazetteer_adm2",
            "current_boundary_reference",
            hdx_resource.get("source_name", "HDX COD-AB Albania 2019 gazetteer ADM2 sheet"),
            hdx_resource.get("source_url", "https://data.humdata.org/dataset/cod-ab-alb"),
            hdx_resource.get("source_year_claim", "2019 municipality-style ADM2 reference"),
            "not_36_district_name_coverage",
            "post_2015_or_2019_units_not_historical_2002",
            "humanitarian_current_reference",
            "blocked_current_municipality_units_not_lsms_district_codes",
            "gazetteer_snapshot_present_not_boundary_promoted",
            "current_unit_mismatch",
            hdx_resource.get("blocking_reason", "HDX COD-AB is a current/post-2019 administrative reference, not the 36 ALB_2002 district layer."),
            "Use only if a documented historical district-to-current-unit crosswalk supports the intended aggregation.",
            ["temp/alb2002_boundary_source_resource_search_audit.csv"],
        ),
        row(
            "unece_instat_2011_gis_paper",
            "official_statistical_system_evidence",
            unece.get("source_name", "UNECE/INSTAT 2011 census GIS implementation paper"),
            unece.get("source_url", "https://unece.org/fileadmin/DAM/stats/documents/ece/ces/ge.50/2014/Topic_3_Albania_Shameti.pdf"),
            unece.get("boundary_level_claim", "negative evidence on pre-2011 national digital map availability"),
            "not_boundary_source",
            "negative_evidence_against_assuming_public_pre2011_digital_boundary",
            "official_statistical_system_context",
            "no_crosswalk_or_boundary_file",
            "not_boundary_geometry",
            "negative_pre2011_digital_map_evidence",
            unece.get("reviewer_interpretation", "Negative evidence reinforces that current/post-2011 GIS layers cannot be treated as 2002 LSMS boundaries without separate proof."),
            unece.get("next_action", "Require a separate official 2001/2002 boundary, EA-map, GPS, or continuity/crosswalk source before promotion."),
            ["temp/alb2002_boundary_manual_source_followup_audit.csv"],
        ),
    ]
    return rows


def build_summary(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    official_families = {
        "official_survey_lead",
        "official_census_lead",
        "official_geoportal_lead",
        "official_statistical_system_evidence",
    }
    incompatible_classes = {
        "current_boundary_not_historical",
        "current_unit_mismatch",
        "level_mismatch",
        "negative_pre2011_digital_map_evidence",
    }
    return [
        summary_row("alb2002_boundary_blocker_resolution_rows", len(rows), "Boundary-source resolution rows consolidated."),
        summary_row("alb2002_boundary_blocker_official_or_primary_lead_rows", sum(1 for r in rows if r["source_family"] in official_families), "Official or primary institutional leads represented in the matrix."),
        summary_row("alb2002_boundary_blocker_candidate_name_coverage_rows", sum(1 for r in rows if r["name_coverage_status"] == "complete_name_coverage_candidate"), "Public boundary leads with complete candidate name coverage but no promotion."),
        summary_row("alb2002_boundary_blocker_incompatible_or_negative_rows", sum(1 for r in rows if r["blocker_class"] in incompatible_classes), "Rows that are current-unit, wrong-level, or negative-evidence sources."),
        summary_row("alb2002_boundary_blocker_historical_2002_ready_rows", sum(1 for r in rows if "ready" in r["historical_vintage_status"] and not r["historical_vintage_status"].startswith("blocked")), "Rows verified as 2001/2002 historical boundary-ready."),
        summary_row("alb2002_boundary_blocker_climate_linkage_ready_rows", sum(safe_int(r["climate_linkage_ready_rows"]) for r in rows), "Rows ready for promoted ALB_2002 climate linkage."),
        summary_row("alb2002_boundary_blocker_data_write_ready_rows", sum(safe_int(r["data_write_ready_rows"]) for r in rows), "Rows allowed for data/ writes by this boundary matrix; intentionally zero."),
        summary_row("alb2002_boundary_blocker_hard_blocked_rows", sum(1 for r in rows if safe_int(r["climate_linkage_ready_rows"]) == 0), "Rows still blocked from promoted climate linkage."),
        summary_row("alb2002_boundary_blocker_required_source_action_rows", sum(1 for r in rows if any(word in r["next_resolution_step"].lower() for word in ["request", "download", "search", "verify", "obtain"])), "Rows with an explicit source-search, request, or verification action."),
        summary_row("alb2002_boundary_blocker_current_decision", DECISION, "Current consolidated ALB_2002 boundary-source decision."),
    ]


def markdown_rows(rows: list[dict[str, str]], columns: list[str]) -> str:
    lines = ["| " + " | ".join(columns) + " |", "|" + "|".join("---" for _ in columns) + "|"]
    for item in rows:
        values = []
        for column in columns:
            value = str(item.get(column, "")).replace("\n", " ").replace("|", "/")
            if len(value) > 120:
                value = value[:117] + "..."
            values.append(value)
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines)


def write_report(rows: list[dict[str, str]], summary: list[dict[str, str]]) -> None:
    summary_table = "\n".join(f"| {item['metric']} | {item['value']} | {item['interpretation']} |" for item in summary)
    REPORT_PATH.write_text(
        f"""# ALB_2002 Boundary Blocker Resolution Matrix

Status: fail-closed boundary-source resolution matrix. This consolidates ALB_2002 raw geography, official source leads, public boundary leads, current-boundary references, and negative evidence into one climate-linkage decision. It does not write `data/`, does not promote any boundary source, and does not relax the ALB_2002 climate-geography gate.

## Summary

| Metric | Value | Interpretation |
|---|---:|---|
{summary_table}

## Boundary Source Matrix

{markdown_rows(rows, ['source_id', 'source_family', 'name_coverage_status', 'historical_vintage_status', 'blocker_class', 'climate_linkage_ready_rows', 'data_write_ready_rows'])}

## Interpretation

- ALB_2002 household files expose district keys and survey timing, but no GPS, EA-map, official historical boundary, or accepted district-code-to-geometry crosswalk has been obtained.
- geoBoundaries 2.0.1 is the cleanest 36-feature public name-coverage lead, but its companion metadata reports boundary year 2013 and OpenStreetMap/Wambacher provenance, so it cannot be treated as a verified 2002 district layer.
- GADM 3.6 is a useful comparison lead because it is typed as Rreth/District and covers the 36 normalized keys, but duplicate `SHKODER` rows and missing official 2001/2002 provenance keep it blocked.
- IHGIS, HDX/COD-AB, current geoBoundaries, ASIG-current evidence, and the UNECE/INSTAT GIS paper all narrow the search space but do not provide a promoted ALB_2002 climate-linkage source.

## Required Resolution

The gate can move only if a future artifact supplies one of these with checksums and documentation: official ALB_2002 GPS/EA-map files, official 2001/2002 district or commune boundaries with codes, or a defensible continuity/crosswalk proof tying a public geometry to the 2002 LSMS district groups. Until then, climate-linkage-ready and data-write-ready rows remain zero.

## Machine-Readable Outputs

- `temp/alb2002_boundary_blocker_resolution_matrix.csv`
- `result/alb2002_boundary_blocker_resolution_summary.csv`
""",
        encoding="utf-8",
    )


def main() -> None:
    ensure_dirs()
    rows = build_matrix()
    summary = build_summary(rows)
    write_csv(AUDIT_PATH, rows, AUDIT_COLUMNS)
    write_csv(SUMMARY_PATH, summary, SUMMARY_COLUMNS)
    write_report(rows, summary)
    append_log(TEMP_DIR / "audit_log.md", f"Built ALB_2002 boundary blocker resolution matrix rows={len(rows)} decision={DECISION}.")
    print(f"ALB_2002 boundary blocker resolution rows={len(rows)} decision={DECISION}.")


if __name__ == "__main__":
    main()
