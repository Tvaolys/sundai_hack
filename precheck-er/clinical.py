"""
clinical.py — a simplified early-warning score + FHIR-shaped intake.

early_warning(): a lightweight, NEWS-inspired deterioration signal from the two
vitals we stream (heart rate + SpO2) plus trend. This is a SIMPLIFIED demo
score, NOT the validated NEWS2 (which also uses respiratory rate, temperature,
consciousness, BP, and supplemental-oxygen status). It exists to turn passive
monitoring into an actionable "stable / watch / critical" flag on the ER board.

fhir_bundle(): shapes the patient profile as a minimal FHIR R4 bundle
(Patient + AllergyIntolerance + MedicationStatement + Condition), which is the
standard hospital EHRs speak — demonstrating a real integration boundary.
"""


def _hr_points(hr):
    # NEWS-inspired heart-rate bands (points rise as HR departs normal).
    if hr is None:
        return 0
    if hr <= 40:
        return 3
    if hr <= 50:
        return 1
    if hr <= 90:
        return 0
    if hr <= 110:
        return 1
    if hr <= 130:
        return 2
    return 3


def _spo2_points(spo2):
    if spo2 is None:
        return 0
    if spo2 >= 96:
        return 0
    if spo2 >= 94:
        return 1
    if spo2 >= 92:
        return 2
    return 3


def early_warning(vitals):
    """
    vitals: list of {t, hr, spo2}. Returns a dict with score, band, trend.
    """
    if not vitals:
        return {"score": 0, "band": "unknown", "trend": "flat", "detail": "no vitals yet"}

    latest = vitals[-1]
    score = _hr_points(latest.get("hr")) + _spo2_points(latest.get("spo2"))

    # Trend over the last ~15 samples using HR slope.
    window = [v["hr"] for v in vitals[-15:] if v.get("hr") is not None]
    trend = "flat"
    if len(window) >= 4:
        delta = window[-1] - window[0]
        if delta >= 12:
            trend = "rising"
        elif delta <= -12:
            trend = "falling"

    if score >= 5:
        band = "critical"
    elif score >= 3:
        band = "watch"
    else:
        band = "stable"

    # A rising trend bumps a 'stable' patient to 'watch'.
    if band == "stable" and trend == "rising":
        band = "watch"

    detail = f"HR {latest.get('hr')} / SpO2 {latest.get('spo2')} · trend {trend}"
    return {"score": score, "band": band, "trend": trend, "detail": detail}


def fhir_bundle(profile):
    """Minimal FHIR R4 bundle from the demo profile (not exhaustive)."""
    entries = []

    patient = {
        "resourceType": "Patient",
        "id": "precheck-demo",
        "name": [{"text": profile.get("name")}],
        "gender": {"F": "female", "M": "male"}.get(profile.get("sex"), "unknown"),
        "birthDate": profile.get("dob"),
    }
    lang = profile.get("language")
    if lang:
        patient["communication"] = [{
            "language": {"text": lang},
            "preferred": True,
        }]
    entries.append({"resource": patient})

    for allergy in profile.get("allergies", []):
        entries.append({"resource": {
            "resourceType": "AllergyIntolerance",
            "patient": {"reference": "Patient/precheck-demo"},
            "code": {"text": allergy},
            "criticality": "high",
        }})

    for med in profile.get("medications", []):
        entries.append({"resource": {
            "resourceType": "MedicationStatement",
            "subject": {"reference": "Patient/precheck-demo"},
            "status": "active",
            "medicationCodeableConcept": {"text": med},
        }})

    for cond in profile.get("conditions", []):
        entries.append({"resource": {
            "resourceType": "Condition",
            "subject": {"reference": "Patient/precheck-demo"},
            "clinicalStatus": {"coding": [{"code": "active"}]},
            "code": {"text": cond},
        }})

    return {"resourceType": "Bundle", "type": "collection", "entry": entries}


