"""Static-page checks for the n1-311triage UI (task T10).

Verifies the single page at ``/`` serves, wires in the offline map/app scripts,
carries the equity caveat, and meets the readability rules (requirements 16-19):
no external URLs in the three static files, every ``border-radius`` value is 0,
and every ``<th>`` carries a ``scope`` (both the hand-written headers in
``index.html`` and the ones ``app.js`` generates at runtime).
"""
from __future__ import annotations

import os
import re

import pytest
from fastapi.testclient import TestClient

from app import server

_FIXTURES = os.path.join(os.path.dirname(__file__), "fixtures")
_SLICE = os.path.join(_FIXTURES, "311_slice_sample.json.gz")
_EJ = os.path.join(_FIXTURES, "ej_api_sample.json")
_PARAMS = os.path.join(_FIXTURES, "params_sample.json")

_STATIC = os.path.join(os.path.dirname(__file__), "..", "app", "static")
_INDEX = os.path.abspath(os.path.join(_STATIC, "index.html"))
_STYLE = os.path.abspath(os.path.join(_STATIC, "style.css"))
_APP = os.path.abspath(os.path.join(_STATIC, "app.js"))

_CAVEAT = "Shows a pattern in the city's own data, not its cause."


@pytest.fixture()
def client(monkeypatch):
    monkeypatch.setenv("N1_SLICE", _SLICE)
    monkeypatch.setenv("N1_EJ", _EJ)
    monkeypatch.setenv("N1_PARAMS", _PARAMS)
    server.reset_state()
    with TestClient(server.app) as c:
        yield c
    server.reset_state()


def _read(path: str) -> str:
    with open(path, "r", encoding="utf-8") as fh:
        return fh.read()


# --- the three static files exist ----------------------------------------

def test_static_files_exist():
    for path in (_INDEX, _STYLE, _APP):
        assert os.path.isfile(path), f"missing {path}"


# --- GET / serves the page ------------------------------------------------

def test_root_serves_html(client):
    resp = client.get("/")
    assert resp.status_code == 200
    ctype = resp.headers.get("content-type", "")
    assert "html" in ctype.lower()
    body = resp.text
    assert "<html" in body.lower()
    assert "Is my block chronically missed?" in body


# --- index.html loads both scripts ---------------------------------------

def test_index_loads_map_and_app():
    html = _read(_INDEX)
    assert 'src="map.js"' in html, "index.html must load map.js"
    assert 'src="app.js"' in html, "index.html must load app.js"


# --- caveat present -------------------------------------------------------

def test_caveat_present():
    index = _read(_INDEX)
    app = _read(_APP)
    assert _CAVEAT in index or _CAVEAT in app, "equity caveat text must be present"


# --- no external URLs in the three files ----------------------------------

def test_no_external_urls():
    for path in (_INDEX, _STYLE, _APP):
        text = _read(path)
        assert "http://" not in text, f"http:// found in {path}"
        assert "https://" not in text, f"https:// found in {path}"


# --- border-radius is always 0 -------------------------------------------

def test_border_radius_always_zero():
    for path in (_INDEX, _STYLE, _APP):
        text = _read(path)
        for match in re.finditer(
            r"border-radius\s*:\s*([^;\n}]+)", text, re.IGNORECASE
        ):
            value = match.group(1).strip().strip("\"'")
            assert value in ("0", "0px"), f"border-radius must be 0 in {path}, got {value!r}"


# --- every <th> in index.html has scope ----------------------------------

def test_index_th_has_scope():
    html = _read(_INDEX)
    ths = re.findall(r"<th\b[^>]*>", html, re.IGNORECASE)
    assert ths, "expected at least one <th> in index.html"
    for th in ths:
        assert re.search(r"\bscope\s*=", th, re.IGNORECASE), f"<th> without scope: {th}"


# --- app.js sets scope on every generated th -----------------------------

def test_app_js_generates_th_with_scope():
    app = _read(_APP)
    # Every cell("th", ...) call that builds a header must pass a scope attr.
    th_calls = re.findall(r'cell\(\s*"th"[^)]*\)', app)
    assert th_calls, "expected app.js to generate <th> cells"
    for call in th_calls:
        assert "scope" in call, f'app.js generated a <th> without scope: {call}'


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(pytest.main([__file__, "-q"]))
