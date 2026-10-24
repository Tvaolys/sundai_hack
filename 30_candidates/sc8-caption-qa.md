# sc8-caption-qa — Catch STEM-term caption errors before they reach students
Track: Education | Scores: I4 F4 N4 | Gates passed: 1, 2
Problem: Instructors with recorded lecture/lab videos must fix auto-caption errors ("misspelled technical words" per UA Little Rock disability-services page); ADA standards now require quality captions. Named user: chemistry professor running prelab/spectroscopy videos (Miami University).
Evidence:
- https://blog.hartleygroup.org/2025/12/05/fixing-youtubes-automatic-captioning-with-ai/ (2025-12-05) — verified verbatim: captions "are terrible... misinterpreting chemistry words"; hand-fixing "extremely tedious"; ADA driver.
- https://help.nationaldeafcenter.org/article/501-are-automatic-captions-enough-for-accessibility (upd. 2026-02-09) — verified: auto captions "often not accurate enough for learning"; schools "should review and correct".
- https://ualr.edu/disability/faculty/captureaudiocaptionvideo/ — verified (fetched 2026-10-24): failure-mode list incl. "Incorrect terminology, Misspelled technical words"; "not accurate enough to meet accessibility standards... must be reviewed and corrected".
Demo moment: Instructor drops a YouTube URL → tool returns the video's captions with every technical term flagged red (re-transcribed diff) + a fix-queue view, in under 2 minutes.
Build plan: see 40_shortlist.md
Agent plan: agent builds the web app, SRT parser, diff engine; humans pick the test video and tune the domain lexicon (chem major supplies term list).
Risks & fallback: ASR also mangles chemistry terms (circular) — fallback: diff highlights *disagreement regions*, not fixes; still surfaces correction spots. [ASSUMPTION TO VERIFY TONIGHT: whisper.cpp small model runs acceptably on laptop CPU for a 10–15 min video.] YouTube download via Studio export only — demo on pre-downloaded SRT if blocked.
Why it matters: Accessibility compliance is newly mandatory and hand-fixing is 3–5× video runtime (vendor-quantified). One professor already tried DIY-LLMing this — demand trace.