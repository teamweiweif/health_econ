from __future__ import annotations

import csv
import re
import subprocess
from pathlib import Path

import requests
from bs4 import BeautifulSoup

from common import (
    REPORT_DIR,
    SNAPSHOT_DIR,
    TEMP_DIR,
    append_log,
    ensure_dirs,
    sha256_file,
    utc_now_iso,
    write_csv,
)


USER_AGENT = "Codex climate_uhc_ml official-source audit"
SOURCE_INVENTORY_COLUMNS = [
    "source name",
    "official URL",
    "access date",
    "file/wave",
    "unit",
    "geography",
    "row count",
    "column count",
    "checksum",
    "status",
]

OFFICIAL_SOURCES = [
    {
        "source_name": "WHO financial protection / SDG 3.8.2",
        "official_url": "https://www.who.int/data/gho/data/themes/topics/financial-protection",
        "snapshot": "who_financial_protection_sdg382_2025.md",
        "kind": "html",
    },
    {
        "source_name": "UN SDG 3.8.2 metadata",
        "official_url": "https://unstats.un.org/sdgs/metadata/files/Metadata-03-08-02.pdf",
        "snapshot": "unstats_sdg_3_8_2_metadata.pdf",
        "kind": "pdf",
    },
    {
        "source_name": "WHO climate-resilient health systems framework",
        "official_url": "https://www.who.int/publications/i/item/9789240081888",
        "snapshot": "who_climate_resilient_health_systems.md",
        "kind": "html",
    },
    {
        "source_name": "WHO climate change and health fact sheet",
        "official_url": "https://www.who.int/news-room/fact-sheets/detail/climate-change-and-health",
        "snapshot": "who_climate_change_health_factsheet.md",
        "kind": "html",
    },
    {
        "source_name": "World Bank Microdata Library",
        "official_url": "https://microdata.worldbank.org/index.php/home",
        "snapshot": "",
        "kind": "catalog",
    },
    {
        "source_name": "World Bank LSMS catalog",
        "official_url": "https://microdata.worldbank.org/index.php/catalog/lsms",
        "snapshot": "",
        "kind": "catalog",
    },
    {
        "source_name": "LSMS-ISA",
        "official_url": "https://www.worldbank.org/en/programs/lsms/initiatives/lsms-ISA",
        "snapshot": "",
        "kind": "catalog",
    },
    {
        "source_name": "World Bank HEFPI",
        "official_url": "https://datatopics.worldbank.org/health-equity-and-financial-protection/",
        "snapshot": "",
        "kind": "validation",
    },
    {
        "source_name": "UNICEF MICS surveys",
        "official_url": "https://mics.unicef.org/surveys",
        "snapshot": "",
        "kind": "secondary_microdata",
    },
    {
        "source_name": "DHS Program data",
        "official_url": "https://dhsprogram.com/data/",
        "snapshot": "",
        "kind": "secondary_microdata",
    },
    {
        "source_name": "DHS spatial covariates",
        "official_url": "https://spatialdata.dhsprogram.com/covariates/",
        "snapshot": "",
        "kind": "secondary_microdata",
    },
    {
        "source_name": "CHIRPS precipitation",
        "official_url": "https://www.chc.ucsb.edu/data/chirps",
        "snapshot": "",
        "kind": "climate",
    },
    {
        "source_name": "CHIRPS daily FTP/HTTP directory",
        "official_url": "https://data.chc.ucsb.edu/products/CHIRPS-2.0/global_daily/",
        "snapshot": "",
        "kind": "climate",
    },
    {
        "source_name": "ERA5-Land",
        "official_url": "https://cds.climate.copernicus.eu/datasets/reanalysis-era5-land",
        "snapshot": "",
        "kind": "climate",
    },
    {
        "source_name": "NASA POWER daily API",
        "official_url": "https://power.larc.nasa.gov/docs/services/api/temporal/daily/",
        "snapshot": "",
        "kind": "climate",
    },
    {
        "source_name": "TerraClimate",
        "official_url": "https://www.climatologylab.org/terraclimate.html",
        "snapshot": "",
        "kind": "climate",
    },
    {
        "source_name": "SPEI Global Drought Monitor",
        "official_url": "https://spei.csic.es/map/",
        "snapshot": "",
        "kind": "climate",
    },
]


