"""Pure geo helpers: haversine distance, bbox checks, point-in-polygon.

Coordinate convention throughout: points are (lon, lat). Rings follow the
ArcGIS JSON / GeoJSON polygon shape: a list of rings, each ring a list of
``[lon, lat]`` pairs. The first ring is the outer boundary and later rings are
holes. Even-odd ray casting across *all* rings handles holes automatically,
and also tolerates multipolygon-style input where several outer rings are
mixed together.
"""

from __future__ import annotations

import math
from typing import Sequence

# Mean Earth radius in metres (same value used by most haversine references).
_EARTH_RADIUS_M = 6_371_000.0

Bbox = tuple[float, float, float, float]  # (minlon, minlat, maxlon, maxlat)


def haversine_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Great-circle distance between two lat/lon points, in metres.

    Always non-negative and symmetric; distance from a point to itself is 0.
    """
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    a = (
        math.sin(dphi / 2.0) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2.0) ** 2
    )
    # Clamp to guard against tiny floating-point overshoot past 1.0.
    a = min(1.0, max(0.0, a))
    c = 2.0 * math.asin(math.sqrt(a))
    return _EARTH_RADIUS_M * c


def in_bbox(lon: float, lat: float, bbox: Bbox) -> bool:
    """True if (lon, lat) is within bbox = (minlon, minlat, maxlon, maxlat).

    Boundaries are inclusive.
    """
    minlon, minlat, maxlon, maxlat = bbox
    return minlon <= lon <= maxlon and minlat <= lat <= maxlat


def ring_bbox(rings: Sequence[Sequence[Sequence[float]]]) -> Bbox:
    """Bounding box (minlon, minlat, maxlon, maxlat) over all vertices of all rings.

    Raises ValueError if there are no vertices.
    """
    minlon = minlat = math.inf
    maxlon = maxlat = -math.inf
    for ring in rings:
        for lon, lat in ring:
            if lon < minlon:
                minlon = lon
            if lon > maxlon:
                maxlon = lon
            if lat < minlat:
                minlat = lat
            if lat > maxlat:
                maxlat = lat
    if minlon is math.inf or minlon > maxlon:
        raise ValueError("ring_bbox: no vertices")
    return (minlon, minlat, maxlon, maxlat)


def point_in_polygon(
    lon: float, lat: float, rings: Sequence[Sequence[Sequence[float]]]
) -> bool:
    """Even-odd ray-casting point-in-polygon test across all rings.

    ``rings`` is a list of rings (ArcGIS/GeoJSON polygon). The outer ring and
    any hole rings are all crossed by the same horizontal ray; because the test
    is even-odd, a point inside a hole flips parity an even number of times and
    is correctly reported as *outside*. Mixed outer rings (multipolygon-style)
    are handled by the same parity logic.
    """
    inside = False
    for ring in rings:
        n = len(ring)
        if n < 3:
            continue
        j = n - 1
        for i in range(n):
            xi, yi = ring[i][0], ring[i][1]
            xj, yj = ring[j][0], ring[j][1]
            # Does the horizontal ray at y=lat cross edge (j -> i)?
            if (yi > lat) != (yj > lat):
                x_cross = (xj - xi) * (lat - yi) / (yj - yi) + xi
                if lon < x_cross:
                    inside = not inside
            j = i
    return inside
