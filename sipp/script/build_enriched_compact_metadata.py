from __future__ import annotations

import hashlib
import json
import re
from collections import OrderedDict
from pathlib import Path

from pypdf import PdfReader


PROJECT_ROOT = Path(__file__).resolve().parents[1]
META_DIR = PROJECT_ROOT / "temp" / "source_metadata"
COMPACT_JSON = META_DIR / "sipp_2018_2024_raw_variable_metadata.compact.json"
OUT_JSON = META_DIR / "sipp_2018_2024_raw_variable_metadata.enriched.compact.json"

PDFS = {
    "2018": META_DIR / "census_sipp" / "2018" / "2018_SIPP_Metadata_v3.pdf",
    "2019": META_DIR / "census_sipp" / "2019" / "2019_SIPP_Data_Dictionary.pdf",
    "2020": META_DIR / "census_sipp" / "2020" / "2020_SIPP_Data_Dictionary.pdf",
    "2021": META_DIR / "census_sipp" / "2021" / "2021_SIPP_Data_Dictionary_AUG22.pdf",
    "2022": META_DIR / "census_sipp" / "2022" / "2022_SIPP_Data_Dictionary.pdf",
    "2023": META_DIR / "census_sipp" / "2023" / "2023_SIPP_Data_Dictionary.pdf",
    "2024": META_DIR / "census_sipp" / "2024" / "2024_SIPP_Data_Dictionary.pdf",
}

OLD_FORMAT_YEARS = {"2018", "2019", "2020"}


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def rel(path: Path) -> str:
    return str(path.relative_to(PROJECT_ROOT))


def norm(text: str | None) -> str:
    return re.sub(r"\s+", " ", text or "").strip()


def strip_page_number(value: str, page_number: int) -> str:
    value = norm(value)
    return re.sub(rf"\s+{page_number}\s*$", "", value).strip()


def between(text: str, start: str, end_markers: list[str]) -> str:
    start_idx = text.find(start)
    if start_idx < 0:
        return ""
    start_idx += len(start)
    end_idx = len(text)
    for marker in end_markers:
        idx = text.find(marker, start_idx)
        if idx >= 0:
            end_idx = min(end_idx, idx)
    return norm(text[start_idx:end_idx])


def parse_possible_values(raw_text: str, source_kind: str) -> OrderedDict:
    raw = norm(raw_text)
    raw = re.sub(r"^Value:\s*Description:\s*", "", raw).strip()
    value_labels = []
    range_info = OrderedDict()
    parse_notes = []

    min_match = re.search(r"(?:Minimum|Min):\s*(.*?)(?=\s+(?:Maximum|Max):|$)", raw)
    max_match = re.search(r"(?:Maximum|Max):\s*(.*)$", raw)
    if min_match:
        range_info["minimum"] = norm(min_match.group(1))
    if max_match:
        range_info["maximum"] = norm(max_match.group(1))

    if not range_info and re.fullmatch(r"[^:]+:[^:]+", raw):
        range_info["range_text"] = raw

    if source_kind == "new":
        pairs = re.findall(r"(-?\d+(?:\.\d+)?)\.\s*(.*?)(?=\s+-?\d+(?:\.\d+)?\.\s+|$)", raw)
    else:
        pairs = re.findall(r"(-?\d+(?:\.\d+)?)\s+(.*?)(?=\s+-?\d+(?:\.\d+)?\s+|$)", raw)

    if pairs and not range_info:
        for code, label in pairs:
            label = norm(label)
            if label:
                value_labels.append(OrderedDict([("code", code), ("label", label)]))
    elif pairs and range_info:
        parse_notes.append("numeric pairs were not stored as value labels because range information was detected")

    if raw and not value_labels and not range_info:
        parse_notes.append("possible values retained as raw text only")

    out = OrderedDict()
    out["possible_values_raw"] = raw
    if value_labels:
        out["value_labels"] = value_labels
    if range_info:
        out["range"] = range_info
    if parse_notes:
        out["parse_notes"] = parse_notes
    return out


