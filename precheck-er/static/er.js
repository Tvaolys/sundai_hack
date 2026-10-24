// er.js — ER charge-nurse dashboard.
// Polls /api/active and renders each inbound patient's pre-filled intake, live
// vitals (ECG-style sparkline), an early-warning triage band, a language/
// interpreter flag, and a map showing the routing decision (chosen vs skipped).

const $ = (id) => document.getElementById(id);
let map = null, routeLayer = null, mapOk = false;
let focusCaseId = null;

async function j(url, opts) {
  const r = await fetch(url, opts);
  return r.json();
}

function initMap() {
  try {
    if (typeof L === "undefined") throw new Error("Leaflet CDN blocked");
    map = L.map("map").setView([42.33, -71.08], 10);
    L.tileLayer("https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png", {
      attribution: "&copy; OpenStreetMap &copy; CARTO", maxZoom: 19,
    }).addTo(map);
    routeLayer = L.layerGroup().addTo(map);
    mapOk = true;
  } catch (e) {
    mapOk = false;
    const el = $("map");
    if (el) el.innerHTML = `<div style="padding:16px;color:#8fa0bd">Map unavailable (${e.message}). Case details still work.</div>`;
  }
}

function drawMapForCase(c) {
  if (!mapOk || !routeLayer) return;
  routeLayer.clearLayers();
  const pts = [];

  // Patient
  if (c.patient_lat != null) {
    L.circleMarker([c.patient_lat, c.patient_lon], {
      radius: 8, color: "#fff", weight: 2, fillColor: "#4ea8ff", fillOpacity: 1,
    }).bindTooltip("Patient").addTo(routeLayer);
    pts.push([c.patient_lat, c.patient_lon]);
  }
  // Chosen ER + route line
  const d = c.destination;
  if (d) {
    L.circleMarker([d.lat, d.lon], {
      radius: 10, color: "#fff", weight: 2, fillColor: "#2fbf71", fillOpacity: 1,
    }).bindTooltip(`✓ ${d.name} — ${d.capability_reason}`, { permanent: false }).addTo(routeLayer);
    if (c.patient_lat != null) {
      L.polyline([[c.patient_lat, c.patient_lon], [d.lat, d.lon]], {
        color: "#2fbf71", weight: 4, opacity: 0.8, dashArray: "1 8",
      }).addTo(routeLayer);
    }
    pts.push([d.lat, d.lon]);
  }
  // Skipped nearer ERs (grey, with reason)
  (c.skipped_nearer || []).forEach((s) => {
    L.circleMarker([s.lat, s.lon], {
      radius: 6, color: "#6b7694", weight: 1.5, fillColor: "#2a3346", fillOpacity: 1,
    }).bindTooltip(`✗ ${s.name} — ${s.skip_reason || "farther from optimum"}`).addTo(routeLayer);
    pts.push([s.lat, s.lon]);
  });

  if (pts.length) map.fitBounds(pts, { padding: [40, 40], maxZoom: 13 });
}

function poll() {
  j("/api/active").then(render).catch(() => {});
  j("/api/events").then(renderEvents).catch(() => {});
}

function renderEvents(data) {
  const bar = document.getElementById("events");
  if (!bar) return;
  const evs = (data.events || []).slice(0, 4);
  bar.innerHTML = evs.length
    ? evs.map((e) => `<span class="ev ev-${e.kind}">${e.kind === 'notify' ? '📲' : e.kind === 'mci' ? '🚨' : '•'} ${e.text}</span>`).join("")
    : "";
  bar.style.display = evs.length ? "flex" : "none";
}

async function triggerMCI() {
  await j("/api/mci", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ count: 4 }) });
  poll();
}

