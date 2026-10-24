# 40_shortlist.md — ranked top 5 (Phase D deep dive, 2026-10-24)

## 1. sc8-caption-qa — STEM caption error catcher (Education) I4 F4 N4
**Problem.** Recorded lecture/lab videos carry auto-caption errors concentrated in technical terms; ADA standards now require quality captions; hand-fixing is extremely tedious (3–5× runtime per vendor estimates).
**Evidence.** hartleygroup.org (2025-12-05, verbatim quotes, verified); National Deaf Center (upd. 2026-02-09, verified); UA Little Rock disability-services failure-mode list (verified).
**Demo moment.** Instructor pastes a YouTube URL → in ~2 min: red-flagged technical-term errors on a caption timeline + downloadable corrected SRT.
**Build plan.**
- 09:00 spec-writer: pin demo video + expected term list; define "flag" contract. 4 CS: scaffold web app (FastAPI + minimal frontend).
- 10:00 CS×2: SRT parse/diff engine; CS×2: download/caption pipeline (YouTube Studio SRT fallback if API blocked); chem major: 50-term chemistry lexicon.
- 13:00 re-transcription with open-weight ASR (whisper.cpp small model, laptop CPU); disagreement detector.
- 16:00 tester: end-to-end on 3 real videos; demo-builder: 60-sec walkthrough.
- 18:00 fallback freeze: pre-baked SRTs in repo.
**Agent plan.** Agent builds app + parser + diff; humans own lexicon and validation.
**Risks & fallback.** ASR circularity (whisper mangles same terms) → show disagreement regions, not auto-fixes; download failure → pre-loaded SRTs. We still demo the flagging UI if ASR fails.
**Why it matters.** Compliance is newly mandatory; one professor already DIY'd this — visible demand, crisp tool.

## 2. s4ref-chemval — Pre-flight validator for chem file conversions (Biotech) I3 F3 N5
**Problem.** Free cheminformatics glue (OpenBabel/RDKit) silently produces wrong chemistry in format conversions; the official workaround for a known heme bug is manual bond-table editing.
**Evidence.** openbabel issues #2427, #1049 (open, verified); rdkit discussions #8529, #4084 (verified).
**Demo moment.** Heme xyz→mol2: stock OpenBabel silently corrupts valence; our validator red-flags it in seconds with a diff of atom/bond invariants.
**Build plan.**
- 09:00 spec-writer: define invariant checks (atom count, formula, total charge, per-atom valence bounds, H-count, kekulization success). 4 CS: env setup (rdkit + openbabel via pip/conda — verify TONIGHT), CLI + web front.
- 10:00 CS: conversion harness (run N tool pairs); CS: invariant checker; CS: report UI; chem major: build 10-file test set (incl. heme, metal centers, charged species).
- 13:00 cross-tool disagreement detector (A says X, B says Y → flag).
- 16:00 tester: full test set pass; demo-builder: side-by-side "silent corruption caught" screen.
- 18:00 fallback freeze: canned outputs.
**Agent plan.** Agent builds harness/checker/UI; humans define invariants + test set (chemistry judgment).
**Risks & fallback.** Invariant definitions may false-positive → tune on test set; install friction → tonight's env check decides CLI-vs-web scope. We still demo the heme catch.
**Why it matters.** Silent errors propagate to docking/MD/publications; no validator sits between free tools. Most esoteric pick; chem-major-native.

