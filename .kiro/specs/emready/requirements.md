# Requirements: emready — "Who gets missed" emergency outreach list

Source: team research shortlist (idea #4, "who gets missed").
Track: Civic Action — Stronger Community Emergency Readiness.

## User story
As a municipal emergency manager or community-org coordinator, I want a ranked list of the
block groups in my town that are hardest to reach (limited-English, low-income) when a coastal
flood is coming, so that I can send door-knock and translated outreach to them first.

## Acceptance criteria (EARS)

### Trigger
1. WHEN the user opens the app THE SYSTEM SHALL show the current Boston tide reading (NOAA station 8443970, ft MLLW), the NWS flood category it has reached (BELOW / MINOR ≥12.50 / MODERATE ≥14.49 / MAJOR ≥16.00 ft MLLW), labeled "NWS thresholds", plus the caveat that this is a still-water trigger signal, not a flood guarantee.
2. IF the live NOAA request fails or takes longer than 5 s THEN THE SYSTEM SHALL use the cached tide reading and show a banner "CACHED DATA — <timestamp>".
3. WHEN the user selects a past event in Replay mode THE SYSTEM SHALL use that event's cached tide peak and FEMA declaration instead of live data.

### Outreach list
4. WHEN the user selects a town THE SYSTEM SHALL list every EJ block group in that town, ordered by the priority rule in design.md.
5. THE SYSTEM SHALL show the raw values used for ranking (limited-English household %, median household income, population) on every row. No hidden composite score.
6. WHEN a row is shown THE SYSTEM SHALL show which rule decided its position (e.g. "ranked by limited-English %; tie broken by income").
7. IF a block group is missing a ranking field THEN THE SYSTEM SHALL list it at the bottom marked "DATA MISSING", never drop it.
8. WHEN the user clicks "Download CSV" THE SYSTEM SHALL download exactly the rows and columns shown.

### Context
9. WHEN an event is active THE SYSTEM SHALL show the hazard-context text for its incident type from the human-curated table, with its source.
10. WHEN the user selects a town THE SYSTEM SHALL list past MA FEMA declarations for that town's county (title, date, incident type).

### Safety
11. THE SYSTEM SHALL NOT generate alert or message text for residents. It outputs a list for a human to act on.
12. THE SYSTEM SHALL show on every screen: "Planning aid only. Not an official alert. Verify with NWS / MEMA."

### Readability (applies to every screen)
13. THE SYSTEM SHALL use dark text on a white background with contrast ≥ 7:1, base font ≥ 18px, and no dark theme.
14. Every clickable element SHALL be a rectangular button or link with a visible 2px border, a text label, and a visible keyboard focus outline. No rounded corners, no icon-only buttons.
15. THE SYSTEM SHALL NOT use color as the only signal; status uses words ("THRESHOLD CROSSED", "CACHED DATA").
16. THE SYSTEM SHALL work with keyboard only (Tab / Enter) and table headers SHALL use `<th scope>`.

## Properties (property-based tests)
- Ranking output is a permutation of the input block groups (none dropped, none duplicated).
- Ranked rows with complete data are non-increasing in limited-English %; ties are non-decreasing in income.
- Rows with missing data always come after rows with complete data.
- Trigger: flood category is monotonic in water level (a higher level never gives a lower category).
- Datum: for every threshold, STND − 3.53 == MLLW (guards against mixing datums).
- CSV export row count equals the displayed row count.

## Out of scope
- Writing or sending alert messages (liability).
- Full GIS inundation modeling; "exposed towns" is a curated coastal-town list.
- Hazards other than coastal flood.
- Naming which languages to cover (v1 shows limited-English % only).
- A map (tables only).
- User accounts / login.
