from __future__ import annotations

import csv
import math
import urllib.error
import urllib.request
from html import unescape
from pathlib import Path
from typing import Any

from common import REPORT_DIR, RESULT_DIR, TEMP_DIR, append_log, ensure_dirs, write_csv


BOUNDARY_NAME_SUMMARY_PATH = RESULT_DIR / "alb2002_boundary_name_match_summary.csv"
CROSSWALK_SUMMARY_PATH = RESULT_DIR / "alb2002_district_climate_crosswalk_summary.csv"
GEOMETRY_SUMMARY_PATH = RESULT_DIR / "alb2002_boundary_geometry_provenance_summary.csv"
GEOMETRY_AUDIT_PATH = TEMP_DIR / "alb2002_boundary_geometry_provenance_audit.csv"
GEOJSON_INVENTORY_PATH = TEMP_DIR / "alb2002_boundary_geojson_inventory.csv"
GEOJSON_SNAPSHOT_PATH = TEMP_DIR / "source_snapshots" / "alb2002_geoboundaries_alb_adm2_current.geojson"
GEOBOUNDARIES_2013_URL = "https://www.geoboundaries.org/data/geoBoundaries-2_0_1/ALB/ADM2/geoBoundaries-2_0_1-ALB-ADM2.geojson"
AUDIT_PATH = TEMP_DIR / "alb2002_boundary_source_alternative_audit.csv"
SUMMARY_PATH = RESULT_DIR / "alb2002_boundary_source_alternative_summary.csv"
REPORT_PATH = REPORT_DIR / "alb2002_boundary_source_alternative_audit.md"

DECISION = "blocked_no_public_2002_district_boundary_source_verified"

AUDIT_COLUMNS = [
    "candidate_id",
    "source_name",
    "source_url",
    "source_type",
    "probe_method",
    "probe_status",
    "http_status",
    "content_type",
    "source_year_claim",
    "local_artifact",
    "local_artifact_rows",
    "page_evidence_flags",
    "local_or_page_evidence",
    "boundary_suitability_status",
    "historical_2002_boundary_ready",
    "climate_linkage_ready",
    "promotion_status",
    "blocking_reason",
    "next_review_action",
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


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(TEMP_DIR.parent)).replace("\\", "/")
    except ValueError:
        return str(path).replace("\\", "/")


def read_csv_dicts(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def row_count(path: Path) -> int:
    return len(read_csv_dicts(path))


def metric_value(rows: list[dict[str, str]], metric: str, default: str = "") -> str:
    for row in rows:
        if row.get("metric") == metric:
            return row.get("value", default)
    return default


def safe_get_page(url: str, max_bytes: int = 300_000) -> tuple[str, str, str, str]:
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "climate-uhc-ml-audit/1.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Range": f"bytes=0-{max_bytes - 1}",
        },
        method="GET",
    )
    try:
        with urllib.request.urlopen(request, timeout=25) as response:
            status = str(getattr(response, "status", ""))
            content_type = response.headers.get("Content-Type", "")
            body = response.read(max_bytes + 1)
        charset = "utf-8"
        if "charset=" in content_type.lower():
            charset = content_type.lower().split("charset=", 1)[1].split(";", 1)[0].strip() or "utf-8"
        text = unescape(body.decode(charset, errors="replace"))
        return "reachable_page_sampled", status, content_type, " ".join(text.split())
    except urllib.error.HTTPError as exc:
        return "blocked_http_error", str(exc.code), "", str(exc)
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        return "blocked_unreachable", "", "", str(exc)


def flags_for_text(text: str) -> str:
    lower = text.lower()
    flags: list[str] = []
    if "maps identifying the boundaries" in lower:
        flags.append("lsms_ea_boundary_maps_documented")
    if "longitude and latitude" in lower or "gps" in lower:
        flags.append("gps_or_coordinates_documented")
    if "census-al 2001" in lower or "census - 2001" in lower or "april 2001" in lower:
        flags.append("official_2001_census_context")
    if "albania 2001 population census" in lower:
        flags.append("albania_2001_census_boundary_context")
    if "prefecture" in lower and "albania 2001" in lower:
        flags.append("prefecture_level_not_district_confirmed")
    if "2015" in lower:
        flags.append("post_2002_or_current_boundary_context")
    if "2019" in lower or "29.05.2019" in lower:
        flags.append("post_2002_2019_boundary_context")
    return ";".join(flags)