## 3. sc2-mabill — MA electric bill supply-rate explainer (Energy) I4 F4 N3
**Problem.** $87.4M FY2025 MA consumer overpayment above basic service; confusion is the mechanism (look-alike utility letters, aggregation opt-out panic). Named victim trace: Brookline resident's DPU complaint.
**Evidence.** energychoicematters.com (2026-03-31, verified); greenenergyconsumers blog with quoted DPU complaint (verified); Globe/WBUR repost (2024-03-28, verified).
**Demo moment.** Paste a (synthetic) Eversource bill → breakdown: delivery vs supply, which supply rate you're on, this-month comparison vs published basic rate, plain-language "what would change if you switched."
**Build plan.**
- 09:00 spec-writer: collect published rate sources (DPU basic-service rates, 2–3 MA municipal aggregation rates from mass.gov/town pages) into a data file. 4 CS: bill input form + parser (fixed demo bill format first).
- 10:00 CS: rate table + comparison math; CS: plain-language report UI; CS: "rate segment" explainer graphics; CS: synthetic bills pack (no real PII).
- 13:00 tester: correctness review of comparisons against source pages; demo-builder: 60-sec flow.
- 18:00 fallback freeze.
**Agent plan.** Agent builds parser/UI; humans own rate data accuracy (spec-writer verifies every number against source).
**Risks & fallback.** Bill formats vary → demo on 1–2 synthetic formats; rate data must be current → freeze a dated snapshot with sources shown. Educational framing only, no advice (Gate 5).
**Why it matters.** Quantified harm, state-documented; MA-native; demoable in 60 seconds.

## 4. sc7-mapermits — Town-specific MA solar permitting profiles (Energy) I3 F3 N3
**Problem.** 351 MA towns, different solar permits each; 125 jurisdictions still in-person (July 2025); installers lose weeks-to-months per job.
**Evidence.** bunewsservice.com (2025-10, verified: named installers on record); MASSPIRG figure (plausible); SolarAPP+ free incumbent exists (verified) — gap is town-specific knowledge, not form software.
**Demo moment.** Installer selects 2 towns → side-by-side permit requirements, required docs, submission channel, turnaround norms — each field citing its source page.
**Build plan.**
- 09:00 spec-writer: pick 5 demo towns with published requirements (Arlington + 4 contrast towns). 4 CS: extraction pipeline (town bylaw/portal pages → structured profile, source-cited).
- 10:00 CS×2: per-town profiles; CS: compare UI; CS: source-verification pane.
- 13:00 humans spot-check extracted fields vs town sites; correct agent output.
- 16:00 tester + demo-builder: end-to-end.
- 18:00 fallback freeze: hand-verified profiles cached.
**Agent plan.** Agent does extraction; humans verify (accuracy beats coverage; demo is 5 towns, not 351).
**Risks & fallback.** Extraction errors → source-citation display keeps claims checkable; pending state legislation could obsolete the pain (noted risk; demo unaffected). We still demo the compare view with cached profiles.
**Why it matters.** Named installers call permitting the biggest blocker; soft costs are the solar cost story.

## 5. sc1-berdo-prep — Self-serve BERDO prep for condo boards (Energy) I3 F3 N3
**Problem.** Boston buildings ≥20,000 sqft / 15+ units must file annual energy/water reports + meet emissions standards ($150–300/day fines); City extended the 2026 deadline and offers human support — smallest owners remain least equipped.
**Evidence.** boston.gov (2026-04-15, verified by fetch); facilitiesdive.com (2026, verified); paid BERDO help-desk market exists (plausible). No first-person trace — weakest Gate 1 of the five, kept for MA-native relevance + clean demo.
**Demo moment.** Condo-board member uploads 12 months of synthetic utility bills → report: fields mapped to BERDO data items, gaps flagged (missing months/fuels), estimated position vs building's standard.
**Build plan.**
- 09:00 spec-writer: BERDO data-item checklist from public docs (boston.gov/berdo). 4 CS: bill-upload → field-mapping skeleton.
- 10:00 CS: mapping + gap checker; CS: compliance-position estimate (published emission factors); CS×2: synthetic bill pack (3 building profiles).
- 13:00 chem/math review of factor math; tester end-to-end.
- 16:00 demo-builder: 60-sec flow. 18:00 fallback freeze.
**Agent plan.** Agent builds mapper/report; humans own the checklist + math sanity.
**Risks & fallback.** We do NOT replicate Portfolio Manager — prep/validation only; mapping errors → gap-report still demoable.
**Why it matters.** Active fines + documented struggle + institutional support program; MA-native.