"""Offline TestClient tests for the n1-311triage API (task T8).

All routes run against the committed fixtures via the N1_SLICE / N1_EJ /
N1_PARAMS env vars. State is loaded lazily and cached, so each test resets the
cache; the ``client`` fixture points the loaders at the fixtures first.
"""
from __future__ import annotations

import os

import pytest
from fastapi.testclient import TestClient

from app import server

_FIXTURES = os.path.join(os.path.dirname(__file__), "fixtures")
_SLICE = os.path.join(_FIXTURES, "311_slice_sample.json.gz")
_EJ = os.path.join(_FIXTURES, "ej_api_sample.json")
_PARAMS = os.path.join(_FIXTURES, "params_sample.json")


@pytest.fixture()
def client(monkeypatch):
    monkeypatch.setenv("N1_SLICE", _SLICE)
    monkeypatch.setenv("N1_EJ", _EJ)
    monkeypatch.setenv("N1_PARAMS", _PARAMS)
    server.reset_state()
    with TestClient(server.app) as c:
        yield c
    server.reset_state()


# --- app wiring -----------------------------------------------------------

def test_title_renamed():
    assert server.app.title == "n1-311triage"


def test_health_still_present(client):
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.json() == {"ok": True}


# --- /api/meta ------------------------------------------------------------

def test_meta_shape(client):
    r = client.get("/api/meta")
    assert r.status_code == 200
    body = r.json()
    assert body["window"]["first_open_date"] is not None
    assert body["window"]["last_open_date"] is not None
    assert body["window"]["first_open_date"] <= body["window"]["last_open_date"]
    # Source text names both 311 systems + the EJ2020 source URL.
    assert "311" in body["source"]["311"]
    assert "arcgisserver" in body["source"]["ej2020"]
    # Row counts per system.
    assert body["counts"]["new"] == 24
    assert body["counts"]["legacy"] == 20
    assert body["counts"]["total"] == 44
    # excluded_by_source from the slim step (resident filter).
    assert body["excluded_by_source"]["Employee Generated"] == 2
    assert body["excluded_by_source"]["City Worker App"] == 2
    # Params in use incl. placeholder flag.
    assert body["params"]["min_n"] == 2
    assert body["params"]["placeholder"] is True


# --- /api/neighborhoods ---------------------------------------------------

def test_neighborhoods_sorted_excludes_unknown(client):
    r = client.get("/api/neighborhoods")
    assert r.status_code == 200
    body = r.json()
    names = [n["name"] for n in body]
    assert names == sorted(names)
    assert "UNKNOWN" not in names
    # totals are positive ints
    assert all(isinstance(n["total"], int) and n["total"] > 0 for n in body)
    ab = next(n for n in body if n["name"] == "Allston / Brighton")
    assert ab["total"] == 6


# --- /api/neighborhood ----------------------------------------------------

def test_neighborhood_stats_chronic_equity(client):
    r = client.get("/api/neighborhood", params={"name": "Allston / Brighton"})
    assert r.status_code == 200
    body = r.json()
    assert body["name"] == "Allston / Brighton"
    stats = body["stats"]
    assert stats["total"] == 6
    assert stats["late"] <= stats["known"] <= stats["total"]
    assert "ranked" in body["chronic"] and "too_few" in body["chronic"]
    equity = body["equity"]
    # Fixture EJ polygon splits Allston into LE and other -> comparable.
    assert equity["comparable"] is True
    assert equity["adjusted"] is True
    assert equity["limited_english"]["known"] >= 2
    assert equity["other"]["known"] >= 2
    assert "pattern in the city's own data" in equity["caveat"]


def test_neighborhood_unknown_404(client):
    r = client.get("/api/neighborhood", params={"name": "UNKNOWN"})
    assert r.status_code == 404
    assert "detail" in r.json()


def test_neighborhood_nonexistent_404(client):
    r = client.get("/api/neighborhood", params={"name": "Narnia"})
    assert r.status_code == 404
    assert "detail" in r.json()


# --- /api/clusters --------------------------------------------------------

def test_clusters_size_ge_2_largest_first(client):
    r = client.get("/api/clusters", params={"name": "Allston / Brighton"})
    assert r.status_code == 200
    body = r.json()
    assert all(c["size"] >= 2 for c in body)
    sizes = [c["size"] for c in body]
    assert sizes == sorted(sizes, reverse=True)
    # The Pothole pair clusters into one size-2 cluster seeded by BCS-00250001.
    assert body[0]["id"] == "BCS-00250001"
    assert body[0]["category"] == "Pothole"
    assert body[0]["size"] == 2
    assert "first" in body[0] and "last" in body[0]


