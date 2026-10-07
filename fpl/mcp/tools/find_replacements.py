from fpl import money, squad
from fpl.mcp import session
from fpl.mcp.names import resolve
from fpl.sections import transfers

TOP_REPLACEMENTS = 5

DESCRIPTION = (
    "For one player in the owner's squad (name or id), list the top "
    f"{TOP_REPLACEMENTS} players who could replace him: same position, affordable, at most three "
    "per club, available. Each row has six-week gain (halved if the newcomer would not start), "
    "price, and whether it clears the free-transfer bar and is worth a hit (hit size and bar "
    "given); the first line says how many options there are. If a name matches "
    "several players, call again with the id."
)


def tool(name: str | int) -> str:  # an id may come as a number (D229)
    return session.reply(lambda feed: _body(name, feed))


def _yes(ok):
    return "yes" if ok else "no"


def _body(name, feed):
    els = feed["bootstrap"]["elements"]
    teams = {t["id"]: t["short_name"] for t in feed["bootstrap"]["teams"]}
    out = resolve(name, els, teams)
    if isinstance(out, str):
        return out
    if out["id"] not in squad.squad_ids(feed):
        return f"{out['web_name']} is not in your squad."
    head = (f"Replacing {out['web_name']}: bank {money.price(money.bank(feed))}, "
            f"selling price {money.price(money.selling_price(feed, out))}")
    rows = transfers.replacements(feed, out)[:TOP_REPLACEMENTS]
    if not rows:
        return f"{head}\nNo legal replacement."
    head += f", {len(rows)} option{'' if len(rows) == 1 else 's'}"  # D267: printed, so not counted by Claude
    return "\n".join([head] + [
        f"  {i['web_name']}, {teams[i['team']]}, {money.price(i['now_cost'])}, "
        f"six-week gain {gain:+.1f}, {'starts' if starts else 'bench, half gain'}, "
        f"clears free bar {transfers.MIN_FREE_GAIN}: {_yes(gain >= transfers.MIN_FREE_GAIN)}, "
        f"worth a {transfers.HIT_COST}-point hit, bar {transfers.MIN_HIT_GAIN}: "
        f"{_yes(gain >= transfers.MIN_HIT_GAIN)}"
        for gain, _, i, starts in rows])