def base_row(
    candidate_id: str,
    source_name: str,
    source_url: str,
    source_type: str,
    source_year_claim: str,
    evidence: str,
    suitability: str,
    blocking_reason: str,
    next_review_action: str,
    local_artifact: Path | None = None,
    page_probe: bool = True,
) -> dict[str, str]:
    if page_probe:
        probe_status, http_status, content_type, page_text = safe_get_page(source_url)
        if probe_status == "reachable_page_sampled":
            page_flags = flags_for_text(page_text)
            if page_text and not page_flags:
                evidence = f"{evidence} Page sampled, but no audit-ready 2002 district boundary evidence was detected in the sampled text."
            elif page_flags:
                evidence = f"{evidence} Page flags: {page_flags}."
        else:
            page_flags = ""
            detail = page_text[:180].replace("|", "/")
            evidence = f"{evidence} Page text was not sampled because the probe status is {probe_status}: {detail}"
    else:
        probe_status, http_status, content_type, page_flags = "local_artifact_review", "", "", ""

    artifact_rows = str(row_count(local_artifact)) if local_artifact is not None and local_artifact.exists() else "0"
    return {
        "candidate_id": candidate_id,
        "source_name": source_name,
        "source_url": source_url,
        "source_type": source_type,
        "probe_method": "GET_landing_page_sample_only_no_gis_download" if page_probe else "local_existing_artifact_review",
        "probe_status": probe_status,
        "http_status": http_status,
        "content_type": content_type,
        "source_year_claim": source_year_claim,
        "local_artifact": rel(local_artifact) if local_artifact is not None and local_artifact.exists() else "",
        "local_artifact_rows": artifact_rows,
        "page_evidence_flags": page_flags,
        "local_or_page_evidence": evidence,
        "boundary_suitability_status": suitability,
        "historical_2002_boundary_ready": "0",
        "climate_linkage_ready": "0",
        "promotion_status": "blocked_not_ready_for_climate_linkage",
        "blocking_reason": blocking_reason,
        "next_review_action": next_review_action,
    }


