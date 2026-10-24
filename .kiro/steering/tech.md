# Tech context (always loaded)

## Stack
Python 3.12 + FastAPI + uvicorn backend. Frontend: plain HTML/CSS/JS in `app/static/`
(no framework, no build step, no CDN — everything served locally for an offline demo).

## Layout
app/ = code, app/static/ = UI, scripts/ = one-off data fetchers, data/ = cached JSON
datasets & fixtures, tests/ = tests.
demo/ = the "Who Gets Missed" app (single-file `index.html` + optional `serve.js` helper).

## Commands
- Install: `python3 -m venv .venv && .venv/bin/pip install -r requirements.txt`
- Run app: `.venv/bin/uvicorn app.server:app --reload`
- Run tests: `.venv/bin/python -m pytest -q`

## Testing
- Every task ships with at least one test that runs fast and offline.
- For pure data transforms (parsing, scoring, ranking), add a property-based test
  (Python: hypothesis, JS/TS: fast-check) stating an invariant, e.g. "ranking is a permutation".
- Network-dependent code reads from a cached file in data/ during tests.
