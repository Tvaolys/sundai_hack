from hypothesis import given
from hypothesis import strategies as st

from app.overlay import CAVEAT, NOT_ENOUGH, compare

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