function render(data) {
  const cases = data.cases || [];
  $("empty").style.display = cases.length ? "none" : "block";
  $("cases").innerHTML = cases.map(renderCase).join("");

  cases.forEach((c) => {
    const btn = document.getElementById(`arrived-${c.case_id}`);
    if (btn) btn.addEventListener("click", () => markArrived(c.case_id));
    const card = document.getElementById(`card-${c.case_id}`);
    if (card) card.addEventListener("click", () => { focusCaseId = c.case_id; drawMapForCase(c); highlight(); });
    drawSpark(c);
  });

  // Keep the map focused on the selected (or newest) case.
  if (!focusCaseId && cases.length) focusCaseId = cases[0].case_id;
  const focus = cases.find((c) => c.case_id === focusCaseId);
  if (focus) drawMapForCase(focus);
  highlight();
}

function highlight() {
  document.querySelectorAll(".case").forEach((el) =>
    el.classList.toggle("focused", el.id === `card-${focusCaseId}`));
}

function vitalClass(hr, spo2) {
  if (hr == null) return "";
  if (hr > 120 || (spo2 != null && spo2 < 92)) return "crit";
  if (hr > 100 || (spo2 != null && spo2 < 95)) return "warn";
  return "ok";
}

function renderCase(c) {
  const p = c.profile || {};
  const v = c.latest_vital || {};
  const vc = vitalClass(v.hr, v.spo2);
  const eta = c.eta_remaining_min != null ? `${c.eta_remaining_min} min` : "—";
  const list = (arr) => (arr && arr.length ? arr.map((x) => `<span class="tag">${x}</span>`).join("") : '<span class="muted">none on file</span>');
  const tri = c.triage || { band: "unknown", detail: "", score: 0 };

  const flags = [];
  if (c.unresponsive) flags.push(`<span class="flag unresp-flag">Unresponsive</span>`);
  if (c.trigger === "fall-auto") flags.push(`<span class="flag fall-flag">Auto: fall detected</span>`);
  if (p.language && p.language.toLowerCase() !== "english")
    flags.push(`<span class="flag lang-flag">Interpreter: ${p.language}</span>`);

  return `<div class="case ${c.status === 'arrived' ? 'arrived' : ''}" id="card-${c.case_id}">
    <div class="case-head">
      <div>
        <div class="etype-badge ${c.type}">${c.type_label}</div>
        <h3>${p.name || 'Unknown'} <span class="muted">· ${p.age || '?'}${p.sex ? '/' + p.sex : ''} · ${p.blood_type || '?'}</span></h3>
        <div class="flags">${flags.join("")}</div>
      </div>
      <div class="eta-box ${c.status === 'arrived' ? 'done' : ''}">
        <div class="eta-num">${c.status === 'arrived' ? 'HERE' : eta}</div>
        <div class="eta-lbl">${c.status === 'arrived' ? 'arrived' : 'ETA'}</div>
      </div>
    </div>

    <div class="triage ${tri.band}">
      <span class="triage-dot"></span>
      <b>${tri.band.toUpperCase()}</b>
      <span class="muted">· EW score ${tri.score} · ${tri.detail}</span>
    </div>

    ${c.deterioration && c.deterioration.startsWith('trending up') ? `<div class="forecast">⚠ ${c.deterioration}</div>` : ''}

    ${c.reserved_resource ? `<div class="reserved">🏥 Reserved: <b>${c.reserved_resource}</b></div>` : ''}

    ${(c.safety_flags && c.safety_flags.length) ? `<div class="safety">
      <div class="safety-title">Safety checks</div>
      ${c.safety_flags.map((f) => `<div class="safety-flag sf-${f.level}">${f.text}</div>`).join('')}
    </div>` : ''}

    <div class="vitals-live ${vc}">
      <div class="big"><span>${v.hr != null ? v.hr : '--'}</span><small>HR bpm</small></div>
      <div class="big"><span>${v.spo2 != null ? v.spo2 : '--'}</span><small>SpO₂ %</small></div>
      <canvas id="spark-${c.case_id}" class="spark" width="220" height="48"></canvas>
    </div>

    <div class="intake">
      <div class="row"><span class="k">Conditions</span><span class="val">${list(p.conditions)}</span></div>
      <div class="row"><span class="k">Medications</span><span class="val">${list(p.medications)}</span></div>
      <div class="row"><span class="k">Allergies</span><span class="val warn-allergy">${list(p.allergies)}</span></div>
      <div class="row"><span class="k">Notes</span><span class="val">${p.notes || '<span class="muted">—</span>'}</span></div>
      <div class="row"><span class="k">Contact</span><span class="val">${p.emergency_contact ? (p.emergency_contact.name + ' · ' + (p.emergency_contact.phone || '')) : '—'}</span></div>
      <div class="row"><span class="k">Insurance</span><span class="val">${p.insurance ? (p.insurance.provider + ' · ' + p.insurance.member_id) : '—'}</span></div>
    </div>

    ${c.baseline_delta && c.baseline_delta.elevated ? `<div class="baseline-note">↑ HR ${c.baseline_delta.text}</div>` : ''}

    <details class="sbar-box">
      <summary>SBAR handoff note</summary>
      <div class="sbar-grid">
        ${['situation','background','assessment','recommendation'].map((k) =>
          `<div class="sbar-row"><span class="sbar-k">${k[0].toUpperCase()}</span><span>${(c.sbar || {})[k] || ''}</span></div>`).join('')}
      </div>
    </details>

    <div class="dest muted">Routed to ${c.destination ? c.destination.name : 'nearest ER'} — ${c.destination ? c.destination.capability_reason : ''} · ${c.destination ? c.destination.load_pct + '% full' : ''}</div>

    <details class="audit-box">
      <summary>Access &amp; consent trail (${(c.access_log || []).length})</summary>
      <div class="audit-list">
        ${(c.access_log || []).map((a) => `<div class="audit-row"><span class="muted">${new Date(a.t*1000).toLocaleTimeString()}</span> ${a.who} — ${a.action}</div>`).join('') || '<span class="muted">no access yet</span>'}
      </div>
    </details>

    <div class="actions">
      <a class="fhir-link" href="/api/fhir" target="_blank" title="Pre-filled intake as a FHIR R4 bundle">View FHIR intake →</a>
      <button id="arrived-${c.case_id}" class="arrived-btn">${c.status === 'arrived' ? 'Clear from board' : 'Mark arrived'}</button>
    </div>
  </div>`;
}

