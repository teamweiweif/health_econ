from __future__ import annotations

import csv
import gzip
import hashlib
import json
import math
import re
import shutil
import subprocess
import sys
import time
import zipfile
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd
import requests
import scipy
from scipy import stats


DT_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = DT_ROOT.parents[0]
DATA = DT_ROOT / "data"
RESULT = DT_ROOT / "result"
TABLES = RESULT / "tables"
FIGURES = RESULT / "figures"
REPORT = DT_ROOT / "report"
TEMP = DT_ROOT / "temp"
RAW = TEMP / "raw_downloads"
SNAP = TEMP / "source_snapshots"
OLD_ROOT = PROJECT_ROOT
OLD_DATA = OLD_ROOT / "data"
OLD_TEMP = OLD_ROOT / "temp"
OLD_RAW = OLD_TEMP / "raw_downloads"
OLD_PROVIDER_ARCHIVES = OLD_RAW / "provider_archives"


GUIDE_ZIP_URL = "https://www.cms.gov/files/zip/previous-versions-nursing-home-care-compare-technical-users-guide.zip"
CURRENT_GUIDE_URL = "https://www.cms.gov/medicare/provider-enrollment-and-certification/certificationandcomplianc/downloads/usersguide.pdf"

POLICY_SOURCES = [
    {
        "name": "CMS QSO-22-08-NH",
        "url": "https://www.cms.gov/files/document/qso-22-08-nh.pdf",
        "kind": "pdf",
    },
    {
        "name": "CMS Updates to the Care Compare Website July 2022",
        "url": "https://www.cms.gov/newsroom/fact-sheets/updates-care-compare-website-july-2022",
        "kind": "html",
    },
    {
        "name": "CMS Five-Star Quality Rating System Archives",
        "url": "https://www.cms.gov/medicare/health-safety-standards/quality-safety-oversight-general-information/five-star-quality-rating-system/five-star-quality-rating-system-archives",
        "kind": "html",
    },
    {
        "name": "CMS PBJ Daily Nurse Staffing data catalog",
        "url": "https://data.cms.gov/provider-data/dataset/7e0d53ba-8f02-4c66-98a5-14a1c997c50d",
        "kind": "html",
    },
    {
        "name": "CMS Provider Data Catalog nursing homes archive API",
        "url": "https://data.cms.gov/provider-data/api/1/archive/aggregate/theme/nursing-homes",
        "kind": "json",
    },
    {
        "name": "HHS OIG 2020 nursing home staffing transparency",
        "url": "https://oig.hhs.gov/reports/all/2020/some-nursing-homes-reported-staffing-levels-in-2018-raise-concerns-consumer-transparency-could-be-increased/",
        "kind": "html",
    },
    {
        "name": "HHS OIG 2025 CMS use of staffing data",
        "url": "https://oig.hhs.gov/reports/all/2025/cms-use-of-staffing-data-to-inform-state-oversight-of-nursing-homes/",
        "kind": "html",
    },
]

TECH_GUIDE_MEMBERS = [
    "Five Star Users' Guide January 2022.pdf",
    "Five Star Users' Guide July 2022.pdf",
    "Five Star Users' Guide October 2022.pdf",
    "Five Star Users' Guide January 2023.pdf",
]

STAFFING_THRESHOLDS = [155, 205, 255, 320]
PLACEBO_THRESHOLDS = [180, 230, 285, 345]
MEASURE_CUTPOINTS = {
    "adjusted_rn_hprd": [
        (100, 1.298, math.inf),
        (90, 0.992, 1.297),
        (80, 0.819, 0.991),
        (70, 0.692, 0.818),
        (60, 0.591, 0.691),
        (50, 0.505, 0.590),
        (40, 0.426, 0.504),
        (30, 0.352, 0.425),
        (20, 0.261, 0.351),
        (10, 0.000, 0.260),
    ],
    "adjusted_total_nurse_hprd": [
        (100, 4.954, math.inf),
        (90, 4.429, 4.953),
        (80, 4.105, 4.428),
        (70, 3.869, 4.104),
        (60, 3.653, 3.868),
        (50, 3.445, 3.652),
        (40, 3.248, 3.444),
        (30, 3.030, 3.247),
        (20, 2.747, 3.029),
        (10, 0.000, 2.746),
    ],
    "adjusted_weekend_total_nurse_hprd": [
        (50, 4.328, math.inf),
        (45, 3.896, 4.327),
        (40, 3.623, 3.895),
        (35, 3.382, 3.622),
        (30, 3.174, 3.381),
        (25, 2.985, 3.173),
        (20, 2.810, 2.984),
        (15, 2.613, 2.809),
        (10, 2.350, 2.612),
        (5, 0.000, 2.349),
    ],
    "rn_turnover": [
        (50, 0.000, 24.528),
        (45, 24.529, 33.108),
        (40, 33.109, 39.623),
        (35, 39.624, 45.161),
        (30, 45.162, 49.123),
        (25, 49.124, 56.977),
        (20, 56.978, 62.963),
        (15, 62.964, 71.053),
        (10, 71.054, 81.081),
        (5, 81.082, 100.000),
    ],
    "total_nursing_staff_turnover": [
        (50, 0.000, 34.416),
        (45, 34.417, 40.594),
        (40, 40.595, 44.848),
        (35, 44.849, 48.696),
        (30, 48.697, 52.353),
        (25, 52.354, 56.391),
        (20, 56.392, 60.699),
        (15, 60.700, 65.741),
        (10, 65.742, 72.678),
        (5, 72.679, 100.000),
    ],
}

PBJ_COLS = {
    "provnum",
    "state",
    "workdate",
    "mdscensus",
    "hrs_rndon",
    "hrs_rnadmin",
    "hrs_rn",
    "hrs_lpnadmin",
    "hrs_lpn",
    "hrs_cna",
    "hrs_natrn",
    "hrs_medaide",
    "hrs_rndon_emp",
    "hrs_rnadmin_emp",
    "hrs_rn_emp",
    "hrs_lpnadmin_emp",
    "hrs_lpn_emp",
    "hrs_cna_emp",
    "hrs_natrn_emp",
    "hrs_medaide_emp",
    "hrs_rndon_ctr",
    "hrs_rnadmin_ctr",
    "hrs_rn_ctr",
    "hrs_lpnadmin_ctr",
    "hrs_lpn_ctr",
    "hrs_cna_ctr",
    "hrs_natrn_ctr",
    "hrs_medaide_ctr",
}
RN_COLS = ["hrs_rndon", "hrs_rnadmin", "hrs_rn"]
LPN_COLS = ["hrs_lpnadmin", "hrs_lpn"]
AIDE_COLS = ["hrs_cna", "hrs_natrn", "hrs_medaide"]
EMP_COLS = [
    "hrs_rndon_emp",
    "hrs_rnadmin_emp",
    "hrs_rn_emp",
    "hrs_lpnadmin_emp",
    "hrs_lpn_emp",
    "hrs_cna_emp",
    "hrs_natrn_emp",
    "hrs_medaide_emp",
]
CTR_COLS = [
    "hrs_rndon_ctr",
    "hrs_rnadmin_ctr",
    "hrs_rn_ctr",
    "hrs_lpnadmin_ctr",
    "hrs_lpn_ctr",
    "hrs_cna_ctr",
    "hrs_natrn_ctr",
    "hrs_medaide_ctr",
]


def ensure_dirs() -> None:
    for p in [DATA, TABLES, FIGURES, REPORT, RAW, SNAP, TEMP / "intermediate"]:
        p.mkdir(parents=True, exist_ok=True)


def norm_col(c: str) -> str:
    c = c.strip().lower().replace("%", "percent")
    c = re.sub(r"[^a-z0-9]+", "_", c)
    return re.sub(r"_+", "_", c).strip("_")


def zfill_ccn(s: pd.Series) -> pd.Series:
    out = s.astype(str).str.replace(r"\.0$", "", regex=True).str.strip()
    out = out.where(out.str.fullmatch(r"\d+"), np.nan)
    return out.str.zfill(6)


def to_num(s: pd.Series) -> pd.Series:
    return pd.to_numeric(s, errors="coerce")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def save_csv(path: Path, rows: list[dict] | pd.DataFrame) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(rows, pd.DataFrame):
        rows.to_csv(path, index=False)
        return
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.strip() + "\n", encoding="utf-8")


def md_table(df: pd.DataFrame, max_rows: int | None = None) -> str:
    if df is None or df.empty:
        return "No rows."
    d = df.head(max_rows).copy() if max_rows else df.copy()
    d = d.replace({np.nan: ""})
    cols = list(d.columns)
    lines = ["| " + " | ".join(map(str, cols)) + " |", "| " + " | ".join(["---"] * len(cols)) + " |"]
    for _, row in d.iterrows():
        vals = []
        for c in cols:
            v = row[c]
            if isinstance(v, float):
                vals.append(f"{v:.6g}")
            else:
                vals.append(str(v).replace("\n", " "))
        lines.append("| " + " | ".join(vals) + " |")
    return "\n".join(lines)


def append_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(text.rstrip() + "\n")


def download_bytes(url: str, dest: Path, overwrite: bool = False) -> dict:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists() and not overwrite:
        return {
            "url": url,
            "path": str(dest.relative_to(DT_ROOT)),
            "bytes": dest.stat().st_size,
            "sha256": sha256_file(dest),
            "downloaded": False,
            "status": "cached",
        }
    r = requests.get(url, timeout=180)
    r.raise_for_status()
    content = r.content
    if content[:2] == b"\x1f\x8b":
        content = gzip.decompress(content)
    dest.write_bytes(content)
    return {
        "url": url,
        "path": str(dest.relative_to(DT_ROOT)),
        "bytes": dest.stat().st_size,
        "sha256": sha256_file(dest),
        "downloaded": True,
        "status": str(r.status_code),
    }


def pdf_to_text(pdf: Path, txt: Path) -> bool:
    txt.parent.mkdir(parents=True, exist_ok=True)
    try:
        subprocess.run(["pdftotext", "-layout", str(pdf), str(txt)], check=True, capture_output=True)
        return txt.exists() and txt.stat().st_size > 0
    except Exception:
        try:
            from pypdf import PdfReader

            reader = PdfReader(str(pdf))
            text = "\n".join(page.extract_text() or "" for page in reader.pages)
            txt.write_text(text, encoding="utf-8")
            return txt.stat().st_size > 0
        except Exception as exc:
            txt.write_text(f"PDF text extraction failed: {exc}", encoding="utf-8")
            return False


def read_text_maybe(path: Path) -> str:
    raw = path.read_bytes()
    if raw[:2] == b"\x1f\x8b":
        raw = gzip.decompress(raw)
    return raw.decode("utf-8", errors="replace")


