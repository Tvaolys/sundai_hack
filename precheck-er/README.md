# PreCheck ER

**No forms at the door. Your ER intake and live vitals arrive before you do.**
Healthcare & Biotech track · HACKACHUSETTS

When someone is in a medical emergency, the last thing they (or a bystander)
should be doing is filling out clipboards of intake paperwork. PreCheck ER flips
the order: you fill out your medical profile **once**, ahead of time. When you
trigger **SOS** (e.g. Apple Watch fall/crash detection or the SOS button), the
system:

1. Finds the **nearest *appropriate* ER** — a suspected stroke goes to a
   stroke-capable center, major trauma to a trauma center, a burn to a burn unit.
2. Sends your **pre-filled intake** (conditions, meds, allergies, contacts,
   insurance) to that ER's board **before you arrive**.
3. Streams your **live vitals** (heart rate, SpO₂) to the ER so staff can watch
   your condition while help is en route and prep accordingly.

Three screens, one live relay (patient → EMS → ER):
- **Patient app** (`/`) — a simulated phone/watch: your profile, an SOS button,
  **Apple-Watch-style fall auto-SOS** (10s countdown, auto-sends if no response),
  a live heart-rate ring, and a scrolling **ECG-style waveform**.
- **EMS crew view** (`/ems`) — the ambulance crew's enroute screen: destination,
  big ETA, live vitals + ECG, the patient card, and the **SBAR handoff note**.
- **ER board** (`/er`) — the charge nurse's view: a **live map** of the routing
  decision, inbound patients **auto-sorted by triage severity**, countdown ETA,
  live vitals sparkline, **early-warning triage band**, SBAR handoff, baseline-HR
  delta, interpreter/unresponsive flags, an **events feed**, a **Simulate MCI**
  button, and a one-click **FHIR intake** export.

## Features

- **Capability-aware routing, visualized.** The ER map shows the patient, the
  chosen ER (green, with the reason it was picked), and the *nearer ERs the
  router skipped* (grey, each labeled with why — "no stroke designation",
  "on diversion (88% full)").
- **ER capacity / diversion.** Each ER carries a simulated live load; the router
  skips a closer-but-saturated ER and says so.
- **Early-warning triage score.** A simplified, NEWS-inspired deterioration
  signal from HR + SpO₂ + trend, shown as a `stable / watch / critical` band
  that escalates as the patient worsens en route. (Simplified demo score — NOT
  validated NEWS2; see limits.)
- **ECG-style waveform.** A synthetic, HR-driven PQRST trace on the patient app,
  so it reads like a real monitor.
- **Fall auto-SOS.** Simulates Apple Watch fall detection: a 10-second countdown
  that auto-sends (patient marked unresponsive) if the user doesn't cancel.
- **Unresponsive handling.** When the patient can't speak, the pre-filled profile
  is "their voice" — flagged prominently on the ER board.
- **Language / equity flag.** The profile carries a preferred language; the ER
  board raises an "Interpreter: Portuguese" flag, tying into MA's documented
  limited-English access gap.
- **FHIR R4 intake.** The profile is exportable as a FHIR bundle
  (`Patient` + `AllergyIntolerance` + `MedicationStatement` + `Condition`) — the
  real standard hospital EHRs speak. See `/api/fhir`.
- **SBAR handoff note.** Each case auto-generates a Situation / Background /
  Assessment / Recommendation summary (the format nurses actually use to hand
  off a patient) from the profile + vitals + triage. Template-based, not AI, and
  not a clinical determination.
- **Baseline-HR delta.** Live HR is compared to the patient's stored resting
  baseline ("63 bpm above their baseline") — more meaningful than a raw number.
- **EMS crew relay.** A third screen completes the real-world chain: patient →
  ambulance crew → ER, all seeing the same live record.
- **Mass-casualty (MCI) mode.** One click spawns several simulated patients at
  once; the ER board auto-sorts them by early-warning severity so the sickest
  float to the top — exactly when pre-registration matters most.
- **Next-of-kin notification.** On SOS, a simulated alert to the emergency
  contact is logged to the events feed.
- **Durable state.** Active cases persist to `data/state.json`, so a server
  reload/restart never drops an in-flight patient.
- **Clinical safety checks.** Each case cross-references the patient's meds,
  allergies, and conditions against the emergency type and likely treatment, and
  surfaces flags — e.g. "on anticoagulant + trauma → bleeding risk, check INR,
  avoid tPA," "penicillin allergy → avoid beta-lactams," "beta-blocker may mask
  tachycardia." A small, transparent rule set (NOT a validated interaction
  engine; real systems use RxNorm + a licensed database).
