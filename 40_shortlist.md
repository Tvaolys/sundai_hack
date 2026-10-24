# 40_shortlist.md — ranked top 8 (Round 2, 2026-10-24)

Round-2 changes: sc8-caption-qa KILLED (human challenge confirmed — 3Play/Verbit serve 2,000+ universities); s4ref-chemval downgraded (human: too narrow; kept at #8); 10 new hypotheses hunted → 3 traces (R10, R1, R2), rest WEAK/CROWDED. Ranks integrate the human's impact judgment.

## 1. r10-massave-rebates — Mass Save rebate doc & status tracker (Energy) I4 F4 N4
Named victims (CBS I-Team 2021-12-10, 2023-12-18: 1-yr waits, "$10K only after TV intervention"); Sept 2026 fraud suit ($7.7M) just raised documentation burden — fresh why-now.
**Demo.** Enter project (heat pump/insulation, utility) → complete requirements packet, expected timeline from published rules, status checklist flagging documented delay causes.
**Build plan.** 09:00 spec-writer: pin Mass Save program requirements from published docs (Manual J, HPQPL, photo rules), dated. CS×4: packet generator + tracker UI scaffold. 10:00 CS×2: requirement DB per measure/utility; CS: timeline explainer; CS: contractor-mode view. 13:00 tester: verify every field vs source pages; chem/math: sanity-check any arithmetic. 16:00 demo-builder: contractor + homeowner flows. 18:00 fallback freeze (canned packets).
**Risks.** Rules change → date every field; never file on users' behalf (Gate 5). Fallback: checklist+timeline explainer.
**Agent plan.** Agent builds generator/UI; humans own requirement accuracy.

## 2. sc2-mabill — MA electric bill supply-rate explainer (Energy) I4 F4 N3
$87.4M FY2025 overpayment (AGO 2026-03-31); quoted DPU complaint (Brookline resident, look-alike utility letters).
**Demo.** Paste synthetic Eversource bill → delivery-vs-supply breakdown, which supply rate you're on, comparison vs published basic rate, plain language.
**Build plan.** 09:00 spec-writer: assemble dated rate sources (DPU basic service, 2–3 aggregation rates). CS×4: input form + parser (1–2 formats), rate tables, comparison math, report UI. 13:00 tester: verify comparisons vs sources. 16:00 demo flow. 18:00 freeze.
**Risks.** Bill formats vary → 1–2 synthetic formats; freeze a dated rate snapshot with sources; educational only, no advice (Gate 5).

## 3. r1-frc-mentor — Attendance/hours logging FRC mentors keep using (Robotics) I3 F4 N4
Whiteboard admission (Chief Delphi 2023-04-25); paper sign-in 2019→2025. Caveat: TeamSnap "good enough" layer + indie PitCrew — wedge is FIRST-specific hours/milestones with zero-setup check-in.
**Demo.** Paper sheet → phone check-in; who's in, hours/student, season hours export in 60s.
**Build plan.** 09:00 spec-writer: extract mentor workflow expectations from Chief Delphi threads; CS×4: offline-first check-in app (roster import, QR/short-code check-in, hours export). 13:00 tester: two-phone live test. 16:00 demo: migration story paper→log. 18:00 freeze.
**Risks.** Adoption is the documented failure mode → 10-second check-in, no student accounts. Fallback: canned-roster demo.

## 4. r2-frc-inspect — Pre-inspection self-check from official FRC PDF (Robotics) I3 F4 N4
2025 checklist still PDF; volunteer "headache" quote (2022-02-02). Caveat: FIRST modernizing FTC portal; may follow in FRC.
**Demo.** Guided checklist at pit table → pass/fail + photos → printable inspector-ready summary.
**Build plan.** 09:00 CS×2: parse public PDF into structured items (human-verify list by 11:00 — rule-critical); CS×2: guided-check UI + photo capture + printable summary. 13:00 tester: full-item walkthrough on 2 preset robot profiles. 16:00 demo flow. 18:00 freeze.
**Risks.** Extraction errors → human-verified item list frozen in repo; seasonality irrelevant to demo.

## 5. sc7-mapermits — Town-specific MA solar permitting profiles (Energy) I3 F3 N3
Named installers on record (Oct 2025): "Permitting is the state's biggest blocker"; 351 regimes; 125 in-person jurisdictions (Jul 2025).
**Demo.** Two towns side-by-side: permit requirements, docs, channel, turnaround — every field source-cited.
**Build plan.** 09:00 spec-writer: pick 5 towns (Arlington + 4 contrast). CS×4: extraction pipeline + compare UI + source-verification pane. 13:00 humans spot-check vs town sites. 16:00 demo. 18:00 freeze (cached profiles).
**Risks.** Extraction errors → per-field citations keep claims checkable; pending state legislation could shrink the problem.

## 6. sc1-berdo-prep — Self-serve BERDO prep for condo boards (Energy) I3 F3 N3
City extended its own 2026 deadline + free support (boston.gov 2026-04-15); $150–300/day fines; smallest owners least equipped. Weakest Gate 1 of the 8 (institutional traces only) — flagged honestly.
**Demo.** Upload 12 months synthetic bills → BERDO field mapping, gap flags, estimated compliance position.
**Build plan.** 09:00 spec-writer: BERDO data-item checklist from public docs. CS×4: bill→field mapping, gap checker, compliance estimate, synthetic bill pack (3 profiles). 13:00 math review. 16:00 demo. 18:00 freeze.
**Risks.** We do NOT replicate Portfolio Manager — prep/validation only; fallback: gap report.

## 7. sc6-protocolscale — Class-scale protocol adaptation (Education) I3 F3 N3
410-instructor survey: 85 discontinuers; "lack of time for course development" (PMC 2025); $135/student cost pressure.
**Demo.** Paste research protocol → 30-student version: per-group quantities, shared-equipment schedule, cost estimate, waste/safety notes — each output line citing its input line.
**Build plan.** 09:00 chem major: pick benign demo protocol. CS×4: parser, scaling engine (quantity/schedule tables), cost estimate, safety-note generator w/ provenance. 13:00 chem-major correctness review. 16:00 demo. 18:00 freeze.
**Risks.** Chemistry correctness → benign protocol + provenance citations; structured tables only, no chatbot drift.

## 8. s4ref-chemval — Chem file-conversion pre-flight validator (Biotech) I2 F3 N5
Open GitHub issues (openbabel #2427 heme valence — official fix is MANUAL editing; #1049 silent wrong SMILES; rdkit #8529/#4084). Human judgment: audience too narrow to prioritize — ranked last for that reason, novelty intact.
**Demo.** Heme xyz→mol2: stock OpenBabel silently corrupts valence; validator red-flags it with an invariants diff.
**Build plan.** 09:00 TONIGHT-VERIFY: pip rdkit+openbabel on team laptops (gate this idea). spec-writer: invariant list (atom count, formula, charge, valence bounds, H-count, kekulization). CS×4: conversion harness + invariant checker + report UI. 13:00 chem major: 10-file test set. 16:00 demo: silent corruption caught. 18:00 freeze.
**Risks.** False positives → tune on test set; install friction → CLI scope.