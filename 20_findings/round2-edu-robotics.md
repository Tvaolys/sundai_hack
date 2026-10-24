# Round 2 Evidence Findings — Education & Robotics

Method note: primary traces pulled from Chief Delphi Discourse search API (search.json, live-fetched 2026-10-24), web search, and direct page fetches. Quotes are blurbs as returned by the source; nothing fabricated.

---

## R1 [Robotics] FIRST robotics volunteer-mentor logistics pain (build-season tracking, parent/student comms, inventory)

### Traces (all chiefdelphi.com, verified via live Discourse API fetch 2026-10-24)

1. **URL:** https://www.chiefdelphi.com/t/360760 | **Date:** 2019-07-25 (user NYtoWI)
   Shows: "My team is looking for a new way to track our students attendance and hours spent throughout season. We currently are just having student mark on paper when they arrive." First-person mentor pain: paper-based attendance tracking with no tooling. **Confidence: verified**

2. **URL:** https://www.chiefdelphi.com/t/435767/7 | **Date:** 2023-04-25 (Marcus Kauffman, mkauffman, 3 likes)
   Shows: "For the past two years my team has not used team management software very effectively. Next year we will be using team management hardware. (whiteboard)" — dated, first-person admission that team-management software failed and they regressed to a whiteboard. **Confidence: verified**

3. **URL:** https://www.chiefdelphi.com/t/398608 | **Date:** 2022-01-02 (Micah Guttman, memtech3)
   Shows: "I've been looking for fancy digital attendance solutions for our team... We currently use a google form but I think there are more effective solutions (quicker for members to check in/out)." — ongoing tooling-gap shopping. **Confidence: verified**

4. **URL:** https://www.chiefdelphi.com/t/418291 | **Date:** 2022-11-21 (James Makar, jamestown)
   Shows: "My team was exploring the use of an attendance tracker for upcoming seasons... couldn't that just be done with a google form or a sign out sheet." — recurring same-pain thread 3 years apart (2019, 2022, 2025). **Confidence: verified**

5. **URL:** https://www.chiefdelphi.com/t/502777 | **Date:** 2025-06-04 (Charlie Hamm, hosting team running state championships)
   Shows: Mentor scrambling for "unique ways to track the attendance of students/mentors competing from every team as well as attendance from community" for events they host. **Confidence: verified**

6. **URL:** https://www.chiefdelphi.com/t/519939 | **Date:** 2026-05-03 (Elijah Crum, crummyh)
   Shows: Season-wind-down post: "One of the main thing I am looking at is how teams are keeping track of their stuff and making sure everything gets made correctly" — inventory/build-tracking pain, first-person, current. **Confidence: verified**

7. **URL:** https://www.chiefdelphi.com/t/416607/3 | **Date:** 2022-10-26 (Technologyman00)
   Shows: "My team just employs a inventory management spreadsheet that lists the item name and where it's supposed to be." — incumbent state of the art is a hand-rolled spreadsheet. **Confidence: verified**

8. **URL:** https://www.chiefdelphi.com/t/366932 | **Date:** 2019-11-29 (Tuck55)
   Shows: "My team is looking at trying out a team management software to collaborate better between our subteams" — evaluating Microsoft DevOps; generic dev tools repurposed for team ops. **Confidence: verified**

9. **URL:** https://www.chiefdelphi.com/t/506280/3 | **Date:** 2025-09-13 (Lee_Hanna)
   Shows: "We use both email and Teamsnap. TS has the calendar and going/not going functions, which some parents like." — parent comms handled by generic sports apps + email. **Confidence: verified**

10. **URL:** https://www.chiefdelphi.com/t/384787/1 | **Date:** 2020-05-09 (Caleb Denio, cjdenio, 12 likes)
    Shows: Long first-person writeup of "helpful (and not-so-helpful) online tools for team collaboration" — practitioners documenting tooling gaps themselves. **Confidence: verified**

11. **URL:** https://www.chiefdelphi.com/ | **Date:** 2020-01-04 (legoguy1000, topic via STIMS/attendance search)
    Shows: Mentor built and shipped his own Progressive Web App (github.com/legoguy1000/FRC-Portal, QR-code hours tracking) because no existing tool fit — classic build-it-yourself signal. **Confidence: verified** (post seen in API blurb; GitHub URL as quoted in post)

