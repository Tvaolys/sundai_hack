# 40_shortlist.md — ranked top 5 (Round 3, corrected tracks, 2026-10-24)

## What this round changed (read first)
The official site is a **data portal**: 4 tracks (Civic action · Robotics & hardware ·
Energy & climate tech · Healthcare & biotech), 19 named challenges, and **166 provided
datasets/resources**. Earlier rounds used wrong tracks (there is no Education or standalone
Energy track) and — critically — ignored the portal entirely. In a data-portal hackathon,
visible honest use of the PROVIDED data + a crisp demo + challenge fit outweighs
competitor-free novelty. Per the human's steer, we optimize for **real-world problems that
real people/orgs actually have and others under-solve**, not single-person cow stories.

Old top-3 (Mass Save rebates, FRC mentor, FRC inspect) all **dropped**: they use zero
portal data and/or sit outside the robotics track's physical-AI intent. New shortlist is
built from the portal up and spans all four tracks. Ranking incorporates an independent
skeptical audit (recorded in 90_log.md). Dropped-but-kept: N4 climate-brief folded into N2.

Portal endpoints marked LIVE were curl-verified 2026-10-24. data.boston.gov is
Cloudflare-walled server-side → fetch client-side or cache a slice tonight.

---

## 1. n1-311triage — Boston 311 repeat-report & SLA-miss finder, with equity overlay
**Track:** Civic action (More Responsive Neighborhood Services / 311) · **I4 F4 N4**
Why #1: strongest data-groundedness of the set — uses the exact challenge-named columns
(`on_time`, `ward`, `neighborhood`, `service_name`) plus a real EJ2020 join (LIVE). The
challenge text itself names this pain ("repeated reports… hard to recognize patterns").
**Demo:** neighborhood → map of open vs SLA-missed cases, top-3 chronic categories,
duplicate reports collapsed to one hot-spot, EJ overlay showing misses skew to a
limited-English block group.
**Must-do tonight:** cache a 311 slice (Cloudflare blocks server-side curl) and pick the
neighborhood that actually shows the pattern; normalize SLA-miss by report volume so the
equity headline is real, not an artifact of volume. Full card: 30_candidates/n1-311triage.md

## 2. n6-bridgetriage — Bridge maintenance triage from MA NBI data (+ optional defect vision)
**Track:** Robotics & hardware (Safer Inspection of Critical Infrastructure) · **I3 F4 N4**
Why #2: matches the challenge's own words — MassDOT already flies drones, so "the bottleneck
has moved from capture to interpretation." Cleanest pipeline: NBI MA22.txt is a static file
(LIVE, no Cloudflare/CORS risk). Real DOT-asset-manager problem.
**Demo:** load MA NBI → ranked maintenance list, each rank explained by its deck/
superstructure/substructure rating; click a bridge → sample inspection photo with a
crack/corrosion flag (defect dataset, CPU inference on a few images).
**Must-do:** freeze a human-verified NBI column-decoding table (items 58/59/60) in the repo
and SHOW it — turns the biggest risk into credibility. Frame as a maintenance aid, not a
safety verdict. Full card: 30_candidates/n6-bridgetriage.md

## 3. n7-pathplanner — "Which path planner should I use?" visual classifier (insurance pick)
**Track:** Robotics & hardware (Path Planning Classifier) · **I3 F5 N4**
Why #3: highest feasibility (pure Python, offline, no GPU, no API) and answers the challenge
verbatim. Can't-fail insurance if a data-dependent idea stalls. Weakness: least MA-specific
and nearest to a student exercise — mitigated by running a multi-map matrix (real decision
boundary) and wiring the actual Boston street-centerline graph for one MA routing scenario.
**Demo:** pick a map + start/goal → A*/Dijkstra/RRT/PRM race side by side (path length,
nodes expanded, runtime); classifier recommends one with a reason; then the same on a real
Boston street graph. Full card: 30_candidates/n7-pathplanner.md

## 4. n2-emready — "Who gets missed" emergency-readiness outreach priority list
**Track:** Civic action (Stronger Community Emergency Readiness) · **I4 F4 N4**
Why #4: strong equity story on LIVE data (EJ2020 + OpenFEMA + NOAA tide). Absorbs the
coastal-flood + EJ core of the cut N4 climate-brief. The challenge names the "vulnerable
populations hardest to reach" gap directly.
**Demo:** coastal-flood advisory (tide gauge threshold) → ranked EJ block groups in
flood-adjacent towns by limited-English % + income, languages to cover, state hazard
context; plus a historical-FEMA-event replay mode as the reliable fallback.
**Safety:** outputs a prioritized outreach LIST for a human — it does NOT auto-author alert
text (liability). Full card: 30_candidates/n2-emready.md

## 5. n8-trialfinder — Plain-language, distance-aware MA clinical-trial finder
**Track:** Healthcare & biotech (Making Clinical Research More Accessible) · **I3 F4 N3**
Why #5: gives the shortlist all-four-track coverage; clean, safe, LIVE-data build on the
ClinicalTrials.gov v2 MA recruiting feed (verified). The challenge names the access gap.
**Demo:** "Type-2 diabetes near Springfield" → 3 recruiting MA trials in plain language
(what it tests, 1-line eligibility gist, site, travel distance), flagged if far from a
care-shortage area. Discovery only.
**Safety:** no eligibility determination, no medical advice; every summary links its raw
NCTId record (Gate 5). Full card: 30_candidates/n8-trialfinder.md

---

## Parked / carried (grounded fallbacks, not shortlisted)
- **n4-climatebrief** (Energy & climate tech): best problem, worst feasibility-to-ambition
  (4+ integrations + geography join + a composite score it must neuter to stay honest).
  Core folded into n2. Resurrect only if the team wants a climate-track entry and cuts to
  ONE hazard (coastal flood) done well.
- **sc2-mabill** (Energy & climate tech): real documented harm ($87.4M FY2025 AGO
  overpayment); re-ground in Electric-utility-by-town + Mass Save data + ISO-NE for a
  data-portal-credible version. Solid backup.
- **sc7-mapermits** → re-tracked to **Civic (Citizen-Friendly Digital Government)**; reuse
  the named-installer permitting traces; ground in Boston permits dataset.
- **sc1-berdo-prep** (Energy & climate tech): now has the Boston BERDO 2021 dataset to
  ground it.

## Open questions for the human
1. Tonight: cache a Boston 311 slice and confirm the neighborhood that actually shows a
   repeat/SLA/equity pattern (Cloudflare blocks server-side pulls).
2. For n6: is a CPU defect-vision model fast/reliable enough on a few sample images, or do
   we ship tabular-only? (Tabular alone is a complete demo.)
3. For n7: is the multi-map matrix + Boston-street-graph scenario enough to make the
   "classifier" more than a lookup table? Confirm PythonRobotics installs clean on laptops.
4. eMOLT ERDDAP returned empty for the sampled window — only relevant if an ocean idea is
   revived; verify a working date range first.
5. Track strategy: the shortlist spans all 4 tracks. Does the team want to concentrate on
   one track (Civic is widest-open with n1+n2) or hedge across tracks?
