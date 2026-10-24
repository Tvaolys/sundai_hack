// patient.js — simulated phone/watch client.
// Profile edit/save, manual SOS, fall-detection auto-SOS with countdown,
// live simulated vitals, and a scrolling ECG-style waveform.

const $ = (id) => document.getElementById(id);
const LOC = { lat: 42.3601, lon: -71.0589 }; // Boston demo location

let profile = null;
let caseId = null;
let vitalsTimer = null;
let ecgTimer = null;
let fallTimer = null;
let hr = 74, spo2 = 98, etype = "cardiac";
let ecgPhase = 0;
let ecgData = [];

async function j(url, opts) {
  const r = await fetch(url, opts);
  return r.json();
}

async function loadProfile() {
  profile = await j("/api/profile");
  $("f-name").value = profile.name || "";
  $("f-age").value = profile.age || "";
  $("f-blood").value = profile.blood_type || "";
  $("f-lang").value = profile.language || "";
  $("f-cond").value = (profile.conditions || []).join(", ");
  $("f-meds").value = (profile.medications || []).join(", ");
  $("f-allerg").value = (profile.allergies || []).join(", ");
  $("f-contact").value = profile.emergency_contact
    ? profile.emergency_contact.name + " " + (profile.emergency_contact.phone || "") : "";
  $("f-notes").value = profile.notes || "";
  hr = profile.baseline_hr || 74;
}

async function saveProfile() {
  const body = {
    name: $("f-name").value,
    age: parseInt($("f-age").value) || profile.age,
    blood_type: $("f-blood").value,
    language: $("f-lang").value,
    conditions: splitList($("f-cond").value),
    medications: splitList($("f-meds").value),
    allergies: splitList($("f-allerg").value),
    notes: $("f-notes").value,
  };
  await j("/api/profile", {
    method: "POST", headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  const tag = $("saved-tag");
  tag.textContent = "saved ✓"; tag.classList.add("flash");
  setTimeout(() => tag.classList.remove("flash"), 900);
  profile = await j("/api/profile");
}

function splitList(s) { return s.split(",").map((x) => x.trim()).filter(Boolean); }

async function triggerSOS(opts = {}) {
  etype = $("etype").value;
  const res = await j("/api/sos", {
    method: "POST", headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      lat: LOC.lat, lon: LOC.lon, type: etype,
      trigger: opts.trigger || "manual",
      unresponsive: !!opts.unresponsive,
    }),
  });
  if (!res.ok || !res.destination) return;
  caseId = res.case_id;
  const d = res.destination;
  $("dest-name").textContent = d.name;
  $("dest-meta").textContent = `${d.muni} · ${d.distance_km} km · ETA ~${d.eta_min} min · ${d.load_pct}% full`;
  $("dest-cap").textContent = `Matched because: ${d.capability_reason}`;
  $("eta-val").textContent = d.eta_min;
  $("unresp-badge").classList.toggle("hidden", !opts.unresponsive);

  $("screen-profile").classList.add("hidden");
  document.querySelector(".sos-zone").classList.add("hidden");
  $("screen-active").classList.remove("hidden");

  renderQR(caseId);
  startVitals();
  startECG();
}

async function renderQR(cid) {
  const box = $("qr");
  if (!box) return;
  box.innerHTML = "";
  try {
    const h = await j(`/api/handoff/${cid}`);
    if (typeof QRCode === "undefined") throw new Error("qr lib");
    new QRCode(box, { text: h.url, width: 120, height: 120,
      colorDark: "#0b1016", colorLight: "#ffffff" });
  } catch (e) {
    // Fallback: show the link if the QR lib didn't load.
    box.innerHTML = `<div class="muted" style="font-size:10px;word-break:break-all">${location.origin}/api/case/${cid}</div>`;
  }
}

// ---- Fall detection auto-SOS ----
function simulateFall() {
  let count = 10;
  $("fall-count").textContent = count;
  $("fall-overlay").classList.remove("hidden");
  fallTimer = setInterval(() => {
    count -= 1;
    $("fall-count").textContent = count;
    if (count <= 0) {
      clearInterval(fallTimer); fallTimer = null;
      $("fall-overlay").classList.add("hidden");
      // No response -> auto SOS, patient treated as unresponsive, type = trauma (fall).
      $("etype").value = "trauma";
      triggerSOS({ trigger: "fall-auto", unresponsive: true });
    }
  }, 1000);
}
function cancelFall() {
  if (fallTimer) clearInterval(fallTimer);
  fallTimer = null;
  $("fall-overlay").classList.add("hidden");
}

