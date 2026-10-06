from fpl.squad import squad_ids
from tests.fakefeed import player, transfer


def test_no_pending(feed):
    assert squad_ids(feed) == list(range(1, 16))


def test_pending_swaps_player_in(feed):
    feed["bootstrap"]["elements"].append(player(99, 3, 2))
    feed["transfers"] = [transfer(99, 9, event=6), transfer(98, 8, event=5)]
    ids = squad_ids(feed)
    assert 99 in ids and 9 not in ids and 8 in ids and len(ids) == 15
