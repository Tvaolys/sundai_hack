# Requirements: n1-311triage — "Is my block chronically missed?" Boston 311 finder

Source research: `30_candidates/n1-311triage.md`, `40_shortlist.md` (#1), `20_findings/round3-newideas.md` (N1).
Track: Civic Action — More Responsive Neighborhood Services (311).

## User stories
- As a city operations analyst, I want repeat reports of the same problem collapsed into one
  hot spot, and the categories that miss their SLA most in a neighborhood, so that I can see
  chronic problems instead of raw ticket volume.
- As a resident or community organizer, I want to see whether service in my neighborhood is
  on time, and whether misses concentrate in limited-English / environmental-justice block
  groups, so that I can raise it with evidence from the city's own data.

## Acceptance criteria (EARS)

### Data
1. THE SYSTEM SHALL run entirely from cached files in `data/` (no network at demo time).
2. WHEN a 311 row has a missing or unparseable `on_time` value THE SYSTEM SHALL exclude it from SLA rates and count it as "SLA UNKNOWN", never as on-time or late.
3. WHEN a 311 row has no coordinates, or coordinates outside the Boston bounding box, THE SYSTEM SHALL keep it in counts but leave it off the map and out of clustering.
4. THE SYSTEM SHALL show the data window (first and last `open_date`) and source on every screen.

### Neighborhood view
5. WHEN the user selects a neighborhood THE SYSTEM SHALL show total cases, open cases, cases with a known SLA result, late cases, and the late rate.
6. WHEN the user selects a neighborhood THE SYSTEM SHALL list the top 3 "chronic" categories (service_name) ranked by late rate, only among categories with at least the minimum case count in design.md; smaller categories are shown as "TOO FEW CASES", not ranked.
7. EVERY rate SHALL be shown with its numerator and denominator (e.g. "41% (82 of 200)"). No composite score.

### Repeat-report clusters
8. WHEN the user selects a neighborhood THE SYSTEM SHALL group reports into clusters using the duplicate rule in design.md (same service_name, within the distance and time window) and list clusters with ≥2 reports, largest first.
9. WHEN the user opens a cluster THE SYSTEM SHALL show the raw rows behind it (case id, open date, status, on_time, address).
10. Every report SHALL belong to exactly one cluster (singletons included), so cluster sizes sum to the number of mapped reports.

### Map
11. WHEN the user selects a neighborhood THE SYSTEM SHALL draw an offline SVG map: block-group outlines, one marker per cluster (size = report count), and a text legend. Late vs on-time SHALL be distinguished by marker shape AND color, not color alone.

### Equity overlay
12. THE SYSTEM SHALL assign each mapped report to an EJ2020 block group by point-in-polygon.
13. WHEN the user selects a neighborhood THE SYSTEM SHALL compare the late rate in EJ block groups flagged for limited-English isolation vs. all other block groups, each with numerator / denominator.
14. IF either group has fewer reports than the minimum in design.md THEN THE SYSTEM SHALL show "NOT ENOUGH DATA TO COMPARE" instead of a rate.
15. THE SYSTEM SHALL show the caveat: "Shows a pattern in the city's own data, not its cause."

### Readability (same rules as emready)
16. Dark text on white, contrast ≥ 7:1, base font ≥ 18px, no dark theme.
17. Every clickable element is a rectangular button/link with a visible 2px border, a text label, and a visible keyboard focus outline. No rounded corners, no icon-only buttons.
18. Color is never the only signal; status uses words.
19. Works keyboard-only; table headers use `<th scope>`; the map has a table equivalent.

## Properties (property-based tests)
- Clustering is a partition: every input report appears in exactly one cluster.
- Every cluster contains a single service_name, and every member is within the distance threshold of the cluster seed and within the time window.
- Clustering is deterministic: same input (any order) → same clusters.
- Late rate is in [0, 1] and late ≤ known ≤ total for every group.
- Chronic-category ranking is non-increasing in late rate and never includes a category below the minimum count.
- Point-in-polygon: a point is assigned to at most one block group; points inside a test square are in, points outside are out.
- Haversine distance is non-negative and symmetric.

## Out of scope
- Live fetching from data.boston.gov at runtime (Cloudflare-walled; cached slice only).
- Predicting resolution times or claiming discrimination / cause.
- Neighborhoods outside Boston; other cities.
- Writing back to 311 or contacting residents.
- User accounts / login.
