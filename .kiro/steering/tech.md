# Tech context (always loaded)

## Stack
<TODO: e.g. Python 3.12 + FastAPI backend, React + Vite frontend>

## Layout
<TODO: e.g. app/ = code, tests/ = tests, data/ = cached datasets & fixtures>
Planning research (00_INDEX.md, 10_seeds.md, 20_findings/, 30_candidates/, 40_shortlist.md,
report/) is reference material. Do not edit it while implementing.

## Commands
- Install: <TODO>
- Run app: <TODO>
- Run tests: <TODO, e.g. `python3 -m pytest -q`>

## Testing
- Every task ships with at least one test that runs fast and offline.
- For pure data transforms (parsing, scoring, ranking), add a property-based test
  (Python: hypothesis, JS/TS: fast-check) stating an invariant, e.g. "ranking is a permutation".
- Network-dependent code reads from a cached file in data/ during tests.
