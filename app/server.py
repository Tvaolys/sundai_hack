"""n1-311triage API routes.

Wires the pure analysis modules (cases, sla, cluster, equity, overlay) behind a
small FastAPI surface. All data is loaded once, lazily, into a cached
``AppState`` the first time any ``/api`` route is hit (so tests can point the
loaders at fixtures by setting the env vars before the first request). Paths are
overridable via ``N1_SLICE`` / ``N1_EJ`` / ``N1_PARAMS`` (defaults under
``data/``).

Per-neighborhood clustering is expensive on the real slice, so it is computed
lazily and cached per neighborhood; a ``case_id -> neighborhood`` index lets
``/api/cluster/{id}`` find the right neighborhood without rescanning everything.
"""
from __future__ import annotations

import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query
from fastapi.staticfiles import StaticFiles

from app.cases import load_cases, load_meta
from app.cluster import cluster
from app.equity import assign, load_block_groups
from app.overlay import baseline, compare
from app.sla import chronic, group_stats, load_params

@asynccontextmanager
async def _lifespan(app: FastAPI):
    """Warm the data cache at startup so the first demo click isn't slow.

    Building ``AppState`` reads the slice/EJ/params files (~3 s on the real
    slice); doing it here means the first ``/api`` request is already warm. Env
    vars are read at this point, so tests that set ``N1_SLICE`` / ``N1_EJ`` /
    ``N1_PARAMS`` and call ``reset_state()`` before entering the TestClient
    context still load their fixtures. A load failure is swallowed so the app
    still starts and the first request can surface the real error.
    """
    try:
        get_state()
    except Exception:  # noqa: BLE001 - don't block startup on a data error.
        pass
    yield


app = FastAPI(title="n1-311triage", lifespan=_lifespan)

_REPO = Path(__file__).resolve().parent.parent
_DEFAULT_SLICE = _REPO / "data" / "311_slice.json.gz"
_DEFAULT_EJ = _REPO / "data" / "ej2020_boston.json"
_DEFAULT_PARAMS = _REPO / "data" / "params.json"

# Source text shown on every screen (requirement 4).
_SOURCE_311 = (
    "City of Boston 311 service requests (data.boston.gov), merged from the "
    "new BOS311 system and the legacy 2026 system."
)
_SOURCE_EJ = (
    "MassGIS EJ2020 block groups: "
    "https://arcgisserver.digital.mass.gov/arcgisserver/rest/services/AGOL/EJ2020/MapServer/0"
)

# Neighborhood that is kept in city totals but never selectable (design.md).
UNKNOWN = "UNKNOWN"


class AppState:
    """Loaded-once data + lazily-cached per-neighborhood clusters."""

    def __init__(self, slice_path: str, ej_path: str, params_path: str) -> None:
        self.params = load_params(params_path)
        self.meta = load_meta(slice_path)
        self.cases = load_cases(slice_path)
        self.bgs = load_block_groups(ej_path)
        assign(self.cases, self.bgs)
        self.base = baseline(self.cases)

        self.dist_m = self.params.get("cluster_distance_m", 50)
        self.days = self.params.get("cluster_window_days", 14)
        self.min_n = self.params.get("min_n", 50)

        # Index cases by neighborhood (UNKNOWN kept) and by case_id.
        self.by_neighborhood: dict[str, list[dict]] = {}
        self.case_neighborhood: dict[str, str] = {}
        for case in self.cases:
            nb = case.get("neighborhood") or UNKNOWN
            self.by_neighborhood.setdefault(nb, []).append(case)
            cid = case.get("case_id")
            if cid is not None:
                self.case_neighborhood[cid] = nb

        # Selectable neighborhoods: everything except UNKNOWN.
        self._cluster_cache: dict[str, list[dict]] = {}

        # Data window: first / last open_date over all cases (requirement 4).
        opens = [c["open_date"] for c in self.cases if c.get("open_date") is not None]
        self.first_open = min(opens) if opens else None
        self.last_open = max(opens) if opens else None

    def neighborhoods(self) -> list[str]:
        return sorted(n for n in self.by_neighborhood if n != UNKNOWN)

    def cases_for(self, name: str) -> list[dict] | None:
        """Cases for a selectable neighborhood, or None if not selectable."""
        if name == UNKNOWN or name not in self.by_neighborhood:
            return None
        return self.by_neighborhood[name]

    def clusters_for(self, name: str) -> list[dict]:
        """Clusters for a neighborhood (cached). Caller validates the name."""
        cached = self._cluster_cache.get(name)
        if cached is None:
            cached = cluster(self.by_neighborhood.get(name, []), self.dist_m, self.days)
            self._cluster_cache[name] = cached
        return cached