- **Resource reservation.** On routing, the ER holds the right resource for the
  emergency (cath lab / trauma bay / stroke CT), with a "priority hold" when the
  patient is critical.
- **Deterioration projection.** A simple linear forecast of the vitals trend
  ("trending up ~6 bpm/s — may reach critical HR in ~2 min"). A demo heuristic,
  not a predictive model.
- **QR handoff.** The patient screen shows a scannable code that opens their
  read-only record — a paper-to-digital bridge for on-scene responders.
- **Access & consent trail.** Every case logs who viewed the record and when
  (PreCheck relay, EMS crew, QR scan) — the privacy/HIPAA-awareness story.
- **Localized SBAR lead.** The handoff's lead line renders in the patient's
  preferred language (demo phrasebook coverage).

## Why the routing is clinically meaningful (not just "nearest building")

PreCheck routes on real MassGIS hospital capability data:

- Suspected **stroke** → nearest **Endovascular / Primary Stroke Service** center
- Major **trauma** → nearest **Level I/II/III trauma** center
- Severe **burn** → nearest hospital with a **burn unit**
- **Pediatric** → nearest peds-ICU / peds-trauma capable ER
- **Cardiac / general** → nearest ER

Verified live: **70 MA emergency departments**, incl. **8 Level I trauma centers**
and **8 endovascular-capable stroke centers**.

## Data source

- **MassGIS `Massachusetts_Hospitals`** filtered to `EMERGENCY_DEPT='Yes'`, with
  `TRAUMA_LEVEL_ADULT`, `TRAUMA_LEVEL_PEDS`, `DPH_STROKE_TIER`, `BURN_UNIT`,
  `PEDIATRIC_ICU`, geolocation, phone, and address.

Rebuild the ER directory from raw data:

```bash
python build_ers.py     # data/raw_ers.json -> data/ers.json
```

## The demo (about 60 seconds)

1. Open the **ER board** (`/er`) in one window and the **patient app** (`/`) in
   another, side by side.
2. On the patient app, pick **Suspected stroke** and hit **SOS**.
3. On the ER board, the patient appears instantly — pre-registered, routed to
   **MGH (endovascular stroke center)**, with ETA counting down and a live heart
   rate climbing. No forms were filled at intake.
4. Switch the type to **Major trauma** on a second SOS to show routing change to
   a **Level I trauma center**.

## Run it

```bash
cd precheck-er
pip install -r requirements.txt
python app.py
# patient app: http://localhost:5080
# ER board:    http://localhost:5080/er
```

## API

| Endpoint | Purpose |
|---|---|
| `GET /api/profile` · `POST /api/profile` | read / update the demo patient profile |
| `GET /api/ers?lat=&lon=&type=` | ranked nearest-appropriate ERs |
| `POST /api/sos` | trigger an emergency → routes + opens a live case |
| `POST /api/vitals` | patient pushes a vitals sample |
| `GET /api/active` | inbound cases + vitals + triage + SBAR (sorted by severity) |
| `GET /api/case/<id>` | one case (EMS crew view) |
| `POST /api/resolve` | mark a case arrived / clear it |
| `POST /api/mci` | spawn N simulated mass-casualty patients |
| `GET /api/events` | recent system events (notify, MCI) |

## Honest limits (read before pitching)

This is a **demo**, and it is built to be truthful about what's real vs.
simulated:

- The **Apple Watch / phone sensor is simulated** in the browser. There is no
  real HealthKit or Watch SOS integration (that needs Apple's native frameworks
  and a device). The architecture is production-shaped; the sensor is mocked.
- **Vitals are synthetic** and scripted to deteriorate during an "event" so the
  ER-side live monitoring is visible. Real vitals would come from the watch.
- **Patients are fictional** and the profile is sample data. This is **not**
  HIPAA-compliant and stores data in-memory only — not for real patient data or
  clinical use.
- ER **routing is real** (live MassGIS capability data) and ETAs are planning
  estimates (straight-line distance + an average ambulance speed), not live
  traffic routing.
- The **early-warning score is a simplified demo signal** (HR + SpO₂ + trend),
  not the validated NEWS2 (which also needs respiratory rate, temperature,
  consciousness, BP, and supplemental-oxygen status). It flags trends for a
  human; it is not a clinical determination.
- **ER load / diversion is simulated** (seeded random occupancy). A real system
  would use a regional bed-availability / EMS diversion feed.
- The **FHIR bundle is a minimal illustration** of the integration boundary, not
  a certified, fully-coded (SNOMED/RxNorm/LOINC) EHR payload.

Future work: real HealthKit/Watch integration, authenticated identity, encrypted
PHI transport, SNOMED/RxNorm-coded FHIR hand-off into hospital EHRs, a live
bed-availability feed, and live traffic-aware ETAs.