def baseline_delta(latest_hr, baseline_hr):
    """How far the current HR is from the patient's stored resting baseline."""
    if latest_hr is None or not baseline_hr:
        return None
    delta = latest_hr - baseline_hr
    return {
        "delta": round(delta),
        "baseline": baseline_hr,
        "text": (f"{abs(round(delta))} bpm {'above' if delta > 0 else 'below'} "
                 f"their resting baseline ({baseline_hr})") if abs(delta) >= 8 else
                f"near their resting baseline ({baseline_hr})",
        "elevated": delta >= 20,
    }


def sbar(case):
    """
    Generate a plain-language SBAR handoff note (Situation, Background,
    Assessment, Recommendation) from the case. This is a template-based
    summary for the ER/EMS — a quick read, not a clinical decision.
    """
    p = case.get("profile", {})
    v = case.get("vitals", [])
    latest = v[-1] if v else {}
    triage = early_warning(v)
    etype = case.get("type_label", "emergency")
    name = p.get("name", "Unknown patient")
    age = p.get("age", "?")
    sex = p.get("sex", "")
    eta = case.get("eta_remaining_min")

    conditions = ", ".join(p.get("conditions", [])) or "none on file"
    meds = ", ".join(p.get("medications", [])) or "none on file"
    allergies = ", ".join(p.get("allergies", [])) or "NKDA"

    hr = latest.get("hr")
    spo2 = latest.get("spo2")
    bd = baseline_delta(hr, p.get("baseline_hr"))

    situation = (f"{name}, {age}{('/' + sex) if sex else ''}, inbound with "
                 f"{etype.lower()}"
                 + (", unresponsive" if case.get("unresponsive") else "")
                 + (f". ETA ~{eta} min." if eta is not None else "."))

    background = (f"History: {conditions}. Current meds: {meds}. "
                  f"Allergies: {allergies}."
                  + (f" Preferred language: {p['language']} — interpreter advised."
                     if p.get("language") and p["language"].lower() != "english" else ""))

    assess_bits = []
    if hr is not None:
        assess_bits.append(f"HR {hr}")
    if spo2 is not None:
        assess_bits.append(f"SpO2 {spo2}%")
    assess = ("Vitals: " + ", ".join(assess_bits) + ". " if assess_bits else "")
    assess += f"Early-warning: {triage['band'].upper()} (score {triage['score']}, trend {triage['trend']})."
    if bd and bd.get("elevated"):
        assess += f" HR is {bd['text']}."

    rec_map = {
        "stroke": "Activate stroke pathway; confirm last-known-well; CT on arrival.",
        "cardiac": "Prep for ACS workup; 12-lead ECG and troponin on arrival.",
        "trauma": "Activate trauma team; prepare trauma bay.",
        "burn": "Notify burn unit; estimate TBSA on arrival.",
        "pediatric": "Notify pediatric team.",
        "general": "Standard ED intake; reassess on arrival.",
    }
    recommendation = rec_map.get(case.get("type"), rec_map["general"])
    if triage["band"] == "critical":
        recommendation = "Resuscitation bay on standby. " + recommendation

    return {
        "situation": situation,
        "background": background,
        "assessment": assess,
        "recommendation": recommendation,
    }


# ---------------------------------------------------------------------------
# Clinical safety checks: meds/allergies vs the emergency + likely treatment.
# This is a small, transparent demo rule set — NOT a validated interaction
# engine (real systems use RxNorm + a licensed interaction database). It exists
# to surface the kind of "stop and check" flags an ER would want up front.
# ---------------------------------------------------------------------------

def _has(items, *needles):
    low = [str(i).lower() for i in (items or [])]
    return any(any(n in i for n in needles) for i in low)