def test_clusters_unknown_404(client):
    r = client.get("/api/clusters", params={"name": "UNKNOWN"})
    assert r.status_code == 404
    assert "detail" in r.json()


# --- /api/cluster/{id} ----------------------------------------------------

def test_cluster_detail_rows(client):
    r = client.get("/api/cluster/BCS-00250001")
    assert r.status_code == 200
    body = r.json()
    assert body["id"] == "BCS-00250001"
    assert body["category"] == "Pothole"
    assert body["size"] == 2
    assert len(body["rows"]) == 2
    row = body["rows"][0]
    for key in ("case_id", "open_date", "case_status", "on_time", "address", "system"):
        assert key in row


def test_cluster_detail_not_a_seed_404(client):
    # BCS-00250002 is a cluster MEMBER (absorbed into BCS-00250001), not a seed.
    r = client.get("/api/cluster/BCS-00250002")
    assert r.status_code == 404
    assert "detail" in r.json()


def test_cluster_detail_unknown_id_404(client):
    r = client.get("/api/cluster/NOPE-123")
    assert r.status_code == 404
    assert "detail" in r.json()


# --- /api/map -------------------------------------------------------------

def test_map_shape(client):
    r = client.get("/api/map", params={"name": "Allston / Brighton"})
    assert r.status_code == 200
    body = r.json()
    bbox = body["bbox"]
    assert bbox["min_lat"] <= bbox["max_lat"]
    assert bbox["min_lon"] <= bbox["max_lon"]
    # The LE_ALLSTON block group bbox intersects the neighborhood case bbox.
    geoids = {bg["geoid"] for bg in body["block_groups"]}
    assert "LE_ALLSTON" in geoids
    for bg in body["block_groups"]:
        assert "limited_english" in bg and "rings" in bg
    # Markers are clusters size >= 2.
    assert all(m["size"] >= 2 for m in body["markers"])
    m = next(m for m in body["markers"] if m["id"] == "BCS-00250001")
    assert m["has_late"] is True  # the Pothole cluster has 1 late


def test_map_unknown_404(client):
    r = client.get("/api/map", params={"name": "UNKNOWN"})
    assert r.status_code == 404
    assert "detail" in r.json()


# --- robust bbox (outlier clipping) --------------------------------------

def test_robust_bbox_clips_default_geocode_outlier():
    # 100 tightly-clustered Roslindale points plus one City Hall outlier
    # (the default-geocode pin) that would otherwise blow the bbox way north.
    mapped = [
        {"latitude": 42.284 + (i % 5) * 0.001, "longitude": -71.128 + (i % 5) * 0.001}
        for i in range(100)
    ]
    outlier = {"latitude": 42.35982, "longitude": -71.05899}  # Boston City Hall
    mapped.append(dict(outlier))

    bbox = server._robust_bbox(mapped)

    # The 98th-percentile clip keeps the outlier out of the box.
    assert bbox["max_lat"] < outlier["latitude"]
    assert bbox["max_lon"] < outlier["longitude"]
    assert not server._in_bbox(bbox, outlier["latitude"], outlier["longitude"])
    # The dense real cluster stays inside the padded box.
    assert server._in_bbox(bbox, 42.284, -71.128)
    assert bbox["min_lat"] <= bbox["max_lat"]
    assert bbox["min_lon"] <= bbox["max_lon"]


def test_robust_bbox_single_point_has_nonzero_span():
    bbox = server._robust_bbox([{"latitude": 42.3, "longitude": -71.1}])
    assert bbox["min_lat"] < bbox["max_lat"]
    assert bbox["min_lon"] < bbox["max_lon"]
    assert server._in_bbox(bbox, 42.3, -71.1)


def test_percentile_endpoints_and_interpolation():
    data = [0.0, 1.0, 2.0, 3.0, 4.0]
    assert server._percentile(data, 0.0) == 0.0
    assert server._percentile(data, 1.0) == 4.0
    assert server._percentile(data, 0.5) == 2.0


# --- startup warm-up ------------------------------------------------------

def test_startup_warms_state_from_fixture_env(monkeypatch):
    # No request issued: entering the TestClient context triggers the lifespan
    # startup, which should warm the cache using the fixture env vars.
    monkeypatch.setenv("N1_SLICE", _SLICE)
    monkeypatch.setenv("N1_EJ", _EJ)
    monkeypatch.setenv("N1_PARAMS", _PARAMS)
    server.reset_state()
    assert server._STATE is None
    with TestClient(server.app):
        assert server._STATE is not None
        # Warmed from the fixtures (44 rows), not the real data slice.
        assert server._STATE.meta.get("counts", {}).get("total") == 44
    server.reset_state()