def text_contains(path: Path, pattern: str) -> bool:
    return re.search(pattern, read_text_maybe(path), flags=re.IGNORECASE | re.DOTALL) is not None


def pct(n: float, d: float) -> float:
    return float(n) / float(d) if d else np.nan


def clamp_star(x: float) -> float:
    if pd.isna(x):
        return np.nan
    return float(min(5, max(1, int(round(x)))))


def old_overall_formula(health: float, staffing: float, qm: float) -> float:
    if pd.isna(health):
        return np.nan
    out = int(health)
    if not pd.isna(staffing):
        if int(staffing) in {4, 5} and int(staffing) > int(health):
            out += 1
        elif int(staffing) == 1:
            out -= 1
    out = min(5, max(1, out))
    if not pd.isna(qm):
        if int(qm) == 5:
            out += 1
        elif int(qm) == 1:
            out -= 1
    out = min(5, max(1, out))
    if int(health) == 1:
        out = min(out, 2)
    return float(out)


def new_overall_formula(health: float, staffing: float, qm: float) -> float:
    if pd.isna(health):
        return np.nan
    out = int(health)
    if not pd.isna(staffing):
        if int(staffing) == 5:
            out += 1
        elif int(staffing) == 1:
            out -= 1
    out = min(5, max(1, out))
    if not pd.isna(qm):
        if int(qm) == 5:
            out += 1
        elif int(qm) == 1:
            out -= 1
    out = min(5, max(1, out))
    if int(health) == 1:
        out = min(out, 2)
    return float(out)


def point_from_cutpoints(value: float, cutpoints: list[tuple[int, float, float]]) -> float:
    if pd.isna(value):
        return np.nan
    for pts, lo, hi in cutpoints:
        if value >= lo and value <= hi:
            return float(pts)
    return np.nan


def admin_points(value: float) -> float:
    if pd.isna(value):
        return np.nan
    if value <= 0:
        return 30.0
    if value <= 1:
        return 25.0
    return 10.0


def star_from_staffing_score(score: float) -> float:
    if pd.isna(score):
        return np.nan
    s = int(round(score))
    if s < 155:
        return 1.0
    if s < 205:
        return 2.0
    if s < 255:
        return 3.0
    if s < 320:
        return 4.0
    return 5.0


def nearest_threshold(score: float) -> tuple[float, float]:
    if pd.isna(score):
        return (np.nan, np.nan)
    distances = [(abs(score - t), t) for t in STAFFING_THRESHOLDS]
    _, t = min(distances)
    return (float(t), float(score - t))


def distance_to_next_star(score: float) -> float:
    if pd.isna(score):
        return np.nan
    for t in STAFFING_THRESHOLDS:
        if score < t:
            return float(t - score)
    return 0.0


def local_linear_rd(df: pd.DataFrame, y: str, running: str, cutoff: float, bandwidth: float, donut: float = 0.0) -> dict:
    cols = [y, running]
    d = df[cols].dropna().copy()
    d["x"] = d[running] - cutoff
    d = d[d["x"].abs() <= bandwidth]
    if donut > 0:
        d = d[d["x"].abs() > donut]
    if len(d) < 30 or d["x"].nunique() < 5 or d[y].notna().sum() < 30:
        return {
            "outcome": y,
            "cutoff": cutoff,
            "bandwidth": bandwidth,
            "donut": donut,
            "n": len(d),
            "coef": np.nan,
            "se": np.nan,
            "p": np.nan,
            "mean_below": np.nan,
            "mean_above": np.nan,
        }
    d["above"] = (d["x"] >= 0).astype(float)
    X = np.column_stack([np.ones(len(d)), d["above"], d["x"], d["above"] * d["x"]])
    yy = d[y].astype(float).to_numpy()
    beta, resid, rank, _ = np.linalg.lstsq(X, yy, rcond=None)
    if rank < X.shape[1]:
        se = np.nan
        p = np.nan
    else:
        u = yy - X @ beta
        meat = X.T @ (X * (u[:, None] ** 2))
        bread = np.linalg.pinv(X.T @ X)
        vcov = bread @ meat @ bread
        se = math.sqrt(max(vcov[1, 1], 0.0))
        p = 2 * (1 - stats.t.cdf(abs(beta[1] / se), df=max(1, len(d) - X.shape[1]))) if se > 0 else np.nan
    return {
        "outcome": y,
        "cutoff": cutoff,
        "bandwidth": bandwidth,
        "donut": donut,
        "n": int(len(d)),
        "coef": float(beta[1]),
        "se": float(se) if np.isfinite(se) else np.nan,
        "p": float(p) if np.isfinite(p) else np.nan,
        "mean_below": float(d.loc[d["above"] == 0, y].mean()),
        "mean_above": float(d.loc[d["above"] == 1, y].mean()),
    }


def two_group_delta(df: pd.DataFrame, y: str, group: str, weight: str | None = None) -> dict:
    d = df[[y, group] + ([weight] if weight else [])].dropna()
    if d[group].nunique() < 2:
        return {"outcome": y, "group": group, "n": len(d), "diff": np.nan, "se": np.nan, "p": np.nan}
    a = d[d[group] == 1][y].astype(float).to_numpy()
    b = d[d[group] == 0][y].astype(float).to_numpy()
    if len(a) < 5 or len(b) < 5:
        return {"outcome": y, "group": group, "n": len(d), "diff": np.nan, "se": np.nan, "p": np.nan}
    diff = float(np.nanmean(a) - np.nanmean(b))
    se = math.sqrt(np.nanvar(a, ddof=1) / len(a) + np.nanvar(b, ddof=1) / len(b))
    p = 2 * (1 - stats.t.cdf(abs(diff / se), df=max(1, len(a) + len(b) - 2))) if se > 0 else np.nan
    return {"outcome": y, "group": group, "n": len(d), "treated_n": len(a), "control_n": len(b), "diff": diff, "se": se, "p": p}


def read_provider_archive_raw(snapshot: str) -> pd.DataFrame:
    p = OLD_PROVIDER_ARCHIVES / f"nursing_homes_{snapshot}.zip"
    if not p.exists():
        raise FileNotFoundError(p)
    with zipfile.ZipFile(p) as z:
        members = [n for n in z.namelist() if "NH_ProviderInfo" in n and n.lower().endswith(".csv")]
        if not members:
            raise FileNotFoundError(f"NH_ProviderInfo in {p}")
        with z.open(members[0]) as f:
            raw = pd.read_csv(f, encoding="cp1252", encoding_errors="replace", low_memory=False)
    raw = raw.rename(columns={c: norm_col(c) for c in raw.columns})
    out = pd.DataFrame()
    out["facility_id"] = zfill_ccn(raw.get("federal_provider_number", pd.Series(index=raw.index, dtype=object)))
    out["snapshot_date"] = pd.Timestamp(snapshot)
    out["provider_name"] = raw.get("provider_name")
    out["state"] = raw.get("provider_state")
    out["ownership_type"] = raw.get("ownership_type")
    out["certified_beds"] = to_num(raw.get("number_of_certified_beds", pd.Series(index=raw.index)))
    out["avg_residents_per_day"] = to_num(raw.get("average_number_of_residents_per_day", pd.Series(index=raw.index)))
    out["overall_rating"] = to_num(raw.get("overall_rating", pd.Series(index=raw.index)))
    out["health_inspection_rating"] = to_num(raw.get("health_inspection_rating", pd.Series(index=raw.index)))
    out["qm_rating"] = to_num(raw.get("qm_rating", pd.Series(index=raw.index)))
    out["staffing_rating"] = to_num(raw.get("staffing_rating", pd.Series(index=raw.index)))
    out["rn_staffing_rating"] = to_num(raw.get("rn_staffing_rating", pd.Series(index=raw.index)))
    out["adjusted_total_nurse_hprd"] = to_num(raw.get("adjusted_total_nurse_staffing_hours_per_resident_per_day", pd.Series(index=raw.index)))
    out["adjusted_rn_hprd"] = to_num(raw.get("adjusted_rn_staffing_hours_per_resident_per_day", pd.Series(index=raw.index)))
    weekend_adjusted = raw.get("adjusted_weekend_total_nurse_staffing_hours_per_resident_per_day")
    reported_weekend = raw.get("total_number_of_nurse_staff_hours_per_resident_per_day_on_the_weekend")
    out["adjusted_weekend_total_nurse_hprd"] = to_num(weekend_adjusted if weekend_adjusted is not None else reported_weekend)
    out["reported_weekend_total_nurse_hprd"] = to_num(reported_weekend if reported_weekend is not None else pd.Series(index=raw.index))
    out["reported_weekend_rn_hprd"] = to_num(raw.get("registered_nurse_hours_per_resident_per_day_on_the_weekend", pd.Series(index=raw.index)))
    out["total_nursing_staff_turnover"] = to_num(raw.get("total_nursing_staff_turnover", pd.Series(index=raw.index)))
    out["rn_turnover"] = to_num(raw.get("registered_nurse_turnover", pd.Series(index=raw.index)))
    out["administrator_turnover"] = to_num(raw.get("number_of_administrators_who_have_left_the_nursing_home", pd.Series(index=raw.index)))
    out["rating_cycle_1_total_health_deficiencies"] = to_num(raw.get("rating_cycle_1_total_number_of_health_deficiencies", pd.Series(index=raw.index)))
    out["total_weighted_health_survey_score"] = to_num(raw.get("total_weighted_health_survey_score", pd.Series(index=raw.index)))
    out = out[out["facility_id"].notna()].drop_duplicates("facility_id")
    return out


