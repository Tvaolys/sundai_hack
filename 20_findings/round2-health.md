# Round 2 — Healthtech evidence findings (researched 2026-10-24)

## H1 — R3: Food pantry / food-rescue ops pain (volunteer inventory, rescue routes, donor-recipient logistics)

### Pain traces
1. **HN thread on LibreFoodPantry** — https://news.ycombinator.com/item?id=27317709 (thread ~June 2021, id 27317709)
   - Commenter (former soup-kitchen volunteer, ~7 yrs): "Inventory and ordering were tracked with hand-written notes in a binder that the staff leader kept in her car. Are those people going to install and set up open-source software on GitHub... Even the mostly-free solution using GSuite or whatever is past the technical interest and abilities of most of the staff."
   - What it shows: paper/binder-based inventory in volunteer kitchens; UI/tech-adoption gap is the real barrier, not tool absence. Confidence: **verified** (fetched full thread).
2. **VolunteerHub, "The Hidden Cost of Managing Volunteers with Spreadsheets"** — https://volunteerhub.com/blog/the-hidden-cost-of-managing-volunteers-with-spreadsheets (vendor blog; no date seen)
   - "30% of nonprofits still rely on spreadsheets for volunteer management"; anecdote of broken shift sign-ups and broken formulas. Vendor-marketing source, but cites the spreadsheet status quo. Confidence: **plausible** (vendor content, not first-person).
3. **Mission-Ready Tools free "Food Pantry Command Center" spreadsheet** — https://www.missionreadytools.com/food-pantry-command-center (v2.0, October 2026)
   - Pitch copy: "Most pantries run on a few volunteers, a clipboard, and someone's memory." A 2026 free spreadsheet still being published for exactly this gap. Confidence: **verified** (page fetched via search summary).
4. **iHeart podcast "The Invisible Weight of Scheduling Volunteers"** (Small Acts, Big Change, no date seen) — https://www.iheart.com/podcast/53-small-acts-big-change-every-343203184/episode/the-invisible-weight-of-scheduling-volunteers-343532576/
   - Includes a "Sarah's food pantry crisis" anecdote: spreadsheets, missed shifts, last-minute cancellations burning out coordinators. Generic/nonprofit-wide, not pantry-specific ops. Confidence: **plausible**.
5. **MA demand context (not ops pain)** — GBFB 2026 Massachusetts Food Access Report — https://foodaccessreport.gbfb.org/ : 40% of MA households food insecure in 2025 (up from 19% in 2019). Demand-side stat only; no ops-pain testimony seen. Confidence: **verified** (page seen).

### Crowding check (mandatory) — what exists
- **Food Rescue Hero (412 Food Rescue)** — https://foodrescuehero.org/our-product/ + https://412foodrescue.org/412-food-rescues-food-rescue-hero-selected-to-join-ai-for-changemakers-accelerator/ : licensed by **18 food rescue orgs, 52 counties**, 54,000 volunteer drivers, 170M lbs diverted; launched 2016; "fully operational in as little as 30 days." Verified.
- **Rescuing Leftover Cuisine** — LinkedIn company page shows **HQ New York, NY** (11-50 employees, founded 2013); i.e., NOT Boston-based (Boston is a chapter/region). Verified.
- **PantrySoft** — https://pantrysoft.com/ ; pricing via PantryPOS comparison: Light $50/mo (500 households), Standard $75/mo, Deluxe $125/mo. Verified.
- **FoodBank Manager** — $34.95/mo base (per PantryPOS guide, https://pantrypos.0xpi.com/guides/best-food-pantry-software.html, updated 11 Oct 2026). Plausible.
- **PantryPOS** ($39/mo), **PantryOS** (https://thepantryos.com/), **Food Pantry Helper** ($79/yr, https://www.foodpantryhelper.com/), **Serve.Love free volunteer software for food banks** (https://www.serve.love/food-banks/), **Link2Feed**, **Oasis Insight**, plus **LibreFoodPantry FOSS** (GitLab). All seen in results this round. Verified/plausible as noted.
- Food Rescue US: not directly observed this round (unverified).
- **Gap assessment**: sub-$80/yr tools and free spreadsheets already target tiny pantries; the remaining gap is adoption/support for 60-70-year-old volunteer staff (per HN trace), not tool absence.

### VERDICT: **CROWDED** — pain is real and traceable, but the software space is dense (8+ products at every price tier, an FOSS project, and a licensed platform covering food-rescue routing). Residual angle is change-management/UX for tiny volunteer teams, not a greenfield build.
