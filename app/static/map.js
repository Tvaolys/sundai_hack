// n1-311triage offline SVG map (task T9).
//
// drawMap(svgEl, data, opts) renders the /api/map payload into an SVG element
// with no external resources: block-group outlines as <path>, one marker per
// cluster, and a text legend. Everything is drawn with the SVG DOM so the demo
// works fully offline (no Leaflet, no tiles, no CDN).
//
// Data shape (from app/server.py map_view):
//   { bbox: {min_lon, min_lat, max_lon, max_lat},   // values may be null
//     block_groups: [{geoid, limited_english, rings}],  // rings: [[ [lon,lat], ... ], ...]
//     markers: [{id, lat, lon, size, late, has_late, category?}] }
//
// Late vs on-time is distinguished by SHAPE and COLOR (req 11):
//   has_late  -> filled square  #b00020
//   all ontime-> hollow circle  stroke #1a5e1a 2px
// Limited-English EJ block groups use a hatched pattern (not color alone, req 18).
//
// Exported as window.N1Map.drawMap (app.js in T10 calls it). No rounded corners.

(function (global) {
  "use strict";

  var SVG_NS = "http://www.w3.org/2000/svg";

  // Colors (kept in sync with design.md).
  var COLOR_LATE = "#b00020"; // filled square
  var COLOR_ONTIME = "#1a5e1a"; // hollow circle stroke
  var COLOR_LE_OUTLINE = "#111"; // limited-English block-group outline
  var COLOR_OTHER_FILL = "#eee"; // other EJ block-group fill
  var COLOR_OTHER_OUTLINE = "#555"; // other EJ block-group outline
  var COLOR_TEXT = "#111";

  function el(name, attrs) {
    var node = document.createElementNS(SVG_NS, name);
    if (attrs) {
      for (var k in attrs) {
        if (Object.prototype.hasOwnProperty.call(attrs, k)) {
          node.setAttribute(k, String(attrs[k]));
        }
      }
    }
    return node;
  }

  // Clear every child of a node (so drawMap can be called repeatedly).
  function clear(node) {
    while (node.firstChild) {
      node.removeChild(node.firstChild);
    }
  }

  function num(v) {
    return typeof v === "number" && isFinite(v);
  }

  // Compute a bbox from the data: prefer data.bbox, else derive from geometry.
  function resolveBbox(data) {
    var b = data && data.bbox;
    if (
      b &&
      num(b.min_lon) &&
      num(b.min_lat) &&
      num(b.max_lon) &&
      num(b.max_lat)
    ) {
      return {
        minLon: b.min_lon,
        minLat: b.min_lat,
        maxLon: b.max_lon,
        maxLat: b.max_lat,
      };
    }
    // Fallback: scan block-group rings and markers.
    var minLon = Infinity;
    var minLat = Infinity;
    var maxLon = -Infinity;
    var maxLat = -Infinity;
    var bgs = (data && data.block_groups) || [];
    for (var i = 0; i < bgs.length; i++) {
      var rings = bgs[i].rings || [];
      for (var r = 0; r < rings.length; r++) {
        var ring = rings[r];
        for (var p = 0; p < ring.length; p++) {
          var lon = ring[p][0];
          var lat = ring[p][1];
          if (lon < minLon) minLon = lon;
          if (lon > maxLon) maxLon = lon;
          if (lat < minLat) minLat = lat;
          if (lat > maxLat) maxLat = lat;
        }
      }
    }
    var markers = (data && data.markers) || [];
    for (var m = 0; m < markers.length; m++) {
      var mk = markers[m];
      if (num(mk.lon) && num(mk.lat)) {
        if (mk.lon < minLon) minLon = mk.lon;
        if (mk.lon > maxLon) maxLon = mk.lon;
        if (mk.lat < minLat) minLat = mk.lat;
        if (mk.lat > maxLat) maxLat = mk.lat;
      }
    }
    if (!isFinite(minLon) || !isFinite(minLat)) {
      // Nothing to draw: default to a tiny Boston-ish box.
      return { minLon: -71.1, minLat: 42.3, maxLon: -71.0, maxLat: 42.4 };
    }
    // Guard against a zero-span box.
    if (maxLon === minLon) {
      maxLon += 1e-4;
      minLon -= 1e-4;
    }
    if (maxLat === minLat) {
      maxLat += 1e-4;
      minLat -= 1e-4;
    }
    return { minLon: minLon, minLat: minLat, maxLon: maxLon, maxLat: maxLat };
  }

  // Build an equirectangular projection into [pad, W-pad] x [pad, H-pad].
  // x is scaled by cos(mid-lat) so the aspect ratio is not distorted. Latitude
  // increases upward, so screen-y is flipped. The map content is centered.
  function makeProjection(bbox, width, height, pad) {
    var midLat = (bbox.minLat + bbox.maxLat) / 2;
    var cosLat = Math.cos((midLat * Math.PI) / 180);
    if (cosLat <= 0) cosLat = 1e-6;

    // Geographic spans in "projected" units (x already scaled by cosLat).
    var spanX = (bbox.maxLon - bbox.minLon) * cosLat;
    var spanY = bbox.maxLat - bbox.minLat;
    if (spanX <= 0) spanX = 1e-9;
    if (spanY <= 0) spanY = 1e-9;

    var availW = width - 2 * pad;
    var availH = height - 2 * pad;
    // One scale for both axes -> keeps aspect ratio (no stretching).
    var scale = Math.min(availW / spanX, availH / spanY);

    var drawW = spanX * scale;
    var drawH = spanY * scale;
    var offX = pad + (availW - drawW) / 2;
    var offY = pad + (availH - drawH) / 2;

    return function project(lon, lat) {
      var px = offX + (lon - bbox.minLon) * cosLat * scale;
      // Flip y: higher latitude -> smaller screen y.
      var py = offY + (bbox.maxLat - lat) * scale;
      return [px, py];
    };
  }

  // Convert one polygon's rings into an SVG path "d" string.
  function ringsToPath(rings, project) {
    var d = "";
    for (var r = 0; r < rings.length; r++) {
      var ring = rings[r];
      if (!ring || ring.length === 0) continue;
      for (var p = 0; p < ring.length; p++) {
        var xy = project(ring[p][0], ring[p][1]);
        d += (p === 0 ? "M" : "L") + xy[0].toFixed(2) + " " + xy[1].toFixed(2);
        if (p !== ring.length - 1) d += " ";
      }
      d += "Z";
    }
    return d;
  }

  // sqrt(size) scaled to a radius clamped to [4, 18] px.
  function markerRadius(size) {
    var s = num(size) && size > 0 ? size : 1;
    var r = Math.sqrt(s) * 3; // sqrt scaling; factor keeps mid sizes readable
    if (r < 4) r = 4;
    if (r > 18) r = 18;
    return r;
  }

  // Build the <defs> hatched pattern used to fill limited-English block groups.
  function makeHatchDefs() {
    var defs = el("defs");
    var pattern = el("pattern", {
      id: "n1-hatch",
      patternUnits: "userSpaceOnUse",
      width: 6,
      height: 6,
    });
    // A light background so the outline/markers stay readable, plus diagonal
    // strokes so the pattern (not color alone) marks limited-English groups.
    pattern.appendChild(
      el("rect", { x: 0, y: 0, width: 6, height: 6, fill: "#fff" })
    );
    pattern.appendChild(
      el("path", {
        d: "M0 6 L6 0 M-1 1 L1 -1 M5 7 L7 5",
        stroke: "#555",
        "stroke-width": 1,
      })
    );
    defs.appendChild(pattern);
    return defs;
  }

  function titleFor(marker) {
    var label =
      marker && typeof marker.category === "string" && marker.category
        ? marker.category
        : "Cluster";
    var size = num(marker.size) ? marker.size : 0;
    var late = num(marker.late) ? marker.late : 0;
    return label + ": " + size + " reports, " + late + " late";
  }

  // Attach keyboard + click handlers that call opts.onSelect(id).
  function wireSelect(node, id, onSelect) {
    node.setAttribute("tabindex", "0");
    node.setAttribute("role", "button");
    if (typeof onSelect !== "function") return;
    node.addEventListener("click", function () {
      onSelect(id);
    });
    node.addEventListener("keydown", function (ev) {
      if (ev.key === "Enter" || ev.key === " " || ev.key === "Spacebar") {
        ev.preventDefault();
        onSelect(id);
      }
    });
  }

  // Draw a text legend group (returned so the caller can place it too).
  function makeLegend(width, height) {
    var pad = 8;
    var lineH = 22;
    var g = el("g", { class: "n1-legend", "aria-hidden": "false" });

    // Opaque backing box so legend text stays readable over geometry.
    var boxW = 320;
    var boxH = lineH * 4 + pad * 2;
    var boxY = height - boxH - pad;
    g.appendChild(
      el("rect", {
        x: pad,
        y: boxY,
        width: boxW,
        height: boxH,
        fill: "#fff",
        stroke: "#111",
        "stroke-width": 2,
        rx: 0,
        ry: 0,
      })
    );

    var swatchX = pad + 10;
    var textX = pad + 34;
    var rowY = boxY + pad + 14;

    // Row 1: filled square -> late reports.
    g.appendChild(
      el("rect", {
        x: swatchX,
        y: rowY - 10,
        width: 14,
        height: 14,
        fill: COLOR_LATE,
        rx: 0,
        ry: 0,
      })
    );
    g.appendChild(legendText(textX, rowY, "Late reports in cluster"));

    // Row 2: hollow circle -> all on time.
    rowY += lineH;
    g.appendChild(
      el("circle", {
        cx: swatchX + 7,
        cy: rowY - 3,
        r: 6,
        fill: "none",
        stroke: COLOR_ONTIME,
        "stroke-width": 2,
      })
    );
    g.appendChild(legendText(textX, rowY, "All on time"));

    // Row 3: hatched swatch -> limited-English EJ block group.
    rowY += lineH;
    g.appendChild(
      el("rect", {
        x: swatchX,
        y: rowY - 10,
        width: 14,
        height: 14,
        fill: "url(#n1-hatch)",
        stroke: COLOR_LE_OUTLINE,
        "stroke-width": 2,
        rx: 0,
        ry: 0,
      })
    );
    g.appendChild(
      legendText(textX, rowY, "Limited-English EJ block group")
    );

    // Row 4: grey swatch -> other EJ block group.
    rowY += lineH;
    g.appendChild(
      el("rect", {
        x: swatchX,
        y: rowY - 10,
        width: 14,
        height: 14,
        fill: COLOR_OTHER_FILL,
        stroke: COLOR_OTHER_OUTLINE,
        "stroke-width": 2,
        rx: 0,
        ry: 0,
      })
    );
    g.appendChild(legendText(textX, rowY, "Other EJ block group"));

    return g;
  }

  function legendText(x, y, text) {
    var t = el("text", {
      x: x,
      y: y,
      fill: COLOR_TEXT,
      "font-size": 16,
      "font-family": "sans-serif",
    });
    t.appendChild(document.createTextNode(text));
    return t;
  }

  /**
   * Draw the map into svgEl.
   * @param {SVGSVGElement} svgEl target <svg> element
   * @param {Object} data /api/map payload
   * @param {Object} [opts] { width, height, padding, onSelect(id) }
   * @returns {SVGGElement} the legend group (also appended to svgEl)
   */
  function drawMap(svgEl, data, opts) {
    opts = opts || {};
    data = data || {};
    var width = num(opts.width) ? opts.width : 800;
    var height = num(opts.height) ? opts.height : 600;
    var pad = num(opts.padding) ? opts.padding : 20;
    var onSelect = opts.onSelect;

    clear(svgEl);
    svgEl.setAttribute("viewBox", "0 0 " + width + " " + height);
    svgEl.setAttribute("preserveAspectRatio", "xMidYMid meet");
    svgEl.setAttribute("role", "img");
    if (!svgEl.getAttribute("aria-label")) {
      svgEl.setAttribute(
        "aria-label",
        "Map of 311 report clusters and environmental-justice block groups"
      );
    }

    svgEl.appendChild(makeHatchDefs());

    // White background (no dark theme, req 16).
    svgEl.appendChild(
      el("rect", {
        x: 0,
        y: 0,
        width: width,
        height: height,
        fill: "#fff",
        rx: 0,
        ry: 0,
      })
    );

    var bbox = resolveBbox(data);
    var project = makeProjection(bbox, width, height, pad);

    // Block-group outlines.
    var bgs = data.block_groups || [];
    var bgGroup = el("g", { class: "n1-block-groups" });
    for (var i = 0; i < bgs.length; i++) {
      var bg = bgs[i];
      var rings = bg.rings || [];
      if (!rings.length) continue;
      var d = ringsToPath(rings, project);
      if (!d) continue;
      var path;
      if (bg.limited_english) {
        path = el("path", {
          d: d,
          fill: "url(#n1-hatch)",
          "fill-rule": "evenodd",
          stroke: COLOR_LE_OUTLINE,
          "stroke-width": 2.5,
        });
      } else {
        path = el("path", {
          d: d,
          fill: COLOR_OTHER_FILL,
          "fill-rule": "evenodd",
          stroke: COLOR_OTHER_OUTLINE,
          "stroke-width": 1,
        });
      }
      if (bg.geoid != null) path.setAttribute("data-geoid", String(bg.geoid));
      bgGroup.appendChild(path);
    }
    svgEl.appendChild(bgGroup);

    // Cluster markers.
    var markers = data.markers || [];
    var markerGroup = el("g", { class: "n1-markers" });
    for (var m = 0; m < markers.length; m++) {
      var mk = markers[m];
      if (!num(mk.lon) || !num(mk.lat)) continue;
      var xy = project(mk.lon, mk.lat);
      var cx = xy[0];
      var cy = xy[1];
      var radius = markerRadius(mk.size);
      var node;
      if (mk.has_late) {
        // Filled square centered on (cx, cy); side ~ 2*radius.
        var side = radius * 2;
        node = el("rect", {
          x: cx - radius,
          y: cy - radius,
          width: side,
          height: side,
          fill: COLOR_LATE,
          stroke: "#111",
          "stroke-width": 1,
          rx: 0,
          ry: 0,
        });
      } else {
        // Hollow circle.
        node = el("circle", {
          cx: cx,
          cy: cy,
          r: radius,
          fill: "none",
          stroke: COLOR_ONTIME,
          "stroke-width": 2,
        });
      }

      var title = el("title");
      title.appendChild(document.createTextNode(titleFor(mk)));
      node.appendChild(title);

      if (mk.id != null) node.setAttribute("data-id", String(mk.id));
      node.setAttribute("aria-label", titleFor(mk));
      node.setAttribute("class", "n1-marker");
      wireSelect(node, mk.id, onSelect);

      markerGroup.appendChild(node);
    }
    svgEl.appendChild(markerGroup);

    // Text legend inside the SVG.
    var legend = makeLegend(width, height);
    svgEl.appendChild(legend);
    return legend;
  }

  var api = { drawMap: drawMap };

  // Export on window.N1Map (plain global, no module system required).
  if (global.N1Map && typeof global.N1Map === "object") {
    global.N1Map.drawMap = drawMap;
  } else {
    global.N1Map = api;
  }

  // Also support CommonJS-style require in case a test harness uses it.
  if (typeof module !== "undefined" && module.exports) {
    module.exports = api;
  }
})(typeof window !== "undefined" ? window : this);