def parse_new_page(text: str, page_number: int, pdf_rel: str) -> OrderedDict | None:
    flat = norm(text)
    name_match = re.search(r"\bName:\s*([A-Za-z0-9_]+)\b", flat)
    if not name_match or "Possible Values" not in flat:
        return None
    name = name_match.group(1)

    topic = ""
    subtopic = ""
    topic_match = re.search(
        rf"Topic:\s*(.*?)\s+Subtopic:\s*(.*?)\s+{re.escape(name)}\s+Name:\s*{re.escape(name)}\b",
        flat,
    )
    if topic_match:
        topic = norm(topic_match.group(1))
        subtopic = norm(topic_match.group(2))

    status_tail_markers = [" File:", " Record Level:", " Possible Values"]
    file_marker = "File:" if " File:" in flat else ("Record Level:" if " Record Level:" in flat else "")

    record_level_or_file = ""
    if file_marker:
        record_level_or_file = between(flat, file_marker, [" Possible Values"])

    values_raw = between(flat, "Possible Values", [])
    values_raw = strip_page_number(values_raw, page_number)

    return OrderedDict(
        [
            ("found", True),
            ("source_pdf_relative_path", pdf_rel),
            ("source_pdf_page", page_number),
            ("topic", topic),
            ("subtopic", subtopic),
            ("description", between(flat, "Description:", [" Universe:"])),
            ("universe", between(flat, "Universe:", [" Universe Description:"])),
            ("universe_description", between(flat, "Universe Description:", [" Length:"])),
            ("length", between(flat, "Length:", [" Status Flag:"])),
            ("status_flag", between(flat, "Status Flag:", status_tail_markers)),
            ("record_level_or_file", record_level_or_file),
            ("possible_values", parse_possible_values(values_raw, "new")),
        ]
    )


def parse_old_page(text: str, page_number: int, pdf_rel: str) -> OrderedDict | None:
    flat = norm(text)
    if "Variable Description:" not in flat and " Description:" not in flat:
        return None

    name = ""
    description_start = ""
    m = re.search(r"(?:^|\s)Variable\s+([A-Za-z0-9_]+)\s+Description:", flat)
    if m:
        name = m.group(1)
        description_start = "Description:"
    else:
        m = re.search(r"(?:^|\s)([A-Za-z0-9_]+)\s+Variable\s+Description:", flat)
        if m:
            name = m.group(1)
            description_start = "Variable Description:"
    if not name:
        return None

    if " Universe Description:" in flat:
        description = between(flat, description_start, [" Universe Description:"])
        universe_description = between(flat, "Universe Description:", [" Universe:"])
    else:
        description = between(flat, description_start, [" Universe:"])
        universe_description = ""

    universe = between(flat, "Universe:", [" Length:"])
    length = between(flat, "Length:", [" Answer List:", " Min:", " Max:", " Status Flag:", " Printed On:"])
    status_flag = between(flat, "Status Flag:", [" Printed On:"])

    if " Answer List:" in flat:
        values_raw = between(flat, "Answer List:", [" Status Flag:", " Printed On:"])
    elif " Min:" in flat or " Max:" in flat:
        values_raw = between(flat, "Min:", [" Status Flag:", " Printed On:"])
        values_raw = ("Min: " + values_raw).strip() if values_raw else ""
    else:
        values_raw = ""

    return OrderedDict(
        [
            ("found", True),
            ("source_pdf_relative_path", pdf_rel),
            ("source_pdf_page", page_number),
            ("topic", ""),
            ("subtopic", ""),
            ("description", description),
            ("universe", universe),
            ("universe_description", universe_description),
            ("length", length),
            ("status_flag", status_flag),
            ("record_level_or_file", ""),
            ("possible_values", parse_possible_values(values_raw, "old")),
        ]
    )


def extract_codebook_entries(year: str, pdf_path: Path) -> OrderedDict:
    parser = parse_old_page if year in OLD_FORMAT_YEARS else parse_new_page
    pdf_rel = rel(pdf_path)
    reader = PdfReader(str(pdf_path))
    entries = OrderedDict()
    duplicate_pages = []
    for idx, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        entry = parser(text, idx, pdf_rel)
        if not entry:
            continue
        name = ""
        if year in OLD_FORMAT_YEARS:
            flat = norm(text)
            m = re.search(r"(?:^|\s)Variable\s+([A-Za-z0-9_]+)\s+Description:", flat)
            if not m:
                m = re.search(r"(?:^|\s)([A-Za-z0-9_]+)\s+Variable\s+Description:", flat)
            if m:
                name = m.group(1)
        else:
            m = re.search(r"\bName:\s*([A-Za-z0-9_]+)\b", norm(text))
            if m:
                name = m.group(1)
        if not name:
            continue
        if name in entries:
            duplicate_pages.append((name, entries[name]["source_pdf_page"], idx))
            continue
        entries[name] = entry
    entries["_extract_summary"] = OrderedDict(
        [
            ("pdf_pages", len(reader.pages)),
            ("entries_extracted", len(entries)),
            ("duplicate_entry_page_count", len(duplicate_pages)),
            ("duplicate_entry_page_examples", duplicate_pages[:25]),
        ]
    )
    return entries


