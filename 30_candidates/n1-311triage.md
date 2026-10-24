# n1-311triage — Repeat-report & SLA-miss finder for Boston 311, with an equity overlay
Track: Civic action (More Responsive Neighborhood Services / 311) | Scores: I4 F4 N4 | Gates passed: 1,2,3,4,5,6
Problem: Cities drown in 311 reports; the official challenge says "high volumes and repeated reports make it hard to recognize patterns, prioritize action, and communicate progress." Duplicate reports bury chronic problems, and residents can't tell if their block is one of many or chronically missed. Generic dashboards show volume, not duplicate-clusters or where SLA misses concentrate.
Evidence:
- Challenge text (official portal, extracted 2026-10-24): verified.
- Boston 311 datastore (resource_id 254adca6-64ab-4c5c-9fc0-a6da622be185) exposes open_date, service_name, case_status, neighborhood, zip_code, on_time, ward — the exact columns for duplicate-clustering + SLA analysis: verified (portal registry + schema).
- MassGIS EJ2020 ArcGIS query LIVE (returns MUNICIPALITY, PCT_MINORITY, LIMENGHHPCT): curl-verified 2026-10-24.
- Feasibility caveat: data.boston.gov is Cloudflare-walled on server-side curl; fetch client-side or cache a slice tonight. verified-blocked 2026-10-24.
Demo moment: Pick a neighborhood → map of open vs on-time-missed cases; top 3 chronic categories; a cluster of duplicate pothole reports collapsed into one hot-spot; EJ overlay showing misses skew to a limited-English block group.
Build plan (09:00–20:00):
- 09:00 spec: define duplicate rule (same service_name + proximity + time window) and SLA-miss = on_time false; pick 1 neighborhood + cache a 311 slice NOW (dodges Cloudflare).
- 10:00 CS×2: ingest + dedup/cluster logic; CS×1: map UI (Leaflet) with case pins; CS×1: EJ2020 join + overlay.
- 13:00 tester: validate clusters against raw rows; sanity-check SLA counts.
- 15:00 add "chronic category" ranking + resident-facing summary line.
- 16:30 demo-builder: neighborhood story + equity reveal; 18:00 FREEZE on cached slice.
Agent plan: Agent builds ingest, clustering, map, and EJ join; humans own the dedup heuristic thresholds and the equity narrative. Client-side fetch keeps it laptop-only.
Risks & fallback: (1) Cloudflare blocks live pull → cache slice tonight (primary). (2) Dedup false-merges → tune window + show raw rows behind each cluster. Fallback: static cached neighborhood still delivers the full demo.
Why it matters: Turns a noisy civic feed into "is my block chronically ignored, and who's most affected" — a resident- and ops-usable view the challenge explicitly asks for, grounded in the city's own data.
