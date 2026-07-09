from __future__ import annotations

import csv
import math
import urllib.error
import urllib.request
from html import unescape
from pathlib import Path
from typing import Any

from common import REPORT_DIR, RESULT_DIR, TEMP_DIR, append_log, ensure_dirs, write_csv


SOURCE_ALTERNATIVES_PATH = TEMP_DIR / "alb2002_boundary_source_alternative_audit.csv"
RESOURCE_SEARCH_PATH = TEMP_DIR / "alb2002_boundary_source_resource_search_audit.csv"
GEOMETRY_SUMMARY_PATH = RESULT_DIR / "alb2002_boundary_geometry_provenance_summary.csv"
ACTION_QUEUE_PATH = TEMP_DIR / "alb2002_boundary_manual_verification_action_queue.csv"

AUDIT_PATH = TEMP_DIR / "alb2002_boundary_manual_source_followup_audit.csv"
SUMMARY_PATH = RESULT_DIR / "alb2002_boundary_manual_source_followup_summary.csv"
REPORT_PATH = REPORT_DIR / "alb2002_boundary_manual_source_followup.md"

DECISION = "blocked_followup_confirms_no_public_2002_district_boundary_source"
RUN_DATE = "2026-07-09"

AUDIT_COLUMNS = [
    "candidate_id",
    "source_name",
    "source_url",
    "followup_method",
    "page_probe_status",
    "http_status",
    "source_catalog_evidence",
    "boundary_level_claim",
    "required_level",
    "level_compatibility_status",
    "verified_blocker_status",
    "historical_2002_boundary_ready",
    "climate_linkage_ready",
    "promotion_status",
    "reviewer_interpretation",
    "next_action",
]
SUMMARY_COLUMNS = ["metric", "value", "interpretation"]


def fmt(value: Any) -> str:
    if value is None:
        return ""
    try:
        if math.isnan(value):
            return ""
    except TypeError:
        pass
    if isinstance(value, float):
        if value.is_integer():
            return str(int(value))
        return f"{value:.6g}"
    return str(value)


def read_csv_dicts(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def metric_value(rows: list[dict[str, str]], metric: str, default: str = "") -> str:
    for row in rows:
        if row.get("metric") == metric:
            return row.get("value", default)
    return default


def rows_by_id(rows: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    return {row.get("candidate_id", ""): row for row in rows if row.get("candidate_id")}


def safe_get_page(url: str, max_bytes: int = 350_000) -> tuple[str, str, str]:
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) climate-uhc-ml-audit/1.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Range": f"bytes=0-{max_bytes - 1}",
        },
        method="GET",
    )
    try:
        with urllib.request.urlopen(request, timeout=35) as response:
            status = str(getattr(response, "status", ""))
            content_type = response.headers.get("Content-Type", "")
            body = response.read(max_bytes + 1)
        charset = "utf-8"
        if "charset=" in content_type.lower():
            charset = content_type.lower().split("charset=", 1)[1].split(";", 1)[0].strip() or "utf-8"
        text = unescape(body.decode(charset, errors="replace"))
        return "reachable_page_sampled", status, " ".join(text.split())
    except urllib.error.HTTPError as exc:
        return "blocked_http_error", str(exc.code), str(exc)
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        return "blocked_unreachable", "", str(exc)


def probe_page_flags(candidate_id: str, url: str) -> tuple[str, str, str]:
    if not url:
        return "not_probed_missing_url", "", ""
    if candidate_id == "unece_instat_2011_gis_paper":
        return "static_official_pdf_evidence_recorded", "", "pre2011_digital_map_absence_evidence_encoded"
    status, http_status, text = safe_get_page(url)
    lower = text.lower()
    flags: list[str] = []
    if candidate_id == "ipums_ihgis_alb2001":
        if "albania 2001 population census" in lower:
            flags.append("albania_2001_population_census_seen")
        if "prefectures (g1)" in lower:
            flags.append("prefectures_g1_seen")
        if "districts (g2)" in lower and "albania 2001" in lower:
            flags.append("possible_albania_g2_text_seen")
    if candidate_id == "worldbank_alb2002_lsms_study":
        if "maps identifying the boundaries" in lower:
            flags.append("ea_boundary_maps_documented")
        if "longitude and latitude" in lower or "gps" in lower:
            flags.append("gps_or_coordinates_documented")
    if candidate_id == "instat_census_2001" and ("2001" in lower or "census" in lower):
        flags.append("census_context_seen")
    if candidate_id == "asig_geoportal_current" and ("geoportal" in lower or "asig" in lower):
        flags.append("geoportal_context_seen")
    return status, http_status, ";".join(flags)


