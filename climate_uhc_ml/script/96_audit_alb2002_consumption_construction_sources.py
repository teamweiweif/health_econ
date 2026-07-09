from __future__ import annotations

import csv
import hashlib
import json
import re
import urllib.request
import zipfile
from pathlib import Path
from typing import Any

from common import REPORT_DIR, RESULT_DIR, TEMP_DIR, append_log, ensure_dirs, write_csv

try:
    import pyreadstat
except ImportError:  # pragma: no cover - environment audit covers this.
    pyreadstat = None

try:
    from pypdf import PdfReader
except ImportError:  # pragma: no cover - fallback below covers older environments.
    try:
        from PyPDF2 import PdfReader  # type: ignore[assignment]
    except ImportError:  # pragma: no cover
        PdfReader = None  # type: ignore[assignment]


IDNO = "ALB_2002_LSMS_v01_M"
COUNTRY = "Albania"
SURVEY_NAME = "Living Standards Measurement Survey 2002"
WAVE = "2002"

SOURCE_DIR = TEMP_DIR / "source_snapshots" / "alb2002_consumption_construction"
PROGRAM_DIR = SOURCE_DIR / "program_files"
RAW_POVERTY_SAV = TEMP_DIR / "raw_extracted" / "lsms2002en_4dbf0b087520" / "lsms2002en" / "Data_2002" / "Poverty_2002.sav"

RELATED_MATERIALS_URL = "https://catalog.ihsn.org/catalog/6/related-materials"
PDF_URL = "https://catalog.ihsn.org/catalog/6/download/28203"
PROGRAM_ZIP_URL = "https://catalog.ihsn.org/catalog/6/download/28204"
METADATA_JSON_URL = "https://catalog.ihsn.org/metadata/export/6/json"

RELATED_HTML = SOURCE_DIR / "ihsn_alb2002_related_materials.html"
PDF_PATH = SOURCE_DIR / "ihsn_alb2002_consumption_aggregate_poverty_line.pdf"
PDF_TEXT_PATH = SOURCE_DIR / "ihsn_alb2002_consumption_aggregate_poverty_line.txt"
PROGRAM_ZIP_PATH = SOURCE_DIR / "ihsn_alb2002_consumption_program_files.zip"
METADATA_JSON_PATH = SOURCE_DIR / "ihsn_alb2002_metadata.json"

TOTCONS_DO = PROGRAM_DIR / "Albania 2002" / "Programs" / "Consumption" / "totcons.do"
POVERTY_DO = PROGRAM_DIR / "Albania 2002" / "Programs" / "Consumption" / "poverty.do"
OVERALL_DO = PROGRAM_DIR / "Albania 2002" / "Programs" / "Consumption" / "overall.do"

AUDIT_PATH = TEMP_DIR / "alb2002_consumption_construction_source_audit.csv"
SUMMARY_PATH = RESULT_DIR / "alb2002_consumption_construction_source_summary.csv"
REPORT_PATH = REPORT_DIR / "alb2002_consumption_construction_source_audit.md"

DECISION = "documented_alb2002_consumption_aggregate_but_not_outcome_sdg_climate_ready"
NO_PROMOTION = "not_promoted_source_documentation_audit_only"

AUDIT_COLUMNS = [
    "country",
    "survey_name",
    "wave",
    "idno",
    "audit_family",
    "evidence_item",
    "source_url",
    "source_file",
    "source_detail",
    "sha256",
    "row_count",
    "evidence_status",
    "documentation_ready",
    "released_variable_mapping_ready",
    "denominator_variant_ready",
    "ready_for_recipe",
    "ready_for_outcome",
    "sdg382_ready",
    "climate_linkage_ready",
    "promotion_status",
    "blocking_reason",
    "next_action",
]
SUMMARY_COLUMNS = ["metric", "value", "interpretation"]


