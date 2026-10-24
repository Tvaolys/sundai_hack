from pathlib import Path

from hypothesis import given
from hypothesis import strategies as st

from app.sla import chronic, group_stats, load_params

PARAMS_PATH = Path(__file__).resolve().parent.parent / "data" / "params.json"


# --- load_params --------------------------------------------------------


def test_load_params_defaults():
    params = load_params()
    assert params["cluster_distance_m"] == 50
    assert params["cluster_window_days"] == 14
    assert params["min_n"] == 20
    assert params["lim_eng_pct_threshold"] == 25
    assert params["window_start"] == "2026-01-01"
    assert params["exclude_sources"] == ["Employee Generated", "City Worker App"]
    assert params["placeholder"] is True


def test_load_params_explicit_path():
    assert load_params(PARAMS_PATH)["min_n"] == 20


# --- group_stats --------------------------------------------------------


def test_group_stats_basic():
    cases = [
        {"on_time": True, "is_open": False},
        {"on_time": False, "is_open": False},
        {"on_time": False, "is_open": True},
        {"on_time": None, "is_open": True},
    ]
    stats = group_stats(cases)
    assert stats == {
        "total": 4,
        "open": 2,
        "known": 3,
        "late": 2,
        "rate": 2 / 3,
    }


def test_group_stats_empty_rate_none():
    assert group_stats([])["rate"] is None


def test_group_stats_all_unknown_rate_none():
    cases = [{"on_time": None, "is_open": False}, {"on_time": None, "is_open": True}]
    stats = group_stats(cases)
    assert stats["known"] == 0
    assert stats["late"] == 0
    assert stats["rate"] is None
    assert stats["total"] == 2


# --- chronic ------------------------------------------------------------


def test_chronic_ordering_and_too_few():
    cases = []
    # cat A: 10 known, 8 late -> rate 0.8
    cases += [{"category": "A", "on_time": False, "is_open": False}] * 8
    cases += [{"category": "A", "on_time": True, "is_open": False}] * 2
    # cat B: 10 known, 5 late -> rate 0.5
    cases += [{"category": "B", "on_time": False, "is_open": False}] * 5
    cases += [{"category": "B", "on_time": True, "is_open": False}] * 5
    # cat C: 10 known, 8 late -> rate 0.8, same as A, fewer late? equal late=8
    # make C have same rate 0.8 but tie-broken by category asc (A before C)
    cases += [{"category": "C", "on_time": False, "is_open": False}] * 8
    cases += [{"category": "C", "on_time": True, "is_open": False}] * 2
    # cat D: too few (known < min_n=5)
    cases += [{"category": "D", "on_time": False, "is_open": False}] * 2

    result = chronic(cases, min_n=5, top=3)
    ranked = result["ranked"]
    assert [r["category"] for r in ranked] == ["A", "C", "B"]
    assert result["too_few"] == ["D"]
    assert ranked[0]["rate"] == 0.8
    assert ranked[0]["late"] == 8
    assert ranked[0]["known"] == 10


def test_chronic_top_limit():
    cases = []
    for i, rate_num in enumerate([9, 8, 7, 6]):
        cat = f"cat{i}"
        cases += [{"category": cat, "on_time": False, "is_open": False}] * rate_num
        cases += [{"category": cat, "on_time": True, "is_open": False}] * (10 - rate_num)
    result = chronic(cases, min_n=5, top=3)
    assert len(result["ranked"]) == 3
    assert [r["category"] for r in result["ranked"]] == ["cat0", "cat1", "cat2"]


def test_chronic_late_count_tiebreak():
    cases = []
    # both rate 0.5 but A has more late (knowns differ)
    cases += [{"category": "A", "on_time": False, "is_open": False}] * 10
    cases += [{"category": "A", "on_time": True, "is_open": False}] * 10
    cases += [{"category": "B", "on_time": False, "is_open": False}] * 5
    cases += [{"category": "B", "on_time": True, "is_open": False}] * 5
    result = chronic(cases, min_n=5, top=3)
    assert [r["category"] for r in result["ranked"]] == ["A", "B"]


# --- property tests -----------------------------------------------------

case_strat = st.fixed_dictionaries(
    {
        "category": st.sampled_from(["A", "B", "C", "D", "E"]),
        "on_time": st.sampled_from([True, False, None]),
        "is_open": st.booleans(),
    }
)


@given(st.lists(case_strat, max_size=200))
def test_group_stats_invariants(cases):
    stats = group_stats(cases)
    assert stats["late"] <= stats["known"] <= stats["total"]
    assert 0 <= stats["open"] <= stats["total"]
    if stats["rate"] is not None:
        assert 0.0 <= stats["rate"] <= 1.0
    else:
        assert stats["known"] == 0


@given(st.lists(case_strat, max_size=200), st.integers(min_value=1, max_value=50))
def test_chronic_invariants(cases, min_n):
    result = chronic(cases, min_n=min_n, top=3)
    ranked = result["ranked"]
    assert len(ranked) <= 3
    for r in ranked:
        # never below min_n
        assert r["known"] >= min_n
        # rate in [0, 1] and late <= known
        assert 0.0 <= r["rate"] <= 1.0
        assert r["late"] <= r["known"]
    # ranking non-increasing in rate
    rates = [r["rate"] for r in ranked]
    assert all(rates[i] >= rates[i + 1] for i in range(len(rates) - 1))
    # full ordering key non-increasing (rate desc, late desc, category asc)
    keys = [(-r["rate"], -r["late"], r["category"]) for r in ranked]
    assert keys == sorted(keys)
    # too_few categories genuinely have known < min_n
    by_cat = {}
    for c in cases:
        by_cat.setdefault(c["category"], []).append(c)
    for cat in result["too_few"]:
        assert group_stats(by_cat[cat])["known"] < min_n