def static_catalog_evidence(candidate_id: str, geometry: list[dict[str, str]], source: dict[str, str], resource: dict[str, str]) -> tuple[str, str, str, str, str]:
    boundary_year = metric_value(geometry, "alb2002_boundary_geometry_metadata_boundary_year", "missing")
    boundary_source = metric_value(geometry, "alb2002_boundary_geometry_metadata_boundary_source", "missing")
    if candidate_id == "worldbank_alb2002_lsms_study":
        return (
            "Official study page evidence and prior audit document ALB_2002 sampling/EA-map/GPS intent, but no direct public GIS/GPS/EA-map artifact has been obtained in the workspace.",
            "survey ancillary geography may exist, artifact not obtained",
            "raw household district code plus official geography/GPS/EA-map artifact or code crosswalk",
            "blocked_artifact_access_not_level_proven",
            "Request or download official ALB_2002 geography/GPS/EA-map files through the Microdata Library access route before any climate-linkage promotion.",
        )
    if candidate_id == "instat_census_2001":
        return (
            "Official INSTAT census context is useful, but the current audit still has no public 2001 district, commune, EA, or cartography boundary file with join keys.",
            "official census context only",
            "2001/2002 district, commune, or EA boundary file with unit definitions and codes",
            "blocked_context_without_boundary_file",
            "Search or request official 2001 cartography/boundary artifacts; do not promote census context alone.",
        )
    if candidate_id == "ipums_ihgis_alb2001":
        return (
            "Browser-visible IHGIS Geography & GIS catalog evidence on 2026-07-09 lists Albania 2001 Population Census (AL2001pop) with Prefectures (g1) only; no Albania 2001 district/g2 row was visible in the catalog evidence reviewed.",
            "prefectures g1 only in visible catalog evidence",
            "district/g2 or lower geography that can cover the 36 ALB_2002 LSMS district groups",
            "blocked_prefecture_g1_not_36_lsms_districts",
            "Treat IHGIS as non-sufficient unless a separate Albania 2001 district/g2 boundary file or crosswalk is found.",
        )
    if candidate_id == "geoboundaries_2_0_1_adm2":
        return (
            f"geoBoundaries 2.0.1 has complete ALB_2002 name coverage, but companion metadata reports boundaryYear={boundary_year} and source={boundary_source}.",
            f"ADM2 geometry with boundaryYear {boundary_year}",
            "verified 2001/2002 district boundary vintage or documented continuity from 2002 to the candidate geometry",
            "blocked_boundary_year_2013_not_verified_2002",
            "Use only as a name-coverage and geometry lead until historical vintage/continuity and code crosswalk evidence pass.",
        )
    if candidate_id == "asig_geoportal_current":
        return (
            "ASIG remains an official geoportal lead, but no historical 2001/2002 district layer was verified by the current automated audit.",
            "official current geoportal lead",
            "historical 2001/2002 layer metadata plus file download, codes, projection, and license",
            "blocked_historical_layer_not_verified",
            "Manually search/request historical administrative or census cartography layers, not current-only local-government divisions.",
        )
    if candidate_id == "hdx_cod_ab_alb_2019_gazetteer_adm2":
        return (
            resource.get("blocking_reason", "HDX COD-AB Albania is a current/post-2019 administrative reference and not the 36-district ALB_2002 boundary layer."),
            "2019 municipality-style ADM2 reference",
            "2001/2002 district boundary or documented historical crosswalk with split/merge evidence",
            "blocked_2019_units_not_2002_lsms_districts",
            "Use only as a current reference unless a historical district-to-municipality crosswalk is documented.",
        )
    if candidate_id == "unece_instat_2011_gis_paper":
        return (
            "UNECE/INSTAT GIS implementation paper reports that Albania's 2001 census maps were paper-based and that no national digital maps/spatial database existed before the 2011 census GIS build.",
            "negative evidence on pre-2011 national digital map availability",
            "actual official 2001/2002 district-compatible boundary, EA map, GPS artifact, or documented historical crosswalk despite the pre-2011 digital-map absence",
            "blocked_pre2011_digital_boundary_source_absence_documented",
            "Treat current/post-2011 public GIS layers as non-sufficient for ALB_2002 unless separate historical continuity or official boundary evidence is obtained.",
        )
    return (
        source.get("current_evidence", "No specific follow-up evidence was encoded for this source."),
        "unverified",
        "verified 2001/2002 LSMS-compatible boundary or coordinate artifact",
        "blocked_unverified_source",
        "Keep blocked until source-specific evidence is obtained.",
    )


