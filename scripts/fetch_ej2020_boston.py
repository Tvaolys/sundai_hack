#!/usr/bin/env python3
"""Fetch the EJ2020 block groups for Boston from the MassGIS ArcGIS service.

Writes ``data/ej2020_boston.json`` with a small header plus one record per
block group. The layer contains ONLY environmental-justice block groups, so
every Boston row has EJ='Yes'; a 311 report that falls outside every polygon
is simply a non-EJ area.

Network lives here only — never in the loader or the tests. Run manually:

    .venv/bin/python scripts/fetch_ej2020_boston.py
"""

from __future__ import annotations

import datetime as _dt
import json
import os
import sys
from typing import Any
from urllib.parse import urlencode
from urllib.request import urlopen

SERVICE = (
    "https://arcgisserver.digital.mass.gov/arcgisserver/rest/services/"
    "AGOL/EJ2020/MapServer/0/query"
)

OUT_FIELDS = [
    "GEOID",
    "MUNICIPALITY",
    "TOTAL_POP",
    "PCT_MINORITY",
    "LIMENGHHPCT",
    "BG_MHHI",
    "LIMITEDENGLISH",
    "EJ_CRITERIA",
    "EJ_CRIT_DESC",
]

PAGE = 2000  # service maxRecordCount
COORD_DP = 5

# Repo root is the parent of scripts/.
_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
OUT_PATH = os.path.join(_ROOT, "data", "ej2020_boston.json")


def _fetch_page(offset: int, max_allowable_offset: float | None) -> dict[str, Any]:
    params = {
        "where": "MUNICIPALITY='Boston'",
        "outFields": ",".join(OUT_FIELDS),
        "returnGeometry": "true",
        "outSR": "4326",
        "f": "json",
        "resultOffset": str(offset),
        "resultRecordCount": str(PAGE),
    }
    if max_allowable_offset is not None:
        params["maxAllowableOffset"] = str(max_allowable_offset)
    url = SERVICE + "?" + urlencode(params)
    with urlopen(url, timeout=120) as resp:  # noqa: S310 (fixed https host)
        return json.loads(resp.read().decode("utf-8"))


def _round_rings(rings: list[list[list[float]]]) -> list[list[list[float]]]:
    out = []
    for ring in rings:
        out.append([[round(x, COORD_DP), round(y, COORD_DP)] for x, y in ring])
    return out


def _feature_to_record(feat: dict[str, Any]) -> dict[str, Any]:
    attrs = feat.get("attributes", {})
    geom = feat.get("geometry", {}) or {}
    rings = _round_rings(geom.get("rings", []))
    limited = attrs.get("LIMITEDENGLISH")
    return {
        "geoid": attrs.get("GEOID"),
        "pct_minority": attrs.get("PCT_MINORITY"),
        "lim_eng_pct": attrs.get("LIMENGHHPCT"),
        "income": attrs.get("BG_MHHI"),
        "population": attrs.get("TOTAL_POP"),
        "limited_english": (limited == "E"),
        "ej_criteria": attrs.get("EJ_CRITERIA"),
        "rings": rings,
    }


def fetch_all(max_allowable_offset: float | None = None) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    offset = 0
    while True:
        payload = _fetch_page(offset, max_allowable_offset)
        if "error" in payload:
            raise RuntimeError(f"ArcGIS error: {payload['error']}")
        feats = payload.get("features", [])
        for feat in feats:
            records.append(_feature_to_record(feat))
        if payload.get("exceededTransferLimit") and feats:
            offset += len(feats)
            continue
        break
    return records


def main() -> int:
    # First try at full resolution; if the file is too big, regenerate
    # generalized geometry.
    records = fetch_all()
    header = {
        "source": SERVICE,
        "fetched_at": _dt.datetime.now(_dt.timezone.utc).isoformat(),
        "block_groups": records,
    }
    text = json.dumps(header)
    if len(text.encode("utf-8")) > 5 * 1024 * 1024:
        print("cache > 5 MB, re-fetching with maxAllowableOffset to generalize")
        records = fetch_all(max_allowable_offset=0.00005)
        header["block_groups"] = records
        header["fetched_at"] = _dt.datetime.now(_dt.timezone.utc).isoformat()
        text = json.dumps(header)

    with open(OUT_PATH, "w", encoding="utf-8") as fh:
        fh.write(text)

    size = len(text.encode("utf-8"))
    limited = sum(1 for r in records if r["limited_english"])
    print(f"wrote {OUT_PATH}")
    print(f"block groups: {len(records)} ({limited} limited-English)")
    print(f"file size: {size} bytes ({size / 1024 / 1024:.2f} MB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
