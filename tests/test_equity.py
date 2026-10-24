"""Offline tests for app.equity (loader + assignment)."""

from __future__ import annotations

import json
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


def test_pct_normalization_is_per_file_not_per_value():
    """Scale is detected once per file; mixed values with max > 1 stay as-is.

    The sample fixture has lim_eng_pct of 0.42, 12.5 and 8. Because the column
    max (12.5) exceeds 1.0 the file is already on a 0-100 scale, so the genuine
    small value 0.42 must NOT be inflated to 42.0 (the old per-value bug).
    """
    bgs = {bg["geoid"]: bg for bg in _load()}
    assert bgs["BG_A"]["lim_eng_pct"] == 0.42   # stays — file is 0-100 scaled
    assert bgs["BG_B"]["lim_eng_pct"] == 12.5
    assert bgs["BG_C"]["lim_eng_pct"] == 8.0


def _write_pct_fixture(tmp_path, values):
    """Write a minimal EJ cache with the given lim_eng_pct values."""
    bgs = []
    for i, v in enumerate(values):
        bgs.append(
            {
                "geoid": f"BG_{i}",
                "lim_eng_pct": v,
                "income": 50000,
                "population": 1000,
                "limited_english": False,
                "ej_criteria": "Minority",
                "rings": [[[0.0, 0.0], [0.0, 1.0], [1.0, 1.0], [1.0, 0.0], [0.0, 0.0]]],
            }
        )
    path = tmp_path / "ej.json"
    path.write_text(json.dumps({"block_groups": bgs}), encoding="utf-8")
    return str(path)


def test_pct_mixed_scale_file_unchanged(tmp_path):
    # max (40.0) > 1.0 -> already 0-100, every value left as-is.
    path = _write_pct_fixture(tmp_path, [0.549, 12.3, 40.0])
    pcts = [bg["lim_eng_pct"] for bg in load_block_groups(path)]
    assert pcts == [0.549, 12.3, 40.0]


def test_pct_fraction_file_scaled(tmp_path):
    # max (0.5) <= 1.0 -> 0-1 fraction, every value scaled by 100.
    path = _write_pct_fixture(tmp_path, [0.1, 0.5])
    pcts = [bg["lim_eng_pct"] for bg in load_block_groups(path)]
    assert pcts == [10.0, 50.0]


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
