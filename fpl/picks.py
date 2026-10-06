"""Which picks to use."""


def current_picks(feed):
    """Last picks; after a Free Hit the gameweek before (the squad reverts)."""
    gw = max(feed["picks"])
    if feed["picks"][gw].get("active_chip") == "freehit":
        gw -= 1
    return feed["picks"][gw]

