from datetime import timedelta

from fpl.eval import replay
from tests.evalfeed import default_points as pts, kickoff, make_eval

POINTS = pts


def el(feed, i):
    return next(e for e in feed["bootstrap"]["elements"] if e["id"] == i)


def build(d, gw, now=None):
    return replay.as_of(d["bootstrap"], d["fixtures"], d["lives"], gw, now)


def test_sums_use_only_earlier_gameweeks():
    e = el(build(make_eval(), 3), 4)  # lives of gameweeks 3-5 are present and must be ignored
    assert e["minutes"] == 180
    assert e["total_points"] == pts(4, 1) + pts(4, 2)
    assert e["appearances"] == 2
    assert e["points_per_game"] == round((pts(4, 1) + pts(4, 2)) / 2, 1)


def test_double_gameweek_counts_two_matches():
    d = make_eval()
    row = d["lives"][1]["elements"][3]  # element 4, gameweek 1: a second match
    row["explain"].append({"fixture": 99, "stats": [{"identifier": "minutes", "points": 2, "value": 60}]})
    row["stats"]["total_points"] += 2
    e = el(build(d, 2), 4)
    assert e["appearances"] == 2
    assert e["points_per_game"] == round((pts(4, 1) + 2) / 2, 1)


def test_no_appearance_means_zero():
    e = el(build(make_eval(), 2), 1)
    assert e["appearances"] == 1
    d = make_eval()
    for row in d["lives"][1]["elements"]:
        row["explain"][0]["stats"][0]["value"] = 0
    e = el(build(d, 2), 1)
    assert e["appearances"] == 0 and e["points_per_game"] == 0.0


def test_form_window_includes_29_days_and_excludes_31():
    d = make_eval()
    p = {g: pts(4, g) for g in (1, 2, 3)}
    inside = el(build(d, 4, now=kickoff(1) + timedelta(days=29)), 4)["form"]
    outside = el(build(d, 4, now=kickoff(1) + timedelta(days=31)), 4)["form"]
    assert inside == round((p[1] + p[2] + p[3]) / 3, 1)
    assert outside == round((p[2] + p[3]) / 2, 1)


def test_today_values_do_not_leak():
    d = make_eval()
    before = build(d, 4)
    for e in d["bootstrap"]["elements"]:
        e.update(form="0.1", points_per_game="0.2", minutes=1, total_points=2,
                 status="u", news="out", chance_of_playing_next_round=0)
        e["now_cost"] += 10  # a price rise: start price is unchanged
        e["cost_change_start"] += 10
    assert build(d, 4) == before
    e = el(before, 4)
    assert e["status"] == "a" and e["news"] == "" and e["chance_of_playing_next_round"] is None


def test_start_price():
    assert el(build(make_eval(), 2), 4)["now_cost"] == 50 + 4 - 3


def test_fixture_after_deadline_is_not_finished():
    feed = build(make_eval(), 3)
    done = {f["event"] for f in feed["fixtures"] if f["finished"]}
    assert done == {1, 2}
    nxt = [e["id"] for e in feed["bootstrap"]["events"] if e["is_next"]]
    assert nxt == [3]


def test_unchecked_and_first_gameweek_skipped():
    d = make_eval()
    assert replay.gameweeks(d["bootstrap"])[0] == [2, 3, 4, 5]
    d["bootstrap"]["events"][4]["data_checked"] = False
    todo, notes, n = replay.gameweeks(d["bootstrap"])
    assert todo == [2, 3, 4] and n == 5
    assert "GW1 skipped" in notes and "GW5 not data-checked" in notes


def test_real_points():
    d = make_eval()
    assert replay.real_points(d["lives"][2])[4] == pts(4, 2)
