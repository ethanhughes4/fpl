"""Current squad: the chosen picks with this week's hand-entered transfers applied (D66)."""
from fpl import manual
from fpl.picks import current_picks


def squad_ids(feed):
    """List of element ids, in pick order, hand-entered swaps applied."""
    ids = [p["element"] for p in current_picks(feed)["picks"]]
    for o, i in manual.swaps(feed):
        ids[ids.index(o["id"])] = i["id"]
    return ids


def squad(feed):
    by_id = {e["id"]: e for e in feed["bootstrap"]["elements"]}
    return [by_id[i] for i in squad_ids(feed)]
