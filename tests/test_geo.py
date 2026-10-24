"""Tests for app.geo: haversine, bbox, ring_bbox, point_in_polygon."""

import math

from hypothesis import given
from hypothesis import strategies as st

from app.geo import haversine_m, in_bbox, point_in_polygon, ring_bbox

# A known axis-aligned square (lon in [0,10], lat in [0,10]) as a single ring.
SQUARE = [[[0.0, 0.0], [10.0, 0.0], [10.0, 10.0], [0.0, 10.0], [0.0, 0.0]]]

# Same square with a hole in its center (lon/lat in [4,6]).
SQUARE_WITH_HOLE = [
    [[0.0, 0.0], [10.0, 0.0], [10.0, 10.0], [0.0, 10.0], [0.0, 0.0]],
    [[4.0, 4.0], [6.0, 4.0], [6.0, 6.0], [4.0, 6.0], [4.0, 4.0]],
]

_coords = st.floats(min_value=-89.0, max_value=89.0, allow_nan=False, allow_infinity=False)
_lons = st.floats(min_value=-179.0, max_value=179.0, allow_nan=False, allow_infinity=False)


# --- haversine properties ---------------------------------------------------

@given(_coords, _lons, _coords, _lons)
def test_haversine_non_negative_and_symmetric(lat1, lon1, lat2, lon2):
    d1 = haversine_m(lat1, lon1, lat2, lon2)
    d2 = haversine_m(lat2, lon2, lat1, lon1)
    assert d1 >= 0.0
    assert math.isclose(d1, d2, rel_tol=1e-9, abs_tol=1e-6)


@given(_coords, _lons)
def test_haversine_point_to_self_is_zero(lat, lon):
    assert haversine_m(lat, lon, lat, lon) == 0.0


def test_haversine_known_distance():
    # ~1 degree of latitude near the equator is roughly 111 km.
    d = haversine_m(0.0, 0.0, 1.0, 0.0)
    assert 110_000 < d < 112_000


# --- in_bbox ----------------------------------------------------------------

def test_in_bbox_inclusive_and_outside():
    bbox = (-71.2, 42.2, -70.9, 42.4)  # roughly Boston
    assert in_bbox(-71.05, 42.35, bbox)
    assert in_bbox(-71.2, 42.2, bbox)  # corner inclusive
    assert not in_bbox(-70.0, 42.35, bbox)
    assert not in_bbox(-71.05, 41.0, bbox)


# --- ring_bbox --------------------------------------------------------------

def test_ring_bbox_of_square():
    assert ring_bbox(SQUARE) == (0.0, 0.0, 10.0, 10.0)


def test_ring_bbox_with_hole_uses_all_vertices():
    # Hole is interior, so outer ring still defines the extent.
    assert ring_bbox(SQUARE_WITH_HOLE) == (0.0, 0.0, 10.0, 10.0)


# --- point_in_polygon -------------------------------------------------------

@given(
    st.floats(min_value=0.5, max_value=9.5, allow_nan=False),
    st.floats(min_value=0.5, max_value=9.5, allow_nan=False),
)
def test_points_inside_square_classified_in(lon, lat):
    # Avoid the hole region [4,6]x[4,6] so the plain square stays fully inside.
    if 4.0 <= lon <= 6.0 and 4.0 <= lat <= 6.0:
        return
    assert point_in_polygon(lon, lat, SQUARE) is True


@given(
    st.floats(min_value=-50.0, max_value=50.0, allow_nan=False),
    st.floats(min_value=-50.0, max_value=50.0, allow_nan=False),
)
def test_points_outside_square_classified_out(lon, lat):
    # Only consider points strictly outside the [0,10] square.
    if 0.0 < lon < 10.0 and 0.0 < lat < 10.0:
        return
    if lon < 0.0 or lon > 10.0 or lat < 0.0 or lat > 10.0:
        assert point_in_polygon(lon, lat, SQUARE) is False


def test_point_inside_hole_is_outside():
    # Center of the hole: inside outer ring but inside the hole -> outside.
    assert point_in_polygon(5.0, 5.0, SQUARE_WITH_HOLE) is False
    # A point in the solid part (between outer edge and hole) is inside.
    assert point_in_polygon(1.0, 5.0, SQUARE_WITH_HOLE) is True


@given(
    st.floats(min_value=4.2, max_value=5.8, allow_nan=False),
    st.floats(min_value=4.2, max_value=5.8, allow_nan=False),
)
def test_random_points_inside_hole_are_outside(lon, lat):
    assert point_in_polygon(lon, lat, SQUARE_WITH_HOLE) is False
