# Tasks: n1-311triage

Spec: `.kiro/specs/n1-311triage/` (requirements.md, design.md). Tests: `.venv/bin/python -m pytest -q`.
Branch: `n1-311triage` (worktree `../sundai_hack-311`). Scaffold (FastAPI + /api/health) is inherited from main.
Tasks marked HUMAN are not dispatched to executors.

- [x] H1 (HUMAN): Download Boston 311 exports in a browser
  - Files: data/raw/311.csv, data/raw/311_legacy_2026.csv
  - Done when: both files saved (new system 75,851 rows; legacy 2026 190,668 rows); schemas confirmed and recorded in design.md "Raw schemas".
  - Depends on: none

- [ ] T1: Fixtures + 311 row normalizer (both schemas)
  - Files: tests/fixtures/311_new_sample.csv, tests/fixtures/311_legacy_sample.csv, app/cases.py, tests/test_cases.py
  - Done when: each fixture has ~25 rows using the exact header of its raw file (design.md "Raw schemas") incl. missing on_time, no coords, out-of-bbox coords, bad dates, `&amp;` in legacy addresses, both timestamp formats; `normalize_new(row)` / `normalize_legacy(row)` return the canonical fields (on_time True/False/None, lat/lon None when invalid, tz-aware open_date, `system` = "new"/"legacy"); `load_cases(path)` reads `data/311_slice.json`; hypothesis test: on_time is always in {True, False, None}.
  - Depends on: none

- [ ] T2: Geo helpers
  - Files: app/geo.py, tests/test_geo.py
  - Done when: `haversine_m`, `in_bbox`, `point_in_polygon(lon, lat, rings)` (holes handled) implemented; property tests: distance ≥ 0 and symmetric; random points inside/outside a known square classified correctly.
  - Depends on: none

- [ ] T3: Params file + SLA stats + chronic ranking
  - Files: data/params.json, app/sla.py, tests/test_sla.py
  - Done when: `params.json` holds the design.md defaults (incl. resident filter `exclude_sources`) with `"placeholder": true`; `group_stats(cases)` returns total/open/known/late/rate; `chronic(cases, min_n)` returns top 3 + too-few list per design.md ordering; property tests: 0 ≤ rate ≤ 1, late ≤ known ≤ total, ranking non-increasing and never below min_n.
  - Depends on: none

- [ ] T4: Duplicate clustering
  - Files: app/cluster.py, tests/test_cluster.py
  - Done when: `cluster(cases, dist_m, days)` implements the design.md greedy rule using `app/geo.haversine_m`; skips unmapped rows; property tests: partition, single category per cluster, every member within dist and window of seed, order-independent output.
  - Depends on: T2

- [ ] T12: Neighborhood + category name maps
  - Files: data/neighborhood_map.json, data/category_map.json, app/names.py, tests/test_names.py
  - Done when: both JSON files implement the design.md maps (category list completed for every raw value with ≥ 200 resident rows, computed from data/raw/ and the count recorded per entry; each entry `"placeholder": true`); `canon_neighborhood(raw)` / `canon_category(raw)` fall back per design.md ("UNKNOWN" / raw name); tests: every seed pair from design.md maps correctly, unknown values pass through, property test that canon_* is idempotent.
  - Depends on: none

- [ ] T5: Slim script merging both exports
  - Files: scripts/slim_311.py, tests/test_slim.py
  - Done when: reads both raw files via `app/cases.py` normalizers, applies the resident filter from params.json and `app/names.py` maps, keeps open_date ≥ 2026-01-01, rounds coords to 5 dp, writes `data/311_slice.json` plus a printed summary (rows per system, excluded by source, per-month counts); exits non-zero with a clear message naming any missing required column; test runs it on both T1 fixtures into a tmp dir and checks row counts and the filter.
  - Depends on: T1, T3, T12

- [ ] T6: EJ2020 Boston fetch + loader + assignment
  - Files: scripts/fetch_ej2020_boston.py, data/ej2020_boston.json, app/equity.py, tests/test_equity.py, tests/fixtures/ej_sample.json
  - Done when: script pages through MassGIS EJ2020 for Boston with geometry (outSR=4326, coords rounded to 5 dp) and the cache is committed; executor reports the real field names for the language-isolation flag; `load_block_groups()` normalizes LIMENGHHPCT to 0–100; `assign(cases, bgs)` sets `geoid` via `app/geo.point_in_polygon` with bbox prefilter; offline tests on a 3-polygon fixture.
  - Depends on: T2

- [ ] T7: EJ vs non-EJ comparison
  - Files: app/overlay.py, tests/test_overlay.py
  - Done when: `compare(cases, bgs, params)` returns late/known/rate for limited-English EJ vs other, or "NOT ENOUGH DATA TO COMPARE" below min_n; property test: the two groups' known counts sum to the number of assigned cases with known SLA.
  - Depends on: T3, T6

- [ ] H2 (HUMAN): Run slim on the real export and pick the demo neighborhood
  - Files: data/311_slice.json, data/params.json
  - Done when: `.venv/bin/python scripts/slim_311.py` produced the slice (< 15 MB); human reviewed per-neighborhood stats/equity output split by system (lead can print it), confirmed thresholds, resident filter, and both name maps; `placeholder` set to false.
  - Depends on: H1, T5, T7, T12

- [ ] T8: API routes
  - Files: app/server.py, tests/test_api.py
  - Done when: all routes in design.md work using T1–T7 modules; data loaded once at startup; unknown neighborhood/cluster → 404; TestClient tests pass offline against fixture data (path overridable by env var).
  - Depends on: T1, T3, T4, T6, T7

- [ ] T9: SVG map module
  - Files: app/static/map.js, tests/test_static_map.py
  - Done when: `drawMap(svg, data)` projects lon/lat to the SVG viewBox (equirectangular with cos(lat) scaling), draws block-group outlines and cluster markers (square = has late, circle = all on time, size by count) with a text legend; no external URLs; test asserts no `http` URLs and that the legend text exists.
  - Depends on: T8

- [ ] T10: Page + styling + wiring
  - Files: app/static/index.html, app/static/style.css, app/static/app.js, tests/test_static.py
  - Done when: page at `/` implements the design.md layout and requirements 16–19; uses map.js; clusters have a table equivalent; test asserts caveat text present, no CDN URLs, `border-radius` only ever 0, every `<th>` has `scope`.
  - Depends on: T8, T9

- [ ] T11: README + demo flow test
  - Files: README.md, tests/test_demo_flow.py
  - Done when: README has install / run / test / data-refresh steps (incl. the manual browser download), data sources + licenses, the 60 s demo script, and the no-auth note; demo-flow test runs neighborhoods → neighborhood → clusters → cluster rows via TestClient.
  - Depends on: T8