def current_geoboundaries_row() -> dict[str, str]:
    geometry_summary = read_csv_dicts(GEOMETRY_SUMMARY_PATH)
    geometry_features = metric_value(geometry_summary, "alb2002_boundary_geometry_feature_rows", "0")
    geometry_matches = metric_value(geometry_summary, "alb2002_boundary_geometry_survey_key_matched_rows", "0")
    geometry_year = metric_value(geometry_summary, "alb2002_boundary_geometry_metadata_boundary_year", "")
    geometry_source = metric_value(geometry_summary, "alb2002_boundary_geometry_metadata_boundary_source", "")
    geometry_ready = metric_value(geometry_summary, "alb2002_boundary_geometry_climate_linkage_ready_rows", "0")
    if geometry_summary and geometry_features != "0":
        evidence = (
            "Local geoBoundaries 2.0.1 geometry/provenance audit found "
            f"{geometry_features} ADM2 features and {geometry_matches} ALB_2002 survey district-key matches. "
            f"The companion metadata reports boundaryYear={geometry_year or 'missing'} and source={geometry_source or 'missing'}; "
            f"climate-linkage-ready rows remain {geometry_ready}."
        )
        return base_row(
            "geoboundaries_2_0_1_adm2",
            "geoBoundaries 2.0.1 Albania ADM2 geometry/provenance lead",
            GEOBOUNDARIES_2013_URL,
            "public_2013_boundary_geojson_local_snapshot",
            f"{geometry_year or 'missing'} boundary year per companion metadata",
            evidence,
            "blocked_complete_geometry_boundary_year_2013_not_verified_2002",
            "The candidate has complete 36-district name/key coverage, but its companion metadata reports a 2013 boundary year and OpenStreetMap/Wambacher provenance rather than a verified 2001/2002 LSMS or census district boundary source.",
            "Verify historical continuity or obtain an official 2001/2002 district, EA, or GPS artifact before any admin-level climate aggregation.",
            GEOMETRY_AUDIT_PATH if GEOMETRY_AUDIT_PATH.exists() else GEOJSON_INVENTORY_PATH,
            page_probe=False,
        )

    name_summary = read_csv_dicts(BOUNDARY_NAME_SUMMARY_PATH)
    crosswalk_summary = read_csv_dicts(CROSSWALK_SUMMARY_PATH)
    source_url = metric_value(
        name_summary,
        "alb2002_boundary_name_match_boundary_source_url",
        "https://github.com/wmgeolab/geoBoundaries/raw/9469f09/releaseData/gbOpen/ALB/ADM2/geoBoundaries-ALB-ADM2.geojson",
    )
    source_year = metric_value(name_summary, "alb2002_boundary_name_match_boundary_year_represented", "current_public_adm2")
    evidence = (
        "Local current-ADM2 GeoJSON audit found "
        f"{metric_value(name_summary, 'alb2002_boundary_name_match_geojson_feature_rows', '0')} features, "
        f"{metric_value(name_summary, 'alb2002_boundary_name_match_exact_rows', '0')} exact survey-name matches, "
        f"{metric_value(name_summary, 'alb2002_boundary_name_match_euro_repaired_rows', '0')} encoding-repaired match, "
        f"{metric_value(name_summary, 'alb2002_boundary_name_match_unmatched_survey_rows', '0')} unmatched survey district row, "
        f"and {metric_value(name_summary, 'alb2002_boundary_name_match_duplicate_boundary_name_keys', '0')} duplicate boundary-name keys. "
        f"The district crosswalk audit reports {metric_value(crosswalk_summary, 'alb2002_district_crosswalk_district_rows', '0')} observed survey district groups."
    )
    artifact = GEOJSON_INVENTORY_PATH if GEOJSON_INVENTORY_PATH.exists() else GEOJSON_SNAPSHOT_PATH
    return base_row(
        "geoboundaries_current_adm2",
        "geoBoundaries gbOpen Albania ADM2 current boundary snapshot",
        source_url,
        "public_current_boundary_geojson_local_snapshot",
        source_year,
        evidence,
        "blocked_current_boundary_name_match_incomplete_historical_crosswalk_no_gps",
        "Current boundary names are not a verified 2002 LSMS district boundary source; local audit still has one unmatched survey district, duplicate current-boundary names, no historical crosswalk, and no verified household or cluster coordinate linkage.",
        "Manually locate or obtain a 2001/2002 district or EA boundary/GPS artifact, then reconcile KORCE/Korce encoding, duplicate current-boundary names, district codes, projections, and no-GPS admin aggregation before any climate linkage.",
        artifact,
        page_probe=False,
    )


