"""
app.py — PreCheck ER demo server.

Roles share one live relay:
  - Patient client ( / )   : medical profile + SOS + simulated live vitals
  - ER dashboard   ( /er ) : incoming patients pre-filled, with vitals + triage
  - EMS crew view  ( /ems ): the ambulance crew's enroute view of the patient

Endpoints:
  GET  /  /er  /ems               -> the three UIs
  GET  /api/ers?lat=&lon=&type=   -> ranked nearest-appropriate ERs (+ skipped)
  GET  /api/profile  POST         -> read / update the demo profile
  GET  /api/fhir                  -> profile as a FHIR R4 bundle
  POST /api/sos                   -> trigger an emergency (routes to best ER)
  POST /api/vitals                -> patient pushes a vitals sample
  GET  /api/active                -> inbound cases + vitals + triage + SBAR
  GET  /api/case/<id>             -> one case (EMS crew view)
  POST /api/resolve               -> mark a case arrived / clear it
  POST /api/mci                   -> spawn N simulated mass-casualty patients
  GET  /api/events                -> recent system events (contact notify, etc.)

DEMO: watch/phone + vitals are simulated, patients fictional. ER routing uses
real MassGIS data. No real PHI; not HIPAA-compliant; not for clinical use.
"""

import json
import os
import random
import time
import uuid

from flask import Flask, jsonify, request, send_from_directory

import clinical
import routing

HERE = os.path.dirname(__file__)
STATE_PATH = os.path.join(HERE, "data", "state.json")
app = Flask(__name__, static_folder="static")
app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 0


@app.after_request
def no_cache(resp):
    resp.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    resp.headers["Pragma"] = "no-cache"
    return resp


DEFAULT_PROFILE = {
    "name": "Jordan Rivera", "dob": "1979-03-14", "age": 47, "sex": "F",
    "blood_type": "O+", "language": "Portuguese",
    "conditions": ["Type 2 diabetes", "Hypertension", "Prior MI (2023)"],
    "medications": ["Metformin 1000mg", "Lisinopril 20mg", "Atorvastatin 40mg", "Aspirin 81mg"],
    "allergies": ["Penicillin", "Shellfish"],
    "emergency_contact": {"name": "Sam Rivera (spouse)", "phone": "(617) 555-0134"},
    "insurance": {"provider": "Mass General Brigham Health Plan", "member_id": "MGB-4471982"},
    "dnr": False, "notes": "Pacemaker implanted 2023. Carries nitroglycerin.",
    "baseline_hr": 74,
}

# ---- Persistent state (survives dev-server reloads / crashes) ----
STATE = {"profile": dict(DEFAULT_PROFILE), "active": {}, "events": []}


def load_state():
    global STATE
    try:
        if os.path.exists(STATE_PATH):
            STATE = json.load(open(STATE_PATH))
            STATE.setdefault("profile", dict(DEFAULT_PROFILE))
            STATE.setdefault("active", {})
            STATE.setdefault("events", [])
    except Exception:
        STATE = {"profile": dict(DEFAULT_PROFILE), "active": {}, "events": []}


def save_state():
    try:
        json.dump(STATE, open(STATE_PATH, "w"))
    except Exception:
        pass


def log_event(kind, text):
    STATE["events"].insert(0, {"t": round(time.time(), 1), "kind": kind, "text": text})
    STATE["events"] = STATE["events"][:30]


load_state()

# Synthetic alt-patients for mass-casualty mode.
MCI_PATIENTS = [
    {"name": "Alex Chen", "age": 29, "sex": "M", "blood_type": "A+", "language": "Mandarin",
     "conditions": ["Asthma"], "medications": ["Albuterol inhaler"], "allergies": ["NKDA"],
     "notes": "Wheezing reported.", "baseline_hr": 68},
    {"name": "Maria Santos", "age": 61, "sex": "F", "blood_type": "B+", "language": "Spanish",
     "conditions": ["COPD", "Atrial fibrillation"], "medications": ["Warfarin", "Tiotropium"],
     "allergies": ["Sulfa"], "notes": "On blood thinners — bleeding risk.", "baseline_hr": 82},
    {"name": "Derek Boyle", "age": 44, "sex": "M", "blood_type": "O-", "language": "English",
     "conditions": [], "medications": [], "allergies": ["NKDA"],
     "notes": "Leg deformity, possible fracture.", "baseline_hr": 70},
    {"name": "Priya Nair", "age": 8, "sex": "F", "blood_type": "A-", "language": "English",
     "conditions": ["Type 1 diabetes"], "medications": ["Insulin"], "allergies": ["Peanuts"],
     "notes": "Pediatric — parent not on scene.", "baseline_hr": 95},
]
MCI_TYPES = ["trauma", "cardiac", "trauma", "pediatric"]


