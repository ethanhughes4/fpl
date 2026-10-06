from pathlib import Path

from fpl import brief, feed as feedmod, score
from fpl.explain.parts import breakdown

DATA = Path(__file__).parent / "data"


def el(i, price, base, n=4):
    return {"id": i, "element_type": 3, "now_cost": price, "form": base, "points_per_game": base,
            "minutes": 90, "appearances": n}


def test_example_a_captain_by_hand():
    f = feedmod.load(str(DATA / "example_a"))
    line = next(x for x in breakdown.lines(brief.build(f), f) if x.strip().startswith("Hart"))
    # Hart: base 8.0, 12 games, typical 7.6 -> (12*8.0 + 3*7.6) / 15 = 7.92
    for part in ["Hart (MID)", "form 8.0", "points per game 8.0", "minutes factor 1.0",
                 "next opponent T4 (H)", "fixture difficulty 3", "playing chance 100%",
                 "next-GW score 7.9", "games played 12", "start price 7.6",
                 "base 8.0 before shrink and 7.9 after"]:
        assert part in line


def test_who_is_listed():
    f = feedmod.load(str(DATA / "example_a"))
    text = "\n".join(breakdown.lines(brief.build(f), f))
    for n in ["Hart", "Marsh", "Orr"]:
        assert f"  {n} (" in text
    assert "Score breakdowns" in text


def test_typical_is_regression_line():
    # points (40, 2), (60, 4), (80, 6) lie on base = 0.1 * price - 2
    t = score.typical_bases([el(1, 40, 2.0), el(2, 60, 4.0), el(3, 80, 6.0)])
    assert all(abs(t[i] - b) < 1e-9 for i, b in [(1, 2.0), (2, 4.0), (3, 6.0)])


def test_typical_skips_unfittable():
    assert score.typical_bases([el(1, 60, 2.0), el(2, 60, 4.0)]) == {}
