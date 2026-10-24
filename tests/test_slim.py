"""Tests for scripts/slim_311.py — merge both 311 exports into a slice.

Offline only: runs on the two T1 fixtures, never on data/raw.
"""
from __future__ import annotations

import csv
import importlib.util
import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_REPO))

from app.cases import load_cases, load_meta  # noqa: E402


def _load_slim():
    spec = importlib.util.spec_from_file_location(
        "slim_311", _REPO / "scripts" / "slim_311.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


slim_311 = _load_slim()

FIXTURES = Path(__file__).parent / "fixtures"
NEW_CSV = FIXTURES / "311_new_sample.csv"
LEGACY_CSV = FIXTURES / "311_legacy_sample.csv"

PARAMS = {
    "window_start": "2026-01-01",
    "exclude_sources": ["Employee Generated", "City Worker App"],
}


def _write_params(tmp_path: Path) -> Path:
    p = tmp_path / "params.json"
    p.write_text(json.dumps(PARAMS), encoding="utf-8")
    return p


def _run(tmp_path: Path):
    out = tmp_path / "slice.json.gz"
    params = _write_params(tmp_path)
    rc = slim_311.main(
        ["--new", str(NEW_CSV), "--legacy", str(LEGACY_CSV),
         "--out", str(out), "--params", str(params)]
    )
    return rc, out


def _legacy_raw():
    with open(LEGACY_CSV, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def test_main_succeeds_and_writes_slice(tmp_path):
    rc, out = _run(tmp_path)
    assert rc == 0
    assert out.exists()


def test_row_count_matches_meta(tmp_path):
    _, out = _run(tmp_path)
    cases = load_cases(out)
    meta = load_meta(out)
    assert len(cases) == meta["counts"]["total"]
    by_system = {"new": 0, "legacy": 0}
    for c in cases:
        by_system[c["system"]] += 1
    assert by_system["new"] == meta["counts"]["new"]
    assert by_system["legacy"] == meta["counts"]["legacy"]


def test_source_filter_excludes_configured_sources(tmp_path):
    _, out = _run(tmp_path)
    cases = load_cases(out)
    # No kept row has an excluded source.
    for c in cases:
        assert c["source"] not in PARAMS["exclude_sources"]
    # The excluded counts match the fixture.
    meta = load_meta(out)
    legacy = _legacy_raw()
    expected = {}
    for row in legacy:
        src = (row["source"] or "").strip()
        if src in PARAMS["exclude_sources"]:
            expected[src] = expected.get(src, 0) + 1
    assert meta["excluded_by_source"] == expected
    assert expected, "fixture should contain excluded sources"


def test_window_filter_drops_bad_or_pre_window_dates(tmp_path):
    _, out = _run(tmp_path)
    cases = load_cases(out)
    # Every kept row has a parsed open_date on/after the window start.
    for c in cases:
        assert c["open_date"] is not None
        assert c["open_date"].isoformat() >= "2026-01-01"
    # The bad-timestamp legacy row (source not excluded) was dropped.
    assert not any(c["case_id"] == "101006640004" for c in cases)
    # The bad-date new row was dropped.
    assert not any(c["case_id"] == "BCS-00250007" for c in cases)


def test_mapping_applied(tmp_path):
    _, out = _run(tmp_path)
    cases = load_cases(out)
    # Category map collapses cross-system pothole names to "Pothole".
    by_id = {c["case_id"]: c for c in cases}
    # New: "Request for Pothole Repair" -> "Pothole"
    assert by_id["BCS-00250001"]["category"] == "Pothole"
    assert by_id["BCS-00250001"]["raw_category"] == "Request for Pothole Repair"
    # Legacy: "BWSC Pothole" -> "Pothole"
    assert by_id["101006640001"]["category"] == "Pothole"
    assert by_id["101006640001"]["raw_category"] == "BWSC Pothole"
    # Neighborhood canon applied (Allston -> Allston / Brighton).
    assert by_id["BCS-00250001"]["neighborhood"] == "Allston / Brighton"


def test_coords_rounded_to_5dp(tmp_path):
    _, out = _run(tmp_path)
    cases = load_cases(out)
    for c in cases:
        for coord in (c["latitude"], c["longitude"]):
            if coord is not None:
                assert round(coord, 5) == coord


def test_per_month_counts_sum_to_total(tmp_path):
    _, out = _run(tmp_path)
    meta = load_meta(out)
    assert sum(meta["per_month"].values()) == meta["counts"]["total"]


def test_load_cases_round_trips(tmp_path):
    _, out = _run(tmp_path)
    cases = load_cases(out)
    assert cases, "slice should have rows"
    c = cases[0]
    # Datetimes parsed back to tz-aware.
    assert c["open_date"].tzinfo is not None
    # Canonical fields present.
    for key in ("case_id", "system", "category", "raw_category", "on_time"):
        assert key in c


def test_missing_column_exits_nonzero(tmp_path, capsys):
    # A new file missing the required 'on_time' column.
    bad = tmp_path / "bad_new.csv"
    bad.write_text("case_id,open_date\nBCS-1,2026-07-01 10:00:00+00\n", encoding="utf-8")
    params = _write_params(tmp_path)
    rc = slim_311.main(
        ["--new", str(bad), "--legacy", str(LEGACY_CSV),
         "--out", str(tmp_path / "x.json.gz"), "--params", str(params)]
    )
    assert rc != 0
    err = capsys.readouterr().err
    assert "on_time" in err
