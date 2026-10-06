from fpl import money
from fpl.sections import transfers
from tests.fakefeed import player

FWD_OUT = {"P13", "P14", "P15"}


def setup(feed, monkeypatch, free, *cands, bank=None):
    monkeypatch.setattr(money, "free_transfers", lambda f: free)
    if bank is not None:
        feed["picks"][5]["entry_history"]["bank"] = bank
    feed["bootstrap"]["elements"] += list(cands)
    return transfers.build(feed)


def star(id, pos=4, team=5, cost=55, base="9.0", **kw):
    return player(id, pos, team, cost, form=base, points_per_game=base, **kw)


def test_best_same_position_swap(feed, monkeypatch):
    d = setup(feed, monkeypatch, 1, star(20), star(21, pos=1))
    (t,) = d["transfers"]
    assert t["in"] == "P20" and t["out"] in FWD_OUT  # the elite keeper is in a different position
    assert round(t["gain"], 6) == 18 and not t["hit"] and d["hit_points"] == 0


def test_budget(feed, monkeypatch):
    d = setup(feed, monkeypatch, 1, star(20, cost=56))  # bank 5 + sell 50 = 55
    assert d["transfers"] == []


def test_three_per_club(feed, monkeypatch):
    d = setup(feed, monkeypatch, 1, star(20, team=2))  # club 2 already holds 3 (P1, P7, P13)
    assert [t["out"] for t in d["transfers"]] == ["P13"]


def test_injured_never_suggested(feed, monkeypatch):
    d = setup(feed, monkeypatch, 1, star(20, status="d"), star(21, chance_of_playing_next_round=50),
              star(22, base="5.0"))
    assert all(t["in"] == "P22" for t in d["transfers"])


def test_gain_below_two_is_saved(feed, monkeypatch):
    d = setup(feed, monkeypatch, 3, star(20, base="5.2"))
    assert d["transfers"] == []
    assert transfers.render(d) == ["No transfer worth making. Save it — you'll have 4 free next week."]


def test_hit_only_at_eight(feed, monkeypatch):
    assert setup(feed, monkeypatch, 0, star(20, base="6.5"))["transfers"] == []  # gain 6.75
    d = setup(feed, monkeypatch, 0, star(21, base="7.0"))  # gain 9
    assert d["hit_points"] == 4 and d["transfers"][0]["hit"]


def test_never_three(feed, monkeypatch):
    d = setup(feed, monkeypatch, 5, star(20, team=4), star(21, team=5), star(22, team=6), bank=50)
    assert len(d["transfers"]) == 2


def test_pair_shares_budget(feed, monkeypatch):
    d = setup(feed, monkeypatch, 2, star(20, team=4), star(21, team=6))  # bank 5 covers only one
    assert len(d["transfers"]) == 1


def test_pair_when_budget_allows(feed, monkeypatch):
    d = setup(feed, monkeypatch, 2, star(20, team=4), star(21, team=6), bank=10)
    assert len(d["transfers"]) == 2


def test_second_transfer_is_hit_when_free_used(feed, monkeypatch):
    d = setup(feed, monkeypatch, 1, star(20, team=4), star(21, team=6), bank=10)
    assert [t["hit"] for t in d["transfers"]] == [False, True] and d["hit_points"] == 4
    assert "Hit: -4 points" in transfers.render(d)[-1]
