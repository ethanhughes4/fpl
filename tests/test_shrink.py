from fpl import score
from fpl.eval.formulas import shrink


def el(i, price, base, n, pos=3, minutes=90):
    return {"id": i, "element_type": pos, "now_cost": price, "form": base, "points_per_game": base,
            "minutes": minutes, "appearances": n}


def test_hand_example_c():
    out = shrink.shrunk_bases([el(1, 40, 2.0, 4), el(2, 80, 6.0, 4), el(3, 60, 6.0, 1), el(4, 60, 6.0, 5)])
    assert abs(out[3] - 5.25) < 1e-9 and abs(out[4] - 5.625) < 1e-9


def test_unfittable_positions_left_alone():
    els = [el(1, 60, 6.0, 1, pos=1), el(2, 60, 2.0, 1, pos=3), el(3, 60, 6.0, 1, pos=3)]
    out = shrink.shrunk_bases(els)
    assert out == {e["id"]: score.base(e) for e in els}


def test_fit_ignores_zero_minutes():
    els = [el(1, 40, 2.0, 4), el(2, 80, 6.0, 4), el(3, 60, 6.0, 1), el(4, 60, 6.0, 5),
           el(5, 100, 0.0, 0, minutes=0)]
    out = shrink.shrunk_bases(els)
    assert abs(out[3] - 5.25) < 1e-9 and out[5] == 0.0
