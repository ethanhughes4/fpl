"""Score breakdowns (D141, D182) for the captain, the vice and players in close calls. No network."""
from fpl import score
from fpl.explain.parts import close
from fpl.feed import num, upcoming

POS = {1: "GK", 2: "DEF", 3: "MID", 4: "FWD"}


def _names(data):
    """Captain, vice, then each player in a close call; no repeats."""
    out = [data["captain"]["captain"]["name"], data["captain"]["vice"]["name"]]
    out += [n for c in close.calls(data) if c["close"] for n in c["players"]]
    return list(dict.fromkeys(out))


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
    by_id = {e["id"]: e for e in els}
    ids = {r["id"]: r["name"] for r in data["lineup"]["starters"] + data["lineup"]["bench"]}
    by_name = {}
    for e in els:
        by_name.setdefault(e["web_name"], e)
    by_name.update({n: by_id[i] for i, n in ids.items()})  # squad rows win over same-named players
    shrunk, typical = score.shrunk_bases(els), score.typical_bases(els)
    out = ["", "Score breakdowns"]
    for name in _names(data):
        el = by_name[name]
        opp = _opponents(feed, el)
        opp_text = " and ".join(f"{t} ({ha})" for t, ha, _ in opp) or "no match"
        diff = " and ".join(str(d) for *_, d in opp) or "none"
        typ = f"{typical[el['id']]:.1f}" if el["id"] in typical else "none"
        out.append(
            f"  {name} ({POS[el['element_type']]}): form {num(el['form']):.1f}, "
            f"points per game {num(el['points_per_game']):.1f}, "
            f"minutes factor {score.minutes_factor(feed, el):.1f}, "
            f"next opponent {opp_text}, fixture difficulty {diff}, "
            f"playing chance {round(score.chance_next(el) * 100)}%, "
            f"next-GW score {score.next_score(feed, el, shrunk[el['id']]):.1f}, "
            f"games played {score.appearances(el)}, "
            f"typical base for position and start price {typ}, "
            f"base {score.base(el):.1f} before shrink and {shrunk[el['id']]:.1f} after")
    return out
