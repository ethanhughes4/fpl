"""Score breakdowns (D141, D182, D192) for the captain, the vice, players in close calls and both
players in every suggested transfer. No network."""
from fpl import score
from fpl.explain.parts import brief, close
from fpl.feed import num, upcoming

POS = {1: "GK", 2: "DEF", 3: "MID", 4: "FWD"}
FORM_MEANS = "average points per match over the last 30 days"  # D199; the feed's form (D87, D119)


def _players(data, feed):
    """[(name, element)]: captain, vice, players in close calls, then both players in every
    suggested transfer (D192); no repeats. Squad players by id; a player coming in by name,
    price and position, since names repeat in the feed (Palmer, Wilson)."""
    els = feed["bootstrap"]["elements"]
    by_id = {e["id"]: e for e in els}
    squad = {r["name"]: by_id[r["id"]] for r in data["lineup"]["starters"] + data["lineup"]["bench"]}
    names = [data["captain"]["captain"]["name"], data["captain"]["vice"]["name"]]
    names += [n for c in close.calls(data) if c["close"] for n in c["players"]]
    out = {n: squad[n] for n in names if n in squad}
    for t in data["transfers"]["transfers"]:
        gone = squad[t["out"]]
        out.setdefault(t["out"], gone)
        out.setdefault(t["in"], next(e for e in els if e["web_name"] == t["in"]
                                     and e["now_cost"] == t["in_price"]
                                     and e["element_type"] == gone["element_type"]))
    order = names + [n for t in data["transfers"]["transfers"] for n in (t["out"], t["in"])]
    return [(n, out[n]) for n in dict.fromkeys(order)]


def _opponents(feed, el):
    """[(club, H or A, difficulty)] for the next gameweek; two for a double."""
    gw, teams = upcoming(feed)["id"], {t["id"]: t["short_name"] for t in feed["bootstrap"]["teams"]}
    out = []
    for f in feed["fixtures"]:
        if f["event"] != gw:
            continue
        if f["team_h"] == el["team"]:
            out.append((teams[f["team_a"]], "H", f["team_h_difficulty"]))
        elif f["team_a"] == el["team"]:
            out.append((teams[f["team_h"]], "A", f["team_a_difficulty"]))
    return out


def lines(data, feed):
    els = feed["bootstrap"]["elements"]
    shrunk, typical = score.shrunk_bases(els), score.typical_bases(els)
    out = ["", "Score breakdowns"]
    for name, el in _players(data, feed):
        opp = _opponents(feed, el)
        opp_text = " and ".join(f"{t} ({ha})" for t, ha, _ in opp) or "no match"
        diff = " and ".join(str(d) for *_, d in opp) or "none"
        typ = f"{typical[el['id']]:.1f}" if el["id"] in typical else "none"
        out.append(
            f"  {name} ({POS[el['element_type']]}): form {num(el['form']):.1f} ({FORM_MEANS}), "
            f"points per game {num(el['points_per_game']):.1f}, "
            f"minutes factor {score.minutes_factor(feed, el):.1f}, "
            f"next opponent {opp_text}, fixture difficulty {diff}, "
            f"{brief.chance_text(round(score.chance_next(el) * 100))}, "
            f"next-GW score {score.next_score(feed, el, shrunk[el['id']]):.1f}, "
            f"games played {score.appearances(el)}, "
            f"typical base for position and start price {typ}, "
            f"base {score.base(el):.1f} before shrink and {shrunk[el['id']]:.1f} after")
    return out