def safety_flags(profile, etype):
    meds = profile.get("medications", [])
    allergies = profile.get("allergies", [])
    conditions = profile.get("conditions", [])
    flags = []

    # Anticoagulants + trauma/stroke -> bleeding risk.
    if _has(meds, "warfarin", "coumadin", "apixaban", "eliquis", "rivaroxaban",
            "xarelto", "dabigatran", "heparin", "clopidogrel", "plavix"):
        if etype in ("trauma", "stroke"):
            flags.append({"level": "high", "text":
                "On anticoagulant/antiplatelet — elevated bleeding risk; check INR, "
                "avoid tPA until hemorrhage ruled out."})
        else:
            flags.append({"level": "info", "text": "On blood thinner — note for any procedure."})

    # Penicillin allergy -> avoid common beta-lactams.
    if _has(allergies, "penicillin", "amoxicillin", "beta-lactam"):
        flags.append({"level": "med", "text":
            "Penicillin allergy on file — avoid beta-lactam antibiotics; use alternative."})

    # Contrast/shellfish historically flagged for CT-with-contrast caution.
    if _has(allergies, "shellfish", "iodine", "contrast") and etype in ("stroke", "trauma"):
        flags.append({"level": "med", "text":
            "Contrast-sensitivity history — flag before CT-with-contrast."})

    # Metformin + contrast imaging caution.
    if _has(meds, "metformin") and etype in ("stroke", "trauma"):
        flags.append({"level": "info", "text":
            "On metformin — hold around iodinated contrast per protocol."})

    # Pacemaker/implant note for cardiac.
    if _has(conditions, "pacemaker") or _has([profile.get("notes", "")], "pacemaker"):
        if etype == "cardiac":
            flags.append({"level": "info", "text":
                "Pacemaker present — consider for ECG interpretation & defibrillation pad placement."})

    # Beta-blocker may blunt tachycardia (masks severity).
    if _has(meds, "metoprolol", "atenolol", "carvedilol", "bisoprolol"):
        flags.append({"level": "info", "text":
            "On beta-blocker — heart rate may under-represent physiologic stress."})

    return flags


# Which ER resource each emergency should reserve.
RESOURCE_FOR = {
    "stroke": "Stroke CT + neuro team",
    "cardiac": "Cath lab + cardiology",
    "trauma": "Trauma bay (surgery on standby)",
    "burn": "Burn unit",
    "pediatric": "Pediatric team + peds bay",
    "general": "General ED bay",
}


def reserved_resource(etype, triage_band):
    base = RESOURCE_FOR.get(etype, RESOURCE_FOR["general"])
    if triage_band == "critical":
        return base + " · priority hold"
    return base


def project_deterioration(vitals):
    """
    Very simple linear projection of the early-warning trend. Returns a short
    forecast string. Clearly a demo heuristic, not a predictive model.
    """
    if len(vitals) < 5:
        return None
    hrs = [v["hr"] for v in vitals[-8:] if v.get("hr") is not None]
    if len(hrs) < 4:
        return None
    slope = (hrs[-1] - hrs[0]) / max(1, len(hrs) - 1)  # bpm per sample
    if slope >= 3:
        # rough time until HR crosses ~140 (a critical-ish threshold)
        gap = 140 - hrs[-1]
        if gap <= 0:
            return "already in critical HR range"
        mins = round((gap / slope) / 60.0 + 0.1, 1)
        return f"trending up ~{round(slope,1)} bpm/s — may reach critical HR in ~{mins} min"
    if slope <= -3:
        return "improving — HR trending down"
    return "stable trend"


# A tiny phrasebook so the SBAR's lead line can appear in the patient's
# preferred language (demo coverage only).
SBAR_LEAD = {
    "Spanish": "Paciente entrante — perfil e historial precargados.",
    "Portuguese": "Paciente a caminho — perfil e histórico pré-preenchidos.",
    "Mandarin": "患者即将到达 — 病历已预先填写。",
    "Haitian Creole": "Pasyan ap vini — pwofil ak istwa pre-ranpli.",
    "Vietnamese": "Bệnh nhân đang đến — hồ sơ đã được điền sẵn.",
}


def localized_lead(language):
    return SBAR_LEAD.get(language)
