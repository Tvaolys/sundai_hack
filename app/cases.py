"""Load and normalize Boston 311 rows from both export systems.

Two raw schemas exist (see .kiro/specs/n1-311triage/design.md "Raw schemas"):
  * "new" system (311.csv): case ids like BCS-..., UTC timestamps.
  * "legacy" system (311_legacy_2026.csv): naive local timestamps, HTML-escaped
    addresses.

Both are normalized to the same canonical dict. Neighborhood/category maps are
NOT applied here (that is task T12 / app/names.py).
"""
from __future__ import annotations

import html
import json
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

# Canonical fields produced by normalize_new / normalize_legacy.
CANONICAL_FIELDS = (
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
)

# Boston bounding box. Coordinates outside this are treated as invalid
# (kept in counts, but no lat/lon so they stay off the map — req 3).
BBOX_LAT_MIN = 42.22
BBOX_LAT_MAX = 42.41
BBOX_LON_MIN = -71.20
BBOX_LON_MAX = -70.98

# Legacy naive timestamps are local Boston time.
_LEGACY_TZ = ZoneInfo("America/New_York")


def _parse_on_time(value) -> bool | None:
    """ONTIME -> True, OVERDUE -> False, anything else -> None."""
    if value is None:
        return None
    v = str(value).strip().upper()
    if v == "ONTIME":
        return True
    if v == "OVERDUE":
        return False
    return None


def _in_bbox(lat: float, lon: float) -> bool:
    return (
        BBOX_LAT_MIN <= lat <= BBOX_LAT_MAX
        and BBOX_LON_MIN <= lon <= BBOX_LON_MAX
    )


def _parse_coord(lat_raw, lon_raw) -> tuple[float | None, float | None]:
    """Return (lat, lon) if both parse and fall inside the Boston bbox, else (None, None)."""
    try:
        lat = float(lat_raw)
        lon = float(lon_raw)
    except (TypeError, ValueError):
        return None, None
    if not _in_bbox(lat, lon):
        return None, None
    return lat, lon


def _parse_dt_utc(value) -> datetime | None:
    """Parse a new-system timestamp (UTC, trailing '+00'); return tz-aware or None."""
    if value is None:
        return None
    s = str(value).strip()
    if not s:
        return None
    # New system uses '+00'; datetime.fromisoformat wants '+00:00'.
    if s.endswith("+00"):
        s = s[:-3] + "+00:00"
    try:
        dt = datetime.fromisoformat(s)
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def _parse_dt_local(value) -> datetime | None:
    """Parse a legacy naive timestamp as America/New_York; return tz-aware or None."""
    if value is None:
        return None
    s = str(value).strip()
    if not s:
        return None
    try:
        dt = datetime.fromisoformat(s)
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=_LEGACY_TZ)
    return dt


def _empty(value):
    """Return None for empty/whitespace strings, else the stripped string."""
    if value is None:
        return None
    s = str(value).strip()
    return s or None


def normalize_new(row: dict) -> dict:
    """Normalize a new-system (311.csv) row to the canonical schema."""
    lat, lon = _parse_coord(row.get("latitude"), row.get("longitude"))
    status = _empty(row.get("case_status"))
    return {
        "case_id": _empty(row.get("case_id")),
        "system": "new",
        "source": _empty(row.get("report_source")),
        "open_date": _parse_dt_utc(row.get("open_date")),
        "close_date": _parse_dt_utc(row.get("close_date")),
        "raw_category": _empty(row.get("service_name")),
        "case_status": status,
        "on_time": _parse_on_time(row.get("on_time")),
        "neighborhood": _empty(row.get("neighborhood")),
        "ward": _empty(row.get("ward")),
        "address": _empty(row.get("full_address")),
        "latitude": lat,
        "longitude": lon,
        "is_open": status != "Closed",
    }


def normalize_legacy(row: dict) -> dict:
    """Normalize a legacy (311_legacy_2026.csv) row to the canonical schema."""
    lat, lon = _parse_coord(row.get("latitude"), row.get("longitude"))
    status = _empty(row.get("case_status"))
    address = row.get("location")
    if address is not None:
        address = html.unescape(str(address)).strip() or None
    return {
        "case_id": _empty(row.get("case_enquiry_id")),
        "system": "legacy",
        "source": _empty(row.get("source")),
        "open_date": _parse_dt_local(row.get("open_dt")),
        "close_date": _parse_dt_local(row.get("closed_dt")),
        "raw_category": _empty(row.get("type")),
        "case_status": status,
        "on_time": _parse_on_time(row.get("on_time")),
        "neighborhood": _empty(row.get("neighborhood")),
        "ward": _empty(row.get("ward")),
        "address": address,
        "latitude": lat,
        "longitude": lon,
        "is_open": status != "Closed",
    }


def load_cases(path) -> list[dict]:
    """Read the slim slice (JSON list from scripts/slim_311.py).

    open_date / close_date are stored as ISO strings; parse them back to
    tz-aware datetimes (None stays None).
    """
    with open(path, "r", encoding="utf-8") as fh:
        rows = json.load(fh)
    for row in rows:
        for key in ("open_date", "close_date"):
            val = row.get(key)
            if isinstance(val, str) and val:
                try:
                    row[key] = datetime.fromisoformat(val)
                except ValueError:
                    row[key] = None
            elif not val:
                row[key] = None
    return rows
