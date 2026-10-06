from fpl.eval import replay
from fpl.eval.measures import captain

# squad ids: 1-2 GK, 3-7 DEF, 8-12 MID, 13-15 FWD
POS = [1, 1, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 4, 4, 4]


def example_a():
    """Hand example (a): X (13) projected 7.2 blanks with 2; Y (8) the owner's captain gets 13;
    Z (3) on the bench gets 15."""
    elements = [{"id": i, "element_type": p, "team": 1, "total_points": 10}
                for i, p in enumerate(POS, 1)]
    proj = {i: 4.0 for i in range(1, 16)}
    real = {i: 3 for i in range(1, 16)}
    proj.update({13: 7.2, 8: 6.1, 3: 1.0})
    real.update({13: 2, 8: 13, 3: 15})
    picks = {"picks": [{"element": i, "position": i, "is_captain": i == 8} for i in range(1, 16)]}
    feed = {"bootstrap": {"elements": elements}}
    return replay.Gameweek(2, feed, real, picks, {"current": proj})


def test_hand_example_a():
    out = captain.measure(example_a())
    assert out == {"captain current": 2, "captain mine": 13, "captain best": 15}


def test_columns_and_total():
    assert captain.columns(["current", "shrink"]) == [
        "captain current", "captain shrink", "captain mine", "captain best"]
    assert captain.total("captain mine", [13, 2]) == 15
