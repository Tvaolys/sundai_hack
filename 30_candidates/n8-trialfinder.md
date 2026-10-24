# n8-trialfinder — Plain-language, distance-aware MA clinical-trial finder
Track: Healthcare & biotech (Making Clinical Research More Accessible) | Scores: I3 F4 N3 | Gates passed: 1,2,3,4,5,6
Problem: The official challenge says patients and referring clinicians struggle to find trials and that "eligibility information can be technical, and access may differ by language, geography, and transportation." ClinicalTrials.gov is searchable but eligibility text is dense; patients outside academic hubs lack a plain-language, distance-aware, equity-aware view.
Evidence:
- Challenge text (official portal, extracted 2026-10-24): verified.
- ClinicalTrials.gov v2 API, MA + RECRUITING filter, LIVE — returns NCTId, BriefTitle, Condition, Phase: curl-verified 2026-10-24.
- MassGIS EJ2020 LIVE (outreach-harder areas) + Western MA acute hospitals ArcGIS LIVE (geography/sites) + HRSA shortage areas: curl-verified / provided.
Demo moment: "Type-2 diabetes near Springfield" → 3 recruiting MA trials rewritten in plain language (what it tests, who qualifies in one line, where, travel distance), each flagged if the site sits far from a care-shortage area. Discovery only — no eligibility verdict, no advice.
Build plan (09:00–20:00):
- 09:00 spec: define the plain-language template (condition, 1-line eligibility gist, site, distance) and the SAFETY boundary (no eligibility determination, no medical advice).
- 10:00 CS×2: ClinicalTrials.gov v2 query + parse; CS×1: geocode sites + distance-from-input; CS×1: results UI + EJ/shortage overlay.
- 13:00 tester: verify every rendered trial matches its NCTId record; confirm no invented eligibility.
- 15:00 add language-of-materials note + "far from you" travel flag.
- 16:30 demo-builder: one condition + one city story; 18:00 FREEZE cached query.
Agent plan: Agent builds query/parse/geocode/UI; humans own the plain-language template and the safety boundary. All free public APIs, laptop-only.
Risks & fallback: (1) LLM paraphrase could distort eligibility → always link the raw NCTId record; label as a summary, not advice (Gate 5, SAFE). (2) Geocoding gaps → cache geocodes for demo cities. Fallback: cached query result set for one condition.
Why it matters: Makes real, currently-recruiting MA research findable and legible to patients and community clinicians who can't parse protocol text — exactly the access gap the challenge names, on the live trial feed, with clinical decisions left to professionals.
