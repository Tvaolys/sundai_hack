# Round 3 — New data-grounded hypotheses (2026-10-24)

Frame: real-world problems real people/orgs have that others under-solve, mapped to a
named challenge, grounded in the official MA data portal, buildable in 11h on laptops.
Portal endpoints marked LIVE were curl-verified today; "client-side" = Cloudflare-walled
on server curl but fine from a browser app.

---

## N1 [Civic — More Responsive Neighborhood Services (311)] Repeat-report & SLA-miss finder for Boston 311
**Real-world problem.** Cities get huge volumes of 311 reports; the challenge text itself
says "high volumes and repeated reports make it hard to recognize patterns, prioritize
action, and communicate progress." Duplicate reports for the same pothole/streetlight
inflate counts and bury chronic issues; residents can't tell if their report is one of
many or if an area is chronically missed.
**Who has it / why under-solved.** City ops staff + residents. Generic 311 dashboards show
volume; they rarely cluster duplicates spatially or flag which categories blow past the
`on_time` SLA in which wards. The portal field set includes `on_time`, `case_status`,
`neighborhood`, `service_name`, `ward` — exactly the columns needed, and nobody ships this
as a resident-facing "is my block chronically ignored?" view.
**Data (LIVE / client-side).** Boston 311 datastore resource_id 254adca6… (fields:
open_date, case_topic, service_name, assigned_department, case_status, neighborhood,
zip_code, on_time, city_council_district, ward). EJ2020 (LIVE) for equity overlay:
are SLA misses concentrated in high-minority / limited-English block groups?
**Confidence.** Challenge text verified (portal). Dataset schema verified (portal + the
field list). 311-is-noisy is a documented civic-tech truism (plausible). 311 endpoint is
Cloudflare-walled server-side → fetch client-side or cache a slice tonight (verified-blocked).
**Demo moment.** Pick a neighborhood → map of open vs on-time-missed cases, top 3 chronic
categories, and a spatial cluster of duplicate pothole reports collapsed into one "hot spot,"
with an EJ overlay showing the misses skew to a limited-English block group.

## N2 [Civic — Stronger Community Emergency Readiness] Who-gets-missed outreach planner
**Real-world problem.** Challenge text: "vulnerable populations can be hardest to reach"
in emergencies; info changes fast. MA has a real disaster history (OpenFEMA) and known
social-vulnerability geography (EJ2020, CDC SVI).
**Who / why under-solved.** Municipal emergency managers + community orgs. ResilientMass
plans exist at the state level, but a *block-group-level* "if a heat/flood event hits here,
which limited-English or low-income areas need door-knock outreach, and in which languages"
planner is not a thing residents or small-town EM offices have.
**Data (LIVE).** OpenFEMA DisasterDeclarationsSummaries MA (LIVE — verified: returns
declarationTitle/Date/incidentType). EJ2020 (LIVE: PCT_MINORITY, LIMENGHHPCT, BG_MHHI).
CDC SVI. NOAA Boston tide gauge (LIVE) / buoy 44013 for a live coastal-flood trigger.
**Confidence.** All endpoints verified LIVE today. Vulnerability-reach gap is documented
in emergency-management literature (plausible).
**Demo moment.** Simulate a coastal-flood advisory (tide gauge crosses threshold) →
the tool lists the specific EJ block groups in the inundation-adjacent towns, ranked by
limited-English %, with the languages to prioritize and an auto-drafted multilingual alert.

## N3 [Civic — Citizen-Friendly Digital Government] Source-grounded permit/application navigator
**Real-world problem.** Challenge text: residents/small businesses face "complex websites,
lengthy PDFs, language barriers, and confusing application processes." (This is the
re-tracked sc7-mapermits, generalized.) Permitting friction is real and MA-documented.
**Who / why under-solved.** Small contractors, homeowners, small businesses. General LLM
chatbots hallucinate civic procedure; the *honest* version grounds every answer in a city
source and says who it is (the portal literally provides the "civic-agents identity & auth"
doc and Boston Open Context for exactly this).
**Data.** Boston permits datastore (worktype/permittypedescr/fees/status — client-side),
Boston Open Context (github CityOfBoston/OpenContext) for source-grounding, civic-agents
identity/auth doc (github projnanda), mass.gov/boston.gov as cited sources.
**Confidence.** Challenge + resources verified (portal). Permit-friction pain carried from
round 1 (sc7: named installers Oct 2025, 351 permit regimes — TRACE, reuse).
**Demo moment.** "I want to add a bedroom in Boston" → step list with the exact permit
types, fees, and the city page each step is quoted from (no invented steps); a "who am I"
banner stating it's an unofficial assistant citing city data.

