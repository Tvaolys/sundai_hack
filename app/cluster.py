"""Duplicate-report clustering (pure).

Implements the design.md duplicate rule:

    Same ``category``, within ``dist_m`` metres of the cluster seed, opened
    within ``days`` days after the seed (window ``[seed, seed + days]``).
    Seed order: by ``open_date`` then ``case_id`` (deterministic). Greedy
    single pass: each still-unassigned case becomes a seed and absorbs every
    *later* unassigned case of the same category within the distance and the
    time window.

Cases are dicts with keys: ``case_id``, ``category``, ``open_date``
(tz-aware ``datetime``), ``latitude``, ``longitude``, ``on_time``. Rows whose
``latitude``/``longitude`` is ``None`` (or ``open_date`` is ``None``) are
unmapped and skipped entirely (they are not clustered).

Scaling: cases are first bucketed by category. Within a category we keep a
two-pointer time window (cases are time-sorted) so only cases whose
``open_date`` is within ``days`` of the seed are even considered, and a coarse
spatial grid index so the distance check only looks at nearby cells rather than
the whole bucket. This keeps the single pass close to linear for the realistic
case of many small clusters, comfortably handling ~30k cases per neighborhood.
"""

from __future__ import annotations

from collections import defaultdict
from datetime import timedelta
from typing import Any, Iterable

from app.geo import haversine_m

# Grid cell size in degrees. Must be large enough that any pair within the
# distance threshold lands in the same or an adjacent cell. ~0.001 deg latitude
# is ~111 m, which safely exceeds the 50 m default threshold; neighbouring
# cells are always scanned so the exact threshold is still enforced by
# haversine, this only bounds the candidate set.
_CELL_DEG = 0.001


def _is_mapped(case: dict[str, Any]) -> bool:
    return (
        case.get("latitude") is not None
        and case.get("longitude") is not None
        and case.get("open_date") is not None
    )


def cluster(cases: Iterable[dict[str, Any]], dist_m: float, days: float) -> list[dict[str, Any]]:
    """Group cases into duplicate clusters per the design.md greedy rule.

    Returns a list of cluster dicts, sorted by ``size`` descending then ``id``
    ascending. Every mapped case belongs to exactly one cluster (singletons
    included). Unmapped cases (missing coords or open_date) are skipped.
    """
    mapped = [c for c in cases if _is_mapped(c)]

    # Bucket by category; clustering never crosses categories.
    by_category: dict[Any, list[dict[str, Any]]] = defaultdict(list)
    for c in mapped:
        by_category[c["category"]].append(c)

    window = timedelta(days=days)
    clusters: list[dict[str, Any]] = []

    for category, bucket in by_category.items():
        # Deterministic seed order: (open_date, case_id).
        bucket.sort(key=lambda c: (c["open_date"], c["case_id"]))
        n = len(bucket)
        assigned = [False] * n

        # Spatial grid index: cell -> list of indices into `bucket`.
        grid: dict[tuple[int, int], list[int]] = defaultdict(list)
        for i, c in enumerate(bucket):
            grid[_cell(c)].append(i)

        for i in range(n):
            if assigned[i]:
                continue
            seed = bucket[i]
            assigned[i] = True
            members = [seed]

            seed_lat = seed["latitude"]
            seed_lon = seed["longitude"]
            seed_open = seed["open_date"]
            window_end = seed_open + window

            # Candidate indices come from the seed cell and its 8 neighbours.
            scell = _cell(seed)
            for cell in _neighbor_cells(scell):
                for j in grid.get(cell, ()):  # noqa: B905
                    if j <= i or assigned[j]:
                        continue
                    cand = bucket[j]
                    # Time window: later cases only, within [seed, seed+days].
                    # Bucket is time-sorted, so once a candidate is past the
                    # window end it and everything later in that cell is too;
                    # but cells interleave, so just test each candidate.
                    if cand["open_date"] > window_end:
                        continue
                    if haversine_m(seed_lat, seed_lon, cand["latitude"], cand["longitude"]) <= dist_m:
                        assigned[j] = True
                        members.append(cand)

            clusters.append(_summarize(category, seed, members))

    clusters.sort(key=lambda cl: (-cl["size"], cl["id"]))
    return clusters


def _cell(case: dict[str, Any]) -> tuple[int, int]:
    return (
        int(case["latitude"] // _CELL_DEG),
        int(case["longitude"] // _CELL_DEG),
    )


def _neighbor_cells(cell: tuple[int, int]) -> list[tuple[int, int]]:
    cx, cy = cell
    return [(cx + dx, cy + dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]


def _summarize(category: Any, seed: dict[str, Any], members: list[dict[str, Any]]) -> dict[str, Any]:
    case_ids = [m["case_id"] for m in members]
    size = len(members)
    late = sum(1 for m in members if m.get("on_time") is False)
    lat = sum(m["latitude"] for m in members) / size
    lon = sum(m["longitude"] for m in members) / size
    opens = [m["open_date"] for m in members]
    return {
        "id": seed["case_id"],
        "category": category,
        "seed": seed["case_id"],
        "case_ids": case_ids,
        "size": size,
        "late": late,
        "lat": lat,
        "lon": lon,
        "first": min(opens),
        "last": max(opens),
    }
