"""Merge both Boston 311 exports into one compact committed slice.

Reads the two raw CSV exports (gitignored, ~27 MB + ~107 MB) via the
``app/cases.py`` normalizers, applies the resident filter and name maps,
windows to ``params["window_start"]`` (America/New_York), rounds coords to
5 decimal places, and writes a gzip'd *columnar* JSON slice to
``data/311_slice.json.gz``.

155k rows as a plain JSON list of dicts would be ~40 MB; the columnar layout
(shared column names, one list per row of bare values) plus gzip keeps the
committed file well under the 15 MB target. See
``.kiro/specs/n1-311triage/design.md`` "Risks" re: size.

Slice shape::

    {
      "meta": {
        "sources": {...}, "generated_at": "...", "window": {...},
        "counts": {"new": n, "legacy": n, "total": n},
        "excluded_by_source": {source: n, ...},
        "per_month": {"2026-01": n, ...}
      },
      "columns": [...],
      "rows": [[...], ...]
    }

Datetimes are stored as ISO strings to the second (``YYYY-MM-DDТHH:MM:SS±HH:MM``);
``app/cases.load_cases`` parses them back to tz-aware datetimes.

CLI::

    python scripts/slim_311.py [--new PATH] [--legacy PATH] [--out PATH] [--params PATH]

Exits non-zero (naming the column) if a required column is missing from
either file.
"""
from __future__ import annotations

import argparse
import csv
import gzip
import json
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

# Allow running as a plain script (python scripts/slim_311.py).
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.cases import normalize_legacy, normalize_new  # noqa: E402
from app.names import canon_category, canon_neighborhood  # noqa: E402
from app.sla import load_params  # noqa: E402

_REPO = Path(__file__).resolve().parent.parent
DEFAULT_NEW = _REPO / "data" / "raw" / "311.csv"
DEFAULT_LEGACY = _REPO / "data" / "raw" / "311_legacy_2026.csv"
DEFAULT_OUT = _REPO / "data" / "311_slice.json.gz"
DEFAULT_PARAMS = _REPO / "data" / "params.json"

_EASTERN = ZoneInfo("America/New_York")

# Columns the normalizers read from each raw file. If any is absent the
# script aborts with a clear message (design.md: "fails loudly").
REQUIRED_NEW = (
    "case_id",
    "open_date",
    "close_date",
    "service_name",
    "case_status",
    "on_time",
    "report_source",
    "neighborhood",
    "ward",
    "full_address",
    "latitude",
    "longitude",
)
REQUIRED_LEGACY = (
    "case_enquiry_id",
    "open_dt",
    "closed_dt",
    "type",
    "case_status",
    "on_time",
    "source",
    "neighborhood",
    "ward",
    "location",
    "latitude",
    "longitude",
)

# Order of values in each columnar row.
COLUMNS = (
    "case_id",
    "system",
    "source",
    "open_date",
    "close_date",
    "category",
    "raw_category",
    "case_status",
    "on_time",
    "is_open",
    "neighborhood",
    "ward",
    "address",
    "latitude",
    "longitude",
)


class MissingColumn(Exception):
    """Raised when a required column is absent from a raw file."""


def _check_columns(header, required, label: str) -> None:
    have = set(header or ())
    missing = [c for c in required if c not in have]
    if missing:
        raise MissingColumn(
            f"{label} file is missing required column(s): "
            f"{', '.join(missing)}"
        )


def _iso_second(dt: datetime | None) -> str | None:
    """ISO string truncated to whole seconds, or None."""
    if dt is None:
        return None
    return dt.replace(microsecond=0).isoformat()


def _round_coord(value):
    return round(value, 5) if value is not None else None


def _month_key(dt: datetime) -> str:
    local = dt.astimezone(_EASTERN)
    return f"{local.year:04d}-{local.month:02d}"