## N4 [Energy & climate tech — Resilient communities in a changing climate] Neighborhood climate-risk + equity brief
**Real-world problem.** Challenge text: "Risks differ by neighborhood… making it hard for
communities to prioritize preparedness investments." MA Climate Change Assessment ranks
hazards statewide but not at a block a resident recognizes.
**Who / why under-solved.** Town planners, community orgs, residents. The state assessment
is a PDF; nobody turns it into a one-screen "your neighborhood's top 3 climate risks +
who's most exposed here" brief that combines hazard, geography, and EJ.
**Data (LIVE/mixed).** EJ2020 (LIVE), NOAA tide gauge (LIVE) + buoy (coastal flood),
USGS Charles River flow (river flood), CDC PLACES (heat-health burden), MA Climate Change
Assessment + ResilientMass (framing). NOAA Digital Coast (shoreline risk).
**Confidence.** EJ2020/tide/USGS verified LIVE. Assessment/ResilientMass are real state
docs (verified via portal). CDC PLACES endpoint pattern verified earlier.
**Demo moment.** Enter a town → "Top risks: coastal flooding (tide-gauge trend), extreme
heat (PLACES + tree-cover proxy); most-exposed block groups (EJ); one preparedness action
the state assessment recommends for this hazard." Everything source-linked.

## N5 [Energy & climate tech — A more reliable clean energy system] "Who delivers the electrons" siting reality-check
**Real-world problem.** Clean-energy pitches ignore *who actually operates the grid* in a
given town and whether transmission exists nearby. Portal usefulFor literally says: "Before
you promise a cleaner grid, name who actually has to deliver the electrons."
**Who / why under-solved.** Municipal energy committees, student climate projects, siting
advocates. There's no simple tool joining town → utility → nearby transmission → existing
landfill-solar to sanity-check a local clean-energy proposal.
**Data (LIVE).** Electric-utility-by-town (351 rows ArcGIS), Electric transmission lines
(ArcGIS, voltage/owner), Renewables at MA landfills (LIVE — verified), ISO-NE Express
(fuel mix/price context).
**Confidence.** Landfill-renewables + utility-by-town endpoints verified LIVE. Framing is
the portal's own stated intent.
**Demo moment.** Pick a town → "Served by [utility]; nearest transmission is [voltage/owner]
X km away; [n] closed landfills here already host [MW] of solar." Turns a vague 'go green'
claim into a sited, operator-named one.

## N6 [Robotics & hardware — Safer Inspection of Critical Infrastructure] Bridge-condition triage from inspection data (+ optional defect vision)
**Real-world problem.** Challenge text is explicit: MassDOT *already* flies drones; "the
bottleneck has moved from capture to interpretation." Interpreting condition ratings and
images to prioritize maintenance is the real, current gap.
**Who / why under-solved.** DOT asset managers. The NBI file is a wall of coded columns;
turning it into a ranked "which MA bridges need attention and why" list — and (stretch)
flagging defects in a sample image via a defect dataset — is the interpretation layer the
challenge names. Laptop-feasible: it's tabular + a small vision model on sample images.
**Data (LIVE).** NBI MA bridges (fhwa MA22.txt — LIVE, verified: real condition columns),
FHWA InfoBridge/SNBI (schema), dacl10k / CODEBRIM (bridge-defect images on HF, request/slice).
**Confidence.** NBI file verified LIVE today with condition fields. Challenge framing verified.
Defect image sets exist (portal; redistribution caveat noted).
**Demo moment.** Load MA NBI → ranked maintenance list with the deck/superstructure/
substructure rating driving each rank; click a bridge, show a sample inspection photo with
a crack/corrosion flag overlaid (defect-dataset model). Capture→interpretation, demonstrated.

