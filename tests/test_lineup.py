from fpl.sections import lineup


def test_best_eleven(feed):
    els = {e["id"]: e for e in feed["bootstrap"]["elements"]}
    for i in (13, 14, 15):  # strong forwards
        els[i]["form"] = els[i]["points_per_game"] = "9.0"
    for i in (8, 9, 10, 11, 12):  # weak mids
        els[i]["form"] = els[i]["points_per_game"] = "1.0"
    d = lineup.build(feed)
    ids = {r["id"] for r in d["starters"]}
    assert d["formation"] == "5-2-3"
    assert {13, 14, 15} <= ids
    assert len(ids) == 11 and len(d["bench"]) == 4
    assert d["bench"][0]["position"] == "GK"


def test_formation_valid(feed):
    d = lineup.build(feed)
    de, mi, fw = map(int, d["formation"].split("-"))
    assert 3 <= de <= 5 and 2 <= mi <= 5 and 1 <= fw <= 3 and de + mi + fw == 10
    assert sum(r["position"] == "GK" for r in d["starters"]) == 1


def test_render(feed):
    assert lineup.render(lineup.build(feed))[0].startswith("Starting XI (")


def test_best_eleven_from_scores(feed):
    # scores given directly, as the transfer section does for a squad after a swap
    els = feed["bootstrap"]["elements"][:15]
    pos_score = {1: 1.0, 2: 1.0, 3: 0.5, 4: 9.0}  # weak mids, strong forwards
    scored = [(pos_score[e["element_type"]], e) for e in els]
    formation, eleven, ranked = lineup.best_eleven(scored)
    assert formation == (5, 2, 3)
    assert {e["id"] for _, e in eleven} >= {13, 14, 15}
    assert ranked[0][0] == 9.0
