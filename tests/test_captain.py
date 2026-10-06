from fpl.sections import captain, lineup


def _els(feed):
    return {e["id"]: e for e in feed["bootstrap"]["elements"]}


def _set(el, v):
    el["form"] = el["points_per_game"] = v


def test_captain_and_vice(feed):
    els = _els(feed)
    _set(els[13], "9.0")
    _set(els[12], "8.0")
    d = captain.build(feed)
    assert (d["captain"]["id"], d["vice"]["id"]) == (13, 12)
    assert d["captain"]["score"] > d["vice"]["score"]


def test_tie_broken_by_points_then_id(feed):
    els = _els(feed)
    for i in (12, 13, 14):
        _set(els[i], "9.0")
        els[i]["total_points"] = 50
    els[14]["total_points"] = 60
    d = captain.build(feed)
    assert (d["captain"]["id"], d["vice"]["id"]) == (14, 12)


def test_never_bench(feed):
    els = _els(feed)
    _set(els[1], "20.0")
    bench = {r["id"] for r in lineup.build(feed)["bench"]}
    d = captain.build(feed)
    assert not {d["captain"]["id"], d["vice"]["id"]} & bench


def test_render(feed):
    lines = captain.render(captain.build(feed))
    assert lines[0].startswith("Captain: ") and lines[1].startswith("Vice: ")
