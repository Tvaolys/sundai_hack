# Health/Biotech Evidence Findings — 2026-10-24

## S3/E1: CHW / NGO field data — paper forms → manual re-entry into DHIS2/CommCare/KoBo

- **ODK forum, Taylor Downs (BES), 2019-11-06** — https://forum.getodk.org/t/23155 — "There are lots of people who want to use ODK Collect in the field, but then send that data into different systems—i.e., not to use ODK Aggregate…" — the origin thread for ODK REST Services; real, dated demand for pushing ODK data into external systems (like national health platforms). Confidence: verified (blurb read via forum search API).
- **ODK forum, Sjlver / Against Malaria Foundation software engineer, 2023-04-27** — https://forum.getodk.org/t/41258 — AMF engineer describes needing ODK to integrate with their own downstream systems; 8 likes. Confidence: verified (blurb).
- **ODK Build GitHub issue #201 (2018)** — https://github.com/getodk/build/issues/201 — "Cannot export to XLSForm" server crash; export pipeline fragility complaint from a real user (Ubuntu 18.04). Confidence: verified.
- **DHIS2 official docs (data-entry page)** — https://docs.dhis2.org/en/use/user-guides/dhis-core-version-242/collecting-data/data-entry.html — states "A data set often corresponds to a paper-based data collection tool" — i.e., manual re-entry of paper forms into DHIS2 is a designed-in workflow, not an edge case. Confidence: verified.
- **dhis2.org community-health page (undated marketing but explicit)** — https://dhis2.org/health/community-health/ — admits "Data generated in communities has traditionally stayed disconnected from national HMIS… leaves community health workers filling in forms whose results they never see." Official acknowledgment of the gap. Confidence: verified (text seen).
- **DHIS2 community forum, Sarah Burnett, 2020-07-24** — https://community.dhis2.org/ (topic on Event Capture grid-column setup) — implementer wrestling with data-entry form usability. Confidence: plausible (blurb only).
- **KoBo community forum search "export frustrating cleaning"** — returned ZERO posts. Notable: could not surface widespread export/cleaning complaint threads via that phrasing.
- **Crowdedness check**: KoBo (35k+ orgs, 25M+ submissions/month), CommCare (Dimagi, 1M+ frontline workers, SOC2/HIPAA, mature no-code platform), ODK Central with OData feeds and official DHIS2 integration paths — the collection layer is heavily served. Residual gap is narrower: glue/cleaning between ODK/KoBo exports and DHIS2, not collection itself.

**VERDICT (S3/E1): CROWDED** — collection tools (KoBo/ODK/CommCare) are mature and dominant; remaining traces are about *integration glue* (ODK→external systems, ODK→DHIS2), a real but narrow wedge.
