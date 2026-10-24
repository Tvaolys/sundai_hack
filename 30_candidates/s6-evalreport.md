# s6-evalreport — Turn blunt student feedback into a literature-grounded teaching report
Track: Education | Scores: I3 F3 N3 | Gates passed: 1, 2
Problem: End-of-term evaluations are documented as uninformative and hard to read constructively; instructors receive blunt/insulting raw comments and no actionable synthesis. Named user: Lewis & Clark instructor (17 years, 1,600 students) editorializing against anonymous term reviews, quoting real received comments (mossylog.org, 2024-11-15).
Evidence:
- https://mossylog.org/2024/11/15/anonymous-term-reviews-are-harmful-obsolete/ (2024-11-15) — verified: first-person editorial with quoted eval comments.
- https://library.cod.edu/feedback/semester — verified: faculty guide citing "six major issues with course evaluations" (Chronicle) and constructive-reading guidance.
- https://www.facultyfocus.com/articles/educational-assessment/course-correcting-mid-semester-a-three-question-feedback-survey/ (2025-03-14) — verified: practitioners rethinking eval timing/format.
- CAVEAT: https://lock.pub/en/blog/anonymous-teacher-feedback — a feedback-tool vendor already productizes aggregation. Confidence: verified.
Demo moment: Instructor pastes 30 anonymized student comments + course context → tool returns a report: clustered themes, severity vs sentiment, 3 literature-grounded change recommendations (each citing an identified pedagogy source), and what similar instructors report trying.
Build plan: see 40_shortlist.md
Agent plan: agent builds anonymizer (name/identifying-regex scrub), clustering, and report generator with source-grounding; humans curate the pedagogy source list (10–20 credible links) — grounding must be real, not invented.
Risks & fallback: FERPA-adjacent — anonymization mandatory, demo uses synthetic comments (Gate 5). Hallucinated citations are the failure mode — fallback: report cites only the human-curated list. Vendor crowding noted at Gate 3 review.
Why it matters: Documented instructor pain; actionable-synthesis-with-citations is the differentiator vs raw dashboards.