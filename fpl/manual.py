"""This week's transfers entered by hand in this-week.json (D65-D69). No I/O here.

The public feed hides transfers for the upcoming gameweek until its deadline,
so the owner types them in. feed.load puts the file's contents in
feed["this_week"] (None when there is no file).
"""
import unicodedata

from fpl.feed import THIS_WEEK as FILE, upcoming
from fpl.picks import current_picks

TENTHS_PER_MILLION = 10  # the file gives the bank in millions; prices stay in tenths


class ManualError(Exception):
    pass


def status(feed):
    """'absent', 'ignored' (gameweek does not match) or 'used'."""
    tw = feed.get("this_week")
    if tw is None:
        return "absent"
    if not isinstance(tw, dict) or not {"gameweek", "transfers", "bank"} <= tw.keys():
        raise ManualError(f'{FILE} needs "gameweek", "transfers" and "bank".')
    return "used" if tw["gameweek"] == upcoming(feed)["id"] else "ignored"


def _full(el):
    return f"{el.get('first_name', '')} {el.get('second_name', '')}".strip()


def _plain(text):
    """Lower case without accents, so "Sangare" finds "Sangaré" (D68)."""
    decomposed = unicodedata.normalize("NFKD", text.strip().casefold())
    return "".join(c for c in decomposed if not unicodedata.combining(c))


def matches(name, pool):
    """Every player in pool whose web_name, second_name or full name is name (D68)."""
    want = _plain(name)
    return [e for e in pool
            if want in (_plain(e["web_name"]), _plain(e.get("second_name", "")), _plain(_full(e)))]


def _find(name, pool, where):
    hits = matches(name, pool)
    if not hits:
        raise ManualError(f'{FILE}: "{name}" matches no player {where}.')
    if len(hits) > 1:
        names = ", ".join(_full(e) or e["web_name"] for e in hits)
        raise ManualError(f'{FILE}: "{name}" matches more than one player {where}: {names}. '
                          "Use the full name.")
    return hits[0]


def swaps(feed):
    """[(out element, in element)] in file order, or [] when the file is not used."""
    if status(feed) != "used":
        return []
    elements = feed["bootstrap"]["elements"]
    by_id = {e["id"]: e for e in elements}
    held = [by_id[p["element"]] for p in current_picks(feed)["picks"]]
    out = []
    for t in feed["this_week"]["transfers"]:
        o = _find(t["out"], held, "in your squad")
        i = _find(t["in"], [e for e in elements if e not in held], "outside your squad")
        if i["element_type"] != o["element_type"]:
            raise ManualError(f'{FILE}: "{t["out"]}" and "{t["in"]}" play different positions.')
        held[held.index(o)] = i
        out.append((o, i))
    return out


def bank(feed):
    """Bank in tenths from the file, or None when the file is not used."""
    if status(feed) != "used":
        return None
    return round(feed["this_week"]["bank"] * TENTHS_PER_MILLION)

