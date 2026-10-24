# Round 2 Findings — Energy (R4, R5, R10)

Evidence hunter round 2. Today: 2026-10-24. Discipline: only URLs/dates/quotes actually observed. Search surface: web_search + web_fetch (Cherry tools).

---

## R4 [Energy] Heat-pump installer quoting/proposal bottleneck in MA

### Findings

1. **URL:** https://shopping.yahoo.com/home-garden/home-improvement/articles/massachusetts-homeowner-gets-24-500-203400258.html (syndicating https://www.reddit.com/r/hvacadvice/comments/1woa8zm/ma_is_24k_reasonable_for_a_bryant_multizone/)
   **Date:** not shown on page fetched (undated in snippet/fetch)
   **What it shows:** Boston-suburbs homeowner comparing heat pump quotes: got 4 quotes, "$24K ~ 28K" for a similar Bryant multi-zone spec; industry commenter worried about corner-cutting. Shows quoting is a multi-quote, price-uncertain process for homeowners, but NOT contractor-side quoting burden.
   **Confidence:** plausible (Reddit thread URL verified via syndication; thread date not verified)

2. **URL:** https://probuildhomeservices.com/blog/how-long-heat-pump-install-take-massachusetts/
   **Date:** published 2026-04-24, updated 2026-05-03 (shown on page)
   **What it shows:** Vendor blog: "Mass Save HPC scheduling lead time (4-6 weeks for in-demand contractors during peak season)"; Manual J + design phase 1-2 weeks; permit pull 5-15 business days. Evidence of long quote-to-install pipeline, but it is self-promotional SEO content (Pro Build sells "Get a Real Quote in 5 Minutes... Mass Save filed for you").
   **Confidence:** plausible (single vendor source, marketing intent)

3. **URL:** https://masshvac.com/resources/mass-save-rebate-claim-process/
   **Date:** "Last updated 2026-09-19" (shown on page)
   **What it shows:** Each Mass Save-qualifying quote must include ACCA Manual J load calc, HPQPL-listed make/model, line-item pricing, stated rebate amount; quotes without Manual J "will not qualify." Documents that quoting in MA is now compliance-heavy. Same SEO-editorial caveat as #2.
   **Confidence:** plausible (single editorial source; rules plausible but not cross-checked against masssave.com primary docs)

4. **Crowding check (mandatory):**
   - https://homewiseai.org/resources/mass-save-ready-heat-pump-proposal — "How to Build a Mass Save-Ready Heat Pump Proposal" (helper already exists; no date shown) — plausible
   - https://payaca.com/us/heat-pump-installer-software — heat-pump-specific installer software: "Load calcs live in PDFs, not your quotes... Pull system designs from your load calc tool straight into Payaca proposals" (no date) — plausible
   - https://getconduit.com/ — LiDAR 3D scans + ACCA Manual J load calcs + proposals for HVAC pros (no date) — plausible
   - https://www.resolvrebates.com/ — Resolv: "Energy Rebate Filing... files the claims start to finish... AI-powered filing from your project docs & photos" for contractors (no date) — plausible
   - https://resources.instafill.ai/docs/hvac-construction/hvac-rebate-application-guide — Instafill.ai auto-populating utility rebate forms from invoice/AHRI data (no date) — plausible
   - Generic CRMs (ServiceTitan, Jobber, Housecall Pro) already serve HVAC quoting (named by Payaca page itself).

5. **Contractor-voice first-person complaint about quoting/proposal load: NOT FOUND.** Phrasings tried: (a) "Mass Save heat pump installer backlog quotes waiting homeowners Reddit"; (b) "HVAC contractor Massachusetts heat pump quoting proposal paperwork too busy forum"; (c) site:reddit.com r/HVAC "Mass Save" contractor paperwork (failed — returned R-project homepage); (d) HVAC-Talk Massachusetts rebate payment/paperwork complaints (no hits); (e) "too busy"/"can't get quote" reddit phrasing (no hits). Homeowner-side wait traces exist indirectly (Pro Build 4-6 week HPC scheduling) but no dated first-person contractor complaint located in this round.

