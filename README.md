# Is my block chronically missed?

Boston 311 repeat-report and late-case finder with an equity check.

**Track:** Civic Action — More Responsive Neighborhood Services (311).

Pick a Boston neighborhood and see, from the city's own 311 data: how often cases
miss their SLA, which categories are chronically late, where the same problem gets
reported over and over (collapsed into one hot spot), and whether late service
concentrates in limited-English environmental-justice block groups. Everything runs
offline from cached data.

## Quick start

```bash
# 1. Install (local venv — never global)
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt

# 2. Run the app
.venv/bin/uvicorn app.server:app
#   -> http://127.0.0.1:8000

# 3. Run the tests (fast, offline, against committed fixtures)
.venv/bin/python -m pytest -q
```

## 60-second demo

The flow judges must see (see `.kiro/specs/n1-311triage/design.md` "Demo"):

1. Select **Downtown**. The raw equity box shows a big gap — late rate in
   limited-English EJ block groups is far above the rest. Then look at the
   **category-mix-adjusted** excess: it nearly vanishes (+0.5 pt). The raw gap is
   almost entirely *what people report there* (≈950 Illegal Parking cases), not
   slower service. The tool is honest about this.
2. Select **Roslindale**. Here the gap **survives** the adjustment (+4.3 pt excess,
   small n, clearly labeled) — a real pattern worth raising.
3. Scroll to the map: repeat reports of the same problem collapse into single
   markers sized by report count.
4. Open the top **Illegal Parking** cluster (35 reports, 20 late) to see the raw
   rows behind it: case id, open date, status, on-time, address.

## How the numbers work

- **Late rate** = `late / (on-time + late)`. Cases with a missing/unparseable
  `on_time` are counted as "SLA UNKNOWN" and excluded from the rate, never silently
  treated as on-time. Every rate is shown with its numerator and denominator,
  e.g. `41% (82 of 200)` — there is no composite score.
- **Repeat-report clusters.** A report joins an existing cluster if it has the
  **same category**, is within **50 m** of the cluster seed, and opened within
  **14 days** after the seed. Seeds are taken in `open_date`, then `case_id` order
  (deterministic, single greedy pass). Every mapped report belongs to exactly one
  cluster; the UI lists clusters with ≥2 reports, largest first.
- **Limited-English EJ flag.** Each mapped report is assigned to a MassGIS EJ2020
  block group by point-in-polygon. A block group is "limited-English" when its
  `LIMITEDENGLISH` flag is `E`. The equity box compares the late rate in those
  block groups vs. all other reports in the neighborhood, each with n. Below the
  minimum count (default 50 known-SLA reports) it shows "NOT ENOUGH DATA TO COMPARE".
- **Category-mix adjustment.** Raw gaps are dominated by what gets reported where,
  so the equity box leads with *excess*, not the raw gap. For each group the
  **expected** late rate is the mean over its cases of the city-wide late rate of
  that case's (category, system); **excess (pt)** = observed − expected.
- **Resident filter.** Legacy rows with `source` ∈ {Employee Generated, City Worker
  App} are staff-generated (mostly parking enforcement), not resident reports, and
  are excluded. The meta endpoint reports how many were dropped and why.
- **Two 311 systems.** Boston is mid-migration. The new BOS311 system (`BCS-…` ids)
  and the legacy 2026 system are merged but treated as disjoint (no cross-file
  dedup). Their SLA definitions differ (legacy ≈38% late vs new ≈25%), so the
  category-mix baseline is computed per `(category, system)` to avoid mixing them
  silently.

## Data refresh

The 311 exports are **not** committed (too large, gitignored). Refresh is manual
because Cloudflare blocks scripted downloads of the portal:

1. In a **browser**, download BOTH exports from data.boston.gov "311 Service
   Requests" and save them to `data/raw/`:
   - the **new** system export → `data/raw/311.csv`
   - the **legacy** 2026 system export → `data/raw/311_legacy_2026.csv`
2. Slim and merge them into the committed slice:
   ```bash
   .venv/bin/python scripts/slim_311.py
   #   -> data/311_slice.json.gz
   ```
   The script fails loudly (non-zero exit, naming the column) if a required column
   is missing from either file.
3. Refresh the EJ2020 block groups (this one *is* scriptable — MassGIS ArcGIS):
   ```bash
   .venv/bin/python scripts/fetch_ej2020_boston.py
   #   -> data/ej2020_boston.json
   ```

Thresholds and name maps live in `data/params.json`, `data/neighborhood_map.json`,
and `data/category_map.json`.

## Data sources & licenses

- **Boston 311 service requests** — City of Boston open data (data.boston.gov).
  Published as open data (ODC-PDDL / public domain dedication); confirm the current
  terms on the portal before redistributing.
- **MassGIS EJ2020 block groups** — MassGIS (Commonwealth of Massachusetts) public
  data, via the ArcGIS service. MassGIS data is published for public use; see the
  portal for the applicable terms.

Where licensing is uncertain, check the source portal rather than assuming.

## Known limitations

- Thresholds (50 m / 14 days / min-n 50), the name maps, and map styling are
  **placeholder defaults pending human confirmation** (`"placeholder": true` in
  `data/params.json`).
- The tool shows a **pattern in the city's own data, not its cause.** A late rate or
  an equity gap is a signal to investigate, not proof of discrimination or of slower
  service.
- Runs on a cached data slice only; there is no live fetch at runtime.

## Security

No authentication. This is a **local demo** — do not deploy it publicly without
adding auth and a hardened deployment.

## Project layout

`app/` is the code (pure analysis modules + a thin FastAPI server and static UI),
`scripts/` holds the one-off data fetchers, `data/` the cached slice and fixtures,
`tests/` the fast offline tests. `.kiro/` holds the spec
(`.kiro/specs/n1-311triage/`) and the agent harness used to build this.
