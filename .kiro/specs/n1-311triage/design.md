# Design: n1-311triage

## Approach
Same stack as the rest of the repo: Python 3.12 + FastAPI, one static page (plain HTML/CSS/JS,
no framework, no CDN). All data is cached in `data/` and committed, so the demo runs offline.
All analysis is pure Python functions with property tests; the server only wires them together.
The map is a hand-drawn SVG (lon/lat → x/y) of EJ2020 block-group outlines plus cluster
markers — no Leaflet, no tiles, so nothing breaks without Wi-Fi.

## Components & files
- `app/cases.py` — load + normalize 311 rows from `data/311_slice.json.gz`
- `app/geo.py` — haversine, point-in-polygon, bbox check (pure)
- `app/equity.py` — load EJ2020 Boston block groups (+ geometry), assign report → block group
- `app/cluster.py` — duplicate-report clustering (pure)
- `app/sla.py` — late-rate stats, chronic-category ranking (pure)
- `app/overlay.py` — EJ vs non-EJ late-rate comparison (pure)
- `app/server.py` — routes, serves `app/static/`
- `app/static/index.html`, `style.css`, `app.js`, `map.js` — UI
- `scripts/slim_311.py` — raw CSV (gitignored) → `data/311_slice.json.gz`
- `scripts/fetch_ej2020_boston.py` — MassGIS EJ2020 query → `data/ej2020_boston.json`
- `tests/fixtures/311_sample.csv` — ~40 hand-made rows incl. edge cases; all tests use this

Module names deliberately differ from emready (`app/ej.py` etc.) so the branches never collide.

## Data
| File | Source | Key fields | Owner |
|---|---|---|---|
| `data/raw/311.csv` (gitignored) | data.boston.gov 311, NEW system export (case ids `BCS-…`), browser download | see schema A | human |
| `data/raw/311_legacy_2026.csv` (gitignored) | data.boston.gov 311, LEGACY system export 2026, browser download | see schema B | human |
| `data/neighborhood_map.json` | curated (below) | raw name → canonical | human |
| `data/category_map.json` | curated (below) | raw category → canonical | human |
| `data/311_slice.json.gz` | `scripts/slim_311.py` (both files merged; gzip columnar JSON, 5.5 MB, 150,822 rows) | case_id, system, source, open_date, close_date, category, raw_category, case_status, on_time, neighborhood, ward, address, latitude, longitude | script |
| `data/ej2020_boston.json` | MassGIS EJ2020 ArcGIS (LIVE), `MUNICIPALITY='Boston'`, `outSR=4326`, with geometry | GEOID, LIMENGHHPCT, PCT_MINORITY, BG_MHHI, EJ criteria flags, rings | script |
| `data/params.json` | human-tuned thresholds (below) | | human |

### Raw schemas (CONFIRMED 2026-10-24 from the downloaded files)
Boston is mid-migration between two 311 systems. Neither file alone covers 2026; together they
give a steady ~25k cases/month. Only 21 of 39,880 legacy rows from Jul 2026 on match a new-system
row (same open minute + location) → treat as disjoint, no cross-file dedup.

| Canonical | A: new system (`311.csv`, 75,851 rows, 2025-08-01…2026-10-24) | B: legacy (`311_legacy_2026.csv`, 190,668 rows, 2026-01…2026-10) |
|---|---|---|
| case_id | `case_id` (`BCS-00253943`) | `case_enquiry_id` (`101006630450`) |
| open_date | `open_date` (`2026-07-14 10:56:30.994145+00`, UTC) | `open_dt` (`2026-05-02 09:14:00`, no tz) |
| close_date | `close_date` | `closed_dt` |
| raw_category | `service_name` (77 values) | `type` (150 values) |
| case_status | `case_status` (Closed / In progress / …) | `case_status` (Closed / Open) |
| on_time | `on_time` ONTIME / OVERDUE | `on_time` ONTIME / OVERDUE |
| source | `report_source` (BOS311 / Call / Email) | `source` (Citizens Connect App / Constituent Call / Employee Generated / City Worker App / Self Service) |
| neighborhood | `neighborhood` | `neighborhood` |
| ward | `ward` | `ward` |
| address | `full_address` | `location` (HTML-escaped, e.g. `&amp;` → unescape) |
| latitude / longitude | `latitude`, `longitude` | `latitude`, `longitude` |

