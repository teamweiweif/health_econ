from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

from common import REPORT_DIR, RESULT_DIR, TEMP_DIR, append_log, ensure_dirs, write_csv


SOURCE_ALTERNATIVES_PATH = TEMP_DIR / "alb2002_boundary_source_alternative_audit.csv"
RESOURCE_SEARCH_PATH = TEMP_DIR / "alb2002_boundary_source_resource_search_audit.csv"
GEOMETRY_SUMMARY_PATH = RESULT_DIR / "alb2002_boundary_geometry_provenance_summary.csv"
LOCAL_GEO_SUMMARY_PATH = RESULT_DIR / "alb2002_local_geography_artifact_summary.csv"
CROSSWALK_SUMMARY_PATH = RESULT_DIR / "alb2002_district_climate_crosswalk_summary.csv"
FOLLOWUP_AUDIT_PATH = TEMP_DIR / "alb2002_boundary_manual_source_followup_audit.csv"

ACTION_QUEUE_PATH = TEMP_DIR / "alb2002_boundary_manual_verification_action_queue.csv"
PROMOTION_GATE_PATH = TEMP_DIR / "alb2002_boundary_promotion_gate_checklist.csv"
SUMMARY_PATH = RESULT_DIR / "alb2002_boundary_manual_verification_packet_summary.csv"
REPORT_PATH = REPORT_DIR / "alb2002_boundary_manual_verification_packet.md"

DECISION = "blocked_manual_boundary_verification_required_before_alb2002_climate_linkage"

ACTION_COLUMNS = [
    "action_rank",
    "candidate_id",
    "source_name",
    "source_url",
    "source_role",
    "current_evidence",
    "blocking_status",
    "manual_verification_action",
    "required_artifacts",
    "acceptance_evidence",
    "fail_closed_stop_rule",
    "post_verification_commands",
]
GATE_COLUMNS = [
    "gate_id",
    "gate_label",
    "current_status",
    "current_evidence",
    "required_evidence_to_pass",
    "promotion_effect_if_passed",
    "fail_closed_stop_rule",
]
SUMMARY_COLUMNS = ["metric", "value", "interpretation"]


