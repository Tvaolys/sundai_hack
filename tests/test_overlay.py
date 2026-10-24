from hypothesis import given
from hypothesis import strategies as st

from app.overlay import CAVEAT, NOT_ENOUGH, baseline, compare

# Two block groups: one flagged limited-English, one not.
BGS = [
    {"geoid": "LE1", "limited_english": True},
    {"geoid": "OT1", "limited_english": False},
]


def _case(geoid, on_time, lat=42.3, lon=-71.0):
    return {"geoid": geoid, "on_time": on_time, "is_open": False, "latitude": lat, "longitude": lon}


# --- basic behaviour ----------------------------------------------------


def test_compare_splits_and_rates():
    cases = []
    # limited-English group: 4 known, 3 late -> 0.75
    cases += [_case("LE1", False)] * 3
    cases += [_case("LE1", True)] * 1
    # other: geoid OT1 and None both count as "other"; 4 known, 1 late -> 0.25
    cases += [_case("OT1", False)] * 1
    cases += [_case("OT1", True)] * 1
    cases += [_case(None, True)] * 2

    result = compare(cases, BGS, min_n=2)
    assert result["comparable"] is True
    assert result["message"] is None
    assert result["limited_english"] == {"late": 3, "known": 4, "rate": 0.75}
    assert result["other"] == {"late": 1, "known": 4, "rate": 0.25}
    assert result["caveat"] == CAVEAT
    assert isinstance(result["rule"], str) and result["rule"]


def test_compare_unknown_excluded_from_known():
    cases = []
    cases += [_case("LE1", None)] * 5  # all unknown -> known 0
    cases += [_case("OT1", False)] * 3
    result = compare(cases, BGS, min_n=1)
    assert result["limited_english"]["known"] == 0
    assert result["limited_english"]["late"] == 0
    # limited-English known (0) < min_n -> not comparable
    assert result["comparable"] is False
    assert result["message"] == NOT_ENOUGH
    assert result["limited_english"]["rate"] is None
    assert result["other"]["rate"] is None


def test_compare_unmapped_skipped():
    cases = [
        _case("LE1", False),
        {"geoid": None, "on_time": False, "is_open": False, "latitude": None, "longitude": None},
    ]
    result = compare(cases, BGS, min_n=1)
    # the unmapped (latitude None) case is skipped entirely
    assert result["limited_english"]["known"] == 1
    assert result["other"]["known"] == 0


def test_compare_not_enough_when_other_below_min():
    cases = [_case("LE1", False)] * 5 + [_case("OT1", False)] * 1
    result = compare(cases, BGS, min_n=3)
    assert result["comparable"] is False
    assert result["message"] == NOT_ENOUGH
    assert result["limited_english"]["rate"] is None
    assert result["other"]["rate"] is None
    # counts are still reported
    assert result["limited_english"]["known"] == 5
    assert result["other"]["known"] == 1


def test_compare_none_geoid_counts_as_other():
    cases = [_case(None, False)] * 4 + [_case("LE1", True)] * 2
    result = compare(cases, BGS, min_n=1)
    assert result["other"]["known"] == 4
    assert result["other"]["late"] == 4
    assert result["limited_english"]["known"] == 2


# --- property test ------------------------------------------------------

geoid_strat = st.sampled_from(["LE1", "OT1", None, "UNSEEN"])
case_strat = st.fixed_dictionaries(
    {
        "geoid": geoid_strat,
        "on_time": st.sampled_from([True, False, None]),
        "is_open": st.booleans(),
        # latitude None means unmapped (skipped); otherwise a number.
        "latitude": st.one_of(st.none(), st.just(42.3)),
        "longitude": st.just(-71.0),
    }
)


@given(st.lists(case_strat, max_size=200), st.integers(min_value=1, max_value=50))
def test_compare_invariants(cases, min_n):
    result = compare(cases, BGS, min_n=min_n)
    le = result["limited_english"]
    ot = result["other"]

    # known counts of the two groups sum to mapped cases with a known SLA
    mapped_known = sum(
        1
        for c in cases
        if c["latitude"] is not None and c["on_time"] in (True, False)
    )
    assert le["known"] + ot["known"] == mapped_known

    # rates in [0, 1] when present, else comparable is False
    for grp in (le, ot):
        if grp["rate"] is not None:
            assert 0.0 <= grp["rate"] <= 1.0
        assert grp["late"] <= grp["known"]

    if result["comparable"]:
        assert le["known"] >= min_n and ot["known"] >= min_n
        assert result["message"] is None
        assert le["rate"] is not None and ot["rate"] is not None
    else:
        assert result["message"] == NOT_ENOUGH
        assert le["rate"] is None and ot["rate"] is None

    assert result["caveat"] == CAVEAT


# --- T13: category-mix adjustment ---------------------------------------


def _ccase(geoid, on_time, category, system, lat=42.3, lon=-71.0):
    return {
        "geoid": geoid,
        "on_time": on_time,
        "is_open": False,
        "latitude": lat,
        "longitude": lon,
        "category": category,
        "system": system,
    }


