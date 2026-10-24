"""End-to-end demo-flow test for the n1-311triage API (task T11).

Walks the exact click path a judge sees in the 60-second demo, against the
committed fixtures, using the same N1_SLICE / N1_EJ / N1_PARAMS env-var
approach as ``tests/test_api.py``:

    /api/neighborhoods          -> pick the first neighborhood
    /api/neighborhood?name=...  -> stats + chronic + equity
    /api/clusters?name=...      -> repeat-report clusters (size >= 2)
    /api/cluster/{id}           -> raw rows behind the first cluster
    /api/map?name=...           -> offline SVG map payload

Every hop must return 200 and the documented shape. If the fixture has no
cluster of size >= 2 for the chosen neighborhood, the clusters list is asserted
to be an empty list rather than indexed into, so the test degrades gracefully.
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


def test_demo_flow(client):
    # 1. Neighborhoods list: non-empty, each has a name + positive total.
    r = client.get("/api/neighborhoods")
    assert r.status_code == 200
    neighborhoods = r.json()
    assert isinstance(neighborhoods, list) and neighborhoods
    for n in neighborhoods:
        assert isinstance(n["name"], str) and n["name"]
        assert isinstance(n["total"], int) and n["total"] > 0
    # Sorted, and never offers the UNKNOWN bucket.
    names = [n["name"] for n in neighborhoods]
    assert names == sorted(names)
    assert server.UNKNOWN not in names

    first = neighborhoods[0]["name"]

    # 2. Neighborhood detail: stats + chronic + equity shapes.
    r = client.get("/api/neighborhood", params={"name": first})
    assert r.status_code == 200
    detail = r.json()
    assert detail["name"] == first

    stats = detail["stats"]
    for key in ("total", "open", "known", "late", "rate"):
        assert key in stats
    # Counts are consistent: late <= known <= total (requirements 5/7).
    assert stats["late"] <= stats["known"] <= stats["total"]
    assert 0.0 <= stats["rate"] <= 1.0

    chronic = detail["chronic"]
    assert "ranked" in chronic and "too_few" in chronic
    assert isinstance(chronic["ranked"], list)
    assert isinstance(chronic["too_few"], list)

    equity = detail["equity"]
    assert "comparable" in equity
    # The caveat (requirement 15) is always present.
    assert "pattern in the city's own data" in equity["caveat"]

    # 3. Clusters: size >= 2, largest first.
    r = client.get("/api/clusters", params={"name": first})
    assert r.status_code == 200
    clusters = r.json()
    assert isinstance(clusters, list)
    sizes = [c["size"] for c in clusters]
    assert all(s >= 2 for s in sizes)
    assert sizes == sorted(sizes, reverse=True)

    # 4. Cluster detail for the first cluster (if any), else assert empty list.
    if clusters:
        first_cluster = clusters[0]
        for key in ("id", "category", "size", "late", "lat", "lon", "first", "last"):
            assert key in first_cluster
        r = client.get(f"/api/cluster/{first_cluster['id']}")
        assert r.status_code == 200
        cd = r.json()
        assert cd["id"] == first_cluster["id"]
        assert cd["category"] == first_cluster["category"]
        assert cd["size"] == first_cluster["size"]
        assert len(cd["rows"]) == first_cluster["size"]
        for row in cd["rows"]:
            for key in ("case_id", "open_date", "case_status", "on_time", "address", "system"):
                assert key in row
    else:
        # Graceful degradation: no repeat-report cluster in this fixture slice.
        assert clusters == []

    # 5. Map payload: bbox + block groups + markers (markers are clusters>=2).
    r = client.get("/api/map", params={"name": first})
    assert r.status_code == 200
    mp = r.json()
    bbox = mp["bbox"]
    assert bbox["min_lat"] <= bbox["max_lat"]
    assert bbox["min_lon"] <= bbox["max_lon"]
    assert isinstance(mp["block_groups"], list)
    for bg in mp["block_groups"]:
        assert "geoid" in bg and "limited_english" in bg and "rings" in bg
    assert isinstance(mp["markers"], list)
    for m in mp["markers"]:
        assert m["size"] >= 2
        assert "has_late" in m and "lat" in m and "lon" in m
