import copy

from fpl import picks
from tests.fakefeed import transfer


def test_last_picks_used(feed):
    assert picks.current_picks(feed) is feed["picks"][5]


def test_free_hit_uses_gameweek_before(feed):
    earlier = copy.deepcopy(feed["picks"][5])
    feed["picks"][4] = earlier
    feed["picks"][5]["active_chip"] = "freehit"
    assert picks.current_picks(feed) is earlier


def test_pending_only_upcoming(feed):
    feed["transfers"] = [transfer(20, 1, 5), transfer(21, 2, 6)]
    assert [t["element_in"] for t in picks.pending_transfers(feed)] == [21]
