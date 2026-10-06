"""Bank, selling price and free transfers. Prices in tenths of a million. No network."""
import math

from fpl import manual
from fpl.feed import num, upcoming
from fpl.picks import current_picks

NO_COST_CHIPS = ("wildcard", "freehit")  # count unchanged in these weeks, no +1 (D32)
FIRST_FREE = 1  # free transfers at gameweek 2
WEEKLY_FREE = 1  # added each week


def price(tenths):
    """61 -> '6.1m'."""
    return f"{tenths / 10:.1f}m"


def _chip_weeks(feed, names):
    # Assumes history.chips rows look like {"name": "wildcard" | "freehit", "event": n}.
    # Unverified against real data: the snapshot has no chips.
    return {c["event"] for c in feed["history"].get("chips", []) if c["name"] in names}


def purchase_price(feed, element):
    """Last transfer in from a non-Free-Hit week, else now_cost - cost_change_start (D31, D60).
    A player bought by hand this week was bought at today's price (D67)."""
    if any(i["id"] == element["id"] for _, i in manual.swaps(feed)):
        return element["now_cost"]
    skip = _chip_weeks(feed, ("freehit",))
    bought = [t for t in feed["transfers"]
              if t["element_in"] == element["id"] and t["event"] not in skip]
    if bought:
        return max(bought, key=lambda t: (t["event"], t["time"]))["element_in_cost"]
    return element["now_cost"] - num(element.get("cost_change_start"))


def selling_price(feed, element):
    now, bought = element["now_cost"], purchase_price(feed, element)
    if now <= bought:
        return now
    fee = feed["bootstrap"]["game_settings"]["transfers_sell_on_fee"]
    return bought + math.floor((now - bought) * fee)


def bank(feed):
    """Bank from this-week.json when used (D67), else from the chosen picks (D30)."""
    entered = manual.bank(feed)
    return current_picks(feed)["entry_history"]["bank"] if entered is None else entered


def free_transfers(feed):
    """Free transfers left for the upcoming gameweek, after hand-entered transfers (never below 0, D67)."""
    cap = 1 + feed["bootstrap"]["game_settings"]["max_extra_free_transfers"]
    used = {h["event"]: h["event_transfers"] for h in feed["history"]["current"]}
    no_cost = _chip_weeks(feed, NO_COST_CHIPS)
    ft = FIRST_FREE
    for gw in range(2, upcoming(feed)["id"]):
        if gw in no_cost:
            continue
        ft = min(cap, max(ft - used.get(gw, 0), 0) + WEEKLY_FREE)
    return max(ft - len(manual.swaps(feed)), 0)
