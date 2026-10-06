"""Which picks to use, and the transfers not yet in them."""
from fpl.feed import upcoming


def current_picks(feed):
    """Last picks; after a Free Hit the gameweek before (the squad reverts)."""
    gw = max(feed["picks"])
    if feed["picks"][gw].get("active_chip") == "freehit":
        gw -= 1
    return feed["picks"][gw]


def pending_transfers(feed):
    gw = upcoming(feed)["id"]
    return [t for t in feed["transfers"] if t["event"] == gw]