Both files have 0 blank `on_time`; ~0.1–0.2% lack coordinates. `cases.py` still normalizes
`on_time` to `True` / `False` / `None` defensively. The slim script fails loudly if a required
column is missing from either file. Dates: legacy timestamps are naive local time — parse both
to timezone-aware America/New_York before windowing; tests cover both formats.
Status: "Closed" → closed; everything else → open.

### Resident filter (PLACEHOLDER, in params.json)
Exclude legacy `source` ∈ {"Employee Generated", "City Worker App"} — 53% of legacy rows, mostly
parking enforcement written by staff, not resident reports. Leaves ~155k rows total. The meta
endpoint shows how many were excluded and why.

### Neighborhood map (canonical = the coarser name both systems can produce)
- "Allston", "Brighton", "Allston / Brighton" → "Allston / Brighton"
- "South Boston", "South Boston Waterfront", "South Boston / South Boston Waterfront" → "South Boston"
- "Fenway", "Longwood", "Fenway / Kenmore / Audubon Circle / Longwood" → "Fenway / Longwood"
- "Mattapan", "Greater Mattapan" → "Mattapan"
- "Downtown", "Downtown / Financial District", "Chinatown", "Leather District", "Bay Village",
  "West End", "North End" → "Downtown"  (legacy has no separate entries for these)
- "", "Boston", "Chestnut Hill" → "UNKNOWN" (kept in city totals, not selectable)
- every other name maps to itself.

### Category map
Clustering and chronic ranking use `category`, not `raw_category`, so the same problem filed in
either system counts once. Seed pairs (executor completes the list for every raw value with
≥ 200 resident rows; anything unmapped keeps its raw name):
- "Request for Pothole Repair", "BWSC Pothole", "Pothole" → "Pothole"
- "Sidewalk Repair (Make Safe)", "Sidewalk Repair" → "Sidewalk Repair"
- "Improper Storage of Trash (Barrels)", "Improper Trash Storage" → "Improper Trash Storage"
- "Missed Trash/Recycling/Yard Waste/Bulk Item", "Missed Waste Pick-up" → "Missed Waste Pick-up"
- "Illegal Dumping", "Illegal Dumping or Disposal" → "Illegal Dumping"
- "Graffiti Removal", "PWD Graffiti", "Illegal Graffiti" → "Graffiti"
- "Pick up Dead Animal", "Dead Animal General" → "Dead Animal"
- "Request for Snow Plowing", "Snow Plowing" → "Snow Plowing"
- "Parking Enforcement", "Illegal Parking" → "Illegal Parking"
- "Sign Repair", "Damaged/Faded Sign", "Missing Sign", "Missing / Knocked Down Sign", "Knocked Down Sign" → "Sign Repair"
- "Tree Maintenance Requests", "Pruning Request" → "Tree Pruning"
- "Code Enforcement Collection", "CE Collection" → "Code Enforcement Collection"
Every entry carries `"placeholder": true` until a human confirms.

## Rules (PLACEHOLDER defaults in `data/params.json` until a human confirms)
- Duplicate rule: same `category`, within **50 m** of the cluster seed, opened within **14 days**
  after the seed. Seed order: by open_date, then case_id (deterministic). Greedy single pass.
