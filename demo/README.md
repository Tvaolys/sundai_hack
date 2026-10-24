# Who Gets Missed — Emergency Outreach demo

Demo of idea #4 from the Hackachusetts research report (`report/hackachusetts_research.tex`,
`30_candidates/n2-emready.md`).

A coastal-flood advisory fires. Door-knock teams can only reach so many homes.
The tool shows **who to reach first, in which languages, and who gets missed** when time runs out.

**Safety:** planning aid only. It never writes or sends alert messages.

## Run it
Open `index.html` in any browser. One file, no install, works offline.

## What to try
| Control | What changes |
|---|---|
| Event | Live sample reading, or replay a past storm |
| Tide slider | More block groups flood as the tide rises |
| Who goes first? | Limited-English % / income / CDC SVI / biggest-first baseline |
| Teams × hours × doors/hr | Capacity; the dashed line shows where it runs out |
| Download CSV | The outreach list, for a human to act on |

The **fairness check** compares your rule with the biggest-first baseline:
how many limited-English households each one reaches.

## How it ranks
One plain sort on one real column, ties broken by GEOID. No combined score.
Doors are given out in rank order until capacity is used up.

## Data
SAMPLE rows inlined in `index.html` — plausible, not official. Field names mirror the live
sources so real adapters can replace `EMO.ROWS`:

| Source | Fields |
|---|---|
| EJ2020 ArcGIS | `LIMENGHHPCT`, `BG_MHHI`, `PCT_MINORITY` |
| CDC SVI | `SVI` percentile |
| NOAA tide gauge 8443970 (Boston) | advisory trigger |
| OpenFEMA DisasterDeclarationsSummaries (MA) | replay events |