function drawSpark(c) {
  const cv = document.getElementById(`spark-${c.case_id}`);
  if (!cv) return;
  const ctx = cv.getContext("2d");
  ctx.clearRect(0, 0, cv.width, cv.height);
  const data = (c.vitals || []).map((x) => x.hr).filter((x) => x != null);
  if (data.length < 2) return;
  const min = Math.min(...data) - 3, max = Math.max(...data) + 3;
  const range = Math.max(1, max - min);
  const crit = c.triage && c.triage.band === "critical";
  ctx.beginPath();
  ctx.strokeStyle = crit ? "#ff6b6b" : "#5ad1a0";
  ctx.lineWidth = 2;
  data.forEach((val, i) => {
    const x = (i / (data.length - 1)) * cv.width;
    const y = cv.height - ((val - min) / range) * cv.height;
    i === 0 ? ctx.moveTo(x, y) : ctx.lineTo(x, y);
  });
  ctx.stroke();
}

async function markArrived(caseId) {
  const data = await j("/api/active");
  const c = (data.cases || []).find((x) => x.case_id === caseId);
  const del = c && c.status === "arrived";
  await j("/api/resolve", {
    method: "POST", headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ case_id: caseId, delete: del }),
  });
  if (del && focusCaseId === caseId) focusCaseId = null;
  poll();
}

const mciBtn = document.getElementById("mci");
if (mciBtn) mciBtn.addEventListener("click", triggerMCI);

initMap();
poll();
setInterval(poll, 1000);