@app.route("/")
def patient():
    return send_from_directory("static", "patient.html")


@app.route("/er")
def er_dashboard():
    return send_from_directory("static", "er.html")


@app.route("/ems")
def ems_view():
    return send_from_directory("static", "ems.html")


@app.route("/api/profile", methods=["GET", "POST"])
def profile():
    if request.method == "POST":
        body = request.get_json(silent=True) or {}
        STATE["profile"].update(body)
        save_state()
        return jsonify({"ok": True, "profile": STATE["profile"]})
    return jsonify(STATE["profile"])


@app.route("/api/fhir")
def fhir():
    return jsonify(clinical.fhir_bundle(STATE["profile"]))


@app.route("/api/ers")
def ers():
    lat = float(request.args.get("lat", 42.3601))
    lon = float(request.args.get("lon", -71.0589))
    etype = request.args.get("type", "general")
    ranked, need, chosen, skipped = routing.rank_ers(lat, lon, etype)
    return jsonify({"ers": ranked, "need": need, "chosen": chosen,
                    "skipped_nearer": skipped, "type": etype})


def _open_case(lat, lon, etype, profile_obj, trigger="manual", unresponsive=False):
    ranked, need, chosen, skipped = routing.rank_ers(lat, lon, etype)
    best = chosen or (ranked[0] if ranked else None)
    case_id = uuid.uuid4().hex[:8]
    STATE["active"][case_id] = {
        "case_id": case_id, "created_at": time.time(), "status": "inbound",
        "type": etype, "type_label": routing.EMERGENCY_TYPES.get(etype, {}).get("label", etype),
        "trigger": trigger, "unresponsive": unresponsive,
        "patient_lat": lat, "patient_lon": lon,
        "destination": best,
        "alternatives": [e for e in ranked if best and e["name"] != best["name"]][:3],
        "skipped_nearer": skipped, "profile": dict(profile_obj), "vitals": [],
        "eta_min": best["eta_min"] if best else None,
        "access_log": [{"t": round(time.time(), 1), "who": "PreCheck relay",
                        "action": "record created & shared with " + (best["name"] if best else "ER")}],
    }
    # Simulated next-of-kin notification.
    ec = profile_obj.get("emergency_contact") or {}
    if ec.get("name"):
        log_event("notify", f"Alerted {ec['name']} ({ec.get('phone','')}): "
                            f"{profile_obj.get('name')} triggered SOS, en route to "
                            f"{best['name'] if best else 'nearest ER'}.")
    return case_id, best, skipped, need


@app.route("/api/sos", methods=["POST"])
def sos():
    body = request.get_json(silent=True) or {}
    lat = float(body.get("lat", 42.3601))
    lon = float(body.get("lon", -71.0589))
    etype = body.get("type", "general")
    case_id, best, skipped, need = _open_case(
        lat, lon, etype, STATE["profile"],
        trigger=body.get("trigger", "manual"),
        unresponsive=bool(body.get("unresponsive", False)))
    save_state()
    return jsonify({"ok": True, "case_id": case_id, "destination": best,
                    "alternatives": STATE["active"][case_id]["alternatives"],
                    "skipped_nearer": skipped, "need": need,
                    "patient": {"lat": lat, "lon": lon}})