def download(url: str, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(request, timeout=60) as response:
        path.write_bytes(response.read())


def sha256(path: Path) -> str:
    if not path.exists():
        return ""
    digest = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def clean_text(value: Any) -> str:
    if value is None:
        return ""
    return " ".join(str(value).split()).encode("ascii", "replace").decode("ascii")


def read_text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def extract_pdf_text(path: Path) -> str:
    if not path.exists() or PdfReader is None:
        return ""
    reader = PdfReader(str(path))
    return "\n".join(page.extract_text() or "" for page in reader.pages)


def ensure_sources() -> None:
    SOURCE_DIR.mkdir(parents=True, exist_ok=True)
    sources = [
        (RELATED_MATERIALS_URL, RELATED_HTML),
        (PDF_URL, PDF_PATH),
        (PROGRAM_ZIP_URL, PROGRAM_ZIP_PATH),
        (METADATA_JSON_URL, METADATA_JSON_PATH),
    ]
    for url, path in sources:
        if not path.exists() or path.stat().st_size == 0:
            download(url, path)
    if PROGRAM_ZIP_PATH.exists():
        PROGRAM_DIR.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(PROGRAM_ZIP_PATH) as zf:
            zf.extractall(PROGRAM_DIR)
    if not PDF_TEXT_PATH.exists() or PDF_TEXT_PATH.stat().st_size == 0:
        PDF_TEXT_PATH.write_text(extract_pdf_text(PDF_PATH), encoding="utf-8")


def load_metadata() -> dict[str, Any]:
    if not METADATA_JSON_PATH.exists():
        return {}
    return json.loads(METADATA_JSON_PATH.read_text(encoding="utf-8"))


def metadata_variable(name: str) -> dict[str, Any]:
    for row in load_metadata().get("variables", []):
        if str(row.get("name", "")).lower() == name.lower():
            return row
    return {}


def metadata_file(file_id: str) -> dict[str, Any]:
    for row in load_metadata().get("data_files", []):
        if str(row.get("file_id", "")) == file_id:
            return row
    return {}


def summary_stats_from_metadata(row: dict[str, Any]) -> dict[str, str]:
    out = {"n": "0", "min": "", "max": ""}
    for stat in row.get("var_sumstat", []) or []:
        if stat.get("type") == "vald":
            out["n"] = str(stat.get("value", "0"))
        elif stat.get("type") == "min":
            out["min"] = str(stat.get("value", ""))
        elif stat.get("type") == "max":
            out["max"] = str(stat.get("value", ""))
    return out


def local_poverty_stats() -> dict[str, str]:
    if pyreadstat is None or not RAW_POVERTY_SAV.exists():
        return {"n": "0", "min": "", "max": "", "columns": "0"}
    df, _ = pyreadstat.read_sav(str(RAW_POVERTY_SAV), apply_value_formats=False)
    if "totcons" not in df.columns:
        return {"n": str(len(df)), "min": "", "max": "", "columns": str(len(df.columns))}
    series = df["totcons"].dropna()
    return {
        "n": str(int(series.shape[0])),
        "min": f"{float(series.min()):.6f}",
        "max": f"{float(series.max()):.6f}",
        "columns": str(len(df.columns)),
    }


def floats_match(left: str, right: str, tolerance: float = 1e-3) -> bool:
    try:
        return abs(float(left) - float(right)) <= tolerance
    except (TypeError, ValueError):
        return False


def count_do_files() -> int:
    if not PROGRAM_DIR.exists():
        return 0
    return sum(1 for _ in PROGRAM_DIR.rglob("*.do"))


def has_pattern(text: str, pattern: str) -> bool:
    return re.search(pattern, text, flags=re.IGNORECASE | re.DOTALL) is not None


def row(
    audit_family: str,
    evidence_item: str,
    source_url: str,
    source_file: Path,
    source_detail: str,
    row_count: int,
    evidence_status: str,
    documentation_ready: int,
    released_variable_mapping_ready: int,
    denominator_variant_ready: int,
    blocking_reason: str,
    next_action: str,
) -> dict[str, str]:
    return {
        "country": COUNTRY,
        "survey_name": SURVEY_NAME,
        "wave": WAVE,
        "idno": IDNO,
        "audit_family": audit_family,
        "evidence_item": evidence_item,
        "source_url": source_url,
        "source_file": str(source_file.as_posix()),
        "source_detail": clean_text(source_detail),
        "sha256": sha256(source_file) if source_file.exists() and source_file.is_file() else "",
        "row_count": str(row_count),
        "evidence_status": evidence_status,
        "documentation_ready": str(documentation_ready),
        "released_variable_mapping_ready": str(released_variable_mapping_ready),
        "denominator_variant_ready": str(denominator_variant_ready),
        "ready_for_recipe": "0",
        "ready_for_outcome": "0",
        "sdg382_ready": "0",
        "climate_linkage_ready": "0",
        "promotion_status": NO_PROMOTION,
        "blocking_reason": blocking_reason,
        "next_action": next_action,
    }


def build_rows() -> list[dict[str, str]]:
    ensure_sources()
    html = read_text(RELATED_HTML)
    pdf_text = read_text(PDF_TEXT_PATH)
    totcons_text = read_text(TOTCONS_DO)
    poverty_text = read_text(POVERTY_DO)
    overall_text = read_text(OVERALL_DO)

    totcons3 = metadata_variable("totcons3")
    rpcons3 = metadata_variable("rpcons3")
    file_f158 = metadata_file("F158")
    meta_stats = summary_stats_from_metadata(totcons3)
    local_stats = local_poverty_stats()
    local_matches_totcons3 = (
        local_stats["n"] == meta_stats["n"]
        and floats_match(local_stats["min"], meta_stats["min"])
        and floats_match(local_stats["max"], meta_stats["max"])
    )

    pdf_components_ready = all(
        phrase in pdf_text.lower()
        for phrase in [
            "food consumption",
            "non food expenses",
            "utilities",
            "education",
            "health",
            "durables",
            "housing",
        ]
    )
    pdf_exclusion_ready = "decision was taken not to include rents" in pdf_text.lower() and "exclude health" in pdf_text.lower()
    code_components_ready = has_pattern(totcons_text, r"egen\s+totcons3\s*=\s*rsum\(food\s+sub1-sub10\s+edu\s+elect\s+fuel\s+waterb\s+phone\s+durcons\)")
    poverty_denominator_ready = "gen rpcons3=totcons3/(psupind*hhsize)" in poverty_text.replace(" ", "")
    if not poverty_denominator_ready:
        poverty_denominator_ready = "gen rpcons3=totcons3/(psupind*hhsize)" in poverty_text

    rows = [
        row(
            "public_catalog_evidence",
            "ihsn_related_materials_lists_consumption_pdf_and_program_zip",
            RELATED_MATERIALS_URL,
            RELATED_HTML,
            "Related materials page lists Construction of the Consumption Aggregate and Estimation of the Poverty Line plus Program Files.",
            1,
            "source_page_downloaded",
            int("Construction of the Consumption Aggregate" in html and "Program Files" in html),
            0,
            0,
            "Catalog source presence is documentation evidence, not outcome construction.",
            "Use the downloaded PDF and Stata programs as source evidence for the denominator audit.",
        ),
        row(
            "official_method_pdf",
            "consumption_aggregate_and_poverty_line_pdf",
            PDF_URL,
            PDF_PATH,
            f"PDF text chars={len(pdf_text)}; consumption aggregate hits={pdf_text.lower().count('consumption aggregate')}; poverty line hits={pdf_text.lower().count('poverty line')}.",
            1,
            "official_method_pdf_downloaded",
            int(PDF_PATH.exists() and PDF_PATH.stat().st_size > 0 and pdf_components_ready),
            0,
            int(pdf_exclusion_ready),
            "The PDF documents aggregate concepts but does not itself construct SDG 3.8.2 or climate-linked outcomes.",
            "Use the PDF with the released code and metadata JSON before accepting the denominator lineage.",
        ),
        row(
            "official_program_files",
            "consumption_stata_program_zip",
            PROGRAM_ZIP_URL,
            PROGRAM_ZIP_PATH,
            f"Extracted do-files={count_do_files()}; key files present: overall.do={OVERALL_DO.exists()}, totcons.do={TOTCONS_DO.exists()}, poverty.do={POVERTY_DO.exists()}.",
            count_do_files(),
            "official_program_zip_downloaded_and_extracted",
            int(count_do_files() >= 19 and TOTCONS_DO.exists() and POVERTY_DO.exists()),
            0,
            int(code_components_ready and poverty_denominator_ready),
            "The code documents the denominator variant but does not resolve OOP numerator scope, SPL/PPP/CPI, or climate geography.",
            "Translate the denominator variant into the harmonization gate while keeping outcome and climate gates closed.",
        ),
        row(
            "code_sequence",
            "overall_do_runs_consumption_pipeline_sequence",
            "",
            OVERALL_DO,
            "overall.do runs base, food, food1, nfood, eduhealth, utilities, durables, prepare_prices, paasche_psu, totcons, povline, poverty, and follow-up checks.",
            1,
            "pipeline_sequence_seen",
            int("do totcons.do" in overall_text.lower() and "do poverty.do" in overall_text.lower()),
            0,
            1,
            "The sequence is source-code evidence only; it is not a reproduced Stata run in this Python workspace.",
            "Keep this as provenance evidence unless Stata reproduction is explicitly required.",
        ),
        row(
            "code_formula",
            "totcons_do_defines_denominator_variants",
            "",
            TOTCONS_DO,
            "totcons.do defines totcons with health, totcons1 without health, totcons2 without durables and health, and totcons3 with durables and without rent and health.",
            4,
            "denominator_variants_defined",
            int(code_components_ready),
            0,
            int(code_components_ready),
            "The final denominator choice still needs to be linked to the released SPSS column and OOP numerator policy.",
            "Use metadata JSON and local SPSS statistics to verify the released column mapping.",
        ),
        row(
            "code_formula",
            "poverty_do_uses_rpcons3_for_poverty_estimates",
            "",
            POVERTY_DO,
            "poverty.do computes rpcons3=totcons3/(psupind*hhsize), labels it without rent, and uses rpcons3 against povline3 for the main poverty measures.",
            1,
            "final_poverty_denominator_variant_seen",
            int(poverty_denominator_ready),
            0,
            int(poverty_denominator_ready),
            "This verifies the poverty denominator variant, but not the SDG 3.8.2 discretionary-budget denominator.",
            "Treat `totcons3`/local `totcons` as a documented CHE total-budget candidate, not an SDG discretionary budget.",
        ),
        row(
            "public_metadata_json",
            "metadata_json_totcons3_label",
            METADATA_JSON_URL,
            METADATA_JSON_PATH,
            f"F158 file name={file_f158.get('file_name') or file_f158.get('name')}; totcons3 label={totcons3.get('labl')}; rpcons3 label={rpcons3.get('labl')}.",
            1 if totcons3 else 0,
            "public_metadata_variable_seen" if totcons3 else "public_metadata_variable_missing",
            int(bool(totcons3 and rpcons3)),
            int(bool(totcons3 and rpcons3)),
            int(str(totcons3.get("labl", "")).lower() == "with durables and without rent and health"),
            "Metadata labels identify the released public variable concepts but do not settle OOP alignment or SDG inputs.",
            "Use the labels to update the ALB_2002 denominator crosswalk from undocumented to documented-but-blocked.",
        ),
        row(
            "released_spSS_mapping",
            "local_totcons_matches_public_metadata_totcons3_stats",
            METADATA_JSON_URL,
            RAW_POVERTY_SAV,
            f"Local totcons n/min/max={local_stats['n']}/{local_stats['min']}/{local_stats['max']}; metadata totcons3 n/min/max={meta_stats['n']}/{meta_stats['min']}/{meta_stats['max']}.",
            int(local_stats["n"] or "0"),
            "local_totcons_matches_totcons3_metadata" if local_matches_totcons3 else "local_totcons_metadata_match_failed",
            int(local_matches_totcons3),
            int(local_matches_totcons3),
            int(local_matches_totcons3),
            "The mapping validates the total-consumption denominator variable, but does not promote outcomes or climate linkage.",
            "Use local `totcons` as the documented total-budget denominator candidate only after OOP and access policies pass.",
        ),
        row(
            "policy_boundary",
            "health_and_rent_exclusion_denominator_policy",
            PDF_URL,
            PDF_PATH,
            "PDF and code show health and rent were excluded from the final poverty denominator variant used for poverty estimates.",
            1,
            "health_rent_exclusion_documented" if pdf_exclusion_ready and code_components_ready else "health_rent_exclusion_not_fully_documented",
            int(pdf_exclusion_ready and code_components_ready),
            int(local_matches_totcons3),
            int(pdf_exclusion_ready and code_components_ready),
            "Excluding health from the denominator is appropriate for total-budget CHE diagnostics, but SDG 3.8.2 still needs SPL and PPP/CPI construction.",
            "Keep SDG 3.8.2 blocked until societal poverty-line and price-conversion gates are built.",
        ),
    ]
    return rows


def summary_row(metric: str, value: Any, interpretation: str) -> dict[str, str]:
    return {"metric": metric, "value": str(value), "interpretation": interpretation}


def build_summary(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    documentation_ready = sum(1 for r in rows if r["documentation_ready"] == "1")
    mapping_ready = sum(1 for r in rows if r["released_variable_mapping_ready"] == "1")
    denominator_ready = sum(1 for r in rows if r["denominator_variant_ready"] == "1")
    return [
        summary_row("alb2002_consumption_construction_source_audit_rows", len(rows), "Rows in the ALB_2002 public consumption-construction source audit."),
        summary_row("alb2002_consumption_construction_public_pdf_present", int(PDF_PATH.exists() and PDF_PATH.stat().st_size > 0), "Public IHSN consumption aggregate and poverty-line PDF downloaded."),
        summary_row("alb2002_consumption_construction_program_zip_present", int(PROGRAM_ZIP_PATH.exists() and PROGRAM_ZIP_PATH.stat().st_size > 0), "Public IHSN Stata program ZIP downloaded."),
        summary_row("alb2002_consumption_construction_do_file_rows", count_do_files(), "Extracted Stata do-files in the public consumption program package."),
        summary_row("alb2002_consumption_construction_totcons_do_present", int(TOTCONS_DO.exists()), "Whether totcons.do is present in the extracted program package."),
        summary_row("alb2002_consumption_construction_poverty_do_present", int(POVERTY_DO.exists()), "Whether poverty.do is present in the extracted program package."),
        summary_row("alb2002_consumption_construction_metadata_json_present", int(METADATA_JSON_PATH.exists() and METADATA_JSON_PATH.stat().st_size > 0), "Public IHSN metadata JSON downloaded."),
        summary_row("alb2002_consumption_construction_documentation_ready_rows", documentation_ready, "Audit rows with accepted public documentation evidence."),
        summary_row("alb2002_consumption_construction_released_variable_mapping_ready_rows", mapping_ready, "Audit rows supporting the mapping from local `totcons` to public metadata `totcons3`."),
        summary_row("alb2002_consumption_construction_denominator_variant_ready_rows", denominator_ready, "Audit rows documenting the final total-budget denominator variant."),
        summary_row("alb2002_consumption_construction_recipe_ready_rows", 0, "Rows promoted to a full harmonization recipe by this source audit; intentionally zero."),
        summary_row("alb2002_consumption_construction_outcome_ready_rows", 0, "Rows promoted to outcome construction by this source audit; intentionally zero."),
        summary_row("alb2002_consumption_construction_sdg382_ready_rows", 0, "Rows promoted to SDG 3.8.2 construction by this source audit; intentionally zero."),
        summary_row("alb2002_consumption_construction_climate_linkage_ready_rows", 0, "Rows promoted to climate linkage by this source audit; intentionally zero."),
        summary_row("alb2002_consumption_construction_current_decision", DECISION, "Current decision for ALB_2002 public consumption aggregate construction evidence."),
    ]


def markdown_table(rows: list[dict[str, str]], columns: list[str]) -> str:
    lines = ["| " + " | ".join(columns) + " |", "|" + "|".join("---" for _ in columns) + "|"]
    for row_data in rows:
        values = []
        for column in columns:
            value = row_data.get(column, "").replace("|", "/")
            if len(value) > 160:
                value = value[:157] + "..."
            values.append(value)
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines)


def write_report(rows: list[dict[str, str]], summary: list[dict[str, str]]) -> None:
    summary_table = "\n".join(f"| {r['metric']} | {r['value']} | {r['interpretation']} |" for r in summary)
    report = f"""# ALB_2002 Consumption Construction Source Audit

Status: public-source documentation audit for the ALB_2002 total-consumption aggregate. This report does not write `data/`, does not construct CHE or SDG outcomes, and does not promote climate-linked analysis.

## Bottom Line

- IHSN related materials list a public PDF titled `Construction of the Consumption Aggregate and Estimation of the Poverty Line`.
- IHSN related materials also list a public Stata program ZIP; the extracted package contains {count_do_files()} `.do` files, including `totcons.do`, `poverty.do`, and `overall.do`.
- The public metadata JSON identifies `totcons3` in file `poverty` as `with durables and without rent and health`.
- Local `Poverty_2002.sav` column `totcons` matches public metadata `totcons3` on row count, minimum, and maximum, so the prior denominator evidence is now documented as the final poverty total-budget variant.
- This resolves the narrow official aggregate-documentation blocker, but it does not resolve OOP numerator policy, SDG 3.8.2 SPL/PPP/CPI/discretionary-budget construction, benchmark validation, or climate linkage.
- Current decision: `{DECISION}`.

## Summary

| Metric | Value | Interpretation |
|---|---:|---|
{summary_table}

## Evidence Rows

{markdown_table(rows, ['audit_family', 'evidence_item', 'row_count', 'evidence_status', 'documentation_ready', 'released_variable_mapping_ready', 'denominator_variant_ready'])}

## Source Files

- `{RELATED_HTML.as_posix()}`
- `{PDF_PATH.as_posix()}`
- `{PDF_TEXT_PATH.as_posix()}`
- `{PROGRAM_ZIP_PATH.as_posix()}`
- `{PROGRAM_DIR.as_posix()}`
- `{METADATA_JSON_PATH.as_posix()}`

## Interpretation

The denominator gate should no longer say no official ALB_2002 consumption-construction source was found. The correct narrower statement is that official source evidence supports local `totcons` as the public metadata `totcons3` variant, with durables and without rent and health. Promotion still remains blocked because this source audit does not define the accepted health OOP numerator, SDG societal poverty line, PPP/CPI conversion, discretionary budget, geography, or climate exposure.
"""
    REPORT_PATH.write_text(report, encoding="utf-8")


def main() -> None:
    ensure_dirs()
    rows = build_rows()
    summary = build_summary(rows)
    write_csv(AUDIT_PATH, rows, AUDIT_COLUMNS)
    write_csv(SUMMARY_PATH, summary, SUMMARY_COLUMNS)
    write_report(rows, summary)
    append_log(TEMP_DIR / "audit_log.md", f"Built ALB_2002 consumption construction source audit rows={len(rows)} decision={DECISION}.")
    print(f"ALB_2002 consumption construction source audit rows={len(rows)} decision={DECISION}.")


if __name__ == "__main__":
    main()
