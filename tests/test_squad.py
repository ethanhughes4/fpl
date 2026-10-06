from fpl.squad import squad_ids
from tests.fakefeed import player, transfer


def test_no_file(feed):
    assert squad_ids(feed) == list(range(1, 16))


def test_feed_transfers_for_upcoming_week_not_applied(feed):
    # D66: the public feed's transfers are never treated as this week's
    feed["bootstrap"]["elements"].append(player(99, 3, 2))
    feed["transfers"] = [transfer(99, 9, event=6)]
    assert squad_ids(feed) == list(range(1, 16))


def test_hand_entered_swap_applied_in_place(feed):
    feed["bootstrap"]["elements"].append(player(99, 3, 2))
    feed["this_week"] = {"gameweek": 6, "transfers": [{"out": "P9", "in": "P99"}], "bank": 0.5}
    ids = squad_ids(feed)
    assert ids[8] == 99 and 9 not in ids and len(ids) == 15
