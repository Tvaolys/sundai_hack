# Tasks: emready

Spec: `.kiro/specs/emready/` (requirements.md, design.md). Tests: `.venv/bin/python -m pytest -q`.

- [x] T1: Scaffold Python app + venv + health route
  - Files: requirements.txt, app/__init__.py, app/server.py, tests/__init__.py, tests/test_health.py
  - Done when: `python3 -m venv .venv && .venv/bin/pip install -r requirements.txt` works; pinned fastapi, uvicorn, httpx, pytest, hypothesis; `GET /api/health` returns `{"ok": true}`; test passes.
  - Depends on: none

- [ ] T2: Fetch + load EJ2020 block groups
  - Files: scripts/fetch_ej2020.py, data/ej2020_bg.json, app/ej.py, tests/test_ej.py
  - Done when: script pages through MassGIS EJ2020 and writes all MA block groups; `load_block_groups()` returns dicts with geoid, town, lim_eng_pct (0–100), income (None if missing/sentinel), population; tests cover pct-scale normalization and sentinel→None, offline.
  - Depends on: T1

- [ ] T3: Fetch + load OpenFEMA MA declarations
  - Files: scripts/fetch_fema.py, data/fema_ma.json, app/fema.py, tests/test_fema.py
  - Done when: cache holds MA declarations; `declarations_for_county(county)` returns title/date/incidentType sorted newest first, deduped by disasterNumber; offline test passes.
  - Depends on: T1

- [ ] T4: Tide reading with live→cache fallback + trigger
  - Files: scripts/fetch_tide.py, data/tide_cache.json, data/thresholds.json, app/tide.py, tests/test_tide.py
  - Done when: `data/thresholds.json` holds the NWS + NOS table from design.md in both STND and MLLW, with the 3.53 ft offset, source URLs and date; `app/tide.py` loads MLLW values only and fetches observations with `datum=MLLW`; `get_status()` returns level, flood_category (BELOW/MINOR/MODERATE/MAJOR, NWS), thresholds, source, timestamp; live call has 5 s timeout and falls back to cache on any error; tests: STND − offset == MLLW for every row (catches datum mixups), 12.49 → BELOW and 12.50 → MINOR, property test that category is monotonic in level; network mocked.
  - Depends on: T1

- [ ] T5: Curated context files + loader
  - Files: data/coastal_towns.json, data/hazard_context.json, data/replay_events.json, app/context.py, tests/test_context.py
  - Done when: loader returns towns (with county), hazard text by incidentType, replay events; uses the 8 towns and 2 events listed under "Decisions" in design.md; town-name normalization tested ("Manchester-By-The-Sea " == "manchester-by-the-sea"). Every curated entry carries `"placeholder": true` until a human confirms it.
  - Depends on: T1

- [ ] T6: Priority rule
  - Files: app/rank.py, tests/test_rank.py
  - Done when: `rank(rows)` implements design.md rule and attaches a `reason` string; hypothesis tests: permutation, ordering, missing-last.
  - Depends on: T1

- [ ] T7: CSV export
  - Files: app/export.py, tests/test_export.py
  - Done when: `to_csv(rows, columns)` returns CSV with header + one line per row; property test row count matches; commas/quotes in town names escaped.
  - Depends on: T1

- [ ] T8: API routes
  - Files: app/server.py, tests/test_api.py
  - Done when: /api/status, /api/towns, /api/events, /api/outreach, /api/outreach.csv work per design.md using T2–T7 modules; unknown town → 404 with message; TestClient tests pass offline.
  - Depends on: T2, T3, T4, T5, T6, T7

- [ ] T9: Readable UI
  - Files: app/static/index.html, app/static/style.css, app/static/app.js, tests/test_static.py
  - Done when: page served at `/` implements the UI layout and readability requirements 12–16 in requirements.md; no external URLs (CDN) in static files; test asserts disclaimer text present and `border-radius` only ever 0.
  - Depends on: T8

- [ ] T10: README run instructions + demo script
  - Files: README.md, tests/test_demo_flow.py
  - Done when: README has install / run / test / refresh-data commands, data sources with licenses, and a 60 s demo script; `test_demo_flow.py` runs Replay event → town → outreach rows → CSV end to end via TestClient.
  - Depends on: T8