### Crowding check (existing tools seen in traces)
- **Generic sports/team apps:** TeamSnap actively used by FRC teams for parent RSVP comms (trace 9).
- **Generic dev tools:** Microsoft DevOps (2019), Jira (JohnFogarty, 2025-08-27, https://www.chiefdelphi.com/t/505687/3 — "I recently onboarded my team to Jira for managing our Software Team"), Slack/Discord (trace 10).
- **FIRST official:** STIMS (Student Team Information Member System) for registration/hours.
- **Purpose-built, new:** PitCrew (the-pitcrew.info) — "mentor-assist command center for small and rebuilding FRC & FTC teams," AI kickoff wizard + build schedule + auto engineering notebook; appears to be a new indie entry. LearnFRC (learnfrc.com) — free curriculum/guide site with a business-operations/kanban lesson.
- **DIY portal pattern:** multiple mentors built their own trackers (FRC-Portal 2020, grizzlytime referenced 2022) — demand exists but has been met by free DIY + generic SaaS, not a dominant paid product.

### Verdict: **TRACE FOUND**
Dated, recurring, first-person mentor complaints (2019→2026, same pain repeating). But crowding is real at the "good enough" layer: TeamSnap/Google Forms/whiteboards/DIY portals absorb the need; a dedicated paid SaaS has little observed traction and at least one new indie entrant (PitCrew) just appeared. Opportunity is real but the wedge must beat free alternatives.

---

## R2 [Robotics] FRC/FTC competition inspection/judging paperwork pain

### Current-state verification (is FIRST still paper/PDF?)
- **URL:** https://firstfrc.blob.core.windows.net/frc2025/Manual/2025FRCInspectionChecklist.pdf | **Date:** 2025 season
  Shows: FIRST's official FRC robot inspection checklist for the 2025 season is still distributed as a printable PDF. **Confidence: verified**
- **URL:** https://ftc-scoring.firstinspires.org/ | **Date:** fetched 2026-10-24, page footer "FIRST Event Portal – v8.2.6, © 2026"
  Shows: FIRST HAS modernized FTC scoring/judging infrastructure into a cloud "FIRST Event Portal"; FTC Local Scoring Software is open-source on GitHub (github.com/FIRST-Tech-Challenge/scorekeeper). So scoring is digital; inspection checklists remain PDF. **Confidence: verified**
- **URL:** https://bovlb.github.io/frc-tips/inspection/2025.html | **Date:** 2025
  Shows: Community-maintained "Annotated Inspection Checklist" exists to make the PDF usable — third parties already patching the gap. **Confidence: verified**

### Traces
1. **URL:** https://www.chiefdelphi.com/t/474492/13 | **Date:** 2024-11-08 (Gavin Matthews, bovlb — an FRC robot inspector)
   Shows: "I have been trying to make a habit of bringing paper to the pits — Inspection Checklists, rule books, answers to common CSA questions, judging criteria." Inspector confirms paper checklists are the working medium at events. **Confidence: verified**
2. **URL:** https://www.chiefdelphi.com/t/460094 | **Date:** 2024-03-25 (Gavin Matthews, 17 likes)
   Shows: FRC inspector's mid-season writeup: "common inspection issues I've seen this year, and what teams could be doing to get through inspection faster" — inspection throughput is a known pain point. **Confidence: verified**
3. **URL:** https://www.chiefdelphi.com/t/474492/2 | **Date:** 2024-09-12 (same inspector)
   Shows: "I feel like much of my time in the pit is spent waiting for teams to attach bumpers, remove panels, and otherwise make the robot ready for inspection" — first-person volunteer time-loss. **Confidence: verified**
4. **URL:** https://www.chiefdelphi.com/t/401917/155 | **Date:** 2022-02-02 (Ryan Swanson, quoting an LRI's complaint)
   Shows: "It becomes a headache for LRI's, inspection managers, and inspectors though. Does it need to be headache with all this paperwork, or could teams just self-identify...?" — dated, first-person inspection-paperwork headache. **Confidence: verified**
5. **URL:** https://www.chiefdelphi.com/t/430324/5 | **Date:** 2023-03-15 (Gus Michel II, GeeTwo — FTC/FLL judge)
   Shows: "We were directed to clearly communicate to any teams who left a binder or other paperwork that it would NOT be returned, but shredded after the event... different than pre-pandemic." Judging paperwork logistics in flux. **Confidence: verified**

### Crowding / context check
- FIRST itself owns and is actively modernizing this workflow (FTC Event Portal cloud scoring v8.2.6; volunteer manuals updated Oct 2026). A third-party tool must be adopted by FIRST or run unofficially; unofficial tools already exist (ftc.nexus queueing, firsttech.tools directory, bovlb's annotated checklist).
- FRC inspection is run by volunteer LRI/RI staff with FIRST-provided PDFs; no commercial SaaS observed for inspection management.

### Verdict: **TRACE FOUND** (with a structural caveat)
Real dated volunteer complaints about paper/PDF inspection paperwork (2022–2024, from named inspectors). But FIRST is the incumbent vendor and is itself modernizing (cloud scoring live); the paper pain persists in FRC inspection specifically. This is a "sell to FIRST" or "gray-area unofficial tool" market — weakest of the robotics hypotheses for a standalone startup.

---

## R7 [Education] School science-fair/STEM-competition volunteer + judge coordination

### Crowding check (mandatory — incumbents found)
- **URL:** https://zfairs.com/ | **Date:** fetched 2026-10-24
  Shows: zFairs is a mature, purpose-built incumbent: "Everything you need to run judged student contests in one place" — registration, project check-in, judge registration, rubric scoring, awards, virtual interviews, companion app, SRC/IRB paperwork workflows. Client list includes the **Massachusetts Science & Engineering Fair**, Twin Cities Regionals, WESEF, VSSEF; explicitly "Recommended by Society for Science." **Confidence: verified**
- **URL:** https://scilympiad.com/ | **Date:** fetched 2026-10-24
  Shows: Scilympiad — free Tournament & Scoring Management System for Science Olympiad since 2017; features include school/team registration, event signup, **volunteer signup**, communications, online tests, grading, scoring. "Scilympiad hosts between 350 and 410 tournaments each year." **Confidence: verified**
- **URL:** https://www.tamucc.edu/education/events/sciencefair/volunteer.php | **Date:** 2026 fair cycle (events dated Feb 2026)
  Shows: Regional fairs also run on **StemWizard** (judge registration at cbrsf.stemwizard.com) and Qualtrics/Google Forms — a third incumbent in the same niche. **Confidence: verified**
- **URL:** https://fairgameinitiative.org/setupguide.html | **Date:** fetched 2026-10-24
  Shows: FairGame Initiative — a nonprofit giving schools a full science-fair setup guide and "handles judge recruitment, fair registration, and student support" for free. **Confidence: verified**

### Traces
1. **URL:** https://www.signupready.com/blog/science-fair-volunteer-signup-guide | **Date:** undated blog (fetched 2026-10-24)
   Shows: "Judges are the backbone of a science fair, and they are consistently the hardest volunteers to recruit." Confirms pain, but it is vendor content marketing for a signup-sheet tool. **Confidence: plausible** (vendor source)
2. **URL:** https://www.science-swfl.org/science-fair-judging | **Date:** 2025-2026 season retrospective
   Shows: Regional science society reports schools cancelling fairs: "three schools later cancelled their fairs... a noticeable decline in the number of schools hosting science fairs this year." Pain signal is declining demand, not coordination tooling. **Confidence: verified**
3. **URL:** https://cpsstemfair.org/supporting-student-research/become-judge | **Date:** 2026 season
   Shows: Chicago Public Schools STEM fairs still coordinate judges via a Google Form + separate district volunteer-approval form — the low-tech end of the market, but no first-person complaint attached. **Confidence: verified** (form-existence only; pain unverified)
4. **URL:** https://www.dailykos.com/stories/2026/9/4/800091039/ | **Date:** 2026-09-04
   Shows: "A Science Fair Judge on Projects Doomed by October" — first-person judge narrative, BUT it links to an off-topic essay-mill guide, so it reads like SEO placement; do not treat as authentic grassroots pain. **Confidence: unverified** (authenticity suspect)

### Verdict: **CROWDED**
Multiple mature purpose-built incumbents (zFairs with MA presence, Scilympiad free at scale, StemWizard) plus free nonprofit support (FairGame). No authentic dated first-person complaint found after 5 phrasings; the strongest "pain" content is vendor marketing. Kill or find a sharply underserved sub-angle (e.g., informal school-level fairs below the regional tier, special-awards judging).

---

## R8 [Education] Substitute-teacher coordination in small districts

### Crowding check (mandatory — heavily saturated)
- **URL:** https://www.powerschool.com/solutions/substitute-management-software/ | **Date:** fetched 2026-10-24
  Shows: PowerSchool SmartFind Express — automated callout, mobile app, absence analytics; copyright 2005-2026. **Confidence: verified**
- **URL:** https://www.tylertech.com/products/absence-substitute | **Date:** fetched 2026-10-24
  Shows: Tyler Technologies "Absence & Substitute" (ReadySub) — "more notification options than any platform on the market," payroll integration, matchmaking. **Confidence: verified**
- **URL:** https://simplyslate.com/ | **Date:** fetched 2026-10-24
  Shows: Slate — newer entrant explicitly selling "fill sub vacancies, fast" with availability notifications to districts. **Confidence: verified**
- **URL:** https://worldmetrics.org/best/automated-substitute-management-software/ | **Date:** updated 2026-09-05
  Shows: Roundup lists at least 10 automated substitute-management vendors incl. Tyler, Red Rover, Frontline Absence & Time — the category is a standard K-12 procurement line item. **Confidence: verified**
- **URL:** https://tcpsoftware.com/articles/best-substitute-teacher-software/ | **Date:** 2026
  Shows: "Most districts already have some form of absence and substitute management software." Direct confirmation of incumbency. **Confidence: verified**

### Traces
1. **URL:** https://www.nber.org/system/files/working_papers/w30714/w30714.pdf | **Date:** NBER working paper (2021+), cited by TCPSoftware 2026
   Shows: "1 in 5 substitute requests go unfilled" — the headline pain stat; market-level, not first-person. **Confidence: verified** (stat as quoted by secondary source)
2. **URL:** https://www.reddit.com/r/SubstituteTeachers/comments/16y04vq/does_anyone_else_use_smartfind_express_is_it_the/ | **Date:** Reddit post ID 16y04vq (circa Oct 2023, inferred from ID — unverified)
   Shows: Thread title "Does anyone else use SmartFind Express? Is it the..." — complaint-shaped post about the dominant incumbent; content body blocked from access, so substance unverified. **Confidence: unverified** (title seen; body not readable)
3. **URL:** https://schoolites.com/school-problems/teacher-substitution | **Date:** undated (fetched 2026-10-24)
   Shows: Vivid "morning crisis" narrative — secretary matching 50 printed timetables, 200+ hours/year on manual sub coordination — but it is a vendor's marketing page, not an authentic practitioner post. **Confidence: unverified** (vendor content)
4. **URL:** https://www.teachngo.com/blog/how_to_handle_substitute_teacher_scheduling_without_a_fuss | **Date:** undated
   Shows: Another vendor restating the same pain (spreadsheets, phone-call floods) — further evidence the pain is real AND the vendor space is full. **Confidence: plausible** (vendor source)
5. **Underserved-angle check ("volunteer substitutes," tiny districts, phone-tree workarounds):** after 3 phrasings (incl. "tiny school district no sub finder secretary calls substitutes each morning workarounds"), no dated first-person trace found. **[EMPTY: phrasings tried — "small rural school district substitute shortage phone tree software"; "reddit teachers hate Frontline sub finder 5am calls"; "tiny school district secretary calls substitutes workarounds"]**

### Verdict: **CROWDED**
Frontline (ex-Aesop), PowerSchool SmartFind Express, Tyler ReadySub, Red Rover, Slate and a long tail of SMB vendors cover everything from mega-districts down; marketing copy itself admits "most districts already have" such software. No authentic underserved angle surfaced (volunteer substitutes: empty). Kill.

---

# Final verdicts

| Hypothesis | Verdict |
|---|---|
| R1 FRC/FTC volunteer-mentor logistics | **TRACE FOUND** — recurring dated mentor complaints (2019→2026), but free/diy/generic-tool incumbency (TeamSnap, Google Forms, DIY portals) plus new indie entrant PitCrew |
| R2 FRC/FTC inspection/judging paperwork | **TRACE FOUND** — PDF checklists + named-inspector complaints confirmed; but FIRST is the incumbent and is actively modernizing (sell-to-FIRST dependency) |
| R7 Science-fair judge/volunteer coordination | **CROWDED** — zFairs (MA fair, Society-for-Science-recommended), Scilympiad (free, 350-410 tournaments/yr), StemWizard; no authentic grassroots complaint found |
| R8 Substitute coordination | **CROWDED** — Frontline, PowerSchool, Tyler ReadySub, Red Rover, Slate et al.; underserved-angle searches empty |
