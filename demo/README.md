# Who Gets Missed — Emergency Outreach planner

Idea #4 from the Hackachusetts research report (`report/hackachusetts_research.tex`,
`30_candidates/n2-emready.md`), built on **live public data**.

A coastal flood is coming. Door-knock teams can only reach so many homes.
The tool shows **who to reach first, in which languages, and who gets missed** when time runs out.

**Safety:** planning aid only. It never writes or sends alert messages.

## Run it
Open `index.html` in a browser (Chrome, Edge, Firefox). One file, no install.
It loads live data on open. The first load takes about 20 seconds (flood zones); later loads are faster.

## Live sources
| Source | Used for |
|---|---|
| NOAA CO-OPS gauge 8443970 (Boston) | Latest tide, 2-day predictions, NWS flood stages, past storm peaks |
| MassGIS EJ 2020 block groups | Households, limited-English households, median income, % minority, shapes |
| CDC/ATSDR SVI 2022 (tract) | Social vulnerability score |
| FEMA National Flood Hazard Layer | Which flood zones each block group touches |
| OpenFEMA disaster declarations (MA) | Past storms to replay |
| Census ACS 2022 5-yr C16001 (tract) | Language split — needs a free [Census API key](https://api.census.gov/data/key_signup.html) |

No keys are needed except the optional Census key, which stays in your browser.

## How it decides
- **Flooding:** a planner-owned rule. Minor stage → FEMA VE wave zones; moderate → + A zones (1%/yr);
  major → + 0.2%/yr zones. A block group counts if it touches the zone. This is not an inundation model,
  and A zones can include river flood areas.
- **Order:** one plain sort on one real column (limited-English %, income, SVI, or size). Missing values last,
  ties by GEOID. No combined score.
- **Capacity:** teams × hours × doors per hour, given out in rank order. The dashed line is where it runs out.
- **Fairness check:** compares your rule with the biggest-first baseline.
- **Languages:** household counts are real; the split by language uses each tract's ACS mix.

## Demo day
Live services can be slow. Load once, then press **Save snapshot**. If live loading fails, the page
falls back to the last good load in this browser, or you can **Open snapshot**.
