"""Transfer suggestions (D33-D38, D62, D63). Takes the feed in, gives data out. No network."""
from itertools import combinations

from fpl import money, score, squad
from fpl.sections import lineup

MIN_CHANCE = 0.75  # D36: incoming player's next-week chance
MIN_FREE_GAIN = 2  # D34: six-week gain needed for a free transfer
MIN_HIT_GAIN = 8  # D35: six-week gain needed for a transfer that costs a hit
HIT_COST = 4
TOP_SINGLES = 50  # D38: singles kept before pairs are tried
MAX_PER_CLUB = 3
BENCH_GAIN_FACTOR = 0.5  # D63: share of the gain counted when the player coming in would not start


def _legal(feed, held, swaps, bank):
    """swaps: [(out, in)]. Budget (selling price in, now_cost in) and club limit."""
    budget = bank + sum(money.selling_price(feed, o) - i["now_cost"] for o, i in swaps)
    if budget < 0:
        return False
    out_ids = {o["id"] for o, _ in swaps}
    clubs = [e["team"] for e in held if e["id"] not in out_ids] + [i["team"] for _, i in swaps]
    return all(clubs.count(c) <= MAX_PER_CLUB for c in set(clubs))


def _order(swaps):
    """Starters first, then highest gain (D63). swaps: [(gain, out, in, starts)]."""
    return sorted(swaps, key=lambda s: (not s[3], -s[0]))


def _plan(swaps, free):
    """Ordered swaps use free transfers first. Returns (net, hits) or None if a rule fails."""
    net, hits = 0.0, 0
    for k, (gain, _, _, starts) in enumerate(_order(swaps)):
        paid = k >= free
        if paid and not starts:  # D62: a hit only for a player who would start
            return None
        if gain < (MIN_HIT_GAIN if paid else MIN_FREE_GAIN):
            return None
        hits += paid
        net += gain - (HIT_COST if paid else 0)
    return net, hits


def _scored(feed, held, swaps, memo):
    """[(out, in)] -> [(gain, out, in, starts)]; starting is judged on the squad after all swaps."""
    def s(kind, fn, el):
        if (kind, el["id"]) not in memo:
            memo[kind, el["id"]] = fn(feed, el)
        return memo[kind, el["id"]]
    out_ids = {o["id"] for o, _ in swaps}
    after = [e for e in held if e["id"] not in out_ids] + [i for _, i in swaps]
    _, eleven, _ = lineup.best_eleven([(s("n", score.next_score, e), e) for e in after])
    starters = {e["id"] for _, e in eleven}
    rows = []
    for o, i in swaps:
        # known simplification (D37): ignores whether the player going out would start
        gain, starts = s("6", score.six_week_score, i) - s("6", score.six_week_score, o), i["id"] in starters
        rows.append((gain if starts else gain * BENCH_GAIN_FACTOR, o, i, starts))
    return rows


def replacements(feed, out_el, memo=None):
    """Single swaps for one squad player: [(gain, out, in, starts)], best first.
    memo: score cache a caller can share between calls."""
    memo = {} if memo is None else memo
    held = squad.squad(feed)
    held_ids = {e["id"] for e in held}
    bank = money.bank(feed)
    rows = []
    for i in feed["bootstrap"]["elements"]:
        if (i["id"] not in held_ids and i["status"] == "a" and score.chance_next(i) >= MIN_CHANCE
                and i["element_type"] == out_el["element_type"]
                and _legal(feed, held, [(out_el, i)], bank)):
            rows += _scored(feed, held, [(out_el, i)], memo)
    return sorted(rows, key=lambda s: (-s[0], s[2]["id"]))


def build(feed):
    held = squad.squad(feed)
    free = money.free_transfers(feed)
    bank, memo = money.bank(feed), {}

    def scored(swaps):
        return _scored(feed, held, swaps, memo)

    singles = []
    for o in held:
        singles += replacements(feed, o, memo)
    singles.sort(key=lambda s: (-s[0], s[2]["id"], s[1]["id"]))
    singles = singles[:TOP_SINGLES]

    options = [[s] for s in singles]
    for a, b in combinations(singles, 2):
        swaps = [(a[1], a[2]), (b[1], b[2])]
        if a[1]["id"] != b[1]["id"] and a[2]["id"] != b[2]["id"] and _legal(feed, held, swaps, bank):
            options.append(scored(swaps))
    best = None
    for opt in options:
        r = _plan(opt, free)
        if r and (best is None or (r[0], -len(opt)) > (best[0], -len(best[2]))):
            best = (r[0], r[1], opt)

    rows, hits = [], 0
    if best:
        hits = best[1]
        for k, (g, o, i, starts) in enumerate(_order(best[2])):
            rows.append({"out": o["web_name"], "in": i["web_name"], "gain": g,
                         "out_price": o["now_cost"], "in_price": i["now_cost"],
                         "starts": starts, "hit": k >= free})
    cap = 1 + feed["bootstrap"]["game_settings"]["max_extra_free_transfers"]
    return {"transfers": rows, "hit_points": hits * HIT_COST, "free_now": free,
            "free_next_week": min(cap, max(free - len(rows), 0) + money.WEEKLY_FREE)}


def render(data):
    if not data["transfers"]:
        n = data["free_now"]  # D206: say how many are saved
        saved = (f"Save your {n} free transfer{'' if n == 1 else 's'}" if n
                 else "No free transfer to save")
        return [f"No transfer worth making. {saved} — you'll have "
                f"{data['free_next_week']} free next week."]
    out = ["Transfers"]
    for t in data["transfers"]:
        out.append(f"  {t['out']} -> {t['in']}  ({money.price(t['out_price'])} -> "
                   f"{money.price(t['in_price'])})  6 GW gain {t['gain']:+.1f}"
                   + ("" if t["starts"] else "  [bench, half gain]")
                   + ("  [hit]" if t["hit"] else ""))
    if data["hit_points"]:
        out.append(f"  Hit: -{data['hit_points']} points")
    return out
