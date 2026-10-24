# r10-massave-rebates — Mass Save rebate documentation & status tracker for homeowners and small contractors
Track: Energy | Scores: I4 F4 N4 | Gates passed: 1, 2
Problem: Mass Save rebate delays are documented with named victims (1-year waits, $10K checks only after TV-station intervention); a Sept 2026 fraud settlement ($7.7M) just raised documentation burden on honest applicants. Named users: John Semas (Norfolk), Barry Rubin, Edward Griffin (CBS I-Team), plus small contractors facing the "Strengthening Oversight" update.
Evidence:
- https://www.cbsnews.com/boston/news/mass-save-heat-pump-rebates-delays-i-team/ (2021-12-10) — verified: Semas >1yr for ~$6,000; Kozuch 6+ months for $250.
- https://www.cbsnews.com/boston/news/i-team-mass-save-rebate-program-changes/ (2023-12-18) — verified: 6-month backlog persisted; named homeowners; checks only after I-Team involvement.
- https://www.bostonglobe.com/2026/09/22/metro/mass-save-fraud-contractor-8-million/ (2026-09-22) — verified: fraud suit; contractor suspended; Sept 23, 2026 program update increases documentation burden.
Demo moment: Contractor/homeowner enters their project (heat pump/insulation, utility) → complete requirements packet (forms, Manual J, HPQPL references, photos), expected timeline from published rules, and a status checklist that flags the documented delay causes.
Build plan: see 40_shortlist.md
Agent plan: agent builds requirement-extraction + packet generator + tracker UI; spec-writer owns accuracy of every requirement against published Mass Save docs.
Risks & fallback: Program rules change; source-date every field. Do not file on users' behalf (Gate 5, educational tracker only). Fallback: checklist + timeline explainer still demos if extraction is shaky.
Why it matters: Named victims, state-documented dysfunction, fresh why-now. MA-native Energy.