def read_csv_dicts(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def metric_value(rows: list[dict[str, str]], metric: str, default: str = "0") -> str:
    for row in rows:
        if row.get("metric") == metric:
            return row.get("value", default)
    return default


def source_by_id(rows: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    return {row.get("candidate_id", ""): row for row in rows if row.get("candidate_id")}


def resource_by_id(rows: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    return {row.get("candidate_id", ""): row for row in rows if row.get("candidate_id")}


def action_row(
    action_rank: int,
    candidate_id: str,
    source_name: str,
    source_url: str,
    source_role: str,
    current_evidence: str,
    blocking_status: str,
    manual_verification_action: str,
    required_artifacts: str,
    acceptance_evidence: str,
    fail_closed_stop_rule: str,
) -> dict[str, str]:
    return {
        "action_rank": str(action_rank),
        "candidate_id": candidate_id,
        "source_name": source_name,
        "source_url": source_url,
        "source_role": source_role,
        "current_evidence": current_evidence,
        "blocking_status": blocking_status,
        "manual_verification_action": manual_verification_action,
        "required_artifacts": required_artifacts,
        "acceptance_evidence": acceptance_evidence,
        "fail_closed_stop_rule": fail_closed_stop_rule,
        "post_verification_commands": "python script/80_audit_alb2002_boundary_geometry_provenance.py; python script/81_build_alb2002_boundary_manual_verification_packet.py; python script/35_build_empirical_readiness_dashboard.py; python script/13_write_reports.py; python script/14_validate_workspace.py",
    }


def build_action_queue() -> list[dict[str, str]]:
    alternatives = source_by_id(read_csv_dicts(SOURCE_ALTERNATIVES_PATH))
    resources = resource_by_id(read_csv_dicts(RESOURCE_SEARCH_PATH))
    followups = source_by_id(read_csv_dicts(FOLLOWUP_AUDIT_PATH))
    geometry = read_csv_dicts(GEOMETRY_SUMMARY_PATH)
    local_geo = read_csv_dicts(LOCAL_GEO_SUMMARY_PATH)
    boundary_year = metric_value(geometry, "alb2002_boundary_geometry_metadata_boundary_year", "missing")
    boundary_source = metric_value(geometry, "alb2002_boundary_geometry_metadata_boundary_source", "missing")
    coordinate_rows = metric_value(local_geo, "alb2002_local_geo_artifact_coordinate_raw_variable_rows", "0")
    questionnaire_coord_rows = metric_value(local_geo, "alb2002_local_geo_artifact_questionnaire_coordinate_field_rows", "0")

    wb = alternatives.get("worldbank_alb2002_lsms_study", {})
    instat = alternatives.get("instat_census_2001", {})
    ipums = alternatives.get("ipums_ihgis_alb2001", {})
    ipums_followup = followups.get("ipums_ihgis_alb2001", {})
    asig = alternatives.get("asig_geoportal_current", {})
    old_gb = resources.get("geoboundaries_2_0_1_adm2", {})
    hdx = resources.get("hdx_cod_ab_alb_2019_gazetteer_adm2", {})

    return [
        action_row(
            1,
            "worldbank_alb2002_lsms_study",
            wb.get("source_name", "World Bank Microdata Library ALB_2002 LSMS study page"),
            wb.get("source_url", "https://microdata.worldbank.org/catalog/86/study-description"),
            "official_survey_geography_and_raw_ancillary_artifacts",
            f"Study documentation flags EA maps/GPS intent; local raw coordinate-variable rows={coordinate_rows}; questionnaire coordinate fields={questionnaire_coord_rows}.",
            "blocked_official_geography_artifact_not_obtained",
            "Use the Microdata Library terms/account workflow or study contact route to request/download all ALB_2002 geography ancillary files, GPS files, EA maps, district/commune codebooks, and sampling-frame documentation.",
            "Original geography/GPS/EA-map files, codebooks, data dictionaries, sampling-frame documentation, and any license/terms text.",
            "A file-level manifest with checksums plus raw schema/value audit proves whether coordinate variables, EA identifiers, or official district/commune boundaries join to ALB_2002 household IDs or district codes.",
            "If no official geography/GPS/EA-map artifact is available, ALB_2002 remains admin-name-only and cannot be promoted to climate linkage.",
        ),
        action_row(
            2,
            "instat_census_2001",
            instat.get("source_name", "INSTAT Census of Population and Housing page"),
            instat.get("source_url", "https://www.instat.gov.al/en/themes/censuses/census-of-population-and-housing/"),
            "official_2001_census_boundary_or_cartography_source",
            instat.get("local_or_page_evidence", "2001 census context was detected, but no district GIS artifact was verified."),
            "blocked_official_2001_boundary_file_not_verified",
            "Search/request 2001 census district, commune, EA, or cartography boundary files from INSTAT, including documentation for unit definitions and codes.",
            "Official 2001/2002 boundary files or cartographic tables, unit definitions, code lists, coordinate reference system/projection metadata, and license terms.",
            "Feature count, names/codes, vintage, and documented unit definitions reconcile to the 36 observed ALB_2002 district groups or a documented lower-level crosswalk.",
            "If only broad census context or post-2013 administrative geography is available, do not treat it as a 2002 LSMS boundary source.",
        ),
        action_row(
            3,
            "ipums_ihgis_alb2001",
            ipums.get("source_name", "IPUMS IHGIS Albania 2001 census GIS boundary files"),
            ipums.get("source_url", "https://ihgis.ipums.org/geography-gis"),
            "historical_census_gis_candidate",
            ipums_followup.get("source_catalog_evidence")
            or ipums.get("local_or_page_evidence", "Historical GIS catalog lead exists, but access/level/join keys are unverified."),
            ipums_followup.get("verified_blocker_status") or "blocked_historical_gis_level_and_access_not_verified",
            "Treat the visible IHGIS catalog evidence as non-sufficient for ALB_2002 district climate linkage; revisit only if a separate Albania 2001 district/g2 boundary file or documented crosswalk is found.",
            "Downloaded district/g2 GIS files if available, metadata on level/vintage, unit count, join keys, license, and any access requirements.",
            "The layer is district-level or can be losslessly crosswalked to ALB_2002 district codes/names with 36/36 coverage and verified 2001 vintage.",
            "If IHGIS only provides prefecture/g1 tabulation units, restricted access, or no compatible join keys, it cannot support ALB_2002 climate linkage.",
        ),
        action_row(
            4,
            "geoboundaries_2_0_1_adm2",
            old_gb.get("source_name", "geoBoundaries 2.0.1 Albania ADM2 GeoJSON"),
            old_gb.get("source_url", "https://www.geoboundaries.org/data/geoBoundaries-2_0_1/ALB/ADM2/geoBoundaries-2_0_1-ALB-ADM2.geojson"),
            "best_public_name_coverage_lead_not_historical_verified",
            f"Complete name coverage found, but companion metadata reports boundaryYear={boundary_year}; source={boundary_source}.",
            "blocked_boundary_year_2013_not_verified_2002",
            "Investigate source history and external official documentation to determine whether the 2013 OSM/Wambacher ADM2 geometries exactly reproduce 2001/2002 district boundaries.",
            "Version history, source lineage, official crosswalk/continuity documentation, geometry comparison evidence, topology validation, and exact code/name crosswalk.",
            "A documented official or source-history record proves the 2013 geometry is valid for 2002 LSMS district aggregation or quantifies acceptable boundary continuity and measurement error.",
            "Name coverage alone is insufficient; if vintage continuity cannot be proven, this lead remains a manual review lead only.",
        ),
        action_row(
            5,
            "asig_geoportal_current",
            asig.get("source_name", "ASIG Geoportal Albania data catalog"),
            asig.get("source_url", "https://geoportal.asig.gov.al/en/data"),
            "official_current_geoportal_possible_historical_catalog",
            asig.get("local_or_page_evidence", "Current official geoportal lead exists, but the automated probe did not verify historical data."),
            "blocked_geoportal_historical_2002_layer_not_verified",
            "Manually search ASIG/official geoportal for historical administrative or census cartography layers around 2001/2002, not only current local-government divisions.",
            "Historical layer metadata, download file, year/vintage, unit definitions, codes, projection, and license.",
            "Official historical layer has compatible district/commune/EA units and join keys for ALB_2002.",
            "Current/post-2019 layers do not pass unless a documented historical crosswalk supports aggregation to 2002 districts.",
        ),
        action_row(
            6,
            "hdx_cod_ab_alb_2019_gazetteer_adm2",
            hdx.get("source_name", "HDX COD-AB Albania 2019 gazetteer ADM2 sheet"),
            hdx.get("source_url", "https://data.humdata.org/dataset/cod-ab-alb"),
            "current_2019_administrative_reference_only",
            hdx.get("blocking_reason", "2019 municipality units do not match the 36 ALB_2002 district groups."),
            "blocked_2019_municipality_units_not_2002_lsms_districts",
            "Use only as a current reference unless a documented historical crosswalk maps 2002 districts to 2019 municipality units and supports measurement-error analysis.",
            "Historical crosswalk table, unit definitions, evidence of split/merge changes, and aggregation weights if using current municipalities.",
            "A documented crosswalk covers all 36 ALB_2002 district groups and explicitly justifies any current-boundary aggregation.",
            "Do not use the 2019 gazetteer as a substitute for 2002 district boundaries.",
        ),
        action_row(
            7,
            "unece_instat_2011_gis_paper",
            "UNECE/INSTAT 2011 census GIS implementation paper",
            "https://unece.org/fileadmin/DAM/stats/documents/ece/ces/ge.50/2014/Topic_3_Albania_Shameti.pdf",
            "official_statistical_system_evidence_on_pre2011_digital_map_absence",
            "UNECE/INSTAT paper reports that 2001 census maps were paper-based and that no national digital maps/spatial database existed before the 2011 census GIS build.",
            "blocked_pre2011_digital_boundary_source_absence_documented",
            "Use this source as negative evidence when evaluating whether current or post-2011 public GIS layers can be treated as 2002 LSMS district boundaries; continue only with actual official 2001/2002 artifacts or a documented historical crosswalk.",
            "Official paper plus any follow-up INSTAT/World Bank geography artifacts, district/commune/EA code lists, and boundary files if later obtained.",
            "A separate source must prove a 2001/2002 district-compatible boundary or crosswalk despite the documented lack of pre-2011 national digital maps.",
            "If no such source is obtained, do not promote ALB_2002 district climate linkage from current/post-2011 GIS layers.",
        ),
    ]


def gate_row(
    gate_id: str,
    gate_label: str,
    current_status: str,
    current_evidence: str,
    required_evidence_to_pass: str,
    promotion_effect_if_passed: str,
    fail_closed_stop_rule: str,
) -> dict[str, str]:
    return {
        "gate_id": gate_id,
        "gate_label": gate_label,
        "current_status": current_status,
        "current_evidence": current_evidence,
        "required_evidence_to_pass": required_evidence_to_pass,
        "promotion_effect_if_passed": promotion_effect_if_passed,
        "fail_closed_stop_rule": fail_closed_stop_rule,
    }


def build_gate_checklist() -> list[dict[str, str]]:
    geometry = read_csv_dicts(GEOMETRY_SUMMARY_PATH)
    local_geo = read_csv_dicts(LOCAL_GEO_SUMMARY_PATH)
    crosswalk = read_csv_dicts(CROSSWALK_SUMMARY_PATH)
    feature_rows = metric_value(geometry, "alb2002_boundary_geometry_feature_rows", "0")
    structure_ok = metric_value(geometry, "alb2002_boundary_geometry_coordinate_structure_ok_rows", "0")
    matched_rows = metric_value(geometry, "alb2002_boundary_geometry_survey_key_matched_rows", "0")
    boundary_year = metric_value(geometry, "alb2002_boundary_geometry_metadata_boundary_year", "missing")
    topology_rows = metric_value(geometry, "alb2002_boundary_geometry_topology_validated_rows", "0")
    coord_rows = metric_value(local_geo, "alb2002_local_geo_artifact_coordinate_raw_variable_rows", "0")
    local_boundary_rows = metric_value(local_geo, "alb2002_local_geo_artifact_local_boundary_ready_rows", "0")
    district_rows = metric_value(crosswalk, "alb2002_district_crosswalk_district_rows", "0")
    survey_month_rows = metric_value(crosswalk, "alb2002_district_crosswalk_survey_month_rows", "0")
    interview_date_rows = metric_value(crosswalk, "alb2002_district_crosswalk_interview_date_rows", "0")
    return [
        gate_row(
            "survey_timing_and_admin_keys",
            "Survey timing and observed district keys exist",
            "candidate_evidence_present_not_sufficient_for_climate_linkage",
            f"district_groups={district_rows}; survey_month_rows={survey_month_rows}; interview_date_rows={interview_date_rows}",
            "Raw household IDs, district codes/names, survey month/date, weights, and codebook meanings are verified and preserved in a non-promoted audit layer.",
            "Allows continued geography verification; does not by itself permit climate extraction.",
            "If district or timing variables cannot be joined at household level, stop ALB_2002 climate linkage.",
        ),
        gate_row(
            "boundary_name_coverage",
            "Candidate boundary names cover all observed ALB_2002 districts",
            "candidate_evidence_present_not_sufficient_for_promotion",
            f"candidate_features={feature_rows}; survey_key_matched_rows={matched_rows}",
            "All observed district names/codes match boundary features with documented encoding and alias decisions.",
            "Allows provenance/topology review of the candidate boundary source.",
            "If names/codes cannot be reconciled 36/36, stop admin-level climate linkage.",
        ),
        gate_row(
            "boundary_geometry_structure",
            "Candidate geometry coordinate structure is parseable",
            "candidate_evidence_present_topology_not_validated",
            f"coordinate_structure_ok_rows={structure_ok}; topology_validated_rows={topology_rows}",
            "A GIS/topology validator confirms valid polygons, no overlaps/gaps relevant to aggregation, correct CRS, and reproducible geometry checks.",
            "Allows candidate polygons to enter a climate-linkage input only after vintage and crosswalk gates also pass.",
            "Coordinate parsing without topology validation is not enough for climate extraction.",
        ),
        gate_row(
            "boundary_vintage",
            "Boundary vintage is valid for 2002 LSMS fieldwork",
            "blocked_boundary_year_not_2002",
            f"candidate metadata boundaryYear={boundary_year}",
            "Metadata or official documentation proves 2001/2002 boundary vintage, or proves the 2013 geometry exactly reproduces 2002 district boundaries with documented continuity.",
            "Allows historical-boundary gate to proceed if topology and crosswalk also pass.",
            "If vintage remains 2013/current or undocumented, climate linkage remains blocked.",
        ),
        gate_row(
            "official_provenance",
            "Boundary source provenance is official or historically defensible",
            "blocked_osm_wambacher_not_official_2002_source",
            f"candidate source={metric_value(geometry, 'alb2002_boundary_geometry_metadata_boundary_source', 'missing')}",
            "Source provenance is official census/LSMS/government geography or a defensible historical GIS source with compatible units and license.",
            "Allows reviewer-facing source justification.",
            "OpenStreetMap/Wambacher provenance alone is not a verified 2002 LSMS sampling-frame source.",
        ),
        gate_row(
            "raw_code_crosswalk",
            "Raw ALB_2002 district codes crosswalk to boundary features",
            "blocked_no_official_code_crosswalk",
            f"name matches exist={matched_rows}; official code crosswalk rows=0",
            "A district-code/name crosswalk joins every raw ALB_2002 district code to one boundary feature, with encoding decisions documented.",
            "Allows deterministic admin-level merge key construction if all other gates pass.",
            "Name-only matching without official code/key validation cannot be promoted.",
        ),
        gate_row(
            "coordinate_or_ea_artifact",
            "Household/cluster GPS or EA-map artifact is available if point or EA linkage is intended",
            "blocked_raw_coordinate_or_ea_artifact_absent",
            f"raw coordinate variable rows={coord_rows}; local boundary-ready rows={local_boundary_rows}",
            "Raw coordinate file, EA map, or EA-to-boundary/centroid crosswalk is obtained, checksummed, and joined to raw IDs.",
            "Would allow point/EA climate linkage or a more precise alternative to district aggregation.",
            "Questionnaire coordinate fields without raw coordinate values are not sufficient.",
        ),
        gate_row(
            "admin_measurement_error",
            "No-GPS admin aggregation measurement error is specified",
            "blocked_until_boundary_and_crosswalk_pass",
            "Only district-level candidate geography is available; no GPS displacement/buffer evidence exists.",
            "If district aggregation is used, the report specifies exposure misclassification, area aggregation method, sensitivity to centroids/polygons, and lower causal claim strength.",
            "Allows climate extraction protocol to document uncertainty after historical boundary gates pass.",
            "Do not call exposure household-level or point-level when using admin polygons.",
        ),
        gate_row(
            "climate_linkage_promotion",
            "ALB_2002 geography may be promoted to climate-linkage input",
            "blocked_not_ready_for_climate_linkage",
            "At least one upstream gate remains blocked: boundary vintage, official provenance, topology validation, raw code crosswalk, and coordinate/EA artifact.",
            "All required gates above pass with machine-readable evidence and reviewer-readable documentation.",
            "Only then create a temp climate-linkage input; write to data/ only after outcome and harmonization gates also pass.",
            "If any required gate remains blocked, keep climate_linkage_ready=0 and do not construct climate exposures.",
        ),
    ]


def summary_row(metric: str, value: Any, interpretation: str) -> dict[str, str]:
    return {"metric": metric, "value": "" if value is None else str(value), "interpretation": interpretation}


def build_summary(actions: list[dict[str, str]], gates: list[dict[str, str]]) -> list[dict[str, str]]:
    blocked_gates = sum(1 for row in gates if row["current_status"].startswith("blocked"))
    candidate_gates = sum(1 for row in gates if row["current_status"].startswith("candidate"))
    return [
        summary_row("alb2002_boundary_manual_verification_action_rows", len(actions), "Manual source/action rows for resolving the ALB_2002 geography blocker."),
        summary_row("alb2002_boundary_manual_verification_gate_rows", len(gates), "Promotion-gate checklist rows for ALB_2002 boundary verification."),
        summary_row("alb2002_boundary_manual_verification_candidate_evidence_gates", candidate_gates, "Gates with candidate evidence that is useful but insufficient for promotion."),
        summary_row("alb2002_boundary_manual_verification_blocked_gates", blocked_gates, "Gates still blocked before any ALB_2002 climate linkage."),
        summary_row("alb2002_boundary_manual_verification_high_priority_actions", sum(1 for row in actions if int(row["action_rank"]) <= 3), "Top-priority manual actions: World Bank geography artifacts, INSTAT 2001 boundary files, and IHGIS historical GIS."),
        summary_row("alb2002_boundary_manual_verification_pre2011_digital_map_absence_rows", sum(1 for row in actions if row["candidate_id"] == "unece_instat_2011_gis_paper"), "Negative-evidence source rows documenting that pre-2011 national digital maps were absent."),
        summary_row("alb2002_boundary_manual_verification_climate_linkage_ready_rows", 0, "Rows ready for climate-linkage promotion after this packet; intentionally zero."),
        summary_row("alb2002_boundary_manual_verification_current_decision", DECISION, "Current fail-closed decision for ALB_2002 manual boundary verification."),
    ]


def markdown_rows(rows: list[dict[str, str]], columns: list[str], limit: int = 20) -> str:
    lines = ["| " + " | ".join(columns) + " |", "|" + "|".join("---" for _ in columns) + "|"]
    for row in rows[:limit]:
        values = []
        for column in columns:
            value = (row.get(column, "") or "").replace("|", "/")
            if len(value) > 120:
                value = value[:117] + "..."
            values.append(value)
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines)


def write_report(actions: list[dict[str, str]], gates: list[dict[str, str]], summary: list[dict[str, str]]) -> None:
    summary_table = "\n".join(f"| {row['metric']} | {row['value']} | {row['interpretation']} |" for row in summary)
    REPORT_PATH.write_text(
        f"""# ALB_2002 Boundary Manual Verification Packet

Status: manual verification packet only. This packet turns the ALB_2002 geography blocker into source-specific actions and pass/fail promotion gates. It does not download new restricted files, does not write `data/`, does not construct centroids or climate exposures, and does not promote any ALB_2002 boundary to analysis-ready status.

## Summary

| Metric | Value | Interpretation |
|---|---:|---|
{summary_table}

## Manual Action Queue

{markdown_rows(actions, ['action_rank', 'candidate_id', 'source_role', 'blocking_status', 'manual_verification_action'], 20)}

## Promotion Gate Checklist

{markdown_rows(gates, ['gate_id', 'current_status', 'current_evidence', 'required_evidence_to_pass'], 20)}

## Interpretation

- ALB_2002 remains the strongest local geography lead because survey timing and district keys exist and the geoBoundaries 2.0.1 lead has complete name coverage.
- The current blocker is narrower and harder: boundary vintage/provenance, official 2001/2002 source status, topology validation, raw district-code crosswalk, and missing GPS/EA artifacts.
- The packet prioritizes World Bank ALB_2002 geography/GPS/EA-map artifacts, official INSTAT 2001 census boundary/cartography sources, and IHGIS Albania 2001 historical GIS verification.
- The UNECE/INSTAT GIS implementation paper is negative evidence: it documents the absence of national digital maps/spatial database before the 2011 census GIS build, so current or post-2011 layers need separate historical crosswalk proof before any ALB_2002 use.
- Climate-linkage-ready rows remain zero.

## Machine-Readable Outputs

- `temp/alb2002_boundary_manual_verification_action_queue.csv`
- `temp/alb2002_boundary_promotion_gate_checklist.csv`
- `result/alb2002_boundary_manual_verification_packet_summary.csv`
""",
        encoding="utf-8",
    )


def main() -> None:
    ensure_dirs()
    actions = build_action_queue()
    gates = build_gate_checklist()
    summary = build_summary(actions, gates)
    write_csv(ACTION_QUEUE_PATH, actions, ACTION_COLUMNS)
    write_csv(PROMOTION_GATE_PATH, gates, GATE_COLUMNS)
    write_csv(SUMMARY_PATH, summary, SUMMARY_COLUMNS)
    write_report(actions, gates, summary)
    append_log(
        TEMP_DIR / "audit_log.md",
        f"Built ALB_2002 boundary manual verification packet actions={len(actions)} gates={len(gates)} decision={DECISION}.",
    )
    print(f"ALB_2002 boundary manual verification packet actions={len(actions)} gates={len(gates)} decision={DECISION}.")


if __name__ == "__main__":
    main()
