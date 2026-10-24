# Who Gets Missed — Emergency Outreach planner

Idea #4 from the Hackachusetts research report (`report/hackachusetts_research.tex`,
`30_candidates/n2-emready.md`), built on **live public data** for **any US county**.

An emergency is coming — a flood, a heat wave, a winter storm, a power outage. Door-knock teams can only
reach so many homes. The tool shows **who to reach first, in which languages, and who gets missed**
when time runs out.

**Safety:** planning aid only. It never writes or sends alert messages.

## Run it
Open `index.html` in a browser (Chrome, Edge, Firefox). One file, no install, no keys.
Pick a **state** and one or more **counties**, then **Load live data**.

For live **power outages** (Massachusetts only), run the small local helper instead (Node 18+):

```powershell
node demo/serve.js
# Who Gets Missed: http://127.0.0.1:8765/
```

MEMA's outage feed blocks direct browser access, so the helper passes that one feed through. It listens
on 127.0.0.1 only. Everything else works either way.

## Area
| Where | Unit | Source |
|---|---|---|
| Massachusetts | Census block groups | MassGIS EJ 2020 (real limited-English households, median income, EJ status). This layer holds only the block groups that meet an Environmental Justice criterion (548 of Suffolk's 681), so the others are not shown; the page says so. |
| Every other state, DC, Puerto Rico | Census tracts | CDC/ATSDR SVI 2022 (limited-English homes estimated from the share of people) |

Town names on the map come from Census county subdivisions. Big counties (thousands of tracts) take a few
minutes to load flood zones; the page works while they load in the background and caches them.

## Map
The map uses Web Mercator, the same projection as Google, Apple and OpenStreetMap maps, over a USGS
The National Map basemap (public domain, no key; **Topo** or **Imagery**), with official Census county
borders on top. Areas are see-through so streets and coastlines show underneath; untick **Street map** to hide it.
Scroll or pinch to zoom, drag to move, double-click to zoom in, or use **+ / − / Reset**. With the map
focused: `+` `-` `0` and the arrow keys. Click (or press Enter on) a table row to find it on the map.

## Two sections
- **Planning aid** — scenario, door-knock capacity, outreach order, languages, fairness.
- **Resident reports** — add/import reports, the incident queue, the quiet at-risk areas for the current
  planning scenario, and the state/county picker. The same map and area picker move into whichever tab is open.

## Live sources
| Source | Used for |
|---|---|
| NWS active alerts (api.weather.gov) | Live trigger for any hazard, and its area (storm polygon or counties) |
| NWS gridpoint forecast | Heat index, wind chill, wind gusts, snow and ice for the next 2 days; the area's time zone |
| NOAA CO-OPS tide station (nearest within 60 km with flood levels) | Latest tide, 2-day predictions, NWS flood stages, past storm peaks |
| NOAA river gauges (NWPS) | Inland flooding: gauges at or forecast to reach flood stage |
| Open-Meteo air quality (CAMS model) | US AQI forecast (a model, not the official AirNow monitors) |
| MEMA power outages | Customers out per town — Massachusetts only (needs `serve.js`) |
| CDC/ATSDR SVI 2022 (tract) | SVI; % adults 65+, no car, disability, below 150% of poverty |
| FEMA National Flood Hazard Layer | Which flood zones each area touches |
| OpenFEMA disaster declarations | Past storms in the state to replay against the tide |
| ACS 2022 C16001 via Esri Living Atlas (tract) | Language mix of limited-English speakers |

No API keys are needed.

## How it decides
- **Emergency:** pick a type, then a source: a live NWS alert, live conditions, the tide (coastal), a past
  storm replay, or a what-if. Coastal flood only appears near the coast.
- **Who is exposed:** floods use FEMA flood zones; every other hazard counts everyone in the NWS alert area
  (center inside the storm polygon, or whole counties), or the whole selected area for a what-if.
- **Live conditions** (planner rules, shown on the page — not official warnings): heat index ≥ 90°F;
  snow ≥ 6 in, ice ≥ 0.25 in or wind chill ≤ −10°F; gusts ≥ 46 mph; US AQI ≥ 101; a river gauge at or
  forecast to minor flood stage (FEMA flood zones within 5 km of it); towns with ≥ 1% of customers out.
  Below the rule, the page says so and lists no one. Point forecasts cover the whole selected area.
- **Coastal floods:** minor stage → FEMA VE wave zones; moderate → + A zones (1%/yr); major → + 0.2%/yr
  zones. Advisories map to minor, warnings and watches to moderate, storm surge warnings to major.
  Not an inundation model; A zones can include river flood areas.
- **Order:** for floods, **Worst flood zone first** (on by default) puts VE → A → 0.2% first. Then one
  plain sort on one real column (limited-English, income (MA), poverty, SVI, adults 65+, no car,
  disability, or size). Missing values last, ties by ID. No combined score.
- **Capacity:** teams × hours × doors per hour, given out in rank order. The dashed line is where it runs out.
- **Fairness check:** compares your rule with the biggest-first baseline.

## Resident reports
**Live incident reports** load on their own and are watched for changes; the map, queue and plan redraw only when a report is added, removed or changes. There is no refresh button:

| Source | What it is | Kept |
|---|---|---|
| NWS Local Storm Reports (via Iowa Environmental Mesonet) | What spotters, the public, police and emergency managers told the Weather Service | Impact reports only (flooding, damage, wires, rescues, fire, ice). Rain totals, gusts and hail size are skipped. |
| SeeClickFix | Open requests residents filed with their city | Emergency-related only (flooding, wires, trees, gas, ice, blocked roads). Everyday issues are skipped. |
| City 311 / 911 open data | NYC, Chicago, San Francisco, Austin and Boston 311; Seattle Fire 911 dispatch. Used automatically when that county is loaded. | Same emergency rules; closed requests skipped. Seattle medical calls are left out. NYC posts with about a 1–2 day delay. |
| NIFC wildfires (WFIGS) | Active wildfire incidents, US-wide | All active fires in the area, whatever the window |
| USGS "Did You Feel It?" | Earthquakes people reported feeling, US-wide | Epicenters inside the area |

Pick a window from 6 hours up to 90 days, or untick a source. Each source is re-checked once its wait is up (1 min; wildfires 2 min;
SeeClickFix 3 min, as it rate-limits), 5x longer for 7+ day windows, and not while the tab is hidden. SeeClickFix checks at most the newest 2,000 requests in the area and backs off
if the service limits the request rate; the page says when either happens. Each live report links to the original. Live reports
are not stored in the browser; your own reports (added on the map, CSV, sample) are, per area. (RescueMesh idea)
Residents' reports show where people are asking for help — but the people least likely to report are the
ones this tool is built to find. So reports are a second layer, not a replacement:

- **Add** a report by clicking the map, **import** a CSV (`lat, lon`, optional `type, severity, time, note`),
  or **load sample reports** for a demo (clearly marked SAMPLE; they lean toward easy-to-reach areas on purpose).
- **Incident queue:** one plain sort — severity (1 life safety, 2 urgent, 3 routine), then newest first.
  Click a report to find it on the map.
- **Quiet at-risk areas:** exposed, in the top third of the outreach order, and no reports at all. They get
  a dashed red outline, a "Quiet" badge and a count. **Quiet at-risk areas first** sends teams there first.
- Reports stay in this browser (per area), go into snapshots, and export as CSV.
- **Medical emergencies and danger to life go to 911.** The page says so and does not dispatch anyone.
  No logins, no server, and no routing (road closures aren't in free routing data).

## Demo day
Live services can be slow. Load once, then press **Save snapshot**. If live loading fails, the page
falls back to the last good load in this browser, or you can **Open snapshot**.