def audit_row(candidate: dict[str, str], source_lookup: dict[str, dict[str, str]], resource_lookup: dict[str, dict[str, str]], geometry: list[dict[str, str]]) -> dict[str, str]:
    candidate_id = candidate.get("candidate_id", "")
    source_url = candidate.get("source_url", "")
    source = source_lookup.get(candidate_id, {})
    resource = resource_lookup.get(candidate_id, {})
    page_status, http_status, page_flags = probe_page_flags(candidate_id, source_url)
    evidence, boundary_level, required_level, blocker, next_action = static_catalog_evidence(candidate_id, geometry, source, resource)
    if page_flags:
        evidence = f"{evidence} Local page probe flags: {page_flags}."
    compatibility = "not_compatible_with_alb2002_district_climate_linkage"
    if candidate_id == "geoboundaries_2_0_1_adm2":
        compatibility = "name_coverage_candidate_but_historical_vintage_blocked"
    elif candidate_id == "worldbank_alb2002_lsms_study":
        compatibility = "potentially_compatible_if_restricted_ancillary_artifacts_obtained"
    elif candidate_id == "instat_census_2001":
        compatibility = "potentially_compatible_if_boundary_file_obtained"
    return {
        "candidate_id": candidate_id,
        "source_name": candidate.get("source_name", ""),
        "source_url": source_url,
        "followup_method": f"local_page_probe_plus_source_catalog_evidence_{RUN_DATE}",
        "page_probe_status": page_status,
        "http_status": http_status,
        "source_catalog_evidence": evidence,
        "boundary_level_claim": boundary_level,
        "required_level": required_level,
        "level_compatibility_status": compatibility,
        "verified_blocker_status": blocker,
        "historical_2002_boundary_ready": "0",
        "climate_linkage_ready": "0",
        "promotion_status": "blocked_not_ready_for_climate_linkage",
        "reviewer_interpretation": "Follow-up evidence narrows the source-specific blocker but does not produce an analysis-ready ALB_2002 climate boundary.",
        "next_action": next_action,
    }


def summary_row(metric: str, value: Any, interpretation: str) -> dict[str, str]:
    return {"metric": metric, "value": "" if value is None else str(value), "interpretation": interpretation}


def build_summary(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    reachable = sum(1 for row in rows if row["page_probe_status"] == "reachable_page_sampled")
    static_ipums = next((row for row in rows if row["candidate_id"] == "ipums_ihgis_alb2001"), {})
    static_unece = next((row for row in rows if row["candidate_id"] == "unece_instat_2011_gis_paper"), {})
    return [
        summary_row("alb2002_boundary_manual_source_followup_rows", len(rows), "Manual-source follow-up rows for ALB_2002 boundary verification leads."),
        summary_row("alb2002_boundary_manual_source_followup_reachable_page_rows", reachable, "Rows whose source page was reachable during the local follow-up probe."),
        summary_row("alb2002_boundary_manual_source_followup_conclusive_blocker_rows", sum(1 for row in rows if row["verified_blocker_status"].startswith("blocked")), "Rows with a source-specific blocker documented."),
        summary_row("alb2002_boundary_manual_source_followup_district_level_ready_rows", 0, "Rows verified as 36-district or lower ALB_2002-compatible geography sources after follow-up; intentionally zero."),
        summary_row("alb2002_boundary_manual_source_followup_climate_linkage_ready_rows", 0, "Rows ready for ALB_2002 climate-linkage promotion after follow-up; intentionally zero."),
        summary_row("alb2002_boundary_manual_source_followup_ipums_level_status", static_ipums.get("verified_blocker_status", "missing"), "IHGIS follow-up status after browser-visible catalog review."),
        summary_row("alb2002_boundary_manual_source_followup_unece_pre2011_map_status", static_unece.get("verified_blocker_status", "missing"), "UNECE/INSTAT follow-up status on pre-2011 national digital map availability."),
        summary_row("alb2002_boundary_manual_source_followup_current_decision", DECISION, "Current fail-closed decision after manual-source follow-up."),
    ]


def markdown_rows(rows: list[dict[str, str]]) -> str:
    columns = ["candidate_id", "page_probe_status", "verified_blocker_status", "boundary_level_claim", "next_action"]
    lines = ["| " + " | ".join(columns) + " |", "|" + "|".join("---" for _ in columns) + "|"]
    for row in rows:
        values = []
        for column in columns:
            value = (row.get(column, "") or "").replace("|", "/")
            if len(value) > 110:
                value = value[:107] + "..."
            values.append(value)
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines)


