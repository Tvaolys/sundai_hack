"""EJ2020 block-group loader and report → block-group assignment.

The cache file (``data/ej2020_boston.json``) is produced by
``scripts/fetch_ej2020_boston.py`` and has the shape::

    {"source": ..., "fetched_at": ..., "block_groups": [
        {"geoid", "pct_minority", "lim_eng_pct", "income", "population",
         "limited_english": bool, "ej_criteria", "rings": [[[lon,lat],...]]},
        ...
    ]}

The layer holds ONLY EJ block groups, so a point outside every polygon is a
non-EJ area and gets ``geoid = None``.
"""

from __future__ import annotations

import json
import math
from typing import Any, Iterable

from app.geo import in_bbox, point_in_polygon, ring_bbox

# Income sentinel used by the Census / MassGIS tables for "no data".
_INCOME_SENTINEL = -666666666


def _norm_pct(value: Any) -> float | None:
    """Normalize a limited-English household percentage to a 0-100 scale.

    Values that look like a 0-1 fraction (<= 1) are scaled by 100. ``None`` and
    non-numeric values pass through as ``None``.
    """
    if value is None:
        return None
    try:
        v = float(value)
    except (TypeError, ValueError):
        return None
    if math.isnan(v):
        return None
    if 0.0 <= v <= 1.0:
        v *= 100.0
    return v


def _norm_income(value: Any) -> float | None:
    """Census income: sentinel or negative -> None."""
    if value is None:
        return None
    try:
        v = float(value)
    except (TypeError, ValueError):
        return None
    if math.isnan(v):
        return None
    if v < 0 or v == _INCOME_SENTINEL:
        return None
    return v


def load_block_groups(path: str) -> list[dict[str, Any]]:
    """Load and normalize block groups, precomputing a bbox per BG.

    Returns a list of dicts with keys: geoid, pct_minority, lim_eng_pct
    (0-100), income (None if sentinel/negative), population, limited_english
    (bool), ej_criteria, rings, bbox.
    """
    with open(path, encoding="utf-8") as fh:
        raw = json.load(fh)
    bgs_in = raw.get("block_groups", raw if isinstance(raw, list) else [])

    out: list[dict[str, Any]] = []
    for bg in bgs_in:
        rings = bg.get("rings") or []
        if not rings:
            continue
        out.append(
            {
                "geoid": bg.get("geoid"),
                "pct_minority": bg.get("pct_minority"),
                "lim_eng_pct": _norm_pct(bg.get("lim_eng_pct")),
                "income": _norm_income(bg.get("income")),
                "population": bg.get("population"),
                "limited_english": bool(bg.get("limited_english")),
                "ej_criteria": bg.get("ej_criteria"),
                "rings": rings,
                "bbox": ring_bbox(rings),
            }
        )
    return out


class _GridIndex:
    """Coarse uniform grid over block-group bounding boxes.

    Each cell lists the block groups whose bbox overlaps it, so assignment only
    tests the handful of candidates near a point instead of all ~600 polygons.
    """

    def __init__(self, bgs: list[dict[str, Any]], cells: int = 64) -> None:
        self.bgs = bgs
        self.cells = max(1, cells)
        self.grid: dict[tuple[int, int], list[int]] = {}
        if not bgs:
            self.minlon = self.minlat = 0.0
            self.lon_span = self.lat_span = 1.0
            return
        minlon = minlat = math.inf
        maxlon = maxlat = -math.inf
        for bg in bgs:
            lo0, la0, lo1, la1 = bg["bbox"]
            minlon = min(minlon, lo0)
            minlat = min(minlat, la0)
            maxlon = max(maxlon, lo1)
            maxlat = max(maxlat, la1)
        self.minlon, self.minlat = minlon, minlat
        self.lon_span = (maxlon - minlon) or 1e-9
        self.lat_span = (maxlat - minlat) or 1e-9
        for idx, bg in enumerate(bgs):
            lo0, la0, lo1, la1 = bg["bbox"]
            cx0, cy0 = self._cell(lo0, la0)
            cx1, cy1 = self._cell(lo1, la1)
            for cx in range(cx0, cx1 + 1):
                for cy in range(cy0, cy1 + 1):
                    self.grid.setdefault((cx, cy), []).append(idx)

    def _cell(self, lon: float, lat: float) -> tuple[int, int]:
        fx = (lon - self.minlon) / self.lon_span
        fy = (lat - self.minlat) / self.lat_span
        cx = min(self.cells - 1, max(0, int(fx * self.cells)))
        cy = min(self.cells - 1, max(0, int(fy * self.cells)))
        return cx, cy

    def candidates(self, lon: float, lat: float) -> list[int]:
        return self.grid.get(self._cell(lon, lat), [])


def assign(cases: Iterable[dict[str, Any]], bgs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Set ``case['geoid']`` for each case via bbox prefilter + point-in-polygon.

    A case with no/invalid coordinates, or outside every block group, gets
    ``geoid = None``. Mutates the case dicts in place and also returns the list.
    Uses a coarse grid index so ~150k points stay fast.
    """
    cases = list(cases)
    index = _GridIndex(bgs)
    for case in cases:
        lon = case.get("longitude")
        lat = case.get("latitude")
        case["geoid"] = None
        if lon is None or lat is None:
            continue
        for idx in index.candidates(lon, lat):
            bg = bgs[idx]
            if not in_bbox(lon, lat, bg["bbox"]):
                continue
            if point_in_polygon(lon, lat, bg["rings"]):
                case["geoid"] = bg["geoid"]
                break
    return cases