def add_value_map(value_maps: OrderedDict, possible_values: OrderedDict) -> str:
    payload = json.dumps(possible_values, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    key = "value_map:" + hashlib.sha1(payload.encode("utf-8")).hexdigest()[:16]
    if key not in value_maps:
        value_maps[key] = possible_values
    return key


def main() -> None:
    data = json.loads(COMPACT_JSON.read_text(encoding="utf-8-sig"), object_pairs_hook=OrderedDict)

    codebook_sources = OrderedDict()
    extracted_by_year = OrderedDict()
    for year, pdf_path in PDFS.items():
        codebook_sources[year] = OrderedDict(
            [
                ("source_pdf_relative_path", rel(pdf_path)),
                ("source_pdf_bytes", pdf_path.stat().st_size),
                ("source_pdf_sha256", sha256_file(pdf_path)),
            ]
        )
        extracted_by_year[year] = extract_codebook_entries(year, pdf_path)

    value_maps = OrderedDict()
    coverage = OrderedDict()
    for year, entries in extracted_by_year.items():
        summary = entries.pop("_extract_summary")
        matched = 0
        unmatched_pdf_entries = []
        variables_for_year = 0
        codebook_missing = 0
        for var_name, var_obj in data["variables"].items():
            if year not in var_obj["years"]:
                continue
            variables_for_year += 1
            if var_name not in entries:
                codebook_missing += 1
                continue
            matched += 1
            entry = entries[var_name]
            possible_values = entry.pop("possible_values")
            entry["possible_values_ref"] = add_value_map(value_maps, possible_values)
            var_obj["years"][year]["codebook"] = entry
        for var_name in entries:
            if var_name not in data["variables"] or year not in data["variables"][var_name]["years"]:
                unmatched_pdf_entries.append(var_name)
        coverage[year] = OrderedDict(
            [
                ("schema_variable_count", variables_for_year),
                ("pdf_entries_extracted", summary["entries_extracted"]),
                ("matched_schema_variables", matched),
                ("schema_variables_without_pdf_codebook_entry", codebook_missing),
                ("pdf_entries_not_matched_to_schema", len(unmatched_pdf_entries)),
                ("duplicate_entry_page_count", summary["duplicate_entry_page_count"]),
                ("duplicate_entry_page_examples", summary["duplicate_entry_page_examples"]),
                ("unmatched_pdf_entry_examples", unmatched_pdf_entries[:25]),
            ]
        )

    data["format"]["name"] = "sipp_2018_2024_raw_variable_metadata_enriched_compact"
    data["format"]["version"] = 2
    data["format"][
        "codebook_enrichment_note"
    ] = (
        "Official Census data dictionary/metadata PDFs were parsed for codebook fields. "
        "No value labels, universes, descriptions, or record-level fields were inferred. "
        "If a variable-year has no codebook object, no matching PDF entry was extracted for that exact raw variable name."
    )
    data["codebook_sources"] = codebook_sources
    data["codebook_coverage"] = coverage
    data["value_maps"] = value_maps
    data["summary"]["unique_value_maps"] = len(value_maps)

    OUT_JSON.write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(json.dumps(
        OrderedDict(
            [
                ("output", str(OUT_JSON)),
                ("bytes", OUT_JSON.stat().st_size),
                ("mb", round(OUT_JSON.stat().st_size / (1024 * 1024), 2)),
                ("unique_value_maps", len(value_maps)),
                ("coverage", coverage),
            ]
        ),
        ensure_ascii=False,
        indent=2,
    ))


if __name__ == "__main__":
    main()
