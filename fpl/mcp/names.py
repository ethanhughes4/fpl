"""Turn a tool argument (an id or a name) into one player, or one message (D229). No network."""
from fpl import manual, money
from fpl.explain.parts.breakdown import POS


def resolve(arg, pool, teams):
    """One element from pool, or a message string when none or several match.
    teams: {team id: short name}, for the several-matches lines."""
    text = str(arg).strip()
    hits = [e for e in pool if e["id"] == int(text)] if text.isdigit() else manual.matches(text, pool)
    if not hits:
        return f'No player matches "{arg}".'
    if len(hits) > 1:
        return f'"{arg}" matches more than one player; call again with the id:\n' + "\n".join(
            f"  {e['web_name']}, {teams[e['team']]}, {POS[e['element_type']]}, "
            f"{money.price(e['now_cost'])}, id {e['id']}" for e in hits)
    return hits[0]
