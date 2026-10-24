// n2-emready demo data — realistic SAMPLE MA coastal block groups.
// In the real build these rows come from LIVE adapters:
//   EJ2020 ArcGIS  -> PCT_MINORITY, LIMENGHHPCT, BG_MHHI
//   OpenFEMA       -> DisasterDeclarationsSummaries (historical replay)
//   NOAA tide gauge -> coastal-flood trigger
//   CDC SVI         -> social-vulnerability index
// Shape and field names mirror those sources so the adapters drop in unchanged.
// Numbers here are plausible stand-ins, NOT official figures — demo use only.

window.EMREADY = {
  // ---- Coastal-flood trigger (NOAA Boston tide gauge 8443970) ----
  tide: {
    station: "8443970",
    stationName: "Boston, MA",
    units: "ft (MLLW)",
    floodThreshold: 11.5,          // minor coastal-flood stage
    // a 24h sample window; the demo "runs" the latest reading
    series: [
      { t: "06:00", h: 9.1 }, { t: "07:00", h: 10.0 }, { t: "08:00", h: 10.9 },
      { t: "09:00", h: 11.7 }, { t: "10:00", h: 12.3 }, { t: "11:00", h: 11.8 },
      { t: "12:00", h: 10.6 }, { t: "13:00", h: 9.4 }
    ]
  },

  // ---- Hazard context (curated from MA Climate Change Assessment, public doc) ----
  hazardContext: {
    "Coastal Flood": {
      rank: 1,
      note: "Top-tier statewide hazard; damage and disruption magnitude both rated High in the MA Climate Change Assessment.",
      drivers: ["sea-level rise", "storm surge", "high-tide flooding"]
    },
    "Inland Flood": {
      rank: 2,
      note: "High exposure along riverine corridors; precipitation intensity rising.",
      drivers: ["extreme precipitation", "undersized culverts"]
    },
    "Hurricane/Tropical Storm": {
      rank: 3,
      note: "Lower frequency, very high consequence; compounds coastal flooding.",
      drivers: ["wind", "surge", "power loss"]
    }
  },

  // ---- Block groups in flood-adjacent MA towns ----
  // limEngPct   = LIMENGHHPCT  (% limited-English-speaking households)
  // mhhi        = BG_MHHI      (median household income, USD)
  // minorityPct = PCT_MINORITY
  // svi         = CDC SVI percentile (0-1, higher = more vulnerable)
  // pop         = block-group population (for per-capita normalization)
  // floodAdj    = within the coastal-flood advisory footprint for this event
  // languages   = top non-English languages spoken (drives outreach language list)
  blockGroups: [
    { id: "250250001001", town: "Chelsea",      pop: 1820, limEngPct: 41.2, mhhi: 42800, minorityPct: 78.0, svi: 0.94, floodAdj: true,  lat: 42.3918, lng: -71.0328, languages: ["Spanish", "Portuguese"] },
    { id: "250250002002", town: "Chelsea",      pop: 1510, limEngPct: 38.5, mhhi: 39100, minorityPct: 82.4, svi: 0.96, floodAdj: true,  lat: 42.3962, lng: -71.0289, languages: ["Spanish", "Haitian Creole"] },
    { id: "250092011003", town: "Lynn",         pop: 1990, limEngPct: 33.7, mhhi: 45600, minorityPct: 67.1, svi: 0.88, floodAdj: true,  lat: 42.4668, lng: -70.9495, languages: ["Spanish", "Khmer"] },
    { id: "250092014001", town: "Lynn",         pop: 1340, limEngPct: 22.4, mhhi: 51200, minorityPct: 54.3, svi: 0.73, floodAdj: true,  lat: 42.4780, lng: -70.9601, languages: ["Spanish", "Khmer"] },
    { id: "250250101002", town: "Revere",       pop: 1720, limEngPct: 29.8, mhhi: 48900, minorityPct: 61.9, svi: 0.81, floodAdj: true,  lat: 42.4084, lng: -70.9925, languages: ["Spanish", "Arabic"] },
    { id: "250250103004", town: "Revere",       pop: 1265, limEngPct: 18.1, mhhi: 57400, minorityPct: 48.7, svi: 0.62, floodAdj: true,  lat: 42.4190, lng: -71.0041, languages: ["Spanish", "Arabic"] },
    { id: "250173201001", town: "Everett",      pop: 1580, limEngPct: 35.9, mhhi: 43700, minorityPct: 71.2, svi: 0.90, floodAdj: true,  lat: 42.4064, lng: -71.0537, languages: ["Spanish", "Haitian Creole", "Portuguese"] },
    { id: "250092502002", town: "Salem",        pop: 1410, limEngPct: 16.3, mhhi: 62100, minorityPct: 38.4, svi: 0.55, floodAdj: true,  lat: 42.5195, lng: -70.8967, languages: ["Spanish"] },
    { id: "250092041003", town: "Gloucester",   pop: 1120, limEngPct: 8.7,  mhhi: 68300, minorityPct: 19.6, svi: 0.41, floodAdj: true,  lat: 42.6159, lng: -70.6620, languages: ["Portuguese"] },
    { id: "250235101001", town: "New Bedford",  pop: 1760, limEngPct: 27.5, mhhi: 41200, minorityPct: 59.8, svi: 0.92, floodAdj: true,  lat: 41.6362, lng: -70.9342, languages: ["Portuguese", "Spanish", "K'iche'"] },
    { id: "250235104002", town: "New Bedford",  pop: 1490, limEngPct: 31.2, mhhi: 38900, minorityPct: 64.1, svi: 0.95, floodAdj: true,  lat: 41.6280, lng: -70.9280, languages: ["Portuguese", "Spanish"] },
    { id: "250277002001", town: "Worcester",    pop: 1650, limEngPct: 24.9, mhhi: 46800, minorityPct: 55.2, svi: 0.84, floodAdj: false, lat: 42.2626, lng: -71.8023, languages: ["Spanish", "Vietnamese", "Portuguese"] },
    { id: "250138012002", town: "Springfield",  pop: 1880, limEngPct: 30.6, mhhi: 37400, minorityPct: 73.9, svi: 0.97, floodAdj: false, lat: 42.1015, lng: -72.5898, languages: ["Spanish", "Vietnamese"] },
    { id: "250092061004", town: "Marblehead",   pop: 980,  limEngPct: 3.1,  mhhi: 112000, minorityPct: 9.4, svi: 0.18, floodAdj: true,  lat: 42.5001, lng: -70.8578, languages: [] }
  ],

  // ---- Historical-event replay (OpenFEMA DisasterDeclarationsSummaries, MA) ----
  historicalEvents: [
    { id: "DR-4214-MA", title: "Severe Winter Storm & Flooding", date: "2015-02-02", incidentType: "Coastal Flood", towns: ["Chelsea","Lynn","Revere","Everett","Salem"] },
    { id: "DR-4372-MA", title: "Severe Storm (Nor'easter)",      date: "2018-03-02", incidentType: "Coastal Flood", towns: ["Revere","Lynn","Gloucester","Salem","New Bedford"] },
    { id: "DR-4496-MA", title: "COVID-19 Pandemic",              date: "2020-03-27", incidentType: "Hurricane/Tropical Storm", towns: ["Chelsea","New Bedford","Springfield","Worcester"] }
  ]
};
