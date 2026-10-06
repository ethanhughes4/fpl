from fpl import score
from fpl import score as shrink


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


def test_brief_appearances_from_total_and_ppg():
    assert score.appearances({"total_points": 45, "points_per_game": "4.5"}) == 10
    assert score.appearances({"total_points": 0, "points_per_game": "0.0"}) == 0
    assert score.appearances({"total_points": 45, "points_per_game": "4.5", "appearances": 7}) == 7


def test_start_price_in_brief_and_rebuilt_feed():
    assert score.start_price({"now_cost": 62, "cost_change_start": 2}) == 60
    assert score.start_price({"now_cost": 60}) == 60


def test_brief_scores_use_shrunk_base(feed):
    els = feed["bootstrap"]["elements"]
    els[7]["now_cost"], els[7]["points_per_game"] = 90, "9.0"  # a MID far above its position's line
    els[8]["now_cost"] = 70  # a third price, so the line does not pass through P8
    el = els[7]
    assert score.next_score(feed, el) == score.next_score(feed, el, score.shrunk_base(feed, el))
    assert score.next_score(feed, el) != score.next_score(feed, el, score.base(el))
