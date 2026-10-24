"""Canonical neighborhood / category name maps.

Both maps live in ``data/*.json`` (curated by a human, see
``.kiro/specs/n1-311triage/design.md`` "Neighborhood map" / "Category map").
The 311 normalizers in ``app/cases.py`` produce ``raw_category`` / ``neighborhood``;
this module collapses same-problem names across the two 311 export systems into one
canonical name so clustering and chronic ranking count each problem once.

JSON shape (both files):
    {"placeholder": true, "map": {raw: {"canonical": ..., "rows": n, "placeholder": ...}}}

``canon_neighborhood`` and ``canon_category`` are idempotent:
``canon(canon(x)) == canon(x)`` for every input.
"""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

_DATA_DIR = Path(__file__).resolve().parent.parent / "data"
_NEIGHBORHOOD_MAP_PATH = _DATA_DIR / "neighborhood_map.json"
_CATEGORY_MAP_PATH = _DATA_DIR / "category_map.json"


def _load_map(path: Path) -> dict[str, str]:
    """Load a name map file -> {raw: canonical}."""
    with open(path, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    return {raw: entry["canonical"] for raw, entry in data["map"].items()}


@lru_cache(maxsize=1)
def _neighborhood_map() -> dict[str, str]:
    return _load_map(_NEIGHBORHOOD_MAP_PATH)


@lru_cache(maxsize=1)
def _category_map() -> dict[str, str]:
    return _load_map(_CATEGORY_MAP_PATH)


def canon_neighborhood(raw) -> str:
    """Map a raw neighborhood name to its canonical name.

    Listed names map to a coarser canonical; the UNKNOWN set ('', 'Boston',
    'Chestnut Hill') maps to 'UNKNOWN'. Every other value (incl. unmapped
    names) passes through stripped of surrounding whitespace.
    """
    key = "" if raw is None else str(raw).strip()
    return _neighborhood_map().get(key, key)


def canon_category(raw) -> str:
    """Map a raw 311 category to its canonical name.

    Mapped raw values collapse cross-system duplicates to one canonical name;
    unmapped values pass through stripped of surrounding whitespace.
    """
    key = "" if raw is None else str(raw).strip()
    return _category_map().get(key, key)
