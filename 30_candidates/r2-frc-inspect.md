# r2-frc-inspect — Pre-inspection self-check for FRC teams from the official PDF checklist
Track: Robotics | Scores: I3 F4 N4 | Gates passed: 1, 2
Problem: The FRC robot inspection is run from an official PDF checklist; volunteers call the paperwork a "headache" (dated, named roles: LRIs, inspection managers, inspectors). Teams that fail inspection waste event time. Named user: FRC volunteer inspecting at events (Chief Delphi, 2022-02-02).
Evidence:
- https://www.chiefdelphi.com/t/401917/155 (2022-02-02) — verified: "It becomes a headache for LRI's, inspection managers, and inspectors... Does it need to be headache with all this paperwork?"
- https://firstfrc.blob.core.windows.net/frc2025/Manual/2025FRCInspectionChecklist.pdf (2025 season) — verified: checklist is still a PDF.
- CAVEAT: FIRST is modernizing (FTC cloud Event Portal v8.2.6) — FRC may follow; problem could shrink.
Demo moment: Team walks through the guided checklist on a laptop at their pit table → live pass/fail per item with photos → printable inspection-ready summary the LRI can verify in 60 seconds.
Build plan: see 40_shortlist.md
Agent plan: agent parses the public PDF checklist into structured items + builds the guided-check UI; humans verify extraction correctness (rule-critical).
Risks & fallback: PDF extraction errors → human-verified item list frozen in repo before demo; FIRST modernization risk noted. Fallback: demo on 2 preset robot profiles.
Why it matters: Seasonal but intense pain; every FRC team preps for this; MA has a dense FRC scene. Distinct user (teams/volunteers) from r1 (mentors).