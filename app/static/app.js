// n1-311triage single-page wiring (task T10).
//
// Fetches the /api/* endpoints and renders the design.md layout into index.html.
// Plain browser JS: no framework, no build, no external URLs. The SVG map is
// drawn by window.N1Map.drawMap (app/static/map.js). Status, loading and error
// states are written in words into an aria-live region (req 19); color is never
// the only signal (statuses use words).

(function () {
  "use strict";

  // Caveat always shown on the equity box (requirement 15). Kept here as a
  // constant so the text is present in app.js regardless of API payload.
  var EQUITY_CAVEAT = "Shows a pattern in the city's own data, not its cause.";

  // --- tiny DOM helpers ---------------------------------------------------

  function byId(id) {
    return document.getElementById(id);
  }

  function clear(node) {
    while (node && node.firstChild) {
      node.removeChild(node.firstChild);
    }
  }

  // Create an element with text content (text is set via textContent, so any
  // API string is treated as data, never HTML).
  function cell(tag, text, attrs) {
    var node = document.createElement(tag);
    if (attrs) {
      for (var k in attrs) {
        if (Object.prototype.hasOwnProperty.call(attrs, k)) {
          node.setAttribute(k, attrs[k]);
        }
      }
    }
    if (text !== undefined && text !== null) {
      node.textContent = String(text);
    }
    return node;
  }

  // Row header <th scope="row"> + data cells for a two-column stats table.
  function statRow(label, value) {
    var tr = document.createElement("tr");
    tr.appendChild(cell("th", label, { scope: "row" }));
    tr.appendChild(cell("td", value));
    return tr;
  }

  function setStatus(message) {
    var node = byId("n1-status");
    if (node) node.textContent = message || "";
  }

  // --- formatting ---------------------------------------------------------

  // "41% (82 of 200)" — every rate shows numerator and denominator (req 7).
  function ratePhrase(late, known) {
    if (!known) return "No known results";
    var pct = Math.round((late / known) * 100);
    return pct + "% (" + late + " of " + known + ")";
  }

  function pct1(rate) {
    if (rate === null || rate === undefined) return "—";
    return (rate * 100).toFixed(1) + "%";
  }

  // Excess in points with an explicit sign, e.g. "+4.3" / "-0.2".
  function signedPoints(excess) {
    if (excess === null || excess === undefined) return "—";
    var s = excess >= 0 ? "+" : "";
    return s + excess.toFixed(1) + " pts";
  }

  // On-time status in words, never color alone (req 18).
  function onTimeWord(onTime) {
    if (onTime === true) return "On time";
    if (onTime === false) return "Late";
    return "SLA unknown";
  }

  function dateOnly(iso) {
    if (!iso) return "—";
    return String(iso).slice(0, 10);
  }

  // --- API ----------------------------------------------------------------

  function getJSON(path) {
    return fetch(path, { headers: { Accept: "application/json" } }).then(
      function (resp) {
        if (!resp.ok) {
          throw new Error("Request failed (" + resp.status + ") for " + path);
        }
        return resp.json();
      }
    );
  }

  // --- header / meta ------------------------------------------------------

  function renderMeta(meta) {
    var w = (meta && meta.window) || {};
    var first = dateOnly(w.first_open_date);
    var last = dateOnly(w.last_open_date);
    byId("n1-window").textContent =
      "Data window: " + first + " to " + last + ".";

    var src = (meta && meta.source) || {};
    var sources = [];
    if (src["311"]) sources.push(src["311"]);
    if (src.ej2020) sources.push(src.ej2020);
    byId("n1-sources").textContent = "Sources: " + sources.join("  ");

    var placeholder = meta && meta.params && meta.params.placeholder;
    byId("n1-placeholder").hidden = !placeholder;
  }

  function renderNeighborhoodOptions(list) {
    var select = byId("n1-neighborhood");
    clear(select);
    var ph = cell("option", "Select a neighborhood", { value: "" });
    select.appendChild(ph);
    (list || []).forEach(function (nb) {
      var label = nb.name + " (" + nb.total + " cases)";
      select.appendChild(cell("option", label, { value: nb.name }));
    });
  }

  // --- stats box ----------------------------------------------------------

  function renderStats(stats) {
    var body = byId("n1-stats-body");
    clear(body);
    if (!stats) return;
    body.appendChild(statRow("Total cases", stats.total));
    body.appendChild(statRow("Open cases", stats.open));
    body.appendChild(statRow("Known SLA result", stats.known));
    body.appendChild(statRow("Late cases", stats.late));
    body.appendChild(statRow("Late rate", ratePhrase(stats.late, stats.known)));
  }

  // --- chronic categories -------------------------------------------------

  function renderChronic(chronic) {
    var body = byId("n1-chronic-body");
    clear(body);
    var ranked = (chronic && chronic.ranked) || [];
    if (!ranked.length) {
      var tr = document.createElement("tr");
      var td = cell("td", "No category met the minimum case count.");
      td.setAttribute("colspan", "5");
      tr.appendChild(td);
      body.appendChild(tr);
    } else {
      ranked.forEach(function (row, i) {
        var tr = document.createElement("tr");
        tr.appendChild(cell("th", i + 1, { scope: "row" }));
        tr.appendChild(cell("td", row.category));
        tr.appendChild(cell("td", ratePhrase(row.late, row.known)));
        tr.appendChild(cell("td", row.late));
        tr.appendChild(cell("td", row.known));
        body.appendChild(tr);
      });
    }

    var tooFew = (chronic && chronic.too_few) || [];
    var labels = tooFew.map(function (name) {
      return name === "" ? "(no category)" : name;
    });
    byId("n1-toofew-summary").textContent = labels.length
      ? "TOO FEW CASES: " + labels.length + " categories had fewer than the minimum number of cases and are not ranked."
      : "TOO FEW CASES: none.";
    byId("n1-toofew").textContent = labels.length
      ? "TOO FEW CASES: " + labels.join(", ")
      : "TOO FEW CASES: none.";
  }

  // --- equity box ---------------------------------------------------------

  // Build the one-sentence plain-language reading from the numbers.
  function equityReading(equity, neighborhood) {
    if (!equity || !equity.comparable) {
      return "NOT ENOUGH DATA TO COMPARE for " + neighborhood + ".";
    }
    var le = equity.limited_english || {};
    var other = equity.other || {};
    if (le.excess_pt === null || le.excess_pt === undefined ||
        other.excess_pt === null || other.excess_pt === undefined) {
      return "NOT ENOUGH DATA TO COMPARE for " + neighborhood + ".";
    }
    var diff = le.excess_pt - other.excess_pt;
    if (Math.abs(diff) < 1.0) {
      return (
        "After adjusting for what people report, limited-English blocks are " +
        "about the same as the rest of " + neighborhood + "."
      );
    }
    var worseBetter = diff > 0 ? "worse" : "better";
    return (
      "After adjusting for what people report, limited-English blocks are " +
      Math.abs(diff).toFixed(1) + " points " + worseBetter + " than the rest of " +
      neighborhood + "."
    );
  }

  function equityRow(label, group) {
    var tr = document.createElement("tr");
    tr.appendChild(cell("th", label, { scope: "row" }));
    if (!group || group.rate === null || group.rate === undefined) {
      tr.appendChild(cell("td", "NOT ENOUGH DATA TO COMPARE"));
      tr.appendChild(cell("td", "—"));
      tr.appendChild(cell("td", "—"));
      return tr;
    }
    tr.appendChild(
      cell("td", pct1(group.rate) + " (" + group.late + " of " + group.known + ")")
    );
    tr.appendChild(cell("td", pct1(group.expected)));
    tr.appendChild(cell("td", signedPoints(group.excess_pt)));
    return tr;
  }

  function renderEquity(equity, neighborhood) {
    byId("n1-equity-reading").textContent = equityReading(equity, neighborhood);

    var body = byId("n1-equity-body");
    clear(body);
    if (equity) {
      body.appendChild(equityRow("Limited-English blocks", equity.limited_english));
      body.appendChild(equityRow("Other blocks", equity.other));
    }

    // Always show the caveat (req 15). Prefer the API text, fall back to ours.
    var caveat = (equity && equity.caveat) || EQUITY_CAVEAT;
    byId("n1-equity-caveat").textContent = caveat;
  }

  // --- clusters table + raw rows ------------------------------------------

  function renderClusters(clusters) {
    var body = byId("n1-clusters-body");
    clear(body);
    byId("n1-rows").hidden = true;

    var top = (clusters || []).slice(0, 25);
    if (!top.length) {
      var tr = document.createElement("tr");
      var td = cell("td", "No repeat-report clusters in this neighborhood.");
      td.setAttribute("colspan", "5");
      tr.appendChild(td);
      body.appendChild(tr);
      return;
    }

    top.forEach(function (cl) {
      var tr = document.createElement("tr");
      tr.appendChild(cell("td", cl.category));
      tr.appendChild(cell("td", cl.size));
      tr.appendChild(cell("td", ratePhrase(cl.late, cl.size)));
      tr.appendChild(cell("td", dateOnly(cl.first) + " / " + dateOnly(cl.last)));

      var btnCell = document.createElement("td");
      var btn = cell("button", "Show reports");
      btn.setAttribute("type", "button");
      btn.addEventListener("click", function () {
        openCluster(cl.id);
      });
      btnCell.appendChild(btn);
      tr.appendChild(btnCell);

      body.appendChild(tr);
    });
  }

  function renderClusterRows(detail) {
    var heading = byId("n1-rows-heading");
    heading.textContent =
      "Reports in cluster: " + detail.category + " (" + detail.size + " reports)";

    var body = byId("n1-rows-body");
    clear(body);
    (detail.rows || []).forEach(function (r) {
      var tr = document.createElement("tr");
      tr.appendChild(cell("td", r.case_id));
      tr.appendChild(cell("td", dateOnly(r.open_date)));
      tr.appendChild(cell("td", r.case_status || "—"));
      tr.appendChild(cell("td", onTimeWord(r.on_time)));
      tr.appendChild(cell("td", r.address || "—"));
      body.appendChild(tr);
    });

    byId("n1-rows").hidden = false;
    heading.setAttribute("tabindex", "-1");
    heading.scrollIntoView({ block: "nearest" });
    heading.focus();
  }

  function openCluster(id) {
    if (id === null || id === undefined) return;
    setStatus("Loading reports for the selected cluster…");
    getJSON("/api/cluster/" + encodeURIComponent(id))
      .then(function (detail) {
        renderClusterRows(detail);
        setStatus("Showing " + (detail.rows || []).length + " reports for this cluster.");
      })
      .catch(function (err) {
        setStatus("Could not load that cluster: " + err.message);
      });
  }

  // --- map ----------------------------------------------------------------

  function renderMap(mapData) {
    var svg = byId("n1-map");
    if (!svg || !window.N1Map || typeof window.N1Map.drawMap !== "function") {
      return;
    }
    window.N1Map.drawMap(svg, mapData, {
      width: 800,
      height: 600,
      onSelect: openCluster,
    });
  }

  // --- neighborhood load --------------------------------------------------

  function showNeighborhood(name) {
    if (!name) {
      setStatus("Pick a neighborhood first, then press Show neighborhood.");
      return;
    }
    setStatus("Loading " + name + "…");
    byId("n1-nb-name").textContent = name;

    Promise.all([
      getJSON("/api/neighborhood?name=" + encodeURIComponent(name)),
      getJSON("/api/clusters?name=" + encodeURIComponent(name)),
      getJSON("/api/map?name=" + encodeURIComponent(name)),
    ])
      .then(function (results) {
        var nb = results[0];
        var clusters = results[1];
        var mapData = results[2];

        renderStats(nb.stats);
        renderChronic(nb.chronic);
        renderEquity(nb.equity, name);
        renderClusters(clusters);
        renderMap(mapData);

        byId("n1-results").hidden = false;
        setStatus("Showing results for " + name + ".");
      })
      .catch(function (err) {
        setStatus("Could not load " + name + ": " + err.message);
      });
  }

  // --- bootstrap ----------------------------------------------------------

  function init() {
    setStatus("Loading data…");

    Promise.all([getJSON("/api/meta"), getJSON("/api/neighborhoods")])
      .then(function (results) {
        renderMeta(results[0]);
        renderNeighborhoodOptions(results[1]);
        setStatus("Ready. Pick a neighborhood and press Show neighborhood.");
      })
      .catch(function (err) {
        setStatus("Could not load the data: " + err.message);
      });

    var btn = byId("n1-show");
    if (btn) {
      btn.addEventListener("click", function () {
        showNeighborhood(byId("n1-neighborhood").value);
      });
    }

    // Selecting with the keyboard and pressing Enter also loads.
    var select = byId("n1-neighborhood");
    if (select) {
      select.addEventListener("keydown", function (ev) {
        if (ev.key === "Enter") {
          ev.preventDefault();
          showNeighborhood(select.value);
        }
      });
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
