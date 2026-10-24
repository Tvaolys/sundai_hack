"""Tests for app.cluster: greedy duplicate clustering.

Covers the design.md duplicate rule and the requirements.md properties:
partition of mapped cases, single category per cluster, every member within
the distance and time window of its seed, deterministic/order-independent
output, and a small performance bound.
"""

import random
import time
from datetime import datetime, timedelta, timezone

from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from app.cluster import cluster
from app.geo import haversine_m

TZ = timezone.utc
BASE = datetime(2026, 1, 1, tzinfo=TZ)

DIST_M = 50.0
DAYS = 14.0

# A metre is ~1/111320 of a degree of latitude near Boston; used to build
# cases a known distance apart.
_DEG_PER_M = 1.0 / 111_320.0


def _case(case_id, category, day, lat, lon, on_time=True):
    return {
        "case_id": case_id,
        "category": category,
        "open_date": BASE + timedelta(days=day),
        "latitude": lat,
        "longitude": lon,
        "on_time": on_time,
    }


# --- basic behaviour --------------------------------------------------------

def test_two_nearby_same_category_cluster_together():
    cases = [
        _case("A", "Pothole", 0, 42.35, -71.06),
        _case("B", "Pothole", 1, 42.35 + 10 * _DEG_PER_M, -71.06),  # ~10 m away
    ]
    result = cluster(cases, DIST_M, DAYS)
    assert len(result) == 1
    cl = result[0]
    assert cl["size"] == 2
    assert set(cl["case_ids"]) == {"A", "B"}
    assert cl["id"] == "A"  # seed is the earlier case
    assert cl["seed"] == "A"
    assert cl["category"] == "Pothole"


def test_clusters_across_cell_boundary_when_dist_m_large():
    """Regression: with dist_m=150 two cases ~120 m apart must cluster.

    The old fixed 0.001-deg grid cell (~82 m of longitude at Boston) meant the
    3x3 neighbourhood spanned less than 150 m, so distant-but-within-threshold
    neighbours were silently missed. Cell size is now derived from dist_m.
    """
    import math

    cos_lat = math.cos(math.radians(42.3))
    dlon_120m = 120.0 / (111_320.0 * cos_lat)
    cases = [
        _case("A", "Pothole", 0, 42.3, -71.06),
        _case("B", "Pothole", 1, 42.3, -71.06 + dlon_120m),  # ~120 m east
    ]
    result = cluster(cases, 150.0, DAYS)
    assert len(result) == 1
    assert result[0]["size"] == 2
    assert set(result[0]["case_ids"]) == {"A", "B"}


def test_cluster_case_ids_sorted_chronologically():
    # Members added out of chronological order must come back sorted by
    # (open_date, case_id).
    cases = [
        _case("A", "Pothole", 0, 42.35, -71.06),
        _case("C", "Pothole", 2, 42.35 + 5 * _DEG_PER_M, -71.06),
        _case("B", "Pothole", 1, 42.35 + 8 * _DEG_PER_M, -71.06),
    ]
    [cl] = cluster(cases, DIST_M, DAYS)
    assert cl["case_ids"] == ["A", "B", "C"]


def test_different_category_never_clusters():
    cases = [
        _case("A", "Pothole", 0, 42.35, -71.06),
        _case("B", "Graffiti", 0, 42.35, -71.06),  # same spot, different category
    ]
    result = cluster(cases, DIST_M, DAYS)
    assert len(result) == 2
    assert all(cl["size"] == 1 for cl in result)


def test_too_far_apart_stays_separate():
    cases = [
        _case("A", "Pothole", 0, 42.35, -71.06),
        _case("B", "Pothole", 0, 42.35 + 500 * _DEG_PER_M, -71.06),  # ~500 m away
    ]
    result = cluster(cases, DIST_M, DAYS)
    assert len(result) == 2


def test_outside_time_window_stays_separate():
    cases = [
        _case("A", "Pothole", 0, 42.35, -71.06),
        _case("B", "Pothole", 20, 42.35, -71.06),  # same spot, 20 days later
    ]
    result = cluster(cases, DIST_M, DAYS)
    assert len(result) == 2


def test_unmapped_rows_skipped():
    cases = [
        _case("A", "Pothole", 0, 42.35, -71.06),
        {"case_id": "B", "category": "Pothole", "open_date": BASE,
         "latitude": None, "longitude": -71.06, "on_time": True},
        {"case_id": "C", "category": "Pothole", "open_date": BASE,
         "latitude": 42.35, "longitude": None, "on_time": True},
        {"case_id": "D", "category": "Pothole", "open_date": None,
         "latitude": 42.35, "longitude": -71.06, "on_time": True},
    ]
    result = cluster(cases, DIST_M, DAYS)
    assert len(result) == 1
    assert result[0]["case_ids"] == ["A"]


