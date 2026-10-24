# sc1-berdo-prep — Self-serve BERDO compliance prep for condo boards and small landlords
Track: Energy | Scores: I3 F3 N3 | Gates passed: 1, 2
Problem: Boston buildings 20,000+ sqft / 15+ units must report annual energy/water data and meet emissions standards ($150–300/day fines); the City extended the 2026 deadline by 3 months and spun up free support — institutional proof the burden bites. Named user: condo boards of 15–34-unit buildings (City's own "Condos & Co-ops" guidance segment).
Evidence:
- https://www.boston.gov/news/building-carbon-emissions-reporting-deadline-extended-free-technical-support-offered-building (2026-04-15) — verified (fetched): extension to Aug 15, free one-on-one support, ARPA-funded advisor program.
- https://www.facilitiesdive.com/news/bostons-berdo-emissions-deadline-has-been-extended-but-prompt-action-is/820593/ (2026) — verified: owners struggled with "submissions and third-party verifications"; fine schedule.
- https://bostonbps.com/ — plausible: paid "BERDO Help Desk" market exists (claims unverified).
- https://mbmllc.com/berdo-condo-buildings-massachusetts.html — verified exists: condo-specific legal explainer, "penalties... steep".
- MISSING: first-person complaint (Reddit bot-walled). Confidence gap noted.
Demo moment: A condo-board member uploads a year of Eversource/fuel bills (CSV/PDF) → tool maps them to BERDO report fields, flags gaps (missing months, unlisted fuels), and shows estimated compliance position vs their building's standard.
Build plan: see 40_shortlist.md
Agent plan: agent builds bill-field mapping + gap checker + plain-language report; humans assemble the BERDO field checklist from public docs and demo data (synthetic bills — no real PII, Gate 5).
Risks & fallback: Official reporting runs through ENERGY STAR Portfolio Manager — we do NOT replicate it; we do prep/validation. Fallback: checklist + gap-report still demoable if mapping breaks.
Why it matters: Fines are active law; smallest covered owners are least equipped. MA-native, Energy track, clear before/after.