_STATE: AppState | None = None


def _paths() -> tuple[str, str, str]:
    return (
        os.environ.get("N1_SLICE", str(_DEFAULT_SLICE)),
        os.environ.get("N1_EJ", str(_DEFAULT_EJ)),
        os.environ.get("N1_PARAMS", str(_DEFAULT_PARAMS)),
    )


def get_state() -> AppState:
    """Return the cached state, building it from the current env vars once."""
    global _STATE
    if _STATE is None:
        slice_path, ej_path, params_path = _paths()
        _STATE = AppState(slice_path, ej_path, params_path)
    return _STATE


def reset_state() -> None:
    """Drop the cached state so the next request reloads (tests use this)."""
    global _STATE
    _STATE = None


def _iso(dt) -> str | None:
    return dt.isoformat() if dt is not None else None


@app.get("/api/health")
def health() -> dict:
    return {"ok": True}


@app.get("/api/meta")
def meta() -> dict:
    state = get_state()
    meta = state.meta
    counts = meta.get("counts", {})
    return {
        "window": {
            "first_open_date": _iso(state.first_open),
            "last_open_date": _iso(state.last_open),
            "slice_start": meta.get("window", {}).get("start"),
            "tz": meta.get("window", {}).get("tz"),
        },
        "source": {
            "311": _SOURCE_311,
            "ej2020": _SOURCE_EJ,
        },
        "counts": {
            "new": counts.get("new", 0),
            "legacy": counts.get("legacy", 0),
            "total": counts.get("total", len(state.cases)),
        },
        "excluded_by_source": meta.get("excluded_by_source", {}),
        "params": {
            "cluster_distance_m": state.dist_m,
            "cluster_window_days": state.days,
            "min_n": state.min_n,
            "lim_eng_pct_threshold": state.params.get("lim_eng_pct_threshold"),
            "exclude_sources": state.params.get("exclude_sources", []),
            "placeholder": bool(state.params.get("placeholder", False)),
        },
    }


@app.get("/api/neighborhoods")
def neighborhoods() -> list[dict]:
    state = get_state()
    return [
        {"name": name, "total": len(state.by_neighborhood[name])}
        for name in state.neighborhoods()
    ]


@app.get("/api/neighborhood")
def neighborhood(name: str = Query(...)) -> dict:
    state = get_state()
    cases = state.cases_for(name)
    if cases is None:
        raise HTTPException(status_code=404, detail=f"Unknown neighborhood: {name}")
    return {
        "name": name,
        "stats": group_stats(cases),
        "chronic": chronic(cases, state.min_n),
        "equity": compare(cases, state.bgs, state.min_n, state.base),
    }


def _cluster_summary(cl: dict) -> dict:
    return {
        "id": cl["id"],
        "category": cl["category"],
        "size": cl["size"],
        "late": cl["late"],
        "lat": cl["lat"],
        "lon": cl["lon"],
        "first": _iso(cl["first"]),
        "last": _iso(cl["last"]),
    }


@app.get("/api/clusters")
def clusters(name: str = Query(...)) -> list[dict]:
    state = get_state()
    if state.cases_for(name) is None:
        raise HTTPException(status_code=404, detail=f"Unknown neighborhood: {name}")
    # Already sorted largest-first by app.cluster.cluster; keep size >= 2.
    return [_cluster_summary(cl) for cl in state.clusters_for(name) if cl["size"] >= 2]


@app.get("/api/cluster/{cluster_id}")
def cluster_detail(cluster_id: str) -> dict:
    state = get_state()
    name = state.case_neighborhood.get(cluster_id)
    if name is None or name == UNKNOWN:
        raise HTTPException(status_code=404, detail=f"Unknown cluster: {cluster_id}")

    for cl in state.clusters_for(name):
        if cl["id"] == cluster_id:
            by_id = {c.get("case_id"): c for c in state.by_neighborhood[name]}
            rows = []
            for cid in cl["case_ids"]:
                c = by_id.get(cid)
                if c is None:
                    continue
                rows.append(
                    {
                        "case_id": c.get("case_id"),
                        "open_date": _iso(c.get("open_date")),
                        "case_status": c.get("case_status"),
                        "on_time": c.get("on_time"),
                        "address": c.get("address"),
                        "system": c.get("system"),
                    }
                )
            return {
                "id": cl["id"],
                "category": cl["category"],
                "size": cl["size"],
                "rows": rows,
            }

    raise HTTPException(status_code=404, detail=f"Not a cluster seed: {cluster_id}")


