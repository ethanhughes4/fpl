from fpl.eval import replay
from fpl.eval.measures import eleven

# squad ids: 1-2 GK, 3-7 DEF, 8-12 MID, 13-15 FWD (hand example (b); M5 = 12, F3 = 15)
POS = [1, 1, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 4, 4, 4]
PROJ = [4.0, 3.0, 4.0, 3.9, 3.8, 1.0, 0.9, 5.0, 4.9, 4.8, 4.7, 1.0, 4.5, 4.4, 4.3]
REAL = [6, 1, 2, 2, 2, 9, 8, 3, 3, 3, 3, 0, 2, 1, 1]


def example_b(positions=None):
    elements = [{"id": i, "element_type": p, "team": 1, "total_points": 10}
                for i, p in enumerate(POS, 1)]
    first = [1, 3, 4, 5, 6, 8, 9, 10, 11, 13, 14]  # GK1, D1-D4, M1-M4, F1, F2
    order = first + [2, 7, 12, 15]  # then the bench
    pos = positions or [order.index(i) + 1 for i in range(1, 16)]
    picks = {"picks": [{"element": i, "position": pos[i - 1], "is_captain": i == 3}
                       for i in range(1, 16)]}
    feed = {"bootstrap": {"elements": elements}}
    return replay.Gameweek(2, feed, dict(enumerate(REAL, 1)),
                           picks, {"current": dict(enumerate(PROJ, 1))})


def test_hand_example_b():
    # captain is D1 (real 2): no doubling anywhere
    assert eleven.measure(example_b()) == {
        "eleven current": 28, "eleven mine": 36, "eleven best": 43}


def test_mine_uses_positions_1_to_11_whatever_the_scores():
    # put the two top-scoring defenders (6, 7) in the first eleven, M3/M4 (10, 11) on the bench
    pos = [1, 12, 2, 3, 4, 5, 6, 7, 8, 13, 14, 9, 10, 11, 15]
    out = eleven.measure(example_b(pos))
    ids = [i for i in range(1, 16) if pos[i - 1] <= 11]
    assert out["eleven mine"] == sum(REAL[i - 1] for i in ids)
    assert out["eleven current"] == 28


def test_columns_and_total():
    assert eleven.columns(["current", "shrink"]) == [
        "eleven current", "eleven shrink", "eleven mine", "eleven best"]
    assert eleven.total("eleven mine", [36, 2]) == 38
