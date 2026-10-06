"""Player scores. Takes the feed in, gives numbers out. No network."""
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


def base(el):
    return FORM_WEIGHT * num(el["form"]) + PPG_WEIGHT * num(el["points_per_game"])


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
    base_value replaces base(el) when given."""
    if week_index is None:
        week_index = gw - upcoming(feed)["id"]
    if base_value is None:
        base_value = base(el)
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


def six_week_score(feed, el):
    nxt = upcoming(feed)["id"]
    return sum(w * gw_score(feed, el, nxt + i, i) for i, w in enumerate(WEEK_WEIGHTS))


def sort_key(el, score):
    """Best first: higher score, then higher total_points, then lower id (D27)."""
    return (-score, -num(el["total_points"]), el["id"])
