# 20_findings/scout-probes.md — Scout's own inline searches (2026-10-24)

## S1 — manim/animation assistant for math teachers
- Searched: "math teachers manim animation lessons request forum reddit" → [] (empty).
- Searched: 3Blue1Brown/manim teacher request → returned tooling pages (manim GitHub, community edition, AI manim skills) but NO trace of a teacher asking for classroom animations. Confidence: verified-empty.
- Background, verified: manim CE is MIT-licensed, community-maintained (https://github.com/3b1b/manim, retrieved 2026-10-24). r/manim and a Discord exist.
- VERDICT so far: no teacher-pain trace yet. Pending agent hunt. If nothing: teacher side of Gate 1 fails.

## E1 — CHW paper-form capture → DHIS2 re-entry
- KoBoToolbox: free, open-source, offline-first, built by Harvard Humanitarian Initiative for exactly this gap; exports CSV/Excel/SPSS/GeoJSON; free hosting at kobotoolbox.org for humanitarian use (https://casrai.org/guides/kobotoolbox-mobile-field-data-collection, retrieved 2026-10-24). Confidence: verified.
- DHIS2 has own Data Entry + Tracker Capture apps (docs.dhis2.org, retrieved 2026-10-24). Confidence: verified.
- VERDICT so far: space well-served by mature free tools. Gate 3 risk HIGH unless a specific workflow gap (e.g., XLSForm authoring difficulty, export-to-DHIS2 munging) shows a trace.

## E5 — worksheet → interactive widget (adjacent signal)
- Chalkbeat interview with math teacher Dylan Kane, 2026-04-07 (https://www.chalkbeat.org/2026/04/07/teacher-dylan-kane-drops-classroom-screens-in-ed-tech-experiment/): teacher valued Desmos activities for letting "students manipulate math in a different way"; went screen-free and finds paper prep "way more work" than clicking to assign online. Confidence: verified (quoted from article).
- Read: weakly supports E5 (teachers want manipulation-style materials but prep is expensive). NOT a direct trace of the specific pain. Confidence for pain: unverified.

## SC1/SC7 quick note
- Nothing gathered inline yet; delegated to energy agent.