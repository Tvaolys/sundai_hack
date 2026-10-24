# Round 3 — Re-gating against CORRECTED tracks + sharpened frame (2026-10-24)

## What changed
1. **True tracks** (from official data portal, extracted from the Vercel SPA bundle):
   Civic action · Robotics & hardware · Energy & climate tech · Healthcare & biotech.
   There is **no Education track** (maps to Civic) and **no standalone Energy track**
   (it is "Energy & climate tech" — climate resilience, ocean, blue economy are in scope).
2. **Sharpened selection frame** (human steer, 2026-10-24): optimize for *real-world
   problems that real people/organizations actually have and that others are not
   adequately solving* — NOT for a single namable individual's forum post. This:
   - relaxes old Gate 1 ("≥1 dated first-person trace") → evidence can be a government
     program, a documented structural gap, or an official dataset's existence;
   - relaxes old Gate 3 ("3+ competitors = kill") → "underserved" now means *poorly*
     served, not only *un*served; crowding is a caution, not an auto-kill;
   - ADDS an implicit gate for THIS event: **uses the official MA data portal** and
     **maps to a named challenge**. A grounded prototype on provided data beats a
     greenfield cow-story that touches none of it.

## Portal endpoint spot-checks (trust boundary)
- MBTA v3 API (routes/alerts/stations): **LIVE**, real JSON. verified 2026-10-24.
- MassGIS EJ2020 ArcGIS query: **LIVE**, returns MUNICIPALITY/PCT_MINORITY/LIMENGHHPCT. verified.
- Western MA hospitals ArcGIS (ICU/beds): **LIVE**. verified.
- ClinicalTrials.gov v2 MA RECRUITING: **LIVE**, returns NCTId/title/condition/phase. verified.
- NBI MA bridges (fhwa MA22.txt): **LIVE**, real delimited file with condition columns. verified.
- Boston 311 / data.boston.gov CKAN: **Cloudflare bot-wall on server-side curl.**
  Works from a browser; a client-side fetch or the datastore_search_sql endpoint is the
  safe path. FEASIBILITY NOTE for any 311/permits/BERDO idea: do the fetch client-side
  or cache a slice tonight. verified-blocked.
- eMOLT ERDDAP csv: returned **empty** for the sampled Aug-2024 window — TONIGHT-VERIFY a
  working date range / mirror before committing an ocean-temp demo to it.

## Re-gate verdicts on existing candidates

| slug | old track | NEW track | verdict under sharpened frame |
|---|---|---|---|
| r10-massave-rebates | Energy | Energy & climate tech | **DOWNGRADE from #1.** Real problem, but uses ZERO portal data and competes with existing rebate-filing SaaS (Resolv/Instafill/Homewise). In a data-portal hackathon this is a structural weakness. Keep as a parked fallback, not a lead. |
| sc2-mabill | Energy | Energy & climate tech | **KEEP, strengthen.** Real documented harm ($87.4M FY2025 AGO overpayment). Can now be *grounded* in portal data: Electric-utility-by-town (351 rows), Mass Save data, ISO-NE price context. Was a thin "paste-a-bill" demo; becomes a data-grounded explainer. |
| sc7-mapermits | Energy | Civic action (Citizen-Friendly Digital Gov / Simplified public services) | **RE-TRACK + KEEP.** Permitting friction is explicitly a Civic challenge ("simpler permitting and application processes"). Can ground in Boston permits SQL dataset. Stronger as Civic than as Energy. |
| sc1-berdo-prep | Energy | Energy & climate tech (Cleaner, more affordable buildings) | **KEEP as grounded.** Now has a real portal dataset: Boston BERDO 2021 reporting (EUI/GHG by property). Was institutional-trace-only; the dataset rescues it. |
| sc6-protocolscale | Education | (no good fit) | **KILL.** No Education track; doesn't fit Civic (not a community/gov problem), Health-biotech (it's teaching logistics, not care/research), or any challenge. Uses no portal data. |
| s4ref-chemval | Biotech | Healthcare & biotech (Accelerating Biotechnology Innovation) | **PARK, low.** Fits track, but human already judged audience too narrow; uses no portal data (ChEMBL/PubChem exist but tangential). Bottom-of-list fallback only. |
| s6-evalreport | Education | (no fit) | **STAYS KILLED.** No Education track; crowding confirmed. |
| sc8-caption-qa | Education | (weak Civic) | **STAYS KILLED.** 3Play/Verbit serve 2,000+ universities. |
| r1-frc-mentor | Robotics | Robotics & hardware | **DOWNGRADE.** Real recurring pain, but (a) uses no portal data, (b) the Robotics track here is clearly about *physical AI / automation / sim / inspection* (see challenge contexts), not youth-team logistics. Off-theme for this track's intent. Park. |
| r2-frc-inspect | Robotics | Robotics & hardware | **DOWNGRADE/park.** Same: off-theme vs the track's physical-AI intent; FIRST is incumbent. |

## Net effect
The old top-3 (Mass Save, FRC mentor, FRC inspect) all **drop out of contention** under
the corrected tracks + "use the portal" expectation. Survivors worth carrying: sc2-mabill,
sc7-mapermits (re-tracked to Civic), sc1-berdo-prep — all re-grounded in portal data.
The real opportunity is NEW, data-grounded ideas in the under-targeted tracks (Civic,
climate-resilience, ocean) and the physical-AI robotics challenges. See round3-newideas.md.