## N7 [Robotics & hardware — Path Planning Classifier] "Which planner should I use?" on a real Boston grid
**Real-world problem.** Challenge text verbatim: "How to choose which path planning
algorithm for your environmental needs and compute resources or other constraints." This
is a genuine recurring question for robotics students/engineers and the portal ships the
exact benchmark asset for it.
**Who / why under-solved.** Robotics learners/practitioners. People reach for A* or RRT by
habit; there's no quick tool that runs several planners on the *same* map and recommends one
by map density / compute budget. The portal provides Boston_0_256 (movingai) and PythonRobotics.
**Data (LIVE/code).** Boston street grid 256 (movingai benchmark zip), Boston street
centerlines (19,440 segs, real geometry — client-side), PythonRobotics (A*/Dijkstra/RRT/PRM).
**Confidence.** movingai Boston benchmark + PythonRobotics are standard, real (portal).
Pure-Python, laptop-only, no GPU — strongest feasibility of any robotics idea.
**Demo moment.** Pick the Boston grid + a start/goal → run A*, Dijkstra, RRT, PRM side by
side; show path length, nodes expanded, runtime; the classifier recommends "use RRT here
because the map is sparse and your compute budget is X." Visual, self-contained, reproducible.

## N8 [Healthcare & biotech — Making Clinical Research More Accessible] Plain-language MA trial finder
**Real-world problem.** Challenge text: patients/clinicians struggle to find trials;
"eligibility information can be technical, and access may differ by language, geography,
transportation." Carried pain is real and MA-specific.
**Who / why under-solved.** Patients + referring clinicians outside academic hubs.
ClinicalTrials.gov is searchable but eligibility text is dense; a plain-language +
distance-from-me + language-aware layer over the MA recruiting feed, with an EJ overlay for
"where outreach must try harder," is not readily available.
**Data (LIVE).** ClinicalTrials.gov v2 MA RECRUITING (LIVE — verified), EJ2020 (LIVE),
Western MA hospitals (LIVE) for geography, HRSA shortage areas.
**Confidence.** Trial API + EJ + hospitals verified LIVE today. Challenge framing verified.
SAFETY: discovery/plain-language only, no eligibility determination, no medical advice (Gate 5).
**Demo moment.** "Type-2 diabetes near Springfield" → 3 recruiting MA trials in plain
language (what it's testing, who qualifies, where, travel distance), flagged if the site is
far from a shortage area. No advice, just findability.

---

## Ranking rationale (pre-shortlist)
Feasibility + data-groundedness + demo clarity + challenge fit + under-solved-ness:
- **Tier 1 (lead):** N7 (path-planning classifier — strongest feasibility, portal ships the
  benchmark, crisp visual demo, exact challenge match), N1 (311 repeat/SLA finder — wide-open
  Civic, rich data, resident-facing demo), N4 (climate-risk+equity brief — untouched climate
  track, multi-dataset, timely).
- **Tier 2:** N6 (bridge triage — exact "capture→interpretation" match; vision is a stretch),
  N2 (emergency-readiness outreach — strong equity story), N8 (trial finder — clean, safe,
  LIVE data).
- **Tier 3 / grounded carries:** N3 (permit navigator — reuses sc7 trace, but agent-grounding
  is the hard part), N5 (grid siting check — neat but niche).

---
## Inspiration pool (NOT gated; idea-stage, added 2026-10-24 on human request)
"data checked" = main dataset curl-fetched today; problem itself not evidence-hunted.
- I1 [Civic] Step-free MBTA route checker — MBTA v3 alerts LIVE: 15 ELEVATOR_CLOSURE alerts on 2026-10-24 (e.g., Aquarium Elevator 914, State Elevator 803). Check: does MBTA trip planner already route around closures? data checked.
- I2 [Robotics: Data Quality] Robot-demo episode linter — DROID-100 LeRobot episode parquet LIVE (138 KB). Flag frame gaps / idle / out-of-range joints. data checked.
- I3 [Robotics: Swarm] Swarm frontier-exploration S&R on movingai street maps (Boston_0/1/2, NewYork, Berlin all LIVE). Risk: textbook-looking. data checked.
- I4 [Health: Coverage] MassHealth renewal-notice decoder on SYNTHETIC notices — WGBH 2026-09-21 (~7,300 lose comprehensive coverage Oct 1). No eligibility decisions. idea only.
- I5 [Health: Access] Western MA specialty-care travel map — hospitals ArcGIS LIVE; licensed beds ≠ live capacity. data checked.
- I6 [Climate: Ocean] eMOLT measured vs NECOFS forecast mismatch — eMOLT LIVE for Jun-2024 window; NetCDF loading is the hard step. data checked.
- I7 [Civic: Digital Gov] Source-citing, self-identifying city-services agent (re-scoped N3). Chatbot-crowding risk. idea only.
- I8 [Climate: Grid] Town clean-energy reality check (= N5). utility-by-town + landfills LIVE. data checked.