def build_rows() -> list[dict[str, str]]:
    rows = [current_geoboundaries_row()]
    rows.extend(
        [
            base_row(
                "hdx_cod_ab_alb",
                "HDX COD-AB Albania subnational administrative boundaries",
                "https://data.humdata.org/dataset/cod-ab-alb",
                "public_current_or_post2015_boundary_catalog",
                "2015 administrative boundaries per COD-AB catalog metadata/search result",
                "Candidate humanitarian COD-AB source; probed as an alternative public boundary catalog, not as an LSMS sampling-frame source.",
                "blocked_current_or_post2015_boundary_not_historical_2002_lsms",
                "The audit did not verify a 2001/2002 LSMS district or EA boundary file from this source, and current/post-2015 administrative units cannot be treated as 2002 survey districts.",
                "If used later, download only documented boundary metadata first, verify the represented administrative year, and build a district-code/name crosswalk against ALB_2002 before any climate aggregation.",
            ),
            base_row(
                "asig_geoportal_current",
                "ASIG Geoportal Albania data catalog",
                "https://geoportal.asig.gov.al/en/data",
                "official_current_boundary_geoportal",
                "updated current administrative map / 2019 local-government division metadata",
                "Official national geospatial catalog candidate; probed only for landing-page evidence.",
                "blocked_current_or_post2019_boundary_not_historical_2002_lsms",
                "The audit did not verify a public 2001/2002 LSMS district, EA, or GPS boundary artifact. Current official administrative maps are not automatically valid for 2002 LSMS district climate aggregation.",
                "Search ASIG/INSTAT for an explicit 2001 census district, commune, EA, or LSMS sampling-frame boundary layer and verify licensing, vintage, unit definitions, and code compatibility.",
            ),
            base_row(
                "worldbank_alb2002_lsms_study",
                "World Bank Microdata Library ALB_2002 LSMS study page",
                "https://microdata.worldbank.org/catalog/86/study-description",
                "official_survey_metadata_and_documentation",
                "2002 survey; sampling frame based on April 2001 census",
                "Official study description documents the ALB_2002 sampling frame, fieldwork period, EA maps, and GPS intent, but the current local audit has not found a directly usable public GIS/GPS artifact.",
                "blocked_lsms_sampling_geography_documented_no_direct_gis_artifact_verified",
                "Documentation evidence is not enough to construct climate exposure; the local audit still lacks a verified coordinate file or historical boundary layer joined to the household/admin codes.",
                "Inspect all ALB_2002 documentation/raw folders for GPS, EA map, district codebook, or boundary files; if unavailable, request official geography files through the Microdata Library terms workflow.",
            ),
            base_row(
                "instat_census_2001",
                "INSTAT Census of Population and Housing page",
                "https://www.instat.gov.al/en/themes/censuses/census-of-population-and-housing/",
                "official_census_context_catalog",
                "2001 census context present; no district GIS artifact verified by this audit",
                "Official INSTAT census page documents the 2001 Census context but no directly audited 2001 district boundary file was established here.",
                "blocked_official_census_context_no_public_district_gis_verified",
                "The source is relevant to the LSMS sampling frame but does not by itself provide a verified district polygon or EA boundary file that can be joined to ALB_2002.",
                "Search INSTAT publications/downloads for 2001 district, commune, EA, or census cartography products, then verify geography level and join keys.",
            ),
            base_row(
                "ipums_ihgis_alb2001",
                "IPUMS IHGIS Albania 2001 census GIS boundary files",
                "https://ihgis.ipums.org/geography-gis",
                "historical_census_boundary_catalog_candidate",
                "Albania 2001 Population Census boundary context; level not verified as LSMS district by this audit",
                "IHGIS is a useful historical census GIS candidate, but the current audit has not verified that its available Albania 2001 geography is the ALB_2002 district boundary needed for LSMS district-code linkage.",
                "blocked_historical_census_candidate_not_lsms_district_crosswalk_verified",
                "A historical census boundary catalog can still be unsuitable if it is only prefecture/tabulation geography, lacks district-level units, or lacks join keys compatible with ALB_2002 raw district codes.",
                "Manually verify available IHGIS Albania 2001 boundary level, unit count, licensing, download requirements, and whether join keys/names can be reconciled to the 36 observed ALB_2002 district groups.",
            ),
        ]
    )
    return rows


def summary_row(metric: str, value: Any, interpretation: str) -> dict[str, str]:
    return {"metric": metric, "value": fmt(value), "interpretation": interpretation}