### VERDICT: WEAK
Pain is inferable from program structure (Manual J + HPQPL + HPIN compliance inside every quote; 4-6 week scheduling) and the space is already crowded with quoting/rebate-filing SaaS, but no dated first-person contractor complaint was found this round. Weakest of the three.

---

## R5 [Energy] Condo EV-charger installation process pain (MA right-to-charge)

### Findings

1. **URL:** https://hoaweekly.com/massachusetts-latest-right-to-charge-60-day-deemed-approval/
   **Date:** 2026-09-10 (shown on page)
   **What it shows:** M.G.L. c. 183A §10A (added by Ch. 239 of Acts of 2024, approved 2024-11-20; EOHLC notice 2025-02-26 says no regulations will be filed — statute stands alone). Board must approve/deny in writing within 60 days or application "shall be deemed approved"; binds HOAs/co-ops too. Legal framework confirmed; the paywalled analysis implies boards are still catching up ("the provision most boards still miss is a deadline that runs against them").
   **Confidence:** verified (statutory citations consistent across two independent sources — HOA Weekly and hoaweekly.com/massachusetts-ev-charging/)

2. **URL:** https://newenglandcondo.com/article/qa-ev-use-charging-ahead
   **Date:** not shown on page fetched (undated)
   **What it shows:** MA condo attorneys Mark Einhorn and Matthew Gaines (Marcus, Errico, Emmer & Brooks, Braintree): boards are "seeing a surge of requests from owners to install chargers, as well as being overwhelmed with how to handle these requests." Closest professional-voice pain statement found. Article likely 2025 (references §10A enacted "last year") — not verified.
   **Confidence:** plausible (quote verified verbatim; publication date not verified)

3. **URL:** https://www.thecooldown.com/green-home/ev-charging-station-hoa-condo-restrictions/ (citing https://www.reddit.com/r/legaladvice/comments/1fcrgs7/condo_association_not_allowing_ev_charging_from/)
   **Date:** The Cool Down image assets dated 2025/04; Reddit post date not verified (post ID format suggests ~2024)
   **What it shows:** First-person MA condo owner: "We have recently purchased an EV and would like to charge it from our home... We do not have a covered garage"; condo association vetoed window-cord charging. First-person trace, but the pain is association refusal, not the approval/installation process itself.
   **Confidence:** plausible (article and quoted post verified; original Reddit date unverified)

4. **URL:** https://www.acton-ma.gov/DocumentCenter/View/10268/FAQ-for-Condo-Owners-re_-EV-Charging-Equipment
   **Date:** not shown
   **What it shows:** Town of Acton publishes a municipal FAQ specifically for condo owners on EV charging equipment — evidence that the process is confusing enough that a municipality writes guidance. PDF body could not be parsed (raw PDF bytes in search result).
   **Confidence:** plausible (URL verified in two separate searches; content not read)