def test_late_count_and_centroid():
    cases = [
        _case("A", "Pothole", 0, 42.0, -71.0, on_time=False),
        _case("B", "Pothole", 1, 42.0 + 10 * _DEG_PER_M, -71.0, on_time=True),
    ]
    [cl] = cluster(cases, DIST_M, DAYS)
    assert cl["late"] == 1
    assert cl["lat"] == (42.0 + 42.0 + 10 * _DEG_PER_M) / 2
    assert cl["first"] == BASE
    assert cl["last"] == BASE + timedelta(days=1)


def test_sorted_by_size_then_id():
    cases = [
        # cluster of 1, id "Z"
        _case("Z", "Graffiti", 0, 43.0, -72.0),
        # cluster of 2, id "A"
        _case("A", "Pothole", 0, 42.0, -71.0),
        _case("A2", "Pothole", 0, 42.0 + 5 * _DEG_PER_M, -71.0),
    ]
    result = cluster(cases, DIST_M, DAYS)
    assert [cl["id"] for cl in result] == ["A", "Z"]


# --- property-based tests ---------------------------------------------------

_cat = st.sampled_from(["Pothole", "Graffiti", "Illegal Dumping", "Sign Repair"])
_lat = st.floats(min_value=42.2, max_value=42.4, allow_nan=False)
_lon = st.floats(min_value=-71.2, max_value=-70.9, allow_nan=False)
_day = st.floats(min_value=0.0, max_value=40.0, allow_nan=False)


@st.composite
def _cases(draw, max_n=30):
    n = draw(st.integers(min_value=0, max_value=max_n))
    out = []
    for i in range(n):
        out.append(_case(f"C{i:04d}", draw(_cat), draw(_day), draw(_lat), draw(_lon),
                          on_time=draw(st.booleans())))
    return out


@settings(max_examples=150, suppress_health_check=[HealthCheck.too_slow])
@given(_cases())
def test_partition_of_mapped_cases(cases):
    result = cluster(cases, DIST_M, DAYS)
    mapped_ids = [c["case_id"] for c in cases]  # all generated cases are mapped
    seen = [cid for cl in result for cid in cl["case_ids"]]
    # Every mapped case appears exactly once across all clusters.
    assert sorted(seen) == sorted(mapped_ids)
    assert len(seen) == len(set(seen))
    # Sizes sum to the number of mapped cases.
    assert sum(cl["size"] for cl in result) == len(mapped_ids)


@settings(max_examples=150, suppress_health_check=[HealthCheck.too_slow])
@given(_cases())
def test_single_category_per_cluster(cases):
    by_id = {c["case_id"]: c for c in cases}
    result = cluster(cases, DIST_M, DAYS)
    for cl in result:
        cats = {by_id[cid]["category"] for cid in cl["case_ids"]}
        assert cats == {cl["category"]}


@settings(max_examples=150, suppress_health_check=[HealthCheck.too_slow])
@given(_cases())
def test_every_member_within_dist_and_window_of_seed(cases):
    by_id = {c["case_id"]: c for c in cases}
    result = cluster(cases, DIST_M, DAYS)
    for cl in result:
        seed = by_id[cl["seed"]]
        for cid in cl["case_ids"]:
            m = by_id[cid]
            d = haversine_m(seed["latitude"], seed["longitude"],
                            m["latitude"], m["longitude"])
            assert d <= DIST_M + 1e-6
            assert seed["open_date"] <= m["open_date"] <= seed["open_date"] + timedelta(days=DAYS)


@settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
@given(_cases(), st.randoms(use_true_random=False))
def test_order_independent(cases, rng):
    expected = cluster(cases, DIST_M, DAYS)
    shuffled = list(cases)
    rng.shuffle(shuffled)
    got = cluster(shuffled, DIST_M, DAYS)
    # Compare on a canonical, order-insensitive representation.
    def canon(cls):
        return [(cl["id"], cl["size"], tuple(sorted(cl["case_ids"]))) for cl in cls]
    assert canon(expected) == canon(got)


# --- performance ------------------------------------------------------------

def test_perf_20k_cases_under_5s():
    rng = random.Random(1234)
    cats = ["Pothole", "Graffiti", "Illegal Dumping", "Sign Repair", "Snow Plowing"]
    cases = []
    for i in range(20_000):
        cases.append(_case(
            f"C{i:06d}",
            rng.choice(cats),
            rng.uniform(0.0, 40.0),
            rng.uniform(42.2, 42.4),
            rng.uniform(-71.2, -70.9),
            on_time=rng.random() > 0.3,
        ))
    start = time.perf_counter()
    result = cluster(cases, DIST_M, DAYS)
    elapsed = time.perf_counter() - start
    # Every case must be accounted for.
    assert sum(cl["size"] for cl in result) == 20_000
    assert elapsed < 5.0, f"clustering 20k took {elapsed:.2f}s"