def build_summary(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    reachable = sum(1 for row in rows if row["probe_status"] == "reachable_page_sampled" or row["probe_status"] == "local_artifact_review")
    current_or_post2015 = sum(
        1
        for row in rows
        if "current" in row["boundary_suitability_status"] or "post2015" in row["boundary_suitability_status"] or "post2019" in row["boundary_suitability_status"]
    )
    lsms_maps_documented = sum(1 for row in rows if "lsms_ea_boundary_maps_documented" in row["page_evidence_flags"])
    gps_documented = sum(1 for row in rows if "gps_or_coordinates_documented" in row["page_evidence_flags"])
    historical_candidate = sum(1 for row in rows if "historical" in row["source_type"] or "2001" in row["source_year_claim"])
    return [
        summary_row("alb2002_boundary_source_alternative_rows", len(rows), "Boundary/geography source alternatives audited for ALB_2002."),
        summary_row("alb2002_boundary_source_alternative_reachable_rows", reachable, "Rows with either a sampled web page or an existing local artifact review."),
        summary_row("alb2002_boundary_source_alternative_current_or_post2015_rows", current_or_post2015, "Sources that are current or post-2015/post-2019 boundary candidates rather than verified 2002 district sources."),
        summary_row("alb2002_boundary_source_alternative_lsms_maps_documented_rows", lsms_maps_documented, "Sources whose sampled page documents LSMS EA boundary maps."),
        summary_row("alb2002_boundary_source_alternative_gps_documented_rows", gps_documented, "Sources whose sampled page documents GPS or longitude/latitude evidence."),
        summary_row("alb2002_boundary_source_alternative_historical_candidate_rows", historical_candidate, "Historical/census-context source candidates that still require boundary-level and join-key verification."),
        summary_row("alb2002_boundary_source_alternative_historical_2002_boundary_ready_rows", 0, "Sources verified as ready 2001/2002 district boundary inputs after this audit; intentionally zero."),
        summary_row("alb2002_boundary_source_alternative_climate_linkage_ready_rows", 0, "Sources ready for climate-linkage input promotion after this audit; intentionally zero."),
        summary_row("alb2002_boundary_source_alternative_current_decision", DECISION, "Current fail-closed decision for ALB_2002 boundary-source alternatives."),
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


def write_report(rows: list[dict[str, str]], summary: list[dict[str, str]]) -> None:
    summary_table = "\n".join(f"| {row['metric']} | {row['value']} | {row['interpretation']} |" for row in summary)
    REPORT_PATH.write_text(
        f"""# ALB_2002 Boundary Source Alternatives Audit

Status: temp-only source-alternatives audit. This audit reviews local boundary evidence and probes public source landing pages for ALB_2002 historical district-boundary candidates. It does not download shapefiles, does not create centroids, does not write `data/`, and does not construct climate exposures.

## Summary

| Metric | Value | Interpretation |
|---|---:|---|
{summary_table}

## Source Alternatives

{markdown_rows(rows, ['candidate_id', 'source_name', 'probe_status', 'http_status', 'source_year_claim', 'boundary_suitability_status', 'historical_2002_boundary_ready', 'climate_linkage_ready'], 20)}

## Evidence and Blocking Reasons

{markdown_rows(rows, ['candidate_id', 'page_evidence_flags', 'local_or_page_evidence', 'blocking_reason'], 20)}

## Interpretation

- ALB_2002 remains the closest local wave for future analytical readiness because household timing, district code/name, consumption, weights, and OOP/access signals exist in temp-only audits.
    - Boundary evidence is still not climate-linkage ready. The strongest local geoBoundaries lead now has complete 36-district geometry/name coverage, but its companion metadata reports a 2013 boundary year rather than verified 2001/2002 LSMS district provenance.
- The official ALB_2002 study documentation is important because it points to EA maps and GPS recording, but this audit did not verify a directly usable GIS/GPS artifact in the current package.
- Historical census/GIS sources are candidate leads only until the boundary level, unit count, codes, names, projections, license, and join keys are manually verified against the 36 observed ALB_2002 district groups.
- Climate-linkage-ready rows remain zero.

## Machine-Readable Outputs

- `temp/alb2002_boundary_source_alternative_audit.csv`
- `result/alb2002_boundary_source_alternative_summary.csv`
""",
        encoding="utf-8",
    )


def main() -> None:
    ensure_dirs()
    if not BOUNDARY_NAME_SUMMARY_PATH.exists():
        raise FileNotFoundError(f"Missing prerequisite: {BOUNDARY_NAME_SUMMARY_PATH}")
    rows = build_rows()
    summary = build_summary(rows)
    write_csv(AUDIT_PATH, rows, AUDIT_COLUMNS)
    write_csv(SUMMARY_PATH, summary, SUMMARY_COLUMNS)
    write_report(rows, summary)
    append_log(
        TEMP_DIR / "audit_log.md",
        f"Built ALB_2002 boundary source alternatives audit rows={len(rows)} decision={DECISION}.",
    )
    print(f"ALB_2002 boundary source alternatives audit rows={len(rows)} decision={DECISION}.")


if __name__ == "__main__":
    main()
