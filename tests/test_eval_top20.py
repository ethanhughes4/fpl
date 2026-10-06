from fpl.eval import replay
from fpl.eval.measures import top20


def make(n, scores, real, cost=None, tp=None):
    elements = [{"id": i, "team": 1, "minutes": 90, "total_points": (tp or {}).get(i, 0),
                 "now_cost": (cost or {}).get(i, 50)} for i in range(1, n + 1)]
    feed = {"bootstrap": {"elements": elements}, "fixtures": [{"event": 2, "team_h": 1, "team_a": 2}]}
    return replay.Gameweek(2, feed, {i: real(i) for i in range(1, n + 1)}, None,
                           {"current": {i: scores(i) for i in range(1, n + 1)}})


def test_picks_top_n_by_projection_and_price():
    gw = make(25, lambda i: i, lambda i: i, cost={i: 100 - i for i in range(1, 26)})
    out = top20.measure(gw)
    assert out["top20 current"] == sum(range(6, 26)) / 20
    assert out["top20 price"] == sum(range(1, 21)) / 20


def test_ties_by_total_points_then_id():
    gw = make(21, lambda i: 1, lambda i: 100 if i == 21 else 0, tp={21: 5})
    assert top20.measure(gw)["top20 current"] == 5  # 21 wins the tie, so it is in
    gw = make(21, lambda i: 1, lambda i: 100 if i == 21 else 0)
    assert top20.measure(gw)["top20 current"] == 0  # lower ids win, 21 is out


def test_small_pool_and_total():
    assert top20.measure(make(3, lambda i: i, lambda i: i * 2))["top20 current"] == 4
    assert top20.columns(["current"]) == ["top20 current", "top20 price"]
    assert top20.total("top20 current", [1.5, 2.0]) == 3.5
