from fpl import score, squad
from fpl.feed import upcoming

FIT_STATUS = "a"
FULL_CHANCE = 1.0


def build(feed):
    gw = upcoming(feed)["id"]
    teams = {f[side] for f in feed["fixtures"] if f["event"] == gw for side in ("team_h", "team_a")}
    out = []
    for el in squad.squad(feed):
        chance = score.chance_next(el)
        blank = el["team"] not in teams
        if el["status"] != FIT_STATUS or chance < FULL_CHANCE or blank:
            out.append({"id": el["id"], "name": el["web_name"], "chance": round(chance * 100),
                        "blank": blank, "news": el.get("news") or ""})
    return out


def render(data):
    if not data:
        return ["Warnings: none"]
    out = ["Warnings"]
    for w in data:
        news = "no fixture next gameweek" if w["blank"] and not w["news"] else w["news"]
        out.append(f"  {w['name']:<16} {w['chance']:3d}%  {news}")
    return out
