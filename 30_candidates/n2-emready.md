# n2-emready — "Who gets missed" emergency-readiness outreach planner
Track: Civic action (Stronger Community Emergency Readiness) | Scores: I4 F4 N4 | Gates passed: 1,2,3,4,5,6
Problem: The official challenge warns "vulnerable populations can be hardest to reach" when severe weather hits and info changes fast. State ResilientMass plans are statewide; small-town emergency managers and community orgs lack a block-group-level "who needs door-knock outreach, and in which languages" planner for a specific event.
Evidence:
- Challenge text (official portal, extracted 2026-10-24): verified.
- OpenFEMA DisasterDeclarationsSummaries MA LIVE (declarationTitle/Date/incidentType): curl-verified 2026-10-24.
- EJ2020 ArcGIS LIVE (PCT_MINORITY, LIMENGHHPCT, BG_MHHI): curl-verified 2026-10-24.
- NOAA Boston tide gauge LIVE (coastal-flood trigger) + CDC SVI: verified / provided.
Demo moment: Simulate a coastal-flood advisory (tide gauge crosses a threshold) → the tool lists the specific EJ block groups in flood-adjacent towns, ranked by limited-English % and median income, names the languages outreach must cover, and shows the state-assessment hazard ranking for context. (It presents WHO to reach and HOW MANY — it does not author the alert.)
Build plan (09:00–20:00):
- 09:00 spec: define the trigger (tide/forecast threshold) and the reach-priority rule (LIMENGHHPCT, BG_MHHI, CDC SVI → rank), normalized by block-group population.
- 10:00 CS×2: EJ2020 + OpenFEMA + NOAA tide adapters; CS×1: map + ranked outreach list UI; CS×1: historical-event mode (pick a past MA FEMA declaration → who was most exposed).
- 13:00 tester: verify block-group ranks trace to real rows; confirm no composite black-box score.
- 15:00 add the MA Climate Change Assessment hazard context per event type (curated table from the public doc).
- 16:30 demo-builder: coastal-town flood story + historical-event replay; 18:00 FREEZE cached responses.
Agent plan: Agent builds adapters, map, ranked list; humans own the priority rule and the curated hazard-context table. Free public APIs, laptop-only.
Risks & fallback: (1) DO NOT generate official-looking alert text (liability) — the tool outputs a prioritized outreach list for a human to act on, not a message to send (Gate 5). (2) Live tide trigger flaky → historical-event mode is the reliable fallback demo. (3) "Skew" may be volume not inequity → normalize per capita and show the raw block-group numbers.
Why it matters: Converts a statewide resilience mandate into an actionable, equity-first outreach priority list at the neighborhood scale small EM offices operate in — the reach gap the challenge names — with zero liability from auto-authoring emergency messaging.