- Minimum count for a category to be ranked / a group to be compared: **50** (raised from 20 after H2) reports with known SLA.
- "Limited-English EJ block group": `LIMITEDENGLISH == 'E'` (CONFIRMED 2026-10-24: 72 of 462 Boston
  EJ block groups). Comparison = reports in those block groups vs. all other reports in the
  neighborhood. NOTE: the EJ2020 layer contains ONLY EJ block groups (all 462 Boston rows have
  EJ='Yes'), so reports outside every polygon are non-EJ areas → geoid None, counted in "other".
  Source: https://arcgisserver.digital.mass.gov/arcgisserver/rest/services/AGOL/EJ2020/MapServer/0
  (maxRecordCount 2000; fields GEOID, MUNICIPALITY, TOTAL_POP, PCT_MINORITY, LIMENGHHPCT, BG_MHHI,
  LIMITEDENGLISH, EJ_CRITERIA, EJ_CRIT_DESC).
- Late rate = late / (on-time + late). Unknown excluded (req 2).
- Category-mix adjustment (added after H2 analysis): for each group, expected late rate =
  mean over its cases of the CITY-WIDE late rate of that case's (category, system). Show
  observed, expected, and excess = observed − expected (percentage points). The equity box leads
  with excess, not the raw gap, because raw gaps are dominated by what people report.
- Chronic ranking: late rate desc, then late count desc, then category asc.

## API
- `GET /api/meta` → data window, source, row counts, params in use
- `GET /api/neighborhoods` → list with total counts
- `GET /api/neighborhood?name=X` → stats (req 5), chronic top 3 + too-few list, equity comparison
- `GET /api/clusters?name=X` → clusters (id, category, size, late count, centroid) largest first
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

## H2 analysis (2026-10-24, lead, on the real slice)
City-wide: limited-English EJ blocks 32.07% late vs other 32.06% — no raw gap.
Per neighborhood (raw late %, LE vs other → excess after category-mix adjustment):
- Downtown (incl. Chinatown): 50.1% (n=2513) vs 36.7% (n=8200) → excess +0.5 vs +2.7 pt.
  The raw gap is almost entirely category mix (950 "Illegal Parking", e.g. Tyler St).
- Roslindale: 43.9% (403) vs 33.8% (5253) → excess +4.3 vs +0.2 pt; same direction in new-system-only data.
- Hyde Park: 34.3% (353) vs 29.8% (3843) → excess +5.8 vs +0.5 pt.
- Dorchester, East Boston, Roxbury: LE blocks do slightly BETTER than other blocks.
Legacy system late rate (~38%) is far above new (~25%) → SLA definitions likely differ; the
adjustment's per-(category, system) baseline absorbs this.
Proposed demo: Downtown first (big raw gap → "but it's the category mix" = the tool is honest),
then Roslindale (a gap that survives adjustment, small n, clearly labeled). Top Downtown cluster:
Illegal Parking, 35 reports, 20 late. min_n raised 20 → 50: at 20, one-off categories
("Planting Request", 20 cases) topped the chronic list.

## Risks
- Cloudflare: no runtime fetch; the human downloads in a browser. Without this file the demo
  has only fixture data → H1 is the critical path.
- The headline might not exist in real data. H2 checks before the UI is polished; if no
  neighborhood shows an equity gap, the demo leads with clusters + chronic categories and
  reports the equity result honestly ("no gap found" is still a valid finding).
- Raw exports are 27 MB + 107 MB → slim to needed columns, window 2026-01-01 … end of data,
  resident filter, coords rounded to 5 dp; target < 15 MB committed (split by neighborhood if over).
- Two systems may measure `on_time` differently (different SLA targets) → overlay and chronic
  tables can show the per-system split on request; never mix silently in the headline without
  checking (H2).
- EJ2020 paging (maxRecordCount) → `resultOffset` loop. Geometry size → round coords to 5 decimals.
- Point-in-polygon on ~100k points × ~600 polygons → bbox prefilter per polygon; precompute at load.
- The server has no auth. Fine for a local demo; do not deploy publicly without it.