@app.route("/api/mci", methods=["POST"])
def mci():
    """Spawn several simulated mass-casualty patients near Boston."""
    body = request.get_json(silent=True) or {}
    n = min(int(body.get("count", 4)), len(MCI_PATIENTS))
    ids = []
    for i in range(n):
        prof = {**DEFAULT_PROFILE, **MCI_PATIENTS[i],
                "emergency_contact": {"name": "Listed next-of-kin", "phone": "(617) 555-0000"},
                "insurance": {"provider": "—", "member_id": "—"}}
        lat = 42.35 + random.uniform(-0.03, 0.03)
        lon = -71.06 + random.uniform(-0.03, 0.03)
        cid, best, _, _ = _open_case(lat, lon, MCI_TYPES[i], prof, trigger="mci")
        # seed a few vitals so triage differs across patients immediately
        base = prof["baseline_hr"]
        sev = [10, 48, 30, 20][i]
        for k in range(6):
            STATE["active"][cid]["vitals"].append(
                {"t": time.time() - (6 - k), "hr": base + sev + k * 3,
                 "spo2": max(86, 99 - (sev // 10) - k)})
        ids.append(cid)
    log_event("mci", f"Mass-casualty incident: {n} patients auto-registered & triaged.")
    save_state()
    return jsonify({"ok": True, "spawned": ids})


@app.route("/api/vitals", methods=["POST"])
def vitals():
    body = request.get_json(silent=True) or {}
    case_id = body.get("case_id")
    case = STATE["active"].get(case_id)
    if not case:
        return jsonify({"ok": False, "error": "no such case"}), 404
    case["vitals"].append({"t": round(time.time(), 1),
                           "hr": body.get("hr"), "spo2": body.get("spo2")})
    case["vitals"] = case["vitals"][-180:]
    save_state()
    return jsonify({"ok": True})


def _enrich(c):
    v = c["vitals"][-1] if c["vitals"] else None
    age_s = time.time() - c["created_at"]
    eta_remaining = None
    if c["eta_min"] is not None:
        eta_remaining = max(0.0, round(c["eta_min"] - age_s / 60.0, 1))
    triage = clinical.early_warning(c["vitals"])
    bd = clinical.baseline_delta(v["hr"] if v else None, c["profile"].get("baseline_hr"))
    lang = c["profile"].get("language")
    return {**c, "latest_vital": v, "eta_remaining_min": eta_remaining,
            "triage": triage, "baseline_delta": bd, "sbar": clinical.sbar(c),
            "safety_flags": clinical.safety_flags(c["profile"], c["type"]),
            "reserved_resource": clinical.reserved_resource(c["type"], triage["band"]),
            "deterioration": clinical.project_deterioration(c["vitals"]),
            "localized_lead": clinical.localized_lead(lang),
            "access_log": c.get("access_log", []),
            "vitals": c["vitals"][-80:]}


@app.route("/api/active")
def active():
    # Sort by triage severity (highest early-warning score first), then recency.
    cases = [_enrich(c) for c in STATE["active"].values()]
    cases.sort(key=lambda c: (c["triage"]["score"], c["created_at"]), reverse=True)
    return jsonify({"cases": cases})


@app.route("/api/case/<case_id>")
def case(case_id):
    c = STATE["active"].get(case_id)
    if not c:
        return jsonify({"error": "not found"}), 404
    # Audit/consent trail: record who viewed the record (from ?viewer=).
    viewer = request.args.get("viewer")
    if viewer:
        c.setdefault("access_log", []).append(
            {"t": round(time.time(), 1), "who": viewer, "action": "viewed record"})
        c["access_log"] = c["access_log"][-20:]
        save_state()
    return jsonify(_enrich(c))


@app.route("/api/events")
def events():
    return jsonify({"events": STATE["events"]})


@app.route("/api/handoff/<case_id>")
def handoff(case_id):
    """A read-only, scannable handoff URL + the record (for the QR code)."""
    c = STATE["active"].get(case_id)
    if not c:
        return jsonify({"error": "not found"}), 404
    base = request.host_url.rstrip("/")
    return jsonify({"url": f"{base}/api/case/{case_id}?viewer=QR%20scan",
                    "case_id": case_id})


@app.route("/api/resolve", methods=["POST"])
def resolve():
    body = request.get_json(silent=True) or {}
    case_id = body.get("case_id")
    if case_id in STATE["active"]:
        if body.get("delete"):
            STATE["active"].pop(case_id, None)
        else:
            STATE["active"][case_id]["status"] = "arrived"
        save_state()
    return jsonify({"ok": True})


if __name__ == "__main__":
    # 5080 is a Chrome-safe port (avoids ERR_UNSAFE_PORT like 5060).
    port = int(os.environ.get("PORT", "5080"))
    app.run(host="127.0.0.1", port=port, debug=True)
