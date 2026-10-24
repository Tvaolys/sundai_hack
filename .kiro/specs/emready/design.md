# Design: emready

## Approach
Python 3.12 + FastAPI serves a JSON API and one static page (plain HTML/CSS/JS, no framework,
no build step, no CDN). All data is fetched once by scripts into `data/` and committed, so the
demo runs offline. The only live call is the NOAA tide reading, with a cached fallback.
Ranking is a plain sort with visible inputs, not a weighted score.

## Components & files
- `app/server.py` — FastAPI app, routes, serves `app/static/`
- `app/ej.py` — load + normalize EJ2020 block groups from `data/ej2020_bg.json`
- `app/fema.py` — load MA FEMA declarations, filter by county / incident type
- `app/tide.py` — live NOAA fetch (5 s timeout) → cached fallback; `crossed()` trigger
- `app/context.py` — load coastal towns, town→county map, hazard-context table
- `app/rank.py` — priority rule (pure function)
- `app/export.py` — CSV export (pure function)
- `app/static/index.html`, `style.css`, `app.js` — UI
- `scripts/fetch_*.py` — one-off fetchers that write `data/*.json`
- `tests/` — pytest + hypothesis

## Data
| File | Source | Key fields | Owner |
|---|---|---|---|
| `data/ej2020_bg.json` | MassGIS EJ2020 ArcGIS (LIVE) | GEOID, MUNICIPALITY, LIMENGHHPCT, BG_MHHI, PCT_MINORITY, population* | script |
| `data/fema_ma.json` | OpenFEMA `DisasterDeclarationsSummaries?$filter=state eq 'MA'` | disasterNumber, declarationTitle, declarationDate, incidentType, designatedArea | script |
| `data/tide_cache.json` | NOAA CO-OPS datagetter, station 8443970, MLLW, ft | t, v | script |
| `data/replay_events.json` | curated: 2–3 past events (date, tide peak, FEMA disasterNumber) | | human |
| `data/coastal_towns.json` | curated list of exposed towns + county | town, county | human |
| `data/hazard_context.json` | curated from MA Climate Change Assessment | incidentType, text, source | human |

*Population field name in EJ2020 is unverified — executor must check the real schema.

## Priority rule (human-confirmed 2026-10-24)
1. Limited-English household % — descending.
2. Tie: median household income — ascending.
3. Tie: GEOID — ascending (stable, deterministic).
Rows missing (1) or (2) go last, marked DATA MISSING.

## Flood threshold (human-verified 2026-10-24)
Convention: NWS thresholds (what the Weather Service issues advisories against). Label "NWS" on screen.
Source: NOAA CO-OPS MDAPI, station 8443970 —
`https://api.tidesandcurrents.noaa.gov/mdapi/prod/webapi/stations/8443970/floodlevels.json` and `.../datums.json`.
MDAPI floodlevels are on station datum (STND). MLLW = STND − 3.53 ft.

| Level | NWS (ft MLLW) | NOS (ft MLLW) |
|---|---|---|
| Minor | 12.50 | 12.32 |
| Moderate | 14.49 | 13.20 |
| Major | 16.00 | 14.51 |

Frozen in `data/thresholds.json` (both STND and MLLW values, offset, source URL, date).
DATUM RULE: observed water level is fetched with `datum=MLLW`; compare ONLY against MLLW values.
Wiring raw STND values (e.g. 16.03) against MLLW readings means the trigger silently never fires.
Status box shows the level reached: BELOW / MINOR / MODERATE / MAJOR (NWS).
UI caveat text: "Still-water tide threshold. Real flooding also depends on surge, waves, and rain. This is a trigger signal, not a flood guarantee."

## API
- `GET /api/status` → tide reading, threshold, crossed, source (LIVE|CACHED), timestamp
- `GET /api/towns` → coastal towns
- `GET /api/events` → replay events
- `GET /api/outreach?town=X[&event=ID]` → ranked rows + rule text + FEMA history + hazard context
- `GET /api/outreach.csv?town=X[&event=ID]` → same rows as CSV

## UI layout (single page, top to bottom)
1. Disclaimer bar (req 12).
2. Status box: tide level, threshold, "THRESHOLD CROSSED" / "BELOW THRESHOLD", LIVE/CACHED + time.
3. Mode buttons: [Live] [Replay past event] — the selected one shows "SELECTED" text, not just color.
4. Town dropdown (labeled `<label>`), [Show outreach list] button.
5. Outreach table: Rank | Block group | Limited-English % | Median income | Population | Note.
6. [Download CSV] button.
7. Hazard context box, FEMA history table.
Style: white bg, #111 text, 18px+, 2px solid borders, `border-radius: 0`, focus outline 3px.

## Decisions (human, 2026-10-24: "use defaults")
- Languages: DROPPED for v1. Show limited-English % only; no ACS C16002 join.
- Demo towns (PLACEHOLDER until a human confirms): Boston, Revere, Chelsea, Winthrop (Suffolk);
  Quincy (Norfolk); Lynn, Salem (Essex); New Bedford (Bristol).
- Replay events (PLACEHOLDER — dates and FEMA disaster numbers must be confirmed by a human):
  2018-01-04 nor'easter; 2024-01-13 coastal storm. Tide peaks taken from NOAA 8443970 history.
- No map. Tables only.

## Risks (where this can fail)
- EJ2020 ArcGIS URL is not recorded in the research → executor must find it; may be paginated (maxRecordCount ~1000–2000) → fetch with `resultOffset` loop.
- EJ2020 has no "languages spoken" field → languages dropped for v1 (decision above).
- FEMA declarations are county-level, EJ rows are town-level → need town→county map (curated in `coastal_towns.json`).
- `MUNICIPALITY` spelling may not match curated town names (e.g. "Manchester-by-the-Sea") → normalize case/whitespace; test it.
- NOAA live may be slow/down at the venue → 5 s timeout + cache; Replay mode is the main demo.
- LIMENGHHPCT may be 0–1 or 0–100 → detect and normalize in `app/ej.py`, test it.
- Sentinel values (e.g. -999 for income) → treat as missing.
- The server has no auth. Fine for a local demo; do not deploy publicly without it.
