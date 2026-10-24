# sc6-protocolscale — Adapt research protocols to 30-student class scale
Track: Education | Scores: I3 F3 N3 | Gates passed: 1, 2
Problem: Instructors abandon research-style labs (CUREs) at scale — 85 of 410 surveyed instructors were discontinuers; complexity/compatibility predict abandonment; course-development time is the named constraint. Named user: survey respondents (not individual-named — trace is peer-reviewed, not forum-first-person).
Evidence:
- https://aaas-iuse.org/resource/a-quantitative-analysis-of-instructor-barriers-for-using-course-based-research-experiences/ — verified: 410 instructors, 217 continuers / 85 discontinuers / 108 never-used.
- https://ohiostate.pressbooks.pub/coursebasedresearch/chapter/g-overcoming-the-challenges-of-cures/ (2023) — verified: obstacle taxonomy compiled from 7 peer-reviewed studies.
- https://bioengineer.org/adapting-laboratory-techniques-for-remote-instruction/ — verified: $135/student kit cost quantifies per-student scaling pressure.
- https://pmc.ncbi.nlm.nih.gov/articles/PMC12369356/ (2025) — verified: "lack of time for course development".
Demo moment: Instructor pastes a research-grade protocol (reagent amounts, equipment, batch workflow) → tool outputs a 30-student/12-groups class version: per-group quantities, shared-equipment schedule, prep-time and cost estimate, waste/safety notes.
Build plan: see 40_shortlist.md
Agent plan: agent builds protocol parser + scaling engine + cost/schedule tables; chem major validates correctness of scaled quantities and safety notes on the demo protocol.
Risks & fallback: Correctness risk on real chemistry — fallback: demo on a benign well-characterized protocol; every output cites the input line it derives from. Risk of drifting into "chatbot slop" — output must be structured tables, not conversation.
Why it matters: The CURE ecosystem funds pedagogy but no tool does the mechanical class-scale adaptation; documented discontinuation is the cost of not having it.