// ---- Simulated vitals ----
function startVitals() {
  stopVitals();
  let t = 0;
  vitalsTimer = setInterval(async () => {
    t += 1;
    hr += (Math.random() - 0.5) * 4;
    if (etype === "cardiac") { hr += 1.6; if (t > 6) spo2 -= 0.4; }
    else if (etype === "trauma") { hr += 1.2; if (t > 8) spo2 -= 0.3; }
    else if (etype === "stroke") { hr += 0.4; }
    else { hr += 0.2; }
    hr = Math.max(50, Math.min(185, hr));
    spo2 = Math.max(80, Math.min(100, spo2));
    $("hr-val").textContent = Math.round(hr);
    $("spo2-val").textContent = Math.round(spo2);
    setPulse(hr);
    await j("/api/vitals", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ case_id: caseId, hr: Math.round(hr), spo2: Math.round(spo2) }),
    });
  }, 1000);
}
function stopVitals() { if (vitalsTimer) clearInterval(vitalsTimer); vitalsTimer = null; }

function setPulse(h) {
  const ring = document.querySelector(".pulse-ring");
  if (!ring) return;
  ring.style.animationDuration = `${Math.max(0.4, 60 / h)}s`;
  ring.classList.toggle("alarm", h > 120 || spo2 < 92);
}

// ---- ECG-style waveform (synthetic, HR-driven) ----
function startECG() {
  const cv = $("ecg");
  if (!cv) return;
  const ctx = cv.getContext("2d");
  const W = cv.width, H = cv.height;
  ecgData = new Array(W).fill(H / 2);
  stopECG();
  ecgTimer = setInterval(() => {
    // beats-per-frame based on HR; frame ~ 33ms
    const beatInterval = (60 / hr) * 1000 / 33; // frames per beat
    ecgPhase += 1;
    const pos = (ecgPhase % beatInterval) / beatInterval; // 0..1 within a beat
    ecgData.push(H / 2 - ecgWave(pos) * (H * 0.4));
    if (ecgData.length > W) ecgData.shift();

    ctx.clearRect(0, 0, W, H);
    ctx.strokeStyle = "rgba(90,209,160,.15)";
    ctx.lineWidth = 1;
    for (let y = 0; y <= H; y += H / 3) { ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(W, y); ctx.stroke(); }
    ctx.beginPath();
    ctx.strokeStyle = (hr > 120 || spo2 < 92) ? "#ff6b6b" : "#5ad1a0";
    ctx.lineWidth = 2;
    ecgData.forEach((y, x) => (x === 0 ? ctx.moveTo(x, y) : ctx.lineTo(x, y)));
    ctx.stroke();
  }, 33);
}
function stopECG() { if (ecgTimer) clearInterval(ecgTimer); ecgTimer = null; }

// A simplified PQRST morphology as a function of beat phase (0..1).
function ecgWave(p) {
  const spike = (c, w, a) => a * Math.exp(-((p - c) ** 2) / (2 * w * w));
  return spike(0.18, 0.012, -0.12) +  // Q
         spike(0.20, 0.010, 1.0) +    // R
         spike(0.225, 0.012, -0.25) + // S
         spike(0.10, 0.02, 0.12) +    // P
         spike(0.38, 0.04, 0.22);     // T
}

async function cancel() {
  stopVitals(); stopECG();
  if (caseId) {
    await j("/api/resolve", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ case_id: caseId, delete: true }),
    });
  }
  caseId = null;
  $("screen-active").classList.add("hidden");
  $("screen-profile").classList.remove("hidden");
  document.querySelector(".sos-zone").classList.remove("hidden");
  spo2 = 98; hr = profile.baseline_hr || 74;
}

function init() {
  loadProfile();
  $("save").addEventListener("click", saveProfile);
  $("sos").addEventListener("click", () => triggerSOS());
  $("fall").addEventListener("click", simulateFall);
  $("fall-cancel").addEventListener("click", cancelFall);
  $("cancel").addEventListener("click", cancel);
}
init();
