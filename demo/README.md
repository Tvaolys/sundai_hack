# EmReady demo — "Who Gets Missed" (n2-emready)

Runnable demo of the emergency-readiness outreach planner from `40_shortlist.md` (#4)
and `30_candidates/n2-emready.md`.

## What it does
A small MA emergency-management office picks an event, and EmReady answers two questions:
1. **Which flood-adjacent block groups to door-knock first**, ranked on equity.
2. **Which languages** the outreach must cover.

It shows the state hazard ranking for context and a full traceability line — every rank is
a transparent sort on real columns, not a black-box score.

**Safety:** it outputs a prioritized list for a human. It never writes or sends alert text.

## Run it
Zero install. Open `index.html` in a browser, or serve locally:

```powershell
python -m http.server 8000 --bind 127.0.0.1 --directory .
# then open http://127.0.0.1:8000/
```

## Two demo modes
- **Live coastal-flood advisory** — NOAA Boston tide gauge crosses the 11.5 ft flood stage,
  firing the advisory and ranking flood-adjacent block groups.
- **Historical FEMA replay** — pick a past MA declaration (OpenFEMA) and replay who was most
  exposed. This is the reliable fallback if the live trigger is flaky.

Switch the **priority rule** (limited-English / income / CDC SVI) to see the order change.

## Data
`data.js` holds **realistic SAMPLE** MA block-group rows. Field names mirror the real LIVE
sources so the adapters drop in unchanged:

| Source | Fields |
|---|---|
| EJ2020 ArcGIS | `LIMENGHHPCT`, `BG_MHHI`, `PCT_MINORITY` |
| OpenFEMA DisasterDeclarationsSummaries (MA) | historical replay events |
| NOAA tide gauge 8443970 (Boston) | coastal-flood trigger |
| CDC SVI | social-vulnerability percentile |

The numbers are plausible stand-ins for the demo, not official figures. For the hackathon
build, replace `data.js` with live adapter output (see the build plan in the candidate card).
