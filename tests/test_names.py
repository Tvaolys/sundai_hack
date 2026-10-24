"""Tests for app/names.py (canonical neighborhood / category maps).

Tests read only the committed data/*_map.json files, never data/raw/.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest
from hypothesis import given, strategies as st

from app.names import canon_category, canon_neighborhood

_DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def _load(name: str) -> dict:
    with open(_DATA_DIR / name, "r", encoding="utf-8") as fh:
        return json.load(fh)


NEIGHBORHOOD_MAP = _load("neighborhood_map.json")
CATEGORY_MAP = _load("category_map.json")


# --- Neighborhood seed pairs from design.md -------------------------------

NEIGHBORHOOD_SEEDS = [
    ("Allston", "Allston / Brighton"),
    ("Brighton", "Allston / Brighton"),
    ("Allston / Brighton", "Allston / Brighton"),
    ("South Boston", "South Boston"),
    ("South Boston Waterfront", "South Boston"),
    ("South Boston / South Boston Waterfront", "South Boston"),
    ("Fenway", "Fenway / Longwood"),
    ("Longwood", "Fenway / Longwood"),
    ("Fenway / Kenmore / Audubon Circle / Longwood", "Fenway / Longwood"),
    ("Mattapan", "Mattapan"),
    ("Greater Mattapan", "Mattapan"),
    ("Downtown", "Downtown"),
    ("Downtown / Financial District", "Downtown"),
    ("Chinatown", "Downtown"),
    ("Leather District", "Downtown"),
    ("Bay Village", "Downtown"),
    ("West End", "Downtown"),
    ("North End", "Downtown"),
    ("", "UNKNOWN"),
    ("Boston", "UNKNOWN"),
    ("Chestnut Hill", "UNKNOWN"),
]


@pytest.mark.parametrize("raw,expected", NEIGHBORHOOD_SEEDS)
def test_neighborhood_seed_pairs(raw, expected):
    assert canon_neighborhood(raw) == expected


def test_neighborhood_unknown_passes_through():
    # A name not in the map keeps itself.
    assert canon_neighborhood("Roxbury") == "Roxbury"
    assert canon_neighborhood("Dorchester") == "Dorchester"


def test_neighborhood_strips_whitespace():
    assert canon_neighborhood("  Roxbury  ") == "Roxbury"
    assert canon_neighborhood("  Allston ") == "Allston / Brighton"


def test_neighborhood_none_is_unknown():
    assert canon_neighborhood(None) == "UNKNOWN"


# --- Category seed pairs from design.md -----------------------------------

CATEGORY_SEEDS = [
    ("Request for Pothole Repair", "Pothole"),
    ("BWSC Pothole", "Pothole"),
    ("Pothole", "Pothole"),
    ("Sidewalk Repair (Make Safe)", "Sidewalk Repair"),
    ("Sidewalk Repair", "Sidewalk Repair"),
    ("Improper Storage of Trash (Barrels)", "Improper Trash Storage"),
    ("Improper Trash Storage", "Improper Trash Storage"),
    ("Missed Trash/Recycling/Yard Waste/Bulk Item", "Missed Waste Pick-up"),
    ("Missed Waste Pick-up", "Missed Waste Pick-up"),
    ("Illegal Dumping", "Illegal Dumping"),
    ("Illegal Dumping or Disposal", "Illegal Dumping"),
    ("Graffiti Removal", "Graffiti"),
    ("PWD Graffiti", "Graffiti"),
    ("Illegal Graffiti", "Graffiti"),
    ("Pick up Dead Animal", "Dead Animal"),
    ("Dead Animal General", "Dead Animal"),
    ("Request for Snow Plowing", "Snow Plowing"),
    ("Snow Plowing", "Snow Plowing"),
    ("Parking Enforcement", "Illegal Parking"),
    ("Illegal Parking", "Illegal Parking"),
    ("Sign Repair", "Sign Repair"),
    ("Damaged/Faded Sign", "Sign Repair"),
    ("Missing Sign", "Sign Repair"),
    ("Missing / Knocked Down Sign", "Sign Repair"),
    ("Knocked Down Sign", "Sign Repair"),
    ("Tree Maintenance Requests", "Tree Pruning"),
    ("Pruning Request", "Tree Pruning"),
    ("Code Enforcement Collection", "Code Enforcement Collection"),
    ("CE Collection", "Code Enforcement Collection"),
]


@pytest.mark.parametrize("raw,expected", CATEGORY_SEEDS)
def test_category_seed_pairs(raw, expected):
    assert canon_category(raw) == expected


def test_category_unknown_passes_through():
    assert canon_category("Some Brand New Service Type") == "Some Brand New Service Type"


def test_category_strips_whitespace():
    assert canon_category("  Pothole  ") == "Pothole"
    assert canon_category("  Totally Unmapped  ") == "Totally Unmapped"


def test_category_entries_have_rows_and_placeholder():
    for raw, entry in CATEGORY_MAP["map"].items():
        assert "canonical" in entry
        assert isinstance(entry["rows"], int)
        assert entry["placeholder"] is True


def test_every_seed_pair_present_in_map():
    for raw, _ in CATEGORY_SEEDS:
        assert raw in CATEGORY_MAP["map"], raw


# --- Idempotency (property) -----------------------------------------------

_known_neighborhoods = list(NEIGHBORHOOD_MAP["map"].keys()) + [
    c for c in {e["canonical"] for e in NEIGHBORHOOD_MAP["map"].values()}
]
_known_categories = list(CATEGORY_MAP["map"].keys()) + [
    c for c in {e["canonical"] for e in CATEGORY_MAP["map"].values()}
]


@given(st.one_of(st.text(), st.sampled_from(_known_neighborhoods)))
def test_canon_neighborhood_idempotent(raw):
    once = canon_neighborhood(raw)
    assert canon_neighborhood(once) == once


@given(st.one_of(st.text(), st.sampled_from(_known_categories)))
def test_canon_category_idempotent(raw):
    once = canon_category(raw)
    assert canon_category(once) == once


def test_canonical_names_map_to_themselves():
    # Every canonical target must be a fixed point of canon_*.
    for entry in NEIGHBORHOOD_MAP["map"].values():
        c = entry["canonical"]
        assert canon_neighborhood(c) == c
    for entry in CATEGORY_MAP["map"].values():
        c = entry["canonical"]
        assert canon_category(c) == c
