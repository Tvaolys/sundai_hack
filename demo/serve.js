// Local helper for the "Who Gets Missed" demo (Node 18+, no installs).
//
//   node demo/serve.js        then open http://127.0.0.1:8765/
//
// It serves this folder and passes MEMA's power-outage feed through at /mema/outages.geojson.
// MEMA's feed is http-only and sends no CORS header, so a web page cannot read it directly.
// Safety: listens on 127.0.0.1 only, serves only files inside this folder, and fetches only the
// one fixed MEMA URL below (it is not an open proxy).
'use strict';
const http = require('http');
const fs = require('fs');
const path = require('path');

const ROOT = __dirname;
const HOST = '127.0.0.1';
const PORT = Number(process.env.PORT) || 8765;
const MEMA = 'http://mema.mapsonline.net/power_outage_public.geojson';
const TYPES = { '.html': 'text/html; charset=utf-8', '.md': 'text/plain; charset=utf-8', '.json': 'application/json' };

let cache = null; // { at, body } — MEMA updates every 15 minutes, so one fetch a minute is plenty

async function sendOutages(res) {
  try {
    if (!cache || Date.now() - cache.at > 60000) {
      const ctl = new AbortController();
      const timer = setTimeout(() => ctl.abort(), 20000);
      try {
        const r = await fetch(MEMA, { signal: ctl.signal });
        if (!r.ok) throw new Error('HTTP ' + r.status);
        const body = await r.text();          // the 20 s limit covers the body too
        cache = { at: Date.now(), body };
      } finally { clearTimeout(timer); }
    }
    res.writeHead(200, { 'Content-Type': 'application/geo+json', 'Cache-Control': 'no-store' });
    res.end(cache.body);
  } catch (e) {
    res.writeHead(502, { 'Content-Type': 'text/plain; charset=utf-8' });
    res.end('MEMA feed unavailable: ' + e.message);
  }
}

http.createServer((req, res) => {
  if (req.method !== 'GET' && req.method !== 'HEAD') { res.writeHead(405); return res.end(); }
  let rel;
  try { rel = decodeURIComponent(new URL(req.url, 'http://local').pathname); }
  catch (e) { res.writeHead(400); return res.end(); }
  if (rel === '/mema/outages.geojson') return sendOutages(res);
  const file = path.resolve(ROOT, '.' + (rel === '/' ? '/index.html' : rel));
  // A NUL byte would make fs throw synchronously and stop the server, so refuse it with the escapes.
  if (rel.includes('\0') || !file.startsWith(ROOT + path.sep)) { res.writeHead(403); return res.end(); }
  fs.readFile(file, (err, data) => {
    if (err) { res.writeHead(404, { 'Content-Type': 'text/plain' }); return res.end('Not found'); }
    res.writeHead(200, { 'Content-Type': TYPES[path.extname(file).toLowerCase()] || 'application/octet-stream' });
    res.end(data);
  });
}).listen(PORT, HOST, () => console.log(`Who Gets Missed: http://${HOST}:${PORT}/  (Ctrl+C to stop)`));
