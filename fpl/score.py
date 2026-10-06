"""Player scores. Takes the feed in, gives numbers out. No network."""
import statistics

from fpl.feed import num, upcoming

FORM_WEIGHT = 0.3  # D61
PPG_WEIGHT = 0.7  # D61
FULL_MINUTES = 90
# Fixture factor by the player's own side's difficulty 1..5 (D21).
FIXTURE_FACTOR = {1: 1.2, 2: 1.1, 3: 1.0, 4: 0.9, 5: 0.8}
WEEK_WEIGHTS = [1.0, 0.9, 0.8, 0.7, 0.6, 0.5]  # D24; length = weeks looked ahead
LATER_WEEKS_TOWARDS = 1.0  # weeks 2-6 chance moves halfway to this
GONE_STATUSES = ("u", "n")  # chance 0 for all six weeks
MINUTES_IF_NO_MATCHES = 0.0  # club has no finished fixtures yet (D64)
SHRINK_K = 3  # D99: pull toward the typical base, in matches


def base(el):
    return FORM_WEIGHT * num(el["form"]) + PPG_WEIGHT * num(el["points_per_game"])


def start_price(el):
    """Tenths. A rebuilt eval feed already stores the start price in now_cost."""
    return el["now_cost"] - el.get("cost_change_start", 0)


def appearances(el):
    """Matches with minutes > 0: the eval's exact count, else total points / points per game (D122)."""
    if "appearances" in el:
        return el["appearances"]
    ppg = num(el["points_per_game"])
    return round(num(el["total_points"]) / ppg) if ppg else 0


def typical_bases(elements):
    """{id: typical base for position and start price} (D99, D182); only players the fit covers."""
    out = {}
    for pos in {el["element_type"] for el in elements}:
        group = [el for el in elements if el["element_type"] == pos and num(el["minutes"]) > 0]
        prices = [start_price(el) for el in group]
        if len(group) < 2 or len(set(prices)) < 2:
            continue
        slope, icpt = statistics.linear_regression(prices, [base(el) for el in group])
        for el, price in zip(group, prices):
            out[el["id"]] = slope * price + icpt
    return out


def shrunk_bases(elements):
    """{id: base pulled toward the typical base for position and start price} (D99, D116)."""
    out = {el["id"]: base(el) for el in elements}
    typical = typical_bases(elements)
    for el in elements:
        if el["id"] in typical:
            n = appearances(el)
            out[el["id"]] = (n * base(el) + SHRINK_K * typical[el["id"]]) / (n + SHRINK_K)
    return out


def shrunk_base(feed, el):
    return shrunk_bases(feed["bootstrap"]["elements"])[el["id"]]


def minutes_factor(feed, el):
    played = sum(1 for f in feed["fixtures"]
                 if f["finished"] and el["team"] in (f["team_h"], f["team_a"]))
    if not played:
        return MINUTES_IF_NO_MATCHES
    return min(1.0, num(el["minutes"]) / (FULL_MINUTES * played))


def chance_next(el):
    if el["status"] in GONE_STATUSES:
        return 0.0
    c = el.get("chance_of_playing_next_round")
    if c is None:
        return 1.0 if el["status"] == "a" else 0.0
    return num(c) / 100


def chance(el, week_index):
    """week_index 0 = next gameweek."""
    c = chance_next(el)
    if week_index == 0 or el["status"] in GONE_STATUSES:
        return c
    return (c + LATER_WEEKS_TOWARDS) / 2


def gw_score(feed, el, gw, week_index=None, base_value=None):
    """One gameweek; blank = 0, double = sum. week_index defaults to gw - next.
    base_value replaces the shrunk base (D121, D123) when given."""
    if week_index is None:
        week_index = gw - upcoming(feed)["id"]
    if base_value is None:
        base_value = shrunk_base(feed, el)
    per_fixture = base_value * minutes_factor(feed, el) * chance(el, week_index)
    total = 0.0
    for f in feed["fixtures"]:
        if f["event"] != gw:
            continue
        if f["team_h"] == el["team"]:
            total += per_fixture * FIXTURE_FACTOR[f["team_h_difficulty"]]
        elif f["team_a"] == el["team"]:
            total += per_fixture * FIXTURE_FACTOR[f["team_a_difficulty"]]
    return total


def next_score(feed, el, base_value=None):
    return gw_score(feed, el, upcoming(feed)["id"], 0, base_value=base_value)


def six_week_score(feed, el, base_value=None):
    nxt = upcoming(feed)["id"]
    if base_value is None:
        base_value = shrunk_base(feed, el)
    return sum(w * gw_score(feed, el, nxt + i, i, base_value) for i, w in enumerate(WEEK_WEIGHTS))


def sort_key(el, score):
    """Best first: higher score, then higher total_points, then lower id (D27)."""
    return (-score, -num(el["total_points"]), el["id"])
