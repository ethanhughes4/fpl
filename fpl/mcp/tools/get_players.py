from fpl import money, score, squad
from fpl.explain.parts import breakdown
from fpl.mcp import session
from fpl.mcp.names import resolve

MAX_PLAYERS = 4
SCORES = (("Next-GW", score.next_score), ("Six-week", score.six_week_score))

DESCRIPTION = (
    f"Look up or compare 1 to {MAX_PLAYERS} players, by name or by id: score breakdown, club, "
    "price, six-week score, status, news, and whether he is in the owner's squad. With "
    "several players it also says who leads on next-GW and six-week score and by how much, "
    "and who costs more and by how much. "
    "If a name matches several players, call again with the id."
)


def _gaps(label, rows):
    """rows: [(name, printed score, element)]. 'Next-GW: A leads; B 0.8 behind; C level with A.'"""
    rows = sorted(rows, key=lambda r: (-r[1], -float(r[2]["total_points"]), r[2]["id"]))  # D27
    lead = rows[0]
    parts = [f"{lead[0]} leads"]
    for name, s, _ in rows[1:]:
        gap = round(lead[1] - s, 1)
        parts.append(f"{name} level with {lead[0]}" if gap == 0 else f"{name} {gap:.1f} behind")
    return f"{label}: " + "; ".join(parts) + "."


def _price_gaps(els):
    """'Price: A costs most at 9.7m; B 3.8m less; C level with A.' Ties by lower id (D266)."""
    els = sorted(els, key=lambda e: (-e["now_cost"], e["id"]))
    top = els[0]
    parts = [f"{top['web_name']} costs most at {money.price(top['now_cost'])}"]
    for e in els[1:]:
        gap = top["now_cost"] - e["now_cost"]  # tenths, so exact
        parts.append(f"{e['web_name']} level with {top['web_name']}" if gap == 0
                     else f"{e['web_name']} {money.price(gap)} less")
    return "Price: " + "; ".join(parts) + "."


def tool(names: list[str | int]) -> str:  # an id may come as a number (D229)
    if not 1 <= len(names) <= MAX_PLAYERS:
        return session.reply(lambda feed: f"Give between 1 and {MAX_PLAYERS} players.")  # D227
    return session.reply(lambda feed: _body(names, feed))


def _body(names, feed):
    els = feed["bootstrap"]["elements"]
    teams = {t["id"]: t["short_name"] for t in feed["bootstrap"]["teams"]}
    found = [resolve(n, els, teams) for n in names]
    if any(isinstance(f, str) for f in found):
        return "\n".join(f for f in found if isinstance(f, str))
    found = list({e["id"]: e for e in found}.values())
    shrunk, typical = score.shrunk_bases(els), score.typical_bases(els)
    mine = set(squad.squad_ids(feed))
    out = []
    for el in found:
        six = score.six_week_score(feed, el, shrunk[el["id"]])
        out += [breakdown.line(el["web_name"], el, feed, shrunk, typical),
                f"    {teams[el['team']]}, {money.price(el['now_cost'])}, six-week score {six:.1f}, "
                f"status {el['status']}, news: {el.get('news') or 'none'}, "
                f"{'in' if el['id'] in mine else 'not in'} your squad"]
    if len(found) > 1:
        for label, fn in SCORES:
            out.append(_gaps(label, [(e["web_name"], round(fn(feed, e, shrunk[e["id"]]), 1), e)
                                     for e in found]))
        out.append(_price_gaps(found))
    return "\n".join(out)
