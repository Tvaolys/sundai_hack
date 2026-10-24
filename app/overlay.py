"""EJ vs non-EJ late-rate comparison (pure functions).

Splits mapped reports into two groups and compares their late rates:
  - ``limited_english``: cases whose ``geoid`` falls in a block group flagged
    for limited-English isolation (``limited_english`` True in ``equity``).
  - ``other``: every other mapped case — a geoid in a non-limited-English EJ
    block group, or ``geoid`` None (outside every polygon = non-EJ area).

A "mapped" case is one with coordinates (``latitude`` is not None); cases that
were never mapped are skipped entirely (requirement 3). Late rate uses the same
rule as :mod:`app.sla`: late / (on-time + late); unknown ``on_time`` is excluded
from the "known" denominator (requirement 2).

If either group has fewer than ``min_n`` cases with a known SLA result, the
comparison is not meaningful: both rates are left as ``None``, ``comparable`` is
False and ``message`` is "NOT ENOUGH DATA TO COMPARE" (requirements 13-14).
"""

from __future__ import annotations

from app.sla import group_stats

CAVEAT = "Shows a pattern in the city's own data, not its cause."
RULE = "Late rate in limited-English EJ block groups vs. all other reports."
NOT_ENOUGH = "NOT ENOUGH DATA TO COMPARE"


def _group_result(cases: list[dict]) -> dict:
    stats = group_stats(cases)
    return {"late": stats["late"], "known": stats["known"], "rate": stats["rate"]}


def compare(cases: list[dict], bgs: list[dict], min_n: int) -> dict:
    """Compare late rates between limited-English EJ block groups and the rest.

    ``cases`` must already be assigned (``case['geoid']`` set, possibly None).
    ``bgs`` is the loaded block-group list (see :func:`app.equity.load_block_groups`).
    Returns a dict with ``limited_english`` and ``other`` group summaries
    (``{late, known, rate}`` each), ``comparable``, ``message``, ``caveat`` and
    ``rule``. When either group's known count is below ``min_n`` the rates are
    set to None and ``comparable`` is False.
    """
    lim_eng_geoids = {
        bg["geoid"] for bg in bgs if bg.get("limited_english") and bg.get("geoid") is not None
    }

    limited: list[dict] = []
    other: list[dict] = []
    for case in cases:
        if case.get("latitude") is None:
            continue  # never mapped (requirement 3)
        geoid = case.get("geoid")
        if geoid is not None and geoid in lim_eng_geoids:
            limited.append(case)
        else:
            other.append(case)

    lim_result = _group_result(limited)
    other_result = _group_result(other)

    comparable = lim_result["known"] >= min_n and other_result["known"] >= min_n
    message = None
    if not comparable:
        lim_result = {**lim_result, "rate": None}
        other_result = {**other_result, "rate": None}
        message = NOT_ENOUGH

    return {
        "limited_english": lim_result,
        "other": other_result,
        "comparable": comparable,
        "message": message,
        "caveat": CAVEAT,
        "rule": RULE,
    }
