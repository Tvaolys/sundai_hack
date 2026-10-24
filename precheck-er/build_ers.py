"""
build_ers.py — Turn raw MassGIS hospital data into PreCheck ER's ER directory.

Source: MassGIS Massachusetts_Hospitals (EMERGENCY_DEPT='Yes'), with trauma
level, stroke tier, burn unit, and pediatric-ICU capability fields. These let
PreCheck route an emergency to the nearest *appropriate* ER, not just the
nearest building.

Output: data/ers.json
"""

import json
import os

HERE = os.path.dirname(__file__)
DATA = os.path.join(HERE, "data")


def clean(v):
    if v in (None, "", "N/A", "NA"):
        return None
    return v


def build():
    raw = json.load(open(os.path.join(DATA, "raw_ers.json")))
    ers = []
    for f in raw["features"]:
        a = f["attributes"]
        g = f.get("geometry") or {}
        if "x" not in g:
            continue
        ers.append({
            "name": (a.get("FACILITY_NAME") or "ER").title(),
            "muni": (a.get("MUNICIPALITY") or "").title(),
            "address": (a.get("STREET_ADDRESS") or "").title(),
            "phone": a.get("PHONE"),
            "lat": g["y"], "lon": g["x"],
            "trauma_adult": clean(a.get("TRAUMA_LEVEL_ADULT")),
            "trauma_peds": clean(a.get("TRAUMA_LEVEL_PEDS")),
            "stroke": clean(a.get("DPH_STROKE_TIER")),
            "burn": (a.get("BURN_UNIT") or 0) and int(float(a.get("BURN_UNIT") or 0)) > 0,
            "peds_icu": (a.get("PEDIATRIC_ICU") or 0) and int(float(a.get("PEDIATRIC_ICU") or 0)) > 0,
            "total_beds": int(float(a.get("TOTAL_BEDS") or 0)),
        })
    ers.sort(key=lambda e: e["name"])
    out = os.path.join(DATA, "ers.json")
    json.dump(ers, open(out, "w"), indent=2)
    return ers, out


if __name__ == "__main__":
    ers, out = build()
    print(f"wrote {out} with {len(ers)} emergency departments")
    print("trauma Level I centers:", sum(1 for e in ers if e["trauma_adult"] == "Level I"))
    print("endovascular stroke centers:", sum(1 for e in ers if e["stroke"] == "Endovascular Capable Stroke Service"))
