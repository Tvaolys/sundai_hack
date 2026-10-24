"""SLA stats and chronic-category ranking (pure functions).

A "case" is a dict with at least:
  - ``on_time``: True (on time), False (late), or None (unknown SLA result)
  - ``is_open``: bool
  - ``category``: canonical category name (used by :func:`chronic`)

Late rate = late / (on-time + late); unknown on_time is excluded from the
"known" denominator (requirement 2).
"""

from __future__ import annotations

import json
from pathlib import Path

DEFAULT_PARAMS_PATH = Path(__file__).resolve().parent.parent / "data" / "params.json"


def load_params(path: str | Path = DEFAULT_PARAMS_PATH) -> dict:
    """Load tuning params from ``data/params.json`` (or an override path)."""
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def group_stats(cases: list[dict]) -> dict:
    """Aggregate SLA stats over a group of cases.

    Returns a dict with keys:
      - ``total``: number of cases
      - ``open``: cases where ``is_open`` is truthy
      - ``known``: cases with a known SLA result (on_time True or False)
      - ``late``: cases with ``on_time`` is False
      - ``rate``: late / known, or None when known == 0
    """
    total = len(cases)
    open_n = 0
    known = 0
    late = 0
    for case in cases:
        if case.get("is_open"):
            open_n += 1
        on_time = case.get("on_time")
        if on_time is True:
            known += 1
        elif on_time is False:
            known += 1
            late += 1
    rate = (late / known) if known else None
    return {
        "total": total,
        "open": open_n,
        "known": known,
        "late": late,
        "rate": rate,
    }


def chronic(cases: list[dict], min_n: int, top: int = 3) -> dict:
    """Rank categories by chronic lateness.

    Groups ``cases`` by ``case['category']``. Categories with fewer than
    ``min_n`` cases with a known SLA result are set aside as ``too_few``.
    The rest are ranked by late rate desc, late count desc, category asc,
    and the top ``top`` are returned.

    Returns ``{'ranked': [...], 'too_few': [...]}`` where each ranked entry
    is ``{category, late, known, rate}`` and ``too_few`` is a list of
    category names.
    """
    groups: dict[str, list[dict]] = {}
    for case in cases:
        groups.setdefault(case["category"], []).append(case)

    ranked_candidates: list[dict] = []
    too_few: list[str] = []
    for category, group in groups.items():
        stats = group_stats(group)
        known = stats["known"]
        if known < min_n:
            too_few.append(category)
            continue
        ranked_candidates.append(
            {
                "category": category,
                "late": stats["late"],
                "known": known,
                "rate": stats["rate"],
            }
        )

    ranked_candidates.sort(
        key=lambda r: (-r["rate"], -r["late"], r["category"])
    )
    too_few.sort()

    return {"ranked": ranked_candidates[:top], "too_few": too_few}
