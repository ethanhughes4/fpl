import pytest

from fpl import score
from tests.fakefeed import fixture, player


def one_fixture_feed(feed, diff=3, team=1):
    feed["fixtures"] = [fixture(1, 6, team, 2, hd=diff),
                        fixture(2, 1, 1, 2, finished=True),
                        fixture(3, 2, 1, 2, finished=True)]
    return feed


def test_base():
    assert score.base(player(1, 3, 1, form="10.0", points_per_game="5.0")) == pytest.approx(8.0)


def test_minutes_factor(feed):
    one_fixture_feed(feed)
    assert score.minutes_factor(feed, player(1, 3, 1, minutes=90)) == 0.5
    assert score.minutes_factor(feed, player(1, 3, 1, minutes=999)) == 1.0


@pytest.mark.parametrize("d,f", [(1, 1.2), (3, 1.0), (5, 0.8)])
def test_fixture_factor(feed, d, f):
    one_fixture_feed(feed, diff=d)
    el = player(1, 3, 1, form="5.0", points_per_game="5.0", minutes=180)
    assert score.next_score(feed, el) == pytest.approx(5 * f)


def test_chance():
    assert score.chance(player(1, 3, 1), 0) == 1
    assert score.chance(player(1, 3, 1, status="d"), 0) == 0  # null, not "a"
    d50 = player(1, 3, 1, status="d", chance_of_playing_next_round=50)
    assert score.chance(d50, 0) == 0.5
    assert score.chance(d50, 3) == 0.75
    assert score.chance(player(1, 3, 1, chance_of_playing_next_round=0), 0) == 0
    for w in range(6):
        assert score.chance(player(1, 3, 1, status="u", chance_of_playing_next_round=100), w) == 0
        assert score.chance(player(1, 3, 1, status="n"), w) == 0


def test_blank_and_double(feed):
    one_fixture_feed(feed)
    el = player(1, 3, 1, minutes=180)
    assert score.gw_score(feed, el, 7) == 0  # blank
    single = score.gw_score(feed, el, 6)
    feed["fixtures"].append(fixture(9, 6, 3, 1))
    assert score.gw_score(feed, el, 6) == pytest.approx(2 * single)


def test_six_week_weights(feed):
    feed["fixtures"] = [fixture(i, g, 1, 2) for i, g in enumerate(range(6, 12), 1)]
    feed["fixtures"].append(fixture(20, 1, 1, 2, finished=True))
    el = player(1, 3, 1, minutes=90)
    one = score.next_score(feed, el)
    assert one > 0
    assert score.six_week_score(feed, el) == pytest.approx(one * 4.5)


def test_tie_break():
    a, b = player(5, 3, 1, total_points=10), player(3, 3, 1, total_points=10)
    c = player(9, 3, 1, total_points=20)
    order = sorted([a, b, c], key=lambda e: score.sort_key(e, 1.0))
    assert [e["id"] for e in order] == [9, 3, 5]
