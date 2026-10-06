"""Current squad: the chosen picks with pending transfers applied."""
from fpl.picks import current_picks, pending_transfers


def squad_ids(feed):
    """List of element ids, in pick order, pending swaps applied."""
    ids = [p["element"] for p in current_picks(feed)["picks"]]
    for t in sorted(pending_transfers(feed), key=lambda t: t["time"]):
        if t["element_out"] in ids:
            ids[ids.index(t["element_out"])] = t["element_in"]
        else:
            ids.append(t["element_in"])
    return ids


def squad(feed):
    by_id = {e["id"]: e for e in feed["bootstrap"]["elements"]}
    return [by_id[i] for i in squad_ids(feed)]
