"""
routing.py — nearest-APPROPRIATE-ER selection with capacity/diversion awareness.

Given a patient location and an emergency type, pick the best ER. "Best" isn't
just nearest: a suspected stroke should go to a stroke-capable center, major
trauma to a trauma center, a pediatric case to a peds-capable ER, etc. We also
account for ER load ("diversion" — too full to accept), so the router can skip a
closer-but-saturated ER. Each candidate carries a human-readable reason it was
chosen or skipped, so the map can explain the decision.
"""

import json
import math
import os
import random

HERE = os.path.dirname(__file__)
ERS = json.load(open(os.path.join(HERE, "data", "ers.json")))

# Simulated live ER load (0..1 occupancy). Real deployments would pull this from
# a regional bed-availability / EMS diversion feed. Seeded for a stable demo.
_rng = random.Random(7)
ER_LOAD = {}


def _init_load():
    for er in ERS:
        ER_LOAD[er["name"]] = round(_rng.uniform(0.35, 0.9), 2)


_init_load()
DIVERSION_THRESHOLD = 0.85  # >= this => on diversion (won't accept unless no alternative)


EMERGENCY_TYPES = {
    "cardiac":   {"label": "Cardiac / chest pain", "need": None},
    "stroke":    {"label": "Suspected stroke",     "need": "stroke"},
    "trauma":    {"label": "Major trauma / fall",  "need": "trauma_adult"},
    "burn":      {"label": "Severe burn",          "need": "burn"},
    "pediatric": {"label": "Pediatric emergency",  "need": "peds"},
    "general":   {"label": "General / unknown",    "need": None},
}

STROKE_RANK = {
    "Endovascular Capable Stroke Service": 3,
    "Primary Stroke Service": 2,
    "Acute Stroke Ready Service": 1,
}
TRAUMA_RANK = {"Level I": 3, "Level II": 2, "Level III": 1}


def haversine_km(a_lat, a_lon, b_lat, b_lon):
    R = 6371.0
    p = math.pi / 180
    dlat = (b_lat - a_lat) * p
    dlon = (b_lon - a_lon) * p
    x = (math.sin(dlat / 2) ** 2 +
         math.cos(a_lat * p) * math.cos(b_lat * p) * math.sin(dlon / 2) ** 2)
    return 2 * R * math.asin(math.sqrt(x))


def _capability_score(er, need):
    """Returns (bonus, matched_bool, reason)."""
    if need == "stroke":
        rank = STROKE_RANK.get(er.get("stroke"), 0)
        return rank * 8, rank > 0, (er["stroke"] if rank else "no stroke designation")
    if need == "trauma_adult":
        rank = TRAUMA_RANK.get(er.get("trauma_adult"), 0)
        return rank * 8, rank > 0, (f"Adult Trauma {er['trauma_adult']}" if rank else "not a trauma center")
    if need == "burn":
        return (20, True, "burn unit") if er.get("burn") else (0, False, "no burn unit")
    if need == "peds":
        has = bool(er.get("peds_icu") or er.get("trauma_peds"))
        return (15, True, "pediatric-capable") if has else (0, False, "limited pediatric care")
    return 0, True, "general ER"


def _eta_minutes(km):
    # Rough ground-ambulance ETA: ~45 km/h effective urban speed + a 3-minute
    # dispatch/mobilization constant. Planning estimate only.
    return round(3 + (km / 45.0) * 60, 1)


def rank_ers(lat, lon, etype, limit=6):
    need = EMERGENCY_TYPES.get(etype, EMERGENCY_TYPES["general"])["need"]
    scored = []
    for er in ERS:
        dist = haversine_km(lat, lon, er["lat"], er["lon"])
        cap, matched, reason = _capability_score(er, need)
        load = ER_LOAD.get(er["name"], 0.5)
        diverting = load >= DIVERSION_THRESHOLD

        # Score: capability dominates, then distance, with a penalty for load.
        score = cap - dist * 0.5 - (load * 4) - (30 if diverting else 0)

        # Build a decision reason.
        skip = None
        if need and not matched:
            skip = f"skipped: {reason}"
        elif diverting:
            skip = f"skipped: on diversion ({int(load*100)}% full)"

        scored.append({
            "name": er["name"], "muni": er["muni"], "address": er["address"],
            "phone": er["phone"], "lat": er["lat"], "lon": er["lon"],
            "distance_km": round(dist, 1), "eta_min": _eta_minutes(dist),
            "capability_reason": reason, "capability_matched": matched,
            "load_pct": int(load * 100), "diverting": diverting,
            "trauma_adult": er.get("trauma_adult"), "stroke": er.get("stroke"),
            "burn": er.get("burn"), "peds_icu": er.get("peds_icu"),
            "skip_reason": skip,
            "_score": round(score, 2), "_dist": dist,
        })
    scored.sort(key=lambda e: e["_score"], reverse=True)
    chosen = scored[0] if scored else None

    # Nearer ERs that were NOT chosen (for the "why skipped" map overlay):
    # any ER closer than the chosen one.
    skipped_nearer = []
    if chosen:
        for e in scored:
            if e["name"] == chosen["name"]:
                continue
            if e["_dist"] < chosen["_dist"]:
                skipped_nearer.append(e)
    skipped_nearer.sort(key=lambda e: e["_dist"])

    return scored[:limit], need, chosen, skipped_nearer[:4]


def set_load(name, pct):
    ER_LOAD[name] = max(0.0, min(1.0, pct / 100.0))
