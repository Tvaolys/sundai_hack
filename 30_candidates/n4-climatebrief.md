# n4-climatebrief — Neighborhood climate-risk + equity brief for MA towns
Track: Energy & climate tech (Resilient communities in a changing climate) | Scores: I4 F3 N4 | Gates passed: 1,2,3,4,5,6
Problem: The official challenge says "risks differ by neighborhood… making it hard for communities to prioritize preparedness investments." The MA Climate Change Assessment ranks hazards statewide but lives in a PDF; no tool turns it into a one-screen "your neighborhood's top climate risks + who's most exposed here" brief that fuses hazard, live conditions, and equity.
Evidence:
- Challenge text (official portal, extracted 2026-10-24): verified.
- EJ2020 ArcGIS LIVE (PCT_MINORITY, LIMENGHHPCT, BG_MHHI): curl-verified 2026-10-24.
- NOAA Boston tide gauge API LIVE (hourly water level, station 8443970): curl-verified 2026-10-24.
- USGS Charles River flow + CDC PLACES (heat-health) + MA Climate Change Assessment + ResilientMass: provided portal resources (verified in registry; PLACES SODA pattern verified earlier).
Demo moment: Enter a town → "Top risks: coastal flooding (tide-gauge trend), extreme heat (PLACES burden); most-exposed block groups (EJ, ranked by limited-English %); one preparedness action the state assessment recommends for this hazard." Every figure source-linked.
Build plan (09:00–20:00):
- 09:00 spec (math grad): define the risk-scoring rule per hazard (what each dataset contributes, how combined, honest about weighting).
- 10:00 CS×2: data adapters (tide gauge, USGS, PLACES, EJ2020); CS×1: brief UI (town picker → one-screen card); CS×1: source-citation pane (every number links its dataset).
- 13:00 tester: verify each number traces to a real response; chem/math review the scoring.
- 15:00 add the assessment-recommended action lookup per hazard (curated table from the public doc).
- 16:30 demo-builder: pick a coastal town (strong flood story) + an inland town (heat); 18:00 FREEZE with cached responses.
Agent plan: Agent builds adapters + UI; humans own the scoring rule honesty and the curated action table. All free public APIs, laptop-only.
Risks & fallback: (1) Over-combining datasets into a fake "risk score" → keep hazards separate, cite each, avoid a single black-box number. (2) eMOLT/ocean endpoints flaky → rely on verified tide gauge + USGS + EJ. Fallback: 2 cached town briefs.
Why it matters: Gives small towns and residents a plain, source-honest preparedness brief at the neighborhood scale the state assessment can't resolve to — directly serving the challenge's prioritization gap.