def write_report(rows: list[dict[str, str]], summary: list[dict[str, str]]) -> None:
    summary_table = "\n".join(f"| {row['metric']} | {row['value']} | {row['interpretation']} |" for row in summary)
    REPORT_PATH.write_text(
        f"""# ALB_2002 Boundary Manual Source Follow-Up

Status: fail-closed follow-up audit. This report records source-specific evidence for the manual boundary verification queue. It does not download restricted files, does not create boundary centroids, and does not promote ALB_2002 to climate linkage.

## Summary

| Metric | Value | Interpretation |
|---|---:|---|
{summary_table}

## Source Follow-Up Rows

{markdown_rows(rows)}

## Interpretation

- IHGIS is no longer just an unresolved high-priority district candidate in this workspace. The browser-visible catalog evidence reviewed on {RUN_DATE} shows Albania 2001 Population Census GIS only at prefecture (`g1`) level, so it does not satisfy the 36-district ALB_2002 linkage requirement unless a separate district/g2 source is found.
- The UNECE/INSTAT GIS implementation paper is direct negative evidence for easy public historical GIS substitution: it reports paper-based 2001 census maps and no national digital maps/spatial database before the 2011 census GIS build.
- World Bank and INSTAT remain potentially relevant because they are official survey/census channels, but they still require actual geography/GPS/EA-map/boundary artifacts.
- geoBoundaries 2.0.1 remains useful for name coverage but blocked by 2013 vintage/provenance.
- HDX and ASIG remain current or unverified historical leads only.
- Climate-linkage-ready rows remain zero.

## Machine-Readable Outputs

- `temp/alb2002_boundary_manual_source_followup_audit.csv`
- `result/alb2002_boundary_manual_source_followup_summary.csv`
""",
        encoding="utf-8",
    )


def main() -> None:
    ensure_dirs()
    source_lookup = rows_by_id(read_csv_dicts(SOURCE_ALTERNATIVES_PATH))
    resource_lookup = rows_by_id(read_csv_dicts(RESOURCE_SEARCH_PATH))
    geometry = read_csv_dicts(GEOMETRY_SUMMARY_PATH)
    actions = read_csv_dicts(ACTION_QUEUE_PATH)
    if not actions:
        actions = [
            {"candidate_id": "worldbank_alb2002_lsms_study", "source_name": "World Bank Microdata Library ALB_2002 LSMS study page", "source_url": "https://microdata.worldbank.org/catalog/86/study-description"},
            {"candidate_id": "instat_census_2001", "source_name": "INSTAT Census of Population and Housing page", "source_url": "https://www.instat.gov.al/en/themes/censuses/census-of-population-and-housing/"},
            {"candidate_id": "ipums_ihgis_alb2001", "source_name": "IPUMS IHGIS Albania 2001 census GIS boundary files", "source_url": "https://ihgis.ipums.org/geography-gis"},
            {"candidate_id": "geoboundaries_2_0_1_adm2", "source_name": "geoBoundaries 2.0.1 Albania ADM2 GeoJSON", "source_url": "https://www.geoboundaries.org/data/geoBoundaries-2_0_1/ALB/ADM2/geoBoundaries-2_0_1-ALB-ADM2.geojson"},
            {"candidate_id": "asig_geoportal_current", "source_name": "ASIG Geoportal Albania data catalog", "source_url": "https://geoportal.asig.gov.al/en/data"},
            {"candidate_id": "hdx_cod_ab_alb_2019_gazetteer_adm2", "source_name": "HDX COD-AB Albania 2019 gazetteer ADM2 sheet", "source_url": "https://data.humdata.org/dataset/cod-ab-alb"},
            {"candidate_id": "unece_instat_2011_gis_paper", "source_name": "UNECE/INSTAT 2011 census GIS implementation paper", "source_url": "https://unece.org/fileadmin/DAM/stats/documents/ece/ces/ge.50/2014/Topic_3_Albania_Shameti.pdf"},
        ]
    rows = [audit_row(action, source_lookup, resource_lookup, geometry) for action in actions]
    summary = build_summary(rows)
    write_csv(AUDIT_PATH, rows, AUDIT_COLUMNS)
    write_csv(SUMMARY_PATH, summary, SUMMARY_COLUMNS)
    write_report(rows, summary)
    append_log(TEMP_DIR / "audit_log.md", f"Built ALB_2002 boundary manual source follow-up rows={len(rows)} decision={DECISION}.")
    print(f"ALB_2002 boundary manual source follow-up rows={len(rows)} decision={DECISION}.")


if __name__ == "__main__":
    main()