def test_no_base_means_not_adjusted():
    """Without ``base`` the result is unadjusted and carries no expected/excess."""
    cases = [_case("LE1", False)] * 3 + [_case("OT1", True)] * 3
    result = compare(cases, BGS, min_n=1)
    assert result["adjusted"] is False
    assert "expected" not in result["limited_english"]
    assert "excess_pt" not in result["other"]


def test_baseline_city_wide_rates():
    """baseline() is the city-wide late rate per (category, system)."""
    cases = [
        _ccase("LE1", False, "Pothole", "new"),
        _ccase("LE1", True, "Pothole", "new"),
        _ccase("OT1", False, "Pothole", "new"),
        _ccase("OT1", False, "Pothole", "new"),  # Pothole/new: 3 late / 4 known
        _ccase("OT1", True, "Graffiti", "legacy"),  # Graffiti/legacy: 0/1
        _ccase("LE1", None, "Pothole", "new"),  # unknown excluded
    ]
    base = baseline(cases)
    assert base[("Pothole", "new")] == 0.75
    assert base[("Graffiti", "legacy")] == 0.0


def test_excess_zero_when_outcomes_match_baseline():
    """If each (category, system) has identical rates in both groups, excess is 0.

    Construct so Pothole/new is exactly 50% late in BOTH groups: the city-wide
    baseline is then 0.5, each group's observed rate is 0.5, so excess is 0.
    """
    cases = []
    # limited-English group: Pothole/new 2 late + 2 on-time -> 0.5
    cases += [_ccase("LE1", False, "Pothole", "new")] * 2
    cases += [_ccase("LE1", True, "Pothole", "new")] * 2
    # other group: Pothole/new 2 late + 2 on-time -> 0.5
    cases += [_ccase("OT1", False, "Pothole", "new")] * 2
    cases += [_ccase("OT1", True, "Pothole", "new")] * 2

    base = baseline(cases)
    result = compare(cases, BGS, min_n=1, base=base)
    assert result["adjusted"] is True
    assert result["limited_english"]["expected"] == 0.5
    assert result["other"]["expected"] == 0.5
    assert result["limited_english"]["excess_pt"] == 0.0
    assert result["other"]["excess_pt"] == 0.0


def test_excess_zero_mixed_categories():
    """Zero excess holds even with a category mix, as long as each group's
    per-(category, system) rate equals the city-wide rate for that key."""
    cases = []
    # Pothole/new is 100% late everywhere; Graffiti/new is 0% late everywhere.
    for geoid in ("LE1", "OT1"):
        cases += [_ccase(geoid, False, "Pothole", "new")] * 3
        cases += [_ccase(geoid, True, "Graffiti", "new")] * 2
    base = baseline(cases)
    result = compare(cases, BGS, min_n=1, base=base)
    assert result["limited_english"]["excess_pt"] == 0.0
    assert result["other"]["excess_pt"] == 0.0


def test_excess_none_when_not_comparable():
    cases = [_ccase("LE1", False, "Pothole", "new")] * 2 + [
        _ccase("OT1", False, "Pothole", "new")
    ] * 1
    base = baseline(cases)
    result = compare(cases, BGS, min_n=5, base=base)
    assert result["comparable"] is False
    assert result["adjusted"] is True
    assert result["limited_english"]["expected"] is None
    assert result["limited_english"]["excess_pt"] is None
    assert result["other"]["expected"] is None
    assert result["other"]["excess_pt"] is None


def test_rule_mentions_adjustment_only_when_used():
    cases = [_ccase("LE1", False, "Pothole", "new")] * 2 + [
        _ccase("OT1", True, "Pothole", "new")
    ] * 2
    base = baseline(cases)
    plain = compare(cases, BGS, min_n=1)
    adj = compare(cases, BGS, min_n=1, base=base)
    assert "adjust" not in plain["rule"].lower()
    assert "adjust" in adj["rule"].lower()


# --- property test: expected in [0, 1] ----------------------------------

ccase_strat = st.fixed_dictionaries(
    {
        "geoid": st.sampled_from(["LE1", "OT1", None, "UNSEEN"]),
        "on_time": st.sampled_from([True, False, None]),
        "is_open": st.booleans(),
        "latitude": st.one_of(st.none(), st.just(42.3)),
        "longitude": st.just(-71.0),
        "category": st.sampled_from(["Pothole", "Graffiti", "Sidewalk Repair"]),
        "system": st.sampled_from(["new", "legacy"]),
    }
)


@given(st.lists(ccase_strat, max_size=200), st.integers(min_value=1, max_value=50))
def test_expected_in_unit_interval(cases, min_n):
    base = baseline(cases)
    # every baseline rate is itself a valid probability
    for rate in base.values():
        assert 0.0 <= rate <= 1.0
    result = compare(cases, BGS, min_n=min_n, base=base)
    assert result["adjusted"] is True
    for grp in (result["limited_english"], result["other"]):
        expected = grp["expected"]
        if expected is not None:
            assert 0.0 <= expected <= 1.0