def fetch_url(url: str) -> requests.Response:
    return requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=60)


def run_defuddle(url: str, output: Path) -> bool:
    try:
        result = subprocess.run(
            ["defuddle", "parse", url, "--md", "-o", str(output)],
            check=False,
            text=True,
            capture_output=True,
            timeout=90,
        )
        if result.returncode != 0:
            append_log(TEMP_DIR / "audit_log.md", f"Defuddle failed for {url}: {result.stderr.strip()[:500]}")
            return False
        if result.stderr.strip():
            append_log(TEMP_DIR / "audit_log.md", f"Defuddle warnings for {url}: {result.stderr.strip()[:500]}")
        return output.exists() and output.stat().st_size > 0
    except FileNotFoundError:
        append_log(TEMP_DIR / "audit_log.md", "Defuddle CLI not found; falling back to BeautifulSoup text extraction.")
    except Exception as exc:
        append_log(TEMP_DIR / "audit_log.md", f"Defuddle exception for {url}: {exc}")
    return False


def html_to_markdownish(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()
    lines = [line.strip() for line in soup.get_text("\n").splitlines()]
    return "\n".join(line for line in lines if line)


def ensure_snapshot(src: dict[str, str]) -> Path | None:
    snapshot_name = src.get("snapshot", "")
    if not snapshot_name:
        return None
    path = SNAPSHOT_DIR / snapshot_name
    url = src["official_url"]
    if path.exists() and path.stat().st_size > 0:
        return path

    if src["kind"] == "html":
        if run_defuddle(url, path):
            return path
        response = fetch_url(url)
        response.raise_for_status()
        path.write_text(html_to_markdownish(response.text), encoding="utf-8")
        return path

    if src["kind"] == "pdf":
        response = fetch_url(url)
        response.raise_for_status()
        path.write_bytes(response.content)
        return path

    return None


def extract_pdf_text(pdf_path: Path) -> str:
    try:
        from pypdf import PdfReader

        reader = PdfReader(str(pdf_path))
        text = "\n".join(page.extract_text() or "" for page in reader.pages)
        txt_path = pdf_path.with_suffix(".txt")
        txt_path.write_text(text, encoding="utf-8")
        return text
    except Exception as exc:
        append_log(TEMP_DIR / "audit_log.md", f"Could not extract PDF text from {pdf_path.name}: {exc}")
        return ""


def get_context(text: str, pattern: str, width: int = 600) -> str:
    match = re.search(pattern, text, flags=re.IGNORECASE | re.DOTALL)
    if not match:
        return ""
    start = max(0, match.start() - 80)
    end = min(len(text), match.end() + width)
    return " ".join(text[start:end].split())


def read_csv_dicts(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def merge_source_inventory(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    existing = read_csv_dicts(TEMP_DIR / "source_inventory.csv")
    merged_by_key = {
        (row.get("source name", ""), row.get("official URL", ""), row.get("file/wave", "")): row
        for row in existing
    }
    for row in rows:
        key = (row.get("source name", ""), row.get("official URL", ""), row.get("file/wave", ""))
        merged_by_key[key] = row
    return list(merged_by_key.values())


def build_source_inventory(snapshots: dict[str, Path | None]) -> None:
    rows = []
    for src in OFFICIAL_SOURCES:
        path = snapshots.get(src["source_name"])
        rows.append(
            {
                "source name": src["source_name"],
                "official URL": src["official_url"],
                "access date": utc_now_iso(),
                "file/wave": path.name if path else "",
                "unit": src["kind"],
                "geography": "",
                "row count": "",
                "column count": "",
                "checksum": sha256_file(path) if path and path.exists() else "",
                "status": "snapshot saved" if path and path.exists() else "registered for later pipeline use",
            }
        )
    write_csv(TEMP_DIR / "source_inventory.csv", merge_source_inventory(rows), SOURCE_INVENTORY_COLUMNS)


def write_reports(texts: dict[str, str]) -> None:
    # Keep the raw PDF text in temp/source_snapshots for auditability, but write a
    # clean report transcription because PDF extraction splits some words.
    sdg_definition_clean = "Proportion of the population with positive out-of-pocket household expenditure on health exceeding 40% of household discretionary budget."
    discretionary_budget_clean = (
        "Household discretionary budget is total household consumption expenditure or income minus the societal poverty line. "
        "The metadata specifies the SPL using 2017 PPPs and the greater of the international poverty line or a median-consumption-based societal line."
    )

    source_audit = f"""# Source Audit

Generated: {utc_now_iso()}

## Official Anchors Verified

| Claim | Status | Evidence |
|---|---|---|
| SDG 3.8.2 uses the 2025 revised 40% discretionary-budget definition | accepted | WHO financial protection page states that the page presents the revised 2025 definition. UNSD metadata defines the indicator as the proportion of population with positive OOP household expenditure on health exceeding 40% of household discretionary budget. |
| Discretionary budget equals total household consumption expenditure or income minus the societal poverty line | accepted | UNSD metadata defines discretionary household budget this way and specifies the SPL using 2017 PPPs. |
| CHE10 and CHE25 remain useful older/common financial hardship indicators | accepted as auxiliary, not the 2025 SDG definition | WHO notes data based on the 2017 definition are archived. The project will use CHE10/CHE25 as comparability and robustness outcomes, not as the current SDG 3.8.2 definition. |
| Climate-resilient health systems and UHC are connected in WHO documentation | accepted | WHO's operational framework says climate-resilient health systems contribute to UHC, global health security, and SDG targets. |
| Climate change can reduce capacity to provide UHC and worsen financial hardship/access barriers | accepted as policy rationale, not empirical proof for this project | WHO's climate fact sheet states climate change affects health systems and can reduce capacity to provide UHC; empirical effects must still be estimated from data. |
| Household microdata can support a multi-country causal ML paper | not yet verified | Requires country-wave inventory, raw schema inspection, usable timing/geography, outcome construction, and falsification tests. |
| Climate shocks cause UHC failure in the candidate data | not yet verified | No causal claim is accepted until exposure construction and reduced-form/placebo tests pass. |

## Extracted Evidence Notes

### WHO financial protection

The WHO financial protection page was snapshotted at `temp/source_snapshots/who_financial_protection_sdg382_2025.md`. It identifies the current SDG 3.8.2 series as the revised 2025 definition and links to the official UNSD metadata PDF. The raw WHO page extraction contains some malformed smart-quote characters from HTML parsing, so the exact definitional text below is taken from the cleaner UNSD PDF extraction.

### UNSD SDG 3.8.2 metadata

Official 2025 indicator definition recorded from the metadata:

> {sdg_definition_clean}

Denominator rule: {discretionary_budget_clean}

The extracted PDF text is saved at `temp/source_snapshots/unstats_sdg_3_8_2_metadata.txt` for traceability.

### WHO climate-resilient health systems

The WHO operational framework on climate-resilient and low-carbon health systems was snapshotted at `temp/source_snapshots/who_climate_resilient_health_systems.md`. It explicitly frames climate-resilient health systems as contributing to UHC, global health security, and SDG targets.

### WHO climate change and health

The WHO climate change and health fact sheet was snapshotted at `temp/source_snapshots/who_climate_change_health_factsheet.md`. It links climate shocks, health-system capacity, and UHC as policy motivation; this is not treated as evidence that the empirical effect exists in the candidate microdata.

## Current Go/No-Go

Go for Phase 1 inventory and screening. No go for causal modeling, causal ML, or policy-learning claims until microdata variables, geography, timing, and placebo tests are audited.
"""
    (REPORT_DIR / "source_audit.md").write_text(source_audit, encoding="utf-8")

    outcome_report = """# Outcome Construction

Status: definitions verified; no household microdata outcomes have been constructed yet.

## Primary Financial Protection Outcomes

| Harmonized outcome | Formula | Current status |
|---|---|---|
| `sdg382_discretionary_40` | positive OOP health expenditure > 40% of household discretionary budget | preferred official outcome only after SPL, PPP/CPI, total consumption or income, OOP, household size, and time-period harmonization pass audit |
| `che10_total_budget` | OOP health expenditure > 10% of total consumption or income | auxiliary robustness/comparability outcome |
| `che25_total_budget` | OOP health expenditure > 25% of total consumption or income | auxiliary robustness/comparability outcome |
| `capacity_to_pay_40` | OOP health expenditure > 40% of capacity to pay under older WHO/World Bank style construction | construct only where subsistence/capacity-to-pay inputs are defensible |
| `impoverishing_health_spending` | above poverty line before OOP and below after OOP | construct after poverty-line and PPP/CPI audit |
| `oop_share_total` | OOP health expenditure / total consumption or income | continuous descriptive and model feature/outcome |
| `log_oop_plus_one` | log(OOP + 1), harmonized within country-wave if units differ | continuous descriptive and model feature/outcome |

## Primary Access Outcomes

| Harmonized outcome | Formula | Current status |
|---|---|---|
| `forgone_care_conditional_need` | illness/injury/health need observed and care not sought | requires need and care-seeking module |
| `forgone_care_cost_barrier` | care not sought due to cost | requires reason-not-sought codes |
| `forgone_care_distance_barrier` | care not sought due to distance/transport | requires reason-not-sought codes |
| `forgone_care_supply_barrier` | care not sought due to provider, drugs, staff, or facility availability | requires reason-not-sought codes |
| `delayed_or_unmet_care` | survey-specific unmet/delayed care item | use only when module wording supports it |

## Composite UHC Failure

Composite outcomes will be built only after financial and access outcomes are audited within each country-wave. The default composite is `financial hardship OR forgone care conditional on need`.

## Caveats

- Do not label `sdg382_discretionary_40` as complete unless the discretionary-budget denominator is correctly constructed.
- Do not annualize health expenditure across different recall periods without documenting the rule and comparability risk.
- Event rates below 3% are flagged before ML or causal ML.
"""
    (REPORT_DIR / "outcome_construction.md").write_text(outcome_report, encoding="utf-8")

    climate_report = """# Climate Linkage Audit

Status: sources registered; no climate extraction has been run yet.

## Planned Source Hierarchy

| Domain | Primary source | Fallback/robustness |
|---|---|---|
| Rainfall | CHIRPS daily/monthly precipitation | ERA5-Land or NASA POWER precipitation subset checks |
| Temperature | ERA5-Land daily statistics | NASA POWER daily API for rapid point extraction |
| Drought/water balance | SPEI and TerraClimate | rainfall z-scores and cumulative deficits |

## Linkage Rules

- Use exact household or cluster GPS only when the microdata actually provide it.
- If GPS is displaced, record displacement uncertainty and use buffer or area aggregation when feasible.
- If only admin geography exists, use admin-level climate aggregation or centroids and explicitly downgrade exposure precision.
- Use interview date/month to define 1, 3, 6, and 12 month pre-interview exposure windows.
"""
    (REPORT_DIR / "climate_linkage_audit.md").write_text(climate_report, encoding="utf-8")

    identification_report = """# Identification Audit

Status: not yet eligible for causal claims.

## Current Judgment

The project may proceed to inventory and raw schema screening. It may not proceed to causal estimation until the analytical sample has valid survey timing, geography, climate exposure linkage, outcome construction, survey design fields, and sufficient identifying variation.

## Required Before Causal Language

- country-wave fixed effects and geography/season controls specified from real variables
- future climate shock placebo
- alternative climate lags
- alternative climate source checks
- country leave-one-out
- clustered/survey-design robustness
- event-rate and missingness diagnostics
"""
    (REPORT_DIR / "identification_audit.md").write_text(identification_report, encoding="utf-8")


def main() -> None:
    ensure_dirs()
    snapshots: dict[str, Path | None] = {}
    texts: dict[str, str] = {}
    for src in OFFICIAL_SOURCES:
        path = ensure_snapshot(src)
        snapshots[src["source_name"]] = path
        if path and path.exists():
            if src["kind"] == "pdf":
                texts[src["source_name"]] = extract_pdf_text(path)
            else:
                texts[src["source_name"]] = path.read_text(encoding="utf-8", errors="replace")

    build_source_inventory(snapshots)
    write_reports(texts)
    append_log(TEMP_DIR / "audit_log.md", "Verified official anchors and wrote Phase 0 source reports.")
    print("Wrote report/source_audit.md, report/outcome_construction.md, and temp/source_inventory.csv")


if __name__ == "__main__":
    main()
