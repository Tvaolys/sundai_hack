"""Offline tests for app.equity (loader + assignment)."""

from __future__ import annotations

import os

from hypothesis import given
from hypothesis import strategies as st

from app.equity import assign, load_block_groups

_FIXTURE = os.path.join(os.path.dirname(__file__), "fixtures", "ej_sample.json")

_GEOIDS = {"BG_A", "BG_B", "BG_C"}


def _load():
    return load_block_groups(_FIXTURE)


def test_loads_three_block_groups():
    bgs = _load()
    assert len(bgs) == 3
    assert {bg["geoid"] for bg in bgs} == _GEOIDS
    for bg in bgs:
        assert "bbox" in bg and len(bg["bbox"]) == 4


def test_pct_normalization_0_1_and_0_100():
    bgs = {bg["geoid"]: bg for bg in _load()}
    # BG_A stored as 0.42 (0-1 scale) -> 42.0
    assert bgs["BG_A"]["lim_eng_pct"] == 42.0
    # BG_B stored as 12.5 (already 0-100) -> unchanged
    assert bgs["BG_B"]["lim_eng_pct"] == 12.5
    # BG_C stored as 8 -> unchanged (> 1)
    assert bgs["BG_C"]["lim_eng_pct"] == 8.0


def test_income_sentinel_to_none():
    bgs = {bg["geoid"]: bg for bg in _load()}
    assert bgs["BG_B"]["income"] is None  # -666666666 sentinel
    assert bgs["BG_A"]["income"] == 65000.0


def test_limited_english_flag():
    bgs = {bg["geoid"]: bg for bg in _load()}
    assert bgs["BG_A"]["limited_english"] is True
    assert bgs["BG_B"]["limited_english"] is False


def test_assign_inside_outside_hole_and_unmapped():
    bgs = _load()
    cases = [
        {"longitude": 0.5, "latitude": 0.5},   # inside BG_A
        {"longitude": 3.0, "latitude": 1.0},   # in BG_B hole -> outside
        {"longitude": 2.25, "latitude": 1.0},  # inside BG_B (outside hole)
        {"longitude": 5.5, "latitude": 5.5},   # inside BG_C
        {"longitude": 10.0, "latitude": 10.0}, # outside everything
        {"longitude": None, "latitude": None}, # unmapped (no coords)
    ]
    assign(cases, bgs)
    assert cases[0]["geoid"] == "BG_A"
    assert cases[1]["geoid"] is None       # hole
    assert cases[2]["geoid"] == "BG_B"
    assert cases[3]["geoid"] == "BG_C"
    assert cases[4]["geoid"] is None       # outside all
    assert cases[5]["geoid"] is None       # unmapped


def test_assign_returns_same_list_mutated():
    bgs = _load()
    cases = [{"longitude": 0.5, "latitude": 0.5}]
    out = assign(cases, bgs)
    assert out[0] is cases[0]
    assert cases[0]["geoid"] == "BG_A"


@given(
    lon=st.floats(min_value=-5, max_value=15, allow_nan=False, allow_infinity=False),
    lat=st.floats(min_value=-5, max_value=15, allow_nan=False, allow_infinity=False),
)
def test_property_at_most_one_geoid(lon, lat):
    bgs = _load()
    case = {"longitude": lon, "latitude": lat}
    assign([case], bgs)
    assert case["geoid"] in _GEOIDS or case["geoid"] is None
