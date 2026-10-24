// ems.js — the ambulance crew's enroute view. Follows the most severe active
// case: destination, ETA, live vitals + ECG, patient card, and SBAR handoff.

const $ = (id) => document.getElementById(id);
let map = null, routeLayer = null, mapOk = false;
let ecgTimer = null, ecgData = [], ecgPhase = 0, curHr = 74, curSpo2 = 98, curCrit = false;

async function j(url) { const r = await fetch(url); return r.json(); }

function initMap() {
  try {
    if (typeof L === "undefined") throw new Error("map blocked");
    map = L.map("map").setView([42.33, -71.08], 11);
    L.tileLayer("https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png", {
      attribution: "&copy; CARTO", maxZoom: 19,
    }).addTo(map);
    routeLayer = L.layerGroup().addTo(map);
    mapOk = true;
  } catch (e) { mapOk = false; }
}

function poll() { j("/api/active").then(render).catch(() => {}); }

function render(data) {
  const cases = (data.cases || []).filter((c) => c.status !== "arrived");
  if (!cases.length) {
    $("empty").style.display = "block";
    $("panel").classList.add("hidden");
    return;
  }
  $("empty").style.display = "none";
  $("panel").classList.remove("hidden");
  const c = cases[0]; // most severe (active sorts by triage score)

  const d = c.destination || {};
  $("dest-name").textContent = d.name || "nearest ER";
  $("dest-sub").textContent = d.muni ? `${d.muni} · ${d.distance_km} km · ${d.capability_reason}` : "";
  $("eta").textContent = c.eta_remaining_min != null ? c.eta_remaining_min : "--";

  const v = c.latest_vital || {};
  $("hr").textContent = v.hr != null ? v.hr : "--";
  $("spo2").textContent = v.spo2 != null ? v.spo2 : "--";
  curHr = v.hr || curHr; curSpo2 = v.spo2 != null ? v.spo2 : curSpo2;

  const tri = c.triage || { band: "unknown" };
  curCrit = tri.band === "critical";
  const tEl = $("triage");
  tEl.className = "triage " + tri.band;
  tEl.innerHTML = `<span class="triage-dot"></span><b>${tri.band.toUpperCase()}</b>`;

  // Patient card
  const p = c.profile || {};
  $("pname").textContent = `${p.name || "Unknown"} · ${p.age || "?"}${p.sex ? "/" + p.sex : ""} · ${p.blood_type || "?"}`;
  const flags = [];
  if (c.unresponsive) flags.push(`<span class="flag unresp-flag">Unresponsive</span>`);
  if (c.trigger === "fall-auto") flags.push(`<span class="flag fall-flag">Auto: fall</span>`);
  if (c.trigger === "mci") flags.push(`<span class="flag fall-flag">MCI</span>`);
  if (p.language && p.language.toLowerCase() !== "english") flags.push(`<span class="flag lang-flag">Interpreter: ${p.language}</span>`);
  if (c.baseline_delta && c.baseline_delta.elevated) flags.push(`<span class="flag unresp-flag">${c.baseline_delta.delta} bpm vs baseline</span>`);
  $("flags").innerHTML = flags.join("");

  const list = (a) => (a && a.length ? a.join(", ") : "none on file");
  $("intake").innerHTML = `
    <div class="row"><span class="k">Conditions</span><span>${list(p.conditions)}</span></div>
    <div class="row"><span class="k">Meds</span><span>${list(p.medications)}</span></div>
    <div class="row"><span class="k">Allergies</span><span class="warn-allergy">${list(p.allergies)}</span></div>
    <div class="row"><span class="k">Notes</span><span>${p.notes || "—"}</span></div>`;

  // Safety flags (most important for the crew)
  if (c.safety_flags && c.safety_flags.length) {
    $("intake").innerHTML += `<div class="safety">
      <div class="safety-title">Safety checks</div>
      ${c.safety_flags.map((f) => `<div class="safety-flag sf-${f.level}">${f.text}</div>`).join("")}
    </div>`;
  }
  if (c.reserved_resource) {
    $("intake").innerHTML += `<div class="reserved">🏥 ER reserving: <b>${c.reserved_resource}</b></div>`;
  }

  // SBAR (localized lead first, if present)
  const s = c.sbar || {};
  const lead = c.localized_lead ? `<div class="sbar-row"><span class="sbar-k">🌐</span><span>${c.localized_lead}</span></div>` : "";
  $("sbar").innerHTML = lead + ["situation", "background", "assessment", "recommendation"]
    .map((k) => `<div class="sbar-row"><span class="sbar-k">${k[0].toUpperCase()}</span><span>${s[k] || ""}</span></div>`)
    .join("");

  drawMap(c);
}

function drawMap(c) {
  if (!mapOk) return;
  routeLayer.clearLayers();
  const pts = [];
  if (c.patient_lat != null) {
    L.circleMarker([c.patient_lat, c.patient_lon], { radius: 8, color: "#fff", weight: 2, fillColor: "#4ea8ff", fillOpacity: 1 }).bindTooltip("Ambulance / patient").addTo(routeLayer);
    pts.push([c.patient_lat, c.patient_lon]);
  }
  const d = c.destination;
  if (d) {
    L.circleMarker([d.lat, d.lon], { radius: 10, color: "#fff", weight: 2, fillColor: "#2fbf71", fillOpacity: 1 }).bindTooltip(d.name).addTo(routeLayer);
    if (c.patient_lat != null) L.polyline([[c.patient_lat, c.patient_lon], [d.lat, d.lon]], { color: "#2fbf71", weight: 4, opacity: .85, dashArray: "1 8" }).addTo(routeLayer);
    pts.push([d.lat, d.lon]);
  }
  if (pts.length) map.fitBounds(pts, { padding: [40, 40], maxZoom: 13 });
}

// ECG-style waveform driven by current HR.
function startECG() {
  const cv = $("ecg"); if (!cv) return;
  const ctx = cv.getContext("2d"), W = cv.width, H = cv.height;
  ecgData = new Array(W).fill(H / 2);
  ecgTimer = setInterval(() => {
    const beat = (60 / Math.max(40, curHr)) * 1000 / 33;
    ecgPhase += 1;
    const pos = (ecgPhase % beat) / beat;
    ecgData.push(H / 2 - ecgWave(pos) * (H * 0.4));
    if (ecgData.length > W) ecgData.shift();
    ctx.clearRect(0, 0, W, H);
    ctx.strokeStyle = "rgba(90,209,160,.12)"; ctx.lineWidth = 1;
    for (let y = 0; y <= H; y += H / 3) { ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(W, y); ctx.stroke(); }
    ctx.beginPath();
    ctx.strokeStyle = curCrit ? "#ff6b6b" : "#5ad1a0"; ctx.lineWidth = 2;
    ecgData.forEach((y, x) => (x === 0 ? ctx.moveTo(x, y) : ctx.lineTo(x, y)));
    ctx.stroke();
  }, 33);
}
function ecgWave(p) {
  const s = (c, w, a) => a * Math.exp(-((p - c) ** 2) / (2 * w * w));
  return s(0.18, 0.012, -0.12) + s(0.20, 0.010, 1.0) + s(0.225, 0.012, -0.25) + s(0.10, 0.02, 0.12) + s(0.38, 0.04, 0.22);
}

initMap();
startECG();
poll();
setInterval(poll, 1000);
