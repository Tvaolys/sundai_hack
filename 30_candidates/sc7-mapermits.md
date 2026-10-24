# sc7-mapermits — Town-specific solar permitting checklist for MA installers
Track: Energy | Scores: I3 F3 N3 | Gates passed: 1, 2
Problem: Each of MA's 351 municipalities has different residential solar permits; 125 jurisdictions still required in-person permitting (July 2025); installers lose days-to-months per job. Named users: David Bridge and Byron Johnson (Great Sky Solar, Lexington), James Manzer (ReVision Energy) — on record Oct 2025.
Evidence:
- https://bunewsservice.com/as-solar-advocates-push-for-streamlined-permitting-installer-claims-arlington-remains-ahead-of-the-curve/ (2025-10) — verified: quotes above; "Permitting is the state's biggest blocker"; Arlington ~1 week vs "months" elsewhere.
- https://pirg.org/massachusetts/edfund/updates/streamlining-permitting-to-bring-more-solar-to-more-homes-more-quickly/ — plausible: source of 125-jurisdiction figure.
- https://www.gosolarapp.org/landing-pages/solarapp-in-massachusetts — verified: SolarAPP+ free for jurisdictions; adoption, not tooling, is the gap.
Demo moment: Installer picks a town → tool generates that town's current permit requirements (from public bylaws/portal), required docs, and turnaround norms — vs. the neighbor town's, side by side.
Build plan: see 40_shortlist.md
Agent plan: agent builds per-town profile extraction from public bylaw PDFs/permit-portal pages for 5–10 demo towns; humans verify extracted requirements against town sites (spot-check) and write installer-facing copy.
Risks & fallback: Bylaw PDFs are messy; LLM extraction may err — fallback: cite-source-per-field display so claims are checkable; demo on towns with clean published requirements. Pending state legislation could obsolete the problem (risk noted).
Why it matters: Soft costs are the documented solar cost driver; installers named the pain on record. MA-native, Energy track.