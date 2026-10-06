from fpl.sections import warnings


def els(feed):
    return {e["id"]: e for e in feed["bootstrap"]["elements"]}


def test_fit_player_no_warning(feed):
    assert warnings.build(feed) == []
    assert warnings.render([]) == ["Warnings: none"]


def test_status_trigger(feed):
    els(feed)[3].update(status="i", news="Knee", chance_of_playing_next_round=0)
    w = warnings.build(feed)
    assert [(x["id"], x["chance"], x["news"]) for x in w] == [(3, 0, "Knee")]
    assert "Knee" in warnings.render(w)[1]


def test_chance_trigger(feed):
    els(feed)[4]["chance_of_playing_next_round"] = 75
    w = warnings.build(feed)
    assert [(x["id"], x["chance"], x["blank"]) for x in w] == [(4, 75, False)]


def test_blank_trigger(feed):
    feed["fixtures"] = [f for f in feed["fixtures"]
                        if not (f["event"] == 6 and 1 in (f["team_h"], f["team_a"]))]
    ids = {x["id"] for x in warnings.build(feed)}
    assert ids == {i for i, e in els(feed).items() if e["team"] in (1, 2)}  # fixture 1 v 2 removed
    assert "no fixture" in warnings.render(warnings.build(feed))[1]
