"""Tests for app/cases.py — 311 row normalizer (both schemas)."""
from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path

from hypothesis import given, strategies as st

from app.cases import (
    BBOX_LAT_MAX,
    BBOX_LAT_MIN,
    BBOX_LON_MAX,
    BBOX_LON_MIN,
    load_cases,
    normalize_legacy,
    normalize_new,
)

FIXTURES = Path(__file__).parent / "fixtures"
NEW_CSV = FIXTURES / "311_new_sample.csv"
LEGACY_CSV = FIXTURES / "311_legacy_sample.csv"

CANONICAL = {
    "case_id",
    "system",
    "source",
    "open_date",
    "close_date",
    "raw_category",
    "case_status",
    "on_time",
    "neighborhood",
    "ward",
    "address",
    "latitude",
    "longitude",
    "is_open",
}


def _read_rows(path: Path) -> list[dict]:
    with open(path, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def test_fixtures_exist_and_are_small():
    for path in (NEW_CSV, LEGACY_CSV):
        rows = _read_rows(path)
        assert 20 <= len(rows) <= 30, f"{path.name} should have ~25 rows, got {len(rows)}"


def test_new_rows_normalize_to_canonical():
    for row in _read_rows(NEW_CSV):
        out = normalize_new(row)
        assert set(out) == CANONICAL
        assert out["system"] == "new"
        assert out["on_time"] in (True, False, None)


def test_legacy_rows_normalize_to_canonical():
    for row in _read_rows(LEGACY_CSV):
        out = normalize_legacy(row)
        assert set(out) == CANONICAL
        assert out["system"] == "legacy"
        assert out["on_time"] in (True, False, None)


def test_new_open_date_is_utc_aware():
    rows = _read_rows(NEW_CSV)
    out = normalize_new(rows[0])
    assert out["open_date"].tzinfo is not None
    assert out["open_date"].utcoffset() == timezone.utc.utcoffset(None)


def test_legacy_open_date_is_tz_aware_eastern():
    rows = _read_rows(LEGACY_CSV)
    out = normalize_legacy(rows[0])
    assert out["open_date"].tzinfo is not None
    # America/New_York is never UTC.
    assert out["open_date"].utcoffset().total_seconds() != 0


def test_bad_date_becomes_none():
    bad_new = {"case_id": "X", "open_date": "not-a-real-date", "latitude": "42.3", "longitude": "-71.07"}
    assert normalize_new(bad_new)["open_date"] is None
    bad_legacy = {"case_enquiry_id": "Y", "open_dt": "bad-timestamp", "latitude": "42.3", "longitude": "-71.07"}
    assert normalize_legacy(bad_legacy)["open_date"] is None


def test_missing_on_time_is_none():
    assert normalize_new({"on_time": ""})["on_time"] is None
    assert normalize_new({})["on_time"] is None
    assert normalize_legacy({"on_time": "maybe"})["on_time"] is None


def test_on_time_mapping():
    assert normalize_new({"on_time": "ONTIME"})["on_time"] is True
    assert normalize_new({"on_time": "OVERDUE"})["on_time"] is False


def test_missing_coords_are_none():
    out = normalize_new({"latitude": "", "longitude": ""})
    assert out["latitude"] is None and out["longitude"] is None


def test_out_of_bbox_coords_are_none():
    # Way outside Boston.
    out = normalize_new({"latitude": "45.0", "longitude": "-80.0"})
    assert out["latitude"] is None and out["longitude"] is None
    # Legacy row with lat 99.
    out2 = normalize_legacy({"latitude": "99.0", "longitude": "-71.0"})
    assert out2["latitude"] is None and out2["longitude"] is None


def test_in_bbox_coords_kept():
    out = normalize_new({"latitude": "42.33688454", "longitude": "-71.07517515"})
    assert out["latitude"] == 42.33688454
    assert out["longitude"] == -71.07517515


def test_legacy_address_html_unescaped():
    row = {"location": "INTERSECTION of Wilkes Psge &amp; Washington St  Roxbury  MA"}
    out = normalize_legacy(row)
    assert "&amp;" not in out["address"]
    assert "&" in out["address"]


def test_is_open_from_status():
    assert normalize_new({"case_status": "Closed"})["is_open"] is False
    assert normalize_new({"case_status": "In progress"})["is_open"] is True
    assert normalize_legacy({"case_status": "Open"})["is_open"] is True
    assert normalize_legacy({"case_status": "Closed"})["is_open"] is False


def test_load_cases_parses_iso_dates(tmp_path):
    slice_path = tmp_path / "311_slice.json"
    data = [
        {
            "case_id": "BCS-1",
            "system": "new",
            "open_date": "2026-07-14T10:56:30.994145+00:00",
            "close_date": "",
            "on_time": True,
        },
        {
            "case_id": "L-1",
            "system": "legacy",
            "open_date": "2026-05-02T09:14:00-04:00",
            "close_date": None,
            "on_time": None,
        },
    ]
    slice_path.write_text(json.dumps(data), encoding="utf-8")
    cases = load_cases(slice_path)
    assert isinstance(cases[0]["open_date"], datetime)
    assert cases[0]["open_date"].tzinfo is not None
    assert cases[0]["close_date"] is None
    assert cases[1]["close_date"] is None
    assert isinstance(cases[1]["open_date"], datetime)


# --- property-based test -------------------------------------------------

@given(st.text())
def test_on_time_always_tristate_new(value):
    assert normalize_new({"on_time": value})["on_time"] in (True, False, None)


@given(st.text())
def test_on_time_always_tristate_legacy(value):
    assert normalize_legacy({"on_time": value})["on_time"] in (True, False, None)


@given(
    st.one_of(st.none(), st.text(), st.floats(allow_nan=True, allow_infinity=True)),
    st.one_of(st.none(), st.text(), st.floats(allow_nan=True, allow_infinity=True)),
)
def test_coords_none_or_in_bbox(lat_raw, lon_raw):
    out = normalize_new({"latitude": lat_raw, "longitude": lon_raw})
    lat, lon = out["latitude"], out["longitude"]
    assert (lat is None) == (lon is None)
    if lat is not None:
        assert BBOX_LAT_MIN <= lat <= BBOX_LAT_MAX
        assert BBOX_LON_MIN <= lon <= BBOX_LON_MAX
