from fpl.eval import replay
from fpl.eval.measures import ranking
from fpl.eval.pool import pool


def make(scores, real, cost=None, minutes=None, teams=None):
    n = len(real)
    elements = [{"id": i, "team": (teams or {}).get(i, 1), "minutes": (minutes or {}).get(i, 90),
                 "total_points": 0, "now_cost": (cost or {}).get(i, 50)} for i in range(1, n + 1)]
    feed = {"bootstrap": {"elements": elements},
            "fixtures": [{"event": 2, "team_h": 1, "team_a": 2},
                         {"event": 3, "team_h": 3, "team_a": 4}]}
    return replay.Gameweek(2, feed, dict(enumerate(real, 1)), None,
                           {"current": dict(enumerate(scores, 1))})


def test_pool_excludes_no_minutes_and_blank_club():
    gw = make([1] * 4, [1] * 4, minutes={2: 0}, teams={3: 3})
    assert [el["id"] for el in pool(gw.feed, 2)] == [1, 4]


def test_perfect_and_reversed():
    out = ranking.measure(make([4, 3, 2, 1], [8, 6, 4, 2], cost={1: 90, 2: 80, 3: 70, 4: 60}))
    assert out == {"ranking current": 1.0, "ranking price": 1.0}
    out = ranking.measure(make([1, 2, 3, 4], [8, 6, 4, 2], cost={1: 60, 2: 70, 3: 80, 4: 90}))
    assert out == {"ranking current": -1.0, "ranking price": -1.0}


def test_all_equal_is_none_and_mean_skips():
    assert ranking.measure(make([5] * 4, [8, 6, 4, 2]))["ranking current"] is None
    assert ranking.columns(["current"]) == ["ranking current", "ranking price"]
    assert ranking.total("ranking current", [1.0, 0.0]) == 0.5
