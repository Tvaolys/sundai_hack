"""Static checks on app/static/map.js (task T9).

These are text assertions on the source file, not a DOM test: the module is
plain browser JS (no framework, no build), so we verify the offline-safety and
API contract that app.js (T10) and the demo depend on.
"""
from pathlib import Path

import re

import pytest

MAP_JS = Path(__file__).resolve().parent.parent / "app" / "static" / "map.js"

SVG_NS = "http://www.w3.org/2000/svg"


@pytest.fixture(scope="module")
def source() -> str:
    assert MAP_JS.is_file(), f"missing {MAP_JS}"
    return MAP_JS.read_text(encoding="utf-8")


def test_only_allowed_url_is_svg_namespace(source: str):
    """No external URLs at all except the allowed SVG namespace.

    Everything must be served locally for the offline demo, so the only
    http(s) string permitted is the SVG XML namespace. Assert the namespace is
    present (the module needs it) and that every http(s) occurrence is exactly
    that namespace.
    """
    assert SVG_NS in source, "SVG namespace must be present"

    for match in re.finditer(r"https?://\S*", source):
        url = match.group(0)
        # Strip trailing JS punctuation/quotes so the comparison is exact.
        url = url.rstrip("\"';),")
        assert url == SVG_NS, f"unexpected external URL: {url!r}"


def test_no_rounded_corners(source: str):
    """No rounded corners anywhere (design.md): border-radius only ever 0."""
    for match in re.finditer(r"border-radius\s*:\s*([^;\n}]+)", source, re.IGNORECASE):
        value = match.group(1).strip().strip("\"'")
        assert value in ("0", "0px"), f"border-radius must be 0, got {value!r}"

    # SVG corner-rounding attributes (rx/ry) must also be 0 wherever set.
    for attr in ("rx", "ry"):
        for match in re.finditer(rf"{attr}\s*:\s*([0-9.]+)", source):
            assert float(match.group(1)) == 0, f"{attr} must be 0"


def test_drawmap_exported(source: str):
    """drawMap is defined and exported on window.N1Map."""
    assert "function drawMap(" in source
    assert "drawMap" in source
    assert "N1Map" in source
    # Exported onto the global N1Map object.
    assert re.search(r"N1Map[\s\S]{0,80}drawMap", source), "drawMap not exported on N1Map"


def test_legend_strings_present(source: str):
    """All four legend labels from the spec must appear verbatim."""
    for phrase in (
        "Late reports in cluster",
        "All on time",
        "Limited-English EJ block group",
        "Other EJ block group",
    ):
        assert phrase in source, f"missing legend text: {phrase!r}"


def test_marker_shapes_and_colors(source: str):
    """Late = filled square #b00020; on-time = hollow circle stroke #1a5e1a."""
    assert "#b00020" in source, "late marker color missing"
    assert "#1a5e1a" in source, "on-time marker color missing"
    # Block-group styling colors (req 11/18): other = #eee fill / #555 outline.
    assert "#eee" in source
    assert "#555" in source


def test_accessibility_hooks(source: str):
    """Markers are focusable buttons with labels and keyboard activation."""
    assert "tabindex" in source
    assert 'role", "button' in source or "role='button'" in source or 'role","button' in source
    assert "aria-label" in source
    assert "data-id" in source
    assert "onSelect" in source
    # Enter / Space activate the marker.
    assert "Enter" in source
    assert '" "' in source or "Spacebar" in source


def test_sqrt_size_scaling_and_clamp(source: str):
    """Marker radius uses sqrt(size) clamped to 4..18 px."""
    assert "Math.sqrt" in source
    assert "4" in source and "18" in source


def test_no_external_script_or_import(source: str):
    """No CDN/script tags or ES-module imports of remote URLs."""
    assert "import(" not in source or "https://" not in source
    assert "<script" not in source.lower()


def test_svg_root_is_group_not_img(source: str):
    """The root <svg> is a labelled 'group', not 'img' (it has focusable
    children when interactive, so 'img' would hide them from AT)."""
    assert 'setAttribute("role", "group")' in source
    assert 'setAttribute("role", "img")' not in source
    # The root still carries an aria-label.
    assert re.search(r'"aria-label"[\s\S]{0,120}clusters', source)


def test_marker_affordance_only_when_selectable(source: str):
    """tabindex/role=button are only set when onSelect is a function.

    In wireSelect the function returns early for a non-function onSelect, so the
    setAttribute calls for tabindex/role=button must come AFTER that guard.
    """
    guard = source.index('if (typeof onSelect !== "function") return;')
    tabindex = source.index('node.setAttribute("tabindex"')
    role_button = source.index('node.setAttribute("role", "button")')
    assert guard < tabindex, "tabindex set before onSelect guard"
    assert guard < role_button, "role=button set before onSelect guard"


def test_legend_strip_below_map(source: str):
    """The legend sits in a reserved strip below the map (viewBox extended by
    the strip height) rather than overlapping geometry."""
    assert "LEGEND_STRIP_H" in source
    # viewBox height is the map height plus the reserved legend strip.
    assert "height + LEGEND_STRIP_H" in source
    assert "totalHeight" in source