5. Additional phrasings tried for first-person dated traces (board approval delays, electrician coordination): r/massachusetts/r/boston EV charger condo (no direct hits); "condo EV charger HOA denied months Reddit 2024 2025" (only general guides, e.g., https://evchargerinstallhub.com/blog/apartment-condo-ev-charging-laws/ updated 2026-10-23, which lists MA §10A among 17 state right-to-charge laws — market context, not pain trace). Third phrasing returned no first-person MA board-delay stories.

### VERDICT: WEAK
Strong legal framework (verified §10A, 60-day deemed approval, effective Feb 2025) plus one professional quote ("boards... overwhelmed with how to handle these requests") and one first-person MA condo-owner post, but no dated first-person trace of the board-approval/electrician-coordination grind itself. Opportunity may exist in the gap between the new statute (Feb 2025) and boards that don't know it — but evidence is thin.

---

## R10 [Energy] Mass Save rebate/incentive paperwork pain (homeowners + small contractors)

### Findings

1. **URL:** https://www.cbsnews.com/boston/news/mass-save-heat-pump-rebates-delays-i-team/
   **Date:** December 10, 2021 (shown on page)
   **What it shows:** WBZ I-Team, named homeowners: John Semas (Norfolk) took over a year to get his ~$6,000 rebate on a >$25,000 system — "It ended up being complete chaos and disorganization"; Michael Kozuch (Provincetown) spent 6+ months on a $250 rebate. Acadia Center's Amy Boyd: "If it's proving difficult for people to actually receive rebates, then we need to fix that administrative system." Semas only got paid after the news contacted Mass Save.
   **Confidence:** verified

2. **URL:** https://www.cbsnews.com/boston/news/i-team-mass-save-rebate-program-changes/
   **Date:** December 18, 2023 (shown on page)
   **What it shows:** Follow-up I-Team: rebate backlog persisted ~6 months after Mass Save hired a new payment processor; "dozens of homeowners contacted WBZ"; named complainers Barry Rubin ($10,000 HEAT loan to repay: "They need to get off their tushies and get going") and Edward Griffin ("It does feel like a scam... we don't have the money"). House chair Rep. Jeffrey Roy set a mid-2024 deadline. Only after the I-Team intervened did the featured families get $10,000 checks via FedEx overnight.
   **Confidence:** verified

3. **URL:** https://www.bostonglobe.com/2026/09/22/metro/mass-save-fraud-contractor-8-million/ (corroborated by https://www.wcvb.com/article/contractor-accused-stealing-millions-taxpayer-funded-mass-save-program/73840420 and https://www.contractingbusiness.com/industry-news/news/55407562/hvac-contractor-hit-with-lawsuit-claiming-rebate-fraud)
   **Date:** 2026-09-22 (Boston Globe URL date); WCVB "this week" relative to suit
   **What it shows:** Mass Save sponsors (National Grid, Eversource, Cape Light Compact JPE) sued MWD Heating & Air Conditioning / owner Mark Dyszczyk (Plymouth Superior Court, filed 2026-09-21 per masssave.com FAQ) for $7.7M in allegedly false heat-pump rebate claims; 220 sites inspected after red flags April 2026; contractor suspended May 2026. Rebate paperwork/verification regime is now under intense scrutiny — "Strengthening Oversight and Consumer Protections" program update posted 2026-09-23 on masssave.com. Raises documentation burden for honest small contractors.
   **Confidence:** verified (three independent outlets + masssave.com FAQ notice)

4. **URL:** https://www.wbur.org/news/2026/06/01/mass-save-energy-efficiency-affordability-eversource-national-grid (URL seen cited from homepros.news; not fetched directly)
   **Date:** 2026-06-01 (in URL)
   **What it shows:** Lawmakers clash over Mass Save's $1.5B annual price tag; House voted to slash funding, Senate to preserve. Program under political pressure → more compliance/paperwork churn likely.
   **Confidence:** unverified (not fetched directly)

5. **Paperwork detail (secondary, SEO-editorial):** https://probuildhomeservices.com/blog/how-long-does-mass-save-rebate-take-arrive/ (pub 2026-04-23): rebate filing requires photos + AHRI cert + Manual J + permit + invoice; "Most delays trace to incomplete filing"; 6-10 weeks total. https://masshvac.com/resources/manual-j-load-calculation/ (updated 2026-09-19): "installers who skip [Manual J] forfeit the rebate." Confidence: plausible.

6. **Existing helpers (crowding note):** Resolv (https://www.resolvrebates.com/, AI rebate filing for contractors), Instafill.ai rebate-form autofill, Homewise AI Mass Save-ready proposals, plus contractor-side "Mass Save filed for you" marketing (Pro Build). Homeowner-side helpers thinner than contractor-side.

### VERDICT: TRACE FOUND
Strongest hypothesis: multiple dated, named first-person complaints (2021 I-Team, 2023 I-Team follow-up), a documented backlog + processor replacement, and a fresh 2026 fraud/oversight wave that is increasing documentation requirements. Note: partially crowded on the contractor-helper side (rebate-filing automation SaaS already exists).

---

## Summary verdicts

- **R4 (heat-pump quoting bottleneck): WEAK** — compliance-heavy quoting inferable; no first-person contractor complaint found; quoting/rebate SaaS already crowded.
- **R5 (condo EV charger): WEAK** — verified new statute + "boards overwhelmed" attorney quote; first-person process traces thin.
- **R10 (Mass Save rebate paperwork): TRACE FOUND** — dated, named complaints (CBS 2021-12-10; 2023-12-18), backlog documented, 2026 fraud suit raising verification burden; contractor-side helpers already exist.
