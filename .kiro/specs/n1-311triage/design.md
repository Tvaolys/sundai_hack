# Design: n1-311triage

## Approach
Same stack as the rest of the repo: Python 3.12 + FastAPI, one static page (plain HTML/CSS/JS,
no framework, no CDN). All data is cached in `data/` and committed, so the demo runs offline.
All analysis is pure Python functions with property tests; the server only wires them together.
The map is a hand-drawn SVG (lon/lat → x/y) of EJ2020 block-group outlines plus cluster
markers — no Leaflet, no tiles, so nothing breaks without Wi-Fi.

## Components & files
- `app/cases.py` — load + normalize 311 rows from `data/311_slice.json`
- `app/geo.py` — haversine, point-in-polygon, bbox check (pure)
- `app/equity.py` — load EJ2020 Boston block groups (+ geometry), assign report → block group
- `app/cluster.py` — duplicate-report clustering (pure)
- `app/sla.py` — late-rate stats, chronic-category ranking (pure)
- `app/overlay.py` — EJ vs non-EJ late-rate comparison (pure)
- `app/server.py` — routes, serves `app/static/`
- `app/static/index.html`, `style.css`, `app.js`, `map.js` — UI
- `scripts/slim_311.py` — raw CSV (gitignored) → `data/311_slice.json`
- `scripts/fetch_ej2020_boston.py` — MassGIS EJ2020 query → `data/ej2020_boston.json`
- `tests/fixtures/311_sample.csv` — ~40 hand-made rows incl. edge cases; all tests use this

Module names deliberately differ from emready (`app/ej.py` etc.) so the branches never collide.

## Data
| File | Source | Key fields | Owner |
|---|---|---|---|
| `data/raw/311.csv` (gitignored) | data.boston.gov "311 Service Requests", downloaded in a browser (Cloudflare blocks curl) | full export | human |
| `data/311_slice.json` | `scripts/slim_311.py` | case_id, open_date, close_date, service_name, case_status, on_time, neighborhood, ward, full_address, latitude, longitude | script |
| `data/ej2020_boston.json` | MassGIS EJ2020 ArcGIS (LIVE), `MUNICIPALITY='Boston'`, `outSR=4326`, with geometry | GEOID, LIMENGHHPCT, PCT_MINORITY, BG_MHHI, EJ criteria flags, rings | script |
| `data/params.json` | human-tuned thresholds (below) | | human |

Schema is UNVERIFIED for the export the human downloads (the new 311 system and the legacy
2011–2024 export differ: e.g. `on_time` "ONTIME"/"OVERDUE" vs other spellings; `latitude`/`longitude`
vs `lat`/`long`). The slim script maps known aliases to the canonical names above and fails loudly
on anything it cannot map. `cases.py` normalizes `on_time` to `True` (on time), `False` (late), `None` (unknown).

## Rules (PLACEHOLDER defaults in `data/params.json` until a human confirms)
- Duplicate rule: same `service_name`, within **50 m** of the cluster seed, opened within **14 days**
  after the seed. Seed order: by open_date, then case_id (deterministic). Greedy single pass.
- Minimum count for a category to be ranked / a group to be compared: **20** reports with known SLA.
- "Limited-English EJ block group": EJ2020 language-isolation criterion flag if present in the
  schema; otherwise `LIMENGHHPCT ≥ 25`. Executor must check the real field names and report.
- Late rate = late / (on-time + late). Unknown excluded (req 2).
- Chronic ranking: late rate desc, then late count desc, then service_name asc.

## API
- `GET /api/meta` → data window, source, row counts, params in use
- `GET /api/neighborhoods` → list with total counts
- `GET /api/neighborhood?name=X` → stats (req 5), chronic top 3 + too-few list, equity comparison
- `GET /api/clusters?name=X` → clusters (id, service_name, size, late count, centroid) largest first
- `GET /api/cluster/{id}` → raw rows of that cluster
- `GET /api/map?name=X` → block-group rings + cluster markers for that neighborhood (lon/lat; JS projects)
Unknown neighborhood / cluster → 404 with message.

## UI layout (single page, top to bottom)
1. Header: title, data window + source (req 4).
2. Neighborhood dropdown (`<label>`) + [Show neighborhood] button.
3. Stats box: total / open / known / late / late rate (with n).
4. Chronic categories table: Rank | Category | Late rate | Late | Known.
5. Equity box: EJ-limited-English vs other — late rate with n each, caveat text (req 15).
6. Map (SVG) + legend; below it the same clusters as a table (req 19).
7. Clusters table: Category | Reports | Late | First / last date | [Show reports] → raw rows.
Style: white bg, #111 text, 18px+, 2px solid borders, `border-radius: 0`, focus outline 3px.
Markers: late = filled square (#b00020), on-time = hollow circle (#1a5e1a).

## Demo (60 s)
Pick the neighborhood the human chose → stats line → "top chronic category is X, 41% late (82/200)"
→ map shows one big cluster of N duplicate reports collapsed to one marker → open it, raw rows
→ equity box: late rate in limited-English EJ block groups vs others, with counts and the caveat.

## Risks
- Cloudflare: no runtime fetch; the human downloads in a browser. Without this file the demo
  has only fixture data → H1 is the critical path.
- The headline might not exist in real data. H2 checks before the UI is polished; if no
  neighborhood shows an equity gap, the demo leads with clusters + chronic categories and
  reports the equity result honestly ("no gap found" is still a valid finding).
- Raw export may be 100+ MB → slim to needed columns and a 12-month window; target < 15 MB committed.
- EJ2020 paging (maxRecordCount) → `resultOffset` loop. Geometry size → round coords to 5 decimals.
- Point-in-polygon on ~100k points × ~600 polygons → bbox prefilter per polygon; precompute at load.
- The server has no auth. Fine for a local demo; do not deploy publicly without it.