def _percentile(sorted_values: list[float], p: float) -> float:
    """Linear-interpolated percentile of a pre-sorted, non-empty list.

    ``p`` is a fraction in [0, 1]. Used to clip default-geocode outliers (e.g.
    City Hall) out of the /api/map bounding box.
    """
    if len(sorted_values) == 1:
        return sorted_values[0]
    k = (len(sorted_values) - 1) * p
    lo = int(k)
    hi = min(lo + 1, len(sorted_values) - 1)
    if lo == hi:
        return sorted_values[lo]
    return sorted_values[lo] * (hi - k) + sorted_values[hi] * (k - lo)


def _robust_bbox(mapped: list[dict]) -> dict:
    """2nd..98th percentile bbox of mapped case lat/lon, padded ~10%.

    Percentile clipping keeps a few default-geocode outliers (e.g. 27 Roslindale
    cases pinned to City Hall at 42.35982,-71.05899) from blowing up the box so
    the map stays centered on the real neighborhood.
    """
    lats = sorted(c["latitude"] for c in mapped)
    lons = sorted(c["longitude"] for c in mapped)
    min_lat = _percentile(lats, 0.02)
    max_lat = _percentile(lats, 0.98)
    min_lon = _percentile(lons, 0.02)
    max_lon = _percentile(lons, 0.98)
    # ~10% padding on each side (guard against a zero-span box).
    lat_pad = (max_lat - min_lat) * 0.1 or 1e-4
    lon_pad = (max_lon - min_lon) * 0.1 or 1e-4
    return {
        "min_lon": min_lon - lon_pad,
        "min_lat": min_lat - lat_pad,
        "max_lon": max_lon + lon_pad,
        "max_lat": max_lat + lat_pad,
    }


def _in_bbox(bbox: dict, lat: float, lon: float) -> bool:
    return (
        bbox["min_lat"] <= lat <= bbox["max_lat"]
        and bbox["min_lon"] <= lon <= bbox["max_lon"]
    )


@app.get("/api/map")
def map_view(name: str = Query(...)) -> dict:
    state = get_state()
    cases = state.cases_for(name)
    if cases is None:
        raise HTTPException(status_code=404, detail=f"Unknown neighborhood: {name}")

    # Robust bounding box (2nd..98th percentile + ~10% pad) of mapped cases, so
    # default-geocode outliers don't blow the box up and squeeze the map.
    mapped = [c for c in cases if c.get("latitude") is not None and c.get("longitude") is not None]
    if mapped:
        bbox = _robust_bbox(mapped)
    else:
        bbox = {"min_lon": None, "min_lat": None, "max_lon": None, "max_lat": None}

    # Block groups whose bbox intersects the (robust) neighborhood case bbox.
    block_groups = []
    if mapped:
        for bg in state.bgs:
            lo0, la0, lo1, la1 = bg["bbox"]
            if (
                lo1 >= bbox["min_lon"]
                and lo0 <= bbox["max_lon"]
                and la1 >= bbox["min_lat"]
                and la0 <= bbox["max_lat"]
            ):
                block_groups.append(
                    {
                        "geoid": bg["geoid"],
                        "limited_english": bg["limited_english"],
                        "rings": bg["rings"],
                    }
                )

    # Markers: clusters size >= 2, largest first, inside the bbox, capped at 400.
    markers = []
    for cl in state.clusters_for(name):
        if cl["size"] < 2:
            continue
        if not _in_bbox(bbox, cl["lat"], cl["lon"]):
            continue
        markers.append(
            {
                "id": cl["id"],
                "lat": cl["lat"],
                "lon": cl["lon"],
                "size": cl["size"],
                "late": cl["late"],
                "has_late": cl["late"] > 0,
            }
        )
        if len(markers) >= 400:
            break

    return {"bbox": bbox, "block_groups": block_groups, "markers": markers}


# Registered last so /api/* routes take precedence. app/static is created in T9;
# skip the mount when it does not exist yet so startup never crashes.
STATIC_DIR = Path(__file__).parent / "static"
if STATIC_DIR.is_dir():
    app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")