def _read_csv(path: Path, required, label: str):
    """Yield raw rows, after verifying the header has every required column."""
    with open(path, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        _check_columns(reader.fieldnames, required, label)
        yield from reader


def build_slice(new_path, legacy_path, params: dict) -> dict:
    """Read both raw files, filter/map/window, return the columnar slice dict."""
    window_start_str = params["window_start"]
    window_start = datetime.fromisoformat(window_start_str).replace(tzinfo=_EASTERN)
    exclude_sources = set(params.get("exclude_sources", []))

    rows: list[list] = []
    counts = Counter()
    excluded_by_source = Counter()
    per_month = Counter()

    sources = (
        (new_path, REQUIRED_NEW, "new", normalize_new),
        (legacy_path, REQUIRED_LEGACY, "legacy", normalize_legacy),
    )
    for path, required, label, normalize in sources:
        for raw in _read_csv(Path(path), required, label):
            rec = normalize(raw)

            if rec["source"] in exclude_sources:
                excluded_by_source[rec["source"]] += 1
                continue

            open_date = rec["open_date"]
            if open_date is None or open_date < window_start:
                continue

            neighborhood = canon_neighborhood(rec["neighborhood"])
            category = canon_category(rec["raw_category"])

            rows.append(
                [
                    rec["case_id"],
                    rec["system"],
                    rec["source"],
                    _iso_second(open_date),
                    _iso_second(rec["close_date"]),
                    category,
                    rec["raw_category"],
                    rec["case_status"],
                    rec["on_time"],
                    rec["is_open"],
                    neighborhood,
                    rec["ward"],
                    rec["address"],
                    _round_coord(rec["latitude"]),
                    _round_coord(rec["longitude"]),
                ]
            )
            counts[rec["system"]] += 1
            per_month[_month_key(open_date)] += 1

    meta = {
        "sources": {
            "new": str(new_path),
            "legacy": str(legacy_path),
        },
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "window": {"start": window_start_str, "tz": "America/New_York"},
        "counts": {
            "new": counts["new"],
            "legacy": counts["legacy"],
            "total": counts["new"] + counts["legacy"],
        },
        "excluded_by_source": dict(sorted(excluded_by_source.items())),
        "per_month": dict(sorted(per_month.items())),
    }
    return {"meta": meta, "columns": list(COLUMNS), "rows": rows}


def write_slice(slice_obj: dict, out_path) -> int:
    """Write the slice as gzip'd JSON; return the file size in bytes."""
    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(slice_obj, ensure_ascii=False, separators=(",", ":"))
    with gzip.open(out, "wt", encoding="utf-8") as fh:
        fh.write(payload)
    return out.stat().st_size


def _print_summary(meta: dict, size_bytes: int) -> None:
    counts = meta["counts"]
    print("311 slice summary")
    print(f"  window start : {meta['window']['start']} ({meta['window']['tz']})")
    print("  rows per system:")
    print(f"    new    : {counts['new']}")
    print(f"    legacy : {counts['legacy']}")
    print(f"    total  : {counts['total']}")
    if meta["excluded_by_source"]:
        print("  excluded by source:")
        for src, n in meta["excluded_by_source"].items():
            print(f"    {src}: {n}")
    else:
        print("  excluded by source: (none)")
    print("  per month:")
    for month, n in meta["per_month"].items():
        print(f"    {month}: {n}")
    print(f"  slice size   : {size_bytes:,} bytes ({size_bytes / 1_000_000:.2f} MB)")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Slim/merge the two Boston 311 exports.")
    parser.add_argument("--new", default=str(DEFAULT_NEW), help="new-system CSV")
    parser.add_argument("--legacy", default=str(DEFAULT_LEGACY), help="legacy CSV")
    parser.add_argument("--out", default=str(DEFAULT_OUT), help="output .json.gz")
    parser.add_argument("--params", default=str(DEFAULT_PARAMS), help="params.json")
    args = parser.parse_args(argv)

    params = load_params(args.params)
    try:
        slice_obj = build_slice(args.new, args.legacy, params)
    except MissingColumn as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    size = write_slice(slice_obj, args.out)
    _print_summary(slice_obj["meta"], size)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
