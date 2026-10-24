# 10_seeds.md — seed hypotheses (human-provided + extrapolations)

## Human seeds (S1–S7)
- S1 [Education] Manim/animation assistant for math teachers: teacher uploads lesson plan/curriculum → tool finds existing open-source math animations (manim galleries) → generates similar animations to spec. Verify: do teachers actually ask for this anywhere?
- S2 [Education?] Attention/brain-rot blocker for students. Pre-flagged: crowded category — needs a sharp underserved angle or dies at Gate 3.
- S3 [Healthtech] Ultra-cheap humanitarian problems (GiveWell-style): find field workers'/NGO volunteers' concrete unmet tooling needs in health, sanitation, logistics. Gold standard: the cow story.
- S4 [Biotech] Schrödinger-suite reverse engineering — FLAGGED IP/rules risk. Reframe only: what do computational chemists use commercial suites for that open tools (RDKit, OpenMM, AutoDock Vina) make awkward? Glue/automation/data-wrangling gap.
- S5 [Biotech] Protein-structure work: do NOT solve a folding problem. Pick one small concrete structure/variant problem (e.g., protein family with no experimental structures → predict, visualize, interpret for a named user type). Verify ColabFold/ESMFold/Boltz-class run on laptop compute or free tiers.
- S6 [Education] Teacher-feedback aggregator: course context in → blunt student feedback → AI aggregates into literature-grounded report with actionable items + what other teachers tried. FERPA-style privacy; anonymization mandatory.
- S7 [no track] Anti-doxxing/OSINT-exposure tool: scan public/breach surfaces → plain-language report + opt-out plan for data brokers. Risks: source sprawl, legal care, weak track fit — likely [OFF-TRACK].

## Extrapolations (Scout, from S1–S7)
- E1 (from S3) [Healthtech] Community health worker (CHW) visit-log pain: paper forms → re-entry into DHIS2/commcare by hand. Tool: offline-first form capture that exports clean CSV for existing systems. Verify: r/AskDevelopers, DHIS2 community forum, GitHub issues on ODK/CommCare.
- E2 (from S3) [Healthtech] Cold-chain fridge-temperature logging for small clinics: manual twice-daily logs, WHO/PQS devices too expensive. Tool: cheap webcam/thermometer + phone workflow. Risk: hardware constraint — laptop/phone only. Verify: eHealth Africa posts, immunization logistics blogs.
- E3 (from S5) [Biotech] Protein-family structure-gap triage: take a PFAM family with no PDB structures, run free-tier structure prediction, auto-generate a one-page brief for a lab. User: grad student picking a rotation project.
- E4 (from S4) [Biotech] "SDF→paper" reproducibility gap: computational chemists' supplemental data (SDF/mol files) often unreadable/inconsistent; tool validates + normalizes supplemental structures against what the paper claims. Verify: r/compchem, RDKit GitHub issues.
- E5 (from S1) [Education] Math-teacher worksheet→interactive widget: teacher pastes a worksheet PDF; tool turns exercises into manipulable Desmos-style/JS widgets with answer checking. Verify: r/matheducation, MTBoS blogs.
- E6 (from S6) [Education] TA/grader rubric-consistency checker: given a rubric + anonymized sample of graded work, flag grading inconsistencies. FERPA-safe if anonymized. Verify: prof blogs, r/Professors.
- E7 (from S2) [Education?] Sharp angle only if found: e.g., students report *specific* app features that defeat blockers (rehooking tricks) — a "defeat patterns" dataset. Verify before developing.

## Scout's own hypotheses (across tracks)
- SC1 [Energy] Massachusetts-specific: MA has aggressive building-emissions rules (BERDO/Boston, building decarbonization). Small landlords / condo boards must report energy data but find the portal/forms hard. Tool: guided BERDO-2 compliance data prep from utility CSVs. Verify: BERDO docs, r/boston, landlord forums. MA relevance: direct.
- SC2 [Energy] Community-choice aggregation / municipal electricity data explainer: MA municipal aggregations confuse residents about rates vs Eversource default. Verify: MA AGO energy division complaints, r/massachusetts.
- SC3 [Robotics] Robotics without hardware: warehouse robotics sim gap for community-college/vocational robotics courses — open-source sim curricula? Track fit weak without hardware; needs verification of a real course-pain trace.
- SC4 [Healthtech] EMS/ambulance crew post-call documentation: ESO/NEMSIS ePCR data entry pain. Might need specific software accounts — verify openness. User: EMT/paramedic instructor.
- SC5 [Education] MassHire / adult-ed (ESOL) teacher admin burden: MA adult basic education programs (DESE-funded) have heavy NRS reporting. Tool for ESOL teachers' attendance/outcome reporting. MA relevance: direct. Verify: MASS ABE docs, adult-ed educator forums.
- SC6 [Biotech] Lab-notebook→protocol converter for undergrad bio teaching labs: instructors need protocols adjusted for class scale (30 students, shared equipment). Verify: r/labrats, biology faculty listservs.
- SC7 [Energy] MA solar permitting: small installers face town-by-town permitting variance. Tool: per-town checklist/explainer from public bylaws. Verify: MassSolar docs, r/massachusetts, MA DOER.
- SC8 [Education] Sign-language / accessibility captioning QA: auto-generated captions in recorded lectures have predictable error classes; tool flags likely STEM-term caption errors for disability-services staff. Verify: disability services blogs, NCSPOD listservs.