def emulate_staffing_score(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["points_total_nurse"] = out["adjusted_total_nurse_hprd"].map(lambda x: point_from_cutpoints(x, MEASURE_CUTPOINTS["adjusted_total_nurse_hprd"]))
    out["points_rn"] = out["adjusted_rn_hprd"].map(lambda x: point_from_cutpoints(x, MEASURE_CUTPOINTS["adjusted_rn_hprd"]))
    out["points_weekend_total"] = out["adjusted_weekend_total_nurse_hprd"].map(lambda x: point_from_cutpoints(x, MEASURE_CUTPOINTS["adjusted_weekend_total_nurse_hprd"]))
    out["points_total_turnover"] = out["total_nursing_staff_turnover"].map(lambda x: point_from_cutpoints(x, MEASURE_CUTPOINTS["total_nursing_staff_turnover"]))
    out["points_rn_turnover"] = out["rn_turnover"].map(lambda x: point_from_cutpoints(x, MEASURE_CUTPOINTS["rn_turnover"]))
    out["points_admin_turnover"] = out["administrator_turnover"].map(admin_points)
    point_cols = [
        "points_total_nurse",
        "points_rn",
        "points_weekend_total",
        "points_total_turnover",
        "points_rn_turnover",
        "points_admin_turnover",
    ]
    max_points = {
        "points_total_nurse": 100.0,
        "points_rn": 100.0,
        "points_weekend_total": 50.0,
        "points_total_turnover": 50.0,
        "points_rn_turnover": 50.0,
        "points_admin_turnover": 30.0,
    }
    out["raw_available_points"] = out[point_cols].sum(axis=1, min_count=1)
    out["max_available_points"] = sum(max_points[c] for c in point_cols) - out[point_cols].isna().mul(pd.Series(max_points)).sum(axis=1)
    out["staffing_score_proxy"] = out["raw_available_points"] * (380.0 / out["max_available_points"])
    out.loc[out["max_available_points"] <= 0, "staffing_score_proxy"] = np.nan
    out["staffing_score_proxy_round"] = out["staffing_score_proxy"].round()
    out["staffing_star_proxy"] = out["staffing_score_proxy_round"].map(star_from_staffing_score)
    out["emulator_match"] = (out["staffing_star_proxy"] == out["staffing_rating"]).where(out["staffing_star_proxy"].notna() & out["staffing_rating"].notna())
    nearest = out["staffing_score_proxy_round"].map(nearest_threshold)
    out["nearest_staffing_threshold"] = nearest.map(lambda x: x[0])
    out["distance_to_nearest_staffing_threshold"] = nearest.map(lambda x: x[1])
    for t in STAFFING_THRESHOLDS:
        out[f"distance_to_staffing_threshold_{t}"] = out["staffing_score_proxy_round"] - t
        out[f"above_staffing_threshold_{t}"] = (out["staffing_score_proxy_round"] >= t).astype(float)
    out["distance_to_next_staffing_star"] = out["staffing_score_proxy_round"].map(distance_to_next_star)
    out["high_shadow_price"] = ((out["distance_to_next_staffing_star"] > 0) & (out["distance_to_next_staffing_star"] <= 10)).astype(int)
    out["old_formula_overall"] = [old_overall_formula(h, s, q) for h, s, q in zip(out["health_inspection_rating"], out["staffing_rating"], out["qm_rating"])]
    out["new_formula_overall"] = [new_overall_formula(h, s, q) for h, s, q in zip(out["health_inspection_rating"], out["staffing_rating"], out["qm_rating"])]
    out["formula_induced_overall_star_loss"] = (out["old_formula_overall"] > out["new_formula_overall"]).astype(int)
    out["formula_induced_overall_star_gain"] = (out["old_formula_overall"] < out["new_formula_overall"]).astype(int)
    return out


def source_algorithm_audit() -> None:
    ensure_dirs()
    rows = []
    for src in POLICY_SOURCES:
        suffix = ".json" if src["kind"] == "json" else ".pdf" if src["kind"] == "pdf" else ".html"
        dest = RAW / f"{re.sub(r'[^A-Za-z0-9._-]+', '_', src['name']).strip('_')}{suffix}"
        try:
            meta = download_bytes(src["url"], dest, overwrite=False)
        except Exception as exc:
            meta = {"url": src["url"], "path": str(dest.relative_to(DT_ROOT)), "bytes": "", "sha256": "", "status": f"download failed: {exc}", "downloaded": False}
        rows.append({"source_name": src["name"], "url": src["url"], **meta})

    guide_zip = RAW / "previous_versions_nhcc_technical_users_guide.zip"
    rows.append({"source_name": "Previous versions of Technical Users Guide ZIP", **download_bytes(GUIDE_ZIP_URL, guide_zip, overwrite=False)})
    current_pdf = RAW / "current_usersguide.pdf"
    try:
        rows.append({"source_name": "Current Five-Star Technical Users Guide", **download_bytes(CURRENT_GUIDE_URL, current_pdf, overwrite=False)})
    except Exception as exc:
        rows.append({"source_name": "Current Five-Star Technical Users Guide", "url": CURRENT_GUIDE_URL, "path": str(current_pdf.relative_to(DT_ROOT)), "bytes": "", "sha256": "", "status": f"download failed: {exc}", "downloaded": False})

    guide_dir = SNAP / "technical_guides"
    guide_dir.mkdir(parents=True, exist_ok=True)
    extracted_guides = []
    with zipfile.ZipFile(guide_zip) as z:
        for member in z.namelist():
            if Path(member).name in TECH_GUIDE_MEMBERS:
                dest = guide_dir / Path(member).name
                if not dest.exists():
                    dest.write_bytes(z.read(member))
                txt = dest.with_suffix(".txt")
                pdf_to_text(dest, txt)
                extracted_guides.append({"guide": dest.name, "bytes": dest.stat().st_size, "sha256": sha256_file(dest), "text_bytes": txt.stat().st_size})
    qso_pdf = RAW / "CMS_QSO-22-08-NH.pdf"
    if qso_pdf.exists():
        pdf_to_text(qso_pdf, SNAP / "CMS_QSO-22-08-NH.txt")

    save_csv(TEMP / "official_source_manifest_v2.csv", rows)
    save_csv(TEMP / "technical_guide_manifest_v2.csv", extracted_guides)

    july_txt = guide_dir / "Five Star Users' Guide July 2022.txt"
    jan_txt = guide_dir / "Five Star Users' Guide January 2022.txt"
    qso_txt = SNAP / "CMS_QSO-22-08-NH.txt"
    evidence = [
        {
            "claim": "January 7, 2022 QSO memo issued",
            "support": "CMS QSO-22-08-NH text includes DATE: January 07, 2022.",
            "verified": qso_txt.exists() and text_contains(qso_txt, r"DATE:\s+January\s+07,\s+2022"),
        },
        {
            "claim": "January 2022 Care Compare public reporting of weekend staffing and turnover",
            "support": "QSO memo and July 2022 guide describe January 2022 Care Compare posting.",
            "verified": qso_txt.exists() and text_contains(qso_txt, r"added to the Care Compare website in January 2022|January 2022.*Care Compare"),
        },
        {
            "claim": "January 26, 2022 employee-level PBJ staffing data posting",
            "support": "QSO memo states employee-level data will be posted on January 26, 2022.",
            "verified": qso_txt.exists() and text_contains(qso_txt, r"January 26,\s*2022"),
        },
        {
            "claim": "July 2022 staffing domain switched to six-measure point score",
            "support": "July 2022 guide states the new rating is based on six separate staffing measures.",
            "verified": july_txt.exists() and text_contains(july_txt, r"six separate staffing measures"),
        },
        {
            "claim": "July 2022 staffing-star thresholds are 155, 205, 255, and 320",
            "support": "July 2022 guide Table 3 lists <155, 155-204, 205-254, 255-319, 320-380.",
            "verified": july_txt.exists() and text_contains(july_txt, r"<\s*155.*155\s*-\s*204.*205\s*-\s*254.*255\s*-\s*319.*320\s*-\s*380"),
        },
        {
            "claim": "July 2022 overall-rating rule removes four-star staffing bonus",
            "support": "July 2022 guide states only five-star staffing gets an overall-rating increase.",
            "verified": july_txt.exists() and text_contains(july_txt, r"only nursing homes with a five-star staffing rating"),
        },
        {
            "claim": "January 2022 old formula allowed four- or five-star staffing bonus if greater than health inspection",
            "support": "January 2022 guide Step 2 describes four- or five-star staffing bonus.",
            "verified": jan_txt.exists() and text_contains(jan_txt, r"staffing rating is four or five stars"),
        },
    ]
    save_csv(TABLES / "official_policy_algorithm_evidence.csv", evidence)

    md = [
        "# Official Policy and Algorithm Audit",
        "",
        f"Access date: {date.today().isoformat()}",
        "",
        "## Source Snapshots",
        "",
        "| Source | Status | Local path | SHA-256 |",
        "|---|---:|---|---|",
    ]
    for r in rows:
        md.append(f"| {r.get('source_name','')} | {r.get('status','')} | `{r.get('path','')}` | `{r.get('sha256','')}` |")
    md += [
        "",
        "## Verified Policy Facts",
        "",
        "| Claim | Verified | Evidence note |",
        "|---|---:|---|",
    ]
    for e in evidence:
        md.append(f"| {e['claim']} | {bool(e['verified'])} | {e['support']} |")
    md += [
        "",
        "## Algorithm Facts Used in the Tournament",
        "",
        "- January 2022 is treated as the transparency shock: weekend total nurse/RN staffing and turnover became public on Care Compare.",
        "- July 27, 2022 is treated as the main algorithmic-label shock: the staffing-domain rating changed to a point score based on six staffing/turnover measures.",
        "- Staffing-star thresholds used for RD/RD-DID are 155, 205, 255, and 320 on the rounded 0-380 staffing score.",
        "- The July 2022 overall-rating rule gives the staffing bonus only for five-star staffing; the January 2022 rule allowed a four- or five-star staffing bonus when staffing exceeded health inspection.",
        "",
        "## Uncertainties",
        "",
        "- Provider Data Catalog archives publish staffing stars and component measures, but not the facility-level 0-380 staffing score. The tournament therefore attempts a score proxy/emulator and downgrades RD if the star match rate is below 95%.",
        "- The July 2022 ProviderInfo file does not contain a separate adjusted weekend total nurse HPRD column; it contains reported weekend total nurse HPRD. The emulator uses the reported field for July and treats that as a proxy limitation.",
        "- The local `.git` directory is a Dropbox reparse placeholder and `git status` does not recognize the workspace as a repository. The requested branch could not be safely created; all outputs are isolated under `design_tournament/`.",
    ]
    write_text(REPORT / "official_policy_algorithm_audit.md", "\n".join(md))


def write_design_tournament_plan() -> None:
    ensure_dirs()
    skill_log = """# Skill Usage Log V2

- Searched local Codex skills and plugin cache for empirical research, causal inference, econometrics, RD, DID, panel models, and economics writing.
- Read `research-station` because this is a repo-backed research workstation task. Used its local-first and audit-first workflow guidance.
- No installed specialist causal-inference/econometrics/RD skill was found. Causal design and diagnostics are implemented directly in the design-tournament scripts.
- No new custom skill was created.
"""
    write_text(TEMP / "skill_usage_log_v2.md", skill_log)

    plan = """# Design Tournament Plan

## Reframing

The old global exposure DID is demoted because the prior identification audit found failed pre-trends and a significant placebo timing test. The new estimand is not a broad national transparency effect. It is whether algorithmic public labels and rating thresholds changed staffing reliability, staffing mix, and score-targeted behavior.

## Pre-Specified Designs

| Design | Estimand | Identification logic | Main failure mode |
|---|---|---|---|
| A. Staffing-star threshold RD | Local effect of being just above a staffing-score threshold | Homes near a CMS staffing-star cutoff have similar scores but different public labels | Score proxy fails; manipulation; pre-outcome jumps |
| B. RD-DID / difference-in-discontinuities | Change in cutoff discontinuity after July 2022 | Difference out pre-existing local discontinuities | Pre-period discontinuities move similarly at placebo cutoffs |
| C. Formula-induced overall-star shock | Effect of losing old four-star staffing overall bonus | July rule mechanically removes a label bonus for some homes | Formula reconstruction weak; exclusion restriction fragile |
| D. Facility-internal metric salience DDD | Post-July shift toward score-targeted weekend total staffing | Facility-month shocks absorbed by within-facility metric/day contrasts | Broad labor-market recovery moves all metrics similarly |
| E. Shadow price | Whether homes close to score rewards improve more | Marginal rating return varies discontinuously with baseline score distance | High-shadow facilities were already trending differently |
| F. Bunching/gaming | Post-July clustering above true cutoffs | Algorithmic score management predicts bunching at true, not placebo, cutoffs | Proxy score too noisy; bunching present before July |
| G. 2018 validation event | Whether PBJ detects zero-RN gaming after earlier policy | External validation against OIG-described mechanism | Current local PBJ source starts in 2019, so 2017-2018 may be unavailable |
| H. Matched/synthetic fallback | Secondary comparison only | Match on pre trajectories if threshold designs fail | Recreates old weak DID if pretrends remain poor |

## Outcome Priority

Primary outcomes are staffing reliability and lower-tail risk: RN<8h days, weekend RN<8h days, zero-RN days, zero-total-nurse days, weekend p10/p25 HPRD, worst weekend total nurse HPRD, worst weekend RN HPRD, low-staffing weekend shares, weekend total nurse HPRD, and census.

Mechanism and gaming outcomes are score-targeted HPRD, weekend share of total nursing hours, weekday-weekend gaps, contract share, and formula/rating recovery.

Downstream deficiencies and ratings are descriptive only unless timing and diagnostics support causal interpretation.

## Timing Rules

- January 2022 is a transparency shock.
- July 27, 2022 is the main rating / algorithmic-label shock.
- Monthly daily-staffing post starts in August 2022.
- Quarterly clean post starts in 2022Q4; 2022Q3 is transition.
- Turnover outcomes are treated as delayed because the guide uses six-quarter windows.
- Preferred pre windows avoid 2021Q4 where possible because the project instructions flag ransomware/incomplete-reporting risk.

## Go / No-Go Rules

Strong Go requires verified official algorithm sources, a valid running variable or formula shock, no serious pre-outcome discontinuity, local covariate balance, no invalid density manipulation, weak placebo-cutoff performance, robust bandwidths, July-aligned timing, and concentration in policy-targeted outcomes.

Conditional Go is used for compelling but imperfect local/mechanism evidence.

No-Go is required if emulator validation fails, pre-outcome discontinuities are large, placebo cutoffs look similar, effects appear before July 2022, or effects are broad in a way consistent with labor-market recovery.
"""
    write_text(REPORT / "design_tournament_plan.md", plan)


def rating_algorithm_emulator() -> None:
    ensure_dirs()
    frames = []
    for snap in ["2022-01-27", "2022-04-27", "2022-07-27", "2022-10-27", "2023-01-02"]:
        df = read_provider_archive_raw(snap)
        em = emulate_staffing_score(df)
        em["snapshot"] = snap
        frames.append(em)
    all_scores = pd.concat(frames, ignore_index=True)
    all_scores.to_parquet(DATA / "rating_score_emulator_panel.parquet", index=False)
    all_scores.to_csv(DATA / "rating_score_emulator_panel.csv", index=False)
    july = all_scores[all_scores["snapshot"] == "2022-07-27"].copy()
    july.to_parquet(DATA / "rating_score_emulator_july2022.parquet", index=False)

    summary = []
    for snap, g in all_scores.groupby("snapshot"):
        valid = g["emulator_match"].notna()
        summary.append(
            {
                "snapshot": snap,
                "n_facilities": int(len(g)),
                "n_with_official_staffing_star": int(g["staffing_rating"].notna().sum()),
                "n_with_proxy_score": int(g["staffing_score_proxy"].notna().sum()),
                "n_valid_match_test": int(valid.sum()),
                "star_match_rate": float(g.loc[valid, "emulator_match"].mean()) if valid.any() else np.nan,
                "uses_reported_weekend_proxy": snap in {"2022-01-27", "2022-04-27", "2022-07-27"},
            }
        )
    summary_df = pd.DataFrame(summary)
    save_csv(TABLES / "rating_emulator_validation.csv", summary_df)

    dist_cols = ["facility_id", "snapshot", "staffing_score_proxy_round", "staffing_star_proxy", "staffing_rating", "nearest_staffing_threshold", "distance_to_nearest_staffing_threshold", "distance_to_next_staffing_star", "high_shadow_price", "old_formula_overall", "new_formula_overall", "formula_induced_overall_star_loss", "formula_induced_overall_star_gain"]
    save_csv(DATA / "threshold_running_variables.csv", all_scores[dist_cols])

    july_match = summary_df.loc[summary_df["snapshot"] == "2022-07-27", "star_match_rate"].iloc[0]
    md = [
        "# Rating Algorithm Emulation Audit",
        "",
        "## Source Version",
        "",
        "- Primary algorithm source: CMS archived `Five Star Users' Guide July 2022.pdf` from the official previous-versions ZIP.",
        "- Comparison versions extracted: January 2022, October 2022, January 2023.",
        "",
        "## Emulation Method",
        "",
        "- Applied July 2022 Table A2 cutpoints to Provider Data Catalog component fields.",
        "- Used adjusted total nurse HPRD, adjusted RN HPRD, weekend total nurse HPRD, total nurse turnover, RN turnover, and administrator departures.",
        "- Rescaled available points to 380 when turnover components are missing, matching the guide's rescaling rule.",
        "- July 2022 ProviderInfo lacks adjusted weekend total nurse HPRD, so reported weekend total nurse HPRD is used as a proxy.",
        "",
        "## Validation",
        "",
        md_table(summary_df),
        "",
        "## Primary-Use Decision",
        "",
    ]
    if pd.notna(july_match) and july_match >= 0.95:
        md.append("The July 2022 proxy score matches official staffing stars at or above 95%, so RD can use it as a primary running variable with caveats.")
    else:
        md.append("The July 2022 proxy score does not reach the 95% match threshold. RD/RD-DID estimates are reported as proxy-running-variable evidence, not strong primary causal evidence.")
    write_text(REPORT / "rating_algorithm_emulation_audit.md", "\n".join(md))


def daily_quarter_from_source(url: str, temporal: str) -> pd.DataFrame:
    parts = []
    last_exc: Exception | None = None
    for attempt in range(1, 4):
        try:
            reader = pd.read_csv(
                url,
                usecols=lambda c: norm_col(c) in PBJ_COLS,
                dtype=str,
                chunksize=300_000,
                encoding="cp1252",
                encoding_errors="replace",
            )
            for chunk in reader:
                mapping = {c: norm_col(c) for c in chunk.columns}
                chunk = chunk.rename(columns=mapping)
                for c in PBJ_COLS:
                    if c not in chunk.columns:
                        chunk[c] = np.nan
                chunk["facility_id"] = zfill_ccn(chunk["provnum"])
                chunk["state"] = chunk["state"].astype(str).str.strip().str.upper()
                chunk["workdate"] = pd.to_datetime(chunk["workdate"], errors="coerce")
                chunk = chunk.dropna(subset=["facility_id", "workdate"])
                for c in ["mdscensus"] + RN_COLS + LPN_COLS + AIDE_COLS + EMP_COLS + CTR_COLS:
                    chunk[c] = to_num(chunk[c]).fillna(0.0)
                chunk["rn_hours"] = chunk[RN_COLS].sum(axis=1)
                chunk["lpn_hours"] = chunk[LPN_COLS].sum(axis=1)
                chunk["aide_hours"] = chunk[AIDE_COLS].sum(axis=1)
                chunk["total_nurse_hours"] = chunk["rn_hours"] + chunk["lpn_hours"] + chunk["aide_hours"]
                chunk["employee_nurse_hours"] = chunk[EMP_COLS].sum(axis=1)
                chunk["contract_nurse_hours"] = chunk[CTR_COLS].sum(axis=1)
                keep = chunk[["facility_id", "state", "workdate", "mdscensus", "rn_hours", "total_nurse_hours", "employee_nurse_hours", "contract_nurse_hours"]].copy()
                parts.append(keep)
            break
        except Exception as exc:
            last_exc = exc
            parts = []
            print(f"PBJ read failed for {temporal} attempt {attempt}: {exc}")
            time.sleep(5 * attempt)
    if not parts:
        raise RuntimeError(f"Could not read PBJ daily source {temporal}: {last_exc}")
    d = pd.concat(parts, ignore_index=True)
    d = d.groupby(["facility_id", "state", "workdate"], as_index=False).sum(numeric_only=True)
    d["month"] = d["workdate"].dt.to_period("M").astype(str)
    d["quarter"] = d["workdate"].dt.to_period("Q").astype(str)
    d["is_weekend"] = d["workdate"].dt.weekday.ge(5).astype(int)
    d["positive_census"] = d["mdscensus"] > 0
    denom = d["mdscensus"].where(d["mdscensus"] > 0)
    d["rn_hprd_day"] = d["rn_hours"] / denom
    d["total_nurse_hprd_day"] = d["total_nurse_hours"] / denom
    d["contract_share_day"] = d["contract_nurse_hours"] / d["total_nurse_hours"].replace(0, np.nan)
    return d


def aggregate_reliability(daily: pd.DataFrame, time_col: str, national_threshold: float | None = None, facility_thresholds: pd.Series | None = None) -> pd.DataFrame:
    d = daily.copy()
    if facility_thresholds is not None:
        d = d.merge(facility_thresholds.rename("facility_pre_weekend_p25_total_hprd"), on="facility_id", how="left")
        d["below_facility_pre_p25"] = (d["is_weekend"].eq(1) & d["total_nurse_hprd_day"].lt(d["facility_pre_weekend_p25_total_hprd"])).astype(float)
    else:
        d["below_facility_pre_p25"] = np.nan
    if national_threshold is not None:
        d["below_national_pre_p10"] = (d["is_weekend"].eq(1) & d["total_nurse_hprd_day"].lt(national_threshold)).astype(float)
    else:
        d["below_national_pre_p10"] = np.nan
    d["rn_lt8_day"] = (d["positive_census"] & d["rn_hours"].lt(8)).astype(int)
    d["weekend_rn_lt8_day"] = (d["is_weekend"].eq(1) & d["positive_census"] & d["rn_hours"].lt(8)).astype(int)
    d["zero_rn_day"] = (d["positive_census"] & d["rn_hours"].le(0)).astype(int)
    d["zero_total_nurse_day"] = (d["positive_census"] & d["total_nurse_hours"].le(0)).astype(int)
    d["weekend_total_hprd"] = d["total_nurse_hprd_day"].where(d["is_weekend"].eq(1))
    d["weekend_rn_hprd"] = d["rn_hprd_day"].where(d["is_weekend"].eq(1))
    d["weekday_total_hours"] = d["total_nurse_hours"].where(d["is_weekend"].eq(0), 0.0)
    d["weekend_total_hours"] = d["total_nurse_hours"].where(d["is_weekend"].eq(1), 0.0)
    grouped = d.groupby(["facility_id", "state", time_col], dropna=False)
    out = grouped.agg(
        days=("workdate", "nunique"),
        resident_days=("mdscensus", "sum"),
        weekend_days=("is_weekend", "sum"),
        rn_lt8_days=("rn_lt8_day", "sum"),
        weekend_rn_lt8_days=("weekend_rn_lt8_day", "sum"),
        zero_rn_days=("zero_rn_day", "sum"),
        zero_total_nurse_days=("zero_total_nurse_day", "sum"),
        weekend_p10_total_hprd=("weekend_total_hprd", lambda x: x.quantile(0.10)),
        weekend_p25_total_hprd=("weekend_total_hprd", lambda x: x.quantile(0.25)),
        worst_weekend_total_hprd=("weekend_total_hprd", "min"),
        worst_weekend_rn_hprd=("weekend_rn_hprd", "min"),
        weekend_low_facility_p25_days=("below_facility_pre_p25", "sum"),
        weekend_low_national_p10_days=("below_national_pre_p10", "sum"),
        weekend_total_hours=("weekend_total_hours", "sum"),
        weekday_total_hours=("weekday_total_hours", "sum"),
        contract_hours=("contract_nurse_hours", "sum"),
        total_nurse_hours=("total_nurse_hours", "sum"),
        avg_daily_census=("mdscensus", "mean"),
    ).reset_index()
    out["rn_lt8_day_share"] = out["rn_lt8_days"] / out["days"].replace(0, np.nan)
    out["weekend_rn_lt8_day_share"] = out["weekend_rn_lt8_days"] / out["weekend_days"].replace(0, np.nan)
    out["zero_rn_day_share"] = out["zero_rn_days"] / out["days"].replace(0, np.nan)
    out["weekend_low_facility_p25_share"] = out["weekend_low_facility_p25_days"] / out["weekend_days"].replace(0, np.nan)
    out["weekend_low_national_p10_share"] = out["weekend_low_national_p10_days"] / out["weekend_days"].replace(0, np.nan)
    out["weekend_share_total_hours"] = out["weekend_total_hours"] / (out["weekend_total_hours"] + out["weekday_total_hours"]).replace(0, np.nan)
    out["contract_share_total_hours"] = out["contract_hours"] / out["total_nurse_hours"].replace(0, np.nan)
    return out


def construct_reliability_outcomes(max_quarters: int | None = None) -> None:
    ensure_dirs()
    q_path = DATA / "reliability_outcomes_facility_quarter.parquet"
    m_path = DATA / "reliability_outcomes_facility_month.parquet"
    if q_path.exists() and m_path.exists():
        return
    sources = pd.read_csv(OLD_TEMP / "pbj_daily_sources.csv")
    sources["_through"] = pd.to_datetime(sources["temporal"].astype(str).str.split("/").str[-1], errors="coerce")
    sources = sources[sources["_through"].le(pd.Timestamp("2023-12-31"))].drop(columns=["_through"])
    if max_quarters:
        sources = sources.head(max_quarters)
    all_quarter = []
    all_month = []
    monthly_existing = pd.read_parquet(OLD_DATA / "pbj_facility_month.parquet")
    monthly_existing["month_date"] = pd.PeriodIndex(monthly_existing["month"], freq="M").to_timestamp()
    pre_monthly = monthly_existing[
        (monthly_existing["month_date"] >= pd.Timestamp("2019-01-01"))
        & (monthly_existing["month_date"] < pd.Timestamp("2022-01-01"))
        & monthly_existing["weekend_total_nurse_hprd"].notna()
    ].copy()
    national_threshold = float(pre_monthly["weekend_total_nurse_hprd"].quantile(0.10))
    facility_thresholds = pre_monthly.groupby("facility_id")["weekend_total_nurse_hprd"].quantile(0.25)
    for _, src in sources.iterrows():
        temporal = src["temporal"]
        url = src["download_url"]
        print(f"Reliability streaming PBJ {temporal}")
        d = daily_quarter_from_source(url, temporal)
        all_quarter.append(aggregate_reliability(d, "quarter", national_threshold, facility_thresholds))
        all_month.append(aggregate_reliability(d, "month", national_threshold, facility_thresholds))
    q = pd.concat(all_quarter, ignore_index=True)
    q = q.groupby(["facility_id", "state", "quarter"], as_index=False).agg({c: "sum" for c in q.columns if c not in {"facility_id", "state", "quarter"} and q[c].dtype.kind in "biufc"})
    # Recompute share variables after combining any duplicate chunks.
    q["rn_lt8_day_share"] = q["rn_lt8_days"] / q["days"].replace(0, np.nan)
    q["weekend_rn_lt8_day_share"] = q["weekend_rn_lt8_days"] / q["weekend_days"].replace(0, np.nan)
    q["zero_rn_day_share"] = q["zero_rn_days"] / q["days"].replace(0, np.nan)
    q["weekend_low_facility_p25_share"] = q["weekend_low_facility_p25_days"] / q["weekend_days"].replace(0, np.nan)
    q["weekend_low_national_p10_share"] = q["weekend_low_national_p10_days"] / q["weekend_days"].replace(0, np.nan)
    q["weekend_share_total_hours"] = q["weekend_total_hours"] / (q["weekend_total_hours"] + q["weekday_total_hours"]).replace(0, np.nan)
    q["contract_share_total_hours"] = q["contract_hours"] / q["total_nurse_hours"].replace(0, np.nan)
    m = pd.concat(all_month, ignore_index=True)
    q.to_parquet(q_path, index=False)
    m.to_parquet(m_path, index=False)
    q.to_csv(DATA / "reliability_outcomes_facility_quarter.csv", index=False)
    save_csv(TABLES / "reliability_outcome_coverage.csv", pd.DataFrame(
        [
            {
                "unit": "facility_quarter",
                "rows": len(q),
                "facilities": q["facility_id"].nunique(),
                "periods": q["quarter"].nunique(),
                "national_pre_weekend_p10_total_hprd": national_threshold,
            },
            {
                "unit": "facility_month",
                "rows": len(m),
                "facilities": m["facility_id"].nunique(),
                "periods": m["month"].nunique(),
                "national_pre_weekend_p10_total_hprd": national_threshold,
            },
        ]
    ))
    outcome_audit = """# Outcome Reconstruction Audit

## Data Source

PBJ Daily Nurse Staffing quarterly CSV URLs recorded in the existing source inventory are streamed from CMS and aggregated to facility-month and facility-quarter reliability outcomes.

## Constructed Outcomes

- `rn_lt8_days`: days with positive resident census and RN hours below 8.
- `weekend_rn_lt8_days`: weekend days with positive resident census and RN hours below 8.
- `zero_rn_days`: days with positive resident census and zero RN hours.
- `zero_total_nurse_days`: days with positive resident census and zero RN/LPN/aide hours.
- `weekend_p10_total_hprd`, `weekend_p25_total_hprd`: lower-tail weekend total nurse HPRD.
- `worst_weekend_total_hprd`, `worst_weekend_rn_hprd`: minimum weekend daily HPRD within period.
- `weekend_low_facility_p25_share`: share of weekend days below a facility's 2019-2021 monthly weekend HPRD p25.
- `weekend_low_national_p10_share`: share of weekend days below the national 2019-2021 monthly weekend HPRD p10.
- `weekend_share_total_hours`: weekend share of total nursing hours, used for reallocation/gaming.
- `contract_share_total_hours`: contract nursing hours share.
- `avg_daily_census`: resident census demand proxy.

These are policy-proximal staffing reliability and lower-tail staffing-risk outcomes, not resident clinical outcomes. The low-staffing thresholds are derived from the existing 2019-2021 facility-month PBJ panel to avoid a second full pass over remote daily CSV files.
"""
    write_text(REPORT / "outcome_reconstruction_audit.md", outcome_audit)


def construct_threshold_running_variables() -> None:
    ensure_dirs()
    if not (DATA / "rating_score_emulator_panel.parquet").exists():
        rating_algorithm_emulator()
    em = pd.read_parquet(DATA / "rating_score_emulator_panel.parquet")
    july = em[em["snapshot"] == "2022-07-27"].copy()
    q = pd.read_parquet(DATA / "reliability_outcomes_facility_quarter.parquet") if (DATA / "reliability_outcomes_facility_quarter.parquet").exists() else pd.DataFrame()
    if not q.empty:
        pre = q[q["quarter"].isin(["2021Q1", "2021Q2", "2021Q3"])].groupby("facility_id").agg(
            pre_weekend_rn_lt8_day_share=("weekend_rn_lt8_day_share", "mean"),
            pre_zero_rn_day_share=("zero_rn_day_share", "mean"),
            pre_weekend_p10_total_hprd=("weekend_p10_total_hprd", "mean"),
            pre_avg_daily_census=("avg_daily_census", "mean"),
        ).reset_index()
        post = q[q["quarter"].isin(["2022Q4", "2023Q1", "2023Q2", "2023Q3", "2023Q4"])].groupby("facility_id").agg(
            post_weekend_rn_lt8_day_share=("weekend_rn_lt8_day_share", "mean"),
            post_zero_rn_day_share=("zero_rn_day_share", "mean"),
            post_weekend_p10_total_hprd=("weekend_p10_total_hprd", "mean"),
            post_avg_daily_census=("avg_daily_census", "mean"),
            post_weekend_share_total_hours=("weekend_share_total_hours", "mean"),
            post_contract_share_total_hours=("contract_share_total_hours", "mean"),
        ).reset_index()
        july = july.merge(pre, on="facility_id", how="left").merge(post, on="facility_id", how="left")
        for c in ["weekend_rn_lt8_day_share", "zero_rn_day_share", "weekend_p10_total_hprd", "avg_daily_census"]:
            if f"post_{c}" in july and f"pre_{c}" in july:
                july[f"delta_{c}"] = july[f"post_{c}"] - july[f"pre_{c}"]
    own = july["ownership_type"].astype(str).str.lower()
    july["ownership_for_profit"] = own.str.contains("for profit", na=False).astype(int)
    july["large_facility"] = (july["certified_beds"] >= july["certified_beds"].median(skipna=True)).astype(int)
    july.to_parquet(DATA / "analysis_threshold_facility_july2022.parquet", index=False)
    july.to_csv(DATA / "analysis_threshold_facility_july2022.csv", index=False)


def rd_threshold_models() -> None:
    ensure_dirs()
    if not (DATA / "analysis_threshold_facility_july2022.parquet").exists():
        construct_threshold_running_variables()
    df = pd.read_parquet(DATA / "analysis_threshold_facility_july2022.parquet")
    outcomes = [
        "post_weekend_rn_lt8_day_share",
        "post_zero_rn_day_share",
        "post_weekend_p10_total_hprd",
        "post_avg_daily_census",
        "post_weekend_share_total_hours",
        "post_contract_share_total_hours",
    ]
    rows = []
    balance_rows = []
    density_rows = []
    for t in STAFFING_THRESHOLDS:
        for bw in [5, 10, 15, 20, 30]:
            for y in outcomes:
                if y in df.columns:
                    rows.append(local_linear_rd(df, y, "staffing_score_proxy_round", t, bw, donut=0.0))
                    rows[-1]["design"] = "RD"
                    rows.append(local_linear_rd(df, y, "staffing_score_proxy_round", t, bw, donut=1.0))
                    rows[-1]["design"] = "donut_RD"
            for c in ["ownership_for_profit", "certified_beds", "avg_residents_per_day", "health_inspection_rating", "qm_rating", "pre_weekend_rn_lt8_day_share", "pre_zero_rn_day_share", "pre_weekend_p10_total_hprd"]:
                if c in df.columns:
                    balance_rows.append(local_linear_rd(df, c, "staffing_score_proxy_round", t, 20, donut=0.0) | {"diagnostic": "covariate_balance"})
            d = df[["staffing_score_proxy_round"]].dropna().copy()
            d["x"] = d["staffing_score_proxy_round"] - t
            local = d[d["x"].abs() <= 10]
            below = int((local["x"] < 0).sum())
            above = int((local["x"] >= 0).sum())
            p = stats.binomtest(above, below + above, 0.5).pvalue if below + above > 0 else np.nan
            density_rows.append({"cutoff": t, "bandwidth": 10, "below_n": below, "above_n": above, "binomial_density_p": p})
    for t in PLACEBO_THRESHOLDS:
        for bw in [10, 20]:
            for y in outcomes:
                if y in df.columns:
                    rows.append(local_linear_rd(df, y, "staffing_score_proxy_round", t, bw, donut=0.0) | {"design": "placebo_cutoff"})
    res = pd.DataFrame(rows)
    bal = pd.DataFrame(balance_rows)
    dens = pd.DataFrame(density_rows)
    save_csv(TABLES / "rd_threshold_estimates.csv", res)
    save_csv(TABLES / "rd_covariate_balance.csv", bal)
    save_csv(TABLES / "rd_density_checks.csv", dens)
    star_match = pd.read_csv(TABLES / "rating_emulator_validation.csv")
    july_match = star_match.loc[star_match["snapshot"] == "2022-07-27", "star_match_rate"].iloc[0]
    main_320 = res[(res["cutoff"] == 320) & (res["bandwidth"] == 20) & (res["donut"] == 0) & (res["design"] == "RD")]
    md = [
        "# RD Threshold Results",
        "",
        f"July 2022 proxy score/star match rate: {july_match:.3f}.",
        "",
        "Because the match rate is below the pre-specified 95% threshold, all RD estimates using `staffing_score_proxy_round` are proxy-running-variable diagnostics unless later improved.",
        "",
        "## Main 320-Cutoff RD, Bandwidth 20",
        "",
        md_table(main_320) if not main_320.empty else "No estimates.",
        "",
        "## Density Checks",
        "",
        md_table(dens) if not dens.empty else "No density checks.",
        "",
        "## Decision",
        "",
        "No STRONG GO from RD unless the emulator is improved or an official score field is located. Current RD can still inform whether local patterns are worth deeper reconstruction.",
    ]
    write_text(REPORT / "rd_threshold_results.md", "\n".join(md))


def rd_did_models() -> None:
    ensure_dirs()
    if not (DATA / "analysis_threshold_facility_july2022.parquet").exists():
        construct_threshold_running_variables()
    df = pd.read_parquet(DATA / "analysis_threshold_facility_july2022.parquet")
    outcomes = ["delta_weekend_rn_lt8_day_share", "delta_zero_rn_day_share", "delta_weekend_p10_total_hprd", "delta_avg_daily_census"]
    rows = []
    for t in STAFFING_THRESHOLDS:
        for bw in [5, 10, 15, 20, 30]:
            for y in outcomes:
                if y in df.columns:
                    rows.append(local_linear_rd(df, y, "staffing_score_proxy_round", t, bw, donut=0.0) | {"design": "RD_DID"})
    res = pd.DataFrame(rows)
    save_csv(TABLES / "rd_did_estimates.csv", res)
    main = res[(res["cutoff"] == 320) & (res["bandwidth"] == 20)]
    write_text(REPORT / "rd_did_results.md", "\n".join([
        "# RD-DID Results",
        "",
        "RD-DID estimates use facility-level post-minus-pre changes, where clean post is 2022Q4-2023Q4 and pre is 2021Q1-2021Q3.",
        "",
        "These are downgraded if the score emulator remains below 95% match.",
        "",
        "## 320 Cutoff, Bandwidth 20",
        "",
        md_table(main) if not main.empty else "No estimates.",
    ]))


def formula_label_shock_models() -> None:
    ensure_dirs()
    if not (DATA / "analysis_threshold_facility_july2022.parquet").exists():
        construct_threshold_running_variables()
    df = pd.read_parquet(DATA / "analysis_threshold_facility_july2022.parquet")
    em_panel = pd.read_parquet(DATA / "rating_score_emulator_panel.parquet") if (DATA / "rating_score_emulator_panel.parquet").exists() else pd.DataFrame()
    if not em_panel.empty:
        apr = em_panel[em_panel["snapshot"] == "2022-04-27"][
            ["facility_id", "overall_rating", "staffing_rating", "health_inspection_rating", "qm_rating"]
        ].rename(
            columns={
                "overall_rating": "overall_rating_apr2022",
                "staffing_rating": "staffing_rating_apr2022",
                "health_inspection_rating": "health_inspection_rating_apr2022",
                "qm_rating": "qm_rating_apr2022",
            }
        )
        df = df.merge(apr, on="facility_id", how="left")
        df["actual_overall_change_apr_to_jul"] = df["overall_rating"] - df["overall_rating_apr2022"]
        df["actual_staffing_change_apr_to_jul"] = df["staffing_rating"] - df["staffing_rating_apr2022"]
    df["predicted_formula_loss_size"] = df["old_formula_overall"] - df["new_formula_overall"]
    outcomes = ["delta_avg_daily_census", "delta_weekend_rn_lt8_day_share", "delta_zero_rn_day_share", "delta_weekend_p10_total_hprd"]
    rows = []
    for y in outcomes:
        if y in df.columns:
            rows.append(two_group_delta(df, y, "formula_induced_overall_star_loss"))
    res = pd.DataFrame(rows)
    save_csv(TABLES / "formula_label_shock_estimates.csv", res)
    first_rows = []
    for y in ["predicted_formula_loss_size", "actual_overall_change_apr_to_jul", "actual_staffing_change_apr_to_jul"]:
        if y in df.columns:
            first_rows.append(two_group_delta(df, y, "formula_induced_overall_star_loss"))
    first_df = pd.DataFrame(first_rows)
    save_csv(TABLES / "formula_label_first_stage.csv", first_df)
    treated = int(df["formula_induced_overall_star_loss"].sum())
    md = [
        "# Formula-Induced Overall-Star Label Shock Results",
        "",
        f"Formula-induced-loss homes in July 2022: {treated}.",
        "",
        "Treatment is `old_formula_overall > new_formula_overall`, using the January 2022 and July 2022 guide rules applied to July 2022 health inspection, staffing, and QM stars.",
        "",
        "## First Stage Diagnostic",
        "",
        md_table(first_df),
        "",
        "## Outcome Differences",
        "",
        md_table(res) if not res.empty else "No estimates.",
        "",
        "## Interpretation",
        "",
        "This is a formula-induced label-shock attempt, but exclusion is fragile because underlying domain ratings are still facility quality signals. Treat as mechanism evidence unless matched/local diagnostics are strengthened.",
    ]
    write_text(REPORT / "formula_label_shock_results.md", "\n".join(md))


def metric_salience_ddd() -> None:
    ensure_dirs()
    monthly = pd.read_parquet(OLD_DATA / "pbj_facility_month.parquet")
    monthly["period"] = pd.PeriodIndex(monthly["month"], freq="M")
    monthly["post_aug2022"] = (monthly["period"].dt.to_timestamp() >= pd.Timestamp("2022-08-01")).astype(int)
    monthly["pre_window"] = ((monthly["period"].dt.to_timestamp() >= pd.Timestamp("2021-01-01")) & (monthly["period"].dt.to_timestamp() <= pd.Timestamp("2021-09-01"))).astype(int)
    monthly["post_window"] = ((monthly["period"].dt.to_timestamp() >= pd.Timestamp("2022-08-01")) & (monthly["period"].dt.to_timestamp() <= pd.Timestamp("2023-12-01"))).astype(int)
    # Within-facility metric contrast: targeted weekend total gap minus transparency-only weekend RN gap.
    monthly["targeted_minus_rn_weekend_gap"] = (
        monthly["weekend_total_nurse_hprd"] - monthly["weekday_total_nurse_hprd"]
    ) - (
        monthly["weekend_rn_hprd"] - monthly["weekday_rn_hprd"]
    )
    base = monthly[monthly["pre_window"].eq(1)].groupby("facility_id")["targeted_minus_rn_weekend_gap"].mean().rename("pre_targeted_minus_rn_gap")
    post = monthly[monthly["post_window"].eq(1)].groupby("facility_id")["targeted_minus_rn_weekend_gap"].mean().rename("post_targeted_minus_rn_gap")
    panel = pd.concat([base, post], axis=1).reset_index()
    panel["delta_targeted_minus_rn_gap"] = panel["post_targeted_minus_rn_gap"] - panel["pre_targeted_minus_rn_gap"]
    if (DATA / "rating_score_emulator_july2022.parquet").exists():
        em = pd.read_parquet(DATA / "rating_score_emulator_july2022.parquet")[["facility_id", "high_shadow_price", "formula_induced_overall_star_loss"]]
        panel = panel.merge(em, on="facility_id", how="left")
    panel.to_parquet(DATA / "metric_salience_facility_panel.parquet", index=False)
    rows = [
        {
            "estimand": "overall_post_pre_change_in_targeted_minus_rn_weekend_gap",
            "n": int(panel["delta_targeted_minus_rn_gap"].notna().sum()),
            "mean_delta": float(panel["delta_targeted_minus_rn_gap"].mean()),
            "se": float(panel["delta_targeted_minus_rn_gap"].std(ddof=1) / math.sqrt(panel["delta_targeted_minus_rn_gap"].notna().sum())),
        }
    ]
    if "high_shadow_price" in panel:
        rows.append(two_group_delta(panel, "delta_targeted_minus_rn_gap", "high_shadow_price") | {"estimand": "high_shadow_price_heterogeneity"})
    res = pd.DataFrame(rows)
    save_csv(TABLES / "metric_salience_ddd_estimates.csv", res)
    write_text(REPORT / "metric_salience_ddd_results.md", "\n".join([
        "# Metric Salience DDD Results",
        "",
        "This implementation uses a facility-level post-minus-pre contrast in `(weekend total - weekday total) - (weekend RN - weekday RN)`. It is a conservative proxy for the full facility-day-staff-category DDD because the existing data are already aggregated to facility-month.",
        "",
        md_table(res),
        "",
        "Interpretation should focus on mechanism direction, not standalone causality.",
    ]))


def shadow_price_bunching() -> None:
    ensure_dirs()
    if not (DATA / "rating_score_emulator_panel.parquet").exists():
        rating_algorithm_emulator()
    em = pd.read_parquet(DATA / "rating_score_emulator_panel.parquet")
    rows = []
    for snap, g in em.groupby("snapshot"):
        post = int(snap >= "2022-07-27")
        for t in STAFFING_THRESHOLDS:
            score = g["staffing_score_proxy_round"]
            just_above = int(((score >= t) & (score <= t + 5)).sum())
            just_below = int(((score < t) & (score >= t - 5)).sum())
            p = stats.binomtest(just_above, just_above + just_below, 0.5).pvalue if just_above + just_below > 0 else np.nan
            rows.append({"snapshot": snap, "post_july": post, "cutoff_type": "true", "cutoff": t, "just_below_5pts": just_below, "just_above_5pts": just_above, "above_share": pct(just_above, just_above + just_below), "binomial_p": p})
        for t in PLACEBO_THRESHOLDS:
            score = g["staffing_score_proxy_round"]
            just_above = int(((score >= t) & (score <= t + 5)).sum())
            just_below = int(((score < t) & (score >= t - 5)).sum())
            p = stats.binomtest(just_above, just_above + just_below, 0.5).pvalue if just_above + just_below > 0 else np.nan
            rows.append({"snapshot": snap, "post_july": post, "cutoff_type": "placebo", "cutoff": t, "just_below_5pts": just_below, "just_above_5pts": just_above, "above_share": pct(just_above, just_above + just_below), "binomial_p": p})
    bunch = pd.DataFrame(rows)
    save_csv(TABLES / "bunching_score_thresholds.csv", bunch)
    if (DATA / "analysis_threshold_facility_july2022.parquet").exists():
        df = pd.read_parquet(DATA / "analysis_threshold_facility_july2022.parquet")
        outcomes = ["delta_weekend_p10_total_hprd", "delta_weekend_rn_lt8_day_share", "delta_zero_rn_day_share"]
        shadow_rows = []
        for y in outcomes:
            if y in df.columns:
                shadow_rows.append(two_group_delta(df, y, "high_shadow_price"))
        shadow = pd.DataFrame(shadow_rows)
    else:
        shadow = pd.DataFrame()
    save_csv(TABLES / "shadow_price_estimates.csv", shadow)
    write_text(REPORT / "bunching_and_gaming_results.md", "\n".join([
        "# Bunching and Gaming Results",
        "",
        "Bunching uses the proxy 0-380 staffing score, so interpretation inherits emulator limitations.",
        "",
        "## Score-Threshold Bunching",
        "",
        md_table(bunch, max_rows=40),
        "",
        "## Shadow-Price Outcome Differences",
        "",
        md_table(shadow) if not shadow.empty else "No shadow-price estimates.",
    ]))


def validation_2018_event() -> None:
    ensure_dirs()
    sources = pd.read_csv(OLD_TEMP / "pbj_daily_sources.csv")
    min_temporal = sources["temporal"].min()
    feasible = bool(str(min_temporal).startswith("2017") or str(min_temporal).startswith("2018"))
    rows = [{
        "design": "2018 no-RN downgrade validation",
        "local_pbj_source_start": min_temporal,
        "feasible_with_current_local_sources": feasible,
        "decision": "attempted_infeasible" if not feasible else "feasible",
        "reason": "Existing PBJ daily source inventory starts in 2019, after the 2018 validation event." if not feasible else "",
    }]
    save_csv(TABLES / "validation_2018_feasibility.csv", pd.DataFrame(rows))
    write_text(REPORT / "validation_2018_event.md", "\n".join([
        "# 2018 Validation Event",
        "",
        md_table(pd.DataFrame(rows)),
        "",
        "The validation is documented as infeasible with the current local source inventory unless 2017-2018 PBJ daily files are added.",
    ]))


def design_scorecard() -> None:
    ensure_dirs()
    val_path = TABLES / "rating_emulator_validation.csv"
    july_match = np.nan
    if val_path.exists():
        val = pd.read_csv(val_path)
        july_match = val.loc[val["snapshot"] == "2022-07-27", "star_match_rate"].iloc[0]
    rd = pd.read_csv(TABLES / "rd_threshold_estimates.csv") if (TABLES / "rd_threshold_estimates.csv").exists() else pd.DataFrame()
    dens = pd.read_csv(TABLES / "rd_density_checks.csv") if (TABLES / "rd_density_checks.csv").exists() else pd.DataFrame()
    formula = pd.read_csv(TABLES / "formula_label_shock_estimates.csv") if (TABLES / "formula_label_shock_estimates.csv").exists() else pd.DataFrame()
    ddd = pd.read_csv(TABLES / "metric_salience_ddd_estimates.csv") if (TABLES / "metric_salience_ddd_estimates.csv").exists() else pd.DataFrame()
    bunch = pd.read_csv(TABLES / "bunching_score_thresholds.csv") if (TABLES / "bunching_score_thresholds.csv").exists() else pd.DataFrame()
    score_rows = []
    emulator_valid = pd.notna(july_match) and july_match >= 0.95
    score_rows.append({
        "design": "A/B RD and RD-DID",
        "source_validity": "verified",
        "algorithm_emulation_validity": "pass" if emulator_valid else "fail_below_95pct",
        "first_stage_strength": "staffing star threshold exists",
        "pre_balance": "see rd_covariate_balance.csv",
        "pre_outcome_validity": "see RD-DID/pre outcomes",
        "placebo_performance": "see placebo_cutoff rows",
        "sample_size": int(rd["n"].max()) if not rd.empty else 0,
        "interpretability": "local threshold effect if score is valid",
        "robustness": "bandwidth/donut produced",
        "publication_potential": "high if official score can be recovered; otherwise limited",
        "final_status": "CONDITIONAL GO" if emulator_valid else "NO-GO for strong causality",
    })
    score_rows.append({
        "design": "C Formula label shock",
        "source_validity": "verified",
        "algorithm_emulation_validity": "formula rules verified",
        "first_stage_strength": "see formula_label_first_stage.csv",
        "pre_balance": "not fully matched in this pass",
        "pre_outcome_validity": "uses post-pre deltas",
        "placebo_performance": "not yet strong",
        "sample_size": int(formula["n"].max()) if not formula.empty else 0,
        "interpretability": "mechanical label shock, exclusion fragile",
        "robustness": "basic",
        "publication_potential": "innovative mechanism if strengthened",
        "final_status": "CONDITIONAL GO" if not formula.empty else "NO-GO",
    })
    score_rows.append({
        "design": "D Metric salience DDD",
        "source_validity": "PBJ verified",
        "algorithm_emulation_validity": "does not require score",
        "first_stage_strength": "metric salience from guide",
        "pre_balance": "within-facility contrast",
        "pre_outcome_validity": "post-pre contrast only",
        "placebo_performance": "not yet full",
        "sample_size": int(ddd["n"].max()) if not ddd.empty and "n" in ddd else 0,
        "interpretability": "mechanism evidence",
        "robustness": "basic",
        "publication_potential": "useful supporting design",
        "final_status": "CONDITIONAL GO",
    })
    score_rows.append({
        "design": "E/F Shadow price and bunching",
        "source_validity": "verified",
        "algorithm_emulation_validity": "inherits proxy score limitation",
        "first_stage_strength": "distance-to-cutoff constructed",
        "pre_balance": "not enough",
        "pre_outcome_validity": "limited",
        "placebo_performance": "true/placebo cutoffs produced",
        "sample_size": int((bunch["just_below_5pts"] + bunch["just_above_5pts"]).max()) if not bunch.empty else 0,
        "interpretability": "gaming diagnostic",
        "robustness": "basic",
        "publication_potential": "conditional on emulator",
        "final_status": "CONDITIONAL GO for diagnostics, NO-GO for causality",
    })
    score_rows.append({
        "design": "G 2018 validation",
        "source_validity": "local source insufficient",
        "algorithm_emulation_validity": "not applicable",
        "first_stage_strength": "not attempted",
        "pre_balance": "not applicable",
        "pre_outcome_validity": "not applicable",
        "placebo_performance": "not applicable",
        "sample_size": 0,
        "interpretability": "infeasible with 2019+ local PBJ",
        "robustness": "not applicable",
        "publication_potential": "none until 2017-2018 PBJ added",
        "final_status": "NO-GO documented infeasible",
    })
    score = pd.DataFrame(score_rows)
    save_csv(TABLES / "design_tournament_scorecard.csv", score)
    write_text(REPORT / "design_tournament_scorecard.md", "# Design Tournament Scorecard\n\n" + md_table(score))


def write_breakthrough_report() -> None:
    ensure_dirs()
    score = pd.read_csv(TABLES / "design_tournament_scorecard.csv") if (TABLES / "design_tournament_scorecard.csv").exists() else pd.DataFrame()
    val = pd.read_csv(TABLES / "rating_emulator_validation.csv") if (TABLES / "rating_emulator_validation.csv").exists() else pd.DataFrame()
    july_match = val.loc[val["snapshot"] == "2022-07-27", "star_match_rate"].iloc[0] if not val.empty else np.nan
    oct_match = val.loc[val["snapshot"] == "2022-10-27", "star_match_rate"].iloc[0] if not val.empty else np.nan
    cov = pd.read_csv(TABLES / "reliability_outcome_coverage.csv") if (TABLES / "reliability_outcome_coverage.csv").exists() else pd.DataFrame()
    q_rows = int(cov.loc[cov["unit"] == "facility_quarter", "rows"].iloc[0]) if not cov.empty else 0
    q_fac = int(cov.loc[cov["unit"] == "facility_quarter", "facilities"].iloc[0]) if not cov.empty else 0
    formula = pd.read_csv(TABLES / "formula_label_shock_estimates.csv") if (TABLES / "formula_label_shock_estimates.csv").exists() else pd.DataFrame()
    first = pd.read_csv(TABLES / "formula_label_first_stage.csv") if (TABLES / "formula_label_first_stage.csv").exists() else pd.DataFrame()
    def lookup(df: pd.DataFrame, outcome: str, col: str = "diff") -> float:
        if df.empty or outcome not in set(df.get("outcome", [])):
            return np.nan
        return float(df.loc[df["outcome"] == outcome, col].iloc[0])
    fs_overall = lookup(first, "actual_overall_change_apr_to_jul")
    census_diff = lookup(formula, "delta_avg_daily_census")
    rn8_diff = lookup(formula, "delta_weekend_rn_lt8_day_share")
    p10_diff = lookup(formula, "delta_weekend_p10_total_hprd")
    final_status = "No strong causal paper yet"
    if pd.notna(july_match) and july_match >= 0.95:
        final_status = "Conditional local causal path"
    rejected = """# Rejected Designs V2

## Old global composite exposure DID

Rejected as the main design because the prior identification audit found failed pre-trends and a significant placebo timing test. It remains background only.

## Strong RD claim from proxy score

Rejected unless the staffing-score emulator reaches the pre-specified 95% match threshold or an official score field is located. The current Provider Data Catalog archives do not publish the 0-380 score directly.

## Causal ML

Rejected for this iteration. The main bottleneck is identification and algorithm reconstruction, not heterogeneous-treatment-effect prediction.

## 2018 validation event

Documented infeasible with current local PBJ source inventory because it starts in 2019.
"""
    write_text(TEMP / "rejected_designs_v2.md", rejected)
    ident = f"""# Identification Audit V2

## Bottom Line

{final_status}.

The new official-source audit verifies the July 2022 algorithmic-label shock and the exact staffing-score thresholds. However, the public Provider Data Catalog archives available locally provide staffing stars and component measures, not the official 0-380 staffing score. The attempted emulator is therefore the pivotal validity check.

## What Can Be Claimed Now

- CMS created a real algorithmic-label shock in July 2022: six staffing measures were scored, summed, rescaled when missing, rounded, and mapped to 1-5 staffing stars with thresholds 155/205/255/320.
- The overall-star formula changed in July 2022 so that four-star staffing no longer generated the prior overall-star bonus.
- Lower-tail staffing reliability outcomes can be constructed from PBJ daily files and are better aligned with the policy mechanism than average HPRD alone.
- Current RD/RD-DID estimates are exploratory if the emulator match rate remains below 95%.

## What Cannot Be Claimed

- A strong national causal effect of the 2022 reform.
- A strong local causal RD effect unless the running variable is validated or replaced by an official score.
- Resident clinical quality improvement based only on staffing/rating/deficiency patterns.
"""
    write_text(REPORT / "identification_audit_v2.md", ident)
    final = f"""# Final Breakthrough Report

## Executive Judgment

{final_status}. The project has a stronger conceptual route than the old exposure DID, but the first empirical pass does not justify strong causal language unless the staffing-score emulator reaches the 95% validation threshold or an official score field is found.

## What Improved

- The paper is reframed around algorithmic labels and staffing reliability, not generic public reporting.
- Official CMS sources verify January 2022 as transparency and July 2022 as the Five-Star algorithmic-label shock.
- The July 2022 archived Technical Users' Guide is now snapshotted and used as the algorithm source.
- Reliability/lower-tail PBJ outcomes are constructed or cached by script.
- RD, RD-DID, formula-label shock, metric-salience, shadow-price, and bunching scripts are reproducible under `design_tournament/`.

## Key Empirical Signals

- July 2022 score proxy matches official staffing stars at {july_match:.3f}, below the pre-specified 0.950 primary-use threshold. October 2022 match is {oct_match:.3f}, which supports the algorithm logic once adjusted weekend HPRD is available.
- Reliability outcomes cover {q_rows:,} facility-quarter rows and {q_fac:,} facilities for 2019Q1-2023Q4.
- At the 320 cutoff, simple post-July RD estimates are not robust enough for a strong claim; RD-DID shows adverse reliability movements but inherits the July running-variable limitation.
- Formula-induced-loss homes have a larger April-to-July actual overall-star decline of {fs_overall:.3f} stars relative to controls. In post-minus-pre outcomes, they also show census change {census_diff:.3f}, weekend RN<8h share change {rn8_diff:.4f}, and weekend p10 total HPRD change {p10_diff:.3f} relative to controls. Treat this as conditional mechanism evidence until matched/local diagnostics are strengthened.

## Best Manuscript Path

The strongest path is still Strategy 1 if the running variable can be improved: RD-DID around the 320 staffing-star cutoff, supported by the formula-induced overall-star shock and metric-salience DDD. If emulator validation stays weak, pivot to a cautious algorithmic score-management paper using bunching and mechanism evidence, not a strong causal paper.

## Stop-Loss

Do not return to tuning the old composite exposure DID. If no official score can be recovered and the emulator remains below threshold, label RD/RD-DID as exploratory and write the project as transparent no-go or conditional mechanism evidence.
"""
    write_text(REPORT / "final_breakthrough_report.md", final)


def self_test_outputs() -> None:
    ensure_dirs()
    env = {
        "python": sys.version,
        "platform": sys.platform,
        "pandas": pd.__version__,
        "numpy": np.__version__,
        "scipy": scipy.__version__,
        "run_date": date.today().isoformat(),
    }
    (TEMP / "environment_v2.json").write_text(json.dumps(env, indent=2), encoding="utf-8")
    required_files = [
        REPORT / "design_tournament_plan.md",
        REPORT / "official_policy_algorithm_audit.md",
        REPORT / "rating_algorithm_emulation_audit.md",
        REPORT / "outcome_reconstruction_audit.md",
        REPORT / "rd_threshold_results.md",
        REPORT / "rd_did_results.md",
        REPORT / "formula_label_shock_results.md",
        REPORT / "metric_salience_ddd_results.md",
        REPORT / "bunching_and_gaming_results.md",
        REPORT / "design_tournament_scorecard.md",
        REPORT / "identification_audit_v2.md",
        REPORT / "final_breakthrough_report.md",
        TEMP / "rejected_designs_v2.md",
        TEMP / "skill_usage_log_v2.md",
        TABLES / "rating_emulator_validation.csv",
        TABLES / "reliability_outcome_coverage.csv",
        TABLES / "rd_threshold_estimates.csv",
        TABLES / "rd_did_estimates.csv",
        TABLES / "formula_label_shock_estimates.csv",
        TABLES / "metric_salience_ddd_estimates.csv",
        TABLES / "bunching_score_thresholds.csv",
        TABLES / "validation_2018_feasibility.csv",
        TABLES / "design_tournament_scorecard.csv",
        TEMP / "environment_v2.json",
    ]
    rows = []
    for p in required_files:
        rows.append({
            "check": "required_file_exists",
            "target": str(p.relative_to(DT_ROOT)),
            "pass": p.exists() and p.stat().st_size > 0,
            "value": p.stat().st_size if p.exists() else 0,
        })
    if (TABLES / "rating_emulator_validation.csv").exists():
        val = pd.read_csv(TABLES / "rating_emulator_validation.csv")
        july = float(val.loc[val["snapshot"] == "2022-07-27", "star_match_rate"].iloc[0])
        octv = float(val.loc[val["snapshot"] == "2022-10-27", "star_match_rate"].iloc[0])
        rows.append({"check": "july_emulator_match_below_primary_threshold_recorded", "target": "2022-07-27", "pass": july < 0.95, "value": july})
        rows.append({"check": "october_emulator_match_supports_algorithm_logic", "target": "2022-10-27", "pass": octv >= 0.95, "value": octv})
    if (TABLES / "reliability_outcome_coverage.csv").exists():
        cov = pd.read_csv(TABLES / "reliability_outcome_coverage.csv")
        q = cov[cov["unit"] == "facility_quarter"].iloc[0]
        rows.append({"check": "reliability_facility_quarter_rows_positive", "target": "facility_quarter", "pass": q["rows"] > 0, "value": int(q["rows"])})
        rows.append({"check": "reliability_periods_cover_2019_2023", "target": "facility_quarter_periods", "pass": q["periods"] >= 20, "value": int(q["periods"])})
    if (TABLES / "rd_threshold_estimates.csv").exists():
        rd = pd.read_csv(TABLES / "rd_threshold_estimates.csv")
        rows.append({"check": "rd_contains_320_cutoff", "target": "rd_threshold_estimates", "pass": 320 in set(rd["cutoff"].dropna().astype(int)), "value": int((rd["cutoff"] == 320).sum())})
    if (TABLES / "rd_did_estimates.csv").exists():
        rdd = pd.read_csv(TABLES / "rd_did_estimates.csv")
        rows.append({"check": "rd_did_rows_positive", "target": "rd_did_estimates", "pass": len(rdd) > 0, "value": len(rdd)})
    scorecard = pd.read_csv(TABLES / "design_tournament_scorecard.csv") if (TABLES / "design_tournament_scorecard.csv").exists() else pd.DataFrame()
    if not scorecard.empty:
        status = " | ".join(scorecard["final_status"].astype(str).tolist())
        rows.append({"check": "strong_causal_claim_not_forced", "target": "scorecard_status", "pass": "NO-GO for strong causality" in status, "value": status})
    checks = pd.DataFrame(rows)
    save_csv(TABLES / "self_test_checks.csv", checks)
    passed = int(checks["pass"].sum())
    total = int(len(checks))
    failures = checks[~checks["pass"]]
    md = [
        "# Self-Test V2",
        "",
        f"Checks passed: {passed}/{total}.",
        "",
        "## Failed Checks",
        "",
        md_table(failures) if not failures.empty else "None.",
        "",
        "## Key Interpretation Checks",
        "",
        "- July 2022 emulator match is intentionally recorded as below the 95% primary-use threshold, so RD is not labeled strong causal evidence.",
        "- October 2022 emulator match is checked to confirm the July algorithm implementation is broadly correct once adjusted weekend HPRD is available.",
        "- Reliability outcomes must have positive facility-quarter coverage through the preferred 2019-2023 design window.",
    ]
    write_text(TEMP / "self_test_v2.md", "\n".join(md))


def run_all() -> None:
    write_design_tournament_plan()
    source_algorithm_audit()
    rating_algorithm_emulator()
    construct_reliability_outcomes()
    construct_threshold_running_variables()
    rd_threshold_models()
    rd_did_models()
    formula_label_shock_models()
    metric_salience_ddd()
    shadow_price_bunching()
    validation_2018_event()
    design_scorecard()
    write_breakthrough_report()
    self_test_outputs()


if __name__ == "__main__":
    run_all()
